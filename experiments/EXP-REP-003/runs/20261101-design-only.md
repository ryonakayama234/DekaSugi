# EXP-REP-003 2026-11-01 — design-only decision receipt
id: EXP-REP-003-DESIGN-20261101
status: PROPOSED / NOT_RUN
updated: 2026-11-01
tags: experiment, receipt, design-only
scope: documentation only

## Observed source baseline
- Read current Draft #132 source docs and corrected disclosed run; 48 worlds x 4 arms x 4 budgets = 768 raw records retained. LQ=FA across four strata; COMPOSITION LQ−LA +0.027995, DISTRACTOR LQ−LA −0.020183. Existing pilot direct-XOR only and role labels public.
- TRAIN64 has 3 independent graph topologies; renaming does not increase structural diversity. Formal DEV/FINAL and independent source custody are absent.
- Draft #129, #131, #132 stack not merged. This receipt makes no re-score and doesn't approve any merge.
- Google Drive folder listing found an encrypted stored `scored-ledger.tar.gpg`. File was NOT opened, exported or modified; unrelated/private source custody not inferred.

## Decision
Choose **opportunity-first role-blind conditional two-step inquiry** over premature Snapshot release, neural epochs, broad general-domain adapters or another label-revealing direct-only experiment. Start with exact reachable witness and strong fixed active FA. Negative findings accepted.

## Execution status
- Experiment code: NOT_IMPLEMENTED
- Synthetic witness generation: NOT_RUN
- Learning curve: NOT_RUN
- CI/tests/docs checker: NOT_RUN at this design receipt
- Independent review: NOT_DONE
- F0/DEV/FINAL: NOT_AUTHORIZED
- Baseline formal acceptance: HOLD

Next implementation slice is only the witness generator and cost ledger with synthetic negative tests, after independent design review. Not a scored intelligence result.
