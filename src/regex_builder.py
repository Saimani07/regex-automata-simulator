"""Visual Regex Builder model and human-readable translator.

Translates regular expressions to natural human-readable explanations and provides
synchronization, undo history, and presets.
"""
from typing import Optional, Tuple
from .parser import parse_regex
from .regex_ast import Alt, Cat, Lit, Node, Opt, Plus, Star
from .tokenizer import RegexSyntaxError


def ast_to_human_readable(node: Node) -> str:
    """Convert an AST node into a clear, beginner-friendly English explanation."""
    if isinstance(node, Lit):
        sym = node.symbol if node.symbol is not None else "#"
        return f"the symbol '{sym}'"

    if isinstance(node, Star):
        if isinstance(node.child, Lit):
            return f"zero or more occurrences of '{node.child.symbol}'"
        return f"zero or more occurrences of ({ast_to_human_readable(node.child)})"

    if isinstance(node, Plus):
        if isinstance(node.child, Lit):
            return f"one or more occurrences of '{node.child.symbol}'"
        return f"one or more occurrences of ({ast_to_human_readable(node.child)})"

    if isinstance(node, Opt):
        if isinstance(node.child, Lit):
            return f"optional '{node.child.symbol}' (zero or one)"
        return f"optional ({ast_to_human_readable(node.child)})"

    if isinstance(node, Alt):
        return f"{ast_to_human_readable(node.left)} OR {ast_to_human_readable(node.right)}"

    if isinstance(node, Cat):
        return f"{ast_to_human_readable(node.left)} followed by {ast_to_human_readable(node.right)}"

    return str(node)


def regex_to_human_readable(pattern: str) -> Tuple[bool, str]:
    """Parse regex and return (is_valid, human_readable_text_or_error)."""
    if not pattern.strip():
        return True, "Empty expression: matches nothing yet."
    try:
        ast = parse_regex(pattern)
        return True, ast_to_human_readable(ast)
    except RegexSyntaxError as err:
        return False, f"Syntax issue: {err}"
    except Exception as err:
        return False, f"Invalid pattern: {err}"


BUILDER_PRESETS = [
    {"label": "Single 'a'", "regex": "a", "desc": "Exactly one 'a'"},
    {"label": "'a' OR 'b'", "regex": "a|b", "desc": "Either 'a' or 'b'"},
    {"label": "'a' followed by 'b'", "regex": "ab", "desc": "Sequence 'ab'"},
    {"label": "Zero or more 'a's", "regex": "a*", "desc": "Any number of 'a's, including empty string"},
    {"label": "One or more 'a's", "regex": "a+", "desc": "At least one 'a'"},
    {"label": "Optional 'a'", "regex": "a?", "desc": "Zero or one 'a'"},
    {"label": "'a' followed by zero or more 'b's", "regex": "ab*", "desc": "'a' then any number of 'b's"},
    {"label": "Any binary string", "regex": "(0|1)*", "desc": "All binary strings over {0, 1}"},
    {"label": "Ends in 'abb'", "regex": "(a|b)*abb", "desc": "Any string over {a, b} ending in 'abb'"},
]


class RegexBuilderState:
    """Encapsulates builder operations with undo history."""

    def __init__(self, initial_regex: str = "a"):
        self.current_regex: str = initial_regex
        self.history: list[str] = [initial_regex]

    def set_regex(self, new_regex: str):
        if self.current_regex != new_regex:
            self.current_regex = new_regex
            self.history.append(new_regex)

    def append_symbol(self, sym: str):
        self.set_regex(self.current_regex + sym)

    def apply_operator(self, op: str):
        """Append unary operator (*, +, ?) or binary (|)."""
        if op in ("*", "+", "?"):
            # Attach to current regex
            if not self.current_regex:
                return
            self.set_regex(self.current_regex + op)
        elif op == "|":
            if self.current_regex and not self.current_regex.endswith("|"):
                self.set_regex(self.current_regex + "|")
        elif op == "(":
            self.set_regex(self.current_regex + "(")
        elif op == ")":
            self.set_regex(self.current_regex + ")")

    def wrap_in_group(self):
        """Wrap the entire current expression in parentheses."""
        if self.current_regex and not (self.current_regex.startswith("(") and self.current_regex.endswith(")")):
            self.set_regex(f"({self.current_regex})")

    def undo(self) -> str:
        if len(self.history) > 1:
            self.history.pop()
            self.current_regex = self.history[-1]
        return self.current_regex

    def clear(self):
        self.set_regex("")

    def reset(self):
        self.history = ["a"]
        self.current_regex = "a"
