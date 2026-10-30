# ACTIVE-001 Gate F — exact public-context structural census (INVENTED SPLIT; NO SCORING)

id: ACTIVE-001-GATE-F-FIXTURE-01
status: engineering_structural_observation; not_scientific_trial; not_source_frozen
updated: 2026-10-30
tags: active-learning, feasibility, exact-enumeration, no-scoring, provenance

Parent: [Issue #96](https://github.com/ryonakayama234/DekaSugi/issues/96), stacked proposal [PR #97](https://github.com/ryonakayama234/DekaSugi/pull/97), [scientific design v2](../method-v2-decision-draft.md). This receipt contains **a deterministic symbolic census of a previously invented split**; it does NOT include any selected official targets, Oracle answers, future evaluator-only labels, held-out score, or a scored ACTIVE-001 task.

## Source and execution

- Instrument: `packages.active_feasibility.census_fixture()` / `python -m packages.active_feasibility`, schema `active-feasibility/1`; stdlib Python 3.12-compatible, no external network.
- Fixed invented engineering split seed `20261030`. **This is NOT the future independently frozen confirmatory split/seed**.
- Source world: current existing InquiryWorld finite 156-input universe, 4,681 syntactic programs and 878 semantic classes; one split of 28 public, 64 query, 64 evaluator-only inputs. Gate F consumes **public and query columns only** from the canonical pure symbolic class signatures; private evaluator labels are never supplied.
- Enumerate all `C(28,2)=378` unordered public pairs; group 878 semantic classes by their two public outputs. This yields 91,367 nonempty public-observation contexts, with total target/public-pair weight `878*378=331,884` when each block is weighted by its semantic class count.
- F1: class count 1. F2: class count >1 and all 64 candidate questions have identical predictions across survivors. F3: class count >1 and at least one candidate distinguishes survivors. F0: empty block cannot appear in a realizable model; design integrity guard. F4 (strict adaptive two-query distinction): **not computed**, not silently assumed false. Exact future algorithm/review requires a separate version.
- The context log is hashed in deterministic public-pair and output-group order. No private target IDs, question-answer episodes or heldout correctness enter the hash.

## Actual deterministic synthetic structure (NOT scientific efficacy)

| State | Distinct public contexts | Full-population class/pair weighted count | Weighted share |
|---|---:|---:|---:|
| F0 invalid/inconsistent | 0 | 0 | 0% |
| F1 already unique | 37,643 | 37,643 | 11.3422% |
| F2 indistinguishable in allowed query pool | 5,866 | 12,130 | 3.6549% |
| F3 informative query available | 47,858 | 282,111 | 85.0029% |
| TOTAL | 91,367 | 331,884 | 100% |

- Max surviving hypothesis count in any public context: **276**.
- Weighted number of positive-disagreement query IDs accumulated over all class/pair tasks: **11,459,844** / `331884*64 = 21,240,576` task/query slots; weighted share **53.9526%**. This is a fraction of *eligible query candidates*, not the probability a query succeeds at identifying a target nor the observed outcome of B1 or B2.
- **Structural gate judgment on THIS invented split:** F3 prevalence ~85% makes the necessary `P(F3)>=5%` opportunity condition pass; this alone proves **neither** the +5pp benefit hypothesis nor the correctness of N4096 or a real-world capability.
- Weighted F1+F2 = 49,773 / 331,884 ~14.9971% comprises zero-information-opportunity tasks under the given grammar/pool. Keep such cases in the future primary full-population estimand rather than conditioning them away.

## Reproducibility identities

- `world_digest`: `158657529ef0b16a92b6f34984d07b8d3a318e6edca2b8a7f183add40bbf50a3`
- `split_digest`: `cbabb2d8f22e2cc73e69c82ae88733bfcfec97e4a6f749c66bf68e3ee2ca4c49`
- `context_sha256`: `9c135ace8f815e4b3ac2465c9918833c3becd43781faeedc36314c28c9203f12`
- Report `role`: `invented-public-structure-only/no-scoring/no-source-freeze`.
- Recomputed locally on a **standalone faithful reconstruction of the public InquiryWorld algorithm** (network clone of exact repository unavailable). Test command: `python -m unittest discover -s tests -v` for this module's invented tests. **4 tests passed** in that standalone local reproduction; this local run is not an exact-head full repository test, and must be independently confirmed by the GitHub PR CI.
- Exact-head GitHub Actions result and reviewer status: **pending in this original record until checked**. Preserve as historical initial receipt; subsequent status append permitted with exact commit/run link.

## Scientific and safety limits

Neither the 878 classes nor the 331,884 potential pairings represent 331,884 independent external tasks. The only implied weighted target law is one random class × one random public pair, conditional on this *invented* split. The future one-shot Gate C has not been frozen, sampled, or scored. F3 gives an **upper bound** on potential B2-vs-B1 advantage; it does not estimate the advantage. A prospective reviewer must independently validate the protocol's target class law, source, power, time budget, F4 necessity, and evaluator secrecy before real scoring.

**New genuine scored ACTIVE-001 observations: ZERO. Old frozen experiments: untouched. No source/seed freeze or scientific activation.**
