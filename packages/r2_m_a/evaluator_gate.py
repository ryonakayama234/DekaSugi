"""G3-3 evaluator-side pre-score gate: DENY by default, no scorer imported.

This module has no public scorer and no current owner-approved G6 activation.
An "approved=True" claim supplied by a caller is never sufficient: G4/G5/G6
future approval must be implemented separately and audited at an exact head.
"""
from __future__ import annotations

from .contracts import EXPECTED_SLOTS, SCIENTIFIC_EXECUTION_AUTHORIZED
from .remote_custody import CustodyBlocked

G4_ACTUAL_PATH_APPROVED = False
G5_ORDER_APPROVED = False
G6_EXECUTION_AND_SCORE_APPROVED = False


def inspect_prescore_readiness(ledger, *, remote) -> dict:
    """Read-only custody verification; does NOT grant scoring authority."""
    locked = ledger.assert_prescore_remote(remote)
    if (locked.get("expected_slot_count") != EXPECTED_SLOTS
            or locked.get("eligible_for_future_score") is not True
            or locked.get("counts") != {"TRACE_PRESENT": EXPECTED_SLOTS}
            or locked.get("q_remote_verified_laws") != 16
            or locked.get("snapshot_locked_laws") != 16):
        raise CustodyBlocked("RUN_BLOCK: incomplete, invalid or missing slots/Q evidence")
    return {"custody": "PRESCORE_REMOTE_VERIFIED", "science": "NOT_AUTHORIZED",
            "score": "NOT_COMPUTED", "expected_slots": EXPECTED_SLOTS}


def require_score_gate(ledger, *, remote, owner_approval=None) -> None:
    """There is deliberately no callable scoring function in G3-3."""
    if (not SCIENTIFIC_EXECUTION_AUTHORIZED or not G4_ACTUAL_PATH_APPROVED
            or not G5_ORDER_APPROVED or not G6_EXECUTION_AND_SCORE_APPROVED):
        raise CustodyBlocked("RUN_BLOCK: G4/G5/G6/scientific scoring not authorized")
    # Future G6 requires separately reviewed authorization verification, not
    # caller-provided booleans or a self-asserted owner token.
    raise CustodyBlocked("RUN_BLOCK: approved G6 scorer not implemented")
