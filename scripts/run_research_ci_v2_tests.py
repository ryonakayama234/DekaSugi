"""Run only the explicitly reviewed CI-SAFE-V2 synthetic test allowlist.

Never use unittest's general discover on the whole tests/ tree here:
legacy tests can regenerate historically frozen DEV/FINAL data.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
# Direct `python scripts/...` execution otherwise hides the root package
# path; only the explicit synthetic allowlist is imported by unittest.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REQUIRED = (
    "test_research_ci_v2.py",
    "test_docs_validation.py",
    "test_metro0001_calibration.py",
    "test_opportunity_fixture.py",
    "test_opportunity_private_copy.py",
)
# A future stacked OPPORTUNITY-002 synthetic fixture becomes eligible once
# merged; absence is not treated as evidence that the fixture passed.
OPTIONAL = (
    "test_opportunity2_boundary.py", "test_opportunity2_audit.py",
    "test_active_learning_synthetic.py", "test_active_learning_integrity.py",
    "test_active_learning_history_integrity.py",
    "test_active_learning_catalog_integrity.py",
    "test_active_learning_lookup_canonicalization.py",
    "test_active_learning_container_boundary.py",
    # ACTIVE-001 Gate F: invented public-context-only census, no scorer/Oracle.
    "test_active_feasibility.py",
    # ACTIVE-001 P2: invented-only CPU instrumentation and dry-run counts.
    "test_active_cost_preflight.py",
)


def run() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in REQUIRED:
        path = TESTS / name
        if not path.is_file() or path.is_symlink():
            print("CI-SAFE-V2: required fixture test missing")
            return 1
        suite.addTests(loader.discover(str(TESTS), pattern=name))
    for name in OPTIONAL:
        path = TESTS / name
        if path.is_symlink():
            print("CI-SAFE-V2: optional fixture symlink denied")
            return 1
        if path.is_file():
            suite.addTests(loader.discover(str(TESTS), pattern=name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() and result.testsRun > 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())
