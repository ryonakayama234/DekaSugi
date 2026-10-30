"""Adversarial, invented-only tests for the isolated C-G2 contract.

The test fixture writer independently models primitive execution, candidate
trace bytes and public invocation counts; the production evaluator is never
imported. Fixtures are not genuine tasks, and these tests cannot score them.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import product
import ast
from pathlib import Path
import json
import unittest

from packages import opportunity2_audit as a


def _execute(program: tuple[str, ...], value: str,
             observed_meter: dict[str, int] | None = None) -> str:
    """Independently count operations actually executed, not estimated costs."""
    def charged(op: str, source: str) -> str:
        if observed_meter is not None:
            observed_meter[op] = observed_meter.get(op, 0) + 1
        if op == "trim":
            return source.strip()
        if op == "lower":
            return source.lower()
        if op == "upper":
            return source.upper()
        raise AssertionError("unsupported synthetic op")

    for op in program:
        if op == a.MACRO:
            value = charged("lower", charged("trim", value))
        else:
            value = charged(op, value)
    return value


def _ast(program: tuple[str, ...]) -> dict:
    result = {"node_kind": "input", "type": "String"}
    for op in program:
        result = {"node_kind": "call", "type": "String",
                  "op_id": op, "children": [result]}
    return result


def _trial(profile: str, arm: str, public: list[dict],
           audit: dict | None, budget: int, budget_id: str) -> dict:
    stream = sha256()
    tally: dict[str, int] = {}
    status, selected = "not_found", None
    tested = 0
    available = a.candidates(profile, arm)
    for program in available:
        if tested >= budget:
            status = "budget_exhausted"
            break
        tested += 1
        stream.update(json.dumps(list(program), separators=(",", ":")).encode("ascii") + b"\n")
        # Observe every actual primitive call, including examples that fail.
        public_verdicts = tuple(
            _execute(program, row["input"], tally) == row["output"]
            for row in public
        )
        if all(public_verdicts):
            status, selected = "solved", program
            break
    output = (_execute(selected, audit["input"])
              if selected is not None and audit is not None else None)
    return {
        "status": status,
        "program": list(selected) if selected is not None else None,
        "selected_ast": _ast(selected) if selected is not None else None,
        "tested_candidates": tested, "public_verifier_passed": status == "solved",
        "audit_correct_claim": (output == audit["output"] if output is not None else None),
        "audit_output_claim": output,
        "trace_sha256": stream.hexdigest(),
        "primitive_calls": sum(tally.values()), "by_op": tally,
        "observed_at": 20 if arm == "OFF" else 21,
        "budget_id": budget_id,
    }


def fixture(*, fixture_id: str = "fx-pr3-unit-001",
            profile: str = "toy_bias_v1",
            public: list[dict] | None = None, audit: dict | None = None,
            budget: int = 100, audit_missing: bool = False) -> dict:
    if public is None:
        public = [{"input": "red", "output": "red"},
                  {"input": "blue", "output": "blue"}]
    if audit is None and not audit_missing:
        audit = {"input": "RED", "output": "red"}
    if audit_missing:
        audit = None
    budget_id = "fixture-budget-4-100"
    return {
        "schema_version": a.SCHEMA,
        "evidence_class": "SYNTHETIC_INVENTED_ONLY",
        "fixture_id": fixture_id, "source_lock": a.SOURCE_LOCK,
        "public_examples": public, "audit_example": audit,
        "budget": {"max_expanded_nodes": 4, "max_candidates": budget,
                   "budget_id": budget_id},
        "comparison": {"profile": profile, "policy_choice": "OFF",
                       "choice_decided_at": 10, "choice_pretrial_sealed": True},
        "arms": {arm: _trial(profile, arm, public, audit, budget, budget_id)
                 for arm in a.ACTIONS},
    }


def classify(row: dict) -> dict:
    # The expected checksum is supplied separately; recomputing the pin after
    # tampering isolates semantic-integrity checks, not authentic custody.
    return a.normalize_pair(row, a.canonical_digest(row))


class Opportunity2AuditTests(unittest.TestCase):
    def test_current_grammar_exact_oracle(self) -> None:
        off, on = a.candidates("current_v1", "OFF"), a.candidates("current_v1", "ON")
        self.assertEqual((len(off), len(on)), (40, 47))
        self.assertEqual(set(off), {a.expand(p) for p in on})
        self.assertEqual(off[5], ("trim", "lower"))
        self.assertEqual(on[4], (a.MACRO,))

    def test_independent_product_grammar_support_oracle(self) -> None:
        for arm, expected in (("OFF", 40), ("ON", 47)):
            registry = a.PRIMITIVES if arm == "OFF" else a.PRIMITIVES + (a.MACRO,)
            oracle = {p for size in range(4)
                      for p in product(registry, repeat=size)
                      if 1 + sum(2 if op == a.MACRO else 1 for op in p) <= 4}
            self.assertEqual(len(oracle), expected)
            self.assertEqual(oracle, set(a.candidates("current_v1", arm)))

    def test_adapter_has_no_production_imports(self) -> None:
        tree = ast.parse(Path(a.__file__).read_text(encoding="utf-8"))
        allowed = {"__future__", "hashlib", "itertools", "json", "re"}
        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Import):
                self.assertTrue(all(x.name in allowed for x in stmt.names))
            elif isinstance(stmt, ast.ImportFrom):
                self.assertIn(stmt.module, allowed)
                self.assertEqual(stmt.level, 0)

    def test_toy_generalization_discordance_valid_not_integrity(self) -> None:
        result = classify(fixture())
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["arm_outcomes"]["OFF"], "public_found_audit_incorrect")
        self.assertEqual(result["arm_outcomes"]["ON"], "public_found_audit_correct")
        aggregate = a.aggregate_pairs([fixture()], {"fx-pr3-unit-001": a.canonical_digest(fixture())})
        self.assertEqual(aggregate["n_both_public_found"], 1)
        self.assertEqual(aggregate["n_third_audit_discordant_given_both_public_found"], 1)
        self.assertEqual(aggregate["paired_audited_accuracy_diff"], 1.0)
        self.assertEqual(aggregate["n_policy_choice_errors"], 1)
        self.assertFalse(aggregate["scoring_authorized"])

    def test_both_correct_original_profile_and_budget_five_search_limit(self) -> None:
        public = [{"input": "  RED  ", "output": "red"},
                  {"input": "  BLUE  ", "output": "blue"}]
        audit = {"input": "  XYZ  ", "output": "xyz"}
        long = fixture(profile="current_v1", public=public, audit=audit)
        self.assertEqual(classify(long)["arm_outcomes"], {
            "OFF": "public_found_audit_correct",
            "ON": "public_found_audit_correct"})
        self.assertEqual(long["arms"]["OFF"]["tested_candidates"], 6)
        self.assertEqual(long["arms"]["ON"]["tested_candidates"], 5)
        # The reviewer caught short-circuit all(); actual two-public-example
        # invocation counts must be recomputed, not inferred from formulae.
        self.assertEqual(long["arms"]["OFF"]["primitive_calls"], 14)
        self.assertEqual(long["arms"]["ON"]["primitive_calls"], 10)
        short = fixture(profile="current_v1", public=public, audit=audit, budget=5)
        self.assertEqual(classify(short)["arm_outcomes"]["OFF"], "public_not_found")
        self.assertEqual(classify(short)["arm_outcomes"]["ON"], "public_found_audit_correct")

    def test_true_public_not_found_not_generalization_miss(self) -> None:
        public = [{"input": "fiz", "output": "zif"},
                  {"input": "abc", "output": "cba"}]
        row = fixture(profile="current_v1", public=public)
        self.assertEqual(classify(row)["arm_outcomes"],
                         {"OFF": "public_not_found", "ON": "public_not_found"})
        s = a.aggregate_pairs([row], {row["fixture_id"]: a.canonical_digest(row)})
        self.assertEqual(s["n_both_public_found"], 0)
        self.assertEqual(s["n_public_not_found_arms"], 2)
        self.assertEqual(s["third_audit_discordance_rate"], "not_estimable")
        self.assertEqual(s["policy_choice_error_rate"], "not_estimable")
        self.assertEqual(s["n_neither_correct"], 1)

    def test_missing_arm_is_not_observed(self) -> None:
        row = fixture()
        row["arms"]["ON"] = None
        self.assertEqual(classify(row)["status"], "not_observed")
        summary = a.aggregate_pairs([row], {row["fixture_id"]: a.canonical_digest(row)})
        self.assertEqual(summary["n_not_observed"], 1)
        self.assertEqual(summary["paired_audited_accuracy_diff"], "not_estimable")

    def test_missing_third_audit_is_not_observed(self) -> None:
        row = fixture(audit_missing=True)
        self.assertEqual(classify(row)["status"], "not_observed")

    def test_truncated_arm_and_third_example_are_not_observed(self) -> None:
        row = fixture()
        row["arms"]["ON"] = {"status": "solved"}
        self.assertEqual(classify(row)["status"], "not_observed")
        row = fixture()
        row["audit_example"] = {"input": "RED"}
        for arm in a.ACTIONS:
            row["arms"][arm]["audit_correct_claim"] = None
            row["arms"][arm]["audit_output_claim"] = None
        self.assertEqual(classify(row)["status"], "not_observed")
        row["audit_example"]["private_extra"] = "not allowed"
        self.assertEqual(classify(row)["status"], "integrity_invalid")

    def test_budget_id_mismatch_is_non_comparable(self) -> None:
        row = fixture()
        row["arms"]["OFF"]["budget_id"] = "different-synthetic-budget"
        self.assertEqual(classify(row)["status"], "non_comparable")

    def test_changed_hash_without_external_repin_fails(self) -> None:
        row = fixture()
        pin = a.canonical_digest(row)
        row["comparison"]["policy_choice"] = "ON"
        self.assertEqual(a.normalize_pair(row, pin)["status"], "integrity_invalid")

    def test_invalid_replay_and_integrity_gates(self) -> None:
        mutations = [
            lambda x: x["arms"]["OFF"].update(program=["lower"]),
            lambda x: x["arms"]["OFF"].update(selected_ast={"node_kind": "input", "type": "Other"}),
            lambda x: x["arms"]["OFF"].update(public_verifier_passed=False),
            lambda x: x["arms"]["OFF"].update(audit_correct_claim=True),
            lambda x: x["arms"]["OFF"].update(audit_output_claim="red"),
            lambda x: x["arms"]["OFF"].update(tested_candidates=99),
            lambda x: x["arms"]["OFF"].update(trace_sha256="0" * 64),
            lambda x: x["arms"]["OFF"].update(primitive_calls=101),
            lambda x: x["arms"]["OFF"].update(by_op={"evil": 1}),
            lambda x: x["arms"]["OFF"].update(observed_at=8),
            lambda x: x["arms"]["OFF"].update(status="not_found"),
            lambda x: x.update(source_lock="forged"),
            lambda x: x.update(evidence_class="REAL_TRAIN"),
            lambda x: x.update(stealth_private_family="secret"),
            lambda x: x["comparison"].update(choice_pretrial_sealed=False),
            lambda x: x["budget"].update(max_expanded_nodes=5),
            lambda x: x["public_examples"][0].update(output="altered"),
            lambda x: x["audit_example"].update(output="different"),
        ]
        for mutation in mutations:
            row = fixture()
            mutation(row)
            with self.subTest(mutation=mutations.index(mutation)):
                self.assertEqual(classify(row)["status"], "integrity_invalid")

    def test_swapped_arm_evidence_is_invalid(self) -> None:
        row = fixture(profile="current_v1",
                      public=[{"input": "  RED  ", "output": "red"},
                              {"input": "  BLUE  ", "output": "blue"}], budget=5)
        row["arms"]["OFF"], row["arms"]["ON"] = row["arms"]["ON"], row["arms"]["OFF"]
        self.assertEqual(classify(row)["status"], "integrity_invalid")

    def test_fail_closed_entire_batch(self) -> None:
        valid = fixture()
        bad = fixture(fixture_id="fx-pr3-unit-002")
        bad["arms"]["OFF"]["audit_correct_claim"] = True
        pins = {r["fixture_id"]: a.canonical_digest(r) for r in (valid, bad)}
        summary = a.aggregate_pairs([valid, bad], pins)
        self.assertEqual(summary["status"], "invalid_stopped")
        self.assertIsNone(summary["estimates"])
        self.assertEqual(summary["n_integrity_invalid"], 1)
        self.assertNotIn("paired_audited_accuracy_diff", summary)

    def test_duplicate_id_stops_batch(self) -> None:
        row = fixture()
        s = a.aggregate_pairs([row, deepcopy(row)], {row["fixture_id"]: a.canonical_digest(row)})
        self.assertEqual(s["status"], "invalid_stopped")

    def test_toy_reachability_witness_and_finite_limit(self) -> None:
        domain = ("red", "blue", "RED")
        r = a.finite_reachability_probe("toy_bias_v1", domain)
        self.assertEqual(r["status"], "IDENTIFIABLE")
        self.assertFalse(r["universal_impossibility_proved"])
        self.assertNotEqual(r["witness"]["off_program"], r["witness"]["on_program"])

    def test_current_probe_never_claims_universal_impossibility(self) -> None:
        r = a.finite_reachability_probe(
            "current_v1", ("red", "blue", "RED", "  RED  ", " A ", "a"))
        self.assertIn(r["status"], ("INCONCLUSIVE", "IDENTIFIABLE"))
        self.assertFalse(r["universal_impossibility_proved"])
        self.assertFalse(r["scoring_authorized"])

    def test_reject_invalid_domain_and_profile(self) -> None:
        for values in ((), ("red", "red"), ["red"], ("a",) * 13):
            with self.assertRaises(a.EvidenceError):
                a.finite_reachability_probe("current_v1", values)
        with self.assertRaises(a.EvidenceError):
            a.candidates("unknown", "ON")

    def test_zero_observations_and_no_real_score(self) -> None:
        r = a.aggregate_pairs([], {})
        self.assertEqual(r["n_paired_valid"], 0)
        self.assertEqual(r["paired_audited_accuracy_diff"], "not_estimable")
        self.assertEqual(r["new_real_scored_tasks"], 0)


if __name__ == "__main__":
    unittest.main()
