"""Tokenizer: turns the regex text into tokens."""
from dataclasses import dataclass


class RegexSyntaxError(ValueError):
    def __init__(self, message, position=None):
        super().__init__(message)
        self.position = position


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    pos: int


SPECIAL = {"|": "ALT", "*": "STAR", "+": "PLUS", "?": "OPT", "(": "LPAREN", ")": "RPAREN"}
UNSUPPORTED = set(".[]{}^$")


def tokenize(text: str) -> list:
    tokens, i = [], 0
    while i < len(text):
        c = text[i]
        if c == "\\":
            if i + 1 >= len(text):
                raise RegexSyntaxError(f"Dangling escape '\\' at position {i}: nothing follows it.", i)
            tokens.append(Token("LIT", text[i + 1], i))
            i += 2
            continue
        if c.isspace():
            raise RegexSyntaxError(f"Whitespace at position {i} is not allowed. Use '\\ ' for a literal space.", i)
        if c in UNSUPPORTED:
            raise RegexSyntaxError(f"'{c}' at position {i} is not supported. Write '\\{c}' to use it as a literal.", i)
        tokens.append(Token(SPECIAL.get(c, "LIT"), c, i))
        i += 1
    return tokens
