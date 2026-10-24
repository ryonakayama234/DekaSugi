"""EXP-0002: bounded baseline-vs-learned comparison on fixed partitions."""
from __future__ import annotations

from hashlib import sha256
import platform
import subprocess
import sys
from time import perf_counter

from packages.library import DEFAULT_REGISTRY, Registry
from packages.learning import SkillCandidate, discover_skills, registry_with_skill
from packages.protocol import (Call, Input, Program, TaskSpec, parse_task,
                               program_hash, program_to_dict, check_program, DSLValidationError)
from packages.synthesis import SearchResult, enumerate_candidates
from packages.verification import verify


def _task(task_id: str, examples: tuple[tuple[str, str], ...]) -> TaskSpec:
    return parse_task({
        "schema_version": "0.1", "task_id": task_id,
        "domain": "string_to_string",
        "examples": [{"input": x, "output": y} for x, y in examples],
        "limits": {"max_ast_nodes": 4, "max_candidates": 100},
    })


TRAIN = (
    _task("train-01", (("  RED ", "red"), (" Blue ", "blue"))),
    _task("train-02", (("  Open ", "open"), (" PENDING  ", "pending"))),
)
DEV = (_task("dev-01", ((" Foo ", "foo"), ("  BAR ", "bar"))),)
HOLDOUT = (
    _task("holdout-01", (("\tMIXED\n", "mixed"), ("  Q  ", "q"))),
    _task("holdout-02", ((" ÅBC ", "åbc"), (" A B ", "a b"))),
    _task("negative-reverse", (("ab", "ba"),)),
    _task("negative-identity", (("abc", "abc"),)),
)
EXPECTED = {
    "holdout-01": "solved", "holdout-02": "solved",
    "negative-reverse": "not_found", "negative-identity": "solved",
}


def expanded_nodes(program: Program,
                   learned: dict[str, SkillCandidate] | None = None) -> int:
    """Count primitive AST nodes after recursive expansion; detect cycles."""
    learned = learned or {}

    def count(node: Program, active: frozenset[str]) -> int:
        if isinstance(node, Input):
            return 1
        if not isinstance(node, Call):
            raise ValueError("Unsupported program")
        child_nodes = count(node.child, active)
        if node.op_id not in learned:
            return 1 + child_nodes
        if node.op_id in active:
            raise ValueError("Cyclic macro dependency")
        candidate = learned[node.op_id]
        if candidate.skill_id != node.op_id:
            raise ValueError("Skill map identity mismatch")
        if program_hash(candidate.body_ast) != candidate.body_hash:
            raise ValueError("Skill metadata body hash mismatch")
        body_nodes = count(candidate.body_ast, active | {node.op_id})
        return body_nodes - 1 + child_nodes

    return count(program, frozenset())


def _trusted_search_registry(registry: Registry,
                             learned: dict[str, SkillCandidate]) -> Registry:
    """Rebuild the execution registry from the immutable primitive allowlist.

    Registry and Primitive are public containers, so a caller can mislabel an
    existing macro as a primitive or replace a Python callable. A claimed
    semantics_version is not an attestation. Never execute those callables.
    Keep canonical primitive order and rebuild approved macro bodies from AST.
    """
    approved = DEFAULT_REGISTRY.primitives
    supplied = registry.primitives
    if len(supplied) != len(approved) + len(learned):
        raise ValueError("Registry and learned-skill metadata must match")
    for actual, canonical in zip(supplied[:len(approved)], approved):
        metadata = (actual.op_id, actual.input_type, actual.output_type,
                    actual.semantics_version)
        allowed = (canonical.op_id, canonical.input_type,
                   canonical.output_type, canonical.semantics_version)
        if metadata != allowed or actual.implementation is not canonical.implementation:
            raise ValueError("Unapproved primitive registry metadata or implementation")

    # Never run the macro implementation supplied by the caller either.
    trusted = DEFAULT_REGISTRY
    for supplied_macro in supplied[len(approved):]:
        candidate = learned.get(supplied_macro.op_id)
        if candidate is None:
            raise ValueError("Registry and learned-skill metadata must match")
        trusted = registry_with_skill(candidate, trusted)
        canonical = trusted.primitives[-1]
        actual_metadata = (supplied_macro.op_id, supplied_macro.input_type,
                           supplied_macro.output_type, supplied_macro.semantics_version)
        canonical_metadata = (canonical.op_id, canonical.input_type,
                              canonical.output_type, canonical.semantics_version)
        if actual_metadata != canonical_metadata:
            raise ValueError("Unapproved derived registry metadata")
    return trusted


def bounded_synthesize(task: TaskSpec, registry: Registry,
                       learned: dict[str, SkillCandidate] | None = None) -> SearchResult:
    """Same candidate budget and MAX EXPANDED primitive-AST nodes in both arms."""
    derived_ids = {p.op_id for p in registry.primitives
                   if p.semantics_version.startswith("derived-")}
    if derived_ids != set(learned or {}):
        raise ValueError("Registry and learned-skill metadata must match")
    # The evaluator must use precisely the AST that was registered to execute.
    # Otherwise a caller could under-report expanded cost with forged metadata.
    primitive_signatures = {
        p.op_id: (p.input_type, p.output_type)
        for p in registry.primitives if p.op_id not in derived_ids
    }
    for skill_id, candidate in (learned or {}).items():
        if candidate.skill_id != skill_id:
            raise ValueError("Skill metadata ID mismatch")
        digest = program_hash(candidate.body_ast)
        if candidate.body_hash != digest:
            raise ValueError("Skill metadata body hash mismatch")
        if registry.by_name[skill_id].semantics_version != "derived-" + digest:
            raise ValueError("Registered skill body hash mismatch")
        try:
            check_program(candidate.body_ast, primitive_signatures, max_nodes=32)
        except DSLValidationError as error:
            raise ValueError("Skill body is not primitive-only and type-safe") from error
    # Validate *all* primitive implementations and reconstruct macro closures.
    # The caller's registry must never be used as executable authority.
    registry = _trusted_search_registry(registry, learned or {})
    started = perf_counter()
    tested = 0
    digest = sha256()

    def outcome(status: str, program: Program | None) -> SearchResult:
        return SearchResult(task.task_id, status, program, tested,
                            task.limits.max_ast_nodes, task.limits.max_candidates,
                            (perf_counter() - started) * 1000, digest.hexdigest())

    for program in enumerate_candidates(registry, max_nodes=task.limits.max_ast_nodes):
        if expanded_nodes(program, learned) > task.limits.max_ast_nodes:
            continue
        if tested >= task.limits.max_candidates:
            return outcome("budget_exhausted", None)
        tested += 1
        digest.update(program_hash(program).encode("ascii") + b"\n")
        if verify(program, task.examples, registry,
                  max_nodes=task.limits.max_ast_nodes).matched:
            return outcome("solved", program)
    return outcome("not_found", None)


def _git_sha() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              check=True, text=True, timeout=3).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def run_experiment() -> dict[str, object]:
    """Train only from TRAIN; never use final outputs for skill discovery."""
    candidates = discover_skills(TRAIN)
    candidate = candidates[0] if candidates else None
    extended = registry_with_skill(candidate) if candidate else DEFAULT_REGISTRY
    learned_map = {candidate.skill_id: candidate} if candidate else {}
    comparisons: list[dict[str, object]] = []
    for task in DEV + HOLDOUT:
        base = bounded_synthesize(task, DEFAULT_REGISTRY)
        proposed = bounded_synthesize(task, extended, learned_map)
        comparisons.append({
            "task_id": task.task_id,
            "partition": "development" if task in DEV else "final_holdout",
            "baseline": base.to_dict(),
            "learned": proposed.to_dict(),
            "candidate_delta": base.tested_candidates - proposed.tested_candidates,
            "baseline_expanded_nodes": expanded_nodes(base.program) if base.program else None,
            "learned_expanded_nodes": expanded_nodes(proposed.program, learned_map)
                                    if proposed.program else None,
        })

    holdout = {row["task_id"]: row for row in comparisons if row["partition"] == "final_holdout"}
    faithful = all(
        row["baseline"]["status"] == EXPECTED[name]
        and row["learned"]["status"] == EXPECTED[name]
        for name, row in holdout.items()
    )
    benefit = bool(candidate and faithful and all(
        holdout[name]["candidate_delta"] >= 1
        for name in ("holdout-01", "holdout-02")
    ))
    no_large_regression = all(
        holdout[name]["learned"]["tested_candidates"]
        <= 2 * holdout[name]["baseline"]["tested_candidates"]
        for name in ("negative-reverse", "negative-identity")
    )
    return {
        "experiment_id": "EXP-0002",
        "plan_version": "2026-10-24-preregistered-v1",
        "status": "functional_pass" if candidate and faithful else "inconclusive",
        "search_benefit_same_task_family": benefit,
        "promotion_gate_metrics_pass": benefit and no_large_regression,
        "promotion_status": "pending_independent_review",
        "source_commit": _git_sha(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor(),
        },
        "registry": [
            {"op_id": p.op_id, "semantics_version": p.semantics_version}
            for p in DEFAULT_REGISTRY.primitives
        ],
        "train_task_ids": [t.task_id for t in TRAIN],
        "dev_task_ids": [t.task_id for t in DEV],
        "final_task_ids": [t.task_id for t in HOLDOUT],
        "candidates": [c.to_dict() for c in candidates],
        "comparisons": comparisons,
        "limits": {"max_expanded_nodes": 4, "max_candidates": 100},
        "caveat": "Macro search candidate savings != total compute or out-of-family generalization.",
    }
