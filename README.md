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

**Bootstrap / Research design.** アーキテクチャは提案であり、AIが学習・性能向上したという結果はまだ存在しない。
初回実験 EXP-0001 は計画段階。測定結果は実行後にのみ登録する。

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

## 次の学習研究: EXP-0002B（設計案、未実装）

[Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7) — 課題ごとに**獲得した技能を使うべきか**を経験から予測する小さなKernel。EXP-0002の成果は[PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6)でレビュー中で、mainにはまだ統合されていない。

[計画（案）](experiments/EXP-0002B/plan.md) / [仕様](docs/specs/EXP-0002B.md) / [システム図](docs/architecture/system.md) / [データフロー](docs/architecture/contracts.md)。現時点の成果は**設計と検証方針の記録**であり、性能改善や学習の実装を意味しない。
