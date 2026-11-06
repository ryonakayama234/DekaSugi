"""G3-2 descriptive raw cost rows. No amortization and no subtraction.

Child import observations are a component of parent wait4 process totals,
not an amount to add to or remove from them. Scientific scoring is absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import RSS_BYTES_CAP, rss_boundary_status

ALLOCATION_RULE_VERSION = "R2-M-A-G3-2-raw/1"
UNMEASURED = "UNMEASURED"


@dataclass(frozen=True, slots=True)
class RawProcessCost:
    """One reaped Linux child. None means genuinely not observed."""
    wall_seconds: float
    cpu_seconds: float | None
    peak_rss_bytes: int | None
    cgroup_memory_peak_bytes: int | None
    import_receipt: dict[str, object] | None
    trace_size_bytes: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "process_total": {
                "monotonic_wall_seconds": self.wall_seconds,
                "wait4_cpu_seconds": self.cpu_seconds,
                "wait4_peak_rss_bytes": self.peak_rss_bytes,
                "rss_boundary_status": (
                    rss_boundary_status(self.peak_rss_bytes)
                    if self.peak_rss_bytes is not None else UNMEASURED),
                "rss_si_limit_bytes": RSS_BYTES_CAP,
            },
            "cgroup": {
                "memory_peak_bytes": self.cgroup_memory_peak_bytes,
                "memory_is_not_process_rss": True,
            },
            "per_fresh_process": {
                "actual_import_cpu_s": (
                    self.import_receipt.get("import_cpu_seconds")
                    if self.import_receipt is not None else UNMEASURED),
                "actual_import_wall_s": (
                    self.import_receipt.get("import_wall_seconds")
                    if self.import_receipt is not None else UNMEASURED),
                "catalog_preparation_cpu_s": (
                    self.import_receipt.get("catalog_preparation_cpu_seconds")
                    if self.import_receipt is not None else UNMEASURED),
                "catalog_preparation_wall_s": (
                    self.import_receipt.get("catalog_preparation_wall_seconds")
                    if self.import_receipt is not None else UNMEASURED),
                "catalog_serialized_bytes": (
                    self.import_receipt.get("catalog_serialized_bytes")
                    if self.import_receipt is not None else UNMEASURED),
                "catalog_entries": (
                    self.import_receipt.get("catalog_entries")
                    if self.import_receipt is not None else UNMEASURED),
                "import_cost_in_parent_process_total": True,
                "catalog_cost_is_part_of_import_not_extra": True,
            },
            "one_off_preparation": {
                "actual_cpu_s": UNMEASURED,
                "actual_wall_s": UNMEASURED,
                "actual_bytes": UNMEASURED,
                "observed": False,
            },
            "per_use": {"trace_raw_bytes": (
                self.trace_size_bytes if self.trace_size_bytes is not None else UNMEASURED)},
            "projection": UNMEASURED,
            "no_raw_total_subtraction": True,
        }


def accounting_rows(
    *, raw: RawProcessCost, arm: str, law_id: str | None = None,
    child_slot: str | None = None, raw_receipt_sha256: str | None = None,
) -> tuple[dict[str, Any], ...]:
    """Parent-side ledger only. Never send law_id or rows to the child.

    The per-process totals are the sole aggregate resource values; detailed
    import rows are included *within* those totals, never summed separately.
    """
    details = raw.as_dict()
    rows: list[dict[str, Any]] = []

    def add(scope: str, phase: str, unit: str, value: object,
            origin: str, included: bool) -> None:
        rows.append({
            "charge_scope": scope, "observed_or_projected": "observed",
            "phase": phase, "arm": arm, "law": law_id, "child_slot": child_slot,
            "metric_unit": unit,
            "value_or_UNMEASURED": UNMEASURED if value is None else value,
            "causal_origin": origin, "included_in_process_total": included,
            "allocation_rule_version": ALLOCATION_RULE_VERSION,
            "raw_receipt_sha256": raw_receipt_sha256,
        })

    total = details["process_total"]
    for key, unit in (("monotonic_wall_seconds", "s"),
                      ("wait4_cpu_seconds", "s"),
                      ("wait4_peak_rss_bytes", "bytes")):
        add("per_fresh_process", key, unit, total[key],
            "parent_monotonic_or_wait4", True)
    for key, unit in (("actual_import_cpu_s", "s"),
                      ("actual_import_wall_s", "s"),
                      ("catalog_preparation_cpu_s", "s"),
                      ("catalog_preparation_wall_s", "s"),
                      ("catalog_serialized_bytes", "bytes")):
        add("per_fresh_process", key, unit, details["per_fresh_process"][key],
            "child_import_receipt_existing_CATALOG_PREPARATION_constants", True)
    add("per_fresh_process", "cgroup_memory_peak", "bytes",
        details["cgroup"]["memory_peak_bytes"], "cgroup_v2_not_process_rss", False)
    add("per_use", "trace_raw_bytes", "bytes",
        details["per_use"]["trace_raw_bytes"], "immutable_trace_raw_bytes", False)
    for metric, unit in (("actual_cpu_s", "s"), ("actual_wall_s", "s"),
                         ("actual_bytes", "bytes")):
        add("one_off_preparation", metric, unit, UNMEASURED,
            "not_prebuilt_outside_fresh_process", False)
    return tuple(rows)
