"""EXP-COEV-001 invented TRAIN-only concept learner. NOT an independent evaluator."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, asdict
import random
from packages.concept_world import Program, SemanticCatalog, build_catalog, digest, inputs, query_argmax, split_inputs, _trusted_catalog

@dataclass(frozen=True, slots=True)
class Episode:
    task_id: str
    arm: str
    public_input_ids: tuple[int,int]
    public_answers: tuple[str,str]
    queried_input_ids: tuple[int,...]
    queried_answers: tuple[str,...]
    initial_hypotheses: int
    remaining_hypotheses: int
    chosen_program_id: str | None
    train_verified_success: bool

@dataclass(frozen=True, slots=True)
class Concept:
    predicate_id: str | None
    then_pattern: tuple[str | None,...]
    else_pattern: tuple[str | None,...]
    support_task_ids: tuple[str,...]
    parameter_count: int
    compression_gain: int
    concept_id: str

    def matches(self, program: Program) -> bool:
        if program.predicate_id != self.predicate_id: return False
        if len(program.then_ops) != len(self.then_pattern) or len(program.else_ops) != len(self.else_pattern): return False
        return (all(x is None or x == y for x,y in zip(self.then_pattern,program.then_ops))
                and all(x is None or x == y for x,y in zip(self.else_pattern,program.else_ops)))

@dataclass(frozen=True, slots=True)
class Snapshot:
    arm: str
    world_digest: str
    train_receipt_digest: str
    concept_library: tuple[Concept,...]
    policy_success_counts: tuple[tuple[int,str,int],...]
    snapshot_digest: str

def _template_from_pair(a: Program,b: Program) -> tuple[str | None,tuple[str | None,...],tuple[str | None,...]] | None:
    if a.predicate_id != b.predicate_id or len(a.then_ops) != len(b.then_ops) or len(a.else_ops) != len(b.else_ops):
        return None
    left=tuple(x if x==y else None for x,y in zip(a.then_ops,b.then_ops))
    right=tuple(x if x==y else None for x,y in zip(a.else_ops,b.else_ops))
    holes=left.count(None)+right.count(None)
    if holes>2 or not any(x is not None for x in left+right): return None
    return a.predicate_id,left,right

def induce_concepts(episodes: tuple[Episode,...],catalog: SemanticCatalog,max_concepts: int=8) -> tuple[Concept,...]:
    catalog=_trusted_catalog(catalog)
    if type(max_concepts) is not int or not 1<=max_concepts<=8: raise ValueError("Invalid library budget")
    known={p.program_id:p for p in catalog.representatives}
    solved=[(e.task_id,known[e.chosen_program_id]) for e in episodes
            if e.train_verified_success and e.chosen_program_id in known]
    if len({t for t,p in solved}) != len(solved): raise ValueError("Duplicate TRAIN provenance")
    proposals=set()
    for i,(_,p) in enumerate(solved):
        proposals.add((p.predicate_id,p.then_ops,p.else_ops))
        for _,q in solved[i+1:]:
            template=_template_from_pair(p,q)
            if template is not None: proposals.add(template)
    concepts=[]
    for pred,then,otherwise in proposals:
        if len(then)+len(otherwise)<2: continue
        holes=then.count(None)+otherwise.count(None)
        supporting=tuple(sorted(t for t,p in solved if (
            p.predicate_id==pred and len(p.then_ops)==len(then) and len(p.else_ops)==len(otherwise)
            and all(x is None or x==y for x,y in zip(then,p.then_ops))
            and all(x is None or x==y for x,y in zip(otherwise,p.else_ops)))))
        if len(supporting)<3: continue
        raw_tokens=len(then)+len(otherwise)+(1 if pred is not None else 0)
        definition_cost=raw_tokens+holes+1
        compressed_use=1+holes
        gain=len(supporting)*(raw_tokens-compressed_use)-definition_cost
        if gain<=0: continue
        key=digest({"predicate":pred,"then":then,"else":otherwise})
        concepts.append(Concept(pred,then,otherwise,supporting,holes,gain,key))
    concepts.sort(key=lambda c:(-c.compression_gain,-len(c.support_task_ids),c.concept_id))
    return tuple(concepts[:max_concepts])

def context_bucket(public_inputs: tuple[int,int],public_answers: tuple[str,str]) -> int:
    if (type(public_inputs) is not tuple or len(public_inputs)!=2
            or type(public_answers) is not tuple or len(public_answers)!=2):
        raise ValueError("Invalid public examples")
    values=inputs()
    if (any(type(i) is not int or not 0<=i<len(values) for i in public_inputs)
            or any(type(v) is not str for v in public_answers)):
        raise ValueError("Invalid public observation")
    feats=tuple((len(values[i]),len(out),values[i]==out,out.isupper()," " in out)
                for i,out in zip(public_inputs,public_answers))
    return int(digest(feats)[:8],16)%64

def recommend_programs(snapshot: Snapshot,catalog: SemanticCatalog,public_inputs: tuple[int,int],
                       public_answers: tuple[str,str],candidates: tuple[int,...],
                       max_candidates: int=64) -> tuple[int,...]:
    catalog=_trusted_catalog(catalog)
    if (type(max_candidates) is not int or not 1<=max_candidates<=256 or
        type(candidates) is not tuple or len(set(candidates))!=len(candidates) or
        any(type(i) is not int or not 0<=i<len(catalog.representatives) for i in candidates)):
        raise ValueError("Invalid candidate request")
    if snapshot.world_digest != catalog.world_digest: raise ValueError("World mismatch")
    bucket=context_bucket(public_inputs,public_answers)
    prior={(b,p):n for b,p,n in snapshot.policy_success_counts}
    def rank(cid: int) -> tuple[int,int,int]:
        p=catalog.representatives[cid]
        gain=max((c.compression_gain for c in snapshot.concept_library if c.matches(p)),default=0)
        visits=prior.get((bucket,p.program_id),0)
        return (-gain,-visits,cid)
    return tuple(sorted(candidates,key=rank)[:max_candidates])

def simulate_train(seed: int=20261031,task_count: int=256,arm: str="active") -> tuple[tuple[Episode,...],Snapshot]:
    if (type(seed) is not int or type(task_count) is not int or not 1<=task_count<=256
            or arm not in ("active","random")):
        raise ValueError("Only bounded TRAIN simulation allowed")
    cat=build_catalog()
    split=split_inputs(seed)
    rng=random.Random(seed)
    pools=(tuple(i for i,p in enumerate(cat.representatives) if p.predicate_id is None),
           tuple(i for i,p in enumerate(cat.representatives) if p.predicate_id is not None))
    train_pool=[]
    for group in pools:
        ids=list(group)
        rng.shuffle(ids)
        train_pool.extend(ids[:round(.45*len(ids))])
    task_rng=random.Random(seed+1)
    episodes=[]
    for task_i in range(task_count):
        # Hidden target remains inside this TRAIN-only simulator, not serialized.
        target=task_rng.choice(train_pool)
        public=tuple(task_rng.sample(split.public_ids,2))
        public_answers=tuple(cat.class_signatures[target][i] for i in public)
        remaining=tuple(i for i,sig in enumerate(cat.class_signatures)
                        if all(sig[q]==cat.class_signatures[target][q] for q in public))
        n_initial=len(remaining)
        queries=[]
        responses=[]
        for step in range(2):
            if len(remaining)==1: break
            allowed=tuple(q for q in split.query_ids if q not in queries)
            q=(query_argmax(cat,remaining,allowed) if arm=="active"
               else random.Random(seed*31+task_i*2+step).choice(allowed))
            if q is None: break
            answer=cat.class_signatures[target][q]
            queries.append(q)
            responses.append(answer)
            remaining=tuple(i for i in remaining if cat.class_signatures[i][q]==answer)
        chosen=min(remaining) if remaining else None
        episodes.append(Episode(f"train-{task_i:05d}",arm,public,public_answers,tuple(queries),
            tuple(responses),n_initial,len(remaining),
            cat.representatives[chosen].program_id if chosen is not None else None,
            chosen==target))
    saved=tuple(episodes)
    library=induce_concepts(saved,cat)
    counts=Counter((context_bucket(e.public_input_ids,e.public_answers),e.chosen_program_id)
                   for e in saved if e.train_verified_success)
    policy=tuple(sorted((b,p,n) for (b,p),n in counts.items() if p is not None))
    receipt=digest([asdict(e) for e in saved])
    snapshot_id=digest({"arm":arm,"world":cat.world_digest,"train":receipt,
        "concepts":[(c.concept_id,c.compression_gain) for c in library],"policy":policy})
    return saved,Snapshot(arm,cat.world_digest,receipt,library,policy,snapshot_id)
