"""Read-only training-side reformation; no prediction or old evaluator imports."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from packages.symbol_bootstrap import Budget, Learner, ResourceStop, canonical, digest

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / 'experiments/SYMBOL-REFORMATION-1/plan.md'
PLAN_SHA = '0a5d3bb4f3e43f474c6d293ce2c11e8e91dbc949b855a4f87f991922c07f75a8'
ARCHIVE = ROOT / 'experiments/SYMBOL-BOOTSTRAP-1/runs/local-02/evidence.zip'
ARCHIVE_SHA = 'd050df3d1caa06203036b15c20e2a6881581133f1ad51d9ed5756666ee1d54e5'
STATE_SHA = 'b28875765b21e0b3603fb750a4fa8e7283d9322efd2b3b286de708aba4cdb7fd'
LIMITS = dict(episode_chars=32, episodes=54, chunk_chars=8, chunks=4096,
              rules=4096, variables=2, variable_chars=6, input_literals=8,
              output_literals=8, output_references=4, output_atoms=16,
              expanded_chars=32, formation_attempts_per_episode=16384,
              output_search_nodes_per_pair=4096, operations_total=20_000_000,
              wall_seconds=120, cpu_seconds=120, artifact_bytes=50_000_000,
              events=65536, fit_cache=147456)
ARMS = ('FULL', 'NO-CHUNK')


def byte_cost(budget, kind, n):
    budget.tick(kind, (n + 1023) // 1024)


def json_cost(value, budget, kind):
    """Charge every JSON value and every key/string character; bound nesting."""
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if depth > 64:
            raise ValueError('JSON depth')
        budget.tick(kind, 1 + (len(item) if isinstance(item, str) else 0))
        if isinstance(item, dict):
            for key, val in item.items():
                budget.tick(kind, len(key))
                stack.append((val, depth+1))
        elif isinstance(item, (list, tuple)):
            stack.extend((v, depth+1) for v in item)


def encode(value, budget):
    json_cost(value, budget, 'serialize_json')
    data = (canonical(value)+'\n').encode()
    byte_cost(budget, 'encode_byte', len(data))
    return data


def load_input(budget):
    plan = PLAN.read_bytes()
    byte_cost(budget, 'input_byte', len(plan))
    if sha256(plan).hexdigest() != PLAN_SHA:
        raise ValueError('fixed plan changed')
    if ARCHIVE.stat().st_size > 50_000_000:
        raise ResourceStop('archive_bytes')
    archive = ARCHIVE.read_bytes()
    byte_cost(budget, 'input_byte', len(archive))
    if sha256(archive).hexdigest() != ARCHIVE_SHA:
        raise ValueError('source archive changed')
    # Read exactly this member. No report/history/result/old lock is decoded.
    with ZipFile(ARCHIVE) as z:
        if z.getinfo('states.json').file_size > 20_000_000:
            raise ResourceStop('state_bytes')
        data = z.read('states.json')
    byte_cost(budget, 'input_byte', len(data))
    if sha256(data).hexdigest() != STATE_SHA:
        raise ValueError('source state changed')
    states = json.loads(data)
    json_cost(states, budget, 'input_json')
    return {a: states[a] for a in ARMS}


def rows_of(states, budget):
    rows = states['FULL']['rows']
    if rows != states['NO-CHUNK']['rows'] or len(rows) != 54:
        raise ValueError('training ledgers differ')
    distinct = []
    seen = set()
    for i, (eid, text) in enumerate(rows):
        budget.tick('ledger', len(text)+1)
        if eid != f'E{i+1:03}' or not 0 < len(text) <= 32:
            raise ValueError('raw row contract')
        if text not in seen:
            seen.add(text)
            distinct.append([eid, text])
    if len(distinct) != 18 or [t for _, t in rows] != [t for _, t in distinct]*3:
        raise ValueError('expected 18 unique rows repeated three times')
    return distinct


def ast_of(rule):
    return dict(pattern=rule['pattern'], output=rule['output'])


def assess(learner, rule, rows, budget):
    result = []
    for eid, text in rows:
        budget.tick('fit_retention')
        if len(learner._fit_cache) >= LIMITS['fit_cache'] // 2:
            raise ResourceStop('fit_cache')
        status, match = learner._fit(rule, text)
        result.append(dict(row=eid, status=status, match=match))
    return result


def compare(arms, budget):
    full, nc = arms['FULL'], arms['NO-CHUNK']
    before_union = set(full['before']) | set(nc['before'])
    nc_after = set(nc['candidates'])
    unique = []
    for rid, candidate in full['candidates'].items():
        budget.tick('compare')
        if (rid not in before_union and rid not in nc_after
                and 'symbol' in candidate['routes'] and 'character' not in candidate['routes']):
            unique.append(rid)
    return dict(full_chunk_exclusive_new=unique,
                full_chunk_exclusive_supported=[r for r in unique if full['candidates'][r]['support'] >= 2],
                interpretation='training_candidate_formation_only_no_prediction_or_ability_claim')


def diagnose(states, budget):
    """Return isolated candidates/events; never call observe/predict or mutate states."""
    rows = rows_of(states, budget)
    json_cost(states, budget, 'state_digest')
    before_digest = digest(states)
    arms, trials, events = {}, [], []
    for arm in ARMS:
        state = states[arm]
        if state['arm'] != arm or len(state['chunks']) > 4096 or len(state['rules']) > 4096:
            raise ValueError('state bounds/arm')
        if arm == 'NO-CHUNK' and (state['chunks'] or state['fragments']):
            raise ValueError('NO-CHUNK has dictionary')
        for expansion, chunk in state['chunks'].items():
            budget.tick('chunk_validation', len(expansion))
            if (expansion != chunk['expansion'] or chunk['id'] != 'C-'+digest(expansion)[:16]
                    or not 2 <= len(expansion) <= 8 or chunk['created_at'] not in {e for e, _ in state['rows']}):
                raise ValueError('chunk provenance')
        learner = Learner(arm, '', budget)
        learner.chunks = copy.deepcopy(state['chunks'])
        candidates = {}
        for rid, rule in state['rules'].items():
            budget.tick('baseline_candidate')
            ast = ast_of(rule)
            if rid != rule['id'] or rid != 'R-'+digest(ast)[:16]:
                raise ValueError('old AST identity')
            candidates[rid] = dict(id=rid, ast=ast, baseline=True, routes=[], events=[],
                                   evidence=assess(learner, rule, rows, budget), status='candidate')
        arm_result = dict(before=sorted(candidates), candidates=candidates, pairs=[], cost={})
        arms[arm] = arm_result
        attempts = 0
        for i in range(1, len(rows)):
            for j in range(i):
                budget.tick('row_pair')
                old_id, old = rows[j]
                new_id, new = rows[i]
                arm_result['pairs'].append([old_id, new_id])
                for split in range(1, min(len(old), len(new))):
                    for symbolic in ((True, False) if arm == 'FULL' else (False,)):
                        attempts += 1
                        learner.tick('formation_attempt')
                        if attempts > LIMITS['formation_attempts_per_episode']:
                            raise ResourceStop('formation_attempts')
                        route = 'symbol' if symbolic else 'character'
                        if not symbolic:
                            budget.tick('character_token', 2*split)
                        formed = learner._pattern(old[:split], new[:split], symbolic)
                        trial = dict(id=f'T{len(trials)+1:05}', arm=arm, pair=[old_id, new_id],
                                     split=split, route=route, pattern_formed=formed is not None, events=[])
                        budget.tick('trial_retention')
                        trials.append(trial)
                        if formed is None:
                            continue
                        pattern, va, vb, spans, deps = formed
                        tokens = [learner.tokenize(t[:split]) for t in (old, new)] if symbolic else [[], []]
                        chunk_uses = []
                        for eid, tt in zip((old_id, new_id), tokens):
                            for token in tt:
                                if token['symbol']:
                                    chunk = state['chunks'][token['text']]
                                    chunk_uses.append(dict(row=eid, start=token['start'], end=token['end'],
                                                           id=chunk['id'], expansion=chunk['expansion'],
                                                           acquired_at=chunk['created_at']))
                        for output in learner._outputs(old[split:], new[split:], va, vb):
                            ast = json.loads(canonical(dict(pattern=pattern, output=output)))
                            json_cost(ast, budget, 'ast_identity')
                            rid = 'R-'+digest(ast)[:16]
                            if len(events) >= LIMITS['events']:
                                raise ResourceStop('events')
                            if rid in candidates and candidates[rid]['ast'] != ast:
                                raise ValueError('AST hash collision')
                            existed = rid in candidates
                            if not existed:
                                if len(candidates) >= LIMITS['rules']:
                                    raise ResourceStop('rules')
                                rule = dict(id=rid, **ast)
                                candidates[rid] = dict(id=rid, ast=ast, baseline=False, routes=[], events=[],
                                                       evidence=assess(learner, rule, rows, budget), status='candidate')
                            candidate = candidates[rid]
                            event_id = f'RF{len(events)+1:05}'
                            event = dict(id=event_id, arm=arm, trial=trial['id'], rule=rid,
                                         reformation_at='AFTER-E054', route=route, dependencies=deps,
                                         chunk_uses=chunk_uses,
                                         sources=[dict(row=eid, split=split, variable_spans=[s[k] for s in spans])
                                                  for k, eid in enumerate((old_id, new_id))],
                                         baseline_rediscovery=candidate['baseline'],
                                         already_formed=bool(candidate['events']))
                            json_cost(event, budget, 'event_retention')
                            events.append(event)
                            trial['events'].append(event_id)
                            candidate['events'].append(event_id)
                            if route not in candidate['routes']:
                                candidate['routes'].append(route)
        for c in candidates.values():
            counts = {s: sum(e['status'] == s for e in c['evidence'])
                      for s in ('support', 'failure', 'inapplicable')}
            budget.tick('support_aggregate', 18*3)
            c.update(counts)
        new = [r for r, c in candidates.items() if not c['baseline']]
        arm_result['after'] = sorted(candidates)
        arm_result['summary'] = dict(before=len(arm_result['before']), after=len(candidates), new=len(new),
                                     new_supported=sum(candidates[r]['support'] >= 2 for r in new),
                                     new_with_failure=sum(candidates[r]['failure'] > 0 for r in new),
                                     new_inapplicable_rows=sum(candidates[r]['inapplicable'] for r in new),
                                     attempts=attempts, pairs=len(arm_result['pairs']),
                                     existing_rediscovery_events=sum(e['arm']==arm and e['baseline_rediscovery'] for e in events),
                                     repeated_formation_events=sum(e['arm']==arm and e['already_formed'] for e in events),
                                     cross_route_asts=sum(len(c['routes'])==2 for c in candidates.values()))
        arm_result['cost'] = dict(learner.cost)
    comparison = compare(arms, budget)
    json_cost(states, budget, 'state_digest')
    if digest(states) != before_digest:
        raise ValueError('old states mutated')
    return dict(schema='symbol-reformation/1', rows=rows, state_before=before_digest,
                state_after=before_digest, arms=arms, comparison=comparison), trials, events
