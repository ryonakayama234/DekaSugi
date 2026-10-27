# EXP-0003A — Pre-DEV source, split and policy freeze v1

id: EXP-0003A-FREEZE-V1
status: candidate_review; immutable source/data/policy values pinned
updated: 2026-10-26
tags: exp0003a, preregistration, freeze, evidence, dev-gate

## Freeze authority and scope
The preregistered methodology remains [plan-v1](plan.md), unchanged. This record is the human-readable explanation of the canonical [freeze-v1.json](freeze-v1.json); the latter is the **single machine-readable authority**. This is a pre-DEV source/data/policy lock only, **not** an authorization to evaluate either DEV64 or FINAL128. [PR4 Issue #36](https://github.com/ryonakayama234/DekaSugi/issues/36).

This freeze is derived from PR3 merged main `55af90d6f1eea11404efef358e4819b63928907e` with source preflight at PR4 feature head `fed42c9258ed7df58f04cd4703f0b209666d2135`; initial freeze values committed at `bd1c695ba105e9975d6b33f10c47d77a8f57df8a`, then **superseded before merge** by reviewed source-first validation and refreshed candidate pinned at `bb1ad056d94d5ba6c47482a4843d352556554b71`. The earlier hashes are obsolete. Source Git blob hashes, not commit SHA, are the immutable source identities: squash merging changes the overall commit SHA without changing bytes. GitHub PR4's final merge SHA must be recorded separately upon integration.

## Verifiable fixed values
- Full source/data/policy `freeze_payload_sha256`: `1e0f6daf1cb80262c187c60a3e0a4d2e76dafea911f0633feed3c40f93db8f44`.
- Full 864-record four-partition `dataset_sha256`: `491e1b930d363c2550ba756f45e88a1873784a22eb503216b04c4e43b2278e49`.
- 14-source Git blob manifest SHA256: `b007533bd1f06f37b740d8f05df463915a8f03cef61cff32fc4b7c92bce91394`.
- TRAIN160 split: `9d32d1755f0497e6053edd9e3dcd1804b886433646ec9d4a58973ce04041a474`.
- DREAM512 split: `4cf20733ba2b4b388c0cbd8f5a9e5dbfb85a5acfc11b7ceec6cdb6e95918ad54`.
- DEV64 split (hash-only): `258237ccc5c360a61d5c0a9e95d03610c0e4b7003e6268323df8429d4eabda45`.
- FINAL128 split (hash-only): `cb0de1103bbb98fc5547545569ec2661c023c76836486f7e1b9182f3407741d2`.
- B1 snapshot SHA256: `3b4fc00f8ad0fe2f1cc0978886d7bc7a6285ed002c842ceeb0106fd51ee5afd4`.
- B2 snapshot SHA256: `01d5595e1b4c32d200e2734630f38a848e77a64f356741445e011865834f5af7`.
- B3 snapshot SHA256: `a6d46ab5dd697e8e90789693fdd3bd67bbca445ec07bc8b119401e1c0cf1e210`.
- B2 random 96 ordered Dream selection SHA256: `39fb4658911ea785055146c4cb50218321a9ed00b85f7fbe84827ab39be6e72b`.
- B3 near-positive 96 ordered Dream selection SHA256: `2b20d808e15ab94df9704507146f0203e78c2605b0d78cd1d6b8efde0601bb92`.

## Preflight method and provenance
- CPython 3.12 `python -m packages.exp0003a.freeze_cli --mode preflight --output <new-file>` regenerates only synthetic reference pairs and hashes; no DEV/FINAL synthesizer, KNN chooser, primitive meter, verifier or independent audit is run on holdouts. It compares the full TRAIN160/DREAM512 tuples to the independently defined plan-v1 generator and their original PR2/PR3 source implementations. It also independently audits full 14 source Git blob IDs (we verified every declared SHA against GitHub's actual blob SHA when pinning).
- `python -m packages.exp0003a.freeze_cli --mode check-freeze --output <new-file>` must **first** check frozen JSON's own digest, schema, runtime and every listed source blob hash **without executing the dataset generator or TRAIN/DREAM learner**, and only after a complete match regenerate source-bound data/skill/policies for strict comparison with the checked-in [JSON](freeze-v1.json). GitHub Actions runs **both** modes on every PR/main verification; the absence of `freeze-v1.json` is an error. Old artifacts are not treated as current if a source file changes.
- [PR4 initial CI #40321644523](https://github.com/ryonakayama234/DekaSugi/actions/runs/40321644523) generated the pinned hash-only candidate; [verified CI #40321874173](https://github.com/ryonakayama234/DekaSugi/actions/runs/40321874173) succeeded 68 unit tests and both preflight/check-freeze, with [Artifact #12649706107](https://github.com/ryonakayama234/DekaSugi/actions/runs/40321874173/artifacts/12649706107). Final exact-head review, CI and main integration must be checked separately.

## Evaluation controls
- Before any DEV engineering evaluation, a separately reviewed evaluator must require `verify_frozen` to pass *before task scoring*, then choose B0/B1/B2/B3 using **only public TaskSpec features**. TRAIN/DREAM snapshots are read-only. No holdout results are allowed to retune a method or change these hashes.
- FINAL128 is not authorized. Its first independent evaluation must be a distinct manually approved, one-time PR with explicit deployment gate, verified raw source blobs, independent meter/Verifier and frozen model. On incomplete or invalid data, persist an `inconclusive`/`invalidated` report; never change the frozen method based on outcomes.
- No DEFAULT_REGISTRY skill promotion, no performance claim about H2/H3, no reusing the old EXP-0002B FINAL112 as holdout.

## Exact-head P1 code review response
- PR #37's automatic ready-for-review check discovered an independent **P1**: the original `verify_frozen()` performed TRAIN/DREAM recomputation before comparing frozen source hashes. This has been corrected with inert JSON/schema/runtime/source-bytes guard first, and a negative test asserting that tampered sources do not call `preflight_record()` at all. The old initial candidate was **superseded**; [source-first candidate CI #40352073490](https://github.com/ryonakayama234/DekaSugi/actions/runs/40352073490) recomputed the new 14-source manifest and immutable digest (its unit suite intentionally failed while the pinned old freeze was stale). The updated committed `freeze-v1.json` at `bb1ad056d94d5ba6c47482a4843d352556554b71` is authoritative. Latest exact-head CI/independent review must be completed separately before merge.
