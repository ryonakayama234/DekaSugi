# WORLD-LEAN-1-ORDER-FREEZE-20261112-03 — six-demo engineering order and source-lock proposal

updated: 2026-11-13
tags: world, lean-editor, freeze, implementation, fixture

id: WORLD-LEAN-1-ORDER-FREEZE-20261112-03
status: REPAIRED_SYNTHETIC_ONLY / SOURCE_DIGEST_LOCKED / SUPERVISOR_REAUDIT_PENDING
source_design: WORLD-LEAN-EXPERIMENT-DESIGN-20261112-03 (two-text-erratum-only copy of adopted -02); resumption pending
supervisor_reference: PR #208 comment 6823583705, AGREE / RQ1–RQ3 agreed

> This is a bit-specific implementation and order contract, not an experiment GO.
> Source bytes are identified by `WORLD-LEAN-1-SOURCE-LOCK-20261112-03.json`.
> Its `source_digest` and exact lock-file hash are also bound by the executable
> manifest. The order is excluded from that source list to avoid a circular hash;
> the manifest separately pins this order's bytes. The repair receipt records both.
> Old -01/-02 locks and orders remain unchanged. No official seed is made here.

## -03 precedence and stage order

The [repair specification and complete constant table](WORLD-LEAN-1-REPAIR-20261113-03.md)
define the exact new transport, artifact and stage contracts. Existing learner
ordering below remains unchanged except the demo index range is uniformly
`range(DEMOS_PER_LAW)`, including the unbranched partition. The canonical single
numeric source is public `packages/world_lean/protocol.py`; the evaluator re-exports it.
FULL acquires ASTs; independent STATIC-RANK/LOOKUP training retains public frequencies/
episodes but no persistent acquired AST. OFF receives literal FULL bytes.

Manifest fixed → authorized evaluator seed generation → private materialization →
ALL snapshots fixed → ALL queries evaluated in fresh public-only children →
complete-schedule exact analysis. Missing commitments/barrier/data fail closed.
Authorization must bind supervisor re-audit, Owner resume, source and manifest.
No official command is run in this round; only explicit synthetic TRAIN fixtures.
The main/extra public token alphabets are decoded by their supplied ordered token
sets to internal opaque identities; numeric or Unicode label ordering is never a prior.
Observational primitive counters and legal action logging do not select candidates.

## Typed and canonical runtime

- 4 symbols are opaque identities A/B/C/D inside `lean-editor/1`; the 11 named
  atom types are kept, with 4 INSERT choices (14 concrete tokens). Buffer and
  clipboard are tuples length ≤16. Cursor is an insertion boundary; selection
  is `none` or `(anchor,head)` with `cursor=head`; empty selection is distinct
  from none but has no replacement range. A selection's replaced range is
  `[min(anchor,head),max(anchor,head))`.
- MOVE_LEFT/RIGHT clears selection even when cursor is at an endpoint; when
  active, EXTEND moves the head and cursor only; COPY nonempty copies the
  selection without clearing it; CLEAR_SELECTION preserves cursor; DELETE
  nonempty removes the selection and places cursor at its minimum boundary.
  Overflow INSERT/PASTE is an atomic four-field no-op. All normal no-ops cost
  one primitive call. Invalid tokens, malformed state/AST and over-budget
  programs FAULT, never silently repair.
- `finish` is a protocol event, not a 12th edit atom. End success is checked
  exactly once against buffer, cursor, selection **and** clipboard on finish or
  the 12th primitive. Intermediate target equality does not stop the episode.
  Only the parent evaluator may supply a target to its session scorer.
- AST arrays have tags OP, SEQ, IF, CALL; symbol terms are `SYM` and `READ`,
  predicates EQ/NE on typed READs. Bound read terms are `cursor,prev,next,first,last`;
  out-of-bounds returns none, and an INSERT of an undefined read faults.
  Normalize only by recursively flattening associative SEQs and eliminating
  a one-child SEQ; no semantic or task-dependent simplification. No unordered
  set/dict iteration is a tie-breaker.
- Canonical bytes: UTF-8, ASCII-escaped JSON, sorted object keys, compact
  separators, LF terminator, no NaN. Ties use canonical **bytes** ordering.
  SHA-256 is lowercase hexadecimal. Syntax and call-expanded AST both have
  ≤32 nodes and depth ≤6; execution expands ≤12 primitives. CALL cycles and
  missing dependencies fail closed; expansion and primitive costs remain visible.

## Learning update total order (the experiment has no hard-coded p/d catalog)

1. Start with **empty** learned predicate, macro, graph and schema inventory,
   while leaving the documented trusted primitive semantics and typed READ/IF
   interpreters available. TRAIN receives one 8-operation public trace block at
   a time; no-op observations are retained. Exactly every 64 primitive events,
   at most 64 updates through b=4096, perform an update. No update at b=0.
2. From the last 8 public blocks in event order enumerate per-block **all**
   half-open windows `[i,j)` of lengths 2..6, with `i=0..7` and `j≤8`.
   Group by ordered atomic operation *names*, with group keys sorted as Python
   ASCII tuples. Within each group pair windows from distinct blocks using
   increasing right index `j`, increasing earlier index `i`; consider at most
   **1024** constructions per update, inclusive of graph constructions below.
   No dictionary/set iteration chooses an order.
3. Each paired window is anti-unified left-to-right. Non-INSERT operation names
   must agree. For INSERT, choose the first of the five fixed READ terms that
   evaluates to each observed insertion symbol at the corresponding pre-step
   state in *both* windows. If none matches, retain a literal SYM only if
   both inserted symbols are identical. Otherwise reject the window pair.
   Normalize the resulting SEQ and deduplicate by canonical bytes, retaining
   the earliest witnesses. The witness list consists of two SHA-256 trace
   interval digests and the enclosing source window digest. This requires
   two distinct observed episodes; demo goals cannot create a macro alone.
4. Sort constructed ASTs by `(canonical byte length, canonical bytes)` and
   attempt at most **128** fresh candidate validations. Each is checked on
   the **last episode's six public TRAIN demos**, not an evaluation query.
   Its rank is `(six-demo mismatch count, serialized macro+CALL byte length,
   canonical AST bytes)`. A reusable macro is retained only if a CALL is
   strictly shorter than its inline AST, with max **64** active library entries.
   The source digest, constructor ID, witnesses, dependencies and
   counterexample record accompany every acquired entry; no candidate is
   called discovered at zero events.
5. Predicate candidates are all unordered pairs of distinct terms among
   `cursor,prev,next,first,last` wrapped as EQ (10 candidates), sorted by
   canonical bytes. Only predicates that split both sides of the most recent
   TRAIN demos are considered for acquired graphs. For learned macro IDs in
   canonical order, try distinct ordered pairs as IF branches. The graph
   constructor counts against the remaining 1024 constructions and 128
   verifications *in that update*. Store only six-demo-consistent graphs,
   with explicit macro dependencies. No completed p0..p3, d0..d3, or
   SELECT_BRANCH graph is preinstalled in the learned library.
6. On new matching observable action-name windows, replay retained macro ASTs
   against observed interval transitions. Any mismatch becomes an archived
   counterexample and revokes the candidate; recursively invalidate dependent
   CALL graphs. After updating/revoking, sort by rank then ID and retain at
   most 64 active entries; recursions/invalid references never survive.
   Revoked entries remain in a separate auditable history, not active search.
7. Snapshot is canonical JSON of public episodes, integer constructor/read
   frequency counts, active library, revoked archive, update receipts and b.
   Identical bytes are supplied to FULL and OFF. OFF forbids *all* acquired
   CALL expansion, including indirect calls; neither arm may receive the
   evaluator target, recipe, seed, hidden phase or success feedback at USE time.

## USE candidate order (the 128 checked candidates)

**-02 dependency**: each law supplies six ordered public input→final-state pairs (three true then three false, labels withheld); predicate partition index domain is 0..5. Candidate verification is six demos ×12 primitives ≤72 per candidate, not the prior four ×12. LOOKUP uses six-by-six demo matching. No candidate order, tie-break, search cap or world semantics changed.

1. Six public input→final-state demo pairs, in supplied array order, are the
   only target evidence. Construct candidates from generic primitive/typed-read
   grammar and one-branch IF scaffold. At a given body search state, possible
   atoms are all non-INSERT types; legal read-derived INSERTs; and literal
   INSERTs for A/B/C/D, sorted by canonical bytes. No operation macro is
   handcrafted to solve a recipe.
2. Body synthesis is a 6-level beam of width **8**, with at most **1024**
   attempted one-step grammar edges **per source demonstration/body search**.
   Discard state-preserving edges only from *constructor search* (the world
   itself still charges no-op). Deduplicate states by their canonical four-field
   bytes, preferring `(guide tuple, program length, program canonical bytes)`.
   Guide tuple is the fixed integer expression in `learner._guide`: symbolic
   clipboard positional mismatch weighted 20, buffer positional mismatch
   weighted 3, cursor absolute distance, selection-prefix shaping `8+6*n`,
   and a 3-unit uncleared-selection penalty after clipboard match. This is
   an open public-demo-guided search heuristic; no query target is used.
3. First attempt unbranched bodies derived from the first demo and verified
   on all six. Next iterate EQ predicates in canonical order, retaining only
   nonempty true and false demonstration partitions; for each partition,
   derive body candidates from its first demo, require agreement on every
   member, and take up to eight bodies in canonical order. FULL may also offer
   acquired CALL macros in the branch body set, if those public examples fit.
   Build ordered IF pairs from the same body grammar. OFF/STATIC-RANK cannot
   propose learned CALLs. Every proposed candidate remains a typed bounded AST.
4. Deduplicate whole ASTs by canonical bytes. Before the 128-verification
   cap, FULL and OFF preselect by `(byte length, canonical bytes)`. STATIC-RANK
   instead preselects by `(-sum TRAIN constructor/read integer frequencies,
   canonical bytes)`, where frequencies are accumulated only from shared
   public TRAIN observations. STATIC-RANK's fixed IF scaffold and direct
   grammar can express the same branches and bodies without persistent
   learned ASTs. No baseline can invoke a concealed acquired AST.
5. For each of at most **128** preselected candidates, simulate up to six
   demo states with at most 12 expanded primitive calls each. Rank checked
   candidates by `(mismatch count, canonical byte length, canonical AST bytes)`.
   Choose the first zero-mismatch candidate. Otherwise ABSTAIN. Query state
   is then executed exactly once up to 12 expanded primitives. Cost logs
   include checked count, constructed edges, primitive simulations, rejected
   candidates and whether acquired CALL was actually used. A legal prediction
   is **not** shown its target or correctness at evaluation time.
6. LOOKUP has no 128-trace memory reduction. For 16 buffer slots, 16
   clipboard slots and cursor/anchor/head fields (35 slots), symbol mismatch
   is 0 or 1; numeric positions use absolute difference; a none-vs-integer
   position difference costs 16. Choose the minimum public six-demo distance
   TRAIN law, ties by opaque public tag. Within that law select the nearest
   successful TRAIN trace to query initial state, ties by public input digest.
   A recorded INSERT can rebind only from a matching observed READ; otherwise
   its recorded literal is used. Without any success in the selected TRAIN
   law, ABSTAIN. No threshold, predicate graph or dynamic success lookup.

## Accounting and replay boundary

Formal design constants remain unchanged: TRAIN24 / planned holdout24;
16 paired realizations; 4 arms; b=(0,512,1024,2048,4096);
6 demos, 48 main queries per realization, final extra 48; 12 primitives;
64 stored candidates, 128 verification candidates, 1024 update construction
attempts; ≤252,928,000 design-maximum primitive transitions;
48h wall / 36h aggregate CPU / 2GiB saved bytes.

Scientific analyzer uses exact rational, 5-checkpoint *b-width-weighted* AULC,
16 paired-seed sign tail `2517/65536` at 12 wins, seed-level bootstrap exactly
9999 paired resamples, Mersenne Twister seeded integer, and the exact
linear `(N-1)*q` 2.5/97.5% percentile endpoints. The joined three-contrast
AND plus final, groups, ambiguity and usage gates are fixed by design;
no post-hoc threshold changes. Some source-path bookkeeping and foreign runtime
metadata are deliberately excluded from byte-equivalence commitments.

**Target replay patch**: CPython 3.12.12, Linux/WSL2 stdlib only, one worker.
**Available local repair fixture patch**: CPython 3.12.14, Linux. CI pins 3.12.12. Cross-patch
byte/replay equality and wall/CPU cap on the target runtime are NOT CERTIFIED.
The six-demo source-lock is a deterministic code commitment, not an approval to score.
Only its synthetic TRAIN fixture counterpart runs here. The official secondary
diagnostic remains NOT_RUN pending supervisor re-audit and Owner resumption.

## Stop and audit gate

The CLI now implements `freeze-manifest`, `formal-generation`, `formal-run`,
`synthetic-dry-run` and `fixture-gate`. Formal entrypoints refuse absent/mismatched
external supervisor re-audit and Owner resume references; exact runtime/code/manifest
must match. There is no CI official activation. Generation/run roots are once-only;
artifacts use exclusive creation and fsync. Aggregate resource stops and integrity
failures never become complete scientific results. See repair specification for
actual stage contract and synthetic profile dimensions. This submission stops
before any formal seed, formal holdout materialization or official evaluation.
