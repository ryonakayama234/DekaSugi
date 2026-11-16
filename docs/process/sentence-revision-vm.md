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

Implementation and synthetic evidence will be added next. No official execution has been performed by Lead.
