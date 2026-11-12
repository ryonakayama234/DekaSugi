# WORLD-LEAN-1 — planned experiment ledger

id: WORLD-LEAN-1-RUNS
status: proposed / planned / NOT_IMPLEMENTED / NOT_RUN
updated: 2026-11-12
tags: world, experiment-ledger, design-only

設計正本: [WORLD-LEAN-EXPERIMENT-DESIGN-20261112-01](../../../docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-01.md)。追跡: [Issue #207](https://github.com/ryonakayama234/DekaSugi/issues/207)。

| 工程 | 現在の状態 | 証拠／次の条件 |
|---|---|---|
| 設計案の提出 | proposed | 11操作、24/24法則、4腕、16 seed、5 checkpointは候補 |
| 監督者審査／Owner採否 | pending | RQ1〜3と比較・閾値・費用を審査 |
| 人工fixture工学実装 | NOT_AUTHORIZED / NOT_IMPLEMENTED | 別途の実装許可が必要 |
| source／数値の固定 | NOT_FROZEN | source・生成規則・解析・候補順・runtimeのdigestは未作成 |
| master seed／split／holdout実体化 | NOT_RUN | 本PRでseed・task・目標を生成しない |
| 学習snapshot | NOT_RUN | 旧CALや旧実験のsnapshotを移植しない |
| 正式評価／再現性確認 | NOT_AUTHORIZED / NOT_RUN | 独立審査と別のOwner評価GOが必要 |
| 結果採用 | NOT_EVALUATED | LEAN候補を旧B／L-Schema最終認定へ自動変換しない |

費用算術・二項尾確率の確認と文書リンク検査は設計の検算であり、世界・学習器・人工fixtureを走らせた実験結果ではない。旧CAL_AUTHORIZED・実施前停止は不変。実験run ID、seed、task digest、成績、CPU実測は存在しない。


## 2026-11-12 engineering implementation update — later authorization

The above `NOT_AUTHORIZED` entries describe the former design-only stage. Following supervisor [AGREE](https://github.com/ryonakayama234/DekaSugi/pull/208#issuecomment-6823583705), Owner adopted design `a0d0a203` and separately granted *implementation plus artificial fixture* GO. [Source order and digest](../../../docs/research/WORLD-LEAN-1-ORDER-FREEZE-20261112.md) are submitted but **not independently approved**.

| Updated gate | State |
|---|---|
| World / public learner / four arms / analyzer implementation | IMPLEMENTED, fixture-only |
| Unit / semantics / STATIC-RANK reachability / process boundary fixture | 23 synthetic tests PASS locally on CPython 3.13.5 |
| Transition benchmark / extrapolation | 100,000 transitions measured; [receipt](20261112-fixture-gate.md), no real-run guarantee |
| TRAIN-only ambiguity (4 artificial series) | 18/192 (9.375%) pooled; one series 7/48 (14.58%), supervisor to assess |
| Total order and 12-file source digest | COMMITTED / SUPERVISOR_REVIEW_PENDING |
| CPython 3.12.12 exact-head CI | PENDING, not claimed as passed |
| Formal seeds / holdout materialization / evaluation | FORBIDDEN / NOT_RUN; separate Owner GO required |
| Existing CAL/SPEC records | UNCHANGED |

[Deterministic and timing evidence JSON](20261112-artificial-fixture.json). Stop after this gate; no evaluation authorization is implied by a passing fixture.

## Six-demo revision -02 (separate proposal and evidence)

- [Design -02](../../../docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-02.md): only the public spec-demo count rises from 4 to 6; dependent order, arithmetic and source lock are versioned separately.
- [Fixture receipt -02](20261112-six-demo-fixture-gate.md): TRAIN-only four named synthetic streams and tests; no scientific data.
- Old four-demo receipt, implementation PR #209, source lock and CAL/SPEC history remain unchanged. Supervisor diff review, separate Owner adoption and later evaluation GO are required.
