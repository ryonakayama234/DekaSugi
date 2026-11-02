"""REP004 disclosed, finite, public-evidence-only concept activation experiment.

No historical benchmark access and no neural/LLM use. This is a research prototype.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import time
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

N = 4
VERSION = 'rep004/executable-concept/1'
ACTIONS = tuple([('pulse', i, None) for i in range(N)] + [('set', i, v) for i in range(N) for v in (0, 1)])
ARMS = ('LQ', 'LA', 'LR', 'ER', 'FA', 'FX', 'BODY-OFF', 'STATIC-MACRO')
BUDGETS = (0, 1, 2, 4, 8)
PERMS = tuple(itertools.permutations(range(N)))
EDGES = tuple([(i,j,-1,-1) for i in range(N) for j in range(N) if i!=j] +
              [(i,j,k,v) for i in range(N) for j in range(N) for k in range(N)
               for v in (0,1) if i!=j and k not in (i,j)])


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def validate_action(a):
    if type(a) is not tuple or len(a)!=3 or a not in ACTIONS:
        raise ValueError('illegal action')


def step(state, action, edges):
    """Trusted pure semantics; simultaneous XOR updates from PRE-action state."""
    validate_action(action)
    if type(state) is not int or not (0 <= state < 16):
        raise ValueError('invalid state')
    kind,i,v=action
    if kind=='set':
        return (state & ~(1<<i)) | (v<<i)
    out=state
    for s,t,g,b in edges:
        if s==i and (g==-1 or ((state>>g)&1)==b):
            out ^= 1<<t
    return out


@lru_cache(maxsize=8192)
def sig(edges):
    return bytes(step(s, ('pulse',i,None),edges) for s in range(16) for i in range(N))


def relabel(edges,perm):
    return tuple(sorted((perm[s],perm[t],-1 if g<0 else perm[g],b) for s,t,g,b in edges))


@lru_cache(maxsize=8192)
def family(edges):
    return min(sig(relabel(edges,p)) for p in PERMS).hex()


def motif(edges):
    if len(edges)<2: return 'ATOMIC'
    a,b=edges
    if a[1]==b[0] or b[1]==a[0]: return 'CHAIN'
    if a[0]==b[0]: return 'FANOUT'
    if a[1]==b[1]: return 'FANIN'
    return 'OTHER'


@lru_cache(maxsize=1)
def catalog():
    """Finite oracle catalog for mechanics and symmetric fixed-model baselines.
    The learner sees only predictions, NEVER the generating model for a world.
    """
    by_sig={}
    for edges in itertools.chain(((),), ((e,) for e in EDGES), itertools.combinations(EDGES,2)):
        key=sig(edges)
        by_sig.setdefault(key,edges)
    return tuple(sorted(by_sig.values(),key=lambda e:sig(e)))


@lru_cache(maxsize=1)
def worlds_by_family():
    d={}
    for edges in catalog():
        f=family(edges)
        d.setdefault(f,edges)
    return d


def study_manifest():
    """Source split fixed by family content, never by truth-dependent score.
    Eval pools are distinct SEMANTIC families, not renamed replicas.
    """
    by=worlds_by_family()
    groups={k:[] for k in ('CHAIN','FANOUT','FANIN','OTHER','ATOMIC')}
    for f,e in sorted(by.items()):groups[motif(e)].append(f)
    # 10 CHAIN train, 22 non-chain train. 12 novel CHAIN and 12 novel non-chain.
    tc=groups['CHAIN'][:10]
    nc=sorted(groups['FANOUT']+groups['FANIN']+groups['OTHER'])
    tn=nc[:22]
    composition=groups['CHAIN'][10:22]
    other=[f for f in nc if f not in tn][:12]
    train=tuple(tc+tn)
    seen=tuple(train[:12])
    assert len(train)==32 and len(composition)==12 and len(other)==12
    assert len(set(train)|set(composition)|set(other))==56
    assert not(set(train)&set(composition) or set(train)&set(other) or set(composition)&set(other))
    m={'version':VERSION,'train_families':list(train),'seen':list(seen),
       'composition':list(composition),'unseen':list(other),
       'family_count':len(by),'candidate_semantics':len(catalog()),
       'train_worlds':64,'eval_worlds':48}
    return {**m,'digest':digest(m)}


@dataclass(frozen=True)
class World:
    """Host-only secret. Must never be passed to learn, bind or plan."""
    edges:tuple
    public_ids:tuple
    family_id:str
    seed:int


class Session:
    def __init__(self,world):
        if type(world) is not World:raise ValueError('host-only world')
        self._world=world
        self.state=0
        self.trace=[]

    def public(self):
        return {'ids':list(self._world.public_ids),'state':self.state,'spent':len(self.trace)}

    def apply(self,action):
        before=self.state
        after=step(before,action,self._world.edges)
        self.trace.append({'before':before,'action':list(action),'after':after,
                           'ordinal':len(self.trace)+1,'cost':1})
        self.state=after
        return self.trace[-1]


def world_for(fam,instance):
    e=worlds_by_family()[fam]
    rng=random.Random(int(digest([fam,instance])[:16],16))
    p=list(range(N));rng.shuffle(p)
    ids=tuple('obj_'+format(rng.getrandbits(48),'012x') for _ in range(N))
    return World(relabel(e,p),ids,fam,instance)


def ood_world(instance):
    rng=random.Random(100098+instance)
    # A three-edge directed chain; guaranteed out of <=2-edge catalog by signature.
    p=list(range(N));rng.shuffle(p)
    e=((p[0],p[1],-1,-1),(p[1],p[2],-1,-1),(p[2],p[3],-1,-1))
    ids=tuple('obj_'+format(rng.getrandbits(48),'012x') for _ in range(N))
    assert sig(e) not in {sig(x) for x in catalog()}
    return World(e,ids,'OOD-'+str(instance),instance)


def validate_trace(rows):
    if type(rows) is not list:raise ValueError('trace must be a list')
    previous=0
    for idx,r in enumerate(rows,1):
        if type(r) is not dict or set(r)!= {'before','action','after','ordinal','cost'}:
            raise ValueError('noncanonical trace')
        if type(r['ordinal']) is not int or r['ordinal']!=idx or type(r['cost']) is not int or r['cost']!=1:
            raise ValueError('uncharged event')
        if type(r['before']) is not int or r['before']!=previous or type(r['after']) is not int or r['after'] not in range(16):
            raise ValueError('broken trace')
        a=r['action']
        if type(a) is not list:raise ValueError('invalid action encoding')
        validate_action(tuple(a))
        if a[0]=='set' and step(previous,tuple(a),())!=r['after']:
            raise ValueError('forged set receipt')
        previous=r['after']
    return previous


def consistent(rows, meter=None):
    validate_trace(rows)
    events=[r for r in rows if r['action'][0]=='pulse']
    matches=[]
    for edges in catalog():
        s=sig(edges)
        if meter is not None:meter['model_checks']+=len(events)
        if all(s[4*r['before']+r['action'][1]]==r['after'] for r in events):
            matches.append(edges)
    return matches


def paid_train(world):
    session=Session(world)
    for state in (0,1,2,4,8):
        for source in range(4):
            for i in range(4):session.apply(('set',i,(state>>i)&1))
            session.apply(('pulse',source,None))
    survivors=consistent(session.trace)
    signatures={sig(e) for e in survivors}
    if len(signatures)!=1: raise ValueError('training evidence did not identify dynamics')
    return survivors[0],session.trace


# A learned concept is an executable single relation, parameterized by three roles.
# Unlike REP003's description, the interpreter below reads the persisted AST.
def concept_ast(edge):
    _,_,g,v=edge
    return {'op':'toggle_if_pulse','source':'source','target':'target',
            'guard':{'op':'always'} if g==-1 else {'op':'state_is','role':'guard','value':v}}


def validate_body(body):
    if type(body) is not dict or set(body)!= {'ast','body_hash','support','positive','negative','status'}:
        raise ValueError('body schema')
    a=body['ast']
    if type(a) is not dict or 'op' not in a:raise ValueError('untrusted AST')
    if a['op']=='toggle_if_pulse':
        if set(a)!= {'op','source','target','guard'} or a['source']!='source' or a['target']!='target':
            raise ValueError('untrusted AST')
        g=a['guard']
        if type(g) is not dict or (g!={'op':'always'} and not (set(g)=={'op','role','value'} and g['op']=='state_is' and g['role']=='guard' and type(g['value']) is int and g['value'] in (0,1))):
            raise ValueError('invalid guard AST')
    elif a['op']=='parallel_xor':
        if a!=compose_ast(a.get('shape')):raise ValueError('invalid composition AST')
    else:raise ValueError('untrusted AST operation')
    if type(body['support']) is not int or body['support']<3 or type(body['positive']) is not list or not body['positive'] or type(body['negative']) is not list or body['status']!='candidate':
        raise ValueError('body provenance')
    if type(body['body_hash']) is not str or body['body_hash']!=digest(a):raise ValueError('altered AST')


def execute_body(body, state, action, binding):
    """Interpreter only; no fixed-model catalog, no callable from untrusted JSON."""
    validate_body(body)
    if type(binding) is not dict or set(binding)!={'source','target','guard'} or any(type(v) is not int or v not in range(N) for v in binding.values()):
        raise ValueError('bad role binding')
    if len(set(binding.values()))!=3:raise ValueError('non-injective roles')
    validate_action(action)
    if type(state) is not int or state not in range(16):raise ValueError('bad state')
    a=body['ast']
    if action[0]!='pulse' or action[1]!=binding[a['source']]:return state
    g=a['guard']
    if g['op']=='state_is' and ((state>>binding[g['role']])&1)!=g['value']:return state
    return state^(1<<binding[a['target']])


def compose_ast(shape):
    if shape not in ('CHAIN','FANOUT','FANIN','OTHER'):
        raise ValueError('invalid learned motif')
    # Role slots are bound using inferred PUBLIC models at USE time; all effects
    # share a simultaneous pre-state. Learning selects which motif to retain.
    return {'op':'parallel_xor','shape':shape,'effects':[
        {'op':'toggle_if_pulse','source':'s0','target':'t0','guard':'g0'},
        {'op':'toggle_if_pulse','source':'s1','target':'t1','guard':'g1'}]}


def execute_composition(body,state,action,edges):
    validate_body(body)
    if body['ast']['op']!='parallel_xor' or len(edges)!=2 or motif(edges)!=body['ast']['shape']:
        raise ValueError('bad composition binding')
    out=state
    for effect,e in zip(body['ast']['effects'],edges):
        if effect['op']!='toggle_if_pulse':raise ValueError('invalid macro')
        i,j,g,v=e
        if action[0]=='pulse' and action[1]==i and (g<0 or (state>>g)&1==v):
            out ^=1<<j
    return out


def sleep_from_public_traces(traces):
    """No World, generator family, seed or secret rule is accepted here."""
    if type(traces) is not list:raise ValueError('public traces required')
    manifest=study_manifest()
    train_worlds=len(traces)
    if train_worlds not in (0,3,8,16,32,64):raise ValueError('unsupported TRAIN size')
    observations={}; episodes=[]; receipts=[]
    for trace in traces:
        survivors=consistent(trace)
        if len({sig(e) for e in survivors})!=1:raise ValueError('unidentified TRAIN semantics')
        edges=survivors[0]
        fam=family(edges)  # Inferred from public trace, not source manifest.
        receipt=digest(trace); receipts.append(receipt)
        episodes.append({'family':family(edges),'receipt':receipt,'edges':[list(e) for e in edges]})
        # Positive: a witnessed pulse toggled this target when guard held.
        # Negative: it did not toggle this target when guard did not hold,
        # with NO confounding second edge active on the same target.
        for e in edges:
            a=concept_ast(e);key=digest(a)
            o=observations.setdefault(key,{'ast':a,'families':set(),'positive':set(),'negative':set()})
            o['families'].add(fam)
            for r in trace:
                if r['action'][0]!='pulse' or r['action'][1]!=e[0]:continue
                active=(e[2]<0 or ((r['before']>>e[2])&1)==e[3])
                if any(z is not e and z[1]==e[1] and z[0]==e[0] and (z[2]<0 or (r['before']>>z[2])&1==z[3]) for z in edges):
                    continue
                if active and (r['before']^r['after'])&(1<<e[1]):o['positive'].add(digest(r))
                if not active and not ((r['before']^r['after'])&(1<<e[1])):o['negative'].add(digest(r))
        if len(edges)==2:
            a=compose_ast(motif(edges));key=digest(a)
            o=observations.setdefault(key,{'ast':a,'families':set(),'positive':set(),'negative':set()})
            o['families'].add(fam);o['positive'].add(receipt)
    library=[]
    for key,o in sorted(observations.items()):
        distinct=len(o['families'])
        if distinct>=3 and o['positive']:
            body={'ast':o['ast'],'body_hash':key,'support':distinct,
                  'positive':sorted(o['positive']),'negative':sorted(o['negative']), 'status':'candidate'}
            validate_body(body);library.append(body)
    raw={'schema':VERSION,'manifest_digest':manifest['digest'],'train_worlds':train_worlds,
         'paid_actions':train_worlds*100,'receipt_digest':digest(receipts),
         'library':library,'episodes':episodes,
         'distinct_train_families':len({e['family'] for e in episodes})}
    return {**raw,'digest':digest(raw)}


def learn(train_worlds=64):
    """Trusted outer host captures observations, then discards World objects."""
    if type(train_worlds) is not int or train_worlds not in (0,3,8,16,32,64):
        raise ValueError('unsupported TRAIN size')
    families=study_manifest()['train_families']
    traces=[]
    for i in range(train_worlds):
        world=world_for(families[i%32],i)
        session=Session(world)
        for state in (0,1,2,4,8):
            for source in range(4):
                for k in range(4):session.apply(('set',k,(state>>k)&1))
                session.apply(('pulse',source,None))
        traces.append(session.trace)
    return sleep_from_public_traces(traces)


def validate_snapshot(s):
    if type(s) is not dict or set(s)!={'schema','manifest_digest','train_worlds','paid_actions','receipt_digest','library','episodes','distinct_train_families','digest'} or s['schema']!=VERSION:
        raise ValueError('snapshot schema')
    if type(s['train_worlds']) is not int or s['train_worlds'] not in (0,3,8,16,32,64) or s['paid_actions']!=s['train_worlds']*100:
        raise ValueError('invalid TRAIN provenance')
    if s['manifest_digest']!=study_manifest()['digest'] or type(s['library']) is not list or type(s['episodes']) is not list or len(s['episodes'])!=s['train_worlds']:
        raise ValueError('manifest mismatch')
    for b in s['library']:validate_body(b)
    if type(s['digest']) is not str or s['digest']!=digest({k:v for k,v in s.items() if k!='digest'}):
        raise ValueError('snapshot checksum')
    return s


def save(snapshot,path):
    from pathlib import Path
    validate_snapshot(snapshot)
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(canonical(snapshot)+'\n',encoding='utf-8')


def load(path):
    from pathlib import Path
    return validate_snapshot(json.loads(Path(path).read_text(encoding='utf-8')))


@lru_cache(maxsize=128)
def _edge_execution_matches(guard_op,guard_value,edge_guard,edge_value):
    # Cache is based on pure AST semantics, never hidden truth / public IDs.
    ast=concept_ast((0,1,2,guard_value)) if guard_op=='state_is' else concept_ast((0,1,-1,-1))
    body={'ast':ast,'body_hash':digest(ast),'support':3,
          'positive':['synthetic-fixture'],'negative':[],'status':'candidate'}
    e=(0,1,edge_guard,edge_value)
    return all(execute_body(body,state,('pulse',0,None),{'source':0,'target':1,'guard':2})==
               step(state,('pulse',0,None),(e,)) for state in range(16))


@lru_cache(maxsize=8192)
def _composition_equivalent(shape,edges):
    ast=compose_ast(shape)
    body={'ast':ast,'body_hash':digest(ast),'support':3,
          'positive':['trusted-schema-check'],'negative':[],'status':'candidate'}
    return all(execute_composition(body,s,('pulse',i,None),edges)==step(s,('pulse',i,None),edges)
               for s in (0,1,3,7,15) for i in range(4))


def concept_matches(snapshot,edges,metrics=None):
    """Pure executed AST semantics -> prior weight. No fixed MODELS alias.
    The full composition motif is also executed as an ordered concurrent XOR.
    """
    covered=0
    for e in edges:
        for body in snapshot['library']:
            ast=body['ast']
            if ast['op']!='toggle_if_pulse':continue
            if metrics is not None:metrics['body_invocations']+=1
            g=ast['guard'];v=g.get('value',-1)
            if _edge_execution_matches(g['op'],v,e[2],e[3]):
                covered+=1;break
    if len(edges)==2:
        for b in snapshot['library']:
            if b['ast']['op']=='parallel_xor' and b['ast']['shape']==motif(edges):
                if metrics is not None:metrics['body_invocations']+=1
                if _composition_equivalent(b['ast']['shape'],edges):
                    covered+=2;break
    return covered


@lru_cache(maxsize=1)
def static_macro_library():
    asts=[concept_ast((0,1,-1,-1)),concept_ast((0,1,2,0)),concept_ast((0,1,2,1))]
    asts.extend(compose_ast(shape) for shape in ('CHAIN','FANIN','FANOUT','OTHER'))
    return [{'ast':a,'body_hash':digest(a),'support':3,'positive':['preinstalled-static'],
             'negative':[],'status':'candidate'} for a in asts]


def weights_for(models,snapshot,arm,metrics):
    if arm in ('FA','FX','BODY-OFF','LA') or not snapshot['library']:
        return [1.0]*len(models)
    if arm=='LR':
        counts=Counter(e['family'] for e in snapshot['episodes'])
        return [1.0+counts.get(family(x),0) for x in models]
    if arm=='ER':
        # Real episode retrieval: compare candidate public semantics to stored
        # inferred TRAIN semantics, invariant to variable renaming.
        ep={e['family'] for e in snapshot['episodes']}
        return [2.0 if family(x) in ep else 1.0 for x in models]
    if arm=='STATIC-MACRO':
        fixed={'library':static_macro_library()}
        return [1.0+3.0*concept_matches(fixed,x,metrics) for x in models]
    return [1.0+3.0*concept_matches(snapshot,x,metrics) for x in models]


def groups_at(models,state,action):
    return [step(state,action,e) for e in models]


def gini(values,weights):
    counts={}
    total=sum(weights)
    if total<=0:return 0.0
    for y,w in zip(values,weights):counts[y]=counts.get(y,0)+w
    return 1-sum((v/total)**2 for v in counts.values())


def choose(state,models,weights,remain,meter,arm):
    if not models or remain<=0:return None
    if arm=='FX':return ('pulse',meter['actions']%4,None)
    # A real paid 2-step plan: score complete visible observation trace.
    # Set first, then pulse. Never treat a set as free; replanning is adaptive.
    best=(-1.0,0)
    for idx,a in enumerate(ACTIONS):
        if a[0]=='set' and step(state,a,())==state:continue
        o1=groups_at(models,state,a)
        meter['model_checks']+=len(models)
        score=gini(o1,weights)
        if score>best[0]+1e-12:best=(score,idx)
        if remain>=2 and a[0]=='set':
            for b in ACTIONS[:4]:
                o2=[(x,step(x,b,m)) for x,m in zip(o1,models)]
                meter['model_checks']+=len(models)
                val=gini(o2,weights)/2
                if val>best[0]+1e-12:best=(val,idx)
    return ACTIONS[best[1]]


def committed_use(snapshot,world,arm,budget):
    validate_snapshot(snapshot)
    if type(world) is not World or arm not in ARMS or type(budget) is not int or budget not in BUDGETS:
        raise ValueError('invalid use arguments')
    session=Session(world)
    meter={'actions':0,'model_checks':0,'body_invocations':0}
    t0=time.process_time()
    for _ in range(budget):
        h=consistent(session.trace,meter)
        if not h:break
        q=weights_for(h,snapshot,arm,meter)
        action=choose(session.state,h,q,budget-len(session.trace),meter,arm)
        if action is None:break
        session.apply(action)
        meter['actions']+=1
    h=consistent(session.trace,meter)
    status='COMMITTED' if h else 'ABSTAIN'
    predarm='LQ' if arm in ('LQ','LA') else arm
    p=weights_for(h,snapshot,predarm,meter)
    pred=h[max(range(len(h)),key=lambda i:(p[i],-i))] if h else None
    commit={'schema':VERSION,'arm':arm,'budget':budget,'public_ids':list(world.public_ids),
            'trace':session.trace,'status':status,'predicted_edges':[list(e) for e in pred] if pred is not None else None,
            'snapshot_digest':snapshot['digest'],'meter':meter}
    return {**commit,'commit_digest':digest(commit),'cpu_seconds':round(time.process_time()-t0,6)}


def audit(world,commit):
    if type(commit) is not dict or commit.get('commit_digest')!=digest({k:v for k,v in commit.items() if k not in ('commit_digest','cpu_seconds')}):
        raise ValueError('prediction not committed')
    if commit['status']!='COMMITTED':return 0
    predicted=tuple(tuple(e) for e in commit['predicted_edges'])
    return sum(step(s,('pulse',i,None),predicted)==step(s,('pulse',i,None),world.edges)
               for s in range(16) for i in range(4))


def evaluate(snapshot):
    """Disclosed only, deterministic scored trial corpus. Never old/private splits."""
    manifest=study_manifest();rows=[]
    for stratum,key in [('SEEN_ROLEBLIND','seen'),('UNSEEN_COMPOSITION','composition'),
                        ('UNSEEN_IN_GRAMMAR','unseen'),('OUT_OF_GRAMMAR',None)]:
        for i in range(12):
            world=ood_world(i) if key is None else world_for(manifest[key][i],1000+i)
            for arm in ARMS:
                for budget in BUDGETS:
                    c=committed_use(snapshot,world,arm,budget)
                    n=audit(world,c)
                    rows.append({'stratum':stratum,'family':world.family_id,'index':i,'arm':arm,
                                 'budget':budget,'exact':n,'score':n/64 if c['status']=='COMMITTED' else 0,
                                 'status':c['status'],'actions':c['meter']['actions'],
                                 'model_checks':c['meter']['model_checks'],
                                 'body_invocations':c['meter']['body_invocations'],
                                 'cpu_seconds':c['cpu_seconds'],'trace_actions':[r['action'] for r in c['trace']],
                                 'commit_digest':c['commit_digest']})
    summaries={}
    for st in ('SEEN_ROLEBLIND','UNSEEN_COMPOSITION','UNSEEN_IN_GRAMMAR','OUT_OF_GRAMMAR'):
        summaries[st]={arm:sum(r['score'] for r in rows if r['stratum']==st and r['arm']==arm)/(12*len(BUDGETS)) for arm in ARMS}
    x={'schema':VERSION,'snapshot_digest':snapshot['digest'],'manifest_digest':manifest['digest'],
       'rows':rows,'summary':summaries,'record_count':len(rows)}
    return {**x,'digest':digest(x)}


def activation_fixture(snapshot):
    """Development-only paid-history gate, never a scored study world."""
    validate_snapshot(snapshot)
    w=world_for(study_manifest()['composition'][0],508)
    session=Session(w)
    for a in [('pulse',0,None),('pulse',1,None)]:session.apply(a)
    h=consistent(session.trace)
    ma={'actions':len(session.trace),'model_checks':0,'body_invocations':0}
    mb={'actions':len(session.trace),'model_checks':0,'body_invocations':0}
    a=choose(session.state,h,weights_for(h,snapshot,'LQ',ma),2,ma,'LQ')
    b=choose(session.state,h,weights_for(h,snapshot,'LA',mb),2,mb,'LA')
    return {'type':'development-only-mechanism-gate','paid_conditioning':len(session.trace),
            'remaining_candidates':len(h),'LQ_first_action':list(a),'LA_first_action':list(b),
            'differs':a!=b,'body_invocations':ma['body_invocations'],
            'transcript_digest':digest(session.trace)}