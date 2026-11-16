"""Invented package; no production worksheet, Owner text or hidden gold."""
from hashlib import sha256
import json
from pathlib import Path

from packages.sentence_revision import State
from packages.sentence_revision.arms import Example
from packages.sentence_revision.evaluator import GoldCase
from packages.sentence_revision.runner import PublicCase
from tests.sentence_revision_c_fixture import fixtures


def encode(value):
    # Deliberately noncanonical: external commitment is the actual file bytes.
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')


def fixture_cases():
    cases = []
    for i, old in enumerate(fixtures()):
        def extend(state):
            return State(state.buffer + ('ABCD'[i],), state.cursor, state.selection, state.clipboard)
        pub = old.public
        new = PublicCase(f'R{i + 1:02d}', 'SYNTHETIC initial only',
                         tuple(Example(extend(x.before), extend(x.after)) for x in pub.initial),
                         extend(pub.correction_input), tuple(map(extend, pub.unseen_inputs)))
        cases.append(GoldCase(new, 'SYNTHETIC correction only', extend(old.correction_output),
                             tuple(map(extend, old.unseen_outputs)), old.intended_role))
    return tuple(cases)


def documents():
    first, correction, hidden = {}, {}, {}
    for case in fixture_cases():
        p = case.public
        key = p.rule_id
        first[key] = {'intended_case_role': case.intended_role, 'initial_text': p.text,
                      'initial_examples': [dict(x.record(), example_id=f'{key}-{i + 1:02d}')
                                           for i, x in enumerate(p.initial)]}
        correction[key] = {'correction_text': case.correction_text,
                           'correction_example': dict(Example(p.correction_input, case.correction_output).record(),
                                                      example_id=f'{key}-03'),
                           'custody': 'invented local test'}
        roles = ('unseen_related', 'unseen_previous_application', 'unseen_near_counterexample')
        hidden[key] = {'intended_rule_id': 'IGNORED-METADATA', 'intended_rule_ast': ['NOT', 'A', 'PROGRAM'],
                       'unseen': [{'example_id': f'{key}-{i + 4:02d}', 'role': roles[i],
                                   'before': x.record(), 'gold_after': y.record()}
                                  for i, (x, y) in enumerate(zip(p.unseen_inputs, case.unseen_outputs))]}
    return first, correction, hidden


def write_package(directory, docs=None, edit_manifest=None):
    directory = Path(directory)
    directory.mkdir()
    names = ('public-initial.json', 'disclosure-corrections.json', 'evaluator-only-unseen.json')
    hashes = {}
    for name, value in zip(names, documents() if docs is None else docs):
        raw = encode(value)
        (directory / name).write_bytes(raw)
        hashes[name] = sha256(raw).hexdigest()
    manifest = {'schema': 'synthetic-private-package/1', 'status': 'synthetic_only',
                'frozen_at': 'synthetic-before-test',
                'source_pin': {'accepted_commit': '3f60aac8de70af9e9575d25bc72009b0c30d89f6',
                               'source_lock_sha256': '3d31660fe094cb00c83c4542aed1c8f98c222d4c5d792006d8f26f9e31813f96',
                               'grammar_sha256': 'ebf86948879d0dc27d66467ce4ff710bc7befbdb25ab899db15553c13eb92758'},
                'files_sha256': hashes, 'choices_sha256': 'synthetic-opaque', 'texts_sha256': 'synthetic-opaque',
                'split': {'initial': 8, 'correction': 4, 'unseen': 12},
                'presentation_order': ['R01', 'R02', 'R03', 'R04'],
                'structural_check': 'synthetic', 'structural_note': 'not official',
                'provenance': 'synthetic', 'custody': 'synthetic',
                'official_predictions': 'not_run', 'official_scoring': 'not_run', 'production_run': None}
    if edit_manifest:
        edit_manifest(manifest)
    raw = encode(manifest)
    (directory / 'manifest.json').write_bytes(raw)
    return sha256(raw).hexdigest()
