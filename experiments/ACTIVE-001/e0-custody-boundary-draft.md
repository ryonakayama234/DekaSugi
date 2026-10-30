# ACTIVE-001 E0 — public-only wire boundary for future independent evaluator

id: ACTIVE-001-E0-CUSTODY-BOUNDARY
status: proposed_engineering_wire_contract; invented_only; no_scoring_authority
updated: 2026-10-31
tags: active-learning, independent-evaluation, information-flow, no-scoring, security

## Immediate decision

E0 is a deliberately **unscored** public-only interface and leak-denial test. It does not give the same-process learner independent custody. The next scientific step is NOT “run heldout evaluation now.” It is to make the future independent evaluator's communication boundary testable and refuse secret data fields. Parent [Issue #104](https://github.com/ryonakayama234/DekaSugi/issues/104) and method lock [Issue #96](https://github.com/ryonakayama234/DekaSugi/issues/96). This branch stacks on P3 statistics PR #103, which remains draft/unmerged. No future secret/root/official target IDs are selected.

## Exactly permitted outward frames

| Frame | Allowed public fields | Disallowed classes |
|---|---|---|
| Task view | \`schema, session_id, public_pool_ids(28), query_input_ids(64), public_examples(2), split_digest, max_questions=2\` | target ID, family, source/seed root, evaluator labels/inputs as an explicit field, future Oracle answers, outcome metrics |
| Query request | \`schema, session_id, challenge_digest, step, input_id\` | third query, stale step, wrong pool, duplicate query, target/evaluation fields |
| One-query response | \`schema, session_id, challenge_digest, step, input_id, output\` | unsolicited response, different step/ID, extra labels, future answers |
| Final | \`schema, session_id, challenge_digest, program\` | auditor predictions, target truth, self-reported score, unapproved program |

Strict JSON parser rejects *all* extra/missing/duplicate keys, including apparently benign metadata; exact int types prevent bool impersonation. Public/query pools are canonical distinct ascending ID ranges; independent recomputation of the 28/64/64 split digest uses the **complement of public+query IDs** but never accesses the 64 auditor **truth labels**. Session ID must be opaque and *independently generated* in future E1; its presence in a frame is not proof it was generated independently. Content digest binds the public frame to query/answer/final messages but cannot authenticate the author.

A deterministic synthetic test holds fabricated \`private_mock\` fields outside the actual serialized frame, injects forbidden keys into copies and verifies strict rejection. It also explicitly proves a forged answer can still pass schema validation: this demonstrates an important E1 blocker rather than claiming total isolation. No official target, withheld truth, scorer or historical experiment is imported.

## E1 independent custodian design (NOT implemented; blocked)

After method+source/seed freeze, use independently owned OS process/container **with no learner imports of the private truth module**, private seed-root creation and custody, no shared memory/files/network side channels to learner and authenticated/provenance-protected answer receipts. Full 64-input auditor scoring happens only inside that custodian **after final program submission**; learner receives no interim score. A hash of public data, Python \`private\` attributes, path naming or a different class within the *same* interpreter is NOT an independence guarantee. Include negative pipe/log/debug/cross-process leaks, forged policy answer/trace, and "no hidden scorer import" checks in a new PR. E1 source approval is distinct from passing E0 tests.

## E2 scientific execution (NOT authorized)

Only after independent evaluator/attestation is verified, select and freeze a single CI/test family and sample size (4096 Student-t draft versus 8138 conservative Hoeffding or new preregistered alternative), exact code/tree/source/secret-root commitment, split+target law, random seeds, CPU/memory resource ceilings, signed provenance and error/STOP policy. Freeze before *any* genuine outcomes; no optional sample-size stopping, no unblinded repair-and-rescore. An invalid/missing scientific record is \`NOT_ESTIMABLE\`, not zero and never silently excluded. New genuine scored ACTIVE-001 observations remain **0**.

## Engineering test and no-claim limits

\`packages.active_custody_boundary\` + explicitly CI-SAFE-V2-allowlisted \`tests/test_active_custody_boundary.py\`; do not alter original disabled workflow, historical locks or main. This module is a parse/validation prototype **without** out-of-process secrecy, actual Oracle, trusted audit, activation or experimental power finding. The preflight is reviewed as code only; Codex no findings cannot certify custodian trust.

[Wire implementation](../../packages/active_custody_boundary/__init__.py) / [negative tests](../../tests/test_active_custody_boundary.py) / [run receipt](runs/20261031-e0-public-wire.md).
