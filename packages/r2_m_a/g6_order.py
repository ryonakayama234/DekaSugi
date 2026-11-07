"""G6-1: independently validate immutable G5, expand to canonical 448 Slots.

Strictly parent-side; no execution, scoring or authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable

from packages.r2_m_a.contracts import (ARMS, EXPECTED_SLOTS, LAW_IDS, Slot,
                                       USE_POINTS, validate_g5_order_manifest)
from packages.r2_m_eng.records import digest

G5_COMMIT = "bb2e27a20657fefa5426d970c3275b8d95a846dc"
G5_BRANCH = "refs/heads/audit/r2ma/g5-order-20261107"
G5_PATH = "audit/r2ma/g5-order-manifest.json"
G5_BYTES = 473
G5_SHA256 = "b4aa94023961d4858919351f0097f197f5397b5f3d6f50c90271535e4c3e65c7"
G5_TARGET = "4e8a0c2d68ba431a8446720b314fd205babe2ac3"
G5_PREREG = "R2-M-A-20261105-EXHAUSTIVE16-ENGINEERING-PREREG"
FIELDS = {"generated_by", "law_order", "method", "prereg_id",
          "schema", "seed", "target_head", "within_law_order"}


class G6Blocked(RuntimeError):
    """A failed or uncertain guarantee always fails closed."""


def sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")


@dataclass(frozen=True)
class SealedG5:
    ordered: tuple[Slot, ...]
    expanded_sha256: str
    raw_sha256: str = G5_SHA256
    pinned_commit: str = G5_COMMIT


def validate_g5(raw: bytes, *, pinned_commit: str, remote_ref: str,
                pinned_readback: bool) -> SealedG5:
    """Validate raw immutable bytes before expanding or checking G3 Slot digest."""
    if (type(raw) is not bytes or len(raw) != G5_BYTES
            or sha(raw) != G5_SHA256 or pinned_commit != G5_COMMIT
            or remote_ref != G5_BRANCH or pinned_readback is not True):
        raise G6Blocked("RUN_BLOCK: G5 sealed bytes/pin/readback mismatch")
    try:
        obj = json.loads(raw.decode("utf-8"),
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        if type(obj) is not dict or set(obj) != FIELDS:
            raise ValueError("G5 schema")
        canon = json.dumps(obj, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("utf-8")
        if canon != raw:
            raise ValueError("G5 byte canonicality")
        if (obj["schema"] != "r2ma-g5-order/1"
                or obj["target_head"] != G5_TARGET
                or obj["prereg_id"] != G5_PREREG
                or obj["generated_by"] != "supervisor (mechanical computation from the frozen method)"
                or obj["within_law_order"] != "manifest-enumeration"
                or obj["method"] != "hash-sort/1"
                or type(obj["seed"]) is not str or not obj["seed"]
                or type(obj["law_order"]) is not list
                or len(obj["law_order"]) != 16
                or any(type(x) is not str for x in obj["law_order"])
                or set(obj["law_order"]) != LAW_IDS
                or len(set(obj["law_order"])) != 16):
            raise ValueError("G5 laws/method")
        actual = sorted(LAW_IDS, key=lambda x: sha256(
            obj["seed"].encode("utf-8") + b"\x00" + x.encode("ascii")).digest())
        if actual != obj["law_order"]:
            raise ValueError("G5 hash-sort/1")
        slots = tuple(Slot(law, point, arm)
                      for law in actual
                      for point in sorted(USE_POINTS)
                      for arm in sorted(ARMS))
        expanded = digest([s.as_dict() for s in slots])
        validate_g5_order_manifest(slots, expected_digest=expanded)
        if len(slots) != EXPECTED_SLOTS:
            raise ValueError("G5 expansion")
        return SealedG5(slots, expanded)
    except (ValueError, TypeError, KeyError, UnicodeError) as e:
        raise G6Blocked("RUN_BLOCK: invalid sealed G5 manifest") from e


def load_pinned_g5(reader: Callable[[str, str, str], bytes]) -> SealedG5:
    """Reader must verify GitHub ref, fetch exact pinned commit and read its bytes."""
    if not callable(reader):
        raise G6Blocked("RUN_BLOCK: pinned remote G5 reader missing")
    return validate_g5(reader(G5_BRANCH, G5_COMMIT, G5_PATH),
                       pinned_commit=G5_COMMIT,
                       remote_ref=G5_BRANCH, pinned_readback=True)
