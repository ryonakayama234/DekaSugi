"""One-shot evaluator driver. Never imported by the isolated learner.

The synthetic profile is conspicuously reduced and contains TRAIN fixtures only.
The official profile is executable only with an explicit external resume record.
No official activation is wired to CI. The parent alone owns seed/recipe/targets.
"""
from __future__ import annotations
import base64
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import tempfile
import time

from packages.world_lean.core import State, TOKENS, canonical, digest, execute
from packages.world_lean import core as metered_core
from packages.world_lean.analysis import scientific_decision
from .protocol import (ARMS, B, DEMOS_PER_LAW, DRAW_LIMIT, EXTRA_DIAG_QUERIES_PER_LAW,
    HELD_OUT_PAIR_PLAN, MAX_CPU_SECONDS, MAX_SAVE_BYTES, MAX_WALL_SECONDS,
    N_REPLICATES, OwnerEvaluationAuthorizationRequired, QUERIES_PER_LAW,
    TRAIN_BODY_PAIRS, WORLD)
from .fixture import (CounterStream, FIXTURE_STREAMS, Recipe, body, condition,
    examples, initial, random_train_blocks, target, train_recipes)

REPO=Path(__file__).resolve().parents[1]
LOCK='docs/research/WORLD-LEAN-1-SOURCE-LOCK-20261112-03.json'
DESIGN='docs/research/WORLD-LEAN-EXPERIMENT-DESIGN-20261112-03.md'
ORDER='docs/research/WORLD-LEAN-1-ORDER-FREEZE-20261112-03.md'
SYNTHETIC_SEED=b'ARTIFICIAL-FORMAL-DRY-RUN-03-NOT-AN-OFFICIAL-SEED'
PUBLIC_FILES=('__init__.py','core.py','learner.py','protocol.py','child_entry.py')

class IntegrityError(ValueError):pass
class ResourceStop(RuntimeError):pass

def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())

def put(path, value, *, raw=False):
    """Exclusive create, flush and fsync; no silent restart/overwrite."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=value if raw else canonical(value)
    with path.open('xb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
    return sha(data)

def verify_lock():
    lock=load(REPO/LOCK)
    actual={p:sha((REPO/p).read_bytes()) for p in sorted(lock['file_sha256'])}
    if actual!=lock['file_sha256'] or digest(actual)!=lock['source_digest']:
        raise IntegrityError('source lock commitment mismatch')
    return lock

def manifest(dry_run=False):
    lock=verify_lock()
    return {'schema':'WORLD-LEAN-1/EXECUTABLE-MANIFEST/3',
        'profile':'SYNTHETIC_TRAIN_ONLY' if dry_run else 'OFFICIAL',
        'world':WORLD,'source_digest':lock['source_digest'],
        'lock_sha256':sha((REPO/LOCK).read_bytes()),
        'design_sha256':sha((REPO/DESIGN).read_bytes()),
        'order_sha256':sha((REPO/ORDER).read_bytes()),
        'runtime':'CPython 3.12.12','arms':list(ARMS),
        'replicates':1 if dry_run else N_REPLICATES,
        'checkpoints':[0,64] if dry_run else list(B),
        'blocks':8 if dry_run else B[-1]//8,
        'train_pairs':[list(p) for p in TRAIN_BODY_PAIRS],
        'holdout_pairs':[] if dry_run else [list(p) for p in HELD_OUT_PAIR_PLAN],
        'demos_per_law':DEMOS_PER_LAW,'main_queries_per_law':QUERIES_PER_LAW,
        'extra_queries_per_law':EXTRA_DIAG_QUERIES_PER_LAW,
        'law_count':1 if dry_run else 24,'draw_limit':DRAW_LIMIT,
        'wall_cap':MAX_WALL_SECONDS,'cpu_cap':MAX_CPU_SECONDS,'save_cap':MAX_SAVE_BYTES,
        'transition_ceiling':252928000,
        'stream':'raw master + length-prefixed world-lean-1/replicate/phase/law/item + uint64 counter; SHA256 unbiased rejection',
        'bootstrap':'MT19937, shared 9999 paired resamples; seed=Stream(master,bootstrap).uint(2**256), SHA256 with uint64 counter=0; exact linear percentile',
        'secondary':'same six demos; query lengths 7..8; separately named public token alphabet',
        'stop':'no retries/redraw except branch/duplicate rejection; all snapshots before all scoring'}

def freeze_manifest(root, *, dry_run=False):
    """Pre-seed step; binds code and protocol, creates no data or entropy."""
    root=Path(root)
    root.mkdir(parents=True,exist_ok=False)
    value=manifest(dry_run)
    put(root/'manifest.json',value)
    put(root/'manifest.sha256',sha(canonical(value)).encode()+b'\n',raw=True)
    return value

def verified_manifest(root, dry_run):
    value=load(root/'manifest.json')
    if value!=manifest(dry_run) or (root/'manifest.sha256').read_text().strip()!=digest(value):
        raise IntegrityError('manifest/lock commitment mismatch')
    return value

def authorize(authorization, dry_run, value):
    if dry_run:
        if value['profile']!='SYNTHETIC_TRAIN_ONLY':raise IntegrityError('synthetic profile required')
        return
    required={'owner_resume_reference','supervisor_reaudit_reference','source_digest','manifest_sha256'}
    if (type(authorization) is not dict or set(authorization)!=required
        or not all(type(v) is str and v for v in authorization.values())
        or authorization['source_digest']!=value['source_digest']
        or authorization['manifest_sha256']!=digest(value)):
        raise OwnerEvaluationAuthorizationRequired('supervisor re-audit and Owner resume record for this exact manifest required')
    if platform.python_implementation()!='CPython' or platform.python_version()!='3.12.12':
        raise IntegrityError('official runtime must be CPython 3.12.12')

class Stream(CounterStream):
    def __init__(self, master, *fields):
        super().__init__('world-lean-1',*map(str,fields))
        self.key=master+self.key

def recipes(pairs):
    return tuple(Recipe(p,a,b) for p in range(4) for x,y in pairs for a,b in ((x,y),(y,x)))

def draw(master, replicate, phase, law, item, recipe, wants, seen, *, extra=False):
    rng=Stream(master,replicate,phase,law,item)
    for _ in range(DRAW_LIMIT):
        state=initial(rng,extra)
        key=digest(state.record())
        if condition(recipe.condition,state)==wants and key not in seen:
            seen.add(key)
            return state,target(recipe,state)
    raise IntegrityError('GENERATION_STOP')

def encode_symbols(value, names):
    if type(value) is list:return [encode_symbols(x,names) for x in value]
    if type(value) is dict:return {k:encode_symbols(v,names) for k,v in value.items()}
    return names['ABCD'.index(value)] if type(value) is str and value in tuple('ABCD') else value

def realization(master, replicate):
    """Only called in the future authorized official generation process."""
    result={'train':[],'main':[],'extra':[]}
    menu=recipes(TRAIN_BODY_PAIRS)
    # Tags and display names use streams separate from initial/trace generation.
    tag_rng=Stream(master,replicate,'tags','TRAIN',0)
    tags=[f'law-{tag_rng.uint(1<<256):064x}' for _ in menu]
    if len(set(tags))!=len(tags):raise IntegrityError('opaque tag collision')
    demo_by_law={}
    for phase,lawset in (('TRAIN',menu),('HOLDOUT',recipes(HELD_OUT_PAIR_PLAN))):
        for law,recipe in enumerate(lawset):
            seen=set();data=[]
            wants=[True]*(DEMOS_PER_LAW//2)+[False]*(DEMOS_PER_LAW//2)+[True,False]
            for item,want in enumerate(wants):
                x,y=draw(master,replicate,phase,law,item,recipe,want,seen)
                data.append([x.record(),y.record()])
            demos=data[:DEMOS_PER_LAW]
            if phase=='TRAIN':demo_by_law[law]=demos
            else:
                for q,(x,y) in enumerate(data[DEMOS_PER_LAW:]):
                    result['main'].append({'law':law,'recipe':[recipe.condition,recipe.then_body,recipe.else_body],
                        'branch':q==0,'demos':demos,'query':x,'target':y})
                for q,want in enumerate((True,False)):
                    x,y=draw(master,replicate,'DIAGNOSTIC',law,q,recipe,want,seen,extra=True)
                    result['extra'].append({'law':law,'recipe':[recipe.condition,recipe.then_body,recipe.else_body],
                        'branch':want,'demos':demos,'query':x.record(),'target':y.record()})
    order_rng=Stream(master,replicate,'TRAIN_ORDER',0,0)
    for round_index in range((B[-1]//8+23)//24):
        order=list(range(24))
        for i in range(23,0,-1):
            j=order_rng.uint(i+1);order[i],order[j]=order[j],order[i]
        for law in order:
            index=len(result['train'])
            if index>=B[-1]//8:break
            recipe=menu[law]
            rng=Stream(master,replicate,'TRAIN_TRACE',law,index)
            start=initial(rng);state=start;actions=[];observations=[state.record()]
            from packages.world_lean.core import step
            for _ in range(8):
                action=TOKENS[rng.uint(len(TOKENS))];state=step(state,action)
                actions.append(list(action));observations.append(state.record())
            result['train'].append({'tag':tags[law],'initial':start.record(),
                'actions':actions,'observations':observations,
                'success':state==target(recipe,start),'demos':demo_by_law[law]})
    def names(phase):
        rng=Stream(master,replicate,'DISPLAY',phase,0)
        return [f'{phase}-{rng.uint(1<<128):032x}' for _ in range(4)]
    result['symbols']=names('main');result['extra_symbols']=names('extra')
    return result

def synthetic_realization():
    """Existing named TRAIN fixtures only. No official HOLDOUT recipe is built."""
    data=examples(train_recipes()[0],FIXTURE_STREAMS[0])
    demos=[[a.record(),b.record()] for a,b in data[:DEMOS_PER_LAW]]
    def queries(extra=False):
        sample=examples(train_recipes()[0],FIXTURE_STREAMS[0],extra=extra)
        return [{'law':0,'recipe':[0,0,1],'branch':q==0,'demos':demos,
                 'query':x.record(),'target':y.record()} for q,(x,y) in enumerate(sample[DEMOS_PER_LAW:])]
    return {'train':list(random_train_blocks(FIXTURE_STREAMS[0],8)),
            'main':queries(),'extra':queries(True),
            'symbols':['fixture-A','fixture-B','fixture-C','fixture-D'],
            'extra_symbols':['diagnostic-A','diagnostic-B','diagnostic-C','diagnostic-D']}

def cpu_now():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime

class Budget:
    def __init__(self,root,value):
        self.root=root;self.value=value;self.started=time.monotonic();self.cpu=cpu_now()
        origin=root/'budget-origin.json'
        if not origin.exists():put(origin,{'epoch':time.time()})
        self.wall_offset=time.time()-load(origin)['epoch']
        metadata=root/'generation-metadata.json'
        self.cpu_offset=load(metadata)['cpu_seconds'] if metadata.exists() else 0
        self.parent_start=metered_core.PRIMITIVE_TRANSITIONS
        self.child_transitions=0
        self.transition_offset=load(metadata)['primitive_transitions'] if metadata.exists() else 0
    def check(self):
        wall=self.wall_offset+time.monotonic()-self.started;cpu=self.cpu_offset+cpu_now()-self.cpu
        size=sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())
        if (wall>=self.value['wall_cap'] or cpu>=self.value['cpu_cap'] or size>self.value['save_cap']
            or self.transitions()>self.value.get('transition_ceiling',252928000)):
            raise ResourceStop('RESOURCE_STOP / INCOMPLETE')
        return min(self.value['wall_cap']-wall,self.value['cpu_cap']-cpu)
    def transitions(self):
        return self.transition_offset+self.child_transitions+metered_core.PRIMITIVE_TRANSITIONS-self.parent_start
    def metadata(self):
        return {'primitive_transitions':self.transitions(),'wall_seconds':self.wall_offset+time.monotonic()-self.started,'cpu_seconds':self.cpu_offset+cpu_now()-self.cpu,
            'rss_self_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'rss_child_max_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'saved_bytes':sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file()),
            'python':platform.python_version()}

@contextmanager
def public_root():
    with tempfile.TemporaryDirectory(prefix='world-lean-public-') as temporary:
        root=Path(temporary);public=root/'world_lean';public.mkdir()
        for name in PUBLIC_FILES:shutil.copyfile(REPO/'packages/world_lean'/name,public/name)
        yield root

def child(root,message,budget):
    timeout=budget.check();begun=time.perf_counter();cpu=cpu_now()
    try:
        process=subprocess.run([sys.executable,'-I',str(root/'world_lean/child_entry.py')],
            input=canonical(message),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            cwd=root,timeout=timeout,check=False,
            env={'PATH':os.environ.get('PATH',''),'HOME':str(root),'PYTHONHASHSEED':'0'})
    except subprocess.TimeoutExpired as err:raise ResourceStop('child exceeded remaining run budget') from err
    budget.check()
    if process.returncode:raise IntegrityError('child crash / INCOMPLETE: '+process.stderr.decode()[:1000])
    answer=json.loads(process.stdout)
    budget.child_transitions+=answer['primitive_transitions']
    budget.check()
    if not answer['ok']:raise IntegrityError('child schema/protocol failure: '+answer['error'])
    return answer['data'],{'wall_seconds':time.perf_counter()-begun,'cpu_seconds':cpu_now()-cpu,'primitive_transitions':answer['primitive_transitions']}

def verify_artifacts(root,record):
    for p,h in record.items():
        path=Path(p)
        if path.is_absolute() or '..' in path.parts or sha((root/path).read_bytes())!=h:
            raise IntegrityError('artifact commitment mismatch: '+p)

def generate(root=None, *, authorization=None, dry_run=False):
    if root is None:raise OwnerEvaluationAuthorizationRequired('explicit pre-fixed manifest root required')
    root=Path(root);value=verified_manifest(root,dry_run);authorize(authorization,dry_run,value)
    put(root/'generation-started.json',{'manifest':digest(value),'synthetic':dry_run})
    budget=Budget(root,value)
    try:
        # Entropy is requested only after manifest verification and authorization.
        # The synthetic branch never calls os.urandom/secrets or constructs HOLDOUT.
        master=SYNTHETIC_SEED if dry_run else os.urandom(32)
        artifacts={'private/master.bin':put(root/'private/master.bin',master,raw=True)}
        for s in range(value['replicates']):
            budget.check()
            data=synthetic_realization() if dry_run else realization(master,s)
            path=f'private/replicate-{s}.json';artifacts[path]=put(root/path,data)
        put(root/'generation.json',{'manifest':digest(value),'artifacts':artifacts,'synthetic':dry_run})
        put(root/'generation-metadata.json',budget.metadata())
        return {'status':'SYNTHETIC_GENERATED' if dry_run else 'GENERATED','artifacts':artifacts}
    except Exception as err:
        put(root/'generation-stop.json',{'status':'RESOURCE_STOP' if isinstance(err,ResourceStop) else 'STOP_INVALID',
                                       'complete':False,'reason':str(err)})
        raise

def audit_item(item,lawset):
    demos=tuple((State.parse(a),State.parse(b)) for a,b in item['demos'])
    if len(demos)!=DEMOS_PER_LAW:raise IntegrityError('demo contract')
    query=State.parse(item['query']);predictions=set()
    for recipe in lawset:
        if all(target(recipe,a)==b for a,b in demos):predictions.add(digest(target(recipe,query).record()))
    if not predictions:raise IntegrityError('generating recipe absent from consistency set')
    return len(predictions)>1

def train_all(root,value,datasets,child_root,budget):
    artifacts={};times=[];trace_digests={}
    for s,data in enumerate(datasets):
        shared=None
        for arm in (ARMS[0],*ARMS[2:]):
            request={'mode':'train','arm':arm,'checkpoints':value['checkpoints'],'symbols':data['symbols'],
                     'blocks':encode_symbols(data['train'],data['symbols'])}
            answer,timing=child(child_root,request,budget);times.append({'replicate':s,'arm':arm,**timing})
            expected=digest(request['blocks'])
            if answer['public_trace_digest']!=expected or (shared is not None and shared!=expected):
                raise IntegrityError('shared experience digest mismatch')
            shared=expected
            for b in value['checkpoints']:
                raw=base64.b64decode(answer['checkpoints_b64'][str(b)],validate=True)
                snap=json.loads(raw)
                if snap['events']!=b or (arm!='FULL' and snap['library']):
                    raise IntegrityError('snapshot event/arm contract')
                path=f'snapshots/{s}/{arm}/{b}.json';artifacts[path]=put(root/path,raw,raw=True)
                if arm=='FULL':
                    off=f'snapshots/{s}/OFF/{b}.json';artifacts[off]=put(root/off,raw,raw=True)
                    if artifacts[off]!=artifacts[path]:raise IntegrityError('FULL/OFF snapshot bytes')
            trace_digests[str(s)]=shared
    # One barrier covers ALL seeds/checkpoints/arms. No inference before this file.
    receipt={'manifest':digest(value),'snapshot_sha256':artifacts,'public_trace_digest':trace_digests}
    put(root/'snapshots-fixed.json',receipt)
    put(root/'training-metadata.json',times)
    budget.check()
    return receipt

def evaluate_all(root,value,datasets,child_root,budget,receipt):
    if load(root/'snapshots-fixed.json')!=receipt or receipt['manifest']!=digest(value):
        raise IntegrityError('missing all-snapshot barrier')
    verify_artifacts(root,receipt['snapshot_sha256'])
    artifacts={};timings=[]
    for s,data in enumerate(datasets):
        for phase in ('main','extra'):
            names=data['symbols'] if phase=='main' else data['extra_symbols']
            for b in (value['checkpoints'] if phase=='main' else value['checkpoints'][-1:]):
                for index,item in enumerate(data[phase]):
                    for arm in ARMS:
                        snap_path=f'snapshots/{s}/{arm}/{b}.json'
                        raw=(root/snap_path).read_bytes()
                        if sha(raw)!=receipt['snapshot_sha256'][snap_path]:raise IntegrityError('snapshot changed')
                        request={'mode':'infer','arm':arm,'symbols':names,
                            'snapshot_b64':base64.b64encode(raw).decode('ascii'),
                            'demos':encode_symbols(item['demos'],names),
                            'query':encode_symbols(item['query'],names)}
                        answer,timing=child(child_root,request,budget)
                        success=answer['status']=='SUBMITTED' and answer['state']==item['target']
                        # Replay legal traces independently; no prediction-only usage claim.
                        actions=[]
                        if answer['status']=='SUBMITTED':
                            library={k:v['ast'] for k,v in json.loads(raw)['library'].items()} if arm=='FULL' else {}
                            end,n,used=execute(answer['ast'],State.parse(item['query']),library,
                                               allow_calls=arm=='FULL',trace=actions)
                            if end.record()!=answer['state'] or used!=answer['used_ast']:
                                raise IntegrityError('illegal/mismatched submitted trace')
                        row={'replicate':s,'phase':phase,'b':b,'query':index,'arm':arm,
                             'snapshot_sha256':sha(raw),'success':success,'answer':answer,'actions':actions}
                        path=f'trials/{s}/{phase}/{b}/{index}/{arm}.json'
                        artifacts[path]=put(root/path,row)
                        timings.append({'trial':path,**timing})
    put(root/'evaluation-fixed.json',{'manifest':digest(value),'artifacts':artifacts})
    put(root/'evaluation-metadata.json',timings)
    return artifacts

def analyze(root,value,datasets,trial_hashes,master):
    verify_artifacts(root,trial_hashes)
    rows=[load(root/path) for path in sorted(trial_hashes)]
    expected=value['replicates']*len(ARMS)*value['law_count']*QUERIES_PER_LAW*(len(value['checkpoints'])+1)
    if len(rows)!=expected:raise IntegrityError('incomplete trial schedule')
    per_seed=[];groups={k:[0,0] for k in ('true','false','with_copy','without_copy','p0','p1','p2','p3')}
    usage=0;ambiguous=0;ambiguous_extra=0
    all_recipes=(train_recipes() if value['profile']=='SYNTHETIC_TRAIN_ONLY' else
                 recipes(tuple(TRAIN_BODY_PAIRS)+tuple(HELD_OUT_PAIR_PLAN)))
    for s,data in enumerate(datasets):
        counts={arm:[sum(r['success'] for r in rows if r['replicate']==s and r['phase']=='main' and r['arm']==arm and r['b']==b)
                     for b in value['checkpoints']] for arm in ARMS}
        per_seed.append(counts);used=False
        for item in data['main']:ambiguous+=audit_item(item,train_recipes() if value['profile']=='SYNTHETIC_TRAIN_ONLY' else all_recipes)
        for item in data['extra']:ambiguous_extra+=audit_item(item,train_recipes() if value['profile']=='SYNTHETIC_TRAIN_ONLY' else all_recipes)
        for r in rows:
            if r['replicate']!=s or r['phase']!='main' or r['arm']!='FULL':continue
            item=data['main'][r['query']]
            if r['b']==value['checkpoints'][-1]:
                p,a,b=item['recipe']
                labels=('true' if item['branch'] else 'false','with_copy' if 3 in (a,b) else 'without_copy',f'p{p}')
                for label in labels:groups[label][0]+=r['success'];groups[label][1]+=1
            if r['answer']['used_ast']:
                off=next(x for x in rows if x['replicate']==s and x['phase']=='main' and x['arm']=='OFF' and x['b']==r['b'] and x['query']==r['query'])
                used|=r['answer']['status']=='SUBMITTED' and off['answer']['status']=='SUBMITTED' and r['actions']!=off['actions']
        usage+=used
    if value['profile']=='SYNTHETIC_TRAIN_ONLY':
        result={'status':'SYNTHETIC_DRY_RUN_COMPLETE','scientific_decision':'NOT_RUN',
            'reduced_schedule':True,'counts':per_seed,'usage_seeds':usage}
    else:
        seed_rng=Stream(master,'bootstrap')
        result=scientific_decision(tuple(per_seed),groups={k:tuple(v) for k,v in groups.items()},
            ambiguous=(ambiguous,N_REPLICATES*24*QUERIES_PER_LAW),usage_seed_count=usage,
            bootstrap_seed=seed_rng.uint(1<<256))
    result.update({'main_ambiguous':ambiguous,'extra_ambiguous':ambiguous_extra,
                   'query_rows':len(rows),'full_curves':per_seed})
    put(root/'analysis.json',result)
    return result

def run(root=None, *, authorization=None, dry_run=False):
    if root is None:raise OwnerEvaluationAuthorizationRequired('explicit pre-fixed manifest root required')
    root=Path(root);value=verified_manifest(root,dry_run);authorize(authorization,dry_run,value)
    generated=load(root/'generation.json')
    if generated['manifest']!=digest(value) or generated['synthetic']!=dry_run:raise IntegrityError('generation manifest mismatch')
    verify_artifacts(root,generated['artifacts'])
    put(root/'run-started.json',{'manifest':digest(value),'synthetic':dry_run})
    budget=Budget(root,value)
    try:
        datasets=[load(root/f'private/replicate-{s}.json') for s in range(value['replicates'])]
        with public_root() as child_root:
            receipt=train_all(root,value,datasets,child_root,budget)
            verified_manifest(root,dry_run)
            verify_artifacts(root,generated['artifacts'])
            rows=evaluate_all(root,value,datasets,child_root,budget,receipt)
        result=analyze(root,value,datasets,rows,(root/'private/master.bin').read_bytes())
        verified_manifest(root,dry_run)
        budget.check();put(root/'run-metadata.json',budget.metadata())
        put(root/'complete.json',{'manifest':digest(value),'analysis_sha256':sha((root/'analysis.json').read_bytes()),'synthetic':dry_run})
        return result
    except Exception as err:
        put(root/'run-stop.json',{'status':'RESOURCE_STOP' if isinstance(err,ResourceStop) else 'STOP_INVALID',
                                'complete':False,'reason':str(err)})
        raise

def dry_run(root):
    freeze_manifest(root,dry_run=True)
    generate(root,dry_run=True)
    return run(root,dry_run=True)
