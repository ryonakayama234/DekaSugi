# EXP-REP-005 G0b V3 — preregistration candidate / execution protocol

id: EXP-REP-005-G0B-PLAN-V3
status: draft_method_not_frozen_not_run
updated: 2026-11-02
tags: experiment, feasibility, representation, active-inquiry, preregistration

## Hypothesis
H-WORLD: a safe bounded causal grammar can produce meaning-distinct, role-nonisomorphic and generator-ancestry-disjoint families with independently checkable intervention and identifiability certificates. H-OPPORTUNITY: some public reachable histories have a provable positive action-selection/information-value gap that can later test learned causal concept activation. H-LIMIT: other families are genuinely budget-8 UNID, outside Hplus_G, or stochastic/invalid, and their correct diagnosis matters as much as positive cases. H-NULL: the grammar may fail to produce a rich independent universe or useful opportunity; then STOP, not quota-filling.

## Pre-implementation contract
Read [V3 decision](../../docs/specs/EXP-REP-005-G0B-DECISION-V3.md) and [ADR](../../docs/architecture/decisions/ADR-0006-causal-world-laboratory.md). Baseline pilot 4 public Boolean objects, 12 legal unit-paid actions, initial 0000, no free reset, B=8, lag<=2, synchronous effects, immutable public action chronology; full interpreter and metagrammar/operator precedence must be enumerated and independently reviewed before claiming G0b certification. 6 motif sources are exploratory only. CPU/memory/search-node ceilings recorded and deterministic STOP states returned. H0_all counterexample proof is not H0_G grammar membership. H0_G subset Hplus_G by explicit typed production inclusion.

## Work sequence
1. Inventory exact source-locked G0a #147 and the unresolved independent review P2. Selectively port only audited methods into an isolated main-based code PR if needed. Do not alter historical sealed scoring entrypoints.
2. Implement typed AST serialization, interpreter, explicit source ancestry and reproducible public-only WorldInterface. Verify ordering of simultaneous effects and lag history.
3. Compute total defined semantics and reachable public semantics separately. Alias reject, canonicalize 24 permutations, normalize typed causal hypergraph and group by ancestor; compare against independently authored oracle/metamorphic fixture.
4. Build exhaustive adaptive worst-case identification for fixed C and B=8, returning ID / UNID / NOT_CERTIFIED with explored branches; separately certify eventual distinguishing witness versus observational alias. No budget-exhausted false UNID.
5. Certify conditional-action opportunity from the same public reachable prefix, matched prior, legal action alphabet, state/history and horizon. Report positive, zero, and NOT_CERTIFIED for all candidates.
6. Construct a feasibility census of actual families by two independent axes, enumerate M2/M3 safety groups separately, present observed cells and source-overlap matrix; do not force equal quotas.
7. Simulate statistical power at family level with assumed effects/variance, state assumptions and sensitivity. Propose reviewed V4 split/frozen experiment ONLY if construction and opportunity gates pass; otherwise archive STOP and exact upper/attained counts.

## Metrics
Primary engineering: #syntactic candidates, #distinct total semantics, #reachable distinct, #role orbits, #independent certificate families, #shared source ancestors, distribution across M0/M1 x ID/UNID, #M2/M3 controls, #eligible legal public prefixes, #positive inquiry opportunities, #zero and #NOT_CERTIFIED.
Secondary engineering: proof branch nodes, finite semantic universe size, witness length, provenance/hash mismatches caught, CPU/wall, peak RSS if measured, timeout and memory-limit incidence. Every quantity requires numerator, denominator, semantics version, source SHA and run artifact digest.
Later SCIENTIFIC measures after new reviewed plan ONLY: paired per-family signed utility vs strongest fixed control, prediction accuracy, abstention, paid actions, primitive dispatches, compute, and TRAIN amortization. Do not print scientific score from G0b code.

## Acceptance
- [ ] Complete typed semantic/operator tables and all finite bounds; H0_all vs H0_G deliberately separated.
- [ ] Independent witness/semantics/role/ancestry cross-check and adversarial alias, unreachable-history, invalid/noisy, type-forgery and branch-budget tests pass.
- [ ] Certification never treats syntactic names, object permutations or parent-shared worlds as independent families.
- [ ] I(C,s0,A,8) certificates include ALL truthful answer branches and precise candidate class; UNID proof complete, otherwise NOT_CERTIFIED.
- [ ] Opportunity certificates have matched comparator and legal public-prefix witness; no hidden truth read through learner API.
- [ ] Explicit result: VERIFIED FEASIBLE, or G0B_STOP with actual family counts and unresolved uncertainties; no implicit quota change.
- [ ] Complete plan/architecture/data contract/AGENTS/INDEX/run synchronization with tests and exact-head independent review.
- [ ] No paid TRAIN, DEV/EVAL score, snapshot promotion, historical workflow reactivation or old holdout reuse in G0b.

## Explicit staged boundaries
THIS docs PR: design-only, 0 experiments, 0 learning, 0 scoring. NEXT substantive unit if approved: G0b-A generation/certification/opportunity engine plus synthetic self-tests and full receipts, NOT G3. G0b-B distribution/power/method freeze only on engineering success. G1–G6 are contingent successors, not included in initial implementation authorization. [Design-only receipt](runs/20261102-v3-design-not-run.md).

## Pilot semantics / ceilings amendment V3.1
The exact pilot semantics in [V3.1 decision appendix](../../docs/specs/EXP-REP-005-G0B-DECISION-V3.md) are normative: world=(four bits,last two public actions); set(i,b) base writes bit i, pulse(i) base no-op; activation on current or previous lag-1/2 pulse(source); guard at pre-action state/history; zero/two conjuncts of current-bit or previous-action equality; <=2 unordered typed source!=target edges; activated effects XOR target bits simultaneously. 16 x (1+12+144) x 12 = 30,144 total typed outcome cells, plus separately the reachable certificate. All 24 renamings cover state/history/action together. H0_G is lag0/current-bit subgrammar; Hplus_G is exact supergrammar. This is pilot scope and may fail G0b richness.

Initial proposed fail-closed engineering ceilings: 200,000 raw candidates per census pass, 250,000 memoized adaptive proof nodes per C proof, 120 seconds per certification job, 2 GiB peak memory; stop with exact status NOT_CERTIFIED if incomplete and do not claim grammar exhaustion, independent-family upper bound, ID/UNID, or 80 feasibility from a partial search. These resource ceilings require pre-code independent review. Cross-check all typed cells with an independently authored reference, verify set/XOR conflict ordering and parity cancellation, last-two lag boundary and public reachable paths. NO learner, no new scoring in this plan.

## Review-driven classification and opportunity proof correction
Review of early V3 PR head found two methodological bugs, fixed before implementation: (1) M1 covers every law inside Hplus_G but outside H0_G even when it happens to be memoryless, and M2 requires nonmembership in Hplus_G; never infer H0_all temporal dependence from M1. (2) Positive opportunity requires a feasible legal policy witness whose achieved expected utility exceeds the baseline, or lower-bound(candidate)>upper-bound(baseline), under maximization; mere upper-bound(optimum)>baseline is NOT sufficient. To prove no opportunity, upper-bound(optimum)<=lower-bound(baseline). If not certified, report NOT_CERTIFIED. Bayes-risk minimization reverses all inequalities. Assert these directions in negative fixtures including loose bounds.
