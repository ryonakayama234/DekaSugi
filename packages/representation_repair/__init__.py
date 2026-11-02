"""EXP-REP-005 G2 synthetic mechanism: learn a public-history state refinement.

This learner sees ONLY public typed episodes. It never imports a world Law,
source family, hidden evaluator, historical scorer or sealed dataset.
Meta-grammar: one equality predicate on public action at lag 1 or 2.
Synthetic engineering demonstration ONLY; not scientific learning/transfer.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

SCHEMA = "rep005-public-repair/1"
ActionKey = tuple[str, int, int]
LEGAL_ACTIONS: tuple[ActionKey, ...] = (
    tuple(("set", i, v) for i in range(4) for v in (0, 1))
    + tuple(("pulse", i, -1) for i in range(4))
)
MAX_EPISODES = 64
MAX_STEPS = 8
MAX_RECORDS = 512
MAX_SNAPSHOT_BYTES = 100_000


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _action(value: object) -> bool:
    return type(value) is tuple and len(value) == 3 and all(
        type(x) is (str if i == 0 else int) for i, x in enumerate(value)
    ) and value in LEGAL_ACTIONS


def _state(value: object) -> bool:
    return type(value) is int and 0 <= value < 16


@dataclass(frozen=True, slots=True)
class PublicStep:
    before: int
    history: tuple[ActionKey, ...]
    action: ActionKey
    after: int
    paid_cost: int = 1

    def __post_init__(self) -> None:
        if (not _state(self.before) or not _state(self.after)
            or type(self.history) is not tuple or len(self.history) > 2
            or not all(_action(x) for x in self.history)
            or not _action(self.action)
            or type(self.paid_cost) is not int or self.paid_cost != 1):
            raise ValueError("invalid charged public observation")


@dataclass(frozen=True, slots=True)
class Feature:
    lag: int
    action: ActionKey

    def __post_init__(self) -> None:
        if type(self.lag) is not int or self.lag not in (1, 2) or not _action(self.action):
            raise ValueError("invalid typed feature")

    def evaluate(self, history: tuple[ActionKey, ...]) -> bool:
        if type(history) is not tuple or len(history) > 2 or not all(
            _action(x) for x in history
        ):
            raise ValueError("invalid public history")
        return len(history) >= self.lag and history[-self.lag] == self.action


@dataclass(frozen=True, slots=True)
class LoadedSnapshot:
    feature: Feature
    # (public state, current action, feature value, observed successor)
    table: tuple[tuple[int, ActionKey, bool, int], ...]
    evidence_sha256: str
    witness_count: int
    candidate_count: int
    paid_actions: int

    def predict(self, before: int, history: tuple[ActionKey, ...],
                action: ActionKey) -> int | None:
        if not _state(before) or not _action(action):
            raise ValueError("invalid public prediction request")
        branch = self.feature.evaluate(history)  # executable ConceptBody dispatch
        for state, stored_action, flag, after in self.table:
            if (state, stored_action, flag) == (before, action, branch):
                return after
        return None  # unseen context; no fabricated prediction


def _validated_records(episodes: tuple[tuple[PublicStep, ...], ...]):
    if (type(episodes) is not tuple or not 1 <= len(episodes) <= MAX_EPISODES):
        raise ValueError("invalid public episode corpus")
    records = []
    receipt = []
    for episode in episodes:
        if type(episode) is not tuple or not 1 <= len(episode) <= MAX_STEPS:
            raise ValueError("episode length outside public bounds")
        before, history = 0, ()
        emitted = []
        for step in episode:
            if (type(step) is not PublicStep or step.before != before
                or step.history != history):
                raise ValueError("forged or nonchronological public episode")
            records.append(step)
            emitted.append([step.before, [list(a) for a in step.history],
                            list(step.action), step.after, step.paid_cost])
            before, history = step.after, (history + (step.action,))[-2:]
        receipt.append(emitted)
    if len(records) > MAX_RECORDS:
        raise ValueError("corpus exceeds bounded proof/experience scope")
    return records, sha256(_canonical(receipt).encode()).hexdigest()


def visible_state_predictions(episodes: tuple[tuple[PublicStep, ...], ...]) -> dict:
    """Memoryless deterministic baseline; ambiguous keys are explicit abstentions."""
    records, _ = _validated_records(episodes)
    buckets: dict[tuple[int, ActionKey], set[int]] = {}
    for s in records:
        buckets.setdefault((s.before, s.action), set()).add(s.after)
    return {key: next(iter(v)) if len(v) == 1 else None for key, v in buckets.items()}


def learn(episodes: tuple[tuple[PublicStep, ...], ...]) -> dict:
    """Public counterexample -> typed feature search -> candidate Snapshot.

    The caller asserts one stationary deterministic world across all episodes.
    This premise cannot be authenticated from public examples alone.
    """
    records, evidence_sha = _validated_records(episodes)
    buckets: dict[tuple[int, ActionKey], list[PublicStep]] = {}
    for s in records:
        buckets.setdefault((s.before, s.action), []).append(s)
    contradictions = []
    for key, group in buckets.items():
        for first in group:
            other = next((s for s in group if s.after != first.after), None)
            if other is not None:
                contradictions.append((first, other))
                break
    result = {"schema": SCHEMA, "paid_actions": len(records),
              "evidence_sha256": evidence_sha,
              "witness_count": len(contradictions)}
    if not contradictions:
        return {**result, "status": "NO_REPAIR_NEEDED",
                "reason": "NO_OBSERVED_VISIBLE_STATE_CONTRADICTION"}
    valid = []
    for lag in (1, 2):
        for action in LEGAL_ACTIONS:
            feature = Feature(lag, action)
            pred: dict[tuple[int, ActionKey, bool], int] = {}
            consistent = True
            for s in records:
                key = (s.before, s.action, feature.evaluate(s.history))
                if key in pred and pred[key] != s.after:
                    consistent = False
                    break
                pred[key] = s.after
            if consistent:
                valid.append((feature, pred))
    if not valid:
        return {**result, "status": "NOT_CERTIFIED",
                "reason": "NO_SINGLE_HISTORY_EQUALITY_FEATURE_FITS"}
    chosen, pred = valid[0]  # shortest lag, then deterministic public action ordering
    table = tuple(sorted(
        ((state, action, flag, next_state)
         for (state, action, flag), next_state in pred.items()),
        key=lambda row: (row[0], row[1], row[2])
    ))
    payload = {"schema": SCHEMA, "feature": {"lag": chosen.lag,
                "action": list(chosen.action)},
               "table": [[s, list(a), flag, nxt] for s, a, flag, nxt in table],
               "evidence_sha256": evidence_sha, "witness_count": len(contradictions),
               "candidate_count": len(valid), "paid_actions": len(records)}
    envelope = {"payload": payload,
                "sha256": sha256(_canonical(payload).encode()).hexdigest()}
    snapshot = _canonical(envelope) + "\n"
    if len(snapshot.encode()) > MAX_SNAPSHOT_BYTES:
        return {**result, "status": "NOT_CERTIFIED", "reason": "SNAPSHOT_CAP"}
    # Validate the serialized artifact with the same verifier used by fresh USE.
    load_snapshot(snapshot)
    first, second = contradictions[0]
    witness = {"state": first.before, "action": first.action,
               "public_history_a": first.history, "successor_a": first.after,
               "public_history_b": second.history, "successor_b": second.after}
    return {**result, "status": "LEARNED_CANDIDATE",
            "typed_body": {"lag": chosen.lag, "action": chosen.action},
            "candidate_count": len(valid), "witness": witness,
            "snapshot": snapshot}


def load_snapshot(raw: str) -> LoadedSnapshot:
    """Strict canonical, digest-bound, executable data ONLY; never eval/exec."""
    if type(raw) is not str or len(raw.encode()) > MAX_SNAPSHOT_BYTES:
        raise ValueError("invalid snapshot container")
    try:
        envelope = json.loads(raw)
        if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
            raise ValueError("invalid snapshot envelope")
        if raw != _canonical(envelope) + "\n":
            raise ValueError("noncanonical snapshot bytes")
        payload = envelope["payload"]
        if type(payload) is not dict or set(payload) != {
            "schema", "feature", "table", "evidence_sha256",
            "witness_count", "candidate_count", "paid_actions"
        } or payload["schema"] != SCHEMA:
            raise ValueError("untrusted snapshot schema")
        actual = sha256(_canonical(payload).encode()).hexdigest()
        if type(envelope["sha256"]) is not str or actual != envelope["sha256"]:
            raise ValueError("snapshot digest mismatch")
        f = payload["feature"]
        if type(f) is not dict or set(f) != {"lag", "action"}:
            raise ValueError("invalid feature body")
        if type(f["action"]) is not list or len(f["action"]) != 3:
            raise ValueError("invalid serialized action")
        feature = Feature(f["lag"], tuple(f["action"]))
        rows = payload["table"]
        if type(rows) is not list or not rows or len(rows) > MAX_RECORDS:
            raise ValueError("invalid prediction table")
        table = []
        for row in rows:
            if type(row) is not list or len(row) != 4 or type(row[1]) is not list:
                raise ValueError("invalid row")
            s, a, flag, nxt = row
            action = tuple(a)
            if not _state(s) or not _action(action) or type(flag) is not bool or not _state(nxt):
                raise ValueError("invalid typed row")
            table.append((s, action, flag, nxt))
        if table != sorted(set(table), key=lambda x: (x[0], x[1], x[2])):
            raise ValueError("noncanonical/duplicate table")
        if len({(s, a, flag) for s, a, flag, _ in table}) != len(table):
            raise ValueError("contradictory table")
        digest = payload["evidence_sha256"]
        if type(digest) is not str or len(digest) != 64 or any(
            c not in "0123456789abcdef" for c in digest
        ):
            raise ValueError("invalid evidence commitment")
        for field in ("witness_count", "candidate_count", "paid_actions"):
            value = payload[field]
            if type(value) is not int or value < 1 or value > MAX_RECORDS:
                raise ValueError("invalid provenance counter")
        return LoadedSnapshot(feature, tuple(table), digest,
                              payload["witness_count"], payload["candidate_count"],
                              payload["paid_actions"])
    except (TypeError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise ValueError("invalid/untrusted snapshot") from exc
