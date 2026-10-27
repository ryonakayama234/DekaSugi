"""POLICY-DIAG-001: read-only diagnostic; no DEV/FINAL scoring."""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import json
import math

SCHEMA = "policy-diagnostic/0.1"

def _sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def _feature_key(obs):
    vec = obs.vector
    if len(vec) != 8 or not all(math.isfinite(v) for v in vec):
        raise ValueError("invalid feature vector")
    return tuple(vec)

def _validate_snapshot(snapshot):
    snapshot.validate()
    raw = snapshot.to_dict()
    if raw["policy_snapshot_sha256"] != _sha({k: v for k, v in raw.items() if k != "policy_snapshot_sha256"}):
        raise ValueError("snapshot hash mismatch")
    ids = [o.task_id for o in snapshot.observations]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate training ID")
    return raw["policy_snapshot_sha256"]

def snapshot_profile(snapshot):
    """Descriptive data-only snapshot profile, no task scoring."""
    digest = _validate_snapshot(snapshot)
    grouped = defaultdict(list)
    for obs in snapshot.observations:
        grouped[_feature_key(obs)].append(obs)
    collision_groups = [group for group in grouped.values() if len(group) > 1]
    conflicts = sum(1 for group in collision_groups if len({(o.prefer_on, o.off_calls - o.on_calls) for o in group}) > 1)
    return {"snapshot_sha256": digest, "observation_count": len(snapshot.observations), "unique_feature_vectors": len(grouped), "feature_collision_records": sum(len(group) for group in collision_groups), "feature_collision_groups": len(collision_groups), "collision_groups_with_label_or_cost_conflict": conflicts, "prefer_on_count": sum(o.prefer_on for o in snapshot.observations)}

def dream_overlap(b2, b3):
    """Count actual selected Dream IDs; common TRAIN data is not counted."""
    if b2.arm != "B2" or b3.arm != "B3":
        raise ValueError("Expected B2 and B3")
    _validate_snapshot(b2)
    _validate_snapshot(b3)
    a, b = set(b2.ordered_selected_pool_ids), set(b3.ordered_selected_pool_ids)
    if len(a) != 96 or len(b) != 96:
        raise ValueError("Expected 96 each")
    intersection = len(a & b)
    return {"b2_count": len(a), "b3_count": len(b), "overlap_count": intersection, "jaccard": intersection / len(a | b)}

def replay(task, snapshot):
    """Explain exact gating behavior and independently compare to frozen choose()."""
    from packages.kernel import features
    from packages.exp0003a import opaque_id
    from packages.exp0003a.pr3 import choose
    _validate_snapshot(snapshot)
    if task.task_id != opaque_id(task.examples) or len(task.examples) != 2:
        raise ValueError("Invalid public TaskSpec")
    vec = features(task)
    ordered = sorted(((sum(abs(x-y) for x,y in zip(vec,o.vector))/8, o.task_id, o) for o in snapshot.observations), key=lambda x:(x[0],x[1]))[:5]
    if len(ordered) != 5:
        raise ValueError("Too few observations")
    close = sum(d <= .18 for d,_,_ in ordered)
    support = sum(o.prefer_on for _,_,o in ordered)
    saving = sum(o.off_calls-o.on_calls for _,_,o in ordered)/5
    veto = any(o.off_correct and o.on_audit_invalid for _,_,o in ordered)
    if close < 3: action, reason = "OFF", "insufficient_support"
    elif veto: action, reason = "OFF", "audit_safety_veto"
    elif support < 4: action, reason = "OFF", "insufficient_on_votes"
    elif saving < 2: action, reason = "OFF", "insufficient_call_saving"
    else: action, reason = "ON", "cost_supported"
    original = choose(task, snapshot)
    actual = (original.action, original.reason, original.neighbors, original.nearest_distance, original.close_support, original.on_support, original.mean_call_saving)
    expected = (action, reason, tuple(i for _,i,_ in ordered), ordered[0][0], close, support, saving)
    if actual != expected:
        raise ValueError("Frozen choose() parity failure")
    return {"task_id":task.task_id,"arm":snapshot.arm,"action":action,"reason":reason,"close_support":close,"on_support":support,"mean_call_saving":saving,"audit_safety_veto":veto,"neighbors":[{"task_id":i,"distance":d,"prefer_on":o.prefer_on,"call_saving":o.off_calls-o.on_calls,"veto":bool(o.off_correct and o.on_audit_invalid)} for d,i,o in ordered]}

def compare_public_tasks(tasks, b2, b3, archived_rows=None):
    """TaskSpecs MUST originate from already archived public evidence; never synthesize holdouts."""
    _validate_snapshot(b2); _validate_snapshot(b3)
    task_ids = [t.task_id for t in tasks]
    if len(set(task_ids)) != len(task_ids): raise ValueError("Duplicate query task IDs")
    rows=[]
    for task in tasks:
        left,right=replay(task,b2),replay(task,b3)
        aa={n["task_id"] for n in left["neighbors"]}; bb={n["task_id"] for n in right["neighbors"]}
        record={"task_id":task.task_id,"b2":left,"b3":right,"neighbor_overlap":len(aa&bb),"action_disagrees":left["action"]!=right["action"],"reason_disagrees":left["reason"]!=right["reason"],"observed_cost_delta":None,"cost_status":"not_observed"}
        if archived_rows is not None:
            old=archived_rows.get(task.task_id)
            if old is None: raise ValueError("Missing archived task evidence")
            arms=old["arms"]
            if arms["B2"]["decision"]!=left["action"] or arms["B3"]["decision"]!=right["action"]: raise ValueError("Archived action mismatch")
            record["observed_cost_delta"]=arms["B2"]["primitive_invocations"]-arms["B3"]["primitive_invocations"]
            record["cost_status"]="observed"
        rows.append(record)
    return {"schema_version":SCHEMA,"source_snapshot_sha256":{"B2":_validate_snapshot(b2),"B3":_validate_snapshot(b3)},"task_count":len(rows),"action_disagreement_count":sum(x["action_disagrees"] for x in rows),"reason_disagreement_count":sum(x["reason_disagrees"] for x in rows),"mean_neighbor_overlap":sum(x["neighbor_overlap"] for x in rows)/len(rows) if rows else None,"rows":rows}
