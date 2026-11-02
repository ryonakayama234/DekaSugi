# EXP-REP-004 — 2026-11-02 disclosed engineering outcome
updated: 2026-11-02
tags: experimental, run, evidence, measured, null-result

id: EXP-REP-004-20261102-DISCLOSED
status: IMPLEMENTED_SYNTHETIC / MECHANISM_ACTIVATED / PRIMARY_NEGATIVE / NO_FORMAL_F0
issue: https://github.com/ryonakayama234/DekaSugi/issues/136
evidence_source: experiments/EXP-REP-004/artifacts/20261102-disclosed-1920-raw.json.zlib.b64

## Provenance, boundaries and accounting

- Historical REP003 (PR #135) had 2,016 records with LQ=LA=FA and no executed concept bodies. Historical archives/code not changed; the prior two-edge OOD and mislabeled NOVEL remain historical facts.
- This implementation is a new, bounded synthetic suite. Python 3.13.5 local / stdlib, WSL-compatible CPU; external independent evaluator/custodian was NOT present. No private, old sealed, DEV/FINAL, Drive ledger or unavailable real-world data was opened.
- TRAIN64 comprised 32 distinct role-invariant semantic families with 2 differently renamed worlds each; 6,400 charged actions. Snapshot digest: 4585f68f150318e94cc38cf26143f29bc9fe0e03a1fc0bd7bb99db997ae040f2. Manifest digest: 440547723d7f7a4ef5f8302c796d8fefc847dfd451be681a3ff7a7d38f08d052.
- Sleep generated seven executable typed body templates: ALWAYS, GUARD0, GUARD1 and 4 concurrent topology macros (CHAIN, FANIN, FANOUT, OTHER). Positive witness receipts and available negative applicability witnesses persisted; no wholly new primitive semantics.
- Mechanism fixture (development only): after two PAID source pulses with identical trace (sha256 238010fc630ff2ffb3d26a964d83534ed7e28aa5d7edd84bd1c6ee9139097de1), 124 hypotheses survive; body-aware LQ proposes pulse(3), LA proposes pulse(2). Runtime executes body AST; mutation of guard changes next-state prediction on a separate test. This is a causal-path unit check, NOT a scientific effect-size estimate.
- Paired disclosed evaluation: 48 worlds x 8 arms x 5 budgets (0/1/2/4/8) = **1,920 trials**, 64 post-commit full-state audits each = **122,880 exact transition checks**. Every raw record retained. Additional paid evaluator-observation actions: 5,702. Training plus evaluation paid actions: 12,102.
- Archive raw reconstruction SHA-256 (uncompressed UTF-8 bytes): **70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3**; raw 860,285 bytes. Archive is standard zlib-compressed JSON encoded as base64 with final newline. Summary JSON is separately preserved.
- Eight local unit tests passed. A reviewer-signoff for the exact GitHub head and an independently custodied source-freeze/one-shot FINAL were **not** completed at measurement time. V2 design and criterion are recorded after this score, so this experiment is EXPLORATORY engineering evidence, not a prospective scientific preregistration.

## Mean exhaustive transition accuracy (equal mean across five action budgets)

| Stratum (12 semantic families/worlds) | LQ | LA | LR | ER | FA | FX | BODY-OFF | STATIC-MACRO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SEEN_ROLEBLIND | 0.717708 | 0.720833 | 0.696875 | 0.692708 | 0.772917 | 0.760417 | 0.772917 | 0.717708 |
| UNSEEN_COMPOSITION | **0.700000** | 0.705208 | 0.713542 | 0.725000 | **0.760417** | 0.743750 | 0.760417 | 0.700000 |
| UNSEEN_IN_GRAMMAR | 0.781250 | 0.790625 | 0.808333 | 0.813542 | 0.847917 | 0.826042 | 0.847917 | 0.781250 |
| OUT_OF_GRAMMAR | 0.495833 | 0.500000 | 0.404167 | 0.445833 | 0.452083 | 0.210417 | 0.452083 | 0.495833 |

## Mechanism versus scientific inference

- **Body-use pathway passes an engineering fixture**: query actions differ in 78/240 matched LQ/LA stratum×world×budget episodes (not 78 distinct families). Across 240 pairs LQ scored better in 8 and worse in 16; the other 216 ties. Changed questions are not reliably more informative.
- **Primary UNSEEN_COMPOSITION is negative**: mean (LQ−LA) = −0.005208; mean (LQ−FA) = −0.060417. Twelve family paired deltas LQ−LA: [0,0,-0.050000,0,0,+0.037500,0,-0.012500,+0.012500,0,0,-0.050000]. Only 2/12 positive, 3/12 negative, 7/12 tied. Fails planned engineering exploratory +0.02 and >=9 positive families.
- **Critical learned-unique attribution null**: STATIC-MACRO *exactly matches LQ* in all strata, when human-preinstalled with the same seven body forms. Thus current scoring does not distinguish learned abstract semantics from an adequately programmed fixed prior; do not claim concept invention.
- **Strong fixed baseline better in-domain**: FA = BODY-OFF for this implemented policy, exceeds LQ in all three in-grammar groups. This can be explained by the richer fixed grammar plus an underperforming template-weighting prior, not necessarily by concept representation failure alone.
- **OOD calibration not achieved**: zero ABSTAIN in 12 three-edge OOD worlds x each budget x each of LQ/LA/FA. Observed OOD accuracy under LQ is ~0.496; failure to reject an out-of-grammar world within the charged budget must not be represented as calibrated uncertainty.
- This is an **engineering mechanism improvement but scientific utility NULL/NEGATIVE**. The next experiment must isolate useful learned role-binding and compositional predictions beyond strong static macros, and separately test OOD non-identifiability and resource costs. No model promotion, release freeze or automatic merge.

## Cost, replay and missing claims

The 1,920 trial receipts report 3,974,007 *logical* learned-body invocations under LQ (cache hits included), per-trial model checks, per-trial CPU times and 5,702 paid environment actions. Per-trial CPU times summed to 38.581072 seconds in the local four-group measurement workflow; these are not standardized cross-platform, not a full training/Sleep/Dream lifetime cost and not comparable to a separate precomputation budget. Cached computation makes runtime and nominal interpreter-invocation counts distinct. No RSS claim. The 64 audits are within-world exhaustive, not 64 independent worlds. The 12 composition families cannot justify powered general-intelligence statements.

Reconstruct and verify the archive with scripts/read_rep004_archive.py. Its source family IDs and results were generated and scored in one disclosed research environment. No separate trusted evaluator custody, prospective independent preregistration, or formal one-shot F0/FINAL evidence is claimed.

**Verdict:** M2 bounded executable learned body YES; M3 live inquiry change YES; M4 query performance benefit NO; M5 unique learned abstraction beyond static macros NO; M6 OOD safe abstention NO. This is a valid negative scientific outcome with a working technical mechanism.
