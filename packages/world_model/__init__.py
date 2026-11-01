"""EXP-REP-001 bounded public hypothesis space for invented 1-edge Boolean worlds."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from packages.relational_world import Action, Observation, Relation, step, _validate_objects


@dataclass(frozen=True, slots=True)
class HypothesisDiagnosis:
    status: str
    direct_survivors: int
    expressive_survivors: int


def candidates(objects: tuple[str, ...], expressive: bool = True) -> tuple[tuple[Relation, ...], ...]:
    _validate_objects(objects)
    models: list[tuple[Relation, ...]] = [()]
    for source in objects:
        for target in objects:
            if target == source:
                continue
            models.append((Relation(source, target),))
            if expressive:
                for context in objects:
                    if context not in (source, target):
                        models.append((Relation(source, target, context, True),))
                        models.append((Relation(source, target, context, False),))
    return tuple(models)


def consistent_models(objects: tuple[str, ...], observations: tuple[Observation, ...],
                      expressive: bool = True) -> tuple[tuple[Relation, ...], ...]:
    models = candidates(objects, expressive)
    for obs in observations:
        if type(obs) is not Observation or obs.object_ids != objects:
            raise ValueError("Malformed public observation or object mismatch")
        models = tuple(model for model in models if
                       step(objects, obs.before, obs.action, model) == obs.after)
    return models


def diagnose(objects: tuple[str, ...], observations: tuple[Observation, ...]) -> HypothesisDiagnosis:
    direct = consistent_models(objects, observations, expressive=False)
    full = consistent_models(objects, observations, expressive=True)
    if len(direct) == 1:
        status = "direct_identified"
    elif direct:
        status = "underidentified"
    elif len(full) == 1:
        status = "representation_refinement_identified"
    elif full:
        status = "representation_refinement_ambiguous"
    else:
        status = "model_class_mismatch"
    return HypothesisDiagnosis(status, len(direct), len(full))


def choose_discriminating_probe(objects: tuple[str, ...],
                                models: tuple[tuple[Relation, ...], ...]) -> tuple[tuple[bool, ...], Action]:
    """Deterministic max-disagreement toy policy. Not an entropy-optimal formal policy."""
    _validate_objects(objects)
    if not models:
        raise ValueError("Cannot query empty hypothesis set")
    best: tuple[tuple[bool, ...], Action] | None = None
    best_diversity = -1
    for bits in product((False, True), repeat=len(objects)):
        state = tuple(bits)
        for object_id in objects:
            act = Action("pulse", object_id)
            diversity = len({step(objects, state, act, model) for model in models})
            if diversity > best_diversity:
                best_diversity, best = diversity, (state, act)
    assert best is not None
    return best


def predicted_next(objects: tuple[str, ...], state: tuple[bool, ...], action: Action,
                   model: tuple[Relation, ...]) -> tuple[bool, ...]:
    return step(objects, state, action, model)
