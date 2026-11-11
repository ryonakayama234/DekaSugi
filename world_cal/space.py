"""Typed AST evaluator and canonical serialization; no learned BRANCH inventory."""
import json
from dataclasses import dataclass
from .world import World

class ASTFault(ValueError):
    pass

@dataclass(frozen=True)
class Node:
    kind: str
    args: tuple = ()

    def canonical(self) -> str:
        def encode(x):
            if isinstance(x, Node): return [x.kind, *[encode(y) for y in x.args]]
            if isinstance(x, (list, tuple)): return [encode(y) for y in x]
            return x
        return json.dumps(encode(self), ensure_ascii=False, separators=(",", ":"))

    def size(self):
        return 1 + sum(x.size() for x in self.args if isinstance(x, Node))

    def depth(self):
        return 1 + max((x.depth() for x in self.args if isinstance(x, Node)), default=0)

def validate(node: Node, *, predicate_depth=0):
    if not isinstance(node, Node) or node.size() > 64 or node.depth() > 8:
        raise ASTFault("AST bounds")
    if node.kind not in ("ATOM", "SEQ", "BIND", "COMPARE", "BRANCH", "FEATURE", "CONST", "VAR"):
        raise ASTFault("unknown node kind")
    if node.kind == "COMPARE" and predicate_depth >= 3:
        raise ASTFault("predicate depth exceeded")
    for sub in node.args:
        if isinstance(sub, Node):
            validate(sub, predicate_depth=predicate_depth + (node.kind == "COMPARE"))
    return node

def enumerate_unique(nodes):
    seen = set()
    for node in sorted((validate(x) for x in nodes), key=lambda x: (x.size(), x.canonical())):
        if node.canonical() not in seen:
            seen.add(node.canonical())
            yield node

def eval_expr(node: Node, world: World, env=()):
    validate(node)
    if node.kind == "CONST": return node.args[0]
    if node.kind == "VAR":
        index = node.args[0]
        if not isinstance(index, int) or index < 0 or index >= len(env):
            raise ASTFault("de Bruijn index out of scope")
        return env[-index-1]
    if node.kind == "FEATURE":
        name = node.args[0]
        obs = world.observe()
        if name == "LENGTH": return len(obs["buffer"])
        if name == "CURSOR": return obs["cursor"]
        if name == "SELECTION_LENGTH":
            return abs(obs["selection"][0] - obs["selection"][1]) if obs["selection"] else 0
        if name == "COUNT":
            symbol = eval_expr(node.args[1], world, env)
            if symbol not in world.alphabet: raise ASTFault("symbol outside live alphabet")
            return obs["buffer"].count(symbol)
        if name == "CURSOR_SYMBOL":
            return obs["buffer"][obs["cursor"]] if obs["cursor"] < len(obs["buffer"]) else None
        if name == "CLIPBOARD": return obs["clipboard"]
        if name == "LAST_EVENT": return obs["last_event"]
        raise ASTFault("unknown feature")
    if node.kind == "COMPARE":
        op, left, right = node.args
        a, b = eval_expr(left, world, env), eval_expr(right, world, env)
        if op == "EQ": return a == b
        if op in ("LT", "LE") and type(a) is type(b) and isinstance(a, int):
            return a < b if op == "LT" else a <= b
        raise ASTFault("invalid compare")
    if node.kind == "BIND":
        _, value, body = node.args
        return eval_expr(body, world, env + (eval_expr(value, world, env),))
    if node.kind == "BRANCH":
        condition, yes, no = node.args
        if not isinstance(eval_expr(condition, world, env), bool):
            raise ASTFault("nonbool predicate")
        return eval_expr(yes if eval_expr(condition, world, env) else no, world, env)
    if node.kind == "SEQ":
        for x in node.args:
            eval_expr(x, world, env)
        return None
    if node.kind == "ATOM":
        name = node.args[0]
        value = eval_expr(node.args[1], world, env) if len(node.args) > 1 else None
        world.step((name, value))
        return None
    raise ASTFault("unsupported expression")
