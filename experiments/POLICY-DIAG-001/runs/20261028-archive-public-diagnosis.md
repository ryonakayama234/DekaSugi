# POLICY-DIAG-001 — immutable archived-public evidence diagnosis (2026-10-28)

id: POLICY-DIAG-001-RUN-20261028
status: completed_archived_public_partial_diagnosis; not_confirmatory; not_full_task_feature_replay
updated: 2026-10-28
tags: read-only, DEV64, TRAIN-DREAM, provenance, identifiability, descriptive

## Objective and evidence lineage

Research question: where does the information difference between **B2 random Dream** and **B3 near-WAKE-positive Dream** disappear between selected experience, 5-nearest-neighbor evidence, threshold choice, and observed primitive cost?

This analysis is **post hoc**, performed against the **original already-scored** DEV64 public result, and cannot prove H3, transfer, a causal mechanism, or a general intelligence gain. No original DEV/FINAL task was rescored, no DEV/FINAL generator was called, and the EXP-0003A v1 freeze or policy was not modified.

Sources, each independently hashed and cross-checked:

- EXP-0003A [freeze-v1.json](../../EXP-0003A/freeze-v1.json): `freeze_payload_sha256=1e0f6daf1cb80262c187c60a3e0a4d2e76dafea911f0633feed3c40f93db8f44`, pinned source/snapshot hashes.
- Original scoring event [run #40518246537](https://github.com/ryonakayama234/DekaSugi/actions/runs/40518246537), Artifact **#12739684056**, member `public.json` exactly SHA-256 `2fa48c841e99a69275c8bd3a5bd78eb2e01d4a3fcc226a6358958bf5cc053134`; 64 original task rows / four arms. Original workflow remains **failed** due to binary64 sum auditing, not modified. The independently corrected read-only audit [run #40522186710](https://github.com/ryonakayama234/DekaSugi/actions/runs/40522186710) passed, as documented in [DEV64 ledger](../../EXP-0003A/runs/20261027-dev64.md).
- Already existing PR3 [TRAIN/DREAM public artifact #12778980603](https://github.com/ryonakayama234/DekaSugi/actions/runs/40600373558/artifacts/12778980603), member `EXP-0003A-PR3-TRAIN-DREAM.json` SHA-256 `da34216419bab7a95bf93d9b6d5805cebf900a9c662efc91a77b4aa8536e621e`, `dev_or_final_evaluated=false`. Its B1/B2/B3 snapshot canonical SHA-256 exactly matched both frozen policy references and original DEV64 `snapshot_sha256` fields. The private companion member was **not parsed**, and no audit example appears in this report.
- Hash-gated reproduction utility: [scripts/analyze_policy_diag_archives.py](../../../scripts/analyze_policy_diag_archives.py). Machine-readable aggregates: [JSON](20261028-archive-public-diagnosis.json). In-memory analysis used only the two verified public JSON members and the pinned frozen selection IDs, not private audit data. The script is a retrospective analyzer, not a new scorer.

## Results: stage-by-stage measurements

| Stage and descriptive metric | Observed |
|---|---|
| Selected DREAM cases | B2 96, B3 96, **24 in common**, Jaccard **0.142857** |
| Distinct feature vectors **within DREAM96** | B2 **95**, B3 **85** |
| Positive `prefer_on` labels within DREAM96 | B2 **12**, B3 **12** |
| TRAIN160 included equally in both snapshots | 160 common observations |
| Distinct 8D vectors across whole 256-observation snapshot | B2 **237**, B3 **222** |
| Exact feature-collision groups | B2 **18** (37 records), B3 **32** (66 records) |
| Feature-collision groups with conflicting teacher label **or** exact call saving | B2 **0**, B3 **0** |
| Same 5NN **membership set** per DEV task | **3/64** |
| Different 5NN membership sets | **61/64** |
| Average shared neighbors per paired query | **2.890625 / 5** |
| Same 5NN `prefer_on` vote count | **63/64** |
| Same mean 5NN OFF−ON training call saving | **63/64** |
| Any safety veto among these original 5NNs | **0/64**, both B2 and B3 |
| Same ON/OFF action | **63/64** |
| Same action reason | **63/64** |
| Same actual primitive-call cost | **64/64** |

The shared-neighbor histogram (matched B2/B3 set size): **1:2 tasks, 2:20, 3:28, 4:11, 5:3**. Thus 5NN member identity changes on most tasks even though aggregate teacher-side vote and cost are usually unchanged.

### Archived reason/vote evidence

| Metric | B2 random Dream | B3 counterfactual Dream |
|---|---:|---:|
| `insufficient_on_votes` decisions | 55 | 56 |
| `cost_supported` / ON decisions | 9 | 8 |
| Queries with 0 positive votes among 5NN | 55 | 55 |
| Queries with 5 positive votes | 8 | 8 |
| Remaining marginal query | 4 votes | 2 votes |

**The only ON/OFF disagreement:** B2 ON (`cost_supported`), 4 of 5 positive neighbors, mean training call saving **3.2**; B3 OFF (`insufficient_on_votes`), 2 of 5 positive neighbors, mean training call saving **1.6**. **The already observed primitive invocations are 2 versus 2**. No newly computed search outcome or hypothetical B3-ON counterfactual is included.

On all other 63 matched tasks, **both** the 5NN positive-vote total **and** mean training call saving match exactly despite frequently different neighbor IDs. These are deterministic joins of original archived public neighbor IDs to preexisting fixed TRAIN/DREAM snapshot observations.

## Mechanism assessment and scientific limitations

| Hypothesis | Descriptive outcome | Bound on interpretation |
|---|---|---|
| **P-H1 selection redundancy** | **Partially supported for decision-relevant aggregate information**: 61 tasks have changed neighbor sets, yet 63 have unchanged vote count and mean saving. | Selected records are not identical; similarity of local decision statistics is not proof of global information equivalence. |
| **P-H2 representation bottleneck** | B3 has more identical 8D feature records (66 vs 37); no observed collision group disagrees on `prefer_on` or exact call saving. | Feature coarsening/concentration is observable, but a harmful representational bottleneck is **not demonstrated**. |
| **P-H3 decision saturation / gates** | **Directly consistent**: 63 tasks retain identical votes/savings and choice; only the one marginal query crosses the required 4/5 vote gate. | The specific mapping is identified from archived decisions and frozen observations; no causal effect of changing gates was tested. |
| **P-H4 action-to-cost insensitivity** | **Direct observation in one task**: B2 ON and B3 OFF nevertheless each used 2 primitive calls. | One case is not a global claim about skill utility or general counterfactual effects. |
| **P-H5 Dream selection-objective mismatch** | B2/B3 differ in 72 selected Dream IDs; B3 concentrates more repeated 8D features without observed DEV cost improvement. | Whether a boundary-aware selector would work better requires a newly preregistered experiment/fresh holdout; unidentifiable here. |

**Crucial missing fields:** the original artifact's `public.json` stores `trial_rows` with `task_id`, action, 5NN IDs and cost, **but does not contain the two visible `TaskSpec.examples` for each query**. Therefore exact DEV query 8D features, ordered neighbor distances and `close_support` cannot be reconstructed independently from this authorized public artifact. The reported 5NN membership is original archival evidence, **not a fresh independent ranking replay**. The scripted analyzer checks original snapshot hashes, neighbor membership, teacher-side votes/savings and reason consistency, but does not falsely claim complete `choose()` parity for DEV64.

A full independent per-query feature/distance replay would require additional **already archived, permissible public TaskSpecs**, verified against the immutable original evidence chain. **Never generate DEV cases now merely to fill the gap**. Absence of those bytes is `not_observed`, not zero. The existing helper's synthetic/TRAIN replay tests provide engineering calibration only.

### Research decision

A strong next hypothesis is *information value at the decision boundary*, rather than more near-positive examples alone. However **do not retune EXP-0003A v1**, substitute old DEV as fresh validation, or open FINAL128. Design a separate Active Learning v2 candidate with pre-registered prospective intervention, cost-of-information metric, and independent new holdout when authorized.

This bounded diagnosis answers the presently observable part of POLICY-DIAG-001. It is **not** a claim that H3 has been disproved on unseen data. Original private ZIP restricted off-repository long-term backup remains outstanding under [Issue #48](https://github.com/ryonakayama234/DekaSugi/issues/48), due before the original Artifact expires 2027-01-25.
