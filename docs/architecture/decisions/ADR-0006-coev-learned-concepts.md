# ADR-0006 — Isolated typed concept learning instead of reusing historical scorers

id: ADR-0006
status: proposed; PR1_design_only
updated: 2026-10-31
tags: architecture, learning, scientific-validity, trust-boundary

## Decision
Create EXP-COEV-001 in independent packages/concept_* modules and a new experiment namespace. Use a small, fully typed G1 AST, bounded inference and deterministic learned parameterized templates. Keep previous packages/learning macro semantics, ACTIVE-001 Stage I, and all historic sealed score artifacts immutable. Do not modify DEFAULT_REGISTRY. Distinguish experimentally supplied G1 L0 power from actual learned L3 abstraction. Separate evaluator via OS process/container and authenticated allowlisted frames before any new official scoring.

## Alternatives
Expanding legacy DSL in place threatens frozen evidence; treating a named macro as semantic invention is false. Neural or RL agents add confounders and cost before basic L3 identification. Continuing ACTIVE-001 solely measures within-task L2 rather than cross-task persistent concepts. This design is constrained but causally interpretable.

## Consequences / risks
G1 is a finite toy world: result does not establish rich-world transfer. Class exhaustion, low opportunity prevalence, inability to freeze honest IID targets, and CPU economics may invalidate planned N2048; must be diagnosed and revised BEFORE evaluation. Abstract templates require safe canonical expansion, exact type validation, provenance, and prevention of evaluator-to-learner feedback. Separate trained snapshots from accepted global skills. Keep docs/process and experiments/EXP-COEV-001 ledger coherent in every follow-up PR.
