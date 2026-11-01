# EXP-REP-002 — disclosed direct-only pilot, actual measured result
id: EXP-REP-002-DIRECT-PREFLIGHT-20261101-MEASURED
status: DISCLOSED_ENGINEERING_CI_PASS; MECHANISM_NOT_ATTRIBUTED; NOT_FORMAL; NOT_H4
updated: 2026-11-01
tags: experiment, synthetic, active-learning, negative-result, reproducibility
source_run: https://github.com/ryonakayama234/DekaSugi/actions/runs/41314971904
source_commit: 7f32b8b6b2085442bd16e43a3880306b1ab323ec
raw_result: 20261101-direct-preflight-measured.json

## Measured engineering execution
The explicitly allowlisted CI tests completed with **150 PASS** on exact source head (G1-D predecessor tests plus seven new rep002 tests). Programmatically generated TRAIN 0,3,8,16,32,64 and corresponding immutable JSON-compatible snapshots. Distinct full-graph structures saturate at **3** by n=3; the remaining named TRAIN worlds only vary the same three structures and role permutations. The learned executable direct-role prior is (hub->x, hub->y), learned at n=3 (3 distinct full graph topologies) and unchanged through n=64.
TRAIN n=64 invokes 320 paid pulse actions. Final digest `86216e36a28b22bf713e3c11be505216c51fa4f9d2c7fa6ce51ed6d044cf2ab0`.
The evaluated 48 worlds cover four fully disclosed synthetic strata × 12 worlds, 4 arms (LQ/LA/LR/FA), 4 fresh-session action budgets (0,2,4,8) and 32 auditor-owned state/action queries per world. Arm metric is unweighted mean per-world exact-vector scores across four budget horizons, called AULC in this protocol. Score records digest: `62e3109633419da4cd56eb3c7c33a59f5c8c66d52fd4ddd8265ea1d740937494`.

## Per-stratum average AULC
| Stratum | LQ concept-aware question | LA concept-blind question | LR no body | FA fixed public-hub heuristic | LQ-LA |
|---|---:|---:|---:|---:|---:|
| COMPOSITION | 0.822266 | 0.794271 | 0.794271 | 0.822266 | +0.027995 |
| RENAMED | 0.904948 | 0.903646 | 0.851562 | 0.904948 | +0.001302 |
| NOVEL | 0.665365 | 0.666016 | 0.664062 | 0.665365 | -0.000651 |
| DISTRACTOR | 0.788411 | 0.808594 | 0.720703 | 0.788411 | -0.020183 |

COMPOSITION world-paired differences (LQ-LA) are stored individually in the machine-readable JSON (12 independent *world entries under this designed fixture*, not independent random graph families).
Total test-arm charged pulse actions: 2,112. Total test-arm expanded node counter: 9,363. One CI runner's `evaluate()` process CPU measured ~320.555 ms at the final-source run; includes recomputing TRAIN curriculum and in-process audit, is **not** total CI runtime nor a hardware-independent performance claim. The activity totals refer to the evaluated arms and are not an all-lifetime metering certificate.

## Critical negative mechanism attribution
**LQ = FA exactly in every world stratum.** Both choose the publicly disclosed 'hub' marker first; FA uses no persistent learned concept. The measured +2.7995 percentage-point composition advantage of LQ over LA therefore does NOT demonstrate concept-body-specific inquiry gain, and it falls short of the previously floated +5 percentage-point engineering practical target. This is a documented negative result about attribution. The complete reduction has a public role shortcut and intentionally narrow grammar; the pilot is not a test of autonomous novel semantics.

## Limitations and what remains unimplemented
- Only 3 genuinely distinct TRAIN full-graph topologies. No evidence of continued abstraction growth with 8/16/32/64.
- The pilot uses a fixed human-authored direct-XOR grammar and a single paid pulse. No gated conditions, no two-step paid state setup, no bounded full H4 hypothesis enumerator or genuinely optimized learned query planning.
- Even when canonical graph structure changes, this code does NOT yet establish the stricter negative-transfer behavior equivalence strata demanded by the independent design review.
- Public role labels carry most of the actionable source-selection information. A fixed heuristic copies the new agent's choice.
- Same-process synthetic host/evaluator is not independent source custody; 32 private-in-code audits/world are not 32 independent samples. Repeat synthetic entries belong to only a few topological families.
- Model commit selection and expanded primitive budget are bounded within this pilot, but the full shared search/AST cost protocol from reviewed design remains unimplemented.
- No sealed DEV/FINAL, no formal preregistered effect/power test, no automatic baseline promotion or PR merge.

## Scientific and engineering decision
ENGINEERING CALIBRATION PASS, provided exact-head independent review finds no new blockers. **H-Q is NOT established**; classify current primary effect as PUBLIC_ROLE_HEURISTIC_SUFFICIENT. Because the strong FA control matches LQ, next work must obscure or vary superficial role labels and test concept-informed *discriminating* questions across behaviorally distinct context-gated worlds with a single audited shared resource ledger. Do not cherry-pick the favorable composition stratum to claim intelligence gain. Prior negative outcomes remain immutable.
