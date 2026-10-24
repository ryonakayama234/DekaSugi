"""Immutable experiment primitive definitions; not a learned library yet."""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping


@dataclass(frozen=True, slots=True)
class Primitive:
    op_id: str
    input_type: str
    output_type: str
    semantics_version: str
    implementation: Callable[[str], str]


# Ordering is a VERSIONED part of the deterministic enumerator specification.
DEFAULT_PRIMITIVES: tuple[Primitive, ...] = (
    Primitive("trim", "String", "String", "python-str-strip-v1", str.strip),
    Primitive("lower", "String", "String", "python-str-lower-v1", str.lower),
    Primitive("upper", "String", "String", "python-str-upper-v1", str.upper),
)


class Registry:
    def __init__(self, primitives: tuple[Primitive, ...] = DEFAULT_PRIMITIVES) -> None:
        if not primitives or len({p.op_id for p in primitives}) != len(primitives):
            raise ValueError("Primitive registry must contain unique operations")
        self.primitives = primitives
        self.by_name: Mapping[str, Primitive] = MappingProxyType({p.op_id: p for p in primitives})
        self.signatures: Mapping[str, tuple[str, str]] = MappingProxyType(
            {p.op_id: (p.input_type, p.output_type) for p in primitives}
        )


DEFAULT_REGISTRY = Registry()
