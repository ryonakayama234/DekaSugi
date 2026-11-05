"""R2-M-ENG independent runtime metering for typed Boolean trees.

Static tree size, actually visited nodes, and executed Boolean primitives are
distinct dimensions. No execution of caller-provided Python or private labels.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import sys
import time

from .records import Node, check_point
from .validator import check_ast

METER_VERSION = "r2-m-bool-shortcircuit-meter/1"


def peak_rss_bytes() -> int | None:
    """Process high-water RSS, *not* invocation-local peak memory."""
    try:
        import resource
    except ImportError:  # Windows: unavailable, do not invent a zero.
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


@dataclass(frozen=True, slots=True)
class AstCounts:
    ast_nodes_static: int
    node_visits_runtime: int
    primitive_ops_runtime: int

    def as_dict(self) -> dict[str, int]:
        return {
            "ast_nodes_static": self.ast_nodes_static,
            "node_visits_runtime": self.node_visits_runtime,
            "primitive_ops_runtime": self.primitive_ops_runtime,
        }


@dataclass(frozen=True, slots=True)
class MeteredPrediction:
    prediction: int
    counts: AstCounts
    cpu_seconds: float
    monotonic_wall_seconds: float
    process_peak_rss_bytes: int | None


def measure_ast(root: Node, point: tuple[int, int, int]) -> MeteredPrediction:
    """Count nodes reached under *actual* left-to-right short-circuit evaluation."""
    check_point(point)
    static = check_ast(root)
    visits = 0
    operations = 0
    start_cpu, start_wall = time.process_time(), time.perf_counter()

    def evaluate(node: Node) -> int:
        nonlocal visits, operations
        visits += 1
        op = node.op
        if op == "0":
            return 0
        if op == "1":
            return 1
        if op in ("x", "y", "z"):
            return point[{"x": 0, "y": 1, "z": 2}[op]]
        if op == "NOT":
            value = evaluate(node.args[0])
            operations += 1
            return 1 - value
        if op == "AND":
            left = evaluate(node.args[0])
            operations += 1
            return evaluate(node.args[1]) if left else 0
        if op == "OR":
            left = evaluate(node.args[0])
            operations += 1
            return 1 if left else evaluate(node.args[1])
        raise ValueError("VALIDATION_FAILED: unexpected AST primitive")

    result = evaluate(root)
    return MeteredPrediction(
        result, AstCounts(static, visits, operations),
        time.process_time() - start_cpu,
        time.perf_counter() - start_wall,
        peak_rss_bytes(),
    )


def cost_ledger(*, paid_inquiries: int, public_observations: int,
                decoder_invocations: int, candidates_generated: int,
                validator_invocations: int, h0_predicates_scanned: int,
                ast_counts: AstCounts, restore_bytes: int = 0,
                stored_bytes: int = 0, cpu_seconds: float = 0.0,
                wall_seconds: float = 0.0,
                process_peak_rss: int | None = None) -> dict[str, object]:
    """Explicit *unweighted* units; no mixed-cost scalar or hidden 16 candidates."""
    metrics = {
        "paid_inquiries": paid_inquiries,
        "public_observations": public_observations,
        "decoder_invocations": decoder_invocations,
        "candidates_generated": candidates_generated,
        "candidate_budget": 16,
        "family_size": 16,
        "validator_invocations": validator_invocations,
        "h0_predicates_scanned": h0_predicates_scanned,
        "restore_bytes": restore_bytes, "stored_bytes": stored_bytes,
        **ast_counts.as_dict(),
    }
    if any(type(v) is not int or v < 0 for v in metrics.values()):
        raise ValueError("INVALID: meter counter type/value")
    if (type(cpu_seconds) is not float or type(wall_seconds) is not float or
            not (0 <= cpu_seconds < float("inf") and
                 0 <= wall_seconds < float("inf")) or
            (process_peak_rss is not None and
             (type(process_peak_rss) is not int or process_peak_rss < 0))):
        raise ValueError("INVALID: meter resource type/value")
    metrics.update({
        "cpu_seconds": cpu_seconds, "monotonic_wall_seconds": wall_seconds,
        "process_peak_rss_bytes": process_peak_rss,
        "resource_scope": "current_process; RSS is process high-water mark",
        "meter_version": METER_VERSION, "candidate_accounting": "actual_generated",
    })
    return metrics
