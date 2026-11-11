"""Deterministic ID-only four-class CAL diagnostic (no tag or seed generation).

Uses the registered four UTF-8 features, multinomial L2 C=1 logistic
regression, zero initialization, full-batch Newton method, and
lexicographic parent-cluster 5-fold cross-validation. Dependencies pinned.
This module contains no CAL runner or access to private truth.
"""
import math

class IDOnlyUnknown(ValueError):
    pass

CLASSES=4
FOLDS=5
PERMUTATIONS=999
MAX_ITER=1000
TOL=1e-8
C=1.0


def features(tag):
    if not isinstance(tag,str) or not tag:
        raise IDOnlyUnknown("STOP_UNKNOWN: invalid tag")
    raw=tag.encode("utf-8")
    return (float(len(raw)),raw[0]/255.0,raw[-1]/255.0,(sum(raw)%256)/255.0)


def parent_fold_ids(parents):
    roots=sorted(set(parents))
    if len(roots)<FOLDS:raise IDOnlyUnknown("STOP_UNKNOWN: fewer than five parents")
    mapping={p:i%FOLDS for i,p in enumerate(roots)}
    return tuple(mapping[p] for p in parents)


def _fit(x, labels):
    import numpy as np
    k=CLASSES
    m,d=x.shape
    # Fix the fourth class as baseline to eliminate the softmax gauge.
    beta=np.zeros((k-1,d),dtype=np.float64)
    truth=np.zeros((m,k-1),dtype=np.float64)
    truth[np.arange(m), np.minimum(labels,k-2)]= (labels<k-1).astype(float)
    penalty=np.ones((k-1,d),dtype=np.float64)
    penalty[:,0]=0.0  # intercept is not penalized
    def evaluate(w):
        scores=np.column_stack((x@w.T,np.zeros(m)))
        scores-=scores.max(axis=1,keepdims=True)
        ex=np.exp(scores)
        probs=ex/ex.sum(axis=1,keepdims=True)
        if np.any(probs<=0):raise IDOnlyUnknown("STOP_UNKNOWN: softmax underflow")
        objective=-np.log(probs[np.arange(m), labels]).sum()+0.5*(penalty*w*w).sum()/C
        return float(objective),probs
    objective,probs=evaluate(beta)
    for iteration in range(MAX_ITER):
        grad=((probs[:,:k-1]-truth).T@x)+penalty*beta/C
        if np.max(np.abs(grad)) <= TOL:return beta
        hess=np.zeros(((k-1)*d,(k-1)*d),dtype=np.float64)
        for a in range(k-1):
            for b in range(k-1):
                weight=probs[:,a]*((1.0 if a==b else 0.0)-probs[:,b])
                hess[a*d:(a+1)*d,b*d:(b+1)*d]=x.T@(weight[:,None]*x)
            hess[a*d:(a+1)*d,a*d:(a+1)*d]+=np.diag(penalty[a]/C)
        try: direction=np.linalg.solve(hess,grad.ravel()).reshape(k-1,d)
        except np.linalg.LinAlgError as exc:raise IDOnlyUnknown("STOP_UNKNOWN: singular Hessian") from exc
        # The registered tolerance applies to the likelihood objective. Near
        # optimum binary64 loss can be flat while the raw gradient remains
        # slightly above 1e-8 on highly correlated tag features.
        predicted_improvement=0.5*float(np.sum(grad*direction))
        if not math.isfinite(predicted_improvement) or predicted_improvement<0:
            raise IDOnlyUnknown("STOP_UNKNOWN: invalid Newton decrement")
        if predicted_improvement <= TOL:
            return beta
        step=1.0
        for _ in range(50):
            candidate=beta-step*direction
            new_obj,new_probs=evaluate(candidate)
            if math.isfinite(new_obj) and new_obj<objective:
                change=objective-new_obj
                beta,objective,probs=candidate,new_obj,new_probs
                if change <= TOL: return beta
                break
            step*=0.5
        else:
            # A tiny Newton step may not reduce rounded binary64 objective;
            # only the pre-registered gradient tolerance permits convergence.
            if predicted_improvement <= TOL:
                return beta
            raise IDOnlyUnknown("STOP_UNKNOWN: optimizer stalled")
    raise IDOnlyUnknown("STOP_UNKNOWN: logistic regression max iterations exceeded")


def _predict(x,beta):
    import numpy as np
    scores=np.column_stack((x@beta.T,np.zeros(len(x))))
    scores-=scores.max(axis=1,keepdims=True)
    ex=np.exp(scores)
    return ex/ex.sum(axis=1,keepdims=True)


def _auc(scores, positives):
    """Exact trapezoidal/Mann-Whitney AUC with half credit for ties."""
    n1=sum(positives); n0=len(positives)-n1
    if not n1 or not n0:raise IDOnlyUnknown("STOP_UNKNOWN: AUC undefined")
    positive=[s for s,y in zip(scores,positives) if y]
    negative=[s for s,y in zip(scores,positives) if not y]
    return math.fsum((1 if a>b else 0.5 if a==b else 0)
                     for a in positive for b in negative)/(n1*n0)


def cross_validated_macro_auc(tags, labels, parents):
    import numpy as np
    if not(len(tags)==len(labels)==len(parents)) or not tags:
        raise IDOnlyUnknown("STOP_UNKNOWN: incomplete CAL vectors")
    if set(labels)!=set(range(CLASSES)):
        raise IDOnlyUnknown("STOP_UNKNOWN: four families required")
    folds=np.asarray(parent_fold_ids(parents))
    x=np.array([[1.0,*features(tag)] for tag in tags],dtype=np.float64)
    y=np.asarray(labels,dtype=np.int64)
    proba=np.empty((len(labels),CLASSES),dtype=np.float64)
    for fold in range(FOLDS):
        train=(folds!=fold)
        test=~train
        if not np.any(test) or set(y[train])!=set(range(CLASSES)):
            raise IDOnlyUnknown("STOP_UNKNOWN: class missing in training fold")
        proba[test]=_predict(x[test],_fit(x[train],y[train]))
    aucs=tuple(_auc(proba[:,c],y==c) for c in range(CLASSES))
    return math.fsum(aucs)/CLASSES


def id_only_permutation_test(tags, labels, parents, permuted_labels):
    """Exactly 999 injected label permutations; no RNG/seed inside this module.

    Each CAL replicate must reissue tags upstream in its registered PRF domain.
    The training/test labels are replaced together for each permutation.
    """
    if len(permuted_labels)!=PERMUTATIONS:
        raise IDOnlyUnknown("STOP_UNKNOWN: need exactly 999 registered permutations")
    observed=cross_validated_macro_auc(tags,labels,parents)
    null=[]
    for perm in permuted_labels:
        if sorted(perm)!=sorted(labels):
            raise IDOnlyUnknown("STOP_UNKNOWN: not a label permutation")
        null.append(cross_validated_macro_auc(tags,perm,parents))
    sorted_null=sorted(null)
    cutoff=sorted_null[math.ceil(.95*PERMUTATIONS)-1]
    return {"observed_macro_auc":observed,"null_p95":cutoff,
            "id_signal_above_null":observed>cutoff,
            "null_repetitions":PERMUTATIONS}
