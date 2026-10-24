"""Validate DekaSugi's navigable Markdown research library.

Only Python standard library required. Use as: python scripts/check_docs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "AGENTS.md",
    "docs/INDEX.md",
    "docs/vision/mission.md",
    "docs/architecture/system.md",
    "docs/architecture/contracts.md",
    "docs/process/workflow.md",
    "docs/process/github.md",
    "docs/specs/EXP-0001.md",
    "experiments/EXP-0001/plan.md",
    "experiments/EXP-0001/runs/README.md",
    "docs/specs/EXP-0002.md",
    "experiments/EXP-0002/plan.md",
    "experiments/EXP-0002/runs/README.md",
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def validate_link(source: Path, destination: str, root: Path) -> str | None:
    """Return an error if an internal markdown link is broken or escapes repo."""
    destination = destination.strip().split("#", 1)[0].split("?", 1)[0]
    if not destination or destination.startswith(("http:", "https:", "mailto:", "data:")):
        return None
    destination = unquote(destination)
    target = (source.parent / destination).resolve()
    if not target.is_relative_to(root.resolve()):
        return f"{source.relative_to(root)}: link escapes repository: {destination}"
    if not target.exists():
        return f"{source.relative_to(root)}: missing link target: {destination}"
    return None


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    for required in REQUIRED:
        if not (root / required).is_file():
            errors.append(f"missing required file: {required}")

    for md in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv"} for part in md.parts):
            continue
        text = md.read_text(encoding="utf-8")
        if md.relative_to(root).parts[0] in {"docs", "experiments", "packages"}:
            for field in ("id:", "status:", "updated:", "tags:"):
                if not any(line.startswith(field) for line in text.splitlines()[:12]):
                    errors.append(f"{md.relative_to(root)}: missing metadata {field}")
        for dest in MARKDOWN_LINK.findall(text):
            err = validate_link(md, dest, root)
            if err:
                errors.append(err)

    plans = sorted((root / "experiments").glob("EXP-*/plan.md"))
    if not plans:
        errors.append("experiments: no EXP-*/plan.md found")
    for plan in plans:
        body = plan.read_text(encoding="utf-8")
        for section in ("## Hypothesis", "## Metrics", "## Acceptance"):
            if section not in body:
                errors.append(f"{plan.relative_to(root)}: missing {section}")
    return errors


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("Documentation validation FAILED:")
        for err in errors:
            print(f" - {err}")
        return 1
    md_count = len(list(ROOT.rglob("*.md")))
    print(f"Documentation validation PASSED: {md_count} markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
