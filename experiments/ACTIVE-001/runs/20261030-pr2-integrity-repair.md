# ACTIVE-001 PR2 — synthetic-only query integrity correction

id: ACTIVE-001-RUN-20261030-PR2-INTEGRITY
status: proposed_patch_pending_exact_head_ci_and_independent_review
updated: 2026-10-30
tags: active-learning, adversarial, synthetic, review, non-scoring

## Research context / hypothesis
Prior local PR2 fixture: 5 tests passed on an earlier branch head, **not** independent scientific validation. Latest Codex review of PR #95 at `00876b7ed3b42601dd22ecb84a3f946c33c3f536` raised 3 P1 (semantic class/budget consistency, input partition boundary, chosen-query policy replay) and 1 P2 (conditional test assertions). This engineering change tests the hypothesis that these local invariants are necessary to faithfully measure subsequent within-task question value.

## Work scope and observable changes
- Principal: `packages/active_learning`. Exact class set reconstructed from all public and ordered answers; reject vote inflation, impossible statuses/budgets and repeated/bad question IDs; independently replay B2 maximum Gini and B1 deterministically seeded random selection.
- Auxiliary: `packages/inquiry_world`. Validate 28/64/64 sorted, disjoint, complete input pools and canonical commitment *before* learner receives the split. Session embeds public/query pool commitment.
- `tests/test_active_learning_synthetic.py`: remove conditional skip around key assertions; `tests/test_active_learning_integrity.py`: invented adversarial counterexamples for all four review areas.
- `scripts/run_research_ci_v2_tests.py`: explicitly allowlist ONLY the two ACTIVE-001 invented-fixture test modules, preserving safe synthetic-only CI; never general discover.
- Same-change docs: AGENTS, INDEX, ARCH-001 and ARCH-002 Mermaid, spec, plan, roadmap, README and run index.

## Evidence and nonclaims at patch construction
- Exact patched commit SHA, source identity and GitHub CI result: **pending until actual GitHub branch update and run**.
- Intended check: `python scripts/check_docs.py` and successor CI-SAFE-V2 allowlisted synthetic tests (on an exact PR head, without any historical scorer).
- Actual run count for new ACTIVE-001 scored evaluations = **0**. There is no independent Oracle/evaluator, externally authenticated answer receipt, verified seed precommitment, frozen N/power, learned questioning strategy or transfer.
- A local digest establishes local consistency only, NOT genuine source/oracle provenance. No false PASS is inferred from a draft receipt.

## Safety and release gates
No alteration of frozen OLD14/NEW9 source members, historical workflow, OPPORTUNITY-001 original TRAIN64, or scored DEV/FINAL. Do not merge draft PR #95 until new exact-head safe CI, independent P0/P1/P2 review and independent GitHub control-plane confirmation that the historical main-push DEV workflow remains `disabled_manually`. Subsequent scientific trials require separate preregistration/evaluator and explicit approval. Historic experimental evidence must never be replayed.

## 2026-10-30 — exact corrective-head CI outcome, append-only

- Verified commit: `639482cc709fdaf27f83f6e4f81377a022dfb45a` (15-file coherent change against earlier `00876b7ed3`).
- GitHub Actions successor workflow: [run 41032936594](https://github.com/ryonakayama234/DekaSugi/actions/runs/41032936594), job `123986786809`, **completed SUCCESS**. Python setup, source-only immutable old9/old14 and v2 explicit allowlist checks, documentation/internal links, and whitelist-only synthetic unit tests all succeeded.
- Decoded GitHub job log: **Ran 88 tests in 1.912s; OK**, including 5 original ACTIVE-001 fixtures and 5 new adversarial integrity fixtures (10 ACTIVE-001 tests), without historical evaluator or scored trial execution in successor CI.
- This demonstrates engineering regression checks at the stated commit only, NOT a separate source-authenticated Oracle, scientific improvement, independent code review, or approval of new scored data.
- The log append changes the branch head and therefore requires a *new* exact-head safe-CI check and independent review on the subsequent commit. Historical original-workflow control-plane state has **not** been verified by this run; main merge remains blocked.
