"""EXP-0002B: gated DEV/FINAL evaluator, separate from immutable Kernel training.

No changes to generator/feature/KNN; all source, dataset and policy hashes are
validated against the pre-DEV/FINAL freeze record before observing any outcomes.
Only DEV is invoked automatically after reviewed integration into main.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
from time import perf_counter, process_time

from packages.evaluation import PrimitiveCallMeter, bounded_synthesize, expanded_nodes
from packages.kernel import (
    _candidate, choose, dataset_manifest, generate_partition, train,
    SKILL_HASH, ALGORITHM_VERSION, FEATURE_VERSION, MEASUREMENT_VERSION,
)
from packages.library import DEFAULT_PRIMITIVES, Registry
from packages.learning import registry_with_skill
from packages.protocol import Example
from packages.verification import verify


FROZEN_RECORD = Path(__file__).resolve().parents[2] / "experiments/EXP-0002B/freeze-v2.json"


def load_and_check_freeze(path: Path = FROZEN_RECORD):
    frozen = json.loads(path.read_text(encoding="utf-8"))
    if frozen["protocol"] != "EXP-0002B-PLAN-V2":
        raise ValueError("Unapproved preregistration")
    if frozen["algorithm_version"] != ALGORITHM_VERSION or frozen["features_version"] != FEATURE_VERSION:
        raise ValueError("Frozen method version mismatch")
    if frozen["measurement_version"] != MEASUREMENT_VERSION or frozen["skill_body_sha256"] != SKILL_HASH:
        raise ValueError("Frozen canonical meter or skill mismatch")
    manifest = dataset_manifest()
    for key, a, b in (
        ("dataset_sha256", frozen["dataset_sha256"], manifest["dataset_sha256"]),
        ("generator_source_sha256", frozen["generator_source_sha256"], manifest["generator_source_sha256"]),
        ("split_sha256", frozen["split_sha256"], manifest["split_sha256"]),
        ("partitions", frozen["partitions"], manifest["partition_counts"]),
        ("unique_rng_seeds", frozen["unique_rng_seeds"], manifest["unique_rng_seeds"]),
    ):
        if a != b:
            raise ValueError(f"Freeze mismatch: {key}")
    evidence = train()  # repeats TRAIN ONLY, never DEV/FINAL
    snap = evidence["snapshot"]
    if snap["policy_sha256"] != frozen["policy_sha256"]:
        raise ValueError("Freeze mismatch: policy_sha256")
    if snap["training_observations_sha256"] != frozen["training_observations_sha256"]:
        raise ValueError("Freeze mismatch: training_observations_sha256")
    if evidence["training_task_count"] != frozen["training_task_count"]:
        raise ValueError("Freeze mismatch: training task count")
    if evidence["training_primitive_invocations"] != frozen["training_off_on_primitive_calls_total"]:
        raise ValueError("Freeze mismatch: training calls")
    from packages.kernel import PolicySnapshot
    policy = PolicySnapshot.from_dict(snap)
    return frozen, manifest, evidence, policy


def _trial(task, audit: Example, registry: Registry, learned: dict):
    meter = PrimitiveCallMeter()
    result = bounded_synthesize(task, registry, learned, meter=meter)
    audit_valid = bool(result.status == "solved" and result.program is not None and
                       verify(result.program, (audit,), registry,
                              max_nodes=task.limits.max_ast_nodes).matched)
    invalid = result.status == "solved" and not audit_valid
    return {
        "search": result.to_dict(),
        "audit_correct": audit_valid,
        "audit_invalid_solved": bool(invalid),
        "primitive_invocations": meter.total,
        "by_op": meter.to_dict()["by_op"],
        "expanded_ast_nodes": (
            expanded_nodes(result.program, learned)
            if result.program is not None else None
        ),
    }


def _oracle_choice(off: dict, on: dict) -> str:
    """Diagnostic upper bound only; impossible to use as a real policy."""
    if off["audit_correct"] != on["audit_correct"]:
        return "ON" if on["audit_correct"] else "OFF"
    if off["primitive_invocations"] != on["primitive_invocations"]:
        return "ON" if on["primitive_invocations"] < off["primitive_invocations"] else "OFF"
    if off["search"]["tested_candidates"] != on["search"]["tested_candidates"]:
        return "ON" if on["search"]["tested_candidates"] < off["search"]["tested_candidates"] else "OFF"
    return "OFF"


def evaluate_record(item, policy, skill, base, enabled):
    """Run one set of three independent measurements; no hidden labels for Kernel."""
    # CRITICAL: decision is computed before OFF/ON results, using TaskSpec only.
    decision = choose(item.task, policy)
    choice = decision.action
    learned = {skill.skill_id: skill}
    off = _trial(item.task, item.audit, base, {})
    on = _trial(item.task, item.audit, enabled, learned)
    selected = _trial(item.task, item.audit,
                      enabled if choice == "ON" else base,
                      learned if choice == "ON" else {})
    reference = on if choice == "ON" else off
    # Re-measuring selected arm must preserve audit, costs, structural result
    # and deterministic trace; overhead elapsed_ms is excluded.
    for field in ("audit_correct", "audit_invalid_solved", "primitive_invocations", "by_op", "expanded_ast_nodes"):
        if selected[field] != reference[field]:
            raise ValueError(f"Independent LEARNED execution mismatch: {field}")
    for field in ("status", "program", "tested_candidates", "trace_sha256"):
        if selected["search"][field] != reference["search"][field]:
            raise ValueError(f"Independent LEARNED search mismatch: {field}")
    oracle = _oracle_choice(off, on)
    return {
        "task_id": item.task.task_id,
        "partition": item.partition,
        "family_for_evaluator_only": item.family,
        "audit_example_sha256": sha256(json.dumps(asdict(item.audit), sort_keys=True,
                                                       ensure_ascii=False,
                                                       separators=(",", ":")).encode()).hexdigest(),
        "policy_decision": asdict(decision),
        "off": off,
        "on": on,
        "learned": selected,
        "oracle_source_action": oracle,
    }


def _percentile_nearest_rank(values: list[int], quantile: float) -> int:
    if not values:
        raise ValueError("Cannot calculate percentile of no observations")
    sorted_values = sorted(values)
    return sorted_values[max(0, math.ceil(quantile * len(sorted_values)) - 1)]


def _score(rows: list[dict], arm: str) -> dict[str, object]:
    return {
        "tasks": len(rows),
        "audited_solved": sum(bool(r[arm]["audit_correct"]) for r in rows),
        "audit_invalid_solved": sum(bool(r[arm]["audit_invalid_solved"]) for r in rows),
        "primitive_invocations": sum(int(r[arm]["primitive_invocations"]) for r in rows),
        "tested_candidates": sum(int(r[arm]["search"]["tested_candidates"]) for r in rows),
        "solved_status": sum(r[arm]["search"]["status"] == "solved" for r in rows),
        "not_found_status": sum(r[arm]["search"]["status"] == "not_found" for r in rows),
        "budget_exhausted_status": sum(r[arm]["search"]["status"] == "budget_exhausted" for r in rows),
    }


def _bootstrap(rows: list[dict]) -> dict[str, object]:
    grouped = {family: [x for x in rows if x["family_for_evaluator_only"] == family]
               for family in sorted(set(x["family_for_evaluator_only"] for x in rows))}
    families = sorted(grouped)
    rand = random.Random(260299)
    samples = {m: [] for m in ("calls_saved_vs_off", "calls_saved_vs_on",
                              "candidates_saved_vs_off", "candidates_saved_vs_on")}
    for _ in range(1000):
        selected = [grouped[rand.choice(families)] for __ in families]
        aggregate = [item for group in selected for item in group]
        score = {arm: _score(aggregate, arm) for arm in ("off", "on", "learned")}
        for field, value in (
            ("calls_saved_vs_off", score["off"]["primitive_invocations"] - score["learned"]["primitive_invocations"]),
            ("calls_saved_vs_on", score["on"]["primitive_invocations"] - score["learned"]["primitive_invocations"]),
            ("candidates_saved_vs_off", score["off"]["tested_candidates"] - score["learned"]["tested_candidates"]),
            ("candidates_saved_vs_on", score["on"]["tested_candidates"] - score["learned"]["tested_candidates"]),
        ):
            samples[field].append(value)
    output = {}
    for field, values in samples.items():
        sorted_values = sorted(values)
        output[field] = {
            "ci95_percentile": [sorted_values[24], sorted_values[974]],
            "mean": statistics.mean(values),
            "min": min(values),
            "max": max(values),
        }
    return {"resamples": 1000, "seed": 260299, "cluster": "family",
            "clusters": len(families), "paired_aggregate_deltas": output,
            "warning": "Only seven family clusters; confidence intervals are descriptive, not evidence of broad transfer."}


def summarize(rows: list[dict], training_evidence: dict, phase: str) -> dict[str, object]:
    off, on, learned = (_score(rows, arm) for arm in ("off", "on", "learned"))
    differences = [int(r["learned"]["primitive_invocations"] - r["off"]["primitive_invocations"])
                   for r in rows]
    ood = [r for r in rows if r["family_for_evaluator_only"] == "replace_first"]
    oracle_off = [r for r in rows if r["oracle_source_action"] == "OFF"]
    oracle_on = [r for r in rows if r["oracle_source_action"] == "ON"]
    oracle_score = {}
    for metric in ("primitive_invocations", "tested_candidates", "audited_solved"):
        col = {"primitive_invocations": "primitive_invocations",
               "tested_candidates": "tested_candidates",
               "audited_solved": "audit_correct"}[metric]
        oracle_score[metric] = sum(
            r[r["oracle_source_action"]][col] if col != "tested_candidates"
            else r[r["oracle_source_action"]]["search"][col]
            for r in rows)
    families = {fam: {arm: _score([r for r in rows if r["family_for_evaluator_only"] == fam], arm)
                      for arm in ("off", "on", "learned")}
                for fam in sorted({r["family_for_evaluator_only"] for r in rows})}
    gains = {
        "vs_off_calls": off["primitive_invocations"] - learned["primitive_invocations"],
        "vs_on_calls": on["primitive_invocations"] - learned["primitive_invocations"],
        "vs_off_candidates": off["tested_candidates"] - learned["tested_candidates"],
        "vs_on_candidates": on["tested_candidates"] - learned["tested_candidates"],
    }
    p90 = _percentile_nearest_rank(differences, 0.90)
    ood_false_on = sum(r["policy_decision"]["action"] == "ON" for r in ood)
    gates = {
        "correctness": (learned["audited_solved"] >= off["audited_solved"]
                        and learned["audit_invalid_solved"] == 0),
        "vs_off": gains["vs_off_calls"] >= 32 and gains["vs_off_candidates"] >= 8,
        "vs_on": (on["primitive_invocations"] > 0 and on["tested_candidates"] > 0
                  and gains["vs_on_calls"] / on["primitive_invocations"] >= .05
                  and gains["vs_on_candidates"] / on["tested_candidates"] >= .05),
        "ood_false_on": len(ood) == 16 and ood_false_on <= 1 and learned["audit_invalid_solved"] == 0,
        "p90_tail": p90 <= 20,
    } if phase == "final" else {}
    training_cost = int(training_evidence["training_primitive_invocations"])
    avg_saved = gains["vs_off_calls"] / len(rows)
    amortization = {str(h): {"primitive_only_net_saved_calls_per_future_task":
                         avg_saved - training_cost / h,
                         "does_not_include_total_cpu_or_policy_overhead": True}
                    for h in (1, 32, 128)}
    decisions = [r["policy_decision"] for r in rows]
    sign = {"better_than_off": sum(d < 0 for d in differences),
            "equal_to_off": sum(d == 0 for d in differences),
            "worse_than_off": sum(d > 0 for d in differences)}
    return {
        "comparison": {"off": off, "on": on, "learned": learned, "oracle_diagnostic": oracle_score},
        "family": families,
        "deltas": gains,
        "bootstrap": _bootstrap(rows),
        "primitive_regressions_vs_off": {
            "median": statistics.median(differences),
            "p90_nearest_rank": p90,
            "max": max(differences),
            "worse_tasks": sign["worse_than_off"],
            "paired_sign_counts": sign,
        },
        "ood_replace_first_total": len(ood),
        "ood_false_on_activations": ood_false_on,
        "policy_decisions": {
            "on": sum(d["action"] == "ON" for d in decisions),
            "off": sum(d["action"] == "OFF" for d in decisions),
            "reasons": dict(sorted((reason, sum(d["reason"] == reason for d in decisions))
                                   for reason in {d["reason"] for d in decisions})),
            "inference_wall_ms": sum(d["inference_wall_ms"] for d in decisions),
        },
        "training_primitive_invocations": training_cost,
        "training_wall_ms": training_evidence["training_wall_ms"],
        "training_cpu_ms": training_evidence["training_cpu_ms"],
        "primitive_only_amortization_sensitivity": amortization,
        "numeric_acceptance_gates": gates,
        "numeric_status": ("metrics_pass_not_promoted" if all(gates.values())
                           else "not_demonstrated") if phase == "final" else "not_applicable_dev_smoke",
        "policy_adoption": "pending_independent_review" if phase == "final" else "not_applicable",
    }


def run_evaluation(phase: str, *, freeze_path: Path = FROZEN_RECORD):
    if phase not in ("dev", "final"):
        raise ValueError("Only DEV or FINAL evaluation are defined")
    frozen, manifest, training, policy = load_and_check_freeze(freeze_path)
    skill = _candidate()
    baseline = Registry(DEFAULT_PRIMITIVES)
    extended = registry_with_skill(skill, baseline)
    before = perf_counter()
    rows = [evaluate_record(item, policy, skill, baseline, extended)
            for item in generate_partition(phase)]
    total_wall = (perf_counter() - before) * 1000
    report = summarize(rows, training, phase)
    try:
        code_sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                  check=True, text=True, timeout=3).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        code_sha = None
    return {
        "experiment_id": "EXP-0002B",
        "phase": phase.upper(),
        "protocol": "EXP-0002B-PLAN-V2",
        "policy_sha256": frozen["policy_sha256"],
        "dataset_sha256": frozen["dataset_sha256"],
        "generator_source_sha256": frozen["generator_source_sha256"],
        "source_commit": code_sha,
        "source_train_code_commit": frozen["source_main_commit"],
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "run_total_wall_ms_excluding_train": total_wall,
        "training_evidence_excludes_final": True,
        "final_has_been_scored": phase == "final",
        "report": report,
        "tasks": rows,
        "caveats": ["Seven clusters only", "Seeds public; not blinded",
                    "Generator family is evaluation-only metadata; Kernel sees only TaskSpec",
                    "Primitive calls exclude policy/feature/whole-system time",
                    "ORACLE uses hindsight; not deployable",
                    "DEV is engineering smoke and cannot tune protocol"],
    }
