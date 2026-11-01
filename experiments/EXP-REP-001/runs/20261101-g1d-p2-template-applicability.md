# G1-D review P2: inapplicable role-template fallback
id: EXP-REP-001-G1D-P2-20261101
status: DISCLOSED_ENGINEERING_CI_PASS; FORMAL_NOT_RUN; INDEPENDENT_REVIEW_PENDING
updated: 2026-11-01
tags: experiment, synthetic, code-review, budget
source_head: 4d8091a8c12f7de7528d3a3dbd3df191e2d8a40b
ci: https://github.com/ryonakayama234/DekaSugi/actions/runs/41315724074

## Corrected logic
Review found a learned six-role template on a four-object target was misclassified as a resource exhaustion and prematurely blocked bounded H2 fallback. A syntactically valid canonical motif requiring too many distinct roles now produces no template instantiations, distinct from malformed body or actual search cap exhaustion; B3 continues with remaining H2 search.

## Evidence
147 explicitly allowlisted synthetic tests including a regression for six-role Snapshot and four-object fork-world fallback PASSED in CI. The corrected B3 prediction equals strong B1 on that regression fixture. No original score or sealed source was modified, no formal DEV/FINAL, and independent current exact-head review has not yet signed off.
