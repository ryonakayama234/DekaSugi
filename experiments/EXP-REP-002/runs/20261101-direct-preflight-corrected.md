# EXP-REP-002 — corrected independent-code-review preflight and raw results
id: EXP-REP-002-DIRECT-PREFLIGHT-REPAIRED
status: DISCLOSED_ENGINEERING_CI_PASS; SCIENTIFIC_ATTRIBUTION_NEGATIVE; INDEPENDENT_REVIEW_PENDING
updated: 2026-11-01
tags: experiment, synthetic, negative-result, quality-assurance
source_commit: 64f1d4dc54f7d150606a0753280d13e639f5039a
ci_run: https://github.com/ryonakayama234/DekaSugi/actions/runs/41315397816
raw_data: 20261101-direct-preflight-corrected-raw.json
supersedes: 20261101-direct-preflight-measured.md (preserved as historical prior variant)

## Four critical defects and their repairs
Independent code review identified 4 P1 defects in the first measured pilot: (1) TRAIN's structure support depended directly on hidden graph metadata instead of reconstructed PUBLIC pulse evidence; (2) FA fixed-query baseline secretly used trained motif during inference; (3) world×arm×budget rows were reduced to digest and discarded instead of being reproducible per-world evidence; (4) source range/cost accepted noncanonical or out-of-range public data. All four were fixed in code; new negative tests verify FA's predictions are unchanged between TRAIN0 and TRAIN3, exact pulse source/cost checks, raw row count and digest. The exact-head synthetic CI passed **152 tests**.

## Corrected actual learned artifacts and evaluation
TRAIN64 uses 320 charged pulses but only **3 distinct** TRAIN graph topologies. The learned executable two-edge public-role motif is hub->x and hub->y (starts at three structurally different TRAIN graph types). Verified Snapshot digest: `86216e36a28b22bf713e3c11be505216c51fa4f9d2c7fa6ce51ed6d044cf2ab0`.
Evaluated 48 disclosed synthetic worlds × four arms × four budgets = **768 raw world-arm-budget records**. Each includes 32 evaluator-only state/action checks. Full raw rows are preserved in JSON, canonical `records_digest` `62e3109633419da4cd56eb3c7c33a59f5c8c66d52fd4ddd8265ea1d740937494`. No raw row has been silently dropped; code regenerates results deterministically.

## World-level average AULC (budgets 0,2,4,8)
| Stratum | LQ concept query+inference | LA blind query+learned inference | LR no learned concept | FA fixed no TRAIN (public hub prior) |
|---|---:|---:|---:|---:|
| COMPOSITION | 0.822266 | 0.794271 | 0.794271 | 0.822266 |
| RENAMED | 0.904948 | 0.903646 | 0.851562 | 0.904948 |
| NOVEL | 0.665365 | 0.666016 | 0.664062 | 0.665365 |
| DISTRACTOR | 0.788411 | 0.808594 | 0.720703 | 0.788411 |

COMPOSITION LQ-LA = +0.027995 (2.7995 percentage points). **Crucial:** After making FA completely independent of trained Snapshot, FA continues to MATCH LQ exactly across all strata. Thus the apparent active benefit can be reproduced by a fixed public-role hub-first heuristic, not evidence that learning the motif was necessary. On DISTRACTOR, LQ-LA = -0.020183, demonstrating possible negative policy transfer.

## Honest classification and limitations
G1-D preceding repair is separately verified; this rep002 pilot does not automatically constitute reference-model promotion. This small *direct-only* pulse experiment does not implement context-gated semantics, genuine two-step setup actions, broad H4 search or a full shared primitive-budget verifier. Only three different structural TRAIN graph shapes are present despite 64 named TRAIN worlds. Public role labels encode a strong shortcut. The exact fixed role prior FA was authored by the experimenter rather than learned from independent experience; it is a powerful mechanism control, not proof of an externally optimal or general active policy. All 48 test worlds derive from a few handmade pattern classes, so per-world differences do not provide independent family-level statistical significance. The synthetic auditor and learner run in the same Python process. The source graph is not an independent formal private custodian. Full causal generalization remains unproven. Do not invoke prior heldout/DEV/FINAL, do not automatically merge.

## Engineering verdict
Exact-head CI and data preservation: PASS (152 allowlisted tests). Four previously identified P1 failure classes: regression-tested. **Independent current-head reviewer verdict pending.** Primary learned-concept-specific question advantage: NOT_SUPPORTED_BY_THIS_PILOT. The next scientifically decisive experiment must remove explicit public-role shortcuts and test genuinely discriminating context-gated reachable questions with exact shared expanded-AST resource budgets, stronger fixed active comparators, semantic-equivalence strata and independent source custody.
