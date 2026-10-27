"""Explicit DEV64-only entrypoint. Never run from pull_request CI."""
from __future__ import annotations

import argparse
from pathlib import Path

from . import require_reviewed_main_push, run_dev, write_once


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-0003A frozen DEV64 engineering evaluator")
    parser.add_argument("--mode", required=True, choices=("dev",))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    require_reviewed_main_push()
    public_path = Path(args.output)
    if public_path.suffix != ".json":
        raise ValueError("--output must end in .json")
    private_path = public_path.with_name(public_path.stem + ".evaluator-private.json")
    if public_path.exists() or private_path.exists():
        raise FileExistsError("Never overwrite experimental evidence")
    public, private = run_dev()
    public_digest = write_once(public_path, public)
    private_digest = write_once(private_path, private)
    print("DEV64 engineering evidence written; NOT FINAL/confirmed/skill promotion")
    print("public_sha256=" + public_digest)
    print("private_sha256=" + private_digest)


if __name__ == "__main__":
    main()
