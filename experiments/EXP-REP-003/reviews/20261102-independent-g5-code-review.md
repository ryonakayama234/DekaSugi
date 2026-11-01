# EXP-REP-003 — G5 independent code/method review, corrected verdict
id: EXP-REP-003-G5-REVIEW-20261102
status: INDEPENDENT_REVIEW_FINDINGS_P2 / ENGINEERING_CI_PASS / BODY_EFFECT_NOT_TESTED
updated: 2026-11-02
tags: review, research, negative-result, provenance
pr: https://github.com/ryonakayama234/DekaSugi/pull/135
design_pr: https://github.com/ryonakayama234/DekaSugi/pull/134

## Independent review of PR #135
Codex independently reviewed current implementation commit 07e16e787b477f61fb20651d781f67e6ac5e09ee and found two P2 methodological defects.

**P2-1: NOVEL is an incorrect semantic label.** The source constructs these worlds with GATE0, which is present eight times in TRAIN64 and explicitly supported by its fixed grammar. This tests held-out public IDs of a SEEN semantic family, not novel semantics. CONDITIONAL_TRANSFER similarly uses already-seen GATE1 and is not multi-edge composition. Source now explicitly maps legacy stratum names to their real meaning via STRATUM_ACTUAL_MEANING. Preserve old archive keys and bytes, rather than altering source seeds after score.

**P2-2: learned Snapshot library body NOT EXECUTED.** TRAIN infers public-evidence structure class counts, and the library stores *descriptive* guarded-toggle rule annotations. At runtime, validation checks the library, but only support frequencies feed prior(); actual step(), choose_action() and prediction execute the fixed predeclared MODELS, not any learned program body. Therefore no acquired executable body was actually used, and BODY-OFF is **not a valid learned-body intervention** in this version. Correct language is **learned categorical prior over researcher-defined classes**, not independent predicate invention, executable representation transfer, concept-body necessity or neural epoch learning.

## Correct measured interpretation
- G1 opportunity: after 4 paid zero-state pulses, all 12 one-step operations exhaustively fail to distinguish 25 hypotheses; a further 2-operation legal set→pulse has a WITNESS. Total cost **for this conditioned history** = 6, not global minimum from scratch or identification of actual true model.
- G2 actual paid TRAIN64 operations = 6400, but only 4 structural classes; new IDs do not provide independent semantic families. Snapshot save/load integrity and local CLI usage are implemented.
- G4 2016 disclosed world/arm/budget records and 64512 evaluator-only transitions: LQ=LA=FA=LR=ER=BODY-OFF across all four strata, and **ZERO different LQ-vs-LA question sequences among 288 paired cases**. This is a failure of the experiment to activate concept-to-question causal treatment, not proof all such learning is impossible.
- Two-edge distractor failure occurs also in untrained FA: at budget8, all 12/12 OOD worlds ABSTAIN with scoring zero. FX accuracy advantage is due in part to the abstention rubric and cannot be called learning-caused negative transfer.
- **ENGINEERING REDUCED-PILOT PASS** (subject to final exact-head safe CI); **QUESTION MECHANISM UNEXPOSED / BODY MECHANISM NOT IMPLEMENTED**; **SEMANTIC NOVELTY NOT TESTED**; **F0/DEV/FINAL NOT RUN**. No frozen model promotion.

## Historical preservation and next gate
Original measured receipt: [20261102-g0g5-reduced-engineering-measured.md](../runs/20261102-g0g5-reduced-engineering-measured.md), with complete [v1.1 raw archive](../artifacts/20261102-reduced-pilot-v1_1-raw.json.zlib.b64) and [summary](../artifacts/20261102-reduced-pilot-v1_1-summary.json). The raw keys remain the historical source labels while this review provides the scientifically correct interpretation. No post-hoc world cherry-picking or retroactive F0. A future design must actually execute learned variable-bound relation bodies and demonstrate query-policy switching before any scored attribution test.
