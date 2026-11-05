"""R2-M-ENG Stage 3 fixed, public-only engineering comparator arms.

Every arm is human-specified before any synthetic fixture is examined.
Comparators are NOT extra fallback routes on the already-frozen F00/F10
dispatch; adding one to that dispatch requires a new reviewed policy version.
No source_gateway, private labels, learned policy, or scientific scoring.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
import os
from pathlib import Path
import time

from .decoder import compile_affine, decode_public
from .dispatch import write_trace_once
from .meter import AstCounts, cost_ledger, measure_ast, peak_rss_bytes
from .records import (
    FAMILY_VERSION, H0_ORDER, Node, SchemaFrame, ast_dict, canonical,
    check_point, digest, validate_public_history,
)
from .snapshot import load_snapshot
from .validator import validate_public

CONTROLS_VERSION = "R2-M-CONTROLS-v2.0"
CONTROL_ARMS = (
    "STATIC-H+", "FIXED-MACRO", "EPISODIC-EXACT", "NEAREST-1NN", "STUMP-1",
)
STUMP_PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))
STUMP_ORDER = (
    ("constant0", None, (0, 0)),
    ("constant1", None, (1, 1)),
    *((f"{name}:{a}{b}", axis, (a, b))
      for axis, name in enumerate(("x", "y", "z"))
      for a, b in STUMP_PAIRS),
)
CONTROL_MANIFEST = {
    "version": CONTROLS_VERSION,
    "method_family": FAMILY_VERSION,
    "arms": list(CONTROL_ARMS),
    "STATIC-H+": {
        "candidate_budget": 16, "family_size": 16, "ast_nodes_max": 32,
        "decoder": "public_affine_one_shot/1", "nonpersistent": True,
        "use_time_redecode": True,
    },
    "FIXED-MACRO": {
        "predeclared_laws": 16, "catalog_order": "lexicographic_a_b_c_d",
        "selection": "public_coefficient_index_only",
        "no_per_law_injection": True,
    },
    "EPISODIC-EXACT": {
        "capacity": 8, "entries_from_public": 4, "miss": "ABSTAIN",
    },
    "NEAREST-1NN": {
        "capacity": 8, "metric": "hamming", "tie": "all_nearest_majority_else_ABSTAIN",
    },
    "STUMP-1": {
        "capacity": 14, "candidate_order": [row[0] for row in STUMP_ORDER],
        "fit": "least_public_zero_one_errors_first_tie",
    },
    "learned_policy": {"F01": "NOT_EVALUATED", "F11": "NOT_EVALUATED"},
    "oracle": "evaluator_only_not_callable",
}
CONTROL_DIGEST = digest(CONTROL_MANIFEST)

# Built without any observation, source, or target-specific coefficient.
# Module-import build is preparation work, NOT free USE-time computation.
_catalog_cpu_start, _catalog_wall_start = time.process_time(), time.perf_counter()
MACRO_CATALOG: tuple[tuple[tuple[int, int, int, int], Node], ...] = tuple(
    (bits, compile_affine(bits)) for bits in product((0, 1), repeat=4)
)
CATALOG_PREPARATION_CPU_SECONDS = time.process_time() - _catalog_cpu_start
CATALOG_PREPARATION_WALL_SECONDS = time.perf_counter() - _catalog_wall_start
CATALOG_DIGEST = digest([
    {"coefficients": list(coefficients), "body": ast_dict(body)}
    for coefficients, body in MACRO_CATALOG
])
CATALOG_SERIALIZED_BYTES = len(canonical([
    {"coefficients": list(coefficients), "body": ast_dict(body)}
    for coefficients, body in MACRO_CATALOG
]).encode("utf-8"))


def _public_coefficients(history: tuple) -> tuple[int, int, int, int]:
    validate_public_history(history, complete=True)
    d, rx, ry, rz = (row.answer for row in history)
    return (rx ^ d, ry ^ d, rz ^ d, d)


def _nearest(history: tuple, point: tuple[int, int, int]) -> tuple[int | None, int]:
    distances = [sum(a != b for a, b in zip(row.point, point)) for row in history]
    minimum = min(distances)
    votes = [row.answer for row, distance in zip(history, distances) if distance == minimum]
    ones = sum(votes)
    return (None if ones * 2 == len(votes) else int(ones * 2 > len(votes))), len(distances)


def _fit_stump(history: tuple, point: tuple[int, int, int]) -> tuple[int, str, int]:
    # Deterministic 14-slot candidate list: constants, x00/01/10/11, y..., z...
    scored = []
    for label, axis, pair in STUMP_ORDER:
        error = sum((pair[0] if axis is None else pair[row.point[axis]])
                    != row.answer for row in history)
        scored.append(error)
    chosen = min(range(len(scored)), key=lambda i: (scored[i], i))
    label, axis, pair = STUMP_ORDER[chosen]
    prediction = pair[0] if axis is None else pair[point[axis]]
    return prediction, label, len(scored)


def predict_control(snapshot_path: str | Path, *, expected_sha256: str,
                    point: tuple[int, int, int], arm: str) -> dict[str, object]:
    """One independent comparator use. Never consumes a USE outcome."""
    check_point(point)
    if type(arm) is not str or arm not in CONTROL_ARMS:
        raise ValueError("INVALID: unapproved comparator or learned-policy arm")
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    snap = load_snapshot(snapshot_path, expected_sha256=expected_sha256)
    history = snap.history
    if len(history) != 4:
        raise ValueError("UNIDENTIFIABLE: public Q001 not complete")

    prediction: int | None
    counts = AstCounts(0, 0, 0)
    decoder_calls = validator_calls = generated = 0
    h0_scans = 0
    public_comparisons = 0
    choice = arm
    if arm == "STATIC-H+":
        # Same public decoder/typed tree as learner, reconstructed at USE time.
        result = decode_public(history)
        decoder_calls += result.decoder_invocations
        generated += result.candidates_generated
        if result.body is None:
            raise ValueError("UNIDENTIFIABLE: static decoder absent")
        receipt = validate_public(result.body, history)
        validator_calls += 1
        if not receipt.passed:
            raise ValueError("VALIDATION_FAILED: static public validation")
        measured = measure_ast(result.body, point)
        prediction, counts = measured.prediction, measured.counts
        h0_scans += 16  # decode_public uses two 8-predicate public scans
    elif arm == "FIXED-MACRO":
        # The full 16-entry library exists before the public history is read.
        coefficients = _public_coefficients(history)
        index = next(i for i, (bits, _) in enumerate(MACRO_CATALOG)
                     if bits == coefficients)
        body = MACRO_CATALOG[index][1]
        receipt = validate_public(body, history)
        validator_calls += 1
        if not receipt.passed:
            raise ValueError("VALIDATION_FAILED: fixed catalog inconsistent")
        measured = measure_ast(body, point)
        prediction, counts = measured.prediction, measured.counts
        choice = f"catalog_index_{index:02d}"
        public_comparisons = 4
    elif arm == "EPISODIC-EXACT":
        if len(history) > 8:
            raise ValueError("INVALID: episodic capacity exceeded")
        prediction = next((row.answer for row in history if row.point == point), None)
        public_comparisons = len(history)
    elif arm == "NEAREST-1NN":
        if len(history) > 8:
            raise ValueError("INVALID: 1NN capacity exceeded")
        prediction, public_comparisons = _nearest(history, point)
    else:
        prediction, choice, generated = _fit_stump(history, point)
        public_comparisons = len(history) * len(STUMP_ORDER)

    status = "ABSTAIN" if prediction is None else "PREDICT"
    cost = cost_ledger(
        paid_inquiries=1, public_observations=4,
        decoder_invocations=1 + decoder_calls,
        candidates_generated=1 + generated,
        validator_invocations=3 + validator_calls,
        h0_predicates_scanned=16 + h0_scans,
        ast_counts=counts, restore_bytes=snap.reference.size_bytes,
        stored_bytes=0, cpu_seconds=float(time.process_time() - start_cpu),
        wall_seconds=float(time.perf_counter() - start_wall),
        process_peak_rss=peak_rss_bytes(),
    )
    cost["breakdown"] = {
        "restore": {
            "decoder_invocations": 1, "candidates_generated": 1,
            "validator_invocations": 3, "h0_predicates_scanned": 16,
            "bytes_read": snap.reference.size_bytes,
        },
        "comparator_use": {
            "decoder_invocations": decoder_calls,
            "candidates_generated": generated, "validator_invocations": validator_calls,
            "h0_predicates_scanned": h0_scans,
            "public_comparisons": public_comparisons,
        },
        "fixed_catalog_preparation": {
            "scope": "module_import_in_each_fresh_process; not USE-time",
            "catalog_entries": len(MACRO_CATALOG),
            "serialized_catalog_bytes_not_disk_storage": CATALOG_SERIALIZED_BYTES,
            "process_cpu_seconds": CATALOG_PREPARATION_CPU_SECONDS,
            "monotonic_wall_seconds": CATALOG_PREPARATION_WALL_SECONDS,
            "included_in_USE_cpu_seconds": False,
        },
        "stump_fit_candidates": generated if arm == "STUMP-1" else 0,
    }
    cost["comparator_capacity"] = CONTROL_MANIFEST[arm].get(
        "capacity", CONTROL_MANIFEST[arm].get("predeclared_laws", 16)
    )
    cost["comparator_manifest_digest"] = CONTROL_DIGEST
    payload = {
        "engineering_only": True, "process_id": os.getpid(),
        "arm": arm, "status": "ENGINEERING_ONLY",
        "snapshot_path_absolute": snap.reference.path,
        "snapshot_sha256": snap.reference.sha256,
        "public_digest": snap.payload["public_digest"],
        "policy_digest": snap.payload["policy_digest"],
        "control_manifest_digest": CONTROL_DIGEST,
        "macro_catalog_digest": CATALOG_DIGEST,
        "point": list(point), "route": choice,
        "activity": {arm: {
            "available": True, "enabled": True, "applicable": True,
            "selected": True, "executed": True, "finished": True,
        }},
        "prediction": prediction, "legal_action": status,
        "abstain": prediction is None, "cost": cost,
        "closure_status": "UNKNOWN", "m_gap": "UNKNOWN",
        "m_use": "NOT_CERTIFIED", "n_rep": "NOT_EVALUATED",
        "u": "NOT_EVALUATED", "t": "NOT_EVALUATED",
    }
    public = SchemaFrame("UseTrace/v2", "public", payload).public_dict()
    return {"trace": public, "trace_digest": digest(public)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Artificial-only R2-M-ENG comparator")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--point", required=True)
    parser.add_argument("--arm", choices=CONTROL_ARMS, required=True)
    parser.add_argument("--trace-output", required=True)
    args = parser.parse_args()
    if len(args.point) != 3 or any(bit not in "01" for bit in args.point):
        parser.error("--point must be three binary digits")
    trace = predict_control(args.snapshot, expected_sha256=args.sha256,
                            point=tuple(int(v) for v in args.point), arm=args.arm)
    receipt = write_trace_once(args.trace_output, trace)
    print(json.dumps({"trace_digest": trace["trace_digest"],
                      "trace_file": receipt}, sort_keys=True))


if __name__ == "__main__":
    main()
