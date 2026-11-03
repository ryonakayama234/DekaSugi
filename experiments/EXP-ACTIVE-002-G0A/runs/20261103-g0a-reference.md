# EXP-ACTIVE-002-G0A — second local reference cross-check, 2026-11-03

id: EXP-ACTIVE-002-G0A-REFERENCE-20261103
status: SYNTHETIC_ENGINEERING; LOCAL_9_OF_9_PASS; NOT_F0_SCIENCE
updated: 2026-11-03
tags: independent-reference, brute-force, negative-tests, local

## What was checked
After the initial eight synthetic tests and first code review, added a **second, structurally independent reference algorithm** in `tests/test_inquiry_opportunity_synthetic.py`. It does not call the production certifier's Bellman or terminal-payoff formula. Instead it explicitly enumerates:
1. Each first action and each public-next-state contingent second action or stop (all depth-2 policies) under lawful public-state masks.
2. Every length-0/1/2 nonadaptive action schedule, rejecting any schedule illegal for any latent law trajectory.
3. Every possible per-audit prediction label and abstention, directly adding +weight/-weight/0 rather than using the closed-form modal-payoff formula.

It compares reference raw optimal adaptive and strongest legal open-loop integer numerators with `packages.inquiry_opportunity.certify` on **18 deterministic artificial small tables** of 3 laws, 2 observed states, 2 actions, B=2, two heldout legal probes, variable legal masks, randomized deterministic transitions and positive nonuniform priors.

## Measured local result
- `python -m unittest discover -s tests -p test_inquiry_opportunity_synthetic.py -v` → **9/9 tests PASS** locally (including the new 18-case brute-force reference).
- Exact module Git blob `22f71b0bd45c167eee6445a296fbffa574b5f0ad` unchanged.
- Exact new test Git blob `fcb1e6875f5ee9f2ba822c93279d4b58b0897117`; matches locally executed bytes.
- Previous PR-head `51dd3dd58df31dc579b76d49ff83ae134641ff3d` CI [#41634766409](https://github.com/ryonakayama234/DekaSugi/actions/runs/41634766409) ran 120 safe synthetic tests and passed, **but that head precedes the new reference test**. The successor head's safe CI and independent code review must be checked anew.

## Scientific limit
The reference confirms the implementation on 18 **invented** 2-state tables, not independent causal mechanism families or formal inquiry opportunity prevalence, and not learner behavior. Original G0C/V4 negative/null records and sealed sources remain untouched. No source-power estimation or new performance score.
