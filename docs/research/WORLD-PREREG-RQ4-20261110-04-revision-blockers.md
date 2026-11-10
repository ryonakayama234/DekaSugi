# WORLD-PREREG-RQ4-20261110-04 — 改訂仕様パックの残存 blocking 逆質問

id: WORLD-PREREG-RQ4-20261110-04
status: research_lead_questions / blocking / NOT_FROZEN / NO_CAL_GO / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration, research-lead, review-questions, docs-only, no-execution
author_role: Research Lead (ChatGPT)
parent_review: [WORLD-PREREG-R4-20261110-04](WORLD-PREREG-R4-20261110-04-lead-revised-specpack-review.md)
target: [Draft PR #194, head 64b3f9e](https://github.com/ryonakayama234/DekaSugi/pull/194)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **趣旨**: RQ3 Q1〜Q8 に対する Owner 採用の再投票ではない。改訂版 -02 の本文で実際に未整合・未定義となっている契約を質問する。回答は項目ごとに AGREE/REVISE/DISAGREE、改訂する節、機械的な決定規則、例、反証/UNKNOWN、非変更範囲を添えてほしい。本票によって CAL プロトコル承認、CAL 実施、事前登録凍結、実装、正式評価、main merge は発生しない。

## Q1（B1/B3）π(H0) が同じ2 law を、いつ何によって識別できるか

改訂 §1 のアンカー例は、同一初期 buffer「ABAB」と同一デモから、観測により L1 と L2 の正しい行動が分かれると主張する。しかし決定的 Editor の law 非依存の状態遷移では、同一公開状態で同じ行動を選べば次の観測も同一である。L1/L2 の違いが **行動選択前** にどう公開されるのか（TRAIN の trial 後成功/失敗、EVAL のデモ、law に依存する状態遷移、その他）を明記してほしい。

- TRAIN の複数 trial を跨ぐ公表 feedback で識別できても、EVAL では feedback は監査専用なので、EVAL の条件付き方策の証人と同一視できない。
- 最低限、合法行動列、デモ3対、各 law の公開 `π(H_t)`、target（監査側のみ）、成功/失敗判定、分岐時刻を持つ小さな**実際の証人表**を出してほしい。単に「アンカーが現れたら」では両 law の観測を区別したことにならない。
- **PASS 条件**: K0-a の「同一 `π(H0)`、共通 open-loop 不在、合法な条件付き方策が双方に成功」の同時成立を、採点時に許された公開情報だけで論証できること。成立しない場合は STOP/UNKNOWN と認定上限を改訂する。

## Q2（B2）経験由来 BRANCH と空 snapshot の E/H+ は同じ AST を生成できるか

- §2 は BRANCH の3スロットに経験由来記号を要求し、E は空 snapshot の閉包と定義する。経験を持たない H+ がこれらの枝/述語をどう表現・列挙するか。E を「純構文の全候補」とするなら、経験由来という**構築・USE 制限**をどの arm/phase に適用するかを分けること。
- typed AST の完全 grammar（observable feature names、ATOM の引数、型・scope、BIND alpha-normalization、COMPARE operand、branch guard、失敗処理、constructor の完全性）、辞書式の total order と重複処理、有限/UNKNOWN判定を出してほしい。
- FIXED-IF の「構築なし」対「FULL と同じ述語発見」、PRED-ONLY の first-order macro/use と制御流の禁止、REC の `k` と policy の完全形も arm × constructor × USE で統一すること。
- **PASS 条件**: 同じ抽象 AST が FULL/H+/RANK-ONLY/FIXED-IF/PRED-ONLY のどこに属するか、経験なし・経験ありの双方で機械的に決められ、「同一空間」の宣言に循環論法がないこと。

## Q3（B4）PPS 無復元の抽出と推定量・信頼区間は具体的に何か

- §5 の `π_l∝p_l` を固定 n に正規化したとき `π_l>1` となる law があればどう扱うか。実際の sampling algorithm、certainty units、1次/2次包含確率、抽出不可能条件、TRAIN/CAL/holdout 分割後の eligible support を明記すること。
- §5 の `p_l/π_l` を正規化する**Hájek 比率型**と**HT 合計型**を区別し、登録分布の estimand と推定量、bias/interval の保証範囲を一意にすること。
- 非復元・不等確率の design に対して、CAL paired SD と discordance、law cluster bootstrap、max-T の標本再抽出単位・重み・分散推定、有限母集団補正をどう整合させるか。G1/G2 は同じ law 親 cluster として扱うこと。
- **PASS 条件**: 非一様 p_l の小さな有限母集団でも、n・包含確率・推定量・route・区間を一意に算出できる。

## Q4（B4）AND 全体80% power の下限を正しい式へ修正できるか

§5 の `P(全ゲート成功) >= ∏P(個別成功)` は無条件には偽である。各ゲート 0.9、3失敗が互いに排反で各確率0.1なら同時成功は0.7であり、積0.729を下回る。

- 有効な保守下界（union bound 等）か、相関構造を保存した joint-power 算法（max-T と7対照の最強事後選択を含む）を採用し、その条件、CAL への依存、再現可能な n 算出手順を明記すること。
- `n_required = max(n_aulc,n_g1,n_g2)` によって**全ゲート同時** power 0.80 を証明すること。不可能なら n を増やす/route STOP_UNKNOWN にする規則を固定すること。
- `N_unique` と実際に抽出可能な holdout law 数、cost_cap と全 arm の費用、有限 frame の判定、STATISTICAL/FINITE_DESCRIPTIVE/STOP_UNKNOWN の優先順位を CAL 前に機械化すること。
- **PASS 条件**: 保守下界または joint-power 推定が、定めた仮定の下で真に0.80以上であるときだけ STATISTICAL を許可する。弱い対照への変更を禁止したままにする。

## Q5（B5）結果の outcome 分割は網羅的か、INVALID は何種類か

- AULC 同時区間 `[-0.02,+0.07]` は負でも、±0.15を跨ぐ INCONCLUSIVE でも、±0.05に全包含する「小さい」でもなく、正ゲートも通らない。**この結果のラベルと判定規則**を示してほしい。区間が正側にあっても効果量 `δ=0.15` 未達のケースも扱うこと。
- 型不一致等による「課金 no-op（§2 の INVALID action）」と K4 汚染による「INVALID family / run STOP（§6）」を別 event kind にすること。否定・欠測・棄権・timeout と主分母の関係も指定すること。
- **PASS 条件**: 任意の推定値・CI・K4状態に一意かつ排他的な outcome label が与えられ、分類不能な空白がないこと。

## Q6（B6）数値/文書の改訂可能時点と v2 の残存条項の衝突を解消できるか

- 改訂 §7 は「数値候補は CAL プロトコル承認までに確定」とするが、置換**対象外**の v2 §5 は「閾値候補は CAL で一度だけ改訂可」、v2 §7 も「CAL による文書改訂1回」を存続させる。このどちらを最終規則とするか §0.1 に追加し、承認前後/CAL 前後/事前登録凍結前後の変更可能フィールドを完全な表にすること。
- CAL の paired SD/discordance から算出する `n_required` や route、生成器 grid/digest は「数値候補の改訂」なのか「承認済みアルゴリズムの出力」なのか分けること。
- CAL 中の G2 長13〜16容量診断は改訂 §4 の CAL 初期長4〜12の例外として扱うか明記すること。
- **PASS 条件**: 修正のタイミングと内容を他の条項と矛盾せず監査可能にできる。

## Q7（B1/B3/B6）合法性・封印・分母の非循環性

- v2 §1 が実際には「11操作の契約を**後で全列挙する**」という TODO のままである。reset/observe/legal_actions/step、11操作の前提と効果、no-op/INVALID の境界、completion/timeout/abort、探索上限と証人対象の演算を仕様表として示すこと。
- K0 は CAL のみなのに「oracle support 全件」を列挙する際、未公開 holdout instance/target/score を読まないことを、生成器の抽象 support と sealed split の読み権限で示すこと。
- 生成後に識別不能な law が出たとき、§4 の分母保存と §6 K0-b の family 不採用を phase ごとに整理し、構造的除外の事後追加を禁止したままにすること。
- **PASS 条件**: 証人・K0・監査 receipt・CAL と EVAL の分離が同じ状態機械と分母規則から導けること。

## 再提出条件

改訂先の節と変更されない節の対応表を付け、**その版の exact head** について Lead に再審査を求めること。Owner 採用済みの主張B、8 arm＋REC、G3 分離、K0三段、同予算比較、CAL／凍結の段階分離、数値未凍結を維持する。未許可の CAL/実装/実験・PR #194 Draft解除・既存PRマージは行わない。
