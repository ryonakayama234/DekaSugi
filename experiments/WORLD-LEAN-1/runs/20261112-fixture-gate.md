# WORLD-LEAN-1 / artificial fixture gate — 2026-11-12

id: WORLD-LEAN-1-ARTIFICIAL-FIXTURE-GATE-20261112
updated: 2026-11-12
tags: world, fixture, engineering-evidence

status: ARTIFICIAL_FIXTURE_PASSED_LOCALLY / CPYTHON_3_12_TARGET_REPLAY_PENDING / SUPERVISOR_AUDIT_PENDING
formal_seed: NOT_CREATED
formal_holdout: NOT_MATERIALIZED
formal_evaluation: NOT_RUN

Source commitment: `ee1ae0b144a0b1deb76034fc23465c9b76828719e98b8dcccd33b40674e4a147`.
Fixture deterministic evidence commitment:
`115f343854b1baeb89e4ab6e4ced205d65ed858da31bc4c70a4497c05212ce91`.
Full evidence JSON in this same directory, `20261112-artificial-fixture.json`.

Artificial-only local verification (`python3 3.13.5`, Linux):

- New 23 unit tests: **PASS**. World transition semantics, endpoint and selection
  behavior, DELETE and overflow no-op, COPY/PASTE, 4-field success, 12-action
  cut-off, finish-only scoring, data AST limits, OFF forbidden CALL, empty
  library at b=0, 64-event learning update budgets, canonical replay, local
  reachable examples, form-only ambiguity, and negative process isolation.
- 100,000 legal transitions: **~624,995 primitive transitions/s** (local single
  timing; not a guarantee for CPython 3.12.12 or arbitrary hardware).
  Engineering proxy with ×2 transition allowance, update sampling and one
  public artificial query timing for each arm: **~0.51 hours** for the design
  nominal 16-seed volume, below 36h CPU / 48h wall caps on this machine under
  the explicitly non-rigorous extrapolation. Inference I/O, worst-case
  construction distributions and cross-runtime effects can change it.
- STATIC-RANK generic grammar within 128 checked candidates: local INSERT
  candidate ordinal 1/128, local delete 1/128, copy 1/8, conditional 1/18.
  These are training-side **artificial** input/output fixtures, not holdout.
- TRAIN-only ambiguity audit: 4 independent *named artificial stream labels*,
  each TRAIN24 laws ×2 query =48. Ambiguous counts **3, 7, 2, 6** of 48,
  combined **18/192 = 9.375%**. The maximum stream is **7/48 = 14.58%**;
  this volatility must be reviewed as risk, even though the pooled point
  estimate is below the 10% design threshold. No sample discarded, no
  favorable redraw, no revision of demo count or formal holdout inspection.
- Negative process test: run copied learner sources in a separate `python -I`
  child with an isolated source root. Evaluator source/synthetic private
  sentinel absent from child import paths; child rejects extra `target`,
  `holdout` and evaluator metadata keys. This implements the **cooperative**
  threat model accepted under RQ2; it is not hostile same-UID custody.

**Freeze/audit caveat**: Source ordering and digests have been authored,
not independently approved. The evaluator never created formal seeds,
real tasks/holdout, scores or source-derived B evidence. Stop here for
supervisor review; official seeds/evaluation require a separate Owner GO.

Regenerate evidence only with artificial input and within the current source
lock. If changed source bytes are needed, create a new versioned lock and
obtain fresh review rather than silently rewriting a frozen artifact.
