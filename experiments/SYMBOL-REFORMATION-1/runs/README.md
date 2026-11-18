# SYMBOL-REFORMATION-1 runs / Muse handoff

id: SYMBOL-REFORMATION-1-RUNS
status: implementation_prepared_diagnostic_not_run
updated: 2026-11-18
tags: training, engineering, handoff

[先行固定](../plan.md) / [仕様](../../../docs/specs/SYMBOL-REFORMATION-1.md)。固定commit `e5c4f5247de55b6d689edb6200d794f657cf0d43` は実装・人工確認より前にGitHubへ保存。診断本体は未実行。

## Muse VM独立確認

1. 提出の最終headをcheckout、head/Python/OSを記録。旧学習器の再実行・旧試験の再評価をせず、専用 `python -m unittest discover -s tests -p test_symbol_reformation.py -v` のみを実行する。
2. 固定plan SHA `0a5d3bb4f3e43f474c6d293ce2c11e8e91dbc949b855a4f87f991922c07f75a8`、旧archive/state SHAをplanと照合。CLIはstates.jsonだけを読む。
3. `python -m packages.symbol_reformation --output /tmp/symbol-reformation-muse-01` （存在しない新しい出力先）。両方式を含む単一runで固定上限。RESOURCE_STOP/INVALIDなら延長・剪定せず停止し、STOP.jsonを報告する。
4. COMPLETE.json、manifestと全payload hash、保存読戻し、全ファイルbyte合計を確認。diagnostic/trials/eventsの内容は提出runと一致を要求し、reportのsource/runtimeとCPU/wallだけを同一bytes比較から除く。操作カウンタも照合する。
5. ペア153×2、split昇順、FULL symbol→character、NO-CHUNK characterのみ、全不成立/出力0試行を独立確認。旧stateの前後digestと原本不変、支持18行・反例・不適用・形成元/変数位置・chunk獲得時点/位置を検算する。
6. 主問いの差集合を独立再計算。同じASTが文字側でも得られたらchunk固有としない。新規0件でもそのまま結果として閉じる。Handoffにhead・環境・成否・digest・前後差・支持/反例・費用を残す。

これは制作物と訓練側候補形成の独立確認で、モデル採用・未見利益・E1完了・mainマージのGOではない。

## local-01 結果と作者検算

[結果票](local-01/result.md) / [全8ファイル証跡](local-01/evidence.zip)。固定後の実行sourceは `6f0084906ea167b7362bab143f6f3555cefc9fb2`。旧本体・旧run・固定計画は不変。これが唯一の診断コーパス実行であり、条件を変えた再試行は行っていない。

|方式|前AST|後AST|新規|chunk固有の新規|行ペア|形成試行|
|---|---:|---:|---:|---:|---:|---:|
|FULL|184|184|0|0|153|4284|
|NO-CHUNK|180|180|0|対象外|153|2142|

各方式の既存AST再発見イベント334件、再形成内重複154件（両者は重なる）。FULL symbol経路は2142試行中637件でpattern成立したが、suffixに合う出力ASTは全637件で0件。FULL文字経路とNO-CHUNKはpattern成立1480件、うち1146件は出力0、出力出現334件。この内訳は保存済みtrials/eventsの読み取り集計であり、新たな再形成実行ではない。

**終了辞書による今回の再訪でも候補集合は増えなかった。** chunk固有の新規支持候補も0件。これはこの固定文法・最長一致分割・18行・一巡の所見で、再形成一般の無効や原因の一意性を示さない。旧負の結論を維持する。成功するまで分割・順序・上限を変えず、この診断を閉じる。候補の採用や新予測評価には進まない。

- CPython 3.12.14 / Linux、全操作3,402,900（最終小票予約4096込み）、CPU約1.33秒／wall約1.41秒。全8ファイル計1,484,747byte、上限内。正本はZIP内cost.jsonとCOMPLETE.json。パッケージ化ZIPは配送用で、診断runの非圧縮8ファイルをそのまま保持する。
- 364 AST × 18行 = 6552判定、6426試行、668形成イベントを、学習器をimportしない `scripts/audit_symbol_reformation.py` で再計算・PASS。全試行のpatternと全出力列挙を別実装で照合、独立した長さ積の照合でsupport/failure/inapplicableを検算。これは作者の別計算法検算でありMuse独立受入ではない。
- 専用12テストPASS。人工入力の一巡/重複/0件・状態不変・支持unique18・反例/不適用・chunk位置/依存、操作/保持/保存停止、入力不整合、完了小票欠損、hashを再計算した試行/支持/依存/summary改変の拒否を含む。初回は人工fixtureの共通suffixから1候補が生じることをテスト期待が見落として1件FAIL。期待を訂正し、出力0件の別人工検査を追加した。診断コーパス実行前に修正済みで、文法・上限・順序は変更していない。
- docs-check、git diff --check、CI-SAFE-V2歴史ソース14/9件の照合PASS。専用テストは既存CI allowlistへ追加していない。既存研究の実行・旧予測評価はしていない。GitHub CIはPR上で別確認、Muse受入は未実施。

## 提出証跡の展開と監査（上記手順3の前に実施）

`python -m zipfile -e experiments/SYMBOL-REFORMATION-1/runs/local-01/evidence.zip /tmp/symbol-reformation-submitted-01` （新しい展開先）。

`python scripts/audit_symbol_reformation.py /tmp/symbol-reformation-submitted-01`。その後、手順3のVM実行と同じauditorをVM出力にも適用する。提出runとVM runのdiagnostic.json / trials.json / events.jsonはbytes一致、operation内訳一致を確認する。report/resultには実行source/runtime、cost/completionには時間値等があるためそこは実測として区別する。最終headは検算器・結果保存を追加するが、実行した診断器のsourceは上記commitのまま変更していない。
