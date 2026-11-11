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

def id_only_diagnostic(tags,labels,parent_ids,permuted_labels,*,
                       synthetic_fixture=False,authorization=None):
    """Complete 999-permutation ID-only diagnostic, execution guarded.

    Tag reissue and registered permutation draws are supplied by the separately
    authorized CAL role. No such real tags/seed exist during implementation GO.
    """
    from .power_engine import CALAuthorization
    from .id_only import id_only_permutation_test
    if not synthetic_fixture and not (isinstance(authorization,CALAuthorization)
            and authorization.role=="CAL_ORACLE" and authorization.approved):
        raise CALNotAuthorized("STOP_UNKNOWN: ID-only CAL role not authorized")
    return id_only_permutation_test(tags,labels,parent_ids,permuted_labels)
