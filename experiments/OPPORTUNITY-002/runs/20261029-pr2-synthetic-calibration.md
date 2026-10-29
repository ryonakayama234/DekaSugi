# OPPORTUNITY-002 PR2 — synthetic-only boundary calibration CI receipt

id: OPPORTUNITY-002-PR2-SYNTHETIC-CI-20261029
status: engineering_calibration_pass; not_scientific_result; review_pending
updated: 2026-10-29
tags: opportunity, synthetic, calibration, independent-enumerator, run

## Observed evidence (no real experimental scoring)
- First staged PR2 exact code/docs head: `7f12a623ce12bda9ac03dd3ec4f60754999a3a7b`, stacked on PR1 branch.
- Official GitHub Actions [Research verification run #40859385151](https://github.com/ryonakayama234/DekaSugi/actions/runs/40859385151), job 123398426021: **completed / success**. Log records: `Documentation validation PASSED: 89 markdown files`, `Ran 247 tests in 12.538s`, five new `test_opportunity2_boundary` checks **ok**. The inherited main-push-only DEV step was **not activated** by this PR workflow.
- Source: [pure independent synthetic script](../../../scripts/opportunity2_boundary.py) and [unit fixtures](../../../tests/test_opportunity2_boundary.py). This source has no production evaluator/generator import and loads no actual frozen original or private third-audit bytes.
- The unit tests executed `calibrate()` on wholly invented examples. Verified structural numbers under the assumed syntax/cap: OFF=40, ON=47; ON primitive-expanded set equals OFF; product enumeration agrees with BFS support sets; budget5 ON finds synthetic macro at fifth vs OFF exhausts; budget100 OFF sixth / ON fifth; lowercase ASCII negative `fiz`→`zif`; unsafe operator and invalid budgets are rejected.
- **Scientific nonclaim:** The result does not prove official frozen skill source/hash authenticity, empirical new TRAIN ability, policy benefit, general Unicode expressivity, learning plasticity, CPU savings, private custody or independent scientific review. Source semantics were modeled independently from specified three primitives and synthetic lower(trim) macro.
- New genuine OPPORTUNITY-002 scored task count **0**; original OPPORTUNITY-001 true 64 pairs **not replayed**; old EXP-0003A DEV64/FINAL128 **not generated/scored**; new scoring authority **false**.
- Independent exact-PR2-head Codex/human review: **pending**; after adding this retrospective public receipt, rerun CI against the updated PR2 head is required before merge. This record describes the original observed CI, not a new claim about later commits.

## Reproducibility / exact command
The production CI invokes `python -m unittest discover -s tests -v` and `python scripts/check_docs.py` under Python 3.12 on Ubuntu. The newly added checker may also be executed as `python scripts/opportunity2_boundary.py` for synthetic-only JSON summary; the latter direct CLI was **not** executed as an official CI step in run #40859385151. Fail closed on unsupported assumptions. No private paths, credentials, labels or source-family mapping are included.

[Method plan](../plan.md) / [Review checklist](../../../docs/specs/OPPORTUNITY-002-REVIEW-CHECKLIST.md) / [Run index](README.md) / [main safety blocker #88](https://github.com/ryonakayama234/DekaSugi/issues/88).
