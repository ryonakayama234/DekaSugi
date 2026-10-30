# ADR-0006 — ACTIVE-001 Stage I: structural feasibility before confirmatory utility

id: ADR-0006
status: proposed_decision_for_review; NOT_FROZEN; no_scoring_authority
updated: 2026-10-30
tags: architecture, methodology, active-learning, measurement, decision

## Context
The current `packages/inquiry_world` + `packages/active_learning` engine (merged PR #94/#95) can choose informative queries and update finite-domain hypotheses, but it has no independently scored Stage-I utility claim. Previous OPPORTUNITY-001 TRAIN64 was UNDERIDENTIFIED. The proposed N=512/+5pp design did not justify statistical power; max Gini on a uniform semantic version space is not the same objective as held-out decision accuracy. Existing B1 chooses uniformly even among zero-information questions, so a positive B2/B1 gap may be an avoidance-of-waste effect.

## Decision (proposed, not frozen)
1. Make **information opportunity, decision utility and economic cost distinct constructs**; measure bounded *within-episode epistemic adaptation*, not across-episode learner growth.
2. First build a **read-only exact structural partition audit** over public examples, not a scorer. F0–F3 are disjoint; F4 is a nested adaptive flag. Use semantic class/population weighting and preserve zero-advantage/degenerate cases.
3. Adopt proposed **4,096 independently drawn task units with replacement** over a **uniform 878-class** finite closed world, plus uniform public pairs under one future fixed input split. The inferential unit is the task; B1's five replicates and 64 evaluator inputs are nested, not clusters. There is **no new family-generalization claim**. Conventional task-level paired t CI primary, nominal N justified conservatively from bounded paired variance; independent review before freeze.
4. B2 versus the *existing* B1 is the only confirmatory scientific effect. B0 and a new future independently implemented informative-uniform B1+ are secondary mechanism diagnostics. Do not alter frozen active-query/2 semantics.
5. Future evaluator/Oracle owns target truth and holdouts behind process/interface separation; reproducible public source and SHA hashes are not secrecy or reviewer independence.
6. Use separate method/source-lock/evaluator/activation PR gates. Neither this ADR nor a green CI approves score execution.

## Alternatives
- N512 inherited by default: rejected as insufficiently justified.
- All 331,884 possible class/public-pair contexts with full scoring: attractive exact finite-model evidence, but computation and random-stream expectation unresolved; reserve as future model checking, no external validity.
- Hierarchical family bootstrap without hierarchical generation: rejected, pseudo-clustering/invalid population.
- New learned query policy or generalized DSL first: rejected for present *causal identification* scope, retained as future Stage II/III.
- B2 versus B1 alone as mechanism proof: rejected; preregister zero-Gini selection analysis and B1+ secondary diagnostic.

## Consequences and limitations
N4096 is a proposal, not an observed-power result or a sample-size freeze; no fixed positive practical utility guaranteed. A finite deterministic world can support a precise **conditional synthetic** capability claim, not natural language, new concepts or domain transfer. If information opportunity is structurally absent or cost infeasible, terminate before official target exposure and issue a new protocol version.

## Implementation boundary
**Primary module:** future independent `packages/active_evaluation` / scientific methodology. **New proposed auxiliary:** `packages/active_feasibility` read-only. **Protected unchanged:** `packages/inquiry_world`, `packages/active_learning`, legacy scorers, historic source locks/workflows, original evidence. No code changes under this ADR.

Detailed method: [Stage I design v2](../../../experiments/ACTIVE-001/method-v2-decision-draft.md). Architecture: [ARCH-001](../system.md); contracts: [ARCH-002](../contracts.md); records: [unscored review ledger](../../../experiments/ACTIVE-001/runs/20261030-design-v2-review-ledger.md).
