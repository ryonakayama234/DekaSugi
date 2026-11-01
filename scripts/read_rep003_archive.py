"""Read-only lossless decoder for the disclosed REP003 raw JSON archive.

Never loads any private/old DEV/FINAL dataset or calls a scorer.
"""
from __future__ import annotations
import argparse
import base64
import json
import zlib
from pathlib import Path
from packages.rep003 import digest, ARMS, STRATA, BUDGETS


def decode_archive(path):
    raw = Path(path).read_text(encoding="utf8").strip()
    if not raw or not all(x in
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        for x in raw):
        raise ValueError("noncanonical archive text")
    obj = json.loads(zlib.decompress(base64.b64decode(raw, validate=True)))
    if type(obj) is not dict or obj.get("record_count") != 48*len(ARMS)*len(BUDGETS):
        raise ValueError("unexpected disclosed archive dimension")
    if len(obj.get("rows", [])) != obj["record_count"]:
        raise ValueError("lost raw rows")
    if digest(obj["rows"]) != obj["records_digest"]:
        raise ValueError("raw row integrity violation")
    if set(obj["summary"]) != set(STRATA) or obj.get("status") != (
        "DISCLOSED_REDUCED_GRAMMAR_ENGINEERING_ONLY"
    ):
        raise ValueError("archive source class mismatch")
    return obj


def main():
    p=argparse.ArgumentParser(description="Decode synthetic-only REP003 raw archive")
    p.add_argument("--archive", required=True)
    p.add_argument("--output")
    a=p.parse_args()
    report=decode_archive(a.archive)
    if a.output:
        dest=Path(a.output)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"status":"VERIFIED_DISCLOSED_ARCHIVE",
        "record_count":report["record_count"],
        "records_digest":report["records_digest"],
        "strata":report["summary"],
        "output":a.output},sort_keys=True))


if __name__=="__main__":
    main()
