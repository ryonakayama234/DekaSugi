"""Immutable editor data, canonical finite conditions and cooperative accounting."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, fields, is_dataclass
from hashlib import sha256
from itertools import combinations
import json
import math
import sys
import time

SYMBOLS = ("A", "B", "C", "D")
READS = ("cursor", "first", "last", "prev")
SCHEMA = "sentence-candidates/1"
GRAMMAR = "sentence-condition/1"
COUNTERS = ("candidate_enumerations", "candidate_checks",
            "condition_evaluations", "atomic_transitions", "submissions")


class Fault(ValueError):
    """Invalid typed data; no repair or arbitrary execution."""


class BudgetExceeded(RuntimeError):
    """A terminal resource stop, distinct from no consistent hypothesis."""


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def _symbols(value: object) -> bool:
    return (type(value) is tuple and len(value) <= 16
            and all(type(x) is str and x in SYMBOLS for x in value))


@dataclass(frozen=True, slots=True)
class State:
    buffer: tuple[str, ...]
    cursor: int
    selection: tuple[int, int] | None = None
    clipboard: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (not _symbols(self.buffer) or not _symbols(self.clipboard)
                or type(self.cursor) is not int
                or not 0 <= self.cursor <= len(self.buffer)):
            raise Fault("invalid state")
        if self.selection is not None:
            if (type(self.selection) is not tuple or len(self.selection) != 2
                    or any(type(x) is not int or not 0 <= x <= len(self.buffer)
                           for x in self.selection)
                    or self.selection[1] != self.cursor):
                raise Fault("invalid selection/head")

    def record(self) -> dict:
        _state(self)
        return {"buffer": list(self.buffer), "cursor": self.cursor,
                "selection": None if self.selection is None else list(self.selection),
                "clipboard": list(self.clipboard)}

    @classmethod
    def parse(cls, value: dict) -> State:
        if (type(value) is not dict
                or set(value) != {"buffer", "cursor", "selection", "clipboard"}
                or type(value["buffer"]) is not list
                or type(value["clipboard"]) is not list):
            raise Fault("state JSON shape")
        sel = value["selection"]
        if sel is not None and (type(sel) is not list or len(sel) != 2):
            raise Fault("selection JSON shape")
        return cls(tuple(value["buffer"]), value["cursor"],
                   None if sel is None else tuple(sel), tuple(value["clipboard"]))


def _state(state: State) -> None:
    if type(state) is not State:
        raise Fault("exact State required")
    State.__post_init__(state)


def validate_input(state: State) -> None:
    _state(state)
    if (not 4 <= len(state.buffer) <= 8 or not 0 < state.cursor < len(state.buffer)
            or state.selection is not None or state.clipboard):
        raise Fault("outside sentence trial input domain")


def delete_right(state: State, meter: Meter | None = None) -> State:
    _state(state)
    if state.selection is not None:
        raise Fault("selection deletion not in this subset")
    if meter is not None:
        meter.tick("atomic_transitions")
        meter.tick("submissions")
    i = state.cursor
    return State(state.buffer[:i] + state.buffer[i + 1:], i, None, state.clipboard)


def keep(state: State, meter: Meter | None = None) -> State:
    _state(state)
    if meter is not None:
        meter.tick("submissions")
    return state


def _atom(atom: tuple) -> None:
    if (type(atom) is not tuple or len(atom) != 3
            or any(type(x) is not str for x in atom)
            or atom[0] not in ("EQ", "NE")
            or atom[1] not in READS or atom[2] not in READS
            or not atom[1] < atom[2]):
        raise Fault("noncanonical atom")


@dataclass(frozen=True, slots=True)
class Condition:
    atoms: tuple[tuple[str, str, str], ...]

    def __post_init__(self) -> None:
        if type(self.atoms) is not tuple or len(self.atoms) not in (1, 2):
            raise Fault("condition arity/type")
        for atom in self.atoms:
            _atom(atom)
        if len(self.atoms) == 2 and not canonical(self.atoms[0]) < canonical(self.atoms[1]):
            raise Fault("duplicate/reversed AND")

    def ast(self) -> list:
        if type(self) is not Condition:
            raise Fault("exact Condition required")
        Condition.__post_init__(self)
        return list(self.atoms[0]) if len(self.atoms) == 1 else ["AND", *map(list, self.atoms)]

    @classmethod
    def parse(cls, value: list) -> Condition:
        if type(value) is not list or len(value) != 3 or type(value[0]) is not str:
            raise Fault("condition JSON shape")
        if value[0] == "AND":
            if any(type(x) is not list for x in value[1:]):
                raise Fault("AND children")
            return cls(tuple(tuple(x) for x in value[1:]))
        return cls((tuple(value),))

    def evaluate(self, state: State, meter: Meter | None = None) -> bool:
        self.ast()  # strict type/canonical validation before any evaluation
        validate_input(state)
        indices = {"cursor": state.cursor, "prev": state.cursor - 1,
                   "first": 0, "last": len(state.buffer) - 1}
        answer = True
        for op, left, right in self.atoms:
            if meter is not None:
                meter.tick("condition_evaluations")
            same = state.buffer[indices[left]] == state.buffer[indices[right]]
            result = same if op == "EQ" else not same
            answer = answer and result
        return answer

    def explain(self) -> str:
        self.ast()
        names = {"cursor": "カーソル右", "prev": "直前", "first": "先頭", "last": "末尾"}
        return " かつ ".join(f"{names[a]}と{names[b]}が{'同じ' if op == 'EQ' else '異なる'}"
                            for op, a, b in self.atoms)


def catalog(meter: Meter | None = None) -> tuple[Condition, ...]:
    atoms = tuple(sorted(((op, a, b) for op in ("EQ", "NE")
                          for a, b in combinations(READS, 2)), key=canonical))
    def emit(terms):
        if meter is not None:
            meter.tick("candidate_enumerations")
        return Condition(terms)
    singles = tuple(emit((a,)) for a in atoms)
    doubles = tuple(sorted((emit(pair) for pair in combinations(atoms, 2)),
                           key=lambda x: canonical(x.ast())))
    return singles + doubles


def grammar_digest(meter: Meter | None = None) -> str:
    return sha256(canonical({"schema": GRAMMAR,
                             "conditions": [c.ast() for c in catalog(meter)]})).hexdigest()


def execute(condition: Condition, state: State, meter: Meter | None = None) -> State:
    if type(condition) is not Condition:
        raise Fault("exact Condition required")
    return delete_right(state, meter) if condition.evaluate(state, meter) else keep(state, meter)


@dataclass(frozen=True, slots=True)
class Snapshot:
    candidate_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.candidate_ids) is not tuple:
            raise Fault("candidate ID tuple required")
        known = tuple(f"cond-{i:03d}" for i in range(78))
        if (any(type(x) is not str or x not in known for x in self.candidate_ids)
                or tuple(sorted(set(self.candidate_ids))) != self.candidate_ids):
            raise Fault("invalid candidate IDs/order")

    @property
    def selected_id(self) -> str | None:
        Snapshot.__post_init__(self)
        return self.candidate_ids[0] if self.candidate_ids else None

    def encode(self, meter: Meter | None = None) -> bytes:
        if type(self) is not Snapshot:
            raise Fault("exact Snapshot required")
        data = canonical({"schema": SCHEMA, "grammar_sha256": grammar_digest(meter),
                          "candidate_ids": list(self.candidate_ids),
                          "selected_id": self.selected_id})
        if meter is not None:
            meter.checkpoint((self, data))
        return data

    @classmethod
    def decode(cls, data: bytes, meter: Meter | None = None) -> Snapshot:
        if type(data) is not bytes or len(data) > 1048576:
            raise Fault("snapshot bytes/size")
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise Fault("duplicate JSON key")
                result[key] = value
            return result
        try:
            value = json.loads(data, object_pairs_hook=unique)
        except (ValueError, UnicodeError) as exc:
            raise Fault("snapshot JSON") from exc
        if (type(value) is not dict
                or set(value) != {"schema", "grammar_sha256", "candidate_ids", "selected_id"}
                or value["schema"] != SCHEMA or value["grammar_sha256"] != grammar_digest(meter)
                or type(value["candidate_ids"]) is not list):
            raise Fault("snapshot schema/grammar")
        result = cls(tuple(value["candidate_ids"]))
        if value["selected_id"] != result.selected_id or data != result.encode(meter):
            raise Fault("snapshot selection/noncanonical bytes")
        return result


def retained_size(value: object) -> int:
    """Deep size of supported case data, counting shared objects once; not RSS."""
    seen = set()
    def visit(obj):
        if id(obj) in seen:
            return 0
        seen.add(id(obj))
        size = sys.getsizeof(obj)
        if type(obj) in (str, bytes, int, bool, float, type(None)):
            return size
        if type(obj) in (tuple, list):
            return size + sum(visit(x) for x in obj)
        if type(obj) is dict:
            return size + sum(visit(k) + visit(v) for k, v in obj.items())
        if type(obj) in (State, Condition, Snapshot) and is_dataclass(obj):
            return size + sum(visit(getattr(obj, f.name)) for f in fields(obj))
        raise Fault("unsupported retained data type")
    return visit(value)


class Meter:
    """Cooperative caps with complete timed phase receipts, including failure."""
    def __init__(self, *, max_checks=100000, phase_cpu=60.0,
                 total_cpu=7200.0, max_bytes=1048576):
        if (type(max_checks) is not int or not 0 <= max_checks <= 100000
                or type(max_bytes) is not int or not 0 < max_bytes <= 1048576
                or any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0
                       for x in (phase_cpu, total_cpu))
                or phase_cpu > 60 or total_cpu > 7200):
            raise Fault("invalid/enlarged budget")
        self.max_checks, self.phase_cpu = max_checks, phase_cpu
        self.total_cpu, self.max_bytes = total_cpu, max_bytes
        self.counts = dict.fromkeys(COUNTERS, 0)
        self.receipts = []
        self._start = time.process_time()
        self._phase = None

    def checkpoint(self, retained: object = None) -> None:
        now = time.process_time()
        if now - self._start >= self.total_cpu:
            raise BudgetExceeded("total CPU cap")
        if self._phase is not None and now - self._phase[0] >= self.phase_cpu:
            raise BudgetExceeded("phase CPU cap")
        if retained_size(retained) > self.max_bytes:
            raise BudgetExceeded("retained case bytes cap")

    def tick(self, counter: str) -> None:
        if type(counter) is not str or counter not in COUNTERS:
            raise Fault("unknown counter")
        self.checkpoint()
        if counter == "candidate_checks":
            if self._phase is None:
                raise Fault("candidate checks require explicit phase")
            if self.counts[counter] - self._phase[2][counter] >= self.max_checks:
                raise BudgetExceeded("candidate checks cap")
        self.counts[counter] += 1

    @contextmanager
    def phase(self, name: str):
        if type(name) is not str or not name or self._phase is not None:
            raise Fault("invalid/nested phase")
        self._phase = (time.process_time(), time.perf_counter(), self.counts.copy())
        status = "complete"
        try:
            self.checkpoint()
            yield self
            self.checkpoint()
        except BaseException as exc:
            status = "budget_exhausted" if isinstance(exc, BudgetExceeded) else "failed"
            raise
        finally:
            cpu, wall, before = self._phase
            self.receipts.append({"phase": name, "status": status,
                                  "cpu_seconds": time.process_time() - cpu,
                                  "wall_seconds": time.perf_counter() - wall,
                                  "counts": {k: self.counts[k] - before[k] for k in COUNTERS}})
            self._phase = None
