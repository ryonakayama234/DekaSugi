"""Meaning-preserving AND/OR commutative ordering, never law revision.

The receipt concerns program equivalence under all eight synthetic inputs;
it is NOT a private USE score, scientific experiment, or body promotion.
"""
from __future__ import annotations
from dataclasses import dataclass

from .records import Node, PublicObservation, ast_dict, canonical, digest
from .validator import check_ast, same_semantics_all_8, validate_public


def _sorted_commutative(node: Node) -> Node:
    children = tuple(_sorted_commutative(child) for child in node.args)
    if node.op in ("AND", "OR"):
        children = tuple(sorted(children, key=lambda n: canonical(ast_dict(n))))
    return Node(node.op, children, node.dtype)


@dataclass(frozen=True, slots=True)
class SleepReceipt:
    operation: str
    before_digest: str
    after_digest: str
    public_digest: str
    meaning_preserved_all_8: bool
    validator_status: str


def sleep_lite(body: Node, history: tuple[PublicObservation, ...]) -> tuple[Node, SleepReceipt]:
    check_ast(body)
    original = validate_public(body, history)
    if not original.passed:
        raise ValueError("VALIDATION_FAILED: original body fails public evidence")
    canonical_body = _sorted_commutative(body)
    check_ast(canonical_body)
    revised = validate_public(canonical_body, history)
    equivalent = same_semantics_all_8(body, canonical_body)
    if not revised.passed or not equivalent:
        raise ValueError("VALIDATION_FAILED: Sleep-lite would change semantics")
    return canonical_body, SleepReceipt(
        "AND_OR_COMMUTATIVE_ORDER_ONLY",
        digest(ast_dict(body)), digest(ast_dict(canonical_body)),
        original.public_digest, equivalent, revised.status,
    )
