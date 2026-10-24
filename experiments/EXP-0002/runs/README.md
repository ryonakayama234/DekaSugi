# EXP-0002 runs

id: EXP-0002-RUNS
status: completed; candidate review pending
updated: 2026-10-24
tags: exp0002, runs, evidence, provenance

## EXP-0002 RUN-002 — review regression test
- [RUN-002 security/cost accounting validation](20261024-0724-42122c9.md)
- [CI evidence and artifacts](https://github.com/ryonakayama234/DekaSugi/actions/runs/40073909590)
- 24/24 tests PASS. The original evaluation data were **not** replaced or presented as independent fresh data.

## EXP-0002 RUN-001 — initial measured test
- [RUN-001 human-readable measured report](20261024-0440-c849632.md)
- [RUN-001 machine-readable JSON](20261024-0440-c849632.json)
- [CI and original downloadable artifact](https://github.com/ryonakayama234/DekaSugi/actions/runs/40063234247)

**Functional gate PASS, limited within-family search benefit, promotion not yet approved.**
Positive holdout: 6→5 candidates (twice). Negative reverse: 40→47 candidates (+17.5%). Independent review pending.

Run metadata records both PR head and test-merge SHA; see individual report. New algorithmic tuning following this published holdout requires a fresh evaluation split.

[Preregistered plan](../plan.md) / [Data contract](../../../docs/architecture/contracts.md) / [Specification](../../../docs/specs/EXP-0002.md).
