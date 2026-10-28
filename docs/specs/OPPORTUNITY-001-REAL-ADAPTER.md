# OPPORTUNITY-001 Real Evidence Adapter — PR8 engineering contract

id: OPPORTUNITY-001-REAL-ADAPTER-V1
status: draft_implementation; synthetic_unit_calibration_only; no_scored_trials
updated: 2026-10-28
tags: opportunity, evaluation, real-adapter, evidence, audit, no-holdout

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


## Exact canonical tuple schema and integrity (post-review hardening)
- `search`: exact keys `task_id,status,solved,program,tested_candidates,max_nodes,max_candidates,trace_sha256`. The fixed public ID must be `t-` followed by 64 lowercase hex digits, with 4 expanded nodes and 100 candidates, a **lowercase 64-hex SHA-256 trace**, and coherent status/solved/program/selected_ast. Unknown search fields are rejected rather than silently leaked.
- `meter`: exact total and `by_op` fields; only `trim/lower/upper` positive integer counters; their sum must equal total, and zero total implies empty mapping. Search/audit CPU and wall values must be finite nonnegative; arbitrary private fields, false_solved, bool-as-int counts, mismatched tasks or budgets are fatal.
- `public_redacted_pair` includes **only hashes** for trace/AST/private third-audit commitment; it never copies a third example or hidden generator label. It does not establish that a genuine original audit exists, its unforgeability, independent custody, or that the frozen B1/B2/B3 choices were recorded before outcomes. This module has no scoring CLI/activation. [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66) blocks any real scoring pending separate reviewed custody/chronology/scorer.

## Solved-program canonical AST and expanded physical-node check
- Before redacting a `solved` result to an AST hash, PR8 recursively verifies the exact unary `node_kind=input/call`, `type=String`, `op_id`, and one-element `children` shape. Unexpected nested/private fields, unknown ops or type drift **hard-stop**; equal dictionaries alone are not proof of a valid program.
- OFF permits only primitive `trim/lower/upper`. ON additionally permits *only* frozen EXP-0003A skill `skill_8fe1361cb5014f85` (body hash `8fe1361cb5014f8503e4a57392e45f4fc7607e788fdd598f66668fbc11338eff`), equal to `lower(trim(Input))` and requiring two physical primitive calls per macro expansion. Search's fixed `max_nodes=4` applies to **expanded** AST, not surface nodes. No actual skill executes in the normalizer.
- This checks only intrinsic AST and budget consistency. It does not independently certify a skill body/source in a caller's real registry; source-first legacy and pilot lock validation remain mandatory in a separately reviewed runner. Synthetic fixtures include empty/malformed/private AST, five-node primitive and expanded-macro cases.
