# ADR-0005 — isolate active epistemic adaptation before learned query policies

id: ADR-0005
status: proposed; not_accepted; no_scoring_authority
updated: 2026-10-30
tags: architecture, active-learning, science, isolation

## Context
[OPPORTUNITY-001 real TRAIN64](../../../experiments/OPPORTUNITY-001/runs/20261029-train64-real-paired-recount.md) reported identical ON/OFF 48/64 correctness, 16 both-wrong and no unique learning-policy accuracy opportunity; its preregistered outcome remains UNDERIDENTIFIED. OPPORTUNITY-002 synthetic boundary analysis is not evidence of acquired intelligence. Existing legacy DSL has only trim/lower/upper with unary String AST; a small syntax variation alone must not be called new ability.

## Decision
Measure **information-acquisition action** first via a finite deterministic query-selection engine. Make three distinct research stages: I) within-task query adaptation; II) across-task learning of the query policy using Wake/Sleep/Dream; III) independently verified domain transfer. Only Stage I is in scope.
Use an isolated eight-op finite InquiryWorld for new identification opportunities and legacy world only for compatibility checks; **do not modify** historical synthesis, learning, evaluation, source locks, existing CI workflow or scored runs. Uniform semantic-class prior, max Gini disagreement, one-answer oracle, hard-stop integrity failures, distinct independent evaluator. Choose stdlib typed pure Python, no LLM or arbitrary code execution.
Do not add ACTIVE tests to existing CI allowlist without separate review of the exact static whitelist and historic source gate. A local synthetic test pass does not authorize CI scoring.

## Alternatives and rejection
- New primitives in production: increases expression power rather than isolating agency, risks frozen-method confounding.
- Immediate Sleep meta-learner: cannot attribute improvement to query selection versus training, target leakage or memorization.
- Entropy / expected-error acquisition: plausible future comparisons but more implicit weight assumptions or evaluation proxies.
- Existing trim/lower/upper only: very limited semantic equivalence classes in small finite domain, structural underidentification.
- Random policy: retained as essential control, not primary candidate.
- Offline task adaptation alone: lacks a self-selected information action.

## Consequences and gates
Positive: clean hypothesis/answer provenance, finite exhaustive correctness audit, feasible on local CPU, replayable synthetic fixtures, future self-improvement data format.
Negative: artificial tasks, fixed oracle, uniform prior, hand-provided primitives, limited question representation, test-label leakage risk under deterministic world generation, and potentially high precomputation cost. Finite-domain equivalence not proof of global function identity.
Review sources, actual task population and family dependence, power, evaluation authority, external original workflow disabled status and exact-head independent review before main merge or scoring. PR1 documentation, PR2 engineering calibration and PR3 evaluator are distinct reviewable stages.

[Specification](../../specs/ACTIVE-001.md) / [plan](../../../experiments/ACTIVE-001/plan.md) / [Issue #93](https://github.com/ryonakayama234/DekaSugi/issues/93).
