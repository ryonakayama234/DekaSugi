# R2-M-A G3 実装計画 — Q-20261105-10へのLead回答

id: R2-M-A-G3-PLAN-20261105
status: PROPOSED / DOCS_ONLY / DRAFT / PLAN_ONLY / NO_IMPLEMENTATION / NO_EXECUTION
updated: 2026-11-05
tags: r2-m, g3, implementation-plan, four-point-runner, metrology, custody, audit

> [Muse質問票 Q-20261105-10 / PR #182](https://github.com/ryonakayama234/DekaSugi/pull/182)へのQG1〜QG6回答。**本PRは計画文書のみ**。実装・テスト実行・source/順序確定・seal・採点・448 child測定・科学GOは認可されていない。Muse独立精査→Owner別途G3実装GOの順序を守る。

## 0. 凍結原本と研究上の主張上限

正本は[PR #181凍結receipt](https://github.com/ryonakayama234/DekaSugi/pull/181#issuecomment-6659764538)（[Issue #146](https://github.com/ryonakayama234/DekaSugi/issues/146)にも記録）。

- ID: `R2-M-A-20261105-EXHAUSTIVE16-ENGINEERING-PREREG`
- main SHA: `cf844094fb5907a37bb496760e206f9061deb021`
- [事前登録文書](R2-M-A-20261105-exhaustive16-engineering-prereg-draft.md)の SHA-256: `865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68`
- Owner採用の[method v2](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md)とStage 1/2/3（[PR #176](https://github.com/ryonakayama234/DekaSugi/pull/176)、[#177](https://github.com/ryonakayama234/DekaSugi/pull/177)、[#178](https://github.com/ryonakayama234/DekaSugi/pull/178)）を変更しない。
- 全16法則 `abcd=0000..1111`、公開3点 `P=(000,100,010)`、事前commit後の有料 `Q001`、USE4点 `(011,101,110,111)`、7固定arm。`16×4×7=448` fresh child（28/law）、F00/F10の64 paired law-points。実行順序はG5まで未決定。
- 上限は**wall 5秒・CPU 5秒・RSS 512 MB / child**、**各child単回、リトライなし**。原値・中央値を報告し、誤差未評価。外部registryは使わない（GitHubのみ）。
- `Expected K=0`は配線整合性予測で仮説検定ではない。`closure UNKNOWN`、`M_use NOT_CERTIFIED`、`M_gap UNKNOWN`、`N_rep/U/T NOT_EVALUATED`、`F01/F11 NOT_EVALUATED`、B `NO-GO`を維持。旧sealed/heldout・凍結v1/R1・過去の原本は不変。

凍結文書本文や既存INDEXに残る`NOT_FROZEN`は**merge前の歴史的記述**である。G2が完了したことは後続の上記凍結receiptに明示されており、本計画では凍結文書を事後改訂しない。

## QG1 — 4点runnerの構造と境界

**推奨:** `packages/r2_m_a/`に科学用（ただしAは既知法則の工学費用測定）オーケストレーションを新設する。`packages/r2_m_eng`の `records/source_gateway/decoder/validator/sleep_lite/snapshot/dispatch/controls/meter/closure`は、承認済み意味論を再利用する。現行`r2_m_eng.runner`は人工1点fixture専用のまま残す。

| 新規の責務 | 提案モジュール | 固定した制約 |
|---|---|---|
| 契約と448-slot集合 | `contracts.py` | 法則集合は全16、点4、arm7、G5 order manifest未設定なら本番BLOCK |
| 公開P/QとSnapshot | `public_coordinator.py` | Q前の耐久precommit→Q回答を法則あたり一度だけ→公開4からdecode/independent validation/Sleep-lite→1 Snapshot/law |
| source側の境界 | `source_boundary.py` | `source_gateway`は評価側だけでimport。learnerの子へ真値・係数・source object・scoreを渡さない |
| child起動 | `launcher.py` | arm×点にfresh process・別cwd・排他的trace。入力は絶対Snapshot path＋親が固定したexpected SHA＋arm＋USE点＋trace pathのみ |
| 親の資源監督 | `resource_supervisor.py` | 5/5/512 cap、子ごとの独立rusage、停止/失敗の記録 |
| 会計・証拠原本 | `accounting.py / evidence.py` | learn/restore/use等を分離、fsync、digest、採点前lock、欠測/INVALIDを保存 |
| 真値照合 | `evaluator.py` | 全raw出力digestの採点前固定と別途G6 GOを満たすまで起動禁止 |

~~~mermaid
flowchart TD
  A["Frozen prereg + exact runner SHA + future G5 order"] --> B["Evaluator-side P3 → durable Q001 precommit"]
  B --> C["Q001 response, once per law"]
  C --> D["Public decoder + independent validator → one immutable Snapshot"]
  D --> E["USE4 × 7arm: fresh children ×16 laws"]
  E --> F["Parent measurement + child public traces"]
  F --> G["Append-only raw ledger + pre-score digest LOCK"]
  G --> H{"G6 scoring authority and lock verified?"}
  H -->|yes| I["Separate evaluator: known-law truth comparison"]
  H -->|no| J["BLOCK, preserve evidence"]
~~~

対応する凍結`5`の順序を**関数/commit境界で固定**する。(1)公開P3、(2)`Q001`前のprecommit書込＋fsync、(3)独立validatorとSnapshotのbyte SHA固定、(4)448 fresh child、(5)全trace/失敗/欠測digestを真値照合**前**に固定、(6)別の評価側で照合。学習側モジュールとchildに`source_gateway`、`source_boundary`、`evaluator`、歴史的sealed資産へのimportを許さない。静的import graphだけでなく動的import、argv、env、cwdも検査する。公開4回答自体が法則を同定する事実は隠さず、「秘密family」と偽装しない。

**根拠:** 現行`packages/r2_m_eng/runner.py`は1点/7child、`--synthetic-affine`、`subprocess.run(timeout=30)`のfixtureであり5秒hard capも採点前証拠確定もない。`snapshot.py`は復元時に再decoder/validator、`dispatch.py`は合法なOFF fallbackを保持する。現行fixtureを直接4点・本番へ改造すると境界が混ざるため不採用。7armを再実装して意味論を変える案も不採用。

## QG2 — 計測器、hard cap、会計列

**推奨:** 「OS/親によるinclusive child総費用」と「子による内部phase費用」を**別列**にする。Linux/WSL2、単一スレッド、子孫processを作らない直接workerを前提とし、正式G6の前に実行hostを監査する。

| 指標 | 主計測 | 強制／判定 | 採らない方法 |
|---|---|---|---|
| wall秒 | 親の`time.monotonic_ns`、spawn開始〜reap（起動・import・復元・USE・出力を含む） | 親watchdog **5秒**、時間切れは子groupを停止・reap・receipt化 | 子内部のUSEタイマをchild総wallと偽る |
| CPU秒 | 親が対象PIDを`os.wait4`でreapし`ru_utime+ru_stime`。子`time.process_time`は照合用 | `RLIMIT_CPU=5秒`、signal/超過で`RESOURCE_STOP`。kernel秒粒度は記録 | `RUSAGE_CHILDREN`を単一child値として利用 |
| peak RSS bytes | 親の個別`wait4.ru_maxrss×1024`（LinuxのKiB）、子の`RUSAGE_SELF`は照合 | cgroup v2 `memory.max`をRSS上限に対する**別指標の先行guard**として用い、`memory.peak/events`も記録。RSSが512 MBを超えた場合も失格 | `RLIMIT_RSS`（現行Linux非実効）、`RLIMIT_AS`（仮想空間≠RSS）、pollingのみ（peak漏れ） |

cgroup `memory.max`はページキャッシュ等も含み、process RSSと一致しない。**memory.peakはRSSの代用品にしない。** cgroup委譲/child所属・初期化/権限/単独PIDが未検証なら正式測定は`BLOCK`であり、制限なしの自動fallbackは禁止。`wait4`を使うため子の標準出力/エラーは容量制限付き排他ファイルへ直接書く等、二重reapやPIPE詰まりを防ぐ方式を実装・G4監査する。OSのCPU hard capに秒単位の境界誤差があるため「5.000秒を数学的に超えない」とは主張せず、超過/killを記録する。資源測定できない異常終了も0で補わない。

[Linux getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)、[getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html)、[cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)を実装根拠とする（**対象WSL2での適用確認結果ではない**）。

**費用台帳の不変条件:**
- `decoder/validator/candidate/H0`の実回数を`learn/synthesis/sleep_lite/store/restore/use/dispatch_verify`に対応させ、全体`CPU/wall/RSS`と多重加算しない。`AST static nodes`、短絡の`runtime visits`、実行`NOT/AND/OR primitive ops`、Q、trace/snapshot bytesは**異種単位のまま**残す。
- **mainコード確認:** `controls.py`はFIXED-MACROに限らず**5 comparatorのimportで全16 `MACRO_CATALOG`を作る**。各fresh comparatorに実際に発生したimport CPU/wall/保持bytesを`per_fresh_process`へ、親で発生した実費だけを`one_off_preparation`へ一度記帳。両列への二重加算禁止。G4のactual import graphで最終帰属を決める。仮想的な「一度だけ構築してn回再利用」は仮定付き投影としてのみ扱う。
- `snapshot.load_snapshot`の**復元時decoder/validator**はF00/F10を含む各armで計上。STATIC-H+のUSE再decode・独立validatorも別記。`STUMP-1`の14候補は16 affine候補とは異なる族。
- 現行childの`paid_inquiries:1`は公開履歴の**来歴**であり、実際にQを448回行ったわけではない。`paid_q_actual=1/law=16 total`と`child_inherited_public_observations=4`を分離し、child値を単純合計しない。
- 1つの`child_total`には全起動・import・復元・trace作成を含め、内部phase値との不明な差額を`UNMEASURED / unallocated`に残す。`RSS peak`は足し算せず分布を報告。実行環境はCPU/OS/kernel/WSL2/Python/cgroup/affinity/負荷/時計/起動順をreceipt化する。
- `C_life,arm,d(n)`と`Δ_d(n)`は凍結`7.3`の式に限定。`n={1,4,16,64}`の16/64は4 USE点の反復**モデル投影**で追加実測ではない。分離不可なら`UNMEASURED`とし、恣意的な費用総合点や優位の合格閾値は設けない。

## QG3 — precommit、digest、append-only証拠、receipt

**推奨:** 機械的に検証できるappend-only `events.jsonl`（連番、前行hash、payload bytes SHA、event種別、slot、時刻）と、`O_EXCL`の不変原本ファイルを併用する。fsync・read-back digest・directory fsyncが失敗したら続行しない。GitHub-only保全の限界（独立timestamp/独立custodyなし）は凍結どおり明記する。

| 将来の証拠 | 原本手続 | 評価前に満たすこと |
|---|---|---|
| `run_manifest.json` | frozen prereg SHA、runner exact SHA、7arm、閾値、G5 order manifest SHA差込欄 | G5未設定なら正式G6はBLOCK。**本計画で順列/seed/nonceを決めない** |
| `public/precommit/<slot>.json` | P3 history digest、許可Q001/残1/期限、precommitを**Q回答前**にO_EXCL+fsync、PublicGatewayと照合 | 無し/遅延/2回目QはINVALID |
| `snapshot/<slot>.json` | 1 lawに唯一のSnapshot/v2。外部固定bytes SHAを子に渡し、毎childロードで照合 | 改竄/不一致/別SnapshotならINVALID |
| `raw-traces/<slot>.json`と`raw-meters/<slot>.json` | 448全slotを事前列挙。予期せぬ終了もexit/signal・測定可否・欠測/部分出力を記録 | 故障をABSTAIN/正解0に変換しない、再試行しない |
| `commitments/pre-score-manifest.json` | 全448slotに`TRACE_PRESENT/INVALID/STOP/NOT_STARTED`、各digest、イベント鎖末尾、全件数を記録。**評価前にGitHub commitを固定しSHAを照合** | commit未確定なら評価側はBLOCK、失敗も原本へ残す |
| `post-score/score-receipt.json` | G6許可後にだけ別評価入口から既知law真値を照合。raw lock commitを参照 | raw原本を更新・欠測補完しない |
| `environment-receipt.json` | CPU/OS/Python/カーネル/cgroup/計測方針/資源上限・起動順/失敗 | source・cost・G4対象commitとの一致 |

普通のファイル`O_APPEND`とGitHub SHAのみで第三者管理者による改竄まで防げるとは主張しない。単回測定途中にSTOP/INVALIDがあれば、部分原本・予定slot・未実施slotの一覧を保全し、`K_full=NOT_EVALUATED`とする。G5でOwnerが固定する**順序manifestを読み込む場所だけ**実装予定（順序はまだ選ばない）。

**代替案と不採用:** 最終CSVだけ、インメモリprecommitだけ、成功traceのみ採用、採点後digest確定、失敗後上書きや自動再実行は、凍結の手続き証拠を損なう。

## QG4 — テスト戦略

**推奨:** Stage 1/2/3の既存型・Snapshot・fallback・meterテストは保持し、`r2_m_a`固有の**負例検査**を主とする。全て**invented synthetic fixture**であり、本測定・旧sealed/heldoutをCIで動かさない。syntheticの成果を448childの正式費用と混同しない。

| 分野 | 必須負例・検証 | 結果の期待 |
|---|---|---|
| Q契約と境界 | Q前commit欠落/後出し、期限切れ、Q重複、正答/係数のargv・env・payload混入、評価側の学習側import | INVALID、情報隔離、回答の再取得禁止 |
| Snapshotと配線 | expected SHA不一致/trace再hash、F00合法fallback削減、片側だけrestore decoder省略、未知arm・F01/F11/ORACLE呼出 | INVALID / BLOCK、全合法route維持 |
| 資源・会計 | 異常終了・SIGXCPU/OOM・wall timeout・cgroup権限拒否、親子計測不一致、macro import無課金、Qを448回計上 | STOP/INVALID/UNMEASURED、単回・再実行無し |
| 原本・時系列 | O_EXCL重複、events hash破損、欠測隠し、部分traceを成功化、pre-score lockなし採点 | INVALID、原本保持・採点禁止 |
| 網羅・解析 | 16×4×7全slot、F00/F10の64点、全適格ならK構造期待0、欠測なら`K_full=NOT_EVALUATED` | 分母と欠損を明示、K>0は陽性でなく監査STOP |
| 回帰 | `tests/test_r2_m_eng_*.py`の互換、静的/動的import graph、人工fixtureと正式runのID/保存先分離 | exact headで独立に再現可能 |

テスト合格の主張は**実装後に実測して初めて**行う。提案コマンドは`python -m unittest discover -s tests -v`、`python scripts/check_docs.py`、専用synthetic CLI。CIで本測定や秘密heldoutを開かない。資源異常を人工再現する場合も専用隔離child/cgroup内だけで行う。

## QG5 — G4実経路監査 dossier

**推奨:** 実装をmainへ統合した後に、**実際に起動するexact commit SHA**を固定し、以下をread-only dossierとしてMuseに提出。監査中または監査後にコード・runner manifestが変わったら再監査が必要。

| 文書 | 監査対象と根拠 |
|---|---|
| `D0 provenance` | 凍結元main/file SHA、method v2、runner exact head、差分、OwnerのG3 GO、schema/digest一覧 |
| `D1 import/dataflow` | 対象commitの静的＋動的import graph、全子argv/env/cwd、public/評価側フィールド境界、旧sealed非到達 |
| `D2 route inventory` | F00/F10のSnapshot restore、全nonbody fallback到達、decoder/validator、5対照の独立入口、`closure UNKNOWN` |
| `D3 input/budget parity` | 7armの同一公開4情報/Snapshot byte SHA/USE点、容量/tie、Q16・448slot、同一制限・子独立性 |
| `D4 measured-cost paths` | 親wait4・child内訳・cap監査、macro import全5 comparatorの請求と親one-off、復元decoder費、n投影 |
| `D5 immutable sequence` | precommit→Q→Snapshot→trace→pre-score lock→評価、append-only chain、失敗保持、GitHub-only限界 |
| `D6 negative evidence` | QG4の全負例、exact-headテスト/CI/document check、Museによる独立再現、未解決事項 |
| `D7 decision` | Muse署名と未解決/逸脱、Ownerゲート、M_use/M_gap等の認定維持 |

**G4受入条件:** 未監査の実接続route、真値混入、F00能力削減、費用配賦の偽装、hard cap不在、pre-score lock不備が1件でもあれば**BLOCK**。既存R2-M-ENGの過去合格をexact runnerの監査で代用しない。G4合格は`H0_effective(B)=COMPLETE`やG6 GOを意味しない。

## QG6 — 段階分割とPR、見積り

**推奨:** R2-M-ENGの3段階方式を踏襲し、**この文書PRは計画だけ**とする。OwnerがG3実装GOを出した場合に限り、次の**3件の別PR**を順にmain基点で起案し、各段階でMuse査読・Owner受入を経る。

| 将来の段階 | 提出物 | 独立受入条件 | 粗いLOC |
|---|---|---|---|
| I: boundary & custody | contracts/source boundary、公開Q前永続precommit、Snapshot・append-only機構 | source真値の非注入、Q先後/改竄/再試行負例が拒否 | 本体250–450＋test250–400 |
| II: supervisor & accounting | Linux CPU/wall/RSS guard、wait4、cgroup、learn/restore/use分離とmacro帰属 | 各cap人工負例、子異常時の親receipt、二重計上無し、未測定はBLOCK | 本体300–500＋test250–450 |
| III: four-point integration | 4点×7arm×16全slot runner、未採点lockと別採点入口、dossier export | synthetic-only通し検査、正式G5 orderなしならBLOCK、全負例・exact-head候補レビュー | 本体300–550＋test300–500 |

新規合計は本体概ね**850–1,500 LOC＋test800–1,350 LOC**（資源制御が環境依存）。`docs/architecture`・`docs/specs`・`docs/INDEX.md`は実装時に同期する。G5順序/seed/nonce確定、G6実測448child/真値採点/結果解釈、B/新原理/表現体系の研究は**本G3実装範囲に含めない**。

**ゲート:** G3計画→Muse独立レビュー→Owner実装GO→I/II/III段階受入→G4対象exact SHAでMuse監査→別G5順序固定・原本保全→別G6 Owner実行GO。いずれも自動承認されない。

## 7. 追加の技術仮説（新実験を起動しない）

**H1 — 同定可能性と因果的使用差は別。** 公開4bitがF_aff係数の十分統計なので、合法F00が同じpublic4からruntime decoderへ到達できる限り、F00/F10の予測差は構造的にゼロが期待される。`K>0`は新能力の陽性ではなく**監査トリガー**。全16lawが適格でなければ`K_full`は未評価。

**H2 — 速いUSEと低い生涯費用は別。** F10はUSE経路を短縮する可能性がある一方、learn/store/restoreがかかる。FIXED-MACROはUSE decoderを避けても全16entryの実際のimport費がある。数値次元ごとに`Δ_d(n)`を記述する以外に「費用の勝者」を定義しない。`n=16/64`は観測点の反復利用の**投影**であって新サンプルではない。

**H3 — 科学的に重要なのは証拠の時系列。** Q前commit、採点前digest固定、fail-closedな計測があれば「何が測れなかったか」も再現可能になる。ただしGitHub-onlyは独立第三者の保全保証ではない。新概念獲得/未知family転移の主張はこのAから生じない。

## 8. Museへの逆質問票（回答未取得）

**MQ-G3-1 / 512 MB単位:** 凍結`512 MB`のSI実装案を`512,000,000 bytes`（保守的）とする。`512 MiB=536,870,912 bytes`へ無断で緩和しない。このbyte換算を凍結の単なる具体化として受け入れるか、Ownerの単位解釈決定を必要とするか。

**MQ-G3-2 / cgroup hard cap:** 実行予定WSL2 hostでcgroup v2委譲が不可能なら、`RLIMIT_AS`/`/proc` pollingへ黙って切り替えずG6を**BLOCK**し環境選定へ戻す方針でよいか。`memory.peak`と`wait4.ru_maxrss`をどの程度独立照合するべきか。

**MQ-G3-3 / FIXED-MACRO:** 現行`controls.py`の全5 comparatorにおける毎child import構築費を`per_fresh_process`、親で実際に発生する準備だけを`one_off_preparation`として請求し、最後はG4 exact headで固定する方針に異論があるか。既存controlの意味論は変えない。

**MQ-G3-4 / commit粒度:** Q001前はlawごとのfsync済み永続receipt、USE後は全448slotの成功/失敗を含む未採点manifestをGitHubへcommitし、確認後だけ採点する案で、凍結の`precommit`/`digest commit`を十分に満たすか。QごとのGitHub遠隔commitも必要と考えるか。

疑問があるからといって凍結値・実行順・既存方法を変更しない。回答は本Draft PRのレビューに記録し、最終判断はOwnerに留保する。

## 9. 逸脱候補とSTOP

**現時点で凍結内容の改訂は推奨しない。** ただし、(a) cap値/単回ルール/448数/合法OFF/policy等を変更する、(b)実効RSS guardなしで正式実行する、(c)macro構築タイミングを変えることでarm意味論・比較を変える、(d)新たな16/64追加childを実測する、(e)結果後に順序/費用配賦/除外基準を変える必要が生じた場合は、**逸脱候補として旧版を保持し、新ID・新版・独立再査読・Owner別決定**を要する。本計画で暗黙に許可しない。

**現在の状態:** docs-only / PR提出後もDraft / G3実装GO無し / G4・G5・G6未実施 / K・費用・能力はNOT_MEASURED。結論は限定的工学計測にとどめる。
