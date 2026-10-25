# MEASURE-0001 — Canonical-meter integration and audit

id: MEASURE-0001-AUDIT
status: CI-passed and Codex code-reviewed; integration tracked by PR #18
updated: 2026-10-25
tags: experiment, audit, measurement, security, exp0002b

## Purpose / testable hypothesis
An optional per-arm counter can observe verifier-time **canonical primitive invocations**, including inside learned macros, without changing answers, trace, candidate count or trust boundary. This is an engineering measurement hypothesis, NOT an EXP-0002B policy-learning outcome.

## Inputs and provenance
- Baseline: main commit `fd0a98a03b2c1937224b54107dcefaa119198aab` (SEC-004 integrated).
- Older draft [PR #9](https://github.com/ryonakayama234/DekaSugi/pull/9), head `857f04fcacc2ff2d688d5ce7374f00aeecfc2074`, demonstrated the need for actual counters but left an unresolved P1: wrapping **caller primitives** executes forged callbacks. It must not be directly merged.
- Implementation: [Issue #17](https://github.com/ryonakayama234/DekaSugi/issues/17), canonical instrumentation PR (see Issue/PR history).
- No new dependencies; Python 3.12, Linux/WSL2 / GitHub Actions.
- Freeze: no alteration to original EXP-0002 plans, historical runs or EXP-0002B preregistration v2.

## Test acceptance
1. Unmeasured and measured modes produce identical status, AST, tested candidate count and trace SHA for primitive and macro arms.
2. Count exact verifier calls: lower-only two examples **4**, normalize macro two examples **10**, identity **0**; diagnostic legacy task totals remain expected (dev normalizing OFF/ON 14/10, reverse 102/122).
3. Fresh independent per-arm counters with deterministic per-operation tallies; reject forged primitive callable before any counted call.
4. Poisoned caller/default lookup and signatures, as well as poisoned macro implementation, never execute in measured or normal mode; macro is reconstructed from verified AST.
5. Expansions and budget checks, EXP-0001 baseline suite, EXP-0002 existing checks, document integrity, and Codex review pass before integration.
6. The metric excludes AST/hash/feature/kernel and wall/CPU total; do not claim speed or fresh generalization.

## Execution record
- Implementation PR [#18](https://github.com/ryonakayama234/DekaSugi/pull/18) code-and-doc head `00e8bee8e30cbcd0514c2f989b9a89fdc67e4669`: [GitHub Actions run #40152416447](https://github.com/ryonakayama234/DekaSugi/actions/runs/40152416447) **success**.
- Job `verify`: docs validation, full unit test suite, EXP-0001 preregistered suite, EXP-0002 diagnostic rerun and both artifact uploads reported success. New nine metering tests augment the existing 26 regression tests. Local WSL2 execution was not performed.
- GitHub `@codex review` code-review status for head `00e8bee`: **completed, has_any_findings=false, has_unresolved_findings=false**. This is not an explicit APPROVED review or a separately completed security review.
- Audit document updates after head `00e8bee` require CI and Codex recheck on their own final SHA before merge. Main integration/closure recorded on PR #18 and Issue #17; do not retroactively rewrite historical runs.
- Old [PR #9 smoke observation](https://github.com/ryonakayama234/DekaSugi/blob/exp/0002b-primitive-meter/experiments/EXP-0002B/runs/20261024-0758-metering-smoke.md) is historical **diagnostic**, not validation of the newly secured implementation.
- Future EXP-0002B FINAL and learned policy: **not run**.

[Measurement contract](../../docs/architecture/measurement.md) / [system](../../docs/architecture/system.md) / [data contracts](../../docs/architecture/contracts.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7).
