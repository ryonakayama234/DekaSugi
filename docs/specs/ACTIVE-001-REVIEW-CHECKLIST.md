# ACTIVE-001 — independent review checklist

id: ACTIVE-001-REVIEW
status: proposed; not_completed
updated: 2026-10-30
tags: active-learning, review, preregistration, security

## Science validity
- [ ] Correct construct and estimand: Stage I same-task acquisition vs Stage II across-task learning.
- [ ] Finite input universe size and 28/64/64 disjoint pool algorithm independently verified.
- [ ] Program semantics, enumeration order and per-world signature uniqueness independently checked; no accidental duplicate weighting or target-label screening.
- [ ] 512 tasks, balancing, family clusters and split seeds are fixed before labels; power/precision and underidentification support independently assessed.
- [ ] B0/B1/B2 same budget and same stopping policy, B1 replicate weighting, deterministic tie breaks, CPU and labels costs declared.
- [ ] 95% CI procedure and direction/failure definitions frozen, no post-hoc threshold or sample size change.

## Trusted dataflow and engineering
- [ ] No evaluator target ID, seed, family, withheld labels/answers or audit verdict in learner input or returned episode.
- [ ] Synthetic calibration covers duplicates, invalid query, repeated queries, contradictory trusted answers, no informative question, limited budget, forged provenance, missing and malformed records.
- [ ] No arbitrary code, dynamic executable imports, externally supplied Registry semantics, legacy scorer/generator/dev/final invocation or old-workflow changes.
- [ ] Source locking, exact-head CI, original workflow disabled control-plane verification, separate independent review of source and methodology; self-review is not independent acceptance.
- [ ] Cross-link AGENTS, INDEX, ARCH-001/002, ADR, spec, preregistration and immutable ledger for **each** PR.

No checklist completion is asserted merely by creating this file.

[Plan](../../experiments/ACTIVE-001/plan.md) / [spec](ACTIVE-001.md) / [Issue #93](https://github.com/ryonakayama234/DekaSugi/issues/93).
