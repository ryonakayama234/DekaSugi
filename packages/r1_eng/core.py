"""R1-ENG/2BIT: isolated, public-only typed-body engineering diagnostic.

OFF retains *all* same-Snapshot nonlearned paths implemented here: episodic
lookup and the six H0 predicates. STATIC-H+ / fixed macro are separate arms,
never silently substituted into this intervention. No scientific scoring.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

GRAMMAR = "r1-eng-bool-ast/1"
POLICY = "r1-eng-fixed-query-and-lookup-first/1"
H0_ORDER = ("0", "1", "!x", "!z", "z", "x")
DOMAIN = ((0, 0), (0, 1), (1, 0), (1, 1))
MAX_AST_NODES = 9
MAX_CANDIDATES = 10000
PARENT = "r1-eng-empty-library/1"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def check_point(point: object) -> tuple[int, int]:
    if (type(point) is not tuple or len(point) != 2 or
        any(type(bit) is not int or bit not in (0, 1) for bit in point)):
        raise ValueError("input must be an exact 2-bit tuple")
    return point


@dataclass(frozen=True, slots=True)
class Observation:
    seq: int
    point: tuple[int, int]
    answer: int
    paid: int
    legal_digest: str
    precommit: str | None

    def as_dict(self) -> dict[str, object]:
        return {"seq": self.seq, "point": list(self.point),
                "answer": self.answer, "paid": self.paid,
                "legal_digest": self.legal_digest, "precommit": self.precommit}


def check_history(history: tuple[Observation, ...]) -> None:
    if type(history) is not tuple:
        raise ValueError("invalid history container")
    seen = set()
    for index, item in enumerate(history):
        if (type(item) is not Observation or type(item.seq) is not int or
            item.seq != index or check_point(item.point) in seen or
            type(item.answer) is not int or item.answer not in (0, 1) or
            type(item.paid) is not int or item.paid not in (0, 1) or
            type(item.legal_digest) is not str or len(item.legal_digest) != 64):
            raise ValueError("invalid public observation")
        if item.paid == 1 and (type(item.precommit) is not str or
                               len(item.precommit) != 64):
            raise ValueError("paid query must be precommitted")
        if item.paid == 0 and item.precommit is not None:
            raise ValueError("initial evidence must not claim a query commit")
        seen.add(item.point)


@dataclass(frozen=True, slots=True)
class Node:
    op: str
    children: tuple["Node", ...] = ()
    dtype: str = "Bool"


def ast_dict(node: Node) -> dict[str, object]:
    if type(node) is not Node:
        raise ValueError("untrusted AST node")
    return {"type": node.dtype, "op": node.op,
            "args": [ast_dict(child) for child in node.children]}


def parse_ast(data: object) -> Node:
    if type(data) is not dict or set(data) != {"type", "op", "args"}:
        raise ValueError("invalid typed AST serialization")
    if type(data["args"]) is not list:
        raise ValueError("invalid AST operands")
    return Node(data["op"], tuple(parse_ast(v) for v in data["args"]), data["type"])


def ast_size(node: Node) -> int:
    return 1 + sum(ast_size(child) for child in node.children)


def canonicalize(node: Node) -> Node:
    """Sleep-lite: ordering of commutative arguments only; NO candidate selection."""
    from .validator import check_ast
    check_ast(node)
    children = tuple(canonicalize(child) for child in node.children)
    if node.op in ("AND", "OR"):
        children = tuple(sorted(children, key=lambda n: canonical(ast_dict(n))))
    return Node(node.op, children)


def h0_predict(name: str, point: tuple[int, int]) -> int:
    x, z = check_point(point)
    if name == "0":
        return 0
    if name == "1":
        return 1
    if name == "!x":
        return 1 - x
    if name == "!z":
        return 1 - z
    if name == "z":
        return z
    if name == "x":
        return x
    raise ValueError("unregistered H0 predicate")


@dataclass(frozen=True, slots=True)
class H0Scan:
    tested: tuple[str, ...]
    consistent: tuple[str, ...]
    complete: bool
    status: str


def scan_h0(history: tuple[Observation, ...], limit: int = 6) -> H0Scan:
    check_history(history)
    if type(limit) is not int or not 1 <= limit <= len(H0_ORDER):
        raise ValueError("invalid H0 search budget")
    tested = H0_ORDER[:limit]
    consistent = tuple(name for name in tested
                       if all(h0_predict(name, o.point) == o.answer for o in history))
    complete = limit == len(H0_ORDER)
    status = ("SEARCH_INCOMPLETE" if not complete else
              "SUFFICIENT_H0" if consistent else "MISMATCH_CANDIDATE")
    return H0Scan(tested, consistent, complete, status)


def _synth_eval(node: Node, point: tuple[int, int]) -> int:
    """Synthesizer's private interpreter; acceptance uses a different implementation."""
    if node.op == "x":
        return point[0]
    if node.op == "z":
        return point[1]
    if node.op == "NOT":
        return 1 - _synth_eval(node.children[0], point)
    a, b = (_synth_eval(child, point) for child in node.children)
    return (a & b) if node.op == "AND" else (a | b)


@dataclass(frozen=True, slots=True)
class Synthesis:
    candidate: Node | None
    considered: int
    status: str


def synthesize_public(history: tuple[Observation, ...]) -> Synthesis:
    """Bottom-up typed enumeration from public pairs ONLY. No law, IDs or targets."""
    check_history(history)
    if not history:
        return Synthesis(None, 0, "NO_PUBLIC_EVIDENCE")
    target = tuple(o.answer for o in history)
    by_size: dict[int, list[Node]] = {}
    seen_signatures: set[tuple[int, ...]] = set()
    considered = 0
    for size in range(1, MAX_AST_NODES + 1):
        pool: dict[str, Node] = {}
        if size == 1:
            for op in ("x", "z"):
                node = Node(op)
                pool[canonical(ast_dict(node))] = node
        else:
            for child in by_size.get(size - 1, ()):
                node = Node("NOT", (child,))
                pool[canonical(ast_dict(node))] = node
            for left_size in range(1, size - 1):
                right_size = size - left_size - 1
                for left in by_size.get(left_size, ()):
                    for right in by_size.get(right_size, ()):
                        for op in ("AND", "OR"):
                            node = canonicalize(Node(op, (left, right)))
                            pool[canonical(ast_dict(node))] = node
        selected: list[Node] = []
        matches: list[Node] = []
        for key in sorted(pool):
            considered += 1
            if considered > MAX_CANDIDATES:
                return Synthesis(None, considered - 1, "BUDGET_EXHAUSTED")
            node = pool[key]
            signature = tuple(_synth_eval(node, o.point) for o in history)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                selected.append(node)
                if signature == target:
                    matches.append(node)
        by_size[size] = selected
        if matches:
            return Synthesis(min(matches, key=lambda n: canonical(ast_dict(n))),
                             considered, "PUBLIC_MATCH")
    return Synthesis(None, considered, "NOT_FOUND")


@dataclass(frozen=True, slots=True)
class Snapshot:
    observations: tuple[Observation, ...]
    body: Node | None
    body_digest: str | None
    validator_receipt: str | None
    policy: str = POLICY
    grammar: str = GRAMMAR
    parent: str = PARENT
    schema: str = "Snapshot/v1"

    def payload(self) -> dict[str, object]:
        return {"schema": self.schema, "observations": [o.as_dict() for o in self.observations],
                "body": ast_dict(self.body) if self.body is not None else None,
                "body_digest": self.body_digest,
                "validator_receipt": self.validator_receipt, "policy": self.policy,
                "grammar": self.grammar, "parent": self.parent,
                "registry_digest": digest({"grammar": GRAMMAR, "H0": H0_ORDER}),
                "policy_digest": digest({"policy": POLICY})}

    def as_dict(self) -> dict[str, object]:
        payload = self.payload()
        return {"payload": payload, "sha256": digest(payload)}


def make_snapshot(history: tuple[Observation, ...], body: Node | None) -> Snapshot:
    from .validator import validate_public
    check_history(history)
    if body is None:
        return Snapshot(history, None, None, None)
    cleaned = canonicalize(body)
    if any(_synth_eval(body, p) != _synth_eval(cleaned, p) for p in DOMAIN):
        raise ValueError("Sleep-lite changed semantics")
    receipt = validate_public(cleaned, history)
    if not receipt["passed"]:
        raise ValueError("independent validator rejected candidate")
    return Snapshot(history, cleaned, digest(ast_dict(cleaned)), digest(receipt))


def save_snapshot(path: Path, snapshot: Snapshot) -> None:
    check_snapshot(snapshot)
    path = Path(path)
    # Exclusive create: never modify/rewrite a published snapshot in place.
    with path.open("x", encoding="utf-8") as stream:
        stream.write(canonical(snapshot.as_dict()) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def check_snapshot(snapshot: Snapshot) -> None:
    from .validator import validate_public
    if type(snapshot) is not Snapshot or (snapshot.schema, snapshot.grammar,
             snapshot.policy, snapshot.parent) != ("Snapshot/v1", GRAMMAR, POLICY, PARENT):
        raise ValueError("unknown Snapshot contract")
    check_history(snapshot.observations)
    if snapshot.body is None:
        if snapshot.body_digest is not None or snapshot.validator_receipt is not None:
            raise ValueError("orphaned body metadata")
    else:
        if canonicalize(snapshot.body) != snapshot.body:
            raise ValueError("noncanonical stored body")
        receipt = validate_public(snapshot.body, snapshot.observations)
        if (not receipt["passed"] or snapshot.body_digest != digest(ast_dict(snapshot.body)) or
                snapshot.validator_receipt != digest(receipt)):
            raise ValueError("invalid stored body or validator receipt")


def load_snapshot(path: Path) -> Snapshot:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if type(raw) is not dict or set(raw) != {"payload", "sha256"}:
        raise ValueError("invalid Snapshot envelope")
    p = raw["payload"]
    required = {"schema", "observations", "body", "body_digest", "validator_receipt",
                "policy", "grammar", "parent", "registry_digest", "policy_digest"}
    if type(p) is not dict or set(p) != required or raw["sha256"] != digest(p):
        raise ValueError("Snapshot tampered or contains prohibited fields")
    if (p["registry_digest"] != digest({"grammar": GRAMMAR, "H0": H0_ORDER}) or
            p["policy_digest"] != digest({"policy": POLICY})):
        raise ValueError("policy or registry drift")
    observations = []
    for r in p["observations"]:
        if type(r) is not dict or set(r) != {"seq", "point", "answer", "paid",
                                           "legal_digest", "precommit"}:
            raise ValueError("invalid public record")
        observations.append(Observation(r["seq"], tuple(r["point"]), r["answer"],
                                        r["paid"], r["legal_digest"], r["precommit"]))
    body = parse_ast(p["body"]) if p["body"] is not None else None
    result = Snapshot(tuple(observations), body, p["body_digest"], p["validator_receipt"],
                      p["policy"], p["grammar"], p["parent"], p["schema"])
    check_snapshot(result)
    return result


def dispatch(snapshot: Snapshot, point: tuple[int, int], *, body_on: bool) -> dict[str, Any]:
    """Same Snapshot/policy. Activity flags refer to the learned body ONLY.

    The separate fallback flags show that OFF truly executes a surviving
    nonlearned path; "body available" does NOT mean selected or executed.
    """
    from .validator import evaluate_independent
    check_snapshot(snapshot)
    check_point(point)
    if type(body_on) is not bool:
        raise ValueError("intervention flag must be boolean")
    available = snapshot.body is not None
    base = {"condition": "ON" if body_on else "OFF", "available": available,
            "selected": False, "executed": False, "finished": False,
            "fallback_selected": False, "fallback_executed": False,
            "fallback_finished": False}
    if body_on and available:
        return {**base, "action": "PREDICT",
                "prediction": evaluate_independent(snapshot.body, point),
                "route": "learned_body", "selected": True,
                "executed": True, "finished": True,
                "body_ast_nodes_executed": ast_size(snapshot.body),
                "episodic_reads": 0}
    for obs in snapshot.observations:
        if obs.point == point:
            return {**base, "action": "PREDICT", "prediction": obs.answer,
                    "route": "episodic_lookup", "fallback_selected": True,
                    "fallback_executed": True, "fallback_finished": True,
                    "body_ast_nodes_executed": 0, "episodic_reads": 1}
    choices = tuple(name for name in H0_ORDER
                    if all(h0_predict(name, item.point) == item.answer
                           for item in snapshot.observations))
    if choices:
        return {**base, "action": "PREDICT", "prediction": h0_predict(choices[0], point),
                "route": "h0:" + choices[0], "fallback_selected": True,
                "fallback_executed": True, "fallback_finished": True,
                "body_ast_nodes_executed": 0, "episodic_reads": 0}
    return {**base, "action": "ABSTAIN", "prediction": None,
            "route": "no_legal_fallback", "body_ast_nodes_executed": 0,
            "episodic_reads": 0}
