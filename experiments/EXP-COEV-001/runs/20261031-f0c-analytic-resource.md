# EXP-COEV-001 F0-C: prospective paired power and PUBLIC resource harness

id: EXP-COEV-001-F0C-ANALYTIC-RESOURCE
status: ANALYTIC_DESIGN + INVENTED_ONLY_BENCHMARK; NOT_FROZEN; NO_SCORES
tags: paired-power, sensitivity, resource-preflight, invented-only
updated: 2026-10-31
parent: #115 / #110 / #106

## Analysis assumptions (pure math; NOT result)
Primary contrast: paired *task-level* exact-match improvement `D=I(C2 correct)-I(C0 correct)`, D in {-1,0,+1}. All audit64 outputs collapse to one all-correct binary per task. For N=2048 with independent identically distributed task sessions conditional on an independently frozen pool: two-sided 95% Hoeffding half-width `sqrt(2 ln(40)/2048) ~= 0.0600`, using D range 2. The proposed joint rule is **observed delta>=0.10 AND bounded 95% CI lower>0**.

Hypothetical normal approximation for true delta, discordance q=P(|D|=1): Var(D)=q-delta^2. Joint pass probability approximated as `Phi((delta-max(0.10,radius))*sqrt(N)/sqrt((q-delta^2)*DE))`, where DE in {1,2,4} is **hypothetical design-effect inflation** for sensitivity, not an estimated intra-class correlation. At true delta=0.10, pass probability is ~0.50 for every nondegenerate q/DE. At delta=0.12, pass probability is sensitive to q and DE. Run invented-only `illustrative_design_table()` with q={.20,.50,.80}, true delta={.10,.12,.15}, DE={1,2,4}. No real labels/target identities/official Oracle accessed.

**Statistical warning:** target class reuse means sampled task sessions are NOT new distinct semantic functions. An iid conditional fixed-class-pool inference may still be valid with independently drawn task sessions/contexts, but cannot imply population-level generalization to unobserved grammar classes. A class-level random-effects or cluster-robust inferential target requires additional independent preregistration and viable 358-class support; DE-only sensitivity is not a substitute. Rules for conditioning, family stratification, cluster consistency, failure-as-incorrect, analysis script, power and N remain subject to review before real TRAIN.

## Engineering resource preflight
Public script `python -m scripts.run_coev_f0c_resource_preflight --mode smoke|full` measures fresh/warm G1 Catalog, paired public synthetic TRAIN arms, candidate ranking and global Linux process VmHWM. No secret data, no evaluator or scoring. `smoke` uses 8 invented tasks per arm / 4 rank repetitions in allowlisted subprocess CI; `full` is bounded 256 invented tasks per arm / 32 ranks, opt-in and not a verified FINAL resource bound. Each phase reports wall and CPU seconds, *cumulative process* high-water RSS, environment and source world count. No benchmark number should be asserted until the exact source/runner is actually executed. Resource safety caps / worst-case 2048-task total still **NOT_FROZEN**, to be set after independent full/cold/warm measurements and reviewer evaluation.

## Remaining F0-C exit criteria
Prospectively choose (1) class-family sampling quotas and target estimand; (2) repetitions/cluster and CI method, (3) N/power vs 10 percentage-point threshold, (4) matched-capacity null controls and learning attribution, (5) actual resource hard limits; (6) exact code/seed manifest. This receipt is a score-free design artifact and does not authorize real TRAIN or FINAL.

## First actual GitHub CI full-public benchmark observation (2026-10-31)
- CI-SAFE-V2 run [#41191597779](https://github.com/ryonakayama234/DekaSugi/actions/runs/41191597779), exact head `6c18e1ab18bd9c2b771f3eb19df1bddcc8c6fc38`, 134 tests passed. This run preceded reviewer P3 zero-variance math fix; resource harness files and G1/TRAIN logic are unchanged by the P3 fix. New latest-head CI still required.
- GitHub-hosted Ubuntu/Linux Azure x86_64 (kernel 7.0.0-1017-azure, glibc2.43), Python 3.12.15, reported 4 logical CPUs. Single unreplicated process, hot OS caches and no independently measured load variance.
- Fresh `build_catalog()`: wall **0.207325 s**, CPU **0.207334 s**, VmHWM **26692 KiB**.
- Repeated cached `build_catalog()`: wall **0.000003 s**, CPU **0.000004 s**, process VmHWM still 26692 KiB.
- Synthetic TRAIN256 `random`: wall **0.127810 s**, CPU **0.127820 s**, cumulative VmHWM **27004 KiB**.
- Synthetic TRAIN256 `active`: wall **0.277281 s**, CPU **0.277251 s**, cumulative VmHWM **27284 KiB**.
- 32 repeated `recommend_programs` calls, 64 publicly consistent candidates: wall **0.120950 s** and CPU **0.120785 s** for all 32; cumulative process VmHWM **27336 KiB** (~26.7 MiB).
- The overall independent **CI suite** (tests plus validation) used ~9.67 s inside the test runner; those timings are NOT the same as per-arm source timings. Active query computation used ~2.17x random-arm CPU on this fixture despite requiring fewer Oracle question labels in earlier pilot.
- Peaks are cumulative `/proc/self/status:VmHWM`, not incremental per-step allocated bytes. A 256-task same-process invented fixture is neither 2048-target evaluation, nor proof of bounded worst-case CPU or memory, nor source-independent truth.
- Safe CI output is the primary evidence. Do not treat these single-run numbers as hard caps or claimed L3 learning generalization; measure variability, worst-case candidate and audit costs, and predeclare hard resource stop rules before F0 freeze.

## Independent reviewer P3 on zero-variance strict inequality
A reviewer found a valid degenerate edge `Design(tasks=8, alpha=2*exp(-4))`, Hoeffding radius exactly 1 and deterministic D=1. The previous `variance==0` branch used non-strict `D>=max(tau,radius)`, wrongly returning pass probability 1 even though CI lower=0 fails strict `>0`. Corrected to require separately `true_lift>=threshold` and `true_lift>radius`; new negative/boundary test covers N8 vs N9. The default N2048 result is unchanged. Re-review and new exact-head safe CI remain mandatory.
