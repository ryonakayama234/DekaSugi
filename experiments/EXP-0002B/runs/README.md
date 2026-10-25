# EXP-0002B — Runs index

id: EXP-0002B-RUNS
status: FINAL112 numeric gates PASS; independently reaggregated; not promoted
updated: 2026-10-25
tags: exp0002b, runs, measurement, preregistration

EXP-0002B has a reproducible TRAIN-only learned Kernel and a separate [DEV48 engineering run](20261025-dev-smoke.md). **FINAL112 was evaluated once and independently reaggregated; all five numeric gates passed, but no scientific skill promotion or total-CPU benefit is claimed.** MEASURE-0001 uses the already published EXP-0002 examples for instrument diagnostics and unit regression, never a new confirmatory holdout.

- [MEASURE-0001 integration and verification record](../metering-log.md).
- [MEASURE-0001 architectural measurement contract](../../../docs/architecture/measurement.md).
- [Experiment design Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7).
- [Current protocol v2](../plan-v2.md) — integrated before implementation; no FINAL outcome.

## 事前登録v2統合状態
- [v2の正本](../plan-v2.md)は評価・学習実行前に固定。旧[v1](../plan.md)は旧seedと閾値の問題から評価には使わない。
- この節は事前登録v2統合当時の経緯である。現在はGenerator・TRAIN観測を実行済み、DEV工学的検査も実施済み。FINAL112問の学習比較は**未実施**。MEASURE-0001以前の公開holdoutは新規評価に流用しない。

## EXP-0002B TRAIN-only evidence（CI上の診断）
- `python -m packages.kernel --mode preflight` は全splitのデータ内容hash・seed一意性だけを記録。
- `python -m packages.kernel --mode train` はTRAIN144課題のpaired実測・ハッシュ付きPolicySnapshotを生成。Github Actions artifact名`EXP-0002B-train-only`に保存する（実装PRのCI実行後）。
- **DEV smokeとFINAL112問の技能選択・検索・採否結果は含まない。** [TRAIN-only実装監査](../reviews/20261025-train-only-kernel.md)。

## TRAIN政策の凍結 (2026-10-25)
- **TRAIN-onlyの2回のCI再実行でsnapshot SHA一致**。[freeze-v2](../freeze-v2.md) / [JSON](../freeze-v2.json)。
- 元のCI evidenceは[main run #40154262757](https://github.com/ryonakayama234/DekaSugi/actions/runs/40154262757)の`EXP-0002B-train-only` artifactで追跡可能。
- DEVは別runとして実施済み。FINALは未実施、科学的採否未判定。

- DEV/FINALの開始前に、方策・全データhashに加え、[凍結した実行基盤9ソースのGit blob hash](../freeze-v2.json)の一致を要求する。不一致なら拒否。

## DEV/FINALの分離した実行ゲート
- `python -m packages.kernel.eval_cli --phase dev --output .run/EXP-0002B-DEV-smoke.json` はレビュー済み**main pushだけ**で自動実行するengineering smoke。学習・閾値調整には使わない。
- `--phase final`の評価コードを使う**一度限りのFINAL起動ゲート**は[PR #28](https://github.com/ryonakayama234/DekaSugi/pull/28)で独立レビュー・CIを通過し、承認subjectのmain pushで一度だけ実行済み。後続の文書同期PRでCIからFINALトリガーを削除する。
- [ゲート監査](../reviews/20261025-evaluator-gate.md) / [freeze](../freeze-v2.md)。

- DEV/FINALでは最初に[実行器・Verifier・meter等9ファイルの固定Git blobハッシュ](../freeze-v2.json)もチェックする。不一致なら評価前に停止する。

## DEV48 工学的run（実測）
- [20261025-dev-smoke.md](20261025-dev-smoke.md)：main `f81b656` / [Actions #40162804951](https://github.com/ryonakayama234/DekaSugi/actions/runs/40162804951) / artifact `12586733583` / JSON SHA-256 を保存。
- 48問すべてで3armの記録あり、正解40/48（3armとも）、誤成功0、LEARNEDのprimitive合計1808。研究上の採用は未判定。FINAL112は未実行。

## FINAL112 起動の承認（結果未取得）
- [起動ゲート監査](../reviews/20261025-final-activation.md) / [PR #28](https://github.com/ryonakayama234/DekaSugi/pull/28) を参照。凍結されたv2の方策・データ・数値ゲートは維持。
- 許可条件は `push(main)`、`github.run_attempt==1`、レビュー後のsquash-merge commit subject `EXP-0002B FINAL112 activation [20261025-APPROVED]`。それ以外のCIはFINALをスキップする。
- FINALを観測した後はArtifact ID / ZIP・JSON SHA-256 / source_commit / 元の方策・全dataset hash / 112問の生データ検算と結論を**別runファイル**として保存し、起動ゲートも削除する。未実行時には採否や性能の結果を書かない。

## FINAL112 本評価（2026-10-25、採用は別途）
- [20261025-final112.md](20261025-final112.md)：唯一の実行main `37b3075`、[Actions #40176125696](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176125696)、生データArtifact `12592665362`、ZIP/JSON SHA-256、独立再集計による五つの数値ゲートPASS、全タスク・family別の証拠と制約。
- 事前登録v2は不変更、FINALデータは以後の方法調整に使えない。結果は `metrics_pass_not_promoted`、標準技能への昇格なし、総CPU効果は未実証。元Artifactの保存期限は2027-01-23（GitHub表示値）；長期的な再監査にはハッシュを保った外部アーカイブが必要。
