"""EXP-0003A PR4 immutable freeze preflight CLI. No DEV/FINAL scorer."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from .freeze import preflight_record, verify_frozen


def main() -> None:
    parser = argparse.ArgumentParser(description="EXP-0003A source/data/policy lock")
    parser.add_argument("--mode", choices=("preflight", "check-freeze"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    record = preflight_record() if args.mode == "preflight" else verify_frozen()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("Refusing to overwrite preflight artifact")
    raw = (json.dumps(record, sort_keys=True, ensure_ascii=False,
                      indent=2, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
    print(json.dumps({
        "mode": args.mode, "experiment_id": record["experiment_id"],
        "freeze_payload_sha256": record["freeze_payload_sha256"],
        "file_sha256": sha256(raw).hexdigest(),
        "split_sha256": record["split_data"]["split_sha256"],
        "all_task_count": record["split_data"]["all_task_count"],
        "all_seed_count": record["split_data"]["all_seed_count"],
        "source_git_blob_manifest_sha256":
            record["sources"]["git_blob_manifest_sha256"],
        "policy_snapshot_sha256": record["policy"]["snapshot_sha256"],
        "dev_or_final_scored": record["split_data"]["dev_or_final_scored"],
        "holdout_scoring_permitted": record["holdout_scoring_permitted"],
    }, sort_keys=True))
    # Hashes and public opaque IDs only. Emitting this entire canonical JSON
    # enables exact record pinning in a subsequent commit without disclosing
    # non-public third examples or creating DEV/FINAL evaluation output.
    if args.mode == "preflight":
        print("FREEZE_MANIFEST_JSON:" + json.dumps(
            record, separators=(",", ":"), sort_keys=True,
            ensure_ascii=False, allow_nan=False
        ))


if __name__ == "__main__":
    main()
