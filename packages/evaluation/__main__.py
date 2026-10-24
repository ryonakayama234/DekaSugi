"""Reproduce EXP-0002 on CPU: python -m packages.evaluation --output FILE."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import run_experiment


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-0002 experiment")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_experiment()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0 if report["status"] == "functional_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
