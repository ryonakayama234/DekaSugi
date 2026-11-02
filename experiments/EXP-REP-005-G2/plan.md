# EXP-REP-005 G2 — public-state repair synthetic source-only preflight

id: EXP-REP-005-G2-PLAN
status: IMPLEMENTED_IN_DRAFT / SCIENTIFIC_NOT_RUN
updated: 2026-11-03
tags: plan, synthetic, representation, counterexample, method

## Goal
Engineering feasibility of public-only representation repair in [Issue #150](https://github.com/ryonakayama234/DekaSugi/issues/150); scientific gate #148 remains STOP. Primary module packages/representation_repair. No paid real world learning, evaluation or historical scored source.

## Artificial fixtures and protocol
Use four visible Boolean public objects, legal set/pulse actions and charged cost=1. Tests construct an explicitly disclosed *synthetic* stationary lag-1 effect under preceding pulse(0), and provide four complete legal reset-from-zero episodes. The memoryless predictor cannot fit the same (0,set(1,0)) pair because lagged history changes successor. Four episodes disambiguate the candidate lag1 pulse(0) from other single public-action equalities. The learner receives only serializable PublicStep observations; generator logic lives in tests.

Negative controls: visible-state-only deterministic consistent trace -> NO_REPAIR_NEEDED; identical full public history with contradictory successors -> NOT_CERTIFIED (deterministic premise violated or grammar insufficient); chronology mutation/type forgery -> exception; checksum mutation -> rejection; unseen prediction row -> abstention. Same-capacity STATIC-Hplus correct-predicate control demonstrates no learning advantage is established.

## Execution, metrics and gates
Whitelist only `python -m unittest discover -s tests -p 'test_rep005_representation_repair_synthetic.py' -v` in a new isolated 5-minute GitHub Actions workflow. Record #tests, PASS/FAIL, exact head commit, run ID, artifact hashes if available. Engineering metrics: observed contradiction count, admissible typed feature candidates out of 24, paid actions, snapshot digest and executable dispatch. Do not aggregate invented transitions as independent families.

G0 pass is not claimed; source anonymity, causal-family population, matched new-world score, train cost amortization, future G3–G6 all NOT_RUN or NOT_CERTIFIED. No old DEV/FINAL or original workflow executes.

## Hypothesis
H-STATE: same public state/action contradictory successors within a stationary deterministic world refute a deterministic memoryless public-state predictor. H-REPAIR: one of 24 typed lagged-public-action equality features can resolve a disclosed artificial counterexample without seeing the hidden law. H-NULL: no observed contradiction or insufficient feature grammar must not yield an adopted concept. H-MATCH: equal-capacity STATIC-Hplus makes matching predictions, therefore this prototype proves no learned superiority.

## Metrics
Synthetic engineering only: charged public action count, conflicting visible-state context count, admissible typed feature count out of 24, snapshot byte integrity, successful fresh-process executable-body dispatch, explicit prediction abstentions, and each negative-control pass/fail. No heldout structural family effect or statistical p-value is defined. CI records include exact head and independent source/docs checks.

## Acceptance
- [ ] Valid same-world public fixture emits a deterministic memoryless contradiction and a consistent executable predicate from the 24-element grammar.
- [ ] Fresh-process Snapshot reload reproduces the witnessed public prediction; unseen context abstains; body-off/STATIC-Hplus attribution is not overstated.
- [ ] No contradiction -> NO_REPAIR_NEEDED; unrepairable same-history conflict -> NOT_CERTIFIED; invalid episode chronology and tampering rejected.
- [ ] Exact-head safe synthetic CI, research source integrity and docs/links pass. Independent expert review remains a separate requirement.
- [ ] Maintain G0b STOP, no historical scorer, no actual G3 paid TRAIN, no scientific DEV/FINAL.
