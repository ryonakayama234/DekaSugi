# ADR-REP-002 — Concept-conditioned cost-aware inquiry

id: ADR-REP-002
status: proposed_for_review; design_only
updated: 2026-11-01
parent: Issue #130

## Decision
Build the next experiment as a separate Python 3.12+ standard-library research module, `packages/rep002`, using validated and metered G1-D primitives but no legacy sealed evaluators. Use deterministic typed relational motif learning (Wake/Sleep), finite-world hypothesis sets, two-step active query planning (Dream as simulated counterfactual probe planning) and canonical external Snapshot files. Use CPU-only, bounded pure interpreters and JSON/JSONL/SHA-256.

## Why
G1-D's 32 name-varied training worlds did not establish cross-topology transfer, and positive active scores confound the information actually acquired with the concept used. The new experiment isolates the added value of allowing a concept body to inform the question policy while holding prediction and Snapshot fixed across the primary pair. This is more falsifiable than simply increasing toy accuracy, dataset repetitions or neural epoch count.

## Alternatives
1. Add SGD neural query router now — deferred: gradient/representation attribution confounds and data hunger.
2. Add unconstrained generated Python operations — rejected for this phase: unsafe, unbounded and unmeasurable search.
3. Improve only fixed search — mandatory strong comparator but alone does not test concept-guided inquiry.
4. Use a purely verbal interactive model — deferred until testable external state and evaluator semantics exist.

## Scientific limits
The relation grammar remains human supplied. Full-graph nonisomorphism alone does not prove learned local-motif novelty; explicitly annotate overlap. Learned concept may be wrong, and valid behavior can be abstention. Disclosed engineering scores are not an independent formal study. Independently controlled data source and one-shot FINAL need separate governance.

## Consequences
New versioned contract for Observation, HypothesisSet, QueryDecision, ConceptSnapshot and RunRecord. Every implementation PR updates the system diagram, data-flow/schema, AGENTS, INDEX and dated evidence. Keep G1-D's historical receipts. Fix its three open P1 issues before measured comparison.

Related: docs/specs/EXP-REP-002.md; experiments/EXP-REP-002/plan.md.
