"""PR3 engineering only: never expose EXP-0003A DEV/FINAL activation."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from .pr3 import run_train_dream


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-0003A PR3 TRAIN/DREAM fixture")
    parser.add_argument("--mode", required=True, choices=("train-dream",))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report, private = run_train_dream()
    output = Path(args.output)
    private_path = output.with_name(output.stem + ".evaluator-private.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or private_path.exists():
        raise FileExistsError("Refusing to overwrite immutable PR3 evidence")
    def encode(value: object) -> bytes:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                           indent=2, allow_nan=False) + "\n").encode("utf-8")
    public_bytes, private_bytes = encode(report), encode(private)
    with output.open("xb") as stream:
        stream.write(public_bytes)
    with private_path.open("xb") as stream:
        stream.write(private_bytes)
    print(json.dumps({
        "phase": "TRAIN_DREAM_ENGINEERING",
        "pool": report["dream_pool_count"],
        "selected_per_arm": report["dream_selected_per_arm"],
        "wake_positive_count": report["wake_positive_count"],
        "snapshot_hashes": report["snapshot_hashes"],
        "report_sha256": sha256(public_bytes).hexdigest(),
        "evaluator_private_sha256": sha256(private_bytes).hexdigest(),
        "public_output": str(output),
        "private_output": str(private_path),
        "dev_or_final_evaluated": report["dev_or_final_evaluated"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
