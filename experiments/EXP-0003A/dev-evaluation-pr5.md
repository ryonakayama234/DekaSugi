# EXP-0003A PR5 — DEV engineering execution record

id: EXP-0003A-PR5-DEV-PLAN
status: implementation_pr; DEV_not_run; FINAL_not_run
updated: 2026-10-27
tags: dev, preregistration, engineering, gate, evidence

## Hypothesis / scope
An independently implemented evaluator can reconstruct the frozen TRAIN/DREAM
skill and B1/B2/B3 policies exactly and produce paired DEV64 four-arm evidence
without training-audit contamination. DEV64 is an engineering smoke, not the
H3 confirmatory FINAL128.

## Freeze and dataset
Only EXP-0003A plan-v1, freeze-v1, fixed source blob manifest, TRAIN160,
DREAM512, precommitted DEV64 hashes. Do not update those assets. Do not reopen
EXP-0002B FINAL112 as new holdout. DEV/FINAL generation and scoring are
forbidden in PR CI. Train fixture validation only before code review.

## Metrics / output
- Exact frozen source/snapshot / DEV partition integrity result.
- B0/B1/B2/B3 verified success, false solved, unanswered, number of candidates,
  canonical primitive invocations, choice action/reason, trace, CPU and wall.
- Per-task pairing, B2−B3 differences and regressions, OOD false ON.
- Descriptive eight-family cluster bootstrap, original artifact hash, source SHA,
  all failures and limitations, independent review state.

## Acceptance
The code passes unittest and documentation checks, exact-head CI and independent
review. Verify fail-closed tests before even generating DEV. DEV run only after
a separate reviewed main-push gate. Store public and evaluator-private JSON as
write-once CI artifact; independently recompute totals and raw SHA. Engineering
success is not H3 primary scientific success; no default library promotion.

## State history
- 2026-10-27: Issue #44 and PR5 development branch initiated. No DEV64 or
  FINAL128 scoring, no independent scientific claim.

## Review amendment: non-overlapping cost ledger (2026-10-27)
PR5 Codex review identified omitted timing of source-first freeze verification
(including the first TRAIN/DREAM replay), and no per-arm policy inference CPU/wall.
The evaluator records separately: freeze verify, second replay, snapshot
validation, asset-load total, DEV generation/validation, four-arm DEV evaluation,
and DEV aggregation. Four-arm evaluation **includes** individual B1/B2/B3
policy inference, search and audit; do not sum these overlapping values twice.
The inner TRAIN/DREAM run cost is diagnostic detail within the second replay.
A CPython3.12 TRAIN-only test checks both replay buckets and a separate
synthetic/TRAIN test checks arm-level inference aggregation. Still no DEV/FINAL.

## DEV64 post-PR5 one-shot activation (Issue #46)
The new activation PR introduces only a main-push first-attempt-only scoring
workflow and a **separate** read-only stdlib verifier. Trigger requires a tagged
reviewed merge commit and successful document/unit/source freeze prechecks.
Same SHA runs B0/B1/B2/B3 against sealed DEV64, and emits original public and
private JSON, independent recount and original-byte hashes with partial attempt
evidence on failure. This is engineering only; no FINAL128/H3 confirmation or
parameter retuning. The activation outcome must be appended **after** the main
run with actual run ID, SHA and independently checked values.
