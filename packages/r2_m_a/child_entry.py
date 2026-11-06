"""G3-2 Linux child entry point: exactly five public research inputs via stdin.

NOT a science-runner CLI. Parent-side authorization, cgroup placement, custody
and G5 order are separate gates. Never import evaluator modules here.
"""
from __future__ import annotations

import ctypes
import json
import os
import resource
import signal
import sys
import time


def arm_parent_death(expected_ppid: int) -> None:
    """PR_SET_PDEATHSIG + parent race check; requires setsid/start_new_session."""
    if (sys.platform != "linux" or expected_ppid < 2
            or os.getpgrp() != os.getpid() or os.getsid(0) != os.getpid()):
        raise RuntimeError("RUN_BLOCK: child requires own Linux session/group")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = (ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                          ctypes.c_ulong, ctypes.c_ulong)
    libc.prctl.restype = ctypes.c_int
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "RUN_BLOCK: PR_SET_PDEATHSIG failed")
    # If the parent died before the prctl call, the signal was not delivered.
    if os.getppid() != expected_ppid:
        raise RuntimeError("RUN_BLOCK: parent died before PDEATHSIG was armed")


def _startup_gate() -> None:
    try:
        expected_ppid = int(os.environ["R2MA_EXPECTED_PPID"])
        gate_fd = int(os.environ["R2MA_GATE_FD"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("RUN_BLOCK: missing parent/gate infrastructure") from exc
    arm_parent_death(expected_ppid)
    # Second barrier: parent must attach child to memory cgroup before RELEASE.
    try:
        release = os.read(gate_fd, 1)
    finally:
        os.close(gate_fd)
    if release != b"G" or os.getppid() != expected_ppid:
        raise RuntimeError("RUN_BLOCK: child not authorized/attached to cgroup")
    resource.setrlimit(resource.RLIMIT_CPU, (5, 6))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1_048_576, 1_048_576))
    os.umask(0o077)


def main() -> None:
    _startup_gate()
    import_cpu_start, import_wall_start = time.process_time(), time.perf_counter()
    # These hooks must be installed BEFORE dispatch/controls (including lazy imports).
    from packages.r2_m_a.import_guard import install_child_import_guard
    install_child_import_guard()
    from packages.r2_m_a.contracts import verify_child_payload
    raw = sys.stdin.buffer.read(4097)
    if len(raw) > 4096 or not raw:
        raise ValueError("INVALID: child request exceeds single fixed payload bound")
    request = verify_child_payload(json.loads(raw))
    # Both entrypoints imported for EVERY arm. Preserve controls.py import-time
    # catalog construction and its own CATALOG_PREPARATION_* observations.
    from packages.r2_m_eng.dispatch import predict_fixed, write_trace_once
    from packages.r2_m_eng.controls import (
        CATALOG_PREPARATION_CPU_SECONDS, CATALOG_PREPARATION_WALL_SECONDS,
        CATALOG_SERIALIZED_BYTES, MACRO_CATALOG, predict_control,
    )
    import_cost = {
        "import_cpu_seconds": time.process_time() - import_cpu_start,
        "import_wall_seconds": time.perf_counter() - import_wall_start,
        "catalog_preparation_cpu_seconds": CATALOG_PREPARATION_CPU_SECONDS,
        "catalog_preparation_wall_seconds": CATALOG_PREPARATION_WALL_SECONDS,
        "catalog_serialized_bytes": CATALOG_SERIALIZED_BYTES,
        "catalog_entries": len(MACRO_CATALOG),
        "catalog_measurement_source": "existing_r2_m_eng.controls_constants",
    }
    params = {
        "expected_sha256": request.expected_sha256,
        "point": request.point, "arm": request.arm,
    }
    if request.arm in ("F00", "F10"):
        result = predict_fixed(request.snapshot_path, **params)
    else:
        result = predict_control(request.snapshot_path, **params)
    trace_file = write_trace_once(request.trace_path, result)
    receipt = {
        "engineering_only": True,
        "trace_digest": result["trace_digest"],
        "trace_sha256": trace_file["sha256"],
        "trace_size_bytes": trace_file["size_bytes"],
        "import_receipt": import_cost,
    }
    sys.stdout.write(json.dumps(receipt, sort_keys=True, allow_nan=False) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as exc:
        # Do not echo raw requests, evaluator fields, or secret provenance.
        sys.stderr.write(type(exc).__name__ + ": " + str(exc)[:240] + "\n")
        sys.exit(2)
