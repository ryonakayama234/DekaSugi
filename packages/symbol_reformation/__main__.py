"""Fixed training diagnostic CLI; exclusive output, bounded complete or STOP receipt."""
import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import platform
import signal
import subprocess
import sys

from . import (ARMS, ARCHIVE_SHA, STATE_SHA, PLAN_SHA, LIMITS, ROOT,
               Budget, ResourceStop, byte_cost, canonical, diagnose, encode, load_input)


@contextmanager
def time_guard():
    """Single-process POSIX CPU/wall interrupts also cover JSON and disk operations."""
    def stopped(signum, frame):
        raise ResourceStop('wall_seconds' if signum == signal.SIGALRM else 'cpu_seconds')
    saved = {}
    try:
        for sig, timer, limit in ((signal.SIGALRM, signal.ITIMER_REAL, 'wall_seconds'),
                                  (signal.SIGPROF, signal.ITIMER_PROF, 'cpu_seconds')):
            saved[sig] = (signal.getsignal(sig), signal.getitimer(timer), timer)
            signal.signal(sig, stopped)
            signal.setitimer(timer, LIMITS[limit])
        yield
    finally:
        for sig, (handler, old_timer, timer) in saved.items():
            signal.setitimer(timer, 0)
            signal.signal(sig, handler)
            signal.setitimer(timer, *old_timer)


def markdown(report):
    lines = ['# SYMBOL-REFORMATION-1 結果票', '', 'id: SYMBOL-REFORMATION-1-RESULT',
             'status: local_engineering_complete_muse_pending', 'updated: 2026-11-18',
             'tags: training, engineering, reformation', '',
             '旧試験・予測器・学習再実行を使わない、訓練側の一巡診断。候補はcandidateのまま。', '',
             '|方式|前AST|後AST|新規|新規支持≧2|新規反例あり|新規の不適用行数|',
             '|---|---:|---:|---:|---:|---:|---:|']
    for arm in ARMS:
        s = report['summary'][arm]
        lines.append('|'+arm+'|'+'|'.join(str(s[k]) for k in ('before','after','new','new_supported','new_with_failure','new_inapplicable_rows'))+'|')
    cmp = report['comparison']
    lines += ['', f"両方式の前集合・NO-CHUNK後集合・FULL文字形成を除いたchunk固有の新規AST: **{len(cmp['full_chunk_exclusive_new'])}件**。そのうち異なる生文字列2件以上の支持: **{len(cmp['full_chunk_exclusive_supported'])}件**。",
              'これは候補形成の結果であり、有効な未見予測・ブートストラップ能力の証拠にはしない。', '',
              '|方式|行ペア|形成試行|既存AST再発見イベント|再形成内重複イベント|両経路AST|',
              '|---|---:|---:|---:|---:|---:|']
    for arm in ARMS:
        s=report['summary'][arm]
        lines.append('|'+arm+'|'+'|'.join(str(s[k]) for k in ('pairs','attempts','existing_rediscovery_events','repeated_formation_events','cross_route_asts'))+'|')
    lines += ['', '再発見と再形成内重複は重なり得る独立カウンタ。全不成立試行・出力0件もtrials.jsonに保持。',
              '候補別AST・形成元位置・chunk獲得episode・支持match・反例・不適用はdiagnostic.jsonとevents.jsonで照合する。',
              '支持の分母は18種類であり、54観測や再形成回数を追加支持にしない。適用範囲もこの18行に限る。', '',
              f"状態digest（前後一致）: `{report['state_sha256']}`。",
              f"固定計画SHA256: `{PLAN_SHA}`。実行source: `{report['source_commit']}`。", '',
              'CPU/wall・全操作と内訳・ファイルbyteはcost.json。COMPLETE.jsonとSHA256SUMS.jsonの読戻しを要する。',
              'Muse独立確認は未実施。旧負の所見を維持し、条件を変えて成功例を探さずこの診断を閉じる。', '']
    return '\n'.join(lines)


def run(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    budget = Budget(LIMITS)
    total_bytes = 0
    written = []

    def put(name, data):
        nonlocal total_bytes
        # Reserve 16KB for an emergency receipt; no silent truncation.
        if total_bytes + len(data) + 16384 > LIMITS['artifact_bytes']:
            raise ResourceStop('artifact_bytes')
        byte_cost(budget, 'write_byte', len(data))
        with (out/name).open('xb') as f:
            f.write(data)
        written.append(name)
        total_bytes += len(data)
        byte_cost(budget, 'readback_byte', len(data))
        back = (out/name).read_bytes()
        if back != data:
            raise ValueError('write/readback mismatch')
        budget.check()
        return sha256(back).hexdigest()

    try:
        with time_guard():
            source = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
            states = load_input(budget)
            diagnostic, trials, events = diagnose(states, budget)
            report = dict(schema='symbol-reformation-report/1', status='COMPLETE', source_commit=source,
                          archive_sha256=ARCHIVE_SHA, input_state_sha256=STATE_SHA, plan_sha256=PLAN_SHA,
                          runtime=dict(python=sys.version, platform=platform.platform()),
                          state_sha256=diagnostic['state_before'],
                          summary={a:diagnostic['arms'][a]['summary'] for a in ARMS},
                          comparison=diagnostic['comparison'])
            hashes = {}
            for name, value in (('diagnostic.json',diagnostic), ('trials.json',trials), ('events.json',events), ('report.json',report)):
                hashes[name] = put(name, encode(value,budget))
            text = markdown(report)
            budget.tick('markdown_character', len(text))
            hashes['result.md'] = put('result.md',text.encode())
            # Counters below include reservation/serialization/readback for the final
            # cost/manifest/completion, recorded separately in COMPLETE's final receipt.
            cost = dict(total=budget.receipt(), arms={a:diagnostic['arms'][a]['cost'] for a in ARMS},
                        artifact_bytes_before_cost=total_bytes,
                        accounting='logical operations; final counters are in COMPLETE.json')
            hashes['cost.json'] = put('cost.json', encode(cost,budget))
            hashes_bytes = encode(hashes,budget)
            put('SHA256SUMS.json',hashes_bytes)
            # Fixed-size reservation avoids self-referential byte/counter claims.
            budget.tick('completion_reserve', 4096)
            budget.check()
            complete = dict(status='COMPLETE', manifest_sha256=sha256(hashes_bytes).hexdigest(),
                            final_cost=budget.receipt(), artifact_bytes_before_completion=total_bytes,
                            completion_reserve_operations=4096,
                            note='final receipt includes reserved cost of completion encode/write/readback')
            data=(canonical(complete)+'\n').encode()
            if len(data)>4096 or total_bytes+len(data)>LIMITS['artifact_bytes']:
                raise ResourceStop('completion_bytes')
            with (out/'COMPLETE.json').open('xb') as f:f.write(data)
            written.append('COMPLETE.json')
            if (out/'COMPLETE.json').read_bytes()!=data:
                raise ValueError('completion readback')
            budget.check()
            total_bytes += len(data)
        print(canonical(dict(status='COMPLETE', summary=report['summary'], comparison=report['comparison'],
                             artifact_bytes=total_bytes, cost=budget.receipt())))
        return 0
    except (ResourceStop, ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        # Remove only our own completed-comparison claims, retain raw partial evidence.
        for name in ('report.json','result.md','COMPLETE.json'):
            if name in written:
                (out/name).unlink(missing_ok=True)
        status='RESOURCE_STOP' if isinstance(exc,ResourceStop) else 'INVALID'
        stop=dict(status=status, reason=str(exc), cost_at_stop=budget.receipt(),
                  comparison_complete=False, emergency_record_unmetered=True,
                  partial_artifacts=[p.name for p in out.iterdir()])
        data=(canonical(stop)+'\n').encode()
        if len(data)>16384: raise RuntimeError('emergency receipt capacity')
        (out/'STOP.json').write_bytes(data)
        print(canonical(dict(status=status, reason=str(exc))))
        return 2


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    raise SystemExit(run(parser.parse_args().output))
