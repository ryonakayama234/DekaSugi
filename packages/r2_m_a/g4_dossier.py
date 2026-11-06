"""G3-3 G4 dossier *generator*, NOT a G4 audit or decision.

Generates eight immutable NOT_AUDITED templates to be filled by a future
independent actual-path auditor. Does not import a child, score or source.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

from .contracts import G2_MAIN_SHA, G2_PREREG_SHA256, EXPECTED_SLOTS
from .evidence_ledger import _write_once, canonical
from .remote_custody import CustodyBlocked

REQUIRED = (
    "source-lock.json", "import-graph.json", "routes.json",
    "arms-and-budget.json", "cost-audit.json", "custody-audit.json",
    "negative-tests.md", "g4-decision-template.md",
)


def generate_g4_dossier(destination: str | Path, *, target_head: str,
                        engineering_only: bool) -> dict[str, str]:
    """Exclusive fresh directory; no files are overwritten and no audits run."""
    if (engineering_only is not True or type(target_head) is not str
            or not re.fullmatch(r"[0-9a-f]{40}", target_head)):
        raise CustodyBlocked("RUN_BLOCK: exact prospective head required")
    directory = Path(destination).absolute()
    if directory.is_symlink():
        raise CustodyBlocked("RUN_BLOCK: dossier must not be a symlink")
    try:
        directory.mkdir(mode=0o700)  # fail if existing
    except OSError as exc:
        raise CustodyBlocked("RUN_BLOCK: dossier already exists/unwritable") from exc

    common = {
        "status": "NOT_AUDITED", "audit_target_head": target_head,
        "g2_frozen_main": G2_MAIN_SHA, "g2_frozen_document_sha256": G2_PREREG_SHA256,
        "g4_approved": False, "g5_order": "NOT_FIXED", "g6_execution": "NOT_AUTHORIZED",
        "actual_path_evidence": "NOT_COLLECTED",
    }
    payloads = {
        "source-lock.json": {**common,
            "git_tree_sha": None, "method_control_policy_digests": None,
            "os_python_kernel_cgroup": None, "changed_files": None},
        "import-graph.json": {**common,
            "static_child_closure": None, "live_audit_meta_path_hooks": None,
            "child_args_env_taint_coverage": None},
        "routes.json": {**common, "f00_f10_route_reachability": None,
            "restore_decoder_validator_call_counts": None,
            "independent_controls_not_fallbacks": None},
        "arms-and-budget.json": {**common, "expected_slots": EXPECTED_SLOTS,
            "arms": 7, "use_points": 4, "laws": 16, "controls_ties_caps": None,
            "g5_order_permit": None, "f01_f11_oracle_inactive_proof": None},
        "cost-audit.json": {**common, "wait4_raw_cpu_rss_wall": None,
            "resource_kill_fault_injection": None, "rss_si_bytes": 512000000,
            "cgroup_group_vs_process_rss": None,
            "catalog_import_and_one_off_confounding": None},
        "custody-audit.json": {**common, "q_before_answer_remote_readback": None,
            "prescore_remote_readback": None, "journal_chronology": None,
            "missingness_and_invalid_slots": None,
            "external_timestamp_authority": "NONE_GITHUB_ONLY",
            "history_rewrite_risk": "NOT_ELIMINATED"},
    }
    md = {
        "negative-tests.md": ("# G4 negative tests — NOT AUDITED\n\n"
             f"Target exact head: `{target_head}`\n\n"
             "Required: parent death survivor, SIGXCPU ignored, cgroup denial, "
             "transitive/delayed import, private-taint, malformed stdout, "
             "short RSS spike, process/group RSS disagreement, missing raw receipt, "
             "Q precommit failure, prescore failure, journal mutation/reorder, "
             "concurrent duplicate attempts, NaN/UTF-8 failures.\n\n"
             "Actual test run IDs/results/logs: NOT_COLLECTED.\n"
             "Independent reviewer/signature: PENDING.\n"),
        "g4-decision-template.md": ("# G4 actual-path decision — NOT AUDITED\n\n"
             f"Target exact head: `{target_head}`\n"
             "Muse: PENDING (PASS / STOP / CHANGE)\n"
             "Owner: PENDING; independent approval required\n"
             "Open P0/P1: UNASSESSED\n"
             "Closure: UNKNOWN; M_use: NOT_CERTIFIED; M_gap: UNKNOWN; "
             "N_rep/U/T/F01/F11: NOT_EVALUATED; B: NO-GO\n"
             "G4 code change -> RUN_BLOCK and new exact-head audit.\n"
             "G5 order and G6 execution/scoring require separate Owner GO.\n"),
    }
    receipts = {}
    for name in REQUIRED:
        raw = (canonical(payloads[name]) if name in payloads
               else md[name].encode("utf-8"))
        _write_once(directory / name, raw)
        receipts[name] = sha256(raw).hexdigest()
    return receipts
