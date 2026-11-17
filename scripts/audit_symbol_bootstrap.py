"""Read-only stdlib recount: no learner, historical scorer or generator imports."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def canon(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def sha(x):return sha256(canon(x).encode()).hexdigest()


def matches(pattern,text,entire=False):
    n=sum(k=='V' for k,v in pattern)
    for lengths in product(range(1,7),repeat=n):
        pos=0;bound=[];valid=True
        for kind,value in pattern:
            if kind=='L':
                if text[pos:pos+1]!=value:valid=False;break
                pos+=1
            else:
                size=lengths[value];part=text[pos:pos+size]
                if len(part)!=size:valid=False;break
                bound.append(part);pos+=size
        if valid and (not entire or pos==len(text)):yield pos,bound


def expand(atoms,bound):return ''.join(v if k=='L' else bound[v] for k,v in atoms)


def rank(rule):
    support={e['text'] for e in rule['evidence'] if e['status']=='support'}
    fail={e['text'] for e in rule['evidence'] if e['status']=='failure'}
    return (-Fraction(len(support),len(support)+len(fail) or 1),-len(support),
            -sum(k=='L' for k,v in rule['pattern']),canon(dict(pattern=rule['pattern'],output=rule['output'])))


def raw_predict(rows,prefix,n):
    memory=Counter();ng=defaultdict(Counter)
    for _,text in rows:
        if text.startswith(prefix):memory[text[len(prefix):]]+=1
        for i,c in enumerate(text):
            for size in range(min(i,4)+1):ng[text[i-size:i]][c]+=1
    output=min(memory,key=lambda x:(-memory[x],x))[:n] if memory else ''
    while len(output)<n:
        context=prefix+output;char=';'
        for size in range(min(len(context),4),-1,-1):
            counts=ng[context[-size:] if size else '']
            if counts:char=min(counts,key=lambda c:(-counts[c],c));break
        output+=char
    return output


def verify(root):
    hashes=json.loads((root/'SHA256SUMS.json').read_text())
    for name,expected in hashes.items():
        if Path(name).name!=name:raise ValueError('invalid artifact path')
        assert sha256((root/name).read_bytes()).hexdigest()==expected,name
    report=json.loads((root/'report.json').read_text())
    assert report['status']=='COMPLETE','incomplete comparison; no accuracy inferred'
    states=json.loads((root/'states.json').read_text());history=json.loads((root/'history.json').read_text())
    assert len(report['rows'])==56 and len({(r['id'],r['arm']) for r in report['rows']})==56
    assert len(history['prequential'])==216
    # Full evidence reclassification uses length-product matching rather than learner recursion/cache.
    verified_rules=0
    for arm,state in states.items():
        if arm=='NO-LEARN':assert not state['rows'] and not state['rules'] and not state['chunks']
        else:assert len(state['rows'])==54 and len(history['episodes'][arm])==54
        if arm!='FULL':assert not state['chunks'] and not state['fragments']
        if arm in ('NO-LEARN','MEMORY'):assert not state['rules']
        chunks={c['id']:c for c in state['chunks'].values()}
        episodes=dict(state['rows'])
        for chunk in chunks.values():
            assert ''.join(p['text'] for p in chunk['parts'])==chunk['expansion']
            sources=state['fragments'][chunk['expansion']]
            prior=[s for s in sources if s['episode']<=chunk['created_at']]
            assert len({s['text'] for s in prior})>=2
            for source in sources:
                assert episodes[source['episode']][source['start']:source['end']]==chunk['expansion']
            for part in chunk['parts']:
                if part['symbol']:
                    ref=chunks[part['symbol']]
                    assert ref['created_at']<chunk['created_at'] and ref['expansion']==part['text']
        for rule in state['rules'].values():
            assert rule['id']=='R-'+sha(dict(pattern=rule['pattern'],output=rule['output']))[:16]
            if rule['route']=='symbol':assert rule['dependencies']
            else:assert not rule['dependencies']
            for dep in rule['dependencies']:assert chunks[dep]['created_at']<rule['created_at']
            for source in rule['sources']:
                text=episodes[source['episode']];split=source['split']
                bound=[text[a:b] for a,b in source['variable_spans']]
                assert expand(rule['pattern'],bound)==text[:split]
                assert expand(rule['output'],bound)==text[split:]
                assert source['episode']<=rule['created_at']
            expected=[]
            for eid,text in state['rows']:
                possibilities=list(matches(rule['pattern'],text))
                if possibilities:
                    right=any(expand(rule['output'],b)==text[p:] for p,b in possibilities)
                    expected.append((eid,'support' if right else 'failure'))
            assert [(e['episode'],e['status']) for e in rule['evidence']]==expected
            verified_rules+=1
    expected_groups={'a':4,'b1':4,'b2':2,'c':4}
    for arm in report['arms']:
        state=states[arm]
        for group,n in expected_groups.items():
            rows=[r for r in report['rows'] if r['arm']==arm and r['group']==group]
            assert len(rows)==n
            correct=0
            for row in rows:
                assert row['state_sha256']==sha(state)
                trace=row['trace'];selected=[]
                for rule in sorted(state['rules'].values(),key=rank):
                    if len({e['text'] for e in rule['evidence'] if e['status']=='support'})<2:continue
                    for _,bindings in matches(rule['pattern'],row['prefix'],True):
                        selected.append((rule,bindings,expand(rule['output'],bindings)))
                if selected:
                    rule,bound,prediction=selected[0]
                    assert trace['selected']['rule']==rule['id'] and trace['selected']['bindings']==bound
                    assert len(trace['competing'])==len(selected)
                    # Fixed cases all generate seven characters entirely from their selected AST.
                    assert len(prediction)==7 and not trace['fallback']
                else:prediction=raw_predict(state['rows'],row['prefix'],7)
                assert trace['prediction']==prediction
                assert row['correct']==(prediction==row['expected'])
                correct+=row['correct']
            assert report['summary'][group]['correct'][arm]==correct
    return dict(status='PASS',verified_predictions=56,verified_rules=verified_rules,
                full_chunk_count=len(states['FULL']['chunks']),independent_vm_check=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path)
    print(json.dumps(verify(p.parse_args().run),sort_keys=True))
