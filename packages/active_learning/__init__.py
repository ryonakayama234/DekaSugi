"""ACTIVE-001 synthetic-only question choice and belief updates; no oracle imports."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
import random
from typing import Literal

from packages.inquiry_world import Catalog, InputSplit, INPUTS, digest, validate_split

Status = Literal["ambiguous", "identified", "query_unidentifiable", "budget_exhausted", "model_inconsistent"]


@dataclass(frozen=True, slots=True)
class QuerySession:
    task_id: str
    public_examples: tuple[tuple[int, str], ...]
    available_query_ids: tuple[int, ...]
    public_pool_ids: tuple[int, ...]
    pool_digest: str
    class_ids: tuple[str, ...]
    answers: tuple[tuple[int, str, str], ...]
    max_questions: int
    status: Status
    world_digest: str
    split_digest: str

    def commitment(self) -> str:
        return digest({"schema": "active-query/1", "task_id": self.task_id,
                       "public": self.public_examples, "available": self.available_query_ids,
                       "public_pool": self.public_pool_ids, "pool_digest": self.pool_digest,
                       "classes": self.class_ids, "answers": self.answers,
                       "budget": self.max_questions, "status": self.status,
                       "world": self.world_digest, "split": self.split_digest})


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


def start(task_id: str, public_examples: tuple[tuple[int, str], ...], split: InputSplit,
          catalog: Catalog, *, max_questions: int = 2) -> QuerySession:
    validate_split(split)
    if type(task_id) is not str or not (1 <= len(task_id) <= 128):
        raise ValueError("invalid task ID")
    if type(max_questions) is not int or not 0 <= max_questions <= 2:
        raise ValueError("question budget outside fixed limit")
    if type(public_examples) is not tuple or len(public_examples) != 2:
        raise ValueError("exactly two public examples required")
    ids = []
    for item in public_examples:
        if type(item) is not tuple or len(item) != 2 or type(item[0]) is not int or item[0] not in split.public_ids or type(item[1]) is not str or len(item[1]) > 64:
            raise ValueError("invalid or evaluator-only public example")
        ids.append(item[0])
    if len(set(ids)) != 2:
        raise ValueError("public inputs must be distinct")
    consistent = tuple(c.class_id for c in catalog.classes if all(c.output_signature[i] == y for i, y in public_examples))
    status: Status = "model_inconsistent" if not consistent else "identified" if len(consistent) == 1 else "budget_exhausted" if max_questions == 0 else "ambiguous"
    pool_digest = digest({"split": split.split_digest, "public": split.public_ids,
                          "query": split.query_ids})
    return QuerySession(task_id, public_examples, split.query_ids, split.public_ids,
                        pool_digest, consistent, (), max_questions, status,
                        catalog.universe_digest, split.split_digest)


def _assert_world(session: QuerySession, catalog: Catalog) -> None:
    """Reconstruct the full version space; does not authenticate a remote Oracle."""
    if type(session) is not QuerySession or type(catalog) is not Catalog:
        raise ValueError("invalid session/catalog")
    if session.world_digest != catalog.universe_digest or type(session.task_id) is not str or not 1 <= len(session.task_id) <= 128:
        raise ValueError("world/task mismatch")
    if type(session.max_questions) is not int or not 0 <= session.max_questions <= 2:
        raise ValueError("invalid budget")
    qpool = session.available_query_ids
    if (type(qpool) is not tuple or len(qpool) != 64 or
        qpool != tuple(sorted(qpool)) or len(set(qpool)) != 64 or
        any(type(i) is not int or not 0 <= i < len(INPUTS) for i in qpool)):
        raise ValueError("invalid question pool")
    pubpool = session.public_pool_ids
    if (type(pubpool) is not tuple or len(pubpool) != 28 or
        pubpool != tuple(sorted(pubpool)) or len(set(pubpool)) != 28 or
        any(type(i) is not int or not 0 <= i < len(INPUTS) for i in pubpool) or
        set(pubpool) & set(qpool)):
        raise ValueError("invalid public pool")
    if session.pool_digest != digest({
        "split": session.split_digest, "public": pubpool, "query": qpool
    }):
        raise ValueError("pool commitment changed")
    if type(session.public_examples) is not tuple or len(session.public_examples) != 2:
        raise ValueError("invalid public observations")
    ids = []
    for item in session.public_examples:
        if (type(item) is not tuple or len(item) != 2 or
            type(item[0]) is not int or not 0 <= item[0] < len(INPUTS) or
            type(item[1]) is not str or len(item[1]) > 64):
            raise ValueError("invalid public example")
        ids.append(item[0])
    if len(set(ids)) != 2 or not set(ids).issubset(pubpool):
        raise ValueError("public/question overlap")
    if type(session.answers) is not tuple or len(session.answers) > session.max_questions:
        raise ValueError("invalid answer history/budget")
    observations = list(session.public_examples)
    used = set()
    for item in session.answers:
        if (type(item) is not tuple or len(item) != 3 or
            type(item[0]) is not int or item[0] not in qpool or item[0] in used or
            type(item[1]) is not str or len(item[1]) > 64 or
            type(item[2]) is not str or len(item[2]) != 64 or
            any(c not in "0123456789abcdef" for c in item[2])):
            raise ValueError("invalid/repeated answer")
        used.add(item[0])
        observations.append((item[0], item[1]))
    expected = tuple(c.class_id for c in catalog.classes
                     if all(c.output_signature[i] == y for i,y in observations))
    if type(session.class_ids) is not tuple or session.class_ids != expected:
        raise ValueError("semantic class votes inconsistent with evidence")
    if not expected:
        status = "model_inconsistent"
    elif len(expected) == 1:
        status = "identified"
    elif len(session.answers) == session.max_questions:
        status = "budget_exhausted"
    else:
        status = "ambiguous"
    if status != "ambiguous":
        if session.status != status:
            raise ValueError("contradictory budget/status")
    elif session.status not in ("ambiguous", "query_unidentifiable"):
        raise ValueError("invalid status")
    elif session.status == "query_unidentifiable":
        if any(len({catalog.by_id[cid].output_signature[i] for cid in expected}) > 1
               for i in qpool if i not in used):
            raise ValueError("discriminating query remains")
    if type(session.split_digest) is not str or len(session.split_digest) != 64 or any(
        c not in "0123456789abcdef" for c in session.split_digest
    ):
        raise ValueError("malformed split digest")


def partitions(session: QuerySession, catalog: Catalog, input_id: int) -> tuple[tuple[str, int], ...]:
    _assert_world(session, catalog)
    if type(input_id) is not int or input_id not in session.available_query_ids or input_id in {a[0] for a in session.answers}:
        raise ValueError("invalid or repeated question")
    counts = Counter(catalog.by_id[cid].output_signature[input_id] for cid in session.class_ids)
    return tuple(sorted(counts.items()))


def _score(groups: tuple[tuple[str, int], ...]) -> tuple[int, int]:
    n = sum(count for _, count in groups)
    return n * n - sum(count * count for _, count in groups), n * n


def _new_proposal(session: QuerySession, catalog: Catalog, input_id: int,
                  policy: str, *, random_seed: int | None = None) -> QueryProposal:
    groups = partitions(session, catalog, input_id)
    numerator, denominator = _score(groups)
    payload = {"schema": "active-query/1", "task": session.task_id,
               "step": len(session.answers), "input": input_id, "policy": policy,
               "random_seed": random_seed, "groups": groups,
               "gini_num": numerator, "gini_den": denominator,
               "before": session.commitment()}
    return QueryProposal(session.task_id, len(session.answers), input_id, policy,
                         random_seed, len(session.class_ids), groups, numerator,
                         denominator, session.commitment(), digest(payload))


def propose_disagreement(session: QuerySession, catalog: Catalog) -> QueryProposal | None:
    _assert_world(session, catalog)
    if session.status != "ambiguous":
        return None
    remaining = [i for i in session.available_query_ids if i not in {a[0] for a in session.answers}]
    scores = [( _score(partitions(session, catalog, i))[0], i) for i in remaining]
    if not scores:
        return None
    largest = max(score for score, _ in scores)
    if largest == 0:
        return None
    winner = min(i for score, i in scores if score == largest)
    return _new_proposal(session, catalog, winner, "max-disagreement-v1")


def propose_random(session: QuerySession, catalog: Catalog, *, seed: int) -> QueryProposal | None:
    _assert_world(session, catalog)
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("invalid random policy seed")
    if session.status != "ambiguous":
        return None
    remaining = [i for i in session.available_query_ids if i not in {a[0] for a in session.answers}]
    if not remaining or all(_score(partitions(session, catalog, i))[0] == 0 for i in remaining):
        return None
    picked = random.Random(f"active001-random-v1:{seed}:{session.commitment()}").choice(remaining)
    return _new_proposal(session, catalog, picked, "uniform-random-v1", random_seed=seed)


def no_informative_query(session: QuerySession, catalog: Catalog) -> QuerySession:
    if session.status != "ambiguous" or propose_disagreement(session, catalog) is not None:
        raise ValueError("cannot declare unidentifiable while a valid query exists")
    return replace(session, status="query_unidentifiable")


def make_answer(proposal: QueryProposal, output: str) -> QueryAnswer:
    """Synthetic fixture helper only. NOT authentication of an external Oracle."""
    if type(output) is not str or len(output) > 64:
        raise ValueError("invalid answer output")
    value = {"proposal": proposal.proposal_digest, "id": proposal.input_id,
             "step": proposal.step, "output": output}
    return QueryAnswer(proposal.proposal_digest, proposal.input_id, proposal.step, output, digest(value))


def update(session: QuerySession, proposal: QueryProposal, answer: QueryAnswer,
           catalog: Catalog) -> QuerySession:
    _assert_world(session, catalog)
    if session.status != "ambiguous" or proposal.task_id != session.task_id or proposal.step != len(session.answers) or proposal.before_digest != session.commitment() or proposal.policy not in ("max-disagreement-v1", "uniform-random-v1"):
        raise ValueError("stale or impossible question proposal")
    if proposal.policy == "max-disagreement-v1":
        if proposal.random_seed is not None:
            raise ValueError("B2 must not carry a random seed")
        expected = propose_disagreement(session, catalog)
    else:
        if type(proposal.random_seed) is not int or not 0 <= proposal.random_seed < 2**63:
            raise ValueError("invalid random policy seed")
        expected = propose_random(session, catalog, seed=proposal.random_seed)
    if expected is None or proposal != expected:
        raise ValueError("proposal violates policy argmax, seed or commitment")
    if answer != make_answer(proposal, answer.output) or answer.proposal_digest != proposal.proposal_digest or answer.input_id != proposal.input_id or answer.step != proposal.step:
        raise ValueError("answer receipt mismatch")
    kept = tuple(cid for cid in session.class_ids if catalog.by_id[cid].output_signature[proposal.input_id] == answer.output)
    answers = session.answers + ((proposal.input_id, answer.output, answer.receipt_digest),)
    status: Status = "model_inconsistent" if not kept else "identified" if len(kept) == 1 else "budget_exhausted" if len(answers) >= session.max_questions else "ambiguous"
    result = replace(session, class_ids=kept, answers=answers, status=status)
    if status == "ambiguous" and propose_disagreement(result, catalog) is None:
        return replace(result, status="query_unidentifiable")
    return result


def final_program(session: QuerySession, catalog: Catalog) -> tuple[str, ...] | None:
    _assert_world(session, catalog)
    return catalog.by_id[session.class_ids[0]].program if session.class_ids else None
