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

## F0-A public structural source-preview diagnostic (#111)
[Unscored feasibility receipt](20261031-f0a-structural-preview.md): 895 finite-domain classes, public throwaway class pools 358/179/358 with per-stratum counts, deterministic source reconstruction and same-hash forgery negative tests. Not frozen scientific class assignment, not an independent Oracle, no actual registered TRAIN/DEV/FINAL. Scientific method/seed source remains Gate F0 #110.

## F0-A P2 correction receipt
The original 5-test public synthetic preview passed basic integrity but missed tuple-subclass iteration spoofing. New exact built-in type and canonical-only count validation plus additional regression are staged; original observations remain unscored. New exact-head safe CI and independent re-review needed.

## F0-B public-toy separate-process negative test index
[Fixed-fixture JSONL denial receipt](20261031-f0b-toy-ipc.md): source, five subprocess tests and limitations. Same account/public target, NO authenticated Oracle, NO real experiment scoring or activation. Complements F0-A public structural pool preview; does not substitute for pre-TRAIN scientific freeze.

## F0-B raw duplicate-key adversarial test
Public-toy IPC source now detects and denies duplicate keys before any schema/phase checks, following independent Codex P2. New sixth subprocess synthetic negative test; historic first 5/5 remains immutable. Exact-head safe CI/re-review needed. No new score.
