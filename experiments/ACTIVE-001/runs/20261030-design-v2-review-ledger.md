# ACTIVE-001 design-v2 — unscored methodology review ledger

id: ACTIVE-001-DESIGN-V2-REVIEW-LEDGER
status: design_only; no_scored_observations; independent_method_review_pending
updated: 2026-10-30
tags: experiment, planning, preregistration, evidence, audit

## Source basis
Main at `d9ad80fc844a09c312f6434d20d0d17fdcac4109` (PR #94/#95 integrated engineering reference). Existing draft PR #97 is a documentation-only design review. [Method v2](../method-v2-decision-draft.md), [ADR-0006](../../../docs/architecture/decisions/ADR-0006-active001-scientific-design.md).

## Evidence status
- New actual scored ACTIVE-001 trials: **ZERO**.
- New actual task-generated targets / oracle labels / 64 private evaluations: **NONE**.
- Historical locked EXP-0003A / OPPORTUNITY-001 / EXP-0002B scoring: **NOT TOUCHED**.
- Current document calculates **planning bounds only**; `n=4096` and split/seed/analysis are NOT independently frozen.
- 878 semantic classes / 4,681 syntax programs are **previously recorded synthetic engineering measurements**, not remeasured in this doc.
- `878*C(28,2)=331884` is a mathematical count of potential finite target/public-pair combinations, not independent experiments.
- Variance bound `Var(D)<=1`, N4096 normal-approx CI worst halfwidth `0.030625`, and nominal positive detection power ≈0.89 at delta=.05, sigma=1: **analytic planning**, not actual observed precision, total cost or scientifically validated power.

## Must independently verify before freeze (ALL pending)
- [ ] Review that the uniform independent sampling-with-replacement task law and inferential unit match the intended limited claim.
- [ ] Confirm N4096 normal-approx power/coverage, practical-size criterion separation, missingness and feasible CPU budgets.
- [ ] Review and implement **read-only Gate F only** on invented/symbolic public-context partitions; cross-check weights and F0–F3/F4 semantics independently. No official heldout accuracy calculations.
- [ ] Verify split generation, secret entropy/commitment, root/PRF stream semantics and evaluator-only truth boundary in an independent PR.
- [ ] Verify the proposal B1+ diagnostic is separate from the existing uniform random baseline.
- [ ] Capture exact-head safe CI results and exact-head independent *scientific-method* review; source lock + evaluator require separate PR.
- [ ] Verify original legacy workflow disabled via independent owner setting, not inferred from docs.
- [ ] Explicit one-shot activation approval; zero results until then.

## Negative-case reporting
No eligibility => UNDERIDENTIFIED; <5% eligibility => proposed 5pp practical effect impossible; CPU budget not feasible => UNAFFORDABLE; method or source trust incomplete => NOT_READY; leak/forgery/invalid state => STOP. Record failures without opening old or official new scored data.

**Decision status:** refined proposal for user agreement, NOT an accepted preregistration.
