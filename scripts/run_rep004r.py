"""EXP-REP-004R: one disclosed, six-exposure end-to-end engineering trial.

ONLY synthetic/public worlds. Never any historic DEV/FINAL or private oracle.
All archived REP004 data remain read-only; score artifacts are newly created.
"""
import argparse
import base64
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import zlib
from pathlib import Path

from packages.rep004 import (ARMS,BUDGETS,canonical,digest,learn,save,load,evaluate,
                             study_manifest,concept_matches,weights_for,catalog,
                             _edge_execution_matches,_composition_equivalent,activation_fixture)

EXPOSURES=(0,3,8,16,32,64)
OLD_RAW_SHA='70ee6d9c531e18d1576d05649469808375678aebda804036d3ccc7d83ca8b1b3'


def raw_bytes(obj):
    return (canonical(obj)+'\n').encode('utf-8')


def put(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=raw_bytes(obj)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def pack(path,obj):
    data=raw_bytes(obj)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(base64.b64encode(zlib.compress(data,9)).decode('ascii')+'\n',encoding='ascii')
    assert zlib.decompress(base64.b64decode(path.read_text().strip()))==data
    return hashlib.sha256(data).hexdigest(),len(data)


def effects(rows,st,control):
    families=sorted({r['family'] for r in rows if r['stratum']==st})
    effect=[]
    for f in families:
        lq={r['budget']:r for r in rows if r['stratum']==st and r['family']==f and r['arm']=='LQ'}
        other={r['budget']:r for r in rows if r['stratum']==st and r['family']==f and r['arm']==control}
        assert set(lq)==set(other)==set(BUDGETS)
        effect.append({'family':f,'effect':round(sum(lq[b]['score']-other[b]['score'] for b in BUDGETS)/len(BUDGETS),9),
                       'better_budget_count':sum(lq[b]['score']>other[b]['score'] for b in BUDGETS),
                       'worse_budget_count':sum(lq[b]['score']<other[b]['score'] for b in BUDGETS)})
    return {'mean':round(sum(f['effect'] for f in effect)/len(effect),9),
            'positive_families':sum(f['effect']>0 for f in effect),
            'negative_families':sum(f['effect']<0 for f in effect),
            'tied_families':sum(f['effect']==0 for f in effect),
            'per_family':effect}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--source-sha',required=True)
    args=parser.parse_args()
    if len(args.source_sha)!=40 or any(c not in '0123456789abcdef' for c in args.source_sha):
        raise ValueError('source commit must be exact SHA40')
    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    manifest=study_manifest()
    # STOP gate: role binding, full-state macro, zero-training independent comparator.
    from packages.rep004 import PERMS,relabel,EDGES,step,motif
    static_models=list(catalog())[:80]
    s0=learn(0);s64=learn(64)
    eq=lambda s:weights_for(static_models,s,'STATIC-MACRO',{'body_invocations':0})
    assert eq(s0)==eq(s64) and any(v>1 for v in eq(s0))
    for edge in EDGES:
        orig=concept_matches(s64,(edge,))
        for perm in PERMS:
            renamed=relabel((edge,),perm)
            assert orig==concept_matches(s64,renamed)
            for state in range(16):
                mapped=sum(((state>>i)&1)<<perm[i] for i in range(4))
                for pulse in range(4):
                    a=step(state,('pulse',pulse,None),(edge,))
                    b=step(mapped,('pulse',perm[pulse],None),renamed)
                    assert sum(((a>>i)&1)<<perm[i] for i in range(4))==b
    mechanism=activation_fixture(s64)
    assert mechanism['differs'], 'STOP: no corrected LQ/LA paid question switch in bounded disclosed development grid'
    print('G1-G2: PASS role permutations (24x60), 16 states/4 pulses, STATIC independent',flush=True)
    print('ACTIVATION '+canonical(mechanism),flush=True)

    meta={'experiment':'EXP-REP-004R','phase':'DISCLOSED_SYNTHETIC_CORRECTED',
          'source_head_sha':args.source_sha,'source_checkout':os.getenv('GITHUB_SHA','unknown'),
          'manifest_digest':manifest['digest'],'historical_raw_sha_read_only':OLD_RAW_SHA,
          'python':sys.version.split()[0],'platform':platform.platform(),
          'train_sizes':EXPOSURES,'budgets':BUDGETS,'arms':ARMS,
          'audit_per_trial':64,'record_count_expected':11520,
          'formal_holdout':False,'review_state':'PENDING_INDEPENDENT_EXACT_HEAD'}
    snapshots=[];stats=[];all_receipts=[]
    for n in EXPOSURES:
        t=time.process_time()
        snapshot=learn(n)
        train_cpu=time.process_time()-t
        sp=out/f'snapshot{n}.json'
        save(snapshot,sp)
        check=load(sp)
        assert check==snapshot
        sp_sha=hashlib.sha256(sp.read_bytes()).hexdigest()
        # Fresh interpreter: normal CLI in a separate child process, not same module.
        use=out/f'use{n}.json'
        u=subprocess.run([sys.executable,'-m','packages.rep004','use','--snapshot',str(sp),
                          '--world-index','501','--arm','LQ','--budget','8','--trace',str(use)],
                         capture_output=True,text=True,timeout=180)
        if u.returncode:raise RuntimeError('fresh USE failed: '+u.stderr[:300])
        trace=json.loads(use.read_text(encoding='utf-8'))
        assert trace['snapshot_digest']==snapshot['digest'] and trace['commit_digest']
        use_sha=hashlib.sha256(use.read_bytes()).hexdigest()
        t=time.process_time()
        scores=evaluate(snapshot)
        score_cpu=time.process_time()-t
        assert len(scores['rows'])==1920 and scores['record_count']==1920
        paid=sum(r['actions'] for r in scores['rows'])
        assert all(r['body_invocations']==r['semantic_cache_misses']+r['body_cache_hits'] for r in scores['rows'])
        raw_path=out/f'scored{n}-raw.json.zlib.b64'
        sha,length=pack(raw_path,scores)
        st='UNSEEN_COMPOSITION'
        fx={a:effects(scores['rows'],st,a) for a in ('LA','STATIC-MACRO','FA')}
        complete=[r for r in scores['rows'] if r['stratum']==st and r['arm'] in ('LQ','LA')]
        action_switch=sum(
            next(r for r in complete if r['family']==f and r['budget']==b and r['arm']=='LQ')['trace_actions']!=
            next(r for r in complete if r['family']==f and r['budget']==b and r['arm']=='LA')['trace_actions']
            for f in sorted({r['family'] for r in complete}) for b in BUDGETS)
        same=all(r['body_invocations']==r['semantic_cache_misses']+r['body_cache_hits'] for r in scores['rows'])
        v={'train_worlds':n,'distinct_semantic_train_families':snapshot['distinct_train_families'],
           'paid_train_actions':snapshot['paid_actions'],'snapshot_digest':snapshot['digest'],
           'snapshot_file_sha256':sp_sha,'library_size':len(snapshot['library']),
           'concept_ops':sorted({b['ast']['op']+':'+b['ast'].get('shape','')+
                                 ':'+str(b['ast'].get('guard',{}).get('value',''))
                                 for b in snapshot['library']}),
           'fresh_use_file_sha256':use_sha,'fresh_use_actions':trace['meter']['actions'],
           'fresh_use_status':trace['status'],'fresh_use_commit_digest':trace['commit_digest'],
           'scores_raw_sha256':sha,'scores_raw_bytes':length,'trial_rows':len(scores['rows']),
           'evaluation_paid_actions':paid,'evaluation_model_checks':sum(r['model_checks'] for r in scores['rows']),
           'logical_body_invocations':sum(r['body_invocations'] for r in scores['rows']),
           'semantic_cache_misses':sum(r['semantic_cache_misses'] for r in scores['rows']),
           'physical_interpreter_calls':sum(r['physical_interpreter_calls'] for r in scores['rows']),
           'body_cache_hits':sum(r['body_cache_hits'] for r in scores['rows']),
           'meter_identity_check':same,'train_cpu_seconds':round(train_cpu,6),
           'evaluation_cpu_seconds':round(score_cpu,6),
           'scores_summary':scores['summary'],'primary_family_deltas':fx,
           'LQ_LA_question_switches_out_of_60':action_switch,
           'seen_stratum_actually_trained_count':len({r['family'] for r in scores['rows']
                if r['stratum']=='SEEN_ROLEBLIND' and r['seen_in_train']}),
           'ood_topology_count':1,'ood_abstentions':sum(r['status']=='ABSTAIN' for r in scores['rows']
                if r['stratum']=='OUT_OF_GRAMMAR')}
        stats.append(v)
        all_receipts.append({'train_worlds':n,'score_raw_sha256':sha,
                             'snapshot_sha256':sp_sha,'use_sha256':use_sha})
        put(out/f'summary{n}.json',v)
        compact={k:v[k] for k in ('train_worlds','distinct_semantic_train_families','library_size',
                 'evaluation_paid_actions','scores_raw_sha256','scores_summary',
                 'LQ_LA_question_switches_out_of_60','ood_abstentions')}
        compact['effects']={k:{a:t for a,t in v['primary_family_deltas'][k].items() if a!='per_family'}
                            for k in v['primary_family_deltas']}
        print('RESULT '+canonical(compact),flush=True)
    totals={'trials':sum(x['trial_rows'] for x in stats),
            'train_actions':sum(x['paid_train_actions'] for x in stats),
            'evaluation_actions':sum(x['evaluation_paid_actions'] for x in stats),
            'audit_transitions':sum(x['trial_rows'] for x in stats)*64,
            'snapshot_count':len(stats),'raw_source_receipts':all_receipts}
    assert totals['trials']==11520 and totals['audit_transitions']==737280
    s={'run':meta,'totals':totals,'exposures':stats,'decision':
       'ENGINEERING_DISCLOSED_ONLY; no model promotion or independent scientific claim'}
    idx_sha=put(out/'experiment-summary.json',s)
    print('FINAL_COUNTS '+canonical(totals),flush=True)
    print('FINAL_SUMMARY_SHA256 '+idx_sha,flush=True)
    print('ARTIFACTS '+str(out),flush=True)


if __name__=='__main__':main()
