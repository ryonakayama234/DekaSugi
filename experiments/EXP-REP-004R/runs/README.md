# EXP-REP-004R — run ledger
id: EXP-REP-004R-RUN-INDEX
status: NOT_RUN
updated: 2026-11-02
tags: experimental, run, evidence, planned

## 2026-11-02 — 設計決定稿候補
id: EXP-REP-004R-20261102-DESIGN
status: DESIGN_ONLY / NOT_IMPLEMENTED / NOT_TRAINED / NOT_SCORED / NO_FORMAL_F0
primary_module: packages/rep004
source_parent_commit: 24e660d8c6926a618595e4747917be59de35b602
parent_historical_score_sha256: 70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3
experiment_spec: docs/specs/EXP-REP-004R.md
experiment_plan: experiments/EXP-REP-004R/plan.md
note: A docs-only design proposal; no patch, no new learning Snapshot, no local USE execution and no scored trials. New dated immutable runs will be appended in the implementation PR.

## Execution authority (2026-11-02)
User approved implementation and end-to-end synthetic learning/use/re-scoring on a separate Draft implementation PR. No run is considered completed until CI and exported raw evidence are checked. Historical source and original 1,920 rows remain frozen. The CI evidence artifact contains all six corrected raw score dumps, snapshots, separate-process USE receipts and an aggregate summary; results and exact hashes must be appended in a distinct dated ledger after verification.


## 2026-11-02 — Corrected-engineering, activation-negative STOP (actual GitHub CI)
id: EXP-REP-004R-20261102-MECHANISM-STOP
status: P1_P2_ENGINEERING_PASS / H_ACT_FAIL / STOP_PRE_SCORE / NO_11520_SCORE
updated: 2026-11-02
tags: experimental, run, negative, evidence, preflight
primary_module: packages/rep004
issue: https://github.com/ryonakayama234/DekaSugi/issues/139
implementation_pr: https://github.com/ryonakayama234/DekaSugi/pull/141
proof_ci: https://github.com/ryonakayama234/DekaSugi/actions/runs/41405956872
proof_ci_independent_path: https://github.com/ryonakayama234/DekaSugi/actions/runs/41405596685

### Measurements performed
- Source-target-guard corrected RoleBinding and pure typed-AST matched all 60 valid atomic relations x all 24 permutations; all 16 Boolean pre-action states x four pulse actions were checked. This regression PASSED. Two-edge concurrent-XOR and 0-vs-64 STATIC-MACRO independence tests PASSED.
- The historical two-pulse public mechanism fixture changed from LQ pulse(3) vs LA pulse(2) (old erroneous source) to LQ pulse(2) vs LA pulse(2) after the repair (CI 41405053144).
- Searching 192 separate paid two-pulse public histories gave ZERO different first questions (CI 41405230005). An independently structured finite mechanism audit on 36 public semantic family instances x budgets 2/4/8 = 108 fully legal adaptive inquiry paths also found ZERO first LQ/LA question divergence (CI 41405596685); an optimized identical-public-prefix audit confirmed the same NULL in CI 41405956872.
- The resulting CI had **11 tests, 10 passed, 1 intentional required failure**: test_actual_first_paid_query_switch; receipt `NO_CAUSAL_ACTION_SWITCH_FOUND`. The negative is NOT a scored accuracy effect, and is NOT universal across all possible histories.
- `learn(64)`, `learn(0)`, small-training calls and limited Snapshot save/load occurred inside the unit tests. The planned six-exposure `G3 TRAIN→persist→fresh USE→G5 score` has NOT run, because its preceding gate failed. There are NO NEW 11,520 raw scores, six Snapshot archive set, corrected utility estimates or raw hashes.

### Interpretation
After repairing role binding, seven learned templates cover ALL atomic guard forms and ALL four two-edge motifs. Under `weights_for`, the resulting complete `learn(64)` prior is precisely a fixed structural complexity prior: 1 for empty, 4 for one-edge, 13 for two-edge candidate. STATIC-MACRO contains precisely the same seven templates. Consequently, at TRAIN64 the two policies have identical candidate prior weights; novel concept-body benefit beyond STATIC-MACRO is not identifiable under this representation. The old 78/240 action-switch statistic included role-position bias and cannot be used as validated concept-driven acquisition.
The modified source is a legitimate corrected engineering candidate, **not a validated new intelligence model**. No accuracy/retention benefit is attributed to it.

### Stop and provenance
G1 role invariance PASS; comparator independence PASS; original mechanism gate FAIL; expanded 108-path H-ACT gate FAIL. Follow fail-closed protocol: do not weaken activation assertion, run corrected full scoring, or promote to model release. Prior EXP-REP-004 raw 1920 records and SHA256 `70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3` are unchanged. A future inquiry-policy redesign or predicate invention requires a new experiment/method ID.
