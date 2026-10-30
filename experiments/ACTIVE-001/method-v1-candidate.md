# ACTIVE-001 — pre-scoring feasibility and scientific-method candidate

id: ACTIVE-001-METHOD-CANDIDATE-01
status: proposed_unfrozen; design_only; no_scoring_authority
updated: 2026-10-30
tags: active-learning, identifiability, estimand, power, preregistration

Parent: [Issue #96](https://github.com/ryonakayama234/DekaSugi/issues/96) / [ACTIVE-001 plan](plan.md).
This is a **new versioned alternative**, not a replacement for the existing draft plan and NOT a frozen preregistration.

## Decision to make before N, seeds or activation

Question: under what task distributions does selecting an informative oracle question change **held-out decision accuracy**, rather than merely reduce hypothesis-set cardinality?

Already integrated: PR #94 design and PR #95 synthetic-only active inquiry engine, main SHA `d9ad80fc844a09c312f6434d20d0d17fdcac4109`. The engine's invented finite world (156 inputs, 4,681 syntax programs, 878 finite-domain semantic classes) is a calibrated **engineering reference**, not evidence of predictive improvement, learned question policy, skill invention or transfer. Scored ACTIVE-001 observations remain **zero**.

## Candidate target construct and competing explanations

Stage I construct: within-episode **epistemic adaptation** from up to two selected oracle responses. Primary claim may at most concern the specified fixed InquiryWorld task distribution.

Competing explanations to distinguish:
1. **No actionable question:** public observations already identify one class, or all allowed questions are nondiscriminatory.
2. **Information without utility:** questions reduce `|H|` but fail to alter the final prediction on evaluator-only inputs; a max-Gini query optimizes class disagreement, not necessarily held-out accuracy.
3. **Policy mismatch:** B2's uniform weighting over semantic classes differs from the true target sampling law; B1 can outperform B2.
4. **Budget limitation:** useful distinguishing questions exist, but the fixed two-query policy cannot reach them.
5. **Integrity or representation limitation:** source/label leakage, unsupported target, false identification or evaluator error invalidates the comparison; in the closed-world target distribution, unsupported targets must not be silently relabelled as valid.

Do not infer Stage II learning-across-episodes or Stage III cross-domain transfer from Stage I results.

## Prospective structural feasibility audit (DESIGN-ONLY)

Without sampling target labels or opening scored data, inspect the **permitted learner-facing** finite catalog, public pair and query input IDs and classify each hypothetical public context:
- F0: `|H0|=0` model-inconsistent; error condition.
- F1: `|H0|=1` already identifiable, zero query opportunity.
- F2: `|H0|>1`, but all remaining allowed query inputs have zero disagreement: query-unidentifiable in this pool.
- F3: `|H0|>1` with at least one informative question: structural information opportunity, **not** proof of positive task utility.
- F4: two-step identification requires adaptive contingent branching; measure reachable branch distinctions within budget as a *secondary structural bound*, not an observed accuracy result.

Classify coverage of public contexts under proposed public-example generator. Do not use the official target/holdout labels, existing historic train/DEV/FINAL, genuine oracle responses, or a future confirmation sample to choose favorable thresholds. For feasibility calculations, use a separately labelled invented design population and preserve its full source and limitations. A positive F3 prevalence does not establish B2 advantage.

Primary population must include F1/F2 and every valid zero-gain task. F3-only effects, if prespecified, are **secondary conditional** claims, with their denominator frozen before scoring.

## Candidate paired scientific estimand — NOT YET FIXED

For genuinely independent sampled task `i` let `a_i(B2)` be the fraction of 64 evaluator-only inputs with exact-match predictions after at most two B2 queries. Let `a_i(B1,r)` for `r=1..5` be analogous accuracy for five frozen B1 random-query replicates on the **same task**.

`D_i = a_i(B2) - (1/5) * sum_r a_i(B1,r)`
`Delta = E_population[D_i]`

Every `D_i` is in [-1,1]. This measures policy *within-task* advantage. The 64 held-out inputs and 5 B1 replicates are repeated measurements, **not additional independent tasks**. B0 is secondary. Freeze target family taxonomy, sampling weights, task ID, target/public-context independence, and whether family is a stratum, an inferential cluster, or both. Do not claim that merely drawing a new random seed from the same finite target class is out-of-family generalization.

Predefine missingness separately from score: absent/rejected oracle or audit, chronology/source mismatch, illegal query, inconsistent H, non-attested evaluation or leak => validity status and STOP for confirmatory analysis until an independently reviewed handling rule exists; never silently convert invalid evidence to zero accuracy.

## Power and precision: why N=512 is only a placeholder

Illustrative *independent task-level* paired-normal planning formula at two-sided alpha .05, power .80, absolute effect `delta=0.05`:
`N ~ (1.96 + 0.842)^2 * sigma_D^2 / 0.05^2`.
If task-level paired SD is 0.20 / 0.30 / 0.40 / 0.50, nominal N is approximately 126 / 283 / 503 / 786; sigma=1.00 requires ~3141. These are **sensitivity scenarios, not observed SD or valid finalized N**. Finite classes, family reuse, unequal weights, effective clusters, discreteness, missingness and a confidence lower-bound decision rule may require more. A conventional cluster-randomized-trial design-effect formula must not be mechanically pasted onto this paired task design; first specify the dependence model and inferential unit.

An independent method review must select an exact family-aware interval/power procedure (for example, predeclared resampling at the correct independent cluster unit with coverage verified on invented fixtures), handling of 5 within-task B1 replicates, strata weights, alpha, precision, family counts, non-informative tasks, and a no-optional-stopping rule. If no defensible N achieves precision within budget, classify **UNDERPOWERED** and redesign **before** score exposure. '+5pp and 95% CI lower >0' remain proposed rather than accepted gates.

## Evaluation separation and source-first lock

Future `packages/active_evaluation` (not implemented) alone may hold target ID, target-family metadata, target generator seed, oracle truth and 64 withheld labels. The active learner receives only two public examples, allowed unlabelled query IDs, current hypothesis signature and validated response to its one proposed query. Publicly visible source constants are **not** secrecy; process isolation and audited interface restrictions are required.

Prior to any scored run freeze independently:
- exact git tree/source blobs and interpreter semantics; 156-input universe and 28/64/64 split algorithm + digest;
- independent target distribution/family map and replacement policy; exactly two public examples and five B1 streams, seed origin/commitments;
- fixed B0/B1/B2 tie-break and terminal rules, max two questions, candidate grammar and cost-meter definitions, amortized preprocessing horizon;
- exact task IDs, estimand, interval/power algorithm, null/negative/missing handling and stop conditions; verifier ownership and immutable raw/aggregate receipt schema.

No real scoring, preregistration approval or evaluator creation is authorized by this document or its merge. Gate order: method review -> source/seed freeze -> separate evaluator PR and adversarial tests -> exact-head independent review -> explicit one-shot activation. Historic OPPORTUNITY-001 TRAIN64, EXP-0003A DEV/FINAL, EXP-0002B FINAL112 and original disabled workflow are untouched.

## Future research tracks — not part of current task

- Stage II / Wake–Sleep: learn query selection *across episodes* using TRAIN-only sanitized transcripts; compare frozen pre/post policies on disjoint new tasks.
- Stage III / action abstraction: encode a query as goal, discriminated relation, expected answer partitions, cost and effect, then test whether it transfers through distinct domain adapters. This is a hypothesis about reusable **intellectual actions**, not a proven common universal representation.
- Cooperative dialogue: the other agent/human may also update their state; a bilateral protocol will require distinct observations/utility and consent/verification, not only a single oracle output.

## Decision state

`PROPOSED`. Approval requires independent methodological review and numeric feasibility justification. A negative feasibility finding or inadequately powered design is a successful scientific stop signal, not a failed software test.

[Architecture](../../docs/architecture/system.md) / [Data contract](../../docs/architecture/contracts.md) / [Unscored design ledger](runs/20261030-pr3-feasibility-proposal.md).
