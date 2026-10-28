# ARCH-002 — Data contracts and flow

id: ARCH-002
status: proposed
updated: 2026-10-28
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

## EXP-0002: SkillCandidate v1 / Macro evaluation data flow

```mermaid
flowchart LR
    TE["Train TaskSpec 0.1"] --> SR["SearchResult 0.1"]
    SR --> EX["AST subtree extractor"]
    EX --> SC["SkillCandidate v1"]
    SC --> VA["Safe Registry with macro"]
    HE["Heldout TaskSpec 0.1"] --> BA["Baseline search"]
    HE --> LA["Learned search"]
    VA --> LA
    BA --> ER["EvaluationReport JSON"]
    LA --> ER
    SC --> ER
    ER --> RU["EXP-0002/run: measured"]
```

### SkillCandidate v1（実装されたcontract）

| Field | Type | Rule |
|---|---|---|
| `schema_version` | String | `1.0` |
| `skill_id` | String | `skill_` + body_hash先頭16文字 |
| `body_ast` | Program 0.1 | 少なくとも2個のcall。既存primitiveのみを参照 |
| `body_hash` | SHA-256 | AST正規化JSONの構造hash。登録前に検証 |
| `dependencies` | sorted String[] | bodyに含まれる一意のprimitive ID |
| `provenance` | sorted String[] | 異なる成功訓練task_idが2個以上 |
| `occurrences` | Integer | distinct task_id数と一致 |
| `status` | String | 初期値 `candidate`。正式採用は自動化しない |

```json
{
  "schema_version": "1.0",
  "skill_id": "skill_<body-hash-prefix>",
  "body_ast": {
    "node_kind": "call", "type": "String", "op_id": "lower",
    "children": [{
      "node_kind": "call", "type": "String", "op_id": "trim",
      "children": [{"node_kind": "input", "type": "String"}]
    }]
  },
  "body_hash": "<SHA256 of canonical AST>",
  "dependencies": ["lower", "trim"],
  "provenance": ["train-01", "train-02"],
  "occurrences": 2,
  "status": "candidate"
}
```

### Data boundaries / 注意点
- `discover_skills(TRAIN)` への最終保留課題の入力は禁止。重複するtask_idはエラーにする。
- `registry_with_skill(candidate)` はbodyハッシュ、署名、来歴を検証し、許可済みの元primitiveを使った純粋なインタプリタに委譲する。任意Pythonソースは実行しない。
- `expanded_nodes` はmacroのInput位置へ引数ASTを置いた際の展開後ノード数を計算。探索上限 `max_ast_nodes` は**両armでこの物理ノード数に適用**。候補数上限も共通。
- `EvaluationReport` はソースcommit、Python、platform、原始演算版、train/dev/holdout task ID、候補・比較結果・判定・限界を保存。
- `status=functional_pass` は発見機構と例照合の成立のみ。`promotion_gate_metrics_pass` は独立レビューを要求する指標条件であり、自動採用ではない。
- EXP-0002はtrain/dev/finalの全入力を公開しているため、結果を用いた改良を行った後の独立評価は**新しい保留課題**が必要。

Related: [実験事前登録](../../experiments/EXP-0002/plan.md) / [仕様](../specs/EXP-0002.md) / [全体図](system.md)。

## EXP-0002 review hardening (PR #6)

- `validate_skill` explicitly rejects references to operations marked with `derived-` semantics when registering a new skill. **Nested macros remain prohibited** in this experiment; they cannot be used to undercount the AST expansion budget.
- `expanded_nodes` recursively expands skill metadata and rejects cyclic dependencies; `bounded_synthesize` rejects mismatch between derived operations in the registry and supplied skill metadata.
- New regression tests cover the formerly accepted `s(s(Input()))` macro (which expands to 5 physical AST nodes) and provenance-preserving rejection. This is a bug fix, **not** new evidence of generalization.

## EXP-0002 evaluator integrity hardening (second independent review finding)

The evaluator must verify each learned macro before any candidate search: `sha256(canonical(body_ast)) == body_hash`, `registry[skill_id].semantics_version == "derived-" + body_hash`, and that the body AST contains only approved primitives with compatible types. A matching skill ID is insufficient to protect expanded-cost accounting. This prevents swapping a shorter fake body into `learned` after a real macro has been registered. Regression tests cover mismatching body and forged internally consistent metadata.

## EXP-0002 第3回安全性検証: Registry trust boundary

- `Registry.primitives`は任意に生成可能なコンテナであり、`semantics_version`だけでは実装の真正性を保証しない。
- `bounded_synthesize`実行前に先頭3原始演算を`DEFAULT_REGISTRY`の**順序・ID・入出力型・版・callable同一性**と照合。許可外callback、旧macroを偽装した追加primitive、順序改変を拒否。
- 検証済み`SkillCandidate`からmacro実行callbackを**canonicalな原始演算のみで再構築**し、呼び出し元が渡したmacro callbackは利用しない。評価の決定性と展開後ノード上限の維持を目的とする。
- 生の`Registry`の型が安全性を保証するわけではない。上記はEXP-0002の探索評価エントリポイントでのfail-closed境界であり、`DEFAULT_REGISTRY`への自動昇格も新しい原始演算の登録も行わない。
- [P1再現条件・テスト・検査状況](../../experiments/EXP-0002/reviews/20261024-primitive-allowlist-hardening.md)を参照。事前登録計画・歴史的runは不変更。

## SEC-004: 実行用データ契約・可変Registryとの境界

```mermaid
flowchart LR
    IN["Untrusted Registry.primitives / by_name / signatures"] --> CHECK["Tuple metadata + SkillCandidate hashes"]
    CAN["DEFAULT_PRIMITIVES: canonical tuple"] --> CHECK
    CHECK -->|approved| NEW["Fresh Registry: primitives / by_name / signatures"]
    CAN --> NEW
    NEW --> MAC["Validated macro AST -> rebuilt callable"]
    MAC --> VER["Synthesis + verifier"]
    VER --> OUT["SearchResult status / AST / candidates / trace"]
    CHECK -->|rejected| ERR["ValueError before candidate search"]
```

**Boundary invariant:** `_trusted_search_registry`は固定の`DEFAULT_PRIMITIVES`のID、順序、型、意味版、実装オブジェクトと、呼出元`Registry.primitives`を照合する。実行用`Registry`は`Registry(DEFAULT_PRIMITIVES)`から新規生成し、公開`DEFAULT_REGISTRY`も呼出元の`by_name`/`signatures`も実行に流用しない。学習済みmacroは検査済み`SkillCandidate`からのみ生成する。

**Contract:** callerが提供した検索表・署名表は実行権限ではない。登録済みmacroの照合は`primitives`の宣言値とbody hashを使用する。未承認primitive/偽装macro/不正ASTは探索前に拒否し、正常系は既存の探索状態、AST、候補数、順序hashを保存する。実CPU時間の一致は保証しない。Pythonプロセス全体を悪意あるコードから隔離する仕組みではない。

この変更は安全性回帰の修正のみで、研究計画v1の事前登録条件、過去の実験run、EXP-0002Bの保留課題には変更を加えない。[監査記録](../../experiments/EXP-0002/reviews/20261025-registry-snapshot-boundary.md)。

## MEASURE-0001: PrimitiveCallMeter observation contract

```mermaid
flowchart LR
    U["Untrusted Registry + SkillCandidate"] --> C["Validate against canonical DEFAULT_PRIMITIVES"]
    P["Canonical fixed tuple"] --> C
    C --> R["Fresh Registry, validated macro AST"]
    P --> W["Canonical primitive wrappers"]
    R --> E["Enumerated AST + expanded budget"]
    W --> V["Independent verifier"]
    R --> V
    E --> V
    V --> M["Per-arm primitive invocations + by_op"]
    E --> S["Unchanged SearchResult"]
    M --> O["Paired diagnostic JSON"]
    S --> O
```

- `PrimitiveCallMeter`: mutable `total: int`, `by_op: dict[str,int]`; `to_dict() -> {primitive_invocations, by_op}`. Each arm creates a fresh instance.
- `bounded_synthesize(..., *, meter: PrimitiveCallMeter | None)` returns the unchanged `SearchResult`. Optional meter counts **only canonical primitive invocation within verifier examples**, including macro expansions. It does not count synthesis or total compute.
- `run_experiment` adds optional diagnostic `primitive_measurement_version="runtime-canonical-v1"` and `comparisons[].primitive_measurements.off/on`. Historical EXP-0002 RUN-001/002 remain unchanged.
- Untrusted executable Registry lookups are never consumed as execution authority: prior to wrapping, `_trusted_search_registry` checks primitive identity, version, order and typed macro metadata, then reconstructs a fresh execution registry; rejecting inputs produces no meter calls.
- No learned Kernel or fresh policy FINAL evaluation here; public EXP-0002 holdout results are diagnostic and cannot confirm EXP-0002B generalization.
- [Full measurement boundary](measurement.md) / [engineering audit](../../experiments/EXP-0002B/metering-log.md) / [SEC-004](../../experiments/EXP-0002/reviews/20261025-registry-snapshot-boundary.md).

## EXP-0002B — 研究計画v2を現行mainへ整合（方法は不変更）

```mermaid
flowchart LR
    T["TRAIN TaskSpec: 2 visible examples"] --> F["TaskFeatures v1: 8 pre-solve dimensions"]
    T --> B["Paired OFF/ON + canonical meter"]
    A["Private 3rd audit example: TRAIN"] --> O["SkillUsageObservation"]
    B --> O
    F --> L["5-NN cost policy: TRAIN-only"]
    O --> L
    L --> P["PolicySnapshot: ordered train IDs/hash, thresholds, skill/hash"]
    H["Unopened FINAL TaskSpec"] --> D["PolicyDecision ON/OFF/abstain"]
    P --> D
    D --> S["SEC-004 + MEASURE-0001 search"]
    S --> V["Independent verifier + separate FINAL audit"]
    V --> R["EvaluationReport: OFF/ON/LEARNED and ORACLE diagnostic"]
```

- **予定された型:** `TaskFeatures v1`（公開2例からの8次元）、`SkillUsageObservation`（TRAINのpaired OFF/ONと第3例audit）、`PolicyDecision`（ON/OFF、理由、5近傍の支持度）、`PolicySnapshot`（TRAIN ID/hash・方策/特徴版・技能body hash・定数）、`EvaluationReport`（全112問の正解、探索候補、primitive invocations、p90、OOD、回帰と欠損を記録）。
- **権限境界:** Kernel入力にgeneratorのfamily/split/seed、audit例、正解変換の識別子、FINAL結果を入れない。独立Verifier/予算/registry意味論は不変更。ORACLEは評価後だけの非実用診断。
- **計測は実装済み・学習は未実装:** [計測契約](measurement.md) / [事前登録v2](../../experiments/EXP-0002B/plan-v2.md) / [改訂履歴](../../experiments/EXP-0002B/preregistration-v2-log.md)。

## EXP-0002B TRAIN-only API契約（実装候補）

```mermaid
flowchart LR
    G["generate_partition: ExperimentTask records"] --> P["public TaskSpec: 2 examples"]
    G --> A["private audit Example: third"]
    P --> F["features -> 8 float tuple"]
    P --> R["paired bounded_synthesize: OFF/ON"]
    A --> AUD["training audit correctness"]
    R --> OBS["TrainingObservation"]
    AUD --> OBS
    F --> OBS
    OBS --> S["PolicySnapshot: frozen train observations + SHA256"]
    P --> C["choose(TaskSpec, snapshot) -> PolicyDecision"]
    S --> C
    C --> RES["ON/OFF reason, support, mean saving, distance"]
```

- `ExperimentTask`: generator専用レコード `(task, audit, family, partition, seeds)`。`TaskSpec`には公開2例と既存DSL limitsのみを含める。auditやfamilyを`choose`へ渡さない。
- `features(TaskSpec)`: 事前登録どおり8個のfloat；順序・正規化はplan-v2に固定、2例以外は拒否。`task_id`やaudit、探索結果は特徴に使わない。
- `TrainingObservation`: TRAIN task ID、8特徴値、正解監査・候補数・原始演算呼出数のOFF/ON比較と選好。Kernel推論は近傍の特徴と観測費用だけを使う。
- `PolicySnapshot`: v2定数（k=5、distance<=0.18、close>=3、ON支持>=4、mean_calls_delta>=2）、訓練観測/ID、datasetとgenerator SHA、技能body SHA、方式版、内容SHA。読み戻し時のhash不一致を拒否。
- `PolicyDecision`: `action` ON/OFF、`reason`、近傍task ID、支持件数、平均呼出節約、推論wall ms。成功確率や学習費用償却を根拠なく宣言しない。
- `preflight()`と`train_report()`はFINAL評価の結果を生成しない。データセットhashの生成は将来のFINAL成績の閲覧を意味しない。
- [事前登録](../../experiments/EXP-0002B/plan-v2.md) / [実装監査](../../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## TRAIN evidence integrity: Codex review findings addressed
- 技能候補の`discover_skills`も独立の`Registry(DEFAULT_PRIMITIVES)`で動かす。`DEFAULT_REGISTRY`の公開可変lookupはcanonicalな実行権限ではない。
- 保存`PolicySnapshot`の受信時は`policy_sha256`を除いた**受信payload全体**を検証した後、`training_ids`と`training_observations_sha256`の整合を確認する。変更部分を黙って再計算しない。
- `training_trial_evidence`はTRAIN各task×OFF/ONの`SearchResult.to_dict()`、監査正誤、原始演算計数を記録する。学習snapshotの入力フィールドには監査例・familyは追加しない。[監査](../../experiments/EXP-0002B/reviews/20261025-train-only-kernel.md)。

## EXP-0002B 統合時のfreeze契約

- `experiments/EXP-0002B/freeze-v2.json`は実験方法、生成器source SHA、dataset/partition SHA、訓練観測SHA、PolicySnapshot SHA、固定技能body SHA、main source commitとCI証拠の識別子を持つ。
- スナップショットの生成結果は実行ノイズを除き決定的で、`snapshot.to_dict().policy_sha256`が凍結値と一致しなければDEV/FINALへ進めない。各armのelapsed_msは変動するため、trial-evidence SHAは等値を要求しない。
- FINALの評価・正解出力・性能はfreezeには記録しない。[凍結の説明](../../experiments/EXP-0002B/freeze-v2.md) / [機械用情報](../../experiments/EXP-0002B/freeze-v2.json)。

## EXP-0002B 実行意味論の固定（DEV/FINALを開く前）
- `freeze-v2.json.frozen_execution_source_git_blob_sha1`で基準コミット`2cd159a`の原始演算、DSL、探索、runtime、Verifier、bounded evaluator/meter、learning、Kernelソースを個別固定する。
- 後続評価器はファイル内容のGit blob hash（`SHA1("blob <size>\\0" + bytes)`）を再計算し、全項目を一致検査してからDEV/FINALへ進む。評価器自体は別の独立レビュー対象。
- これは方策の再学習や方法変更ではなく、評価前の保全要件。[source manifest](../../experiments/EXP-0002B/freeze-v2.json)。

## EXP-0002B 評価データ契約（DEV/FINALゲート）
- `run_evaluation(phase in {dev,final},freeze_path)`: まず`freeze-v2.json`とTRAINだけで再生成した方策hash、生成器source hash、全dataset hashを検証。不一致なら評価前に拒否。
- `evaluate_record`: **判断→OFF/ON/LEARNEDの独立探索→監査**。返値は3条件の`SearchResult.to_dict`、`audit_correct`、`audit_invalid_solved`、`primitive_invocations`、`expanded_ast_nodes`、`PolicyDecision`、事後`oracle_source_action`、監査例hash。
- `summarize`: 全task/7familyのstatusとcorrectness/cost、OOD誤ON、nearest-rank p90、最大悪化、勝敗数、family-cluster paired bootstrap1000、学習費用と推論wall時間、horizon 1/32/128のprimitive限定償却、v2の固定採否ゲート。
- `numeric_status`は数値条件を満たすかのみを示し、標準Skill/Kernel自動昇格を許可しない。ORACLEは実用方策ではない。
- `pull_request`CIではDEV/FINALを呼ばず、通常のmain pushではDEVのみを実行。FINAL専用トリガーは後述の独立PR #28で条件付き追加。[評価監査](../../experiments/EXP-0002B/reviews/20261025-evaluator-gate.md)。

## DEV/FINAL gate の実行ソース不変条件とCPU計測
- 評価器は[凍結された9ファイルのGit blob SHA](../../experiments/EXP-0002B/freeze-v2.json)を比較し、pythonのruntime、synthesis、verification、canonical meter、library、Kernel等が変更されていれば**TASK評価前に拒否**。
- 3armそれぞれ`trial_cpu_ms_including_audit` / `trial_wall_ms_including_audit`、推論`policy_inference_cpu_ms`、評価全体`run_total_cpu_ms_excluding_train`を記録。原始演算呼出数は総CPU量を表さない。

## EXP-0002B DEV Evidence v1（実測・科学的採用未判定）
- `run_evaluation("dev")` は `phase="DEV"`、`final_has_been_scored=false`、`source_commit`、`policy_sha256`、`dataset_sha256`、`run_total_cpu_ms_excluding_train`、`tasks[]`、`report` を出力する。
- `tasks[]` は公開2例に基づく `policy_decision` と3arm別の `search` / `primitive_invocations` / `audit_correct` / `trial_cpu_ms_including_audit` を保存。監査用第3例はKernel選択の引数にしない。
- 同じ意思決定のLEARNED独立再試行が元armと`trace_sha256`・呼出数で一致することを検査する。時間の完全一致は要求しない。
- DEVの6familyとFINALの7familyは混同しない。`numeric_acceptance_gates={}`、`numeric_status="not_applicable_dev_smoke"` を保つ。FINALの採否は未算出。
- 実測証拠: [EXP-0002B-DEV-20261025](../../experiments/EXP-0002B/runs/20261025-dev-smoke.md)。

## EXP-0002B FINAL112 activation contract（PR #28：実行前）
- FINAL実行条件: `github.event_name == 'push'`、`github.ref == 'refs/heads/main'`、`github.run_attempt == 1`、`startsWith(github.event.head_commit.message, 'EXP-0002B FINAL112 activation [20261025-APPROVED]')` の論理積。レビュー済PRの指定subjectでのsquash-merge以外では起動しない。
- `pull_request`および通常のmain push、同じworkflow runの再試行はFINALステップと証拠アップロードをスキップする。候補・監査・評価の計算はしない。
- 凍結した9ソースGit blob、`freeze-v2.json`のdataset/policy/generator hash、TRAIN再計算snapshotと観測数を検証し、一致しなければFINAL taskを評価しない。
- 成果物: `EXP-0002B-FINAL112` というActions Artifactの `EXP-0002B-FINAL112.json`。全112問の独立3arm、監査、family別、OOD16、policy decisions、5数値ゲート、bootstrap、CPUとprimitiveを分離して収録。採用は自動化しない。
- 一度限りの運用はcommit subject + 初回attempt + 結果後のゲート削除で成立する。堅牢な一度限りの外部ロックではない点も監査記録に残す。[activation gate](../../experiments/EXP-0002B/reviews/20261025-final-activation.md)。

## EXP-0002B FINAL Evidence v1（2026-10-25採点済み・ゲート退役）
- JSON `experiment_id="EXP-0002B"`, `phase="FINAL"`, `final_has_been_scored=true`, `source_commit="37b30752..."`, `source_train_code_commit="2cd159af..."`, `policy_sha256`、`dataset_sha256`、`tasks[]`（112要素）、`report`を保持。CI artifact ID `12592665362`、ZIPとJSONの元バイト列SHAは[FINAL実測run](../../experiments/EXP-0002B/runs/20261025-final112.md)を参照。
- 各 `task`: `task_id`（全件重複なし）、`family_for_evaluator_only`、`audit_example_sha256`、`policy_decision`、独立 `off/on/learned`（検索status/AST/trace/candidate、primitive呼出数・by_op、監査正誤、CPU/wall）。選択済trialは選択元armとの不変結果一致が必要。
- `report.numeric_acceptance_gates`: correctness, vs_off, vs_on, ood_false_on, p90_tail。FINALで全trueだが `numeric_status="metrics_pass_not_promoted"`・`policy_adoption="pending_independent_review"`のまま。既定Registryへの自動昇格を禁止する。
- 反実仮想 `ORACLE`、クラスタ7種類bootstrap1000、学習費用、推論CPU、全実験CPUを原始演算とは別計測とする。独立再集計はArtifact JSONを一件ずつ再計算した算術・整合性監査で、完全に独立した合成器実行を意味しない。
- 採点済みholdoutで方法を調整せず、今後の改訂には別計画と未使用の保留課題が必要。上記FINAL起動経路は結果記録後にCIから除去する。

## EXP-0003A: versioned experience, dream and evidence contracts (TRAIN PR2 implementation; later phases planned)
この項は**実装予定の論理契約**。既存`TaskSpec v0.1`・`SkillCandidate v1.0`・`PolicySnapshot`の改変を要求しない。PR1では新APIや永続DBは未実装。各schemaは`schema_version`、不変の論理ID、provenance/sha256、source_commit、状態を持つ。照合用hashはcanonical JSON (sorted keys / UTF-8 / NaN禁止)から算出する。

```mermaid
flowchart LR
  TASK["Public TaskSpec (two examples)"] --> WAKE["WakeEpisode (task_ref, AST, status, trace, counts)"]
  AUD["PrivateAudit (third example; verifier-only)"] --> VER["Independent audit / verifier"]
  WAKE --> SLP["Sleep: verified-success episodes"]
  VER --> SLP
  SLP --> PROP["SkillProposal (body hash, provenance, dependencies)"]
  PROP --> DR["DreamCase (parent program, seed, public task, private audit)"]
  DR --> TRAIN["Paired OFF/ON cost observations (TRAIN/DREAM)"]
  WAKE --> TRAIN
  TRAIN --> CYCLE["CycleSnapshot (candidate hash, policy hash, selected IDs)"]
  HIDE["Fresh private FINAL (128; separate namespace)"] --> EVAL["Evaluator only"]
  CYCLE --> EVAL
  EVAL --> EVID["EvaluationEvidence (4arms / per-task / freeze hashes)"]
  WAKE -.-> VIEW["Read-only UI projection"]
  PROP -.-> VIEW
  DR -.-> VIEW
  EVID -.-> VIEW
```

| Schema v1 / owner | Minimum typed fields | 禁止される流入・書換 |
|---|---|---|
| `WakeEpisode` / `memory` | `episode_id: str`, `public_task_ref: str`, `status: enum`, `program_ast: Program|null`, `trace_sha256: str`, `tested_candidates: int`, `primitive_invocations: int`, `audit_evidence_ref: str`, `partition: TRAIN` | `family`/hidden answerを学習器に同梱しない。結果上書き禁止 |
| `SkillProposal` / `learning` | `proposal_id`, `candidate: SkillCandidate`, `source_episode_ids: sorted[str]`, `candidate_body_sha256`, `status: candidate|withheld|rejected` | 実行コード文字列、PR1中のaccepted状態、任意callback禁止 |
| `DreamCase` / `dream` | `dream_case_id`, `pool_id`, `public_task_ref`, `generator_program_hash`, `seed`, `strategy: random|counterfactual`, `private_audit_ref`, `selected: bool` | generator正解・familyは学習選択APIへ渡さない。私的auditの参照は監査権限のみ |
| `CycleSnapshot` / `learning` | `cycle_id`, `candidate_hash`, `wake_episode_ids`, `dream_case_ids`, `ordered_selected_pool_ids`, `ordered_selected_task_ids`, `pool_public_input_sha256`, `id_protocol_version: ID-v1`, `arm: B1|B2|B3`, `policy_snapshot_sha256`, `source_manifest_sha256`, `status: frozen|planned` | FINALやDEVで再学習しない。旧B2B snapshotを書換えない |
| `EvaluationEvidence` / `evaluation` | `evaluation_id`, `phase: DEV|FINAL`, `source_commit`, `dataset_sha256`, `policy_hashes`, `task_results[B0,B1,B2,B3]`, `audit_correct`, `metrics`, `numeric_gates`, `review_ref`, `artifact_sha256` | FINAL outcome→Sleep/Dream/Kernelへ逆流しない。UIによる採用判定禁止 |

### ID-v1: manifest-facing identifiers vs learner-facing opaque task IDs
- [EXP-0003A plan ID-v1](../../experiments/EXP-0003A/plan.md#deterministic-id-and-tie-break-protocol-exp-0003a-id-v1-before-any-generated-dataset)が正本。private manifestの`source_record_id = <split>-fNN-iNNN`、`pool_id = dream-fNN-iNNN`、`dream_case_id = b2:pool_id|b3:pool_id` は、`TaskSpec.task_id = t-<full-lowercase-SHA256-of-ordered-public-task>`と混同しない。
- `TrainingObservation.task_id`は公開TaskSpec hash IDを継承し、family/split/seed/auditおよびprovenance IDを入力として生成してはならない。複数armは独立snapshotで同一task_idを使う。異なる公開TaskSpecでIDが衝突した場合は評価前にfail closed。
- `CycleSnapshot`のmanifest項目は`id_protocol_version="ID-v1"`, `ordered_selected_pool_ids`, `ordered_selected_task_ids`, `pool_public_input_sha256`, `source_manifest_sha256`, `policy_snapshot_sha256`を含む。各selected IDからprivate manifestを経由してpublic hashを照合し、Kernelには非公開元情報を渡さない。
- 5NNは`(binary64 mean-L1 distance, opaque task_id)`、B3のpool選択は`(min distance to positive TRAIN features, pool_id)`、B2はfixed-seed shuffle後の順序で決定する。単なるunordered setや処理順への暗黙依存を禁止。ID順序とhashは運用・研究の再現性契約であって、新しい学習特徴ではない。

### PR3 TRAIN/DREAM paired search, selection and policy contracts
- PR3 `PairedObservation`はpublic task ID/8D featuresと実際に行ったOFF/ON検索・第三例auditの教師結果のみ。`paired_trial`はSEC-004真正Registry/MEASURE-0001 meterをOFF/ON独立に使用。監査は検索の後の独立第三例で、結果による追加探索を禁止。
- evaluatorのみがfamilyで8×64候補プールを層化しB2/B3それぞれ8×12=96を選択。B2固定seedシャッフルの生成順を保持。B3は正しいONかつ厳密primitive節約のTRAIN正例8D近傍距離/opaque pool ID同点処理。公開2例の事前特徴のみを選別に使う。DREAMの答え・audit・正解変換IDを特徴や選別距離へ流入させない。
- `ArmSnapshot`はB1=160, B2=B3=256の観測、同一WAKE top skill body SHA、source/private manifest SHA、共通512 pool public input SHA、選別済みpool IDとpublic task IDの**順序付き**列、固定方策version/threshold、自己内容hashを持つ。`from_dict`は意味的フィールド照合後に再生成hashを検証。160件のWAKE観測と各`wake_episode_id`の対応は維持し、public `task_id`のASCII昇順へ正規化してから`training_ids`/`observations`/`observations_sha256`/`policy_snapshot_sha256`を計算する。B2/B3の追加Dream96件は**明示的な選別順序を保持**する。WAKE入力行をシャッフルしても5NN決定・意味的SHAは一致し、Dream選別順序や来歴の偽装は拒否する。
- `choose(task,snapshot)`は公開2例の既存8D特徴と教師コストのみで（mean L1距離、opaque public task ID）順の上位5件を使い、距離0.18/近接3/ON支持4/平均削減2/監査リスクvetoの不変閾値でON/OFFを決定。新しい技能生成、Registry昇格、FINALへの直接アクセスはしない。
- PR3はTRAIN/DREAMの公開runと評価器専用の実際の第三audit・512 pool・全paired raw trialを別ファイルに隔離して証拠hashを保持する（公開repoのArtifactに対外秘匿性はない）。generator、WAKE/SLEEP、paired trial、選別、snapshot/CPU-wall、primitive実行数を分離報告。旧EXP-0002B方策・snapshotを変更しない。

### PR2 TRAIN records and evidence
- `packages/exp0003a`の`TrainCase`と`private_train_manifest`はgenerator/evaluator専用。`TaskSpec`は公開2例とopaque task IDのみ。`wake(task, private_audit)`で唯一の独立監査を行い、`WakeEpisode.to_dict()`には監査の生入力/出力・family/seedを格納しない。
- `WakeReceipt`は監査器がWAKE完了直後に発行する独立の原本照合証拠。`task_id`、`episode_sha256`（時刻以外の全フィールド）、`program_sha256`、`trace_sha256`、`audit_evidence_ref`、監査判定を束ねる。SLEEPは監査器保管のoriginal receiptsとの厳密一致を必須にする。`frozen`や自己申告のSHAだけを署名・認証と誤認しない。原本照合は再合成でも非公開監査を学習に渡す行為でもない。
- `WakeEpisode`は`public_search_status`, `status`, `program_ast`, `trace_sha256`, `tested_candidates`, `primitive_invocations`, `audit_correct`, `audit_evidence_ref`, `audit_primitive_invocations`、検索/監査CPU・wallを分離。監査合格したASTだけが`sleep()`の技能候補根拠。
- `SkillProposal`は既存`SkillCandidate`の検証済み本文hash/型/依存/出典（2課題以上）と`proposal_id`, `source_episode_ids`の候補記録。ランキング先頭1件のproposal statusのみ`candidate`、他は`withheld`。正式Registry採用もDream由来方策もPR2では作らない。
- `train_report()`はTRAIN160件のエピソードのcanonical hash、ソースblob hash、出典manifest hash、候補とrankingを持つ工学的証拠。生成器、WAKEの公開探索/独立監査、SLEEPの各CPU/wall時間を別フィールドで報告し、primitive callsと混同しない。`*_ms`の実測値は再生の厳密一致hashから除外しCPU/wall別報告。CIでArtifactにアップロードするがFINAL判定には流用しない。
- PR2 CLIはrun全体のJSON、1行1WakeEpisodeのJSONLに加え、実際に消費した全TRAINの公開TaskSpec・private第三例・family/seed/source ID、原本のWakeReceiptを**評価器専用別ファイル**として出力する。学習向けrun JSONはprivate行のSHAだけを持つ。リポジトリ公開のためActions Artifactの外部秘匿は保証せず、`private`は学習器からのアクセス隔離を意味する。出力時に新規ファイル専用`xb`で出力し、既存証拠を上書きしない。各ファイルのSHA256をログ出力しCI Artifactで保全。永続DB・Web UIが完成したという主張は禁止。

- 実保存はまずappend-only JSONL + manifest（canonical hash、run ID、partition、schema、read-model参照）。SQLiteや外部サービスは導入不要。大きな証拠ArtifactはGitHub Actionsの期限/元SHAを持つ。各レコードには`producer_version`と`source_commit`を保存し、過去データをin-place migrationしない。
- `wake()`は探索で公開TaskSpecのみを見て、Verifierのauditを別経路から受け取る。成功エピソードのASTだけをSLEEP候補の証拠とし、偶然2公開例を満たしても非公開audit不正解なら除外。
- `select_dream_cases()`は明示の乱数seedかTRAINで得た8D特徴だけを比較する。B2/B3の各8 family×12という層化はgenerator/evaluatorだけの配分情報。学習観測にfamily、seed、正解programが混入していないことを負試験で確認する。
- `EvaluationEvidence`は選択決定**前**に得たTaskSpec以外をKernelへ渡さない。B0/B1/B2/B3はそれぞれ新しいmeterと独立探索・audit。総CPU(学習/生成/選別/推論)とprimitive callsを別列として保存する。
- `Research Console`のパネル別責務と投影元は[ARCH-UI-001](ui-panels.md)を正本とし、UIに新しい科学的方法を実装しない。
- スキーマ変更・責務の追加時は[ARCH-001](system.md)、[spec](../specs/EXP-0003A.md)、[run目録](../../experiments/EXP-0003A/runs/README.md)も同一PRで更新。

Related: [experiment plan](../../experiments/EXP-0003A/plan.md) / [UI responsibility map](ui-panels.md).

## EXP-0003A PR4 — source/data/policy immutable pre-DEV freeze (Issue #36)
- `packages/exp0003a/freeze.py`はplan-v1の同一生成条件と8 familyでTRAIN160/DREAM512/DEV64/FINAL128を**採点せず**生成・hash照合する。第三audit出力はdataのhash計算にのみ使用し、DEV/FINALの探索・方策選択・Verifier評価を起動しない。TRAIN/DREAMはPR2/PR3生成器とのfull record一致が必須。4 partitionのseed/公開TaskSpec ID/出典ID衝突は全体FAIL（調整や再抽選なし）。各split内重複input数は診断用集計のみ。
- `freeze-v1.json`はPR4ソースを変更し終えてから、PR CI preflightが生成するCPython3.12固定manifestを別commitでピン留め。plan-v1・generator/DSL/meter/learning/policy/verification/preflightソースのGit blob SHA1とraw SHA256、全4splitのcanonical private row hash（第三例自体はレポートへ出さない）、top skill body hash、B1/B2/B3 semantic snapshot hash、B2/B3 ordered Dream ID/selection SHAを保存。
- `--mode check-freeze`は凍結値を同一ソースとTRAIN/DREAMで再計算して完全比較する。SOURCE違い、スプリット変更、policy hashのずれ、JSON書換えは拒否。**Git commit SHAはsquashで変わるため研究的source lockにはGit blob SHAを正本とする**。PR4のCIでDEV/FINAL評価は実行しない。別のDEV工程はfreezeレビュー成功後にのみ起動可、FINALはさらに別の人間承認付き起動PRを必要とする。

### PR4 source-guard validation order (P1 review remediation)
- `check-freeze`は評価者のtraining/生成処理に到達する前に、**保存済みJSONの自己hash、schema/plan/runtime、固定14ソースのGit blob SHA1/raw SHA256**を不活性なbyte readだけで照合し、不一致なら即失敗。これらの合格後のみ`preflight_record`がTRAIN/DREAMの再生成・学習を行ってsplit/skill/policy hashと照合する。Pythonの悪意あるimport-time codeをsandboxする設計ではないので、実行環境自体の隔離も別責務である。初回凍結値はP1修正で再固定し、source identityが同一な限り保存データSHAとpolicy SHAは変わらない。

## METRO-0001 — EvidenceEnvelope / measurement / claim data flow (proposal)

```mermaid
flowchart LR
    P["Public TaskSpec"] --> T["TrialRef"]
    S["AgentStateRef: fixed primitive/skill/policy hash"] --> T
    T --> O["Raw Observation"]
    T --> V["Independent VerificationRef"]
    O --> M["MetricSpec + Measurement"]
    V --> M
    M --> C["Comparable paired Comparison"]
    C --> I["Claim with scope / uncertainty / review"]
    H["Private audit / FINAL"] --> V
```

- 記録の正本は既存のraw JSON/JSONLとハッシュ。METRO EvidenceEnvelopeはread-only参照。原始計測値、metric version、欠測・分母を必須にして結果と解釈を区別する。
- paired比較の一致キーは同じ公開task_id・課題入力・探索予算・primitive意味版・独立検証基準・環境/費用scopeとする。**armは一致キーに含めず**、事前登録したcontrol/interventionの組（例: OFF対ON）を明示的に検査する。同一task/arm内の重複観測は原則invalid。比較不成立はnon_comparableとし効果量を計算しない。raw証拠不一致・偽造hash・禁止学習経路はinvalidとして拒否。
- private出典識別子/監査生行/FINALデータはEvaluator以外へ渡さない。現在のEXP-0003Aの凍結済みschemaやplan-v1は一切変更しない。
- 正式契約（提案）: [METRO Evidence v0.1](../metrology/evidence-model.md) / [MetricSpec](../metrology/metrics.md) / [妥当性](../metrology/validity.md) / [CAL-01 plan](../../experiments/METRO-0001/plan.md)。

## METRO-0001 PR2 — 実装した限定契約
- `packages.metrology` accepts schema=`metro-evidence/0.1`, experiment=`METRO-0001`, run=`CAL-01`, role=`fixture_calibration` **only**。任意のEXP-0003A生データは拒否し、raw元証拠や評価器を書き換えない。
- SHA-256はJSONのsort_keys=True/UTF-8/compact-separator/allow_nan=Falseで計算したraw record本体のsealであり、鍵付き署名や改ざん不可能な外部認証ではない。
- paired joinは(public_task_id, role)を中心に行い、armはOFFとONの別条件として検査。片方がmetric/unit/予算非互換なら`non_comparable`として差分を出さず、raw不正/欠測/重複/学習機密混入なら`EvidenceError`。
- summary hashは既定plan-v1の固定summary JSONに対して計算し、raw record順序に依存しない。固定条件以外の学習・領域横断評価は未実装。
Related: [evidence spec](../metrology/evidence-model.md) / [gold fixture](../../experiments/METRO-0001/plan.md).

## METRO-0001 CAL-01の実装済み証拠契約: scoped acceptance
- `metro-evidence/0.1` **人工 `METRO-0001/CAL-01` roleだけ** のcanonical JSON seal/検査・F01–F08固定summary・元fixture明細hashの保存を[PR #41](https://github.com/ryonakayama234/DekaSugi/pull/41)としてmain統合済み。
- 元Artifact ZIP/JSON/fixtureを独立取得してSHAを検査し、[校正決定](../../experiments/METRO-0001/reviews/20261027-cal01-adoption.md)に記録。観測のraw bytesのdigestと正規化summary digestを混同しない。
- invalid recordと合法だがnon_comparableなarmの差を維持。既存TaskSpec/EvaluationEvidence/Private auditの任意入出力を受け取る一般化Adapterは **未実装**。EXP-0003Aの凍結評価やLearnerへのprivateデータ導線は追加しない。


## EXP-0003A PR5 — Independent DEV64 evidence flow and data contract

```mermaid
flowchart LR
    A["FreezeManifest (read only)"] --> B["Source/Policy validator"]
    C["Frozen TRAIN/DREAM ArmSnapshot"] --> B
    B --> D["DEV TaskSpec(public only)"]
    D --> E["Pre-search policy choice"]
    E --> F["Four independent TrialEvidence records"]
    G["DEV private audit (evaluator-only)"] --> H["Independent verifier"]
    F --> H
    H --> I["DEV public RunEvidence"]
    H --> J["DEV private provenance manifest"]
    I --> K["Diagnostic Summary / Review"]
    J --> K
```

Immutable authority: `freeze-v1.json`, original 14 Git blobs, 
`experiments/EXP-0003A/plan.md`. New evaluator reads, never changes them.

- **FrozenAssets** (in memory): verified frozen manifest, B1/B2/B3
  `ArmSnapshot` and semantic SHA, one TRAIN-derived `SkillCandidate`,
  training rebuild cost. FAIL if any hash or status mismatches.
- **TrialEvidence** (per `task_id` × `arm`): action/reason, neighbors (public
  opaque IDs only), policy SHA, `SearchResult`, audit SHA reference, independently
  checked audit correctness and false-solved, tested candidates, canonical
  primitive meter, search/audit CPU+wall, selected typed AST.
- **DEV public RunEvidence**: exact source commit, freeze/split/snapshot SHA,
  per-task arm evidence, paired aggregates, regressions and uncertainty
  labelled engineering only. Does not include raw audit input/output or
  evaluator-only family/seed/source IDs.
- **DEV private provenance manifest**: full generator-only source/audit
  records, original public trial digest. Separate write-once artifact;
  must never be passed to Kernel/learner.
- **Validation order**: inert freeze schema/source bytes -> deterministic
  TRAIN/DREAM replay/policy -> DEV full manifest -> choice -> search -> audit.
  Any precondition failure exits without scoring.

Read [PR5 spec](../specs/EXP-0003A-DEV-EVALUATOR.md). DEV cannot replace
future independent FINAL128 evidence and cannot use CAL-01 synthetic
calibration as a claim of measured intelligence growth.

### PR5 additive timing evidence fields (reviewed contract)
`FrozenAssets.asset_load_cost_ms` contains `freeze_verify_cpu/wall`,
`second_train_dream_replay_cpu/wall`, `snapshot_validation_cpu/wall`,
`asset_load_total_cpu/wall`. The freeze verification contains the **first**
replayed TRAIN/DREAM policy; the later explicit replay is the **second**. Nested
`train_dream_second_replay_internal_cost_ms` is **not** an additive cost.
`TrialEvidence` adds `policy_inference_cpu_ms` and
`policy_inference_wall_ms` per arm; B0=0, B1/B2/B3 are measured before
search. `summary.arm_totals` sums the fields by arm. Overall four-arm elapsed
and CPU costs already include these trials and must not be double counted.

## EXP-0003A DEV64 one-shot evidence and trust contract (Issue #46)
```mermaid
flowchart TD
  X[Verified main SHA + frozen 14 blobs] --> V[verify_frozen then DEV hash check]
  V --> B[DEV64 task x four independent arms]
  B --> O[public.json: 256 trial rows, costs, hashes]
  B --> P[public.evaluator-private.json: audit + source records]
  O --> I[Independent stdlib audit]
  P --> I
  R[freeze-v1.json SHA locks] --> I
  I --> T[independent-audit.json and SHA256SUMS]
  T --> C[Append-only Actions artifact, 90-day retention]
```
The standalone evidence auditor does **not** import source scorer or generate
DEV/FINAL; it checks canonical raw split digest, opaque TaskSpec IDs, third-audit
references, all 256 arm meters/trials, paired B2−B3 calls/candidates/cluster
bootstrap, OOD activation counts, family and arm totals, and cost inclusion.
Four raw files have separate original-byte SHA256; failed attempts retain
`attempt.json` and logs. Artifact expires; permanent SHA/run/metrics record
requires a subsequent reviewed evidence archival update. Never silently
double-count phase totals or equate DEV with FINAL confirmation.

### Independent Codex P2 review hardening (2026-10-27)
- Each primitive meter's `by_op` canonical positive counters must sum to
  `primitive_invocations` (not just agree with copied top-level total).
- Check search status/solved/program/selected AST against audited_correct and
  false_solved, including consistent unsolved/null-program outcomes.
- Verify BOTH evidence source_commit values match the externally supplied
  40-character runner `GITHUB_SHA`; attempt must match main/first run/SHA.
- A finalization step with `always()` hashes **all extant** original JSON
  into SHA256SUMS even if scoring, preflight or independent audit fails.
- New negative and positive synthetic evidence tests run in PR CI. No DEV/FINAL
  generation/scoring may be performed before reviewed main activation.

## EXP-0003A DEV64 immutable original vs audited derived report (Issue #48)
- Original source SHA `26eaf3b4c4717968d68eb7f383b126b23b2062c8`;
  public JSON SHA256 `2fa48c841e99a69275c8bd3a5bd78eb2e01d4a3fcc226a6358958bf5cc053134`;
  evaluator-private raw SHA256 `490fbb3da156cc70e3525d6c67307b4b4e06bb725703e0b39543546275b87653`.
- Original scorer's `sum(...)` float accumulator differs from independent
  `+=` at binary64 roundoff. CPU/wall-only totals compare with
  `math.isclose(rtol=1e-12, atol=1e-10 ms)`, reject larger drift. Integer,
  outcome, per-op meter, AST/program, TaskSpec, private audit refs and SHA
  remain strict equality. Derived audit states max accepted difference.
- Audit-only CI validates original bytes before inspecting records. The public
  research ledger preserves hashes, source, metrics and provenance; **private
  manifest raw records must not enter the public Git repository**. Raw
  Artifact retention is 90 days; retaining its SHA does not preserve its bytes.


## POLICY-DIAG-001 — 診断用データ契約（設計案・未実装）
```mermaid
flowchart LR
  A["B2/B3 ArmSnapshot: hash + observations"] --> V["外部caller: source-first凍結・証拠SHA検査"]
  B["採点済みDEV64公開TaskSpec/Decision"] --> V
  V --> D["helper: snapshot構造検査と特徴量・5NN・gate trace再構成"]
  D --> E["PolicyDiagnosticRecord/0.1"]
  E --> F["根拠・欠測・不確実性つき研究記録"]
  X["private audit / FINAL128"] -.->|"学習器・再生器に渡さない"| D
```
想定レコード：`schema_version, task_id, source_refs{freeze,snapshot,dev_public_sha}, policy_reconstruction{B2,B3}, comparison{neighbor_overlap, action_disagrees, archived_primitive_difference}, classification{mechanism_labels,status,alternatives,evidence_refs}`。全フィールドに観測/再構成/探索的解釈・欠測区分を与え、privateデータは公開リポジトリに書かない。判定再生は`choose`の近傍距離昇順・公開task_id同点処理・5近傍全体の支持票と費用・順次veto/閾値を厳密に維持する。診断は新規採点を実行しない。[Issue #52](https://github.com/ryonakayama234/DekaSugi/issues/52)。

## POLICY-DIAG-001 implementation contract (not a new Evaluator)
`packages/policy_diagnostics` implements `snapshot_profile(snapshot)`, `dream_overlap(B2,B3)`, `replay(public_task,snapshot)`, and `compare_public_tasks(archived_public_tasks,B2,B3,optional_archived_rows)`. `replay` asserts exact `choose()` parity, with the ordered five neighbors, exact gate precedence and no synthesis. Data is labeled `not_observed` for absent archived costs. Caller must perform an independent pinned-source/freeze and archived-evidence integrity check before treating its outputs as authenticated research evidence; the module alone is not a complete raw-artifact provenance gateway.


## POLICY-DIAG-001 — archived-public analyzed record contract v0.1
```mermaid
flowchart LR
    A["Frozen source + policy SHA"] --> V["archive gateway validates pinned bytes"]
    B["Existing scored DEV public.json (5NN IDs and decisions)"] --> V
    C["PR3 public TRAIN/DREAM observations"] --> V
    V --> J["join archived nearest IDs to fixed observations"]
    J --> O["aggregate counters, overlap and candidate mechanisms"]
    O --> R["Report: aggregate-only, status partial"]
    T["Archived public TaskSpec.examples: absent"] -. "not_observed" .-> R
```
Only original `public.json` and PR3 public snapshot member are read; ZIP evaluator-private members are not parsed. `archive-policy-diag/0.1` input is a pair of byte-checksummed immutable public JSON payloads, plus source-blob-checked `freeze-v1.json`. Output has original-public evidence SHA, frozen snapshot SHA, denominators and descriptive aggregates, without task IDs, private examples, source rows, evaluation execution or query features. Since archived TaskSpecs are absent, exact 8D query features, neighbor distances and `close_support` are `not_observed`; replay of the 5NN *membership* from precomputed archived IDs is not an independent KNN search. [Report](../../experiments/POLICY-DIAG-001/runs/20261028-archive-public-diagnosis.md).

## OPPORTUNITY-001 — prospective paired-trial contract (design-only, no production adapter)

```mermaid
flowchart TD
  T["Fresh public TaskSpec / public task_id"] --> K["Kernel choice before trials"]
  T --> V["Independent paired OFF/ON"]
  C["Frozen canonical primitives / one skill / budget"] --> K
  C --> V
  H["Private audit example / generator-only family, seed"] --> V
  V --> R["Evaluator-only raw TrialEvidence"]
  K --> R
  R --> G["Source/hash/metric/split comparability gateway"]
  G --> M["OpportunityRecord/0.1 (sanitized)"]
  M --> A["MetricSpec + uncertainty + claim review"]
  A --> Z["New future research plan, never old holdout retune"]
  H -.->|"forbidden"| L["Kernel / Learning"]
  R -.->|"no DEV/FINAL labels"| L
  X["METRO-0001 CAL-01 fixture reducer"] -.->|"not a validated real adapter"| G
```

**Proposed schema** (`opportunity-record/0.1`, see [spec](../specs/OPPORTUNITY-001.md)):
- Identity: `schema_version`, `phase`, `task_id`, `run_id`, `source_refs{dataset_sha256,primitive_blob_sha,skill_hash,policy_sha,verifier_version,meter_version,budget_id}`. All identity/metric-version fields must be present before comparison.
- `policy{chosen_before_trials,decision_hash}`, `paired{OFF,ON}` with separate independent audit correctness, false-solved, candidate count, canonical primitive calls, trace and CPU/wall phase scope.
- `classification` is one of `both_correct_on_cheaper`, `both_correct_off_cheaper`, `both_correct_tie`, `on_only_correct`, `off_only_correct`, `neither_correct`, `not_observed`, `invalid`, `non_comparable`. Classification requires verified comparison keys, and missingness is not a numeric zero.
- `policy_excess_calls` may be non-null only if **both arms audited correct**. `missed_success`/`lost_success` are separate accuracy events. `best_of_two` is a retrospective restricted choice, never a learner-facing oracle.
- `expressibility_evidence`: `formal_invariant_proof` with reviewed proof reference and domain assumptions, `exhaustive_within_budget` with exact enumerator/budget and visible+audit example scope, `found_verified_program`, or `unknown_or_censored`. Failed search alone does not establish unrepresentability.
- `quality{comparison_status,missing_reason,provenance_ref}` plus MetricSpec name/version/unit/denominator and declared task/family analysis level.

**Trust / lifecycle**: TRAIN-only allowable paired teachers may be presented to learner only by explicit training interface; DEV/FINAL raw private outcomes remain evaluator-only. A public sanitized aggregate must not contain private third examples, family/seed/source IDs, or reuse old holdout labels to tune. Original raw records are write-once with SHA; read-only Gateway rejects mismatched SHA/schema/duplicate/split/primitive/metric/budget before analysis. `packages/metrology` currently accepts CAL-01 fixture only; new adapter requires separate calibration and design approval.

**No unapproved execution**: PR1 is purely documents. New sample generation, training, experiments and especially EXP-0003A FINAL128 are not authorized. Linked [spec](../specs/OPPORTUNITY-001.md), [plan proposal](../../experiments/OPPORTUNITY-001/plan.md), [run ledger](../../experiments/OPPORTUNITY-001/runs/README.md).

## OPPORTUNITY-001 PR2 implemented fixture contract
```mermaid
flowchart TD
  F["SYNTHETIC fx-task fixture"] --> V{"Schema, source lock, strict type"}
  V -->|"bad identity / false-solved / private field"| E["raise ValueError; no aggregate"]
  V -->|"missing audit"| M["not_observed"]
  V -->|"legal but budget differs"| N["non_comparable"]
  V -->|"verified compatible"| Q{"Which arm audited-correct?"}
  Q -->|"both"| C["calls cost gap / excess"]
  Q -->|"one"| S["missed/lost success; calls regret null"]
  Q -->|"neither"| U["unknown opportunity; calls regret null"]
  C --> A["aggregate-only counts and denominators"]
  S --> A
  U --> A
  M --> A
  N --> A
```
- Version `opportunity-fixture-v1`, phase `SYNTHETIC`, task `fx-...`. Exact row keys: `schema_version,phase,task_id,source_lock,policy_choice,policy_decision_before_trials,trials`. Lock: dataset/skill/policy/primitive SHA256, source_commit SHA-40, meter_version, budget_id. Each OFF/ON: audit_status, audited_correct, search_status, primitive_calls, tested_candidates, false_solved, budget_id.
- Caller-pinned lock equality **does not independently verify the original bytes**; pretrial flag is not independent proof of chronology. Real `opportunity-record/0.1` remains unimplemented.
- Summary is aggregate-only: class counts, denominators, policy errors, one-correct missed/lost success, both-correct excess calls, input content hash, no raw evidence/TaskSpec or scientific uncertainty. Synthetic calibration never authorizes holdouts.
- [Implementation](../../packages/evaluation/opportunity.py) / [tests](../../tests/test_opportunity_fixture.py) / [spec](../specs/OPPORTUNITY-001.md).

## OPPORTUNITY-001-PILOT-V1 prospective trust contract
- A future generator must yield exactly 64 new TRAIN TaskSpecs (8 fixed families x 8), two public examples and a distinct third evaluator-only audit. Seed formula/alphabet/rejection/transforms/task ID and budget are fully enumerated in [pilot-v1](../../experiments/OPPORTUNITY-001/pilot-v1.md).
- A reviewer must source-first pin implementation blobs and full public-dataset canonical hash, all 3 legacy B1/B2/B3 snapshot hashes and the exact frozen candidate skill before **any** search. Source + split metadata remain evaluator-only except anonymous public task IDs.
- Separate sealed pretrial decisions for B1/B2/B3 must exist BEFORE paired ON/OFF trial; no access from Kernel to source family, private audit, seed or measured outcomes. Independently verify decision and audit chronology, not merely Boolean flags.
- Real evidence MUST use a distinct future adapter/schema; `opportunity-fixture-v1` rejects it. Missing original bytes, false-solved, source mismatch or privacy leak is a stop/failure record, not a newly valid zero-cost observation.
- Method is **frozen proposal for exploratory TRAIN only**; source/manifest lock and run activation pending. No DEV/FINAL, no regression claim. [Issue #60](https://github.com/ryonakayama234/DekaSugi/issues/60).

## OPPORTUNITY-001 PR4 public-only source generator contract
- `generate_train_pilot()->tuple[TrainCase,...]` provides 64 TRAIN-only evaluator-side wrappers with `task` (exactly 2 public examples), `private_audit` (third), `family`, `seeds`, `source_record_id`. These wrappers must **never** cross into Kernel or public reports.
- `public_manifest(cases)` exports only 64 `{task_id, schema_version, domain, limits, examples[2]}` dicts. `canonical_public_digest` computes SHA256 of `json.dumps(rows, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')`. No other private fields or raw audits.
- `public_preflight()`/CLI `--mode hash-only` reports method, version, count, public SHA256 and explicit `paired_trials_executed=0`, `dev_or_final_evaluated=false`. It does NOT check source blobs or audit independence by itself.
- **No code path here runs paired searches, policy choice or any old DEV/FINAL**. The future source-first lock/real adapter must bind method, task manifest, frozen skill/policy hashes, source commits and chronological pretrial decision. Code-only source hash output is not an audit of scientific performance. [Method](../../experiments/OPPORTUNITY-001/pilot-v1.md) / [tests](../../tests/test_opportunity_pilot.py).

## OPPORTUNITY-001 PR5 independent source-only commitment contract
- Standalone `scripts/audit_opportunity_pilot_public.py` duplicates the exact frozen generation protocol with Python stdlib and NO imports of `packages.*`; `verify_public()` rejects any public manifest SHA different from the previously observed `bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85`.
- Hash-only output: `method, schema_version, public_count=64, public_manifest_sha256, third_audit_commitments_sha256, private_audit_bytes_published=false, paired_trials_executed=0, dev_or_final_evaluated=false, independent_from_project_generator_imports=true`. Private commitment canonicalizes per-task public ID plus SHA of third example; never raw third bytes or source IDs.
- A digest is **not custody**, confidentiality or a temporal pretrial seal; full live evaluator and independent evidence recount remain future trust boundaries. CI may run this source-only verifier on PR; new paired scoring is forbidden. [Method](../../experiments/OPPORTUNITY-001/pilot-v1.md).

## OPPORTUNITY-001 PR6 — immutable generator source-lock contract
- Strict `OPPORTUNITY-PILOT-GENERATOR-LOCK-V1` record pins `source_main_commit`, 9 exact Git blob SHA-1 sources (including local verifier self-file), Python 3.12.15, original EXP-0003A frozen payload + top candidate skill + snapshots B1/B2/B3, public 64-case SHA256, third-audit source commitment SHA256 and reviewed CI origin.
- `validate_source_blobs()` checks exact keys/fields and byte-for-byte `sha1(b"blob "+len+NUL+bytes)` locally BEFORE source generator import. `verify_generator_lock()` then validates historic freeze fields, both independent manifest derivations, same private third-audit commitment, counts and `paired_trials_executed=0`.
- **No scoring authority**: `new_train_pilot_scoring_permitted=false`, `old_dev_or_final_scoring_permitted=false`. No false boolean can be coerced. Actual-evidence adapter must use a distinct schema, independently seal each B1/B2/B3 choice BEFORE any candidate/search result and preserve restricted original evidence. Source lock alone is not external custody.
- [Lock](../../experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json) / [source verifier](../../scripts/verify_opportunity_generator_lock.py) / [tamper tests](../../tests/test_opportunity_generator_lock.py).

## OPPORTUNITY-001 PR7 pretrial public decision evidence contract
- `opportunity-pretrial-public-decisions-v1`: `{schema_version,method,phase,source_manifest_sha256,skill_body_sha256,policy_snapshot_sha256,decisions[64],paired_trials_executed=0,dev_or_final_evaluated=false}`. Each decision row is `{task_id,choices:{B1:{action,reason},B2:{action,reason},B3:{action,reason}}}`.
- All 3 actions are created from exactly one TaskSpec only after verifying source/freeze and rebuilding frozen TRAIN/DREAM policy snapshots. No audit inputs, task family/seed/source ID or ON/OFF trial result enters the chooser. `digest(payload)` is canonical JSON SHA256. Costs from policy inference in independent `inference_cost_ms` (not part of source-stable digest).
- Public read-only GitHub Actions artifacts and before-trial source commit evidence are engineering gate only; a later immutable pin of decision digest and independent chronology review MUST precede solver invocation. Existing source-lock permission `new_train_pilot_scoring_permitted=false` unchanged.

## OPPORTUNITY-001 PR7 P1 trust-boundary remediation
Before `verify_generator_lock` or ANY `packages.*` import, `verify_opportunity_legacy_sources.verify_legacy_source_bytes` checks the exact reviewed historic EXP-0003A manifest and all 14 blob+raw source checksums with stdlib only. `load_frozen_assets()` was found to regenerate old DEV/FINAL references via legacy `freeze.verify_frozen`; this API is now forbidden in the opportunity pretrial. A new TRAIN/DREAM-only reconstruction uses `run_train_dream`, validates original snapshot/candidate identity and selection lists without calling legacy freeze preflight. Review finding: [PR #65](https://github.com/ryonakayama234/DekaSugi/pull/65). Historical PR7 head results are retained as diagnostic, not method-valid until rerun.

## OPPORTUNITY-001 PR9 — public pretrial origin/identity/retention data contract (design-only)
**Boundary**: `evaluation / provenance`は「公開64 TaskSpecに対し、B1/B2/B3が採点前に選んだ192 action+reasonを保持・検証する」責務を負う。これはscorerや学習器ではなく、既存の`opportunity-pretrial-public-decisions-v1` payloadを新規のartifact custody envelopeで包む**提案**である。設計正本：[choice lock spec](../specs/OPPORTUNITY-001-CHOICE-LOCK-DESIGN.md)。

```mermaid
flowchart LR
  A["Official Actions artifact: original public JSON bytes"] --> B["member_raw_sha256"]
  A --> C["Strict JSON exact keys / duplicate keys reject"]
  C --> D["canonical_decision_payload_sha256"]
  E["Source-locked TRAIN64 public manifest"] --> F["64 unique task_id and order"]
  G["Frozen B1/B2/B3 snapshots + top skill"] --> H["action/reason parity (same chooser replay; auxiliary)"]
  B --> I["pilot-choice-lock-v1: origin+digest+retention"]
  D --> I
  F --> I
  H --> I
  I --> J["Copied original public member in versioned Git commit (future)"]
  K["Private raw third audit"] -.->|"NO public crossing"| I
```

**Input exact payload** (already produced by PR7, not a proposed redesign): `{schema_version,method,phase,source_manifest_sha256,skill_body_sha256,policy_snapshot_sha256,decisions[64],paired_trials_executed,dev_or_final_evaluated}`。各`decision` = `{task_id,choices:{B1:{action,reason},B2:{action,reason},B3:{action,reason}}}`、`phase=FRESH_TRAIN_ONLY`、`paired_trials_executed`はboolでない整数0、`dev_or_final_evaluated=false`。Task IDは`t-`+64 lowercase hex、3方策のchoicesは`OFF/ON`のみ。欠落/追加key、重複、private audit/family/seed/source ID/outcome混入はhard stop。決定行の順序も論理digestの一部。

**Hashes must not alias each other**:
- ZIP raw SHA256は補助的出典証拠。単一の指定JSON memberのraw SHA256と、後日Gitにコピーされたmemberのraw SHA256はbyte-for-byte一致すること。
- Canonical payload SHA256は`json.dumps(obj,sort_keys=True,separators=(',', ':'),ensure_ascii=False,allow_nan=False)`のUTF-8で計算する。raw JSON formatting変更はpayload digestを保持しても、元byte custodyを保持したことにならない。
- public TaskSpec manifest hashは新TRAIN課題分布の同一性、policy snapshot hashesは方策同一性、skill body hashは候補技能同一性。decision hashと混同しない。
- Lockにはofficial main commit、Actions run/job/artifact ID、取得時期と取得経路、original/copied member digest、認証結果と保持先、レビューheadを置く（詳細schemaは実装前にversion freeze）。Payload digestへlock自身を含めない。

**State / tri-state quality**: `planned → origin_retrieved → byte_verified → semantic_verified → retained_public → sealed_pretrial_only`、いずれもfailや必要な`not_observed`では`blocked`。`sealed_pretrial_only`は`scoring_permitted=false`を保持。元pretrialの初期禁止経路runは同じdigestでもoriginが違うため不可。replayは同じchooser実装による補助結果であって、原本の代替・独立したプログラム実装の検証ではない。

**Trust & latency**: source lock/legacy source bytesをプロジェクトimport以前に照合。元原本のZIP archiveは期間限定なので元memberを**取得・検証してから**保管する。後続scorerとのchronologyはActions/commitの観測とimmutableなGit参照の前後関係で別検証（時計表示だけでは不十分）。private第三audit元bytesのoff-repoアクセス制限付き保管はIssue #66、実験結果と旧DEV/FINALはここでは取得・採点しない。

**Status**: schema/保存先/検証器は計画であって実装済みではない。原本member raw digest、保存copy digest、actual paired outcomesは`not_observed`。negative casesとC01–C09は[engineering preregistration](../../experiments/OPPORTUNITY-001/choice-custody-preregistration.md)参照。

## OPPORTUNITY-001 PR9 — implemented public original-custody contract
**Owner**: `evaluation / provenance`の独立stdlib source `scripts/verify_opportunity_choice_lock.py`、synthetic negative `tests/test_opportunity_choice_lock.py`。公表するデータ正本は[original JSON](../../experiments/OPPORTUNITY-001/evidence/pilot-choices-public-v1.json)と[lock](../../experiments/OPPORTUNITY-001/pilot-choice-lock-v1.json)の2ファイル。元原本を再演算で置き換えず、元memberのUTF-8 JSON**27360 bytesをそのまま保全**。

```mermaid
flowchart LR
    A["Official public artifact member bytes"] --> B["raw-member SHA256 1d08..."]
    A --> C["Strict JSON parse / 64x3 / keys"]
    C --> D["logical canonical SHA256 8a8625..."]
    E["Verified source/skill/policy identities"] --> F["read-only same-chooser parity"]
    B --> L["origin+member+copy public-lock"]
    D --> L
    F --> L
    L --> G["Git content-addressed original copy"]
    P["private third original / labels / score"] -.->|"forbidden"| G
```

- exact payload：`opportunity-pretrial-public-decisions-v1`、`64` rows / `192` decisions、`{task_id,choices:{B1:{action,reason},B2:{action,reason},B3:{action,reason}}}`。action ∈ `{ON,OFF}`、reasonは固定5択で`cost_supported⇔ON`。余分・重複・非公開字段は禁止。`paired_trials_executed=0` (boolを拒否)、`dev_or_final_evaluated=false`。
- raw SHA256：`1d08e6c1518d6730e75bfaf3033a00884f7517a7d91c98a5dfff75192aabc433`。canonical JSON digest：`8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2`。この区別が同一内容の再formatによるoriginal byte差替えを検出する。
- Lockはsource main SHA、run/job/artifact ID、GitHub観測timestamps、raw digestとlogical digest、TaskSpec/snapshot/skill identities、copy pathname、全scoring flags falseを正確に持つ。**ユーザー入力のprovenance claimだけを根拠にしない**：公式APIから取ったrun/job/artifactを元のcapture run中に検証。後からのロック検査では固定ID・構造・digest・bytesを検査し、元APIが不変であると仮定しない。
- 本moduleはstdlibだけで構成。old 14-source・new 9-sourceをproject import前に検証した後、元凍結TRAIN/DREAMのみを用いる固定chooserの再演算と**元原本を比較**。これは独立実装による選択アルゴリズム監査ではない。
- [run ledger](../../experiments/OPPORTUNITY-001/runs/20261028-pr9-public-choice-custody.md)には独立の観測と非主張を記録。現時点の公開pretrial origin engineering gateは成立しても、private raw audit off-repo archival・独立actual scorer・once-only activationが未成立なのでscoring許可なし。古いDEV/FINALへの干渉なし。


## OPPORTUNITY-001 fresh TRAIN64 private original vs public SHA receipt (2026-10-28)
```mermaid
flowchart LR
  A["PRIVATE original raw audit archive (future)"] --> H["Local SHA-256 equality helper"]
  B["PRIVATE separate raw byte-copy (future)"] --> H
  C["Separately pinned original raw digest"] --> H
  H --> P["PUBLIC receipt: digest / size / copies / non-authority flags"]
  A -.->|"forbidden"| K["Public Git / Kernel / PR CI"]
  B -.->|"forbidden"| K
  P -.->|"cannot satisfy alone"| S["New TRAIN64 one-shot scoring gate BLOCKED"]
  R["Private ACL + immutable version + retention + independent restore, separately verified (future)"] -.-> S
```
- Implemented read-only `opportunity-private-copy-byte-check-v1` emits exactly `schema_version,status,raw_sha256,raw_size_bytes,copy_count,different_filesystems_observed,independent_private_raw_custody_verified,acl_encryption_retention_restore_verified,scoring_authorized,private_bytes_disclosed`. Public receipt has **no original bytes, audit examples, secrets, local file paths or evaluator-only labels**. Always false: custody verified, storage controls/restore verified, scoring authorized, private bytes disclosed.
- Caller-supplied original digest **must be separately independently grounded**: two matching copies and a caller-provided digest by themselves do **not** attest original provenance. The script rejects unsafe public-repo destinations, symlinked or same-inode files, missing/empty/oversized raw artifacts, hash/length drift.
- **Unimplemented separate authority contract:** source-first genuine fresh TRAIN64 64-original capture before search; independently reviewed immutable private store with object version, ACL, encryption/retention and readback; independent true audit; one-shot real paired scorer. [Spec](../specs/OPPORTUNITY-001-PRIVATE-CUSTODY.md) / [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).
