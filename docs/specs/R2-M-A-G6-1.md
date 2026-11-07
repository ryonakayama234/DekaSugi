# R2-M-A G6-1 — Revised-plan v2 implementation and recovery

id: R2-M-A-G6-1-20261107
status: draft_implementation / synthetic_only / G6-3_NOT_AUTHORIZED / no_scoring
updated: 2026-11-07
tags: r2-m-a, g6-1, remote-custody, slot-first, synthetic-only, recovery, owner-gate

## Authority

The Owner adopted [G6-0](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6704026771) and [revision v2](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6704172654), following [Lead entrance review](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6704099665) and [Muse agreement](https://github.com/ryonakayama234/DekaSugi/issues/146#issuecomment-6704129515). This PR implements G6-1 only. It does not rehearse G6-2, authorize/run G6-3, score G6-4, execute real laws or pay research Q. No GO artifact is published. Existing G3 engineering-only and scoring guards and G5 sealed original are unchanged.

## R1: G5 two-layer validator

Frozen G5 ref: audit/r2ma/g5-order-20261107; pin bb2e27a20657fefa5426d970c3275b8d95a846dc; 473 bytes SHA-256 b4aa94023961d4858919351f0097f197f5397b5f3d6f50c90271535e4c3e65c7. The remote reader verifies ref SHA, fetches the pinned commit and bytes and verifies ref unchanged. Raw-byte verification includes exact schema, target_head, hash-sort/1 (SHA256(seed || 0x00 || law_id)) and unique 16 laws. Separately expand G5 law order × USE points lexicographically (011,101,110,111) × seven arm identifiers lexicographically into 448 Slot tuples; call the frozen validate_g5_order_manifest. The expanded canonical Slot digest, not G5 raw SHA, goes in versioned run-lock.

## R2: Remote slot-first write-once and resume

Only the pinned GitHub run ref audit/r2ma/g6-run-20261107 is authoritative. SLOT_RESERVED includes exact slot identity, ordinal, prior journal tip and versioned run-lock digest. In the same new Git commit, create a separate immutable reservation marker. A non-force fast-forward push followed by remote ref confirmation, fetched pinned commit and byte-for-byte event and marker readback **must finish before child spawn**. Failure/timeout/unknown result is RUN_BLOCK; never retry. The Actions workflow uses a single concurrency group, cancel-in-progress false. GitHub-only custody is tamper-evident but is not independent WORM/timestamp security.

State machine: NOT_STARTED -> RESERVED -> FINISHED. A reserved but unfinished slot is materialized as STARTED_MISSING on restart, forever nonspawnable and stops the run. End records are terminal. An additional LAW_CHECKPOINT preserves the digest of the **entire previous run root**, not a substitute for slot-by-slot checkpoints.

## R3: Recovery matrix

| Verified remote evidence | Restart decision | Non-repeat rule |
|---|---|---|
| No Q_ATTEMPT | May begin when otherwise eligible | No prior Q attempt |
| Q_ATTEMPT without Q_PRECOMMIT | STOPPED_PRECOMMIT_UNKNOWN / run STOP | Precommit push uncertain; no second precommit |
| Q_PRECOMMIT without Q_ANSWER | STOPPED_Q_UNKNOWN / run STOP | Paid Q may have happened; no requery or fabricated recomputation |
| Q_ANSWER without SNAPSHOT_LOCK | Regenerate from recorded public4 and journal | No second Q |
| SNAPSHOT_LOCK | Regenerate exact Snapshot/v2 and compare locked bytes SHA before reuse | Local cached bytes not authoritative |
| SLOT_RESERVED without SLOT_FINISHED | STARTED_MISSING / run STOP | Child may have spawned; no second spawn |
| SLOT_FINISHED | Check terminal receipt, skip | No second child |
| LAW_CHECKPOINT | Revalidate full root digest | No suppressed missingness |

Q answer is recorded as public observations plus the validated public journal in remote evidence, not merely as an isolated hash. An unknown precommit push is treated as possibly sealed, without re-precommit. No local workspace evidence can be used to infer successful Q.

## R4: Formal mode

G3 EvidenceLedger, child_supervisor, child_entry, their engineering_only requirements, and old evaluator_gate are untouched. G6 has a separate versioned run-lock, OwnerGOReference, three-way gate (R1 G5 pin + exact run-lock + pinned GitHub G6-3 Owner GO artifact crosschecked with authenticated Owner comment on Issue #146), and an independent raw MeasurementReceipt schema with environment and raw CPU/wall/RSS. A caller-supplied boolean or fake G3 engineering receipt cannot open the production path. **No audited G6 production executor is installed** in G6-1; production slot requests RUN_BLOCK even if the gate were later satisfied, pending separate Owner authorization/review. G6-4 scoring permission is wholly separate and not implemented.

Frozen per-child: wall 5 seconds, CPU 5 seconds, RSS 512,000,000 bytes, exactly one attempt without retry. F01/F11 NOT_EVALUATED, M_use NOT_CERTIFIED, M_gap UNKNOWN, closure UNKNOWN, B NO-GO.

## R5: Opaque artifacts and synthetic verification

Snapshot and trace paths use only opaque 32-hex identifiers, never law ID or arm. ChildRequest still has exactly five public allowlisted fields; parent-only law and true USE value never become child fields. Tests inject altered G5 order, duplicate reservation, push loss before/after remote publication, forced termination before spawn and after spawn/before terminal, STARTED_MISSING, Q uncertain window, raw journal tampering, Snapshot regeneration mismatch and no-GO production denial.

## Changed existing sources / review boundary

The only existing source modification is a deny-only extension of the child import guard to include the new G6 parent-side modules. It is necessary to keep the audited child/evaluator import separation and does not relax any guard. Other changes are new parent modules, tests, this document and read-only workflow. GitHub-only timestamp and admin rewrite limitations persist; G6-2 rehearsal, actual remote custody verification, G6-3 implementation and G6-4 scoring are not claimed by a green synthetic test.
