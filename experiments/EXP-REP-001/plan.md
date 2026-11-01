# EXP-REP-001 — Preregistration candidate / integrated workflow
id: EXP-REP-001-PLAN-V1
status: PROPOSED_NOT_FROZEN; NO_TRAIN; NO_DEV; NO_FINAL
approved_direction: 2026-11-01
owner_issue: https://github.com/ryonakayama234/DekaSugi/issues/123

## Experimental claim and model
Primary H1 is the *paired* generalization effect `E_world[accuracy(R3)-accuracy(R2)]` on fresh structurally distinct graph-worlds. Both arms share 256 TRAIN worlds and exactly matched evaluation-world action/observation sequences. Retrieval can memorize episodes but cannot store abstract reusable typed relation templates; R3 can induce templates. R0 is limited-expressivity floor, R1 is strong fixed-expressivity baseline, R4 is R3's same Snapshot with active query selection, R3-ablated isolates the library mechanism. Avoid claims of autonomous primitive discovery outside fixed typed meta-language.

## Candidate data/cost budget — ALL REQUIRE F0 LOCK
- TRAIN256 independent worlds, DEV64 worlds, FINAL1024 worlds; 4–8 objects, 12 interventions per new world, 32 heldout next-state transitions per world. These are planning values, not frozen commitments.
- Per-world score = 32 exact next-state vector matches / 32. R3−R2 paired by **world**. Do not count 32 audits or multiple random seeds as independent worlds.
- Predeclared candidate success: mean paired difference >=0.10 absolute and lower 95% two-sided uncertainty bound >0; report total train+eval CPU, wall, peak RSS, graph-family sensitivity, overlap and concept-ablation effects. Exact inference procedure depends on F0 family sampling: world bootstrap under IID or cluster/family-aware methods if dependence; no posthoc selection.
- Preflight resource caps: set max AST nodes, candidates, primitive executions, wall watchdog and memory after measuring invented fixture resource distributions, before formal source lock.
- TRAIN/DEV/FINAL structurally disjoint under graph isomorphism with objects renamed; preserve class family and difficulty distribution. Independent source/custodian selects confidential roots. No reuse of EXP-0002B, OPPORTUNITY-001 or EXP-COEV-001 holdouts.
- Negative/noisy/partially observed worlds are explicitly secondary exploratory controls and excluded from primary estimand unless newly preregistered.

## Sequence and authorization
**G0 Design**: establish Issue/ADR/spec/ARCH docs/data contracts, review identifiability and alternative mechanism controls.
**G1 Invented-only engineering**: implementation of deterministic world and typed observer, bounded hypotheses, representation learner, Sleep, snapshot, safe evaluator. Run all six conditions on fully disclosed *invented toy worlds* to verify plumbing, not claim H1. Fail-closed adversarial tests and CPU/RSS budget preflight.
**F0 Science and custody gate, before formal sources**: independent critic signs source/seed and sampling law, code/evaluator versions, power and cost evidence, structural disjoint algorithm, confidential custody model, arm order/randomness and precise evaluation CI. If invalid, revise G0/F0 method in new commit and version; no outcome-dependent changes.
**G2 Formal TRAIN and DEV**: source-locked TRAIN experience only; R2 memory and R3/R4 concept learner built from same source episodes; immutable signed or independently witnessed Snapshot hash. DEV run only after snapshot freeze; exploratory fixes tracked and formally restarted where necessary.
**G3 One-shot FINAL**: after distinct **explicit authorization** and independent custodian sign-off only, execute FINAL1024 once with frozen protocol/arms, record per-world paired scores, raw anonymized metrics, costs and evaluator logs. No source-hash adjustment, optional stopping, re-use or unofficial rescoring.
**G4 Interpretation**: prespecified statistical recount, ablation, resource regressions, mechanism verdict; reviewer independent of developer signs ACCEPTED / REJECTED / UNDERIDENTIFIED / NOT_ESTIMABLE. Acceptance of a concept library into `DEFAULT_REGISTRY` is separate ADR, never automatic.

## Threats and gates
Graph signatures, generator functions, hidden target patterns and holdout seeds must never cross into learner process. Source-controlled nominal `hidden=True` is not sufficient if trainer can call hidden methods. Split evaluator uses distinct process/user and preferably independently controlled machine/account for formal research. Same-machine Unix DAC alone is not independent authority. Schema+content hash protects integrity, not secrecy/authenticity. Failed power/cost gate blocks formal work but not invented engineering testing.

## Required artifacts
`docs/specs/EXP-REP-001.md`, `docs/architecture/system.md`, `docs/architecture/contracts.md`, `docs/architecture/decisions/ADR-REP-001.md`, `AGENTS.md`, `docs/INDEX.md`, `experiments/EXP-REP-001/runs/README.md`, code/tests and a verified reproducibility record. Each implementation PR synchronizes the relevant documents.

## Invariance
Historical EXP-0001/EXP-0002B/EXP-0003A/OPPORTUNITY-001/ACTIVE-001/EXP-COEV-001 sources and sealed old evaluation records remain unchanged. Frozen datasets are not rescored. The project does not promise an automatic merge, automatic scoring or research success.
