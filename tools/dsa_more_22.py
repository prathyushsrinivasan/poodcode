# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 22 — tries, 2D prefix sums, graph states, and word lists.
#
#   word-search-ii                   one DFS over the board guided by a trie of all the words
#   longest-string-chain             sort by length; each word extends its best one-deletion predecessor
#   short-encoding-of-words          a word hidden as another's suffix costs nothing
#   range-sum-2d                     inclusion–exclusion over a prefix-sum table
#   count-odd-sum-subarrays          an odd sum pairs an odd prefix with an even one
#   largest-color-value              DP of colour counts in topological order; a leftover node is a cycle
#   remove-max-edges-traversable     shared edges first, then each person's own union-find
#   cheapest-trip-with-discounts     Dijkstra over (city, discounts used) states
#   substring-concatenation-words    fixed-length words: a sliding window per offset
#   concatenated-words               word break, with the dictionary built from shorter words
# ===========================================================================

_p(
    "word-search-ii", "Word Search II", "Hard",
    topics=["Tries", "Backtracking"], subtopics=["Trie", "Grid DFS"], companies=["Amazon", "Microsoft", "Google"],
    shape="grid_words", ret="String", todo="insert every word into a trie; DFS from each cell, following trie children and collecting words as their nodes are reached",
    description=(
        "Find every word from the list that can be traced on the board. A word is traced through "
        "**horizontally or vertically adjacent** cells, and a cell may be used at most once "
        "within one word.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: the board rows.\n- Next line: `k`.\n- Next line: `k` distinct words.\n\n"
        "### Output\nThe words found, in lexicographic order, separated by spaces — or `NONE`."
    ),
    constraints="1 ≤ r, c ≤ 12\n1 ≤ k ≤ 3·10^4\n1 ≤ word length ≤ 10\nLowercase English letters",
    hints=[
        "Running Word Search once per word repeats the same board walks for every shared prefix.",
        "Put all words in a trie. A DFS can then follow the board and the trie together, abandoning a path the moment no word continues it.",
        "Store the complete word at its trie node. When the DFS reaches such a node, record the word and clear it so it is not reported twice.",
    ],
    opt=("O(r · c · 4 · 3^(L−1))", "O(total word length)", "Each start cell explores at most 4 · 3^(L−1) paths of length L, pruned by the trie."),
    editorial=(
        "## The one thing this teaches\n**Search for many patterns at once by sharing their "
        "prefixes.** One DFS per word re-walks the board for `cat`, `cats` and `catch` separately. "
        "A trie merges them into one path, so the board is walked once per distinct prefix.\n\n"
        "## Approach\n```java\nclass Node { Node[] next = new Node[26]; String word; }\n\n"
        "void dfs(char[][] g, int i, int j, Node parent, List<String> found) {\n"
        "    char ch = g[i][j];\n    Node node = parent.next[ch - 'a'];\n"
        "    if (node == null) return;                       // no word continues this path\n"
        "    if (node.word != null) { found.add(node.word); node.word = null; }\n"
        "    g[i][j] = '#';                                  // mark used\n"
        "    for (int[] d : DIRS) {\n        int x = i + d[0], y = j + d[1];\n"
        "        if (inside(x, y) && g[x][y] != '#') dfs(g, x, y, node, found);\n    }\n"
        "    g[i][j] = ch;                                   // unmark on the way back\n}\n```\n\n"
        "## Why clear the word\nThe same word can often be traced along several paths. Clearing "
        "`node.word` after the first report removes duplicates without a set.\n\n"
        "## Pruning further\nWhen a trie node has no children and no word left, removing it from "
        "its parent stops later DFS calls from entering a dead branch — a large speedup on boards "
        "where most words are found early."
    ),
    py='''
def solve(g, words):
    r, c = len(g), len(g[0])

    def traced(word):
        def go(i, j, pos, used):
            if g[i][j] != word[pos]:
                return False
            if pos == len(word) - 1:
                return True
            used.add((i, j))
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < r and 0 <= y < c and (x, y) not in used and go(x, y, pos + 1, used):
                    return True
            used.discard((i, j))
            return False
        return any(go(i, j, 0, set()) for i in range(r) for j in range(c))

    found = sorted(w for w in words if traced(w))
    return " ".join(found) if found else "NONE"
''',
    java='''
    static class Node { Node[] next = new Node[26]; String word; }

    static void dfs(char[][] g, int i, int j, Node parent, List<String> found) {
        char ch = g[i][j];
        Node node = parent.next[ch - 'a'];
        if (node == null) return;
        if (node.word != null) { found.add(node.word); node.word = null; }
        g[i][j] = '#';
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        for (int[] d : dirs) {
            int x = i + d[0], y = j + d[1];
            if (x >= 0 && y >= 0 && x < g.length && y < g[0].length && g[x][y] != '#') dfs(g, x, y, node, found);
        }
        g[i][j] = ch;
    }

    static String solve(char[][] g, String[] words) {
        Node root = new Node();
        for (String w : words) {
            Node cur = root;
            for (char ch : w.toCharArray()) {
                if (cur.next[ch - 'a'] == null) cur.next[ch - 'a'] = new Node();
                cur = cur.next[ch - 'a'];
            }
            cur.word = w;
        }
        List<String> found = new ArrayList<>();
        for (int i = 0; i < g.length; i++)
            for (int j = 0; j < g[0].length; j++) dfs(g, i, j, root, found);
        if (found.isEmpty()) return "NONE";
        Collections.sort(found);
        return String.join(" ", found);
    }
''',
    examples=[
        ("Example 1", "4 4\noaan\netae\nihkr\niflv\n4\noath pea eat rain\n"),
        ("Example 2", "2 2\nab\ncd\n1\nabcb\n"),
    ],
    hidden=[
        ("Single cell", "1 1\na\n2\na b\n"),
        ("Cells cannot be reused", "2 2\naa\naa\n2\naaaaa aaaa\n"),
        ("Words sharing a prefix", "2 3\nabc\nfed\n4\nab abc abcdef abcdefa\n"),
        ("Many paths to one word", "3 3\naaa\naba\naaa\n2\naba bab\n"),
    ],
    expl=[
        "\"oath\" starts at the top-left o and goes right, down, down; \"eat\" runs right to left along the second row. \"pea\" and \"rain\" cannot be traced.",
        "\"abcb\" would need to reuse the b cell.",
    ],
    prereqs=[
        ("trie", "A prefix tree whose nodes carry the complete word that ends there."),
        ("backtracking", "Marking a cell as used on the way down and restoring it on the way back."),
    ],
)

_p(
    "longest-string-chain", "Longest String Chain", "Medium",
    topics=["Dynamic Programming", "Hashing", "Strings"], subtopics=["1D DP", "Sort by Length"], companies=["Google", "Amazon"],
    shape="words", ret="int", todo="sort words by length; best[w] = 1 + max best of the words obtained by deleting one character from w",
    description=(
        "Word `A` is a **predecessor** of word `B` if inserting exactly one letter anywhere in `A` "
        "gives `B`. A chain is a sequence of words where each is a predecessor of the next. Print "
        "the length of the longest chain using words from the list.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` distinct words.\n\n"
        "### Output\nThe longest chain length."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ word length ≤ 16\nLowercase English letters",
    hints=[
        "A chain is a path in a graph whose edges go from shorter words to longer ones — a DAG, ordered by length.",
        "Checking \"is A a predecessor of B\" for every pair is O(n² · L). Go the other way: from B, the candidates are the L words made by deleting one letter.",
        "Process words by increasing length, keeping best[word] in a hash map: best[B] = 1 + max best[B with one letter deleted] over those present.",
    ],
    opt=("O(n log n + n · L²)", "O(n · L)", "Sorting, then L deletions per word, each building an O(L) string."),
    editorial=(
        "## The one thing this teaches\n**Generate predecessors instead of testing pairs.** A "
        "word of length L has at most L predecessors, and they are cheap to construct. Looking "
        "them up in a hash map beats comparing every pair of words.\n\n"
        "## Approach\n```java\nArrays.sort(words, Comparator.comparingInt(String::length));\n"
        "Map<String, Integer> best = new HashMap<>();\nint answer = 0;\nfor (String w : words) {\n"
        "    int b = 1;\n    for (int i = 0; i < w.length(); i++) {\n"
        "        String pred = w.substring(0, i) + w.substring(i + 1);\n"
        "        b = Math.max(b, best.getOrDefault(pred, 0) + 1);\n    }\n"
        "    best.put(w, b);\n    answer = Math.max(answer, b);\n}\n```\n\n"
        "## Why sorting by length is enough\nA predecessor is exactly one letter shorter, so it is "
        "processed before the word that needs it. Words of equal length never depend on each "
        "other — any order among them works.\n\n"
        "## Walkthrough (Example 1)\n`a`, `b` → 1. `ba` → 2 (from either). `bca`, `bda` → 3 "
        "(from `ba`). `bdca` → 4 (from `bca` or `bda`)."
    ),
    py='''
def solve(words):
    from functools import lru_cache
    present = set(words)

    @lru_cache(maxsize=None)
    def longest_ending(w):
        best = 1
        for i in range(len(w)):
            shorter = w[:i] + w[i + 1:]
            if shorter in present:
                best = max(best, 1 + longest_ending(shorter))
        return best

    return max(longest_ending(w) for w in words)
''',
    java='''
    static int solve(String[] words) {
        Arrays.sort(words, Comparator.comparingInt(String::length));
        HashMap<String, Integer> best = new HashMap<>();
        int answer = 0;
        for (String w : words) {
            int b = 1;
            for (int i = 0; i < w.length(); i++) {
                String pred = w.substring(0, i) + w.substring(i + 1);
                b = Math.max(b, best.getOrDefault(pred, 0) + 1);
            }
            best.put(w, b);
            answer = Math.max(answer, b);
        }
        return answer;
    }
''',
    examples=[
        ("Example 1", "6\na b ba bca bda bdca\n"),
        ("Example 2", "5\nxbc pcxbcf xb cxbc pcxbc\n"),
    ],
    hidden=[
        ("One word", "1\nabcd\n"),
        ("Rearranged letters do not count", "2\nabcd dbqca\n"),
        ("Branches", "4\na ab ac abc\n"),
        ("Gap in lengths", "3\na abc abcd\n"),
    ],
    expl=[
        "a → ba → bda → bdca.",
        "xb → xbc → cxbc → pcxbc → pcxbcf.",
    ],
    prereqs=[
        ("dp", "best[word] built from the best of its predecessors, in order of length."),
        ("hashing", "Looking up generated predecessor strings in a map."),
    ],
)

_p(
    "short-encoding-of-words", "Short Encoding of Words", "Medium",
    topics=["Tries", "Strings"], subtopics=["Suffix Trie"], companies=["Google"],
    shape="words", ret="int", todo="a word that is a suffix of another costs nothing; every other distinct word costs its length + 1",
    description=(
        "A **reference string** encodes a list of words: it is a string ending in `#`, and every "
        "word can be read starting at some index and ending just before a `#`. For example "
        "`time#bell#` encodes `time`, `me` and `bell`. Print the length of the shortest reference "
        "string that encodes all the words.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` words (they may repeat).\n\n"
        "### Output\nThe minimum length."
    ),
    constraints="1 ≤ n ≤ 2000\n1 ≤ word length ≤ 7\nLowercase English letters",
    hints=[
        "A word read \"ending just before a #\" is a suffix of some segment. So `me` is free once `time#` is present.",
        "Only words that are not a suffix of another word need their own segment, each costing length + 1.",
        "Reverse each word: suffixes become prefixes. Insert reversed words in a trie — the words that end at leaves are the ones that pay. Or sort the reversed words and compare neighbours.",
    ],
    opt=("O(total length)", "O(total length)", "A trie of reversed words; sorting instead costs an extra log factor."),
    editorial=(
        "## The one thing this teaches\n**Reverse to turn suffixes into prefixes.** Tries answer "
        "prefix questions. Reversing every word makes \"is this a suffix of that\" a prefix "
        "question — and in a trie of reversed words, the words that must be written out are "
        "exactly those ending at leaves.\n\n"
        "## Approach (sorted reversals)\n```java\nString[] rev = reversed copies of the words;\n"
        "Arrays.sort(rev);\nint total = 0;\nfor (int i = 0; i < rev.length; i++)\n"
        "    if (i + 1 == rev.length || !rev[i + 1].startsWith(rev[i]))   // not a prefix of a longer one\n"
        "        total += rev[i].length() + 1;\n```\n\n"
        "## Why checking only the next word works\nIn sorted order, every string that starts "
        "with `x` comes immediately after `x`, contiguously. If any word extends `x`, the very "
        "next one does. Duplicates are handled too: an identical copy \"starts with\" `x`.\n\n"
        "## Walkthrough: time me bell\nReversed and sorted: `em`, `emit`, `lleb`. `em` is a prefix of "
        "`emit` → free. `emit` → 5. `lleb` → 5. Total 10: `time#bell#`."
    ),
    py='''
def solve(words):
    keep = set(words)
    for w in words:
        for i in range(1, len(w)):
            keep.discard(w[i:])
    return sum(len(w) + 1 for w in keep)
''',
    java='''
    static int solve(String[] words) {
        int n = words.length;
        String[] rev = new String[n];
        for (int i = 0; i < n; i++) rev[i] = new StringBuilder(words[i]).reverse().toString();
        Arrays.sort(rev);
        int total = 0;
        for (int i = 0; i < n; i++)
            if (i + 1 == n || !rev[i + 1].startsWith(rev[i])) total += rev[i].length() + 1;
        return total;
    }
''',
    examples=[("Example 1", "3\ntime me bell\n"), ("Example 2", "1\nt\n")],
    hidden=[
        ("Repeated word", "2\nme me\n"),
        ("Nested suffixes", "3\nabc bc c\n"),
        ("Nothing shared", "3\nab cd ef\n"),
        ("Prefix is not a suffix", "2\ntime tim\n"),
        ("Suffix of a longer word", "2\natime time\n"),
    ],
    expl=[
        "\"time#bell#\": me is read inside time#.",
        "\"t#\".",
    ],
    prereqs=[
        ("trie", "A trie of reversed words, where the paying words end at leaves."),
        ("sorting", "Sorted order places every extension of a string right after it."),
    ],
)

_p(
    "range-sum-2d", "Range Sum Query 2D", "Medium",
    topics=["Prefix Sums", "Arrays"], subtopics=["2D Prefix Sums"], companies=["Meta", "Amazon"],
    shape="matrix_q", ret="String", todo="P[i][j] = sum of the rectangle above-left of (i, j); each query is P[r2+1][c2+1] − P[r1][c2+1] − P[r2+1][c1] + P[r1][c1]",
    description=(
        "Answer many queries of the form: what is the sum of the sub-rectangle with top-left "
        "corner `(r1, c1)` and bottom-right corner `(r2, c2)`, inclusive? Rows and columns are "
        "0-indexed.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers each.\n- Next line: `q`.\n"
        "- Next `q` lines: `r1 c1 r2 c2`.\n\n"
        "### Output\n`q` lines: the sums."
    ),
    constraints="1 ≤ r, c ≤ 200\n-10^5 ≤ value ≤ 10^5\n1 ≤ q ≤ 10^4\n0 ≤ r1 ≤ r2 < r, 0 ≤ c1 ≤ c2 < c",
    hints=[
        "Summing each rectangle directly is O(r · c) per query.",
        "Precompute P[i][j] = the sum of all cells in rows < i and columns < j, with an extra zero row and column.",
        "P[i+1][j+1] = m[i][j] + P[i][j+1] + P[i+1][j] − P[i][j]. A query subtracts the strips above and to the left, then adds back their overlap.",
    ],
    opt=("O(r · c + q)", "O(r · c)", "One table build, then O(1) per query."),
    editorial=(
        "## The one thing this teaches\n**Inclusion–exclusion lifts prefix sums to two "
        "dimensions.** In one dimension a range is `P[r+1] − P[l]`. In two, a rectangle is the big "
        "corner block, minus the block above, minus the block to the left, plus the corner that "
        "was subtracted twice.\n\n"
        "## Approach\n```java\nlong[][] P = new long[r + 1][c + 1];\n"
        "for (int i = 0; i < r; i++)\n    for (int j = 0; j < c; j++)\n"
        "        P[i + 1][j + 1] = m[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j];\n\n"
        "long query(int r1, int c1, int r2, int c2) {\n"
        "    return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1];\n}\n```\n\n"
        "## The picture\n```\nP[r2+1][c2+1]   =  A | B\n                   --+--\n                   C | Q     ← Q is the query\n```\n"
        "`P[r1][c2+1]` is `A + B`, `P[r2+1][c1]` is `A + C`, and `P[r1][c1]` is `A`. So "
        "`(A+B+C+Q) − (A+B) − (A+C) + A = Q`.\n\n"
        "## The padding row\nThe extra zero row and column mean a query touching row 0 or column 0 "
        "needs no special case."
    ),
    py='''
def solve(m, queries):
    out = []
    for r1, c1, r2, c2 in queries:
        out.append(sum(m[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1)))
    return "\\n".join(map(str, out))
''',
    java='''
    static String solve(int[][] m, int[][] queries) {
        int r = m.length, c = m[0].length;
        long[][] P = new long[r + 1][c + 1];
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                P[i + 1][j + 1] = m[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j];
        StringBuilder sb = new StringBuilder();
        for (int[] q : queries) {
            long s = P[q[2] + 1][q[3] + 1] - P[q[0]][q[3] + 1] - P[q[2] + 1][q[1]] + P[q[0]][q[1]];
            if (sb.length() > 0) sb.append('\\n');
            sb.append(s);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5 5\n3 0 1 4 2\n5 6 3 2 1\n1 2 0 1 5\n4 1 0 1 7\n1 0 3 0 5\n3\n2 1 4 3\n1 1 2 2\n1 2 2 4\n"),
        ("Example 2", "1 1\n-7\n1\n0 0 0 0\n"),
    ],
    hidden=[
        ("Whole matrix", "2 3\n1 2 3\n4 5 6\n1\n0 0 1 2\n"),
        ("Single cells", "2 2\n1 -2\n-3 4\n4\n0 0 0 0\n0 1 0 1\n1 0 1 0\n1 1 1 1\n"),
        ("One row and one column", "3 3\n1 2 3\n4 5 6\n7 8 9\n2\n1 0 1 2\n0 2 2 2\n"),
        ("Large values", "2 2\n100000 100000\n100000 100000\n1\n0 0 1 1\n"),
    ],
    expl=[
        "Rows 2–4, columns 1–3: 2+0+1 + 1+0+1 + 0+3+0 = 8. Then 6+3+2+0 = 11 and 3+2+1+0+1+5 = 12.",
        "The only cell is −7.",
    ],
    prereqs=[
        ("prefix_sum", "One-dimensional prefix sums, extended with inclusion–exclusion."),
        ("grid", "Row and column indexing with a padded border."),
    ],
)

_p(
    "count-odd-sum-subarrays", "Count Subarrays with Odd Sum", "Medium",
    topics=["Prefix Sums", "Math"], subtopics=["Parity Counting"], companies=["Amazon"],
    shape="arr", ret="long", todo="count prefix sums by parity (the empty prefix is even); an odd prefix pairs with every earlier even one and vice versa",
    description=(
        "Print the number of non-empty contiguous subarrays whose sum is **odd**.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe count."
    ),
    constraints="1 ≤ n ≤ 10^5\n-100 ≤ a[i] ≤ 100",
    hints=[
        "sum(a[i..j]) = P[j+1] − P[i]. A difference is odd exactly when the two prefix sums have different parity.",
        "So you do not need the prefix sums themselves — only how many earlier prefixes were even and how many were odd.",
        "Start with one even prefix (the empty one). At each index, add the count of prefixes of the opposite parity, then record this one.",
    ],
    opt=("O(n)", "O(1)", "Two counters and a running parity."),
    editorial=(
        "## The one thing this teaches\n**Prefix sums only need to remember what the question "
        "asks about.** Subarray Sum Equals K keeps a map of exact sums. Here only parity matters, "
        "so the map collapses to two counters.\n\n"
        "## Approach\n```java\nlong even = 1, odd = 0, count = 0;   // the empty prefix is even\nint parity = 0;\n"
        "for (int x : a) {\n    parity ^= x & 1;                   // & 1 is safe for negatives; % 2 is not\n"
        "    if (parity == 1) { count += even; odd++; }\n    else             { count += odd;  even++; }\n}\n```\n\n"
        "## Negative numbers\nIn Java, `-3 % 2` is `-1`, not `1`. `x & 1` reads the lowest bit, "
        "which is 1 for every odd number in two's complement, negative or not.\n\n"
        "## Walkthrough: 1 3 5\nParities of prefixes: 0 (empty), 1, 0, 1. The odd prefixes at "
        "positions 1 and 3 pair with the even ones before them: 1 + 2 = 3 from odd prefixes, plus "
        "1 from the even prefix at position 2 pairing with the odd one at 1: 4."
    ),
    py='''
def solve(a):
    total = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s % 2:
                total += 1
    return total
''',
    java='''
    static long solve(int[] a) {
        long even = 1, odd = 0, count = 0;
        int parity = 0;
        for (int x : a) {
            parity ^= x & 1;
            if (parity == 1) { count += even; odd++; }
            else { count += odd; even++; }
        }
        return count;
    }
''',
    examples=[("Example 1", "3\n1 3 5\n"), ("Example 2", "3\n2 4 6\n")],
    hidden=[
        ("Mixed", "7\n1 2 3 4 5 6 7\n"),
        ("Single odd negative", "1\n-3\n"),
        ("Negatives and zero", "4\n-1 -2 3 0\n"),
        ("All odd", "4\n1 1 1 1\n"),
    ],
    expl=[
        "[1], [3], [5] and [1, 3, 5] have odd sums; [1, 3] and [3, 5] are even.",
        "Every value is even, so every sum is even.",
    ],
    prereqs=[
        ("prefix_sum", "A subarray sum as a difference of prefix sums."),
        ("bit_manip", "Reading parity with & 1, which also works for negative numbers."),
    ],
)

_p(
    "largest-color-value", "Largest Color Value in a Directed Graph", "Hard",
    topics=["Graphs", "Topological Sort", "Dynamic Programming"], subtopics=["DP on DAG", "Cycle Detection"], companies=["Google"],
    shape="str_pairs", ret="int", todo="Kahn's algorithm carrying cnt[v][colour] = most nodes of that colour on a path ending at v; unprocessed nodes mean a cycle",
    description=(
        "A directed graph has `n` nodes; node `i` has colour `s[i]`, a lowercase letter. The "
        "**colour value** of a path is the number of nodes on it with the path's most frequent "
        "colour. Print the largest colour value of any path — or `-1` if the graph contains a "
        "cycle.\n\n"
        "### Input\n- Line 1: `s` (its length is `n`).\n- Line 2: `m`.\n- Next `m` lines: `u v`, an edge from `u` to `v`.\n\n"
        "### Output\nThe largest colour value, or `-1`."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 10^5\n0 ≤ u, v < n (self-loops possible)",
    hints=[
        "A cycle lets a path repeat nodes forever, which is why the answer is then −1. Kahn's algorithm detects a cycle for free: some node never reaches in-degree 0.",
        "For a single colour, \"most nodes of colour c on a path ending at v\" is a longest-path DP in topological order.",
        "Run all 26 colours together: cnt[v][c] = max over edges u → v of cnt[u][c], then add 1 for v's own colour when v is dequeued.",
    ],
    opt=("O((n + m) · 26)", "O(n · 26)", "Kahn's algorithm, with 26 counters carried along each edge."),
    editorial=(
        "## The one thing this teaches\n**Split a hard maximum into per-value subproblems.** "
        "\"The most frequent colour along the best path\" mixes two choices. Fixing the colour "
        "makes it a plain longest path; doing all 26 colours in one topological pass costs a "
        "constant factor.\n\n"
        "## Approach\n```java\nint[][] cnt = new int[n][26];\n// queue every node with in-degree 0\nint seen = 0, best = 0;\n"
        "while (!q.isEmpty()) {\n    int u = q.poll();\n    seen++;\n"
        "    best = Math.max(best, ++cnt[u][s.charAt(u) - 'a']);     // count u itself\n"
        "    for (int v : adj[u]) {\n        for (int c = 0; c < 26; c++) cnt[v][c] = Math.max(cnt[v][c], cnt[u][c]);\n"
        "        if (--indeg[v] == 0) q.add(v);\n    }\n}\nreturn seen == n ? best : -1;\n```\n\n"
        "## When u's own colour is added\nAt dequeue time, every predecessor of `u` has already "
        "pushed its counts into `cnt[u]`, so adding `u`'s colour then is final. Adding it earlier "
        "would be overwritten by a later `max`.\n\n"
        "## Cycle detection comes free\nNodes on a cycle (or downstream of one) never reach "
        "in-degree 0, so `seen < n` exactly when a cycle exists — including a self-loop."
    ),
    py='''
def solve(s, p):
    import sys
    sys.setrecursionlimit(10000)
    n = len(s)
    out = [[] for _ in range(n)]
    for u, v in p:
        out[u].append(v)
    state = [0] * n          # 0 unvisited, 1 on the stack, 2 done

    def has_cycle(u):
        state[u] = 1
        for v in out[u]:
            if state[v] == 1 or (state[v] == 0 and has_cycle(v)):
                return True
        state[u] = 2
        return False

    if any(state[u] == 0 and has_cycle(u) for u in range(n)):
        return -1
    memo = {}

    def best_from(u, colour):
        if (u, colour) not in memo:
            here = 1 if s[u] == colour else 0
            memo[(u, colour)] = here + max([0] + [best_from(v, colour) for v in out[u]])
        return memo[(u, colour)]

    return max(best_from(u, colour) for colour in set(s) for u in range(n))
''',
    java='''
    static int solve(String s, int[][] p) {
        int n = s.length();
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : p) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
        int[][] cnt = new int[n][26];
        int seen = 0, best = 0;
        while (!q.isEmpty()) {
            int u = q.poll();
            seen++;
            best = Math.max(best, ++cnt[u][s.charAt(u) - 'a']);
            for (int v : adj.get(u)) {
                for (int c = 0; c < 26; c++) cnt[v][c] = Math.max(cnt[v][c], cnt[u][c]);
                if (--indeg[v] == 0) q.add(v);
            }
        }
        return seen == n ? best : -1;
    }
''',
    examples=[
        ("Example 1", "abaca\n4\n0 1\n0 2\n2 3\n3 4\n"),
        ("Example 2", "a\n1\n0 0\n"),
    ],
    hidden=[
        ("No edges", "ab\n0\n"),
        ("One colour chain", "aaaa\n3\n0 1\n1 2\n2 3\n"),
        ("Cycle away from the start", "abc\n3\n0 1\n1 2\n2 1\n"),
        ("Diamond", "abba\n4\n0 1\n0 2\n1 3\n2 3\n"),
        ("Best colour is not the start's", "abbbc\n4\n0 1\n1 2\n2 3\n3 4\n"),
    ],
    expl=[
        "0 → 2 → 3 → 4 has colours a, a, c, a: three a's.",
        "The self-loop on node 0 is a cycle.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm, which also reveals a cycle when nodes are left over."),
        ("dp", "Longest-path counts pushed along edges in topological order."),
    ],
)

_p(
    "remove-max-edges-traversable", "Remove Max Edges to Keep Graph Traversable", "Hard",
    topics=["Union-Find", "Graphs"], subtopics=["Spanning Forest"], companies=["Google", "Uber"],
    shape="wgraph", ret="int", todo="union type-3 edges first in both structures, then type 1 for Alice and type 2 for Bob; count the edges that joined nothing",
    description=(
        "An undirected graph has `n` nodes and edges of three types:\n\n"
        "- type 1: only Alice may use it,\n- type 2: only Bob may use it,\n- type 3: both may use it.\n\n"
        "Remove as many edges as possible so that both Alice and Bob can still reach every node "
        "from every other node. Print the number removed, or `-1` if one of them cannot traverse "
        "the full graph even with every edge.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v type`.\n\n"
        "### Output\nThe maximum number of removable edges, or `-1`."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 10^5\n0 ≤ u, v < n, u ≠ v\ntype ∈ {1, 2, 3}",
    hints=[
        "Each person needs a spanning tree: n − 1 edges they can use. The goal is to share as many of those as possible.",
        "A type-3 edge can serve both trees at once, so it is never worse to take it first.",
        "Keep one union-find per person. Add every useful type-3 edge to both, then type 1 to Alice's and type 2 to Bob's. Edges that union nothing are removable.",
    ],
    opt=("O((n + m) · α(n))", "O(n)", "Two union-find structures, each edge offered at most twice."),
    editorial=(
        "## The one thing this teaches\n**Greedy spanning forests prefer the edge that does more "
        "work.** Every spanning tree has n − 1 edges; what varies is how many can be shared. A "
        "type-3 edge fills a slot in both trees, so using shared edges first maximises the "
        "overlap — Kruskal's idea, where the \"weight\" is how many people an edge helps.\n\n"
        "## Approach\n```java\nDSU alice = new DSU(n), bob = new DSU(n);\nint used = 0;\n"
        "for (edge of type 3) {\n    boolean a = alice.union(u, v), b = bob.union(u, v);\n"
        "    if (a || b) used++;                          // useful to at least one of them\n}\n"
        "for (edge of type 1) if (alice.union(u, v)) used++;\n"
        "for (edge of type 2) if (bob.union(u, v)) used++;\n"
        "if (alice.components > 1 || bob.components > 1) return -1;\nreturn m - used;\n```\n\n"
        "## Why type 3 first is safe\nAfter the type-3 pass, both structures hold the same forest "
        "F. Any spanning tree for Alice can be rearranged to contain F — swapping one of her own "
        "edges for a shared one keeps her connected and never costs Bob anything.\n\n"
        "## Counting directly\nThe type-3 forest has `n − c₃` edges, where c₃ is the number of "
        "components using only shared edges. Each person then needs `c₃ − 1` private edges, so "
        "the kept total is `(n − c₃) + 2(c₃ − 1)`."
    ),
    py='''
def solve(n, edges):
    def components(allowed):
        adj = [[] for _ in range(n)]
        for u, v, t in edges:
            if t in allowed:
                adj[u].append(v)
                adj[v].append(u)
        seen = [False] * n
        count = 0
        for s in range(n):
            if not seen[s]:
                count += 1
                seen[s] = True
                stack = [s]
                while stack:
                    u = stack.pop()
                    for v in adj[u]:
                        if not seen[v]:
                            seen[v] = True
                            stack.append(v)
        return count

    if components({1, 3}) > 1 or components({2, 3}) > 1:
        return -1
    c3 = components({3})
    kept = (n - c3) + 2 * (c3 - 1)
    return len(edges) - kept
''',
    java='''
    static int find(int[] parent, int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static boolean union(int[] parent, int[] comps, int a, int b) {
        int ra = find(parent, a), rb = find(parent, b);
        if (ra == rb) return false;
        parent[ra] = rb;
        comps[0]--;
        return true;
    }

    static int solve(int n, int[][] edges) {
        int[] alice = new int[n], bob = new int[n];
        for (int i = 0; i < n; i++) { alice[i] = i; bob[i] = i; }
        int[] ca = {n}, cb = {n};
        int used = 0;
        for (int[] e : edges)
            if (e[2] == 3) {
                boolean a = union(alice, ca, e[0], e[1]);
                boolean b = union(bob, cb, e[0], e[1]);
                if (a || b) used++;
            }
        for (int[] e : edges) {
            if (e[2] == 1 && union(alice, ca, e[0], e[1])) used++;
            if (e[2] == 2 && union(bob, cb, e[0], e[1])) used++;
        }
        if (ca[0] > 1 || cb[0] > 1) return -1;
        return edges.length - used;
    }
''',
    examples=[
        ("Example 1", "4 6\n0 1 3\n1 2 3\n0 2 1\n1 3 1\n0 1 1\n2 3 2\n"),
        ("Example 2", "4 4\n0 1 3\n1 2 3\n0 3 1\n0 3 2\n"),
        ("Example 3", "4 3\n1 2 3\n0 1 1\n2 3 2\n"),
    ],
    hidden=[
        ("Single node", "1 0\n"),
        ("Shared edge makes private ones redundant", "2 3\n0 1 3\n0 1 1\n0 1 2\n"),
        ("Separate private trees", "3 4\n0 1 1\n1 2 1\n0 1 2\n1 2 2\n"),
        ("Bob is cut off", "3 2\n0 1 3\n1 2 1\n"),
        ("Redundant shared edge", "3 4\n0 1 3\n1 2 3\n0 2 3\n0 2 1\n"),
    ],
    expl=[
        "Shared edges 0–1 and 1–2 serve both; Alice adds 1–3, Bob adds 2–3. The edges 0–2 and 0–1 for Alice are redundant.",
        "Every edge is needed: the shared path 0–1–2 plus one private edge each to reach node 3.",
        "Alice cannot reach node 3 at all.",
    ],
    prereqs=[
        ("union_find", "Union returning whether it joined two components, with a component count."),
        ("greedy", "Taking the edges that help both people before those that help one."),
    ],
)

_p(
    "cheapest-trip-with-discounts", "Cheapest Trip with Discounts", "Medium",
    topics=["Graphs", "Shortest Paths", "Heaps"], subtopics=["Dijkstra", "State Expansion"], companies=["Google", "Amazon"],
    shape="wgraph_k", ret="long", todo="Dijkstra over states (city, discounts used): each road can be taken at full toll or, if discounts remain, at toll / 2",
    description=(
        "Cities `0` to `n − 1` are joined by two-way roads with tolls. You hold `k` discounts; "
        "using one on a road halves its toll, rounding down. Each road use takes at most one "
        "discount. Print the minimum cost to travel from city `0` to city `n − 1`, or `-1` if it "
        "cannot be reached.\n\n"
        "### Input\n- Line 1: `n m k`.\n- Next `m` lines: `u v toll`.\n\n"
        "### Output\nThe minimum cost, or `-1`."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ m ≤ 1000\n0 ≤ toll ≤ 10^5\n0 ≤ k ≤ 500",
    hints=[
        "Plain Dijkstra on cities fails: arriving at a city cheaply with no discounts left is not always better than arriving dearer with discounts in hand.",
        "Make the discounts part of the node. State (city, used) with used from 0 to k.",
        "From (u, j), a road to v with toll t leads to (v, j) at cost t and, if j < k, to (v, j + 1) at cost t / 2. Answer: the first time any (n − 1, j) is popped.",
    ],
    opt=("O((n · k + m · k) log(n · k))", "O(n · k)", "Dijkstra on a graph with k + 1 layers."),
    editorial=(
        "## The one thing this teaches\n**When a greedy search forgets something that matters, "
        "put it in the state.** Dijkstra keeps one best distance per node. Here \"best\" depends "
        "on how many discounts remain, so the node becomes `(city, discounts used)` — a layered "
        "graph where a discounted road steps up one layer.\n\n"
        "## Approach\n```java\nlong[][] dist = new long[n][k + 1];   // filled with infinity\n"
        "dist[0][0] = 0;\npq.add(new long[]{0, 0, 0});           // cost, city, used\n"
        "while (!pq.isEmpty()) {\n    long[] cur = pq.poll();\n    int u = (int) cur[1], j = (int) cur[2];\n"
        "    if (cur[0] > dist[u][j]) continue;               // stale entry\n"
        "    if (u == n - 1) return cur[0];\n    for (int[] e : adj[u]) {\n"
        "        relax(e.to, j, cur[0] + e.toll);\n"
        "        if (j < k) relax(e.to, j + 1, cur[0] + e.toll / 2);\n    }\n}\nreturn -1;\n```\n\n"
        "## Why the first pop of city n − 1 is the answer\nAll states of the destination are "
        "separate nodes, and Dijkstra pops states in increasing cost. The first one of any layer "
        "is the cheapest overall.\n\n"
        "## Walkthrough (Example 1)\n0 → 1 costs 4. 1 → 4 costs 11, or 5 with the discount. "
        "Total 9 — cheaper than 0 → 1 → 2 → 3 → 4 at 4 + 3 + 3 + 2 = 12 with no discount, or 10 "
        "with the discount on the 4."
    ),
    py='''
def solve(n, edges, k):
    INF = float("inf")
    dist = [[INF] * (k + 1) for _ in range(n)]
    dist[0][0] = 0
    changed = True
    while changed:
        changed = False
        for u, v, t in edges:
            for a, b in ((u, v), (v, u)):
                for j in range(k + 1):
                    if dist[a][j] == INF:
                        continue
                    if dist[a][j] + t < dist[b][j]:
                        dist[b][j] = dist[a][j] + t
                        changed = True
                    if j < k and dist[a][j] + t // 2 < dist[b][j + 1]:
                        dist[b][j + 1] = dist[a][j] + t // 2
                        changed = True
    best = min(dist[n - 1])
    return -1 if best == INF else best
''',
    java='''
    static long solve(int n, int[][] edges, int k) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); adj.get(e[1]).add(new int[]{e[0], e[2]}); }
        long[][] dist = new long[n][k + 1];
        for (long[] row : dist) Arrays.fill(row, Long.MAX_VALUE);
        PriorityQueue<long[]> pq = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
        dist[0][0] = 0;
        pq.add(new long[]{0, 0, 0});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            int u = (int) cur[1], j = (int) cur[2];
            if (cur[0] > dist[u][j]) continue;
            if (u == n - 1) return cur[0];
            for (int[] e : adj.get(u)) {
                long full = cur[0] + e[1];
                if (full < dist[e[0]][j]) { dist[e[0]][j] = full; pq.add(new long[]{full, e[0], j}); }
                if (j < k) {
                    long half = cur[0] + e[1] / 2;
                    if (half < dist[e[0]][j + 1]) { dist[e[0]][j + 1] = half; pq.add(new long[]{half, e[0], j + 1}); }
                }
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", "5 5 1\n0 1 4\n2 1 3\n1 4 11\n3 2 3\n3 4 2\n"),
        ("Example 2", "4 5 20\n1 3 17\n1 2 7\n3 2 5\n0 1 6\n3 0 20\n"),
        ("Example 3", "4 2 0\n0 1 3\n2 3 2\n"),
    ],
    hidden=[
        ("Start is the destination", "1 0 0\n"),
        ("No discounts", "2 1 0\n0 1 7\n"),
        ("More discounts than roads", "2 1 3\n0 1 7\n"),
        ("Discount changes the best route", "3 3 1\n0 1 10\n1 2 10\n0 2 30\n"),
        ("Odd tolls round down", "3 2 2\n0 1 5\n1 2 3\n"),
    ],
    expl=[
        "0 → 1 → 4, with the discount on the 11: 4 + 5 = 9.",
        "0 → 1 → 2 → 3 with discounts on every road: 3 + 3 + 2 = 8.",
        "City 3 is not connected to city 0.",
    ],
    prereqs=[
        ("dijkstra", "Dijkstra with a priority queue and stale-entry skipping."),
        ("graph_repr", "An adjacency list for two-way roads, and states that pair a city with a count."),
    ],
)

_p(
    "substring-concatenation-words", "Substring with Concatenation of All Words", "Hard",
    topics=["Sliding Window", "Hashing", "Strings"], subtopics=["Fixed-length Tokens"], companies=["Amazon", "Apple"],
    shape="str_list", ret="String", todo="for each offset 0..L−1, slide a window over word-sized chunks, keeping chunk counts against the word counts",
    description=(
        "All words have the same length. Find every index in `s` where a substring starts that "
        "is a concatenation of **all** the words, each used exactly as many times as it appears "
        "in the list, in any order.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `k`.\n- Line 3: the `k` words.\n\n"
        "### Output\nThe starting indices in increasing order, separated by spaces — or `NONE`."
    ),
    constraints="1 ≤ |s| ≤ 10^4\n1 ≤ k ≤ 5000\n1 ≤ word length ≤ 30, all equal\nLowercase English letters",
    hints=[
        "Checking every start with a fresh count costs O(|s| · k · L).",
        "Every match aligns with word boundaries. Chunks starting at offsets 0, L, 2L, … form one sequence; offsets 1, L+1, … another. There are only L such sequences.",
        "On each sequence, slide a window of chunks. Add the chunk on the right; while it is over-used, drop chunks from the left. A window of exactly k chunks is a match.",
    ],
    opt=("O(|s| · L)", "O(k)", "L sliding passes, each over |s| / L chunks of length L."),
    editorial=(
        "## The one thing this teaches\n**Fixed-size tokens make a sliding window work on a "
        "string.** Characters do not line up with words, but word-length chunks do — once you "
        "fix the starting offset. Each of the L offsets gives an ordinary sliding-window problem "
        "over tokens.\n\n"
        "## Approach\n```java\nMap<String, Integer> need = counts of words;\n"
        "for (int off = 0; off < L; off++) {\n    Map<String, Integer> have = new HashMap<>();\n    int left = off, used = 0;\n"
        "    for (int right = off; right + L <= n; right += L) {\n"
        "        String w = s.substring(right, right + L);\n"
        "        if (!need.containsKey(w)) { have.clear(); used = 0; left = right + L; continue; }\n"
        "        have.merge(w, 1, Integer::sum); used++;\n"
        "        while (have.get(w) > need.get(w)) {             // too many w: shrink from the left\n"
        "            have.merge(s.substring(left, left + L), -1, Integer::sum); used--; left += L;\n        }\n"
        "        if (used == k) result.add(left);\n    }\n}\n```\n\n"
        "## Why the window never needs to reset on overuse\nAn over-used word is fixed by "
        "dropping from the left until one copy of it leaves. Everything between is still valid, "
        "so the window keeps its progress. Only a chunk that is not a word at all resets it.\n\n"
        "## Sorting the output\nMatches from different offsets interleave, so collect them and "
        "sort before printing."
    ),
    py='''
def solve(s, words):
    L, k = len(words[0]), len(words)
    want = Counter(words)
    out = []
    for i in range(len(s) - L * k + 1):
        if Counter(s[i + j * L:i + (j + 1) * L] for j in range(k)) == want:
            out.append(i)
    return " ".join(map(str, out)) if out else "NONE"
''',
    java='''
    static String solve(String s, String[] words) {
        int n = s.length(), k = words.length, L = words[0].length();
        HashMap<String, Integer> need = new HashMap<>();
        for (String w : words) need.merge(w, 1, Integer::sum);
        List<Integer> result = new ArrayList<>();
        for (int off = 0; off < L; off++) {
            HashMap<String, Integer> have = new HashMap<>();
            int left = off, used = 0;
            for (int right = off; right + L <= n; right += L) {
                String w = s.substring(right, right + L);
                if (!need.containsKey(w)) { have.clear(); used = 0; left = right + L; continue; }
                have.merge(w, 1, Integer::sum);
                used++;
                while (have.get(w) > need.get(w)) {
                    have.merge(s.substring(left, left + L), -1, Integer::sum);
                    used--;
                    left += L;
                }
                if (used == k) result.add(left);
            }
        }
        if (result.isEmpty()) return "NONE";
        Collections.sort(result);
        StringBuilder sb = new StringBuilder();
        for (int x : result) { if (sb.length() > 0) sb.append(' '); sb.append(x); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "barfoothefoobarman\n2\nfoo bar\n"),
        ("Example 2", "wordgoodgoodgoodbestword\n4\nword good best word\n"),
        ("Example 3", "barfoofoobarthefoobarman\n3\nbar foo the\n"),
    ],
    hidden=[
        ("Overlapping matches", "aaaaaa\n2\naa aa\n"),
        ("Whole string", "a\n1\na\n"),
        ("String too short", "ab\n2\nab ab\n"),
        ("Match at a non-zero offset", "xfoobarbaz\n2\nbar foo\n"),
    ],
    expl=[
        "\"barfoo\" at 0 and \"foobar\" at 9.",
        "\"word\" is needed twice, but no window has two words and one each of good and best.",
        "\"foobarthe\" at 6, \"barthefoo\" at 9 and \"thefoobar\" at 12.",
    ],
    prereqs=[
        ("sliding_window", "A window that grows on the right and shrinks from the left while a count is exceeded."),
        ("hashing", "Word counts compared against the counts inside the window."),
    ],
)

_p(
    "concatenated-words", "Concatenated Words", "Hard",
    topics=["Tries", "Dynamic Programming", "Strings"], subtopics=["Word Break"], companies=["Amazon", "Apple"],
    shape="words", ret="String", todo="sort by length; a word is concatenated if word break succeeds using only the shorter words seen so far",
    description=(
        "Print every word in the list that can be written as a concatenation of **at least two** "
        "shorter words from the same list (repetition allowed), in lexicographic order — or `NONE`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` distinct words.\n\n"
        "### Output\nThe concatenated words, separated by spaces, or `NONE`."
    ),
    constraints="1 ≤ n ≤ 10^4\n1 ≤ word length ≤ 30\nLowercase English letters",
    hints=[
        "For one word, \"can it be split into dictionary words?\" is Word Break.",
        "The pieces of a concatenated word are strictly shorter than it. So a word's dictionary is exactly the words shorter than it.",
        "Sort by length. For each word, run Word Break against the set of words added so far, then add it. \"At least two pieces\" is automatic, since the word itself is not yet in the set.",
    ],
    opt=("O(n log n + Σ L³)", "O(Σ L)", "A word-break DP per word: L² split points, each an O(L) substring lookup."),
    editorial=(
        "## The one thing this teaches\n**Order the input so the dictionary is built for free.** "
        "Excluding the word itself from its own dictionary is the fiddly part of this problem. "
        "Processing words shortest-first means the set, at that moment, contains precisely the "
        "allowed pieces.\n\n"
        "## Approach\n```java\nArrays.sort(words, Comparator.comparingInt(String::length));\n"
        "Set<String> dict = new HashSet<>();\nfor (String w : words) {\n"
        "    if (!dict.isEmpty() && canBreak(w, dict)) result.add(w);\n    dict.add(w);\n}\n\n"
        "boolean canBreak(String w, Set<String> dict) {\n    boolean[] ok = new boolean[w.length() + 1];\n    ok[0] = true;\n"
        "    for (int i = 1; i <= w.length(); i++)\n        for (int j = 0; j < i && !ok[i]; j++)\n"
        "            ok[i] = ok[j] && dict.contains(w.substring(j, i));\n"
        "    return ok[w.length()];\n}\n```\n\n"
        "## With a trie\nWalking a trie from position `j` finds every dictionary word starting "
        "there in one pass, instead of looking up each substring separately — the same DP with a "
        "faster inner loop.\n\n"
        "## Equal lengths\nTwo words of the same length can never be pieces of each other, so "
        "the order among equal lengths does not matter."
    ),
    py='''
def solve(words):
    present = set(words)

    def pieces(w):
        best = [0] + [-1] * len(w)          # most pieces covering w[:i], -1 if impossible
        for i in range(1, len(w) + 1):
            for j in range(i):
                if best[j] >= 0 and w[j:i] in present and w[j:i] != w:
                    best[i] = max(best[i], best[j] + 1)
        return best[len(w)]

    found = sorted(w for w in words if pieces(w) >= 2)
    return " ".join(found) if found else "NONE"
''',
    java='''
    static boolean canBreak(String w, Set<String> dict) {
        boolean[] ok = new boolean[w.length() + 1];
        ok[0] = true;
        for (int i = 1; i <= w.length(); i++)
            for (int j = 0; j < i && !ok[i]; j++)
                ok[i] = ok[j] && dict.contains(w.substring(j, i));
        return ok[w.length()];
    }

    static String solve(String[] words) {
        Arrays.sort(words, Comparator.comparingInt(String::length));
        Set<String> dict = new HashSet<>();
        List<String> result = new ArrayList<>();
        for (String w : words) {
            if (!dict.isEmpty() && canBreak(w, dict)) result.add(w);
            dict.add(w);
        }
        if (result.isEmpty()) return "NONE";
        Collections.sort(result);
        return String.join(" ", result);
    }
''',
    examples=[
        ("Example 1", "8\ncat cats catsdogcats dog dogcatsdog hippopotamuses rat ratcatdogcat\n"),
        ("Example 2", "3\ncat dog catdog\n"),
    ],
    hidden=[
        ("One word", "1\na\n"),
        ("Powers of a letter", "4\naaaa aaa aa a\n"),
        ("Repeated piece", "3\nab abab ba\n"),
        ("Pieces do not cover it", "3\nabc ab cd\n"),
    ],
    expl=[
        "catsdogcats = cats + dog + cats; dogcatsdog = dog + cats + dog; ratcatdogcat = rat + cat + dog + cat.",
        "catdog = cat + dog.",
    ],
    prereqs=[
        ("dp", "Word Break: ok[i] is true when a prefix of length i splits into dictionary words."),
        ("trie", "A trie that finds every dictionary word starting at a position in one walk."),
    ],
)
