# EXP-REP-002 engineering protocol
id: EXP-REP-002-PLAN-V1
status: DESIGN_ONLY; NOT_RUN
updated: 2026-11-01
tags: experiment, preregistration, active-learning, research

Status: DESIGN_ONLY / NOT_RUN / F0_NOT_FROZEN. Source: docs/specs/EXP-REP-002.md, Issue #130.

## Execution roadmap

G0: Resolve 3 P1 findings in PR #129, add negative tests, reproduce the existing disclosed baseline, obtain independent review at exact head. Never overwrite past results.

G1: Preflight new typed generator, canonical graph and motif-overlap checks, bounded model search, charged action/session interface, evaluator isolation and fixed arm contracts. Publish revisions before scoring if infeasible.

G2: Actual learning on nested 0,3,8,16,32,64 structurally diverse disclosed worlds. WAKE collects metered observations; SLEEP constructs role motifs from >=3 structurally different sources; DREAM plans synthetic discriminating questions. Store each snapshot and digest. Same-data replay 1/2/5/10 is an idempotence test, not epochs.

G3: Actual local use: train, inspect, load and use saved Snapshot in fresh disclosed worlds, choose legal actions, log all decisions, predict or abstain. Linux/WSL2 Python 3.12+ CPU standard-library.

G4: Actual disclosed scoring: 48 test worlds in 4 strata, 32 private audit transitions per world, budgets 0,2,4,8 charged actions and all comparator arms. Start a fresh session at each budget. Do not feed evaluator labels to learner. Score each world as one paired observation.

G5: Review: verify complete source, manifest and model hashes, safe CI, adversarial tests, CPU/wall/primitive/inference plus full training cost, trace reproducibility and independent code review. Report zero or negative effects. No automatic baseline promotion.

F0 and later: a new independent study requires separate source custody, pre-registration, power and statistical decisions, and explicit owner permission before one-shot FINAL. Never touch prior sealed experiments.

## Primary outcome

LQ and LA use identical learned Snapshot for inference but only LQ may consult the executable body to choose questions. Y(world,arm,budget) is the fraction of 32 exact full-vector matches, abstentions counted zero. AULC per world = average Y at budgets 0,2,4,8. Primary descriptive contrast is paired mean AULC(LQ)-AULC(LA) on structurally new compositions. Fixed active and role-neutral retrieval are strong controls. Candidate practical difference >=0.05 is an engineering target only, not a frozen formal hypothesis test.

Each code task updates AGENTS.md, docs/INDEX.md, ARCH-001 Mermaid, ARCH-002 contracts/flow, plan, specs, and dated run ledger together. Preserve old records and no automatic merge.

## Hypothesis
Concept-aware question selection LQ improves world-mean costed AULC against same-Snapshot query-blind LA, with identical prediction mechanisms.

## Metrics
Per-world AULC over 0,2,4,8 paid operations, exact transition accuracy, abstention, candidate and expanded primitive budgets, CPU and full training cost.

## Acceptance
Engineering PASS requires safe deterministic train/save/use/score, validated costs and negative tests, exact-head code review and full receipts. Scientific promotion requires separate independent F0 and untouched FINAL authorization.


## Executed-code scope amendment (source staged; score pending CI)
The first disclosed engineering pilot is direct-XOR-only, 5 objects, <=4 edges, PUBLIC roles hub/x/y/z/q; no gated actions, no paid setup/reset and no two-step question lookahead. This reduction makes the finite direct grammar tractable, and does NOT fulfill the complete planned H4 study. TRAIN nested 0/3/8/16/32/64; test 48 worlds (12/stratum), arms LQ/LA/LR/FA and budgets 0/2/4/8. Query policy's public role shortcuts are explicitly checked by fixed FA. Use typed fixed predictor commitment before evaluator-only audit. Scores and real CI state go in a new dated immutable run receipt, not the old design receipt.


## Measured direct-only execution outcome (engineering, not F0)
On exact source 7f32b8b, CI 150 tests PASS; TRAIN64 contained 3 unique structures and 320 paid TRAIN pulses, learned fork motif from n3. All 48 disclosed worlds, four arms and four budgets scored. Primary COMPOSITION LQ-LA +0.027995 AULC, but FA=LQ exactly, and DISTRACTOR LQ-LA=-0.020183. The fixed public-role heuristic sufficiently explains concept-aware policy's selections; proposed concept-body unique advantage is NOT demonstrated. Raw measurements and status: [run](runs/20261101-direct-preflight-measured.md) / [JSON](runs/20261101-direct-preflight-measured.json). No formal power or independent custody.
