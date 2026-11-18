"""Separate prediction and scoring processes for PART-REFERENCE-1."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FREEZE = '5ea88306a957bc85385cacfa2a57cf24eac4b9ea'
DATA = ROOT / 'experiments/PART-REFERENCE-1'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def frozen(name):
    path = DATA / name
    expected = subprocess.check_output(['git', 'show', f'{FREEZE}:{path.relative_to(ROOT)}'], cwd=ROOT)
    raw = path.read_bytes()
    if raw != expected:
        raise ValueError(f'freeze drift: {name}')
    return raw


def save(path, value):
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    if path.read_bytes() != raw:
        raise ValueError('readback mismatch')
    return digest(raw)


def run(stage, out):
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    if stage == 'predict':
        out.mkdir(parents=True, exist_ok=False)
        inputs = {name: frozen(name) for name in ('train.json', 'queries.json', 'plan.md')}
        sys.path.insert(0, str(ROOT))
        from packages.part_reference import acquire, predict
        rows = json.loads(inputs['train.json'])
        queries = json.loads(inputs['queries.json'])
        if len(queries) != 16 or len({q['id'] for q in queries}) != 16:
            raise ValueError('query count')
        arms = {}
        for arm in ('REF', 'CHAR', 'MASK'):
            cpu, wall = time.process_time(), time.perf_counter()
            chunks, costs = acquire(rows)
            records = [predict(chunks, q, arm, costs) for q in queries]
            arms[arm] = dict(chunks=chunks, records=records,
                             cpu_seconds=time.process_time()-cpu,
                             wall_seconds=time.perf_counter()-wall)
        source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        prediction_sha = save(out / 'predictions.json', dict(schema='part-reference/1', arms=arms,
                              source_commit=source, freeze_commit=FREEZE, python=platform.python_version(),
                              input_sha256={k: digest(v) for k, v in inputs.items()},
                              answers_read_before_lock=0))
        save(out / 'PREDICTIONS-LOCK.json', dict(predictions_sha256=prediction_sha))
    else:
        from audit_part_reference import audit
        raw = (out / 'predictions.json').read_bytes()
        lock = json.loads((out / 'PREDICTIONS-LOCK.json').read_text())
        if lock != dict(predictions_sha256=digest(raw)):
            raise ValueError('prediction lock mismatch')
        # The first answer read happens in this process after prediction readback.
        answers_raw = frozen('answers.json')
        evidence = json.loads(raw)
        summary = audit(evidence, json.loads(answers_raw))
        save(out / 'report.json', dict(summary, predictions_sha256=digest(raw),
                                       answers_sha256=digest(answers_raw)))
    save(out / f'{stage}-cost.json', dict(cpu_seconds=time.process_time()-start_cpu,
         wall_seconds=time.perf_counter()-start_wall,
         payload_bytes_before_cost=sum(p.stat().st_size for p in out.iterdir())))
    if stage == 'score':
        save(out / 'COMPLETE.json', {p.name: digest(p.read_bytes()) for p in sorted(out.iterdir())})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('predict', 'score'))
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    run(args.stage, args.out)
