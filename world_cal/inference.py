"""Unnormalized design-based HT, SYG and parent-cluster bootstrap."""
import math
from collections import Counter

class InferenceUnknown(ValueError):pass

def ht(sample, q, pi, outcomes):
    return sum(q[i]/pi[i]*outcomes[i] for i in sample)

def syg(sample, q, pi, pij, outcomes):
    value=0.0
    for ix,i in enumerate(sample):
        for j in sample[ix+1:]:
            p=pij[i][j]
            if p<=0:raise InferenceUnknown("zero joint inclusion")
            term=q[i]*outcomes[i]/pi[i]-q[j]*outcomes[j]/pi[j]
            value+=(pi[i]*pi[j]-p)/p*term*term
    if value < -1e-10 or not math.isfinite(value):
        raise InferenceUnknown("invalid SYG")
    return max(0.0,value)

def parent_bootstrap_ht(sample,q,pi,values,parent_ids,drawn_parents):
    groups={}
    for i in sample:
        groups.setdefault(parent_ids[i],0.0)
        groups[parent_ids[i]]+=q[i]/pi[i]*values[i]
    if len(groups)<2 or len(drawn_parents)!=len(groups) or any(c not in groups for c in drawn_parents):
        raise InferenceUnknown("invalid cluster bootstrap")
    counts=Counter(drawn_parents)
    return sum(counts[c]*groups[c] for c in sorted(groups))

def bootstrap_vectors(sample,q,pi,outcomes_by_law,parent_ids,draws):
    """One draw of parent IDs applies to all seven outcomes/indices."""
    if not sample:raise InferenceUnknown("empty sample")
    dimensions=len(outcomes_by_law[sample[0]])
    if dimensions!=9 or any(len(outcomes_by_law[i])!=dimensions for i in sample):
        raise InferenceUnknown("expected seven contrasts plus G1,G2")
    pts=tuple(ht(sample,q,pi,{i:outcomes_by_law[i][j] for i in sample})
              for j in range(dimensions))
    repl=[]
    for draw in draws:
        repl.append(tuple(parent_bootstrap_ht(sample,q,pi,
              {i:outcomes_by_law[i][j] for i in sample},parent_ids,draw)
              for j in range(dimensions)))
    return pts,repl

def quantile(xs,prob):
    if not xs or not 0<=prob<=1 or any(not math.isfinite(x) for x in xs):
        raise InferenceUnknown("invalid quantile")
    ordered=sorted(xs)
    return ordered[min(len(ordered)-1, math.ceil(prob*len(ordered))-1)]

def studentized_max_t(points,replicates,alpha=0.0125):
    if len(points)!=7 or len(replicates)<2 or any(len(r)!=7 for r in replicates):
        raise InferenceUnknown("invalid dimensions")
    m=len(replicates)
    sd=[]
    for j in range(7):
        v=sum((r[j]-points[j])**2 for r in replicates)/(m-1)
        if not math.isfinite(v) or v<=0:raise InferenceUnknown("degenerate bootstrap variance")
        sd.append(math.sqrt(v))
    t=[max(abs((r[j]-points[j])/sd[j]) for j in range(7)) for r in replicates]
    critical=quantile(t,1-alpha)
    return tuple((points[j]-critical*sd[j],points[j]+critical*sd[j]) for j in range(7))

def one_sided_lower(point,replicates,index,alpha=0.00625):
    if len(replicates)<2:raise InferenceUnknown("insufficient replicates")
    changes=[r[index]-point for r in replicates]
    if max(changes)==min(changes):raise InferenceUnknown("degenerate bootstrap")
    return point-quantile(changes,1-alpha)

def ten_and_gates(deltas,main_intervals,g1,g2,g1_lower,g2_lower,contrast):
    if len(deltas)!=7 or len(main_intervals)!=7:
        raise InferenceUnknown("gate dimensions")
    parts=[d>=0.15 and interval[0]>0 for d,interval in zip(deltas,main_intervals)]
    parts.extend([g1>=0.90 and g1_lower>0.90,
                  g2>=0.80 and g2_lower>0.80,contrast>=0.10])
    return tuple(parts),all(parts)

def bootstrap_vectors_cached(sample,q,pi,outcomes_by_law,parent_ids,draws):
    """Semantics-preserving 999-bootstrap acceleration, bitwise order maintained.

    Cache exact per-parent HT sums once, rather than recalculating them 9
    times per bootstrap draw. Within each dimension, unit traversal and
    parent traversal are IDENTICAL to parent_bootstrap_ht/bootstrap_vectors.
    This changes neither the number of resamples nor their contents.
    """
    if not sample:raise InferenceUnknown("empty sample")
    dimensions=len(outcomes_by_law[sample[0]])
    if dimensions!=9 or any(len(outcomes_by_law[i])!=dimensions for i in sample):
        raise InferenceUnknown("expected seven contrasts plus G1,G2")
    # Same additions and multiplication order as original ht (dimension-wise).
    points=tuple(ht(sample,q,pi,{i:outcomes_by_law[i][j] for i in sample})
                 for j in range(dimensions))
    parents=tuple(sorted({parent_ids[i] for i in sample}))
    if len(parents)<2:raise InferenceUnknown("invalid cluster bootstrap")
    groups={}
    # Maintain the same per-dimension, per-sample order of floating operations.
    for j in range(dimensions):
        for i in sample:
            c=parent_ids[i]
            if c not in groups:groups[c]=[0.0]*dimensions
            groups[c][j]+=q[i]/pi[i]*outcomes_by_law[i][j]
    replicates=[]
    for draw in draws:
        if len(draw)!=len(parents) or any(c not in groups for c in draw):
            raise InferenceUnknown("invalid cluster bootstrap")
        counts=Counter(draw)
        replicates.append(tuple(sum(counts[c]*groups[c][j] for c in sorted(groups))
                                for j in range(dimensions)))
    return points,replicates


def bootstrap_vectors_array(sample,q,pi,outcomes_by_law,parent_ids,draws):
    """Same cluster sums/draws; native final sums (roundoff audited <=1e-10).

    No BLAS reduction or thread pool; bounded native sequential reduction.
    Keep the scalar implementation above as an independent numerical reference.
    """
    try:
        from ._prf_batch import weighted_sums
    except ImportError:
        return bootstrap_vectors_cached(sample,q,pi,outcomes_by_law,parent_ids,draws)
    if not sample:raise InferenceUnknown("empty sample")
    if any(len(outcomes_by_law[i])!=9 for i in sample):
        raise InferenceUnknown("expected seven contrasts plus G1,G2")
    points=tuple(ht(sample,q,pi,{i:outcomes_by_law[i][j] for i in sample})
                 for j in range(9))
    parents=tuple(sorted({parent_ids[i] for i in sample}))
    if len(parents)<2:raise InferenceUnknown("invalid cluster bootstrap")
    groups={c:[0.0]*9 for c in parents}
    for j in range(9):
        for i in sample:
            groups[parent_ids[i]][j]+=q[i]/pi[i]*outcomes_by_law[i][j]
    counts=[]
    for draw in draws:
        if len(draw)!=len(parents) or any(c not in groups for c in draw):
            raise InferenceUnknown("invalid cluster bootstrap")
        count=Counter(draw)
        counts.append([count[c] for c in parents])
    if not counts:return points,[]
    try:
        return points,weighted_sums(counts,list(groups.values()))
    except ValueError as exc:
        raise InferenceUnknown("invalid bootstrap arrays") from exc
