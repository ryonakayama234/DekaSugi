# ADR-0004 — preserve immutable old CI source; create a separate safe successor

id: ADR-0004
status: proposed; pending_external_actions_disablement
updated: 2026-10-29
tags: architecture, decision, ci, research-integrity, source-lock

## Context and rejected alternatives
Original `.github/workflows/docs-check.yml` contains main-push old EXP-0002B DEV smoke and its artifact upload. It is *itself* one of nine PILOT-V1 byte-locked source files. Editing/removing the old DEV step changes the frozen evidence source; [closed PR #84](https://github.com/ryonakayama234/DekaSugi/pull/84) demonstrated source-lock validation failure. Rewriting historic lock hashes or weakening validators would sever experiment provenance, so reject both. Also reject merging any new PR while the old workflow is still enabled.

## Decision
Add versioned `research-verification-v2.yml` with only safe/synthetic commands, a separate source-only exact-byte verifier, explicit narrow unittest allowlist and no artifacts/scorers. Never patch the historical workflow. Before any main merge, the owner disables the original workflow via GitHub Actions and independently verifies actual `disabled_manually` state; repository code alone cannot do this. Versioned successor CI and historic evidence remain distinct systems.

## Consequences and tradeoffs
- Original PILOT-V1 byte provenance preserved; future documentation PRs can eventually merge without re-triggering historical DEV smoke.
- Reduced CI coverage is intentional and explicit, *not parity*. Future coverage restoration requires fresh safe test audit, no old partition generation or scoring, new reviewed CI version and exact-head approval.
- If the owner cannot securely disable/verify the old workflow, STOP; do not merge even if all PR checks are green.
- Re-enabling the original workflow is a recurring operational hazard. Record and monitor the disabled state before subsequent main merges; do not treat source byte-gates as an Actions control-plane monitor.

[Specification](../../specs/CI-SAFE-V2.md) / [Evidence ledger](../../process/ci-safe-v2-ledger.md) / [Issue #88](https://github.com/ryonakayama234/DekaSugi/issues/88).
