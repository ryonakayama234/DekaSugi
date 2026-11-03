"""Exact semantic membership in the old 61-model H0, NOT full H+ closure."""
from __future__ import annotations
from time import monotonic
from . import ACTIONS, HISTORIES, N, Edge, Law, _transition, law, signature


def certify_old_h0(model: Law, *, deadline_seconds: float = 120) -> dict:
    if type(model) is not Law:
        raise ValueError("Law required")
    if type(deadline_seconds) not in (int, float) or not 0 < deadline_seconds <= 3600:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP"}
    end = monotonic() + deadline_seconds
    try:
        ref = signature(model, deadline_at=end)
        # G2b old fixed hypothesis envelope: NULL + three lags x 20 ordered roles.
        candidates = [("NULL", law())] + [
            (f"lag{lag}:{s}->{t}", law(Edge(s, t, lag)))
            for lag in (0, 1, 2) for s in range(N) for t in range(N) if s != t
        ]
        rejected = 0
        for label, candidate in candidates:
            j = 0
            mismatch = False
            for x in range(1 << N):
                for h in HISTORIES:
                    if monotonic() >= end:
                        raise TimeoutError("H0 budget exceeded")
                    for action in ACTIONS:
                        if _transition(candidate, x, h, action)[0] != ref[j]:
                            mismatch = True
                            break
                        j += 1
                    if mismatch:
                        break
                if mismatch:
                    break
            if not mismatch:
                if monotonic() >= end:
                    raise TimeoutError("H0 budget exceeded")
                return {"status": "IN_H0", "matching_model": label,
                        "h0_total_candidates": 61, "matching_cells": len(ref),
                        "rejected_models": rejected}
            rejected += 1
        if monotonic() >= end:
            raise TimeoutError("H0 budget exceeded")
        return {"status": "OUTSIDE_H0", "h0_total_candidates": 61,
                "mismatch_witnesses": rejected,
                "scope": "only_61_fixed_single_edge_models_over_full_declared_domain"}
    except TimeoutError:
        return {"status": "NOT_CERTIFIED", "reason": "PROOF_RESOURCE_CAP"}
