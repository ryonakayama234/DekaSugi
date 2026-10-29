# OPPORTUNITY-001 — owner-private reviewed one-shot activation contract

id: OPPORTUNITY-001-ACTIVATION-V1
status: ACTIVATION_PR_REVIEW_PENDING_NO_LIVE_SCORE
updated: 2026-10-29
tags: opportunity, train64, main-only, activation, single-use, no-public-data

## Authorization and scope

The owner already captured the 64 genuine evaluator-only third audits once on
WSL2 using the previously reviewed source-first program and exact Python
3.12.15, with exact SHA readback. The owner has locally recovered the original
raw SHA from GPG ciphertext and matched local ciphertext SHA with an independent
download of the owner-only Drive object; Drive's available version is marked
keepForever. The nonshared Drive archive is versioned and independently
retrievable; keepForever is NOT WORM protection from whole-file deletion or
account loss. The frozen method does not separately mandate WORM, but this
limitation must be disclosed in the custodian's authorization record.

[Actual engine](../../scripts/opportunity_real_pair_engine.py) and
[private one-shot runner](../../scripts/opportunity_one_shot_runner.py)
**retain False source flags** on this branch and in regular Python imports.
[Owner-only activation wrapper](../../scripts/opportunity_approved_activation.py)
temporarily enables them only AFTER explicit owner confirmations and the
exact reviewed clean canonical origin/main checkout and Python 3.12.15
are verified; it restores both flags to False even if the scorer fails.

The official frozen method, public TRAIN64 task manifest, 192 prespecified
policy choices, exact top SkillCandidate, original private third-audit bytes,
immutable old14/new9 source locks and budgets 4/100 MUST remain unchanged.
The actual trial engine uses a fresh canonical registry/meter per arm and
OFF before ON; false_solved aborts the run before trying the next arm.

## One irreversible run, no rerun

Only the **owner's WSL2 private Linux host** may execute the wrapper after
this exact-head PR is independently reviewed (no P0/P1/P2), passes CI and
is merged to main. The owner needs the previously captured original.bin,
which must NEVER be regenerated or uploaded to public GitHub.

A run is approved only for a **single fixed, clean main commit** and
one fixed external raw-original SHA. The private runner verifies all gates
before scoring and reserves a private fsynced STARTED directory. Each OFF/ON
arm is separately marked ARM_STARTED (fsync) **before** invoking the canonical
scorer; its exact original 9-element audited tuple is saved owner-private
before normalization; a strictly redacted paired summary is also saved.
After 64 complete pairs, COMPLETED is written. A false_solved or crash
writes STOPPED or leaves a start marker and **permanently forbids retry**.
Independent external chronology must preserve the ledger (root deletion
is not prevented by a normal filesystem).

Do not add a GitHub Actions scorer workflow or run from a GitHub/CI runner.
CI calls only artificial-data tests. The activation wrapper prints a generic
failure on exception; never private third-audit, source labels, paths, seeds,
passphrase or original scorer tuples. The user must not paste raw scorer output
or files into an issue.

## After merge, before owner runs locally

1. Verify exact-head independent Codex review, full PR CI green and successful
   main merge CI; freeze activation main commit and relevant evaluator/
   verifier/meter source blobs as external reviewed provenance.
2. Independently check restricted external original chronology, recorded
   ciphertext byte identity, owner ACL, one retained Drive revision and
   restoration record against the specific original. Record any lack of
   deletion- or account-loss-proof retention, without falsely claiming WORM.
3. Issue a single owner command using source main commit and pre-existing
   original SHA, requiring both --confirm-offsite-custody and
   --confirm-never-retry. Do not include raw input/output in the command.
   Never use a newer unreviewed main commit, PR branch, or Actions.
4. On completion or abort, collect only redacted hashes/count/status;
   independent read-only recount of private per-arm original tuples and
   public redacted aggregate is a separate follow-on review. Do not claim
   a scientific capability result before it.

Current genuine new TRAIN64 paired OFF/ON score count: **0**.

Refs: [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66),
[Issue #79](https://github.com/ryonakayama234/DekaSugi/issues/79),
[One-shot runner contract](OPPORTUNITY-001-ONE-SHOT-RUNNER.md),
[Frozen pilot method](../../experiments/OPPORTUNITY-001/pilot-v1.md).
