# ACTIVE-001 — preregistration feasibility proposal receipt (no run)

id: ACTIVE-001-PR3-FEASIBILITY-RECEIPT
status: planned; documentation_only; no_scored_observations
updated: 2026-10-30
tags: run, methodology, evidence, identifiability, power

## Provenance
- Basis: Issue #96 and main after PR #94/#95, SHA \`d9ad80fc844a09c312f6434d20d0d17fdcac4109\`.
- New work: candidate method and risks before research power/source freeze. No learner/evaluator code or historical source modifications in this task.
- Confirmatory task evaluations: **0**; independent Stage-I evaluation: **not implemented**.
- Local empirical runs by this documentation task: **none**. No claim of fresh synthetic engine tests or completed CI.
- Linked proposal: [method candidate](../method-v1-candidate.md); [existing draft](../plan.md).

## Design-only reasoning receipt, NOT measurement
- 512 independent task-level samples have nominal 95% normal half-width \`1.96*sigma_D/sqrt(512)\`; with unknown \`sigma_D\`, no precision guarantee. 64 withheld inputs and five B1 replicates are not independent sample multipliers.
- At effect \`delta=0.05\`, two-sided alpha .05, 80% nominal paired-normal power, \`N ~ 3140.5 * sigma_D^2\`. These are analytical hypothetical inputs, not estimated real-world variance. No sample size fixed.
- Semantic-class information gain and downstream held-out accuracy have distinct objectives; some structures may allow zero useful information, and target distribution can differ from uniform semantic-class weighting.

## Reviewer checklist, all pending
- [ ] Structural opportunity strata and full-population denominator independently justified.
- [ ] Target family definition, sampling distribution, replacement rules and inferential cluster determined.
- [ ] Sample-size/power/coverage independently calculated without true scored labels.
- [ ] Pre-exposure split/seed/source/target ownership and independent evaluator trust gates specified.
- [ ] B1 five repetitions correctly nested; all negative, invalid and missing cases specified.
- [ ] AGENTS, INDEX, ARCH-001/002 and plan maintained together; safe docs check and exact-head independent review reported when actually executed.
- [ ] Separate evaluator/activation decision; historical workflow disablement checked independently.

This file is a **design ledger**, not an immutable run result or evidence of intelligence gain.
