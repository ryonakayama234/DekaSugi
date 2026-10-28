# OPPORTUNITY-001-PILOT-V1 — fresh TRAIN-only exploratory actionability method

id: OPPORTUNITY-001-PILOT-V1
status: method_spec_frozen_before_outcomes; source_and_manifest_freeze_pending; not_run
updated: 2026-10-28
tags: pilot, preregistration, fresh-train, actionability, frozen-method, no-holdout

> This is the immutable **METHOD specification for a future TRAIN-only exploratory pilot**. It is **not** a scientific confirmation, and does not authorize scoring until an independently reviewed source-first hash / manifest / skill snapshot lock and one-shot main-only activation are separately recorded. Source implementation must match every rule below; a disagreement requires a new method version and fresh seeds, not a quiet amendment.

## Research objective and interpretation

Identify whether a single frozen validated skill ON/OFF yields any independently audited advantage, and whether existing fixed EXP-0003A B1/B2/B3 Kernel selectors miss it, on entirely new TRAIN-scope tasks. The pilot measures *fixed-two-arm actionability*, not a new learned skill, broad intelligence, general representability, or the validity of a different active learner.

Method basis: [OPPORTUNITY-001 spec](../../docs/specs/OPPORTUNITY-001.md) and [plan proposal](plan.md). Historic EXP-0003A DEV64 is descriptive only; original FINAL128 remains sealed and must not be accessed.

## Dataset population: exactly 64 NEW TRAIN tasks

- 8 family strata in exactly this order: `identity`, `trim`, `lower`, `upper`, `normalize_lower`, `normalize_upper`, `reverse_ood`, `replace_first_ood`.
- Exactly 8 task indices `i=0..7` per family; exactly **2 public examples** (j=0,1) and **one distinct evaluator-only audit example** (j=2) per task.
- Seed formula (decimal integers): `seed = 910000000 + family_index * 100000 + task_index * 10 + example_index`; reject duplicate seeds. Namespace is separate from the historic EXP-0003A known TRAIN/DREAM master seeds and does not instantiate any old DEV/FINAL task or generator.
- `ALPHABET = "uvwxYQ03"` (8 distinct characters), Python `random.Random(seed)`; `n = rng.randrange(3,8)`, then draw `n` characters independently via `rng.choice(ALPHABET)`. Retry up to 4096 times if token has fewer than two distinct characters or is a palindrome, or `lower/normalize_lower` lacks uppercase, or `upper/normalize_upper` lacks lowercase. If no valid token, **abort**; do not choose another seed after seeing outcomes.
- Whitespace pairs, ordered: `[(" ", ""), ("  ", " "), ("\\t", "\\n")]`; for example j use `(prefix,suffix)=WHITESPACE[(i+j)%3]`. These quoted escape sequences denote actual tab/newline characters at runtime. The alphabet deliberately excludes the output prefix "Z" so `replace_first_ood` always changes the first character.
- Target mappings:
  - `identity`: input=token, output=token.
  - `trim`: input=prefix+token+suffix, output=token.
  - `lower`: input=token, output=token.lower().
  - `upper`: input=token, output=token.upper().
  - `normalize_lower`: input=prefix+token+suffix, output=token.lower().
  - `normalize_upper`: input=prefix+token+suffix, output=token.upper().
  - `reverse_ood`: input=token, output=token[::-1].
  - `replace_first_ood`: input=token, output="Z"+token[1:].
- Public TaskSpec: domain `string_to_string`, `schema_version=0.1`, limits exactly `max_ast_nodes=4`, `max_candidates=100`. Canonical `public_shape` JSON includes exactly schema/domain/limits/two example objects in j order, and `task_id = "t-" + sha256(json.dumps(public_shape,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")).hexdigest()`.
- Private/source ID is `op-pilot-f{family_index:02d}-i{task_index:03d}`, evaluator-only. No family, seed, source ID or third example is passed to any Kernel chooser. Abort on duplicate public IDs/source IDs/new seeds, unexpected count, or any collision with legally available historic TRAIN/DREAM public IDs; do not generate old DEV/FINAL to check overlap.
- Python `random.Random` algorithm/stdlib version and Python minor version shall be reported and a canonical complete *public* task manifest SHA-256 locked before trial outcomes. Even with seed formula public, third audits are logically isolated from the learner, not cryptographically secret.

## Skill, policy, budgets, intervention

- **Only candidate skill**: exact EXP-0003A preexisting `freeze-v1.json` top `SkillCandidate` (body hash and skill ID must match source-first frozen assets); no freshly learned or modified macro, no library promotion.
- **Primary pretrial policy**: historic frozen B1 TRAIN-only KNN snapshot from EXP-0003A. **Secondary pretrial policies**: B2 and B3 frozen snapshots (descriptive only). Validate all three immutable SHA256 and `choose(TaskSpec, snapshot)` inputs; all three choices MUST be sealed **before** any ON/OFF search. No oracle, audit, family, seed or paid trial outcome is exposed to the chooser.
- **Two actual actions on each task**: OFF canonical fixed primitives, ON same trusted primitives + exact frozen skill; fresh independent `Registry` and `PrimitiveCallMeter` per action. EXP-0003A `bounded_synthesize` semantics and search order unchanged, same max expanded AST 4, max candidates 100. Meter scope is verifier-time canonical primitive invocations; CPU/wall by phase recorded separately.
- Independent third example audits actual selected AST; `false_solved` is a **safety stop**, with a redacted failed-run provenance record. It may not be converted to a valid/negative label.
- Research pairing: independently compare OFF/ON only **after all B1/B2/B3 decisions have been recorded**. Post hoc best-of-two is a diagnostic upper envelope, not an executable Oracle. Do not let the comparison choose the skill or refine a policy mid-run.

## Evidence protocol / phase gates

1. A new dedicated implementation PR creates a pure new TRAIN-pilot generator and public-hash-only preflight, plus negative fixture tests; no new scored task in PR CI.
2. Independently review implementation *exact head* and its method equivalence to this file; pin all source Git blobs, canonical public TaskSpec manifest hash, fixed policies/skill hash, Python version, code commit, and explicit one-shot activation scope to a **separate immutable source-freeze record**. Source lock must complete before first paired trial.
3. A distinct reviewed main-only **once-only activation** runs the 64 TRAIN tasks, checks SHA and policy decisions before the first OFF/ON trial, and writes originally observed evidence as immutable artifact(s). Never rerun to improve results. PR CI cannot trigger scoring; a failed run records an incomplete result and does not quietly retry.
4. Independent stdlib evidence recount verifies exact counts, classification, decision chronology/source identities, source lock and no private material in public output. Restricted/private raw audit retention must be verified before expiry and never committed to public Git.
5. Publish original public aggregate and redacted provenance (success/failure) to `runs/`; keep private third examples/evaluator-only generator labels out of public repository and learner. Source lock must bind candidate skill, policy, generator, meter/verifier, environment and full public dataset hash.

## Metric priority and denominators (not mutable after run)

- `paired_valid`: both independently audited outcomes and equivalent source/budget.
- On valid tasks, classes: both_correct_on_cheaper / both_correct_off_cheaper / both_correct_tie / on_only_correct / off_only_correct / neither_correct.
- Cost regret `max(0,selected_calls-min(off_calls,on_calls))` ONLY when both audited correct. On-only/OFF-only accuracy misses separately, with regret null. Neither-correct: unknown, regret null.
- For each B1/B2/B3, report `unique_better_action` and `policy_decision_error`; denominator excludes ties/neither; `choice_sensitivity` denominator valid paired. Report overall and per family; all excluded/invalid counts explicitly.
- `best_of_two_success` is retrospective coverage restricted to these two fixed arms. Primitive calls, candidates, search CPU/wall, audit CPU/wall and policy inference cost separate; no invented cross-scope speed improvement. **No scientific p-value or confidence interval for capability gain from this pilot**. Eight family strata are not eight independent real-world domains.
- An expression-proof claim requires separate formal invariant proof and review; `reverse_ood` family label or both-arms-unsolved cannot substitute.

## Exploratory branch rules / not scientific gates

- If at least **8 of 64** valid tasks have a unique better arm and fixed B1 misses any such choices in at least **2 different families**, prioritize new independently registered AL-v2 policy hypothesis (but don't declare improvement).
- If at most **2 of 64** valid tasks have unique better actions while substantial both-unsolved cases remain, prioritize separately designed search/skill-invention diagnostic, never claim DSL impossibility based on this run.
- Otherwise, underidentified, and propose a new fresh identification distribution with adequate sample size; do not tune this pilot and rescore the same tasks.

These are resource-allocation heuristics, not probability/error-controlled scientific hypothesis tests. **Any** source mismatch, unexpected task count, false_solved, private leak, missing audit, independent review failure, forbidden holdout access, or incomplete raw evidence preservation stops promotion. Preserve precise numbers and failure causes.

## Scope and immutable exclusions

This method is **TRAIN-only**, not EXP-0003A v1 H3 or a new FINAL. No existing DEV64 reanalysis beyond the archived diagnostic; no original FINAL128 or EXP-0002B FINAL112 execution or reclassification. Full confirmatory study requires an independently designed fresh DEV/FINAL, power/precision basis, preregistration, review and separately authorized one-shot run.

Related: [Issue #60](https://github.com/ryonakayama234/DekaSugi/issues/60) / [PR2 calibration](runs/20261028-pr2-fixture-calibration.md) / [METRO validity](../../docs/metrology/validity.md).
