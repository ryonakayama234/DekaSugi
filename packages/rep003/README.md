# REP003 — Disclosed anonymous conditional causal learner (engineering subset)
id: PKG-REP003
status: IMPLEMENTED_CANDIDATE / DISCLOSED_ONLY / NOT_FORMAL
updated: 2026-11-02
tags: package, active-learning, conditional, wake-sleep, synthetic

## Scope / API
`packages.rep003` implements a **reduced one-edge** n=4 Boolean causal interpreter under exact paid `set(i,0|1)` / `pulse(i)` actions. All 61 finite learner hypotheses are `EMPTY`, `DIRECT(src,target)`, or `GATE(src,target,guard,value)`; distinct src,target,guard. Pulse effects toggle target using **pre-pulse** state; no arbitrary free resets. World truth is host-owned in `Session`; learning, model selection and Snapshot induction call only `Session.apply` and validate public traces. Public IDs are anonymous 48-bit strings, permuted independent of semantics.

This is NOT the full two-edge composition, rule primitive invention, adaptive learned neural optimizer or F0-scored evaluation proposed by [Decision V2](../../docs/specs/EXP-REP-003-DECISION-V2.md). Two-edge DISTRACTOR worlds are deliberate OOD negative controls and can cause ABSTAIN. All disclosed data is synthetic and same-process; formal custodians are absent.

## WSL2 / bash CLI
```bash
python -m packages.rep003 preflight --scope disclosed --output .run/rep003/preflight.json
python -m packages.rep003 train --worlds 64 --snapshot .run/rep003/snapshot.json
python -m packages.rep003 inspect --snapshot .run/rep003/snapshot.json
python -m packages.rep003 use --snapshot .run/rep003/snapshot.json --world-index 301 --stratum CONDITIONAL_TRANSFER --arm LQ --budget 6 --trace .run/rep003/use.json
python -m packages.rep003 evaluate-disclosed --output .run/rep003/pilot.json
python -m unittest tests.test_rep003_engineering -v
```

Train uses paid 5 state settings × 4 source pulses = 20 pulses/world, each preceded by 4 charged `set` actions: **100 operations/world** (including no-op sets), never host graph reads for model support. SLEEP is deterministic canonicalization of identified `EMPTY/DIRECT/GATE0/GATE1` into an executable guarded-toggle abstract template with a TRAIN-frequency prior. DREAM is only bounded two-step counterfactual model planning; NOT SGD nor novel world evidence. Storage is typed canonical JSON + SHA-256, no auto-import into production library.

`preflight` spends 4 public pulses in the invented witness world to rule out DIRECT and GATE0; among remaining hypotheses all legal *next single actions* yield identical outputs, whereas a paid set→pulse trace can distinguish. **Total charged history + witness cost = 6**, not 2 from scratch. It is an existence demonstration, not proof all worlds have a two-step-only opportunity.

`use` records public action trace, charged action and model-check counts, exact learner prediction and immutable commit hash; never returns hidden gold. `evaluate-disclosed` applies 32 synthetic evaluator-only transitions to committed models, emits 48 worlds × 7 arms × 6 budget horizons (0/1/2/4/6/8) = 2016 raw rows with digests. It does NOT imply independent semantic-family replication or formal one-shot DEV/FINAL.

Compare LQ learned class-conditioned query prior vs LA uniform query prior but same learned prediction; this tests **learned prior usefulness**, not necessarily executable concept-body-specific value. FA is complete untrained 2-step information-gain search under uniform semantic hypotheses; LR rank-only and ER episodic/class support can match LQ, correctly preventing overclaim. Controls, budget cap and numerical observations in [V1 implementation specification](../../docs/specs/EXP-REP-003-ENGINEERING-V1.md).

## Boundaries and known limitations
- All four TRAIN semantic structure types remain only FOUR independent **class categories** despite n=64 distinct opaque IDs. Same-process truth and sampler; no significance estimate.
- Conditional-composition stratum has one gated edge only, not a novel multi-edge topology. The two-edge DISTRACTOR is *out of the learner grammar*. Genuine compound-body transfer is NOT_TESTED.
- Plan horizon is 2, actual operation budget includes paid conditioning history, and all learner model candidate checks capped at 200000 per episode.
- TRAIN costs and planner checks are separate ledgers; CPU/wall/RSS (and cross-platform performance) are not uniformly measured yet. Cost parity is **partially implemented**; not formal matched lifetime compute.
- No new neural weights, gradient epochs, language-world transfer, self-invented grammar, formal custody or model promotion.
