# ARCH-002 — Data contracts and flow

id: ARCH-002
status: proposed
updated: 2026-10-24
tags: contracts, schema, task, ast, evaluation

EXP-0001は**型付きの小さなDSL**を実装し、自由なPythonコードを生成・実行しない。以下のTaskSpec/ASTのJSON例は実装スキーマ `0.1` に対応する。

## 境界を越えるデータ

| オブジェクト | 意味 | 最低限のフィールド |
|---|---|---|
| TaskSpec v0 | 課題・制約 | task_id, domain, examples, limits |
| Primitive v0 | 許可された基本操作 | op_id, input_type, output_type, semantics_version |
| Program v0 | 型付きAST | node_kind, type, operands/children |
| Attempt v0 | 探索試行 | task_id, program_hash, evaluation, cost |
| SearchResult v0 | 判定と計算量 | task_id, status, solved, program, tested_candidates, max_nodes, max_candidates, elapsed_ms, trace_sha256 |
| SkillCandidate v1 | 将来の抽象技能 | skill_id, body_ast, dependencies, provenance, status |

## データフロー

```mermaid
flowchart TD
  T["TaskSpec JSON"] --> S["探索器"]
  P["Primitive定義"] --> S
  S --> AST["型付きProgram AST"]
  AST --> I["制限付きインタプリタ"]
  I --> V["Examples照合"]
  V --> A["Attempt: 実行・試行記録"]
  A --> E["EvalResult"]
  E --> F["実験run記録"]
```

### TaskSpec例（提案）
```json
{
  "schema_version": "0.1",
  "task_id": "str-trim-lower-01",
  "domain": "string_to_string",
  "examples": [
    {"input": "  RED ", "output": "red"},
    {"input": " Blue  ", "output": "blue"}
  ],
  "limits": {"max_ast_nodes": 4, "max_candidates": 5000}
}
```

### AST例（提案）
```json
{
  "node_kind": "call",
  "type": "String",
  "op_id": "lower",
  "children": [{
    "node_kind": "call",
    "type": "String",
    "op_id": "trim",
    "children": [{"node_kind": "input", "type": "String"}]
  }]
}
```

## 不変条件
1. 型に合致しないASTは実行前に拒否する。
2. 実行可能な操作はallowlistにある決定的な純粋関数だけ。
3. 同じTaskSpec・同じプリミティブ集合・同じ予算で探索順が再現する（タイムアウトによる変動を除く）。
4. 入出力例への適合と未知例への一般化は別々に測る。
5. runにはソースのcommit SHA、Python版、OS、探索制限、seed、データセット版を残す。
6. 検証器は探索アルゴリズムの外側に置き、解法を不正に誘導しない。

Related: [ARCH-001](system.md), [EXP-0001](../specs/EXP-0001.md)。

## EXP-0001の実装契約 (schema_version 0.1)

- `TaskSpec`: `domain=string_to_string`、`task_id`、`examples`（1〜256）、`limits.max_ast_nodes`（1〜32、既定4）、`limits.max_candidates`（1〜100000、既定5000）。文字列長は最大4096文字。
- `Program`: `input` または `call(op_id, child)` の一引数AST。`type=String` を型検査し、登録外操作/型不一致/ノード数超過は実行前に拒否。
- `Registry`: `trim`, `lower`, `upper` の順。実装はPython `str.strip/str.lower/str.upper`、追加依存なし。
- `Synthesis`: ノード数昇順、同じノード数では親候補の列挙順×レジストリ登録順。構造SHA-256重複除去。**意味的な重複除去はしない**。
- `Verification`: 全例の一致を要求。空の例集合は拒否。判定器は探索器と別モジュール。
- `SearchResult.status`: `solved`（全例一致）、`not_found`（指定ノード上限まで全列挙）、`budget_exhausted`（次候補を評価する前に候補予算に到達）。
- `tested_candidates` は評価したASTの個数、`trace_sha256` は評価順にAST構造ハッシュを改行連結したSHA-256。経過msは測定ノイズがあるため決定性の比較から除く。
- `--suite` の実験レポートはcommit SHA・Python・プラットフォーム・操作のsemantics_versionを同時に記録する。

**注:** `not_found` は**今回のDSLと探索上限で見つからなかった**ことを意味する。一般にその問題が解けないことの証明ではない。

実装: [protocol](../../packages/protocol/__init__.py) / [synthesis](../../packages/synthesis/__init__.py) / [runtime](../../packages/runtime/__init__.py) / [verification](../../packages/verification/__init__.py)。

## EXP-0002B — 課題別技能選択の契約・データフロー（**提案・未実装**）

```mermaid
flowchart LR
    T["TaskSpec v0.1"] --> X["TaskFeatures v1"]
    X --> Q["Kernel Policy v1"]
    S["SkillCandidate v1"] --> Q
    P["PolicySnapshot v1"] --> Q
    Q --> D["PolicyDecision v1"]
    D --> RUN["Bounded synthesis + verifier"]
    RUN --> E["SkillUsageObservation v1"]
    E --> MEM["Append-only episodes / SQLite later"]
    MEM --> FIT["Policy training on TRAIN only"]
    FIT --> P
    E --> REP["EvaluationReport + independent holdout"]
```

| Object | 必須フィールド（提案） | 保存先と境界 |
|---|---|---|
| `TaskFeatures v1` | `feature_version`, `task_id`, `vector`, `derived_from_example_ids` | 解答前にTaskSpec入出力例から計算。未知の正解ASTは不使用 |
| `SkillUsageObservation v1` | `observation_id`, `task_id`, `partition`, `skill_id`, `policy_arm`, `status`, `verified`, `tested_candidates`, `primitive_invocations`, `runtime_ms`, `source_commit` | 結果は追記のみ。正誤と計算量を別フィールドで保持 |
| `PolicyDecision v1` | `task_id`, `policy_id`, `enabled_skill_ids`, `estimated_cost_delta`, `confidence`, `reason_code`, `fallback` | 初期値はbaseline・不確実ならOFF。判断は検証器の外側 |
| `PolicySnapshot v1` | `policy_id`, `algorithm_version`, `features_version`, `training_ids`, `training_hash`, `parameters`, `candidate_skill_hashes` | 学習版をimmutableに固定。holdoutに対して再訓練しない |
| `EvaluationReport v1` | `experiment_id`, `dataset_version`, `arm`, `metrics`, `source_commit`, `policy_snapshot_hash`, `env` | 候補数・演算回数・時間・失敗・退行を別集計 |

**教師信号:** 同一訓練TaskSpecに「技能OFF」と「技能ON」を同じ予算で試した差分（正確性を優先し、次に実際の原始演算呼出数を評価）。生成した技能名を入力の正解ラベルとして直接教えない。

**公平性:** holdoutの結果をPolicySnapshotへ逆流させない。oracle方式は比較の上限でしかなく、実際のKernelに使わせない。重複family/seedや、TaskSpecの入出力例を跨ぐリークを監査する。

**安全性:** 不確実な場合は技能OFFに戻し、すべての探索候補は既存の型検査・allowlist実行・独立検証器を通す。macro展開後コストも計測する。新スキルの正式昇格とは無関係。

Related: [EXP-0002B spec](../specs/EXP-0002B.md), [experiment proposal](../../experiments/EXP-0002B/plan.md), [architecture](system.md)。

## EXP-0002B preregistered trial: task/audit isolation v1（提案、未実装）

```mermaid
flowchart LR
    GEN["Frozen dataset generator"] --> PUB["TaskSpec: two IO examples"]
    GEN --> PRIVATE["Evaluation-only: third audit example + family"]
    PUB --> FEATURE["TaskFeatures: 8 numeric features"]
    PUB --> ARMS["Paired OFF/ON runs: TRAIN"]
    ARMS --> OBS["SkillUsageObservation: status, candidates, primitive calls"]
    PRIVATE --> SCORE["Audit after search"]
    OBS --> SCORE
    SCORE --> FIT["KNN cost learner: TRAIN only"]
    FIT --> SNAP["PolicySnapshot: source hashes + frozen parameters"]
    SNAP --> EVAL["Unopened FINAL evaluation"]
    EVAL --> REPORT["EvaluationReport: per-task + grouped metrics"]
    PRIVATE --> REPORT
```

| Data object | 機密/役割 | 正本/バージョン |
|---|---|---|
| `TaskSpec` | 学習器・探索器に渡す**2組のみ**の入出力例と共通の予算。family,split,監査例は禁止 | protocol v0.1 / generator v1 |
| `AuditExample` | 第3例。特徴抽出・探索中には使わない。TRAINでの教師信号とFINALでの独立採点には使える | generator v1 / restricted evaluator |
| `TaskFeatures` | 観測可能な8値。正解プログラム、技能効果、family/seed/splitを含めない | `task-features-v1` |
| `SkillUsageObservation` | 同一訓練課題に対するOFF/ONの正誤、候補、基本演算呼出数、監査・来歴 | `runtime-wrapped-v1`を元とするv1提案 |
| `PolicySnapshot` | 5-NNの固定閾値、全訓練ID/Hash、学習内容、skill body hash、source commit、canonical hash | `knn-cost-v1` |
| `EvaluationReport` | 112最終課題の4条件、独立監査、族別コスト/退行、OOD、CI環境を記録 | EXP-0002B v1 proposal |

不変条件: 最終112課題を結果に合わせて再利用しない。公開されたEXP-0002旧holdoutの診断値は学習器の教師・採否根拠から排除する。前計算やPolicy推論の時間とprimitive呼出数は混同しない。exact generator/feature/policy constants: [preregistered plan](../../experiments/EXP-0002B/plan.md)。

## EXP-0002B v2 — 隔離した分割・監査データの契約（未実装）

```mermaid
flowchart TD
   G["Generator: disjoint train/dev/final seeds"] --> PUB["TaskSpec: visible IO×2"]
   G --> PRIV["AuditExample: hidden IO×1 + family"]
   PUB --> FEAT["Features: 8 numeric values; pre-solve"]
   PUB --> SEARCH["TRAIN pair: OFF/ON"]
   SEARCH --> OBS["Observation: statuses and primitive calls"]
   PRIV --> SCORE["Independent post-search audit"]
   OBS --> SCORE
   SCORE --> SNAP["Immutable PolicySnapshot: TRAIN only"]
   SNAP --> FINAL["Unopened FINAL evaluation"]
```

生成seedはsplitごとに`10000000/20000000/30000000`の非重複領域とし、例番号を加算しても重複しない。TaskSpecには`family/seed/split/audit`を含めない。v1は[履歴](../../experiments/EXP-0002B/plan.md)として保存し、[v2の固定契約](../../experiments/EXP-0002B/plan-v2.md)を実装の唯一の基準とする。
