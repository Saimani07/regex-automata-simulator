# Viva Questions and Answers

1. **What is a regular expression?** A formula built from symbols, `|`, concatenation, `*`, `+`, `?` and parentheses that describes a regular language.
2. **What is a formal language?** Any set of strings over an alphabet.
3. **What is an alphabet?** A finite, non-empty set of symbols.
4. **What is a finite automaton?** A machine with a finite set of states, an alphabet, transitions, a start state and accepting states.
5. **What is a DFA?** An automaton with exactly one transition for each state and input symbol.
6. **What is an NFA?** An automaton where a state may have zero, one or many transitions on a symbol.
7. **What is nondeterminism?** The ability to be in several possible states at once; the NFA accepts if any path accepts.
8. **When does an NFA accept?** When, after the whole input, at least one active state is accepting.
9. **What is an epsilon transition?** A move that consumes no input. This project never creates them.
10. **Why is the generated NFA epsilon-free?** Glushkov's construction links positions directly with real symbols.
11. **What is a position?** A unique number given to each literal occurrence in the expression.
12. **What is nullable?** True if the sub-expression can match the empty string.
13. **What is firstpos?** The set of positions that can match the first symbol of a string.
14. **What is lastpos?** The set of positions that can match the last symbol of a string.
15. **What is followpos?** For a position p, the positions that can directly follow it.
16. **How is followpos computed for concatenation?** For each p in lastpos(left), add firstpos(right) to followpos(p).
17. **How is followpos computed for star/plus?** For each p in lastpos(child), add firstpos(child) to followpos(p).
18. **Nullable of `r+`?** Same as nullable(r). `r*` and `r?` are always nullable.
19. **What are the states of the position NFA?** `q0` plus one state per position.
20. **When is `q0` accepting?** When the whole expression is nullable.
21. **What are the accepting states of the NFA?** The positions in lastpos(root) (and q0 if nullable).
22. **Why add an end-marker `#` for the DFA?** So a DFA state can tell whether the end of the expression was reached (it contains the `#` position).
23. **What is the DFA start state?** firstpos(root of the extended tree).
24. **How is a DFA transition computed?** Union of followpos(p) for every p in the state labelled with the symbol.
25. **When is a DFA state accepting?** When it contains the end-marker position.
26. **What is a trap state?** A non-accepting state with self-loops on every symbol; it makes the DFA complete.
27. **Is the DFA built from the NFA here?** No. It is built directly from the syntax tree, independently.
28. **Why only reachable states?** The worklist only creates states discovered from the start state.
29. **Does the DFA have fewer states than the NFA?** Not always; it depends on the expression.
30. **What does a transition table show?** For each state and symbol, the destination state(s).
31. **How does the NFA simulator work?** It keeps a set of active states and replaces it with all reachable targets for each symbol.
32. **How does the DFA simulator work?** It follows exactly one transition per symbol.
33. **How does the empty string get handled?** It is accepted iff the start state is accepting.
34. **Why test the whole string?** Acceptance means the entire input is in the language, not just a substring.
35. **Are NFAs more powerful than DFAs?** No; both recognise exactly the regular languages.
36. **How do you verify correctness?** Pytest compares NFA, DFA and Python `re.fullmatch` (test oracle only) on all short strings.
37. **Why is Python's `re` not used for building automata?** The project must demonstrate the algorithms themselves.
38. **What is the precedence of operators?** Parentheses, postfix `* + ?`, concatenation, then `|`.
