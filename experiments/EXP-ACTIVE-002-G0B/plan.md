# EXP-ACTIVE-002-G0B — Finite source-only dual opportunity census

id: EXP-ACTIVE-002-G0B-PLAN
status: stopped_after_synthetic_source_census; no_F0_authority
updated: 2026-11-03
tags: experiment, exact, negative-result, preregistration-limit

## Hypothesis
World-aware conditional questions can be beneficial while the optimal question procedure under a mixture of unknown world structures may have no such benefit. The discriminating test compares two exact and separately scoped Oracle comparisons, all using the SAME independent terminal future-prediction utility. If publicly available opportunity equals zero, **STOP before G1**; if positive, further method/security review would still precede a learner.

This plan documents the owner's approved design and subsequent **disclosed engineering** run. It was not locked by an independent custodian before the first synthetic computation. Therefore the result is not one-shot confirmatory evidence or an independently powered source-family prevalence estimate.

## Source and protocol
The complete source, audit, prior, partition and costs are fixed *for reproduction* by [spec](../../docs/specs/EXP-ACTIVE-002-G0B.md). Three eight-choice Boolean grammar rows; 512 total worlds. First 64 all-low-index entries are labeled prior-disclosed calibration, 448 other entries census. Each world has four equiprobable hidden bits. Audit on unreachable legal state 2; same law, fixed q0/q1/q2; B2, all actions legal. No corpus, historical DEV/FINAL, real public paid TRAIN, source-family samples or model-generated DREAM data.

## Arms / controls
1. WORLD_KNOWN adaptive vs every WORLD_KNOWN fixed length 0..2 schedule (counterfactual ceiling).
2. PUBLIC_MIXTURE adaptive vs every PUBLIC_MIXTURE fixed length 0..2 schedule (G0B *decision* gate). Public Oracle sees the source distribution, **never** the selected world identity.
3. Independent brute-force reference enumerating all terminal prediction choices (+1/-1/0) and every two-stage contingent question policy, and every 0..2 fixed schedule.
4. CAL64 disclosed slice reported separately, never used as a prospective confirmation sample.

## Metrics
- Exact signed utility: `U=(correct-wrong)/3`, abstention 0, averaged over a uniform prior on the hypotheses; no precision roundoff.
- `Delta_world`, `Delta_public`, exact numerator/denominator, positive-world count, NULL count, complete source index denominator, source semantic signature count, full policy/tree, and deterministic raw-receipt SHA.
- Status distinguish `SYNTHETIC_ENGINEERING`, `CERTIFIED_CLOSED_CLASS`, `STOP_G0B_PUBLIC_OPPORTUNITY_ZERO`, `NOT_RUN`, `INVALID`, `NOT_CERTIFIED`. No confidence intervals on this fully enumerated constructed distribution, no independence or natural-prevalence claims.
- Total 13 nonadaptive schedules including stop, plus all two-question adaptive policies and optional early stop. All question probes stay in states 0/1, and heldout probes only at unreachable state 2.

## Acceptance
- [x] Versioned finite source, all 512 grammar entries enumerated; 64+448 partition explicit.
- [x] World-known and public-mixture exact Oracle; full strongest fixed baseline.
- [x] Independent local brute reference for all 512 individual worlds and EXT448 public mixture; five unittest methods PASS locally.
- [x] Negative result and STOP, no post-result source tuning or G1.
- [x] Dated append-only local run with raw canonical JSON SHA256, source/test blob identity.
- [ ] Exact-head GitHub safe CI and independent latest-head method/security review, same-PR docs/AGENTS/INDEX/ARCH synchronization. These are repository-integrity gates, NOT permission to proceed with G1.
- [ ] Owner conversation for next **new** hypothesis/distribution (or formal end of research branch).

## Reproduction
```bash
python -m unittest discover -s tests -p test_inquiry_landscape.py -v
python -m packages.inquiry_landscape --output .run/g0b-census-UNIQUE.json
python scripts/check_docs.py
python scripts/check_research_ci_v2.py
```
The `--output` command refuses overwrite. The safe CI test allowlist must include only the focused test file, never broad suite discovery. The raw JSON is evaluator-private detailed evidence, **not** learner input. Exact SHA expected: `fdb1d686e6aa918c5751df7a51f6a277a2bff51057dfdb1dde1b8b471631a3d8` when run with the reviewed source bytes.

## STOP and authority
A strict positive world-known opportunity in 25/448 does not rescue `Delta_public = 0/5376`. STOP. No source retuning, G1 learner, TRAIN, DEV, FINAL or skill adoption. No main merge without independent latest-head review and original-workflow safety verification. [Issue #166](https://github.com/ryonakayama234/DekaSugi/issues/166).
