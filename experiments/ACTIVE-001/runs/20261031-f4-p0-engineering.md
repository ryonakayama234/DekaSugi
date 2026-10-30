# ACTIVE-001 P0 F4 — bounded invented-toy engineering receipt

id: ACTIVE-001-F4-P0-RUN
status: source_committed; exact_head_safe_CI_and_review_to_be_verified
updated: 2026-10-31
tags: active-learning, synthetic, identification, no-scoring

## Evidence scope
Stack: F4 P0 branch based on Gate-F PR #98 head \`667200f49444c029ceb8cf5ee78453f05595cac8\`, which is stacked on method draft PR #97. P0 adds \`packages/active_feasibility/f4.py\` and five invented-only tests inside pre-allowlisted \`tests/test_active_feasibility.py\`. No new target selection, no Oracle answers, no evaluator labels, no historical scorer; original Gate-F \`census_fixture()\` report and hash must be invariant.

## Acceptance checks
1. Strict toy case: A=4 and N=2; stable first/second tie-breaking; F4=True.
2. Independent brute-force reference enumerates all fixed pairs and all response-contingent second-question assignments for several small worlds; compare exact integers, not approximate Gini.
3. Fully indistinguishable 3-class context gives A=N=0/F4=False; singleton gives A=N=1/F4=False.
4. Resource overrun produces \`not_computed/resource_budget\` and null (never False) identification counts.
5. Exact types, equal row widths, 2..64 questions, 1..276 classes, protected work budget.
6. Original synthetic Gate-F F0–F3 census checksum/counts and F4 status unchanged. Source lock and safe-doc gate pass.
7. Exact-head CI and \`@codex review\` results are established via the linked PR once actually observed; don't infer review completion from source receipt.

## Claim limitations
**This is a proposal and tiny-world engineering reference, not a full F4 census or a scored trial.** F4 real full 91,367-context frequency remains \`NOT_COMPUTED\`; CPU cost awaits P2; Stage-I H1 remains unfrozen; independent evaluator absent and no source/seed activation. Official newly scored ACTIVE-001 tasks: **0**. Distinguish code-review coverage from independent method or statistical certification.

[Operational definition](../f4-operational-definition.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).
