"""Stage 3 synthetic-only integrated fixture and source/runner isolation checks."""
from __future__ import annotations

import ast
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from packages.r2_m_eng.closure import validate_closure_audit
from packages.r2_m_eng.controls import CONTROL_ARMS, CONTROL_DIGEST
from packages.r2_m_eng.records import PRIVATE_INPUTS, canonical, digest
from packages.r2_m_eng.runner import RUN_ARMS, run_synthetic
from packages.r2_m_eng.snapshot import load_snapshot


class Stage3FixtureTests(unittest.TestCase):
    def test_seven_fresh_arms_same_pinned_snapshot_and_no_private_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "stage3"
            result = run_synthetic(root, coefficients=(1, 0, 1, 1),
                                   point=(1, 1, 1))
            self.assertEqual(set(result["arms"]), set(RUN_ARMS))
            self.assertEqual(len(result["arms"]), 7)
            self.assertTrue(result["engineering_only"])
            self.assertEqual(result["m_use"], "NOT_CERTIFIED")
            self.assertEqual(result["m_gap"], "UNKNOWN")
            self.assertEqual(result["F01"], "NOT_EVALUATED")
            self.assertEqual(result["F11"], "NOT_EVALUATED")
            self.assertEqual(result["scientific_scoring"], "NOT_AUTHORIZED")
            self.assertEqual(result["oracle_ref"], "EVALUATOR_ONLY_NOT_EXECUTED")
            self.assertTrue(Path(result["snapshot_path_absolute"]).is_absolute())
            self.assertEqual(result["control_manifest_digest"], CONTROL_DIGEST)
            snap = load_snapshot(result["snapshot_path_absolute"],
                                 expected_sha256=result["snapshot_sha256"])
            self.assertEqual([e["event"] for e in snap.journal],
                             ["initial", "initial", "initial", "precommit", "answer"])
            self.assertEqual(snap.payload["closure_status"], "UNKNOWN")
            record = json.loads((root / "closure.json").read_text())
            validate_closure_audit(result["snapshot_path_absolute"],
                                   expected_sha256=result["snapshot_sha256"],
                                   record=record)
            self.assertEqual(result["closure_file"]["sha256"],
                             sha256((root / "closure.json").read_bytes()).hexdigest())
            traces = {}
            for arm in RUN_ARMS:
                path = Path(result["arms"][arm]["absolute_path"])
                self.assertTrue(path.is_absolute())
                self.assertEqual(path.parent, root / "traces")
                self.assertEqual(sha256(path.read_bytes()).hexdigest(),
                                 result["arms"][arm]["sha256"])
                record = json.loads(path.read_text())
                self.assertEqual(record["trace_digest"], digest(record["trace"]))
                payload = record["trace"]["payload"]
                self.assertEqual(payload["arm"], arm)
                self.assertEqual(payload["snapshot_sha256"], result["snapshot_sha256"])
                self.assertEqual(payload["snapshot_path_absolute"],
                                 result["snapshot_path_absolute"])
                self.assertEqual(payload["closure_status"], "UNKNOWN")
                self.assertEqual(payload["m_gap"], "UNKNOWN")
                self.assertEqual(payload["m_use"], "NOT_CERTIFIED")
                self.assertEqual(payload["status"], "ENGINEERING_ONLY")
                self.assertEqual(payload["point"], [1, 1, 1])
                self.assertEqual(payload["cost"]["paid_inquiries"], 1)
                self.assertEqual(payload["cost"]["public_observations"], 4)
                self.assertIn("ast_nodes_static", payload["cost"])
                self.assertIn("node_visits_runtime", payload["cost"])
                self.assertIn("primitive_ops_runtime", payload["cost"])
                if arm in CONTROL_ARMS:
                    self.assertEqual(payload["control_manifest_digest"], CONTROL_DIGEST)
                traces[arm] = payload
            # In this existing legal inventory OFF can decode at runtime.
            self.assertEqual(traces["F00"]["route"], "runtime_affine_decoder")
            self.assertEqual(traces["F10"]["route"], "learned_body")
            self.assertEqual(traces["F00"]["prediction"], traces["F10"]["prediction"])
            self.assertEqual(traces["STATIC-H+"]["prediction"],
                             traces["FIXED-MACRO"]["prediction"])
            self.assertEqual(traces["STATIC-H+"]["prediction"],
                             traces["F10"]["prediction"])
            self.assertEqual(traces["F00"]["policy_digest"],
                             traces["F10"]["policy_digest"])
            self.assertEqual(traces["F00"]["public_digest"],
                             traces["F10"]["public_digest"])
            # No fixture law or hidden answer is written anywhere as a field.
            for path in root.rglob("*.json"):
                raw = path.read_text(encoding="utf-8")
                for forbidden in ('"private_labels"', '"source_law"', '"seed"',
                                  '"score_outcome"', '"score_receipt"',
                                  '"oracle_answer"', '"target"'):
                    self.assertNotIn(forbidden, raw)
            self.assertNotIn("coefficients", json.dumps(result))

    def test_duplicate_output_directory_is_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "fixture"
            run_synthetic(root, coefficients=(0, 0, 0, 0), point=(0, 0, 0))
            prior = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
                     for path in root.rglob("*.json")}
            with self.assertRaisesRegex(ValueError, "INVALID"):
                run_synthetic(root, coefficients=(1, 1, 1, 1), point=(1, 1, 1))
            after = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
                     for path in root.rglob("*.json")}
            self.assertEqual(prior, after)

    def test_reject_non_fixture_arguments_and_no_science_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "INVALID"):
                run_synthetic(root / "bad", coefficients=(0, 0, 1, True),
                              point=(1, 0, 1))
            with self.assertRaisesRegex(ValueError, "INVALID"):
                run_synthetic(root / "bad", coefficients=(0, 0, 0, 0),
                              point=(1, 2, 1))
            process = subprocess.run(
                [sys.executable, "-m", "packages.r2_m_eng.runner",
                 "--output-dir", str(root / "unsupported"),
                 "--synthetic-affine", "1111", "--point", "111",
                 "--score", "private"],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=30,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("unrecognized arguments", process.stderr)
            self.assertFalse((root / "unsupported").exists())

    def test_learner_side_stage3_modules_do_not_import_evaluator_gateway(self):
        directory = Path(__file__).resolve().parents[1] / "packages" / "r2_m_eng"
        for filename in ("controls.py", "closure.py"):
            code = (directory / filename).read_text(encoding="utf-8")
            syntax = ast.parse(code)
            imports = []
            for entry in ast.walk(syntax):
                if isinstance(entry, ast.Import):
                    imports.extend(alias.name for alias in entry.names)
                if isinstance(entry, ast.ImportFrom):
                    imports.append(entry.module or "")
                    imports.extend(alias.name for alias in entry.names)
            for name in imports:
                self.assertNotIn("source_gateway", name)
                self.assertNotIn("private_source", name)
                self.assertNotIn("evaluator", name)
            self.assertNotIn("SyntheticPrivateSource", code)
        runner_code = (directory / "runner.py").read_text(encoding="utf-8")
        self.assertIn("from .source_gateway import", runner_code)
        self.assertNotIn("ScoreReceipt/v2", runner_code)
        self.assertNotIn("score_private", runner_code)


if __name__ == "__main__":
    unittest.main()
