# Evaluator-side public artificial fixtures only

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
