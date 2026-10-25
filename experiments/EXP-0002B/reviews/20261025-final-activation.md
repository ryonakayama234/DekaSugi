# EXP-0002B — FINAL112 activation gate / independent review

id: EXP-0002B-FINAL-ACTIVATION
status: approved by human; one-shot CI activation PR pending review; FINAL not evaluated
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
