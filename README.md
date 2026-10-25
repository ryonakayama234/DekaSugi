# DekaSugi

**小さな中枢が、外部の知識・技能・道具を再利用し、自ら新しい操作体系を獲得できるかを検証する研究プロジェクト。**

- 事前学習済みの巨大LLMは初期実験で使わない。
- 失敗した仮説も記録し、未検証の構想と実証済みの成果を区別する。
- Python / Linux (WSL2) / ローカルCPUから始める。
- プロジェクト名は **DekaSugi**。旧構想の仮称「ATELIER」は文献・議論上の呼称であり、リポジトリ名ではない。

## Entry points

| 読者 | 最初に読むもの |
|---|---|
| 初めて参加する人 | [研究目的](docs/vision/mission.md) → [全体構造](docs/architecture/system.md) |
| 実装するAIエージェント | [AGENTS.md](AGENTS.md) → [資料索引](docs/INDEX.md) |
| 実験を再現する人 | [初回実験](experiments/EXP-0001/plan.md) → [実験プロセス](docs/process/workflow.md) |
| 進捗を確認する人 | [ロードマップ](docs/roadmap.md) とGitHub Issues / Pull Requests |

## 現在の状態

**EXP-0002B**: TRAIN-only PolicySnapshot凍結と独立評価器はmain統合済み。[DEV48 engineering smoke](experiments/EXP-0002B/runs/20261025-dev-smoke.md)は2026-10-25に正常終了（OFF/ON/LEARNEDとも40/48監査正解、学習型は候補440・primitive1808）。**FINAL112問は未実行、科学的採用は未判定**。[CI #40162804951](https://github.com/ryonakayama234/DekaSugi/actions/runs/40162804951)。

**EXP-0001 は技術的にPASS、固定DSLの非学習baselineとして採用済み。** [実測run](experiments/EXP-0001/runs/README.md)。
**EXP-0002 は技能候補の発見と小規模実験を実施済み（保留課題で6→5候補、反転課題で40→47候補）。** [事前登録計画](experiments/EXP-0002/plan.md)、[再実行](experiments/EXP-0002/runs/README.md)。技能の一般的な性能向上は未実証。安全修正を含む[PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6)はCIとCodexコードレビューを経てmainへ統合済み。技能の科学的な正式採用は別判断として保留。

**MEASURE-0001**: 次段階の技能価値学習に向け、`bounded_synthesize`に安全な原始演算呼出数カウンタを[PR #18](https://github.com/ryonakayama234/DekaSugi/pull/18)で実装し、CIとCodexコードレビューで検証。これは計測装置であって、Kernelの学習や新しいFINAL実験の成功ではない。[計測仕様](docs/architecture/measurement.md) / [監査記録](experiments/EXP-0002B/metering-log.md)。

**EXP-0002Bの研究計画v2**：[固定プロトコル](experiments/EXP-0002B/plan-v2.md)を評価方法の正本として保存。旧[v1](experiments/EXP-0002B/plan.md)は歴史的参考に限定し、学習KernelはTRAIN-onlyの実装・レビュー段階であり、新規FINALの実行結果はまだない。[仕様](docs/specs/EXP-0002B.md)。

ローカル資料検査: `python scripts/check_docs.py`（標準ライブラリのみ）。

## 原則

**課題 → 仮説 → 設計 → 実装 → 実験 → 第三者視点の検証 → 採否決定 → 文書更新**。
コードとともに図・データ契約・実験記録を更新する。詳細は [開発ルール](docs/process/workflow.md)。

## EXP-0001: 動くベースライン

前提: Python 3.12+ / Linux または WSL2。追加のPython依存は不要。

```bash
python -m unittest discover -s tests -v
python scripts/check_docs.py
python -m packages.cli --task experiments/EXP-0001/tasks/composition.json
python -m packages.cli --suite --output /tmp/exp0001.json
```

- 事前登録の7ケースは `--suite` で検証する。
- 出力は探索状態・候補数・解法AST・探索順ハッシュ・実行時間を含む。
- 実行結果の採否は [実験run記録](experiments/EXP-0001/runs/README.md) で管理。
- **EXP-0001は自動学習ではない。** 学習による改善の検証は後続の実験。

## EXP-0002: 共通部分式から技能候補を作る

独立した訓練エピソードの解法ASTから共通部分式を抽出し、許可済みDSLだけで新しい技能候補を実行する。学習条件と固定baselineを同じ候補数・**展開後の原始ASTノード数**で比較する。

```bash
python -m packages.evaluation --output .run/EXP-0002-result.json
```

機能/効率の実測と、技能を標準ライブラリへ正式採用する判断は別段階。[設計図](docs/architecture/system.md) / [仕様](docs/specs/EXP-0002.md)。

## EXP-0002B：訓練専用Kernel（研究段階）

```bash
python -m packages.kernel --mode preflight --output .run/EXP-0002B-preflight.json
python -m packages.kernel --mode train --output .run/EXP-0002B-train-only.json
```

上の実装段階で生じる結果は**TRAINのみ**。データセットhashは計算するが、FINALの探索・評価は実行しない。参照：[事前登録v2](experiments/EXP-0002B/plan-v2.md) / [実装監査](experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## EXP-0002B — 評価前に固定した学習方策

TRAIN144問での学習と復元可能なKNN方策がCIで一致。**[DatasetとPolicySnapshotの凍結記録](experiments/EXP-0002B/freeze-v2.md)**を先に保存してから、DEVとFINALの別工程で独立評価する。TRAIN証拠は凍結済み。DEV48の工学的診断結果は別runとして保存し、FINALの汎化性能は未判定。

## EXP-0002B — DEVとFINALの独立ゲート

学習済みKernelの改変を検出する評価器を[監査手順](experiments/EXP-0002B/reviews/20261025-evaluator-gate.md)として追加。コードPR内では訓練fixturesのみをテストし、レビュー済みmainでDEV48 smokeを実施し、その証拠を保存した。FINALは独立レビューを経た別トリガーが設定されるまで実行しない。
