"""Deterministic typed enumeration baseline (no learning, no heuristics)."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from time import perf_counter
from typing import Iterator

from packages.library import DEFAULT_REGISTRY, Registry
from packages.protocol import Call, Input, Program, TaskSpec, program_hash, program_to_dict
from packages.verification import verify


@dataclass(frozen=True, slots=True)
class SearchResult:
    task_id: str
    status: str
    program: Program | None
    tested_candidates: int
    max_nodes: int
    max_candidates: int
    elapsed_ms: float
    trace_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "solved": self.status == "solved",
            "program": program_to_dict(self.program) if self.program is not None else None,
            "tested_candidates": self.tested_candidates,
            "max_nodes": self.max_nodes,
            "max_candidates": self.max_candidates,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "trace_sha256": self.trace_sha256,
        }


def enumerate_candidates(registry: Registry = DEFAULT_REGISTRY, *, max_nodes: int = 4) -> Iterator[Program]:
    """BFS by node count; each layer retains primitive declaration order.

    EXP-0001 grammar only has unary String -> String operations. No semantics-
    based pruning: semantically equivalent ASTs remain measurable candidates.
    """
    if type(max_nodes) is not int or not 1 <= max_nodes <= 32:
        raise ValueError("max_nodes out of bounds")
    layer: tuple[Program, ...] = (Input(),)
    seen: set[str] = set()
    for depth in range(1, max_nodes + 1):
        next_layer: list[Program] = []
        for program in layer:
            key = program_hash(program)
            if key not in seen:
                seen.add(key)
                yield program
            if depth < max_nodes:
                for op in registry.primitives:
                    if op.input_type == program.value_type:
                        next_layer.append(Call(op.op_id, program, op.output_type))
        layer = tuple(next_layer)


def synthesize(task: TaskSpec, registry: Registry = DEFAULT_REGISTRY) -> SearchResult:
    started = perf_counter()
    tested = 0
    digest = sha256()

    def result(status: str, program: Program | None) -> SearchResult:
        return SearchResult(task.task_id, status, program, tested, task.limits.max_ast_nodes,
                            task.limits.max_candidates, (perf_counter() - started) * 1000,
                            digest.hexdigest())

    for program in enumerate_candidates(registry, max_nodes=task.limits.max_ast_nodes):
        if tested >= task.limits.max_candidates:
            return result("budget_exhausted", None)
        tested += 1
        digest.update(program_hash(program).encode("ascii") + b"\n")
        if verify(program, task.examples, registry, max_nodes=task.limits.max_ast_nodes).matched:
            return result("solved", program)
    return result("not_found", None)
