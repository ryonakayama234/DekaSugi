# EXP-0002B — preregistration provenance record

id: EXP-0002B-PREREG-001
status: preregistered protocol v1; implementation and evaluation NOT STARTED
updated: 2026-10-24
tags: preregistration, immutable-method, versioning, provenance, no-results

## Goal

Complete an auditable **pre-implementation** methodological freeze for learning whether an EXP-0002 skill is beneficial for a task. The user-facing design remains exploratory until the new independent dataset and policy are implemented and tested.

## Freeze sequence

1. Preregistration plan first fixed in commit `17151ccc33d20c30f94d5071a5f586dd9f23e143` on `exp/0002b-preregistration-v1` before any EXP-0002B policy code or new test-dataset generator.
2. Metadata headings were normalized for `scripts/check_docs.py` in `6f9ac64f63f7bc192d7da920730fcd19d06fb62b`, **without changing any algorithm, generator, thresholds or samples**. The latter commit is the plan-content reference for implementation.
3. Afterwards synchronize [experiment spec](../../docs/specs/EXP-0002B.md), [system diagram](../../docs/architecture/system.md), [data contracts](../../docs/architecture/contracts.md), [agent rules](../../AGENTS.md), and [index](../../docs/INDEX.md). None of those documents replaces the plan as the method's source of truth.

## Study definition

- TRAIN 144, DEV 48, FINAL 112 task instances; six known transformation families and one final-only unsupported OOD family.
- Paired off/on TRAIN observations; eight **pre-solve** TaskSpec features; deterministic five-nearest-neighbours cost-sensitive policy; confidence/coverage abstention to OFF.
- Independent third example excluded from TaskSpec and feature extraction. Exact partition-specific token RNG and whitespace patterns pre-specified.
- Primary gate: no audit correctness regression, and > =5% reductions of both candidate count and executed primitive calls versus BOTH Always-OFF and Always-ON on fresh final tasks. OOD and tail-regression gates separate.
- Policy inference costs and training overhead explicitly reported separately from primitive counts; no blanket CPU-time improvement claim.

## Current evidence

| Artifact | State |
|---|---|
| Dataset generation program | not implemented |
| Fresh split files and source/hash | not generated |
| TaskFeatures implementation | not implemented |
| PolicySnapshot / training | not implemented |
| FINAL 112 task experiment output | **no run, no results** |
| Independent code/research review | pending |
| Existing EXP-0002 published holdout | prior diagnostic only; not eligible |

## Integrity / future work

A protocol-changing modification after outcome inspection is not allowed under v1. Start v2 with new untouched FINAL seed and preserve this document and earlier outcomes rather than overwriting them. PR #6 is awaiting review for its skill registry safety fixes; PR #9 metering and PR #8 design are also unmerged dependencies. Do not auto-merge or promote skills/policies on a document-only preregistration.

[Preregistered experiment plan](plan.md) / [Issue #7](https://github.com/ryonakayama234/DekaSugi/issues/7) / [Architecture](../../docs/architecture/system.md).
