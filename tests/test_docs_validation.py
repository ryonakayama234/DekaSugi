"""Focused unit tests for docs checker; uses no external dependencies."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_docs import validate_link  # noqa: E402


class LinkValidationTests(unittest.TestCase):
    def test_valid_relative_link(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "docs").mkdir()
            (root / "docs" / "target.md").write_text("# target\n")
            source = root / "docs" / "index.md"
            self.assertIsNone(validate_link(source, "target.md#heading", root))

    def test_missing_link(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "docs").mkdir()
            error = validate_link(root / "docs" / "index.md", "missing.md", root)
            self.assertIsNotNone(error)
            self.assertIn("missing link target", error)

    def test_escape_root(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "docs").mkdir()
            error = validate_link(root / "docs" / "index.md", "../../escape.md", root)
            self.assertIsNotNone(error)
            self.assertIn("escapes repository", error)

    def test_external_reference(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertIsNone(validate_link(root / "index.md", "https://example.org", root))


if __name__ == "__main__":
    unittest.main()
