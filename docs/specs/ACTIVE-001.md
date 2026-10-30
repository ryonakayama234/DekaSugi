# ACTIVE-001 — 能動的質問選択と課題内適応 / specification v0.1

id: ACTIVE-001-SPEC
status: proposed; draft; design_only; no_scoring_authority
updated: 2026-10-30
tags: active-learning, information, epistemic-agency, trust-boundary

## Research construct and precise non-claims
The Stage I construct is **within-task active epistemic adaptation**, not across-task learning, new primitive invention, general intelligence or cross-domain transfer. The agent is allowed to select an input for an oracle and use **only** the response to update a finite version space of typed pure programs. State update: H_(t+1)={h in H_t | h(q_t)=answer}; the meaningfully *new action* is the choice of q, not acquisition of a new primitive.
Stage II (not implemented) would learn a new query policy across episodes and compare frozen pre/post policy snapshots on fresh tasks. Stage III (not implemented) would test transfer of the *abstract discrimination operation* across domain adapters. No Stage I score permits those claims.

## Why a two-world design
**World A: legacy compatibility calibration** uses the canonical frozen legacy primitive semantics (trim, lower, upper) and existing AST as a read-only reference. Small finite-string semantics collapse many syntactic ASTs to few behavior classes; good for API calibration, inadequate alone as an identification experiment. Must not import historic scorers or generate DEV/FINAL.
**World B: InquiryWorld v1** is an **isolated**, trusted, synthetic domain with five-character alphabet `a,A,b,B,space`, inputs of length 0..3 inclusive (156 unique inputs), and eight built-in unary string operations: `trim`, `lower`, `upper`, `reverse`, `drop_first`, `drop_last`, `replace_first_a_b`, `append_a`. Exactly pin semantics before study: trim uses ASCII `' '` at both ends, reverse is Python code-point reverse, drop first/last return `''` for empty input, replace only the FIRST literal lowercase `a` by `b`, append literal lowercase `a`. This is an experimenter-supplied fixed toolbox, **not learned operations**. Typed unary String->String; Input plus at most 4 calls; 1+8+8^2+8^3+8^4=4681 syntactic programs. Entire output may exceed input-length bound; evaluation is still defined.
Programs with identical 156-input output vectors form one **semantic equivalence class**; use classes (not syntax multiplicity) for the version-space weight and oracle disagreement. A class is finite-domain-equivalent, not universally equivalent beyond the domain. Choose canonical representative by fixed lexicographic (depth, operator enumeration order, serialized AST hash). Never equate a generated macro with new expressivity.

## Observation split and authority
Partition 156 input strings into 28 **public candidate** inputs, 64 **query candidate** inputs and 64 **evaluator-only** inputs, disjoint by content. Selection/seed for this partition MUST be frozen source-first, independent of any program labels or test outcomes. Exactly two distinct public examples per task, drawn exclusively from public pool by a frozen, pre-answer sampling method; all arms see exactly the same two examples. The agent may see public examples and the 64 unlabelled query inputs, its permitted hypothesis signatures, and past answers within that task, but NOT: target program ID, task generator seed, family/record source metadata, eval inputs or labels, future oracle answers, audit verdict, or evaluation acceptance metrics. Oracle answers only to a valid selected q once per task; duplicate questions are invalid. No access to external network/files/credentials from proposal logic. Answers and final audit must have separate dataflow.

## Version space and query logic
H0 = all semantic classes consistent with the two public examples; if empty => model_inconsistent. Fixed class weights: uniform 1/|H|, **not** a learned posterior nor evidence of true target probabilities.
For each unasked q in fixed query pool, partition H by predicted output. Define D(q)=1-sum_y (count_y/|H|)^2. B2 chooses maximal D(q) with tie-break by stable query input ID; D=0 for every available q => query_unidentifiable and stop (do NOT claim globally identified). Oracle gives a trusted one-answer observation; reduce H to consistent classes. Zero remaining => model_inconsistent, one remaining => identified, no questions left or used 2 => budget_exhausted unless already identified. Deterministic final representative chosen by the same preregistered priority across B0/B1/B2. A query may not be scored as an extra labelled evaluation example.
B0: zero questions. B1: up to 2 distinct uniform random questions, five fixed RNG replicates; define stop policy *identically* across B1/B2 (one class, no remaining discriminatory query, budget) and count all responses. B2: max-disagreement. Oracle cost is identical per successful query; total selector CPU is metered separately.

## Interactions and invariants
`HypothesisSet`: schema, task id, semantic-class commitments, class count, observation-order commitment, fixed-world source hash.
`QueryProposal`: task id, sequential query id, allowed input ID, algorithm/version, proposed-before-answer timestamp/order, predictive output-partition counts, disagreement rational numerator/denominator (avoid float-ranking artifacts), trace hash, no answer/target/audit.
`QueryAnswer`: proposal hash, oracle receipt, output, answered-at/order, status, no private target ID.
`BeliefUpdate`: before and after class commitments/counts, answer-receipt commitment, status.
`InquiryEpisode`: public observations and query-answer-update trace, final program representative, all costs, source commitments, no evaluator-only labels/target IDs.
`EvaluationReport`: evaluator-owned labels/verdicts, paired task IDs and arms, evaluator source identity, evidence integrity/missingness and aggregate metrics, no learner input path.
Use canonical JSON UTF-8 SHA256; simple digests establish identity, not custody, provenance authenticity or reviewer independence. All externally supplied data and AST nodes are type/length/allowlist-validated before processing.

## States and negative cases
`initialized`, `ambiguous`, `query_selected`, `answer_observed`, `updated`, terminal `identified`, `query_unidentifiable`, `budget_exhausted`, `model_inconsistent`; independent integrity state `integrity_invalid` is a hard stop. Missing answer/audit => `not_observed`, not zero performance. Report false identification, empty hypothesis, no-solution, high selector cost, invalid query ID, duplicated response, shuffled chronology, forged scores/digests, semantic duplicate skew, partition overlap, and oracle-label leakage explicitly. No arbitrary Python code execution, no dynamic imports, no production registry injection.

## Stage II/III extension boundary
Only independently authorized future SLEEP can load sanitized train episodes to propose reusable query plans. No third-audit/eval labels enter train history, and frozen policy is evaluated on disjoint held-out target families. Stage III needs separate domain adapters and shared intellectual-action representation; adapter implementation effort is not learned intelligence.

Related: [plan](../../experiments/ACTIVE-001/plan.md) / [runs](../../experiments/ACTIVE-001/runs/README.md) / [ADR](../architecture/decisions/ADR-0005-active-inquiry.md) / [Issue #93](https://github.com/ryonakayama234/DekaSugi/issues/93).

## PR2 engineering implementation status (2026-10-30; not scientific adoption)
A separate stacked implementation adds `packages/inquiry_world` and `packages/active_learning` plus inventor-only fixture tests, not a genuine evaluator. Catalog enumeration locally found 878 semantic classes over 156 test-domain inputs. The `QueryAnswer` fixture receipt does not prove independent Oracle authorship, and `EvaluationReport`/adversarial identity validation remain future work. [Engineering receipt](../../experiments/ACTIVE-001/runs/20261030-pr2-local-synthetic.md). No scored research study, validated sample power, true learner policy update or transfer claim.

## PR2 adversarial correction (2026-10-30; synthetic-only)
- Accept an `InputSplit` only after full 28/64/64 partition, typed IDs, uniqueness, non-overlap and digest validation. The active session stores a commitment to public and query pool IDs; evaluator-only input labels remain inaccessible.
- Reconstruct the complete canonical semantic-class set from two public examples and the ordered answer history at every public operation. Reject duplicate/reweighted semantic IDs, unsound status, exceeded budget, impossible query history, and modified input pools. `query_unidentifiable` requires absence of remaining discriminatory queries.
- Recompute B2 true maximum Gini (including tie-break); replay B1 deterministic random selector using `QueryProposal.random_seed`. Hash-only equivalence of a proposed input is not enough. Note: selecting a seed after seeing outcomes remains scientifically invalid; external seed precommitment awaits PR3.
- Original synthetic tests must unconditionally assert that the critical scenario is ambiguous. Adversarial tests are explicitly included in CI-SAFE-V2 allowlist. This produces engineering evidence only, never independently authenticated Oracle evidence or learned competence.
