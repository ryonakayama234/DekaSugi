# DekaSugi G1-D toy research lab

**Disclosed, invented, deterministic engineering only. Not a formally scored intelligence model.**
No previous experiment's frozen TRAIN/DEV/FINAL inputs are loaded, changed or scored.

## Run (WSL2 / Linux, repo root)

Requires Python 3.12+ and the standard library. No CUDA, cloud model, pip dependencies or API keys.


~~~bash
python -m packages.rep_lab train --worlds 32 --snapshot .run/rep-g1d/snapshot.json
python -m packages.rep_lab inspect --snapshot .run/rep-g1d/snapshot.json
python -m packages.rep_lab use --snapshot .run/rep-g1d/snapshot.json
python -m packages.rep_lab evaluate-toy
~~~

`train` performs metered set_state/pulse Wake observations across 32 named (but same-structural-family) invented worlds and learns a two-relation role-template. It creates a versioned JSON Snapshot on local disk. `inspect` validates the digest and displays its structure; `use` loads that Snapshot and infers over a fresh **disclosed** toy world by publicly observed actions. `evaluate-toy` re-runs the full engineering learning curve, passive and active arms, all without sealed data.

For the *reviewed* synthetic subset in CI, run:


~~~bash
python scripts/check_research_ci_v2.py
python scripts/check_docs.py
python scripts/run_research_ci_v2_tests.py
~~~

Do not use unrestricted discovery across legacy experiments; old frozen sources may be protected by source-first gates.

## What is and is not learned

`RepairSnapshotV1` persists an abstraction over object roles with an executable **typed constructor** for two relation atoms. After enough distinct named TRAIN worlds are uniquely solved (>=3) a canonical body is retained. On a new world, the learner binds roles to new IDs and validates generated candidates against *all* public observations before prediction. A failed template fit falls back to bounded full two-relation search.

This is **learned template reuse within an experimenter-provided grammar**, not invention of new primitive semantics. The same TRAIN topology appears under renamed object IDs; real graph-class generalization is untested. The `ToySession` host shares a Python process with learner code; its private fields are not a formal security boundary. Audit transitions are host-only but artificial and fully disclosed in source.

## Honest toy outcome and limitations

See [final template constructor run](../../experiments/EXP-REP-001/runs/20261101-g1d-template-constructor.md). In the six disclosed worlds, B1 fixed H2 = B2 rank-only = B3 executable body = B3x body-off in prediction score. B3 makes fewer candidate checks after n>=3, but that is not a universal computational advantage or formal transfer. B5 Active Learning uses a different public transcript and can improve prediction on this toy without proving the representation hypothesis. Strong episodic memory, independent evaluator custody, formal preregistration, and true structurally disjoint worlds remain open research gates.

Snapshot integrity hashes do not authenticate source; do not use toy archives as official/reference/promoted intelligence.
