"""POLICY-DIAG-001: archive-verified, aggregate-only, read-only DEV64 analysis.

Requires EXISTING original evidence ZIP and EXISTING PR3 TRAIN/DREAM ZIP.
Never invokes a DEV/FINAL generator, learner, synthesizer or verifier.
Never writes task IDs, audit examples or raw trial rows to report.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

DEV_PUBLIC_SHA = "2fa48c841e99a69275c8bd3a5bd78eb2e01d4a3fcc226a6358958bf5cc053134"
PR3_PUBLIC_SHA = "da34216419bab7a95bf93d9b6d5805cebf900a9c662efc91a77b4aa8536e621e"
FREEZE_SHA = "1e0f6daf1cb80262c187c60a3e0a4d2e76dafea911f0633feed3c40f93db8f44"
DEV_SOURCE_COMMIT = "26eaf3b4c4717968d68eb7f383b126b23b2062c8"
DEV_DATA_SHA = "258237ccc5c360a61d5c0a9e95d03610c0e4b7003e6268323df8429d4eabda45"
PR3_SOURCE_SHA = "dae68d03ff6c6f1989e823e17e17308a6e515d4f4160070aa73016e00ba8190e"
SNAPSHOT_SHA = {
    "B1": "3b4fc00f8ad0fe2f1cc0978886d7bc7a6285ed002c842ceeb0106fd51ee5afd4",
    "B2": "01d5595e1b4c32d200e2734630f38a848e77a64f356741445e011865834f5af7",
    "B3": "a6d46ab5dd697e8e90789693fdd3bd67bbca445ec07bc8b119401e1c0cf1e210",
}

def require_digest(data: bytes, expected: str, label: str) -> None:
    actual = sha256(data).hexdigest()
    if actual != expected:
        raise ValueError(f"{label}: unexpected sha256 {actual}")

def canonical_sha(obj: object) -> str:
    return sha256(json.dumps(obj, ensure_ascii=False, allow_nan=False,
                sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

def _read_verified_member(path: Path, name: str, checksum: str) -> dict:
    with ZipFile(path) as archive:
        if archive.namelist().count(name) != 1:
            raise ValueError(f"Missing or duplicate permitted member {name}")
        # Do NOT open or parse the evaluator-private companion ZIP member.
        raw = archive.read(name)
    require_digest(raw, checksum, name)
    return json.loads(raw)

def load_verified(original_dev_zip: Path, train_dream_zip: Path,
                  frozen_json: Path) -> tuple[dict, dict, dict]:
    # Source-first: load pinned declared freeze BEFORE accepting evidence.
    freeze = json.loads(frozen_json.read_text(encoding="utf-8"))
    if (freeze.get("freeze_payload_sha256") != FREEZE_SHA
            or freeze.get("holdout_scoring_permitted") is not False
            or freeze.get("split_data", {}).get("pr3_source_manifest_sha256") != PR3_SOURCE_SHA
            or freeze.get("split_data", {}).get("split_sha256", {}).get("dev") != DEV_DATA_SHA):
        raise ValueError("Freeze-source/permission mismatch")
    for arm in ("B1", "B2", "B3"):
        if freeze["policy"]["snapshot_sha256"][arm] != SNAPSHOT_SHA[arm]:
            raise ValueError("Freeze snapshot mismatch")
    dev = _read_verified_member(original_dev_zip, "public.json", DEV_PUBLIC_SHA)
    dream = _read_verified_member(train_dream_zip, "EXP-0003A-PR3-TRAIN-DREAM.json", PR3_PUBLIC_SHA)
    if (dev.get("source_commit") != DEV_SOURCE_COMMIT
            or dev.get("freeze_payload_sha256") != FREEZE_SHA
            or dev.get("dev_dataset_sha256") != DEV_DATA_SHA
            or dev.get("final_evaluated") is not False
            or len(dev.get("trial_rows", [])) != 64
            or dream.get("dev_or_final_evaluated") is not False
            or dream.get("source_manifest_sha256") != PR3_SOURCE_SHA):
        raise ValueError("Original scoring / TRAIN-only provenance mismatch")
    for arm in ("B1", "B2", "B3"):
        snapshot = dream["snapshots"][arm]
        sig = snapshot["policy_snapshot_sha256"]
        payload = {k: v for k, v in snapshot.items() if k != "policy_snapshot_sha256"}
        if (canonical_sha(payload) != sig or sig != SNAPSHOT_SHA[arm]
                or dream["snapshot_hashes"][arm] != sig
                or dev["snapshot_sha256"][arm] != sig
                or snapshot["arm"] != arm):
            raise ValueError("Snapshot integrity mismatch")
        if len(snapshot["observations"]) != (160 if arm == "B1" else 256):
            raise ValueError("Unexpected training observation count")
        if arm in ("B2", "B3") and (
                snapshot["ordered_selected_pool_ids"] != freeze["policy"][arm.lower()+"_ordered_selected_pool_ids"]
                or snapshot["ordered_selected_task_ids"] != freeze["policy"][arm.lower()+"_ordered_selected_task_ids"]):
            raise ValueError("Frozen Dream selection mismatch")
    return dev, dream, freeze

def summarize(dev: dict, dream: dict, freeze: dict) -> dict:
    """No TaskSpec recomputation: only previously archived public evidence."""
    rows = dev["trial_rows"]
    if len(rows) != 64 or len({r["task_id"] for r in rows}) != 64:
        raise ValueError("64 unique original public trial IDs required")
    profiles = {}
    observations_by_arm = {}
    for arm in ("B1", "B2", "B3"):
        obs = dream["snapshots"][arm]["observations"]
        if len({o["task_id"] for o in obs}) != len(obs):
            raise ValueError("Duplicated snapshot observation")
        observations_by_arm[arm] = {o["task_id"]: o for o in obs}
        grouped = defaultdict(list)
        for o in obs:
            grouped[tuple(o["vector"])].append(o)
        duplicated = [g for g in grouped.values() if len(g)>1]
        profiles[arm] = {
            "observations": len(obs),
            "unique_8d_vectors": len(grouped),
            "collision_groups": len(duplicated),
            "collision_records": sum(map(len, duplicated)),
            "conflicting_label_or_cost_groups": sum(
                len({(o["prefer_on"], o["off_calls"]-o["on_calls"]) for o in g})>1
                for g in duplicated),
            "prefer_on_count": sum(o["prefer_on"] for o in obs),
        }
    B2 = set(freeze["policy"]["b2_ordered_selected_pool_ids"])
    B3 = set(freeze["policy"]["b3_ordered_selected_pool_ids"])
    if len(B2)!=96 or len(B3)!=96: raise ValueError("Dream cardinality drift")
    joint = len(B2 & B3)
    reasons = {arm: Counter() for arm in ("B2", "B3")}
    votes = {arm: Counter() for arm in ("B2", "B3")}
    saving = {arm: Counter() for arm in ("B2", "B3")}
    overlaps = Counter()
    different_votes = different_savings = different_actions = different_reasons = different_costs = different_veto = 0
    one_action_delta = []
    for row in rows:
        traces = {}
        for arm in ("B2","B3"):
            action = row["arms"][arm]
            if action["policy_snapshot_sha256"] != SNAPSHOT_SHA[arm] or len(action["neighbors"])!=5:
                raise ValueError("Archived decision/snapshot association invalid")
            if len(set(action["neighbors"]))!=5:
                raise ValueError("Repeated archived 5NN ID")
            try:
                near = [observations_by_arm[arm][n] for n in action["neighbors"]]
            except KeyError as e:
                raise ValueError("Neighbor absent from exact frozen snapshot") from e
            on = sum(o["prefer_on"] for o in near)
            mean_save = sum(o["off_calls"] - o["on_calls"] for o in near)/5
            veto = any(o["off_correct"] and o["on_audit_invalid"] for o in near)
            reason = action["decision_reason"]
            if reason not in {"insufficient_support","audit_safety_veto","insufficient_on_votes","insufficient_call_saving","cost_supported"}:
                raise ValueError("Unexpected original reason")
            if (reason=="cost_supported" and (on<4 or mean_save<2 or veto or action["decision"]!="ON")
                    or reason=="insufficient_on_votes" and (on>=4 or veto or action["decision"]!="OFF")
                    or reason=="audit_safety_veto" and (not veto or action["decision"]!="OFF")
                    or reason=="insufficient_call_saving" and (on<4 or mean_save>=2 or veto or action["decision"]!="OFF")):
                raise ValueError("Stored choice inconsistent with frozen neighbor labels/cost")
            reasons[arm][reason] += 1
            votes[arm][str(on)] += 1
            saving[arm][str(mean_save)] += 1
            traces[arm] = (on,mean_save,veto,action)
        x,y=traces["B2"],traces["B3"]
        overlap=len(set(x[3]["neighbors"])&set(y[3]["neighbors"]))
        overlaps[str(overlap)] += 1
        different_votes += (x[0]!=y[0])
        different_savings += (x[1]!=y[1])
        different_veto += (x[2]!=y[2])
        different_reasons += (x[3]["decision_reason"]!=y[3]["decision_reason"])
        different_actions += (x[3]["decision"]!=y[3]["decision"])
        different_costs += (x[3]["primitive_invocations"]!=y[3]["primitive_invocations"])
        if x[3]["decision"]!=y[3]["decision"]:
            one_action_delta.append({"B2_action":x[3]["decision"],"B3_action":y[3]["decision"],
                "B2_votes":x[0],"B3_votes":y[0],
                "B2_mean_call_saving":x[1],"B3_mean_call_saving":y[1],
                "B2_calls":x[3]["primitive_invocations"],"B3_calls":y[3]["primitive_invocations"],
                "B2_reason":x[3]["decision_reason"],"B3_reason":y[3]["decision_reason"]})
    if len(one_action_delta)>64: raise ValueError("Unexpected analysis size")
    if any(dev["summary"]["arm_totals"][arm]["primitive_invocations"] !=
            sum(row["arms"][arm]["primitive_invocations"] for row in rows)
           for arm in ("B0","B1","B2","B3")):
        raise ValueError("Original integer aggregate mismatch")
    return {
        "schema_version":"policy-diag-archive-report/0.1",
        "status":"completed_archived_public_partial_diagnosis",
        "scientific_class":"post_DEV_exploratory_not_CONFIRMATORY",
        "source_bytes_sha256":{"dev_public":DEV_PUBLIC_SHA,"train_dream_public":PR3_PUBLIC_SHA},
        "freeze_payload_sha256":FREEZE_SHA,
        "policy_snapshot_sha256":SNAPSHOT_SHA,
        "population":"fixed original one-shot DEV64, no scoring, N=64",
        "dream_selection":{"B2":96,"B3":96,"overlap":joint,"jaccard":joint/(192-joint)},
        "snapshot_feature_profiles":profiles,
        "archived_query_5NN":{
            "tasks":64,"overlap_histogram":dict(sorted(overlaps.items())),
            "overlap_mean":sum(int(k)*v for k,v in overlaps.items())/64,
            "different_neighbor_sets":64-overlaps.get("5",0),
            "different_ON_votes":different_votes,
            "different_mean_call_saving":different_savings,
            "different_veto":different_veto,
            "different_action":different_actions,
            "different_reason":different_reasons,
            "different_observed_primitive_cost":different_costs,
            "ON_votes_histograms":{a:dict(sorted(v.items())) for a,v in votes.items()},
            "decision_reason_histograms":{a:dict(sorted(v.items())) for a,v in reasons.items()},
            "action_disagreement_detail_without_task_ID":one_action_delta,
        },
        "unobserved":{"query_public_TaskSpec":True,
            "8D_query_features":True,
            "per_neighbor_distance":True,
            "close_support_replay":True,
            "new_DEV_or_FINAL_trials":True},
        "interpretation_limit":"Can join archived neighbor IDs to frozen observations and reconstruct votes/savings/veto; cannot independently re-run features or distance ranking from absent archived public TaskSpec. No causal identifiability or confirmatory H3 claim.",
    }

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-dev-zip", type=Path,required=True)
    parser.add_argument("--train-dream-zip",type=Path,required=True)
    parser.add_argument("--freeze",type=Path,default=Path("experiments/EXP-0003A/freeze-v1.json"))
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    dev, dream, freeze=load_verified(args.original_dev_zip,args.train_dream_zip,args.freeze)
    result=summarize(dev,dream,freeze)
    if args.output.exists(): raise FileExistsError("Refuse to overwrite immutable diagnostic output")
    args.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("policy-diag: verified and summarized original public evidence only; no task scoring")
if __name__=="__main__":
    main()
