"""python -m packages.cli --suite [--output file.json] or --task task.json."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import subprocess
import sys

from packages.protocol import Call, Input, DSLValidationError, parse_task, check_program
from packages.library import DEFAULT_REGISTRY
from packages.runtime import evaluate
from packages.synthesis import synthesize


def _git_sha() -> str | None:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True,
                              text=True, timeout=3)
        return proc.stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def _task(name: str, pairs: list[tuple[str, str]], *, limit: int = 5000) -> dict:
    return {
        "schema_version": "0.1", "task_id": name, "domain": "string_to_string",
        "examples": [{"input": x, "output": y} for x, y in pairs],
        "limits": {"max_ast_nodes": 4, "max_candidates": limit},
    }


def run_suite() -> dict:
    """Seven preregistered case categories, with deterministic twice-run check."""
    cases = [
        ("case-01-identity", [("abc", "abc"), ("z", "z")], "solved", 5000),
        ("case-02-trim", [(" x ", "x"), ("  y", "y")], "solved", 5000),
        ("case-03-lower", [("HI", "hi"), ("Z", "z")], "solved", 5000),
        ("case-04-composition", [(" RED ", "red"), (" Blue ", "blue")], "solved", 5000),
        ("case-05-not-found", [("ab", "ba")], "not_found", 5000),
        ("case-06-budget", [(" RED ", "red"), (" Blue ", "blue")], "budget_exhausted", 1),
    ]
    rows = []
    for name, pairs, expected, limit in cases:
        task = parse_task(_task(name, pairs, limit=limit))
        first, second = synthesize(task), synthesize(task)
        stable = (first.status, first.program, first.tested_candidates, first.trace_sha256) == (
            second.status, second.program, second.tested_candidates, second.trace_sha256)
        passed = first.status == expected and stable and first.tested_candidates <= limit
        rows.append({"case": name, "expected": expected, "passed": passed, "deterministic": stable,
                     "result": first.to_dict(), "repeat": second.to_dict()})

    invalids = [Call("unknown", Input()), Call("trim", Input("Integer"))]
    rejected = []
    for ast in invalids:
        try:
            check_program(ast, DEFAULT_REGISTRY.signatures)
            evaluate(ast, "some text")
        except DSLValidationError:
            rejected.append(True)
        else:
            rejected.append(False)
    rows.append({"case": "case-07-invalid-ast", "expected": "rejected",
                 "passed": all(rejected), "checks_rejected": rejected})

    return {"experiment_id": "EXP-0001", "status": "pass" if all(row["passed"] for row in rows) else "fail",
            "source_commit": _git_sha(), "environment": {"python": sys.version.split()[0],
            "platform": platform.platform(), "processor": platform.processor()},
            "registry": [{"op_id": p.op_id, "semantics_version": p.semantics_version}
                         for p in DEFAULT_REGISTRY.primitives], "cases": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DekaSugi bounded program synthesizer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--suite", action="store_true", help="Run EXP-0001 preregistered cases")
    group.add_argument("--task", type=Path, help="JSON TaskSpec file")
    parser.add_argument("--output", type=Path, help="Optional machine-readable JSON output")
    args = parser.parse_args(argv)
    try:
        if args.suite:
            outcome = run_suite()
        else:
            task = parse_task(json.loads(args.task.read_text(encoding="utf-8")))
            outcome = synthesize(task).to_dict()
        encoded = json.dumps(outcome, ensure_ascii=False, sort_keys=True, indent=2)
        print(encoded)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded + "\n", encoding="utf-8")
        return 0 if outcome.get("status") not in {"fail"} else 1
    except (DSLValidationError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
