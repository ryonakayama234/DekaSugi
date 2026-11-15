"""Deliberately repetitive invented fixtures, never a production case table."""
from packages.sentence_revision import State
from packages.sentence_revision.arms import Example
from packages.sentence_revision.evaluator import GoldCase
from packages.sentence_revision.runner import PublicCase


def fixtures():
    result = []
    for i in range(4):
        alphabet = "ABCD"[i:] + "ABCD"[:i]
        trans = str.maketrans("ABCD", alphabet)
        s = lambda text: State(tuple(text.translate(trans)), 2)
        initial = (Example(s("ABCD"), s("ABCD")), Example(s("AAAA"), State(tuple("AAA".translate(trans)), 2)))
        correction = s("BBBD" if i == 3 else "ABAC")
        unseen = tuple(s(x) for x in ("DDAA", "AABA", "CBCD"))
        erase = lambda state: State(state.buffer[:2] + state.buffer[3:], 2)
        target = lambda state: state.buffer[2] == state.buffer[0 if i == 3 else -1]
        pub = PublicCase(f"invented-{i}", "artificial initial text", initial, correction, unseen)
        result.append(GoldCase(pub, "artificial pre-fixed clarification", erase(correction) if target(correction) else correction,
                               tuple(erase(x) if target(x) else x for x in unseen),
                               "confirmation" if i == 3 else "revise"))
    return tuple(result)
