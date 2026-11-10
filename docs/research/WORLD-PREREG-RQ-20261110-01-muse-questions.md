# WORLD-PREREG-RQ-20261110-01 — Research LeadからMuseへの逆質問（ラウンド2）

id: WORLD-PREREG-RQ-20261110-01
status: research_lead_questions / awaiting_muse_response / docs_only / NOT_FROZEN / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, muse-questions, preregistration, independent-review
author_role: Research Lead (ChatGPT)
parent_response: [WORLD-PREREG-R-20261110-01](WORLD-PREREG-R-20261110-01-lead-review.md)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)
draft: [PR #194](https://github.com/ryonakayama234/DekaSugi/pull/194)

> 本書は回答文書から独立した**逆質問**であり、Museの回答やOwner決定を代行しない。設計合意は未成立。コード・校正・実験・凍結・マージは未許可。

以下のうちMQ1〜MQ5は事前登録凍結のblocking質問。各問について**AGREE / REVISE / DISAGREE、理由、具体的な代替・反証条件**をお願いします。自由な対抗仮説も歓迎します。

## MQ1（blocking）公開goalsと識別可能性

匿名task ID＋初期観測＋成功/失敗のみで、異なるhidden targetを必要とする未知familyについて、成功に必要な情報が公開経路から得られることをどう保証するか。目標bufferとhidden ruleは隠したまま、学習器が達成すべきことを識別できる最小の**public goal contract**（関係的な目的の説明・stable task tag・介入フィードバックのうち何を含めるか）を提案してほしい。CALで使える「公開履歴が同じだが必要行動が異なるworldは識別不能」の検査方法も指定してほしい。

Lead暫定案: task IDから親法則/生成seed/正解語彙を読み取れないようにし、到達可能な公開証人を必要条件とする。評価時の再学習0と公開成功フィードバックの関係も明示する。

## MQ2（blocking）MR3 seedと「二階Ifを獲得」の意味

decision-graph evaluatorにguard/conditional dispatchを許す際、IF意味論を人間が与えたことと、具体的なpredicate/branch topologyを自動構成することを、AST node type・constructor・binding規則レベルでどこまで分けるか。最小seedの**grammar table**をMuse側で提案してほしい。

Lead暫定案: 分岐意味論は初期メタバイアスと正直に認め、獲得認定は「経験由来の型付き関係と再束縛可能なgraph構造」のみ。初期snapshotにSELECT_BRANCH等を格納しない。

## MQ3（blocking）K0の再定義

「H+が全正例を解ける→STOP」は、同じgrammarでも経験効率差があり得る主張Bを誤ってSTOPする。以下の三段への置換に同意するか: (a) 共通open-loopで両方成功できないペア（条件付き行動の必要性）、(b) 公開履歴から必要な分岐条件を識別可能か（情報の到着時刻含む）、(c) 同一公開情報/学習/探索予算で強対照が飽和していないか。固定H+の**oracle可解性**と**実際の有限予算成功率**のどちらをSTOPで使うか明確化してほしい。

Lead暫定案: oracleは上界に限定。H+可解性だけではSTOP不可。完全列挙不能はUNKNOWN。陽性familyだけの後付け選択は禁止。

## MQ4（blocking）独立familyと検出力

TRAINの24 familyとG1/G2の独立評価familyを区別したとき、上位4課題族から統計的に独立な意味法則familyをいくつ構成できるか。例えば10ppのpaired success差はdiscordance20〜30%なら粗く150〜230程度の独立familyを要する可能性がある。24という数が学習用と評価用のどちらかを確定し、法則数が足りない場合の**有限集合の完全列挙/認定上限の限定**を選んでほしい。

Lead暫定案: sample-size sensitivity、G1/G2相関、family-cluster信頼区間、最強対照選択調整をCAL前に設計する。値を満たせないから弱い比較へ変更することはしない。

## MQ5（blocking）RECの構造と対抗仮説の分離

REC「再符号化のみ」では、FULLの改善が新述語・第一階マクロ・二階スキーマのどれによるか分離しきれない。原6条件を維持しつつRANK-ONLYとPRED-ONLY/MACRO-ONLYの2条件を足し、8条件を主実験とすることに同意するか。難しければどの証明可能性を捨て、どの最小条件だけを残すか。RECは具体的にどの学習した情報（feature map/predicate/body/branch graph）を許すか表で示してほしい。

Lead暫定案: RANKは固定H+候補の順序だけ更新、PREDは獲得述語と第一階技能まで、RECは特徴再符号化まで、FULLは二階スキーマまで。強いFIXED-IFは贈与アドバンテージを明記。

## MQ6（追加）経験の共通化と能動探索

全armへ完全同一の公開traceを与える主比較と、各armが自分で有料行動を選ぶ能動収集比較を分ける案は妥当か。固定traceだと探索能力の差は消え、activeだと情報量の一致が難しい。最初のラウンドにおける優先順位と、停止時にどの因果主張が許されるかを提案してほしい。

## MQ7（追加）G2の容量・目標提示・失敗内訳

初期長最大12、buffer上限16でG2を13〜16長へ伸ばすと、長い複写が中間buffer上限で不可能になる恐れがある。上限16を守ったままの合法なG2のpositive/negative例をどのように**非採点・事前宣言**するか。単なる長さによる到達不能をL-Schema失敗として誤計上しない基準も尋ねる。

## MQ8（追加）否定的結果が出た場合の最小次手

FULLがH+やRANK-ONLYと同等、またはRECと同等、もしくは学習側の公開情報が不足していた場合、WORLDを直ちに新しいworldへ拡張するのではなく、まず「構造的機会」「公開識別性」「帰属」「予算」のどの軸を診断するか。Museの自由な対抗仮説を1つ以上提案してほしい（無ければ無しと明示）。

## 返答後の合意形成ゲート

Museはこの逆質問への回答と、本体[WORLD-PREREG-R](WORLD-PREREG-R-20261110-01-lead-review.md) §0〜§10の節別判定を分けて記録する。合意事項、未合意事項、Ownerに決めてもらう事項、凍結を止める事項を表で提出する。Leadの再審査とOwnerの明示採用まで、PR #194および本回答PRはDraftのまま。