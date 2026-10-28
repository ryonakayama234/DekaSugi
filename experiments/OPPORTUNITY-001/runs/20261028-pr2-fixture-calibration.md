# OPPORTUNITY-001 PR2 — synthetic fixture logic calibration evidence, 2026-10-28

id: OPPORTUNITY-001-PR2-CALIBRATION-20261028
status: completed_engineering_calibration_only; not_scientific_result
updated: 2026-10-28
tags: opportunity, fixture, calibration, ci, independent-review, no-holdout

## Exact tested source / controls
- PR: [#59](https://github.com/ryonakayama234/DekaSugi/pull/59) (Issue [#58](https://github.com/ryonakayama234/DekaSugi/issues/58)).
- Code head tested: `c13daf7545992678d256d7d238852f63a15e9f15`.
- GitHub Actions: [verify run #40620036592](https://github.com/ryonakayama234/DekaSugi/actions/runs/40620036592), job [#122591571474](https://github.com/ryonakayama234/DekaSugi/actions/runs/40620036592/job/122591571474), conclusion **success** (docs gate and full Python unittest suite).
- Independent [Codex PR review](https://github.com/ryonakayama234/DekaSugi/pull/59): **completed**, exact above head, `has_any_findings=false`, `has_unresolved_findings=false`. This is an independent code review, not independent verification of real experiment artifacts.
- Synthetic module: `packages/evaluation/opportunity.py`; adversarial test suite: `tests/test_opportunity_fixture.py`. Test invocation was the repository's existing full CI unit-test step; PR-scoped code produced no TRAIN/DEV/FINAL trial.
- Code-level output contracts tested include both-correct excess calls, one-correct missed/lost success, neither-correct null regret, missing vs non_comparable, forbidden hidden fields, false-solved hard-stop, bad types and duplicated IDs.
- No external task manifest, original audit bytes, CPU benchmarks or scientific confidence intervals exist for this PR2 fixture reducer.

## Recorded outcome and bounds
- **Engineering conclusion**: logical classification, strict schemas and aggregate-only reducer passed repo CI and exact-head independent review.
- **Scientific conclusion**: `not_run`. New study TRAIN/DEV/FINAL evaluations **0**. This PR does NOT prove actionability, learning, independent audit validity, origin hash authenticity, expressive power or out-of-distribution transfer. The new proposed dataset/seed/metric thresholds are not yet frozen.
- The old EXP-0003A DEV64 was not rescored and FINAL128 was not opened. The pinned EXP-0003A source and freeze remain untouched.
- The fixture's before-trial boolean and caller-supplied source_lock are **unverified declarations**. Future actual-evidence adapter must verify chronology and original bytes independently.

## Future stage
Separate reviewed method-freeze and real-evidence adapter; tests must retain hard rejection of real task IDs/phase in `opportunity-fixture-v1`. If source provenance, experimental separability or audit independence cannot be established, halt before any fresh holdout.

Related: [plan](../plan.md) / [spec](../../../docs/specs/OPPORTUNITY-001.md) / [run index](README.md).
