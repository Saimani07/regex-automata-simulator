"""Recursive-descent parser.
Grammar:  alt := cat ('|' cat)* ; cat := post+ ; post := atom ('*'|'+'|'?')* ; atom := LIT | '(' alt ')'
Precedence (high->low): parentheses, postfix, concatenation, alternation."""
from .regex_ast import Alt, Cat, Lit, Opt, Plus, Star, Node
from .tokenizer import RegexSyntaxError, tokenize

_POST = {"STAR": Star, "PLUS": Plus, "OPT": Opt}


class _Parser:
    def __init__(self, tokens):
        self.t, self.i = tokens, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def parse(self) -> Node:
        if not self.t:
            raise RegexSyntaxError("The expression is empty. Enter at least one symbol.")
        node = self.alt()
        tok = self.peek()
        if tok is not None:
            raise RegexSyntaxError(f"Unmatched ')' at position {tok.pos}.", tok.pos)
        return node

    def alt(self):
        node = self.cat()
        while (tok := self.peek()) and tok.kind == "ALT":
            self.i += 1
            node = Alt(node, self.cat())
        return node

    def cat(self):
        tok = self.peek()
        if tok is None or tok.kind in ("ALT", "RPAREN"):
            where = "the end of the expression" if tok is None else f"position {tok.pos}"
            raise RegexSyntaxError(f"Missing operand: expected a symbol or '(' at {where}.",
                                   None if tok is None else tok.pos)
        node = self.post()
        while (tok := self.peek()) and tok.kind in ("LIT", "LPAREN"):
            node = Cat(node, self.post())
        return node

    def post(self):
        node = self.atom()
        while (tok := self.peek()) and tok.kind in _POST:
            self.i += 1
            node = _POST[tok.kind](node)
        return node

    def atom(self):
        tok = self.peek()
        if tok.kind == "LIT":
            self.i += 1
            return Lit(tok.value)
        if tok.kind == "LPAREN":
            self.i += 1
            nxt = self.peek()
            if nxt is not None and nxt.kind == "RPAREN":
                raise RegexSyntaxError(f"Empty group '()' at position {tok.pos}.", tok.pos)
            node = self.alt()
            close = self.peek()
            if close is None or close.kind != "RPAREN":
                raise RegexSyntaxError(f"Missing ')' for the '(' at position {tok.pos}.", tok.pos)
            self.i += 1
            return node
        raise RegexSyntaxError(f"Operator '{tok.value}' at position {tok.pos} has nothing to repeat.", tok.pos)


def parse_regex(text: str) -> Node:
    return _Parser(tokenize(text)).parse()
