# SYMBOL-BOOTSTRAP-1 runs / Muse handoff

id: SYMBOL-BOOTSTRAP-1-RUNS
status: local_engineering_checked_muse_pending
updated: 2026-11-17
tags: artificial, engineering, evidence, handoff

[実行前固定](../plan.md) / [仕様](../../../docs/specs/SYMBOL-BOOTSTRAP-1.md) / [lock](../lock.json)。制作はOwner GO（Issue #227 コメント6949870568）の範囲。一つのDraft PR、マージは別判断。

## 結果

|分類|分母|FULL|NO-LEARN|NO-CHUNK|MEMORY|
|---|---:|---:|---:|---:|---:|
|a: 見た反復|4|4|0|4|4|
|b1: 未見の順序付き組合せ|4|4|0|4|0|
|b2: 未見の文脈pairing|2|2|0|2|0|
|b: b1+b2|6|6|0|6|0|
|c: 内容語彙が完全未見|4|4|0|4|0|

**未見予測はできたが、自作したまとまりの寄与は未確認。** b全6件のFULL選択は文字経路で形成された `R-4d7c92c5afe3d05a` / `R-d098d82e5d2aa500`。各束縛・元episode・文字位置はreportとstatesで追跡できる。

FULLはchunk 320、規則184（文字180／symbol4）。NO-CHUNKは規則180。symbol由来4規則には実際の形成依存があるが、bの7文字予測では選ばれなかった。chunkを使った新候補の形成経路はあるが、この比較で予測の改善には寄与していない。cの成功も未知語の意味理解ではなく、与えた汎用コピー文法の適用による。

## 保存した実行

- [local-01結果票](local-01/result.md) / [初回の全証跡ZIP](local-01/evidence.zip)：最初の人工確認。事前予測のNO-LEARN行が未収録だった（162行）。最終56件の比較は完了。原本を変更・除外せず保持。
- [local-02結果票](local-02/result.md) / [提出対象の全証跡ZIP](local-02/evidence.zip)：欠損/重複集計の拒否とNO-LEARN事前予測の記録を補い、同じ固定条件で再照合。216事前予測。全56件の予測・trace・最終状態digest・分類別得点は初回と完全一致。学習器本体、例、上限、選択順は不変。
- local-02はPython 3.12.14、CPU/wall約1.24秒、操作314,746。FULL形成試行4,284、NO-CHUNK2,142、どちらも上限未達。実測値の正本はZIP内のcost.json。時間を再現性の同一条件と扱わない。
- [source-history.bundle](source-history.bundle) は人工確認前の元ローカルcommitを含む4commitのGit bundle。GitHub転送では同一treeを維持して別commit IDとなったため、下記の対応と併用する。ローカルで先行commitを固定した事実と、後のGitHub公開時刻を混同しない。

|役割|元ローカルcommit|GitHub同一treeのcommit|
|---|---|---|
|実行前固定|acac7c132ab59bcae88d097a94e976a1ba23b88d|5d755f8cd3c204c455f8718fa95a2b52d4f66989|
|初回実行の実装|d8ae29bf23196724a0548706a8f5c28f9f362fbf|9623e5c6b2a5bb14db76e8fb457ac068e58f3328|
|提出実行のコード|2abbdc374461fc54fc7e2688d337810bec43b1fb|ab77a851347a90fce870f0149952458e663b17ff|

local-02はGitHubの固定commit公開後、`ab77a851347a90fce870f0149952458e663b17ff`上で実行。初回の後に比較表の欠損拒否、NO-LEARN履歴追加、テスト配置のIndentationError修正のみを行った。失敗したテスト収集も隠さず記録する。学習・予測アルゴリズムを結果に合わせて調整していない。

## MuseのVM独立確認

1. このDraft PRの最終headをcheckoutし、commitと `lock.json` SHA256 `cc9c4f5275a6d9e6af972caa98eb2d8a24464dc1ee8395d73fd128ca446a4457`、`plan.md` SHA256 `54b21502668d7b45a6663e7d1ee2a71a64d73ea4c2dbbc0d44875888e0732242` を記録。
2. `python -m unittest discover -s tests -p test_symbol_bootstrap.py -v` を実行。全研究testの無差別discoverはしない。
3. `python -m zipfile -e experiments/SYMBOL-BOOTSTRAP-1/runs/local-02/evidence.zip /tmp/symbol-submitted`。既存の展開先があれば別の新規pathを使う。
4. `python scripts/audit_symbol_bootstrap.py /tmp/symbol-submitted`。学習器をimportせず56件を再予測し、364規則の支持/反例・形成元・文字位置・chunk依存の時系列を照合。これは別計算法による同じ担当の自己検算済みであり、Museの独立確認済みという意味ではない。
5. `python -m packages.symbol_bootstrap --output /tmp/symbol-muse-01`。CLIの条件は固定で、RESOURCE_STOPなら延長せず停止。試験prefix・期待は学習入力に加えない。
6. 新しいrunにもauditorを実行。reportの `rows`, `summary`, `interpretation`, `ledger` と `states.json`, `history.json` は提出runと一致すること。reportのsource_commit/runtime、costのCPU/wallはVMで変わるため同一bytesを要求しない。arm別操作カウンタは一致を確認。
7. Handoffでhead、環境、実行成否、digest照合、分類別得点、全bの選択規則と依存、負の結論を報告。独立確認は制作物の確認で、モデル採用・E1完了・mainマージのGOではない。

初回の証跡は旧形式なのでauditorの216件条件には合わない。local-02を監査対象とする。負例として、予測、依存、summaryを改変しファイルhashも計算し直しても、自己検算のauditorは全て拒否した。一般的な不正検出を保証するものではない。

## 提出前の確認記録

専用11テストPASS（反例によるconfidence低下、試験状態不変、NO-CHUNK別学習、記憶/空対照、欠損/重複拒否、操作/保存上限のRESOURCE_STOP、再署名した改変記録の拒否）。別計算法auditorは56予測・364規則とchunk320件の来歴をPASS。docs-checkは126 Markdown PASS、既存CI-SAFE-V2の14/9歴史ソース照合PASS。既存safe allowlistの118テストもPASS。専用11件は既存CIへ追加していない。git diff --check PASS。これらは作者の工学確認であり、Museの独立受入ではない。
