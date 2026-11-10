# WORLD-PREREG-RQ3-20261110-03 — 仕様パック審査後の blocking 逆質問

id: WORLD-PREREG-RQ3-20261110-03  
status: lead_questions / blocking_revisions_required / NOT_FROZEN / NO_CAL_GO / NOT_IMPLEMENTED / NOT_RUN  
updated: 2026-11-10  
author_role: Research Lead (ChatGPT)  
parent_review: [WORLD-PREREG-R3-20261110-03](WORLD-PREREG-R3-20261110-03-lead-specpack-review.md)  
target: [PR #194 / 仕様パック head a01662cc](https://github.com/ryonakayama234/DekaSugi/pull/194)  
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> RQ2 の Owner 採用（[コメント 6768253225](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6768253225)）を撤回するための再質問ではない。採用案を矛盾なく、第三者が同じ結論を再現できる仕様にするための **blocking 明確化**である。回答は AGREE / REVISE / DISAGREE、変更するドラフト/パックの節、具体的な規則・表、反証/UNKNOWN、変更対象・非対象を対応付けてほしい。CAL・実装・実験は未許可。

## Q1（B1/B3、最優先）tag の一意性と `H_0` 分岐証人をどう両立するか

- パック §1 は `law_i ≠ law_j ⇒ tag_i ≠ tag_j`、同時に `H_0` は tag を含む。§6 K0-a は異なる law 間の `H_0` 同一ペアを要求する。現状のままでは証人が存在しない。
- `H_0` 等価を不透明 ID の α-renaming の下で判定するのか、tag の law 専属性を修正するのか、それ以外の規則にするのか、**唯一の判定方法**を選んでほしい。デモ、初期観測、行動後の履歴、feedback をどの順序で比較するか。ID-only 漏洩検査で帰無分布とフェーズ内/間の再使用規則をどう定義するか。
- **受入条件**: 異なる law の非空の K0-a 証人が定義上可能であることを小さな構成例とともに示し、K0-b の識別性判定まで一貫した比較表があること。

## Q2（B3、v2 §7との整合）K0 の STOP は何の主張を止めるのか

- パック §6 の「K0-a 証人なしなら二階必要性のみ停止」と v2 §7 の「課題設計を STOP/REDESIGN」をどちらに統一するか。K0-a/b/c ごとに「主張B」「二階スキーマへの帰属」「family採用」「本実験 GO」「再設計」の遷移表が必要。
- K0-c の `δ` の指す主指標、oracle が完全列挙された条件、H=64 手の対象、confidence bound 計算法と UNKNOWN の優先順位は何か。
- **受入条件**: 同じ K0 証拠で異なるレビュー担当者が異なる STOP 範囲を選べないこと。

## Q3（B2、seed/arm）評価器 grammar と H+/RANK-ONLY の閉包を正確に定義できるか

- v2 §4 は evaluator node 4種「のみ」、パック §2 は BRANCH を第5種に追加。誰がいつ BRANCH の evaluator 実装とインスタンスを持てるのか、構成 operator の上位権限と分離してほしい。
- 全 operator の入出力型・guard/dispatch・変数の可視範囲・観測特徴/定数・失敗時の扱い・意味論、生成順序・prior、固定 H+ の候補列挙規則、FULL の経験由来述語との候補集合同値の成立条件・反証条件を示してほしい。特に H+ の「構築なし」と「constructor 閉包」を整合させる。
- FIXED-IF 贈与内容、LOOKUP 距離/容量/abstain、REC の feature/policy、PRED-ONLY の feature map 継承と BRANCH 含有 AST の拒否を権限表へ反映してほしい。
- **受入条件**: 新記号なしの初期状態での callable 在庫と、経験後に可能な AST を、全 arm で同一テスト入力に対して列挙・比較できる契約があること（テスト実行は要求しない）。

## Q4（B1/B4、世界・分母）G2 の長さと不可能例の分母をどう定義するか

- v2 §1 の初期長4〜12とパック §4 の G2初期長13〜16はどう住み分けるか。G1/G2/訓練の initial buffer と intermediate buffer の区別を表にすること。
- v2 §2 は不可能 family を分母に残す一方、パック §4 は容量不能類型を生成前除外する。除外前母数、主推定の母数、生成後発見した不能/UNKNOWN の処理、除外判断の校正データ範囲と版を分けること。
- **受入条件**: 生成規則と主分母が一意で、結果を見てから除外が増えないこと。

## Q5（B4 / MQ4、標本単位）復元 iid と unique-law n をどう統計的に整合させるか

- v2 §6 の「各 draw で1 family」とパック §5 の「重複 law は n に数えない」をどちらの主標本単位にするか。登録分布の estimand を変えないなら、重複 draw/cluster の扱いと推定量、サンプリング停止規則、重複 law の重みを固定すること。unique 無復元に切り替えるなら inclusion probability と母集団上の主張範囲を変更すること。
- G1/G2 の共通親 law cluster と4族テンプレート層の推定・区間・bootstrap unit も明示すること。
- **受入条件**: 非一様な生成確率でも登録分布に対する推定量が正しく解釈できること。

## Q6（B4 / MQ4、検出力と経路）7対照・2 gate・G1/G2 の80% power はどう確保するか

- §5 の `n_binary` / `n_aulc` は「2 gate」だけを Bonferroni 処理するが、7対照の最強事後選択、G1/G2、family cluster、AND 連結に対しどこまで同時誤差/検出力を保証するのか。数式・実際の採用/棄却手順・max-T の標本再抽出単位・CIの片/両側・代替仮説を揃えてほしい。
- 4族内テンプレート重み、各パラメータ/長さ/語彙の確率、`N_unique` 算出法、`cost_cap`、`n_min_descriptive` と有限 frame の完全列挙判定、CAL による1回改訂の条件/範囲/判断者を CAL プロトコルに先立ち確定候補として提示してほしい。
- **受入条件**: CAL 実測入力を与えたとき `STATISTICAL / FINITE_DESCRIPTIVE / STOP_UNKNOWN` が機械的・一意に決まること。不十分な power の場合も弱い対照へ変更しない。

## Q7（B5、帰属）機構説明・等価性・小効果・不精確の優先順位は

- §6 K2 の「FULL−REC の両側同時区間が ±0.05 内」を、性能等価性の結論として限定するか、「再符号化で説明できる」という因果帰属に必要な追加比較/仮定を指定するか。
- K3 の `|Δ|<0.05` かつ成功率差<5pp の点推定判定は、広い区間が0と±δを跨ぐ INCONCLUSIVE と重なる。カテゴリの優先順位、差が統計的に負のときの扱い、B時点成績/区間の family 集約方法を指定すること。
- **受入条件**: 同一データに二つの排他的 outcome label が付かず、単なる差の不検出を同等や機構同定としないこと。

## Q8（B6、履歴と封印）CAL 前の完全な決定可能性・アクセス証拠をどう示すか

- §6〜§7 の manifest/schema に、生成分布の版、乱数源・tag発行、split の親 law cluster、デモ digest、費用、snapshot、分析コード、役割別 read path、hash 計算法/アルゴリズム、失敗時 INVALID/STOP の監査ログを必須フィールドとして型定義できるか。
- CAL プロトコル承認→別 CAL GO→CAL→事前登録凍結→別実装/正式評価 GO の各段で、Owner が Issue #195 に何を記録し、どの SHA/digest を参照し、何を変更可能とするかを決定表にしてほしい。
- **受入条件**: 現時点で未凍結の数値候補と、CAL前に変更してはいけない決定規則を区別でき、第三者が receipt と read path を追跡できること。

## 再提出の境界

上記の答えは本体とパックの修正文書として示し、exact-head の対応表を添えてほしい。Owner採用済みの8 arm・REC・G3分離・K0三段・強い対照・CALと凍結の分離を理由なく再議論しない。**校正、世界/学習器/評価器の実装、正式採点、結果認定、PR #194 の Draft解除・マージのいずれも行わない。**
