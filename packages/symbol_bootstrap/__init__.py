"""Bounded raw-character induction. No fixture, task grammar or scorer imports."""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import groupby
import json
import time


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


class ResourceStop(RuntimeError):
    pass


class Budget:
    def __init__(self, limits):
        self.limits = dict(limits)
        self.started = time.monotonic()
        self.cpu_started = time.process_time()
        self.operations = 0
        self.by_kind = Counter()

    def tick(self, kind, count=1):
        self.operations += count
        self.by_kind[kind] += count
        if self.operations > self.limits['operations_total']:
            raise ResourceStop('operations_total')
        self.check()

    def check(self):
        if time.monotonic() - self.started > self.limits['wall_seconds']:
            raise ResourceStop('wall_seconds')
        if time.process_time() - self.cpu_started > self.limits['cpu_seconds']:
            raise ResourceStop('cpu_seconds')

    def receipt(self):
        return dict(operations=self.operations, by_kind=dict(self.by_kind),
                    wall_seconds=time.monotonic()-self.started,
                    cpu_seconds=time.process_time()-self.cpu_started)


class Learner:
    def __init__(self, arm, alphabet, budget):
        if arm not in ('FULL', 'NO-CHUNK', 'MEMORY', 'NO-LEARN'):
            raise ValueError('unknown arm')
        self.arm, self.alphabet, self.budget = arm, ''.join(sorted(alphabet)), budget
        self.limits = budget.limits
        self.rows = []
        self.seen = {}  # raw strings -> first episode, never fixture labels
        self.memory = defaultdict(Counter)
        self.ngrams = defaultdict(Counter)
        self.fragments = {}
        self.chunks = {}
        self.rules = {}
        self.history = []
        self.cost = Counter()
        self._fit_cache = {}

    def tick(self, kind, n=1):
        self.cost[kind] += n
        self.budget.tick(kind, n)

    def state(self):
        return dict(arm=self.arm, rows=self.rows, chunks=self.chunks,
                    fragments=self.fragments, rules=self.rules,
                    memory={k: dict(v) for k, v in self.memory.items()},
                    ngrams={k: dict(v) for k, v in self.ngrams.items()})

    def tokenize(self, text, chunks=None):
        chunks = self.chunks if chunks is None else chunks
        result, pos = [], 0
        ordered = sorted(chunks, key=lambda s: (-len(s), s))
        while pos < len(text):
            self.tick('token_scan')
            match = next((s for s in ordered if text.startswith(s, pos)), text[pos])
            result.append(dict(text=match, start=pos, end=pos+len(match),
                               symbol=chunks[match]['id'] if match in chunks else None))
            pos += len(match)
        return result

    def _pattern(self, a, b, symbolic):
        ta = self.tokenize(a) if symbolic else [dict(text=c, start=i, end=i+1, symbol=None) for i,c in enumerate(a)]
        tb = self.tokenize(b) if symbolic else [dict(text=c, start=i, end=i+1, symbol=None) for i,c in enumerate(b)]
        if len(ta) != len(tb):
            return None
        pattern, va, vb, spans, deps = [], [], [], [], set()
        for equal, indices in groupby(range(len(ta)), key=lambda i: ta[i]['text'] == tb[i]['text']):
            indices = list(indices)
            aa = ''.join(ta[i]['text'] for i in indices)
            bb = ''.join(tb[i]['text'] for i in indices)
            for ts in (ta, tb):
                deps.update(ts[i]['symbol'] for i in indices if ts[i]['symbol'])
            if equal:
                pattern.extend(('L', c) for c in aa)
            else:
                if len(va) == self.limits['variables'] or max(len(aa),len(bb)) > self.limits['variable_chars']:
                    return None
                pattern.append(('V', len(va)))
                va.append(aa); vb.append(bb)
                spans.append([[ta[indices[0]]['start'],ta[indices[-1]]['end']],
                              [tb[indices[0]]['start'],tb[indices[-1]]['end']]])
        if not va or sum(t[0]=='L' for t in pattern) > self.limits['input_literals']:
            return None
        if symbolic and not deps:
            return None
        return pattern, va, vb, spans, sorted(deps)

    def _outputs(self, a, b, va, vb):
        """Enumerate shared literal/copy ASTs; no target-specific operator."""
        found, nodes = set(), 0
        def visit(i, j, atoms, refs, literals):
            nonlocal nodes
            nodes += 1
            self.tick('output_search_node')
            if nodes > self.limits['output_search_nodes_per_pair']:
                raise ResourceStop('output_search_nodes_per_pair')
            if i==len(a) and j==len(b):
                found.add(tuple(atoms)); return
            if len(atoms) >= self.limits['output_atoms']:
                return
            if i<len(a) and j<len(b) and a[i]==b[j] and literals<self.limits['output_literals']:
                visit(i+1,j+1,atoms+[('L',a[i])],refs,literals+1)
            if refs < self.limits['output_references']:
                for v,(x,y) in enumerate(zip(va,vb)):
                    if a.startswith(x,i) and b.startswith(y,j):
                        visit(i+len(x),j+len(y),atoms+[('V',v)],refs+1,literals)
        visit(0,0,[],0,0)
        return sorted(found, key=canonical)

    def _bindings(self, pattern, text, entire):
        def visit(k, pos, bound):
            self.tick('match_node')
            if k == len(pattern):
                if not entire or pos == len(text):
                    yield pos, bound
                return
            kind, value = pattern[k]
            if kind == 'L':
                if pos<len(text) and text[pos]==value:
                    yield from visit(k+1,pos+1,bound)
            else:
                for length in range(1, min(self.limits['variable_chars'],len(text)-pos)+1):
                    yield from visit(k+1,pos+length,bound+[text[pos:pos+length]])
        yield from visit(0,0,[])

    def _expand(self, atoms, bound):
        self.tick('expand_atom',len(atoms))
        text = ''.join(value if kind=='L' else bound[value] for kind,value in atoms)
        if len(text)>self.limits['expanded_chars']:
            raise ResourceStop('expanded_chars')
        return text

    def _fit(self, rule, text):
        key = rule['id'], text
        if key in self._fit_cache:
            self.tick('fit_cache'); return self._fit_cache[key]
        applied, correct = False, None
        for end,bound in self._bindings(rule['pattern'],text,False):
            applied = True
            if self._expand(rule['output'],bound) == text[end:]:
                correct = dict(split=end, bindings=bound); break
        result = ('support' if correct else 'failure' if applied else 'inapplicable',correct)
        self._fit_cache[key] = result
        return result

    def _evidence(self, rule, eid, text):
        status, binding = self._fit(rule,text)
        if status != 'inapplicable':
            rule['evidence'].append(dict(episode=eid,text=text,status=status,match=binding))
            rule['updated_at'] = eid

    def _form(self, eid, text):
        attempts = 0
        for old, old_eid in self.seen.items():
            if old==text: continue
            for split in range(1,min(len(old),len(text))):
                for symbolic in ([True,False] if self.arm=='FULL' else [False]):
                    attempts += 1
                    self.tick('formation_attempt')
                    if attempts>self.limits['formation_attempts_per_episode']:
                        raise ResourceStop('formation_attempts_per_episode')
                    formed = self._pattern(old[:split],text[:split],symbolic)
                    if formed is None: continue
                    pattern,va,vb,spans,deps = formed
                    for output in self._outputs(old[split:],text[split:],va,vb):
                        ast = dict(pattern=pattern,output=output)
                        rid = 'R-'+digest(ast)[:16]
                        if rid in self.rules: continue
                        if len(self.rules)>=self.limits['rules']:
                            raise ResourceStop('rules')
                        rule = dict(id=rid,**ast,created_at=eid,updated_at=eid,
                                    route='symbol' if symbolic else 'character',dependencies=deps,
                                    sources=[dict(episode=old_eid,split=split,variable_spans=[s[0] for s in spans]),
                                             dict(episode=eid,split=split,variable_spans=[s[1] for s in spans])],evidence=[])
                        for past_id,past in self.rows:
                            self._evidence(rule,past_id,past)
                        self.rules[rid]=rule
        return attempts

    def _chunks(self,eid,text,prior):
        created=[]
        for size in range(2,self.limits['chunk_chars']+1):
            for start in range(len(text)-size+1):
                self.tick('fragment')
                value=text[start:start+size]
                if value not in self.fragments:
                    if len(self.fragments)>=self.limits['chunks']:
                        raise ResourceStop('fragment_retention')
                    self.fragments[value]=[]
                self.fragments[value].append(dict(episode=eid,text=text,start=start,end=start+size))
                if value not in self.chunks and len({p['text'] for p in self.fragments[value]})>=2:
                    if len(self.chunks)>=self.limits['chunks']:
                        raise ResourceStop('chunks')
                    parts=self.tokenize(value,prior)
                    self.chunks[value]=dict(id='C-'+digest(value)[:16],expansion=value,created_at=eid,
                                           parts=parts,dependencies=sorted({p['symbol'] for p in parts if p['symbol']}))
                    created.append(self.chunks[value]['id'])
        return created

    def observe(self, eid, text):
        if type(text) is not str or not text or len(text)>self.limits['episode_chars'] or any(c not in self.alphabet for c in text):
            raise ValueError('raw episode outside character contract')
        if self.arm=='NO-LEARN': return
        if len(self.rows)>=self.limits['episodes']: raise ResourceStop('episodes')
        before = set(self.rules)
        prior = dict(self.chunks)
        self.rows.append((eid,text))
        for split in range(len(text)+1):
            self.tick('memory_prefix')
            self.memory[text[:split]][text[split:]] += 1
        for i,c in enumerate(text):
            for n in range(min(4,i)+1):
                self.tick('ngram')
                self.ngrams[text[i-n:i]][c] += 1
        for rule in self.rules.values(): self._evidence(rule,eid,text)
        attempts=0
        if self.arm in ('FULL','NO-CHUNK') and text not in self.seen:
            attempts=self._form(eid,text)
        created_chunks=self._chunks(eid,text,prior) if self.arm=='FULL' else []
        self.seen.setdefault(text,eid)
        changes=[]
        for rule in self.rules.values():
            last=rule['evidence'][-1] if rule['evidence'] else None
            if rule['id'] not in before or (last and last['episode']==eid):
                support={e['text'] for e in rule['evidence'] if e['status']=='support'}
                failure={e['text'] for e in rule['evidence'] if e['status']=='failure'}
                changes.append(dict(id=rule['id'],new=rule['id'] not in before,unique_support=len(support),unique_failure=len(failure),last=last))
        self.history.append(dict(episode=eid,observed=text,new_chunks=created_chunks,rule_changes=changes,formation_attempts=attempts,
                                 retained_rules=len(self.rules),retained_chunks=len(self.chunks),cost=dict(self.cost)))

    def _rank(self, rule):
        support={e['text'] for e in rule['evidence'] if e['status']=='support'}
        failure={e['text'] for e in rule['evidence'] if e['status']=='failure'}
        confidence=Fraction(len(support),len(support)+len(failure) or 1)
        return (-confidence,-len(support),-sum(k=='L' for k,v in rule['pattern']),canonical(dict(pattern=rule['pattern'],output=rule['output'])))

    def predict(self, prefix, length):
        if type(prefix) is not str or len(prefix)>self.limits['episode_chars'] or any(c not in self.alphabet for c in prefix):
            raise ValueError('prefix outside character contract')
        if not 0<length<=self.limits['expanded_chars']: raise ValueError('generation length')
        candidates=[]
        for rule in sorted(self.rules.values(),key=self._rank):
            if len({e['text'] for e in rule['evidence'] if e['status']=='support'})<2: continue
            for _,bound in self._bindings(rule['pattern'],prefix,True):
                expansion=self._expand(rule['output'],bound)
                candidates.append(dict(rule=rule['id'],bindings=bound,expansion=expansion,
                                       dependencies=rule['dependencies'],route=rule['route']))
        if candidates:
            chosen=candidates[0]
            generated=chosen['expansion'][:length]
            tail=[]
            while len(generated)<length:
                c,trace=self._next(prefix+generated); generated+=c; tail.append(trace)
            return dict(prediction=generated,path='rule',selected=chosen,competing=candidates,fallback=tail)
        if prefix in self.memory:
            suffix=min(self.memory[prefix],key=lambda s:(-self.memory[prefix][s],s))
            generated=suffix[:length]; tail=[]
            while len(generated)<length:
                c,trace=self._next(prefix+generated); generated+=c; tail.append(trace)
            return dict(prediction=generated,path='memory',selected=None,competing=[],fallback=tail,memory_suffix=suffix)
        generated=''; tail=[]
        while len(generated)<length:
            c,trace=self._next(prefix+generated); generated+=c; tail.append(trace)
        return dict(prediction=generated,path='ngram',selected=None,competing=[],fallback=tail)

    def _next(self, context):
        for n in range(min(4,len(context)),-1,-1):
            self.tick('ngram_lookup')
            key=context[-n:] if n else ''
            counts=self.ngrams.get(key)
            if counts:
                c=min(counts,key=lambda c:(-counts[c],c))
                return c,dict(context=key,character=c,count=counts[c])
        return self.alphabet[0],dict(context=None,character=self.alphabet[0],count=0)
