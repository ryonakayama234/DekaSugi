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

## 2026-11-12 limited six-demo revision proposal

Owner selected (b) after PR #209's implementation PASS. [Design -02](../../docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-02.md) changes precisely one experimental input: four public demos (true2/false2) to six (true3/false3) per law. All derivative source, ordering and arithmetic are updated; arms, seeds, thresholds, cap and world semantics remain identical. [New order](../../docs/research/WORLD-LEAN-1-ORDER-FREEZE-20261112-02.md), [new source lock](../../docs/research/WORLD-LEAN-1-SOURCE-LOCK-20261112-02.json) and [new fixture receipt](runs/20261112-six-demo-fixture-gate.md) coexist with untouched -01 originals. Formal seed/holdout/scoring remains forbidden. Independent supervisor diff review precedes separate Owner adoption and later evaluation GO.
