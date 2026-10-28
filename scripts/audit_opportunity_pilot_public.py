"""OPPORTUNITY-001-PILOT-V1 independent source-only manifest checker.

Pure stdlib independent reimplementation of the preregistered public generator.
NO imports from packages/, no task solving, no policy choice, no DEV/FINAL.
It verifies a KNOWN public digest and computes a hash-only audit commitment.
Do not treat the third-audit hash as encryption or proof of private custody.
"""
from __future__ import annotations

from hashlib import sha256
import json
import random
import sys

METHOD = "OPPORTUNITY-001-PILOT-V1"
EXPECTED_PUBLIC_SHA256 = "bc950ef3187fc34851eef5cff6df194ce27186b3a03b5399f2209e9905f04a85"
FAMILIES = (
    "identity", "trim", "lower", "upper",
    "normalize_lower", "normalize_upper",
    "reverse_ood", "replace_first_ood",
)
ALPHABET = "uvwxYQ03"
WHITESPACE = ((" ", ""), ("  ", " "), ("\t", "\n"))


def _json_digest(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256(data).hexdigest()


def _token(seed: int, family: str, alphabet: str) -> str:
    rng = random.Random(seed)
    for _ in range(4096):
        length = rng.randrange(3, 8)
        value = "".join(rng.choice(alphabet) for _ in range(length))
        if len(set(value)) < 2 or value == value[::-1]:
            continue
        if family.endswith("lower") or family == "lower":
            if not any(ch.isupper() for ch in value):
                continue
        if family.endswith("upper") or family == "upper":
            if not any(ch.islower() for ch in value):
                continue
        return value
    raise ValueError("Independent generator token exhausted")


def _make_example(family: str, index: int, example_index: int,
                  seed: int, alphabet: str) -> dict[str, str]:
    token = _token(seed, family, alphabet)
    left, right = WHITESPACE[(index + example_index) % 3]
    if family == "identity":
        source, target = token, token
    elif family == "trim":
        source, target = left + token + right, token
    elif family == "lower":
        source, target = token, token.lower()
    elif family == "upper":
        source, target = token, token.upper()
    elif family == "normalize_lower":
        source, target = left + token + right, token.lower()
    elif family == "normalize_upper":
        source, target = left + token + right, token.upper()
    elif family == "reverse_ood":
        source, target = token, token[::-1]
    elif family == "replace_first_ood":
        source, target = token, "Z" + token[1:]
    else:
        raise ValueError("Unknown family")
    return {"input": source, "output": target}


def derive_hashes(*, alphabet: str = ALPHABET) -> dict[str, object]:
    """Recompute all 64 public cases and third audits in memory; expose hashes only."""
    public_rows = []
    private_commitments = []
    seen_seeds: set[int] = set()
    seen_public_ids: set[str] = set()
    for f, family in enumerate(FAMILIES):
        for i in range(8):
            examples = []
            for j in range(3):
                seed = 910000000 + f * 100000 + i * 10 + j
                if seed in seen_seeds:
                    raise ValueError("Independent seed collision")
                seen_seeds.add(seed)
                examples.append(_make_example(family, i, j, seed, alphabet))
            if len({(ex["input"], ex["output"]) for ex in examples}) != 3:
                raise ValueError("Independent example collision")
            public_shape = {
                "schema_version": "0.1",
                "domain": "string_to_string",
                "limits": {"max_ast_nodes": 4, "max_candidates": 100},
                "examples": examples[:2],
            }
            task_id = "t-" + _json_digest(public_shape)
            if task_id in seen_public_ids:
                raise ValueError("Independent public ID collision")
            seen_public_ids.add(task_id)
            public_rows.append({"task_id": task_id, **public_shape})
            private_commitments.append({
                "task_id": task_id,
                "third_audit_sha256": _json_digest(examples[2]),
            })
    if len(public_rows) != 64 or len(seen_seeds) != 192:
        raise ValueError("Independent population incomplete")
    return {
        "method": METHOD,
        "schema_version": "opportunity-pilot-independent-preflight-v1",
        "public_count": len(public_rows),
        "public_manifest_sha256": _json_digest(public_rows),
        "third_audit_commitments_sha256": _json_digest(private_commitments),
        "private_audit_bytes_published": False,
        "paired_trials_executed": 0,
        "dev_or_final_evaluated": False,
        "independent_from_project_generator_imports": True,
    }


def verify_public() -> dict[str, object]:
    result = derive_hashes()
    if result["public_manifest_sha256"] != EXPECTED_PUBLIC_SHA256:
        raise ValueError("Independent public manifest SHA mismatches fixed plan")
    return result


def main() -> int:
    print(json.dumps(verify_public(), sort_keys=True, ensure_ascii=False,
                     allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
