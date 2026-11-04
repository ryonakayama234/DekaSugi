"""Orchestrate ONLY the authorized N/S/R/E fixture engineering diagnostic."""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

from .core import (DOMAIN, H0_ORDER, digest, dispatch, h0_predict, load_snapshot,
                   make_snapshot, save_snapshot, scan_h0, synthesize_public)
from .fixture import LEGAL, PublicGateway, PrivateSource, finite_certificate
from .validator import validate_public

ROOT = Path(__file__).resolve().parents[2]
FIXED_QUERY = {"N": (0, 0), "S": (0, 0), "R": (1, 1)}


def fresh_dispatch(snapshot_path: Path, point: tuple[int, int], mode: str) -> dict:
    if mode not in ("on", "off") or point not in DOMAIN:
        raise ValueError("unapproved fresh-use request")
    result = subprocess.run(
        [sys.executable, "-m", "packages.r1_eng", "--snapshot", str(snapshot_path),
         "--mode", mode, "--x", str(point[0]), "--z", str(point[1])],
        cwd=ROOT, capture_output=True, text=True, check=True, timeout=15)
    return json.loads(result.stdout)


def run_fixture(case: str, variant: str, output_dir: Path) -> dict[str, object]:
    """Engineering-only runner. Fixture selection belongs to the operator, not learner."""
    source = PrivateSource(case, variant)
    gateway = PublicGateway(source)
    initial, _, _ = gateway.public()
    before = scan_h0(initial, 5 if case == "E" else 6) if initial else None
    if case in FIXED_QUERY:
        point = FIXED_QUERY[case]  # fixed; not a learned Active Learning policy
        # Before the answer is obtained, commit a prediction or explicit ABSTAIN.
        eligible = tuple(h for h in H0_ORDER
                         if all(h0_predict(h, o.point) == o.answer for o in initial))
        prediction = h0_predict(eligible[0], point) if eligible else None
        precommit = gateway.precommit(point, prediction)
        gateway.ask(point, precommit)
    public, remaining, budget = gateway.public()
    h0 = scan_h0(public, 5 if case == "E" else 6)
    source_side_proof = finite_certificate(case)
    body = None
    synthesis_status = "NOT_APPLICABLE"
    considered = 0
    validation = None
    if case == "R":
        if before is None or before.status != "MISMATCH_CANDIDATE":
            raise AssertionError("R missing complete public H0 mismatch")
        if remaining or budget:
            raise AssertionError("R query did not complete before synthesis")
        synth = synthesize_public(public)
        synthesis_status, considered, body = synth.status, synth.considered, synth.candidate
        if body is None:
            raise AssertionError("public-only typed synthesis did not find an R body")
        validation = validate_public(body, public)
        if not validation["passed"]:
            raise AssertionError("independent public validator mismatch")
    if case == "E" and h0.status != "SEARCH_INCOMPLETE":
        raise AssertionError("E incorrectly certified representation mismatch")
    if h0.status != source_side_proof["status"] and case != "N":
        raise AssertionError("finite diagnostic does not match paper fixture")
    snap = make_snapshot(public, body)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / ("snapshot-" + digest(snap.payload())[:20] + ".json")
    save_snapshot(path, snap)  # refuses overwrite, even with identical bytes
    restored = load_snapshot(path)
    if restored != snap:
        raise AssertionError("immutable snapshot roundtrip failed")
    use = []
    if body is not None:
        for point in DOMAIN:  # all four already public: NOT unknown inputs
            on = fresh_dispatch(path, point, "on")
            off = fresh_dispatch(path, point, "off")
            use.append({"input": list(point), "on": on, "off": off,
                        "prediction_or_action_delta":
                            (on["prediction"], on["action"]) !=
                            (off["prediction"], off["action"])})
    delta = any(row["prediction_or_action_delta"] for row in use)
    return {
        "kind": "R1-ENG-2BIT-ENGINEERING-DIAGNOSTIC",
        "scientific_scoring": False,
        "case": case, "variant": variant,  # operator report only; NOT in Snapshot
        "paper_certificate": source_side_proof,
        "public_records": [o.as_dict() for o in public],
        "h0_object": {"tested": list(h0.tested), "consistent": list(h0.consistent),
                      "complete": h0.complete, "status": h0.status},
        "synthesis": {"status": synthesis_status, "considered": considered,
                      "body_from_public_only": body is not None},
        "validator": validation,
        "sleep_lite": {"canonicalized": body is not None,
                       "validator_recorded": validation is not None},
        "snapshot_sha256": snap.as_dict()["sha256"],
        "snapshot_path": str(path),
        "fresh_use": use,
        "body_off_retains": ["episodic_lookup", "H0_object"],
        "external_arms_not_in_off": ["STATIC-H+", "fixed_macro"],
        "M_use_engineering": ("prediction_or_action_delta_observed" if delta else
                              "not_certified_no_prediction_or_action_delta"),
        "M_gap": "NOT_EVALUATED", "N_rep": "NOT_EVALUATED",
        "U": "NOT_EVALUATED", "T": "NOT_EVALUATED",
        "limitation": "all four R points public; fresh use checks persistence/dispatch only",
    }
