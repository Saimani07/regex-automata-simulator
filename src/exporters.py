"""Table rows, CSV and JSON exports built from the real automata."""
from __future__ import annotations
import csv, io, json
from .nfa import skey

NFA_COLS = ["State", "Input Symbol", "Destination States"]
DFA_COLS = ["DFA State", "Input Symbol", "Destination State", "Accepting?"]


def nfa_rows(nfa):
    return [{"State": s, "Input Symbol": a,
             "Destination States": ", ".join(sorted(nfa.targets(s, a), key=skey)) or "∅"}
            for s in nfa.states for a in nfa.alphabet]


def dfa_rows(dfa):
    return [{"DFA State": s, "Input Symbol": a, "Destination State": dfa.transitions[(s, a)],
             "Accepting?": "Yes" if s in dfa.accepting else "No"}
            for s in dfa.states for a in dfa.alphabet]


def rows_to_csv(rows) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def automaton_to_dict(auto, kind: str) -> dict:
    d = {"type": kind, "states": list(auto.states), "alphabet": list(auto.alphabet), "start": auto.start,
         "accepting": sorted(auto.accepting, key=skey), "has_epsilon_transitions": False}
    if kind == "NFA":
        d["construction"] = "Glushkov position automaton (epsilon-free)"
        d["transitions"] = [{"from": s, "symbol": a, "to": sorted(ts, key=skey)}
                            for (s, a), ts in sorted(auto.transitions.items(), key=lambda kv: (skey(kv[0][0]), kv[0][1]))]
    else:
        d["construction"] = "Direct followpos construction (complete DFA)"
        d["transitions"] = [{"from": s, "symbol": a, "to": t} for s, a, t in auto.edges()]
        d["state_positions"] = {k: sorted(v) for k, v in auto.contents.items()}
        d["trap_state"] = auto.trap
    return d


def automaton_to_json(auto, kind: str) -> str:
    return json.dumps(automaton_to_dict(auto, kind), indent=2, ensure_ascii=False)
