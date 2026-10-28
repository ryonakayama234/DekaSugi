"""OPPORTUNITY-001: read-only, redacted comparison of two private raw copies.

This is NOT a custody authority or a scorer. It cannot verify the provenance,
access restrictions, encryption, storage version, retention, or restoration of
original evaluator-only third examples. Never run on public GitHub CI data.
Tests use synthetic bytes only. No project scorer/generator imports here.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 128 * 1024 * 1024
SCHEMA = "opportunity-private-copy-byte-check-v1"


def _local_file(path: Path, *, root: Path) -> os.stat_result:
    """Reject public Git, symlinks, aliases and non-files without logging paths."""
    if not isinstance(path, Path) or not path.is_absolute():
        raise ValueError("private copies require absolute paths")
    try:
        if path.is_symlink():
            raise ValueError("symlinked private archive forbidden")
        resolved = path.resolve(strict=True)
        if resolved.is_relative_to(root.resolve(strict=True)):
            raise ValueError("private archive must stay outside public repository")
        info = path.stat(follow_symlinks=False)
    except OSError:
        raise ValueError("private archive unavailable or inaccessible") from None
    if not stat.S_ISREG(info.st_mode) or info.st_size <= 0 or info.st_size > MAX_BYTES:
        raise ValueError("private archive nonregular, empty or oversized")
    return info


def _hash_limited(path: Path) -> tuple[int, str]:
    """Never deserialize, print, or persist raw evaluator-only bytes."""
    digest = sha256()
    size = 0
    try:
        with path.open("rb") as source:
            while True:
                block = source.read(1024 * 1024)
                if not block:
                    break
                size += len(block)
                if size > MAX_BYTES:
                    raise ValueError("private archive size limit exceeded")
                digest.update(block)
    except OSError:
        raise ValueError("private archive read failure") from None
    return size, digest.hexdigest()


def verify_private_copies(primary: Path, secondary: Path, expected_sha256: str,
                          *, root: Path = ROOT) -> dict[str, object]:
    """Compare original bytes only; success NEVER authorizes scored research."""
    if type(expected_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise ValueError("expected original SHA256 is invalid")
    first = _local_file(primary, root=root)
    second = _local_file(secondary, root=root)
    if (first.st_dev, first.st_ino) == (second.st_dev, second.st_ino):
        raise ValueError("private archive paths refer to the same file")
    if first.st_size != second.st_size:
        raise ValueError("private copies have different byte lengths")
    first_size, first_hash = _hash_limited(primary)
    second_size, second_hash = _hash_limited(secondary)
    if (first_size != first.st_size or second_size != second.st_size or
            first_size != second_size or first_hash != expected_sha256 or
            second_hash != expected_sha256):
        raise ValueError("private copy byte digests mismatch original")
    # Changing files during read is a hard-stop, not success.
    later_a = _local_file(primary, root=root)
    later_b = _local_file(secondary, root=root)
    if (later_a.st_size != first.st_size or later_a.st_mtime_ns != first.st_mtime_ns or
            later_a.st_ino != first.st_ino or later_a.st_dev != first.st_dev or
            later_b.st_size != second.st_size or later_b.st_mtime_ns != second.st_mtime_ns or
            later_b.st_ino != second.st_ino or later_b.st_dev != second.st_dev):
        raise ValueError("private copy changed while verifying")
    return {
        "schema_version": SCHEMA,
        "status": "two_local_copy_bytes_equal_expected_only",
        "raw_sha256": expected_sha256,
        "raw_size_bytes": first_size,
        "copy_count": 2,
        "different_filesystems_observed": first.st_dev != second.st_dev,
        "independent_private_raw_custody_verified": False,
        "acl_encryption_retention_restore_verified": False,
        "scoring_authorized": False,
        "private_bytes_disclosed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Redacted local raw-copy SHA256 check (NOT a custody gate)")
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--secondary", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        report = verify_private_copies(args.primary, args.secondary, args.expected_sha256)
    except (ValueError, OSError):
        print("ERROR: private-copy integrity check failed; no research authorization", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
