"""Explicit newly disclosed G0 source-only engineering diagnostic, not a score."""
import json
from packages.rep005_g0b_v4 import (
    Edge, certificate_catalog, feasible_fixed_opportunity, law,
    legal_closed_class_id, memorylessness_witness,
)


def main():
    m0, direct, lag1 = law(), law(Edge(0, 1)), law(Edge(0, 1, 1))
    result = {
        "status": "G0_ENGINEERING_ONLY_NO_TRAIN_NO_SCIENCE",
        "source_catalog": certificate_catalog(),
        "witness_memoryless_contradiction": memorylessness_witness(lag1),
        "id_null_vs_direct_B1": legal_closed_class_id((m0, direct), 1),
        "id_null_vs_lag1_B1": legal_closed_class_id((m0, lag1), 1),
        "id_null_vs_lag1_B2": legal_closed_class_id((m0, lag1), 2),
        "proof_budget_cap": legal_closed_class_id((m0, lag1), 2, max_nodes=0),
        "feasible_public_question_vs_repeated_set": feasible_fixed_opportunity(
            m0, direct, ("pulse", 0, -1), ("set", 0, 0)),
        "scientific_result": "NOT_RUN",
        "full_hplus_G": "NOT_CERTIFIED",
        "independent_family_power": "NOT_CERTIFIED",
        "paid_wake_sleep_use": "NOT_RUN",
    }
    print("REP005_V4_G0_RESULT_START")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    print("REP005_V4_G0_RESULT_END")


if __name__ == "__main__":
    main()
