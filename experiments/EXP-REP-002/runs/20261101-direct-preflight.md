# EXP-REP-002 direct-XOR preflight receipt
id: EXP-REP-002-DIRECT-PREFLIGHT
status: IMPLEMENTATION_STAGED; SCORE_PENDING_CI; NOT_FORMAL; NOT_H4
updated: 2026-11-01
tags: experiment, synthetic, active-learning, learning-curve
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/130

## Work scope
New packages/rep002 engine, CLI and explicitly allowlisted test suite are staged. At receipt creation exact-head CI scoring and independent review are pending; no numeric EXP-REP-002 result is asserted.

## Preregistered engineering reduction before scoring
Five Boolean objects with <=4 DIRECT XOR relations, public role labels, pulse-only paid learner actions, no gated setup/reset, no actual two-step action lookahead, no exhaustive H4. Distinct 3-edge TRAIN full graphs provide an executable 2-edge shared motif, 4-edge COMPOSITION full graphs test bounded transfer of that motif. A fixed FA hub-first control knows public role labels and may explain any advantage over naive LA. Synthetic host and audit remain same process. This is intentionally not the complete EXP-REP-002 design, formal DEV/FINAL, independent custody or general intelligence evidence.

## Reproduction commands
python -m packages.rep002 train --worlds 64 --snapshot .run/rep002/snapshot.json
python -m packages.rep002 inspect --snapshot .run/rep002/snapshot.json
python -m packages.rep002 use --snapshot .run/rep002/snapshot.json --world-index 301 --stratum COMPOSITION --arm LQ --budget 4
python -m packages.rep002 evaluate-disclosed --output .run/rep002/pilot.json
python scripts/check_docs.py
python scripts/run_research_ci_v2_tests.py

## Measures to report after actual execution
Nested TRAIN n=0/3/8/16/32/64 and structure count; Snapshot digest, TRAIN charged actions; COMPOSITION and negative strata world scores under LQ/LA/LR/FA at budgets 0/2/4/8; AULC paired effects; actions, expanded nodes and CPU time; exact source/CI and negative results. Do not report as done until execution evidence exists. Do not touch any historical sealed source or old run.
