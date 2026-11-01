# EXP-REP-004 — Executable Concept Activation: 研究・技術決定稿 V1

id: EXP-REP-004-DECISION-V1
status: DESIGN_DECISION_CANDIDATE / OWNER_REVIEW_PENDING / NOT_IMPLEMENTED / NOT_SCORED / F0_NOT_AUTHORIZED
updated: 2026-11-02
tags: representation, active-learning, executable-concept, wake-sleep, transfer, evaluation
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/136
base_evidence: Draft PR #135, source head 2dbde10ac79decfad03b2c331adb67581fdf94df

> This is a prospective execution contract for one substantial research cycle, not a result. No existing scored/secret holdout may be read or reused. Owner approval is required before scientific preregistration becomes binding; this Draft design does not authorize a formal FINAL or automatic merge/promotion.

## 0. Decision and intellectual target
- **Primary implementation owner:** new isolated packages/rep004 (typed ConceptBody, binding, execution, activation). Supporting: REP003 read-only semantics as historical reference, world-model/inquiry adapter, standalone evaluator and provenance; do not modify scored REP003 source.
- The target is **observe → form a variable-bound executable relation → externalize Snapshot → use it to choose costed interventions → receive feedback → revise/retract → assess on independent new synthetic worlds**. Dialogue and cross-media knowledge are future Adapter targets, not claims tested in this experiment.
- **Decision:** implement and run disclosed engineering Wake/Train, Sleep/Snapshot, inspect/load, unseen-world use and reproducible paired scoring **in one program**, stopping at explicitly stated gates. F0/DEV/FINAL and Local Learning Model promotion require separate source/custody/owner approval.
- **Claim ladder** (report separately): M0 pipeline runs; M1 charged distinguishing opportunity; M2 body inferred from public evidence and truly executed; M3 body intervention changes a predicted transition and an actual legal paid question; M4 positive causal predictive/query effect on new composition worlds relative to matched controls; M5 broader cross-domain or primitive invention (NOT TESTED).

## 1. Failure diagnosis and alternative hypotheses
REP003's 2016 disclosed rows and 288 LQ-vs-LA matched episodes showed identical inquiry actions and equal AULC to FA. Snapshot.library was metadata only; support frequencies were consumed, not bodies. A purported NOVEL stratum was trained GATE0; two-edge OOD caused abstention in untrained FA too. Do not reinterpret these outcomes.
- H1 BODY-EXEC: a program inferred **from charged observations** and stored in Snapshot can be loaded, role-bound, and executed without consulting a hidden world rule or using a precomputed model alias. Null: only fixed template names/priors execute.
- H2 ACTIVATION: at least one prespecified *mechanism fixture* has identical legal history and budget where real body-on vs body-masked planning chooses a different first paid action; body substitution changes an interpreter prediction. Null: no actual behavioral change. Fixture is an implementation assertion, never a score.
- H3 QUERY-VALUE (primary measured): paired mean of budget-AULC (LQ minus LA) on heldout **composition semantic-family clusters** is positive. Null <=0.
- H4 UNIQUE-EXPLANATION (co-gates): LQ also exceeds strong two-edge FA, same-TRAIN rank-only LR, episode-only ER, and BODY-OFF, at matched observation/action/compute resources; if not, report fixed-grammar or policy-only sufficiency. Strong fixed search may match an exact learned-body search even when learning is valid; such parity is intellectually meaningful.
- H5 ROBUSTNESS: on out-of-grammar worlds, uncertainty/abstention is explicit, error and coverage jointly reported; null includes overconfident negative transfer.
- H6 LEARNING-CURVE: distinct semantic training families improve body reuse or query value; replaying identical immutable data is **idempotence**, not SGD epochs. Hypothesis supported only by heldout changes, not body-count growth alone.
- Competing explanations: stronger inherited grammar, training class-prior, lucky identifier/role shortcut, episode retrieval, search depth, query opportunity distribution, simulator/cost accounting bug, survivorship, erroneous abstention scoring.

## 2. Technology choices — chosen versus deferred
- **Chosen:** Python 3.12+ stdlib, WSL2/Linux CPU, immutable dataclasses with exact-type validation, hash-locked canonical JSON/JSONL, small typed symbolic AST, sandboxed *pure* interpreter; deterministic exhaustive finite semantic equivalence and role-permutation canonicalization.
- **Chosen:** bounded cost-aware adaptive 2-step belief-tree planning with exact finite model semantics, separating probability assumptions from facts; support compact bitset/cached transition tables if preflight reveals bottlenecks. Score expected entropy/partition reduction over **whole charged plan**, not a free set operation and not a myopic Gini/2 shortcut. Replan after observed first-step result.
- **Chosen:** variable anti-unification/canonical subgraph mining + negative public counterexample filtering + a bounded minimum-description-length (MDL) criterion. No direct role labels or class names as learner features. Track both exact and heuristic inference states.
- **Deferred:** PyTorch epochs/neural policy, LLM prompt-based rule generator, unbounded Python/eval, external DB, unconstrained SAT/SMT dependency, new primitive meaning invention. These add confounds before the mechanism gate.
- Existing independently reviewed fixed execution and source validation patterns (SEC-004) are reused conceptually, never bypassed by dynamically imported Python.

## 3. Finite world and learnable language
- n=4 visible Boolean objects, all-zero initial state, opaque randomized IDs (role labels unavailable). Legal set(i,v) and pulse(i), each cost one **including no-op set**; reset only by evaluator creating a fresh separate episode.
- Hidden true world is a set of 0–2 distinct conditional/direct edges in the in-grammar study. Pulse simultaneously toggles each target by XOR parity of enabled edges calculated from the **pre-action state**. A guard is either ALWAYS or state(role)=0/1; source/target distinct; guards distinct from these in initial grammar.
- Under n=4 there are 60 syntactic atomic edge choices and at most 1+60+C(60,2)=1831 unordered 0/1/2-edge rule collections *before* semantic deduplication. Exact semantic identity uses every 2^4 state × 4 pulse action; alias/identifier permutation and non-isomorphic structures must be distinguished.
- ConceptBody AST (learned as a *composition* of authorized metaprimitives, NOT invention of metaprimitives): role variables; Pulse(source); GuardIs(guard,bit) or Always; Toggle(target); ParallelXor(list[conditional_effect]) with pre-state semantics. Variable binding is inferred from public transitions; no role hint, generator seed or hidden graph enters learner.
- **Two levels are distinct**: a per-world candidate binding inferred from observations; an *across-world reusable* abstract body whose role variables and applicability/negative witnesses survive at least 3 non-identical, non-isomorphic whole-world training families. A body hardcoded from an existing fixed MODELS entry cannot pass provenance and counterfactual body execution checks.
- If the metagrammar cannot represent a new effect, record REPRESENTATION_LIMIT_CERTIFIED only after exhaustive finite proof; otherwise INSUFFICIENT_EVIDENCE, RESOURCE_EXHAUSTED, DATA_INVALID, BODY_CONTRADICTED or UNKNOWN. Automatic metagrammar growth beyond 2 edges is OUT OF SCOPE for V1.
- A live concept is a refutable hypothesis, not truth. On real counterexample, retract or lower applicability, preserve the counterexample, and fall back to a conservative fixed expressive predictor. Never silently continue with a contradictory concept.

## 4. Critical no-shortcut activation design
1. Train observations are paid Session.apply traces; independent source manifest separates generator-only world rules/seed/class and evaluator-only hidden audit from Wake/Planner/Library.
2. Sleep infers a typed AST from observations; Snapshot contains AST bytes+SHA, variable roles, constraints, positive/negative evidence hashes, source-family-independent support, metagrammar version and status.
3. A *fresh interpreter* loads that AST and applies explicit variable binding to predicted transitions. Instrument body invocation count, binding witnesses, before/after outputs and body hash. A validator rejecting unknown AST/roles/typed fields executes **before** planner.
4. **Body ablation test:** given identical public history and same priors and budgets, body-on versus body-replaced/disabled must change at least one next-state prediction in a chosen negative fixture. Mutation must not change a cached fixed model table instead.
5. **Inquiry activation test:** same matched history/budget yields different first *legal, charged* question under LQ (query sees executing bodies) and LA (query body-masked; final predictor may use same body); verify different actions due to body and not alternative support or seed. Instrument a semantic trace of plan values. Include no-difference control fixture.
6. Mechanism fixtures are handcrafted/diagnostic with predetermined histories and **cannot become treated evaluation worlds**; success demonstrates only exposure of the causal path, not superiority.
7. Query comparisons also include LR (support/rank), ER (episodic analogies), FA (full grammar fixed optimized), FX (fixed schedule), BODY-OFF (both prediction/query body disabled), STATIC-MACRO (same metagrammar with researcher-preinstalled macro); all receive identical legal action menu, trained data where applicable, capped expansions, prediction audit rules and no gold access.

## 5. Data boundaries and exact record requirements
- PublicObservationV1: episode_id, opaque object IDs, initial/current Boolean state, *contiguous* paid (before,action,after,cost,ordinal) records, schema/source versions; reject noncanonical Python subclasses, forged set transitions, gaps, mismatched IDs or unauthorized keys.
- ConceptBodyV1: AST, ordered role constraints, preconditions, effects, binding witness hashes, positive/negative source receipt hashes, support distinct semantic families, body_hash, status candidate/validated/contradicted.
- ConceptSnapshotV1: schema/metagrammar/algorithm/source fingerprint, train manifest hash, train n, concept library, class prior separately tagged, observed cost, provenance hashes, canonical content digest. Verification after save/load must be lossless and fail closed on tamper.
- PredictionCommitV1: pre-audit prediction/ABSTAIN, body execution trace hash, paid inquiry trace hash, unique result checksum, source/snapshot reference, cost and decision flags. Audit never feeds back into that committed episode.
- TrialEvidenceV1: immutable per world×arm×budget record with family key evaluator-only, actual question sequence, concept ON/OFF, audited exact-vector counts, coverage, model checks, expanded primitive AST, training+sleep+dream+inference+question CPU and wall, peak RSS, independent semantic/seed source hash, errors and explicit missingness. Keep confidential audit provenance outside public learner output.
- SHA-256 of raw bytes, committed source SHA, Python environment and test/metric versions. Replays must reproduce decisions, trace hashes and counts; CPU/wall need distributions, not bitwise identity.

## 6. Study and sampling, BEFORE first new score
- G0-G1 feasibility only: exhaustive legal one-step and conditional/adaptive two-step distinction; record TRUE WITNESS vs complete NO_OPPORTUNITY vs capped UNKNOWN, including charged conditioning cost. The REP003 4+2 witness is a historical existence case, not a fresh test and not the global shortest experiment.
- TRAIN-size curve n={0,3,8,16,32,64} distinct semantic families where feasible; record both raw worlds and family/isomorphism hashes. Repeat the identical frozen evidence for passes={1,2,5,10} as idempotence; no "epoch improvement" claim.
- For a prospective **disclosed engineering pilot only**, 4 strata × 12 evaluation worlds = 48, with 12 non-equivalent semantic-family clusters per stratum if feasibility enumeration supports: SEEN_ROLEBLIND, UNSEEN_COMPOSITION (primary), UNSEEN_IN_GRAMMAR, OUT_OF_GRAMMAR (3-edge/guard mismatch). If 12 separate families are infeasible, STOP and revise source design BEFORE any score, never silently relabel duplicates.
- Budgets b={0,2,4,6,8} charged actions per fresh arm episode; 8 arms = 48×5×8=1920 raw trials. n4 evaluator calculates all 16 states ×4 pulse interventions = 64 exact transition checks for each committed trial; that evaluator truth is never a learner input.
- Generator version, family split/permutation canonicalizer, TRAIN and evaluation source manifests, sampling seeds, question budgets, per-episode model/plan limits and statistic code must be **frozen before any disclosed G4 comparison**, then new worlds not touched by G1/G2 fixture tuning. Disclosed pilot is not a sealed/scientifically powered FINAL.
- **Primary estimand:** mean over 12 UNSEEN_COMPOSITION semantic-family clusters of [mean across 5 budgets of exact transition accuracy LQ – LA], treating abstention as zero for this historical-compatible utility. Separately report coverage and selective committed risk, never confuse zero-utility abstention with being wrong.
- Report LQ−FA, −LR, −ER, −BODY-OFF, −STATIC-MACRO, paired first-question-switch counts, body invocation counts, learned concept validity, negative-transfer, cost/accuracy Pareto and resource lifetime. Show sign per family, leave-one-family-out sensitivity and descriptive cluster bootstrap interval; **12 clusters cannot justify general scientific power claims**.
- Positive **exploratory signal** threshold (not formal acceptance): primary mean ≥ +0.02 AULC, positive in ≥9/12 primary families, LQ also ≥ +0.02 against each of FA/LR/ER/BODY-OFF, and no out-of-grammar confident-error rate increase greater than 0.02 absolute; STATIC-MACRO comparison reported without forced dominance. Reaching the threshold DOES NOT prove novel intelligence or warrant model promotion. Any failed control reports NULL, FIXED_SUFFICIENT, POLICY_ONLY, NEGATIVE_TRANSFER, UNDERIDENTIFIED or INVALID as appropriate. If G2 or G3 fail, do not score at all.
- **Costs:** disclose paid observations, model checks, expanded primitive executions, CPU/wall/RSS; total amortized training cost at use horizons N={1,32,128,1024} as (TRAIN+SLEEP+DREAM)/N + inference/use, with fixed search baseline zero training. Do not mix CPU-ms and paid actions into an arbitrary scalar. If bottlenecks require revised caps/algorithms, record a new prospective version before scoring.

## 7. End-to-end gated execution within one substantial work package
- P0 Design (this PR): spec, architecture Mermaid, typed data contract, prereg plan, NOT_RUN ledger, AGENTS/INDEX, exact base, independent research review. Source and original scored archives unchanged.
- G1 Source/security/feasibility: review isolated branch dependency, finite enumerator, semantic class split, legal costed 2-step adaptive oracle, 1- and 2-step positive/negative/capped fixtures; NO score. Stop on incorrect equivalence, leakage or missing query opportunities.
- G2 Implementation/Wake/Sleep: isolated typed interpreter, real paid TRAIN, positive/negative evidence abstraction, saved/reloaded Snapshot, train size/idempotence curves; demonstrate meaningful bodies. Stop if no learned body or role shortcut.
- G3 Actual Use and activation: fresh role-blind worlds, saved Snapshot, explicit paid actions, committed prediction, contradictory/retraction scenario, body-on/off counterfactual and first-action switch with equal evidence/budget. Stop if concept cannot affect behavior.
- G4 Disclosed engineering evaluation: freeze method/source/splits first; run every stratum×arm×budget, all raw outcomes, exact audit 64 state-action transitions, full resource ledger, negative outcomes and replay. Never touch historical/private sealed DEV/FINAL.
- G5 Exact-head independent reviewer, CI, source+raw digest readback, docs/diagrams/contracts/run ledger same PR, final PASS/NULL/NEGATIVE/INVALID report. No auto merge.
- F0 future: independent sampling/power/custody and genuinely fresh sealed holdout, separate owner approval, one-shot FINAL, only then consider Research Prototype → Local Learning Model or release.

## 8. Local user-facing demonstration (G3, no evaluator gold)
~~~bash
python -m packages.rep004 preflight --output .run/rep004/preflight.json
python -m packages.rep004 train --train-worlds 64 --snapshot .run/rep004/snapshot.json
python -m packages.rep004 inspect --snapshot .run/rep004/snapshot.json
python -m packages.rep004 use --snapshot .run/rep004/snapshot.json --world-index 501 --budget 8 --trace .run/rep004/use.json
python -m packages.rep004 evaluate-disclosed --output .run/rep004/pilot.json
python -m unittest discover -s tests -v
python scripts/check_docs.py
~~~
These commands are a **proposed CLI interface**, not yet implemented or run. G3 use produces public observation, question sequence, prediction/abstain and cost. Evaluation uses a separated truth-holding scorer; no fake "learner grading itself" claims.

## 9. Scientific limits and adoption
Even if this passes, it demonstrates **bounded metagrammar symbolic concept induction**, not invention of new primitive semantics, domain-general dialogue or SGD training. Accuracy gains may be absent if an exhaustive same-grammar planner already has all hypotheses. Primary target is a causally active learned representation and its efficiency/generalization consequences. Preserve negative result and continue to dynamic representation repair only when this experiment identifies whether expression, planning or learning is limiting.
References: DreamCoder PLDI 2021 (doi:10.1145/3453483.3454080); Hocquette et al. IJCAI 2024 (doi:10.24963/ijcai.2024/379); repo Issue #136 and measured REP003 PR #135.
