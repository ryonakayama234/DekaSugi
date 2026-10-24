"""Typed DSL structures and bounded task contracts (EXP-0001)."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping


class DSLValidationError(ValueError):
    """Malformed tasks, ASTs, or unsupported types."""


def _positive_int(value: object, key: str, ceiling: int) -> int:
    if type(value) is not int or not (1 <= value <= ceiling):
        raise DSLValidationError(f"{key} must be an integer in [1, {ceiling}]")
    return value


@dataclass(frozen=True, slots=True)
class Input:
    value_type: str = "String"


@dataclass(frozen=True, slots=True)
class Call:
    op_id: str
    child: Program
    value_type: str = "String"


Program = Input | Call


@dataclass(frozen=True, slots=True)
class Example:
    input: str
    output: str


@dataclass(frozen=True, slots=True)
class Limits:
    max_ast_nodes: int = 4
    max_candidates: int = 5000


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    examples: tuple[Example, ...]
    limits: Limits = Limits()
    domain: str = "string_to_string"
    schema_version: str = "0.1"


def parse_task(data: object) -> TaskSpec:
    if not isinstance(data, dict):
        raise DSLValidationError("TaskSpec must be an object")
    if data.get("schema_version") != "0.1" or data.get("domain") != "string_to_string":
        raise DSLValidationError("Unsupported schema_version or domain")
    task_id = data.get("task_id")
    if not isinstance(task_id, str) or not 1 <= len(task_id) <= 128:
        raise DSLValidationError("task_id must be a nonempty string (<=128)")
    examples = data.get("examples")
    if not isinstance(examples, list) or not 1 <= len(examples) <= 256:
        raise DSLValidationError("examples must be a list of 1..256 items")
    checked = []
    for item in examples:
        if not isinstance(item, dict) or type(item.get("input")) is not str or type(item.get("output")) is not str:
            raise DSLValidationError("examples require string input/output")
        if len(item["input"]) > 4096 or len(item["output"]) > 4096:
            raise DSLValidationError("example strings must be <=4096 characters")
        checked.append(Example(item["input"], item["output"]))
    raw_limits = data.get("limits", {})
    if not isinstance(raw_limits, dict):
        raise DSLValidationError("limits must be an object")
    limits = Limits(
        _positive_int(raw_limits.get("max_ast_nodes", 4), "max_ast_nodes", 32),
        _positive_int(raw_limits.get("max_candidates", 5000), "max_candidates", 100000),
    )
    return TaskSpec(task_id, tuple(checked), limits)


def program_to_dict(program: Program) -> dict[str, Any]:
    if isinstance(program, Input):
        return {"node_kind": "input", "type": program.value_type}
    if isinstance(program, Call):
        return {"node_kind": "call", "type": program.value_type, "op_id": program.op_id,
                "children": [program_to_dict(program.child)]}
    raise DSLValidationError("Unknown AST node")


def parse_program(raw: object, *, depth: int = 0) -> Program:
    if depth > 32 or not isinstance(raw, dict):
        raise DSLValidationError("AST too deep or not an object")
    kind = raw.get("node_kind")
    if kind == "input":
        if set(raw) != {"node_kind", "type"}:
            raise DSLValidationError("Invalid input AST fields")
        return Input(raw["type"])
    if kind == "call":
        if set(raw) != {"node_kind", "type", "op_id", "children"}:
            raise DSLValidationError("Invalid call AST fields")
        children = raw["children"]
        if not isinstance(children, list) or len(children) != 1:
            raise DSLValidationError("Only unary calls are supported")
        return Call(raw["op_id"], parse_program(children[0], depth=depth + 1), raw["type"])
    raise DSLValidationError("Unknown node_kind")


def check_program(program: Program, signatures: Mapping[str, tuple[str, str]], *, max_nodes: int = 32) -> int:
    """Validate all nodes, type flow and budget BEFORE any evaluation."""
    def visit(node: Program, remaining: int) -> tuple[str, int]:
        if remaining <= 0:
            raise DSLValidationError("AST exceeds node budget")
        if isinstance(node, Input):
            if node.value_type != "String":
                raise DSLValidationError("Input type must be String")
            return node.value_type, 1
        if not isinstance(node, Call) or not isinstance(node.op_id, str):
            raise DSLValidationError("Invalid call node")
        if node.op_id not in signatures:
            raise DSLValidationError(f"Unknown primitive: {node.op_id}")
        input_type, output_type = signatures[node.op_id]
        child_type, child_nodes = visit(node.child, remaining - 1)
        if child_type != input_type or node.value_type != output_type:
            raise DSLValidationError(f"Type mismatch at {node.op_id}")
        return output_type, child_nodes + 1

    return visit(program, max_nodes)[1]


def program_hash(program: Program) -> str:
    return sha256(json.dumps(program_to_dict(program), sort_keys=True,
                             separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
