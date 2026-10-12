"""Graphviz DOT generation (computed from the real automata) and optional rendering."""
from __future__ import annotations
from collections import defaultdict
from .nfa import skey


def _esc(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def automaton_dot(auto, kind: str, active=(), used=()) -> str:
    fill, line = ("#DBEAFE", "#1D4ED8") if kind == "NFA" else ("#DCFCE7", "#15803D")
    active, used = set(active), set(used)
    legend = (f"{kind} legend: arrow from dot = start state | double circle = accepting state | "
              "yellow = active state (simulation)")
    out = ["digraph G {", "rankdir=LR;", 'bgcolor="white";', f'label="{_esc(legend)}"; labelloc=b; fontsize=11;',
           'node [fontname="Helvetica", style=filled];', 'edge [fontname="Helvetica"];',
           '__start [shape=point, width=0.2, label="", style=solid];']
    for s in sorted(auto.states, key=skey):
        shape = "doublecircle" if s in auto.accepting else "circle"
        attrs = [f"shape={shape}", f'fillcolor="{fill}"', f'color="{line}"']
        if getattr(auto, "trap", None) == s:
            attrs = [f"shape={shape}", 'fillcolor="#E5E7EB"', 'color="#6B7280"', 'style="filled,dashed"']
        if s in active:
            attrs += ['fillcolor="#FDE047"', "penwidth=3"]
        out.append(f'"{_esc(s)}" [{", ".join(attrs)}];')
    out.append(f'__start -> "{_esc(auto.start)}" [color="{line}"];')
    grouped = defaultdict(list)
    for s, a, t in auto.edges():
        grouped[(s, t)].append(a)
    for (s, t), syms in grouped.items():
        hot = any((s, a, t) in used for a in syms)
        style = 'color="#DC2626", penwidth=3' if hot else f'color="{line}"'
        out.append(f'"{_esc(s)}" -> "{_esc(t)}" [label="{_esc(",".join(sorted(syms)))}", {style}];')
    out.append("}")
    return "\n".join(out)


def render_bytes(dot: str, fmt: str):
    """SVG/PNG bytes if the Graphviz 'dot' program is installed, otherwise None."""
    try:
        import graphviz
        return graphviz.Source(dot).pipe(format=fmt)
    except Exception:
        return None
