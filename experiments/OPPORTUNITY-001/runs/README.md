# OPPORTUNITY-001 — Run ledger

id: OPPORTUNITY-001-RUN-INDEX
status: not_run; design_only; no_implementation
updated: 2026-10-28
tags: experiment, opportunity, provenance, planned, not-run

## Current status
- 本研究は測定対象・仮説・アーキテクチャ・データ契約・事前登録**案**の設計段階。生成器・paired試行器・分析器は未実装。
- TRAIN/DEV/FINAL、メータ校正、新しい二択試験、学習、確証評価は **0件 / not_run**。
- この目録には新しい結果・改善の証拠・性能数値は存在しない。POLICY-DIAG-001の過去DEV64とMETRO CAL-01の人工fixture結果を再利用して新しい効果を主張しない。
- 事前登録数値・seed・新規母集団はreview/freeze前のproposal。凍結の新しいcommit以降だけ実験を許す。

## Future run record contract (not executed)
各run: immutable run_id、phase、exact command、Git source commit + blobs、Python/OS/CPU、generator/skill/policy/verifier/meter SHA、public split hash、private manifest checksum（非公開）、生証拠hash、全arm母数、監査判定、missing/invalid/non_comparable、calls/candidates/CPU/wall費用、区間・代替説明、独立レビューと採否。

## Safeguards
- PR CIはsynthetic/TRAIN-fixtureのみ。元のEXP-0003A DEV64や封印されたFINAL128を起動しない。
- private audit第3例・generator source records・secretは公開リポジトリへ書かない。
- 失敗や欠測も不変の独立run記録として保存する。

Related: [plan](../plan.md) / [spec](../../../docs/specs/OPPORTUNITY-001.md) / [Issue #56](https://github.com/ryonakayama234/DekaSugi/issues/56)。

## PR2 synthetic-fixture calibration scope
- 工学校正専用 `packages/evaluation/opportunity.py` および `tests/test_opportunity_fixture.py`。意図的に作成した分類用fixtureであり新規研究の生成課題ではない。
- 新しい研究用TRAIN/DEV/FINALの試行・採点は **0件 / not_run**。独立原証拠監査や一般化性能の証明ではない。
- CIと独立レビュー結果は完成後に追記記録。将来のmethod freeze、actual-evidence adapter、fresh holdoutは未着手。

- [2026-10-28 PR2 synthetic fixture CI/review calibration](20261028-pr2-fixture-calibration.md): completed_engineering_calibration_only; not_scientific_result. No new study TRAIN/DEV/FINAL trial.

## OPPORTUNITY-001-PILOT-V1 (new TRAIN-only; pre-measurement)
- [Frozen pilot METHOD](../pilot-v1.md): exact new generator specification, 64 TRAIN tasks, fixed skill/policy/budget, pretrial evidence and stop conditions.
- Actual source/manifest freeze, implementation and scoring status: **not_run**. Pilot has not produced any task-level outcome or learning gain; old DEV/FINAL unchanged.

## PR4 source generation / hash-only preflight
- New `packages/evaluation/opportunity_pilot.py` and `tests/test_opportunity_pilot.py` implement fixed PILOT-V1 generation and public-only SHA preflight. No actual paired trial/measurement; source and manifest freeze pending.
- After exact-head CI and independent review, preserve preflight hash, source SHA and environment in separate immutable provenance record. Research outcomes remain **not_run**.

## PR5 independent source-only preflight
- `scripts/audit_opportunity_pilot_public.py` recomputes expected public SHA and commits to third audits **by digest only**, without importing generator/scorer. CI tests and hash-only CLI are the engineering scope; no new paired trials and no raw private original artifact archival claimed.
- Record observed digest, source Git blob SHA and Python version in a later immutable generator lock only after CI/independent review. Scientific status remains `not_run`.

## PR6 generator source freeze, no new scored run
- [Source/policy/public manifest lock](../pilot-generator-lock-v1.json) and [read-only verifier](../../../scripts/verify_opportunity_generator_lock.py) bind the exact source bytes and legacy frozen skill/policy identity. This step is **source-only** (both scoring permissions false), not a research effect measurement.
- Evidence origin: [PR #63](https://github.com/ryonakayama234/DekaSugi/pull/63) latest-reviewed head `3f90466babfef29b42b5fdda69ba7b043da5c66f`; [CI run #40622827537](https://github.com/ryonakayama234/DekaSugi/actions/runs/40622827537) source SHA and independent third audit commitment. New TRAIN/DEV/FINAL scored rows: **0**.

## PR7 policy pretrial public choice artifact (not scored)
- [Pretrial-only chooser](../../../scripts/prepare_opportunity_decisions.py) / [read-only CI workflow](../../../.github/workflows/opportunity-pretrial.yml) materialize exactly 64×3 B1/B2/B3 decisions before pairing, without private audit, source family or outcomes. A separate main commit will pin resulting public decision manifest SHA before any actual trials.
- Source freeze [pilot-generator-lock-v1.json](../pilot-generator-lock-v1.json) remains intact and declares actual scoring false. Scientific state `not_run`.

## PR7 initial pretrial boundary error (explicitly retained)
- Initial PR7 code head `7d1e74f`, CI [run #40649096613](https://github.com/ryonakayama234/DekaSugi/actions/runs/40649096613): public pretrial payload SHA `8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2`, paired new TRAIN trials 0, no old holdout scoring. **However it regenerated old DEV/FINAL reference tasks via legacy freeze preflight**, contrary to stricter new protocol. Hence SHA is rejected as an authoritative pretrial seal; do not use it to authorize paired work.
- Remediate and reexecute pretrial under stdlib legacy source-gate + TRAIN/DREAM-only policy reconstruction and independent exact-head review. All actual new TRAIN paired trials are still 0.

## PR8 audited-tuple normalizer (draft; no experimental run)
- Pure `packages/evaluation/opportunity_actual.py` + synthetic adversarial tests; no task execution, no actual paired trial/assessment, no old DEV/FINAL access. New TRAIN=0, DEV=0, FINAL=0.
- Gate checks: strict SHA/redaction, search/program/status coherence, canonical positive `by_op` breakdown and sums, fixed 4/100 budgets, equal public task identity, correctness before cost, missing/unknown not imputed.
- Real-audit source identity, before-trial decisions and restricted original-private-evidence retention remain independently blocked. PR #65 requires final review; a distinct source-first one-shot scorer and independent recount are future work. [Contract](../../../docs/specs/OPPORTUNITY-001-REAL-ADAPTER.md) / [Issue #66](https://github.com/ryonakayama234/DekaSugi/issues/66).

- PR8 Codex P2 AST hardening: synthetic negatives for noncanonical/private solved AST and expanded node-budget overflow; positive canonical primitive and frozen-macro AST fixtures. No research trial was performed for these tests. Review/CI gate applies to exact PR head.
