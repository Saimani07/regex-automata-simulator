"""Syntax-tree node types for regular expressions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union


@dataclass(frozen=True)
class Lit:
    symbol: Optional[str]  # None = internal end-marker (never an input symbol)


@dataclass(frozen=True)
class Alt:
    left: "Node"
    right: "Node"


@dataclass(frozen=True)
class Cat:
    left: "Node"
    right: "Node"


@dataclass(frozen=True)
class Star:
    child: "Node"


@dataclass(frozen=True)
class Plus:
    child: "Node"


@dataclass(frozen=True)
class Opt:
    child: "Node"


Node = Union[Lit, Alt, Cat, Star, Plus, Opt]


def pretty(n: Node) -> str:
    """Readable parsed representation, e.g. Cat(Lit(a), Star(Alt(Lit(b), Lit(c))))."""
    if isinstance(n, Lit):
        return f"Lit({n.symbol if n.symbol is not None else '#'})"
    if isinstance(n, (Alt, Cat)):
        return f"{type(n).__name__}({pretty(n.left)}, {pretty(n.right)})"
    return f"{type(n).__name__}({pretty(n.child)})"


def _walk(n: Node):
    yield n
    for c in (getattr(n, "left", None), getattr(n, "right", None), getattr(n, "child", None)):
        if c is not None:
            yield from _walk(c)


def alphabet_of(n: Node) -> list:
    return sorted({x.symbol for x in _walk(n) if isinstance(x, Lit) and x.symbol is not None})


def operators_used(n: Node) -> list:
    names = {Alt: "Alternation |", Cat: "Concatenation (implicit)", Star: "Kleene star *",
             Plus: "One-or-more +", Opt: "Optional ?"}
    found = {names[type(x)] for x in _walk(n) if type(x) in names}
    return [v for v in names.values() if v in found]
