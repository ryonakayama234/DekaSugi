# OPPORTUNITY-001 — Learning Opportunity and Capability Boundary Research Plan v0.1

id: OPPORTUNITY-001-PLAN-V0.1
status: proposed_preregistration_not_frozen; design_only; not_run
updated: 2026-10-28
tags: preregistration-proposal, learning-opportunity, paired-evaluation, governance

> **重要**: これは実装着手前の精緻化された「事前登録案」であり、数値ゲート・新規生成器/seed・primary estimandを独立レビュー後の**別commit**でfreezeするまで確証実験の事前登録は成立しない。PR1では実装・生成・TRAIN/DEV/FINAL評価を実行しない。

## Hypothesis / hypotheses

- **Primary research question (design proposal)**: 固定skillと2arm、固定探索予算で、課題分布内に行動選択が正答/探索費用を変える余地がどれだけあるか。そのうち現行Kernelが取り逃がす部分はどれだけか。
- **H0**: 固定された課題分布で有効二択の取り逃がしは無い、または実用的な閾値を下回る。差の未検出を「0の証明」としない。
- **H1**: valid paired trialsで正答か正答時のprimitive callsが異なる課題がある。正確性差をcalls差へ換算しない。
- **H2**: 固定Kernelの学習前決定と事後best-of-twoで、監査付き正解機会または両正解時の費用に差がある。
- **H3**: 同じ公開8D特徴群に二択利得が矛盾する場合がある。衝突の存在を一般的な特徴不全の確証とはしない。
- **H4**: 両arm未解決の一部に探索予算不足または演算意味論の不足がある。ただし証明・予算内失敗・不明を峻別。
- **H5**: 学習データ取得費用を入れると、改善機会が存在しても償却費用は大きくなりうる。
- 研究後のAL-v2優位性・新技能獲得・領域転移は**本実験の確証仮説ではない**。

## Unit, estimand, outcome priority

- Unit: fresh public TaskSpec x fixed primitive/skill/policy/budget; paired OFF/ON independently audited.
- Fixed Kernel chooses before paired results; evaluator never provides final labels to chooser.
- Valid outcome strata: both-correct-ON-cheaper, both-correct-OFF-cheaper, both-correct-tie, ON-only-correct, OFF-only-correct, neither-correct, missing, invalid, non_comparable.
- Define `best_of_two` only as ex post best action among the two tested arms. Accuracy dominates cost, cost is compared only if both correct. Off is proposed default tie action.
- **Estimands**: choice_sensitivity_rate on valid tasks; missed-success/lost-success counts on one-correct cases; policy_excess_calls on both-correct cases; policy_decision_error_rate on uniquely better-arm cases; best_of_two_success_coverage as restricted diagnostic envelope; acquisition and inference costs reported separately.
- Zero is meaningful only for a measured equal result; missing/unknown/unfinished is never zero-imputed.

## Dataset design / 新規独立データ（候補、未確定）

- Pilot: **TRAIN-only** synthetic calibration + genuine fresh TRAIN paired cases, independently hashed, never using existing EXP-0003A DEV/FINAL task results. This stage estimates instrumentation/strata coverage, not confirmatory gain.
- Prospective split candidate: fresh TRAIN/DEV/FINAL with distinct seed namespaces, disjoint public TaskSpec hashes and independent reference third examples. Candidate sizes **TRAIN160 / DEV64 / FINAL128** are planning estimates, **not frozen**. A review must justify sample size with detectable effect and independent family/seed clusters; 8-family bootstrap alone cannot establish generalization.
- Pre-outcome generator strata: simple representable string transforms, compositional string transforms, deliberately hard/ambiguous public examples, and independently specified outside-DSL controls. Family allocation must be fixed *a priori*, **not** by retrospectively selecting tasks with large ON/OFF benefit. No test-time resampling based on measured outcome. Generated synthetic distribution is not human-use distribution.
- Start from existing pure `String -> String` grammar and fixed audited skill to isolate `policy choice`. Any expanded primitive/skill or changed budget is a **different experiment and causal intervention**, not an arm adjustment.
- All generator-private family labels, seeds, target transformations, and third-audit records remain evaluator-only. Train-only supervisor may receive explicitly allowed audited costs/teacher outcomes; DEV/FINAL data may not train or revise the policy.

## Controls, costs and comparability

1. OFF: canonical DEFAULT_PRIMITIVES only. ON: the same canonical primitives + one validated, same-body candidate skill, no automatic registry promotion.
2. Identical TaskSpec, independently allocated meter per task/arm, same `max_ast_nodes` expanded budget and `max_candidates`, same primitive/version/order, source-first hash check. Candidate exact limits to be fixed in preregistration; current EXP-0003A reference is max_ast_nodes=4 / max_candidates=100.
3. Third example independent audit; false-solved=0 is safety acceptance. No hidden audit/family to learner. Meter canonical as MEASURE-0001; total CPU/wall measured by separated phases and no double counting.
4. Kernel trial choice is recorded and sealed **before** evaluator computes paired outcomes. An arm may be better in hindsight but is not a feasible online oracle.
5. Reject run if frozen manifest/source SHA, split boundary, duplicate record, public/private isolation or canonical implementation changes unexpectedly.
6. METRO-0001 CAL-01 is artificial-fixture-only; a versioned real-evidence adapter and synthetic negative controls are required in a later implementation PR, not implied by the present design.

## Metrics / 必須記録（事前固定対象）

| metric | denominator / unit | policy |
|---|---|---|
| paired_valid | all fresh tasks / tasks | invalid, missing, non_comparable separately |
| choice_sensitivity_rate | valid paired / tasks per task | cost only when both correct |
| decision_error_rate | valid with a unique better arm / tasks per task | tie excluded |
| missed_success, lost_success | one-correct valid tasks / tasks | no calls-regret |
| excess_calls | both-correct valid tasks / calls | selected calls minus min(OFF,ON) |
| best_of_two_success_coverage | valid paired / tasks | retrospective 2-arm envelope |
| feature_collision_utility_disagreement | exact 8D collision groups / groups | exploratory, never raw private features |
| expressibility_evidence_levels | all tasks / tasks | proof vs bounded enumeration vs unknown |
| training, Dream, inference, evaluation, audit cost | phase-specific calls / CPU ns / wall ns | no cross-scope aggregation |
| uncertainty | task and independent family/seed clusters | point estimate + interval, all negatives |

## Acceptance / stop/go gates

**PR1 design gate (この段階で評価可能)**
- 仕様/図/契約/plan/run/索引/AGENTSを同期し、仮説と反証条件、母数、比較可能性、証拠不十分・失敗時の扱いを固定する。
- 既存EXP-0003A method/freeze/sourceを変えない。CIと独立latest-headレビューを経て docs-onlyで統合。
- 結果なしを `not_run` と明記。実装コード変更0件。

**Future methodology freeze gate (未承認・別commit必須)**
- Task generatorの正確な仕様、sample size/power assumptions、fresh seed/character partitions、固定 skill, budget, primary estimand, effect threshold, uncertainty and multiplicity handling, branch-decision thresholds を、**課題生成・結果観測より前**に固定。
- Positive outcomeを意図的に注入したfixtureは測定器の技術検査に限り、未知課題での能力証拠としない。
- Frozen research planは実測後に上書きしない。変更はv2とnew FINALで扱う。

**Future instrument gate (未実装)**
- TRAIN fixtureのみでstrict source/metric/hash, outcome precedence, two-arm comparator and meter invariance; independent review and CI. No DEV/FINAL in PR CI.
- Acceptability must include 100% identity/integrity for records actually evaluated, 0 unacknowledged missing, 0 cross-split leakage and 0 false-solved. Statistically valid effect size/branch threshold is separate from these engineering criteria.

**Future scientific gate**
- TRAIN pilot -> audited, frozen DEV engineering diagnosis -> **separate human authorization for fresh FINAL once-only evaluation**.
- If robust missed benefit exists, recommend separate AL/policy improvement experiment. If opportunities are scarce or unresolved because of grammar/budget, recommend skill invention/expressibility study. If underidentified, mark `inconclusive` and create fresh identification study.
- Never treat `best_of_two` coverage as deployed intelligence, a proof of general intelligence or a guarantee of learnability.

## Limitations, alternative explanations, stopping conditions

- Synthetic task strata can make apparent opportunity artificially abundant or scarce; publish strata allocation, denominators and generalization scope.
- Both arms solve no task: may reflect representation, search budget, ambiguity, examples, solver bug; cannot infer impossibility.
- A lower call count may be offset by training/Dream/policy CPU; practical advantage is not implied.
- Feature collisions can be harmless if utility labels agree. Selector changes do not imply policy changes or cost changes.
- If fresh-source/review gates fail or PRIVATE records leak to learner/repo, stop before evaluation and preserve failure evidence.

Related: [spec](../../docs/specs/OPPORTUNITY-001.md) / [Issue #56](https://github.com/ryonakayama234/DekaSugi/issues/56) / [METRO-0001](../METRO-0001/reviews/20261027-cal01-adoption.md) / [POLICY-DIAG-001](../POLICY-DIAG-001/runs/20261028-archive-public-diagnosis.md) / [runs](runs/README.md)。

## PR2 instrument calibration (not method freeze)
The pure fixture reducer accepts only `opportunity-fixture-v1` / SYNTHETIC / fx task IDs. Artificial positive/negative cases calibrate outcome precedence, missingness, strict provenance field shape and rejection of malformed input. This does **not** instantiate the fresh TRAIN/DEV/FINAL population or independently verify source bytes/audits/pretrial decision chronology. Scientific primary estimand and branch thresholds remain `not_frozen`; research trial count stays zero.

## TRAIN-only exploratory pilot method frozen before any outcome (2026-10-28)
- [Pilot-v1](pilot-v1.md) is the immutable method authority for future TRAIN64 exploratory measurements: 8 families x 8, master seed namespace 910000000, new alphabet, independent third example, canonical budget 4/100, source-locked EXP-0003A top skill and B1/B2/B3 decisions before OFF/ON.
- **Status**: method fixed, **source/manifest/provenance lock pending**, code and actual evidence adapter not implemented, no activation, TRAIN/DEV/FINAL new paired trials **0**.
- The plan-v0.1 larger prospective study remains an unfrozen proposal. Pilot heuristics do not freeze or authorize a confirmatory FINAL. Any result-driven change requires a different pilot method/seeds.

## PR4 implementation status (pretrial, no outcomes)
- The dedicated `opportunity_pilot` source implements PILOT-V1 generation, anonymous public TaskSpec IDs and public manifest SHA; tests may generate TRAIN public inputs without invoking search or auditing. New actual paired trials **0**, old DEV/FINAL untouched.
- This implementation PR is **not source/manifest freeze**. Following latest-head CI/review/merge, commit a separate pinned source/CLI manifest hash record **before any scoring**. Method edits require new method version/seed namespace, not opportunistic fixes after outcomes.
