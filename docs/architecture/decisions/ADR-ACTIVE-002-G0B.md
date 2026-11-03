# ADR-ACTIVE-002-G0B — Dual opportunity before learned inquiry

id: ADR-ACTIVE-002-G0B
status: engineering_stop; design_review_and_owner_next_decision_pending
updated: 2026-11-03
tags: architecture, research-method, inquiry, decision

## Context
[G0A #164](https://github.com/ryonakayama234/DekaSugi/issues/164) proves exact constructed **world-aware** terminal prediction-adaptive gain +1/6, but not how a learner without the true source structure can benefit. The [V2 parent #162](https://github.com/ryonakayama234/DekaSugi/issues/162) requires genuine learned action switches and independent downstream prediction benefit. Earlier G0C-3 MAP law-ID population diagnostics found 0/9 certified positive, a different objective. Learning a body that changes predictions without changing questions has recurred.

## Decision
1. Implement isolated `packages/inquiry_landscape` source-only evaluator. Preserve `packages/active_learning`, old score source locks, G0A/G0C Draft stacks and old CI workflows.
2. Separate `WORLD_KNOWN` closed-class gains from `PUBLIC_MIXTURE` gains; neither belongs in learner input. Same true transition law supplies both question answer and hidden audit state2.
3. Use 8x8x8 fully enumerable Boolean source (64 low-index disclosed; 448 distinct source indices), no resampling or posthoc adaptive-positive filtering. Always legal action, B2, unreachable audit context, strongest schedule of lengths 0..2, prediction reward +1/-1/0.
4. Independent exhaustive reference enumerates policies and terminal choices without using production Bellman/payoff.
5. **STOP** on exact public adaptive gap zero; proceed neither to G1 nor to post-hoc grammar modifications. Treat designed source indices as **not** independent natural causal families.
6. Require separate owner research decision, new ID and independently reviewed method for alternative source grammar or representation problem.

## Observed consequence
Complete synthetic local census: 25/448 indexed worlds world-aware positive, but publicly usable optimum **1040/5376 adaptive = 1040/5376 fixed**. STOP. The public source distribution permits a fixed [1,2] schedule matching all adaptive policies in terminal utility. This is exact within stated grammar and does not refute adaptation in other distributions.

## Governance
No historical sealed data or old source lock changed, no learner or scored experiment, no model promotion. CI and latest head independent method/security review are **pending** at the time of the initial local record; passing tests do not authorize merge. [Spec](../../specs/EXP-ACTIVE-002-G0B.md) / [run](../../../experiments/EXP-ACTIVE-002-G0B/runs/20261103-local-stop.md) / [Issue #166](https://github.com/ryonakayama234/DekaSugi/issues/166).
