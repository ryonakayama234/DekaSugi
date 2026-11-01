# G1-D exact-head P1 repair and repeat measurement
id: EXP-REP-001-G1D-P1-20261101
status: DISCLOSED_ENGINEERING_CI_PASS; FORMAL_UNEXECUTED; INDEPENDENT_REVIEW_PENDING
updated: 2026-11-01
tags: experiment, review, synthetic, reproducibility
source_commit: a440b27bb25bb6be64d82fef7bab977e50fd1263
ci: https://github.com/ryonakayama234/DekaSugi/actions/runs/41313876335

## Code repair and test evidence
Three P1 findings from review on 719439f were repaired: shared B3 template+H2 remaining pair budget, exact nested atom_rank tuple validation, and exact object IDs validation before comparison. Three new adversarial tests are explicitly allowlisted. CI synthetic/source/docs checks succeeded; **146 tests passed**. No old sealed DEV/FINAL was scored. The independent current-head review has not yet signed off.

## New measured G1-D disclosed pilot values
- TRAIN 32 worlds, same fork topology under rename; snapshot 783fb01764e7ea5e4dd3055eaaa7c3a2dd304e613495f0035fcbea6caaca4858; TRAIN idempotence true.
- Correct per 384 audit transitions, same disclosed worlds: {"B0":112,"B1":368,"B2":368,"B3":368,"B3x":368,"B4":0,"B5":384}.
- Candidate checks in last curve point: {"B0":366,"B1":7446,"B2":7446,"B3":414,"B3x":7446,"B4":0,"B5":3978}.
- Inference CPU ns last curve: {"B0":6805706,"B1":11706986,"B2":12074521,"B3":8437692,"B3x":12064774,"B4":291728130,"B5":10813888}.
- Total pilot CPU ms: 9096.397. One CI runner; not a general latency or total cost claim.

## Interpretation
B1=B2=B3=B3x remains in accuracy; no body-specific accuracy improvement. B5 uses different paid active evidence and its improvement cannot be attributed to concept body. B3 candidate savings relative to the implemented fixed exhaustive comparator remain on the disclosed fork. New P1 tests show consumption accounting on targeted cases; this is not independent proof that all possible budget paths are sound. This dated receipt supersedes the code-integrity status of the earlier source but DOES NOT alter or overwrite its historical measurements. No formal GENERALIZATION, DEV or FINAL.
