# OPPORTUNITY-001-PILOT-V1 — 2026-10-29 REAL TRAIN64 paired evaluation (read-only recount)

id: OPPORTUNITY-001-TRAIN64-REAL-PAIRED-RECOUNT-20261029
updated: 2026-10-29
tags: opportunity, pilot-v1, genuine-train64, independent-readonly-recount, exploratory, no-rescoring
status: OWNER_REPORTED_COMPLETED_64_PAIRED_INDEPENDENT_READONLY_RECOUNT
date: 2026-10-29 Asia/Tokyo
method: [Frozen exploratory PILOT-V1](../pilot-v1.md)
scoring_commit: `d34f367a36311934975662bb611687fc8cbe0e98`
python: `3.12.15`
original_raw_sha256: `ef1e9c02a82240dbc4e450dd75b7d3102732d463b2793192f8f83a98ff5ec7c6`
public_manifest_sha256: `bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85`
recount_reviewed_head: `49cd1ac9b9ae2d418c23cb8cf65a7ec7ff982ba3` (PR #83, synthetic CI successful; exact-head review summary completed without findings)
recount_status: `COMPLETE_64_PAIRED_RECOUNT_VERIFIED`
source: owner's actual WSL2 read-only recount CLI JSON supplied privately to assistant (not direct GitHub access to private original bytes)
pasted_aggregate_JSON_line_sha256: `9eb701cc9b089446da8a4c79db92b815a7e177b5463353210ca3be4c72c905aa`
true_scored_retries: `0` (strictly no rerun or rescoring)

## Outcome classifications — original denominator 64 / 64

| Fixed prespecified class | Count |
|---|---:|
| Both correct, ON cheaper | 8 |
| Both correct, OFF cheaper | 8 |
| Both correct, primitive-call cost tie | 32 |
| Only ON correct | 0 |
| Only OFF correct | 0 |
| Neither correct | 16 |

- Valid paired independent third-example audits: **64/64** according to owner-local independent read-only comparator of all 128 original nine-element arm tuples and 64 redacted paired summaries (plus 128 ARM_STARTED and two run markers).
- OFF correct: **48/64 = 75%**. ON correct: **48/64 = 75%**. Paired accuracy advantage: **none observed**. Retrospective best-of-two: **48/64 = 75%**, not executable oracle improvement.
- All 16 one-arm-better examples are *cost-only* distinctions among mutually correct solutions, split 8 ON-better and 8 OFF-better. Both-failed OOD examples are not evidence of DSL impossibility; no false_solved was counted as a valid negative.
- No invented significance test or CI for a capability effect: this is an **exploratory new TRAIN-only pilot**, not confirmatory external DEV/FINAL.

## Original primitive call, search, audit, and policy metrics

| 64-pair total | OFF | ON | Interpretation |
|---|---:|---:|---|
| Canonical primitive calls | 3,616 | 4,256 | ON +640 (+17.7%) |
| Tested search candidates | 824 | 936 | ON +112 (+13.6%) |
| Search CPU (ms) | 27.5484 | 45.7293 | separately measured, ON higher |
| Search wall (ms) | 27.5498 | 45.7209 | separately measured, ON higher |
| Independent audit CPU (ms) | 0.3184 | 1.3165 | separate scope; don't treat as general speed estimate |
| Independent audit wall (ms) | 0.3246 | 1.3304 | separate scope |
| Inference of fixed B1/B2/B3 policy | NOT METERED | NOT METERED | never silently impute zero |

On the **48 both-correct** cases alone, original primitive calls total **OFF=352, ON=352**: ON saves 32 in `normalize_lower` and adds 32 in `normalize_upper` (net zero). On the **16 both-unsolved OOD** cases, OFF=3,264 and ON=3,904. Thus all **+640** ON primitive calls in the pooled total arise within both-unsolved cases; this is a real search-cost burden, not a gain in correct outcomes.

## Presealed policy selection: primary B1, descriptive B2/B3

| Prespecified metric | B1 primary | B2 descriptive | B3 descriptive |
|---|---:|---:|---:|
| Unique better action eligible (excludes tied and neither-correct) | 16 | 16 | 16 |
| Wrong choices among eligible | **0/16** | **0/16** | **0/16** |
| Both-correct regret eligible | 48 | 48 | 48 |
| Sum of excess canonical primitive calls | **0** | **0** | **0** |
| Missed success / lost success | 0 / 0 | 0 / 0 | 0 / 0 |

The three sealed policy choices disagree on **1/64 tasks** (in `trim`), but that task belongs to a both-correct, equal-cost stratum; no scored decision error or regret resulted. Neither-correct examples cannot be labeled as having a unique cheaper successful action, and accuracy misses are zero partly because there were **zero arm-only successes**. Do **not** report B1 error as 0/64; the actual decision-eligible denominator is **16**.

## Per-family aggregate (8 cases per family; no individual mapping)

| Family | OFF correct | ON correct | OFF calls | ON calls | Cost/class |
|---|---:|---:|---:|---:|---|
| `identity` | 8 | 8 | 0 | 0 | correct cost tie |
| `trim` | 8 | 8 | 16 | 16 | correct cost tie |
| `lower` | 8 | 8 | 32 | 32 | correct cost tie |
| `upper` | 8 | 8 | 48 | 48 | correct cost tie |
| `normalize_lower` | 8 | 8 | 112 | 80 | ON cheaper |
| `normalize_upper` | 8 | 8 | 144 | 176 | OFF cheaper |
| `reverse_ood` | 0 | 0 | 1,632 | 1,952 | neither correct |
| `replace_first_ood` | 0 | 0 | 1,632 | 1,952 | neither correct |

No private audit examples, original score tuples, family-per-task mappings, source IDs, seeds, passphrase or private cloud location identifiers are in this report. Eight deliberate strata are not eight independent real-world domains.

## Frozen branching decision — DO NOT amend after outcomes

The preregistered branch for investigating AL-v2 requires **at least 8 uniquely better arms AND B1 misses in at least 2 different families**. Here the first component holds (16), but **B1 misses 0**, so the branch does **not** trigger. The separate search/skill invention branch requires **at most 2 uniquely better actions**, also false (16). Therefore the preregistered **otherwise = UNDERIDENTIFIED** branch applies.

**Next research recommendation:** preregister a **new, independently sampled identification distribution** that has diagnostic power to distinguish accuracy-changing skill effects from equal-accuracy cost differences, with separately justified sample size. Do not retune, rescore, resample, or reinterpret the original 64 tasks. The two observed OOD failure strata invite a distinct investigation into search space vs. representation, but they do not prove expressivity impossibility.

## Custody, independent corroboration, limits

- Genuine third-audit original was created once prior to scored trials, 64 distinct records; fixed 192 public B1/B2/B3 choices and frozen historical skill confirmed by source-first preflight. Original and score ledger remain **owner private**.
- Owner reported true one-shot engine receipt: `{"paired_count":64,"scoring_authorized_again":false,"status":"completed_private_local"}`; never rerun this scorer, even if a later report is disputed.
- Scored evidence archive consists of 322 original private files (STARTED, COMPLETED, 128 ARM_STARTED, 128 original audited nine-element scorer tuples, 64 redacted pair summaries). AES-256 GPG ciphertext is 56,043 bytes; connected Drive API independently fetched the encrypted file and computed SHA256 `f001db8ca970028a07a439b19fba25a75e3d137388b2405d886fbfd496e995f9`. Owner independently reported **DRIVE_BYTES_MATCH** of local ciphertext against that SHA, and **LEDGER_ARCHIVE_MATCH** of decrypt-piped-to-`tar --compare` with `pipefail`.
- The ciphertext is in a nonshared owner-only Drive object and folder with one revision marked `keepForever`. This is **not deletion-proof WORM** or a guarantee against owner-account loss.
- The independent read-only owner-local recount reports exact 64 saved paired results against privately retained original scorer tuples, with `scored_again=false` and `retry_authorized=false`; GitHub did **not** itself retrieve or decrypt original score data.
- The frozen generator/source lock includes a historical main-push CI workflow that would run an unrelated past DEV smoke; a proposed workflow alteration failed the original byte lock and was closed. This report is proposed on an isolated review branch without amending the locked method, original source, test outputs, or historic DEV/FINAL. Do not accidentally trigger historical DEV smoke to publish this report.
- No confirmatory p-value or CI, cross-domain generalization, formal expressivity proof, or newly run DEV/FINAL. No promotion claim based on this exploratory pilot.

**Final conclusion: 64/64 pairs independently recounted in the owner's environment; 48/64 correct in both ON and OFF, no observed correctness uplift; B1/B2/B3 make 0/16 eligible cost-action errors, while overall ON incurs +640 canonical calls concentrated on unsolved OOD strata. The frozen decision is UNDERIDENTIFIED, calling for a newly registered identification distribution, not a retroactive replay.**
