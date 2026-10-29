# OPPORTUNITY-001 — reviewed one-shot runner architecture (NOT ACTIVATED)

id: OPPORTUNITY-001-ONE-SHOT-RUNNER-V1
status: IMPLEMENTED_HARD_OFF_SYNTHETIC_CI_ONLY
updated: 2026-10-29
tags: opportunity, train64, one-shot, pretrial, private-original, safety, no-scoring

## Purpose

This is the next engineering step AFTER the real fresh TRAIN64 original was
captured once (64 evaluator-only audit rows), encrypted locally, uploaded to a
restricted Drive destination and compared byte-for-byte against an independently
downloaded ciphertext. Do not regenerate the original: the existing file is the
source of evidence. None of those external observations authorize a scored run
merely because local hashes match. Keep original and GPG passphrase private.

A new `scripts/opportunity_one_shot_runner.py` contains the full private-host
one-shot call graph but has `ONE_SHOT_ACTIVATED = False`. The previously reviewed
`scripts/opportunity_real_pair_engine.py` independently has
`SCORING_ACTIVATED = False`. **Both** gates must remain false in this PR,
in CI and in the merged nonactivated implementation.

## Mandatory pretrial sequence (never a CI task)

1. Require exact Python 3.12.15, clean checked-out source commit matching the
   separately approved **main** activation SHA, and the explicit main-only
   activation receipt. No evaluation if an unreviewed commit is checked out.
2. Before importing project packages, independently verify the pinned historical
   14 source files, fresh generator nine source files and original official
   public 64 × 3 B1/B2/B3 choice bytes/digest. Do not rerun decision selection,
   old DEV/FINAL evaluation or historical holdouts.
3. Open existing private owner-only directory by nofollow file descriptors;
   reject unsafe intermediate ancestors. Read the original 0600 regular file
   by `dir_fd`, reject symlinks/hardlinks and verify its previously recorded
   exact SHA256. Do not create/rewrite/copy/regenerate an original.
4. Require 64 archival rows and locked third-audit commitments, then generate
   the new *TRAIN-only* source for public task identity verification, and
   compare all 64 original audit values, source IDs, family and seeds to the
   source reproduction. The original archived third audit, **not a replacement
   audit**, is passed to the evaluator. No private audits reach a chooser.
5. Reconstruct the exact old frozen top `SkillCandidate` only from
   independently verified historical TRAIN/DREAM (no DEV/FINAL) using
   the already reviewed `_rebuild_historic_train_dream_only`; validate
   frozen body hash, skill ID and all three original policy snapshot hashes.
   NEVER fabricate a new candidate or its provenance merely because the
   lower(trim(Input)) body looks similar.
6. Atomically create an exclusive reserved `opportunity-001-scoring-once-only`
   private directory and fsync it **BEFORE first scored OFF/ON arm**.
   A crash after reservation means no rerun. Fixed directory existence refuses
   a second attempt; independent external custodian must preserve that
   reservation against owner deletion (not cryptographically enforced by
   local filesystem alone).
7. Score 64 pairs sequentially, OFF before ON with the existing
   `false_solved` stop in canonical engine, never evaluate a DEV/FINAL.
   Each independently normalized/redacted paired result is saved exclusively
   in a private 0600 JSON file with fsync. No raw audit input/output,
   source-record ID, family or seed is written to the pair files.
8. Write `COMPLETED.json` only after all 64 pairs. On ANY failure, write
   `STOPPED.json` with completed count (no private example, path or exception
   string); never retry the run. Even successful completion permits no
   re-execution, resampling, post-hoc threshold change or new scorer mode.
9. Independently verify count, status and absence of private content.
   Publish approved redacted aggregate/provenance only after separate result
   audit. An incomplete run is an **incomplete run**, not a negative result.

## External records still mandatory for a live activation

- Restricted Drive version, owner ACL, retention/restore lifecycle, byte SHA
  comparison and operator-side GPG plaintext restoration have been reported or
  independently checked in earlier issue checkpoints. A revision with
  `keepForever=true` is useful but not WORM or protection against file/account
  deletion. Reassess the actual experiment's documented durability threshold
  before activation; do not invent stronger guarantees.
- Independently approved immutable run authorisation for this exact code commit,
  full owner-private raw-origin chronological record, the off-GitHub custodial
  record and one fixed run ID. The public GitHub repository/Actions MUST NOT
  receive an original, decrypted archive, passphrase, full private trace or
  private scored files. The owner must be able to retain evidence after a crash.
- A **separate exact-head CI-green independent Codex review** of this implementation
  and a later, separate main-only activation patch are mandatory.
- No scoring is authorized by this document, PR, synthetic tests or the existence
  of an encrypted backup. **Current scored real fresh TRAIN64 pairs: 0.**

Reference: [original capture operator guide](OPPORTUNITY-001-PRIVATE-OPERATOR.md),
[canonical engine](../../scripts/opportunity_real_pair_engine.py),
[frozen pilot METHOD](../../experiments/OPPORTUNITY-001/pilot-v1.md),
[Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).
