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


## G0 refinement: pre-registered witness fixture candidate (NOT RUN)
Before G1, independently review a 4-bit-visible-state, paid `set/pulse` synthetic fixture with an optional one-step public action-history guard. The four-event legal trace proposed in [the diagnostic specification](../../docs/specs/EXP-REP-005-DIAG.md#g0-illustrative-discriminating-world-temporal-aliasing-proposal-not-executed) is a **candidate** for G2; do not treat the hand-derived inconsistency as completed exhaustive testing.

G1 acceptance proposal: enforce charged `set` and `pulse`, canonical ordered observations, explicit initial history marker, source/target role permutation, and no direct truth/generator references in learner-visible records. Make a source-only check that the same public state+action can be reached on two distinct legal histories. Check the exact allowed action horizon; any shorter-horizon negative result is scoped to that horizon.

G2 acceptance proposal: construct finite behavior signatures for H0 and Hplus; verify two contradictory old-model pulse outcomes and a consistent Hplus model; produce a reproducible witness transcript and SHA; test visible-state-conditional H0, delayed-memory beyond Hplus, both-spaces-empty and insufficient-budget controls. Run only synthetic, non-scored verification after separate methods review and approval; preserve all old evidence.

G3+ remain entirely separate. Neither a deterministic analytical witness nor the human-provided Hplus guard demonstrates the agent autonomously inventing it. Capacity-matched preinstalled-Hplus comparison and independent structural-family transfer remain mandatory.


## G0 identification-method correction (2026-11-02; PROPOSED_NOT_RUN)
Use **two** test modes. (1) `same_public_prefix_diagnostic`: fixed paid public history, H0/Hplus finite-semantic witness only. (2) `paired_world_independent_policy`: same hidden target and starting information per arm with independent legal paid question trajectories and matched action/compute budgets; no inter-arm answers. Independent inquiry is the experimental treatment: **do not force identical complete query paths**. If independently run policies naturally choose identical paths, retain those paired worlds in the full comparison. Never exclude coincident paths post hoc or force an arm to ask a different question. Only world, starting public prefix, legal actions and charged/compute budgets are matched.

Before G1 implementation or any G5 score freeze: exact action horizons, structural-family split, paired effect estimands, role permutation checks, abstention failures, stochastic/long-memory negatives, physical execution and training costs, source SHA and verifier design. This is a methodology review proposal, not completed independent G0 approval. See [audit](../../docs/research/EXP-REP-005-G0-identification-audit.md).

## Integrated G0→G6 protocol proposal (2026-11-02, NOT FROZEN / NOT RUN)
The decision candidate [v1](../../docs/specs/EXP-REP-005-INTEGRATED-DECISION-V1.md) now sets a full possible course through actual public paid TRAIN, counterexample-driven repair, Sleep, immutable Snapshot, independent fresh USE, disclosed scoring and independent adoption decision, subject to stop rules. Proposed sample design: 32 TRAIN families ×2 worlds=64, 16 DEV families ×2=32, 32 disclosed EVAL families ×2=64; all family-disjoint across P/R/U/N, minimum total 80 canonical families required or STOP before training. 0/8/16/32/64 TRAIN-world exposures are NOT epochs. Eight matched arms have independent local inquiry histories, up to eight charged actions each; 12 evaluator-only precommitted probes/world.
No split/seed/utility threshold is frozen by this note. The master specification details proposed utility, types, fixed-capacity controls, exact G1–G4 gates, and G5 scope (synthetic disclosed engineering only); a new immutable reviewed plan/manifest and explicit owner authorization are required before actual G1/G2 work or any G5 score. Historical EXP-REP-004R scores remain NOT_RUN.

## G0 shortest witness pilot (2026-11-02; executed METHOD PRECHECK, not G1/G2)
The original illustrative 4-action path has a shorter 3-paid-action contradiction for the specific initial state and guardian: `pulse(source)` → `set(source,0)` → `pulse(source)`. Exhaustive 12-action-alphabet enumeration over horizons 1/2/3 and 24 role renamings is implemented as a **synthetic method-only checker** in [g0_witness.py](g0_witness.py); evidence and remaining blockers in [G0 report](../../docs/research/EXP-REP-005-G0-witness-feasibility-20261102.md). Correct prospective insufficient-horizon control to <=2 for this fixture, not <=3. It is not independently approved G2 evidence. 80 independent structural families not yet certified: full G0 FAIL-CLOSED and TRAIN/USE/EVAL NOT_RUN.


## G0 pilot generator capacity upper bound (2026-11-02; METHOD PRECHECK)
The current `PrivateFixture` source can yield **at most 14 S4-role-orbit classes**: 12 guarded (guard relative to source/target/other × two values × two lags) plus always/never. This is an upper bound, NOT a verified count of independent structural families; stricter meaning criteria reduce it. Hence the current fixture cannot satisfy 20 P and 20 R structural families, much less the proposed 80-family split. The full typed Hplus grammar is not covered by this bound; its generator remains unimplemented. See [G0 report](../../docs/research/EXP-REP-005-G0-witness-feasibility-20261102.md). Preserve 32/16/32 as a *blocked proposal*, not a completed manifest; do not run downstream gates. Independent methods review and an expanded audited family generator remain required.
