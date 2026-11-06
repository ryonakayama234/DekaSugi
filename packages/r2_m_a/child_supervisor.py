"""G3-2 Linux fresh-child supervisor, engineering-only; no scientific runner.

Single spawn per reserved trace, independent process session/group, Linux
PDEATHSIG child bootstrap, cgroup-v2 memory fail-closed, parent monotonic +
wait4 metering, and proactive /proc child CPU watch. Never run an evaluator.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import tempfile
import time

from .contracts import (
    ChildRequest, PROCESS_CPU_SECONDS_CAP, RSS_BYTES_CAP, WALL_SECONDS_CAP,
    rss_boundary_status, verify_child_payload,
)
from .cost_accounting import RawProcessCost, accounting_rows

POLL_SECONDS = 0.01
POST_KILL_REAP_SECONDS = 1.0


class RunBlocked(RuntimeError):
    """A missing safety capability is NOT a valid measurement."""


def _linux_required() -> None:
    if sys.platform != "linux" or not hasattr(os, "wait4") or not hasattr(os, "killpg"):
        raise RunBlocked("RUN_BLOCK: Linux wait4, process groups and /proc required")
    try:
        if os.sysconf("SC_CLK_TCK") <= 0:
            raise ValueError
    except (OSError, ValueError):
        raise RunBlocked("RUN_BLOCK: unavailable /proc CPU clock")


def _integer_file(path: Path) -> int:
    try:
        value = path.read_text(encoding="ascii").strip()
        result = int(value)
        if result < 0:
            raise ValueError
        return result
    except (OSError, ValueError) as exc:
        raise RunBlocked("RUN_BLOCK: missing/malformed cgroup counter " + path.name) from exc


def _memory_events(path: Path) -> dict[str, int]:
    try:
        rows = (line.split() for line in path.read_text(encoding="ascii").splitlines())
        result = {key: int(value) for key, value in rows}
        if not {"oom", "oom_kill"}.issubset(result) or any(v < 0 for v in result.values()):
            raise ValueError
        return result
    except (OSError, ValueError) as exc:
        raise RunBlocked("RUN_BLOCK: cgroup memory.events unavailable") from exc


@dataclass(slots=True)
class CgroupV2Lease:
    path: Path
    initial_events: dict[str, int]

    @classmethod
    def create(cls, delegated_root: str | Path) -> "CgroupV2Lease":
        """Require already-delegated memory controller. Never enable host fallback."""
        _linux_required()
        base = Path(delegated_root)
        if (not base.is_absolute() or base.is_symlink()
                or str(base.resolve()) != str(base) or not base.is_dir()):
            raise RunBlocked("RUN_BLOCK: canonical delegated cgroup v2 root required")
        try:
            if "memory" not in (base / "cgroup.controllers").read_text().split():
                raise RunBlocked("RUN_BLOCK: cgroup memory controller unavailable")
            if "memory" not in (base / "cgroup.subtree_control").read_text().split():
                raise RunBlocked("RUN_BLOCK: cgroup memory controller not delegated")
            path = base / ("r2ma-" + str(os.getpid()) + "-" + secrets.token_hex(8))
            path.mkdir(mode=0o700)
        except (OSError, ValueError) as exc:
            raise RunBlocked("RUN_BLOCK: cannot create delegated cgroup") from exc
        try:
            # These files must exist in the kernel cgroup2 FS, not as regular
            # files fabricated on a fallback directory.
            for name in ("cgroup.procs", "cgroup.kill", "memory.max",
                         "memory.swap.max", "memory.oom.group", "memory.events",
                         "memory.peak", "cgroup.events"):
                item = path / name
                if not item.is_file() or not str(item.resolve()).startswith(str(path) + "/"):
                    raise RunBlocked("RUN_BLOCK: missing cgroup v2 interface " + name)
            (path / "memory.max").write_text(str(RSS_BYTES_CAP))
            if (path / "memory.max").read_text().strip() != str(RSS_BYTES_CAP):
                raise RunBlocked("RUN_BLOCK: memory.max not enforced")
            (path / "memory.swap.max").write_text("0")
            if (path / "memory.swap.max").read_text().strip() != "0":
                raise RunBlocked("RUN_BLOCK: swap guard not enforced")
            (path / "memory.oom.group").write_text("1")
            if (path / "memory.oom.group").read_text().strip() != "1":
                raise RunBlocked("RUN_BLOCK: group OOM policy not enforced")
            start = _memory_events(path / "memory.events")
            _integer_file(path / "memory.peak")
            return cls(path, start)
        except BaseException:
            try:
                path.rmdir()
            except OSError:
                pass
            raise

    def attach(self, pid: int) -> None:
        if type(pid) is not int or pid < 2:
            raise RunBlocked("RUN_BLOCK: invalid child PID")
        try:
            (self.path / "cgroup.procs").write_text(str(pid))
            members = (self.path / "cgroup.procs").read_text().split()
            if str(pid) not in members:
                raise RunBlocked("RUN_BLOCK: child not confirmed in cgroup")
        except OSError as exc:
            raise RunBlocked("RUN_BLOCK: child cgroup attachment failed") from exc

    def memory_observation(self) -> tuple[int, dict[str, int]]:
        return _integer_file(self.path / "memory.peak"), _memory_events(
            self.path / "memory.events")

    def kill(self) -> None:
        try:
            (self.path / "cgroup.kill").write_text("1")
        except OSError as exc:
            raise RunBlocked("RUN_BLOCK: cgroup.kill unavailable") from exc

    def cleanup(self) -> None:
        # cgroup.kill is mandatory even when the leader exited: grandchildren
        # might have left its original process group but still share the cgroup.
        self.kill()
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            try:
                if "populated 0" in (self.path / "cgroup.events").read_text():
                    self.path.rmdir()
                    return
            except OSError:
                pass
            time.sleep(POLL_SECONDS)
        raise RunBlocked("RUN_BLOCK: cgroup still populated / cleanup not verified")


def _live_cpu_seconds(pid: int) -> float:
    """Read Linux /proc/<pid>/stat fields 14+15, not the *parent* CPU."""
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
        tail = raw[raw.rindex(")") + 2:].split()
        ticks = int(tail[11]) + int(tail[12])
        if ticks < 0:
            raise ValueError
        return ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError) as exc:
        raise RunBlocked("RUN_BLOCK: cannot observe child CPU live") from exc


def _kill_group(pid: int) -> None:
    """Never target only the leader PID."""
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


@dataclass(frozen=True, slots=True)
class Wait4Result:
    wait_status: int | None
    cpu_seconds: float | None
    peak_rss_bytes: int | None
    stopped_for: str | None
    wall_seconds: float
    reaped: bool


def _wait_with_watchdog(pid: int, *, start: float, cgroup: CgroupV2Lease,
                        wall_cap: float = WALL_SECONDS_CAP,
                        cpu_cap: float = PROCESS_CPU_SECONDS_CAP) -> Wait4Result:
    """Single wait4/reap owner. Caps are fixed at caller; test can inject tighter caps."""
    stopped: str | None = None
    raw_status = None
    usage = None
    kill_started: float | None = None
    while True:
        got, status, ru = os.wait4(pid, os.WNOHANG)
        if got == pid:
            raw_status, usage = status, ru
            break
        now = time.monotonic()
        if stopped is None:
            if now - start >= wall_cap:
                stopped = "WALL"
            else:
                try:
                    if _live_cpu_seconds(pid) >= cpu_cap:
                        stopped = "CPU"
                except RunBlocked:
                    stopped = "CPU_UNMEASURED"
        if stopped is not None:
            _kill_group(pid)
            cgroup.kill()
            if kill_started is None:
                kill_started = now
            elif now - kill_started > POST_KILL_REAP_SECONDS:
                break  # Never let uninterruptible D-state block indefinitely.
        time.sleep(POLL_SECONDS)
    wall = time.monotonic() - start
    if usage is None:
        return Wait4Result(None, None, None, stopped or "UNREAPED", wall, False)
    cpu = float(usage.ru_utime + usage.ru_stime)
    rss = int(usage.ru_maxrss * 1024)  # Linux wait4 reports KiB.
    if wall > wall_cap:
        stopped = stopped or "WALL_OVERRUN"
    if cpu > cpu_cap:
        stopped = stopped or "CPU_OVERRUN"
    if rss > RSS_BYTES_CAP and rss > 536_870_912:
        stopped = stopped or "RSS_OVERRUN"
    return Wait4Result(raw_status, cpu, rss, stopped, wall, True)


def _reserve_once(path: Path, payload: dict[str, object]) -> None:
    """Durable local anti-retry marker; G3-3 owns remote slot custody."""
    marker = path.with_name(path.name + ".attempt")
    body = (sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            + "\n").encode("ascii")
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o400)
        with os.fdopen(fd, "wb") as f:
            f.write(body)
            f.flush()
            os.fsync(f.fileno())
        directory = os.open(marker.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except OSError as exc:
        raise RunBlocked("RUN_BLOCK: duplicate/unwritable child attempt") from exc


def supervise_synthetic_child(
    request: ChildRequest, *, delegated_cgroup_root: str | Path,
    engineering_only: bool, law_id: str | None = None,
    child_slot: str | None = None,
) -> dict[str, object]:
    """One synthetic child only. G3-3/G5/G6 custody/order/measurement not wired.

    Production calls with engineering_only=False are rejected. No evaluator,
    USE label, score, law ID, or order seed is sent to the child.
    """
    if engineering_only is not True:
        raise RunBlocked("RUN_BLOCK: G6/scientific measurement not authorized")
    _linux_required()
    if type(request) is not ChildRequest:
        raise RunBlocked("RUN_BLOCK: invalid child contract")
    payload = request.as_dict()
    verify_child_payload(payload)
    snapshot = Path(request.snapshot_path)
    trace = Path(request.trace_path)
    if (snapshot.is_symlink() or not snapshot.is_file()
            or sha256(snapshot.read_bytes()).hexdigest() != request.expected_sha256):
        raise RunBlocked("RUN_BLOCK: missing or changed immutable Snapshot bytes")
    if not trace.parent.is_dir() or trace.exists():
        raise RunBlocked("RUN_BLOCK: trace target not fresh")
    # No weaker mode: obtain and verify cgroup BEFORE reserving or spawning.
    cgroup = CgroupV2Lease.create(delegated_cgroup_root)
    proc: subprocess.Popen | None = None
    gate_r: int | None = None
    gate_w: int | None = None
    started: float | None = None
    observation: Wait4Result | None = None
    child_receipt: dict[str, object] | None = None
    stdout_digest = stderr_digest = None
    cgroup_peak = None
    cgroup_events: dict[str, int] | None = None
    failure: str | None = None
    cleaned = False
    try:
        _reserve_once(trace, payload)
        repo_root = Path(__file__).resolve().parents[2]
        env = {
            "PYTHONPATH": str(repo_root),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "LANG": "C.UTF-8",
            "R2MA_EXPECTED_PPID": str(os.getpid()),
        }
        with tempfile.TemporaryDirectory(prefix="r2ma-fresh-") as cwd:
            gate_r, gate_w = os.pipe()
            env["R2MA_GATE_FD"] = str(gate_r)  # infra, not a research input
            with open(Path(cwd) / "stdout", "wb") as out, open(
                    Path(cwd) / "stderr", "wb") as err:
                started = time.monotonic()
                proc = subprocess.Popen(
                    [sys.executable, "-S", "-B", "-m",
                     "packages.r2_m_a.child_entry"],
                    cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=out,
                    stderr=err, start_new_session=True, pass_fds=(gate_r,),
                    close_fds=True)
                os.close(gate_r)
                gate_r = None
                cgroup.attach(proc.pid)
                os.write(gate_w, b"G")
                os.close(gate_w)
                gate_w = None
                try:
                    assert proc.stdin is not None
                    proc.stdin.write(json.dumps(payload, sort_keys=True).encode())
                    proc.stdin.close()
                except (BrokenPipeError, OSError):
                    pass  # child might have failed; wait4 preserves exit evidence
                observation = _wait_with_watchdog(proc.pid, start=started,
                                                   cgroup=cgroup)
                # Always terminate any descendant in the same process group.
                _kill_group(proc.pid)
                cgroup_peak, cgroup_events = cgroup.memory_observation()
            stdout_bytes = (Path(cwd) / "stdout").read_bytes()
            stderr_bytes = (Path(cwd) / "stderr").read_bytes()
            stdout_digest, stderr_digest = (sha256(stdout_bytes).hexdigest(),
                                            sha256(stderr_bytes).hexdigest())
            if len(stdout_bytes) <= 4096:
                try:
                    parsed = json.loads(stdout_bytes)
                    if (type(parsed) is dict and parsed.get("engineering_only") is True
                            and set(parsed) == {"engineering_only", "trace_digest",
                                                "trace_sha256", "trace_size_bytes",
                                                "import_receipt"}):
                        child_receipt = parsed
                except (ValueError, UnicodeDecodeError):
                    pass
    except (OSError, ValueError, RunBlocked) as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    finally:
        for fd in (gate_r, gate_w):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        if proc is not None:
            _kill_group(proc.pid)
            # Reap when aborted before entering the watchdog, never hang.
            if observation is None:
                deadline = time.monotonic() + POST_KILL_REAP_SECONDS
                while time.monotonic() < deadline:
                    got, _, _ = os.wait4(proc.pid, os.WNOHANG)
                    if got == proc.pid:
                        break
                    time.sleep(POLL_SECONDS)
        try:
            cgroup.cleanup()
            cleaned = True
        except RunBlocked as exc:
            failure = (failure + "; " if failure else "") + str(exc)
    if observation is None:
        raise RunBlocked(failure or "RUN_BLOCK: child did not enter wait4")
    raw = None
    if trace.is_file() and not trace.is_symlink():
        raw = trace.read_bytes()
    trace_sha = sha256(raw).hexdigest() if raw is not None else None
    imported = child_receipt.get("import_receipt") if child_receipt else None
    if type(imported) is not dict:
        imported = None
    cost = RawProcessCost(
        observation.wall_seconds, observation.cpu_seconds,
        observation.peak_rss_bytes, cgroup_peak, imported,
        len(raw) if raw is not None else None,
    )
    oom = bool(cgroup_events and any(
        cgroup_events.get(k, 0) > cgroup.initial_events.get(k, 0)
        for k in ("oom", "oom_kill")))
    valid_receipt = bool(
        child_receipt and raw is not None
        and child_receipt.get("trace_sha256") == trace_sha
        and child_receipt.get("trace_size_bytes") == len(raw))
    exit_code = (os.waitstatus_to_exitcode(observation.wait_status)
                 if observation.wait_status is not None else None)
    status = (
        "RUN_BLOCK" if failure or not cleaned or not observation.reaped
        or observation.cpu_seconds is None or observation.peak_rss_bytes is None
        or cgroup_peak is None else
        "RESOURCE_STOP" if observation.stopped_for is not None or oom else
        "INVALID" if exit_code != 0 or not valid_receipt else
        "BOUNDARY_REVIEW" if rss_boundary_status(observation.peak_rss_bytes)
        == "BOUNDARY_REVIEW" else "ENGINEERING_ONLY"
    )
    return {
        "engineering_only": True, "status": status,
        "reason": failure or observation.stopped_for,
        "exit_code": exit_code, "reaped": observation.reaped,
        "process_group_id": proc.pid if proc else None,
        "trace_sha256": trace_sha, "stdout_sha256": stdout_digest,
        "stderr_sha256": stderr_digest,
        "cgroup_memory_events": cgroup_events,
        "raw_cost": cost.as_dict(),
        "accounting_rows": accounting_rows(
            raw=cost, arm=request.arm, law_id=law_id,
            child_slot=child_slot, raw_receipt_sha256=trace_sha),
        "child_trace_digest": (
            child_receipt.get("trace_digest") if child_receipt else None),
    }
