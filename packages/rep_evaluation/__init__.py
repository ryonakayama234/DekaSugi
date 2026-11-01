"""ENGINEERING-ONLY, fully disclosed toy pipeline. NEVER formal TRAIN/DEV/FINAL."""
from __future__ import annotations
from dataclasses import dataclass
from packages.relational_world import Action, InventedWorld, Observation, Relation
from packages.world_model import consistent_models, predicted_next
from packages.representation import (ConceptSnapshot, induce_train_snapshot,
                                     induce_rank_only_snapshot, rank_only_prediction,
                                     episodic_prediction, relational_prediction)


@dataclass(frozen=True, slots=True)
class ToyResult:
    source_kind: str
    train_worlds: int
    toy_eval_worlds: int
    examples_per_world: int
    concept_names: tuple[str, ...]
    r1_correct: int
    r2_correct: int
    r2p_correct: int
    r3_correct: int
    audit_count: int


def training_fixture() -> dict[str, tuple[Observation, ...]]:
    """Disclosed hand-designed training examples. No sealed seeds or independence."""
    result: dict[str, tuple[Observation, ...]] = {}
    for i in range(3):
        ids = tuple(f"train{i}-obj{j}" for j in range(4))
        src, ctx, tgt = (ids[0], ids[1], ids[2]) if i % 2 == 0 else (ids[2], ids[0], ids[3])
        world = InventedWorld(f"train{i}", ids, (Relation(src, tgt, ctx, True),))
        context_idx = ids.index(ctx)
        rows: list[Observation] = []
        for context_on in (False, True):
            states = [False] * 4
            states[context_idx] = context_on
            for object_id in ids:
                rows.append(world.probe(tuple(states), Action("pulse", object_id)))
        result[f"train{i}"] = tuple(rows)
    return result


def run_toy() -> ToyResult:
    """Check the entire toy adapter on deliberately favorable, non-blinded worlds."""
    memory = training_fixture()
    snapshot: ConceptSnapshot = induce_train_snapshot(memory)
    rank_only = induce_rank_only_snapshot(memory)
    assert snapshot.world_receipt == rank_only.world_receipt, "TRAIN transcript mismatch"
    r1 = r2 = r2p = r3 = count = 0
    for i in range(4):
        ids = tuple(f"eval{i}-novel{j}" for j in range(4))
        src, ctx, tgt = (ids[2], ids[0], ids[1]) if i % 2 == 0 else (ids[1], ids[3], ids[0])
        world = InventedWorld(f"toy-eval{i}", ids, (Relation(src, tgt, ctx, True),))
        initial = [False] * 4
        initial[ids.index(ctx)] = True
        evidence = (world.probe(tuple(initial), Action("pulse", src)),)
        fixed_models = consistent_models(ids, evidence, expressive=True)
        assert fixed_models, "Toy evidence must be consistent"
        fixed_model = fixed_models[0]
        for context_on, target_on in ((True, True), (False, True)):
            state = [False] * 4
            state[ids.index(ctx)] = context_on
            state[ids.index(tgt)] = target_on
            before = tuple(state)
            action = Action("pulse", src)
            truth = world.probe(before, action).after
            r1 += predicted_next(ids, before, action, fixed_model) == truth
            r2 += episodic_prediction(memory, ids, before, action) == truth
            r2p += rank_only_prediction(rank_only, ids, evidence, before, action) == truth
            r3 += relational_prediction(snapshot, ids, evidence, before, action) == truth
            count += 1
    return ToyResult("INVENTED_TOY_ENGINEERING_ONLY", len(memory), 4, 1,
                     tuple(c.role_pattern for c in snapshot.concepts), r1, r2, r2p, r3, count)
