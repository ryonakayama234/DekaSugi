# METRO-0001 — 計量基盤の校正（CAL-01）事前登録 v1

id: METRO-0001-PLAN-V1
status: proposed_preregistration; not_run
updated: 2026-10-27
tags: metrology, preregistration, calibration, evidence, integrity

> この文書は測定器の正しさを検証するCAL-01の事前登録提案。PR1はdocs-only。PR2の実装や実測前に方法/失敗基準を固定し、修正時はv2として履歴を残す。これは知能向上や汎化の独立試験ではない。

## Hypothesis / 反証可能な仮説
- M1 deterministic aggregation: 同じvalid EvidenceEnvelopeとMetricSpecなら、集計順序を変えてもinteger/ID/hashが同じ。
- M2 provenance/integrity: 偽hash・重複・欠測・版不一致を黙って数値に補完しない。invalidをfail-closedで拒否。
- M3 non-interference: 既存canonical metering on/offがstatus, chosen AST, candidates, trace, selected policyを変えない。新METRO reducerは過去の証拠へのread-only作用のみ。
- M4 comparability: same task pairs、source/version、limit、primitive semantics、audit条件、コストscopeを確認。異なる比較はnon_comparableで効果差を主張しない。

## Dataset / inputs（新しい評価問題を生成しない）
- 決定的な人工fixture: (F01) valid 3 tasks × 2 arms、(F02) shuffled order、(F03) duplicate id、(F04) missing audit、(F05) changed source/hash、(F06) mismatched budget/unit、(F07) split leak marker、(F08) negative/nonfinite time。各値はfixtureに固定しexpected metricsを記録する。
- 追加工学的診断として、取得が許されるTRAIN-only evidence artifactのみを使用してよい。その場合exact artifact hash/CLI/source shaと監査アクセス範囲をrunに記録し、artifact不達の場合fixture-onlyをinconclusive for external-adapterとする。
- 使用済みEXP-0002B FINAL112は後方互換性の再集計のみ許可しCAL-01の新しい学習能力の肯定材料にしない。EXP-0003A DEV64/FINAL128は生成・採点・閲覧を禁止。

## Experimental controls / procedure
1. PR1のMetricSpec/evidence-model/ontology/validityとこの計画を別PRで固定。first evaluation run before PR2 feature implementationは禁止。
2. Schema parse + source/read-only constraint + duplicate/missing/tamper preflight。valid以外は統計計算を開始しない。
3. valid fixtureでsuccess/candidate/calls/paired deltasを期待値と整数完全一致で比較。
4. shuffled valid evidenceでも正規化集計hashが一致。元raw hashは輸送内容が違うなら同一と誤解しない。
5. test adversarial fixturesごとに所定のinvalid/non_comparableを出すことを確認。invalidに効果量を付与しない。
6. 測定器計算とCPU/wall費用を記録。タイミングは非決定的な測定量として実測範囲と環境情報を報告。
7. コードtest、docs check、exact-head CI、独立レビュー、全run記録の後に計測器の採否を決定。

## Metrics / success criteria
- Valid F01/F02: expected exact discrete metrics / canonical normalized summary hash **100%一致**。
- Invalid F03/F04/F05/F07/F08: **100% fail-closed**, no effect claim, raw data unmodified.
- Incomparable F06: **100% non_comparable**; paired delta must not be returned.
- M3: test on canonical SearchResult fixtures and existing non-instrumented/instumented regression: status/AST/candidates/trace/choose invariants 100% same. If comparison source is inaccessible, M3=inconclusive, not pass.
- Quality: no new dependencies; same docs/ARCH-001/ARCH-002/UI/AGENTS/INDEX/run sync in implementation PR; all preexisting regression tests unchanged and success.

## Acceptance / stop
METRO-0001 v1 can be **calibrated** only if M1–M4 tests have evidence and independent review accepts exact head. Missing source or parser incompatibility -> inconclusive; silent measurement drift/security leak -> invalidated; failing any preregistered gate -> failed. Never retune thresholds based on tests without documenting new protocol version. No skill promotion, DEV/FINAL trigger, source/freeze modification or performance claim.
Calibration PASS means instrument correctness on specified fixtures, not general AI intelligence measurement validation.

## Limits / future
No human/AI dialog evaluation, cross-domain transfer, latent single intelligence score, skill utility causal proof or production UI in CAL-01. These need separate experiment and fresh holdout. The data contracts keep future domain adapters possible.

Related: [runs](runs/README.md) / [ontology](../../docs/metrology/ontology.md) / [metrics](../../docs/metrology/metrics.md) / [evidence](../../docs/metrology/evidence-model.md) / [validity](../../docs/metrology/validity.md).

## CAL-01: F01/F02 gold fixture v1 (固定した既知解)
これらは文字列DSLの実際の結果ではない **人工の測定器検証入力** である。IDはfixture名前空間 `cal-t01` 等であり、EXP-0003Aの公開TaskSpec ID-v1として再利用しない。同一分割、同じprimitive版・予算・監査設定をfixture metadataに持つ。OFF/ONの双方でstatus=solvedの成否と独立audit verdictは一致すること。

| fixture task | OFF audited_correct / calls / candidates | ON audited_correct / calls / candidates |
|---|---|---|
| cal-t01 | true / 9 / 4 | true / 7 / 3 |
| cal-t02 | true / 12 / 6 | true / 17 / 7 |
| cal-t03 | false / 3 / 2 | false / 3 / 2 |

期待集計: task_count=3、OFF audited_correct=2、ON audited_correct=2、OFF candidate_count=12、ON candidate_count=12、OFF primitive_invocations=24、ON primitive_invocations=27、OFF_minus_ON_calls=-3。監査付き成功率は両arm 2/3（統計的推論なし）。paired unitは各cal-taskで厳密一致させる。失敗taskも費用合計に含める。

Normalized summary hashの対象は次の値だけを含むcanonical JSON（UTF-8, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False）である。元evidence hashとsummary hashを同一とみなさない。

```json
{"arm_totals":{"OFF":{"audited_correct":2,"candidate_count":12,"primitive_invocations":24},"ON":{"audited_correct":2,"candidate_count":12,"primitive_invocations":27}},"paired":{"OFF_minus_ON_calls":-3},"task_count":3}
```

expected SHA-256 = `0ef732ea2bc266d8d4da2139f665c0240fc1866d71e52a57151ba31f01e89373`。F02ではraw record順序を入れ替えてもこのsummaryとhashは一致。F03–F08はF01の一箇所のみを改変する反例として生成し、異なる失敗種別を予め固定する。source recordの実際のSHAはPR2のfixture作成時にimmutable evidenceとして保存し、事後に期待値を書換えない。
