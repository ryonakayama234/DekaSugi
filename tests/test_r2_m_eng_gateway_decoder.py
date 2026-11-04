"""R2-M-ENG stage 1: artificial known-law exhaustive and negative checks only."""
from __future__ import annotations

from dataclasses import replace
from itertools import product
import unittest

from packages.r2_m_eng.decoder import compile_affine, decode_public
from packages.r2_m_eng.records import (
    FAMILY_SIZE, MAX_AST_NODES, PRIVATE_INPUTS, PUBLIC_POINTS, Node,
    PublicObservation, ast_size, digest, validate_public_history,
)
from packages.r2_m_eng.source_gateway import (
    PublicGateway, SyntheticPrivateSource,
)
from packages.r2_m_eng.validator import check_ast, interpret_public, validate_public


def complete_gateway(coefficients=(1, 1, 0, 1)):
    gateway = PublicGateway(SyntheticPrivateSource(coefficients), expires_at=10)
    state = gateway.public_state(now=0)
    commitment = gateway.precommit(
        PUBLIC_POINTS[3], expected_legal_digest=state["legal_digest"],
        prediction=0, now=1)
    gateway.answer(PUBLIC_POINTS[3], precommit=commitment, now=2)
    return gateway


class GatewayDecoderTests(unittest.TestCase):
    def test_all_sixteen_human_supplied_laws_public_identification(self):
        for coefficients in product((0, 1), repeat=4):
            with self.subTest(coefficients=coefficients):
                gateway = PublicGateway(
                    SyntheticPrivateSource(tuple(coefficients)), expires_at=10)
                before = decode_public(gateway.public_state(now=0)["observations"])
                self.assertEqual(before.status, "UNIDENTIFIABLE")
                self.assertEqual(before.candidates_generated, 0)
                self.assertEqual(before.decoder_invocations, 0)
                self.assertEqual(before.certificate.payload["version_space_size"], 2)
                state = gateway.public_state(now=0)
                commitment = gateway.precommit(
                    (0, 0, 1), expected_legal_digest=state["legal_digest"],
                    prediction=None, now=1)
                obs = gateway.answer((0, 0, 1), precommit=commitment, now=2)
                self.assertEqual(obs.paid, 1)
                history = gateway.public_state(now=2)["observations"]
                result = decode_public(history)
                self.assertEqual(result.coefficients, tuple(coefficients))
                self.assertEqual(result.candidates_generated, 1)
                self.assertEqual(result.decoder_invocations, 1)
                self.assertEqual(result.family_size, FAMILY_SIZE)
                self.assertEqual(result.candidate_budget, 16)
                self.assertEqual(result.certificate.payload["design_rank"], 4)
                self.assertEqual(result.certificate.payload["closure_status"], "UNKNOWN")
                self.assertEqual(result.certificate.payload["m_gap"], "UNKNOWN")
                self.assertEqual(result.concept.payload["validated"], False)
                self.assertEqual(result.concept.payload["ast_nodes_static"], ast_size(result.body))
                self.assertTrue(validate_public(result.body, history).passed)
                for point in product((0, 1), repeat=3):
                    a, b, c, d = coefficients
                    expected = (a & point[0]) ^ (b & point[1]) ^ (c & point[2]) ^ d
                    # The eight synthetic test expectations are NOT private scientific labels.
                    self.assertEqual(interpret_public(result.body, point), expected)
                self.assertEqual(len(gateway.public_journal()), 5)
                self.assertEqual([e["event"] for e in gateway.public_journal()],
                                 ["initial", "initial", "initial", "precommit", "answer"])
                self.assertEqual(gateway.public_state(now=2)["legal_actions"], ())
                self.assertEqual(gateway.public_state(now=2)["paid_budget_remaining"], 0)
                self.assertEqual(PUBLIC_POINTS + PRIVATE_INPUTS,
                                 ((0,0,0),(1,0,0),(0,1,0),(0,0,1),
                                  (0,1,1),(1,0,1),(1,1,0),(1,1,1)))

    def test_compiler_structure_max_and_left_associativity(self):
        body = compile_affine((1, 1, 1, 1))
        self.assertEqual(ast_size(body), 26)
        self.assertEqual(check_ast(body), 26)
        self.assertLessEqual(ast_size(body), MAX_AST_NODES)
        self.assertEqual(body.op, "NOT")
        self.assertEqual(body.args[0].op, "OR")
        self.assertEqual(compile_affine((0, 0, 0, 0)).op, "0")
        self.assertEqual(compile_affine((0, 0, 0, 1)).op, "NOT")
        self.assertEqual(compile_affine((0, 1, 0, 0)).op, "y")
        with self.assertRaisesRegex(ValueError, "INVALID"):
            compile_affine((True, 0, 0, 0))

    def test_public_only_surface_has_no_private_coefficients_or_labels(self):
        gateway = complete_gateway()
        for event in gateway.public_journal():
            self.assertEqual(set(event), {
                "schema", "event", "seq", "point", "legal_actions",
                "legal_digest", "event_at", "answer", "paid_cost",
                "precommit", "prediction",
            })
            self.assertNotIn("law", event)
            self.assertNotIn("seed", event)
            self.assertNotIn("private_labels", event)
            self.assertNotIn("target", event)
        self.assertNotIn("coefficients", gateway.public_state(now=2))
        self.assertNotIn("source", gateway.public_state(now=2))

    def test_precommit_digest_is_bound_to_preanswer_state_and_time(self):
        gateway = PublicGateway(SyntheticPrivateSource((0, 1, 0, 1)), expires_at=10)
        st = gateway.public_state(now=0)
        commitment = gateway.precommit((0, 0, 1),
                                       expected_legal_digest=st["legal_digest"],
                                       prediction=1, now=3)
        self.assertEqual(len(commitment), 64)
        self.assertNotIn("answer", gateway.public_journal()[-1]["event"])
        paid = gateway.answer((0, 0, 1), precommit=commitment, now=4)
        self.assertEqual(paid.precommit, commitment)
        self.assertEqual(gateway.public_journal()[-1]["precommit"], commitment)
        self.assertEqual(gateway.public_journal()[-1]["paid_cost"], 1)

    def test_reject_unauthorized_paid_query_and_quarantine(self):
        for illegal in ((1, 1, 1), (0, 1, 1), (1, 0, 0)):
            with self.subTest(illegal=illegal):
                gateway = PublicGateway(SyntheticPrivateSource((1,0,0,1)))
                st = gateway.public_state(now=0)
                with self.assertRaisesRegex(ValueError, "INVALID"):
                    gateway.precommit(illegal, expected_legal_digest=st["legal_digest"],
                                      prediction=None, now=1)
                with self.assertRaisesRegex(ValueError, "INVALID"):
                    gateway.public_state(now=2)

    def test_reject_bad_legal_digest_and_uncommitted_response(self):
        gateway = PublicGateway(SyntheticPrivateSource((1,0,0,1)))
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.precommit((0,0,1), expected_legal_digest="0"*64,
                              prediction=None, now=1)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.public_journal()
        gateway = PublicGateway(SyntheticPrivateSource((1,0,0,1)))
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.answer((0,0,1), precommit="0"*64, now=1)

    def test_reject_mismatched_or_repeated_precommit_and_bad_clock(self):
        gateway = PublicGateway(SyntheticPrivateSource((1, 0, 0, 1)))
        st = gateway.public_state(now=0)
        gateway.precommit((0,0,1), expected_legal_digest=st["legal_digest"],
                          prediction=None, now=1)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.precommit((0,0,1), expected_legal_digest=st["legal_digest"],
                              prediction=None, now=2)
        gateway = PublicGateway(SyntheticPrivateSource((0,0,0,0)))
        gateway.public_state(now=3)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.public_state(now=2)
        gateway = complete_gateway()
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.answer((0,0,1), precommit="0"*64, now=3)

    def test_q001_deadline_no_late_response(self):
        gateway = PublicGateway(SyntheticPrivateSource((1,1,1,1)),
                                expires_at=2)
        st = gateway.public_state(now=3)
        self.assertEqual(st["legal_actions"], ())
        with self.assertRaisesRegex(ValueError, "UNIDENTIFIABLE"):
            gateway.precommit((0,0,1), expected_legal_digest=st["legal_digest"],
                              prediction=None, now=4)
        gateway = PublicGateway(SyntheticPrivateSource((1,1,1,1)),
                                expires_at=2)
        st = gateway.public_state(now=0)
        pre = gateway.precommit((0,0,1), expected_legal_digest=st["legal_digest"],
                                prediction=None, now=1)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            gateway.answer((0,0,1), precommit=pre, now=3)

    def test_reject_malformed_history_and_false_public_candidate(self):
        history = complete_gateway((1,1,0,1)).public_state(now=2)["observations"]
        for bad in (
            (history[0], history[1], history[2], history[2]),
            history[:3] + (replace(history[3], point=(1,1,1)),),
            history[:3] + (replace(history[3], paid=0),),
            history[:3] + (replace(history[3], precommit=None),),
            history[:3] + (replace(history[3], answer=True),),
            history[:3] + (replace(history[3], received_at=-1),),
        ):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "INVALID"):
                decode_public(bad)
        with self.assertRaisesRegex(ValueError, "UNIDENTIFIABLE"):
            validate_public(Node("0"), history[:3])
        self.assertEqual(validate_public(Node("0"), history).status, "VALIDATION_FAILED")
        self.assertFalse(validate_public(Node("0"), history).passed)

    def test_no_illegal_type_acceptance(self):
        for value in ((0, 0, True), (0, 1), [0,0,1], (0,0,2)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                SyntheticPrivateSource((1,0,0,0))._answer(value)
        with self.assertRaises(ValueError):
            SyntheticPrivateSource((1,1,1,True))


if __name__ == "__main__":
    unittest.main()
