"""Unscored EXP-COEV-001 Gate-F0 design-only synthetic preview.

Never use this public fixture/salt as the registered private class partition.
No scorer, Oracle, hidden labels or protected source is imported or executed.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from math import log, sqrt
from packages.concept_world import SemanticCatalog, _trusted_catalog, build_catalog, digest

SPLIT_SCHEMA = "coev-f0-public-feasibility-preview/1"
PREVIEW_SALT = "SYNTHETIC-ONLY-F0-PREVIEW-20261031"

@dataclass(frozen=True, slots=True)
class PoolPreview:
    schema: str
    world_digest: str
    train_class_ids: tuple[int, ...]
    dev_class_ids: tuple[int, ...]
    final_class_ids: tuple[int, ...]
    commitment: str

def _n_split(n: int) -> tuple[int, int, int]:
    train=(n*40+50)//100
    dev=(n*20+50)//100
    return train,dev,n-train-dev

def synthetic_pool_preview(catalog: SemanticCatalog | None = None,
                           *, salt: str = PREVIEW_SALT) -> PoolPreview:
    """Deterministic PUBLIC, THROWAWAY class split for structural checking."""
    if type(salt) is not str or salt != PREVIEW_SALT:
        raise ValueError("Only fixed public synthetic preview salt is allowed")
    c=_trusted_catalog(build_catalog() if catalog is None else catalog)
    groups=(tuple(i for i,p in enumerate(c.representatives) if p.predicate_id is None),
            tuple(i for i,p in enumerate(c.representatives) if p.predicate_id is not None))
    train: list[int]=[]
    dev: list[int]=[]
    final: list[int]=[]
    for ids in groups:
        ranked=sorted(ids,key=lambda i:(sha256((salt+":"+c.world_digest+":"+str(i)).encode()).hexdigest(),i))
        a,b,_=_n_split(len(ids))
        train.extend(ranked[:a]);dev.extend(ranked[a:a+b]);final.extend(ranked[a+b:])
    a,b,z=tuple(sorted(train)),tuple(sorted(dev)),tuple(sorted(final))
    if len(set(a+b+z)) != len(c.representatives) or set(a)&set(b) or set(a)&set(z) or set(b)&set(z):
        raise AssertionError("Class partition collision")
    payload={"schema":SPLIT_SCHEMA,"world":c.world_digest,"train":a,"dev":b,"final":z}
    return PoolPreview(SPLIT_SCHEMA,c.world_digest,a,b,z,digest(payload))

def _validated_preview(preview: PoolPreview, catalog: SemanticCatalog) -> PoolPreview:
    """Validate exact builtins; return canonical, NEVER caller-owned containers."""
    if (type(preview) is not PoolPreview or type(preview.schema) is not str or
            type(preview.world_digest) is not str or type(preview.commitment) is not str):
        raise ValueError("Untrusted preview metadata")
    for ids in (preview.train_class_ids, preview.dev_class_ids, preview.final_class_ids):
        if (type(ids) is not tuple or
                any(type(i) is not int or not 0 <= i < len(catalog.representatives) for i in ids)):
            raise ValueError("Untrusted class ID container")
    canonical=synthetic_pool_preview(catalog)
    if (preview.schema != canonical.schema or
            preview.world_digest != canonical.world_digest or
            preview.commitment != canonical.commitment or
            preview.train_class_ids != canonical.train_class_ids or
            preview.dev_class_ids != canonical.dev_class_ids or
            preview.final_class_ids != canonical.final_class_ids):
        raise ValueError("Forged, stale, or noncanonical synthetic pool preview")
    return canonical

def validate_preview(preview: PoolPreview, catalog: SemanticCatalog | None=None) -> None:
    c=_trusted_catalog(build_catalog() if catalog is None else catalog)
    _validated_preview(preview,c)

def preflight_metrics(preview: PoolPreview, catalog: SemanticCatalog | None=None) -> dict[str, object]:
    c=_trusted_catalog(build_catalog() if catalog is None else catalog)
    preview=_validated_preview(preview,c)
    counts={"TRAIN":len(preview.train_class_ids),"DEV":len(preview.dev_class_ids),
            "FINAL":len(preview.final_class_ids)}
    stratify={name:{"plain":sum(c.representatives[i].predicate_id is None for i in xs),
                    "conditional":sum(c.representatives[i].predicate_id is not None for i in xs)}
              for name,xs in (("TRAIN",preview.train_class_ids),("DEV",preview.dev_class_ids),
                              ("FINAL",preview.final_class_ids))}
    N=2048
    K=counts["FINAL"]
    expected_unique=K*(1-(1-1/K)**N)
    # Paired per-task D in [-1,1] is the unit, NEVER 64 correlated audit inputs.
    radius=sqrt(2*log(40)/N)
    return {"schema":SPLIT_SCHEMA,"status":"STRUCTURAL_PREVIEW_NOT_FROZEN",
            "population_classes":len(c.representatives),"class_counts":counts,
            "family_counts":stratify,"commitment":preview.commitment,
            "proposed_final_task_draws":N,
            "expected_unique_final_classes_if_uniform_iid":round(expected_unique,3),
            "expected_repeated_class_draws_if_uniform_iid":round(N-expected_unique,3),
            "paired_hoeffding_95_radius":round(radius,6),
            "formal_train_or_final_authorized":False,
            "claims":"No target outputs, holdout labels, trained skill effect or official score observed"}
