"""CI-SAFE-V2: no-execution allowlist for the successor workflow.

The historical docs-check.yml is immutable because PILOT-V1 included its
Git blob in a source-first freeze. This script never imports production
packages or launches a scorer/generator. It is intentionally self-pinning:
any successor YAML change requires updating this manifest and review.
"""
from __future__ import annotations

from hashlib import sha1
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR = ".github/workflows/research-verification-v2.yml"
HISTORIC = ".github/workflows/docs-check.yml"
HISTORIC_GIT_BLOB = "1a3ce868010a320216642abf56093dc3a89d8e91"

# Exact source text prevents extra steps, covert unsafe calls, triggers,
# third-party actions, shell blocks, environment substitutions and uploads.
EXPECTED_SUCCESSOR = "name: Research verification v2 (safe successor)\n\non:\n  push:\n    branches: [main]\n  pull_request:\n\npermissions:\n  contents: read\n\njobs:\n  verify-synthetic-and-source:\n    runs-on: ubuntu-latest\n    timeout-minutes: 15\n    steps:\n      - name: Checkout\n        uses: actions/checkout@v4\n      - name: Set up Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: \"3.12\"\n      - name: Assert v2 allowlist and exact historic source bytes\n        run: python scripts/check_research_ci_v2.py\n      - name: Validate docs and internal links\n        run: python scripts/check_docs.py\n      - name: Run whitelisted synthetic-only unit tests\n        run: python scripts/run_research_ci_v2_tests.py\n"


class CISafetyError(ValueError):
    """Fail closed on source drift or added workflow capability."""


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def validate_successor(source: bytes) -> None:
    if type(source) is not bytes or source != EXPECTED_SUCCESSOR.encode("utf-8"):
        raise CISafetyError("Successor CI workflow content/trigger/steps changed")


def validate_repo_files(root: Path = ROOT) -> dict[str, object]:
    """Static source gate only; no original generator, model or scoring run."""
    source_path = root / SUCCESSOR
    historic_path = root / HISTORIC
    lock_path = root / "experiments/OPPORTUNITY-001/pilot-generator-lock-v1.json"
    for path in (source_path, historic_path, lock_path):
        if not path.is_file() or path.is_symlink():
            raise CISafetyError("Missing or symlinked pinned CI source")
    validate_successor(source_path.read_bytes())
    if git_blob_sha(historic_path.read_bytes()) != HISTORIC_GIT_BLOB:
        raise CISafetyError("Historical workflow bytes have drifted")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("source_git_blobs", {}).get(HISTORIC) != HISTORIC_GIT_BLOB:
        raise CISafetyError("Historical PILOT-V1 workflow hash mismatches source lock")
    if (lock.get("new_train_pilot_scoring_permitted") is not False
            or lock.get("old_dev_or_final_scoring_permitted") is not False):
        raise CISafetyError("Historical method permits scoring unexpectedly")

    # A direct script invocation has scripts/ rather than the repo root on
    # sys.path. Add it only AFTER workflow, lock and old-workflow bytes were
    # checked; never import project scoring packages during this step.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Import only TWO stdlib-based *source byte* checkers; do not call the
    # generator's verify_generator_lock(), which reconstructs public tasks.
    from scripts.verify_opportunity_generator_lock import validate_source_blobs
    from scripts.verify_opportunity_legacy_sources import verify_legacy_source_bytes

    validate_source_blobs(lock, root)  # PILOT-V1 original 9 source files
    legacy = verify_legacy_source_bytes(root)  # old 14 source files, no partitions
    if (legacy["verified_source_count"] != 14
            or legacy.get("dev_or_final_generated") is not False):
        raise CISafetyError("Legacy source-only gate contract changed")
    return {
        "schema_version": "research-ci-successor-v2/source-only/1",
        "status": "static_source_integrity_pass",
        "historic_original_workflow_blob": HISTORIC_GIT_BLOB,
        "historic_pilot_source_count": 9,
        "historic_exp0003a_source_count": 14,
        "successor_command_allowlist_verified": True,
        "historic_dev_or_final_generated": False,
        "scoring_authorized": False,
        "legacy_workflow_disabled_verified": False,
        "successor_main_merge_authorized": False,
    }


def main() -> int:
    try:
        receipt = validate_repo_files()
    except (OSError, ValueError, TypeError, KeyError):
        # No local path or sensitive original contents in the CI log.
        print("CI-SAFE-V2: FAIL CLOSED (source or workflow gate)")
        return 1
    print(json.dumps(receipt, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
