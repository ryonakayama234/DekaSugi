"""Independent R1-ENG public evidence validator.

This module intentionally does NOT import or call the synthesizer's interpreter.
It validates only already-public observations, never a private world law.
"""
from __future__ import annotations

from .core import Node, Observation, ast_size, check_history, check_point, MAX_AST_NODES


def check_ast(node: Node) -> None:
    def visit(item: Node, depth: int) -> int:
        if type(item) is not Node or item.dtype != "Bool" or depth > 9:
            raise ValueError("unknown or untyped AST")
        if type(item.op) is not str or type(item.children) is not tuple:
            raise ValueError("invalid AST node fields")
        expected = {"x": 0, "z": 0, "NOT": 1, "AND": 2, "OR": 2}
        if item.op not in expected or len(item.children) != expected[item.op]:
            raise ValueError("operator not in typed allowlist")
        return 1 + sum(visit(child, depth + 1) for child in item.children)
    if visit(node, 1) > MAX_AST_NODES or ast_size(node) > MAX_AST_NODES:
        raise ValueError("AST exceeds fixed node budget")


def evaluate_independent(node: Node, point: tuple[int, int]) -> int:
    check_ast(node)
    x, z = check_point(point)

    def interpret(item: Node) -> bool:
        if item.op == "x":
            return bool(x)
        if item.op == "z":
            return bool(z)
        if item.op == "NOT":
            return not interpret(item.children[0])
        if item.op == "AND":
            return all(interpret(c) for c in item.children)
        if item.op == "OR":
            return any(interpret(c) for c in item.children)
        raise ValueError("illegal operator")

    return int(interpret(node))


def validate_public(node: Node, history: tuple[Observation, ...]) -> dict[str, object]:
    check_ast(node)
    check_history(history)
    if not history:
        raise ValueError("no public evidence for validation")
    actual = tuple(evaluate_independent(node, o.point) for o in history)
    expected = tuple(o.answer for o in history)
    return {"schema": "HypothesisValidation/v1", "passed": actual == expected,
            "matched": sum(a == b for a, b in zip(actual, expected)),
            "total": len(expected), "ast_nodes": ast_size(node),
            "public_only": True}
