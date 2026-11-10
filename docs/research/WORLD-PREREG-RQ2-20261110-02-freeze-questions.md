# WORLD-PREREG-RQ2-20261110-02 — Research Leadから監督者への v2 再審査・凍結前逆質問

id: WORLD-PREREG-RQ2-20261110-02
status: research_lead_questions / awaiting_supervisor_reply / docs_only / NOT_FROZEN / NOT_CALIBRATED / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration, review-questions, no-execution
author_role: Research Lead (ChatGPT)
parent_response: [WORLD-PREREG-R2-20261110-02](WORLD-PREREG-R2-20261110-02-lead-rereview.md)
draft_target: [Draft PR #194 v2 / head a67e0dbb](https://github.com/ryonakayama234/DekaSugi/pull/194)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> 本文は質問票であり、Ownerが既に採用した「8 arm＋REC」「CAL分散→固定power規則→統計/有限集合切替」「v2→Lead再審査→設計合意候補→別CAL GO」を覆す提案ではない。全問は **凍結前の未確定な運用契約**を問うもので、校正、実装、学習、評価、凍結、マージの許可ではない。

監督者は各問に **AGREE / REVISE / DISAGREE、理由、v2の修正節、機械可読化対象、反証条件** を付して回答してほしい。Q1〜Q7は B1〜B6 を実際に PASS にするための blocking、Q8 は手続き整合の blocking とする。

## Q1（B1/B4）公開デモの料金と単一予算軸

v2 §2 は別インスタンスの公開デモ対を「経験予算に課金」とし、§5 は原始操作呼出の累積 b だけを主要予算軸とする。記録済みのデモ対は原始操作を実行していない。この場合、(A) デモ1対ごとに事前固定の b 相当コストを課す、(B) デモは arm 共通の独立した数量制限に置き、b は実原始呼出に限る、のどちらを採るか。数・提示時点・追加取得可否・評価フェーズでの公開範囲も固定できるか。

## Q2（B1/B3）公開同値・ID漏洩と分岐証人

task tag の同一法則内再使用と異法則間再使用の規則、生成seedとの独立性をどう保証するか。デモ内容・tag・初期観測・試行結果・成功フィードバックが同じ「公開履歴同値類」を具体的に定義してほしい。K0-aで共通open-loopが存在しない証人と、K0-bで行動前に必要情報が到達する証人を同時にどう認定するか。どの時点で識別不能としてSTOPか、UNKNOWNか。

## Q3（B2/B5）完全 grammar と H+ の到達可能性

branch-construct が作る AST の node type と分岐 evaluator の guard/dispatch 意味論の対応、全 node の arity/型/binding/scope/可用定数/深さ/prior/列挙順序、空 snapshot での不可呼出試験を表にできるか。H+ は FULL が後で獲得する二階 AST を同じ制約下で原理的に構成できるのか。できない場合は「同一候補空間」の記述をどこまで撤回するか。PRED-ONLY の二階 USE 禁止も明示できるか。

## Q4（B4 / MQ4）母集団・抽出と重複

評価可能な意味 law の正規形と unique ID、4上位族の下のテンプレート重みと生成分布、法則の有限/無限性、TRAIN/CAL/holdout 間の親法則連結成分隔離、G1/G2 関連 cluster をどう固定するか。復元抽出 iid と、重複なし有限集合無復元抽出のどちらを採るか。同一 law 再出現を n の何単位として数え、共有テンプレートによる相関/外挿限界をどう報告するか。原則 iid に同意するが、条件付き分布外への一般化まで認定しない線引きに同意するか。

## Q5（B4 / MQ4）事前固定 power と route 切替の決定表

CAL前に主AULC・B時点ゲートの効果量代替仮説、paired SD/discordance からの保守的分散推定、多重比較調整（7対照の最強事後選択・G1/G2・ANDゲート）、片側α=0.025/80% powerの n 算出を決定式/疑似コードにできるか。計算された n_required と独立lawの可用数 N、許容総コスト、全件列挙完全性をどの順番で比較し、統計路線/有限集合記述路線/STOP-UNKNOWNに機械分岐するか。満たせない場合も対照を弱めない規則を維持するか。

## Q6（B3/B4）AULCの分母とK0-c飽和判定

等間隔checkpointの台形面積を B で割るのか、B+1点の算術平均を採るのか。0〜Bの端点・補間・打切り・欠測・凍結snapshotの評価費をどう処理するか。K0-cで強対照が「必要な上乗せ余地なし」と判定する際、理論的上界とCALの不確かな点推定をどう分けるか。H、max nodes、探索完備性、UNKNOWNのトリガをどう決めるか。

## Q7（B5/B6）キル条件と監査receipt

K1の行動差（確率的policyの場合も）、K2の等価性マージン/信頼区間、K3の実用的小幅・負/不精確、K4のINVALIDの影響範囲と再採点禁止を数値あるいは決定式で定められるか。各ARMの許容構築/USE/費用、CAL・holdout隔離、manifest・生成器・分析・snapshotのsource-first digest とアクセス表を、どの証拠で第三者が確認するか。

## Q8（手続き）「凍結」と校正の順序

v2 §10の「Ownerによる凍結判断→校正」と§7の「校正後に決めた n/閾値を含む凍結receipt」は、凍結という語の指す対象が異なるように読める。前者は CALプロトコルの設計承認（CAL自体は別 Owner GO）、後者は CAL結果に基づく最終事前登録凍結、と明確に二分してよいか。決定記録をどの文書とSHAで残すか。PR #194/#196 の Draft 維持、未許可の実装/実験を当然の前提とする。

## 回答後に要求する区分

- **合意済み骨格**: Ownerの3採用点、K0三段、認定3段、G3分離は再投票しない。
- **未合意/凍結阻止**: 上記 Q1〜Q8 の具体契約と B1〜B6 の完全性。
- **次の Owner 判断**: この審査の採用可否と、後日準備されるCALプロトコルおよびCAL GO。数値の凍結は CAL後に別途判断。
- **証拠境界**: 設計上の「合意候補」から「校正済み」「事前登録凍結済み」「実験実行可」を推論しない。
