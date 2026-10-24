# EXP-0001 runs

id: EXP-0001-RUNS
status: completed
updated: 2026-10-24
tags: experiment, runs, provenance

初回の事前登録機能検証を実行し、PASSを記録した。ただし概念学習はまだ実装していない。

- [RUN-001 — 結果と採用判定](20261024-0423-9cfb4c1.md)
- [RUN-001 — machine-readable JSON](20261024-0423-9cfb4c1.json)

実行ごとに別ファイルを作成する（例: `20261024-1200-abcdef0.md`）。
必須情報: 実際のcommit SHA、実行日時、環境、コマンド、入力データ版、実測値、期待と異なる挙動、採否。
出力を後から訂正する場合は元ファイルに注記し、必要なら新runとして再実行する。

[事前登録計画](../plan.md) / [共通テンプレート](../../../docs/templates/experiment.md)。
