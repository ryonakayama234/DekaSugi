# ACTIVE-001 PR2 — canonical split and replayable history engineering integration

id: ACTIVE-001-RUN-20261030-PR2-HISTORY
status: STAGED_FOR_DRAFT_PR_REVIEW_NOT_SCIENTIFIC_SCORING
updated: 2026-10-30
prior_head: d453ffac82f54029201ee73017940c42ed2a9cf2
pr: https://github.com/ryonakayama234/DekaSugi/pull/95

## Defect and falsifiable engineering hypothesis

At the preceding PR #95 exact-head independent review, two P1 items remained: an attacker could alter a QuerySession query pool and recompute only a helper digest, exposing evaluator-only inputs; and lossy compact answer history did not prove intermediate choice/receipt/terminal legality. Hypothesis: validating the complete canonical input split on EVERY public session entry, plus replaying every ordered question-answer prefix, rejects these local forgeries. This does not establish external source/oracle authenticity.

## Patch contract, modules and reproducibility

- Principal packages/active_learning/__init__.py changes QuerySession to active-query/2 with full ordered (QueryProposal, QueryAnswer) trace in the session commitment; recomputes the exact inquiry-world/1 28/64/64 split SHA using the complement of public and query IDs; checks seed-bound B1 / true argmax B2, each receipt, class transition and each terminal prefix, rejecting any continuation after terminal.
- New tests/test_active_learning_history_integrity.py contains eight invented-only adversarial tests: query/audit pool swap plus forged helper hash, public/query swap, bad answer receipt, B1 seed/policy trace change, missing trace and class vote tamper, after-budget continuation, after-identified continuation, and synthetic 25-target B1/B2 state transitions.
- Explicitly allowlisted the new test module in scripts/run_research_ci_v2_tests.py without broad unittest discovery; README, AGENTS, docs/INDEX, ARCH-001 Mermaid, ARCH-002 data flow, spec, plan, roadmap and this new run ledger are synchronized.
- Local checked artifact content SHA256 before staged integration: new active_learning Python module d611ab47fe9022f9b2b8eb5c8997e5790b74ede26789fe050aa2b5da7ad40db1; new history tests 6319b66c9716da2d11f7bf637c2c6c41471dbd53391e75ed768c0713c7e2c6ef. GitHub blobs are compared to the locally tested Git blob identities before any branch update.

## Pre-integration synthetic test evidence

The prior isolated Linux Python 3.13.5 reconstruction ran 5 original synthetic fixtures, 5 first-hardening integrity fixtures, and eight novel adversarial history tests: 18/18 PASS. Two additional test-only smoke fixtures produced 20/20 on that reconstruction; these extra two are NOT repository tests. Independently sourced scientific scores = **0**. This local observation is not the post-push exact-head safe CI, and does not validate source custody or hidden targets.

## Scientific and release constraints

The active-query/2 commitment changes the deterministic B1 random stream, so it is not serialized-compatible with earlier synthetic active-query/1 states. No real scored ACTIVE-001 results exist; no learned questioning policy, capability uplift, third-party source authenticity, private evaluator, or transfer outcome is established. The original OPPORTUNITY-001 TRAIN64, historical DEV/FINAL, OLD14/NEW9 source-locked bytes, old original CI workflow, and all historic scorers must remain unchanged.

The owner has supplied a screenshot displaying the historical Research verification workflow as manually disabled. The current repository is public and the successor uses free standard ubuntu-latest runner. The integrated branch must nevertheless pass its own exact-head safe CI and a new independent review (P0/P1/P2). Neither passing synthetic CI nor a screenshot alone authorizes the real scientific study. PR #95 remains draft and MUST NOT be merged directly to main before its PR #94 dependency is independently accepted and all branch/main integration gates hold.

## Post-integration receipt method

Record CI run number / exact head and independent reviewer result in the PR discussion after an actual run, avoiding a new source commit that would invalidate a previously checked head. Do not falsely rewrite this pre-integration snapshot as a future passing test.
