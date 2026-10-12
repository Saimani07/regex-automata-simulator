# Five-Minute Demo Script

**0:00 - Intro (30 s).** "Regex Automata Lab converts a regular expression into an epsilon-free NFA and, separately, directly into a DFA. No epsilon transitions, no NFA-to-DFA conversion."

**0:30 - Dashboard and Regex Input (45 s).** Type `(a|b)*abb`, click *Convert to Both*. Point out parsed tree, alphabet, operators, state counts and the "no epsilon" confirmation.

**1:15 - RE → NFA (45 s).** Show positions 1..5, nullable/firstpos/lastpos/followpos. Explain: one state per position plus q0. Open *NFA Diagram*; show start arrow and double circle.

**2:00 - RE → DFA (45 s).** Show the end-marker `#`, DFA states as position sets, the 4-state DFA. Stress it is built directly, not from the NFA.

**2:45 - Tables and exports (30 s).** Show both tables, download a CSV and JSON.

**3:15 - String Simulator (45 s).** Test `abb` (accepted), `abba` (rejected), and the empty string. Show NFA active-set trace vs DFA single-state trace.

**4:00 - Step-by-Step (30 s).** Use Start/Next on `aabb`; highlight the yellow active states.

**4:30 - Comparison and wrap-up (30 s).** Show the comparison table and the "same language" check. Mention tests: `python -m pytest -q`. Load `a(b|c)*` from the gallery to finish.
