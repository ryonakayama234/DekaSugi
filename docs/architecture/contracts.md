# ARCH-002 — Data contracts and flow

id: ARCH-002
status: proposed
updated: 2026-10-26
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
