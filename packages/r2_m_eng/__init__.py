"""R2-M-ENG stages 1-3: artificial engineering components only.

Public exports remain minimal. The evaluator-facing synthetic runner exists
as a separate explicit module, not a package-level export. No scientific
scoring, learned policy or closure certification is exposed here.
"""
from .records import (
    CANDIDATE_BUDGET, CLOSURE_STATUS, FAMILY_SIZE, FAMILY_VERSION,
    MAX_AST_NODES, M_GAP, M_USE, PENDING_ARMS, PRIVATE_INPUTS,
    PUBLIC_POINTS, Node, PublicObservation, SchemaFrame,
)
from .decoder import DecodeResult, compile_affine, decode_public
from .validator import ValidationReceipt, check_ast, interpret_public, validate_public
from .sleep_lite import SleepReceipt, sleep_lite

__all__ = [
    "CANDIDATE_BUDGET", "CLOSURE_STATUS", "FAMILY_SIZE", "FAMILY_VERSION",
    "MAX_AST_NODES", "M_GAP", "M_USE", "PENDING_ARMS", "PRIVATE_INPUTS",
    "PUBLIC_POINTS", "Node", "PublicObservation", "SchemaFrame",
    "DecodeResult", "compile_affine", "decode_public", "ValidationReceipt",
    "check_ast", "interpret_public", "validate_public",
    "SleepReceipt", "sleep_lite",
]
