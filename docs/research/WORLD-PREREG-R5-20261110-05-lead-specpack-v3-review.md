# WORLD-PREREG-R5-20261110-05 — Research Lead 第3版仕様パック exact-head 再判定

id: WORLD-PREREG-R5-20261110-05
status: research_lead_v3_review / REVISE_BEFORE_DESIGN_CONSENSUS / NOT_FROZEN / NO_CAL_PROTOCOL_APPROVAL / NO_CAL_GO / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration, research-lead, exact-head-review, docs-only, no-execution
author_role: Research Lead (ChatGPT)
review_target: [Draft PR #194, head 7c4255be106dd31d7ea3d7a41699dd0708b360d6](https://github.com/ryonakayama234/DekaSugi/pull/194)
proposals_to_muse: [WORLD-PREREG-RQ5-20261110-05](WORLD-PREREG-RQ5-20261110-05-v3-repair-proposals.md)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **審査のみ／権限を発生させない**: CAL プロトコル承認、CAL 実施 GO、CAL、事前登録凍結、実装、学習、実験、正式評価、結果認定、main マージ、PR #194 の Draft 解除はいずれも行わず、許可しない。候補値の未凍結を単独の不合格事由にしない。以下の反例は数式・仕様の静的査読であり、実測・CAL・コード実行ではない。

## 0. 固定対象・基準・総合判定

- **現行正本**: [`WORLD-PREREG-SPEC-20261110-03` §0〜§7・付表A](https://github.com/ryonakayama234/DekaSugi/blob/7c4255be106dd31d7ea3d7a41699dd0708b360d6/docs/research/WORLD-PREREG-SPEC-20261110-03-specification-pack-v3.md)、blob `dd8cc93395c02d43dbe7f7b736a2d91a32030dca`。-01／-02 は履歴であり、有効条文としては混用しない。
- **併読**: 同 exact head の [ドラフト v2](https://github.com/ryonakayama234/DekaSugi/blob/7c4255be106dd31d7ea3d7a41699dd0708b360d6/docs/research/WORLD-PREREG-DRAFT-20261110-01-minimal-experiment.md)、blob `f0218f9454a92eb9512463be444f69e3c6fc7530`。v3 **§0.1 に明示された箇所だけ**を置換済みとみなし、非置換条項との整合を調べた。
- **来歴**: [R4/RQ4 PR #199](https://github.com/ryonakayama234/DekaSugi/pull/199)、[監督者 Muse の修正案 6769451282](https://github.com/ryonakayama234/DekaSugi/pull/199#issuecomment-6769451282)、[Owner 採用記録 6769534051](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6769534051)。§0.2 の対応表は参照したが、採否は各本文・付表を根拠に決めた。
- **判定**: PASS は、将来の CAL 値・実コードなしでも第三者が同一の型、推定対象、判定・状態遷移を一意に規定でき、論理と統計の必要条件を満たすこと。PARTIAL は中心的設計の改善を認めるが境界・識別可能性・再現性に残件があること。FAIL は現行の中核的契約が相反または数理的に成立しないこと。

**総合 = REVISE、B1 PARTIAL / B2 FAIL / B3 PARTIAL / B4 FAIL / B5 PARTIAL / B6 PARTIAL。PASS 0/6。設計合意は未成立。** 修復方法は別紙で Muse に具体的に提案する。Owner に残るのが CAL プロトコル承認判断だけ、という前提はまだ満たされない。

## 1. B1〜B6 の再判定（本文と付表を直接確認）

| ID | 判定 | 現行本文における進展 | 未解決の blocking・対応節 |
|---|---|---|---|
| **B1 — goal contract と識別可能性** | **PARTIAL** | **§1**: デモ3対、予算外の仕様費用、TRAIN/EVAL feedback 分離、tag の α-renaming、law の同定と episode 内の条件分岐の2層を分離。ID-only AUC 統計量も候補として記載。**付表A** は環境の主要な操作を列挙。 | **§1 証人表**の初期「AB」「AD」は **§4 TRAIN/G1 初期長4〜12**に違反。証人は同一 law の2 instance で **初期観測が異なる**ため、`π(H_0)` が一致する law-pair 証人と混同不可（§1 同値関係／v2 §2 非置換の「同一公開課題条件」を再定義要）。さらに **§1**「law 自体の同定は TRAIN にのみ起こり EVAL は snapshot が保持」対 **§5** TRAIN/holdout 親 law 非交差、v2 §0 の **未見 law G1**: unseen law 固有の同定結果は TRAIN snapshot に存在し得ない。EVAL のデモから episode 内で暫定推論してよい範囲を明示すること。3デモが未観測特徴を区別しない場合の情報上限も K0-b と整合要。 |
| **B2 — grammar・8 arm の到達可能空間** | **FAIL** | **§2/§3**: `Space`（純構文）と `R_FULL(h)⊆Space` を分離し、de Bruijn 正準形・列挙順、FIXED-IF の predicate-slot のみ構築、REC の `k=8` と線形方策、PRED-ONLY の §0.1 意図的置換を明記。以前の「空 snapshot＝学習済み閉包」という論理矛盾は解消。 | **非置換 v2 §1** は G1 を「新しい不透明トークンへ改名し、INSERT は名称を hardcode しない」と規定するのに、**§2/付表A** は記号リテラル・`INSERT(s)` を `A〜D` に限定し、G1 での操作・型付けが定義されない。新しいトークンを `Sym` として注入・観測・INSERT する α-equivariant 規則が必要。**§3 FIXED-IF** の「直近の観測特徴」は §2 の COMPARE 特徴語彙にない。PRED-ONLY の SEQ/BIND による第一階技能の USE 可否、Space 全域の grammar arity/型検査・候補評価の課金・prior/共有 read path も一意ではない。 |
| **B3 — K0-a/b/c と UNKNOWN** | **PARTIAL** | **§6**: state-pair BFS（open-loop）、公開履歴木 DP（条件付き方策）、H≤64、K0-a 不在時の主張別遷移、K0-b STOP、K0-c 上界、UNKNOWN 優先。§6 は CAL oracle の law 抽象定義のみへのアクセスを明記。 | **§1** の長さ違反の証人は K0-a の実行可能な立証にならない。**§6** は K0-a の **2 instance** と K0-b の **2 law** で同値条件・公開情報・必要な分岐時刻が異なるのに、目的語・入力範囲が未確定。状態ペア BFS が「共通系列なし」、履歴木 DP が「共通条件付き方策あり」を確認する際、成功述語・デモ／フィードバック・形だけを共有するのか snapshot の情報も共有するのかを固定する必要がある。K0-c は各 law の AULC を「law 定義のみ」で厳密に算出するとするが、instance/デモ分布と予算内経験系列が必要。抽象生成規則のどこまでを許可するか再定義が必要。 |
| **B4 — AULC・n・PPS・route** | **FAIL** | **§4/§5**: AULC の9 checkpoint、PPS 無復元／water-filling／Sampford／HT、Sen–Yates–Grundy、union bound、校正時の設計ベース同時検出力、N_eligible/cost_cap の導入は妥当な方向の修復。 | **§5 内部の厳密な計算矛盾**: `HT = Σ(p_l/π_l)Δ_l` に対し `π_l=1` の certainty unit に「重み1」と書く（正しくは `p_l`）。さらに **§4** 母集団 `frame = support \ structural exclusions` と **§5** `N_eligible = holdout 層の support 総数` が異なり、除外 law を n の容量に誤算入する。**§5** は「元の登録分布の平均 `Σ p_l Δ_l`」を estimand としながら holdout 内の `p` を再正規化して HT を適用。固定 split の外側 law は包含確率0なので元分布の母平均を design-unbiased に推定できず、条件付き estimand への切替か split-inclusive 推論を要する。**§5** power の代替シナリオは「閾値ちょうど」なのに、成功ゲートは点推定 `≥` 閾値を要求し、正規近似ではその真値で単独通過確率が約0.5となる（下記）。7対照＋G1/G2 に加え「最強対照差≥10pp」の扱いが9成分の内訳に不明。n と STATISTICAL の保証は現行のままでは成立しない。 |
| **B5 — 帰属・等価性・null/invalid** | **PARTIAL** | **§6** の結果分類は負→等価→正→閾値未達の正→INCONCLUSIVE（残余）として**網羅・排他**を確保。§4/§6 は ACTION_FAULT、FAMILY_INVALID、FAMILY_UNIDENTIFIABLE を区分。K2 は「FULL と REC の性能等価性」に主張を制限し、機構同一性を主張しない。 | **§3 PRED-ONLY** の第一階マクロ USE が不明なので FULL>PRED-ONLY を「二階スキーマ増分」候補に限定するための対称性が不明。**§4** の評価分母と **§6**「K4 で family 隔離、manifest 不一致なら run STOP」の整合がなく、汚染中の `family_status` と `run_outcome` を別階層にする必要がある。K2 の **両側**等価性区間と §5 主検定の **片側**同時区間は別仕様として信頼水準・多重性を明記するべき。新しい event kind による結果の扱いは改善であり、旧 R4 の outcome 空白は解消。 |
| **B6 — CAL・封印・改訂来歴** | **PARTIAL** | **§0.1/§7**: v2 の PRED-ONLY と CAL 後改訂条項を明示置換。決定規則／数値候補／アルゴリズム出力の3区分を導入。**§6**: CAL oracle の sealed holdout 非アクセス、manifest hash と fail-closed、Owner 段階別 GO を規定。 | **§7 の同じ文書内で**「数値候補は CAL 中に1回改訂可」と記しつつ、CAL プロトコル承認段階の「この段まで数値候補の確定」と併記。初期値の承認と CAL 後の許可された再選択を明示区別しないと権限が二通りになる。数値更新の決裁者、許可フィールド、改訂幅、入力と判断ログ、CAL 終了 receipt/holdout 開封権限が未定義。§5 の generator grid/eligible frame と §6 の `random_source_spec`/read path を具体的な版と schema に落とす必要がある。 |

### 1.1 決定的な静的反例（観測データではない）

**R5-a: certainty units の重み（§5）**。正しい HT 式が `Σ_{sample} p_lΔ_l/π_l` なら、`π_l=1` に対する係数は `p_l`。例えば2 law の確率 `p=(0.8,0.2)`、n=2、`π=(1,1)`、各 `Δ=1` のとき、正しい母平均も HT も1。一方「certainty の重みを1」と機械実装すると `1+1=2` になり、§5 の母平均を逸脱する。これは CAL 数値の問題ではなく式の衝突。

**R5-b: holdout 再正規化と estimand（§4〜§5）**。全 support で `p=(0.5,0.5)`、split 後の holdout が law1 のみ、`Δ=(1,1)` とする。全母平均は1だが、全分布 p を使う HT は `0.5×1/1=0.5`。holdout 条件付き確率 `q=(1)` を使う HT は1となるが、これは **holdout 条件付き平均**であり、登録分布全体への推論とは別。固定 split 外には包含確率0なので補正不能。加えて §4 の構造的除外を §5 の N_eligible に反映しなければ n の上限が過大になる。

**R5-c: 点閾値と検出力の境界（§5）**。真の効果が `Δ=0.15`、ゲートが `hatΔ≥0.15` なら、対称な連続推定誤差の下で `P(hatΔ≥0.15)≈0.5`（n を増やしても境界での通過確率は一般に 0.98 にはならない）。同様に真の G1 成功率がちょうど0.90で観測閾値0.90なら通過確率は概ね半分にとどまる。多数ゲート AND の80%同時検出力を**閾値そのものの代替**で要求する規則は少なくとも通常の非退化推定誤差モデルでは達成できない。モデルに依存しない100%不可能性を断定するのではなく、事前登録すべき「真の効果が閾値より十分大きい」代替シナリオが欠けることを指摘する。

**R5-d: G1 と固定トークン集合（v2 §1／v3 §2・付表A）**。v2 の未置換条項は G1 の `A/B/C/D` を**新しい不透明トークンへ一対一に改名**し、観測・INSERT のハードコードを禁止。付表A は `INSERT(s), s∈{A,B,C,D}` と記載している。位相に依存する `Sym` 引数と token binding がない限り、G1 での INSERT 許可域を一つに決められない。

## 2. 新規不整合の棚卸し（意図した置換を除外）

| ID | 種別・位置 | 指摘 |
|---|---|---|
| **V3-01** | **内部の具体的違反**・§1 証人表／§4 長さ | 証人 AB/AD の長さ2は TRAIN/G1 の初期長4〜12に属さない。K0-a の証人は admissible な例に差し替える。 |
| **V3-02** | **未置換 v2 §1 との衝突**・§2／付表A | G1 opaque token rename と `INSERT(s∈A〜D)`／記号リテラルが不整合。token role と実際の文字列を区別する。 |
| **V3-03** | **内部の対象不整合**・§1／§5／v2 §0 | TRAIN でのみ law identity を得るという説明に、未見 holdout law の EVAL snapshot が identity を保持するという矛盾。meta-model vs law-instance inference の境界が必要。 |
| **V3-04** | **内部の数学的衝突**・§5 | `π=1` certainty weight1 は `p/π` と両立しない。 |
| **V3-05** | **内部の estimand 衝突**・§5 | 元の登録分布 p の平均という主張と holdout 内 p の再正規化が不整合。 |
| **V3-06** | **内部の frame 衝突**・§4／§5 | 事前構造的除外後の frame と `N_eligible=holdout support 総数` がずれ、評価不能 law を標本上限に数え得る。 |
| **V3-07** | **内部の power 設計問題**・§5 | 真の代替を閾値ちょうどとする一方、点閾値をゲートに持つため、正規近似の80%同時検出力の計画代替として不適切。 |
| **V3-08** | **内部のゲート数曖昧**・§5 | 「9成分 AND（7比較＋G1＋G2）」の一方で「最強対照差≥10pp」を追加。10pp が G1/G2 内の複合ゲートか独立の10番目かを固定していない。 |
| **V3-09** | **内部の手続き衝突**・§7 | CAL プロトコル承認で候補確定（この段まで）と、CAL 中1回候補改訂可、が同じ表で未整理。 |
| **V3-10** | **内部の未定義**・§2／§3 | FIXED-IF の「直近の観測特徴」は現行 COMPARE 特徴語彙（直近行動結果まで）に明示されず、贈与スキーマの Space 所属が不明。 |
| **V3-11** | **内部の結果状態衝突**・§4／§6 | family 単位で K4 INVALID を隔離する一方、manifest mismatch で run 全体 STOP、AULC 分母で INVALID の具体処理が未規定。 |
| **V3-12** | **付表A の曖昧性**・付表A | INSERT は buffer 長16で必ず no-op と書くが selection 置換なら長さ減少して適法になり得る。PASTE は置換**後**の長さで判定するため非対称。選択削除と挿入を1回とみなす原子的遷移式が必要。 |
| **V3-13** | **内部の情報境界不足**・§6 K0-c／access | oracle が abstract law 定義のみを読むとしつつ goal contract、デモ/instance 分布に対する最良 AULC を計算する。どの抽象分布・生成規則まで読み、どの sealed 実体を禁じるか不十分。 |

V3-10〜13 は必ずしも相互否定の**形式的矛盾**とは断定せず、主張に必要な前提・操作が未定義であるという意味で区別した。第3版 §0.1 が既に意図的に置換した v2 §3 PRED-ONLY、§5 AULC/閾値改訂、§7 K0/校正改訂などを古い矛盾として再計上しない。-01・-02 の問題を履歴本文から再輸入しない。

## 3. Muse に提案する実質修正（次の本文改訂で採用可否を判断）

[別紙 RQ5／修復案](WORLD-PREREG-RQ5-20261110-05-v3-repair-proposals.md) に、単なる質問ではなく、差し替え可能な正規化ルールと受入試験を提示した。優先順は次のとおり。

1. **B4 の中核を先に修理**: `frame = eligible holdout` と条件付き estimand を一意化し、`q_l / π_l` の HT を使う。certainty では `q_l`。全 support への一般化が必要なら split-inclusive な包含確率を別途定義し、ゼロ確率部分を放置しない。
2. **B4 の joint power を再設計**: 成功判定の点閾値より厳密に高い planning alternative vector を登録し、7対照/達成率/10pp差のイベントを列挙。依存を含めた design-based simulation または正当な union-bound で `P_joint≥0.80` を判定する。ただしどちらも想定モデル条件つきの power。
3. **B1/B2 の world contract と G1**: 証人を初期長4以上へ差し替え、K0-a は **同一 law・同一 goal contract・異なる公開 instance**、K0-b は **異なる law の公開識別性**と規定。G1 のシンボルは phase の runtime token type `Sym` にし、`INSERT` と COMPARE を α-equivariant に。
4. **B5/B6 の結果・承認状態機械**: `ACTION_FAULT`、`FAMILY_INVALID`、`RUN_STOP`、未見法則の識別不能を分離。§7 の「CAL 前の初期数値承認」と「CAL 後に予め許可した1回の更新」を区別し、版・決裁者・digest を fix する。

**現時点の設計合意は未成立**であり、修正案は Research Lead proposal として Muse に審査を依頼するもので、Owner 採用・仕様確定・CAL 承認ではない。最優先の V3-04/V3-05/V3-07 と V3-02 を修正した後に、その新しい exact head で再判定する。

## 4. 不実施の確認

本書で扱った計算は静的な整合性検証であり、law 生成、模擬サンプル、CAL、実験、実装、学習、コードテストを一切行っていない。既存 PR の Draft 状態変更、他 PR への commit、main 変更を意図しない。
