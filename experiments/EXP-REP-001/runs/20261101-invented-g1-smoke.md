# EXP-REP-001 — Invented G1 smoke / 2026-11-01
status: ENGINEERING_ONLY; NOT_FROZEN; NOT_FORMAL_TRAIN; NOT_DEV; NOT_FINAL
id: EXP-REP-001-RUN-G1-20261101
updated: 2026-11-01
tags: experiment, engineering, synthetic-run, representation
issue: https://github.com/ryonakayama234/DekaSugi/issues/123
design_pr: https://github.com/ryonakayama234/DekaSugi/pull/124
code_commit: 1e25c08ace31be2b8725e915c04dc22e5d86bb73

## Local verification (not CI, not an independent audit)
Python 3.13.5, Linux container, standard library only. Commands:
```bash
python -m unittest discover -s tests -p 'test_rep001_toy_engineering.py' -v
python -m packages.rep_evaluation
```
The exact six code files in the code commit were also executed in an isolated local directory (git blob content hashes checked). Eight `unittest` tests passed; CLI output:
```json
{"audit_count":8,"concept_names":["gated_true"],"examples_per_world":1,"r1_correct":4,"r2_correct":4,"r3_correct":8,"source_kind":"INVENTED_TOY_ENGINEERING_ONLY","toy_eval_worlds":4,"train_worlds":3}
```
This **does not** estimate H1: fixtures were hand-chosen and disclosed; all 3 training worlds and 4 toy evaluation worlds share the same abstract gated-true relation, so they are NOT structurally disjoint. One public probe and 2 subsequent toy audit transitions per eval world. R2 is weak exact-instance retrieval and does not use the new-world public observation as a robust within-world learner; R1 uses the first consistent expressive fixed model. Counterfactual resets/setup are free in this toy. Results are not blinded or independently controlled and have no generalizable statistical confidence interval. **No scientific adoption, holdout activation, or prior frozen score.**

Tested: strict Boolean/action validation, deterministic synchronous transition, contradiction diagnosis vs direct grammar, deterministic maximum-disagreement candidate query, observation without hidden graph field, 3-world supported role concept, snapshot tamper detection, object-name invariance and public toy CLI. Internal `InventedWorld._rules` is still inspectable inside the same interpreter and therefore cannot serve as an independent scoring boundary.

## G1 blockers
Implement genuine independent environment/evaluator, complete 4–8 objects and multi-edge mixtures, graph-isomorphism canonical class-disjoint train/dev/final splits, fair R2 with matched test-time observation transcript, query/setup charges and bounded active loop, resource/power preflight, graph/leakage negative tests, independent review and exact PR-head CI. Never treat this document as authorization for future FINAL.
