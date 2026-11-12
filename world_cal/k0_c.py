"""Finite exact-support K0-c oracle and L90 search, FAIL-CLOSED on incompleteness.

A purported oracle curve is accepted ONLY with a certified exhaustive Space
iterator and a complete abstract instance distribution. No sealed samples
or targets are read. If those preconditions cannot be established, UNKNOWN
is mandatory; partial single-program or shortest-path curves are NOT used
as exact oracle evidence. This module does not run at import or in CI.
"""
import math
from collections import deque
from dataclasses import dataclass

from .gtheta import trapezoid
from .k0_oracle import nearest_rank90, OracleUnknown
from .space import Node, eval_expr, validate, ASTFault
from .world import State, World

MAX_NODES=2_000_000
# All 63-atom SEQ programs are distinct size-64/depth-2 canonical Space ASTs.
# This proves an unconditional syntactic Space lower bound.
SPACE_SYNTAX_LOWER_BOUND=14**63
T_HORIZON=24
CONTROLS=("H+","FIXED-IF","PRED-ONLY","REC","RANK-ONLY","LOOKUP","OFF")


@dataclass(frozen=True)
class AbstractCell:
    initial: tuple[str,...]
    verifier: object
    weight: float
    alphabet: tuple[str,...]

    def __post_init__(self):
        if not callable(self.verifier) or not 0<self.weight<=1:
            raise OracleUnknown("bad abstract source cell")
        if len(self.alphabet)!=4 or len(set(self.alphabet))!=4:
            raise OracleUnknown("not a four-symbol live alphabet")


def shortest_path_abstract(cell,*,cap=MAX_NODES,horizon=T_HORIZON):
    try:
        if type(cap) is not int or not 1<=cap<=MAX_NODES:
            raise OracleUnknown("invalid registered node cap")
        return _shortest_path_abstract(cell,cap=cap,horizon=horizon)
    except (OracleUnknown,ValueError,TypeError,StopIteration,RecursionError,MemoryError):
        return {"status":"UNKNOWN","length":None}


def _shortest_path_abstract(cell,*,cap,horizon):
    """Exact BFS shortest primitive path or UNKNOWN (no early negative)."""
    w=World(cell.alphabet,cell.verifier,horizon=horizon)
    w.reset(cell.initial)
    if w.success:return {"status":"REACHABLE","length":0,"nodes":1}
    queue=deque([(w.state,0)])
    seen={(w.state,0)}
    actions=w.legal_actions()
    while queue:
        state,t=queue.popleft()
        if t>=horizon:continue
        for action in actions:
            v=World(cell.alphabet,cell.verifier,horizon=horizon)
            v.state=state;v.calls=t
            v.step(action)
            if v.success:
                return {"status":"REACHABLE","length":t+1,"nodes":len(seen)}
            node=(v.state,t+1)
            if node in seen:continue
            if len(seen)>=cap:
                return {"status":"UNKNOWN","length":None,"nodes":len(seen)}
            seen.add(node)
            queue.append(node)
    return {"status":"UNREACHABLE","length":None,"nodes":len(seen)}


def complete_l90(cells,*,support_complete,cap=MAX_NODES):
    """Do not omit missing/failed/UNKNOWN distances when computing rank-90."""
    if (not isinstance(support_complete,dict) or
            support_complete.get("law_instance_demo_support_exhausted") is not True
            or support_complete.get("weights_audited") is not True or not cells):
        raise OracleUnknown("STOP_UNKNOWN: missing complete CAL abstract support")
    distances=[]
    for cell in cells:
        result=shortest_path_abstract(cell,cap=cap)
        if result["status"]!="REACHABLE":
            raise OracleUnknown("STOP_UNKNOWN: incomplete oracle shortest path")
        distances.append(result["length"])
    return nearest_rank90(distances)


def exhaustive_k0c_curve(*,cells,space_candidates,space_complete,
                          support_complete,b_final,
                          control_curves,cap=MAX_NODES):
    # Reject inflated caps: a caller cannot bypass the proven syntax lower
    # bound with a huge integer and a forged one-program 'complete' receipt.
    if type(cap) is not int or not 1<=cap<=MAX_NODES:
        return {"status":"UNKNOWN","reason":"invalid registered enumeration cap"}
    try:
        return _exhaustive_k0c_curve(cells=cells,space_candidates=space_candidates,
            space_complete=space_complete,support_complete=support_complete,
            b_final=b_final,control_curves=control_curves,cap=cap)
    except (OracleUnknown,ValueError,TypeError,KeyError,StopIteration,
            RecursionError,MemoryError):
        return {"status":"UNKNOWN","reason":"incomplete oracle enumeration"}


def _exhaustive_k0c_curve(*,cells,space_candidates,space_complete,
                          support_complete,b_final,
                          control_curves,cap=MAX_NODES):
    """Maximal success rate at each registered checkpoint over entire Space.

    The supplied Space iterator must be COMPLETE and independently certified;
    a truncated enumerator cannot convert an oracle upper bound into an exact
    curve. All eight checkpoints and the 0-origin are preserved.
    """
    # Unqualified booleans are not completeness certificates. In particular,
    # the source 384-law index census says nothing about demo draws, full
    # typed AST Space, or all seven control curves. Require separately
    # auditable, exhausted finite iterator receipts before claiming COMPLETE.
    if not isinstance(support_complete,dict) or not isinstance(space_complete,dict):
        return {"status":"UNKNOWN","reason":"Space/support completeness uncertified"}
    if not (support_complete.get("law_instance_demo_support_exhausted") is True
            and support_complete.get("weights_audited") is True
            and space_complete.get("typed_space_exhausted") is True
            and space_complete.get("control_curves_exhausted") is True
            and isinstance(space_complete.get("canonical_space_sha256"),str)
            and space_complete.get("canonical_space_count",0)>0):
        return {"status":"UNKNOWN","reason":"missing full typed Space/control/source receipts"}
    if cap<SPACE_SYNTAX_LOWER_BOUND:
        return {"status":"UNKNOWN","reason":"canonical Space exceeds enumeration cap",
                "lower_bound":str(SPACE_SYNTAX_LOWER_BOUND)}
    if b_final not in (4096,6144) or not cells or cap<1:
        return {"status":"UNKNOWN","reason":"invalid oracle inputs"}
    if abs(math.fsum(cell.weight for cell in cells)-1)>1e-10:
        return {"status":"UNKNOWN","reason":"incomplete support probability"}
    if set(control_curves)!=set(CONTROLS):
        return {"status":"UNKNOWN","reason":"missing seven control curves"}
    if any(len(curve)!=9 or any(not 0<=x<=1 for x in curve)
           for curve in control_curves.values()):
        return {"status":"UNKNOWN","reason":"invalid control curve"}
    checkpoints=tuple(j*b_final//8 for j in range(9))
    if any(j*b_final%8 for j in range(9)):
        return {"status":"UNKNOWN","reason":"nonintegral checkpoint"}
    best=[0.0]*9
    inspected=0
    for program in space_candidates:
        inspected+=1
        if inspected>cap:
            return {"status":"UNKNOWN","reason":"Space cap reached","nodes":inspected}
        try:validate(program)
        except ASTFault:
            return {"status":"UNKNOWN","reason":"untyped or illegal Space candidate"}
        primitive_total=0
        successes=0.0
        for cell in cells:
            w=World(cell.alphabet,cell.verifier,horizon=T_HORIZON)
            w.reset(cell.initial)
            try:eval_expr(program,w)
            except (ASTFault,ValueError,TypeError):
                return {"status":"UNKNOWN","reason":"incomplete program semantics"}
            primitive_total+=w.calls
            successes+=cell.weight*int(w.success)
        for j,budget in enumerate(checkpoints):
            if primitive_total<=budget and successes>best[j]:
                best[j]=successes
    if inspected==0 or inspected!=space_complete["canonical_space_count"]:
        return {"status":"UNKNOWN","reason":"Space iterator did not exhaust",
                "nodes":inspected}
    # j=0 is strictly zero primitive calls; the zero-budget candidate is
    # required to be present in the certified Space iterator.
    auc=trapezoid(best)
    best_control=max(trapezoid(control_curves[a]) for a in CONTROLS)
    return {"status":"COMPLETE","nodes":inspected,
            "oracle_curve":tuple(best),"oracle_AULC":auc,
            "best_control_AULC":best_control,
            "saturated":(auc-best_control)<.15,
            "opportunity_gap":auc-best_control,
            "precision":"exact abstract support/typed Space only"}
