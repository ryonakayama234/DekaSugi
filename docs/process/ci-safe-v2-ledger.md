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
