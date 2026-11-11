# WORLD-PREREG-R8-20261111-08 — Research Lead 仕様パック第6版 exact-head 最終判定・設計合意認定

id: WORLD-PREREG-R8-20261111-08
status: research_lead_final_review / DESIGN_CONSENSUS_PASS_B1_B6 / CAL_PROTOCOL_APPROVAL_PENDING / NOT_FROZEN / NO_CAL_APPROVAL / NO_CAL_GO / NO_IMPLEMENTATION / NO_EXPERIMENT
updated: 2026-11-11
tags: world-expansion, research-lead, preregistration, specification-pack-v6, exact-head-review, design-consensus, docs-only, no-execution
author_role: Research Lead (ChatGPT)
target_pr: [PR #194](https://github.com/ryonakayama234/DekaSugi/pull/194)
target_head: 351016fe0e2d468c80736a477133a274cfb713b8
target_spec: [WORLD-PREREG-SPEC-20261110-06](https://github.com/ryonakayama234/DekaSugi/blob/351016fe0e2d468c80736a477133a274cfb713b8/docs/research/WORLD-PREREG-SPEC-20261110-06-specification-pack-v6.md)
decision_record: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **設計文書の最終確認のみ。** 本書の PASS／設計合意は実行許可ではない。CAL プロトコル承認、CAL 実施 GO、CAL、事前登録凍結、実装、学習、実験、正式評価、結果認定、既存 Draft PR の解除・マージは**行わず、許可しない**。数値はすべて凍結前の確定候補である。B1〜B6 PASS は研究設計の**契約上の閉鎖**を意味し、現実世界の達成率や実験の成功を保証しない。

## 0. 審査根拠と有効範囲

- **完全固定対象:** [Draft PR #194](https://github.com/ryonakayama234/DekaSugi/pull/194) の head `351016fe0e2d468c80736a477133a274cfb713b8`。正本は `docs/research/WORLD-PREREG-SPEC-20261110-06-specification-pack-v6.md`、Git blob `9362065507791ced44e2a3cc218c93a0b3cef395`、§0〜§7 および付表A。仕様 -01〜-05 は**履歴**とし、旧条項を第6版の有効規則に混ぜない。第6版 §0.1 で明示的に置換されていない v2 の範囲だけを存続する設計前提として扱う。
- **Muse 受け入れ:** [PR #202 コメント 6783402893](https://github.com/ryonakayama234/DekaSugi/pull/202#issuecomment-6783402893)。`S1-A` と `S2` は ACCEPT、`S1-B`（新 ACL）は**不採用**。`S3`（H の二義）は CAL プロトコル schema で対処。明示修正として `S4` の §7 一文を採用。
- **Owner 採用:** [Issue #195 コメント 6783478862](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6783478862)。採用対象は上記の**設計改訂**であり、CAL プロトコル承認ではない。
- **独立照合の方法:** v6 §0.2 の自己申告対応表は根拠としない。同一 exact head 上の v5（blob `82a2ff16a0f057dba7f9c89cae9a357d827d1bbc`）と v6 の行単位差分を照合し、v6 **§1/§2/§3/§4/§5/§6/§7/付表A** へ戻って確認した。差分は新設 `G_θ` 規範、calculator read の解析規則内訳、episode/run outcome の名前変更、S4 の CAL_AUTHORIZED 例外、版・対応表の更新に限られる。旧フィールド `outcome_kind` の**独立した識別子**は v6 に残っていない。

## 1. 最終 verdict — B1〜B6

| 項目 | v5 Lead R7 | v6 Lead R8 | 第6版の根拠と判定 |
|---|---|---|---|
| **B1: goal contract・公開識別可能性** | PASS | **PASS** | §1 は TRAIN law 同定と EVAL episode 暫定推論を分離し、task tag の非意味化と公開 demo/feedback 境界を固定。§1 証人 `ABAB/ADAD` は H≥9 で固定列に負ける失格例として明記。§6 の K0-a が正しい仮説境界に従って STOP を定義。v6 差分による情報逆流なし。 |
| **B2: Space・grammar・arm/read 境界** | PASS | **PASS** | §2 は純構文 Space/正準形/統一文法および `Alphabet(phase)` の opaque `Sym` 改名等変性、§3 は8 arm・READ(PUB)/READ(SEC)・贈与 AST・PRED-ONLY 第一階マクロの能力差を維持。全量正規化アクセス行は§3が CAL プロトコル manifest の事前承認成果物に指定（Muse E2 の受け入れ済み手順）。v6 で新 learner read の追加なし。 |
| **B3: K0-a/b/c・UNKNOWN** | PASS | **PASS** | §6 は open-loop の `DONE_SUCCESS` 吸収・経過ステップを BFS に記録し、条件付き方策を公開履歴木 DP で別検証。K0-b は TRAIN と EVAL の識別列を分離し、K0-c oracle は abstract support のみに限定。上限超過 UNKNOWN／二階帰属 STOP は継続。G_θ 導入は CAL 計画系の入力定義であり K0 の成功を仮定しない。 |
| **B4: 推定対象・PPS/HT・joint power・route** | **PARTIAL** | **PASS** | §4/§5 で `F`→`H=F∩holdout`、`q_l` と `Σ_{sample}(q_l/π_l)Δ_l`、certainty weight `q_l`、H のみの finite description、汚染時再集計禁止を維持。§5 は **10 gate の joint synthetic outcome generator `G_θ` を全確率モデルとして明示**し、law/親 cluster の対差、G1/G2 成否、依存構造、分散・共分散、checkpoint 間の関係、max-T の計画を含めた事前登録の**シナリオ識別子**を `θ*` に要求。モデル候補・選択関数・感度ケース・digest/read path は `PROTOCOL_APPROVED` で lock、CAL 観測後の選択は禁止。model 不完全なら `STOP_UNKNOWN`。§6 calculator read は既存の閉じた `解析規則` に `G_θ` の構成を追加明記し、S1-B 新 ACL はない。同時検出力は **G_θ に条件付く設計値**であり、実測性能の保証ではない。S1 の入力型不足は閉鎖。 |
| **B5: 等価性・result/error status・null/invalid** | **PARTIAL** | **PASS** | §4 は集約結果を `run_inference_outcome` と呼称。§6 は run status COMPLETE かつ有効集約のときのみ5分類、未完/STOP では **null**。§6 の episode ログ列は `episode_outcome_kind`（SUCCESS/FAIL/ABSTAIN/FAULT_ACTION）となり、run 停止時も監査台帳に残す。§7 は `run_inference_outcome` の決定順序を固定する規則に名称統一。family_status の `FAMILY_INVALID` と K4 の `STOP_INVALID`、valid-only HT の禁止は存続。二義の `outcome_kind` は除去され S2 閉鎖。 |
| **B6: 承認・封印・改訂可能性** | PASS | **PASS** | §7 の6状態（DESIGN_DRAFT→PROTOCOL_APPROVED→CAL_AUTHORIZED→CAL_COMPLETE→FROZEN→EXECUTION_GO）と3区分の改訂規則を維持。§7 CAL_AUTHORIZED に**§6 に列挙した評価側 calculator 設計メタデータ read だけを抽象定義制限の明示例外**とする S4 を追加。実 holdout instance/target/score/seed の read は引き続き禁止し、calculator 実行は**別途 CAL GO**後のみ。Learner への新たな権限なし。 |

**計数: PASS 6 / PARTIAL 0 / FAIL 0。Research Lead の設計判定: ACCEPT — DESIGN CONSENSUS ACHIEVED（現行第6版 exact head に限る）。**

これは **Research Lead の設計査読上の合意認定**であり、Owner の CAL プロトコル承認を代理しない。全項目 PASS の根拠は候補値が確定したからではなく、**候補値・アルゴリズムの計画/封印/停止を定める契約が矛盾なく与えられた**からである。

## 2. Muse R7/RQ7 受け入れ内容の全量確認（§0.2 非依存）

| 要件 | v6 の実際の条文・検証 |
|---|---|
| **S1-A：`G_θ` を10ゲートを再現可能な全確率モデルとして宣言** | **§5** `joint outcome の生成モデル G_θ` で law/cluster のペア差、G1/G2、相関・分散、checkpoint、max-T、scenario digest を列挙。 |
| **S1-A：PROTOCOL_APPROVED で scenario 選択・感度ケース・digest を lock** | **§5** は `θ*→G_θ` 選択関数、model digest/read path を承認時 lock。CAL 難度・holdout outcome の事後確認後に選ぶことを禁止。 |
| **S1-A：モデル依存の計画値／不完全なモデルでは STOP_UNKNOWN** | **§5** の同段落末尾を確認。`P_joint` を実分布上の真の power と偽称していない。 |
| **S1-B 不採用、新 ACL を作らない** | **§6** の calculator ACL は旧来の closed READ に `解析規則（G_θ のシナリオ候補集合・選択規則・感度ケース・モデル digest）` と明記するだけ。`CAL_JOINT_SUMMARY` 等の新しい read 権限は追加されていない。 |
| **S2：`episode_outcome_kind` と `run_inference_outcome` の型・時点分離** | **§4** は run 結果分類の名前変更。**§6** は episode 台帳の outcome 列と run 集約の決定順序・null を分離。**§7** の決定規則の名前も一貫。旧独立 field `outcome_kind` は登場しない。 |
| **S4：calculator の design read 例外のみ** | **§7 CAL_AUTHORIZED** は `§6` を参照し、設計メタデータのみ明示例外、実 instance/target/score/seed の read を禁止。calculator 実行に CAL 実施 GO を必要とする規則も維持。 |
| **S3：H の二義は CAL schema で区別** | 第6版 **§5 の `H` は holdout law frame**、**§6／付表A の `H` は horizon** のまま。Muse が非 blocking として CAL プロトコル schema で `H_laws`／`T_horizon` の型別命名を要求した通り、本文の記法を全面改変していない。 |

第5版への R6 PATCH1〜5＋E1〜E3 は、§1/§2/§3/§5/§6/§7／付表A で維持。**§0.2 の対応先だけではなく意味論・アクセス表・ログ列と入力型を独立に読んだ**。

## 3. 新規不整合の探索結果と非 blocking の残作業

**現行第6版で新たな blocking inconsistency は発見しなかった。** 第5版からの行単位差分（version/front matter/対応表の更新を除く）は S1-A の1段落、§6 calculator 解析規則、`run_inference_outcome`／`episode_outcome_kind` の名称統一、§7 の S4 例外に対応し、設計の中心的な数量/方策/権限を逸脱していない。

なお、以下は **CAL プロトコル承認までに具体化すべき入力・監査成果物**であり、R8 によって確定済みと偽ってはならない。

1. **`G_θ` の具体化**: 10ゲートの joint law/cluster generator、感度シナリオ、選択関数、モデル digest、simulation 反復数/乱数源/片側下限の方式。固定後のモデル条件付き power を**実際の未知分布における保証と誤表示しない**。
2. **解析・統計/route の具体化**: `θ*` の ε の許容域と選択関数、Sampford 実装契約、`π_l/π_{ll'}`、HT/SYG/max-T、K2 両側等価性の confidence/error accounting、m=10 の joint-power、H のみの有限記述 route、cost_cap と停止条件。入力不足は `STOP_UNKNOWN` とする。
3. **manifest/型契約**: §3 の arm×node×constructor×READ×USE 全量正規化表（E2 指定成果物）、`H_laws` と `T_horizon` の型別名（S3）、`episode_outcome_kind` と `run_inference_outcome` を別の episode/run スキーマで表現・保存する仕様、role ACL・receipt/digest・漏洩監査。
4. **ゲートの独立性**: Owner の `PROTOCOL_APPROVED` は、決定規則・候補初期値・許可改訂範囲・read path・モデル選択を lock する判断であり、`CAL_AUTHORIZED`、`FROZEN`、`EXECUTION_GO` は**別の Owner 判断**。CAL/実験は未実施。

第6版の S4 は evaluator calculator read の例外を明示したが、正式 holdout の outcome や law の正解情報の漏洩権限を加えていない。旧 `outcome_kind` の二義も再出現していない。

## 4. 設計合意と残る Owner 判断

**YES — 第6版 `351016fe0e2d468c80736a477133a274cfb713b8` に関する B1〜B6 の Research Lead 設計合意は成立。** 以前の R1〜R7 の FAIL/PARTIAL と Muse 監督者の ACCEPT_WITH_EXPLICIT_EDIT の履歴を消すものではなく、採用された最小差分が現行正本に組み込まれたことを確認したものである。

**YES — 次の設計手続き上の承認判断は、Owner の CAL プロトコル承認可否のみ。** その判断のためには、前節の具体的な CAL プロトコルと manifest が**まだ作成・提示される必要がある**。「設計合意成立」と「CAL プロトコルの作成済み・承認済み」は同義ではない。

**NO — CAL プロトコル承認は現時点で行われていない**。CAL 実施、事前登録凍結、実装、実験の GO もない。今後の工程ごとに §7 の6状態に従い Owner の独立した明示承認が必要。現在の PR #194 は Draft に維持、別の docs-only Draft PR でこの審査記録のみを提出する。
