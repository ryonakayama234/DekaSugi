"""Fixture-only evaluator-side command; deliberately no formal evaluation subcommand."""
import argparse
import json
from pathlib import Path
from .gate import run_gate

p=argparse.ArgumentParser(description='WORLD-LEAN-1 artificial fixture gate ONLY')
p.add_argument('command',choices=['fixture-gate'])
p.add_argument('--output',type=Path,help='write fixture evidence JSON')
a=p.parse_args()
report=run_gate()
result=json.dumps(report,ensure_ascii=True,sort_keys=True,indent=2)+'\n'
if a.output:
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(result,encoding='utf-8')
print(result)
