"""G3-3 parent/evaluator-side custody; engineering fixtures only.

Unordered 448-slot design is a census, NOT a G5 execution manifest. Append-only
hashes detect accidental modifications when remotely anchored, but cannot
cryptographically prevent a GitHub administrator or local owner rewriting history.
No true USE labels, law source, scientific evaluator or scoring is imported.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import fcntl
import json
import os

from .contracts import (ARMS, EXPECTED_SLOTS, G2_MAIN_SHA, G2_PREREG_SHA256,
                        PAID_Q001, PUBLIC_INITIAL_POINTS, SCIENTIFIC_EXECUTION_AUTHORIZED,
                        Slot, expected_slot_set)
from .remote_custody import CustodyBlocked, RemoteReceipt

ZERO = "0" * 64
TERMINAL = frozenset({"TRACE_PRESENT", "INVALID", "RESOURCE_STOP",
                      "RUN_BLOCK", "UNMEASURED"})
SCHEMA = "r2ma-custody-g3-3/1"


def canonical(obj: object) -> bytes:
    try:
        return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise CustodyBlocked("INVALID: noncanonical/nonfinite evidence") from exc


def _sha(value: object) -> str:
    if (type(value) is not str or len(value) != 64 or
            any(c not in "0123456789abcdef" for c in value)):
        raise CustodyBlocked("INVALID: lowercase SHA256 required")
    return value


def _dirsync(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_once(path: Path, raw: bytes) -> None:
    if path.is_symlink() or not path.parent.is_dir() or path.parent.is_symlink():
        raise CustodyBlocked("RUN_BLOCK: custody directory unsafe")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                     0o400)
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        _dirsync(path.parent)
    except OSError as exc:
        raise CustodyBlocked("RUN_BLOCK: immutable artifact already exists or write failed") from exc


def _read_events(raw: bytes) -> tuple[dict, ...]:
    if raw and not raw.endswith(b"\n"):
        raise CustodyBlocked("INVALID: journal partial trailing event")
    events = []
    prev = ZERO
    for line in raw.splitlines(keepends=True):
        try:
            entry = json.loads(line.decode("utf-8"),
                               parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        except (ValueError, UnicodeError) as exc:
            raise CustodyBlocked("INVALID: invalid journal JSON/UTF-8/NaN") from exc
        if (type(entry) is not dict or set(entry) !=
                {"seq", "kind", "data", "prev_sha256", "entry_sha256"} or
                type(entry["seq"]) is not int or entry["seq"] != len(events) + 1
                or entry["prev_sha256"] != prev
                or type(entry["kind"]) is not str or type(entry["data"]) is not dict):
            raise CustodyBlocked("INVALID: journal sequence/shape/previous hash")
        digest = _sha(entry["entry_sha256"])
        content = {k: entry[k] for k in ("seq", "kind", "data", "prev_sha256")}
        if sha256(canonical(content)).hexdigest() != digest or canonical(entry) != line:
            raise CustodyBlocked("INVALID: altered or noncanonical journal event")
        prev = digest
        events.append(entry)
    _chronology(events)
    return tuple(events)


def _chronology(events: list[dict]) -> None:
    q_pre, q_remote, q_answer, snaps, started, finished = (
        set(), set(), set(), set(), set(), set())
    prescore_local = prescore_remote = False
    for entry in events:
        k, data = entry["kind"], entry["data"]
        law = data.get("law_id")
        if prescore_remote or (prescore_local and k != "PRE_SCORE_REMOTE"):
            raise CustodyBlocked("INVALID: event after local/remote pre-score freeze")
        if k == "Q_PRECOMMIT":
            if law in q_pre or law in q_remote or law not in {s.law_id for s in expected_slot_set()}:
                raise CustodyBlocked("INVALID: duplicate/unknown Q precommit")
            q_pre.add(law)
        elif k == "Q_REMOTE":
            if law not in q_pre or law in q_remote:
                raise CustodyBlocked("INVALID: Q remote before precommit / duplicate")
            q_remote.add(law)
        elif k == "Q_ANSWER":
            if law not in q_remote or law in q_answer:
                raise CustodyBlocked("INVALID: answer before verified remote / duplicate")
            q_answer.add(law)
        elif k == "SNAPSHOT_LOCK":
            if law not in q_answer or law in snaps:
                raise CustodyBlocked("INVALID: snapshot before answer / duplicate")
            snaps.add(law)
        elif k in ("SLOT_START", "SLOT_END"):
            try:
                d = data["slot"]
                slot = Slot(d["law_id"], tuple(d["point"]), d["arm"])
            except (KeyError, TypeError, ValueError) as exc:
                raise CustodyBlocked("INVALID: malformed slot event") from exc
            key = (slot.law_id, slot.point, slot.arm)
            if k == "SLOT_START":
                if slot.law_id not in snaps or key in started:
                    raise CustodyBlocked("INVALID: duplicate/early slot reservation")
                started.add(key)
            elif key not in started or key in finished or data.get("status") not in TERMINAL:
                raise CustodyBlocked("INVALID: duplicate/early slot completion")
            else:
                finished.add(key)
        elif k == "PRE_SCORE_LOCAL":
            if prescore_local:
                raise CustodyBlocked("INVALID: duplicate pre-score manifest")
            prescore_local = True
        elif k == "PRE_SCORE_REMOTE":
            if not prescore_local or prescore_remote:
                raise CustodyBlocked("INVALID: remote pre-score before local freeze")
            prescore_remote = True
        else:
            raise CustodyBlocked("INVALID: unknown journal event kind")


def _key(slot: Slot) -> tuple[str, tuple[int, int, int], str]:
    return (slot.law_id, slot.point, slot.arm)


class EvidenceLedger:
    """One run root, strictly exclusive files and linked fsynced JSONL.

    All entry points are engineering_only; there is deliberately no G6 runner.
    """

    def __init__(self, root: Path):
        self.root = Path(root).absolute()
        self.journal = self.root / "journal" / "events.jsonl"

    @classmethod
    def create(cls, root: str | Path, *, engineering_only: bool) -> "EvidenceLedger":
        if engineering_only is not True or SCIENTIFIC_EXECUTION_AUTHORIZED:
            raise CustodyBlocked("RUN_BLOCK: no G6 scientific execution authorization")
        root = Path(root).absolute()
        if root.is_symlink():
            raise CustodyBlocked("RUN_BLOCK: symlinked run root")
        try:
            root.mkdir(mode=0o700)  # existing root always rejected
            (root / "journal").mkdir(mode=0o700)
            (root / "public").mkdir(mode=0o700)
            (root / "receipts").mkdir(mode=0o700)
            _dirsync(root.parent)
        except OSError as exc:
            raise CustodyBlocked("RUN_BLOCK: existing/unwritable run root") from exc
        _write_once(root / "prereg-lock.json", canonical({
            "schema": SCHEMA, "g2_main_sha": G2_MAIN_SHA,
            "g2_prereg_sha256": G2_PREREG_SHA256,
            "scientific_execution": "NOT_AUTHORIZED",
            "g5_order": "NOT_FIXED", "g4_audit": "NOT_PERFORMED",
        }))
        _write_once(root / "expected-slots.json", canonical({
            "schema": SCHEMA, "count": EXPECTED_SLOTS,
            "enumeration_not_execution_order": True,
            "slots": [s.as_dict() for s in sorted(expected_slot_set(), key=_key)],
        }))
        _write_once(root / "journal" / "events.jsonl", b"")
        return cls(root)

    def events(self) -> tuple[dict, ...]:
        if self.journal.is_symlink():
            raise CustodyBlocked("INVALID: journal symlink")
        try:
            self._verify_initial()
            return _read_events(self.journal.read_bytes())
        except OSError as exc:
            raise CustodyBlocked("RUN_BLOCK: missing journal") from exc

    def _verify_initial(self) -> None:
        for name in ("prereg-lock.json", "expected-slots.json"):
            path = self.root / name
            if path.is_symlink():
                raise CustodyBlocked("INVALID: changed run-lock path")
            try:
                content = path.read_bytes()
                info = json.loads(content)
            except (OSError, ValueError) as exc:
                raise CustodyBlocked("INVALID: damaged run lock") from exc
            if content != canonical(info):
                raise CustodyBlocked("INVALID: noncanonical run lock")
            if name == "prereg-lock.json":
                if info != {"schema": SCHEMA, "g2_main_sha": G2_MAIN_SHA,
                    "g2_prereg_sha256": G2_PREREG_SHA256,
                    "scientific_execution": "NOT_AUTHORIZED", "g5_order": "NOT_FIXED",
                    "g4_audit": "NOT_PERFORMED"}:
                    raise CustodyBlocked("INVALID: prereg anchor changed")
            elif info != {"schema": SCHEMA, "count": EXPECTED_SLOTS,
                    "enumeration_not_execution_order": True,
                    "slots": [s.as_dict() for s in sorted(expected_slot_set(), key=_key)]}:
                raise CustodyBlocked("INVALID: planned slot set changed")

    def _append(self, kind: str, data: dict) -> dict:
        self._verify_initial()
        try:
            fd = os.open(self.journal, os.O_RDWR | os.O_APPEND | os.O_NOFOLLOW)
            with os.fdopen(fd, "r+b", buffering=0) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.seek(0)
                entries = _read_events(f.read())
                entry = {
                    "seq": len(entries) + 1, "kind": kind, "data": data,
                    "prev_sha256": entries[-1]["entry_sha256"] if entries else ZERO,
                }
                entry["entry_sha256"] = sha256(canonical(entry)).hexdigest()
                _chronology([*entries, entry])
                f.seek(0, os.SEEK_END)
                line = canonical(entry)
                if f.write(line) != len(line):
                    raise CustodyBlocked("RUN_BLOCK: short journal append")
                os.fsync(f.fileno())
                _dirsync(self.journal.parent)
                return entry
        except OSError as exc:
            raise CustodyBlocked("RUN_BLOCK: journal append failed") from exc

    def _path(self, section: str, name: str) -> Path:
        if section not in ("public", "receipts") or not name or "/" in name or ".." in name:
            raise CustodyBlocked("INVALID: unsafe custody path")
        return self.root / section / name

    def _remote_check(self, remote, proof: RemoteReceipt, path: Path) -> None:
        if type(proof) is not RemoteReceipt or not callable(getattr(remote, "verify_receipt", None)):
            raise CustodyBlocked("RUN_BLOCK: verified remote receipt required")
        if proof.content_sha256 != sha256(path.read_bytes()).hexdigest():
            raise CustodyBlocked("RUN_BLOCK: remote receipt digest mismatch")
        remote.verify_receipt(proof, path)  # must fetch actual remote pinned SHA bytes

    def precommit_q(self, law_id: str, *, history_sha256: str, legal_sha256: str,
                    deadline: int, committed_at: int, method_sha256: str,
                    policy_sha256: str, remote) -> RemoteReceipt:
        """Remote readback MUST succeed before this returns a Q-answer permit."""
        if type(deadline) is not int or type(committed_at) is not int or committed_at > deadline:
            raise CustodyBlocked("INVALID: Q expired / bad clock")
        data = {
            "law_id": law_id, "history_sha256": _sha(history_sha256),
            "legal_sha256": _sha(legal_sha256),
            "point": list(PAID_Q001), "paid_budget_remaining": 1,
            "deadline": deadline, "committed_at": committed_at,
            "method_sha256": _sha(method_sha256),
            "policy_sha256": _sha(policy_sha256),
            "public_initial_count": len(PUBLIC_INITIAL_POINTS),
        }
        event = self._append("Q_PRECOMMIT", data)
        raw = canonical({"schema": SCHEMA, "intent": data,
                         "local_event_sha256": event["entry_sha256"]})
        path = self._path("public", "q-" + law_id + "-precommit.json")
        _write_once(path, raw)
        if not callable(getattr(remote, "commit_and_verify", None)):
            raise CustodyBlocked("RUN_BLOCK: no GitHub remote publisher")
        proof = remote.commit_and_verify(path, sha256(raw).hexdigest())
        self._remote_check(remote, proof, path)
        self._append("Q_REMOTE", {"law_id": law_id, "receipt": proof.as_dict()})
        return proof

    def synthetic_answer_gate(self, law_id: str, *, remote, answer,
                              now: int) -> object:
        """Synthetic-only gate; never a 448-child or actual Q runner."""
        events = self.events()
        q = next((e for e in events if e["kind"] == "Q_PRECOMMIT"
                  and e["data"]["law_id"] == law_id), None)
        p = next((e for e in events if e["kind"] == "Q_REMOTE"
                  and e["data"]["law_id"] == law_id), None)
        if (not q or not p or type(now) is not int or now < q["data"]["committed_at"]
                or now > q["data"]["deadline"] or
                any(e["kind"] == "Q_ANSWER" and e["data"]["law_id"] == law_id
                    for e in events) or not callable(answer)):
            raise CustodyBlocked("RUN_BLOCK: Q is unverified, expired, or already used")
        receipt = RemoteReceipt(**p["data"]["receipt"])
        self._remote_check(remote, receipt, self._path("public", "q-" + law_id + "-precommit.json"))
        result = answer()
        # Explicit public digest only, no source/hidden answers or scientific score.
        self._append("Q_ANSWER", {"law_id": law_id, "public_answer_sha256":
                                  sha256(canonical(result)).hexdigest()})
        return result

    def lock_snapshot(self, law_id: str, *, snapshot_sha256: str) -> None:
        self._append("SNAPSHOT_LOCK", {"law_id": law_id,
                                     "snapshot_sha256": _sha(snapshot_sha256)})

    def start_slot(self, slot: Slot, *, engineering_only: bool) -> None:
        if engineering_only is not True or type(slot) is not Slot:
            raise CustodyBlocked("RUN_BLOCK: G6 execution unauthorized")
        self._append("SLOT_START", {"slot": slot.as_dict()})

    def finish_slot(self, slot: Slot, *, status: str,
                    raw_receipt_sha256: str | None = None,
                    trace_sha256: str | None = None,
                    missing_reason: str | None = None) -> None:
        if type(slot) is not Slot or status not in TERMINAL:
            raise CustodyBlocked("INVALID: unexpected completion status")
        if status == "TRACE_PRESENT":
            if missing_reason is not None or raw_receipt_sha256 is None or trace_sha256 is None:
                raise CustodyBlocked("INVALID: trace needs immutable raw receipt and trace SHA")
        elif type(missing_reason) is not str or not missing_reason:
            raise CustodyBlocked("INVALID: failure/missingness reason is mandatory")
        self._append("SLOT_END", {"slot": slot.as_dict(), "status": status,
                     "raw_receipt_sha256": (_sha(raw_receipt_sha256) if raw_receipt_sha256
                                            is not None else None),
                     "trace_sha256": (_sha(trace_sha256) if trace_sha256
                                       is not None else None),
                     "missing_reason": missing_reason})

    def manifest(self) -> dict:
        entries = self.events()
        by_key = {}
        for e in entries:
            if e["kind"] in ("SLOT_START", "SLOT_END"):
                d = e["data"]["slot"]
                key = (d["law_id"], tuple(d["point"]), d["arm"])
                if e["kind"] == "SLOT_START":
                    by_key[key] = {"status": "STARTED_MISSING", "trace_sha256": None,
                                   "raw_receipt_sha256": None,
                                   "missing_reason": "started without terminal receipt"}
                else:
                    by_key[key] = {k: e["data"][k] for k in (
                        "status", "trace_sha256", "raw_receipt_sha256", "missing_reason")}
        rows = []
        counts = {}
        for s in sorted(expected_slot_set(), key=_key):
            data = by_key.get(_key(s), {"status": "NOT_RUN", "trace_sha256": None,
                  "raw_receipt_sha256": None, "missing_reason": "no attempt reserved"})
            counts[data["status"]] = counts.get(data["status"], 0) + 1
            rows.append({"slot": s.as_dict(), **data})
        ready_q = {e["data"]["law_id"] for e in entries if e["kind"] == "Q_REMOTE"}
        ready_snap = {e["data"]["law_id"] for e in entries if e["kind"] == "SNAPSHOT_LOCK"}
        all_laws = {s.law_id for s in expected_slot_set()}
        return {"schema": SCHEMA, "expected_slot_count": EXPECTED_SLOTS,
                "enumeration_not_execution_order": True, "slots": rows,
                "counts": counts, "q_remote_verified_laws": len(ready_q),
                "snapshot_locked_laws": len(ready_snap),
                "eligible_for_future_score": (
                    len(ready_q) == 16 and ready_snap == all_laws
                    and counts == {"TRACE_PRESENT": EXPECTED_SLOTS}),
                "journal_tip_sha256": entries[-1]["entry_sha256"] if entries else ZERO,
                "g5_order": "NOT_FIXED", "scientific_execution": "NOT_AUTHORIZED"}

    def seal_prescore(self, remote) -> RemoteReceipt:
        manifest = self.manifest()
        raw = canonical(manifest)
        event = self._append("PRE_SCORE_LOCAL", {"manifest_sha256": sha256(raw).hexdigest(),
                   "eligible_for_future_score": manifest["eligible_for_future_score"]})
        path = self._path("receipts", "pre-score-manifest.json")
        _write_once(path, raw)
        if not callable(getattr(remote, "commit_and_verify", None)):
            raise CustodyBlocked("RUN_BLOCK: no GitHub remote publisher for pre-score")
        proof = remote.commit_and_verify(path, sha256(raw).hexdigest())
        self._remote_check(remote, proof, path)
        self._append("PRE_SCORE_REMOTE", {"manifest_sha256": sha256(raw).hexdigest(),
                    "local_event_sha256": event["entry_sha256"],
                    "receipt": proof.as_dict()})
        return proof

    def assert_prescore_remote(self, remote) -> dict:
        events = self.events()
        local = [x for x in events if x["kind"] == "PRE_SCORE_LOCAL"]
        verified = [x for x in events if x["kind"] == "PRE_SCORE_REMOTE"]
        if len(local) != 1 or len(verified) != 1:
            raise CustodyBlocked("RUN_BLOCK: pre-score remote commitment absent")
        path = self._path("receipts", "pre-score-manifest.json")
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != local[0]["data"]["manifest_sha256"]:
            raise CustodyBlocked("INVALID: prescore artifact overwritten")
        self._remote_check(remote, RemoteReceipt(**verified[0]["data"]["receipt"]), path)
        if verified[0]["data"]["manifest_sha256"] != sha256(raw).hexdigest():
            raise CustodyBlocked("INVALID: prescore receipt mismatch")
        # The published manifest must match the *actual* earlier journal
        # state, not a later reconstructed/altered event sequence.
        recreated = self.manifest()
        recreated["journal_tip_sha256"] = local[0]["prev_sha256"]
        if canonical(recreated) != raw:
            raise CustodyBlocked("INVALID: journal changed after pre-score lock")
        # A pre-score GitHub commit cannot stand in for the individual Q seals.
        for event in events:
            if event["kind"] == "Q_REMOTE":
                law = event["data"]["law_id"]
                receipt = RemoteReceipt(**event["data"]["receipt"])
                self._remote_check(remote, receipt,
                    self._path("public", "q-" + law + "-precommit.json"))
        return json.loads(raw)
