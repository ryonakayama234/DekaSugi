# ACTIVE-001 P1 B1+ — invented-only engineering gate (2026-10-31)

id: ACTIVE-001-B1PLUS-P1-ENGINEERING
status: code_and_source_only; exact_head_CI_and_review_pending
updated: 2026-10-31

## Goal and falsifiers
Add policy \`informative-uniform-v1\` that draws only from unanswered positive-integer-Gini inputs. A zero-Gini choice, duplicate question, mismatched seed or historical choice, accepted tampering, changed B1 RNG domain or B2 argmax falsifies engineering acceptance.

## Scope and evidence custody
Branch \`research/active001-b1plus-informative-uniform\` based on main \`d9ad80fc844a09c312f6434d20d0d17fdcac4109\`. Source: \`packages/active_learning/__init__.py\`. Tests extend pre-allowlisted \`tests/test_active_learning_synthetic.py\`. Invented \`input_split(20261030)\` fixture only; it is **not** official target/split/seed. Built-in \`make_answer\` is local synthetic receipt, not independent Oracle. No frozen source, old TRAIN/DEV/FINAL, hidden evaluator, old docs-check.yml or scored study was touched.

## Tests to verify at exact PR head
1. Positive-only query choice matches independently constructed semantic-output partition and fixed RNG.
2. Existing B1 all-remaining pool and original RNG domain; B2 integer argmax.
3. Complete \`active-query/2\` history replay and canonical terminal statuses after answer(s).
4. Construct real F2 public-output context with multiple hypotheses and zero informative queries; stop as \`query_unidentifiable\`.
5. Invalid seed, bool-as-int, forged proposal, policy/seed, altered class IDs and zero budget rejected.
6. Full safe explicitly allowlisted CI plus docs/source locks; Codex review requested independently where available.

**This document is a source declaration, not proof of CI PASS.** Record actual run URLs, head SHAs, success or failure in the PR once observed.

## Interpretation
New **scored** ACTIVE-001 observations: 0. Official evaluator: none. Heldout accuracy improvement: **not measured**. Full structural F4: **not computed**. CPU benefit: **not measured**. New confirmatory method and source/seed freeze: **not approved**. P2 CPU and P3 statistical checks plus independent evaluator/activation decision remain separate.

[ADR-0007](../../../docs/architecture/decisions/ADR-0007-active001-b1plus-control.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).
