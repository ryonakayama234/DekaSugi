"""METRO-0001 CAL-01: read-only, fixture-only evidence calibration.

No evaluator, learner, private datasets, networking, dynamic imports, or
execution of serialized code. This module never runs heldout experiments.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = "metro-evidence/0.1"
FIXTURE_RUN = "CAL-01"
SUMMARY_SHA256 = "0ef732ea2bc266d8d4da2139f665c0240fc1866d71e52a57151ba31f01e89373"
FORBIDDEN_FIELDS = frozenset(("family", "split", "seed", "source_record_id",
                              "private_audit", "audit_example", "final_label"))
METRICS = {
    "primitive_invocations": ("runtime-canonical-v1", "calls"),
    "cpu_process_ns": ("process-cpu-ns-v1", "ns"),
}

# Fully synthetic, preregistered numeric CAL-01 F01. These are NOT
# string-DSL results and not official TaskSpec ID-v1 identifiers.
GOLDEN_ROWS = (
    ("cal-t01", "OFF", True, "solved", 9, 4),
    ("cal-t01", "ON", True, "solved", 7, 3),
    ("cal-t02", "OFF", True, "solved", 12, 6),
    ("cal-t02", "ON", True, "solved", 17, 7),
    ("cal-t03", "OFF", False, "not_found", 3, 2),
    ("cal-t03", "ON", False, "not_found", 3, 2),
)


class EvidenceError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise EvidenceError("invalid_serialization") from exc


def digest(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def seal(record: Mapping[str, Any]) -> dict[str, Any]:
    """Seal synthetic transport bytes; SHA is integrity, NOT authenticity."""
    result = deepcopy(dict(record))
    result.pop("raw_sha256", None)
    result["raw_sha256"] = digest(result)
    return result


def _has_private_field(node: Any) -> bool:
    if isinstance(node, dict):
        return bool(FORBIDDEN_FIELDS.intersection(node)) or any(
            _has_private_field(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_private_field(v) for v in node)
    return False


def validate(record: Any) -> None:
    if not isinstance(record, dict):
        raise EvidenceError("invalid_schema")
    if _has_private_field(record):
        raise EvidenceError("partition_leak")
    stored = record.get("raw_sha256")
    if not isinstance(stored, str) or len(stored) != 64:
        raise EvidenceError("missing_hash")
    data = dict(record)
    data.pop("raw_sha256")
    if digest(data) != stored:
        raise EvidenceError("invalid_hash")

    required = ("schema_version", "experiment_id", "run_id", "record_role",
                "record_id", "source", "task_ref", "agent_state_ref",
                "trial_ref", "observation", "audit", "raw_sha256")
    if set(record) != set(required):
        raise EvidenceError("missing_or_extra_field")
    if (record["schema_version"] != SCHEMA_VERSION or
            record["experiment_id"] != "METRO-0001" or
            record["run_id"] != FIXTURE_RUN or
            record["record_role"] != "fixture_calibration"):
        raise EvidenceError("invalid_scope")

    src, task, agent = record["source"], record["task_ref"], record["agent_state_ref"]
    trial, obs, audit = record["trial_ref"], record["observation"], record["audit"]
    if not all(isinstance(v, dict) for v in (src, task, agent, trial, obs, audit)):
        raise EvidenceError("invalid_schema")
    if (src.get("reference_id") != "METRO-0001-F01" or
            src.get("content_sha256") != digest("CAL-01-fixed-gold-v1")):
        raise EvidenceError("source_mismatch")
    task_id = task.get("public_task_id")
    if (task_id not in ("cal-t01", "cal-t02", "cal-t03") or
            task.get("domain") != "synthetic_calibration" or
            task.get("public_task_sha256") != digest(task_id)):
        raise EvidenceError("invalid_task")
    if (agent.get("primitive_semantics_version") != "calibration-primitives-v1" or
            agent.get("policy_snapshot_sha256") is not None or
            agent.get("skill_body_sha256") is not None):
        raise EvidenceError("invalid_agent_state")
    if (trial.get("arm") not in ("OFF", "ON") or
            trial.get("record_id") != record["record_id"] or
            record["record_id"] != task_id + ":" + trial["arm"]):
        raise EvidenceError("invalid_trial_identity")
    limits = trial.get("limits")
    if not isinstance(limits, dict) or set(limits) != {"max_ast_nodes", "max_candidates"}:
        raise EvidenceError("invalid_budget")
    nodes, cap = limits["max_ast_nodes"], limits["max_candidates"]
    if (type(nodes) is not int or type(cap) is not int or
            not (1 <= nodes <= 32) or not (1 <= cap <= 10000)):
        raise EvidenceError("invalid_budget")
    candidates = trial.get("tested_candidates")
    if type(candidates) is not int or candidates < 0 or candidates > cap:
        raise EvidenceError("invalid_candidates")
    if trial.get("status") not in ("solved", "not_found", "budget_exhausted"):
        raise EvidenceError("invalid_status")
    if type(trial.get("audit_correct")) is not bool:
        raise EvidenceError("missing_audit")
    # CAL-01's synthetic golden oracle fixes solved and independent audit
    # to agree in BOTH directions; future real audit policies differ.
    if trial["audit_correct"] != (trial["status"] == "solved"):
        raise EvidenceError("inconsistent_verification")
    if audit.get("status") != "verified" or audit.get("evidence_ref") != "cal-audit-only":
        raise EvidenceError("missing_audit")
    if audit.get("evidence_access_class") != "evaluator_only":
        raise EvidenceError("invalid_audit_access")
    metric_id = obs.get("metric_id")
    if metric_id not in METRICS:
        raise EvidenceError("unknown_metric")
    version, unit = METRICS[metric_id]
    if obs.get("metric_version") != version or obs.get("unit") != unit:
        raise EvidenceError("invalid_unit")
    value = obs.get("value")
    if type(value) is not int or value < 0:
        raise EvidenceError("invalid_value")


def gold_evidence() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id, arm, success, status, calls, candidates in GOLDEN_ROWS:
        record = {
            "schema_version": SCHEMA_VERSION,
            "experiment_id": "METRO-0001",
            "run_id": FIXTURE_RUN,
            "record_role": "fixture_calibration",
            "record_id": task_id + ":" + arm,
            "source": {"reference_id": "METRO-0001-F01",
                       "content_sha256": digest("CAL-01-fixed-gold-v1")},
            "task_ref": {"public_task_id": task_id, "domain": "synthetic_calibration",
                         "public_task_sha256": digest(task_id)},
            "agent_state_ref": {"primitive_semantics_version": "calibration-primitives-v1",
                                "policy_snapshot_sha256": None, "skill_body_sha256": None},
            "trial_ref": {"record_id": task_id + ":" + arm, "arm": arm,
                          "status": status, "audit_correct": success,
                          "tested_candidates": candidates,
                          "limits": {"max_ast_nodes": 4, "max_candidates": 100}},
            "observation": {"metric_id": "primitive_invocations",
                            "metric_version": "runtime-canonical-v1",
                            "value": calls, "unit": "calls"},
            "audit": {"status": "verified", "evidence_ref": "cal-audit-only",
                      "evidence_access_class": "evaluator_only"},
        }
        rows.append(seal(record))
    return rows


def analyze(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Return a verified comparable summary or an explicit non_comparable state."""
    if not isinstance(records, (tuple, list)):
        raise EvidenceError("invalid_collection")
    seen: set[tuple[str, str]] = set()
    paired: dict[str, dict[str, dict[str, Any]]] = {}
    for record in records:
        validate(record)
        task = record["task_ref"]["public_task_id"]
        arm = record["trial_ref"]["arm"]
        key = (task, arm)
        if key in seen:
            raise EvidenceError("duplicate_record")
        seen.add(key)
        paired.setdefault(task, {})[arm] = record
    if set(paired) != {"cal-t01", "cal-t02", "cal-t03"} or any(
            set(arms) != {"OFF", "ON"} for arms in paired.values()):
        raise EvidenceError("missing_pair")

    for task_id in sorted(paired):
        off, on = paired[task_id]["OFF"], paired[task_id]["ON"]
        for name in ("domain", "public_task_sha256"):
            if off["task_ref"][name] != on["task_ref"][name]:
                return {"status": "non_comparable", "reason": "task_mismatch"}
        if off["trial_ref"]["limits"] != on["trial_ref"]["limits"]:
            return {"status": "non_comparable", "reason": "budget_mismatch"}
        if (off["agent_state_ref"]["primitive_semantics_version"] !=
                on["agent_state_ref"]["primitive_semantics_version"]):
            return {"status": "non_comparable", "reason": "primitive_mismatch"}
        x, y = off["observation"], on["observation"]
        if ((x["metric_id"], x["metric_version"], x["unit"]) !=
                (y["metric_id"], y["metric_version"], y["unit"]) or
                x["metric_id"] != "primitive_invocations"):
            return {"status": "non_comparable", "reason": "metric_mismatch"}

    summary = {
        "arm_totals": {arm: {
            "audited_correct": sum(int(paired[t][arm]["trial_ref"]["audit_correct"])
                                   for t in sorted(paired)),
            "candidate_count": sum(paired[t][arm]["trial_ref"]["tested_candidates"]
                                   for t in sorted(paired)),
            "primitive_invocations": sum(paired[t][arm]["observation"]["value"]
                                         for t in sorted(paired)),
        } for arm in ("OFF", "ON")},
        "paired": {"OFF_minus_ON_calls": sum(
            paired[t]["OFF"]["observation"]["value"] -
            paired[t]["ON"]["observation"]["value"] for t in sorted(paired))},
        "task_count": len(paired),
    }
    return {"status": "comparable", "summary": summary, "summary_sha256": digest(summary)}


def _tampered_case(case_id: str) -> list[dict[str, Any]]:
    records = gold_evidence()
    if case_id == "F02":
        return list(reversed(records))
    if case_id == "F03":
        return records + [deepcopy(records[0])]
    if case_id == "F04":
        records[0].pop("audit")
        records[0] = seal(records[0])
    elif case_id == "F05":
        records[0]["observation"]["value"] = 999
    elif case_id == "F06":
        records[1]["observation"] = {"metric_id": "cpu_process_ns",
            "metric_version": "process-cpu-ns-v1", "value": 7, "unit": "ns"}
        records[1] = seal(records[1])
    elif case_id == "F07":
        records[0]["task_ref"]["split"] = "final"
        records[0] = seal(records[0])
    elif case_id == "F08":
        records[0]["observation"] = {"metric_id": "cpu_process_ns",
            "metric_version": "process-cpu-ns-v1", "value": -1, "unit": "ns"}
        records[0] = seal(records[0])
    return records


def calibrate() -> dict[str, Any]:
    """Finite, synthetic fixture calibration; NOT a confirmatory AI evaluation."""
    expected_errors = {"F03": "duplicate_record", "F04": "missing_or_extra_field",
                       "F05": "invalid_hash", "F07": "partition_leak",
                       "F08": "invalid_value"}
    results: list[dict[str, str]] = []
    for case_id in ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08"):
        records = gold_evidence() if case_id == "F01" else _tampered_case(case_id)
        try:
            result = analyze(records)
            if case_id in ("F01", "F02"):
                valid = (result.get("status") == "comparable" and
                         result.get("summary_sha256") == SUMMARY_SHA256)
                observed = result.get("summary_sha256", "")
            elif case_id == "F06":
                valid = result.get("status") == "non_comparable" and "paired" not in result
                observed = result.get("status", "")
            else:
                valid, observed = False, "unexpected_success"
        except EvidenceError as error:
            observed = error.code
            valid = error.code == expected_errors.get(case_id)
        results.append({"case_id": case_id, "result": "pass" if valid else "fail",
                        "observed": observed})
    passed = all(row["result"] == "pass" for row in results)
    return {"experiment_id": "METRO-0001", "run_id": FIXTURE_RUN,
            "scope": "synthetic_fixture_only", "status":
            "engineering_fixture_pass" if passed else "engineering_fixture_fail",
            "golden_summary_sha256": SUMMARY_SHA256, "cases": results,
            "m3_non_interference": "requires_separate_unit_regression",
            "scientific_claim": "no_intelligence_improvement_claim"}

def fixture_manifest() -> dict[str, Any]:
    """Immutable serializable CAL-01 source cases, distinct from analysis."""
    cases: list[dict[str, Any]] = []
    for case_id in ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08"):
        rows = gold_evidence() if case_id == "F01" else _tampered_case(case_id)
        cases.append({"case_id": case_id, "raw_rows_sha256": digest(rows),
                      "raw_rows": rows})
    return {"schema_version": "metro-fixtures/0.1", "experiment_id": "METRO-0001",
            "source_kind": "synthetic-only", "cases": cases}
