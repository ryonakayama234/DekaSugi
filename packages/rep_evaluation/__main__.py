"""Public toy-only smoke command; no option to load formal private data."""
import json
from dataclasses import asdict
from . import run_toy

if __name__ == "__main__":
    print(json.dumps(asdict(run_toy()), sort_keys=True, ensure_ascii=False))
