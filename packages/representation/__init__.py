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
    if type(snapshot) is not ConceptSnapshot or snapshot.schema != "rep-toy-snapshot/0.1":
        raise ValueError("Wrong snapshot format")
    if (type(snapshot.world_receipt) is not str or len(snapshot.world_receipt) != 64 or
            type(snapshot.concepts) is not tuple or len(snapshot.concepts) > 3):
        raise ValueError("Invalid snapshot metadata")
    if tuple(sorted(snapshot.concepts, key=lambda c: c.role_pattern)) != snapshot.concepts:
        raise ValueError("Noncanonical ordering")
    for c in snapshot.concepts:
        if (type(c) is not ConceptCandidate or
                c.role_pattern not in ("direct", "gated_true", "gated_false") or
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
