# EXP-ACTIVE-002-G0A — Exact finite predictive inquiry opportunity

id: EXP-ACTIVE-002-G0A-SPEC
status: engineering_candidate; not_merged; no_population_inference; no_scored_authority
updated: 2026-11-03
tags: inquiry, exact-oracle, predictive-utility, synthetic-calibration, trust-boundary

## Research question and authority
[Issue #164](https://github.com/ryonakayama234/DekaSugi/issues/164), parent research direction [#162](https://github.com/ryonakayama234/DekaSugi/issues/162). Does a finite deterministic causal-observation table permit strictly greater expected **future legal action prediction** with observation-conditioned decisions than with the strongest precommitted action sequence at the same maximum number of paid steps? This is a **constructed source-only calibration**, not a sample of causal families or a learned AI.

Existing draft G0C-3 [PR #161](https://github.com/ryonakayama234/DekaSugi/pull/161) uses **law-ID MAP** on a different grammar; its null is not superseded. This module is new and isolated on main, without importing V4/G0C draft modules, scorers, model snapshots, hidden DEV/FINAL, historical locks or learner.

## Bounded canonical evaluator-only ClosedWorld
`ClosedWorld(prior, transitions, legal, audit_probes, initial_state, budget)`:
- `prior[law]`: 2..8 **positive exact** integer weights 1..1000; normalized by their total, no learned prior.
- `transitions[law][public_state][action]`: deterministic next observed state, canonical tuple of tuples of bounded exact ints. 2..8 public states; 1..5 action IDs (zero-index).
- `legal[public_state][action]`: exact bool mask, common across hypotheses, no action-specific callback. Closed-world private legal source is declared before certification.
- `audit_probes[probe]=(public_state,action)`: 1..8 **distinct legal state-action pairs** (no arbitrary oracle labels). Evaluator-only true label is computed from the **same trusted transition table** as query results, `transitions[law][state][action]`. A source may designate unreachable legal contexts for unseen generalization checks, as the constructed fixture does with state 2.
- `initial_state`: declared observable state, `budget`: at most 4 paid query steps; legal adaptive stop at every node.
- Each externally provided container and nested primitive is validated for *exact built-in type* before computation. False integers/bool masquerading, tuple subclasses, malformed dimensions, out-of-range transitions and illegal probes are rejected with ValueError. The private source is not a learner observation.

The fixed state table is **Markov**. Causal history dependencies must be encoded in the full observable state or addressed in a future separately versioned model; do not claim history-2 equivalence with G0C source. The learner NEVER receives the full table/audit probes; this G0A module has no learner interface.

## Exact mathematical objective
Let `I` be the remaining law indices and `w_i` positive prior weights. For each precommitted audit `p=(s,a)`, let `c_y=Σ_{i∈I, T_i(s,a)=y} w_i`, `W_I=Σ_i w_i`. At terminal stage the evaluator may predict **one label per audit probe** (correct = +1, wrong = −1) or abstain (0), so unnormalized optimal expected payoff per public information set is:

```text
F(I) = Σ_{audit p} max(0, 2*max_y c_y(p,I) - W_I)
D = (Σ_all_i w_i) * number_of_audit_probes
V(pi) = (Σ_terminal_public_outcome_groups F(I_group)) / D
```

This is **per-probe** optimal prediction, not a joint law-ID guess, and is in [-1,+1] on the stated convention though the Bayes-optimal with abstain is >=0. For general downstream operational utility, a new objective version is necessary.

**Adaptive dynamic program:** `V(I,s,b) = max(F(I), max_{a legal at s} Σ_y V(I_y, y, b-1))`. Output y is the new public state; `I_y` contains hypotheses that transition to y. Memoized exact integer values; tie-breaking prefers stop and then lower action index; policy tree lists public state branches.

**Strong open loop:** enumerate **every** precommitted action sequence of length 0..B. Reject any sequence illegal under **any** possible source law trajectory. Group law indices by complete public outcome sequence, and maximize the sum of terminal `F`. A shorter fixed schedule is allowed; this is stronger than comparing against just one hand-picked sequence or random questions.

Scores and gain return integer numerators with common denominator `D`; no floating comparisons decide equality or improvement. `V_ad ≥ V_ol` must hold. A certified positive is **only** a proof about declared source/prior/initial state/budget/audit probes, not frequency in a population or learnability.

## Fail closed and resource bounds
- Preflight full number of schedules `Σ_{b=0}^B actions^b`; when above `max_plans` return `NOT_CERTIFIED / OPEN_LOOP_PLAN_CAP`.
- Total visited adaptive nodes and transition evaluations each limited; deadline monotonic and finite. `ADAPTIVE_NODE_CAP`, `TRANSITION_CAP`, `PROOF_DEADLINE` all return **NOT_CERTIFIED**, never success, tie or scientific NULL.
- Valid tables may have illegal schedules, no informative actions, duplicate observational signatures and unidentifiable hidden worlds; report exact score and legal-count, not `INVALID`.
- Local result is a mathematical/computational certificate **only under trusted source/table semantics**, not an independent cryptographic proof of source custody or model-agnostic intelligence.

## Deliberately constructed controls
The 4-law branching fixture has three action IDs `Q0`, `QA`, `QB` with per-law visible next-state signatures `(0,0,0)`, `(0,1,0)`, `(1,0,0)`, `(1,0,1)` from public states 0 and 1. `Q0` splits A/B, `QA` distinguishes A, `QB` distinguishes B. State 2 has the same signature and is *unreachable from initial state 0*, but its legal state-action pairs are heldout probes. Prior uniform, budget=2, 3 separate heldout probes: adaptive 12/12, strongest precommitted 10/12, exact positive +2/12=+1/6. **This is NOT a population estimate.**

Negatives: identical heldout state-2 outputs for all four laws while query transitions still vary => both achieve 12/12, so law identifiability does not imply a gain in predictions. No informative public query transitions but distinct state-2 probe results => equal predictions despite unidentifiable law. Nonuniform prior, state-specific legality, B=0/1, strict invalid schemas, resource caps provide additional adversarial checks.

## Limits and extension gates
This source-only proof contains **no** inquiry learner, WAKE/MDL/SLEEP, actual paid WorldAdapter, new random family distribution, hidden holdout split, independent source witness or cross-family test. Its fixtures were explicitly constructed after knowing their expected structure; cannot use them for confirmatory effect estimates or freeze a new true population by selecting only positives. Source-world audit is chosen by the evaluator (for theoretical opportunity), not the learner; a positive bound does not guarantee any realistic learner can discover the optimal policy without audit access.

Prospective G0B requires an independently specified transition grammar, generation/ancestry policy, holdout legal probe distribution, proof-resource power/prevalence feasibility and comparable static policies, before interpreting learned USE results.

Related: [plan](../../experiments/EXP-ACTIVE-002-G0A/plan.md) / [run ledger](../../experiments/EXP-ACTIVE-002-G0A/runs/README.md) / [module](../../packages/inquiry_opportunity/__init__.py) / [tests](../../tests/test_inquiry_opportunity_synthetic.py).

## Independent implementation cross-check (engineering only)
The separate [2026-11-03 brute-force reference](../../experiments/EXP-ACTIVE-002-G0A/runs/20261103-g0a-reference.md) enumerates all lawful depth-2 observation-conditioned policies and all terminal prediction-label/abstention choices independently of the production Bellman/payoff formula. Eighteen deterministic small invented tables match both optimal numerators. This adds confidence in finite-table correctness, **not** a population performance result.
