"""Full-domain deterministic engineering census; never a scored learner test."""
from __future__ import annotations
from hashlib import sha256
import json
from .source import SOURCE_VERSION, enumerate_worlds, semantic_signature
from .oracle import certify


def build_report() -> dict:
    worlds = enumerate_worlds()
    if len(worlds) != 512:
        raise AssertionError("source census incomplete")
    partitions = {"CAL64_DISCLOSED": [], "EXT448_NEW": []}
    for w in worlds:
        partitions[w.partition].append(w)
    if len(partitions["CAL64_DISCLOSED"]) != 64 or len(partitions["EXT448_NEW"]) != 448:
        raise AssertionError("source partition broken")
    report = {"source_version": SOURCE_VERSION,
              "status": "SYNTHETIC_ENGINEERING_ONLY_NOT_TRAINED_NOT_F0",
              "calibration_count": 64, "new_design_count": 448,
              "prior": "uniform over 448 source indices then uniform over 4 latent states",
              "audit_labels": "state2 actions 0,1,2: u,v,u_xor_v",
              "world_rows": [], "known_limitations": [
                "constructed grammar; not a sample of independent natural causal families",
                "CAL64 exact prior-study identity unverified; explicitly defined low-index slice",
                "Public Oracle knows source grammar, not sampled source identity; not a trained learner",
                "prediction probes are unreachable from query initial state but deterministic by the same law",
                "no evidence of concept invention, transfer, or cost reduction"]}
    seen_keys = {}
    for w in worlds:
        signature = semantic_signature(w)
        group_id = seen_keys.setdefault(signature, len(seen_keys))
        cert = certify(w.models, "WORLD_KNOWN")
        report["world_rows"].append({"world_id": w.source_id, "partition": w.partition,
            "semantic_group": group_id, "adaptive": cert.numerator_adaptive,
            "fixed": cert.numerator_fixed, "gain_num": cert.gain,
            "denominator": cert.denominator,
            "branch_actions_differ": cert.branch_actions_differ,
            "root_gap": list(cert.root_contingent_gap)})
    for name, group in partitions.items():
        rs = [row for row in report["world_rows"] if row["partition"] == name]
        public_models = tuple(m for w in group for m in w.models)
        pub = certify(public_models, "PUBLIC_MIXTURE")
        report[name] = {
            "world_count": len(group), "distinct_exact_semantics":len({semantic_signature(w) for w in group}),
            "world_oracle_positive":sum(r["gain_num"] > 0 for r in rs),
            "world_oracle_zero":sum(r["gain_num"] == 0 for r in rs),
            "world_oracle_gain_sum_num":sum(r["gain_num"] for r in rs),
            "world_oracle_gain_sum_den":sum(r["denominator"] for r in rs),
            "world_oracle_positive_branch_switch":sum(r["gain_num"] > 0 and r["branch_actions_differ"] for r in rs),
            "public_oracle":pub.to_dict(),
        }
    return report


def canonical_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def report_digest(report: dict) -> str:
    return sha256(canonical_json(report).encode("utf-8")).hexdigest()
