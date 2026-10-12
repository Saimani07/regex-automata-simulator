"""Epsilon-free NFA data structure."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


def skey(name: str):
    """Natural sort key so q2 comes before q10."""
    return (len(name), name)


@dataclass
class NFA:
    states: list
    alphabet: list
    start: str
    accepting: frozenset
    transitions: dict  # (state, symbol) -> frozenset(states)
    analysis: Any = None

    def targets(self, state, symbol):
        return self.transitions.get((state, symbol), frozenset())

    def edges(self):
        return sorted(((s, a, t) for (s, a), ts in self.transitions.items() for t in ts),
                      key=lambda e: (skey(e[0]), e[1], skey(e[2])))

    @property
    def transition_count(self):
        return len(self.edges())

    def max_branching(self):
        return max((len(v) for v in self.transitions.values()), default=0)
