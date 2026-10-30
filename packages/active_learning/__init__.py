"""ACTIVE-001 synthetic-only question choice and auditable local state transitions.

This module validates local provenance; a hash is NOT independent Oracle authority.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from types import MappingProxyType
import random
from typing import Literal

from packages.inquiry_world import (
    Catalog, InputSplit, INPUTS, SCHEMA, build_catalog, digest, validate_split,
)

Status = Literal[
    "ambiguous", "identified", "query_unidentifiable", "budget_exhausted",
    "model_inconsistent",
]


@lru_cache(maxsize=1)
def _canonical_catalog() -> Catalog:
    """Build the trusted, fixed finite-world catalog once per process."""
    return build_catalog()


def _assert_catalog(catalog: Catalog) -> Catalog:
    """Reject forged classes, signatures, representative programs or ID lookups.

    The world digest covers only world semantics; it does NOT commit to
    reconstructed Catalog.classes or Catalog.by_id. This comparison checks
    the full canonical generated catalogue (including syntax_count), while
    cached construction avoids 4,681 program enumerations per operation.

    A caller may supply a MappingProxyType wrapping a dict subclass whose
    __getitem__ disagrees with equality.  Never return that untrusted mapping:
    all predictions and program lookups use the internally built canonical
    catalogue returned by this gate.
    """
    if (type(catalog) is not Catalog or
        type(catalog.classes) is not tuple or
        type(catalog.by_id) is not MappingProxyType or
        catalog != _canonical_catalog()):
        raise ValueError("catalog deviates from canonical finite world")
    return _canonical_catalog()


@dataclass(frozen=True, slots=True)
class QuerySession:
    task_id: str
    public_examples: tuple[tuple[int, str], ...]
    available_query_ids: tuple[int, ...]
    public_pool_ids: tuple[int, ...]
    pool_digest: str
    class_ids: tuple[str, ...]
    answers: tuple[tuple[int, str, str], ...]
    trace: tuple[tuple[QueryProposal, QueryAnswer], ...]
    max_questions: int
    status: Status
    world_digest: str
    split_digest: str

    def commitment(self) -> str:
        return digest({
            "schema": "active-query/2", "task_id": self.task_id,
            "public": self.public_examples, "available": self.available_query_ids,
            "public_pool": self.public_pool_ids, "pool_digest": self.pool_digest,
            "classes": self.class_ids, "answers": self.answers,
            "trace": tuple({"proposal": asdict(p), "answer": asdict(a)}
                           for p, a in self.trace),
            "budget": self.max_questions,
            "status": self.status, "world": self.world_digest,
            "split": self.split_digest,
        })


@dataclass(frozen=True, slots=True)
class QueryProposal:
    task_id: str
    step: int
    input_id: int
    policy: str
    random_seed: int | None
    class_count: int
    predictive_partition: tuple[tuple[str, int], ...]
    gini_numerator: int
    gini_denominator: int
    before_digest: str
    proposal_digest: str


@dataclass(frozen=True, slots=True)
class QueryAnswer:
    proposal_digest: str
    input_id: int
    step: int
    output: str
    receipt_digest: str


def _assert_proposal_fields(proposal: QueryProposal) -> None:
    """Require exact primitive storage, not equality-preserving subclasses."""
    if (type(proposal) is not QueryProposal or
        type(proposal.task_id) is not str or
        type(proposal.step) is not int or
        type(proposal.input_id) is not int or
        type(proposal.policy) is not str or
        not (proposal.random_seed is None or type(proposal.random_seed) is int) or
        type(proposal.class_count) is not int or
        type(proposal.gini_numerator) is not int or
        type(proposal.gini_denominator) is not int or
        type(proposal.before_digest) is not str or
        type(proposal.proposal_digest) is not str or
        type(proposal.predictive_partition) is not tuple or
        any(type(part) is not tuple or len(part) != 2 or
            type(part[0]) is not str or type(part[1]) is not int
            for part in proposal.predictive_partition)):
        raise ValueError("noncanonical proposal field type")


def _assert_answer_fields(answer: QueryAnswer) -> None:
    if (type(answer) is not QueryAnswer or
        type(answer.proposal_digest) is not str or
        type(answer.input_id) is not int or
        type(answer.step) is not int or
        type(answer.output) is not str or
        type(answer.receipt_digest) is not str):
        raise ValueError("noncanonical answer field type")


def _assert_session_fields(session: QuerySession) -> None:
    """Block tuple/str/int subclasses whose equality and iteration disagree.

    These are external entry-point storage contracts; the canonical replay
    below validates the actual values and the complete state transition.
    """
    if (type(session) is not QuerySession or
        type(session.class_ids) is not tuple or
        any(type(cid) is not str for cid in session.class_ids) or
        type(session.answers) is not tuple or
        any(type(item) is not tuple or len(item) != 3 or
            type(item[0]) is not int or type(item[1]) is not str or
            type(item[2]) is not str for item in session.answers) or
        type(session.trace) is not tuple or
        type(session.status) is not str or
        type(session.pool_digest) is not str or
        type(session.world_digest) is not str or
        type(session.split_digest) is not str):
        raise ValueError("noncanonical session field type")


def _status(class_ids: tuple[str, ...], answers: int, max_questions: int) -> Status:
    if not class_ids:
        return "model_inconsistent"
    if len(class_ids) == 1:
        return "identified"
    if answers >= max_questions:
        return "budget_exhausted"
    return "ambiguous"


def start(task_id: str, public_examples: tuple[tuple[int, str], ...],
          split: InputSplit, catalog: Catalog, *, max_questions: int = 2) -> QuerySession:
    validate_split(split)
    catalog = _assert_catalog(catalog)
    if type(task_id) is not str or not 1 <= len(task_id) <= 128:
        raise ValueError("invalid task ID")
    if type(max_questions) is not int or not 0 <= max_questions <= 2:
        raise ValueError("question budget outside fixed limit")
    if type(public_examples) is not tuple or len(public_examples) != 2:
        raise ValueError("exactly two public examples required")
    ids: list[int] = []
    for item in public_examples:
        if (type(item) is not tuple or len(item) != 2 or
            type(item[0]) is not int or item[0] not in split.public_ids or
            type(item[1]) is not str or len(item[1]) > 64):
            raise ValueError("invalid or evaluator-only public example")
        ids.append(item[0])
    if len(set(ids)) != 2:
        raise ValueError("public inputs must be distinct")
    classes = tuple(c.class_id for c in catalog.classes if all(
        c.output_signature[i] == y for i, y in public_examples
    ))
    pool_digest = digest({
        "split": split.split_digest, "public": split.public_ids,
        "query": split.query_ids,
    })
    return QuerySession(task_id, public_examples, split.query_ids,
                        split.public_ids, pool_digest, classes, (), (),
                        max_questions, _status(classes, 0, max_questions),
                        catalog.universe_digest, split.split_digest)


def _remaining(session: QuerySession) -> list[int]:
    asked = {item[0] for item in session.answers}
    return [i for i in session.available_query_ids if i not in asked]


def _partition_without_revalidation(session: QuerySession, catalog: Catalog,
                                    input_id: int) -> tuple[tuple[str, int], ...]:
    counts = Counter(_canonical_catalog().by_id[cid].output_signature[input_id]
                     for cid in session.class_ids)
    return tuple(sorted(counts.items()))


def _score(groups: tuple[tuple[str, int], ...]) -> tuple[int, int]:
    n = sum(count for _, count in groups)
    return n * n - sum(count * count for _, count in groups), n * n


def _proposal_without_revalidation(session: QuerySession, catalog: Catalog,
                                   input_id: int, policy: str,
                                   random_seed: int | None) -> QueryProposal:
    groups = _partition_without_revalidation(session, catalog, input_id)
    num, den = _score(groups)
    payload = {
        "schema": "active-query/2", "task": session.task_id,
        "step": len(session.answers), "input": input_id,
        "policy": policy, "random_seed": random_seed,
        "groups": groups, "gini_num": num, "gini_den": den,
        "before": session.commitment(),
    }
    return QueryProposal(session.task_id, len(session.answers), input_id,
                         policy, random_seed, len(session.class_ids), groups,
                         num, den, session.commitment(), digest(payload))


def _choose_without_revalidation(session: QuerySession, catalog: Catalog,
                                 policy: str, seed: int | None) -> QueryProposal | None:
    if session.status != "ambiguous":
        return None
    if policy not in ("max-disagreement-v1", "uniform-random-v1"):
        raise ValueError("unrecognized query policy")
    if policy == "max-disagreement-v1":
        if seed is not None:
            raise ValueError("B2 has no random seed")
    elif type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("invalid B1 seed")
    remaining = _remaining(session)
    if not remaining:
        return None
    scores = [(i, _score(_partition_without_revalidation(session, catalog, i))[0])
              for i in remaining]
    best = max((n for _, n in scores), default=0)
    if best == 0:
        return None
    if policy == "max-disagreement-v1":
        chosen = min(i for i, n in scores if n == best)
    else:
        chosen = random.Random(
            f"active001-random-v1:{seed}:{session.commitment()}"
        ).choice(remaining)
    return _proposal_without_revalidation(session, catalog, chosen, policy, seed)


def make_answer(proposal: QueryProposal, output: str) -> QueryAnswer:
    """Synthetic fixture receipt only; NO independent Oracle authentication."""
    _assert_proposal_fields(proposal)
    if type(output) is not str or len(output) > 64:
        raise ValueError("invalid synthetic answer")
    payload = {"proposal": proposal.proposal_digest, "id": proposal.input_id,
               "step": proposal.step, "output": output}
    return QueryAnswer(proposal.proposal_digest, proposal.input_id,
                       proposal.step, output, digest(payload))


def _apply_without_revalidation(session: QuerySession, proposal: QueryProposal,
                                answer: QueryAnswer, catalog: Catalog) -> QuerySession:
    kept = tuple(cid for cid in session.class_ids if
                 _canonical_catalog().by_id[cid].output_signature[proposal.input_id] == answer.output)
    answers = session.answers + ((proposal.input_id, answer.output,
                                  answer.receipt_digest),)
    trace = session.trace + ((proposal, answer),)
    result = replace(session, class_ids=kept, answers=answers, trace=trace,
                     status=_status(kept, len(answers), session.max_questions))
    if result.status == "ambiguous" and _choose_without_revalidation(
        result, catalog, "max-disagreement-v1", None
    ) is None:
        result = replace(result, status="query_unidentifiable")
    return result


def _assert_world(session: QuerySession, catalog: Catalog) -> None:
    """Replay the *entire* ordered history; trust neither caller classes nor receipts."""
    _assert_session_fields(session)
    catalog = _assert_catalog(catalog)
    if (session.world_digest != catalog.universe_digest or
        type(session.task_id) is not str or not 1 <= len(session.task_id) <= 128 or
        type(session.max_questions) is not int or not 0 <= session.max_questions <= 2):
        raise ValueError("invalid task/world/budget")
    pub, query = session.public_pool_ids, session.available_query_ids
    if (type(pub) is not tuple or type(query) is not tuple or
        len(pub) != 28 or len(query) != 64 or
        any(type(i) is not int or not 0 <= i < len(INPUTS) for i in pub + query) or
        tuple(sorted(pub)) != pub or tuple(sorted(query)) != query or
        len(set(pub + query)) != 92):
        raise ValueError("invalid public/question partition")
    audit = tuple(i for i in range(len(INPUTS)) if i not in set(pub + query))
    canonical_split = InputSplit(pub, query, audit, session.split_digest)
    validate_split(canonical_split)  # Compare recomputed schema digest with stored split digest.
    if session.pool_digest != digest({
        "split": session.split_digest, "public": pub, "query": query
    }):
        raise ValueError("tampered public/question pool commitment")
    if (type(session.trace) is not tuple or
        len(session.trace) > session.max_questions or
        type(session.answers) is not tuple or
        len(session.answers) != len(session.trace)):
        raise ValueError("invalid history length or budget")
    # start() enforces that two public observations lie inside the public-only pool.
    replay = start(session.task_id, session.public_examples, canonical_split,
                   catalog, max_questions=session.max_questions)
    for pair in session.trace:
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("invalid historical proposal/answer pair")
        proposal, answer = pair
        _assert_proposal_fields(proposal)
        _assert_answer_fields(answer)
        if replay.status != "ambiguous":
            raise ValueError("question after terminal state or invalid record")
        if proposal.policy == "max-disagreement-v1":
            if proposal.random_seed is not None:
                raise ValueError("B2 seed must be null")
        elif proposal.policy == "uniform-random-v1":
            if type(proposal.random_seed) is not int or not 0 <= proposal.random_seed < 2**63:
                raise ValueError("invalid historical B1 seed")
        else:
            raise ValueError("invalid historical policy")
        expected = _choose_without_revalidation(
            replay, catalog, proposal.policy, proposal.random_seed
        )
        if expected is None or proposal != expected:
            raise ValueError("historical policy/choice/digest does not replay")
        if answer != make_answer(proposal, answer.output):
            raise ValueError("historical answer receipt failed local replay")
        replay = _apply_without_revalidation(replay, proposal, answer, catalog)
    # An explicitly requested query_unidentifiable terminal state is legal when
    # the initial/public-only state already has zero informative questions.
    if (replay.status == "ambiguous" and
        session.status == "query_unidentifiable" and
        _choose_without_revalidation(replay, catalog, "max-disagreement-v1", None) is None):
        replay = replace(replay, status="query_unidentifiable")
    if session != replay:
        raise ValueError("session differs from the complete replayed history")


def partitions(session: QuerySession, catalog: Catalog,
               input_id: int) -> tuple[tuple[str, int], ...]:
    _assert_world(session, catalog)
    if (type(input_id) is not int or input_id not in session.available_query_ids or
        input_id in {a[0] for a in session.answers}):
        raise ValueError("invalid/repeated question")
    return _partition_without_revalidation(session, catalog, input_id)


def _new_proposal(session: QuerySession, catalog: Catalog, input_id: int,
                  policy: str, *, random_seed: int | None = None) -> QueryProposal:
    partitions(session, catalog, input_id)
    return _proposal_without_revalidation(session, catalog, input_id,
                                          policy, random_seed)


def propose_disagreement(session: QuerySession, catalog: Catalog) -> QueryProposal | None:
    _assert_world(session, catalog)
    return _choose_without_revalidation(session, catalog, "max-disagreement-v1", None)


def propose_random(session: QuerySession, catalog: Catalog,
                   *, seed: int) -> QueryProposal | None:
    _assert_world(session, catalog)
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("invalid random policy seed")
    return _choose_without_revalidation(session, catalog, "uniform-random-v1", seed)


def no_informative_query(session: QuerySession, catalog: Catalog) -> QuerySession:
    _assert_world(session, catalog)
    if (session.status != "ambiguous" or
        _choose_without_revalidation(session, catalog, "max-disagreement-v1", None) is not None):
        raise ValueError("cannot declare unidentifiable with a valid question")
    return replace(session, status="query_unidentifiable")


def update(session: QuerySession, proposal: QueryProposal, answer: QueryAnswer,
           catalog: Catalog) -> QuerySession:
    _assert_world(session, catalog)
    _assert_proposal_fields(proposal)
    _assert_answer_fields(answer)
    if session.status != "ambiguous":
        raise ValueError("invalid/stale question proposal")
    if proposal.policy == "max-disagreement-v1":
        if proposal.random_seed is not None:
            raise ValueError("B2 seed must be null")
    elif proposal.policy == "uniform-random-v1":
        if type(proposal.random_seed) is not int or not 0 <= proposal.random_seed < 2**63:
            raise ValueError("B1 seed invalid")
    else:
        raise ValueError("unrecognized policy")
    expected = _choose_without_revalidation(
        session, catalog, proposal.policy, proposal.random_seed
    )
    if expected is None or proposal != expected:
        raise ValueError("proposal did not follow true policy argmax/seed")
    if answer != make_answer(proposal, answer.output):
        raise ValueError("answer receipt mismatch")
    result = _apply_without_revalidation(session, proposal, answer, catalog)
    _assert_world(result, catalog)
    return result


def final_program(session: QuerySession, catalog: Catalog) -> tuple[str, ...] | None:
    _assert_world(session, catalog)
    return _canonical_catalog().by_id[session.class_ids[0]].program if session.class_ids else None
