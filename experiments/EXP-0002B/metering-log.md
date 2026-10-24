# EXP-0002B — measurement-development log (not a learning run)

id: EXP-0002B-METER-LOG
status: CI-verified diagnostic; independent review and prerequisite merge pending
updated: 2026-10-24
tags: experiments, instrumentation, run-log, no-results, exp0002b

## Purpose and hypothesis

**Hypothesis:** It is possible to count verified primitive operations executed during bounded search, including safe macro bodies, while preserving answer, program, candidate count and trace order. The meter must not quietly treat one macro as one primitive invocation.

## Scope / version

- Change ID: `MEASURE-0001`; observation format: `runtime-wrapped-v1`.
- Target dependency: EXP-0002 candidate implementation [PR #6](https://github.com/ryonakayama234/DekaSugi/pull/6); research dependency [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7).
- Changes to Python code: optional per-arm `PrimitiveCallMeter` for `bounded_synthesize`; individual primitive implementation wrappers; paired diagnostics in re-runnable EXP-0002 JSON.
- Existing verifier, DSL semantics, default skill registry, allowed execution operations, train/dev/final partitions and promotion criteria are unchanged.

## Conditions and reproducibility

1. Control: original uninstrumented bounded search.
2. Intervention: identical bounded search with a fresh `PrimitiveCallMeter`, first with primitives only, then with the isolated candidate macro.
3. Unit-test fixtures: lower-only, identity, and the original **development** normalization case. Published EXP-0002 final holdout is not a basis for tuning an EXP-0002B policy.
4. Assert same `program`, `status`, `tested_candidates` and `trace_sha256` in both conditions.
5. Assert exact runtime-count examples: two lower-only examples give 4 primitive calls before first solution; two normalize examples with macro active give 10 calls before first solution; identity gives 0 calls.

## Metrics

- `primitive_invocations` and `by_op` (counted as actual wrapper executions), by arm.
- `tested_candidates`, `status`, `trace_sha256` unchanged from `SearchResult`.
- Wall time is noisy and includes metering overhead in the measured mode; do not compare it as an optimization claim.
- **Not covered:** AST checking, program hashing, macro registry setup, task-feature extraction, Kernel inference/learning, whole-system CPU time.

## Acceptance and failure criteria

- PASS only when unit tests, EXP-0001/EXP-0002 regression tests, document checks, and independent review are complete.
- FAIL on changed answers/search traces, macro calls counted as one, mismatched registry versions/order, or unauthorized skills.
- Does **not** show that a contextual policy improves generalization. That needs a separate EXP-0002B preregistered training/development/holdout experiment.

## Execution record

| Field | Status |
|---|---|
| Code and regression tests | 28/28 PASS on [CI run 40076212287](https://github.com/ryonakayama234/DekaSugi/actions/runs/40076212287) |
| Local WSL/Linux test run | not run in this environment |
| CI test evidence | docs, unittest, EXP-0001 and EXP-0002 steps PASS (run 40076212287) |
| Actual experiment output JSON | [diagnostic run](runs/20261024-0758-metering-smoke.json); [interpretation](runs/20261024-0758-metering-smoke.md) (NOT independent policy evaluation) |
| Independent adoption review | pending |
| New policy training / holdout | not started |

**Integrity note:** The 2026-10-24 EXP-0002 historic run artifacts remain immutable. A re-run with counters must be saved as a new artifact tied to the new code SHA. No preregistered EXP-0002 findings are retroactively changed.

[System](../../docs/architecture/system.md) / [Data contracts](../../docs/architecture/contracts.md) / [Measurement spec](../../docs/architecture/measurement.md) / [Doc index](../../docs/INDEX.md).
