# R2-M-A G3-3 — custody, remote pre-score seal and G4 audit materials

id: R2-M-A-G3-3-CUSTODY-20261106
status: implementation_candidate / engineering_only / no_G4_G5_G6_GO
updated: 2026-11-06
tags: r2-m-a, g3-3, custody, synthetic-only, audit-scaffolding, owner-gate

## Authority and frozen boundary

Owner's [G3 implementation GO](https://github.com/ryonakayama234/DekaSugi/pull/183#issuecomment-6675971478) covers three separately reviewed implementation PRs under DIAG-R-20261106-10 and Muse R-20261106-11. G3-1 PR #184 and G3-2 PR #185 are merged. This G3-3 branch starts from new main `177bfa1757f40c6451dc521b413841d790bdae24`. Frozen G2 main `cf844094fb5907a37bb496760e206f9061deb021` and document SHA256 `865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68` are unchanged.

**No 448 fresh-child scientific measurements, paid research Q, actual G4 audit, G5 law ordering/seed, G6 execution/score, B science or method rewrite are authorized.** The contract constant `SCIENTIFIC_EXECUTION_AUTHORIZED=False` and G4/G5/G6 gate flags remain false. Even an asserted `owner_approval=True` is rejected. F01/F11 NOT_EVALUATED, M_use NOT_CERTIFIED, M_gap UNKNOWN, N_rep/U/T NOT_EVALUATED, closure UNKNOWN, B NO-GO.

## Storage and chronology

- `evidence_ledger.py`: per-run **exclusive** root with G2 anchor and complete *unordered* expected set of 16 laws × 4 USE points × 7 arms = **448 parent-only slots**. The sorted serialization is **not** a G5 execution order.
- Canonical JSONL event entries contain monotone `seq`, `prev_sha256` and `entry_sha256`; the entire chain and state transitions are replayed under `flock` before every `O_APPEND` write. fsync file and directory. Exclusive raw receipts use `O_EXCL`; existing targets, duplicates, missing predecessors, altered sequence, malformed UTF-8/NaN, and post-prescore events are refused.
- Q001 intent fixes P3 evidence SHA, legal Q digest, single paid budget, query 001, deadline, method/policy SHA **before the answer**. `remote_custody.py` commits the exact immutable intent to a *dedicated GitHub audit branch*, uses non-force push, confirms remote ref SHA, fetches the exact pinned commit and compares the actual bytes. Missing push or byte readback **blocks the answer**; the synthetic-only answer seam rechecks the remote object immediately before its callback. A failed intent cannot be retried within the same run.
- Per-slot START may occur once, END once. Missingness is **NOT_RUN** or **STARTED_MISSING**; terminal results are TRACE_PRESENT, INVALID, RESOURCE_STOP, RUN_BLOCK or UNMEASURED with raw SHA/typed reason. No silent success-zero substitution, removal from denominator or automatic retry.
- Before any score the ledger creates a 448-row manifest with every missing/failure status and prior journal-tip SHA, commits it to the remote audit branch and re-reads the pinned remote commit. Replay must match the frozen manifest; all individual Q remote receipts are reverified. Failed pre-score commit/readback stops the process. Even a complete and remotely sealed 448-slot manifest **does not grant score permission**.

## Isolation and limitations

The modules are **parent/evaluator-side only**, on the child import denylist and not reached from `child_entry`. No scientific runner, public/private truth comparator or scorer is added. G3-1's local synthetic barrier is **not** proof of a GitHub remote commit. The Git remote backend is real (explicit audit checkout and origin), but tests use a deliberate `FakeRemote`; their success cannot attest the actual GitHub API, remote custody or the prospective execution environment. SHA hash chains provide tamper evidence *when externally pinned*, not OS-enforced WORM storage. GitHub-only history is not an independent trusted timestamp and privileged operators could rewrite it; G4 must assess these residual risks.

## G4 dossier generator

`g4_dossier.py` creates eight exclusive files with target 40-digit head and every audit field marked **NOT_AUDITED**: `source-lock.json`, `import-graph.json`, `routes.json`, `arms-and-budget.json`, `cost-audit.json`, `custody-audit.json`, `negative-tests.md`, `g4-decision-template.md`. It returns SHA256 for those template bytes; no exact-head real-path audit, reviewer signature or PASS is fabricated. G4 after code merge must be separately approved and capture real evidence; changes thereafter require a new audit.

## Synthetic-only negative coverage

`tests/test_r2_m_a_g3_3_custody.py`: push loss, remote readback mismatch, Q absent/expired/duplicated/out of order, forged SHA/law, duplicate run/slot, replay after failure, O_EXCL overwrite, event delete/reorder/alter/truncate/non-UTF-8/NaN, pre-score incomplete or lost, missingness retention and approval-spoof score denial, dossier generation refusal on existing path. G3-1/G3-2 and R2-M-ENG synthetic regressions remain separate. CI never runs 448 measurements or actual research source scoring. Every synthetic green check is engineering evidence only, **not** G4/G5/G6 authorization.
