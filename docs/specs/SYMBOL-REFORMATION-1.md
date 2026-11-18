# SYMBOL-REFORMATION-1 — 終了辞書による再形成

id: SYMBOL-REFORMATION-1-SPEC
status: implemented_independent_review_pending
updated: 2026-11-18
tags: training, candidate, engineering

[実行前固定](../../experiments/SYMBOL-REFORMATION-1/plan.md)が方法・数値・順序の正本。[Owner GO](https://github.com/ryonakayama234/DekaSugi/issues/227#issuecomment-6969285381)。旧 `symbol_bootstrap` 本体・予測順位・旧runは変更しない。

## 入出力と責務

`packages.symbol_reformation.load_input(budget)` はSHAを固定した旧archiveのstates.jsonだけを読み、FULL/NO-CHUNKを返す。旧試験台帳・report・history・旧lockを読まない。`diagnose(states, budget)` は各153ペアを一巡し、旧文法の `_pattern/_outputs/_fit` を利用する。`observe/predict` は呼ばない。入力状態は前後digest一致を要求。辞書copyは固定し、新candidateを別表に保持。旧規則のcreated_at/evidenceを更新しない。

|ファイル|契約|
|---|---|
|diagnostic.json|18生文字列と最初のepisode、両方式のbefore/after ID集合、全ASTとcandidate状態・18行の判定、形成イベント参照、方式別集計、前後digest|
|trials.json|不成立pattern・出力0も含む全試行。arm/pair/split/routeと生成イベント参照|
|events.json|全AST出現の再形成来歴。AFTER-E054、既存再発見・再形成内重複、変数位置、chunk ID/展開/獲得episode/位置|
|report.json / result.md|方式別の前後差、chunk固有の新規/支持候補、反例/不適用、source/runtime/input/plan SHA。新規0件も記録|
|cost.json|全体/方式別の論理操作、CPU/wall、保存byte。自己参照を避け最終化直前の値と明示|
|SHA256SUMS.json / COMPLETE.json|各payload hash、manifest hash、最終操作費用（最終小票分4096操作を先計上）、保存読戻し済みの完了小票|
|STOP.json|RESOURCE_STOPまたはINVALID。完了マーカーなし、summary/結論の小票を除去。残存raw部分記録は完了扱い禁止|

全生成ファイルの非圧縮サイズが成果物上限。停止小票に16KBを予約。支持cacheは各方式4096×18、trial数は各方式16384、出現イベントは両方式65536を上限とする。全体20M論理操作はCPU命令数ではなく固定した計算法。JSON値/key/string文字も計数し、入力検査・集計・保存・読戻しを除外しない。最終小票は最大4096byte/操作を予約し、実測CPU/wall checkを保存後まで行う。POSIX SIGALRM/ITIMER_PROFが同期処理中の時間停止も担う。非POSIX環境ではCLIを使わずMuseのLinux VMで確認する。

## 判定の射程

canonical AST = pattern/outputの文字展開構文。意味論的に同じ別構文を同一化した主張ではない。FULL新規でも、両方式の前集合、NO-CHUNK後集合、FULL文字形成のいずれかにあればchunk固有に数えない。候補ごとの支持/failure/inapplicableは18行上の照合であり、普遍的な適用範囲ではない。全既存候補にも同じ判定をつけ前後で分母を共有する。既存AST再発見イベントと再形成内重複イベントは重なり得る。

結果後に文法・分割・順序・上限・入力を変えない。訓練適合の新規候補は能力認定ではない。新予測評価・E1統合・モデル採用・mainマージは範囲外。提出後のMuse独立確認は別ゲート。
