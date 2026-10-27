# METRO-0001 CAL-01 — 合成fixtureによる計測器の校正 run

id: METRO-0001-CAL01-20261027
status: engineering_fixture_pass; candidate_review; no_intelligence_result
updated: 2026-10-27
tags: metrology, calibration, engineering, provenance, synthetic-only

## 研究上の位置づけ
[事前登録v1](../plan.md)のF01–F08を **合成fixtureだけ** で検査。目的はEvidenceEnvelopeとpaired reducerの工学的校正。Agentの知能が向上した証拠、異領域転移の証拠、EXP-0003AのDEV/FINAL評価ではない。計測器の正式な採用はCIと独立レビュー後に判断する。

## 実行来歴
- source PR2 head: `ff97ac8a6a942be6b52119c5421f25d3af6407e1` （CAL-01 CLIとCI uploadを含む版）。
- [GitHub Actions #40457141475](https://github.com/ryonakayama234/DekaSugi/actions/runs/40457141475): workflow `Research verification`、event=pull_request、conclusion=success。
- job ID `122032978048`、CPython `3.12.15`、GitHub-hosted `ubuntu-latest`。
- Artifact `METRO-0001-CAL-01` ID `12712349141`、ZIP 549 bytes、2027-01-25T05:45:37Z失効予定（Actions環境で表示）。元ArtifactのZIP/JSONのバイト列SHA-256は本runでは**未取得**。内容を再計算した値と、取得・監査したoriginal bytesを同一と主張しない。
- CLI: `python -m packages.metrology --mode calibrate --output .run/METRO-0001-CAL-01.json`、新規ファイルへの排他的書込み。
- 全unit test: **82 tests、PASS**。文書リンク検査、EXP-0001/0002回帰、EXP-0003A preflight/check-freeze、TRAIN/DREAM工学工程もActionsで成功。EXP-0003A DEV/FINALは未採点。

## F01–F08実測（CAL-01人工入力）
| case | observed | preregistered expected | result |
|---|---|---|---|
| F01 gold | `0ef732ea2bc266d8d4da2139f665c0240fc1866d71e52a57151ba31f01e89373` | same canonical summary SHA | PASS |
| F02 reordered | `0ef732ea2bc266d8d4da2139f665c0240fc1866d71e52a57151ba31f01e89373` | order independent | PASS |
| F03 duplicate | `duplicate_record` | invalid | PASS |
| F04 missing audit | `missing_or_extra_field` | invalid | PASS |
| F05 changed value no reseal | `invalid_hash` | invalid | PASS |
| F06 individually valid incompatible units | `non_comparable` | no paired effect | PASS |
| F07 forbidden split leaked | `partition_leak` | invalid | PASS |
| F08 negative CPU-time metric | `invalid_value` | invalid | PASS |

Synthetic gold task count3、OFF/ON audited correct各2、candidate各12、primitive calls OFF24/ON27、paired OFF−ON=-3。**これはコードの確認用に人工的に決めた値であって、DekaSugiの実世界での能力測定値ではない。**

## M1–M4の観測結果
- M1: F01/F02の整数集計/summary hash一致、PASS。
- M2: F03/F04/F05/F07/F08の誤証拠を拒否、指定fixture範囲でPASS。SHAは真正性の暗号学的署名ではない。
- M3: 新METRO reducerは既存探索を呼び出さないread-only処理。ユニットテスト `test_m3_existing_canonical_meter_does_not_change_synthesis` は人工公開TaskSpecで同一status/AST/candidates/traceを確認しPASS。一般的な計測非干渉性の証明ではない。
- M4: F06ではvalidだが異単位の対照と介入からeffect deltaを算出しないことを確認、PASS。

## 決定・限界
この時点で **engineering_fixture_pass**。正式統合はPR2最新headの全CIと独立レビューを別途要求する。観測・解釈・主張の三区分、原始演算と総CPUの区別、実験分割の隔離は維持。従来の凍結済み手法/Library/DEV/FINALを変更していない。
