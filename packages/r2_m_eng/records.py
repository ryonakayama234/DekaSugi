"""R2-M-ENG stage 1 public records and typed Boolean tree; synthetic-only.

No source or evaluator module is imported here. Versioned later-stage records
are SCHEMA FRAMES, not evidence of an executed experiment.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any

METHOD_VERSION = "R2-M-20261104-SINGLE-METHOD-V2-PROPOSAL"
FAMILY_VERSION = "F_aff_3bit_16"
COMPILER_VERSION = "r2-m-affine-tree/1"
MAX_AST_NODES = 32
FAMILY_SIZE = CANDIDATE_BUDGET = 16
DECODER_INVOCATIONS_MAX = 1
PUBLIC_POINTS = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
PRIVATE_INPUTS = ((0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1))
H0_ORDER = ("0", "1", "x", "!x", "y", "!y", "z", "!z")
SCHEMA_ROLES = {
    "PublicStep/v2": "public",
    "HypothesisCertificate/v2": "public",
    "ConceptBody/v2": "public",
    "Snapshot/v2": "public",
    "UseTrace/v2": "public",
    "ScoreReceipt/v2": "evaluator",
}
# Frames for the later stages are deliberately NOT a policy learner / oracle API.
PENDING_ARMS = {"F01": "NOT_EVALUATED", "F11": "NOT_EVALUATED"}
ORACLE_REF_ROLE = "evaluator"
CLOSURE_STATUS = "UNKNOWN"
M_GAP = "UNKNOWN"
M_USE = "NOT_CERTIFIED"


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def check_bit(value: object) -> int:
    if type(value) is not int or value not in (0, 1):
        raise ValueError("INVALID: Bool must be an exact int 0/1")
    return value


def check_point(value: object) -> tuple[int, int, int]:
    if type(value) is not tuple or len(value) != 3:
        raise ValueError("INVALID: exact 3bit tuple required")
    for bit in value:
        check_bit(bit)
    return value


def check_sha(value: object) -> str:
    if (type(value) is not str or len(value) != 64 or
            any(c not in "0123456789abcdef" for c in value)):
        raise ValueError("INVALID: canonical sha256 digest required")
    return value


@dataclass(frozen=True, slots=True)
class Node:
    """Typed, unshared Bool tree. Never an executable Python expression."""
    op: str
    args: tuple["Node", ...] = ()
    dtype: str = "Bool"


def ast_dict(node: Node) -> dict[str, Any]:
    if type(node) is not Node:
        raise ValueError("INVALID: untrusted AST")
    return {"type": node.dtype, "op": node.op,
            "args": [ast_dict(child) for child in node.args]}


def ast_size(node: Node) -> int:
    return 1 + sum(ast_size(child) for child in node.args)


@dataclass(frozen=True, slots=True)
class PublicObservation:
    seq: int
    point: tuple[int, int, int]
    answer: int
    paid: int
    legal_digest: str
    precommit: str | None
    received_at: int

    def as_dict(self) -> dict[str, object]:
        return {"seq": self.seq, "point": list(self.point),
                "answer": self.answer, "paid": self.paid,
                "legal_digest": self.legal_digest, "precommit": self.precommit,
                "received_at": self.received_at}


@dataclass(frozen=True, slots=True)
class PublicStep:
    event: str
    seq: int
    point: tuple[int, int, int]
    legal_actions: tuple[tuple[int, int, int], ...]
    legal_digest: str
    event_at: int
    answer: int | None = None
    paid_cost: int = 0
    precommit: str | None = None
    prediction: int | None = None

    def as_dict(self) -> dict[str, object]:
        return {"schema": "PublicStep/v2", "event": self.event,
                "seq": self.seq, "point": list(self.point),
                "legal_actions": [list(p) for p in self.legal_actions],
                "legal_digest": self.legal_digest, "event_at": self.event_at,
                "answer": self.answer, "paid_cost": self.paid_cost,
                "precommit": self.precommit, "prediction": self.prediction}


def validate_public_history(history: object, *, complete: bool = False) -> tuple[PublicObservation, ...]:
    if type(history) is not tuple or not (0 <= len(history) <= 4):
        raise ValueError("INVALID: public history shape")
    if complete and len(history) != 4:
        raise ValueError("UNIDENTIFIABLE: Q001 response missing")
    for i, record in enumerate(history):
        if type(record) is not PublicObservation:
            raise ValueError("INVALID: public observation type")
        if type(record.seq) is not int or record.seq != i:
            raise ValueError("INVALID: observation order")
        if check_point(record.point) != PUBLIC_POINTS[i]:
            raise ValueError("INVALID: wrong public point or order")
        check_bit(record.answer)
        if type(record.paid) is not int or record.paid != int(i == 3):
            raise ValueError("INVALID: paid cost mismatch")
        check_sha(record.legal_digest)
        if i == 3:
            check_sha(record.precommit)
        elif record.precommit is not None:
            raise ValueError("INVALID: initial observation has precommit")
        if type(record.received_at) is not int or record.received_at < 0:
            raise ValueError("INVALID: receipt timestamp")
        if i and record.received_at < history[i - 1].received_at:
            raise ValueError("INVALID: nonmonotonic timestamps")
    return history


def public_evidence_digest(history: tuple[PublicObservation, ...]) -> str:
    validate_public_history(history)
    return digest([obs.as_dict() for obs in history])


def _check_public_keys(obj: object) -> None:
    """Deny private provenance recursively in any public schema frame."""
    forbidden = ("private", "secret", "target", "seed", "oracle",
                 "source_law", "heldout", "use_label", "score_outcome")
    if type(obj) is dict:
        for key, value in obj.items():
            if type(key) is not str or any(token in key.lower() for token in forbidden):
                raise ValueError("INVALID: private field in public record")
            _check_public_keys(value)
    elif type(obj) in (tuple, list):
        for value in obj:
            _check_public_keys(value)
    elif obj is not None and type(obj) not in (str, int, float, bool):
        raise ValueError("INVALID: unsupported public value")


@dataclass(frozen=True, slots=True)
class SchemaFrame:
    """Role-checked schema envelope; not a scientific receipt or snapshot.

    Later stages implement full per-schema validation and immutable custody.
    An evaluator-only frame cannot be serialized via public_dict().
    """
    schema: str
    role: str
    payload: dict[str, object]

    def __post_init__(self) -> None:
        if self.schema not in SCHEMA_ROLES or self.role != SCHEMA_ROLES[self.schema]:
            raise ValueError("INVALID: schema role mismatch")
        if type(self.payload) is not dict:
            raise ValueError("INVALID: schema payload must be a dict")
        if self.role == "public":
            _check_public_keys(self.payload)
        if self.schema == "HypothesisCertificate/v2":
            if self.payload.get("closure_status") != "UNKNOWN" or self.payload.get("m_gap") != "UNKNOWN":
                raise ValueError("INVALID: ENG closure must stay UNKNOWN")
        if self.schema == "Snapshot/v2":
            if self.payload.get("closure_status") != "UNKNOWN":
                raise ValueError("INVALID: ENG closure must stay UNKNOWN")
        if self.schema == "UseTrace/v2" and self.payload.get("arm") in ("F01", "F11"):
            if self.payload.get("status") != "NOT_EVALUATED":
                raise ValueError("INVALID: learned-policy arms not enabled")

    def public_dict(self) -> dict[str, object]:
        if self.role != "public":
            raise ValueError("INVALID: evaluator-only record")
        # Revalidate at export: callers may mutate a nested dict after construction.
        self.__post_init__()
        return {"schema": self.schema, "role": self.role, "payload": deepcopy(self.payload)}


def h0_predict(name: str, point: tuple[int, int, int]) -> int:
    x, y, z = check_point(point)
    candidates = {"0": 0, "1": 1, "x": x, "!x": 1 - x,
                  "y": y, "!y": 1 - y, "z": z, "!z": 1 - z}
    if name not in H0_ORDER:
        raise ValueError("INVALID: unknown H0 object")
    return candidates[name]


def scan_h0(history: tuple[PublicObservation, ...]) -> tuple[str, ...]:
    validate_public_history(history)
    return tuple(name for name in H0_ORDER
                 if all(h0_predict(name, row.point) == row.answer for row in history))
