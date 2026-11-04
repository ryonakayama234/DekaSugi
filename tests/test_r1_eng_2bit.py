"""R1-ENG N/S/R/E artificial engineering tests. NOT scientific scoring."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from packages.r1_eng.core import (
    DOMAIN, Node, ast_dict, canonicalize, dispatch, digest, load_snapshot,
    make_snapshot, save_snapshot, scan_h0, synthesize_public,
)
from packages.r1_eng.fixture import (
    PublicGateway, PrivateSource, finite_certificate, LEGAL,
)
from packages.r1_eng.runner import run_fixture
from packages.r1_eng.validator import check_ast, validate_public


class R1EngFiniteEngineeringTests(unittest.TestCase):
    def test_N_and_S_paper_diagnosis_are_not_learned_ability(self):
        for case in ("N", "S"):
            for variant in ("A", "B"):
                with self.subTest(case=case, variant=variant), tempfile.TemporaryDirectory() as d:
                    report = run_fixture(case, variant, Path(d))
                    self.assertEqual(report["paper_certificate"]["status"],
                                     "UNIDENTIFIABLE" if case == "N" else "SUFFICIENT_H0")
                    self.assertEqual(report["public_records"][0]["point"], [0, 0])
                    self.assertEqual(report["public_records"][0]["paid"], 1)
                    self.assertEqual(report["synthesis"]["status"], "NOT_APPLICABLE")
                    self.assertFalse(report["synthesis"]["body_from_public_only"])
                    self.assertEqual(report["fresh_use"], [])
                    self.assertFalse(report["scientific_scoring"])
                    self.assertEqual(report["M_gap"], "NOT_EVALUATED")
                    self.assertNotIn("variant", load_snapshot(Path(report["snapshot_path"])).payload())
        self.assertEqual(PrivateSource("N", "A").answer((1, 1)), 1)
        self.assertEqual(PrivateSource("N", "B").answer((1, 1)), 0)
        self.assertNotIn((1, 1), LEGAL["N"])

    def test_E_incomplete_search_never_claims_expression_gap(self):
        with tempfile.TemporaryDirectory() as d:
            report = run_fixture("E", "A", Path(d))
            self.assertEqual(report["paper_certificate"]["status"], "SEARCH_INCOMPLETE")
            self.assertFalse(report["h0_object"]["complete"])
            self.assertEqual(report["h0_object"]["tested"], ["0", "1", "!x", "!z", "z"])
            self.assertEqual(report["h0_object"]["consistent"], [])
            self.assertIsNone(load_snapshot(Path(report["snapshot_path"])).body)
            self.assertEqual(report["M_use_engineering"],
                             "not_certified_no_prediction_or_action_delta")

    def test_R_both_laws_public_synthesis_validator_fresh_use_and_strong_off(self):
        for variant in ("A", "B"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as d:
                report = run_fixture("R", variant, Path(d))
                self.assertEqual(report["h0_object"]["status"], "MISMATCH_CANDIDATE")
                self.assertEqual(report["paper_certificate"]["object_error_min"], {"A": 2, "B": 1})
                self.assertEqual(report["synthesis"]["status"], "PUBLIC_MATCH")
                self.assertTrue(report["validator"]["passed"])
                self.assertEqual(report["validator"]["total"], 4)
                snap = load_snapshot(Path(report["snapshot_path"]))
                self.assertEqual(tuple(o.point for o in snap.observations), DOMAIN)
                self.assertEqual(sum(o.paid for o in snap.observations), 1)
                self.assertEqual(snap.body_digest, digest(ast_dict(snap.body)))
                self.assertEqual(len(report["fresh_use"]), 4)
                self.assertEqual(report["body_off_retains"], ["episodic_lookup", "H0_object"])
                for row in report["fresh_use"]:
                    self.assertEqual(row["on"]["route"], "learned_body")
                    self.assertEqual(row["off"]["route"], "episodic_lookup")
                    self.assertEqual(row["on"]["prediction"], row["off"]["prediction"])
                    self.assertEqual(row["on"]["action"], "PREDICT")
                    self.assertEqual(row["off"]["action"], "PREDICT")
                    self.assertFalse(row["prediction_or_action_delta"])
                    self.assertNotEqual(row["on"]["fresh_process_id"], os.getpid())
                    self.assertNotEqual(row["off"]["fresh_process_id"], os.getpid())
                self.assertEqual(report["M_use_engineering"],
                                 "not_certified_no_prediction_or_action_delta")
                for key in ("M_gap", "N_rep", "U", "T"):
                    self.assertEqual(report[key], "NOT_EVALUATED")
                self.assertFalse(report["scientific_scoring"])

    def test_source_to_public_prohibits_future_and_uncommitted_answers(self):
        gateway = PublicGateway(PrivateSource("N", "A"))
        history, legal, budget = gateway.public()
        self.assertEqual(history, ())
        self.assertEqual(budget, 1)
        self.assertEqual(len(legal), 3)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.ask((0, 0), "0" * 64)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.precommit((0, 1), None)
        gateway = PublicGateway(PrivateSource("N", "A"))
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.precommit((1, 1), None)
        gateway = PublicGateway(PrivateSource("R", "A"))
        pre = gateway.precommit((1, 1), None)
        obs = gateway.ask((1, 1), pre)
        self.assertEqual(obs.answer, 0)
        self.assertEqual(obs.precommit, pre)
        self.assertEqual(obs.paid, 1)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.precommit((1, 1), None)
        allowed_fields = {"seq", "point", "answer", "paid", "legal_digest", "precommit"}
        self.assertEqual(set(obs.as_dict()), allowed_fields)

    def test_validator_rejects_forged_or_untyped_body(self):
        gateway = PublicGateway(PrivateSource("R", "A"))
        pending = gateway.precommit((1, 1), None)
        gateway.ask((1, 1), pending)
        history = gateway.public()[0]
        body = synthesize_public(history).candidate
        self.assertIsNotNone(body)
        self.assertTrue(validate_public(body, history)["passed"])
        self.assertFalse(validate_public(Node("x"), history)["passed"])
        for malformed in (Node("EXEC", ()), Node("x", dtype="String"),
                          Node("AND", (Node("x"),)), Node("NOT", (Node("z"), Node("x")))):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                check_ast(malformed)
        self.assertEqual(canonicalize(canonicalize(body)), canonicalize(body))

    def test_snapshot_is_exclusive_and_rejects_tampering_and_private_fields(self):
        gateway = PublicGateway(PrivateSource("S", "A"))
        token = gateway.precommit((0, 0), None)
        gateway.ask((0, 0), token)
        snap = make_snapshot(gateway.public()[0], None)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "snapshot.json"
            save_snapshot(path, snap)
            with self.assertRaises(FileExistsError):
                save_snapshot(path, snap)
            self.assertEqual(load_snapshot(path), snap)
            record = json.loads(path.read_text())
            record["payload"]["source_law"] = "private"
            record["sha256"] = digest(record["payload"])
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "prohibited fields"):
                load_snapshot(path)
            record["payload"].pop("source_law")
            record["payload"]["policy"] = "attacker"
            record["sha256"] = digest(record["payload"])
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                load_snapshot(path)


if __name__ == "__main__":
    unittest.main()
