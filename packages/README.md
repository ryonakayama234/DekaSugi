# packages/ — Module responsibility map

id: PKG-INDEX
status: proposed
updated: 2026-10-24
tags: packages, modularity, api

以下は**予定構成**。このREADMEだけではモジュールが実装されたことにはならない。

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
