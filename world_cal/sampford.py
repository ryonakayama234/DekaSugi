"""Sampford PPSWOR exact small-fixture subset reference; large case fails closed.

This is an exact *sampling law*, not a with-replacement or Poisson approximation.
A scalable vetted pi_ij implementation remains a blocking audit dependency.
"""
from fractions import Fraction
from itertools import combinations
from math import isfinite

class SamplingUnknown(ValueError): pass

def waterfill(q, n, tol=1e-12):
    q=tuple(float(x) for x in q)
    N=len(q)
    if not 2 <= n <= N or any(x<=0 or not isfinite(x) for x in q):
        raise SamplingUnknown("invalid n or q")
    total=sum(q)
    if total<=0: raise SamplingUnknown("invalid q total")
    q=tuple(x/total for x in q)
    lo,hi=0.0, max(1/x for x in q)
    for _ in range(100):
        mid=(lo+hi)/2
        if sum(min(1.0,mid*x) for x in q)<n: lo=mid
        else: hi=mid
    pi=tuple(min(1.0,hi*x) for x in q)
    if abs(sum(pi)-n)>tol:
        raise SamplingUnknown("waterfill accuracy")
    return pi

def exact_subset_law(pi, max_units=14):
    """Return all subset probabilities as Fractions; correct Sampford law.

    For residual pi, P(S) proportional to prod_i pi_i/(1-pi_i)
    times sum_i (1-pi_i), after certainties are removed.
    """
    pi=tuple(Fraction(x) for x in pi)
    n_round=round(sum(pi))
    if sum(pi)!=n_round or n_round<2:
        raise SamplingUnknown("expected exact integer target n>=2")
    N=len(pi)
    if N>max_units:
        raise SamplingUnknown("exact enumeration exceeds audited size bound")
    sure=tuple(i for i,p in enumerate(pi) if p==1)
    rest=[i for i,p in enumerate(pi) if p<1]
    k=n_round-len(sure)
    if k==0:return {tuple(range(N)):Fraction(1)}
    if not 1 <= k <= len(rest) or any(pi[i]<=0 for i in rest):
        raise SamplingUnknown("residual design degenerate")
    weights={i:pi[i]/(1-pi[i]) for i in rest}
    raw={}
    for subset in combinations(rest,k):
        w=Fraction(1)
        for i in subset:w*=weights[i]
        raw[tuple(sorted(sure+subset))]=w*sum(1-pi[i] for i in subset)
    z=sum(raw.values(),Fraction(0))
    if not z:raise SamplingUnknown("zero normalizer")
    result={s:p/z for s,p in raw.items()}
    first,joint=inclusion(result,N)
    if any(abs(first[i]-pi[i])>Fraction(1,10**10) for i in range(N)):
        raise SamplingUnknown("Sampford first-order mismatch")
    return result

def inclusion(probs,N):
    first=[Fraction(0)]*N
    pair=[[Fraction(0)]*N for _ in range(N)]
    for s,p in probs.items():
        for i in s:
            first[i]+=p
            for j in s:
                if j!=i: pair[i][j]+=p
    return tuple(first),tuple(tuple(x) for x in pair)

def sample_from_exact_law(probs, u):
    """Pure inverse-CDF draw from an injected synthetic uniform; no seed creation."""
    if not 0 <= u < 1:raise SamplingUnknown("uniform out of range")
    cumulative=0.0
    for subset,p in sorted(probs.items()):
        cumulative+=float(p)
        if u<cumulative:return subset
    return next(reversed(sorted(probs)))
