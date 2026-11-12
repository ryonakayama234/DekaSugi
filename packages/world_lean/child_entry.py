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
from world_lean import core as metered_core
from world_lean.learner import Learner, infer
from world_lean.protocol import B, ARMS


def respond(request: dict) -> dict:
    if type(request) is not dict or type(request.get('mode')) is not str:
        raise Fault('schema')
    wire_request=request
    symbols=request.get('symbols')
    if symbols is not None:
        if type(symbols) is not list or len(symbols)!=4 or len(set(symbols))!=4 or any(type(s) is not str for s in symbols):
            raise Fault('public token alphabet')
        request=dict(request)
        del request['symbols']
        def decode(value):
            if type(value) is list:return [decode(x) for x in value]
            if type(value) is dict:return {k:decode(v) for k,v in value.items()}
            return 'ABCD'[symbols.index(value)] if type(value) is str and value in symbols else value
        for key in ('blocks','demos','query'):
            if key in request:request[key]=decode(request[key])
    mode=request['mode']
    if mode=='boundary_probe':
        readable=False
        for private_path in ('private/master.bin','private/replicate-0.json','manifest.json'):
            try:
                with open(private_path,'rb') as private_stream:private_stream.read(1)
                readable=True
            except (FileNotFoundError,PermissionError):pass
        if set(request)!={'mode'}:raise Fault('forbidden keys')
        return {'evaluator_importable':importlib.util.find_spec('world_lean_evaluator') is not None,
                'sys_path':list(sys.path),'cwd':os.getcwd(),
                'private_relative_readable':readable}
    if mode=='train':
        if set(request) not in ({'mode','blocks'},{'mode','blocks','arm'},{'mode','blocks','arm','checkpoints'}) or type(request['blocks']) is not list:
            raise Fault('forbidden TRAIN metadata/target/seed')
        arm=request.get('arm','FULL')
        if arm not in ARMS or arm=='OFF':raise Fault('training arm')
        checkpoint_b=request.get('checkpoints',list(B))
        if type(checkpoint_b) is not list or any(type(b) is not int or b not in B+(64,) for b in checkpoint_b):
            raise Fault('public checkpoint schedule')
        learner=Learner()
        checkpoints={'0':base64.b64encode(learner.snapshot()).decode('ascii')}
        for block in request['blocks']:
            learner.add_block(block,acquire=arm=='FULL')
            if learner.events in checkpoint_b:
                checkpoints[str(learner.events)]=base64.b64encode(learner.snapshot()).decode('ascii')
        current=learner.snapshot()
        return {'snapshot_b64':base64.b64encode(current).decode('ascii'),
                'snapshot_sha256':__import__('hashlib').sha256(current).hexdigest(),
                'public_trace_digest':digest(wire_request['blocks']),
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
    answer['primitive_transitions']=metered_core.PRIMITIVE_TRANSITIONS
    sys.stdout.buffer.write(canonical(answer))
