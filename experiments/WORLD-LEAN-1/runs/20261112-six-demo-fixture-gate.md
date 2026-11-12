# WORLD-LEAN-1 / six-demo artificial TRAIN fixture gate — 2026-11-12

id: WORLD-LEAN-1-SIX-DEMO-FIXTURE-GATE-20261112
updated: 2026-11-12
tags: world, fixture, engineering-evidence, six-demo
status: PENDING_EXACT_HEAD_CI_REPLAY / SUPERVISOR_DIFF_REVIEW_PENDING
formal_seed: NOT_CREATED
formal_holdout: NOT_MATERIALIZED
formal_evaluation: NOT_RUN

This is a **new -02 record**, not an edit to the old [four-demo receipt](20261112-fixture-gate.md). It is bound to [design -02](../../../docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-02.md), [order -02](../../../docs/research/WORLD-LEAN-1-ORDER-FREEZE-20261112-02.md) and [source lock -02](../../../docs/research/WORLD-LEAN-1-SOURCE-LOCK-20261112-02.json).

## Scope and reproducibility

- Four original artificial TRAIN-only fixture stream labels, TRAIN24 recipes in each stream, six specification pairs per recipe (T,T,T,F,F,F, unlabeled) and balanced two queries. The sample sequence is fixed by the named stream, not repeatedly redrawn to improve ambiguity.
- Ambiguity is present if recipes matching **all six** public demos disagree on a query final state. The threshold remains 10%, and ambiguous queries are not excluded.
- The historical four-demo audit was 3/48, 7/48, 2/48, 6/48 = 18/192. It is **not** an estimate of six-demo performance.

## Evidence state

- Six-demo design transition ceiling: **252,928,000**, versus 185,688,064 in -01. The 48h wall / 36h CPU / 2GiB saved-bytes caps remain unchanged.
- Expected commands: `python -m unittest tests.test_world_lean_fixture -v`; `python scripts/verify_world_lean_freeze.py`; `python -m world_lean_evaluator fixture-gate --output /tmp/world-lean-artificial-evidence.json`.
- Added two negative regression tests: old four-demo TRAIN payload and four-demo inference must be rejected. Old historical files are not modified.
- Six-demo ambiguity counts and fixture PASS/FAIL: **PENDING exact-head CI execution; numbers must be copied from the actual CI artifact**. No results are claimed before that execution.
- The PR workflow uploads the TRAIN-only evidence JSON as `world-lean-six-demo-train-only`. Formal generation and scoring entry points remain fail-closed.
- A failure remains a failure; do not silently change the ordering, thresholds, arms, seed count or cap to force passage.

Supervisor diff review and separate Owner adoption precede another explicit evaluation GO. This receipt and successful fixture CI (if achieved) are not authorization to generate formal seeds, materialize holdout, run an official experiment or merge.
