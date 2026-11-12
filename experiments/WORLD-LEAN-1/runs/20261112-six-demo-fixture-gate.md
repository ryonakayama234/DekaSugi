# WORLD-LEAN-1 / six-demo artificial TRAIN fixture gate — 2026-11-12

id: WORLD-LEAN-1-SIX-DEMO-FIXTURE-GATE-20261112
updated: 2026-11-12
tags: world, fixture, engineering-evidence, six-demo
status: ARTIFICIAL_FIXTURE_PASSED_IN_CI / SUPERVISOR_DIFF_REVIEW_PENDING
formal_seed: NOT_CREATED
formal_holdout: NOT_MATERIALIZED
formal_evaluation: NOT_RUN

This is a **new -02 record**, not an edit to the old [four-demo receipt](20261112-fixture-gate.md). It is bound to [design -02](../../../docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-02.md), [order -02](../../../docs/research/WORLD-LEAN-1-ORDER-FREEZE-20261112-02.md) and [source lock -02](../../../docs/research/WORLD-LEAN-1-SOURCE-LOCK-20261112-02.json).

## Scope and reproducibility

- Four original artificial TRAIN-only fixture stream labels, TRAIN24 recipes in each stream, six specification pairs per recipe (T,T,T,F,F,F, unlabeled) and balanced two queries. The sample sequence is fixed by the named stream, not repeatedly redrawn to improve ambiguity.
- Ambiguity is present if recipes matching **all six** public demos disagree on a query final state. The threshold remains 10%, and ambiguous queries are not excluded.
- The historical four-demo audit was 3/48, 7/48, 2/48, 6/48 = 18/192. It is **not** an estimate of six-demo performance.

## Evidence state

- Six-demo design transition ceiling: **252,928,000**, versus 185,688,064 in -01. The 48h wall / 36h CPU / 2GiB saved-bytes caps remain unchanged.
- Expected commands: `python -m unittest tests.test_world_lean_fixture -v`; `python scripts/verify_world_lean_freeze.py`; `python -m world_lean_evaluator fixture-gate --output /tmp/world-lean-artificial-evidence.json`.
- Added two negative regression tests: old four-demo TRAIN payload and four-demo inference must be rejected. Old historical files are not modified.
- **Six-demo TRAIN-only early audit (actual CI)**: A **0/48**, B **2/48**, C **2/48**, D **0/48**; combined **4/192 = 2.083333...%**, below the unchanged 10% threshold. Demo-nonunique recipe counts A=0, B=3, C=5, D=1 (do not confuse them with ambiguous query counts). No ambiguous case was excluded or redrawn.
- **Comparison caution**: the former four-demo artificial audit was 18/192 = 9.375%, but the six-demo fixture uses changed per-item counterstream indices: its T/F query inputs are at positions 6/7 instead of 4/5. These figures are **not a strictly paired same-query causal comparison**; the six-demo absolute ambiguity audit is the eligible engineering result.
- **25/25 tests PASS** on CPython **3.12.12** Ubuntu **24.04**; six-demo legacy-payload rejection tests, source-only subprocess boundary and formal-call fail-closed checks PASS. [Exact-run artificial CI](https://github.com/ryonakayama234/DekaSugi/actions/runs/43243785571); [safe research verification CI](https://github.com/ryonakayama234/DekaSugi/actions/runs/43243785525) PASS.
- **New source lock PASS** for 12 files, combined SHA-256 `aceeae29d1bd443403495973212db50ae718a9cd17dc2646aea69fbe789b4480`; manifest SHA-256 `6918f91a28b467fb7f8e6c870008e41997fc49e695cfb33550cb16cfb1aa799d`. Legacy -01 source digest remains `ee1ae0b144a0b1deb76034fc23465c9b76828719e98b8dcccd33b40674e4a147`.
- **Artifact**: `world-lean-six-demo-train-only`, GitHub Actions artifact ID **13954519749**, [run link](https://github.com/ryonakayama234/DekaSugi/actions/runs/43243785571), fixture evidence schema `WORLD-LEAN-1/ARTIFICIAL-FIXTURE-GATE/2`, deterministic digest `e9cd69b5c438b496bc9fd0e0688c7010aee9a134b6a9e9ff0b8ef2944d6e6c0c`.
- **Bench (CI)**: 100,000 primitive transitions at **364,063.12/s**, sample 64-event update 0.023726s, projection **1.296 CPU hours** under the existing rough twofold-transition + example-query overhead proxy (both 36h CPU and 48h wall proxy checks true). This is **not** an exhaustive worst-case 16-seed runtime guarantee; especially 512-trace LOOKUP distance work, I/O, larger learned libraries and scheduling can increase CPU cost.
- **STATIC-RANK invented fixture reachability**: local insert, local delete, copy and conditional each found at ordinal 1 among verified candidates; checked candidate counts **128/64/8/16** respectively, all within 128. This does not establish holdout strength or scientific performance.
- The PR workflow uploads the TRAIN-only evidence JSON as `world-lean-six-demo-train-only`. Formal generation and scoring entry points remain fail-closed.
- A failure remains a failure; do not silently change the ordering, thresholds, arms, seed count or cap to force passage.

Supervisor diff review and separate Owner adoption precede another explicit evaluation GO. This receipt and successful fixture CI (if achieved) are not authorization to generate formal seeds, materialize holdout, run an official experiment or merge.
