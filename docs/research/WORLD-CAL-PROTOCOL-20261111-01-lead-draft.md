# WORLD CAL プロトコル確定候補 — Research Lead 起草（未承認）

id: WORLD-CAL-PROTOCOL-20261111-01
status: lead_draft / PROTOCOL_APPROVAL_PENDING / NOT_CAL_AUTHORIZED / NOT_FROZEN / NO_IMPLEMENTATION / NO_EXPERIMENT
updated: 2026-11-11
tags: world-expansion, cal-protocol, research-lead, specification-pack-v6, preregistration, design-only, docs-only
author_role: Research Lead (ChatGPT)
authority: Owner approval required after supervisor review
normative_source: WORLD-PREREG-SPEC-20261110-06
normative_ref: PR #194 / 351016fe0e2d468c80736a477133a274cfb713b8
normative_blob: 9362065507791ced44e2a3cc218c93a0b3cef395

> **本書の全数値は「確定候補」であり、採用済み値でも観測値でもない。** R8（PR #203）の設計合意を受けて §7 の PROTOCOL_APPROVED で lock する入力を起草したもの。監督者審査→Owner 明示承認が必要であり、本 PR の作成は承認行為ではない。CAL 実施・simulation・BFS・凍結・実装・学習・実験・評価を一切実施していない。現行 main 基点、docs-only。仕様パックの条文変更は行わない。

## 0. 正本・権限・優先順位

1. 規範は [仕様パック第6版（exact head）](https://github.com/ryonakayama234/DekaSugi/blob/351016fe0e2d468c80736a477133a274cfb713b8/docs/research/WORLD-PREREG-SPEC-20261110-06-specification-pack-v6.md) の §0〜§7 と付表A。v2 の存続条項は第6版 §0.1 **非置換部分だけ**。過去版 -01〜-05、R1〜R7 は履歴。
2. [R8 設計合意（PR #203）](https://github.com/ryonakayama234/DekaSugi/pull/203) は B1〜B6 の設計上の PASS であり、本書の数値・モデル・権限を既承認にはしない。
3. [Issue #195](https://github.com/ryonakayama234/DekaSugi/issues/195) が Owner 決定記録の正本。違反・欠測・実行不能は成功扱いせず fail-closed。相反する場合は第6版を優先し、解決には新しい設計版・再審査が必要。
4. 本書の「固定」は **Owner が将来 PROTOCOL_APPROVED を明示記録した場合にのみ効力が生じる**。Draft 時点での「固定候補」「将来の手続き規則」は lock の先取りではない。

## 1. 型付き入力スキーマと数値の確定候補

**名前空間（S3、必須）**: \`H_laws: FiniteSet<LawUniqueId>\` は sealed split に属する適格 holdout law の集合（第6版 §5 の H）、\`N_eligible: uint64 = |H_laws|\`。\`T_horizon: uint16\` は一 episode に発行可能な原始 action token の上限（第6版 §6／付表A の H）。**両者の \`H\` という略称をデータ・関数・ログ・receipt に保存してはならない。** \`F_laws\`、\`q_l: probability\`、\`pi_l\`、\`pi_ll\` は evaluator/calculator の private design metadata とし、学習側へ law ID↔重みの対応を出さない。

| 項目 | PROTOCOL_APPROVED での確定候補 | 根拠と採用時 lock |
|---|---|---|
| \`delta_AULC\` / \`δ_AULC\` | **0.15** | 第6版 §5 の主実用閾値。全7対照と最強対照に共通。更新禁止。 |
| \`m_equivalence\` / \`m\` | **0.05** | 第6版 §6 K2 と結果分類の等価幅。片側差と混同しない。更新禁止。 |
| \`g1_gate\` / \`G1\` | **0.90** | 未見法則＋改名の B 時点成功率候補。更新禁止。 |
| \`g2_gate\` / \`G2\` | **0.80** | 長さ13〜16の B 時点成功率候補。更新禁止。 |
| \`contrast_gate\` / \`c\` | **+0.10**（10pp） | FULL−事後最強対照の B 時点の差。**点閾値の実用ゲート**であり別の有意差検定にしない。更新禁止。 |
| \`alpha_primary\` | **0.025（片側）** | 7対照 AULC の max-T 0.0125、G1 0.00625、G2 0.00625。更新禁止。 |
| \`alpha_equivalence\` | **0.05（両側、独立の記述的 K2）** | FULL−REC 等価性の事前区間。主 family-wise 片側 α に混ぜない。更新禁止。 |
| \`beta_joint_total\` | **0.20** | §5 の AND 10成分へ \`beta_i=0.02\` ×10、union bound に使用。更新禁止。 |
| \`n_min_descriptive\` | **30 unique law** | §5 の有限全件記述 route の下限。更新禁止。 |
| \`cost_cap\` | **20,000,000 原始呼出** | 8 arm 合算・CAL 分を含めた保守的作業枠。加重費用と混同しない。更新禁止。 |
| \`B_initial\` | **4,096 原始呼出/arm** | 9 checkpoint を整数化できる8の倍数。§2 の一度きりの条件付更新のみ可。 |
| \`B_max_after_cal\` | **6,144 原始呼出/arm** | 上限は1.5倍。§2 の関数外の任意調整禁止。 |
| \`T_horizon\` | **24 steps/episode**（§6 上限64内） | 長さ16の移動＋編集に余地を与えつつ、有限探索の上限を抑える。**K0 と本試行で同一**、更新禁止。 |
| \`n_train\` | **24 law family** | 先行 v2 の候補、評価 \`n_required\` と別。更新禁止。 |
| \`n_cal\` | **各4族6件、計24 law** | TRAIN 分布から独立に確保、親 cluster を TRAIN/CAL/holdout で隔離。更新禁止。 |
| \`n_k1\` | **20診断 family** | 第6版 §6 の K1 固定候補。更新禁止。 |
| \`n_lookup\` / \`lookup_abstain\` | **512件 / 距離>0.20で棄権** | 第6版 §3 の既定候補。更新禁止。 |
| \`demo_pairs\` | **3 / family / phase** | 第6版 §1 の仕様費、原始呼出課金から独立。更新禁止。 |
| \`eval_replicates\` | **4 instance / law×G1/G2×checkpoint** | 同一 law の複製を独立 n と数えない。抽出後の正準 instance グリッド順。更新禁止。 |
| \`n_search_max\` | **512 unique law** | 512 より上の統計 route は \`STOP_UNKNOWN\`、全件 route の可否は別判定。更新禁止。 |
| \`k0_a_pair_count\` | **最大20 pair（各族5）** | §5 の選択関数による設計診断、陽性は仮定しない。更新禁止。 |
| \`k0_state_cap\` / \`k0_tree_cap\` | **2,000,000 / 2,000,000 states/nodes（各診断）** | メモリ・時間の有限上限。超過は真偽ではなく UNKNOWN。更新禁止。 |
| \`cal_primitive_reserve\` | **250,000 calls** | cost_cap 内の事前 CAL 予約上限。実際の CAL が不足すれば \`STOP_UNKNOWN\`。更新禁止。 |

**金額・時間換算は観測値ではなく仮定を明記した計画表示**: 処理能力を仮に500 calls/sec とした場合、20,000,000 calls = 約40,000秒（約11.1時間）の primitive 層の純処理時間。仮想単価 $0.01/1,000 calls を置けば $200 相当。いずれも実課金・CPU/wall の保証ではない。候補評価、BFS、bootstrap、simulation の CPU は別に費用ベクトルへ記録し、時間・金額を原始呼出へ換算して足さない。

**共通推論条件**: B 点の達成率・AULC は \`H_laws\` 上の \`q_l\` 付き HT。G1/G2 の同一 law を二標本と数えない。8 arm = FULL/OFF/PRED-ONLY/REC/RANK-ONLY/FIXED-IF/LOOKUP/H+。\`Space\` は §2 の正準 AST 全体、初期値 \`depth<=8, nodes<=64, predicate_depth<=3\`、相対位置定数 −16〜16。全 arm の PUBLIC trace は同一 digest、OFF と FULL の TRAIN snapshot は byte-wise digest 一致を必要とする。

## 2. CAL_COMPLETE で許される**1回のみ**の数値更新（関数・上限を事前固定）

- 更新可能な唯一のフィールドは \`B_final\`（整数、8の倍数、上限6144）。その他の表中数値、α／β、\`T_horizon\`、εの関数形、G_θ、\`cost_cap\`、K0/route/CI の決定規則、ACL、read path、split 法、分母は **更新不可**。更新不可のものを変えるにはプロトコル新規版を起草し、監督者再審査→Owner 再承認（既存 run の再解釈なし）。
- 選択統計量 \`L90\`: **TRAIN 分布のみ**から取得した CAL 24 law の容量上有効な全代表 instance について、抽象 oracle による最短成功手数（§5 K0-c の抽象 support の範囲でのみ測る）の nearest-rank 90パーセンタイル \`ceil(0.9*n)\` 番目。法則ごと1件、正準順で決め、失敗/不確定/未列挙を除外してパーセンタイルを再計算してはならない。いずれかが UNKNOWN なら \`STOP_UNKNOWN\`。
- **完全固定の写像**:
  \`B_final = 4096 if L90 <= 12 else 6144 if 12 < L90 <= 24 else STOP_UNKNOWN\`。
  CAL 結果の見た目・arm 性能・正式 holdout・都合のよい閾値を条件に足さない。値を変えない場合も唯一の改訂機会を消費し \`B_final=4096\` と1回だけ記録。別個の2回目の変更は不可。
- 更新後の checkpoint は \`b_j = j * B_final/8 (j=0,...,8)\`。CAL の \`L90\` と費用集計を source-first receipt に残す。ただし外部 calculator の閉じた出力にフィールドを追加しない（CAL 実施者の別台帳）。
- \`n_required\`、\`route\`、\`pi_l\`、\`pi_ll\` は算法出力であって改訂フィールドではない。CAL input が不完備なら数値改訂のように補完せず \`STOP_UNKNOWN\`。

## 3. planning alternative の ε — **承認時固定の純関数**

CAL 観測値を一切引数に取らない。以下は閾値を引数とする有理演算、切り捨てや手動丸めなし。

\`\`\`text
epsilon_A(delta) = min(0.05, delta/3)                  # 0.05
epsilon_1(g1)    = min(0.05, (1-g1)/2)                  # 0.05
epsilon_2(g2)    = min(0.05, (1-g2)/2)                  # 0.05
epsilon_c(c)     = min(0.05, (1-c)/2)                    # 0.05
theta_star:
  Delta_star    = delta_AULC + epsilon_A              # 0.20
  G1_star       = g1_gate + epsilon_1                  # 0.95
  G2_star       = g2_gate + epsilon_2                  # 0.85
  Contrast_star = contrast_gate + epsilon_c            # 0.15
  scenario_id   = "GTHETA-BASE-01"                     # 固定
\`\`\`

ε 許容域は \`0 < epsilon_A,epsilon_1,epsilon_2,epsilon_c <= 0.05\`、planning alternative は各確率・正規化 AULC の実現可能域内。許容域外／入力欠損／境界超過は \`STOP_UNKNOWN\`（εを再選択しない）。**閾値ちょうどの効果を代替にしない**。上記関数とシナリオ ID、感度集合を \`PROTOCOL_APPROVED\` で lock。εは CAL の難易度・分散・成功率による最適化を行わない。

## 4. G_θ : 10ゲートの joint synthetic outcome generator

規範となる**候補モデルのデータ正本**は同一 PR 内 [G_θ JSON](WORLD-CAL-GTHETA-20261111-01-model-candidates.json)。次のシナリオの分布族・係数・条件・選択規則は1セットとして承認時 lock し、CAL 後に使い分けない。

| scenario ID | 共有親 cluster / law / gate / arm / checkpoint / episode の独立分散寄与 | checkpoint AR(1) |
|---|---|---|
| \`GTHETA-BASE-01\`（primary） | 0.20 / 0.15 / 0.10 / 0.10 / 0.15 / 0.30 | 0.60 |
| \`GTHETA-LOWCORR-01\`（感度） | 0.05 / 0.10 / 0.05 / 0.10 / 0.20 / 0.50 | 0.30 |
| \`GTHETA-HIGHCORR-01\`（感度） | 0.35 / 0.20 / 0.10 / 0.10 / 0.15 / 0.10 | 0.85 |

1. 各反復で親 cluster→law→gate→arm→checkpoint→episode の識別子にドメイン分離した標準正規 \`Z_C,Z_L,Z_G,Z_A,Z_T,Z_E\` を引く。\`Z_T\` は同一 law/gate/arm 内で checkpoint j=0..8 の定常 AR(1)。他の因子は表の共有スコープを保つ独立標準正規。\`U = sqrt(wC)Z_C+sqrt(wL)Z_L+sqrt(wG)Z_G+sqrt(wA)Z_A+sqrt(wT)Z_T+sqrt(wE)Z_E\`（全寄与の和=1）。各 gate・checkpoint の binary success は \`Y=1{Phi(U)<=p_arm,gate,j}\`。4 episode は同一 law 下の反復測定であり独立 law ではない。
2. FULL の checkpoint j における周辺成功確率は \`logit(p_FULL,g,j) = logit(Gg_star)-1.5*(8-j)/8\`。7対照は強さの全順序（固定）\`[H+, FIXED-IF, PRED-ONLY, REC, RANK-ONLY, LOOKUP, OFF]\` の d 列 \`[0,.005,.010,.015,.020,.025,.030]\` に対応し、\`p_a,g,8 = Gg_star-Contrast_star-d_a\` とする。各対照の時系列傾き \`kappa_a\` は非負実数 [0,8] から、9点台形 AULC の G1/G2 等重みで \`AULC_FULL − AULC_a = Delta_star\` を満たす**最小根**を、区間二分法（固定64回）で求める。無根・誤差>1e−10・確率が(0,1)外なら \`STOP_UNKNOWN\`。閾値変更の結果でシナリオを選び直さない。
3. \`law\` と \`parent_cluster\` は calculator が読める設計メタデータ上の識別子。分布は law ID による能力差を**学習・適合せず**、共有乱数効果だけで依存を生成。lawごとの \`AULC\`、B 時点の \`G1/G2\`、7対照差を同一 \`Y\` から作り、10番目の \`Contrast\` は **FULL − max(7対照の B 時点集約成功率)** として従属に作る（独立な擬似10本目の乱数は引かない）。各値を \`q_l\`／Sampford／HT／SYG／max-T へ渡す。checkpoints・gate・arm・cluster を独立標本扱いしない。
4. \`theta_star -> scenario_id\` は上述の **常に BASE を返す純関数**。\`LOWCORR/HIGHCORR\` は感度必須。統計 route では \`power_lower_bound\` に3ケースの**最小**の片側99%下限を採用（追加ゲートの保守的規則でありモデル選択ではない）。分布係数を CAL variance へ fit しない。CAL の分散・相関診断は記述情報のみとして別台帳へ保全し、モデル選択・パラメータ変更・統計 route の恣意的な切替えには使用しない。必要な診断自体が未完なら既存の不完備/UNKNOWN 規則に従う。
5. model digest: \`sha256:<lowercase-64hex>\`、対象 bytes は JSON ファイル全体を UTF-8/LF で正準化（key を再ソートせず保存 bytes 自体を SHA-256）。\`model_version\`、上記係数・因子スコープ・時系列式、d 列、ε関数バージョン、感度、二分法仕様、標準正規変換版、model file Git blob SHA を manifest に記録。**モデル条件付きの設計値**以外を名乗らない。

**source-first ロール read path**（既存 ACL の展開であり S1-B 新権限ではない）: Owner が source manifest/digest を承認 → 評価側の \`BLIND_DESIGN_CALCULATOR\` が署名済みの \`split_design_metadata\`（\`|H_laws|\`、q、親 cluster）と承認済み \`G_θ\` JSON／解析規則だけを許可済み path で読む → outcome を合成 → 統計設計を検査 → **閉じた receipt だけ**を Owner と監査者に返す。law ID↔q 対応、real holdout instance/target/score/seed、実成績を読む／出力する経路を追加しない。calculator の設計メタデータ READ は第6版 §7 S4 の **CAL_AUTHORIZED 後だけ**の例外である。入力モデルの欠損や再現不能は \`STOP_UNKNOWN\`。

## 5. simulation・PPS/HT・interval・費用の実行仕様（**実行は未許可**）

- 計画乱数は source-first の登録済み \`HMAC-SHA256\` counter PRF（master 256-bit seed は Owner が CAL_GO 後に別途 escrow、プロトコルでは**seed の値を作らない**）。\`domain = "WORLD-CAL-v1" || model_digest || scenario_id || n || repetition || stage || draw_index\`、index は大端64bit。疑似一様から逆正規 CDF を適用（丸め: IEEE754 binary64、tie は小さい正準 ID）。PPS、G_θ、bootstrap、tag はそれぞれ別ドメイン。正式 EVAL seed も sealed split 実体も参照しない。種の場所は role manifest 内、値は学習側・PR 文面に出さない。
- \`MC_R=10,000\` **固定反復** / candidate n / scenario（BASE/LOWCORR/HIGHCORR）。各反復は split の設計条件に従い固定 \`H_laws\` 上で PPS 無復元を引き、同じ law/cluster について8 arm×2 gate×9 checkpoint×4 episode の synthetic outcome を一度生成、9点台形 AULC と B ゲートを集約する。各反復内の max-T bootstrap は **999回**、law cluster 単位で再抽出、HT 係数を保持。異なる law として checkpoint・episode を再抽出しない。
- 同時区間の **主推論**: 7対照 AULC の studentized max-T を **両側 family-wise 98.75% CI** とし、保守的に主 α 0.0125 の範囲へ収める。G1/G2 は同じ weighted law bootstrap で片側下限（それぞれ α=0.00625）。Contrast 10pp は **点閾値のみ**（追加検定とせず α を支出しない）。K2 の FULL−REC 等価性は **別系統の両側95%同時区間**（7対照の同時 max-T ベクトル内の REC 成分）で \`CI subset [-0.05,+0.05]\` のときだけ等価の支持と呼ぶ。非有意は等価ではない。主 \`run_inference_outcome\` の「等価（小）」判定には §6 の主 Δ 同時 CI を使用し、K2 の記述的等価検査と混同しない。bootstrap の分散ゼロ、離散退化、近似精度不足は STOP_UNKNOWN、恣意的な代替法に切替えない。
- \`pi_l = min(1, lambda*q_l)\` は water filling で \`sum pi=n\`（certainty を分離）し、残余を **Sampford PPS 無復元**で抽出。二次包含 \`pi_ll'\` を同設計から計算し、和・非負・対称性・size consistency を数値検証（tol=1e−10）。\`hat_mu = sum_sample (q_l/pi_l)*Delta_l\`、certainty の係数は \`q_l\`。分散は total \`y_l=q_l*Delta_l\` に対する Sen–Yates–Grundy（SYG）; 未定義・pi_ll'=0 の不適格な設計・n=1 は STATISTICAL 不可。bootstrap は PPS の cluster 設計を保持し、iid bootstrap を使わない。
- 10 AND イベントを **7 AULC lower CI>0 かつ点差>=delta、G1/G2 B point>=gate かつ各片側下限>該当 gate（α=0.00625 ずつ）、Contrast B point>=c** と明記して記帳する。 \`P_joint\` は all 10 の成功頻度。Monte Carlo の **Clopper–Pearson 片側99%下限**（10,000回の二項計数のベータ分位点、再計算誤差≤1e−10）を各シナリオで計算し最小値を採用。\`power_lower_bound>=0.80\` が条件。別計算の \`P_i\` に対して \`1−sum_i(1−P_i)>=0.80\` を満たす保守的 union-bound 経路も許すが、\`P_i\` は同じ登録シナリオの**片側99%下側限界**を使用し、境界までの近似不足は STOP_UNKNOWN。積の下界は禁止。
- \`n\` の全探索域は \`2..min(N_eligible,512)\` の**整数昇順**。各 n で同一の検定・calculation・cap check を行い、最初に基準を満たす n を \`n_required\` とする。探索予算不足・不完全な \`pi_ll'\`・Monte Carlo の未完了は \`STOP_UNKNOWN\`（大きな n の試行だけで「最小」としない）。別 route の \`n_required\` は null とする。
- 事前の原始呼出 upper bound 候補（単位＝calls）: \`C(n)=250000 + 8*B_final + 2*20*T_horizon + 8*2*9*4*T_horizon*n\`。CAL reserve、全 arm TRAIN 上限、K1診断、全 arm の G1/G2 checkpoint 評価を保守的に課金。**上限が cost_cap 以下**でなければ当該 n は採択しない。実運用の各費用ベクトルも別台帳へ。CALLS 単位へ CPU、wall、spec デモを加算しない。
- route は第6版 §5 の順序を不変とする: \`STATISTICAL\`（合法な最小 n＋power＋cap）、不可時 \`FINITE_DESCRIPTIVE\`（\`N_eligible>=30\`、\`H_laws\` 完全列挙＋全件有効評価＋\`C(N_eligible)<=cost_cap\` が可能で \`mu_H=sum q_l Delta_l\` を集合限定で厳密記述）、それ以外 \`STOP_UNKNOWN\`。有限記述では推論/有意性/power を主張しない。**設計段階で有効評価を保証できない**場合は route を保留し、実評価で汚染が出た場合は §7 K4 の \`STOP_INVALID\` とする。主推論の \`H_laws\` を TRAIN/CAL で補わない。

**simulation が示すのは**「承認された \`G_θ\` の下で、承認されたサンプリング・推定・判定手続きを synthetic outcomes に適用したときの条件付き joint power」**のみ**。実 holdout の達成率・概念獲得・帰属の証明ではない。

## 6. K0・容量・CAL 実施仕様（E1、実行は別 Owner GO）

### 6.1 CAL が測るもの／測らないもの

**測る**: TRAIN 分布から隔離抽出した24 CAL law（各4族6件）の最短成功手数・分散／共分散の診断、原始呼出・候補評価・CPU/wall/RSS の費用ベクトル、強対照の飽和余地、ID-only tag AUC（固定分類器による順列 null の95パーセンタイル比較、複製ごと再 tag）、G2長13〜16についての**TRAIN law のみの工学的容量診断**、K0-a/b/c の抽象 support 診断、generator support の列挙可能性と parent-cluster 分離。CAL の分散結果は記述的診断だけに使用し、G_θ の再fit・シナリオ選択を行わず、分散値を calculator の新規 READ には追加しない。

**測らない**: 正式 G1/G2 holdout 成績、真の power、正式 law に対する実験、二階概念の効果認定、評価用 seed、sealed instance/target/score、学習結果の最適化。EVAL seed・split 実体には一度も触れず、\`F_laws\` の生成分布の **TRAIN 領域だけ**から採る。CAL で「未見 law 成績」を検証したと呼ばない。

**境界**: generator support の抽象 law については §6 の CAL oracle だけが source-first の schema/instance 分布/デモ分布/feedback/予算規則を読める。generator の実 holdout サンプルを実体化しない。BLIND_DESIGN_CALCULATOR は同節で閉じた評価側設計メタデータだけを CAL_AUTHORIZED の後に読む（S4 例外）、learner の権限は増やさない。新 ACL \`CAL_JOINT_SUMMARY\` は作らない。

### 6.2 T_horizon を固定してからの完全検査

- \`T_horizon=24\` は CAL 開始前、PROTOCOL_APPROVED で確定する。K0-a/b/c／同予算 H+／正式試行の episode termination は24 token と成功時吸収で一致。\`T_horizon\` に従って以前の H≥9 失格例を**再評価する**（E1）。例示 pair \`ABAB->ABABA\` と \`ADAD->ADADC\` について固定列 \`MOVE_RIGHT*4;SET_ANCHOR;INSERT(A);DELETE_BACK;SET_ANCHOR;INSERT(C)\` の成功時終了を2系統の静的遷移トレースとして照合する。9手以内の open-loop success が確認できるなら \`T_horizon=24\` で K0-a 陽性候補から除外し、**新しい陽性証人に数えない**。再確認の結果が正本と食い違えば fail-closed／逆質問。
- **K0-a pair の事前選択**: 各4族の CAL TRAIN 抽象 support の law を \`SHA-256(canonical law)\` 昇順に並べる。law 内では公開初期状態 digest 昇順の instance support の**異なる2点**、同一 law/tag/demo/goal contract、異なる公開観測（\`pi(H0)\` の一致は要求しない）を選び、pair の正準2初期状態 digest の辞書式最小組で候補とする。各族の先頭5 law で最大20 pair を**事前に確定**し、計算後に陽性だけへ差し替えない。law/instance の列挙が不足・未完了なら \`UNKNOWN\`。既知失格 pair は診断再現用の**別** negative control とし、この20の選択枠へ成功証人として混ぜない。
- **open-loop BFS**: pair の状態は \`(state_left or DONE_SUCCESS, state_right or DONE_SUCCESS, step_count)\`。初期2状態から全 live Alphabet の原子 token（INSERT は全4 Sym）を付表A の正準順に同時に発行。成功した側は吸収し、その後の token は実行も課金もしない。残る側のみ step 進行。各 token 後に success predicate を評価し、\`step_count<=24\` の間に両側が DONE_SUCCESS へ到達すれば \`OPEN_LOOP_WINS=true\`。同一公開観測による条件分岐を BFS に混入させない。各 node に前駆と digest を保存し、最大200万状態を超える／全合法遷移の列挙が完結しなければ UNKNOWN（不在証明しない）。
- **条件付き公開履歴木 DP**: \`pi(H_t)\`（tag を α-renaming で除去）を情報集合キーとし、同一公開履歴では同じ合法 action を選ぶ方策だけを許す。両 instance の選択された action で24内の成功を要求。TRAIN の複数 trial での成功/失敗 feedback と EVAL の feedback なしは混同しない。\`conditional_success=true\` **かつ** 完全 BFS で \`open_loop_wins=false\` のときだけ \`K0a_WITNESS=true\`。どちらか未完は UNKNOWN。node 上限200万。
- **K0-b**: 異 law の組について同じ公開情報射影の区別不能性を調べ、TRAIN 複数 trial／成功 feedback ありの列と EVAL 単独 episode／feedback なしの列を別々に完全 DP（上限200万）し、判定結果 \`PASS/FAIL/UNKNOWN\` と pair digest を残す。どちらかに識別不能で必要行動が異なる法則対があり完全列挙なら FAIL。未完なら UNKNOWN を優先。K0-c: 抽象 support の最良曲線を同 \`Space\`・\`B_final\`・24 steps・9 checkpoint／goal contract で厳密列挙し、\`oracle_AULC−best_control_AULC\` の**上限**が0.15未満なら飽和 STOP。列挙不能は UNKNOWN。oracle は機会上界のみで主成績に混ぜない。
- K0-a 証人なし（完結）は **二階スキーマ帰属のみ STOP**、二階必要 family は不採用。K0-b FAIL、K0-c 飽和は **主張B・実験 GO を STOP/REDESIGN**。UNKNOWN が1件でもあれば PASS/FAIL より優先して **STOP_UNKNOWN**。このルート規則を数値閾値やモデルの都合で変更しない。

## 7. source-first ACL、E2 全量 manifest、ログ、fail-closed

### 7.1 添付 E2 正規化アクセス表

添付 [E2 full matrix](WORLD-CAL-ACL-20261111-01-normalized-manifest.csv) は \`arm,node,constructor,phase,read_source,use_action,allow,reason\` の**全キーに対する実体行**を持つ。生成集合と優先順は下記で固定し、表外の任意の組は **default deny**（allow として類推・継承しない）。

- arm = \`FULL,OFF,PRED-ONLY,REC,RANK-ONLY,FIXED-IF,LOOKUP,H+\`。typed \`(node,constructor)\` 8件 = \`(ATOM,NONE),(SEQ,COMPOSE),(SEQ,ABSTRACT),(BIND,COMPOSE),(BIND,ABSTRACT),(COMPARE,PREDICATE_SLOT),(BRANCH,BRANCH_CONSTRUCT),(BRANCH,SEED_GIFT)\`。最後の \`SEED_GIFT\` は FIXED-IF の**唯一の贈与 AST の由来区別**であり、一般に実行できる新 constructor を付与しない。評価器 BRANCH-dispatch は全 arm 共通 seed の**評価機構**であって、初期 BRANCH インスタンスを許可することではない。
- phase = \`TRAIN,G1,G2,CAL\`。read_source = \`PUB,SELF_SNAPSHOT,SEED_GIFT,SPACE_ENUM,CAL_ORACLE,CAL_DESIGN_META,SEC\`。use_action = \`READ,REGISTER,USE\`。この有限積 **8×8×4×7×3=5,376 正規化行**、キー重複なし、\`allow\` boolean と閉じた \`reason\` code。すべての端点・理由を CSV に列挙。行が欠ける／重複する／未知値なら \`STOP_INVALID\`。
- \`PUB\` = token table／3 demo／公開履歴・trace・観測特徴（同一 digest）。\`SELF_SNAPSHOT\` = 自分の許可登録済み AST（OFF の TRAIN は FULL と同一）。\`SEED_GIFT\` = FIXED-IF の1件の既存語彙 AST。\`SPACE_ENUM\` = E 由来の候補（H+ と RANK-ONLY が既存 Space を直接探索、public trace 自体ではない）。\`CAL_ORACLE\`／\`CAL_DESIGN_META\`／\`SEC\` は**learner arm 全8種では常に deny**。CAL の evaluator 側の source-first 例外は下記の**別 role 表**だけに置く。
- \`REGISTER\` は TRAIN/PUB と許可 constructor／node のみに許可。FULL/OFF は compose／abstract／predicate-slot／branch-construct。PRED-ONLY は branch-construct 禁止。FIXED-IF は predicate-slot だけ。REC と RANK-ONLY の weights/prior、LOOKUP の episode memory は**AST の REGISTER ではない**（§3 の別台帳）。\`USE\` は G1/G2 のみに許可、OFF の獲得 AST は完全遮断。PRED-ONLY の COMPARE \`USE\` は**順位特徴のみ**で制御分岐への直結は禁止。FULL の未登録 AST 名呼び出しは deny。全 arm の ATOM primitive は PUB から USE 可。H+／RANK-ONLY の SPACE_ENUM USE は同一純構文 Space に限定。
- \`CAL\` phase の learner 行はすべて deny。CAL 実施者の **role** と arm を混同しない。ACL を実装しても良いという許可ではなく、事前審査する**設計 manifest**。

| role | 事前承認 source-first READ path | 禁止（例外なし） |
|---|---|---|
| \`LEARNER_ARMS\` | \`public/token_table,public/demo,public/history,public/trace,self/allowed_snapshot\`（権限は CSV） | \`SEC\` 一式、CAL oracle/design metadata、他 arm snapshot |
| \`EVALUATOR\` | \`private/manifest,private/verifier_truth,private/frozen_snapshot,private/analysis_rule\` | 学習への逆流を生む writer |
| \`CAL_ORACLE\` | \`abstract/generator_laws,abstract/generator_instance_distribution,abstract/demo_distribution,abstract/feedback_rule,abstract/budget_rule\`（source version/digest 必須） | \`sealed/split_instances, sealed/target, sealed/score, sealed/eval_seed\` |
| \`BLIND_DESIGN_CALCULATOR\` | \`design/split_metadata\` 内の \`N_eligible,q,parent_cluster\` と \`analysis/approved_theta_epsilon,analysis/alpha_beta,analysis/G_theta_model,analysis/sampling_and_tests\` **だけ**（§6 E3/S4 の限定例外） | 実 holdout instance/target/score/seed、law ID↔q の外部出力、CAL 実測共分散の新規 READ |
| \`AUDITOR\` | 事後に digest と全監査ログ（run が終わった後） | 学習/評価へ事後情報を feedback |

**アクセス表の生成規則と監査**: 行順は上の列挙ドメイン順に nested loop（arm→typed pair→phase→source→action）。初期 allow=false / reason=\`DENY_DEFAULT\`。先に \`CAL\` を \`DENY_CAL_PHASE\`、次に \`SEC\` を \`DENY_SEC\`、\`CAL_ORACLE/CAL_DESIGN_META\` を \`DENY_PRIVILEGED\` とする。残りに明示 allow 規則（PUB READ、TRAIN PUB の許可 REGISTER、G1/G2 PUB ATOM USE、許可 SNAPSHOT READ/USE、FIXED-IF 贈与 READ/USE、H+/RANK-ONLY SPACE_ENUM USE）の**み**を適用。矛盾する allow は作らず、理由の行ごとの byte-level 比較と SHA-256 を承認 receipt に含む。未知 tuple は default deny。

### 7.2 二階スキーマとログの契約

\`\`\`text
EpisodeRecord:
  episode_id, law_unique_id [EVALUATOR only; parent ID private], phase, goal_contract_version,
  task_tag, demo_set_digest, checkpoint_b, step_index, observation_before_digest,
  legal_action_set_digest, chosen_action, observation_after_digest,
  action_event: VALID | NO_OP_PRECONDITION | ACTION_FAULT,
  episode_outcome_kind: SUCCESS | FAIL | ABSTAIN | FAULT_ACTION,
  event_kind: ACTION_FAULT | FAMILY_INVALID | FAMILY_UNIDENTIFIABLE | null,
  full_cost_vector, symbol_event{kind,dependencies,proposal,rejection,promotion,USE,OFF,ast_digest},
  receipt_digest
FamilyRecord:
  family_status: SCORED | UNIDENTIFIABLE | FAMILY_INVALID
RunRecord:
  run_status: CONTINUE | STOP_INVALID | STOP_K0 | STOP_UNKNOWN | COMPLETE
  run_inference_outcome: NEGATIVE | SMALL_EQUIVALENT | POSITIVE |
                         BELOW_THRESHOLD_POSITIVE | INCONCLUSIVE | null
  H_laws_digest, T_horizon, route, all_digests, amendment_history
\`\`\`

\`episode_outcome_kind\` は episode 完了で保存し、run STOP でも台帳から消さない。\`run_inference_outcome\` は **COMPLETE かつ有効集約あり**のときだけ第6版 §6 の排他5分類順で計算、それ以外 null。失敗・abstain・打切・FAMILY_UNIDENTIFIABLE は分母に残す。ACTION_FAULT は no-op＋1 call 課金で episode を継続。K4 で FAMILY_INVALID が主抽出に1件でも出れば \`STOP_INVALID\`、**valid-only HT 再推定禁止**。digest 不一致、read 越境、seed 混線、情報漏洩、署名不一致も隔離と fail-closed、再実行は新事前登録版だけ。

### 7.3 source-first の必須 manifest・digest

\`\`\`text
generator_version, distribution_table_digest, random_source_spec{prf_version,seed_escrow_path},
tag_issuance_rule_version, split_manifest{parent_cluster_allocation_digest,H_laws_digest},
demo_set_digests, cost_vector_schema_version, snapshot_digests,
analysis_code_digest, role_read_paths, model_digest, acl_csv_digest,
hash_algorithm="SHA-256", failure_log_schema,
sampling_design{Sampford_version,pi_method,pi_ll_method},
T_horizon, B_initial, B_final, amendment_history
\`\`\`

源ファイルと同一 bytes に対する SHA-256 を source-first で計算し、各 raw object と manifest の参照先を再解決してから利用する。CAL の raw trace・input・receipt を保存し、生成した合成 outcome は実 holdout outcome と別 namespace に置く。ログと manifest の署名に失敗したら成功扱いにせず \`STOP_UNKNOWN\`、既存の正式推論標本や sealed truth に汚染があるなら \`STOP_INVALID\`。

## 8. BLIND_DESIGN_CALCULATOR receipt — 閉じた署名済み出力

**機械可読の出力キーは以下7件だけ**（追加キー・law単位出力・生 simulation outcome・「等」は不許可）。

\`\`\`json
{
  "N_eligible": null,
  "n_required": null,
  "route": "STOP_UNKNOWN",
  "power_lower_bound": null,
  "cost_cap_check": false,
  "algorithm_digest": "sha256:<64 lowercase hex after approval>",
  "split_digest": "sha256:<64 lowercase hex after CAL authorization>"
}
\`\`\`

上記 payload の署名は envelope header \`signer_role=BLIND_DESIGN_CALCULATOR; key_id; signature_algorithm=Ed25519; signature; payload_sha256\` として**外側**に置き、列挙済み出力欄に混ぜない。署名対象は RFC 8785 JCS で canonicalize した上の **7列だけ**、alg/split digest は独立の source-first artifact により固定。署名検証は Owner と監査側だけで行う（private raw metadata を learner へ転送しない）。\`route\` は \`STATISTICAL,FINITE_DESCRIPTIVE,STOP_UNKNOWN\` の3値。STOP のとき power/null・n/null など不明を null とし、成功見せかけのゼロ埋めをしない。\`algorithm_digest\` は解析規則・model・ε・alpha/beta・ACL/route 設計文書の登録 digest 集合への参照。signature または入力不一致は fail-closed。

## 9. PROTOCOL_APPROVED 提出・承認記録テンプレート（本稿では未記入）

Issue #195 に **Owner 本人が** post-review に以下を記載する。空欄のまま Draft PR を作っても承認ではない。

\`\`\`text
state: PROTOCOL_APPROVED | REJECTED
actor_role: Owner
decision_timestamp_utc:
source_spec_id: WORLD-PREREG-SPEC-20261110-06
source_spec_head: 351016fe0e2d468c80736a477133a274cfb713b8
source_spec_blob: 9362065507791ced44e2a3cc218c93a0b3cef395
reviewed_protocol_id: WORLD-CAL-PROTOCOL-20261111-01
reviewed_protocol_commit:
reviewed_protocol_blob:
reviewed_acl_csv_sha256:
reviewed_model_json_sha256:
reviewed_digest_algorithm: SHA-256
reviewer_verdict_and_link:
locked_decision_rules: [K0,route,PPS/HT/SYG,maxT,K2,K4,run_outcome,epsilon,G_theta]
locked_numeric_fields: [delta_AULC,m,g1,g2,c,alpha_primary,alpha_equivalence,beta_i,n_min_descriptive,cost_cap,B_initial,B_max_after_cal,T_horizon,n_train,n_cal,n_k1,eval_replicates,n_search_max]
sole_post_cal_amendment: "B_final=f(L90), once, 4096/6144"
locked_role_read_paths_and_acl_digest:
locked_random_source_and_seed_escrow_policy:
locked_mc_rules: [MC_R=10000,CP_one_sided_99,maxT_bootstrap=999,ascending_n]
locked_receipt_schema_and_signature:
locked_generator_schema_and_abstract_support_dependency:
cal_authorized: false
frozen: false
execution_go: false
\`\`\`

この記録は PROTOCOL_APPROVED の**入力・許容更新範囲の lock**のみで、CAL 実施 GO とは別。第6版 §7 の **DESIGN_DRAFT→PROTOCOL_APPROVED→CAL_AUTHORIZED→CAL_COMPLETE→FROZEN→EXECUTION_GO** をそのまま採用する。CAL_AUTHORIZED／FROZEN／EXECUTION_GO は個別の Owner 明示判断（実装 GO と評価 GO も個別）。既存 PR #194/#196/#197/#198/#199 は Draft のまま。

## 10. 監督者へ提出する未解決依存・逆質問（正本の変更要求ではない）

- **RQ-CAL-01（生成器版）**: 第6版 §5 の有限グリッド／構造的除外／正確な \`N_unique\` は、将来の generator source manifest に全量列挙・digest が必要。未定のまま \`N_eligible\`、PPS、K0 の全称探索を PASS としない。どの設計版で source-first に固定するか監督者確認が必要（本書が generator を密かに追加定義しない）。
- **RQ-CAL-02（全量探索の実現性）**: \`T_horizon=24\` と state/tree cap 200万は確定候補であり、K0-a/b/c 全称の完全探索可能性は未検証。cap に達したら UNKNOWN とするため、要求する証人・識別可能性を証明できない可能性がある。CAL_GO 前に範囲を変更したい場合はプロトコルを改版・再承認する。
- **RQ-CAL-03（K2 と power の判定定義）**: K2 は主片側 α とは別の 95% 両側同時区間とした。Contrast は点ゲートで追加検定にしない。この区別が監督者の帰属審査と一致するかを確認し、不整合なら Draft 段階で修正する。
- **RQ-CAL-04（source-first 実装前監査）**: \`G_θ\` の完全再現には固定モデルの確率変換/二分法、Sampford π_ll、加重 bootstrap の厳密な実装/検証が必要。いずれの実装も本稿の承認に含まれず、digest 未確定なら CAL を実施しない。

**提出範囲**: 本プロトコル本文、\`G_θ\` 候補 JSON、E2 全量 ACL CSV、\`docs/INDEX.md\` の入口だけ。コード変更・自動検定・simulation・CAL・実データ採点・実験の実施なし。
