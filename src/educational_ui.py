"""Educational UI components and pages for Regex Automata Lab.

Implements:
- 22-step learning path
- Visual Regex Playground
- Build-a-Regex visual studio
- Interactive String Lab with 'Why' decomposition
- Regex Operator Lab
- Natural Language translation studio
- Predict-Before-Simulating interactive lab
- Guided end-to-end example for a(b|c)*
- Interactive NFA & DFA concept teachers
- NFA vs DFA side-by-side stepper
- Beginner Challenge Mode
- Glossary & Notation guide
"""
import pandas as pd
import streamlit as st

from .challenges import CHALLENGES, evaluate_challenge
from .direct_dfa import build_direct_dfa
from .learning_content import LESSONS, get_lesson
from .position_automaton import build_glushkov_nfa
from .regex_ast import alphabet_of, operators_used, pretty
from .regex_builder import BUILDER_PRESETS, regex_to_human_readable
from .simulator import simulate_dfa, simulate_nfa
from .string_lab import explain_string_lab
from .validation import validate_regex
from .visualization import automaton_dot


def render_explanation_toggle():
    """Toggle between Beginner (intuitive) and Advanced (formal TOC) explanations."""
    st.session_state.setdefault("explanation_level", "Beginner")
    c1, c2 = st.columns([3, 1])
    with c2:
        level = st.radio(
            "Explanation Level",
            ["Beginner", "Advanced"],
            horizontal=True,
            index=0 if st.session_state.explanation_level == "Beginner" else 1,
            key="explanation_level_radio",
            help="Beginner uses intuitive English; Advanced shows formal TOC notation (Σ, L(R), δ, followpos).",
        )
        st.session_state.explanation_level = level


# ---------------------------------------------------------------- LEARNING PATH
def render_learning_path(send_to_sim_fn):
    st.header("🎓 Interactive Learning Journey")
    st.caption("A step-by-step introduction to alphabets, languages, regular expressions, and automata.")
    render_explanation_toggle()

    st.session_state.setdefault("learning_lesson_idx", 0)
    st.session_state.setdefault("completed_lessons", set())

    total = len(LESSONS)
    curr_idx = st.session_state.learning_lesson_idx
    lesson = LESSONS[curr_idx]

    # Progress bar and selector
    completed = len(st.session_state.completed_lessons)
    st.progress(completed / total, text=f"Progress: {completed} of {total} lessons completed ({int((completed/total)*100)}%)")

    col_sel, col_nav = st.columns([3, 1])
    with col_sel:
        chosen_id = st.selectbox(
            "Jump to Lesson",
            options=[l.id for l in LESSONS],
            index=curr_idx,
            format_func=lambda i: f"Lesson {i}: {LESSONS[i-1].title} ({'✓ Done' if i in st.session_state.completed_lessons else '○ In progress'})",
            key="lesson_select_box",
        )
        if chosen_id - 1 != curr_idx:
            st.session_state.learning_lesson_idx = chosen_id - 1
            st.rerun()

    st.divider()

    # Lesson Card
    st.subheader(f"Lesson {lesson.id}: {lesson.title}")
    st.markdown(f"**Concept:** `{lesson.concept}` | **Category:** *{lesson.category}*")

    # Explanation based on level
    if st.session_state.explanation_level == "Beginner":
        st.info(f"💡 **Intuitive Explanation:**\n\n{lesson.short_explanation_beginner}")
    else:
        st.warning(f"📐 **Formal Definition (Theory of Computation):**\n\n{lesson.short_explanation_advanced}")

    # Visual Example
    with st.container(border=True):
        st.markdown("### 👁️ Visual Example")
        st.markdown(lesson.visual_example)

    # Prediction Question
    st.markdown("### ❓ Prediction Check")
    st.markdown(f"**Question:** {lesson.prediction_question}")

    pred_key = f"pred_ans_{lesson.id}"
    user_choice = st.radio("Your answer:", lesson.prediction_options, key=pred_key)
    c_check, c_bridge = st.columns([2, 2])

    if c_check.button("Submit Prediction", key=f"btn_check_{lesson.id}", type="primary"):
        if user_choice == lesson.correct_option:
            st.success(f"🎉 **{lesson.feedback_correct}**")
            st.session_state.completed_lessons.add(lesson.id)
        else:
            st.error(f"❌ **{lesson.feedback_incorrect}**")

    # Bridge to Automata / Simulator
    if lesson.demo_regex:
        with st.expander(f"🔬 Automaton Preview for '{lesson.demo_regex}'"):
            st.caption(f"See how the regular expression `{lesson.demo_regex}` looks as a machine:")
            ok, _, ast = validate_regex(lesson.demo_regex)
            if ok:
                nfa = build_glushkov_nfa(ast)
                st.graphviz_chart(automaton_dot(nfa, "NFA"))
                if st.button(f"Open '{lesson.demo_regex}' in Simulator", key=f"btn_open_sim_{lesson.id}"):
                    send_to_sim_fn(lesson.demo_regex, "String Simulator", lesson.demo_string or "a")

    # Navigation buttons
    st.divider()
    c_prev, c_mark, c_next = st.columns([1, 1, 1])
    if c_prev.button("◀ Previous Lesson", disabled=(curr_idx == 0)):
        st.session_state.learning_lesson_idx = max(0, curr_idx - 1)
        st.rerun()

    if c_mark.button("Mark as Complete ✓", key=f"mark_btn_{lesson.id}"):
        st.session_state.completed_lessons.add(lesson.id)
        st.rerun()

    if c_next.button("Next Lesson ▶", disabled=(curr_idx == total - 1)):
        st.session_state.completed_lessons.add(lesson.id)
        st.session_state.learning_lesson_idx = min(total - 1, curr_idx + 1)
        st.rerun()


# ---------------------------------------------------------------- REGEX PLAYGROUND
PLAYGROUND_ITEMS = [
    {
        "regex": "a",
        "title": "1. Single Literal Symbol",
        "meaning": "Matches exactly one 'a'.",
        "accepted": ["a"],
        "rejected": ["", "b", "aa"],
        "note": "A single character matches only itself. Whole-string matching requires exactly one symbol.",
    },
    {
        "regex": "a|b",
        "title": "2. Alternation (OR)",
        "meaning": "'a' OR 'b'.",
        "accepted": ["a", "b"],
        "rejected": ["", "ab", "ba", "c"],
        "note": "Pick one branch: either 'a' alone or 'b' alone.",
    },
    {
        "regex": "ab",
        "title": "3. Concatenation (Sequence)",
        "meaning": "'a' followed immediately by 'b'.",
        "accepted": ["ab"],
        "rejected": ["a", "b", "ba", "abb"],
        "note": "Strict order: 'a' must be read first, then 'b'.",
    },
    {
        "regex": "a*",
        "title": "4. Kleene Star (Zero or More)",
        "meaning": "Zero or more occurrences of 'a'.",
        "accepted": ["", "a", "aa", "aaa", "aaaa"],
        "rejected": ["b", "ab", "ba"],
        "note": "Includes the empty string (0 times) and any count of 'a's.",
    },
    {
        "regex": "a+",
        "title": "5. Plus Operator (One or More)",
        "meaning": "At least one 'a'.",
        "accepted": ["a", "aa", "aaa"],
        "rejected": ["", "b", "ab"],
        "note": "Rejects the empty string! Requires at least one 'a'.",
    },
    {
        "regex": "a?",
        "title": "6. Optional Operator (Zero or One)",
        "meaning": "Zero or one 'a' (optional).",
        "accepted": ["", "a"],
        "rejected": ["aa", "aaa", "b"],
        "note": "Allows at most one occurrence.",
    },
    {
        "regex": "ab*",
        "title": "7. Composite: 'a' then zero or more 'b's",
        "meaning": "Start with 'a', followed by any number of 'b's.",
        "accepted": ["a", "ab", "abb", "abbb"],
        "rejected": ["", "b", "ba", "aa"],
        "note": "The '*' binds only to 'b', not to 'a'.",
    },
    {
        "regex": "a(b|c)",
        "title": "8. Grouping with Choice: a(b|c)",
        "meaning": "'a' followed by either 'b' or 'c'.",
        "accepted": ["ab", "ac"],
        "rejected": ["", "a", "b", "c", "abc"],
        "note": "Parentheses group the choice (b|c) together as one unit.",
    },
    {
        "regex": "(a|b)*",
        "title": "9. Universal Choice Repetition: (a|b)*",
        "meaning": "Any sequence of 'a's and 'b's of any length.",
        "accepted": ["", "a", "b", "ab", "ba", "abba", "bbbb"],
        "rejected": ["c", "1"],
        "note": "Every binary word over {a, b} is accepted.",
    },
    {
        "regex": "(a|b)*abb",
        "title": "10. Pattern: Any string ending in 'abb'",
        "meaning": "Strings over {a, b} that end strictly with 'abb'.",
        "accepted": ["abb", "aabb", "babb", "ababb"],
        "rejected": ["", "a", "ab", "abba", "b"],
        "note": "The classic Theory of Computation benchmark.",
    },
]


def render_regex_playground(send_to_sim_fn):
    st.header("🎮 Visual Regex Playground")
    st.caption("Explore regular expressions interactively from elementary literals to compound patterns.")
    render_explanation_toggle()

    choices = [f"{i+1}. `{p['regex']}` — {p['meaning']}" for i, p in enumerate(PLAYGROUND_ITEMS)]
    sel_idx = st.selectbox("Select a Pattern to Explore", range(len(choices)), format_func=lambda i: choices[i])
    item = PLAYGROUND_ITEMS[sel_idx]

    c_left, c_right = st.columns([1, 1])
    with c_left.container(border=True):
        st.subheader(f"Expression: `{item['regex']}`")
        st.markdown(f"**Meaning:** {item['meaning']}")
        st.info(f"💡 {item['note']}")

        st.markdown("#### Sample Strings")
        show_str = lambda s: f"`'{s}'`" if s else "`(empty string ε)`"
        st.write("**Accepted:** " + ", ".join(show_str(s) for s in item["accepted"]))
        st.write("**Rejected:** " + ", ".join(show_str(s) for s in item["rejected"]))

    with c_right.container(border=True):
        st.subheader("🧪 Live Interactive Tester")
        user_test = st.text_input("Test any string:", value=item["accepted"][0], key=f"pg_test_{sel_idx}")
        ok, _, ast = validate_regex(item["regex"])
        if ok:
            dfa = build_direct_dfa(ast)
            res = simulate_dfa(dfa, user_test)
            if res.accepted:
                st.success(f"✅ String `'{user_test}'` is **ACCEPTED** by `{item['regex']}`")
            else:
                st.error(f"❌ String `'{user_test}'` is **REJECTED** by `{item['regex']}`")

        c1, c2 = st.columns(2)
        if c1.button("Send to Simulator", key=f"pg_send_{sel_idx}", type="primary"):
            send_to_sim_fn(item["regex"], "String Simulator", user_test)
        if c2.button("View Automata Diagrams", key=f"pg_diag_{sel_idx}"):
            send_to_sim_fn(item["regex"], "DFA Diagram", user_test)

    # Mini automaton diagram
    st.divider()
    st.subheader(f"State Machine for `{item['regex']}`")
    tab_dfa, tab_nfa = st.tabs(["DFA Diagram", "NFA Diagram"])
    ok, _, ast = validate_regex(item["regex"])
    if ok:
        with tab_dfa:
            st.graphviz_chart(automaton_dot(build_direct_dfa(ast), "DFA"))
        with tab_nfa:
            st.graphviz_chart(automaton_dot(build_glushkov_nfa(ast), "NFA"))


# ---------------------------------------------------------------- BUILD-A-REGEX MODE
def render_builder(send_to_sim_fn):
    st.header("🧱 Build-a-Regex Studio")
    st.caption("Visually construct regular expressions using symbol blocks and operations.")
    render_explanation_toggle()

    st.session_state.setdefault("builder_regex", "a")
    st.session_state.setdefault("builder_history", ["a"])

    # Synchronized text input
    c_in, c_clear = st.columns([4, 1])
    with c_in:
        current_text = st.text_input(
            "Formal Regular Expression (edit directly or use the buttons below):",
            value=st.session_state.builder_regex,
            key="builder_regex_input_field",
        )
        if current_text != st.session_state.builder_regex:
            st.session_state.builder_regex = current_text
            st.session_state.builder_history.append(current_text)

    with c_clear:
        st.write("")
        if st.button("Clear / Reset", key="b_clear"):
            st.session_state.builder_regex = ""
            st.session_state.builder_history.append("")
            st.rerun()

    # Human-readable sync
    is_valid, human_desc = regex_to_human_readable(st.session_state.builder_regex)
    with st.container(border=True):
        st.markdown("### 🗣️ Human-Readable Meaning")
        if is_valid:
            st.success(f"**Description:** {human_desc}")
        else:
            st.error(f"⚠️ **Syntax Alert:** {human_desc}")

    # Visual Builder Palette
    st.markdown("### 🎨 Visual Construction Palette")
    col_sym, col_ops, col_actions = st.columns(3)

    with col_sym.container(border=True):
        st.markdown("**Add Symbols**")
        c1, c2 = st.columns(2)
        if c1.button("➕ Add 'a'", key="add_a"):
            st.session_state.builder_regex += "a"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()
        if c2.button("➕ Add 'b'", key="add_b"):
            st.session_state.builder_regex += "b"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()
        c3, c4 = st.columns(2)
        if c3.button("➕ Add '0'", key="add_0"):
            st.session_state.builder_regex += "0"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()
        if c4.button("➕ Add '1'", key="add_1"):
            st.session_state.builder_regex += "1"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()

        cust = st.text_input("Custom symbol:", max_chars=1, key="cust_sym")
        if st.button("➕ Add Custom Symbol", key="add_cust"):
            if cust:
                st.session_state.builder_regex += cust
                st.session_state.builder_history.append(st.session_state.builder_regex)
                st.rerun()

    with col_ops.container(border=True):
        st.markdown("**Add Operations**")
        o1, o2 = st.columns(2)
        if o1.button("OR (|)", key="op_alt", help="Alternative choice"):
            st.session_state.builder_regex += "|"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()
        if o2.button("Repeat (*)", key="op_star", help="Zero or more repetitions"):
            st.session_state.builder_regex += "*"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()
        o3, o4 = st.columns(2)
        if o3.button("One+ (+)", key="op_plus", help="One or more repetitions"):
            st.session_state.builder_regex += "+"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()
        if o4.button("Optional (?)", key="op_opt", help="Zero or one occurrence"):
            st.session_state.builder_regex += "?"
            st.session_state.builder_history.append(st.session_state.builder_regex)
            st.rerun()

        if st.button("Group in ( ... )", key="op_group", help="Wrap current pattern in parentheses"):
            rx = st.session_state.builder_regex
            if rx and not (rx.startswith("(") and rx.endswith(")")):
                st.session_state.builder_regex = f"({rx})"
                st.session_state.builder_history.append(st.session_state.builder_regex)
                st.rerun()

    with col_actions.container(border=True):
        st.markdown("**Builder Controls & Presets**")
        if st.button("↩ Undo Last Action", key="b_undo"):
            if len(st.session_state.builder_history) > 1:
                st.session_state.builder_history.pop()
                st.session_state.builder_regex = st.session_state.builder_history[-1]
                st.rerun()

        preset = st.selectbox(
            "Try Example Preset:",
            options=[p["label"] for p in BUILDER_PRESETS],
            key="preset_sel",
        )
        if st.button("Load Preset", key="load_preset_btn"):
            sel_rx = next(p["regex"] for p in BUILDER_PRESETS if p["label"] == preset)
            st.session_state.builder_regex = sel_rx
            st.session_state.builder_history.append(sel_rx)
            st.rerun()

    # Test Strings & Simulator Bridge
    st.divider()
    c_test, c_sim = st.columns([2, 1])
    with c_test:
        test_val = st.text_input("Test a string against built regex:", value="a", key="b_test_val")
        if is_valid and st.session_state.builder_regex:
            ok, _, ast = validate_regex(st.session_state.builder_regex)
            if ok:
                dfa = build_direct_dfa(ast)
                res = simulate_dfa(dfa, test_val)
                if res.accepted:
                    st.success(f"✅ String `'{test_val}'` is **ACCEPTED**")
                else:
                    st.error(f"❌ String `'{test_val}'` is **REJECTED**")

    with c_sim:
        st.write("")
        st.write("")
        if st.button("🚀 Send to Simulator", key="b_send_sim", type="primary", disabled=(not is_valid or not st.session_state.builder_regex)):
            send_to_sim_fn(st.session_state.builder_regex, "Dashboard", test_val)


# ---------------------------------------------------------------- NATURAL LANGUAGE EXAMPLES
NATURAL_EXAMPLES = [
    {
        "intent": "I want strings containing exactly one 'a'",
        "formal": "a",
        "steps": [
            ("Step 1: Identify symbol", "'a' is the required literal."),
            ("Step 2: Formalize", "The regular expression is simply `a`."),
        ],
        "samples": (["a"], ["", "b", "aa"]),
    },
    {
        "intent": "I want either 'a' or 'b'",
        "formal": "a|b",
        "steps": [
            ("Step 1: Identify alternatives", "We want 'a' as option 1, 'b' as option 2."),
            ("Step 2: Choose operator", "Alternation '|' denotes union/choice."),
            ("Step 3: Combine", "`a|b`"),
        ],
        "samples": (["a", "b"], ["", "ab", "ba"]),
    },
    {
        "intent": "I want an 'a' followed by a 'b'",
        "formal": "ab",
        "steps": [
            ("Step 1: First symbol", "Initial symbol must be 'a'."),
            ("Step 2: Second symbol", "Next symbol must be 'b'."),
            ("Step 3: Combine in sequence", "Concatenation writes symbols side-by-side: `ab`."),
        ],
        "samples": (["ab"], ["a", "b", "ba"]),
    },
    {
        "intent": "I want zero or more 'a's",
        "formal": "a*",
        "steps": [
            ("Step 1: Base symbol", "The symbol to repeat is 'a'."),
            ("Step 2: Repetition type", "Zero or more repetitions corresponds to Kleene star '*'."),
            ("Step 3: Combine", "`a*` (accepts empty string, 'a', 'aa', etc.)."),
        ],
        "samples": (["", "a", "aaa"], ["b", "ab"]),
    },
    {
        "intent": "I want strings beginning with 'a' followed by zero or more 'b's",
        "formal": "ab*",
        "steps": [
            ("Step 1: Starts with 'a'", "Prefix literal `a`."),
            ("Step 2: Zero or more 'b's", "Repetition `b*`."),
            ("Step 3: Combine in sequence", "Concatenate prefix with suffix: `ab*`."),
        ],
        "samples": (["a", "ab", "abbb"], ["", "b", "ba"]),
    },
    {
        "intent": "I want strings ending with 'abb'",
        "formal": "(a|b)*abb",
        "steps": [
            ("Step 1: Any prefix of a and b", "Zero or more repetitions of choice: `(a|b)*`."),
            ("Step 2: Strict suffix", "Sequence of literal characters: `abb`."),
            ("Step 3: Combine", "Concatenation: `(a|b)*abb`."),
        ],
        "samples": (["abb", "aabb", "babb"], ["", "ab", "abba"]),
    },
]


def render_natural_language(send_to_sim_fn):
    st.header("💬 Natural-Language to Regex Studio")
    st.caption("Learn how plain English requirements translate into mathematically precise regular expressions.")
    render_explanation_toggle()

    intents = [e["intent"] for e in NATURAL_EXAMPLES]
    pick = st.selectbox("Choose a Language Requirement:", range(len(intents)), format_func=lambda i: intents[i])
    ex = NATURAL_EXAMPLES[pick]

    with st.container(border=True):
        st.subheader(f"Requirement: \"{ex['intent']}\"")
        st.markdown(f"**Formal Regular Expression:** `{ex['formal']}`")

        st.markdown("#### 🪜 Step-by-Step Construction")
        for title, desc in ex["steps"]:
            st.markdown(f"- **{title}:** {desc}")

        st.markdown("#### 🧪 Test Strings")
        show_str = lambda s: f"`'{s}'`" if s else "`(empty string ε)`"
        st.write("**Accepted:** " + ", ".join(show_str(s) for s in ex["samples"][0]))
        st.write("**Rejected:** " + ", ".join(show_str(s) for s in ex["samples"][1]))

        if st.button("🚀 Transfer to Simulator", key=f"nl_send_{pick}", type="primary"):
            send_to_sim_fn(ex["formal"], "String Simulator", ex["samples"][0][0])


# ---------------------------------------------------------------- PREDICT BEFORE SIMULATING
QUIZ_QUESTIONS = [
    {
        "regex": "a*",
        "string": "aaa",
        "question": "Will 'aaa' be accepted by 'a*'?",
        "expected": True,
        "correct_feedback": "Correct! 'a*' means zero or more occurrences of 'a', so 'aaa' (3 occurrences) belongs to the language.",
        "wrong_feedback": "Not quite. '*' allows the preceding expression to repeat zero or more times. Therefore 'aaa' is accepted.",
    },
    {
        "regex": "a+",
        "string": "",
        "question": "Will the empty string be accepted by 'a+'?",
        "expected": False,
        "correct_feedback": "Correct! '+' requires ONE or more occurrences. The empty string contains zero 'a's, so it is rejected.",
        "wrong_feedback": "Incorrect. Unlike '*', the '+' operator requires at least one occurrence. The empty string is rejected.",
    },
    {
        "regex": "a|b",
        "string": "ab",
        "question": "Will 'ab' be accepted by 'a|b'?",
        "expected": False,
        "correct_feedback": "Correct! 'a|b' means 'a' OR 'b'. 'ab' is concatenation, which is rejected by alternation.",
        "wrong_feedback": "Not quite. Alternation '|' gives a choice of ONE branch: either 'a' alone or 'b' alone.",
    },
    {
        "regex": "ab*",
        "string": "a",
        "question": "Will 'a' be accepted by 'ab*'?",
        "expected": True,
        "correct_feedback": "Correct! 'ab*' means an 'a' followed by zero or more 'b's. Zero 'b's gives 'a', which is accepted.",
        "wrong_feedback": "Incorrect. 'b*' allows zero 'b's. So 'a' followed by zero 'b's is accepted.",
    },
    {
        "regex": "(a|b)*abb",
        "string": "babb",
        "question": "Will 'babb' be accepted by '(a|b)*abb'?",
        "expected": True,
        "correct_feedback": "Correct! '(a|b)*' matches the prefix 'b', and 'abb' matches the required ending suffix.",
        "wrong_feedback": "Not quite. '(a|b)*' can match any sequence of 'a' and 'b', including 'b'. Suffix 'abb' satisfies the end condition.",
    },
]


def render_predictor(send_to_sim_fn):
    st.header("🎯 Predict Before Simulating")
    st.caption("Test your intuition! Make a prediction before watching the machine run.")
    render_explanation_toggle()

    q_idx = st.selectbox(
        "Select a Prediction Challenge:",
        range(len(QUIZ_QUESTIONS)),
        format_func=lambda i: f"Challenge {i+1}: `{QUIZ_QUESTIONS[i]['regex']}` with input `'{QUIZ_QUESTIONS[i]['string']}'`",
    )
    q = QUIZ_QUESTIONS[q_idx]

    with st.container(border=True):
        st.subheader(f"Expression: `{q['regex']}`")
        st.markdown(f"**Test String:** `'{q['string']}'`")
        st.markdown(f"### ❓ {q['question']}")

        c1, c2 = st.columns(2)
        user_pred = None
        if c1.button("✅ ACCEPT", key=f"btn_acc_{q_idx}", use_container_width=True):
            user_pred = True
        if c2.button("❌ REJECT", key=f"btn_rej_{q_idx}", use_container_width=True):
            user_pred = False

        if user_pred is not None:
            if user_pred == q["expected"]:
                st.success(f"🎉 **{q['correct_feedback']}**")
            else:
                st.error(f"❌ **{q['wrong_feedback']}**")

            st.divider()
            if st.button("🔍 Show me in the automaton", key=f"btn_show_auto_{q_idx}", type="primary"):
                send_to_sim_fn(q["regex"], "Step-by-Step Execution", q["string"])


# ---------------------------------------------------------------- INTERACTIVE STRING LAB
def render_string_lab(send_to_sim_fn):
    st.header("🧪 Interactive String Lab")
    st.caption("Deconstruct strings component-by-component to understand WHY they are accepted or rejected.")
    render_explanation_toggle()

    c_rx, c_str = st.columns([2, 2])
    with c_rx:
        rx_val = st.text_input("Regular Expression:", value="ab*", key="strlab_rx")
    with c_str:
        test_val = st.text_input("Test String (leave blank for empty string ε):", value="abb", key="strlab_str")

    try:
        report = explain_string_lab(rx_val, test_val)
    except Exception as err:
        st.error(f"❌ {err}")
        return

    # Verdict Card
    with st.container(border=True):
        if report.accepted:
            st.success(f"### ✅ {report.verdict}")
        else:
            st.error(f"### ❌ {report.verdict}")
        st.markdown(f"**Educational Reason:** {report.summary_explanation}")

    # Decomposition Breakdown
    st.subheader("🧩 Structural Decomposition")
    decomp_rows = []
    for p in report.decomposition:
        decomp_rows.append({
            "Substring / Token": f"'{p.substring}'",
            "Target Component": p.component,
            "Evaluation": "✅ Satisfied" if p.status == "Satisfied" else "❌ Failed",
            "Explanation Note": p.note,
        })
    st.dataframe(pd.DataFrame(decomp_rows), hide_index=True)

    # Bridge Buttons
    st.divider()
    st.subheader("🔬 Watch Automata Execution")
    b1, b2 = st.columns(2)
    if b1.button("👁️ See how the NFA processes this", key="strlab_nfa_btn"):
        send_to_sim_fn(rx_val, "Step-by-Step Execution", test_val)
    if b2.button("👁️ See how the DFA processes this", key="strlab_dfa_btn"):
        send_to_sim_fn(rx_val, "Step-by-Step Execution", test_val)


# ---------------------------------------------------------------- REGEX OPERATOR LAB
OPERATORS_DATA = [
    {
        "name": "Alternation (|)",
        "pattern": "a|b",
        "concept": "a OR b",
        "desc": "Chooses between two alternative subexpressions. Exactly one branch is taken.",
        "accepted": ["a", "b"],
        "rejected": ["", "ab", "ba"],
    },
    {
        "name": "Concatenation (ab)",
        "pattern": "ab",
        "concept": "a followed by b",
        "desc": "Sequential order: first read 'a', then immediately read 'b'.",
        "accepted": ["ab"],
        "rejected": ["a", "b", "ba"],
    },
    {
        "name": "Kleene Star (*)",
        "pattern": "a*",
        "concept": "Zero or more a's",
        "desc": "Repeats the preceding symbol zero or more times. Always accepts the empty string.",
        "accepted": ["", "a", "aa", "aaa"],
        "rejected": ["b", "ab"],
    },
    {
        "name": "Plus Operator (+)",
        "pattern": "a+",
        "concept": "One or more a's",
        "desc": "Repeats the preceding symbol one or more times. Rejects the empty string.",
        "accepted": ["a", "aa", "aaa"],
        "rejected": ["", "b"],
    },
    {
        "name": "Optional Operator (?)",
        "pattern": "a?",
        "concept": "Zero or one a",
        "desc": "The preceding symbol is optional: either 0 or 1 occurrence allowed.",
        "accepted": ["", "a"],
        "rejected": ["aa", "b"],
    },
    {
        "name": "Grouping Parentheses ((a|b)*)",
        "pattern": "(a|b)*",
        "concept": "Repeat either a or b zero or more times",
        "desc": "Overrides operator precedence, applying repetition to the combined choice.",
        "accepted": ["", "a", "b", "ab", "ba", "abba"],
        "rejected": ["c", "1"],
    },
]


def render_operator_lab(send_to_sim_fn):
    st.header("🎛️ Regex Operator Laboratory")
    st.caption("Deep-dive into each primitive regular expression operator.")
    render_explanation_toggle()

    cols = st.columns(3)
    for i, op in enumerate(OPERATORS_DATA):
        with cols[i % 3].container(border=True):
            st.subheader(op["name"])
            st.code(op["pattern"], language="regex")
            st.markdown(f"**Meaning:** {op['concept']}")
            st.caption(op["desc"])
            show_str = lambda s: f"`'{s}'`" if s else "`(empty ε)`"
            st.markdown(f"**Accepted:** {', '.join(show_str(s) for s in op['accepted'])}")
            st.markdown(f"**Rejected:** {', '.join(show_str(s) for s in op['rejected'])}")
            if st.button(f"Test '{op['pattern']}'", key=f"btn_op_test_{i}"):
                send_to_sim_fn(op["pattern"], "String Simulator", op["accepted"][0])


# ---------------------------------------------------------------- GUIDED EXAMPLE: a(b|c)*
def render_guided_example(send_to_sim_fn):
    st.header("📘 Guided Walkthrough: `a(b|c)*`")
    st.caption("Follow the complete pipeline from informal English to formal Regex, NFA, DFA, and string execution.")
    render_explanation_toggle()

    rx = "a(b|c)*"
    steps = [
        ("1. Language Description", "We want strings that start with 'a', followed by any number of 'b' or 'c' symbols."),
        ("2. Individual Symbols", "Alphabet Σ = {a, b, c}. We have three distinct literal symbols."),
        ("3. Alternation", "The choice between 'b' and 'c' is written as `b|c`."),
        ("4. Grouping", "To treat the choice as a single unit, wrap it in parentheses: `(b|c)`."),
        ("5. Kleene Star", "To repeat the choice zero or more times, attach `*`: `(b|c)*`."),
        ("6. Concatenation", "Prepend the mandatory initial 'a': `a(b|c)*`."),
        ("7. Final Regular Expression", "Formal pattern: `a(b|c)*`."),
    ]

    for title, desc in steps:
        with st.expander(title, expanded=True):
            st.write(desc)

    st.subheader("🧪 Predict and Test Sample Strings")
    accepted_samples = ["a", "ab", "ac", "abb", "abc", "acbc"]
    rejected_samples = ["", "b", "c", "ba", "aa"]

    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.markdown("**Accepted Strings ✅**")
        st.write(", ".join(f"`'{s}'`" for s in accepted_samples))
    with c2.container(border=True):
        st.markdown("**Rejected Strings ❌**")
        st.write(", ".join(f"`'{s}'`" if s else "`(empty string ε)`" for s in rejected_samples))

    st.subheader("🔬 Generated Automata")
    ok, _, ast = validate_regex(rx)
    if ok:
        nfa = build_glushkov_nfa(ast)
        dfa = build_direct_dfa(ast)
        t_nfa, t_dfa = st.tabs(["NFA (Glushkov)", "DFA (Direct followpos)"])
        with t_nfa:
            st.graphviz_chart(automaton_dot(nfa, "NFA"))
        with t_dfa:
            st.graphviz_chart(automaton_dot(dfa, "DFA"))

    st.divider()
    if st.button("🚀 Load 'a(b|c)*' into Full Simulator", type="primary"):
        send_to_sim_fn(rx, "NFA vs DFA Comparison", "abc")


# ---------------------------------------------------------------- TEACH NFA & DFA
def render_teach_nfa(send_to_sim_fn):
    st.header("⚡ What is an NFA? (Interactive Lesson)")
    st.caption("Discover nondeterminism: multiple active states at the same time.")
    render_explanation_toggle()

    st.info(
        "💡 **Key Concept:** An NFA (Nondeterministic Finite Automaton) may have **more than one possible next state** "
        "for the same input symbol. The machine tracks ALL possible active branches in parallel."
    )

    rx = "(a|b)*abb"
    st.subheader(f"Interactive Exploration on `{rx}`")
    st.write("Notice state `q0` has transitions on symbol 'a' to BOTH `q1` and `q3`!")

    st.session_state.setdefault("teach_nfa_input", "a")
    inp = st.text_input("Type input symbols (e.g. 'a', 'ab', 'abb'):", value=st.session_state.teach_nfa_input, key="teach_nfa_inp")

    ok, _, ast = validate_regex(rx)
    if ok:
        nfa = build_glushkov_nfa(ast)
        res = simulate_nfa(nfa, inp)
        st.markdown(f"**Input:** `'{inp}'` | **Active States:** `{set(res.final)}`")
        st.graphviz_chart(automaton_dot(nfa, "NFA", active=res.final))

    if st.button("🚀 Open Full NFA Simulator", type="primary"):
        send_to_sim_fn(rx, "RE → NFA", inp)


def render_teach_dfa(send_to_sim_fn):
    st.header("🎯 What is a DFA? (Interactive Lesson)")
    st.caption("Discover determinism: exactly one next state for every move.")
    render_explanation_toggle()

    st.info(
        "💡 **Key Concept:** A DFA (Deterministic Finite Automaton) has **exactly one next state** for each state and "
        "input symbol. There is never any ambiguity or branching. If no transition is valid, the machine goes to TRAP."
    )

    rx = "ab"
    st.subheader(f"Interactive Exploration on `{rx}`")
    st.session_state.setdefault("teach_dfa_input", "a")
    inp = st.text_input("Type input symbols (e.g. 'a', 'ab', 'z'):", value=st.session_state.teach_dfa_input, key="teach_dfa_inp")

    ok, _, ast = validate_regex(rx)
    if ok:
        dfa = build_direct_dfa(ast)
        res = simulate_dfa(dfa, inp)
        st.markdown(f"**Input:** `'{inp}'` | **Single Current State:** `{res.final[0] if res.final else 'TRAP'}`")
        st.graphviz_chart(automaton_dot(dfa, "DFA", active=res.final))

    if st.button("🚀 Open Full DFA Simulator", type="primary"):
        send_to_sim_fn(rx, "RE → DFA", inp)


def render_nfa_vs_dfa_interactive(send_to_sim_fn):
    st.header("⚖️ NFA vs DFA Visual Learning")
    st.caption("Side-by-side execution: compare active state sets in NFA vs single state in DFA.")
    render_explanation_toggle()

    rx = "(a|b)*abb"
    text = st.text_input("Test String for Dual Simulation:", value="abb", key="dual_sim_txt")

    ok, _, ast = validate_regex(rx)
    if ok:
        nfa = build_glushkov_nfa(ast)
        dfa = build_direct_dfa(ast)
        res_n = simulate_nfa(nfa, text)
        res_d = simulate_dfa(dfa, text)

        c_n, c_d = st.columns(2)
        with c_n.container(border=True):
            st.subheader("NFA (Glushkov)")
            st.write(f"Active States: `{set(res_n.final)}`")
            st.write(f"Verdict: **{'ACCEPTED ✅' if res_n.accepted else 'REJECTED ❌'}**")
            st.graphviz_chart(automaton_dot(nfa, "NFA", active=res_n.final))

        with c_d.container(border=True):
            st.subheader("DFA (Direct followpos)")
            st.write(f"Current State: `{res_d.final[0] if res_d.final else 'TRAP'}`")
            st.write(f"Verdict: **{'ACCEPTED ✅' if res_d.accepted else 'REJECTED ❌'}**")
            st.graphviz_chart(automaton_dot(dfa, "DFA", active=res_d.final))

        st.info(
            "💡 **Takeaway:** The internal computations are different (NFA branches over state sets; DFA tracks a single state), "
            "but both machines recognize the EXACT SAME regular language!"
        )

        if st.button("Open in Advanced Comparison Tool", type="primary"):
            send_to_sim_fn(rx, "NFA vs DFA Comparison", text)


# ---------------------------------------------------------------- CHALLENGES
def render_challenges(send_to_sim_fn):
    st.header("🏆 Beginner Challenge Mode")
    st.caption("Test your regular expression construction skills with instant automated grading.")
    render_explanation_toggle()

    c_titles = [f"Challenge {c.id}: {c.title}" for c in CHALLENGES]
    c_idx = st.selectbox("Select Challenge", range(len(CHALLENGES)), format_func=lambda i: c_titles[i])
    ch = CHALLENGES[c_idx]

    with st.container(border=True):
        st.subheader(f"Challenge {ch.id}: {ch.title}")
        st.markdown(f"**Task:** {ch.description}")
        with st.expander("💡 Need a Hint?"):
            st.info(ch.hint)

    cand_rx = st.text_input("Enter your Regular Expression solution:", value="a|b" if ch.id == 1 else "a*", key=f"cand_rx_{ch.id}")

    if st.button("Evaluate Solution", key=f"eval_ch_{ch.id}", type="primary"):
        eval_res = evaluate_challenge(ch, cand_rx)
        if not eval_res.valid_syntax:
            st.error(f"❌ Syntax Error: {eval_res.syntax_error}")
        elif eval_res.all_passed:
            st.success(f"🎉 **PERFECT! All {eval_res.total_count} test cases passed!**")
            st.info(eval_res.educational_note)
        else:
            st.warning(f"⚠️ Passed {eval_res.passed_count} of {eval_res.total_count} tests.")

        # Results breakdown
        if eval_res.valid_syntax:
            rows = []
            for tc, passed, reason in eval_res.results:
                rows.append({
                    "Test String": f"'{tc.text}'" if tc.text else "ε (empty)",
                    "Description": tc.label,
                    "Expected": "ACCEPT" if tc.expected_accepted else "REJECT",
                    "Result": "✅ Passed" if passed else "❌ Failed",
                    "Details": reason,
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True)

            if eval_res.all_passed:
                if st.button("🚀 Load Solution into Simulator", key=f"ch_send_{ch.id}"):
                    send_to_sim_fn(cand_rx, "Dashboard", "a")


# ---------------------------------------------------------------- GLOSSARY
def render_glossary():
    st.header("📖 Glossary & Notation Reference")
    st.caption("Quick contextual lookup for Theory of Computation terminology and symbols.")

    terms = [
        ("Σ (Sigma)", "The Alphabet", "A finite, non-empty set of atomic symbols used to construct strings (e.g., Σ = {0, 1} or Σ = {a, b})."),
        ("ε (Epsilon)", "The Empty String", "The unique string of length 0 containing no symbols. (In our lab, ε is used only in notation; no epsilon transitions are ever created)."),
        ("∅ (Empty Set)", "Empty Language", "The set containing zero elements or strings. Different from {ε}, which contains one string."),
        ("| (Vertical Bar)", "Alternation (OR)", "Union of two languages: L(R1 | R2) = L(R1) ∪ L(R2)."),
        ("* (Asterisk)", "Kleene Star", "Zero or more repetitions: L(R*) = ⋃_{i ≥ 0} L(R)^i. Always includes the empty string ε."),
        ("+ (Plus)", "Positive Closure", "One or more repetitions: L(R+) = L(R) L(R)*. Rejects the empty string unless the inner pattern is nullable."),
        ("? (Question Mark)", "Optional", "Zero or one occurrence: L(R?) = L(R) ∪ {ε}."),
        ("NFA", "Nondeterministic Finite Automaton", "A state machine that can have multiple active states simultaneously on a single input symbol."),
        ("DFA", "Deterministic Finite Automaton", "A state machine with exactly one next state for each state and input symbol."),
        ("Glushkov Automaton", "Position Automaton", "An epsilon-free RE → NFA construction where each state corresponds to a literal position in the regex plus start state q0."),
        ("followpos", "Follow Positions", "The set of positions that can immediately follow a given position in an accepted string. Core algorithm for direct DFA."),
        ("TRAP State", "Dead State", "A non-accepting DFA sink state with self-loops on all symbols, ensuring the DFA transition function is complete."),
    ]

    for sym, name, desc in terms:
        with st.container(border=True):
            st.markdown(f"### `{sym}` — {name}")
            st.write(desc)
