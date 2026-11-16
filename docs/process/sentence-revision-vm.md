# SENTENCE-REVISION-1 — supervisor VM loader

id: SENTENCE-REVISION-VM
status: proposed
updated: 2026-11-16
tags: sentence-revision, activation, private-custody, synthetic-verification

## Authority and scope

[Owner GO](https://github.com/ryonakayama234/DekaSugi/issues/195#issuecomment-6904747793): one prediction/scoring run on Muse VM after loader audit. Source accepted at3f60aac8, pinned by PR222. Preserve13 source/test/workflow bytes and original source-lock. This loader PR contains no actual package, completed Owner response or production output. Method and verification plan are fixed in [ARCH-002](../architecture/contracts.md) before implementation.

## Input contract

The private directory contains exactly the four named inputs (other custody files may coexist). Three JSON payloads map R01..R04 to cases; State records equal pinned `State.record()`.

| File | Case fields | Probe correspondence |
|---|---|---|
| public-initial.json | intended_case_role, initial_text, initial_examples[{example_id,before,after}] | suffix01/02 →0/1 |
| disclosure-corrections.json | correction_text, correction_example{example_id,before,after}, custody | suffix03 →2 |
| evaluator-only-unseen.json | unseen[{example_id,role,before,gold_after}], optional intended_rule_id/intended_rule_ast | suffix04/05/06 →3/4/5 |
| manifest.json | schema/status/frozen_at/source_pin/files_sha256/choices_sha256/texts_sha256/split/presentation_order/structural_check/structural_note/provenance/custody/official_predictions/official_scoring/production_run | exact externally committed bytes |

Unseen roles are unseen_related, unseen_previous_application, unseen_near_counterexample in that order. Intended-rule ID/AST are ignored, including for normalization/grammar checks/selection. Role revise/confirmation belongs to scoring provenance only. Loader authenticates all manifest bytes and the three file hashes, without inventing algorithms for choices/texts hashes or interpreting unspecified manifest metadata formats. It uses the explicit R01→R04 and example/probe correspondence supplied by Owner; no payload dict insertion order can change it. A changed private format or source mismatch stops; do not edit/reseal the authorized package to make it pass.

## Execution (planned until supervisor audit)

1. Supervisor audits this loader head and verifies the13-file pin/source-lock against PR222. Use a clean checkout of that audited head with Python3.12 and standard library only. No dependency installation is needed. New code: [loader](../../scripts/run_sentence_revision.py), [explicit verification](../../scripts/verify_sentence_loader.py), [invented package/tests](../../tests/test_sentence_loader.py).
2. Keep the four private input files outside the checkout. Directory must be writable to persist its exclusive manifest-named activation latch. Keep package and resulting outputs private; the report and results include unseen gold. Use a separate nonexistent run root outside checkout and outside package. Do not precreate it; loader creates0700.
3. Determine prior cumulative CPU already spent under the adopted budget from preparation/verification/other supervisor records. Pass that observed number explicitly; do not assume zero or grant a fresh7200 seconds. Loader includes fresh interpreter startup, imports/preflight and all remaining work in the same7200s total. This numeric debit is supervisor-supplied provenance, not an independently authenticated budget ledger.
4. Run exactly once **after supervisor audit**. Substitute only the private paths and observed prior CPU number:

```bash
python -I scripts/run_sentence_revision.py \
  --package /private/sentence-revision-fixed \
  --run-root /private/sentence-revision-official-run \
  --prior-cpu-seconds OBSERVED_CUMULATIVE_CPU
```

The CLI has no manifest/hash/source/budget override, synthetic mode or resume option. Official manifest SHA256 is163f11d38827af0c2908ce1d3dc250b11645ad6a509cf8768037f94be7149c06. It rejects synthetic package commitments. `-I` is required; user Python paths and stale pycache are excluded. The unchanged packages bootstrap file is also authenticated before imports.

5. Stdout contains bounded status/cost metadata, never input texts/states/results/gold. Exit0 requires `status=complete`. Any other status exits2. A preflight rejection leaves no run root/latch; diagnose without fetching predictions. Once the package latch exists, every error/interruption consumes activation. A duplicate root or package activation is refused. Do not delete/copy the latch or change the package to retry; report partial state for Owner/supervisor judgment. Local filesystem custody cannot prevent a privileged user deleting/copying the entire package.
6. Authoritative success requires completion.json **and no stop.json**. Verify the completion artifact index before reviewing report.md/results.json. All192 scheduled rows include96 main unseen outputs; retain all four cases and negative/empty/abstain outcomes. stop.json overrides any partial report or results and records saved/indexed rows, last phase and cumulative observed CPU. Missing slots are schedule minus saved rows, never zero scores. Existing score-started.json is the unchanged scorer's once-only latch.

## Output provenance and report

`input-manifest.json` is a canonical copy for inspection; the external manifest commitment still refers to the original private file bytes. `freeze.json` links that commitment, source-lock, current settings/grammar/runtime bytes, public/gold digests and the unchanged schedule. Per-case public and private-disclosure files are separated. All four before seals and all output/snapshot bytes are sealed before the pinned score_batch entry; no incremental scoring.

`frozen-renderer.md` preserves fixed renderer output, whose historic preamble says artificial. `report.md` substitutes only that known preamble with loader mode/manifest provenance; all scored tables/body remain byte-identical. It must be interpreted with completion/stop and the cost-receipt shards. `results.json` uses sentence-loader-results/1 and explicit official_supervisor_vm or synthetic_loader_check mode. No fixed renderer/scorer/kernel source is edited.

One Meter is shared throughout, including result serialization, receipts and completion. Checks use live results, not an empty retained argument. Prior CPU is included; phase60s/check100000/data1MiB remain unchanged. Limits are cooperative retained-data/CPU guards, not OS memory/process isolation. Final caller-visible CPU includes completion persistence; a persisted timestamp cannot include its own subsequent write.

## Synthetic verification ledger

The explicit command is `python scripts/verify_sentence_loader.py --output /tmp/loader-check.json`. It runs only named A/B/C and invented-loader test modules, never broad discovery, actual Owner inputs or production execution. Temporary private packages and artifacts are removed after tests. The internal synthetic test seam cannot label a non-authorized commitment official and is not exposed by CLI. Separate pull-request-only CI uses the same command; all pinned workflows remain unchanged.

Local Python3.12.14 verification: **59/59 PASS, skip0**, A13+B14+C16+loader16. Wall301.220s; parent CPU268.992s plus child CPU31.723s. [Unedited generated receipt](../../experiments/SENTENCE-REVISION-1/evidence/loader-synthetic-20261116.json) records local tested commit and every source hash. [Publication binding](../../experiments/SENTENCE-REVISION-1/evidence/loader-publication-binding-20261116.json) connects it to published source7a378f46: identical Git tree and byte-equal GitHub readback of11 changed files. No source changes followed this test.

Checks cover fixed-orchestrator192-row/snapshot/score equivalence; all13 source and source-lock tampering; manifest and each payload tampering; invalid types/IDs/role/order/states and duplicate JSON/inputs; ignored intended-rule metadata and changed unseen gold leaving predictions unchanged; before-seal disclosure and one all-output score; same/other-root activation refusal and concurrent processes; real final serialization caps for results, cost receipts and completion with live results retained; real depleted lifetime CPU; terminal failure consumption and CLI privacy/no hash override. All13 pinned hashes still match. Documentation123 files and historical14+9-source/old-workflow static checks pass.

Independent supervisor loader audit and exact-head CI/review are tracked in Draft PR224; these local synthetic results are not supervisor acceptance. No official package has been loaded and no official execution has been performed by Lead.
