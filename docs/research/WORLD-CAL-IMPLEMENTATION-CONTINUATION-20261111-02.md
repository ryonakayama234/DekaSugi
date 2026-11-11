# WORLD CAL PR #206 — implementation continuation and audit ledger

id: WORLD-CAL-IMPLEMENTATION-CONTINUATION-20261111-02
status: SYNTHETIC_ID_REPRO_PASS / K0B_UNKNOWN / K0C_UNKNOWN / CPU_STOP_UNKNOWN / NOT_FINAL_AUDIT_PASS
updated: 2026-11-11
tags: world-expansion, world-cal, research-lead, synthetic-audit, no-cal, implementation-go

## Authority and unchanged boundaries

Normative five settled RQs: [supervisor PR #206 intermediate audit comment 6794959589](https://github.com/ryonakayama234/DekaSugi/pull/206#issuecomment-6794959589). Owner's existing implementation GO continues. No CAL, actual power simulation, K0 production full search, sealed split, secret seed generation, real holdout evaluation, algorithm_digest fixing, FROZEN or CAL_AUTHORIZED occurred.

## RQ implementation record

| RQ | Candidate change | Source/test disposition |
| --- | --- | --- |
| 01 tokens | Errata document; 10 non-INSERT + 4 INSERT = **14 concrete actions**; distinct from 24-step horizon | Verified |
| 02 PRF u boundary | u>=1 binary64 -> nextafter(1,0); u<=0 and other invalid endpoints -> STOP_UNKNOWN | Verified |
| 03 B contrast | Each arm's two B-family successes equally averaged, global FULL-max(seven controls) AFTER HT on SAME Y; family contrasts descriptive only | Verified |
| 04 Sampford | Exact algebraic two-mass group count; certainty separation; rational independent cross-check every n=2..336 | Local CI verified, supervisor independent check outstanding |
| 05 CPU | Complete structural ONE synthetic repetition with PPS/Gtheta/999 cluster bootstrap/max-T/10-AND, optimized parent HT caching | Measured; STOP_UNKNOWN |

## Source-only N=336 numerical evidence

[CI run 43028909813](https://github.com/ryonakayama234/DekaSugi/actions/runs/43028909813), CPython 3.12.16, Ubuntu 24.04 x86_64, glibc 2.39: source-implied PUBLIC q multiset: 72 units 1/160 + 264 units 1/480; checked 335 integer n in 2..336. Minimum pi_ij 8.682158274646867e-06; maximum reported numerical residual 1.4210854715202004e-13 (tol=1e-10). Each n's pair positivity, identity and exact Fraction reference comparison is in the workflow audit JSON artifact. No actual law-ID/q allocation or parent assignment was materialized.

## CPU feasibility: measured but unresolved

At synthetic n=96 on Intel Xeon Platinum 8370C @ 2.80 GHz (4 CI CPUs assigned; CPython 3.12.16; PYTHONHASHSEED=0, OpenBLAS one thread): wall 1.293906738 seconds, CPU 1.293843446 seconds, ru_maxrss 24,076 KiB. Complete one repetition used public non-secret constant key, a synthetic parent layout, all six Gtheta factors and 999 actual bootstrap replicates. This is not the CAL or a full power-simulation run. The linear-in-n arithmetic all-scan extrapolation is **6,358.9002 wall-hours (~265 days)** for all n, three scenarios, MC_R=10,000; it is only a scenario, not a validated runtime prediction and excludes early successful stopping. The cached per-parent HT bootstrap acceleration preserves draw count and arithmetic order and is covered by a bitwise synthetic equality test. The worst-case budget remains unrealistic; further optimization/resource planning or separately authorized protocol revision is necessary, **feasibility=STOP_UNKNOWN**.

## Synthetic OS access-boundary evidence

The same CI exercised isolated bubblewrap LEARNER_ARMS and EVALUATOR processes with read-only role-specific mounts and isolated user/PID/network/mount namespaces (sudo needed on the GitHub runner). Synthetic allowed reads succeeded; cross-role read attempts failed. Role stage bytes are SHA-pinned and closed, and the learner executable code bundle rejects abstract oracle code and unlisted non-code data. This is implementation-side negative evidence, not independent supervisor PASS or production custody certification.

## Remaining blocking work (no premature PASS)

1. K0-b: exact bounded public-history TRAIN-feedback/EVAL-no-feedback law-pair DP is coded, with lazy registered abstract generator support. Complete certified law-pair/instance enumeration is NOT shown; K0-b remains UNKNOWN.
2. K0-c: bounded shortest-path, L90 and guarded oracle candidates exist, but complete typed Space enumeration and exact best-control/oracle policy curves are NOT proven exhaustive. K0-c remains UNKNOWN.
3. ID-only: four tag-byte features, five parent folds, L2 C=1 multinomial logistic, OVR macro AUC and 999 label-permutation classifier exist. CAL-real tag reissuance and PRF permutation inputs are forbidden before CAL_AUTHORIZED; end-to-end independent ID-only reproducibility audit remains unproved.
4. Integrated scan: guarded future n-ascending, MC_R=10,000, 3 scenarios, 999-resample pathway is present but NOT executed. n=2 numerical/cluster degeneracy and correct STOP behavior require separate independent review; no optimistic skipping is authorized.
5. CPU wall feasibility remains STOP_UNKNOWN. This document does not confer CAL_AUTHORIZED or permission to execute production K0/simulation.
6. Candidate algorithm source manifest must match final exact head, followed by independent source/access/numeric/environment audit; algorithm_digest remains null.

This is explicitly a lead implementation continuation report, NOT a completed implementation PASS or a final supervisor verdict.

## Supervisor progress-audit-2 follow-through (source-only / 2026-11-11)

- Reference: [supervisor comment 6797428860](https://github.com/ryonakayama234/DekaSugi/pull/206#issuecomment-6797428860).
- [Coverage and reproducibility self-audit](WORLD-CAL-IMPLEMENTATION-COVERAGE-AUDIT-20261111-03.md) records a source-index bijection, all registered phase index counts, exact rational mass and 73,536 canonical distinct-law pairs, plus the hard obstruction to literal full typed-Space enumeration (`14^63` distinct legal size-64 SEQ/ATOM strings). This is **not** an executed pair×demo×trial K0-b search nor a complete K0-c oracle/control curve.
- Bounded K0-b and K0-c wrappers now reject caller-provided boolean "complete" claims and maintain UNKNOWN without complete iteration receipts; tests cover those negative cases.
- Synthetic ID-only audit now exercises all 999 injected permutations through the complete classifier, twice in fresh processes per environment, on Ubuntu 22.04 and Ubuntu 24.04 with exact output-byte digest agreement. CI [43033546871](https://github.com/ryonakayama234/DekaSugi/actions/runs/43033546871). CAL-real tags and PRF schedules were neither generated nor audited.
- CPU feasibility is still STOP_UNKNOWN. Existing `scan_authorized` has **no hardware wall-budget timer**; the 20,000,000 cap is a primitive-call cost bound checked after completing an n. An external time/CPU budget interruption before all three scenarios×10,000 repetitions for some n provides no completed eligible n and must result in STOP_UNKNOWN, not an optimistic later-n selection. No further measurement or optimization.
- No final completion claim: K0-b full joint demo/trial/instance histories, K0-c full typed Space/control curves and CPU feasibility remain blocking. Draft, null algorithm_digest and no CAL/K0 production execution are unchanged.
