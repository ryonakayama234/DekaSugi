"""Independent finite-table recount. Does not import the learner or runner."""
import hashlib
import json
import subprocess
from pathlib import Path
import sys


TEXT = {'left': {1: 'ABBA', 2: 'BAAB'}, 'right': {1: 'CDDC', 2: 'DCCD'}}
IDS = {'left': {1: 'C01', 2: 'C02'}, 'right': {1: 'C03', 2: 'C04'}}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(evidence, answers):
    require(evidence['schema'] == 'part-reference/1', 'schema')
    require(evidence['answers_read_before_lock'] == 0, 'early answers')
    require(set(evidence['arms']) == {'REF', 'CHAR', 'MASK'}, 'arms')
    chunks = []
    for i, (side, selector) in enumerate([('left', 1), ('left', 2), ('right', 1), ('right', 2)]):
        chunks.append(dict(id=f'C{i+1:02}', side=side, selector=selector, text=TEXT[side][selector],
                           evidence=[f'T{2*i+1:02}', f'T{2*i+2:02}'], order=i+1, status='candidate'))
    counts = {}
    outputs = {}
    for arm, state in evidence['arms'].items():
        require(state['chunks'] == chunks, 'acquisition evidence')
        require(len(state['records']) == 16, 'record count')
        counts[arm] = dict(main=0, control=0)
        outputs[arm] = []
        for index, record in enumerate(state['records']):
            pairs = [(1,1),(1,2),(2,1),(2,2),(1,0),(2,0),(0,1),(0,2)]
            l, r = pairs[index // 2]
            text = ('m', 'n')[index % 2]
            key = f'Q{index+1:02}'
            group = 'main' if index < 8 else 'control'
            require(record['query'] == dict(id=key, group=group, left=l, right=r, text=text), 'query order')
            expected_candidates = []
            for left_mode in range(3 if l else 1):
                for right_mode in range(3 if r else 1):
                    body = []; expanded = []
                    for side, selector, mode in [('left',l,left_mode), ('right',r,right_mode)]:
                        if side == 'right':
                            body.append(['copy',None]); expanded.append(['copy',None])
                        if mode:
                            letters = [['char',c] for c in TEXT[side][selector]]
                            expanded.extend(letters)
                            body.extend([['ref',IDS[side][selector]]] if mode == 2 and arm != 'CHAR' else letters)
                    expected_candidates.append(dict(slot=len(expected_candidates), body=body, expanded=expanded,
                        satisfied=int(left_mode > 0)+int(right_mode > 0), stored_length=len(body),
                        expanded_length=len(expanded), within_limits=len(body) <= 5 and len(expanded) <= 9))
            require(record['candidates'] == expected_candidates, 'candidate replay')
            require(record['preselection_cost'] == dict(training_rows=8, scanned_characters=40, acquired=4,
                candidate_slots=len(expected_candidates), selection_slots=len(expected_candidates),
                expanded_instructions=sum(c['expanded_length'] for c in expected_candidates)), 'cost recount')
            eligible = sorted((c for c in expected_candidates if c['within_limits'] and
                (arm != 'MASK' or not any(op == 'ref' for op, _ in c['body']))),
                key=lambda c: (-c['satisfied'], c['stored_length'], c['slot']))
            winner = eligible[0]
            require(record['selected_slot'] == winner['slot'], 'winner')
            used = [value for op,value in winner['body'] if op == 'ref']
            output = ''.join(text if op == 'copy' else value for op,value in winner['expanded'])
            require(record['used_references'] == used and record['output'] == output, 'execution')
            require(record['executed_instructions'] == len(winner['expanded']), 'execution cost')
            require(answers[key] == TEXT['left'].get(l,'')+text+TEXT['right'].get(r,''), 'answer table')
            counts[arm][group] += int(output == answers[key])
            outputs[arm].append(output)
            if arm == 'REF' and group == 'main' and output == answers[key]:
                require(used == [IDS['left'][l], IDS['right'][r]], 'reference dependency')
    require(set(answers) == {f'Q{i:02}' for i in range(1,17)}, 'answer coverage')
    for ref, mask, char in zip(*(evidence['arms'][a]['records'] for a in ('REF','MASK','CHAR'))):
        for field in ('candidates','preselection_cost','query'):
            require(ref[field] == mask[field], 'REF MASK mismatch')
        require([c['expanded_length'] for c in ref['candidates']] ==
                [c['expanded_length'] for c in char['candidates']], 'CHAR expanded mismatch')
    require(all(v['control'] == 8 for v in counts.values()), 'control failure')
    require(counts['CHAR']['main'] == counts['MASK']['main'] == 0, 'unexpected baseline success')
    totals = {}
    for arm, state in evidence['arms'].items():
        records = state['records']
        totals[arm] = dict(training_rows=8, scanned_characters=40, acquired=4,
            candidate_slots=sum(r['preselection_cost']['candidate_slots'] for r in records),
            expanded_instructions=sum(r['preselection_cost']['expanded_instructions'] for r in records),
            selection_slots=sum(r['preselection_cost']['selection_slots'] for r in records),
            executed_instructions=sum(r['executed_instructions'] for r in records))
    return dict(verdict='MET' if counts['REF']['main'] == 8 else 'NOT_MET', counts=counts,
                paired_accuracy_difference={a:(counts['REF']['main']-counts[a]['main'])/8 for a in ('CHAR','MASK')},
                audit_mismatches=0, selected_limit_violations=0, reference_dependent_main=counts['REF']['main'],
                logical_cost=totals, independent_vm_review='pending')


def audit_directory(root):
    manifest = json.loads((root/'COMPLETE.json').read_text())
    expected = {'predictions.json','PREDICTIONS-LOCK.json','predict-cost.json','report.json','score-cost.json'}
    require(set(manifest) == expected, 'manifest members')
    for name, sha in manifest.items():
        require(hashlib.sha256((root/name).read_bytes()).hexdigest() == sha, 'file digest')
    evidence = json.loads((root/'predictions.json').read_text())
    lock = json.loads((root/'PREDICTIONS-LOCK.json').read_text())
    require(lock == {'predictions_sha256':manifest['predictions.json']}, 'prediction lock')
    repo = Path(__file__).resolve().parents[1]
    data = repo/'experiments/PART-REFERENCE-1'
    freeze = '5ea88306a957bc85385cacfa2a57cf24eac4b9ea'
    require(evidence['freeze_commit'] == freeze, 'freeze identity')
    for name in ('train.json','queries.json','answers.json','plan.md'):
        original = subprocess.check_output(['git','show',f'{freeze}:experiments/PART-REFERENCE-1/{name}'],cwd=repo)
        require((data/name).read_bytes() == original, 'frozen bytes')
    for path in ('packages/part_reference/__init__.py','scripts/run_part_reference.py',
                 'scripts/audit_part_reference.py'):
        original = subprocess.check_output(['git','show',f"{evidence['source_commit']}:{path}"],cwd=repo)
        require((repo/path).read_bytes() == original, 'execution source drift')
    for name, sha in evidence['input_sha256'].items():
        require(name in ('train.json','queries.json','plan.md'), 'input name')
        require(hashlib.sha256((data/name).read_bytes()).hexdigest() == sha, 'input digest')
    require(set(evidence['input_sha256']) == {'train.json','queries.json','plan.md'}, 'input coverage')
    answers_raw = (data/'answers.json').read_bytes()
    result = audit(evidence, json.loads(answers_raw))
    report = json.loads((root/'report.json').read_text())
    require(report == dict(result, predictions_sha256=manifest['predictions.json'],
                           answers_sha256=hashlib.sha256(answers_raw).hexdigest()), 'report recount')
    for filename in ('predict-cost.json','score-cost.json'):
        cost = json.loads((root/filename).read_text())
        require(all(isinstance(cost[k],(int,float)) and 0 <= cost[k] < float('inf')
                    for k in ('cpu_seconds','wall_seconds','payload_bytes_before_cost')), 'process cost')
    return result


if __name__ == '__main__':
    print(json.dumps(audit_directory(Path(sys.argv[1])), ensure_ascii=False, indent=2))
