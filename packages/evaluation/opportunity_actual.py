"""OPPORTUNITY-001: non-activated, pure audited-pair normalizer.

Only synthetic tuples are accepted in tests. This module neither executes any
search nor verifies the trustworthiness, chronology or custody of original
evidence. No historic DEV/FINAL path or live scoring entrypoint exists here.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import re
from typing import Mapping

SCHEMA = "opportunity-paired-evidence-v1"
POLICIES = ("B1", "B2", "B3")
ACTIONS = ("OFF", "ON")
TRIAL_KEYS = frozenset((
    "search", "audit_correct", "audit_invalid_solved", "meter", "selected_ast",
))
# Frozen canonical SearchResult.to_dict minus elapsed_ms; reject unknown keys
# rather than silently discarding potentially private raw evidence.
SEARCH_KEYS = frozenset((
    "task_id", "status", "solved", "program", "tested_candidates",
    "max_nodes", "max_candidates", "trace_sha256",
))
METER_KEYS = frozenset(("primitive_invocations", "by_op"))
CANONICAL_PRIMITIVES = frozenset(("trim", "lower", "upper"))
MAX_NODES = 4
MAX_CANDIDATES = 100


def _digest(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _sha256(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _task_id(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"t-[0-9a-f]{64}", value) is not None


def _exact(obj: object, keys: frozenset, context: str) -> dict:
    if type(obj) is not dict or set(obj) != keys:
        raise ValueError(f"{context}: malformed or private fields")
    return obj


def normalize_audited_trial(raw: tuple, *, arm: str) -> dict[str, object]:
    """Normalize a canonical _audited_trial tuple; do not assert audit authority."""
    if type(arm) is not str or arm not in ACTIONS:
        raise ValueError("Invalid action arm")
    if type(raw) is not tuple or len(raw) != 9:
        raise ValueError("Expected canonical independent audited tuple")
    (evidence, candidates, calls, correct, invalid, search_cpu, search_wall,
     audit_cpu, audit_wall) = raw
    if type(correct) is not bool or type(invalid) is not bool:
        raise ValueError("Audit flags must be bool")
    if invalid:
        raise ValueError("false_solved: independent audit failed; stop experiment")
    if any(type(x) is not int or x < 0 for x in (candidates, calls)):
        raise ValueError("Invalid canonical count")
    for x in (search_cpu, search_wall, audit_cpu, audit_wall):
        if type(x) not in (float, int) or not math.isfinite(x) or x < 0:
            raise ValueError("Invalid search/audit phase time")
    item = _exact(evidence, TRIAL_KEYS, arm)
    if type(item["audit_correct"]) is not bool or item["audit_correct"] != correct:
        raise ValueError("Independent audit label mismatch")
    if (type(item["audit_invalid_solved"]) is not bool
            or item["audit_invalid_solved"] != invalid):
        raise ValueError("False-solved flag mismatch")

    search = _exact(item["search"], SEARCH_KEYS, "search")
    if not _task_id(search["task_id"]):
        raise ValueError("Invalid canonical search task ID")
    if type(search["max_nodes"]) is not int or search["max_nodes"] != MAX_NODES:
        raise ValueError("Fixed expanded-AST budget mismatch")
    if (type(search["max_candidates"]) is not int
            or search["max_candidates"] != MAX_CANDIDATES):
        raise ValueError("Fixed candidate budget mismatch")
    if search["status"] not in ("solved", "not_found", "budget_exhausted"):
        raise ValueError("Invalid canonical search status")
    if (type(search["tested_candidates"]) is not int
            or search["tested_candidates"] != candidates
            or not 1 <= candidates <= MAX_CANDIDATES):
        raise ValueError("Candidate-count provenance mismatch")
    if not _sha256(search["trace_sha256"]):
        raise ValueError("Unsafe or missing search trace SHA256")
    if type(search["solved"]) is not bool:
        raise ValueError("Canonical search solved flag must be bool")
    if search["solved"] != (search["status"] == "solved"):
        raise ValueError("Canonical solved/status contradiction")
    if search["status"] == "budget_exhausted" and candidates != MAX_CANDIDATES:
        raise ValueError("Budget-exhausted count contradiction")

    meter = _exact(item["meter"], METER_KEYS, "meter")
    if (type(meter["primitive_invocations"]) is not int
            or meter["primitive_invocations"] != calls):
        raise ValueError("Canonical primitive-call meter mismatch")
    by_op = meter["by_op"]
    if type(by_op) is not dict or any(
            type(op) is not str or op not in CANONICAL_PRIMITIVES
            or type(count) is not int or count <= 0
            for op, count in by_op.items()):
        raise ValueError("Noncanonical primitive-call by_op")
    if sum(by_op.values()) != calls:
        raise ValueError("Canonical primitive-call by_op sum mismatch")

    program = search["program"]
    selected = item["selected_ast"]
    if search["status"] == "solved":
        if not correct or type(program) is not dict or type(selected) is not dict:
            raise ValueError("Unaudited or missing solved AST")
        if program != selected:
            raise ValueError("Canonical selected AST/program contradiction")
    elif correct or program is not None or selected is not None:
        raise ValueError("Unsolved outcome contradicts audit/program")

    return {
        "arm": arm,
        "task_id": search["task_id"],
        "max_nodes": MAX_NODES,
        "max_candidates": MAX_CANDIDATES,
        "search_status": search["status"],
        "audited_correct": correct,
        "primitive_calls": calls,
        "tested_candidates": candidates,
        "trace_sha256": search["trace_sha256"],
        "selected_ast_sha256": _digest(selected) if selected is not None else None,
        "search_cpu_ms": float(search_cpu),
        "search_wall_ms": float(search_wall),
        "audit_cpu_ms": float(audit_cpu),
        "audit_wall_ms": float(audit_wall),
    }


def classify_pair(off: Mapping, on: Mapping, choices: Mapping[str, str]) -> dict[str, object]:
    """Audit correctness first, primitive calls second; neither-success unknown."""
    if type(choices) is not dict or set(choices) != set(POLICIES):
        raise ValueError("Invalid policy choice set")
    if any(type(choices[a]) is not str or choices[a] not in ACTIONS for a in POLICIES):
        raise ValueError("Invalid pretrial choice action")
    if not isinstance(off, Mapping) or not isinstance(on, Mapping):
        raise ValueError("Invalid paired evidence")
    if off.get("arm") != "OFF" or on.get("arm") != "ON":
        raise ValueError("Wrong paired arm identity")
    if (not _task_id(off.get("task_id")) or off["task_id"] != on.get("task_id")
            or off.get("max_nodes") != MAX_NODES or on.get("max_nodes") != MAX_NODES
            or off.get("max_candidates") != MAX_CANDIDATES
            or on.get("max_candidates") != MAX_CANDIDATES):
        raise ValueError("Paired task identity or search budget mismatch")
    for row in (off, on):
        if type(row.get("audited_correct")) is not bool:
            raise ValueError("Missing independent audited correctness")
        if type(row.get("primitive_calls")) is not int or row["primitive_calls"] < 0:
            raise ValueError("Invalid paired calls")
    oc, nc = off["audited_correct"], on["audited_correct"]
    if oc and nc:
        if off["primitive_calls"] == on["primitive_calls"]:
            classification, best = "both_correct_tie", None
        elif off["primitive_calls"] < on["primitive_calls"]:
            classification, best = "both_correct_off_cheaper", "OFF"
        else:
            classification, best = "both_correct_on_cheaper", "ON"
    elif oc:
        classification, best = "off_only_correct", "OFF"
    elif nc:
        classification, best = "on_only_correct", "ON"
    else:
        classification, best = "neither_correct", None
    policy = {}
    for name in POLICIES:
        selected = choices[name]
        policy[name] = {
            "action": selected,
            "decision_error": None if best is None else selected != best,
            "missed_success": bool(nc and not oc and selected == "OFF"),
            "lost_success": bool(oc and not nc and selected == "ON"),
            "excess_calls": (
                max(0, (off if selected == "OFF" else on)["primitive_calls"] -
                    min(off["primitive_calls"], on["primitive_calls"]))
                if oc and nc else None),
        }
    return {
        "classification": classification,
        "unique_better_action": best,
        "policies": policy,
        "both_arms_audited": True,
        "best_of_two_correct": bool(oc or nc),
    }


def public_redacted_pair(task_id: str, off_raw: tuple, on_raw: tuple,
                         policy_actions: Mapping[str, str],
                         audit_commitment_sha256: str) -> dict[str, object]:
    """Only prevalidated public IDs and hashes; never private raw examples."""
    if not _task_id(task_id):
        raise ValueError("Invalid public task ID")
    if not _sha256(audit_commitment_sha256):
        raise ValueError("Missing private audit commitment")
    off = normalize_audited_trial(off_raw, arm="OFF")
    on = normalize_audited_trial(on_raw, arm="ON")
    if off["task_id"] != task_id or on["task_id"] != task_id:
        raise ValueError("Public record and paired search task IDs mismatch")
    classified = classify_pair(off, on, policy_actions)
    return {
        "schema_version": SCHEMA,
        "task_id": task_id,
        "audit_commitment_sha256": audit_commitment_sha256,
        "trials": {"OFF": off, "ON": on},
        **classified,
    }
