# EXP-REP-005-DIAG — When should an agent invent a concept?

id: EXP-REP-005-DIAG
status: proposed_design_only
updated: 2026-11-02
tags: representation, active-learning, counterexample, diagnosis, wake-sleep
issue: https://github.com/ryonakayama234/DekaSugi/issues/142

## Research decision candidate
Primary module: future packages/representation_repair (NOT IMPLEMENTED).
Supporting boundaries: packages/active_learning, typed interpreter, independent evaluation, Snapshot storage.
This is the FIRST MILESTONE of EXP-REP-005, not permission to implement, score, publish, or merge.
Historical EXP-REP-004/004R source, evidence and failed H-ACT gate are immutable.

**Core question:** Can a learner distinguish lack of observations, ineffective inquiry, and genuine hypothesis-language insufficiency from paid public interactions, without reading generator truth, private labels, or outcome-based posthoc tuning?

## Why
EXP-REP-004R's corrected role-invariant semantics removed the old query switch in 108 disclosed adaptive paths. Its TRAIN64 seven-body prior equals preinstalled STATIC-MACRO on all 1,735 finite semantic candidates (0/1/2 relations -> 1/4/13). Corrected 11,520 scoring trials were NOT RUN. These facts do not prove that no query policy works, but do invalidate learned-novelty claims from that comparison. See #139 and Draft #141.

## Competing alternatives (no preferred implementation until evidence)
| Candidate | Testable expectation | Risk / confound | Disposition for first milestone |
|---|---|---|---|
| More exposure / repeated training | Existing representation becomes sufficient | Identical deterministic replay supplies no new information; counts can be misleading | retain as controlled reference |
| Context/history-aware inquiry | Better paid questions within H0 | Policy advantage mistaken for learned representation | directly test |
| Counterexample-directed representation repair | Old hypothesis set provably inadequate; typed candidate explains novel evidence | Expanded grammar alone gives unfair head start | directly test after expressibility gate |
| Wake–Sleep replay / skill activation history | Independent-family transfer at reduced cost | Memorizing policy traces or family frequency | defer until a mechanism exists |
| Neural-guided search | Faster bounded exploration | Compute, data and implementation confounds | defer, not prohibited |

## Scientific identification: the 2 x 2 experiment
Factor 1: **representation** H0 = original validated finite grammar; Hplus = bounded typed extension.
Factor 2: **inquiry** P0 = fixed strong active policy; Pctx = state/history-conditioned active policy.
Compare H0/P0, H0/Pctx, Hplus/P0 and Hplus/Pctx using identical paid questions, computational budgets, priors declared before evaluation and the same evidence visibility. Add (a) learned repair candidate, (b) preinstalled Hplus STATIC comparator, (c) policy-only learner, (d) episodic lookup and (e) body-off ablation.
The static Hplus control must have the same expressible semantic candidate space as learned Hplus. A gain over H0 alone demonstrates capacity, NOT learning.

## Diagnosis and epistemic limits
Let O_t be the chronological sequence of paid public interventions and responses. V0(O_t) is the set of H0 programs consistent with all of O_t. Vplus(O_t) is defined analogously with Hplus.
- If V0(O_t) is nonempty, old representation has not yet been *publicly falsified*. Poor choices may indicate inquiry/search limitations, insufficient evidence, or ambiguity.
- If V0(O_t) is empty AND Vplus(O_t) nonempty, a publicly witnessed mismatch exists relative to these checked deterministic grammars. An independent witness must reproduce it under all relevant role renamings.
- If both sets are empty, abstain as unsupported, inconsistent, or outside Hplus. Do not force a new concept.
- If all feasible remaining paid questions yield the same answer under still-viable alternatives, record UNIDENTIFIABLE under the specified horizon. Do not hallucinate distinguishability.
- A model-compatible prefix does not prove H0 can express the full hidden law. Conversely, a failure on secret evaluation samples must not be a training signal.

## Finite identifiability gate
Before choosing a toy world, enumerate behavior signatures for H0 and Hplus on an explicitly finite state/action/sequence universe. Exhibit at least one Hplus behavior not expressible by H0, prove it by exhaustive signatures or an auditable equivalent, and independently show a LEGAL paid observation sequence capable of exposing that gap. Merely changing syntax or naming a predicate fails this gate. If no witness exists, STOP and report that this formulation cannot test representational invention.

## Candidate lifecycle and safety
Wake public observation -> mismatch diagnosis -> typed candidate invention -> counterexample test -> Sleep canonicalize and retain candidate evidence -> content-addressed Snapshot -> fresh-process USE -> independent evaluation.
A repair AST is always a candidate until independent gates pass. The only executed semantics are allowlisted typed interpreter operations; no generated Python/shell is executed. Store explicit version, preconditions, role binding, canonical AST, counterexamples, validation traces and hashes. Hidden labels, target-family/source seeds and future evaluation observations never enter the learner or Snapshot.

## Scientific decision criteria (numerical thresholds NOT YET FROZEN)
G0: independently review split, costs, admissible grammars, finite proof procedure, controls and stop rules.
G1: validate public/private separation, role-permutation invariance and legally priced multi-step inquiry.
G2: machine-check old-vs-extended semantic witness and feasible distinguishing intervention.
G3: implement paid Wake -> repair -> Sleep -> save/load -> fresh USE, with deliberately unrepairable and misleading controls.
G4: compare strong matched fixed/learned baselines and ablations; separate representation L0, search L1, inquiry L2 and transfer L3.
G5: disclosed engineering-only evaluation after independent exact-head review. Separate F0 authorization and NEW sealed families required for confirmatory FINAL.
G6: report signed family-unit effects, calibration/abstention, accuracy, paid actions, real interpreter dispatch, CPU/wall/RSS (if measured), training and storage amortization. Failures and missing values remain explicit.

Do not set or revise thresholds after viewing heldout performance. The eventual local learning curve must distinguish new *independent worlds* from repeated SGD epochs. Replaying deterministic traces cannot by itself be evidence of more knowledge.

## Research foundations, not claimed results
- Angluin, Learning regular sets from queries and counterexamples (1987), https://doi.org/10.1016/0890540187900526
- Clarke et al., Counterexample-guided Abstraction Refinement (2000), https://web.stanford.edu/class/cs357/cegar.pdf
- Ellis et al., DreamCoder Wake–Sleep library learning (2021), https://doi.org/10.1145/3453483.3454080
These are conceptual analogies; DekaSugi does not inherit their guarantees.
