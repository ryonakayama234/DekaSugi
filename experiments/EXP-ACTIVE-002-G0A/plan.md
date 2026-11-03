# EXP-ACTIVE-002-G0A — Exact predictive opportunity engineering calibration

id: EXP-ACTIVE-002-G0A-PLAN
status: engineering_fixture_only; not_frozen; no_formal_scoring
updated: 2026-11-03
tags: plan, synthetic, proof, exact, calibration

## Hypothesis
There exists a **constructed** finite Markov transition world, fixed prior, state/action legality, maximum two paid observations and evaluator-only predeclared legal prediction probes such that observation-conditioned adaptive questioning has higher terminal optimal predictive value than **every** legal fixed action schedule of 0..B steps. The same certifier must return exact NULL when extra identification is not relevant for the prediction task, and `NOT_CERTIFIED` on resource exhaustion.

This is a calibration of source-and-Oracle mechanics, NOT a population inquiry-prevalence survey, actual paid training, learned policy, formal heldout or predictive generalization science.

## Source model
[Specification](../../docs/specs/EXP-ACTIVE-002-G0A.md). Source-law index and full tables are evaluator-owned. Deterministic transition labels are from the **same** canonical transition as query observations. Public initial state, 2..8 visible states, 1..5 actions, 2..8 laws and positive integer prior weights. Evaluator audit probes are 1..8 distinct legal state/action pairs. Budget B<=4 incl B=0; stop is legal at every adaptive node, fixed precommitted plans must remain legal under every candidate hidden law. No human user data or historical sealed source used.

## Controls and execution
- Constructed early branching four-law positive where 2 questions cannot precommit a universally optimal sequence. Unreachable state 2 with distinct legal probes checks unseen transition predictions.
- Constructed zero predictive advantage despite available law-ID distinction: all future legal probe outputs the same.
- Constructed no-information public source (but heterogeneous heldout predictions), nonuniform priors, state-dependent illegal fixed schedules, zero/single question budget.
- Resource-cap, malformed input, exact types and state-transition negative tests.
- Run **only** `python -m unittest discover -s tests -p 'test_inquiry_opportunity_synthetic.py' -v`; CI runner adds this named file to its explicit synthetic-only allowlist. No broad unittest discovery, generator, learner, old DEV/FINAL evaluator, archived research workflow, unbounded enumeration or external network.

## Metrics
- Primary **engineering**: certifier's rational `gain_numerator / score_denominator`, separate adaptive/open-loop integer numerators and actual complete-schedule count; positive witness should be 2/12 on declared constructed model. Exhaustive algorithm's ability to reject invalid, zero and unknown states is equally important.
- Correctness: actual legal schedule eligibility across all potential world trajectories, public-state observation branching, abstention payoff, positive prior weighting, no floating decisions, exact witness.
- Safety: no imports of private historical modules/learner/evaluation, strict validation and fail-closed caps, no unreviewed workflow scope changes. CLI/test result local CI receipts must attach exact source head and distinguish test PASS from scientific study approval.
- **No** population mean, confidence interval, cross-family sample size, independent prior/grammar proof or trained model score is measurable in G0A. A positive 2/12 is *not* EXP-ACTIVE-002 H3/H4 acceptance.

## Acceptance
- [ ] Exact source code and independent tests committed in isolated module, all required malformed/legality/resource fixtures PASS.
- [ ] All existing historic source locks and original CI workflow bytes unchanged; successor safe runner only explicitly includes the synthetic-only test, no broad discovery.
- [ ] AGENTS.md, docs/INDEX.md, ARCH-001 Mermaid, ARCH-002 data flow, packages/README, spec and dated measured engineering record synchronized in the same Draft PR.
- [ ] GitHub PR-head CI `Research verification v2` PASS including new 8+ tests and docs, plus independent newest-head code/security review with no unresolved P0/P1 before main merge *consideration*.
- [ ] No source-family prevalence inference, real learned-policy results, TRAIN/DEV/FINAL execution or unreviewed method freeze.

## STOP and future
`NOT_CERTIFIED` for any certificate cap; `ValueError` for noncanonical tables; `NEGATIVE` is valid zero gain, not loss of proof. If numerical witness, input legality, independent tests, source locks or trust boundary fails, STOP. Follow-up G0B is a separate preregistered source distribution, public observation protocol, semantic-family grouping and opportunity-prevalence/power study, contingent on independent review. Owner's general implementation delegation does not waive formal sealed FINAL activation or code review.

[Issue #164](https://github.com/ryonakayama234/DekaSugi/issues/164) / [run index](runs/README.md) / [parent issue #162](https://github.com/ryonakayama234/DekaSugi/issues/162).
