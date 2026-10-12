from src.validation import validate_regex, has_epsilon_transitions, unknown_symbols
from src.position_automaton import build_glushkov_nfa
from src.direct_dfa import build_direct_dfa


def test_validate_ok_and_error():
    ok, msg, ast = validate_regex("a(b|c)*")
    assert ok and ast is not None
    ok, msg, ast = validate_regex("a(b")
    assert not ok and "Missing ')'" in msg and ast is None


def test_unknown_symbols():
    assert unknown_symbols("abz", ["a", "b"]) == ["z"]


def test_no_epsilon_anywhere():
    for rx in ["a", "a*", "(a|b)*abb", "(ab|ba)*", "a?b+"]:
        ast = validate_regex(rx)[2]
        assert not has_epsilon_transitions(build_glushkov_nfa(ast))
        assert not has_epsilon_transitions(build_direct_dfa(ast))
