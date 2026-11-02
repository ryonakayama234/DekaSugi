# EXP-REP-005 G0b-A — independent P1/P2 review remediation (2026-11-03)

id: EXP-REP-005-G0B-A-REVIEW-HARDENING-20261103
status: IMPLEMENTED_PENDING_EXACT_HEAD_CI_AND_INDEPENDENT_REVIEW
updated: 2026-11-03
tags: experiment, synthetic, review, security, source-only, stop

## Motivation

[Issue #148](https://github.com/ryonakayama234/DekaSugi/issues/148) / [Draft PR #149](https://github.com/ryonakayama234/DekaSugi/pull/149).
P1: full labeled semantics and syntax role orbit alone missed aliasing under object substitution plus inert Edge.
P2: signatures for an unbounded tuple of models were built before proof limits were tested, permitting severe memory amplification.

## Implemented fixes and adversarial evidence protocol

- Private split auditor checks each law's **exact 30,144-byte semantics over all 24 object permutations**. A renamed direct Edge carrying an inert Edge with an impossible previous-set guard must be rejected across TRAIN and EVAL, both record orders.
- Adaptive-identification and opportunity proof APIs reject candidate classes >64 with NOT_CERTIFIED/CANDIDATE_CAP before allocating signatures; a zero-node request also returns NOT_CERTIFIED before signature work; checked_candidates, missing candidate digest and peak RSS are explicit. Finite valid classes are scanned one signature at a time and semantic aliases are rejected.
- Node cap 250,000. Cooperative wall timeout 120s, RSS observation ceiling 2 GiB; **hard OS process limits still required**. This fix does not independently certify total memory/wall bounds for all runtime environments.
- Tests cover exact P1 alias, 100,000 repeated hypotheses without full-signature allocation, zero-node preflight, duplicate semantics and oversized max_nodes. These are *synthetic* adversarial regressions, not genuine scientific capability measurements.

## Status and evidence chronology

- New code/tests/docs are committed to the Draft #149 branch. GitHub Actions exact-head status: **NOT_YET_OBSERVED** at authoring; report actual run ID and SHA in a subsequent append-only note.
- Full Hplus_G grammar contains 100,090,027 syntax candidates, above 200,000 census cap. The independent-family universe, source ancestry completeness, family-level power, M2/M3 classes, paid TRAIN, learner Snapshots, DEV/FINAL score all remain **NOT_CERTIFIED / NOT_RUN**.
- No historic scored evaluator, protected run, old holdout, or merged main source was changed.

## Exact-head independent GitHub Actions evidence (2026-11-03)

- Tested head: `c9cafa171460ad5bb9d2d06dddf82281a60bf566`. [Dedicated G0b synthetic run 41485212370](https://github.com/ryonakayama234/DekaSugi/actions/runs/41485212370) **SUCCESS**; test step, source-only pilot census and source-only artifact upload succeeded.
- [Research verification v2 41485212233](https://github.com/ryonakayama234/DekaSugi/actions/runs/41485212233) **SUCCESS**; historical source lock, documentation/internal links and explicit synthetic-only tests succeeded.
- These results validate the committed engineering regressions; they are NOT an independent expert methods/security review and do not certify causal-family independence. This receipt update itself is docs-only and requires the usual docs checks. G0b scientific status remains STOP.
