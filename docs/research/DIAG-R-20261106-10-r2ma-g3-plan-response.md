# R2-M-A G3 — Q-20261105-10への回答・科学用4点runner実装計画（提案）

id: DIAG-R-20261106-10-R2MA-G3-IMPLEMENTATION-PLAN
status: proposed / docs_only / plan_only / no_implementation / no_execution / pending_muse_review_and_owner_decision
updated: 2026-11-06
tags: r2-m-a, g3, qg1-qg6, scientific-runner, accounting, custody, exact-head-audit, owner-gate

> **権限:** [監督者質問票 PR #182](https://github.com/ryonakayama234/DekaSugi/pull/182)へのResearch Lead回答。**本書は計画提案のみ**であり、実装、科学用runnerの実行、law順序/seedの確定、source取得、採点、G4/G5/G6の開始、PRのmergeを許可しない。独立精査後の**Ownerによる別途G3実装GO**が必要。凍結原本を変更しない。

## 0. 正本・観測事実・仮説・出口

### 正本の固定（変更不可）
- G2凍結receipt: [PR #181 コメント 6659764538](https://github.com/ryonakayama234/DekaSugi/pull/181#issuecomment-6659764538) および [Issue #146](https://github.com/ryonakayama234/DekaSugi/issues/146)。凍結main commit **cf844094fb5907a37bb496760e206f9061deb021**、原本文書 [R2-M-A-20261105](R2-M-A-20261105-exhaustive16-engineering-prereg-draft.md) のbytes SHA-256 **865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68**。**FROZEN**はreceiptが正本。原本内の歴史的NOT_FROZEN記述を遡及修正しない。
- 全16 F_aff法則（0000–1111、列挙集合であり実行順序ではない）、public P=(000,100,010) + **Q001=001を各law一度**、USE=(011,101,110,111)、**16×4×7=448 fresh child**、28/law、64 F00/F10対応点。F01/F11=NOT_EVALUATED、ORACLE-REFはevaluator-only。Kの配線期待は0で、仮説検定ではない。
- **wall 5秒/child、process CPU 5秒/child、process peak RSS 512 MB/child**。単回計測・自動リトライなし。各lawの生値とarm別中央値、誤差未評価。費用ベクトルの異種次元を恣意的な重みで合算しない。
- F10: validated persistent body → episodic_exact → h0_consistent → runtime_affine_decoder → ABSTAIN。F00は**persistent body呼出だけOFF**、他の全合法nonbody fallbackと公開情報からのSnapshot復元decoder/validatorを維持。5対照は独立armでありfallbackではない。
- closure_status=UNKNOWN、M_use=NOT_CERTIFIED、M_gap=UNKNOWN、N_rep/U/T=NOT_EVALUATED、B=NO-GO。G4実経路監査、G5順序固定、G6工学測定は**未許可**。外部registryなし/GitHubのみ（独立時刻証明なし）。

### mainで確認した実装と未解決点
- 現行 [Stage 3仕様](../specs/R2-M-ENG-STAGE3.md) と [Stage 2仕様](../specs/R2-M-ENG-STAGE2.md) の実装はmainに統合済み。人工fixture runnerは **1 USE点×7 child**。科学用4点・448 child・G4監査・費用強制は未実装。
- packages/r2_m_eng/runner.pyはsubprocess.run(timeout=30)の工学fixtureである。**科学上限wall=5秒に流用不可**。同fixtureには実測の採点前GitHub custody機構もない。
- packages/r2_m_eng/controls.pyの **MACRO_CATALOGはimport時に全16 entryを構築する**。FIXED-MACRO以外の4対照プロセスでも同モジュールimportで準備が生じる。現行の関数内CPU/wall計測はimport前と子プロセス起動を含まないため、現状の工学UseTrace費用だけで総process費用や公平な生涯費用を主張できない。この観測を隠さず会計原則で処理する。
- **独立研究仮説ではなく計測設計上の仮説**: 一般的な1点fixtureの単純4回ループ化は、precommit・raw outputの採点前固定・子の起動費・import費・欠測を隠す危険がある。別の科学用境界と親側メータを必要とする。対立仮説は「既存コードの出力にループを追加すれば十分」だが、上記の未実装境界のため採用しない。

## QG1 — runner構造と隔離、凍結§5の工程への対応

**提案:** packages/r2_m_engは既存の意味論・型付きAST・manifest/routeの実装資産として維持し、新規の **packages/r2_m_a/**（名称は提案）を**G3計測制御レイヤ**とする。科学実行エントリポイントを既存の --synthetic-affine fixture CLI に増設しない。安全な読み取り専用importで再利用可能なものを優先する。

| 新規責務（将来実装） | 再利用/境界 | 凍結手順への対応 |
|---|---|---|
| contracts.py | recordsのPublicObservation/PublicStep・SchemaFrame、固定manifestをread-only検証 | 事前登録・G5順序・閾値・arm固定、G2 digest照合 |
| public_pipeline.py | source_gatewayの合法Q001手続きを、公開3点→前commit→応答という評価側adapterから呼ぶ。decode_public/validate_public/sleep_lite/write_snapshotを再利用 | Q前commit、公開4点構築、独立validator、単一Snapshot作成・expected SHA固定 |
| orchestrator.py | runner.pyの1点fixtureは**呼ばず**、契約・工程のみ移植 | law×4点×7armの予定448スロット、各fresh processと別cwd |
| child_supervisor.py | dispatch/controlsの既存CLI・純粋APIをexact-headで呼ぶ。子にlaw真値/seed/scoreを渡さない | child spawn、5s資源制限、独立trace、失敗記録 |
| cost_accounting.py | meterのAST静的/実訪問/primitive計数を継承、親側process費用とphase別費用を追加 | CPU/wall/RSS、learn/restore/use、import、trace、保存・償却列 |
| evidence_ledger.py | snapshot.write_snapshot/dispatch.write_trace_onceのO_EXCL/fsyncを再利用し、イベント連鎖・remote commitを追加 | 前commit、出力digestの採点前commit、append-only原本、receipt |
| evaluator_gate.py | **評価側のみ**。真値比較を子から隔離、未承認時はデフォルト拒否。今回のG3文書では実行しない | 結果digestコミット確認後だけの照合（G6別GOが前提） |

**import/data境界:** evaluator専用のtruth source→public gateway→公開4点/型付きbody→Snapshot→child。child側の推移的import集合から source_gateway、evaluator_gate、truth/score handlingへの到達を禁止する。静的AST import graph、実行モジュール読み込み監視、CLI args/env/traceのdenylist・allowlistの三重検査を提案する。子には**唯一のcanonical絶対Snapshot path、その事前固定expected bytes SHA-256、arm、USE入力点、排他的trace path**だけを渡す。sourceやlaw id、真値、順序seedをchildコマンド/envに持ち込まない。子は単一のSnapshotを自分で復元し、共通policy/digestに照合する。law識別は親のcustody台帳だけが保持。

**工程状態機械（将来）:**
1. PR #181の確定G2 SHA/文書digestと実行対象exact-head・7arm manifest・資源閾値をread-only照合。**G5の順序manifest** をここで注入する場所だけ定義（**この計画では順序/seed/nonce生成なし**）。16件のスロットを予定表に登録。
2. 各lawの公開P3を提示。合法Q001・deadline・remaining budget=1・public history digest/問い合わせ001を確定し、**remoteで確認できるQ前commitが完了した後**にのみQを呼ぶ。commit不能時はQを実施せずSTOP。
3. 返却されたQ001を加えて公開4点から係数/ASTを構築。独立validator、意味保存Sleep-lite、Snapshot/v2を一回のみO_EXCL+fsyncで作成し、評価者側がexpected SHAを固定。生成物は不変。
4. G5の順序に従い、各lawでUSE4点×7armの **28 fresh child** を実行。各childは別cwd・一意なtrace名、起動から終了まで親側resource計測。スロットごとに一試行のみ。7arm間で公開4点・USE入力・Snapshot bytes・合法規約・上限を同等にする。
5. child exit/failure、実際の観測値（nullを含む）、legal_action、route/activity、費用ベクトル、stdout/stderrの安全なdigest、trace raw bytes SHAを**採点前**に記録。欠測・resource STOP・INVALIDを予定スロット上で明示。
6. すべての予定スロットの出力状態・欠測/INVALIDを含むmanifestをGitHub側に**採点前commit**。不一致・不完全ならG6評価gateは開かない（§8のSTOP/INVALIDに優先従属）。
7. 上記が完了し**別G6許可が存在する場合に限り**、評価側の真値照合と記述集計を行う。K_fullは全16適格時だけ算出。**本計画では実行・採点しない**。

**代替・不採用:** 既存1点runnerへ4重ループを追加するだけでは、timeout=30、evaluator/fixture依存、親側process費用・採点前custody欠落を解決しない。既存decoder/validator/dispatchを再実装すると意味論のドリフトを生む。両者を不採用。

## QG2 — 費用計測、hard capと会計列

**提案:** 指標の正本は**親の独立計測**、子のcost ledgerは**フェーズ内訳と相互照合**。OSが制御する資源と、学術的に報告する「process RSS」を同一視しない。CPU/OS/Python・kernel/cgroup/clock・依存/locale・CPU affinity/並行負荷・runner SHAをreceiptに残す。

| 指標 | 測定/単位 | 5s/512MBの制限と未測定時 |
|---|---|---|
| wall | 親のmonotonic_ns、spawn直前からreapまで秒換算。child内perf_counterは内訳 | 5秒の親watchdogでprocess group/cgroupをkill、超過はRESOURCE_STOP。子内の短い処理時間で起動費を隠さない |
| process CPU | Linux wait4(pid)で対象**個別child**の ru_utime+ru_stime（秒）、補助cgroup cpu.stat/子内time.process_time | RLIMIT_CPU=5sを二重ガードとし、親がCPU累積を監視。RLIMIT_CPUの信号粒度は厳密な5.000s保証ではない。最終実測>5sはRESOURCE_STOP・生値保存 |
| process peak RSS | 同じ個別childのwait4/rusage.ru_maxrss（Linux KiB→bytesで×1024）。子内RUSAGE_SELFは監査用突合 | cgroup v2 memory.maxで保守的な実行時抑止、memory.peak/memory.eventsは**別のgroupメモリ指標**として記録。process RSSと同一名で報告しない。未測定・不一致はUNMEASURED/STOP |
| 選択/計数 | decoder/validator **learn, restore, use別**の実call-siteカウンタ、候補生成実数/上限、H0 scan、公開比較、route、ABSTAIN、AST静的/実訪問/実primitive | call-siteテストで独立手計算照合。restore時の再decoder/validatorの片側非課金は禁止 |
| Bytes/準備 | Snapshot write/read、trace raw bytes、catalog保持のserialized bytes、process起動、preparation/import/serialize/restore/dispatch/verifyのCPU/wall | 単位・scope・発生時刻・算出根拠を保持。独立に測れない項目を0にしない |

**重要なLinux上の厳密性:** RLIMIT_RSSはLinuxでは強制手段として信用できず、RLIMIT_ASは仮想アドレス空間でありRSS上限ではない。cgroup v2 memory.maxはハードガードだがRSSではなくページキャッシュ等も含み、瞬間的超過を完全には排除しない。cpu.maxは周期的なCPU帯域制限であり「生涯5 CPU秒」そのものではない。**単にresource limitsを指定しただけで厳密制限を実証したと書かず、G4でkill/正確な計測/トレースの故障注入を監査する**。WSL2/Linux環境でcgroupの委譲・権限・wait4等が使用不能なら正式実行はfail-closedでブロックする（弱い方式へ黙ってフォールバックしない）。
- 外部技術根拠: [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)、[getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)、[getrlimit(2)](https://man7.org/linux/man-pages/man2/prlimit.2.html)。
- **512 MBのバイト解釈は本凍結には明記されていない。** 本提案はより厳しい暫定ガードとして 512,000,000 bytes（SI MB）を候補とし、G4前にMuse/Ownerが単位を監査確定する。512 MiB（536,870,912 bytes）への無断読み替えはしない。

**FIXED-MACROの二重計上防止:**
- 観測生値: actual fresh childに発生したmodule-import・全カタログ構築の費用は、どのarmで生じたかにかかわらず **per_fresh_process.actual_import_cpu_s / wall_s / bytes** に記録。現行controls.pyのimport副作用は**5対照全armに発生し得る交絡**として正直に公開する。固定カタログの16 entriesと保存bytesも別記。実測生値から恣意的に差し引かない。
- one_off_preparation: lawの公開3点を渡す**前**のsource-independent全16カタログ準備について、別の **one_off_preparation.actual_cpu_s/wall_s/bytes** 列を設ける。G3仕様が実際に事前構築した費用だけを記入し、実際には準備していなければUNMEASUREDとする。前払いとfresh importを混同/二重加算しない。「共有キャッシュ再利用」は実装が証明されない限り計算上の反実仮想であり、追加の実測や改造は行わない。
- accounting rowには **charge_scope = per_fresh_process / one_off_preparation / per_law / per_use**、**observed_or_projected**、**phase**、**arm**、**law**、**child_slot**、**metric_unit**、**value_or_UNMEASURED**、**causal_origin**、**included_in_process_total**、**allocation_rule_version**、**raw_receipt_sha256**を必須化。親の全process実測と子の部分費用を足して二重計上しない（部分費用は内訳）。
- 現行モジュールの不要なmacro importを科学用armだけで回避する最適化は、観測対象の配線/費用を変える。**自動採用しない**。Museへ独立質問として提示し、変更するならG4前・exact-headで対照不変性と同予算を再査読する。

**投影:** n={1,4,16,64}は**4点巡回・同頻度の記述的再利用モデル**であり、追加のfresh child実測を意味しない。実測448 childと投影の表を分離し、準備/起動/restoreの分解が十分でなければC_life,d(n)=UNMEASURED。RSS peakは和にせずmax/分布。異種単位の重み付けや優位性の統計主張をしない。

**代替・不採用:** 子自己申告だけ（起動費・異常終了時に欠測）、/proc定期ポーリングだけ（短いRSS spike見逃し）、RLIMIT_AS=RSS（次元誤認）、cpu.maxだけ=5s CPU累積制限（意味が異なる）は正本方式として不採用。

## QG3 — precommit、digest、append-only原本とreceipt

**提案:** 各runは一意の専用root（存在したら拒否）に、read-only config、G5順序manifest参照、予定スロット448件、event journalとraw artifactを置く。実際のG5順序データはここでは**作成しない**。local O_CREAT|O_EXCL、権限制限、ファイルfsync＋親ディレクトリfsync、同一FSでの原子的手順、イベントの単調seq/prev_sha256/entry_sha256で書き換え・穴・順序異常を検出する。JSON（canonical UTF-8、sort_keys、NaN禁止）/JSONLとraw bytes SHA256を併存させる。append-onlyはOSの絶対不可変性を意味しないため監査検出と権限分離を併用する。

**二つの不可逆境界（将来のG6のみ）:**
1. Q001回答を見る**前**: public P3 digest、合法actions=(001)、paid budget=1、期限、event_seq、Q001入力、method/policy SHAを含む precommit record をlocalに排他確定し、**GitHub audit branchへのcommit/pushがリモートで確認された後にのみ**ゲートウェイのanswerを許可。remote保全失敗・重複Q・期限切れでは回答取得を試みずSTOP/INVALIDへ。1 lawにつきQは一回。
2. 真値照合の**前**: 全スロットについて child_start/exit、trace bytes SHA・失敗/欠測、resource STOP、追加なし（各child一回）、raw manifest root hashをGitHubにcommit/push確認。そのdigestのみをevaluator_gateに引き渡す。後付けtrace補完・欠測削除・同じslotの再計測を禁止。

**推奨保存構造（名称のみ。G3では実ファイルを生成しない）:**
~~~text
run-<id>/                           # 将来のG6でのみ生成
  prereg-lock.json                  # 凍結原本SHA、method/control/runner SHA
  order-manifest-reference.json     # G5での確定物を参照（現時点TBD）
  environment.json                  # CPU/OS/kernel/Python, cgroup, clock, affine/load
  expected-slots.json               # 16×4×7の全448予定slot（実行順は未設定）
  journal/events.jsonl              # prev-hash連鎖、事前/終了/失敗/commitイベント
  public/<law>/q-precommit.json     # Q前固定、history/allowed digest
  public/<law>/q-answer.json        # Q後の公開証拠
  snapshots/<law>/snapshot.json     # 単一不変Snapshot/v2
  traces/<slot>/attempt-1.json      # 成功trace、再試行禁止
  failures/<slot>/exit.json         # 起動失敗/kill/欠測の生証拠
  receipts/pre-score-manifest.json  # 全結果の採点前digest/欠測commit
  receipts/score.json              # G6の別許可・採点前固定成功時のみ
  receipts/custody-git.json        # remote commit SHA/URL、外部registry=NONE
~~~
※角括弧のlaw/slotは親側custody内の識別子で、子へ法則係数を渡すことを意味しない。フォルダの実パス、READMEリンクとmethod lockを決定論的に記録する。public/score領域はロールとプロセスを分ける。個別失敗は**実行しなかったことも含め**原本から削らない。途中STOPなら残りのslotはNOT_RUNであり448回実行したと偽らない。

**比較/採用しない案:** SQLiteの後からUPDATE可能な単一台帳だけ、rawを保存しないdigestだけ、childが自分の成果を自己採点する設計、G6後のGitHub一括pushだけは、precommit/採点前固定と独立照合を満たさない。GitHub自体の管理者による履歴変更や外部timestamp欠如は**残余リスク**としてreceiptに必ず記す（凍結どおり外部registryなし）。

## QG4 — テスト戦略、INVALID負例、fixtureとの隔離

**提案:** 実装PR内の自動試験は、既知の人工law/架空時刻/偽のOS resource読み取りのみ。**448本測定をテストで自動起動しない**。既存tests/test_r2_m_eng_*.pyを回帰基準とし、将来 tests/test_r2_m_a_{contracts,boundary,meter,custody,orchestration}.py を追加する計画。実装前の現時点で新しいテストPASSとは書かない。

| 観点 | 正常系の受入 | 必須負例（fail-closed） |
|---|---|---|
| full-design counting | 集合16×4×7=448の予定スロット、一意性、1law28 | law/arm/point欠落・二重登録・黙殺→INVALID、K_full=NOT_EVALUATED |
| Q001 chronology | 3公開→precommit→001回答、各law一度、全16Q | Q前commitなし・合法digest変造・Q二度・期限切れ→INVALID/UNIDENTIFIABLE |
| public/private boundary | child args/env/Snapshot/traceにtruth不在、eval側だけが正答 | source_gatewayの推移的import、law bits/seed/true USE labelの混入→INVALID |
| snapshot/route | identical bytes/path/SHA、別cwd、F00全fallback＋F10 body、restore再decoder同課金 | 改ざん+digest再計算、expected SHA mismatch、片側decoder削除→INVALID |
| controls | 5つの独立arm、tie/容量、同public4/USE/計数規約 | macro target単独注入、1NN first-tie、STUMP 16候補の混同、F01/F11/ORACLE起動→INVALID |
| resources | wall/CPU/RSSの個別単位・peak・起動費、終了コード/シグナル/制限イベント | 5秒wall超/5秒CPU超/512MB超、計測不可能、cgroup無権限、子の異常終了/取り逃し→STOP、隠蔽はINVALID |
| custody | O_EXCL/fsync、prev-hash連鎖、GitHub確認→次段階 | trace上書き、pre-score commit前にtruth照合、journalの削除/順序飛び、remote失敗を無視→INVALID/STOP |
| one-shot | 各slot一回、失敗もraw記録 | 同一slotの自動リトライ、欠測を成功0件とみなす、完了数を448と偽装→INVALID |
| score rule | 16法則全適格の時のみKを計算し、K>0は監査停止 | 一部欠測でK=0宣言、経路だけの差でD_use陽性認定、NULLをM_use認定に昇格→INVALID |

**さらに必要な独立検査:** kill競争（wall/cpu/RSS閾値付近）、瞬間的RSS spike、child stdout破損、異常exit、親の中断後のjournal再生、同時起動拒否、remote push喪失、process descendants混入、process vs cgroup peak不一致、非UTF-8/NaN、原本改ざんの負例。故障時もrawが消えないことを監査する。負例は人為的に失敗させる**テスト**であって研究上の実験結果ではない。

**環境分離:** fixtureには既存の --synthetic-affine と専用一時ディレクトリ、固定の明示的 engineering_only=true、scientific_scoring=NOT_AUTHORIZEDを使う。科学用runnerは実行時にG2/G4/G5/G6署名・正確なdigest lockの存在を検証し、未承認では起動しない。docs-only本PRではfixtureすら実行しない。

## QG5 — G4実経路監査 dossier（作成計画）

**提出物はコード実装後にexact-headで採取するread-only dossier。現在は未作成・未監査。**
1. **source-lock.md/json**: 実行対象runner **40桁commit SHA**、全tree hash、変更ファイル、凍結文書bytes SHA、method/policy/control/closure manifest digests、Python/OS環境。G4開始後の変更は新しいexact-head監査へ戻る。
2. **import-graph.md/json**: 対象commitの静的+実行時importグラフ（入口ごと）、child→evaluator/source/score禁止到達の証拠、実際のCLI/env allowlistと非漏洩テスト。
3. **routes.md/json**: F00/F10全実接続routeの選択優先、全fallbackのreachable test、復元時decode/validatorの呼出、有効化/選択/実行/終了状態、5対照をfallbackへ混ぜていない証拠。
4. **arms-and-budget.md/json**: 7arm同一Snapshot/公開4点/4 USE、候補実生成と上限、STUMP14別族、exact8、tie、上限、static nodes、F01/F11/ORACLE不活性。
5. **cost-audit.md/json**: process wall/CPU/RSSとkillの故障注入、512MB単位解釈、import-catalogのper_fresh_process vs one_off_preparation、学習/restore/use別call-siteと総費用照合。
6. **custody-audit.md/json**: Q前commitの時系列、全slot結果の採点前digest GitHub確定、append-only+hash chain、GitHubのみの限界、失敗/INVALIDの欠測不隠蔽。
7. **negative-tests.md**: 通常・敵対的fixtureのテスト名、結果/失敗ログ、チェックを実施したexact-head、独立レビュー署名欄。
8. **g4-decision-template.md**: MuseのPASS/STOP/要変更、Owner判断欄、未解消P0、closure UNKNOWN・主張上限・G5/G6独立GOを明記。

**固定方法:** 全G3コードPR統合後に候補main SHAをピン留めし、そこから再現可能な読み取り専用監査を行う。G4自身がmainに変更を入れない。G4完了後のコード更新は対象SHA不一致として**RUN BLOCK→再G4**。単なるCI successや過去のStage3工学合格で代替しない。H0_effective(B)=COMPLETEの証明ではなく、**現在の全実配線監査**に留める。

## QG6 — 作業分割・段階PR・受入と見積もり

**提案:** 既存R2-M-ENG段階1〜3を踏襲。ただし各PRはG3 Owner許可後の**新規main基点・小さなコードPR**とし、古いPRの積み上げ/学習データ変更をしない。各段階でowner merge許可と独立exact-headレビューを受け、次段階への権限は別途判断。

| 段階（すべて未許可） | 将来PR内容 | 受入条件 |
|---|---|---|
| G3-1：contract/分離 | 新packages/r2_m_aの型、公開→Q前commit→独立validator→Snapshot準備の境界、予定448 slot、G5順序manifest挿入口、禁止import | 16-law人工fixtureで合法Q001/公開4点・Snapshot不変・真値非混入、負例、ARCH-001/002同期 |
| G3-2：fresh child/費用 | 4点×7arm起動監督、wall/CPU/RSSの個別計測とhard cap、learn/restore/use breakdown、fixed macro会計、失敗STOP | OS上の強制/測定・kill注入と公平性、単回/再試行なし、現行dispatchの意味論不変、外部source不使用 |
| G3-3：custody/監査材料 | append-only events、Q前/採点前remote digest固定、pre-score gate、欠測可視化、G4 dossier生成器、全負例 | 上書き拒否/時系列不変/全448予定枠、score gate未承認時拒否、チェックとexact-head独立確認 |

概算（**見積もり・GOではない**）: 追加コードは合計600〜1,100 LOC、テスト500〜900 LOC、仕様/ARCH/INDEX/人工fixture記録の同期。大部分の資産は既存のr2_m_engから再利用する。cgroup権限/信頼境界/remote custodyは見積もり不確実性が高く、承認前に規模を確約しない。

**非対象:** 448本の測定、law順序/seed/nonce固定、真値の正式採点/解釈、C_lifeの未監査宣言、外部registry、Bの方法改訂、F01/F11、ORACLE子、旧holdout/sealed再実行、新しい学習器、能力/転移認定。G4・G5・G6は各別Owner決定。

## 7. Museへの独立逆質問（QG-RQ1〜RQ3）と暫定判断

**QG-RQ1 — 512 MBの単位とRSS/cgroupの契約:** 凍結された512 MBを**512,000,000 bytes**としてG4実装仕様に確定し、個別child wait4 peak RSSを報告値、cgroup memory.maxを保守的hard guardとする提案に同意できるか。それとも512 MiB等を想定するか。**暫定:** 厳しいSI値で準備、単位・計測方式のG4確認までG6 BLOCK。method上限を変更する提案ではない。

**QG-RQ2 — CPU hard capの実効性と環境:** RLIMIT_CPUの秒粒度を明示したうえで、親がCPU累積を監視・killし、終了時wait4実測が5秒を超えた場合RESOURCE_STOPとする案は、凍結した「hard cap」の実装として受容可能か。cgroup delegate権限がないLinux/WSL2で、統計だけを取って採点する運用は**不可**とするのに同意できるか。**暫定:** fail-closed、G4で実効性を実測してからG6判断。

**QG-RQ3 — FIXED-MACRO現行importの交絡:** 既存controls.pyの全arm import時カタログ構築を、まず**全armの観測生値**として正直に残し、one-offモデルを独立・未観測はUNMEASUREDとする案で十分か。比較公平性のためmacro以外のarmでimport副作用を避ける**実装時の局所refactor**を望むか。後者の場合は**同一control/route/コスト規約とsource前16件構築の同等性を事前に独立査読**しなければ導入しない。**暫定:** 凍結済みmethodと既存意味論を優先し、結果後補正しない。

各回答には **結論／根拠／認める反例・STOP条件／Owner決定が必要な範囲**を明示していただきたい。柔軟な代案は歓迎するが、凍結済みmethodの変更と混同しない。

## 8. 逸脱候補と停止基準

**現時点で凍結本文の変更を要求する提案はない。** 以下は**必要になった場合に限る新版が必要な逸脱候補**であり、現G3で実施しない:
- 512 MB/5秒の閾値変更、単回/リトライなしの変更、448 childの増減、別の法則やUSE点を追加する変更。
- F00の合法fallback（とりわけruntime_affine_decoder）を削除・弱体化、F00/F10に非対称な計数・情報・容量制限を課す変更。
- G5で順序固定前に法則順序を確定、結果を見て順序/threshold/配賦を変更すること。
- 追加実測でn=16,64を「fresh repeatした」ことにする変更、外部registry導入、B科学研究への連結、F01/F11起動、M_use/M_gap認定。
- G4監査後の実行対象コード変更のままG6へ進むこと（少なくとも新exact-head監査を要する）。

**STOPを優先する条件:** 凍結SHA不一致、G3/G4/G5/G6の承認不足、公開・評価側の情報逆流、Q前commit欠落、保管書込障害、OS capの実効強制不可能、cost不測をゼロ処理、expected SHA mismatch、fallback消失、全予定slotの不当な欠落、評価前digest commit失敗、K>0未説明。これらを「0件の失敗」へ修正して継続しない。

## 9. 合意形成ゲート（今回の依頼の出口）

- **検証済み根拠:** PR #181凍結receipt、[質問票 PR #182](https://github.com/ryonakayama234/DekaSugi/pull/182)、[Stage2](../specs/R2-M-ENG-STAGE2.md)/[Stage3](../specs/R2-M-ENG-STAGE3.md)、mainのrunner.py/controls.py/dispatch.py/meter.py/関連テスト（参照時main=cf84409）。
- **不確実性:** 資源hard capの実効保証、512 MBのバイト規約、FIXED-MACRO起動交絡とC_lifeの割当、GitHub-only保全の外部時刻証明なし。いずれもG6前に監査し、根拠不足はUNMEASURED/STOPとする。
- **提案決定:** MuseによるQG1〜QG6およびQG-RQ1〜RQ3の独立method・security査読を先行。**合意=査読合格+Owner明示G3実装GO**であり、提出やCI合格だけでは成立しない。
- **次の最小行動:** Muse査読のコメント（PASS/FIX/STOPと根拠）、OwnerのG3計画採否・実装許可可否。承認まではG3コードPR作成・実行は停止。

<!-- 本書に実測の正解率・K・費用中央値・CPU/RSS実測値・監査合格は存在しない。 -->
