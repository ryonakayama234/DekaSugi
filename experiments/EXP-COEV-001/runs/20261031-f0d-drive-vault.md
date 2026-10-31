# EXP-COEV-001 F0-D Drive storage preflight

id: EXP-COEV-001-F0D-DRIVE
status: ENGINEERING_ONLY; NOT_FROZEN; NOT_SCORED
tags: drive, ciphertext, custody, integrity, synthetic
updated: 2026-10-31

Verified through Google Drive metadata only: historical OPPORTUNITY-001 GPG archives are owner-only and unshared. The historical files were not opened or modified. A new empty owner-only folder was created for future COEV encrypted artifacts, with its ID omitted from this public repo. No source, holdout labels or new secret seeds were generated.

The new Python preflight calculates a SHA-256 hash and size for bounded local .gpg byte files and compares a strict source-method receipt. It does not verify GPG encryption, perform decryption, authenticate an operator, serve Oracle answers or score any data. Five synthetic tests cover mutation, forged metadata, invalid method/shape, empty and symlink rejection, and command-line behavior. A .gpg filename alone is not proof of encryption.

Owner-operated local custody may separate evaluator material from the learning client but is not independent third-party custody. The actual source generator, isolated evaluator, signature policy, preregistered method, and acceptance checks remain outstanding under F0 #110 and #116. Formal TRAIN and FINAL remain unauthorized.
