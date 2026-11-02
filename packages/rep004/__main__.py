"""Disclosed engineering CLI, no private holdout access."""
import argparse
import json
from . import (learn,save,load,study_manifest,world_for,committed_use,evaluate,
               ARMS,BUDGETS,canonical,digest)
from pathlib import Path


def write(obj,path):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(canonical(obj)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    for cmd in ('preflight','train','inspect','use','evaluate-disclosed'):
        s=sub.add_parser(cmd)
        s.add_argument('--output')
        if cmd in ('train','inspect','use','evaluate-disclosed'):s.add_argument('--snapshot')
        if cmd=='train':s.add_argument('--train-worlds',type=int,default=64)
        if cmd=='use':
            s.add_argument('--world-index',type=int,default=501)
            s.add_argument('--budget',type=int,choices=BUDGETS,default=8)
            s.add_argument('--arm',choices=ARMS,default='LQ')
            s.add_argument('--trace')
    a=p.parse_args()
    if a.command=='preflight':o=study_manifest()
    elif a.command=='train':
        o=learn(a.train_worlds)
        if a.snapshot:save(o,a.snapshot)
    elif a.command=='inspect':o=load(a.snapshot)
    elif a.command=='use':
        m=study_manifest();f=m['composition'][a.world_index%12]
        o=committed_use(load(a.snapshot),world_for(f,a.world_index),a.arm,a.budget)
        if a.trace:write(o,a.trace)
    else:o=evaluate(load(a.snapshot))
    if a.output:write(o,a.output)
    else:print(json.dumps(o,indent=2,ensure_ascii=False) if a.command!='evaluate-disclosed' else json.dumps({'record_count':o['record_count'],'summary':o['summary']},indent=2))

if __name__=='__main__':main()