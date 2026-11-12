"""Public-history projection / bounded coupled-policy DP; no implicit experiment."""
from .world import World

def public_projection(task_tag, demo_digest, initial, events):
    # Law/tag identity cannot be used as an oracle for public policies.
    return ("TAG", demo_digest, initial, tuple(events))

def separate_feedback(train_events,eval_events):
    """EVAL feedback must be absent, TRAIN feedback may be present."""
    if any(len(e)!=3 for e in train_events):
        raise ValueError("TRAIN requires (action,observation,feedback)")
    if any(len(e)!=2 for e in eval_events):
        raise ValueError("EVAL forbids feedback")
    return tuple(train_events), tuple(eval_events)

def conditional_pair_dp(*, initial_left,initial_right,alphabet,
                        verify_left,verify_right,horizon=24,cap=2_000_000):
    """Exact small-tree DP over coupled public histories, fail-closed on cap.

    Multiple actions may be chosen only when the public history differs.
    This implementation is limited to an episode pair, not K0-b law discovery.
    """
    actions=World(tuple(alphabet)).legal_actions()
    from functools import lru_cache
    budget=[0]
    class Cap(Exception): pass
    @lru_cache(None)
    def rec(s1,s2,h1,h2,d1,d2,t):
        budget[0]+=1
        if budget[0]>cap:raise Cap()
        if d1 and d2:return True
        if t==horizon:return False
        p1=tuple(h1)
        p2=tuple(h2)
        for a in actions:
            for b in (actions if p1!=p2 else (a,)):
                w1=World(tuple(alphabet),verify_left,horizon=horizon)
                w2=World(tuple(alphabet),verify_right,horizon=horizon)
                w1.state,w1.done,w1.success=s1,d1,d1
                w2.state,w2.done,w2.success=s2,d2,d2
                if not d1:w1.step(a)
                if not d2:w2.step(b)
                nh1=h1 if d1 else h1+((a,w1.observe()["buffer"]),)
                nh2=h2 if d2 else h2+((b,w2.observe()["buffer"]),)
                if rec(w1.state,w2.state,nh1,nh2,w1.success,w2.success,t+1):
                    return True
        return False
    try:
        result=rec(initial_left,initial_right,((None,initial_left.buffer),),
                   ((None,initial_right.buffer),),False,False,0)
    except (Cap,RecursionError):
        return {"status":"UNKNOWN","nodes":budget[0]}
    return {"status":"CONDITIONAL_WINS" if result else "CONDITIONAL_DOES_NOT_WIN",
            "nodes":budget[0]}
