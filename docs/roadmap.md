# Research roadmap

id: ROADMAP
status: proposed
updated: 2026-10-24
tags: milestones, roadmap, planning

| Phase | 課題 | 成立条件 | 状態 |
|---|---|---|---|
| 0 | AGENTS / 図 / データ契約 / 実験記録の基盤 | 目録・計画・検査・PRの導線が存在 | completed (CI verified) |
| 1 | EXP-0001: 型付き小規模DSLの合成器 | 同じ設定で候補探索・検証・計測を再現 | completed — technical acceptance PASS |
| 2 | EXP-0002: 部分プログラムを技能候補化 | 候補抽出が決定的で、探索の変化を比較可能 | evaluated — functional PASS; candidate not promoted |
| 3 | EXP-0003: Wake–Sleep + Dream | 合成問題と独立評価で非学習baselineと比較 | candidate |
| 4 | 現実のCSV/JSON資料・記憶と接続 | 出典・権限・再実行可能性を守る | candidate |
| 5 | 小型学習型Kernel・領域間転移 | 保留課題で再現可能な利益を確認 | research idea |

次の機能を作る前に、[研究目的](vision/mission.md)と[EXP-0001仕様](specs/EXP-0001.md)を確認。
日付や性能達成の見込みは確定しない。

## EXP-0002B preregistration integration checkpoint (2026-10-25)
- SEC-004とMEASURE-0001はmainに統合済み。[PR #18](https://github.com/ryonakayama234/DekaSugi/pull/18)のcanonical primitive meterを学習に使う。
- [事前登録v2](../experiments/EXP-0002B/plan-v2.md)を実装前の唯一の方法正本として統合。v1は歴史資料、採用ゲートとseedはv2で凍結、結果を見て再調整しない。
- 次段階：別PRでgenerator・8次元特徴・TRAIN-only KNN・PolicySnapshotを実装し、凍結とレビューを経てFINALを開く。
- 目的は限定された文字列family上の技能の使い分けの検証であり、広範な領域転移・自律学習の実証ではない。

## EXP-0002B TRAIN-only実装 (2026-10-25)
- 計画v2を不変更で使い、別PRでsplit generator、8D features、TRAIN 144 paired comparison、conservative 5NN policy and hash snapshotを実装する。
- 後続のDEV/FINAL研究評価は独立レビューとfreezeの後。今回の実装・テストだけで改善・汎化成功を主張しない。[監査記録](../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## EXP-0002B 評価器の実装ゲート (2026-10-25)
- 凍結したTRAIN方策でのみDEV smokeとFINALを評価。PRのCIはTRAIN-fixtureだけ、main pushではDEVだけを実行。
- FINAL112問の実行トリガーは評価コードの独立レビューとDEV証拠取得の後に別PRで開く。学習方法のretune、性能の過大主張は禁止。[評価監査](../experiments/EXP-0002B/reviews/20261025-evaluator-gate.md)。
