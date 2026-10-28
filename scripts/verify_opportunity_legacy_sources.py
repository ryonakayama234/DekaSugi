"""Strict stdlib-only historic EXP-0003A 14-source verification.

This is NOT packages.exp0003a.freeze.verify_frozen(): that legacy function
regenerates DEV/FINAL hashes after byte checks. This function NEVER imports
packages/ or generates any partition.
"""
from __future__ import annotations

from hashlib import sha1, sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FROZEN_FILE = "experiments/EXP-0003A/freeze-v1.json"
PINNED_FREEZE_PAYLOAD_SHA256 = "1e0f6daf1cb80262c187c60a3e0a4d2e76dafea911f0633feed3c40f93db8f44"
PINNED_RAW_FREEZE_GIT_BLOB = "9b18d9bd4ab44094fae94d9cdcc3f23b4b8ee603"
PINNED_SOURCE_MANIFEST_SHA256 = "b007533bd1f06f37b740d8f05df463915a8f03cef61cff32fc4b7c92bce91394"
SOURCE_FILES = frozenset((
    "experiments/EXP-0003A/plan.md",
    "packages/evaluation/__init__.py",
    "packages/exp0003a/__init__.py",
    "packages/exp0003a/freeze.py",
    "packages/exp0003a/freeze_cli.py",
    "packages/exp0003a/pr3.py",
    "packages/exp0003a/pr3_cli.py",
    "packages/kernel/__init__.py",
    "packages/learning/__init__.py",
    "packages/library/__init__.py",
    "packages/protocol/__init__.py",
    "packages/runtime/__init__.py",
    "packages/synthesis/__init__.py",
    "packages/verification/__init__.py",
))


def _hash(x: object) -> str:
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _blob(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_legacy_source_bytes(root: Path = ROOT) -> dict[str, object]:
    """Validate 14 frozen files before ANY project package is imported."""
    freeze_path = root / FROZEN_FILE
    if not freeze_path.is_file() or freeze_path.is_symlink():
        raise ValueError("Missing or linked historic freeze")
    raw_bytes = freeze_path.read_bytes()
    if _blob(raw_bytes) != PINNED_RAW_FREEZE_GIT_BLOB:
        raise ValueError("Historic freeze raw byte drift")
    record = json.loads(raw_bytes)
    if not isinstance(record, dict):
        raise ValueError("Malformed historic freeze")
    payload = {k: v for k, v in record.items() if k != "freeze_payload_sha256"}
    if (record.get("freeze_payload_sha256") != PINNED_FREEZE_PAYLOAD_SHA256
            or _hash(payload) != PINNED_FREEZE_PAYLOAD_SHA256
            or record.get("holdout_scoring_permitted") is not False
            or record.get("registry_promotion_permitted") is not False):
        raise ValueError("Historic freeze integrity/permission drift")
    sources = record.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("Historic source manifest missing")
    rows = sources.get("files")
    if (not isinstance(rows, dict) or set(rows) != SOURCE_FILES
            or sources.get("git_blob_manifest_sha256") != PINNED_SOURCE_MANIFEST_SHA256
            or _hash({path: rows[path].get("git_blob_sha1") for path in sorted(rows)})
            != PINNED_SOURCE_MANIFEST_SHA256):
        raise ValueError("Historic source manifest integrity mismatch")
    for path in sorted(SOURCE_FILES):
        entry = rows[path]
        if not isinstance(entry, dict) or set(entry) != {"git_blob_sha1", "raw_sha256"}:
            raise ValueError("Historic source entry shape drift")
        if (not isinstance(entry["git_blob_sha1"], str)
                or not re.fullmatch("[0-9a-f]{40}", entry["git_blob_sha1"])
                or not isinstance(entry["raw_sha256"], str)
                or not re.fullmatch("[0-9a-f]{64}", entry["raw_sha256"])):
            raise ValueError("Historic source digest format drift")
        file_path = root / path
        if not file_path.is_file() or file_path.is_symlink():
            raise ValueError(f"Historic source missing/symlinked: {path}")
        data = file_path.read_bytes()
        if (_blob(data) != entry["git_blob_sha1"]
                or sha256(data).hexdigest() != entry["raw_sha256"]):
            raise ValueError(f"Historic source byte drift: {path}")
    return {
        "schema_version": "opportunity-legacy-source-gate-v1",
        "freeze_payload_sha256": PINNED_FREEZE_PAYLOAD_SHA256,
        "verified_source_count": len(SOURCE_FILES),
        "status": "stdlib_source_only_verified_no_partitions_generated",
        "dev_or_final_generated": False,
    }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(verify_legacy_source_bytes(), sort_keys=True, allow_nan=False))
