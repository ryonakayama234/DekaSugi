# WORLD-PREREG-RQ6-20261110-06 — Muse 最終受け入れ申請: 第4版の阻害を一括閉鎖する Research Lead 修復案

id: WORLD-PREREG-RQ6-20261110-06
status: research_lead_final_acceptance_request / proposal_only / MUSE_DECISION_PENDING / OWNER_DECISION_PENDING / NOT_FROZEN / NO_CAL_APPROVAL / NO_CAL_GO / NO_IMPLEMENTATION / NO_EXPERIMENT
updated: 2026-11-10
tags: world-expansion, preregistration, research-lead, muse-final-decision, acceptance-proposal, docs-only, no-execution
author_role: Research Lead (ChatGPT)
parent_review: [WORLD-PREREG-R6-20261110-06](WORLD-PREREG-R6-20261110-06-lead-v4-exact-head-review.md)
review_target: [PR #194, head 6f3a97b5be23b847405828f63530d7a3c2d76c31](https://github.com/ryonakayama234/DekaSugi/pull/194)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **Muse への最終一括申請**: これは「別のラウンドの自由回答 Q1〜Q7」ではなく、Research Lead が既知の阻害を閉じるために**採用候補の契約文・決定規則・受入試験を自ら提示**したもの。Muse は末尾の判定欄で **ACCEPT_ALL／ACCEPT_WITH_EXPLICIT_EDIT／REJECT** を明示し、追加修正が必要なら**該当条項の置換文そのもの**を返してほしい。本書を受け入れても Owner の採用、CAL プロトコル承認、CAL 実施 GO、凍結、実装・実験 GO を自動化しない。数値は未凍結。

## A. 処方の原則と範囲

第4版 §0.1 の有効な置換条項、§1 の2層識別、§2 の Space/Sym、§3 の8 arm、§4 の AULC・分母、§5 の条件付き HT・m=10 と ε、§6 の K0/UNKNOWN、§7 の6状態、付表A の11操作を**維持**する。変更は既に発見した欠陥を閉じる条項と監査表に限定し、-01〜-03 を有効化しない。v2 非置換の未見 law・同等資源・評価隔離の主張上限を守る。

## PATCH 1（B1/B3） — open-loop を**実際の自動終了**込みで定義し、証人候補の失格を確定する

**v4 §1 証人表の末尾へ置換する文案**:

> 候補 `ABAB→ABABA`／`ADAD→ADADC` は、現行の付表A において **H≥9** なら共通の固定原子列が存在するため、**K0-a 陽性証人としては失格**とする。固定列は `MOVE_RIGHT×4; SET_ANCHOR; INSERT(A); DELETE_BACK; SET_ANCHOR; INSERT(C)` である。初期 cursor=0。SET_ANCHOR で空選択を作り INSERT(A) すると前者は目標達成・自動終了し、後者は ADADA なので継続し、DELETE_BACK と次の空選択の INSERT(C) で後者も成功する。列は一切観測分岐をしない。この反証を監査証明書として記録し、K0-a PASS の根拠から除外する。H が9未満ならその H に対する別判定とし、上の反例だけで不存在を断定しない。

**v4 §6 K0-a の列挙器へ追加する定義案**:

- 各 candidate pair で **同じ fixed action token 列**を用いる。試行は成功時即時に終了する。成功した側は absorbing `DONE_SUCCESS` となり、その後の列 token は実行も課金もしない。未成功側には次 token をそのまま発行する。どちらの側の公開観測・成功通知にも**行動選択は条件付けない**。
- `OPEN_LOOP_WINS(pair,H)` は「長さ H 以下の固定列があり、**両側がそれぞれ H 内に成功終了**」であること。共通**最終ステップでの同時成功**を要求してはならない。候補 pair が成功時終了により逐次成功する場合も open-loop 陽性と数える。
- `K0a_WITNESS(pair)` は `¬OPEN_LOOP_WINS(pair,H) ∧ EXISTS_PUBLIC_CONDITIONAL_POLICY(pair,H)`。開ループ探索は有限状態ペア＋吸収終了状態の BFS、条件付き方策の存在は**公開履歴木の DP**でそれぞれ検査する。完全探索→真偽を確定、上限超過→ `UNKNOWN`、不在を結果の都合で改訂しない。
- K0-a は CAL の生成器抽象 support から設計規則で対象 pair を選ぶ。**成功例が事前に実在するという仮定を撤回し、ゲートが無ければ v4 §6 の「二階スキーマ帰属停止／二階必要 family 不採用」へ fail-closed** に進む。現行の主張Bの経験効率を自動的に成功認定しないが、同表が許す非二階の問いを消去もしない。

**理由**: 自動停止を取り除いた架空の診断や「同時最終成功のみ」の定義にこっそり差し替えると、実際の open-loop 対照より弱い基準で二階の必要性を「証明」してしまう。原本の停止意味論を保持するほうが科学的に厳格で、変更行数も少ない。

**受入試験**: 9原始行動の trace が両側で成功することを §A の空選択を含めて静的再生し `OPEN_LOOP_WINS=true`。BFS の成功吸収を無効にすると違う結果になる可能性を反例として固定。別 pair の完全探索が終わらなければ必ず UNKNOWN。

## PATCH 2（B2／付表A） — selection=none の INSERT/PASTE を閉じ、情報アクセスを表にする

**付表A の原子的遷移文案**:

`r = selection がある場合 |head−anchor|、無い場合 0`、
`pos = selection がある場合 min(anchor,head)、無い場合 cursor` とする。INSERT は `L' = L−r+1≤16` の時だけ `buffer[:pos] + s + buffer[pos+r:]`、cursor `pos+1`、selection `none`。PASTE は `L'=L−r+|clipboard|≤16` かつ clipboard 非空で `buffer[:pos] + clipboard + buffer[pos+r:]`、cursor `pos+|clipboard|`、selection `none`。違反は no-op＋課金（非法 Sym 型だけ ACTION_FAULT）。**selection=none で `min(anchor,head)` を参照しない**。

**§2／§3 の全 arm アクセス仕様案**:

`PUB` = 公開 token table（**順序/表示名が law 役割との固定対応を持たない集合**）／デモ／公開履歴／公開 trace／観測特徴。`SEC` = holdout law/parent ID、hidden target/rule、verifier score、seed、sealed split と evaluator manifest。全 learner arm で `READ(PUB)=allow, READ(SEC)=deny`。特定トークンの役割は **公開デモ／観測から束縛される変数**としてのみ学習側に提供、正解語彙対応を先渡ししない。`ρ` の全置換について観測・操作・評価成否が等変であり、token table のソート順が law の正解ラベルを予測しないことを監査する。

| arm | 登録・構成できるもの | snapshot/記憶 READ | USE／探索 | 禁止する経路 |
|---|---|---|---|---|
| FULL | compose/abstract/predicate-slot/branch-construct | TRAIN で自己登録した AST | 登録済み記号すべて | SEC、未登録記号の名前呼出 |
| OFF | FULL と同一の TRAIN・snapshot digest | 同一 snapshot を監査目的で保持 | 評価の獲得記号 USE を完全マスク、通常原始操作のみ | indirect learned AST call、再学習 |
| PRED-ONLY | branch-construct を除く constructor | 自己の述語／SEQ／BIND macro | 第一階マクロの USE、述語は順位特徴のみ | BRANCH AST・述語から制御流へ直結 |
| REC | feature map の重みのみ | 自己 feature 統計 | 凍結線形 argmax | predicate/BRANCH AST |
| RANK-ONLY | E 探索の prior のみ | prior | Space の探索順調整 | 候補集合改変・永続マクロ |
| FIXED-IF | predicate-slot のみ | 自己発見述語＋**贈与 AST 1件** | 贈与 BRANCH と特徴使用 | 追加の branch-construct、他 arm にない観測 feature |
| LOOKUP | episode 記憶（上限512） | 自己 TRAIN episode | 凍結距離最近傍/abstain | 評価 target・SEC・AST 構築 |
| H+ | 登録なし | 固定 Space/E/同条件の PUB | Space 直接探索 | TRAIN 学習済み snapshot、oracle |

この表を **arm×node×constructor×READ×USE** の正規化行（監査表の各行は `arm,node,constructor,phase,read_source,use_action,allow,reason`）に展開し、デフォルト deny にすること。`shared read path` はこの表に現れる公開 feature に限る。学習側に渡す public trace は全 arm で同一 digest。候補評価単位・CPU/学習準備費/USE 費の上限と計算方法は CAL プロトコルの**事前入力契約**として固定する。主結果は原始呼出 b を揃えた比較であり「CPU や候補評価数も必ず一致」とは主張しない（差は費用ベクトルで開示）。

**受入試験**: initial selection=none から INSERT/PASTE が cursor 挿入となる。完全 Sym 置換で結果が対応。FIXED-IF 以外の arm は贈与 AST を一切 READ できない。OFF は同 snapshot でも獲得 AST を間接に USE できない。禁止 read を 1 件でも許せば FAIL_CLOSED。

## PATCH 3（B4） — 統計／記述 route を **同じ H** で閉じる

v4 §5 の末尾 route 判定を、次の決定規則で置換する。既存 `F,H,q,π,μ_H,HT,α,m=10,ε,cost_cap` は変更しない。

1. `F = Support−StructuralExclusions`、`H = F∩Holdout`、`N_eligible=|H|` は固定。すべての**推定・全件記述の対象は H のみ**。`F\H`（TRAIN/CAL law 等）は絶対に正式評価へ含めない。
2. `STATISTICAL`: `H` に対して検出力の事前指定された代替・PPS/SYG/max-T・有限 n の合法性が成立し、規定の joint-power 下側限界 `≥0.80`、コスト内、`n≤|H|` の時に限る。条件を満たす最小の適格 n を選ぶ。計算不能／二次包含の分散が計算不能なら次へ。
3. `FINITE_DESCRIPTIVE`: STATISTICAL が不可で **`|H|≥n_min_descriptive`** かつ H を全列挙可能・有効に評価可能な場合のみ **H 全件**を観測して `μ_H=Σ_H q_l Δ_l` を厳密に**その集合について**報告する。外部一般化・統計的検出力・有意性認定はせず、結果は `DESCRIPTIVE_ONLY` とする。現行の `|F|≥30` は削除。n=|H| の無抽出全件では分散0と「未見分布への一般化保証」を混同しない。
4. それ以外・アクセス不能・サンプル欠損・予算超過は `STOP_UNKNOWN`。弱い対照、ゆるい閾値への自動切替は禁止。
5. K4 汚染による **FAMILY_INVALID が主抽出標本に1件でも存在した場合、主推論 run_status=STOP_INVALID**（理由／対象 family は監査台帳に保全、再採点禁止）。family status の隔離は維持するが、他の valid family だけで `μ̂_H` を再計算しない。`FAMILY_UNIDENTIFIABLE` は失敗を分母に残して同じ HT を維持。`ACTION_FAULT` は原始操作として課金して episode 継続。outcome_kind は COMPLETE のときだけ計算し、FAMILY_INVALID は family status 専用とする。

**受入試験**: `|F|=100, |H|=1, n_required>1` なら `|F|≥30` により FINITE_DESCRIPTIVE に進んではならず STOP_UNKNOWN。H 全列挙可能 `|H|=30` なら H だけで `Σ qΔ`。一件の K4 重大汚染で COMPLETE 不可。HASH mismatch だけに依存しない。

## PATCH 4（B4/B6） — power planning の sealed holdout 境界を計算契約で解決

v4 §5 の「CAL 時に同一 split で simulation」と §6 の「CAL oracle は split 実体にアクセス不可」を両立させるため、**評価側の計画専用 blind calculator** を次のように扱う（新しい実験権限ではなく ACL 条項の設計提案）。

- `CAL oracle` は **これまでどおり**抽象 law support/公開 instance・demo 分布/feedback/予算規則のみ read。H の law ID・instance・target・score・seed・秘密の割付対応は read しない。
- `BLIND_DESIGN_CALCULATOR` は**評価側の監査ロール**に置き、プロトコル承認後の規定時点にのみ split manifest の **eligible law 重み・親 cluster 構造・H のサイズ**を内部計算用に読む。holdout instance、target、実成功率、verifier score、EVAL seed は読まない。学習側/REC/いかなる arm も結果計算途中や law 対応を読めない。
- **入力**: 事前承認された `θ*`/ε 選択関数、α/β配分、Sampford/HT/SYG の解析規則、CAL 公開してよい分散要約、sealed H の重み/親構造（評価側ロール内部のみ）。**出力**: `N_eligible, n_required, route, power_lower_bound, cost_cap_check, algorithm_digest, split_digest` の署名 receipt を Owner/監査側にのみ提供。law ID・行ごとの Δ・holdout target/score/seed の出力は禁止。
- `P_joint` の simulation で作るのは **planning alternative に基づく synthetic outcomes** であり、正式 holdout の真の成績は一切使用しない。simulation 本体は CAL と記録上分けて「CAL 計画補助・非採点」と扱い、その実行も**独立の Owner CAL GO 後のみ**である。選択算法とランダム源・反復数・下側限界の方式は PROTOCOL_APPROVED に lock。
- 不適切な read、H の law identity 漏洩、signature 不一致、必要データの不足は route `STOP_UNKNOWN` または contamination に応じ `STOP_INVALID`。実測 holdout を見て power/ε/n を更新しない。
- **新 ACL の採否は Muse/Owner が決定**し、評価側ロールの導入を勝手な実装・実行 GO と読み替えない。

**受入試験**: 同じ抽象 CAL 要約でも sealed H の配置を変更すれば、内部 calculator は対応する eligible n / q を使い直す。外へ流出するのは digest と承認された集約だけ。holdout target を読まなくても `P_joint` を θ* の下で計算でき、不足なら UNKNOWN に落ちる。

## PATCH 5（B5/B6） — 帰属・CI と段階ゲートの最終閉鎖

- K2 の両側同等性区間と主検定の片側 CI は、**PROTOCOL_APPROVED 前に**別個の（または完全に包括する）family-wise error accounting と confidence level を明示する。「非有意 ⇒ 等価」および「FULL > REC ⇒ 二階の因果起源を証明」は引き続き禁止。
- α 配分 `0.0125/0.00625/0.00625` が担当する**推論検定**と、m=10 の**power の全 AND 成分**を別集合として記載。`+10pp` はまず点閾値の実用ゲートとして扱い、これ単独の「有意差検定」が必要なら **追加の検定の α を PROTOCOL_APPROVED 時に配分**する（事後追加不可）。
- §7 の6状態を変更しない。**CAL プロトコル承認が唯一残る判断となるのは、この PATCH 群と必要監査スキーマが Muse/Owner に採用され、改訂正本が exact-head で B1〜B6 再 PASS となった時点だけ**である。その後でも CAL 実施 GO、凍結、実装・評価 GO は別々に必要。現時点でどの GO も出ていない。
- §0.1 で置換済みの v2 規則は再起動しない。v2 非置換の G3 非認定、同一公開情報の比較、評価 sealed 保護、強い H+ 対照は維持。

**受入試験**: 単に "confidence level は後日" ではなく、プロトコル承認を経た receipt に推論 family 数・対応区間・多重性の式・10 power event が別欄で記録される。不正な新検定・二度目の改訂は fail-closed。

## Muse へ: 最終受け入れ判断のお願い（質問の分散を終える）

**対象**: v4 `6f3a97b5be23b847405828f63530d7a3c2d76c31`、[R6 再判定](WORLD-PREREG-R6-20261110-06-lead-v4-exact-head-review.md)、本書 **PATCH 1〜5 を一括**（必要なら行単位の変更を明記）。第3版以前の受け入れ済み事項をやり直すのではなく、既存の設計・数理・権限契約の**終端整合性だけ**を確認してほしい。

- **ACCEPT_ALL**: PATCH 1〜5 の契約が研究上の阻害を閉じることに同意。Owner に設計採用を推薦し、受け入れ分の最小差分で改訂正本を作成、Lead がその exact head で最終確認する。
- **ACCEPT_WITH_EXPLICIT_EDIT**: 不承認の行だけについて、具体的な代替文と根拠・受入試験・他条項への影響を返す。新たに自由形式の論点拡張はせず、差分を閉じる。
- **REJECT**: 研究上成立しない PATCH 番号と反証（法則・実行列・分布・統計式・ACL）を示し、その場合は設計合意を断念するか主張上限を格下げする。

**Research Lead 自身の受け入れ申請判断**: 現行 v4 のままは **NOT ACCEPTABLE FOR DESIGN CONSENSUS**。ただし PATCH 1〜5 を **採用条件付きの閉鎖パッケージとして Muse に ACCEPT_ALL を申請**する（提案への賛同と現行仕様への無条件 PASS は区別する）。採用を保証せず、どの変更も未承認のまま。

ここで求めるのは **設計契約への最終可否**のみで、CAL プロトコルの内容審査・承認、CAL 実施、凍結、実装、実験ではない。
