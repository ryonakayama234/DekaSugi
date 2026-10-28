# OPPORTUNITY-001 Real Evidence Adapter — PR8 engineering contract

id: OPPORTUNITY-001-REAL-ADAPTER-V1
status: draft_implementation; synthetic_unit_calibration_only; no_scored_trials
updated: 2026-10-28

## Scope and trust boundary

This source provides a **pure normalization and classification of the result tuples** returned by the already pinned canonical `_audited_trial` primitive evaluation boundary. It does not call the solver, generate any new TRAIN/DEV/FINAL task, construct or call Kernel, or open original holdouts. The synthetic fixture `opportunity-fixture-v1` module remains separate and MUST NOT ingest these records.

A future separate source-first activated runner will be responsible for (i) verifying frozen source and exact fresh TRAIN64 public TaskSpec, (ii) verifying source-replayed B1/B2/B3 choices against a separately sealed pretrial decision SHA from CI, (iii) writing time-ordered decisions to independent durable storage **before** scoring, (iv) independently evaluating OFF and ON using fresh canonical registries/meters and evaluator-only third example, and (v) preserving private original raw evidence in a verified access-controlled off-public-GitHub archive. None of those become true merely by having this adapter.

## Public-only record `opportunity-paired-evidence-v1`

A single record includes an opaque public task ID, a SHA-only commitment to a third audit, redacted evidence for OFF and ON, a truth-valued audited correctness for each, primitive meter total and candidate count, selected AST hash and trace SHA if available, isolated search/audit CPU and wall times, a classification, posthoc unique best choice when identifiable, and independently accounted outcome/cost regret for three **previously chosen** B1/B2/B3 actions.

- **Both correct**: compare primitive calls and allow excess-calls regret, including cost ties.
- **Only ON correct**: OFF choice misses success. No primitive cost regret is defined.
- **Only OFF correct**: ON choice loses success. No primitive cost regret is defined.
- **Neither correct**: unidentifiable choice benefit; no zero-imputation.
- Any false_solved / score vs search status contradiction / missing solved program / canonical count or boolean mismatch / invalid CPU time / forbidden unexpected private evidence field is an exception that stops a later execution, not an observed negative case.

## Limitations / nonclaims

These are **schema/logic checks**, not independent verification of scorer provenance, audited correctness, source identity, temporal ordering, custody, or scientific effectiveness. A caller could fabricate a tuple; this module cannot promote such a tuple to trusted scientific evidence. Consequently there is NO actual pilot CLI/activation in this PR and no new paired TRAIN64 outcomes. The repository is publicly visible and cannot host the raw private third audits in plain GitHub Actions artifacts; see [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).

Method authority: [pilot-v1](../../experiments/OPPORTUNITY-001/pilot-v1.md). History: [source lock](../../experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json), [pretrial PR #65](https://github.com/ryonakayama234/DekaSugi/pull/65), [data custody gate #66](https://github.com/ryonakayama234/DekaSugi/issues/66).
