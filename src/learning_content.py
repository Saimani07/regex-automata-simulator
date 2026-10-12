"""Learning content for the 22-step beginner journey.

Each lesson includes:
- Short explanation (beginner & advanced)
- Simple visual example
- Interactive example data
- Prediction question with options and immediate feedback
- Demo regex for automaton bridge
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Lesson:
    id: int
    title: str
    category: str
    concept: str
    short_explanation_beginner: str
    short_explanation_advanced: str
    visual_example: str
    interactive_prompt: str
    prediction_question: str
    prediction_options: List[str]
    correct_option: str
    feedback_correct: str
    feedback_incorrect: str
    demo_regex: Optional[str] = None
    demo_string: Optional[str] = None


LESSONS: List[Lesson] = [
    Lesson(
        id=1,
        title="What is an Alphabet?",
        category="Foundations",
        concept="Alphabet (Σ)",
        short_explanation_beginner=(
            "An alphabet is simply the set of allowed building blocks (characters or symbols) you can use. "
            "Just like the English alphabet has 26 letters from A to Z, a computer science alphabet is any fixed set of symbols."
        ),
        short_explanation_advanced=(
            "In Theory of Computation, an alphabet is a non-empty, finite set of symbols, typically denoted by the Greek letter Σ (Sigma). "
            "For example, the binary alphabet is Σ = {0, 1}, and a common simple alphabet is Σ = {a, b}."
        ),
        visual_example=(
            "**Examples of Alphabets:**\n\n"
            "- Binary alphabet: `Σ = {0, 1}`\n"
            "- Two-letter alphabet: `Σ = {a, b}`\n"
            "- Decimal digit alphabet: `Σ = {0, 1, 2, ..., 9}`"
        ),
        interactive_prompt="Select or inspect an alphabet to see valid symbols.",
        prediction_question="If our alphabet is Σ = {a, b}, is the character 'c' allowed?",
        prediction_options=["Yes, any character is allowed", "No, only 'a' and 'b' are allowed"],
        correct_option="No, only 'a' and 'b' are allowed",
        feedback_correct="Correct! Only symbols explicitly included in Σ are permitted in this alphabet.",
        feedback_incorrect="Not quite. An alphabet strictly defines the allowed characters. Any symbol not in Σ is forbidden.",
        demo_regex="a|b",
        demo_string="a",
    ),
    Lesson(
        id=2,
        title="What is a Symbol?",
        category="Foundations",
        concept="Symbol",
        short_explanation_beginner=(
            "A symbol is a single individual character from the alphabet. "
            "Think of it as a single Lego brick. You cannot break it down any further."
        ),
        short_explanation_advanced=(
            "A symbol (or token) is an atomic element s ∈ Σ. "
            "Symbols have length 1. In formal languages, symbols are never further decomposed."
        ),
        visual_example=(
            "If `Σ = {a, b}`:\n\n"
            "- `'a'` is a symbol.\n"
            "- `'b'` is a symbol.\n"
            "- `'ab'` is NOT a symbol (it is a sequence of two symbols)."
        ),
        interactive_prompt="Identify whether an item is a single symbol or a sequence.",
        prediction_question="Is '01' a single symbol over the binary alphabet Σ = {0, 1}?",
        prediction_options=["Yes, it's one binary value", "No, it is two consecutive symbols: '0' and '1'"],
        correct_option="No, it is two consecutive symbols: '0' and '1'",
        feedback_correct="Correct! '01' is composed of two atomic symbols: '0' followed by '1'.",
        feedback_incorrect="Incorrect. '0' and '1' are individual symbols. '01' is a string of length 2.",
        demo_regex="01",
        demo_string="01",
    ),
    Lesson(
        id=3,
        title="What is a String?",
        category="Foundations",
        concept="String (w)",
        short_explanation_beginner=(
            "A string is a sequence of symbols lined up in a specific order. "
            "For example, putting 'a' and 'b' and 'b' together gives the string 'abb'. "
            "The length of a string is simply the count of symbols in it: length('abb') = 3."
        ),
        short_explanation_advanced=(
            "A string (or word) w over an alphabet Σ is a finite sequence of symbols chosen from Σ. "
            "The length |w| is the number of symbols in w. The set of all possible strings over Σ is denoted Σ* (the Kleene closure of Σ)."
        ),
        visual_example=(
            "**String:** `w = a b b`\n\n"
            "- Symbol 1: `a`\n"
            "- Symbol 2: `b`\n"
            "- Symbol 3: `b`\n"
            "- Length: `|w| = 3`"
        ),
        interactive_prompt="Count the symbols and observe the order.",
        prediction_question="What is the length of the string 'aba'?",
        prediction_options=["1", "2", "3", "Undefined"],
        correct_option="3",
        feedback_correct="Correct! 'aba' contains three symbols: 'a', 'b', and 'a', so |aba| = 3.",
        feedback_incorrect="Not quite. Count the characters: 'a' (1) + 'b' (2) + 'a' (3) = 3.",
        demo_regex="aba",
        demo_string="aba",
    ),
    Lesson(
        id=4,
        title="What is the Empty String?",
        category="Foundations",
        concept="Empty String (ε)",
        short_explanation_beginner=(
            "The empty string is a string with zero symbols. It has length 0. "
            "Think of an empty text message or a blank page: it exists as a container, but has nothing written inside. "
            "In mathematics and computer science, we often write it as the Greek letter ε (epsilon)."
        ),
        short_explanation_advanced=(
            "The empty string is uniquely denoted ε (or λ). By definition, |ε| = 0. "
            "For every string w, concatenating ε leaves w unchanged: wε = εw = w. "
            "Note: ε is a string, NOT the empty set ∅. The set {ε} has 1 element (the empty string), whereas ∅ has 0 elements."
        ),
        visual_example=(
            "- Regular string `'a'`: Length = 1\n"
            "- Empty string `ε`: Length = 0 (no characters)\n"
            "- Analogy: An empty paper sheet vs. a sheet with 'a' written on it."
        ),
        interactive_prompt="Notice that testing an empty string tests whether the start state itself is accepting.",
        prediction_question="What is the length of the empty string ε?",
        prediction_options=["0", "1", "Undefined"],
        correct_option="0",
        feedback_correct="Correct! The empty string contains 0 symbols, so |ε| = 0.",
        feedback_incorrect="Incorrect. The empty string contains no symbols at all, meaning its length is exactly 0.",
        demo_regex="a*",
        demo_string="",
    ),
    Lesson(
        id=5,
        title="What is a Language?",
        category="Foundations",
        concept="Language (L)",
        short_explanation_beginner=(
            "In computer science, a 'language' is simply a collection (set) of valid strings. "
            "For example, 'all strings of only letter a' is a language: {a, aa, aaa, ...}. "
            "Any string either belongs to the language (Accepted) or does not belong (Rejected)."
        ),
        short_explanation_advanced=(
            "A formal language L over alphabet Σ is a subset of Σ*, i.e., L ⊆ Σ*. "
            "A language can be finite (e.g., L = {a, b, ab}) or infinite (e.g., L = {a^n : n ≥ 0}). "
            "The core goal of automata theory is recognizing whether a given string w belongs to L."
        ),
        visual_example=(
            "**Language Definition:** 'All strings that end with b'\n\n"
            "- `'ab'` ∈ L (Accepted ✅)\n"
            "- `'b'` ∈ L (Accepted ✅)\n"
            "- `'a'` ∉ L (Rejected ❌)"
        ),
        interactive_prompt="See how a rule separates strings into accepted and rejected sets.",
        prediction_question="If L is the language of strings starting with 'a', does 'ba' belong to L?",
        prediction_options=["Yes", "No"],
        correct_option="No",
        feedback_correct="Correct! 'ba' begins with 'b', so it fails the rule and does not belong to L.",
        feedback_incorrect="Incorrect. 'ba' begins with 'b', not 'a', so it is rejected.",
        demo_regex="a(a|b)*",
        demo_string="ba",
    ),
    Lesson(
        id=6,
        title="What is a Regular Expression?",
        category="Regex Basics",
        concept="Regular Expression (Regex)",
        short_explanation_beginner=(
            "A Regular Expression (Regex) is a compact formula that describes a pattern of strings. "
            "Instead of listing thousands of strings one by one, you write a short formula like `a*` or `a|b`. "
            "It acts like a stencil: any string that matches the stencil is accepted."
        ),
        short_explanation_advanced=(
            "A regular expression R denotes a regular language L(R). "
            "The base cases are the empty set ∅, the empty string ε, and literal symbols a ∈ Σ. "
            "Inductive operations are union (alternation |), concatenation, and Kleene closure (*)."
        ),
        visual_example=(
            "**Pattern:** `(a|b)*abb`\n\n"
            "**Meaning:** 'Any sequence of a's and b's that ends with abb.'\n"
            "- `'abb'` matches ✅\n"
            "- `'babb'` matches ✅\n"
            "- `'abba'` does not match ❌"
        ),
        interactive_prompt="Experience how a small pattern represents infinite possible matches.",
        prediction_question="What does a regular expression define?",
        prediction_options=["A single fixed string only", "A pattern or set of strings (a language)", "A Python script"],
        correct_option="A pattern or set of strings (a language)",
        feedback_correct="Correct! A regular expression is a declarative specification of a language.",
        feedback_incorrect="Not quite. A regular expression defines a pattern matching zero, one, or infinitely many strings.",
        demo_regex="a",
        demo_string="a",
    ),
    Lesson(
        id=7,
        title="Literal Symbols",
        category="Regex Basics",
        concept="Literal Match",
        short_explanation_beginner=(
            "Writing a single character like `a` means: match exactly one `a`, and nothing else! "
            "If you input `a`, it is accepted. If you input `b` or `aa`, it is rejected."
        ),
        short_explanation_advanced=(
            "For a ∈ Σ, the expression `a` denotes the singleton language L(a) = {a}. "
            "In our Glushkov NFA, this creates start state q0 and position state q1 with transition q0 --a--> q1."
        ),
        visual_example=(
            "**Expression:** `a`\n\n"
            "- Input `'a'` → ACCEPTED ✅\n"
            "- Input `'b'` → REJECTED ❌\n"
            "- Input `'aa'` → REJECTED ❌\n"
            "- Input `''` (empty) → REJECTED ❌"
        ),
        interactive_prompt="Test literal symbol matching.",
        prediction_question="Does the regular expression 'a' accept the string 'aa'?",
        prediction_options=["Yes, because it contains 'a'", "No, because 'a' matches exactly one 'a'"],
        correct_option="No, because 'a' matches exactly one 'a'",
        feedback_correct="Correct! In automata theory, the regex must match the ENTIRE string, not just a substring.",
        feedback_incorrect="Incorrect. The regex must match the entire input. 'aa' has two symbols, but the regex expects only one.",
        demo_regex="a",
        demo_string="a",
    ),
    Lesson(
        id=8,
        title="Alternation: The OR Operator (|)",
        category="Operators & Syntax",
        concept="Alternation (|)",
        short_explanation_beginner=(
            "The vertical bar `|` means OR. It gives you a choice between two alternatives. "
            "`a|b` means: accept string 'a' OR accept string 'b'."
        ),
        short_explanation_advanced=(
            "Alternation represents language union: L(R1 | R2) = L(R1) ∪ L(R2). "
            "Nullable(R1 | R2) = Nullable(R1) ∨ Nullable(R2). "
            "Firstpos(R1 | R2) = Firstpos(R1) ∪ Firstpos(R2)."
        ),
        visual_example=(
            "**Expression:** `a|b`\n\n"
            "- Input `'a'` → ACCEPTED ✅\n"
            "- Input `'b'` → ACCEPTED ✅\n"
            "- Input `'ab'` → REJECTED ❌ (that is concatenation, not choice!)"
        ),
        interactive_prompt="Explore how | creates branch choices.",
        prediction_question="Does the expression 'a|b' accept the string 'ab'?",
        prediction_options=["Yes, both 'a' and 'b' are there", "No, it accepts either 'a' or 'b', but not both together"],
        correct_option="No, it accepts either 'a' or 'b', but not both together",
        feedback_correct="Correct! 'a|b' chooses one branch. It does NOT concatenate them.",
        feedback_incorrect="Not quite. 'a|b' means pick 'a' OR pick 'b'. To accept 'ab', you need concatenation `ab`.",
        demo_regex="a|b",
        demo_string="b",
    ),
    Lesson(
        id=9,
        title="Concatenation: Following In Order",
        category="Operators & Syntax",
        concept="Concatenation (ab)",
        short_explanation_beginner=(
            "Writing symbols next to each other like `ab` means: first match `a`, followed immediately by `b`. "
            "Order matters! `ab` accepts 'ab', but rejects 'ba'."
        ),
        short_explanation_advanced=(
            "Concatenation of languages: L(R1 R2) = {uv : u ∈ L(R1), v ∈ L(R2)}. "
            "In our AST, Cat(R1, R2). Nullable(Cat) = Nullable(R1) ∧ Nullable(R2). "
            "Firstpos = Firstpos(R1) ∪ (Firstpos(R2) if Nullable(R1) else ∅)."
        ),
        visual_example=(
            "**Expression:** `ab`\n\n"
            "- Step 1: Read `'a'`\n"
            "- Step 2: Read `'b'`\n"
            "- Input `'ab'` → ACCEPTED ✅\n"
            "- Input `'ba'` → REJECTED ❌"
        ),
        interactive_prompt="Observe the required sequence order.",
        prediction_question="Does the expression 'ab' accept the string 'ba'?",
        prediction_options=["Yes, it has both letters", "No, order is strict: 'a' must come first"],
        correct_option="No, order is strict: 'a' must come first",
        feedback_correct="Correct! Concatenation requires the symbols to appear in the exact sequential order.",
        feedback_incorrect="Incorrect. Order matters in concatenation: 'a' followed by 'b' cannot accept 'b' first.",
        demo_regex="ab",
        demo_string="ab",
    ),
    Lesson(
        id=10,
        title="Kleene Star: Zero or More (*)",
        category="Operators & Syntax",
        concept="Kleene Star (*)",
        short_explanation_beginner=(
            "The asterisk `*` means: repeat the preceding symbol ZERO or more times! "
            "`a*` means: any number of 'a's, including none at all (the empty string!). "
            "Accepted: empty string, 'a', 'aa', 'aaa', 'aaaa', etc."
        ),
        short_explanation_advanced=(
            "Kleene star closure: L(R*) = L(R)^0 ∪ L(R)^1 ∪ L(R)^2 ∪ ... = ⋃_{i ≥ 0} L(R)^i. "
            "Notice that L(R)^0 = {ε}, so R* is ALWAYS nullable (Nullable(R*) = True)."
        ),
        visual_example=(
            "**Expression:** `a*`\n\n"
            "- `''` (0 times) → ACCEPTED ✅\n"
            "- `'a'` (1 time) → ACCEPTED ✅\n"
            "- `'aa'` (2 times) → ACCEPTED ✅\n"
            "- `'b'` → REJECTED ❌"
        ),
        interactive_prompt="Test repetition counts including zero.",
        prediction_question="Does 'a*' accept the empty string?",
        prediction_options=["Yes, zero occurrences of 'a' is allowed", "No, at least one 'a' is required"],
        correct_option="Yes, zero occurrences of 'a' is allowed",
        feedback_correct="Correct! Kleene star means ZERO or more, so the empty string is always accepted by a*.",
        feedback_incorrect="Not quite. Remember: * includes ZERO occurrences, which means the empty string is accepted.",
        demo_regex="a*",
        demo_string="",
    ),
    Lesson(
        id=11,
        title="One-or-More: The Plus Operator (+)",
        category="Operators & Syntax",
        concept="Plus (+)",
        short_explanation_beginner=(
            "The plus sign `+` means: repeat ONE or more times! "
            "Unlike `*`, the plus operator requires AT LEAST ONE occurrence. "
            "`a+` accepts 'a', 'aa', 'aaa', but REJECTS the empty string."
        ),
        short_explanation_advanced=(
            "Positive closure: L(R+) = ⋃_{i ≥ 1} L(R)^i = L(R) L(R)*. "
            "Nullable(R+) = Nullable(R). If R is not nullable, R+ cannot accept ε."
        ),
        visual_example=(
            "**Difference between `*` and `+`:**\n\n"
            "- `a*`: accepts `''`, `'a'`, `'aa'`...\n"
            "- `a+`: rejects `''` ❌, accepts `'a'`, `'aa'`..."
        ),
        interactive_prompt="Compare zero-or-more vs one-or-more.",
        prediction_question="Does 'a+' accept the empty string?",
        prediction_options=["Yes", "No, it requires at least one 'a'"],
        correct_option="No, it requires at least one 'a'",
        feedback_correct="Correct! '+' requires at least one occurrence, so the empty string is rejected.",
        feedback_incorrect="Incorrect. '+' means ONE or more. The empty string has zero 'a's, so it is rejected.",
        demo_regex="a+",
        demo_string="a",
    ),
    Lesson(
        id=12,
        title="Optional: The Question Mark (?)",
        category="Operators & Syntax",
        concept="Optional (?)",
        short_explanation_beginner=(
            "The question mark `?` means: ZERO or ONE occurrence (optional). "
            "`a?` means: 'a' is optional. Either it is there, or it isn't. "
            "Accepted: '' (empty) and 'a'. Rejected: 'aa' (too many!)."
        ),
        short_explanation_advanced=(
            "Optional operator: L(R?) = L(R) ∪ {ε}. "
            "Nullable(R?) is always True. It allows either exactly zero instances or exactly one instance."
        ),
        visual_example=(
            "**Expression:** `a?`\n\n"
            "- `''` (0 times) → ACCEPTED ✅\n"
            "- `'a'` (1 time) → ACCEPTED ✅\n"
            "- `'aa'` (2 times) → REJECTED ❌ (maximum is 1!)"
        ),
        interactive_prompt="See how ? acts as an optional toggle.",
        prediction_question="Does 'a?' accept the string 'aa'?",
        prediction_options=["Yes, any number of 'a's", "No, at most one 'a' is allowed"],
        correct_option="No, at most one 'a' is allowed",
        feedback_correct="Correct! '?' means at most one occurrence. 'aa' has two, so it is rejected.",
        feedback_incorrect="Not quite. '?' means zero or ONE. Two 'a's exceed the limit of 1.",
        demo_regex="a?",
        demo_string="a",
    ),
    Lesson(
        id=13,
        title="Parentheses: Grouping Operations",
        category="Operators & Syntax",
        concept="Grouping ( )",
        short_explanation_beginner=(
            "Parentheses `( )` group subexpressions together, just like in math `(2 + 3) * 4`. "
            "Without parentheses, `ab*` repeats only `b`! "
            "With parentheses, `(ab)*` repeats the whole pair `ab`: 'ababab'..."
        ),
        short_explanation_advanced=(
            "Parentheses explicitly override operator precedence in the syntax tree. "
            "In `ab*`, Star binds directly to Lit('b'): Cat(Lit('a'), Star(Lit('b'))). "
            "In `(ab)*`, Star binds to Cat: Star(Cat(Lit('a'), Lit('b')))."
        ),
        visual_example=(
            "- `ab*` = `a` followed by `b*` → matches `'a'`, `'ab'`, `'abb'`, `'abbb'`\n"
            "- `(ab)*` = repeat `ab` as a unit → matches `''`, `'ab'`, `'abab'`, `'ababab'`"
        ),
        interactive_prompt="Compare grouped vs ungrouped repetition.",
        prediction_question="Does 'ab*' accept the string 'abab'?",
        prediction_options=["Yes", "No, only 'b' can repeat in 'ab*'"],
        correct_option="No, only 'b' can repeat in 'ab*'",
        feedback_correct="Correct! In 'ab*', the '*' applies only to 'b'. To repeat 'ab', you must write '(ab)*'.",
        feedback_incorrect="Incorrect. The '*' attaches only to the immediately preceding symbol 'b', unless parentheses group '(ab)*'.",
        demo_regex="(ab)*",
        demo_string="abab",
    ),
    Lesson(
        id=14,
        title="Operator Precedence",
        category="Operators & Syntax",
        concept="Precedence Order",
        short_explanation_beginner=(
            "When multiple operators appear together, there is a strict hierarchy: "
            "1. Parentheses `( )` (highest priority) \n"
            "2. Postfix operators `*`, `+`, `?` \n"
            "3. Concatenation `ab` \n"
            "4. Alternation `|` (lowest priority) \n\n"
            "So `ab|c` means `(ab) | c`, NOT `a (b|c)`."
        ),
        short_explanation_advanced=(
            "Grammar derivation hierarchy (high to low precedence): \n"
            "atom: Lit | '(' alt ')' \n"
            "post: atom ('*' | '+' | '?')* \n"
            "cat: post+ \n"
            "alt: cat ('|' cat)* \n"
            "This standard precedence eliminates ambiguity in the grammar."
        ),
        visual_example=(
            "**Parsing `ab*|c`:**\n\n"
            "1. `b*` binds first (postfix)\n"
            "2. `a(b*)` binds second (concatenation)\n"
            "3. `(ab*) | c` binds last (alternation)"
        ),
        interactive_prompt="Trace which operator binds first.",
        prediction_question="In 'a|bc', which operation happens first?",
        prediction_options=["'a|b' alternation happens first", "'bc' concatenation happens first"],
        correct_option="'bc' concatenation happens first",
        feedback_correct="Correct! Concatenation has higher precedence than alternation, so 'bc' binds before '|'.",
        feedback_incorrect="Not quite. Concatenation binds tighter than alternation '|'. So 'a|bc' is parsed as 'a | (bc)'.",
        demo_regex="ab|c",
        demo_string="ab",
    ),
    Lesson(
        id=15,
        title="Combining Operators",
        category="Regex Basics",
        concept="Composite Patterns",
        short_explanation_beginner=(
            "By combining concatenation, alternation, and repetition, you can express complex patterns. "
            "Example: `(a|b)*abb` means: 'Any sequence of a's and b's, as long as it ends with abb'."
        ),
        short_explanation_advanced=(
            "Regular expressions are closed under union, concatenation, and Kleene star. "
            "Any regular language can be formed through finite combinations of these three primitive operations."
        ),
        visual_example=(
            "**Pattern:** `(a|b)*abb`\n\n"
            "- `(a|b)*`: Any prefix of 'a's and 'b's\n"
            "- `abb`: Must end with exactly 'abb'\n"
            "- Accepted: `'abb'`, `'aabb'`, `'babb'`, `'ababb'`\n"
            "- Rejected: `'abba'` (ends with 'a', not 'b')"
        ),
        interactive_prompt="See how prefixes, loops, and suffixes combine.",
        prediction_question="Does '(a|b)*abb' accept 'babb'?",
        prediction_options=["Yes, prefix is 'b' and suffix is 'abb'", "No, it must start with 'a'"],
        correct_option="Yes, prefix is 'b' and suffix is 'abb'",
        feedback_correct="Correct! '(a|b)*' can match 'b', and 'abb' matches the suffix.",
        feedback_incorrect="Incorrect. '(a|b)*' allows any combinations of 'a' or 'b', including starting with 'b'.",
        demo_regex="(a|b)*abb",
        demo_string="babb",
    ),
    Lesson(
        id=16,
        title="From Regular Expression to Automaton",
        category="Automata Concepts",
        concept="The Bridge: Regex → Automaton",
        short_explanation_beginner=(
            "Why do we need an automaton? \n"
            "A regular expression tells us WHAT strings belong to a language. \n"
            "An automaton provides the step-by-step MACHINE that tests a string character by character! \n"
            "Think of regex as the blueprint, and the automaton as the working factory machine."
        ),
        short_explanation_advanced=(
            "Kleene's Theorem proves that a language is regular if and only if it is recognized by a finite automaton. "
            "A regular expression provides a declarative definition; a finite state machine provides an operational recognizer."
        ),
        visual_example=(
            "```\n"
            "REGULAR EXPRESSION:  ab*\n"
            "         ↓\n"
            "LANGUAGE DESCRIPTION: 'a followed by zero or more b\\'s'\n"
            "         ↓\n"
            "FINITE AUTOMATON:    (q0) --a--> ((q1)) <--b--\n"
            "         ↓\n"
            "TEST STRING:         Read 'a', read 'b' → ACCEPTED!\n"
            "```"
        ),
        interactive_prompt="Understand why machines need state transitions to decide strings.",
        prediction_question="What role does an automaton play compared to a regular expression?",
        prediction_options=[
            "It is a machine-like procedure that executes state transitions on input strings",
            "It only generates random strings",
        ],
        correct_option="It is a machine-like procedure that executes state transitions on input strings",
        feedback_correct="Correct! The automaton operationalizes the pattern into a state-transition decision machine.",
        feedback_incorrect="Not quite. An automaton receives an input string and transitions between states to accept or reject it.",
        demo_regex="ab*",
        demo_string="abb",
    ),
    Lesson(
        id=17,
        title="What is an NFA?",
        category="Automata Concepts",
        concept="Nondeterministic Finite Automaton (NFA)",
        short_explanation_beginner=(
            "NFA stands for Nondeterministic Finite Automaton. \n"
            "'Nondeterministic' means: from one state reading a symbol, the machine can branch into MULTIPLE possible states at the same time! "
            "Think of it like exploring multiple paths at once in a maze. If at least ONE active path reaches an accepting state, the string is ACCEPTED."
        ),
        short_explanation_advanced=(
            "An NFA is a 5-tuple (Q, Σ, δ, q0, F) where the transition function δ: Q × Σ → P(Q) maps to the POWERSET of states. "
            "During simulation, the active state set S ⊆ Q evolves via S' = ⋃_{q ∈ S} δ(q, a). "
            "Our Glushkov position automaton is epsilon-free, having exactly one state per position in the regular expression plus q0."
        ),
        visual_example=(
            "**In an NFA:**\n\n"
            "State `q0` reading symbol `'a'` might transition to BOTH `q1` AND `q3`!\n"
            "Active state set: `{q0}` --a--> `{q1, q3}`."
        ),
        interactive_prompt="Watch the active state set expand and track multiple branches.",
        prediction_question="In an NFA, can multiple states be active at the same time?",
        prediction_options=["Yes, the machine tracks all possible active paths simultaneously", "No, strictly only one state"],
        correct_option="Yes, the machine tracks all possible active paths simultaneously",
        feedback_correct="Correct! An NFA allows a set of states to be active simultaneously.",
        feedback_incorrect="Incorrect. That is a DFA! An NFA allows branching, so multiple states can be active at once.",
        demo_regex="(a|b)*abb",
        demo_string="a",
    ),
    Lesson(
        id=18,
        title="What is a DFA?",
        category="Automata Concepts",
        concept="Deterministic Finite Automaton (DFA)",
        short_explanation_beginner=(
            "DFA stands for Deterministic Finite Automaton. \n"
            "'Deterministic' means: from every state and symbol, there is EXACTLY ONE next state. "
            "No guessing, no branching! Exactly one single current state is active at any time. "
            "If an input symbol has nowhere valid to go, it transitions to a TRAP (dead) state."
        ),
        short_explanation_advanced=(
            "A DFA is a 5-tuple (Q, Σ, δ, q0, F) where δ: Q × Σ → Q is a total single-valued function. "
            "For every state q and symbol a, |δ(q, a)| = 1. "
            "Our direct DFA builder groups position sets into DFA states using followpos, adding a TRAP state when a transition set is empty."
        ),
        visual_example=(
            "**In a DFA:**\n\n"
            "Current state: `S0`\n"
            "Read `'a'` → EXACTLY ONE next state: `S1`\n"
            "Active state: only `S1`."
        ),
        interactive_prompt="Watch how a DFA moves from one precise state to another.",
        prediction_question="In a DFA, how many next states can exist for a given state and input symbol?",
        prediction_options=["Exactly one next state", "Zero, one, or multiple next states"],
        correct_option="Exactly one next state",
        feedback_correct="Correct! Determinism guarantees exactly one target state for every valid transition.",
        feedback_incorrect="Not quite. In a deterministic machine (DFA), each transition points to exactly one specific state.",
        demo_regex="ab",
        demo_string="ab",
    ),
    Lesson(
        id=19,
        title="NFA vs DFA: Side-by-Side Comparison",
        category="Automata Concepts",
        concept="NFA vs DFA",
        short_explanation_beginner=(
            "Both NFA and DFA recognize the EXACT SAME regular languages! "
            "- NFA: Flexible, can have multiple active states, often fewer states in construction. \n"
            "- DFA: Strict, exactly one active state, easy and fast for computers to run directly. \n"
            "Neither is 'better' — they are two mathematical representations of the same language."
        ),
        short_explanation_advanced=(
            "The Rabin-Scott powerset theorem guarantees that every NFA has an equivalent DFA. "
            "In our project, RE → NFA (Glushkov) and RE → DFA (direct followpos) are computed independently. "
            "Both produce identical language acceptance without epsilon transitions."
        ),
        visual_example=(
            "| Feature | NFA (Glushkov) | DFA (Direct followpos) |\n"
            "| :--- | :--- | :--- |\n"
            "| Active states | Set `{q0, q1, ...}` | Exactly one `S_i` |\n"
            "| Next transition | 0, 1, or multiple | Exactly 1 (complete) |\n"
            "| Epsilon transitions | None (in our lab) | None |\n"
            "| Final acceptance | If ANY active state is accepting | If the single final state is accepting |"
        ),
        interactive_prompt="Compare execution traces side by side.",
        prediction_question="Do an NFA and DFA generated from the same regular expression accept the same language?",
        prediction_options=["Yes, they accept the exact same set of strings", "No, DFAs can accept more languages"],
        correct_option="Yes, they accept the exact same set of strings",
        feedback_correct="Correct! NFAs and DFAs have identical computational power for regular languages.",
        feedback_incorrect="Incorrect. NFA and DFA recognize the exact same class of regular languages.",
        demo_regex="a(b|c)*",
        demo_string="abc",
    ),
    Lesson(
        id=20,
        title="String Acceptance: How a Machine Decides",
        category="Automata Concepts",
        concept="Acceptance Condition",
        short_explanation_beginner=(
            "How does an automaton give its final verdict? \n"
            "1. Start in the Initial State. \n"
            "2. Read the input string symbol by symbol, moving along transitions. \n"
            "3. After all symbols are read, check where you stopped. \n"
            "If your final state (or at least one active state in an NFA) is an ACCEPTING state (double circle), the string is ACCEPTED! Otherwise, REJECTED."
        ),
        short_explanation_advanced=(
            "For a string w = a1 a2 ... an: \n"
            "- DFA accepts iff δ*(q0, w) ∈ F. \n"
            "- NFA accepts iff δ*(q0, w) ∩ F ≠ ∅. \n"
            "Crucially, the entire string must be consumed. Substring matches do not count."
        ),
        visual_example=(
            "**Accepting State:** Drawn as a **double circle** `((q1))`.\n"
            "**Non-accepting State:** Drawn as a single circle `(q0)`.\n\n"
            "If you land in `((q1))` when the string ends → **ACCEPTED ✅**"
        ),
        interactive_prompt="Track the path to double-circle accepting states.",
        prediction_question="When is a string accepted by an automaton?",
        prediction_options=[
            "When the machine ends in an accepting state after consuming the entire string",
            "As soon as any accepting state is visited, even if symbols remain",
        ],
        correct_option="When the machine ends in an accepting state after consuming the entire string",
        feedback_correct="Correct! The entire string must be read, and the final configuration must contain an accepting state.",
        feedback_incorrect="Incorrect. Automata test whole strings. Acceptance is checked ONLY after the complete string is consumed.",
        demo_regex="ab",
        demo_string="ab",
    ),
    Lesson(
        id=21,
        title="Transition Diagrams: Reading the Graph",
        category="Automata Concepts",
        concept="State Diagrams",
        short_explanation_beginner=(
            "A transition diagram is a directed graph where: \n"
            "- Circles are STATES. \n"
            "- An arrow pointing in from nowhere indicates the START state. \n"
            "- Arrows with letters show TRANSITIONS (where to go when reading that letter). \n"
            "- Double circles are ACCEPTING states."
        ),
        short_explanation_advanced=(
            "The transition graph G = (V, E) has vertex set V = Q and directed labeled edges (u, v) with label a ∈ Σ iff v ∈ δ(u, a). "
            "Graphviz DOT syntax represents vertices and labeled edges, colored yellow during step execution."
        ),
        visual_example=(
            "```\n"
            "--> (q0) --- a ---> ((q1))\n"
            "     |                ^\n"
            "     +------- b ------+\n"
            "```\n"
            "- Arrow from outside = start state `q0`\n"
            "- Arrow labelled `a` = transition on symbol 'a'\n"
            "- Double circle = accepting state `q1`"
        ),
        interactive_prompt="Read and navigate the visual graph representation.",
        prediction_question="In a state diagram, what does a double circle indicate?",
        prediction_options=["An accepting (final) state", "The initial start state", "An error state"],
        correct_option="An accepting (final) state",
        feedback_correct="Correct! Double circle always marks an accepting state.",
        feedback_incorrect="Not quite. In standard automata diagrams, double circle denotes an accepting (final) state.",
        demo_regex="a|b",
        demo_string="a",
    ),
    Lesson(
        id=22,
        title="Transition Tables: The Tabular Map",
        category="Automata Concepts",
        concept="Transition Table",
        short_explanation_beginner=(
            "A transition table represents the exact same information as a diagram, but in a spreadsheet grid! \n"
            "- Rows = Current States \n"
            "- Columns = Input Symbols \n"
            "- Grid cells = Where you go next. \n"
            "This table is exactly what software uses to implement fast state machines."
        ),
        short_explanation_advanced=(
            "A transition table tabulates the function δ: Q × Σ → Q (or P(Q)). "
            "For DFAs, each entry is a single state S_j or TRAP. "
            "For NFAs, each entry is a subset of states {q_i, ...} or ∅."
        ),
        visual_example=(
            "| State | Input 'a' | Input 'b' | Accepting? |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **S0** (Start) | S1 | TRAP | No |\n"
            "| **S1** | TRAP | TRAP | Yes |\n"
            "| **TRAP** | TRAP | TRAP | No |"
        ),
        interactive_prompt="Check how rows and columns uniquely map every move.",
        prediction_question="What do the columns of a transition table represent?",
        prediction_options=["Input symbols from the alphabet", "All accepting states", "Step numbers in a trace"],
        correct_option="Input symbols from the alphabet",
        feedback_correct="Correct! Columns correspond to the alphabet symbols Σ.",
        feedback_incorrect="Incorrect. Rows represent states, and columns represent the input symbols.",
        demo_regex="(a|b)*abb",
        demo_string="abb",
    ),
]


def get_lesson(lesson_id: int) -> Optional[Lesson]:
    for lesson in LESSONS:
        if lesson.id == lesson_id:
            return lesson
    return None
