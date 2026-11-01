# EXP-REP-001 — Run ledger
id: EXP-REP-001-RUNS
status: planned_no_evidence
updated: 2026-11-01
tags: experiment, run-index, representation

| Run | Scope | State | Evidence |
|---|---|---|---|
| DESIGN-V1 | approved direction / proposed preregistration | documented only | docs/specs/EXP-REP-001.md, plan.md |
| ENGINEERING-G1 | synthetic public world, negative tests and resource preflight | NOT_RUN | pending |
| TRAIN256 | future formal training (N candidate) | NOT_AUTHORIZED / NOT_RUN | pending |
| DEV64 | future source-locked diagnostic (N candidate) | NOT_AUTHORIZED / NOT_RUN | pending |
| FINAL1024 | future independently held-out evaluation (N candidate) | **NOT_AUTHORIZED / NOT_RUN** | pending |

Never present invented synthetic toy runs as formal TRAIN/DEV/FINAL. Every executed run must record commit SHA, runtime, machine environment, input hashes, sources, seeds for public toy only, command, raw counts and failure cases. Private seeds and targets remain in external custody.


- [20261101-invented-g1-smoke](20261101-invented-g1-smoke.md): 3 disclosed toy training worlds, 4 deliberately favorable toy evaluation worlds, 8 audit probes; **engineering-only, not a preregistered scientific estimate**. No formal TRAIN/DEV/FINAL.

- [20261101 G1-C rank-only / evidence-integrity engineering](20261101-g1c-rank-only-engineering.md) — R2P policy-only control and fail-closed negative tests. No independent scientific scoring; exact CI-head evidence separately required.
