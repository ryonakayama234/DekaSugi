"""OPPORTUNITY-001 source-first, hash-only frozen pilot generator verifier.

No paired evaluator, old DEV/FINAL generation or scored data access.
A source lock is necessary but insufficient for independent outcome evidence.
"""
from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json"
REQUIRED_SOURCE_FILES = frozenset((
    "scripts/verify_opportunity_generator_lock.py",
    "packages/evaluation/opportunity_pilot.py",
    "scripts/audit_opportunity_pilot_public.py",
    "packages/exp0003a/__init__.py",
    "packages/protocol/__init__.py",
    "packages/evaluation/__init__.py",
    ".github/workflows/docs-check.yml",
    "experiments/EXP-0003A/freeze-v1.json",
    "experiments/OPPORTUNITY-001/pilot-v1.md",
))
REQUIRED_LOCK_KEYS = frozenset((
    "schema_version", "method_id", "source_main_commit",
    "python_version", "source_git_blobs", "public_manifest_sha256",
    "third_audit_commitments_sha256", "historic_exp0003a_freeze_payload_sha256",
    "historic_top_skill_id", "historic_top_skill_body_sha256",
    "historic_policy_snapshot_sha256", "evidence_origin",
    "new_train_pilot_scoring_permitted", "old_dev_or_final_scoring_permitted",
))


def _hex(value: object, n: int) -> bool:
    return type(value) is str and re.fullmatch(f"[0-9a-f]{{{n}}}", value) is not None


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate_source_blobs(lock: dict, root: Path) -> None:
    """Fail BEFORE importing or generating any project TaskSpec."""
    if not isinstance(lock, dict) or set(lock) != REQUIRED_LOCK_KEYS:
        raise ValueError("Source lock shape drift")
    if lock["schema_version"] != "OPPORTUNITY-PILOT-GENERATOR-LOCK-V1":
        raise ValueError("Unexpected source lock version")
    if lock["method_id"] != "OPPORTUNITY-001-PILOT-V1":
        raise ValueError("Unexpected pilot method")
    if lock["source_main_commit"] != "50bad2c7b31d21492e895a19ea107b82734e49fd":
        raise ValueError("Unexpected immutable main source commit")
    if type(lock["python_version"]) is not str or not re.fullmatch(r"3\.12\.\d+", lock["python_version"]):
        raise ValueError("Unsupported source Python version")
    for key in ("public_manifest_sha256", "third_audit_commitments_sha256",
                "historic_exp0003a_freeze_payload_sha256",
                "historic_top_skill_body_sha256"):
        if not _hex(lock[key], 64):
            raise ValueError(f"Bad lock hash for {key}")
    if lock["public_manifest_sha256"] != "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85":
        raise ValueError("Unexpected public source commitment")
    if lock["third_audit_commitments_sha256"] != "fd4a1afd1eae84026a526d82a75cec13107dfd394f86d166c7efca4763a52eaa":
        raise ValueError("Unexpected audit source commitment")
    if lock["new_train_pilot_scoring_permitted"] is not False or lock["old_dev_or_final_scoring_permitted"] is not False:
        raise ValueError("No scoring authorization in generator source lock")
    if lock["historic_top_skill_id"] != "skill_8fe1361cb5014f85":
        raise ValueError("Frozen skill identifier mismatch")
    snapshots = lock["historic_policy_snapshot_sha256"]
    if (not isinstance(snapshots, dict) or
            set(snapshots) != {"B1", "B2", "B3"} or
            any(not _hex(snapshots[k], 64) for k in snapshots)):
        raise ValueError("Missing frozen KNN snapshot hashes")
    files = lock["source_git_blobs"]
    if not isinstance(files, dict) or set(files) != REQUIRED_SOURCE_FILES:
        raise ValueError("Wrong source file coverage")
    for file_name in sorted(REQUIRED_SOURCE_FILES):
        if not _hex(files[file_name], 40):
            raise ValueError("Malformed source blob SHA")
        path = root / file_name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing/symlinked source file: {file_name}")
        if _git_blob_sha(path) != files[file_name]:
            raise ValueError(f"Source byte drift: {file_name}")
    if not isinstance(lock["evidence_origin"], dict) or set(lock["evidence_origin"]) != {"run_id","job_id","reviewed_pr"}:
        raise ValueError("Missing source CI provenance")
    for k in ("run_id","job_id","reviewed_pr"):
        if type(lock["evidence_origin"][k]) is not int or lock["evidence_origin"][k] <= 0:
            raise ValueError("Invalid source CI provenance")


def verify_generator_lock(root: Path = ROOT) -> dict[str, object]:
    """Read-only preflight. Does not score new or historic task partitions."""
    lock_file = root / "experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json"
    lock = json.loads(lock_file.read_text(encoding="utf-8"))
    validate_source_blobs(lock, root)   # Hard gate before any project imports
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Source lock verification requires Python 3.12")
    version = ".".join(map(str, sys.version_info[:3]))
    if version != lock["python_version"]:
        raise ValueError("Python patch version mismatch")
    freeze = json.loads((root/"experiments/EXP-0003A/freeze-v1.json").read_text(encoding="utf-8"))
    if freeze["freeze_payload_sha256"] != lock["historic_exp0003a_freeze_payload_sha256"]:
        raise ValueError("Legacy freeze payload drift")
    policy = freeze["policy"]
    if policy["top_skill_id"] != lock["historic_top_skill_id"] or policy["top_skill_body_sha256"] != lock["historic_top_skill_body_sha256"]:
        raise ValueError("Frozen candidate skill mismatch")
    if policy["snapshot_sha256"] != lock["historic_policy_snapshot_sha256"]:
        raise ValueError("Frozen B1/B2/B3 snapshots mismatch")

    # Only AFTER all source SHA and frozen-identity checks may public generation run.
    from packages.evaluation.opportunity_pilot import public_preflight
    from scripts.audit_opportunity_pilot_public import verify_public
    generated = public_preflight()
    independently = verify_public()
    if generated["task_count"] != 64 or independently["public_count"] != 64:
        raise ValueError("Pilot population count drift")
    if (generated["public_manifest_sha256"] != lock["public_manifest_sha256"] or
            independently["public_manifest_sha256"] != lock["public_manifest_sha256"] or
            independently["third_audit_commitments_sha256"] != lock["third_audit_commitments_sha256"]):
        raise ValueError("Pinned public/private source commitment drift")
    if (generated["paired_trials_executed"] != 0 or
            independently["paired_trials_executed"] != 0 or
            generated["dev_or_final_evaluated"] is not False or
            independently["dev_or_final_evaluated"] is not False):
        raise ValueError("Unexpected scoring in source preflight")
    return {
        "schema_version": "opportunity-generator-lock-preflight-v1",
        "status": "source_identity_verified_not_scoring_authorized",
        "source_main_commit": lock["source_main_commit"],
        "public_manifest_sha256": lock["public_manifest_sha256"],
        "third_audit_commitments_sha256": lock["third_audit_commitments_sha256"],
        "source_file_count": len(REQUIRED_SOURCE_FILES),
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify_generator_lock(), sort_keys=True, allow_nan=False))
