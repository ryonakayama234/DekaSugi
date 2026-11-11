# 仕様パック改訂版: WORLD 最小実験の機械可読仕様

id: WORLD-PREREG-SPEC-20261110-02
status: specification_pack_revised / not_frozen / not_implementation / no_calibration / no_experiment
updated: 2026-11-10
tags: successor-axis, world-expansion, specification, preregistration-draft, supervisor

> 本書は仕様パック初版（WORLD-PREREG-SPEC-20261110-01）に代わる改訂版であり、Research Lead 審査 R3／逆質問 RQ3（PR #198）と監督者回答（PR #198 コメント 6768694529）、Owner 採用（2026-11-10）に基づく。初版は履歴として保持し、現行の正は本書とする。数値はすべて確定候補であり凍結値ではない。

## 0. ドラフト v2 本文への修正条項と対応表

### 0.1 本書が置換する v2 の条項

- v2 §1 の初期長規定 → 本書 §4 の長さ表。
- v2 §2 のデモ課金・tag 規定・分母規定 → 本書 §1・§4。
- v2 §4 の評価器 node「4種のみ」 → 本書 §2 の統一文法表。
- v2 §5 の AULC 定義 → 本書 §4。
- v2 §6 の iid/標本単位規定 → 本書 §5（PPS 無復元）。
- v2 §7 の K0 停止規定 → 本書 §6 の主張ごと遷移表。
- v2 §10 の手続き → 本書 §7 の段階決定表。

### 0.2 対応表（指摘 → 改訂先）

| 指摘 | 改訂先 |
|---|---|
| B1（tag/H_0 矛盾、デモ・合法性の列挙） | §1（π 同値・漏洩検査・証人構成例） |
| B2（grammar・閉包・各 arm の未確定部） | §2（統一文法・列挙器 E）、§3（贈与・距離・feature の確定候補） |
| B3（K0 の停止範囲・δ・列挙） | §6（遷移表、δ_AULC 明記、BFS 列挙と UNKNOWN 優先） |
| B4（iid/unique、検出力、分布・cost） | §4（分母）、§5（PPS/HT、α 配分、同時検出力） |
| B5（K2 の帰属・K3 の重なり） | §6（結論の格下げ、outcome 決定順序） |
| B6（manifest・段階の記録） | §6（manifest 必須フィールド、fail-closed）、§7（段階決定表） |
| C1（BRANCH の位置づけ） | §2（dispatch は機構、インスタンスは初期在庫なし、CMP=COMPARE alias） |
| C2（G2 の長さ） | §4 長さ表（G2 は OOD 拡張として明示） |
| C3（K0-a の停止範囲の衝突） | §6 遷移表に一本化 |
| C4（n の数え方） | §5（unique law の PPS 抽出を主設計に統一） |
| C5（tag の識別子性） | §1（台帳機能として明記、漏洩検査は内容予測に限定） |
| C6（分母の読み分け） | §4（生成前の構造的除外と生成後の不能を別欄で報告） |
| RQ3 Q1〜Q8 | §1／§6／§2・§3／§4／§5／§5・§6／§6／§6・§7 |

## 1. 課題提示・デモ・tag・公開履歴（B1）

- デモ対は family あたり3対（確定候補）、試行開始前の一括提示のみ、追加取得・再提示は不可。全 arm で同一（digest を記録）。予算 b に課金せず、費用ベクトルに「仕様コスト」として別掲する。評価フェーズでも同じ3対を与え、評価デモの学習への持ち帰りは禁止。
- task tag: 法則の生成 seed と独立な登録済み乱数源から引く不透明 ID。フェーズ内では同一 law に同一 tag を再使用し、異なる law が tag を共有しない。tag の役割は**フェーズ内での同一課題の同定（episode の台帳）**であり、意味内容を符号化しない。フェーズごとに再抽選する。
- 公開履歴 H_t = (task_tag, demo_set_digest, 初期観測, (行動, 観測, フィードバック) 列)。
- **同値判定は内容射影 π(H) に対して行う**。π は task_tag をプレースホルダに置換したもの（α-renaming 同値）。K0-a／K0-b の「H_0 の一致」「識別可能性」は π(H) の列についての判定であり、比較順序はデモ→初期観測→行動後の観測列→フィードバックとする。
- ID 漏洩検査: CAL の複製ごとに tag 割付を引き直し、tag 文字列の統計量が law の性質（族・テンプレート・必要行動の種別）を偶然水準を超えて予測しないことを順列帰無分布で検査する。フェーズ内での同一 law への tag 再使用は台帳機能であり漏洩とみなさない。
- 証人構成例: 初期 buffer「ABAB」、デモ集合（アンカー記号を含まない入力の対）が同一の2法則 L1「アンカーが現れるまでコピーし現れたら停止」／L2「全てコピーする」は π(H_0) が一致するが、アンカーを含む継続観測への正しい行動が異なるため共通の open-loop 列は存在せず、条件付き方策でのみ分離できる。K0-a の証人ペアはこの型で構成可能である。
- フィードバック: TRAIN では試行ごとに成功/失敗を返し費用に計上。評価では完了後の監査専用とし学習へ戻さない。
- 世界の合法性・終了契約は v2 §1 の列挙（11原子操作の事前条件・効果・no-op の扱い・試行の終了条件）を存続させ、本書と矛盾する場合は §0.1 の置換を優先する。

## 2. 統一文法表と列挙器（B2/C1）

| 評価器の型 | 意味 | 初期在庫 |
|---|---|---|
| ATOM(a) | 原子行動 a（11種） | 行動そのもののみ。意味名付きマクロなし |
| SEQ(x1..xn) | 連接 | 構成は constructor による |
| BIND(v, e, body) | 型付き変数束縛（lexical scope、型 {Sym, Pos, Bool, AST}） | 機構のみ |
| COMPARE(op, l, r) | op ∈ {EQ, LT, LE}。表記 CMP は COMPARE の alias | 機構のみ |
| BRANCH-dispatch | 述語を評価し分岐先を選ぶ評価機構（seed の一部） | **機構のみ。BRANCH インスタンスは初期在庫に存在しない** |

- 学習側 constructor: compose（SEQ 生成）／abstract（BIND 生成、anti-unification）／predicate-slot（COMPARE 述語の生成）／branch-construct（BRANCH インスタンスの生成。3スロットは経験由来の記号でのみ充填可）。
- 評価順序は call-by-value・左から右。評価失敗（型不一致・範囲外参照）は INVALID 行動として no-op＋課金で処理する。
- 定数: 記号リテラル A〜D、相対位置 -16〜16。絶対位置の定数は禁止。サイズ上限（確定候補）: AST 深さ ≤8、node 数 ≤64、述語深さ ≤3。
- **列挙器 E**: 候補空間 = 空 snapshot から上記 constructor の閉包で到達できる AST のうちサイズ上限内の全体。E は (node 数, 辞書式) の正準順序で列挙する。H+ の「構築なし」は学習による構築・永続化をしない意味であり、各 episode で E を予算内に再探索する。FULL の候補集合も E の到達集合と同一である（同一 constructor・同一上限）。反証条件: 一方にのみ属する AST が1件でも示されれば「同一候補空間」の記述を撤回し再設計する。

## 3. arm の権限・費用 matrix（B2/B5）

| arm | 構築 | USE | 確定候補の詳細 |
|---|---|---|---|
| FULL | 全 constructor | 獲得した全記号 | 主張の本体 |
| OFF | FULL と同一訓練（同一 snapshot、digest で確認） | 評価時に USE のみマスク。再学習・別前処理は禁止 | 同一性の検査は §6 の receipt による |
| PRED-ONLY | branch-construct を除く全て | COMPARE 述語は順位付けの特徴としてのみ使用可。BRANCH を含む AST は構築時・読込時に型検査で拒否 | 制御流への述語使用は禁止 |
| REC | feature map の学習のみ | feature map = (buffer 長、記号別カウント、カーソル位置、直近 k 件の成否) の固定統計ベクトルへの写像と、固定形の第一階方策テンプレート内での使用 | 述語型 AST の生成は型で不可能 |
| RANK-ONLY | なし | E の列挙順序への prior 学習のみ。候補集合は E と同一 | 探索順序以外の変更は禁止 |
| FIXED-IF | なし | 贈与 BRANCH スキーマ1件（述語スロットに汎用 COMPARE テンプレート「観測特徴が直近の観測特徴と等しいか」型を充填済み、確定時に形式を固定）＋FULL と同じ述語発見の範囲 | 贈与分は費用に開示。「同一 seed」とは記さない |
| LOOKUP | なし | 距離 = (初期 buffer, 行動列) 対の正規化編集距離。容量 = TRAIN episode 全件（上限512件、超過時は抽出を停止して報告）。最近傍距離 > 閾値 0.2（確定候補）で abstain | 距離・容量・閾値は凍結時に固定 |
| H+ | なし（学習による構築・永続化なし） | E の到達集合全体への同予算の再探索 | 無制限 oracle は機会診断専用で主成績に含めない |

- 全 arm 共通: 主比較は同一の事前割付公開 trace のリプレイ。能動収集は副比較として分離する。停止条件・holdout・公開情報は同一。
- 費用ベクトル（単位ごとに独立照合、加重和に混ぜない）: 予算 b（原始呼出累積、no-op を含む）、episode 数、候補評価数、有料問い合わせ、成功フィードバック数、学習準備費、USE 費、CPU、wall、RSS、保存量、仕様コスト（デモ）。

## 4. 測定・長さ・分母（B4/C2/C6）

- checkpoint: b ∈ {0, B/8, …, B} の9点。s_f(b) は凍結 snapshot の評価成功率（棄権・打切り・INVALID は分母に残す）。checkpoint 評価費は測定費として別掲。
- AULC_f = （s_f の台形積分） / B。主エンドポイントは family ペア差 Δ の §5 の加重平均。判定は §5 の誤差配分と §6 の outcome 決定順序による。
- 長さ表:

| フェーズ | 初期 buffer 長 | 中間 buffer 上限 |
|---|---|---|
| TRAIN | 4〜12 | 16 |
| G1（未見 law） | 4〜12 | 16 |
| G2（未見長さ、OOD 拡張） | 13〜16 | 16 |
| CAL | TRAIN と同一範囲 | 16 |

- 分母: 母集団 frame = 登録生成器の support から、生成器仕様に事前に列挙された構造的除外（容量で到達不能な類型）を引いた集合。除外類型と件数は生成器仕様の版に固定し、結果を見てから追加しない。生成後に発見された不能・識別不能 family は主分母に残し（失敗または K4 の INVALID）、「生成前の除外」と「生成後の不能」は別欄で報告する。

## 5. 法則母集団・抽出・検出力・route（B4）

- law の正規形: (テンプレート ID, 述語 AST 正規形, 分岐操作, 対象役割, 正規化パラメータ)。unique ID = 正規形のハッシュ。N_unique = 登録生成器 support の総数（有限・列挙可能、仕様凍結時に厳密に数える）。
- 生成分布（確定候補）: 4族（転写／反復コピー／観測依存編集／2段連結）へ均等配分（各 0.25）。族内のテンプレート・パラメータ・長さ・語彙は有限グリッド上の一様抽出とし、グリッドは生成器仕様の付表に列挙する。推定対象はこの登録分布に限る。
- **主設計の抽出: unique law の PPS 無復元抽出**。包含確率 π_l は登録分布の law 確率 p_l に比例させる。重複 draw は主設計に存在しない（復元抽出は CAL の診断専用）。
- 推定量: ペア差 Δ の Horvitz–Thompson 型加重平均（重み w_l = p_l / π_l、正規化して使用）。区間は unique law を単位とする cluster bootstrap（G1/G2 は同一親 law を同一 cluster、4族テンプレートで層化併記）。TRAIN/CAL/holdout は親法則の連結成分で隔離する。
- 誤差配分（片側 α = 0.025 の内訳）: 主 family（FULL 対 7対照の ΔAULC、max-T 同時区間）に 0.0125、G1 ゲートに 0.00625、G2 ゲートに 0.00625 を Bonferroni 配分する。max-T の再抽出単位は unique law cluster。
- n の決定: n_required = max(n_aulc, n_g1, n_g2)。AULC は正規近似、二値ゲートは paired discordance 式で、配分後の α' と CAL 実測の保守的分散入力（paired SD と discordance の片側80%上限）を用いる。AND 連結の同時検出力は各部の検出力の積を下限として評価し、0.80 未満なら STATISTICAL 路線を取らない。
- 判定ゲート: 第一に AULC（点推定 ≥ +0.15 かつ同時区間下限 > 0）、追加 AND ゲートとして B 時点の達成率（G1 ≥ 90%、G2 ≥ 80%、最強対照差 ≥ +10pp、いずれも確定候補で CAL プロトコル時に1回だけ改訂可）。
- cost_cap: 全 arm 合計の原始呼出総量の上限として単一の数値で固定する（確定候補の値は CAL プロトコルで提示し、金額・時間換算を併記する）。
- route 決定（機械的）: n_required ≤ N_unique かつ同時検出力 ≥ 0.80 かつコスト内 → STATISTICAL（n = n_required）。有限 frame が全列挙可能で |frame| ≥ n_min_descriptive（確定候補 30）→ FINITE_DESCRIPTIVE（全件評価、分布外一般化・検出力の主張なし）。それ以外 → STOP_UNKNOWN（対照を弱めない）。

## 6. K0・キル条件・ログ・manifest（B3/B5/B6）

### K0 の主張ごと遷移表（校正系列のみで実施。oracle は上界専用）

| 診断結果 | 主張B（経験効率） | 二階スキーマ帰属 | family 採用 | 本実験 GO | 再設計 |
|---|---|---|---|---|---|
| K0-a 証人あり（π(H_0) 一致・分離可能） | 継続 | 継続 | 継続 | 他条件に委ねる | 不要 |
| K0-a 証人なし（列挙完結） | 継続可 | **停止**（認定対象から除外） | 二階を要する family は不採用 | 二階なしの範囲でのみ可 | 課題生成への証人ペア型の追加を次版で必須化 |
| K0-b 識別不能（列挙完結） | **停止** | 停止 | 不採用 | **不可** | 必須（STOP/REDESIGN） |
| K0-c 余地なし（(oracle AULC − 最強対照 AULC) の上限 < δ_AULC = 0.15） | **停止**（飽和） | 停止 | — | **不可** | 予算・課題側の再設計 |
| いずれか UNKNOWN（列挙未完結） | 判定保留 | 判定保留 | 保留 | **不可** | 列挙範囲の拡大が先 |

- K0-a の列挙: 共通 open-loop 列の探索上限は H ≤ 64 手。状態ペアの BFS で列挙し、有限 support と有限の合法行動集合の下で完結させる。完結しなければ UNKNOWN とし、UNKNOWN は PASS/STOP に優先する。
- K0-c の oracle AULC は生成器 support 全件の列挙で厳密に計算する。列挙不能なら UNKNOWN。

### キル条件と outcome の決定順序

| 条件 | 判定式（数値は確定候補） |
|---|---|
| K1 実使用 | 診断 family（事前固定20件）× checkpoint で、ON/OFF の最初の行動または trace digest が異なる組が1件以上。確率的方策では診断状態の行動分布の total variation > 0.1 の状態が1件以上 |
| K2 等価性 | FULL−REC の AULC 差の両側同時区間が ±0.05 内なら「性能の等価性（マージン内）」のみを支持する。「再符号化が機構を説明した」とは主張しない。機構帰属は §3 の比較階層の模様全体が事前登録した読み方と一致する場合に限り、「帰属の候補として整合する」と限定して述べる |
| K3 結果区分 | 下記の決定順序でのみ付ける |
| K4 INVALID | 汚染が及んだ family のみ隔離し再採点しない。再実行は新しい事前登録版でのみ可能 |

- outcome ラベルの決定順序（排他）: (1) K4 INVALID の有無 → (2) 負: 同時区間上限 < 0 → (3) INCONCLUSIVE: 区間が 0 と ±δ の双方を跨ぐ → (4) 小さい: 区間全体が ±0.05 内に収まり、かつ点推定の条件（|Δ_AULC| < 0.05 かつ成功率差 < 5pp）を満たす → (5) 正: §5 のゲート判定へ。
- family 集約: 主エンドポイント・B 時点成績とも §5 の加重で集約し、区間は max-T と同じ再抽出で構成する。

### ログ schema（最小列）

episode_id / law_unique_id（評価側のみ親 ID を併記）/ phase / goal_contract_version / task_tag / demo_set_digest / checkpoint_b / step_index / observation_before_digest / legal_action_set_digest / chosen_action / observation_after_digest / outcome_kind（SUCCESS/FAIL/INVALID/ABSTAIN/STOP）/ 費用ベクトル全項目 / symbol_event（型、依存先、proposal/rejection/promotion/USE/OFF、AST digest）/ receipt_digest。

### アクセス表と manifest

| 主体 | 読めるもの | 読めないもの |
|---|---|---|
| 学習側 | 公開履歴 H_t、公開 trace、自己の snapshot | 評価 manifest、hidden target/rule、holdout score、生成 seed |
| 評価側 | 全 manifest、verifier の真値、凍結 snapshot | （学習への逆流経路を持たない） |
| 監査者 | digest 一覧、ログ全件（事後） | — |

- manifest 必須フィールド: generator_version / distribution_table_digest / random_source_spec（方式と seed の保管場所）/ tag_issuance_rule の版 / split_manifest（親 law cluster 単位の割付 digest）/ demo_set_digests / cost_vector_schema の版 / snapshot_digests / analysis_code_digest / role_read_paths / hash_algorithm（SHA-256）/ failure_log_schema。
- fail-closed: manifest と実体の digest が1件でも一致しなければ、当該 family は INVALID、run 全体は STOP とし、監査ログに記録する。receipt は source-first の manifest に集約し、第三者は digest 再計算と trace 再生で検証する。

## 7. 手続きと段階決定表（B6）

| 段階 | 承認者 | Issue #195 への記録 | 参照する digest | この段で変更可能なもの |
|---|---|---|---|---|
| CAL プロトコル承認 | Owner | 承認コメント（対象文書の版を明記） | 本書＋ドラフトの head SHA | 数値候補の確定（この段まで） |
| CAL 実施 GO | Owner | GO コメント | CAL プロトコルの digest | なし（実施のみ） |
| 事前登録凍結 | Owner | receipt コメント＋repo の receipt 文書 | 全 manifest digest | なし（凍結後は版を上げる） |
| 実装 GO／正式評価 GO | Owner | GO コメント（個別） | 凍結 receipt の digest | なし |

- 「CAL 前に変更してはいけないもの」は決定規則・比較階層・同値関係・route の分岐構造であり、「未凍結の数値候補」は CAL プロトコル承認の段までのみ変更できる。
- 決定記録の正本は Issue #195 のコメントとし、PR #194/#196/#197/#198 は引き続き Draft とする。
