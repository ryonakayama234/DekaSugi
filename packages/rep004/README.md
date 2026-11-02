# rep004 — executable symbolic concept engineering pilot

status: IMPLEMENTED / DISCLOSED_1920_SCORED / SCIENTIFIC_BENEFIT_NEGATIVE
updated: 2026-11-02

Research question: Does a learned typed body, induced only from charged public transitions, execute on new role-blind worlds and improve inquiry beyond strong fixed, episodic and macro controls? Body/actual-query activation works; new-family utility does not.

Requirements: Python 3.12+, standard library only, WSL2/Linux or comparable CPU. No older sealed datasets, private Google Drive keys, network or external model.

~~~bash
python -m unittest tests.test_rep004_engineering -v
python -m packages.rep004 preflight --output .run/rep004/preflight.json
python -m packages.rep004 train --train-worlds 64 --snapshot .run/rep004/snapshot.json
python -m packages.rep004 inspect --snapshot .run/rep004/snapshot.json
python -m packages.rep004 use --snapshot .run/rep004/snapshot.json --world-index 501 --arm LQ --budget 8 --trace .run/rep004/use.json
python -m packages.rep004 evaluate-disclosed --snapshot .run/rep004/snapshot.json --output .run/rep004/full-local.json
python scripts/read_rep004_archive.py --archive experiments/EXP-REP-004/artifacts/20261102-disclosed-1920-raw.json.zlib.b64 --output .run/rep004/recovered.json
python scripts/check_docs.py
~~~

Public evidence collected by Session.apply costs one for every set/pulse. Sleep receives only public observation lists and derives the inferred semantics and family IDs from those lists; host secret edges are not API inputs. Each library entry includes an executable typed AST, support from distinct learned families, positive/negative applicability evidence hashes and a checked body_hash. Snapshot is canonical JSON with digest. A fresh use loads this Snapshot, selects actions using executed concept semantics, commits before a separate audit, and reports raw actions and inference costs.

The archive is a *disclosed* synthetic engineering score, not a formal sealed or powered test. Some other source versions are historical draft designs; this module implements V2. CPU values are descriptive, and invocation meters include logical checks even when pure transition results were cached. No calibration of confidence/OOD and no novel primitive semantics have been demonstrated. See docs/specs/EXP-REP-004-DECISION-V2.md and experiments/EXP-REP-004/runs/20261102-disclosed-engineering.md.
