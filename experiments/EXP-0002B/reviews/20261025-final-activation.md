# EXP-0002B — FINAL112 activation gate / independent review

id: EXP-0002B-FINAL-ACTIVATION
status: reviewed and executed once; FINAL112 audited; trigger retired in follow-up PR
updated: 2026-10-25
tags: exp0002b, final, gate, preregistration, audit

## Authorization and scientific constraints
- Human authorized on 2026-10-25: freeze integrity preflight, isolated activation PR, PR CI, exact-head independent review, **one** FINAL112 evaluation only if all gates pass, complete artifact audit and follow-up documentation. Stop before FINAL for any serious mismatch.
- [plan-v2](../plan-v2.md), [freeze-v2.json](../freeze-v2.json), kernel, generator, evaluator, Registry, verifier, canonical meter, all thresholds, datasets and accept/reject gates are **unchanged** by this PR.
- Prior main `bd325da60154a13e767d017543472f03fe5d8043`; [DEV engineering record](../runs/20261025-dev-smoke.md) successfully verified 48 tasks with all three independent arms. DEV never used for tuning.
- Pre-activation read-only audit: all nine frozen execution-source Git blobs matched the entries in `freeze-v2.json`; current main workflow had no FINAL trigger, latest main Actions #40163160602 succeeded. Runtime evaluator separately validates all frozen source/data/policy identifiers and retrains TRAIN-only before any FINAL task.

## Single activation control
- Workflow is still triggered by regular `pull_request` and `push(main)`, but FINAL step **runs only** on the first attempt of a `main` push with the exact approved squash-merge subject prefix: `EXP-0002B FINAL112 activation [20261025-APPROVED]`.
- PR CI, ordinary main pushes, and reruns with `github.run_attempt > 1` do not evaluate FINAL. The PR must be squash-merged with the activation title **exactly** as above; otherwise FINAL remains disabled. The published artifact is `EXP-0002B-FINAL112`. Source code and audit methods remain frozen.
- The one-shot predicate is a CI workflow gate, not a cryptographically enforced once-ever lock. After reading the outcome, a follow-up documentation PR must **remove** the activation steps to disable replay of this activation subject. No intentional reactivation using the same title.
- No CI use of `--phase final` in pull requests. Run once in main only after exact-head Codex review completes without material issues, PR CI is successful, and change diff is workflow plus this gate/document index.

## Post-run disposition
- Inspect the complete 112-task immutable JSON; independently reaggregate OFF/ON/LEARNED, audits, candidate/call totals, seven-family OOD16, correctness and numeric thresholds, sign counts, p90, family-cluster bootstrap, training/CPU cost separation.
- Store original binary artifact ID, ZIP SHA-256, internal JSON SHA-256, source main commit, exact policy/dataset hashes and all results under `experiments/EXP-0002B/runs/`; synchronize AGENTS, DOC-INDEX, ARCH-001/002, specification, roadmap, gate audit and relevant issue.
- If any frozen v2 numeric acceptance gate fails, record `not_demonstrated`. Even all numeric passes do **not** automatically promote to the default Registry; adoption requires a separate independent research decision.

Related: [DEV run](../runs/20261025-dev-smoke.md) / [independent evaluator review](20261025-evaluator-gate.md) / [plan-v2](../plan-v2.md).

## 実施完了・起動ゲート解除（2026-10-25）
- 最初の[PR #28](https://github.com/ryonakayama234/DekaSugi/pull/28)レビューの文書整合性P1を修正し、修正後最終head `a4ee8592a94d1d091aeaac47475c97e1446db4be`は[PR CI #40176002565](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176002565)成功、Codexの再レビュー `has_any_findings=false`、`has_unresolved_findings=false`。古いP1スレッドは返信・解決済み。
- 承認タイトルでsquash-mergeしたmain `37b30752b46ea108d18dbdb531797e0106f52dc0`の[Actions #40176125696](https://github.com/ryonakayama234/DekaSugi/actions/runs/40176125696)が成功。FINALの実行とArtifact uploadは各1回のみ成功、後続runでは再実行しない。
- 成果Artifact `12592665362`、ZIP SHA-256 `1a013bb9fc2a4fa70006c0b0e3e52b7120217f2e66364459a5d615b3db4b6304`。112問を読み出し、独立に五つの数値ゲートと7 cluster bootstrapを再集計して一致。詳細は[正式FINAL run](../runs/20261025-final112.md)。
- 同じFINALへの偶発的な再計測を防ぐため、この文書同期PRでworkflowからFINAL実行・uploadの2ステップを削除。今後再実行はせず、新しい研究は別未使用holdoutで行う。
