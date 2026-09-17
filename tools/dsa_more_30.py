# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 30 — foundations practice, then grids, design and DP.
#
#   floor-division-and-modulo        Java's / truncates toward zero; floor division rounds down
#   quadrant-of-point                test the special cases (axes, origin) before the general ones
#   strong-number                    sum of digit factorials, with the factorials precomputed
#   even-digit-numbers               count digits by repeated division
#   check-rotated-sorted             a rotated sorted array has at most one descent, counted cyclically
#   max-ascending-subarray-sum       reset the running sum whenever the order breaks
#   nearest-exit-maze                BFS from the entrance; the first border cell reached is closest
#   spiral-matrix-iii                walk segment lengths 1, 1, 2, 2, 3, 3, … and keep the cells inside
#   number-container-system          index → number, plus number → ordered set of indices
#   min-time-visit-cell-grid         Dijkstra where waiting means stepping back and forth (parity)
#   solving-questions-brainpower     DP from the back: skip, or take and jump
#   longest-arith-subseq-difference  dp[value] = 1 + dp[value − difference]
# ===========================================================================

_p(
    "floor-division-and-modulo", "Floor Division and Modulo", "Easy",
    topics=["Math"], subtopics=["Integer Division"], companies=["Google"],
    shape="two", ret="String", todo="q = floor(a / b) and r = a − b·q; Java's / truncates toward zero, so adjust when the signs differ and the division is inexact",
    description=(
        "Print `q r` where `q` is `a / b` **rounded down** (toward negative infinity) and "
        "`r = a − b·q`. The remainder then always has the same sign as `b` (or is 0).\n\n"
        "### Input\nOne line: `a b`.\n\n"
        "### Output\n`q r`."
    ),
    constraints="-10^9 ≤ a ≤ 10^9\n-10^9 ≤ b ≤ 10^9, b ≠ 0",
    hints=[
        "For non-negative a and b every language agrees: 7 / 2 = 3, remainder 1.",
        "With a negative operand, Java's / rounds toward zero: -7 / 2 is -3, not -4.",
        "Floor division differs from truncation only when the signs differ and the division is not exact — then subtract 1 from the truncated quotient. Or use Math.floorDiv and Math.floorMod.",
    ],
    opt=("O(1)", "O(1)", "Two arithmetic operations."),
    editorial=(
        "## The one thing this teaches\n**Integer division has two conventions.** C, C++, Java "
        "and JavaScript truncate toward zero; Python floors toward negative infinity. The "
        "remainder follows the quotient, so `-7 % 2` is `-1` in Java and `1` in Python. Bugs "
        "appear exactly when negatives meet `/` or `%`.\n\n"
        "## Approach\n```java\nlong q = a / b;                               // truncated\n"
        "if ((a % b != 0) && ((a < 0) != (b < 0))) q--;  // signs differ and inexact: round down\n"
        "long r = a - b * q;\n// or simply: Math.floorDiv(a, b), Math.floorMod(a, b)\n```\n\n"
        "## The table\n| a | b | truncate | floor |\n|---|---|---|---|\n"
        "| 7 | 2 | 3 r 1 | 3 r 1 |\n| −7 | 2 | −3 r −1 | −4 r 1 |\n| 7 | −2 | −3 r 1 | −4 r −1 |\n"
        "| −7 | −2 | 3 r −1 | 3 r −1 |\n\n"
        "## Where it matters\nIndexing a circular array with `(i + k) % n` breaks for negative k "
        "in Java. `Math.floorMod(i + k, n)` — or `((i + k) % n + n) % n` — always lands in `0..n−1`."
    ),
    py='''
def solve(x, y):
    q, r = divmod(x, y)
    return f"{q} {r}"
''',
    java='''
    static String solve(long a, long b) {
        long q = a / b;
        if (a % b != 0 && ((a < 0) != (b < 0))) q--;
        long r = a - b * q;
        return q + " " + r;
    }
''',
    examples=[("Example 1", "7 2\n"), ("Example 2", "-7 2\n")],
    hidden=[
        ("Negative divisor", "7 -2\n"),
        ("Both negative", "-7 -2\n"),
        ("Zero dividend", "0 5\n"),
        ("Exact negative", "-6 3\n"),
        ("Large values", "-1000000000 3\n"),
    ],
    expl=[
        "7 = 2 · 3 + 1.",
        "−7 / 2 = −3.5, rounded down to −4; −7 − 2·(−4) = 1.",
    ],
    prereqs=[
        ("modulo", "The remainder operator and its sign conventions."),
        ("overflow", "b · q stays within 64 bits for these inputs."),
    ],
)

_p(
    "quadrant-of-point", "Quadrant of a Point", "Easy",
    topics=["Math"], subtopics=["Conditionals"], companies=["Adobe"],
    shape="two", ret="String", todo="check the origin, then each axis, then decide the quadrant from the two signs",
    description=(
        "Print where the point `(x, y)` lies: `Origin`, `X-axis`, `Y-axis`, or `Quadrant 1` to "
        "`Quadrant 4` (1 is x > 0, y > 0, numbered counter-clockwise).\n\n"
        "### Input\nOne line: `x y`.\n\n"
        "### Output\nThe location."
    ),
    constraints="-10^9 ≤ x, y ≤ 10^9",
    hints=[
        "The quadrant rules use strict inequalities, so points with a zero coordinate need their own answers.",
        "Test x == 0 and y == 0 together first, then each axis alone.",
        "With both coordinates non-zero, the signs decide: (+, +) 1, (−, +) 2, (−, −) 3, (+, −) 4.",
    ],
    opt=("O(1)", "O(1)", "At most a handful of comparisons."),
    editorial=(
        "## The one thing this teaches\n**Boundaries first.** The quadrant branches all assume "
        "both coordinates are non-zero. Handling the zero cases at the top means the later "
        "branches can rely on that without repeating it.\n\n"
        "## Approach\n```java\nif (x == 0 && y == 0) return \"Origin\";\n"
        "if (y == 0) return \"X-axis\";                 // x is non-zero here\n"
        "if (x == 0) return \"Y-axis\";\nif (x > 0) return y > 0 ? \"Quadrant 1\" : \"Quadrant 4\";\n"
        "return y > 0 ? \"Quadrant 2\" : \"Quadrant 3\";\n```\n\n"
        "## Why the order of the axis checks matters less\nOnce the origin is excluded, a point "
        "cannot lie on both axes, so the two axis checks never compete.\n\n"
        "## Counter-clockwise numbering\nQuadrant 2 is upper-left and 4 is lower-right — a common "
        "place to swap numbers by mistake."
    ),
    py='''
def solve(x, y):
    names = {
        (0, 0): "Origin",
        (1, 0): "X-axis", (-1, 0): "X-axis",
        (0, 1): "Y-axis", (0, -1): "Y-axis",
        (1, 1): "Quadrant 1", (-1, 1): "Quadrant 2", (-1, -1): "Quadrant 3", (1, -1): "Quadrant 4",
    }
    sign = lambda v: (v > 0) - (v < 0)
    return names[(sign(x), sign(y))]
''',
    java='''
    static String solve(long x, long y) {
        if (x == 0 && y == 0) return "Origin";
        if (y == 0) return "X-axis";
        if (x == 0) return "Y-axis";
        if (x > 0) return y > 0 ? "Quadrant 1" : "Quadrant 4";
        return y > 0 ? "Quadrant 2" : "Quadrant 3";
    }
''',
    examples=[("Example 1", "3 4\n"), ("Example 2", "-2 0\n")],
    hidden=[
        ("Origin", "0 0\n"),
        ("Negative y-axis", "0 -5\n"),
        ("Third quadrant", "-1 -1\n"),
        ("Fourth quadrant", "5 -9\n"),
        ("Second quadrant", "-3 7\n"),
    ],
    expl=[
        "Both coordinates are positive.",
        "y is 0 and x is not.",
    ],
    prereqs=[
        ("iteration", "An if chain where early returns simplify later conditions."),
        ("math_digits", "Signs of coordinates."),
    ],
)

_p(
    "strong-number", "Strong Number", "Easy",
    topics=["Math"], subtopics=["Digits", "Factorials"], companies=["TCS"],
    shape="n", ret="String", todo="precompute 0! to 9!; sum the factorials of n's digits and compare with n",
    description=(
        "A **strong number** equals the sum of the factorials of its digits — for example "
        "`145 = 1! + 4! + 5!`. Print `YES` if `n` is strong, otherwise `NO`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 10^9",
    hints=[
        "Extract digits with % 10 and / 10.",
        "Recomputing a factorial for every digit repeats work — there are only ten possible digits.",
        "Store 0! … 9! in an array once, then sum fact[digit]. Remember that 0! = 1.",
    ],
    opt=("O(log n)", "O(1)", "One pass over the digits with a 10-entry table."),
    editorial=(
        "## The one thing this teaches\n**Precompute what a small domain allows.** Digits range "
        "over 0–9, so every factorial the loop will ever need fits in a table of ten entries. "
        "Looking one up is cheaper and clearer than a nested loop.\n\n"
        "## Approach\n```java\nlong[] fact = new long[10];\nfact[0] = 1;\n"
        "for (int d = 1; d < 10; d++) fact[d] = fact[d - 1] * d;\n"
        "long sum = 0;\nfor (long v = n; v > 0; v /= 10) sum += fact[(int) (v % 10)];\nreturn sum == n;\n```\n\n"
        "## 0! = 1\nA zero digit contributes 1, not 0. `40585 = 4! + 0! + 5! + 8! + 5!` depends on it.\n\n"
        "## There are only four\nIn base 10 the strong numbers are 1, 2, 145 and 40585. A "
        "10-digit number's digit factorials sum to at most 10 · 9! = 3 628 800, far too small."
    ),
    py='''
def solve(n):
    from math import factorial
    return "YES" if sum(factorial(int(ch)) for ch in str(n)) == n else "NO"
''',
    java='''
    static String solve(long n) {
        long[] fact = new long[10];
        fact[0] = 1;
        for (int d = 1; d < 10; d++) fact[d] = fact[d - 1] * d;
        long sum = 0;
        for (long v = n; v > 0; v /= 10) sum += fact[(int) (v % 10)];
        return sum == n ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "145\n"), ("Example 2", "123\n")],
    hidden=[
        ("One", "1\n"),
        ("Two", "2\n"),
        ("Zero digit counts as one", "40585\n"),
        ("Ten", "10\n"),
        ("Large", "999999999\n"),
    ],
    expl=[
        "1 + 24 + 120 = 145.",
        "1 + 2 + 6 = 9, not 123.",
    ],
    prereqs=[
        ("math_digits", "Extracting digits with % 10 and / 10."),
        ("iteration", "Building a small lookup table before the main loop."),
    ],
)

_p(
    "even-digit-numbers", "Numbers with an Even Number of Digits", "Easy",
    topics=["Arrays", "Math"], subtopics=["Digits"], companies=["Quora"],
    shape="arr", ret="int", todo="for each value, count digits by dividing by 10 until it reaches 0; count the values whose digit count is even",
    description=(
        "Print how many of the positive integers have an **even** number of digits.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` positive integers.\n\n"
        "### Output\nThe count."
    ),
    constraints="1 ≤ n ≤ 500\n1 ≤ a[i] ≤ 10^5",
    hints=[
        "How many digits does a number have? Count how many times you can divide by 10 before reaching 0.",
        "Converting to a string and taking its length also works.",
        "With values at most 10^5, ranges work too: 10–99, 1000–9999 and 100000 are the even-digit ones.",
    ],
    opt=("O(n · log max)", "O(1)", "At most six divisions per value."),
    editorial=(
        "## The one thing this teaches\n**A loop inside a loop is fine when the inner one is "
        "tiny.** The digit count of a number up to 10^5 takes at most six steps, so the whole "
        "scan is effectively linear.\n\n"
        "## Approach\n```java\nint count = 0;\nfor (int x : a) {\n    int digits = 0;\n"
        "    for (int v = x; v > 0; v /= 10) digits++;\n    if (digits % 2 == 0) count++;\n}\n```\n\n"
        "## Three ways to count digits\n- repeated division, as above;\n"
        "- `String.valueOf(x).length()`;\n- `(int) Math.log10(x) + 1` — fine for positive values, "
        "but floating-point logarithms can be off by one at exact powers of ten on some "
        "platforms, so integer methods are safer."
    ),
    py='''
def solve(a):
    return sum(1 for x in a if len(str(x)) % 2 == 0)
''',
    java='''
    static int solve(int[] a) {
        int count = 0;
        for (int x : a) {
            int digits = 0;
            for (int v = x; v > 0; v /= 10) digits++;
            if (digits % 2 == 0) count++;
        }
        return count;
    }
''',
    examples=[("Example 1", "5\n12 345 2 6 7896\n"), ("Example 2", "4\n555 901 482 1771\n")],
    hidden=[
        ("Six digits", "1\n100000\n"),
        ("Boundaries", "4\n9 10 99 100\n"),
        ("None", "3\n1 123 12345\n"),
    ],
    expl=[
        "12 (2 digits) and 7896 (4 digits).",
        "Only 1771 has an even number of digits.",
    ],
    prereqs=[
        ("math_digits", "Counting digits by repeated division."),
        ("iteration", "A short inner loop inside a scan."),
    ],
)

_p(
    "check-rotated-sorted", "Check if Array Is Sorted and Rotated", "Easy",
    topics=["Arrays"], subtopics=["Traversal", "Circular Index"], companies=["Amazon", "SoundHound"],
    shape="arr", ret="String", todo="count positions i with a[i] > a[(i + 1) % n]; a rotated non-decreasing array has at most one",
    description=(
        "Was this array obtained by rotating a **non-decreasing** array by some number of "
        "positions (possibly zero)? Print `YES` or `NO`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 100\n1 ≤ a[i] ≤ 100",
    hints=[
        "Trying every rotation and checking whether it is sorted is O(n²).",
        "A sorted array has no place where a value is followed by a smaller one. Rotating it creates exactly one such place — at the seam.",
        "Count descents a[i] > a[i + 1], including the wrap-around pair (last, first). At most one means YES.",
    ],
    opt=("O(n)", "O(1)", "One pass with a circular index."),
    editorial=(
        "## The one thing this teaches\n**Characterise the shape instead of searching for it.** "
        "Rather than finding the rotation, describe what any rotation looks like: a single "
        "\"drop\" when the array is read in a circle. Counting drops is one pass.\n\n"
        "## Approach\n```java\nint drops = 0;\nfor (int i = 0; i < n; i++)\n"
        "    if (a[i] > a[(i + 1) % n]) drops++;\nreturn drops <= 1;\n```\n\n"
        "## Why the wrap-around pair is needed\n`2 1 3 4` has one internal drop (2 > 1), but "
        "reading on from 4 back to 2 is fine only if 4 ≤ 2 — it is not, so there is a second "
        "drop and the answer is `NO`.\n\n"
        "## Zero rotation\nAn already sorted array has no internal drop and one at the wrap "
        "(last > first), unless all values are equal — either way at most one."
    ),
    py='''
def solve(a):
    target = sorted(a)
    return "YES" if any(a[i:] + a[:i] == target for i in range(len(a))) else "NO"
''',
    java='''
    static String solve(int[] a) {
        int n = a.length, drops = 0;
        for (int i = 0; i < n; i++) if (a[i] > a[(i + 1) % n]) drops++;
        return drops <= 1 ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "5\n3 4 5 1 2\n"), ("Example 2", "4\n2 1 3 4\n"), ("Example 3", "3\n1 2 3\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All equal", "4\n1 1 1 1\n"),
        ("Rotation with duplicates", "5\n2 2 1 2 2\n"),
        ("Descending", "3\n3 2 1\n"),
    ],
    expl=[
        "1 2 3 4 5 rotated by three positions.",
        "Two drops: 2 > 1 and, wrapping around, 4 > 2.",
        "Rotated by zero positions.",
    ],
    prereqs=[
        ("array_patterns", "Comparing neighbours, including the wrap-around pair."),
        ("modulo", "A circular index with (i + 1) % n."),
    ],
)

_p(
    "max-ascending-subarray-sum", "Maximum Ascending Subarray Sum", "Easy",
    topics=["Arrays"], subtopics=["Running Sum"], companies=["Amazon"],
    shape="arr", ret="long", todo="keep the sum of the current strictly increasing run; restart it at a[i] when a[i] ≤ a[i − 1]",
    description=(
        "A subarray is **ascending** if every element is strictly larger than the one before it. "
        "Print the largest sum of an ascending subarray (a single element counts).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` positive integers.\n\n"
        "### Output\nThe maximum sum."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^9",
    hints=[
        "Checking every subarray is O(n²).",
        "Ascending runs do not overlap: each element either continues the current run or starts a new one.",
        "Carry the current run's sum; reset it to a[i] when a[i] ≤ a[i − 1]. Values are positive, so extending a run always increases its sum.",
    ],
    opt=("O(n)", "O(1)", "One pass with a running sum."),
    editorial=(
        "## The one thing this teaches\n**Split the array where the condition breaks.** Maximal "
        "ascending runs partition the array, and because every value is positive, the best "
        "ascending subarray is always a whole run.\n\n"
        "## Approach\n```java\nlong run = a[0], best = a[0];\nfor (int i = 1; i < n; i++) {\n"
        "    run = a[i] > a[i - 1] ? run + a[i] : a[i];\n    best = Math.max(best, run);\n}\n```\n\n"
        "## Strictly increasing\n`5 5 5` has three runs of length 1: equal neighbours break "
        "the run.\n\n"
        "## Use long\nA run of 10^5 values near 10^9 reaches 10^14."
    ),
    py='''
def solve(a):
    best = 0
    for i in range(len(a)):
        s = a[i]
        best = max(best, s)
        j = i + 1
        while j < len(a) and a[j] > a[j - 1]:
            s += a[j]
            best = max(best, s)
            j += 1
    return best
''',
    java='''
    static long solve(int[] a) {
        long run = a[0], best = a[0];
        for (int i = 1; i < a.length; i++) {
            run = a[i] > a[i - 1] ? run + a[i] : a[i];
            best = Math.max(best, run);
        }
        return best;
    }
''',
    examples=[
        ("Example 1", "6\n10 20 30 5 10 50\n"),
        ("Example 2", "5\n10 20 30 40 50\n"),
        ("Example 3", "7\n12 17 15 13 10 11 12\n"),
    ],
    hidden=[
        ("Single element", "1\n5\n"),
        ("Equal values", "3\n5 5 5\n"),
        ("Large values", "3\n999999998 999999999 1000000000\n"),
        ("Short run wins", "5\n1 2 3 100 1\n"),
    ],
    expl=[
        "5 + 10 + 50 = 65 beats 10 + 20 + 30 = 60.",
        "The whole array is ascending.",
        "10 + 11 + 12 = 33.",
    ],
    prereqs=[
        ("array_patterns", "A running value that resets when a condition breaks."),
        ("overflow", "Sums up to 10^14."),
    ],
)

_p(
    "nearest-exit-maze", "Nearest Exit from Entrance in Maze", "Medium",
    topics=["Graphs", "BFS", "Matrix"], subtopics=["Grid BFS"], companies=["Amazon", "Meta"],
    shape="grid", ret="int", todo="BFS from the entrance over open cells; the first dequeued border cell other than the entrance is the answer",
    description=(
        "A maze has open cells `.`, walls `+` and one entrance `E` (itself open). An **exit** is "
        "an open cell on the border of the maze, other than the entrance. Moving up, down, left "
        "or right, print the fewest steps from the entrance to an exit, or `-1`.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: the maze.\n\n"
        "### Output\nThe fewest steps, or `-1`."
    ),
    constraints="1 ≤ r, c ≤ 100",
    hints=[
        "Every step costs the same, so BFS finds the nearest exit.",
        "Mark cells visited when they are enqueued, starting with the entrance.",
        "When dequeuing a cell, check whether it is on the border and not the entrance — the first such cell is the answer.",
    ],
    opt=("O(r · c)", "O(r · c)", "Each cell is enqueued at most once."),
    editorial=(
        "## The one thing this teaches\n**BFS order is distance order.** Cells come out of the "
        "queue in non-decreasing distance, so the first exit dequeued is a nearest one — there "
        "is no need to explore the rest of the maze.\n\n"
        "## Approach\n```java\nqueue.add(entrance); seen[entrance] = true; dist[entrance] = 0;\n"
        "while (!queue.isEmpty()) {\n    cell = queue.poll();\n"
        "    if (cell != entrance && onBorder(cell)) return dist[cell];\n"
        "    for (each open, unseen neighbour) { seen = true; dist = dist[cell] + 1; queue.add(neighbour); }\n}\nreturn -1;\n```\n\n"
        "## The entrance on the border\nThe entrance may itself be a border cell, but it does not "
        "count as an exit — hence the explicit `cell != entrance` check.\n\n"
        "## Checking at enqueue time\nTesting for an exit when a neighbour is *enqueued* returns "
        "one level earlier and is equally correct; checking at dequeue time is simpler to get "
        "right."
    ),
    py='''
def solve(g):
    from collections import deque
    r, c = len(g), len(g[0])
    dist = {}
    q = deque()
    for i in range(r):
        for j in range(c):
            if g[i][j] == "." and (i in (0, r - 1) or j in (0, c - 1)):
                dist[(i, j)] = 0
                q.append((i, j))
    while q:
        i, j = q.popleft()
        for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= a < r and 0 <= b < c and g[a][b] != "+" and (a, b) not in dist:
                dist[(a, b)] = dist[(i, j)] + 1
                if g[a][b] == "E":
                    return dist[(a, b)]
                q.append((a, b))
    return -1
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length, si = 0, sj = 0;
        for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) if (g[i][j] == 'E') { si = i; sj = j; }
        int[][] dist = new int[r][c];
        for (int[] row : dist) Arrays.fill(row, -1);
        ArrayDeque<int[]> q = new ArrayDeque<>();
        dist[si][sj] = 0;
        q.add(new int[]{si, sj});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!q.isEmpty()) {
            int[] cur = q.poll();
            int i = cur[0], j = cur[1];
            boolean border = i == 0 || j == 0 || i == r - 1 || j == c - 1;
            if (border && !(i == si && j == sj)) return dist[i][j];
            for (int[] d : dirs) {
                int a = i + d[0], b = j + d[1];
                if (a < 0 || b < 0 || a >= r || b >= c || g[a][b] == '+' || dist[a][b] != -1) continue;
                dist[a][b] = dist[i][j] + 1;
                q.add(new int[]{a, b});
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", "3 4\n++.+\n..E+\n+++.\n"),
        ("Example 2", "3 3\n+++\nE..\n+++\n"),
        ("Example 3", "1 2\nE+\n"),
    ],
    hidden=[
        ("Entrance only open cell", "3 3\n+++\n+E+\n+++\n"),
        ("Exit next to entrance", "2 2\nE.\n++\n"),
        ("Long corridor", "5 5\n+++++\n+E..+\n+++.+\n+...+\n+.+++\n"),
        ("Walled in", "4 4\n....\n.++.\n.+E+\n.+++\n"),
    ],
    expl=[
        "One step up from the entrance reaches the open border cell above it.",
        "The entrance is on the border but does not count; the exit at the right end is 2 steps away.",
        "The only other cell is a wall.",
    ],
    prereqs=[
        ("bfs", "Breadth-first search, where dequeue order is distance order."),
        ("grid", "Border detection and four-directional moves."),
    ],
)

_p(
    "spiral-matrix-iii", "Spiral Matrix III", "Medium",
    topics=["Simulation", "Matrix"], subtopics=["Spiral Walk"], companies=["Google"],
    shape="arr", ret="String", todo="walk east, south, west, north with segment lengths 1, 1, 2, 2, 3, 3, …; record positions inside the grid until all are seen",
    description=(
        "Start at `(rStart, cStart)` in a grid with `rows` rows and `cols` columns, facing east. "
        "Walk in a clockwise spiral — even outside the grid — and record each grid cell the "
        "first time the walk visits it, until every cell is recorded.\n\n"
        "### Input\n- Line 1: `4`.\n- Line 2: `rows cols rStart cStart`.\n\n"
        "### Output\nOne line per cell, `r c`, in visiting order."
    ),
    constraints="1 ≤ rows, cols ≤ 100\n0 ≤ rStart < rows, 0 ≤ cStart < cols",
    hints=[
        "Spiral segments grow in a pattern: 1 east, 1 south, 2 west, 2 north, 3 east, 3 south, …",
        "Each length is used for two directions, then increases by one.",
        "Walk step by step, even outside the grid; record a position only if it lies inside. Stop when rows · cols cells are recorded.",
    ],
    opt=("O(max(rows, cols)²)", "O(rows · cols)", "The spiral must grow until it covers the whole grid; the output holds every cell."),
    editorial=(
        "## The one thing this teaches\n**Simulate the simple infinite process and filter.** "
        "Clipping the spiral against the grid edges case by case is fiddly. Walking the ideal "
        "spiral and ignoring out-of-bounds positions is short and obviously correct.\n\n"
        "## Approach\n```java\nint[][] dirs = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};   // E, S, W, N\n"
        "record(r, c);\nint d = 0, len = 1;\nwhile (recorded < rows * cols) {\n"
        "    for (int turn = 0; turn < 2; turn++) {            // two directions per length\n"
        "        for (int s = 0; s < len; s++) {\n            r += dirs[d][0]; c += dirs[d][1];\n"
        "            if (inside(r, c)) record(r, c);\n        }\n        d = (d + 1) % 4;\n    }\n    len++;\n}\n```\n\n"
        "## Why each cell is recorded once\nThe spiral never revisits a position: each ring lies "
        "strictly outside the previous one.\n\n"
        "## Stopping mid-segment\nThe loop may finish a segment after the last cell is recorded; "
        "those extra steps are all outside the grid and record nothing."
    ),
    py='''
def solve(a):
    rows, cols, r, c = a
    seen = [(r, c)]
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    length, d = 1, 0
    while len(seen) < rows * cols:
        for _ in range(2):
            dr, dc = moves[d]
            for _ in range(length):
                r, c = r + dr, c + dc
                if 0 <= r < rows and 0 <= c < cols:
                    seen.append((r, c))
            d = (d + 1) % 4
        length += 1
    return "\\n".join(f"{x} {y}" for x, y in seen[:rows * cols])
''',
    java='''
    static String solve(int[] a) {
        int rows = a[0], cols = a[1], r = a[2], c = a[3];
        int[][] dirs = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        StringBuilder sb = new StringBuilder();
        sb.append(r).append(' ').append(c);
        int recorded = 1, d = 0, len = 1;
        while (recorded < rows * cols) {
            for (int turn = 0; turn < 2; turn++) {
                for (int s = 0; s < len; s++) {
                    r += dirs[d][0];
                    c += dirs[d][1];
                    if (r >= 0 && c >= 0 && r < rows && c < cols) {
                        sb.append('\\n').append(r).append(' ').append(c);
                        recorded++;
                    }
                }
                d = (d + 1) % 4;
            }
            len++;
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4\n1 4 0 0\n"), ("Example 2", "4\n5 6 1 4\n")],
    hidden=[
        ("Single cell", "4\n1 1 0 0\n"),
        ("Start in a corner", "4\n3 3 2 2\n"),
        ("Tall grid", "4\n4 1 1 0\n"),
        ("Centre of a square", "4\n3 3 1 1\n"),
    ],
    expl=[
        "Walking east from (0, 0) covers the whole single row; the rest of the spiral lies outside.",
        "The spiral starts at (1, 4), goes east to (1, 5), south to (2, 5), west through (2, 4) and (2, 3), and keeps growing.",
    ],
    prereqs=[
        ("simulation", "Walking a path with direction changes and a growing segment length."),
        ("grid", "Bounds checks that filter positions outside the grid."),
    ],
)

_p(
    "number-container-system", "Design a Number Container System", "Medium",
    topics=["Design", "Hashing", "Heaps"], subtopics=["Two Maps", "Ordered Set"], companies=["Google", "Amazon"],
    shape="ops", ret="String", todo="map index → number; map number → ordered set of indices; on change, remove the index from the old number's set",
    description=(
        "Maintain containers at integer indices, each holding one number:\n\n"
        "- `change index number` — put `number` at `index`, replacing what was there;\n"
        "- `find number` — print the **smallest index** currently holding `number`, or `-1`.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: the operations.\n\n"
        "### Output\nOne line per `find`."
    ),
    constraints="1 ≤ q ≤ 10^5\n1 ≤ index, number ≤ 10^9",
    hints=[
        "A map from index to number handles change. Scanning it for find is O(n) per query.",
        "Also keep, for each number, the set of indices holding it — ordered, so the smallest is at hand.",
        "On change, remove the index from its old number's set before adding it to the new one. A TreeSet's first() answers find.",
    ],
    opt=("O(log n) per operation", "O(n)", "Two hash maps, one of them holding ordered sets."),
    editorial=(
        "## The one thing this teaches\n**Maintain the reverse index, and keep both directions "
        "consistent.** Queries go from number to indices, updates from index to number. Two "
        "maps serve both — but every update must fix both, including the entry the old value "
        "leaves behind.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> at = new HashMap<>();\n"
        "Map<Integer, TreeSet<Integer>> where = new HashMap<>();\n\n"
        "void change(int index, int number) {\n    Integer old = at.put(index, number);\n"
        "    if (old != null) where.get(old).remove(index);            // stale entry\n"
        "    where.computeIfAbsent(number, k -> new TreeSet<>()).add(index);\n}\n\n"
        "int find(int number) {\n    TreeSet<Integer> s = where.get(number);\n"
        "    return s == null || s.isEmpty() ? -1 : s.first();\n}\n```\n\n"
        "## The heap alternative\nA min-heap per number with **lazy deletion** also works: on "
        "find, pop indices whose current number (checked in `at`) no longer matches. Cheaper "
        "updates, occasionally slower queries.\n\n"
        "## Same number again\n`change 1 10` twice removes index 1 from 10's set and adds it back "
        "— harmless."
    ),
    py='''
def solve(ops):
    at = {}
    out = []
    for op in ops:
        if op[0] == "change":
            at[int(op[1])] = int(op[2])
        else:
            number = int(op[1])
            holders = [i for i, v in at.items() if v == number]
            out.append(str(min(holders)) if holders else "-1")
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        HashMap<Integer, Integer> at = new HashMap<>();
        HashMap<Integer, TreeSet<Integer>> where = new HashMap<>();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("change")) {
                int index = Integer.parseInt(op[1]), number = Integer.parseInt(op[2]);
                Integer old = at.put(index, number);
                if (old != null) where.get(old).remove(index);
                where.computeIfAbsent(number, k -> new TreeSet<>()).add(index);
            } else {
                TreeSet<Integer> s = where.get(Integer.parseInt(op[1]));
                if (sb.length() > 0) sb.append('\\n');
                sb.append(s == null || s.isEmpty() ? -1 : s.first());
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "8\nfind 10\nchange 2 10\nchange 1 10\nchange 3 10\nchange 5 10\nfind 10\nchange 1 20\nfind 10\n"),
    ],
    hidden=[
        ("Overwrite with the same number", "3\nchange 1 7\nchange 1 7\nfind 7\n"),
        ("Last holder leaves", "4\nchange 4 9\nchange 4 8\nfind 9\nfind 8\n"),
        ("Large indices", "4\nchange 1000000000 5\nchange 999999999 5\nfind 5\nfind 6\n"),
        ("Move back", "5\nchange 3 1\nchange 2 2\nchange 2 1\nchange 3 2\nfind 1\n"),
    ],
    expl=[
        "No container holds 10 at first. After four changes the smallest index with 10 is 1; once index 1 holds 20, it is 2.",
    ],
    prereqs=[
        ("design_ds", "Two maps kept consistent across updates."),
        ("bst", "An ordered set whose first element is the smallest index."),
    ],
)

_p(
    "min-time-visit-cell-grid", "Minimum Time to Visit a Cell in a Grid", "Hard",
    topics=["Graphs", "Shortest Paths", "Heaps"], subtopics=["Dijkstra", "Parity"], companies=["Atlassian", "Google"],
    shape="matrix", ret="long", todo="Dijkstra on arrival time; if a cell opens later, arrive at grid[i][j] or grid[i][j] + 1 so the parity matches the back-and-forth wait",
    description=(
        "You start at the top-left cell at time 0. Each second you **must** move to an adjacent "
        "cell (up, down, left or right). You may enter cell `(i, j)` only at a time of at least "
        "`grid[i][j]`. Print the minimum time to reach the bottom-right cell, or `-1` if it is "
        "impossible.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers each (`grid[0][0]` is 0).\n\n"
        "### Output\nThe minimum time, or `-1`."
    ),
    constraints="2 ≤ r · c\n1 ≤ r, c ≤ 1000, r · c ≤ 10^5\n0 ≤ grid[i][j] ≤ 10^5",
    hints=[
        "You cannot stand still, but you can wait by stepping back and forth between two cells — each round trip costs 2 seconds.",
        "If both neighbours of the start open after time 1, you can never make a first move: the answer is −1. Otherwise waiting is always possible.",
        "Run Dijkstra on time. From time t, a neighbour is reached at t + 1 if that is ≥ its opening time; otherwise at its opening time, plus 1 if the parity differs (back-and-forth moves change time by 2).",
    ],
    opt=("O(r·c · log(r·c))", "O(r·c)", "Dijkstra over grid cells with four edges each."),
    editorial=(
        "## The one thing this teaches\n**Model waiting precisely, including its parity.** The "
        "no-waiting rule looks like it breaks shortest paths, but bouncing between two cells "
        "wastes exactly 2 seconds per round. So a late cell can be entered at its opening time "
        "if the parity works out, or one second later if not.\n\n"
        "## Approach\n```java\nif (grid[0][1] > 1 && grid[1][0] > 1) return -1;   // stuck at the start\n"
        "dist[0][0] = 0; pq.add({0, 0, 0});\nwhile (!pq.isEmpty()) {\n    {t, i, j} = pq.poll();\n"
        "    if (t > dist[i][j]) continue;\n    if (i == r - 1 && j == c - 1) return t;\n"
        "    for (neighbour (a, b)) {\n        long arrive = t + 1;\n        if (arrive < grid[a][b]) {\n"
        "            long wait = grid[a][b] - arrive;\n            arrive = grid[a][b] + (wait % 2);   // bounce, fixing parity\n        }\n"
        "        if (arrive < dist[a][b]) { dist[a][b] = arrive; pq.add({arrive, a, b}); }\n    }\n}\n```\n\n"
        "## Why the start check is enough\nAfter the first move there is always a previous cell "
        "to bounce back to, so every later cell is eventually reachable.\n\n"
        "## Why +1 on a parity mismatch\nEvery move changes time by 1 and the grid is bipartite, "
        "so the time you can stand on a given cell always has a fixed parity from any fixed "
        "starting time. A bounce keeps parity; only the extra second fixes a mismatch."
    ),
    py='''
def solve(m):
    from collections import deque
    r, c = len(m), len(m[0])
    limit = max(max(row) for row in m) + 2 * r * c + 4
    seen = {(0, 0, 0)}
    q = deque([(0, 0, 0)])
    while q:
        i, j, t = q.popleft()
        if (i, j) == (r - 1, c - 1):
            return t
        if t + 1 > limit:
            continue
        for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= a < r and 0 <= b < c and m[a][b] <= t + 1 and (a, b, t + 1) not in seen:
                seen.add((a, b, t + 1))
                q.append((a, b, t + 1))
    return -1
''',
    java='''
    static long solve(int[][] g) {
        int r = g.length, c = g[0].length;
        boolean canRight = c > 1 && g[0][1] <= 1, canDown = r > 1 && g[1][0] <= 1;
        if (!canRight && !canDown) return -1;
        long[][] dist = new long[r][c];
        for (long[] row : dist) Arrays.fill(row, Long.MAX_VALUE);
        dist[0][0] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
        pq.add(new long[]{0, 0, 0});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            long t = cur[0];
            int i = (int) cur[1], j = (int) cur[2];
            if (t > dist[i][j]) continue;
            if (i == r - 1 && j == c - 1) return t;
            for (int[] d : dirs) {
                int a = i + d[0], b = j + d[1];
                if (a < 0 || b < 0 || a >= r || b >= c) continue;
                long arrive = t + 1;
                if (arrive < g[a][b]) arrive = g[a][b] + ((g[a][b] - arrive) % 2);
                if (arrive < dist[a][b]) { dist[a][b] = arrive; pq.add(new long[]{arrive, a, b}); }
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", "3 4\n0 1 3 2\n5 1 2 5\n4 3 8 6\n"),
        ("Example 2", "3 3\n0 2 4\n3 2 1\n1 0 4\n"),
    ],
    hidden=[
        ("Two cells", "1 2\n0 1\n"),
        ("Two cells, closed", "1 2\n0 5\n"),
        ("Bounce with parity fix", "2 2\n0 1\n5 5\n"),
        ("Straight path", "2 3\n0 1 99\n1 1 1\n"),
        ("Long wait at the end", "3 3\n0 1 1\n9 9 9\n9 9 20\n"),
    ],
    expl=[
        "One optimal route: (0,0) → (0,1) at 1 → (1,1) at 2 → (1,2) at 3 → (0,2) at 4 → (1,2) at 5 → (1,3) at 6 → (2,3) at 7.",
        "Both neighbours of the start open after time 1, so no first move is possible.",
    ],
    prereqs=[
        ("dijkstra", "Dijkstra where the edge cost depends on the arrival time."),
        ("modulo", "Parity of waiting time when every move changes time by one."),
    ],
)

_p(
    "solving-questions-brainpower", "Solving Questions With Brainpower", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP", "Take or Skip"], companies=["Google", "Amazon"],
    shape="pairs", ret="long", todo="dp[i] = max(dp[i + 1], points[i] + dp[i + brainpower[i] + 1]), filled from the last question backwards",
    description=(
        "Questions must be handled in order. For question `i` you either **solve** it — earning "
        "`points` and being unable to solve the next `brainpower` questions — or **skip** it. "
        "Print the maximum total points.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `points brainpower`.\n\n"
        "### Output\nThe maximum points."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ points, brainpower ≤ 10^5",
    hints=[
        "Deciding greedily fails: a big question may block several bigger ones.",
        "The best you can do from question i onward does not depend on what happened before i.",
        "Fill dp from the back: dp[i] = max(skip → dp[i + 1], solve → points + dp[i + brainpower + 1]), treating indices past the end as 0.",
    ],
    opt=("O(n)", "O(n)", "One table entry per question."),
    editorial=(
        "## The one thing this teaches\n**Go backwards when a choice jumps forward.** Solving "
        "question i affects which questions come *after* it. Defining the state as \"best from i "
        "onward\" makes that jump a lookup into an already-computed entry.\n\n"
        "## Approach\n```java\nlong[] dp = new long[n + 1];\nfor (int i = n - 1; i >= 0; i--) {\n"
        "    int next = Math.min(n, i + q[i][1] + 1);\n"
        "    dp[i] = Math.max(dp[i + 1], q[i][0] + dp[next]);\n}\nreturn dp[0];\n```\n\n"
        "## Why forwards is awkward\nA forward state \"best total having reached i\" would need "
        "to know which earlier solved question still blocks i. The backward state never needs "
        "the past.\n\n"
        "## Walkthrough (Example 1)\nQuestions `(3,2) (4,3) (4,4) (2,5)`: dp from the back is "
        "2, 4, 4, 5. Solving question 0 skips 1 and 2 and then takes question 3: 3 + 2 = 5."
    ),
    py='''
def solve(p):
    import sys
    from functools import lru_cache
    sys.setrecursionlimit(10000)

    @lru_cache(maxsize=None)
    def best(i):
        if i >= len(p):
            return 0
        points, brain = p[i]
        return max(best(i + 1), points + best(i + brain + 1))

    return best(0)
''',
    java='''
    static long solve(int[][] q) {
        int n = q.length;
        long[] dp = new long[n + 1];
        for (int i = n - 1; i >= 0; i--) {
            int next = (int) Math.min(n, (long) i + q[i][1] + 1);
            dp[i] = Math.max(dp[i + 1], q[i][0] + dp[next]);
        }
        return dp[0];
    }
''',
    examples=[
        ("Example 1", "4\n3 2\n4 3\n4 4\n2 5\n"),
        ("Example 2", "5\n1 1\n2 2\n3 3\n4 4\n5 5\n"),
    ],
    hidden=[
        ("Single question", "1\n10 5\n"),
        ("Blocker is worth it", "3\n100 2\n60 1\n60 1\n"),
        ("Skip the first", "4\n5 3\n4 1\n4 1\n4 1\n"),
        ("Eight questions", "8\n21 5\n92 3\n74 2\n39 4\n58 2\n5 5\n49 4\n65 3\n"),
    ],
    expl=[
        "Solve questions 0 and 3: 3 + 2 = 5.",
        "Solve questions 1 and 4: 2 + 5 = 7.",
    ],
    prereqs=[
        ("dp", "A suffix DP where taking an item jumps ahead in the table."),
        ("recurrence", "Take-or-skip transitions."),
    ],
)

_p(
    "longest-arith-subseq-difference", "Longest Arithmetic Subsequence of Given Difference", "Medium",
    topics=["Dynamic Programming", "Hashing"], subtopics=["DP over Values"], companies=["Google"],
    shape="arr_k", ret="int", todo="scan left to right; best[x] = best[x − difference] + 1, stored in a hash map keyed by value",
    description=(
        "Print the length of the longest subsequence in which each element minus the previous "
        "one equals `difference`.\n\n"
        "### Input\n- Line 1: `n difference`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe longest length."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^4 ≤ a[i], difference ≤ 10^4",
    hints=[
        "The O(n²) DP compares every earlier element with the current one.",
        "With the difference fixed, the only useful predecessor of x has value x − difference. Its position does not matter, as long as it came earlier.",
        "Keep a map from value to the longest valid subsequence ending with that value so far. Process left to right: best[x] = best.get(x − difference, 0) + 1.",
    ],
    opt=("O(n)", "O(n)", "One hash lookup and update per element."),
    editorial=(
        "## The one thing this teaches\n**Key the DP by value when the transition names a "
        "value.** Longest Increasing Subsequence must consider every smaller earlier element. "
        "Here the predecessor is fully determined — `x − difference` — so one map lookup "
        "replaces the inner loop.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> best = new HashMap<>();\nint answer = 0;\n"
        "for (int x : a) {\n    int len = best.getOrDefault(x - difference, 0) + 1;\n"
        "    best.put(x, len);          // later copies of x overwrite with a length at least as long\n"
        "    answer = Math.max(answer, len);\n}\n```\n\n"
        "## Why overwriting is safe\nA later occurrence of `x` sees every earlier element, so its "
        "length is never shorter than an earlier occurrence's.\n\n"
        "## Difference 0\nThen `x − difference = x` and the map counts occurrences of each value "
        "— the longest subsequence of equal elements."
    ),
    py='''
def solve(a, k):
    n = len(a)
    best = [1] * n
    for i in range(n):
        for j in range(i):
            if a[i] - a[j] == k:
                best[i] = max(best[i], best[j] + 1)
    return max(best)
''',
    java='''
    static int solve(int[] a, long diff) {
        HashMap<Long, Integer> best = new HashMap<>();
        int answer = 0;
        for (int x : a) {
            int len = best.getOrDefault(x - diff, 0) + 1;
            best.put((long) x, len);
            answer = Math.max(answer, len);
        }
        return answer;
    }
''',
    examples=[
        ("Example 1", "4 1\n1 2 3 4\n"),
        ("Example 2", "4 1\n1 3 5 7\n"),
        ("Example 3", "9 -2\n1 5 7 8 5 3 4 2 1\n"),
    ],
    hidden=[
        ("Single element", "1 0\n5\n"),
        ("Zero difference", "5 0\n2 2 3 2 2\n"),
        ("Order matters", "4 1\n4 3 2 1\n"),
        ("Negative values", "6 3\n-6 -3 0 -3 3 6\n"),
    ],
    expl=[
        "The whole array.",
        "No two elements differ by exactly 1.",
        "7, 5, 3, 1.",
    ],
    prereqs=[
        ("dp", "A DP whose state is keyed by value rather than index."),
        ("hashing", "Looking up the one predecessor value in a map."),
    ],
)
