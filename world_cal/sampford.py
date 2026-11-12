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

def _poisson_binomial_weighted(probabilities):
    """Stable coefficients of ∏(1-p_i + p_i*t) and its sum(1-p_i) weighted counterpart."""
    E=[1.0]
    F=[0.0]
    for p in probabilities:
        a=1.0-p
        e=[0.0]*(len(E)+1)
        f=[0.0]*(len(E)+1)
        for k in range(len(E)):
            e[k]+=a*E[k]
            e[k+1]+=p*E[k]
            f[k]+=a*F[k]
            f[k+1]+=p*F[k]+a*p*E[k]
        E,F=e,f
    return E,F

def _remove_factor(E,F,p):
    """Polynomial quotient in stable direction (p or 1-p is >=1/2)."""
    a=1.0-p
    N=len(E)-1
    e=[0.0]*N
    f=[0.0]*N
    if a>=p:
        e[0]=E[0]/a
        f[0]=F[0]/a
        for k in range(1,N):
            e[k]=(E[k]-p*e[k-1])/a
            f[k]=(F[k]-p*f[k-1]-a*p*e[k-1])/a
    else:
        e[-1]=E[-1]/p
        f[-1]=(F[-1]-a*p*e[-1])/p
        for k in range(N-2,-1,-1):
            e[k]=(E[k+1]-a*e[k+1])/p
            f[k]=(F[k+1]-a*f[k+1]-a*p*e[k])/p
    return e,f

def exact_inclusions(pi,tol=1e-10):
    """O(N^3) algebraic pi_i/pi_ij from the SAME Sampford law, no approximation.

    Bernoulli likelihood ∏(p_i if selected else 1-p_i), conditioned on
    fixed sample size n, tilted by sum_{i in S}(1-p_i).
    This expression is exactly the accepted Sampford rejection law.
    The computation is floating binary64 and fails closed if identities
    cannot be certified to tol. No probabilistic approximation is used.
    """
    import math
    pi=tuple(float(x) for x in pi)
    N=len(pi)
    if N<2 or any(not (0<p<=1) or not math.isfinite(p) for p in pi):
        raise SamplingUnknown("invalid first-order probabilities")
    n=round(math.fsum(pi))
    if n<2 or n>N or abs(math.fsum(pi)-n)>tol:
        raise SamplingUnknown("invalid fixed sample size")
    if n==N:
        return tuple([1.0]*N),tuple(tuple(0.0 if i==j else 1.0
                       for j in range(N)) for i in range(N))
    E,F=_poisson_binomial_weighted(pi)
    norm=F[n]
    if not (norm>0 and math.isfinite(norm)):
        raise SamplingUnknown("degenerate Sampford normalizer")
    first=[0.0]*N
    pairs=[[0.0]*N for _ in range(N)]
    for i,p in enumerate(pi):
        e1,f1=_remove_factor(E,F,p)
        first[i]=p*(f1[n-1]+(1-p)*e1[n-1])/norm
        if not math.isfinite(first[i]) or abs(first[i]-p)>tol:
            raise SamplingUnknown("Sampford first-order consistency fail")
        for j in range(i+1,N):
            z=pi[j]
            e2,f2=_remove_factor(e1,f1,z)
            joint=p*z*(f2[n-2]+(2-p-z)*e2[n-2])/norm
            if not math.isfinite(joint) or joint<=0 or joint>min(p,z)+tol:
                raise SamplingUnknown("Sampford second-order positivity fail")
            pairs[i][j]=pairs[j][i]=joint
    for i in range(N):
        if abs(math.fsum(pairs[i])-(n-1)*pi[i])>tol:
            raise SamplingUnknown("Sampford exact pi_ij size identity fail")
    return tuple(pi),tuple(tuple(row) for row in pairs)

def _suffix_polynomials(pi):
    N=len(pi)
    suffix=[None]*(N+1)
    suffix[N]=([1.0],[0.0])
    for i in range(N-1,-1,-1):
        p=pi[i]
        e,f=suffix[i+1]
        a=1-p
        nex=[0.0]*(len(e)+1);nfx=[0.0]*(len(f)+1)
        for j in range(len(e)):
            nex[j]+=a*e[j]
            nex[j+1]+=p*e[j]
            nfx[j]+=a*f[j]
            nfx[j+1]+=p*f[j]+a*p*e[j]
        suffix[i]=(nex,nfx)
    return suffix

def draw_sampford(pi,uniforms):
    """Exact Sampford subset draw with injected independent uniforms.

    Uses weighted conditional DP; *never* constructs a seed or RNG and never
    substitutes Poisson, iid PPS, or iid draws with duplicates.
    """
    import math
    pi=tuple(float(x) for x in pi)
    N=len(pi)
    n=round(math.fsum(pi))
    if not 2<=n<=N or abs(math.fsum(pi)-n)>1e-10:
        raise SamplingUnknown("invalid design")
    if n==N:return tuple(range(N))
    suffix=_suffix_polynomials(pi)
    if suffix[0][1][n]<=0:raise SamplingUnknown("zero Sampford partition function")
    remaining=n
    accumulated_a=0.0
    chosen=[]
    draws=iter(uniforms)
    for i,p in enumerate(pi):
        if remaining==0:break
        if remaining==N-i:
            chosen.extend(range(i,N));break
        e,f=suffix[i+1]
        a=1-p
        include=p*((accumulated_a+a)*e[remaining-1]+f[remaining-1])
        exclude=a*(accumulated_a*e[remaining]+f[remaining])
        denom=include+exclude
        if not denom>0 or not math.isfinite(denom):
            raise SamplingUnknown("degenerate conditional draw")
        try:u=next(draws)
        except StopIteration as exc:raise SamplingUnknown("incomplete PRF draw stream") from exc
        if not 0<u<1:raise SamplingUnknown("injected uniform outside open interval")
        if u<include/denom:
            chosen.append(i)
            accumulated_a+=a
            remaining-=1
    if len(chosen)!=n:raise SamplingUnknown("wrong sample size")
    return tuple(chosen)
