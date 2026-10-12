"""Validation helpers."""
from .parser import parse_regex
from .tokenizer import RegexSyntaxError

EPSILON_NAMES = {"", "ε", "eps", "epsilon", None}


def validate_regex(text: str):
    """Return (ok, message, ast)."""
    try:
        return True, "Valid regular expression.", parse_regex(text)
    except RegexSyntaxError as e:
        return False, str(e), None


def unknown_symbols(text: str, alphabet) -> list:
    return sorted({c for c in text if c not in alphabet})


def has_epsilon_transitions(auto) -> bool:
    """True if any transition is labelled with epsilon or a symbol outside the alphabet."""
    return any(a in EPSILON_NAMES or a not in auto.alphabet for (_, a) in auto.transitions)
