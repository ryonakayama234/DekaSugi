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

## PR2 engineering-only observation — not confirmation or method freeze
An isolated synthetic fixture found 878 semantic classes / 4,681 syntax programs and passed 5 local Python 3.13.5 tests; full-scored study **still has zero observations**. Split seed 20261030 and first two public inputs belong to invented calibration, not to a source-locked confirmatory distribution. Study population/512 tasks/power/95% CI and target sampling remain NOT_FROZEN, and H1 acceptance cannot be assessed. [Receipt](runs/20261030-pr2-local-synthetic.md).

## PR2 correction — falsifiable engineering hypotheses (2026-10-30; NOT_FROZEN)
The P1 review identified three distinct local integrity threats: class vote inflation/budget-state mismatch, split pool overlap into evaluator-only IDs, and policy-conformant-looking nonmaximal B2 proposals. P2 identified a test suite that can skip critical assertions. Before the future independently scored study, synthetic fixtures must reject each defect with negative tests and exact-head CI plus an independent review. Replay of deterministic random seed is required but **external independent seed freeze** still belongs to PR3. Planned 512 tasks, power/sample model, actual evaluator and target secrecy remain unfrozen; scientific score = 0. Frozen historical results are never inputs to this patch. [Engineering receipt](runs/20261030-pr2-integrity-repair.md).

## PR2 P1x2 acceptance checkpoint — synthetic-only, not a scientific preregistration freeze
The accepted *engineering question* is whether the learner rejects auditor-only query pool substitution and impossible historical selection/receipt sequences, not whether actively asking questions improves unknown-task performance. Add the active-query/2 full-history contract, canonical split reconstruction and exact allowlisted adversarial regressions in one PR with AGENTS, INDEX, ARCH-001/002 and an immutable evidence receipt. Public fixed 156-input toy world only; no change to the proposed but unfrozen N512 study, independent source ownership or future transfer tests. Prior historical TRAIN64/DEV/FINAL are excluded. [Engineering run](runs/20261030-pr2-history-boundary-integration.md).

## PR2 P2 synthetic Catalog identity hypothesis (2026-10-30; NOT_FROZEN)
Review identified a **local** provenance gap distinct from source-authenticated scientific scoring: a caller can hand the learner an altered by_id map while preserving the world digest and classes. Require exact reconstructed Catalog equality to the trusted fixed finite-world catalogue on both session creation and replay, and test malformed signatures, representative programs, class IDs, lookup keys, syntax count, mutable lookup, order and unchanged canonical copies. Engineering cost should be bounded by one cached canonical build; preserve true question selection semantics and B1 reproducibility. [Synthetic run](runs/20261030-pr2-catalog-integrity.md). Scientific observations remain zero, planned N512 and power/evaluator remain unfrozen, historic TRAIN64/DEV/FINAL excluded.

## PR2 P2 lookup canonicalization checkpoint (2026-10-30, NOT scientific scoring)
Acceptance criterion: reproduce a `MappingProxyType(dict_subclass)` whose normal equality preserves the canonical map but `__getitem__` returns forged predictions; B2 correct argmax, B1 seeded policy, semantic posterior, replay and final program must remain identical to a trusted-canonical run; false `query_unidentifiable` rejected. Use a cached internal reference for **actual calculation**, not only comparing candidate objects. Add synthetic-only explicitly allowlisted regression tests and align AGENTS, INDEX, ARCH-001/002 Mermaid, spec, roadmap, README, and new separate engineering receipt. No N512 preregistration freeze, hidden evaluator, real score or historic data rescore is authorized. [Run](runs/20261030-pr2-lookup-canonicalization.md).

## PR2 container-subclass integrity — local engineering gate (2026-10-30; NOT FROZEN)
New P2 adversary on b2acf54 uses `LyingIds(tuple)` with equal values but overwritten `__iter__` to multiply a single semantic class's apparent voting weight. Test its effect on partitions, disagreement choice, random control, final_program and false terminal marking, then require exact primitive field types for session/proposal/answer/trace before replay. Add invented fixtures for subclass IDs, inner answer tuples, status/digests, bool-as-int proposals and history answer fields. Only explicit safe CI allowlist tests; never historical evaluator imports or scored experiment reruns. Scientific ACTIVE-001 observations = **0**. [Run](runs/20261030-pr2-container-types.md).

## #96 pre-scoring method alternative — versioned candidate only (2026-10-30)

See [method-v1-candidate.md](method-v1-candidate.md) and its [unscored review ledger](runs/20261030-pr3-feasibility-proposal.md) for a distinct proposed feasibility/design response to Issue #96. The current PR1 draft remains an unfrozen historical draft; this addendum does **not** freeze N=512, 5pp, 95% CI, target families, source seeds, scoring, or independent evaluator. The new candidate separates hypothesis reduction from held-out decision utility and the identification/power gate. No old or fresh scored data are read or executed.

## ACTIVE-001 #96 — Stage I decision text v2 (2026-10-30, UNFROZEN)

[Versioned decision draft v2](method-v2-decision-draft.md) / [ADR-0006](../../docs/architecture/decisions/ADR-0006-active001-scientific-design.md) / [no-scoring ledger](runs/20261030-design-v2-review-ledger.md) refine future methodology without rewriting the historical PR1 draft. Proposed Stage I separates an unscored finite public-context feasibility audit from N4096 IID task-level B2-vs-B1 comparison under a uniform 878 semantic-class and public-pair distribution with replacement, conditional on a frozen split. This is NOT independently reviewed/frozen; no target/seed/evaluator activation and zero official ACTIVE-001 scientific scores.

## Gate F invented structural implementation — engineering-only receipt (2026-10-30)
[Receipt](runs/20261030-gate-f-invented-census.md) / [source](../../packages/active_feasibility/__init__.py) / [six synthetic-only tests](../../tests/test_active_feasibility.py). A fixture-only partition census found 85.00% F3 **class/pair-weighted opportunity prevalence** on existing invented seed 20261030, and 14.997% F1+F2 with no information opportunity. This is no evidence of held-out improvement; F4 adaptive two-query property remains unmeasured and the official split/seed/source/evaluator, N4096 methodological power, separate independent review and activation are still NOT_FROZEN. Keep zero actual scored ACTIVE-001 observations.
