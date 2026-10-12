"""Beginner-friendly String Lab with structural decomposition and 'Why' explanations.

Explains string acceptance from an educational perspective in addition to
the automaton state-transition trace.
"""
from dataclasses import dataclass
from typing import List, Optional

from .direct_dfa import build_direct_dfa
from .position_automaton import build_glushkov_nfa
from .regex_ast import Alt, Cat, Lit, Node, Opt, Plus, Star, alphabet_of
from .simulator import SimResult, simulate_dfa, simulate_nfa
from .validation import validate_regex


@dataclass
class DecompositionPart:
    substring: str
    component: str
    status: str
    note: str


@dataclass
class StringLabReport:
    regex: str
    input_string: str
    accepted: bool
    verdict: str
    decomposition: List[DecompositionPart]
    summary_explanation: str
    nfa_result: SimResult
    dfa_result: SimResult


def _decompose_cat_lit_star(node: Cat, text: str) -> Optional[List[DecompositionPart]]:
    """Specialized decomposition for Cat(Lit, Star(Lit)) like ab*."""
    if isinstance(node.left, Lit) and isinstance(node.right, Star) and isinstance(node.right.child, Lit):
        sym_a = node.left.symbol
        sym_b = node.right.child.symbol
        if not text:
            return [DecompositionPart("", f"Expected '{sym_a}'", "Failed", f"Empty string does not contain initial '{sym_a}'")]
        first = text[0]
        rest = text[1:]
        parts = []
        if first == sym_a:
            parts.append(DecompositionPart(first, f"'{sym_a}'", "Satisfied", f"Initial symbol matches required '{sym_a}'"))
            if all(ch == sym_b for ch in rest):
                parts.append(DecompositionPart(rest if rest else "ε", f"'{sym_b}*'", "Satisfied", f"{len(rest)} occurrence(s) of '{sym_b}' satisfy '{sym_b}*'"))
            else:
                parts.append(DecompositionPart(rest, f"'{sym_b}*'", "Failed", f"Remaining characters contain symbols other than '{sym_b}'"))
        else:
            parts.append(DecompositionPart(first, f"'{sym_a}'", "Failed", f"Expected '{sym_a}' at position 0, but found '{first}'"))
            if rest:
                parts.append(DecompositionPart(rest, "Remaining", "Unreachable", "Processing aborted due to initial mismatch"))
        return parts
    return None


def _decompose_alt(node: Alt, text: str) -> Optional[List[DecompositionPart]]:
    """Specialized decomposition for Alt(Lit, Lit) like a|b."""
    if isinstance(node.left, Lit) and isinstance(node.right, Lit):
        sym_a = node.left.symbol
        sym_b = node.right.symbol
        if text == sym_a:
            return [DecompositionPart(text, f"Left branch '{sym_a}'", "Satisfied", f"Matches the first alternative '{sym_a}'")]
        if text == sym_b:
            return [DecompositionPart(text, f"Right branch '{sym_b}'", "Satisfied", f"Matches the second alternative '{sym_b}'")]
        return [DecompositionPart(text, f"'{sym_a}|{sym_b}'", "Failed", f"Neither '{sym_a}' nor '{sym_b}' matched '{text}'")]
    return None


def _decompose_star(node: Star, text: str) -> Optional[List[DecompositionPart]]:
    """Specialized decomposition for Star(Lit) like a*."""
    if isinstance(node.child, Lit):
        sym = node.child.symbol
        if not text:
            return [DecompositionPart("ε (empty)", f"'{sym}*'", "Satisfied", f"Zero occurrences of '{sym}' satisfies the '*' operator")]
        if all(ch == sym for ch in text):
            return [DecompositionPart(text, f"'{sym}*'", "Satisfied", f"{len(text)} repetitions of '{sym}' satisfies the '*' operator")]
        return [DecompositionPart(text, f"'{sym}*'", "Failed", f"String contains characters other than '{sym}'")]
    return None


def explain_string_lab(pattern: str, test_string: str) -> StringLabReport:
    """Analyze a string against a regex and produce an educational report."""
    ok, msg, ast = validate_regex(pattern)
    if not ok:
        raise ValueError(f"Invalid regex: {msg}")

    nfa = build_glushkov_nfa(ast)
    dfa = build_direct_dfa(ast)
    res_dfa = simulate_dfa(dfa, test_string)
    res_nfa = simulate_nfa(nfa, test_string)
    accepted = res_dfa.accepted

    # Structural decomposition
    decomp = None
    if isinstance(ast, Cat):
        decomp = _decompose_cat_lit_star(ast, test_string)
    elif isinstance(ast, Alt):
        decomp = _decompose_alt(ast, test_string)
    elif isinstance(ast, Star):
        decomp = _decompose_star(ast, test_string)

    if decomp is None:
        # Generic decomposition based on simulation steps
        decomp = []
        if not test_string:
            if accepted:
                decomp.append(DecompositionPart("ε (empty)", "Start state", "Satisfied", "Start state is an accepting state (pattern is nullable)"))
            else:
                decomp.append(DecompositionPart("ε (empty)", "Start state", "Failed", "Start state is not an accepting state (requires input)"))
        else:
            for s in res_dfa.steps:
                target = s.next[0] if s.next else "none"
                status = "Satisfied" if target != dfa.trap else "Failed"
                decomp.append(DecompositionPart(s.symbol, f"Step {s.index}", status, s.explanation))

    # Educational summary explanation
    if not test_string:
        if accepted:
            summary = "The empty string is ACCEPTED because this regular expression is nullable (permits zero characters, e.g. using '*' or '?')."
        else:
            summary = "The empty string is REJECTED because this regular expression requires at least one symbol."
    elif accepted:
        summary = (
            f"The string '{test_string}' is ACCEPTED. Every symbol successfully transitioned through the automaton "
            f"and finished in accepting state '{res_dfa.final[0] if res_dfa.final else '—'}'."
        )
    else:
        # Check if symbol outside alphabet
        unknown = [ch for ch in test_string if ch not in dfa.alphabet]
        if unknown:
            summary = f"The string '{test_string}' is REJECTED because symbol '{unknown[0]}' is not in the alphabet {dfa.alphabet}."
        elif res_dfa.final and res_dfa.final[0] == dfa.trap:
            summary = f"The string '{test_string}' is REJECTED because the machine transitioned into the TRAP state."
        else:
            summary = f"The string '{test_string}' is REJECTED because after reading all symbols, the final state is not an accepting state."

    verdict_text = "ACCEPTED ✅" if accepted else "REJECTED ❌"
    return StringLabReport(
        regex=pattern,
        input_string=test_string,
        accepted=accepted,
        verdict=verdict_text,
        decomposition=decomp,
        summary_explanation=summary,
        nfa_result=res_nfa,
        dfa_result=res_dfa,
    )
