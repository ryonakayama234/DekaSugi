# ACTIVE-001 P2 — synthetic-only CPU and memory resource preflight

id: ACTIVE-001-P2-RESOURCE-BUDGET
status: engineering_measurement_proposal; NOT_FREEZE_NOT_SCORED
updated: 2026-10-31
tags: active-learning, cpu, performance, no-scoring, measurement

## Task, bounds and interpretation

Measure engineering execution cost **before** locking source, official split and target list. The subject is the existing fixed finite-world public context, NOT a target accuracy trial. Benchmark seed 20261030 is an **invented fixture**. The existing #97 study is one proposed task sampling law (878 semantic classes × 378 public pairs; with replacement). This P2 instrument neither draws those target trials nor accesses auditor-only labels. Source-only and old workflow locks remain untouched.

## Measurement phases

- Fresh \`build_catalog()\` (true recomputation, NOT a cache), followed by cached catalog mapping lookup (warm lookup, NOT a second fresh build).
- Session start, first-query partition + validation, B2 argmax choice, B1 seeded choice.
- Fabricated consistent **allowed query input** answer, \`update()\`, full-prefix session validation and final representative. No independent Oracle or hidden target ID.
- 64 program executions on **allowed query inputs**, measured only as a CPU execution proxy for future 64-item prediction sweeps. No evaluator-only input truth, no correctness or heldout accuracy.
- Exactly one existing non-scored Gate F F0–F3 public-context census, preserving its checksum; F4 remains full-census \`NOT_COMPUTED\`. Tiny F4 toy timing is not a whole-population F4 estimate.
- Linux \`resource.getrusage(RUSAGE_SELF).ru_maxrss\` before and after is **cumulative process peak KiB**, not phase peak, current RSS or hypothetical future memory consumption.
- Multiple repeated phase samples using \`time.process_time_ns\` (process CPU) and \`time.perf_counter_ns\` (wall time); store every ns sample, median, max. OS scheduling, cache, runner noise, CPU frequency and cold/warm contamination require caution. The future scorer machine/runtime is not fixed.

## Exact prospective workload counts (not executed)

| Independent task draws | Draft 7 arms: episodes / maximum queries / 64-step predictions | Future 12 arms: episodes / maximum queries / 64-step predictions |
|---:|---|---|
| 512 | 3,584 / 6,144 / 229,376 | 6,144 / 11,264 / 393,216 |
| 1,024 | 7,168 / 12,288 / 458,752 | 12,288 / 22,528 / 786,432 |
| 4,096 | 28,672 / 49,152 / 1,835,008 | 49,152 / 90,112 / 3,145,728 |

7 arms = B0 ×1, B1 ×5, B2 ×1. 12 arms adds B1+ ×5 **on an independent PR**, not currently measured. Query figures are hard *count maxima* given two questions per active arm; early stops reduce actual calls. Prediction figures count all 64 per arm and are a planned full sweep, not observed label evaluations or CPU timings. **A model class is not a primitive execution.**

## Engineering extrapolation

Define \`E\` episodes, \`Q\` maximum successful query calls, and \`t_X\` measured invented median process-CPU nanoseconds for a named phase. Scenario estimate:

\`T_cpu ≈ t_catalog + t_gateF + E*(t_start+t_finalReplay+t_64Predictions) + Q*(t_B2choice+t_syntheticUpdate)\`.

It uses B2 selection+update timing as a **proxy for ALL query policies**, even though actual B1 and B1+ may be slower/faster. This is neither a strict worst-case CPU upper bound nor wall-clock/peak RSS, omits full official evaluator orchestration/receipt I/O/OS variance, and does NOT account for full F4 census. It should *never* automatically trigger a new official 4096-task sample. P2 result should be tagged **PROVISIONAL_CPU_ESTIMATE**. An independent resource ceiling for real runs must be set and checked separately before source/seed freeze. If projected spending exceeds the future ceiling, change method **before** scoring; do not retroactively reduce sample size after outcomes are observed.

## Safety, acceptance and next scientific gates

CI may run **only** the newly explicit \`test_active_cost_preflight.py\` through \`scripts/run_research_ci_v2_tests.py\`; the pinned successor workflow remains byte-identical and original \`docs-check.yml\` must remain disabled. The CI receipt is an actual engineering-run *machine-dependent* timestamp, not a scored scientific observation. Source/seed/Oracle and evaluator isolation gates remain pending in #96; full F4 feasibility is a separate expensive computation requiring a credible resource ceiling; statistical adequacy is #99/P3. Before adoption, check exact-head safe CI, documentation links, Codex review and raw receipt.

[Module](../../packages/active_cost/__init__.py) / [Tests](../../tests/test_active_cost_preflight.py) / [Engineering receipt](runs/20261031-p2-invented-cpu.md) / [Issue #99](https://github.com/ryonakayama234/DekaSugi/issues/99).
