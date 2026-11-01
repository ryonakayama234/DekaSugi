# EXP-REP-002 design decision receipt, 2026-11-01

id: EXP-REP-002-DESIGN-20261101
updated: 2026-11-01
tags: experiment, design, review
status: DESIGN_ONLY / NOT_RUN / NO_TRAIN / NO_USE / NO_SCORE / NO_FORMAL_DEV_FINAL
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/130

## Examined evidence

- Existing Draft PR #129, 719439fccd: G1-D same-fork topology TRAIN32, B1/B2/B3/B3x exact score 368/384, B5 active 384/384 under changed evidence, B3 414 versus B1 7446 candidate evaluations. These are disclosed engineering measurements not formal transfer.
- Latest Codex review of #129 found three P1 issues: shared search budget, nested Snapshot rank types, observation object IDs validation. New experiment comparison is blocked until repair + adversarial tests + new immutable receipt + exact-head review.
- Prior project design: AGENTS, docs/INDEX, ARCH-001, ARCH-002, EXP-REP-001 method/spec and local rep_lab instructions. Earlier closed or sealed scientific evidence was not read or rescored.
- Reference research: DreamCoder / symbolic library learning with Wake-Sleep and information-theoretic experimental design. No external pretrained model is used.

## Decision

Design candidate EXP-REP-002 with one primary causal mechanism: learned executable concept used to choose a *better next question*. LQ and LA share concept-enabled prediction and snapshot, differing only in the question planner's use of the body. Structurally novel *global compositions* containing local learned motifs form the engineering primary distribution; genuinely novel motifs are negative-transfer controls. Use CPU-only typed grammar, bounded active two-step plans, Wake/Sleep deterministic abstraction, counterfactual DREAM probes and immutable concept snapshots.

Target end-to-end engineering path: correct G1-D P1 -> preflight generator -> actual disclosed TRAIN -> Snapshot save/inspect -> actual local use -> disclosed paired scoring -> independent review. The intended 48-world pilot and budget curves are **not executed**. F0 independently controlled study, formal FINAL and release promotion remain separate approval gates.

## No claims

No experiment code was written in this design-only PR. No new TRAIN episode, learned Snapshot, local use, CPU result, candidate savings, score, formal evidence, official release, CI pass or model promotion is claimed. Design-only edits do not fix G1-D P1 issues. Disclosed toy evaluation cannot be reported as independent science.
