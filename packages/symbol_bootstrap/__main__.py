"""Fixed invented engineering check; evaluator metadata never enters observe()."""
import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

from . import Budget, Learner, ResourceStop, canonical, digest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT/'experiments/SYMBOL-BOOTSTRAP-1'
LOCK_SHA = 'cc9c4f5275a6d9e6af972caa98eb2d8a24464dc1ee8395d73fd128ca446a4457'
PLAN_SHA = '54b21502668d7b45a6663e7d1ee2a71a64d73ea4c2dbbc0d44875888e0732242'


def load_lock():
    for name, expected in [('lock.json',LOCK_SHA),('plan.md',PLAN_SHA)]:
        if sha256((FIXTURE/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('pre-execution freeze changed: '+name)
    return json.loads((FIXTURE/'lock.json').read_text())


def audit_ledger(lock):
    train=lock['train']; tests=lock['tests']
    assert len(train)==18 and len(tests)==14
    assert len({r['prefix'] for r in train})==18
    audit=[]
    alltext=''.join(r['prefix']+r['expected'] for r in train)
    for t in tests:
        pair=sum(r['x']==t['x'] and r['y']==t['y'] for r in train)
        exact=sum(r['prefix']==t['prefix'] for r in train)
        content=sum(r['expected'][:-1]==t['expected'][:-1] for r in train)
        if t['group']=='a': assert exact==1
        if t['group']=='b1': assert pair==0 and content==0
        if t['group']=='b2': assert pair==1 and exact==0
        if t['group']=='c': assert not set(t['x']+t['y']) & set(alltext)
        audit.append(dict(id=t['id'],group=t['group'],prefix_occurrences_per_round=exact,
                          pair_occurrences_per_round=pair,content_occurrences_per_round=content,
                          context_occurrences_per_round=sum(r['context']==t['context'] for r in train)))
    return audit


def aggregate(rows, arms):
    expected={'a':4,'b1':4,'b2':2,'c':4}
    keys=[(r['id'],r['arm']) for r in rows]
    if len(keys)!=56 or len(set(keys))!=56:
        raise ValueError('incomplete or duplicate comparison')
    for arm in arms:
        for group,n in expected.items():
            if sum(r['arm']==arm and r['group']==group for r in rows)!=n:
                raise ValueError('fixed denominator missing')
    result={}
    for group in ('a','b1','b2','b','c'):
        selected=[r for r in rows if r['group']==group or (group=='b' and r['group'] in ('b1','b2'))]
        n=len(selected)//len(arms)
        counts={arm:sum(r['correct'] for r in selected if r['arm']==arm) for arm in arms}
        paired={}
        for arm in arms[1:]:
            pairs=[(next(r['correct'] for r in selected if r['arm']=='FULL' and r['id']==t),
                    next(r['correct'] for r in selected if r['arm']==arm and r['id']==t))
                   for t in sorted({r['id'] for r in selected})]
            paired[arm]=dict(win=sum(a and not b for a,b in pairs),loss=sum(b and not a for a,b in pairs),tie=sum(a==b for a,b in pairs))
        result[group]=dict(denominator=n,correct=counts,full_vs=paired,
                           abstentions={a:sum(r['trace']['prediction']=='' for r in selected if r['arm']==a) for a in arms})
    return result


def interpret(summary, rows):
    b=summary['b']['correct']; a=summary['a']['correct']
    if all(b['FULL']>b[k] for k in b if k!='FULL'):
        paths=[r for r in rows if r['arm']=='FULL' and r['group'] in ('b1','b2') and r['correct']]
        if paths and all(r['trace']['selected'] and r['trace']['selected']['dependencies'] for r in paths):
            return 'fixed_artificial_reuse_finding_pending_independent_trace_audit'
        return 'unseen_gain_without_verified_symbol_dependency'
    if b['FULL']==0 and any(a['FULL']>a[k] for k in a if k!='FULL'):
        return 'repetition_memory_effect_only'
    if b['FULL']:
        return 'unseen_prediction_observed_chunk_contribution_unconfirmed'
    return 'no_unseen_improvement_observed'


def markdown(report):
    lines=['# SYMBOL-BOOTSTRAP-1 結果票','','id: SYMBOL-BOOTSTRAP-1-RUN','status: '+report['status'],
           'updated: 2026-11-17','tags: artificial, engineering, bootstrap','','固定上限・選択順は先行の別commit。人工工学確認のみ。Museの独立確認は未実施。',
           '',f"実行ソース: `{report['source_commit']}`。固定JSON SHA256: `{LOCK_SHA}`。",'']
    if report['status']!='COMPLETE':
        lines += ['RESOURCE_STOP／欠損を正答率へ混ぜない。完了した比較として解釈しない。',str(report.get('reason',''))]
    else:
        lines += ['|分類|件数|FULL|NO-LEARN|NO-CHUNK|MEMORY|','|---|---:|---:|---:|---:|---:|']
        for g,s in report['summary'].items():
            lines.append('|'+g+'|'+str(s['denominator'])+'|'+'|'.join(str(s['correct'][a]) for a in report['arms'])+'|')
        lines += ['', '解釈: `'+report['interpretation']+'`。分類別の勝ち／負け／同点・棄権はJSONに収録。',
                  'NO-CHUNKやMEMORYと同程度なら、自作したまとまりの寄与は未確認。一般能力・意味理解の認定はしない。','',
                  '|分類/ID|方式|prefix|期待|予測|正誤|経路|','|---|---|---|---|---|---|---|']
        for r in report['rows']:
            esc=lambda s:s.replace('|','\\|')
            lines.append('|'+ '|'.join([r['id'],r['arm'],esc(r['prefix']),r['expected'],r['trace']['prediction'],str(r['correct']),r['trace']['path']])+'|')
    lines += ['', '生の記録: `report.json`（全56予測・来歴参照・候補競合・prefix/期待/予測）。',
              '`states.json` は全候補・元episode/文字位置・chunkの依存DAG・支持/反例、`history.json` は入力順の増減と事前予測。',
              '処理費用は `cost.json`。CPU/wallは実測値、candidate/primitive countersとは別。',
              '結果を見て条件を延長・調整しない。E1・既存研究・マージは範囲外。','']
    return '\n'.join(lines)


def run(out):
    lock=load_lock(); budget=Budget(lock['limits'])
    out.mkdir(parents=True,exist_ok=False)
    try:
        source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except subprocess.SubprocessError:
        source='not_observed'
    report=dict(schema='symbol-bootstrap-report/1',status='INCOMPLETE',source_commit=source,arms=lock['arms'],rows=[],
                lock_sha256=LOCK_SHA,plan_sha256=PLAN_SHA,runtime=dict(python=sys.version,platform=platform.platform()))
    learners={}; prequential=[]
    try:
        report['ledger']=audit_ledger(lock)
        for arm in lock['arms']:
            learner=Learner(arm,lock['alphabet'],budget); learners[arm]=learner
            for i in range(lock['rounds']*len(lock['train'])):
                record=lock['train'][i%len(lock['train'])]
                eid=f'E{i+1:03}'
                prequential.append(dict(arm=arm,episode=eid,prefix=record['prefix'],
                                        trace=learner.predict(record['prefix'],7),expected=record['expected']))
                learner.observe(eid,record['prefix']+record['expected'])
        for test in lock['tests']:
            for arm in lock['arms']:
                learner=learners[arm]
                before=digest(learner.state())
                trace=learner.predict(test['prefix'],7)
                assert before==digest(learner.state()),'prediction updated training state'
                report['rows'].append(dict(id=test['id'],group=test['group'],arm=arm,prefix=test['prefix'],
                                           expected=test['expected'],trace=trace,correct=trace['prediction']==test['expected'],state_sha256=before))
        report['summary']=aggregate(report['rows'],lock['arms'])
        report['interpretation']=interpret(report['summary'],report['rows'])
        report['status']='COMPLETE'
        budget.check()
    except ResourceStop as exc:
        report['status']='RESOURCE_STOP'; report['reason']=str(exc)
        report.pop('summary',None); report.pop('interpretation',None)
    states={a:l.state() for a,l in learners.items()}
    history=dict(prequential=prequential,episodes={a:l.history for a,l in learners.items()})
    payloads={'report.json':report,'states.json':states,'history.json':history,
              'cost.json':dict(total=budget.receipt(),arms={a:dict(l.cost) for a,l in learners.items()})}
    # Size check before writing; no partial file is accepted as a complete comparison.
    encoded={k:(canonical(v)+'\n').encode() for k,v in payloads.items()}
    if sum(map(len,encoded.values()))>lock['limits']['artifact_bytes']:
        report['status']='RESOURCE_STOP'; report['reason']='artifact_bytes';report.pop('summary',None);report.pop('interpretation',None)
        report['missing_artifacts']=['states.json','history.json','cost.json']
        encoded={'report.json':(canonical(report)+'\n').encode()}
    if report['status']=='COMPLETE':
        try: budget.check()
        except ResourceStop as exc:
            report['status']='RESOURCE_STOP'; report['reason']=str(exc);report.pop('summary',None);report.pop('interpretation',None)
            encoded['report.json']=(canonical(report)+'\n').encode()
    for name,data in encoded.items():
        with (out/name).open('xb') as f:f.write(data)
    (out/'result.md').write_text(markdown(report))
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}
    (out/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],summary=report.get('summary'),reason=report.get('reason'),cost=budget.receipt()),indent=2))
    return 0 if report['status']=='COMPLETE' else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    raise SystemExit(run(parser.parse_args().output))
