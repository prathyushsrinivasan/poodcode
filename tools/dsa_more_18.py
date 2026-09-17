# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 18 — interview classics as extra practice.
#
#   three-sum-closest          two pointers, tracking the best distance instead of equality
#   valid-sudoku               three families of sets — rows, columns, boxes — checked in one pass
#   median-two-sorted-arrays   binary search the partition of the shorter array
#   maximal-rectangle          each row is a histogram; reuse Largest Rectangle in Histogram
#   burst-balloons             interval DP on the LAST balloon burst
#   regex-matching             2-D DP over (text prefix, pattern prefix)
#   critical-connections       Tarjan's low-link: an edge is a bridge when the child cannot reach above it
#   reverse-bits               shift bits out of one number into another, 32 times
#   path-sum-iii               prefix sums along a root-to-node path, in a hash map
#   target-sum                 signs split the array in two; count subsets with the right sum
# ===========================================================================

_p(
    "three-sum-closest", "3Sum Closest", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers", "Sorting"], companies=["Meta", "Amazon"],
    shape="arr_k", ret="long", todo="sort; fix i, two-pointer the rest, keeping the sum closest to target",
    description=(
        "Choose three elements at different positions whose sum is **closest** to `target`, and "
        "print that sum. The closest sum is unique.\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: `n` integers.\n\n### Output\nThe closest sum."
    ),
    constraints="3 ≤ n ≤ 500\n-1000 ≤ a[i] ≤ 1000\n-10^4 ≤ target ≤ 10^4",
    hints=[
        "It is 3Sum with 'equals' replaced by 'as close as possible'.",
        "Sort. Fix a[i]; with l = i + 1 and r = n − 1, a sum below the target needs l++, above needs r--.",
        "Update the best whenever |sum − target| improves; an exact hit can return immediately.",
    ],
    opt=("O(n²)", "O(1)", "A sort and an O(n) scan per fixed element."),
    editorial=(
        "## The one thing this teaches\n**Two pointers work for 'closest' as well as 'equal'.** The "
        "moves are driven by the sign of `sum − target`, which is defined whether or not an exact "
        "match exists. What changes is only what you record: the best distance seen, not a hit.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong best = (long) a[0] + a[1] + a[2];\n"
        "for (int i = 0; i < n - 2; i++) {\n    int l = i + 1, r = n - 1;\n    while (l < r) {\n"
        "        long s = (long) a[i] + a[l] + a[r];\n"
        "        if (Math.abs(s - target) < Math.abs(best - target)) best = s;\n"
        "        if (s == target) return s;\n        if (s < target) l++; else r--;\n    }\n}\n```\n\n"
        "## Why no sum is skipped that could win\nWhen `s < target`, every sum with the same `i` and "
        "`l` and a smaller `r` is even further below the target, so discarding `l` loses nothing — "
        "the same argument as Two Sum II."
    ),
    py='''
def solve(a, k):
    from itertools import combinations
    return min((sum(c) for c in combinations(a, 3)), key=lambda s: abs(s - k))
''',
    java='''
    static long solve(int[] a, long target) {
        Arrays.sort(a);
        int n = a.length;
        long best = (long) a[0] + a[1] + a[2];
        for (int i = 0; i < n - 2; i++) {
            int l = i + 1, r = n - 1;
            while (l < r) {
                long s = (long) a[i] + a[l] + a[r];
                if (Math.abs(s - target) < Math.abs(best - target)) best = s;
                if (s == target) return s;
                if (s < target) l++; else r--;
            }
        }
        return best;
    }
''',
    examples=[("Example 1", "4 1\n-1 2 1 -4\n"), ("Example 2", "3 1\n0 0 0\n")],
    hidden=[
        ("Target far above", "3 100\n1 2 3\n"),
        ("Negatives", "5 -11\n-5 -4 -3 1 2\n"),
        ("Exact hit", "6 11\n1 1 1 1 1 9\n"),
    ],
    expl=[
        "−1 + 2 + 1 = 2 is closest to 1.",
        "The only triple sums to 0.",
    ],
    prereqs=[
        ("two_pointers", "Converging pointers steered by the sign of sum − target."),
        ("sorting", "Sorting makes the pointer moves meaningful."),
    ],
)

_p(
    "valid-sudoku", "Valid Sudoku", "Medium",
    topics=["Hashing", "Matrix"], subtopics=["Hash Set", "Grid"], companies=["Amazon", "Apple", "Uber"],
    shape="grid", ret="String", todo="for each filled cell, check its digit is new to its row, its column and its 3×3 box",
    description=(
        "Is a partially filled 9×9 Sudoku board **valid** so far — no digit repeated in any row, "
        "column, or 3×3 box? Empty cells (`.`) are ignored; the board need not be solvable.\n\n"
        "### Input\n- Line 1: `9 9`.\n- Next 9 lines: a row of digits and `.`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="The board is 9×9, using the characters '1'–'9' and '.'.",
    hints=[
        "Each digit must be unique within 27 groups: 9 rows, 9 columns, 9 boxes.",
        "Keep a set (or a 9-bit mask) per row, per column and per box.",
        "Cell (i, j) is in box (i / 3) * 3 + j / 3.",
    ],
    opt=("O(81)", "O(81)", "One pass over the board with 27 small sets."),
    editorial=(
        "## The one thing this teaches\n**Index arithmetic assigns cells to groups.** Rows and "
        "columns are given; boxes need a formula. `(i / 3) * 3 + j / 3` numbers the boxes 0–8 in "
        "reading order, and then all 27 constraints are the same check: \"have I seen this digit "
        "in this group?\"\n\n"
        "## Approach\n```java\nint[] row = new int[9], col = new int[9], box = new int[9];   // bitmasks\n"
        "for (int i = 0; i < 9; i++)\n    for (int j = 0; j < 9; j++) {\n"
        "        if (g[i][j] == '.') continue;\n        int bit = 1 << (g[i][j] - '1'), b = (i / 3) * 3 + j / 3;\n"
        "        if ((row[i] & bit) != 0 || (col[j] & bit) != 0 || (box[b] & bit) != 0) return \"NO\";\n"
        "        row[i] |= bit; col[j] |= bit; box[b] |= bit;\n    }\nreturn \"YES\";\n```\n\n"
        "## Valid is not solvable\nThe question is only about repeats among the filled cells. A "
        "board can be valid and have no solution; checking solvability is the (much harder) "
        "Sudoku Solver."
    ),
    py='''
def solve(g):
    seen = set()
    for i in range(9):
        for j in range(9):
            ch = g[i][j]
            if ch == ".":
                continue
            keys = [("r", i, ch), ("c", j, ch), ("b", i // 3, j // 3, ch)]
            if any(k in seen for k in keys):
                return "NO"
            seen.update(keys)
    return "YES"
''',
    java='''
    static String solve(char[][] g) {
        int[] row = new int[9], col = new int[9], box = new int[9];
        for (int i = 0; i < 9; i++)
            for (int j = 0; j < 9; j++) {
                if (g[i][j] == '.') continue;
                int bit = 1 << (g[i][j] - '1'), b = (i / 3) * 3 + j / 3;
                if ((row[i] & bit) != 0 || (col[j] & bit) != 0 || (box[b] & bit) != 0) return "NO";
                row[i] |= bit; col[j] |= bit; box[b] |= bit;
            }
        return "YES";
    }
''',
    examples=[
        ("Example 1", "9 9\n53..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79\n"),
        ("Example 2", "9 9\n83..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79\n"),
    ],
    hidden=[
        ("Empty board", "9 9\n" + ".........\n" * 9),
        ("Repeat in a row", "9 9\n1.......1\n" + ".........\n" * 8),
        ("Repeat in a box only", "9 9\n1........\n.1.......\n" + ".........\n" * 7),
    ],
    expl=[
        "No digit repeats in any row, column or box.",
        "The 8 in the top-left corner repeats the 8 further down column 0 (and in its box).",
    ],
    prereqs=[
        ("hashing", "A set or bitmask per row, column and box."),
        ("grid", "Mapping a cell to its 3×3 box with (i / 3) * 3 + j / 3."),
    ],
)

_p(
    "median-two-sorted-arrays", "Median of Two Sorted Arrays", "Hard",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search"], companies=["Google", "Amazon", "Apple"],
    shape="arr2", ret="String", todo="binary search how many elements of the shorter array go in the left half",
    description=(
        "Find the median of the combined contents of two sorted arrays in O(log(min(m, n))).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the first sorted array (empty if n is 0).\n"
        "- Line 3: `m`.\n- Line 4: the second sorted array (empty if m is 0).\n\n"
        "### Output\nThe median: an integer if it is one, otherwise the value ending in `.5` "
        "(for example `2.5` or `-3.5`)."
    ),
    constraints="0 ≤ n, m ≤ 1000, 1 ≤ n + m\n-10^6 ≤ values ≤ 10^6",
    hints=[
        "Merging is O(n + m). The target is logarithmic.",
        "Split both arrays so the left parts together hold half the elements. If A contributes i, B contributes half − i.",
        "The split is right when A[i−1] ≤ B[j] and B[j−1] ≤ A[i]. Binary search i over the shorter array; use ±∞ at the edges.",
    ],
    opt=("O(log min(n, m))", "O(1)", "A binary search over the partition point of the shorter array."),
    editorial=(
        "## The one thing this teaches\n**Binary search a partition, not a value.** The median "
        "splits the combined data into two halves with every left element ≤ every right element. "
        "Choosing how many elements come from A fixes how many come from B, and whether the split "
        "is valid is monotone in that choice.\n\n"
        "## Approach\n```java\n// ensure A is the shorter array; half = (n + m + 1) / 2\nint lo = 0, hi = n;\n"
        "while (lo <= hi) {\n    int i = (lo + hi) / 2, j = half - i;\n"
        "    long aL = i == 0 ? MIN : A[i - 1], aR = i == n ? MAX : A[i];\n"
        "    long bL = j == 0 ? MIN : B[j - 1], bR = j == m ? MAX : B[j];\n"
        "    if (aL <= bR && bL <= aR) {\n"
        "        if ((n + m) % 2 == 1) return max(aL, bL);\n"
        "        return (max(aL, bL) + min(aR, bR)) / 2.0;\n    }\n"
        "    if (aL > bR) hi = i - 1; else lo = i + 1;\n}\n```\n\n"
        "## Why search the shorter array\nThen `j = half − i` is always within B's bounds, and the "
        "search is logarithmic in the smaller size.\n\n"
        "## The output format\nThe median of integers is an integer or ends in .5, so it can be "
        "printed exactly without floating-point formatting surprises: compute the sum of the two "
        "middle values and halve it by hand."
    ),
    py='''
def solve(a, b):
    c = sorted(a + b)
    t = len(c)
    if t % 2:
        return str(c[t // 2])
    s = c[t // 2 - 1] + c[t // 2]
    if s % 2 == 0:
        return str(s // 2)
    sign = "-" if s < 0 else ""
    return f"{sign}{abs(s) // 2}.5"
''',
    java='''
    static String solve(int[] a, int[] b) {
        if (a.length > b.length) { int[] t = a; a = b; b = t; }
        int n = a.length, m = b.length, half = (n + m + 1) / 2;
        long MIN = Long.MIN_VALUE / 4, MAX = Long.MAX_VALUE / 4;
        int lo = 0, hi = n;
        while (lo <= hi) {
            int i = (lo + hi) / 2, j = half - i;
            long aL = i == 0 ? MIN : a[i - 1], aR = i == n ? MAX : a[i];
            long bL = j == 0 ? MIN : b[j - 1], bR = j == m ? MAX : b[j];
            if (aL <= bR && bL <= aR) {
                if ((n + m) % 2 == 1) return String.valueOf(Math.max(aL, bL));
                long s = Math.max(aL, bL) + Math.min(aR, bR);
                if (s % 2 == 0) return String.valueOf(s / 2);
                return (s < 0 ? "-" : "") + (Math.abs(s) / 2) + ".5";
            }
            if (aL > bR) hi = i - 1; else lo = i + 1;
        }
        return "";
    }
''',
    examples=[("Example 1", "2\n1 3\n1\n2\n"), ("Example 2", "2\n1 2\n2\n3 4\n")],
    hidden=[
        ("One array empty", "0\n\n1\n1\n"),
        ("Negative half", "1\n-5\n1\n-2\n"),
        ("Disjoint ranges", "3\n1 2 3\n3\n4 5 6\n"),
        ("All zeros", "2\n0 0\n2\n0 0\n"),
        ("Interleaved, odd total", "3\n1 4 7\n4\n2 3 5 6\n"),
    ],
    expl=[
        "Combined `1 2 3`: the median is 2.",
        "Combined `1 2 3 4`: (2 + 3) / 2 = 2.5.",
    ],
    prereqs=[
        ("binary_search", "Searching for a valid partition point in the shorter array."),
        ("array_patterns", "Sentinels (±∞) at the array edges remove the boundary cases."),
    ],
)

_p(
    "maximal-rectangle", "Maximal Rectangle", "Hard",
    topics=["Stack", "Dynamic Programming"], subtopics=["Monotonic Stack", "2D DP"], companies=["Google", "Meta", "Amazon"],
    shape="grid", ret="int", todo="build column heights row by row; run Largest Rectangle in Histogram on each row",
    description=(
        "In a grid of `0`s and `1`s, find the **area** of the largest rectangle containing only `1`s.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n### Output\nThe largest area."
    ),
    constraints="1 ≤ r, c ≤ 200",
    hints=[
        "Fix the bottom row of the rectangle. Above each column, how many consecutive 1s are there?",
        "Those counts form a histogram, and the best rectangle with that bottom row is the largest rectangle in the histogram.",
        "Update heights row by row (height + 1 or 0) and run the monotonic-stack histogram algorithm each time.",
    ],
    opt=("O(r·c)", "O(c)", "Each row's histogram is solved in O(c) with a monotonic stack."),
    editorial=(
        "## The one thing this teaches\n**Reduce a 2-D problem to repeated 1-D ones.** Every "
        "rectangle has a bottom row. With the bottom row fixed, the column heights of consecutive "
        "1s above it form a histogram, and Largest Rectangle in Histogram — already solved with a "
        "monotonic stack — gives the best rectangle ending there.\n\n"
        "## Approach\n```java\nint[] h = new int[c];\nint best = 0;\nfor (int i = 0; i < r; i++) {\n"
        "    for (int j = 0; j < c; j++) h[j] = g[i][j] == '1' ? h[j] + 1 : 0;\n"
        "    best = Math.max(best, largestInHistogram(h));\n}\n```\n\n"
        "## Why heights reset to zero\nA 0 in the current row breaks every rectangle through that "
        "column with this bottom row, however tall the column was above it.\n\n"
        "This is why Largest Rectangle in Histogram is worth knowing cold: its main use is as a "
        "subroutine."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    pre = [[0] * (c + 1) for _ in range(r + 1)]
    for i in range(r):
        for j in range(c):
            pre[i + 1][j + 1] = pre[i][j + 1] + pre[i + 1][j] - pre[i][j] + (g[i][j] == "1")
    best = 0
    for i1 in range(r):
        for i2 in range(i1, r):
            for j1 in range(c):
                for j2 in range(j1, c):
                    area = (i2 - i1 + 1) * (j2 - j1 + 1)
                    if area > best:
                        ones = pre[i2 + 1][j2 + 1] - pre[i1][j2 + 1] - pre[i2 + 1][j1] + pre[i1][j1]
                        if ones == area:
                            best = area
    return best
''',
    java='''
    static int largest(int[] h) {
        int n = h.length, best = 0;
        int[] st = new int[n + 1];
        int top = 0;
        for (int i = 0; i <= n; i++) {
            int cur = i == n ? 0 : h[i];
            while (top > 0 && h[st[top - 1]] >= cur) {
                int height = h[st[--top]];
                int left = top == 0 ? -1 : st[top - 1];
                best = Math.max(best, height * (i - left - 1));
            }
            st[top++] = i;
        }
        return best;
    }

    static int solve(char[][] g) {
        int c = g[0].length, best = 0;
        int[] h = new int[c];
        for (char[] row : g) {
            for (int j = 0; j < c; j++) h[j] = row[j] == '1' ? h[j] + 1 : 0;
            best = Math.max(best, largest(h));
        }
        return best;
    }
''',
    examples=[("Example 1", "4 5\n10100\n10111\n11111\n10010\n"), ("Example 2", "1 1\n0\n")],
    hidden=[
        ("Single one", "1 1\n1\n"),
        ("Full block", "2 3\n111\n111\n"),
        ("Bottom block", "3 3\n101\n111\n111\n"),
        ("Tall and thin wins", "4 3\n010\n010\n010\n011\n"),
    ],
    expl=[
        "A 2×3 rectangle of 1s in rows 1–2, columns 2–4: area 6.",
        "No 1s at all.",
    ],
    prereqs=[
        ("stack", "Largest Rectangle in Histogram, run on each row's heights."),
        ("dp2d", "Column heights carried from one row to the next."),
    ],
)

_p(
    "burst-balloons", "Burst Balloons", "Hard",
    topics=["Recursion & DP"], subtopics=["2D DP"], companies=["Google", "Amazon"],
    shape="arr", ret="long", todo="pad with 1s; dp[l][r] = max over the LAST balloon k in (l, r) of dp[l][k] + dp[k][r] + v[l]·v[k]·v[r]",
    description=(
        "Balloons in a row have numbers. Bursting balloon `i` earns `left × num[i] × right`, where "
        "`left` and `right` are its current neighbours (a missing neighbour counts as 1). Burst all "
        "balloons to earn the most coins.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` numbers.\n\n### Output\nThe maximum coins."
    ),
    constraints="1 ≤ n ≤ 300\n0 ≤ num ≤ 100",
    hints=[
        "Choosing the FIRST balloon to burst changes everyone's neighbours — the subproblems interact.",
        "Choose the LAST balloon k to burst in an interval instead: when it bursts, its neighbours are the interval's boundaries.",
        "Pad the array with 1 at both ends. dp[l][r] (exclusive bounds) = max over k of dp[l][k] + dp[k][r] + v[l]·v[k]·v[r].",
    ],
    opt=("O(n³)", "O(n²)", "O(n²) intervals, each trying O(n) last balloons."),
    editorial=(
        "## The one thing this teaches\n**Pick the decision that makes subproblems independent.** "
        "If balloon k is burst first, the balloons on its left and right become neighbours, so the "
        "two sides depend on each other. If k is burst *last* in the open interval (l, r), "
        "everything left of k was burst while k stood as a wall — the two sides never meet.\n\n"
        "## Approach\n```java\nint[] v = new int[n + 2];  v[0] = v[n + 1] = 1;  // copy nums into v[1..n]\n"
        "long[][] dp = new long[n + 2][n + 2];\nfor (int len = 2; len <= n + 1; len++)\n"
        "    for (int l = 0; l + len <= n + 1; l++) {\n        int r = l + len;\n"
        "        for (int k = l + 1; k < r; k++)\n"
        "            dp[l][r] = Math.max(dp[l][r], dp[l][k] + dp[k][r] + (long) v[l] * v[k] * v[r]);\n    }\n"
        "return dp[0][n + 1];\n```\n\n"
        "## Why the boundaries are l and r\nIn the open interval (l, r), balloons l and r are not "
        "burst yet — they are outside it. So when k is the last one inside, its neighbours are "
        "exactly `v[l]` and `v[r]`. The padding 1s make the whole row an interval of the same kind."
    ),
    py='''
def solve(a):
    from functools import lru_cache
    import sys
    sys.setrecursionlimit(10000)
    v = [1] + list(a) + [1]

    @lru_cache(maxsize=None)
    def best(l, r):
        return max((best(l, k) + best(k, r) + v[l] * v[k] * v[r] for k in range(l + 1, r)), default=0)

    return best(0, len(v) - 1)
''',
    java='''
    static long solve(int[] nums) {
        int n = nums.length;
        int[] v = new int[n + 2];
        v[0] = v[n + 1] = 1;
        for (int i = 0; i < n; i++) v[i + 1] = nums[i];
        long[][] dp = new long[n + 2][n + 2];
        for (int len = 2; len <= n + 1; len++)
            for (int l = 0; l + len <= n + 1; l++) {
                int r = l + len;
                for (int k = l + 1; k < r; k++)
                    dp[l][r] = Math.max(dp[l][r], dp[l][k] + dp[k][r] + (long) v[l] * v[k] * v[r]);
            }
        return dp[0][n + 1];
    }
''',
    examples=[("Example 1", "4\n3 1 5 8\n"), ("Example 2", "2\n1 5\n")],
    hidden=[
        ("Single balloon", "1\n7\n"),
        ("All ones", "3\n1 1 1\n"),
        ("Zeros", "3\n0 5 0\n"),
        ("Five balloons", "5\n9 76 64 21 97\n"),
    ],
    expl=[
        "Burst 1, 5, 3, 8 in that order: 15 + 120 + 24 + 8 = 167.",
        "Burst 1 then 5: 5 + 5 = 10.",
    ],
    prereqs=[
        ("dp2d", "An interval table filled by increasing length."),
        ("recursion", "Choosing the last balloon splits an interval into two independent ones."),
    ],
)

_p(
    "regex-matching", "Regular Expression Matching", "Hard",
    topics=["Dynamic Programming", "Strings"], subtopics=["2D DP", "Matching"], companies=["Google", "Meta", "Uber"],
    shape="str2", ret="String", todo="dp[i][j] = s[:i] matches p[:j]; a '*' either matches zero of its char or one more of s",
    description=(
        "Does the pattern `p` match the **entire** string `s`? In the pattern, `.` matches any single "
        "character and `x*` matches zero or more copies of the preceding element `x`.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `p`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s|, |p| ≤ 30\ns has lowercase letters; p has lowercase letters, '.' and '*'.\nEvery '*' follows a letter or '.'.",
    hints=[
        "Let dp[i][j] mean: the first i characters of s match the first j characters of p.",
        "If p[j−1] is a letter or '.', it must match s[i−1] and dp[i−1][j−1] must hold.",
        "If p[j−1] is '*': either use it zero times (dp[i][j−2]), or it matches s[i−1] and dp[i−1][j] holds (one more copy).",
    ],
    opt=("O(|s|·|p|)", "O(|s|·|p|)", "One table cell per pair of prefixes, each O(1)."),
    editorial=(
        "## The one thing this teaches\n**A star is a choice between two smaller problems.** `x*` "
        "either contributes nothing — drop it and its letter from the pattern — or it consumes "
        "one character of `s` and stays available for more. Both options point to smaller "
        "prefixes, which is exactly what a DP table provides.\n\n"
        "## Approach\n```java\nboolean[][] dp = new boolean[n + 1][m + 1];\ndp[0][0] = true;\n"
        "for (int j = 2; j <= m; j++) dp[0][j] = p.charAt(j - 1) == '*' && dp[0][j - 2];   // a*b*c* matches \"\"\n"
        "for (int i = 1; i <= n; i++)\n    for (int j = 1; j <= m; j++) {\n        char pc = p.charAt(j - 1);\n"
        "        if (pc == '*') {\n"
        "            boolean zero = dp[i][j - 2];\n"
        "            boolean more = matches(s.charAt(i - 1), p.charAt(j - 2)) && dp[i - 1][j];\n"
        "            dp[i][j] = zero || more;\n"
        "        } else dp[i][j] = matches(s.charAt(i - 1), pc) && dp[i - 1][j - 1];\n    }\n"
        "return dp[n][m];\n```\n\n"
        "## Why `dp[i − 1][j]` for \"one more\"\nThe star stays at position j: having matched one "
        "character, the same `x*` may match again. Moving to `j − 2` there would allow only one "
        "copy.\n\n"
        "## The first row\nAn empty string matches patterns like `a*b*`, because each starred "
        "element can be used zero times. Initialising `dp[0][j]` is where that is recorded."
    ),
    py='''
def solve(s, t):
    import re
    return "YES" if re.fullmatch(t, s) else "NO"
''',
    java='''
    static boolean matches(char c, char p) {
        return p == '.' || p == c;
    }

    static String solve(String s, String p) {
        int n = s.length(), m = p.length();
        boolean[][] dp = new boolean[n + 1][m + 1];
        dp[0][0] = true;
        for (int j = 2; j <= m; j++) dp[0][j] = p.charAt(j - 1) == '*' && dp[0][j - 2];
        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++) {
                char pc = p.charAt(j - 1);
                if (pc == '*') dp[i][j] = dp[i][j - 2] || (matches(s.charAt(i - 1), p.charAt(j - 2)) && dp[i - 1][j]);
                else dp[i][j] = matches(s.charAt(i - 1), pc) && dp[i - 1][j - 1];
            }
        return dp[n][m] ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "aa\na\n"), ("Example 2", "aa\na*\n")],
    hidden=[
        ("Dot star matches anything", "ab\n.*\n"),
        ("Stars used zero times", "aab\nc*a*b\n"),
        ("Classic miss", "mississippi\nmis*is*p*.\n"),
        ("Trailing requirement", "ab\n.*c\n"),
        ("Star after the end", "a\nab*\n"),
    ],
    expl=[
        "`a` matches only one character.",
        "`a*` matches two `a`s.",
    ],
    prereqs=[
        ("dp2d", "A table over prefixes of the string and the pattern."),
        ("recursion", "A star splits into 'use it zero times' and 'use it once more'."),
    ],
)

_p(
    "critical-connections", "Critical Connections (Bridges)", "Hard",
    topics=["Graphs"], subtopics=["Tree DFS", "Connected Components"], companies=["Amazon", "Google"],
    shape="graph", ret="String", todo="DFS with discovery times and low-links; edge (u, v) is a bridge when low[v] > disc[u]",
    description=(
        "A connected undirected network of `n` servers is given by its edges. An edge is "
        "**critical** if removing it disconnects the network. List every critical edge.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v`.\n\n"
        "### Output\nOne critical edge per line as `u v` with `u < v`, sorted — or `NONE`."
    ),
    constraints="2 ≤ n ≤ 10^4\nn − 1 ≤ m ≤ 10^5\nThe graph is connected, with no repeated edges or self-loops.",
    hints=[
        "Removing each edge and checking connectivity is O(m · (n + m)).",
        "An edge is a bridge exactly when it lies on no cycle.",
        "Tarjan: record each node's DFS discovery time and the lowest discovery time reachable from its subtree using one back edge. Tree edge (u, v) is a bridge if low[v] > disc[u].",
    ],
    opt=("O(n + m)", "O(n + m)", "One DFS computing discovery times and low-links."),
    editorial=(
        "## The one thing this teaches\n**Low-link values detect cycles through a subtree.** In a "
        "DFS tree, a back edge from a descendant to an ancestor closes a cycle. `low[v]` is the "
        "earliest ancestor that `v`'s subtree can reach by such an edge. If even that is not "
        "above `u`, then the tree edge `u–v` is the subtree's only connection upward — a bridge.\n\n"
        "## Approach\n```java\nvoid dfs(int u, int parent) {\n    disc[u] = low[u] = ++time;\n"
        "    for (int v : adj.get(u)) {\n        if (v == parent) continue;\n"
        "        if (disc[v] == 0) {\n            dfs(v, u);\n            low[u] = Math.min(low[u], low[v]);\n"
        "            if (low[v] > disc[u]) bridges.add(new int[]{Math.min(u, v), Math.max(u, v)});\n"
        "        } else low[u] = Math.min(low[u], disc[v]);          // back edge\n    }\n}\n```\n\n"
        "## Skipping the parent\nThe edge back to the parent is the tree edge itself, not a cycle. "
        "Skipping it by vertex works because the graph has no parallel edges; with multi-edges, "
        "skip by edge id instead.\n\n"
        "For 10⁴ nodes the recursion can be deep; an explicit stack avoids stack overflow."
    ),
    py='''
def solve(n, edges):
    def connected(skip):
        adj = [[] for _ in range(n)]
        for idx, (u, v) in enumerate(edges):
            if idx != skip:
                adj[u].append(v)
                adj[v].append(u)
        seen = [False] * n
        seen[0] = True
        st = [0]
        while st:
            u = st.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    st.append(v)
        return all(seen)

    bridges = sorted((min(u, v), max(u, v)) for idx, (u, v) in enumerate(edges) if not connected(idx))
    return "\\n".join(f"{u} {v}" for u, v in bridges) if bridges else "NONE"
''',
    java='''
    static List<List<Integer>> adj;
    static int[] disc, low;
    static int time = 0;
    static List<int[]> bridges = new ArrayList<>();

    static void dfs(int u, int parent) {
        disc[u] = low[u] = ++time;
        for (int v : adj.get(u)) {
            if (v == parent) continue;
            if (disc[v] == 0) {
                dfs(v, u);
                low[u] = Math.min(low[u], low[v]);
                if (low[v] > disc[u]) bridges.add(new int[]{Math.min(u, v), Math.max(u, v)});
            } else low[u] = Math.min(low[u], disc[v]);
        }
    }

    static String solve(int n, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
        disc = new int[n];
        low = new int[n];
        dfs(0, -1);
        if (bridges.isEmpty()) return "NONE";
        bridges.sort((x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);
        StringBuilder sb = new StringBuilder();
        for (int[] b : bridges) { if (sb.length() > 0) sb.append('\\n'); sb.append(b[0]).append(' ').append(b[1]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4 4\n0 1\n1 2\n2 0\n1 3\n"), ("Example 2", "2 1\n0 1\n")],
    hidden=[
        ("A cycle has no bridges", "3 3\n0 1\n1 2\n2 0\n"),
        ("A tail of two bridges", "5 5\n0 1\n1 2\n2 0\n1 3\n3 4\n"),
        ("Two cycles joined by one edge", "6 7\n0 1\n1 2\n2 0\n2 3\n3 4\n4 5\n5 3\n"),
    ],
    expl=[
        "0–1–2 is a cycle; 1–3 is the only way to reach 3.",
        "A single edge is always critical.",
    ],
    prereqs=[
        ("graph_cycle", "An edge is a bridge exactly when no cycle passes through it."),
        ("tree_traversal", "A DFS tree with discovery times and low-link values."),
    ],
)

_p(
    "reverse-bits", "Reverse Bits", "Easy",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation"], companies=["Apple", "Airbnb"],
    shape="n", ret="long", todo="32 times: shift the result left and append the lowest bit of n, then shift n right",
    description=(
        "Reverse the bits of a **32-bit unsigned** integer and print the result as an unsigned "
        "integer.\n\n"
        "### Input\nOne integer `n`, `0 ≤ n < 2^32`.\n\n### Output\nThe value with its 32 bits reversed."
    ),
    constraints="0 ≤ n ≤ 2^32 − 1",
    hints=[
        "Build the answer bit by bit: take the lowest bit of n and push it onto the right of the result.",
        "`result = (result << 1) | (n & 1)`, then `n >>= 1`. Do it exactly 32 times, even if n becomes 0 early.",
        "Java has no unsigned int; read and compute in a long, masking to 32 bits.",
    ],
    opt=("O(1)", "O(1)", "Exactly 32 iterations."),
    editorial=(
        "## The one thing this teaches\n**Moving bits between two numbers.** Reading bits off the "
        "low end of one number and pushing them onto the low end of another reverses their "
        "order — the same trick as reversing the digits of an integer, in base 2.\n\n"
        "## Approach\n```java\nlong result = 0;\nfor (int i = 0; i < 32; i++) {\n"
        "    result = (result << 1) | (n & 1);\n    n >>= 1;\n}\n```\n\n"
        "## Exactly 32\nStopping when `n` reaches 0 loses the leading zeros, and those zeros must "
        "become trailing zeros of the result: reversing `1` gives `2³¹`, not `1`.\n\n"
        "## Unsigned in Java\nWith `int`, the result's top bit is the sign bit, so values ≥ 2³¹ print "
        "as negatives. Keeping everything in a `long` — or using `Integer.toUnsignedString` — "
        "prints them correctly. `Integer.reverse` does the whole job in the library."
    ),
    py='''
def solve(n):
    return int(format(n, "032b")[::-1], 2)
''',
    java='''
    static long solve(long n) {
        long result = 0;
        for (int i = 0; i < 32; i++) {
            result = (result << 1) | (n & 1);
            n >>= 1;
        }
        return result;
    }
''',
    examples=[("Example 1", "43261596\n"), ("Example 2", "4294967293\n")],
    hidden=[
        ("Zero", "0\n"),
        ("Lowest bit becomes highest", "1\n"),
        ("All ones", "4294967295\n"),
        ("Highest bit becomes lowest", "2147483648\n"),
    ],
    expl=[
        "`00000010100101000001111010011100` reversed is `00111001011110000010100101000000` = 964176192.",
        "`11111111111111111111111111111101` reversed is `10111111111111111111111111111111` = 3221225471.",
    ],
    prereqs=[
        ("bit_manip", "Shifting bits out of one number and into another."),
        ("overflow", "Unsigned 32-bit values held in a long so the top bit is not a sign."),
    ],
)

_p(
    "path-sum-iii", "Path Sum III (Count Downward Paths)", "Medium",
    topics=["Trees", "Prefix Sum"], subtopics=["Tree DFS", "Prefix Sum"], companies=["Amazon", "Meta"],
    shape="tree_k", ret="long", todo="DFS carrying a map of prefix sums on the current root path; count prefix = running − k",
    description=(
        "Count the paths that sum to `k`. A path may start and end at **any** nodes, but must go "
        "**downward** (from parent to child).\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child.\n- Line 2: `k`.\n\n"
        "### Output\nThe number of paths."
    ),
    constraints="1 ≤ nodes ≤ 1000\n-10^9 ≤ value ≤ 10^9\n-1000 ≤ k ≤ 1000",
    hints=[
        "Starting a separate sum from every node is O(n²) in the worst case.",
        "Along one root-to-node path, a downward path ending here is a difference of two prefix sums.",
        "It is Subarray Sum Equals K on the current root path: keep a map of prefix-sum counts, and remove the current sum when backtracking.",
    ],
    opt=("O(n)", "O(h)", "One DFS; the map holds the prefix sums of the current path only."),
    editorial=(
        "## The one thing this teaches\n**A root-to-node path is an array.** Subarray Sum Equals K "
        "works on any sequence, and the path from the root to the current node is one. The only "
        "addition is that the sequence changes as the DFS moves, so the prefix map must be undone "
        "when a node is left.\n\n"
        "## Approach\n```java\nMap<Long, Integer> prefix = new HashMap<>();   // starts with {0: 1}\n"
        "long dfs(TreeNode t, long run) {\n    if (t == null) return 0;\n    run += t.val;\n"
        "    long count = prefix.getOrDefault(run - k, 0);\n"
        "    prefix.merge(run, 1, Integer::sum);\n"
        "    count += dfs(t.left, run) + dfs(t.right, run);\n"
        "    prefix.merge(run, -1, Integer::sum);           // backtrack\n    return count;\n}\n```\n\n"
        "## Why backtrack\nWithout removing `run` on the way out, a prefix from one branch would pair "
        "with a node in a sibling branch — a \"path\" that goes up and back down, which the "
        "question forbids.\n\n"
        "Values reach 10⁹ and paths are long: running sums need a `long`."
    ),
    py='''
def solve(root, k):
    count = 0
    stack = [(root, [])]
    while stack:
        t, sums_above = stack.pop()
        sums = [s + t.val for s in sums_above] + [t.val]
        count += sum(1 for s in sums if s == k)
        if t.left:
            stack.append((t.left, sums))
        if t.right:
            stack.append((t.right, sums))
    return count
''',
    java='''
    static Map<Long, Integer> prefix = new HashMap<>();
    static long K;

    static long dfs(TreeNode t, long run) {
        if (t == null) return 0;
        run += t.val;
        long count = prefix.getOrDefault(run - K, 0);
        prefix.merge(run, 1, Integer::sum);
        count += dfs(t.left, run) + dfs(t.right, run);
        prefix.merge(run, -1, Integer::sum);
        return count;
    }

    static long solve(TreeNode root, int k) {
        K = k;
        prefix.put(0L, 1);
        return dfs(root, 0);
    }
''',
    examples=[("Example 1", "10 5 -3 3 2 null 11 3 -2 null 1\n8\n"), ("Example 2", "5 4 8 11 null 13 4 7 2 null null 5 1\n22\n")],
    hidden=[
        ("Single node", "1\n1\n"),
        ("Zero sum", "1 -1 1\n0\n"),
        ("All zeros", "0 0 0\n0\n"),
        ("Large values", "1000000000 1000000000 null -1000000000\n1000000000\n"),
    ],
    expl=[
        "5→3, 5→2→1 and −3→11.",
        "5→4→11→2, 5→8→4→5 and 4→11→7.",
    ],
    prereqs=[
        ("prefix_sum", "Downward paths as differences of prefix sums along the root path."),
        ("backtracking", "Adding a prefix on the way down and removing it on the way back up."),
    ],
)

_p(
    "target-sum", "Target Sum", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP", "Subset Sum"], companies=["Meta", "Google"],
    shape="arr_k", ret="long", todo="the '+' group must sum to (total + target) / 2; count subsets with that sum",
    description=(
        "Put a `+` or `-` sign in front of every number. In how many ways does the resulting "
        "expression equal `target`?\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: `n` non-negative integers.\n\n### Output\nThe number of ways."
    ),
    constraints="1 ≤ n ≤ 20\n0 ≤ a[i] ≤ 1000, sum ≤ 1000\n-1000 ≤ target ≤ 1000",
    hints=[
        "Trying all 2ⁿ sign choices works at n = 20, and there is a better route.",
        "Let P be the sum of the '+' numbers and N the sum of the '−' ones. P − N = target and P + N = total.",
        "So P = (total + target) / 2 — count the subsets summing to P (none if that is negative or not an integer).",
    ],
    opt=("O(n · total)", "O(total)", "A 0/1 knapsack count over sums up to the total."),
    editorial=(
        "## The one thing this teaches\n**Algebra turns a new problem into subset sum.** Assigning "
        "signs is choosing which numbers are positive. Adding the two equations `P − N = target` "
        "and `P + N = total` fixes `P`, and \"how many sign assignments\" becomes \"how many "
        "subsets sum to P\".\n\n"
        "## Approach\n```java\nint total = sum(a);\n"
        "if (Math.abs(target) > total || (total + target) % 2 != 0) return 0;\n"
        "int p = (total + target) / 2;\nlong[] ways = new long[p + 1];\nways[0] = 1;\n"
        "for (int x : a)\n    for (int s = p; s >= x; s--) ways[s] += ways[s - x];   // downward: each number once\nreturn ways[p];\n```\n\n"
        "## Zeros\nA 0 can take either sign without changing the sum, doubling the count. The DP "
        "handles it: with `x = 0`, `ways[s] += ways[s]`.\n\n"
        "## Downward loop\nAs in 0/1 knapsack, iterating `s` downward uses each number at most "
        "once. Upward would let one number be counted repeatedly."
    ),
    py='''
def solve(a, k):
    from itertools import product
    return sum(1 for signs in product((1, -1), repeat=len(a)) if sum(s * x for s, x in zip(signs, a)) == k)
''',
    java='''
    static long solve(int[] a, long target) {
        int total = 0;
        for (int x : a) total += x;
        if (Math.abs(target) > total || (total + target) % 2 != 0) return 0;
        int p = (int) ((total + target) / 2);
        long[] ways = new long[p + 1];
        ways[0] = 1;
        for (int x : a)
            for (int s = p; s >= x; s--) ways[s] += ways[s - x];
        return ways[p];
    }
''',
    examples=[("Example 1", "5 3\n1 1 1 1 1\n"), ("Example 2", "1 1\n1\n")],
    hidden=[
        ("Unreachable parity", "1 2\n1\n"),
        ("Zeros double the count", "3 0\n0 0 0\n"),
        ("Negative target", "4 -2\n1 2 1 2\n"),
        ("Target beyond the total", "3 10\n1 2 3\n"),
    ],
    expl=[
        "Exactly one of the five 1s is negative: five ways.",
        "+1.",
    ],
    prereqs=[
        ("dp", "A 0/1 knapsack count of subsets reaching a sum."),
        ("math_digits", "Solving P − N = target, P + N = total for the positive group."),
    ],
)
