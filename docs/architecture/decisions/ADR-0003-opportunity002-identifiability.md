# ADR-0003 — distinguish capability boundaries before new search or policy interventions

id: ADR-0003
status: proposed; PR1 pending independent review
updated: 2026-10-29
tags: architecture, decision, identifiability, capability, opportunity

## Context
OPPORTUNITY-001 PILOT-V1 produced valid owner-reported one-shot TRAIN64 paired outcomes but no ON-only/OFF-only accuracy opportunity and no B1/B2/B3 wrong eligible choice. The exploratory branch is UNDERIDENTIFIED. Additional learner or primitive changes now would confound representability, search, policy and information quality before the mechanism of failure is distinguished.

## Decision
Select an independent capability/identification design work unit in `packages/evaluation` as PR1, then a separately reviewed synthetic-only independent analyzer PR2, followed by a new independently authorized method if necessary. Reuse `METRO-0001` evidence constructs without reclassifying calibration as cognitive improvement. New metadata contracts `ContrastSpec` and optional `BoundaryCertificate` are analytical/descriptive, not direct commands or new authority to score.

Reject for this first step: modifying the frozen DSL, adding a model/LLM, self-learning on old outcomes, rescoring existing 64, opening DEV/FINAL, choosing n=64 by convenience, and a metrology-only refactor without an identification design.

## Consequences
Positive: explicit reviewable mechanisms; fixed source and information boundaries; decision-based use of later work. Negative: no immediate new capability score; independent proof and evaluator provenance impose work. Reconsider if the reviewed P1–P4 obligations are false or the planned contrasts are structurally non-identifiable. Preserve the negative evidence in the run ledger.

[Spec](../../specs/OPPORTUNITY-002.md) / [Plan](../../../experiments/OPPORTUNITY-002/plan.md) / [Issue #86](https://github.com/ryonakayama234/DekaSugi/issues/86).
