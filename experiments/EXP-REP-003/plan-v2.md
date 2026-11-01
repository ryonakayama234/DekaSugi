# EXP-REP-003 — G0–G5 一貫実施計画 / V2
id: EXP-REP-003-PLAN-V2
status: DECISION_CANDIDATE / NOT_RUN / F0_NOT_FROZEN
updated: 2026-11-02
tags: experiment, preregistration, learning-curve, active-learning, evaluation

**Source of truth**: [V2 science/architecture decision](../../docs/specs/EXP-REP-003-DECISION-V2.md). Previous [V1 plan](plan.md) is design history, not a second scoring protocol. Issue #133, Draft PR #134.

## Hypothesis
Can a concept body learned from paid public observations in distinct structural/semantic TRAIN worlds improve **question selection** in anonymous conditional two-step worlds (LQ−LA) and beat optimized fixed active, rank-only, episodic and body-ablated comparators in fresh structural families? Existential distinguishability is a prerequisite, NOT success itself. Null/underidentified is acceptable.

## Research units
- Initial world grammar: n4 binary public variables, one unit-cost bit `set(i,v)` or `pulse(i)`, max two typed DIRECT / GATED edges, synchronous before-state XOR update. Randomized opaque IDs, full states observable after paid interventions.
- Pre-scoring witness: complete cost-bounded legal plan enumeration; WITNESS iff two models predict different public traces, NO_OPPORTUNITY iff complete legal-plan exhaustion, else UNKNOWN; grammar must be fully enumerated. Witness is not private audit and never leaked to learner.
- Four disclosed strata: renamed invariant, conditional novel whole-graph composition, unseen semantic rule, distractor/contradiction repair. True family diversity explicitly recorded. No engineering result can be called independent population-level evidence.
- Planned TRAIN: n=0/3/8/16/32/64 distinct public worlds, with topology and semantic family counts; 1/2/5/10 identical evidence replays as idempotence control, **not** stochastic epoch.
- Planned disclosed evaluation: 48 worlds (4 × 12), arms LQ/LA/LR/ER/FA/FX/BODY-OFF, budgets 0/1/2/4, 32 evaluator-only transition audits per arm/world/budget. All study dimensions **candidate design**, subject to G1 feasibility lock before any actual scores. Do not recycle REP002 0/2/4/8 horizons.
- Uniform semantic-class prior and exact costed two-step discriminating-plans information criterion. Every predictor frozen **before** auditor inputs.

## Metrics
Primary descriptive paired world-/family-level signed mean `AULC(LQ)-AULC(LA)`; attribution co-gates LQ−FA, LQ−ER, LQ−LR, LQ−BODY-OFF. `Y=full-vector audit matches/32` (ABSTAIN = 0 plus separate reporting), `AULC=average_b Y`. No transition/horizon pseudoreplication. Record opportunity witness length/cost, actual question discriminating rate, model applicability, contradictions/retractions, calibration of confidence/abstention, OOD negative transfer and semantic family diversity.

**Resource budget**: same fixed maximum charged actions **and** same precommitted expanded primitive nodes / model tests / planner rollout cap for every arm; meter all fallback and concept expansions, CPU/wall/RSS, train/sleep/dream cost and amortization over N uses. Numeric caps are frozen after strictly nonscoring public feasibility tests and before results. Invalid input or incomplete enumeration must fail-closed / UNKNOWN.

## Work execution (single large program; no micro-approval for routine steps)
| Gate | Actual work | Exit evidence | Stop on |
|---|---|---|---|
| G0 | review REP002 parent exact head and stack, correct P1 safety claims; preserve historic source; decide initial engineering baseline | source/readme/CI/custody review log | unresolved safety blocking isolated safe study |
| G1 | implementation of n4 environment, paid legal actions, hypothesis enumeration, semantic canonicalization, witness oracle, 2-step planner, common ledger; adversarial tests; no scores | WITNESS and NO_OPPORTUNITY and UNKNOWN fixtures, no hidden-role leakage, feasibility manifest | no discriminating legal 2-step plan / exhausted common resources |
| G2 | implement and execute disclosed WAKE observations, SLEEP causal concept abstraction, DREAM counterfactual planning, versioned Snapshot, CLI train+inspect | nested TRAIN curves; validated saved and round-tripped Snapshots, negative witnesses, exact-data replay controls | leaked hidden truth, non-deterministic data, invalid schema, insufficient independent structures |
| G3 | CLI use saved Snapshot on fresh public world with actual paid queries, save public trace, contradictory repairs and immutable PredictionCommit | at least informative / counterexample / UNKNOWN traces, saved commits and operation costs | audit selects predictor or uses hidden labels |
| G4 | evaluator-only disclosed raw scoring, 7 arms × 4 budgets × 48 worlds, per-family paired reporting, exact replay twice | append-only full raw rows, SHA source/run/snapshot, negative effect and resource report | missing arms, unfair budget, selective worlds, non-reproducibility |
| G5 | independent exact-head review, CI + docs + safety tests, scientific verdict independent from engineering verdict | adoption/hold decision and observed limitations | any major P1 invalidates mechanism claims |
| F0 (later) | separately reviewed and authorized design/power/statistical methods/custody; DEV and one-shot FINAL explicit gate | formal preregistration | NOT AUTHORIZED BY V2 |

## Acceptance
Engineering: deterministic legal train→save→inspect→use→commit→audit with valid data and adversarial negative tests, docs diagrams and contracts updated every task, source and experiment records retained, exact-head safe CI and independent code review.

Scientific: positive **only** if LQ−LA, LQ−FA, LQ−ER, LQ−LR and LQ−BODY-OFF and error/transfer/cost checks survive adequate independent family sampling and preregistered decision law. No fixed arbitrary significance/power inferred from 48 handcrafted worlds. Otherwise conclude NULL / POLICY_ONLY / FIXED_SUFFICIENT / NEGATIVE_TRANSFER / UNDERIDENTIFIED / INVALID.

## CLI contract proposal (NOT EXECUTABLE as of V2)
```bash
python -m packages.rep003 preflight --scope disclosed --output .run/rep003/opportunity.json
python -m packages.rep003 train --worlds 64 --snapshot .run/rep003/snapshot-v3.json
python -m packages.rep003 inspect --snapshot .run/rep003/snapshot-v3.json
python -m packages.rep003 use --snapshot .run/rep003/snapshot-v3.json --world-index 301 --budget 2 --trace .run/rep003/use.jsonl
python -m packages.rep003 evaluate-disclosed --output .run/rep003/pilot.json
```
No old DEV/FINAL invoked. Draft branches not merged automatically. See the V2 spec for full typed contracts, operational logic, risks and trust boundaries.

## Current execution status / scope divergence (2026-11-02)
[Reviewer-corrected **engineering subset**](../../docs/specs/EXP-REP-003-ENGINEERING-V1.md) has implemented an <=1-edge finite grammar, not this plan's full two-edge compositions or body-specific causal attribution. Paid history consumes 4 pulses and two-stage witness a further 2 operations (total 6). To observe effects past conditioning, disclosed engineering budgets are **0,1,2,4,6,8** (a pre-existing V2 budget 0/1/2/4 is not treated as enough to prove two-stage necessity). Full G0–G5 only completes at *reduced disclosed engineering* fidelity; full V2 and F0 remain distinct unfinished research. No publication-level mechanism claim even after synthetic CI success.
