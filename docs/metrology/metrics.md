# METRO-METRICS — 指標レジストリ契約 v0.1

id: METRO-METRICS
status: proposed; not_implemented
updated: 2026-10-27
tags: metrology, metric, measurement, units, reproducibility

## MetricSpec の必須属性
metric_id, metric_version, construct_id, observation_source, unit, population_and_denominator, aggregation, valid_values, missingness_policy, scope_limitations, comparison_constraintsを必須とする。MetricSpecは集計前に固定し、変更時は新versionを作る。元runを上書きしない。

## Phase 1: 校正する観測指標
| metric_id (proposed) | unit | authoritative source | aggregation / 注意 |
|---|---|---|---|
| audited_success_count | tasks | evaluator verifier verdict | verified=trueの件数。監査欠測は成功0と黙って置換しない |
| false_solved_count | tasks | independent private audit | solvedかつ監査不合格。private raw答をlearnerへ戻さない |
| tested_candidates | candidates | SearchResult | 課題/armで整数、合計は比較可能な予算のみ |
| primitive_invocations | calls | MEASURE-0001 runtime-canonical-v1 | verifier中のcanonical primitive実行のみ。総CPUではない |
| expanded_ast_nodes | nodes | bounded synthesis budget | 展開後のAST予算であり実行callではない |
| cpu_process_ns | nanoseconds | sampled phase CPU clock | 特定phase/scopeを固定、ノイズがありbit-wise再現を要求しない |
| wall_elapsed_ns | nanoseconds | sampled phase monotonic clock | スケジューリング影響。CPUとの差は必ず報告 |
| policy_abstention | decisions | policy decision record | 定義された条件下のOFF保留を含む。未知領域成功率とは区別 |

機能が出力していない項目はnot_observedにする。可能な限り既存スキーマの原値を転記/参照し、新しい値を推測生成しない。一つの観測内で宣言済みMetricSpecの値域やunitに違反する場合はinvalidとしてfail closed。個々の観測が各MetricSpecに適合していても、arm間でmetric_id・version・unit・対象数・予算が対応せず同じ差分を計算できない場合はnon_comparableとし、効果量を返さない。

## 条件付き推定指標（初回の新しい測定結果ではない）
- success_rate = audited_success_count / audited_trials_count。監査欠測を分母に含むか否かは分析前に宣言。欠測件数は別に併記する。
- paired_cost_delta(task) = calls_control(task) − calls_intervention(task)。task_idの完全一致と同じ意味/予算/環境条件が必要。負差も含め全件開示。
- learning_gain = E[D,B,V|post] − E[D,B,V|pre]。学習前後以外を変更した場合は学習の効果と断言しない。
- amortized_cpu(n) = total_learning_cpu / n + mean_inference_cpu。訓練・dream・探索・メータを含む範囲を明記し、primitive_countと混同しない。
- 各推定にはn、分母、課題分布、効果方向、ばらつき/CI、解析単位（task/family）を保存。8 familyのbootstrap区間を一般化の証明としない。

## 比較が成立する条件
1. 同じ公開課題を同じ検証器で監査し、paired unitのIDが一致すること。
2. 同じprimitive意味論・探索予算・評価条件・metric_versionで比較すること。意味上許可されたarm介入差は事前計画に明記。
3. 学習・推論・監査の費用のうち、どの範囲を含めたか明記すること。
4. 異領域にまたがる場合、task accuracyを一つの尺度に合算せず、分布別の推定と対照を提示すること。
5. 矛盾する条件はnon_comparable。数値結果が存在しても優劣の主張は禁止。

## 計測器校正の通過条件
- deterministic integers (counts/hash/status) は同一証拠・同一MetricSpecでbit-for-bit一致。
- elapsed time は再現要求なし。負値・NaN/Infinity・欠測非申告は拒否。
- instrumentation-on/offでSearchResult status, AST, candidates, traceとpolicy choiceが不変（異なる計測値の混同はしない）。
- provenance改変・重複・source-identity driftは集計前に拒否。
Related: [measurement existing](../architecture/measurement.md) / [calibration plan](../../experiments/METRO-0001/plan.md) / [ontology](ontology.md).
