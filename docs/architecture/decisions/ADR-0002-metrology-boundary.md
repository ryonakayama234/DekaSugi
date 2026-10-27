# ADR-0002 — 独立Metrology層と証拠の非干渉性

id: ADR-0002
status: proposed
updated: 2026-10-27
tags: architecture, decision, metrology, trust-boundary

## Context
実装済みのMEASURE-0001はcanonical primitiveを正しく数えるが、観測が何の能力を測るか、どの条件が比較可能か、どの証拠からどこまで主張できるかは別の責務。EXP-0003Aの凍結済み評価器に評価指標を後付けすれば、独立評価の妥当性が損なわれる。

## Decision proposed
1. 既存kernel/synthesis/runtime/verification/learningを一切書き換えず、versioned read-only Evidence Gateway → Quality Validator → Metric Reducer → Analysis → Claim/Reviewの論理層を外付け。
2. ファイル/参照hashとMetricSpecを正本にし、表示UIやClaimは元データを改変しない。
3. 初回はstd-lib PythonとJSON/JSONL。DB、Web UI、外部依存は導入しない。
4. 科学的な推論、正式技能昇格、FINALの起動には別ゲート。measureに実行権限を与えない。
5. sourceと指標の変更履歴を版管理。比較不能はfail closedではなくnon_comparableとして記録し、不正証拠はfail closed。

## Alternatives
- 既存Evaluator内部へ全測定を追加: 結合が強く凍結方法を破るため却下。
- 汎用指標1点へ統合: 意味と費用が混ざり妥当性が失われるため却下。
- 大規模DB/可視化から着手: 初期の校正前には過剰のため延期。

## Consequences
既存ロジックを変更せず校正できる。証拠アダプタの対応範囲は明示的に制限される。過去の実験成果を新しい証拠として再利用することはできない。

Related: [ontology](../../metrology/ontology.md) / [evidence model](../../metrology/evidence-model.md) / [system](../system.md) / [METRO plan](../../../experiments/METRO-0001/plan.md).
