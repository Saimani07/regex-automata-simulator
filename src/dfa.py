"""Complete deterministic automaton data structure."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DFA:
    states: list
    alphabet: list
    start: str
    accepting: frozenset
    transitions: dict  # (state, symbol) -> state   (exactly one per pair)
    contents: dict     # state name -> frozenset of positions it represents
    trap: Optional[str] = None
    analysis: Any = None

    def edges(self):
        from .nfa import skey
        return sorted(((s, a, t) for (s, a), t in self.transitions.items()),
                      key=lambda e: (skey(e[0]), e[1]))

    @property
    def transition_count(self):
        return len(self.transitions)
