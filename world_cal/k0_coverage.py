"""Public, source-first K0 support INDEX coverage; no K0/CAL execution.

This certifies the *generator index set*, not the completion of the
exponentially larger paired TRAIN/EVAL public-history policy search.
The distinction prevents a cardinality proof being mistaken for K0 PASS.
"""
import hashlib
import itertools
import json
from math import comb
from fractions import Fraction

from .abstract_support import (
    PATTERNS, PHASE_LENGTHS, iter_law_cells, verified_rows,
    MAX_SUPPORT_CELLS, AbstractSourceUnknown,
)
from .generator_contract import capacity_admissible

class CoverageUnknown(ValueError):
    pass

def _rows():
    rows = tuple(sorted(verified_rows(), key=lambda r: r[0]))
    if len(rows) != 384 or len({r[0] for r in rows}) != 384:
        raise CoverageUnknown("STOP_UNKNOWN: incomplete canonical law set")
    if len(PATTERNS) != 8 or len(set(PATTERNS)) != 8:
        raise CoverageUnknown("STOP_UNKNOWN: word-pattern vocabulary mismatch")
    if len(tuple(itertools.permutations(range(4)))) != 24:
        raise CoverageUnknown("STOP_UNKNOWN: role bijection count mismatch")
    return rows

def law_cell_count(row, phase):
    if phase not in PHASE_LENGTHS:
        raise CoverageUnknown("STOP_UNKNOWN: unknown phase")
    return 24 * len(PATTERNS) * sum(
        capacity_admissible(row, length) for length in PHASE_LENGTHS[phase])

def exact_cell_mass(row, phase):
    """Per-cell mass under law p and the registered hierarchical uniform grid."""
    valid_lengths=sum(capacity_admissible(row, n) for n in PHASE_LENGTHS[phase])
    if not valid_lengths:
        raise CoverageUnknown("STOP_UNKNOWN: no admissible lengths")
    return Fraction(row[8], row[9]) / (valid_lengths * 24 * len(PATTERNS))

def iter_law_pairs(rows=None):
    """Canonical unordered distinct-law pairs: bijection with i<j indices."""
    if rows is None:
        rows = _rows()
    else:
        rows = tuple(sorted(rows, key=lambda r: r[0]))
        if len({r[0] for r in rows}) != len(rows):
            raise CoverageUnknown("STOP_UNKNOWN: duplicate law")
    yield from itertools.combinations(rows, 2)

def source_index_certificate(*, verify_generator_yields=True):
    """Count actual source iterator emissions and assert arithmetic coverage.

    Proof: every law is a pinned row; every valid length is visited once;
    permutations(range(4)) are exactly all 4! role bijections; PATTERNS
    is an 8-element registered vocabulary. The only structural exclusion
    is capacity_admissible. Cartesian product loops are surjective on this
    finite INDEX domain, and their keys are injective on
    (law,phase,length,permutation_rank,pattern).
    """
    rows = _rows()
    counts = {}
    for phase,expected in MAX_SUPPORT_CELLS.items():
        arithmetic = sum(law_cell_count(row, phase) for row in rows)
        if arithmetic != expected:
            raise CoverageUnknown("STOP_UNKNOWN: source-grid arithmetic mismatch")
        if verify_generator_yields:
            produced = sum(1 for row in rows for _ in iter_law_cells(row, phase))
            if produced != arithmetic:
                raise CoverageUnknown("STOP_UNKNOWN: generator/index discrepancy")
        total_mass=sum((law_cell_count(row,phase)*exact_cell_mass(row,phase)
                        for row in rows), Fraction(0))
        if total_mass!=1:
            raise CoverageUnknown("STOP_UNKNOWN: probability mass missing")
        counts[phase] = arithmetic
    pair_hash = hashlib.sha256()
    total = 0
    for left,right in iter_law_pairs(rows):
        pair_hash.update((left[0] + "|" + right[0] + "\n").encode("ascii"))
        total += 1
    if total != comb(len(rows), 2) or total != 73536:
        raise CoverageUnknown("STOP_UNKNOWN: incomplete law-pair index")
    return {
        "status": "PUBLIC_INDEX_COVERAGE_ONLY_NOT_K0_PASS",
        "law_count": len(rows), "unordered_law_pairs": total,
        "pair_order_sha256": pair_hash.hexdigest(),
        "phase_index_cells": counts,
        "phase_total_probability_exact": {phase:"1/1" for phase in counts},
        "per_law_phase_formula": "24 * 8 * number_of_capacity_admissible_lengths",
        "pair_index_formula": "n*(n-1)//2",
        "all_training_paths_exhausted": False,
        "all_evaluation_paths_exhausted": False,
        "all_history_dp_exhausted": False,
        "K0b_status": "UNKNOWN",
        "K0c_status": "UNKNOWN",
    }

def path_index_cardinality(left, right, phase, trials, *, demos_per_law=3):
    """Exact symbolic support count for FIXED-length trial sequences.

    Three demo cells are ordered, distinct and excluded from the trial
    index set. A trial may recur (source only prohibits demo/trial overlap).
    Does NOT choose a demo, trial, CAL law, tag, sealed split or seed.
    """
    if phase not in PHASE_LENGTHS or type(trials) is not int or trials < 1:
        raise CoverageUnknown("STOP_UNKNOWN: trial length/phase not fixed")
    if demos_per_law != 3:
        raise CoverageUnknown("STOP_UNKNOWN: registered demo count changed")
    a,b = law_cell_count(left,phase),law_cell_count(right,phase)
    if a < 3 or b < 3:
        raise CoverageUnknown("STOP_UNKNOWN: insufficient support")
    falling = lambda x: x * (x-1) * (x-2)
    return falling(a) * falling(b) * ((a-3)*(b-3)) ** trials

def bounded_pair_cell_indices(left,right,phase,*,cap):
    """Exact Cartesian product prefix; reaching cap is UNKNOWN, not COMPLETE.

    Complete only if the caller consumes StopIteration after ALL cells.
    This iterator never constructs target, law allocation, demo or seed.
    """
    if type(cap) is not int or cap <= 0:
        raise CoverageUnknown("STOP_UNKNOWN: invalid cap")
    expected=law_cell_count(left,phase)*law_cell_count(right,phase)
    emitted=0
    for lc in iter_law_cells(left,phase):
        for rc in iter_law_cells(right,phase):
            if emitted >= cap:
                raise CoverageUnknown("STOP_UNKNOWN: support Cartesian cap reached")
            yield (lc["cell_digest"],rc["cell_digest"])
            emitted+=1
    if emitted != expected:
        raise CoverageUnknown("STOP_UNKNOWN: support Cartesian incomplete")

def status_when_not_exhausted(*, law_pairs_complete, trial_lengths_fixed,
                              demo_exclusion_verified, histories_complete):
    """Gate that cannot turn a mere row/grid counting proof into PASS."""
    if not all((law_pairs_complete,trial_lengths_fixed,
                demo_exclusion_verified,histories_complete)):
        return "UNKNOWN"
    return "READY_FOR_INDEPENDENT_K0B_RESULT_AUDIT"
