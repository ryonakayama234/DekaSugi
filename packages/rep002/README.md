# EXP-REP-002 disclosed direct-grammar engineering pilot

id: REP002-DIRECT-PILOT
status: ENGINEERING_STAGED; NOT_FORMAL; NOT_H4
updated: 2026-11-01
tags: active-learning, experiment, synthetic, representation

Requirements: Python 3.12+, stdlib, CPU, Linux/WSL2, repository root. NO sealed sources or previous DEV/FINAL evaluator. The synthetic host and learner share a process; this is a reproducible engineering demonstration, not independently controlled scientific scoring.

Run:

~~~bash
python -m packages.rep002 train --worlds 64 --snapshot .run/rep002/snapshot.json
python -m packages.rep002 inspect --snapshot .run/rep002/snapshot.json
python -m packages.rep002 use --snapshot .run/rep002/snapshot.json --world-index 301 --stratum COMPOSITION --arm LQ --budget 4
python -m packages.rep002 evaluate-disclosed --output .run/rep002/pilot.json
~~~

TRAIN uses n = 0/3/8/16/32/64 named worlds, but requires 3 structurally different full-graph topologies for motif support; mere renaming does not contribute independent support. Learned hub-to-two-target motif is a **public-role conditioned** direct-edge prior. Object roles are intentionally public. The FA baseline chooses the public hub first without learned concepts: a positive LQ-LA difference is **not** sufficient to claim learned concept-specific advantage. LR removes concept body. Session charges each pulse. Active questions are only single-step pulses in this first deliberately restricted calibration; no gated/contextual inference, setup/reset operations, or comprehensive H4 search is implemented.

The evaluator receives committed typed direct-edge predictor output and tests its predictions against 32 evaluator-only state/action pairs per world; it never asks learner to select a model using private gold. Results are per-world AULC with budgets 0/2/4/8, not 32 independent worlds. Strong fixed FA is mandatory for interpretation. No formal pre-registration/power/independent custody. Keep design proposal docs separate from the actually implemented direct-only slice.

CI-safe tests: \`tests/test_rep002_disclosed_preflight.py\` is explicit in \`scripts/run_research_ci_v2_tests.py\`. Do not launch broad legacy test discovery.
