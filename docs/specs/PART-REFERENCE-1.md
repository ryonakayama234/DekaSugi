# PART-REFERENCE-1 — 参照を保持する最小人工試験

id: PART-REFERENCE-1-SPEC
status: implemented_review_pending
updated: 2026-11-18
tags: synthetic, reference, candidate

[先行固定](../../experiments/PART-REFERENCE-1/plan.md)と同commitの3 JSONが正本。`packages.part_reference` はファイル入出力・正解・旧学習器への依存を持たず、`acquire(rows)` と `predict(chunks, query, arm, acquisition_cost)` を公開する。前者が学習例2行の一意な本文除去から有向残差を形成、後者が選択子に対応する候補を列挙する。合成の型は与えた事前知識。

| 記録 | 契約 |
|---|---|
| predictions.json | 全3方式の獲得状態、16行×全候補の本体・展開形・格納長・展開長・充足数・上限適格性、選択枠、実使用参照、出力、論理費用、CPU/wall、freeze/source/input SHA |
| PREDICTIONS-LOCK.json | 全予測保存・fsync・hash読戻し後のファイルSHA |
| report.json | 別採点プロセスによる完全一致集計、paired差、機構照合、全候補の独立再計算、計数、独立VM確認pending |
| predict-cost.json / score-cost.json | プロセス開始からpayload保存読戻しまでのCPU/wall、各costファイル保存直前の全payload byte。cost小票自体・COMPLETE保存の所要時間は外部timeで追加計測 |
| COMPLETE.json | 上記5ファイル全てのraw SHA目録。目録保存後の外部検算が完了証拠。ディレクトリの総byteは目録を含め別集計 |

実行は `python scripts/run_part_reference.py predict OUT` の終了後、別起動の `... score OUT`。OUTは新規のみ、各ファイルは排他的作成。予測側はtrain/queries/planだけを固定commitとbyte照合して読む。採点側は予測lockを確認後に初めてanswersを読む。途中失敗は例外終了しCOMPLETEを持たない部分記録となり、完了率を報告しない。追加の時間枠は設定せず固定有限人工処理の費用を測る。

`python scripts/audit_part_reference.py OUT` は学習器・runnerをimportせず、独立した表と二重ループで全候補、順位、参照展開・実行、正解、費用、reportを再計算する。固定commitの入力bytesと実行sourceのコードbytesも照合する。同じ作者による別計算であり、Museの独立確認は提出後に行う。保存hashは外部による時系列認証を保証しない。

主8件でREF 8、CHAR/MASK 0、片側対照全方式8が判定線。REF主正答の全件で左右参照の実使用が必要。工程不整合・想定外の対照正答はINVALIDで止まり、REF未達はNOT_MET。結果の射程は、与えた合成型と格納制約における参照付き表現の寄与。
