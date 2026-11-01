# EXP-REP-001 G1-D — Full-path experimental protocol candidate v1
id: EXP-REP-001-G1D-METHOD
status: ENGINEERING_TOY_EXECUTED; F0_NOT_FROZEN; NO_FORMAL_DEV_OR_FINAL
updated: 2026-11-01
tags: preregistration, learning-curves, experiment, controlled-comparison
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/128

## Estimands and separately falsifiable hypotheses
- H-D1 (diagnostic validity): if a valid deterministic public transcript excludes every fully enumerated one-edge model, the learner emits `MODEL_CLASS_MISMATCH`, not `UNDERIDENTIFIED`/search-limit; if no complete search, it refuses to certify mismatch. Report confusion matrix, invalid-evidence refusals, false repair triggers, abstention.
- H-D2 (repair fit): bounded two-edge repair can *in principle* explain complete multi-edge world traces not explainable by one-edge, then predict fresh transitions **within that world**. Report repair success conditional on diagnostic certificate, fit and fresh prediction; do not claim cross-world transfer.
- H-D3 (body-specific transfer): on fresh, class-disjoint worlds and identically observed/charged action transcripts, `RepairSnapshot` *body enabled* improves paired exact-vector accuracy or constrained compute compared with both learned rank-only and strong fixed expressive search plus ablation, with equivalent TRAIN evidence and budgets. This is transfer of a constructed representation within a typed meta-language, not genuinely new primitive semantics.
- H-D4 (active information acquisition): with the *same frozen RepairSnapshot*, cost-aware active probes reduce mean charged interventions until identification or improve accuracy under a fixed total charged cost versus frozen passive probes. Keep the H-D4 contrast separate from H-D3.
- H-D5 (learning dynamics): distinct independently generated TRAIN worlds may change body/policy/accuracy; replay of identical episodes 1/2/5/10 passes should leave count-based learner output invariant. Negative or null gains are reportable.

## Arms and valid contrasts
| ID | Initialization / transfer | New-world observations | Interpretation |
|---|---|---|---|
| B0 | one-edge-only H1, no repair | fixed passive | diagnostic expressivity floor; NOT fair primary competitor |
| B1 | fixed full two-edge H2 with exhaustive/bounded typed search, no training | identical passive | strongest untrained expressive comparator |
| B2 | same TRAIN episodes, full H2 + family-frequency ranking, no executable learned body | identical passive | policy-only mechanism control (frequency is itself abstraction) |
| B3 | same TRAIN episodes, executable Sleep role-template body + ranking, bounded repair | identical passive | proposed learned representation |
| B3x | same as B3 but body disabled/replaced, same runtime envelope | identical passive | body-specific ablation |
| B4 | stronger role-neutral bounded episodic retrieval, matched TRAIN exposure and H2 interpreter | identical passive | episodic memory mechanism check |
| B5 | B3 frozen, cost-aware active probes | independent metered active transcript | test-time active acquisition only; NEVER use for B3 vs B2 causal contrast |

For B1-B4 the **same frozen public test-world transcript** must be supplied, regardless of arm predictions. Baselines get the same permissible H2 semantics and comparable search effort. Do not compare B3 to a deliberately handicapped R2 and claim conceptual growth.

## Disclosed engineering pilot (development data, NOT scientific FINAL)
1. Syntax/runtime calibration: one-edge, two independent edges, two gated edges, role renaming, non-identifiable setup, misleading counterexamples, invalid observations, deterministic replay.
2. A *stateful* toy task interface counts each `set_state` and `pulse` and a fixed-price `reset`. Training cannot teleport to `before`; audit-only arbitrary-state probes are kept separate. Warm-start cost, snapshot loading and index construction are separately measured.
3. Learning curve training sizes: unique worlds `n=0,1,2,3,4,8,16,32` drawn as nested prefixes from a documented disclosed pool; 3+ independently solved worlds required to publish a role support. Independently replay identical sequences with `passes=1,2,5,10` to check idempotence.
4. For every n, record full `RepairSnapshot` digest and diff (new/retired body hash, support, ranks), self-test on TRAIN, public diagnostic worlds, pairwise heldout-style **disclosed development** worlds. These development worlds may guide changes and are explicitly nonfinal.
5. Evaluate all arms with identical fixed transcripts for B1/B2/B3/B3x/B4; B5 comparison uses charged actions and its own separately randomized order. Report accuracy, abstention, valid mismatch recall, false repairs, queries, resets, candidate evaluations, primitive calls, CPU process time, wall time, peak RSS, precompute and train cost.
6. Require negative tests: malformed exact types, mutated snapshots, label/graph/seed leakage, query transcript mismatch, repetition conflicts, all-models-empty before later malformed observation, world reset charges, invalid graph canonicalization, source drift.
7. End with a local example: train on disclosed world set, save `RepairSnapshot`, start a fresh stateful world with no graph access, choose and pay for probes, predict an unobserved transition or abstain, print a human-readable trace and reproducible snapshot digest. CLI verbs `train, inspect, use, evaluate-toy` are PROPOSED, not present today.

## Formal methodology candidate — explicitly NOT yet locked
Dataset plan inherited as proposal: 256 independent TRAIN worlds / 64 DEV worlds / up to 1024 FINAL worlds, 4-8 objects, 12 paid actions per test world, 32 **evaluator-private** audit transitions per world. Before F0, run *disclosed* cost/power feasibility simulation to decide final numbers, legal graph families, heldout structural sampling, query allocation, primary contrast and inference method. Once F0 locks parameters, never choose based on FINAL. Holdout data must originate from an independently controlled source, and training may only access documented public IPC.

**Statistical estimand**: for each independent world i let `d_i = (exact_vector_matches_B3_i / 32) - (exact_vector_matches_B2_i / 32)` under the identical passive transcript and fixed resources. Predeclare one primary test (B3 vs B2), report mean paired difference and uncertainty interval using independent-world resampling or family-cluster correction if generation induces dependency. B3 vs B1 and B3x are mandatory mechanism/robustness checks, not uncorrected co-primary fishing. Candidate practical effect threshold `>=0.10` absolute with lower 95% interval `>0` is inherited **not frozen**; also require noninferior correctness against strong fixed H2 if the primary benefit is cost. Predeclare absolute resource ceilings and define missing/timeout/abstention as prespecified penalties, never drop them.

**Claim levels**:
- ENGINEERING_PASS = code, contracts, repeatable toy training/use/score.
- DIAGNOSIS_VALIDATED = complete bounded H1 mismatch detection on disclosed adversarial fixtures.
- REPAIR_DEMONSTRATED = trained model repairs a disclosed multi-edge world then predicts new transitions.
- TRANSFER_EVIDENCE = independently scored body-specific generalization vs matched B2/B1/B3x/B4; no external-domain claims.
- PROMOTED_REFERENCE = separate independent adoption decision and publishable immutable source/snapshot, not an automatic side effect of passing numeric tests.

## Stage/stop boundaries
E0 review stacked #124/#125/#127 safely (not automatic merge) and define graph/test/cost contract.
E1 implement public stateful simulator, complete diagnosis, bounded typed repair, evidence schema and tests.
E2 implement Wake/Sleep snapshot, snapshot replay, disclosed pilot learning curves, and end-to-end local use.
E3 implement matched controls, independent scorer interface, disclosed toy measurements and resources; document failures.
F0 freeze exact fresh methods/seeds/sources, independently witnessed evaluator and power; if infeasible stop formal scoring.
G2 frozen TRAIN + separately authorized DEV; train and freeze snapshots, diagnose.
G3 separately and explicitly approved FINAL one-shot only; do not access previous frozen EXP holdouts.
G4 independent audit/recount, promotion/rejection and optional immutable local release.

## Expected result and honest branch decision
If B3=B2 on heldout worlds: cannot claim body-specific transfer; prioritize learned policy/diagnosis/active inquiries. If B3=B1: fixed expressive search suffices within the measured budget; no arbitrary new-semantic claims. If B3>B2 but B3x does not degrade: body attribution falsified. If within-world repair works but transfer fails: keep diagnosis/repair module as engineering artifact and study invariance/role-binding or broader task family. If setup/CPU dominates: do not promote. If any data/trust/provenance check fails: NOT_ESTIMABLE and no one-shot FINAL retries.

## Preflight review checklist
Hypothesis, world distribution and classes, stateful action costs, arm information parity, independent evaluation privilege, one primary estimand, multiplicity correction if needed, power/resource upper bounds, secrets and hashes, frozen dataset separation, source identity and regression checks, explicit user final authorization and automatic one-shot trigger retirement.

## Executed disclosed toy calibration (not F0 pre-registration)
Engineering implementation now exists in `packages/rep_lab`. Synthetic CI ran 140 tests including TRAIN, Snapshot round trip, use CLI, bounded repair, validation, active 4-action budget and the full disclosed toy pilot. Pilot TRAIN world counts are 0/1/2/3/4/8/16/32, but all named TRAIN worlds share a two-direct-edge fork topology under renaming; this violates formal structural-disjoint independence requirements. The disclosed evaluation has 4 fork + 2 gated-mixture worlds and 64 auditor-only transitions/world. Passive B0/B1/B2/B3/B3x/B4 receive identical 4 public pulse observations/world. B5 chooses at most 4 paid operations under its own public transcript. Same-process host is NOT a formally sealed evaluator. B4 remains weak strict exact-instance retrieval, NOT a strong memory baseline.

Results and negative attribution verdict: B1=B2=B3=B3x 368/384, B0 112/384 with 256 abstentions, B4 0/384 with 384 abstentions, B5 384/384 under its different transcript. One role-body is learned at n=3 without changing B3 scores. Pass repetitions are a snapshot idempotence control, not SGD epochs. For exact artifact SHA, resource timings and interpretation see [dated engineering run](runs/20261101-g1d-engineering-pilot.md). User authorization of engineering work does not waive separate explicit approval for future formal FINAL.

Implemented CLI:
```bash
python -m packages.rep_lab train --worlds 8 --snapshot .run/rep-g1d/snapshot.json
python -m packages.rep_lab inspect --snapshot .run/rep-g1d/snapshot.json
python -m packages.rep_lab use --snapshot .run/rep-g1d/snapshot.json
python -m packages.rep_lab evaluate-toy
```

## G1-D measured constructor ablation amendment, disclosed only
The source-controlled `RepairSnapshotV1` now supplies a typed role-body **constructor**, not only family ranking. On the six disclosed eval worlds, B3 with constructor counted 414 model candidate checks vs B1 fixed H2 / B2 rank-only / B3x disabled 7,446, with identical passive observations and B3/B1/B2/B3x accuracy 368/384. B3 fallback to complete bounded H2 remains part of the protocol if no template-generated candidate fits. One-run measured inference CPU: B3 8.31ms vs B1 11.62ms; setup, training costs, cross-hardware repeatability and stronger fixed heuristics are not normalized. Distinct TRAIN world count 0,1,2 has no reusable template; n>=3 uses one structural body and sharply reduces counted candidates but does not raise accuracy. The unchanged same-family toy cannot be interpreted as independent structural transfer. Separate B5 active query =384/384 on distinct charged evidence. See [versioned experiment](runs/20261101-g1d-template-constructor.md) and [disclosed Snapshot](../EXP-REP-001/artifacts/g1d-toy-snapshot32.json).
