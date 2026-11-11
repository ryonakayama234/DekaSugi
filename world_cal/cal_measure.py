"""CAL algorithms, callable only after separate CAL authorization by a role boundary.

No measurement runner or seed accessor is defined here. Synthetic-only utilities
may be used in the implementation GO, never with real CAL law instances.
"""
from .k0_oracle import nearest_rank90

class CALNotAuthorized(PermissionError):pass

def l90_from_complete_lengths(lengths, *, synthetic_fixture=False):
    if not synthetic_fixture:
        raise CALNotAuthorized("L90 CAL measurement requires separate CAL GO")
    return nearest_rank90(lengths)

def tag_features(tag):
    if not isinstance(tag,str) or not tag:
        raise ValueError("invalid synthetic tag")
    raw=tag.encode("utf-8")
    return (float(len(raw)),raw[0]/255.0,raw[-1]/255.0,(sum(raw)%256)/255.0)

def parent_folds(parent_ids, folds=5):
    if folds!=5:raise ValueError("only registered 5 folds")
    roots=sorted(set(parent_ids))
    return {root:i%5 for i,root in enumerate(roots)}

def id_only_diagnostic(*args,**kwargs):
    raise CALNotAuthorized("ID-only classifier execution is CAL; not included in implementation GO")
