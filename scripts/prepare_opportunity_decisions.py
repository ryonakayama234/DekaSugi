"""OPPORTUNITY-001: pre-trial PUBLIC choice seal, never a scorer.

Run only after source-first hash lock verifies. This code has no OFF/ON
search, audit call or actual experiment outcome access.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from time import process_time, perf_counter

from scripts.verify_opportunity_generator_lock import verify_generator_lock

ARMS = ("B1", "B2", "B3")
METHOD = "OPPORTUNITY-001-PILOT-V1"


def digest(obj: object) -> str:
    return sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _build_decision_manifest(cases, snapshots, hashes, skill_body_hash,
                             chooser) -> dict[str, object]:
    """Pure decision assembly; evaluator-only case metadata never passed to chooser."""
    if len(cases) != 64 or len({c.task.task_id for c in cases}) != 64:
        raise ValueError("Expected 64 unique fresh pilot tasks")
    if set(snapshots) != set(ARMS) or set(hashes) != set(ARMS):
        raise ValueError("Expected three fixed KNN policy snapshots")
    if any(not isinstance(hashes[arm], str) or len(hashes[arm]) != 64 for arm in ARMS):
        raise ValueError("Bad policy snapshot hashes")
    rows = []
    cpu_sums = {arm: 0.0 for arm in ARMS}
    wall_sums = {arm: 0.0 for arm in ARMS}
    for case in cases:
        task = case.task
        if len(task.examples) != 2 or task.limits.max_ast_nodes != 4 or task.limits.max_candidates != 100:
            raise ValueError("Public TaskSpec/budget drift")
        decisions = {}
        for arm in ARMS:
            start_cpu, start_wall = process_time(), perf_counter()
            decision = chooser(task, snapshots[arm])  # TaskSpec ONLY
            cpu_sums[arm] += (process_time() - start_cpu) * 1000
            wall_sums[arm] += (perf_counter() - start_wall) * 1000
            if decision.action not in ("ON", "OFF"):
                raise ValueError("Invalid pretrial policy action")
            if type(decision.reason) is not str or not decision.reason:
                raise ValueError("Empty policy decision reason")
            decisions[arm] = {
                "action": decision.action,
                "reason": decision.reason,
            }
        rows.append({"task_id": task.task_id, "choices": decisions})
    if len(rows) != 64:
        raise ValueError("Incomplete pretrial decisions")
    payload = {
        "schema_version": "opportunity-pretrial-public-decisions-v1",
        "method": METHOD,
        "phase": "FRESH_TRAIN_ONLY",
        "source_manifest_sha256": "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85",
        "skill_body_sha256": skill_body_hash,
        "policy_snapshot_sha256": {arm: hashes[arm] for arm in ARMS},
        "decisions": rows,
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
    }
    return {"payload": payload,
            "payload_sha256": digest(payload),
            "inference_cost_ms": {
                "policy_cpu": cpu_sums, "policy_wall": wall_sums,
            }}


def build_pretrial_decisions() -> dict[str, object]:
    """Read-only source first. Rebuilding old TRAIN/DREAM is not evaluating old DEV."""
    source = verify_generator_lock()  # authenticates source before generator import
    if source["status"] != "source_identity_verified_not_scoring_authorized":
        raise ValueError("Unverified source lock")
    from packages.evaluation.opportunity_pilot import generate_train_pilot, canonical_public_digest
    from packages.exp0003a_dev import load_frozen_assets
    from packages.exp0003a.pr3 import choose

    cases = generate_train_pilot()
    if canonical_public_digest(cases) != source["public_manifest_sha256"]:
        raise ValueError("Public source identity drift")
    assets = load_frozen_assets()  # immutable old TRAIN/DREAM assets only, no DEV/FINAL generation
    lock = json.loads(Path(__file__).resolve().parents[1].joinpath(
        "experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json").read_text(encoding="utf-8"))
    if (assets.skill.body_hash != lock["historic_top_skill_body_sha256"]
            or assets.skill.skill_id != lock["historic_top_skill_id"]
            or assets.snapshot_hashes != lock["historic_policy_snapshot_sha256"]):
        raise ValueError("Policy/skill frozen identity mismatch")
    result = _build_decision_manifest(cases, assets.snapshots,
                                      assets.snapshot_hashes, assets.skill.body_hash, choose)
    if result["payload"]["source_manifest_sha256"] != source["public_manifest_sha256"]:
        raise ValueError("Pretrial public identity mismatch")
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="OPPORTUNITY-001 pretrial decisions only; NEVER score")
    parser.add_argument("--mode", required=True, choices=("decisions-hash-only",))
    parser.add_argument("--output", type=Path, help="Create PUBLIC decision manifest; fail if path exists")
    args = parser.parse_args()
    result = build_pretrial_decisions()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as f:
            json.dump(result["payload"], f, sort_keys=True, ensure_ascii=False, indent=2)
            f.write("\n")
    print(json.dumps({
        "schema_version": "opportunity-pretrial-seal-preflight-v1",
        "source_manifest_sha256": result["payload"]["source_manifest_sha256"],
        "policy_snapshot_sha256": result["payload"]["policy_snapshot_sha256"],
        "decision_payload_sha256": result["payload_sha256"],
        "task_count": 64,
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
        "status": "pretrial_choices_computed_not_scoring_authorized",
    }, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
