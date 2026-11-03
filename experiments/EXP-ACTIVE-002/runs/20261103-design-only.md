# EXP-ACTIVE-002 — 2026-11-03 V2 owner design approval

id: EXP-ACTIVE-002-DESIGN-20261103
status: DESIGN_ONLY; OWNER_DESIGN_APPROVED; METHOD_NOT_FROZEN; NOT_RUN
updated: 2026-11-03
tags: design, owner-approval, not-run, provenance

## What happened
Owner explicitly agreed to the V2 research direction in conversation on 2026-11-03. Registered as [Issue #162](https://github.com/ryonakayama234/DekaSugi/issues/162). This main-based Draft PR proposes written research hypotheses, alternatives, typed dataflow, architecture, PR gates and falsifiers. It does not implement code or invoke source generation, learner TRAIN, synthetic model scoring, DEV, FINAL or the historical evaluation workflows.

## Source/provenance
- Repository: `ryonakayama234/DekaSugi`.
- Verified base-main commit at design intake: `d9ad80fc844a09c312f6434d20d0d17fdcac4109` (2026-10-30).
- Source comparison: main ACTIVE-001 versus unmerged G0C-3 (#161) and V4 G2b (#157); draft evidence not promoted.
- The current Draft PR head, CI and independent review outcomes are **not known at time of this initial document authoring**; add separate append-only receipts when verifiable.

## Planned/not observed
- New `packages/inquiry_learning`: NOT_CREATED.
- New sampling/family census/Oracle certification: NOT_RUN.
- New paid TRAIN, learned Snapshot, experimental USE: NOT_RUN.
- New paired utility data, numerical acceptance, transfer generalization: NOT_RUN.
- Independent method/power/security review: PENDING.
- Formal model/method freeze and sealed FINAL: NOT_AUTHORIZED.

## Gate to implementation
Resolve review findings and verify docs/CI at exact head. Freeze a separately approved methodological version with semantics, family independence, power, comparator fairness and cost accounting *before* opening new scored evidence. See [plan](../plan.md) and [spec](../../../docs/specs/EXP-ACTIVE-002.md).
