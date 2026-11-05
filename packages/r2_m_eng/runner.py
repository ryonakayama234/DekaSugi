"""R2-M-ENG Stage 3 artificial-fixture orchestration; NOT a scientific runner.

Evaluator-side bootstrap alone imports source_gateway. Fresh learner children
only receive canonical absolute Snapshot path, externally pinned SHA, public
query input, arm, and exclusive public trace path. There is NO private USE
scoring, sealed corpus use, policy learning, or source-first certification.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from .closure import audit_closure, validate_closure_audit
from .controls import CONTROL_ARMS, CONTROL_DIGEST
from .decoder import decode_public
from .dispatch import write_trace_once
from .records import PUBLIC_POINTS, check_bit, check_point, digest
from .snapshot import write_snapshot
from .source_gateway import PublicGateway, SyntheticPrivateSource
from .validator import validate_public

RUNNER_VERSION = "r2-m-eng-synthetic-runner/1"
RUN_ARMS = ("F00", "F10", *CONTROL_ARMS)


def run_synthetic(output_dir: str | Path, *,
                  coefficients: tuple[int, int, int, int],
                  point: tuple[int, int, int]) -> dict[str, object]:
    """Isolated artificial law: one public journal, one immutable Snapshot,
    seven fresh child processes, a partial UNKNOWN closure, no ground-truth use.
    """
    if type(coefficients) is not tuple or len(coefficients) != 4:
        raise ValueError("INVALID: explicit artificial four-bit fixture required")
    for value in coefficients:
        check_bit(value)
    check_point(point)
    root = Path(output_dir).resolve()
    if root.exists():
        raise ValueError("INVALID: a fresh output directory is required")
    root.mkdir(parents=True, exist_ok=False)
    (root / "traces").mkdir()
    (root / "children").mkdir()

    # Evaluator-only synthetic source is never passed to child processes or
    # serialized into the learner's snapshot/trace/closure outputs.
    gateway = PublicGateway(SyntheticPrivateSource(coefficients),
                            opened_at=5, expires_at=20)
    state = gateway.public_state(now=5)
    precommit = gateway.precommit(
        PUBLIC_POINTS[3], expected_legal_digest=state["legal_digest"],
        prediction=None, now=6,
    )
    gateway.answer(PUBLIC_POINTS[3], precommit=precommit, now=7)
    history = gateway.public_state(now=7)["observations"]
    journal = gateway.public_journal()
    decoded = decode_public(history)
    if decoded.body is None or not validate_public(decoded.body, history).passed:
        raise ValueError("VALIDATION_FAILED: artificial public decoder")

    reference = write_snapshot(root / "snapshot.json", history, journal,
                               decoded.body, expires_at=20)
    report = audit_closure(reference.path, expected_sha256=reference.sha256)
    validate_closure_audit(reference.path, expected_sha256=reference.sha256,
                           record=report)
    closure_file = write_trace_once(root / "closure.json", report)

    repo_root = Path(__file__).resolve().parents[2]
    child_env = dict(os.environ)
    child_env["PYTHONPATH"] = (
        str(repo_root) + os.pathsep + child_env.get("PYTHONPATH", "")
    )
    receipts: dict[str, dict[str, object]] = {}
    for arm in RUN_ARMS:
        cwd = root / "children" / arm
        cwd.mkdir()
        trace_path = root / "traces" / (arm + ".json")
        child_module = (
            "packages.r2_m_eng.dispatch" if arm in ("F00", "F10")
            else "packages.r2_m_eng.controls"
        )
        args = [
            sys.executable, "-m", child_module,
            "--snapshot", reference.path, "--sha256", reference.sha256,
            "--point", "".join(map(str, point)), "--arm", arm,
            "--trace-output", str(trace_path),
        ]
        # No fixture coefficient, source instance, oracle, or expected label
        # appears in args/environment constructed here.
        proc = subprocess.run(args, cwd=cwd, env=child_env,
                              capture_output=True, text=True,
                              timeout=30, check=True)
        response = json.loads(proc.stdout)
        raw = trace_path.read_bytes()
        receipt = response["trace_file"]
        if (receipt["absolute_path"] != str(trace_path.resolve())
                or receipt["sha256"] != sha256(raw).hexdigest()
                or receipt["size_bytes"] != len(raw)):
            raise ValueError("INVALID: child receipt or trace bytes changed")
        record = json.loads(raw)
        payload = record["trace"]["payload"]
        if (record["trace_digest"] != digest(record["trace"])
                or response["trace_digest"] != record["trace_digest"]
                or payload["snapshot_sha256"] != reference.sha256
                or payload["snapshot_path_absolute"] != reference.path
                or payload["point"] != list(point)
                or payload["arm"] != arm
                or payload["m_gap"] != "UNKNOWN"
                or payload["m_use"] != "NOT_CERTIFIED"):
            raise ValueError("INVALID: child public trace not pinned or non-scientific")
        if arm in CONTROL_ARMS and payload["control_manifest_digest"] != CONTROL_DIGEST:
            raise ValueError("INVALID: control manifest mismatch")
        receipts[arm] = {
            "absolute_path": receipt["absolute_path"],
            "sha256": receipt["sha256"],
            "trace_digest": record["trace_digest"],
        }

    # Public execution inventory only. Deliberately NO score table, ground
    # truth comparison, causal use result, or scientific certification.
    result = {
        "runner_version": RUNNER_VERSION,
        "engineering_only": True,
        "fixture": "human_supplied_known_affine_law_no_scientific_evidence",
        "snapshot_path_absolute": reference.path,
        "snapshot_sha256": reference.sha256,
        "snapshot_size_bytes": reference.size_bytes,
        "closure_file": closure_file,
        "closure_status": "UNKNOWN",
        "control_manifest_digest": CONTROL_DIGEST,
        "arms": receipts,
        "F01": "NOT_EVALUATED", "F11": "NOT_EVALUATED",
        "oracle_ref": "EVALUATOR_ONLY_NOT_EXECUTED",
        "m_use": "NOT_CERTIFIED", "m_gap": "UNKNOWN",
        "n_rep": "NOT_EVALUATED", "u": "NOT_EVALUATED",
        "t": "NOT_EVALUATED", "scientific_scoring": "NOT_AUTHORIZED",
    }
    write_trace_once(root / "public_manifest.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=(
        "R2-M-ENG artificial fixture only; no scientific scoring or private USE"
    ))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--synthetic-affine", required=True,
                        help="explicit four human-supplied bits a,b,c,d")
    parser.add_argument("--point", default="111",
                        help="public query input only, no USE answer")
    args = parser.parse_args()
    if (len(args.synthetic_affine) != 4 or
            any(bit not in "01" for bit in args.synthetic_affine)):
        parser.error("--synthetic-affine requires 4 binary digits")
    if len(args.point) != 3 or any(bit not in "01" for bit in args.point):
        parser.error("--point requires 3 binary digits")
    result = run_synthetic(
        args.output_dir,
        coefficients=tuple(int(bit) for bit in args.synthetic_affine),
        point=tuple(int(bit) for bit in args.point),
    )
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
