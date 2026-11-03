"""Run G0B finite synthetic engineering census with exclusive output creation."""
import argparse
from pathlib import Path
from .analysis import build_report, canonical_json, report_digest


def main():
    p=argparse.ArgumentParser(description="G0B finite source engineering census; no learner/F0")
    p.add_argument("--output", required=True, help="New output path; exclusive creation")
    ns=p.parse_args()
    if ns.output.startswith("/dev/"):
        p.error("device outputs are not permitted")
    report=build_report()
    out=Path(ns.output)
    # no overwrite of raw evidence
    with out.open("x", encoding="utf-8") as f:
        f.write(canonical_json(report))
    print("source:", report["source_version"])
    for part in ("CAL64_DISCLOSED", "EXT448_NEW"):
        d=report[part]
        print(part, "worlds", d["world_count"], "positive", d["world_oracle_positive"],
              "public delta", d["public_oracle"]["gain_numerator"], "/",d["public_oracle"]["denominator"])
    print("sha256:",report_digest(report))


if __name__ == "__main__":
    main()
