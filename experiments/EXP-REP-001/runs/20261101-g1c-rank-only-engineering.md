# EXP-REP-001 G1-C — synthetic engineering receipt
id: EXP-REP-001-G1C-20261101
status: IMPLEMENTED_UNVERIFIED; NO_FORMAL_TRAIN; NO_DEV; NO_FINAL
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
**No fresh execution evidence recorded at document creation**. Expected
qualitative invariant in the intentionally favorable fixture:
R2P is equivalent to R3 because R3's stored `gated_true` support frequency
is fully reproducible from TRAIN episodes without persisted concept bodies.
The committed test asserts this. Do NOT report 8/8 until exact-head CI or
independent local execution actually confirms it. The previous R2=4/8 and
R3=8/8 numbers remain historical toy plumbing evidence, not H1 support.

No resource matching or intervention reset/setup metering was added. No
secret source, no graph-isomorphism split, no independent custodian,
no quantitative power, no formal scientific outcome. The effect estimate
R3−R2P remains **NOT_ESTIMATED**.

## Acceptance
Pending exact-head safe CI, technical review, and explicit scientific-method
review of the attribution rule. Any unexpected difference or failure is
recorded, not tuned using a sealed holdout. Previous frozen projects remain
unchanged. PR remains Draft; no automatic merge and no FINAL trigger.
