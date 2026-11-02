# EXP-REP-005 — G0 methods-only feasibility and research protocol V2

id: EXP-REP-005-PLAN-V2
status: provisional_method_only_not_frozen_not_train_not_scored
updated: 2026-11-02
tags: research, methods, representation, active-learning, feasibility

This main-based G0 engineering pilot is scoped to the 4-object restricted fixture. It preserves prior Draft #145's source-only three-action counterexample and its tests as a selective unmodified port. The independent methodological issues raised on earlier V2 review are reflected here. No archived DEV/FINAL, paid TRAIN, Snapshot learning, or statistical trial is executed or authorized.

## Hypothesis

**H_G0a (method):** an identical visible-state/legal-action pair with divergent successor states can falsify every deterministic memoryless H0 from three real priced public actions, even though a bounded history-aware Hplus can explain them. This alone is neither learned concept invention nor comparative benefit.

**H_axes (method):** representational sufficiency and finite-horizon identifiability are independent axes. Worlds from outside Hplus or stochastic evidence must be correctly diagnosed as negative controls; they are *not* forced into Hplus and should not automatically fail the G2 classification contract.

**H_G0b (future scientific feasibility):** at least 80 *independent structural* world families, in four prespecified M0/M1 × ID/UNID cells, can be independently verified and assigned to disjoint TRAIN/DEV/disclosed-EVAL cohorts, with separately designed M2/M3 OOD/noise controls. This hypothesis is **NOT VERIFIED** by G0a.

## Finite baseline semantics

- Four visible Boolean object bits; initial visible state 0.
- Twelve legal actions: set each object bit to 0 or 1 (eight actions), or pulse each object (four actions); every action has exactly unit cost and there is no reset between steps.
- Restricted evaluator fixture: source, distinct target, guard index, guard value, lag 1 or 2; modes guard, always, never. This is a **tiny subset** of the proposed full typed metalanguage.
- Three-action artificial witness: pulse(source), set(source,0), pulse(source); for the given guard example the two pulse events have same public state/action but unequal successors.
- Exhaustive source-only enumeration on 12^1, 12^2, 12^3 sequences and 24 role relabelings for the fixture. A full G0b equivalence check on the entire Hplus language is NOT provided.
- The pilot fixture supports **at most fourteen role-permutation structural orbits**: always 1, never 1, guard 12. Different orbits may still be semantically redundant. Therefore it is mathematically impossible for THIS fixture set to satisfy the 80-independent-family quota.

## Orthogonal classification and proposed strata

Representation membership is M0=H0 sufficient, M1=Hplus only, M2=outside full Hplus, M3=stochastic/invalid or independently specified probabilistic law. Identification is a second axis: ID=there exists an allowed budget-8, worst-case adaptive decision tree that identifies **all source indexes** of a preregistered, closed, finite hypothesis set from common public initial state 0; UNID=exhaustive finite proof no such tree exists; NOT_CERTIFIED=not fully searched or unsupported contract. Detecting one H0 contradiction and achieving full Hplus hypothesis identification are different targets.

For the synthetic diagnostic, identify_finite_class exhaustively memoizes legal action/outcome branches over (candidate-index set, visible state, last two public actions, remaining actions), with 12 unit-cost actions, at most eight steps, and a hard node budget. All observable answer branches must be identifiable. It returns NOT_CERTIFIED on budget exhaustion. This does not prove real-world identification, does not authenticate events, and does not itself prove membership of the full Hplus semantics.

Primary hypothetical study cells: M0×ID, M0×UNID, M1×ID, M1×UNID, provisionally twenty *independent* families each; additional M2 OOD-grammar and M3 stochastic/noise safety controls are **outside** the 80-cell plan, with counts to be fixed before any scoring. This revises and supersedes the old four disjoint P/R/U/N quota, which was not logically valid.

## Metrics

G0a measurements: minimal priced witness length, counts for horizon 1/2/3, 24 permutations, public chronology validity, number of role-orbit *upper bound* types, exact finite identification status and explored proof nodes, invalid input and search-budget STOP. Never report invented concept, acquired skill, generalization, true independent family count or scored world utility as an engineering method test.

G0b required future measurements: independently certified semantic signatures over full finite scope; role-equivalence; causal structural family/ancestry; class membership proof; reachable H0 counterexample opportunity; complete candidate-set identification; independent family split; time/memory ceilings and method precision/power.

## Acceptance

- G0a engineering PASS is limited to the correctly scoped fixture, negative tests, and CI allowlisted no-score runs. The restricted method precheck can pass while full scientific G0b still fails.
- G0b must **STOP** if a quota cell lacks verified families, the full language is unverified, the uniform decision tree cannot be certified, semantic/source overlap remains, or source custody and independent method reviewer are missing.
- G2 classification is satisfied only when each class has verified correct membership diagnosis, **including correct M2 nonmembership and M3 probabilistic/invalid diagnostics**. It does *not* require Hplus to fit all test worlds.
- G3/G4/G5/G6 TRAIN/Sleep/Snapshot/fresh USE/comparator scoring and model promotion remain NOT_RUN/NOT_AUTHORIZED until subsequent reviewed preregistration.

## Source / architecture / run references

- [V2 decision](../../docs/specs/EXP-REP-005-DECISION-V2.md).
- [ARCH-001 diagram](../../docs/architecture/system.md), [ARCH-002 contract](../../docs/architecture/contracts.md).
- [Main-based witness](g0_witness.py), [orthogonal finite pilot](g0_axes.py).
- [Evidence ledger](runs/20261102-v2-design-not-run.md), [prior Draft #145](https://github.com/ryonakayama234/DekaSugi/pull/145).

Synthetic-only reproduction: python -m unittest discover -s tests -p test_rep005_g0_witness.py -v ; python -m unittest discover -s tests -p test_rep005_g0_axes.py -v ; python scripts/run_research_ci_v2_tests.py ; python scripts/check_docs.py. None invokes sealed scoring.

## G0a実施結果と次のSTOP（2026-11-02）

[G0a CI evidence](runs/20261102-g0a-synthetic-calibration.md): exact restricted finite semantics 16×157×12 = 30,144 outcomes; two candidate laws with identical complete bytes are SEMANTIC_ALIASES and MUST NOT be counted as genuine U/UNID task families. Two genuinely distinct candidates can remain indistinguishable under one action yet become identifiable in two actions, establishing a valid budget-sensitive negative control. This is not a proof that a meaningful 8-action-unidentifiable family exists. Current pilot has at most 14 role orbits, therefore 80 target FAILS. Follow-up [G0b redesign #148](https://github.com/ryonakayama234/DekaSugi/issues/148) requires a new independently reviewed generator and full semantics before any TRAIN or scored EVAL.
