# R2-M-A G6 executor & isolated rehearsal scope (G6-2 remainder / G6-3 preparation)

id: R2-M-A-G6-3-EXECUTOR-20261107
status: implementation_draft / NOT_AUTHORIZED / NO_EXECUTION / NO_SCORING
updated: 2026-11-07
tags: r2-m-a, g6, executor, rehearsal, fail-closed, recovery

## Authority and non-goals

Base: G6-1 PR #187, merge `5312672bf593f65d5d6dbbce2d7ff3729dd588ef`.
Owner-adopted G6-0 revision v2 and Issue #146 custody recovery rules remain normative.
This change **does not** issue or activate either Owner GO artifact, perform a
GitHub remote executor run, execute G6-3, score, alter the G5 seal, change G2
preregistration, modify the evaluator gate, or assert a scientific result.

Frozen children: wall 5 s; process CPU 5 s; RSS 512,000,000 SI bytes;
one attempt and no retry. G5 law-order, within-law USE×arm order and all
5 child-payload allowlisted fields are unchanged. The original G6-1
`r2ma-g6-event/1` schema and the production run-lock layout remain unchanged.
The parent alone holds law IDs, approved order, credentials and outcomes.

## Explicit start/resume contract

`G6Driver.start()` is **only** for a remote journal with no run-lock.
It verifies scope-specific Owner GO, seals the exact lock remotely and enters
the law-by-law sequence. It cannot assume that startup authorization implies
an implicit resume. `G6Driver.resume()` is **only** for an already-sealed
journal, reauthenticates against the remote GO and enters
`G6Orchestrator.resume_authorized()` before working on any slot.
Every call to a formal slot reauthenticates before reservation, and the
supervisor reauthenticates before process spawn. Each fresh driver instance
must provide its GO reference, delegated cgroup-v2 root and Q artifact files.

For a real `GitRunJournal`, production is strictly bound to
`refs/heads/audit/r2ma/g6-run-20261107` and `audit/r2ma/g6`.
For `RehearsalGitRunJournal`, the only writable journal ref and root are
`refs/heads/audit/r2ma/g6-rehearsal-20261107` and
`audit/r2ma/g6-rehearsal`; local artifacts must reside below the
corresponding `audit/r2ma/g6-rehearsal/artifacts/` subtree.
A ref/root/scope drift is rejected at the journal call boundary, not only
during constructor validation. There is no ref fallback and no force push.

### The irreversible per-slot ordering

1. Strictly verify Owner GO and require a delegated cgroup root argument.
2. Check `NOT_STARTED`, Q answer and snapshot lock; prepare the public
   5-field `ChildRequest`, but do not spawn.
3. Append `SLOT_RESERVED` + write-once marker to the scoped remote,
   push without force, verify remote pinned event bytes and exact journal tip.
4. **Only after reservation**, regenerate and revalidate the immutable
   Snapshot/v2 from recorded public4 and journal.
5. Invoke supervisor **formal mode** in a real fresh Linux subprocess with
   existing cgroup-v2 memory limit, process-group kill, PDEATHSIG gate,
   wait4 CPU/RSS and monotonic wall metrology. No G3 synthetic-mode bypass.
6. Transform raw supervisor observations into
   `r2ma-g6-measurement/1` receipt, check actual terminal enumeration,
   validate the receipt (including cap and environment checks) and
   write-once seal its canonical bytes locally.
7. Append `SLOT_FINISHED` to the remote with `receipt_sha256`
   and the original reservation entry digest. Never finish based on an
   exception handler or a missing child.

Any failure **after** step 3 leaves the slot reserved and unfinished.
A later resume emits `STARTED_MISSING` and blocks the run awaiting Owner
decision. No slot auto-repeat or rescore is possible. Missing raw CPU, RSS or
cgroup evidence is represented as `None`/`UNMEASURED`, never fabricated
as zero. The allowed terminal statuses remain exactly
`TRACE_PRESENT, INVALID, RESOURCE_STOP, RUN_BLOCK, UNMEASURED,
BOUNDARY_REVIEW`.

The child still emits its pre-existing engineering-prefixed protocol receipt;
the formal *parent* authenticates and verifies that child receipt and the
actual process metrics, and separately emits a formal MeasurementReceipt.
The child payload, child import contract and evaluator scoring boundary are
unchanged. Receipt files are local write-once evidence bound by the remote
terminal digest; relocating the full receipt bytes to an independent remote
evidence store needs an explicit retention decision before actual G6-3.

## Scope separation / Owner decisions

Production requires `OwnerGOReference` and `ProductionPermit`, under
`r2ma-g6-owner-go/1` at
`refs/heads/audit/r2ma/g6-owner-go-20261107`,
`audit/r2ma/g6-owner-go.json`, with decision `G6-3_OWNER_GO`.
The production authorization checks remain pinned G5 + exact production
run-lock + pinned GitHub GO artifact and authenticated Owner Issue #146
decision comment.

Rehearsal requires `RehearsalGOReference` and `RehearsalPermit`, under
`r2ma-g6-rehearsal-owner-go/1` at
`refs/heads/audit/r2ma/g6-rehearsal-go-20261107`,
`audit/r2ma/g6-rehearsal-owner-go.json`, with decision
`G6-2_REHEARSAL_OWNER_GO`. Its comment must contain the distinct
`G6-2 Rehearsal GO` marker and the exact rehearsal lock digest, and must
be posted by the same authenticated Owner to Issue #146.

Rehearsal run-lock schema is `r2ma-g6-rehearsal-run-lock/1` and includes
`rehearsal_only: true`. The original production lock is
`r2ma-g6-run-lock/1`. Both contain the same anchored G5 expansion, fixed
resource caps and no-score flags, but hashes are distinct. The production
authorization function rejects a rehearsal lock/GO, and the rehearsal
function rejects production lock/GO. Neither permit can select the other's
journal or supervisor mode. There is **no permit-generation function**, GO
file, activated branch, or permission shortcut in this PR. The old journal-only
rehearsal evidence remains unmodified.

## Public Q and Snapshot

`G6QStage.precommit()` checks public3, legality, remaining budget=1,
deadline, and the method/policy byte references **before** irreversible
`Q_ATTEMPT`; it then invokes the eng-style gateway precommit with
`prediction=None` and records matching `Q_PRECOMMIT`.
`record_q()` makes the single paid Q after the precommit remote seal,
validates public4 and appends the complete public observations and journal.
`snapshot()` regenerates, validates and remotely locks Snapshot/v2. The
recorded data and G6-1 event structure are identical in both scopes. An
uncertain precommit or Q window stops on restart; no requery or inference of
a missing answer.

### Unresolved: authoritative frozen METHOD / POLICY bytes

No independently identified pair of frozen byte artifacts **and exact
SHA-256 digest anchors** was found for `method_sha256` and
`policy_sha256` in a G6 Q intent. Method-v2 has an Owner adoption
record, but a version label or a nearby source file is **not** a valid
digest anchor. `FROZEN_PRODUCTION_METHOD` and
`FROZEN_PRODUCTION_POLICY` therefore remain `None`, and
`QArtifactFiles.digests(scope="production")` returns `RUN_BLOCK`
without emitting `Q_ATTEMPT`. Owner/Muse must identify the canonical
path, exact pinned commit, raw bytes and digest for each before production Q
can operate. This is a deferred authority decision, not a request to amend
method/policy content or invent a digest.

Rehearsal instead hashes two actual, explicitly chosen fixture files.
This is synthetic evidence scoped only to its independent run-lock and GO,
and it cannot authorize a production Q.

## Law driver and intermediate report

The driver processes the fixed G5 law order, exactly 28 reserved/finished
slots per law. A complete law receives the existing whole-run
`LAW_CHECKPOINT`; no next law begins before it. If the first law completes,
the driver writes `first-law-cost-only.json` with counts, measured/unmeasured
wall/CPU and peak RSS/cgroup values. There are **no predictions, legal
actions, truth labels, routes, statistical inference or scores** in that
report. If some costs cannot be reconstructed, they are marked unmeasured.
`max_laws=1` permits an intentional boundary pause. `STOPPED_*` or
`STARTED_MISSING` stops processing and is surfaced as `RUN_BLOCK` with
Owner decision required; it never skips to the next law.

The gateway constructor is an explicit dependency: rehearsal may use
`synthetic_rehearsal_gateway`; production must supply a separately
reviewed gateway factory. Supplying a gateway is **not** permission to
override production frozen method/policy hashes.

## Verification and remaining review

New `tests/test_r2_m_a_g6_executor.py` uses mock journals and fault
injection for all frozen terminal statuses, reservation-before-restore,
post-reservation crash, cross-scope permit and lock rejection, wrong branch/root,
missing digest references and eng-style Q. A Linux test launches an actual
fresh child with an explicitly **test-only** cgroup stub; this does not
claim a real production cgroup or GitHub rehearsal. The added read-only
Actions workflow shares G6-1's single concurrency group and executes
both R2-M-A and R2-M-ENG regression suites.

Before a real rehearsal or production run, Muse independently validates
the exact PR head, confirms delegated real cgroup-v2 support and remote
custody behavior, and the Owner separately decides whether to create and
activate the relevant GO artifact. This implementation PR is neither of
those decisions. Merge requires another explicit Owner approval.
