"""Safe EXP-0003A TRAIN engineering entrypoint; no other phase is executable."""
from __future__ import annotations

import argparse
from hashlib import sha256
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
    raw = (json.dumps(
        report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
    ) + "\n").encode("utf-8")
    # Fail closed if rerun tries to overwrite already retained evidence.
    with output.open("xb") as stream:
        stream.write(raw)
    episodes_path = output.with_name(output.stem + ".episodes.jsonl")
    episode_lines = "".join(json.dumps(
        episode, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ) + "\n" for episode in report["episodes"]).encode("utf-8")
    with episodes_path.open("xb") as stream:
        stream.write(episode_lines)
    print(json.dumps({
        "phase": "TRAIN", "wake_status": report["wake_status"],
        "proposals": len(report["proposals"]),
        "functional_gate": report["functional_gate"],
        "output": str(output), "report_sha256": sha256(raw).hexdigest(),
        "episodes_jsonl": str(episodes_path),
        "episodes_jsonl_sha256": sha256(episode_lines).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
