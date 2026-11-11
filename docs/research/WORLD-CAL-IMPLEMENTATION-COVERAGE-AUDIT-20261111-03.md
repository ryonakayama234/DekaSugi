# WORLD CAL PR #206 — final-round scope boundary and proof audit (source-only)

id: WORLD-CAL-IMPLEMENTATION-COVERAGE-AUDIT-20261111-03
status: SYNTHETIC_ID_REPRO_EVIDENCE_PASS / K0B_UNKNOWN / K0C_UNKNOWN / CPU_STOP_UNKNOWN / NO_CAL
updated: 2026-11-11
tags: world-cal, implementation-go, synthetic-audit, k0-enumeration, stop-unknown
authority: Existing implementation GO; supervisor progress audit #6797428860. This is Lead self-audit evidence, NOT the supervisor's final PASS.

## 1. Exact public-source coverage, and what it does **not** prove

The pinned WORLD-GEN-SRC-1.0.0 source defines 384 distinct canonical law rows. In each phase, the admissible length set, all 24 permutations of four live roles and all 8 registered word patterns constitute the *entire indexed abstract source*. For each law, the per-phase count is

    c(l, phase) = 24 * 8 * #{L in phase lengths: capacity_admissible(l,L)}

because the only structural exclusion is REPEAT_COPY with L+k>16. Every index has its unique tuple (law,phase,length,permutation_rank,pattern); the source iterator uses exactly these nested loops. It enumerates **draw cells**, not semantically distinct observed buffers. Actual iterator emissions and independent arithmetic count are checked per phase. Their sums must be TRAIN=663,552, CAL=663,552, G1=663,552, G2=239,616. Hierarchical weights p(l)/#{legal lengths}/24/8 sum to exactly 1 in each phase under rational arithmetic. The canonical unordered different-law index pairs are precisely (i,j) with 0<=i<j<384, count C(384,2)=73,536; a streaming order SHA-256 of all 73,536 IDs is recorded by `scripts/audit_world_cal_k0_index.py`. This DOES NOT create any split, tag, secret key, law allocation, sampled demo, instance or target.

**Proof scope:** bijection and mass conservation of registered generator *indices*. The CI artifact is a full census of these indices, NOT a K0-b PASS. For each fixed law pair and fixed episode count t, a complete index of ordered distinct three-demo sets and trial cells avoiding those demos has cardinality

    (c_left)_3 * (c_right)_3 * ((c_left-3)*(c_right-3))^t.

This is a combinatorial description, not an exhausted paired public-history tree. Even ignoring demo enumeration, two TRAIN trials on two laws with 1,728 cells each already have 1,728^4 > 8e12 joint combinations **per law pair**. The exact registered number of TRAIN trials, the demo-path integration, all trial/evaluation paths, and all 2-million-node DP exhaustions have not been proven complete. No claim of law-pair separability over all such paths is warranted. The bounded pair-cell iterator raises STOP_UNKNOWN at its cap. `scan_k0b_pairs` now explicitly rejects an unsubstantiated `complete_support=True`, duplicate/missing law-pair enumeration, or absent demo/TRAIN/EVAL exhaustion receipts. K0-b remains UNKNOWN (not FAIL).

## 2. Typed Space K0-c lower bound and curve completeness

Spec v6 §2 defines the Space by canonical *syntax* (node count<=64, depth<=8, predicate depth<=3, de Bruijn binding). The registered 14 primitive tokens are available. Every `SEQ(ATOM(a1),...,ATOM(a63))` has 64 nodes, depth 2 and predicate depth 0. These programs have distinct canonical strings. Thus, **even this one subclass** of Space contains exactly `14^63 = 1607186396188673214933428422746430966564755954690227345058705914036486144` syntactically distinct members. A 2,000,000-node enumeration cap cannot exhaust Space by literal syntax, and the 24-action episode horizon does not remove these terms from the spec's syntactically defined Space. Even restricting this subclass to 24 actions leaves `14^24 = 3214199700417740936751087616` syntax strings.

This lower bound is an obstruction to a *literal full enumeration*, not a proof that a sound, symbolic equivalence quotient / dynamic-programming proof is impossible. Such a quotient would require an explicit theorem preserving all goals, checkpoints, budget, success absorption, TRAIN/EVAL information and all registered controls; no such theorem or separately reproducible certificate has been supplied. Moreover, `world_cal/space.py::validate` currently checks high-level node kinds/bounds but does not yet implement the complete closed typed grammar (e.g. arbitrary `CONST` literals are accepted), so a claim that its accepted ASTs are exactly the normative finite Space would be false. `exhaustive_k0c_curve` also consumes supplied control curves; there is no independent proof those curves are all seven best curves on the complete abstract support. It now rejects bare boolean `space_complete=True` / `support_complete=True` and demands explicit full-source, typed-Space, and control-curve receipts. No such receipt is asserted here. K0-c remains UNKNOWN, and no saturation conclusion is drawn.

## 3. ID-only synthetic end-to-end reproducibility evidence

`scripts/audit_world_cal_id_only_repro.py` uses 40 literal synthetic label positions in ten synthetic parent groups and synthetic SHA-256-derived *public*, nonsecret fixture tag strings. Each of exactly 999 synthetic label shuffles is derived deterministically from a public domain-separated hash ordering (not a registered CAL PRF draw, not a CAL seed). The same input is passed through registered four-byte-feature extraction, lexicographic five-parent-fold CV, zero-initialized C=1 multinomial logistic fitting, one-versus-rest macro-AUC and 999-permutation null p95. The input digest and binary64 `float.hex` outputs are bound into a canonical JSON result digest.

Each operating-system job launches two *independent interpreters* with distinct PYTHONHASHSEEDs and compares all JSON bytes. GitHub Actions additionally runs on Ubuntu 22.04 and 24.04 (both x86_64, pinned Python 3.12.16, NumPy 2.2.6 and one BLAS thread) and performs an exact cross-environment byte comparison. The artifacts contain the concrete `input_sha256`, output `result_digest`, p95 and observed AUC. Source: [synthetic CI run 43033546871](https://github.com/ryonakayama234/DekaSugi/actions/runs/43033546871). This is a synthetic reproduction audit, not CAL-real tag issuance, not a calibration, and not evidence of absence of tag leakage in future CAL data. ID-only synthetic process/environment reproducibility is independently reproducible from committed code and fixture.

## 4. CPU budget semantics of *the present implementation*

`world_cal/power_engine.py::scan_authorized` would, **only after separate CAL authorization**, iterate n in exact integer ascending order 2..min(N,512), with all three scenarios, 10,000 repetitions each, and 999 bootstraps inside each repetition. It returns the **first** eligible n after *complete* counts in every scenario, satisfying `min_scenario CP99_lower >= .80` and `cost(n,B_final)<=20,000,000`. If no suitable n is found, it returns STOP_UNKNOWN, with n_required=null. The pure `route_from_completed_scan` also returns STOP_UNKNOWN if any earlier n or any complete scenario count is absent; it does not skip gaps to choose a later n. A degenerate repetition (e.g. fewer than two sampled parent clusters, singular variance, insufficient inclusion probability) raises STOP_UNKNOWN instead of being silently discarded.

**Important distinction:** the current `scan_authorized` has *no implemented CPU/wall-clock deadline check*. Its 20,000,000 bound is a *registered primitive-call cost check*, applied to an already completed n; it is not a hardware wall budget. Therefore saying 'wall budget hits X hours and this code automatically returns STOP_UNKNOWN' would be an unfounded claim. If Owner imposes a finite external wall budget under future CAL_AUTHORIZED, interruption before all required counts at n are completed leaves an incomplete scan and therefore STOP_UNKNOWN/no n_required; this requires an audited external guard or future implementation, not an already-tested automatic timeout. The supervisor-checked 1.2939 s per n96 synthetic repetition and worst-case arithmetic ~6,358.9 wall-hours (~265 days) remain unchanged; feasibility is STOP_UNKNOWN. No extra profiler run, speedup, protocol revision or production execution is asserted in this round.

## 5. Final-supervisor gate

- **Demonstrated now:** complete public law/instance index grammar and exact weights, canonical law-pair domain, cap-to-UNKNOWN defenses, and synthetic ID-only process and OS reproducibility.
- **NOT demonstrated:** exhausted registered joint demo/TRAIN/EVAL K0-b support with every coupled history DP; complete typed Space, oracle and all-seven control curves for K0-c; finite production wall feasibility. Those are not silently converted to PASS.
- **Forbidden:** CAL; formal power simulation; K0 production; sealed split; private/evaluation seed; EVAL; algorithm_digest fixing; CAL_AUTHORIZED; FROZEN; EXPERIMENT_GO; merge / ready-for-review.

As such, **this is an implementation evidence resubmission for the portions proven, but NOT a claim of an all-blockers-cleared final implementation**. The supervisor must not treat it as a final PASS request until the missing completeness proofs exist.
