"""Independent DEV64 artifact auditor. Stdlib-only, no learner imports or holdout scoring."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import re

ARMS = ("B0", "B1", "B2", "B3")
FAMILIES = ("identity", "trim", "lower", "upper", "normalize_lower",
            "normalize_upper", "reverse_ood", "replace_first_ood")
CLOCKS = ("policy_inference_cpu_ms", "policy_inference_wall_ms", "search_cpu_ms",
          "search_wall_ms", "audit_cpu_ms", "audit_wall_ms")
COUNT_FIELDS = ("audited_correct", "false_solved", "tested_candidates",
                "primitive_invocations", "selected_on") + CLOCKS

def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def require(ok, why):
    if not ok:
        raise ValueError(why)

def audit(public, private, freeze, expected_sha):
    require(public["phase"] == private["phase"] == "DEV_ENGINEERING", "Not DEV")
    require(public["final_evaluated"] is False and
            public["registry_promoted"] is False, "FINAL/promotion drift")
    require(type(expected_sha) is str and
            re.fullmatch(r"[0-9a-f]{40}", expected_sha) is not None and
            public["source_commit"] == private["source_commit"] == expected_sha,
            "Source SHA mismatch against runner GITHUB_SHA")
    require(public["freeze_payload_sha256"] == freeze["freeze_payload_sha256"],
            "Freeze drift")
    sealed = freeze["split_data"]["split_sha256"]["dev"]
    require(public["dev_dataset_sha256"] == private["dev_dataset_sha256"] == sealed,
            "DEV hash drift")
    require(public["snapshot_sha256"] == freeze["policy"]["snapshot_sha256"],
            "Snapshot drift")
    rows, records = public["trial_rows"], private["source_records"]
    require(len(rows) == len(records) == 64, "DEV64 cardinality mismatch")
    require(digest(rows) == private["public_trial_rows_sha256"],
            "Public trial evidence digest mismatch")
    require(digest(records) == sealed, "Private DEV raw split digest mismatch")
    by_id = {}
    for i, record in enumerate(records):
        fi, ri = divmod(i, 8)
        family = FAMILIES[fi]
        task_id = record["task_id"]
        require(record["family"] == family and
                record["source_record_id"] == f"dev-f{fi:02d}-i{ri:03d}",
                "Family/source order drift")
        require(task_id not in by_id, "Duplicate private task")
        shape = dict(record["public_task"])
        require(shape.pop("task_id") == task_id and
                "t-" + digest(shape) == task_id and
                record["public_task_sha256"] == task_id[2:],
                "Public TaskSpec hash drift")
        require(record["audit_evidence_ref"] ==
                "audit-sha256:" + digest({"task_id": task_id,
                                          "private_example": record["audit"]}),
                "Private audit reference drift")
        by_id[task_id] = record
    require(len({r["task_id"] for r in rows}) == 64 and
            {r["task_id"] for r in rows} == set(by_id),
            "Public/private task pairing mismatch")
    totals = {a: {k: 0 for k in COUNT_FIELDS} for a in ARMS}
    families = {f: {a: {"audited_correct": 0, "primitive_invocations": 0}
                    for a in ARMS} for f in FAMILIES}
    ood = {a: 0 for a in ARMS}
    diffs, candidate_diffs = [], []
    family_diffs = {f: [] for f in FAMILIES}
    sample_failures = {a: [] for a in ARMS}
    for row in rows:
        task_id = row["task_id"]
        family = by_id[task_id]["family"]
        require(set(row["arms"]) == set(ARMS), "Incomplete arms")
        for arm in ARMS:
            tr = row["arms"][arm]
            require(tr["audit_ref"] == by_id[task_id]["audit_evidence_ref"],
                    "Trial/private audit reference mismatch")
            require(tr["policy_snapshot_sha256"] ==
                    (None if arm == "B0" else public["snapshot_sha256"][arm]),
                    "Arm snapshot mismatch")
            require(tr["decision"] in ("ON", "OFF") and
                    not (arm == "B0" and tr["decision"] != "OFF"),
                    "Illegal arm decision")
            require(type(tr["audited_correct"]) is bool and
                    type(tr["false_solved"]) is bool and
                    not (tr["audited_correct"] and tr["false_solved"]),
                    "Invalid audit verdict")
            for k in ("tested_candidates", "primitive_invocations"):
                require(type(tr[k]) is int and tr[k] >= 0, "Invalid integer counter")
            require(tr["search"]["tested_candidates"] == tr["tested_candidates"] and
                    tr["meter"]["primitive_invocations"] == tr["primitive_invocations"],
                    "Canonical meter/search mismatch")
            by_op = tr["meter"]["by_op"]
            require(type(by_op) is dict and all(
                op in ("trim", "lower", "upper") and type(n) is int and n > 0
                for op, n in by_op.items()) and
                sum(by_op.values()) == tr["primitive_invocations"],
                "Meter by_op breakdown differs from total primitive invocations")
            search = tr["search"]
            status = search["status"]
            require(status in ("solved", "not_found", "budget_exhausted") and
                    search["task_id"] == task_id and
                    type(search["solved"]) is bool and
                    search["solved"] == (status == "solved"),
                    "Audit/search status mismatch")
            program, selected = search["program"], tr["selected_ast"]
            require((status == "solved" and program is not None and
                     program == selected) or
                    (status != "solved" and program is None and selected is None),
                    "Audit/search program/selected AST mismatch")
            require((not tr["audited_correct"] or status == "solved") and
                    tr["false_solved"] == (status == "solved" and
                                           not tr["audited_correct"]),
                    "Audit/search verdict mismatch")
            for k in CLOCKS:
                v = tr[k]
                require(type(v) in (int, float) and math.isfinite(v) and v >= 0,
                        "Invalid CPU/wall cost")
            if arm == "B0":
                require(tr["policy_inference_cpu_ms"] ==
                        tr["policy_inference_wall_ms"] == 0.0,
                        "B0 cannot infer")
            for k in COUNT_FIELDS:
                totals[arm][k] += (tr["decision"] == "ON") if k == "selected_on" else tr[k]
            families[family][arm]["audited_correct"] += tr["audited_correct"]
            families[family][arm]["primitive_invocations"] += tr["primitive_invocations"]
            if family.endswith("_ood") and tr["decision"] == "ON":
                ood[arm] += 1
            if not tr["audited_correct"] and len(sample_failures[arm]) < 8:
                sample_failures[arm].append({
                    "task_id": task_id, "family": family, "decision": tr["decision"],
                    "false_solved": tr["false_solved"],
                    "search_status": tr["search"]["status"],
                })
        a = row["arms"]
        diff = a["B2"]["primitive_invocations"] - a["B3"]["primitive_invocations"]
        diffs.append(diff)
        candidate_diffs.append(a["B2"]["tested_candidates"] -
                               a["B3"]["tested_candidates"])
        family_diffs[family].append(diff)
    require(all(len(v) == 8 for v in family_diffs.values()), "Family pairing drift")
    rng = random.Random(260303)
    fcalls = [sum(family_diffs[f]) for f in FAMILIES]
    bootstrap = sorted(sum(fcalls[rng.randrange(8)] for _ in range(8))
                       for _ in range(1000))
    paired = {
        "primitive_invocations": sum(diffs),
        "tested_candidates": sum(candidate_diffs),
        "audited_correct_B3_minus_B2": totals["B3"]["audited_correct"] -
                                        totals["B2"]["audited_correct"],
        "primitive_regressions": sum(d < 0 for d in diffs),
        "primitive_improvements": sum(d > 0 for d in diffs),
        "family_cluster_bootstrap_95pct_total_calls_delta":
            [bootstrap[24], bootstrap[974]],
        "bootstrap_seed": 260303, "bootstrap_rounds": 1000,
    }
    summary = public["summary"]
    require(summary["task_count"] == 64 and
            summary["arm_totals"] == totals, "Arm totals mismatch")
    require(summary["paired_B2_minus_B3"] == paired, "Paired delta mismatch")
    require(summary["family_summary"] == families, "Family summary mismatch")
    require(summary["ood_false_on_counts"] == ood, "OOD counts mismatch")
    clocks = public["phase_cost_ms"]["asset_load_cost_ms"]
    for unit in ("cpu", "wall"):
        c = [clocks["freeze_verify_" + unit],
             clocks["second_train_dream_replay_" + unit],
             clocks["snapshot_validation_" + unit]]
        full = clocks["asset_load_total_" + unit]
        require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0
                    for v in [*c, full]) and full + 1e-6 >= sum(c),
                "Frozen replay cost ledger mismatch")
    return {
        "schema": "exp0003a-dev64-independent-audit-v1", "status": "pass",
        "source_commit": public["source_commit"], "task_count": 64,
        "arm_trial_count": 256, "freeze_payload_sha256": public["freeze_payload_sha256"],
        "dev_dataset_sha256": sealed, "arm_totals": totals,
        "paired_B2_minus_B3": paired, "family_summary": families,
        "ood_false_on_counts": ood, "failure_examples": sample_failures,
        "interpretation": "DEV engineering only; FINAL sealed; no retuning.",
    }

def audit_paths(public_path, private_path, freeze_path, expected_sha, attempt_path):
    raw_public, raw_private = public_path.read_bytes(), private_path.read_bytes()
    attempt = json.loads(attempt_path.read_bytes())
    require(attempt["source_sha"] == expected_sha and
            attempt["event"] == "push" and attempt["ref"] == "refs/heads/main" and
            str(attempt["run_attempt"]) == "1",
            "Attempt metadata disagrees with exact main-run SHA")
    report = audit(json.loads(raw_public), json.loads(raw_private),
                   json.loads(freeze_path.read_bytes()), expected_sha)
    report["public_json_sha256"] = sha256(raw_public).hexdigest()
    report["private_json_sha256"] = sha256(raw_private).hexdigest()
    return report

def main():
    p = argparse.ArgumentParser()
    for name in ("public", "private", "freeze", "output", "attempt"):
        p.add_argument("--" + name, required=True, type=Path)
    p.add_argument("--source-sha", required=True)
    a = p.parse_args()
    report = audit_paths(a.public, a.private, a.freeze,
                         a.source_sha, a.attempt)
    with a.output.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
    print("INDEPENDENT_AUDIT=PASS")
    print("PUBLIC_JSON_SHA256=" + report["public_json_sha256"])
    print("PRIVATE_JSON_SHA256=" + report["private_json_sha256"])
    print("DEV64_SUMMARY=" + json.dumps({
        "arm_totals": report["arm_totals"],
        "paired_B2_minus_B3": report["paired_B2_minus_B3"],
        "ood_false_on_counts": report["ood_false_on_counts"],
        "failure_examples": report["failure_examples"],
    }, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
