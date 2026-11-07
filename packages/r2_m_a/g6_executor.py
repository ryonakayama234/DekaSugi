"""G6 formal raw receipt bridge; no evaluator truth, score or retry here."""
from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
import platform
import re
import sys

from .contracts import ChildRequest, Slot
from .g6_order import G6Blocked, canonical, sha
from .g6_measurement import MeasurementReceipt, ProductionPermit
from .g6_scope import RehearsalPermit

TOKEN = re.compile(r"[0-9a-f]{32}\\Z")
FORMAL_STATUSES = frozenset({
    "TRACE_PRESENT", "INVALID", "RESOURCE_STOP",
    "RUN_BLOCK", "UNMEASURED", "BOUNDARY_REVIEW",
})


def make_formal_receipt(slot: Slot, request: ChildRequest,
                        permit: ProductionPermit | RehearsalPermit,
                        result: dict) -> MeasurementReceipt:
    """Construct one formal MeasurementReceipt from actual supervisor observations.

    The G3 synthetic/engineering receipt is not itself a formal result.
    Missing metrology is represented by None, NEVER made up as zero.
    """
    if (type(permit) not in (ProductionPermit, RehearsalPermit)
            or type(result) is not dict
            or result.get("engineering_only") is not False):
        raise G6Blocked("RUN_BLOCK: formal child receipt absent")
    status = result.get("status")
    if status not in FORMAL_STATUSES:
        raise G6Blocked("RUN_BLOCK: child returned unregistered status")
    cost = result.get("raw_cost")
    if type(cost) is not dict:
        raise G6Blocked("RUN_BLOCK: supervisor raw metrology absent")
    process, cgroup = cost.get("process_total"), cost.get("cgroup")
    if type(process) is not dict or type(cgroup) is not dict:
        raise G6Blocked("RUN_BLOCK: supervisor cost fields absent")
    wall = process.get("monotonic_wall_seconds")
    cpu = process.get("wait4_cpu_seconds")
    rss = process.get("wait4_peak_rss_bytes")
    peak = cgroup.get("memory_peak_bytes")
    if status == "TRACE_PRESENT" and any(v is None for v in (wall, cpu, rss, peak)):
        status = "UNMEASURED"
    reason = result.get("reason")
    if status != "TRACE_PRESENT":
        reason = reason if type(reason) is str and reason else status
    else:
        reason = None
    receipt = MeasurementReceipt(
        slot=slot.as_dict(),
        request_sha256=sha(canonical(request.as_dict())),
        run_lock_sha256=permit.lock_sha256,
        status=status, trace_sha256=result.get("trace_sha256"),
        stdout_sha256=result.get("stdout_sha256"),
        stderr_sha256=result.get("stderr_sha256"),
        wall_seconds=wall, cpu_seconds=cpu,
        peak_rss_bytes=rss, cgroup_peak_bytes=peak,
        exit_code=result.get("exit_code"),
        reaped=result.get("reaped"),
        stop_reason=reason,
        environment={"runner_os": sys.platform, "python": platform.python_version(),
                     "cgroup_v2": True, "kernel": platform.release()},
    )
    receipt.verify(slot, request, permit)
    return receipt


def seal_local_receipt(directory: str | Path, token: str,
                       receipt: MeasurementReceipt) -> Path:
    """Write-once local evidence. Remote SLOT_FINISHED binds its exact digest.

    A failed write after reservation must NOT mark a slot finished.
    """
    if type(token) is not str or not TOKEN.fullmatch(token):
        raise G6Blocked("RUN_BLOCK: receipt filename is not opaque")
    folder = Path(directory).resolve(strict=True)
    path = folder / ("receipt-" + token + ".json")
    raw = canonical(asdict(receipt))
    if sha(raw) != receipt.digest:
        raise G6Blocked("RUN_BLOCK: measurement receipt changed")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o400)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        dirfd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    except OSError as exc:
        raise G6Blocked("RUN_BLOCK: receipt write-once seal unavailable") from exc
    if sha(path.read_bytes()) != receipt.digest:
        raise G6Blocked("RUN_BLOCK: receipt local readback mismatch")
    return path
