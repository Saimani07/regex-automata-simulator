from src.parser import parse_regex
from src.position_automaton import analyze, build_glushkov_nfa


def nfa(rx):
    return build_glushkov_nfa(parse_regex(rx))


def test_single_symbol():
    n = nfa("a")
    assert n.states == ["q0", "q1"] and n.start == "q0"
    assert n.accepting == {"q1"}
    assert n.transitions == {("q0", "a"): frozenset({"q1"})}


def test_star_initial_state_accepting():
    n = nfa("a*")
    assert "q0" in n.accepting and "q1" in n.accepting
    assert n.targets("q1", "a") == {"q1"}


def test_plus_initial_not_accepting():
    assert "q0" not in nfa("a+").accepting


def test_optional_initial_accepting():
    assert "q0" in nfa("a?").accepting


def test_followpos_sets():
    a = analyze(parse_regex("a(b|c)*"))
    assert a.symbols == {1: "a", 2: "b", 3: "c"}
    assert not a.nullable and a.first == {1} and a.last == {1, 2, 3}
    assert a.follow[1] == {2, 3} and a.follow[2] == {2, 3} and a.follow[3] == {2, 3}


def test_abb_state_count_and_nondeterminism():
    n = nfa("(a|b)*abb")
    assert len(n.states) == 6            # q0 + 5 positions
    assert n.max_branching() > 1         # genuinely nondeterministic
    assert n.accepting == {"q5"}
