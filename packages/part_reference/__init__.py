"""Finite reference experiment. No fixture, answer or file access."""
from itertools import product


def acquire(rows):
    """Learn directed residuals only from pairs of training observations."""
    if len(rows) != 8 or len({r['id'] for r in rows}) != 8:
        raise ValueError('expected eight distinct training rows')
    groups = {}
    scans = 0
    for row in rows:
        left, right, text, output = (row[k] for k in ('left', 'right', 'text', 'output'))
        if (left == 0) == (right == 0) or not text or output.count(text) != 1:
            raise ValueError('ambiguous or non-unilateral training row')
        side, selector = ('left', left) if left else ('right', right)
        before, after = output.split(text)
        residual, opposite = (before, after) if left else (after, before)
        if opposite or not residual:
            raise ValueError('residual on wrong side')
        groups.setdefault((side, selector), []).append((row['id'], text, residual))
        scans += len(output)
    if len(groups) != 4:
        raise ValueError('expected four residual groups')
    chunks = []
    for (side, selector), examples in groups.items():
        if len(examples) != 2 or len({x[1] for x in examples}) != 2 or examples[0][2] != examples[1][2]:
            raise ValueError('two distinct supporting examples required')
        chunks.append(dict(id=f'C{len(chunks)+1:02}', side=side, selector=selector,
                           text=examples[0][2], evidence=[x[0] for x in examples],
                           order=len(chunks)+1, status='candidate'))
    return chunks, dict(training_rows=8, scanned_characters=scans, acquired=len(chunks))


def expand(body, chunks):
    lookup = {c['id']: c for c in chunks}
    expanded = []
    used = []
    for operation, value in body:
        if operation == 'ref':
            chunk = lookup[value]
            expanded.extend([['char', ch] for ch in chunk['text']])
            used.append(value)
        elif operation == 'char' and isinstance(value, str) and len(value) == 1:
            expanded.append(['char', value])
        elif operation == 'copy' and value is None:
            expanded.append(['copy', None])
        else:
            raise ValueError('invalid instruction')
    return expanded, used


def predict(chunks, query, arm, acquisition_cost):
    if arm not in ('REF', 'CHAR', 'MASK'):
        raise ValueError('unknown arm')
    choices = []
    for side in ('left', 'right'):
        selector = query[side]
        options = [[]]
        if selector:
            matches = [c for c in chunks if c['side'] == side and c['selector'] == selector]
            if len(matches) != 1:
                raise ValueError('unknown or ambiguous selector')
            chunk = matches[0]
            options += [[['char', ch] for ch in chunk['text']], [['ref', chunk['id']]]]
        choices.append(options)
    candidates = []
    for slot, (left, right) in enumerate(product(*choices)):
        if slot >= 9:
            raise ValueError('candidate cap')
        body = left + [['copy', None]] + right
        expanded, _ = expand(body, chunks)
        if arm == 'CHAR':
            body = expanded
        candidates.append(dict(slot=slot, body=body, expanded=expanded,
                               satisfied=int(bool(left)) + int(bool(right)),
                               stored_length=len(body), expanded_length=len(expanded),
                               within_limits=len(body) <= 5 and len(expanded) <= 9))
    cost = dict(acquisition_cost, candidate_slots=len(candidates),
                expanded_instructions=sum(c['expanded_length'] for c in candidates),
                selection_slots=len(candidates))
    eligible = [c for c in candidates if c['within_limits'] and
                (arm != 'MASK' or all(op != 'ref' for op, _ in c['body']))]
    winner = min(eligible, key=lambda c: (-c['satisfied'], c['stored_length'], c['slot']))
    expanded, used = expand(winner['body'], chunks)
    output = ''.join(query['text'] if op == 'copy' else value for op, value in expanded)
    return dict(query=query, candidates=candidates, preselection_cost=cost,
                selected_slot=winner['slot'], used_references=used, output=output,
                executed_instructions=len(expanded))
