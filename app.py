"""Regex Automata Lab - Interactive Learning & Simulation Laboratory.

Preserves the existing mathematically rigorous core engine and wraps it in a
complete, interactive beginner-to-advanced educational experience.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from src.direct_dfa import build_direct_dfa
from src.educational_ui import (
    render_builder,
    render_challenges,
    render_glossary,
    render_guided_example,
    render_learning_path,
    render_natural_language,
    render_nfa_vs_dfa_interactive,
    render_operator_lab,
    render_predictor,
    render_regex_playground,
    render_string_lab,
    render_teach_dfa,
    render_teach_nfa,
)
from src.examples import EXAMPLES
from src.exporters import automaton_to_json, dfa_rows, nfa_rows, rows_to_csv
from src.nfa import skey
from src.position_automaton import build_glushkov_nfa
from src.regex_ast import alphabet_of, operators_used, pretty
from src.simulator import languages_agree, simulate_dfa, simulate_nfa
from src.validation import has_epsilon_transitions, validate_regex
from src.visualization import automaton_dot, render_bytes

ROOT = Path(__file__).parent
st.set_page_config(page_title="Regex Automata Lab", page_icon="🔬", layout="wide")
ss = st.session_state

# Session state initialization
defaults = dict(
    regex_input="(a|b)*abb",
    ast=None,
    nfa=None,
    dfa=None,
    error=None,
    regex_used="",
    test_string="abb",
    step_string="abb",
    cmp_string="abb",
    step_idx=0,
    step_started=False,
    page="Home",
    app_mode="🎓 Learning Mode",
    example_pick=EXAMPLES[7]["regex"],
    explanation_level="Beginner",
    completed_lessons=set(),
    learning_lesson_idx=0,
)
for k, v in defaults.items():
    ss.setdefault(k, v)


# ---------------------------------------------------------------- Core Engine Helpers
def convert(which):
    text = ss.regex_input
    ok, msg, ast = validate_regex(text)
    if not ok:
        ss.error = msg
        return
    if text != ss.regex_used:
        ss.nfa = ss.dfa = None
    ss.error, ss.ast, ss.regex_used, ss.step_idx, ss.step_started = None, ast, text, 0, False
    if which in ("nfa", "both"):
        ss.nfa = build_glushkov_nfa(ast)
    if which in ("dfa", "both"):
        ss.dfa = build_direct_dfa(ast)


def clear_all():
    ss.regex_input, ss.ast, ss.nfa, ss.dfa, ss.error, ss.regex_used = "", None, None, None, None, ""
    ss.step_idx, ss.step_started = 0, False


def load_example(rx):
    ss.regex_input = rx
    convert("both")


def send_to_sim(rx: str, target_page: str = "Regex Input", test_str: str = "abb"):
    """Seamless bridge from educational layer directly into existing simulator."""
    ss.regex_input = rx
    ss.test_string = test_str
    ss.step_string = test_str
    ss.cmp_string = test_str
    convert("both")
    ss.app_mode = "🔬 Simulator Mode"
    ss.page = target_page
    st.rerun()


def fset(items):
    items = sorted(items, key=skey)
    return "{" + ", ".join(items) + "}" if items else "∅"


def pset(items):
    return "{" + ", ".join(map(str, sorted(items))) + "}" if items else "∅"


def fmt(states, kind):
    return fset(states) if kind == "NFA" else (states[0] if states else "—")


def need(*kinds):
    if ss.error:
        st.error(f"❌ {ss.error}")
    if any(ss[k] is None for k in kinds):
        st.info("ℹ️ Go to **Regex Input**, enter an expression and press the convert button first.")
        return False
    return True


def summary(auto, kind):
    c = st.columns(5)
    c[0].metric("States", len(auto.states))
    c[1].metric("Transitions", auto.transition_count)
    c[2].metric("Initial state", auto.start)
    c[3].metric("Accepting states", fset(auto.accepting))
    c[4].metric("Epsilon transitions", "None ✅" if not has_epsilon_transitions(auto) else "FOUND ❌")


def analysis_view(a, marker):
    sym = lambda p: a.symbols[p] if a.symbols[p] is not None else "# (end-marker)"
    c = st.columns(3)
    c[0].metric("Nullable(root)", str(a.nullable))
    c[1].metric("Firstpos(root)", pset(a.first))
    c[2].metric("Lastpos(root)", pset(a.last))
    st.dataframe(
        pd.DataFrame([{"Position": p, "Symbol": sym(p), "Followpos": pset(a.follow[p])} for p in sorted(a.symbols)]),
        hide_index=True,
    )


def run_sim(kind, text):
    return simulate_nfa(ss.nfa, text) if kind == "NFA" else simulate_dfa(ss.dfa, text)


def trace_df(res):
    return pd.DataFrame([
        {
            "Step": s.index,
            "Input Symbol": s.symbol,
            "Current State(s)": fmt(s.current, res.kind),
            "Next State(s)": fmt(s.next, res.kind),
            "Explanation": s.explanation,
        }
        for s in res.steps
    ])


def verdict(res):
    (st.success if res.accepted else st.error)("✅ ACCEPTED" if res.accepted else "❌ REJECTED")


def diagram_downloads(dot, kind):
    svg, png = render_bytes(dot, "svg"), render_bytes(dot, "png")
    c = st.columns(3)
    if svg:
        c[0].download_button("⬇ Download SVG", svg, f"{kind.lower()}.svg", "image/svg+xml")
    if png:
        c[1].download_button("⬇ Download PNG", png, f"{kind.lower()}.png", "image/png")
    c[2].download_button("⬇ Download DOT source", dot, f"{kind.lower()}.dot", "text/plain")
    if not (svg and png):
        st.caption("SVG/PNG downloads need the Graphviz program installed (see README). The diagram above works without it.")


# ---------------------------------------------------------------- HOME PAGE
def page_home():
    st.title("🔬 Regex Automata Lab")
    st.markdown("### *Learn Regular Expressions. Build Them. Convert Them. Watch Them Run.*")
    st.caption("Interactive Regular Expression to Epsilon-Free NFA and Direct DFA Simulator")

    with st.container(border=True):
        st.markdown("#### 🌟 Philosophy: Educational Pipeline")
        st.markdown(
            "`LEARN` ➔ `EXPERIMENT` ➔ `BUILD` ➔ `PREDICT` ➔ `CONVERT` ➔ `VISUALIZE` ➔ `SIMULATE` ➔ `UNDERSTAND`"
        )

    st.markdown("### How would you like to begin?")
    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.subheader("🎓 I'm New — Teach Me")
        st.write(
            "Designed for complete beginners with no background in Theory of Computation. "
            "Learn alphabets, symbols, regex operators, build expressions visually, make predictions, "
            "and watch state machines execute step-by-step."
        )
        if st.button("🚀 Enter Learning Mode", type="primary", use_container_width=True):
            ss.app_mode = "🎓 Learning Mode"
            ss.page = "Learning Path"
            st.rerun()

    with c2.container(border=True):
        st.subheader("🔬 I Know Regex — Open Simulator")
        st.write(
            "Designed for students and instructors who already know regular expressions. "
            "Direct access to Glushkov epsilon-free NFA and direct followpos DFA construction, "
            "transition tables, Graphviz diagrams, and full string simulators."
        )
        if st.button("⚡ Open Advanced Simulator", use_container_width=True):
            ss.app_mode = "🔬 Simulator Mode"
            ss.page = "Dashboard"
            st.rerun()

    st.divider()
    st.markdown("#### 🛠️ What Makes Regex Automata Lab Unique?")
    col_a, col_b, col_c = st.columns(3)
    with col_a.container(border=True):
        st.markdown("**1. No Epsilon Transitions**")
        st.caption("Constructs pure Glushkov position NFAs and direct followpos DFAs without bloated epsilon steps.")
    with col_b.container(border=True):
        st.markdown("**2. Independent Constructions**")
        st.caption("Both NFA and DFA are built independently from the same parsed AST. Neither algorithm relies on the other.")
    with col_c.container(border=True):
        st.markdown("**3. Seamless Learning Bridge**")
        st.caption("Every educational lesson, playground widget, and builder connects directly to the core simulator engine.")


# ---------------------------------------------------------------- FOCUSED FOUNDATION PAGES
def page_alphabet_strings():
    st.header("🔤 Alphabet, Symbols & Strings")
    st.caption("The foundational building blocks of formal languages.")
    st.session_state.setdefault("explanation_level", "Beginner")

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.subheader("1. What is an Alphabet (Σ)?")
        st.write("An alphabet is a non-empty, finite set of allowed symbols. Think of it as your available toolbox of characters.")
        st.code("Σ = {a, b}        # Two-letter alphabet\nΣ = {0, 1}        # Binary alphabet")

    with c2.container(border=True):
        st.subheader("2. What is a Symbol?")
        st.write("A single indivisible token from the alphabet. If Σ = {a, b}, then 'a' is a symbol and 'b' is a symbol.")
        st.code("Length of symbol = 1")

    c3, c4 = st.columns(2)
    with c3.container(border=True):
        st.subheader("3. What is a String (w)?")
        st.write("A finite ordered sequence of symbols from Σ. Example: `w = abb`. Its length |w| is 3.")
        st.code("w = 'abb'   -->   |w| = 3")

    with c4.container(border=True):
        st.subheader("4. The Empty String (ε)?")
        st.write("A string with length 0. It contains no characters at all. In theory, written as Greek letter ε (epsilon).")
        st.code("|ε| = 0")

    st.divider()
    if st.button("🚀 Go to Step-by-Step Learning Journey (Lesson 1)", type="primary"):
        ss.learning_lesson_idx = 0
        ss.page = "Learning Path"
        st.rerun()


def page_what_is_regex():
    st.header("✨ What is a Regular Expression?")
    st.caption("A declarative formula for specifying a language.")

    with st.container(border=True):
        st.write(
            "A **Regular Expression (Regex)** is a compact pattern formula. "
            "Instead of listing an infinite number of accepted strings, you describe the pattern with a short rule."
        )
        st.markdown(
            "- `a` — Match literal 'a'\n"
            "- `a|b` — Match 'a' OR 'b'\n"
            "- `ab` — Match 'a' FOLLOWED BY 'b'\n"
            "- `a*` — Match zero or more repetitions of 'a'\n"
            "- `(a|b)*abb` — Any string ending in 'abb'"
        )

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("🎮 Try in Visual Playground", type="primary", use_container_width=True):
        ss.page = "Regex Playground"
        st.rerun()
    if c2.button("🧱 Build an Expression Visually", use_container_width=True):
        ss.page = "Build a Regex"
        st.rerun()


# ---------------------------------------------------------------- EXISTING SIMULATOR PAGES
def page_dashboard():
    st.title("🔬 Regex Automata Lab - Dashboard")
    st.caption("Interactive Regular Expression to NFA and DFA Simulator")
    c = st.columns(3)
    with c[0].container(border=True):
        st.subheader("RE → NFA")
        st.write("Epsilon-free **Glushkov position automaton** built from nullable, firstpos, lastpos and followpos.")
    with c[1].container(border=True):
        st.subheader("RE → DFA")
        st.write("**Direct followpos construction** with an internal end-marker. Complete DFA, no NFA involved.")
    with c[2].container(border=True):
        st.subheader("Simulate")
        st.write("Run strings on both automata, step by step, and compare the results.")
    st.divider()
    if ss.nfa or ss.dfa:
        st.write(f"**Current expression:** `{ss.regex_used}`")
        if ss.nfa:
            summary(ss.nfa, "NFA")
        if ss.dfa:
            summary(ss.dfa, "DFA")
    else:
        st.info("Start with **Regex Input** in the sidebar, or load an example from the **Example Gallery**.")


def page_input():
    st.header("Regex Input")
    st.text_input(
        "Regular expression",
        key="regex_input",
        help="Symbols: letters/digits. Operators: | * + ? ( ). Escape a metacharacter with \\",
    )
    c = st.columns(4)
    c[0].button("Convert to NFA", on_click=convert, args=("nfa",))
    c[1].button("Convert to DFA", on_click=convert, args=("dfa",))
    c[2].button("Convert to Both", on_click=convert, args=("both",), type="primary")
    c[3].button("Clear / Reset", on_click=clear_all)
    c = st.columns([3, 1])
    c[0].selectbox(
        "Example",
        [e["regex"] for e in EXAMPLES],
        key="example_pick",
        format_func=lambda r: f"{r}   -   " + next(e["title"] for e in EXAMPLES if e["regex"] == r),
    )
    c[1].write("")
    c[1].button("Load example", on_click=load_example, args=(ss.example_pick,))
    if ss.error:
        st.error(f"❌ {ss.error}")
    if ss.ast is None:
        return
    st.success(f"✅ Valid expression: `{ss.regex_used}`")
    st.write(f"**Parsed representation:** `{pretty(ss.ast)}`")
    st.write(f"**Alphabet:** {{{', '.join(alphabet_of(ss.ast))}}}   |   **Operators:** {', '.join(operators_used(ss.ast)) or 'none'}")
    for kind, auto in (("NFA", ss.nfa), ("DFA", ss.dfa)):
        if auto is not None:
            st.subheader(kind)
            summary(auto, kind)
            st.caption("✅ No epsilon transitions exist in this automaton.")


def page_nfa():
    st.header("RE → NFA (Glushkov position automaton)")
    if not need("nfa"):
        return
    st.markdown(
        "Every **literal occurrence** gets a unique position number. The NFA has one start state `q0` plus one state `qi` "
        "per position. `q0 --a--> qi` for every `i` in firstpos with symbol `a`, and `qi --a--> qj` for every `j` in "
        "followpos(i) with symbol `a`. Accepting states are lastpos (plus `q0` if the expression is nullable)."
    )
    st.write(f"Expression: `{ss.regex_used}`")
    analysis_view(ss.nfa.analysis, False)
    summary(ss.nfa, "NFA")


def page_dfa():
    st.header("RE → DFA (direct followpos construction)")
    if not need("dfa"):
        return
    st.markdown(
        "The tree is extended to `(r)#` with a unique end-marker `#`. Start state = firstpos(root). For state `S` and "
        "symbol `a`: next = union of followpos(p) for every `p` in `S` labelled `a`. A state is accepting if it contains "
        "the `#` position. An empty next set goes to the **TRAP** state so the DFA is complete."
    )
    st.write(f"Expression: `{ss.regex_used}#`")
    analysis_view(ss.dfa.analysis, True)
    st.subheader("DFA states as position sets")
    st.dataframe(
        pd.DataFrame([
            {"DFA State": s, "Positions": pset(ss.dfa.contents[s]), "Accepting?": "Yes" if s in ss.dfa.accepting else "No"}
            for s in ss.dfa.states
        ]),
        hide_index=True,
    )
    summary(ss.dfa, "DFA")


def page_diagram(kind):
    st.header(f"{kind} Diagram")
    if not need(kind.lower()):
        return
    auto = ss.nfa if kind == "NFA" else ss.dfa
    dot = automaton_dot(auto, kind)
    st.graphviz_chart(dot)
    diagram_downloads(dot, kind)


def page_table(kind):
    st.header(f"{kind} Transition Table")
    if not need(kind.lower()):
        return
    auto = ss.nfa if kind == "NFA" else ss.dfa
    rows = nfa_rows(auto) if kind == "NFA" else dfa_rows(auto)
    if kind == "DFA":
        st.caption("'Accepting?' tells whether the DFA State in that row is accepting. TRAP is the empty-set trap state.")
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    c = st.columns(2)
    c[0].download_button("⬇ Download CSV", rows_to_csv(rows), f"{kind.lower()}_table.csv", "text/csv")
    c[1].download_button("⬇ Export JSON", automaton_to_json(auto, kind), f"{kind.lower()}.json", "application/json")


def page_simulator():
    st.header("String Simulator")
    if not need("nfa", "dfa"):
        return
    kind = st.radio("Automaton", ["NFA", "DFA"], horizontal=True)
    st.text_input("Test string (leave empty to test the empty string)", key="test_string")
    res = run_sim(kind, ss.test_string)
    verdict(res)
    st.write(f"Start state: **{res.start}** | Final: **{fmt(res.final, kind)}** | Whole string tested (not a substring).")
    if not res.steps:
        st.info(f"Empty string: no symbols are read, so it is accepted only if the start state ({res.start}) is accepting.")
    else:
        st.dataframe(trace_df(res), hide_index=True)


def page_compare():
    st.header("NFA vs DFA Comparison")
    if not need("nfa", "dfa"):
        return
    st.text_input("Test string", key="cmp_string")
    n, d = ss.nfa, ss.dfa
    rn, rd = simulate_nfa(n, ss.cmp_string), simulate_dfa(d, ss.cmp_string)
    yn = lambda b: "Yes" if b else "No"
    st.dataframe(
        pd.DataFrame([
            ("Number of states", len(n.states), len(d.states)),
            ("Number of transitions", n.transition_count, d.transition_count),
            ("Number of accepting states", len(n.accepting), len(d.accepting)),
            ("Alphabet size", len(n.alphabet), len(d.alphabet)),
            ("Initial state accepting?", yn(n.start in n.accepting), yn(d.start in d.accepting)),
            ("Transitions per (state, symbol)", f"0 or more (max here: {n.max_branching()})", "exactly 1"),
            ("String acceptance", "ACCEPTED" if rn.accepted else "REJECTED", "ACCEPTED" if rd.accepted else "REJECTED"),
        ], columns=["Property", "NFA", "DFA"]).astype(str),
        hide_index=True,
    )
    agree, L, cex = languages_agree(n, d)
    if agree:
        st.success(f"✅ NFA and DFA accept exactly the same strings (checked all strings up to length {L}).")
    else:
        st.error(f"❌ Disagreement on '{cex}'")
    st.info("NFA and DFA are two representations of the same regular language. Either one can have more states, so never assume one is always smaller.")
    st.markdown(
        "**Construction difference:** the Glushkov NFA keeps *one state per position* and lets several transitions share a "
        "symbol (nondeterminism). The direct DFA groups positions into *sets* that are the states, so each (state, symbol) "
        "has exactly one target. The two are built independently from the same parsed expression."
    )


def _step_cb(action):
    if action == "start":
        ss.step_started, ss.step_idx = True, 0
    elif action == "next":
        ss.step_started, ss.step_idx = True, ss.step_idx + 1
    elif action == "prev":
        ss.step_idx = max(0, ss.step_idx - 1)
    elif action == "all":
        ss.step_started, ss.step_idx = True, 10**6
    else:
        ss.step_started, ss.step_idx = False, 0


def page_steps():
    st.header("Step-by-Step Execution")
    if not need("nfa", "dfa"):
        return
    c = st.columns([1, 3])
    kind = c[0].radio("Automaton", ["NFA", "DFA"])
    c[1].text_input("Test string", key="step_string")
    text = ss.step_string
    res = run_sim(kind, text)
    n = len(res.steps)
    ss.step_idx = min(max(ss.step_idx, 0), n)
    b = st.columns(5)
    for col, (label, act) in zip(b, [("▶ Start", "start"), ("Next Step", "next"), ("Previous Step", "prev"), ("Run All", "all"), ("Reset", "reset")]):
        col.button(label, on_click=_step_cb, args=(act,))
    if not ss.step_started:
        st.info("Press **Start** to begin.")
        st.graphviz_chart(automaton_dot(ss.nfa if kind == "NFA" else ss.dfa, kind))
        return
    idx = ss.step_idx
    auto = ss.nfa if kind == "NFA" else ss.dfa
    if idx == 0:
        active, used = [res.start], []
        st.write(f"**Position:** 0 of {len(text)} | **Current state(s):** {fmt(active, kind)} | **Remaining input:** `{text}`")
        st.caption("Initial configuration: we are in the start state and nothing has been read yet.")
    else:
        s = res.steps[idx - 1]
        active, used = s.next, s.used
        c = st.columns(4)
        c[0].metric("Input position", f"{idx} of {len(text)}")
        c[1].metric("Current symbol", s.symbol)
        c[2].metric("Current state(s)", fmt(s.current, kind))
        c[3].metric("Next state(s)", fmt(s.next, kind))
        st.write("**Transition taken:** " + (", ".join(f"{a} --{y}--> {z}" for a, y, z in s.used) or "none"))
        st.write(f"**Remaining input:** `{s.remaining}`")
        st.info(s.explanation)
    st.graphviz_chart(automaton_dot(auto, kind, active=active, used=used))
    st.caption("Yellow = active state(s). Red thick arrows = transitions just taken.")
    if idx == n:
        if n:
            st.dataframe(trace_df(res), hide_index=True)
        verdict(res)


def page_examples():
    st.header("Example Gallery")
    show = lambda l: ", ".join(f"`{w}`" if w else "`(empty string)`" for w in l)
    for e in EXAMPLES:
        ast = validate_regex(e["regex"])[2]
        nfa, dfa = build_glushkov_nfa(ast), build_direct_dfa(ast)
        with st.expander(f"`{e['regex']}` - {e['title']}"):
            st.write(e["desc"])
            st.write(f"**Accepted:** {show(e['accept'])}")
            st.write(f"**Rejected:** {show(e['reject'])}")
            st.write(
                f"Generated now: NFA {len(nfa.states)} states / {nfa.transition_count} transitions; "
                f"DFA {len(dfa.states)} states / {dfa.transition_count} transitions."
            )
            st.button("Load into converter", key=f"ex_{e['regex']}", on_click=load_example, args=(e["regex"],))


def page_learning():
    st.header("Learning Resources & Theory")
    f = ROOT / "docs" / "theory.md"
    st.markdown(f.read_text(encoding="utf-8") if f.exists() else "docs/theory.md not found.")
    st.subheader("Worked example (computed live): a(b|c)*")
    ast = validate_regex("a(b|c)*")[2]
    nfa, dfa = build_glushkov_nfa(ast), build_direct_dfa(ast)
    st.write(f"Parsed: `{pretty(ast)}`")
    st.write("**NFA analysis:**")
    analysis_view(nfa.analysis, False)
    c = st.columns(2)
    c[0].write("**NFA table**")
    c[0].dataframe(pd.DataFrame(nfa_rows(nfa)), hide_index=True)
    c[1].write("**DFA table** (analysis includes end-marker #)")
    c[1].dataframe(pd.DataFrame(dfa_rows(dfa)), hide_index=True)
    st.write(f"NFA: {len(nfa.states)} states, {nfa.transition_count} transitions. DFA: {len(dfa.states)} states, {dfa.transition_count} transitions (including the trap).")


def page_info():
    st.header("Project Information")
    st.markdown("""
**Regex Automata Lab** - an Interactive Theory of Computation Learning and Simulation Laboratory.

- **Dual-Mode System:** Beginner Learning Mode & Advanced Simulator Mode.
- **Core Engine:** RE → NFA (Glushkov, epsilon-free) and RE → DFA (direct followpos), diagrams, tables, simulation, exports.
- **Not included by design:** epsilon-NFA, separate NFA → DFA conversion, DFA minimization.
- **Stack:** Python 3.11+, Streamlit, Graphviz, Pandas, Pytest.
- **Syntax:** `|` alternation, implicit concatenation, `* + ?`, parentheses, `\\` escape.
- **Docs:** see `README.md`, `docs/theory.md`, `docs/viva_questions.md`, `docs/demo_script.md`.
""")


# ---------------------------------------------------------------- PAGE ROUTER
LEARN_PAGES = {
    "Home": page_home,
    "Learning Path": lambda: render_learning_path(send_to_sim),
    "Alphabet & Strings": page_alphabet_strings,
    "What is Regex?": page_what_is_regex,
    "Regex Operators": lambda: render_operator_lab(send_to_sim),
    "Regex Playground": lambda: render_regex_playground(send_to_sim),
    "Build a Regex": lambda: render_builder(send_to_sim),
    "Natural Language to Regex": lambda: render_natural_language(send_to_sim),
    "Predict Before Simulating": lambda: render_predictor(send_to_sim),
    "String Lab": lambda: render_string_lab(send_to_sim),
    "Guided Example (a(b|c)*)": lambda: render_guided_example(send_to_sim),
    "What is an NFA?": lambda: render_teach_nfa(send_to_sim),
    "What is a DFA?": lambda: render_teach_dfa(send_to_sim),
    "NFA vs DFA Visual Learning": lambda: render_nfa_vs_dfa_interactive(send_to_sim),
    "Challenges": lambda: render_challenges(send_to_sim),
    "Glossary & Notation": render_glossary,
    "Theory & Viva": page_learning,
    "Project Information": page_info,
}

SIM_PAGES = {
    "Home": page_home,
    "Dashboard": page_dashboard,
    "Regex Input": page_input,
    "RE → NFA": page_nfa,
    "RE → DFA": page_dfa,
    "NFA Diagram": lambda: page_diagram("NFA"),
    "DFA Diagram": lambda: page_diagram("DFA"),
    "NFA Transition Table": lambda: page_table("NFA"),
    "DFA Transition Table": lambda: page_table("DFA"),
    "String Simulator": page_simulator,
    "NFA vs DFA Comparison": page_compare,
    "Step-by-Step Execution": page_steps,
    "Example Gallery": page_examples,
    "Theory & Viva": page_learning,
    "Project Information": page_info,
}

ALL_PAGES = {**LEARN_PAGES, **SIM_PAGES}

# ---------------------------------------------------------------- SIDEBAR NAVIGATION
with st.sidebar:
    st.title("🔬 Regex Automata Lab")

    # Mode Selector
    current_mode = st.radio(
        "Active Mode",
        ["🎓 Learning Mode", "🔬 Simulator Mode"],
        index=0 if ss.app_mode == "🎓 Learning Mode" else 1,
        key="mode_radio",
    )
    if current_mode != ss.app_mode:
        ss.app_mode = current_mode
        # If switching modes and current page not in new mode, reset to Home or relevant page
        valid_pages = LEARN_PAGES if current_mode == "🎓 Learning Mode" else SIM_PAGES
        if ss.page not in valid_pages:
            ss.page = "Learning Path" if current_mode == "🎓 Learning Mode" else "Dashboard"
        st.rerun()

    active_page_dict = LEARN_PAGES if ss.app_mode == "🎓 Learning Mode" else SIM_PAGES
    page_list = list(active_page_dict.keys())

    # Ensure page is valid in active dictionary
    if ss.page not in active_page_dict:
        ss.page = page_list[0]

    chosen_page = st.radio(
        "Navigation",
        page_list,
        index=page_list.index(ss.page),
        key="nav_radio",
    )
    if chosen_page != ss.page:
        ss.page = chosen_page
        st.rerun()

    st.divider()
    st.write("**Core Engine Status**")
    st.write(f"Expression: `{ss.regex_used or '—'}`")
    st.write("NFA: " + ("✅ ready" if ss.nfa else "⬜ not built"))
    st.write("DFA: " + ("✅ ready" if ss.dfa else "⬜ not built"))

    if ss.app_mode == "🎓 Learning Mode":
        st.caption("💡 Tip: Use 'Send to Simulator' on any lesson or playground to load expressions directly into the engine.")
    else:
        st.caption("⚡ Advanced mode with complete epsilon-free Glushkov NFA and direct followpos DFA construction.")

# Render chosen page
ALL_PAGES[ss.page]()
