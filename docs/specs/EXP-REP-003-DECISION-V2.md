# EXP-REP-003 — 研究・技術設計決定稿候補 V2
id: EXP-REP-003-DECISION-V2
status: DESIGN_DECISION_CANDIDATE / OWNER_APPROVAL_PENDING / NOT_RUN / F0_NOT_FROZEN
updated: 2026-11-02
tags: research, active-learning, causal-model, representation, evaluation
issue: https://github.com/ryonakayama234/DekaSugi/issues/133
pr: https://github.com/ryonakayama234/DekaSugi/pull/134

> This V2 supersedes V1 **as a design proposal only**. This document is a proposed complete execution contract, not evidence of implementation or permission for protected FINAL. Historic receipts remain immutable.

## A. Scientific question, unit of intelligence, and hierarchy of claims

DekaSugi's operational research object is the **update cycle** (observe → hypothesize → choose an intervention → obtain feedback → revise representation → externalize a reusable concept → test in an unseen world), not a static benchmark score or the number of named skills.

**Primary module:** Inquiry / World Model: a version space of candidate causal dynamics and a bounded cost-sensitive active experiment planner. **Supporting:** Observation/World (only lawful environmental I/O), Representation/Sleep (learned executable abstraction and counterexamples), Snapshot/Library (externalized persistent state), Evaluator/Provenance (independent result).

The corrected EXP-REP-002 disclosed direct-only baseline has LQ = FA in every stratum, COMPOSITION LQ−LA = +0.027995 AULC, DISTRACTOR LQ−LA = −0.020183; TRAIN64 has only three full-graph topologies; public `hub` role was a strong shortcut. These facts justify a more discriminating design, not belief in a positive result.

Claim levels (do not collapse): C0 implementation; C1 legal informative action exists; C2 learned causal/conditional structure from paid observations; C3 externalized structure changes **question choice** beyond a policy-only alternative; C4 improves unseen-world predictions beyond a strong fixed planner and other same-experience alternatives, net of training costs; C5 transfer across **semantic** families. Only C0–C4 are directly targeted by the disclosed pilot; C5 is developmental, not general intelligence.

## B. Refutable hypotheses and explicit alternatives

- H-OPP: Under publicly available initial state and action costs, a positive proportion of eligible worlds has **two-step** distinguishing traces even when no one-step pulse distinguishes the current hypotheses. H0-OPP: no such trace exists under the prespecified action grammar/budget.
- H-LEARN: With increasingly varied TRAIN families (not renaming), Wake/Sleep learns **executable conditional relations with applicability and negative witnesses** from learner-facing public evidence. H0: no concept survives counterexamples, new concept is merely an ID/role shortcut, or simple episodic/parameter prior suffices.
- **H-Q (mechanism primary):** On new role-blind conditional-composition worlds, at matched TRAIN Snapshot used for prediction, LQ (body available to question policy) obtains higher per-world budget-AULC than LA (body shielded only from query policy). H0: delta ≤ 0. The actual causal contrast includes different *resulting* observations.
- **H-UNIQUE (attribution co-gate):** LQ exceeds an optimized untrained FA **and** adequately trained episode-only ER, rank-only LR and LQ body-disabled control, with shared executable grammar/action menu and resource ceilings. H0: a simpler prior/search/episodic policy explains any gain.
- H-ROBUST: Novel semantics or distractors should not cause concealed overconfident negative transfer; detect/retract/abstain. H0: learned concepts increase confident error or hide unknown uncertainty.
- H-COST: Count inference and amortized TRAIN/SLEEP/DREAM costs; a cheaper representation is not proven by lower syntactic candidate count alone.
- H-META is explicitly NOT claimed: autonomously inventing an interpreter primitive or unknown control-flow constructor; initial grammar comes from the researcher.

A valid NULL/NEGATIVE/UNDERIDENTIFIED result is a legitimate end result. No post-hoc change from query advantage to a different primary outcome after seeing scores.

## C. Minimal finite causal world (engineering V1 grammar)

Initial target: n=4 Boolean variables, expandable only **after separate pre-score feasibility review** to n=5 or n=6. Each variable has an opaque, uniformly permuted public ID; do not expose `hub`, `source`, `guard`, graph type, class, intended query, source seed or hidden rule. Anonymous object IDs may be mapped into canonical sorted order for deterministic storage; check that ID order is not predictive of hidden semantics. Each episode begins at publicly disclosed all-zero Boolean state. Full Boolean state is observable *only after actual paid action* and initially; no free counterfactual query. No hidden feature labels.

Legal primitive actions:
- `set(i,v)`: choose one of n observed bits and set its value to Boolean v (cost 1); costs 1 even if no value changes; return resulting state. This is **not** an arbitrary free before-state injection. Every arm can set any bit.
- `pulse(i)`: trigger hidden outgoing edges from source i (cost 1), returns resulting full Boolean vector. It does not inherently flip i, except if a typed allowed edge targets i (disallowed at n4 base).
- `reset` is omitted from V1 active menu; a fresh initial episode is evaluator-only between arms/budgets. If later added, charge it and version the study.

Hidden typed causal edges are either `DIRECT(src,target)` or `GATED(src,target,guard,value)` with distinct src,target,guard for GATED; no self edges, max 2 edges in the initial exact n4 grammar. For state s, `pulse(i)` computes all targets simultaneously from **pre-action** s: `s'[j] = s[j] XOR parity({edge | edge.src=i, edge.target=j, gate_condition(edge,s)})`. Other bits remain unchanged. `set` changes only its addressed bit. Both direct and gated edges use the SAME XOR semantics, so finite behavior equivalence is checked rather than inferred from graph syntax. In-domain generator draws typed edges and checks exact semantic class. Out-of-grammar tests are marked OOD, not forcibly fitted.

Illustrative **not experimental evidence**: two hypotheses that do not change the target after `pulse(A)` at initial guard C=0 can differ after `set(C,1) → pulse(A)`; this is a cost-2 actionable witness. A counterexample with identical full finite transition semantics must be labeled equivalent, NOT novel. For budget 1, two-step-only pairs are explicitly NO_OPPORTUNITY, even if budget 2 has a witness.

Why choose this grammar: fully enumeratable 2^4 states, deterministic test oracle, no pretrained model, no uncontrolled host Python generation, and a genuine role-blind conditional intervention interaction. It is deliberately **not** free-form causal representation discovery or text/dialogue.

## D. Identifiability audit before learning — completely separate oracle

Define H(o) = models consistent with the exact paid public transcript o. Initial prior = uniform over canonical **semantic behavior classes**, not syntactic programs (avoid counting duplicates as evidence). For any legal plan p of length ≤ horizon, simulate candidate outputs including all intermediate visible observations. `WITNESS` iff there are at least two surviving hypotheses with distinct observable plan traces and p is actually executable/reachable at charged cost. Output concrete pair, action trace, both traces, cost and model/semantics hashes. `NO_OPPORTUNITY` iff **all** lawful sequences ≤ budget have been exhaustively checked and none separates any surviving hypotheses. If cap reached or grammar incomplete: `UNKNOWN`, NEVER false impossibility. A WITNESS is a separation of possible models, **not** proof which candidate is true and not a model-learning score.

Run a fully enumerated independent diagnostic on all-state/all-action finite transition functions to distinguish (i) graph structural isomorphism, (ii) full finite semantic equivalence under relabeling and (iii) *reachable/observed* equivalence. Avoid placing hidden world truth or the witness action itself into any learner API, Snapshot or question planner. The oracle is engineering preflight only; its results may be aggregated for study feasibility. Eligible world strata and generator decisions must be committed **before** comparison scores.

## E. Learner logic — answer the next question with models, not heuristics alone

1. `WakeObservation`: accept only strict exact typed public `set/pulse` actions and paid observations; check monotonic trace and causal transition consistency; reject forged/unknown fields.
2. `HypothesisSpace`: enumerate typed n4 models up to 2 edges with deterministic cap; maintain compatibility, canonical finite semantic signatures and uncertainty flags; no unenumerated-excluded world treated as logically impossible.
3. `Inquiry`: consider all legal next actions and 2-step reachable plans under same fixed limit for every comparator; score expected partition reduction in semantic version space per **total charged cost** (one uniform prior within compatible semantic classes). Deterministic tie-break by canonical public action encoding. Execute the FIRST step only, update with actual observation, then replan. If exact prior is infeasible, mark heuristic and freeze the change in new version; do not disguise it as exact Bayesian posterior.
4. `Wake→Sleep`: after independent TRAIN experiences with varied graph/behavior families, infer variable-renaming-invariant conditional templates through anti-unification/canonical graph matching, positive and negative counterexamples, and minimum structural support. The algorithm must infer role mappings FROM public effects; no role hints. Permit executable template library entries and record applicable/contradicted/unknown.
5. `Dream`: mentally simulate known models to index potential falsifying plans or rehearse a **policy**; charge all simulated expansions and preserve generated data provenance as `synthetic_counterfactual`, not independent world evidence. Dream cannot invent unobserved truth. This version uses deterministic symbolic planning, not SGD or learned neural weights.
6. `Use`: validate a saved Snapshot schema/grammar/trace provenance and budget, instantiate learned templates for a NEW opaque-ID world, actively interrogate, revise or abstain, emit immutable prediction commit **before** audit. Optional actual local use traces and independent scored audit must be separate outputs.

Representation repair diagnostic: `insufficient_evidence` when hypotheses disagree and legal probes remain; `model_contradicted` when a learned body fails real observations; `out_of_grammar_or_resource` when no model survives **but** budget/grammar completeness is not proven; `representation_limit_witness` only when a complete finite search has a proof that no current-grammar model satisfies observations. These labels do not auto-install new primitives.

## F. Comparator matrix and causal attribution

| Arm | TRAIN access | Prediction | Query | Purpose |
|---|---|---|---|---|
| LQ | learned full Snapshot | executable body | body-aware, 2-step | treatment |
| LA | SAME full Snapshot | SAME body | body inaccessible, same 2-step model planner | primary mechanism control |
| LR | SAME public TRAIN episodes | rank/frequency only | rank/frequency only | learned policy-only |
| ER | SAME public TRAIN episodes | episodic structural analogies + common bounded fallback | episodic, 2-step | memorization/analogy alternative |
| FA | no TRAIN by definition | strong fixed grammar search | optimized 2-step information-gain policy | genuinely untrained strong baseline |
| FX | none | bounded fixed search | passive or canonical fixed schedule | lower-level diagnostic |
| BODY-OFF | SAME TRAIN/Snapshot source as LQ | body disabled; fallback uses SAME grammar | body disabled | concept-body ablation |

Each arm uses the same public action alphabet, same input validation, same model grammar and maximum expanded primitive models/rollouts in an episode. Learned-body expansions, cache preparation and fixed FA precomputation must be visible and metered. FA may be as sophisticated as is computationally feasible; do not weaken to manufacture progress. **FA cannot be identical in experience to LQ by definition**, and LQ−FA alone cannot establish body-specific attribution. Matching TRAIN exposure for LR/ER and LQ−LA+BODY-OFF is critical. Evaluate additional `LQ-with-shuffled-concept` negative control where safe, to reveal template leakage/overfitting.

If LA's inference implementation indirectly leaks learned body to its query policy (e.g. predicted actions or ranking derivable from body), reject the test as INVALID. Explicit opaque query-policy interface controls prevent that.

## G. Metrics, designs and numerical decision discipline

Engineering study: TRAIN sizes 0/3/8/16/32/64 public worlds; record count of **distinct semantic families and graph topologies separately**. At each size collect frozen Snapshot hash, legal paid action count, cost of Wake/Sleep/Dream, model body(s), positive/negative witnesses and idempotence replay 1/2/5/10 on exactly same data. This repeat is NOT a stochastic gradient epoch.

Disclosed evaluation candidate: 4 strata × 12 worlds (48 total), 7 comparator arms, per-budget independent fresh episodes at B={0,1,2,4} charged operations (the b=1 vs b=2 contrast resolves two-stage necessity; replaces REP002's 0/2/4/8 for this **new** study only), and 32 preselected evaluator-only full-state next-transition audits / episode. This is a **descriptive engineering pilot**; 48 worlds do not imply 48 independent semantic families, and 32 audits in a world are not independent scientific samples. Feasibility and workload estimates are provisional until P1 run.

Per-world `Y(w,a,b) = exact_next_vector_matches / 32` with ABSTAIN scored 0 (report abstain separately); `AULC(w,a) = mean_b Y`. Primary descriptive mechanism estimand: `mean_family,w (AULC_LQ−AULC_LA)` on conditional-composition stratum; co-gate `LQ−FA`, `LQ−ER`, `LQ−LR`, `LQ−BODY-OFF`. Report every signed paired family/world delta and censoring/UNKNOWN. Do NOT treat the same world's budgets or audit transitions as independent replications. Also report `question_discrimination_rate`, minimum paid witness cost, exact semantics complexity, false-confidence rate, OOD abstention, negative transfer and calibration where meaningful. Diagnostic oracle-optimal action gap is evaluator-only and not a learner target.

All-arm **two budgets**: (a) identical action budget; (b) identical common deterministic inference/planning cap; the same fixed symbol/expanded-node semantics across body and no-body. Separate lifetime `C_total(N)=C_train+C_sleep+C_dream+C_precompute + N*(C_load+C_query+C_predict)`; expose CPU/wall/RSS, node expansions, model checks, rollout lengths, intervention counts. No speed claim from candidate count only. A small fixed procedural prior may have lower cost and win even if learned model predicts well.

The exact shared numerical inference/rollout ceilings are intentionally **UNFROZEN** until a published *no-scoring* feasibility preflight proves all arms can run on CPU; ceilings and all class distributions are locked before scoring. Never drop one comparator or expand only LQ caps after seeing outcomes.

Formal positive claim is NOT defined by the descriptive pilot. A subsequent F0 requires independent prior review of target practical improvement (candidate 0.05 absolute AULC), family-level power, family cluster bootstrap/confidence method, multiplicity/hierarchical gate, random generation law, code/snapshot/seed freeze and authenticated custody. A 95% CI lower bound >0 only has meaning after genuine independent family sampling and preregistration. No formal FINAL without separate explicit owner approval.

## H. World families and failure-discriminating strata

- INVARIANCE: held-out ID relabelings of TRAIN semantics, diagnostic invariance only, not structural transfer.
- COMPOSITION: held-out complete transition compositions built from independently supported local learned conditional motifs but graph/semantic whole-system unseen; primary developmental target. Avoid giving `family=COMPOSITION` to learner.
- NOVEL: semantically new conditional motif/guard logic, designed negative transfer/OOD; expect calibrated uncertainty/abstention, not forced accuracy.
- DISTRACTOR: extra irrelevant variable effects, misleading correlations or counterexamples; test false applicability and repair. Require true counterexample distinguishability, not syntax-only novelty.

Train/test generator paths, class hierarchy and any parameter aliases are audited for seed/label/ID leakage; unit of independence is generating causal **family**, not renamed instance. With n4 insufficient family diversity, retain synthetic sanity testing only and increase n to 5/6 in a separately frozen new version.

## I. Architecture and interface (PROPOSED)

~~~mermaid
flowchart TD
  subgraph PRIVATE["Environment / audit authority (not learner-visible)"]
    WG["World generator + hidden causal model"]
    OR["Reachability/semantic-opportunity oracle"]
    SC["Audit scorer: gold transitions"]
  end
  subgraph PUBLIC["Learner-facing paid interface"]
    A["set(i,v), pulse(i); exact cost ledger"]
    O["typed public observations / trace"]
    H["VersionSpace: candidate dynamics"]
    Q["Inquiry: costed 2-step planning"]
    W["Wake experience"]
    S["Sleep: canonical conditional abstractions"]
    D["Dream: counterfactual simulations"]
    SNAP[("Versioned external Snapshot")]
    C["PredictionCommit before audit"]
  end
  WG --> A --> O --> H --> Q --> A
  O --> W --> S --> SNAP --> Q
  H --> D --> Q
  SNAP --> C
  H --> C
  C --> SC
  WG --> OR
  OR --> MET["Opportunity feasibility report only"]
  SC --> RUN["Per-world/family evaluation ledger"]
~~~

No hidden truth edges into `train`, `query`, or Snapshot, even through support/topology statistics. The *preflight opportunity oracle* owns hidden candidate-model comparisons but must not send hints to the learner. Gold auditor purely runs the committed predictor on its private inputs and never calls learner search.

~~~mermaid
flowchart LR
  TS["Public Task/SessionSpec"] --> OBS["Paid Action/ObservationTrace"]
  OBS --> VS["Semantic VersionSpace + contradiction"]
  VS --> PLAN["QueryPlan + ResourceLedger"]
  PLAN --> OBS
  OBS --> EXP["WakeExperience"]
  EXP --> CND["ConceptCandidate(body,scope,witnesses)"]
  CND --> SNAP["ConceptSnapshot(version,hash,provenance)"]
  SNAP --> PLAN
  SNAP --> PRED["PredictionCommit(model or ABSTAIN)"]
  PRED --> SCORE["AuditOnly score rows"]
  SCORE --> DEC["Review + release decision"]
~~~

Canonical typed schema keys: `WorldPublicV2`, `ActionV2`, `ObservationV2`, `VersionSpaceV2`, `OpportunityWitnessV2`, `QueryPlanV2`, `ResourceLedgerV2`, `WakeExperienceV2`, `CausalConceptV2`, `ConceptSnapshotV3`, `PredictionCommitV2`, `AuditRowV2`, `EvaluationSummaryV2`. All exact built-in types validated before equality/comparison/digests; named schema versions and executable grammar hash prevent mixing pilot vintages. Store canonical JSON/JSONL (immutable raw + digest); optional SQLite derived *index only*, not provenance authority.

## J. Selected technologies and rejected alternatives

- Python 3.12+ stdlib, Linux/WSL2 CPU, deterministic fixed-bit interpreter and typed finite-model grammar, JSONL/canonical JSON/SHA256, exhaustive initial n4 reachability/semantic equivalence, finite version-space posterior and exact expected partition reduction, template anti-unification and deterministic Snapshot. This is **symbolic representation learning** and active model-based experimental design, not SGD.
- Reject replacing project logic with external pretrained LLM; confounds attribution and violates initial objective. No deep neural optimization in this cycle: would introduce weights/epoch overfitting before proving an information opportunity. No unrestricted generated code on host. No mysterious role tokens, ground-truth "correct next query", synthetic DREAM scored as independent data, or arbitrary Python world callbacks.
- Later neural recognizer may be a plug-in to QueryPlan candidate ranking, after a fixed F0 study and held-out data. Its training epochs, loss and validation curves are **separate** from current deterministic replay. No forced domain-specific expansion: operator/interface contracts can later be adapted to textual, numerical and real-world interactions without claiming that those transfer today.
- Scientific foundations, not direct empirical transfer of results: DreamCoder (Ellis et al., PLDI 2021, doi:10.1145/3453483.3454080); active intervention design (Zhang et al., Nature Machine Intelligence 2023, doi:10.1038/s42256-023-00719-0); identifiability under assumptions (Varici et al., AISTATS 2024, PMLR 238). Their assumptions differ from this finite XOR-world.

## K. End-to-end execution as one research program, not micro-chat deliverables

**G0 — baseline/review:** inspect current exact PR stack, outstanding P1 and corrected evidence. Do not merge before review. Freeze *engineering comparison copy* of REP002 (not call it a scientifically accepted model). Record signed limitations.

**G1 — hypothesis/opportunity + guardrail preflight:** implement new isolated `packages/rep003` with hidden-world generator, legal paid states/actions, finite exact witness/semantic equivalence, common deterministic resource ledger, adversarial invalid-type/cost/role-leak/false-witness tests; verify existence and impossibility on deliberately different disclosed fixtures. Source/method revise openly until ready, then lock engineering pilot manifest **before scoring**. If no informative witness at chosen budgets, STOP; redesign as a new version, not cherry-pick favorable test worlds.

**G2 — learn and externalize:** implement Wake evidence collection from public API, Sleep canonical abstractions and negations, Dream simulation, SnapshotV3 save/load validation, CLI `train` and `inspect` and exact same-data replay. Run disclosed nested TRAIN0/3/8/16/32/64, keep all snapshots and costs. No prohibited old sealed DEV/FINAL.

**G3 — use:** reload TRAIN Snapshot in a fresh opaque-ID world; CLI `use` issues actual sequential paid setup/pulse and logs predictions, evidence/revisions and a pre-audit commitment. Log at least one successful, one refuted and one deliberately non-identifiable synthetic trace. No audit gold in learner response.

**G4 — evaluate disclosed:** implemented scorer receives only immutable PredictionCommit and evaluator-only transitions; all seven arms, the four budget horizons and four strata. Produce complete world×arm×budget raw JSONL, condition aggregates, family-level paired diagnostics, resource and negative-transfer report, source/snapshot/manifest SHA, reproduce the run twice with exact bytes. Label synthetic disclosed, NOT formal science.

**G5 — independent review and decision:** exact head CI and docs checker, source/negative tests, independent reviewer checks oracle isolation, budget symmetry, comparator strength, independent family counts and chronology. Decide `ENGINEERING_PASS/FAIL` separately from `MECHANISM_POSITIVE/NULL/POLICY_ONLY/FIXED_SUFFICIENT/NEGATIVE_TRANSFER/UNDERIDENTIFIED/INVALID`. If no attribution, preserve record and stop; do not force a V0 freeze.

**F0 / formal later:** after G5, independently review and freeze sampling, statistical power, split source, one-shot evaluators, custody, immutable code + training snapshot, and separately authorized DEV then FINAL. Not authorized by this design. Formal acceptance of any `FrozenReferenceBaseline` is a distinct ADR; `ResearchPrototype` can be versioned without promoting scientific claims.

All G steps are part of one planned execution program; each meaningful implementation slice changes in the **same Draft PR** its module, tests, AGENTS, docs/INDEX, ARCH-001 system Mermaid, ARCH-002 contracts/flow, spec/plan, and append-only dated experiment receipt. CI never runs sealed benchmarks by default. User need not handle branches or Git.

## L. Required run artifacts and local UX (planned, NOT yet executable)

```bash
python -m packages.rep003 preflight --scope disclosed --output .run/rep003/opportunity.json
python -m packages.rep003 train --worlds 64 --snapshot .run/rep003/snapshot-v3.json
python -m packages.rep003 inspect --snapshot .run/rep003/snapshot-v3.json
python -m packages.rep003 use --snapshot .run/rep003/snapshot-v3.json --world-index 301 --budget 2 --trace .run/rep003/use.jsonl
python -m packages.rep003 evaluate-disclosed --output .run/rep003/pilot.json
```

Every `run` includes source commit, implementation/grammar/data version, manifest SHA, evaluation type, provenance and access classes; all raw world×arm×budget rows, each committed predictor and abstention, training and inference costs, positive/negative evidence, checksums and signed review verdict. Secret originals stay out of public Git.

## M. Explicit major unresolved risks before implementation

1. Strong FA may exactly match LQ again; this is an informative null. No expectation of guaranteed positive concept effect, even in conditional worlds.
2. n4 supports very few semantically independent families; descriptive 48 renamed worlds cannot justify population confidence. F0 may need richer n5/n6 world generation and independent source.
3. Distinguishability does not guarantee *usefulness* for full-transition audit scoring or generalization. The primary estimand is scored independently of opportunity oracle.
4. If a learned concept body is a re-encoding of the exact prior in ER/LR/FA, claiming unique representational gain is invalid.
5. Counterfactual DREAM and public synthetic training can overfit to researcher-defined grammar; source-holdout OOD and independent custody necessary.
6. Cost-equivalent planners may lack a genuine expected-information optimum under caps; record approximation and resource exhaustion/UNKNOWN transparently.
7. Current REP002 Draft stack has dependent branches and reviews; do not call later stages done or auto-merge while parent evidence is unresolved.

## N. Owner decision and current evidence

Research/design judgment is **DECISION_CANDIDATE_V2**, awaiting owner agreement; it is not F0 pre-registration or training authorization. No code, TRAIN, use, new scoring, new CI evidence or independently approved science is claimed by this document. On agreement, one substantial G0→G5 disclosed engineering program may be executed, stopping only at pre-agreed quality/science gates rather than asking to approve every small commit. Formal F0/FINAL always separately authorized.
