"""OPPORTUNITY-001: real-evidence normalizer, **NOT** an activated scorer.

Consumes canonical independent OFF/ON _audited_trial return tuples only. Has
no CLI, generator import, policy inference, holdout access or network/storage.
Original private audits must be retained by a separate reviewed access-controlled
sink BEFORE a one-shot runner can be authorized. The source-lock fixture reducer
intentionally rejects these real-evidence records.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from typing import Mapping

SCHEMA = "opportunity-paired-evidence-v1"
POLICIES = ("B1", "B2", "B3")
ACTIONS = ("OFF", "ON")
TRIAL_KEYS = frozenset((
    "search", "audit_correct", "audit_invalid_solved", "meter", "selected_ast",
))


def _digest(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def _exact(obj: object, keys: frozenset, context: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != keys:
        raise ValueError(f"{context}: malformed or private fields")
    return obj


def normalize_audited_trial(raw: tuple, *, arm: str) -> dict[str, object]:
    """Validate a canonical _audited_trial result; do not fake audit authority."""
    if arm not in ACTIONS or type(arm) is not str:
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
    if type(item["audit_invalid_solved"]) is not bool or item["audit_invalid_solved"] != invalid:
        raise ValueError("False-solved flag mismatch")
    search = item["search"]
    if not isinstance(search, dict) or search.get("status") not in (
            "solved", "not_found", "budget_exhausted"):
        raise ValueError("Invalid canonical search result")
    if (type(search.get("tested_candidates")) is not int
            or search["tested_candidates"] != candidates):
        raise ValueError("Candidate-count provenance mismatch")
    meter = item["meter"]
    if (not isinstance(meter, dict)
            or type(meter.get("primitive_invocations")) is not int
            or meter["primitive_invocations"] != calls):
        raise ValueError("Canonical primitive-call meter mismatch")
    if search["status"] == "solved":
        if not correct or item["selected_ast"] is None:
            raise ValueError("Unaudited or missing solved AST")
    elif correct or item["selected_ast"] is not None:
        raise ValueError("Unsolved outcome contradicts audit/program")
    return {
        "arm": arm,
        "search_status": search["status"],
        "audited_correct": correct,
        "primitive_calls": calls,
        "tested_candidates": candidates,
        "trace_sha256": search.get("trace_sha256"),
        "selected_ast_sha256": (
            _digest(item["selected_ast"]) if item["selected_ast"] is not None else None),
        "search_cpu_ms": float(search_cpu),
        "search_wall_ms": float(search_wall),
        "audit_cpu_ms": float(audit_cpu),
        "audit_wall_ms": float(audit_wall),
    }


def classify_pair(off: Mapping, on: Mapping, choices: Mapping[str, str]) -> dict[str, object]:
    """Audited accuracy first, primitive call economy second. Unknown is not zero."""
    if not isinstance(choices, dict) or set(choices) != set(POLICIES):
        raise ValueError("Invalid policy choice set")
    if any(type(choices[a]) is not str or choices[a] not in ACTIONS for a in POLICIES):
        raise ValueError("Invalid pretrial choice action")
    if off.get("arm") != "OFF" or on.get("arm") != "ON":
        raise ValueError("Wrong paired arm identity")
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
    """No audit contents, family, hidden source ID or learner-exposed label."""
    if (type(task_id) is not str or not task_id.startswith("t-")
            or len(task_id) != 66):
        raise ValueError("Invalid public task ID")
    if (type(audit_commitment_sha256) is not str
            or len(audit_commitment_sha256) != 64
            or any(x not in "0123456789abcdef" for x in audit_commitment_sha256)):
        raise ValueError("Missing private audit commitment")
    off = normalize_audited_trial(off_raw, arm="OFF")
    on = normalize_audited_trial(on_raw, arm="ON")
    classified = classify_pair(off, on, policy_actions)
    return {
        "schema_version": SCHEMA,
        "task_id": task_id,
        "audit_commitment_sha256": audit_commitment_sha256,
        "trials": {"OFF": off, "ON": on},
        **classified,
    }
