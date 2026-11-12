"""Fixture-only engineering gate. Formal-science CLI does not exist by design."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from packages.world_lean.core import State, Session, TOKENS, canonical, step, execute
from packages.world_lean.learner import (Learner, demo_candidates, derive_bodies,
                                         infer, sequence)
from .fixture import (FIXTURE_STREAMS, Recipe, audit_ambiguity, body, examples,
                      random_train_blocks)

from .protocol import DEMOS_PER_LAW

DESIGN_TRANSITION_CEILING=252_928_000
WALL_CAP_SECONDS=48*3600
CPU_CAP_SECONDS=36*3600

def child_request(root: Path, message: dict) -> dict:
    process=subprocess.run([sys.executable,'-I',str(root/'world_lean'/'child_entry.py')],
        input=canonical(message),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        cwd=root,timeout=120,check=False,
        env={'PATH':os.environ.get('PATH',''),'HOME':str(root),'PYTHONHASHSEED':'0'})
    if process.returncode!=0:raise AssertionError(process.stderr.decode())
    return json.loads(process.stdout)

def negative_boundary_fixture() -> dict:
    with tempfile.TemporaryDirectory(prefix='world-lean-boundary-') as temporary:
        root=Path(temporary)
        public=root/'child_only'/'world_lean'
        public.mkdir(parents=True)
        public_src=Path(__file__).parents[1]/'packages'/'world_lean'
        for filename in ('__init__.py','core.py','learner.py','child_entry.py','protocol.py'):
            shutil.copyfile(public_src/filename,public/filename)
        private=root/'evaluator_private'
        private.mkdir()
        (private/'holdout-seed.fixture-sentinel').write_text('CANARY-DO-NOT-LEAK')
        (private/'evaluator-source.fixture-sentinel').write_text('CANARY-EVAL-SOURCE')
        probe=child_request(public.parent,{'mode':'boundary_probe'})
        assert probe['ok']
        assert probe['data']['evaluator_importable'] is False
        assert all(str(private) not in path for path in probe['data']['sys_path'])
        assert all(str(Path(__file__).parent) not in path for path in probe['data']['sys_path'])
        attack=child_request(public.parent,{'mode':'train','blocks':[],
                                          'holdout':'FORBIDDEN','evaluation_source':'FORBIDDEN'})
        assert attack['ok'] is False and 'forbidden' in attack['error']
        attack2=child_request(public.parent,{'mode':'infer','snapshot_b64':'',
                           'arm':'FULL','demos':[],'query':{},'target':'FORBIDDEN'})
        assert attack2['ok'] is False and 'forbidden' in attack2['error']
        return {'process_mode':'python -I','learner_imports_evaluator':False,
                'private_root_absent':True,'extra_target_seed_keys_rejected':True,
                'threat_model':'cooperative code; same-UID malicious access not prevented'}

def reachability_fixture() -> dict:
    # Invented public demo sets only. Never query any designed HOLDOUT recipe.
    categories={'local_insert':Recipe(0,0,1),'local_delete':Recipe(3,1,2),
                'copy':Recipe(2,3,2),'conditional':Recipe(1,3,1)}
    evidence={}
    for category,recipe in categories.items():
        data=examples(recipe,FIXTURE_STREAMS[0])
        asts,stats=demo_candidates(data[:DEMOS_PER_LAW])
        successes=[ast for ast in asts if all(execute(ast,x)[0]==y for x,y in data[:DEMOS_PER_LAW])]
        if not successes:raise AssertionError('STATIC-RANK fixture unreachable: '+category)
        assert stats['verified']<=128
        evidence[category]={'candidate_ordinal':next(i+1 for i,a in enumerate(asts)
               if all(execute(a,x)[0]==y for x,y in data[:DEMOS_PER_LAW])),
               'verified':stats['verified'],'constructed_edges':stats['construct_edges'],
               'chosen_ast_digest':hashlib.sha256(canonical(successes[0])).hexdigest()}
    return evidence

def benchmark() -> dict:
    state=State(('A','B','C','D'),2)
    # 100,000 legal primitive transitions, source supplied operations only.
    started=time.perf_counter()
    for i in range(100_000):state=step(state,TOKENS[i%14])
    seconds=time.perf_counter()-started
    rate=100_000/seconds
    learner=Learner()
    blocks=random_train_blocks(FIXTURE_STREAMS[0],8)
    begun=time.perf_counter()
    for block in blocks:learner.add_block(block)
    update_seconds=time.perf_counter()-begun
    # Observe the six-demo inference paths on one TRAIN-only artificial law.
    demo=examples(Recipe(1,3,1),FIXTURE_STREAMS[0])
    snap=learner.snapshot()
    inference_seconds={}
    for arm in ('FULL','OFF','STATIC-RANK','LOOKUP'):
        begin=time.perf_counter()
        infer(snap,arm,demo[:DEMOS_PER_LAW],demo[DEMOS_PER_LAW][0])
        inference_seconds[arm]=time.perf_counter()-begin
    estimated_transition_sec=DESIGN_TRANSITION_CEILING/rate
    # pessimistic 16*64*3 observed update costs, plus 2x transition-time reserve
    # (not a formal upper bound; CPU overhead may be non-linear).
    # The nominal query schedule: (5*48 + 48) queries x16 realizations/arm.
    expected_queries_per_arm=16*(5*48+48)
    inferred_cpu=sum(expected_queries_per_arm*t for t in inference_seconds.values())
    estimated_cpu=estimated_transition_sec*2+update_seconds*16*64*3+inferred_cpu
    return {'n_transitions':100_000,'seconds':round(seconds,6),
            'measured_transitions_per_sec':round(rate,2),
            'update_for_64_train_events_seconds':round(update_seconds,6),
            'updates_reached':learner.updates,'update_library_size':len(learner.library),
            'sample_one_query_per_arm_seconds':{k:round(v,6) for k,v in inference_seconds.items()},
            'sample_query_extrapolation_hours':round(inferred_cpu/3600,3),
            'design_cap_transitions':DESIGN_TRANSITION_CEILING,
            'transitions_only_hours':round(estimated_transition_sec/3600,3),
            'extrapolation_2x_transitions_plus_update_hours':round(estimated_cpu/3600,3),
            'under_36h_cpu_proxy':estimated_cpu<=CPU_CAP_SECONDS,
            'under_48h_wall_proxy':estimated_cpu<=WALL_CAP_SECONDS,
            'meets_5000_per_sec':rate>=5000,
            'caveat':'Artificial one-law timings, CPython fixture runtime and projected per-query costs are NOT rigorous 16-seed wall/CPU bounds; filesystem I/O, source patch differences and worst-case grammar remain unmeasured.'}

def run_gate() -> dict:
    amb=[audit_ambiguity(s) for s in FIXTURE_STREAMS]
    total=sum(a['queries'] for a in amb)
    ambiguous=sum(a['ambiguous_queries'] for a in amb)
    bench=benchmark()
    reach=reachability_fixture()
    boundary=negative_boundary_fixture()
    evidence={'schema':'WORLD-LEAN-1/ARTIFICIAL-FIXTURE-GATE/2',
        'formal_seed_generation':'NOT_RUN','formal_holdout':'NOT_MATERIALIZED',
        'formal_evaluation':'NOT_RUN','ambiguous_train_only':amb,
        'ambiguity_combined_fraction':f'{ambiguous}/{total}',
        'ambiguity_above_10pct':ambiguous*10>total,
        'transitions':bench,'static_rank_reachability':reach,
        'boundary_negative':boundary}
    # Raw deterministic evidence digest does NOT include nondeterministic timings.
    evidence['deterministic_digest']=hashlib.sha256(canonical({
        'ambiguous_train_only':amb,'static_rank_reachability':reach,
        'boundary_negative':boundary})).hexdigest()
    evidence['engineering_gate_status']=('REVIEW_DESIGN_AMBIGUITY' if ambiguous*10>total
        else 'REVIEW_CPU_EXTRAPOLATION' if not bench['under_36h_cpu_proxy'] or not bench['meets_5000_per_sec']
        else 'FIXTURE_PASSED_SUPERVISOR_PENDING')
    return evidence
