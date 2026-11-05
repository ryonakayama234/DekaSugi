"""R2-M-ENG immutable public-only Snapshot/v2; synthetic engineering, no scoring.

This is a local hash/creation guarantee, NOT independent custody or a trusted
timestamp. Loading always requires the out-of-band expected file SHA-256.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from .decoder import decode_public
from .records import (
    COMPILER_VERSION, FAMILY_VERSION, H0_ORDER, METHOD_VERSION, Node,
    PUBLIC_POINTS, PublicObservation, SchemaFrame, ast_dict, canonical,
    check_bit, check_sha, digest, public_evidence_digest,
    validate_public_history,
)
from .sleep_lite import sleep_lite
from .validator import VALIDATOR_VERSION, validate_public

SNAPSHOT_VERSION = "Snapshot/v2"
DISPATCH_VERSION = "r2-m-fixed-dispatch/1"
POLICY_VERSION = "r2-m-fixed-policy/1"
ROUTES = ("episodic_exact", "h0_consistent", "runtime_affine_decoder")
ROUTE_VERSIONS = {
    "episodic_exact": "r2-m-episodic/1",
    "h0_consistent": "r2-m-h0/1",
    "runtime_affine_decoder": "r2-m-affine-runtime/1",
}
LOOKUP_CAPACITY = 8
CLOSURE_MANIFEST = {
    "version": "R2-M-CLOSURE-v2.0", "status": "UNKNOWN",
    "closure_complete": False, "m_gap": "UNKNOWN",
    "unknown_reason": "H0_effective(B) and all legal routes not certified",
}
FIXED_POLICY = {
    "version": POLICY_VERSION, "dispatch_version": DISPATCH_VERSION,
    "route_order": list(ROUTES), "route_versions": ROUTE_VERSIONS,
    "h0_order": list(H0_ORDER), "lookup_capacity": LOOKUP_CAPACITY,
    "body_priority": True, "off_disables_only": "learned_body",
    "policy_learning": "NOT_EVALUATED",
}


@dataclass(frozen=True, slots=True)
class SnapshotRef:
    path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class LoadedSnapshot:
    reference: SnapshotRef
    history: tuple[PublicObservation, ...]
    journal: tuple[dict[str, object], ...]
    body: Node
    payload: dict[str, object]


def _absolute(path: str | Path) -> Path:
    raw = Path(path)
    if not raw.is_absolute():
        raise ValueError("INVALID: snapshot path must be absolute")
    resolved = raw.resolve()
    if str(raw) != str(resolved):
        raise ValueError("INVALID: noncanonical snapshot path")
    return resolved


def _public_history(data: object) -> tuple[PublicObservation, ...]:
    if type(data) is not list or len(data) != 4:
        raise ValueError("INVALID: snapshot public observations")
    keys = {"seq", "point", "answer", "paid", "legal_digest",
            "precommit", "received_at"}
    rows = []
    for item in data:
        if type(item) is not dict or set(item) != keys:
            raise ValueError("INVALID: observation fields")
        point = item["point"]
        if type(point) is not list or len(point) != 3:
            raise ValueError("INVALID: observation point")
        rows.append(PublicObservation(
            item["seq"], tuple(point), item["answer"], item["paid"],
            item["legal_digest"], item["precommit"], item["received_at"],
        ))
    return validate_public_history(tuple(rows), complete=True)


def _journal_checked(data: object, history: tuple[PublicObservation, ...],
                     expires_at: int) -> tuple[dict[str, object], ...]:
    """Verify public precommit precedes its public answer; no source import."""
    if type(expires_at) is not int or expires_at < 0:
        raise ValueError("INVALID: public query deadline")
    if type(data) not in (tuple, list) or len(data) != 5:
        raise ValueError("INVALID: public journal length")
    expected_legal = digest({
        "family": FAMILY_VERSION, "legal_actions": [[0, 0, 1]],
        "paid_budget_remaining": 1, "expires_at": expires_at,
    })
    keys = {"schema", "event", "seq", "point", "legal_actions",
            "legal_digest", "event_at", "answer", "paid_cost",
            "precommit", "prediction"}
    events: list[dict[str, object]] = []
    for i, step in enumerate(data):
        if type(step) is not dict or set(step) != keys or step["schema"] != "PublicStep/v2":
            raise ValueError("INVALID: public journal schema")
        expected_event = "initial" if i < 3 else ("precommit" if i == 3 else "answer")
        expected_seq = i if i < 3 else 3
        if (step["event"] != expected_event or type(step["seq"]) is not int
                or step["seq"] != expected_seq or
                step["point"] != list(PUBLIC_POINTS[expected_seq])):
            raise ValueError("INVALID: journal event order")
        if step["legal_actions"] != [[0, 0, 1]]:
            raise ValueError("INVALID: missing legal Q001")
        check_sha(step["legal_digest"])
        if (type(step["event_at"]) is not int or step["event_at"] < 0 or
                (events and step["event_at"] < events[-1]["event_at"])):
            raise ValueError("INVALID: journal time")
        if (step["legal_digest"] != history[expected_seq].legal_digest or
                step["legal_digest"] != expected_legal or
                step["event_at"] > expires_at):
            raise ValueError("INVALID: public journal legal digest/deadline")
        if i < 3:
            if (step["answer"] != history[i].answer or
                    step["event_at"] != history[i].received_at or
                    type(step["paid_cost"]) is not int or step["paid_cost"] != 0 or
                    step["precommit"] is not None or step["prediction"] is not None):
                raise ValueError("INVALID: initial receipt mismatch")
        elif i == 3:
            if (step["answer"] is not None or
                    type(step["paid_cost"]) is not int or step["paid_cost"] != 0 or
                    step["precommit"] != history[3].precommit):
                raise ValueError("INVALID: Q001 precommit")
            if step["prediction"] is not None:
                check_bit(step["prediction"])
        else:
            if (step["answer"] != history[3].answer or
                    type(step["paid_cost"]) is not int or step["paid_cost"] != 1 or
                    step["precommit"] != history[3].precommit or
                    step["prediction"] is not None or
                    step["event_at"] != history[3].received_at):
                raise ValueError("INVALID: Q001 answer mismatch")
        events.append(step)
    if (events[3]["event_at"] > events[4]["event_at"] or
            history[3].received_at < history[2].received_at):
        raise ValueError("INVALID: response before precommit")
    return tuple(events)


def _body_from_dict(data: object) -> Node:
    """Bound reconstruction; no eval, callbacks, extra fields or shared DAG."""
    remaining = [32]

    def walk(item: object) -> Node:
        remaining[0] -= 1
        if remaining[0] < 0 or type(item) is not dict or set(item) != {"type", "op", "args"}:
            raise ValueError("INVALID: malformed snapshot AST")
        if (item["type"] != "Bool" or type(item["op"]) is not str or
                type(item["args"]) is not list):
            raise ValueError("INVALID: AST type")
        return Node(item["op"], tuple(walk(child) for child in item["args"]), "Bool")

    node = walk(data)
    from .validator import check_ast
    check_ast(node)
    return node


def _check_body(body: Node, history: tuple[PublicObservation, ...]) -> dict[str, object]:
    validated = validate_public(body, history)
    if not validated.passed:
        raise ValueError("VALIDATION_FAILED: body does not match public 4")
    result = decode_public(history)
    if result.body is None or result.candidates_generated != 1:
        raise ValueError("UNIDENTIFIABLE: missing Q001")
    normalized, sleep_receipt = sleep_lite(result.body, history)
    allowed = (canonical(ast_dict(result.body)), canonical(ast_dict(normalized)))
    if canonical(ast_dict(body)) not in allowed:
        raise ValueError("INVALID: body not from specified decoder/Sleep-lite")
    return {
        "status": validated.status, "public_digest": validated.public_digest,
        "ast_digest": validated.ast_digest, "ast_nodes_static": validated.ast_nodes_static,
        "validator_version": VALIDATOR_VERSION,
        "decoder_invocations_at_creation": result.decoder_invocations,
        "candidates_generated_at_creation": result.candidates_generated,
        "candidate_budget": result.candidate_budget, "family_size": result.family_size,
        "sleep_lite_receipt": asdict(sleep_receipt),
        "sleep_lite_receipt_digest": digest(asdict(sleep_receipt)),
    }


def _make_payload(history: tuple[PublicObservation, ...],
                  journal: tuple[dict[str, object], ...], body: Node,
                  parent_digest: str | None, expires_at: int) -> dict[str, object]:
    if parent_digest is not None:
        check_sha(parent_digest)
    public_digest = public_evidence_digest(history)
    receipt = _check_body(body, history)
    payload: dict[str, object] = {
        "method_version": METHOD_VERSION, "family_version": FAMILY_VERSION,
        "compiler_version": COMPILER_VERSION, "closure_status": "UNKNOWN",
        "closure": CLOSURE_MANIFEST, "closure_digest": digest(CLOSURE_MANIFEST),
        "policy": FIXED_POLICY, "policy_digest": digest(FIXED_POLICY),
        "route_manifest_digest": digest(ROUTE_VERSIONS),
        "parent_digest": parent_digest, "expires_at": expires_at,
        "public_observations": [r.as_dict() for r in history],
        "public_digest": public_digest, "public_journal": list(journal),
        "public_journal_digest": digest(list(journal)),
        "body": ast_dict(body), "body_digest": digest(ast_dict(body)),
        "validator_receipt": receipt, "validator_receipt_digest": digest(receipt),
        "arm_manifest": {"F00": "BODY_OFF_FIXED", "F10": "BODY_ON_FIXED",
                         "F01": "NOT_EVALUATED", "F11": "NOT_EVALUATED",
                         },
    }
    SchemaFrame(SNAPSHOT_VERSION, "public", payload).public_dict()
    return payload


def write_snapshot(path: str | Path, history: tuple[PublicObservation, ...],
                   journal: tuple[dict[str, object], ...], body: Node, *,
                   expires_at: int, parent_digest: str | None = None) -> SnapshotRef:
    """Create once; payload contains public evidence ONLY."""
    dest = Path(path).resolve()  # Capture absolute path at creation, not at child cwd.
    validate_public_history(history, complete=True)
    checked = _journal_checked(journal, history, expires_at)
    payload = _make_payload(history, checked, body, parent_digest, expires_at)
    envelope = {"schema": SNAPSHOT_VERSION, "role": "public",
                "payload": payload, "payload_digest": digest(payload)}
    data = (canonical(envelope) + "\n").encode("utf-8")
    try:
        fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o444)
    except OSError as exc:
        raise ValueError("INVALID: snapshot exclusive creation failed") from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise
    reference = SnapshotRef(str(dest), sha256(data).hexdigest(), len(data))
    # Fail closed if written content cannot be restored as specified.
    load_snapshot(reference.path, expected_sha256=reference.sha256)
    return reference


def load_snapshot(path: str | Path, *, expected_sha256: str) -> LoadedSnapshot:
    """Mandatory external digest; reject altered bytes and schema on every fresh load."""
    check_sha(expected_sha256)
    src = _absolute(path)
    if src.is_symlink() or not src.is_file():
        raise ValueError("INVALID: snapshot is not a regular file")
    raw = src.read_bytes()
    if sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("INVALID: snapshot SHA mismatch")
    try:
        envelope = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ValueError("INVALID: snapshot JSON") from exc
    if raw != (canonical(envelope) + "\n").encode("utf-8"):
        raise ValueError("INVALID: snapshot canonical bytes")
    if (type(envelope) is not dict or set(envelope) !=
            {"schema", "role", "payload", "payload_digest"} or
            envelope["schema"] != SNAPSHOT_VERSION or envelope["role"] != "public"):
        raise ValueError("INVALID: snapshot schema")
    payload = envelope["payload"]
    if type(payload) is not dict or digest(payload) != envelope["payload_digest"]:
        raise ValueError("INVALID: snapshot payload hash")
    SchemaFrame(SNAPSHOT_VERSION, "public", payload).public_dict()
    history = _public_history(payload.get("public_observations"))
    journal = _journal_checked(payload.get("public_journal"), history,
                               payload.get("expires_at"))
    body = _body_from_dict(payload.get("body"))
    recalculated = _make_payload(history, journal, body,
                                 payload.get("parent_digest"), payload["expires_at"])
    if payload != recalculated:
        raise ValueError("INVALID: snapshot public or manifest mismatch")
    return LoadedSnapshot(SnapshotRef(str(src), expected_sha256, len(raw)),
                          history, journal, body, payload)
