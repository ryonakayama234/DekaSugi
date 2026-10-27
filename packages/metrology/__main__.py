"""CLI for synthetic METRO-0001 CAL-01 fixture calibration (no DEV/FINAL access)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import calibrate


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only synthetic calibration")
    parser.add_argument("--mode", choices=("calibrate",), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = calibrate()
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True,
                         indent=2, allow_nan=False) + "\n"
    # Exclusive creation: never overwrite immutable experiment evidence.
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(payload)
    print(payload, end="")
    return 0 if report["status"] == "engineering_fixture_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
