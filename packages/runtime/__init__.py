"""Interpreter for explicitly allowlisted, type-checked, bounded ASTs."""
from __future__ import annotations
from packages.library import DEFAULT_REGISTRY, Registry
from packages.protocol import Call, Input, Program, DSLValidationError, check_program


def evaluate(program: Program, value: str, registry: Registry = DEFAULT_REGISTRY, *, max_nodes: int = 32) -> str:
    if type(value) is not str:
        raise DSLValidationError("Runtime input must be String")
    check_program(program, registry.signatures, max_nodes=max_nodes)

    def run(node: Program) -> str:
        if isinstance(node, Input):
            return value
        if isinstance(node, Call):
            return registry.by_name[node.op_id].implementation(run(node.child))
        raise DSLValidationError("Unsupported AST")

    return run(program)
