"""OPPORTUNITY-001 PR2: synthetic-fixture-only actionability reducer.

This module deliberately does not import generators, learners, evaluators,
policy snapshots, metrology real adapters or experiment archives.
It cannot attest independent audits; only an independently verified future
adapter may produce real-evidence input, under a different schema/version.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Mapping, Sequence

SCHEMA = "opportunity-fixture-v1"
PHASE = "SYNTHETIC"
ACTIONS = frozenset(("OFF", "ON"))
LOCK_FIELDS = frozenset((
    "dataset_sha256", "skill_sha256", "policy_sha256",
    "primitive_sha256", "source_commit", "meter_version", "budget_id",
))
ROW_FIELDS = frozenset((
    "schema_version", "phase", "task_id", "source_lock",
    "policy_choice", "policy_decision_before_trials", "trials",
))
TRIAL_FIELDS = frozenset((
    "audit_status", "audited_correct", "search_status",
    "primitive_calls", "tested_candidates", "false_solved", "budget_id",
))
SHA256_FIELDS = ("dataset_sha256", "skill_sha256",
                 "policy_sha256", "primitive_sha256")
SEARCH_STATUSES = frozenset(("solved", "not_found", "budget_exhausted"))
CLASSIFICATIONS = frozenset((
    "both_correct_on_cheaper", "both_correct_off_cheaper",
    "both_correct_tie", "on_only_correct", "off_only_correct",
    "neither_correct", "not_observed", "non_comparable",
))


def _exact_keys(value: object, required: frozenset[str], name: str) -> dict:
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError(f"{name}: wrong shape or forbidden private field")
    return value


def _source_lock(value: object) -> dict:
    lock = _exact_keys(value, LOCK_FIELDS, "source_lock")
    if any(type(lock[k]) is not str or not re.fullmatch("[0-9a-f]{64}", lock[k])
           for k in SHA256_FIELDS):
        raise ValueError("source_lock: invalid sha256")
    if (type(lock["source_commit"]) is not str or
            not re.fullmatch("[0-9a-f]{40}", lock["source_commit"])):
        raise ValueError("source_lock: invalid source commit")
    if lock["meter_version"] != "runtime-canonical-v1":
        raise ValueError("source_lock: unknown meter version")
    if type(lock["budget_id"]) is not str or not 1 <= len(lock["budget_id"]) <= 80:
        raise ValueError("source_lock: invalid budget id")
    return lock


def _trial(value: object, arm: str) -> dict:
    item = _exact_keys(value, TRIAL_FIELDS, arm)
    if item["audit_status"] not in ("verified", "missing"):
        raise ValueError(f"{arm}: invalid audit status")
    if item["budget_id"] is None or type(item["budget_id"]) is not str or not item["budget_id"]:
        raise ValueError(f"{arm}: invalid budget id")
    if type(item["false_solved"]) is not bool:
        raise ValueError(f"{arm}: false_solved must be bool")
    if item["false_solved"]:
        # Keep the error visible to callers. Never silently infer a valid label.
        raise ValueError(f"{arm}: false_solved safety violation")
    if item["audit_status"] == "missing":
        if any(item[k] is not None for k in (
                "audited_correct", "search_status",
                "primitive_calls", "tested_candidates")):
            raise ValueError(f"{arm}: mixed missing and observed fields")
        return item
    if type(item["audited_correct"]) is not bool:
        raise ValueError(f"{arm}: correctness must be bool")
    if item["search_status"] not in SEARCH_STATUSES:
        raise ValueError(f"{arm}: unknown search status")
    for k in ("primitive_calls", "tested_candidates"):
        if type(item[k]) is not int or item[k] < 0:
            raise ValueError(f"{arm}: invalid {k}")
    if item["audited_correct"] and item["search_status"] != "solved":
        raise ValueError(f"{arm}: correct but unsolved")
    if item["search_status"] == "solved" and not item["audited_correct"]:
        raise ValueError(f"{arm}: unaudited false solution")
    return item


@dataclass(frozen=True, slots=True)
class Result:
    """In-memory classification only: do not serialize task-level trial rows."""

    classification: str
    best_action: str | None
    choice: str
    excess_calls: int | None
    missed_success: bool
    lost_success: bool
    comparison_valid: bool

    @property
    def unique_best(self) -> bool:
        return self.best_action is not None and self.classification != "both_correct_tie"


def classify_fixture(row: Mapping[str, object],
                     expected_lock: Mapping[str, object]) -> Result:
    """Classify one synthetic fixture under an externally specified identity.

    Calls never convert accuracy failures into cost. Unknown != zero.
    Invalid schemas/hashes/private fields raise ValueError (fail-closed).
    A trial-specific legal budget mismatch is non_comparable.
    """
    r = _exact_keys(row, ROW_FIELDS, "row")
    locked = _source_lock(r["source_lock"])
    if locked != _source_lock(expected_lock):
        raise ValueError("source_lock does not match externally pinned identity")
    if r["schema_version"] != SCHEMA or r["phase"] != PHASE:
        raise ValueError("real experiment data is forbidden in fixture reducer")
    if (type(r["task_id"]) is not str or
            not re.fullmatch(r"fx-[A-Za-z0-9_-]{1,80}", r["task_id"])):
        raise ValueError("not a synthetic task id")
    if r["policy_choice"] not in ACTIONS or type(r["policy_choice"]) is not str:
        raise ValueError("invalid policy choice")
    if r["policy_decision_before_trials"] is not True:
        raise ValueError("policy decision was not recorded before trial")
    arms = _exact_keys(r["trials"], ACTIONS, "trials")
    off, on = _trial(arms["OFF"], "OFF"), _trial(arms["ON"], "ON")
    choice = r["policy_choice"]
    if off["audit_status"] == "missing" or on["audit_status"] == "missing":
        return Result("not_observed", None, choice, None, False, False, False)
    if any(t["budget_id"] != locked["budget_id"] for t in (off, on)):
        return Result("non_comparable", None, choice, None, False, False, False)

    oc, nc = off["audited_correct"], on["audited_correct"]
    if oc and nc:
        if on["primitive_calls"] < off["primitive_calls"]:
            klass, best = "both_correct_on_cheaper", "ON"
        elif off["primitive_calls"] < on["primitive_calls"]:
            klass, best = "both_correct_off_cheaper", "OFF"
        else:
            klass, best = "both_correct_tie", "OFF"  # deterministic tie
        excess = (max(0, arms[choice]["primitive_calls"] -
                      min(off["primitive_calls"], on["primitive_calls"])))
        return Result(klass, best, choice, excess, False, False, True)
    if nc:
        return Result("on_only_correct", "ON", choice, None,
                      choice == "OFF", False, True)
    if oc:
        return Result("off_only_correct", "OFF", choice, None,
                      False, choice == "ON", True)
    return Result("neither_correct", None, choice, None, False, False, True)


def summarize_fixtures(rows: Sequence[Mapping[str, object]],
                       expected_lock: Mapping[str, object]) -> dict[str, object]:
    """Aggregate only; never return task IDs, per-task outcomes or private bytes."""
    _source_lock(expected_lock)
    counts = {status: 0 for status in sorted(CLASSIFICATIONS)}
    seen: set[str] = set()
    excess = missed = lost = unique = errors = both = 0
    for row in rows:
        result = classify_fixture(row, expected_lock)
        task_id = row["task_id"]
        if task_id in seen:
            raise ValueError("duplicate task id")
        seen.add(task_id)
        counts[result.classification] += 1
        if not result.comparison_valid:
            continue
        if result.excess_calls is not None:
            both += 1
            excess += result.excess_calls
        missed += int(result.missed_success)
        lost += int(result.lost_success)
        if result.unique_best:
            unique += 1
            errors += int(result.best_action != result.choice)
    valid = sum(counts[x] for x in counts if x not in ("not_observed", "non_comparable"))
    sensitivity = (counts["both_correct_on_cheaper"] +
                   counts["both_correct_off_cheaper"] +
                   counts["on_only_correct"] + counts["off_only_correct"])
    best_two_solved = valid - counts["neither_correct"]
    canonical = json.dumps(rows, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), allow_nan=False)
    return {
        "schema_version": "opportunity-fixture-summary-v1",
        "evidence_kind": "synthetic_calibration_only",
        "status": "calibration_observed_not_scientific_result",
        "input_sha256": sha256(canonical.encode("utf-8")).hexdigest(),
        "total_count": len(rows),
        "paired_valid_count": valid,
        "not_observed_count": counts["not_observed"],
        "non_comparable_count": counts["non_comparable"],
        "classification_counts": counts,
        "choice_sensitivity_numerator": sensitivity,
        "choice_sensitivity_denominator": valid,
        "unique_better_action_count": unique,
        "policy_decision_error_count": errors,
        "policy_decision_error_denominator": unique,
        "policy_missed_success_count": missed,
        "policy_lost_success_count": lost,
        "both_correct_cost_denominator": both,
        "policy_excess_calls_sum": excess,
        "best_of_two_success_count": best_two_solved,
        "best_of_two_success_denominator": valid,
        "uncertainty": "not_estimated_for_synthetic_fixtures",
    }
