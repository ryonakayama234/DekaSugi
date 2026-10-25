# EXP-0003A — Run index (not executed)

id: EXP-0003A-RUNS
status: planned_only; no EXP-0003A trials or outcome
updated: 2026-10-25
tags: exp0003a, run-index, preregistration, evidence

## 状態
- PR1: [plan-v1](../plan.md)、[spec](../../../docs/specs/EXP-0003A.md)、[ARCH-001](../../../docs/architecture/system.md)、[ARCH-002](../../../docs/architecture/contracts.md)、[UI map](../../../docs/architecture/ui-panels.md)の設計のみ。
- `TRAIN`: not_run。`DREAM`: not_run。`DEV`: not_run。`FINAL`: not_run。自動生成問題・成功数・CPU/primitive結果・PolicySnapshotの実測値はいずれも存在しない。
- 今回のCIで既存のEXP-0001/0002/0002B回帰が走っても、それをEXP-0003Aのrunと呼ばない。
- PR2以降の各作業は専用の不変run記録とCI SHAを追記し、`planned` / `engineering` / `confirmatory`を区別。失敗も保存。
- FINALはplanの事前固定・source/data/snapshot freeze・独立レビュー・人間による一度限りの実行承認より前に開かない。
- 生Artifactは保存期間・ZIP/JSON SHAと長期アーカイブの有無を明記。EXP-0002Bの既存FINAL Artifactの期限は2027-01-23であり、新研究のデータと混同しない。

Related: [preregistration](../plan.md) / [previous FINAL](../../EXP-0002B/runs/20261025-final112.md).
