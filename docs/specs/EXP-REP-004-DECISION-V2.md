# EXP-REP-004 — Executable Concept Learning: implemented engineering decision V2
tags: research, experimental, executable-concept, active-learning, synthetic

id: EXP-REP-004-DECISION-V2
status: IMPLEMENTED_DISCLOSED_ENGINEERING / POSITIVE_MECHANISM / NEGATIVE_QUERY_VALUE / NOT_FORMAL
updated: 2026-11-02
issue: https://github.com/ryonakayama234/DekaSugi/issues/136
historical_design: EXP-REP-004-DECISION-V1.md

## Chosen research object

An agent must (1) pay for real public observations of a hidden causal world; (2) infer typed variable-bound executable relations; (3) generalize templates across different inferred semantic families; (4) save and restore a Snapshot; (5) execute the acquired AST within fresh-world inquiry and prediction; (6) commit its prediction before evaluator-only 64-transition audit; and (7) compare matched learners, ablations, and strong fixed-grammar search. This is symbolic induction, **not** gradient-trained neural intelligence, autonomous new interpreter primitive invention or general dialogue.

## Formal world and semantic-equivalence correction

- Four observed Boolean positions, anonymous IDs, all-zero start, two charged operations: set(i,bit) and pulse(i), cost 1 each including no-ops. No free reset within an episode.
- Hidden grammar: zero, one or two distinct direct/guarded XOR edges. Pulse effect is concurrent, evaluated against the entire *pre-action* state. Self targets are excluded and a condition's guard differs from its source and target.
- 60 primitive edge syntaxes, 1,831 zero-to-two-edge syntactic worlds, 1,735 distinct complete transition signatures, **85 families up to four-variable renaming**. Family counts verified in executable enumeration; no pseudoreplication of renamed world IDs.
- The earlier V1 proposed 64 independent train families alongside 24 distinct unseen families, which cannot fit the n4 finite universe. Implemented V2 has 32 unique TRAIN families, seen-ID controls reusing 12 of those, 12 unseen CHAIN composition families, 12 other unseen 2-edge families, and 12 out-of-grammar 3-edge worlds. Up to 64 TRAIN worlds repeat those 32 families with new role permutations. Source split hash is locked in the reported run.
- In-domain truth rules are retained inside host Session. Sleep takes only contiguous charged before/action/after observations; inferred family and edge relations are derived from surviving *public evidence* hypotheses, not supplied by host metadata.

## Chosen implementation and limitations

- Python 3.12+, standard library only, WSL2/Linux/CPU, immutable/fail-closed canonical Snapshot and SHA-256 integrity, typed pure AST interpretation (not dynamic Python/eval).
- Full fixed 0–2-edge hypothesis-space filtering and bounded 1–2-operation information-gain planning (two-step set→pulse has fully charged cost and the planner executes only the first action before replanning).
- Wake obtains 100 paid operations per train world by state-basis probing. Sleep extracts guards (ALWAYS/GATE0/GATE1) and four concurrent 2-edge topology macros (CHAIN/FANOUT/FANIN/OTHER), retaining templates with support from >=3 inferred semantic families, positive evidence hashes and negative applicability witnesses where present. Reusable relation bodies are interpreted and bound at USE; bounded caches memoize *pure semantics* but no evaluator truth.
- Interpreted composition macros use typed binding to candidate edges already inferred from public histories. They do not invent the underlying primitive operators, and the same macro family can be specified statically. Treat AST invocation and real new abstract semantics as separate claims.
- The learned-composition query policy adds prior weight for inferred candidates that satisfy executable learned bodies. Its LA control hides bodies only from the query policy and shares the learned prediction path; BODY-OFF removes them entirely. FA uses the full fixed grammar; LR and ER receive equal TRAIN exposure via inferred semantic family summaries; STATIC-MACRO executes the same family of human-preinstalled templates; FX is a fixed schedule.
- Current weakness: no explicit out-of-grammar anomaly detector/calibrated abstention within budgets <=8, so 3-edge worlds are not reliably recognized. Model predictions there are unreliable and reported as such. CPU/RSS and amortization are not validated by a common independent metering protocol.

## Operational falsifiability

M0 implementation and strict source checks: engineering test. M1 finite semantic space: enumerated, but a fully independent all-history NO_OPPORTUNITY certificate is NOT delivered. M2 train->AST->save->load->execute: limited symbolic engineering PASS. M3 actual paid-history concept-query intervention: PASS on a development-only fixture. M4 new-family query utility: NEGATIVE (LQ below LA/FA). M5 concept-unique learning beyond human installed templates: FAIL (LQ equals STATIC-MACRO). M6 OOD safe abstention: FAIL (0 abstentions in the disclosed OOD stratum).

Disclosed score protocol: 48 synthetic worlds x 8 arms x B={0,1,2,4,8} = 1,920 independent arm/budget executions. After prediction commit, the evaluator audits 16 states x 4 pulse operations = 64 exhaustive transitions per trial (122,880 audit checks). Distinct-family, not transition or budget, is the descriptive effect unit.

**Scientific integrity:** V2 source and methods are written down *after* the disclosed result was computed. Hence this is a reproducible, disclosed engineering pilot, NOT a formally preregistered independent F0/DEV/FINAL test, not a powered causal-generalization claim and not a release-model promotion. For a future formal study, freeze source/split, policy, code SHA and score thresholds BEFORE any new independent holdout is scored. Historical sealed records were not accessed.

See the immutable scored receipt at experiments/EXP-REP-004/runs/20261102-disclosed-engineering.md and complete compressed raw score archive.
