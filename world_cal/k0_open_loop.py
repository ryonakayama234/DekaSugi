"""Resource-bounded open-loop pair BFS. Never called implicitly."""
from collections import deque
from .world import World, State

UNKNOWN = "UNKNOWN"

def _advance(state, done, token, alphabet, verifier):
    if done:return state,True
    w=World(tuple(alphabet),verifier)
    w.state=state
    _,_,success,_=w.step(token)
    return w.state,success

def pair_bfs(left: State,right: State, alphabet, verify_left, verify_right,
             *, horizon=24,cap=2_000_000):
    actions=World(tuple(alphabet)).legal_actions()
    initial=(left,right,False,False)
    queue=deque([(initial,())])
    visited={initial}
    while queue:
        ((s1,s2,d1,d2),path)=queue.popleft()
        if d1 and d2:return {"status":"OPEN_LOOP_WINS","path":path,"nodes":len(visited)}
        if len(path)>=horizon:continue
        for token in actions:
            a,x=_advance(s1,d1,token,alphabet,verify_left)
            c,y=_advance(s2,d2,token,alphabet,verify_right)
            node=(a,c,x,y)
            if node in visited:continue
            if len(visited)>=cap:
                return {"status":UNKNOWN,"path":None,"nodes":len(visited)}
            visited.add(node)
            queue.append((node,path+(token,)))
    return {"status":"OPEN_LOOP_DOES_NOT_WIN","path":None,"nodes":len(visited)}

def trace_known_negative():
    """Only sanctioned known-pair golden control; no K0 discovery search."""
    tokens=("MOVE_RIGHT",)*4+("SET_ANCHOR",("INSERT","A"),"DELETE_BACK",
                              "SET_ANCHOR",("INSERT","C"))
    out=[]
    for initial,target in (("ABAB","ABABA"),("ADAD","ADADC")):
        w=World(tuple("ABCD"), lambda b,t=target: "".join(b)==t)
        w.reset(initial)
        for token in tokens:
            w.step(token)
        out.append((w.success,w.calls,"".join(w.state.buffer)))
    return tuple(out)
