"""Public-input collector. No gold/scorer imports and no evaluation feedback API."""
from dataclasses import dataclass
import json

from .arms import ARMS, Case, Example, _text
from .artifacts import Artifacts, attributed, digest
from .foundation import BudgetExceeded, Fault, Meter, State, validate_input

STAGES = ("before", "after")


@dataclass(frozen=True, slots=True)
class PublicCase:
    rule_id: str
    text: str
    initial: tuple[Example, Example]
    correction_input: State
    unseen_inputs: tuple[State, State, State]

    def record(self):
        if type(self) is not PublicCase:
            raise Fault("exact PublicCase required")
        _text(self.rule_id, 128)
        _text(self.text, 4096)
        if (type(self.initial) is not tuple or len(self.initial) != 2
                or any(type(x) is not Example for x in self.initial)
                or type(self.unseen_inputs) is not tuple or len(self.unseen_inputs) != 3):
            raise Fault("public input shape")
        inputs = self.inputs()
        for state in inputs:
            validate_input(state)
        if len(set(inputs)) != 6:
            raise Fault("overlapping public input states")
        return {"rule_id": self.rule_id, "text": self.text,
                "initial": [x.record() for x in self.initial],
                "correction_input": self.correction_input.record(),
                "unseen_inputs": [x.record() for x in self.unseen_inputs]}

    def inputs(self):
        return (*[x.before for x in self.initial], self.correction_input, *self.unseen_inputs)


def slot(case_index, arm, stage, probe):
    return f"c{case_index}-{arm}-{stage}-p{probe}"


def schedule():
    return [{"slot": slot(c, a, s, p), "case": c, "arm": a, "stage": s,
             "probe": p, "status": "not_run"}
            for c in range(4) for a in ARMS for s in STAGES for p in range(6)]


class Episode:
    def __init__(self, public, case_index, *, meter, store):
        if type(public) is not PublicCase or type(meter) is not Meter or type(store) is not Artifacts:
            raise Fault("typed public collector inputs required")
        if store.meter is not meter or type(case_index) is not int or not 0 <= case_index < 4:
            raise Fault("meter identity/case index")
        self.public, self.case_index = public, case_index
        self.meter, self.store = meter, store
        self.cases, self.snapshots = {}, {}
        self.state = "new"
        with attributed(meter, f"case{case_index}/prepare"), meter.phase("public-prepare"):
            self.public_record = public.record()
            meter.checkpoint(self.public_record)

    def roots(self, extra=None):
        return (self.public_record, [x._data for x in self.cases.values()], self.snapshots, extra)

    def check(self, extra=None):
        with attributed(self.meter, f"case{self.case_index}/overhead"), self.meter.phase("collector-check"):
            self.meter.checkpoint(self.roots(extra))

    def _snapshot(self, arm, stage):
        with attributed(self.meter, f"case{self.case_index}/{arm}/{stage}/save"):
            raw = self.cases[arm].save()
        self.check(raw)
        # Parsing is separate from learner operations and is timed explicitly.
        with attributed(self.meter, f"case{self.case_index}/{arm}/{stage}/snapshot"), self.meter.phase("snapshot-decode"):
            value = json.loads(raw)
            self.meter.checkpoint(self.roots((raw, value)))
        name = f"snapshot-c{self.case_index}-{arm}-{stage}.json"
        self.store.write(name, value, retained=self.roots(raw))
        self.snapshots[(arm, stage)] = raw

    def _predict(self, arm, stage):
        for p, input_state in enumerate(self.public.inputs()):
            key = slot(self.case_index, arm, stage, p)
            self.check(input_state)
            with attributed(self.meter, f"case{self.case_index}/{arm}/{stage}/p{p}"):
                prediction = self.cases[arm].predict(input_state)
            with attributed(self.meter, f"case{self.case_index}/{arm}/{stage}/record"), self.meter.phase("prediction-record"):
                row = {"slot": key, "case": self.case_index, "arm": arm, "stage": stage,
                       "probe": p, "input": input_state.record(), "input_sha256": digest(input_state.record()), **prediction}
                self.meter.checkpoint(self.roots(row))
            self.store.write("row-" + key + ".json", row, retained=self.roots(row))
        # Stronger than comparing selected IDs: prediction must preserve entire saved history.
        with attributed(self.meter, f"case{self.case_index}/{arm}/{stage}/immutability"):
            if self.cases[arm].save() != self.snapshots[(arm, stage)]:
                raise Fault("prediction changed case bytes")

    def before(self):
        if self.state != "new":
            raise Fault("before collection cannot repeat")
        self.state = "collecting-before"
        for arm in ARMS:
            self.check()
            with attributed(self.meter, f"case{self.case_index}/{arm}/build"):
                self.cases[arm] = Case.create(arm, self.public.rule_id, self.public.text,
                                               self.public.initial, meter=self.meter)
            self._snapshot(arm, "before")
            self._predict(arm, "before")
        names = ["row-" + slot(self.case_index, a, "before", p) + ".json"
                 for a in ARMS for p in range(6)]
        names += [f"snapshot-c{self.case_index}-{a}-before.json" for a in ARMS]
        with attributed(self.meter, f"case{self.case_index}/pre-disclosure-seal"), self.meter.phase("pre-disclosure-seal"):
            seal = {"public_sha256": digest(self.public_record),
                    "artifacts": {n: self.store.index[n] for n in names}}
            self.meter.checkpoint(self.roots(seal))
        self.store.write(f"before-seal-c{self.case_index}.json", seal, retained=self.roots(seal))
        self.state = "before-sealed"

    def after(self, text, correction):
        if self.state != "before-sealed":
            raise Fault("correction requires completed persisted before seal")
        try:
            seal = self.store.read(f"before-seal-c{self.case_index}.json", retained=self.roots())
            if seal["public_sha256"] != digest(self.public_record):
                raise Fault("changed public plan")
            for name, meta in seal["artifacts"].items():
                if self.store.index.get(name) != meta:
                    raise Fault("changed pre-disclosure index")
                self.store.read(name, retained=self.roots())
            with attributed(self.meter, f"case{self.case_index}/disclosure"), self.meter.phase("disclosure"):
                _text(text, 4096)
                if type(correction) is not Example or correction.before != self.public.correction_input:
                    raise Fault("wrong disclosed input")
                self.meter.checkpoint(self.roots(correction.record()))
            self.state = "collecting-after"
            for arm in ARMS:
                self.check()
                with attributed(self.meter, f"case{self.case_index}/{arm}/update"):
                    self.cases[arm].correct(text, correction)
                self._snapshot(arm, "after")
                self._predict(arm, "after")
            self.state = "complete"
        except (BudgetExceeded, Fault):
            self.state = "stopped"
            raise
