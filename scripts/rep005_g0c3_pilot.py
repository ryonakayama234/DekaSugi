"""Disclosed, synthetic-only G0C3 source pilot. Never imports a learner."""
import argparse
import json
import platform
from hashlib import sha256
from pathlib import Path
from packages.rep005_g0c3 import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--draws", type=int, default=48)
    parser.add_argument("--proof-seconds", type=float, default=180)
    parser.add_argument("--panel-seconds", type=float, default=30)
    args = parser.parse_args()
    result = run(args.draws, proof_seconds=args.proof_seconds, panel_seconds=args.panel_seconds)
    result["runtime"]["python"] = platform.python_version()
    result["runtime"]["platform"] = platform.platform()
    data = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as f:
        f.write(data)
    print(json.dumps(dict(artifact=str(target), sha256=sha256(data).hexdigest(),
                          roots=result["root_attempts"], valid=result["valid_roots"],
                          orbit_status=result["orbit"]["status"],
                          panels_positive=result["inquiry"]["positive"],
                          panels_unknown=result["inquiry"]["not_certified"],
                          learning="NOT_RUN"), sort_keys=True))


if __name__ == "__main__":
    main()
