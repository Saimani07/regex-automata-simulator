import csv, io, json, re
from itertools import product
import pytest
from src.parser import parse_regex
from src.position_automaton import build_glushkov_nfa
from src.direct_dfa import build_direct_dfa
from src.simulator import simulate_nfa, simulate_dfa, languages_agree
from src.examples import EXAMPLES
from src.exporters import (nfa_rows, dfa_rows, rows_to_csv, automaton_to_dict, automaton_to_json,
                           NFA_COLS, DFA_COLS)
from src.visualization import automaton_dot

PATTERNS = [e["regex"] for e in EXAMPLES] + ["a?b*", "(a|b)+a?", "((a|b)c)*", "(a*)*", "(a?)+", "a(b|c)?d*", "(ab)+|c"]


def build(rx):
    ast = parse_regex(rx)
    return build_glushkov_nfa(ast), build_direct_dfa(ast)


@pytest.mark.parametrize("rx", PATTERNS)
def test_against_python_re_oracle(rx):
    nfa, dfa = build(rx)
    alphabet = nfa.alphabet + ["z"]
    for n in range(6):
        for t in product(alphabet, repeat=n):
            w = "".join(t)
            expected = re.fullmatch(rx, w) is not None   # oracle only; never used to build/simulate
            assert simulate_nfa(nfa, w).accepted == expected, (rx, w)
            assert simulate_dfa(dfa, w).accepted == expected, (rx, w)


@pytest.mark.parametrize("ex", EXAMPLES, ids=lambda e: e["regex"])
def test_example_samples(ex):
    nfa, dfa = build(ex["regex"])
    for w in ex["accept"]:
        assert simulate_nfa(nfa, w).accepted and simulate_dfa(dfa, w).accepted, w
    for w in ex["reject"]:
        assert not simulate_nfa(nfa, w).accepted and not simulate_dfa(dfa, w).accepted, w


def test_empty_string_and_trace():
    nfa, dfa = build("a*")
    assert simulate_nfa(nfa, "").accepted and simulate_dfa(dfa, "").accepted
    nfa, dfa = build("a+")
    assert not simulate_nfa(nfa, "").accepted and not simulate_dfa(dfa, "").accepted


def test_nfa_active_sets():
    nfa, _ = build("(a|b)*abb")
    r = simulate_nfa(nfa, "abb")
    assert r.steps[0].current == ["q0"] and r.steps[0].next == ["q1", "q3"]
    assert "q5" in r.final and r.accepted
    r = simulate_nfa(nfa, "abc")
    assert r.steps[-1].next == [] and not r.accepted


def test_dfa_single_transition_and_unknown_symbol():
    _, dfa = build("ab")
    r = simulate_dfa(dfa, "ab")
    assert all(len(s.next) == 1 for s in r.steps) and r.accepted
    r = simulate_dfa(dfa, "az")
    assert not r.accepted


def test_whole_string_not_substring():
    nfa, dfa = build("ab")
    assert not simulate_nfa(nfa, "xab").accepted and not simulate_dfa(dfa, "abab").accepted


@pytest.mark.parametrize("rx", PATTERNS)
def test_languages_agree(rx):
    nfa, dfa = build(rx)
    assert languages_agree(nfa, dfa, 5)[0]


def test_exports_match_automata():
    nfa, dfa = build("(a|b)*abb")
    d = json.loads(automaton_to_json(nfa, "NFA"))
    assert d["states"] == nfa.states and d["start"] == "q0" and d["has_epsilon_transitions"] is False
    assert sum(len(t["to"]) for t in d["transitions"]) == nfa.transition_count
    d = json.loads(automaton_to_json(dfa, "DFA"))
    assert len(d["transitions"]) == len(dfa.states) * len(dfa.alphabet)
    rows = list(csv.DictReader(io.StringIO(rows_to_csv(nfa_rows(nfa)))))
    assert list(rows[0]) == NFA_COLS and len(rows) == len(nfa.states) * len(nfa.alphabet)
    for r in rows:
        dest = set() if r["Destination States"] == "∅" else set(r["Destination States"].split(", "))
        assert dest == set(nfa.targets(r["State"], r["Input Symbol"]))
    rows = list(csv.DictReader(io.StringIO(rows_to_csv(dfa_rows(dfa)))))
    assert list(rows[0]) == DFA_COLS
    for r in rows:
        assert dfa.transitions[(r["DFA State"], r["Input Symbol"])] == r["Destination State"]
        assert (r["Accepting?"] == "Yes") == (r["DFA State"] in dfa.accepting)


def test_diagram_matches_automata():
    nfa, dfa = build("a(b|c)*")
    for auto, kind in ((nfa, "NFA"), (dfa, "DFA")):
        dot = automaton_dot(auto, kind)
        assert "__start" in dot
        for s in auto.states:
            assert f'"{s}" [' in dot
        for s in auto.accepting:
            assert f'"{s}" [shape=doublecircle' in dot
        for s, a, t in auto.edges():
            assert f'"{s}" -> "{t}"' in dot
