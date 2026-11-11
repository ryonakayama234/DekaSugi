# WORLD CAL Implementation Plan §2 — Errata 2026-11-11

id: WORLD-CAL-IMPLEMENTATION-ERRATA-20261111-01
updated: 2026-11-11
tags: world-expansion, cal-preparation, implementation-errata, research-lead, no-cal
status: HISTORICAL_CORRECTION / IMPLEMENTATION_GO_CONTINUATION / NOT_CAL_AUTHORIZED
authority: supervisor intermediate audit PR #206 comment 6794959589
original: docs/research/WORLD-CAL-IMPLEMENTATION-PLAN-20261111-01.md §2, row world_cal/k0_open_loop.py

## Correction (no normative specification revision)

- **Incorrect historic plan wording**: "24 action tokens".
- **Correct value**: **14 concrete tokens** for every phase with four live Sym values. Appendix A specifies 11 operation TYPES; INSERT has four possible Sym arguments, the other ten each have one: 10+4=14. The figure 24 in plan §2 is a transcription error, NOT a different alphabet or protocol.
- The episode HORIZON **remains 24 issued primitive steps**; this is a separate quantity and MUST NOT be conflated with the 14-token action inventory.
- Approved source: specification pack v6 Appendix A and WORLD-CAL-PROTOCOL §6.2; audit comment https://github.com/ryonakayama234/DekaSugi/pull/206#issuecomment-6794959589.
- Code: world_cal/world.py World.legal_actions() yields exactly 14 tokens. K0-a/BFS and K0-b/DP enumerate the identical 14-token ordered action set.
- Documentation handling: preserve the byte-pinned historical plan verbatim and bind this explicit erratum as a separate tracked source, rather than rewriting the historic reviewed document.

## Other five-RQ audit dispositions embodied by implementation sources

1. PRF upper boundary: for binary64 computed u>=1, u=nextafter(1.0,0.0), otherwise u<=0 and other invalid endpoints STOP_UNKNOWN. This is a **representation rule only**, not a probability law change. See world_cal/prf.py.
2. B-time Contrast: average each arm's G1/G2 B success rates with equal weight, THEN FULL - max of seven controls on the **same Y**. Do not average law-level maxima before applying HT, and do not substitute G1-only. Family-specific contrasts are descriptive, not inferential. See world_cal/gtheta.py and world_cal/power_engine.py.
3. Sampford: public N=336 quota-implied q multiset has 72 laws of q=1/160 and 264 of q=1/480. The implementation separates certainty units, exact group-count law and second inclusions; the all-n 2..336 source-only audit cross-checks independent exact rational enumeration. No actual H_laws assignment, law-ID weight mapping or escrow is materialized. Any degeneration is STOP_UNKNOWN, no approximation. See world_cal/sampford_grouped.py and scripts/audit_world_cal_sampford_336.py.
4. CPU feasibility remains STOP_UNKNOWN. Only one synthetic complete structural repetition may run before CAL authorization, with explicitly public static test key, synthetic parent labels, exact 999 bootstrap and no full R or scan. Independent wall/CPU/RSS and system disclosure required. See scripts/profile_world_cal_integrated.py.
5. Every claim remains implementation-candidate-only until supervisor's **independent** numeric/access/reproducibility and exact-head source audit PASS. algorithm_digest=null. No CAL_AUTHORIZED, K0 production run, power simulation, sealed split, seed generation or final evaluation is permitted in this PR.
