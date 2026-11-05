"""R2-M-ENG stage 2 artificial-only Snapshot, fixed dispatch and meter tests."""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.dispatch import predict_fixed, write_trace_once
from packages.r2_m_eng.meter import AstCounts, cost_ledger, measure_ast
from packages.r2_m_eng.records import Node, canonical, digest
from packages.r2_m_eng.snapshot import (
    CLOSURE_MANIFEST, FIXED_POLICY, ROUTES, load_snapshot, write_snapshot,
)
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource
from packages.r2_m_eng.validator import interpret_public


def fixture(coefficients=(1, 1, 0, 1)):
    source = SyntheticPrivateSource(coefficients)  # test oracle; never into snapshot
    gateway = PublicGateway(source, opened_at=5, expires_at=20)
    state = gateway.public_state(now=5)
    pre = gateway.precommit((0, 0, 1),
                            expected_legal_digest=state["legal_digest"],
                            prediction=0, now=6)
    gateway.answer((0, 0, 1), precommit=pre, now=7)
    state = gateway.public_state(now=7)
    return state["observations"], gateway.public_journal()


def create_snap(root: Path, coefficients=(1, 1, 0, 1)):
    history, journal = fixture(coefficients)
    decoded = decode_public(history)
    path = root / "snapshot.json"
    ref = write_snapshot(path, history, journal, decoded.body)
    return ref, history, journal, decoded


class SnapshotStage2Tests(unittest.TestCase):
    def test_all_sixteen_synthetic_families_public_snapshot(self):
        for coefficients in product((0, 1), repeat=4):
            with self.subTest(coefficients=coefficients), tempfile.TemporaryDirectory() as tmp:
                ref, history, journal, decoded = create_snap(Path(tmp), tuple(coefficients))
                self.assertTrue(Path(ref.path).is_absolute())
                snap = load_snapshot(ref.path, expected_sha256=ref.sha256)
                self.assertEqual(snap.history, history)
                self.assertEqual(snap.journal, journal)
                self.assertEqual(snap.payload["body_digest"], digest(snap.payload["body"]))
                self.assertEqual(snap.payload["closure_status"], "UNKNOWN")
                self.assertEqual(snap.payload["closure"]["closure_complete"], False)
                self.assertEqual(snap.payload["arm_manifest"]["F01"], "NOT_EVALUATED")
                self.assertEqual(snap.payload["validator_receipt"]["candidates_generated_at_creation"], 1)
                self.assertEqual(snap.payload["validator_receipt"]["candidate_budget"], 16)
                self.assertNotIn("ORACLE-REF", snap.payload["arm_manifest"])
                self.assertEqual(len(journal), 5)
                self.assertEqual(ref.size_bytes, Path(ref.path).stat().st_size)
                with self.assertRaisesRegex(ValueError, "INVALID"):
                    write_snapshot(ref.path, history, journal, decoded.body)

    def test_snapshot_requires_external_expected_sha_and_canonical_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, history, journal, decoded = create_snap(Path(tmp))
            with self.assertRaises(TypeError):
                load_snapshot(ref.path)
            with self.assertRaisesRegex(ValueError, "INVALID"):
                load_snapshot(Path(tmp) / "." / "snapshot.json",
                              expected_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "INVALID"):
                load_snapshot("snapshot.json", expected_sha256=ref.sha256)
            with self.assertRaisesRegex(ValueError, "INVALID"):
                load_snapshot(ref.path, expected_sha256="0" * 64)
            # Even a locally edited copy cannot impersonate the pinned original.
            Path(ref.path).chmod(0o600)
            Path(ref.path).write_bytes(Path(ref.path).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "INVALID"):
                load_snapshot(ref.path, expected_sha256=ref.sha256)

    def test_content_tamper_with_recomputed_file_hash_is_semantically_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, _, _, _ = create_snap(Path(tmp))
            original = json.loads(Path(ref.path).read_text(encoding="utf-8"))
            for label, edit in (
                ("policy", lambda p: p["policy"].update(route_order=["episodic_exact"])),
                ("closure", lambda p: p["closure"].update(status="COMPLETE")),
                ("receipt", lambda p: p["validator_receipt"].update(ast_nodes_static=999)),
                ("journal", lambda p: p["public_journal"].pop(3)),
                ("private", lambda p: p.update(private_labels=[0, 0, 0, 1])),
                ("body", lambda p: p["body"].update(op="EXEC")),
            ):
                with self.subTest(label=label):
                    data = json.loads(json.dumps(original))
                    edit(data["payload"])
                    data["payload_digest"] = digest(data["payload"])
                    raw = (canonical(data) + "\n").encode()
                    target = Path(tmp) / (label + ".json")
                    target.write_bytes(raw)
                    with self.assertRaises(ValueError):
                        load_snapshot(target, expected_sha256=sha256(raw).hexdigest())

    def test_public_journal_precommit_order_and_legal_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            history, journal = fixture()
            body = decode_public(history).body
            for label, change in (
                ("missing_precommit", lambda j: j.pop(3)),
                ("early_answer", lambda j: j[4].update(event_at=4)),
                ("wrong_legal", lambda j: j[3].update(legal_actions=[])),
                ("forged_digest", lambda j: j[3].update(legal_digest="f" * 64)),
                ("wrong_cost", lambda j: j[4].update(paid_cost=0)),
                ("wrong_point", lambda j: j[3].update(point=[1, 1, 1])),
            ):
                with self.subTest(label=label):
                    modified = json.loads(json.dumps(journal))
                    change(modified)
                    with self.assertRaisesRegex(ValueError, "INVALID"):
                        write_snapshot(Path(tmp) / (label + ".json"), history,
                                       tuple(modified), body)

    def test_body_must_be_decoder_or_meaning_preserving_sleep(self):
        with tempfile.TemporaryDirectory() as tmp:
            history, journal = fixture()
            with self.assertRaises(ValueError):
                write_snapshot(Path(tmp) / "wrong.json", history, journal, Node("0"))
            # Correct public history, but non-decoder equivalent form is forbidden.
            from packages.r2_m_eng.sleep_lite import sleep_lite
            body = decode_public(history).body
            normalized, receipt = sleep_lite(body, history)
            ref = write_snapshot(Path(tmp) / "sleep.json", history, journal, normalized)
            self.assertEqual(load_snapshot(ref.path, expected_sha256=ref.sha256)
                             .payload["body_digest"], digest(
                                 load_snapshot(ref.path, expected_sha256=ref.sha256).payload["body"]))


class MeterStage2Tests(unittest.TestCase):
    def test_short_circuit_never_counts_unvisited_branch(self):
        cases = (
            (Node("OR", (Node("1"), Node("NOT", (Node("x"),)))), (0,0,0), 1, (4, 2, 1)),
            (Node("AND", (Node("0"), Node("NOT", (Node("x"),)))), (0,0,0), 0, (4, 2, 1)),
            (Node("OR", (Node("0"), Node("NOT", (Node("x"),)))), (0,0,0), 1, (4, 4, 2)),
            (Node("NOT", (Node("x"),)), (1,0,0), 0, (2, 2, 1)),
            (Node("x"), (1,0,0), 1, (1, 1, 0)),
        )
        for tree, point, expected, counters in cases:
            with self.subTest(tree=tree):
                metered = measure_ast(tree, point)
                self.assertEqual(metered.prediction, expected)
                self.assertEqual((metered.counts.ast_nodes_static,
                                  metered.counts.node_visits_runtime,
                                  metered.counts.primitive_ops_runtime), counters)
                self.assertEqual(metered.prediction, interpret_public(tree, point))

    def test_zero_ast_route_and_no_heterogeneous_cost_sum(self):
        cost = cost_ledger(
            paid_inquiries=1, public_observations=4, decoder_invocations=0,
            candidates_generated=0, validator_invocations=1,
            h0_predicates_scanned=8, ast_counts=AstCounts(0, 0, 0),
            restore_bytes=100, stored_bytes=100, cpu_seconds=0.0,
            wall_seconds=0.0)
        self.assertEqual(cost["candidate_budget"], 16)
        self.assertEqual(cost["candidates_generated"], 0)
        self.assertEqual(cost["primitive_ops_runtime"], 0)
        self.assertNotIn("weighted_total", cost)
        with self.assertRaisesRegex(ValueError, "INVALID"):
            cost_ledger(paid_inquiries=1, public_observations=4,
                        decoder_invocations=0, candidates_generated=True,
                        validator_invocations=1, h0_predicates_scanned=8,
                        ast_counts=AstCounts(0, 0, 0))

    def test_all_sixteen_synthetic_bodies_meter_matches_independent_interpreter(self):
        for coefficients in product((0, 1), repeat=4):
            with tempfile.TemporaryDirectory() as tmp:
                _, _, _, decoded = create_snap(Path(tmp), tuple(coefficients))
                for bits in product((0, 1), repeat=3):
                    value = measure_ast(decoded.body, bits)
                    self.assertEqual(value.prediction, interpret_public(decoded.body, bits))
                    self.assertLessEqual(value.counts.node_visits_runtime,
                                         value.counts.ast_nodes_static)
                    self.assertLessEqual(value.counts.primitive_ops_runtime,
                                         value.counts.node_visits_runtime)


class DispatchStage2Tests(unittest.TestCase):
    def test_off_keeps_all_fallback_routes_and_runtime_decoder(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, _, _, _ = create_snap(Path(tmp))
            off = predict_fixed(ref.path, expected_sha256=ref.sha256,
                                point=(1, 1, 1), arm="F00")["trace"]["payload"]
            on = predict_fixed(ref.path, expected_sha256=ref.sha256,
                               point=(1, 1, 1), arm="F10")["trace"]["payload"]
            self.assertEqual(off["snapshot_sha256"], on["snapshot_sha256"])
            self.assertEqual(off["public_digest"], on["public_digest"])
            self.assertEqual(off["policy_digest"], on["policy_digest"])
            self.assertEqual(set(off["activity"]), {"learned_body", *ROUTES})
            self.assertTrue(off["activity"]["learned_body"]["available"])
            self.assertFalse(off["activity"]["learned_body"]["enabled"])
            self.assertEqual(off["route"], "runtime_affine_decoder")
            self.assertEqual(on["route"], "learned_body")
            self.assertEqual(off["prediction"], on["prediction"])
            self.assertEqual(off["cost"]["decoder_invocations"], 1)
            self.assertEqual(off["cost"]["candidates_generated"], 1)
            self.assertEqual(on["cost"]["decoder_invocations"], 0)
            self.assertEqual(on["cost"]["candidates_generated"], 0)
            self.assertEqual(on["cost"]["paid_inquiries"], off["cost"]["paid_inquiries"])
            self.assertEqual((off["closure_status"], off["m_gap"], off["m_use"]),
                             ("UNKNOWN", "UNKNOWN", "NOT_CERTIFIED"))
            self.assertTrue(all(v["available"] for k,v in off["activity"].items() if k in ROUTES))
            with self.assertRaisesRegex(ValueError, "INVALID"):
                predict_fixed(ref.path, expected_sha256=ref.sha256,
                              point=(1, 1, 1), arm="F11")

    def test_exact_and_h0_routes_are_not_artificially_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref, _, _, _ = create_snap(Path(tmp), (1, 0, 0, 0))
            exact = predict_fixed(ref.path, expected_sha256=ref.sha256,
                                  point=(0,0,0), arm="F00")["trace"]["payload"]
            h0 = predict_fixed(ref.path, expected_sha256=ref.sha256,
                               point=(1,1,1), arm="F00")["trace"]["payload"]
            self.assertEqual(exact["route"], "episodic_exact")
            self.assertEqual(h0["route"], "h0_consistent")
            self.assertEqual(exact["cost"]["primitive_ops_runtime"], 0)
            self.assertEqual(h0["cost"]["primitive_ops_runtime"], 0)
            self.assertEqual(exact["prediction"], 0)
            self.assertEqual(h0["prediction"], 1)

    def test_fresh_children_different_cwds_restore_exact_bytes_and_write_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ref, _, _, _ = create_snap(root)
            repo = Path(__file__).resolve().parents[1]
            outputs = []
            for arm, directory in (("F00", root / "child_off"), ("F10", root / "child_on")):
                directory.mkdir()
                target = root / (arm + "-trace.json")
                env = dict(os.environ)
                env["PYTHONPATH"] = str(repo) + os.pathsep + env.get("PYTHONPATH", "")
                args = [sys.executable, "-m", "packages.r2_m_eng.dispatch",
                        "--snapshot", ref.path, "--sha256", ref.sha256,
                        "--point", "111", "--arm", arm,
                        "--trace-output", str(target)]
                proc = subprocess.run(args, cwd=directory, env=env,
                                      text=True, capture_output=True, timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                receipt = json.loads(proc.stdout)
                self.assertEqual(receipt["trace_file"]["absolute_path"], str(target.resolve()))
                record = json.loads(target.read_text())
                self.assertEqual(record["trace_digest"], receipt["trace_digest"])
                outputs.append(record["trace"]["payload"])
                again = subprocess.run(args, cwd=directory, env=env,
                                       text=True, capture_output=True, timeout=30)
                self.assertNotEqual(again.returncode, 0)
                self.assertIn("exclusive creation failed", again.stderr)
            self.assertEqual(outputs[0]["snapshot_path_absolute"], ref.path)
            self.assertEqual(outputs[1]["snapshot_path_absolute"], ref.path)
            self.assertEqual(outputs[0]["snapshot_sha256"], ref.sha256)
            self.assertEqual(outputs[1]["snapshot_sha256"], ref.sha256)
            self.assertEqual(outputs[0]["prediction"], outputs[1]["prediction"])


if __name__ == "__main__":
    unittest.main()
