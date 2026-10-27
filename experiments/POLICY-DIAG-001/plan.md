# POLICY-DIAG-001 — diagnostic pre-analysis plan

id: POLICY-DIAG-001-PLAN
status: proposed; not_run
updated: 2026-10-28
tags: preregistration, diagnostic, exploratory, design-only

## Scientific status
This is a **post-DEV64 exploratory diagnosis**, not a prospective blinded preregistration or new H3 confirmatory experiment. Source inputs, hypothesis definitions, metrics and exclusion rules are committed before diagnostic implementation. The frozen EXP-0003A v1 protocol and remaining FINAL128 are untouched.

## Research question
At which of selection, 8D feature representation, 5NN neighborhood, sequential decision gates, or search outcome does B2/B3 divergence diminish, based only on frozen snapshots and already observed public DEV64 evidence? See [spec](../../docs/specs/POLICY-DIAG-001.md) and [Issue #52](https://github.com/ryonakayama234/DekaSugi/issues/52).

## Populations / exposures / outcomes
Units: 64 fixed paired DEV task IDs with B2/B3; training evidence B1's WAKE160 and each arm's separately selected DREAM96. No additional task trials, no parameter tuning. Exposure: frozen B2/B3 snapshot membership, not a randomized intervention. Outcomes: feature/neighbor/decision differences and archived cost differences. Stratified 8-family labels only in permitted aggregated evaluator reporting, not policy input.

## Hypotheses and classifications
P-H1 selection redundancy, P-H2 representation bottleneck, P-H3 decision saturation, P-H4 action/cost insensitivity, P-H5 selection-objective mismatch. Findings may be multi-label or indeterminate. Distinguish direct observation, deterministic replay, exploratory mechanism inference; avoid false causal attribution.

## Metrics and analysis
Fixed definitions in the spec. Report B2/B3 selected-Dream Jaccard/count; feature vector collisions and conflicting utility; per-task ordered 5NN, set overlap, distances, support/veto/cost gate states; action/reason disagreements; existing paired cost/count differences; coverage/missingness. No parameter sweeps, p-values, new confirmatory confidence intervals, or bootstrap dressed as external validity. Preserve every task where available, including negative outcomes. Difference in final behavior may not identify any single upstream cause.

## Source validation / privacy
Require source-first hash lock, frozen snapshot identity and authenticated public DEV bytes. Private audit examples and FINAL128 never enter diagnosis. Existing public report may not contain all task-level records: declare `not_observed`, no invented rows. A separate secure archival obligation for original private ZIP remains unresolved.

## Implementation acceptance (later, separately gated)
Immutable policy reproduction; negative synthetic fixtures for ties/thresholds/veto/collisions/missing/corruption and deterministic source-order invariance; exact replay parity with `choose`; reproducible JSON/hash outputs; correct documentation, CI and independent review. Failure to obtain essential evidence yields inconclusive report, not retrying DEV64.

## Run state
`not_run`; no real metric outputs, measurements, learner updates, or trials were produced by this docs-only plan.
