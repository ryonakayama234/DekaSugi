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

## Hypothesis

H1: reproducible composition yields nonalias role-orbit diversity; H2: distinguishability is possible using allowed public interventions; H3: positive adaptive gain may occur in the 12 unselected natural-draw panels; H4: later truly independent-family and adequately powered learner transfer is feasible, but currently unproven. Counterexamples: invalid/aliased structures, no reachable differences, zero gain, inconclusive proofs and insufficient family diversity. This experiment is disclosed engineering only, not preregistered scientific confirmation.

## Metrics

Count every attempted root (48), role-variant slot (48), typed-source rejection, full invariant and exact-orbit pair proof, certified orbit lower/upper bound, twelve attempted panels grouped as positive/zero/invalid/NOT_CERTIFIED, per-panel adaptive and best open-loop MAP, node/plan counts, opportunity lower/upper bound with unknown retained, CPU/wall and exact-head source/artifact provenance. Never equate root samples or orbit classes with independent scientific families.

## Acceptance

PASS only if strict typed-draw and proof-cutoff tests, zero-resampling evidence, exact challenge positive/null controls, full-panel denominator retention, safe source-only CI, documentation validator and exact-head independent method/security review agree. If any proof limit, INVALID/NOT_CERTIFIED remains reported; if true family independence/power not established, SCIENTIFIC_STOP with no paid TRAIN, DEV/FINAL, new model or merge.
