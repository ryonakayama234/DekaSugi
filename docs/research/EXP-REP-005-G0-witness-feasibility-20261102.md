# EXP-REP-005 G0 witness feasibility — reproducible pilot audit

id: EXP-REP-005-G0-WITNESS-FEASIBILITY-20261102
status: precheck_executed_not_independently_approved
updated: 2026-11-02
tags: research, representation, exhaustive-search, public-interventions, negative-controls
issue: https://github.com/ryonakayama234/DekaSugi/issues/142
pr: https://github.com/ryonakayama234/DekaSugi/pull/145

## Scope and what is actually verified

This is a **G0 methodology feasibility precheck**, not G1/G2 certified implementation, NOT learner invention, NOT TRAIN, NOT test-score, NOT a released model. Method code: [g0_witness.py](../../experiments/EXP-REP-005/g0_witness.py); tests: [test_rep005_g0_witness.py](../../tests/test_rep005_g0_witness.py). It uses a small evaluator-private deterministic 4-object world with legal paid `set(i,0/1)` and `pulse(i)`, each exactly cost 1. Visible initial state 0; the public record consists of state/action/next-state/ordinal/cost, not the private generating law.

Publicly described fixture for audit only: on `pulse(source)`, toggle `target` IFF the immediately preceding **public** action is `set(source,0)`. Otherwise do nothing. Any `set` changes only the named visible bit. This is a human specified positive **Hplus feasibility** example; no agent infers the rule here.

## A shorter contradiction than the old illustrative four-action trace

Original proposed sequence of length 4 remains legal and discriminating. However, from initial state zero and empty public action history, a **three-paid-action** trace already suffices:

| Ordinal | Legal priced action | Visible state before | Visible state after |
|---|---|---:|---:|
| 0 | `pulse(source)` | 0 | 0 |
| 1 | `set(source,0)` | 0 | 0 |
| 2 | `pulse(source)` | 0 | `1 << target` |

Ordinals 0 and 2 have the **same exact** `(visible state=0, action=pulse(source))` but unequal successors. Thus every deterministic, history-blind `f(state,action)`, not merely a tiny H0 catalogue, is contradicted by this public trace. One-lag Hplus models reproduce the trace. The finite checker searches a legal alphabet of 12 actions (8 set and 4 pulse); it verifies that none of the 12 length-1 or 144 length-2 sequences exposes this type of contradiction and **exactly one** of the 1,728 length-3 sequences does, for the specified role binding and private fixture. The built-in checker separately requires the witness and an Hplus-consistent public-only candidate under all 24 role renamings. Independent review of source and execution logs remains required before treating this as a certified research proof.

Consequently, **do not claim a horizon-3 negative opportunity control** for this fixture. A horizon <=2 negative is scoped to this starting state and allowed action alphabet. A forced 4-step path might needlessly give the agent an extra paid action and bias inquiry comparisons. Report both the historical proposed 4-action witness and the new shortest 3-action witness without editing historical documents or score receipts.

## What is NOT established

- No actual learning, autonomous construction of a typed AST, persisted Snapshot, fresh-process USE, improved utility, or scored outcome.
- Even a successful Hplus match shows **representational possibility only**. The witness's exact guarded relation is **built into the fixture**, not invented by a learner; the separate future equal-capacity STATIC-Hplus baseline remains mandatory.
- All 80 *distinct canonical structural semantic families* required for preregistered 32 TRAIN +16 DEV +32 EVAL **remain ungenerated and unverified**. Counting permutations, object IDs, lag values or candidate programs as independent structural families is prohibited. Therefore the prospective numeric split is **not certified**.
- No independent exact-head G0 scientific methods review has approved the proof, family design, sample-size, statistical plan, and leakage boundaries; engineering CI pass does not grant that approval.
- The public-only checker validates event shape, chronology and price, **not authoritative origin**; future G1 requires a trusted environment's signed/custodied public event receipts and adversarial provenance checks.
- Finite `Hplus` enumeration in this precheck is restricted to source, target, guard, set value, lag 1/2 and memoryless always/never. It is **not** the full preregistered generic typed metalanguage or a proof of its complete expressive semantics.

## Decision / stop gates

- G0 positive subfinding: the deterministic memoryless H0 vs one-lag Hplus opportunity can be exposed by **3** public paid actions, and role/permutation and type/value/cost controls are executable.
- G0 BLOCKERS: independent review of exact PR head, a typed metagrammar/full family generator with independently validated 80 structural families, and prospective private split manifest and score protocol.
- G1/G2/G3/G4/G5/G6: **NOT CERTIFIED / NOT RUN**. Do not create 64-TRAIN or 64-EVAL score rows, mark a model trained, or silently redefine a family to reach sample counts. Stop and explicitly report scientific scope if G0 blockers remain.

## Reproduction (new synthetic method-only test)

```bash
python -m unittest discover -s tests -p test_rep005_g0_witness.py -v
python scripts/run_research_ci_v2_tests.py
python scripts/check_docs.py
```

These commands are source/method and non-scoring synthetic tests only; the CI allowlist includes the G0 test explicitly. Never run the archived DEV/FINAL generators from this receipt.

## Provenance / review

User approved delegation to continue a full conditional research workflow in the conversation on 2026-11-02. This is not a waiver of the agreed scientific gates. This precheck is authored on stacked Draft PR #145; independent exact-head Codex review has been requested. Engineering CI result, reviewer findings and source SHA must be recorded separately when available. No merge and no model promotion.

## Engineering CI chronology (historical failures preserved)

- [CI #41451824758](https://github.com/ryonakayama234/DekaSugi/actions/runs/41451824758): **FAIL**; a newly inserted Python test had literal escaped newline sequences and accidentally commented out the assignment of `shortest`, resulting in `NameError`. The G0 test code was corrected; this was an engineering error, not a failed H0/Hplus proof.
- [CI #41452266862](https://github.com/ryonakayama234/DekaSugi/actions/runs/41452266862): **SUCCESS** on the corrected test head `7ba4a2bd27f521f26d5c3cf97ebc6f0e13f0289a` (safe source verification, doc validation, whitelisted tests). A later source refactor requires its own exact-head CI check.
- Neither CI run is independent scientific G0 approval, training, or scoring.
