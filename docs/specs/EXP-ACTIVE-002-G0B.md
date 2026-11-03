# EXP-ACTIVE-002-G0B — Dual opportunity certification / exact finite census

id: EXP-ACTIVE-002-G0B-SPEC
status: synthetic_engineering_stop; public_opportunity_zero; not_F0; draft
updated: 2026-11-03
tags: active-learning, oracle, closed-class, adaptive-query, negative-result

## Research target and scope
[Issue #166](https://github.com/ryonakayama234/DekaSugi/issues/166). Distinguish (1) the **world-aware** adaptive gain when the evaluator knows a particular finite hypothesis class from (2) **publicly usable** adaptive gain when the evaluator knows a public *source grammar and distribution* but not the actual source index. Neither Oracle is a learned system. This work is evaluator-only, disclosed, finite synthetic engineering. The source was designed with knowledge of prior artificial examples; no new independent/scientific power is claimed.

[Parent design #162](https://github.com/ryonakayama234/DekaSugi/issues/162) and G0A [#164](https://github.com/ryonakayama234/DekaSugi/issues/164) remain unmerged Drafts. **Do not import G0A** or claim that two different law-ID/prediction objectives are directly comparable. This study uses the same +1/-1/abstain terminal *predictive* utility as G0A. The independent local reference enumerates all terminal labels rather than using the Bellman payoff shortcut.

## Closed causal world
- Hidden u,v are the two exact bits (00, 01, 10, 11), uniform 4-law prior inside each world.
- Public states 0 and 1: action q emits a single bit f_q(u,v); next public state is that bit, independently of current state.
- State 2: mathematically legal as a heldout probe context but **unreachable from initial state 0** by every q from states 0/1. For actions q0,q1,q2 its outcomes are respectively u, v, u XOR v. These are from the **same deterministic transition law**, not a separate arbitrary label table.
- Initial state=0, paid query budget B=2 incl early stop; all three actions legally available in all public states. Hence no legality difference can artificially disadvantage the nonadaptive schedule.
- Per heldout probe utility: prediction right +1, wrong -1, abstain 0, averaged over three fixed audit pairs state2×q0/q1/q2. No audit source enters any learner input (none exists here).
- Public action semantics: three grammar rows, each with 8 listed Boolean expressions (see [source.py](../../packages/inquiry_landscape/source.py)); full space 8^3=512 indexed worlds. Indices (i,j,k) with all values <4 are a **declared CAL64 disclosed slice**; other 448 make EXT448. **CAL64 is not proven identical** to a previously discussed 64-world pilot and its alleged +1/48 result must not be reported as reproduced.
- Uniform over the EXT448 indexed worlds (not uniform over role-orbits, not independent causal family sampling), then uniform over the four bits per indexed world.

## Value functions and exact proof
For a terminal subset I of weighted hypotheses, prior mass W_I and audit label counts c_0,c_1, the **unnormalized** optimal signed prediction payoff is

```text
F(I) = sum_probes max(0, 2*max(c_0,c_1) - W_I)
     = sum_probes abs(c_0-c_1)  [binary labels only]
D = 3 * sum_all prior_weights
```

The adaptive Bellman recursion with remaining b questions is
`V(I,b)=max(F(I), max_q(sum_{y=0,1} V(I_{q=y},b-1)))`.
For fixed nonadaptive actions, enumerate every sequence of lengths 0,1,2 (1+3+9=13), group outcomes, and maximize the sum of terminal F. No floating-point optimization or posthoc reward shaping. Within one source world use its four hypotheses. In the public mixture use **all 448×4=1792** hypothesis pairs. Identical observational/audit signatures may be compressed by summing integer prior weights; this is exact, not family deduplication.

Report the paired exact gain `(adaptive_numerator-fixed_numerator)/D`, best fixed sequence, optimal tree, and fixed-root contingent gain. The public Oracle knows the **entire grammar and mixture weights**; this is an information-theoretic upper bound for a learner with that knowledge, not a trained action policy.

## Technical boundaries
- New isolated stdlib-only `packages/inquiry_landscape`: `source` (versioned expression interpreter and 512-world enumeration), `oracle` (pure finite value / strong nonadaptive comparator), `analysis` (full census and canonical SHA), and `__main__` (exclusive-create report).
- Exact built-in immutable input checks, no callbacks, network, shell, historical scorer/holdout imports or subprocess. Code accepts only up to 2000 models with bounded positive integer weights, three binary query/audit values and two questions. No arbitrary code execution.
- Independent `tests/test_inquiry_landscape.py` **does not call the production terminal payoff function**; it explicitly tries each prediction label or abstention, all 13 fixed sequences, and contingent 2-stage branch policies. Validates every one of the 512 individual worlds plus the 448 public mixture.
- No external-world model, learner, TRAIN, DEV, FINAL, downstream concept creation, skill promotion, cross-family transfer or natural-population inference.

## Complete engineering outcome and stop
At the original local engineering computation:
- EXT448: 448 attempted/valid source indices, 448 distinct exact *fixed-label* full signatures, 25 world-aware adaptive positives (each 12/12 vs 8/12), 423 exact world-aware NULL. The 448 signatures **are not** 448 independent structural families.
- EXT448 public mixture: adaptive `1040/5376`, fixed `1040/5376`, best fixed `[1,2]`, root contingent gains `[0,0,0]`. The public adaptive opportunity is **exactly ZERO**. Numerators are signed utility, not percent-correct counts.
- CAL64: 64 source indices; 2 world positives, 62 NULL, public adaptive=fixed `304/768`. CAL64 is disclosed/diagnostic, not a new confirmatory holdout.
- All five independent unittest methods PASS locally Python 3.13.5 Linux; canonical full JSON SHA256 `fdb1d686e6aa918c5751df7a51f6a277a2bff51057dfdb1dde1b8b471631a3d8` (88,825 bytes). The exact-head GitHub Actions and latest-head independent reviews must be separately verified before any merge.

**STOP_G0B_PUBLIC_OPPORTUNITY_ZERO**: the new public mixture does not permit strict adaptive benefit. A world-aware opportunity positive does not justify G1. Do not mutate the grammar to fish for a positive after seeing this result. The source's artificial scope does not prove adaptive inquiry never helps elsewhere. Continue only after a separate owner decision for a new versioned distribution/problem.

[Plan](../../experiments/EXP-ACTIVE-002-G0B/plan.md) / [run](../../experiments/EXP-ACTIVE-002-G0B/runs/20261103-local-stop.md) / [module](../../packages/inquiry_landscape/__init__.py).
