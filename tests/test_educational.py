"""Tests for the new educational layer."""
import pytest

from src.challenges import CHALLENGES, evaluate_challenge
from src.direct_dfa import build_direct_dfa
from src.learning_content import LESSONS, get_lesson
from src.parser import parse_regex
from src.position_automaton import build_glushkov_nfa
from src.regex_builder import RegexBuilderState, ast_to_human_readable, regex_to_human_readable
from src.string_lab import explain_string_lab
from src.validation import has_epsilon_transitions, validate_regex


def test_twenty_two_lessons_exist():
    assert len(LESSONS) == 22
    for i in range(1, 23):
        lesson = get_lesson(i)
        assert lesson is not None
        assert lesson.id == i
        assert lesson.title
        assert lesson.short_explanation_beginner
        assert lesson.short_explanation_advanced
        assert lesson.visual_example
        assert lesson.prediction_question
        assert lesson.correct_option in lesson.prediction_options
        if lesson.demo_regex:
            ok, _, ast = validate_regex(lesson.demo_regex)
            assert ok, f"Lesson {i} demo regex '{lesson.demo_regex}' failed validation"


def test_educational_demo_regexes_have_no_epsilons():
    for lesson in LESSONS:
        if lesson.demo_regex:
            ok, _, ast = validate_regex(lesson.demo_regex)
            assert ok
            nfa = build_glushkov_nfa(ast)
            dfa = build_direct_dfa(ast)
            assert not has_epsilon_transitions(nfa)
            assert not has_epsilon_transitions(dfa)


def test_regex_builder_human_readable():
    cases = [
        ("a", "the symbol 'a'"),
        ("a|b", "the symbol 'a' OR the symbol 'b'"),
        ("ab", "the symbol 'a' followed by the symbol 'b'"),
        ("a*", "zero or more occurrences of 'a'"),
        ("a+", "one or more occurrences of 'a'"),
        ("a?", "optional 'a' (zero or one)"),
        ("ab*", "the symbol 'a' followed by zero or more occurrences of 'b'"),
        ("(a|b)*abb", "zero or more occurrences of (the symbol 'a' OR the symbol 'b') followed by the symbol 'a' followed by the symbol 'b' followed by the symbol 'b'"),
    ]
    for rx, expected in cases:
        valid, desc = regex_to_human_readable(rx)
        assert valid
        assert desc == expected


def test_regex_builder_state_operations():
    state = RegexBuilderState("a")
    assert state.current_regex == "a"
    state.append_symbol("b")
    assert state.current_regex == "ab"
    state.apply_operator("*")
    assert state.current_regex == "ab*"
    state.wrap_in_group()
    assert state.current_regex == "(ab*)"
    # Undo
    assert state.undo() == "ab*"
    assert state.undo() == "ab"
    assert state.undo() == "a"
    # Clear & Reset
    state.clear()
    assert state.current_regex == ""
    state.reset()
    assert state.current_regex == "a"


def test_string_lab_decompositions():
    # abb with ab*
    rep = explain_string_lab("ab*", "abb")
    assert rep.accepted
    assert rep.verdict == "ACCEPTED ✅"
    assert len(rep.decomposition) >= 2
    assert rep.decomposition[0].substring == "a" and rep.decomposition[0].status == "Satisfied"
    assert rep.decomposition[1].substring == "bb" and rep.decomposition[1].status == "Satisfied"

    # b with ab* (mismatch)
    rep = explain_string_lab("ab*", "b")
    assert not rep.accepted
    assert rep.verdict == "REJECTED ❌"
    assert rep.decomposition[0].status == "Failed"

    # empty string with a*
    rep = explain_string_lab("a*", "")
    assert rep.accepted

    # empty string with a+
    rep = explain_string_lab("a+", "")
    assert not rep.accepted

    # unknown symbol outside alphabet
    rep = explain_string_lab("ab", "az")
    assert not rep.accepted
    assert "not in the alphabet" in rep.summary_explanation


def test_challenges_evaluation():
    # Challenge 1: a|b
    ch1 = CHALLENGES[0]
    res = evaluate_challenge(ch1, "a|b")
    assert res.all_passed
    assert res.passed_count == res.total_count

    # Semantic equivalence: b|a should also pass
    res_alt = evaluate_challenge(ch1, "b|a")
    assert res_alt.all_passed

    # Incorrect solution: "a" alone should fail on "b"
    res_wrong = evaluate_challenge(ch1, "a")
    assert not res_wrong.all_passed

    # Syntax error
    res_syntax = evaluate_challenge(ch1, "a(")
    assert not res_syntax.valid_syntax

    # All challenges have reference solutions that pass 100%
    for ch in CHALLENGES:
        res = evaluate_challenge(ch, ch.reference_regex)
        assert res.all_passed, f"Challenge {ch.id} ({ch.title}) failed reference regex '{ch.reference_regex}'"


def test_page_routing_structure():
    from app import ALL_PAGES, LEARN_PAGES, SIM_PAGES

    assert "Home" in ALL_PAGES
    assert "Learning Path" in LEARN_PAGES
    assert "Build a Regex" in LEARN_PAGES
    assert "Challenges" in LEARN_PAGES
    assert "Dashboard" in SIM_PAGES
    assert "Regex Input" in SIM_PAGES
    assert "RE → NFA" in SIM_PAGES
    assert "RE → DFA" in SIM_PAGES
    assert "Step-by-Step Execution" in SIM_PAGES
    for name, fn in ALL_PAGES.items():
        assert callable(fn), f"Page handler for '{name}' is not callable"
