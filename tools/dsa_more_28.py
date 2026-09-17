# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 28 — stacks, grid DP, enumeration, number theory, sorting and counting.
#
#   validate-stack-sequences          replay the pushes; pop greedily whenever the top is next
#   remove-adjacent-duplicates-k      a stack of (letter, run length)
#   min-falling-path-sum              each cell adds the best of the three cells above
#   min-ascii-delete-sum              edit distance where a deletion costs the character's code
#   subsets-ii                        sort, then skip a duplicate unless its twin was just taken
#   unique-paths-iii                  backtracking with a count of cells still to visit
#   smallest-repunit-divisible-by-k   track remainders only; a repeat means never
#   consecutive-numbers-sum           a run of length k exists when n − k(k−1)/2 is a positive multiple of k
#   relative-sort-array               counting sort, emitted in the given order first
#   num-subsequences-sum-condition    sort; for each minimum, every subset of the allowed range counts
#   longest-palindrome-two-letter     pair each word with its reverse; one symmetric word may sit in the middle
#   find-players-zero-one-losses      count losses per player who appeared
# ===========================================================================

_p(
    "validate-stack-sequences", "Validate Stack Sequences", "Medium",
    topics=["Stacks", "Simulation"], subtopics=["Stack Simulation"], companies=["Google", "Amazon"],
    shape="arr2", ret="String", todo="push each value in order; after every push, pop while the top equals the next value to pop",
    description=(
        "Values are pushed onto an empty stack in the order `pushed`, and at any moment the top "
        "may be popped. Could the pops happen in exactly the order `popped`?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `pushed`.\n- Line 3: `n`.\n- Line 4: `popped` (a permutation of `pushed`).\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 1000\nValues are distinct, 0 ≤ value ≤ 1000",
    hints=[
        "Simulate a real stack instead of reasoning about all interleavings.",
        "When should you pop? If the top is the next value that must be popped, popping now is never wrong — nothing else can be popped first.",
        "Push each value, then pop while the top matches popped[j]. The sequence is valid when the stack ends empty.",
    ],
    opt=("O(n)", "O(n)", "Each value is pushed and popped at most once."),
    editorial=(
        "## The one thing this teaches\n**Greedy simulation when delaying never helps.** If the "
        "value on top is the next one to pop, waiting only buries it under later pushes — and a "
        "buried value can never come out first. So pop immediately, every time.\n\n"
        "## Approach\n```java\nDeque<Integer> st = new ArrayDeque<>();\nint j = 0;\n"
        "for (int x : pushed) {\n    st.push(x);\n"
        "    while (!st.isEmpty() && st.peek() == popped[j]) { st.pop(); j++; }\n}\nreturn st.isEmpty();\n```\n\n"
        "## Walkthrough: pop order 4 3 5 1 2\nPush 1, 2, 3, 4 → pop 4, pop 3. Push 5 → pop 5. "
        "The next pop must be 1, but 2 is on top. Nothing is left to push, so the answer is `NO`.\n\n"
        "## Why distinct values matter\nWith duplicates, \"the top equals the next pop\" could "
        "match the wrong copy, and the greedy choice would no longer be forced."
    ),
    py='''
def solve(a, b):
    stack = []
    i = 0
    for want in b:
        if stack and stack[-1] == want:
            stack.pop()
            continue
        while i < len(a) and a[i] != want:
            stack.append(a[i])
            i += 1
        if i == len(a):
            return "NO"
        i += 1
    return "YES"
''',
    java='''
    static String solve(int[] pushed, int[] popped) {
        ArrayDeque<Integer> st = new ArrayDeque<>();
        int j = 0;
        for (int x : pushed) {
            st.push(x);
            while (!st.isEmpty() && st.peek() == popped[j]) { st.pop(); j++; }
        }
        return st.isEmpty() ? "YES" : "NO";
    }
''',
    examples=[
        ("Example 1", "5\n1 2 3 4 5\n5\n4 5 3 2 1\n"),
        ("Example 2", "5\n1 2 3 4 5\n5\n4 3 5 1 2\n"),
    ],
    hidden=[
        ("Single value", "1\n7\n1\n7\n"),
        ("Pop immediately", "4\n1 2 3 4\n4\n1 2 3 4\n"),
        ("Pop all at the end", "4\n1 2 3 4\n4\n4 3 2 1\n"),
        ("Buried value", "3\n1 2 3\n3\n3 1 2\n"),
    ],
    expl=[
        "Push 1–4, pop 4, push 5, pop 5, then pop 3, 2, 1.",
        "After popping 4, 3 and 5, the stack holds 1 under 2, so 1 cannot come out next.",
    ],
    prereqs=[
        ("stack", "Pushing and popping while comparing the top to a target sequence."),
        ("simulation", "Replaying a process step by step instead of reasoning about it abstractly."),
    ],
)

_p(
    "remove-adjacent-duplicates-k", "Remove All Adjacent Duplicates II", "Medium",
    topics=["Stacks", "Strings"], subtopics=["Run-Length Stack"], companies=["Meta", "Bloomberg"],
    shape="str_k", ret="String", todo="stack of (letter, count); increment on a match, pop when the count reaches k",
    description=(
        "Repeatedly delete `k` **adjacent, equal** letters from `s` until no such group remains. "
        "Print the final string, or `EMPTY` if nothing is left. (The result does not depend on "
        "the order of deletions.)\n\n"
        "### Input\nOne line: `s k`.\n\n"
        "### Output\nThe final string, or `EMPTY`."
    ),
    constraints="1 ≤ |s| ≤ 10^5\n2 ≤ k ≤ 10^4\nLowercase English letters",
    hints=[
        "Rescanning the string after every deletion is O(n² / k).",
        "A deletion can make two runs meet — in abbbaa with k = 3, removing bbb joins the a's. A stack handles that naturally.",
        "Push (letter, run length). A matching letter increments the top's count; when it reaches k, pop the whole run.",
    ],
    opt=("O(n)", "O(n)", "Each letter touches the stack once."),
    editorial=(
        "## The one thing this teaches\n**Store runs, not characters.** Removing adjacent pairs "
        "needs a stack of letters. Removing groups of `k` needs to know how long the current run "
        "is — so each stack entry carries a count, and the top is always the run a new letter "
        "may extend.\n\n"
        "## Approach\n```java\nchar[] letter = new char[n];\nint[] count = new int[n];\nint top = 0;\n"
        "for (char ch : s.toCharArray()) {\n"
        "    if (top > 0 && letter[top - 1] == ch) {\n        if (++count[top - 1] == k) top--;    // run complete: remove it\n"
        "    } else {\n        letter[top] = ch; count[top] = 1; top++;\n    }\n}\n"
        "// rebuild: each entry's letter repeated count times\n```\n\n"
        "## Chain reactions\nIn `deeedbbcccbdaa`, k = 3: `eee` goes, joining the d's into `dd`; "
        "later `ccc` goes, joining the b's into `bbb`, which goes and makes `ddd` — also removed. "
        "The stack performs each of these as the letters arrive, with no rescanning."
    ),
    py='''
def solve(s, k):
    import re
    pattern = re.compile(r"(.)\\1{%d}" % (k - 1))
    while True:
        shorter = pattern.sub("", s)
        if shorter == s:
            return s if s else "EMPTY"
        s = shorter
''',
    java='''
    static String solve(String s, int k) {
        int n = s.length(), top = 0;
        char[] letter = new char[n];
        int[] count = new int[n];
        for (int i = 0; i < n; i++) {
            char ch = s.charAt(i);
            if (top > 0 && letter[top - 1] == ch) {
                if (++count[top - 1] == k) top--;
            } else {
                letter[top] = ch;
                count[top] = 1;
                top++;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < top; i++) for (int c = 0; c < count[i]; c++) sb.append(letter[i]);
        return sb.length() == 0 ? "EMPTY" : sb.toString();
    }
''',
    examples=[
        ("Example 1", "abcd 2\n"),
        ("Example 2", "deeedbbcccbdaa 3\n"),
        ("Example 3", "pbbcggttciiippooaais 2\n"),
    ],
    hidden=[
        ("Everything goes", "aaaa 2\n"),
        ("Chain reaction", "abbbaaca 3\n"),
        ("Run longer than k", "aaaaa 3\n"),
        ("No run reaches k", "aabbaabb 3\n"),
    ],
    expl=[
        "No two adjacent letters are equal.",
        "eee, then ccc, then bbb, then ddd are removed, leaving aa.",
        "Pairs keep collapsing until only p and s remain.",
    ],
    prereqs=[
        ("stack", "A stack whose entries record a letter and its run length."),
        ("string_basics", "Rebuilding a string from runs."),
    ],
)

_p(
    "min-falling-path-sum", "Minimum Falling Path Sum", "Medium",
    topics=["Dynamic Programming", "Matrix"], subtopics=["2D DP"], companies=["Google", "Amazon"],
    shape="matrix", ret="long", todo="row by row: each cell adds the minimum of the up-to-three cells diagonally-left, above and diagonally-right in the previous row",
    description=(
        "A falling path starts at any cell in the first row of an `n × n` matrix and moves down "
        "one row at a time, to the cell directly below or diagonally left or right below. Print "
        "the minimum sum of a falling path.\n\n"
        "### Input\n- Line 1: `n n`.\n- Next `n` lines: `n` integers each.\n\n"
        "### Output\nThe minimum falling path sum."
    ),
    constraints="1 ≤ n ≤ 100\n-100 ≤ value ≤ 100",
    hints=[
        "Trying all paths is up to 3^(n−1) per starting cell.",
        "The best path ending at (i, j) came from (i−1, j−1), (i−1, j) or (i−1, j+1) — whichever had the smallest best sum.",
        "Fill row by row keeping only the previous row; clamp the column range at the edges. The answer is the minimum of the last row.",
    ],
    opt=("O(n²)", "O(n)", "Each cell looks at three cells above; one row of state."),
    editorial=(
        "## The one thing this teaches\n**Grid DP with a wider neighbourhood is still grid DP.** "
        "Minimum Path Sum looks at two predecessors; here there are three. The structure — each "
        "row depends only on the one before — is unchanged, and so is the rolling row.\n\n"
        "## Approach\n```java\nlong[] prev = first row;\nfor (int i = 1; i < n; i++) {\n"
        "    long[] cur = new long[n];\n    for (int j = 0; j < n; j++) {\n        long best = prev[j];\n"
        "        if (j > 0) best = Math.min(best, prev[j - 1]);\n        if (j < n - 1) best = Math.min(best, prev[j + 1]);\n"
        "        cur[j] = m[i][j] + best;\n    }\n    prev = cur;\n}\nreturn min(prev);\n```\n\n"
        "## Why a new row array\nUpdating `prev` in place would overwrite `prev[j − 1]` before "
        "`cur[j]` reads it. A fresh array (or a saved diagonal value) keeps the previous row "
        "intact.\n\n"
        "## Walkthrough (Example 1)\nRows `2 1 3`, `6 5 4`, `7 8 9`. Second row becomes "
        "`7 6 5`; third becomes `13 13 14`. Minimum 13, e.g. 1 → 5 → 7."
    ),
    py='''
def solve(m):
    import sys
    from functools import lru_cache
    sys.setrecursionlimit(10000)
    n = len(m)

    @lru_cache(maxsize=None)
    def best_from(i, j):
        if i == n - 1:
            return m[i][j]
        return m[i][j] + min(best_from(i + 1, c) for c in (j - 1, j, j + 1) if 0 <= c < n)

    return min(best_from(0, j) for j in range(n))
''',
    java='''
    static long solve(int[][] m) {
        int n = m.length;
        long[] prev = new long[n];
        for (int j = 0; j < n; j++) prev[j] = m[0][j];
        for (int i = 1; i < n; i++) {
            long[] cur = new long[n];
            for (int j = 0; j < n; j++) {
                long best = prev[j];
                if (j > 0) best = Math.min(best, prev[j - 1]);
                if (j < n - 1) best = Math.min(best, prev[j + 1]);
                cur[j] = m[i][j] + best;
            }
            prev = cur;
        }
        long ans = Long.MAX_VALUE;
        for (long v : prev) ans = Math.min(ans, v);
        return ans;
    }
''',
    examples=[("Example 1", "3 3\n2 1 3\n6 5 4\n7 8 9\n"), ("Example 2", "2 2\n-19 57\n-40 -5\n")],
    hidden=[
        ("Single cell", "1 1\n-7\n"),
        ("Edge columns", "3 3\n1 100 100\n100 100 1\n1 100 100\n"),
        ("Zigzag", "4 4\n1 9 9 9\n9 1 9 9\n9 9 1 9\n9 9 9 1\n"),
        ("All negative", "2 2\n-1 -2\n-3 -4\n"),
    ],
    expl=[
        "1 → 5 → 7 (or 1 → 4 → 8) sums to 13.",
        "−19 → −40 sums to −59.",
    ],
    prereqs=[
        ("dp2d", "Row-by-row grid DP with a rolling row."),
        ("grid", "Clamping neighbour columns at the matrix edges."),
    ],
)

_p(
    "min-ascii-delete-sum", "Minimum ASCII Delete Sum for Two Strings", "Medium",
    topics=["Dynamic Programming", "Strings"], subtopics=["2D DP", "Edit Distance"], companies=["TripAdvisor", "Amazon"],
    shape="str2", ret="int", todo="dp[i][j] = cheapest cost to equalise s[i..] and t[j..]: free on a match, else delete the cheaper of the two first characters",
    description=(
        "Delete characters from `s` and `t` so the two strings become equal. Each deleted "
        "character costs its ASCII code. Print the minimum total cost.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `t`.\n\n"
        "### Output\nThe minimum ASCII sum of deleted characters."
    ),
    constraints="1 ≤ |s|, |t| ≤ 1000\nLowercase English letters",
    hints=[
        "This is edit distance with only deletions, and weighted costs.",
        "Look at the first characters. If equal, keep both. Otherwise one of them must be deleted: pay its code and continue.",
        "dp[i][j] over suffixes; the base cases delete everything that remains in the other string. Alternatively: total ASCII − 2 × (heaviest common subsequence).",
    ],
    opt=("O(|s| · |t|)", "O(|t|)", "One cell per pair of positions; a rolling row suffices."),
    editorial=(
        "## The one thing this teaches\n**Edit-distance DPs change costs, not structure.** "
        "Swapping \"1 per operation\" for \"the character's code\" leaves the table and its "
        "transitions intact — only the numbers added along the edges change.\n\n"
        "## Approach\n```java\nint[][] dp = new int[n + 1][m + 1];\n"
        "for (int i = n - 1; i >= 0; i--) dp[i][m] = dp[i + 1][m] + s.charAt(i);\n"
        "for (int j = m - 1; j >= 0; j--) dp[n][j] = dp[n][j + 1] + t.charAt(j);\n"
        "for (int i = n - 1; i >= 0; i--)\n    for (int j = m - 1; j >= 0; j--)\n"
        "        dp[i][j] = s.charAt(i) == t.charAt(j) ? dp[i + 1][j + 1]\n"
        "                 : Math.min(s.charAt(i) + dp[i + 1][j], t.charAt(j) + dp[i][j + 1]);\nreturn dp[0][0];\n```\n\n"
        "## Keep what is heavy\nEquivalently, keep the common subsequence with the largest ASCII "
        "sum; everything else is deleted from both strings. The cost is `total(s) + total(t) − "
        "2 × kept`.\n\n"
        "## Walkthrough: sea / eat\nKeep `ea` (weight 101 + 97). Delete `s` (115) and `t` (116): 231."
    ),
    py='''
def solve(s, t):
    n, m = len(s), len(t)
    keep = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            if s[i] == t[j]:
                keep[i + 1][j + 1] = keep[i][j] + ord(s[i])
            else:
                keep[i + 1][j + 1] = max(keep[i][j + 1], keep[i + 1][j])
    return sum(map(ord, s)) + sum(map(ord, t)) - 2 * keep[n][m]
''',
    java='''
    static int solve(String s, String t) {
        int n = s.length(), m = t.length();
        int[][] dp = new int[n + 1][m + 1];
        for (int i = n - 1; i >= 0; i--) dp[i][m] = dp[i + 1][m] + s.charAt(i);
        for (int j = m - 1; j >= 0; j--) dp[n][j] = dp[n][j + 1] + t.charAt(j);
        for (int i = n - 1; i >= 0; i--)
            for (int j = m - 1; j >= 0; j--)
                dp[i][j] = s.charAt(i) == t.charAt(j) ? dp[i + 1][j + 1]
                        : Math.min(s.charAt(i) + dp[i + 1][j], t.charAt(j) + dp[i][j + 1]);
        return dp[0][0];
    }
''',
    examples=[("Example 1", "sea\neat\n"), ("Example 2", "delete\nleet\n")],
    hidden=[
        ("Identical", "a\na\n"),
        ("Nothing shared", "a\nb\n"),
        ("Disjoint letters", "abc\nxyz\n"),
        ("Heavier letters are kept", "az\nza\n"),
    ],
    expl=[
        "Delete s from sea and t from eat: 115 + 116 = 231.",
        "Keep \"let\"; delete d, e, e from delete (100 + 101 + 101) and e from leet (101): 403.",
    ],
    prereqs=[
        ("dp2d", "An edit-distance table over suffixes with weighted transitions."),
        ("string_basics", "Character codes, and common subsequences."),
    ],
)

_p(
    "subsets-ii", "Subsets II", "Medium",
    topics=["Backtracking", "Arrays"], subtopics=["Duplicates"], companies=["Meta", "Amazon"],
    shape="arr", ret="String", todo="sort; recurse from a start index, skipping a value equal to the previous one at the same depth",
    description=(
        "The array may contain duplicates. Print every **distinct** subset, each with its values "
        "in increasing order, one per line. Order the lines lexicographically as sequences of "
        "integers; the empty subset comes first and is printed as `EMPTY`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe distinct subsets."
    ),
    constraints="1 ≤ n ≤ 10\n-10 ≤ a[i] ≤ 10",
    hints=[
        "Generating all 2^n subsets and removing duplicates works, but produces the same subset many times.",
        "Sort first so equal values sit together. Then a subset is determined by how many copies of each value it uses.",
        "In the recursion over start positions, skip a[i] when i > start and a[i] == a[i − 1]: that choice was already explored with the earlier copy.",
    ],
    opt=("O(2^n · n)", "O(n)", "At most 2^n subsets, each copied in O(n); recursion depth n."),
    editorial=(
        "## The one thing this teaches\n**Skip duplicates at the same decision level, not across "
        "levels.** Choosing \"the next element\" from position `start` onward, two equal values "
        "offered at the same level lead to identical subtrees. The second copy is still allowed "
        "*deeper* — that is how `[2, 2]` is formed.\n\n"
        "## Approach\n```java\nArrays.sort(a);\n\nvoid build(int start, List<Integer> cur) {\n"
        "    output(cur);                                   // every node of the tree is a subset\n"
        "    for (int i = start; i < n; i++) {\n"
        "        if (i > start && a[i] == a[i - 1]) continue;   // same value at the same level\n"
        "        cur.add(a[i]);\n        build(i + 1, cur);\n        cur.remove(cur.size() - 1);\n    }\n}\n```\n\n"
        "## Why the output is sorted\nThe tree is visited in preorder, a subset is printed before "
        "its extensions, and children are tried in increasing value — exactly lexicographic "
        "order on sorted sequences.\n\n"
        "## Walkthrough: 1 2 2\n`[]`, `[1]`, `[1 2]`, `[1 2 2]`, `[2]`, `[2 2]`. At the top level "
        "the second 2 is skipped; inside `[2]` it is used."
    ),
    py='''
def solve(a):
    from itertools import combinations
    subsets = {tuple(sorted(c)) for r in range(len(a) + 1) for c in combinations(a, r)}
    return "\\n".join(" ".join(map(str, s)) if s else "EMPTY" for s in sorted(subsets))
''',
    java='''
    static int[] vals;
    static StringBuilder out;

    static void build(int start, ArrayList<Integer> cur) {
        if (out.length() > 0) out.append('\\n');
        if (cur.isEmpty()) out.append("EMPTY");
        for (int i = 0; i < cur.size(); i++) { if (i > 0) out.append(' '); out.append(cur.get(i)); }
        for (int i = start; i < vals.length; i++) {
            if (i > start && vals[i] == vals[i - 1]) continue;
            cur.add(vals[i]);
            build(i + 1, cur);
            cur.remove(cur.size() - 1);
        }
    }

    static String solve(int[] a) {
        vals = a.clone();
        Arrays.sort(vals);
        out = new StringBuilder();
        build(0, new ArrayList<>());
        return out.toString();
    }
''',
    examples=[("Example 1", "3\n1 2 2\n"), ("Example 2", "1\n0\n")],
    hidden=[
        ("Negative duplicates", "3\n-1 -1 0\n"),
        ("All equal", "3\n5 5 5\n"),
        ("No duplicates", "3\n3 1 2\n"),
        ("Two pairs", "4\n2 1 2 1\n"),
    ],
    expl=[
        "Six distinct subsets; [2] and [1 2] would otherwise appear twice.",
        "The empty subset and [0].",
    ],
    prereqs=[
        ("backtracking", "Start-index recursion with choose / recurse / un-choose."),
        ("sorting", "Grouping equal values so duplicates can be skipped by comparing neighbours."),
    ],
)

_p(
    "unique-paths-iii", "Unique Paths III", "Hard",
    topics=["Backtracking", "Matrix"], subtopics=["Hamiltonian Paths", "Grid DFS"], companies=["Amazon", "Google"],
    shape="grid", ret="long", todo="count free cells; DFS from S marking cells, and count arrivals at E when every free cell has been used",
    description=(
        "A grid has one start `S`, one end `E`, empty cells `.` and obstacles `#`. Count the walks "
        "from `S` to `E` that move up, down, left or right and visit **every non-obstacle cell "
        "exactly once** (including S and E).\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: the grid.\n\n"
        "### Output\nThe number of such walks."
    ),
    constraints="1 ≤ r · c ≤ 20\nExactly one S and one E",
    hints=[
        "This asks for Hamiltonian paths — no polynomial method is known, but the grid has at most 20 cells.",
        "DFS from S, marking cells as used and unmarking on return.",
        "Count the non-obstacle cells first. A walk that reaches E is valid only if it has used all of them; otherwise it is a dead end.",
    ],
    opt=("O(3^k)", "O(k)", "k free cells; after the first step each move has at most three unvisited neighbours."),
    editorial=(
        "## The one thing this teaches\n**Backtracking with a completion check.** Reaching the "
        "goal is not enough; the walk must also have covered everything. Tracking how many cells "
        "remain turns that check into `remaining == 0`.\n\n"
        "## Approach\n```java\nlong dfs(int i, int j, int remaining) {\n"
        "    if (g[i][j] == 'E') return remaining == 0 ? 1 : 0;\n"
        "    char saved = g[i][j];\n    g[i][j] = '#';                                  // mark used\n    long ways = 0;\n"
        "    for (int[] d : DIRS) {\n        int x = i + d[0], y = j + d[1];\n"
        "        if (inside(x, y) && g[x][y] != '#') ways += dfs(x, y, remaining - 1);\n    }\n"
        "    g[i][j] = saved;                                // unmark\n    return ways;\n}\n"
        "// remaining = free cells (including E) not yet visited, excluding S\n```\n\n"
        "## Why E ends the walk\nE must be the last cell. Stepping onto it early and continuing "
        "would visit it in the middle — so arrival at E always stops the recursion.\n\n"
        "## Memoising\nWith (cell, set of visited cells) as the state, a bitmask DP counts the "
        "same walks in O(2^k · k) — useful when many partial walks reach the same situation."
    ),
    py='''
def solve(g):
    cells = [(i, j) for i in range(len(g)) for j in range(len(g[0])) if g[i][j] != "#"]
    index = {cell: k for k, cell in enumerate(cells)}
    start = next(index[c] for c in cells if g[c[0]][c[1]] == "S")
    end = next(index[c] for c in cells if g[c[0]][c[1]] == "E")
    full = (1 << len(cells)) - 1
    ways = {(1 << start, start): 1}
    for mask in range(1 << len(cells)):
        for last in range(len(cells)):
            count = ways.get((mask, last))
            if not count or last == end:
                continue
            i, j = cells[last]
            for nb in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                k = index.get(nb)
                if k is not None and not mask >> k & 1:
                    key = (mask | 1 << k, k)
                    ways[key] = ways.get(key, 0) + count
    return ways.get((full, end), 0)
''',
    java='''
    static char[][] grid;

    static long dfs(int i, int j, int remaining) {
        if (grid[i][j] == 'E') return remaining == 0 ? 1 : 0;
        char saved = grid[i][j];
        grid[i][j] = '#';
        long ways = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        for (int[] d : dirs) {
            int x = i + d[0], y = j + d[1];
            if (x >= 0 && y >= 0 && x < grid.length && y < grid[0].length && grid[x][y] != '#')
                ways += dfs(x, y, remaining - 1);
        }
        grid[i][j] = saved;
        return ways;
    }

    static long solve(char[][] g) {
        grid = g;
        int free = 0, si = 0, sj = 0;
        for (int i = 0; i < g.length; i++)
            for (int j = 0; j < g[0].length; j++) {
                if (g[i][j] != '#') free++;
                if (g[i][j] == 'S') { si = i; sj = j; }
            }
        return dfs(si, sj, free - 1);
    }
''',
    examples=[
        ("Example 1", "3 4\nS...\n....\n..E#\n"),
        ("Example 2", "3 4\nS...\n....\n...E\n"),
        ("Example 3", "2 2\n.S\nE.\n"),
    ],
    hidden=[
        ("Adjacent", "1 2\nSE\n"),
        ("Straight line", "1 3\nS.E\n"),
        ("Around an obstacle", "2 2\nS#\n.E\n"),
        ("End in the middle", "1 3\nSE.\n"),
        ("Small room", "3 3\nS..\n...\n..E\n"),
    ],
    expl=[
        "Two snakes cover all eleven free cells and finish on E.",
        "Four ways to sweep all twelve cells ending in the corner.",
        "Any walk from S reaches E before covering both empty cells.",
    ],
    prereqs=[
        ("backtracking", "Marking and unmarking grid cells during a DFS."),
        ("grid", "Four-directional moves with bounds and obstacle checks."),
    ],
)

_p(
    "smallest-repunit-divisible-by-k", "Smallest Integer Divisible by K", "Medium",
    topics=["Math", "Hashing"], subtopics=["Modular Arithmetic", "Pigeonhole"], companies=["Google"],
    shape="n", ret="int", todo="track r = (r · 10 + 1) mod k for lengths 1..k; zero gives the length, and no zero within k steps means never",
    description=(
        "Print the length of the smallest positive integer made only of the digit `1` (such as "
        "`1`, `11`, `111`, …) that is divisible by `k`, or `-1` if none exists.\n\n"
        "### Input\nOne line: `k`.\n\n"
        "### Output\nThe length, or `-1`."
    ),
    constraints="1 ≤ k ≤ 10^5",
    hints=[
        "The numbers overflow any integer type almost immediately — but only the remainder mod k matters.",
        "Going from length L to L + 1: remainder' = (remainder · 10 + 1) mod k.",
        "There are only k possible remainders. If none of the first k lengths gives 0, a remainder has repeated and the sequence cycles forever without reaching 0.",
    ],
    opt=("O(k)", "O(1)", "At most k remainder updates."),
    editorial=(
        "## The one thing this teaches\n**Carry only the remainder, and let pigeonhole bound the "
        "search.** The repunits grow without limit, but their remainders mod k live in k values. "
        "Each remainder determines the next, so once one repeats the sequence is in a cycle.\n\n"
        "## Approach\n```java\nif (k % 2 == 0 || k % 5 == 0) return -1;   // a number ending in 1 is odd and not divisible by 5\n"
        "int r = 0;\nfor (int len = 1; len <= k; len++) {\n    r = (r * 10 + 1) % k;\n"
        "    if (r == 0) return len;\n}\nreturn -1;\n```\n\n"
        "## Why k steps suffice\nAmong the first k + 1 remainders two must be equal. If 0 has not "
        "appeared by then, the sequence has entered a loop that does not contain 0.\n\n"
        "## Why the shortcut is safe\nRepunits end in 1, so they are odd and not multiples of 5. "
        "For every other k, a repunit divisible by k always exists — the loop will find it."
    ),
    py='''
def solve(n):
    seen = set()
    r, length = 1 % n, 1
    while r != 0:
        if r in seen:
            return -1
        seen.add(r)
        r = (r * 10 + 1) % n
        length += 1
    return length
''',
    java='''
    static int solve(long kk) {
        int k = (int) kk;
        if (k % 2 == 0 || k % 5 == 0) return -1;
        int r = 0;
        for (int len = 1; len <= k; len++) {
            r = (r * 10 + 1) % k;
            if (r == 0) return len;
        }
        return -1;
    }
''',
    examples=[("Example 1", "1\n"), ("Example 2", "2\n"), ("Example 3", "3\n")],
    hidden=[
        ("Seven", "7\n"),
        ("Seventeen", "17\n"),
        ("Forty-one", "41\n"),
        ("Multiple of ten", "100000\n"),
        ("Large odd", "99999\n"),
    ],
    expl=[
        "1 is divisible by 1.",
        "Every repunit is odd.",
        "111 = 3 × 37.",
    ],
    prereqs=[
        ("modulo", "Updating a remainder as digits are appended."),
        ("visited_set", "A repeated state proves a cycle that will never reach the target."),
    ],
)

_p(
    "consecutive-numbers-sum", "Consecutive Numbers Sum", "Hard",
    topics=["Math"], subtopics=["Arithmetic Series", "Divisors"], companies=["Google", "Amazon"],
    shape="n", ret="int", todo="for each length k with k(k+1)/2 ≤ n, a run exists when n − k(k−1)/2 is divisible by k",
    description=(
        "In how many ways can `n` be written as a sum of **one or more consecutive positive "
        "integers**?\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe number of ways."
    ),
    constraints="1 ≤ n ≤ 10^9",
    hints=[
        "A run of length k starting at x sums to k·x + k(k − 1)/2.",
        "So for a fixed k, x = (n − k(k − 1)/2) / k must be a positive integer.",
        "x ≥ 1 needs k(k + 1)/2 ≤ n, so k is at most about √(2n). Test each k.",
    ],
    opt=("O(√n)", "O(1)", "About √(2n) candidate lengths."),
    editorial=(
        "## The one thing this teaches\n**Fix the free parameter that has a small range.** A run "
        "has a start and a length. The start can be huge, but the length is at most √(2n) — and "
        "once the length is fixed, the start is determined by one division.\n\n"
        "## Approach\n```java\nint ways = 0;\nfor (long k = 1; k * (k + 1) / 2 <= n; k++)\n"
        "    if ((n - k * (k - 1) / 2) % k == 0) ways++;\nreturn ways;\n```\n\n"
        "## The number-theory view\nThe answer equals the number of **odd divisors** of n. For "
        "`15 = 3 · 5`, the odd divisors 1, 3, 5, 15 correspond to `15`, `4+5+6`, `1+2+3+4+5` and "
        "`7+8`.\n\n"
        "## Use long for k(k+1)/2\nWith n near 10^9, k reaches about 44 721, and `k · (k + 1)` "
        "is near 2·10^9 — at the edge of an int."
    ),
    py='''
def solve(n):
    while n % 2 == 0:
        n //= 2
    count, d = 0, 1
    while d * d <= n:
        if n % d == 0:
            count += 1 if d * d == n else 2
        d += 2
    return count
''',
    java='''
    static int solve(long n) {
        int ways = 0;
        for (long k = 1; k * (k + 1) / 2 <= n; k++)
            if ((n - k * (k - 1) / 2) % k == 0) ways++;
        return ways;
    }
''',
    examples=[("Example 1", "5\n"), ("Example 2", "9\n"), ("Example 3", "15\n")],
    hidden=[
        ("One", "1\n"),
        ("Power of two", "2\n"),
        ("Large power of ten", "1000000000\n"),
        ("Many odd divisors", "999999999\n"),
    ],
    expl=[
        "5 and 2 + 3.",
        "9, 4 + 5 and 2 + 3 + 4.",
        "15, 7 + 8, 4 + 5 + 6 and 1 + 2 + 3 + 4 + 5.",
    ],
    prereqs=[
        ("math_digits", "The arithmetic-series sum k·x + k(k − 1)/2."),
        ("overflow", "k(k + 1) near 2·10^9 needs a long."),
    ],
)

_p(
    "relative-sort-array", "Relative Sort Array", "Easy",
    topics=["Sorting", "Hashing"], subtopics=["Counting Sort", "Custom Order"], companies=["Amazon", "Google"],
    shape="arr2", ret="String", todo="count arr1's values; emit arr2's values by their counts in arr2's order, then the remaining values ascending",
    description=(
        "Sort `arr1` so that values appearing in `arr2` come first, in the same relative order as "
        "in `arr2`. Values not in `arr2` follow in increasing order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `arr1`.\n- Line 3: `m`.\n- Line 4: `arr2` (distinct values, all present in arr1; may be empty).\n\n"
        "### Output\nThe sorted `arr1`."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ m ≤ 1000\n0 ≤ value ≤ 1000",
    hints=[
        "A comparator can rank each value by its position in arr2, putting unknown values after all known ones.",
        "Values are at most 1000 — a counting array replaces the sort.",
        "Count arr1. Walk arr2, printing each value count times and zeroing its count. Then walk 0..1000 printing what is left.",
    ],
    opt=("O(n + m + V)", "O(V)", "V = 1001 possible values; no comparison sort."),
    editorial=(
        "## The one thing this teaches\n**When values are small, count instead of compare.** A "
        "custom comparator works in O(n log n). With values below 1001, a counting array does "
        "the ordering for free — first in the order arr2 dictates, then in natural order.\n\n"
        "## Approach\n```java\nint[] count = new int[1001];\nfor (int x : arr1) count[x]++;\n"
        "List<Integer> out = new ArrayList<>();\nfor (int x : arr2) { while (count[x]-- > 0) out.add(x); }\n"
        "for (int v = 0; v <= 1000; v++) while (count[v]-- > 0) out.add(v);\n```\n\n"
        "## The comparator version\nKey each value by `(rank in arr2, value)` with rank = "
        "arr2's size for values not in arr2. Sorting by that pair gives the same order and "
        "works for any value range.\n\n"
        "## The post-decrement trap\n`count[x]-- > 0` leaves `count[x]` at −1 when it stops, "
        "which is harmless here since the second loop also stops at non-positive counts."
    ),
    py='''
def solve(a, b):
    rank = {v: i for i, v in enumerate(b)}
    return " ".join(map(str, sorted(a, key=lambda v: (rank.get(v, len(b)), v))))
''',
    java='''
    static String solve(int[] arr1, int[] arr2) {
        int[] count = new int[1001];
        for (int x : arr1) count[x]++;
        StringBuilder sb = new StringBuilder();
        for (int x : arr2)
            while (count[x] > 0) { if (sb.length() > 0) sb.append(' '); sb.append(x); count[x]--; }
        for (int v = 0; v <= 1000; v++)
            while (count[v] > 0) { if (sb.length() > 0) sb.append(' '); sb.append(v); count[v]--; }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "11\n2 3 1 3 2 4 6 7 9 2 19\n6\n2 1 4 3 9 6\n"),
        ("Example 2", "6\n28 6 22 8 44 17\n4\n22 28 8 6\n"),
    ],
    hidden=[
        ("Empty order", "3\n3 1 2\n0\n"),
        ("Order covers everything", "4\n1 2 1 2\n2\n2 1\n"),
        ("Zeros and the top value", "5\n1000 0 5 0 1000\n1\n5\n"),
        ("Single value", "1\n7\n1\n7\n"),
    ],
    expl=[
        "2 2 2 1 4 3 3 9 6 follow arr2's order; 7 and 19 come last, ascending.",
        "22 28 8 6 in arr2's order, then 17 and 44.",
    ],
    prereqs=[
        ("sorting", "Counting sort, and comparators keyed by a rank."),
        ("hashing", "A value-to-count table indexed directly by the value."),
    ],
)

_p(
    "num-subsequences-sum-condition", "Subsequences with Min + Max ≤ Target", "Medium",
    topics=["Two Pointers", "Sorting", "Math"], subtopics=["Counting Subsets", "Powers of Two"], companies=["Amazon"],
    shape="arr_k", ret="long", todo="sort; for each left end l, find the largest r with a[l] + a[r] ≤ target and add 2^(r − l) subsets",
    description=(
        "Count the **non-empty subsequences** whose minimum plus maximum is at most `target`. "
        "Subsequences are chosen by index, so equal values at different positions give "
        "different subsequences. Print the count modulo `10^9 + 7`.\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe count modulo 10^9 + 7."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^6\n1 ≤ target ≤ 10^6",
    hints=[
        "Only the minimum and the maximum matter, not the order — so sort the array (the count of index subsets does not change).",
        "Fix the minimum as a[l], the smallest index chosen. Any subset of a[l+1..r] can join it, where r is the largest index with a[l] + a[r] ≤ target.",
        "That is 2^(r − l) subsequences. As l increases, r only decreases: two pointers, with powers of two precomputed modulo 10^9 + 7.",
    ],
    opt=("O(n log n)", "O(n)", "Sorting, then a linear two-pointer pass with a table of powers of two."),
    editorial=(
        "## The one thing this teaches\n**Count subsets by fixing one required element.** Every "
        "valid subsequence has a unique smallest position in sorted order. Fixing it, the rest "
        "may be *any* subset of a range — a power of two — so there is no need to enumerate.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong[] pow2 = powers of 2 mod MOD up to n;\n"
        "long count = 0;\nint l = 0, r = n - 1;\nwhile (l <= r) {\n"
        "    if (a[l] + a[r] > target) r--;               // a[r] is too big to pair with a[l] or anything after\n"
        "    else { count = (count + pow2[r - l]) % MOD; l++; }\n}\n```\n\n"
        "## Why sorting is allowed\nA subsequence is a set of indices; its minimum and maximum "
        "do not depend on order. Sorting permutes the indices without changing how many sets "
        "satisfy the condition.\n\n"
        "## Singletons\nWhen `l == r`, `2a[l] ≤ target` and `pow2[0] = 1` counts the one-element "
        "subsequence `[a[l]]`."
    ),
    py='''
def solve(a, k):
    from itertools import combinations
    MOD = 10**9 + 7
    total = 0
    for size in range(1, len(a) + 1):
        for chosen in combinations(a, size):
            if min(chosen) + max(chosen) <= k:
                total += 1
    return total % MOD
''',
    java='''
    static long solve(int[] a, long target) {
        final long MOD = 1_000_000_007L;
        int n = a.length;
        Arrays.sort(a);
        long[] pow2 = new long[n + 1];
        pow2[0] = 1;
        for (int i = 1; i <= n; i++) pow2[i] = pow2[i - 1] * 2 % MOD;
        long count = 0;
        int l = 0, r = n - 1;
        while (l <= r) {
            if ((long) a[l] + a[r] > target) r--;
            else { count = (count + pow2[r - l]) % MOD; l++; }
        }
        return count;
    }
''',
    examples=[("Example 1", "4 9\n3 5 6 7\n"), ("Example 2", "4 10\n3 3 6 8\n"), ("Example 3", "6 12\n2 3 3 4 6 7\n")],
    hidden=[
        ("Single too large", "1 1\n1\n"),
        ("Single fits", "1 2\n1\n"),
        ("Everything fits", "5 100\n1 1 1 1 1\n"),
        ("Unsorted input", "7 7\n5 1 4 2 3 9 8\n"),
    ],
    expl=[
        "[3], [3, 5], [3, 5, 6] and [3, 6].",
        "[3], [3], [3, 3], [3, 6], [3, 6] and [3, 3, 6] — the two 3s are different positions.",
        "Every subsequence except the two whose min + max exceeds 12: 63 − 2 = 61.",
    ],
    prereqs=[
        ("two_pointers", "A right pointer that only moves left as the left pointer advances."),
        ("modulo", "Powers of two precomputed modulo 10^9 + 7."),
    ],
)

_p(
    "longest-palindrome-two-letter", "Longest Palindrome by Concatenating Two-Letter Words", "Medium",
    topics=["Hashing", "Greedy", "Strings"], subtopics=["Pairing with Reverse"], companies=["Amazon", "Google"],
    shape="words", ret="int", todo="match each word with an unused copy of its reverse (+4 per pair); at the end, one leftover double-letter word may go in the middle (+2)",
    description=(
        "Each word has exactly two letters. Choose some of the words (each at most once) and "
        "concatenate them in any order to form a palindrome. Print the length of the longest "
        "possible palindrome, or 0.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` two-letter words.\n\n"
        "### Output\nThe maximum length."
    ),
    constraints="1 ≤ n ≤ 10^5\nLowercase English letters",
    hints=[
        "In a palindrome made of 2-letter blocks, the block at position i from the left is the reverse of the block at position i from the right.",
        "So words pair with their reverses: ab with ba, and gg with another gg. Each pair adds 4.",
        "At most one block can sit alone in the exact middle, and it must read the same reversed — a word like gg. That adds 2 if any such word is left unpaired.",
    ],
    opt=("O(n)", "O(1)", "Counts over at most 26 × 26 distinct words."),
    editorial=(
        "## The one thing this teaches\n**Palindromes pair things up, with one exception in the "
        "middle.** Mirror symmetry means everything off-centre has a partner. Count the pairs "
        "greedily, then check whether a self-symmetric piece is left over for the centre.\n\n"
        "## Approach\n```java\nMap<String, Integer> waiting = new HashMap<>();\nint length = 0;\n"
        "for (String w : words) {\n    String rev = \"\" + w.charAt(1) + w.charAt(0);\n"
        "    if (waiting.getOrDefault(rev, 0) > 0) { waiting.merge(rev, -1, Integer::sum); length += 4; }\n"
        "    else waiting.merge(w, 1, Integer::sum);\n}\n"
        "for (entry : waiting) if (entry is like \"gg\" && entry.count > 0) { length += 2; break; }\n```\n\n"
        "## Why only one middle word\nTwo unpaired words in the middle would sit side by side "
        "and would have to mirror each other — but then they form a pair and were already counted.\n\n"
        "## Walkthrough: lc cl gg\n`cl` pairs with the waiting `lc` (+4). `gg` has no partner but "
        "is symmetric: +2. Total 6, e.g. `lcggcl`."
    ),
    py='''
def solve(words):
    count = Counter(words)
    length = 0
    middle = False
    for w, c in count.items():
        rev = w[::-1]
        if w == rev:
            length += (c // 2) * 4
            if c % 2:
                middle = True
        elif w < rev:
            length += min(c, count.get(rev, 0)) * 4
    return length + (2 if middle else 0)
''',
    java='''
    static int solve(String[] words) {
        HashMap<String, Integer> waiting = new HashMap<>();
        int length = 0;
        for (String w : words) {
            String rev = "" + w.charAt(1) + w.charAt(0);
            if (waiting.getOrDefault(rev, 0) > 0) { waiting.merge(rev, -1, Integer::sum); length += 4; }
            else waiting.merge(w, 1, Integer::sum);
        }
        for (Map.Entry<String, Integer> e : waiting.entrySet())
            if (e.getKey().charAt(0) == e.getKey().charAt(1) && e.getValue() > 0) { length += 2; break; }
        return length;
    }
''',
    examples=[
        ("Example 1", "3\nlc cl gg\n"),
        ("Example 2", "6\nab ty yt lc cl ab\n"),
        ("Example 3", "2\ncc ll\n"),
    ],
    hidden=[
        ("No partner", "1\nab\n"),
        ("Three identical doubles", "3\naa aa aa\n"),
        ("Two pairs", "4\nab ba ba ab\n"),
        ("Only one middle", "4\naa bb cc aa\n"),
    ],
    expl=[
        "lc + gg + cl = \"lcggcl\".",
        "ty with yt and lc with cl: e.g. \"tylcclyt\". The two ab words have no partner.",
        "Only one of cc and ll can be the middle.",
    ],
    prereqs=[
        ("hashing", "Counting words and looking up each word's reverse."),
        ("greedy", "Pairing immediately, and choosing one symmetric word for the centre."),
    ],
)

_p(
    "find-players-zero-one-losses", "Find Players With Zero or One Losses", "Medium",
    topics=["Hashing", "Sorting"], subtopics=["Counting"], companies=["Amazon"],
    shape="pairs", ret="String", todo="record every player who appears and count losses; list those with 0 losses, then those with exactly 1, each sorted",
    description=(
        "Each match is `winner loser`. Print two lines:\n\n"
        "1. the players who have played and **never lost**, in increasing order;\n"
        "2. the players who lost **exactly once**, in increasing order.\n\n"
        "Print `NONE` for an empty line.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `winner loser`.\n\n"
        "### Output\nThe two lines."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ player ≤ 10^5\nwinner ≠ loser; no match is repeated",
    hints=[
        "A winner who never appears as a loser has zero losses — but only players who played at all should be listed.",
        "One map from player to loss count covers both lists: insert winners with 0 (if absent), and add 1 for each loss.",
        "Iterate the players in sorted order (a TreeMap, or sort the keys) and split by count.",
    ],
    opt=("O(n log n)", "O(n)", "A map of up to 2n players, iterated in sorted order."),
    editorial=(
        "## The one thing this teaches\n**Register presence separately from counting.** A player "
        "who only ever won has no loss to count, so a plain loss counter never sees them. "
        "Inserting every winner with count 0 makes \"played but never lost\" visible.\n\n"
        "## Approach\n```java\nTreeMap<Integer, Integer> losses = new TreeMap<>();\n"
        "for (int[] m : matches) {\n    losses.putIfAbsent(m[0], 0);             // winner: present, maybe unbeaten\n"
        "    losses.merge(m[1], 1, Integer::sum);     // loser: one more loss\n}\n"
        "// keys with value 0 → line 1; value 1 → line 2 (TreeMap iterates in order)\n```\n\n"
        "## Why putIfAbsent\n`put(winner, 0)` would erase losses recorded for that player in "
        "earlier matches.\n\n"
        "## Counting array alternative\nWith player numbers up to 10^5, an array of counts plus a "
        "\"has played\" flag gives O(n + P) without sorting."
    ),
    py='''
def solve(p):
    players = set()
    lost = Counter()
    for w, l in p:
        players.add(w)
        players.add(l)
        lost[l] += 1
    zero = sorted(x for x in players if lost[x] == 0)
    one = sorted(x for x in players if lost[x] == 1)
    fmt = lambda xs: " ".join(map(str, xs)) if xs else "NONE"
    return fmt(zero) + "\\n" + fmt(one)
''',
    java='''
    static String solve(int[][] matches) {
        TreeMap<Integer, Integer> losses = new TreeMap<>();
        for (int[] m : matches) {
            losses.putIfAbsent(m[0], 0);
            losses.merge(m[1], 1, Integer::sum);
        }
        StringBuilder zero = new StringBuilder(), one = new StringBuilder();
        for (Map.Entry<Integer, Integer> e : losses.entrySet()) {
            StringBuilder target = e.getValue() == 0 ? zero : e.getValue() == 1 ? one : null;
            if (target == null) continue;
            if (target.length() > 0) target.append(' ');
            target.append(e.getKey());
        }
        return (zero.length() == 0 ? "NONE" : zero.toString()) + "\\n" + (one.length() == 0 ? "NONE" : one.toString());
    }
''',
    examples=[
        ("Example 1", "10\n1 3\n2 3\n3 6\n5 6\n5 7\n4 5\n4 8\n4 9\n10 4\n10 9\n"),
        ("Example 2", "4\n2 3\n1 3\n5 4\n6 4\n"),
    ],
    hidden=[
        ("One match", "1\n1 2\n"),
        ("Everyone has lost", "3\n1 2\n2 3\n3 1\n"),
        ("Winner loses later", "3\n7 8\n8 9\n9 7\n"),
        ("Many losses", "4\n1 5\n2 5\n3 5\n4 1\n"),
    ],
    expl=[
        "1, 2 and 10 never lost; 4, 5, 7 and 8 lost once each; 3, 6 and 9 lost twice.",
        "1, 2, 5 and 6 never lost; 3 and 4 each lost twice, so the second line is empty.",
    ],
    prereqs=[
        ("hashing", "A map from player to loss count, including players with none."),
        ("sorting", "Emitting keys in increasing order."),
    ],
)
