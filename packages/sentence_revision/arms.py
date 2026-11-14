"""Four finite-rule arms; public examples only, mandatory cooperative metering.

No evaluator, production loader, text parser, synthesis cache or historical import.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import json

from .foundation import (
    BudgetExceeded, Fault, Meter, State, canonical, catalog,
    execute, grammar_digest, validate_input,
)

ARMS = ("REVISE", "FROZEN", "MEMORY", "FRESH")
SCHEMA = "sentence-case/1"


def _text(value: str, limit: int) -> None:
    if type(value) is not str or not value.strip() or len(value) > limit:
        raise Fault("invalid bounded text")


@dataclass(frozen=True, slots=True)
class Example:
    before: State
    after: State

    def record(self) -> dict:
        if type(self) is not Example:
            raise Fault("exact Example required")
        validate_input(self.before)
        if type(self.after) is not State:
            raise Fault("exact output State required")
        # Validate all fields without charging a simulation that did not run.
        after = self.after.record()
        b, i = self.before.buffer, self.before.cursor
        deleted = State(b[:i] + b[i + 1:], i)
        if self.after not in (self.before, deleted):
            raise Fault("example output is neither KEEP nor DELETE_RIGHT")
        return {"before": self.before.record(), "after": after}

    @classmethod
    def parse(cls, value: dict) -> Example:
        if type(value) is not dict or set(value) != {"before", "after"}:
            raise Fault("example JSON shape")
        result = cls(State.parse(value["before"]), State.parse(value["after"]))
        result.record()
        return result


def _pairs(examples: tuple[Example, ...], count: int) -> tuple:
    if type(examples) is not tuple or len(examples) != count:
        raise Fault("wrong example tuple/count")
    pairs = []
    for example in examples:
        if type(example) is not Example:
            raise Fault("exact Example required")
        example.record()
        pairs.append((example.before, example.after))
    return tuple(pairs)


def _coherent(pairs: tuple) -> None:
    for i, (before, after) in enumerate(pairs):
        if any(before == b and after != a for b, a in pairs[:i]):
            raise Fault("contradictory public state key; no overwrite")


def _filter(ids: tuple[str, ...], pairs: tuple, rules: tuple,
            meter: Meter, retained: object) -> tuple[str, ...]:
    kept = []
    for candidate_id in ids:
        rule = rules[int(candidate_id[5:])]
        for before, after in pairs:
            meter.checkpoint((retained, rules, ids, pairs, kept))
            meter.tick("candidate_checks")
            if execute(rule, before, meter) != after:
                break
        else:
            kept.append(candidate_id)
    return tuple(kept)


def _build(pairs: tuple, meter: Meter, retained: object) -> tuple[str, ...]:
    rules = catalog(meter)
    return _filter(tuple(f"cond-{i:03d}" for i in range(78)),
                   pairs, rules, meter, retained)


def _updated(arm: str, initial: tuple[str, ...] | None, pairs: tuple,
             meter: Meter, retained: object) -> tuple[str, ...] | None:
    if arm == "MEMORY":
        return None
    if arm == "FROZEN":
        return initial
    if arm == "FRESH":
        return _build(pairs, meter, retained)
    rules = catalog(meter)
    return _filter(initial, pairs[-1:], rules, meter, retained)


def _view(ids: tuple[str, ...] | None, rules: tuple) -> dict | None:
    if ids is None:
        return None
    selected = ids[0] if ids else None
    return {"candidate_ids": list(ids), "selected_id": selected,
            "selected_ast": rules[int(selected[5:])].ast() if selected else None,
            "explanation": rules[int(selected[5:])].explain() if selected else None}


def _saved(data: dict, meter: Meter, retained: object = None) -> bytes:
    # Diagnostics are recomputed and charged; prediction never trusts this as a cache.
    rules = catalog(meter)
    value = {"schema": SCHEMA, "grammar_sha256": grammar_digest(meter),
             "arm": data["arm"], "rule_id": data["rule_id"],
             "texts": list(data["texts"]),
             "examples": [{"before": b.record(), "after": a.record()}
                          for b, a in data["pairs"]],
             "initial": _view(data["initial"], rules),
             "current": _view(data["current"], rules)}
    meter.checkpoint((retained, data, rules, value))
    raw = canonical(value)
    meter.checkpoint((retained, data, rules, value, raw))
    return raw


class Case:
    """A single arm/case, created or restored using a run-wide Meter.

    Failures are not predictions. Budget exhaustion permanently stops this object;
    the caller retains the meter's failed receipt and later C will render stop rows.
    """
    def __init__(self):
        raise Fault("use Case.create or Case.restore")

    @classmethod
    def _new(cls, meter: Meter) -> Case:
        if cls is not Case or type(meter) is not Meter:
            raise Fault("exact Case and mandatory Meter required")
        result = object.__new__(cls)
        result._meter = meter
        result._data = {}
        result._stopped = False
        return result

    @contextmanager
    def _operation(self, name: str, request: object = None):
        if self._stopped:
            raise BudgetExceeded("case is terminal after resource exhaustion")
        try:
            with self._meter.phase(name):
                self._meter.checkpoint((self._data, request))
                yield
                self._meter.checkpoint((self._data, request))
        except BudgetExceeded:
            self._stopped = True
            raise

    @classmethod
    def create(cls, arm: str, rule_id: str, text: str,
               examples: tuple[Example, Example], *, meter: Meter) -> Case:
        result = cls._new(meter)
        # Convert only exact validated objects to supported retained data.
        with result._operation("build"):
            if type(arm) is not str or arm not in ARMS:
                raise Fault("unknown arm")
            _text(rule_id, 128)
            _text(text, 4096)
            pairs = _pairs(examples, 2)
            _coherent(pairs)
            data = {"arm": arm, "rule_id": rule_id, "texts": (text,), "pairs": pairs}
            meter.checkpoint(data)
            ids = None if arm == "MEMORY" else _build(pairs, meter, data)
            data.update(initial=ids, current=ids)
            meter.checkpoint(data)
            result._data = data
        return result

    def correct(self, text: str, example: Example) -> None:
        with self._operation("update"):
            if len(self._data["pairs"]) != 2:
                raise Fault("correction slot already consumed")
            _text(text, 4096)
            pair = _pairs((example,), 1)
            data = dict(self._data, texts=(*self._data["texts"], text),
                        pairs=(*self._data["pairs"], *pair))
            _coherent(data["pairs"])
            self._meter.checkpoint((self._data, data))
            data["current"] = _updated(data["arm"], data["initial"], data["pairs"],
                                       self._meter, (self._data, data))
            self._meter.checkpoint((self._data, data))
            self._data = data

    def predict(self, state: State) -> dict:
        # Convert after exact type validation, before including in retained roots.
        with self._operation("predict"):
            validate_input(state)
            self._meter.checkpoint((self._data, state))
            rules, ids, output = (), (), None
            if self._data["arm"] == "MEMORY":
                output = next((a for b, a in self._data["pairs"] if b == state), None)
                if output is not None:
                    self._meter.tick("submissions")
                result = {"status": "predicted" if output is not None else "abstain",
                          "output": output.record() if output is not None else None,
                          "selected_id": None}
            else:
                ids = (_build(self._data["pairs"], self._meter, (self._data, state))
                       if self._data["arm"] == "FRESH" else self._data["current"])
                if not ids:
                    result = {"status": "no_consistent_candidate", "output": None,
                              "selected_id": None}
                else:
                    rules = catalog(self._meter)
                    self._meter.checkpoint((self._data, state, ids, rules))
                    output = execute(rules[int(ids[0][5:])], state, self._meter)
                    result = {"status": "predicted", "output": output.record(),
                              "selected_id": ids[0]}
            self._meter.checkpoint((self._data, state, rules, ids, output, result))
            return result

    def save(self) -> bytes:
        with self._operation("save"):
            return _saved(self._data, self._meter)

    @classmethod
    def restore(cls, raw: bytes, *, meter: Meter) -> Case:
        result = cls._new(meter)
        with result._operation("restore"):
            if type(raw) is not bytes:
                raise Fault("exact bytes required")
            meter.checkpoint(raw)  # before JSON allocation, counted as resource stop
            if len(raw) > 1048576:
                raise BudgetExceeded("serialized case cap")
            def unique(pairs):
                value = {}
                for key, item in pairs:
                    if key in value:
                        raise Fault("duplicate JSON field")
                    value[key] = item
                return value
            try:
                value = json.loads(raw, object_pairs_hook=unique)
            except (ValueError, UnicodeError, RecursionError) as exc:
                raise Fault("invalid case JSON") from exc
            try:
                meter.checkpoint((raw, value))
            except RecursionError as exc:
                raise Fault("excessively nested case JSON") from exc
            keys = {"schema", "grammar_sha256", "arm", "rule_id", "texts",
                    "examples", "initial", "current"}
            if type(value) is not dict or set(value) != keys or value["schema"] != SCHEMA:
                raise Fault("case schema/shape")
            arm = value["arm"]
            if type(arm) is not str or arm not in ARMS:
                raise Fault("unknown arm")
            _text(value["rule_id"], 128)
            texts, examples = value["texts"], value["examples"]
            if (type(examples) is not list or len(examples) not in (2, 3)
                    or type(texts) is not list or len(texts) != len(examples) - 1):
                raise Fault("case history counts")
            for text in texts:
                _text(text, 4096)
            pairs = _pairs(tuple(Example.parse(x) for x in examples), len(examples))
            _coherent(pairs)
            data = {"arm": arm, "rule_id": value["rule_id"],
                    "texts": tuple(texts), "pairs": pairs}
            meter.checkpoint((raw, value, data))
            initial = None if arm == "MEMORY" else _build(pairs[:2], meter, (raw, value, data))
            data.update(initial=initial, current=initial)
            if len(pairs) == 3:
                data["current"] = _updated(arm, initial, pairs, meter, (raw, value, data))
            meter.checkpoint((raw, value, data))
            encoded = _saved(data, meter, (raw, value))
            meter.checkpoint((raw, value, data, encoded))
            if raw != encoded:
                raise Fault("noncanonical case or incorrect candidate provenance")
            result._data = data
        return result
