# EXP-REP-004R — run ledger
id: EXP-REP-004R-RUN-INDEX
status: NOT_RUN
updated: 2026-11-02
tags: experimental, run, evidence, planned

## 2026-11-02 — 設計決定稿候補
id: EXP-REP-004R-20261102-DESIGN
status: DESIGN_ONLY / NOT_IMPLEMENTED / NOT_TRAINED / NOT_SCORED / NO_FORMAL_F0
primary_module: packages/rep004
source_parent_commit: 24e660d8c6926a618595e4747917be59de35b602
parent_historical_score_sha256: 70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3
experiment_spec: docs/specs/EXP-REP-004R.md
experiment_plan: experiments/EXP-REP-004R/plan.md
note: A docs-only design proposal; no patch, no new learning Snapshot, no local USE execution and no scored trials. New dated immutable runs will be appended in the implementation PR.

## Execution authority (2026-11-02)
User approved implementation and end-to-end synthetic learning/use/re-scoring on a separate Draft implementation PR. No run is considered completed until CI and exported raw evidence are checked. Historical source and original 1,920 rows remain frozen. The CI evidence artifact contains all six corrected raw score dumps, snapshots, separate-process USE receipts and an aggregate summary; results and exact hashes must be appended in a distinct dated ledger after verification.
