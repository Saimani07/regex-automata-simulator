from src.parser import parse_regex
from src.direct_dfa import build_direct_dfa


def dfa(rx):
    return build_direct_dfa(parse_regex(rx))


def test_single_symbol_with_trap():
    d = dfa("a")
    assert d.states == ["S0", "S1", "TRAP"] and d.trap == "TRAP"
    assert d.accepting == {"S1"}
    assert d.transitions[("S0", "a")] == "S1" and d.transitions[("S1", "a")] == "TRAP"
    assert d.transitions[("TRAP", "a")] == "TRAP"


def test_complete_and_deterministic():
    for rx in ["a", "a|b", "ab", "a*", "(a|b)*abb", "(ab|ba)*", "a(b|c)*"]:
        d = dfa(rx)
        assert len(d.transitions) == len(d.states) * len(d.alphabet)
        for s in d.states:
            for a in d.alphabet:
                assert d.transitions[(s, a)] in d.states


def test_no_trap_when_not_needed():
    d = dfa("(0|1)*")
    assert d.trap is None and len(d.states) == 1 and d.accepting == {"S0"}


def test_abb_has_four_states():
    d = dfa("(a|b)*abb")
    assert len(d.states) == 4 and d.trap is None and len(d.accepting) == 1


def test_marker_never_an_input_symbol():
    d = dfa("ab")
    assert None not in d.alphabet and "#" not in d.alphabet


def test_initial_accepting_when_nullable():
    assert "S0" in dfa("a*").accepting and "S0" not in dfa("a+").accepting
