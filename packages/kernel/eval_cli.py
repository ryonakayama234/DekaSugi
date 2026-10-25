"""Gated experimental evaluation CLI; never invoked on pull_request CI."""
import argparse
import json
from pathlib import Path
from packages.kernel.evaluation import run_evaluation

def main():
    parser = argparse.ArgumentParser(description="Frozen EXP-0002B evaluation")
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--freeze", type=Path, default=Path("experiments/EXP-0002B/freeze-v2.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_evaluation(args.phase, freeze_path=args.freeze)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"EXP-0002B {args.phase.upper()}: "
          f"tasks={len(result['tasks'])} "
          f"numeric_status={result['report']['numeric_status']}")


if __name__ == "__main__":
    main()
