"""Stage-2 public-only fixed F00/F10 dispatch and fresh-process entry point.

The OFF arm disables ONLY the persisted learned body; it retains all wired
nonbody routes including the runtime affine decoder. No private answer scoring.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import time

from .decoder import decode_public
from .meter import AstCounts, cost_ledger, measure_ast, peak_rss_bytes
from .records import (
    H0_ORDER, SchemaFrame, check_point, check_sha, digest, h0_predict, scan_h0,
)
from .snapshot import LoadedSnapshot, ROUTES, load_snapshot
from .validator import validate_public

ARMS = ("F00", "F10")


def predict_fixed(snapshot_path: str | Path, *, expected_sha256: str,
                  point: tuple[int, int, int], arm: str
                  ) -> dict[str, object]:
    """Load and revalidate the SAME snapshot bytes for either fixed arm."""
    check_point(point)
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("INVALID: stage 2 only enables F00/F10")
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    snap = load_snapshot(snapshot_path, expected_sha256=expected_sha256)
    if snap.payload["policy"]["route_order"] != list(ROUTES):
        raise ValueError("INVALID: unaudited fallback inventory")

    # All routes remain registered regardless of arm; applicability is separate
    # from existence, selection, execution, and finish.
    exact = next((row.answer for row in snap.history if row.point == point), None)
    h0_choices = scan_h0(snap.history)
    activity: dict[str, dict[str, bool]] = {}
    activity["learned_body"] = {
        "available": True, "enabled": arm == "F10", "applicable": True,
        "selected": False, "executed": False, "finished": False,
    }
    for name, applicable in (
        ("episodic_exact", exact is not None),
        ("h0_consistent", bool(h0_choices)),
        ("runtime_affine_decoder", True),
    ):
        activity[name] = {
            "available": True, "enabled": True, "applicable": applicable,
            "selected": False, "executed": False, "finished": False,
        }

    selected = ("learned_body" if arm == "F10" else
                "episodic_exact" if exact is not None else
                "h0_consistent" if h0_choices else "runtime_affine_decoder")
    if selected not in activity or not activity[selected]["applicable"]:
        raise ValueError("INVALID: illegal or unavailable route")
    entry = activity[selected]
    entry["selected"] = True
    entry["executed"] = True

    counters = AstCounts(0, 0, 0)
    decoder_invocations = 0
    candidates_generated = 0
    validator_invocations = 1  # load_snapshot recomputes public validator
    if selected == "learned_body":
        metered = measure_ast(snap.body, point)
        prediction = metered.prediction
        counters = metered.counts
    elif selected == "episodic_exact":
        prediction = exact
    elif selected == "h0_consistent":
        prediction = h0_predict(h0_choices[0], point)
    else:
        # This legal pre-existing capability must not be disconnected from OFF.
        decoded = decode_public(snap.history)
        decoder_invocations += decoded.decoder_invocations
        candidates_generated += decoded.candidates_generated
        if decoded.body is None or decoded.concept is None:
            raise ValueError("UNIDENTIFIABLE: runtime decoder failed")
        receipt = validate_public(decoded.body, snap.history)
        validator_invocations += 1
        if not receipt.passed:
            raise ValueError("VALIDATION_FAILED: runtime decoder public mismatch")
        metered = measure_ast(decoded.body, point)
        prediction = metered.prediction
        counters = metered.counts

    if type(prediction) is not int or prediction not in (0, 1):
        raise ValueError("INVALID: output must be Bool 0/1")
    entry["finished"] = True
    elapsed_cpu = float(time.process_time() - start_cpu)
    elapsed_wall = float(time.perf_counter() - start_wall)
    costs = cost_ledger(
        paid_inquiries=1, public_observations=len(snap.history),
        decoder_invocations=decoder_invocations,
        candidates_generated=candidates_generated,
        validator_invocations=validator_invocations,
        h0_predicates_scanned=len(H0_ORDER),
        ast_counts=counters, restore_bytes=snap.reference.size_bytes,
        stored_bytes=snap.reference.size_bytes,
        cpu_seconds=elapsed_cpu, wall_seconds=elapsed_wall,
        process_peak_rss=peak_rss_bytes(),
    )
    payload: dict[str, object] = {
        "engineering_only": True,
        "arm": arm, "status": "ENGINEERING_ONLY",
        "snapshot_sha256": snap.reference.sha256,
        "snapshot_path_absolute": snap.reference.path,
        "snapshot_size_bytes": snap.reference.size_bytes,
        "public_digest": snap.payload["public_digest"],
        "policy_digest": snap.payload["policy_digest"],
        "point": list(point),
        "body_enabled": arm == "F10",
        "activity": activity, "route": selected,
        "prediction": prediction, "legal_action": "PREDICT",
        "abstain": False, "cost": costs,
        "closure_status": "UNKNOWN", "m_gap": "UNKNOWN",
        "m_use": "NOT_CERTIFIED",
    }
    frame = SchemaFrame("UseTrace/v2", "public", payload)
    public = frame.public_dict()
    return {"trace": public, "trace_digest": digest(public)}


def write_trace_once(path: str | Path, trace: dict[str, object]) -> dict[str, object]:
    """Local exclusive pre-score commit; not scientific custody/timestamp."""
    file = Path(path).resolve()
    body = (json.dumps(trace, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    try:
        fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except OSError as exc:
        raise ValueError("INVALID: trace exclusive creation failed") from exc
    with os.fdopen(fd, "wb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    return {"absolute_path": str(file), "sha256": sha256(body).hexdigest(),
            "size_bytes": len(body)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic R2-M-ENG fixed dispatch only")
    parser.add_argument("--snapshot", required=True, help="absolute immutable snapshot path")
    parser.add_argument("--sha256", required=True, help="expected independent snapshot SHA256")
    parser.add_argument("--point", required=True, help="3-bit query input, never a label")
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--trace-output", required=True,
                        help="exclusive output for public-only pre-score trace")
    args = parser.parse_args()
    if len(args.point) != 3 or any(bit not in "01" for bit in args.point):
        parser.error("--point must be a three-character binary string")
    trace = predict_fixed(args.snapshot, expected_sha256=args.sha256,
                          point=tuple(int(bit) for bit in args.point),
                          arm=args.arm)
    receipt = write_trace_once(args.trace_output, trace)
    print(json.dumps({"trace_digest": trace["trace_digest"],
                      "trace_file": receipt}, sort_keys=True))


if __name__ == "__main__":
    main()
