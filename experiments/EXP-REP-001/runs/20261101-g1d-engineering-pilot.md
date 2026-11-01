# EXP-REP-001 G1-D — Disclosed engineering pilot
id: EXP-REP-001-G1D-ENGINEERING-20261101
status: ENGINEERING_PASS; DISCLOSED_SYNTHETIC_ONLY; NO_FORMAL_TRAIN_DEV_FINAL; F0_NOT_FROZEN
updated: 2026-11-01
tags: experiment, synthetic, representation, active-learning, learning-curve
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/128
pr: https://github.com/ryonakayama234/DekaSugi/pull/129
source_commit: 926573a4a5d0c0dcae30c8e20721e9c14188f8df
ci_run: https://github.com/ryonakayama234/DekaSugi/actions/runs/41304826825

## Source / custody and what was actually executed
GitHub Actions successor safe CI: source-only freeze integrity passed, documentation validation passed, explicit synthetic-only test allowlist passed. 140 tests executed successfully. The G1-D unit test runs the whole disclosed toy pilot and prints machine-readable G1D_TOY_RESULT into the workflow job log. No historical generator/DEV/FINAL used; no independent evaluator custody. Host and learner share an in-process Python address space; all toy TRAIN/eval structure is visible in source.

Implementation: packages/rep_lab/__init__.py, packages/rep_lab/__main__.py, tests/test_rep001_g1d_engineering.py, scripts/run_research_ci_v2_tests.py. Uses only CPython 3.12 standard library, existing packages/relational_world and packages/world_model primitives. Legacy G1-C modules and historical frozen sources remained unchanged.

## Public toy protocol and non-independence
TRAIN: 32 object-renamed, 4-object, deterministic, directed two-direct-edge **fork** worlds; identical structural topology. Training visits 16 Boolean before-states x 4 pulse sources per world, with all state changes paid as set_state actions, total TRAIN action count 3824. No SGD or meaningful epoch is performed.
Evaluation: six entirely disclosed new-alias worlds, four same fork topology + two different gated-mixture topology. 64 evaluator-owned audit transitions/world; 384 audit transitions/arm. Passive B0/B1/B2/B3/B3x/B4 receive identical 4-pulse public transcript/world; B5 chooses its own 3–4 charged actions/world with no more than four total operations including setup. This is NOT a structurally-disjoint formal heldout or a secret test.

B0 one-edge only, B1 fixed expressive two-edge, B2 learned atomic family ranking, B3 learned executable two-atom body prior, B3x body removed, B4 **strict exact-instance retrieval**, B5 B3+active query selection. B4 is deliberately weak against object renamings, not the strong retrieval baseline required by formal F0.

## Observed machine measurements (not a scientific confidence interval)
| Arm | Exact-vector matches / 384 | Abstentions / 384 | Sum model candidate checks | Inference CPU ns (one CI runner) |
|---|---:|---:|---:|---:|
| B0 one-edge | 112 | 256 | 366 | 7,578,154 |
| B1 fixed two-edge | 368 | 0 | 7,446 | 12,672,230 |
| B2 learned rank-only | 368 | 0 | 7,446 | 13,050,134 |
| B3 learned body | 368 | 0 | 7,446 | 16,561,012 |
| B3x body ablation | 368 | 0 | 7,446 | 13,649,551 |
| B4 exact episode | 0 | 384 | 0 | 300,347,860 |
| B5 active query | 384 | 0 | 10,986 | 13,554,294 |

Note: CPU inference measurements are small, process/runtime/noise dependent, and not strong multi-run performance evidence. B4 includes repeated episodic lookup per audit; other arms freeze an inferred per-world model. Differences in implementation and the **different B5 public transcript** prohibit cross-arm resource causal claims without further normalization. The pilot's overall CPU 9,381.720 ms and wall 9,382.797 ms include synthetic data construction, learning-curve training, active-query search, scoring and test-side orchestration of the pilot.

## H-D1 and H-D2 observations
- A bounded, **complete** one-edge hypothesis search flags MODEL_CLASS_MISMATCH for all four disclosed fork evaluation worlds under the passive transcript; the two gated-mixture worlds remain UNDERIDENTIFIED under passive evidence. This is expected given the constructed fixture.
- A valid two-edge model can be identified for exhaustive public train transcripts (unit tests including exact role renaming and gated models).
- Insufficient evidence vs search budget exhaustion vs malformed observations vs contradictory deterministic replays are tested separately; none constitutes a broad-world diagnostic accuracy estimate.
- Learner-facing state preparation is charged; toy auditor-only arbitrary-state probes remain out of learner transcripts.

## H-D3 learning dynamics and negative result
| Different TRAIN worlds n | 0 | 1 | 2 | 3 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|
| Persisted two-atom templates | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 |
| Template distinct-world support | 0 | 0 | 0 | 3 | 4 | 8 | 16 | 32 |
| B3 toy exact-vector matches / 384 | 368 | 368 | 368 | 368 | 368 | 368 | 368 | 368 |
| B5 toy exact-vector matches / 384 | 384 | 384 | 384 | 384 | 384 | 384 | 384 | 384 |

The learned canonical body is the disclosed fork roles [[0,1,-1,true],[0,2,-1,true]]; B3 does not outperform B1 fixed two-edge, B2 rank-only, or B3x body-removed even after this body is learned. **Conclusion: no positive evidence that acquired body caused any accuracy improvement; fixed expressive grammar suffices for this toy, and ranked policy-only mechanism is not excluded.** This is an IMPORTANT negative attribution result, not a failure of code functionality.

Repeated replay of the SAME 32 public worlds at 1,2,5,10 passes yields the same snapshot digest 783fb01764e7ea5e4dd3055eaaa7c3a2dd304e613495f0035fcbea6caaca4858. Repeated identical exposure isn't gradient-based epochs and cannot be counted as new independent support.

## H-D4 active action effect, qualified
B5 reached 384/384 vs passive B3 368/384 using at most 4 paid actions/world. Active diagnosed one-edge mismatch on all six worlds, including the two gated-mixture worlds not identified by passive four-pulse evidence. In one of six worlds B5 used 3 rather than 4 actions. This illustrates that chosen public interventions can reveal unobserved context effects and improve predictions on this disclosed toy. B5's different transcript invalidates interpretation as a learned-concept body effect or independent statistical transfer evidence. The active selector is deterministic distinct-predicted-outcomes-per-paid-cost, NOT known optimal.

## Verdict and next scientific requirements
- **ENGINEERING_PASS**: yes for this disclosed toy (unit tests, toy Wake/Sleep, versioned Snapshot, local train/inspect/use CLI, toy evaluation).
- **DIAGNOSIS_VALIDATED**: only against disclosed engineering fixtures, not formal distribution.
- **REPAIR_DEMONSTRATED**: only bounded typed two-edge repairs on constructed data.
- **TRANSFER_EVIDENCE**: NO. B3 = B1 = B2 = B3x; same-topology TRAIN/eval, no independent authority.
- **PROMOTED_REFERENCE**: NO. Draft stack remains unmerged.

Before formal F0: require graph-isomorphism-disjoint test families, a stronger B4 episodic mechanism, actual independent evaluator host process/account and private source, tests of invariant policy vs executable body at equal information/resources, explicit action-cost estimator and sufficient power/cost budget. Historical TRAIN/DEV/FINAL remain untouched and no one-shot FINAL is authorized.

This record supersedes NO earlier design-only or old experiment record. It is appended as evidence, not an edit to old holdouts.
