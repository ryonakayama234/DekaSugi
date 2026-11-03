# EXP-REP-005-G0C3 — disclosed source-only engineering plan

id: EXP-REP-005-G0C3-PLAN
status: engineering_method_frozen_no_blinded_science
updated: 2026-11-03
tags: plan, source-only, synthetic, inquiry

Owner-delegated Issue #160; dependency on G0C V5 Draft #159, original head afed85765f0b419bd617635fe8bf85422d7bf513. Version CFAM-V1 frozen before *new* pilot inspection; previous handpicked G0C opportunities publicly known, hence no independent preregistered science. Exactly 48 index draws; one variant/root, no success-driven resampling; 12 contiguous four-root panels at B3, uniform prior and initial state zero. Full 115680-domain role-invariant and exact G0C role checker, 180s orbit global, 30s/panel, <=4000 schedules, <=250000 adaptive nodes. Missing/invalid stays full denominator, evidence is append-only.

Observe valid/invalid roots, 96 attempt slots, certified semantic role-orbit bounds, positive/zero/invalid/unknown panels, empirical opportunity interval, wall runtime, JSON SHA and exact-head Actions. Never call roots scientific-family N. Controls use existing disclosed positive/null fixtures only for tests; those outcomes cannot estimate prevalence.

```bash
python -m unittest tests.test_rep005_g0c3 -v
python scripts/check_docs.py
python -m scripts.rep005_g0c3_pilot --output .run/g0c3-v1.json --draws 48 --proof-seconds 180 --panel-seconds 30
```

Engineering pass needs tests and docs plus exact-head CI and independent review. Scientific G0C-3 power and independent-family gate remains STOP_NOT_CERTIFIED, learned inquiry improvement NOT_RUN, historical DEV/FINAL untouched.
