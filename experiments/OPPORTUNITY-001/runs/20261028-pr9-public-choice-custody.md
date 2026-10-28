# OPPORTUNITY-001 PR9 — original public pretrial Evidence Capsule custody

id: OPPORTUNITY-001-PR9-ORIGINAL-PUBLIC-CUSTODY-20261028
status: completed_public_origin_engineering_verification; pending_independent_latest_head_review; new_paired_scoring_not_run
updated: 2026-10-28
tags: opportunity, pretrial, provenance, original-bytes, retention, engineering-only, no-scoring

## Objective and precise scope

主対象モジュール：`evaluation / provenance`。既に実行した採点前TRAIN64×B1/B2/B3の**公開action+reason 192件**について、元公式main Actions原本の出典、byte同一性、論理hash、固定方策との一致、公開長期コピーを作成・監査した。ここで得たデータは**実採点・学習効果・能力向上・機会率ではない**。元のEXP-0003A DEV/FINALを再生成・採点せず、新規TRAIN64のpaired OFF/ON試験は0件。

## Official evidence origin and independent observations

| Stage | Verified observation | Meaning / limitation |
|---|---|---|
| Pretrial source | [PR #65](https://github.com/ryonakayama234/DekaSugi/pull/65) merged main commit `c6b01c2a856a989e9b642fbe211cfd195f0e57e3` | Formal source-corrected pretrial; initial faulty PR7 attempt is **not** the authoritative origin despite identical canonical digest |
| Official pretrial | [Actions run #40659741488](https://github.com/ryonakayama234/DekaSugi/actions/runs/40659741488), job `122719482732`, artifact `12803053107` | API confirmed run main push/commit success, job success and artifact ID/name/run linkage |
| Artifact member | `OPPORTUNITY-001-pretrial-public.json`, `27360` original bytes | Only public decisions (no private audit bytes, outcomes or generator-hidden labels) |
| Original member raw SHA256 | `1d08e6c1518d6730e75bfaf3033a00884f7517a7d91c98a5dfff75192aabc433` | **Byte identity**, distinct from logical JSON SHA |
| Canonical payload SHA256 | `8a8625ed86e66b27bef8d09a023172d2adbc9ad0d42c155ab7f137097e2dccb2` | Same method as original `prepare_opportunity_decisions.digest`; identical with independent local zip retrieval |
| Fixed public TaskSpec SHA256 | `bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85` | New TRAIN64 manifest identity, **not** raw decision identity |
| Public retention commit | `0dfe3814547d944519fa7a27fab2446059a4f39b` (GitHub Actions bot on branch) | Original member bytes committed unchanged with [copy](../evidence/pilot-choices-public-v1.json) and [provenance lock](../pilot-choice-lock-v1.json) |
| Capture workflow | [run #40668908541](https://github.com/ryonakayama234/DekaSugi/actions/runs/40668908541), job `122750392890`, source head `db3f70b65028c3d2c4c610d086cffb6a51003930` | Exactly official artifact ID downloaded. Source-first historic 14/new 9 source checks, fixed TRAIN/DREAM replay, synthetic negative tests, raw and canonical verification, push succeeded |
| Independent first retrieval | GitHub connector downloaded the same official artifact ID, ZIP SHA256 `daa2363f746f0d37701b36341887714fb698671ec9fcbb02bf4817b3e6e97cc2` | Supplementary observed downloaded ZIP digest (transport/container); compressed ZIP byte identity is **not** relied on for the member-level lock |

Official artifact remains subject to GitHub expiry `2027-01-26T08:50:55Z`. The public member is now also committed in Git, so the explicit 90-day artifact TTL is no longer the **only** copy. GitHub public Git itself is not immutable or permanent external escrow; the underlying repository and commit can still be deleted or rewritten by authorized actors.

## Captured public-only decision distribution (not scored outcomes)

| Frozen policy | Before-trial ON | Before-trial OFF | Reasons |
|---|---:|---:|---|
| B1 | 9 | 55 | 9 `cost_supported`, 55 `insufficient_on_votes` |
| B2 | 8 | 56 | 8 `cost_supported`, 56 `insufficient_on_votes` |
| B3 | 8 | 56 | 8 `cost_supported`, 56 `insufficient_on_votes` |

Only **1/64** tasks has a different B1/B2/B3 chosen action (also one reason disagreement). This is a property of the **unscored prior choices**, not evidence about which action would be more correct/cheaper. No claims about opportunity rate, missed success, intelligence growth, transfer, or the value of Active Learning follow.

## Evidence quality C01–C09 and negative-control status

| Check | Result | Evidence and limit |
|---|---|---|
| C01 official origin | pass (engineering) | CI captured exact GET run/job/artifact IDs with expected head SHA, status and relation; original artifact download |
| C02 raw original copy | pass (engineering) | Git original member copy SHA matches separately retrieved 27360 bytes, `1d08…` |
| C03 canonical SHA | pass | exact canonical 64×3 payload SHA `8a8625…` |
| C04 64×3 completeness | pass | exact schema, unique 64 opaque IDs, three actions/reasons each, order committed |
| C05 frozen source / skill / policy | pass under pinned source replay | 14-source old byte gate + 9-source new gate precede TRAIN/DREAM-only replay; output identical to original |
| C06 pretrial chronology | pass **for historic pretrial vs *not-yet-executed* actual score** | Source main pretrial execution preceded all new paired scoring (0); any future scorer must independently pin this sealed git commit before executing |
| C07 public/privacy boundary | pass (schema) | public fields only, no third audit original/family/seed/source IDs/score; not a security review of other systems |
| C08 public retention/CI | public copy pass; **independent PR-head review pending** | Git copy and raw digest persist beyond original Actions artifact TTL; CI and exact-head reviewer required before merger |
| C09 no-scoring permissions | pass | source lock unchanged, new lock scoring permission false; private custody/scorer/activation flags false |

Artificial negative test matrix N01–N12 is implemented at [tests](../../../tests/test_opportunity_choice_lock.py). Included: duplicate/removed/reordered IDs, policy/source drift, incorrect reasons, private field and permission injection, strict JSON duplicate keys/nonfinite, original-vs-pretty JSON raw mismatch, official run/artifact mismatch, copy overwrite/lock mutation. **Unit tests validate engineering invariants**; they do not prove unforgeability of the GitHub host or verify private raw third-audit custody. Independent latest-head Codex review and main integration must still be confirmed separately.

## Run transitions and stopping rules

`planned → official_origin_retrieved → raw_and_semantic_verified → retained_public_on_PR_branch` now observed. The engineering state is **public origin verified / reviewer pending**, not `sealed_pretrial_only` until latest-head independent review + full CI + main integration. If any of these fail, retain failure evidence and stop rather than rewrite the original.

A GitHub Actions one-off branch-only workflow was required to download the original GitHub Artifact with authorized Actions read access and safely write the **two public files only** to the development branch. It had a 1st-attempt-only branch guard; it never performed paired scoring. The source is preserved at commit `db3f70b` and workflow run `40668908541`. Remove/retire the branch-specific contents-write workflow from the final main tree after capture; review the source via the pinned commit.

Original EXP-0003A FINAL128 is sealed; no new TRAIN64 paired ON/OFF result exists. **Issue #66** still blocks scoring until non-public third-audit **raw original bytes** have verified restricted GitHub-external custody, a separately reviewed actual scorer and immutable chronology gate, and explicit once-only activation. PR #67 adapter review is independent and not promoted by this work.

## Reproducibility and data provenance

Read-only check once the two public files are present:

```bash
python -m scripts.verify_opportunity_choice_lock --mode verify
python -m unittest tests.test_opportunity_choice_lock -v
```

Source first + same-chooser diagnostic replay (this is **not** independent chooser implementation):

```bash
python -m scripts.verify_opportunity_legacy_sources
python -m scripts.verify_opportunity_generator_lock
python -m scripts.prepare_opportunity_decisions --mode decisions-hash-only --output /tmp/OPPORTUNITY-PR9-replay.json
python -m scripts.verify_opportunity_choice_lock --mode compare-replay --replay /tmp/OPPORTUNITY-PR9-replay.json
```

See [PR #70](https://github.com/ryonakayama234/DekaSugi/pull/70), [Issue #68](https://github.com/ryonakayama234/DekaSugi/issues/68), [method](../pilot-v1.md), [engineering preregistration](../choice-custody-preregistration.md), [ARCH-001](../../../docs/architecture/system.md), [ARCH-002](../../../docs/architecture/contracts.md).
