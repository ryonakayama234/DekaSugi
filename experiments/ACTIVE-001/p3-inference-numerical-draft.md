# ACTIVE-001 P3 — numerical inference/power method preflight, invented only

id: ACTIVE-001-P3-NUMERICAL
status: decision_draft; NO_SCIENTIFIC_FREEZE_NO_SCORING
updated: 2026-10-31
tags: active-learning, statistics, iid, power, coverage, synthetic

## Task law and estimand

Primary proposed H1: under a **single future pre-frozen split** of 28/64/64 finite-world inputs, draw 4096 tasks IID *with replacement* as uniform semantic class × uniform unordered public pair, conditional on this split. For independent task i, measure B2's auditor-only exact-match fraction \`A_i(B2)\`, and the **mean of five B1 independent seeded replicate fractions on the same task**, \`bar A_i(B1)\`. Then \`D_i=A_i(B2)-bar A_i(B1) ∈[-1,1]\`. The independent unit is **task**, not five B1 draws, 64 auditor inputs or semantic class family. Same task law, including zero-F3 and null cases, no post-result exclusion.

The data do **not** exist in this P3 branch. All simulated D are invented from formulas, with no target, private label, official task seed, scorer, old frozen run or experiment source accessed. A single split means inference is conditional on that split, not transfer to arbitrary split/family/language/world.

## Two candidate inference approaches

1. **PR #97 primary draft: two-sided 95% Student t CI.** Use \`t_{n-1;0.975}\` numeric critical and empirical SD of N task-level differences; declare *positive evidence* only when the lower CI bound exceeds zero, independent of whether point estimate >+.05. For true mean Δ=.05 and worst possible SD≤1 from boundedness, the normal-asymptotic positive-evidence power is \`Φ(Δ sqrt(n)/1 - z_0.975)\` ≈0.892 at N4096. This **is not** guaranteed small-sample/non-Gaussian exact t power, joint adoption power, or independent scientific validation. Student-t can undercover for highly discrete/sparse cases. Treat **all constant samples** (including a strictly positive constant) as `zero_sample_variance` / **NO INFERENCE**: return a vacuous [-1,1] bounded-mean range with `positive_evidence=False`, not a zero-width t CI. This is necessary even if a sample mean is positive because a rare negative outcome can produce the same constant observed sample under a population null.
2. **Conservative distribution-free check:** Hoeffding for independent bounded \`D_i∈[-1,1]\`, two-sided CI \`bar D ± sqrt(2 log(2/alpha)/n)\`. For true Δ≥0.05, the sufficient lower-positive probability≥.80 follows from \`sqrt(n)*.05 >= sqrt(2 log(2/.05)) + sqrt(2 log(1/.20))\`, giving **ceil(8137.21484)=8138 independent task draws**. This is sufficient and very conservative, not minimal nor automatically adopted, and rests on IID/bounds/source independence. At 4096 the two-sided radius ≈0.04244067. Do not choose N after inspecting scored efficacy.

The two-sided CI is for a *single confirmatory contrast*, B2 vs mean-five B1. B1+−B1 and B2−B1+ remain secondary descriptive diagnostics unless a separately reviewed statistical family is committed **before** all outcome exposure. Do not replace null or negative outcomes with \`UNDERPOWERED\` retroactively or treat +5pp as an extra test.

## Verification and simulation scope

\`packages.active_statistics\` implements an independent pure-stdlib Student-t CDF inversion via incomplete beta (quantile tests for df=1,29,4095), bounded IID Hoeffding CI, normal-planning approximation and seven explicitly invented difference laws, including a mean-zero rare-negative adversarial distribution (positive 1/9999 with probability 0.9999 and -1 otherwise): all-zero null, symmetric ±1 null, symmetric ±1 +.05, sparse Bernoulli +.05, point-mass at 0 with positive/negative heavy tails +.05, and symmetric ±1 -.05. Monte Carlo repeats (100 in CI by default) at N=512,4096,8138 measure simulated CI coverage and positive-evidence frequency. These estimates are **noisy diagnostics**, not observed accuracy, certified power or bound validation. The analytic Hoeffding statement does not rely on these finite Monte Carlo counts. Negative and unfavorable results must be retained.

## STOP / adoption boundary

Before any real Stage-I evaluation: (i) independently verify task-generating law, label-source isolation, fixed split and seed commitments, (ii) approve CPU/wall/memory budget using P2 (plus separate direct B1+ and evaluator measurements), (iii) choose **one** CI and N and freeze before any target outcomes, (iv) use one-shot evaluator with complete missing/invalid evidence STOP and no optional stopping, (v) report all results even if null/negative. No self-review or Codex PASS substitutes for independent methodology proof; absent external human scientific review, claims must be limited to **single-team synthetic evidence**.

[Source](../../packages/active_statistics/__init__.py) / [Safe synthetic tests](../../tests/test_active_statistics_synthetic.py) / [Run receipt](runs/20261031-p3-invented-stat.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).

## Exact-head P2 numerical underflow correction (2026-10-31)
A further Codex review found that very small nonconstant differences, e.g. `(0,0,0,0,6e-162)`, could produce a positive but minimum-subnormal sample variance which becomes **zero after division by n**, silently generating a zero-width Student-t CI and a false-positive claim. The updated implementation computes squared deviations **after scaling relative to an observed reference**, takes the normalized standard error and t multiplier before applying the original scale, and marks unrepresentable/zero interval margins `precision_loss` with vacuous [-1,1] and `positive_evidence=False`. Tests compare the same shape scaled to `0.6`, include subnormal input and preserve constant-series guards. This is a numerical fail-closed policy, **not** a claim that Student-t has finite-sample distribution-free coverage.
