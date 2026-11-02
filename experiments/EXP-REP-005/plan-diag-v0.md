# EXP-REP-005 — diagnostic research plan (proposal v0)

id: EXP-REP-005-PLAN-DIAG-V0
status: proposed_not_frozen_not_run
updated: 2026-11-02
tags: representation, diagnostic, active-learning, experiment
related: ../../docs/specs/EXP-REP-005-DIAG.md
issue: https://github.com/ryonakayama234/DekaSugi/issues/142

## Task for this review
Choose a falsifiable next experiment, not a favorable score. Main owner is FUTURE packages/representation_repair. No code was written or trained by this proposal.

## G0 decision deliverables
1. Independent methods review of H0 and Hplus semantics, prospective structural-family partitions and role/pulse action renaming.
2. Public-only counterexample opportunity proof under a strict action budget; distinguish observation cost from offline exhaustive proof cost.
3. A fixed comparison matrix: H0/P0, H0/Pctx, Hplus/P0, Hplus/Pctx; learned-repair vs preinstalled Hplus, rank-only, episodic, body-off, unrepairable OOD and abstain.
4. Versioned event/snapshot schema with information-leakage checks and fresh-process USE.
5. Numerical thresholds, sample-size rationale, seeds, action horizons, units and stop criteria in a NEW preregistration commit BEFORE any score.
6. Source hash, input family manifest hashes, independent verifier and separated sealed evaluation authority.

## Prospective world partitions (definitions, not generated datasets)
- P: target expressible in H0; potential failure is information acquisition/policy.
- R: target outside H0 but inside Hplus; a legal public counterexample exists within budget.
- U: available public interventions do not distinguish the competing models at the stated horizon; abstention is correct.
- N: target outside Hplus or observations contradictory; no forced repair.
Families must be structurally disjoint by meaning, not superficial object ID, variable renaming or rearranged instances. Existing REP004R public trajectories may inspire controls but cannot become fresh heldout proof.

## Planned operations, not results
G0 write and review contract -> G1 synthetic non-scoring fixtures -> G2 exhaustive expressibility/opportunity witness -> STOP if any gate fails -> G3 new isolated code and fresh synthetic train/use -> G4 comparisons -> G5 new disclosed development score -> G6 evidence synthesis and independent scientific decision. F0/FINAL is a separate future authorization.

## Observation ledger
| Date | Milestone | Run status | Scientific result |
|---|---|---|---|
| 2026-11-02 | docs-only design candidate | NOT_RUN | None |

## Local-model note
Do NOT call a fresh-world exposure sweep an epoch. With any future neural policy, log both independent training-world count and SGD epochs/gradient steps separately. Reserve a new unseen-family test set for every confirmatory model change. No baseline release, model promotion or sealed test is authorized by this document.
