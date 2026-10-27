# METRO-VALIDITY — 測定妥当性・因果推論と不確実性

id: METRO-VALIDITY
status: proposed; no confirmatory result
updated: 2026-10-27
tags: metrology, validity, causal-inference, uncertainty, bias

## 妥当性の四つの問い
1. **Construct**: 何を測りたいか。原始演算回数は知能そのものではなく費用の限定的観測。
2. **Internal**: 介入以外の差は統制されたか。学習済み技能、予算、評価器、データ露見状態を記録。
3. **External**: その能力推定がどの課題分布まで通用するか。String→Stringの合成familyから他領域への一般化は不可。
4. **Statistical conclusion**: pairing/cluster/time noise/欠測/多重探索により効果を誤認していないか。効果量、区間、不利なtaskも報告。

## 科学上の分離
- Observation: 実際に測った原値（検証済み探索状態、call数、CPU）。
- Estimate: 条件付き成功率・paired差・CI。前処理/集計法/分母/集約単位を固定。
- Claim: 『学習に起因する』等のメカニズムの説明。代替仮説（単なる暗記、探索順、予算差、評価データ露見、cost移転）を列記しreviewを要する。

## 実験データ利用規則
- 既存EXP-0002B FINAL112は使用済みのholdout。METRO校正のreaggregation/regression用途は可能でも、新しい能力仮説を確認する独立データではない。
- EXP-0003A DEV64/FINAL128は凍結済み。METROの試験はsynthetic fixtureと明示的に許可されたTRAIN工程記録を使う。新しいEvaluator起動や結果参照を行わない。
- EXP-0003A B3/B2の既定計画、family cluster bootstrap/閾値/判定条件は不変更。METROの指標を後付けの正式採否へ混ぜない。

## Calibrationと新しい科学実験の違い
Calibrationは測定器が既知の入力に対し期待された出力を返し、改変・欠測を拒否するかを検査する。知能成長の証明ではない。新しい能力科学は、pre/post状態、介入、対照、fresh holdout、事前登録のestimandと不確実性を要する。

## 停止条件
P0/P1の trust leak、方法とschemaの矛盾、測定器による本体の行動変化、改変の黙認、不公正な比較、古いFINALを新規confirmatory証拠として使用、資料リンク破損、独立レビュー未完了ではmergeしない。負の校正結果もrunとして保存し、人間と次段階を検討する。

Related: [ontology](ontology.md) / [metrics](metrics.md) / [METRO plan](../../experiments/METRO-0001/plan.md) / [EXP-0003A protocol](../../experiments/EXP-0003A/plan.md).
