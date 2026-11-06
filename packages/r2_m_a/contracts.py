"""G3-1 immutable preregistration, slot and child-input contracts.

This module is public-data-only. It does not import comparator controls (whose
import builds a 16-entry macro catalog), evaluator sources, or scoring modules.
G5 determines order later: enumerating a set is NOT an execution order.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path

from packages.r2_m_eng.records import PRIVATE_INPUTS, PUBLIC_POINTS, check_point, check_sha, digest

G2_MAIN_SHA = "cf844094fb5907a37bb496760e206f9061deb021"
G2_PREREG_SHA256 = "865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68"
WALL_SECONDS_CAP = 5
PROCESS_CPU_SECONDS_CAP = 5
RSS_BYTES_CAP = 512_000_000  # SI MB, not MiB; see Owner PR #183 decision.
RSS_BOUNDARY_UPPER_BYTES = 536_870_912
PUBLIC_INITIAL_POINTS = PUBLIC_POINTS[:3]
PAID_Q001 = PUBLIC_POINTS[3]
USE_POINTS = PRIVATE_INPUTS  # Input coordinates only. No private labels.
# Independent arms; F00's fallback inventory MUST NOT gain any of the controls.
ARMS = ("F00", "F10", "STATIC-H+", "FIXED-MACRO",
        "EPISODIC-EXACT", "NEAREST-1NN", "STUMP-1")
LAW_IDS = frozenset("".join(map(str, bits)) for bits in product((0, 1), repeat=4))
EXPECTED_SLOTS = 16 * 4 * 7
SCIENTIFIC_EXECUTION_AUTHORIZED = False


def _sha40(value: object) -> str:
    if (type(value) is not str or len(value) != 40 or
            any(c not in "0123456789abcdef" for c in value)):
        raise ValueError("RUN_BLOCK: 40-character lowercase commit SHA required")
    return value


def verify_g2_anchor(*, main_sha: str, document_sha256: str,
                     document_bytes: bytes | None = None) -> None:
    """Reject drift without rewriting the frozen preregistration."""
    if (_sha40(main_sha) != G2_MAIN_SHA or
            check_sha(document_sha256) != G2_PREREG_SHA256):
        raise ValueError("RUN_BLOCK: frozen G2 anchor mismatch")
    if document_bytes is not None:
        if type(document_bytes) is not bytes or sha256(document_bytes).hexdigest() != G2_PREREG_SHA256:
            raise ValueError("RUN_BLOCK: frozen preregistration bytes mismatch")


def rss_boundary_status(value: int) -> str:
    """Reporting contract only: G3-2 must still guard at the SI threshold.

    A borderline result must be reported with its raw bytes, not silently
    reduced to one interpretation of MB. G4 + Owner determine disposition.
    """
    if type(value) is not int or value < 0:
        raise ValueError("UNMEASURED: process RSS must be nonnegative integer bytes")
    if RSS_BYTES_CAP <= value <= RSS_BOUNDARY_UPPER_BYTES:
        return "BOUNDARY_REVIEW"  # includes equality, regardless of guard event
    return "WITHIN_SI_CAP" if value < RSS_BYTES_CAP else "RESOURCE_STOP"


@dataclass(frozen=True, slots=True)
class Slot:
    """Parent-only administrative identity: NEVER serialized into child args/env."""
    law_id: str
    point: tuple[int, int, int]
    arm: str

    def __post_init__(self) -> None:
        if type(self.law_id) is not str or self.law_id not in LAW_IDS:
            raise ValueError("INVALID: unknown frozen law identifier")
        if check_point(self.point) not in USE_POINTS:
            raise ValueError("INVALID: only four USE inputs are planned")
        if type(self.arm) is not str or self.arm not in ARMS:
            raise ValueError("INVALID: unknown independent arm")

    def as_dict(self) -> dict[str, object]:
        return {"law_id": self.law_id, "point": list(self.point), "arm": self.arm}


def expected_slot_set() -> frozenset[Slot]:
    """Unordered G2 design set, not G5 run order or a generated random seed."""
    result = frozenset(Slot(law, point, arm)
                       for law in LAW_IDS for point in USE_POINTS for arm in ARMS)
    if len(result) != EXPECTED_SLOTS:
        raise ValueError("INVALID: incomplete 448-slot design")
    return result


def validate_g5_order_manifest(ordered: object, *, expected_digest: str) -> tuple[Slot, ...]:
    """G5 insertion point; cannot create, shuffle, seed or authorize an order.

    Digest is of the supplied canonical list; independent G5 remote/source
    authorization is a later gate, NOT established by this local check.
    """
    check_sha(expected_digest)
    if (type(ordered) is not tuple or len(ordered) != EXPECTED_SLOTS
            or any(type(item) is not Slot for item in ordered)):
        raise ValueError("RUN_BLOCK: G5 order manifest missing/incomplete")
    if frozenset(ordered) != expected_slot_set():
        raise ValueError("RUN_BLOCK: G5 order has missing or duplicate slots")
    if digest([item.as_dict() for item in ordered]) != expected_digest:
        raise ValueError("RUN_BLOCK: G5 order digest mismatch")
    return ordered


def _canonical_absolute_path(value: object) -> str:
    if type(value) is not str or not value or "\x00" in value:
        raise ValueError("INVALID: canonical absolute path required")
    path = Path(value)
    if not path.is_absolute() or str(path) != value or str(path.resolve()) != value:
        raise ValueError("INVALID: noncanonical absolute path")
    return value


@dataclass(frozen=True, slots=True)
class ChildRequest:
    """Exactly five public fields for future G3-2 child handoff (no truth/seed)."""
    snapshot_path: str
    expected_sha256: str
    arm: str
    point: tuple[int, int, int]
    trace_path: str

    def __post_init__(self) -> None:
        _canonical_absolute_path(self.snapshot_path)
        _canonical_absolute_path(self.trace_path)
        if self.snapshot_path == self.trace_path:
            raise ValueError("INVALID: snapshot and trace paths cannot coincide")
        check_sha(self.expected_sha256)
        if type(self.arm) is not str or self.arm not in ARMS:
            raise ValueError("INVALID: unauthorized child arm")
        if check_point(self.point) not in USE_POINTS:
            raise ValueError("INVALID: child input must be USE coordinate only")

    def as_dict(self) -> dict[str, object]:
        return {"snapshot_path": self.snapshot_path,
                "expected_sha256": self.expected_sha256,
                "arm": self.arm, "point": list(self.point),
                "trace_path": self.trace_path}


def verify_child_payload(payload: object) -> ChildRequest:
    """Exact allowlist; law ID, ground truth, score, seed cannot be accepted."""
    if type(payload) is not dict or set(payload) != {
        "snapshot_path", "expected_sha256", "arm", "point", "trace_path"
    }:
        raise ValueError("INVALID: child payload fields are not allowlisted")
    if type(payload["point"]) is not list or len(payload["point"]) != 3:
        raise ValueError("INVALID: child input point shape")
    return ChildRequest(payload["snapshot_path"], payload["expected_sha256"],
                        payload["arm"], tuple(payload["point"]), payload["trace_path"])
