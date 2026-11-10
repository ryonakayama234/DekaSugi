# WORLD-PREREG-R2-20261110-02 — Research Leadによる事前登録ドラフト v2 再審査

id: WORLD-PREREG-R2-20261110-02
status: research_lead_v2_rereview / design_consensus_candidate_with_conditions / revise_before_freeze / docs_only / NOT_FROZEN / NOT_CALIBRATED / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration-rereview, research-lead, methodology, no-execution
author_role: Research Lead (ChatGPT)
review_target: [WORLD-PREREG-DRAFT-20261110-01, Draft PR #194, head a67e0dbb](https://github.com/ryonakayama234/DekaSugi/blob/a67e0dbb5491961253e21dbfe88f451857319f0f/docs/research/WORLD-PREREG-DRAFT-20261110-01-minimal-experiment.md)
previous_review: [WORLD-PREREG-R-20261110-01, PR #196](https://github.com/ryonakayama234/DekaSugi/blob/2dc8dd2efc187a25a1961191683fe6801bdd5340/docs/research/WORLD-PREREG-R-20261110-01-lead-review.md)
questions: [WORLD-PREREG-RQ2-20261110-02](WORLD-PREREG-RQ2-20261110-02-freeze-questions.md)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **権限・証拠の境界**: この文書は main ae44f126e36410b98dc5ee450a05348c9f11105b を基点とする独立した docs-only 再審査であり、PR #194 自体には変更を加えない。参照元は PR #194 の明示 head a67e0dbb、前回審査 PR #196 と[監督者回答](https://github.com/ryonakayama234/DekaSugi/pull/196#issuecomment-6767408437)、[Owner 採用記録 6767632884](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6767632884)。v2 は main に未統合。本回答による設計上の同意は、数値事前登録の凍結・校正 GO・実装 GO・実験 GO・結果認定・main マージを意味しない。

## 0. 総合判定と判断の粒度

**総合判定: REVISE（凍結不可）、ただし研究設計の骨格は「条件付き設計合意候補」として回付可能。**

v1 に対する主要な論理修正は真正に反映された。とりわけ旧 K0「固定 H+ が可解なら STOP」の撤回、K0-a/b/c の分離、goal identifiability の先行検査、8 arm と REC の採用、B を主張とする認定上限、family 単位・同時区間・否定結果の保存を評価する。ただし「文章で方針が定義されたこと」と「機械可読かつ裁量なく凍結可能な決定規則が揃ったこと」は異なる。**B1〜B6 は方針段階で部分充足したが、凍結チェックを完全 PASS した項目はゼロ**である。

特に優先する未解決点は、(a) デモ課金と単一の主予算軸との不整合、(b) AULC 台形積分の分母、(c) MQ4 の母集団・重複・多重比較込み検出力計算と自動切替の実行規則、(d) 分岐意味論を含む grammar の実際の可到達集合、(e) K0/キルの数値化、(f) 校正前の「凍結判断」と校正後の「凍結 receipt」の手続き的な衝突である。以下はドラフトの実験結果の評価ではなく、**方法の審査**である。

## 1. v1 審査の節別指摘と v2 反映の対照

前回審査 [WORLD-PREREG-R-20261110-01](https://github.com/ryonakayama234/DekaSugi/pull/196) の節番号を左、v2 の節番号を右に記す。「反映」は概念・文章としての充足であり凍結完了を意味しない。

| v1 審査対象 | v2 該当 | 再審査 | 根拠と残り |
|---|---|---|---|
| R§0/§1 主張 B と認定3段 | §0 | **AGREE** | B を主、A を補助、記号系譜→ON/OFF行動差→未知 family 上の効率差を分離。Editor→Form は非認定 |
| R§2 世界 v0 | §1, §5 | **AGREE WITH RESERVATION** | 4記号、11操作種、no-op 課金、H 上限要求、G1 不透明改名、G2 可解性検査を記述。ただし操作ごとの前提・容量・終了・H の値は未列挙。G2 の「長さ」が初期/目標/中間のどれかも未固定 |
| R§3 課題・封印 | §2, §7, §9 | **AGREE WITH RESERVATION** | 公開 goal 3要素、非公開 target、law 連結成分 split、ID-only 対照、識別不能 STOP を反映。デモ提示数・生成方式・課金、task tag 再使用範囲・公開履歴の同値判定が未定 |
| R§4 arm | §3 | **AGREE WITH RESERVATION** | 原6＋RANK-ONLY＋PRED-ONLY の8条件、REC、贈与 FIXED-IF、主 trace/副 active の分離を採用。空間/実行費の同一性、禁止対象、OFF 介入単位は監査表が必要 |
| R§5 seed/MR3 | §4 | **REVISE** | 4種 evaluator node と構築 operator を示し、分岐意味論の先渡しを開示したことは改善。ただし仕様書自身が要求する node arity/AST/guard/定数/prior/共有 read path の全表はまだない |
| R§6 指標・標本 | §5, §6 | **REVISE** | B の一本化、AULC と同時区間、G1/G2 の追加ゲート、CAL-SD 検出力・有限集合切替を導入。ただし AULC の分母、デモ課金、評価 n の計算法、同時検定を含む power、有限母集団が未確定 |
| R§7 旧 K0 の論理誤り | §7 | **AGREE WITH RESERVATION** | K0-a/b/c へ実質的に置換。oracle 可解性は上界のみ、列挙不能 UNKNOWN。H・探索範囲・飽和 STOP の数値式は未固定 |
| R§8 K1〜K4・D0〜D3 | §8 | **AGREE WITH RESERVATION** | 診断 family 同一 snapshot、同一乱数、REC 等価性、NEGATIVE/SMALL/INCONCLUSIVE、INVALID、相対 D3 を採用。等価性幅・推定精度・監査結果遷移が未固定 |
| R§9 ログと隔離 | §9 | **AGREE WITH RESERVATION** | family 親 ID、公開/private 境界、費用・記号 AST 系譜と未観測記録を採用。イベント schema、時系列と digest/receipt の権限が未固定 |
| R§10 Owner 4判断点 | §3, §6, §7, §10 / Issue #195 | **AGREE（決定反映）** | 8 arm と REC、G3分離、CAL→数値規則、Lead再審査と別 Owner GO を反映。ただし §10 の凍結/校正の時系列は修正文言が必要 |
| R§11 範囲外 | §10 | **AGREE** | 非凍結・非実装・非校正・非実験、PR #194/#196 Draft の維持を明記 |
| R§12 機構仮説、R§13 外部知見 | §0, §3, §4, §8, §9 | **AGREE WITH LIMIT** | 因果帰属の階層と D3 の仮説相対性は適切。記号系譜の相関だけで因果連鎖全体の実証とはしない。未照合外部文献を新たな根拠とはしない |

## 2. §2 goal contract と識別可能性 — 方針 AGREE、B1 の実装契約 REVISE

不透明 task tag、別インスタンスの公開デモ対、試行ごとの成功/失敗、hidden target/hidden law の非公開という構造を支持する。学習器が使える情報を増やして問題を識別可能にしながら、真値の直接漏洩を禁止するのは合理的。law 連結成分で train/holdout を分け、G1/G2 を独立2標本に数えない点も適切。

**未解決**: §2 は「公開デモを経験予算に課金」、§5 は「唯一の主予算軸は有料原始操作呼出 b」としている。既成の（初期状態→目標状態）対を受け取るだけでは原始操作は発生しない。デモ一つを b の何単位に換算するかを固定するか、デモ提示数を全arm共通の別上限とし、b の主軸を変更しないか、いずれかを選ぶ。任意の換算率を事後設定してはいけない。評価時の無学習と、TRAIN における試行フィードバックの扱いも phase ごとにイベント規則を分ける。

証人の公開履歴同値は、デモ内容・task tag・操作結果・フィードバックをすべて含む、行動前に利用可能な情報で判定する必要がある。デモを見ればすでに異なる公開課題条件となる証人を「同一公開条件の分岐証人」と誤認しない。task tag は法則名の符号化だけでなく、同一法則内/別法則間での再使用範囲とランダム割付順序まで凍結する。

## 3. §3 8条件と帰属の読み方 — 方針 AGREE、機構認定は条件付き

**AGREE**: FULL/OFF/PRED-ONLY/REC/RANK-ONLY/FIXED-IF/LOOKUP/H+ の8条件、REC 採用、主比較の同一事前割付公開 trace、副比較の各 arm 能動収集という階層は、前回の欠落を是正した。FULL>OFF＋合法行動差は USE の寄与、FULL>REC のみでは述語か二階スキーマか未判別、FULL>PRED-ONLY は二階スキーマの増分の「候補」という読みは正確。FIXED-IF は seed 贈与による強い対照であり初期条件一致とは記さない。

**REVISE before freeze**: arm ごとの構築・実行可能 AST、入力特徴、学習可能な prior/ranking、保持できる episode、training/USE コスト、停止条件を一枚の permission/cost matrix として固定する。とくに PRED-ONLY における二階スキーマの禁止は構築だけでなく USE も含めて定義し、RANK-ONLY が同一候補集合を持つとは何を同一とするか（未発見 AST を含むか）明示する。OFF は FULL の同じ訓練済み snapshot に評価時の USE マスクだけを適用し、再学習/別前処理を許さない。差が非有意なら「同等」とは扱わず、因果帰属は同時区間と K1 の行動介入まで必要とする。能動収集の副比較へ主比較の認定を一般化しない。

## 4. §4 seed の grammar 表と到達可能集合 — 方針 AGREE、B2 は未充足

v2 は「evaluator: ATOM/SEQ/BIND/COMPARE、learner construction: compose/abstract/predicate-slot/branch-construct」と明記した。分岐実行意味論は与えられた meta-runtime のバイアスであり、獲得は経験由来の型付き述語と再束縛可能な構造の構築に限る、という MR3 境界も保持した。

一方、**これは完全な grammar table ではない**。branch-construct が評価器の AST node type としてどう表現・評価されるか、型・arity・束縛スコープ・状態観測・比較の演算子・初期定数・深さ/size・合法性・prior/列挙順序・学習器と評価器の共有参照路を機械可読に記す必要がある。H+ は「同一 runtime」を使うだけでは「同じ候補表現集合」を保証しない。H+ が FULL の獲得後の有効 AST を seed の既存 operator で再現できるのか、できないならどの表現差を許す研究なのか、反証可能な reachability table を要する。空 snapshot で完成 If を名前参照できないことは必要だが十分ではない。

## 5. §5 予算・AULC・判定階層 — REVISE（数式の不整合あり）

予算は累積有料原始操作 b、他の episode/candidate/CPU/wall/RSS/準備/USE は別ベクトルとする決定を支持する。ただし、評価 checkpoint に使う b が TRAIN 中の取得費用なのか、評価側の解答実行費なのか、デモ費なのかを混同しないよう、phase 別会計を固定する。無効操作 no-op も原始呼出に課金する方針は適切。

**AULC の算術的な要修正点**: v2 は「等間隔 checkpoint で台形積分し (B+1) で正規化」とする。b=0,...,B の単位刻みで台形積分すると幅は B である。全checkpointで s(b)=1 の場合、台形面積は B、(B+1) で割ると B/(B+1) となり 1 に正規化されない。連続曲線の台形面積なら B で除す（B>0）。または B+1 点の単純平均を定義し、台形積分とは呼ばない。疎 checkpoint なら台形重み・端点・補間・未到達 B・打切り/棄権の扱いを正確に定義する。

判定階層「AULC 主、B時点 G1/G2 と対照差は追加 AND ゲート」、最強対照の事後選択を同時信頼区間で扱う、負例/全対照を残す点は支持する。ただし閾値候補改訂の許容範囲、主要な同時比較集合、片側検定と同時95%区間の整合、B時点ゲートに対する多重性・欠測規則、最強対照選択のアルゴリズムは凍結前に決める。「AULC点推定≥+0.15」と「差の下側同時区間>0」の両方を要求する際の検出力の想定効果は、0.15ちょうどではない点にも留意する。

G2の13〜16は何の長さか（初期/目標/最大中間）と、中間容量16の制約を事前に指定する。容量による不可能を「設計上の除外」にするなら、除外規則を評価 family 生成前に固定し、生成後の母集団と元分母をともに報告する。

## 6. §6 MQ4 — **REVISE**（Owner 採用方針は維持）

**結論**: 「まず独立 CAL 分散を測り、事前固定の検出力規則から評価 n を決め、実現不能なら有限法則集合の完全列挙による記述的認定へ切替え、弱い対照に替えない」という Owner 決定には **AGREE**。しかし v2 §6 をそのまま凍結可能な MQ4 運用形とするかには **REVISE**。

理由:
1. **推定対象を固定すること**。登録法則生成文法が規定する分布（テンプレート重み、法則の正規形、パラメータ・長さ・語彙の分布）からの iid draw は、その固定分布に対する期待効果を推定する枠組みにはなる。ただし「独立に抽出された seed/draw」が「未知テンプレートへ一般化できる独立な意味 law family」を保証するわけではない。共通親テンプレートや共通学習 snapshot などの階層依存をどこまで条件付けるかを宣言し、template 別結果は監査付録のみか推定/cluster 単位かを決める。G1/G2 の同一 law 派生は同じ cluster で扱う。
2. **重複と finite frame**。同一意味 law が二度 draw された場合に独立な family 数として加算するか、重複を排除し意味法則の unique ID で cluster 化するかを決める。有限集合から無復元に採るなら通常の iid ではなく、無復元の有限母集団標本である。復元抽出 iid なら標本対象は登録分布であり、法則の実効多様性と重複率を必須報告する。両者を混ぜない。
3. **計算規則の完全固定**。CAL 前に、推定 SD/discordance の選択、分散の保守的上限/不確実性、効果量仮定、片側 α=0.025、80% power、G1/G2 相関、8 arm 中の7対照に対する選択/同時区間、主要 AULC と追加 AND ゲートを考慮する n 計算法を指定する。単純な正規近似で例示された 149〜227 等を「必要 n の確定値」として使わない。検出力の代替効果と判定閾値を同一にすると、閾値を厳密に超える確率の解釈が変わるため、決定規則を式か決定的擬似コードで定義する。
4. **切替規則を真正に事前固定すること**。比較可能な unique law 母集団の全件数 N、列挙可能性の証明/UNKNOWN、CAL-評価の非重複境界、実現可能な最小 n（費用・時間上限を含む）と n_required の比較を定義する。n_required>N という文章だけでは不足。切替後は集合内の全件の分母・欠測・arm 差を記述し、母集団外の統計的一般化、等価性や検出力80%の主張は行わない。全列挙が不能なら「記述的完全認定」には移れず STOP/REDESIGN/INCONCLUSIVE の事前分岐とする。
5. **必要な帰属は強い対照を維持**。固定H+、RANK-ONLY、FIXED-IFなどを落として n を縮めず、観測された効果で route を選び直さない。

**提案する固定前 gate**: CAL実行より前に sampling-frame／重複規則／power式または固定疑似コード／7対照の多重比較調整／有限集合完全性判定／費用上限／route decision table をバージョン・digest 付きで先行承認する。CAL の結果から差し込めるのは、予め指定された分散入力および feasibility 計測値に限る。候補効果・比較対象の選択を後から操作しない。これは Owner 採用済み手順の具体化であって、その3決定を覆さない。

## 7. §7 K0-a/b/c — AGREE、形式化未完

旧 K0 文の撤回を高く評価する。3診断はそれぞれ「条件分岐の構造的必要性」「公開情報による実現可能性」「同予算・同情報下での改善余地」を測り、無制限oracle可解性をSTOPに使わない。列挙不完了 UNKNOWN、陰性家族を消さない点も適切。

**凍結前**: K0-a の family 対照ペアと公開条件、H・AST node/depth/無限反復防止・合法 open-loop 定義、K0-b の公開履歴の完全一致/同値・情報到着時刻、K0-c の強対照飽和判定（可能最大差の上界と必要ゲートの比較）を機械判定表にする。CAL の推定平均がたまたま高かっただけで「理論上飽和して改善不能」とは断定しない。完全性証明ができない箇所は UNKNOWN とし、STOP の原因を分けて記録する。K0-a の分岐証人が不存在なら「二階スキーマ必要性の主張」は停止しても、その他の経験効率に関する問いまで自動的に偽とはしない。

## 8. §8 キル条件 — AGREE、定量監査は未完

K1は固定診断 family／同一 snapshot／同一公開状態／同一乱数に限定した ON/OFF 行動・合法trace監査、K2は非有意≠等価、K3は負/実用的小/不精確、K4は漏洩/予算逸脱を独立監査で INVALID とする、D0〜D3はH0相対という設計を支持する。前回の論理的懸念は概ね解消した。

**凍結前に必要**: K1の「行動差」を確率的方策の場合にどの統計量・何件の診断で判定するか、K2の等価性マージンと両側区間/同時性、K3の practical-small 幅とNEGATIVE判定アルゴリズム、K4の検知者・時点・影響範囲・INVALID分母と停止/再開可否を固定する。記号の生成直後の寄与が後で失われても、その時系列だけでは保持干渉を因果同定しないため、仮説検討に留める。

## 9. §9 ログ — AGREE、schema と custody は凍結対象

法則親と匿名 task ID 生成 audit hash、split、goal contract、公開/hidden 情報境界、checkpoint・費用ベクトル、AST provenance、snapshot digest、欠測/STOP/INVALID を記録する方向を支持する。誰がいつ原本を書いたか、CAL と正式評価で同じ renderer/learner や storage を共有するか、評価前・後の参照経路、one-shot receipt、秘匿 manifest の custody を登録 schema とアクセス表として固める。正式 holdout の score が学習へ戻る経路は認めない。凍結前にログ設計を採用することと、実際にログ取得を開始することは別である。

## 10. B1〜B6 凍結前 blocking checklist の再判定

| 項目 | v2 で満たされた設計上の要件 | 未決事項 / 機械可読化 | 凍結判定 |
|---|---|---|---|
| **B1** goal/識別性 | 公開3要素・hidden分離・ID-only・到達可能証人・分母維持 | demo数/料金とbの整合、task ID再使用、phase別feedback、公開履歴同値と識別不能判定 | **PARTIAL / BLOCK** |
| **B2** grammar/arm空間 | evaluator/learner node候補、分岐意味論をバイアスと明示、空snapshot反証案 | AST全node/constructor/型/guard/prior、H+到達性、8 arm permission/cost matrix、graph費用 | **PARTIAL / BLOCK** |
| **B3** K0 | a/b/cの機能とSTOP/UNKNOWNの分離、oracle≠有限予算を反映 | 証人集合、Hと列挙完全性、同値類、K0-c改善幅の数値条件、UNKNOWNログ | **PARTIAL / BLOCK** |
| **B4** 指標/検出力 | 主b軸・AULC/追加ゲート、familyペア差・CAL-SDからn選択、有限集合切替 | AULC分母、checkpointと費用scope、分布/重複、power式、多重性、finite frame/route式 | **PARTIAL / BLOCK** |
| **B5** 帰属/結果 | REC/PRED/RANK/8 arm、OFF同一snapshot、非有意≠等価、K1〜K4の監査形 | USE権限差、等価性・small幅、同時区間、K1/K4判定式とINVALID扱い | **PARTIAL / BLOCK** |
| **B6** 封印/改訂 | CAL/評価分離、1回改訂、Owner別GO、receiptの必要性 | generator・split・分析の先行lock、seed/manifest ID、変更許容範囲、receipt順とcustody | **PARTIAL / BLOCK** |

したがって「B1〜B6 は v2 により方向性が満たされた」は正しいが、「B1〜B6 が凍結前に全件充足」は誤り。**凍結可能判定: NO**。各 B は仕様 hash と独立した読み合わせ/反証検査が定義されて初めて PASS の候補になる。実際の校正・実装・試験をこの審査で行っていない。

## 11. 手続き、設計合意候補、残る逆質問

**設計合意候補にしてよい範囲**: 8 arm＋REC、Bを主とする認定3段、goal identifiabilityを先に検査する原則、K0の3段化、最強対照維持、CAL分散で事前固定規則を入力する統計/有限集合の二経路、G3の次ラウンド分離、INVALID/NULL保全、校正にも独立 Owner GO が必要という骨格。Muse/Ownerの採用済み3点の再承認要求はしない。

**まだ合意にしてはいけない範囲**: B1〜B6の操作仕様・数値・診断・分析コード・生成母集団の凍結、具体的な効果と検出力、何らかの能力認定。§10 の現状の順序「Owner による凍結判断 → 校正」は、§7 の「校正後に数値/生成器/分析コード digest を凍結 receipt」と読み合わせると曖昧である。前者を**校正プロトコルの設計承認**と呼び分け、数値事前登録の最終凍結は、別GOを受けたCALの後の Owner receipt 承認とする必要がある。

**推奨手続き（Owner採用順序の具体化、GOの代行ではない）**:
1. v2 の Lead 再審査（本書）と監督者の逆質問への回答 → 研究設計の論点別合意候補。
2. CAL前に必要な仕様と決定規則を docs-only で固定し、Owner が**CALプロトコルのレビュー**と**CAL実施GO**を別途判断する。現時点ではどちらも実施を許可していない。
3. GO が出た場合に限り、隔離された非採点CAL。指定分散だけで評価 n と route を機械決定し、許容された1回の改訂後、Ownerが数値・source・split・分析手順と digest の正式**事前登録凍結**を判断する。
4. 凍結後も実装・学習・正式評価の実行には段階ごとの別 Owner GO を求める。PR #194/#196 は引き続き Draft。明示承認なしで main にマージしない。

監督者へ提出する具体的な逆質問は独立文書 [WORLD-PREREG-RQ2-20261110-02](WORLD-PREREG-RQ2-20261110-02-freeze-questions.md) にまとめる。回答は各問 AGREE/REVISE/DISAGREE と仕様化可能な代替案、変更箇所、owner判断事項との境界を示してほしい。

**最終結論**: **MQ4はREVISE（採用済み経路の運用規則を補完）、総合はREVISE before freeze、研究設計の骨格のみ条件付き合意候補**。本書は docs-only の審査記録で、校正・実装・実験・凍結・マージは一切行わない。
