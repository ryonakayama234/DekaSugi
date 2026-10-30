# ACTIVE-001 P0 — F4 operational identification advantage (design-only)

id: ACTIVE-001-F4-OPERATIONAL
status: proposed_operational_definition; bounded_invented_toy_fixture; NOT_SCIENTIFIC_FREEZE
updated: 2026-10-31
tags: active-learning, structural-feasibility, adaptive-experiment-design, no-scoring

Parent [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99), method draft [PR #97](https://github.com/ryonakayama234/DekaSugi/pull/97), Gate F [PR #98](https://github.com/ryonakayama234/DekaSugi/pull/98). This is a stack on #98, which is in turn stacked on #97. No scored target, Oracle response, evaluator-only labels, new split selection or official sampling.

## Population and meaning

H is one nonempty semantic version-space block of classes with the same two PUBLIC predictions. Its n classes carry equal weight **within this structural analysis**. Q is the **64 distinct allowed query input IDs** in ascending order, excluding both public IDs and 64 auditor-only IDs. A response is a hypothetical predicted output from an allowed class, not observed truth. A class h counts as structurally identified after <=2 observations iff its two-question output signature is unique among H; earlier identification (including n=1) counts as identified. Neither accuracy nor real target success is computed.

## Exact objective functions

For a fixed unordered pair q1<q2, let S_N(h;q1,q2) be 1 if no other class in H shares h's ordered outputs on (q1,q2). Define:

N(H) = max_{q1<q2 in Q} sum_{h in H} S_N(h;q1,q2).

For each first question q1, partition H into H_y={h:prediction_h(q1)=y}. For each distinct response y, choose a second q2(y) != q1 and count h in H_y whose prediction on q2(y) is unique in H_y. Define:

A(H) = max_{q1 in Q} sum_y max_{q2 != q1} #{h in H_y : output_h(q2) is unique in H_y}.

The response-contingent q2(y) is a **policy**, not a third question. An already singleton H_y contributes 1 regardless of the second choice. Since the best fixed pair is representable by a constant q2(y), **A(H)>=N(H)**; F4(H) iff A(H)>N(H). F4 is a **nonexclusive subset of F3**: if there is no informative allowed first question, both A=N=0 for ambiguous H; if n=1, A=N=1 but F1, not F4. F2 has A=N=0. This is exactly a structural uniqueness count: alternative metrics (entropy, Gini, expected posterior size, final heldout prediction) require distinct protocol versions.

Tie rules: choose lexicographically smallest best fixed pair, smallest best first q, and for each response y in sorted order choose smallest optimal second q. The probe works on integer *column indices* supplied in ascending allowed-ID order; always map them back through the caller's Q IDs if producing a source-level report.

## Engineering-only bounded reference

\`packages.active_feasibility.f4.probe_f4\` uses only exact tuple vectors of model-predicted outputs and standard-library Counter. Input: 1..276 class rows, 2..64 query columns. Default conservative \`work_upper_bound = 2*n*|Q|*(|Q|-1)\` with \`max_work=50_000\` and a hard cap of 5,000,000 abstract comparison units. This count is **a deliberately conservative algorithmic work proxy, not CPU time or memory and not a derived primitive invocation count**. If upper bound exceeds limit, status is \`not_computed/resource_budget\`, quantitative results \`None\` and **F4 is None**, not False. The limit can only be varied in separate bounded preflight; no automatic all-context census. Independent exhaustive reference enumerates all first questions, all fixed pairs and all response-contingent second-question policies on invented small worlds.

The existing \`census_fixture()\` F0–F3 complete tally, F4_status=\`not_computed\`, and stable hash MUST stay identical. No F4 fraction is claimed or inferred from F3=85.0029%. The complete 91,367-context F4 census is an explicit separate resource decision. Any later F4 percentage must report **both** (i) distinct F3 contexts with F4, and (ii) semantic-class/public-pair-weighted F4 mass (sum of |H|), using exact denominator 331,884 and *nested* F4, never adding it as an exclusive fifth category.

## Interpretation and gates

F4 positive means a **contingent second question permits more unique semantic-class identification than the best two fixed questions**, under the declared uniform-class structural objective. It does not prove Gini B2 is an optimal adaptive policy or predict any measured B2/B1/B1+ heldout performance. No learner action, source freeze, independent scientific review, or actual scored task occurs. P2 must budget CPU before expensive full-census decisions, P3 must check 4096-task statistical precision before true evaluation, and an independent evaluator/source freeze/explicit activation remains mandatory.

[Code](../../packages/active_feasibility/f4.py) / [Synthetic tests](../../tests/test_active_feasibility.py) / [Architecture](../../docs/architecture/system.md) / [Data contract](../../docs/architecture/contracts.md).
