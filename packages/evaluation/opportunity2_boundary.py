"""OPPORTUNITY-002: independent synthetic-only bounded grammar check.

Never imports production synthesis/evaluation, historical generators, policies,
skill snapshots, private data, or any scorer. Invented fixtures only.
This is NOT historical source authenticity or an ability measurement.
"""
from __future__ import annotations

from itertools import product

PRIMITIVES = ("trim", "lower", "upper")
MACRO = "synthetic_lower_trim"
EXTENDED = PRIMITIVES + (MACRO,)
PUBLIC_EXAMPLES = (("  RED  ", "red"), ("  BLUE  ", "blue"))


class BoundaryError(ValueError):
    """Fail closed on unsupported syntax or synthetic budgets."""


def expand(program: tuple[str, ...]) -> tuple[str, ...]:
    if type(program) is not tuple:
        raise BoundaryError("program must be a tuple")
    result = []
    for op in program:
        if op == MACRO:
            result.extend(("trim", "lower"))
        elif op in PRIMITIVES:
            result.append(op)
        else:
            raise BoundaryError("unknown operation")
    return tuple(result)


def enumerate_eligible(operators: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    """Independent BFS: syntax nodes and expanded primitive nodes <= 4."""
    if type(operators) is not tuple or operators not in (PRIMITIVES, EXTENDED):
        raise BoundaryError("noncanonical synthetic registry")
    layer = ((),)
    accepted = []
    for depth in range(1, 5):
        next_layer = []
        for p in layer:
            if 1 + len(expand(p)) <= 4:
                accepted.append(p)
            if depth < 4:
                next_layer.extend(p + (op,) for op in operators)
        layer = tuple(next_layer)
    return tuple(accepted)


def independent_oracle(operators: tuple[str, ...]) -> set[tuple[str, ...]]:
    """A different enumeration algorithm: itertools Cartesian product."""
    if type(operators) is not tuple or operators not in (PRIMITIVES, EXTENDED):
        raise BoundaryError("noncanonical synthetic registry")
    return {
        p for n in range(4) for p in product(operators, repeat=n)
        if 1 + len(expand(p)) <= 4
    }


def apply(program: tuple[str, ...], value: str) -> str:
    if type(value) is not str:
        raise BoundaryError("synthetic value must be a string")
    for op in expand(program):
        if op == "trim":
            value = value.strip()
        elif op == "lower":
            value = value.lower()
        elif op == "upper":
            value = value.upper()
    return value


def first_match(operators: tuple[str, ...], budget: int) -> dict[str, object]:
    """Only the fixed, invented public examples; never a real TaskSpec API."""
    if type(budget) is not int or not 1 <= budget <= 100:
        raise BoundaryError("unsupported synthetic budget")
    for index, p in enumerate(enumerate_eligible(operators), 1):
        if index > budget:
            return {"status": "budget_exhausted", "tested": budget, "program": None}
        if all(apply(p, src) == dst for src, dst in PUBLIC_EXAMPLES):
            return {"status": "solved", "tested": index, "program": list(p)}
    return {"status": "not_found",
            "tested": len(enumerate_eligible(operators)), "program": None}


def calibrate() -> dict[str, object]:
    """Deterministic synthetic structural receipt, never scoring authorization."""
    off = enumerate_eligible(PRIMITIVES)
    on = enumerate_eligible(EXTENDED)
    if (len(off), len(on)) != (40, 47):
        raise BoundaryError("unexpected syntax counts")
    if set(off) != independent_oracle(PRIMITIVES):
        raise BoundaryError("OFF independent oracle mismatch")
    if set(on) != independent_oracle(EXTENDED):
        raise BoundaryError("ON independent oracle mismatch")
    if {expand(p) for p in on} != set(off):
        raise BoundaryError("macro expansion changed primitive support")
    b5_off, b5_on = first_match(PRIMITIVES, 5), first_match(EXTENDED, 5)
    b100_off, b100_on = first_match(PRIMITIVES, 100), first_match(EXTENDED, 100)
    if ((b5_off["status"], b5_on["status"]) != ("budget_exhausted", "solved")
            or b5_on["tested"] != 5
            or b5_on["program"] != [MACRO]
            or (b100_off["tested"], b100_on["tested"]) != (6, 5)):
        raise BoundaryError("budget witness mismatch")
    if any(apply(p, "fiz") == "zif" for p in on):
        raise BoundaryError("restricted ASCII negative witness violated")
    return {
        "schema_version": "opportunity2-synthetic-boundary/1",
        "status": "synthetic_calibration_pass",
        "off_eligible_syntax": len(off),
        "on_eligible_syntax": len(on),
        "on_expansion_equals_off_syntax": True,
        "independent_product_oracle_equal": True,
        "budget_5": {"off": b5_off, "on": b5_on},
        "budget_100": {"off": b100_off, "on": b100_on},
        "restricted_ascii_reverse_negative": True,
        "historical_skill_source_authenticated": False,
        "independent_review_completed": False,
        "new_real_scored_tasks": 0,
        "scoring_authorized": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(calibrate(), ensure_ascii=False, sort_keys=True))
