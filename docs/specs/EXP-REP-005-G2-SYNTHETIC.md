# EXP-REP-005 G2-SYNTHETIC — public-only predictive-state repair, engineering V1

id: EXP-REP-005-G2-SYNTHETIC
status: IMPLEMENTED_SYNTHETIC_ONLY / SCIENTIFIC_NOT_RUN
updated: 2026-11-03
tags: representation, public-history, counterexample, typed-ast, wake-sleep, source-only

## Problem and falsifiable hypotheses
Issue [#150](https://github.com/ryonakayama234/DekaSugi/issues/150) / parent [#142](https://github.com/ryonakayama234/DekaSugi/issues/142). Existing REP004R mechanism gate found zero inquiry changes; G0b scientific family universe remains STOP under [#148](https://github.com/ryonakayama234/DekaSugi/issues/148). A standalone G2 artificial mechanism check is permissible as engineering but does NOT open G3 paid TRAIN, scoring or statistical transfer.

H-STATE: In a declared stationary deterministic single-world task, legal public episodes can witness two identical (visible state, action) pairs with different successors; deterministic visible-state-only representation cannot fit both.
H-REPAIR: A bounded typed candidate `HistoryEquals(lag, public_action)` with lag in {1,2}, and action in 12 legal actions, can resolve a selected public witness and produce an executable snapshot without private world laws.
H-NULL: No contradiction, forged chronology or contradictions not explainable by the grammar MUST NOT create a learned candidate.
H-MATCH: A STATIC-Hplus agent preinstalled with the same predicate has identical expressive ability; this artificial pilot does not demonstrate learned superiority.

## Strict contract
PublicStep = (before: 4-bit public state, history: tuple of last <=2 public action keys, action: public typed key, after: 4-bit public state, paid_cost=1). Action is exactly ('set',obj,bit) or ('pulse',obj,-1) for four public objects. Episodes must start (0,()), follow exactly from prior observed after/history, length 1..8. A corpus is 1..64 episodes and <=512 paid records. Same-world stationarity/determinism is an external premise, not something an in-memory public record proves.

No learner import of `rep005_g0b`, generator/private Law, source labels, scoring or sealed datasets. No arbitrary code/eval; all input types must match exact builtin types. Source-free synthetic tests may generate disclosed fake outcomes in TEST CODE only.

## Algorithm
1. Validate exact public chronology. A memoryless predictor groups experiences by (before, action); conflicting successors imply a same-world memoryless contradiction (subject to determinism/stationarity assumption).
2. When no contradiction: NO_REPAIR_NEEDED; do not silently improve by inventing unnecessary concepts.
3. Search exactly 24 typed single-predicate bodies in deterministic order: lags 1,2 x 12 action keys. A candidate is admissible iff every observed (before,action,Boolean predicate) key has one successor. Collect ALL admissible features, not just first match; select lowest lag then public action order and report ambiguity count.
4. If no candidate fits: NOT_CERTIFIED/NO_SINGLE_HISTORY_EQUALITY_FEATURE_FITS. A single observed contradiction without any repair is not proof of a true temporal law.
5. Save canonical JSON envelope `{payload, sha256}`, with typed body, observed prediction table, paid-action count, witness count, candidate count and public-evidence hash. Fresh process reloads only the envelope; `LoadedSnapshot.predict` dispatches the executable predicate and abstains on unseen table rows.
6. This is public evidence compression, not general world-law induction. No role-generalization, independent family transfer, policy improvement or learning-to-learn is claimed.

## Primary synthetic engineering checks
Same-state/action different successor witness, exact chosen lag-1 feature under disambiguating legal public experiences, memoryless baseline abstention, same-capacity STATIC-Hplus parity, executable fresh-process Snapshot, unseen-context abstention, forged public chronology/type rejection, no-contradiction and unrepairable conflict negative tests.

## Not measured / blocked
Actual G0b independent causal-family census, verified same-world external custody, source-isolated process/server for paid interaction, structural OOD transfer, family clustered uncertainty, live Active Inquiry policy, strong empirical baseline superiority, neural epochs, scored DEV/FINAL, model promotion. All are NOT_RUN / NOT_CERTIFIED. A synthetic test PASS must never be re-labelled as scientific success.
