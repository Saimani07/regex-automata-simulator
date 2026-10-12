import pytest
from src.parser import parse_regex
from src.regex_ast import Alt, Cat, Lit, Opt, Plus, Star, pretty
from src.tokenizer import RegexSyntaxError


def test_single_symbol():
    assert parse_regex("a") == Lit("a")


def test_precedence_postfix_over_concat_over_alt():
    assert parse_regex("ab*|c") == Alt(Cat(Lit("a"), Star(Lit("b"))), Lit("c"))


def test_parentheses_override():
    assert parse_regex("(ab)*") == Star(Cat(Lit("a"), Lit("b")))


def test_postfix_operators():
    assert parse_regex("a+") == Plus(Lit("a"))
    assert parse_regex("a?") == Opt(Lit("a"))


def test_escape():
    assert parse_regex(r"\*a") == Cat(Lit("*"), Lit("a"))


def test_pretty():
    assert pretty(parse_regex("a(b|c)*")) == "Cat(Lit(a), Star(Alt(Lit(b), Lit(c))))"


@pytest.mark.parametrize("bad", ["", "(", ")", "a|", "|a", "*a", "a(b", "a)b", "()", "a\\", "a b", "a.b", "+", "a||b"])
def test_invalid_expressions(bad):
    with pytest.raises(RegexSyntaxError):
        parse_regex(bad)
