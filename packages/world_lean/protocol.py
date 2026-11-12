"""Public numeric contract; no evaluator data, recipes, IO or imports.

The sole definition of DEMOS_PER_LAW. Copied with public learner sources to
isolated child roots; evaluator protocol re-exports this module.
"""
WORLD='lean-editor/1'
ARMS=('FULL','OFF','STATIC-RANK','LOOKUP')
N_REPLICATES=16
B=(0,512,1024,2048,4096)
TRAIN_BODY_PAIRS=((0,1),(1,2),(2,3))
HELD_OUT_PAIR_PLAN=((0,2),(0,3),(1,3))
DEMOS_PER_LAW=6
QUERIES_PER_LAW=2
EXTRA_DIAG_QUERIES_PER_LAW=2
DRAW_LIMIT=4096
MAX_WALL_SECONDS=48*3600
MAX_CPU_SECONDS=36*3600
MAX_SAVE_BYTES=2*1024**3
