# packages/ — Module responsibility map

id: PKG-INDEX
status: proposed
updated: 2026-10-24
tags: packages, modularity, api

現在の実装と将来の予定を区別する。EXP-0001は型付き文字列DSLの探索・実行・検証・CLIを実装。正式な採否は実験runに依存する。

| package | 責務 | 想定フェーズ |
|---|---|---|
| protocol | TaskSpec, AST, SearchResult等の型 | 1 |
| synthesis | 制限付き候補列挙と探索方針 | 1 |
| runtime | 許可されたDSL演算の安全な解釈実行 | 1 |
| verification | 正解判定と計算コストの測定 | 1 |
| library | 技能・概念の登録、依存関係 | 2 |
| memory | 課題・試行・出典付き経験ログ | 2 |
| learning | Sleep抽象化、Dream自己生成課題 | 2–3 |
| kernel | 状態に応じて探索/道具を選ぶ中枢 | 3–5 |
| tools | ファイル・外部資料等への制御された接続 | 4 |
| evaluation | 独立データセットでの評価と比較 | 1–5 |
| cli | 人間/CIが実験を実行する窓口 | 1 |

モジュール間通信の形式は [ARCH-002](../docs/architecture/contracts.md)、全体関係は [ARCH-001](../docs/architecture/system.md)。

## EXP-0001で実装したパッケージ

| Package | 主要API | 状態 |
|---|---|---|
| `protocol` | `parse_task`, `parse_program`, `check_program`, `program_to_dict`, `program_hash` | implemented |
| `library` | `Registry`, `DEFAULT_PRIMITIVES` | implemented, fixed primitives only |
| `runtime` | `evaluate` | implemented |
| `verification` | `verify` | implemented |
| `synthesis` | `enumerate_candidates`, `synthesize` | implemented |
| `cli` | `python -m packages.cli --task/--suite` | implemented |

この段階の `library` は**固定操作の管理**のみ。技能の自動獲得は未実装。

## EXP-0002 で追加するパッケージ

| Package | API | State |
|---|---|---|
| `learning` | `SkillCandidate`, `discover_skills`, `validate_skill`, `registry_with_skill` | implemented, candidate only |
| `evaluation` | `bounded_synthesize`, `expanded_nodes`, `run_experiment` | implemented; CI evaluation pending |

技能は隔離レジストリ内でのみ解釈実行され、正式ライブラリへは自動昇格しない。比較結果は [EXP-0002 runs](../experiments/EXP-0002/runs/README.md)。

## EXP-0002B TRAIN-only研究実装
| Package | API | State |
|---|---|---|
| `kernel` | `generate_partition`, `dataset_manifest`, `features`, `train`, `choose`, `PolicySnapshot` | TRAIN-only integrated and frozen; DEV evaluated separately |

Generatorは3分割の内容hashを計算するが、Kernelの判断と監査付き費用実験はTRAINでのみ実行する。FINAL評価経路と技能の自動昇格は未実装。[Audit](../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## EXP-0002B 実験評価器
| Module | API | State |
|---|---|---|
| `kernel.evaluation` | `load_and_check_freeze`, `evaluate_record`, `run_evaluation`, `summarize` | reviewed and main-integrated; FINAL112 evaluated once, numeric gates PASS, no promotion |

原始演算の計数は既存のcanonical meterに委譲。FINALは別のレビューゲートでのみ実行。[監査](../experiments/EXP-0002B/reviews/20261025-evaluator-gate.md)。

## EXP-0002B DEV工程
`kernel.evaluation`はTRAIN方策・凍結実行ソースを検証してからDEVの3armを独立実行する。[実測run](../experiments/EXP-0002B/runs/20261025-dev-smoke.md)はmainのCI Artifactとhashに紐づけた工学的検査であり、FINALの研究採用ではない。

## EXP-0002B FINAL112 outcome
[唯一のFINAL112 run](../experiments/EXP-0002B/runs/20261025-final112.md)で凍結されたKernelを独立検証し、五つの事前登録済み数値条件を満たした。独立再集計済みだがデフォルトのRegistryには何も自動昇格していない。起動ゲートは文書同期PRで撤去。次の研究方法変更には新しい評価セットが必要。

## METRO-0001 — metrology (fixture-only calibration)
- `packages/metrology` (PR2 implementation): immutable synthetic fixture evidence sealing/validation, paired metric reducer, negative controls F01–F08 and CLI `python -m packages.metrology --mode calibrate --output <fresh.json>`.
- `tests/test_metro0001_calibration.py`: exact F01/F02 gold SHA / invalid-vs-non_comparable / M3 existing meter invariant.
- This adapter intentionally rejects all production experiment evidence. No new learner/evaluator/holdout scoring, skill promotion or network access.
- [Scientific contract](../docs/metrology/evidence-model.md) / [plan](../experiments/METRO-0001/plan.md).
