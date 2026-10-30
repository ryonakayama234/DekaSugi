"""ACTIVE-001 isolated finite synthetic grammar. Never imports historic scorers."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
import random
from types import MappingProxyType
from typing import Mapping

ALPHABET = ("a", "A", "b", "B", " ")
OPERATIONS = ("trim", "lower", "upper", "reverse", "drop_first", "drop_last", "replace_first_a_b", "append_a")
INPUTS = tuple("".join(letters) for length in range(4) for letters in product(ALPHABET, repeat=length))
SCHEMA = "inquiry-world/1"


def digest(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def execute(ops: tuple[str, ...], value: str) -> str:
    """Apply trusted unary operations in execution order, innermost first."""
    if type(ops) is not tuple or len(ops) > 4 or any(type(op) is not str or op not in OPERATIONS for op in ops):
        raise ValueError("invalid approved program")
    if type(value) is not str or len(value) > 3 or any(c not in ALPHABET for c in value):
        raise ValueError("invalid finite-world input")
    for op in ops:
        if op == "trim":
            value = value.strip(" ")
        elif op == "lower":
            value = value.lower()
        elif op == "upper":
            value = value.upper()
        elif op == "reverse":
            value = value[::-1]
        elif op == "drop_first":
            value = value[1:]
        elif op == "drop_last":
            value = value[:-1]
        elif op == "replace_first_a_b":
            value = value.replace("a", "b", 1)
        elif op == "append_a":
            value += "a"
    return value


@dataclass(frozen=True, slots=True)
class SemanticClass:
    class_id: str
    program: tuple[str, ...]
    output_signature: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Catalog:
    classes: tuple[SemanticClass, ...]
    by_id: Mapping[str, SemanticClass]
    universe_digest: str
    syntax_count: int


@dataclass(frozen=True, slots=True)
class InputSplit:
    public_ids: tuple[int, ...]
    query_ids: tuple[int, ...]
    audit_ids: tuple[int, ...]
    split_digest: str


def input_split(seed: int) -> InputSplit:
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("seed outside reviewed range")
    ids = list(range(len(INPUTS)))
    random.Random(seed).shuffle(ids)
    public = tuple(sorted(ids[:28]))
    query = tuple(sorted(ids[28:92]))
    audit = tuple(sorted(ids[92:]))
    if len(INPUTS) != 156 or len(set(public + query + audit)) != 156:
        raise AssertionError("world split invalid")
    return InputSplit(public, query, audit, digest({"schema": SCHEMA, "public": public, "query": query, "audit": audit}))


def build_catalog() -> Catalog:
    if len(INPUTS) != 156 or len(set(INPUTS)) != len(INPUTS):
        raise AssertionError("invalid input universe")
    known: dict[tuple[str, ...], SemanticClass] = {}
    syntax_count = 0
    for depth in range(5):
        for ops in product(OPERATIONS, repeat=depth):
            syntax_count += 1
            signature = tuple(execute(ops, value) for value in INPUTS)
            if signature not in known:
                class_id = digest({"schema": SCHEMA, "output_signature": signature})
                known[signature] = SemanticClass(class_id, ops, signature)
    classes = tuple(known.values())
    return Catalog(classes, MappingProxyType({c.class_id: c for c in classes}), digest({"schema": SCHEMA, "alphabet": ALPHABET, "inputs": INPUTS, "ops": OPERATIONS}), syntax_count)
