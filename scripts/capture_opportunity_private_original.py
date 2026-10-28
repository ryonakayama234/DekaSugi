"""OPPORTUNITY-001: source-first, manually armed private TRAIN64 origin capture.

NEVER performs search, audit scoring, policy learning, or holdout generation.
Not invoked by GitHub Actions. Actual generation requires the explicit
--capture-before-scoring CLI flag on a trusted private host (Python 3.12.15).
No source/private data is printed. Two independent storage providers, ACL
and retention must still be externally certified before one-shot scoring.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_RAW_BYTES = 256_000
METHOD = "OPPORTUNITY-001-PILOT-V1"
SCHEMA = "opportunity-private-audit-original-v1"
THIRD_COMMITMENT = "fd4a1afd1eae84026a526d82a75cec13107dfd394f86d166c7efca4763a52eaa"
PUBLIC_MANIFEST = "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"
CHOICES_CANONICAL = "8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2"
CHOICES_RAW = "1d08e6c1518d6730e75bfaf3033a00884f7517a7d91c98a5dfff75192aabc433"


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(obj: object) -> str:
    return sha256(canonical(obj)).hexdigest()


def _fail() -> None:
    raise ValueError("private original capture failed closed")


def _sealed_source_and_public_choices() -> tuple[object, dict]:
    """This call is the ONLY real-source generation entry; no scorer imports."""
    if any(n == "packages" or n.startswith("packages.") for n in sys.modules):
        _fail()  # project package was imported ahead of source verification
    from scripts.verify_opportunity_legacy_sources import verify_legacy_source_bytes
    historic = verify_legacy_source_bytes(ROOT)
    if historic["verified_source_count"] != 14 or historic["dev_or_final_generated"] is not False:
        _fail()
    from scripts.verify_opportunity_generator_lock import verify_generator_lock
    pilot = verify_generator_lock(ROOT)
    if (pilot["status"] != "source_identity_verified_not_scoring_authorized"
            or pilot["public_manifest_sha256"] != PUBLIC_MANIFEST
            or pilot["third_audit_commitments_sha256"] != THIRD_COMMITMENT
            or pilot["paired_trials_executed"] != 0):
        _fail()

    from scripts.verify_opportunity_choice_lock import (
        PUBLIC_PATH, LOCK_PATH, verify_custody, validate_payload,
    )
    raw_public = PUBLIC_PATH.read_bytes()
    raw_lock = LOCK_PATH.read_bytes()
    verified = verify_custody(raw_public, raw_lock)
    choices = validate_payload(raw_public)
    if (sha256(raw_public).hexdigest() != CHOICES_RAW
            or verified["decision_payload_sha256"] != CHOICES_CANONICAL
            or verified["paired_trials_executed"] != 0
            or verified["new_train_pilot_scoring_permitted"] is not False
            or verified["once_only_activation_approved"] is not False
            or verified["independent_private_raw_custody_verified"] is not False
            or choices["source_manifest_sha256"] != PUBLIC_MANIFEST):
        _fail()
    # Only AFTER all immutable source and official pretrial original checks.
    from packages.evaluation.opportunity_pilot import (
        generate_train_pilot, canonical_public_digest,
    )
    cases = generate_train_pilot()  # only fresh TRAIN64, never old DEV/FINAL
    if canonical_public_digest(cases) != PUBLIC_MANIFEST:
        _fail()
    return cases, choices


def build_private_original(cases: object, public_choices: dict) -> bytes:
    """Pure serialization logic; unit tests supply synthetic cases only."""
    if (type(cases) not in (list, tuple) or len(cases) != 64
            or type(public_choices) is not dict
            or type(public_choices.get("decisions")) is not list
            or len(public_choices["decisions"]) != 64
            or public_choices.get("paired_trials_executed") != 0
            or public_choices.get("dev_or_final_evaluated") is not False
            or public_choices.get("source_manifest_sha256") != PUBLIC_MANIFEST):
        _fail()
    rows = []
    audit_commitments = []
    seen = set()
    for case, entry in zip(cases, public_choices["decisions"], strict=True):
        task_id = case.task.task_id
        if (type(task_id) is not str
                or re.fullmatch(r"t-[0-9a-f]{64}", task_id) is None
                or task_id in seen or type(entry) is not dict
                or entry.get("task_id") != task_id):
            _fail()
        seen.add(task_id)
        options = entry.get("choices")
        if (type(options) is not dict or set(options) != {"B1", "B2", "B3"}
                or any(type(options[k]) is not dict
                       or options[k].get("action") not in ("ON", "OFF")
                       for k in options)):
            _fail()
        audit = {"input": case.private_audit.input, "output": case.private_audit.output}
        if not all(type(v) is str for v in audit.values()):
            _fail()
        seeds = case.seeds
        if (type(seeds) is not tuple or len(seeds) != 3
                or any(type(v) is not int for v in seeds)
                or type(case.family) is not str or type(case.source_record_id) is not str):
            _fail()
        rows.append({"task_id": task_id, "third_audit": audit,
                     "source_record_id": case.source_record_id,
                     "family": case.family, "seeds": list(seeds)})
        audit_commitments.append({"task_id": task_id, "third_audit_sha256": digest(audit)})
    if digest(audit_commitments) != THIRD_COMMITMENT:
        _fail()
    raw = canonical({
        "schema_version": SCHEMA,
        "method": METHOD,
        "scope": "fresh_train64_before_any_scored_trials",
        "public_manifest_sha256": PUBLIC_MANIFEST,
        "public_pretrial_original_raw_sha256": CHOICES_RAW,
        "public_pretrial_decision_sha256": CHOICES_CANONICAL,
        "third_audit_commitments_sha256": THIRD_COMMITMENT,
        "paired_trials_executed_at_capture": 0,
        "records": rows,
    }) + b"\n"
    if len(raw) > MAX_RAW_BYTES:
        _fail()
    return raw


def _private_destination(path: Path) -> os.stat_result:
    """Require existing owner-only real directory outside the public repo."""
    if not isinstance(path, Path) or not path.is_absolute():
        _fail()
    try:
        if path.exists() or path.is_symlink():
            _fail()  # no overwrite/rerun
        parent = path.parent
        if not parent.is_absolute() or parent.resolve(strict=True) != parent:
            _fail()  # no symlink parents
        if parent.is_relative_to(ROOT.resolve(strict=True)):
            _fail()
        info = parent.stat(follow_symlinks=False)
        if (not stat.S_ISDIR(info.st_mode)
                or stat.S_IMODE(info.st_mode) & 0o077
                or hasattr(os, "geteuid") and info.st_uid != os.geteuid()):
            _fail()
        return info
    except (OSError, RuntimeError):
        _fail()


def _write_exclusive(path: Path, raw: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as destination:
            destination.write(raw)
            destination.flush()
            os.fsync(destination.fileno())
    except OSError:
        _fail()


def _readback(path: Path, raw_hash: str, length: int) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        with os.fdopen(os.open(path, flags), "rb") as source:
            info = os.fstat(source.fileno())
            if (not stat.S_ISREG(info.st_mode) or
                    stat.S_IMODE(info.st_mode) & 0o077 or info.st_size != length):
                _fail()
            data = source.read(MAX_RAW_BYTES + 1)
            if len(data) != length or sha256(data).hexdigest() != raw_hash:
                _fail()
    except OSError:
        _fail()


def save_private_original(raw: bytes, primary: Path, secondary: Path) -> dict:
    """One-shot local save+readback; not externally attested durable custody."""
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_RAW_BYTES:
        _fail()
    a, b = _private_destination(primary), _private_destination(secondary)
    if ((a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
            or a.st_dev == b.st_dev):
        _fail()  # require distinct mounted filesystems; still not proof of offsite
    digest_bytes = sha256(raw).hexdigest()
    _write_exclusive(primary, raw)
    _readback(primary, digest_bytes, len(raw))
    # If the second copy fails, the first private original is deliberately
    # preserved for investigation. Do not regenerate/rerun silently.
    _write_exclusive(secondary, raw)
    _readback(secondary, digest_bytes, len(raw))
    return {
        "schema_version": "opportunity-private-capture-receipt-v1",
        "status": "two_distinct_mount_copies_raw_readback_pass_only",
        "raw_sha256": digest_bytes,
        "raw_size_bytes": len(raw),
        "private_record_count": 64,
        "different_filesystems_observed": True,
        "public_choice_raw_sha256": CHOICES_RAW,
        "audit_commitments_sha256": THIRD_COMMITMENT,
        "scored_trials": 0,
        "independent_private_raw_custody_verified": False,
        "acl_version_retention_independent_restore_verified": False,
        "scoring_authorized": False,
        "private_examples_disclosed": False,
    }


class _RedactedParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        _fail()  # do not echo private paths into CLI error output


def main(argv: list[str] | None = None) -> int:
    parser = _RedactedParser(description="Capture frozen fresh TRAIN64 audit originals; never score")
    parser.add_argument("--capture-before-scoring", action="store_true", required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--secondary", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        # Validate private destinations before source/replay work.
        a = _private_destination(args.primary)
        b = _private_destination(args.secondary)
        if a.st_dev == b.st_dev:
            _fail()
        cases, choices = _sealed_source_and_public_choices()
        raw = build_private_original(cases, choices)
        result = save_private_original(raw, args.primary, args.secondary)
    except (ValueError, OSError, RuntimeError, KeyError, TypeError):
        # Generic fixed message; do not leak private paths, examples, seeds.
        print("ERROR: private original capture rejected; no scoring", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
