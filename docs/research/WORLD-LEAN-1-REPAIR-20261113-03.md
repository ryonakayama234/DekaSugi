# WORLD-LEAN-1 修復 -03 — 定数対応表と実行契約

id: WORLD-LEAN-1-REPAIR-20261113-03
status: IMPLEMENTED / SYNTHETIC_ONLY / SUPERVISOR_REAUDIT_PENDING
updated: 2026-11-13
tags: world, repair, protocol, evidence

対象基点: PR #210 head `c618358dfbcc3d1e3ff57cee6058b89019345d60`。
[停止記録](https://github.com/ryonakayama234/DekaSugi/pull/210#issuecomment-6828933595)と今回のOwner修復指示に基づく。
設計 -02 は採用済み、正式評価 GO は成立済み。ただし再監査とOwner再開確認まで正式seed・正式holdout・正式評価は実施しない。
本書が最新の工程状態を示す。旧文書内の当時の `proposed` / GO待ち / stub記述は履歴である。

## 1. protocol.py の全定数の照合

**唯一の定義元は `packages/world_lean/protocol.py`**。評価側の
`world_lean_evaluator/protocol.py` は下記13個を同じ名前で再公開する。
子に評価側モジュールをimportさせず、このデータを持たない公開ファイルだけをコピーするための配置である。
`DEMOS_PER_LAW` の定義は1か所のみ。fixture、曖昧性監査、正式生成、学習側検証・partitionは同じ定数を参照する。
下表は旧評価側protocolの全12定数＋明示化したARMSを網羅する（関数・例外クラスは定数ではない）。

| 定数 | 旧値 | -03 値 | 設計 -02 の対応 | 判定 |
|---|---|---|---|---|
| WORLD | `lean-editor/1` | `lean-editor/1` | §1 新世界版 | 一致・不変 |
| ARMS（明示化） | protocolになし | `(FULL,OFF,STATIC-RANK,LOOKUP)` | §4 4腕 | 一致 |
| N_REPLICATES | 16 | 16 | §6.2 16 seed固定 | 一致・不変 |
| B | `(0,512,1024,2048,4096)` | 同左 | §3.2／§6.1 | 一致・不変 |
| TRAIN_BODY_PAIRS | `((0,1),(1,2),(2,3))` | 同左 | §2.2 TRAIN24 | 一致・不変 |
| HELD_OUT_PAIR_PLAN | `((0,2),(0,3),(1,3))` | 同左 | §2.2 HOLDOUT24 | 一致・不変 |
| DEMOS_PER_LAW | **4** | **6** | §2.3 真3／偽3 | **不整合を修復** |
| QUERIES_PER_LAW | 2 | 2 | §2.2 真1／偽1、24×2=48 | 一致・不変 |
| EXTRA_DIAG_QUERIES_PER_LAW | 2 | 2 | §2.2 最終のみ48 | 一致・不変 |
| DRAW_LIMIT | 4096 | 4096 | §2.3 itemごと有限rejection | 一致・不変 |
| MAX_WALL_SECONDS | 172800 | 172800 | §8 48時間 | 一致・不変 |
| MAX_CPU_SECONDS | 129600 | 129600 | §8 全process合計36時間 | 一致・不変 |
| MAX_SAVE_BYTES | 2147483648 | 2147483648 | §8 2GiB | 一致・不変 |

関連する他モジュールの制限も照合した。これらをprotocolの新しい定義として重複追加してはいない。

| 実装箇所 | 値 | 設計の対応 |
|---|---|---|
| core: OPS / TOKENS / SYMS | 11種 / 14 token / 4 Sym | §1／§2.1 |
| core: MAX_BUFFER / MAX_STEPS / MAX_NODES / MAX_DEPTH | 16 / 12 / 32 / 6 | §1／§3.1 |
| learner: UPDATE_EVERY / MAX_LIBRARY / MAX_VERIFIED / MAX_CONSTRUCTIONS | 64 / 64 / 128 / 1024 | §3.1–3.3／§8 |
| learner: BEAM_WIDTH / BODY_HORIZON | 8 / 6 | 実装全順序 -02、設計 §3.3 に委ねた具体順序。不変 |
| analysis: ARMS / B / N_SEEDS / MAIN_QUERY_DENOMINATOR / BOOTSTRAP | 4腕 / 同じ5点 / 16 / 48 / 9999 | §4／§6.1–6.2 |
| gate: DESIGN_TRANSITION_CEILING / WALL_CAP_SECONDS / CPU_CAP_SECONDS | 252928000 / 172800 / 129600 | §8。正式manifestでも同値 |
| formal manifest: law_count / blocks | 24 / 512 | §2.2／§3.2、16×512×8=65536共有イベント |
| formal manifest: primary / extra length | 4..6 / 7..8 | §2.1–2.2 |

数値条件（平均D≥1/10、12勝、FULL最終≥4/5、最強対照との差≥−1/20、8群≥3/5、曖昧率≤1/10、usage≥12）とkill条件は既存pure analyzerから不変更。

## 2. 設計 -03 の厳密な訂正範囲

[設計 -03](WORLD-LEAN-EXPERIMENT-DESIGN-20261112-03.md) は -02 のbytesに
`6×12=48` → `6×12=72`、`TRAIN更新の4検証例` → `TRAIN更新の6検証例`
の各1回の置換だけを施した。**見出し、文書内部id、updated、status、旧版参照まで敢えて -02 のまま**である。
これは「それ以外byte同一」というOwner条件を優先したためで、版の対応と現在の採用・再開状態は本書／-03全順序で示す。
規範の表、総上限252928000、合格条件に変更はない。-02採用を引き継ぐ。旧 -01／-02 のファイルは変更しない。

## 3. 正式経路の順序とデータ契約

1. `freeze-manifest`: 新規rootにmanifestと外付SHAをexclusive作成。source lockの実bytes／合成digest、lock自身、訂正版設計、全順序、数値、乱数、runtimeを束縛する。source commitはPR/headという外側記録で結び付け、循環自己hashを作らない。
2. `formal-generation`: manifestを既定値と完全一致検証。`owner_resume_reference`、`supervisor_reaudit_reference`、正確な`source_digest`、`manifest_sha256`を持つ外部authorizationが必要。これは独立署名の検証器ではなく、協力的コードに対する明示的運用ゲート。公式runtimeはCPython 3.12.12。**本ラウンドはこの入口を実行しない。**
3. 検証後のみ評価親processが32byteのOS乱数masterを取得。masterとTRAIN／main／extra原本は`private/`。各実現のTRAIN24／HOLDOUT24、真偽、重複排除、draw capを固定手順で生成。GENERATION_STOPは全体停止。生成結果に合わせた再抽選・law除外・seed補充なし。
4. 同じ512ブロックを独立のFULL／STATIC-RANK／LOOKUP子へ渡す。FULLのみ獲得ASTを生成。STATIC-RANKは公開頻度、LOOKUPは公開traceを保持し、両者の永続獲得ASTは空。OFFの全snapshotはFULLのbytesをそのままコピーする。公開trace digestを3者で照合。
5. **全実現・全checkpoint・全腕のsnapshotを保存し、`snapshots-fixed.json`を先にexclusive固定**。欠けたcheckpointを0成功や別snapshotへ置換しない。このファイルと個別bytesの検証前にはinferを1件も呼ばない。
6. 各trialは`python -I`の新規子process。子rootには公開5ファイルだけ。入力はsnapshot、腕、6公開デモ、query初期状態、公開token表のみ。target／recipe／seed／law／phase／私有pathを渡さない。query由来状態の持越しなし。成否照合と合法trace再生は親のみ。
7. 全mainを5点、extraを最終だけ全腕で一括評価し、全行をexclusive保存。全原本・snapshot・trial digestを再照合して解析する。正式経路は既存exact AULC／16-seed統計／AND判定を使用。最終FULLの8群、usage、48-recipe一致監査、extra曖昧性も保存。
8. source/manifestを再検証してcompletion receiptを作る。事故・ログ欠落・digest不一致はSTOP_INVALID／INCOMPLETE、資源超過はRESOURCE_STOP／INCOMPLETE。未完了seedを除いて認定しない。開始済みrootでのgeneration/run再実行・上書きを拒否する。

公開tokenの表示は主／副次で別の不透明名を生成し、順序つき4token宣言で内部の4つのopaque identityへ束縛する。子は公開入力を正規化し、snapshotと出力を内部identityで返す。Unicodeの大小や表示名の意味を使わない。改名・長さ同時診断なので個別G1/G2認定は行わない。

wallはgenerationからの実経過、CPUはgeneration＋親＋待機回収した子の合計。保存量を各子の前後に確認し、残余wall/CPUの短い方で子をtimeoutする。全工程の原始遷移（構成・検証・再生も含む）を親と子で別計測し、設計の252928000も保守的に停止上限として監視する。cap到達時に全完了を名乗らない。RSSは親／子の最大をmetadataに残すが、設計の512MiBは目安であり新たなhard capにはしない。

原始遷移のカウンタと合法行動trace出力は観測専用で、候補順位・乱数・成功条件は参照しない。
`simulated`等の既存局所メーターに加えて全stepを測り、候補構成や再検証費用を隠さない。
個別原始遷移、候補数／構成数、展開上限、snapshot来歴、CPU/wall/RSS/保存量は別に記録する。

## 4. 修復差分と人工検証

- protocol定数4→6と、全定数対応表。
- fixture・TRAIN曖昧性・正式経路・学習側のデモ長／partitionの参照統一。
- 候補生成の分岐なしpartitionに残っていた`(0,1,2,3)`も`range(DEMOS_PER_LAW)`に修復。6例全体を構成段階でも検査するための直接依存修正で、候補予算・順位式・基本文法は不変更。
- 正式stage driver、公開alphabet束縛、3者独立TRAINとFULL/OFF同bytes、snapshot barrier、完全schedule解析、資源／上書き停止を追加。
- `synthetic-dry-run` は**1実現、8 TRAINブロック、b=(0,64)、TRAIN1法則、主2＋extra2 query、24 trial**という明示的縮小profile。同じstage関数を通すが、公式master乱数も正式HOLDOUT生成器も呼ばない。人工の固定seed bytesは`ARTIFICIAL-...`と表示し正式seedとは別物。科学的判定はNOT_RUN。
- 正式analyzerのAND／不完了拒否は、別の架空16組の整数成績だけでunit検証する。縮小dry-runを16 seed正式評価と呼ばない。
- schema／import root／相対private path negativeは協力的コードに対する検証。同一UIDの悪意ある絶対path読出しへの防御、独立escrow証明とは主張しない（採用済みRQ2を維持）。

検証コマンド・実測結果・digestは[修復証跡](../../experiments/WORLD-LEAN-1/runs/20261113-repair-03.md)を参照。
監督者再監査とOwner再開確認までここで停止する。
