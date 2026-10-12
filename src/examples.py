"""Example gallery data."""
EXAMPLES = [
    {"regex": "a", "title": "Single symbol", "desc": "Exactly the one-letter string a.", "accept": ["a"], "reject": ["", "b", "aa"]},
    {"regex": "a|b", "title": "Alternation", "desc": "Either a or b.", "accept": ["a", "b"], "reject": ["", "ab"]},
    {"regex": "ab", "title": "Concatenation", "desc": "a followed by b.", "accept": ["ab"], "reject": ["a", "ba", "abb"]},
    {"regex": "a*", "title": "Zero or more", "desc": "Any number of a's, including none.", "accept": ["", "a", "aaa"], "reject": ["b", "ab"]},
    {"regex": "a+", "title": "One or more", "desc": "At least one a.", "accept": ["a", "aaa"], "reject": ["", "b"]},
    {"regex": "a?", "title": "Optional", "desc": "Zero or one a.", "accept": ["", "a"], "reject": ["aa", "b"]},
    {"regex": "a(b|c)*", "title": "a then b/c", "desc": "a followed by any number of b or c symbols.", "accept": ["a", "ab", "acbc"], "reject": ["", "b", "aa"]},
    {"regex": "(a|b)*abb", "title": "Ends in abb", "desc": "Strings over {a,b} that end with abb.", "accept": ["abb", "aabb", "babb"], "reject": ["", "ab", "abba"]},
    {"regex": "(0|1)*", "title": "All binary strings", "desc": "Every string of 0s and 1s, including the empty string.", "accept": ["", "0", "101"], "reject": ["2", "0a"]},
    {"regex": "(ab|ba)*", "title": "Repeated ab or ba", "desc": "Zero or more blocks, each ab or ba.", "accept": ["", "ab", "abba", "baab"], "reject": ["a", "aa", "aba"]},
]
