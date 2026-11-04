"""Independent public-only Boolean interpreter and AST validator.

Do NOT import decoder, source_gateway, or a synthetic private target.
Validation of the public 4 does not certify predictions on private USE.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product

from .records import (
    MAX_AST_NODES, Node, PublicObservation, ast_dict, check_point,
    digest, public_evidence_digest, validate_public_history,
)

ARITY = {"0": 0, "1": 0, "x": 0, "y": 0, "z": 0,
         "NOT": 1, "AND": 2, "OR": 2}
VALIDATOR_VERSION = "r2-m-independent-public-interpreter/1"


def check_ast(root: Node) -> int:
    """Enforce typed Bool TREE, no user callbacks, no shared DAG subtrees."""
    visited: set[int] = set()
    count = 0

    def visit(node: Node) -> None:
        nonlocal count
        if type(node) is not Node or type(node.dtype) is not str or node.dtype != "Bool":
            raise ValueError("VALIDATION_FAILED: untyped AST node")
        if id(node) in visited:
            raise ValueError("VALIDATION_FAILED: shared DAG subtree")
        visited.add(id(node))
        count += 1
        if count > MAX_AST_NODES:
            raise ValueError("VALIDATION_FAILED: tree node budget exceeded")
        if (type(node.op) is not str or node.op not in ARITY or
                type(node.args) is not tuple or len(node.args) != ARITY[node.op]):
            raise ValueError("VALIDATION_FAILED: unknown op or wrong arity")
        for child in node.args:
            visit(child)

    visit(root)
    return count


def _interpret(node: Node, point: tuple[int, int, int]) -> int:
    """Own independent semantics; no decoder or shared runtime eval."""
    if node.op == "0":
        return 0
    if node.op == "1":
        return 1
    if node.op in ("x", "y", "z"):
        return point[{"x": 0, "y": 1, "z": 2}[node.op]]
    if node.op == "NOT":
        return 1 - _interpret(node.args[0], point)
    if node.op == "AND":
        left = _interpret(node.args[0], point)
        return _interpret(node.args[1], point) if left else 0
    if node.op == "OR":
        left = _interpret(node.args[0], point)
        return 1 if left else _interpret(node.args[1], point)
    raise ValueError("VALIDATION_FAILED: unknown primitive")


def interpret_public(node: Node, point: tuple[int, int, int]) -> int:
    check_point(point)
    check_ast(node)
    return _interpret(node, point)


@dataclass(frozen=True, slots=True)
class ValidationReceipt:
    status: str
    checked_public: int
    ast_nodes_static: int
    ast_digest: str
    public_digest: str
    validator_version: str = VALIDATOR_VERSION

    @property
    def passed(self) -> bool:
        return self.status == "PUBLIC_MATCH"


def validate_public(node: Node, history: tuple[PublicObservation, ...]) -> ValidationReceipt:
    """Four public points only. No repair or alternative candidate on failure."""
    validate_public_history(history, complete=True)
    nodes = check_ast(node)
    matches = all(_interpret(node, row.point) == row.answer for row in history)
    return ValidationReceipt(
        "PUBLIC_MATCH" if matches else "VALIDATION_FAILED",
        len(history), nodes, digest(ast_dict(node)),
        public_evidence_digest(history),
    )


def same_semantics_all_8(before: Node, after: Node) -> bool:
    """Synthetic truth-table equivalence of programs, NOT target scoring."""
    check_ast(before)
    check_ast(after)
    return all(_interpret(before, point) == _interpret(after, point)
               for point in product((0, 1), repeat=3))
