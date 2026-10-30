"""ACTIVE-001 P2: strictly invented-only CPU and memory engineering preflight.

No old TRAIN/DEV/FINAL source, scientific targets, Oracle or evaluator-only
labels are imported. Times are descriptive observations on one machine, not
budgets or measurements of heldout accuracy.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
import platform
import resource
import statistics
import sys
from time import perf_counter_ns, process_time_ns
from typing import Callable

from packages.active_feasibility import census_fixture
from packages.active_feasibility.f4 import probe_f4
from packages.active_learning import (
    final_program, make_answer, partitions, propose_disagreement,
    propose_random, start, update,
)
from packages.inquiry_world import INPUTS, build_catalog, execute, input_split

SCHEMA = "active001-cpu-preflight/invented-only/1"
FIXTURE_SEED = 20261030


@dataclass(frozen=True, slots=True)
class Phase:
    repeats: int
    cpu_ns: tuple[int, ...]
    wall_ns: tuple[int, ...]
    median_cpu_ns: int
    median_wall_ns: int
    max_cpu_ns: int
    max_wall_ns: int


def _phase(repeats: int, function: Callable[[], object]) -> Phase:
    cpus: list[int] = []
    walls: list[int] = []
    for _ in range(repeats):
        c0, w0 = process_time_ns(), perf_counter_ns()
        function()
        cpus.append(process_time_ns() - c0)
        walls.append(perf_counter_ns() - w0)
    return Phase(repeats, tuple(cpus), tuple(walls),
                 int(statistics.median(cpus)), int(statistics.median(walls)),
                 max(cpus), max(walls))


def workload_counts(n_tasks: int, *, include_b1plus: bool) -> dict[str, int]:
    """Structural upper COUNTs only, not measured runtime or Oracle usage."""
    if type(n_tasks) is not int or n_tasks not in (512, 1024, 4096):
        raise ValueError("Only prespecified illustrative task counts allowed")
    if type(include_b1plus) is not bool:
        raise ValueError("include_b1plus must be an exact bool")
    # Per task: B0 once, B2 once, B1 five independent seeded repeats,
    # optional B1+ five distinct within-task repeats.
    episodes = (12 if include_b1plus else 7) * n_tasks
    active_arms = (11 if include_b1plus else 6) * n_tasks
    return {
        "n_tasks": n_tasks,
        "arm_episodes": episodes,
        "active_arm_episodes": active_arms,
        "maximum_query_calls": active_arms * 2,
        "model_predictions": episodes * 64,
        "auditor_input_count_per_episode": 64,
    }


def extrapolate_cpu_ns(phases: dict[str, Phase], *,
                       n_tasks: int, include_b1plus: bool) -> int:
    """Scenario estimate using B2 timing for every question, NOT an upper bound.

    This conservatively *assigns* B2 choice/update timing to both stochastic
    arms but makes NO assumption that it dominates their actual cost.
    """
    counts = workload_counts(n_tasks, include_b1plus=include_b1plus)
    episodes = counts["arm_episodes"]
    queries = counts["maximum_query_calls"]
    per_episode = (phases["start"].median_cpu_ns +
                   phases["replay_final"].median_cpu_ns +
                   phases["predict_64_query_inputs"].median_cpu_ns)
    per_query = (phases["choose_b2"].median_cpu_ns +
                 phases["update_synthetic"].median_cpu_ns)
    # Fixed one-process setup: one catalog build and one Gate-F census.
    return (phases["catalog_build"].median_cpu_ns +
            phases["gate_f_census"].median_cpu_ns +
            episodes * per_episode + queries * per_query)


def _maxrss_kib() -> int:
    """Linux ru_maxrss is cumulative process high-water mark, KiB."""
    if sys.platform != "linux":
        raise RuntimeError("resource.ru_maxrss KiB contract is Linux-only")
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def measure_invented_fixture(*, repeats: int = 3) -> dict[str, object]:
    """Bounded measurement; no new scientific tasks and no withheld labels."""
    if type(repeats) is not int or not 1 <= repeats <= 3:
        raise ValueError("repeats must be an exact int 1..3")
    before_kib = _maxrss_kib()
    phases: dict[str, Phase] = {}
    # Each fresh build enumerates finite DSL; distinct from cached lookups.
    phases["catalog_build"] = _phase(repeats, build_catalog)
    cat = build_catalog()
    split = input_split(FIXTURE_SEED)
    first, second = split.public_ids[:2]
    public = ((first, INPUTS[first]), (second, INPUTS[second]))
    base = start("p2-invented-only", public, split, cat)
    if base.status != "ambiguous":
        raise AssertionError("P2 context must exercise question choice")
    # Explicit catalog lookup uses already-validated catalog, no future lock.
    phases["catalog_cached_reference"] = _phase(repeats, lambda: cat.by_id[base.class_ids[0]])
    phases["start"] = _phase(repeats, lambda: start("p2-invented-only", public, split, cat))
    chosen = propose_disagreement(base, cat)
    if chosen is None:
        raise AssertionError("P2 context needs a discriminating question")
    phases["partition_and_validation"] = _phase(
        repeats, lambda: partitions(base, cat, chosen.input_id))
    phases["choose_b2"] = _phase(repeats, lambda: propose_disagreement(base, cat))
    phases["choose_b1"] = _phase(repeats, lambda: propose_random(base, cat, seed=11))
    # The following response is synthesized from a canonical class at a
    # PUBLICLY ALLOWED QUESTION input. It is not a target or scored label.
    fabricated_class = cat.by_id[base.class_ids[-1]]
    toy_answer = make_answer(chosen, fabricated_class.output_signature[chosen.input_id])
    advanced = update(base, chosen, toy_answer, cat)
    phases["update_synthetic"] = _phase(
        repeats, lambda: update(base, chosen, toy_answer, cat))
    phases["replay_final"] = _phase(repeats, lambda: final_program(advanced, cat))
    program = final_program(advanced, cat)
    if program is None:
        raise AssertionError("consistent invented answer cannot erase all classes")

    # 64 predictions on the *allowed query IDs*, NOT audit-only target labels.
    # This is a computational proxy for a future 64-input prediction sweep.
    def predict_64() -> None:
        predictions = tuple(execute(program, INPUTS[q]) for q in split.query_ids)
        if len(predictions) != 64:
            raise AssertionError("prediction sweep drifted")

    phases["predict_64_query_inputs"] = _phase(repeats, predict_64)
    # One full PREEXISTING structural Gate F F0-F3 census, no F4 full census.
    reports = []
    def run_gate_f() -> None:
        reports.append(census_fixture())
    phases["gate_f_census"] = _phase(1, run_gate_f)
    report = reports[0]
    if (report.context_sha256 !=
            "9c135ace8f815e4b3ac2465c9918833c3becd43781faeedc36314c28c9203f12"
            or report.f4_status.split(";")[0] != "not_computed"):
        raise AssertionError("existing Gate-F source/counts have drifted")

    # Tiny local F4 probe; NOT representative of all 91,367 contexts.
    toy = (("0", "0", "0"), ("0", "1", "0"),
           ("1", "0", "0"), ("1", "0", "1"))
    phases["f4_tiny_toy"] = _phase(repeats, lambda: probe_f4(toy))
    after_kib = _maxrss_kib()

    projections = []
    for n in (512, 1024, 4096):
        for expanded in (False, True):
            counts = workload_counts(n, include_b1plus=expanded)
            projections.append({
                "regime": "12-arm-future-proposal" if expanded else "7-arm-draft",
                **counts,
                "rough_cpu_seconds": round(extrapolate_cpu_ns(
                    phases, n_tasks=n, include_b1plus=expanded) / 1e9, 3),
            })
    return {
        "schema": SCHEMA,
        "scope": "invented public/query only; NO scientific scoring or heldout labels",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "fixture_seed": FIXTURE_SEED,
        "world_digest": cat.universe_digest,
        "split_digest": split.split_digest,
        "phase_ns": {key: asdict(value) for key, value in phases.items()},
        "process_maxrss_kib_before": before_kib,
        "process_maxrss_kib_after": after_kib,
        "memory_note": "Linux cumulative process high-water mark, not per-phase or peak of future evaluator",
        "structural_context_count": report.public_context_count,
        "structural_f4": "NOT_COMPUTED",
        "projections": projections,
        "projection_note": (
            "CPU-only engineering scenario using median invented B2 timings for "
            "all query arms; NOT a strict bound, B1+ NOT measured, not scaled "
            "wall time, not an official resource approval"),
        "scientific_scored_tasks": 0,
    }


def main() -> int:
    print(json.dumps(measure_invented_fixture(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
