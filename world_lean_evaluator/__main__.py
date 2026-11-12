"""Explicit evaluator stages; CI uses fixture-gate and synthetic-dry-run only."""
import argparse
import json
from pathlib import Path
from .gate import run_gate
from .formal import dry_run, freeze_manifest, generate, run

p=argparse.ArgumentParser(description='WORLD-LEAN-1 evaluator, one-shot staged protocol')
p.add_argument('command',choices=['fixture-gate','synthetic-dry-run','freeze-manifest','formal-generation','formal-run'])
p.add_argument('--output',type=Path)
p.add_argument('--root',type=Path)
p.add_argument('--authorization',type=Path,help='external supervisor re-audit + Owner resume record; never synthesized by this CLI')
a=p.parse_args()
if a.command=='fixture-gate':report=run_gate()
else:
    if a.root is None:p.error('--root is required')
    if a.command=='synthetic-dry-run':report=dry_run(a.root)
    elif a.command=='freeze-manifest':report=freeze_manifest(a.root)
    else:
        auth=json.loads(a.authorization.read_bytes()) if a.authorization else None
        report=(generate if a.command=='formal-generation' else run)(a.root,authorization=auth)
result=json.dumps(report,ensure_ascii=True,sort_keys=True,indent=2)+'\n'
if a.output:
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(result,encoding='utf-8')
print(result)
