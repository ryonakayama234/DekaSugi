# 仕様パック第3版: WORLD 最小実験の機械可読仕様

id: WORLD-PREREG-SPEC-20261110-03
status: specification_pack_v3 / not_frozen / not_implementation / no_calibration / no_experiment
updated: 2026-11-10
tags: successor-axis, world-expansion, specification, preregistration-draft, supervisor

> 本書は仕様パック改訂版（WORLD-PREREG-SPEC-20261110-02）に代わる第3版であり、Research Lead 再判定 R4／逆質問 RQ4（PR #199）と監督者回答（PR #199 コメント 6769451282）、Owner 採用（2026-11-10）に基づく。-01・-02 は履歴として保持し、現行の正は本書とする。数値はすべて確定候補であり凍結値ではない。

## 0. ドラフト v2 本文への修正条項と対応表

### 0.1 本書が置換する v2 の条項

- v2 §1 の初期長規定 → 本書 §4 の長さ表。v2 §1 の「行動契約を凍結前に全列挙する」は TODO であり、本書の付表Aがその列挙自体として置換する。
- v2 §2 のデモ課金・tag 規定・分母規定 → 本書 §1・§4。
- v2 §3 の PRED-ONLY の範囲 → 本書 §3（意図的な縮小: 述語は順位付けの特徴としてのみ使用可とし、FULL との差を制御流分岐の構築に純化する）。
- v2 §4 の評価器 node「4種のみ」 → 本書 §2 の統一文法。
- v2 §5 の AULC 定義 → 本書 §4。v2 §5 の閾値改訂条項 → 本書 §7 の3区分（数値候補の区分で存続）。
- v2 §6 の iid/標本単位規定 → 本書 §5（PPS 無復元）。
- v2 §7 の K0 停止規定・校正後文書改訂条項 → 本書 §6・§7（改訂は §7 の3区分の手続きによる）。
- v2 §10 の手続き → 本書 §7。

### 0.2 対応表（指摘 → 改訂先）

| 指摘 | 改訂先 |
|---|---|
| B1（識別の層、証人の具体性、ID-only 統計量） | §1（2層の識別、証人表、AUC 統計量） |
| B2（Space と登録集合、権限の訂正、文法の完全性） | §2（純構文 Space、正準形と全順序、特徴語彙）、§3（FIXED-IF 訂正、REC の形） |
| B3（条件付き分離可能性の判定手続き、oracle の条件） | §6（履歴木 DP、UNKNOWN 規則、oracle の定義） |
| B4（PPS 算法・推定量、同時検出力） | §5（Sampford＋HT、union bound と simulation） |
| B5（outcome の網羅性、INVALID の分離） | §4・§6（決定順序と残余カテゴリ、event kind 3種） |
| B6（改訂時点の3区分、CAL の読み取り範囲） | §7（3区分表）、§6（アクセス表の CAL oracle 行） |
| N1〜N11 | §2／§3／§5／§6／§4／§0.1・§7／付表A／§0.1・§3／§4／§4・§6／§6 |
| RQ4 Q1〜Q7 | §1／§2・§3／§5／§5／§4・§6／§7／付表A・§6 |

## 1. 課題提示・デモ・tag・識別の2層（B1）

- デモ対は family あたり3対（確定候補）、試行開始前の一括提示のみ、追加取得・再提示は不可。全 arm で同一（digest を記録）。デモは生成器が当該 law のデモ分布から生成し、trial instance とは重ならない。予算 b に課金せず、費用ベクトルに「仕様コスト」として別掲する。評価フェーズでも同じ3対を与え、評価デモの学習への持ち帰りは禁止。
- task tag: 法則の生成 seed と独立な登録済み乱数源から引く不透明 ID。フェーズ内では同一 law に同一 tag を再使用し、異なる law が tag を共有しない。tag の役割はフェーズ内での同一課題の同定（episode の台帳）であり、意味内容を符号化しない。フェーズごとに再抽選する。
- 公開履歴 H_t = (task_tag, demo_set_digest, 初期観測, (行動, 観測, フィードバック) 列)。同値判定は内容射影 π(H)（tag をプレースホルダに置換する α-renaming 同値）に対して行う。
- **識別の2層**:
  - 層1（episode 内の分岐）: 分岐の根拠は instance の公開特徴（初期 buffer とその遷移）である。分岐に使う情報は行動選択前に π(H_t) へ到達していなければならない。
  - 層2（law の同定）: law 自体の同定は TRAIN の複数 trial に跨る成功/失敗フィードバックでのみ起きる。EVAL では snapshot が同定結果を保持し、episode 内で新たな law 情報は入らない。EVAL の識別可能性の主張は層1に限る。
- **証人表（層1）**: law L = 「マーカー規則」（buffer に D が含まれれば末尾に C を、含まれなければ末尾に A を追加したものが目標）。デモ3対は D を含まない instance の対で、両 instance と共通（digest を記録）。instance 1: 初期 buffer「AB」→ 目標「ABA」。instance 2: 初期 buffer「AD」→ 目標「ADC」（target は監査側のみが保持）。共通の open-loop 列は両 instance に同一の編集しか生まず双方を成功させられない。初期観測の特徴（D の有無）に条件付けた方策は双方に成功する。分岐時刻は最初の行動選択前である。
- 境界: TRAIN で到達・試行されなかった instance 類型でのみ異なる law ペアは同定できない。この境界は K0-b が生成器 support に対する列挙で検査する。
- ID-only 検査: 統計量は「tag 文字列の特徴から law の族を予測する固定分類器の AUC」とし、順列帰無分布の95パーセンタイルを閾値の確定候補とする。CAL の複製ごとに tag 割付を引き直す。
- フィードバック: TRAIN では試行ごとに成功/失敗を返し費用に計上。評価では完了後の監査専用とし学習へ戻さない。

## 2. 候補空間 Space と統一文法（B2）

- **候補空間 Space** は純構文で定義する: 下表の型付き AST の正準形のうち、サイズ上限（深さ ≤8、node 数 ≤64、述語深さ ≤3、以上確定候補）内の全体。正準形は束縛変数を de Bruijn 指数化した形とし、列挙器 E の順序は (node 数, 正準逐次文字列の辞書式) の全順序、重複は正準形の同一性で除く。
- 「経験由来」は構文の制限ではなく**学習 arm の登録制限**である: FULL 等の学習 arm は、観測した素材への constructor 適用で得た AST のみを snapshot に登録できる。H+ は Space を直接探索し、登録の概念を持たない。候補空間の同一性とは Space の定義の同一性を指し、FULL の登録集合 R_FULL(h) ⊆ Space は履歴とともに育つ。効率の主張は「同じ Space に対し、予算あたりに実効的に到達できる範囲の差」として述べる。

| 評価器の型 | 意味 | 初期在庫 |
|---|---|---|
| ATOM(a) | 原子行動 a（付表Aの11種、INSERT は記号を引数に取る） | 行動そのもののみ |
| SEQ(x1..xn) | 連接 | 機構のみ |
| BIND(v, e, body) | 型付き変数束縛（lexical scope、型 {Sym, Pos, Bool, AST}） | 機構のみ |
| COMPARE(op, l, r) | op ∈ {EQ, LT, LE}。表記 CMP は COMPARE の alias | 機構のみ |
| BRANCH-dispatch | 述語を評価し分岐先を選ぶ評価機構（seed の一部） | 機構のみ。BRANCH インスタンスは初期在庫に存在しない |

- 学習側 constructor: compose／abstract（anti-unification）／predicate-slot／branch-construct（BRANCH インスタンスの生成）。
- COMPARE の被演算子に使える観測特徴の語彙（確定候補）: buffer 長、カーソル位置、選択長、クリップボードの記号または none、カーソル位置の記号、記号別カウント、直近の行動結果。定数は記号リテラル A〜D と相対位置 -16〜16（絶対位置は禁止）。
- 評価順序は call-by-value・左から右。評価失敗（型不一致・範囲外参照）は ACTION_FAULT（§4）として処理する。

## 3. arm の権限・費用 matrix（B2/B5）

| arm | 構築（登録） | USE | 確定候補の詳細 |
|---|---|---|---|
| FULL | 全 constructor | 登録した全記号 | 主張の本体 |
| OFF | FULL と同一訓練（同一 snapshot、digest で確認） | 評価時に USE のみマスク。再学習・別前処理は禁止 | 同一性は §6 の receipt による |
| PRED-ONLY | branch-construct を除く全て | COMPARE 述語は順位付けの特徴としてのみ使用可（制御流への使用は禁止）。BRANCH を含む AST は構築時・読込時に型検査で拒否 | v2 §3 からの意図的縮小（§0.1） |
| REC | feature map の学習のみ | feature map = (buffer 長、記号別カウント、カーソル位置、直近 k=8 件の成否) の固定統計ベクトル。方策は特徴ベクトルへの線形スコアの合法行動に対する argmax に固定（重みのみ学習） | 述語型 AST の生成は型で不可能 |
| RANK-ONLY | なし | E の列挙順序への prior 学習のみ。候補集合は Space と同一 | 探索順序以外の変更は禁止 |
| FIXED-IF | **predicate-slot のみ許可**（FULL と同じ述語発見）。branch-construct は禁止 | 贈与 BRANCH スキーマ1件（述語スロットに汎用 COMPARE テンプレート「観測特徴が直近の観測特徴と等しいか」型を充填済み、確定時に形式を固定）の USE ＋ 発見した述語の特徴使用 | 贈与分は費用に開示。「同一 seed」とは記さない |
| LOOKUP | なし | 距離 = (初期 buffer, 行動列) 対の正規化編集距離。容量 = TRAIN episode 全件（上限512件、超過時は抽出を停止して報告）。最近傍距離 > 閾値 0.2（確定候補）で abstain | 距離・容量・閾値は凍結時に固定 |
| H+ | なし（登録の概念なし） | Space 全体への同予算の直接探索 | 無制限 oracle は機会診断専用で主成績に含めない |

- 全 arm 共通: 主比較は同一の事前割付公開 trace のリプレイ。能動収集は副比較として分離する。停止条件・holdout・公開情報は同一。
- 費用ベクトル（単位ごとに独立照合、加重和に混ぜない）: 予算 b（原始呼出累積、no-op を含む）、episode 数、候補評価数、有料問い合わせ、成功フィードバック数、学習準備費、USE 費、CPU、wall、RSS、保存量、仕様コスト（デモ）。

## 4. 測定・長さ・分母・event kind（B4/B5）

- checkpoint: b ∈ {0, B/8, …, B} の9点。s_f(b) は凍結 snapshot の評価成功率（棄権・打切り・各 event の分母上の扱いは下記）。checkpoint 評価費は測定費として別掲。
- AULC_f = （s_f の台形積分） / B。主エンドポイントは family ペア差 Δ の §5 の加重平均。
- 長さ表:

| フェーズ | 初期 buffer 長 | 中間 buffer 上限 |
|---|---|---|
| TRAIN | 4〜12 | 16 |
| G1（未見 law） | 4〜12 | 16 |
| G2（未見長さ、OOD 拡張） | 13〜16 | 16 |
| CAL | TRAIN と同一範囲（例外: 採点対象外の工学診断として長13〜16の容量診断を実施可） | 16 |

- 分母: 母集団 frame = 登録生成器の support から、生成器仕様に事前に列挙された構造的除外（容量で到達不能な類型）を引いた集合。除外類型と件数は生成器仕様の版に固定し、結果を見てから追加しない。生成後に発見された不能・識別不能 family は主分母に残し、「生成前の除外」と「生成後の不能」は別欄で報告する。
- event kind の分離: **ACTION_FAULT**（型失敗・範囲外参照による no-op＋課金。episode は継続し当該試行は分母に残る）／**FAMILY_INVALID**（K4 の汚染による隔離。再採点禁止）／**FAMILY_UNIDENTIFIABLE**（EVAL で発見された識別不能。失敗として採点し分母に残す）。棄権（abstain）と打切り（ホライズン到達）は失敗として分母に残す。

## 5. 法則母集団・PPS 抽出・推定・検出力・route（B4）

- law の正規形: (テンプレート ID, 述語 AST 正規形, 分岐操作, 対象役割, 正規化パラメータ)。unique ID = 正規形のハッシュ。N_unique = 登録生成器 support の総数（有限・列挙可能、仕様凍結時に厳密に数える）。
- 生成分布（確定候補）: 4族（転写／反復コピー／観測依存編集／2段連結）へ均等配分（各 0.25）。族内のテンプレート・パラメータ・長さ・語彙は有限グリッド上の一様抽出とし、グリッドは生成器仕様の付表に列挙する。推定対象はこの登録分布に限る。
- **抽出: unique law の PPS 無復元抽出（Sampford 法）**。包含確率 π_l = min(1, λ p_l)（λ は Σπ_l = n を満たす water-filling で定める）。π_l = 1 の law は certainty unit として常時含める。2次包含確率 π_ll' は Sampford 法により計算可能とする。抽出は split ごとに行う: support を親 law cluster で TRAIN/CAL/holdout に分割し、holdout 層内で p を再正規化して抽出する。N_eligible = holdout 層の support 総数。TRAIN/CAL/holdout は親法則の連結成分で隔離する。
- 推定量: **正規化しない Horvitz–Thompson 型**。推定対象は登録分布の平均 Δ̄ = Σ_l p_l Δ_l、推定量は Σ_{l∈標本} (p_l / π_l) Δ_l（certainty unit は重み1）。分散は Sen–Yates–Grundy 推定量を主とし、同時区間は law cluster を単位とし HT 重みを保持する加重 bootstrap で構成する（近似であることを分析計画に明記）。support 全件列挙の場合は有限母集団補正を適用する。
- 誤差配分（片側 α = 0.025 の内訳）: 主 family（FULL 対 7対照の ΔAULC、max-T 同時区間）に 0.0125、G1 ゲートに 0.00625、G2 ゲートに 0.00625 を Bonferroni 配分する。max-T の再抽出単位は unique law cluster。
- **同時検出力**: 成功の主張は9成分の AND（7対照の ΔAULC 比較＋G1 ゲート＋G2 ゲート）である。同時検出力の下界は union bound（1 − Σ(1 − P_i)）を用い、積の下界は使わない。失敗予算 0.20 の配分（確定候補）: 7対照に各 0.02（計 0.14）、G1 に 0.03、G2 に 0.03。各成分の n_i は検出力 1 − β_i を満たすよう計算し、n_required = max(n_i) とする。主たる検出力評価は設計ベース simulation とする: CAL 段階で登録した代替シナリオ（最弱対照で ΔAULC = 0.15、ゲートは閾値ちょうどの代替）の下で抽出・推定・判定の全手続きを反復し、全ゲート同時成功の頻度を同時検出力の推定値とする（反復回数と乱数源は CAL プロトコルに固定）。STATISTICAL 路線は、union bound の保証か simulation 推定（下側信頼限界つき）のいずれかで 0.80 以上が示された場合にのみ許可する。
- 判定ゲート: 第一に AULC（点推定 ≥ +0.15 かつ同時区間下限 > 0）、追加 AND ゲートとして B 時点の達成率（G1 ≥ 90%、G2 ≥ 80%、最強対照差 ≥ +10pp、いずれも確定候補で §7 の数値候補の区分により改訂可）。
- cost_cap: 全 arm 合計の原始呼出総量の上限として単一の数値で固定する（確定候補の値は CAL プロトコルで提示し、金額・時間換算を併記する）。
- route 決定（機械的）: n_required ≤ N_eligible かつ同時検出力 ≥ 0.80 かつコスト内 → STATISTICAL（n = n_required）。有限 frame が全列挙可能で |frame| ≥ n_min_descriptive（確定候補 30）→ FINITE_DESCRIPTIVE（全件評価、分布外一般化・検出力の主張なし）。それ以外 → STOP_UNKNOWN（対照を弱めない）。

## 6. K0・キル条件・ログ・manifest（B3/B5/B6）

### K0 の主張ごと遷移表（校正系列のみで実施。oracle は上界専用）

| 診断結果 | 主張B（経験効率） | 二階スキーマ帰属 | family 採用 | 本実験 GO | 再設計 |
|---|---|---|---|---|---|
| K0-a 証人あり | 継続 | 継続 | 継続 | 他条件に委ねる | 不要 |
| K0-a 証人なし（列挙完結） | 継続可 | **停止**（認定対象から除外） | 二階を要する family は不採用 | 二階なしの範囲でのみ可 | 課題生成への証人ペア型の追加を次版で必須化 |
| K0-b 識別不能（列挙完結） | **停止** | 停止 | 不採用 | **不可** | 必須（STOP/REDESIGN） |
| K0-c 余地なし（(oracle AULC − 最強対照 AULC) の上限 < δ_AULC = 0.15） | **停止**（飽和） | 停止 | — | **不可** | 予算・課題側の再設計 |
| いずれか UNKNOWN（列挙未完結） | 判定保留 | 判定保留 | 保留 | **不可** | 列挙範囲の拡大が先 |

- K0-a の列挙: 共通 open-loop 列の探索上限は H ≤ 64 手。状態ペアの BFS で列挙する。
- K0-b の条件付き分離可能性: 決定的環境の到達可能履歴木（H 上限内）に対する動的計画法で、2つの instance／law の成功条件を同時に満たす決定木の有無を判定する。木の node 数が事前固定の上限（確定候補）を超えたら UNKNOWN とする。UNKNOWN は PASS/STOP に優先する。
- K0-c の oracle: 生成器の抽象 support の各 law について、同一の候補空間 Space・同一予算 B・同一 checkpoint・同一の goal contract の下で到達可能な最良の成功曲線から AULC を厳密に計算する。support が列挙不能な場合は UNKNOWN。oracle が読むのは law 定義のみであり、sealed な holdout instance・target・score は読まない。

### キル条件と outcome の決定順序

| 条件 | 判定式（数値は確定候補） |
|---|---|
| K1 実使用 | 診断 family（事前固定20件）× checkpoint で、ON/OFF の最初の行動または trace digest が異なる組が1件以上。確率的方策では診断状態の行動分布の total variation > 0.1 の状態が1件以上 |
| K2 等価性 | FULL−REC の AULC 差の両側同時区間が ±0.05 内なら「性能の等価性（マージン内）」のみを支持する。機構帰属は §3 の比較階層の模様全体が事前登録した読み方と一致する場合に限り、「帰属の候補として整合する」と限定して述べる |
| K4 汚染 | FAMILY_INVALID として当該 family のみ隔離し再採点しない。再実行は新しい事前登録版でのみ可能 |

- outcome ラベルの決定順序（排他・網羅。同時 CI は ΔAULC のもの、m = 0.05、δ = 0.15）: (1) FAMILY_INVALID → (2) 負: CI 上限 < 0 → (3) 等価（小さい）: CI 全体が [−m, +m] 内 → (4) 正（認定）: CI 下限 > 0 かつ点推定 ≥ δ かつ全ゲート通過 → (5) 閾値未達の正方向: CI 下限 > 0 だが (4) を満たさない → (6) INCONCLUSIVE: 上記のいずれでもないもの（残余カテゴリとして定義し網羅性を保証する）。
- family 集約: 主エンドポイント・B 時点成績とも §5 の加重で集約し、区間は max-T と同じ再抽出で構成する。

### ログ schema（最小列）

episode_id / law_unique_id（評価側のみ親 ID を併記）/ phase / goal_contract_version / task_tag / demo_set_digest / checkpoint_b / step_index / observation_before_digest / legal_action_set_digest / chosen_action / observation_after_digest / outcome_kind（SUCCESS/FAIL/ABSTAIN/FAULT_ACTION）/ event_kind（ACTION_FAULT/FAMILY_INVALID/FAMILY_UNIDENTIFIABLE の該当時）/ 費用ベクトル全項目 / symbol_event（型、依存先、proposal/rejection/promotion/USE/OFF、AST digest）/ receipt_digest。

### アクセス表と manifest

| 主体 | 読めるもの | 読めないもの |
|---|---|---|
| 学習側 | 公開履歴 H_t、公開 trace、自己の snapshot | 評価 manifest、hidden target/rule、holdout score、生成 seed |
| 評価側 | 全 manifest、verifier の真値、凍結 snapshot | （学習への逆流経路を持たない） |
| CAL oracle | 生成器の抽象 support（law 定義）のみ | sealed な split 実体（instance・target・score） |
| 監査者 | digest 一覧、ログ全件（事後） | — |

- manifest 必須フィールド: generator_version / distribution_table_digest / random_source_spec（方式と seed の保管場所）/ tag_issuance_rule の版 / split_manifest（親 law cluster 単位の割付 digest）/ demo_set_digests / cost_vector_schema の版 / snapshot_digests / analysis_code_digest / role_read_paths / hash_algorithm（SHA-256）/ failure_log_schema。
- fail-closed: manifest と実体の digest が1件でも一致しなければ、当該 family は FAMILY_INVALID、run 全体は STOP とし、監査ログに記録する。receipt は source-first の manifest に集約し、第三者は digest 再計算と trace 再生で検証する。

## 7. 改訂可能性の3区分と段階決定表（B6）

| 区分 | 内容 | 変更可能時点 |
|---|---|---|
| 決定規則 | 比較階層・同値関係・route の分岐構造・outcome の決定順序 | CAL プロトコル承認まで。以後は版を上げる場合のみ |
| 数値候補 | δ・マージン・閾値・上限類 | CAL 中に1回だけ、CAL の難易度データのみに基づき、判断ログを残して改訂可 |
| アルゴリズム出力 | n_required・route・包含確率など、承認済み算法が CAL 実測から算出する値 | 改訂ではなく出力。算法自体は決定規則に属する |

| 段階 | 承認者 | Issue #195 への記録 | 参照する digest | この段で変更可能なもの |
|---|---|---|---|---|
| CAL プロトコル承認 | Owner | 承認コメント（対象文書の版を明記） | 本書＋ドラフトの head SHA | 数値候補の確定（この段まで） |
| CAL 実施 GO | Owner | GO コメント | CAL プロトコルの digest | §7 の数値候補の区分による1回改訂のみ |
| 事前登録凍結 | Owner | receipt コメント＋repo の receipt 文書 | 全 manifest digest | なし（凍結後は版を上げる） |
| 実装 GO／正式評価 GO | Owner | GO コメント（個別） | 凍結 receipt の digest | なし |

- 決定記録の正本は Issue #195 のコメントとし、PR #194/#196/#197/#198/#199 は引き続き Draft とする。

## 付表A. 行動契約（世界のインターフェースと11原子操作）

### インターフェース

| 関数 | 意味論 |
|---|---|
| reset(instance) | instance の初期状態（buffer、cursor=0、selection=none、clipboard=空）を設定し、初期観測を返す。 |
| observe() | 現在の (buffer, cursor, selection, clipboard, 直近の行動結果) を完全観測として返す。 |
| legal_actions() | 現在状態で発行可能な行動の集合を返す（全行動が常に発行可能で、事前条件を満たさない場合は no-op として処理する。下記の各操作の「無効時」を参照）。 |
| step(action) | 行動を1回適用し、原始呼出として課金する。新しい観測と、試行の終了したかどうか（成功述語の成立／ホライズン到達）を返す。 |

- 状態: buffer（上限16記号）、cursor（0〜buffer 長）、selection（anchor/head の半開区間または none）、clipboard（記号列または空）。undo はない。環境は決定的で law 非依存。
- no-op と ACTION_FAULT の境界: 事前条件を満たさない正規の行動は no-op（状態不変・課金あり・失敗として数えない）。型失敗・範囲外参照など AST 評価の失敗は ACTION_FAULT（no-op＋課金、episode は継続）。
- 終了条件: verifier の成功述語が成立した時点、またはホライズン上限 H（試行ごとの原始呼出上限、確定候補）に到達した時点で試行を終了する。中止は manifest 不一致等の fail-closed の場合にのみ発生し、run 全体の STOP として記録する。

### 11原子操作

| 操作 | 事前条件 | 効果 | 無効時 |
|---|---|---|---|
| MOVE_LEFT | なし | cursor を1左へ（0で下限） | cursor=0 では no-op |
| MOVE_RIGHT | なし | cursor を1右へ（buffer 長で上限） | 末尾では no-op |
| INSERT(s)（s ∈ {A,B,C,D}） | buffer 長 < 16 | cursor 位置に s を挿入し cursor を1進める。selection がある場合は選択範囲を置換してから挿入 | buffer 長=16 では no-op |
| DELETE_BACK | cursor > 0 | cursor の左1記号を削除し cursor を1戻す | cursor=0 では no-op |
| DELETE_RIGHT | cursor < buffer 長 | cursor 位置の1記号を削除 | 末尾では no-op |
| SET_ANCHOR | なし | selection の anchor を cursor に設定し、head=cursor の空選択を開始 | 常に有効 |
| EXTEND_LEFT | selection あり | head を1左へ（0で下限） | selection なし／下限では no-op |
| EXTEND_RIGHT | selection あり | head を1右へ（buffer 長で上限） | selection なし／上限では no-op |
| COPY | selection が非空 | 選択範囲の記号列を clipboard に上書き | 選択なし／空選択では no-op |
| PASTE | clipboard が非空、かつ貼付後の buffer 長 ≤ 16 | cursor 位置に clipboard の内容を挿入（selection がある場合は置換） | clipboard 空／容量超過では no-op |
| CLEAR_SELECTION | なし | selection を none に戻す | 常に有効（selection なしでも no-op として課金） |

- selection の範囲は anchor と head の半開区間 [min, max) とし、編集操作（INSERT/DELETE/PASTE）の後は selection を none に戻し、cursor は編集結果の末尾に置く。
