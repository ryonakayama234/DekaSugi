# EXP-COEV-001 — Counterexample-driven learning preregistration draft

id: EXP-COEV-001-PLAN
status: draft_v0; NOT_FROZEN; NO_ACTIVATION; no_scoring_authority
updated: 2026-10-31
tags: preregistration, persistent-learning, active-inquiry, evidence

## Hypothesis
H1: After identical sealed typed-grammar access, C2 trained using information-seeking counterexamples yields positive and practically material task-level heldout accuracy gain vs C0 no-learning fixed grammar. Proposed Δ>=0.10 and conservative 95% bounded-IID lower>0. This is a **testable hypothesis**, not an anticipated finding. H2 C2-C1 isolates training query strategy; H3 C4-C3 isolates inference query strategy; H4 total costs; H5 later separate transfer study. Exclude model claims not supported by this finite string domain.

## Population and schedule
Initially TRAIN=256, DEV=128, FINAL=2048 *tasks*, 64 distinct hidden audit inputs per task, two public pairs, max 2 Oracle queries per requested arm. All arms task-paired. Input universe: 156 bounded strings, split into public28/query64/audit64 with independently committed source/seed and no content overlap. Training and evaluation target semantic classes disjoint; validate sufficient independent support and predeclare class/family mix/weights. No semantic class leakage through generated training, Dream data, feature IDs or snapshots. Confirm distribution-level opportunity and CPU costs on design-only synthetic test cases **before** committing formal N.

## Arms
- C0 G1 fixed DSL, zero TRAIN, zero test query.
- C1 TRAIN random <=2 queries, learned concepts/selection policy, zero test query.
- C2 TRAIN max disagreement <=2 queries, learned concepts/policy, zero test query.
- C3 frozen C2, random <=2 test queries, five within-task RNG replicates.
- C4 frozen C2, max disagreement <=2 test queries.
- Structural negative control same #uninformed skills. Frozen exact max AST/expanded node and candidate budgets on all arms; query arms have separately reported Oracle expense.

## Metrics
Primary task i: D_i=mean_{64 hidden inputs}1[C2(x)=f_i(x)] - mean_{64}1[C0(x)=f_i(x)] (includes unsolved/invalid handling predeclared). Average D_i; two-sided bounded-IID 95% interval with radius sqrt(2*ln(40)/N) if independent target sampling established. Lower>0 and point >=.10 required jointly. Cost vectors: per task exact match, solved@budget, primitive invocations, expansions, candidate count, learned snapshot sizes, question count, inferred information gain and evaluator-only CPU/elapsed/RSS. Report zero-opportunity subsets and failures separately; do not select on final outcomes. C3 repeats averaged per task, not independent samples.

## Failure / non-estimability
Prespecify excluded only corrupted source/evaluator/protocol records; do not exclude hard tasks or unfavorable accuracy. Failed-to-solve is valid negative. Missing truth, unauthenticated response, train-test semantic overlap, invalid sequence, verifier forgery, unavailable private data, source freeze mismatch or inaccessible independent custodian -> STOP/NOT_ESTIMABLE. Sensitivity analysis documents omissions without replacement/rescoring.

## Stage and scientific boundary
1. PR1 docs-only decision, architecture/contract/index/AGENTS/ADR/run ledger (no scoring).
2. PR2 G1 isolated interpreter, no external IO, exact semantics / canonical classes / deterministic negative invented fixtures, resource calibration; no official target outcome.
3. PR3 TRAIN-only actual Wake/Sleep + typed templates + contextual policy + snapshots and train receipts; do not consult DEV/FINAL.
4. PR4 separate-process custody/evaluator, source/seed/method/power reviewed and frozen; full resource budget; adversarial replay; independent reviewer.
5. Fresh confirmatory FINAL one-shot only following a **separate explicit activation** under immutable approved method; independent raw artifact recalc and acceptance report. No old scorer workflow reenable or old EXP runs. DEV is controlled engineering diagnostic, not adaptive hyperparameter fitting against FINAL.
6. Adoption ADR separately; H5 new versioned protocol and holdout. Actual numerical results may be negative and must be retained.

## Acceptance
Design: mechanisms, alternative hypotheses, comparison fairness, no claimed autonomous grammar creation, resource/power caveats, independent trust boundary. Engineering: synthetic tests and safe CI, strict schema/typed AST, deterministic replay, no historic source changes, docs check, new receipt. Scientific: prerequisite methodological and custody gates, independent audit, H1 numerical criteria frozen before any FINAL labels. Abort if insufficient independent semantic target classes / inappropriate IID; version a redesigned study rather than quietly relax criterion.

[Spec](../../docs/specs/EXP-COEV-001.md) / [run index](runs/README.md) / [ADR](../../docs/architecture/decisions/ADR-0006-coev-learned-concepts.md) / [Issue #106](https://github.com/ryonakayama234/DekaSugi/issues/106).

## Feasibility amendment to the draft (pre-outcome, 2026-10-31)
Structural synthetic enumeration (not official scoring) found **895 distinct G1 behaviors** from 3,741 syntax programs. The original notion of 2,048 unique unseen target classes is impossible. FINAL2048 means 2,048 independent *task draws with replacement* from a finite held-out **class pool** disjoint from TRAIN/DEV class pools; repeated target classes are reported. The uncertainty interval targets repeated independent task draws conditional on fixed class-pool weights and frozen trained snapshot. It is NOT a claim about all possible programs, nor 2,048 unique unknown functions. Freeze exact class-level split, weights, public-example resampling, class-family concentration and finite-domain identification opportunities after a separate resource/power review, before accessing any real scored target. This correction precedes any real learning/score. Synthetic engineering tests=6/6 locally; independent CI/review not yet available.

## Binding pre-TRAIN scientific validity correction v0.2 (Codex P1; 2026-10-31)

**Supersedes every earlier stage ordering that put formal TRAIN before source/method/seed freeze.** Local PR3's publicly seeded 256-task `simulate_train(20261031)` is **engineering training on invented known fixtures**, not the registered scientific TRAIN256 cohort. It demonstrates code that truly changes candidate concepts and policy state, but it must never be used to select confirmatory method, source split/weights, sample size, seed, effect thresholds or subsequent formal snapshots.

New mandatory order: **(0) research design + pretrial finite-world feasibility; (1) invented-only G1 and learning algorithm prototype; (2) independently reviewed semantic-class pool allocation, IID-with-replacement task law, outcome analysis, multiplicity/power, resource budget, fresh confidential seed roots, target/Oracle custodian, source/tree hashes and verified historic workflow disablement — FROZEN BEFORE ANY REAL TRAIN; (3) source-locked fresh real TRAIN256 using only the separate reviewed TRAIN custodian, with genuine selected answer receipts and TRAIN-only reward; (4) freeze trained library and contextual policy snapshot before any real DEV; (5) independent DEV diagnostic / evaluator verification under frozen rules, no policy retuning; (6) separately activated new one-shot FINAL2048 with original evidence preservation, audit and negative results; (7) independent L4 preregistration if warranted.** If the proposed N/target distribution is infeasible or the review fails, stop and version a new plan **before** formal TRAIN; do not retrofit the publicly observed PR3 pilot to the formal population. No real TRAIN/DEV/FINAL or formal H1 score is authorized by PR1-PR3.

Reference: [Issue #106](https://github.com/ryonakayama234/DekaSugi/issues/106), [PR #107](https://github.com/ryonakayama234/DekaSugi/pull/107) method-review P1.
## PR2 checkpoint (unscored)
G1 source/typed-execute/finite catalog / integrity tests staged with `test_concept_world.py` in safe synthetic CI allowlist. Exact-head CI and independent review required, no target trial/holdout and no H1 outcome. New parent #106; stacked implementation PR2 is not a method/source/seed freeze or an official score trigger.

## PR3 TRAIN engineering checkpoint (2026-10-31)
Actual deterministic invented-world TRAIN256, same target/public pairs, query cap 2, 105 random vs 231 active binary verified class-ID matches. Approximate MDL template induction yields 8 candidates per arm; 64-bucket contextual frequencies are frozen into local snapshots. These data are training observations and no new unseen target class score, not H1 evidence. Pinned local receipt digests appear in [run](runs/20261031-pr3-local-train-only.md). No independent evaluator or official FINAL/DEV activation has been authorized; preserve exact source, run local/safe CI first, and review negative cases.
