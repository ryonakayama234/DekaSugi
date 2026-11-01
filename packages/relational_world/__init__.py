"""EXP-REP-001 public, invented-only finite world; NOT a private evaluator."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Action:
    kind: str
    object_id: str
    value: bool | None = None


@dataclass(frozen=True, slots=True)
class Relation:
    source: str
    target: str
    context: str | None = None
    context_value: bool = True


@dataclass(frozen=True, slots=True)
class Observation:
    world_alias: str
    object_ids: tuple[str, ...]
    before: tuple[bool, ...]
    action: Action
    after: tuple[bool, ...]


def _validate_objects(objects: tuple[str, ...]) -> None:
    if type(objects) is not tuple or not 4 <= len(objects) <= 8 or any(type(x) is not str or not x for x in objects) or len(set(objects)) != len(objects):
        raise ValueError("Expected 4–8 distinct nonempty string IDs")


def validate_state(objects: tuple[str, ...], state: tuple[bool, ...]) -> None:
    _validate_objects(objects)
    if type(state) is not tuple or len(state) != len(objects) or any(type(x) is not bool for x in state):
        raise ValueError("State must be a tuple of Boolean values")


def validate_action(objects: tuple[str, ...], action: Action) -> None:
    if (type(action) is not Action or type(action.kind) is not str or
            type(action.object_id) is not str or action.object_id not in objects):
        raise ValueError("Unknown action or object")
    if action.kind == "pulse" and action.value is None:
        return
    if action.kind == "set_state" and type(action.value) is bool:
        return
    raise ValueError("Action is not on the fixed allowlist")


def step(objects: tuple[str, ...], state: tuple[bool, ...], action: Action,
         rules: tuple[Relation, ...]) -> tuple[bool, ...]:
    """Synchronous pulse: active edges toggle their targets by parity; set_state is local."""
    validate_state(objects, state)
    validate_action(objects, action)
    if type(rules) is not tuple or any(type(r) is not Relation for r in rules):
        raise ValueError("Invalid rule tuple")
    lookup = {name: idx for idx, name in enumerate(objects)}
    toggles = [False] * len(objects)
    for rule in rules:
        if (type(rule.source) is not str or type(rule.target) is not str or
                (rule.context is not None and type(rule.context) is not str) or
                rule.source not in lookup or rule.target not in lookup or
                rule.source == rule.target or
                (rule.context is not None and (rule.context not in lookup or
                 rule.context in (rule.source, rule.target))) or
                type(rule.context_value) is not bool):
            raise ValueError("Invalid hidden relation")
        if action.kind == "pulse" and action.object_id == rule.source and (
                rule.context is None or state[lookup[rule.context]] == rule.context_value):
            toggles[lookup[rule.target]] ^= True
    after = list(state)
    if action.kind == "set_state":
        after[lookup[action.object_id]] = action.value
    else:
        after = [value ^ flip for value, flip in zip(state, toggles)]
    return tuple(after)


class InventedWorld:
    """Toy host-owned world. Same-process isolation is NOT a security boundary."""
    def __init__(self, alias: str, object_ids: tuple[str, ...], rules: tuple[Relation, ...]):
        _validate_objects(object_ids)
        if type(alias) is not str or not alias or type(rules) is not tuple:
            raise ValueError("Invalid invented world")
        step(object_ids, (False,) * len(object_ids), Action("pulse", object_ids[0]), rules)
        self._alias = alias
        self._objects = object_ids
        self._rules = rules

    @property
    def object_ids(self) -> tuple[str, ...]:
        return self._objects

    def probe(self, before: tuple[bool, ...], action: Action) -> Observation:
        """One counterfactual probe. Reset/state setup cost is NOT modeled yet."""
        return Observation(self._alias, self._objects, before, action,
                           step(self._objects, before, action, self._rules))
