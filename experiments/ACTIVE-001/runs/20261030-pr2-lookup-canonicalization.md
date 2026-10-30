# ACTIVE-001 PR2 — use an internal canonical lookup after validation

id: ACTIVE-001-RUN-20261030-LOOKUP
status: PATCH_CANDIDATE_PENDING_EXACT_HEAD_CI_AND_INDEPENDENT_REVIEW
updated: 2026-10-30
tags: active-learning, synthetic, trust-boundary, MappingProxyType, canonical-lookup, no-scoring
pr: https://github.com/ryonakayama234/DekaSugi/pull/95
preceding_head: 0baf02ee8686d9d21e7b4f0fef0b605486b9b912

## Code-review defect

Independent Codex review of prior exact head 0baf02e identified a **P2**: a caller can supply MappingProxyType wrapping a dict subclass whose ordinary equality matches the canonical mapping but whose __getitem__ returns forged SemanticClass predictions. The old _assert_catalog() only compared equality, after which the learner continued to read the caller's by_id. In a synthetic reproduction this suppressed the true best input 138 and falsely allowed query_unidentifiable.

## Engineering correction and trust contract

Primary packages/active_learning: _assert_catalog now **returns** the private cached canonical Catalog. Both start() and _assert_world() replace the passed Catalog with that trusted instance for computation and replay. All actual lower-level by_id reads in partition scoring, state updates and final_program are explicitly made against _canonical_catalog().by_id. Original structural checks still reject ordinary noncanonical catalogues. This is a **runtime canonicalization** boundary, not a statement that MappingProxyType deeply freezes a dictionary. An equality-preserving malicious wrapper might be admitted, but cannot change predictions, selection, posteriors, historical replay or final program.

New tests/test_active_learning_lookup_canonicalization.py comprises **four invented-fixture-only tests**:
1. Reproduce a dict subclass whose __getitem__ lies although MappingProxyType equality passes; B2 input, partition, final program and false-stop rejection must match the trusted catalog.
2. A true target's selected answer and entire history update remain identical under the lying catalog.
3. B1 fixed-seed random choice agrees for several seeds regardless of forged lookup behavior.
4. A mutable proxy backing that changes after validation cannot poison trusted lookup and is rejected when no longer equal.

Explicit CI-SAFE-V2 allowlist addition for the new file only. Synchronized AGENTS, docs/INDEX, ARCH-001 Mermaid system map, ARCH-002 data flow, ACTIVE-001 spec/plan, roadmap, README and experiments/ACTIVE-001/runs/README in the **same patch**.

## Pre-push engineering evidence and reproduction limits

- Locally reconstructed isolated public synthetic world under Linux Python 3.13.5; fixed 156 inputs / 878 semantic classes; test command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m unittest discover -s tests -p 'test_active_learning*.py' -q.
- **Observed 28/28 PASS** (24 prior ACTIVE invented tests + 4 new ones; elapsed 7.421s).
- Git blob IDs of locally tested changes: packages/active_learning/__init__.py = 1407b18279b21e93b01064af38dfe16c01d9f8ed; tests/test_active_learning_lookup_canonicalization.py = de6f3d51d661c7d92951c890fb0046d686ade6a1.
- This pre-push receipt is not a full exact-head GitHub CI result or an independent reviewer endorsement. Post-push CI and latest-head Codex review must be logged in PR discussion rather than retroactively modifying the record.

## Strict nonclaims and release gates

This does NOT authenticate source custody, the externally supplied Oracle, evaluator-held labels, precommitted B1 seeds, statistical power or genuine intelligence gain. New ACTIVE-001 scored trial count remains **0**. Historical original OPPORTUNITY-001 TRAIN64, EXP-0003A DEV/FINAL, frozen OLD14/NEW9 source files and disabled legacy workflow remain untouched. No broad test discovery, main merge or scientific experiment execution. PR #95 remains DRAFT stacked on prerequisite PR #94 until complete safe CI and independent exact-head P0/P1/P2 review.
