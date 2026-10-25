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

## EXP-0002 の実装境界（技能の自動発見）

```mermaid
flowchart TD
    T["Train TaskSpec x2"] --> S["Synthesis: EXP-0001の探索器"]
    L["Library: trim / lower / upper"] --> S
    S --> E["解法ASTとtask_id"]
    E --> D["Learning: 共通部分式を構造Hashで集計"]
    D --> C["SkillCandidate: body・provenance・依存関係"]
    C --> G{"Validation: 型・来歴・body hash"}
    G -->|OK| R["隔離したRegistryを構築"]
    R --> X["Evaluation: Learned条件"]
    L --> B["Evaluation: Fixed baseline"]
    H["開発と保留課題"] --> X
    H --> B
    X --> M["同じ候補上限・展開後AST上限で比較"]
    B --> M
    M --> F["再現可能な実験run / 採否判定"]
    F -.->|"独立レビュー後のみ"| A["将来の正式ライブラリ採用"]
```

- **実装済み:** `packages/learning` の共通部分式抽出と安全なmacro登録、`packages/evaluation` の比較CLI、学習候補の独立test。
- **未実装:** Sleep/Dream全体ループ、永続Episodes DB、学習された検索方針、Kernelによる自律タスク選択。
- **決定的な境界:** `learning` は訓練課題からのみ候補を作る。`evaluation` は候補を触らず開発/最終評価を計測。生成したmacroは `DEFAULT_REGISTRY` を変更しない。
- 探索条件とデータの対応は [ARCH-002](contracts.md)、研究ゲートは [EXP-0002](../specs/EXP-0002.md)、実測は [runs](../../experiments/EXP-0002/runs/README.md) を参照。

## EXP-0002 security boundary — 第3回独立レビュー指摘への対応

```mermaid
flowchart LR
    IN["TaskSpec + caller Registry + SkillCandidate"] --> CHECK["実行前: canonical primitive allowlist照合"]
    BASE["DEFAULT_REGISTRY: trim/lower/upper のID・型・版・実装"] --> CHECK
    CHECK -->|偽装・順序変更・未知演算| REJECT["拒否: ValueError"]
    CHECK -->|一致| REBUILD["技能body hash・型検証、ASTからmacroを再構築"]
    REBUILD --> EVAL["Bounded synthesis: 展開後ASTと候補数の予算"]
    EVAL --> VER["独立Verification"]
    VER --> REP["結果と監査証跡"]
```

- 呼び出し元から提供されたRegistry内の実装callbackは、原始演算もmacroも実行権限の根拠にしない。primitiveは`DEFAULT_REGISTRY`の実装同一性で検査し、macroは型付きASTから再構築する。
- PR #6の第3回P1を含む安全修正はSEC-004とあわせてmainへ統合済み。コード品質の検査根拠は[独立監査の記録](../../experiments/EXP-0002/reviews/20261024-primitive-allowlist-hardening.md)と[SEC-004追跡](../../experiments/EXP-0002/reviews/20261025-registry-snapshot-boundary.md)。科学的な技能昇格は別判断。

## SEC-004: 実行用Registryの独立スナップショット（mainへ統合済み）

```mermaid
flowchart TD
    A["Caller Registry / SkillCandidate（非信頼）"] --> V["Metadata / hash / budget validation"]
    P["DEFAULT_PRIMITIVES（固定の原始演算定義）"] --> V
    V -->|invalid| X["Fail closed: reject before search"]
    V -->|valid| R["Registry(DEFAULT_PRIMITIVES): fresh maps"]
    P --> R
    R --> M["Rebuild macros from validated AST"]
    M --> S["Bounded synthesis + independent verifier"]
    S --> E["Same status / candidates / AST / trace"]
```

- `DEFAULT_REGISTRY`の`primitives`、`by_name`、`signatures`は公開属性で、可変な実行権限の根拠にしない。原始演算の正本は`DEFAULT_PRIMITIVES`、実行に使う検索表と署名表は毎回新しい`Registry`で生成する。
- 呼出元の`Registry.by_name`を参照してmacroを認証しない。登録情報は`primitives`タプルと`SkillCandidate`のbody hashで検査し、macro callableも検証済みASTから再構築する。
- この境界はEXP-0002の`bounded_synthesize`に限定される。任意のPythonコードや同一プロセスの攻撃者からの完全な隔離を意味しない。新Kernelの実装やFINAL評価には進んでいない。
- [SEC-004の回帰・監査記録](../../experiments/EXP-0002/reviews/20261025-registry-snapshot-boundary.md)と[Issue #14](https://github.com/ryonakayama234/DekaSugi/issues/14)を参照。

## MEASURE-0001: 実行時primitive計測（PR #18、まだKernel学習なし）

```mermaid
flowchart TD
    I["TaskSpec + caller Registry + SkillCandidate"] --> V["SEC-004 validation"]
    P["DEFAULT_PRIMITIVES: canonical definitions"] --> V
    V -->|invalid| X["Reject before executing"]
    V -->|valid| T["Fresh trusted Registry"]
    T --> E["Enumerate same AST candidates"]
    P --> W["Wrap canonical primitive implementations only"]
    T --> M["Rebuild macros from validated AST"]
    W --> M
    M --> F["Metered independent verifier"]
    E --> F
    F --> C["PrimitiveCallMeter.total / by_op"]
    F --> R["SearchResult invariants"]
    C --> D["Diagnostic comparison, not Kernel training"]
    R --> D
```

- `packages/evaluation`: optional per-arm counter for verifier-time canonical primitive calls. The DSL/AST/limits/enumerator are unchanged.
- **Not implemented:** EXP-0002B feature extraction, training, contextual policy, future sealed FINAL. An original public EXP-0002 holdout rerun is diagnostic only.
- [計測仕様](measurement.md) / [データフロー](contracts.md) / [監査記録](../../experiments/EXP-0002B/metering-log.md)。

## EXP-0002B — 研究計画v2を現行mainへ整合（方法は不変更）

```mermaid
flowchart TD
    PROTO["事前登録v2: immutable protocol"] --> GENERATE["Dataset generator: planned, split-disjoint seeds"]
    GENERATE --> TRAIN["TRAIN 144; private audit separately held"]
    GENERATE --> DEV["DEV 48; engineering smoke only"]
    GENERATE --> FINAL["FINAL 112; unopened"]
    TRAIN --> PAIR["Canonical metered OFF/ON trials"]
    PAIR --> FEATURE["TaskFeatures v1, public examples only"]
    PAIR --> OBS["Audited costs and outcomes"]
    FEATURE --> FIT["5-NN knn-cost-v1 training: planned"]
    OBS --> FIT
    FIT --> SNAP["Immutable PolicySnapshot: planned"]
    SNAP --> EVAL["Learned vs OFF vs ON vs oracle evaluation: planned"]
    FINAL --> EVAL
    DEV --> CHECK["No threshold fitting"]
```

- **統合済み基盤:** SEC-004の正本RegistryとMEASURE-0001（[PR #18](https://github.com/ryonakayama234/DekaSugi/pull/18)）。古い計測[PR #9](https://github.com/ryonakayama234/DekaSugi/pull/9)は安全性問題により未マージ・クローズ済み。
- **今回の作業は方法と図のみ:** v1原本を歴史資料として追加し、[v2現行正本](../../experiments/EXP-0002B/plan-v2.md)を一文字も変更せず載せる。新規Generator・Kernel・学習済Policy・FINAL結果は依然として未実装。
- [v2改訂理由](../../experiments/EXP-0002B/preregistration-v2-log.md) / [仕様](../specs/EXP-0002B.md) / [データフロー](contracts.md) / [Issue #19](https://github.com/ryonakayama234/DekaSugi/issues/19)。

## EXP-0002B TRAIN-only Kernel（実装候補、FINALは未実行）

```mermaid
flowchart TD
    V["Frozen protocol v2"] --> G["Generator: separated train/dev/final seeds"]
    G --> T["TRAIN 144 with visible two examples"]
    G --> H["TRAIN private third audit example"]
    T --> F["8D pre-solve features"]
    T --> S["Canonical metered OFF / ON search"]
    H --> O["Audited training observations"]
    S --> O
    F --> K["5-NN fit and conservative ON/OFF"]
    O --> K
    K --> SNAP["Immutable PolicySnapshot + SHA256"]
    G --> HASH["All-split dataset content hashes only"]
    SNAP --> NO["FINAL evaluation disabled in this PR"]
    HASH --> NO
```

- `packages/kernel`: v2仕様に固定したsplit生成器、8次元特徴、TRAIN 144問のfull-information paired search、監査付き教師ラベル、5近傍の選択、PolicySnapshot hash。
- `packages/evaluation`の安全な `bounded_synthesize(..., meter=...)` を再利用し、原始演算・独立Verifier・候補予算を変更しない。
- FINALについては**データセットの内容hashだけ**計算可能とする。最終課題での技能選択・探索・正誤評価を行うコード経路は本PRに追加しない。
- [実装監査](../../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md) / [方法正本](../../experiments/EXP-0002B/plan-v2.md)。
