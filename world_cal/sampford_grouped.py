"""Exact two-mass Sampford law, including certainty units.

The enumeration is over GROUP COUNTS, not a sampling approximation: for a
residual sample of size k, each subset S has probability proportional to
prod_{i in S}(pi_i/(1-pi_i)) * sum_{i in S}(1-pi_i).
Every subgroup of a fixed count is equiprobable. No held-out IDs are needed.
"""
import math
from itertools import groupby

from .sampford import SamplingUnknown

TOL = 1e-10


def _design(pi):
    p = tuple(float(x) for x in pi)
    n = round(math.fsum(p))
    if not 2 <= n <= len(p) or any(not 0 < x <= 1 or not math.isfinite(x) for x in p):
        raise SamplingUnknown("STOP_UNKNOWN: invalid Sampford design")
    if abs(math.fsum(p) - n) > TOL:
        raise SamplingUnknown("STOP_UNKNOWN: sample size inconsistent with pi")
    certain = tuple(i for i, x in enumerate(p) if x == 1)
    groups = [(v, tuple(i for i, x in enumerate(p) if x == v))
              for v in sorted(set(p)) if v < 1]
    if len(groups) > 2:
        raise SamplingUnknown("STOP_UNKNOWN: exact grouped law supports at most two residual masses")
    return p, n, certain, groups


def _group_count_law(groups, k):
    if not groups:
        if k: raise SamplingUnknown("STOP_UNKNOWN: no residual units")
        return (((), 1.0),)
    if len(groups) == 1:
        m = len(groups[0][1])
        if not 0 <= k <= m: raise SamplingUnknown("STOP_UNKNOWN: impossible count")
        return (((k,), 1.0),)
    (pa, ia), (pb, ib) = groups
    ma, mb = len(ia), len(ib)
    terms = []
    for ka in range(max(0, k-mb), min(k,ma)+1):
        kb = k-ka
        weight = ka*(1-pa)+kb*(1-pb)
        if weight <= 0: continue
        logw = (math.lgamma(ma+1)-math.lgamma(ka+1)-math.lgamma(ma-ka+1)
                +math.lgamma(mb+1)-math.lgamma(kb+1)-math.lgamma(mb-kb+1)
                +ka*math.log(pa/(1-pa)) +kb*math.log(pb/(1-pb))
                +math.log(weight))
        terms.append(((ka,kb),logw))
    if not terms: raise SamplingUnknown("STOP_UNKNOWN: Sampford partition zero")
    shift = max(w for _, w in terms)
    denom = math.fsum(math.exp(w-shift) for _,w in terms)
    if not denom > 0 or not math.isfinite(denom):
        raise SamplingUnknown("STOP_UNKNOWN: Sampford normalizer invalid")
    out = tuple((counts,math.exp(w-shift)/denom) for counts,w in terms)
    if abs(math.fsum(prob for _,prob in out)-1)>TOL:
        raise SamplingUnknown("STOP_UNKNOWN: Sampford mass sum")
    return out


def grouped_inclusions(pi, tol=TOL):
    """Binary64 exact-law pi_ij, checked against first-order and size identities.

    This is an analytic COUNT COLLAPSE of the exact Sampford subset law.
    It is not a Poisson / PPS-with-replacement approximation.
    """
    p,n,certain,groups = _design(pi)
    N=len(p)
    k=n-len(certain)
    law=_group_count_law(groups,k)
    if not groups and k: raise SamplingUnknown("STOP_UNKNOWN: invalid certainties")
    marginal={}
    joint={}
    for g,(value,indices) in enumerate(groups):
        m=len(indices)
        mean=math.fsum(counts[g]*w for counts,w in law)
        marginal[g]=mean/m
        joint[g,g]=(math.fsum(counts[g]*(counts[g]-1)*w for counts,w in law)
                    /(m*(m-1)) if m>1 else 0.0)
    if len(groups)==2:
        a,b=groups
        joint[0,1]=joint[1,0]=math.fsum(c[0]*c[1]*w for c,w in law)/(len(a[1])*len(b[1]))
    assignment={i:g for g,(_,indices) in enumerate(groups) for i in indices}
    sure=set(certain)
    matrix=[]
    for i in range(N):
        row=[]
        for j in range(N):
            if i==j: x=0.0
            elif i in sure and j in sure: x=1.0
            elif i in sure: x=p[j]
            elif j in sure: x=p[i]
            else: x=joint[assignment[i],assignment[j]]
            row.append(x)
        matrix.append(tuple(row))
    for i in range(N):
        if i not in sure and abs(marginal[assignment[i]]-p[i]) > tol:
            raise SamplingUnknown("STOP_UNKNOWN: first-order Sampford mismatch")
        if any(i!=j and (matrix[i][j] <= 0 or matrix[i][j] > min(p[i],p[j])+tol)
               for j in range(N)):
            raise SamplingUnknown("STOP_UNKNOWN: degenerate pi_ij")
        if abs(math.fsum(matrix[i])-(n-1)*p[i]) > tol:
            raise SamplingUnknown("STOP_UNKNOWN: Sampford size identity mismatch")
    return p,tuple(matrix)


def draw_grouped(pi, uniforms):
    """Draw an exact fixed-size subset using independent injected open uniforms.

    One uniform selects the exact conditional GROUP COUNT. One uniform for each
    residual law gives a uniform size-k subset in that group (ties by index).
    Certainties are included without consuming random inputs.
    """
    p,n,certain,groups=_design(pi)
    law=_group_count_law(groups,n-len(certain))
    stream=iter(uniforms)
    if not groups: return tuple(range(len(p)))
    try: u=next(stream)
    except StopIteration as exc: raise SamplingUnknown("STOP_UNKNOWN: missing count draw") from exc
    if not math.isfinite(u) or not 0<u<1:
        raise SamplingUnknown("STOP_UNKNOWN: bad count uniform")
    cumulative=0.0
    counts=law[-1][0]
    for possible,prob in law:
        cumulative+=prob
        if u<cumulative:
            counts=possible
            break
    selected=list(certain)
    for g,(_,indices) in enumerate(groups):
        ranks=[]
        for i in indices:
            try: u=next(stream)
            except StopIteration as exc: raise SamplingUnknown("STOP_UNKNOWN: missing subset draw") from exc
            if not math.isfinite(u) or not 0<u<1:
                raise SamplingUnknown("STOP_UNKNOWN: bad subset uniform")
            ranks.append((u,i))
        selected.extend(i for _,i in sorted(ranks)[:counts[g]])
    if len(selected)!=n:raise SamplingUnknown("STOP_UNKNOWN: wrong exact sample size")
    return tuple(sorted(selected))
