# OPPORTUNITY-002 PR3 — synthetic C-G2 evidence adapter engineering record

id: OPPORTUNITY-002-PR3-SYNTHETIC
updated: 2026-10-30
status: implementation_staged; CI_pending; independent_review_pending
phase: invented_synthetic_only
new_real_scored_tasks: 0
scoring_authorized: false

## Source and reproducibility
- Parent [Issue #91](https://github.com/ryonakayama234/DekaSugi/issues/91); baseline main `07e3cdbc2d4789658a460ed157bbfafbff811e6d`. New engineering branch `research/opportunity002-pr3-audit-normalizer`. Exact PR SHA / Actions run / observed test counts are **pending**, not fabricated.
- Test command: `python scripts/check_research_ci_v2.py && python scripts/check_docs.py && python scripts/run_research_ci_v2_tests.py` (Python 3.12; standard library; safe allowlist). Do not use whole-project `unittest discover`, historical generator/scorer or any private archive.
- Contract `opportunity2-audit-normalizer/1`, synthetic fixture values only, checksum pinned separately for each row, first solution replay, public and third audit independently reconstructed, strict trace/AST/meter fields, integrity hard stop and no mixed-valid estimates.
- In this phase synthetic third example is intentionally PUBLIC test data; it is never owner-private evaluator-only material. The artificial `toy_bias_v1` profile deliberately changes ordering to create a witness; `current_v1` is only independent synthetic grammar modeling. No inference about the actual frozen policy's unseen generalization, no claimed learning or skill promotion.
- The old source lock 9 files, EXP-0003A 14 files, original opportunity_actual normalizer, true one-shot TRAIN64 and old DEV/FINAL must remain unchanged. The GitHub CI itself cannot attest external private custody or the operational state of the inherited legacy workflow.

## Claims / limitations
- This entry is an **implementation-stage plan**, not an observed passing test. After exact-head CI, independently validated counts and review must be appended or linked, not silently claimed here.
- Proposed outcomes: `public_found_audit_correct`, `public_found_audit_incorrect`, `public_not_found`, `not_observed`, `integrity_invalid` and non-comparable pair state. Zero support => `not_estimable`. Unexpected evidence => whole-batch `invalid_stopped`.
- Author self-audit is not independent review. No official new experiment distribution, no numerical statistical-power claim and no real scoring activation.

[Plan](../plan.md) / [Spec](../../../docs/specs/OPPORTUNITY-002.md) / [ARCH-001](../../../docs/architecture/system.md) / [ARCH-002](../../../docs/architecture/contracts.md).
