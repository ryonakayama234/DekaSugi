# POLICY-DIAG-001 — Policy Identifiability Diagnostic Specification

id: POLICY-DIAG-001-SPEC
status: proposed; design_only; not_implemented
updated: 2026-10-28
tags: policy, dream, diagnosis, research, metrology

## Objective and authority
Read-only analysis of fixed EXP-0003A B2 random-Dream and B3 counterfactual-Dream policy behavior. Source of truth: [Issue #52](https://github.com/ryonakayama234/DekaSugi/issues/52), [EXP-0003A plan](../../experiments/EXP-0003A/plan.md), [freeze](../../experiments/EXP-0003A/freeze-v1.json), [existing DEV64 ledger](../../experiments/EXP-0003A/runs/20261027-dev64.md).

Main module studied: `packages/exp0003a/pr3.py` `ArmSnapshot`/`choose`. Future code location `packages/policy_diagnostics` (not created in this PR). Present metrics and research classifications are proposals, **not measurements**.

## Competing explanatory hypotheses
P-H1 selection redundancy; P-H2 feature representation collisions/loss; P-H3 policy threshold saturation/veto; P-H4 differing policy actions without different observed primitive cost; P-H5 alignment of near-positive selection with expected decision change. These hypotheses can coexist. `unidentifiable` is a valid finding; DEV64 is post hoc exploratory evidence only.

## Strict observational population and estimand
Fixed previously scored DEV64 public TaskSpecs: per-matched-task comparison of B2/B3 snapshot-dependent selected-neighbor evidence and resulting action; report already archived cost differences only. Sampling uncertainty cannot be generalized from synthetic 8-family DEV. No DEV generator, new synthesis, verification, audit, or FINAL128 operation.

## Exact policy contract
`features(TaskSpec)` public 8D; mean absolute distance; sort all TRAIN160+DREAM96 per arm by `(distance, task_id)`; take five. `close_support = sum(d <= .18)`; `on_support = sum(prefer_on for all five)`; `mean_call_saving = mean(off_calls-on_calls for all five)`; `veto = any(off_correct and on_audit_invalid)`. Sequential gate: `close_support <3` → OFF; veto → OFF; `on_support<4` → OFF; `mean_call_saving<2` → OFF; else ON. Tie cases stable by opaque public task_id. Preserve original choose and reject disagreements.

## Diagnostic metrics and controls
- Dream96 set overlap: count, Jaccard (with no implication of information equivalence).
- Snapshot feature duplicates/collisions and differing label/cost in equal 8D coordinates.
- DEV64 paired 5NN set overlap (0..5), ordered neighbor equality, per-neighbor distance, label, signed cost.
- Decision gate trace, first blocker, veto, per-arm action and reason disagreement.
- Existing DEV64 cost/candidate/correctness differences; never re-score or fabricate unavailable counterfactuals.
- Coverage (valid task rows / 64) and explicit `not_observed`, `invalid`, `non_comparable` states.
- Exact denominators, source SHA, metric version, units, privacy classification, missingness policy, rationale and competing explanations in outputs.

## Trust and data contract
Inputs are frozen B2/B3 snapshots, public sanitized archived DEV evidence with checksum and strictly permitted identifiers. Verify immutable source manifest and snapshot/data SHA **before** replay. No evaluator-private raw records, third audit examples, generator-only family/seed/source IDs to learner; FINAL sealed. Do not synthesize private bytes from generator. Preserve old original failed Action and subsequent successful audit. If authorized public per-task bytes are unavailable, emit `not_observed`; do not infer records from totals.

Proposed record `PolicyDiagnosticRecord/0.1`: `schema_version`, `task_id`, `source_refs`, `policy_reconstruction.B2/B3{neighbors,distance,close_support,on_support,mean_call_saving,veto,first_gate,action}`, `comparison{neighbor_overlap,action_disagrees,archived_primitive_difference}`, `classification{mechanism_labels,status,alternatives,evidence_refs}`. Optional fields may be absent/null with explicit reason. Human conclusions remain distinct from reproducible observations.

## Acceptance and negative controls for later implementation PR (no implementation in this PR)
Synthetic cases: different neighbors/same action, differing action/same cost, feature collision with conflicting label, exact 5NN ties, veto precedence, boundary equal to each threshold, corrupted source/checksums/duplicate task IDs/missing records, input permutation invariance. Replay must match unmodified `choose()` exactly on eligible tasks. Never change frozen hashes, thresholds, dream selection, or source policy. No new DEV/FINAL scoring. Independent exact-head review and CI, docs/index/architecture/dataflow/experiment report synch, fail closed on P0/P1.

## Exit
Explain observed mechanism(s) with caveats or explicitly `unidentifiable`; prioritize a *future* separately preregistered new method/fresh holdout if change is justified. Do not assert H3 confirmation, cross-domain transfer, general intelligence or total CPU benefit.
