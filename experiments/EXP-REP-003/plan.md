# EXP-REP-003 — Opportunity-first research pre-registration DRAFT
id: EXP-REP-003-PLAN-V1
status: PROPOSED / NOT_RUN / F0_NOT_FROZEN
updated: 2026-11-01
tags: experiment, preregistration, active-learning
issue: https://github.com/ryonakayama234/DekaSugi/issues/133

## Primary question
Can a learned executable causal concept improve which **paid, reachable** experiment to run, above an optimized fixed active policy, under anonymous roles and conditional two-stage dynamics? The current REP002 direct pilot gives no such attribution; do not infer a positive result.

## Sequence and gates
1. **Design-only PR**: contract/spec/architecture/data flow/runs/AGENTS/INDEX; independent method review. No new code execution or scores.
2. **Opportunity calibration**: synthetic finite-state ground truths and two-step reachable action sequences; enumerate exact semantic transition signatures, graph ID permutations and distinguishable reachable transcripts. Return WITNESS / NO_OPPORTUNITY / UNKNOWN. Test the negative paths and false-identifiability signatures. Record both success and non-opportunity cases.
3. **Cost and fairness preflight**: common primitive-node / rollout / model-check ledger; enforce identical caps in every comparator including learned macro expansion, fallback and hypothetical information gain. FA may use a strong, budgeted two-step planner. Reject leaks from hidden labels/edges/audit.
4. **Public engineering learning**: Wake observation traces, Sleep typed relation + applicability + counterexamples, Dream falsifying hypotheses, canonical typed saved Snapshot; CPU local inspect/load/use. TRAIN 0/3/8/16/32/64 count **and distinct topology/semantic families**, plus repeats 1/2/5/10 as no-new-evidence control.
5. **Disclosed comparisons**: independently generated worlds, fixed 0/2/4/8 horizons (or different horizon only if frozen ahead of score), arms LQ/LA/LR/FA/ER/FX/BODY-OFF, auditor-only scored transitions post PredictionCommit; record each world and family, negative-transfer failures, full lifetime cost.
6. **Separate formal gate F0**: external independent review, generator-source/custody and statistical power, preregistered estimand & threshold, permission to score DEV and separately one-shot FINAL. Not covered by this draft.

## Primary metrics (planned; not frozen)
Per-world paired delta AULC(LQ−LA) and AULC(LQ−FA), together with LQ−BODY-OFF; costs for both learner and training amortized over use count. Exact likelihood or heuristic proxy must be specified before measurement. Preliminary **mechanism-positive** requires all attribution controls and meaningful disjoint generalization, not merely an engineered advantage over a weak FA. Null, role-prior sufficient and negative transfer are acceptable outcomes.

## Model freeze
ResearchPrototype remains non-released. A checksum of saved Snapshot proves integrity only, not science. FrozenReferenceBaseline will be considered after exact-head CI, independent review, runnable WSL2 train/inspect/use, stable contract, reproducible publicly disclosed evaluation, and documented limitations. No model is promoted in this plan.

## Prohibitions
No changes to historical DEV/FINAL; do not use or upload the private Google Drive scored-ledger; no automatic merge; no manipulation of researcher-held audit gold through the learner. This plan records NO training/experiment/CI.

## Hypothesis
In anonymous conditional worlds where costed setup→pulse can distinguish observationally equivalent candidates, learning *executable causal concepts* may improve active inquiry beyond a strong fixed policy. Null is plausible and acceptable.

## Metrics
The pre-scoring opportunity detector reports WITNESS / NO_OPPORTUNITY / UNKNOWN, minimum charged discriminating trace length, and exhaustive coverage. After a separately frozen scoring protocol, per-world AULC(LQ−LA), AULC(LQ−FA), AULC(LQ−BODY-OFF), negative transfer, abstention and fully expanded lifetime cost are reported. Repeated transitions in one world are not independent samples.

## Acceptance
This DESIGN_ONLY task is complete when the synchronized specification, plan, run receipt, AGENTS/INDEX, architecture and data contracts are reviewable, contain no ungrounded result claim, and pass link/metadata checks. It does not authorize code, scoring or release. Later engineering must include false-positive/negative witness tests, identical bounds, independently checked predictive commitments, and honest null-result recording before any scientific promotion.
