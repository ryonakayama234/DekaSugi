"""Resource-bounded COMPLETE deterministic K0-b public-history AND/OR DP.

This is an abstract support solver, NOT a CAL/K0 run. It is forbidden to
materialize sealed law allocations or inject hidden law IDs into policy keys.
All successor actions are enumerated; node exhaustion returns UNKNOWN, never
a fabricated PASS or FAIL. TRAIN and EVAL are disjoint information models.
"""
import hashlib
from dataclasses import dataclass
from functools import lru_cache

from .world import State, World


class K0Unknown(ValueError):
    pass


@dataclass(frozen=True)
class K0Hypothesis:
    # law_digest is for PRIVATE auditor pairing only, never in public keys.
    law_digest: str
    instances: tuple[State,...]
    verifier: object    # callable(trial_index, buffer) -> bool, evaluator only
    demo_digest: str

    def __post_init__(self):
        if not self.law_digest or not self.instances or not self.demo_digest:
            raise K0Unknown("incomplete hypothesis")
        if not callable(self.verifier):raise K0Unknown("missing private verifier")


@dataclass(frozen=True)
class _Node:
    which: int
    trial: int
    step: int
    state: State
    history: tuple
    finished: bool=False
    success: bool=False


def _observation(state):
    # Public editor state, excluding private verifier, law and parent IDs.
    return (state.buffer,state.cursor,state.selection,state.clipboard,state.last_event)


def _start(hyp,which):
    return _Node(which,0,0,hyp.instances[0],
                 (("TAG_RENAMED",hyp.demo_digest,_observation(hyp.instances[0])),))


def _advance(node,hyp,action,mode,horizon):
    if node.finished:return node
    world=World(tuple("ABCD"),lambda b:hyp.verifier(node.trial,b),horizon=horizon)
    world.state=node.state
    world.calls=node.step
    _,done,success,event=world.step(action)
    history=node.history+(("ACT",action,_observation(world.state)),)
    if not done:
        return _Node(node.which,node.trial,node.step+1,world.state,history)
    # Feedback is emitted ONLY between TRAIN trials; never during EVAL.
    next_trial=node.trial+1
    if next_trial<len(hyp.instances) and mode=="TRAIN":
        state=hyp.instances[next_trial]
        history+=(("TRAIN_FEEDBACK",bool(success)),("NEXT_TRIAL",_observation(state)))
        return _Node(node.which,next_trial,0,state,history)
    return _Node(node.which,node.trial,node.step+1,world.state,history,True,bool(success))


def _policy_key(node):
    # Entire public history, NOT the hidden law digest/verifier/success bit.
    # A successful world may be absorbed and its remaining actions are irrelevant.
    return node.history


def solve_k0b_pair(left,right,*,mode,horizon=24,cap=2_000_000):
    """Returns PASS / FAIL / UNKNOWN for one *complete* abstract law pair.

    TRAIN: fixed multiple trials, feedback after each, only final trial must
    succeed; exploratory TRAIN failures are allowed.
    EVAL: exactly one episode and NO success/failure feedback.
    Every possible action is examined in Appendix A canonical 14-token order.
    """
    if mode not in ("TRAIN","EVAL") or not 1<=horizon<=64 or cap<=0:
        raise K0Unknown("invalid mode/bounds")
    if mode=="EVAL" and (len(left.instances)!=1 or len(right.instances)!=1):
        raise K0Unknown("EVAL must have exactly one trial")
    if mode=="TRAIN" and (len(left.instances)<2 or len(right.instances)<2 or
                          len(left.instances)!=len(right.instances)):
        raise K0Unknown("TRAIN requires equal multiple trials")
    if left.law_digest==right.law_digest:
        raise K0Unknown("K0-b requires distinct laws")
    actions=World(tuple("ABCD")).legal_actions()
    hypotheses=(left,right)
    seen=[0]
    class CapReached(Exception):pass

    @lru_cache(None)
    def rec(nodes):
        seen[0]+=1
        if seen[0]>cap:raise CapReached
        if any(node.finished and not node.success for node in nodes):
            return False
        if all(node.finished and node.success for node in nodes):
            return True
        active=tuple(node for node in nodes if not node.finished)
        if not active:return True
        grouped={}
        for node in active:
            grouped.setdefault(_policy_key(node),[]).append(node)
        if len(grouped)>1:
            # Histories are distinguishable; independently choose actions.
            return all(rec(tuple(group)) for _,group in sorted(grouped.items()))
        for action in actions:
            next_nodes=tuple(_advance(node,hypotheses[node.which],action,mode,horizon)
                             for node in active)
            if rec(next_nodes):return True
        return False

    try:
        wins=rec((_start(left,0),_start(right,1)))
    except (CapReached,RecursionError,MemoryError):
        return {"status":"UNKNOWN","nodes":seen[0],"mode":mode}
    return {"status":"PASS" if wins else "FAIL","nodes":seen[0],"mode":mode}


def scan_k0b_pairs(pairs,*,complete_support,cap=2_000_000):
    """All pairs from a separately certified COMPLETE abstract source iterator.

    No provisional PASS if a single pair is UNKNOWN. FAIL also waits for
    completeness because normative UNKNOWN takes precedence over FAIL.
    Caller supplies each (digest, train_left, train_right, eval_left, eval_right).
    """
    unknown=False
    fails=[]
    audited=0
    # A caller-supplied bool cannot certify a 73,536-pair Cartesian support.
    # A complete coverage receipt must also certify every demo/trial/EVAL path,
    # not just the 384-law index. These fields remain false until an actual
    # exhaustive, separately audited enumeration has finished.
    required=("law_pair_count","law_pairs_digest","demo_paths_exhausted",
              "train_paths_exhausted","eval_paths_exhausted")
    if not isinstance(complete_support,dict) or any(
            key not in complete_support for key in required):
        return {"status":"UNKNOWN","reason":"missing complete law/instance proof"}
    if (complete_support["law_pair_count"]!=73536 or
            not isinstance(complete_support["law_pairs_digest"],str) or
            not all(complete_support[key] is True
                    for key in required[2:])):
        return {"status":"UNKNOWN","reason":"unexhausted law/instance support"}
    pair_digests=set()
    for pair_digest,tr_l,tr_r,ev_l,ev_r in pairs:
        if pair_digest in pair_digests:
            return {"status":"UNKNOWN","reason":"duplicate law pair"}
        pair_digests.add(pair_digest)
        train=solve_k0b_pair(tr_l,tr_r,mode="TRAIN",cap=cap)
        test=solve_k0b_pair(ev_l,ev_r,mode="EVAL",cap=cap)
        audited+=1
        if "UNKNOWN" in (train["status"],test["status"]):unknown=True
        elif "FAIL" in (train["status"],test["status"]):
            fails.append({"pair_digest":pair_digest,
                          "train":train["status"],"eval":test["status"]})
    if audited!=complete_support["law_pair_count"]:
        return {"status":"UNKNOWN","reason":"law pair iterator did not exhaust",
                "pairs_audited":audited}
    return {"status":"UNKNOWN" if unknown else "FAIL" if fails else "PASS",
            "pairs_audited":audited,"failed_pairs":fails if not unknown else [],
            "unknown_prioritized":unknown}
