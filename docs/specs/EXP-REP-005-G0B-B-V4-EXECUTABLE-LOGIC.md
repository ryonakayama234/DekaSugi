# EXP-REP-005 V4 — Executable logic contracts and falsifiable learner mechanics

id: EXP-REP-005-G0B-B-V4-EXECUTABLE-LOGIC
status: implementation_contract_candidate_not_frozen_not_run
updated: 2026-11-03
tags: science, protocol, finite-grammar, concept-invention, active-learning, evaluator

## Relation to integrated decision
This is a **more concrete implementation contract candidate** for the [V4 integrated decision](EXP-REP-005-G0B-B-INTEGRATED-DECISION-V4.md). It is not executable yet, does not approve paid TRAIN/scoring and must be jointly independently reviewed. It corrects an ambiguity in early proposals: merely storing the G2 feature + observed transition lookup table is *not* enough to predict unseen causal states. The V4 candidate must learn an **executable effect body** and a role-binding procedure, not only a history feature.

## 1. Finite source language

Types: BitState5, PublicAction5, ActionHistory2, Role5, BooleanPredicate, EffectMask5, Law.

- Action = Set(index in 0..4, bit in 0..1) OR Pulse(index in 0..4).
- History = tuple of 0, 1 or 2 previous Action, in chronological order.
- Atom = CurrentBit(role,value) OR PreviousPulse(role,lag) OR PreviousSet(role,value,lag), lag in {1,2}.
- Guard = TRUE OR Atom OR AND(Atom1,Atom2). Contradictory same-bit and mutually exclusive same-lag previous-action atoms are rejected. All orderings normalized.
- Edge = (source role, target role, pulse-trigger-lag in {0,1,2}, Guard); source != target.
- Law = canonical unordered 0,1,2 Edge tuples; exact duplicate Edge rejected, distinct Edge effects onto same target XOR-cancel by parity when both fire. A previous pulse trigger at lag1/2 matches *public* typed history, never hidden evaluator data.
- Before applying effects, compute base(x, current Action); then for each Edge whose pulse trigger and pre-action guard match, XOR its target bit in a 5-bit mask. next_state = base XOR mask, next_history = last two of (history + current Action). Only this semantics is accepted. All tests must compare full typed results with an independently authored reference.

A motif constructor is a **recipe to produce these Laws**. Predeclared recipes: 0 edges; single direct/lag1/lag2; single edge current bit 0/1 guard; previous-action pulse/set guard; 2-atom AND guard; two-edge source→intermediate→target, one-source fan-out, two-source convergence; same source/target competing guarded XOR. Constructors are numbered/frozen before enumeration; role constraints declared per template (distinct where necessary); the apparent inhibitory/feedback name is NOT a new primitive and must either compile through this syntax or be rejected. Generator selection is canonical-recipe order then canonical role tuples then canonical guard atoms; hold source ancestry template and all parents before random instance/role names. This permits source feasibility measurement without the false premise that every syntax is an independent law/family.

G0 proof records full typed semantic byte equivalence over 32 visible states × 241 histories × 15 actions, 120 role renamings, source ancestry and reachable <=8 prefixes separately. Close a finite candidate set C (<=64 semantic laws per proof) **before** ID/UNID proof. No assertion about the complete historical Hplus_G. Source-specific C and secret root/split/target Law stay private; only the generic typed operator/grammar contract is public to both F0 and L2.

## 2. Learner algorithm: actual effect synthesis, not label repair

**Inputs:** paid public episodes per opaque world session. Each observation permits computing a public 5-bit effect mask r = observed_after XOR base(observed_before, observed_action). This mask is data inferred from experience, not hidden source access.

1. For each world session, fit baseline memoryless transition map keyed by (before,action); if same key has distinct observed successors, retain **two complete public causal-prefix witnesses**. Never aggregate contradictory keys across separate world IDs.
2. If a public contradiction is absent, keep H0/unknown models and select an informative legal question; do not hallucinate a concept.
3. If H0 fails, enumerate public-grammar candidate effect bodies with <=2 typed Edge, <=2 Guard literals/edge, <=6 AST operator nodes for the learned reusable template, and at most 4,096 *tested candidates per repair*; candidate checking uses only the paid observed (before,history,action,after), including both zero-effect and nonzero-effect records. A zero mask is ambiguous (no active effect versus cancelling effects), so keep competing hypotheses rather than treat it as a proof of no rule.
4. A candidate is consistent only if its independently interpreted **next full state** matches every observed record in its own world; record all fitting alternatives and their true tested count. Any capped search is NOT_CERTIFIED, not NO_POSSIBLE_PREDICATE. If exactly zero fitting candidates under a fully completed finite search, return OUTSIDE_DECLARED_REPAIR_LANGUAGE, not global impossibility.
5. Group consistent typed bodies across public training worlds by role-variable structural anti-unification; all proposed abstract role bindings must be deduced from **observed** roles/actions/bit transitions. A private source-root or oracle matching label cannot serve as role alignment.
6. Rank/store candidate templates by a review-frozen **two-part MDL** code: cost of public typed serialized body plus cost of public residual exceptions; prefer fewer operators/less exception coding. The precise encoder/bit count must be committed in the G1 code-implementation gate *before G2 data*; no hand-chosen post-score length weights. To avoid falsely turning a singleton memorized law into a transferable concept, reusable templates need evidence in at least two separately observed training world sessions and their withheld-public TRAIN validation episodes; else status=CANDIDATE_ONLY.
7. At test USE, bind learned role variables using **only new-world public paid observations** via canonical bounded matching; if several bindings remain, keep a version space or abstain, not a guessed oracle mapping. Invoke the *learned executable effect body* to produce new-state predictions on unseen legal contexts, with an actual dispatch trace; the old G2 observed-row lookup can remain a fallback diagnostic but cannot count as inferred novel dynamics.

**Interpretation:** candidate synthesis and variable generalization from observations are constrained program induction. This still cannot claim acquisition of unprovided primitive semantics. It can, however, distinguish two very different engineering achievements: (a) reproducing already observed table rows, and (b) evaluating a learned typed causal effect on a new state/history/action.

## 3. Public active inquiry policy

At each new-world public history, create a source-blind bounded set of candidate typed predictors/bindings. Let p(m|public observations) be its declared prior/posterior (uniform in F0, learned from TRAIN in L2 only). For each legal action, compute predicted successor partitions by actually interpreting each public candidate on (state,history,action); choose maximum **expected entropy reduction** under this finite belief, with a frozen canonical typed-action tie-break. Do not enumerate hidden true source-world catalog C or read private source ancestry. Report the exact candidate set/weights/digest, entropy score, action chosen **before** environmental result, paid cost and proof/resource reason. If candidates overflow, sample/truncate via predeclared deterministic rule with status BOUNDED_APPROXIMATE; do not claim exact optimal policy.

Counterfactual body ablation: use *identical saved public prefix, candidate weights, model snapshot and budget*, toggle only learned body dispatch; show alternate legal action/prediction and corresponding dispatch trace. If weights/role binding differ too, it is not a controlled body-only comparison. A legal switch does not prove positive downstream utility; independently score both arms.

## 4. Paired scoring flow and data leakage proof obligations

Two matched evaluator copies have the **same true new-world law and reset state**, but allow F0/F1/L2 independently selected legal paid question sequences. The new-world source root and fully canonical role semantics must be disjoint from TRAIN/DEV; no role-relabel-only split. The evaluator preselects 16 legal reachable prefix/action prediction probes under a source-blind deterministic *public reference prefix schedule*; it can privately simulate the true response but does not expose probe results to learners. Arms score these same probes, even if their active trajectories differ. Log accidental overlap with an arm's paid observation; do not retroactively resample probes. No use of true Law from G0 inside learner AST/role binding.

Primary U = (correct - wrong)/16, abstain=0; evaluate for each world with 8 max paid USE actions and separate costs. Only whole independent family/source clusters count as statistical N. G3 sample size and power depend on G0 attained independent groups, not 16 probes times many seeds. Do not call full Hplus_G certified because a constructed closed C is certified.

## 5. Required property and mutation tests

- Same (before,action), different *same-world* history => H0 conflict; different-world fake conflict => reject.
- A learned effect Edge predicts at least one legal *not-trained-row* transition; body-off mutation changes the prediction; wrong target/source/lag/role flips fail.
- Full 5-bit set-vs-XOR and double-target parity cancellation, lag1/2 boundaries, zero-effect ambiguity, invalid contradictory guards.
- All 120 role permutations preserve full semantics and produce a canonical equal orbit; independent reference returns the same 115,680 typed cells on predeclared fixtures.
- Model source/body/weights cannot read private Law/ancestry/evaluator probe; wrong public sequence/type/paid counter refused; tainted Snapshot digest refused after separate-process reload.
- Proof capped before candidate signature evaluation when <=64 candidate cap is violated; exhausted node/time/memory returns NOT_CERTIFIED not UNSOLVABLE/UNID.
- Positive opportunity includes an actually executable legal policy witness and verified cost/utility, not merely theoretical upper bound.
- STATIC-Hplus and learned body have the **same grammar/meta-operator capacity**, including fixed control with role binding, equal legal action budget and measured CPU/AST calls; no one wins by unequal DSL.
- Negative/hard cases: observational alias, unreachable-only semantic difference, M2 out-of-grammar, M3 stochastic/nonstationary and insufficient independent source groups.

## 6. Engineering output contract
Deliver typed serialized source and public API, reference proof tests, immutable source and learner logs, actual paid Wake steps, explicit MDL encoder/version, executable learned effect body and causal ablation, fresh process/use witness, signed paired disclosed result or precise STOP reason. Update [ARCH-001](../architecture/system.md), [ARCH-002](../architecture/contracts.md), AGENTS and INDEX with the exact code/test/run in each PR. No real V4 experiments have been run or approved by writing this candidate.
