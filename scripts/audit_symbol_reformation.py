"""Read-only training diagnostic recount. No learner/runner/predictor imports."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from zipfile import ZipFile


def canon(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def digest(v):return sha256(canon(v).encode()).hexdigest()


def bindings(pattern,text):
    for lengths in product(range(1,7),repeat=sum(k=='V' for k,v in pattern)):
        pos=0;bound=[]
        for k,v in pattern:
            if k=='L':
                if text[pos:pos+1]!=v:break
                pos+=1
            else:
                value=text[pos:pos+lengths[v]]
                if len(value)!=lengths[v]:break
                bound.append(value);pos+=lengths[v]
        else:yield pos,bound


def expansion(atoms,values):return ''.join(v if k=='L' else values[v] for k,v in atoms)


def pattern_for(a,b,chunks):
    def tokenize(text):
        result=[];p=0
        while p<len(text):
            words=[w for w in chunks if text.startswith(w,p)]
            word=min(words,key=lambda w:(-len(w),w)) if words else text[p]
            result.append((word,p,p+len(word),chunks[word] if word in chunks else None));p+=len(word)
        return result
    aa,bb=tokenize(a),tokenize(b)
    if len(aa)!=len(bb):return None
    groups=[]
    for i,(x,y) in enumerate(zip(aa,bb)):
        eq=x[0]==y[0]
        if groups and groups[-1][0]==eq:groups[-1][1].append(i)
        else:groups.append((eq,[i]))
    pattern=[];va=[];vb=[];spans=[]
    for eq,indices in groups:
        x=''.join(aa[i][0] for i in indices);y=''.join(bb[i][0] for i in indices)
        if eq:pattern.extend([['L',c] for c in x])
        else:
            if len(va)==2 or max(len(x),len(y))>6:return None
            pattern.append(['V',len(va)]);va.append(x);vb.append(y)
            spans.append([[aa[indices[0]][1],aa[indices[-1]][2]], [bb[indices[0]][1],bb[indices[-1]][2]]])
    if not va or sum(k=='L' for k,v in pattern)>8:return None
    uses=[]
    for row,ts in enumerate((aa,bb)):
        for word,start,end,chunk in ts:
            if chunk:uses.append(dict(row_index=row,start=start,end=end,id=chunk['id'],expansion=word,acquired_at=chunk['created_at']))
    return pattern,va,vb,spans,uses


def outputs(a,b,va,vb):
    # Iterative path enumeration rather than the learner's recursive search.
    queue=[(0,0,[],0,0)];found=[]
    for i,j,atoms,refs,lits in queue:
        if i==len(a) and j==len(b):found.append(atoms);continue
        if len(atoms)>=16:continue
        if i<len(a) and j<len(b) and a[i]==b[j] and lits<8:
            queue.append((i+1,j+1,atoms+[['L',a[i]]],refs,lits+1))
        if refs<4:
            for v,(x,y) in enumerate(zip(va,vb)):
                if a.startswith(x,i) and b.startswith(y,j):queue.append((i+len(x),j+len(y),atoms+[['V',v]],refs+1,lits))
        assert len(queue)<=4096,'search bound'
    return [json.loads(s) for s in sorted({canon(p) for p in found})]


def verify(root):
    assert not (root/'STOP.json').exists(),'stopped comparison'
    complete=json.loads((root/'COMPLETE.json').read_text());assert complete['status']=='COMPLETE'
    manifest=(root/'SHA256SUMS.json').read_bytes()
    assert sha256(manifest).hexdigest()==complete['manifest_sha256']
    hashes=json.loads(manifest)
    assert set(hashes)=={'diagnostic.json','trials.json','events.json','report.json','result.md','cost.json'}
    for name,h in hashes.items():assert sha256((root/name).read_bytes()).hexdigest()==h,name
    assert {p.name for p in root.iterdir()}==set(hashes)|{'SHA256SUMS.json','COMPLETE.json'}
    sizes=sum(p.stat().st_size for p in root.iterdir())
    assert sizes<=50_000_000
    assert sizes==complete['artifact_bytes_before_completion']+(root/'COMPLETE.json').stat().st_size
    cost=complete['final_cost'];assert cost['operations']==sum(cost['by_kind'].values())<=20_000_000
    assert cost['cpu_seconds']<=120 and cost['wall_seconds']<=120
    project=Path(__file__).resolve().parents[1]
    archive=project/'experiments/SYMBOL-BOOTSTRAP-1/runs/local-02/evidence.zip'
    assert sha256(archive.read_bytes()).hexdigest()=='d050df3d1caa06203036b15c20e2a6881581133f1ad51d9ed5756666ee1d54e5'
    with ZipFile(archive) as z:data=z.read('states.json')
    assert sha256(data).hexdigest()=='b28875765b21e0b3603fb750a4fa8e7283d9322efd2b3b286de708aba4cdb7fd'
    states=json.loads(data);states={a:states[a] for a in ('FULL','NO-CHUNK')}
    d=json.loads((root/'diagnostic.json').read_text());trials=json.loads((root/'trials.json').read_text());events=json.loads((root/'events.json').read_text())
    report=json.loads((root/'report.json').read_text());assert report['status']=='COMPLETE'
    assert report['plan_sha256']==sha256((project/'experiments/SYMBOL-REFORMATION-1/plan.md').read_bytes()).hexdigest()
    rows=states['FULL']['rows'][:18];assert d['rows']==rows
    assert states['FULL']['rows']==states['NO-CHUNK']['rows']
    assert [t for _,t in states['FULL']['rows']]==[t for _,t in rows]*3
    assert len({t for _,t in rows})==18
    assert d['state_before']==d['state_after']==digest(states)==report['state_sha256']
    ti=0;ei=0;verified=0
    for arm in ('FULL','NO-CHUNK'):
        state=states[arm];result=d['arms'][arm];candidates=result['candidates']
        before=set(state['rules']);formed_ids=set();routes={r:set() for r in candidates};event_ids={r:[] for r in candidates};pairs=[]
        assert result['before']==sorted(before)
        for i in range(1,18):
            for j in range(i):
                pair=[rows[j][0],rows[i][0]];pairs.append(pair)
                for split in range(1,min(len(rows[j][1]),len(rows[i][1]))):
                    for route in (('symbol','character') if arm=='FULL' else ('character',)):
                        t=trials[ti];ti+=1
                        assert (t['id'],t['arm'],t['pair'],t['split'],t['route'])==(f'T{ti:05}',arm,pair,split,route)
                        chunks=state['chunks'] if route=='symbol' else {}
                        texts=[rows[j][1],rows[i][1]]
                        p=pattern_for(texts[0][:split],texts[1][:split],chunks)
                        if route=='symbol' and p and not p[4]:p=None
                        assert t['pattern_formed']==(p is not None)
                        expected_events=[]
                        if p:
                            pattern,va,vb,spans,uses=p
                            for output in outputs(texts[0][split:],texts[1][split:],va,vb):
                                ast=dict(pattern=pattern,output=output);rid='R-'+digest(ast)[:16]
                                assert candidates[rid]['ast']==ast
                                e=events[ei];ei+=1
                                eid=f'RF{ei:05}';expected_events.append(eid)
                                assert (e['id'],e['trial'],e['arm'],e['rule'],e['route'])==(eid,t['id'],arm,rid,route)
                                assert e['baseline_rediscovery']==(rid in before)
                                assert e['already_formed']==(rid in formed_ids)
                                assert e['reformation_at']=='AFTER-E054'
                                assert e['dependencies']==sorted({u['id'] for u in uses})
                                expected_uses=[dict(row=pair[u['row_index']],**{k:v for k,v in u.items() if k!='row_index'}) for u in uses]
                                assert e['chunk_uses']==expected_uses
                                assert e['sources']==[dict(row=pair[k],split=split,variable_spans=[s[k] for s in spans]) for k in range(2)]
                                for u in uses:assert u['acquired_at']<='E054'
                                formed_ids.add(rid);routes[rid].add(route);event_ids[rid].append(eid)
                        assert t['events']==expected_events
        assert result['pairs']==pairs
        assert set(candidates)==before|formed_ids
        assert result['after']==sorted(candidates)
        for rid,c in candidates.items():
            assert c['id']==rid=='R-'+digest(c['ast'])[:16]
            assert c['baseline']==(rid in before) and c['status']=='candidate'
            assert set(c['routes'])==routes[rid] and c['events']==event_ids[rid]
            if rid in before:assert c['ast']=={k:state['rules'][rid][k] for k in ('pattern','output')}
            expected=[]
            for row,text in rows:
                possibilities=list(bindings(c['ast']['pattern'],text))
                supports=[dict(split=end,bindings=b) for end,b in possibilities if expansion(c['ast']['output'],b)==text[end:]]
                expected.append(dict(row=row,status='support' if supports else 'failure' if possibilities else 'inapplicable',match=supports[0] if supports else None))
            assert c['evidence']==expected
            counts=Counter(e['status'] for e in expected)
            for k in ('support','failure','inapplicable'):assert c[k]==counts[k]
            verified+=1
        new=set(candidates)-before
        es=[e for e in events if e['arm']==arm]
        summary=dict(before=len(before),after=len(candidates),new=len(new),new_supported=sum(candidates[r]['support']>=2 for r in new),new_with_failure=sum(candidates[r]['failure']>0 for r in new),new_inapplicable_rows=sum(candidates[r]['inapplicable'] for r in new),attempts=sum(t['arm']==arm for t in trials),pairs=153,existing_rediscovery_events=sum(e['baseline_rediscovery'] for e in es),repeated_formation_events=sum(e['already_formed'] for e in es),cross_route_asts=sum(len(c['routes'])==2 for c in candidates.values()))
        assert result['summary']==report['summary'][arm]==summary
    assert ti==len(trials) and ei==len(events)
    f,n=d['arms']['FULL'],d['arms']['NO-CHUNK']
    unique=sorted(set(f['after'])-set(f['before'])-set(n['before'])-set(n['after']))
    unique=[r for r in unique if 'symbol' in f['candidates'][r]['routes'] and 'character' not in f['candidates'][r]['routes']]
    assert sorted(d['comparison']['full_chunk_exclusive_new'])==unique
    assert sorted(d['comparison']['full_chunk_exclusive_supported'])==[r for r in unique if f['candidates'][r]['support']>=2]
    assert report['comparison']==d['comparison']
    return dict(status='PASS',candidates=verified,row_assessments=verified*18,trials=ti,events=ei,artifact_bytes=sizes,independent_vm_check=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path)
    print(json.dumps(verify(p.parse_args().run),sort_keys=True))
