# R2-M-ENG範囲案へのClaude精査 — 合格、GO条件4件を付してOwner判断へ

id: R-20261104-08-MUSE-REVIEW
status: review_passed / owner_go_decision_pending / no_code_yet / no_experiment / no_scoring
updated: 2026-11-04
tags: gate-r2-m-paper, claude-review, r2-m-eng, scope, engineering-only

> 本書は外部監督者Claude（ごま）による独立精査である。対象は [R2-M-ENG-SCOPE-20261104](../specs/R2-M-ENG-SCOPE.md)（PR #175、head `d89309c3a77189aa8cfcfbc4a43d9b4a3c303189`）。本書は実装GOではない。実装の可否と範囲の確定はOwnerの別途決定を要する。正本はOwner採用済みの[方法v2](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md)である。

## 1. 独立確認

- PR #175の差分は範囲案1件とINDEX登録のみ（2ファイル）。コード・テスト・CI設定への変更は0件で、提出者報告と一致する。基点は現行main（PR #171マージ `67f5764`）。
- 監督者環境で `python scripts/check_docs.py` を再実行しPASS。差分が文書のみであるため、既存テストの結果に影響し得る変更は含まれていない。
- 規模見積もりの検算: 実装モジュール9件の合計は **1,970行**、テスト5件は **1,220行**、合計 **3,190行**となり、文書の概算と一致する。

## 2. 指示項目との照合（Owner指示6項目）

| 項目 | 判定 | 根拠 |
|---|---|---|
| 1. 実装範囲の定義 | 合格 | §2で方法v2 §1〜§5への逐条対応表。新規隔離パッケージ `packages/r2_m_eng`、`packages/r1_eng` は変更しない。gateway、復号器・ASTコンパイラ、独立validator、Sleep-lite、Snapshot（絶対パス＋メータ3種）、F00/F10、対照5arm、閉包記録、6 schemaが全て含まれる |
| 2. ENG許可境界の案 | 合格 | §1・§2.1で「工学診断のみ」を明記。人工の既知法則fixture（全16係数組の単体確認を含む）とし、その人間提供性を明記。科学評価・事前登録を要する実行・M_use/M_gap認定は範囲外。公開済みparity例の証拠利用も禁止 |
| 3. テスト計画 | 合格 | §3の9区分。復号の一意性、OFFの全合法fallback保持、短絡を含むメータ検算、異cwd子プロセスでの同一bytes復元、Snapshotの排他作成・改ざん検知、漏洩ガードの負例、tie規則、閉包の自動昇格禁止まで含む |
| 4. 成果物と受入基準 | 合格 | §4。受入は「ENG機構が仕様どおり動く」という工学判定までに限定し、科学的認定は別ゲートと明記。CI導線の追加は許可後に限るとしている |
| 5. 規模の見積もり | 合格 | §5に予定ファイル14件＋CI差分。検算一致（上記§1） |
| 6. 未決定事項の明示 | 合格 | §6の6件はいずれも勝手に決めず選択肢として返されている。特に科学source・事前登録・custodyを「ENGで決定・稼働しない」と明言した点が正しい |

## 3. 評価する点

1. **ScoreReceiptの扱い**。ENGではschemaと人工値の検証のみに限定し、本当のprivate outcome採点はしない、と先に縛っている。
2. **validatorの独立性**を「decoder内部の同一実装で代用しない」と明記したこと。R1-ENGで独立validatorが果たした役割を正しく継承している。
3. **候補数の会計**。「候補上限16を生成16個と数えない」をテスト計画側にも入れており、前回精査のP1注記が反映されている。

## 4. GOに際しての条件案（Owner判断に付すもの）

範囲案§6の未決定事項のうち、ENGの実施に必要な範囲で次を条件として提案する。科学側の未決定（§6-4）はENGでは扱わないことで確定してよい。

- **条件A（提出の分割）:** 約3,190行を単一PRにせず、段階に分けて提出し、各段階でClaudeの受入確認を経ること。分割案: 段階1＝records/gateway/decoder/validator/sleep_lite、段階2＝snapshot/dispatch/meter、段階3＝controls/closure/runner/fixture。R1-ENG（約12ファイル）の3倍規模であり、独立検証の実効性を保つためである。
- **条件B（source境界の水準）:** ENGの人工fixtureでは、モジュール分離＋import境界の負例テストで足りるものとし、敵対的同一プロセス防御やプロセス分離の保証は科学ゲート側の判断に送る。人工sourceには守るべき実秘密が存在しないため、この水準が比例する。
- **条件C（閉包の固定）:** ENG期間中、閉包はUNKNOWNのまま固定する。COMPLETEへの昇格試行はENGの成果物に含めない。
- **条件D（未起動armの固定）:** F01/F11はNOT_EVALUATEDのschema枠のみ、ORACLE-REFはEvaluator専用の参照schemaのみとし、範囲案の提案どおりとする。

## 5. 監督者の判定と勧告

**判定: 合格。** 範囲案は方法v2の契約を過不足なく実装範囲へ写像しており、許可境界も自己申告として正確である。

勧告: **上記条件A〜Dを付して、R2-M-ENGの実装GOを出すこと。** GOの効力は人工fixtureによる工学診断の実装と受入までであり、科学実験・封印評価・採点・M_use/M_gap認定は引き続き未許可である。

| 項目 | 状態 |
|---|---|
| R2-M-ENG範囲案（PR #175） | 提出済み・Claude精査合格 |
| R2-M-ENG実装GO | Owner未決定（監督者勧告: 条件A〜DつきでGO） |
| 科学実験・採点・認定 | 未許可（別途、事前登録とOwner許可が必要） |
| 現在の認定 | M_use NOT_CERTIFIED、M_gap UNKNOWN、N_rep/U/T NOT_EVALUATED |
| PR #175のマージ | 未実施・未承認 |
