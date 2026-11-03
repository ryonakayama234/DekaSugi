# EXP-REP-005-G0C — 2026-11-03 disclosed source-only engineering receipt

id: EXP-REP-005-G0C-20261103-SOURCE
status: SOURCE_ENGINEERING_CI_PASS_INDEPENDENT_REVIEW_PENDING
updated: 2026-11-03
tags: source-only, synthetic, engineering, negative-result
issue: #158
classification: disclosed synthetic calibration; NOT prospective science
main_module: packages/rep005_g0c

## Local execution evidence

Executed in an isolated Python 3.13.5 Linux environment; source files implement deterministic finite typed rules and are independent of unmerged V4 modules. Commands: `PYTHONPATH=. python -m unittest tests.test_rep005_g0c -v` and `PYTHONPATH=. python scripts/rep005_g0c_source_pilot.py --output /tmp/g0c-source.json` (local output path may vary). **8/8 local dedicated tests passed**. Approximate pilot wall-time 19.37 s; time is environment-dependent, not a fixed performance guarantee. The source report emitted all 48 proposal records, proof results, legal policy tree and run environment; GitHub CI artifact is required for independent download of the branch-exact result.

### Observed cohort census

| Measure | Observed |
|---|---:|
| Interleaved generated syntax proposals | 48 |
| Distinct declared production roots | 12 |
| Exact nonalias semantic role orbits | 11 |
| Exact typed transitions examined per proposed Law | 115,680 |
| Tested renamings for a NONALIAS pair | all 120 |
| Distinct statistically independent causal families | **NOT_CERTIFIED** |
| Historical complete 100M-syntax Hplus_G closure | **NOT_CERTIFIED** |

The cohort contains four concrete role-binding variants per predeclared production. Consequently the 48 proposals are not 48 independent mechanisms. The 11 orbit number is a structural count, not statistical N; neither the four binding variants nor recipe IDs can establish independent family-level evidence. Negative semantic alias: `split_guard_alias` exactly equals `direct` over the declared domain, despite different program syntax.

### Representability and inquiry controls

- Old H0 = 61 models, NULL plus all single, unguarded pulse effects with lag0/1/2 and ordered 5x4 bindings. `direct` and `split_guard_alias`: **IN_H0**; `guard_bit`: **OUTSIDE_H0** with 61 completed candidate mismatch witnesses. This is a finite meta-grammar diagnostic, not a learned new primitive.
- Positive disclosed closed class: four Laws `direct`, `guard_bit`, `guard_pulse`, `chain`, common reset 0, 3 paid legal actions, uniformly weighted true law. Exact exhaustive best adaptive terminal MAP = **1.0**, best nonadaptive open-loop MAP = **0.75**, gap **+0.25**, over all **3,375** legal fixed schedules; adaptive solver visited **2,184** memo nodes. This is an oracle property of these four **human-selected correlated** Laws, not a trained policy.
- Null control closed class: `direct` vs `guard_bit`, B2: adaptive=1.0 and open-loop=1.0, gap **0.0**; all **225** legal fixed schedules compared (240 memo nodes).
- Resource cap control: B4 has `15^4=50,625` schedules, exceeding default max_plans=4,000: returns **NOT_CERTIFIED / OPEN_LOOP_PLAN_CAP**, not UNID or a negative study result.

### Independent engineering checks

- Six reference Laws: all 115,680 cells/Law independently recomputed using a second evaluator based on the bit-level specification.
- 120 role renaming samples and three full-domain role-orbit equalities; one negative complete nonalias and cross-role alias.
- XOR parity, contradictory guards, typed false/Boolean index, role constraints, SHA-backed source output, proof budget failure.
- Latest exact-head GitHub CI and code/security review are **not yet certified by this local record**. CI receipts should be appended, not retroactively treated as prior preregistration.

## Research interpretation

G0C-1 finite source and G0C-2 exact small-class inquiry calibration **work locally**. Crucially, source diversity is only 11 role orbits among 12 predeclared production mechanisms, with strong within-root overlap. G0C-3 (independent generative ancestry cohort size, future sample precision/power) is **SCIENTIFIC_STOP / NOT_CERTIFIED**. Do not run G1/G2 fresh paid TRAIN, protected DEV/FINAL or automatic model adoption on this basis.

The constructive positive +0.25 inquiry gap establishes only the *existence* of a finite setting where using observations to change an action improves oracle identification over an optimized open-loop schedule. It says nothing about actual learned DekaSugi inquiry decisions, total training cost, real-world generalization, dialogue or new primitive semantics.

## Next research decision (not executed here)

An independently reviewed **prospectively specified distribution of mechanisms and ancestry clusters** must be established before claiming family-disjoint learning transfer. A later study must compare same-capacity fixed-Hplus controllers, active and prior-only policies, episodic retrieval and exact body-off, using paid public-only observations and a new independently custodied holdout. The previous V4 #155/#157 research Drafts and archived negative outcomes remain unchanged.


## GitHub Actions exact-code execution addendum (after original local receipt)

- Dedicated source-only CI: [run #41604853288](https://github.com/ryonakayama234/DekaSugi/actions/runs/41604853288), exact tested PR head `1faa8512272a0ac2ee80fe3736950349fd421a91`, **SUCCESS**; Python 3.12.15, 8/8 unit tests, document integrity PASS (108 Markdown documents), complete 48-proposal source pilot SUCCESS.
- CI's stdout confirms **48 proposals / 11 nonalias semantic role orbits / adaptive oracle gap +0.25**. This matches the disclosed local experiment, after fixing an initial script-as-file import failure (rerun as a module) and initial missing documentation metadata. Earlier failed CI runs remain historical and unaltered.
- [Raw GitHub Actions proof JSON artifact #13216860042](https://github.com/ryonakayama234/DekaSugi/actions/runs/41604853288/artifacts/13216860042) uploaded (3,467 compressed bytes; expected GitHub expiry 2026-12-03). It contains generated proposal records, H0 representability checks, adaptive witness tree, open-loop schedule, negative cap and runtime details. Source data are disclosed synthetic evaluator-only artifacts, not a hidden scientific score.
- [Research verification safe successor #41604853241](https://github.com/ryonakayama234/DekaSugi/actions/runs/41604853241) also SUCCESS at the same head.
- Latest-head independent method/security review was requested on Draft [PR #159](https://github.com/ryonakayama234/DekaSugi/pull/159); **approval NOT CONFIRMED**. This documentation addendum causes a new branch head and does not retroactively change the CI-evaluated source or confer new scientific evidence.

**Final substantive gate resolution:** G0C-1 engineering PASS, G0C-2 constructed closed-class opportunity engineering PASS, G0C-3 independent source-family sampling/power **STOP_NOT_CERTIFIED**, prospective paid Wake/Sleep/USE and protected G3 **NOT_RUN**, no formal model adoption or `main` merge.

## Independent review P2 remediation — 2026-11-03

An independent Codex code review of commit `8ef81ef637` reported two P2 findings: (1) a forged `Edge` subclass bypassing constructor validation could be accepted into `Law`; (2) NaN/+infinity proof deadlines disabled time caps. Both are security/engineering trust-boundary defects; they do **not** invalidate the idea of the finite synthetic setup but must be fixed before accepting its exact certificates.

The corrected code now validates `type(edge) is Edge` **before** dedup/sort of `Law.edges`, rejecting subclasses; all certificate entry points (`census`, `full_semantic_orbit_equivalence`, old-H0, `opportunity.certify`) require a built-in finite positive deadline <=3600s, and `signature` rejects nonfinite absolute deadlines. New adversarial regressions reproduce the rejected subclass and NaN/+Inf/-Inf inputs. In local rerun, **9/9** focused tests PASS; the original reported 48-proposal/11-orbit and positive +0.25 oracle results remain unchanged. GitHub exact-head CI and independent **re-review of this amended head** are required; historic earlier failed and passing runs are preserved.
