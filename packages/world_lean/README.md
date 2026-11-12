# WORLD-LEAN-1 — public learner / lean-editor/1

id: WORLD-LEAN-1-PUBLIC-LEARNER
status: IMPLEMENTED_FIXTURE_ONLY / FORMAL_NOT_AUTHORIZED
updated: 2026-11-12
tags: world, learner, runtime, fixture

Independent from `world_cal`. CPython 3.12.12 is the selected exact patch for
future replay; the 2026-11-12 local engineering fixture was run on 3.13.5.
No third-party runtime packages, arbitrary code execution, runtime source
compilation, or network calls are needed.

Public runtime contract:

```sh
python -m packages.world_lean contract
python -m packages.world_lean aulc 0 12 24 36 48
python -m packages.world_lean sign-p 12
```

The public learner child receives **only** canonical, exact-key JSON public
TRAIN blocks, or a snapshot, 4 public demos and a query initial state. It never
receives target, evaluator recipe, law index, phase, seed or scoring feedback.
The parent copies `__init__.py`, `core.py`, `learner.py`, `child_entry.py` into
an isolated temporary root and invokes its child entrypoint through `python -I`.
This is cooperative-code input isolation, not malicious same-Unix-user custody.

Snapshot bytes are identical for FULL and OFF; OFF forbids acquired CALL ASTs.
STATIC-RANK uses the same primitive/typed term grammar and supplied one-branch
scaffold, but does not register learned ASTs. LOOKUP reads public success traces
without branching and selects a nearest public-demo law then nearest trace.

No formal evaluator invocation or holdout generation command is exposed. Only
`python -m world_lean_evaluator fixture-gate` is authorized at this stage.
