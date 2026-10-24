"""EXP-0002: deterministic common-subexpression discovery, no arbitrary code."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from packages.library import DEFAULT_REGISTRY, Primitive, Registry
from packages.protocol import (
    Call, Input, Program, TaskSpec, DSLValidationError, check_program,
    program_hash, program_to_dict,
)
from packages.runtime import evaluate
from packages.synthesis import synthesize


def _subexpressions(program: Program) -> Iterable[Call]:
    """All unary AST suffixes with at least two primitive calls."""
    node = program
    while isinstance(node, Call):
        if isinstance(node.child, Call):
            yield node
        node = node.child


def _operation_ids(program: Program) -> tuple[str, ...]:
    ids: list[str] = []
    node = program
    while isinstance(node, Call):
        ids.append(node.op_id)
        node = node.child
    return tuple(sorted(set(ids)))


@dataclass(frozen=True, slots=True)
class SkillCandidate:
    skill_id: str
    body_ast: Program
    body_hash: str
    dependencies: tuple[str, ...]
    provenance: tuple[str, ...]
    occurrences: int
    status: str = "candidate"
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "skill_id": self.skill_id,
            "body_ast": program_to_dict(self.body_ast),
            "body_hash": self.body_hash,
            "dependencies": list(self.dependencies),
            "provenance": list(self.provenance),
            "occurrences": self.occurrences,
            "status": self.status,
        }


def discover_skills(tasks: tuple[TaskSpec, ...],
                    registry: Registry = DEFAULT_REGISTRY,
                    *, min_distinct_tasks: int = 2) -> tuple[SkillCandidate, ...]:
    """Find repeated typed subtrees in solved TRAIN episodes only.

    No holdout input or expected output enters this function.
    """
    if type(min_distinct_tasks) is not int or min_distinct_tasks < 2:
        raise ValueError("min_distinct_tasks must be >=2")
    if len({task.task_id for task in tasks}) != len(tasks):
        raise ValueError("Duplicate training task_id")
    groups: dict[str, tuple[Call, set[str]]] = {}
    for task in tasks:
        answer = synthesize(task, registry)
        if answer.status != "solved" or answer.program is None:
            continue
        check_program(answer.program, registry.signatures, max_nodes=32)
        observed: set[str] = set()
        for subtree in _subexpressions(answer.program):
            key = program_hash(subtree)
            if key in observed:
                continue
            observed.add(key)
            if key not in groups:
                groups[key] = (subtree, set())
            groups[key][1].add(task.task_id)
    candidates: list[SkillCandidate] = []
    for digest, (body, task_ids) in groups.items():
        if len(task_ids) < min_distinct_tasks:
            continue
        candidates.append(SkillCandidate(
            skill_id="skill_" + digest[:16],
            body_ast=body,
            body_hash=digest,
            dependencies=_operation_ids(body),
            provenance=tuple(sorted(task_ids)),
            occurrences=len(task_ids),
        ))
    return tuple(sorted(candidates, key=lambda c: (-c.occurrences, c.skill_id)))


def validate_skill(candidate: SkillCandidate, registry: Registry = DEFAULT_REGISTRY) -> None:
    """Reject forged, nested, untyped and unsupported macro metadata."""
    if candidate.schema_version != "1.0" or candidate.status != "candidate":
        raise DSLValidationError("Unsupported skill schema or status")
    if type(candidate.body_hash) is not str or program_hash(candidate.body_ast) != candidate.body_hash:
        raise DSLValidationError("Skill body hash mismatch")
    if candidate.skill_id != "skill_" + candidate.body_hash[:16]:
        raise DSLValidationError("Skill ID mismatch")
    if candidate.skill_id in registry.by_name:
        raise DSLValidationError("Skill ID collides with existing operation")
    if not isinstance(candidate.body_ast, Call) or not isinstance(candidate.body_ast.child, Call):
        raise DSLValidationError("Skill must compress >=2 primitive calls")
    check_program(candidate.body_ast, registry.signatures, max_nodes=32)
    if candidate.dependencies != _operation_ids(candidate.body_ast):
        raise DSLValidationError("Skill dependencies mismatch")
    if (candidate.occurrences < 2 or len(candidate.provenance) < 2
            or candidate.occurrences != len(candidate.provenance)
            or candidate.provenance != tuple(sorted(set(candidate.provenance)))):
        raise DSLValidationError("Invalid independent provenance")


def registry_with_skill(candidate: SkillCandidate,
                        registry: Registry = DEFAULT_REGISTRY) -> Registry:
    """Create an isolated registry; macro is interpreted using approved primitives.

    Does not mutate DEFAULT_REGISTRY or execute generated Python.
    """
    validate_skill(candidate, registry)
    body = candidate.body_ast

    def macro(value: str) -> str:
        return evaluate(body, value, registry, max_nodes=32)

    return Registry(registry.primitives + (
        Primitive(candidate.skill_id, "String", "String",
                  "derived-" + candidate.body_hash, macro),
    ))
