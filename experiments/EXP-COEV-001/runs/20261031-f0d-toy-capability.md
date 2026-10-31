# EXP-COEV-001 F0-D — public mock bearer / nonce / HMAC wire

id: EXP-COEV-001-F0D-TOY-CAPABILITY
status: PUBLIC_INVENTED_ONLY; NOT_AUTHENTICATED; NO_REAL_TRAIN; NO_SCORE
updated: 2026-10-31
tags: custody, toy-wire, protocol-negative, hmac, replay, research-integrity

## Local owner context
The owner ran a pinned, hash-checked GnuPG toy code under coevcustodian UID; public toy AES256 roundtrip and incorrect disposable passphrase rejection succeeded. This is OWNER-REPORTED host evidence, not third-party attestation or signed real study data. No private source or real scientific key was accessed or created.

## Design-only message boundary
`packages.concept_custody.toy_capability_gate.PublicToyCapabilityGate` is deliberately IN-PROCESS with a FIXED PUBLIC target and PUBLIC partition seed 2501. Per-run toy capability is random (bearer, not a signed client credential) and is returned to the dummy learner. Toy HMAC key is random and kept in the Python gate object (not independent key custody). All claims are purely about **code invariants and adversarial test harness**, not secure production authentication.

Requests are exact 1024-byte-max single JSONL object containing wire, op=query/close, phase=TRAIN only, arm, opaque session ID, disposable bearer capability, next integer sequence, unique 128-bit-format nonce, and query input_id only for op=query. Duplicate JSON keys at any depth, extra fields, bool-for-int, wrong phase/arm/session/capability, replay/non-monotonic sequence and repeated nonce are rejected with constant `{"error":"REJECTED"}`. Only up to two unique G1 query-pool IDs return selected toy answers; audit IDs, off-pool values, a third question and all DEV/FINAL/scoring requests are denied. Denied requests must never consume a sequence, quota or receipt position.

Each accepted response contains permitted selected answer (or close count) and previous-digest pointer. SHA-256 content hash and HMAC-SHA256 simulate a tamper-evident append-only transcript; tests reject forged answer, previous pointer, digest, MAC, extra fields or wrong predecessor. HMAC verifier operates in the SAME PROCESS as dummy signer; it is not external verification, a key-management standard or a GPG signature. No target class, secret heldout outputs, audit IDs, seeds or official scores returned. No Google Drive interaction.

## Gate status
Review exact-head safe CI and Codex before any suggestion to use local fixture. Real independent source, signer/verifier isolation, private key custody, human/review authority, actual source-seed freeze, method/power lock and separately authorized TRAIN/FINAL are still absent. A real custodian would need an authenticated wire, signed append-only records verifiable by a separate principal, isolated data-generation context and a protected source. This toy is NOT production-ready.
