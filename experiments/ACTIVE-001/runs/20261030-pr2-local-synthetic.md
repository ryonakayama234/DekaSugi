# ACTIVE-001 PR2 — synthetic-only local engineering receipt

id: ACTIVE-001-RUN-20261030-PR2-SYNTHETIC
status: engineering_calibration_pass_local; no_scored_study; independent_review_pending
updated: 2026-10-30
tags: run, synthetic, active-learning, verification

## Scope
Invented-fixture-only local test. **NOT** a new scored research distribution, trained policy result, independently authenticated Oracle, generalization proof, or capability promotion. No legacy DEV/FINAL/TRAIN64 generator or scorer accessed.

## Exact test provenance
The source tree used for local tests contains exactly these new GitHub-matching source blobs:
- `packages/inquiry_world/__init__.py` = `c045ecb2b397acd5fd2cfad36f48bb6223f4c5bc`
- `packages/active_learning/__init__.py` = `e9042d5e87916623df759c9315609a685fe4a30c`
- `tests/test_active_learning_synthetic.py` = `967847df24438b4b0f07da156c9629562159b741`
Code-only branch head before documentation: `8349079fa48b8ba0d8edbc7f8316e4685f13e0aa`.

Local isolated tree command:
```bash
cd /mnt/data/active001_local
PYTHONPATH=. python -m unittest discover -s tests -p test_active_learning_synthetic.py -v
```
Linux x86_64, **Python 3.13.5** (not the planned CI Python 3.12). Five named synthetic tests **5 passed, 0 failed**, second run 0.802 s (first 0.783 s). Tests cover finite domain and syntax count, trusted operation semantics and invalid operators, deterministic Gini argmax/tie, random policy/B0 parity, forged/stale answer and model-inconsistent update. Some negative branches depend on the particular ambiguous invented fixture and need later explicit independent coverage.

## Exact engineering observations
156 distinct input strings (alphabet `a,A,b,B,space`, lengths 0..3), 4,681 syntactic programs, **878 distinct semantic signatures**. Synthetic test public examples chosen as the first two seeded public inputs; `status=ambiguous`, 20 remaining semantic classes, first maximum disagreement selected input ID 138; exact Gini score 368/400. World digest `158657529ef0b16a92b6f34984d07b8d3a318e6edca2b8a7f183add40bbf50a3`, invented split seed 20261030 and digest `cbabb2d8f22e2cc73e69c82ae88733bfcfec97e4a6f749c66bf68e3ee2ca4c49`. **This is not the future scored source/split freeze.**

## Not satisfied / blocking
- The tests were run **locally in an isolated partial source tree**. Full-repository `python scripts/check_docs.py` and GitHub CI on exact PR2 head not yet demonstrated. The CI-SAFE-V2 explicit test allowlist is deliberately **unchanged**, so these tests are not included there by implication.
- `QueryAnswer` currently models an invented local receipt. Digest equality is not proof of external Oracle authority, private target non-leakage or custody. Future independent evaluator must verify chronology, split/target secrecy, source identity, missingness and all negative cases.
- No independent latest-head review. Owner verification that old main-push historical workflow is `disabled_manually` is not established. No main merge or fresh real scoring authorized; no scientific `H1` improvement estimate.

[Plan](../plan.md) / [Spec](../../../docs/specs/ACTIVE-001.md) / [Issue #93](https://github.com/ryonakayama234/DekaSugi/issues/93).
