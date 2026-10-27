# METRO-0001 — 校正run目録

id: METRO-0001-RUNS
status: planned; no_calibration_run
updated: 2026-10-27
tags: metrology, calibration, run-index, preregistration

## Run index
| run ID | phase | status | measurement | source |
|---|---|---|---|---|
| CAL-01 | independent fixture + optional TRAIN evidence | not_run | no observations or claims | [plan-v1](../plan.md) |

## 必須run属性
source_commit, metric_spec_version, adapter_version, fixture_hash, original_evidence_hashes, Python/OS, test command, CI job/URL, expected/observed integer metrics, missing/invalid reason, independent review, and acceptance decision。未実行や接続不能は結果ではない。

## 証拠保存
生証拠と集計を分離、追記専用。結論はcalibration/engineering/confirmatoryを区別。EXP-0003Aのholdoutは触らず、旧FINALは新規能力仮説に流用しない。

Related: [calibration plan](../plan.md) / [measure contract](../../../docs/metrology/metrics.md) / [evidence model](../../../docs/metrology/evidence-model.md).

## PR2 calibration implementation status (2026-10-27)
- `packages/metrology` adds synthetic CAL-01 cases F01–F08 and exact preregistered SHA comparison. Source code and unit tests exist on PR2 feature branch; CI result and immutable run record must be added **only after execution**. This does not imply an AI learning result.
- [Implementation](../../../packages/metrology/__init__.py) / [CLI](../../../packages/metrology/__main__.py) / [tests](../../../tests/test_metro0001_calibration.py).
