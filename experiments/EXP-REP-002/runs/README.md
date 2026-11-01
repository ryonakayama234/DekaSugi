# EXP-REP-002 immutable run register

id: EXP-REP-002-RUN-INDEX
updated: 2026-11-01
tags: experiment, runs, reproducibility
status: NOT_RUN

This index distinguishes documentation from measured work. The design-only record is `20261101-design-review.md` and has **no training, inference or score**. Future disclosed engineering runs MUST add a new dated immutable receipt and raw manifest/model hashes. Never rewrite older G1-D receipts or claim a disclosed pilot is formal DEV/FINAL.

Required per run: exact code source head, tests and independent reviewer, generator/grammar/arm/split versions and hashes, structural-family manifest, training Snapshot hashes, per-world/arm/budget results (32 audit transitions are one world outcome), costs including action setup, learner-versus-evaluator boundary, complete negative findings, reproducibility commands and scientific claim level.
