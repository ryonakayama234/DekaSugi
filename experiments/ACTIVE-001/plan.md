# ACTIVE-001 — Stage I active-question research plan (PR1 DRAFT)

id: ACTIVE-001-PLAN
status: draft_method_v0; NOT_FROZEN; no_activation_or_scoring_authority
updated: 2026-10-30
tags: preregistration, active-learning, adaptation, audit

## Hypothesis
H1 (primary): At identical public examples, grammar, query allowance (max 2), fixed finite task universe and independent evaluator, disagreement-driven B2 improves unknown-input accuracy versus random B1. The within-task gain is **not** across-task improvement or learned primitive acquisition.
H2: Reduction of semantic hypotheses is mechanistically related to accuracy gain (not sufficient as a success criterion).
H3: Unidentifiable, exhausted, inconsistent and invalid evidence are separated without false success.
H4: Query selection and CPU expenses may offset informational benefit; report separately.
H5: Episodes are reproducible and capable of forming later train-only records; this is NOT Stage II policy learning.

## Population and data boundaries (proposal, not frozen)
Fresh synthetic target functions drawn at semantic-class level from the fixed [InquiryWorld](../../docs/specs/ACTIVE-001.md): alphabet `a,A,b,B,space`, length 0..3 => 156 input values, eight fixed unary operations, max four operations, 4681 syntax programs pre-deduplication. Semantic equivalence uses all 156 input values; program class representatives are deterministic. No result from old TRAIN64/DEV64/FINAL128/FINAL112 may be reused as new confirmation. Inputs partition before any target labels are inspected into 28 public-candidate, 64 query-candidate, 64 evaluator-only. Two initial public labelled examples; all arms share examples and identical question candidates.
Proposed total **512 paired tasks** with target-family balancing, frozen independent task IDs, seeds and family-cluster mapping. Need independently justify target population, sampling weights, within-family dependence/cluster effect and positive opportunity prevalence; adjust methodology before formal freeze, not after reading outcomes. Include zero-advantage and information-unidentifiable tasks in whole-population analysis. 512 is a **planning value**, not a validated powered sample.
The scorer holds target ID, source/family/seed and evaluation labels privately; chooser never gets these fields. For publicly reproducible synthetic worlds, source code/seed visibility does **not** constitute a secure secrecy boundary: independent evaluator isolation and strict data-flow auditing are required, and leakage tests are mandatory.

## Arms and controls
B0: no queries and fixed canonical representative of semantic classes consistent with public examples.
B1: up to 2 uniformly sampled distinct query inputs without replacement; five explicitly frozen independent random replicate streams. Stops under the same identification/unidentifiability/resource states as B2.
B2: up to 2 max Gini-disagreement queries over uniform semantic version-space, deterministic stable query-ID tiebreak. No learned B3 until a separate Stage II plan.
All arms use equal target, public observations, allowed input pool, program set, interpreter/verifier and CPU environment. B1 five seeds are *within-task nuisance repeats*, never 5 independent tasks. Oracle answers selected valid question only. No learned macro injected.

## Metrics
Primary paired estimator = task-level mean heldout exact-match accuracy(B2) − mean over five B1 replicates, with 64 evaluator-only inputs per task. B0 serves reference. Effect unit: fraction / absolute percentage points; negative differences retained.
Proposed practical difference threshold: +0.05 (five percentage points), and predeclared 95% confidence interval **lower bound >0** using a paired cluster-aware procedure at independent target-family level; precise method, alpha, family stratification and power calculation MUST be reviewed/frozen **before any genuine scored tasks**. No claim of adequate power from N=512 alone.
Secondary: correctness per input/task, semantic identification, false-identification, stop state, query count, novel labels acquired, query informativeness, version-space shrinkage, invalid/missing records, compiler/candidate construction/search costs, oracle calls, selector CPU ns, interpreter calls, total CPU/wall ns (distinct units). CPU method must separate one-time/precomputation from per-task phases and show amortization horizon; never equate program candidates with primitive calls.
Report per-arm all cases and conditional ambiguous/question-eligible subset **separately**. If eligible support=0 => `not_estimable`. No choosing outcome-favorable strata after observation. Evaluation errors, answered queries outside allowed pool, repeated questions, missing third-audit, inconsistent provenance, target leaks are integrity/missingness states, not silently scored as failures.

## Stage structure and freezing
1. PR1 documentation only: plan, spec, ADR, ARCH-001/002, ledger, AGENTS, INDEX. Mark DRAFT; no actual test run or new scoring.
2. PR2 **invented-only** implementation: finite grammar enumeration and semantic dedup, one-step query ranking, update, property/negative tests. No fresh scored task outcomes, historical imports or benchmark access. Engineering receipts distinguish attempted/passed tests.
3. PR3 independent synthetic evaluator/evidence validation; adversarial replay, masked-private-label dataflow. Separate freeze of exact source tree/partitions/task policy snapshots/reviewer outcome and numerical precision/power; no automatic activation.
4. Only a separately approved new one-shot future evaluation after verified source locks and independent review. Record immutable originals and full unfavorable results; no sample-size stopping or reusing evaluation labels for development.

## Acceptance
Engineering PR2: deterministic finite equivalence classification, Gini partition arithmetic and tiebreak, B0/B1/B2 parity, strict response chronology and oracle contracts, negative tests for invalid inputs/duplicate answers/empty H/no discriminating q, no imports from legacy scorers/generators, explicit resource ceilings.
Scientific future (not yet authorized): paired accuracy effect >=+0.05, reviewed clustered 95% CI lower >0 and no contradictory invalid data; report query and CPU costs even if positive; future meta-learning/transfer remain untested. If design lacks identifiable opportunities or adequate statistical power => UNDERIDENTIFIED/NOT_ESTIMABLE and redesign before activation. Any P0/P1 trust issue => STOP.
Main merge blocked without exact-head independent review, safe CI, and independent verification that the old historic main-push scorer workflow remains disabled; do not infer owner setting from docs or green CI.

## Metrics / unresolved preregistration obligations
Unfrozen numeric/provenance items: task/family sampling procedure, exact seeds, disjoint split algorithm/hash, semantic universe class count and distribution, confidence-interval computation/cluster units and power, availability of truly distinguishable target pairs, target-labelled-holdout authority, query cost definitions, deterministic precomputation CPU accounting and source-first lock. Every unresolved item must be frozen before formal evaluation; initial proposed numbers are **not** confirmatory authorization.

[Spec](../../docs/specs/ACTIVE-001.md) / [run ledger](runs/README.md) / [ADR](../../docs/architecture/decisions/ADR-0005-active-inquiry.md) / [Issue #93](https://github.com/ryonakayama234/DekaSugi/issues/93).
