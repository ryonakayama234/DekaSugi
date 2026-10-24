# EXP-0002B-METER-RUN-001 — runtime primitive-call smoke test

id: EXP-0002B-METER-RUN-001
status: measured diagnostic only; not a preregistered EXP-0002B learning result
updated: 2026-10-24
tags: experiment, metering, published-holdout, diagnostic, no-policy

> **解釈上の禁止:** This reruns EXP-0002's already published examples. It cannot establish fresh-holdout generalization or learned-policy improvement.

## Provenance / reproduction

- GitHub Actions: [run 40076212287](https://github.com/ryonakayama234/DekaSugi/actions/runs/40076212287) (success; workflow steps: doc validation, full unittest, EXP-0001, EXP-0002).
- Head commit: `0921f1cee59c9f3d35baf7740af7feeb940b48c9`; CI checkout source commit in emitted JSON: `4dcd7d6762b5ec0eaf8771fc03cf5ad035ee825d` (GitHub PR synthetic merge commit).
- 2026-10-24 07:58 UTC; Python 3.12 on GitHub Actions Linux runner.
- 28/28 unit tests PASS; documentation validation PASS (28 Markdown documents); EXP-0001/EXP-0002 workflow steps PASS.
- Command: `python -m packages.evaluation --output .run/EXP-0002-result.json`.
- Source fields, machine-readable metrics and caveat: [JSON observation](20261024-0758-metering-smoke.json). Archived original EXP-0002 run data is not overwritten.

## Results: calls to allowed primitives during verifier execution

| Existing task | Split in old EXP-0002 | OFF candidates | ON candidates | OFF primitive calls | ON primitive calls |
|---|---|---:|---:|---:|---:|
| dev-01 (normalize) | development | 6 | 5 | 14 | 10 |
| holdout-01 (normalize) | previously published holdout | 6 | 5 | 14 | 10 |
| holdout-02 (normalize) | previously published holdout | 6 | 5 | 14 | 10 |
| negative-reverse | previously published holdout | 40 | 47 | 102 | 122 |
| negative-identity | previously published holdout | 1 | 1 | 0 | 0 |

Existing published holdout 4-task total: OFF **130** calls, ON **142** calls (+12 / +9.23%). The two normalization tasks each save 4 calls; the unsolved reverse task spends 20 extra calls. This is a small diagnostic set and cannot establish true population performance.

## Interpretation and next gate

Candidate-count improvements do not imply unconditional efficiency improvement. The meter exposes why task-conditional selection is worth testing. **No contextual policy was trained** and no independent EXP-0002B dataset was evaluated. Next: independent review of PR #6; freeze a genuinely new EXP-0002B benchmark and algorithm *before* code is fitted; only then report LEARNED vs Always-ON/OFF.

### Threats to validity

- Published holdout reused for **diagnosing** the instrument; it is contaminated for policy selection and confirmatory testing.
- Counts omit hashing, AST checks, skill validation, feature extraction, time, memory, Kernel overhead, and training cost.
- Macro body is pure and unary; result does not automatically generalize to non-unary or side-effecting operations.
- Interleaved PR dependencies (#6 skill implementation, #8 research design) require reconciliation before merging.

[Measure design](../../../docs/architecture/measurement.md) / [Experiment development log](../metering-log.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7).
