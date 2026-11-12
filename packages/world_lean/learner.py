"""Frozen bounded learner and identical-grammar inference for WORLD-LEAN-1.

Only public episodes and demonstrations enter these APIs. Evaluator recipes are absent.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations, product
from typing import Iterable
from .core import (State, Fault, READS, OPS, TOKENS, MAX_NODES, MAX_DEPTH,
                   MAX_STEPS, canonical, digest, execute, eval_predicate,
                   normalize, read, step, _validate_ast)

UPDATE_EVERY=64
MAX_LIBRARY=64
MAX_VERIFIED=128
MAX_CONSTRUCTIONS=1024
BEAM_WIDTH=8
BODY_HORIZON=6
READ_TERMS=tuple(['READ',r] for r in READS)
PREDICATES=tuple(['EQ',['READ',a],['READ',b]] for a,b in combinations(READS,2))
FIXED_SCAFFOLD=['IF',None,None,None]  # Template only; no completed predicate or branch.

# All construction orders and canonicalized serializations are part of the freeze.
def op_node(name: str, arg: list | None = None) -> list:
    return ['OP',name,arg] if name=='INSERT' else ['OP',name]

def sequence(nodes: Iterable[list]) -> list:
    nodes=list(nodes)
    return normalize(['SEQ',*nodes])

def available_nodes(s: State) -> tuple[list,...]:
    """No recipe-index/body-index cases: only 11 primitive types and typed terms."""
    choices=[op_node(op) for op in OPS if op!='INSERT']
    choices += [op_node('INSERT',t) for t in READ_TERMS if read(s,t) is not None]
    choices += [op_node('INSERT',['SYM',sym]) for sym in ('A','B','C','D')]
    # Sort on canonical bytes, not Python set/hash/unicode order.
    return tuple(sorted(choices,key=canonical))

def _sym_distance(x: tuple, y: tuple) -> int:
    # Positional symbolic mismatch; no lexical ordering of Sym values.
    return abs(len(x)-len(y))+sum(a!=b for a,b in zip(x,y))

def _guide(s: State, target: State) -> tuple[int,int,int,int]:
    # Goal-directed beam ranking is a *generic* observation-state distance;
    # no evaluator body names, program templates or recipe indices enter it.
    cb=_sym_distance(s.clipboard,target.clipboard)
    b=_sym_distance(s.buffer,target.buffer)
    pos=abs(s.cursor-target.cursor)
    selected_progress=0
    if s.selection is not None and target.clipboard and s.clipboard!=target.clipboard:
        a,h=s.selection
        part=s.buffer[min(a,h):max(a,h)]
        if len(part)<=len(target.clipboard) and target.clipboard[:len(part)]==part:
            selected_progress=8+6*len(part)
    uncleared=3 if s.selection is not None and s.clipboard==target.clipboard and target.selection is None else 0
    return (cb*20+b*3+pos-selected_progress+uncleared, cb, b, pos)

def derive_bodies(start: State, goal: State, *, max_attempts: int = MAX_CONSTRUCTIONS) -> tuple[tuple[list,...],int]:
    """8-wide deterministic beam over typed atoms; no pre-written d0/d1/d2/d3 programs.

    A construction attempt is an evaluated one-step grammar edge. Path/state
    dedup uses canonical state bytes; successes are retained across depths.
    """
    frontier=[(start,tuple())]
    solutions={}
    attempts=0
    for depth in range(1,BODY_HORIZON+1):
        next_by_state={}
        for state,path in frontier:
            for node in available_nodes(state):
                if attempts>=max_attempts: break
                attempts+=1
                arg=node[2][1] if node[1]=='INSERT' and node[2][0]=='SYM' else None
                if node[1]=='INSERT' and node[2][0]=='READ':
                    arg=read(state,node[2])
                after=step(state,(node[1],arg))
                # Explicit no-op is legal but pointless as a candidate constructor.
                if after==state: continue
                seq=path+(node,)
                key=canonical(after.record())
                if after==goal:
                    k=canonical(sequence(seq))
                    solutions[k]=seq
                # Domain-independent beam priority by observable end state.
                val=(_guide(after,goal),len(seq),canonical(sequence(seq)))
                if key not in next_by_state or val<next_by_state[key][0]:
                    next_by_state[key]=(val,after,seq)
            if attempts>=max_attempts: break
        frontier=[(s,p) for _,s,p in sorted(next_by_state.values(),key=lambda x:x[0])[:BEAM_WIDTH]]
        if not frontier or attempts>=max_attempts:break
    seqs=tuple(solutions[k] for k in sorted(solutions))
    return seqs,attempts

def _matches(ast: list, demo: tuple[State,State], library: dict[str,list] | None = None,
             *, calls: bool = True) -> bool:
    try: return execute(ast,demo[0],library,allow_calls=calls)[0]==demo[1]
    except Fault: return False

def demo_candidates(demos: tuple[tuple[State,State], ...],
                    *, max_verified: int=MAX_VERIFIED, library: dict[str,list] | None=None,
                    learned: tuple[list,...]=(),
                    frequency: dict[str,int] | None=None) -> tuple[tuple[list,...],dict]:
    """Public-demo-only candidate construction and bounded full-demo verification.

    Fixed IF scaffold tries all 5-read equalities in canonical order. Branch
    bodies come from uniform grammar beam synthesis; not a hand-written recipe.
    """
    if len(demos)!=6 or any(type(x) is not tuple or len(x)!=2 for x in demos):
        raise Fault('six public input/output demo pairs required')
    formed={}
    construction=0
    for ast in learned:
        try:
            n=normalize(ast)
            if len(canonical(n))>4096:continue
            formed[canonical(n)]=n
        except Fault:continue
    # Build single-body paths and one-branch graphs from demo groupings.
    partitions=[(None,(0,1,2,3),())]
    for pred in sorted(PREDICATES,key=canonical):
        truth=tuple(i for i,(s,_) in enumerate(demos) if eval_predicate(s,pred))
        false=tuple(i for i in range(6) if i not in truth)
        if truth and false:
            partitions.append((pred,truth,false))
    body_cache={}
    macro_bodies=tuple(['CALL',k] for k in sorted(library or {}))
    for pred,idx_true,idx_false in partitions:
        def bodies(indices: tuple[int,...]) -> tuple[list,...]:
            nonlocal construction
            if indices in body_cache:return body_cache[indices]
            paths,n=derive_bodies(*demos[indices[0]],max_attempts=MAX_CONSTRUCTIONS)
            construction+=n
            candidates=[]
            for path in paths:
                program=sequence(path)
                if all(_matches(program,demos[i]) for i in indices):
                    candidates.append(program)
            for macro in macro_bodies:
                if all(_matches(macro,demos[i],library) for i in indices):
                    candidates.append(macro)
            body_cache[indices]=tuple(sorted({canonical(x):x for x in candidates}.values(),key=canonical))[:BEAM_WIDTH]
            return body_cache[indices]
        l=bodies(idx_true)
        if pred is None:
            for a in l:formed[canonical(a)]=a
        else:
            r=bodies(idx_false)
            for a,b in product(l,r):
                graph=['IF',pred,a,b]
                try:
                    if len(canonical(graph))>4096:continue
                    if _ast_ok(graph,library):formed[canonical(graph)]=graph
                except Fault:pass
    # Candidate *verification* is capped. Rank by mismatch, MDL, canonical bytes.
    # A construction-only pre-ranking limits the checked set without goal query access.
    # STATIC-RANK constructor/reference prior is accumulated from TRAIN only.
    def constructor_features(ast: list) -> tuple[str,...]:
        if ast[0]=='CALL':return ('constructor:CALL',)
        if ast[0]=='OP':
            return ('constructor:OP','op:'+ast[1])+(('read:'+ast[2][1],) if len(ast)==3 and ast[2][0]=='READ' else ())
        if ast[0]=='IF':
            return ('constructor:IF', 'read:'+ast[1][1][1], 'read:'+ast[1][2][1])+constructor_features(ast[2])+constructor_features(ast[3])
        return ('constructor:SEQ',)+tuple(z for node in ast[1:] for z in constructor_features(node))
    if frequency is not None:
        pool=sorted(formed.values(),key=lambda a:(-sum(frequency.get(k,0) for k in constructor_features(a)),canonical(a)))
    else:
        pool=sorted(formed.values(),key=lambda a:(len(canonical(a)),canonical(a)))
    pool=pool[:max_verified]
    checked=[]
    for ast in pool:
        mismatches=sum(not _matches(ast,x,library) for x in demos)
        checked.append((mismatches,len(canonical(ast)),canonical(ast),ast))
    checked.sort(key=lambda x:x[:3])
    return tuple(v[3] for v in checked),{'construct_edges':construction,
        'formed':len(formed),'verified':len(checked),'capped':len(formed)>max_verified,
        'best_mismatches':checked[0][0] if checked else 6}

def _ast_ok(ast: list, library: dict[str,list] | None = None) -> bool:
    try:
        if _validate_ast(normalize(ast))>MAX_NODES: return False
        # A learned CALL must refer only to valid, present dependencies.
        def check(node: list, stack: tuple[str,...]) -> bool:
            if node[0]=='CALL':
                k=node[1]
                return bool(library and k in library and k not in stack and
                            check(library[k],stack+(k,)))
            if node[0]=='IF':return check(node[2],stack) and check(node[3],stack)
            if node[0]=='SEQ':return all(check(n,stack) for n in node[1:])
            return True
        return check(ast,())
    except (Fault,ValueError,RecursionError):return False

def _from_record(obj: dict) -> tuple[tuple[State,State],...]:
    if type(obj) is not dict or set(obj)!={'tag','initial','actions','observations','success','demos'}:
        raise Fault('public trace schema exact keys')
    if type(obj['tag']) is not str or type(obj['success']) is not bool:
        raise Fault('trace field types')
    if type(obj['actions']) is not list or len(obj['actions'])!=8 or type(obj['observations']) is not list or len(obj['observations'])!=9:
        raise Fault('8-step trace')
    s=State.parse(obj['initial'])
    if obj['observations'][0]!=s.record():raise Fault('observation mismatch')
    for i,raw in enumerate(obj['actions']):
        if type(raw) is not list or len(raw)!=2:raise Fault('action pair')
        s=step(s,tuple(raw))
        if obj['observations'][i+1]!=s.record():raise Fault('transition trace mismatch')
    if type(obj['demos']) is not list or len(obj['demos'])!=6:raise Fault('six TRAIN demos')
    return tuple((State.parse(a),State.parse(b)) for a,b in obj['demos'])

@dataclass
class Learner:
    # The same snapshot bytes are supplied unchanged to FULL and OFF.
    episodes: list[dict] = field(default_factory=list)
    library: dict[str,dict] = field(default_factory=dict)
    revoked: dict[str,dict] = field(default_factory=dict)
    frequency: Counter = field(default_factory=Counter)
    updates: int = 0
    events: int = 0
    update_receipts: list[dict] = field(default_factory=list)

    def add_block(self, obj: dict) -> None:
        _from_record(obj)
        if self.events+8>4096:raise Fault('TRAIN event cap')
        self.episodes.append(obj)
        self.events+=8
        for name,arg in obj['actions']:
            self.frequency['constructor:OP']+=1
            self.frequency['op:'+name]+=1
            if name=='INSERT':
                for term in READ_TERMS:
                    # Only observation-context frequencies, not evaluator recipe IDs.
                    self.frequency['read:'+term[1]]+=1 if arg==read(State.parse(obj['initial']),term) else 0
        if self.events%UPDATE_EVERY==0:self.update()

    def update(self) -> dict:
        if self.events==0 or self.events%UPDATE_EVERY or self.updates>=64:
            raise Fault('update only at 64-event boundaries')
        recent=self.episodes[-8:]
        demos=_from_record(recent[-1])
        window_digest=digest([{'actions':x['actions'],'observations':x['observations']} for x in recent])
        # Each observed interval is identified by episode-index and half-open range;
        # no evaluator goal or predicate/body index participates in synthesis.
        grouped={}
        for ep_index,episode in enumerate(recent):
            for begin in range(8):
                for end in range(begin+2,min(8,begin+6)+1):
                    shape=tuple(x[0] for x in episode['actions'][begin:end])
                    grouped.setdefault(shape,[]).append((ep_index,begin,end))
        proposals={}
        constructions=0
        for shape in sorted(grouped):
            entries=grouped[shape]
            for j in range(len(entries)):
                for i in range(j):
                    if constructions>=MAX_CONSTRUCTIONS:break
                    ep_a,lo_a,hi_a=entries[i]
                    ep_b,lo_b,hi_b=entries[j]
                    if ep_a==ep_b:continue
                    constructions+=1
                    a,b=recent[ep_a],recent[ep_b]
                    states_a=[State.parse(x) for x in a['observations']]
                    states_b=[State.parse(x) for x in b['observations']]
                    nodes=[]
                    for offset,name in enumerate(shape):
                        x=a['actions'][lo_a+offset][1]
                        y=b['actions'][lo_b+offset][1]
                        if name=='INSERT':
                            common=[term for term in READ_TERMS
                                    if read(states_a[lo_a+offset],term)==x
                                    and read(states_b[lo_b+offset],term)==y]
                            if common:arg=list(common[0])
                            elif x==y:arg=['SYM',x]
                            else:break
                            nodes.append(op_node(name,arg))
                        else:nodes.append(op_node(name))
                    if len(nodes)!=len(shape):continue
                    ast=sequence(nodes)
                    key=canonical(ast)
                    witnesses=[digest({'tag':a['tag'],'range':[lo_a,hi_a],
                         'actions':a['actions'][lo_a:hi_a]}),
                         digest({'tag':b['tag'],'range':[lo_b,hi_b],
                         'actions':b['actions'][lo_b:hi_b]})]
                    if key not in proposals:proposals[key]=(ast,witnesses,shape)
                if constructions>=MAX_CONSTRUCTIONS:break
            if constructions>=MAX_CONSTRUCTIONS:break
        # At most 128 fresh candidates checked in this update, ordered by
        # canonical program size then bytes. Larger libraries are not a reward.
        checked=[]
        for key,(ast,witness,shape) in sorted(proposals.items(),key=lambda x:(len(x[0]),x[0]))[:MAX_VERIFIED]:
            if not _ast_ok(ast):continue
            mismatches=sum(not _matches(ast,pair) for pair in demos)
            mid=digest(ast)[:16]
            encoded_call=len(canonical(['CALL',mid]))
            description=len(canonical(ast))
            if encoded_call>=description:continue
            checked.append((mismatches,description+encoded_call,key,ast,witness,shape))
        checked.sort(key=lambda x:x[:3])
        for mismatch,mdl,key,ast,witness,shape in checked:
            mid=digest(ast)[:16]
            if mid not in self.library:
                self.library[mid]={'ast':ast,'source_digest':window_digest,
                    'constructor':'paired-trace-window-antiunification',
                    'dependencies':[],'witnesses':witness,
                    'counterexamples':[],'tag':recent[-1]['tag'],
                    'rank':[mismatch,mdl,key.decode('utf-8')]}
        # Candidate branches are constructed only from previously acquired
        # macros and general read-term equalities that split six TRAIN demos.
        macro_lib={k:v['ast'] for k,v in self.library.items()}
        graph_constructed=0
        graph_checked=0
        for predicate in sorted(PREDICATES,key=canonical):
            if graph_constructed>=MAX_CONSTRUCTIONS-constructions:break
            if not (any(eval_predicate(a,predicate) for a,_ in demos) and
                    any(not eval_predicate(a,predicate) for a,_ in demos)):
                continue
            for then_id in sorted(macro_lib):
                for else_id in sorted(macro_lib):
                    if then_id==else_id:continue
                    if graph_constructed>=MAX_CONSTRUCTIONS-constructions or graph_checked>=MAX_VERIFIED-len(checked):break
                    graph_constructed+=1
                    candidate=['IF',predicate,['CALL',then_id],['CALL',else_id]]
                    if not _ast_ok(candidate,macro_lib):continue
                    graph_checked+=1
                    mismatch=sum(not _matches(candidate,pair,macro_lib) for pair in demos)
                    if mismatch!=0:continue
                    gid=digest(candidate)[:16]
                    self.library[gid]={'ast':candidate,'source_digest':window_digest,
                        'constructor':'TRAIN-read-comparison+acquired-macros',
                        'dependencies':[then_id,else_id],
                        'witnesses':[digest([x.record(),y.record()]) for x,y in demos],
                        'counterexamples':[],'tag':recent[-1]['tag'],
                        'rank':[0,len(canonical(candidate)),canonical(candidate).decode('utf-8')]}
                if graph_constructed>=MAX_CONSTRUCTIONS-constructions or graph_checked>=MAX_VERIFIED-len(checked):break
        # Revalidate observed deterministic effects rather than calling a
        # standalone fragment 'wrong' just because it isn't a whole law.
        for mid in sorted(list(self.library)):
            entry=self.library[mid]
            if entry['constructor']!='paired-trace-window-antiunification':continue
            ast=entry['ast']
            if ast[0]=='OP':continue
            if ast[0]!='SEQ':continue
            names=tuple(node[1] for node in ast[1:])
            invalid=[]
            for ep in recent:
                acts=ep['actions']
                states=[State.parse(x) for x in ep['observations']]
                for start in range(9-len(names)):
                    if tuple(x[0] for x in acts[start:start+len(names)])!=names:continue
                    try:found=execute(ast,states[start])[0]
                    except Fault:found=None
                    if found!=states[start+len(names)]:
                        invalid.append(digest([ep['tag'],start,len(names)]))
            if invalid:
                entry['counterexamples'].extend(sorted(invalid))
                self.revoked[mid]=entry
                del self.library[mid]
        # Invalidated dependencies cannot survive through cached graph calls.
        while True:
            invalid=[k for k,v in self.library.items() if any(dep not in self.library for dep in v['dependencies'])]
            if not invalid:break
            for k in sorted(invalid):
                self.revoked[k]=self.library[k]
                del self.library[k]
        if len(self.library)>MAX_LIBRARY:
            keys=sorted(self.library,key=lambda k:(self.library[k]['rank'],k))[:MAX_LIBRARY]
            self.library={k:self.library[k] for k in keys}
            while True:
                invalid=[k for k,v in self.library.items() if any(dep not in self.library for dep in v['dependencies'])]
                if not invalid:break
                for k in sorted(invalid):
                    self.revoked[k]=self.library[k]
                    del self.library[k]
        self.updates+=1
        receipt={'update':self.updates,'events':self.events,'window_digest':window_digest,
                 'constructed':constructions+graph_constructed,
                 'verified':len(checked)+graph_checked,
                 'library_size':len(self.library),'candidate_proposals':len(proposals),
                 'graph_constructed':graph_constructed}
        self.update_receipts.append(receipt)
        return receipt

    def snapshot(self) -> bytes:
        return canonical({'version':'WORLD-LEAN-1/snapshot/1',
            'events':self.events,'updates':self.updates,'episodes':self.episodes,
            'library':{k:self.library[k] for k in sorted(self.library)},
            'revoked':{k:self.revoked[k] for k in sorted(self.revoked)},
            'frequency':{k:self.frequency[k] for k in sorted(self.frequency)},
            'update_receipts':self.update_receipts})

def _snap(snapshot: bytes) -> dict:
    import json
    value=json.loads(snapshot)
    if type(value) is not dict or value.get('version')!='WORLD-LEAN-1/snapshot/1' or canonical(value)!=snapshot:
        raise Fault('noncanonical snapshot')
    return value

def _lookups(snapshot: dict, demos: tuple[tuple[State,State],...], query: State) -> list:
    # Encoder: 16 buffer +16 clipboard slots + cursor,anchor,head =35.
    def dist(a: State,b: State) -> int:
        symbol_d=sum((a.buffer[i] if i<len(a.buffer) else None)!=(b.buffer[i] if i<len(b.buffer) else None) for i in range(16))
        symbol_d+=sum((a.clipboard[i] if i<len(a.clipboard) else None)!=(b.clipboard[i] if i<len(b.clipboard) else None) for i in range(16))
        for ai,bi in ((a.cursor,b.cursor),
                      (a.selection[0] if a.selection is not None else None,b.selection[0] if b.selection is not None else None),
                      (a.selection[1] if a.selection is not None else None,b.selection[1] if b.selection is not None else None)):
            symbol_d += (0 if ai==bi else 16 if ai is None or bi is None else abs(ai-bi))
        return symbol_d
    # All 512 TRAIN blocks retained, distance from fixed six public demos.
    grouped=[]
    for ep in snapshot['episodes']:
        ed=tuple((State.parse(a),State.parse(b)) for a,b in ep['demos'])
        lawdist=sum(min(dist(a,c)+dist(b,d) for c,d in ed) for a,b in demos)
        pre=State.parse(ep['initial'])
        grouped.append((lawdist,dist(pre,query),digest(ep['initial']),ep))
    if not grouped:return []
    best=min(x[0] for x in grouped)
    nearest=[x for x in grouped if x[0]==best]
    nearest_tags={x[-1]['tag'] for x in nearest}
    # Deterministic nearest TRAIN tag from the entire observed demo catalog,
    # then nearest *successful* trace in that selected law only.
    best_tag=min(nearest_tags)
    return sorted((x for x in grouped if x[-1]['tag']==best_tag and x[-1]['success']), key=lambda x:x[1:3])

def infer(snapshot: bytes, arm: str, demos: tuple[tuple[State,State],...], query: State) -> dict:
    if arm not in ('FULL','OFF','STATIC-RANK','LOOKUP'):raise Fault('arm')
    data=_snap(snapshot)
    if arm=='LOOKUP':
        choices=_lookups(data,demos,query)
        if not choices:return {'status':'ABSTAIN','checked':0,'simulated':0,'used_ast':False}
        ep=choices[0][-1]
        seq=[]
        states=[State.parse(x) for x in ep['observations']]
        for i,(name,arg) in enumerate(ep['actions']):
            if name=='INSERT':
                terms=[list(t) for t in READ_TERMS if read(states[i],t)==arg]
                seq.append(op_node(name,terms[0] if terms else ['SYM',arg]))
            else:seq.append(op_node(name))
        ast=sequence(seq)
        # No evaluator target, no extra training at query time.
        try: end,count,used=execute(ast,query)
        except Fault:return {'status':'FAULT','checked':0,'simulated':0,'used_ast':False}
        return {'status':'SUBMITTED','state':end.record(),'ast':ast,
                'checked':0,'simulated':count,'used_ast':False}
    library={k:v['ast'] for k,v in data['library'].items()} if arm=='FULL' else {}
    learned=tuple(['CALL',k] for k in sorted(library)) if arm=='FULL' else ()
    # OFF and FULL receive exactly the same snapshot bytes. OFF cannot expand CALL.
    candidates,stats=demo_candidates(demos,library=library,learned=learned,
        frequency=data['frequency'] if arm=='STATIC-RANK' else None)
    simulations=0; rejected=0
    ranked=[]
    for ast in candidates:
        if arm=='OFF' and ast[0]=='CALL':raise AssertionError('OFF leak')
        mismatches=0
        for initial,goal in demos:
            try:
                end,n,_=execute(ast,initial,library,allow_calls=arm!='OFF')
                simulations+=n
                mismatches+=end!=goal
            except Fault:
                mismatches+=1
        if mismatches:rejected+=1
        ranked.append((mismatches,len(canonical(ast)),canonical(ast),ast))
    ranked.sort(key=lambda x:x[:3])
    passing=next((x[-1] for x in ranked if x[0]==0),None)
    if passing is None:
        return {'status':'ABSTAIN','checked':len(candidates),'simulated':simulations,
                'used_ast':False,'rejected':rejected,'generation':stats}
    try:end,n,used=execute(passing,query,library,allow_calls=arm!='OFF')
    except Fault:return {'status':'FAULT','checked':len(candidates),'simulated':simulations,
                         'used_ast':False,'rejected':rejected,'generation':stats}
    return {'status':'SUBMITTED','state':end.record(),'ast':passing,
            'checked':len(candidates),'simulated':simulations+n,
            'used_ast':used,'rejected':rejected,'generation':stats}
