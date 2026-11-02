# EXP-REP-005 G0b-A — executable source-only engineering census (2026-11-03)

id: EXP-REP-005-G0B-A-SYNTHETIC-20261103
status: engineering_pass_full_hplus_census_stop_no_science
updated: 2026-11-03
tags: experiment, synthetic, engineering, causal-world, stop, source-only

## Evidence and provenance
- Parent method: [V3.1](../../../docs/specs/EXP-REP-005-G0B-DECISION-V3.md); [Issue #148](https://github.com/ryonakayama234/DekaSugi/issues/148); [Draft PR #149](https://github.com/ryonakayama234/DekaSugi/pull/149).
- Exact tested code+tests PR head: 364d7d62aa5ea7f892f3940140a6dea83433bce4; [dedicated workflow run 41468327655](https://github.com/ryonakayama234/DekaSugi/actions/runs/41468327655), test job 125354979463, Python 3.12; **13 tests, PASS in 7.173 seconds**. Source code and tests were executed on GitHub-hosted synthetic-only CI, not on a research evaluator. Earlier [run 41468008510](https://github.com/ryonakayama234/DekaSugi/actions/runs/41468008510) confirmed initial 8-fixture engineering smoke before the grammar and provenance additions.
- Command: python -m unittest discover -s tests -p 'test_rep005_g0b_synthetic.py' -v ; then python -m packages.rep005_g0b --output .run/EXP-REP-005-G0B-pilot.json . The dedicated workflow uploads source-only artifact REP005-G0b-source-only-pilot; no sealed evidence read.
- Existing v2 pinned historic source and docs verification on the tested head: [run 41468327487](https://github.com/ryonakayama234/DekaSugi/actions/runs/41468327487) SUCCESS. Prior sealed raw source, scored data and main remain unchanged.

## Actual observed synthetic measurements (not scientific world transfer)
| Metric | Result | Definition |
|---|---:|---|
| disclosed fixture laws | 8 | hand-chosen source-only deterministic examples |
| full typed cells PER law | 30,144 | 16 visible states x 157 histories x 12 legal actions |
| full semantic distinct signatures | 8 | byte equality, not only hashes |
| typed role-orbit keys among fixtures | 8 | role permutations over four objects; not generator-independent families |
| independently validated full-domain transitions | 241,152 | 8 x 30,144 verified against second independently coded list-of-bits reference |
| object-role permutations | 24 | complete S4 object permutations tested for equivariance |
| syntactic normal-form Boolean literals | 32 | 8 current bit, 16 prior set, 8 prior pulse |
| valid two-literal guard pairs | 360 | exclusion of same-bit and same-time contradictory previous-action pairs |
| guard options per Edge | 393 | TRUE + 32 literals + 360 pairs |
| syntactic Edge candidates | 14,148 | 4 sources x 3 other targets x 3 lags x 393 guards |
| syntactic Law candidates (0/1/2 Edge) | 100,090,027 | 1 + 14,148 + C(14,148,2), NOT independent families |
| source-only raw grammar census cap | 200,000 | prior V3.1 method, cannot exhaust 100M |
| full-Hplus_G semantic census | NOT_CERTIFIED | not attempted beyond safe cap |
| structurally independent causal families | NOT_CERTIFIED | no complete ancestry/provenance independent review |
| M0/M1 x ID/UNID population | NOT_CERTIFIED | incomplete finite class universe |
| M2/M3 stress cohorts | NOT_CONSTRUCTED | require independent later work |
| statistical power / family-level split | NOT_ESTIMATED | no independent family universe |
| paid TRAIN, learner Snapshot, DEV/FINAL score | NOT_RUN | zero new scored research observations |

## Witness properties / exact reproducible controls
- ID: the closed two-law class (null law vs direct pulse0->bit1) is identifiable with B=1; exhaustive adaptive search emits a feasible decision tree.
- UNID: the closed two-law class (null law vs lag1 pulse0->bit1) has no legal B=1 distinguishing tree; with B=2 it becomes ID. This is a **candidate-class-relative budget** verdict, not an inherent world label.
- NOT_CERTIFIED: node cap 0 returns NOT_CERTIFIED rather than false UNID; duplicate semantic laws are rejected before closed-class reasoning.
- Universal memoryless refutation: a legal pair of different reset-from-zero prefixes reaches identical public state and action with conflicting successors under the lag1 law. This refutes H0_all for that law; it is not a complete finite H0_G membership test.
- Positive **feasible action opportunity**: under a uniform two-law prior and terminal-MAP identification utility, the legal pulse0 policy achieves 1.0 vs repeated fixed set(0,0) 0.5 with one paid action; the actual public policy tree is recorded source-only. This is a constructed baseline opportunity, **not** learner achievement and not a fair learning-control superiority result.
- No-opportunity and proof-limit cases are separately tested. The family split audit rejects supplied shared ancestor IDs, semantic aliases and role-orbits across TRAIN/DEV/EVAL; it cannot infer omitted ancestors. Public-step projection emits no source-law or ancestry fields. Python-level projection is NOT a security boundary against a learner with import access.

## Decision, limitations and next action
Engineering **PASS for the eight invented fixture laws and proof mechanics**. G0b full-family universe **STOP / NOT_CERTIFIED**: 100,090,027 syntactic candidates exceed the 200,000 direct-census cap. This calculation does not establish an 80-family impossibility upper bound, nor prove the full grammar has any given number of meaningful independent families. Do not inflate eight role orbits into eight independent families, change sample quota, run paid TRAIN, or reuse existing FINAL.

Next scientific-method decision requires an independent, small constructive mechanism grammar with a tractable canonical semantic census or independently sound structural compression, and source ancestry confirmed separately. Under the present code, 80-family preregistration, G1–G6 and learned novelty claims are blocked. [Module](../../../packages/rep005_g0b/__init__.py) / [tests](../../../tests/test_rep005_g0b_synthetic.py) / [ARCH-001](../../../docs/architecture/system.md) / [ARCH-002](../../../docs/architecture/contracts.md).
