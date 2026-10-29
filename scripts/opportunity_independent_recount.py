"""OPPORTUNITY-001: independent READ-ONLY private evidence recount.

Never invokes any new TRAIN64 scorer, old DEV/FINAL evaluation or activation.
Reads original per-arm audited tuples and checks each saved redacted result
against the frozen normalizer. Only aggregate counts leave the owner host.
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

CLASSES = ("both_correct_on_cheaper", "both_correct_off_cheaper",
           "both_correct_tie", "on_only_correct", "off_only_correct",
           "neither_correct")
ARMS = ("OFF", "ON")
POLICIES = ("B1", "B2", "B3")
MAX_JSON = 256_000


def _stop() -> None:
    raise ValueError("independent private evidence recount failed; no scoring")


def _strict_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            _stop()
        out[key] = value
    return out


def _constant(_: str):
    _stop()


def _exact(obj, keys):
    if type(obj) is not dict or set(obj) != set(keys):
        _stop()
    return obj


def _load_privately(fd: int, name: str) -> dict:
    """Read a single 0600, owner-controlled regular file, no symlink/hardlink."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+(?:[.][A-Za-z0-9_-]+)*", name):
        _stop()
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        with os.fdopen(os.open(name, flags, dir_fd=fd), "rb") as stream:
            info = os.fstat(stream.fileno())
            if (not stat.S_ISREG(info.st_mode) or
                    info.st_uid != os.geteuid() or info.st_nlink != 1 or
                    info.st_mode & 0o077 or not 0 < info.st_size <= MAX_JSON):
                _stop()
            data = stream.read(MAX_JSON + 1)
        if len(data) != info.st_size:
            _stop()
        result = json.loads(data.decode("utf-8"), object_pairs_hook=_strict_pairs,
                            parse_constant=_constant)
    except (OSError, ValueError, UnicodeError, TypeError):
        _stop()
    if type(result) is not dict:
        _stop()
    return result


def _read_optional(fd: int, name: str):
    try:
        os.stat(name, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError:
        _stop()
    return _load_privately(fd, name)


def _bucket():
    return {
        "paired_valid": 0,
        "classifications": {k: 0 for k in CLASSES},
        "off_audited_correct": 0,
        "on_audited_correct": 0,
        "best_of_two_success": 0,
        "off_primitive_calls_sum": 0,
        "on_primitive_calls_sum": 0,
        "off_tested_candidates_sum": 0,
        "on_tested_candidates_sum": 0,
        "off_search_cpu_ms_sum": 0.0,
        "on_search_cpu_ms_sum": 0.0,
        "off_search_wall_ms_sum": 0.0,
        "on_search_wall_ms_sum": 0.0,
        "off_audit_cpu_ms_sum": 0.0,
        "on_audit_cpu_ms_sum": 0.0,
        "off_audit_wall_ms_sum": 0.0,
        "on_audit_wall_ms_sum": 0.0,
        "choice_disagreement_tasks": 0,
        "choice_sensitivity_denominator": 0,
        "policy_inference_cost": "not_metered_by_original_pilot",
        "policies": {
            p: {"decision_eligible": 0, "decision_errors": 0,
                "missed_success": 0, "lost_success": 0,
                "regret_eligible": 0, "sum_excess_calls": 0}
            for p in POLICIES
        },
    }


def _count(b, pair):
    classification = pair["classification"]
    if classification not in CLASSES:
        _stop()
    trials = _exact(pair["trials"], ARMS)
    if pair.get("both_arms_audited") is not True:
        _stop()
    off, on = trials["OFF"], trials["ON"]
    b["paired_valid"] += 1
    b["classifications"][classification] += 1
    b["off_audited_correct"] += int(off["audited_correct"])
    b["on_audited_correct"] += int(on["audited_correct"])
    b["best_of_two_success"] += int(pair["best_of_two_correct"])
    b["off_primitive_calls_sum"] += off["primitive_calls"]
    b["on_primitive_calls_sum"] += on["primitive_calls"]
    b["off_tested_candidates_sum"] += off["tested_candidates"]
    b["on_tested_candidates_sum"] += on["tested_candidates"]
    for arm, record in (("off",off),("on",on)):
        for meter in ("search_cpu_ms", "search_wall_ms",
                      "audit_cpu_ms", "audit_wall_ms"):
            b[f"{arm}_{meter}_sum"] += record[meter]
    b["choice_sensitivity_denominator"] += 1
    b["choice_disagreement_tasks"] += int(len({
        pair["policies"][name]["action"] for name in POLICIES
    }) > 1)
    for name in POLICIES:
        p = _exact(pair["policies"][name],
                   {"action", "decision_error", "missed_success",
                    "lost_success", "excess_calls"})
        dest = b["policies"][name]
        if p["decision_error"] is not None:
            dest["decision_eligible"] += 1
            dest["decision_errors"] += int(p["decision_error"])
        dest["missed_success"] += int(p["missed_success"])
        dest["lost_success"] += int(p["lost_success"])
        if p["excess_calls"] is not None:
            dest["regret_eligible"] += 1
            dest["sum_excess_calls"] += p["excess_calls"]


def recount_complete(read_file, filenames, public_rows, originals, cases,
                     approved_score_commit: str, original_sha256: str):
    """Pure recount from caller-injected files. CI uses fake private tuples only."""
    started = _exact(read_file("STARTED.json"),
                     {"schema_version", "source_commit", "original_sha256",
                      "planned_pairs", "no_retry_even_on_failure"})
    if (started["schema_version"] != "opportunity-once-only-start-v1"
            or started["source_commit"] != approved_score_commit
            or started["original_sha256"] != original_sha256
            or type(started["planned_pairs"]) is not int
            or started["planned_pairs"] != 64
            or started["no_retry_even_on_failure"] is not True):
        _stop()
    complete = _exact(read_file("COMPLETED.json"),
                      {"schema_version", "paired_count", "status",
                       "no_public_raw_data"})
    if (complete["schema_version"] != "opportunity-once-only-completion-v1"
            or type(complete["paired_count"]) is not int
            or complete["paired_count"] != 64
            or complete["status"] != "complete_redacted_private_evidence_only"
            or complete["no_public_raw_data"] is not True):
        _stop()
    if len(public_rows) != 64 or len(originals) != 64 or len(cases) != 64:
        _stop()
    expected = {"STARTED.json", "COMPLETED.json"}
    overall = _bucket()
    by_family = {}
    from packages.evaluation.opportunity_actual import public_redacted_pair
    from scripts.opportunity_real_pair_engine import _canonical
    from scripts.opportunity_one_shot_runner import _redacted_only
    for i, (decision, original, case) in enumerate(
            zip(public_rows, originals, cases, strict=True)):
        tid = decision["task_id"]
        if (tid != case.task.task_id or original["task_id"] != tid):
            _stop()
        actions = {arm: decision["choices"][arm]["action"] for arm in POLICIES}
        raw_pair = {}
        for arm in ARMS:
            marker_name = f"ARM_STARTED-{i:03d}-{arm}.json"
            trial_name = f"trial-{i:03d}-{arm}.json"
            expected.update((marker_name, trial_name))
            marker = _exact(read_file(marker_name),
                            {"schema_version", "task_id", "arm", "index"})
            if (marker["schema_version"] != "opportunity-once-only-arm-start-v1"
                    or marker["task_id"] != tid or marker["arm"] != arm
                    or type(marker["index"]) is not int or marker["index"] != i):
                _stop()
            trial = _exact(read_file(trial_name),
                           {"schema_version", "task_id", "arm",
                            "canonical_original_tuple"})
            if (trial["schema_version"] != "opportunity-private-raw-trial-v1"
                    or trial["task_id"] != tid or trial["arm"] != arm
                    or type(trial["canonical_original_tuple"]) is not list
                    or len(trial["canonical_original_tuple"]) != 9):
                _stop()
            raw_pair[arm] = tuple(trial["canonical_original_tuple"])
        pair_name = f"pair-{i:03d}.json"
        expected.add(pair_name)
        private_digest = sha256(_canonical(original["third_audit"])).hexdigest()
        recreated = public_redacted_pair(tid, raw_pair["OFF"], raw_pair["ON"],
                                         actions, private_digest)
        saved = read_file(pair_name)
        if _redacted_only(recreated) != _redacted_only(saved):
            _stop()
        family = case.family
        if type(family) is not str or not family:
            _stop()
        _count(overall, recreated)
        _count(by_family.setdefault(family, _bucket()), recreated)
    if set(filenames) != expected or len(filenames) != len(expected):
        _stop()
    if overall["paired_valid"] != 64 or sum(
            overall["classifications"].values()) != 64:
        _stop()
    return {"overall": overall, "by_family": by_family}


def inspect_private_evidence(private_dir: Path, original_sha256: str,
                             approved_score_commit: str,
                             reviewed_recount_main: str):
    """Source-first no-score verification of preexisting private ledger only."""
    from scripts import opportunity_one_shot_runner as runner
    from scripts import opportunity_real_pair_engine as engine
    if runner.ONE_SHOT_ACTIVATED is not False or engine.SCORING_ACTIVATED is not False:
        _stop()
    runner._require_checkout(reviewed_recount_main)
    public = engine.source_first_preflight()
    from scripts.verify_opportunity_choice_lock import (
        PUBLIC_PATH, LOCK_PATH, verify_custody)
    verify_custody(PUBLIC_PATH.read_bytes(), LOCK_PATH.read_bytes())
    with runner._private_root(private_dir) as root_fd:
        original_raw = runner._read_original(root_fd, original_sha256)
        originals = engine.validate_private_archive(
            original_raw, original_sha256, public)
        from packages.evaluation.opportunity_pilot import (
            generate_train_pilot, canonical_public_digest)
        cases = generate_train_pilot()  # reference in memory; no actual scored trial
        if (canonical_public_digest(cases)
                != "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"):
            _stop()
        runner._original_binding(cases, originals, public["decisions"])
        fd = None
        try:
            fd = os.open(runner.LEDGER_NAME,
                         os.O_DIRECTORY | os.O_RDONLY | os.O_CLOEXEC |
                         os.O_NOFOLLOW, dir_fd=root_fd)
            info = os.fstat(fd)
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or (
                    info.st_mode & 0o777) != 0o700:
                _stop()
            names = os.listdir(fd)
            started = _load_privately(fd, "STARTED.json")
            if (started.get("source_commit") != approved_score_commit
                    or started.get("original_sha256") != original_sha256):
                _stop()
            completed = _read_optional(fd, "COMPLETED.json")
            stopped = _read_optional(fd, "STOPPED.json")
            if completed is None or stopped is not None:
                return {
                    "schema_version": "opportunity-independent-recount-v1",
                    "status": "INCOMPLETE_NO_RETRY_NO_SCIENTIFIC_RESULT",
                    "original_sha256": original_sha256,
                    "approved_score_commit": approved_score_commit,
                    "evidence_file_count": len(names),
                    "scored_again": False,
                    "retry_authorized": False,
                    "private_data_disclosed": False,
                }
            data = recount_complete(
                lambda name: _load_privately(fd, name),
                names, public["decisions"], originals, cases,
                approved_score_commit, original_sha256)
            # Original byte hash must still match after all evidence reads.
            runner._read_original(root_fd, original_sha256)
        finally:
            if fd is not None:
                os.close(fd)
    return {
        "schema_version": "opportunity-independent-recount-v1",
        "status": "COMPLETE_64_PAIRED_RECOUNT_VERIFIED",
        "original_sha256": original_sha256,
        "approved_score_commit": approved_score_commit,
        "source_manifest_sha256": public["source_manifest_sha256"],
        "paired_count": 64,
        **data,
        "scored_again": False,
        "retry_authorized": False,
        "private_data_disclosed": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=(
        "Read-only independent original OFF/ON record recount; NEVER score"))
    p.add_argument("--private-dir", type=Path, required=True)
    p.add_argument("--original-sha256", required=True)
    p.add_argument("--approved-score-commit", required=True)
    p.add_argument("--reviewed-recount-main", required=True)
    ns = p.parse_args(argv)
    try:
        report = inspect_private_evidence(
            ns.private_dir, ns.original_sha256, ns.approved_score_commit,
            ns.reviewed_recount_main)
    except BaseException:
        print("STOP: read-only evidence recount failed; DO NOT RETRY SCORE",
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
