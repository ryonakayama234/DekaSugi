# G0B — exact synthetic local execution, public-opportunity-zero STOP

id: EXP-ACTIVE-002-G0B-RUN-20261103
status: LOCAL_5_OF_5_PASS; SYNTHETIC_ENGINEERING; RESEARCH_STOP; PR_CI_PENDING
updated: 2026-11-03
tags: run, negative-result, independent-reference, exact-integer

## Setup / immutable data
- Date UTC: 2026-11-03. Linux, CPython 3.13.5. Main base `d9ad80fc844a09c312f6434d20d0d17fdcac4109`; source-only G0B branch documented in [Issue #166](https://github.com/ryonakayama234/DekaSugi/issues/166).
- Exact source.py Git blob `4d1c90f0d44398e66159bab44c20659990ce30e7`; oracle.py Git blob `81170e0922e6e0977ea63a77bb5c99cbfd009d19`. The local analysis source used the same JSON semantics as the committed module; report digest checked by a second fresh local run.
- `python -m unittest discover -s tests -p test_inquiry_landscape.py -v`: 5 test methods PASS, ~0.8s on local CPU. The independent reference directly enumerates all terminal prediction label choices/abstain and every depth-two adaptive policy; 512/512 individual world Oracle comparisons and EXT448 public mixture matched.
- `python -m packages.inquiry_landscape --output second_census.json`: deterministic 88,825-byte canonical UTF-8 JSON; SHA256 `fdb1d686e6aa918c5751df7a51f6a277a2bff51057dfdb1dde1b8b471631a3d8`. This hash records reproducibility, not independent custody. CLI creates a fresh file exclusively.

## Complete census (no replacement)
| Partition | Indexed worlds | Exact fixed-label semantic signatures | World-aware gain >0 | World-aware gain =0 | Public adaptive utility | Public best fixed utility | Public gain |
|---|---:|---:|---:|---:|---:|---:|---:|
| CAL64 disclosed | 64 | 64 | 2 | 62 | 304/768 | 304/768 | 0 |
| EXT448 designed census | 448 | 448 | 25 | 423 | **1040/5376** | **1040/5376** | **0** |

- Each of the 25 positive EXT448 worlds has world-aware `12/12` vs `8/12` = `+4/12`. Sum of **world-aware** gain over the 448 indexed worlds is `100/5376`, a counterfactual world-informed ceiling; this number is **not** a public adaptive gain or learned result.
- For EXT448, the best **precommitted** schedule is q1 then q2 (zero-index `[1,2]`). Public-optimal root-conditional extra gain is `[0,0,0]`; no strictly beneficial second-action switch under the public prior.
- Per-world exact signatures reflect fixed labeled actions/latent audit semantics, not semantic orbits under role permutation nor independently sampled causal families. No statistical n=448 natural-population interpretation.

## Interpretation and research decision
World-aware positives confirm that the closed-class source contains constructed questions where branch-sensitive policies are strictly better. Yet when source identity is unknown and only the grammar/prior is public, both adaptive and optimal fixed plans achieve the same utility. The learner has **no strict publicly usable adaptive advantage in this source mixture**, even with full knowledge of the generating distribution.

This explicitly satisfies `STOP_G0B_PUBLIC_OPPORTUNITY_ZERO` from the approved G0B decision. Do **not** construct G1, silently retune the grammar, exclude zero worlds, modify the source posthoc or run historical sealed evaluation. If a new asymmetrical source or another objective is proposed, it must have a **new research ID**, separate method and outcome record, independent review and owner decision.

## Scientific cautions
- The low-index CAL64 slice is newly declared as the disclosed comparator. It is **not proven** to reproduce the previous conversational 64-structure example; the prior +1/48 statement is not reproduced by this versioned source and must be treated as unverified.
- This is exact for a designed finite distribution under a model that knows the public grammar. It is not a negative theorem about inquiry in nature, not evidence of learner failure, and not a scored artificial or real TRAIN/DEV/FINAL.
- No independently custodied split, independent mechanism family sample, preregistered scientific power, method review, or cryptographic truth authentication.
- The GitHub PR head and safe CI outcome, any new tests and independent review are separate gates. A local PASS must not be relabeled exact-head review approval.

[Spec](../../../docs/specs/EXP-ACTIVE-002-G0B.md) / [plan](../plan.md) / [run index](README.md).
