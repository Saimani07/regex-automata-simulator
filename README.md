# Regex Automata Lab
*Interactive Regular Expression to NFA and DFA Simulator*

## Abstract
A Streamlit app that converts a regular expression into (1) an epsilon-free NFA using the Glushkov position-automaton construction and (2) a complete DFA using the direct followpos algorithm. It draws both automata, shows transition tables, simulates strings, and exports everything.

## Problem statement
Textbook conversions from regular expressions to automata are hard to follow by hand. This tool computes them step by step and lets students check results interactively.

## Objectives and scope
- Implement RE → NFA and RE → DFA as two **independent**, direct constructions.
- Never create epsilon transitions.
- **Out of scope by design:** epsilon-NFA, a separate NFA → DFA feature, DFA minimization.

## Features
14 pages: Dashboard, Regex Input, RE → NFA, RE → DFA, NFA/DFA diagrams, NFA/DFA tables, String Simulator, Comparison, Step-by-Step, Example Gallery, Learning Resources, Project Information. Downloads: SVG/PNG/DOT diagrams, CSV tables, JSON exports.

## Regex syntax
`a` literal, `|` alternation, `ab` concatenation, `*` `+` `?`, `( )` grouping, `\` escape. Precedence: parentheses, postfix, concatenation, alternation. Spaces, `. [ ] { } ^ $` are rejected unless escaped.

## Technology stack
Python 3.11+, Streamlit, Graphviz (graphviz Python package + optional Graphviz program), pandas, Pytest.

## Architecture
```
app.py                  Streamlit UI only
src/tokenizer.py        text -> tokens        src/parser.py          tokens -> syntax tree
src/regex_ast.py        tree nodes, pretty()  src/validation.py      error handling, epsilon check
src/position_automaton.py  nullable/first/last/follow + Glushkov NFA
src/direct_dfa.py       direct followpos DFA  src/nfa.py, dfa.py     data structures
src/simulator.py        NFA/DFA simulation    src/visualization.py   Graphviz DOT
src/exporters.py        tables, CSV, JSON     src/examples.py        gallery
tests/                  pytest suite          docs/                  theory, viva, demo script
```

## Algorithms
See `docs/theory.md`. NFA: states `q0` + one per position; transitions from firstpos and followpos; accepting = lastpos (+ q0 if nullable). DFA: append `#`; start = firstpos(root); next(S,a) = union of followpos(p), p in S labelled a; accepting if it contains `#`; empty set goes to TRAP.

## Installation (Windows)
1. **Python:** download from https://www.python.org/downloads/ (3.11 or newer). On the first installer screen tick **"Add python.exe to PATH"**, then Install.
2. **VS Code:** download from https://code.visualstudio.com/ and install. Add the *Python* extension (Extensions icon, search "Python").
3. **Open the project:** unzip `regex-automata-lab.zip`, then in VS Code choose *File → Open Folder* and pick the `regex-automata-lab` folder.
4. **Open a terminal inside VS Code:** *Terminal → New Terminal* (PowerShell). Run every command below there; the prompt must end in `regex-automata-lab>`.
5. **Create the virtual environment:** `py -m venv .venv`
6. **Activate it:** `.\.venv\Scripts\Activate.ps1` (you should see `(.venv)` in the prompt).
   - If PowerShell says scripts are disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer Y, and retry; **or** use Command Prompt (*Terminal → dropdown → Command Prompt*) and run `.venv\Scripts\activate.bat`.
7. **Install dependencies:** `python -m pip install -r requirements.txt`
8. **Graphviz program (optional):** diagrams already appear in the browser without it. Only the SVG/PNG *download* buttons need it: run `winget install Graphviz.Graphviz` (or install from https://graphviz.org/download/ and tick "Add to PATH"), then restart VS Code.
9. **Launch the app:** `streamlit run app.py` (a browser tab opens at http://localhost:8501).
10. **Run tests:** `python -m pytest -q`

## Usage
Open *Regex Input*, type e.g. `(a|b)*abb`, press **Convert to Both**, then browse the pages in the sidebar. Use *String Simulator* or *Step-by-Step Execution* to test strings.

## Troubleshooting
- `py` not recognised: reinstall Python with "Add to PATH", or use `python -m venv .venv`.
- `streamlit` not recognised: the virtual environment is not active; repeat step 6, or run `python -m streamlit run app.py`.
- `ModuleNotFoundError: src`: run commands from the project folder (where `app.py` is).
- SVG/PNG buttons missing: Graphviz program is not installed or not on PATH (step 8); DOT download still works.
- Port busy: `streamlit run app.py --server.port 8502`.

## Testing
`python -m pytest -q` covers parser, validation, NFA, DFA (determinism, completeness, trap state), simulators (including empty string), exports (CSV/JSON consistency), diagram consistency, and an NFA/DFA/`re.fullmatch` comparison over all strings up to length 5 (the `re` module is used only as a test oracle).

## Limitations
Supports only literal symbols and the operators above (no character classes, `.`, counted repetition, anchors). Large expressions give large diagrams.

## Future improvements
DFA minimization, regex-to-JSON import, language equivalence checker, animated diagrams.
