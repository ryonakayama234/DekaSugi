"""EXP-REP-001 invented-only counterexample refinement and cross-world Sleep sketch.

Concepts are learned within a human-supplied typed relation meta-language.
No official evaluator, holdout scoring or independently sealed data belongs here.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from packages.relational_world import Observation, Relation, Action
from packages.world_model import consistent_models, predicted_next


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")).hexdigest()


def shape(model: tuple[Relation, ...]) -> str:
    if len(model) != 1:
        return "none" if not model else "unsupported_multi_edge"
    edge = model[0]
    return "direct" if edge.context is None else ("gated_true" if edge.context_value else "gated_false")


@dataclass(frozen=True, slots=True)
class ConceptCandidate:
    concept_id: str
    role_pattern: str
    support_worlds: tuple[str, ...]
    support_count: int


@dataclass(frozen=True, slots=True)
class ConceptSnapshot:
    schema: str
    world_receipt: str
    concepts: tuple[ConceptCandidate, ...]
    snapshot_digest: str


def _snapshot_body(snapshot: ConceptSnapshot) -> dict[str, object]:
    return {"schema": snapshot.schema, "world_receipt": snapshot.world_receipt,
            "concepts": [asdict(c) for c in snapshot.concepts]}


def validate_snapshot(snapshot: ConceptSnapshot) -> None:
    if (type(snapshot) is not ConceptSnapshot or
            type(snapshot.schema) is not str or
            snapshot.schema != "rep-toy-snapshot/0.1"):
        raise ValueError("Wrong snapshot format")
    if (type(snapshot.world_receipt) is not str or len(snapshot.world_receipt) != 64 or
            type(snapshot.snapshot_digest) is not str or len(snapshot.snapshot_digest) != 64 or
            type(snapshot.concepts) is not tuple or len(snapshot.concepts) > 3):
        raise ValueError("Invalid snapshot metadata")
    # Validate nested builtin types before comparisons, sets, hashing, sorting
    # or serialization: hostile str/int subclasses can change dictionary keys
    # without changing their JSON text or a prior content digest.
    for c in snapshot.concepts:
        if (type(c) is not ConceptCandidate or
                type(c.concept_id) is not str or
                type(c.role_pattern) is not str or
                type(c.support_count) is not int or
                type(c.support_worlds) is not tuple or
                any(type(w) is not str or not w for w in c.support_worlds)):
            raise ValueError("Noncanonical concept primitive types")
    if tuple(sorted(snapshot.concepts, key=lambda c: c.role_pattern)) != snapshot.concepts:
        raise ValueError("Noncanonical ordering")
    for c in snapshot.concepts:
        if (c.role_pattern not in ("direct", "gated_true", "gated_false") or
                c.concept_id != digest({"type": c.role_pattern}) or
                c.support_count != len(c.support_worlds) or c.support_count < 3 or
                c.support_worlds != tuple(sorted(set(c.support_worlds)))):
            raise ValueError("Invalid concept provenance")
    if snapshot.snapshot_digest != digest(_snapshot_body(snapshot)):
        raise ValueError("Tampered snapshot")


def induce_train_snapshot(world_episodes: dict[str, tuple[Observation, ...]]) -> ConceptSnapshot:
    """Canonicalize learned relation *roles* across >=3 uniquely solved TRAIN worlds."""
    if type(world_episodes) is not dict or not world_episodes:
        raise ValueError("Nonempty TRAIN episodes required")
    supports: dict[str, list[str]] = {}
    receipt: list[dict[str, object]] = []
    if any(type(alias) is not str for alias in world_episodes):
        raise ValueError("TRAIN aliases must be exact builtin strings")
    for world_alias, observations in sorted(world_episodes.items()):
        if type(world_alias) is not str or not world_alias or type(observations) is not tuple or not observations:
            raise ValueError("Invalid world/observations")
        if any(type(obs) is not Observation or obs.world_alias != world_alias for obs in observations):
            raise ValueError("Cross-world observation injection")
        objects = observations[0].object_ids
        models = consistent_models(objects, observations, expressive=True)
        receipt.append({"world": world_alias, "observations": [{"objects": o.object_ids,
            "before": o.before, "action": asdict(o.action), "after": o.after} for o in observations]})
        if len(models) == 1:
            family = shape(models[0])
            if family in ("direct", "gated_true", "gated_false"):
                supports.setdefault(family, []).append(world_alias)
    concepts = tuple(sorted((ConceptCandidate(digest({"type": kind}), kind, tuple(worlds), len(worlds))
                             for kind, worlds in supports.items() if len(worlds) >= 3),
                            key=lambda c: c.role_pattern))
    body = {"schema": "rep-toy-snapshot/0.1", "world_receipt": digest(receipt),
            "concepts": [asdict(c) for c in concepts]}
    snapshot = ConceptSnapshot(body["schema"], body["world_receipt"], concepts, digest(body))
    validate_snapshot(snapshot)
    return snapshot


def learned_model_preference(objects: tuple[str, ...], observations: tuple[Observation, ...],
                             snapshot: ConceptSnapshot) -> tuple[Relation, ...]:
    """Choose a public-consistent model using persisted cross-world relation concepts."""
    validate_snapshot(snapshot)
    models = consistent_models(objects, observations, expressive=True)
    if not models:
        raise ValueError("Observed world outside one-edge hypothesis class")
    preferred = {c.role_pattern: c.support_count for c in snapshot.concepts}
    return min(models, key=lambda m: (-preferred.get(shape(m), 0),
                tuple((r.source, r.target, r.context or "", r.context_value) for r in m)))


def episodic_prediction(train_episodes: dict[str, tuple[Observation, ...]],
                        objects: tuple[str, ...], before: tuple[bool, ...],
                        action: Action) -> tuple[bool, ...]:
    """R2 engineering placeholder: exact experience retrieval, no induced relation roles."""
    if type(train_episodes) is not dict:
        raise ValueError("Invalid memory")
    for world_id, episodes in sorted(train_episodes.items()):
        for obs in episodes:
            if (obs.object_ids == objects and obs.before == before and obs.action == action):
                return obs.after
    return before


def relational_prediction(snapshot: ConceptSnapshot, objects: tuple[str, ...],
                          test_observations: tuple[Observation, ...],
                          before: tuple[bool, ...], action: Action) -> tuple[bool, ...]:
    model = learned_model_preference(objects, test_observations, snapshot)
    return predicted_next(objects, before, action, model)


# R2P is a *policy-only mechanism control*, not a claim of concept-free
# cognition. Its fixed-grammar family frequencies encode a coarse abstraction,
# but it stores no executable or reusable ConceptCandidate/role template.
@dataclass(frozen=True, slots=True)
class RankOnlySnapshot:
    schema: str
    world_receipt: str
    preferences: tuple[tuple[str, int], ...]
    snapshot_digest: str


def validate_rank_only_snapshot(snapshot: RankOnlySnapshot) -> None:
    if (type(snapshot) is not RankOnlySnapshot or
            type(snapshot.schema) is not str or snapshot.schema != "rep-toy-rank-only/0.1" or
            type(snapshot.world_receipt) is not str or len(snapshot.world_receipt) != 64 or
            type(snapshot.snapshot_digest) is not str or len(snapshot.snapshot_digest) != 64 or
            type(snapshot.preferences) is not tuple):
        raise ValueError("Malformed R2P snapshot")
    for item in snapshot.preferences:
        if (type(item) is not tuple or len(item) != 2 or
                type(item[0]) is not str or
                item[0] not in ("direct", "gated_true", "gated_false") or
                type(item[1]) is not int or item[1] < 3):
            raise ValueError("Malformed R2P preference")
    if tuple(sorted(snapshot.preferences)) != snapshot.preferences:
        raise ValueError("Unsorted R2P preferences")
    if len({p[0] for p in snapshot.preferences}) != len(snapshot.preferences):
        raise ValueError("Duplicate R2P preferences")
    body = {"schema": snapshot.schema, "world_receipt": snapshot.world_receipt,
            "preferences": snapshot.preferences}
    if snapshot.snapshot_digest != digest(body):
        raise ValueError("Tampered R2P snapshot")


def induce_rank_only_snapshot(
    world_episodes: dict[str, tuple[Observation, ...]]
) -> RankOnlySnapshot:
    """TRAIN-only fixed-grammar frequency prior, no persisted concept bodies."""
    if type(world_episodes) is not dict or not world_episodes:
        raise ValueError("Nonempty TRAIN episodes required")
    if any(type(alias) is not str for alias in world_episodes):
        raise ValueError("TRAIN aliases must be exact builtin strings")
    counts: dict[str, int] = {}
    receipt: list[dict[str, object]] = []
    for alias, observations in sorted(world_episodes.items()):
        if type(alias) is not str or not alias or type(observations) is not tuple or not observations:
            raise ValueError("Invalid TRAIN data")
        if any(type(o) is not Observation or type(o.world_alias) is not str or
               o.world_alias != alias for o in observations):
            raise ValueError("Cross-world observation")
        models = consistent_models(observations[0].object_ids, observations, expressive=True)
        receipt.append({"world": alias, "observations": [
            {"objects": o.object_ids, "before": o.before,
             "action": asdict(o.action), "after": o.after} for o in observations]})
        if len(models) == 1:
            family = shape(models[0])
            if family in ("direct", "gated_true", "gated_false"):
                counts[family] = counts.get(family, 0) + 1
    body = {"schema": "rep-toy-rank-only/0.1", "world_receipt": digest(receipt),
            "preferences": tuple(sorted((family, n) for family, n in counts.items() if n >= 3))}
    snapshot = RankOnlySnapshot(body["schema"], body["world_receipt"],
                                body["preferences"], digest(body))
    validate_rank_only_snapshot(snapshot)
    return snapshot


def rank_only_prediction(snapshot: RankOnlySnapshot, objects: tuple[str, ...],
                         test_observations: tuple[Observation, ...],
                         before: tuple[bool, ...], action: Action) -> tuple[bool, ...]:
    """R2P and R3 use identical inference grammar, tie-break and test transcript."""
    validate_rank_only_snapshot(snapshot)
    models = consistent_models(objects, test_observations, expressive=True)
    if not models:
        raise ValueError("Observed world outside one-edge hypothesis class")
    pref = dict(snapshot.preferences)
    model = min(models, key=lambda m: (-pref.get(shape(m), 0),
                tuple((r.source, r.target, r.context or "", r.context_value) for r in m)))
    return predicted_next(objects, before, action, model)
