# EXP-REP-003 — G0–G5 disclosed reduced engineering experiment (measured)
id: EXP-REP-003-G0G5-REDUCED-20261102
status: DISCLOSED_ENGINEERING_CI_PASS / LEARNED_QUERY_EFFECT_NULL / BODY_ATTRIBUTION_UNIDENTIFIED / F0_NOT_RUN
updated: 2026-11-02
tags: experiment, measured, negative-result, transfer, review
issue: https://github.com/ryonakayama234/DekaSugi/issues/133
pr: https://github.com/ryonakayama234/DekaSugi/pull/135
measured_source_commit: 0407250e7a3d96b8491c4efc6b11934a6422a90e
source_ci: https://github.com/ryonakayama234/DekaSugi/actions/runs/41327359807
original_ci: https://github.com/ryonakayama234/DekaSugi/actions/runs/41327088853
raw_archive: ../artifacts/20261102-reduced-pilot-v1_1-raw.json.zlib.b64
summary: ../artifacts/20261102-reduced-pilot-v1_1-summary.json

## Evidence classifications (no F0 or DEV/FINAL)
- G0 baseline: prior corrected REP002 disclosed experiment LQ=FA across all four strata; #132 remains unmerged Draft. Historic source frozen; no historic run replay.
- G1 exact mechanism fixture: 4 actual paid all-zero source pulses eliminate unobservable DIRECT/GATE0 candidates; 25 consistent models remain. **All 12 legal one-step actions** exhaustively checked: NO_OPPORTUNITY, exact. Under legal two-step plan, a WITNESS appears after 74 exhaustive candidate plans examined, with `set(0,1)→pulse(1)` at additional cost 2. **Total recorded conditioning plus witness cost is 6.** This is the minimum within the selected conditioned state and 1/2-step enumeration, NOT the global minimum experiment cost from a fresh unknown world (which already has one-step DIRECT-vs-EMPTY distinguishing opportunity). It only witnesses different outputs of two possible models, not identification of the evaluator's true world.
- G2 actual TRAIN: 64 disclosed invented worlds, 100 charged operations/world, **6400 operations**; snapshot SHA256 digest `110dbfdb1f7b81ae16c6c86ae1c8e77a8a426eb641bb4a684343c2dab48bbede`. Learning curve TRAIN sizes: 0,3,8,16,32,64; inferred `EMPTY/DIRECT/GATE0/GATE1` groups rise 0→1→4 and then remain 4. Distinct anonymous worlds ≠ independent causal family count; **only four semantic classes** in the entire one-edge grammar template library. No SGD epoch, no self-invented grammar primitive.
- G3 actual local CLI train/inspect/use performed by exact-head CI synthetic tests, including Snapshot save/load/typed validation, paid queries, immutable `commit_digest`, on unfamiliar opaque-ID world; no private gold returned. The CLI is reusable from WSL2. This is not a human-facing interactive agent or process-isolated eval.
- G4 disclosed score: 48 deterministic worlds × 7 controls × budgets `0,1,2,4,6,8` = **2016 complete rows**, each scored on 32 evaluator-only full next-state vector checks = **64512 audits**. Complete v1.1 archive reversible zlib+base64 contains every row, all action sequences and predicted models, not just a digest. Canonical row `records_digest = 6792a8cff8d3e69f4b4789da80309df4d11d602bf870a39537176d116ae5e1b9`.
- G5: source CI run above PASSED whitelisted synthetic-only test suites, source integrity and docs; review requested in PR #135 and is **not** a claimed independent accepted code/method result until review is complete. Existing source is safe-allowlist test only. No auto merge or formal model promotion.

## Disclosed budget-averaged vector-accuracy AULC (six horizons)
| Disclosed stratum | LQ | LA | LR | ER | FA | BODY-OFF | FX |
|---|---:|---:|---:|---:|---:|---:|---:|
| RENAMED | .907118 | .907118 | .907118 | .907118 | .907118 | .907118 | .905382 |
| CONDITIONAL_TRANSFER (same known GATE1 motif, different opaque IDs) | .899306 | .899306 | .899306 | .899306 | .899306 | .899306 | .885417 |
| NOVEL (misnamed: actually heldout GATE0, present in TRAIN and grammar) | .924479 | .924479 | .924479 | .924479 | .924479 | .924479 | .874132 |
| DISTRACTOR (two edges, **out-of-grammar**) | .498698 | .498698 | .498698 | .498698 | .498698 | .498698 | .806424 |

**Mechanism conclusion:** LQ−LA = 0 and LQ−FA = 0 in ALL strata. LQ also matches LR, ER and BODY-OFF exactly. Critical additional *action-trace diagnosis*: there are **0 distinct LQ vs LA paid action sequences across 48×6 = 288 same-world/budget comparisons**, and similarly zero LQ vs FA query differences and zero LQ/LA committed model differences. The implementation has a trained prior path, but under this generator and exact two-step Gini/cost planner it never changes the actual query policy. Thus the task does not causally expose the intended concept-to-question mechanism; the result is **UNIDENTIFIED/NULL FOR THIS PILOT**, not a strong falsification of all learnable concepts.

## OOD abstention explanation — important negative effect, NOT learned negative transfer
For 12 two-edge DISTRACTOR worlds, within the one-edge model grammar the active planners lose their consistent model set and correctly `ABSTAIN` rather than invent a false fit. Number of ABSTAIN worlds at B=4/6/8 for each of LQ, LA, LR, ER, FA and BODY-OFF is **3/12, 11/12, 12/12** respectively; their deterministic rubric scores abstention as 0. FX does not abstain at any horizon and retains high full-vector accuracy **under a sparse-edge task**, yielding FX .806424 vs LQ .498698, difference −.307726. This score comparison is conditional on a zero-for-abstain rubric. Report **accuracy with coverage** rather than interpret FX as a safer representation model; and do not call it learned-knowledge negative transfer, since untrained FA has the same failure.

At B=8 the bounded one-edge learner attains 1.0 audited next-vector accuracy on the `NOVEL` label, but that label is a **semantic misnomer**: GATE0 was already sampled in TRAIN and explicitly in its hypothesis grammar. No claim of truly unseen causal semantics or broad generalization is licensed. `CONDITIONAL_TRANSFER` is also only a held-out ID permutation of a seen GATE1 pattern, NOT new multirule composition.

## Training cost and action metering
The reported 6400 paid TRAIN actions are real `Session.apply` operations; query model-check expansions are tracked per-world/arm. For example at CONDITIONAL_TRANSFER B=8 LQ/FA each average 7699 model checks; FX averages 1530. Model budgets permit up to 200000 checks per episode. **No shared full-lifetime CPU/wall/RSS or train/Sleep/Dream amortization has been matched**, and structurally hand-built priors appear in all arms. Therefore no efficiency advantage, reference model freeze, causal body-specific benefit, statistical significance or scientific custody can be inferred.

## Reproducing raw data (local, read-only)
```bash
python scripts/read_rep003_archive.py --archive experiments/EXP-REP-003/artifacts/20261102-reduced-pilot-v1_1-raw.json.zlib.b64 --output .run/rep003/recovered.json
python -m packages.rep003 preflight --output .run/rep003/preflight.json
python -m packages.rep003 train --worlds 64 --snapshot .run/rep003/snapshot.json
python -m packages.rep003 inspect --snapshot .run/rep003/snapshot.json
python -m packages.rep003 use --snapshot .run/rep003/snapshot.json --budget 6 --trace .run/rep003/use.json
python -m packages.rep003 evaluate-disclosed --output .run/rep003/recomputed.json
```
Check `records_digest` of recomputed output against `6792a8cff8d3e69f4b4789da80309df4d11d602bf870a39537176d116ae5e1b9`; sources at measured source commit above. The newer archive includes action sequences and policy-switch diagnostics; the first disclosed preflight archive from 41327088853 is also preserved as history, **not silently overwritten**.

## Scientific gate / next intellectual decision
1. **ResearchPrototype engineering**: runnable, versionable, quality-gated. NOT scientifically validated FrozenReferenceBaseline.
2. **Current question-selective learning claim**: NOT_SUPPORTED, mechanism has no actual action switch in this test; do not tune the identical test generator to force positivity.
3. **Next source-design work, separate from present score**: build true two-edge conditional COMPOSITION family with structurally independent TRAIN/TEST, nontrivial learned body instantiation/binding, interventional data under a realistic shared full-lifetime budget, and a pre-score *mechanism manipulation check* that some learner-world pair gives different LQ-vs-LA queries. A pilot generator can be redesigned openly; all worlds touched by the earlier score must be excluded from future formal holdout. Add coverage-calibrated OOD policy rather than penalizing evidence-based abstention without cost analysis.
4. F0/independent formal DEV and one-shot FINAL: NOT_RUN, need separate power/source/custody review and owner permission. No private Google Drive archive read.
