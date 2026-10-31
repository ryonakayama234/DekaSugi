# EXP-COEV-001 F0-A — structural feasibility preview receipt

id: EXP-COEV-001-F0A-SYNTHETIC
status: DESIGN_ONLY; invented_public_seed; NOT_FROZEN; NOT_SCORED
updated: 2026-10-31
tags: pool-preview, provenance, sample-size, source-integrity

## Source and qualification
Run `packages/concept_preflight.synthetic_pool_preview()` on approved G1 semantic catalog, with a FIXED PUBLIC salt `SYNTHETIC-ONLY-F0-PREVIEW-20261031`. This is a throwaway design fixture, deliberately **cannot** accept a private seed, does not generate scored targets and must never be promoted as TRAIN/DEV/FINAL source. PR base is G1 Draft #108, not dependent on PR3 engineering TRAIN.

## Unscored structural finding
- 895 total distinct finite-domain classes, 29 plain and 866 conditional representatives. Proposed preview 40% TRAIN, 20% DEV, remainder FINAL **within each stratum**.
- TRAIN **358** classes: plain 12, conditional 346.
- DEV **179** classes: plain 6, conditional 173.
- FINAL **358** classes: plain 11, conditional 347.
- All 895 class IDs are present exactly once, no TRAIN/DEV/FINAL semantic-class overlap under the preview.
- 2048 hypothetical IID-with-replacement FINAL task draws from 358 equally weighted held-out classes imply expected unique classes `358*(1-(357/358)^2048)`, **about 356.8**, and **about 1691 repeated class draws**; independent *task sessions* are NOT independently new function meanings.
- Proposed two-sided 95% Hoeffding half-width for bounded paired task differences [-1,1]: `sqrt(2*ln(40)/2048)` about **0.060**. This is only arithmetic under conditional-IID; not proof of IID, power, cost feasibility or a real H1 effect.

## Negative tests and exclusions
Five synthetic regression tests in PR verify counts, exact disjointness, deterministic preview identity, same-digest forged class assignment rejected, invalid private/custom salt rejected and malformed Catalog rejected. Local isolated prototype ran 5/5; GitHub exact-head CI and reviewer are required for PR source. No official target identities, labels, frozen source roots, authenticated Oracle, genuine TRAIN, DEV or FINAL scores were generated.

## Remaining mandatory F0 gates
A future different, secret-rooted and independently owned class allocation and audit protocol must be reviewed/frozen **before** new registered TRAIN. Verify conditional and semantic-family opportunity, effective sample independence, target-specific costs, actual Oracle isolation/approval, source commitments, strict statistical and resource controls. F0-A cannot satisfy independent custody or grant a scorer activation by itself.

[Parent F0 #110](https://github.com/ryonakayama234/DekaSugi/issues/110) / [subissue #111](https://github.com/ryonakayama234/DekaSugi/issues/111) / [study #106](https://github.com/ryonakayama234/DekaSugi/issues/106).

## Source correction following independent P2 (2026-10-31)
Original preview API accepted a tuple subclass capable of overriding iteration while preserving equality and claimed commitment. Corrected source requires exact built-in tuple/int types, validates all fields and computes statistics from a reconstructed canonical preview. Adds sixth invented-only negative unittest for same-digest tuple-subclass forged iterator. Original 5/5 local record remains historical; new GitHub exact-head CI/review must confirm the corrected version. No real source/secret or H1 results.
