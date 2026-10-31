"""F0-D ciphertext-only local receipt preflight for an external Google Drive vault.

Never generates real seeds, opens decryption keys, decrypts GPG, reads target
truth tables, communicates with Google Drive, or invokes official scorers.
A filename ending in .gpg DOES NOT prove that contents are encrypted.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat

SCHEMA="coev001-ciphertext-receipt/1"
STATUS="CIPHERTEXT_HASH_ONLY_UNATTESTED"
MAX_BYTES=128*1024*1024
ALLOWED_KINDS=("sealed_source","oracle_transcript","aggregate_only")
SHA_PATTERN=re.compile(r"^[0-9a-f]{40}$")
HASH_PATTERN=re.compile(r"^[0-9a-f]{64}$")

def _check_method(method_commit: str) -> None:
    if type(method_commit) is not str or not SHA_PATTERN.fullmatch(method_commit):
        raise ValueError("Method commit must be exact lowercase Git SHA-1")

def _hash_candidate(path: str) -> tuple[int,str]:
    """Hash bounded ciphertext candidate without resolving symlink targets."""
    if type(path) is not str or not path or Path(path).suffix != ".gpg":
        raise ValueError("Ciphertext filename must end with .gpg")
    flags=os.O_RDONLY
    if hasattr(os,"O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd=os.open(path,flags)
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or not 0<st.st_size<=MAX_BYTES:
            raise ValueError("Not a regular bounded nonempty ciphertext candidate")
        dig=sha256()
        total=0
        with os.fdopen(os.dup(fd),"rb") as handle:
            while chunk:=handle.read(65536):
                total+=len(chunk)
                if total>MAX_BYTES:
                    raise ValueError("Ciphertext candidate exceeds size cap")
                dig.update(chunk)
        if total != st.st_size:
            raise ValueError("Candidate changed during preflight")
        return total,dig.hexdigest()
    finally:
        os.close(fd)

def ciphertext_receipt(path: str, *, method_commit: str,
                       artifact_kind: str) -> dict[str,object]:
    _check_method(method_commit)
    if type(artifact_kind) is not str or artifact_kind not in ALLOWED_KINDS:
        raise ValueError("Invalid artifact kind")
    size,hash_value=_hash_candidate(path)
    return {
        "schema":SCHEMA,
        "study":"EXP-COEV-001",
        "status":STATUS,
        "artifact_kind":artifact_kind,
        "method_commit":method_commit,
        "ciphertext_sha256":hash_value,
        "ciphertext_bytes":size,
        "cryptographic_encryption_verified":False,
        "independent_custody_verified":False,
        "scientific_source_frozen":False,
    }

def verify_ciphertext_receipt(path: str, *, method_commit: str,
                              artifact_kind: str, receipt: dict[str,object]) -> None:
    """Recompute public hash and compare all fields; NOT a signature verifier."""
    if type(receipt) is not dict or any(type(key) is not str for key in receipt):
        raise ValueError("Untrusted receipt structure")
    canonical=ciphertext_receipt(path,method_commit=method_commit,artifact_kind=artifact_kind)
    if receipt != canonical or set(receipt)!=set(canonical) or any(
           type(receipt[k]) is not type(value) for k,value in canonical.items()):
        raise ValueError("Forged, stale or incomplete ciphertext receipt")

def _unique_keys(pairs: list[tuple[str,object]]) -> dict[str,object]:
    result={}
    for key,value in pairs:
        if key in result: raise ValueError("Duplicate receipt key")
        result[key]=value
    return result

def main() -> int:
    parser=argparse.ArgumentParser(description="LOCAL ciphertext hash check only; never decrypts")
    parser.add_argument("--mode",choices=("inspect","verify"),required=True)
    parser.add_argument("--ciphertext",required=True)
    parser.add_argument("--method-commit",required=True)
    parser.add_argument("--kind",choices=ALLOWED_KINDS,required=True)
    parser.add_argument("--receipt",help="Local JSON receipt file, verify mode only")
    args=parser.parse_args()
    if args.mode=="inspect":
        if args.receipt: parser.error("inspect does not read receipts")
        output=ciphertext_receipt(args.ciphertext,method_commit=args.method_commit,
                                  artifact_kind=args.kind)
        print(json.dumps(output,sort_keys=True,separators=(",",":")))
    else:
        if not args.receipt: parser.error("verify requires --receipt")
        with open(args.receipt,encoding="utf-8") as f:
            receipt=json.load(f,object_pairs_hook=_unique_keys)
        verify_ciphertext_receipt(args.ciphertext,method_commit=args.method_commit,
                                  artifact_kind=args.kind,receipt=receipt)
        print('{"status":"PUBLIC_CIPHERTEXT_HASH_MATCH_ONLY"}')
    return 0

if __name__=="__main__":
    raise SystemExit(main())
