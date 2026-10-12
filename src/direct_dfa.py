"""Direct RE -> DFA (followpos algorithm with an internal end-marker). Independent of the NFA."""
from __future__ import annotations
from collections import deque
from .dfa import DFA
from .position_automaton import analyze
from .regex_ast import Cat, Lit, Node

TRAP = "TRAP"


def build_direct_dfa(ast: Node) -> DFA:
    root = Cat(ast, Lit(None))                 # append unique end-marker '#'
    a = analyze(root)
    marker = max(a.symbols)                    # marker is the last leaf, so it has the highest id
    alphabet = sorted({s for s in a.symbols.values() if s is not None})
    start = a.first
    names, queue, raw = {start: "S0"}, deque([start]), {}
    while queue:
        S = queue.popleft()
        for sym in alphabet:
            T = frozenset().union(*(a.follow[p] for p in S if a.symbols[p] == sym))
            raw[(S, sym)] = T
            if T and T not in names:
                names[T] = f"S{len(names)}"
                queue.append(T)
    need_trap = any(not T for T in raw.values())
    trans = {(names[S], sym): (names[T] if T else TRAP) for (S, sym), T in raw.items()}
    states = list(names.values())
    contents = {n: S for S, n in names.items()}
    if need_trap:
        states.append(TRAP)
        contents[TRAP] = frozenset()
        for sym in alphabet:
            trans[(TRAP, sym)] = TRAP
    accepting = frozenset(n for S, n in names.items() if marker in S)
    return DFA(states=states, alphabet=alphabet, start="S0", accepting=accepting,
               transitions=trans, contents=contents, trap=TRAP if need_trap else None, analysis=a)
