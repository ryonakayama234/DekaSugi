"""ACTIVE-001 E0: invented-only public wire envelope parser, NO evaluator.

The parser is intentionally dependency-free and rejects unexpected fields;
it does NOT implement an Oracle, scoring, process isolation, cryptographic
authentication, seed custody or private auditor-label access.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from typing import Any

PUBLIC_SCHEMA = "active001-public-task/1"
QUERY_SCHEMA = "active001-public-query/1"
ANSWER_SCHEMA = "active001-public-answer/1"
FINAL_SCHEMA = "active001-public-final/1"
OPERATIONS = frozenset((
    "trim", "lower", "upper", "reverse", "drop_first", "drop_last",
    "replace_first_a_b", "append_a",
))
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX32 = re.compile(r"[0-9a-f]{32}\Z")


@dataclass(frozen=True, slots=True)
class PublicTaskView:
    schema: str
    session_id: str
    public_pool_ids: tuple[int, ...]
    query_input_ids: tuple[int, ...]
    public_examples: tuple[tuple[int, str], ...]
    split_digest: str
    max_questions: int


@dataclass(frozen=True, slots=True)
class PublicQuestion:
    schema: str
    session_id: str
    challenge_digest: str
    step: int
    input_id: int


@dataclass(frozen=True, slots=True)
class PublicAnswer:
    schema: str
    session_id: str
    challenge_digest: str
    step: int
    input_id: int
    output: str


@dataclass(frozen=True, slots=True)
class FinalProgramSubmission:
    schema: str
    session_id: str
    challenge_digest: str
    program: tuple[str, ...]


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key is prohibited")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant not permitted")


def _load(raw: str, keys: frozenset[str]) -> dict[str, Any]:
    if type(raw) is not str or len(raw) > 12_000:
        raise ValueError("invalid wire input")
    try:
        data = json.loads(raw, object_pairs_hook=_no_duplicate_keys,
                          parse_constant=_reject_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("invalid JSON") from exc
    if type(data) is not dict or set(data) != keys:
        raise ValueError("missing or unapproved wire fields")
    return data


def _hex(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError("invalid opaque session/digest field")
    return value


def _ids(value: object, n: int) -> tuple[int, ...]:
    if (type(value) is not list or len(value) != n or
        any(type(x) is not int or not 0 <= x < 156 for x in value) or
        value != sorted(set(value))):
        raise ValueError("query/public ID pool must be distinct ascending ints")
    return tuple(value)


def _str_output(value: object) -> str:
    if type(value) is not str or len(value) > 64:
        raise ValueError("invalid public/Oracle output")
    return value


def _dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def parse_public_task(raw: str) -> PublicTaskView:
    d = _load(raw, frozenset((
        "schema", "session_id", "public_pool_ids", "query_input_ids",
        "public_examples", "split_digest", "max_questions",
    )))
    if d["schema"] != PUBLIC_SCHEMA or type(d["max_questions"]) is not int or d["max_questions"] != 2:
        raise ValueError("incorrect public view schema or question budget")
    session_id = _hex(d["session_id"], HEX32)
    split_digest = _hex(d["split_digest"], HEX64)
    pub = _ids(d["public_pool_ids"], 28)
    query = _ids(d["query_input_ids"], 64)
    if set(pub).intersection(query):
        raise ValueError("overlapping public and allowed-query pools")
    audit_complement = tuple(i for i in range(156)
                             if i not in set(pub + query))
    expected_split_digest = sha256(_dump({
        "schema": "inquiry-world/1", "public": pub,
        "query": query, "audit": audit_complement,
    }).encode("utf-8")).hexdigest()
    if split_digest != expected_split_digest:
        raise ValueError("canonical pool partition does not match split commitment")
    examples = d["public_examples"]
    if (type(examples) is not list or len(examples) != 2 or
        any(type(pair) is not list or len(pair) != 2 or
            type(pair[0]) is not int or pair[0] not in pub
            for pair in examples)):
        raise ValueError("exactly two public-only examples required")
    if examples[0][0] == examples[1][0]:
        raise ValueError("repeated public observation input")
    pairs = tuple((pair[0], _str_output(pair[1])) for pair in examples)
    # No fields for evaluator-only inputs/labels, target, seed root, scores.
    return PublicTaskView(PUBLIC_SCHEMA, session_id, pub, query, pairs,
                          split_digest, 2)


def encode_public_task(view: PublicTaskView) -> str:
    if type(view) is not PublicTaskView:
        raise ValueError("unexpected public-view type")
    payload = asdict(view)
    raw = _dump(payload)
    if parse_public_task(raw) != view:
        raise ValueError("public-view not canonically representable")
    return raw


def challenge_digest(view: PublicTaskView) -> str:
    return sha256(("ACTIVE001-E0-CHALLENGE:" +
                   encode_public_task(view)).encode("utf-8")).hexdigest()


def _parent_guard(data: dict[str, Any], schema: str,
                  view: PublicTaskView) -> None:
    if (data["schema"] != schema or
        data["session_id"] != view.session_id or
        data["challenge_digest"] != challenge_digest(view)):
        raise ValueError("mismatched session/challenge/schema")


def parse_question(raw: str, view: PublicTaskView,
                   *, asked_ids: tuple[int, ...]) -> PublicQuestion:
    if type(asked_ids) is not tuple or any(type(i) is not int for i in asked_ids):
        raise ValueError("invalid prior query history")
    if len(asked_ids) > 2 or len(set(asked_ids)) != len(asked_ids) or any(
        i not in view.query_input_ids for i in asked_ids
    ):
        raise ValueError("invalid prior query pool/order")
    d = _load(raw, frozenset(("schema", "session_id", "challenge_digest",
                              "step", "input_id")))
    _parent_guard(d, QUERY_SCHEMA, view)
    if (type(d["step"]) is not int or d["step"] != len(asked_ids) or
        len(asked_ids) >= view.max_questions or
        type(d["input_id"]) is not int or
        d["input_id"] not in view.query_input_ids or
        d["input_id"] in asked_ids):
        raise ValueError("wrong-step, repeated or unauthorized question")
    return PublicQuestion(QUERY_SCHEMA, view.session_id, challenge_digest(view),
                          d["step"], d["input_id"])


def parse_answer(raw: str, view: PublicTaskView,
                 *, question: PublicQuestion) -> PublicAnswer:
    if type(question) is not PublicQuestion:
        raise ValueError("invalid outstanding question")
    d = _load(raw, frozenset(("schema", "session_id", "challenge_digest",
                              "step", "input_id", "output")))
    _parent_guard(d, ANSWER_SCHEMA, view)
    if (question.session_id != view.session_id or
        question.challenge_digest != challenge_digest(view) or
        type(d["step"]) is not int or d["step"] != question.step or
        type(d["input_id"]) is not int or d["input_id"] != question.input_id):
        raise ValueError("response does not match outstanding question")
    return PublicAnswer(ANSWER_SCHEMA, view.session_id,
                        challenge_digest(view), question.step,
                        question.input_id, _str_output(d["output"]))


def parse_final(raw: str, view: PublicTaskView) -> FinalProgramSubmission:
    d = _load(raw, frozenset((
        "schema", "session_id", "challenge_digest", "program",
    )))
    _parent_guard(d, FINAL_SCHEMA, view)
    ops = d["program"]
    if (type(ops) is not list or len(ops) > 4 or
        any(type(x) is not str or x not in OPERATIONS for x in ops)):
        raise ValueError("invalid final DSL program")
    # No requested predictions on auditor-only IDs, and no scores.
    return FinalProgramSubmission(FINAL_SCHEMA, view.session_id,
                                  challenge_digest(view), tuple(ops))
