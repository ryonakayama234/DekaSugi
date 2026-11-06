"""G3-1 child import boundary: static graph + live import hooks.

Install BEFORE child-side dispatch imports. The process-wide audit hook is
irreversible; use only at a dedicated child entry point in G3-2. sys.modules
is checked once at installation to reject modules preloaded before the hook;
it is NOT used as a substitute for observing future imports.
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from importlib.abc import MetaPathFinder
from typing import Mapping

FORBIDDEN_CHILD_MODULES = (
    "packages.r2_m_eng.source_gateway",
    "packages.r2_m_eng.runner",
    "packages.r2_m_a.public_pipeline",
    "packages.r2_m_a.evaluator_gate",
    "packages.r2_m_a.evidence_ledger",
    "packages.r2_m_a.orchestrator",
)


def forbidden(name: object) -> bool:
    return type(name) is str and any(
        name == prefix or name.startswith(prefix + ".")
        for prefix in FORBIDDEN_CHILD_MODULES
    )


def _reject(name: object) -> None:
    if forbidden(name):
        raise ImportError("INVALID: evaluator/source/score import in child: " + str(name))


class ChildMetaPathGuard(MetaPathFinder):
    def find_spec(self, fullname: str, path=None, target=None):
        _reject(fullname)
        return None


def _audit_import(event: str, args: tuple[object, ...]) -> None:
    if event == "import" and args:
        _reject(args[0])


def install_child_import_guard() -> ChildMetaPathGuard:
    """Child-process startup ONLY; must precede ANY evaluator-related import.

    A previously cached forbidden module is blocked at installation. Audit and
    meta_path hooks continue observing function-local and importlib imports.
    """
    for module in tuple(sys.modules):
        _reject(module)
    guard = ChildMetaPathGuard()
    sys.meta_path.insert(0, guard)
    sys.addaudithook(_audit_import)
    return guard


def _imports(module_name: str, source: str) -> set[str]:
    package = module_name.rpartition(".")[0]
    found: set[str] = set()
    for entry in ast.walk(ast.parse(source, filename=module_name)):
        if isinstance(entry, ast.Import):
            found.update(alias.name for alias in entry.names)
        elif isinstance(entry, ast.ImportFrom):
            if entry.level:
                root = importlib.util.resolve_name(
                    "." * entry.level + (entry.module or ""), package)
            else:
                root = entry.module or ""
            if root:
                found.add(root)
            for alias in entry.names:
                if alias.name != "*":
                    found.add(root + "." + alias.name if root else alias.name)
    return found


def audit_static_child_graph(
    sources: Mapping[str, str], *, entrypoints: tuple[str, ...]
) -> frozenset[str]:
    """Reject reachable forbidden imports in the provided module source map.

    A PARTIAL source map cannot prove the complete import closure. G4 audits the
    entire exact-head graph, while the live hook covers delayed imports.
    """
    if type(sources) is not dict or type(entrypoints) is not tuple:
        raise ValueError("INVALID: source map and entrypoints required")
    if not entrypoints or any(type(name) is not str or name not in sources
                              for name in entrypoints):
        raise ValueError("INVALID: missing child entrypoint source")
    visited: set[str] = set()
    pending = list(entrypoints)
    while pending:
        name = pending.pop()
        _reject(name)
        if name in visited:
            continue
        visited.add(name)
        for target in _imports(name, sources[name]):
            _reject(target)
            if target in sources and target not in visited:
                pending.append(target)
    return frozenset(visited)
