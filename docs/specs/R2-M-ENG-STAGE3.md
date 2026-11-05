# R2-M-ENG Stage 3 — controls / closure / synthetic runner

id: R2-M-ENG-STAGE3-20261105
status: implemented_in_draft / engineering_only / pending_exact_head_ci_and_independent_acceptance / no_scientific_scoring
updated: 2026-11-05
tags: r2-m-eng, stage3, controls-v2, closure-unknown, runner, synthetic-fixtures

## Authority and unchanged boundaries

The baseline is the Owner-approved, merged Stage 2 [PR #177](https://github.com/ryonakayama234/DekaSugi/pull/177) at aed3fea224ce4d3a9d93759effa3d3957e0d5776. [Owner conditions A-D](https://github.com/ryonakayama234/DekaSugi/pull/175#issuecomment-6633458178) authorize Stage 3 artificial engineering after independent Stage 2 acceptance. Method authority: [adopted R2-M v2 §3–§5](https://github.com/ryonakayama234/DekaSugi/blob/d32606c12608b6f6bd4e09fd758e4eb4f69089f7/docs/research/R2-M-20261104-single-method-v2-proposal.md), [scope](R2-M-ENG-SCOPE.md) and [Stage 2 contract](R2-M-ENG-STAGE2.md).

This is a new main-based **Draft**. Owner approval is still required before merge. Only artificial known F_aff laws and fixture tests are authorized. Frozen R1/v1, historical sealed/heldout sources and old results remain untouched. No genuine private USE, independent scientific custody, preregistered source, learned policy, scientific scoring or claims about M_use, M_gap, N_rep, U or T.

## Data flow and trust boundary (ARCH-001/002 delta)

~~~mermaid
flowchart TD
    E["Evaluator fixture: human-supplied synthetic F_aff coefficients"] --> G["Stage 1 public gateway: P, Q001 precommit, response"]
    G --> V["Public decoder / independent validator"]
    V --> S["Single immutable Snapshot/v2 and externally pinned SHA"]
    S --> C["Stage 3 closure: UNKNOWN only"]
    S --> R["Stage 3 runner: separate cwd and process per arm"]
    R --> F["Stage 2 F00, F10 unchanged"]
    R --> K["Five Stage 3 controls, separately defined"]
    F --> T["Public UseTrace/v2, local exclusive receipt"]
    K --> T
    C --> M["Public fixture manifest; no private scores"]
    T --> M
    M -.-> X["Real private USE scoring: NOT AUTHORIZED"]
~~~

Only evaluator-side packages/r2_m_eng/runner.py imports source_gateway. Learner-side controls.py and closure.py never see source coefficients, oracle answers, hidden law metadata or USE outcomes. Children receive only one canonical absolute Snapshot path, its independent expected bytes SHA256, an input point, an arm and an exclusive output trace path. Local hashes/creation are neither trusted timestamps nor independent external custody; the module split does not defend against a malicious same-process actor.

## Frozen controls — R2-M-CONTROLS-v2.0

Five **comparator arms**, not newly added fallback routes in existing F00/F10. All are fixed before any artificial source observations. No target-specific macro injection.

| Arm | Capability and tie/capacity | Accounted work |
|---|---|---|
| STATIC-H+ | Same preprovided F_aff 16-law decoder and tree up to 32 nodes. No persistent body; recreate from public P+Q001 at USE | One decoder, one actual candidate and one independent validator in addition to restore |
| FIXED-MACRO | Entire lexicographic 16-entry a,b,c,d typed-body catalog predeclared before source/public data. Select index from four public responses | Catalog construction happens at Python module import; prep CPU/wall and serialized in-memory bytes reported separately. One public validator of selected body |
| EPISODIC-EXACT | All four public entries preserved, capacity 8. No extrapolation: unseen exact key ABSTAIN | Four public comparisons; no artificial pruning |
| NEAREST-1NN | Hamming over every public row, capacity 8. Vote **all** equally nearest; exact tie ABSTAIN | Four distances, no arbitrary first-neighbor selection |
| STUMP-1 | 14 hypotheses: constant0, constant1, then x/y/z with pairs 00/01/10/11. Min public 0–1 error, first listed tie | 14 fit candidates and 56 public comparisons |

The common affine candidate budget 16 is not 16 generated affine candidates. STUMP has a **distinct** fixed 14-slot family; do not misrepresent its fit candidates as affine-body synthesis. Cost metrics include decoder/validator calls, actual candidate counts, H0 scans, public comparisons, three AST counters, paid Q, restore/store bytes, CPU/wall and process high-water RSS. Macro preparation cost is disclosed separately, **not included in per-use CPU seconds**; the fixture cannot establish a fair lifetime cost advantage. No post-hoc weighted scalar.

Each comparator writes a public UseTrace/v2 with prediction as 0/1 or null, legal_action as PREDICT/ABSTAIN, route, explicit activity states, cost and manifest digest. F01/F11 are NOT_EVALUATED and rejected if invoked. ORACLE-REF is evaluator-only and not callable.

F00 legitimately retains episodic_exact, h0_consistent and runtime_affine_decoder. An artificially weakened OFF route is INVALID. Because its decoder remains reachable, F00 and F10 may agree on **all predictions**; route difference or synthetic fixture accuracy is not evidence of causal M_use.

## Closure — R2-M-CLOSURE-v2.0

packages/r2_m_eng/closure.py reconstructs a deterministic public HypothesisCertificate/v2 anchored to Snapshot SHA/path, public journal digest, frozen dispatch policy, known full Stage 2 route inventory, five separate comparators, resource bounds and unresolved obligations.

~~~yaml
closure_status: UNKNOWN
closure_complete: false
effective_h0_reachability: UNKNOWN
best_off_fallback: NOT_CERTIFIED
m_gap: UNKNOWN
m_use: NOT_CERTIFIED
n_rep: NOT_EVALUATED
u: NOT_EVALUATED
t: NOT_EVALUATED
~~~

There is **no COMPLETE API**. validate_closure_audit compares a given record against a fresh canonical reconstruction and rejects even forgeries whose internal digest has been recomputed: altered closure flags, removed routes, missing unknowns or policy arm claims.

Unproven items include all legal histories, all reachable fallback/Kernel/memory/generalization routes, best legal OFF under equal B, independently proved same-budget nonrealizability, and external source-first custody. The inventory describes the isolated R2-M-ENG wiring; it is **not** a complete proof of effective H0(B).

## Synthetic runner

Example from repository root on WSL2/Linux, using a nonexistent output directory:

~~~bash
python -m packages.r2_m_eng.runner \
  --output-dir /tmp/r2-m-eng-stage3-example \
  --synthetic-affine 1011 \
  --point 111
~~~

1. Validate explicit four-bit artificial fixture and three-bit input; reject any existing output directory.
2. Create the public P triple, precommit Q001 against its legal digest/deadline **before** receiving Q001; decode from only the four public receipts and independently validate.
3. Create exactly one exclusive canonical Snapshot/v2, preserve its absolute path and external SHA; produce and validate closure UNKNOWN, then commit it to an exclusive local file.
4. Start **seven fresh independent subprocesses** in separate child working directories: F00, F10, STATIC-H+, FIXED-MACRO, EPISODIC-EXACT, NEAREST-1NN, STUMP-1. All restore identical Snapshot bytes and receive no synthetic source or expected USE answer.
5. Verify byte hash and canonical trace digest, path, snapshot SHA, input, arm, manifest and claim flags for each child, then write public execution manifest. No scientific score table or ScoreReceipt is produced.

Child failure leaves a partial directory and stops, without silent overwrite or retry. Source remains confined to evaluator-side runner/gateway; no target answer comparison occurs.

## Verification and gates

~~~bash
python -m unittest discover -s tests -p 'test_r2_m_eng_*.py' -v
python scripts/check_docs.py
~~~

Artificial tests: all 16 human-provided laws on all eight points, 16 prebuilt fixed macros, STATIC rederivation and validator charges, EPISODIC full-public and unknown-key behavior, 1NN all-nearest tie and majority, STUMP 14-slot order/first-tie, changed-SHA rejection, closure UNKNOWN forgery rejection, seven different working-directory subprocesses with identical pinned Snapshot, exclusive outputs and absence of private scoring. Existing Stage 1/2 negative and short-circuit tests are preserved.

### Independent reviewer STOP checklist

- [ ] Reproduce synthetic and docs CI on **final exact head**; do not infer PASS until it is observed.
- [ ] Independently verify each comparator capacity/tie and actual cost breakdown, including macro preparation.
- [ ] Verify F00 nonbody routes are neither suppressed nor replaced; audit isolation from evaluator source.
- [ ] Test corrupted/rehashed closure and same Snapshot restore in fresh children with distinct cwd.
- [ ] Confirm no private USE scoring, F01/F11, ORACLE, sealed or historical research artifacts activated.
- [ ] Claude independent acceptance before next gate, separate Owner approval before merge.

Even full engineering acceptance does not authorize a scientific experiment. Scientific source-first preregistration, independent custody and Owner decision remain separate gates.
