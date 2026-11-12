"""Read-only byte lock of WORLD-LEAN-1 source. No evaluation imported or run."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs/research/WORLD-LEAN-1-SOURCE-LOCK-20261112-02.json'

def canonical(obj):
    return (json.dumps(obj,sort_keys=True,ensure_ascii=True,separators=(',',':'))+'\n').encode('utf-8')

def main():
    manifest=json.loads(MANIFEST.read_bytes())
    expected=manifest['file_sha256']
    actual={}
    for path in sorted(expected):
        if path.startswith('/') or '..' in Path(path).parts:raise SystemExit('UNSAFE PATH')
        actual[path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    if actual!=expected:raise SystemExit('WORLD-LEAN SOURCE-LOCK MISMATCH')
    combined=hashlib.sha256(canonical(actual)).hexdigest()
    if combined!=manifest['source_digest']:
        raise SystemExit('WORLD-LEAN SOURCE-LOCK COMBINED DIGEST MISMATCH')
    print('WORLD-LEAN-1 SIX-DEMO SOURCE-LOCK PASS',combined,'files',len(actual))

if __name__=='__main__':main()
