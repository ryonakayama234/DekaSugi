# EXP-REP-005-G0C3 — first exact-source CI engineering measurement

id: EXP-REP-005-G0C3-CI-20261103
status: SOURCE_ENGINEERING_CI_PASS_SCIENTIFIC_STOP
updated: 2026-11-03
tags: source-only, engineering, negative-result, provenance

## Exact evidence origin

- Scope: disclosed **synthetic P-NAT** generator CFAM-V1 on stacked [Draft PR #161](https://github.com/ryonakayama234/DekaSugi/pull/161), [Issue #160](https://github.com/ryonakayama234/DekaSugi/issues/160).
- Evaluated code commit: `4ceafe4b4b5273aba5c8b519bb702f3695ce0ce9`, parent dependency on unmerged PR #159 original source `afed85765f0b419bd617635fe8bf85422d7bf513`.
- [G0C-3 exact-head Actions run #41617632263](https://github.com/ryonakayama234/DekaSugi/actions/runs/41617632263): SUCCESS; 12/12 focused source tests; docs check PASS (112 Markdown); full source pilot SUCCESS. Python 3.12.15 Linux; source pilot wall 9.849s (environment dependent).
- [Raw synthetic JSON artifact #13222047342](https://github.com/ryonakayama234/DekaSugi/actions/runs/41617632263/artifacts/13222047342) contains the complete 48-root census, 12 panel rows and runtime, 31,395 bytes uncompressed, SHA-256 of the original JSON member `0445b9db626bb1f1c64166a98c0856a43c06616f8f6acb373754fe8b1063900d`; downloaded and independently recomputed digest and aggregates. Artifact GitHub expiry expected 2026-12-03, so the source commit and this immutable digest are necessary provenance.
- Safe [Research verification #41617632246](https://github.com/ryonakayama234/DekaSugi/actions/runs/41617632246): SUCCESS. Inherited [G0C V5 source-only #41617632359](https://github.com/ryonakayama234/DekaSugi/actions/runs/41617632359): SUCCESS at same revision. **CI pass is not scientific review approval.**

## Source census and exact role-orbits

| Source measure | Independently reaggregated outcome |
| --- | ---: |
| Fixed-index root draws | 48 |
| Syntactic attempt slots (root + role variant per index) | 96 |
| Valid root Laws | 45 |
| Invalid root Laws (no replacement) | 3 |
| Actually constructed valid role variants | 45 |
| Equivalent syntactic roots under complete role semantics | 13 |
| Certified distinct semantic role orbits among 45 valid roots | 32 |
| Unresolved orbit proofs | 0 |
| Full-domain invariant NONALIAS comparisons against representatives | 622 |
| Existing all-role exact fallback comparisons | 18 |
| Semantic domain per valid root | 115,680 typed transitions |
| Independent scientifically sampled causal families | **NOT_CERTIFIED** |

Three invalid root IDs: `root-0003`, `root-0036`, `root-0046`. They are INVALID_TYPED_LAW; the current first-pilot record does not distinguish duplicate-edge rejection from invalid guard rejection, so finer causal attribution is **unknown**. The 13 exact certified aliases must not count toward independent structure. The 96 syntactic *attempt slots* include three invalid role-variant slots; 96 successful worlds would be an incorrect statement. 32 role orbits are distinct under the finite declared G0C source and the complete semantic invariant plus exact fallback; they do **not** establish 32 independent natural causal families.

## Closed-class inquiry opportunity: negative P-NAT result

| Panel property | Result |
| --- | ---: |
| Preassigned four-law B3 panels attempted | 12 |
| Valid and exactly certified | 9 |
| Invalid (contains invalid root, no replacement) | 3 |
| Proof-cap NOT_CERTIFIED panels | 0 |
| Certified adaptive advantage strictly positive | **0** |
| Certified adaptive advantage exactly zero | **9** |
| Fixed schedules examined (9 x 15^3) | **30,375** |
| Both oracles terminal MAP = 1.00 | 6 panels |
| Both oracles terminal MAP = 0.75 | 2 panels |
| Both oracles terminal MAP = 0.50 | 1 panel |
| Mean terminal MAP over the nine valid panels | 0.8888888889 for both |
| Positive opportunity fraction among valid certified panels | 0/9 |
| **Attempted-panel empirical positive-frequency bound** | **[0, 0.25]** |

The invalid panels were rooted at indices 0000..0003, 0036..0039 and 0044..0047. They are **unknown opportunity**, not confirmed zero. The [0, 0.25] bound is simply 0 positives through at most 3 invalids among 12 attempted panels, not a confidence interval or a general population estimate.

Every one of the nine valid panels shows the strongest fixed/open-loop schedule matching the best adaptive inquiry tree. In six, the nonadaptive schedule already perfectly identifies the true Law. In three, both remain at identical partial terminal accuracy (two at 0.75 and one at 0.50). That suggests either a shallow identification problem or hard-to-reach ambiguity in this particular distribution; these interpretations are **hypotheses**, not separately proved causal mechanisms. The previously constructed G0C positive +0.25 class remains a P-CHALLENGE fixture and is **not included in these 12 panels**.

## Scientific decision and limitations

- **Engineering:** source construction, typed proof, exact closed-class oracle, no-resampling accounting, full denominator and CI all PASS at evaluated SHA.
- **Research:** no positive adaptive-inquiry opportunity was detected in the nine valid randomly indexed P-NAT panels. This does NOT refute adaptive inquiry generally, and 12 attempted panels are not a powered independent-family study.
- **Population and transfer:** the deterministic synthetic source has shared grammar and only pseudo-independent index streams; independent source-family N and prospective power remain STOP_NOT_CERTIFIED. No learned policy, no Wake/Sleep, no public paid TRAIN, no fresh USE, no model adoption, and no DEV/FINAL.
- **Governance:** this is an append-only measured receipt following the original pre-CI NOT_RUN register. It must not overwrite earlier failed CI runs or old protected scores. A separate exact-head code/security review and dependencies gate merge. If a new source version targets branching-rich active inquiry after seeing this zero result, it must have a new explicit hypothesis/distribution/experiment ID; it cannot retrospectively modify CFAM-V1 or classify these zeros as successes.
