"""OPPORTUNITY-001 Issue #68: read-only verifier and one-time public choice custody.

Never scores a trial, opens an old DEV/FINAL, or reads a private audit.
Network/API provenance is supplied by GitHub Actions, not trusted caller flags.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ORIGIN_COMMIT = "c6b01c2a856a989e9b642fbe211cfd195f0e57e3"
ORIGIN_RUN = 40659741488
ORIGIN_JOB = 122719482732
ORIGIN_ARTIFACT = 12803053107
ORIGIN_ARTIFACT_NAME = "OPPORTUNITY-001-PILOT-V1-public-choices-only"
ORIGIN_MEMBER = "OPPORTUNITY-001-pretrial-public.json"
ORIGINAL_MEMBER_SHA256 = "1d08e6c1518d6730e75bfaf3033a00884f7517a7d91c98a5dfff75192aabc433"
DECISION_SHA256 = "8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2"
SOURCE_SHA256 = "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"
SKILL_SHA256 = "8fe1361cb5014f8503e4a57392e45f4fc7607e788fdd598f66668fbc11338eff"
SNAPSHOTS = {
    "B1": "3b4fc00f8ad0fe2f1cc0978886d7bc7a6285ed002c842ceeb0106fd51ee5afd4",
    "B2": "01d5595e1b4c32d200e2734630f38a848e77a64f356741445e011865834f5af7",
    "B3": "a6d46ab5dd697e8e90789693fdd3bd67bbca445ec07bc8b119401e1c0cf1e210",
}
REASONS = frozenset({
    "insufficient_support", "audit_safety_veto", "insufficient_on_votes",
    "insufficient_call_saving", "cost_supported",
})
ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATH = ROOT / "experiments/OPPORTUNITY-001/evidence/pilot-choices-public-v1.json"
LOCK_PATH = ROOT / "experiments/OPPORTUNITY-001/pilot-choice-lock-v1.json"
MAX_PUBLIC_BYTES = 100_000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def pairs_unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> object:
    raise ValueError("nonfinite JSON numeric literal: " + value)


def parse_strict(data: bytes) -> object:
    if type(data) is not bytes or len(data) > MAX_PUBLIC_BYTES:
        raise ValueError("missing or oversized public member bytes")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs_unique,
                          parse_constant=reject_constant)
    except (UnicodeError, TypeError) as exc:
        raise ValueError("invalid public UTF-8 JSON") from exc


def exact(obj: object, keys: set[str], label: str) -> dict:
    if type(obj) is not dict or set(obj) != keys:
        raise ValueError(label + ": unexpected/missing/private keys")
    return obj


def validate_payload(raw: bytes, *, require_original: bool = True) -> dict:
    if require_original and sha(raw) != ORIGINAL_MEMBER_SHA256:
        raise ValueError("original public member raw bytes mismatch")
    obj = exact(parse_strict(raw), {
        "schema_version", "method", "phase", "source_manifest_sha256",
        "skill_body_sha256", "policy_snapshot_sha256", "decisions",
        "paired_trials_executed", "dev_or_final_evaluated",
    }, "payload")
    if (obj["schema_version"] != "opportunity-pretrial-public-decisions-v1"
            or obj["method"] != "OPPORTUNITY-001-PILOT-V1"
            or obj["phase"] != "FRESH_TRAIN_ONLY"
            or obj["source_manifest_sha256"] != SOURCE_SHA256
            or obj["skill_body_sha256"] != SKILL_SHA256
            or obj["policy_snapshot_sha256"] != SNAPSHOTS
            or type(obj["paired_trials_executed"]) is not int
            or obj["paired_trials_executed"] != 0
            or obj["dev_or_final_evaluated"] is not False):
        raise ValueError("frozen identity or scoring permission drift")
    rows = obj["decisions"]
    if type(rows) is not list or len(rows) != 64:
        raise ValueError("expected exactly 64 decision rows")
    seen = set()
    for row in rows:
        row = exact(row, {"task_id", "choices"}, "decision row")
        task_id = row["task_id"]
        if (type(task_id) is not str or
                re.fullmatch(r"t-[0-9a-f]{64}", task_id) is None or task_id in seen):
            raise ValueError("invalid/duplicate task ID")
        seen.add(task_id)
        choices = exact(row["choices"], set(SNAPSHOTS), "choice set")
        for arm in SNAPSHOTS:
            decision = exact(choices[arm], {"action", "reason"}, "policy decision")
            action, reason = decision["action"], decision["reason"]
            if (type(action) is not str or action not in ("ON", "OFF")
                    or type(reason) is not str or reason not in REASONS
                    or (action == "ON") != (reason == "cost_supported")):
                raise ValueError("action/reason contradiction")
    if sha(canonical(obj)) != DECISION_SHA256:
        raise ValueError("canonical decision payload digest mismatch")
    return obj


def validate_origin(run: dict, job: dict, artifact: dict) -> dict:
    """Validate API observations before treating downloaded bytes as official."""
    if (type(run) is not dict or run.get("id") != ORIGIN_RUN
            or run.get("head_sha") != ORIGIN_COMMIT or run.get("head_branch") != "main"
            or run.get("event") != "push" or run.get("status") != "completed"
            or run.get("conclusion") != "success"):
        raise ValueError("official main run identity/status mismatch")
    if (type(job) is not dict or job.get("id") != ORIGIN_JOB
            or job.get("run_id") != ORIGIN_RUN or job.get("status") != "completed"
            or job.get("conclusion") != "success" or job.get("head_sha") != ORIGIN_COMMIT):
        raise ValueError("official main job identity/status mismatch")
    origin = artifact.get("workflow_run") if type(artifact) is dict else None
    if (type(artifact) is not dict or artifact.get("id") != ORIGIN_ARTIFACT
            or artifact.get("name") != ORIGIN_ARTIFACT_NAME
            or artifact.get("expired") is not False
            or type(origin) is not dict or origin.get("id") != ORIGIN_RUN
            or origin.get("head_sha") != ORIGIN_COMMIT):
        raise ValueError("official public artifact identity/retention mismatch")
    return {
        "main_commit": ORIGIN_COMMIT,
        "workflow_run_id": ORIGIN_RUN,
        "job_id": ORIGIN_JOB,
        "artifact_id": ORIGIN_ARTIFACT,
        "artifact_name": ORIGIN_ARTIFACT_NAME,
        "member_name": ORIGIN_MEMBER,
        "run_created_at": run.get("created_at"),
        "run_updated_at": run.get("updated_at"),
        "artifact_created_at": artifact.get("created_at"),
        "artifact_expires_at": artifact.get("expires_at"),
    }


def make_lock(origin: dict) -> dict:
    return {
        "schema_version": "pilot-choice-lock-v1",
        "status": "verified_public_pretrial_origin_only",
        "method_id": "OPPORTUNITY-001-PILOT-V1",
        "origin": origin,
        "original_public_member_raw_sha256": ORIGINAL_MEMBER_SHA256,
        "copied_public_member_raw_sha256": ORIGINAL_MEMBER_SHA256,
        "decision_payload_sha256": DECISION_SHA256,
        "public_manifest_sha256": SOURCE_SHA256,
        "skill_body_sha256": SKILL_SHA256,
        "policy_snapshot_sha256": SNAPSHOTS,
        "public_copy_path": "experiments/OPPORTUNITY-001/evidence/pilot-choices-public-v1.json",
        "task_count": 64,
        "decision_count": 192,
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
        "new_train_pilot_scoring_permitted": False,
        "old_dev_or_final_scoring_permitted": False,
        "independent_private_raw_custody_verified": False,
        "actual_scorer_approved": False,
        "once_only_activation_approved": False,
    }


def verify_custody(raw: bytes, lock_bytes: bytes) -> dict:
    validate_payload(raw)
    lock = exact(parse_strict(lock_bytes), set(make_lock({})), "choice lock")
    if lock != make_lock(lock["origin"]):
        raise ValueError("public choice lock metadata/permissons mismatch")
    if exact(lock["origin"], {
        "main_commit", "workflow_run_id", "job_id", "artifact_id",
        "artifact_name", "member_name", "run_created_at", "run_updated_at",
        "artifact_created_at", "artifact_expires_at",
    }, "origin") != lock["origin"]:
        raise ValueError("origin metadata mismatch")
    # Check known identifiers, while preserving the API-observed timestamps.
    for key, expected in {
        "main_commit": ORIGIN_COMMIT, "workflow_run_id": ORIGIN_RUN,
        "job_id": ORIGIN_JOB, "artifact_id": ORIGIN_ARTIFACT,
        "artifact_name": ORIGIN_ARTIFACT_NAME, "member_name": ORIGIN_MEMBER,
    }.items():
        if lock["origin"][key] != expected:
            raise ValueError("origin mismatch " + key)
    if not all(type(lock["origin"][k]) is str and lock["origin"][k] for k in
               ("run_created_at", "run_updated_at", "artifact_created_at", "artifact_expires_at")):
        raise ValueError("origin timestamps missing")
    if sha(raw) != lock["original_public_member_raw_sha256"]:
        raise ValueError("retained public copy does not match original digest")
    return lock


def save_exact(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("destination already exists with different original bytes: " + str(path))
        return
    with path.open("xb") as f:
        f.write(data)


def capture(member: Path, run: Path, job: Path, artifact: Path) -> None:
    if member.name != ORIGIN_MEMBER or member.is_symlink():
        raise ValueError("unrecognized or symlinked original public member")
    # Public member bytes, unchanged by JSON pretty-printer or newline conversion.
    raw = member.read_bytes()
    validate_payload(raw)
    origin = validate_origin(
        parse_strict(run.read_bytes()), parse_strict(job.read_bytes()),
        parse_strict(artifact.read_bytes()),
    )
    lock = make_lock(origin)
    save_exact(PUBLIC_PATH, raw)
    save_exact(LOCK_PATH, json.dumps(lock, sort_keys=True, indent=2,
                                     ensure_ascii=False, allow_nan=False).encode() + b"\n")
    verify_custody(PUBLIC_PATH.read_bytes(), LOCK_PATH.read_bytes())
    print(json.dumps({"status": "verified_public_pretrial_origin_only",
                      "raw_member_sha256": sha(raw),
                      "canonical_decision_payload_sha256": sha(canonical(parse_strict(raw))),
                      "task_count": 64, "decision_count": 192,
                      "paired_trials_executed": 0, "scoring_permitted": False},
                     sort_keys=True))


def main() -> int:
    ap = argparse.ArgumentParser(description="Source-only pretrial public custody; NEVER score")
    ap.add_argument("--mode", choices=("capture", "verify", "compare-replay"), required=True)
    ap.add_argument("--member", type=Path)
    ap.add_argument("--run-json", type=Path)
    ap.add_argument("--job-json", type=Path)
    ap.add_argument("--artifact-json", type=Path)
    ap.add_argument("--replay", type=Path)
    ns = ap.parse_args()
    if ns.mode == "capture":
        if not all((ns.member, ns.run_json, ns.job_json, ns.artifact_json)):
            ap.error("capture requires official origin files")
        capture(ns.member, ns.run_json, ns.job_json, ns.artifact_json)
    else:
        raw, lock_bytes = PUBLIC_PATH.read_bytes(), LOCK_PATH.read_bytes()
        verify_custody(raw, lock_bytes)
        if ns.mode == "compare-replay":
            if ns.replay is None:
                ap.error("compare-replay requires --replay")
            replay = parse_strict(ns.replay.read_bytes())
            validate_payload(raw)
            if replay != parse_strict(raw):
                raise ValueError("source-first TRAIN/DREAM-only chooser replay differs from original")
        print(json.dumps({"status": "verified_public_pretrial_origin_only",
                          "raw_sha256": sha(raw), "decision_payload_sha256": DECISION_SHA256,
                          "paired_trials_executed": 0, "scoring_permitted": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
