"""Independent example matching: acceptance never trusts a synthesizer's success flag."""
from __future__ import annotations
from dataclasses import dataclass
from packages.library import DEFAULT_REGISTRY, Registry
from packages.protocol import Example, Program, DSLValidationError
from packages.runtime import evaluate


@dataclass(frozen=True, slots=True)
class Verification:
    matched: bool
    passed: int
    total: int


def verify(program: Program, examples: tuple[Example, ...], registry: Registry = DEFAULT_REGISTRY,
           *, max_nodes: int = 32) -> Verification:
    if not examples:
        raise DSLValidationError("Verification requires at least one example")
    passed = sum(evaluate(program, sample.input, registry, max_nodes=max_nodes) == sample.output
                 for sample in examples)
    return Verification(passed == len(examples), passed, len(examples))
