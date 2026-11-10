# WORLD-PREREG-R-20261110-01 — Research Leadによる事前登録ドラフト審査（ラウンド2）

id: WORLD-PREREG-R-20261110-01
status: research_lead_review / revise_before_freeze / docs_only / NOT_FROZEN / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration-review, research-lead, methods, no-execution
author_role: Research Lead (ChatGPT)
review_target: [WORLD-PREREG-DRAFT-20261110-01 / Draft PR #194](https://github.com/ryonakayama234/DekaSugi/pull/194)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)
reverse_questions: [WORLD-PREREG-RQ-20261110-01](WORLD-PREREG-RQ-20261110-01-muse-questions.md)

> **権限境界**: 本文はドラフトへの項目別審査と修正提案である。凍結済みの研究設計基礎 [WORLD-R-20261110-01](WORLD-R-20261110-01-lead-response.md) とOwnerのMR1/MR3批准を変更しない。本回答の提出は、事前登録の凍結・校正実施・世界/学習器/評価器の実装・学習・採点・実験実行・実PC操作ログ収集・mainマージの許可ではない。Museの同意とOwnerの決定は未取得。

## 0. 総評、参照した事実、認定の境界

**総合判定: REVISE（条件付き支持）。** 主張Bを「同一meta-runtime・同等の公開情報と学習/探索資源における未知familyの経験効率改善」とし、A（有限H0に対する意味クラス拡張）を補助とする方針は支持する。一方、現行のK0、課題識別可能性、対照の帰属、効果量の判定と標本設計は、このまま凍結できない。

参照したプロジェクト証拠（研究結果と提案を混同しない）:
- 本回答の基点はmain commit [ae44f126](https://github.com/ryonakayama234/DekaSugi/commit/ae44f126e36410b98dc5ee450a05348c9f11105b)。[README](../../README.md)、[INDEX](../INDEX.md)、[WORLD-R](WORLD-R-20261110-01-lead-response.md)、[Ownerの採用記録](https://github.com/ryonakayama234/DekaSugi/pull/192#issuecomment-6758374273)、[ドラフトPR #194](https://github.com/ryonakayama234/DekaSugi/pull/194)、[追跡Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)を照合。PR #194のドラフト文書はmainにはまだないため、mainの相対リンクとして参照しない。
- 実験AのG6-4は448/448 receiptを採点済みだが、wall中央値0.0874–0.0877秒で優位なし、C_lifeはUNMEASURED、M_useはNOT_CERTIFIED。[Issue #146 G6-4](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6754631517)。本研究の成績ではない。
- 公開適応的質問の厳密利得ゼロでSTOPした先例は[Issue #166](https://github.com/ryonakayama234/DekaSugi/issues/166)。表現修復/観測識別性の事前点検は[Issue #168](https://github.com/ryonakayama234/DekaSugi/issues/168)のR0-A〜Eとも整合。旧実験の陽性/陰性をWORLDに移植しない。
- [PR #192](https://github.com/ryonakayama234/DekaSugi/pull/192)と[PR #193](https://github.com/ryonakayama234/DekaSugi/pull/193)の独立レビューは、K0で「固定H+で表現・可解」と「同予算で獲得効率の改善機会なし」を混同しないよう指摘している。この留保をラウンド2では解消する必要がある。

### 節ごとの判定

| 節 | 判定 | 要旨 |
|---|---|---|
| §0 主張・認定上限 | **AGREE** | 認定Bを主とし、Aを補助に限定 |
| §1 世界v0 | **REVISE** | G2の長さ/容量、合法性、プログラム展開ホライズンを確定 |
| §2 課題族・封印 | **REVISE** | generator階層・公開ゴール・task IDのリーク、公共観測での識別可能性を検査 |
| §3 比較arm | **REVISE** | 6 armを必須候補として保持しRECを採用。rank-only等を追加し帰属を補強 |
| §4 seed在庫 | **REVISE** | runtimeの構文/コンストラクタが完成Ifを暗に供与していないか検査 |
| §5 指標・閾値 | **REVISE** | AULCの予算軸、family単位推定、検出力、複数比較を明文化 |
| §6 K0診断 | **REVISE** | 現行STOPは主張Bの機会を誤消去するため修正必須 |
| §7 キル条件 | **REVISE** | TRUE NULLと検出力不足、OFF同一挙動、等価性を分離 |
| §8 ログ | **REVISE** | evalを隔離したcheckpoint/公開情報/コスト会計/生成履歴を強化 |
| §9 Owner判断点 | **REVISE** | 4点への下記推奨で回答 |
| §10 範囲外 | **AGREE** | 未凍結・非実装・非実行を維持 |

## 1. §0 主張と認定上限 — AGREE

認定上限Bを支持する。固定の汎用graph evaluatorがある以上、「Ifという計算原理をゼロから発明した」「数学的に計算可能な範囲を拡張した」とは言わない。主張すべきは、学習履歴から獲得し、再束縛可能な構造が未見の意味familyで行動と経験効率を改善したこと。

認定を3段に切る: (i) 学習由来の新記号・依存系譜と実行可能性、(ii) 同一公開状態・固定snapshotでUSE ON/OFFの合法な行動差、(iii) 強い対照を上回る未知familyでの有効性。いずれか未成立なら下位の主張に留める。G1/G2成功のみで「Editor→Form転移」は認定しない。

## 2. §1 世界v0 — REVISE

4記号、初期buffer長4〜12、最大16、11種の原子行動、完全観測・決定論、独立verifierの枠組みには賛成。ただし以下は凍結前に機械可読契約へ固定する。
- 各原子行動の事前条件・無効時のno-op/INVALID・selection/clipboardの境界・容量・undoなし・終了規則を全列挙。no-opを合法と扱うなら、無限no-opを許さない原始呼出課金とホライズンが必須。
- G2はTRAIN最大長超えが必要だが、v0最大16の下では13〜16への外挿など狭い条件になり、COPY/PASTEが途中で容量上限を越えうる。各長さの可解性と最短経路の上限を非採点で確認。解けない場合は値だけを後から動かさず、Owner判断の設計版更新を行う。
- G1の「未見文字名」は単なるA/B/C/Dの置換と区別し、新しい不透明トークン名への一対一改名を事前定義。型付きINSERT(symbol)と観測側は名称ハードコードをしない。同形の文字改名だけでは新世界転移を示さない。
- 11種は操作**種**であり、INSERT(symbol)の記号インスタンスを含む実際の分岐数とは別に監査する。

## 3. §2 課題族と封印 — REVISE

4族と観測依存の対照ペアを支持するが、三項組合せ（述語×分岐先×対象）だけでは足りない。generatorの親法則・操作役割同型・課題テンプレート・語彙/長さ分布・random seedの系列で依存グラフを作り、同じ親法則の派生物がtrainとholdoutを跨がないよう、**意味生成法則の連結成分単位**で分割する。G1文字改名とG2長さの同一family再利用は独立な2標本とみなさず、関連性を記帳する。少数の親テンプレートから大量の事例を作っても独立family数は増えない。

goal leakageより前段の**goal identifiability（課題同定可能性）**が未確定。匿名task ID・初期観測・成功/失敗のみで、異なる隠れた目標を一意に同定できるとは限らない。同一の公開履歴で異なる正解行動を要求するworldが存在し、予算内の公開介入でも区別できないなら、どの学習器にも成功保証はない。逆にtask IDが規則の安定した符号ならLOOKUPが解ける。次を指定する:
1. 「公開goal contract」と「hidden target値」を分ける。何を成功と見なすかに必要な公開の関係的仕様は必要最小限にし、真のtarget buffer/hidden rule/正解列はverifierのみ。
2. task IDは分割・生成規則・真値のハッシュや連番を含まない不透明な識別子とする。同一/新規IDの反復範囲とtraining/evaluationでの分布を固定し、ID-onlyの予測対照を置く。
3. USEで凍結snapshotを使用する場合、評価中の成功/失敗は完了後の監査専用にし、同じholdoutの繰返し回答を再学習へ戻さない。学習適応を評価する別試験は新しい事前登録が必要。
4. 対照ペアの証人は「同一公開課題条件で、任意の共通open-loop行動列が同時成功できない」と「公開観測で条件分岐できる」をセットで確かめる。限られたホライズン内の不在証明はその範囲に限定。
5. 生成後に「陽性family」だけを選ぶのは禁止。陰性・不可能・識別不能・欠測を予め割り当てた分母と原因に残す。校正と評価の生成系列は別に封印する。

## 4. §3 比較arm — REVISE

**FULL / OFF / FIXED-IF / LOOKUP / H+ / REC の6条件は維持し、RECは採用。だが、これだけで高階スキーマ固有の帰属が完結するとはしない。**

- FULL: 分節・anti-unification・述語・技能・二階スキーマの候補生成・昇格を許す。
- OFF: FULLの同一訓練済snapshotで、獲得物USEを評価時のみマスクする。学習や前処理を別実装にせず、マスク以外の同一性をdigestで確認する。
- FIXED-IF: 事前の完成スキーマを贈与した**強い対照**。seedの非対称性を開示し、FULLと同じ初期seedだとは記さない。受け取る条件語彙/記号発見・bindingと探索資源はできるだけ同じにする。
- LOOKUP: exact/nearestの距離関数・検索候補容量・失敗時のabstain/探索方針を凍結し、同じ公開学習履歴のみで動かす。
- H+: 同じgraph runtime/実行可能候補空間と同予算で探索。計算無制限oracleを主成績に含めない。静的grammarに情報上の不足を人工的に作らない。
- REC: 観測の再符号化・同じ下位予測学習を許すが、実行可能な新述語と二階スキーマを作らない条件として明記。単なる特徴数の縮小ではなく、R（feature mapping）の効果を観測する。

**追加を推奨（主張Bの帰属に重要）**:
- C3 / RANK-ONLY: 同じ固定H+候補を持ち、公開履歴から候補探索の優先順位だけ学習する。これがないとFULLの改善が探索の優先順位学習に由来する可能性を排除できない。
- PRED-ONLY / MACRO-ONLY: FULLと同じ獲得述語・第一階技能・再符号化を許すが、再束縛可能な**二階スキーマのみ**禁止する。これがないとFULL対RECの差を「述語の発見」と「二階スキーマの構築」に分解できない。C4固定マクロ対照の機能も兼ねる設計を検討する。

推奨形は**原6条件＋RANK-ONLY＋PRED-ONLY（計8条件）**。実装負荷のため6条件に留める場合も、RANK/PRED固有の反証を欠くことを事前宣言し、L-Schemaの機構帰属を「示唆」に格下げする。数値認定を強めるために低予算の対照を脱落させない。

評価の公正性は、公開経験を共通の事前割付traceとしてリプレイすること（主比較）、各armの合法な能動探索を比較すること（独立した副比較）を分ける。後者は情報量が同じとは限らないため獲得成功フィードバック数・原始呼出・問い合わせ・候補評価・CPU/wall・保存量を別々に計上する。学習費とUSE費も分離し、固定IFの人手設計/先渡しは明記する。

因果比較表:
- FULL > OFF かつUSEの行動差あり: 獲得物の実利用寄与。
- FULL > REC だけ: 再符号化**以外の何か**が寄与。述語とスキーマのどちらかは未確定。
- FULL > PRED-ONLY: 二階スキーマ使用の増分の候補（同一特徴・同一予算を要確認）。
- FULL > RANK-ONLY / H+ / FIXED-IF / LOOKUP: 固定表現・検索・優先順位だけでは説明しにくい経験効率改善。
- 差が「非有意」: 同等の証明ではない。等価性マージンと十分な精度がある場合のみ機構同等と評価する。

## 5. §4 seed在庫 — REVISE

Owner批准MR3に従い、decision-graph評価、変数束縛、比較（等値・順序）、原子行動に限る方向は支持。現記述の「全量宣言」は**機能名の列挙であり構文と学習可能な仮説空間の全量宣言にはまだ不足**する。

追加する監査表: (i) 全node type、arity、AST constructor、可用graph topologyと深度、(ii) 比較の入力型・束縛規則、(iii) graph evaluator内のguard/branch/dispatchの有無、(iv) 特定の状態・文字・roleに結びついた初期定数と特徴量、(v) 記号/技能の生成operator、事前のpriorと探索順序、(vi) evaluatorとlearnerが共有するコード/辞書とread path。

反証試験は「学習を行わない空のsnapshotで、完成済みIf/SELECT_BRANCHや意味述語を単なる名前参照で呼べないか」。ただし一般decision graphが条件分岐を実行できるなら**条件分岐の実行意味論自体は初期バイアス**である。そこで獲得と呼べるのはgraphの有用な構築/再束縛の発見であり、原始If意味論の創出ではない。この区別を認定本文へ維持する。

## 6. §5 測定・閾値・予算 — REVISE

### 6.1 AULCと予算軸

Bを「episode数×原始呼出」の曖昧な換算単位にしない。主要な学習軸を1つ選ぶ（推奨: 有料原始操作呼出の累積 b、必要ならepisodic checkpointを明示）。他の経験件数・問い合わせ・候補評価・CPU/wall/RSS・学習準備費は別ベクトルで制限と表示。各snapshotが未見familyに与える成功率を s_f(b) とし、AULC_f = [Σ_{b=0}^B s_f(b)]/(B+1) または凍結済みの等間隔checkpoint台形積分とし、分母・補間・棄権・打切り・再現用乱数種を指定する。評価familyのscoreは学習側へ一切戻さない。

「familyあたり200 episode相当」「TRAIN 24 family」は**工学的校正候補**に過ぎない。仮に全familyを各armで200episode走らせると6条件×24×200=28,800 episode（8条件なら38,400）相当になるが、ステップ・探索・checkpoint費は別であり、実費を保証する算術ではない。訓練族24と**独立評価族のn**は別物である。

### 6.2 family単位の検出力

主要効果は同じ独立評価family上でのペア差 Δ_f = AULC_f(FULL) − AULC_f(control)、ならびに予算B時点の成功率差。固定対照5〜7種類のうち最高性能を事後的に選ぶため、最強対照との比較は同一データへの選択を考慮した同時信頼区間（例: family単位max-T bootstrap）または全対照に対する階層的検定を事前指定する。独立単位は匿名episodeでなく生成法則family。同一familyの複数例、複数checkpoint、seed反復はcluster内で扱う。

**規模感の算例（実測でない仮定）**: paired binary差が10pp、discordant family比率20%なら、近似Var(Δ_f)=0.20−0.10²=0.19。片側α=0.025・power=80%、正規近似で必要nは約149独立family。discordance30%なら約227。24独立familyなら差の標準誤差は約0.089（20%仮定）で、10pp判定には弱い。AULC差0.15でpaired SD=0.25なら約22、SD=0.40なら約56という別の粗い算例になる。これらは**計画用感度分析**であり、現行データから得た推定値ではない。複数対照・2ゲート・family共有構造・非正規性を考慮すれば必要量は増えうる。

したがって、独立法則が十分用意できるならG1・G2それぞれ150〜230程度を一つの検出力検討レンジとし、共通familyは階層化して計上する。ただし4つの上位テンプレートしか独立の生成法則がないなら、150個の見かけのseedを作ってもn=150とは言えない。この場合は有限法則集合の完全列挙による**その集合に限定した記述的推論**か、独立生成機構の拡張を再設計する。無理に統計的な一般化主張をしない。

### 6.3 判定規則と校正プロトコル

G1 90%、G2 80%、最強対照+10pp、AULC +0.15は当面の**候補値**として保持。ただし達成率とAULCは異なる主張なので、「AULCを第一評価指標、B時点のG1/G2達成率と対照差を追加のANDゲート」と階層固定する。効果量下限と不確実性のどちらを要求するか（例: 点推定が+10pp/+0.15を満たし、family clusterでの同時95%区間下限が0を超える）は別途事前登録し、探索結果後に選び直さない。FULLと対照の全成績、信頼区間、NULL/NEGATIVEを表示する。

非採点校正は**評価用の法則/seed/receipt/hidden scoreを使わない**。事前に隔離したCAL familyだけで可解性・強対照の飽和・費用分布・分散感度・目標識別性を測る。CALで閾値を改訂する場合は事前に定義した改訂可能範囲、回数上限（1回）、判断者、判断ログを固定し、CAL以外をのぞかず、変更後の文書・生成器・分割・分析コードのdigestをOwner許可のうえ本評価前に凍結する。既存の採点を後付けで改訂しない。

## 7. §6 K0機会診断 — REVISE（blocking）

**現行文「全正例familyが固定H+または最良の合法open-loopで解ければSTOP」は不適切。** 同じ表現力で全課題が可解でも、固定H+は予算B内で発見しにくく、FULLが少ない経験で発見する機会は残る。無制限oracleの可解性を同予算対照の経験効率と混同しないこと。

推奨K0の決定表（すべてCAL系の非採点検査のみ）:

| 診断 | evaluator-onlyの実行定義 | 結論 |
|---|---|---|
| K0-a 分岐証人 | 同一公開課題条件の所定の対照ペアについて、H以内の共通合法open-loop系列を全探索し、両方を同時成功させる系列の有無と、公開観測で分離する合法条件付き方策の有無を記録 | 証人が皆無ならL-Schemaの必要性を示せない。対象課題設計をSTOP/REDESIGN（他の経験効率問いと区別） |
| K0-b 公開識別性 | 予算内で学習側が取得可能な公開履歴の同値類を列挙し、異なる必要行動を要求する真のlawが分離できるか、情報が行動選択前に到着するかを点検 | 公開区別不能なら学習器に不可能な成功を要求しない。対象課題STOP/REDESIGN |
| K0-c 同予算での余地 | 先渡しなしの固定H+・合法open-loop・RANK等を**同じ公開情報、訓練予算、探索ホライズン**でCAL評価し、G1/G2達成率とAULCの改善可能幅・天井を記帳。全件解けるかだけではSTOPしない | 強対照が飽和し、必要な+10pp等を理論的に満たせないなら再設計/STOP。可解でも高コストならCONTINUEの機会あり |

「最良open-loop」は隠れた真のlawを家族ごとに知るoracleか、公開分布に対して一つの列を選ぶ実行可能対照かを必ず区別。前者は機会の上界であり、学習者としての比較結果に混ぜない。全正例のみ後から選ぶことも禁止。完全列挙のH・max nodes・合法性・同値類を仕様に固定し、列挙できない場合はUNKNOWNであって「不存在」を主張しない。K0-a〜cを形式化できない限り事前登録凍結を推奨しない。

## 8. §7 キル条件 — REVISE

- K0は上記の設計前STOP。K1〜K4は結果に対する事後認定ゲートであり、測定値を消さない。
- K1: 同一snapshot・同一公開状態・同一乱数系列でUSE ON/OFFを強制比較し、選択行動・行動確率・合法実行トレース・記号呼出を監査。「行動差なし」を無限定な全状態で主張せず、事前固定した診断family上でのみ評価。差なしならL-Schemaの実使用を認定しない。
- K2: FULL対RECで差がない**ように見える**だけなら証拠不足。再符号化だけで説明できることの積極的な証拠には、前指定の等価性マージン内へ信頼区間が収まる等の規則が必要。さらにPRED-ONLY対FULLが必要で、なければ述語とスキーマの帰属を未確定とする。
- K3: 統計的に負、実用的に小、推定不精確（INCONCLUSIVE）を別の outcome kindとして報告する。「実質0」の幅を事前固定。strongest-controlの選択バイアスを調整。
- K4: target/生成規則漏洩、評価への訓練フィードバック逆流、予算の非等価を独立監査で認めた場合はINVALID。漏洩原因と範囲を監査台帳に保持し、同じ評価結果を都合良く再スコアしない。
- D0〜D3: D3は仮説族H0相対の不足診断であり無条件の不可能性証明ではない。陰性（H0十分）、識別不能、予算不足、修復不能の各世界で点火の偽陽性・偽陰性を区分する。

## 9. §8 ログ・再現性 — REVISE

WORLD-Rの最小台帳を採用し、以下の列/境界を追加する:
- 生成法則familyの親ID（評価側のみ）、非公開manifest hash、split境界、goal contract version、匿名task ID生成法の監査hash、公開観測とprivate truthのアクセス制御。
- checkpointごとの累積経験数、原始呼出、candidate tests、paid queries、成功フィードバック、学習準備費、USE費、CPU/wall/RSS、欠測とtimeout。予算の等価性は同じ単位ごとに独立照合。
- acquisition traceとsymbol lineage: feature-only / predicate / first-order macro / second-order schemaの型、生成前後の依存先、前提条件/反例、proposal・rejection・promotion・USE・OFFのdigest。表現種類を名前だけでなくASTで監査。
- 学習者はeval familyのscore、hidden target/seed、正解列、親法則名、評価途中の統計にアクセスできない。評価レポートは最終frozen snapshotsを集約した後にのみ公開。
- 全armの失敗/棄権/invalid、family単位での不一致、陰性・未観測・STOPを保全。工学fixtureと科学holdoutは別系統で記録する。

## 10. §9 Owner判断点への回答 — REVISE（推奨は明確）

1. **arm構成**: 原6条件を最低限維持、RECを必須採用する。機構帰属を主張するならRANK-ONLYとPRED-ONLYを追加して計8条件が望ましい。6条件だけを凍結する場合はL-Schema固有の因果帰属に上限を置く。
2. **G3分離**: AGREE。G1/G2はEditor内の名称・長さ汎化の証拠に限り、別媒体・別環境への転移はG3の別事前登録に譲る。将来G3への接続を壊さぬよう観測と行為の抽象データ契約のみ維持する。
3. **校正→凍結**: AGREE WITH REVISION。まずgoal identifiability/K0/容量の非採点方法審査、次にCAL専用法則で候補B・閾値・独立n・検出力の設計値を固定する。**校正の実施にも別のOwner GOが必要**。正式holdoutに触れず凍結receiptをOwnerが別承認した後にのみ、さらに別の実装・実行GOへ進む。
4. **進め方**: 本ラウンドはResearch Leadの独立審査を提出し、Museが節ごとにAGREE/REVISE/DISAGREEと反証条件を回答、Ownerが決定する順序を推奨。PR #194をReady/mergeしない。回答PRもdocs-only Draftとする。双方が論点ごとに一致した場合のみ**設計合意候補**と記録し、黙示の承認を認めない。

### 凍結前のblocking checklist

- [ ] B1 公開goal contract・課題ID・public indistinguishabilityとgoal leakageの証明方法
- [ ] B2 seed全AST/constructorとFULL/FIXED-IF/H+の利用可能空間・費用境界
- [ ] B3 K0-a/b/cの機械実行可能な判定式、ホライズンとUNKNOWN規則
- [ ] B4 主要AULC軸・checkpoint・独立評価family数と検出力/不確実性/複数比較
- [ ] B5 REC/PRED/RANKの効果帰属、OFF介入とnegative/null outcome契約
- [ ] B6 校正法則と正式評価法則の独立封印、source-firstの改訂履歴とOwner凍結ゲート

## 11. §10 範囲外 — AGREE

本ラウンドは設計審査のみ。PR作成/質問提出/研究文献の確認は凍結、コード実装、校正実行、TRAIN/DEV/FINAL、実PCログ収集、認定変更、mainマージを意味しない。DraftのままMuseの独立審査とOwner判断を待つ。

## 12. 一段階深めた論理・アーキテクチャ仮説（設計のみ）

中心仮説を「概念発明器が作動すれば新しい道具が増える」から、**公開観測で区別できる未説明の反例が、必要な関係変数の生成を促し、その関係の再束縛可能性が将来の必要経験を減らす**へ精緻化する。

検証したい因果連鎖: public intervention → prequential prediction mismatch → D0/D1/D2排除・D3相対的証人 → 匿名特徴/関係の提案 → 独立訓練familyへの反例検証・MDL・費用AND昇格 → snapshot保存 → 同一条件でのON/OFF行動差 → 未見family AULC増分。各矢印をログで検査し、FULLが勝っても中間段階が欠ければ「因果機構を同定済み」と呼ばない。

設計境界: environment source+truth / public interaction adapter / transcript+cost ledger / hypothesis+diagnoser / typed symbol proposer / immutable library snapshot / action policy / independent holdout evaluator / third-party auditorを分離。FIXED-IFやRANK-ONLYは同一公開traceを受け取る。評価側は訓練エージェントのプロセスとprivate truthを共有しない。graphの分岐実行意味論は人手で与えるバイアスとして証拠に明記する。

識別性に関する重要な反例: 公開履歴が全く同じ2つのhidden lawで異なる正解行動が必要なら、どのpolicyも両者で確実に正解できない。これはモデルの貧弱さではなく**情報不足**。一方、同一文法のH+が無制限の探索で正解を表現できても、有限Bでの習得効率は異なり得る。これは**統計的/計算的効率**。この2つを分けることがWORLDの研究成立条件である。

## 13. 外部知見の照合（概念的援用、WORLDの実測ではない）

- Ellis et al., [DreamCoder, PLDI 2021](https://doi.org/10.1145/3453483.3454080): プログラム/抽象化ライブラリと探索方針の共同学習。一般的な「道具を発明した」の新規性は主張しない。
- Hocquette et al., [Learning Logic Programs by Discovering Higher-Order Abstractions, IJCAI 2024](https://www.ijcai.org/proceedings/2024/379): 高階抽象の発見と転移。二階スキーマを最初に研究したとの主張はしない。
- Agarwal et al., [Deep RL at the Edge of the Statistical Precipice, NeurIPS 2021](https://papers.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html): 少数実行の点推定で不確実性を無視しない、区間・性能分布を示す教訓。WORLDのfamily独立性や必要nを直接保証する論文ではない。
- Bertran et al., [Instance-based Generalization in Reinforcement Learning, NeurIPS 2020](https://proceedings.neurips.cc/paper/2020/hash/82674fc29bc0d9895cee346548c2cb5c-Abstract.html): train/testのinstance再利用による過学習・分布依存の注意。Editorの三項splitに直接の保証を与えるわけではない。
- Ferns et al., [Metrics for Finite MDPs, UAI 2004](https://mlanthology.org/uai/2004/ferns2004uai-metrics/): 状態抽象と遷移同値性の理論背景。自動Editor→Form対応を証明しない。
- WORLD-R §16で監督者原典照合未了として留保されたScaleEnv/データスケーリング関連2件は、本審査の根拠から引き続き除外する。

**研究上の最終推奨**: 最初に解くべき問題は高機能なProposer実装ではなく、目標情報を漏らさずに**公開情報だけで分岐を学習できる証人**と、同予算の強い対照に対し**経験効率差の識別余地が残る評価分布**を厳密に指定すること。その証明が固まるまで実装を開始しない。