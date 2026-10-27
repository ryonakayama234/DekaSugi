# METRO-0001 CAL-01 — 原本保存後の独立再検証記録

id: METRO-0001-CAL01-PROVENANCE-20261027
status: engineering_calibration_pass; independent_source_integrity_verified; no_intelligence_result
updated: 2026-10-27
tags: metrology, calibration, evidence, reproducibility, provenance, independent-review

## 記録の性質と前段階
[最初のCAL-01実行](20261027-cal01-synthetic.md)は固定されたsynthetic fixtureの工学的試行であり、この文書は後続の **元fixtureを保存する改良後の独立した実行記録**。過去の実測runの値や履歴を書き換えず、続く独立監査の証拠を付加する。

## 検証した source / CI / 成果物
- PR2 exact executed source: `0a01cdb6274f0e6244d5dafb3781c6dd6ce59b2c`（合成fixture元記録・CPU/wall計時・負例回帰付き）。
- [GitHub Actions #40458100322](https://github.com/ryonakayama234/DekaSugi/actions/runs/40458100322) / job `122036030528`、run conclusion=success。Python 3.12.15、Linux GitHub-hosted CI。
- `python scripts/check_docs.py` PASS、unit tests **86 tests / 9.298 sec / PASS**。EXP-0003A freeze-checkもPASS、EXP-0003A DEV/FINALは起動なし。
- [GitHub Actions artifact #12712772906](https://github.com/ryonakayama234/DekaSugi/actions/runs/40458100322/artifacts/12712772906) `METRO-0001-CAL-01` をGitHubから直接取得。原ZIP SHA-256: `ee299f75b0aef4d0fbb92345b38758cca93b3f1a784cb61a820e3ee70249e6eb`。
- ZIP内部の `METRO-0001-CAL-01.json` raw bytes SHA-256: `91c0a0d0244143d8c817440639a35efd757fe771419f345240ad35509bbd42a9`。
- ZIP内部の `METRO-0001-CAL-01.fixtures.json` raw bytes SHA-256: `f2fb4f9ad2ff4102c11051f08ab080cc638d7b76a406fe4b83a4452c9480b596`。
- fixture manifest canonical JSON SHA-256 (UTF-8, sorted keys, compact separators) = `c4628bf5f9cbb08232d63806e833926128eeab355f0e69c2979e9b5b2ce00d8f`。同SHAはreportの `source_fixture_manifest_sha256` と一致。各F01–F08 raw_rowsの再計算SHAも全件保存値と一致。
- ArtifactはGitHub Actionsの保存期限・権限に従うため、署名付き出典保証や永久保存の証明ではない。runに実測されたバイト列SHAを残し、後の取り直し時に再照合できる。

## 実測の内容（合成データのみ）
- F01/F02: preregistered canonical summary SHA `0ef732ea2bc266d8d4da2139f665c0240fc1866d71e52a57151ba31f01e89373` と一致。
- F03 duplicate: `duplicate_record`、F04 no audit: `missing_or_extra_field`、F05 tampered: `invalid_hash`、F06 compatible individual rows but non-comparable metric units: `non_comparable`、F07 split leak: `partition_leak`、F08 negative value: `invalid_value`。8/8 expected PASS。
- CAL-01計測器のCPU時間 `7,065,012 ns`、wall時間 `7,063,327 ns`。scope=`fixture_manifest_plus_calibrate_excludes_io`。非決定的な実行時間であり、gold summaryのhashや人工課題の能力指標に含めない。
- budgetを片armで正当な別値に変えた場合は `non_comparable`、不正なbudgetはinvalid。solved/audit判定不一致はinvalid。双方とも付加回帰テストPASS。
- 人工gold fixtureの整数値: 3 tasks×2 arms、正答2/3 each、candidate OFF12/ON12、primitive OFF24/ON27、paired OFF−ON=-3。**合成の既知データであり、Agentの性能測定や学習効果の主張は禁止。**

## 独立レビューと判定境界
- exact source `0a01cdb...` のCodexレビュー状態 completed / has_any_findings=false / has_unresolved_findings=false（GitHub PR #41）。過去headのP2四件は全てsource/test/artifactの対処を照合してreview threadsを解決。
- これはPR2用の **calibrated engineering evidence**。知能成長・能力転移・正規Evaluator評価・技能昇格は行わない。
- このrun文書の追加自体はコード/校正器の方法を変更しないが、PR統合は最終exact headのCIと独立reviewを別途要する。

Related: [preregistered CAL-01 plan](../plan.md) / [original run](20261027-cal01-synthetic.md) / [run index](README.md) / [metric contract](../../../docs/metrology/metrics.md).
