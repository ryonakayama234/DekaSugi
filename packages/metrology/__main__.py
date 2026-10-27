"""CLI for synthetic METRO-0001 CAL-01 fixture calibration (no DEV/FINAL access)."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from time import perf_counter_ns, process_time_ns

from . import calibrate, digest, fixture_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only synthetic calibration")
    parser.add_argument("--mode", choices=("calibrate",), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixtures-output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.fixtures_output.resolve():
        parser.error("summary and raw source paths must differ")
    if args.output.exists() or args.fixtures_output.exists():
        parser.error("immutable output path already exists")

    cpu_start, wall_start = process_time_ns(), perf_counter_ns()
    raw_fixtures = fixture_manifest()
    report = calibrate()
    cpu_ns = process_time_ns() - cpu_start
    wall_ns = perf_counter_ns() - wall_start

    # Timings and environment are observations, not part of the fixed
    # discrete golden summary hash.
    report["calibration_execution"] = {
        "cpu_process_ns": cpu_ns,
        "wall_elapsed_ns": wall_ns,
        "scope": "fixture_manifest_plus_calibrate_excludes_io",
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    report["source_fixture_manifest_sha256"] = digest(raw_fixtures)
    raw_payload = json.dumps(raw_fixtures, ensure_ascii=False, sort_keys=True,
                             indent=2, allow_nan=False) + "\n"
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True,
                         indent=2, allow_nan=False) + "\n"
    # Two independent exclusive-create artifacts; never overwrite.
    with args.fixtures_output.open("x", encoding="utf-8") as source:
        source.write(raw_payload)
    with args.output.open("x", encoding="utf-8") as result:
        result.write(payload)
    print(payload, end="")
    return 0 if report["status"] == "engineering_fixture_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
