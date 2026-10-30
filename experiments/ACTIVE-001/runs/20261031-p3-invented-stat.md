# ACTIVE-001 P3 — invented-only statistics numerical evidence ledger

id: ACTIVE-001-P3-SYNTHETIC-STAT-RUN
status: code_committed; exact_head_safe_ci_and_review_pending
updated: 2026-10-31
tags: active-learning, statistics, numerical-verification, synthetic, no-scoring

## Preparation and custody

Branch \`research/active001-p3-statistical-preflight\` based directly on scientific method draft PR #97 head \`d10195eda542d0b543722ab33a38207cbb16c8eb\`. No dependency on P0/P2 implementation and no change to P1 B1+, historical 2026-10-30 Gate-F counts, old frozen scored data, original disabled workflow or prospective auditor evaluator. New source \`packages/active_statistics/__init__.py\` and \`tests/test_active_statistics_synthetic.py\`, with only the latter added to the safe v2 CI allowlist.

## Required engineering checks

1. Reference exact Student-t critical quantiles (df1,df29,df4095).
2. Task-level bounded difference shape/type/mean/CI computations, null zero variance identified; 5 B1 replicates and 64 predictions never used as independent n.
3. Exact normal power planning approximation at N4096, analytically conservative Hoeffding sufficient N8138.
4. Deterministic invented Monte Carlo across N512/4096/8138: all-zero null, worst-variance null, positive +5pp, sparse +5pp, heavy-tail +5pp, negative -5pp; record simulated coverage, positive-claim rates and zero-variance cases. Monte Carlo uncertainty is material (100 replicates per setting).
5. CI log \`ACTIVE001_P3_INVENTED_STAT_RECEIPT=\` contains actual **invented simulation** results; source alone is not proof of CI execution/pass. The original method remains unfrozen.

**Actual scored ACTIVE-001 observations: ZERO.** Exact-head CI and external review results must be checked and subsequently referenced in the PR/Issue; do not invent empirical frequencies before seeing output. A successful check is numerical engineering, not independently validated inference, split custody, source-freeze or a signed Oracle.

[P3 method](../p3-inference-numerical-draft.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).

## Exact-head code-review finding and corrective policy (2026-10-31)
Codex reviewed original P3 head `99b3c0dad98acc866ef503cc63b982f0dc3851df` and found **P1: false positive** when an all-equal **positive** sample has zero sample variance. Example IID null: `P(D=1/9999)=0.9999, P(D=-1)=0.0001`. Original `paired_t_interval()` wrongly set `positive_evidence=True` on such samples. **Not scientifically acceptable**; original CI log is retained for provenance but the original implementation must not be treated as inferentially validated.
Corrective behavior: `zero_sample_variance` is `NOT_ESTIMABLE`, always `positive_evidence=False`, with vacuous known bounded mean limits [-1,1]. Simulations explicitly contain this rare-negative mean-zero law and must record zero false-positive claims for it under the tested seeds. Final acceptance requires NEW exact-head CI and fresh Codex review; do not claim the previous CI or review certifies the new commit.

## Follow-up numerical precision finding (2026-10-31)
Second Codex review of head `0912ba63ca706a339e36c20c4573d41d11783d71` found floating-point centering could bypass the zero-sample-variance guard: `(0.0059,)*8138` or `(0.1,)*3` yielded tiny nonzero variance and false positive. The corrective reference now detects **all exactly identical observed values before computing variance**, always returning `zero_sample_variance`/vacuous [-1,1]/no positive evidence. Add both exact regressions. A fresh exact-head safe CI and independent code review are mandatory; previous heads remain superseded, not proof of resolution.

## Third corrective review: underflow safety
Codex at `477b77530d71437062fc600e5af13fc2a993d189` found an **additional P2** false positive: `(0.,0.,0.,0.,6e-162)` had an underflowed standard-error term, unlike `(0.,0.,0.,0.,.6)`. The new code normalizes differences before squaring, restores the correct scale **after** calculating Student-t margin and fail-closes on nonrepresentable margins. Exact-head CI and Codex reviews must be checked anew; previous successful check runs are NOT evidence for the new head. All scientific task scores remain zero.
