# OPPORTUNITY-001 — WSL2 private original capture and encrypted Drive backup (NO SCORING)

id: OPPORTUNITY-001-PRIVATE-OPERATOR-V1
status: DRAFT_NOT_ACTIVATED_NO_PRIVATE_CAPTURE
updated: 2026-10-29
tags: opportunity, private-custody, operator-guide, wsl2, encrypted-backup, no-scoring


Status: DRAFT. **Do not execute until PR #75 has independent exact-head review, green CI and is merged into main.** No genuine new TRAIN64 private originals have been captured yet. Never upload an old DEV64 ZIP in their place. This runbook does NOT grant scoring authority.

## Prerequisites

Run inside **WSL2/Linux bash**, from the root of a clean, reviewed main checkout. Exact Python **3.12.15** is required; the frozen generator refuses a different patch version. If necessary, use uv to install the pinned interpreter (uv python install 3.12.15) and verify it with (uv run --no-project --python 3.12.15 python -V). Have GnuPG/gpg installed. Keep its encryption passphrase in a private password manager, never a chat, terminal command, public repo or public CI.

The dedicated Google Drive folder already created for the owner must stay **unshared**. Do not put its URL, ID, account information, raw audit examples, families or seeds in this public repository.

## Step 1 — One durable local volume and one ephemeral second file system

The source-first capture CLI currently requires TWO owner-only pre-existing output directories on distinct mounted Linux filesystems. On a typical WSL2 machine, the home folder is persistent and /dev/shm is a distinct, volatile tmpfs mount. The tmpfs copy is **not independent long-term custody**. Run:

    set -euo pipefail
    umask 077
    PRIVATE_DIR="$HOME/dekasugi-train64-private"
    SECOND_DIR="/dev/shm/dekasugi-train64-second-$(id -u)"
    install -d -m 700 "$PRIVATE_DIR" "$SECOND_DIR"
    test "$(stat -c %d "$PRIVATE_DIR")" != "$(stat -c %d "$SECOND_DIR")" || {
      echo "STOP: two distinct filesystems required" >&2; exit 2;
    }
    test "$(stat -c %a "$PRIVATE_DIR")" = 700
    test "$(stat -c %a "$SECOND_DIR")" = 700
    test ! -e "$PRIVATE_DIR/original.bin" && test ! -e "$SECOND_DIR/original.bin" || {
      echo "STOP: original already exists, do not regenerate" >&2; exit 2;
    }

If these tests fail, STOP; do not bypass the checks. The owner-only original must be outside the public repo. Do not begin a new capture if any partial original was left by a failed prior invocation.

## Step 2 — Capture new TRAIN64 audit originals BEFORE scoring

This command is only for a reviewed, merged main checkout on a trusted private host (NEVER public GitHub Actions). Use Python module execution (-m) to make the repo's scripts package importable:

    uv run --no-project --python 3.12.15 python -m scripts.capture_opportunity_private_original \
      --capture-before-scoring \
      --primary "$PRIVATE_DIR/original.bin" \
      --secondary "$SECOND_DIR/original.bin"

The implementation verifies the old 14 immutable source blobs, the new nine-source lock and preserved ORIGINAL public B1/B2/B3 policy choices, independently verified 64 public tasks and third-audit commitment BEFORE storing. It creates two exclusive mode-0600 raw files and verifies full readback hashes. No OFF/ON score is computed. Only the redacted SHA256/size/count receipt may be copied; do NOT publish or upload the raw files. Failure must STOP, preserving any existing original unchanged.

## Step 3 — Encrypt locally and verify exact plaintext recovery

After a **successful** capture and readback, run:

    test -f "$PRIVATE_DIR/original.bin"
    gpg --no-symkey-cache --cipher-algo AES256 --symmetric \
      --output "$PRIVATE_DIR/original.bin.gpg" "$PRIVATE_DIR/original.bin"
    chmod 600 "$PRIVATE_DIR/original.bin.gpg"
    RAW_SHA="$(sha256sum "$PRIVATE_DIR/original.bin" | cut -d' ' -f1)"
    RESTORED_SHA="$(gpg --quiet --decrypt "$PRIVATE_DIR/original.bin.gpg" | sha256sum | cut -d' ' -f1)"
    test "$RAW_SHA" = "$RESTORED_SHA" || {
      echo "STOP: private ciphertext cannot recover original bytes" >&2; exit 2;
    }
    sha256sum "$PRIVATE_DIR/original.bin.gpg"

The gpg prompt is local. Never paste the passphrase into a chat or terminal argument. Record the redacted raw and ciphertext hashes privately.

## Step 4 — Encrypted upload to owner-only Drive; independent restore

Open the WSL2 private folder in Windows Explorer:

    explorer.exe "$(wslpath -w "$PRIVATE_DIR")"

Drag ONLY the ciphertext named original.bin.gpg into the dedicated non-shared owner Drive folder. **Never upload original.bin or the ephemeral tmpfs copy.**

Before any scoring, independently check Drive's API metadata (file ID, revision, owner-only permissions, size, timestamps, retention state). Download the exact uploaded ciphertext to a **new** local file, verify its SHA256 against the original ciphertext, decrypt the downloaded file **locally**, and verify the plaintext SHA256 matches RAW_SHA from Step 3. Retain original receipt, source identity, chronology, readback, object revision, ACL and documented lifecycle off-public GitHub. A normal unshared Drive folder is not automatically immutable or retention-protected; until these are independently attested, external private custody remains **NOT VERIFIED** and score authorization remains **FALSE**.

## Step 5 — Separate reviewed one-shot activation

Only after archive identity, restricted durability, independently verified restore and a separately reviewed single-activation actual scorer is explicitly approved may the 64 fresh TRAIN64 OFF/ON pairs be scored exactly once. This capture procedure is **not** that activation. Do not regenerate prior DEV/FINAL or infer a research null result from zero scored rows.

References: [private capture specification](OPPORTUNITY-001-PRIVATE-CAPTURE.md), [capture program](../../scripts/capture_opportunity_private_original.py), [two-copy comparison](../../scripts/verify_opportunity_private_copy.py), [actual scorer (hard-off)](../../scripts/opportunity_real_pair_engine.py), [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).
