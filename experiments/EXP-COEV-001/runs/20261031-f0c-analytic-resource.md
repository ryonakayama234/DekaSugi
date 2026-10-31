# EXP-COEV-001 F0-C: prospective paired power and PUBLIC resource harness

status: ANALYTIC_DESIGN + INVENTED_ONLY_BENCHMARK; NOT_FROZEN; NO_SCORES
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
