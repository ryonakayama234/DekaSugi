"""Disclosed source-only G0C engineering pilot. No TRAIN or sealed scores."""
from __future__ import annotations
import argparse
import json
import platform
from pathlib import Path
from time import perf_counter
from packages.rep005_g0c import PRODUCTIONS, compose, census
from packages.rep005_g0c.opportunity import certify
from packages.rep005_g0c.expressibility import certify_old_h0


def run(proposals: int = 48, proof_seconds: float = 90) -> dict:
    start = perf_counter()
    source = census(proposals, deadline_seconds=proof_seconds)
    if source["status"] != "CERTIFIED_CLOSED_COHORT":
        return {"experiment": "EXP-REP-005-G0C", "status": "SOURCE_NOT_CERTIFIED",
                "source": source, "science": "NOT_RUN"}
    positive = certify(tuple(compose(PRODUCTIONS[i], (0, 1, 2)) for i in (0, 3, 4, 6)), 3)
    negative = certify((compose("direct", (0, 1, 2)),
                        compose("guard_bit", (0, 1, 2))), 2)
    limit = certify((compose("direct", (0, 1, 2)),
                     compose("guard_bit", (0, 1, 2))), 4)
    return {"experiment": "EXP-REP-005-G0C", "status": "SOURCE_ONLY_ENGINEERING_DIAGNOSTIC",
            "source_implementation": "G0C-V5-1", "synthetic_only": True,
            "real_paid_train_actions": 0, "new_family_scientific_score": "NOT_RUN",
            "source": source,
            "expressibility": {
                "direct": certify_old_h0(compose("direct", (0, 1, 2))),
                "semantic_alias_of_direct": certify_old_h0(compose("split_guard_alias", (0, 1, 2))),
                "current_bit_guard": certify_old_h0(compose("guard_bit", (0, 1, 2))),
            },
            "inquiry": {"positive_four_law_budget3": positive,
                        "negative_two_law_budget2": negative,
                        "cap_two_law_budget4": limit},
            "runtime": {"python": platform.python_version(), "platform": platform.platform(),
                        "elapsed_wall_seconds": round(perf_counter() - start, 3)},
            "interpretation": "Meaning/role closed-cohort certificates; not independent family N or learned inquiry benefit"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--proposals", type=int, default=48)
    parser.add_argument("--proof-seconds", type=float, default=90)
    args = parser.parse_args()
    result = run(args.proposals, args.proof_seconds)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "proposals": result.get("source", {}).get("proposals"),
                      "nonalias_role_orbits": result.get("source", {}).get("nonalias_role_orbits"),
                      "adaptive_gain": result.get("inquiry", {}).get("positive_four_law_budget3", {}).get("adaptive_gain"),
                      "report": str(path)}, sort_keys=True))
    if result["status"] != "SOURCE_ONLY_ENGINEERING_DIAGNOSTIC":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
