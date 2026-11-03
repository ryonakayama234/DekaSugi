# EXP-REP-005 V4 G2b — two-part MDL and exact body-only ablation (disclosed engineering)

id: EXP-REP-005-G0B-B-G2B-MDL-20261103
status: engineering_pass_h_query_null_l3_source_overlap_stop
updated: 2026-11-03
tags: experiment, wake-sleep, snapshot, two-part-mdl, action-ablation, synthetic, non-confirmatory

## Distinct method from earlier G2a
This G2b version was developed **after the earlier G2a results were already disclosed**. It fixes two independent reviewer P1 objections: missing preregistered two-part MDL codec and BODY_OFF replacing the full candidate set with a memoryless-only model. The earlier [G2a receipt](20261103-v4-g2-disclosed-engineering.md) remains preserved as a method-noncompliant **engineering diagnostic**. This G2b result is another disclosed development calibration; its new codec cannot retroactively preregister old outcomes and G2b has no independent blinded study.

New method: MDL-C1-FIXED-BITS-V1-POST-G2A, pure stdlib Python, 61 candidate true-effect models (NULL and lag 0/1/2 x five sources x four distinct targets). The model code is 1 bit for NULL; or 1 effect prefix +2 lag bits + exactly five bits for each train-world source/target binding (20 ordered choices). Residual code is one match/exception flag per actually paid PublicStep, plus five XOR-residual bits for every mismatch. Ties, a NULL winner or winner needing exceptions => NOT_CERTIFIED; no retrospectively tuned weights. Model/response bit counts are mechanically recorded and replayable.

## Measured newer G2b dataset and codec selection
New train bindings (0->3), (2->4), (4->0) all with lag1; two separately reset 8-step episodes per training world = **48 charged TRAIN**. Actual code lengths:
- NULL: model1 + residual73 = **74 bits**, five wrong transitions
- lag0 effect: model18 + residual88 = **106 bits**, eight wrong transitions
- lag1 effect: model18 + residual48 = **66 bits**, zero wrong transitions => chosen
- lag2 effect: model18 + residual73 = **91 bits**, five wrong transitions

Resulting executable public-only body is previous_public_pulse(source_role,lag1) => XOR(target_role), with source/target bindings re-inferred from paid public new-world observations, not private Law. The typed Body and evidence digest are serialized as JSON to a **real filesystem file**, read back, validated as SHA-bound Snapshot and executed through a **fresh Python -I subprocess** with only public JSON messages. This is not a hard OS sandbox.

## Latest exact-head tests and artifact
- [G2b dedicated CI 41564186131](https://github.com/ryonakayama234/DekaSugi/actions/runs/41564186131): **8 tests PASS**, exact test/learner/runner head 4ee0e26d913611410902b4188afce6c67142dfdb.
- [Research verification v2 41564186084](https://github.com/ryonakayama234/DekaSugi/actions/runs/41564186084): PASS on same head.
- [Archived public-only Snapshot file + full raw disclosed report, artifact 13197918123](https://github.com/ryonakayama234/DekaSugi/actions/runs/41564186131/artifacts/13197918123), 30-day GitHub artifact retention.
- New use-role assignments (1->2), (3->4), (4->3) — **same lag1 causal motif as TRAIN**, so structurally/source ancestrally correlated.
- Three new world instances × 3 arms × 8 charged interventions = **72 USE**, total **120 actual TRAIN+USE charged operations**.
- Each world/arm scored on identical source-blind evaluator-only panel of 16 reachable legal probes, not passed to learner as ground truth.

| Arm | Correct /48 | Wrong /48 | Abstain /48 | U=(correct-wrong)/48 | Paid USE |
|---|---:|---:|---:|---:|---:|
| LEARNED public typed lag1 Body | **46** | **0** | **2** | **0.958333** | 24 |
| STATIC full same 61-candidate envelope / myopic entropy active | 42 | 0 | 6 | 0.875000 | 24 |
| BODY_OFF same trained Snapshot and posterior, only effect-body disabled | 42 | 6 | 0 | 0.750000 | 24 |

LEARNED minus STATIC: **+0.083333**, explained by exactly four more correctly answered problems and four fewer abstentions; **both have zero erroneous accepted predictions**. Per related new-world instance LEARNED/STATIC: (1.0/0.8125), (1.0/0.8125), (0.875/1.0); **LEARNED loses in the third world**, and this case must remain in the report.

### Stronger body-only causal test
At each of 24 learned-world paid public prefixes, the code compares Body ON/OFF with the **same prefix, SHA Snapshot, candidate set/weights (uniform), role-binding alternatives and query budget**, changing ONLY typed effect execution. It recorded:
- **10/24** true predictive dispatch mutations
- **0/24** legal query-action switches
- **24/24** equality of candidate-support count under ON/OFF

Hence direct use of the learned temporal effect changes predictions on the *same observed evidence*, but **H-QUERY remains NULL**, not an action-selection improvement. This corrects the G2a ablation, which improperly removed candidates. The BODY_OFF arm is an intentionally low-expressivity mechanism ablation and cannot replace the fair STATIC-Hplus comparator.

## No scientific promotion: explicit STOP
All use instances are object-role variations of the same lag1 training mechanism; their distinct names and object bindings do **not** yield independent source/semantic family-level samples. The 48 probes are correlated, not N=48. The G2b codec was created after G2a diagnostics, so this is not a new preregistered confirmatory holdout. Fixed active is myopic and not proven optimal, and actual CPU/RSS/inference cost parity is not certified. Learned incurs **48 paid TRAIN actions** beyond STATIC; with only three USE worlds this is 16 additional TRAIN steps per use-world, not an amortized lifetime benefit. No full two-edge/guard, M2/M3, unseen motif, out-of-language, dialogue/game/app, neural epochs or open-ended primitive concept invention was evaluated. G3 independently powered and sealed scoring: **NOT_RUN**.

Result classification: G1/G2b engineering working proof-of-mechanism; descriptive within-motif prediction-coverage gain; H_QUERY_NULL; H_XFER_SOURCE_OVERLAP_STOP; G3 NOT_RUN; no model promotion or main merge. Independent exact-head methods/security review and a truly independent source-family population remain gating requirements.

Related: [G2a earlier run](20261103-v4-g2-disclosed-engineering.md), [integrated V4 design](../../../docs/specs/EXP-REP-005-G0B-B-INTEGRATED-DECISION-V4.md), [G0 receipt](20261103-v4-g0-code-pending.md), [stacked PR #157](https://github.com/ryonakayama234/DekaSugi/pull/157).

## Independent reviewer P1: archive all 48 paid TRAIN public steps (2026-11-03 amendment)
Codex correctly noted that the first G2b CI artifact archived only the Snapshot and use-report summary, **not the actual 48 public TRAIN observations**. A digest without the input records is insufficient for independent recomputation of the MDL residuals or evidence SHA. Code now includes an exact allowlisted training_public_episodes_raw list (6 chronological episodes /48 paid observations) in the evaluator report artifact; the regression recomputes SHA-256 with the learner's exact canonical JSON encoding and asserts identity to Snapshot evidence_sha256. It asserts the corpus has no secret Law/source fields. This is an archival/integrity remedy, not a new training distribution, model selection change or scientific benefit. Earlier artifacts remain untouched; the newest exact-head CI and artifact must be independently verified before claiming complete raw auditability.


## Raw TRAIN audit fix — executed verification
The corrected [G2b dedicated CI run #41565074071](https://github.com/ryonakayama234/DekaSugi/actions/runs/41565074071) passed **8 tests**, explicitly verifying that the public-only report includes **6 chronological TRAIN episodes, 48 actual paid PublicStep records**, no private Law/source fields, and that independently recomputed canonical SHA-256 of the original public records equals Snapshot evidence_sha256. New [artifact #13198720547](https://github.com/ryonakayama234/DekaSugi/actions/runs/41565074071/artifacts/13198720547), size 5,149 bytes, contains the actual public-only Snapshot JSON and full disclosed run JSON with raw TRAIN+USE records. The old [artifact #13197918123](https://github.com/ryonakayama234/DekaSugi/actions/runs/41564186131/artifacts/13197918123) lacked raw TRAIN records and remains preserved as a historical incomplete audit. Neither artifact includes private source Law. Final scientific status stays source-overlap STOP and G3 NOT_RUN; archival reproducibility correction is not new model gain.
