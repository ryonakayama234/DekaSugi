"""OPPORTUNITY-001-PILOT-V1 explicitly armed MAIN-only private scorer.

Do NOT invoke from GitHub Actions, CI or an unreviewed branch. Only the owner
holding the already-captured 64-row private original may run this after this
exact-head code and external custody have been independently accepted.
Original third audits and scorer tuples are NEVER uploaded to public GitHub.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys


def _stop() -> None:
    raise ValueError("one-shot activation not authorized, STOP; NEVER retry after STARTED")


@contextmanager
def _scoped_engine_activation(runner, engine):
    """The two global engine flags remain FALSE except within this run.

    This is an accidental-use guard, NOT a cryptographic capability. The
    external custodian must preserve the original and irreversible markers.
    """
    if runner.ONE_SHOT_ACTIVATED is not False or engine.SCORING_ACTIVATED is not False:
        _stop()
    runner.ONE_SHOT_ACTIVATED = True
    engine.SCORING_ACTIVATED = True
    try:
        yield
    finally:
        engine.SCORING_ACTIVATED = False
        runner.ONE_SHOT_ACTIVATED = False


def start_owner_private_once(private_dir: Path, original_sha256: str,
                             approved_main_commit: str,
                             *, custody_confirmed: bool,
                             never_retry_confirmed: bool) -> dict:
    """A user-controlled one-shot entrypoint, not an Actions or CI trigger."""
    if (custody_confirmed is not True or never_retry_confirmed is not True
            or not isinstance(private_dir, Path)):
        _stop()
    from scripts import opportunity_one_shot_runner as runner
    from scripts import opportunity_real_pair_engine as engine
    # Verify exact clean, canonical origin/main SHA BEFORE toggling scorer flags.
    runner._require_checkout(approved_main_commit)
    with _scoped_engine_activation(runner, engine):
        # This checks old14/new9 sources, fixed 192 choices, private ORIGINAL,
        # 64 third commitments, frozen real TRAIN/DREAM skill and registers
        # STARTED before it calls the first real OFF arm. No automatic retry.
        return runner.run_private_once(private_dir, original_sha256,
                                       approved_main_commit)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(
        "TRUE one-shot OFF/ON pilot: once only on approved private WSL2 main;"
        " no public GitHub/CI scorer"))
    parser.add_argument("--execute-fresh-train64-once", required=True,
                        action="store_true")
    parser.add_argument("--confirm-offsite-custody", required=True,
                        action="store_true")
    parser.add_argument("--confirm-never-retry", required=True,
                        action="store_true")
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--original-sha256", required=True)
    parser.add_argument("--approved-main-commit", required=True)
    args = parser.parse_args(argv)
    try:
        result = start_owner_private_once(
            args.private_dir, args.original_sha256, args.approved_main_commit,
            custody_confirmed=args.confirm_offsite_custody,
            never_retry_confirmed=args.confirm_never_retry)
    except BaseException:
        # Do not echo private original paths, exceptions, audit examples or
        # raw scorer tuples. The irreversible ledger already records STOP.
        print("STOP: activation was rejected or scoring aborted; "
              "do not rerun or regenerate the original", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
