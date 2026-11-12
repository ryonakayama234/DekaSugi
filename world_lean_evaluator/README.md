# Evaluator-side public artificial fixtures only

id: WORLD-LEAN-1-ARTIFICIAL-EVALUATOR
status: FIXTURE_ONLY / FORMAL_NOT_AUTHORIZED
updated: 2026-11-12
tags: world, evaluator, fixture, boundary

`fixture.py` owns TRAIN-only recipe meanings and deterministic synthetic
example/trace generation. It is never distributed to the learner subprocess.
`protocol.py` records design constants and fail-closed formal entrypoints.
`gate.py` measures 100,000 legal synthetic transitions, one 64-event update,
1 query per arm, a 4-category STATIC-RANK reachability fixture, 4 TRAIN-only
ambiguity realizations and a private-root negative process probe.

```sh
python -m world_lean_evaluator fixture-gate --output /tmp/lean-fixture.json
```

These four named fixture streams are not the official 16 seeds, not the actual
holdout and not independent generalization evidence. Failure to reproduce
performance on CPython 3.12.12, or a larger ambiguity estimate, must be treated
as an audit finding and not patched using official holdout feedback.

## Six-demo revision -02 (proposed)

The TRAIN-only artificial generator emits six public law demos (T,T,T,F,F,F) followed by two balanced queries and reruns the same four named synthetic ambiguity streams. No official seed, holdout or formal scoring is created. See [design -02](../docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-02.md), [separate source lock -02](../docs/research/WORLD-LEAN-1-SOURCE-LOCK-20261112-02.json) and [fixture receipt -02](../experiments/WORLD-LEAN-1/runs/20261112-six-demo-fixture-gate.md).

## Repair -03: executable stages, synthetic-only current scope

The [repair specification](../docs/research/WORLD-LEAN-1-REPAIR-20261113-03.md)
is the current stage contract. `python -m world_lean_evaluator synthetic-dry-run
--root /tmp/a-new-synthetic-root` exercises manifest → artificial seed → TRAIN
fixtures → all snapshots → 24 synthetic trials → engineering summary. It never
calls official entropy or the formal holdout generator and makes no scientific
qualification. `freeze-manifest`, `formal-generation`, `formal-run` are implemented
for the future resumed run, require a matching external supervisor/Owner resume
record, and are **not run in this repair round or CI**. The data-free public
`packages/world_lean/protocol.py` is the sole demo-count definition; evaluator
`protocol.py` re-exports its constants.
