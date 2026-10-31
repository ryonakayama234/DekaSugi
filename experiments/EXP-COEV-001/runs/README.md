# EXP-COEV-001 run and review evidence index

id: EXP-COEV-001-RUNS
status: planned; NO_SCORED_RUNS; NOT_FROZEN
updated: 2026-10-31
tags: runs, evidence, provenance, research

| Phase | Status | Evidence | Interpretation |
|---|---|---|---|
| PR1 docs-only | drafting | Issue #106, docs/ spec/ plan/ ADR/ architecture | Proposal, not a trained model |
| PR2 G1 synthetic fixtures | not_run | Future local and safe CI receipts | Engineering only, not target accuracy |
| PR3 TRAIN learning | not_run | Future actual training episode/policy manifests | Training only, not independent generalization |
| PR4 isolated evaluator | not_implemented | Future source/seed/evaluator freeze | Security + scientific validity prerequisite |
| New FINAL2048 | NOT_AUTHORIZED | No dataset or evaluation labels opened | ZERO confirmed COEV accuracy results |
| L4 transfer | not_registered | Future experiment | No transfer result |

Historical OPPORTUNITY-001 TRAIN64 and EXP-0003A DEV/FINAL are never inputs to this study. A PR containing invented fixture tests cannot be described as scientific scoring. All future entries retain failed and negative results.

## 2026-10-31 PR2 feasibility work-in-progress (non-scientific)
Local invented-world structural probe: **3,741 syntax programs; 895 distinct 156-input semantic classes; 866 conditional representatives**. Six module unit tests passed locally (not a GitHub CI receipt). These are design-time computational facts, **not trained outcomes, target accuracy, or official scoring**. Exact source and tests are to be staged separately in implementation PR2; retain results as untrusted-local until exact-head verification. The proposed FINAL2048 refers to repeated IID draws from a sealed class pool, never to 2,048 distinct classes.

## Gate-order correction before scientific TRAIN (2026-10-31)
Codex P1 on PR #107 identified the draft's invalid TRAIN-before-freeze ordering. Public PR3 256-task simulation is **engineering-only** and cannot become confirmatory TRAIN evidence. A separate pre-TRAIN method/source/seed/pool/Oracle custody freeze is mandatory before new real TRAIN; a post-TRAIN policy snapshot freeze follows. Current official new TRAIN/DEV/FINAL observation count remains **zero**.
## PR2 stacked implementation candidate
[PR2 G1 local calibration](20261031-pr2-g1-local-calibration.md): synthetic-only 6 local unittest tests; 895 class count; GitHub CI / exact-head review pending. No supervised TRAIN, paired evaluation or final result.

## PR3 genuine TRAIN-only learning implementation (synthetic local)
[2026-10-31 PR3 training receipt](20261031-pr3-local-train-only.md): 256 paired invented TRAIN tasks, random 105 solved vs active 231, eight learned templates each, 64-bucket policy snapshots and local SHA digests. This is real experience-conditioned candidate learning under a same-process TRAIN simulator, not independent DEV/FINAL evidence. No official scoring authority.

## PR3 P2 reproducibility amendment (2026-10-31)
Original PR3 digest strings refer only to the earlier publicly seeded engineering algorithm; after mandatory full-payload hashing they cannot be treated as matching current source. New CI synthetic negative tests bind concept body/support/policy; no independent custodian or registered TRAIN/FINAL result.

## F0-C prospective power/resource design (no target truth)
[Analytic paired-test and Linux probe receipt](20261031-f0c-analytic-resource.md) reports invented-only hypothetical power/variance sensitivity and bounded public-resource instrumentation. No independently sampled target outcomes, official TRAIN/DEV/FINAL or source/seed freeze. Review under #115.

## F0-C actual invented-only cost measurement + P3 edge
[Paired-power and CPU/RSS receipt](20261031-f0c-analytic-resource.md) contains GitHub safe CI #41191597779 exact-head synthetic timing and peak RSS, plus reviewer P3 correction requiring strict confidence lower>0 even for variance zero. No official score, no CPU hard limits yet.
