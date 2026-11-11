"""Immutable abstract source verification, never split/instance sampling."""
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

VERSION = "WORLD-GEN-SRC-1.0.0"
MANIFEST_SHA = "3b0e500890a0836cb2711422b54d55412e6d07654e1dabe5aeaeab18b8b85f3a"
DISTRIBUTION_SHA = "bdc841181fe370d940df95d12150e9216b110e065c89c4bfced031dc89339576"
FAMILIES = ("TRANSCRIBE", "REPEAT_COPY", "OBS_EDIT", "TWO_STAGE_JOIN")

class SourceMismatch(ValueError):
    pass

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def recompute_id(row):
    law, parent, family, template, predicate, signal, payload, k, numerator, denominator = row
    ast = f"COMPARE({'EQ' if predicate == 'COUNT_EQ' else 'LT'},COUNT_ROLE(S{signal}),COUNT_ROLE(S{payload}))"
    normal = [template, ast, "IF_TRUE_ELSE_FALSE", f"S{payload}", [signal, payload, k]]
    candidate = digest(("WORLD-LAW-NORMAL-FORM-v1\n" + _compact(normal)).encode("utf-8"))
    cluster = digest(("WORLD-PARENT-CLUSTER-v1\n" + _compact([family, template, signal, payload])).encode("utf-8"))
    return "sha256:" + candidate, "sha256:" + cluster

def capacity_admissible(row, length: int) -> bool:
    return not (row[3] in ("R_HEAD", "R_TAIL") and length + row[7] > 16)

def load_verified(manifest_path: str | Path, distribution_path: str | Path):
    mb = Path(manifest_path).read_bytes()
    db = Path(distribution_path).read_bytes()
    if digest(mb) != MANIFEST_SHA or digest(db) != DISTRIBUTION_SHA:
        raise SourceMismatch("raw source byte digest mismatch")
    manifest, dist = json.loads(mb), json.loads(db)
    if manifest["generator_version"] != VERSION or dist["generator_version"] != VERSION:
        raise SourceMismatch("generator version mismatch")
    rows = dist["rows"]
    if len(rows) != 384 or len({row[0] for row in rows}) != 384:
        raise SourceMismatch("law support mismatch")
    parents = set()
    family_counts = Counter()
    mass = {family: Fraction(0) for family in FAMILIES}
    for row in rows:
        if len(row) != 10 or row[0:2] != list(recompute_id(row)):
            raise SourceMismatch("noncanonical law/parent ID")
        if row[5] == row[6] or row[8] != 1 or row[9] not in (192, 576):
            raise SourceMismatch("illegal law weight/role")
        family = row[2]
        if family not in mass:
            raise SourceMismatch("unknown family")
        parents.add(row[1])
        family_counts[family] += 1
        mass[family] += Fraction(row[8], row[9])
    if len(parents) != 96 or dict(family_counts) != dict(dist["counts_by_family"]):
        raise SourceMismatch("parent counts mismatch")
    if any(mass[f] != Fraction(1, 4) for f in FAMILIES):
        raise SourceMismatch("law mass mismatch")
    if sum(not capacity_admissible(row, length) for row in rows for length in range(13, 17)) != 288:
        raise SourceMismatch("G2 capacity grid mismatch")
    if sum(capacity_admissible(row, length) for row in rows for length in range(4, 13)) != 3456:
        raise SourceMismatch("TRAIN/G1 capacity grid mismatch")
    split = manifest["parent_cluster_split"]
    if split["parent_cluster_allocation_digest"] is not None or split["H_laws_digest"] is not None:
        raise SourceMismatch("source definition unexpectedly materializes split")
    return manifest, dist

def abstract_quota_counts(manifest: dict) -> dict[str, int]:
    # Pure arithmetic on publicly registered parent quotas, no assignment.
    out = {"TRAIN": 0, "CAL": 0, "HOLDOUT": 0}
    for family, quotas in manifest["parent_cluster_split"]["quotas_in_parents"].items():
        size = manifest["parent_cluster_split"]["parent_size_by_family"][family]
        for phase, count in quotas.items():
            out[phase] += size * count
    return out
