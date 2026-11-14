"""SENTENCE-REVISION-1 common foundation; no learner or official runner.

Only fixed typed conditions are interpreted. No historical experiment imports.
"""
from .foundation import (
    BudgetExceeded, Condition, Fault, Meter, Snapshot, State, canonical,
    catalog, delete_right, execute, grammar_digest, keep, validate_input,
)

__all__ = [
    "BudgetExceeded", "Condition", "Fault", "Meter", "Snapshot", "State",
    "canonical", "catalog", "delete_right", "execute", "grammar_digest",
    "keep", "validate_input",
]
