"""EXP-0003A PR5: independent, read-only DEV64 engineering evaluator.

This file is OUTSIDE all 14 frozen source blobs. Importing it cannot score a
holdout. PR CI must never call run_dev() or generate_partition("dev").
Scientific method: experiments/EXP-0003A/plan.md (immutable v1).
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
from time import perf_counter, process_time
from typing import Mapping

from packages.exp0003a import FAMILIES, TrainCase, _audit_ref, digest, opaque_id
from packages.exp0003a.freeze import _record, generate_partition, verify_frozen
from packages.exp0003a.pr3 import ArmSnapshot, _audited_trial, choose, run_train_dream
from packages.learning import SkillCandidate, registry_with_skill, validate_skill
from packages.library import DEFAULT_PRIMITIVES, Registry
from packages.protocol import parse_program


ARMS = ("B0", "B1", "B2", "B3")
SCHEMA = "exp0003a-dev-engineering-v1"
DEV_COUNT = 64
BOOTSTRAP_SEED = 260303
BOOTSTRAP_ROUNDS = 1000


@dataclass(frozen=True, slots=True)
class FrozenAssets:
    freeze: dict[str, object]
    snapshots: Mapping[str, ArmSnapshot]
    snapshot_hashes: Mapping[str, str]
    skill: SkillCandidate
    training_cost_ms: dict[str, object]


def _rehydrate_skill(raw: object) -> SkillCandidate:
    if not isinstance(raw, dict):
        raise ValueError("Missing TRAIN-derived top skill")
    skill = SkillCandidate(
        skill_id=raw["skill_id"], body_ast=parse_program(raw["body_ast"]),
        body_hash=raw["body_hash"],
        dependencies=tuple(raw["dependencies"]),
        provenance=tuple(raw["provenance"]),
        occurrences=raw["occurrences"],
        status=raw["status"], schema_version=raw["schema_version"],
    )
    validate_skill(skill, Registry(DEFAULT_PRIMITIVES))
    return skill


def load_frozen_assets() -> FrozenAssets:
    """Fail before holdout generation and before choosing/scoring any DEV task.

    verify_frozen() first compares inert manifest/schema and all pinned source
    bytes, then deterministically rebuilds TRAIN/DREAM. The second rebuild
    obtains ephemeral snapshots/skill without writing or modifying the freeze.
    """
    frozen = verify_frozen()
    if frozen.get("holdout_scoring_permitted") is not False:
        raise ValueError("Freeze permission drift; DEV requires a separate gate")
    report, _private = run_train_dream()
    if report.get("dev_or_final_evaluated") is not False:
        raise ValueError("Training pipeline unexpectedly scored holdout")
    if report.get("registry_promotion") != "not_authorized":
        raise ValueError("Unexpected skill promotion")
    if report["source_manifest_sha256"] != frozen["split_data"]["pr3_source_manifest_sha256"]:
        raise ValueError("TRAIN/DREAM source provenance drift")
    skill = _rehydrate_skill(report["top_skill"])
    if (skill.skill_id != frozen["policy"]["top_skill_id"]
            or skill.body_hash != frozen["policy"]["top_skill_body_sha256"]):
        raise ValueError("Frozen top-skill mismatch")
    snapshots: dict[str, ArmSnapshot] = {}
    hashes: dict[str, str] = {}
    for arm in ARMS[1:]:
        raw = report["snapshots"][arm]
        snapshot = ArmSnapshot.from_dict(raw)
        expected = frozen["policy"]["snapshot_sha256"][arm]
        if (snapshot.arm != arm or raw["policy_snapshot_sha256"] != expected
                or report["snapshot_hashes"][arm] != expected
                or snapshot.skill_id != skill.skill_id
                or snapshot.skill_body_sha256 != skill.body_hash):
            raise ValueError(f"Frozen {arm} policy/skill mismatch")
        if arm != "B1" and (
            list(snapshot.ordered_selected_pool_ids)
            != frozen["policy"][arm.lower() + "_ordered_selected_pool_ids"]
            or list(snapshot.ordered_selected_task_ids)
            != frozen["policy"][arm.lower() + "_ordered_selected_task_ids"]
        ):
            raise ValueError(f"Frozen {arm} DREAM selection mismatch")
        snapshots[arm] = snapshot
        hashes[arm] = expected
    return FrozenAssets(frozen, snapshots, hashes, skill, report["cost_ms"])


def validate_dev_cases(cases: tuple[TrainCase, ...],
                       frozen: dict[str, object]) -> None:
    """Match the entire independently generated DEV split to its sealed hash."""
    if len(cases) != DEV_COUNT:
        raise ValueError("DEV64 cardinality mismatch")
    if (len({c.task.task_id for c in cases}) != DEV_COUNT
            or len({c.source_record_id for c in cases}) != DEV_COUNT
            or len({s for c in cases for s in c.seeds}) != 3 * DEV_COUNT):
        raise ValueError("DEV task/source/seed duplication")
    for i, case in enumerate(cases):
        family_index, case_index = divmod(i, 8)
        if (case.family != FAMILIES[family_index]
                or case.source_record_id != f"dev-f{family_index:02d}-i{case_index:03d}"
                or len(case.task.examples) != 2
                or case.task.task_id != opaque_id(case.task.examples)):
            raise ValueError("DEV public/private record mismatch")
    sealed = frozen["split_data"]
    if (digest([_record(c) for c in cases]) != sealed["split_sha256"]["dev"]
            or digest([c.task.task_id for c in cases])
            != sealed["ordered_public_task_ids_sha256"]["dev"]
            or digest([c.source_record_id for c in cases])
            != sealed["ordered_source_ids_sha256"]["dev"]):
        raise ValueError("DEV dataset differs from immutable pre-DEV seal")


def evaluate_case(case: TrainCase, assets: FrozenAssets) -> dict[str, object]:
    """Select all three policies from public TaskSpec BEFORE any arm executes."""
    if case.source_record_id.split("-", 1)[0] not in ("train", "dev"):
        raise ValueError("Only TRAIN fixture or DEV case allowed; FINAL forbidden")
    if case.task.task_id != opaque_id(case.task.examples):
        raise ValueError("Noncanonical public TaskSpec")
    # The chooser gets exactly TaskSpec, never case/family/audit/seed.
    decisions = {arm: choose(case.task, assets.snapshots[arm])
                 for arm in ARMS[1:]}
    canonical = Registry(DEFAULT_PRIMITIVES)
    validate_skill(assets.skill, canonical)
    result = {}
    for arm in ARMS:
        decision = decisions.get(arm)
        enabled = arm != "B0" and decision.action == "ON"
        if arm != "B0" and decision.action not in ("ON", "OFF"):
            raise ValueError("Unknown policy choice")
        # New pristine registry and fresh PrimitiveCallMeter in _audited_trial.
        registry = registry_with_skill(assets.skill, canonical) if enabled else Registry(DEFAULT_PRIMITIVES)
        learned = {assets.skill.skill_id: assets.skill} if enabled else {}
        (evidence, candidates, calls, correct, false_solved,
         search_cpu, search_wall, audit_cpu, audit_wall) = _audited_trial(
            case.task, case.private_audit, registry, learned
        )
        if (candidates != evidence["search"]["tested_candidates"]
                or calls != evidence["meter"]["primitive_invocations"]
                or bool(evidence["audit_correct"]) != correct
                or bool(evidence["audit_invalid_solved"]) != false_solved):
            raise ValueError("Trial evidence/canonical-meter mismatch")
        if not all(math.isfinite(v) and v >= 0 for v in
                   (search_cpu, search_wall, audit_cpu, audit_wall)):
            raise ValueError("Invalid CPU/wall observation")
        result[arm] = {
            "decision": "OFF" if decision is None else decision.action,
            "decision_reason": "no_learned_policy" if decision is None else decision.reason,
            "neighbors": [] if decision is None else list(decision.neighbors),
            "policy_snapshot_sha256": assets.snapshot_hashes.get(arm),
            "audit_ref": _audit_ref(case.task.task_id, case.private_audit),
            "audited_correct": correct, "false_solved": false_solved,
            "tested_candidates": candidates,
            "primitive_invocations": calls,
            "search_cpu_ms": search_cpu, "search_wall_ms": search_wall,
            "audit_cpu_ms": audit_cpu, "audit_wall_ms": audit_wall,
            "search": evidence["search"], "meter": evidence["meter"],
            "selected_ast": evidence["selected_ast"],
        }
    return {"task_id": case.task.task_id, "arms": result}


def _bootstrap_family_delta(rows: list[dict[str, object]],
                            by_id: dict[str, TrainCase]) -> list[int]:
    """DEV descriptive interval, NOT a confirmatory inference or gate."""
    per_family: dict[str, list[int]] = {f: [] for f in FAMILIES}
    for row in rows:
        arms = row["arms"]
        per_family[by_id[row["task_id"]].family].append(
            arms["B2"]["primitive_invocations"] - arms["B3"]["primitive_invocations"]
        )
    if any(len(v) != 8 for v in per_family.values()):
        raise ValueError("DEV family pairing/cardinality drift")
    totals = [sum(v) for v in per_family.values()]
    rng = random.Random(BOOTSTRAP_SEED)
    return sorted(sum(totals[rng.randrange(8)] for _ in range(8))
                  for _ in range(BOOTSTRAP_ROUNDS))


def summarize(rows: list[dict[str, object]],
              cases: tuple[TrainCase, ...]) -> dict[str, object]:
    by_id = {c.task.task_id: c for c in cases}
    if (len(rows) != DEV_COUNT or len(by_id) != DEV_COUNT
            or len({r["task_id"] for r in rows}) != DEV_COUNT
            or {r["task_id"] for r in rows} != set(by_id)):
        raise ValueError("Cannot summarize unpaired/incomplete DEV64")
    totals = {}
    for arm in ARMS:
        trials = [r["arms"][arm] for r in rows]
        totals[arm] = {
            "audited_correct": sum(t["audited_correct"] for t in trials),
            "false_solved": sum(t["false_solved"] for t in trials),
            "tested_candidates": sum(t["tested_candidates"] for t in trials),
            "primitive_invocations": sum(t["primitive_invocations"] for t in trials),
            "selected_on": sum(t["decision"] == "ON" for t in trials),
            "search_cpu_ms": sum(t["search_cpu_ms"] for t in trials),
            "audit_cpu_ms": sum(t["audit_cpu_ms"] for t in trials),
            "search_wall_ms": sum(t["search_wall_ms"] for t in trials),
            "audit_wall_ms": sum(t["audit_wall_ms"] for t in trials),
        }
    diff_calls = [r["arms"]["B2"]["primitive_invocations"]
                  - r["arms"]["B3"]["primitive_invocations"] for r in rows]
    diff_candidates = [r["arms"]["B2"]["tested_candidates"]
                       - r["arms"]["B3"]["tested_candidates"] for r in rows]
    sorted_boot = _bootstrap_family_delta(rows, by_id)
    ood = {arm: sum(
        r["arms"][arm]["decision"] == "ON"
        for r in rows if by_id[r["task_id"]].family.endswith("_ood"))
           for arm in ARMS}
    return {
        "task_count": DEV_COUNT, "arm_totals": totals,
        "paired_B2_minus_B3": {
            "primitive_invocations": sum(diff_calls),
            "tested_candidates": sum(diff_candidates),
            "audited_correct_B3_minus_B2":
                totals["B3"]["audited_correct"] - totals["B2"]["audited_correct"],
            "primitive_regressions": sum(d < 0 for d in diff_calls),
            "primitive_improvements": sum(d > 0 for d in diff_calls),
            "family_cluster_bootstrap_95pct_total_calls_delta":
                [sorted_boot[24], sorted_boot[974]],
            "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_rounds": BOOTSTRAP_ROUNDS,
        },
        "ood_false_on_counts": ood,
        "family_summary": {
            f: {arm: {
                "audited_correct": sum(r["arms"][arm]["audited_correct"]
                    for r in rows if by_id[r["task_id"]].family == f),
                "primitive_invocations": sum(r["arms"][arm]["primitive_invocations"]
                    for r in rows if by_id[r["task_id"]].family == f),
            } for arm in ARMS} for f in FAMILIES
        },
        "interpretation": "DEV64 engineering diagnostics only; not an independent FINAL confirmation.",
    }


def require_reviewed_main_push(env: Mapping[str, str] | None = None) -> None:
    """Deployment guard, NOT a cryptographic approval mechanism."""
    env = os.environ if env is None else env
    if (env.get("GITHUB_EVENT_NAME") != "push"
            or env.get("GITHUB_REF") != "refs/heads/main"
            or env.get("EXP0003A_DEV_APPROVED") != "reviewed-main-only"):
        raise PermissionError("DEV64 requires separately reviewed main-push activation")
    actual = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, check=True,
        text=True, timeout=5,
    ).stdout.strip()
    if actual != env.get("GITHUB_SHA"):
        raise PermissionError("Source checkout does not match trusted CI event SHA")


def run_dev() -> tuple[dict[str, object], dict[str, object]]:
    """DEV is called only by separately gated CI, never PR tests or import."""
    require_reviewed_main_push()
    assets = load_frozen_assets()  # MUST precede generate_partition("dev")
    start_cpu, start_wall = process_time(), perf_counter()
    cases = generate_partition("dev")
    validate_dev_cases(cases, assets.freeze)
    prep_cpu_ms = (process_time() - start_cpu) * 1000
    prep_wall_ms = (perf_counter() - start_wall) * 1000
    start_cpu, start_wall = process_time(), perf_counter()
    rows = [evaluate_case(c, assets) for c in cases]
    eval_cpu_ms = (process_time() - start_cpu) * 1000
    eval_wall_ms = (perf_counter() - start_wall) * 1000
    summary = summarize(rows, cases)
    source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, check=True,
        text=True, timeout=5,
    ).stdout.strip()
    public = {
        "schema_version": SCHEMA, "experiment": "EXP-0003A",
        "phase": "DEV_ENGINEERING", "status": "engineering_only",
        "source_commit": source_sha, "python_version": platform.python_version(),
        "freeze_payload_sha256": assets.freeze["freeze_payload_sha256"],
        "dev_dataset_sha256": assets.freeze["split_data"]["split_sha256"]["dev"],
        "snapshot_sha256": dict(assets.snapshot_hashes),
        "skill_id": assets.skill.skill_id, "skill_body_sha256": assets.skill.body_hash,
        "summary": summary, "trial_rows": rows,
        "phase_cost_ms": {
            "dev_generation_validation_cpu": prep_cpu_ms,
            "dev_generation_validation_wall": prep_wall_ms,
            "dev_four_arm_cpu": eval_cpu_ms, "dev_four_arm_wall": eval_wall_ms,
            "train_dream_rebuild_cost_ms": assets.training_cost_ms,
        },
        "final_evaluated": False, "registry_promoted": False,
        "claims": "no confirmatory inference, no skill promotion, no total-CPU benefit claimed",
    }
    private = {
        "schema_version": "exp0003a-dev-evaluator-private-v1",
        "phase": "DEV_ENGINEERING", "source_commit": source_sha,
        "dev_dataset_sha256": public["dev_dataset_sha256"],
        "source_records": [_record(c) for c in cases],
        "public_trial_rows_sha256": digest(rows),
    }
    return public, private


def write_once(path: Path, value: dict[str, object]) -> str:
    """Append-only artifact semantics; never overwrite previous evidence."""
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(raw)
    return sha256(raw).hexdigest()
