# EXP-REP-001 G1-C — synthetic engineering receipt
id: EXP-REP-001-G1C-20261101
status: ENGINEERING_CI_VERIFIED; NO_FORMAL_TRAIN; NO_DEV; NO_FINAL
updated: 2026-11-01
tags: experiment, synthetic, rank-control, security
parent_issue: https://github.com/ryonakayama234/DekaSugi/issues/126
source_branch: research/rep001-g1c-controls
source_kind: INVENTED_TOY_ENGINEERING_ONLY

## Hypothesis
The disclosed G1 R3=8/8 vs weak exact-retrieval R2=4/8 can be
explained entirely by a TRAIN-derived fixed-grammar *family-ranking prior*,
rather than new representational expressivity. An R2P **rank-only** control
trained on exactly the same episodes, with the identical new-world observation
transcript and inference candidate grammar, is a direct mechanism probe.
Because R2P's frequency features already generalize across object labels,
this is NOT a proof of concept-free learning.

## Engineering changes
- Toy `RankOnlySnapshot` with canonical preferences, minimum 3 unique
  solved TRAIN worlds per family, exact primitive types and digest check.
- Toy `rank_only_prediction` sharing R3 expressive candidate enumeration,
  public evidence, deterministic ordering and audit transitions.
- Typed Action/Relation/Observation exact built-in validation before
  comparisons/model pruning; Snapshot primitive and provenance hardening.
- New negative regression tests for behavioral string subclasses, invalid
  later observations after an empty candidate set, snapshot tampering and
  policy-only R2P/R3 equivalence in deliberately favorable toy fixtures.
- ARCH-001 and ARCH-002 Mermaid maps, specification, candidate plan,
  AGENTS.md, docs/INDEX.md and module directory register updated together.

## Reproduction (invented engineering only)
```bash
python -m unittest discover -s tests -p 'test_rep001_toy_engineering.py' -v
python -m packages.rep_evaluation
python scripts/check_docs.py
```

## Metrics / observed evidence
GitHub Actions [safe-successor workflow run #41290327154](https://github.com/ryonakayama234/DekaSugi/actions/runs/41290327154)
on exact source HEAD `346d2a9e1e6cdca6fc97d4b54de30c87d135eb9f` returned
**SUCCESS**: safe historical source-byte gate, docs/link checker, and
**124 explicitly allowlisted synthetic tests PASS** (112 prior + 12 toy
tests). The four new regression methods passed, including the asserted
R2P=R3=8/8 invariant on hand-selected invented toy worlds.
The toy's previously disclosed R1=4/8, weak exact-episode R2=4/8 and
R3=8/8 are NOT independent research outcomes. R2P matching R3 is evidence
that a **ranking-prior explanation is sufficient in this specific toy**;
it does not refute the long-term concept-acquisition hypothesis.
This documentation-only update is committed after the verified code HEAD;
the post-update HEAD must be rechecked separately.

No resource matching or intervention reset/setup metering was added. No
secret source, no graph-isomorphism split, no independent custodian,
no quantitative power, no formal scientific outcome. A formal
R3−R2P population effect estimate remains **NOT_ESTIMATED**.

## Acceptance
Safe CI passed for the code HEAD above; final documentation HEAD requires
reverification. Technical and independent scientific-method review of the
attribution rule remain pending. Any unexpected difference or failure is
recorded, not tuned using a sealed holdout. Previous frozen projects remain
unchanged. PR remains Draft; no automatic merge and no FINAL trigger.
