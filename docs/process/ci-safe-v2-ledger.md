# CI-SAFE-V2 — append-only safety migration ledger

id: CI-SAFE-V2-LEDGER
status: staged_source_only; not_merged; actions_disablement_not_verified
updated: 2026-10-29
tags: ci, custody, evidence, workflow, source-lock

## PR preparation checkpoint
- Scope: an **additional** independent workflow, exact static source/command allowlist, synthetic-only unittest selection, negative injection controls, and architecture/runbook updates. Historic workflow and all frozen original generator locks untouched.
- GitHub initial base: `main` at `f2c1f2aa6885223badc39434577f6a39a12b943b`. No true EXP-0002B DEV evaluation, OPPORTUNITY-001 original TRAIN64 rerun, or historical EXP-0003A DEV64/FINAL128 generation/scoring authorized.
- Exact PR-head CI observation: **pending until performed**.
- Independent exact-head security review: **pending**.
- Manual Actions old-workflow disablement: **not performed / not verified**. Neither source-only checks nor the v2 workflow asserts repository-side `disabled_manually`. Owner must provide independently checked control-plane evidence before any main merge.
- Main merges of PR #87, #89 and successor: **blocked** until owner verification and independent acceptance. A future recorded CI PASS would not change this by itself.

## Future immutable receipts (append, never retroactive overwrite)
Each checkpoint: observed UTC/JST time, exact Git SHA/PR, GitHub job/run ID and pass/fail, independent review identity/verdict, specific workflow ID/path/state `disabled_manually` evidence with no credentials, exact reviewed merge SHA and absence of old DEV event, explicit nonclaims. Record failures/incomplete states rather than converting absent status to green.

[Spec](../specs/CI-SAFE-V2.md) / [Architecture](../architecture/decisions/ADR-0004-ci-safe-successor.md) / [Issue #88](https://github.com/ryonakayama234/DekaSugi/issues/88).

## 2026-10-29 — observed CI regression and corrective calibration (PR #90, PR only)
- Initial exact PR head `dbc745dff12540e6ce19cce4b5a49f9f12739613`: new workflow [run 40870498690](https://github.com/ryonakayama234/DekaSugi/actions/runs/40870498690) **FAILED** before unit tests: direct `python scripts/check_research_ci_v2.py` launched with `scripts/` on Python import path, causing `ModuleNotFoundError: No module named 'scripts'`. No source-drift or scored experiment caused this. The original legacy PR workflow on the same head [run 40870498815](https://github.com/ryonakayama234/DekaSugi/actions/runs/40870498815) **PASSED**; its main-push-only DEV branch was not triggered.
- Intermediate head `62fae6463b4019b56c3f77cc828bb79c666ded48`: corrected first static verifier import path, but the second synthetic test runner still required a root-path fix. The intermediate new workflow [run 40870653392](https://github.com/ryonakayama234/DekaSugi/actions/runs/40870653392) **FAILED**, retained as separate observable engineering feedback.
- Fixed head `da431cd37ebbe501f562000c6fbdaadced878ff5`: new successor [run 40870665316](https://github.com/ryonakayama234/DekaSugi/actions/runs/40870665316) **PASSED**. Source/command byte gate PASS (original nine-source PILOT-V1 and old fourteen-source EXP-0003A), documentation validation PASS, exact allowlisted synthetic `unittest` **50 tests / OK**. No historical DEV/FINAL scorer or trial task was executed by the successor; it has no score/upload step.
- The inherited legacy workflow on fixed head is a separate PR-only run and does not provide main-merge safety evidence. The addition of this ledger itself changes the PR head and requires fresh exact-head CI and independent review.
- **Owner Actions old-workflow disablement remains NOT PERFORMED / NOT VERIFIED. No merge allowed.** Even all-green GitHub Actions cannot establish a remote disable state or certify independent scientific validity.
