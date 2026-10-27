# EXP-0003A PR5 — Independent DEV64 evaluator (engineering protocol)

id: EXP-0003A-DEV-EVAL-PR5
status: implemented_proposal; dev_not_run; final_sealed
updated: 2026-10-27
tags: evaluation, development, freeze, evidence, source-integrity

## Research purpose
Bridge the already-frozen TRAIN/DREAM model to an **independent four-arm
DEV64 engineering smoke**. This is NOT new preregistration, not a change to the
immutable [plan-v1](../../experiments/EXP-0003A/plan.md), not acceptance of H2/H3,
and not permission to open FINAL128.

## Main module and responsibilities
- `packages/exp0003a_dev/__init__.py`: read-only, independent evaluator.
- `packages/exp0003a_dev/__main__.py`: reviewed main-push activation gate.
- `packages/exp0003a.freeze.verify_frozen()`: source-first lock against 14 fixed blobs,
  split hashes, selections, SkillCandidate and B1/B2/B3 PolicySnapshots.
- `packages/exp0003a.pr3`: canonical chooser and audited search reused unmodified.
- `packages/metrology`: CAL-01 synthetic fixture-only; NOT used as production scorer.

## Execution order and protection
1. On explicit reviewed main-push activation only, confirm GitHub event and SHA.
2. `verify_frozen()`: inert schema + exact source bytes BEFORE any regeneration.
3. Rehydrate the top TRAIN-only skill and B1/B2/B3 PolicySnapshots by a second
   independent TRAIN/DREAM reconstruction; match all frozen hashes. This
   rebuild has nonzero CPU cost and must be reported separately.
4. Generate DEV64 only *after* freeze and snapshot checks, then match ordered
   task/source IDs and raw split SHA against immutable `freeze-v1.json`.
5. For each DEV TaskSpec: decide B1/B2/B3 from public 2-example TaskSpec before
   any search. B0 is always OFF. Execute independent B0/B1/B2/B3 search,
   using canonical SEC-004 runtime and new MEASURE-0001 meter per arm.
6. Evaluate selected AST against evaluator-only third example; never pass
   audit, family, seeds, source ID, OOD flag to `choose`.
7. Store all trials, unsuccessful searches, errors and separate private raw
   manifest in two write-once JSON outputs. Preserve raw hashes and source commit.
8. DEV64 is an engineering diagnostic, never retune method or claim
   confirmatory improvement. FINAL128 requires separate explicit human approval
   and one-shot activation PR.

## Comparison and validity
Same DEV64 task IDs, fixed CPU environment, canonical primitives, expanded AST
budget 4, candidates budget 100, no untrusted callbacks. All four arms independently
search even when B1/B2/B3 select OFF; do NOT reuse B0's computed trace or meter.

Record task/arm: decision, reason, feature-neighbor IDs, search status/AST/trace,
false-solved, independent audit verdict, candidates, canonical primitive calls,
search/audit CPU+wall. Summary includes paired B2 minus B3 deltas, regressions,
OOD false ON, family breakdown, and descriptive cluster bootstrap
(8 family clusters, 1000 draws, seed 260303). The bootstrap on DEV is **not**
the preregistered FINAL confirmatory analysis. Do not convert a DEV improvement
into a scientific promotion.

## Stop rules / no regression
Abort before any DEV generation if frozen source/policy mismatches. Abort before
any scoring if generated DEV manifest is not exactly the pinned split. Fail
closed on duplicate task, source or seed IDs; false solved must be reported, not
silently reclassified. Keep original plan/freeze/14 source files unchanged.
`pull_request` CI runs ONLY unit/synthetic/TRAIN tests; DEV and FINAL never.
Separate post-review activation must be reviewed before enabling main-push smoke.
No FINAL evaluator/trigger is introduced in PR5.

## Review evidence required
Independent exact-head review, PR CI (Python3.12 unittest + docs validation),
freeze check without scoring, source manifest unchanged, immutable run report
and original artifact byte SHA after separately authorized DEV smoke.

Related: [ARCH-001](../architecture/system.md) /
[ARCH-002](../architecture/contracts.md) /
[run index](../../experiments/EXP-0003A/runs/README.md) /
[review gates](../process/workflow.md).
