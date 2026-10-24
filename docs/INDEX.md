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
| EXP-0002 | 共通部分式の発見と未知例での比較 | functionally verified; promotion pending independent review | [spec](specs/EXP-0002.md) / [preregistered plan](../experiments/EXP-0002/plan.md) / [runs](../experiments/EXP-0002/runs/README.md) |
| MEASURE-0001 | 実行されたprimitiveのコスト計測と反実仮想比較の下準備 | experimental branch; independent verification pending | [system/data diagrams](architecture/measurement.md) / [measurement log](../experiments/EXP-0002B/metering-log.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7) |
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
