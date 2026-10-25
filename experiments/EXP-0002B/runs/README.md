# EXP-0002B — Runs index

id: EXP-0002B-RUNS
status: generator and TRAIN-only implementation PR; no DEV/FINAL result
updated: 2026-10-25
tags: exp0002b, runs, measurement, preregistration

EXP-0002B has **no train/learned-Kernel/fresh FINAL result**. MEASURE-0001 uses the already published EXP-0002 examples for instrument diagnostics and unit regression, never a new confirmatory holdout.

- [MEASURE-0001 integration and verification record](../metering-log.md).
- [MEASURE-0001 architectural measurement contract](../../../docs/architecture/measurement.md).
- [Experiment design Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7).
- [Current protocol v2](../plan-v2.md) — integrated before implementation; no FINAL outcome.

## 事前登録v2統合状態
- [v2の正本](../plan-v2.md)は評価・学習実行前に固定。旧[v1](../plan.md)は旧seedと閾値の問題から評価には使わない。
- Generator、TRAIN観測、DEV検査、FINAL 112問の学習比較結果は**未実施**。MEASURE-0001以前の公開holdoutは新規評価に流用しない。

## EXP-0002B TRAIN-only evidence（CI上の診断）
- `python -m packages.kernel --mode preflight` は全splitのデータ内容hash・seed一意性だけを記録。
- `python -m packages.kernel --mode train` はTRAIN144課題のpaired実測・ハッシュ付きPolicySnapshotを生成。Github Actions artifact名`EXP-0002B-train-only`に保存する（実装PRのCI実行後）。
- **DEV smokeとFINAL112問の技能選択・検索・採否結果は含まない。** [TRAIN-only実装監査](../reviews/20261025-train-only-kernel.md)。
