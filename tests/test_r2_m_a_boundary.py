"""G3-1 synthetic-only public boundary, import hook, and negative tests.

No real source, no G4 audit, no fresh scientific child, and no scoring.
"""
from __future__ import annotations

from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from packages.r2_m_a.import_guard import (
    ChildMetaPathGuard, audit_static_child_graph, forbidden,
)
from packages.r2_m_a.public_pipeline import (
    SyntheticPrecommitReceipt, prepare_synthetic_snapshot,
)
from packages.r2_m_eng.decoder import decode_public
from packages.r2_m_eng.records import PUBLIC_POINTS
from packages.r2_m_eng.snapshot import load_snapshot
from packages.r2_m_eng.source_gateway import PublicGateway, SyntheticPrivateSource


def artificial_gateway(coefficients=(1, 0, 1, 0), *, journal_path=None):
    return PublicGateway(SyntheticPrivateSource(coefficients), opened_at=5,
                         expires_at=20, journal_path=journal_path)


def fixture_barrier(intent):
    return SyntheticPrecommitReceipt(intent.commitment)


class G31PublicBoundaryTests(unittest.TestCase):
    def test_all_16_synthetic_laws_have_3_then_4_public_and_one_snapshot(self):
        for coefficients in product((0, 1), repeat=4):
            with self.subTest(coefficients=coefficients), tempfile.TemporaryDirectory() as tmp:
                journal = Path(tmp) / "public.jsonl"
                gateway = artificial_gateway(tuple(coefficients), journal_path=journal)
                observed_at_barrier = []
                def before_answer(intent):
                    events = gateway.public_journal()
                    self.assertEqual([v["event"] for v in events],
                                     ["initial", "initial", "initial", "precommit"])
                    self.assertEqual([v["event"] for v in
                                      map(json.loads, journal.read_text().splitlines())],
                                     ["initial", "initial", "initial", "precommit"])
                    self.assertEqual(len(gateway.public_state(now=6)["observations"]), 3)
                    self.assertEqual(intent.point, (0, 0, 1))
                    self.assertEqual(intent.paid_budget_remaining, 1)
                    observed_at_barrier.append(intent.history_digest)
                    return fixture_barrier(intent)
                ref = prepare_synthetic_snapshot(
                    gateway, snapshot_path=Path(tmp) / "snapshot.json",
                    precommit_at=6, answer_at=7, barrier=before_answer,
                    engineering_only=True)
                self.assertEqual(len(observed_at_barrier), 1)
                loaded = load_snapshot(ref.path, expected_sha256=ref.sha256)
                self.assertEqual(len(loaded.history), 4)
                self.assertEqual(decoded := decode_public(loaded.history).coefficients,
                                 tuple(coefficients))
                self.assertEqual(loaded.payload["closure_status"], "UNKNOWN")
                self.assertEqual(loaded.payload["arm_manifest"]["F01"], "NOT_EVALUATED")
                self.assertEqual(len(loaded.journal), 5)
                self.assertEqual([e["event"] for e in loaded.journal][-2:],
                                 ["precommit", "answer"])
                self.assertTrue(ref.path.startswith(str(Path(tmp).resolve())))
                self.assertFalse(any(k in loaded.payload for k in (
                    "source_law", "true_use_labels", "seed", "score_outcome")))
                with self.assertRaisesRegex(ValueError, "INVALID"):
                    prepare_synthetic_snapshot(
                        gateway, snapshot_path=ref.path,
                        precommit_at=8, answer_at=9, barrier=fixture_barrier,
                        engineering_only=True)

    def test_failed_missing_or_forged_barrier_never_calls_paid_query(self):
        for barrier in (
            lambda intent: None,
            lambda intent: SyntheticPrecommitReceipt("0"*64),
            lambda intent: SyntheticPrecommitReceipt(intent.commitment, False),
        ):
            with self.subTest(barrier=barrier), tempfile.TemporaryDirectory() as tmp:
                gateway = artificial_gateway()
                with patch.object(PublicGateway, "answer",
                                  side_effect=AssertionError("Q MUST NOT execute")):
                    with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
                        prepare_synthetic_snapshot(
                            gateway, snapshot_path=Path(tmp) / "snapshot.json",
                            precommit_at=6, answer_at=7, barrier=barrier,
                            engineering_only=True)
                self.assertEqual([v["event"] for v in gateway.public_journal()][-1],
                                 "precommit")
                self.assertFalse((Path(tmp) / "snapshot.json").exists())

    def test_barrier_exception_stops_without_answer(self):
        gateway = artificial_gateway()
        def remote_unavailable(_intent):
            raise ConnectionError("simulated remote unavailability")
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(PublicGateway, "answer",
                              side_effect=AssertionError("Q MUST NOT execute")):
                with self.assertRaisesRegex(ConnectionError, "simulated"):
                    prepare_synthetic_snapshot(
                        gateway, snapshot_path=Path(tmp) / "snapshot.json",
                        precommit_at=6, answer_at=7, barrier=remote_unavailable,
                        engineering_only=True)
            self.assertFalse((Path(tmp) / "snapshot.json").exists())
            self.assertEqual(len(gateway.public_journal()), 4)

    def test_no_nonfixture_execution_or_expired_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            gateway = artificial_gateway()
            with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
                prepare_synthetic_snapshot(gateway,
                    snapshot_path=Path(tmp)/"snapshot.json",
                    precommit_at=6, answer_at=7, barrier=fixture_barrier,
                    engineering_only=False)
            self.assertEqual(len(gateway.public_journal()), 3)
            with self.assertRaisesRegex(ValueError, "RUN_BLOCK"):
                prepare_synthetic_snapshot(gateway,
                    snapshot_path=Path(tmp)/"snapshot.json",
                    precommit_at=21, answer_at=22, barrier=fixture_barrier,
                    engineering_only=True)
            self.assertEqual(len(gateway.public_journal()), 3)

    def test_synthetic_snapshot_cannot_be_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "snapshot.json"
            existing.write_text("sentinel", encoding="utf-8")
            gateway = artificial_gateway()
            with self.assertRaisesRegex(ValueError, "INVALID"):
                prepare_synthetic_snapshot(
                    gateway, snapshot_path=existing,
                    precommit_at=6, answer_at=7, barrier=fixture_barrier,
                    engineering_only=True)
            self.assertEqual(existing.read_text(encoding="utf-8"), "sentinel")


class G31ImportGuardTests(unittest.TestCase):
    def test_static_relative_transitive_and_dynamic_literal_graph(self):
        sources = {
            "packages.r2_m_a.child": "from . import helper\n",
            "packages.r2_m_a.helper": "from packages.r2_m_eng import records\n",
        }
        self.assertEqual(audit_static_child_graph(
            sources, entrypoints=("packages.r2_m_a.child",)),
            frozenset(sources))
        for src in (
            "from packages.r2_m_eng import source_gateway\n",
            "import packages.r2_m_a.public_pipeline\n",
            "from . import public_pipeline\n",
            "from . import evaluator_gate\n",
        ):
            sources["packages.r2_m_a.helper"] = src
            with self.subTest(src=src), self.assertRaisesRegex(ImportError, "INVALID"):
                audit_static_child_graph(
                    sources, entrypoints=("packages.r2_m_a.child",))
        with self.assertRaisesRegex(ValueError, "INVALID"):
            audit_static_child_graph(sources, entrypoints=("missing",))
        self.assertTrue(forbidden("packages.r2_m_a.evaluator_gate.unseen"))
        self.assertFalse(forbidden("packages.r2_m_eng.snapshot"))

    def test_meta_path_catches_lazy_import_not_only_sys_modules_snapshot(self):
        # MetaPathFinder runs when a new module is imported later within a function.
        # Do not install the irreversible audit hook in this test process.
        import importlib
        target = "packages.r2_m_a.evaluator_gate.unseen"
        guard = ChildMetaPathGuard()
        with self.assertRaisesRegex(ImportError, "INVALID"):
            guard.find_spec(target)
        # Full runtime test executes in a separate synthetic-only Python process.
        code = ("import importlib\n"
                "from packages.r2_m_a.import_guard import install_child_import_guard\n"
                "install_child_import_guard()\n"
                "def delayed():\n"
                "    return importlib.import_module('packages.r2_m_eng.source_gateway')\n"
                "try:\n"
                "    delayed()\n"
                "except ImportError as e:\n"
                "    assert 'INVALID' in str(e)\n"
                "else:\n"
                "    raise AssertionError('lazy forbidden import was allowed')\n")
        repo = Path(__file__).resolve().parents[1]
        # Explicitly an isolated import-hook smoke test, not a scoring child.
        result = subprocess.run([sys.executable, "-c", code], cwd=repo,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))


if __name__ == "__main__":
    unittest.main()
