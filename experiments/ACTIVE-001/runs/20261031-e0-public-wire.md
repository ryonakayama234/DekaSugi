# ACTIVE-001 E0 — invented-only public wire/no-leak engineering receipt

id: ACTIVE-001-E0-PUBLIC-WIRE-RECEIPT
status: implementation_committed; exact_head_safe_ci_and_review_to_verify
updated: 2026-10-31
tags: active-learning, security-boundary, negative-test, synthetic, no-scoring

## Scope

New strict frames \`packages.active_custody_boundary\` and \`tests/test_active_custody_boundary.py\`. Branch \`research/active001-e0-public-wire-preflight\` stacked on corrected P3 PR #103 head \`0912ba63ca706a339e36c20c4573d41d11783d71\`, not on a scored evaluator. No hidden truth/imports, official root/seed/sample, historical scored data, original source lock or workflow changes.

## Test cases

- Public task view includes exactly seven public keys; fabricated secret fields \`target_id\`, \`audit_labels\`, \`seed_root\`, \`future_answers\`, \`audit_ids\` never serialize or parse when injected.
- Canonical input split commitment reconstructs the 64-ID auditor complement **without label access**. Reject malformed 28/64 pool lengths, intersections, unsorted/duplicate/boolean IDs, spoofed split digest, wrong session and duplicate JSON keys.
- A query is legal only for step 0 or 1, from 64 allowed IDs, not repeated, not an unapproved public input. Matching response accepts exactly one output and matching step+input+challenge; extra labels rejected.
- Final program submission is allowlisted DSL only, **not learner-provided audit predictions or score**.
- An untrusted fabricated Oracle answer can pass the E0 schema test: explicitly record that E0 **does NOT authenticate source**; a separate-process/credential-based custodian is mandatory in E1.

Exact-head safe CI job, source integrity and Codex review must be checked and appended as PR/Issue evidence before labelling engineering acceptance. The new official scored task count is **0**.

[Contract](../e0-custody-boundary-draft.md) / [Issue #104](https://github.com/ryonakayama234/DekaSugi/issues/104).
