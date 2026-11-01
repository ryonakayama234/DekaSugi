# EXP-REP-001 G1-D — Template constructor & active query final toy pilot
id: EXP-REP-001-G1D-TOY-20261101-V2
status: SYNTHETIC_ENGINEERING_PASS; NO_FORMAL_TRAIN_DEV_FINAL; NOT_PROMOTED
updated: 2026-11-01
tags: experiment, synthetic, representation, active-learning, learning-curve
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/128
pr: https://github.com/ryonakayama234/DekaSugi/pull/129
tested_code_head: b070964dfafc7687b2e02bbb6489b8ab9f36a0f8
ci_run: https://github.com/ryonakayama234/DekaSugi/actions/runs/41305507637

## Execution / scientific status
CI job verify-synthetic-and-source PASS on tested code head. 142 tests successful, including original source-byte/freeze integrity, documentation, explicit synthetic allowlist, malformed inputs, bounded search, deterministic replay conflicts, charged state operations, canonical role invariance, Snapshot tamper/reload, actual role-body model instantiation, CLI train/inspect/use and public toy scoring. No old or sealed source/generator was run, scored or modified. No automatic merge. This is NOT independent or preregistered scientific testing.

Host and learner remain in one Python process. Toy auditor privately uses the host object in code but this is NOT an independently controlled process or custody. No claim of protected heldout data is made.

## Toy worlds and training
- TRAIN: 32 named Boolean 4-object worlds whose *graph shape is the same two-direct-edge fork*, with object IDs and role index varied. 3824 total paid TRAIN operations, including set_state and pulse; no free arbitrary-before learner probes.
- Eval: 6 disclosed worlds, four direct fork and two gated mixture. Passive transcript contains 4 charged pulse actions/world and is exactly shared by B0/B1/B2/B3/B3x/B4. B5 chooses distinct public observations with 3–4 charged actions/world, never >4. Auditor privately scores 64 next-state Boolean vector transitions/world = 384 audits/arm.
- Independent structure separation is absent: toy fixture is favorable by design, NOT evidence of true-world transfer or statistically independent generalization. Same process cannot protect secret targets.
- B4 is strict exact-instance retrieval and therefore weak against renamed object IDs. It is NOT the strong episodic control required for F0.

## Measured paired toy outcome
| Arm | Exact correct / 384 | Abstentions | Candidate checks summed over six new-world inferences | Inference CPU ns on one CI runner |
|---|---:|---:|---:|---:|
| B0 limited one-edge | 112 | 256 | 366 | 6,939,028 |
| B1 fixed two-edge | 368 | 0 | 7,446 | 11,619,283 |
| B2 learned rank-only | 368 | 0 | 7,446 | 12,018,066 |
| **B3 learned executable two-atom role-body prior** | **368** | **0** | **414** | **8,311,632** |
| B3x body removed | 368 | 0 | 7,446 | 12,139,954 |
| B4 strict episode retrieval | 0 | 384 | 0 | 288,287,187 |
| B5 body-enabled + active queries | 384 | 0 | 3,978 | 10,716,149 |

Candidate checks B3 vs B1: (7446 - 414)/7446 = 94.44% fewer. Instrumented inference CPU B3 vs B1: 8.312ms vs 11.619ms, approximate 28.5% lower on this ONE small noisy CI run. Inference CPU excludes TRAIN and full toy pilot setup, so do not claim total-lifetime amortized CPU advantage. CPU time includes different model-selection and episodic lookup implementation costs. The overall pilot itself used 9,095.011ms process CPU / 9,095.556ms wall, including training setup, learning curve, repeated fixed public eval and active probe search.

The B3 body is an **executable typed hypothesis constructor**: after a validated H1 class mismatch, roles in learned [[0,1,-1,true],[0,2,-1,true]] bind to new public object IDs, instantiate a bounded set of new-world H2 candidates, and filter them against every observation. If none fit, it falls back to fixed H2 bounded search. This is stronger than a mere label/rank prior but remains completely inside a HUMAN-PROVIDED two-relation meta-grammar. A good fixed H2 search heuristic could provide similar savings; the causal claim here is relative only to the **implemented matched comparator**, not to an optimally tuned solver.

## Learning trajectory (distinct experiences, NOT epochs)
| Unique named TRAIN worlds | 0 | 1 | 2 | 3 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|
| Persisted templates | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 |
| Support for fork role body | 0 | 0 | 0 | 3 | 4 | 8 | 16 | 32 |
| B3 correct out of 384 | 368 | 368 | 368 | 368 | 368 | 368 | 368 | 368 |
| B3 candidate checks | 7446 | 7446 | 7446 | 414 | 414 | 414 | 414 | 414 |
| B1 candidate checks | 7446 | 7446 | 7446 | 7446 | 7446 | 7446 | 7446 | 7446 |

Role body digest at n=32:
783fb01764e7ea5e4dd3055eaaa7c3a2dd304e613495f0035fcbea6caaca4858.
Repeating identical public TRAIN observations 1, 2, 5 and 10 passes yields the exact same digest. This is deterministic idempotence, not SGD gradient training or evidence of learning from mere repetition.

## Model-class diagnosis and active acquisition
- Passive B0/B1/B2/B3/B3x see four fork worlds in H1 MODEL_CLASS_MISMATCH and two gated worlds UNDERIDENTIFIED (H1 fits the observed subset). No model can honestly infer inaccessible context structure from their particular passive evidence.
- B5 runs a deterministic max-diversity-of-hypothesis-predictions / charged-cost query heuristic, constrained by live reachable states. For all six disclosed eval worlds it obtains an H1 mismatch certificate with 3–4 paid actions; two gated worlds are therefore identifiable enough for the two-edge solver and 384/384 audits are correct.
- B5 is **not** an identical-observations comparison to B3; its 16 correct-audit advantage is compatible with better ACTIVE information acquisition, NOT with body-specific representation gain. This is an engineered fixture, not a confidence interval.

## Verdict / falsification
- Engineering end-to-end train/snapshot/load/use/toy score: PASS.
- H-D1 diagnostic statuses and H-D2 bounded two-edge repair: PASS on constructed examples only.
- H-D3 body-specific accuracy uplift: **NO** (B3=B1=B2=B3x at 368/384, 0 percentage point improvement).
- H-D3 body-conditioned search effort reduction: **YES relative to the implemented fixed/exhaustive baseline** (414 vs 7446 candidate checks after n>=3). It is NOT a new-primitive semantic discovery, a formal transfer claim, or optimal search proof.
- H-D4 active knowledge-acquisition effect on disclosed toy: YES (384/384 vs passive 368/384, with same max 4 charged actions but distinct query transcripts).
- F0 independent protocol/data custody, structural splits, strong episodic comparator, formal one-shot FINAL and promoted reference: NOT DONE. They remain *separate future gates* requiring owner approval and independent review. No implicit permission to run FINAL or merge draft stack.

The earlier dated engineering pilot file records the **previous rank-only B3 implementation** at commit 926573a; it must not be overwritten or passed off as the final template-constructor measurement. This V2 record is the current measured engineering baseline.
