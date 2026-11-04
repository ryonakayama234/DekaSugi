"""One-shot public-only affine coefficient decoder; deterministic typed TREE compiler.

The family and XOR rule are human-supplied biases, not invented semantics.
This module never imports any evaluator/private source or sees USE labels.
"""
from __future__ import annotations
from dataclasses import dataclass

from .records import (
    CANDIDATE_BUDGET, COMPILER_VERSION, FAMILY_SIZE, FAMILY_VERSION,
    H0_ORDER, MAX_AST_NODES, Node, PublicObservation, SchemaFrame,
    ast_dict, ast_size, digest, public_evidence_digest, scan_h0,
    validate_public_history,
)


def _clone(node: Node) -> Node:
    return Node(node.op, tuple(_clone(child) for child in node.args), node.dtype)


def _xor(left: Node, right: Node) -> Node:
    """Expand each operand TWICE as independent subtree copies, not a DAG."""
    return Node("OR", (
        Node("AND", (_clone(left), Node("NOT", (_clone(right),)))),
        Node("AND", (Node("NOT", (_clone(left),)), _clone(right))),
    ))


def compile_affine(coefficients: tuple[int, int, int, int]) -> Node:
    if type(coefficients) is not tuple or len(coefficients) != 4 or any(
        type(x) is not int or x not in (0, 1) for x in coefficients
    ):
        raise ValueError("INVALID: affine coefficients")
    a, b, c, d = coefficients
    terms = [Node(name) for bit, name in zip((a, b, c), ("x", "y", "z"))
             if bit == 1]
    if not terms:
        result = Node("0")
    else:
        result = terms[0]
        for term in terms[1:]:
            result = _xor(result, term)
    if d:
        result = Node("NOT", (result,))
    if ast_size(result) > MAX_AST_NODES:
        raise ValueError("VALIDATION_FAILED: compiler exceeded 32 tree nodes")
    return result


@dataclass(frozen=True, slots=True)
class DecodeResult:
    status: str
    body: Node | None
    certificate: SchemaFrame
    concept: SchemaFrame | None
    coefficients: tuple[int, int, int, int] | None
    decoder_invocations: int
    candidates_generated: int
    family_size: int = FAMILY_SIZE
    candidate_budget: int = CANDIDATE_BUDGET


def decode_public(history: tuple[PublicObservation, ...]) -> DecodeResult:
    """Decode only four ordered public receipts; incomplete is non-identifiable."""
    validate_public_history(history)
    base = {"method_version": "R2-M-20261104-SINGLE-METHOD-V2-PROPOSAL",
            "family": FAMILY_VERSION, "public_digest": public_evidence_digest(history),
            "design_rank": len(history), "h0_object_order": list(H0_ORDER),
            "h0_consistent": list(scan_h0(history)),
            "h0_effective": "UNKNOWN", "closure_status": "UNKNOWN",
            "m_gap": "UNKNOWN", "candidate_budget": CANDIDATE_BUDGET,
            "family_size": FAMILY_SIZE}
    if len(history) < 4:
        base.update(status="UNIDENTIFIABLE",
                    reason="Q001 response missing; c coefficient not identified",
                    version_space_size=2 ** (4 - len(history)))
        certificate = SchemaFrame("HypothesisCertificate/v2", "public", base)
        return DecodeResult("UNIDENTIFIABLE", None, certificate, None, None, 0, 0)

    r000, r100, r010, r001 = (row.answer for row in history)
    d = r000
    a, b, c = r100 ^ d, r010 ^ d, r001 ^ d
    coefficients = (a, b, c, d)
    body = compile_affine(coefficients)
    h0 = scan_h0(history)
    status = "SUFFICIENT_H0" if h0 else "MISMATCH_CANDIDATE"
    base.update(status=status, reason="unique F_aff coefficients from public rank 4",
                version_space_size=1, coefficients_from_public=list(coefficients))
    certificate = SchemaFrame("HypothesisCertificate/v2", "public", base)
    tree = ast_dict(body)
    concept = SchemaFrame("ConceptBody/v2", "public", {
        "family": FAMILY_VERSION,
        "compiler_version": COMPILER_VERSION,
        "coefficients_from_public": list(coefficients),
        "public_digest": public_evidence_digest(history),
        "ast": tree, "ast_nodes_static": ast_size(body),
        "ast_digest": digest(tree),
        "validated": False,
        "decoder_invocations": 1, "family_size": FAMILY_SIZE,
        "candidate_budget": CANDIDATE_BUDGET, "candidates_generated": 1,
        "provenance": "public_only_coefficient_identification",
    })
    return DecodeResult(status, body, certificate, concept, coefficients, 1, 1)
