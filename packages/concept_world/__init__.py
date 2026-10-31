"""Isolated, deterministic ConceptWorld G1. Synthetic structural study only; no scorer."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from functools import lru_cache
from itertools import product
import json
import random

ALPHABET = ("a", "A", "b", "B", " ")
OPERATIONS = ("trim", "lower", "upper", "reverse", "drop_first", "append_a")
PREDICATES = ("contains_a", "is_empty")
WORLD_ID = "concept-world-g1/0.1"

def digest(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()

def inputs() -> tuple[str, ...]:
    return tuple("".join(chars) for n in range(4) for chars in product(ALPHABET, repeat=n))

def apply_unary(op: str, value: str) -> str:
    if type(op) is not str or op not in OPERATIONS or type(value) is not str:
        raise ValueError("Unapproved unary operation or input")
    if op == "trim": return value.strip(" ")
    if op == "lower": return value.lower()
    if op == "upper": return value.upper()
    if op == "reverse": return value[::-1]
    if op == "drop_first": return value[1:]
    return value + "a"

def apply_predicate(op: str, value: str) -> bool:
    if type(op) is not str or op not in PREDICATES or type(value) is not str:
        raise ValueError("Unapproved predicate or input")
    return ("a" in value) if op == "contains_a" else value == ""

def _check_ops(ops: tuple[str, ...]) -> None:
    if type(ops) is not tuple or len(ops) > 2 or any(type(v) is not str or v not in OPERATIONS for v in ops):
        raise ValueError("Invalid <=2 unary operation chain")

@dataclass(frozen=True, slots=True)
class Program:
    predicate_id: str | None
    then_ops: tuple[str, ...]
    else_ops: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.predicate_id is not None and (type(self.predicate_id) is not str or self.predicate_id not in PREDICATES):
            raise ValueError("Invalid conditional predicate")
        _check_ops(self.then_ops)
        _check_ops(self.else_ops)
        if self.predicate_id is None and self.else_ops:
            raise ValueError("Plain program cannot have else branch")

    def to_dict(self) -> dict[str, object]:
        return {"predicate": self.predicate_id, "then_ops": list(self.then_ops), "else_ops": list(self.else_ops)}

    @property
    def program_id(self) -> str:
        return digest(self.to_dict())

def execute(program: Program, value: str) -> str:
    if type(program) is not Program or type(value) is not str:
        raise ValueError("Only approved Program and str allowed")
    selected = program.then_ops if program.predicate_id is None or apply_predicate(program.predicate_id, value) else program.else_ops
    for op in selected:
        value = apply_unary(op, value)
    return value

def execution_cost(program: Program, value: str) -> int:
    if type(program) is not Program or type(value) is not str:
        raise ValueError("Bad cost input")
    if program.predicate_id is None: return len(program.then_ops)
    return 1 + (len(program.then_ops) if apply_predicate(program.predicate_id, value) else len(program.else_ops))

def chains() -> tuple[tuple[str, ...], ...]:
    return ((),) + tuple((op,) for op in OPERATIONS) + tuple(product(OPERATIONS, repeat=2))

def enumerate_programs() -> tuple[Program, ...]:
    c = chains()
    programs = tuple(Program(None, ops) for ops in c) + tuple(
        Program(pred, left, right) for pred in PREDICATES for left in c for right in c)
    if len(programs) != 3741: raise AssertionError("G1 grammar drift")
    return programs

@dataclass(frozen=True, slots=True)
class InputSplit:
    public_ids: tuple[int, ...]
    query_ids: tuple[int, ...]
    audit_ids: tuple[int, ...]
    commitment: str

def split_inputs(seed: int) -> InputSplit:
    if type(seed) is not int: raise ValueError("Seed must be exactly int")
    indices = list(range(len(inputs())))
    random.Random(seed).shuffle(indices)
    a,b,c = tuple(sorted(indices[:28])),tuple(sorted(indices[28:92])),tuple(sorted(indices[92:]))
    return InputSplit(a,b,c,digest({"world":WORLD_ID,"public":a,"query":b,"audit":c}))

@dataclass(frozen=True, slots=True)
class SemanticCatalog:
    representatives: tuple[Program, ...]
    class_signatures: tuple[tuple[str, ...], ...]
    class_sizes: tuple[int, ...]
    world_digest: str

@lru_cache(maxsize=1)
def build_catalog() -> SemanticCatalog:
    domain = inputs()
    seen: dict[tuple[str, ...], int] = {}
    reps: list[Program] = []
    signatures: list[tuple[str, ...]] = []
    sizes: list[int] = []
    for program in enumerate_programs():
        signature = tuple(execute(program, x) for x in domain)
        if signature not in seen:
            seen[signature] = len(reps)
            reps.append(program)
            signatures.append(signature)
            sizes.append(1)
        else:
            sizes[seen[signature]] += 1
    return SemanticCatalog(tuple(reps),tuple(signatures),tuple(sizes),
        digest({"world":WORLD_ID,"domain":domain,"representatives":[p.program_id for p in reps]}))


def _trusted_catalog(candidate: SemanticCatalog) -> SemanticCatalog:
    """Canonicalize caller-supplied Catalog; a matching digest alone is insufficient."""
    canonical = build_catalog()
    if candidate is canonical: return canonical
    if type(candidate) is not SemanticCatalog:
        raise ValueError("Untrusted Catalog type")
    if (type(candidate.representatives) is not tuple or
        type(candidate.class_signatures) is not tuple or
        type(candidate.class_sizes) is not tuple or
        type(candidate.world_digest) is not str):
        raise ValueError("Untrusted Catalog containers")
    if (len(candidate.representatives) != len(canonical.representatives) or
        len(candidate.class_signatures) != len(canonical.class_signatures) or
        len(candidate.class_sizes) != len(canonical.class_sizes)):
        raise ValueError("Invalid Catalog size")
    for p in candidate.representatives:
        if (type(p) is not Program or
            type(p.predicate_id) not in (str, type(None)) or
            type(p.then_ops) is not tuple or type(p.else_ops) is not tuple or
            any(type(op) is not str for op in p.then_ops+p.else_ops)):
            raise ValueError("Untrusted Catalog representative")
    if (any(type(row) is not tuple or any(type(x) is not str for x in row)
            for row in candidate.class_signatures) or
        any(type(x) is not int for x in candidate.class_sizes)):
        raise ValueError("Untrusted semantic signatures")
    if (candidate.world_digest != canonical.world_digest or
        candidate.representatives != canonical.representatives or
        candidate.class_signatures != canonical.class_signatures or
        candidate.class_sizes != canonical.class_sizes):
        raise ValueError("Noncanonical or forged Catalog")
    return canonical

def _validate_class_ids(catalog: SemanticCatalog, class_ids: tuple[int, ...]) -> None:
    if (type(class_ids) is not tuple or not class_ids or
        len(set(class_ids)) != len(class_ids) or
        any(type(i) is not int or not 0 <= i < len(catalog.representatives) for i in class_ids)):
        raise ValueError("Invalid distinct semantic classes")

def _canonical_gini(catalog: SemanticCatalog, class_ids: tuple[int, ...], q: int) -> int:
    count = Counter(catalog.class_signatures[i][q] for i in class_ids)
    return len(class_ids)**2-sum(v*v for v in count.values())

def query_disagreement(catalog: SemanticCatalog, class_ids: tuple[int, ...], query_input_id: int) -> int:
    trusted = _trusted_catalog(catalog)
    _validate_class_ids(trusted, class_ids)
    if type(query_input_id) is not int or not 0 <= query_input_id < 156:
        raise ValueError("Invalid query ID")
    return _canonical_gini(trusted, class_ids, query_input_id)

def query_argmax(catalog: SemanticCatalog, class_ids: tuple[int, ...],
                 remaining_ids: tuple[int, ...]) -> int | None:
    trusted = _trusted_catalog(catalog)
    _validate_class_ids(trusted, class_ids)
    if (type(remaining_ids) is not tuple or len(set(remaining_ids)) != len(remaining_ids) or
            any(type(q) is not int or not 0 <= q < 156 for q in remaining_ids)):
        raise ValueError("Invalid remaining query IDs")
    if not remaining_ids: return None
    pairs = [(_canonical_gini(trusted,class_ids,q),q) for q in remaining_ids]
    maximum = max(score for score,_ in pairs)
    return min(q for score,q in pairs if score == maximum) if maximum else None
