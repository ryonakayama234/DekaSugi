# EXP-COEV-001 PR3 — actual invented TRAIN episodes and Sleep concept snapshots

id: EXP-COEV-001-PR3-TRAIN-RECEIPT
status: local_engineering_train; NOT_SCIENTIFIC; CI_PENDING; no_scoring_authority
updated: 2026-10-31
tags: train-only, active-inquiry, learning, evidence, local

## Intervention and training source
Same 256 invented **TRAIN only** tasks, chosen by fixed seed 20261031 after a type-stratified 45% TRAIN-class pool is selected from 895 finite-domain semantic classes; independent public pair per task, candidate hypotheses always all 895 classes, <=2 distinct questions. Oracle is a same-process **TRAIN simulator** with an internal hidden target class; only chosen question answers and a terminal TRAIN-only binary success feedback are retained in learner Episodes. No DEV or FINAL task generated or scored. This is NOT independent custody or a confirmatory experiment.

## Local training observation (before PR exact-head CI)
| Arm | Tasks verified correct at TRAIN | TRAIN failures | Mean remaining semantic hypotheses | Learned top concepts | Contextual frequency records |
|---|---:|---:|---:|---:|---:|
| Random TRAIN queries | 105 / 256 | 151 | 10.4492 | 8 | 104 |
| Max-disagreement TRAIN queries | 231 / 256 | 25 | 1.2461 | 8 | 228 |

The exact same target/public input observations were paired. The learner chooses a canonical representative after observing at most two answers. Mean initial version-space size ~32.4844 in both arms. The difference 126 TRAIN successes is evidence of a useful **within-task query policy on this invented training distribution**, not evidence of a learned skill improving new targets. Unlike prior exploratory design-only work, the code *actually induces* typed anti-unified concepts from independently successful TRAIN episodes, requiring >=3 supporting task IDs, <=2 operation variables, positive approximate MDL gain, max eight concepts, and records 64-bucket contextual frequency policy. This library is a candidate, NOT adopted globally.

## Snapshots (local reference; GitHub exact-head must replay)
- Random snapshot digest: `87ba61a1b39019a2a88c4bd6b6b2c624fd580871e7cb921d41f6201b97428a00`.
- Active snapshot digest: `e07f49ad4e011d48e7fd142fcbc492b61fe286d3d385a7bb2bb278bc61d78663`.
- Active receipt digest: `0e440bed39d9095640daa04cfa81568a0f115fe926dd0eb08607cd88f3d7f619`.
These values derive from the local prototype of the algorithm; different exact-head source code may legitimately yield different hashes, to be checked independently before any promoted evidence.

## Nonclaims, risks and next gate
TRAIN target class is used internally by a local simulator for answers/binary verification, so this is not process-isolated confidential truth. The success feedback Boolean could be forged in an untrusted Episode; third-party authenticated TRAIN records are not implemented. Approximate MDL gain is an explicit heuristic, not measured CPU benefit. A task sample with replacement can reuse targets. The policy/skills' effect on genuinely new class-disjoint targets remains UNKNOWN; H1 result not estimated. Before DEV/FINAL: independently held trainer/custodian, source/seed lock, separate power and class opportunity review, exact-head safe CI, independent code review, evidence preservation and separate activation. Historic experiments never rerun.

## Superseding snapshot identity note — Codex P2
The three local prototype hashes above are preserved as history, but are **not hashes of the corrected PR3 source**. Original snapshot hash omitted concept body/support/parameter fields; now the complete payload, policy and receipt are committed and strictly checked. Synthetic negative tests reject body, support, parameter, gain, ID, policy or receipt alterations. These corrections do not turn the public invented TRAIN256 pilot into registered scientific TRAIN. The actual post-patch snapshot digest must be reproduced under verified exact-head code; no numerical H1 result exists.
