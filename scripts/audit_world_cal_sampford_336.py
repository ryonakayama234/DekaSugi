#!/usr/bin/env python3
"""Pre-CAL source-only Sampford real-N audit; NEVER materializes sealed allocation.

The approved generator quotas prove a q MULTISET: 72 * 1/160 and
264 * 1/480. Indices here are artificial weight-class positions only.
All n=2..336 are checked, including the certainty transition at n=160.
Cross-reference is independent exact rational group-count enumeration.
"""
import argparse
import hashlib
import json
import math
import platform
import sys
from fractions import Fraction as F
from math import comb

from world_cal.sampford import waterfill
from world_cal.sampford_grouped import grouped_inclusions, draw_grouped

N=336
Q=(1/160,)*72+(1/480,)*264
TOL=1e-10


def rational_group_reference(n):
    """Returns (aa,ab,bb) as exact Fractions for the real-N public q multiset."""
    if n==N: return F(1),F(1),F(1)
    if n>=160:
        k=n-72
        return F(1),F(k,264),F(k*(k-1),264*263)
    a,b=F(n,160),F(n,480)
    terms=[]
    for ka in range(max(0,n-264),min(n,72)+1):
        kb=n-ka
        w=(F(comb(72,ka)*comb(264,kb))*(a/(1-a))**ka
           *(b/(1-b))**kb*(ka*(1-a)+kb*(1-b)))
        terms.append((ka,kb,w))
    z=sum((t[2] for t in terms),F(0))
    if z<=0: raise ArithmeticError("zero exact reference normalizer")
    aa=sum((ka*(ka-1)*w for ka,kb,w in terms),F(0))/z/F(72*71)
    ab=sum((ka*kb*w for ka,kb,w in terms),F(0))/z/F(72*264)
    bb=sum((kb*(kb-1)*w for ka,kb,w in terms),F(0))/z/F(264*263)
    return aa,ab,bb


def audit():
    records=[]
    maximum_error=0.0
    minimum_pair=1.0
    for n in range(2,N+1):
        pi=waterfill(Q,n)
        p,pij=grouped_inclusions(pi)
        aa,ab,bb=rational_group_reference(n)
        refs=(float(aa),float(ab),float(bb))
        actual=(pij[0][1],pij[0][100],pij[100][101])
        errors=[abs(a-b) for a,b in zip(actual,refs)]
        row_error=max(errors)
        if row_error>TOL:raise ArithmeticError("exact rational cross-check failed at n="+str(n))
        residual=max(abs(math.fsum(pij[i])-(n-1)*p[i]) for i in range(N))
        if residual>TOL:raise ArithmeticError("size identity failed at n="+str(n))
        if abs(math.fsum(p)-n)>TOL:raise ArithmeticError("first-order size failed")
        if any(pij[i][j]!=pij[j][i] for i in range(N) for j in (0,71,72,335) if i!=j):
            raise ArithmeticError("symmetry failure")
        minpair=min(pij[i][j] for i in range(N) for j in (0,72,335) if i!=j)
        if minpair<=0:raise ArithmeticError("degenerate joint inclusion")
        maximum_error=max(maximum_error,row_error,residual)
        minimum_pair=min(minimum_pair,minpair)
        signature=hashlib.sha256(
            ("|".join(float.hex(x) for x in (p[0],p[100],*actual))).encode("ascii")
        ).hexdigest()
        records.append({"n":n,"certainty_count":sum(x==1 for x in p),
                        "min_pair":minpair,"max_identity_abs_error":residual,
                        "max_rational_pair_abs_error":row_error,
                        "class_pair_sha256":signature})
    return {"kind":"PUBLIC_Q_MULTISET_NO_SEALED_IDS_PRECAL_NUMERICAL_AUDIT",
            "status":"CANDIDATE_INDEPENDENT_SUPERVISOR_RECHECK_REQUIRED",
            "N":N,"q_multiset":{"1/160":72,"1/480":264},
            "n_checked":list(range(2,N+1)),"tol":TOL,
            "max_residual":maximum_error,"min_pair":minimum_pair,
            "certainty_transition":160,
            "python":platform.python_version(),"platform":platform.platform(),
            "rows":records,
            "limitations":"No split, law ID, or parent-cluster assignment; no CAL or simulation. "
            "Algebraic equality checked against separate exact rational group-count law "
            "for all n. Final audit must validate authorized metadata and environment."}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    args=ap.parse_args()
    report=audit()
    raw=json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.output:
        with open(args.output,"w",encoding="utf-8",newline="\n") as f:f.write(raw)
    else: print(raw)
