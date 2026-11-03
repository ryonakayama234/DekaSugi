"""G0B finite *designed* causal inquiry source. No RNG, no sealed data.

Do not claim independence of the 448 source variants. This is a complete,
versioned algebraic design-space census; it is NOT a natural-family sample.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product

OPS = (
    ("zero", "one", "u", "v", "not_u", "not_v", "xor", "and"),
    ("v", "not_u_and_v", "and", "xor", "zero", "one", "not_v", "or"),
    ("v", "and", "not_u_and_v", "xor", "zero", "one", "not_u", "or"),
)
DOMAIN = ((0, 0), (0, 1), (1, 0), (1, 1))
SOURCE_VERSION = "G0B-EXT448-v1"


def bit(expr: str, u: int, v: int) -> int:
    if expr == "zero": return 0
    if expr == "one": return 1
    if expr == "u": return u
    if expr == "v": return v
    if expr == "not_u": return 1 - u
    if expr == "not_v": return 1 - v
    if expr == "xor": return u ^ v
    if expr == "and": return u & v
    if expr == "or": return u | v
    if expr == "not_u_and_v": return (1 - u) & v
    raise ValueError("unknown source primitive")


@dataclass(frozen=True, slots=True)
class Model:
    """A single complete hidden mechanism (private to evaluator)."""
    questions: tuple[int, int, int]
    audit: tuple[int, int, int]
    weight: int = 1


@dataclass(frozen=True, slots=True)
class World:
    source_id: str
    source_choices: tuple[int, int, int]
    models: tuple[Model, Model, Model, Model]
    partition: str


def world_from_choices(choices: tuple[int, int, int]) -> World:
    if type(choices) is not tuple or len(choices) != 3 or any(type(v) is not int or not 0 <= v < 8 for v in choices):
        raise ValueError("invalid construction indices")
    models = []
    for u, v in DOMAIN:
        questions = tuple(bit(OPS[i][choices[i]], u, v) for i in range(3))
        models.append(Model(questions, (u, v, u ^ v)))
    # CAL-64 is explicitly the 4x4x4 low-index design region; whether its
    # exact structures match previously discussed exploratory code is unknown.
    partition = "CAL64_DISCLOSED" if all(i < 4 for i in choices) else "EXT448_NEW"
    return World("%d-%d-%d" % choices, choices, tuple(models), partition)


def enumerate_worlds() -> tuple[World, ...]:
    return tuple(world_from_choices(idx) for idx in product(range(8), repeat=3))


def semantic_signature(world: World) -> tuple:
    """Exact observational equivalence for declared query labels and audit roles.

    Identical signatures need not mean independent causal families; role
    permutation and different source ancestry are NOT assumed independent.
    """
    return tuple(sorted((m.questions, m.audit) for m in world.models))


def g0a_transition_rows(world: World) -> tuple:
    """Evaluator-only interop with G0A ClosedWorld (not imported here).

    States 0/1 observe the question bit; state 2 is a valid evaluator-only
    probe context but cannot be reached by any action from initial state 0.
    """
    return tuple((m.questions, m.questions, m.audit) for m in world.models)
