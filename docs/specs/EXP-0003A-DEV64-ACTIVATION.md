# EXP-0003A DEV64 — reviewed main-only one-shot activation
id: EXP-0003A-DEV64-ACTIVATE
status: activation_pr; dev_not_run; final_sealed
updated: 2026-10-27
tags: exp0003a, dev64, independent-audit, one-shot, provenance

## Authority and constraints
User delegated DEV64 engineering measurement under [Issue #46](https://github.com/ryonakayama234/DekaSugi/issues/46).
This does **not** authorize EXP-0003A FINAL128 scoring, H3 claim, policy or skill
retuning, promotion, or changes to [plan-v1](../../experiments/EXP-0003A/plan.md)
or [freeze-v1](../../experiments/EXP-0003A/freeze-v1.json).

## One-shot state transition
1. PR contains workflow and independent stdlib auditor. PR CI is synthetic/
   TRAIN-only; workflow is push-to-main-only.
2. Exact PR HEAD CI and independent Codex review must complete with P0/P1/P2
   resolved, prior to squash merge with subject beginning exactly
   `EXP0003A-DEV64-ONE-SHOT-ACTIVATE`.
3. GitHub main push with the workflow path changed triggers job; require first
   run attempt, main ref and exact source SHA. No dispatch, PR or retry path.
4. Save attempt ID + GitHub commit + Python/OS/processor before score.
   Run docs, unit suite and immutable freeze check first. Abort on failure.
5. Execute `python -m packages.exp0003a_dev --mode dev` with approved
   environment **only** on this guarded main job; it rechecks all frozen source
   and policy hashes before generating 64 DEV cases. FINAL is never accessed.
6. Audit 64×4 public/private records independently without importing scorer
   or rerunning holdouts. Recompute paired B2−B3 effects, family/OOD counts,
   trace/meter alignment, raw dataset/task/audit/snapshot IDs and CPU ledger.
7. Save `attempt.json`, `precheck-freeze.json`, `public.json`,
   `public.evaluator-private.json`, `independent-audit.json` and
   `SHA256SUMS` as 90-day Actions Artifact; print exact SHA and summary to
   the job log; do not overwrite existing files.
8. A separate later evidence archival PR preserves reviewed run metrics
   and hashes in repository. Loss or expiry of 90-day original raw Artifact
   must be disclosed, not described as permanent reproducibility.

## Failure and epistemic rules
No automatic rerun after partial scoring, source/hash mismatch or audit FAIL.
Preserve attempt evidence and stop; determine subsequent actions from observed
failure and a new review, never selectively repeat DEV results. A reproducible
paired DEV advantage is *engineering diagnostics*, not independent FINAL
scientific acceptance. B3>B2 is not presumed and false solved, not_found,
OOD false ON and tail regressions must be disclosed.

## Useful links
[Architecture](../architecture/system.md) /
[Data contract](../architecture/contracts.md) /
[Run index](../../experiments/EXP-0003A/runs/README.md) /
[PR5 evaluator](EXP-0003A-DEV-EVALUATOR.md).

### Independent Codex P2 review hardening (2026-10-27)
- Each primitive meter's `by_op` canonical positive counters must sum to
  `primitive_invocations` (not just agree with copied top-level total).
- Check search status/solved/program/selected AST against audited_correct and
  false_solved, including consistent unsolved/null-program outcomes.
- Verify BOTH evidence source_commit values match the externally supplied
  40-character runner `GITHUB_SHA`; attempt must match main/first run/SHA.
- A finalization step with `always()` hashes **all extant** original JSON
  into SHA256SUMS even if scoring, preflight or independent audit fails.
- New negative and positive synthetic evidence tests run in PR CI. No DEV/FINAL
  generation/scoring may be performed before reviewed main activation.

## Post-activation correction: original evidence audit-only (Issue #48)
The one-shot DEV64 job is irrevocably used: 64×4 scoring completed on main
`26eaf3b4`; independent audit CI failed on binary64 clock aggregation.
Do not repeat the scored workflow. Fix the independent read-only auditor's
CPU/wall-only tolerance, review the change and use a distinct main-push
**audit-only** workflow over exact original Artifact `12739684056`.
Preserve failed run as failed; derive new audit SHA separately. No private
raw records in the public source repository. FINAL128 stays sealed.
