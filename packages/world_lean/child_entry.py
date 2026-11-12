"""Dedicated public learner subprocess. Invoke with Python -I and private code root absent."""
from __future__ import annotations
import base64
import importlib.util
import json
import os
import sys

# In isolated mode script directory is omitted; add *only* this copied public root.
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world_lean.core import State, Fault, canonical, digest
from world_lean.learner import Learner, infer


def respond(request: dict) -> dict:
    if type(request) is not dict or type(request.get('mode')) is not str:
        raise Fault('schema')
    mode=request['mode']
    if mode=='boundary_probe':
        if set(request)!={'mode'}:raise Fault('forbidden keys')
        return {'evaluator_importable':importlib.util.find_spec('world_lean_evaluator') is not None,
                'sys_path':list(sys.path),'cwd':os.getcwd()}
    if mode=='train':
        if set(request)!={'mode','blocks'} or type(request['blocks']) is not list:
            raise Fault('forbidden TRAIN metadata/target/seed')
        learner=Learner()
        checkpoints={'0':base64.b64encode(learner.snapshot()).decode('ascii')}
        for block in request['blocks']:
            learner.add_block(block)
            if learner.events in (512,1024,2048,4096):
                checkpoints[str(learner.events)]=base64.b64encode(learner.snapshot()).decode('ascii')
        current=learner.snapshot()
        return {'snapshot_b64':base64.b64encode(current).decode('ascii'),
                'snapshot_sha256':__import__('hashlib').sha256(current).hexdigest(),
                'public_trace_digest':digest(request['blocks']),
                'checkpoints_b64':checkpoints,
                'events':learner.events,'updates':learner.updates}
    if mode=='infer':
        if set(request)!={'mode','snapshot_b64','arm','demos','query'}:
            raise Fault('forbidden evaluator metadata/target/seed')
        snap=base64.b64decode(request['snapshot_b64'],validate=True)
        demos=tuple((State.parse(a),State.parse(b)) for a,b in request['demos'])
        query=State.parse(request['query'])
        return infer(snap,request['arm'],demos,query)
    raise Fault('unknown mode')

if __name__=='__main__':
    try:
        raw=sys.stdin.buffer.readline(8_000_001)
        if not raw or not raw.endswith(b'\n'):raise Fault('missing/oversize request')
        obj=json.loads(raw)
        answer={'ok':True,'data':respond(obj)}
    except (Fault,ValueError,TypeError,KeyError,IndexError) as err:
        answer={'ok':False,'error':type(err).__name__+': '+str(err)}
    sys.stdout.buffer.write(canonical(answer))
