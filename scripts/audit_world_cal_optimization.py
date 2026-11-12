#!/usr/bin/env python3
"""Paired public-fixture audit against immutable 834fe0dc; NEVER a power scan.

Private subprocess mode only snapshots explicitly enumerated synthetic inputs.
No CAL capability, authentic IDs, split, escrow or implicit RNG is constructed.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
import resource

BASE='834fe0dc0c33065a1b8039764097141c1d526d98'
ROOT=Path(__file__).resolve().parents[1]
PUBLIC_KEY=bytes.fromhex('0b'*32)
TOL=1e-10

def encoded(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(x):return hashlib.sha256(encoded(x)).hexdigest()

def snapshot(n,scenario,repetition):
    import world_cal.power_engine as e
    from world_cal.prf import draw_digest,encode_parts
    from scripts.profile_world_cal_integrated import Q,PARENTS
    data={'fixture':{'n':n,'scenario':scenario,'repetition':repetition}}
    trace=hashlib.sha256();binary=hashlib.sha256();instances=[]
    counters=[];scores={};variances=[];bootstrap={}
    original=e._CounterDraws
    native=hasattr(original,'uniform_many')
    class Traced(original):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);instances.append(self)
        if native:
            def uniform_many(self,stage,count):
                start=self.next_index.get(stage,0)
                values=super().uniform_many(stage,count)
                for ix,value in enumerate(values,start):
                    trace.update(encoded((stage,ix,value.hex())))
                return values
        else:
            def uniform(self,stage):
                ix=self.next_index.get(stage,0)
                value=super().uniform(stage)
                trace.update(encoded((stage,ix,value.hex())))
                return value
    e._CounterDraws=Traced
    aggregate=e.aggregate_law
    def scored(y):
        binary.update(encoded(y));result=aggregate(y)
        scores[str(len(scores))]=result
        return result
    e.aggregate_law=scored
    syg=e.syg
    def variance(*a,**kw):
        value=syg(*a,**kw);variances.append(value);return value
    e.syg=variance
    name='bootstrap_vectors_array' if native else 'bootstrap_vectors_cached'
    bootstrap_fn=getattr(e,name)
    def boot(sample,q,pi,vectors,parents,draws):
        bootstrap.update(sample=sample,vectors=vectors,draws_sha256=digest(draws),
                         draw_count=len(draws))
        points,reps=bootstrap_fn(sample,q,pi,vectors,parents,draws)
        bootstrap.update(points=points,replicates=reps)
        return points,reps
    setattr(e,name,boot)
    try:
        data['result']=e.run_one_repetition(q=Q,parent_ids=PARENTS,n=n,
            scenario_id=scenario,repetition=repetition,key=PUBLIC_KEY,synthetic_fixture=True)
    except e.PowerUnknown as exc:
        data['exception']={'type':type(exc).__name__,'message':str(exc)}
    obj=instances[0]
    # The production path's actual consumed uniforms and terminal spare/counters.
    data.update(uniform_trace_sha256=trace.hexdigest(),counters=obj.next_index,
                spare={k:v.hex() for k,v in obj.spare.items()},
                binary_y_sha256=binary.hexdigest(),scores=scores,syg=variances,
                bootstrap=bootstrap)
    # Verify FULL 32-byte native digests for every actually consumed scope/index,
    # not merely the leading 53 uniform bits. Extra calls are audit-only replay.
    raw_reference=hashlib.sha256();raw_native=hashlib.sha256()
    if native:
        from world_cal._prf_batch import uniforms
    for stage,count in sorted(obj.next_index.items()):
        expected=b''.join(draw_digest(PUBLIC_KEY,'sha256:'+e.MODEL_SHA,
            scenario,n,repetition,stage,i) for i in range(count))
        raw_reference.update(expected)
        if native:
            prefix=encode_parts('WORLD-CAL-v1','sha256:'+e.MODEL_SHA,
                                scenario,n,repetition,stage)
            actual=uniforms(PUBLIC_KEY,prefix,0,count,True)
            assert actual==expected, 'full digest byte mismatch'
            raw_native.update(actual)
    data['raw_prf_sha256']=raw_reference.hexdigest()
    if native:assert raw_native.digest()==raw_reference.digest()
    return data

def bench():
    from scripts.profile_world_cal_integrated import profile
    report=profile()
    # Unlike getrusage ru_maxrss, this excludes a parent's inherited pre-exec
    # high-water mark on Linux; retain both counters transparently.
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith('VmHWM:'):
            report['measurement']['exec_image_rss_hwm_kib']=int(line.split()[1])
    return report


def profiled():
    import cProfile
    import pstats
    profiler=cProfile.Profile();profiler.enable();bench();profiler.disable()
    stats=pstats.Stats(profiler)
    rows=[]
    for (file,line,name),(cc,nc,tt,ct,callers) in stats.stats.items():
        if '/world_cal/' in file:
            rows.append({'file':file.split('/world_cal/')[-1], 'line':line,
                         'function':name,'calls':nc,'self_seconds':tt,
                         'cumulative_seconds':ct})
    return sorted(rows,key=lambda r:r['cumulative_seconds'],reverse=True)[:16]

def compare(a,b,path=''):
    if type(a) is float and type(b) is float:
        error=abs(a-b)
        assert error<=TOL,(path,a,b,error)
        return error
    assert type(a) is type(b),(path,type(a),type(b))
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        return max((compare(a[k],b[k],path+'/'+str(k)) for k in a),default=0.)
    if isinstance(a,list):
        assert len(a)==len(b),path
        return max((compare(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),default=0.)
    assert a==b,(path,a,b)
    return 0.

def child(root,mode,fixture=None):
    env=os.environ.copy();env.update(PYTHONPATH=str(root),PYTHONHASHSEED='0',
                    OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    args=[sys.executable,str(Path(__file__).resolve()),'--child',mode]
    if fixture:args+=['--n',str(fixture[0]),'--scenario',fixture[1],'--repetition',str(fixture[2])]
    return json.loads(subprocess.check_output(args,cwd=root,env=env))

def audit():
    rows=[]
    with tempfile.TemporaryDirectory(prefix='world-cal-public-reference-') as td:
        reference=Path(td)
        raw=subprocess.check_output(['git','archive',BASE,'world_cal','scripts/profile_world_cal_integrated.py'],cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as tar:tar.extractall(reference,filter='data')
        scenarios=('GTHETA-BASE-01','GTHETA-LOWCORR-01','GTHETA-HIGHCORR-01')
        # Finite enumerated fixtures, NOT the registered ascending n scan.
        fixtures=[(n,s,0) for n in (8,96,160,336) for s in scenarios]
        fixtures.append((96,scenarios[0],7))
        for fixture in fixtures:
            a=child(reference,'snapshot',fixture);b=child(ROOT,'snapshot',fixture)
            error=compare(a,b)
            rows.append({'fixture':a['fixture'],'reference_sha256':digest(a),
                         'optimized_sha256':digest(b),'max_abs_float_error':error,
                         'uniform_trace_sha256':a['uniform_trace_sha256'],
                         'full_prf_digest_sha256':a['raw_prf_sha256'],
                         'random_draw_count':sum(a['counters'].values()),
                         'binary_y_sha256':a['binary_y_sha256'],
                         'result':b.get('result'), 'exception':b.get('exception'),
                         'components':{k:{'reference_sha256':digest(a[k]),
                             'optimized_sha256':digest(b[k]),
                             'max_abs_float_error':compare(a[k],b[k])}
                             for k in ('counters','spare','scores','syg','bootstrap')}})
            print('fixture PASS',fixture,'max error',error,file=sys.stderr,flush=True)
        timings=[]
        for pair in range(5):
            # Alternate process order, include cold per-repetition design/model.
            order=(('reference',reference),('optimized',ROOT))
            if pair%2:order=order[::-1]
            results={name:child(root,'bench') for name,root in order}
            timings.append(results)
        profiles={'reference':child(reference,'profile'),'optimized':child(ROOT,'profile')}
        baseline=statistics.median(t['reference']['measurement']['wall_seconds'] for t in timings)
        optimized=statistics.median(t['optimized']['measurement']['wall_seconds'] for t in timings)
    from world_cal import _prf_batch
    binary_path=Path(_prf_batch.__file__)
    return {'id':'WORLD-CAL-OPTIMIZATION-EVIDENCE-20261112-01',
      'kind':'PUBLIC_SYNTHETIC_FIXTURE_COMPARISON_ONLY','reference_head':BASE,
      'reference_algorithm_digest':'sha256:1c722753379711b49c01df12bcc4be2d910e14cfc549ed65ba9d828c8a8e1e01',
      'algorithm_digest':None,'cal_authorized':False,'cal_executed':False,
      'full_power_executed':False,'k0_executed':False,'seed_generated':False,
      'sealed_split_materialized':False,'tolerance':TOL,'fixtures':rows,
      'benchmark_pairs':timings,'instrumented_profile_not_used_for_speedup':profiles,
      'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (
           'world_cal/power_engine.py','world_cal/inference.py','world_cal/prf_batch.c',
           'scripts/build_world_cal_prf_batch.py','scripts/audit_world_cal_optimization.py',
           'tests/test_world_cal_optimization.py')},'median_reference_wall_seconds':baseline,
      'median_optimized_wall_seconds':optimized,'paired_same_host_speedup':baseline/optimized,
      'fivefold_gate':'MET' if baseline/optimized>=5 else 'NOT_MET_STOP_FOR_OWNER',
      'execution_cores':1,'parallelism':'none; sequential native loops; no BLAS',
      'native_binary':{'sha256':hashlib.sha256(binary_path.read_bytes()).hexdigest(),
                       'size_bytes':binary_path.stat().st_size},
      'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
      'openssl':subprocess.check_output(['openssl','version'],text=True).strip(),
      'limitations':'No production feasibility certification. All-n wall projection is '
       'the existing linear-in-n extrapolation, not a validated per-n runtime model.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--child',choices=('snapshot','bench','profile'))
    p.add_argument('--n',type=int);p.add_argument('--scenario');p.add_argument('--repetition',type=int,default=0)
    p.add_argument('--output');args=p.parse_args()
    result=(snapshot(args.n,args.scenario,args.repetition) if args.child=='snapshot' else
            bench() if args.child=='bench' else profiled() if args.child=='profile' else audit())
    raw=json.dumps(result,indent=None if args.child else 2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:Path(args.output).write_text(raw,encoding='utf-8')
    else:print(raw)
