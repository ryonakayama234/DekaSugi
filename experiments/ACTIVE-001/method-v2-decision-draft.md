# ACTIVE-001 Stage I — Scientific Design Decision v2 (pre-implementation)

id: ACTIVE-001-DESIGN-V2
status: decision_draft_for_user_and_independent_review; NOT_FROZEN; no_scoring_authority
updated: 2026-10-30
tags: active-learning, scientific-method, information-value, epistemic-action, identifiability, power, reproducibility

Parent: [Issue #96](https://github.com/ryonakayama234/DekaSugi/issues/96), [draft PR #97](https://github.com/ryonakayama234/DekaSugi/pull/97). This is the **proposed decision text** for what to build next, **not** an executed preregistration, an accepted independent review, a frozen source identity, or an authorization to score. Historical [method v1 candidate](method-v1-candidate.md) and [original draft plan](plan.md) remain readable. The previously merged PR #94/#95 active engine is an **engineering reference baseline**, not a scientific capability claim.

## Executive decision

**Research question:** When does an AI's self-chosen *epistemic action* (an allowed question) create **downstream held-out predictive utility**, rather than only reduce uncertainty?

**Primary research module:** scientific evaluation / prospective `packages/active_evaluation`. **Referenced, unchanged modules:** `packages/inquiry_world` and `packages/active_learning`. A read-only structural `packages/active_feasibility` module is a future proposal, not implemented. Kernel, Sleep, Dream, legacy scorers and all frozen historic sources are OUT OF SCOPE.

**Selected design:** a two-gate project:
1. **Gate F (design-only)**: exact structural census of *public-context version spaces* and query partition opportunities, with **no official scored target or withheld-label comparisons**.
2. **Gate C (future confirmatory, separately authorized)**: one fixed independent paired evaluation over **4,096 independent task draws**, with replacement, uniform across the 878 finite-domain semantic classes and uniform across unordered pairs of the 28 public inputs, comparing B2 to mean-five B1. This is a *proposed exact number* to review and freeze **before** any scored evaluation, rather than silently retaining N=512.

The 878, 4,681 and 156 counts are previously recorded **synthetic engineering** facts, not fresh measurements from this document. Under this finite design the maximum number of class/public-pair contexts is `878 * C(28,2) = 331,884`; it is **not** a claim about independent out-of-domain tasks. Repeated classes under sampling with replacement are allowed and do not imply external generalization.

## What is and is not measured

**Operational construct (Stage I):** task-internal epistemic adaptation. Input: two labelled public examples and unlabelled question candidates. Action: choose up to two new inputs for a deterministic Oracle. Update: remove incompatible semantic hypotheses. Output: a final program. Scientific observation: accuracy on 64 evaluator-only inputs.

**Not measured:** long-term policy learning across episodes, automatic primitive invention, new expressive completeness, out-of-domain generalization, human-machine mutual learning, or general intelligence. The experimenter supplies all eight primitive operations. A positive score only establishes the bounded value of information-seeking in the specified fixed synthetic distribution.

**Information ≠ utility:** B2 uses `Gini(q) = 1 - sum_y (n_y / |H|)^2`. It maximizes response disagreement across currently uniform-weighted semantic classes, *not* expected downstream held-out accuracy after choosing the first canonical surviving program. Thus B2 may shrink H but have zero or negative decision advantage. No adaptive-greedy optimality guarantee is assumed; the required assumptions for such a theorem have not been established here.

**Mechanistic terms:** information opportunity = existence of a query separating hypotheses; decision opportunity = possible change in the eventual predicted answer; realized utility = independently measured paired held-out accuracy difference; economic utility = realized benefit after question/selector/computation costs. These four are not interchangeable.

## Competing hypotheses and falsifiers

| ID | Logical prediction | Falsification / alternative |
|---|---|---|
| H1 (only confirmatory efficacy hypothesis) | Mean paired held-out `B2 - B1` difference on the full registered task-generating distribution is >0 | CI lower ≤0; significant negative also retained |
| H2 (mechanism, secondary) | Gini and hypothesis reduction are associated with changes in final prediction | Reduction without downstream benefit; decoder choice or prior mismatch |
| H3 (structural eligibility, Gate F) | A nonzero fraction of valid public contexts has an informative permitted query (F3) | F3 = 0, or upper opportunity bound too small for meaningful improvement |
| H4 (control explanation, secondary) | B2 may outperform B1 because B1 spends queries on zero-Gini inputs, not because max-Gini ranking is better among informative inputs | Prespecified *informative-uniform* B1+ diagnostic eliminates most of B2's advantage |
| H5 (resource economics, secondary) | Improved answers may be worth Oracle and CPU cost at a declared workload | Total amortized cost dominates, or improvement disappears when measuring total CPU |
| H6 (integrity) | Only a valid answer to a proposed query changes beliefs; hidden labels never inform policy | Any target/audit leakage, forged receipt, mismatched split or invalid state => STOP, no efficacy claim |

A positive H1 does **not** establish H2, H4, Stage II or transfer. Do not derive new acceptance gates from post-run subgroup differences.

## Alternatives considered and decision

| Option | Scientific strength | Main objection | Decision |
|---|---|---|---|
| A: immediately run N=512 sampled tasks | Familiar and inexpensive | With bounded task difference [-1,1], +5pp detection has no defensible worst-case nominal power at N=512 | reject as an unjustified confirmatory N |
| B: exhaustive score all 331,884 possible class/public-pair contexts | Exact expectation for a specified finite deterministic world, **no sampling CI** | Computational and cost feasibility not established, random B1 policy needs an exact expectation over seeds, and census adds no external validity | reserve for a later independently costed **model-checking** study |
| C: full structural census first, then N=4096 independent precommitted task draws | Identifies possible information opportunity without scoring; paired inference; bounded-variance conservative nominal planning | More CPU; still only one finite closed-world distribution; reviewer must validate assumptions | **SELECT** |
| D: arbitrary hand-balanced target families | Higher apparent rare-family coverage | Unknown population weights and fabricated cluster/generalization interpretation | reject for primary; exploratory stratification only |

The proposed sample size is based on a **normal-approximation sensitivity bound**, not observed paired variance: for `D_i ∈ [-1,1]`, `Var(D_i) <= 1`. At `n=4096`, `delta=.05`, worst-case `sigma=1`, noncentrality `delta*sqrt(n)/sigma=3.2`; nominal two-sided .05 positive-detection power `Phi(3.2-1.96) ≈ .89`, and worst-case approximate 95% half-width `1.96/sqrt(4096)=.030625`. **This is not a distribution-free guarantee, a measured power, or power for the separate 5pp practical-value classification.** A reviewer must check finite-sample coverage, IID assumptions, missingness and feasibility prior to freeze. If Gate F or cost review blocks N4096, redesign via a new version **before exposure**; no outcome-dependent N change or optional stopping.

## Target distribution, sampling unit and support (proposal to freeze)

- Fixed universe: `ALPHABET=("a","A","b","B"," ")`, input strings lengths 0–3; `156` inputs. Fixed operation order and depth 0–4 yield `4,681` syntax programs; semantic class defined by equality of all 156 outputs; canonical first representative retained, yielding 878 classes in prior engineering run.
- One input split `28 public / 64 query / 64 evaluator`, sorted IDs, disjoint, generated by the reviewed `input_split(seed)` semantics; **official split seed has NOT been chosen or frozen**. Every official task uses the same split. Scope of inference is therefore **conditional on this one split**, not all possible splits.
- A task is `T_i = (target_semantic_class_i, unordered_public_pair_i, B1_rng_streams_i)`. Target class is sampled independently, uniformly, **with replacement** from all 878 unique semantic classes. The two distinct public IDs are selected uniformly without replacement from the 28 public IDs, independently of target. Five B1 seeds/streams are independent nested repeat randomizations within the same task; they are NOT five tasks.
- One task draw is the inferential unit; `n=4096` independent draws. Repeated class IDs and shared evaluator input IDs do not constitute independence from a new domain, but are allowed IID draws **under this stated artificial generative distribution**. Target depth, operator types, public ambiguity and F3 status are diagnostic strata; **no unknown family-level random effect** or target-family bootstrap is invoked for the primary claim. If the study instead seeks superpopulation-of-families generalization, that is a **different protocol**, requiring new families and a new design before scoring.
- B2 weights hypotheses equally by semantic class, which matches the intended uniform prior conditional on the two public examples. Alternative syntax-weighted or depth-weighted target laws are **separate exploratory sensitivity distributions** only and must not be used to select the primary estimate.
- A public deterministic source generator and a fixed symbolic catalog are not hidden data; the evaluator-only target ID and oracle/audit outputs must be isolated at process/interface boundaries. A hash of a guessable small seed is not a security guarantee.

## Gate F: exact structural, non-scored feasibility

Consider each unordered 2-ID pair from the 28 *public pool* and the induced partition of the 878 catalog signatures by their two public outputs. This enumerates the possible **hypothesis classes** without running any official task, sampling official target IDs, issuing a genuine Oracle query or comparing held-out labels. Each partition block is the potential public-observation context `H0`.

**Disjoint states:** F0: impossible or empty consistent H for a purported valid task (integrity fault; theoretically zero in this realizable world); F1: `|H|=1`; F2: `|H|>1` but all 64 query IDs have zero disagreement; F3: `|H|>1` and at least one of the 64 question IDs distinguishes semantic classes. F4 is a **nonexclusive nested flag within F3**: response-dependent second-question branching can distinguish additional states beyond a one-question choice.

Count both unweighted public contexts and **target-and-public-pair-weighted** prevalence: for each public pair and each partition block, weight `|H|/(878*C(28,2))`. This weighting is uniquely implied by the proposed uniform target/public-pair distribution and does not require selected official target IDs. No private evaluator-only target label or held-out exact-match computation is permitted in Gate F.

**Necessary feasibility bound:** because all valid F1 and F2 contexts cause B1/B2 to have the same final program without useful queries, `Delta <= P(F3)` in absolute percentage-point units when `D_i∈[-1,1]`; if `P(F3)<0.05`, a +5pp population advantage is **structurally impossible**, and confirmatory activation stops. `P(F3)>=.05` is *necessary but not sufficient*. If F3=0 => `UNDERIDENTIFIED`. Log F0 independently; zero F0 expected.

Additional design-only indicators: distribution of `|H|`, count/fraction of discriminating query IDs, maximum Gini and gap versus uniform-input expected Gini, depth-two reachability with and without adaptive second question. **Do not compute B0/B1/B2 held-out performance, program decisions against evaluator-only truth, or a future official target score during Gate F.**

This finite design census is not independent experimental replication. Treat it as an exact **structural proof obligation** under stated semantics and source identity. Independent second implementation must cross-check the catalog, partition weights and counts without importing the learner's classification helper.

## Gate C: actual evidence, only after separate authorization

Arms: B0 no query, B1 up to 2 uniform random allowed remaining query IDs (five independently derived seeds per task), B2 up to 2 max-Gini questions over semantic class hypotheses, deterministic ID tie-break. All arms share target, two public observations, 64 query options, 64 audit inputs, interpreter and same max-query budget; actual #questions can differ by legal stopping. B1 samples uninformative remaining IDs if informative ones exist: this is an **intentional baseline characteristic** and must be disclosed.

**Primary task-level metric:** with `a_i(π)` equal to the fraction correct among the fixed 64 evaluator-only inputs after the last legal question and canonical first surviving program,
`D_i = a_i(B2) - (1/5) * Σ[r=1..5] a_i(B1,r)`,
`Delta = E_{T~P_v1}[D_i]`.
All valid F1/F2, no-gain and negative-gain tasks remain in the population and the denominator. Each `D_i∈[-1,1]`; 64 evaluator inputs and 5 B1 replicates are **nested observations**, never `4096*64*5` independent samples.

**Only H1 confirmatory test:** two-sided .05 task-level paired Student-t CI around mean `D_i`, based on `n=4096` independent task draws, `df=n-1`; declare evidence of **positive within-world query-policy advantage** only if its 95% CI lower bound >0 and all integrity gates pass. Preserve actual negative effects, false identification, missing counts, unexpected stopping, CI upper/lower and total task count. As a separate descriptive **practical-size classification**, report whether point estimate is ≥+0.05; this threshold is **not** an additional powered hypothesis test. Practical adoption additionally requires an explicit pre-registered cost/benefit decision (not supplied by any positive H1 result alone). Do **not** assert .89 power for the joint statistical+practical rule.

**Predefined secondary mechanism outcomes:** mean hypothesis reduction, final-program change, number of zero-Gini selections, informative-query prevalence, status F1/F2/F3/F4, number of questions, per-task B0 accuracy, B2-minus-B0, posterior/calibration diagnostics, false-identified status and unsupported targets. H2/H4/H5 are explanatory (no family-wise confirmatory p-value claims). Since `B1+` (uniform over *currently positive-Gini* remaining input IDs) is not implemented in the baseline, a separately versioned, reviewed new diagnostic adapter is required if a B1+ secondary arm is ever introduced; do not silently relabel baseline B1 as B1+ or treat an absent result as observed.

**Inference/coverage caveat:** The IID model describes **the synthetic task-draw process with replacement**. An external domain, a new operation vocabulary, unseen target family, or a changed input split is not in the estimand. Exact scoring of the complete finite population in a later model-checking study would have no sampling CI and must not be presented as independent transfer evidence.

## Randomness, source-first lock and trust boundary

Before Gate C:
1. Independent custodian generates a 256-bit random secret root, commits to `SHA256(domain || root || protocol_version)`, keeps root off GitHub and away from learner, evaluator PR and ordinary CI. Hash of low-entropy enumerated target ID/seed is not enough.
2. Freeze exact code/tree/blob SHAs; operation order, canonical class IDs/signatures, fixed split seed+digest, 28/64/64, target draw and public pair sampling, five B1 seeds/stream expansion, stable task ID derivation, interpreter, canonical final program, statuses, resource ceiling, 4096 tasks and no optional stops.
3. **PRF domain-separated expansion** (HMAC-SHA256 or independently reviewed equivalent) for target/pair/B1 streams and unique task IDs; use rejection sampling for unbiased selection of class and public-pair indices. Define exact byte order, encoding and retry-counter behavior in implementation PR and lock their known-answer vectors **before** genuine labels. Fixed `random.Random` for current B1 chooser remains pinned and replayed under the reviewed Python runtime.
4. Run isolated roles/processes. Learner accepts only `PublicTaskView` and `QueryAnswer` for one legal proposed input. Evaluator owns target ID, target-family annotation, seed root, Oracle and all 64 audit labels; independent auditor validates the saved transcript, not by trusting learner-supplied hashes. No target ID, family metadata, future answer, evaluator output or audit verdict may enter the learner.
5. Evidence custodian preserves immutable raw originals and restricted private audit evidence; public repo stores redacted task/aggregate receipts and content identities only. Encrypted Google Drive archives and historic frozen sources remain untouched. The source, custody, methods, run ledger and result must carry separate hash identities, reviewer attestations and timestamp/provenance.
6. Independently review exact-head source/CI and confirm original historic workflow still disabled by owner setting; a green CI alone cannot certify secret isolation. Allowlisted invented/synthetic tests only on PR. Separate activation decision controls one-shot real scoring. Any P0/P1 leak => STOP.

## Status semantics and failures

- `F0 / model_inconsistent`: synthetic valid-world target should never produce H empty; treat as contract/provenance violation, not a model failure to hide.
- `identified`: exactly one finite-domain semantic class, not proof of universal function identity.
- `query_unidentifiable`: remaining pool offers no distinguishable signatures, not global impossibility.
- `budget_exhausted`: after two successful answers with >1 class; not automatically scored as wrong.
- `integrity_invalid`, forged/reordered receipt, wrong split, repeated/unallowed question, missing independent audit: **no scientific estimate**, stop and document; do not silently coerce to 0 or discard favorable/unfavorable tasks.
- `not_observed` remains distinct from genuine false prediction. A failed run triggers independent root-cause review; **no unblinded fix-and-reuse** of target labels or rescore under the same confirmation claim.
- If Gate F fails, N4096 cost budget fails before exposure, or source/seed review fails: halt as `UNDERIDENTIFIED`, `UNAFFORDABLE`, or `NOT_READY`, revise a NEW version; no scored evaluations.

## Cost/engineering definitions

Use **counts and clocks as separate dimensions**: `queried_oracle_calls`, `positive_gini_queries`, `candidate_lookups`, `canonical_primitive_calls`, `selector_process_cpu_ns`, `learner_process_cpu_ns`, `oracle_process_cpu_ns`, `evaluator_cpu_ns`, `wall_elapsed_ns`, `catalog_precompute_cpu_ns`. Define source/phase of each clock and do not attribute evaluator-only audit cost to the inference policy. Log max memory and failures.

Two economic interpretations:
- **Online inference cost**: per-task public parsing + question selection + chosen-Oracle cost + belief update + prediction (exclude auditor-only evaluation).
- **Amortized cost at registered workload M**: `C_precompute/M + mean_online_C`. Report at `M=1, 100, 4096` tasks without selecting the best M after measurement. If no real-valued Oracle cost can be grounded, report **number of queries** rather than inventing latency or yen equivalent.

Compute the paired **cost difference** with the same task IDs, including B1 replicas nested per task. CPU improvements are not implied by primitive counts. No automatic promotion to a permanent skill on the basis of correctness alone.

## Data architecture and contracts

~~~mermaid
flowchart TB
    C["Immutable finite Catalog (existing inquiry_world)"] --> F["Read-only Gate F: partitions, opportunity (PROPOSED)"]
    F --> G{"Independent feasibility / scientific method review"}
    G -->|block| RED["Revise NEW version, no scoring"]
    G -->|pass and separate lock| LOCK["SourceLock + root/seed custodian (FUTURE)"]
    LOCK --> E["Independent active_evaluation (FUTURE)"]
    E --> PUB["PublicTaskView: two labeled examples + query IDs"]
    PUB --> L["Existing active_learning: B0/B1/B2"]
    L --> Q["QueryProposal before answer"]
    Q --> ORA["Oracle (evaluator-owned)"]
    ORA --> ANS["Only selected QueryAnswer"]
    ANS --> L
    L --> EP["InquiryEpisode: ordered replay + final program"]
    E --> SEC["Withheld target + 64 audit labels"]
    EP --> R["PairedOutcome / Metrology report (FUTURE)"]
    SEC --> R
    R --> SCI["Independent scientific claim + cost review"]
    SEC -.->|NO INPUT| L
    R -.->|NO POLICY FEEDBACK| L
~~~

~~~mermaid
flowchart LR
    SPEC["FeasibilitySpec v2"] --> GATE["F0-F3 exclusive / F4 nested"]
    GATE --> LOCK["SourceLock manifest"]
    LOCK --> TASK["Task ID + PublicTaskView"]
    TASK --> PROPOSAL["QueryProposal"]
    PROPOSAL --> ANSWER["QueryAnswer"]
    ANSWER --> HISTORY["InquiryEpisode + before/after H commitments"]
    HISTORY --> OUTCOME["PairedOutcome: B0, B1x5, B2"]
    OUTCOME --> REPORT["EvaluationReport + CI + costs + validity"]
    SECRET["Target / held-out labels / root: evaluator-only"] --> OUTCOME
    SECRET -.->|forbidden| PROPOSAL
~~~

**Existing contracts:** `Catalog`, `InputSplit`, `QuerySession`, `QueryProposal`, `QueryAnswer` and `active-query/2`. Preserve exact Python built-in type checks, full chronological replay, and canonical internal catalog; never weaken these with a new adapter.

**Proposed new sidecar schemas** (NOT implemented): `FeasibilitySpec/2` (unscored disjoint strata, weighting, source hash, no heldout accuracy), `SourceLock/1` (exact build/protocol and private-seed commitment), `PublicTaskView/1`, `InquiryEpisode/1` (full ordered transcript separate from original `active-query/2`), `PairedOutcome/1` (one independent task, B1 list of five nested replicates, validity and cost fields), `EvaluationReport/1` (analysis identity, confidence method, complete denominator, aggregate negative/zero cases, provenance). All require version, task/source/split hash commitments and independently validated length/type bounds. Future schemas must not place any secret evaluator-only field in learner-visible views.

**Intellectual action representation — research bridge only:** `InquiryAction = (goal, available observations, candidate discriminations, chosen intervention, returned observation, belief transition, cost, evidence)`. Later Stage II may learn when to choose an action and Stage III may test mappings to other domain adapters. **This is not a claim that existing ACTIVE-001 learned it**.

## Decision and release gates

- **Gate 0: design agreement:** approve or revise THIS proposed decision, with explicit interpretation of N4096, IID uniform semantic-class population, no out-of-domain claims, new B1+ secondary diagnostic and separated economic value.
- **Gate F: engineering implementation** in a *new* PR, only synthetic, unscored structural enumerator and independently checked exact count/provenance; do not touch historic scoring sources. Unfavorable F0/F2/F3 distributions kept.
- **Gate P: independent methodological and numerical review:** confirm IID/sample size, practical threshold interpretation, power/coverage and finite-world relevance; record source/seed protocol **before** official target draws.
- **Gate E: evaluator PR:** distinct owner/reviewer, independent oracle/audit, leakage negative fixtures, safe CI, freeze lock and original-workflow disabled external check.
- **Gate A: one-shot scored activation** is explicit, independent, separate from merge. Preserve raw originals and publish **all** unfavorable results.
- **Gate R: scientific acceptance**: if H1 CI lower>0 and integrity passes, accept only bounded *within-task information-seeking* capability. A practical-value or Stage II/Sleep / Stage III/transfer claim requires new research with its own experiment and reviewer decision.

**Decision status:** `design_complete_for_review` / `not_frozen`. Nothing here authorizes scored task generation, official labels, historical rescore, API/DSL modification, new credentials or production adoption.

## References and provenance

Repository: [Issue #96](https://github.com/ryonakayama234/DekaSugi/issues/96), [ACTIVE-001 spec](../../docs/specs/ACTIVE-001.md), [ARCH-001](../../docs/architecture/system.md), [ARCH-002](../../docs/architecture/contracts.md), [METRO validity](../../docs/metrology/validity.md). External conceptual context (NOT evidence of DekaSugi effectiveness): Golovin & Krause, [Adaptive Submodularity (JAIR 2011)](https://arxiv.org/abs/1003.3967); Filstroff et al., [Targeted Active Learning for Bayesian Decision-Making (TMLR 2024)](https://openreview.net/forum?id=KxPjuiMgmm). No theorem from these works is assumed to apply automatically to this engine.

[Design rationale ADR-0006](../../docs/architecture/decisions/ADR-0006-active001-scientific-design.md) / [Unscored design ledger](runs/20261030-design-v2-review-ledger.md).

## Branch-side Gate F engineering evidence — ADDENDUM, not prospective scientific proof (2026-10-30)
[Invented split census record](runs/20261030-gate-f-invented-census.md), [implementation](../../packages/active_feasibility/__init__.py) and [tests](../../tests/test_active_feasibility.py) provide an engineering-only **read-only symbolic context census** for split seed 20261030 (historical invented fixture, **not future official confirmatory split**). Of 331884 weighted hypothetical class/public-pair combinations, 282111 (85.00%) have ≥1 allowed discriminating question F3. This is a **necessary information opportunity**, not evidence that the B2 max-Gini policy improves held-out accuracy, not prospective scientific power, and not a locked 4096-task sampling authority. F4 has **not been computed**, so it must not be described as a measured second-query advantage. This addendum updates the implementation status; earlier prospective design text remains visible for historical provenance. No real scoring.
