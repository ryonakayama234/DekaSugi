"""Fresh-process, read-only Snapshot USE for R1-ENG diagnostics."""
from __future__ import annotations

import argparse
import json
import os

from .core import check_point, dispatch, load_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--mode", choices=("on", "off"), required=True)
    parser.add_argument("--x", type=int, required=True)
    parser.add_argument("--z", type=int, required=True)
    args = parser.parse_args()
    point = check_point((args.x, args.z))
    # Source world / evaluator is not imported, loaded or reachable here.
    snap = load_snapshot(args.snapshot)
    decision = dispatch(snap, point, body_on=args.mode == "on")
    print(json.dumps({"fresh_process_id": os.getpid(), **decision},
                     sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
