"""Training and preflight only. Intentionally no FINAL invocation path."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from packages.kernel import preflight, train_report


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-0002B preregistered TRAIN-only runner")
    parser.add_argument("--mode", choices=("preflight", "train"), default="preflight")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = train_report() if args.mode == "train" else preflight()
    content = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
