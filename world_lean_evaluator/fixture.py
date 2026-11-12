"""Synthetic TRAIN-only engineering fixtures; no formal seed/holdout materialization."""
from __future__ import annotations
import hashlib
import itertools
from dataclasses import dataclass
from packages.world_lean.core import State, TOKENS, SYMS, Session, read, step, digest

FIXTURE_STREAMS=('artificial-fixture-A','artificial-fixture-B','artificial-fixture-C','artificial-fixture-D')
TRAIN_PAIRS=((0,1),(1,2),(2,3))
DRAW_LIMIT=4096

@dataclass(frozen=True)
class Recipe:
    condition: int
    then_body: int
    else_body: int


def train_recipes() -> tuple[Recipe,...]:
    # Publicly specified TRAIN pairs only, both orientations and all 4 equalities.
    return tuple(Recipe(p,a,b) for p in range(4) for x,y in TRAIN_PAIRS for a,b in ((x,y),(y,x)))

def condition(p: int, s: State) -> bool:
    b,c=s.buffer,s.cursor
    if p==0: return b[c]==b[c-1]
    if p==1: return b[c]==b[0]
    if p==2: return b[c-1]==b[-1]
    if p==3: return b[0]==b[-1]
    raise ValueError('non-TRAIN condition index')

def body(k: int, s: State) -> State:
    if k==0:
        # The current cursor Sym is bound before the atomic edit.
        return step(s,('INSERT',s.buffer[s.cursor]))
    if k==1: return step(s,('DELETE_RIGHT',None))
    if k==2: return step(s,('DELETE_BACK',None))
    if k==3:
        for a in (('SET_ANCHOR',None),('EXTEND_RIGHT',None),('EXTEND_RIGHT',None),
                  ('COPY',None),('CLEAR_SELECTION',None),('PASTE',None)):
            s=step(s,a)
        return s
    raise ValueError('non-TRAIN body index')

def target(recipe: Recipe,s: State) -> State:
    return body(recipe.then_body if condition(recipe.condition,s) else recipe.else_body,s)

class CounterStream:
    """Length-prefixed domain-separated SHA-256, rejection-sampled unbiased integers."""
    def __init__(self, *fields: str):
        if not fields or not all(type(f) is str for f in fields):
            raise ValueError('stream domain required')
        self.key=b''.join(len(f.encode('utf-8')).to_bytes(4,'big')+f.encode('utf-8') for f in fields)
        self.index=0
    def uint(self, n: int) -> int:
        if type(n) is not int or n<=0: raise ValueError('non-positive range')
        bound=(1<<256) - ((1<<256)%n)
        while True:
            x=int.from_bytes(hashlib.sha256(self.key+self.index.to_bytes(8,'big')).digest(),'big')
            self.index+=1
            if x<bound: return x%n

def initial(stream: CounterStream, extra: bool = False) -> State:
    lengths=(7,8) if extra else (4,5,6)
    n=lengths[stream.uint(len(lengths))]
    c=1+stream.uint(n-2)
    return State(tuple(SYMS[stream.uint(4)] for _ in range(n)),c)

def examples(recipe: Recipe, fixture_stream: str, extra: bool = False) -> tuple[tuple[State,State],...]:
    if fixture_stream not in FIXTURE_STREAMS: raise ValueError('only named artificial fixture streams')
    out=[]; seen=set()
    # T,T,T,F,F,F fixed presentation (labels omitted); query T,F.
    for kind,wants in [('demo',True)]*3+[('demo',False)]*3+[('query',True),('query',False)]:
        index=len(out)
        rng=CounterStream('world-lean-1','FIXTURE_TRAIN_ONLY',fixture_stream,
                          str(recipe.condition),str(recipe.then_body),str(recipe.else_body),
                          'extra' if extra else 'main',kind,str(index))
        for _ in range(DRAW_LIMIT):
            s=initial(rng,extra=extra)
            key=digest(s.record())
            if condition(recipe.condition,s)==wants and key not in seen:
                seen.add(key);out.append((s,target(recipe,s)));break
        else: raise RuntimeError('GENERATION_STOP')
    return tuple(out)

def audit_ambiguity(fixture_stream: str, extra: bool = False) -> dict:
    """TRAIN menu only. Never treats ambiguity as a license to regenerate/drop."""
    lawset=train_recipes()
    ambiguous=0; unresolved=0; total=0
    for true_law in lawset:
        data=examples(true_law,fixture_stream,extra=extra)
        agreeing=tuple(h for h in lawset if all(target(h,s)==t for s,t in data[:6]))
        if len(agreeing)>1: unresolved+=1
        for query,_ in data[6:]:
            predictions={digest(target(h,query).record()) for h in agreeing}
            ambiguous+=len(predictions)>1
            total+=1
    return {'fixture_stream':fixture_stream,'recipe_scope':'TRAIN_ONLY',
            'recipes':len(lawset),'queries':total,'ambiguous_queries':ambiguous,
            'ambiguous_fraction':f'{ambiguous}/{total}',
            'demo_nonunique_recipes':unresolved,'extra':extra}

def random_train_blocks(fixture_stream: str, blocks: int = 3) -> tuple[dict,...]:
    if fixture_stream not in FIXTURE_STREAMS or not 0<=blocks<=512:
        raise ValueError('fixture-only bounded blocks')
    rng=CounterStream('world-lean-1','FIXTURE_TRAIN_RANDOM',fixture_stream)
    laws=train_recipes()
    # 24-law rounds, Fisher-Yates order per round.
    result=[]
    for round_idx in range((blocks+23)//24):
        order=list(range(24))
        for i in range(23,0,-1):
            j=rng.uint(i+1);order[i],order[j]=order[j],order[i]
        for law_index in order:
            if len(result)>=blocks:break
            recipe=laws[law_index]
            s=initial(rng)
            pre=s
            actions=[];observations=[s.record()]
            for _ in range(8):
                a=TOKENS[rng.uint(14)]
                s=step(s,a)
                actions.append([a[0],a[1]])
                observations.append(s.record())
            opaque_tag='fixture-'+hashlib.sha256((fixture_stream+'|TRAIN-TAG|'+str(law_index)).encode()).hexdigest()[:16]
            result.append({'tag':opaque_tag,
                'initial':pre.record(),'actions':actions,'observations':observations,
                'success':s==target(recipe,pre),
                'demos':[[x.record(),y.record()] for x,y in examples(recipe,fixture_stream)[:6]]})
    return tuple(result)
