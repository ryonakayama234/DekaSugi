"""Deterministic lean-editor/1 semantics and bounded typed data AST interpreter."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json

SYMS = ('A', 'B', 'C', 'D')
OPS = ('MOVE_LEFT', 'MOVE_RIGHT', 'INSERT', 'DELETE_BACK', 'DELETE_RIGHT',
       'SET_ANCHOR', 'EXTEND_LEFT', 'EXTEND_RIGHT', 'COPY', 'PASTE',
       'CLEAR_SELECTION')
TOKENS = tuple((op, sym) for op in OPS for sym in (SYMS if op == 'INSERT' else (None,)))
READS = ('cursor', 'prev', 'next', 'first', 'last')
MAX_BUFFER = 16
MAX_STEPS = 12
MAX_NODES = 32
MAX_DEPTH = 6

class Fault(ValueError):
    """Invalid input, AST or step; terminal unsuccessful attempt."""

def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')

def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

@dataclass(frozen=True)
class State:
    buffer: tuple[str, ...]
    cursor: int
    selection: tuple[int, int] | None = None  # anchor, head
    clipboard: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (type(self.buffer) is not tuple or any(type(x) is not str or x not in SYMS for x in self.buffer)
                or len(self.buffer) > MAX_BUFFER or type(self.cursor) is not int
                or not 0 <= self.cursor <= len(self.buffer)
                or type(self.clipboard) is not tuple or len(self.clipboard) > MAX_BUFFER
                or any(type(x) is not str or x not in SYMS for x in self.clipboard)):
            raise Fault('invalid state')
        if self.selection is not None:
            if (type(self.selection) is not tuple or len(self.selection) != 2
                    or any(type(x) is not int for x in self.selection)
                    or not all(0 <= x <= len(self.buffer) for x in self.selection)
                    or self.cursor != self.selection[1]):
                raise Fault('invalid selection/head/cursor')

    def record(self) -> dict:
        return {'buffer': list(self.buffer), 'cursor': self.cursor,
                'selection': list(self.selection) if self.selection is not None else None,
                'clipboard': list(self.clipboard)}

    @classmethod
    def parse(cls, obj: dict) -> 'State':
        if type(obj) is not dict or set(obj) != {'buffer','cursor','selection','clipboard'}:
            raise Fault('state schema')
        if type(obj['buffer']) is not list or type(obj['clipboard']) is not list:
            raise Fault('state list schema')
        sel = obj['selection']
        if sel is not None and (type(sel) is not list or len(sel) != 2):
            raise Fault('state selection schema')
        return cls(tuple(obj['buffer']), obj['cursor'], None if sel is None else tuple(sel), tuple(obj['clipboard']))

def _range(state: State) -> tuple[int, int] | None:
    if state.selection is None:
        return None
    a, h = state.selection
    if a == h:
        return None
    return min(a, h), max(a, h)

def step(s: State, action: tuple[str, str | None]) -> State:
    if type(action) is not tuple or len(action) != 2 or action not in TOKENS:
        raise Fault('invalid atomic token')
    op, arg = action
    b, c, sel, cb = s.buffer, s.cursor, s.selection, s.clipboard
    if op in ('MOVE_LEFT', 'MOVE_RIGHT'):
        c = max(0, c-1) if op == 'MOVE_LEFT' else min(len(b), c+1)
        return State(b, c, None, cb)
    if op == 'SET_ANCHOR':
        return State(b, c, (c, c), cb)
    if op in ('EXTEND_LEFT', 'EXTEND_RIGHT'):
        if sel is None:
            return s
        n = max(0, c-1) if op == 'EXTEND_LEFT' else min(len(b), c+1)
        return State(b, n, (sel[0], n), cb)
    if op == 'CLEAR_SELECTION':
        return State(b, c, None, cb)
    r = _range(s)
    if op == 'COPY':
        return State(b, c, sel, b[r[0]:r[1]]) if r is not None else s
    if op in ('INSERT','PASTE'):
        content = (arg,) if op == 'INSERT' else cb
        if not content:
            return s
        start, end = r if r is not None else (c, c)
        if len(b) - (end-start) + len(content) > MAX_BUFFER:
            return s
        return State(b[:start] + content + b[end:], start+len(content), None, cb)
    if op in ('DELETE_BACK','DELETE_RIGHT'):
        if r is None:
            if op == 'DELETE_BACK':
                if c == 0:
                    return State(b, c, None, cb)
                r = (c-1,c)
            else:
                if c == len(b):
                    return State(b, c, None, cb)
                r = (c,c+1)
        return State(b[:r[0]] + b[r[1]:], r[0], None, cb)
    raise Fault('unreachable')

def read(state: State, term: list) -> str | None:
    if type(term) is not list or len(term) != 2 or term[0] != 'READ' or term[1] not in READS:
        raise Fault('invalid read')
    index = {'cursor':state.cursor,'prev':state.cursor-1,'next':state.cursor+1,
             'first':0,'last':len(state.buffer)-1}[term[1]]
    return state.buffer[index] if 0 <= index < len(state.buffer) else None

def eval_predicate(s: State, p: list) -> bool:
    if type(p) is not list or len(p) != 3 or p[0] not in ('EQ','NE'):
        raise Fault('invalid predicate')
    left, right = read(s,p[1]),read(s,p[2])
    if left is None or right is None:
        return False
    return (left==right) if p[0]=='EQ' else (left!=right)

def _validate_ast(ast: list, depth: int = 1) -> int:
    if type(ast) is not list or not ast or depth > MAX_DEPTH:
        raise Fault('invalid AST/depth')
    k = ast[0]
    if k == 'OP':
        if len(ast) not in (2,3) or ast[1] not in OPS:
            raise Fault('invalid primitive AST')
        if ast[1] == 'INSERT':
            if len(ast)!=3:
                raise Fault('missing INSERT arg')
            arg=ast[2]
            if type(arg) is not list or len(arg)!=2 or (arg[0]=='SYM' and (type(arg[1]) is not str or arg[1] not in SYMS)):
                raise Fault('invalid symbol expression')
            if arg[0]=='READ':
                read(State(('A',),0),arg)  # type-check only
            elif arg[0]!='SYM':
                raise Fault('invalid symbol expression kind')
        elif len(ast)!=2:
            raise Fault('extraneous argument')
        return 1 + (1 if len(ast)==3 else 0)
    if k=='CALL':
        if len(ast)!=2 or type(ast[1]) is not str or len(ast[1])!=16:
            raise Fault('invalid macro call')
        return 1
    if k=='SEQ':
        if len(ast)<2:
            raise Fault('empty sequence')
        return 1+sum(_validate_ast(x,depth+1) for x in ast[1:])
    if k=='IF':
        if len(ast)!=4:
            raise Fault('invalid branch')
        pred=ast[1]
        eval_predicate(State(('A','B'),1),pred)
        return 1+3+_validate_ast(ast[2],depth+1)+_validate_ast(ast[3],depth+1)
    raise Fault('unknown AST tag')

def normalize(ast: list) -> list:
    """Only associative sequence normalization; no semantic rewrite or data-dependent repair."""
    if type(ast) is not list or not ast:
        raise Fault('invalid AST')
    if ast[0]=='SEQ':
        children=[]
        for node in ast[1:]:
            n=normalize(node)
            children.extend(n[1:] if n[0]=='SEQ' else (n,))
        if not children:
            raise Fault('empty sequence')
        return children[0] if len(children)==1 else ['SEQ',*children]
    if ast[0]=='IF' and len(ast)==4:
        return ['IF',ast[1],normalize(ast[2]),normalize(ast[3])]
    return ast

def expanded_nodes(ast: list, library: dict[str,list] | None = None,
                   *, allow_calls: bool = True) -> int:
    """Count call-expanded AST nodes (including CALL wrapper) and reject recursion."""
    library=library or {}
    def visit(node: list, depth: int, stack: tuple[str,...]) -> int:
        if depth>MAX_DEPTH:raise Fault('expanded AST depth')
        if node[0]=='CALL':
            key=node[1]
            if not allow_calls or key not in library or key in stack:
                raise Fault('unavailable/cyclic learned CALL')
            return 1+visit(normalize(library[key]),depth+1,stack+(key,))
        if node[0]=='SEQ':return 1+sum(visit(x,depth+1,stack) for x in node[1:])
        if node[0]=='IF':return 4+visit(node[2],depth+1,stack)+visit(node[3],depth+1,stack)
        return 1+(len(node)==3)
    n=visit(ast,1,())
    if n>MAX_NODES:raise Fault('expanded AST too large')
    return n

def execute(ast: list, s: State, library: dict[str,list] | None = None, *, allow_calls: bool = True) -> tuple[State, int, bool]:
    ast=normalize(ast)
    if _validate_ast(ast)>MAX_NODES:
        raise Fault('AST too large')
    expanded_nodes(ast,library,allow_calls=allow_calls)
    count=0
    used=False
    stack=[]
    library=library or {}
    def go(node: list, current: State) -> State:
        nonlocal count,used
        if node[0]=='CALL':
            if not allow_calls: raise Fault('OFF: learned AST calls disabled')
            key=node[1]
            if key not in library or key in stack or len(stack)>=MAX_DEPTH:
                raise Fault('missing/cyclic macro')
            used=True
            stack.append(key)
            try: return go(normalize(library[key]), current)
            finally: stack.pop()
        if node[0]=='SEQ':
            for ch in node[1:]: current=go(ch,current)
            return current
        if node[0]=='IF':
            return go(node[2] if eval_predicate(current,node[1]) else node[3], current)
        op=node[1]
        if count >= MAX_STEPS:
            raise Fault('program exceeds 12 primitives')
        arg=None
        if op=='INSERT':
            v=node[2]
            arg=v[1] if v[0]=='SYM' else read(current,v)
            if arg not in SYMS:
                raise Fault('read undefined at INSERT')
        count+=1
        return step(current,(op,arg))
    end=go(ast,s)
    return end,count,used

@dataclass
class Session:
    state: State
    calls: int = 0
    finished: bool = False
    result: bool | None = None

    def apply(self, action: tuple[str,str|None] | str, target: State | None = None) -> None:
        if self.finished:
            raise Fault('terminal session')
        if action == 'finish':
            if target is None:
                raise Fault('target must remain evaluator-only')
            self.finished=True
            self.result=(self.state==target)
            return
        self.state=step(self.state,action)
        self.calls+=1
        if self.calls==MAX_STEPS:
            if target is None:
                raise Fault('target must remain evaluator-only')
            self.finished=True
            self.result=(self.state==target)
