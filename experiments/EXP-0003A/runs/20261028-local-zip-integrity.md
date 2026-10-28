# EXP-0003A DEV64 — user-provided local original ZIP integrity attestation (2026-10-28)

id: EXP-0003A-DEV64-LOCAL-ZIP-CUSTODY-20261028
status: local_uploaded_copy_integrity_verified; second_independent_long_term_custody_not_verified
classification: PUBLIC HASHES ONLY; NEVER PUBLISH PRIVATE ZIP
updated: 2026-10-28

## Scope and provenance

The user supplied a purported 2026-10-27 local backup bundle to the assistant for an **offline, read-only check**. The supplied bytes were examined without rescoring any DEV/FINAL or generating any historical holdout. This attestation establishes **content digest equivalence** with the already archived public DEV64 ledger, **not** a validated permanent archive, nonrepudiation, or a cryptographically authenticated original chain. The local filename suffix `(1)` does **not** prove multiple surviving backups.

- Supplied outer ZIP: `DekaSugi_EXP-0003A_DEV64_private_evidence_backup_20261027(1).zip`
- Outer ZIP byte length: **65,315 bytes**
- Outer ZIP raw SHA-256: `bf84b5098cc5caa5ef47d2fca2c34e923ab65d1b785c281acf8404fe401d581d`
- Outer ZIP: 4 ZIP entries; `testzip()` CRC passed. The two embedded ZIPs also passed CRC verification.
- Embedded **original one-shot scoring** ZIP: SHA-256 `a70f21756c67c7d2c737d5bc4bd1ec410a6b369d505e3bd91a2f1a89ba3f09cb` (original run `40518246537`, Artifact `12739684056`).
- Embedded **independent audit-only** ZIP: SHA-256 `5b1826105cc1409bb707ae2d5328977f694f9fabdde1fd4f01338f3b9c75c5c3` (run `40522186710`, derived Artifact `12742377403`).
- Original original-member `SHA256SUMS`: **4/4 PASS**, including private JSON digest `490fbb3da156cc70e3525d6c67307b4b4e06bb725703e0b39543546275b87653` and public JSON digest `2fa48c841e99a69275c8bd3a5bd78eb2e01d4a3fcc226a6358958bf5cc053134`.
- Audit-only derived-member `SHA256SUMS`: **2/2 PASS**, including `independent-audit.json` digest `815249008c4121954053ee8fee5e2ff37efe7a81f6dab149ac6b9b1a0719bc19`.
- The embedded expected hashes and independent audit result match the pre-existing [DEV64 historical ledger](20261027-dev64.md).

## Trust and retention assessment

**What this proves:** the provided uploaded bundle contained ZIP members whose raw hashes equal the pre-registered and previously independent-audited historical DEV64 bytes; no reconstruction or new scoring was needed.

**What this does not prove:** that the user's device has durable encryption, that another physically / administratively separate copy exists, that any cloud location is access-controlled, that archive objects are versioned/retained past expiry, or that a future restore succeeds. **The uploaded ZIP is NOT encrypted** (ZIP encryption flag false). Do not put raw ZIP/third audit examples into this public repository or ordinary public Actions artifacts.

The historical original GitHub Artifact expires **2027-01-25T14:08:19Z** and audit artifact expires **2027-01-25T14:33:08Z**, according to the frozen original ledger. Keep the exact verified outer ZIP unchanged; create a **second private, access-controlled copy in a distinct storage location**, then verify the copied ZIP raw SHA equals the value above. Until the restored second copy is verified, the durable restricted-custody gate remains **not_verified**. The uploaded copy is neither an encrypted backup nor a substitute for independent off-GitHub retention.

## Research boundaries

This attestation applies **only to prior EXP-0003A DEV64** (64 tasks × four already-scored arms) and its audit-only correction. The DEV64 negative/engineering outcome and original failed workflow status are unchanged. **EXP-0003A FINAL128 remains sealed and not_run.** No new DEV/FINAL scoring or old task regeneration occurred.

**It is NOT the original private third-audit custody for the separate OPPORTUNITY-001 fresh TRAIN64 paired experiment** ([Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66)). That experiment remains `scored_trials=0`; its own independently verified restricted archive, source-first real scorer and one-shot authorization are separate mandatory gates.