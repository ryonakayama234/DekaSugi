# ADR-ACTIVE-002 — Separate learned inquiry skill from legacy active-query engine

id: ADR-ACTIVE-002
status: proposed; owner_direction_approved; independent_review_pending
updated: 2026-11-03
tags: adr, architecture, active-learning, decision

## Context
Main @ `d9ad80fc844a09c312f6434d20d0d17fdcac4109` includes ACTIVE-001 `packages/active_learning`: a finite fixed semantic Catalog, two public examples and at most two questions. The G0C-3 5-bit/15-action/history2 opportunity certificate and V4 G2b MDL learner are unmerged Draft assets with negative/null action evidence. Generalizing ACTIVE-001 directly risks changing frozen semantics and losing a strong reference baseline.

## Decision
**Research direction approved, implementation NOT approved by this ADR alone.**
1. New prospective `packages/inquiry_learning` contains public-only `BeliefTracker`, `InquiryPlanner`, `SleepLearner` and typed `InquirySkill/v1`. No runnable code is included.
2. Existing `packages/active_learning` remains unchanged as ACTIVE-001's calibrated reference; experiment-specific G0C/V4 code remains on own Draft stacks. Reuse only reviewed source/contract slices through a main-based PR, with versioned compatibility tests.
3. Exact finite Oracle/certifier and target truth remain evaluator-side; training consumes only charged `PublicStep`. A digest cannot establish custody. `python -I` subprocess does not provide OS sandboxing.
4. A two-timescale WAKE belief update / SLEEP typed policy synthesis plus fixed-codec MDL is the primary design. DREAM-generated counterfactuals are tagged model predictions, never independent truth.
5. Separate terminal predictive utility from MAP Law-ID exact certification; separate concept-aided prediction from concept-aided question selection; separate mechanistic positive fixtures from an outcome-unselected population.

## Competing alternatives
- Modify `active_learning` in place: fewer packages but high risk to fixed semantics, historical evidence and comparison validity → rejected for first phase.
- End-to-end RL/LLM training: flexible but high data/compute confounding and no clear expressive-mechanism ablation → deferred.
- Exact planner only: strong fair baseline and opportunity upper bound but does not establish cross-world learned skill → adopted as control, not the learning mechanism.
- Memory retrieval only: provides episodic control but cannot independently establish generalized learned procedure → adopted as control.
- Small neural learner: accepted only as separately capacity-matched exploratory learning-curve arm with recorded epochs; symbolic codec passes are not neural epochs.

## Consequences
More interfaces and small-module integration work; more falsifiability and historical comparability. Typed policy grammar is human-supplied, so success does not prove unlimited autonomous concept invention. Strong STATIC can tie/beat LEARNED; this is scientific negative evidence, not a reason to silently weaken baseline.

## Rejected shortcuts
No cherry-picked positive worlds as population; no claim that altered query alone proves usefulness; no hidden-law supervised policy training; no automatic skill promotion; no background F0/DEV/FINAL; no old source-lock/CI changes; no bulk merge or PR retargeting.

## Follow-up gates
G0 source/opportunity/method review → G1 public belief learner → G2 paid acquisition, Snapshot fresh use and action ablation → G3 independent family-level performance and amortized cost → G4 audit and adoption/rejection. Each step requires its own scoped Issue/PR and dated record, including ARCH-001/002/INDEX/AGENTS synchronization.

Related: [spec](../../specs/EXP-ACTIVE-002.md) / [plan](../../../experiments/EXP-ACTIVE-002/plan.md) / [Issue #162](https://github.com/ryonakayama234/DekaSugi/issues/162) / [governance #146](https://github.com/ryonakayama234/DekaSugi/issues/146).
