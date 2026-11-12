# WORLD-LEAN-1 — implementation / artificial fixture engineering plan

id: WORLD-LEAN-1-ENGINEERING-PLAN-20261112
status: IMPLEMENTATION_FIXTURE_ONLY / EVALUATION_FORBIDDEN
updated: 2026-11-12
tags: world, experiment-plan, fixture-only

Owner adopted design `WORLD-LEAN-EXPERIMENT-DESIGN-20261112-01` as head
`a0d0a203`, PR #208. Supervisor AGREE comment `6823583705` includes RQ1–3.
Separate Owner implementation GO authorizes *only* implementation, freeze,
artificial fixtures and submission to supervisor. The design parameters remain
untouched. The old CAL/SPEC records remain immutable.

Stage permitted now: isolated `packages/world_lean` public learner, separate
`world_lean_evaluator` fixture runner and protocol gate, exact code digest,
unit/negative tests, 100k transition benchmark and TRAIN-only ambiguity audit.
Stage **not permitted**: formal master seed, formal TRAIN/holdout materialization,
formal evaluation, positive B certification, merge/ready, or changes to old CAL.

The source-lock checker and the `world-lean-artificial.yml` workflow run only
new artificial tests. No legacy research workflows, old scored material,
DEV/FINAL data or production evaluation processes are imported.

After fixture receipts, STOP and request independent supervisor audit. Future
formal run needs separate Owner GO, new pinned source/runtime/manifest and
snapshot-before-evaluation custody. Current implementation deliberately raises
`OwnerEvaluationAuthorizationRequired` on the formal entrypoints.
