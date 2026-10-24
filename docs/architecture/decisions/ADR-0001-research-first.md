# ADR-0001 — Research-first modular architecture

id: ADR-0001
status: proposed
updated: 2026-10-24
tags: design-decision, modularity, evaluation

## Context
巨大モデルを個人でゼロから学習する負担は大きい。ユーザーが研究したいのはパラメータの肥大化ではなく、**外部化された技能・抽象化による知能拡張**である。

## Decision proposal
- Python標準ライブラリ中心、Linux/WSL2、CPUで最小実験を開始。
- `packages/` に責務分離。初期は独立配布可能な多数パッケージにしない（過剰設計回避）。
- 型付きDSL → 決定的探索 → 制限付き実行 → 独立検証 → 経験保存、の順で育てる。
- MLを導入する前に非学習ベースラインと評価方法を作る。
- Mermaid図、データ契約、実験ログ、PR/Issueをソースコードと同じくバージョン管理する。

## Alternatives
1. 事前学習LLM中心エージェント: 即効性は高いが研究仮説の切り分けが難しい。
2. 最初からすべてをニューラル学習: データ・計算予算と失敗分析が重い。
3. 大規模なマイクロサービス構成: 現時点では運用コストが利点を上回る。

## Consequences
利点: 再現性、責務の明確化、部品単位の能力評価。
欠点: 自然言語汎用性は低い。記号DSLに依存する部分がある。
再検討条件: 実験で探索不能・表現力不足が反復して観測されたとき。

Linked: [VISION-001](../../vision/mission.md), [ARCH-001](../system.md), [EXP-0001](../../specs/EXP-0001.md)。
