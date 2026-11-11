# WORLD CAL 実装計画（実装ではない）— Research Lead 提出

id: WORLD-CAL-IMPLEMENTATION-PLAN-20261111-01
status: PLANNING_ONLY / SUPERVISOR_AUDIT_PENDING / IMPLEMENTATION_GO_NOT_GRANTED / NOT_CAL_AUTHORIZED
updated: 2026-11-11
tags: world-expansion, cal-preparation, implementation-plan, research-lead, design-only, no-execution

> **この文書は実装の作成依頼・実装 GO・CAL_AUTHORIZED・実験 GO・FROZEN のいずれでもない。** 承認済み [WORLD-CAL-PROTOCOL-20261111-01](https://github.com/ryonakayama234/DekaSugi/blob/156491a5e710b2ef8b7ea38d9fa92f83439aa9f5/docs/research/WORLD-CAL-PROTOCOL-20261111-01-lead-draft.md) と [仕様パック第6版](https://github.com/ryonakayama234/DekaSugi/blob/351016fe0e2d468c80736a477133a274cfb713b8/docs/research/WORLD-PREREG-SPEC-20261110-06-specification-pack-v6.md) の**将来の実装・独立監査手順だけ**を提案する。Owner の次の別判断より前に、世界シミュレータ、K0、BLIND_DESIGN_CALCULATOR のコードを作らず、CAL／simulation／K0 を実行しない。実 holdout の instance・target・score・seed は封印維持。

## 1. 責任分界と将来の工程

1. **現在**: Lead が生成器 data source と本計画を Draft PR へ提出。監督者は条項対応・数式・想定計算量・情報流を独立審査し、未解決事項は逆質問にする。Owner は提出物の採否を決めるが、この受入だけで実装・CAL は始まらない。
2. **実装を望む場合**: Owner の**別の明示的な実装 GO**で対象 module／fixture テスト範囲を指定。許可後に初めて実装・合成 golden テスト・CI を実施。実データ、CAL、K0 本実行、power simulation、sealed split 実体は触らない。
3. **第三者監査**: 監督者が source-first 仕様・コード・境界・数値一致・費用に対する PASS/PARTIAL/FAIL を記録。FAIL/PARTIAL は未承認状態を維持し、修復は別 head／新 digest で再監査。
4. **algorithm_digest**: 全 source／依存環境／規範入力の byte digest と再現性を独立確認して**その時点の exact commit**へ結合する。digest 固定は CAL 実施許可を意味しない。
5. **Owner 別判断**: 生成器 source digest＋監督者審査＋algorithm_digest＋後続の許可済み sealed split 入力・seed custody 等を見て、Issue #195 へ **CAL_AUTHORIZED** を明示記録するかを Owner が別途判断。承認前は一切実施しない。
6. **CAL_AUTHORIZED が成立して初めて**: 承認された CAL 実施者が CAL 分離 family を用い、許された source と設計メタデータだけで CAL／K0／simulation を実施。CAL_COMPLETE は計測成果の提出であり FROZEN ではない。B_final の変更は固定 L90 写像による**一度だけ**。正式 EVAL と学習／実験は別途 FROZEN と EXECUTION_GO を必要とする。

この順序は [Issue #195 PROTOCOL_APPROVED](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6784655532) および [監督者 RQ-CAL-01／04 回答](https://github.com/ryonakayama234/DekaSugi/pull/204#issuecomment-6784585337) を保持する。

## 2. 実装単位、入出力境界、条項対応

以下の path は**将来の提案名**であって、作成済みファイルを意味しない。module は import 時にデータ生成・暗号種生成・計測を起動しない（side effect 禁止）。

| 将来 module / 役割 | 機能・source-first 入出力 | 仕様第6版／CAL プロトコル |
|---|---|---|
| `world_cal/world.py` 世界シミュレータ | `reset,observe,legal_actions,step`、buffer≤16／cursor／selection／clipboard、11原子操作、Sym 等変性、成功時吸収、no-op と ACTION_FAULT の1 call課金。verifier truth は独立 private path。 | 付表A、§1/§2/§4；§1、§6.2 |
| `world_cal/generator_contract.py` source 読取・型検証 | 384 law 分布と p_l の raw byte digest、有限グリッド・容量除外 F・親 root・sealed split quota を**検証**。authorized 時のみ abstract instance に遷移。生成器定義を推論結果に適合させない。 | §4/§5/§6 manifest；§0、§6.1、§7.3、RQ-CAL-01 |
| `world_cal/space.py` AST／列挙 | ATOM/SEQ/BIND/COMPARE/BRANCH-dispatch、de Bruijn 正規化、`(node数,正準文字列)` 全順序、深さ8／node64／predicate深さ3、Sym live binding、arm 権限の共通評価器。 | §2/§3；§1、§7.1 |
| `world_cal/k0_open_loop.py` | pair の `(state_left|DONE_SUCCESS,state_right|DONE_SUCCESS,step)` BFS。24 action tokens、200万 state cap、成功側は追加実行/課金なし、全候補探索完結時だけ OPEN_LOOP_WINS=false。 | §1/§6 K0-a、付表A；§6.2 |
| `world_cal/k0_history_dp.py` | alpha-renamed `π(H_t)` の公開履歴木 DP。K0-a 条件付き成功、K0-b TRAIN(複数試行/feedbackあり) と EVAL(単 episode/feedbackなし) の別木。200万 node cap と UNKNOWN 優先。 | §1/§6 K0-a/b；§6.2 |
| `world_cal/k0_oracle.py` | K0-c の抽象法則・公開 instance/demo 分布・同一 Space/B/checkpoint/goal contract に限定した最良成功曲線と飽和上限。L90 は CAL 24 law 各1代表 instance の nearest-rank、欠測を外さない。 | §5/§6/§7；§2、§6.1/6.2 |
| `world_cal/prf.py` | Owner escrow 256-bit seed を後日許可 role が取る HMAC-SHA256 counter PRF。domain + model digest + scenario + n + repetition + stage + index を長さ曖昧性なく byte encode。53bit `u=(x+.5)/2^53`、Box–Muller、Phi=erfc、全順序 stable tie。PRF domain は split/tag/demo/simulation/bootstrap ごとに分離。 | §5/§6 access；§5、§7.3 |
| `world_cal/gtheta.py` | G_θ 3シナリオ (BASE/LOW/HIGH) 6因子 Gaussian、AR(1) 9点、8 arm×2 gate×4 episode、7対照の固定強さ、64回二分法の最小 kappa root、同一 Y から10 AND 成分。実 holdout 成績の読込なし。 | §5 S1；§3/§4/§5、model JSON |
| `world_cal/sampford.py` | q 正規化、certainty 分離、water-filling `Σπ=n`、固定サイズ Sampford PPSWOR、**同一確率法則に整合する二次包含 `π_ll'`**。n=1／不適格 π_ll は不可。 | §5；§5 |
| `world_cal/inference.py` | 非正規化 HT（certainty の係数は q）、SYG 分散、親 cluster 倍数を使う non-normalized bootstrap（999）、7比較 studentized max-T、G1/G2 片側下限、FULL−REC の独立95%両側 K2 accounting。 | §4/§5/§6；§5 |
| `world_cal/power_route.py` | MC_R=10000×各 n×3 scenarios、Clopper–Pearson 片側99% lower、10 AND、union bound、`n=2..min(N_eligible,512)` 昇順、route と費用 `C(n)`、欠測 STOP_UNKNOWN。 | §5/§7；§3/§4/§5 |
| `world_cal/cal_measure.py` | CAL 24 law で oracle 最短手数 L90、強対照飽和余地、費用ベクトルと分散／共分散の**記述的診断のみ**、TRAIN law の G2 長さ容量診断、ID-only tag 特徴→L2 logistic / 5-fold CV / OVR macro AUC /999ラベル置換。正式 EVAL は測らない。 | §1/§4/§6；§1/§2/§6.1 |
| `world_cal/ledger.py` | role read-path の明示 allowlist、E2 CSV 5376行 digest、Episode/Family/Run の3層 schema、fault/invalid/unknown、raw trace・UTF-8 byte digest・元入力・再生ログ。 | §3/§4/§6/§7；§7.1-7.3 |
| `world_cal/receipt.py` | calculator payload は**閉じた7キーのみ** `N_eligible,n_required,route,power_lower_bound,cost_cap_check,algorithm_digest,split_digest`。RFC8785 JCS→Ed25519 署名を外部 envelope に保存。署名/ハッシュ不一致時 fail-closed。 | §5/§6/§7；§7.3、§8 |

**原則**: private verifier truth、holdout law↔weight、snapshot、PRF secret は別 role／別プロセス／別ファイル権限。learner には `CAL_ORACLE` と `CAL_DESIGN_META` が常時 deny。calculator の READ は `design/split_metadata:{N_eligible,q,parent_cluster}` と承認済み `analysis/*` の閉じた集合だけ。E2 の `CAL` learner 行は全 deny。運用アカウントで ACL を無効化する「テスト専用迂回路」は本番に残さない。

## 3. テスト戦略（**将来の実装 GO 後に実行**）

機械的単体テスト、性質テスト、独立実装の数値 golden、監督者の別環境再計算、権限遮断の negative test を分離する。golden は**手計算可能な合成 fixture**のみ、holdout seed／実 instance は用いない。

| 条項・対象 | golden case と反証用テスト | 合格条件／誤差 |
|---|---|---|
| 付表A／world | `reset('ABAB')` は cursor0、selection none、clipboard空。`MOVE_RIGHT×4` で cursor4、`INSERT(A)` で `ABABA`、成功時は DONE_SUCCESS。selection 長 r を持つ INSERT/PASTE の `L-r+insert_length` を照合。 | 状態・イベント・呼出数は**完全一致**。成功後の余剰 token は実行・課金しない。 |
| §4 action event | len16 無選択への INSERT は no-op＋1 call、cursor0 の DELETE_BACK は no-op＋1、live Alphabet 外 Sym は ACTION_FAULT＋1。 | fault で episode を誤終了しない。K4 汚染と混同しない。 |
| §2 Sym／AST | 4 role の全24 rename で `execute(ρ(s),ρ(a))=ρ(execute(s,a))`、node／深さ／de Bruijn／enumerator 重複除去、初期 BRANCH instance 不在。 | AST の正準 bytes・legal decisions 完全一致。 |
| §4/§5 generator | 生512、無効 role128、unique384、parent96、各 p_l 総質量1/4、G2 除外 law×L 288、384×9×192=663552、親単位 quota 24/24/336。全384 law ID再計算。 | **整数・有理数で厳密一致**、2 JSON raw SHA一致。意図しない law/instance 事後除外なし。 |
| §6 K0 | **既知陰性**: `ABAB→ABABA`／`ADAD→ADADC` は仕様 §1 の9 token open-loop 証明に合う（成功時吸収を考慮）。条件付き方策は公開履歴だけ、TRAIN と EVAL feedback を別木にする。 | この pair を K0-a 陽性に数えたら FAIL。完全 BFS／DP 未完は UNKNOWN、偽の不在証明をしない。 |
| §5 HMAC/normal | HMAC-SHA256 に RFC4231 等の既知ベクトル、53bit uniform の開区間、Box–Muller: `u1=u2=0.5` なら `Z0=-sqrt(2ln2),Z1≈0`。Phi(0)=0.5。 | HMAC bytes**完全一致**。浮動演算は同一 pin された参照実装に対し絶対誤差≤`1e-10`、NaN/∞不許可。 |
| §4 G_θ | 全3 scenarios の6寄与和1、共有因子 scope、AR(1) 9点、FULL endpoint .95/.85、対照の d 列、kappa の64回二分法最小根。same Y で10 AND を作成、Contrast 独立乱数なし。 | endpoint と root residual ≤`1e-10`。根なし／境界不能は STOP_UNKNOWN。相関構造は独立 golden covariance と照合。 |
| §5 PPS/HT/SYG | 均等3 law・n=2 なら `π_i=2/3, π_ij=1/3`、n=3 なら全 certainty。`q=1/3,π=2/3` の HT 係数は `1/2`、n=N で HT 真値一致。Sampford unequal weight の小 N は全標本確率を独立列挙。 | `Σπ=n`、`Σ_{j≠i}π_ij=(n-1)π_i`、対称・非負・確率加算・SYG の独立照合がすべて≤`1e-10`。n=1 等は不可。 |
| §5 bootstrap/max-T | 2親 A/B で resample `(A,A)` の HT は `2×HT(A)`、`(A,B)` は元の HT。7比較は**同じ resample**、G1/G2 も law-level のみ。Studentized=0分散の退化 fixture。 | 重みの再正規化、episode 再抽出が混じれば FAIL。k<2/退化は STOP_UNKNOWN。 |
| §4 AULC、§5 CI/power | 9点 `s_j=j/8` または定数0.5は AULC=0.5（分母 B、B+1ではない）。MC 1万件全成功で片側99% CP 下限は `0.01^(1/10000)`。α主0.0125／G1,G2各0.00625、K2は別0.05両側。 | AULC≤`1e-10`、CP beta 逆関数誤差≤`1e-10`、事前固定ゲート・10 AND の判定は完全一致。 |
| §6 ID-only | 合成された無関係 tag、既知 AUC の小表、親ごとの辞書順5-fold、L2 `C=1`、OVR macro AUC、999 label permutation。 | 必要 class が fold で欠ける／未収束（tol1e-8, max1000）／未定義 AUC は STOP_UNKNOWN。score と tag の混線は禁止。 |
| §7–§8 ACL/receipt | E2 全5376キー（allow383／deny4993）を原表と byte 照合。learner から `CAL_ORACLE`／SEC／holdout target を read する negative test。7キー以外の payload、署名無効、source digest 不一致を注入。 | 許可外 READ と不正 writer は絶対に成功しない。JCS/Ed25519 検証、sha は**完全一致**。STOP_UNKNOWN/STOP_INVALID を正常認定に変換しない。 |

**`tol=1e-10` の規範**: binary64 の数値ルーチンであって、「結果が近いから異なる確率法則・アルゴリズムを採用可」ではない。比較では `abs(actual−golden)≤1e−10` を当該プロトコルが tol を要求した数値へ適用し、分母0／逆 CDF 境界／丸めにより判定が変わる場合は STOP_UNKNOWN。SHA-256・HMAC・シリアライズ・法則 ID・原始呼出数・run outcome・ACL は**ゼロ許容差の byte／離散値一致**。固定バージョンの Python、libm、アーキテクチャ、依存ライブラリ、浮動小数点設定を監査 artifact に記録し、同じ入力と seed で異なる出力 digest が出た場合は環境再固定・再監査。浮動計算順序や並列 reduction の非決定性を隠さない。

**再現試験**: 許可後の合成 fixture に固定の非秘密 seed を使い、別プロセス2回・監督者別環境で `raw input→normalization→draw sequence→aggregate→JCS payload→SHA-256` を照合（同一入力・同一 pin 環境で同一 digest）。1bit変更したモデル／ACL／source／seed／配列順序で digest が変わり fail-closed することも検証。これは実 holdout の seed を使用しない**計画上のテスト**である。

## 4. algorithm_digest の固定手順と Owner CAL_AUTHORIZED 記録

1. **対象の列挙**: 将来の承認済み実装 commit の tracked source `world_cal/*`、該当テスト／golden fixture／AST schema／sampling 法、pin された interpreter＋数学ライブラリ＋依存 lockfile、SHA-256／RFC8785／Ed25519 バージョン、承認済み仕様第6版 exact blob、CAL プロトコル exact blob、G_θ JSON の SHA-256 `31124f2d…e375d077a`、E2 CSV の SHA-256 `faf1962f…a76b44c`、生成器2 JSON digest、各 stage の role paths、CI job 定義を**閉じたファイル一覧**へ登録。別 namespace の seed 値／holdout truth は入れない。
2. **byte-lock**: 各 raw bytes の SHA-256 と path、サイズ、文字コード、commit、toolchain を辞書順で収録した `algorithm-source-manifest` を immutable source-first artifact にする。manifest 自身をその manifest のハッシュ対象にせず、`algorithm_digest=sha256(exact manifest bytes)` を独立した監査記録に置く。曖昧な `git HEAD` や「最新 package」参照は禁止。
3. **独立監査**: 実装担当者が合成 fixture で golden/境界/再現性を満たした証跡を提出→**監督者が別 actor／別環境で** manifest と source・all 7 output keys・権限分離・Sampford `π_ll` まで再演算→PASS した exact commit／digest のみ固定候補化。変更があれば digest を失効させ再テスト・再監査。
4. **決定記録**: Owner の別 `CAL_AUTHORIZED` 明示記録（Issue #195）には generator_version、2 JSON bytes digest、reviewed source commit、承認済み spec/protocol/model/ACL digests、**audited algorithm_digest**、split ルール・承認時の sealed split digest の保管経路／受領状態、seed escrow role、監督者 verdict/link、範囲・禁止 read paths、CAL 以外の GO が false であることを明示。既承認 `PROTOCOL_APPROVED` の lock 数値を再選択しない。
5. **受領後も fail-closed**: CAL 開始時には各 raw source を再ハッシュし、署名付き設計メタデータ／runtime manifest 参照（第6版 §6、プロトコル §7.3）と照合。不一致は停止、後追いで実行条件を緩和しない。

**責任主体**: Lead=成果物と設計、許可後の実装担当=コード・試験記録、監督者=独立数値／アクセス監査と digest 確定候補、Owner=実装許可と CAL_AUTHORIZED の個別判断。algorithm_digest は**今は null／未固定**。

## 5. 計算量と予算（すべて**事前の合成的・記号的見積**）

### 5.1 原始呼出 `cost_cap` は CPU 予算と別

承認済みプロトコル §5 の保守的上限（8 arm の原始 call の合計、CAL 予約を含む）:

```text
C(n) = 250000 + 8 * B_final + 2 * 20 * T_horizon
       + 8 * 2 * 9 * 4 * T_horizon * n
T_horizon = 24, B_final ∈ {4096,6144}, cost_cap = 20000000 calls
```

| 設計上の n | B_final 上限6144での C(n) | 2,000万 calls 比 | 判定 |
|---|---:|---:|---|
| `n=336`（提案 generator の予定 N_eligible） | **4,944,976** | **24.7%** | calls 式の上では cap 内 |
| `n=512`（プロトコルの探索上限、仮想上界） | **7,378,000** | **36.9%** | calls 式の上では cap 内 |

この `n=336` は今回の source grid＋split quota からの**設計算術**であり、holdout instance を抽選した結果ではない。有限記述 route の全件成績が有効になる保証ではない。実 CAL reserve 不足・学習/評価の実費超過・fee schema 不一致は STOP_UNKNOWN/STOP_INVALID。CPU・wall・RSS・候補評価・demo の仕様費を呼出数へ換算して「予算内」と言わない。

### 5.2 simulation の本当の規模：原始 calls と独立

承認済み計算規則: `MC_R=10000` × **候補 n の整数昇順（必要なら全走査）** × **3 scenario**。各反復の synthetic outcome は `8 arm×2 gate×9 checkpoints×4 episodes×n = 576 n` Bernoulli（共有 Gaussian を使用）。各反復で `999` 回の parent cluster bootstrap。これは**現時点で実行していない数式ベースの上限見積**。

| 全候補を調べる仮定 | n 候補数 | MC 反復総数 | binary outcomes の理論個数 | bootstrap 複製数 |
|---|---:|---:|---:|---:|
| `n=2..336` | 335 | **10,050,000** | **978,307,200,000**（約9,783億） | **10,039,950,000**（約100億） |
| `n=2..512` | 511 | **15,330,000** | **2,269,330,560,000**（約2.27兆） | **15,314,670,000**（約153億） |

bootstrap を各標本サイズ n の law/cluster 寄与で愚直に積算するなら、`n≤336` で**約1.70兆**、`n≤512` で**約3.94兆**の寄与処理を要する上限規模（実際の k は標本内親数による）。例えば binary 生成だけが仮に**毎秒100万 outcomes** で処理できても `n≤336` で約11.3日、`n≤512` で約26.3日の純生成時間となる。実測 throughput ではなく、PRF・Normal CDF・Sampford・bootstrap・max-T・データ転送・監査は未加算。**calls cap 内だから simulation が実行可能という結論は成り立たない**。

複雑度の概形: world step は buffer≤16 のため O(16)、K0 BFS/DP は**各診断200万** state/node cap と `T_horizon=24`、本質的に分岐数・履歴数は指数的。generator 静的列挙は O(384＋96＋law×L)、Sampford の `π_ll` は最低 O(N²) データ規模で、exact 計算方法の計算量を別途監査。simulation は naive O(3×MC_R×Σ_n[576 n +999×n]) に、確率法則の抽出と max-T 計算が追加される。

**対処方針（境界）**: 実装 GO 後の**合成 fixture に限る** deterministic profiler で `PRF/G_θ, Sampford/π_ll, bootstrap/max-T, I/O` を個別計測し CPU/wall/RSS 計画を提出する。cache は q・π・π_ll など同一入力の純関数結果だけ、reduction の順序を維持し、圧縮や vectorization を使っても MC_R／999／n 昇順／3 scenario／誤差・digest 条件を一切変更しない。部分的な試走から「CAL 完了」と呼ばない。計算資源・時間・exact π_ll の実現性が不足するなら**STOP_UNKNOWN** として監督者へ報告し、サンプリング法・反復回数・数値閾値・アルゴリズムを勝手に縮小せず、必要なら**新プロトコル版→再審査→Owner 再承認**を求める。simulation CPU の現実的予算は、現時点の cost_cap とは**別途監査が必要な未確定リスク**。

## 6. reviewer の blocking checklist と逆質問

| Gate | 要求される証拠 | 本計画の状態 |
|---|---|---|
| G-SOURCE | 生成器2 JSON 全 bytes SHA・384 p_l 行・全構造除外・parent root・F/N_unique | **Source draft 提出**、監督者 acceptance 待ち |
| G-SEMANTICS | 付表A 11操作／24 horizon／吸収成功／K0 TRAIN/EVAL 権限での golden・型検査 | **未実装・未実行** |
| G-NUMERIC | HMAC／Box–Muller／G_θ root／Sampford `π_ll`／HT/SYG／bootstrap／max-T／CP の独立 golden | **未実装・未実行** |
| G-ACCESS | E2 行全量、source-first read paths、7-key Ed25519 receipt、seed 漏洩 negative test | **未実装・未実行** |
| G-REPRO | pinned 環境・raw SHA・同一入力同一 digest・第三者再計算 | **未実行** |
| G-COMPUTE | calls 式と CPU 計測を分離、worst-case MC 負荷を監査し超過なら STOP/再承認 | **数式見積のみ** |
| G-AUTH | 監督者監査済み algorithm_digest＋Owner の CAL_AUTHORIZED 明示記録 | **未成立** |

**RQ-PREP-I01（Sampford 実装の独立基準）**: `π_ll'` が同じ Sampford 抽出法則に整合することを監査するため、無復元の原実装・exact reference 計算法を別 actor に割り当てる方針でよいか。近似的な二次包含を黙認しない。ゼロ分散／k<2／小さい n の不適格が出た場合は §5 の既定 STOP に従い、選択的に n を飛ばさない。

**RQ-PREP-I02（CPU feasibility）**: 2,000万 primitive calls と**別**の約100億 bootstrap／約9,783億 synthetic outcomes（n≤336 の全走査時）に対し、どの CPU/wall/RSS 枠を事前監査対象とするか。実測 profiler による STOP_UNKNOWN リスク評価を受けてから、実装 GO／CAL_AUTHORIZED を Owner が判断できる形にしたい。現在の計画では CPU の保証はしない。

**RQ-PREP-I03（暗号資料の custody と split digest）**: protocol §5 の seed escrow が CAL GO 後である一方、§7.3 には split allocation digest を持つ runtime manifest が必要。source-only 段階の null と、Owner がいつ非公開 digest を承認記録へ添付するかの手順を監督者に確認したい（generator 定義・seed 値・実 split の混同防止）。

**最終区分**: 実装の作成・監査が完了しても **CAL_AUTHORIZED ではない**。Owner が Issue #195 で別途明示決定するまで CAL／simulation／K0 本実行は不可。さらに CAL_COMPLETE も FROZEN／正式実験 GO の代替ではない。
