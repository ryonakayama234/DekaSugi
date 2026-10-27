# EXP-0003A — Run index (PR3 TRAIN/DREAM engineering; DEV/FINAL not run)

id: EXP-0003A-RUNS
status: PR3 TRAIN/DREAM engineering merged on main; PR4 pre-DEV freeze under review; no DEV/FINAL outcomes
updated: 2026-10-26
tags: exp0003a, run-index, preregistration, evidence

## 状態
- PR1: [plan-v1](../plan.md)、[spec](../../../docs/specs/EXP-0003A.md)、[ARCH-001](../../../docs/architecture/system.md)、[ARCH-002](../../../docs/architecture/contracts.md)、[UI map](../../../docs/architecture/ui-panels.md)の設計のみ。
- **PR2完了時点の履歴**：`TRAIN`160問をWAKE/SLEEPで実行し、GitHub Actions Artifact `EXP-0003A-TRAIN-engineering` に記録。当時は`DREAM`: not_run、方策Snapshotなしだった。**PR3の現行状態は後述の行が正本**。EXP-0003A `DEV`/`FINAL`は引き続きnot_run。
- 初回PR CI [#40242971478](https://github.com/ryonakayama234/DekaSugi/actions/runs/40242971478) は成功（55 unit tests、既存回帰、TRAIN160実行）。[Artifact 12618215378](https://github.com/ryonakayama234/DekaSugi/actions/runs/40242971478/artifacts/12618215378) に初回TRAINのJSON証拠を保持。初回WAKE結果: 監査付き成功120、not_found40、監査不合格0、予算枯渇0、SLEEP候補2。**これはPR2途中の工程診断であって、最新版headの最終証拠ではない**。最終headではappend-only JSONLも同Artifactへ保持する。
- TRAIN初回の結果は技能候補の発見可否の工程診断であり、H2/H3の性能検証ではない。候補0件・監査不合格・run異常を失敗のまま保存し閾値やseedを変更しない。
- 今回のCIで既存のEXP-0001/0002/0002B回帰が走っても、それをEXP-0003Aのrunと呼ばない。
- Codex再レビューでP1×2（エピソードAST差し替え・監査元レコード不保存）、P2×1（generator/SLEEP CPU/wall未計測）を検出し、PR #33を一度Draftに戻した。合意済み修正は、監査器所有の`WakeReceipt`原本照合、TRAINの第三例・公開TaskSpec・出典対応を評価器用別ファイルで保全、生成器/SLEEPのCPU/wall計測。現行のTRAIN成果はreview/CIゲートを再通過するまで暫定証拠である。
- PR3 [Issue #34](https://github.com/ryonakayama234/DekaSugi/issues/34) / [PR #35](https://github.com/ryonakayama234/DekaSugi/pull/35): DREAM pool512からB2 fixed random96、B3 near-positive96を各family12選択。TRAIN160の独立OFF/ON paired観測と合わせB1/B2/B3の独立snapshot hashを保存。CI Artifact `EXP-0003A-PR3-TRAIN-DREAM`には公開run JSONと評価者専用raw trial/監査例/候補プールを保存。**PR3ではEXP-0003A DEV/FINALを生成・採点しない**。選別と方策の学習自体はH2/H3の性能優位を示さない。CI/runの確定SHAは検証後に記録。
- PR3品質監査: 最新CI [#40307790699](https://github.com/ryonakayama234/DekaSugi/actions/runs/40307790699) でunit62件・TRAIN/DREAM工学実行は成功。前回Artifact [#12642659210](https://github.com/ryonakayama234/DekaSugi/actions/runs/40307790699/artifacts/12642659210) はpool512、B2/B3各96、監査付き費用削減TRAIN正例20件、B1/B2/B3 snapshot生成を確認。ただしそのコミットではWAKE行の輸送順でsemantic snapshot hashが変わるP2が残存したため、**正式freezeや最終headのhashとして使わない**。PR3のP2修正はWAKEと出典を公開task ID順で正規化し、Dreamの選別順は保持。修正版headのCI/ArtifactとCodexレビューを採用すること。
- PR2以降の各作業は専用の不変run記録とCI SHAを追記し、`planned` / `engineering` / `confirmatory`を区別。失敗も保存。
- FINALはplanの事前固定・source/data/snapshot freeze・独立レビュー・人間による一度限りの実行承認より前に開かない。
- 生Artifactは保存期間・ZIP/JSON SHAと長期アーカイブの有無を明記。EXP-0002Bの既存FINAL Artifactの期限は2027-01-23であり、新研究のデータと混同しない。

Related: [preregistration](../plan.md) / [previous FINAL](../../EXP-0002B/runs/20261025-final112.md).

## PR4 source/data/policy freeze (Issue #36; PR development)
- PR3は[PR #35](https://github.com/ryonakayama234/DekaSugi/pull/35)をmain `55af90d6f1eea11404efef358e4819b63928907e`へ統合済み。[post-merge CI #40319898724](https://github.com/ryonakayama234/DekaSugi/actions/runs/40319898724) SUCCESS (unit62件、TRAIN/DREAM工学実行、旧EXP-0002B DEV smokeのみ)。[TRAIN/DREAM Artifact #12648672302](https://github.com/ryonakayama234/DekaSugi/actions/runs/40319898724/artifacts/12648672302) にrun raw証拠を保存。PR3 snapshot SHA: B1 `3b4fc00f8ad0fe2f1cc0978886d7bc7a6285ed002c842ceeb0106fd51ee5afd4`, B2 `01d5595e1b4c32d200e2734630f38a848e77a64f356741445e011865834f5af7`, B3 `a6d46ab5dd697e8e90789693fdd3bd67bbca445ec07bc8b119401e1c0cf1e210`。工学的根拠のみ、H2/H3の確証ではない。
- [Issue #36](https://github.com/ryonakayama234/DekaSugi/issues/36): PR4は前工程の凍結準備。TRAIN160/DREAM512とのfull record一致 + DEV64/FINAL128のhash-only生成・4split 864件の公開ID/seed衝突検査、全source blobとB1/B2/B3 snapshot・選別順序SHAをまとめる。`freeze-v1.json`をコミットするまでは`preflight`は**候補**であり凍結完了とは呼ばない。DEV/FINAL scoring = not_run。後続DEV診断・FINAL一度限り採点は別ゲート。

## Freeze-v1 preregistered hash lock pinned (2026-10-26; pending PR4 merge)
- 完整な[freeze-v1.json](../freeze-v1.json)をPRE-DEV研究用にピン留めし、[初回preflight CI #40321644523](https://github.com/ryonakayama234/DekaSugi/actions/runs/40321644523)と[凍結照合CI #40321874173](https://github.com/ryonakayama234/DekaSugi/actions/runs/40321874173)で**68件のunit全成功、preflight/check-freeze双方成功**。工学記録[Artifact #12649706107](https://github.com/ryonakayama234/DekaSugi/actions/runs/40321874173/artifacts/12649706107) (2027-01-24T12:21:12Z失効予定)を保存。こちらは最終レビューヘッドではなく、レビュー完了とCI後に最終結果をIssueに追記する。
- immutable `freeze_payload_sha256=1e0f6daf1cb80262c187c60a3e0a4d2e76dafea911f0633feed3c40f93db8f44`、全4分割 `dataset_sha256=491e1b930d363c2550ba756f45e88a1873784a22eb503216b04c4e43b2278e49`、14ソースGit blob manifest `b007533bd1f06f37b740d8f05df463915a8f03cef61cff32fc4b7c92bce91394`。
- DEV64/FINAL128は参照例生成による**データhashだけ**、未採点。独立学習結果B1/B2/B3のsemantic SHA、B2/B3選択順序は[freeze-v1.md](../freeze-v1.md)およびJSONが正本。PR4後もDEVの工学的診断は別ゲート、FINALは別途人間承認まで保留。

## Review P1: source-first validation and repinning
- [PR #37](https://github.com/ryonakayama234/DekaSugi/pull/37)のreviewで発見したP1は、凍結hashの検査より先にTRAIN/DREAM処理が実行されること。`verify_frozen()`をJSON自己hash・schema・Python環境・14 source byte SHAの照合を先に行う順序に修正。未承認ソースでは`preflight_record()`を呼ばないnegative testを追加した。
- 上の`freeze_payload_sha256`とsource manifest SHAは**P1修正後の再固定値**である。初回commitの旧source hashは正式freezeとしない。新候補証拠[CI #40352073490](https://github.com/ryonakayama234/DekaSugi/actions/runs/40352073490)は旧凍結ファイル不整合でunitが意図通りFAILした時のpreflightのみであり、再固定後に別途all-pass CI/レビューが必要。


## PR5 independent DEV engineering evaluator — planned, NOT RUN (2026-10-27)
- [Issue #44](https://github.com/ryonakayama234/DekaSugi/issues/44) /
  [new spec](../../../docs/specs/EXP-0003A-DEV-EVALUATOR.md) /
  [engineering protocol](../dev-evaluation-pr5.md).
- Evaluator implements source-first freeze, B0/B1/B2/B3 pre-search public
  chooser, independent audit/meter and write-once reports in a new separate
  module. PR CI may test synthetic/TRAIN only; **DEV64 not_run; FINAL128 not_run**.
- Future DEV record requires exact source SHA, full raw artifact bytes SHA,
  run URL, private manifest hash, independent recomputation and stated
  failure/invalid/inconclusive counts. No forward revision of old run reports.

### PR5 review gate correction (2026-10-27)
Addressed two P2 code review findings in evaluator-only timing contract:
complete frozen asset loading (two TRAIN/DREAM replays) and per-arm B1/B2/B3
inference CPU/wall. Tests run TRAIN only; DEV64/FINAL128 remain **not_run**.
Latest evidence is PR CI, not a held-out experimental result.

## DEV64 activation attempt (Issue #46; source-gated trigger PR)
- [Activation contract](../../../docs/specs/EXP-0003A-DEV64-ACTIVATION.md):
  new one-shot main-only workflow, explicit source-commit marker and first run
  attempt; **never run DEV in PR CI**.
- Public original JSON, evaluator-private raw provenance, separate independent
  audit output, original-byte SHA256SUMS and runner metadata will be uploaded as
  a 90-day Actions Artifact on the scored main-push job.
- Record run ID/main SHA, both exact raw JSON SHA-256, verified DEV dataset hash,
  B0/B1/B2/B3 audited correctness/call/CPU and B2−B3 regressions in an immutable
  follow-up run record. Artifacts are not permanent archives; preserve long-term
  evidence with an independent reviewed evidence PR.
- At trigger PR stage: **DEV64 not_run; FINAL128 not_run**. PR success must
  never be mislabeled as scored experiment.

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

## EXP-0003A DEV64 scored once — evidence correction pending (2026-10-27)
- Actual original [job #40518246537](https://github.com/ryonakayama234/DekaSugi/actions/runs/40518246537)
  **scored** 64 tasks × four arms on main `26eaf3b4`. Its **independent
  audit failed** because of last-bit CPU/wall rounding; the original job
  remains FAILURE. All raw public/private bytes and SHA256SUMS were retained
  as [Artifact #12739684056](https://github.com/ryonakayama234/DekaSugi/actions/runs/40518246537/artifacts/12739684056).
- [Immutable result/retention ledger](20261027-dev64.md) records observed
  outcomes, exact original hashes, audit-only readout gate and restricted
  archival obligation. This **supersedes the historic** "DEV not_run" headings
  above without changing their original historical text.
- No scorer rerun; FINAL128 remains not_run.
