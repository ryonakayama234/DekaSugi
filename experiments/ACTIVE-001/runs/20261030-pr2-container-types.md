# ACTIVE-001 PR2 — strict primitive storage against equality-preserving container subclasses

id: ACTIVE-001-RUN-20261030-CONTAINER
status: PATCH_CANDIDATE_PENDING_EXACT_HEAD_CI_AND_INDEPENDENT_REVIEW
updated: 2026-10-30
tags: active-learning, synthetic, untrusted-session, exact-types, replay, no-scoring
pr: https://github.com/ryonakayama234/DekaSugi/pull/95
reviewed_previous_head: b2acf54c99ef4d82ad59d070167f6e607c737740

## Independent review defect and proposed invariant

Codex's latest exact-head review found P2: an untrusted tuple subclass with normal tuple equality but overridden __iter__ can replace a canonical QuerySession.class_ids tuple, pass the full session equality check, and then report a wrong semantic class vote distribution in partitions/Gini. A natural 20-class fixture can be transformed into 20 identical apparent votes, falsely returning no informative query.

Hypothesis: exact built-in container and field-type checks at the public learner boundary, **before** any use of caller-provided state, reject this and related equality-vs-behavior attacks. Semantic-class membership, canonical split, full ordered history, the seeded B1 and argmax B2 choice, and local answer receipts are still replayed separately.

## Code and negative tests

- Principal: packages/active_learning/__init__.py. Add _assert_session_fields: QuerySession.class_ids must be an exact tuple of exact str IDs; compact answers must be an exact outer tuple of exact inner (int, str, str) triples; trace is an exact tuple; session status and commitment digests are exact strings. Call it at the _assert_world entry before evaluating any derived partitions.
- Add _assert_proposal_fields and _assert_answer_fields: exact dataclasses and built-in primitive fields, including each predictive partition pair; reject bool-as-int and equality-preserving subclasses. Apply to history replay, update and the synthetic make_answer helper. Preserve the already established internal canonical Catalog and full active-query/2 trace contract.
- New invented-only tests/test_active_learning_container_boundary.py has six tests: misleading class_ids iteration despite equal dataclass; subclassed semantic ID; subclassed compact answer inner triple; status/digest subclasses; bool step in QueryProposal; historical QueryAnswer step subclass. Tests verify the targeted API refuses forged containers while canonical question selection still works.
- Add **only** the new invented-fixture module to the CI-SAFE-V2 explicit allowlist. Synchronize AGENTS, docs/INDEX, ARCH-001 Mermaid, ARCH-002 Mermaid/data contract, spec/plan/roadmap/README and run index.

## Local checks and limitations before remote integration

- Linux Python 3.13.5, isolated packages/inquiry_world + packages/active_learning and the ACTIVE synthetic-only tests, no historic scorer import. Command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m unittest discover -s tests -p 'test_active_learning*.py' -q.
- **Actual result: 34 / 34 PASS, 8.411 s** (28 prior ACTIVE tests and 6 new negative tests).
- Git object IDs of exactly these locally tested files: active_learning module e9e93ee16644afa18cf0d39b77dd164f0b470348; new adversarial test module 9c540b76ff07e1adf19a8cb09807d0d8cc516591. Compare uploaded blobs before any PR ref update.
- Previous GitHub exact-head CI b2acf54 succeeded 106/106. This does not imply the new patch passed CI. Record post-integration safe CI and reviewer result in PR discussion, not as invented future PASS in this immutable engineering ledger.

## Scientific and release boundaries

The checks do NOT authenticate Oracle answers, evaluator-held target labels, externally custodied split or B1 random seed; do not claim learned inquiry policy, generalization or positive correctness effect. ACTIVE-001 real scored observations remain **0**. Never modify original disabled historical workflow, source-locked OLD14/NEW9 members, or rescore TRAIN64/DEV/FINAL. PR #95 stays DRAFT stacked on PR #94; successful exact-head safe synthetic CI AND fresh independent P0/P1/P2 review are necessary before marking reviewed or merging.
