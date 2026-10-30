# ADR-0007 — ACTIVE-001 B1+ informative-uniform control

id: ADR-0007
status: proposed_engineering; NOT_SCIENTIFIC_ADOPTION
updated: 2026-10-31
tags: architecture, active-learning, decision, research

## Research decision
B1 (uniform-random-v1) chooses from all unasked question IDs if any positive-Gini choice exists. B2 (max-disagreement-v1) chooses the maximum exact integer Gini numerator. Their contrast confounds avoiding uninformative questions and ranking informative questions. Introduce **B1+** (informative-uniform-v1) strictly as an additional **secondary synthetic engineering control**, without changing B1, B2 or the proposed primary comparison in draft PR #97.

## Alternative review
1. Replace B1 by B1+: reject; breaks existing baseline, digests and prospective primary estimand.
2. Duplicate the entire inquiry engine: reject; diverging replay, source trust and budget checks compromise comparability.
3. Add one policy to the canonical selector, updater and history replay: **adopt**; preserves common InquiryWorld, state, final program and 2-query budget.
4. Introduce learned cross-task acquisition: defer to Stage II, where it must have separate data and transfer tests.

## Exact contract
- Public API: \`propose_informative_random(session, catalog, *, seed)\`; policy string \`informative-uniform-v1\`.
- Only exact Python integer seed \`0 <= seed < 2**63\`. Let \`remaining\` be ascending unasked query IDs. For q compute \`g(q)=|H|**2 - sum_y n_y(q)**2\` using the internally built canonical catalog. Filter \`g(q)>0\`; if empty return \`None\` without inventing identification.
- Otherwise sample \`random.Random(f"active001-informative-uniform-v1:{seed}:{session.commitment()}").choice(positive_ids)\`.
- The original B1 choice pool and RNG string \`active001-random-v1:<seed>:<commitment>\` remain exactly unchanged. B2 remains deterministic, stable-ID argmax.
- All outcomes have original \`QueryProposal\`, \`QueryAnswer\`, \`QuerySession\` and \`active-query/2\` digest schemas. \`update\` and \`_assert_world\` replay the **exact policy, seed and choice** at each historical prefix; preserve \`identified\`, \`query_unidentifiable\`, \`budget_exhausted\`, \`model_inconsistent\`.
- The engine may replay mixed-policy histories, but a future independent *scientific evaluator* must enforce one policy per arm and isolate target/auditor-only labels. A local receipt digest is not independent Oracle authentication.

## Falsifiable scientific interpretation (future only)
\`Delta_total = E[A(B2)-A(B1)]\` (draft #97 primary), \`Delta_avoid = E[A(B1+)-A(B1)]\` and \`Delta_rank = E[A(B2)-A(B1+)]\` (secondary), so \`Delta_total=Delta_avoid+Delta_rank\` at matched task laws. These differences are not fully separated causal mediators; information acquisition alone is not measured heldout prediction. No new confirmatory testing family, statistical freeze, source/seed lock or scoring is authorized. F4 is a separate structural opportunity analysis.

## Engineering acceptance and safety
Positive-only seeded choice, independent semantic-output reference, complete replay for 1st/2nd question, zero-informative F2 context, seeded B1/B2 preservation, type/seed/proposal tampering refusal, and <=2-question limit. Use existing explicitly allowlisted synthetic unittest and safe docs/source gates ONLY; do not run historic evaluators, unlock frozen datasets or enable the original disabled workflow. Future CPU telemetry (\`active-selection-diagnostic/1\`) and new 12-arm cost plan belong to Issue #99 P2, not this P1 commit. CI and Codex review do not independently validate scientific efficacy.

[Architecture](../system.md) / [Contracts](../contracts.md) / [Run gate](../../../experiments/ACTIVE-001/runs/20261031-b1plus-p1-engineering.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).
