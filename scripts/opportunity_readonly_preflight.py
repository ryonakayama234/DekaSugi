"""OPPORTUNITY-001 source-first READ-ONLY owner preflight; NO NEW PILOT SCORE.

This preflight consumes only the previously captured private original, never
rewrites it or creates a run ledger; it does not invoke audited_trial,
bounded_synthesize on any *new* TRAIN64 case, or the activation wrapper.
Historical pinned TRAIN/DREAM frozen-skill reconstruction is required for the
same provenance checks as the actual runner; historical DEV/FINAL forbidden.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

FROZEN_PUBLIC_SHA = "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"
FROZEN_SKILL_ID = "skill_8fe1361cb5014f85"


def _stop() -> None:
    raise ValueError("pretrial integrity/one-shot-readiness check failed; STOP; no score")


def _reject_existing_ledger(root_fd: int, ledger_name: str) -> None:
    """No scoring is requested: reject ANY prior attempt without altering it."""
    try:
        os.stat(ledger_name, dir_fd=root_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError:
        _stop()
    _stop()


def verify_readonly(private_dir: Path, original_sha256: str,
                    approved_main_sha: str) -> dict:
    """Run every locked provenance/readback check WITHOUT reserving or scoring.

    No private data may be printed or committed. This cannot prove independent
    cloud account-loss durability or authorize an irreversible scored run.
    """
    # Do not import any project package or original loader before source gate.
    from scripts import opportunity_real_pair_engine as engine
    from scripts import opportunity_one_shot_runner as runner
    if engine.SCORING_ACTIVATED is not False or runner.ONE_SHOT_ACTIVATED is not False:
        _stop()
    runner._require_checkout(approved_main_sha)  # exact canonical clean origin/main; 3.12.15
    public = engine.source_first_preflight()  # old14/new9 + public original choices
    from scripts.verify_opportunity_choice_lock import (
        PUBLIC_PATH, LOCK_PATH, verify_custody)
    verify_custody(PUBLIC_PATH.read_bytes(), LOCK_PATH.read_bytes())

    with runner._private_root(private_dir) as root_fd:
        _reject_existing_ledger(root_fd, runner.LEDGER_NAME)
        original = runner._read_original(root_fd, original_sha256)
        originals = engine.validate_private_archive(
            original, original_sha256, public)
        # All imports below occur after byte locks are verified.
        from packages.evaluation.opportunity_pilot import (
            generate_train_pilot, canonical_public_digest)
        from scripts.prepare_opportunity_decisions import (
            _rebuild_historic_train_dream_only)

        cases = generate_train_pilot()  # trusted in-memory replay only, NO scored trial
        if (canonical_public_digest(cases) != FROZEN_PUBLIC_SHA
                or public["source_manifest_sha256"] != FROZEN_PUBLIC_SHA):
            _stop()
        runner._original_binding(cases, originals, public["decisions"])
        frozen = json.loads((runner.ROOT / "experiments/EXP-0003A/freeze-v1.json")
                            .read_bytes())
        # Only existing historic TRAIN/DREAM policy reconstruction; NEVER DEV/FINAL.
        skill, _snapshots, policy_hashes = _rebuild_historic_train_dream_only(frozen)
        if (skill.skill_id != FROZEN_SKILL_ID
                or skill.body_hash != engine.LOCKED_SKILL
                or policy_hashes != public["policy_snapshot_sha256"]):
            _stop()
        # Defensive readback after the legacy policy replay: original did not change.
        runner._read_original(root_fd, original_sha256)

    return {
        "schema_version": "opportunity-live-readonly-preflight-v1",
        "status": "all_frozen_pretrial_and_private_original_checks_pass_no_score",
        "approved_clean_main_commit": approved_main_sha,
        "original_sha256": original_sha256,
        "original_record_count": len(originals),
        "pretrial_choices": 192,
        "frozen_skill_body_sha256": engine.LOCKED_SKILL,
        "audit_commitments_sha256": engine.LOCKED_THIRD_COMMITMENTS,
        "original_readback_twice": True,
        "irreversible_run_ledger_created": False,
        "new_train64_scored_trials": 0,
        "old_dev_or_final_evaluated": False,
        "scoring_authorized": False,
        "private_original_disclosed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(
        "Read-only, no new scored trial; trusted owner WSL2 ONLY"))
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--original-sha256", required=True)
    parser.add_argument("--approved-main-commit", required=True)
    args = parser.parse_args(argv)
    try:
        report = verify_readonly(args.private_dir, args.original_sha256,
                                 args.approved_main_commit)
    except BaseException:
        # No private traceback, audit text, family/seed, local path or secret.
        print("STOP: read-only preflight failed; no new TRAIN64 scored",
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
