"""Deterministic, invented-fixture-only Gate F structural report."""
import json
from packages.active_feasibility import census_fixture

if __name__ == "__main__":
    print(json.dumps(census_fixture().to_dict(), sort_keys=True, ensure_ascii=False,
                     indent=2))
