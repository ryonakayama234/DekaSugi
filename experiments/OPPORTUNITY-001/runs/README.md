# OPPORTUNITY-001 — Run ledger

id: OPPORTUNITY-001-RUN-INDEX
status: not_run; design_only; no_implementation
updated: 2026-10-28
tags: experiment, opportunity, provenance, planned, not-run

## Current status
- 本研究は測定対象・仮説・アーキテクチャ・データ契約・事前登録**案**の設計段階。生成器・paired試行器・分析器は未実装。
- TRAIN/DEV/FINAL、メータ校正、新しい二択試験、学習、確証評価は **0件 / not_run**。
- この目録には新しい結果・改善の証拠・性能数値は存在しない。POLICY-DIAG-001の過去DEV64とMETRO CAL-01の人工fixture結果を再利用して新しい効果を主張しない。
- 事前登録数値・seed・新規母集団はreview/freeze前のproposal。凍結の新しいcommit以降だけ実験を許す。

## Future run record contract (not executed)
各run: immutable run_id、phase、exact command、Git source commit + blobs、Python/OS/CPU、generator/skill/policy/verifier/meter SHA、public split hash、private manifest checksum（非公開）、生証拠hash、全arm母数、監査判定、missing/invalid/non_comparable、calls/candidates/CPU/wall費用、区間・代替説明、独立レビューと採否。

## Safeguards
- PR CIはsynthetic/TRAIN-fixtureのみ。元のEXP-0003A DEV64や封印されたFINAL128を起動しない。
- private audit第3例・generator source records・secretは公開リポジトリへ書かない。
- 失敗や欠測も不変の独立run記録として保存する。

Related: [plan](../plan.md) / [spec](../../../docs/specs/OPPORTUNITY-001.md) / [Issue #56](https://github.com/ryonakayama234/DekaSugi/issues/56)。

## PR2 synthetic-fixture calibration scope
- 工学校正専用 `packages/evaluation/opportunity.py` および `tests/test_opportunity_fixture.py`。意図的に作成した分類用fixtureであり新規研究の生成課題ではない。
- 新しい研究用TRAIN/DEV/FINALの試行・採点は **0件 / not_run**。独立原証拠監査や一般化性能の証明ではない。
- CIと独立レビュー結果は完成後に追記記録。将来のmethod freeze、actual-evidence adapter、fresh holdoutは未着手。

- [2026-10-28 PR2 synthetic fixture CI/review calibration](20261028-pr2-fixture-calibration.md): completed_engineering_calibration_only; not_scientific_result. No new study TRAIN/DEV/FINAL trial.
