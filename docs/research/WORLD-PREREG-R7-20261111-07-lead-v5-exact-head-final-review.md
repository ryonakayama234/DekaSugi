# WORLD-PREREG-R7-20261111-07 — Research Lead 仕様パック第5版 exact-head 最終確認

id: WORLD-PREREG-R7-20261111-07
status: research_lead_v5_final_review / TWO_MINIMAL_RESIDUAL_CLARIFICATIONS / DESIGN_CONSENSUS_NOT_YET / NOT_FROZEN / NO_CAL_APPROVAL / NO_CAL_GO / NO_IMPLEMENTATION / NO_EXPERIMENT
updated: 2026-11-11
tags: world-expansion, preregistration, research-lead, exact-head-review, docs-only, no-execution
author_role: Research Lead (ChatGPT)
review_target: [Draft PR #194 exact head 3d98c13818ebb9078c123b8117b7248470e8a10b](https://github.com/ryonakayama234/DekaSugi/pull/194)
minimal_closure: [WORLD-PREREG-RQ7-20261111-07](WORLD-PREREG-RQ7-20261111-07-minimal-final-clarifications.md)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **文書査読のみ**。本書は CAL プロトコル承認、CAL 実施 GO、CAL、事前登録凍結、実装、学習、正式評価、結果認定、PR Draft 解除、main マージを行わず、許可しない。数値はすべて候補。以下は本文の静的な論理・統計的整合性の査読であり、実験・CAL シミュレーションの実施ではない。

## 0. 対象固定・採用された決定

- **唯一の現行正本**: [`WORLD-PREREG-SPEC-20261110-05` §0〜§7・付表A](https://github.com/ryonakayama234/DekaSugi/blob/3d98c13818ebb9078c123b8117b7248470e8a10b/docs/research/WORLD-PREREG-SPEC-20261110-05-specification-pack-v5.md)、Git blob `82a2ff16a0f057dba7f9c89cae9a357d827d1bbc`。-01〜-04 は履歴として扱い、有効な規則と混在させない。
- **存続する条文**: 同一 head のドラフト v2 のうち、v5 **§0.1 の明示置換対象ではない部分のみ**を検査する。v5 §0.2 は自己申告の索引であり、判定の代用品としない。
- **監督者判断と Owner 採用**: [Muse コメント 6782396877](https://github.com/ryonakayama234/DekaSugi/pull/201#issuecomment-6782396877)、[Owner 記録 6782523555](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6782523555)。Muse は RQ6 PATCH 1〜5 を ACCEPT_WITH_EXPLICIT_EDIT（E1〜E3）として受け入れ、Owner は**第5版への設計反映**を採用した。これを CAL 承認と混同しない。
- **判定基準**: PASS = その論点の設計ルールが矛盾なく閉じ、数値・実行用 manifest の生成が後日でも事前に固定する入力/権限/判定が指定されている。PARTIAL = 核心設計は合理的に修正されたが、正式に承認する前に機械可読な同じ結果を導くための契約補完が必要。FAIL = 数学的に不成立か、主張の中核を覆す未解消の矛盾。実測がないこと、CAL の数値が未凍結なこと、E2 により全 ACL 行を後日生成すること**だけ**では減点しない。

**R7 再判定: B1 PASS / B2 PASS / B3 PASS / B4 PARTIAL / B5 PARTIAL / B6 PASS。PASS 4、PARTIAL 2、FAIL 0。** 第4版の具体的欠陥は大幅に閉鎖したが、以下の **2件の最小入力/名前空間契約**が現行 v5 本文に残るため、**現時点では設計合意未成立**と判定する。前回の fail を修復済みなのに再び FAIL とすることはしない。

## 1. B1〜B6 — §0.2 と独立に本文・付表を判定

| 対象 | 判定 | 実際の本文で確認した閉鎖点／残件 |
|---|---|---|
| **B1 goal contract／識別可能性** | **PASS** | §1 は TRAIN の law 同定と未見 law の EVAL 暫定推論を分離。marker pair `ABAB/ADAD` は **H≥9 で失格**と記録し、証人が存在すると仮定しない。新しい候補は §6 K0-a の停止判定に服する。公開デモ、tag 射影、feedback 境界、Sym 入手経路も §1/§2 に規定。証人が見つからない場合は主張範囲を下げる規則が存在し、未観測の CAL 値を PASS の条件とはしない。 |
| **B2 seed grammar／arm 権限** | **PASS** | §2 の Space／登録集合／Sym α-equivariance、非対応 token table と特徴語彙、§3 の8 arm・READ(PUB)=allow/READ(SEC)=deny・要約アクセス表・デフォルト deny を確認。**E2 により全正規化 ACL 行は CAL プロトコルの manifest 成果物**と明示されており、この委任自体は矛盾ではない。全 arm の候補評価コスト・trace digest は同じ原則のもとで記帳する。 |
| **B3 K0-a/b/c、UNKNOWN** | **PASS** | §6 K0-a は `DONE_SUCCESS` 吸収、経過ステップ数を BFS 状態へ含め、逐次成功を open-loop 陽性と数える。公開条件付き方策は別の履歴木 DP、同一 law/異なる law の対象分離、上限超過 UNKNOWN を規定。§6 K0-b は TRAIN/EVAL 2列、K0-c は抽象 support のみを読み、非完結を UNKNOWN。E1 の H 固定と再確認は CAL プロトコル入力に置かれた。 |
| **B4 AULC／PPS／検出力／route** | **PARTIAL** | §4/§5 の F・H・q・HT `Σ(q_l/π_l)Δ_l`、certainty `q_l`、Sampford、H のみ FINITE_DESCRIPTIVE、m=10、α 推論と power 計画の分離は整合し、R6 の route 欠陥は解消。**残件 S1**: §5 は `θ*` 下で joint-power simulation を実施すると定めるが、§6 E3 で列挙して閉じた BLIND_DESIGN_CALCULATOR の READ に **CAL 分散・共分散要約または10成分の同時 synthetic-outcome 生成分布**が明示されない。§5 の `Δ*,G1*,G2*,Contrast*` と H/q/cluster だけでは10 gate の同時分布・max-T 分布、したがって `P_joint` が一意に定まらない。RQ6 PATCH 4 の提案入力にあった「CAL 公開してよい分散要約」の経路も第5版の閉じた READ 列挙から欠ける。これは**単に CAL 数値が未収集だから**ではなく、どの型の入力を許可するかという契約不足。 |
| **B5 帰属・等価性・outcome** | **PARTIAL** | §6 は K4 汚染時の主標本 1件による `STOP_INVALID`、valid-only 再集計禁止、3階層の状態と、5 outcome の残余分類を明文化。K2 の両側等価性と主片側検定の α account も分離。**残件 S2**: §4/§6 の run 完了後しか計算しない**推論の `outcome_kind`** と、§6「ログ schema」にある episode ごとの `outcome_kind=(SUCCESS/FAIL/ABSTAIN/FAULT_ACTION)` が**同じキー名で異なる型・有効化時点**を要求する。明示した schema 名前空間がないと、run 停止中の episode ログを失わずに機械可読判定を実装する仕様が一意でない。 |
| **B6 CAL／封印／段階決定** | **PASS** | §7 の6状態、初期候補の lock と CAL 完了時に許された1回改訂、CAL calculator 実行への**独立 Owner GO**、§6 CAL oracle と calculator の別ロール、receipt 出力の列挙、sealed holdout の outcome 非アクセス、manifest mismatch の fail-closed を確認。S1 の**追加 READ 型をどう許すか**は B4 の問題として再判定し、B6 に二重算入しない。もし追加 read を要求するなら §6 ACL に明示し、§7 の CAL_GO 境界を保持すること。 |

## 2. PATCH 1〜5 と E1〜E3 の実装監査

| 採用済み要件 | 確認結果と第5版の根拠 |
|---|---|
| **PATCH1 + E1** — H≥9 失格、OPEN_LOOP_WINS/吸収/BFS 経過ステップ、H 固定 | **反映**。§1 の失格記録、§6 K0-a の逐次成功含む固定列・DONE_SUCCESS・ステップ数・UNKNOWN・CAL プロトコル入力。 |
| **PATCH2 + E2** — selection の pos/r、opaque token、READ×USE要約/後日 ACL 全展開 | **反映**。§2 の token table（順序/表示名は正解役割と非対応）、§3 の全8 arm 要約＋全正規化行を CAL プロトコル manifest とする明示規則、付表A の `pos=selection?min(anchor,head):cursor`、INSERT/PASTE 原子的遷移式。 |
| **PATCH3** — F/H route 一貫、invalid→STOP、結果階層 | **反映**。§5 の STATISTICAL・FINITE_DESCRIPTIVE・STOP_UNKNOWN が H だけを対象、§4/§6 の K4 STOP_INVALID と valid-only 再推定禁止、family_status と推論 outcome を分離。**S2 は残存するログ列名の問題**であって PATCH3 の STOP 意味論自体への反対ではない。 |
| **PATCH4 + E3** — calculator 独立ロール/封印、列挙 READ/receipt、CAL GO | **構造は反映、S1 の入力源だけ PARTIAL**。§5 計算主体、§6 calculator ACL の READ/禁止内容と7つの receipt 欄、§7 CAL GO。読取集合を閉じた際に synthetic joint outcome モデル・CAL の合法な分散情報が型として列挙されていない。 |
| **PATCH5** — α と power 集合の分離、K2 accounting、10pp実用ゲート | **反映**。§5 は α 0.0125/0.00625/0.00625、power 10成分×β0.02、§6 K2 は両側区間の別 account、10pp を追加の有意差検定にする場合の α 事前配分を規定。 |

**E1〜E3 の形式的な取り込み自体はすべて確認した**。S1/S2 は新規の、あるいは第5版を機械可読に追ったことで判明した別種の契約残件であり、受け入れ済み PATCH 全体を否定するものではない。

## 3. 新たに顕在化した不整合と重大度

- **S1（blocking、§5 power／§6 calculator ACL）**: 10ゲートの**周辺平均**と PPS 設計情報だけでは **同時通過確率**を計算できない。例えば二つのゲートの周辺通過確率がともに0.9であっても、完全同時失敗なら同時通過0.9、失敗が排反なら同時通過0.8となる。10ゲート/max-T では同時依存をさらに必要とする。E3 の closed read set に、承認する入力モデルの型／CAL の公開可能な多変量要約の合法経路が欠けるため、設計計算を第三者が再現できない。**数値未凍結の問題ではなく入力型の不足**。
- **S2（schema 型衝突、§4/§6）**: `outcome_kind` の名称が、run 完了後の NEGATIVE/SMALL_EQUIVALENT/POSITIVE/BELOW_THRESHOLD_POSITIVE/INCONCLUSIVE と、episode 逐次ログの SUCCESS/FAIL/ABSTAIN/FAULT_ACTION で二重使用。両レベルを区分すれば矛盾は解消するため、実験設計そのものの否定ではない。
- **S3（要注意、非 blocking）**: `H` が §5 では holdout law frame、§1/§6/付表A では試行ホライズンを表す。同じ文字の型が異なる。文脈で判別できるが、CAL manifest と型付き DSL では `H_laws` と `T_horizon` に変えると安全。前記 S1/S2 と違い、これ単独で PASS を取り消すものではない。
- **S4（要注意、非 blocking）**: §7 `CAL_AUTHORIZED` の「読み取りは CAL/source の抽象定義に限定」は、§6 の calculator が許可される split 設計メタデータと字面上重なる。§7 の一般 CAL oracle 制限に対し、**§6 に列挙した評価側 calculator の設計メタデータだけを明示的な特例**として参照すればよい。実測 holdout の閲覧は引き続き禁止。

S1/S2 以外を理由に新たな設計ラウンド全体をやり直す必要はない。**PATCH と E1〜E3 の受け入れを撤回する趣旨ではない**。

## 4. 設計合意の可否と Owner の次段

**現行第5版にはまだ設計合意を宣言しない**。したがって「今この瞬間、残る手続きは Owner の CAL プロトコル承認判断のみ」と断言できない。

ただし残件は **二つの最小契約補完 S1/S2**に絞られる。新しい評価系、法則族、arms、閾値、K0 の仕組み、抽出法、route、権限段階の変更は求めない。[別紙 RQ7](WORLD-PREREG-RQ7-20261111-07-minimal-final-clarifications.md) に**差し替え可能な規範文と最小反証試験**を記載した。Muse に本2条項を一括で ACCEPT/EXPLICIT_EDIT/REJECT と判断してもらい、Owner が採用して最小差分を正本へ反映すれば、次回の exact-head 確認で B1〜B6 全 PASS に収束できる可能性が高い。ただし**現状の全 PASS は先取りしない**。

**その後に残る第一の意思決定が Owner の CAL プロトコル承認可否**となることと、**その承認が CAL GO/凍結/実装/評価 GO を含まない**ことは区別する。§7 の段階決定表を維持。

## 5. 非実施と監査

検証は GitHub 上の指定 head の文書・Muse comment・Owner comment の静的照合のみ。BFS、CAL、power simulation、学習・実験は未実施。現行 PR #194 の Draft 状態を変更せず、docs-only の審査文書を別 Draft PR で提出する。
