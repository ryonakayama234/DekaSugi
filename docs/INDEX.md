# Documentation Index / 資料目録

id: DOC-INDEX
status: active
updated: 2026-10-24
tags: navigation, architecture, research, experiments

**探す → 該当する小さな文書を読む → 必要な依存文書だけを辿る。**
長大な総合仕様書ではなく、永続的なIDとリンクで資料を接続する。

| ID | テーマ | 状態 | 文書 |
|---|---|---|---|
| VISION-001 | 研究目的・前提・非目標 | proposed | [mission](vision/mission.md) |
| ARCH-001 | 全体システム図・モジュール関係 | proposed | [system](architecture/system.md) |
| ARCH-002 | データ構造・境界・処理フロー | proposed | [contracts](architecture/contracts.md) |
| ADR-0001 | 研究優先の軽量構成 | proposed | [decision](architecture/decisions/ADR-0001-research-first.md) |
| PROC-001 | 仮説→実験→採否 | active | [workflow](process/workflow.md) |
| PROC-002 | GitHub運用・進捗管理 | active | [github](process/github.md) |
| ROADMAP | 実験ロードマップ | proposed | [roadmap](roadmap.md) |
| EXP-0001 | 型付きプログラム合成ベースライン | accepted baseline (EXP-0001) | [spec](specs/EXP-0001.md) / [plan](../experiments/EXP-0001/plan.md) |
| EXP-0002 | 共通部分式から技能候補化（PR #6） | implemented in open PR; review pending | [issue](https://github.com/ryonakayama234/DekaSugi/issues/5) / [implementation PR](https://github.com/ryonakayama234/DekaSugi/pull/6) |
| EXP-0002B | Contextual Kernel: 技能使用の学習 | **v2 protocol proposed for review; no implementation/results; v1 superseded as evaluation plan** | [spec](specs/EXP-0002B.md) / [v2 current plan](../experiments/EXP-0002B/plan-v2.md) / [v1 historical plan](../experiments/EXP-0002B/plan.md) / [runs](../experiments/EXP-0002B/runs/README.md) |
| EXP-0002B-AUDIT-001 | PR依存と実験境界の静的監査 | static audit; adoption on hold | [audit record](../experiments/EXP-0002B/reviews/20261024-audit-001.md) / [architecture](architecture/system.md) / [contracts](architecture/contracts.md) |
| RSRCH-INDEX | 研究資料の検索入口 | collecting | [research](research/INDEX.md) |
| RSRCH-001 | プログラム合成・抽象化 | notes | [program synthesis](research/program-synthesis.md) |
| TPL-SPEC | 仕様書テンプレート | active | [template](templates/spec.md) |
| TPL-EXP | 実験テンプレート | active | [template](templates/experiment.md) |
| PKG-INDEX | packages責務の一覧 | proposed | [packages](../packages/README.md) |

## AI向け検索方針
1. 質問に関連するIDかタグをこの目録で探す。
2. 目的が実装なら `specs` → `architecture/contracts` → 対応する `packages`。
3. 目的が「なぜこの設計か」なら `decisions`。科学的根拠は `research`。
4. 目的が「本当に改善したか」なら `experiments` の計画とrun。**計画と実測を混同しない**。
5. 意見の対立や未解決論点はIssueに登録し、資料には状態を明記。

## 文書の作成ルール
- 冒頭にID・status・updated・tagsを記載（README / AGENTS / GitHubテンプレートは例外）。
- 各文書は一つの責務だけ持つ。内容のコピーを増やさずリンクする。
- 変更時は参照元の図や契約を確認し、この索引も更新する。
- Mermaid図はMarkdown内に埋め込み、GitHub上で読めるようにする。

## EXP-0002B v1: 歴史的な文書導線（**現行評価で使用禁止**）
- **旧版の履歴資料:** [v1 preregistration](../experiments/EXP-0002B/plan.md)。旧seedと閾値に方法上の欠陥があるため正式評価には使用しない。**現行の唯一の方法正本は[v2](../experiments/EXP-0002B/plan-v2.md)**。実験は未実施。
- **可視化:** [ARCH-001](architecture/system.md) と [ARCH-002](architecture/contracts.md) にpreregisteredな構成・監査データの分離図。
- **状態と来歴:** [preregistration record](../experiments/EXP-0002B/preregistration-log.md) / [run directory](../experiments/EXP-0002B/runs/README.md)（後者は未実施）。

## EXP-0002B：2026-10-24 評価計画の改訂履歴
- [最新の事前登録プロトコルv2](../experiments/EXP-0002B/plan-v2.md)：split seedを分離し、現状の探索器で達成可能な採用ゲートを事前設定。
- [v1原本（使用禁止・参考史料）](../experiments/EXP-0002B/plan.md)：研究結果を見た調整ではなく、コード実装前レビューで方法上の欠陥が発見されたため、正式評価には使用しない。
- [v2改訂理由・未実装の記録](../experiments/EXP-0002B/preregistration-v2-log.md)：新しいFINALの結果は存在しない。

## EXP-0002B：統合前のレビュー証跡
- [AUDIT-001: PR #6 / #9 / #12 の静的監査、残余リスク、統合順序](../experiments/EXP-0002B/reviews/20261024-audit-001.md)。**静的点検は記録済み・正式な独立承認/新規実験runは未実施**。
- 調査用の[PR依存図](architecture/system.md)、[監査データ境界](architecture/contracts.md)、[run目録](../experiments/EXP-0002B/runs/README.md)へ移動できる。
