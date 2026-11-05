"""R2-M-ENG Stage 3 partial closure inventory, deliberately UNKNOWN.

This is NOT a proof of H0_effective(B), M_gap, causal use, or best OFF.
All public fields are deterministically recomputed from pinned Snapshot/v2
and the version-frozen synthetic comparator manifest.
"""
from __future__ import annotations

from pathlib import Path

from .controls import CATALOG_DIGEST, CONTROL_DIGEST, CONTROL_MANIFEST
from .records import (
    H0_ORDER, METHOD_VERSION, PRIVATE_INPUTS, PUBLIC_POINTS,
    SchemaFrame, digest,
)
from .snapshot import CLOSURE_MANIFEST, FIXED_POLICY, ROUTES, load_snapshot

CLOSURE_AUDIT_VERSION = "r2-m-eng-closure-audit/1"
UNRESOLVED = (
    "No independent source-first audit of every legal history and state transition",
    "No exhaustive proof for all legally wired Kernel/memory/generalization paths",
    "No independently certified best reachable OFF policy under fixed budget B",
    "No independent same-resource H+ loss/nonrealizability witness",
    "No external immutable custody, preregistration, or private USE scoring authority",
)


def audit_closure(snapshot_path: str | Path, *,
                  expected_sha256: str) -> dict[str, object]:
    """Reconstruct a strictly UNKNOWN public HypothesisCertificate/v2."""
    snap = load_snapshot(snapshot_path, expected_sha256=expected_sha256)
    if (snap.payload["closure"] != CLOSURE_MANIFEST or
            snap.payload["policy"] != FIXED_POLICY or
            tuple(snap.payload["policy"]["route_order"]) != ROUTES):
        raise ValueError("INVALID: unaudited fixed dispatch inventory")

    payload = {
        "audit_version": CLOSURE_AUDIT_VERSION,
        "method_version": METHOD_VERSION,
        "closure_manifest_version": CLOSURE_MANIFEST["version"],
        "snapshot_sha256": snap.reference.sha256,
        "snapshot_path_absolute": snap.reference.path,
        "public_digest": snap.payload["public_digest"],
        "public_journal_digest": snap.payload["public_journal_digest"],
        "policy_digest": snap.payload["policy_digest"],
        "closure_digest": snap.payload["closure_digest"],
        "control_manifest_digest": CONTROL_DIGEST,
        "macro_catalog_digest": CATALOG_DIGEST,
        "source_family_public": snap.payload["family_version"],
        "public_points": [list(p) for p in PUBLIC_POINTS],
        "reserved_unseen_inputs_no_labels": [list(p) for p in PRIVATE_INPUTS],
        "known_public_observations": len(snap.history),
        "public_journal_events": [step["event"] for step in snap.journal],
        "resource_bounds": {
            "paid_q": 1, "public_observations": 4,
            "episodic_entries_max": 8, "h0_predicates": len(H0_ORDER),
            "ast_nodes_static_max": 32, "candidate_budget": 16,
        },
        "fixed_dispatch_routes": ["learned_body", *ROUTES],
        "fixed_off_routes": list(ROUTES),
        "fixed_off_disables_only": "learned_body",
        "fixed_route_versions": snap.payload["policy"]["route_versions"],
        "comparator_arms_not_fixed_dispatch_routes": list(CONTROL_MANIFEST["arms"]),
        "pending_learned_policy_arms": {
            "F01": "NOT_EVALUATED", "F11": "NOT_EVALUATED",
        },
        "oracle_ref": "EVALUATOR_ONLY_NOT_EXECUTED",
        "inventory_scope": "isolated_r2_m_eng_stage3_engineering_only",
        "all_legal_history_enumeration": "NOT_PROVEN",
        "effective_h0_reachability": "UNKNOWN",
        "best_off_fallback": "NOT_CERTIFIED",
        "unresolved": list(UNRESOLVED),
        "closure_status": "UNKNOWN", "closure_complete": False,
        "m_gap": "UNKNOWN", "m_use": "NOT_CERTIFIED",
        "n_rep": "NOT_EVALUATED", "u": "NOT_EVALUATED",
        "t": "NOT_EVALUATED",
        "science_scoring": "NOT_AUTHORIZED",
        "engineering_only": True,
    }
    public = SchemaFrame("HypothesisCertificate/v2", "public", payload).public_dict()
    return {"certificate": public, "certificate_digest": digest(public)}


def validate_closure_audit(snapshot_path: str | Path, *, expected_sha256: str,
                           record: dict[str, object]) -> None:
    """Fail closed on edits, including rehashed COMPLETE or removed unknowns."""
    expected = audit_closure(snapshot_path, expected_sha256=expected_sha256)
    if type(record) is not dict or record != expected:
        raise ValueError("INVALID: closure audit differs from fixed UNKNOWN inventory")
