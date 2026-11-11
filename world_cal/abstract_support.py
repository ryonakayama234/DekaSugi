"""Pure and lazy generator abstract support for future authorized K0.

Only public source byte-pinned 384-law distribution and exact finite word/
vocabulary grids. Never assigns parents to TRAIN/CAL/holdout, creates an
evaluation seed, or materializes sealed instances. This is an ABSTRACT
source interpreter, not a CAL/K0 executor.
"""
import hashlib
import itertools
import math
from pathlib import Path

from .generator_contract import load_verified, capacity_admissible

PATTERNS=("UNIFORM_S0","UNIFORM_S1","ALTERNATE_01","HALF_BLOCKS_01",
          "CYCLE_0123","CYCLE_1230","LEADING_S2","TRAILING_S3")
ROLE_LABELS=("S0","S1","S2","S3")
PHASE_LENGTHS={"TRAIN":tuple(range(4,13)),
               "CAL":tuple(range(4,13)),
               "G1":tuple(range(4,13)),
               "G2":tuple(range(13,17))}
MAX_SUPPORT_CELLS={"TRAIN":663552,"CAL":663552,
                   "G1":663552,"G2":239616}


class AbstractSourceUnknown(ValueError):
    pass


def verified_rows(base=None):
    if base is None:
        base=Path(__file__).resolve().parents[1]/"docs"/"research"
    manifest,dist=load_verified(
        base/"WORLD-CAL-GENERATOR-MANIFEST-20261111-01.json",
        base/"WORLD-CAL-GENERATOR-DISTRIBUTION-20261111-01.json")
    return tuple(dist["rows"])


def word_roles(pattern,length):
    if pattern not in PATTERNS or not isinstance(length,int) or not 4<=length<=16:
        raise AbstractSourceUnknown("STOP_UNKNOWN: unsupported word cell")
    if pattern=="UNIFORM_S0":return (0,)*length
    if pattern=="UNIFORM_S1":return (1,)*length
    if pattern=="ALTERNATE_01":return tuple(i%2 for i in range(length))
    if pattern=="HALF_BLOCKS_01":
        return tuple(0 if i<length//2 else 1 for i in range(length))
    if pattern=="CYCLE_0123":return tuple(i%4 for i in range(length))
    if pattern=="CYCLE_1230":return tuple((i+1)%4 for i in range(length))
    if pattern=="LEADING_S2":return (2,)+(0,)*(length-1)
    if pattern=="TRAILING_S3":return (1,)*(length-1)+(3,)
    raise AbstractSourceUnknown("unreachable pattern")


def target_roles(row,word):
    """Interpret the exact private template truth on ABSTRACT role indices.

    This is only for the authorized CAL_ORACLE future abstract support; the
    returned output is never exposed to LEARNER_ARMS, and is not a holdout.
    """
    _,_,_,template,predicate,signal,payload,k,_,_=row
    if template not in ("T_HEAD","T_TAIL","R_HEAD","R_TAIL",
                        "O_HEAD","O_TAIL","C_PREFIX","C_SUFFIX"):
        raise AbstractSourceUnknown("STOP_UNKNOWN: unknown template")
    if predicate not in ("COUNT_EQ","COUNT_LT"):
        raise AbstractSourceUnknown("STOP_UNKNOWN: unknown predicate")
    x=tuple(word);L=len(x)
    a=x.count(signal);b=x.count(payload)
    pred=(a==b) if predicate=="COUNT_EQ" else (a<b)
    if template=="T_HEAD":target=(x[-1] if pred else payload,)+x[1:]
    elif template=="T_TAIL":target=x[:-1]+(x[0] if pred else payload,)
    elif template=="R_HEAD":target=x+(x[0] if pred else payload,)*k
    elif template=="R_TAIL":target=x+(x[-1] if pred else payload,)*k
    elif template=="O_HEAD":target=(payload if pred else signal,)+x[1:]
    elif template=="O_TAIL":target=x[:-1]+(payload if pred else signal,)
    elif template=="C_PREFIX":target=x[k:]+x[:k] if pred else x
    else:target=x[-k:]+x[:-k] if pred else x
    if len(target)>16:
        raise AbstractSourceUnknown("STOP_UNKNOWN: capacity invariant")
    return target


def iter_law_cells(row,phase,*,include_target=False):
    """Yield *every* canonical abstract cell of ONE law, no random draws.

    The target is private oracle metadata: callers are responsible for OS
    role enforcement; no learner read path is provided here.
    """
    if phase not in PHASE_LENGTHS:
        raise AbstractSourceUnknown("STOP_UNKNOWN: invalid phase")
    ranks=tuple(itertools.permutations(range(4)))
    if len(ranks)!=24:raise AbstractSourceUnknown("bad symbolic role grid")
    for length in PHASE_LENGTHS[phase]:
        if not capacity_admissible(row,length):continue
        for rank,perm in enumerate(ranks):
            for pattern in PATTERNS:
                word=word_roles(pattern,length)
                init=tuple(perm[i] for i in word)
                target=tuple(perm[i] for i in target_roles(row,word))
                digest=hashlib.sha256(
                    repr((row[0],phase,length,rank,pattern)).encode("ascii")
                ).hexdigest()
                yield {"cell_digest":"sha256:"+digest,
                       "length":length,"permutation_rank":rank,
                       "pattern":pattern,"initial":init,
                       **({"abstract_target":target} if include_target else {})}


def source_grid_counts(rows=None):
    """Pure arithmetic, no target/instance materialization."""
    rows=verified_rows() if rows is None else rows
    if len(rows)!=384:raise AbstractSourceUnknown("STOP_UNKNOWN: law count")
    result={}
    for phase in PHASE_LENGTHS:
        count=sum(sum(capacity_admissible(row,L) for L in PHASE_LENGTHS[phase])
                  for row in rows)*24*len(PATTERNS)
        if count!=MAX_SUPPORT_CELLS[phase]:
            raise AbstractSourceUnknown("STOP_UNKNOWN: grid cardinality mismatch")
        result[phase]=count
    return result
