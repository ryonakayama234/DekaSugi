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
- immutable `freeze_payload_sha256=e6c44802938ff4c9975a4aaae72e1f1c2cbad0dc3bff904bdb67d7f65e3d0262`、全4分割 `dataset_sha256=491e1b930d363c2550ba756f45e88a1873784a22eb503216b04c4e43b2278e49`、14ソースGit blob manifest `860d787dba517b2339bf8a0aca78377cc5c41d6ca18375dfd698a2821290929a`。
- DEV64/FINAL128は参照例生成による**データhashだけ**、未採点。独立学習結果B1/B2/B3のsemantic SHA、B2/B3選択順序は[freeze-v1.md](../freeze-v1.md)およびJSONが正本。PR4後もDEVの工学的診断は別ゲート、FINALは別途人間承認まで保留。
