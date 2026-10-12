"""Nullable/firstpos/lastpos/followpos analysis and the Glushkov (position) NFA."""
from __future__ import annotations
from dataclasses import dataclass
from .nfa import NFA
from .regex_ast import Alt, Cat, Lit, Plus, Star, Node


@dataclass
class Analysis:
    symbols: dict   # position -> symbol (None for the end-marker)
    nullable: bool
    first: frozenset
    last: frozenset
    follow: dict    # position -> frozenset(positions)


def analyze(root: Node) -> Analysis:
    symbols, follow = {}, {}

    def walk(n):
        if isinstance(n, Lit):
            p = len(symbols) + 1          # unique id per literal occurrence, left to right
            symbols[p] = n.symbol
            follow[p] = set()
            return False, frozenset([p]), frozenset([p])
        if isinstance(n, (Alt, Cat)):
            n1, f1, l1 = walk(n.left)
            n2, f2, l2 = walk(n.right)
            if isinstance(n, Alt):
                return n1 or n2, f1 | f2, l1 | l2
            for p in l1:                  # concatenation: lastpos(left) is followed by firstpos(right)
                follow[p] |= f2
            return n1 and n2, ((f1 | f2) if n1 else f1), ((l1 | l2) if n2 else l2)
        nl, f, l = walk(n.child)
        if isinstance(n, (Star, Plus)):   # repetition: lastpos is followed by firstpos
            for p in l:
                follow[p] |= f
        return (nl if isinstance(n, Plus) else True), f, l

    nullable, first, last = walk(root)
    return Analysis(symbols, nullable, first, last, {p: frozenset(v) for p, v in follow.items()})


def build_glushkov_nfa(ast: Node) -> NFA:
    """Epsilon-free NFA: state q0 plus one state qi per literal position i."""
    a = analyze(ast)
    name = lambda p: f"q{p}"
    trans = {}

    def add(src, p):
        trans.setdefault((src, a.symbols[p]), set()).add(name(p))

    for p in a.first:
        add("q0", p)
    for p, qs in a.follow.items():
        for q in qs:
            add(name(p), q)
    accepting = {name(p) for p in a.last} | ({"q0"} if a.nullable else set())
    return NFA(states=["q0"] + [name(p) for p in sorted(a.symbols)],
               alphabet=sorted(set(a.symbols.values())), start="q0",
               accepting=frozenset(accepting),
               transitions={k: frozenset(v) for k, v in trans.items()}, analysis=a)
