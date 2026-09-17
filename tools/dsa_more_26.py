# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 26 — twelve problems across DP, search, design and graphs.
#
#   dungeon-game                    DP backwards from the goal: what you need, not what you have
#   count-square-submatrices        dp[i][j] = largest square ending here = the count ending here
#   magnetic-force-between-balls    binary search the minimum gap; place greedily to test it
#   min-operations-reduce-x         removing from both ends = keeping the longest middle
#   word-pattern                    a bijection needs a map in each direction
#   score-of-parentheses            each innermost "()" is worth 2^depth
#   authentication-manager          expiry times only grow, so an insertion-ordered map expires from the front
#   max-events-attended             each day, attend the open event that ends soonest
#   robot-bounded-in-circle         after one pass: back at the start, or facing a new direction
#   jump-game-iii                   reachability is BFS over indices
#   min-swaps-couples               couples on couches form cycles; a cycle of c couples needs c − 1 swaps
#   kth-smallest-prime-fraction     a heap merges n sorted rows of fractions
# ===========================================================================

_p(
    "dungeon-game", "Dungeon Game", "Hard",
    topics=["Dynamic Programming", "Matrix"], subtopics=["2D DP", "Backward DP"], companies=["Microsoft", "Amazon"],
    shape="matrix", ret="long", todo="need[i][j] = health required on entering (i, j): max(1, min(need below, need right) − m[i][j]), filled from the bottom-right",
    description=(
        "A knight starts at the top-left room of a dungeon and must reach the bottom-right room, "
        "moving only **right** or **down**. Each room changes the knight's health by its value "
        "(negative is damage, positive heals). If health ever drops to **0 or below**, the "
        "knight dies — including in the first and last rooms.\n\n"
        "Print the minimum initial health that lets the knight reach the bottom-right room.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers each.\n\n"
        "### Output\nThe minimum initial health."
    ),
    constraints="1 ≤ r, c ≤ 200\n-1000 ≤ value ≤ 1000",
    hints=[
        "Tracking the best health from the start fails: a path with more health now may need more later, and a path with less may heal soon.",
        "Ask the reverse question: to survive from room (i, j) to the end, how much health must the knight have when entering it?",
        "need[i][j] = max(1, min(need[i+1][j], need[i][j+1]) − m[i][j]). At the goal, the \"next\" requirement is 1.",
    ],
    opt=("O(r · c)", "O(c)", "One pass from the bottom-right, keeping one row."),
    editorial=(
        "## The one thing this teaches\n**Pick the DP direction whose state is self-contained.** "
        "Going forward, \"current health\" is not enough — you also need the lowest point reached "
        "so far, and the two pull in different directions. Going backward, one number captures "
        "everything: the health required from here on.\n\n"
        "## Approach\n```java\nlong[] need = new long[c + 1];\nArrays.fill(need, Long.MAX_VALUE);\n"
        "need[c - 1] = 1;                          // after the goal, just stay alive\n"
        "for (int i = r - 1; i >= 0; i--) {\n"
        "    for (int j = c - 1; j >= 0; j--) {\n        long next = Math.min(need[j], need[j + 1]);   // need[j] still holds row i+1\n"
        "        need[j] = Math.max(1, next - m[i][j]);\n    }\n}\nreturn need[0];\n```\n\n"
        "## Why max(1, …)\nA big healing room could make the requirement zero or negative, but "
        "the knight must be alive on entering it. The floor of 1 encodes that.\n\n"
        "## Walkthrough (Example 1)\nThe goal (−5) needs 6. The room above it (+1) needs 5; the "
        "room left of it (+30) needs 1. Working back to the start gives 7, along "
        "right → right → down → down."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    NEG = float("-inf")

    def survives(h):
        best = [[NEG] * c for _ in range(r)]
        for i in range(r):
            for j in range(c):
                if i == 0 and j == 0:
                    before = h
                else:
                    before = max(best[i - 1][j] if i else NEG, best[i][j - 1] if j else NEG)
                if before == NEG:
                    continue
                after = before + m[i][j]
                if after >= 1:
                    best[i][j] = after
        return best[r - 1][c - 1] != NEG

    lo, hi = 1, 1 + sum(abs(v) for row in m for v in row)
    while lo < hi:
        mid = (lo + hi) // 2
        if survives(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long solve(int[][] m) {
        int r = m.length, c = m[0].length;
        long[] need = new long[c + 1];
        Arrays.fill(need, Long.MAX_VALUE);
        need[c - 1] = 1;
        for (int i = r - 1; i >= 0; i--)
            for (int j = c - 1; j >= 0; j--) {
                long next = Math.min(need[j], need[j + 1]);
                need[j] = Math.max(1, next - m[i][j]);
            }
        return need[0];
    }
''',
    examples=[("Example 1", "3 3\n-2 -3 3\n-5 -10 1\n10 30 -5\n"), ("Example 2", "1 1\n0\n")],
    hidden=[
        ("One damaging room", "1 1\n-5\n"),
        ("Heal before damage", "1 3\n5 -10 1\n"),
        ("Both paths are costly", "2 2\n100 -1000\n-1000 100\n"),
        ("Choose the route", "2 3\n0 0 0\n-3 -3 -3\n"),
        ("Healing never lowers the floor below 1", "2 2\n50 50\n50 50\n"),
    ],
    expl=[
        "Right, right, down, down: 7 − 2 − 3 + 3 + 1 − 5 = 1, and health never drops below 1 on the way.",
        "The single room does nothing; the knight must simply start alive.",
    ],
    prereqs=[
        ("dp2d", "A grid DP filled from the bottom-right with a rolling row."),
        ("recurrence", "Expressing the requirement at a cell through the requirements of the next cells."),
    ],
)

_p(
    "count-square-submatrices", "Count Square Submatrices with All Ones", "Medium",
    topics=["Dynamic Programming", "Matrix"], subtopics=["2D DP"], companies=["Google", "Amazon"],
    shape="matrix", ret="long", todo="dp[i][j] = 1 + min(up, left, up-left) for a 1 cell; the sum of all dp values is the answer",
    description=(
        "The matrix holds 0s and 1s. Print how many **square** submatrices consist entirely of 1s "
        "(of every size).\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` values, each 0 or 1.\n\n"
        "### Output\nThe number of all-ones squares."
    ),
    constraints="1 ≤ r, c ≤ 300",
    hints=[
        "Let dp[i][j] be the side of the largest all-ones square whose bottom-right corner is (i, j).",
        "Such a square of side s exists only if squares of side s − 1 end at the cell above, the cell to the left and the cell diagonally up-left.",
        "A largest square of side s at (i, j) means squares of sides 1..s all end there — so dp[i][j] is also the count ending there. Sum them.",
    ],
    opt=("O(r · c)", "O(r · c)", "One pass; the table can be the matrix itself."),
    editorial=(
        "## The one thing this teaches\n**One DP value can answer two questions.** The largest "
        "square ending at a cell also tells you how many squares end there: sides 1, 2, …, s. So "
        "the Maximal Square table, summed instead of maximised, counts every square once.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int i = 0; i < r; i++)\n    for (int j = 0; j < c; j++) {\n"
        "        if (m[i][j] == 1 && i > 0 && j > 0)\n"
        "            m[i][j] = 1 + Math.min(m[i - 1][j - 1], Math.min(m[i - 1][j], m[i][j - 1]));\n"
        "        total += m[i][j];\n    }\n```\n\n"
        "## Why the minimum of three\nA square of side s ending at (i, j) contains a square of "
        "side s − 1 ending at each of the three neighbours. The smallest of them limits how far "
        "the square can grow.\n\n"
        "## Counted exactly once\nEvery square has one bottom-right corner, and at that corner it "
        "is counted in exactly one of the sizes 1..dp."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    total = 0
    for i in range(r):
        for j in range(c):
            size = 1
            while i + size <= r and j + size <= c and all(
                m[x][y] == 1 for x in range(i, i + size) for y in range(j, j + size)
            ):
                total += 1
                size += 1
    return total
''',
    java='''
    static long solve(int[][] m) {
        int r = m.length, c = m[0].length;
        long total = 0;
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                if (m[i][j] == 1 && i > 0 && j > 0)
                    m[i][j] = 1 + Math.min(m[i - 1][j - 1], Math.min(m[i - 1][j], m[i][j - 1]));
                total += m[i][j];
            }
        return total;
    }
''',
    examples=[
        ("Example 1", "3 4\n0 1 1 1\n1 1 1 1\n0 1 1 1\n"),
        ("Example 2", "3 3\n1 0 1\n1 1 0\n1 1 0\n"),
    ],
    hidden=[
        ("Single zero", "1 1\n0\n"),
        ("Full 2 × 2", "2 2\n1 1\n1 1\n"),
        ("One row", "1 5\n1 1 0 1 1\n"),
        ("Full 3 × 3", "3 3\n1 1 1\n1 1 1\n1 1 1\n"),
    ],
    expl=[
        "10 squares of side 1, 4 of side 2 and 1 of side 3.",
        "6 squares of side 1 and 1 of side 2.",
    ],
    prereqs=[
        ("dp2d", "A table where each cell depends on three neighbours above and to the left."),
        ("grid", "Row and column indexing with care at the first row and column."),
    ],
)

_p(
    "magnetic-force-between-balls", "Magnetic Force Between Two Balls", "Medium",
    topics=["Binary Search", "Greedy", "Sorting"], subtopics=["Binary Search on Answer"], companies=["Amazon", "Roblox"],
    shape="arr_k", ret="long", todo="sort; binary search the largest d such that greedily placing each ball at the first basket ≥ last + d fits all k balls",
    description=(
        "Baskets sit at distinct positions on a line. Place `k` balls in different baskets so "
        "that the **minimum distance** between any two balls is as large as possible. Print that "
        "distance.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: the `n` basket positions.\n\n"
        "### Output\nThe largest possible minimum distance."
    ),
    constraints="2 ≤ k ≤ n ≤ 10^5\n1 ≤ position ≤ 10^9, distinct",
    hints=[
        "For a fixed distance d, is there a placement with every gap at least d? That question is easier than the original.",
        "To test d, put the first ball in the leftmost basket and each next ball in the first basket at least d further on. Greedy-early leaves the most room.",
        "If d works, every smaller d works too. Binary search for the largest d that works.",
    ],
    opt=("O(n log n + n log W)", "O(1)", "A sort, then a linear greedy check per step of a search over distances up to W."),
    editorial=(
        "## The one thing this teaches\n**Maximise a minimum by searching the answer.** \"Make "
        "the smallest gap as large as possible\" is hard directly, but \"can every gap be at least "
        "d?\" is a greedy check — and its answer flips from yes to no exactly once as d grows.\n\n"
        "## Approach\n```java\nArrays.sort(pos);\nlong lo = 1, hi = pos[n - 1] - pos[0];\n"
        "while (lo < hi) {\n    long mid = (lo + hi + 1) / 2;            // upper middle: we search for the LAST yes\n"
        "    if (fits(pos, k, mid)) lo = mid; else hi = mid - 1;\n}\nreturn lo;\n\n"
        "boolean fits(int[] pos, int k, long d) {\n    int placed = 1;\n    long last = pos[0];\n"
        "    for (int p : pos) if (p - last >= d) { placed++; last = p; }\n    return placed >= k;\n}\n```\n\n"
        "## Why the greedy check is right\nAny valid placement can be shifted so its first ball "
        "is in the leftmost basket, and each later ball moved left to the earliest basket that "
        "keeps the gap — never making a later placement harder.\n\n"
        "## Upper middle\nWhen `lo = mid` on success, rounding `mid` down could leave `lo` "
        "unchanged forever. `(lo + hi + 1) / 2` guarantees progress."
    ),
    py='''
def solve(a, k):
    a = sorted(a)
    best = 0
    for d in sorted({q - p for i, p in enumerate(a) for q in a[i + 1:]}):
        placed, last = 1, a[0]
        for p in a[1:]:
            if p - last >= d:
                placed += 1
                last = p
        if placed >= k:
            best = d
    return best
''',
    java='''
    static boolean fits(int[] pos, long k, long d) {
        long placed = 1, last = pos[0];
        for (int p : pos) if (p - last >= d) { placed++; last = p; }
        return placed >= k;
    }

    static long solve(int[] pos, long k) {
        Arrays.sort(pos);
        long lo = 1, hi = pos[pos.length - 1] - pos[0];
        while (lo < hi) {
            long mid = (lo + hi + 1) / 2;
            if (fits(pos, k, mid)) lo = mid; else hi = mid - 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "5 3\n1 2 3 4 7\n"), ("Example 2", "6 2\n5 4 3 2 1 1000000000\n")],
    hidden=[
        ("Two baskets", "2 2\n1 2\n"),
        ("Every basket used", "5 5\n1 3 6 10 15\n"),
        ("Unsorted positions", "7 3\n1 2 8 4 9 13 20\n"),
        ("Far apart", "3 2\n1 500000000 1000000000\n"),
    ],
    expl=[
        "Balls at 1, 4 and 7 are 3 apart; no placement does better.",
        "With two balls, use the two ends: 1000000000 − 1.",
    ],
    prereqs=[
        ("binary_search", "Searching for the last distance whose feasibility check succeeds."),
        ("greedy", "Placing each ball as early as the gap allows."),
    ],
)

_p(
    "min-operations-reduce-x", "Minimum Operations to Reduce X to Zero", "Medium",
    topics=["Sliding Window", "Prefix Sums", "Arrays"], subtopics=["Complement Window"], companies=["Google", "Amazon"],
    shape="arr_k", ret="int", todo="removing from both ends leaves a middle subarray summing to total − x; find the longest such window",
    description=(
        "In one operation, remove the leftmost or the rightmost element of the array and subtract "
        "it from `x`. Print the minimum number of operations that makes `x` **exactly 0**, or "
        "`-1` if it is impossible.\n\n"
        "### Input\n- Line 1: `n x`.\n- Line 2: `n` positive integers.\n\n"
        "### Output\nThe minimum number of operations, or `-1`."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^4\n1 ≤ x ≤ 10^9",
    hints=[
        "Trying every split between \"taken from the left\" and \"taken from the right\" is O(n²) pairs.",
        "Whatever you remove, the elements that remain form one contiguous middle block, with sum total − x.",
        "So maximise the length of a subarray with sum exactly total − x. All values are positive, so a sliding window finds it.",
    ],
    opt=("O(n)", "O(1)", "A single sliding window over positive values."),
    editorial=(
        "## The one thing this teaches\n**Flip a two-ended choice into one window.** Removing a "
        "prefix and a suffix is the same as keeping a middle. Minimising what you remove is "
        "maximising what you keep — and \"longest subarray with a given sum\" over positive "
        "numbers is a textbook window.\n\n"
        "## Approach\n```java\nlong target = total - x;\nif (target < 0) return -1;\n"
        "int best = -1, left = 0;\nlong sum = 0;\nfor (int right = 0; right < n; right++) {\n"
        "    sum += a[right];\n    while (sum > target && left <= right) sum -= a[left++];\n"
        "    if (sum == target) best = Math.max(best, right - left + 1);\n}\n"
        "return best == -1 ? -1 : n - best;\n```\n\n"
        "## The empty middle\nIf `x` equals the total, the middle is empty with sum 0. The loop "
        "handles it: when the window shrinks to `left = right + 1`, the sum is 0 and the length "
        "is 0, so the answer is `n`.\n\n"
        "## Why positivity matters\nWith only positive values, shrinking the window always "
        "lowers its sum, which is what lets the left edge move one way only."
    ),
    py='''
def solve(a, k):
    n = len(a)
    prefix = [0]
    for v in a:
        prefix.append(prefix[-1] + v)
    best = None
    for left in range(n + 1):
        for right in range(n - left + 1):
            if prefix[left] + (prefix[n] - prefix[n - right]) == k:
                if best is None or left + right < best:
                    best = left + right
    return -1 if best is None else best
''',
    java='''
    static int solve(int[] a, long x) {
        int n = a.length;
        long total = 0;
        for (int v : a) total += v;
        long target = total - x;
        if (target < 0) return -1;
        int best = -1, left = 0;
        long sum = 0;
        for (int right = 0; right < n; right++) {
            sum += a[right];
            while (sum > target && left <= right) sum -= a[left++];
            if (sum == target) best = Math.max(best, right - left + 1);
        }
        return best == -1 ? -1 : n - best;
    }
''',
    examples=[
        ("Example 1", "5 5\n1 1 4 2 3\n"),
        ("Example 2", "5 4\n5 6 7 8 9\n"),
        ("Example 3", "6 10\n3 2 20 1 1 3\n"),
    ],
    hidden=[
        ("Single element", "1 1\n1\n"),
        ("Take everything", "3 6\n1 2 3\n"),
        ("More than the total", "4 100\n1 2 3 4\n"),
        ("Only from the left", "4 3\n1 2 50 50\n"),
    ],
    expl=[
        "Remove 3 and 2 from the right.",
        "Every element exceeds 4.",
        "Remove 3 and 2 from the left and 3, 1, 1 from the right: five operations.",
    ],
    prereqs=[
        ("sliding_window", "A variable window over positive values, shrinking while the sum is too large."),
        ("complement", "Removing both ends equals keeping the middle, whose sum is total − x."),
    ],
)

_p(
    "word-pattern", "Word Pattern", "Easy",
    topics=["Hashing", "Strings"], subtopics=["Bijection"], companies=["Uber", "Dropbox"],
    shape="str_list", ret="String", todo="map letter → word and word → letter; any conflict in either map (or a length mismatch) means NO",
    description=(
        "Does the list of words follow the pattern? Each letter of the pattern must map to "
        "exactly one word, and each word to exactly one letter, so that replacing letters by "
        "their words reproduces the list.\n\n"
        "### Input\n- Line 1: `pattern`.\n- Line 2: `k`.\n- Line 3: the `k` words.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |pattern| ≤ 300\n1 ≤ k ≤ 3000\nLowercase English letters",
    hints=[
        "First, the pattern and the word list must have the same length.",
        "A single map from letter to word catches \"a\" meaning two different words — but not two letters meaning the same word.",
        "Keep a second map from word to letter, or check that the numbers of distinct letters, distinct words and distinct (letter, word) pairs are all equal.",
    ],
    opt=("O(n)", "O(n)", "One pass with two hash maps."),
    editorial=(
        "## The one thing this teaches\n**A bijection is two functions.** Checking one direction "
        "lets `a → dog` and `b → dog` through. Both directions must be consistent, so both need "
        "a map.\n\n"
        "## Approach\n```java\nif (pattern.length() != words.length) return false;\n"
        "Map<Character, String> toWord = new HashMap<>();\nMap<String, Character> toLetter = new HashMap<>();\n"
        "for (int i = 0; i < words.length; i++) {\n    char p = pattern.charAt(i);\n    String w = words[i];\n"
        "    if (toWord.containsKey(p) && !toWord.get(p).equals(w)) return false;\n"
        "    if (toLetter.containsKey(w) && toLetter.get(w) != p) return false;\n"
        "    toWord.put(p, w);\n    toLetter.put(w, p);\n}\nreturn true;\n```\n\n"
        "## The counting shortcut\nThe mapping is a bijection exactly when "
        "`|distinct letters| = |distinct words| = |distinct (letter, word) pairs|`. It is one line "
        "in Python and a nice check on the map version.\n\n"
        "## Compare strings with equals\nIn Java, `==` on strings compares references. Words "
        "read separately are different objects even when equal."
    ),
    py='''
def solve(s, words):
    if len(s) != len(words):
        return "NO"
    pairs = set(zip(s, words))
    return "YES" if len(pairs) == len(set(s)) == len(set(words)) else "NO"
''',
    java='''
    static String solve(String pattern, String[] words) {
        if (pattern.length() != words.length) return "NO";
        HashMap<Character, String> toWord = new HashMap<>();
        HashMap<String, Character> toLetter = new HashMap<>();
        for (int i = 0; i < words.length; i++) {
            char p = pattern.charAt(i);
            String w = words[i];
            if (toWord.containsKey(p) && !toWord.get(p).equals(w)) return "NO";
            if (toLetter.containsKey(w) && toLetter.get(w) != p) return "NO";
            toWord.put(p, w);
            toLetter.put(w, p);
        }
        return "YES";
    }
''',
    examples=[
        ("Example 1", "abba\n4\ndog cat cat dog\n"),
        ("Example 2", "abba\n4\ndog cat cat fish\n"),
        ("Example 3", "aaaa\n4\ndog cat cat dog\n"),
    ],
    hidden=[
        ("Two letters, one word", "abba\n4\ndog dog dog dog\n"),
        ("Length mismatch", "abc\n2\nx y\n"),
        ("Single pair", "a\n1\nz\n"),
        ("All distinct", "abcd\n4\nw x y z\n"),
    ],
    expl=[
        "a ↔ dog and b ↔ cat, consistently.",
        "a would have to mean both dog and fish.",
        "a would have to mean both dog and cat.",
    ],
    prereqs=[
        ("hashing", "Two maps enforcing a one-to-one correspondence."),
        ("canonical", "Comparing structures by their distinct-element counts."),
    ],
)

_p(
    "score-of-parentheses", "Score of Parentheses", "Medium",
    topics=["Stacks", "Strings"], subtopics=["Nesting Depth"], companies=["Google"],
    shape="str", ret="long", todo="track depth; every '()' pair (an opening immediately closed) adds 2^depth",
    description=(
        "Score a balanced parentheses string:\n\n"
        "- `()` scores 1;\n- `AB` scores `A + B` for balanced strings A and B;\n"
        "- `(A)` scores `2 × A`.\n\n"
        "### Input\nOne line: the string.\n\n"
        "### Output\nIts score."
    ),
    constraints="2 ≤ length ≤ 60\nThe string is balanced",
    hints=[
        "A stack of partial scores works: push 0 at '(', and at ')' pop v and add max(2v, 1) to the new top.",
        "Only the innermost \"()\" pairs create value; every enclosing pair just doubles it.",
        "So each \"()\" at depth d contributes 2^d. Sum those contributions in one pass.",
    ],
    opt=("O(n)", "O(1)", "One pass with a depth counter."),
    editorial=(
        "## The one thing this teaches\n**Distribute the rules over the leaves.** Doubling "
        "distributes over addition: `((A)(B)) = 2(A + B) = 2A + 2B`. Pushing every doubling down "
        "to the innermost `()` shows each is worth `2^depth`, and the total is their sum.\n\n"
        "## Approach\n```java\nlong score = 0;\nint depth = 0;\nfor (int i = 0; i < s.length(); i++) {\n"
        "    if (s.charAt(i) == '(') depth++;\n    else {\n        depth--;\n"
        "        if (s.charAt(i - 1) == '(') score += 1L << depth;   // a \"()\" at this depth\n    }\n}\n```\n\n"
        "## The stack version\n```java\nDeque<Long> st = new ArrayDeque<>();\nst.push(0L);\n"
        "for (char ch : s.toCharArray()) {\n    if (ch == '(') st.push(0L);\n"
        "    else { long v = st.pop(); st.push(st.pop() + Math.max(2 * v, 1)); }\n}\nreturn st.pop();\n```\n"
        "It mirrors the grammar directly and generalises to other scoring rules.\n\n"
        "## Walkthrough: (()(()))\nThe first `()` is at depth 1 (worth 2); the second at depth 2 "
        "(worth 4). Total 6."
    ),
    py='''
def solve(s):
    def score(lo, hi):
        total, depth, start = 0, 0, lo
        for i in range(lo, hi):
            depth += 1 if s[i] == "(" else -1
            if depth == 0:
                total += 1 if i == start + 1 else 2 * score(start + 1, i)
                start = i + 1
        return total
    return score(0, len(s))
''',
    java='''
    static long solve(String s) {
        long score = 0;
        int depth = 0;
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == '(') depth++;
            else {
                depth--;
                if (s.charAt(i - 1) == '(') score += 1L << depth;
            }
        }
        return score;
    }
''',
    examples=[("Example 1", "()\n"), ("Example 2", "(())\n"), ("Example 3", "()()\n")],
    hidden=[
        ("Mixed nesting", "(()(()))\n"),
        ("Deep", "((((((((((()))))))))))\n"),
        ("Siblings inside", "(()())\n"),
        ("Sibling then nested", "()(())\n"),
    ],
    expl=[
        "The base case.",
        "Doubling the base: 2.",
        "Two base cases side by side: 1 + 1.",
    ],
    prereqs=[
        ("stack", "A stack of partial scores, or the depth counter that replaces it."),
        ("recursion", "The recursive grammar A B and (A) that the scoring follows."),
    ],
)

_p(
    "authentication-manager", "Authentication Manager", "Medium",
    topics=["Design", "Hashing"], subtopics=["Expiring Entries"], companies=["Twitter", "Amazon"],
    shape="ops", ret="String", todo="map token → expiry; since expiries only grow, keep insertion order by expiry and drop expired tokens from the front",
    description=(
        "Design a session-token manager with a fixed time-to-live `ttl`:\n\n"
        "- `init ttl` — always the first operation;\n"
        "- `generate id t` — create token `id` at time `t`, expiring at `t + ttl`;\n"
        "- `renew id t` — if token `id` exists and has not expired, extend it to expire at `t + ttl`; otherwise do nothing;\n"
        "- `count t` — print the number of unexpired tokens at time `t`.\n\n"
        "A token expiring at time `t` is already expired for any operation at time `t`. Times "
        "strictly increase across operations.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: the operations.\n\n"
        "### Output\nOne line per `count`."
    ),
    constraints="1 ≤ ttl ≤ 10^8\n1 ≤ q ≤ 2·10^4\n1 ≤ t ≤ 10^8\nIDs are lowercase strings; generate never reuses a live ID",
    hints=[
        "A hash map from ID to expiry answers renew directly. Counting by scanning the map is O(tokens) per count.",
        "Times only increase, so every newly set expiry (t + ttl) is larger than all earlier ones.",
        "Keep tokens ordered by expiry: a renewed token moves to the back. Expired tokens are then always at the front — remove them before each operation.",
    ],
    opt=("O(1) amortised per operation", "O(tokens)", "Each token is removed from the front at most once per generate or renew."),
    editorial=(
        "## The one thing this teaches\n**Monotone timestamps turn a priority queue into a "
        "queue.** In general, expiring the soonest item needs a heap. When every new expiry is "
        "the latest yet, insertion order *is* expiry order — and an insertion-ordered map both "
        "looks up by ID and expires from the front.\n\n"
        "## Approach\n```java\nLinkedHashMap<String, Integer> expiry = new LinkedHashMap<>();\n\n"
        "void expire(int t) {\n    Iterator<Map.Entry<String, Integer>> it = expiry.entrySet().iterator();\n"
        "    while (it.hasNext() && it.next().getValue() <= t) it.remove();\n}\n\n"
        "void generate(String id, int t) { expire(t); expiry.put(id, t + ttl); }\n"
        "void renew(String id, int t) {\n    expire(t);\n"
        "    if (expiry.containsKey(id)) { expiry.remove(id); expiry.put(id, t + ttl); }   // move to the back\n}\n"
        "int count(int t) { expire(t); return expiry.size(); }\n```\n\n"
        "## Why remove then put\n`LinkedHashMap.put` on an existing key keeps its old position. "
        "Removing first makes the renewed token the newest entry, preserving the order.\n\n"
        "## The boundary\n\"Expires at t\" means gone at t, so the test is `expiry <= t`."
    ),
    py='''
def solve(ops):
    ttl = 0
    expiry = {}
    out = []
    for op in ops:
        kind = op[0]
        if kind == "init":
            ttl = int(op[1])
        elif kind == "generate":
            expiry[op[1]] = int(op[2]) + ttl
        elif kind == "renew":
            t = int(op[2])
            if expiry.get(op[1], 0) > t:
                expiry[op[1]] = t + ttl
        else:
            t = int(op[1])
            out.append(str(sum(1 for e in expiry.values() if e > t)))
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        long ttl = 0;
        LinkedHashMap<String, Long> expiry = new LinkedHashMap<>();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("init")) { ttl = Long.parseLong(op[1]); continue; }
            long t = Long.parseLong(op[op.length - 1]);
            Iterator<Map.Entry<String, Long>> it = expiry.entrySet().iterator();
            while (it.hasNext() && it.next().getValue() <= t) it.remove();
            if (op[0].equals("generate")) expiry.put(op[1], t + ttl);
            else if (op[0].equals("renew")) {
                if (expiry.containsKey(op[1])) { expiry.remove(op[1]); expiry.put(op[1], t + ttl); }
            } else {
                if (sb.length() > 0) sb.append('\\n');
                sb.append(expiry.size());
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "8\ninit 5\nrenew aaa 1\ngenerate aaa 2\ncount 6\ngenerate bbb 7\nrenew aaa 8\nrenew bbb 10\ncount 15\n"),
    ],
    hidden=[
        ("Count on an empty manager", "2\ninit 10\ncount 1\n"),
        ("Renewal keeps a token alive", "6\ninit 3\ngenerate x 1\nrenew x 3\ncount 5\nrenew x 6\ncount 8\n"),
        ("Expiry exactly at the count", "4\ninit 5\ngenerate a 1\ncount 5\ncount 6\n"),
        ("Renew reorders expiries", "8\ninit 10\ngenerate a 1\ngenerate b 2\nrenew a 5\ncount 11\ncount 12\ncount 14\ncount 15\n"),
    ],
    expl=[
        "At 6, aaa (expires 7) is live: 1. At 8 aaa has expired, so its renewal does nothing. bbb is renewed at 10 to expire at 15, so the count at 15 is 0.",
    ],
    prereqs=[
        ("design_ds", "Operations sharing one structure, each cleaning up expired state first."),
        ("hashing", "An insertion-ordered hash map used as both a lookup table and a queue."),
    ],
)

_p(
    "max-events-attended", "Maximum Number of Events That Can Be Attended", "Medium",
    topics=["Greedy", "Heaps", "Intervals"], subtopics=["Earliest Deadline First"], companies=["Google", "Amazon"],
    shape="pairs", ret="int", todo="sweep days; add events starting today to a min-heap of end days, drop ended ones, attend the one ending soonest",
    description=(
        "Event `i` runs from day `start` to day `end`, inclusive. You can attend an event on any "
        "single day within its range, and at most one event per day. Print the maximum number of "
        "events you can attend.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `start end`.\n\n"
        "### Output\nThe maximum number of events."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ start ≤ end ≤ 10^5",
    hints=[
        "Think day by day. Several events may be available on a given day — which one should you use it for?",
        "The event ending soonest has the fewest remaining chances; the others can wait.",
        "Sort by start. For each day, push the end days of events starting that day into a min-heap, pop events that have already ended, and attend the top one.",
    ],
    opt=("O((n + D) log n)", "O(n)", "D is the last day; each event enters and leaves the heap once."),
    editorial=(
        "## The one thing this teaches\n**Earliest deadline first.** When tasks have windows and "
        "each slot serves one task, the task whose window closes first is the one to serve now. "
        "Swapping it for any other never loses: the other one can still use a later day.\n\n"
        "## Approach\n```java\nsort events by start;\nPriorityQueue<Integer> ends = new PriorityQueue<>();\n"
        "int i = 0, attended = 0;\nfor (int day = 1; day <= lastDay; day++) {\n"
        "    while (i < n && ev[i][0] == day) ends.add(ev[i++][1]);   // opened today\n"
        "    while (!ends.isEmpty() && ends.peek() < day) ends.poll();  // already over\n"
        "    if (!ends.isEmpty()) { ends.poll(); attended++; }           // attend the most urgent\n}\n```\n\n"
        "## Sorting by end alone is not enough\nPicking events in order of end day and giving each "
        "its earliest free day needs a structure to find free days. The day sweep with a heap "
        "avoids that entirely.\n\n"
        "## Skipping idle days\nWhen the heap is empty, jump `day` to the next start instead of "
        "counting through empty days — the answer is the same."
    ),
    py='''
def solve(p):
    match_of_day = {}

    def try_event(i, seen):
        s, e = p[i]
        for d in range(s, e + 1):
            if d in seen:
                continue
            seen.add(d)
            if d not in match_of_day or try_event(match_of_day[d], seen):
                match_of_day[d] = i
                return True
        return False

    return sum(1 for i in range(len(p)) if try_event(i, set()))
''',
    java='''
    static int solve(int[][] ev) {
        int n = ev.length;
        Arrays.sort(ev, (x, y) -> Integer.compare(x[0], y[0]));
        int lastDay = 0;
        for (int[] e : ev) lastDay = Math.max(lastDay, e[1]);
        PriorityQueue<Integer> ends = new PriorityQueue<>();
        int i = 0, attended = 0;
        for (int day = 1; day <= lastDay; day++) {
            while (i < n && ev[i][0] == day) ends.add(ev[i++][1]);
            while (!ends.isEmpty() && ends.peek() < day) ends.poll();
            if (!ends.isEmpty()) { ends.poll(); attended++; }
        }
        return attended;
    }
''',
    examples=[("Example 1", "3\n1 2\n2 3\n3 4\n"), ("Example 2", "4\n1 2\n2 3\n3 4\n1 2\n")],
    hidden=[
        ("One event", "1\n1 1\n"),
        ("Same single day", "3\n1 1\n1 1\n1 1\n"),
        ("Short events first", "5\n1 5\n1 5\n1 5\n2 3\n2 3\n"),
        ("Too many for the window", "4\n1 2\n1 2\n1 2\n1 2\n"),
        ("Long event waits", "3\n1 10\n2 2\n1 1\n"),
    ],
    expl=[
        "One event on each of days 1, 2 and 3.",
        "Days 1–4 each host one: [1,2] on day 1, the other [1,2] on day 2, [2,3] on day 3, [3,4] on day 4.",
    ],
    prereqs=[
        ("heap", "A min-heap of end days, popping expired and most urgent events."),
        ("greedy", "Earliest deadline first, justified by an exchange argument."),
    ],
)

_p(
    "robot-bounded-in-circle", "Robot Bounded in Circle", "Medium",
    topics=["Simulation", "Math"], subtopics=["Direction Vectors"], companies=["Amazon", "Goldman Sachs"],
    shape="str", ret="String", todo="simulate one pass; the robot stays bounded if it is back at the origin or no longer facing north",
    description=(
        "A robot starts at `(0, 0)` facing north. It follows the instructions — `G` moves one "
        "step forward, `L` turns 90° left, `R` turns 90° right — and then **repeats them "
        "forever**. Print `YES` if the robot stays within some circle, otherwise `NO`.\n\n"
        "### Input\nOne line: the instructions.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ length ≤ 100\nOnly G, L and R",
    hints=[
        "\"Forever\" cannot be simulated. Look at what one pass does: a displacement and a change of direction.",
        "If the direction is unchanged and the robot moved, each pass adds the same displacement — it drifts away.",
        "If the direction changed, four passes rotate the displacement through all four directions and bring the robot back. So: bounded iff back at the origin or not facing north after one pass.",
    ],
    opt=("O(n)", "O(1)", "One pass of simulation."),
    editorial=(
        "## The one thing this teaches\n**Reason about repetition through what one period does.** "
        "A repeated process is determined by its effect per cycle. Here that effect is a shift "
        "and a rotation, and rotations have order at most 4.\n\n"
        "## Approach\n```java\nint[][] dir = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};   // N, E, S, W\n"
        "int x = 0, y = 0, d = 0;\nfor (char ch : s.toCharArray()) {\n"
        "    if (ch == 'G') { x += dir[d][0]; y += dir[d][1]; }\n"
        "    else if (ch == 'R') d = (d + 1) % 4;\n    else d = (d + 3) % 4;        // left = three rights, avoiding negative %\n}\n"
        "return (x == 0 && y == 0) || d != 0;\n```\n\n"
        "## Why four passes return\nIf one pass ends facing east (a 90° turn), the next pass's "
        "displacement is the first one rotated by 90°, and so on. Four displacements rotated by "
        "0°, 90°, 180° and 270° sum to zero. A 180° turn returns after two passes.\n\n"
        "## Direction as an index\nStoring the direction as 0–3 into a vector table turns turning "
        "into modular arithmetic and moving into one addition."
    ),
    py='''
def solve(s):
    x = y = 0
    dx, dy = 0, 1
    for _ in range(4):
        for ch in s:
            if ch == "G":
                x, y = x + dx, y + dy
            elif ch == "L":
                dx, dy = -dy, dx
            else:
                dx, dy = dy, -dx
    return "YES" if (x, y) == (0, 0) else "NO"
''',
    java='''
    static String solve(String s) {
        int[][] dir = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        int x = 0, y = 0, d = 0;
        for (char ch : s.toCharArray()) {
            if (ch == 'G') { x += dir[d][0]; y += dir[d][1]; }
            else if (ch == 'R') d = (d + 1) % 4;
            else d = (d + 3) % 4;
        }
        return (x == 0 && y == 0) || d != 0 ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "GGLLGG\n"), ("Example 2", "GG\n"), ("Example 3", "GL\n")],
    hidden=[
        ("Turn only", "L\n"),
        ("Square with a spare step", "GRGRGRG\n"),
        ("Ends facing north, displaced", "GLGLGGLGL\n"),
        ("Full square", "GGRGGRGGRGGR\n"),
    ],
    expl=[
        "Up two, turn around, down two: back at the origin.",
        "Two steps north every pass, forever.",
        "Each pass turns left, so after four passes the robot is home.",
    ],
    prereqs=[
        ("simulation", "Stepping through instructions with a position and a direction."),
        ("modulo", "Turning as addition modulo 4."),
    ],
)

_p(
    "jump-game-iii", "Jump Game III", "Medium",
    topics=["Graphs", "BFS", "Arrays"], subtopics=["Implicit Graph"], companies=["Microsoft", "Amazon"],
    shape="arr_k", ret="String", todo="BFS from start over indices; from i go to i + a[i] and i − a[i] when inside the array",
    description=(
        "Start at index `start`. From index `i` you may jump to `i + a[i]` or `i − a[i]`, if that "
        "index is inside the array. Can you reach **any** index whose value is 0?\n\n"
        "### Input\n- Line 1: `n start`.\n- Line 2: `n` non-negative integers.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 5·10^4\n0 ≤ a[i] < n\n0 ≤ start < n",
    hints=[
        "Indices are nodes; each has at most two outgoing edges.",
        "Some jumps lead back to indices already explored. Without a visited mark, the search can loop forever.",
        "BFS (or DFS) from start, marking visited indices, and stop as soon as a zero is found.",
    ],
    opt=("O(n)", "O(n)", "Each index is visited at most once."),
    editorial=(
        "## The one thing this teaches\n**Arrays with jump rules are graphs.** No edge list is "
        "stored — the neighbours of `i` are computed from `a[i]` — but reachability is plain "
        "BFS, and the visited array is what makes it terminate.\n\n"
        "## Approach\n```java\nboolean[] seen = new boolean[n];\nDeque<Integer> q = new ArrayDeque<>();\n"
        "q.add(start); seen[start] = true;\nwhile (!q.isEmpty()) {\n    int i = q.poll();\n"
        "    if (a[i] == 0) return true;\n    for (int j : new int[]{i + a[i], i - a[i]})\n"
        "        if (j >= 0 && j < n && !seen[j]) { seen[j] = true; q.add(j); }\n}\nreturn false;\n```\n\n"
        "## Cycles are common\nIn `1 1`, index 0 jumps to 1 and index 1 jumps back to 0. Marking "
        "on enqueue guarantees each index is processed once.\n\n"
        "## BFS or DFS?\nOnly reachability matters, not the number of jumps, so either works. "
        "An iterative version avoids deep recursion on long jump chains."
    ),
    py='''
def solve(a, k):
    import sys
    sys.setrecursionlimit(100000)
    seen = set()

    def reach(i):
        if i < 0 or i >= len(a) or i in seen:
            return False
        if a[i] == 0:
            return True
        seen.add(i)
        return reach(i + a[i]) or reach(i - a[i])

    return "YES" if reach(k) else "NO"
''',
    java='''
    static String solve(int[] a, long start) {
        int n = a.length;
        boolean[] seen = new boolean[n];
        ArrayDeque<Integer> q = new ArrayDeque<>();
        q.add((int) start);
        seen[(int) start] = true;
        while (!q.isEmpty()) {
            int i = q.poll();
            if (a[i] == 0) return "YES";
            for (int j : new int[]{i + a[i], i - a[i]})
                if (j >= 0 && j < n && !seen[j]) { seen[j] = true; q.add(j); }
        }
        return "NO";
    }
''',
    examples=[
        ("Example 1", "7 5\n4 2 3 0 3 1 2\n"),
        ("Example 2", "7 0\n4 2 3 0 3 1 2\n"),
        ("Example 3", "5 2\n3 0 2 1 2\n"),
    ],
    hidden=[
        ("Start on a zero", "1 0\n0\n"),
        ("Two-index cycle", "2 0\n1 1\n"),
        ("Both jumps leave the array", "3 1\n2 2 0\n"),
        ("Long chain", "6 0\n1 1 1 1 1 0\n"),
    ],
    expl=[
        "5 → 4 → 1 → 3, where the value is 0.",
        "0 → 4 → 1 → 3.",
        "From 2 the reachable indices are 0, 3 and 4; index 1, the only zero, is never reached.",
    ],
    prereqs=[
        ("bfs", "Breadth-first search with a visited array."),
        ("visited_set", "Marking indices so cycles of jumps terminate."),
    ],
)

_p(
    "min-swaps-couples", "Couples Holding Hands", "Hard",
    topics=["Union-Find", "Graphs", "Greedy"], subtopics=["Cycle Decomposition"], companies=["Google"],
    shape="arr", ret="int", todo="union the couples sitting on each couch; the answer is the number of couples minus the number of components",
    description=(
        "`2m` people sit in a row of seats, where seats `2i` and `2i + 1` form couch `i`. People "
        "are numbered `0` to `2m − 1`, and the couples are `(0, 1)`, `(2, 3)`, and so on. In one "
        "swap, any two people exchange seats. Print the minimum number of swaps so that every "
        "couple shares a couch.\n\n"
        "### Input\n- Line 1: `2m`.\n- Line 2: the person in each seat.\n\n"
        "### Output\nThe minimum number of swaps."
    ),
    constraints="2 ≤ 2m ≤ 60\nThe row is a permutation of 0..2m − 1",
    hints=[
        "A person's partner is person ^ 1 — the other number in {2c, 2c + 1}.",
        "Make each couple a node and each couch an edge between the two couples sitting on it. Every node then has degree 2, so the graph is a union of cycles.",
        "A cycle through c couples needs exactly c − 1 swaps to fix. Summed over cycles: m − (number of cycles) — count them with union-find.",
    ],
    opt=("O(m · α(m))", "O(m)", "One union per couch."),
    editorial=(
        "## The one thing this teaches\n**Minimum swaps = elements − cycles.** Whenever swaps "
        "untangle a structure made of cycles, each swap can split at most one cycle into two. A "
        "cycle of size c starts as one component and must end as c, so it needs c − 1 swaps — "
        "and the greedy \"fix one couch at a time\" achieves exactly that.\n\n"
        "## Approach\n```java\nint[] parent = couples 0..m−1;\nint components = m;\n"
        "for (int couch = 0; couch < m; couch++) {\n    int a = row[2 * couch] / 2, b = row[2 * couch + 1] / 2;   // couples on this couch\n"
        "    if (union(a, b)) components--;\n}\nreturn m - components;\n```\n\n"
        "## The greedy view\nWalk the couches left to right. If a couch's second person is not "
        "the first person's partner, swap the partner into that seat. Each swap completes one "
        "couch and never breaks a finished one — and it produces the same count.\n\n"
        "## Walkthrough: 0 2 1 3\nCouch 0 holds couples 0 and 1; couch 1 holds couples 0 and 1. "
        "One component of size 2: 2 − 1 = 1 swap."
    ),
    py='''
def solve(a):
    row = list(a)
    where = {person: seat for seat, person in enumerate(row)}
    swaps = 0
    for seat in range(0, len(row), 2):
        partner = row[seat] ^ 1
        if row[seat + 1] != partner:
            other = where[partner]
            row[other], row[seat + 1] = row[seat + 1], partner
            where[row[other]] = other
            where[partner] = seat + 1
            swaps += 1
    return swaps
''',
    java='''
    static int find(int[] p, int x) {
        while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
        return x;
    }

    static int solve(int[] row) {
        int m = row.length / 2;
        int[] parent = new int[m];
        for (int i = 0; i < m; i++) parent[i] = i;
        int components = m;
        for (int couch = 0; couch < m; couch++) {
            int a = find(parent, row[2 * couch] / 2), b = find(parent, row[2 * couch + 1] / 2);
            if (a != b) { parent[a] = b; components--; }
        }
        return m - components;
    }
''',
    examples=[("Example 1", "4\n0 2 1 3\n"), ("Example 2", "4\n3 2 0 1\n")],
    hidden=[
        ("One couple", "2\n1 0\n"),
        ("Two out of place", "6\n0 2 4 1 3 5\n"),
        ("A four-couple cycle", "8\n0 4 1 2 5 6 3 7\n"),
        ("Already seated", "6\n5 4 0 1 2 3\n"),
    ],
    expl=[
        "Swap 2 and 1: couches (0, 1) and (2, 3).",
        "Both couches already hold a couple.",
    ],
    prereqs=[
        ("union_find", "Counting components while uniting couples that share a couch."),
        ("graph_cycle", "Swaps needed to sort a permutation: size minus number of cycles."),
    ],
)

_p(
    "kth-smallest-prime-fraction", "K-th Smallest Prime Fraction", "Hard",
    topics=["Heaps", "Binary Search", "Math"], subtopics=["K-way Merge"], companies=["Google", "Amazon"],
    shape="arr_k", ret="String", todo="seed a min-heap with a[0]/a[j] for every j; pop k − 1 times, each time pushing the next numerator in that row",
    description=(
        "A sorted array starts with 1 and continues with distinct primes. For every pair "
        "`i < j`, form the fraction `a[i] / a[j]`. Print the `k`-th smallest fraction as "
        "`numerator denominator`.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: the `n` values, increasing.\n\n"
        "### Output\n`p q` for the k-th smallest fraction p / q."
    ),
    constraints="2 ≤ n ≤ 1000\n1 ≤ k ≤ n(n − 1)/2\n1 ≤ a[i] ≤ 3·10^4",
    hints=[
        "Generating and sorting all n²/2 fractions is O(n² log n).",
        "For a fixed denominator a[j], the fractions a[0]/a[j] < a[1]/a[j] < … are already sorted — n sorted lists.",
        "Merge those lists with a min-heap: start with each list's smallest, pop k − 1 times, pushing the popped fraction's successor. Compare fractions by cross-multiplication.",
    ],
    opt=("O((n + k) log n)", "O(n)", "A heap of at most n entries, popped k times."),
    editorial=(
        "## The one thing this teaches\n**K-way merge finds the k-th smallest without sorting "
        "everything.** The fractions split into sorted rows (one per denominator). A heap holding "
        "each row's current head yields the global order one element at a time.\n\n"
        "## Approach\n```java\nPriorityQueue<int[]> pq = new PriorityQueue<>((x, y) ->\n"
        "    Long.compare((long) a[x[0]] * a[y[1]], (long) a[y[0]] * a[x[1]]));   // a[x0]/a[x1] vs a[y0]/a[y1]\n"
        "for (int j = 1; j < n; j++) pq.add(new int[]{0, j});\n"
        "for (int step = 1; step < k; step++) {\n    int[] top = pq.poll();\n"
        "    if (top[0] + 1 < top[1]) pq.add(new int[]{top[0] + 1, top[1]});   // next numerator, same row\n}\n"
        "int[] ans = pq.poll();\n```\n\n"
        "## Why cross-multiply\n`p/q < r/s` ⇔ `p·s < r·q` for positive denominators. Integer "
        "arithmetic avoids floating-point ties and rounding entirely.\n\n"
        "## A faster route\nBinary search on the fraction's value, counting fractions below it "
        "with two pointers, reaches O(n log W) — the same \"count instead of select\" idea as the "
        "k-th smallest pair distance."
    ),
    py='''
def solve(a, k):
    from fractions import Fraction
    fracs = sorted((Fraction(a[i], a[j]), a[i], a[j]) for i in range(len(a)) for j in range(i + 1, len(a)))
    _, p, q = fracs[k - 1]
    return f"{p} {q}"
''',
    java='''
    static String solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) ->
            Long.compare((long) a[x[0]] * a[y[1]], (long) a[y[0]] * a[x[1]]));
        for (int j = 1; j < n; j++) pq.add(new int[]{0, j});
        for (int step = 1; step < k; step++) {
            int[] top = pq.poll();
            if (top[0] + 1 < top[1]) pq.add(new int[]{top[0] + 1, top[1]});
        }
        int[] ans = pq.poll();
        return a[ans[0]] + " " + a[ans[1]];
    }
''',
    examples=[("Example 1", "4 3\n1 2 3 5\n"), ("Example 2", "2 1\n1 7\n")],
    hidden=[
        ("Largest fraction", "5 10\n1 2 3 5 7\n"),
        ("Smallest fraction", "5 1\n1 2 3 5 7\n"),
        ("Middle of six", "6 7\n1 2 3 5 7 11\n"),
        ("Two primes", "3 2\n1 2 3\n"),
    ],
    expl=[
        "In order: 1/5, 1/3, 2/5, 1/2, 3/5, 2/3. The third is 2/5.",
        "The only fraction is 1/7.",
    ],
    prereqs=[
        ("heap", "A min-heap merging several sorted sequences."),
        ("overflow", "Comparing fractions by cross-multiplying in 64-bit integers."),
    ],
)
