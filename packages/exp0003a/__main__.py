"""Safe EXP-0003A TRAIN engineering entrypoint; no other phase is executable."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import train_report


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-0003A TRAIN-only evidence")
    parser.add_argument("--mode", required=True, choices=("train",))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = train_report()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(
        report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
    ) + "\n", encoding="utf-8")
    print(json.dumps({
        "phase": "TRAIN", "wake_status": report["wake_status"],
        "proposals": len(report["proposals"]),
        "functional_gate": report["functional_gate"],
        "output": str(output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
