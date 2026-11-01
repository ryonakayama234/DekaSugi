# EXP-REP-002 — Final-candidate integrated research design
id: EXP-REP-002-SPEC-V1
status: DESIGN_FINAL_CANDIDATE; NOT_IMPLEMENTED; NOT_SCORED; NOT_F0_FROZEN
updated: 2026-11-01
tags: experiment, active-learning, wake-sleep, representation, evaluation
owner: Issue #130
lineage: EXP-REP-001 G1-D Draft PR #129, head 719439fccd50e2d03c3b39319c86cbd43394887d
primary_module: new isolated packages/rep002 (reusing audited rep_lab interfaces)
support: packages/active_learning, packages/relational_world, isolated evaluator, docs/tests

## 0. Research decision and limits
The research object is NOT "get 100% accuracy on a toy". It is the counterfactual contribution of a persistently learned, executable *relational motif* to selecting the next costed observation when confronting a structurally novel composite world. A genuine effect requires differences against an equally expressive, equal-information, budget-matched solver with the same concept body available for prediction but not to its query policy. No claim of unrestricted semantic invention or general intelligence follows. Current human-provided typed meta-grammar bounds expressivity.

Proceed end-to-end for a **fully disclosed engineering study**: correct -> train -> save -> inspect -> load -> use on fresh disclosed worlds -> scored audit -> independent code review and evidence ledger. Scientific independent TRAIN/DEV/FINAL is a distinct, later F0 gate and must not silently execute. Existing sealed evaluations and original dated G1-D measurements are immutable.

## 1. Status and blocking defects
G1-D public toy: 32 named but same fork topology TRAIN worlds; B1/B2/B3/B3x all 368/384, B5 with different paid observations 384/384, B3 414 candidate evaluations vs B1 7446. The current PR #129 review on 719439f reported 3 unresolved P1 defects: template-to-H2 fallback does not subtract earlier attempted pairs; inner atom_rank exact tuple validation; Observation.object_ids exact tuple/str before any comparisons. Before any new claimed comparison:
- repair each P1 with fail-closed adversarial regression; verify shared candidate budget across all phases, including query planning;
- rerun baseline and record a NEW immutable dated receipt, retaining old receipt and snapshot; if scores change, explicitly supersede comparisons;
- pass exact-head safe CI, docs validator and independent review. No merge or formal FINAL by default.
No new code is included in THIS design-only PR.

## 2. Operational constructs and causal assumptions
Intelligence-in-process = iterative change in (i) questions/actions, (ii) hypotheses/predictions, and (iii) externally retained concepts, with verifiable improvement on nontraining worlds. Its **measured manifestations** are not synonymous with an abstract intelligence score.
- Active acquisition: selecting an allowed operation given current public state to reduce expected *prediction-relevant* uncertainty per charged unit.
- Executable concept: a type-checked, object-name-invariant, parameterized relation-body plus applicability, provenance, counterexamples and falsification profiles. Semantic primitives remain fixed.
- Composition transfer: the heldout full relation graph is non-isomorphic to every TRAIN graph but contains reusable local motifs; system must reuse learned motif while adapting the global composition.
- Novel-motif negative transfer: heldout world requires a motif absent from TRAIN; correct behavior is uncertainty, probe, fallback or abstention, not forced inappropriate reuse.
- Representation failure: complete enumeration of a declared class H_k yields no model consistent with every valid public observation. Incomplete search NEVER certifies a model-class failure.
- Identifiability: distinct surviving models predict identical answers on reachable experiments => underidentified; neither active learning nor more epochs can resolve it without richer observations.

## 3. Exact research hypotheses
H-Q (primary mechanism): on compositional heldout worlds, with the same frozen concept Snapshot and identical **prediction** mechanism, allowing the active **question policy** to consult executable concept-body/counterexample applicability yields a positive world-paired area-under-budget learning-curve effect against an otherwise identical concept-blind active policy.
H-R (secondary representation): with equal TRAIN exposure, active-query algorithm, metagrammar, and all charged/compute ceilings, executable bodies improve the cost/accuracy frontier against rank-only and body-ablated variants, and against a strong fixed-expressive search + role-neutral episodic retrieval comparator.
H-C (secondary curriculum): diverse independent training graph structures improve motif discovery/transfer compared to the same number of mere object-renamed experiences. Repeat identical evidence for 1/2/5/10 passes MUST not count as newly learned information.
H-S (validity): invalid or contradictory evidence, budget exhaustion, no applicable motif, or true novel motif causes safe reject/abstain/fallback without optimistic fabricated model-class mismatch.
H-I (exploratory interaction): concept-conditioned inquiry effect cannot be explained entirely by better predictions using the same observations, better heuristic fixed search, or altered cost accounting.

Null possibilities MUST be stated: H-Q=0 is plausible; an already-strong cost-aware fixed active planner may match learned concepts. H-R may be zero even when H-Q positive. Negative transfer may worsen outcomes. No automatic success designation.

## 4. World generator and transfer strata
Initial engineering pilot: 4–6 Boolean objects, deterministic synchronous transitions and typed direct/gated relation atoms with XOR/parity composition; no arbitrary Python callbacks. Model capacity up to 4 atoms via an explicitly versioned **human-provided** meta-grammar. If H4 is computationally infeasible, declare bounded underidentification, reduce generated graph complexity in a versioned preflight, never change arms or audit after scoring.
- RENAMED: graph-isomorphic variants of TRAIN (plumbing-only, never counted as structural generalization).
- COMPOSITION: new full-graph topologies combining local motifs observed across TRAIN; *primary* engineering evaluation stratum.
- NOVEL: at least one motif not observed in TRAIN; negative-transfer / abstention stratum, not expected positive body gain.
- DISTRACTOR: distractors and irrelevant causal paths, controls spurious identity/position correlations.
Canonically hash typed edge-labelled graphs up to object-ID permutations. Reject forbidden full-graph collisions across splits. IMPORTANT: nonisomorphic full graphs may intentionally share a local motif; annotate motif overlap explicitly, not pretend all heldout edges are novel. Record graph counts, source seeds, canonical digests, motif membership and family strata in manifest accessible only to evaluator where needed.
Engineering pilot proposal: nested distinct TRAIN counts 0/3/8/16/32/64; 48 disclosed test worlds (12 per stratum), 32 evaluator-only fresh state-action audits/world, and budget horizons {0,2,4,8} actions. Sample sizes are engineering targets, not evidence of statistical power and NOT frozen F0. The generator must be feasibility-tested on public smoke tasks before any heldout-style development scoring. Tests may be regenerated only under new versioned protocol with reason and old receipts retained.
For a future formal study, independent custodian must provide new sources; no disclosed pilot evaluation fixture is eligible for final inference.

## 5. Agent architecture and isolation
~~~mermaid
flowchart TD
 E["Environment: hidden graph + audit truth (never learner-visible)"] -->|stateful metered operations| O["Public Observation / ActionCost"]
 O --> V["Strict exact-type validator + replay consistency"]
 V --> H["Version space H1..H4 / diagnosis / abstention"]
 H --> Q["Query planner: 2-step costed lookahead; concept-blind or concept-aware"]
 Q -->|reachable set_state / pulse / reset| E
 H --> W["WAKE: validated trace + counterexamples"]
 W --> S["SLEEP: motifs + canonical role generalization"]
 S --> C["ConceptSnapshotV2: external immutable versioned concept library"]
 C --> Q
 C --> I["Inference: rank / instantiate / H4 fallback"]
 I --> R["Independent engineering scorer: private 32-action audit"]
 R --> L["Run ledger + human scientific decision"]
~~~
Implemented G1-D components are dependencies, not proof this target architecture works. For engineering, the disclosed synthetic host may run same-process with strict method discipline; label it *not independent custody*. For formal claims, separate evaluator source, process and authority.

## 6. Learning algorithm and test-time logic
WAKE: on each training world, begin with public initial state. Validated operations (set_state, pulse, reset) produce immutable Observation records with metering receipts. Maintain the complete evidence-consistent version space; infer local mismatch only after complete bounded class enumeration. Unknowns remain explicit.
SLEEP: synthesize minimal executable role motifs of size <=2 from supported H2-H4 fits and useful counterexample witnesses. Canonicalize roles under object permutations. Register only motifs supported in >=3 **different structural training worlds** (not three names of the same graph), with versioned applicability/negative witnesses and static grammar coverage. Deduplicate semantically equivalent fragments where tractable, cap retained candidates, reject inconsistent templates. A concept is a hypothesis with scope, NOT accepted world truth.
DREAM: from candidate models generate counterfactual reachable action/outcome partitions and falsification probes to index which questions can distinguish models. These are simulated hypotheses, not new independent evidence or fresh worlds. In the pilot use deterministic symbolic planning: NO SGD, NO training epochs and NO pretrained LLM. Record optional Dream simulation cost separately.
USE: load validated Snapshot, reconstruct hypotheses from public evidence and typed learned templates; when a template fails, use resource-remaining bounded fixed search. Query and prediction separately consult concept data based on arm. Nonidentifiability, cap exhaustion and out-of-scope must yield labelled abstention, not confident guessing.
QUERY: because a setup action can have zero *immediate* information but enable an informative pulse, evaluate 1–2-step reachable plans, including setup/reset cost. At each state, compute predicted answer partitions over surviving hypotheses under a fixed documented prior and frozen tie-break; target expected entropy reduction divided by total charged plan cost, optionally preplanned falsification objective across H1/H4/model-other. Execute only first operation, observe, replan. Ensure no hidden graph/seed/gold access. Learned concept may propose additional typed candidate models and probes but not change allowed actions. Both concept-aware and blind query planners share identical lookahead depth, hypothesis/CPU caps and source evidence.
If full H4 cannot be enumerated, any approximate posterior and information-gain proxy must be explicitly labelled heuristic; it cannot certify absence of an unenumerated model.

## 7. Comparators / precise mechanism isolation
All arms have same TRAIN world experience as applicable and the same H4 expressive typed primitive grammar and operation/candidate budgets. ALL report costed actions/CPU/setup and fully audited abstentions. Primary comparator pair must be *identical* in trained Snapshot, inference body, initial state, permitted actions, priors, and implementation except the query policy's access to body/applicability/falsification entries:
- LQ: learned body **for inference and for question selection** (primary treatment).
- LA: same learned body **for inference**, but question planner cannot consult body/applicability; uses same cost-aware fixed query algorithm and rank/count prior (primary control). Other information and compute envelope equivalent.
- LR: same TRAIN and active planner but executable body disabled for both inference/query; rank-only policy control.
- LP: body-enabled inference with fixed passive legal query schedule; observation transcript shared with passive body-off comparator.
- FA: strong fixed H4 solver and cost-aware active query, no trained templates; optimize with same canonical signature/cache tricks.
- ER: role-neutral structural episodic retrieval / analogical nearest trace from same TRAIN, with no stored executable abstraction, plus H4 fallback.
- FX: fixed exhaustive/beam H4 under deterministic budget, with passive paired evidence. Additional limited-expression H1 is diagnostic, NOT a strong competitor.
Primary LQ–LA effect isolates **question use of concept** conditional on already having same concepts in prediction, not overall concept acquisition. Secondary LQ–LR and LA–LR isolate body and overall transfer; LQ–FA and LQ–ER test alternative explanations. For active arms, different obtained evidence is part of the randomized treatment; NEVER call it identical-observation comparison. Passive pairs alone can share identical transcript.

## 8. Outcome and estimand
At each budget horizon b in B={0,2,4,8}, each arm uses a fresh episode on the same audit world starting from an identical initial state; the *evaluator* may reset between independent runs, but learner cannot perform an uncharged reset within an episode. No arm sees its own previous horizon evaluation or any evaluator gold feedback. Once cost ceiling reached, model predicts the post-action full Boolean vector on 32 **private evaluator-chosen** state-action transitions. Abstention scores 0, with abstention separately reported; 32 audits form ONE per-world score. The private audit states may be chosen by evaluator without the learner observing them.
Define Y(w,arm,b) = exact-vector matches / 32. AULC(w,arm) = (Y(w,arm,0)+Y(w,arm,2)+Y(w,arm,4)+Y(w,arm,8))/4.
Primary estimand over COMPOSITION worlds: Delta_Q = mean_world[AULC(w,LQ)-AULC(w,LA)].
Secondary transfer: Delta_body = mean[AULC(LA)-AULC(LR)] and robust comparator deltas to FA/ER. Negative transfer: mean differences on NOVEL and abstention/error calibration.
Report per-world paired deltas and bootstrap uncertainty / family-cluster correction only after independence and sampling are settled at formal F0; in disclosed 12-world/stratum pilot, report descriptive intervals where useful but never significance or capability promotion.
Candidate FUTURE F0 decision target (not frozen): primary mean improvement >=0.05 absolute and 95% interval lower bound >0, with no serious negative-transfer regression, justified sample size/power and valid source/cost custody. If interval excludes strong gain or remains wide, report REJECTED or UNDERIDENTIFIED; do NOT rescue a failed primary contrast by selecting a different budget/metric after observing outcomes.

## 9. Measurement and no-cheating constraints
Every action charged in fixed integer units: engineering pilot set_state=1, pulse=1, reset=1; record also state bits changed and all underlying primitive executions. Record *actual* operations including setup and early stop, planner evaluated hypotheses and candidates, fixed candidate budget carried through template plus fallback, query planner state expansions, CPU process_ns, wall_ns, peak RSS, Snapshot train + serialization/loading/precompute and inference. CPU is secondary platform-dependent. Store total lifetime amortized cost for N uses:
 C_total(N)=C_train+C_sleep+C_precompute+N*(C_load/N+C_use) ; compare actual full path and break-even N, do not infer speed from candidate count alone.
Invalid exact builtin types or subclass behavior must be rejected BEFORE comparisons/hash/pruning. Never leak hidden rule generator, split IDs, audit gold, or candidate labels. A deterministic digest is integrity evidence, NOT independent authenticity or custody. Separate trained data, developer-visible synthetic test evidence and formal evaluator-only data by source lock.

## 10. Engineering gate and release states
G0: fix all P1 on PR #129, exact-head safe CI and independent re-review, reproduce NEW disclosed baseline. Historical dated receipts are immutable. No P1 means READY_FOR_BASELINE; snapshot and parser versions fixed with hash and recovery commands.
G1: implement isolated rep002 generator, validator, metering, canonical graph/motif contracts, 2-step active query planner and data/negative tests. Update AGENTS, INDEX, ARCH-001 Mermaid, ARCH-002 data flow and contracts, spec, plan and dated run receipt in SAME work PR.
G2: train disclosed nested curriculum; save every Snapshot with digest and independent structural supports; negative tests and 1/2/5/10 replay idempotence control. Do NOT call those epochs.
G3: use saved Snapshot in fresh disclosed world through CLI; compare all paired arms and budgets, independent private-in-code audit, reproduce twice, record failures/timings; reviewer checks code and raw receipts.
G4: decide engineering continuation (MECHANISM_POSITIVE, POLICY_ONLY, FIXED_SEARCH_SUFFICIENT, NEGATIVE_TRANSFER, UNDERIDENTIFIED or INVALID) and baseline candidate status. A successful toy is still NOT formal science.
F0: only after independent method/power/generator/custody/cost/security review, pre-register exact statistical law and code/split/manifest SHA. Formal TRAIN/DEV later separately; formal FINAL one-shot always requires NEW explicit owner authorization, independent custodian and sealed evidence chain. Do NOT auto-merge Draft PR or modify legacy holdouts/CI triggers.
Engineering PASS requires: zero unresolved P1, exact-head CI/document tests and reproducibility, correct resource caps and fail-closed inputs, end-to-end train/inspect/use/evaluate, all arms and per-world raw metrics. Positive intelligence claim is NOT a condition of engineering PASS; negative results are the primary scientific value when valid.

## 11. Local interface (planned, not implemented)
    python -m packages.rep002 preflight --scope disclosed
    python -m packages.rep002 train --curriculum manifest.json --snapshot output.json
    python -m packages.rep002 inspect --snapshot output.json
    python -m packages.rep002 use --snapshot output.json --world disclosed:new --budget 8 --trace trace.jsonl
    python -m packages.rep002 evaluate-disclosed --protocol protocol.json --output run.json
All commands proposed; do NOT present as runnable today. CPU-only Python >=3.12 and stdlib at pilot stage. Canonical JSON/JSONL + SHA-256 for research data; SQLite optional index later, not authoritative provenance. No external LLM or pretrained model.

## 12. Scope and alternative technologies
Chosen: typed symbolic model classes + canonical relational motifs, version-space reasoning, two-step costed active experiment planning, deterministic Wake–Sleep–Dream analysis, versioned external Snapshot, independent scored verifier. Why: isolates mechanism, tractable on CPU, interpretable, makes negative findings actionable.
Rejected for this stage: neural SGD/epoch model (parameter change confounds mechanism), unconstrained Python generator (security and measurement ambiguity), large search exhaustive H4 without caps (combinatorial explosion), language-chat interface as primary scorer (uncontrolled semantic ambiguity). These are deferred, not excluded from DekaSugi's long-term scope.
Research precedents: DreamCoder (Ellis et al., PLDI 2021) library + search policy co-learning and Bayesian experimental design/information gain. DekaSugi is not a reimplementation of DreamCoder.
