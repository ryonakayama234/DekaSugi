# EXP-COEV-001 F0-D: PUBLIC disposable GPG rehearsal

id: EXP-COEV-001-F0D-PUBLIC-GPG
status: PUBLIC_SYNTHETIC_ONLY; NOT_FROZEN; NOT_SCORED
tags: gpg, aes256, negative-test, custody, engineering-only
updated: 2026-10-31

## Inputs / outputs
The owner reported Linux directory DAC access test: normal WSL UID denied read+execute of the custodian home, whereas `sudo -u coevcustodian` allowed both. This is **owner-reported local DAC evidence**, not protection from sudo/root/Windows administration or third-party independent custody. No private key or scientific source has been created.

`packages.concept_custody.public_gpg_rehearsal` is a PUBLIC INVENTED synthetic AES256 symmetric roundtrip, deliberately distinct from the real source generator. Under the current unprivileged Linux UID it creates a 0700 temporary directory, a disposable GPG home, a fixed publicly known dummy plaintext, and randomly generated **disposable test-only passphrase** in a 0600 file. GnuPG encrypts dummy, then decrypts it, checks byte identity, and verifies a wrong dummy passphrase is rejected. The entire temporary directory is deleted on exit. All child subprocesses are argument-vector GPG invocations without a shell, no user secret values in argv, and have 20-second individual timeouts. Stdout prints only a tiny JSON status with explicit NO-SCIENCE flags.

Security qualifications: this uses **symmetric GPG with disposable temporary passphrases**, NOT a long-term science encryption key, not an offline root seed, not genuine private label separation, not an independently controlled evaluator. A successful test shows that this host can perform a dummy roundtrip, not that actual hidden-target data can safely be evaluated. The temporary GPG agent and process/session environment require further review. Real TRAIN/DEV/FINAL remains forbidden pending approved source/custody freeze under F0 #110, #115, #116, #117.

## Evidence gate
A standalone new CI-SAFE-V2 explicit synthetic test runs the public rehearsal under an unprivileged GitHub Actions user, checking AES256 roundtrip, incorrect-passphrase rejection, no printed secrets and false scientific result flags. Exact-head CI and independent review needed; no real key/data/score is generated or read.
