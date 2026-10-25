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

## 現在の状態 (2026-10-25)

**EXP-0002B はFINAL112の一回限りの評価まで完了しました。** [正式実測](experiments/EXP-0002B/runs/20261025-final112.md)で4条件ではなく既定3arm (OFF/ON/LEARNED) を比較し、監査正解はすべて80/112、LEARNEDは候補1520・原始演算6880（OFF1536/6944、ON1744/8160）。事前登録の5数値基準はPASS、ただし**正式技能昇格なし・総CPU利益は未実証**。FINAL起動ステップは削除済み。[統合後CI](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176764493)。

**EXP-0003A は新規の設計・事前登録段階です（未実装・未実行）。** [新計画](experiments/EXP-0003A/plan.md) / [仕様](docs/specs/EXP-0003A.md) / [アーキテクチャ](docs/architecture/system.md) / [データ契約](docs/architecture/contracts.md) / [研究コンソールのUI責務](docs/architecture/ui-panels.md) / [run目録](experiments/EXP-0003A/runs/README.md)。WAKE・SLEEP・DREAMの未知課題評価はまだありません。

**既存の成果**: EXP-0001は非学習baselineとして技術的PASS、EXP-0002は技能候補発見を実装済み（候補の一般的正式採用なし）。SEC-004の実行信頼境界とMEASURE-0001のcanonical primitive meterは継承。

## EXP-0002B の過去の開発コマンド・工程（当時の位置づけ）

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

このコマンドが出力する内容は**TRAINのみ**。データセットhashは計算するが、FINALの探索・評価は実行しない。参照：[事前登録v2](experiments/EXP-0002B/plan-v2.md) / [実装監査](experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## EXP-0002B — 評価前に固定した学習方策

TRAIN144問での学習と復元可能なKNN方策がCIで一致。**[DatasetとPolicySnapshotの凍結記録](experiments/EXP-0002B/freeze-v2.md)**を先に保存してから、DEVとFINALの別工程で独立評価する。TRAIN証拠は凍結済み。DEV48の工学的診断結果および後続FINAL112の正式結果は別runとして保存した。

## EXP-0002B — DEVとFINALの独立ゲート

学習済みKernelの改変を検出する評価器を[監査手順](experiments/EXP-0002B/reviews/20261025-evaluator-gate.md)として追加。コードPR内では訓練fixturesのみをテストし、レビュー済みmainでDEV48 smokeを実施し、その証拠を保存した。FINALは独立レビュー後に専用トリガーから実行済みであり、トリガーは削除済み。
