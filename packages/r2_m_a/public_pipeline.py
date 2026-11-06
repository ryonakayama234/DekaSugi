"""Evaluator-side SYNTHETIC ONLY Q001-to-Snapshot adapter for G3-1.

No production entry point exists here. The local precommit barrier is an
engineering fixture, NOT a verified GitHub remote commit. G3-3 must implement
and independently verify remote custody before any future scientific query.
This module must NEVER be reachable from a child import graph.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.records import (
    PUBLIC_POINTS, PublicObservation, check_sha, public_evidence_digest,
    validate_public_history,
)
from packages.r2_m_eng.sleep_lite import sleep_lite
from packages.r2_m_eng.snapshot import SnapshotRef, load_snapshot, write_snapshot
from packages.r2_m_eng.source_gateway import PublicGateway
from packages.r2_m_eng.validator import validate_public


@dataclass(frozen=True, slots=True)
class SyntheticPrecommitIntent:
    """Only information knowable BEFORE receiving the Q001 answer."""
    commitment: str
    history_digest: str
    legal_digest: str
    point: tuple[int, int, int]
    paid_budget_remaining: int
    expires_at: int
    committed_at: int

    def __post_init__(self) -> None:
        check_sha(self.commitment)
        check_sha(self.history_digest)
        check_sha(self.legal_digest)
        if self.point != PUBLIC_POINTS[3] or self.paid_budget_remaining != 1:
            raise ValueError("INVALID: illegal synthetic Q001 intent")


@dataclass(frozen=True, slots=True)
class SyntheticPrecommitReceipt:
    """Local test receipt. NEVER evidence of remote GitHub custody."""
    commitment: str
    engineering_only: bool = True


def prepare_synthetic_snapshot(
    gateway: PublicGateway, *, snapshot_path: str | Path, precommit_at: int,
    answer_at: int, barrier: Callable[[SyntheticPrecommitIntent], SyntheticPrecommitReceipt],
    engineering_only: bool,
) -> SnapshotRef:
    """Synthetic 3+Q001 -> decoder -> independent validator -> immutable Snapshot.

    Barrier failure stops BEFORE the paid query. This procedure never evaluates
    USE outputs, schedules 448 child processes, or invokes a scientific scorer.
    """
    if engineering_only is not True or type(gateway) is not PublicGateway:
        raise ValueError("RUN_BLOCK: only an artificial gateway is permitted in G3-1")
    if not callable(barrier):
        raise ValueError("RUN_BLOCK: pre-answer barrier is required")
    # Called before gateway.precommit to avoid consuming an expired paid query.
    state = gateway.public_state(now=precommit_at)
    history = state["observations"]
    validate_public_history(history)
    if (len(history) != 3 or state["paid_budget_remaining"] != 1 or
            state["legal_actions"] != (PUBLIC_POINTS[3],) or
            type(answer_at) is not int or answer_at < precommit_at or
            answer_at > state["expires_at"]):
        raise ValueError("RUN_BLOCK: incomplete, expired or noncanonical public inquiry")
    # The local gateway checks the legal digest and writes its own fsynced
    # precommit event BEFORE we permit the fixture's artificial answer.
    commitment = gateway.precommit(PUBLIC_POINTS[3],
                                   expected_legal_digest=state["legal_digest"],
                                   prediction=None, now=precommit_at)
    intent = SyntheticPrecommitIntent(
        commitment, public_evidence_digest(history), state["legal_digest"],
        PUBLIC_POINTS[3], 1, state["expires_at"], precommit_at)
    receipt = barrier(intent)
    if (type(receipt) is not SyntheticPrecommitReceipt or
            receipt.engineering_only is not True or
            receipt.commitment != commitment):
        raise ValueError("RUN_BLOCK: synthetic precommit barrier not confirmed")
    observed = gateway.answer(PUBLIC_POINTS[3], precommit=commitment, now=answer_at)
    if type(observed) is not PublicObservation or observed.precommit != commitment:
        raise ValueError("INVALID: mismatched paid observation")
    completed = gateway.public_state(now=answer_at)["observations"]
    validate_public_history(completed, complete=True)
    decoded = decode_public(completed)
    if (decoded.body is None or decoded.decoder_invocations != 1 or
            decoded.candidates_generated != 1):
        raise ValueError("UNIDENTIFIABLE: Q001 failed to identify public body")
    receipt_public = validate_public(decoded.body, completed)
    if not receipt_public.passed or receipt_public.checked_public != 4:
        raise ValueError("VALIDATION_FAILED: independent public interpreter")
    canonical_body, sleep_receipt = sleep_lite(decoded.body, completed)
    if not sleep_receipt.meaning_preserved_all_8:
        raise ValueError("VALIDATION_FAILED: Sleep-lite changed semantics")
    reference = write_snapshot(snapshot_path, completed, gateway.public_journal(),
                               canonical_body, expires_at=state["expires_at"])
    # Independent expected bytes hash required for every read; no private truth.
    loaded = load_snapshot(reference.path, expected_sha256=reference.sha256)
    if loaded.history != completed:
        raise ValueError("INVALID: immutable Snapshot readback mismatch")
    return reference
