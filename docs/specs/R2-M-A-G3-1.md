# R2-M-A G3-1 — contract / separation (synthetic-only code PR)

id: R2-M-A-G3-1-CONTRACT-20261106
status: implemented_candidate / pending_supervisor_acceptance_and_owner_merge / not_scientific_execution
updated: 2026-11-06
tags: r2-m-a, g3-1, synthetic-only, contracts, import-boundary, owner-gate

## Authority and invariants

- [Owner G3 implementation GO](https://github.com/ryonakayama234/DekaSugi/pull/183#issuecomment-6675971478), [Issue #146 update](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6675976148), reviewed [DIAG-R-20261106-10](https://github.com/ryonakayama234/DekaSugi/blob/docs/r2ma-g3-qg1-qg6-plan-20261106/docs/research/DIAG-R-20261106-10-r2ma-g3-plan-response.md), and [R-20261106-11](https://github.com/ryonakayama234/DekaSugi/blob/docs/r2ma-g3-qg1-qg6-plan-20261106/docs/research/R-20261106-11-muse-review.md) are the controlling references. This PR changes **neither** frozen G2 preregistration nor its receipt.
- G2 main \`cf844094fb5907a37bb496760e206f9061deb021\`; prereg raw SHA-256 \`865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68\`. Immutable anchor checks are read-only.
- Public inputs: three free observations 000/100/010, only paid Q001; USE inputs 011/101/110/111. Exactly 16 enumerated F_aff coefficients × four USE points × seven independent arms = **448 planned slots**, but **no execution order** is chosen here. Law identifier is parent-only. \`expected_slot_set()\` returns an unordered set. G5 must later supply a complete, independently authorized ordered manifest; local digest validation alone is insufficient.
- Arm set: F00 / F10 / STATIC-H+ / FIXED-MACRO / EPISODIC-EXACT / NEAREST-1NN / STUMP-1. The five controls do **not** modify F00 fallback routes; F01/F11 and ORACLE-REF cannot be child arms.
- Raw process metrics remain **unmeasured**. SI RSS guard baseline = **512,000,000 bytes**. Any individual child with observed peak RSS in inclusive **512,000,000..536,870,912 bytes** must be reported with raw bytes as **BOUNDARY_REVIEW**, not silently STOP from one interpretation; G4/Owner decide disposition. \`rss_boundary_status\` is a future reporting classifier **not** a live guard. Wall and process CPU caps remain 5 s / child.
- M_use NOT_CERTIFIED; M_gap UNKNOWN; N_rep/U/T NOT_EVALUATED; F01/F11 NOT_EVALUATED; closure UNKNOWN; B NO-GO.

## G3-1 execution and trust boundary

~~~mermaid
flowchart LR
    S["Evaluator-only synthetic known-law source"] --> G["PublicGateway: P3, one paid Q001"]
    G --> C["Local Q001 precommit event (fsync)"]
    C --> E{"Synthetic barrier receipt exact?"}
    E -->|"No"| B["RUN_BLOCK: no paid query"]
    E -->|"Yes, engineering fixture only"| Q["One Q001 answer"]
    Q --> D["decode_public, independent validate_public, Sleep-lite"]
    D --> V["write_snapshot O_EXCL/fsync, verify bytes SHA"]
    V --> T["Parent-only unordered 448 Slot contracts"]
    T --> F["Future G3-2/G3-3, currently RUN BLOCK"]
    V -.-> I["ChildRequest 5-field allowlist only"]
    X["source_gateway / public_pipeline / evaluator_gate"] -.-> Z["Blocked by child import guard"]
    I --> Z
~~~

The \`prepare_synthetic_snapshot\` adapter imports \`source_gateway\` on the **evaluator side only**. It requires an explicit \`engineering_only=True\` and synthetic barrier receipt, and it will not call \`gateway.answer\` if the barrier fails. The barrier confirms only a local engineering fixture; it **does not** attest a GitHub remote commit. Production-grade pre-answer GitHub remote push and readback **remain G3-3**. No G3-1 CLI, production query path, supervisor or scientific evaluator/scorer exists.

The reusable \`r2_m_eng\` records, decoder, independent validator, Sleep-lite and Snapshot/v2 are unchanged. A single newly created canonical immutable Snapshot is verified with an expected raw-bytes SHA before child use. G3-1 code never reads true USE labels or generates scientific scores. Full static and runtime child-edge checking is **partially implemented**: \`audit_static_child_graph\` rejects forbidden reachable imports within an explicit source map; \`install_child_import_guard\` installs **both** \`sys.meta_path\` and an audit \`import\` hook, and checks preloaded forbidden modules before activation. G3-2 must install these hooks at child startup **before** importing dispatch/controls; the exact-head full graph, CLI/env allowlist/taint checks and delayed-import fault injection remain G4 acceptance evidence. A \`sys.modules\` snapshot alone is never treated as runtime monitoring.

### Child contract / isolation prerequisites

A future G3-2 child receives **only** canonical absolute Snapshot path, externally pinned bytes SHA-256, arm, one USE input coordinate, and exclusive trace output path. \`ChildRequest\` / \`verify_child_payload\` reject unknown keys including law ID, truth, seed, score and oracle. Future child argument and environment construction must avoid law or seed tokens in the *contents of allowed path fields* as well; an allowlist of keys alone cannot eliminate covert leakage. A separate working directory and exclusive trace file are still G3-2 requirements.

G3-2 owns fresh-child supervision and raw cost observation: parent monotonic wall clock, wait4 individual process CPU/RSS, 5 s hard caps, process-group kill, child's own process group + parent-death kill (PDEATHSIG equivalent), cgroup v2 fail-closed, SIGXCPU-ignored spinning child negative test, and parent-killed child survivor negative test. Reuse existing \`CATALOG_PREPARATION_*\` values for FIXED-MACRO when G3-2 implements accounting: no simultaneous remeasurement, no subtraction from raw process totals, \`one_off_preparation\` is UNMEASURED unless observed, no r2_m_eng import refactor without separate pre-G4 review. G3-1 has no child launch or meter.

G3-3 owns hash-linked append-only evidence, actual remote precommit confirmation, pre-score manifest digest lock, missingness handling, evaluator gate and audit dossier. G4 actual-path audit, G5 sequence fixation, G6 execution and any B/scientific measurement remain **NOT AUTHORIZED**. This code PR is not evidence of any completed audit, scientific run, or legal measurement.

## Synthetic tests / negative coverage

- \`tests/test_r2_m_a_contracts.py\`: frozen anchor rejection, complete 16×4×7 unordered slot design and duplicate/missing/future-arm rejection, synthetic G5 seam, child payload allowlist and raw RSS boundary classifier.
- \`tests/test_r2_m_a_boundary.py\`: 16 known artificial coefficient cases; P3 → precommit barrier → one Q001 → independent validation → immutable Snapshot, failed/mismatched/absent barrier prevents answer, expiry/duplicate and O_EXCL, source/child static transitive boundary and delayed import hook subprocess smoke.
- Existing \`tests/test_r2_m_eng_*.py\` are regression baseline. Test execution records must distinguish actual CI results from intended coverage. **No 448 child measurement**; no external source; no score.
