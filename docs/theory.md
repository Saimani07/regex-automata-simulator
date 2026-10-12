### Key ideas in simple English
- **Alphabet / string / language:** an alphabet is a set of symbols (e.g. {a,b}); a string is a finite sequence of them; a language is a set of strings.
- **Regular expression:** a short formula describing a language using `|` (alternation), concatenation, `*`, `+`, `?` and parentheses.
- **Finite automaton:** a machine with finitely many states that reads a string symbol by symbol. One **initial** state; some **accepting** states. It accepts if it ends in an accepting state.
- **DFA:** exactly one move for every (state, symbol). **NFA:** zero, one or many moves; this is *nondeterminism*. The NFA accepts if at least one path ends in an accepting state.
- **Alternation** `r|s`: either. **Concatenation** `rs`: r then s. **Kleene star** `r*`: zero or more. **Plus** `r+`: one or more. **Optional** `r?`: zero or one.

### The four position functions
Give every literal occurrence a unique number (a *position*), left to right.
- **Nullable(n):** can the sub-expression match the empty string?
- **Firstpos(n):** positions that can start a string matched by n.
- **Lastpos(n):** positions that can end a string matched by n.
- **Followpos(p):** positions that can come right after position p.

Rules: `Alt`: nullable = either; first/last = unions. `Cat(x,y)`: nullable = both; first = first(x) (plus first(y) if x nullable); last = last(y) (plus last(x) if y nullable); for every p in last(x), followpos(p) gets first(y). `Star(x)`: nullable; for every p in last(x), followpos(p) gets first(x). `Plus(x)`: nullable = nullable(x); same followpos rule as star. `Opt(x)`: nullable.

### Algorithm 1: RE → NFA (Glushkov / position automaton, no epsilon)
States: `q0` and one state per position. `q0 --a--> p` for each p in firstpos(root) with symbol a. `p --a--> q` for each q in followpos(p) with symbol a. Accepting: lastpos(root), plus `q0` if the root is nullable. Every transition is labelled with a real symbol, so no epsilon transitions are needed.

### Algorithm 2: direct RE → DFA (followpos method)
Append a unique end-marker: `(r)#`. Start state = firstpos(root). For state S and symbol a: next(S,a) = union of followpos(p) for all p in S whose symbol is a. New sets are added to a worklist until none remain. A state is accepting if it contains the position of `#`. An empty next set goes to a **trap** state (self-looping on every symbol) so the DFA is complete. The marker is internal; it is never an input symbol.

### Difference between the two
The NFA's states are *single positions*; a symbol may lead to several states. The DFA's states are *sets of positions*; each symbol leads to exactly one state. Both come from the same parsed tree and the same nullable/first/last/follow analysis, but they are built independently, and the DFA does **not** come from the NFA. Neither is always smaller.

### Worked example: a(b|c)*
Positions: 1=a, 2=b, 3=c. Firstpos(root)={1}; lastpos={1,2,3} (the star is nullable); followpos(1)={2,3}, followpos(2)={2,3}, followpos(3)={2,3}. NFA: q0 -a-> q1; q1,q2,q3 -b-> q2; q1,q2,q3 -c-> q3; accepting q1,q2,q3. DFA (with # as position 4): S0={1}; S0 -a-> S1={2,3,4}; S1 -b-> S1, S1 -c-> S1; all other moves go to TRAP; S1 accepts because it contains 4. The live tables below are computed by the program.
