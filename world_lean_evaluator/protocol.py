"""Evaluator entrypoints and re-export of the data-free public numeric contract."""
from packages.world_lean.protocol import (WORLD, ARMS, N_REPLICATES, B,
    TRAIN_BODY_PAIRS, HELD_OUT_PAIR_PLAN, DEMOS_PER_LAW, QUERIES_PER_LAW,
    EXTRA_DIAG_QUERIES_PER_LAW, DRAW_LIMIT, MAX_WALL_SECONDS, MAX_CPU_SECONDS,
    MAX_SAVE_BYTES)

class OwnerEvaluationAuthorizationRequired(PermissionError):
    pass

def formal_generation(root=None, *, authorization=None, dry_run=False):
    from .formal import generate
    return generate(root, authorization=authorization, dry_run=dry_run)

def formal_run(root=None, *, authorization=None, dry_run=False):
    from .formal import run
    return run(root, authorization=authorization, dry_run=dry_run)
