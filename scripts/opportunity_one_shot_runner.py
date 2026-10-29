"""OPPORTUNITY-001 one-shot local private-host runner: NOT ACTIVATED.

Scientific METHOD: immutable PILOT-V1. This module is an inert implementation
until a SEPARATE, independently reviewed main-only activation changes the
two hard-off gates and approves the off-GitHub custody/lifecycle receipt.
CI may ONLY call synthetic helpers: never source/generator/real audited_trial.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LEDGER_NAME = "opportunity-001-scoring-once-only"
MAX_PRIVATE = 256_000
EXPECTED_SOURCE_COMMIT = "940a3acad37998e2e117d0798cb37359113f3783"
# Real activation requires a distinct reviewed change; leave False until then.
ONE_SHOT_ACTIVATED = False


def _stop() -> None:
    raise ValueError("one-shot private evaluation STOP; no automatic retry")


def _json(data: object) -> bytes:
    return (json.dumps(data, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


@contextmanager
def _private_root(path: Path):
    """Pin an owner-only 0700 directory through O_NOFOLLOW ancestor traversal."""
    if not isinstance(path, Path) or not path.is_absolute():
        _stop()
    fd = None
    try:
        if path.is_relative_to(ROOT):
            _stop()
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        fd = os.open("/", flags)
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
            info = os.fstat(fd)
            if (not stat.S_ISDIR(info.st_mode) or
                    (info.st_mode & 0o022) and not
                    (info.st_mode & stat.S_ISVTX and info.st_uid == 0)):
                _stop()
        info = os.fstat(fd)
        if ((info.st_mode & 0o777) != 0o700 or
                info.st_uid != os.geteuid()):
            _stop()
        yield fd
    except OSError:
        _stop()
    finally:
        if fd is not None:
            os.close(fd)


def _read_original(fd: int, expected_sha: str) -> bytes:
    """Read ONLY the original already captured; never regenerate or rewrite it."""
    if (type(expected_sha) is not str or
            re.fullmatch("[0-9a-f]{64}", expected_sha) is None):
        _stop()
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
    try:
        with os.fdopen(os.open("original.bin", flags, dir_fd=fd), "rb") as stream:
            info = os.fstat(stream.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                    or info.st_mode & 0o077 or not 0 < info.st_size <= MAX_PRIVATE
                    or info.st_nlink != 1):
                _stop()
            raw = stream.read(MAX_PRIVATE + 1)
        if len(raw) != info.st_size or sha256(raw).hexdigest() != expected_sha:
            _stop()
        return raw
    except OSError:
        _stop()


def _write_exclusive(parent_fd: int, filename: str, payload: dict) -> None:
    if (not re.fullmatch(r"[A-Za-z0-9_-]+(?:[.][A-Za-z0-9_-]+)*", filename)
            or len(filename) > 70):
        _stop()
    data = _json(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    with os.fdopen(os.open(filename, flags, 0o600, dir_fd=parent_fd), "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.fsync(parent_fd)


@contextmanager
def _reserve_once(root_fd: int, source_commit: str, original_sha: str):
    """No second try, even if first run aborted after reservation or crashed.

    A deleted external ledger cannot be detected here: independent custodian
    must preserve and attest this run identity outside this machine.
    """
    fd = None
    os.mkdir(LEDGER_NAME, mode=0o700, dir_fd=root_fd)
    os.fsync(root_fd)
    try:
        fd = os.open(LEDGER_NAME, os.O_RDONLY | os.O_DIRECTORY |
                     os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root_fd)
        _write_exclusive(fd, "STARTED.json", {
            "schema_version": "opportunity-once-only-start-v1",
            "source_commit": source_commit,
            "original_sha256": original_sha,
            "planned_pairs": 64,
            "no_retry_even_on_failure": True,
        })
        yield fd
    finally:
        if fd is not None:
            os.close(fd)


def _guard_activated(engine) -> None:
    if ONE_SHOT_ACTIVATED is not True or engine.SCORING_ACTIVATED is not True:
        _stop()


def _original_binding(cases, original_rows, decisions) -> None:
    """All 64 exact source IDs/seeds/third examples must agree before trial 1."""
    if (len(cases) != 64 or len(original_rows) != 64 or
            len(decisions) != 64):
        _stop()
    for case, row, decision in zip(cases, original_rows, decisions, strict=True):
        third = row["third_audit"]
        if (case.task.task_id != row["task_id"] or
                case.task.task_id != decision["task_id"] or
                row["source_record_id"] != case.source_record_id or
                row["family"] != case.family or
                row["seeds"] != list(case.seeds) or
                third != {"input": case.private_audit.input,
                          "output": case.private_audit.output}):
            _stop()


def _redacted_only(pair: dict) -> dict:
    """Defence in depth: never serialize third audit, source/family/seeds."""
    if type(pair) is not dict or set(pair) != {
            "schema_version", "task_id", "audit_commitment_sha256",
            "trials", "classification", "unique_better_action",
            "policies", "both_arms_audited", "best_of_two_correct"}:
        _stop()
    forbidden = {"third_audit", "source_record_id", "family", "seeds",
                 "input", "output", "private_audit"}
    def inspect(node):
        if type(node) is dict:
            if any(type(k) is not str or k in forbidden for k in node):
                _stop()
            for child in node.values():
                inspect(child)
        elif type(node) in (list, tuple):
            for child in node:
                inspect(child)
    inspect(pair)
    return pair


def _require_checkout(expected_sha: str) -> None:
    if type(expected_sha) is not str or not re.fullmatch("[0-9a-f]{40}", expected_sha):
        _stop()
    if sys.version_info[:3] != (3, 12, 15):
        _stop()
    try:
        actual = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, timeout=5).decode().strip()
        modified = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, timeout=5)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        _stop()
    if actual != expected_sha or modified:
        _stop()


def run_private_once(private_dir: Path, expected_raw_sha256: str,
                     approved_commit_sha: str) -> dict:
    """Real source runner, unavailable until TWO separately reviewed flips.

    This must be executed on the owner's private Linux machine, NEVER in CI,
    GitHub Actions, or in this chat. Archive and scored rows stay local.
    """
    # Stop before reading originals, importing generators or attempting scoring.
    from scripts import opportunity_real_pair_engine as engine
    _guard_activated(engine)
    _require_checkout(approved_commit_sha)
    # Both source-identity verifiers are stdlib-only, before project imports.
    public = engine.source_first_preflight()
    from scripts.verify_opportunity_choice_lock import (
        PUBLIC_PATH, LOCK_PATH, verify_custody)
    verify_custody(PUBLIC_PATH.read_bytes(), LOCK_PATH.read_bytes())

    with _private_root(private_dir) as root_fd:
        original = _read_original(root_fd, expected_raw_sha256)
        original_rows = engine.validate_private_archive(
            original, expected_raw_sha256, public)
        # These imports/operations occur only AFTER source-first byte verification.
        from packages.evaluation.opportunity_pilot import (
            generate_train_pilot, canonical_public_digest)
        from packages.protocol import Example
        from scripts.prepare_opportunity_decisions import (
            _rebuild_historic_train_dream_only)
        cases = generate_train_pilot()
        if canonical_public_digest(cases) != (
                "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"):
            _stop()
        _original_binding(cases, original_rows, public["decisions"])
        frozen = json.loads((ROOT / "experiments/EXP-0003A/freeze-v1.json")
                            .read_bytes())
        skill, _snapshots, policy_hashes = _rebuild_historic_train_dream_only(frozen)
        if (skill.body_hash != engine.LOCKED_SKILL or
                skill.skill_id != "skill_8fe1361cb5014f85" or
                policy_hashes != public["policy_snapshot_sha256"]):
            _stop()
        # Reservation occurs strictly BEFORE the FIRST real OFF/ON trial.
        # If anything fails after this, STARTED remains and rerun is forbidden.
        with _reserve_once(root_fd, approved_commit_sha, expected_raw_sha256) as ledger_fd:
            completed = 0
            try:
                for i, (case, row, decision) in enumerate(
                        zip(cases, original_rows, public["decisions"], strict=True)):
                    actions = {arm: decision["choices"][arm]["action"]
                               for arm in ("B1", "B2", "B3")}
                    audited = Example(**row["third_audit"])
                    third_sha = sha256(_json(row["third_audit"]).strip()).hexdigest()
                    pair = engine._unactivated_real_pair(
                        case.task, audited, skill, actions, third_sha)
                    _write_exclusive(ledger_fd, f"pair-{i:03d}.json",
                                     _redacted_only(pair))
                    completed += 1
                _write_exclusive(ledger_fd, "COMPLETED.json", {
                    "schema_version": "opportunity-once-only-completion-v1",
                    "paired_count": completed,
                    "status": "complete_redacted_private_evidence_only",
                    "no_public_raw_data": True,
                })
            except BaseException:
                # Must NEVER include traceback, private audit or exception text.
                try:
                    _write_exclusive(ledger_fd, "STOPPED.json", {
                        "schema_version": "opportunity-once-only-stop-v1",
                        "completed_pairs": completed, "rerun_allowed": False,
                    })
                finally:
                    raise
            return {"status": "completed_private_local", "paired_count": completed,
                    "scoring_authorized_again": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inert one-shot TRAIN-only runner; no scoring until separate approval")
    parser.add_argument("--execute-one-shot", action="store_true", required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--expected-raw-sha256", required=True)
    parser.add_argument("--approved-commit", required=True)
    args = parser.parse_args(argv)
    try:
        result = run_private_once(args.private_dir, args.expected_raw_sha256,
                                  args.approved_commit)
    except BaseException:
        print("STOP: one-shot not authorized or run aborted; DO NOT RETRY",
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
