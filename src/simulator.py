"""NFA / DFA string simulators (own transition logic; Python's `re` is never used)."""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import product
from .nfa import skey


@dataclass
class Step:
    index: int
    symbol: str
    current: list
    next: list
    remaining: str
    explanation: str
    used: list = field(default_factory=list)  # (src, symbol, dst)


@dataclass
class SimResult:
    kind: str
    accepted: bool
    steps: list
    start: str
    final: list


def simulate_nfa(nfa, text: str) -> SimResult:
    active, steps = frozenset([nfa.start]), []
    for i, ch in enumerate(text, 1):
        nxt, used = set(), []
        for s in sorted(active, key=skey):
            for t in sorted(nfa.targets(s, ch), key=skey):
                nxt.add(t)
                used.append((s, ch, t))
        if not active:
            why = "No active states remain, so nothing can follow."
        elif not nxt:
            why = f"No active state has a transition on '{ch}'; the active set becomes empty."
        else:
            why = f"Follow every '{ch}' transition from all active states."
        steps.append(Step(i, ch, sorted(active, key=skey), sorted(nxt, key=skey), text[i:], why, used))
        active = frozenset(nxt)
    return SimResult("NFA", bool(active & nfa.accepting), steps, nfa.start, sorted(active, key=skey))


def simulate_dfa(dfa, text: str) -> SimResult:
    cur, steps, dead = dfa.start, [], False
    for i, ch in enumerate(text, 1):
        if ch not in dfa.alphabet:
            steps.append(Step(i, ch, [cur], [], text[i - 1:],
                              f"'{ch}' is not in the alphabet, so no transition exists. Input rejected."))
            dead = True
            break
        nxt = dfa.transitions[(cur, ch)]
        why = f"Exactly one transition: {cur} --{ch}--> {nxt}."
        if nxt == dfa.trap:
            why += " This is the trap state; no string can be accepted from here."
        steps.append(Step(i, ch, [cur], [nxt], text[i:], why, [(cur, ch, nxt)]))
        cur = nxt
    return SimResult("DFA", (not dead) and cur in dfa.accepting, steps, dfa.start, [] if dead else [cur])


def languages_agree(nfa, dfa, max_len: int = 6, cap: int = 20000):
    """Compare NFA and DFA on all strings up to max_len (shrinks automatically). Returns (agree, checked_len, counterexample)."""
    alpha = nfa.alphabet
    while max_len > 0 and sum(len(alpha) ** k for k in range(max_len + 1)) > cap:
        max_len -= 1
    for n in range(max_len + 1):
        for tup in product(alpha, repeat=n):
            w = "".join(tup)
            if simulate_nfa(nfa, w).accepted != simulate_dfa(dfa, w).accepted:
                return False, max_len, w
    return True, max_len, None
