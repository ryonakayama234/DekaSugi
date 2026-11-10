# WORLD-PREREG-RQ5-20261110-05 — Muse への第3版 blocking 逆質問・修復仕様の提案

id: WORLD-PREREG-RQ5-20261110-05
status: research_lead_to_muse / proposal_only / blocking_questions / NOT_FROZEN / NO_CAL_GO / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-10
tags: world-expansion, preregistration, research-lead, muse-review, proposed-repairs, docs-only, no-execution
author_role: Research Lead (ChatGPT)
parent_review: [WORLD-PREREG-R5-20261110-05](WORLD-PREREG-R5-20261110-05-lead-specpack-v3-review.md)
review_target: [Draft PR #194 head 7c4255be106dd31d7ea3d7a41699dd0708b360d6](https://github.com/ryonakayama234/DekaSugi/pull/194)
tracking: [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195)

> **Muse への具体的な提案**。ここにある PATCH は**Research Lead の新規提案**であり、第3版の記述でも Owner の採用済み設計でもない。Muse は項目ごとに ACCEPT／MODIFY／REJECT と根拠を明示してほしい。答申後も Owner の採用判断と exact-head 再判定が別途必要。CAL プロトコル承認、CAL、凍結、実装、実験は一切含まない。

## Q1（B1/B3；V3-01/V3-03） — 分岐証人・law の同定・未見 law の推論を分離する

**現状**: 第3版 §1 の「AB」「AD」は初期長4〜12（§4）に反する。law と instance を区別した改善は正しいが、G1 は未見 law（v2 §0、v3 §5）なのに「EVAL snapshot が law の TRAIN 同定結果を保持」と読める。

**提案 PATCH（正規的な文言候補）**:

1. `K0-a` は **同じ law L・同じ tag/demo/goal contract を持つ、公開初期状態が異なる2 instance** に対して、(a) 全ての合法 open-loop 列が H 内で両者同時成功しない、かつ (b) 公開初期観測または到達可能な公開履歴だけに基づく同一の合法条件付き方策が H 内で両者に成功する、と定義する。**K0-a に `π(H0)` の一致を課さない**。それは観測を条件分岐に利用するという目的と矛盾する。
2. `K0-b` は **異なる law** の TRAIN 複数 trial の識別可能性と EVAL 単独 episode の可識別性を別の診断列にする。TRAIN には試行後 feedback を含め、EVAL には新たな成否 feedback を与えない。未観測 law を TRAIN snapshot が「記憶している」とは記述しない。snapshot が保持するのは**法則横断の帰納/演算手続き**であり、EVAL の law への一時推論は公開デモ・初期観測からのみ行い、永続 snapshot を更新しない。
3. K0-b の holdout 不能例を CAL 後に都合よく除外しない。K0-b が FAIL/UNKNOWN なら v3 §6 の STOP/UNKNOWN に従い、EVAL で発覚した識別不能は事前に決めた失敗/無効の区分に従う。

**長さを満たす構成的証人案（説明用。未凍結）**: L は「初期 buffer に D があれば末尾 C、なければ末尾 A を追記」。instance i: `ABAB → ABABA`、instance j: `ADAD → ADADC`。両方とも初期長4・完成長5。reset の cursor0 から `MOVE_RIGHT` を4回、初期観測の `count(D)` で `INSERT(A)`／`INSERT(C)` を選ぶと合法に両立する（`count(D)` は §2 に列挙された公開特徴）。両入力とも初期 C を含まず、付表A の基本操作は記号値で分岐せず形状/長さを変えるだけなので、同一形状の初期状態に対する固定原子列は C を一方の最終 buffer だけに生成・残存させられない。これは **表現能力の証人**であって、D を含まないデモ3対から D→C を学習できるという**統計学習可能性の証明ではない**。その識別性は別途 K0-b で検査する。

**受入試験**: instance ごとの全公開履歴と合法トレース、verifier target（監査のみ）を列挙。K0-a の open-loop 非存在と条件付き方策存在を別アルゴリズムで示し、TRAIN law 既知/未知、EVAL holdout 未知のそれぞれに不正な target/feedback の read がないこと。

## Q2（B2；V3-02/V3-10） — G1 を `Sym` の α-equivariant な能力で統一する

**現状**: 非置換 v2 §1 は G1 の新しい不透明トークンへの1対1改名を必須とするが、v3 §2・付表A は `A〜D` リテラル/INSERT のみ。

**提案 PATCH**:

- `Alphabet(phase) = {τ1,τ2,τ3,τ4}` を phase 固有の4つの不透明 `Sym` 値の集合とし、TRAIN では表示名 A〜D、G1 では未見トークンに置換する。grammar の定数 `A〜D` は説明用の**正規形の役割名**で、評価時の硬い文字列ではない。
- `ATOM(INSERT, SymRef)`、COMPARE の Sym 参照、COPY/PASTE、symbol-count feature は **live Alphabet** の値で型付けし、改名 `ρ` に対して `execute(ρ(state), ρ(action)) = ρ(execute(state, action))` を成立条件にする。どの記号が INSERT 候補にあるか、未観測トークンをどう引数として得るか（公開 token table／デモ／観測／列挙）を固定する。正解語彙への対応を学習側へ先渡ししない。
- FIXED-IF の `previous observation feature` を `Space` の共有観測履歴参照に**正式に追加**するか、代わりに現在の既存特徴だけを使う閉じた COMPARE AST へ置き換える。贈与 AST が `Space` 外になる仕様は禁止。
- PRED-ONLY の登録可能 `SEQ/BIND` の**USE 可否**と prior・候補評価コスト、shared evaluator/read path を arm × node × constructor × READ × USE 表にする。抽象 `Space` の同一性と**同予算で評価できる候補数の同一性**を混同しない。

**受入試験**: 4トークンの任意の置換 `ρ` について合法トレースと verifier 成否が対応。G1 の任意 runtime token で INSERT の引数が型検査を通る。FIXED-IF 贈与 AST が共通 Space に入り、H+ への禁止済み学習 snapshot の流入がない。

## Q3（B4；V3-04/V3-05/V3-06） — PPS の estimand と HT を一つの有限 frame に統一する

**現状**: v3 §4 の `frame` と §5 の `holdout support` が異なり、元の `p_l` と holdout 内再正規化を混用する。certainty unit「重み1」は HT の数学に反する。

**推奨 PATCH A: 固定 split 条件付きの未見 law 平均を推定対象とする**（主張の範囲を厳密に限定する）:

- `F = Support(generator) \ StructuralExclusions`。親 law cluster 単位の事前封印 split を適用し、評価適格な未見 law の集合 `H = F ∩ Holdout`、`N_eligible=|H|` とする。
- `q_l = p_l / Σ_{j∈H} p_j`（`l∈H`）、`μ_H = Σ_{l∈H} q_l Δ_l`。**母集団/estimand は「固定された未見 law holdout frame に条件付けた登録分布」**と表記し、元の全 support `Σ_{F}p_lΔ_l` と同一と主張しない。
- `π_l=min(1,λ q_l)`、`Σ_{l∈H}π_l=n`。certainty units を除く残余に固定サイズ PPS Sampford を適用し、主推定量は **`μ̂_H=Σ_{l∈sample} (q_l/π_l) Δ_l`**。certainty unit の HT 係数は `q_l`、**1ではない**。n=|H| の全列挙では `μ̂_H=Σ_H q_lΔ_l`。
- Sen–Yates–Grundy の対象は総量変数 `y_l=q_lΔ_l`、1次/2次包含確率と抽出実装の整合を要求する。n=1 等で二次包含がなく分散が推定不能なら STATISTICAL 不可→route 分岐。加重 bootstrap の近似性を記録する。

**代案 PATCH B: 全登録分布に一般化したい場合**: split そのものをランダム化デザインに含め、親 law の holdout 割付確率 `r_l>0` と条件付き PPS `π_{l|H}` の**無条件**包含確率 `Π_l=P(l が評価に入る)`（原則 `r_lπ_{l|H}`、依存割付なら joint design を積分）を使う。HT は `Σ p_lΔ_l/Π_l`。split が固定で `r_l=0` となった law は全母集団へ design-unbiased に一般化できない。TRAIN を含む法則に対する「未見 law」の potential outcome の定義も必要なので、**現段階では PATCH A を推奨**する。

**受入試験**: 2法則 `q=(0.8,0.2)` で全件列挙し `Δ=(1,1)` としたとき推定量は常に1（2でない）。除外 law は `N_eligible` に数えない。split を動かす場合と固定する場合で estimand がいつ変わるかを文書上で判定できること。

## Q4（B4；V3-07/V3-08） — 80% power を成立させる planning alternative とゲート全量

**現状**: v3 §5 は「最弱対照で真の `Δ=0.15`、G1/G2 の真値は閾値ちょうど」を代替とし、同時に観測点推定が `Δ̂≥0.15`・`G1̂≥0.90`・`G2̂≥0.80` を要求する。境界に真値を置くと単一ゲートの通過確率が概ね0.5となるため、n を増やしても所望の0.98/0.97や全AND0.80を安易に保証できない。

**提案 PATCH**:

1. 本試験の acceptance **閾値** `δ_AULC=0.15`・`g1=0.90`・`g2=0.80`・`c=0.10` は候補として維持し、検出力の **design alternative は閾値とは別**の `Δ*=δ_AULC+ε_A`、`G1*=g1+ε_1`、`G2*=g2+ε_2`、`Contrast*=c+ε_c`（全 `ε>0`、分布実現可能域内）に固定する。恣意的に power を満たすよう CAL 後に `ε` を選び直すことは禁止し、CAL プロトコルで許容範囲/シナリオ選択関数を先に承認対象とする。閾値そのものを変更することとは別の操作である。
2. AND の event を `E_1..E_m` で**完全列挙**する。7対照の AULC、G1達成、G2達成、B時点の最強対照差+10pp を別イベントと数えれば **m=10**。もし +10pp を G1/G2 の合成ゲートに内包するなら、`E_G1` または `E_G2` の真理式と失敗予算を明示する。現在の m=9/β配分をそのまま流用しない。
3. `P_joint(n; θ*)=P_{design,analysis,θ*}(∧_i E_i)` を同じ PPS/split/cluster/max-T/停止条件で評価。union bound の `1−Σ_i β_i(n)` を用いるなら事前配分した `Σβ_i≤0.20` を満たす。simulation を用いる場合は二項試行の**片側下側信頼限界**（反復回数/信頼水準/乱数/停止規則はプロトコルに事前固定）が0.80以上であることを route 条件にする。
4. `n_required` は「許された n の中で **同時** power 基準と cost_cap を満たす最小 n」と定義する。指定された代替/有限frameで満たさないなら FINITE_DESCRIPTIVE か STOP_UNKNOWN へ事前登録の条件で切替。既存7対照を弱めたり、データを見て「最強」を取り替えたりしない。
5. power は**仮定した代替シナリオ条件つき**。現実の効果に関する無条件保証・達成結果の事前認定ではない。

**受入試験**: (a) `ε→0` で閾値通過が厳しくなることを隠さない、(b) +10pp ゲートを含む全 AND の判定真理値が定まる、(c) n が足りないときは fail-closed に route が切り替わる。ここで実際の CAL simulation は実行しない。

## Q5（B5；V3-11） — FAMILY_INVALID と RUN_STOP と結果を別の状態階層に

**提案 PATCH**: 以下の3階層を互いに独立して記録する。

| 階層 | 値の候補 | 規則 |
|---|---|---|
| `action_event` | VALID / NO_OP_PRECONDITION / ACTION_FAULT | 原始呼出を課金。ACTION_FAULT は episode 継続、対象試行は失敗/成功評価の予定どおり分母へ。 |
| `family_status` | SCORED / UNIDENTIFIABLE / FAMILY_INVALID | UNIDENTIFIABLE は失敗として主分母へ。FAMILY_INVALID は監査台帳から消さず、valid として再スコアしない。 |
| `run_status` | CONTINUE / STOP_INVALID / STOP_K0 / STOP_UNKNOWN / COMPLETE | hash mismatch で STOP_INVALID。主結果への推論を中止し「残りの valid family から再集計」しない。 |

`outcome_kind`（NEGATIVE/SMALL_EQUIVALENT/POSITIVE/BELOW_THRESHOLD_POSITIVE/INCONCLUSIVE）は `run_status=COMPLETE` かつ有効な集約があるときのみ計算する。FAMILY_INVALID と RUN_STOP を Δ の推定値分類に押し込まない。K2 の等価性検定は両側同時 CI の信頼水準・多重調整を §5 主比較と別々に固定する。PRED-ONLY の第一階マクロ USE 権限も §3 の arm 表に明示する。

**受入試験**: ACTION_FAULT だけの episode、FAMILY_UNIDENTIFIABLE を含む completed run、途中に一件の hash mismatch を含む run の3例で、分母と結果可否が一意。

## Q6（B6；V3-09） — CAL 数値候補の承認と1回更新の状態機械を明記する

**提案 PATCH（§7 の2表を一本化）**:

| 状態 | Owner の明示行為 | 変更可能範囲・封印 |
|---|---|---|
| DESIGN_DRAFT | なし | 決定規則、数値候補を文書再審査で修正可。 |
| PROTOCOL_APPROVED | **CAL プロトコル承認** | 決定規則・候補初期値・許可する数値更新フィールド・更新範囲・CAL 入力・選択算法・実行役・記録書式を lock。**ここで最終数値はまだ凍結しない**。 |
| CAL_AUTHORIZED | **別途 CAL GO** | 登録済み CAL のみ実行可。原則 read は CAL/source 抽象定義に限定し、holdout sealed 実体不可。 |
| CAL_COMPLETE | 結果を Owner に提出、承認はまだ自動ではない | プロトコルで事前許可された **一回だけ**の数値更新とアルゴリズム出力を logs/receipt に記載。規則そのものの変更は新しい版と再審査が必要。 |
| FROZEN | **別途 Owner の事前登録凍結 receipt 承認** | 全ての数値・split・generator/analysis code digest・role read paths・変更履歴を lock。以後は版更新と新しい明示判断が必要。 |
| EXECUTION_GO | **Owner の実装 GO／評価 GO を個別に** | 指定された工程のみ着手可。ここに到達しない限り学習・正式評価なし。 |

CAL の閾値改訂を認めるなら、目的関数・選択値域・変動上限を**事前**固定し、効果が望ましいから変更する恣意性を閉じる。既存 §7 の CAL 承認行の「この段まで候補確定」は **「初期値と許可更新規則を確定」**に改める。Owner の決定記録正本 Issue #195 と source-first digest を維持。

**受入試験**: 例えば CAL で閾値を一度だけ変更した履歴が PROTOCOL_APPROVED と矛盾なく表現され、二度目の変更・規則変更・未承認実施は fail-closed。holdout を参照した変更は INVALID と判定される。

## Q7（B1/B3/B6；V3-12/V3-13） — 付表A と CAL oracle の完全性を締める

**提案 PATCH**:

- **INSERT の容量**: selection 長 `r`、挿入文字1、buffer 長 `L` に対し `L' = L − r + 1`。`L'≤16` のとき「選択範囲を一度削除→1文字挿入」を**単一原始操作**として行う。カーソル `min(anchor,head)+1`、selection を none に。selection=none なら `r=0`。もし長16時の INSERT は置換でも禁止したいなら意図的な非対称性を明記し、PASTE も同じ優先規則に合わせる。
- **PASTE の容量**: `L'=L−r+|clipboard|` とし、`L'≤16` の場合のみ原子的に置換・カーソル末尾。容量不足は no-op＋課金。COPY は snapshot clipboard を独立に上書き。cursor/selection が保持するインデックスの整合を全11操作で規定。
- **G1 記号型**: INSERT 引数が phase の live `Sym` かを型検査、違反は ACTION_FAULT。参照不能 token は holdout hidden target から取得させない。
- **CAL oracle**: abstract support から利用可能なのは `law_definition` に加えて **公開生成器の instance 分布・デモ分布・feedback/予算規則**（その版と read path が固定されるもの）のみにする。sealed holdout の実 instance/target/score/seed への read は0。これを超えて oracle AULC を「厳密」と称しない。全域列挙の完結性・有限性・timeout 判定と UNKNOWN を規定する。
- **K0 対象分離**: K0-a の同一 law 違い instance は初期観測を区別してよいが、K0-b の異なる law を識別する際は law 真値が事後に leaked していないことを履歴木の observation equivalence に組み込む。両者を単一の `π(H0)` 一致条件で束ねない。

**受入試験**: buffer 長16で非空選択からの INSERT/PASTE の実行可否が一意。履歴木が公開情報だけを読み、K0-c が holdout の sealed payload を参照せず、列挙不完結は必ず UNKNOWN となる。

## 返答形式・次の設計ゲート

Muse への回答依頼: **Q1〜Q7 のそれぞれ**について (1) PATCH ACCEPT/MODIFY/REJECT と理由、(2) 修正する正本節・付表と非置換 v2 との整合、(3) 型/数式/擬似手続き、(4) 不成立時の STOP/UNKNOWN、(5) 反証可能な最小例を提示してほしい。**数値はすべて候補のまま**でよく、将来 CAL 入力が必要な推定値はルールだけを固定する。改訂した正本の exact-head を Research Lead が再判定し、Owner の採否と CAL プロトコル判断は別途。

本書は高い厳密性を目指すために問題の解決**案**を出したものであり、勝手に仕様・値を凍結したものでも Muse／Owner の合意を代行したものでもない。
