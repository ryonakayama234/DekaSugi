# ADR-REP-001 — Choose typed, counterexample-driven relational representation learning
id: ADR-REP-001
status: accepted_as_research_direction; scientific_evidence_pending
date: 2026-11-01
issue: https://github.com/ryonakayama234/DekaSugi/issues/123

## Decision
Isolate EXP-REP-001 from EXP-COEV-001 and the EXP-0001 technical baseline. Implement a deterministic finite relational-state simulation and a typed, bounded, counterexample-guided predicate/refinement learner. Evaluate R3 learned cross-world concept reuse against R2 instance-memory retrieval, R1 expressive fixed search, and R4 active intervention choice. Wake/Sleep saves candidate abstractions; Dream is out of the H1 causal estimate.

## Alternatives
1. **Full neural latent world model:** extensible but obscures the mechanism and costs more CPU/data; defer as independent comparator.
2. **Fixed program DSL synthesis:** clear/cheap but does not test acquiring new selection of relational representation; use R1 as comparator.
3. **Counterexample-guided typed relational synthesis (chosen):** explicit, inspectable concepts, bounded combinatorics, strong falsifiable ablations, fits local CPU.
4. **Immediate multi-domain transfer:** more ambitious, but increases distribution/identifiability confounds before relation learning is established.
5. **Search-heuristic-only/active-selector project:** existing related research already tests these; does not isolate representational learning.

## Consequences and limitations
Finite rule-construction meta-language is human-given. A learned predicate is a *new reusable internal relation* but not arbitrary primitive semantic invention. The true success signal is a paired heldout accuracy gain plus concept-specific ablation and matching of episodes/resources. More concepts alone are not success. Preserve immutable Reference Baseline and evolve only reviewed Research Track. Formal FINAL requires future explicit independent authorization. No past frozen data reused.
