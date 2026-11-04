"""Stage-1 import/role/AST/Sleep-lite negative tests; no evaluator scoring."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.records import (
    CLOSURE_STATUS, M_GAP, M_USE, ORACLE_REF_ROLE, PENDING_ARMS,
    SCHEMA_ROLES, Node, SchemaFrame, ast_dict, canonical, digest,
)
from packages.r2_m_eng.sleep_lite import sleep_lite
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
from packages.r2_m_eng.validator import (
    check_ast, interpret_public, same_semantics_all_8, validate_public,
)


def public_fixture(coefficients=(1, 1, 1, 0)):
    gateway = PublicGateway(SyntheticPrivateSource(coefficients), expires_at=10)
    state = gateway.public_state(now=0)
    pre = gateway.precommit((0,0,1),
                            expected_legal_digest=state["legal_digest"],
                            prediction=None, now=1)
    gateway.answer((0,0,1), precommit=pre, now=2)
    return gateway.public_state(now=2)["observations"]


class Stage1BoundaryTests(unittest.TestCase):
    def test_import_dependency_boundary_no_source_private_in_learner_modules(self):
        root = Path(__file__).resolve().parents[1] / "packages" / "r2_m_eng"
        for name in ("__init__", "records", "decoder", "validator", "sleep_lite"):
            with self.subTest(name=name):
                tree = ast.parse((root / (name + ".py")).read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        self.assertNotIn(node.module, ("source_gateway", "fixture",
                                                       "private_source", "evaluator"))
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertNotIn("source_gateway", alias.name)
        # Expose public API only: importing the package must not import source.
        import sys
        # The module may have been explicitly imported by these tests, so inspect
        # package source imports (above) instead of sys.modules global state.

    def test_fixed_six_schema_roles_and_no_oracle_public_route(self):
        self.assertEqual(len(SCHEMA_ROLES), 6)
        self.assertEqual(SCHEMA_ROLES["ScoreReceipt/v2"], "evaluator")
        self.assertEqual(ORACLE_REF_ROLE, "evaluator")
        self.assertEqual(PENDING_ARMS, {"F01": "NOT_EVALUATED",
                                       "F11": "NOT_EVALUATED"})
        self.assertEqual((CLOSURE_STATUS, M_GAP, M_USE),
                         ("UNKNOWN", "UNKNOWN", "NOT_CERTIFIED"))
        frame = SchemaFrame("ScoreReceipt/v2", "evaluator",
                            {"artificial_only": True})
        with self.assertRaisesRegex(ValueError, "INVALID"):
            frame.public_dict()
        with self.assertRaisesRegex(ValueError, "INVALID"):
            SchemaFrame("ScoreReceipt/v2", "public", {})
        with self.assertRaisesRegex(ValueError, "INVALID"):
            SchemaFrame("NoSuchSchema/v2", "public", {})

    def test_public_schema_private_fields_and_closure_upgrade_fail_closed(self):
        for payload in (
            {"private_labels": [0, 1]},
            {"nested": {"seed": 123}},
            {"a": [{"source_law": [1,0,0,1]}]},
            {"target": "synthetic"},
        ):
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "INVALID"):
                SchemaFrame("ConceptBody/v2", "public", payload)
        for schema in ("HypothesisCertificate/v2", "Snapshot/v2"):
            with self.subTest(schema=schema), self.assertRaisesRegex(ValueError, "INVALID"):
                SchemaFrame(schema, "public", {"closure_status": "COMPLETE",
                                               "m_gap": "UNKNOWN"})
        with self.assertRaisesRegex(ValueError, "INVALID"):
            SchemaFrame("UseTrace/v2", "public",
                        {"arm": "F11", "status": "PASSED"})
        self.assertEqual(SchemaFrame("UseTrace/v2", "public",
                                     {"arm": "F01",
                                      "status": "NOT_EVALUATED"}).payload["status"],
                         "NOT_EVALUATED")

    def test_validator_rejects_dag_untyped_unbounded_and_unknown_ops(self):
        leaf = Node("x")
        for invalid in (
            Node("EXEC"),
            Node("x", dtype="String"),
            Node("NOT"),
            Node("NOT", (Node("x"), Node("y"))),
            Node("AND", (leaf, leaf)),  # same object, DAG not expanded tree
            Node("OR", (Node("0"),)),
            Node("1", args=(Node("x"),)),
        ):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "VALIDATION_FAILED"):
                check_ast(invalid)
        chain = Node("x")
        for _ in range(32):
            chain = Node("NOT", (chain,))
        with self.assertRaisesRegex(ValueError, "VALIDATION_FAILED"):
            check_ast(chain)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            interpret_public(Node("x"), (True, 0, 0))

    def test_independent_interpreter_public_validation_and_sleep_equivalence(self):
        history = public_fixture()
        result = decode_public(history)
        self.assertEqual(result.status, "MISMATCH_CANDIDATE")
        receipt = validate_public(result.body, history)
        self.assertTrue(receipt.passed)
        normalized, sleep = sleep_lite(result.body, history)
        self.assertTrue(sleep.meaning_preserved_all_8)
        self.assertEqual(sleep.validator_status, "PUBLIC_MATCH")
        self.assertEqual(sleep.before_digest, receipt.ast_digest)
        self.assertEqual(sleep.after_digest, digest(ast_dict(normalized)))
        self.assertTrue(same_semantics_all_8(result.body, normalized))
        rerun, twice = sleep_lite(normalized, history)
        self.assertEqual(canonical(ast_dict(rerun)), canonical(ast_dict(normalized)))
        self.assertEqual(twice.after_digest, sleep.after_digest)

    def test_sleep_lite_does_not_repair_public_mismatch(self):
        history = public_fixture()
        with self.assertRaisesRegex(ValueError, "VALIDATION_FAILED"):
            sleep_lite(Node("0"), history)

    def test_explicit_h0_limit_is_not_effective_closure(self):
        history = public_fixture((1,0,0,0))
        decoded = decode_public(history)
        self.assertEqual(decoded.status, "SUFFICIENT_H0")
        self.assertIn("x", decoded.certificate.payload["h0_consistent"])
        self.assertEqual(decoded.certificate.payload["h0_effective"], "UNKNOWN")
        self.assertEqual(decoded.certificate.payload["m_gap"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
