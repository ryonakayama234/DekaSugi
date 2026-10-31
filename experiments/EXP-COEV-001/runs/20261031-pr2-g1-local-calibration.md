# EXP-COEV-001 PR2 — G1 invented-world structural calibration

id: EXP-COEV-001-G1-PR2-CAL
status: engineering_local_only; no_scoring_authority; CI_UNVERIFIED
updated: 2026-10-31
tags: invented-fixture, grammar, semantics, negative-test

## Source/measurement
This PR provides standalone typed pure Python in `packages/concept_world`; it does NOT import any historical data or scorer and never looks up test target truth. A local Python 3 implementation of the same six unary operations, two predicates and 156-domain grammar found 3,741 syntax candidates; **895** unique finite-domain behavior signatures, **866** with conditional canonical representatives, 29 plain. Results are structural enumeration, not new scientific target accuracy, learning, score or transfer.

## Local engineering test evidence
Six synthetic unittest cases passed in isolated local workspace, covering enumeration, pure semantics, invalid AST/type refusal, 28/64/64 split disjointness, stable catalog digest, integer Gini argmax and forged/duplicate query IDs. Connector-staged source must receive separate exact-head GitHub CI and independent review: this draft does **not** claim those passed. Audit official source SHA after code reaches GitHub; no FINAL ever invoked.

## Feasibility blocker
FINAL2048 cannot mean 2,048 distinct target classes. Future tasks must be IID draws *with replacement* from an independently frozen semantic-class holdout pool, disjoint from TRAIN and DEV class pools, using fresh independently chosen public pairs. Sampling independence/power under repeated target identity must be independently reviewed before genuine scoring. The existence of 895 classes is not a successful learner.
