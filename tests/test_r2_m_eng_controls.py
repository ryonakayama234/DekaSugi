"""Stage 3: artificial control arms, tie/capacity/cost, UNKNOWN closure."""
from __future__ import annotations

from copy import deepcopy
from itertools import product
from pathlib import Path
import tempfile
import unittest

from packages.r2_m_eng.closure import audit_closure, validate_closure_audit
from packages.r2_m_eng.controls import (
    CATALOG_DIGEST, CONTROL_ARMS, CONTROL_DIGEST, CONTROL_MANIFEST,
    MACRO_CATALOG, STUMP_ORDER, predict_control,
)
from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.records import PRIVATE_INPUTS, PUBLIC_POINTS, digest
from packages.r2_m_eng.snapshot import load_snapshot, write_snapshot
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
from packages.r2_m_eng.validator import interpret_public


def make_fixture(root: Path, bits=(1, 0, 1, 0)):
    # Artificial source is only used in test-side fixture construction.
    gateway = PublicGateway(SyntheticPrivateSource(bits),
                            opened_at=5, expires_at=20)
    st = gateway.public_state(now=5)
    pre = gateway.precommit(PUBLIC_POINTS[3],
                            expected_legal_digest=st["legal_digest"],
                            prediction=None, now=6)
    gateway.answer(PUBLIC_POINTS[3], precommit=pre, now=7)
    history = gateway.public_state(now=7)["observations"]
    body = decode_public(history).body
    ref = write_snapshot(root / "snapshot.json", history,
                         gateway.public_journal(), body, expires_at=20)
    return ref, history


def truth(bits, point):
    a, b, c, d = bits
    return (a & point[0]) ^ (b & point[1]) ^ (c & point[2]) ^ d


class ControlManifestTests(unittest.TestCase):
    def test_fixed_manifest_and_predeclared_macro_catalog(self):
        self.assertEqual(CONTROL_MANIFEST["version"], "R2-M-CONTROLS-v2.0")
        self.assertEqual(len(MACRO_CATALOG), 16)
        self.assertEqual([bits for bits, _ in MACRO_CATALOG],
                         list(product((0, 1), repeat=4)))
        self.assertEqual(CONTROL_MANIFEST["STUMP-1"]["capacity"], 14)
        self.assertEqual(len(STUMP_ORDER), 14)
        self.assertEqual([row[0] for row in STUMP_ORDER],
                         ["constant0", "constant1",
                          "x:00", "x:01", "x:10", "x:11",
                          "y:00", "y:01", "y:10", "y:11",
                          "z:00", "z:01", "z:10", "z:11"])
        self.assertEqual(CONTROL_MANIFEST["EPISODIC-EXACT"]["capacity"], 8)
        self.assertEqual(CONTROL_MANIFEST["NEAREST-1NN"]["capacity"], 8)
        self.assertEqual(CONTROL_MANIFEST["STATIC-H+"]["ast_nodes_max"], 32)
        self.assertEqual(CONTROL_MANIFEST["learned_policy"]["F01"],
                         "NOT_EVALUATED")
        self.assertEqual(CONTROL_MANIFEST["oracle"],
                         "evaluator_only_not_callable")
        self.assertEqual(CONTROL_DIGEST, digest(CONTROL_MANIFEST))
        self.assertEqual(len(CATALOG_DIGEST), 64)
        for bits, body in MACRO_CATALOG:
            for point in product((0, 1), repeat=3):
                self.assertEqual(interpret_public(body, point), truth(bits, point))

    def test_all_sixteen_artificial_laws_static_and_macro_no_target_injection(self):
        for coefficients in product((0, 1), repeat=4):
            with self.subTest(coefficients=coefficients), tempfile.TemporaryDirectory() as tmp:
                ref, history = make_fixture(Path(tmp), coefficients)
                for point in product((0, 1), repeat=3):
                    for arm in ("STATIC-H+", "FIXED-MACRO"):
                        trace = predict_control(ref.path,
                                                expected_sha256=ref.sha256,
                                                point=point, arm=arm)["trace"]["payload"]
                        self.assertEqual(trace["prediction"], truth(coefficients, point))
                        self.assertEqual(trace["legal_action"], "PREDICT")
                        self.assertEqual(trace["control_manifest_digest"], CONTROL_DIGEST)
                        self.assertEqual(trace["snapshot_sha256"], ref.sha256)
                        self.assertEqual(trace["public_digest"],
                                         load_snapshot(ref.path,
                                                       expected_sha256=ref.sha256)
                                         .payload["public_digest"])
                        self.assertEqual(trace["m_use"], "NOT_CERTIFIED")
                        self.assertEqual(trace["m_gap"], "UNKNOWN")
                        self.assertEqual(trace["cost"]["stored_bytes"], 0)
                        self.assertEqual(trace["cost"]["breakdown"]["restore"]
                                         ["validator_invocations"], 3)
                        self.assertEqual(trace["cost"]["candidate_budget"], 16)
                        self.assertEqual(trace["cost"]["breakdown"]["fixed_catalog_preparation"]
                                         ["catalog_entries"], 16)
                        if arm == "STATIC-H+":
                            self.assertEqual(trace["cost"]["decoder_invocations"], 2)
                            self.assertEqual(trace["cost"]["candidates_generated"], 2)
                            self.assertEqual(trace["cost"]["validator_invocations"], 4)
                        else:
                            self.assertEqual(trace["cost"]["decoder_invocations"], 1)
                            self.assertEqual(trace["cost"]["candidates_generated"], 1)
                            self.assertEqual(trace["cost"]["validator_invocations"], 4)
                self.assertEqual(len(history), 4)

    def test_episodic_uses_all_four_public_rows_and_abstains_on_unseen(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, history = make_fixture(Path(tmp))
            for row in history:
                trace = predict_control(ref.path, expected_sha256=ref.sha256,
                                        point=row.point, arm="EPISODIC-EXACT")["trace"]["payload"]
                self.assertEqual(trace["prediction"], row.answer)
                self.assertEqual(trace["legal_action"], "PREDICT")
            for point in PRIVATE_INPUTS:
                trace = predict_control(ref.path, expected_sha256=ref.sha256,
                                        point=point, arm="EPISODIC-EXACT")["trace"]["payload"]
                self.assertIsNone(trace["prediction"])
                self.assertTrue(trace["abstain"])
                self.assertEqual(trace["legal_action"], "ABSTAIN")
                self.assertEqual(trace["cost"]["breakdown"]["comparator_use"]
                                 ["public_comparisons"], 4)

    def test_nearest_all_minimum_ties_majority_and_equal_abstain(self):
        with tempfile.TemporaryDirectory() as tmp:
            # y only: 011 has equidistant 010=1 and 001=0.
            ref, _ = make_fixture(Path(tmp), (0, 1, 0, 0))
            result = predict_control(ref.path, expected_sha256=ref.sha256,
                                     point=(0, 1, 1), arm="NEAREST-1NN")["trace"]["payload"]
            self.assertIsNone(result["prediction"])
            self.assertEqual(result["legal_action"], "ABSTAIN")
            self.assertEqual(result["cost"]["breakdown"]["comparator_use"]
                             ["public_comparisons"], 4)
            # 111 has three equidistant public neighbors; majority of 0,1,0 is 0.
            majority = predict_control(ref.path, expected_sha256=ref.sha256,
                                       point=(1, 1, 1), arm="NEAREST-1NN")["trace"]["payload"]
            self.assertEqual(majority["prediction"], 0)

    def test_stump_14_slots_min_error_and_first_tie(self):
        for bits in product((0, 1), repeat=4):
            with tempfile.TemporaryDirectory() as tmp:
                ref, history = make_fixture(Path(tmp), bits)
                # Independently fit all fourteen specified hypotheses, including ties.
                scored = []
                for _, axis, pair in STUMP_ORDER:
                    scored.append(sum((pair[0] if axis is None else pair[r.point[axis]])
                                      != r.answer for r in history))
                i = min(range(14), key=lambda index: (scored[index], index))
                label, axis, pair = STUMP_ORDER[i]
                for point in PRIVATE_INPUTS:
                    trace = predict_control(ref.path, expected_sha256=ref.sha256,
                                            point=point, arm="STUMP-1")["trace"]["payload"]
                    self.assertEqual(trace["route"], label)
                    self.assertEqual(trace["prediction"],
                                     pair[0] if axis is None else pair[point[axis]])
                    self.assertEqual(trace["cost"]["breakdown"]["stump_fit_candidates"], 14)
                    self.assertEqual(trace["cost"]["candidates_generated"], 15)
                    self.assertEqual(trace["cost"]["breakdown"]["comparator_use"]
                                     ["public_comparisons"], 56)

    def test_reject_unapproved_and_policy_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, _ = make_fixture(Path(tmp))
            for arm in ("F00", "F01", "F11", "ORACLE-REF", "UNKNOWN", ""):
                with self.subTest(arm=arm), self.assertRaisesRegex(ValueError, "INVALID"):
                    predict_control(ref.path, expected_sha256=ref.sha256,
                                    point=(1, 1, 1), arm=arm)
            with self.assertRaises(TypeError):
                predict_control(ref.path, point=(1, 1, 1), arm="STATIC-H+")
            with self.assertRaisesRegex(ValueError, "INVALID"):
                predict_control(ref.path, expected_sha256="0" * 64,
                                point=(1, 1, 1), arm="STATIC-H+")


class ClosureStage3Tests(unittest.TestCase):
    def test_unknown_inventory_never_certifies_h0_effective(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, _ = make_fixture(Path(tmp))
            record = audit_closure(ref.path, expected_sha256=ref.sha256)
            validate_closure_audit(ref.path, expected_sha256=ref.sha256, record=record)
            c = record["certificate"]
            p = c["payload"]
            self.assertEqual(c["schema"], "HypothesisCertificate/v2")
            self.assertEqual(p["closure_status"], "UNKNOWN")
            self.assertIs(p["closure_complete"], False)
            self.assertEqual(p["effective_h0_reachability"], "UNKNOWN")
            self.assertEqual(p["m_gap"], "UNKNOWN")
            self.assertEqual(p["m_use"], "NOT_CERTIFIED")
            self.assertEqual(p["fixed_off_routes"], [
                "episodic_exact", "h0_consistent", "runtime_affine_decoder",
            ])
            self.assertEqual(p["comparator_arms_not_fixed_dispatch_routes"],
                             list(CONTROL_ARMS))
            self.assertEqual(p["control_manifest_digest"], CONTROL_DIGEST)
            self.assertEqual(p["known_public_observations"], 4)
            self.assertGreater(len(p["unresolved"]), 0)
            self.assertEqual(p["oracle_ref"], "EVALUATOR_ONLY_NOT_EXECUTED")

    def test_rehashed_closure_escalation_route_delete_and_misstatement_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, _ = make_fixture(Path(tmp))
            base = audit_closure(ref.path, expected_sha256=ref.sha256)
            for label, change in (
                ("complete", lambda p: p.update(closure_status="COMPLETE",
                                                closure_complete=True)),
                ("m_gap", lambda p: p.update(m_gap="CERTIFIED")),
                ("missing_route", lambda p: p["fixed_off_routes"].pop()),
                ("missing_unresolved", lambda p: p["unresolved"].clear()),
                ("fake_cert", lambda p: p.update(best_off_fallback="PROVEN")),
                ("fake_policy", lambda p: p["pending_learned_policy_arms"].update(
                    F11="EVALUATED")),
            ):
                with self.subTest(label=label):
                    forged = deepcopy(base)
                    change(forged["certificate"]["payload"])
                    forged["certificate_digest"] = digest(forged["certificate"])
                    with self.assertRaisesRegex(ValueError, "INVALID"):
                        validate_closure_audit(ref.path, expected_sha256=ref.sha256,
                                               record=forged)
            with self.assertRaisesRegex(ValueError, "INVALID"):
                audit_closure(ref.path, expected_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
