"""Appendix A deterministic editor. The truth callback belongs to an isolated evaluator."""
from dataclasses import dataclass
from typing import Callable

OPS = ("MOVE_LEFT", "MOVE_RIGHT", "INSERT", "DELETE_BACK", "DELETE_RIGHT",
       "SET_ANCHOR", "EXTEND_LEFT", "EXTEND_RIGHT", "COPY", "PASTE", "CLEAR_SELECTION")
MAX_LENGTH = 16

@dataclass(frozen=True)
class State:
    buffer: tuple[str, ...]
    cursor: int = 0
    selection: tuple[int, int] | None = None
    clipboard: tuple[str, ...] = ()
    last_event: str | None = None

class World:
    def __init__(self, alphabet: tuple[str, ...], verifier: Callable[[tuple[str, ...]], bool] | None = None,
                 horizon: int = 24):
        if len(alphabet) != 4 or len(set(alphabet)) != 4 or horizon < 1:
            raise ValueError("invalid alphabet/horizon")
        self.alphabet, self.__verifier, self.horizon = tuple(alphabet), verifier, horizon
        self.state = State(())
        self.calls = 0
        self.done = False
        self.success = False

    def reset(self, instance):
        if len(instance) > MAX_LENGTH or any(x not in self.alphabet for x in instance):
            raise ValueError("invalid initial buffer")
        self.state = State(tuple(instance))
        self.calls = 0
        self.success = bool(self.__verifier and self.__verifier(self.state.buffer))
        self.done = self.success
        return self.observe()

    def observe(self):
        s = self.state
        return {"buffer": s.buffer, "cursor": s.cursor, "selection": s.selection,
                "clipboard": s.clipboard, "last_event": s.last_event}

    def legal_actions(self):
        # Appendix A: an inapplicable legitimate action is still issuable.
        return tuple((op, sym) for op in OPS for sym in (self.alphabet if op == "INSERT" else (None,)))

    def step(self, action):
        if self.done:
            return self.observe(), True, self.success, "ABSORBED"
        self.calls += 1
        s = self.state
        op, arg = action if isinstance(action, tuple) and len(action) == 2 else (action, None)
        buf, cur, sel, clip = s.buffer, s.cursor, s.selection, s.clipboard
        event = "VALID"
        if op not in OPS or (op == "INSERT" and arg not in self.alphabet) or (op != "INSERT" and arg is not None):
            event = "ACTION_FAULT"
        elif op == "MOVE_LEFT":
            if cur: cur -= 1
            else: event = "NO_OP_PRECONDITION"
        elif op == "MOVE_RIGHT":
            if cur < len(buf): cur += 1
            else: event = "NO_OP_PRECONDITION"
        elif op == "SET_ANCHOR":
            sel = (cur, cur)
        elif op == "EXTEND_LEFT":
            if sel and sel[1] > 0: sel = (sel[0], sel[1] - 1)
            else: event = "NO_OP_PRECONDITION"
        elif op == "EXTEND_RIGHT":
            if sel and sel[1] < len(buf): sel = (sel[0], sel[1] + 1)
            else: event = "NO_OP_PRECONDITION"
        elif op == "CLEAR_SELECTION":
            if sel is None: event = "NO_OP_PRECONDITION"
            sel = None
        elif op == "COPY":
            if sel and sel[0] != sel[1]:
                a, b = sorted(sel)
                clip = buf[a:b]
            else: event = "NO_OP_PRECONDITION"
        elif op in ("INSERT", "PASTE"):
            value = (arg,) if op == "INSERT" else clip
            a, b = sorted(sel) if sel is not None else (cur, cur)
            if not value or len(buf) - (b-a) + len(value) > MAX_LENGTH:
                event = "NO_OP_PRECONDITION"
            else:
                buf = buf[:a] + value + buf[b:]
                cur, sel = a + len(value), None
        elif op == "DELETE_BACK":
            if cur:
                buf = buf[:cur-1] + buf[cur:]
                cur -= 1
                sel = None
            else: event = "NO_OP_PRECONDITION"
        elif op == "DELETE_RIGHT":
            if cur < len(buf):
                buf = buf[:cur] + buf[cur+1:]
                sel = None
            else: event = "NO_OP_PRECONDITION"
        self.state = State(buf, cur, sel, clip, event)
        self.success = bool(self.__verifier and self.__verifier(buf))
        self.done = self.success or self.calls >= self.horizon
        return self.observe(), self.done, self.success, event

def rename(state: State, mapping: dict[str, str]) -> State:
    return State(tuple(mapping[x] for x in state.buffer), state.cursor, state.selection,
                 tuple(mapping[x] for x in state.clipboard), state.last_event)
