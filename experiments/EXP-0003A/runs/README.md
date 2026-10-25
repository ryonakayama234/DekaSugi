# EXP-0003A — Run index (PR2 TRAIN engineering; DREAM/DEV/FINAL not run)

id: EXP-0003A-RUNS
status: PR2 TRAIN evidence implemented; no DREAM/DEV/FINAL outcomes
updated: 2026-10-26
tags: exp0003a, run-index, preregistration, evidence

## 状態
- PR1: [plan-v1](../plan.md)、[spec](../../../docs/specs/EXP-0003A.md)、[ARCH-001](../../../docs/architecture/system.md)、[ARCH-002](../../../docs/architecture/contracts.md)、[UI map](../../../docs/architecture/ui-panels.md)の設計のみ。
- `TRAIN`: PR2実装とCIによる160問の工学的WAKE/SLEEP記録。単一run JSONをGitHub Actions Artifact `EXP-0003A-TRAIN-engineering` に保存し、最新CI/Artifact IDとrun成果のhashはレビュー後に追跡する。`DREAM`: not_run。`DEV`: not_run。`FINAL`: not_run。PolicySnapshot/FINALの成果は存在しない。
- TRAIN初回の結果は技能候補の発見可否の工程診断であり、H2/H3の性能検証ではない。候補0件・監査不合格・run異常を失敗のまま保存し閾値やseedを変更しない。
- 今回のCIで既存のEXP-0001/0002/0002B回帰が走っても、それをEXP-0003Aのrunと呼ばない。
- PR2以降の各作業は専用の不変run記録とCI SHAを追記し、`planned` / `engineering` / `confirmatory`を区別。失敗も保存。
- FINALはplanの事前固定・source/data/snapshot freeze・独立レビュー・人間による一度限りの実行承認より前に開かない。
- 生Artifactは保存期間・ZIP/JSON SHAと長期アーカイブの有無を明記。EXP-0002Bの既存FINAL Artifactの期限は2027-01-23であり、新研究のデータと混同しない。

Related: [preregistration](../plan.md) / [previous FINAL](../../EXP-0002B/runs/20261025-final112.md).
