# ARCH-001 — System architecture

id: ARCH-001
status: proposed
updated: 2026-10-24
tags: diagram, architecture, components, wake-sleep

> 目標全体図は**提案**。EXP-0001に限定した型付き探索・実行・検証は実装済み（採否は実験runを参照）。各モジュールは [packages目録](../../packages/README.md) で管理。

## 目標アーキテクチャ

```mermaid
flowchart TD
    U["TaskSpec: 目的と制約"] --> K["Kernel: 何を試すか選ぶ"]
    L["Library: 原始演算と獲得技能"] <--> K
    K --> S["Synthesis: 型付き候補を探索"]
    S --> R["Runtime: 制限付きAST評価"]
    R --> V["Verification: 入出力と条件を検証"]
    V --> E["Episodes: 試行・結果を記録"]
    V --> O["解答または失敗理由"]
    E --> W["Sleep: 抽象候補を発見"]
    W --> D["Dream: 合成課題を生成"]
    D --> A["Evaluation: 独立課題と比較"]
    A -->|"採用基準を満たす"| L
    A -->|"失敗・保留"| E
```

## 最初の実装境界 (EXP-0001)

```mermaid
flowchart LR
    T["TaskSpec / examples"] --> S["Enumeration search"]
    P["Primitive registry"] --> S
    S --> X["Typed AST"]
    X --> R["Pure interpreter"]
    R --> V["Example verifier"]
    V --> M["Result / counters"]
```

EXP-0001は **学習・Wake-Sleep・外部Webアクセスを実装しない**。型付き表現・探索・検証・測定のみを実装する。依存は `protocol → library/runtime/verification/synthesis → cli`。実験結果は [run目録](../../experiments/EXP-0001/runs/README.md) に分離。

## レイヤの責任と依存方向
- `protocol`: 共通の不変データ形式とバージョン。外部依存なし。
- `synthesis`: protocol + primitive情報から候補を探索。任意コード実行は禁止。
- `runtime`: 型付きASTの純粋なインタプリタ。許可された演算のみ。
- `verification`: 正解/不正解と評価指標を記録。探索器の都合で採点基準を変更しない。
- `library`: 原始演算/採用技能のメタデータと履歴。
- `memory`: 観測・試行ログ。結果と解釈を分離。
- `learning`: 後続フェーズで抽象化・Wake-Sleep・練習課題生成。
- `kernel`: 後続フェーズで課題と技能から行動を選択する。

新しくコードを追加するときは、この図の実装範囲を塗り分ける代わりに各要素の実装/未実装を明記し、[データ契約](contracts.md)を同期する。
