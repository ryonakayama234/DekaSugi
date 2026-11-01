# EXP-REP-003 engineering V1 — Reviewer-corrected reduced-scope implementation
id: EXP-REP-003-ENGINEERING-V1
status: ENGINEERING_DRAFT / DISCLOSED_ONLY / F0_NOT_FROZEN
updated: 2026-11-02
tags: research, engineering, representation, causal-learning, evaluation
issue: https://github.com/ryonakayama234/DekaSugi/issues/133
pr: https://github.com/ryonakayama234/DekaSugi/pull/135

## Independent P2 findings from design review of PR #134
1. The *initial full finite hypothesis space* contains empty and DIRECT models separated by a single pulse. A cherry-picked GATED-vs-EMPTY `set→pulse` example does NOT prove globally two-stage necessity. **Correction:** collect four actual paid public pulse observations at all-zero state, reconstruct `H(o)`, enumerate every legal one-step action to prove NO_OPPORTUNITY, then two-step traces to find a WITNESS. Include the 4 paid conditioning actions: total witness action cost 6. No inference of budget-1 vs budget-2 uplift from this diagnostic.
2. A uniform prior over the exact full hypothesis set plus the same criterion yields equal LQ and LA questions. **Correction:** explicitly define training-induced query prior from executable concept templates; LQ may use it, LA's query API uses uniform semantic prior and cannot see template weights or rankings, although its prediction API uses the same Snapshot as LQ. This tests learned-structure **prior benefit**, not the unique contribution of a body versus a rank-only prior. If LR or ER matches LQ, report POLICY_ONLY/EPISODIC_SUFFICIENT, not concept-body success.

## Implemented grammar subset
n=4, exactly 61 candidate models = 1 empty + 12 direct + 48 typed gated single-edge models; `step(before, pulse(i), model)` XORs each matching target based on **preaction** guard bit, and `set(i,v)` pays one regardless of no-op. Full n4 state/action semantic signatures unique for this one-edge grammar (checked at import and by tests). World generator holds hidden edges and anonymous opaque public IDs. Experimenter-fixed class mixture is a disclosed synthetic convenience, not structure discovery from a broad task distribution.

Canonical public TRAIN observations: for each of 5 representative initial target bit vectors (zero or one-hot), for each of 4 pulse sources, pay 4 sets to place state, then pay one pulse: **100 actions/world**, and infer one consistent model using strictly public `before/action/after` records. Infer group family `EMPTY/DIRECT/GATE0/GATE1` from reconstructed behavior, never from hidden rule labels. SLEEP records abstract guarded-toggle body plus counts of independent named worlds (**not** independent semantic families). DREAM counterfactual planner scores 1-step or set→pulse two-step predictions in the surviving version space, without treating simulations as external evidence.

Use: same public session / model grammar / budget / max 200000 model checks; 7 arms LQ/LA/LR/ER/FA/FX/BODY-OFF. LQ/ER query learned class-conditional priors, LA/FA/BODY-OFF uniform query priors. LR uses class-rank weights for questions but no body-based predictions; FA no TRAIN access and strong finite planner. Negative or null effects acceptable. This is **not** a complete FAIR computation comparison: cumulative TRAIN/SLEEP/FA precomputation is reported but not hard constrained across arms; inference model-check caps are shared.

## Bounded disclosed scoring protocol
4 non-independent strata × 12 index worlds, each arm at B=0/1/2/4/6/8 actual charged actions, 32 deterministic evaluator-only next-state vector samples after frozen prediction; total **2016** world-arm-budget rows. `Y=correct /32`, AULC arithmetic mean over six budgets, report LQ−LA/FA/ER/LR/BODY-OFF per stratum and negative transfer. A complete exact-`head` repeated run is needed for reproducibility. Trajectory predictions are not scored online; only committed final predicted transition function. 32 audit draws and renamed worlds are not independent causal family replicates. No bootstrapped p values or scientific effect acceptance.

## Stop conditions and honest verdicts
- If paid-history NO_OPPORTUNITY proof fails or only 2-step witness found via hidden metadata: INVALID_IDENTIFIABILITY.
- If learner or Snapshot derives topology from host secret rather than public trace: INVALID_LEAK.
- If source/test/docs checks fail: ENGINEERING_FAIL.
- If LQ matches strong FA or LR/ER: FIXED_OR_PRIOR_SUFFICIENT; if LQ loses in novel/distractor, report signed negative transfer.
- An identical deterministic rerun is reproducibility evidence only; scientific independent-review gate and formal F0 remain separate.
- Full 2-edge conditional composition, symbolic variable-binding rule invention, dynamic repair after counterexample and policy/body causality attribution are NOT implemented at V1. These are dependencies for a later full V2, not hidden partial successes.
