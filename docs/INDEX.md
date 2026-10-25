# Documentation Index / 資料目録

id: DOC-INDEX
status: active
updated: 2026-10-25
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
| EXP-0002 | 共通部分式の発見と未知例での比較 | implemented in main; scientific promotion unaccepted | [spec](specs/EXP-0002.md) / [preregistered plan](../experiments/EXP-0002/plan.md) / [runs](../experiments/EXP-0002/runs/README.md) |
| EXP-0002-SEC-003 | Registry偽装と展開予算すり抜けの安全監査 | security remediations reviewed and merged to main | [review record](../experiments/EXP-0002/reviews/20261024-primitive-allowlist-hardening.md) / [PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6) |
| EXP-0002B-EVAL-GATE | 凍結方策による独立DEV/FINAL評価器 | main integrated; FINAL112 numeric gates PASS, not promoted | [evaluator code](../packages/kernel/evaluation.py) / [review gate](../experiments/EXP-0002B/reviews/20261025-evaluator-gate.md) / [Issue #25](https://github.com/ryonakayama234/DekaSugi/issues/25) |
| EXP-0002B-FINAL-ACTIVATION | FINAL112の1回限りの承認済み実行ゲート | completed; once-trigger retired after FINAL run | [activation audit](../experiments/EXP-0002B/reviews/20261025-final-activation.md) / [v2 protocol](../experiments/EXP-0002B/plan-v2.md) |
| EXP-0002B-FINAL-20261025 | FINAL112の保留評価・五つの数値採否・独立再集計 | metrics_pass_not_promoted; no total-CPU benefit proven | [FINAL measured run](../experiments/EXP-0002B/runs/20261025-final112.md) / [run index](../experiments/EXP-0002B/runs/README.md) / [CI #40176125696](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176125696) |
| EXP-0002B-DEV-20261025 | DEV48の工学的検査・生データ再現情報 | engineering smoke PASS; scientific adoption undecided | [measured run](../experiments/EXP-0002B/runs/20261025-dev-smoke.md) / [run index](../experiments/EXP-0002B/runs/README.md) / [CI #40162804951](https://github.com/ryonakayama234/DekaSugi/actions/runs/40162804951) |
| EXP-0002B-FREEZE | TRAIN結果とDataset/PolicySnapshot SHAの評価前固定 | fixed before DEV/FINAL; no new outcome | [freeze record](../experiments/EXP-0002B/freeze-v2.md) / [machine-readable hashes](../experiments/EXP-0002B/freeze-v2.json) / [Issue #23](https://github.com/ryonakayama234/DekaSugi/issues/23) |
| EXP-0002B-TRAIN | 訓練専用のgenerator・8次元features・KNN方策とhash付snapshot | frozen TRAIN policy reused unchanged for FINAL112 | [code](../packages/kernel/__init__.py) / [audit](../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md) / [Issue #21](https://github.com/ryonakayama234/DekaSugi/issues/21) |
| EXP-0002B | 文脈付き技能ON/OFF価値の学習 | FINAL112 numeric acceptance PASS; independent audit done; not promoted | [spec](specs/EXP-0002B.md) / [current v2 protocol](../experiments/EXP-0002B/plan-v2.md) / [historical v1](../experiments/EXP-0002B/plan.md) / [change log](../experiments/EXP-0002B/preregistration-v2-log.md) / [static audit](../experiments/EXP-0002B/reviews/20261024-audit-001.md) / [run index](../experiments/EXP-0002B/runs/README.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7) |
| MEASURE-0001 | verifier内primitive実行費用の観測（Kernel学習の前提） | CI and Codex code review passed; PR #18; no policy | [measurement](architecture/measurement.md) / [audit](../experiments/EXP-0002B/metering-log.md) / [runs index](../experiments/EXP-0002B/runs/README.md) / [Issue #17](https://github.com/ryonakayama234/DekaSugi/issues/17) |
| SEC-004 | Mutable lookupを信用しない実行Registryの再生成 | main-integrated; CI and Codex code-review verified | [security record](../experiments/EXP-0002/reviews/20261025-registry-snapshot-boundary.md) / [Issue #14](https://github.com/ryonakayama234/DekaSugi/issues/14) |
| EXP-0003A | WAKE–SLEEP/Couterfactual DREAMの設計・事前登録 | proposed; design-only, no outcomes | [spec](specs/EXP-0003A.md) / [plan-v1](../experiments/EXP-0003A/plan.md) / [runs](../experiments/EXP-0003A/runs/README.md) |
| ARCH-UI-001 | Research Consoleパネル→module→data正本 | proposed interface contract, UI not implemented | [UI responsibility map](architecture/ui-panels.md) |
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
