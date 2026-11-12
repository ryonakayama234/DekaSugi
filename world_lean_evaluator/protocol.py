"""Protocol constants for future evaluator-only execution; no permitted formal run."""
from __future__ import annotations

WORLD='lean-editor/1'
N_REPLICATES=16
B=(0,512,1024,2048,4096)
TRAIN_BODY_PAIRS=((0,1),(1,2),(2,3))
HELD_OUT_PAIR_PLAN=((0,2),(0,3),(1,3))  # a plan, not tasks or a split manifest
DEMOS_PER_LAW=4
QUERIES_PER_LAW=2
EXTRA_DIAG_QUERIES_PER_LAW=2
DRAW_LIMIT=4096
MAX_WALL_SECONDS=48*3600
MAX_CPU_SECONDS=36*3600
MAX_SAVE_BYTES=2*1024**3

class OwnerEvaluationAuthorizationRequired(PermissionError):pass

def formal_generation(*args,**kwargs):
    """Fail closed until separate supervisor audit and Owner evaluation GO."""
    raise OwnerEvaluationAuthorizationRequired(
        'Formal seed/task/holdout materialization is forbidden in the implementation-GO stage')

def formal_run(*args,**kwargs):
    raise OwnerEvaluationAuthorizationRequired(
        'Formal evaluation is forbidden until a distinct Owner evaluation GO')
