# EXP-REP-005-G0C — V5 bounded source / inquiry engineering specification

id: EXP-REP-005-G0C-V5
status: implementation_candidate_source_only_scientific_G1_G3_NOT_RUN
updated: 2026-11-03
tags: causal-source, active-learning, finite-proof, engineering
parent_issue: #158 / #142 / #148
primary_module: packages/rep005_g0c
research_level: source-engineering, NOT trained intelligence

## Research question and hard boundaries

Can a deterministic, versioned finite causal source *verify* (a) old-H0 representational limitation, (b) meaningfully distinct structures modulo all object renamings, and (c) a feasible public inquiry advantage over the best action schedule that never branches on observations? Are there enough independent family ancestries to support a **future** scientific study? These are separate outcomes.

V4 G2b [Draft #157](https://github.com/ryonakayama234/DekaSugi/pull/157) observed BODY effect on prediction (10/24) and no question switch (0/24) for one correlated lag1 motif. V4 G0 [Draft #155](https://github.com/ryonakayama234/DekaSugi/pull/155) certified 12 human-authored semantic orbits but NOT independent family population. These drafts remain untouched, and G0C is independently based on main.

## Fixed typed source contract — G0C-V5-1

- Five Boolean public objects, states 0..31; 15 actions: 10 Set(i,0/1), 5 Pulse(i); history of up to two prior typed actions, chronological.
- An Edge is pulse-triggered at lag 0, 1 or 2; 0..2 guard atoms (current bit, previous pulse, previous set). Edge applies XOR bit mask to its target after any current Set effect. At most two distinct edges per Law; guard contradiction and malformed types fail closed.
- Full declared semantics: 32 states x 241 histories x 15 actions = **115,680** transitions per Law. Includes unreachable counterfactual input tuples; do NOT interpret as experimentally reachable.
- 12 fixed productions with role parameters across distinct triples (up to 720 syntax proposals). Interleave productions so one pattern cannot fill the first batch. Includes intentionally equivalent split guard (bit 0 or 1) vs direct pulse as a negative alias control.
- One proof compares the complete semantics for all 120 simultaneous role renamings. Each disproven permutation has a concrete typed witness; one equality requires 115,680 agreeing transitions. SHA-256 is provenance only, not equality proof.
- A cohort census reports every proposal and alias, number of production roots, representative orbit IDs, and **independent_scientific_family_count: null**. Distinct construction labels or role permutations are NOT independent source families.
- A separate *old H0* proof checks the complete declared semantics against NULL + (3 lags x 5 source x 4 other target) = 61 single-edge unguarded models. OUTSIDE_H0 is only relative to these 61; it is not new primitive invention.
- All proof limits (deadline and resource caps) return NOT_CERTIFIED, never claim mathematical UNID from an incomplete proof.

## Inquiry opportunity certificate

Closed class: 2..8 explicitly listed Laws, initial visible state 0 (or specified), legal action budget B=1..8, uniform prior, deterministic observable successors. Terminal decision is MAP selection of Law identity. The objective is **expected identification accuracy**, not downstream task utility.

The adaptive oracle may branch on each *public after-state* and chooses its next legal action based on that outcome. The open-loop oracle chooses a fixed, possibly time-varying legal action sequence independent of observations; its terminal classifier may use all observed outputs. Both get the same class, prior, action alphabet and budget.

For a deterministic uniform closed class, the expected MAP accuracy of a policy is its number of distinct nonempty observation leaves divided by the class cardinality. The adaptive dynamic program maximizes summed child leaves. The open-loop method enumerates all 15^B sequences, grouping Laws by complete observed response sequences. Exhaustive outputs are exact only for this closed class, initial condition, prior and B.

Safety limits: at most 4,000 fixed schedules, at most 250,000 visited adaptive memo nodes, per-certificate 120 s, and resource caps checked before and during search. B=4 requires 50,625 schedules and must return NOT_CERTIFIED under default limits. The positive and null examples are disclosed **constructed engineering fixtures**: do not interpret an oracle's adaptive gain as a learned active policy or a result across independent families.

## Scientific gates

1. G0C-1: semantic interpreter / independent reference / complete orbit / H0 checks and negative fixtures.
2. G0C-2: adaptive and open-loop exact inquiry opportunities, including positive, null and cap examples.
3. G0C-3: independent ancestry and family-level power preflight. **NOT_CERTIFIED** by this pilot. Generator productions are manually defined and sharing source-root mechanisms; exhaustive full-Hplus is not proven.
4. Future G1/G2: separate-process PUBLIC paid TRAIN -> Sleep -> executable Snapshot -> fresh USE, capacity-matched strong static+active/prior/retrieval/body-off controls. **NOT_RUN** in G0C.
5. Future G3: independently custodied, family-disjoint prospective final test only with separate method approval. Historic DEV/FINAL protected; never rerun.

## Null / counterexample matrix

- Equivalent but different syntax: split guard vs direct => ALIAS, never count twice.
- Distinct old-H0 capacity: current-bit guarded pulse => OUTSIDE_H0 after exact 61-model proof.
- All 120 simultaneous role permutations: invariance checks; full equality proof for representative transformations.
- Constructed four-Law B3 adaptive advantage vs optimal open-loop; constructed two-Law B2 null gain.
- B4 schedule cap => NOT_CERTIFIED, not UNID or no opportunity.
- Incorrect guard, lag, roles, Boolean subclass, missing invalid actions => reject.
- Independent reference implementation checks all 115,680 typed cells of six predeclared Laws.
- Sources, private Law and family provenance must not be exported as learner-side observations.

## Acceptance/status

Engineering-only evidence may be accepted after relevant tests, `python scripts/check_docs.py`, CI exact-head verification and independent code/security review. Nothing in G0C authorizes model promotion or implies scientific L2/L3 improvement. Related [plan](../../experiments/EXP-REP-005-G0C/plan.md), [run](../../experiments/EXP-REP-005-G0C/runs/20261103-disclosed-source.md), [architecture](../architecture/system.md), and [contracts](../architecture/contracts.md).

## P2 exact-head review hardening (2026-11-03)

Source `Law.edges` accepts strictly `Edge` instances, never unchecked subclasses, before deduplication or sorting. All proof deadline arguments must be built-in int/float and finite positive <=3600 seconds; invalid certificate deadlines fail closed as NOT_CERTIFIED, and `signature(deadline_at=...)` rejects nonfinite deadlines. Tests cover forged `Edge` subclass and NaN/infinite deadlines. These remedies followed post-disclosure Codex review; do not retroactively call previous results preregistered science.
