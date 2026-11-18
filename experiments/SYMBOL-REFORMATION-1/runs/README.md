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
