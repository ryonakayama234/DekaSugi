# OPPORTUNITY-002 — Ability Boundary and Identification preregistration proposal

id: OPPORTUNITY-002-PLAN
status: draft_method_v0; NOT_FROZEN; design_only; scored_activation_prohibited
updated: 2026-10-29
tags: experiment, preregistration, opportunity, identifiability, synthetic

## Hypothesis
This is **not** an amendment of OPPORTUNITY-001 PILOT-V1. Frozen original results (64 paired, OFF=ON=48 correct, no accuracy discordance, B1/B2/B3 each 0/16 eligible decision errors) yield `UNDERIDENTIFIED` and remain immutable. New independent research must separate:
- `H1 representability`: the current pure flat lower(trim(x)) macro conservatively extends primitive-only expressions, without adding semantic functions under an identical 4-expanded-node cap.
- `H2 exploration`: changing vocabulary/order can change how soon a solution is considered, despite equal representation sets; increasing a budget on a *new* synthetic family can change bounded accessibility.
- `H3 generalization`: distinct public-example-matching programs can differ in private audit correctness, if such a witness is constructible under the selected grammar.
- `H4 decision`: where a unique arm is better, distinguish actual frozen-policy choice error from impossibility due to identical admissible observations or a lossy feature map.
- `H5 new ability`: separately, an experience-driven state update might improve future independent competence; no such learned effect is measured by PR1/PR2.

## Scientific scope versus engineering phases
**PR1 (this proposal):** inspect source and register logical claims; no execution results, no source lock for new tasks, no new scored trials.
**PR2 (separate):** invented synthetic finite fixtures, independent structural enumerator/invariants, false positive/negative/adversarial calibration; never invoke existing private scorer or real task generator.
**PR3+ (not yet authorized):** propose a new independent task universe, freeze a full method v1 and source-first evidence, separately review a single future TRAIN-only owner run. Never open/regenerate original 64, old DEV64 or sealed FINAL128. No automatic progression from engineering calibration to scoring.

## Planned discriminating contrasts (PR2 synthetic / PR3 future distribution)
| ID | Intervention and control | Measured contrast | Identity conditions | Classification |
|---|---|---|---|---|
| C-R0 | Primitive-only vs same primitives + one verified two-call macro, cap4/candidates100 | expanded program-set identity, cost/selection differences | immutable semantics, same audit examples, common budgets | representation closure |
| C-S1 | Same registries, **synthetic only** cap5 vs cap100 | availability by candidate position | exact same public examples, audit, registry and expansion cap | budgeted accessibility |
| C-G2 | OFF vs ON, same public two examples; independent **synthetic** third example (future real C-G2 is gated) | **both-public-found** conditional third-audit discordance, plus separate public-not-found counts | frozen first-matching program, independent third audit, NEW versioned normalizer distinguishing valid generalization miss from integrity failure | generalization/inductive bias (no live scorer authorized) |
| C-P3 | Frozen B1/B2/B3 vs both-arm post-hoc outcomes, decision sealed first | regret / decision errors | same public observation and preregistered accuracy-first then cost order | policy opportunity |
| C-I4 | Two distinct evaluator states with identical *admissible observation* | policy identifiability lower bound | deterministic decision, information boundary fixed | information insufficiency |
| C-E5 | Representable target vs invariant-proven unrepresentable target | oracle reachability and proof | fixed string alphabet, semantics, expanded DSL | expressivity boundary |

Contrast groups are mechanisms and **not** a guaranteed outcome-generating fresh population. Synthetic classes never support a confirmatory generalization claim by themselves. Any new primitive injected by an experimenter is a control, not autonomous invention.

## Metrics
Primary when real trials are authorized: `paired_audited_accuracy_diff` = mean(ON_correct − OFF_correct) across **all valid paired tasks**; report ON-only, OFF-only, both-correct and neither counts, their denominators and uncertainty. For all valid cases report canonical `primitive_invocations` and search candidate counts separately. Among both-correct only, compare OFF−ON canonical verifier calls; ties explicitly counted. For one-arm-correct apply correctness priority; avoid arbitrary conversion of a success to calls. Policy regret: accuracy loss where choice failed and other succeeded; extra primitive calls **only when both succeed**. Do not label neither-correct as an eligible cheap action. If `n_eligible=0` report `not_estimable`, **not** 0/0 or 0/N.

Separate total CPU, wall, policy inference CPU, optional learning CPU amortization and auditing cost; any unmetered component is `not_observed`, not zero. No arithmetic across incompatible units. The **legacy** OPPORTUNITY-001 `false_solved` flag always remains invalid/safety stop and must NEVER be relabeled or relaxed. For a *new*, separately versioned future C-G2 evaluator, distinguish `public_found_audit_incorrect` (trusted public verifier passed, independently correct provenance/label, third example failed: **valid generalization error**, `audited_correct=false`) from `integrity_invalid` (public verification, trace, hash, trusted audit label/raw, provenance or chronology contradiction: **hard stop**). `public_not_found` is a distinct valid search failure, not a first-solution generalization miss. The old `normalize_audited_trial()` raises on failed third audit and **cannot** be reused for C-G2. Missing audit => `not_observed`, excluded with reason; mismatched measurement contracts => `non_comparable`; never treat invalid evidence as negative accuracy.

### C-G2 prospective feasibility gate (NOT implemented)
Before including any genuine C-G2 task in the paired estimand, independently implement/freeze a **new** evaluator and normalization contract with adversarial invented tests covering (a) both arms select public-correct programs but only one passes the private audit (valid discordant generalization), (b) genuine `public_not_found`, (c) deliberate public-verifier contradiction, (d) mismatched audit label and source/hash, and (e) missing/incomplete records. Reject (c)/(d) as `integrity_invalid`, not as `audited_correct=false`. Keep old PILOT-V1 `false_solved` hard stop unchanged. Report conditional `n_both_public_found`, `n_audit_discordant_given_both_public_found`, all-task `n_paired_valid`, `n_public_not_found`, `n_integrity_invalid` and `n_not_observed`; zero both-found support means `not_estimable`, not an observed zero effect. The future source-first commit and precise inclusion/exclusion rules must be independently reviewed **before** any new private third-example use. PR1 and PR2 authorize neither evaluator construction against real tasks nor scored trials.

## Future sampling and identification prerequisites (NOT FROZEN)
1. Specify target population and independent source families. Distinct source IDs/seeds, no training/evaluation literal overlap or template leakage; all splits explicitly *new* and disjoint. Keep fresh training-only and independent evaluation layers separate.
2. Positive diagnostic cells must exist for both ON-only/OFF-only accuracy contrasts if mathematically constructible; otherwise declare the accuracy-effect objective structurally impossible under selected premises and redesign. Independently test cost-only cells in both directions, ties and both-unsolved cases. Outcome-stratified post hoc selection is prohibited for confirmatory prevalence estimates.
3. Predeclare admissible policy information (public TaskSpec, exact feature version, any permitted observation cost), fixed B1/B2/B3 frozen snapshot hashes, arm choice order, allowed skill library and first-solution semantics. Predecision public choice seal MUST precede scorer access.
4. Independently freeze numeric values **before any genuine scoring**: number of family clusters, per-family tasks, candidate budget, expanded cap, character sets, generator seeds, one-sided/two-sided alpha if testing, interval coverage, minimally meaningful effect, anticipated discordant share, cluster intraclass correlation/design effect, multiplicity handling, stop rule and precision/power calculation. Numbers from OPPORTUNITY-001 are hypothesis-generating only, not independent pilot data for confirmatory power.
5. Example for planning only, NOT adopted: 15% ON-only and 5% OFF-only, 10pp net paired improvement, independent-pair two-sided alpha .05 and 80% power yields ~155 pairs by a normal McNemar approximation; positive cluster correlation increases requirement. Do not register 155 or repurpose historical 64 without a *new* reviewed method.
6. Predeclare all denominators/exclusions (intended N, source-generated, attempted, paired-valid, false_solved, audit missing, each eligible decision class). Include zero support and an explicit `inconclusive` branch if the contrast cannot be estimated.
7. Real raw third audits and source mapping remain owner-private outside GitHub/CI; verify original byte SHA, encrypted versioned offsite restore, ACL and retention independently before any first trial; do not assume provider deletion-proof/WORM.
8. Read-only provenance receipts need source blob SHA, original byte/content digest separately, immutable plan, policy, skill, evaluator, meter, environment and accepted exact-head reviewer. Fail before project imports if source-first check is required; never use historical DEV/FINAL generation or `freeze.verify_frozen` in the new custody path.
9. A future independently reviewed **once-only** owner-local runner must persist STARTED/ARM_STARTED before action, stop on first provenance/confidence error, never retry, and publish only redacted aggregate with independent readonly recount.

## Acceptance
**PR1 C01:** Formal proof obligations P1–P4 and their limits are reviewable, not misreported as executed.
**C02:** Every estimand states measured construct, arm, unit, eligible denominator, missingness, forbidden evidence/causal claims.
**C03:** C-R0/C-S1/C-G2/C-P3/C-I4/C-E5 distinguish expression/search/generalization/policy/information.
**C04:** Numeric power/precision is a **future preregistration obligation**, not an invented committed sample or retrospective significance test.
**C05:** System Mermaid + data flow/trust contract + AGENTS/INDEX/roadmap + run register kept together.
**C06:** PR1 leaves Python, frozen policy/generator, all historical evidence and CI workflows unmodified.
**C07:** No new scored tasks, no heldout generation, no owner-private original accesses or unlock commands.
**C08:** Independent latest-head review and PR CI required before merge, with an explicit resolution of inherited main-push old DEV smoke/source-lock conflict.
**C09:** PR2 must independently verify structural counts 40/47 and synthetic tests before any new live method is proposed.
**C10:** An unsupported result stays `not_observed/inconclusive` and never becomes a PASS.

PR1 research decision status: **PROPOSED / NOT APPROVED FOR SCORING**. This file deliberately contains no final generator seeds, N, frozen new task manifest or executable scorer because no such experiment has been approved. A future method v1 must be an independent preregistered immutable revision; results never retroactively authorize this proposal.

[Spec](../../docs/specs/OPPORTUNITY-002.md) / [Independent reviewer checklist](../../docs/specs/OPPORTUNITY-002-REVIEW-CHECKLIST.md) / [Run index](runs/README.md) / [Issue #86](https://github.com/ryonakayama234/DekaSugi/issues/86).

## PR2 synthetic engineering calibration (separate from future scored method)
Read-only [standalone checker](../../scripts/opportunity2_boundary.py) and [synthetic tests](../../tests/test_opportunity2_boundary.py) check source-inspected predictions with fixed invented examples: OFF40/ON47, independent-set oracle, on-expanded=off, budget5 OFF exhausts / ON succeeds at candidate5, budget100 both succeed (OFF6, ON5), restricted ASCII negative, fail-closed bad operators/budgets. No real TaskSpec IDs, private third audits, learner updates, historical generator runs or old DEV/FINAL. This does **not** freeze the future live distribution, authenticates no frozen SkillCandidate/source hash and authorizes zero new scored trials. Record exact CI and independent scientific review separately; any failure returns to PR1 design rather than adjusting historical methods.
