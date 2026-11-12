#!/usr/bin/env python3
"""Pure source index coverage evidence; NEVER invokes a K0 world search."""
import argparse
import json
from pathlib import Path
from world_cal.k0_coverage import source_index_certificate

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output")
    args=p.parse_args()
    result=source_index_certificate(verify_generator_yields=True)
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    print(payload)
    if args.output:
        Path(args.output).write_text(payload,encoding="utf-8")
