"""Beginner Challenge Mode.

Evaluates student-constructed regular expressions against bounded test suites
using the core simulation engine.
"""
from dataclasses import dataclass
from typing import List, Tuple

from .direct_dfa import build_direct_dfa
from .simulator import simulate_dfa
from .validation import validate_regex


@dataclass(frozen=True)
class ChallengeTestCase:
    text: str
    expected_accepted: bool
    label: str


@dataclass(frozen=True)
class Challenge:
    id: int
    title: str
    description: str
    hint: str
    reference_regex: str
    test_cases: List[ChallengeTestCase]


CHALLENGES: List[Challenge] = [
    Challenge(
        id=1,
        title="Alternation: Either 'a' or 'b'",
        description="Construct a regular expression that accepts either 'a' or 'b', and nothing else.",
        hint="Use the vertical bar '|' between symbols.",
        reference_regex="a|b",
        test_cases=[
            ChallengeTestCase("a", True, "Single 'a'"),
            ChallengeTestCase("b", True, "Single 'b'"),
            ChallengeTestCase("", False, "Empty string"),
            ChallengeTestCase("ab", False, "Both together"),
            ChallengeTestCase("ba", False, "Reversed both"),
            ChallengeTestCase("c", False, "Different symbol"),
        ],
    ),
    Challenge(
        id=2,
        title="Kleene Star: Zero or More 'a's",
        description="Construct an expression representing zero or more occurrences of 'a'.",
        hint="Use the Kleene star operator '*' on symbol 'a'.",
        reference_regex="a*",
        test_cases=[
            ChallengeTestCase("", True, "Zero occurrences (empty string)"),
            ChallengeTestCase("a", True, "One occurrence"),
            ChallengeTestCase("aa", True, "Two occurrences"),
            ChallengeTestCase("aaaa", True, "Four occurrences"),
            ChallengeTestCase("b", False, "Forbidden symbol 'b'"),
            ChallengeTestCase("ab", False, "Forbidden sequence 'ab'"),
        ],
    ),
    Challenge(
        id=3,
        title="Sequence & Repetition: 'a' followed by any number of 'b's",
        description="Construct an expression representing an 'a' followed by zero or more 'b's.",
        hint="Concatenate 'a' with 'b*'.",
        reference_regex="ab*",
        test_cases=[
            ChallengeTestCase("a", True, "'a' with zero 'b's"),
            ChallengeTestCase("ab", True, "'a' with one 'b'"),
            ChallengeTestCase("abb", True, "'a' with two 'b's"),
            ChallengeTestCase("abbb", True, "'a' with three 'b's"),
            ChallengeTestCase("", False, "Empty string (missing required 'a')"),
            ChallengeTestCase("b", False, "Missing initial 'a'"),
            ChallengeTestCase("ba", False, "Wrong order"),
            ChallengeTestCase("aa", False, "Extra 'a'"),
        ],
    ),
    Challenge(
        id=4,
        title="One-or-More: At least one '0', followed by '1'",
        description="Construct an expression that accepts one or more '0's, followed by exactly one '1'.",
        hint="Use the '+' operator on '0', then concatenate '1'.",
        reference_regex="0+1",
        test_cases=[
            ChallengeTestCase("01", True, "One '0' then '1'"),
            ChallengeTestCase("001", True, "Two '0's then '1'"),
            ChallengeTestCase("0001", True, "Three '0's then '1'"),
            ChallengeTestCase("1", False, "Missing required '0's (must have ≥ 1)"),
            ChallengeTestCase("0", False, "Missing final '1'"),
            ChallengeTestCase("011", False, "Too many '1's"),
            ChallengeTestCase("", False, "Empty string"),
        ],
    ),
    Challenge(
        id=5,
        title="Binary Strings Ending With '1'",
        description="Construct an expression over {0, 1} for all binary strings that end with '1'.",
        hint="Repeat (0|1) zero or more times, then end with '1'.",
        reference_regex="(0|1)*1",
        test_cases=[
            ChallengeTestCase("1", True, "Single '1'"),
            ChallengeTestCase("01", True, "Starts with '0', ends with '1'"),
            ChallengeTestCase("11", True, "Starts with '1', ends with '1'"),
            ChallengeTestCase("0001", True, "Multiple '0's ending in '1'"),
            ChallengeTestCase("10101", True, "Mixed string ending in '1'"),
            ChallengeTestCase("0", False, "Ends in '0'"),
            ChallengeTestCase("10", False, "Ends in '0'"),
            ChallengeTestCase("00", False, "Ends in '0'"),
            ChallengeTestCase("", False, "Empty string (does not end in '1')"),
        ],
    ),
    Challenge(
        id=6,
        title="Optional Symbol: Optional 'a' then one or more 'b's",
        description="Construct an expression where 'a' is optional, followed by at least one 'b'.",
        hint="Use '?' on 'a' and '+' on 'b'.",
        reference_regex="a?b+",
        test_cases=[
            ChallengeTestCase("b", True, "Zero 'a's, one 'b'"),
            ChallengeTestCase("bb", True, "Zero 'a's, two 'b's"),
            ChallengeTestCase("ab", True, "One 'a', one 'b'"),
            ChallengeTestCase("abbb", True, "One 'a', three 'b's"),
            ChallengeTestCase("", False, "Empty string (missing 'b')"),
            ChallengeTestCase("a", False, "Missing required 'b'"),
            ChallengeTestCase("aab", False, "Too many 'a's (at most 1 allowed)"),
        ],
    ),
    Challenge(
        id=7,
        title="The Classic: Ending in 'abb'",
        description="Construct an expression for all strings over {a, b} that end in 'abb'.",
        hint="Any combination of 'a' and 'b' repeated: (a|b)*, followed by 'abb'.",
        reference_regex="(a|b)*abb",
        test_cases=[
            ChallengeTestCase("abb", True, "Exactly 'abb'"),
            ChallengeTestCase("aabb", True, "'a' prefix then 'abb'"),
            ChallengeTestCase("babb", True, "'b' prefix then 'abb'"),
            ChallengeTestCase("ababb", True, "'ab' prefix then 'abb'"),
            ChallengeTestCase("", False, "Empty string"),
            ChallengeTestCase("ab", False, "Missing second 'b'"),
            ChallengeTestCase("abba", False, "Ends in 'a', not 'abb'"),
            ChallengeTestCase("b", False, "Single 'b'"),
        ],
    ),
]


@dataclass
class ChallengeEvaluation:
    challenge: Challenge
    candidate_regex: str
    valid_syntax: bool
    syntax_error: str
    all_passed: bool
    passed_count: int
    total_count: int
    results: List[Tuple[ChallengeTestCase, bool, str]]
    educational_note: str


def evaluate_challenge(challenge: Challenge, candidate_regex: str) -> ChallengeEvaluation:
    """Test candidate regex against challenge test cases using the core DFA engine."""
    candidate_regex = candidate_regex.strip()
    ok, err_msg, ast = validate_regex(candidate_regex)
    if not ok:
        return ChallengeEvaluation(
            challenge=challenge,
            candidate_regex=candidate_regex,
            valid_syntax=False,
            syntax_error=err_msg,
            all_passed=False,
            passed_count=0,
            total_count=len(challenge.test_cases),
            results=[],
            educational_note="Syntax error encountered. Fix the regex syntax before evaluating test cases.",
        )

    dfa = build_direct_dfa(ast)
    results = []
    passed = 0

    for tc in challenge.test_cases:
        res = simulate_dfa(dfa, tc.text)
        is_correct = res.accepted == tc.expected_accepted
        if is_correct:
            passed += 1
            reason = f"Correctly {'ACCEPTED' if tc.expected_accepted else 'REJECTED'}"
        else:
            reason = (
                f"FAILED: expected {'ACCEPT' if tc.expected_accepted else 'REJECT'}, "
                f"but your regex {'ACCEPTED' if res.accepted else 'REJECTED'} it"
            )
        results.append((tc, is_correct, reason))

    all_passed = passed == len(challenge.test_cases)
    note = (
        "Passing all bounded test cases demonstrates correctness on this exercise test suite. "
        "In formal language theory, general regular expression equivalence is proven by showing that the "
        "symmetric difference language L(R1) △ L(R2) is empty."
    )

    return ChallengeEvaluation(
        challenge=challenge,
        candidate_regex=candidate_regex,
        valid_syntax=True,
        syntax_error="",
        all_passed=all_passed,
        passed_count=passed,
        total_count=len(challenge.test_cases),
        results=results,
        educational_note=note,
    )
