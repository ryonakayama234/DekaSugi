# EXP-COEV-001 — Counterexample-driven concept evolution / research spec v0.1

id: EXP-COEV-001-SPEC
status: proposed; design_only; NOT_FROZEN; no_scoring_authority
updated: 2026-10-31
tags: abstraction, learning, counterexamples, concept-library, independent-evaluation

## Construct and exclusions
Study *persistent cross-task learning*: whether a small typed-program learner, trained on independently generated tasks using counterexample questions, acquires reusable abstract skills and a selection policy that improve entirely fresh target classes. Distinguish OPPORTUNITY-002 levels: L0 representation, L1 bounded search, L2 query value, L3 persistent plasticity, L4 representation transfer. Primary L3. Neither toy-domain improvement nor learning a macro proves AGI, autonomy in the wild, or new primitive semantics. Historical OPPORTUNITY-001 TRAIN64, EXP-0003A DEV64/FINAL128 and EXP-0002B FINAL112 are immutable and not part of this research.

## Design alternatives (why this route)
- Continue ACTIVE-001 Stage I: evaluates within-task active querying, not persistent learning; important parallel project, but insufficient L3.
- Neural end-to-end learner: high expressivity, but weak causal attribution/cost at current CPU scale.
- ON/OFF Hebbian or RL controller: interesting L3 mechanism, but reward and identifiability uncalibrated; later branch.
- Typed structure induction + contextual frequency policy: chosen for auditable hypothesis, deterministic snapshots, finite cost, variable-independent exact holdouts.

## Experimenter-defined G1 grammar (not autonomously learned semantics)
String -> String. Input; UnaryOp(Input/UnaryOp(Input)); Conditional(Predicate(Input),BranchA(Input),BranchB(Input)) where BranchA/B are unary chains depth<=2. UnaryOp order: trim, lower, upper, reverse, drop_first, append_a; Predicate order: contains_a, is_empty. ASCII-space trim; lowercase and uppercase Python Unicode on a fixed ASCII alphabet; reverse by Python codepoints; drop_first empty->empty; append_a appends literal "a"; contains_a is literal lowercase "a"; is_empty tests length zero. No nested if, no arbitrary Python, no learned builtin callable, no recursive macro. Exactly 43 unary chains and 2*(43*43) conditional templates, 3741 syntactic programs before semantic dedup. Execution is pure, typed, deterministic. Program expansion caps, inference proposal budgets and costs must be frozen before actual evaluation. Learned parameterized structural templates never introduce new primitive semantics. **L0 expansion relative to old 3-op DSL is experimenter-supplied G1**.

## Data and unit of analysis
Fresh world uses the ACTIVE-001 compatible finite input universe from alphabet [a,A,b,B,space], lengths 0 through 3 (156 strings). One source-independent, cryptographically committed partition: 28 public-candidate, 64 question-candidate, 64 evaluator-only input IDs. Sample exactly 2 distinct initial public examples before viewing labels; same within-task pair across all arms. All training/DEV/FINAL target identities are sampled from semantic-equivalent program classes; their actual distinct-class counts and family balance MUST be established by score-free structure enumeration. No semantic target class may appear in both TRAIN and FINAL. A stable family is a **predeclared AST structural family**, not a hidden label available to the learner. The 64 audit inputs are only consumed in independent scoring; learner sees no evaluation IDs, predicted outputs, target IDs, source labels or future Oracle answers. Task-level IID assumption/finite sampling correction must be justified; clustering families, reuse of target class, or finite-population exhaustion require revising the statistical plan BEFORE source freeze. Count non-identifiable and zero opportunity tasks, never filter by outcomes.

## Learning mechanics and explicit local model
- Wake (per TRAIN task): start from two public pairs, choose <=2 *distinct* allowed queries using random or maximal disagreement of semantic hypotheses, obtain precisely these two trusted labels, find a bounded candidate using a fixed search engine, preserve failures/valid receipts.
- Sleep: extract repeated contiguous typed AST structures from independently solved TRAIN tasks; do typed anti-unification of shape-compatible expressions (up to two op variables) with deterministic lexicographic canonicalization; independently count >=3 supporting tasks; reject duplicate, unverifiable, recursively defined or over-budget templates. Do not use labels/outputs from hidden scoring.
- Library objective: compress TRAIN solution descriptions accounting for template definition cost and expansion cost. Cap 8 stored concepts; never mutate DEFAULT_REGISTRY or an existing experiment's sealed policy.
- Policy: publicly observable task features -> deterministic 64-bucket mapping; for each bucket and candidate skill use smoothed success/attempt counts to choose an order; append the original fixed grammar as fallback. A policy may learn skill choice but not see family/target ID. Freeze canonical snapshot hashes.
- Dream: optional TRAIN-only synthetically generated transformations for separate ablation. It must not contaminate DEV/FINAL. No automatic inference-time self-modification. Report no DREAM benefit unless controlled.
- The learner must never execute generated Python code; only validated ASTs and approved builtins.

## Five arms and estimands
C0: G1 fixed only, no TRAIN, no inference-time query.
C1: TRAIN using <=2 uniform random queries and Sleep/policy, zero inference-time query.
C2: same TRAIN tasks/budget and Sleep/policy using <=2 max-disagreement questions, zero inference-time query.
C3: frozen C2, <=2 random inference queries (5 predeclared streams nested within task).
C4: frozen C2, <=2 max-disagreement inference queries.
Extra *negative control*: same-size uninformed skill library, same search budgets. Do not call mere additional macro names a representational gain.
H1 primary: task-level mean of 64-audit-input accuracy(C2) - accuracy(C0) on all admissible paired tasks; aspirational material effect >=+0.10 absolute. H2 C2-C1, H3 C4-C3, H4 total compute and budgeted search, H5 separately registered later transfer. H2-H4 descriptive until multiplicity correction is frozen. **No result exists at design stage.**

## Sample size / statistical caveat
Initial planning TRAIN256 / DEV128 / FINAL2048. Each 64 audit-input result belongs to its task, not 64 independent observations; C3 five RNG repeats nested within task. Proposed two-sided 95% conservative bounded-IID Hoeffding CI for D in [-1,1]: radius sqrt(2*ln(40)/N), ~0.060 at N=2048. This does NOT justify IID or sufficient target population. Confirm effect only if observed Δ>=0.10, CI lower>0, independent custody and evidence gate pass. If finite target classes cannot support fresh IID tasks, DO NOT run this as confirmatory; redesign distribution/N/analysis in a new version before training/freeze, not after reading outcomes. No optional stopping, posthoc family optimization, rerun-on-failure, or holdout retuning.

## Cost, failure and threat model
Separate primitive executions, structural candidates, expanded AST nodes, Oracle query count, learned policy inference CPU, train CPU, evaluator CPU, process CPU nanoseconds, wall, max RSS, per-task amortization. Precompute costs and raw measurements recorded separately. No efficacy conclusion from synthetic fixture tests. Fail closed on invalid program, invalid observation order, private field leak, missing label/evidence, split contamination, source hash mismatch, budget overrun, target semantic-class overlap or evaluator isolation failure. Invalid runs => NOT_ESTIMABLE, not zero accuracy.

## Custody and activation
Use separate evaluator process/container with authenticated allowlisted IPC, isolated secrets and labels, immutable results and independent recount. Schema alone does not authenticate an Oracle. Freeze code/tree blobs, task distribution, dataset source, seed roots, split commitment, snapshot, evaluator and analysis code BEFORE any FINAL scoring. Existing ACTIVE-001 draft E0 (#105) is NOT an independent evaluator or approval. New FINAL runs require separate explicit activation record and independently reviewed exact-head CI plus verified historic workflow-disable state. No main auto merge, no automatic score scheduling.

## Implementation responsibility
packages/concept_world (grammar, finite semantics), concept_learning (episodes, induction, snapshots), concept_search (bounded learner), concept_custody (independent evaluator interface), concept_metrology (read-only audit/cost). Separate from packages/inquiry_world and previous frozen packages/learning. See [plan](../../experiments/EXP-COEV-001/plan.md), [ADR](../architecture/decisions/ADR-0006-coev-learned-concepts.md), [Issue #106](https://github.com/ryonakayama234/DekaSugi/issues/106).

## PR1 structural feasibility finding (2026-10-31; invented-only local enumeration)
A fresh G1 implementation enumerated 3,741 distinct syntax programs and exactly **895 finite-domain semantic equivalence classes** over the 156 inputs (866 classes have a conditional representative, 29 have a plain representative). This is structural source analysis, not target scoring or learned improvement. Hence 2,048 *different target classes* is impossible: reject that interpretation of FINAL2048. Revised design: independently partition the 895 class IDs into disjoint TRAIN / DEV / FINAL **class pools** (including structural-family quotas), then sample target tasks IID **with replacement within the separately sealed FINAL pool**, with fresh independently drawn public-pair sessions. Repeated targets are intentional; report unique classes, repetition and conditional-on-frozen-pool estimand. IID here is *conditional on the fixed grammar, pool and frozen learner*, not evidence of general out-of-support transfer. Before scientific freeze, independently check whether strict class-pool isolation leaves enough train opportunities and whether the sampling scheme supports generalization. Exact split seed/weights and resampling unit remain NOT_FROZEN; no official scoring is permitted.

## Binding pre-TRAIN scientific validity correction v0.2 (Codex P1; 2026-10-31)

**Supersedes every earlier stage ordering that put formal TRAIN before source/method/seed freeze.** Local PR3's publicly seeded 256-task `simulate_train(20261031)` is **engineering training on invented known fixtures**, not the registered scientific TRAIN256 cohort. It demonstrates code that truly changes candidate concepts and policy state, but it must never be used to select confirmatory method, source split/weights, sample size, seed, effect thresholds or subsequent formal snapshots.

New mandatory order: **(0) research design + pretrial finite-world feasibility; (1) invented-only G1 and learning algorithm prototype; (2) independently reviewed semantic-class pool allocation, IID-with-replacement task law, outcome analysis, multiplicity/power, resource budget, fresh confidential seed roots, target/Oracle custodian, source/tree hashes and verified historic workflow disablement — FROZEN BEFORE ANY REAL TRAIN; (3) source-locked fresh real TRAIN256 using only the separate reviewed TRAIN custodian, with genuine selected answer receipts and TRAIN-only reward; (4) freeze trained library and contextual policy snapshot before any real DEV; (5) independent DEV diagnostic / evaluator verification under frozen rules, no policy retuning; (6) separately activated new one-shot FINAL2048 with original evidence preservation, audit and negative results; (7) independent L4 preregistration if warranted.** If the proposed N/target distribution is infeasible or the review fails, stop and version a new plan **before** formal TRAIN; do not retrofit the publicly observed PR3 pilot to the formal population. No real TRAIN/DEV/FINAL or formal H1 score is authorized by PR1-PR3.

Reference: [Issue #106](https://github.com/ryonakayama234/DekaSugi/issues/106), [PR #107](https://github.com/ryonakayama234/DekaSugi/pull/107) method-review P1.
## PR2 engineering implementation checkpoint
`packages/concept_world` now contains an isolated typed finite-world interpreter, 3741 enumeration, 895-class semantic dedup and deterministic query-disagreement arithmetic. `test_concept_world.py` is invented-only, no official targets. The 28/64/64 partition is a structural fixture; future custodian must withhold private labels and not export its private audit IDs. No actual persistent learning or evaluation is implemented in PR2.

## F0-A structural feasibility preview (Issue #111; no official scoring)
The candidate class-pool split can be represented by **358 TRAIN, 179 DEV, 358 FINAL** disjoint finite-domain behavior classes using independently stratified plain/conditional representative groups. This is a fixed-salt *PUBLIC SYNTHETIC PREVIEW* only, not an independent source/seed freeze, actual TRAIN or source of official targets. At 2048 hypothetical IID with-replacement FINAL task draws from 358 equally likely class IDs, many task sessions repeat identical semantic functions. The conditional-on-frozen-pool estimand and statistical assumptions remain subject to F0 review; no evidence of positive heldout H1 is generated. [Receipt](../../experiments/EXP-COEV-001/runs/20261031-f0a-structural-preview.md).

## F0-A reviewer P2 canonical-pool correction
Public fixture equality was vulnerable to a tuple subclass that compares equal but iterates forged class IDs. Metrics now validate exact built-in tuple/int types and use internally reconstructed canonical pools, with new same-digest forged-iterator negative test. Independent source/seed authority still unimplemented; results structural only.
