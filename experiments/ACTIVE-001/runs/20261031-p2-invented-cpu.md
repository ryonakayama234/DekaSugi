# ACTIVE-001 P2 — invented-only CPU measurement provenance (2026-10-31)

id: ACTIVE-001-P2-CPU-RECEIPT
status: instrumentation_committed; exact_head_ci_receipt_must_be_checked
updated: 2026-10-31
tags: active-learning, measurement, cpu, memory, no-scoring

## What was prepared

Branch \`research/active001-p2-cpu-budget\` stacked on draft F4 #101 head \`ced3bb691a7749a0637ea9b7b8d3341c572af009\`. The new \`packages/active_cost\` and explicit allowlisted \`test_active_cost_preflight.py\` generate a machine-readable **\`ACTIVE001_P2_CPU_RECEIPT=\`** JSON line in the safe CI log. It contains actual process CPU/wall ns vectors and Linux cumulative RSS high-water mark, plus structural *count-only* workload ceiling and a rough CPU proxy model for 7 and 12 arms over 512/1024/4096 independent task draws. **These are not scientific scoring runs.**

## Evidence status and provenance

The committed document asserts **no actual measured values**: consult the exact-head CI log and subsequent PR/Issue comment to recover the real results. No particular wall/CPU seconds, memory size or upper bound is inferred from the planned code. Confirm Gate F canonical public-context digest \`9c135ace8f815e4b3ac2465c9918833c3becd43781faeedc36314c28c9203f12\` at runtime and F4 full census \`NOT_COMPUTED\`. Review \`process_time_ns\`/wall-clock distinction and repeated values, and preserve any failed CI before marking technical acceptance.

## Restrictions / status
- Only \`input_split(20261030)\` invented public/question IDs. Predict 64 *query* inputs, not official auditor-input truth.
- Existing Gate F report is a structural census, not future scored target trial.
- B1+ separate PR #100: no directly measured B1+ CPU here; 12-arm projections are **scenario-only**.
- No official target/seed freeze, hidden scorer, sealed historical experiment imports, old workflow change, source-lock modification, scientific efficacy observation, or automatic merge.
- Full F4 91,367-context census is explicitly NOT_COMPUTED; short toy F4 timer cannot justify scaling that full workload.
- Next: exact-head safe CI, Codex source review, #99/P3 simulated inference; scientific source/evaluator approval required before official tasks.

[Plan](../p2-resource-budget-draft.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).
