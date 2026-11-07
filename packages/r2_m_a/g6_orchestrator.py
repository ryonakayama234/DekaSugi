"""G6-1 fail-closed remote-first orchestration, recovery and synthetic tests.

No scientific run or score entrypoint. G3 engineering-only paths are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import tempfile
from typing import Callable

from .contracts import (ARMS, EXPECTED_SLOTS, G2_MAIN_SHA, G2_PREREG_SHA256,
                        PAID_Q001, WALL_SECONDS_CAP, PROCESS_CPU_SECONDS_CAP,
                        RSS_BYTES_CAP, ChildRequest, Slot)
from .g6_order import (G5_COMMIT, G5_SHA256, G5_TARGET, G6Blocked, SealedG5,
                       canonical, sha, load_pinned_g5)
from .g6_measurement import OwnerGOReference, MeasurementReceipt, authorize_g6
from packages.r2_m_eng.records import (PublicObservation, public_evidence_digest,
                                        validate_public_history)
from packages.r2_m_eng.snapshot import write_snapshot, load_snapshot, _journal_checked
from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.sleep_lite import sleep_lite

RUN_BRANCH = "refs/heads/audit/r2ma/g6-run-20261107"
ROOT = "audit/r2ma/g6"
EVENT_SCHEMA = "r2ma-g6-event/1"
LOCK_SCHEMA = "r2ma-g6-run-lock/1"
ZERO = "0" * 64
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
TOKEN = re.compile(r"[0-9a-f]{32}\Z")
TERMINAL = {"TRACE_PRESENT", "INVALID", "RESOURCE_STOP", "RUN_BLOCK",
            "UNMEASURED", "BOUNDARY_REVIEW"}


def run_lock(g5: SealedG5) -> dict:
    if (type(g5) is not SealedG5
            or g5.pinned_commit != G5_COMMIT or g5.raw_sha256 != G5_SHA256):
        raise G6Blocked("RUN_BLOCK: G5 not pinned")
    return {"schema": LOCK_SCHEMA, "target_head": G5_TARGET,
            "g2_main_sha": G2_MAIN_SHA, "g2_prereg_sha256": G2_PREREG_SHA256,
            "g5_pin": G5_COMMIT, "g5_raw_sha256": G5_SHA256,
            "g5_expanded_sha256": g5.expanded_sha256,
            "slot_count": EXPECTED_SLOTS, "attempts_per_slot": 1, "retry": False,
            "wall_seconds_cap": WALL_SECONDS_CAP,
            "cpu_seconds_cap": PROCESS_CPU_SECONDS_CAP,
            "rss_bytes_cap": RSS_BYTES_CAP,
            "scientific_execution": "NOT_AUTHORIZED", "score": "NOT_AUTHORIZED"}


def make_event(seq: int, kind: str, data: dict, previous: str) -> dict:
    event = {"schema": EVENT_SCHEMA, "seq": seq, "kind": kind,
             "data": data, "prev_sha256": previous}
    event["entry_sha256"] = sha(canonical(event))
    return event


def decode(raw: bytes) -> dict:
    try:
        obj = json.loads(raw.decode("utf-8"),
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        if type(obj) is not dict or canonical(obj) != raw:
            raise ValueError("not canonical")
        return obj
    except (ValueError, UnicodeError, TypeError) as exc:
        raise G6Blocked("RUN_BLOCK: noncanonical remote bytes") from exc


def checked_slot(d: object) -> Slot:
    try:
        if type(d) is not dict or set(d) != {"law_id", "point", "arm"} or type(d["point"]) is not list:
            raise ValueError("slot")
        return Slot(d["law_id"], tuple(d["point"]), d["arm"])
    except (ValueError, TypeError, KeyError) as exc:
        raise G6Blocked("RUN_BLOCK: malformed slot identity") from exc


def public_answer(data: dict) -> tuple[PublicObservation, ...]:
    try:
        if set(data) != {"law_id", "observations", "journal", "expires_at"}:
            raise ValueError("Q answer schema")
        observations = tuple(PublicObservation(
            x["seq"], tuple(x["point"]), x["answer"], x["paid"],
            x["legal_digest"], x["precommit"], x["received_at"])
            for x in data["observations"])
        validate_public_history(observations, complete=True)
        _journal_checked(data["journal"], observations, data["expires_at"])
        return observations
    except (ValueError, TypeError, KeyError) as exc:
        raise G6Blocked("RUN_BLOCK: malformed recorded public4") from exc


@dataclass
class RunState:
    g5: SealedG5
    lock: dict | None
    events: tuple[dict, ...]
    tip: str
    stages: dict[str, set[str]]
    reservations: dict[int, dict]
    finishes: dict[int, dict]
    missing: set[int]
    stopped: set[str]

    def slot_status(self, ordinal: int) -> str:
        if ordinal in self.finishes:
            return "FINISHED"
        if ordinal in self.reservations:
            return "STARTED_MISSING" if ordinal in self.missing else "RESERVED"
        return "NOT_STARTED"

    def recovery_status(self, law: str) -> str | None:
        seen = self.stages.get(law, set())
        if "Q_ATTEMPT" in seen and "Q_PRECOMMIT" not in seen:
            return "STOPPED_PRECOMMIT_UNKNOWN"
        if "Q_PRECOMMIT" in seen and "Q_ANSWER" not in seen:
            return "STOPPED_Q_UNKNOWN"
        if law in self.stopped:
            return "STOPPED_Q_UNKNOWN"
        return None


def replay(raw: tuple[bytes, ...], g5: SealedG5) -> RunState:
    """Rebuild exclusively from pinned remote canonical bytes, no workspace state."""
    if type(raw) is not tuple or type(g5) is not SealedG5:
        raise G6Blocked("RUN_BLOCK: missing remote journal")
    stages = {}
    reservations = {}
    finishes = {}
    missing = set()
    stopped = set()
    checkpoints = set()
    events = []
    previous = ZERO
    lock = None
    kinds = {"RUN_LOCK", "Q_ATTEMPT", "Q_PRECOMMIT", "Q_ANSWER",
             "SNAPSHOT_LOCK", "SLOT_RESERVED", "SLOT_FINISHED",
             "STARTED_MISSING", "STOPPED_PRECOMMIT_UNKNOWN",
             "STOPPED_Q_UNKNOWN", "LAW_CHECKPOINT"}
    law_ids = {s.law_id for s in g5.ordered}
    for ordinal, record in enumerate(raw, 1):
        e = decode(record)
        if (set(e) != {"schema", "seq", "kind", "data", "prev_sha256", "entry_sha256"}
                or e["schema"] != EVENT_SCHEMA or type(e["seq"]) is not int
                or e["seq"] != ordinal or e["kind"] not in kinds
                or e["prev_sha256"] != previous or type(e["data"]) is not dict
                or type(e["entry_sha256"]) is not str
                or not SHA64.fullmatch(e["entry_sha256"])
                or sha(canonical({k: v for k, v in e.items()
                                  if k != "entry_sha256"})) != e["entry_sha256"]):
            raise G6Blocked("RUN_BLOCK: altered remote chain/sequence")
        kind, d = e["kind"], e["data"]
        if ordinal == 1:
            if kind != "RUN_LOCK" or d != run_lock(g5):
                raise G6Blocked("RUN_BLOCK: run-lock mismatch")
            lock = d
        elif kind == "RUN_LOCK":
            raise G6Blocked("RUN_BLOCK: duplicate run-lock")
        elif kind in {"Q_ATTEMPT", "Q_PRECOMMIT", "Q_ANSWER", "SNAPSHOT_LOCK",
                      "STOPPED_PRECOMMIT_UNKNOWN", "STOPPED_Q_UNKNOWN"}:
            law = d.get("law_id")
            if law not in law_ids:
                raise G6Blocked("RUN_BLOCK: unknown law")
            seen = stages.setdefault(law, set())
            if kind == "Q_ATTEMPT":
                n = len(checkpoints) * 4 * len(ARMS)
                if (n >= EXPECTED_SLOTS or g5.ordered[n].law_id != law
                        or len(reservations) != n or len(finishes) != n):
                    raise G6Blocked("RUN_BLOCK: Q law order/checkpoint violated")
            prerequisite = {"Q_ATTEMPT": None, "Q_PRECOMMIT": "Q_ATTEMPT",
                            "Q_ANSWER": "Q_PRECOMMIT", "SNAPSHOT_LOCK": "Q_ANSWER",
                            "STOPPED_PRECOMMIT_UNKNOWN": "Q_ATTEMPT",
                            "STOPPED_Q_UNKNOWN": "Q_PRECOMMIT"}[kind]
            if (kind in seen or (prerequisite and prerequisite not in seen)
                    or law in stopped
                    or (kind == "STOPPED_PRECOMMIT_UNKNOWN" and "Q_PRECOMMIT" in seen)
                    or (kind == "STOPPED_Q_UNKNOWN" and "Q_ANSWER" in seen)):
                raise G6Blocked("RUN_BLOCK: duplicate/out-of-order Q phase")
            if kind == "Q_PRECOMMIT":
                intent = d.get("intent")
                required = {"history_sha256", "legal_sha256", "point",
                            "paid_budget_remaining", "deadline", "committed_at",
                            "method_sha256", "policy_sha256", "public_initial_count",
                            "commitment_sha256"}
                if (set(d) != {"law_id", "intent"} or type(intent) is not dict
                        or set(intent) != required or intent["point"] != list(PAID_Q001)
                        or type(intent["paid_budget_remaining"]) is not int
                        or intent["paid_budget_remaining"] != 1
                        or intent["public_initial_count"] != 3
                        or type(intent["committed_at"]) is not int
                        or type(intent["deadline"]) is not int
                        or not 0 <= intent["committed_at"] <= intent["deadline"]
                        or any(type(intent[k]) is not str or not SHA64.fullmatch(intent[k])
                               for k in ("history_sha256", "legal_sha256", "method_sha256",
                                         "policy_sha256", "commitment_sha256"))):
                    raise G6Blocked("RUN_BLOCK: invalid immutable Q intent")
            if kind == "Q_ANSWER":
                observations = public_answer(d)
                intent = next((x["data"]["intent"] for x in events
                               if x["kind"] == "Q_PRECOMMIT"
                               and x["data"]["law_id"] == law), None)
                if (intent is None or observations[3].precommit != intent["commitment_sha256"]
                        or public_evidence_digest(observations[:3]) != intent["history_sha256"]
                        or observations[3].legal_digest != intent["legal_sha256"]
                        or not intent["committed_at"] <= observations[3].received_at <= intent["deadline"]):
                    raise G6Blocked("RUN_BLOCK: public Q evidence mismatch")
            if kind == "SNAPSHOT_LOCK":
                if (set(d) != {"law_id", "sha256", "token"}
                        or type(d["sha256"]) is not str or not SHA64.fullmatch(d["sha256"])
                        or type(d["token"]) is not str or not TOKEN.fullmatch(d["token"])):
                    raise G6Blocked("RUN_BLOCK: invalid snapshot lock")
            seen.add(kind)
            if kind.startswith("STOPPED_"):
                stopped.add(law)
        elif kind in {"SLOT_RESERVED", "SLOT_FINISHED", "STARTED_MISSING"}:
            n = d.get("ordinal")
            if type(n) is not int or not (0 <= n < EXPECTED_SLOTS):
                raise G6Blocked("RUN_BLOCK: bad slot index")
            if kind == "SLOT_RESERVED":
                if (stopped or n != len(reservations) or len(finishes) != len(reservations)
                        or (n > 0 and n % (4 * len(ARMS)) == 0
                            and g5.ordered[n - 1].law_id not in checkpoints)
                        or n in reservations or set(d) != {"ordinal", "slot", "journal_tip_before", "run_lock_sha256"}
                        or checked_slot(d["slot"]) != g5.ordered[n]
                        or d["journal_tip_before"] != previous
                        or d["run_lock_sha256"] != sha(canonical(run_lock(g5)))
                        or "SNAPSHOT_LOCK" not in stages.get(g5.ordered[n].law_id, set())):
                    raise G6Blocked("RUN_BLOCK: duplicate/early reservation")
                reservations[n] = e
            elif kind == "SLOT_FINISHED":
                if (n not in reservations or n in finishes or n in missing
                        or d.get("reservation_tip") != reservations[n]["entry_sha256"]
                        or d.get("status") not in TERMINAL
                        or type(d.get("receipt_sha256")) is not str
                        or not SHA64.fullmatch(d["receipt_sha256"])):
                    raise G6Blocked("RUN_BLOCK: invalid completion")
                finishes[n] = e
            elif n not in reservations or n in finishes or n in missing:
                raise G6Blocked("RUN_BLOCK: invalid STARTED_MISSING")
            else:
                missing.add(n)
        elif kind == "LAW_CHECKPOINT":
            count = len(finishes)
            root = sha(canonical({"run_lock": run_lock(g5), "prior_tip": previous,
                                  "reserved": sorted(reservations),
                                  "finished": sorted(finishes),
                                  "missing": sorted(missing)}))
            if (set(d) != {"law_id", "root_sha256", "counts"}
                    or not count or count % (4 * len(ARMS)) != 0
                    or len(reservations) != count
                    or count != (len(checkpoints) + 1) * 4 * len(ARMS)
                    or d["law_id"] in checkpoints
                    or d["law_id"] != g5.ordered[count - 1].law_id
                    or d["root_sha256"] != root
                    or d["counts"] != {"reserved": len(reservations),
                                       "finished": count, "missing": len(missing)}):
                raise G6Blocked("RUN_BLOCK: full-run law checkpoint mismatch")
            checkpoints.add(d["law_id"])
        previous = e["entry_sha256"]
        events.append(e)
    return RunState(g5, lock, tuple(events), previous, stages,
                    reservations, finishes, missing, stopped)


class GitRunJournal:
    """Remote-only GitHub authority. Each append is a new FF commit + pinned readback.

    Actions concurrency must serialize all invocations; a racing ref change is
    rejected rather than rebased, merged, retried or force-pushed.
    """
    def __init__(self, checkout: str | Path, *,
                 repo: str = "ryonakayama234/DekaSugi"):
        self.root = Path(checkout).resolve(strict=True)
        self.ref = RUN_BRANCH
        self.repo = repo
        if (self.git("rev-parse", "--show-toplevel").strip() != str(self.root)
                or self.git("symbolic-ref", "HEAD").strip() != self.ref):
            raise G6Blocked("RUN_BLOCK: wrong run-branch checkout")
        origin = self.git("remote", "get-url", "origin").strip()
        if origin not in (f"https://github.com/{repo}", f"https://github.com/{repo}.git",
                          f"git@github.com:{repo}.git"):
            raise G6Blocked("RUN_BLOCK: wrong origin")

    def git(self, *args: str) -> str:
        try:
            return subprocess.run(["git", "-C", str(self.root), *args],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=45, check=True, text=True).stdout
        except (OSError, subprocess.SubprocessError) as exc:
            raise G6Blocked("RUN_BLOCK: git/push result unknown") from exc

    def object(self, commit: str, path: str) -> bytes:
        if (type(commit) is not str or not SHA40.fullmatch(commit)
                or not path.startswith("audit/r2ma/")):
            raise G6Blocked("RUN_BLOCK: invalid pinned path")
        try:
            return subprocess.run(["git", "-C", str(self.root), "show", f"{commit}:{path}"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=45, check=True).stdout
        except (OSError, subprocess.SubprocessError) as exc:
            raise G6Blocked("RUN_BLOCK: pinned remote blob unavailable") from exc

    def head(self, ref: str) -> str:
        lines = self.git("ls-remote", "--exit-code", "origin", ref).splitlines()
        if len(lines) != 1:
            raise G6Blocked("RUN_BLOCK: missing/ambiguous remote ref")
        parts = lines[0].split()
        if len(parts) != 2 or parts[1] != ref or not SHA40.fullmatch(parts[0]):
            raise G6Blocked("RUN_BLOCK: invalid remote ref")
        return parts[0]

    def fetch(self, commit: str) -> None:
        self.git("fetch", "--no-tags", "origin", commit)
        if self.git("rev-parse", "FETCH_HEAD").strip() != commit:
            raise G6Blocked("RUN_BLOCK: pinned fetch SHA mismatch")

    def pinned_g5(self, ref: str, commit: str, path: str) -> bytes:
        from .g6_order import G5_BRANCH, G5_PATH
        if ref != G5_BRANCH or commit != G5_COMMIT or path != G5_PATH:
            raise G6Blocked("RUN_BLOCK: unrecognized G5 pin")
        if self.head(ref) != commit:
            raise G6Blocked("RUN_BLOCK: frozen G5 ref changed")
        self.fetch(commit)
        data = self.object(commit, path)
        if self.head(ref) != commit:
            raise G6Blocked("RUN_BLOCK: G5 ref moved during readback")
        return data

    def load(self) -> tuple[bytes, ...]:
        """Never trust unpushed local events or workspace-derived state."""
        head = self.head(self.ref)
        self.fetch(head)
        paths = self.git("ls-tree", "-r", "--name-only", head, "--", ROOT).splitlines()
        if self.head(self.ref) != head:
            raise G6Blocked("RUN_BLOCK: remote changed during load")
        event_files = sorted(p for p in paths if p.startswith(ROOT + "/events/"))
        markers = {p for p in paths if p.startswith(ROOT + "/reservations/")}
        if (set(paths) != set(event_files) | markers
                or any(p != f"{ROOT}/events/{i:06d}.json"
                       for i, p in enumerate(event_files, 1))):
            raise G6Blocked("RUN_BLOCK: missing/unexpected remote journal files")
        events = tuple(self.object(head, p) for p in event_files)
        expected = {}
        for raw in events:
            e = decode(raw)
            if e.get("kind") == "SLOT_RESERVED":
                n = e.get("data", {}).get("ordinal")
                if type(n) is not int or n in expected:
                    raise G6Blocked("RUN_BLOCK: malformed write-once slot")
                expected[n] = raw
        required = {f"{ROOT}/reservations/{n:03d}.json" for n in expected}
        if markers != required:
            raise G6Blocked("RUN_BLOCK: missing or extra remote reservation")
        for n, raw in expected.items():
            if self.object(head, f"{ROOT}/reservations/{n:03d}.json") != raw:
                raise G6Blocked("RUN_BLOCK: reservation pinned bytes changed")
        return events

    def append(self, kind: str, data: dict, *, expected_tip: str,
               g5: SealedG5) -> dict:
        rows = self.load()
        state = replay(rows, g5)
        if state.tip != expected_tip:
            raise G6Blocked("RUN_BLOCK: remote CAS journal tip moved")
        event = make_event(len(rows) + 1, kind, data, state.tip)
        replay((*rows, canonical(event)), g5)
        head = self.head(self.ref)
        if self.git("rev-parse", "HEAD").strip() != head:
            raise G6Blocked("RUN_BLOCK: checkout and remote diverged")
        if self.git("diff", "--cached", "--name-only").strip():
            raise G6Blocked("RUN_BLOCK: dirty Git index")
        rel = f"{ROOT}/events/{event['seq']:06d}.json"
        files = {rel: canonical(event)}
        if kind == "SLOT_RESERVED":
            files[f"{ROOT}/reservations/{data['ordinal']:03d}.json"] = canonical(event)
        try:
            for rel, raw in files.items():
                target = self.root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o400)
                with os.fdopen(fd, "wb") as f:
                    f.write(raw)
                    f.flush()
                    os.fsync(f.fileno())
            self.git("add", "--", *files)
            self.git("commit", "-m", "R2-M-A G6 checkpoint " + event["entry_sha256"],
                     "--only", "--", *files)
            commit = self.git("rev-parse", "HEAD").strip()
            # Non-force FF only; UNKNOWN means never retry the one-shot operation.
            self.git("push", "--porcelain", "origin", "HEAD:" + self.ref)
            if self.head(self.ref) != commit:
                raise G6Blocked("RUN_BLOCK: remote push acknowledgement mismatch")
            self.fetch(commit)
            for rel, raw in files.items():
                if self.object(commit, rel) != raw:
                    raise G6Blocked("RUN_BLOCK: pinned remote readback mismatch")
            if self.head(self.ref) != commit:
                raise G6Blocked("RUN_BLOCK: remote moved after pinned readback")
            return event
        except (G6Blocked, OSError) as exc:
            raise G6Blocked("RUN_BLOCK: remote push/readback outcome unknown") from exc


def restore_locked_snapshot(answer: dict, lock: dict,
                            artifact_dir: str | Path) -> Path:
    """Always regenerate from recorded public4; cached local bytes are not truth."""
    token = lock.get("token")
    if type(token) is not str or not TOKEN.fullmatch(token):
        raise G6Blocked("RUN_BLOCK: invalid opaque snapshot token")
    observations = public_answer(answer)
    decoded = decode_public(observations)
    if (decoded.body is None or decoded.decoder_invocations != 1
            or decoded.candidates_generated != 1):
        raise G6Blocked("RUN_BLOCK: public4 cannot uniquely restore")
    normalized, receipt = sleep_lite(decoded.body, observations)
    if not receipt.meaning_preserved_all_8:
        raise G6Blocked("RUN_BLOCK: public4 Sleep-lite failed")
    folder = Path(artifact_dir).resolve(strict=True)
    dest = folder / ("snapshot-" + token + ".json")
    with tempfile.TemporaryDirectory(prefix="g6-public4-") as tmp:
        temp = Path(tmp) / "public.json"
        write_snapshot(temp, observations, tuple(answer["journal"]), normalized,
                       expires_at=answer["expires_at"])
        raw = temp.read_bytes()
    if sha(raw) != lock.get("sha256"):
        raise G6Blocked("RUN_BLOCK: regenerated snapshot digest mismatch")
    if dest.is_symlink():
        raise G6Blocked("RUN_BLOCK: snapshot path symlink")
    if dest.exists():
        if not dest.is_file() or dest.read_bytes() != raw:
            raise G6Blocked("RUN_BLOCK: cached snapshot diverges")
    else:
        fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o400)
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
    load_snapshot(str(dest), expected_sha256=lock["sha256"])
    return dest


class G6Orchestrator:
    """Remote-first finite-state controller. No built-in scientific executor."""

    def __init__(self, remote, g5: SealedG5, artifact_dir: str | Path):
        if type(g5) is not SealedG5 or len(g5.ordered) != EXPECTED_SLOTS:
            raise G6Blocked("RUN_BLOCK: G5 expansion absent")
        if type(remote) is GitRunJournal:
            if load_pinned_g5(remote.pinned_g5) != g5:
                raise G6Blocked("RUN_BLOCK: G5 remote readback mismatch")
        self.remote = remote
        self.g5 = g5
        self.artifact_dir = Path(artifact_dir).resolve(strict=True)
        self._production_permit = None

    def state(self) -> RunState:
        return replay(self.remote.load(), self.g5)

    def _append(self, kind: str, data: dict) -> RunState:
        if type(self.remote) is GitRunJournal and self._production_permit is None:
            raise G6Blocked("RUN_BLOCK: G6-3 Owner GO required for remote writes")
        before = self.state()
        self.remote.append(kind, data, expected_tip=before.tip, g5=self.g5)
        after = self.state()
        if (len(after.events) != len(before.events) + 1
                or after.events[-1]["kind"] != kind
                or after.events[-1]["prev_sha256"] != before.tip):
            raise G6Blocked("RUN_BLOCK: pinned remote transition unconfirmed")
        return after

    def initialize(self, *, owner_go=None) -> RunState:
        if type(self.remote) is GitRunJournal:
            self._production_permit = authorize_g6(self.g5, run_lock(self.g5), owner_go)
        if self.state().lock is not None:
            raise G6Blocked("RUN_BLOCK: run-lock already sealed")
        return self._append("RUN_LOCK", run_lock(self.g5))

    def resume(self) -> RunState:
        """Any reserved slot missing terminal evidence is permanently nonspawnable."""
        state = self.state()
        if state.lock is None:
            raise G6Blocked("RUN_BLOCK: remote run-lock missing")
        for n in sorted(state.reservations):
            if n not in state.finishes and n not in state.missing:
                state = self._append("STARTED_MISSING", {"ordinal": n})
        for law in dict.fromkeys(slot.law_id for slot in self.g5.ordered):
            reason = state.recovery_status(law)
            if reason and law not in state.stopped:
                state = self._append(reason, {"law_id": law})
        if state.missing or state.stopped:
            missing = "STARTED_MISSING; " if state.missing else ""
            unknown = ", ".join(sorted({state.recovery_status(law) or "STOPPED_Q_UNKNOWN"
                                        for law in state.stopped}))
            raise G6Blocked("RUN_BLOCK: " + missing + unknown + "; Owner decision required")
        return state

    def precommit_synthetic(self, law: str, intent: dict) -> RunState:
        """One-shot mock Q precommit. First seal Q_ATTEMPT before Q_PRECOMMIT.

        If the second remote push is uncertain, the first irreversible marker
        remains and a subsequent run may NEVER precommit a second time.
        """
        self.resume()
        if law not in {s.law_id for s in self.g5.ordered} or law in self.state().stages:
            raise G6Blocked("RUN_BLOCK: duplicate/unknown precommit attempt")
        self._append("Q_ATTEMPT", {"law_id": law})
        return self._append("Q_PRECOMMIT", {"law_id": law, "intent": intent})

    def record_synthetic_q(self, law: str, observations: tuple[PublicObservation, ...],
                           journal: tuple[dict, ...], expires_at: int) -> RunState:
        """Store the actual public Q response, not merely its hash."""
        state = self.state()
        if "Q_PRECOMMIT" not in state.stages.get(law, set()) or "Q_ANSWER" in state.stages.get(law, set()):
            raise G6Blocked("RUN_BLOCK: paid Q already used/not precommitted")
        data = {"law_id": law, "observations": [o.as_dict() for o in observations],
                "journal": list(journal), "expires_at": expires_at}
        public_answer(data)
        return self._append("Q_ANSWER", data)

    def snapshot_synthetic(self, law: str, *, token: str) -> Path:
        self.resume()
        state = self.state()
        if type(token) is not str or not TOKEN.fullmatch(token):
            raise G6Blocked("RUN_BLOCK: snapshot path must be opaque")
        if "SNAPSHOT_LOCK" in state.stages.get(law, set()):
            raise G6Blocked("RUN_BLOCK: duplicate snapshot lock")
        answer = next((e["data"] for e in state.events
                       if e["kind"] == "Q_ANSWER" and e["data"]["law_id"] == law), None)
        if answer is None:
            raise G6Blocked("RUN_BLOCK: public4 not remotely recorded")
        observations = public_answer(answer)
        decoded = decode_public(observations)
        if decoded.body is None or decoded.decoder_invocations != 1 or decoded.candidates_generated != 1:
            raise G6Blocked("RUN_BLOCK: invalid snapshot decoder")
        body, receipt = sleep_lite(decoded.body, observations)
        if not receipt.meaning_preserved_all_8:
            raise G6Blocked("RUN_BLOCK: Sleep-lite semantic change")
        path = self.artifact_dir / ("snapshot-" + token + ".json")
        if path.exists() or path.is_symlink():
            raise G6Blocked("RUN_BLOCK: snapshot cannot overwrite")
        write_snapshot(path, observations, tuple(answer["journal"]), body,
                       expires_at=answer["expires_at"])
        digest = sha(path.read_bytes())
        lock = {"law_id": law, "sha256": digest, "token": token}
        self._append("SNAPSHOT_LOCK", lock)
        return restore_locked_snapshot(answer, lock, self.artifact_dir)

    def _reserve(self, ordinal: int, *, trace_token: str) -> tuple[Slot, ChildRequest]:
        self.resume()
        state = self.state()
        if (type(ordinal) is not int or not 0 <= ordinal < EXPECTED_SLOTS
                or state.slot_status(ordinal) != "NOT_STARTED"
                or type(trace_token) is not str or not TOKEN.fullmatch(trace_token)):
            raise G6Blocked("RUN_BLOCK: duplicate/invalid slot or nonopaque trace")
        slot = self.g5.ordered[ordinal]
        answer = next((e["data"] for e in state.events
                       if e["kind"] == "Q_ANSWER" and e["data"]["law_id"] == slot.law_id), None)
        lock = next((e["data"] for e in state.events
                     if e["kind"] == "SNAPSHOT_LOCK" and e["data"]["law_id"] == slot.law_id), None)
        if answer is None or lock is None:
            raise G6Blocked("RUN_BLOCK: missing public4 or snapshot lock")
        snap = restore_locked_snapshot(answer, lock, self.artifact_dir)
        trace = self.artifact_dir / ("trace-" + trace_token + ".json")
        if trace.exists() or trace.is_symlink():
            raise G6Blocked("RUN_BLOCK: trace target not fresh")
        request = ChildRequest(str(snap), lock["sha256"], slot.arm, slot.point, str(trace))
        self._append("SLOT_RESERVED", {"ordinal": ordinal,
                     "slot": slot.as_dict(), "journal_tip_before": state.tip,
                     "run_lock_sha256": sha(canonical(run_lock(self.g5)))})
        # A second pinned readback confirms remote state before any spawn.
        if ordinal not in self.state().reservations:
            raise G6Blocked("RUN_BLOCK: slot not remotely confirmed; no spawn")
        return slot, request

    def run_synthetic_slot(self, ordinal: int, *, trace_token: str,
                           fake_spawn: Callable[[ChildRequest], dict]) -> RunState:
        if type(self.remote) is GitRunJournal or not callable(fake_spawn):
            raise G6Blocked("RUN_BLOCK: synthetic callback not allowed on real audit ref")
        slot, request = self._reserve(ordinal, trace_token=trace_token)
        # Faults at this boundary are irreversible. No try/retry wrapper.
        result = fake_spawn(request)
        if (type(result) is not dict or set(result) != {"status", "receipt_sha256"}
                or result["status"] not in TERMINAL
                or type(result["receipt_sha256"]) is not str
                or not SHA64.fullmatch(result["receipt_sha256"])):
            raise G6Blocked("RUN_BLOCK: invalid terminal synthetic receipt")
        reserved = self.state().reservations[ordinal]
        return self._append("SLOT_FINISHED", {"ordinal": ordinal,
                            "reservation_tip": reserved["entry_sha256"], **result})

    def run_production_slot(self, ordinal: int, *, trace_token: str,
                            owner_go: object = None, measurement_executor=None):
        # G6-1 cannot open the executable path: no audited G6 measurement
        # executor has been installed. Even if approval is later published,
        # a separately reviewed G6-3 implementation is required to enable it.
        authorize_g6(self.g5, run_lock(self.g5), owner_go)
        raise G6Blocked("RUN_BLOCK: audited G6 measurement executor not installed")

    def checkpoint_law(self, law: str) -> RunState:
        """Additional per-law full-run root seal; does not replace slot seals."""
        state = self.state()
        if law not in {slot.law_id for slot in self.g5.ordered}:
            raise G6Blocked("RUN_BLOCK: unknown law")
        root = {"run_lock": run_lock(self.g5), "prior_tip": state.tip,
                "reserved": sorted(state.reservations),
                "finished": sorted(state.finishes), "missing": sorted(state.missing)}
        return self._append("LAW_CHECKPOINT", {"law_id": law,
                            "root_sha256": sha(canonical(root)),
                            "counts": {"reserved": len(state.reservations),
                                       "finished": len(state.finishes),
                                       "missing": len(state.missing)}})
