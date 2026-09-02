# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 5 — Prefix sums, two pointers, sliding window.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# The three patterns that turn an O(n^2) array answer into an O(n) one. All
# three are "precompute or maintain something as you walk, instead of
# recomputing it", and the module says that out loud rather than presenting
# them as three unrelated tricks.
#
# This closes Part 1 of the roadmap. Everything here composes module 1's
# traversal, module 3's sorted-array reasoning and module 4's two pointers.
# ---------------------------------------------------------------------------

_M5 = []


# --- Python mirrors ---------------------------------------------------------

def _prefix(a):
    p = [0]
    for x in a:
        p.append(p[-1] + x)
    return p


def _range_sum(a, l, r):
    """Inclusive range sum, via the same prefix array the Java code builds."""
    p = _prefix(a)
    return p[r + 1] - p[l]


def _prefix2d(m):
    rows, cols = len(m), len(m[0])
    p = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            p[r + 1][c + 1] = m[r][c] + p[r][c + 1] + p[r + 1][c] - p[r][c]
    return p


def _sub_sum(m, r1, c1, r2, c2):
    p = _prefix2d(m)
    return p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1]


def _best_square(m, k):
    rows, cols = len(m), len(m[0])
    best = None
    for r in range(rows - k + 1):
        for c in range(cols - k + 1):
            s = _sub_sum(m, r, c, r + k - 1, c + k - 1)
            if best is None or s > best:
                best = s
    return best


def _has_pair(a, target):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return True
        if s < target:
            i += 1
        else:
            j -= 1
    return False


def _count_pairs(a, target):
    """Two-pointer pair count. Every test array is sorted and duplicate-free,
    so each pair is found exactly once."""
    i, j, count = 0, len(a) - 1, 0
    while i < j:
        s = a[i] + a[j]
        if s == target:
            count += 1
            i += 1
            j -= 1
        elif s < target:
            i += 1
        else:
            j -= 1
    return count


def _sorted_squares(a):
    return sorted(x * x for x in a)


def _window_sums(a, k):
    return [sum(a[i:i + k]) for i in range(len(a) - k + 1)]


def _best_window(a, k):
    return max(_window_sums(a, k))


def _best_window_at(a, k):
    ws = _window_sums(a, k)
    return ws.index(max(ws))


def _shortest_at_least(a, target):
    """Length of the shortest subarray with sum >= target, or 0 if none.
    Values are positive in every test case, which is what makes the window
    monotone."""
    best = len(a) + 1
    s = 0
    left = 0
    for right in range(len(a)):
        s += a[right]
        while s >= target:
            best = min(best, right - left + 1)
            s -= a[left]
            left += 1
    return 0 if best == len(a) + 1 else best


def _longest_at_most(a, target):
    best = 0
    s = 0
    left = 0
    for right in range(len(a)):
        s += a[right]
        while s > target and left <= right:
            s -= a[left]
            left += 1
        best = max(best, right - left + 1)
    return best


# --- 5.1 Prefix sums --------------------------------------------------------

_M5.append(_jlesson(
    "m5-prefix", "Prefix sums",
    "Pay O(n) once, then answer any range-sum question in O(1).",
    """
"What is the sum of `a[l]` through `a[r]`?" costs O(r − l) if you loop. Asked
a thousand times, that is a thousand loops. A **prefix-sum array** turns every
one of those into a single subtraction.

```java
int[] pre = new int[n + 1];                       // note: n + 1, not n
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
```

`pre[i]` holds the sum of the **first `i` elements** — so `pre[0]` is 0
(the sum of nothing), `pre[1]` is `a[0]`, and `pre[n]` is the whole total.

```
a   =        3    1    4    1    5
pre =   0    3    4    8    9   14
index   0    1    2    3    4    5
```

**The query, inclusive on both ends:**

```java
int sum = pre[r + 1] - pre[l];       // sum of a[l..r]
```

Everything up to and including `r`, minus everything before `l`. The `+ 1`
lives on `r` because `pre` is offset by one — which is exactly why the array is
`n + 1` long and starts with a 0. Without that leading zero you would need a
special case for `l == 0`, and that special case is where the bugs live.

**Sanity check it every time** with `l = 0, r = n - 1`: the formula gives
`pre[n] - pre[0]`, the whole total. If your formula does not survive that, it
is wrong.

**The trade.** Building costs O(n) time and O(n) space, once. Each query is
then O(1). Worth it from about two queries onward, and transformative for
thousands. This is the simplest example of the general move: **precompute
something so the repeated question becomes cheap.**

**Overflow.** `pre[n]` is the sum of everything, so it overflows an `int` far
sooner than any individual element does. `long[] pre` is the safe default in
real code.

**Beyond sums.** The same idea works for any operation with an inverse —
prefix products (divide), prefix XOR (XOR again). It does *not* work for max or
min, because you cannot "subtract" a maximum back out; those need a different
structure entirely.
""",
    warmup=[
        _jq("`a = {3, 1, 4, 1, 5}` with the prefix array above. What is the sum of `a[1..3]`?",
            ["6", "8", "9", "5"],
            0,
            "`pre[4] - pre[1]` = 9 − 3 = 6, which is 1 + 4 + 1. The `+1` on the right index "
            "is what makes the range inclusive."),
        _jq("Why is `pre` given length `n + 1` with `pre[0] = 0`?",
            ["So `l == 0` needs no special case — `pre[0]` is 'the sum of nothing'",
             "To leave room for the total",
             "Because arrays are 0-indexed",
             "It doesn't need to be; `n` works fine"],
            0,
            "With a length-n prefix array the query becomes `pre[r] - pre[l-1]`, which is out "
            "of bounds when l is 0. The leading zero removes the branch."),
    ],
    exercises=[
        _je("j5-pre-build", "Build the prefix array",
            "Build the prefix-sum array and print it. Replace `____` with the line "
            "that fills one slot — remember `pre[i + 1]` describes the first `i + 1` "
            "elements.",
            _jscan(
                _RD_ARR
                + "        int[] pre = new int[n + 1];\n"
                  "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
                  "        System.out.println(Arrays.toString(pre));"),
            "pre[i + 1] = pre[i] + a[i];",
            [_acase(a, _jarr(_prefix(a)))
             for a in ([3, 1, 4, 1, 5], [7], [-2, 5, -3])],
            hints=["Each slot is the previous slot plus one more element.",
                   "You are writing to `i + 1` and reading from `i`.",
                   "`pre[i + 1] = pre[i] + a[i];`"]),

        _je("j5-pre-query", "One subtraction per question",
            "After the array come two indices `l` and `r` (both inclusive). Print "
            "the sum of `a[l..r]` using the prefix array. Replace `____` with the "
            "expression.",
            _jscan(
                _RD_ARR
                + "        int l = sc.nextInt();\n"
                  "        int r = sc.nextInt();\n"
                  "        int[] pre = new int[n + 1];\n"
                  "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
                  "        System.out.println(pre[r + 1] - pre[l]);"),
            "pre[r + 1] - pre[l]",
            [_case(f"{len(a)}\n{_sp(a)}\n{l}\n{r}", _range_sum(a, l, r))
             for (a, l, r) in (([3, 1, 4, 1, 5], 1, 3), ([3, 1, 4, 1, 5], 0, 4),
                               ([3, 1, 4, 1, 5], 2, 2), ([-2, 5, -3], 0, 1))],
            hints=["Everything up to `r`, minus everything before `l`.",
                   "`pre` is offset by one, so 'up to and including r' is `pre[r + 1]`.",
                   "`pre[r + 1] - pre[l]`"],
            difficulty="Medium"),

        _jfix("j5-pre-offby", "Off by one element",
              "This answers range-sum queries and is always short by exactly the "
              "value at `a[r]`. One index is wrong.",
              _jscan(
                  _RD_ARR
                  + "        int l = sc.nextInt();\n"
                    "        int r = sc.nextInt();\n"
                    "        int[] pre = new int[n + 1];\n"
                    "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
                    "        System.out.println(pre[r] - pre[l]);"),
              _jscan(
                  _RD_ARR
                  + "        int l = sc.nextInt();\n"
                    "        int r = sc.nextInt();\n"
                    "        int[] pre = new int[n + 1];\n"
                    "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
                    "        System.out.println(pre[r + 1] - pre[l]);"),
              [_case(f"{len(a)}\n{_sp(a)}\n{l}\n{r}", _range_sum(a, l, r))
               for (a, l, r) in (([3, 1, 4, 1, 5], 1, 3), ([3, 1, 4, 1, 5], 0, 4),
                                 ([2, 2, 2], 0, 0))],
              hints=["Test the formula on `l = 0, r = n - 1`; it should give the whole total.",
                     "`pre[r]` is the sum of the first r elements — it stops just short of "
                     "`a[r]`.",
                     "`pre[r + 1] - pre[l]`"]),

        _jch("j5-pre-queries", "Answer a thousand questions", "Medium",
             "After the array comes `q`, then `q` lines each holding an `l` and an "
             "`r`. Print each range sum on its own line. Build the prefix array "
             "**once**, before the query loop — that is the whole point. Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int[] pre = new int[n + 1];\n"
                   "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
                   "        int q = sc.nextInt();\n"
                   "        for (int t = 0; t < q; t++) {\n"
                   "            int l = sc.nextInt();\n"
                   "            int r = sc.nextInt();\n"
                   "            System.out.println(pre[r + 1] - pre[l]);\n"
                   "        }"),
             "        int[] pre = new int[n + 1];\n"
             "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
             "        int q = sc.nextInt();\n"
             "        for (int t = 0; t < q; t++) {\n"
             "            int l = sc.nextInt();\n"
             "            int r = sc.nextInt();\n"
             "            System.out.println(pre[r + 1] - pre[l]);\n"
             "        }",
             [_case(f"{len(a)}\n{_sp(a)}\n{len(qs)}\n"
                    + "\n".join(f"{l} {r}" for (l, r) in qs),
                    _nl(*[_range_sum(a, l, r) for (l, r) in qs]))
              for (a, qs) in (([3, 1, 4, 1, 5], [(0, 4), (1, 3), (2, 2)]),
                              ([1, 2, 3], [(0, 0), (0, 2)]),
                              ([-2, 5, -3, 4], [(1, 3), (0, 1)]))],
             hints=["The prefix array is built once, outside the query loop.",
                    "Inside the loop, read `l` and `r` and print one subtraction.",
                    "Total cost is O(n + q), not O(n × q) — that is the win."]),
    ],
    quiz=[
        _jq("Building a prefix array costs O(n). From how many queries does it pay off?",
            ["About two — after that every query is O(1) instead of O(n)",
             "About n",
             "It never pays off for small arrays",
             "About log n"],
            0,
            "One query is a wash. Beyond that the O(n) build is amortised away and the "
            "answers are free."),
        _jq("Which of these can NOT be answered with a prefix array?",
            ["The maximum of a range", "The sum of a range",
             "The XOR of a range", "The product of a nonzero range"],
            0,
            "Prefix tricks need an inverse operation to 'subtract off' the front. Sum has "
            "minus, XOR is its own inverse, product has divide — max has nothing."),
    ],
))

# --- 5.2 2D prefix sums -----------------------------------------------------

_M5.append(_jlesson(
    "m5-prefix2d", "2D prefix sums",
    "The same idea on a grid — and the inclusion–exclusion that makes it work.",
    """
The grid version answers "what is the sum of this rectangle?" in O(1), and it
is the first place inclusion–exclusion shows up in ordinary code.

```java
int[][] pre = new int[rows + 1][cols + 1];         // one extra row AND column
for (int r = 0; r < rows; r++)
    for (int c = 0; c < cols; c++)
        pre[r + 1][c + 1] = m[r][c]
                          + pre[r][c + 1]           // everything above
                          + pre[r + 1][c]           // everything to the left
                          - pre[r][c];              // the overlap, counted twice
```

`pre[r][c]` is the sum of the rectangle from the top-left corner down to (but
not including) row `r`, column `c`. The `- pre[r][c]` is the whole trick: the
block above and the block to the left both contain the top-left corner region,
so adding them counts it twice and you take one copy back off.

**The query** for the rectangle from `(r1, c1)` to `(r2, c2)`, inclusive, is
the same idea inverted — take the big block, remove the strip above, remove the
strip to the left, and add back the corner you removed twice:

```java
int sum = pre[r2 + 1][c2 + 1]
        - pre[r1][c2 + 1]
        - pre[r2 + 1][c1]
        + pre[r1][c1];
```

Four array reads, regardless of how big the rectangle is. Every `+1` is the
offset from the extra row and column, exactly as in 1D.

**Sanity check:** the full grid is `(0, 0)` to `(rows-1, cols-1)`, which gives
`pre[rows][cols] - pre[0][cols] - pre[rows][0] + pre[0][0]` = `pre[rows][cols]`,
since the whole border row and column of `pre` are zero. If your signs do not
survive that check, they are wrong.

**Where it earns its keep:** "find the best `k × k` block" becomes a double
loop over top-left corners with an O(1) query each — O(rows × cols) instead of
O(rows × cols × k²). Image processing, heat maps and DP tables all lean on it.
""",
    warmup=[
        _jq("Why does the build formula subtract `pre[r][c]`?",
            ["The block above and the block to the left both include that corner region",
             "To handle negative values",
             "To keep the numbers small",
             "It is an optimisation, not a correctness issue"],
            0,
            "Inclusion–exclusion: adding two overlapping regions double-counts the overlap, "
            "so one copy has to come back off."),
        _jq("How many array reads does a rectangle-sum query take, for a 500×500 rectangle?",
            ["4", "500", "250,000", "1,000"],
            0,
            "Four, always. The size of the rectangle does not appear anywhere in the query — "
            "that is the entire point of the precomputation."),
    ],
    exercises=[
        _je("j5-p2-build", "Build the 2D prefix grid",
            "Build the 2D prefix-sum grid and print the total of the whole grid "
            "(which is its bottom-right corner). Replace `____` with the build "
            "formula for one cell.",
            _jscan(
                _RD_MAT
                + "        int[][] pre = new int[rows + 1][cols + 1];\n"
                  "        for (int r = 0; r < rows; r++) {\n"
                  "            for (int c = 0; c < cols; c++) {\n"
                  "                pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(pre[rows][cols]);"),
            "pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];",
            [_mcase(m, sum(sum(r) for r in m))
             for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[1, -2], [-3, 4]])],
            hints=["The cell itself, plus the block above, plus the block to the left…",
                   "…minus the corner region those two share.",
                   "`pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];`"],
            difficulty="Medium"),

        _je("j5-p2-query", "Sum a rectangle in O(1)",
            "After the grid come `r1 c1 r2 c2` — the inclusive corners of a "
            "rectangle. Print its sum. Replace `____` with the four-term query.",
            _jscan(
                _RD_MAT
                + "        int r1 = sc.nextInt();\n"
                  "        int c1 = sc.nextInt();\n"
                  "        int r2 = sc.nextInt();\n"
                  "        int c2 = sc.nextInt();\n"
                  "        int[][] pre = new int[rows + 1][cols + 1];\n"
                  "        for (int r = 0; r < rows; r++)\n"
                  "            for (int c = 0; c < cols; c++)\n"
                  "                pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];\n"
                  "        System.out.println(pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1] - pre[r2 + 1][c1] + pre[r1][c1]);"),
            "pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1] - pre[r2 + 1][c1] + pre[r1][c1]",
            [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(r) for r in m)
                   + f"\n{r1} {c1} {r2} {c2}", _sub_sum(m, r1, c1, r2, c2))
             for (m, r1, c1, r2, c2) in (
                 ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1, 1, 2, 2),
                 ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 0, 0, 2, 2),
                 ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 0, 1, 1, 2),
                 ([[5]], 0, 0, 0, 0))],
            hints=["Big block, minus the strip above, minus the strip to the left…",
                   "…plus the top-left corner you just removed twice.",
                   "Every index gets a `+1` on the bottom-right corner and none on the "
                   "top-left."],
            difficulty="Hard"),

        _jfix("j5-p2-signs", "The corner subtracted twice",
              "This 2D prefix build is missing one term, so every total below and "
              "right of the first cell comes out too small. Fix the build formula.",
              _jscan(
                  _RD_MAT
                  + "        int[][] pre = new int[rows + 1][cols + 1];\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < cols; c++) {\n"
                    "                pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c];\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(pre[rows][cols]);"),
              _jscan(
                  _RD_MAT
                  + "        int[][] pre = new int[rows + 1][cols + 1];\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < cols; c++) {\n"
                    "                pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(pre[rows][cols]);"),
              [_mcase(m, sum(sum(r) for r in m))
               for m in ([[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6]], [[9]])],
              hints=["Adding the block above and the block to the left counts something twice.",
                     "Which region belongs to both of them?",
                     "Subtract `pre[r][c]` — the overlap."]),

        _jch("j5-p2-square", "The best k × k block", "Hard",
             "After the grid comes `k`. Print the largest sum of any `k × k` block. "
             "Build the 2D prefix grid once, then check every top-left corner with an "
             "O(1) query. Write the whole block where you see `____`.",
             _jscan(
                 _RD_MAT
                 + "        int k = sc.nextInt();\n"
                   "        int[][] pre = new int[rows + 1][cols + 1];\n"
                   "        for (int r = 0; r < rows; r++)\n"
                   "            for (int c = 0; c < cols; c++)\n"
                   "                pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];\n"
                   "        int best = pre[k][k] - pre[0][k] - pre[k][0] + pre[0][0];\n"
                   "        for (int r = 0; r + k <= rows; r++) {\n"
                   "            for (int c = 0; c + k <= cols; c++) {\n"
                   "                int s = pre[r + k][c + k] - pre[r][c + k] - pre[r + k][c] + pre[r][c];\n"
                   "                if (s > best) best = s;\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(best);"),
             "        int[][] pre = new int[rows + 1][cols + 1];\n"
             "        for (int r = 0; r < rows; r++)\n"
             "            for (int c = 0; c < cols; c++)\n"
             "                pre[r + 1][c + 1] = m[r][c] + pre[r][c + 1] + pre[r + 1][c] - pre[r][c];\n"
             "        int best = pre[k][k] - pre[0][k] - pre[k][0] + pre[0][0];\n"
             "        for (int r = 0; r + k <= rows; r++) {\n"
             "            for (int c = 0; c + k <= cols; c++) {\n"
             "                int s = pre[r + k][c + k] - pre[r][c + k] - pre[r + k][c] + pre[r][c];\n"
             "                if (s > best) best = s;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(best);",
             [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(r) for r in m) + f"\n{k}",
                    _best_square(m, k))
              for (m, k) in (([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2),
                             ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1),
                             ([[1, 2], [3, 4]], 2),
                             ([[-1, -2, -3], [-4, -5, -6]], 2))],
             hints=["Corners run while `r + k <= rows` and `c + k <= cols`.",
                    "With a top-left corner at (r, c), the block's inclusive bottom-right is "
                    "(r + k - 1, c + k - 1) — so the query indices are `r + k` and `c + k`.",
                    "Seed `best` from a real block (the one at the origin), not from 0 — the "
                    "all-negative case is in the hidden tests.",
                    "Total cost is O(rows × cols), not O(rows × cols × k²)."]),
    ],
    quiz=[
        _jq("The 2D query has four terms with signs + − − +. Which check proves your signs?",
            ["Query the whole grid; it must equal pre[rows][cols]",
             "Query a single cell; it must equal 0",
             "Query an empty rectangle",
             "Compare against a nested-loop sum for one random rectangle"],
            0,
            "For the full grid the three other terms are all on `pre`'s zero border, so the "
            "answer collapses to the bottom-right corner. It is a two-second check that "
            "catches every sign error."),
        _jq("Finding the best k × k block by summing each block directly costs…",
            ["O(rows × cols × k²), versus O(rows × cols) with prefix sums",
             "O(rows × cols) either way",
             "O(k²)",
             "O(rows + cols)"],
            0,
            "Each block sum is k² additions and there are about rows × cols blocks. Prefix "
            "sums make each block O(1)."),
    ],
))

# --- 5.3 Two pointers -------------------------------------------------------

_M5.append(_jlesson(
    "m5-twoptr", "The two-pointer technique",
    "On sorted data, one comparison rules out a whole row of possibilities.",
    """
Module 4 used two pointers walking *toward* each other to reverse an array.
The same shape solves a much more interesting problem: **find a pair that sums
to a target, in a sorted array, in O(n) time and O(1) space.**

```java
int i = 0, j = n - 1;
while (i < j) {
    int sum = a[i] + a[j];
    if (sum == target) { found = true; break; }
    else if (sum < target) i++;        // need MORE: give up the smallest
    else j--;                           // need LESS: give up the largest
}
```

**Why this is correct, not just fast.** When `a[i] + a[j] < target`, `a[i]` is
the smallest value left — so it cannot make the target with *any* remaining
partner, because `a[j]` was the largest one available. Discarding it discards a
whole row of the pair table, which is why one pass suffices instead of n².

**It only works on sorted data.** The argument above depends entirely on `a[i]`
being the smallest and `a[j]` the largest. On unsorted data the technique is
simply wrong. If the input is not sorted you either sort first (O(n log n)) or
use a hash set (O(n) time, O(n) space) — naming both is the interview answer.

**`i < j`, not `i <= j`.** With `i == j` you would be pairing an element with
itself, which is almost never allowed.

**Counting pairs** instead of just detecting one: on a hit, move **both**
pointers, since each of them has now been used.

```java
if (sum == target) { count++; i++; j--; }
```

**The other two-pointer shape: fill from the back.** "Given a sorted array that
may contain negatives, return the sorted array of squares." The largest square
is at one end or the other — never in the middle — so compare the two ends and
write the winner into the *last* free slot:

```java
int[] out = new int[n];
int i = 0, j = n - 1;
for (int p = n - 1; p >= 0; p--) {
    int left = a[i] * a[i], right = a[j] * a[j];
    if (left > right) { out[p] = left; i++; }
    else               { out[p] = right; j--; }
}
```

O(n), versus O(n log n) for "square everything then sort". Writing backwards is
the move that makes it work — the answers arrive largest-first.
""",
    warmup=[
        _jq("Sorted `{1, 3, 5, 8}`, target 9. `i=0, j=3` gives 1+8=9. What if the target were 10?",
            ["1+8 < 10, so i++ — 1 cannot reach 10 with anything smaller than 8",
             "j-- , to try a smaller partner",
             "Both move",
             "Neither; the answer is absent"],
            0,
            "`a[j]` is the biggest partner available. If the smallest element cannot make the "
            "target even with it, it can never make the target — so discard it."),
        _jq("Why does the two-pointer pair search fail on unsorted data?",
            ["The 'a[i] is the smallest remaining' argument no longer holds",
             "It doesn't fail — it just gets slower",
             "Because `i < j` becomes wrong",
             "It only fails when the array has duplicates"],
            0,
            "Every discard is justified by order. Without it, moving a pointer throws away "
            "pairs that might have worked."),
    ],
    exercises=[
        _je("j5-tp-pair", "Does a pair sum to the target?",
            "The array arrives **sorted**. Print `true` when some pair of distinct "
            "positions sums to `target`, otherwise `false`. Replace `____` with the "
            "branch that decides which pointer moves.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int i = 0;\n"
                  "        int j = n - 1;\n"
                  "        boolean found = false;\n"
                  "        while (i < j) {\n"
                  "            int sum = a[i] + a[j];\n"
                  "            if (sum == target) { found = true; break; }\n"
                  "            else if (sum < target) i++;\n"
                  "            else j--;\n"
                  "        }\n"
                  "        System.out.println(found);"),
            "            else if (sum < target) i++;\n"
            "            else j--;",
            [_akcase(a, t, _jbool(_has_pair(a, t)))
             for (a, t) in (([1, 3, 5, 8], 9), ([1, 3, 5, 8], 10),
                            ([1, 3, 5, 8], 4), ([2, 4], 6), ([2, 4], 7))],
            hints=["Too small means you need a bigger contribution — from which end?",
                   "The left pointer holds the smallest remaining value.",
                   "`else if (sum < target) i++;` then `else j--;`"],
            difficulty="Medium"),

        _je("j5-tp-count", "Count the pairs",
            "Same sorted, duplicate-free array. Print **how many** distinct pairs sum "
            "to `target`. Replace `____` with what happens on a hit — remember both "
            "elements are now used up.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int i = 0;\n"
                  "        int j = n - 1;\n"
                  "        int count = 0;\n"
                  "        while (i < j) {\n"
                  "            int sum = a[i] + a[j];\n"
                  "            if (sum == target) { count++; i++; j--; }\n"
                  "            else if (sum < target) i++;\n"
                  "            else j--;\n"
                  "        }\n"
                  "        System.out.println(count);"),
            "{ count++; i++; j--; }",
            [_akcase(a, t, _count_pairs(a, t))
             for (a, t) in (([1, 2, 3, 4, 5], 6), ([1, 2, 3, 4, 5], 9),
                            ([1, 2, 3, 4, 5], 100), ([1, 2, 3, 4], 5))],
            hints=["Record the pair, then retire both elements.",
                   "Moving only one pointer would find the same pair again.",
                   "`{ count++; i++; j--; }`"],
            difficulty="Medium"),

        _jfix("j5-tp-self", "It pairs an element with itself",
              "This counts pairs summing to `target`, but on `{1, 2, 3, 4}` with "
              "target `6` it reports 2 instead of 1 — it is counting `3 + 3` using the "
              "same element twice. One comparison is wrong.",
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int i = 0;\n"
                    "        int j = n - 1;\n"
                    "        int count = 0;\n"
                    "        while (i <= j) {\n"
                    "            int sum = a[i] + a[j];\n"
                    "            if (sum == target) { count++; i++; j--; }\n"
                    "            else if (sum < target) i++;\n"
                    "            else j--;\n"
                    "        }\n"
                    "        System.out.println(count);"),
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int i = 0;\n"
                    "        int j = n - 1;\n"
                    "        int count = 0;\n"
                    "        while (i < j) {\n"
                    "            int sum = a[i] + a[j];\n"
                    "            if (sum == target) { count++; i++; j--; }\n"
                    "            else if (sum < target) i++;\n"
                    "            else j--;\n"
                    "        }\n"
                    "        System.out.println(count);"),
              [_akcase(a, t, _count_pairs(a, t))
               for (a, t) in (([1, 2, 3, 4], 6), ([1, 2, 3, 4, 5], 6), ([2, 4], 4))],
              hints=["What does the loop do on the iteration where `i` and `j` are equal?",
                     "A pair needs two distinct positions.",
                     "`while (i < j)`"]),

        _jch("j5-tp-squares", "Sorted squares in O(n)", "Hard",
             "The array arrives **sorted** and may contain negatives. Print the sorted "
             "array of the squares — without calling `Arrays.sort`. The largest square "
             "is always at one end or the other, so compare the ends and fill the "
             "output from the back. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int[] out = new int[n];\n"
                   "        int i = 0;\n"
                   "        int j = n - 1;\n"
                   "        for (int p = n - 1; p >= 0; p--) {\n"
                   "            int left = a[i] * a[i];\n"
                   "            int right = a[j] * a[j];\n"
                   "            if (left > right) { out[p] = left; i++; }\n"
                   "            else { out[p] = right; j--; }\n"
                   "        }\n"
                   "        System.out.println(Arrays.toString(out));"),
             "        int[] out = new int[n];\n"
             "        int i = 0;\n"
             "        int j = n - 1;\n"
             "        for (int p = n - 1; p >= 0; p--) {\n"
             "            int left = a[i] * a[i];\n"
             "            int right = a[j] * a[j];\n"
             "            if (left > right) { out[p] = left; i++; }\n"
             "            else { out[p] = right; j--; }\n"
             "        }\n"
             "        System.out.println(Arrays.toString(out));",
             [_acase(a, _jarr(_sorted_squares(a)))
              for a in ([-4, -1, 0, 3, 10], [-7, -3, 2, 3, 11], [1, 2, 3],
                        [-5, -4, -3], [6])],
             hints=["A negative with a big magnitude squares to a big number, so the maximum "
                    "square is at one END of a sorted array.",
                    "Fill `out` from index n-1 downward, because you discover the answers "
                    "largest-first.",
                    "Each pass writes exactly one slot and moves exactly one pointer — that "
                    "is why the loop runs exactly n times.",
                    "On a tie either branch is fine; the values are equal."]),
    ],
    quiz=[
        _jq("Two-sum on an UNSORTED array. What are your two options and their costs?",
            ["Sort then two pointers — O(n log n) / O(1); or a hash set — O(n) / O(n)",
             "Two pointers works anyway — O(n) / O(1)",
             "Only brute force — O(n²) / O(1)",
             "Sort then binary search — O(n²) / O(1)"],
            0,
            "The trade is time against space. If the array is already sorted, two pointers "
            "wins outright."),
        _jq("Sorted squares by 'square everything, then Arrays.sort' costs what compared with two pointers?",
            ["O(n log n) versus O(n)",
             "The same, O(n log n) both",
             "O(n²) versus O(n)",
             "Two pointers is slower but uses less memory"],
            0,
            "Both allocate an output array, so space is the same. The two-pointer version "
            "exploits the existing order instead of throwing it away and re-sorting."),
    ],
))

# --- 5.4 Fixed-size sliding window -----------------------------------------

_M5.append(_jlesson(
    "m5-window-fixed", "The fixed-size sliding window",
    "Add the entering element, subtract the leaving one — never re-add the middle.",
    """
"What is the largest sum of any `k` consecutive elements?" The naive answer
sums each window from scratch: O(n·k). The window answer notices that
consecutive windows **overlap in all but two elements**.

```java
int sum = 0;
for (int i = 0; i < k; i++) sum += a[i];    // the first window, in full
int best = sum;                              // seed from REAL data

for (int i = k; i < n; i++) {
    sum += a[i] - a[i - k];                  // one in, one out
    if (sum > best) best = sum;
}
```

**`a[i] - a[i - k]` is the whole algorithm.** When the window moves one step
right, `a[i]` enters and `a[i - k]` — the element that was at the far left —
leaves. Everything between them is unchanged and must not be touched.

Work out `i - k` once, carefully, and it never troubles you again: when `i` is
the new right end, the window covers `i-k+1 .. i`, so the element that just
fell off is at `i - k`.

**Seed `best` from the first window, not from 0.** Same rule as module 1's max:
`0` asserts that an all-negative array has a window summing to zero, which is a
lie. This is one of the two bugs in this lesson.

**The number of windows is `n - k + 1`.** For `n = 5, k = 3` there are three:
starting at 0, 1 and 2. Getting the loop bound from that count (rather than
guessing) is how you avoid the other bug.

**Cost:** O(n) time, O(1) space, exactly `n` additions instead of `n·k`.

**When it does not apply.** The window trick needs the quantity to be
**reversible** — you must be able to un-add the element that leaves. Sums and
counts qualify. The *maximum* of a window does not: once the biggest element
leaves, you cannot recover what the second biggest was without extra structure
(a deque — Part 6 of the roadmap). Knowing where the pattern stops is as
valuable as knowing it.
""",
    warmup=[
        _jq("`a = {1, 2, 3, 4, 5}`, k = 3. How many windows are there?",
            ["3", "4", "5", "2"],
            0,
            "`n - k + 1` = 5 − 3 + 1 = 3: [1,2,3], [2,3,4], [3,4,5]."),
        _jq("When the right end of a size-k window reaches index `i`, which element just left?",
            ["a[i - k]", "a[i - k + 1]", "a[i - 1]", "a[k]"],
            0,
            "The window now covers `i-k+1 .. i`, so the element immediately before that "
            "range, `a[i - k]`, is the one that fell off."),
    ],
    exercises=[
        _je("j5-fw-slide", "One in, one out",
            "After the array comes `k`. Print the largest sum of any `k` consecutive "
            "elements. Replace `____` with the line that slides the window one step.",
            _jscan(
                _RD_ARR
                + "        int k = sc.nextInt();\n"
                  "        int sum = 0;\n"
                  "        for (int i = 0; i < k; i++) sum += a[i];\n"
                  "        int best = sum;\n"
                  "        for (int i = k; i < n; i++) {\n"
                  "            sum += a[i] - a[i - k];\n"
                  "            if (sum > best) best = sum;\n"
                  "        }\n"
                  "        System.out.println(best);"),
            "sum += a[i] - a[i - k];",
            [_akcase(a, k, _best_window(a, k))
             for (a, k) in (([1, 2, 3, 4, 5], 3), ([5, 1, 1, 1, 9], 2),
                            ([-3, -1, -4], 2), ([7], 1))],
            hints=["Exactly one element enters and exactly one leaves.",
                   "The one entering is `a[i]`; the one leaving is k slots back.",
                   "`sum += a[i] - a[i - k];`"],
            difficulty="Medium"),

        _je("j5-fw-all", "Every window's sum",
            "Print the sum of **every** window of size `k`, in order, space "
            "separated. There are `n - k + 1` of them. Replace `____` with the loop "
            "that slides and prints the rest.",
            _jscan(
                _RD_ARR
                + "        int k = sc.nextInt();\n"
                  "        int sum = 0;\n"
                  "        for (int i = 0; i < k; i++) sum += a[i];\n"
                  '        System.out.print(sum + " ");\n'
                  "        for (int i = k; i < n; i++) {\n"
                  "            sum += a[i] - a[i - k];\n"
                  '            System.out.print(sum + " ");\n'
                  "        }\n"
                  "        System.out.println();"),
            "        for (int i = k; i < n; i++) {\n"
            "            sum += a[i] - a[i - k];\n"
            '            System.out.print(sum + " ");\n'
            "        }",
            [_akcase(a, k, _sp(_window_sums(a, k)))
             for (a, k) in (([1, 2, 3, 4, 5], 3), ([1, 2, 3, 4, 5], 1),
                            ([1, 2, 3, 4, 5], 5), ([4, 4, 4], 2))],
            hints=["The first window is already printed, so the loop starts at `i = k`.",
                   "Slide, then print — one line of each.",
                   "The loop runs n − k times and prints n − k more sums, for n − k + 1 total."]),

        _jfix("j5-fw-seed", "Best window of a negative array",
              "This finds the largest window sum, and gets it right until every value "
              "is negative — then it reports `0`, which is not the sum of any window. "
              "Fix it.",
              _jscan(
                  _RD_ARR
                  + "        int k = sc.nextInt();\n"
                    "        int sum = 0;\n"
                    "        for (int i = 0; i < k; i++) sum += a[i];\n"
                    "        int best = 0;\n"
                    "        for (int i = k; i < n; i++) {\n"
                    "            sum += a[i] - a[i - k];\n"
                    "            if (sum > best) best = sum;\n"
                    "        }\n"
                    "        System.out.println(best);"),
              _jscan(
                  _RD_ARR
                  + "        int k = sc.nextInt();\n"
                    "        int sum = 0;\n"
                    "        for (int i = 0; i < k; i++) sum += a[i];\n"
                    "        int best = sum;\n"
                    "        for (int i = k; i < n; i++) {\n"
                    "            sum += a[i] - a[i - k];\n"
                    "            if (sum > best) best = sum;\n"
                    "        }\n"
                    "        System.out.println(best);"),
              [_akcase(a, k, _best_window(a, k))
               for (a, k) in (([-3, -1, -4], 2), ([-5, -2], 1), ([1, 2, 3], 2))],
              hints=["Where does `best` start, and is that a sum any window actually has?",
                     "Module 1's rule: seed from real data.",
                     "`int best = sum;` — the first window's sum."]),

        _jch("j5-fw-index", "Where the best window starts", "Medium",
             "Print two lines: the largest window sum, and the **starting index** of "
             "the first window achieving it. For `{5, 1, 1, 1, 9}` with `k = 2` that "
             "is `10` and `3`. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int k = sc.nextInt();\n"
                   "        int sum = 0;\n"
                   "        for (int i = 0; i < k; i++) sum += a[i];\n"
                   "        int best = sum;\n"
                   "        int bestAt = 0;\n"
                   "        for (int i = k; i < n; i++) {\n"
                   "            sum += a[i] - a[i - k];\n"
                   "            if (sum > best) { best = sum; bestAt = i - k + 1; }\n"
                   "        }\n"
                   "        System.out.println(best);\n"
                   "        System.out.println(bestAt);"),
             "        int sum = 0;\n"
             "        for (int i = 0; i < k; i++) sum += a[i];\n"
             "        int best = sum;\n"
             "        int bestAt = 0;\n"
             "        for (int i = k; i < n; i++) {\n"
             "            sum += a[i] - a[i - k];\n"
             "            if (sum > best) { best = sum; bestAt = i - k + 1; }\n"
             "        }\n"
             "        System.out.println(best);\n"
             "        System.out.println(bestAt);",
             [_akcase(a, k, _nl(_best_window(a, k), _best_window_at(a, k)))
              for (a, k) in (([5, 1, 1, 1, 9], 2), ([1, 2, 3, 4, 5], 3),
                             ([4, 4, 4, 4], 2), ([-3, -1, -4], 2), ([7], 1))],
             hints=["Seed both `best` and `bestAt` from the first window: its sum, and index 0.",
                    "When the right end is at `i`, the window starts at `i - k + 1`.",
                    "Strict `>` keeps the FIRST window of a tie — `{4,4,4,4}` with k=2 must "
                    "report index 0."]),
    ],
    quiz=[
        _jq("The sliding window turns O(n·k) into O(n) by relying on what property?",
            ["The quantity is reversible — you can subtract the element that leaves",
             "The array is sorted",
             "k is small",
             "The values are positive"],
            0,
            "Sums and counts can be un-done. A window *maximum* cannot, which is why that "
            "problem needs a deque rather than a running variable."),
        _jq("`n = 10, k = 4`. The sliding loop `for (int i = k; i < n; i++)` runs how many times, and how many windows exist?",
            ["6 times, 7 windows", "7 times, 7 windows",
             "6 times, 6 windows", "10 times, 7 windows"],
            0,
            "The first window is built before the loop; the loop produces the other six. "
            "n − k + 1 = 7 windows in total."),
    ],
))

# --- 5.5 Variable-size sliding window --------------------------------------

_M5.append(_jlesson(
    "m5-window-var", "The variable-size sliding window",
    "Grow on the right, shrink on the left, and touch every element at most twice.",
    """
When the window's *size* is what you are solving for — "the shortest subarray
summing to at least `target`", "the longest subarray summing to at most
`target`" — the window has two moving ends under one rule:

```java
int best = n + 1;                              // impossible sentinel
int sum = 0, left = 0;
for (int right = 0; right < n; right++) {
    sum += a[right];                            // GROW to the right
    while (sum >= target) {                     // while the window is valid…
        if (right - left + 1 < best) best = right - left + 1;
        sum -= a[left];                          // …SHRINK from the left
        left++;
    }
}
System.out.println(best == n + 1 ? 0 : best);
```

**Why it is O(n), not O(n²).** `right` only ever increases, and `left` only ever
increases. Between them they advance at most `2n` times no matter how the
`while` loop interleaves — so the nested loop does *not* make this quadratic.
Being able to say that sentence is the point of the lesson.

**`while`, not `if`.** After one step to the right, the window may need to
shrink several times before it stops being valid. An `if` shrinks once and
leaves the window in the wrong state — the classic bug, and the fix-the-bug
below.

**The window length is `right - left + 1`.** Both ends inclusive. Write it once
and reuse it; deriving it under pressure is where off-by-ones come from.

**Shortest vs longest changes where you measure.**

- *Shortest valid*: record the length **inside** the shrink loop, while the
  window is still valid, then shrink past it.
- *Longest valid*: shrink **until** the window becomes valid again, then record
  the length after the `while`, when validity has just been restored.

```java
for (int right = 0; right < n; right++) {       // longest with sum <= target
    sum += a[right];
    while (sum > target) { sum -= a[left]; left++; }
    if (right - left + 1 > best) best = right - left + 1;
}
```

**The precondition everybody forgets: the values must be positive.** The whole
method assumes that adding an element can only push the sum up and removing one
can only push it down. With negatives that monotonicity is gone and a sliding
window is simply wrong — you need prefix sums plus a map instead. Say this out
loud in an interview; it is the follow-up question.
""",
    warmup=[
        _jq("Why does replacing the shrink `while` with an `if` break the algorithm?",
            ["One step right can make several shrinks necessary before the window stops being valid",
             "`if` cannot contain a subtraction",
             "It makes the algorithm O(n²)",
             "It doesn't — they are equivalent"],
            0,
            "Adding one large element can make a long window valid; you may have to remove "
            "several from the left before validity is lost again."),
        _jq("Both `left` and `right` only ever move forward. What does that make the total cost?",
            ["O(n) — the two pointers advance at most 2n times between them",
             "O(n²), because of the nested loop",
             "O(n log n)",
             "It depends on the target"],
            0,
            "The `while` is nested but not quadratic: it is bounded globally by how far "
            "`left` can travel, which is n."),
    ],
    exercises=[
        _je("j5-vw-shrink", "Shrink from the left",
            "All values are positive. Print the length of the **shortest** subarray "
            "whose sum is at least `target`, or `0` if there is none. Replace `____` "
            "with the two statements that shrink the window.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int best = n + 1;\n"
                  "        int sum = 0;\n"
                  "        int left = 0;\n"
                  "        for (int right = 0; right < n; right++) {\n"
                  "            sum += a[right];\n"
                  "            while (sum >= target) {\n"
                  "                if (right - left + 1 < best) best = right - left + 1;\n"
                  "                sum -= a[left];\n"
                  "                left++;\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(best == n + 1 ? 0 : best);"),
            "                sum -= a[left];\n"
            "                left++;",
            [_akcase(a, t, _shortest_at_least(a, t))
             for (a, t) in (([2, 3, 1, 2, 4, 3], 7), ([1, 1, 1, 1], 3),
                            ([1, 2], 100), ([5], 5))],
            hints=["Undo the element at `left`, then move `left` past it.",
                   "Order matters: subtract first, or you subtract the wrong element.",
                   "`sum -= a[left];` then `left++;`"],
            difficulty="Hard"),

        _je("j5-vw-longest", "The longest that stays under",
            "All values are positive. Print the length of the **longest** subarray "
            "whose sum is at most `target` (`0` if even a single element is too big). "
            "Replace `____` with the shrink loop.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int best = 0;\n"
                  "        int sum = 0;\n"
                  "        int left = 0;\n"
                  "        for (int right = 0; right < n; right++) {\n"
                  "            sum += a[right];\n"
                  "            while (sum > target && left <= right) {\n"
                  "                sum -= a[left];\n"
                  "                left++;\n"
                  "            }\n"
                  "            if (right - left + 1 > best) best = right - left + 1;\n"
                  "        }\n"
                  "        System.out.println(best);"),
            "            while (sum > target && left <= right) {\n"
            "                sum -= a[left];\n"
            "                left++;\n"
            "            }",
            [_akcase(a, t, _longest_at_most(a, t))
             for (a, t) in (([2, 1, 5, 1, 3, 2], 8), ([1, 1, 1, 1], 2),
                            ([10, 20], 5), ([4], 4))],
            hints=["Shrink while the window is INVALID — that is, while the sum exceeds the "
                   "target.",
                   "`left <= right` keeps the window from inverting when a single element "
                   "already exceeds the target.",
                   "The measurement happens after the `while`, once validity is restored."],
            difficulty="Hard"),

        _jfix("j5-vw-if", "It only shrinks once",
              "This should find the shortest subarray with sum at least `target`. It "
              "over-reports the length whenever the window needs more than one shrink "
              "— try `{1, 1, 1, 10}` with target `10`. One keyword is wrong.",
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int best = n + 1;\n"
                    "        int sum = 0;\n"
                    "        int left = 0;\n"
                    "        for (int right = 0; right < n; right++) {\n"
                    "            sum += a[right];\n"
                    "            if (sum >= target) {\n"
                    "                if (right - left + 1 < best) best = right - left + 1;\n"
                    "                sum -= a[left];\n"
                    "                left++;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(best == n + 1 ? 0 : best);"),
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int best = n + 1;\n"
                    "        int sum = 0;\n"
                    "        int left = 0;\n"
                    "        for (int right = 0; right < n; right++) {\n"
                    "            sum += a[right];\n"
                    "            while (sum >= target) {\n"
                    "                if (right - left + 1 < best) best = right - left + 1;\n"
                    "                sum -= a[left];\n"
                    "                left++;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(best == n + 1 ? 0 : best);"),
              [_akcase(a, t, _shortest_at_least(a, t))
               for (a, t) in (([1, 1, 1, 10], 10), ([2, 3, 1, 2, 4, 3], 7),
                              ([1, 1, 1, 1], 3))],
              hints=["After one shrink, is the window still valid? Should you check again?",
                     "One element entering can make several shrinks necessary.",
                     "`while (sum >= target)`"]),

        _jch("j5-vw-count", "Count the short-enough windows", "Hard",
             "All values are positive. Print how many subarrays have a sum of at most "
             "`target`. Use the variable window: when the window ending at `right` is "
             "valid, **every** subarray ending at `right` that starts at or after "
             "`left` is also valid — that is `right - left + 1` of them. Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int target = sc.nextInt();\n"
                   "        int count = 0;\n"
                   "        int sum = 0;\n"
                   "        int left = 0;\n"
                   "        for (int right = 0; right < n; right++) {\n"
                   "            sum += a[right];\n"
                   "            while (sum > target && left <= right) {\n"
                   "                sum -= a[left];\n"
                   "                left++;\n"
                   "            }\n"
                   "            count += right - left + 1;\n"
                   "        }\n"
                   "        System.out.println(count);"),
             "        int count = 0;\n"
             "        int sum = 0;\n"
             "        int left = 0;\n"
             "        for (int right = 0; right < n; right++) {\n"
             "            sum += a[right];\n"
             "            while (sum > target && left <= right) {\n"
             "                sum -= a[left];\n"
             "                left++;\n"
             "            }\n"
             "            count += right - left + 1;\n"
             "        }\n"
             "        System.out.println(count);",
             [_akcase(a, t, sum(1 for i in range(len(a)) for j in range(i, len(a))
                                if sum(a[i:j + 1]) <= t))
              for (a, t) in (([1, 2, 3], 4), ([1, 1, 1, 1], 2),
                             ([10, 20], 5), ([3], 3), ([2, 1, 5, 1, 3, 2], 8))],
             hints=["Same skeleton as the longest-window drill; only the last line differs.",
                    "After shrinking, every start position from `left` to `right` gives a "
                    "valid subarray ending at `right`.",
                    "That is `right - left + 1` subarrays — add them all at once.",
                    "When a single element already exceeds the target, `left` ends up past "
                    "`right`… which is why the shrink loop also tests `left <= right`, "
                    "leaving `right - left + 1` equal to 0."]),
    ],
    quiz=[
        _jq("Sliding window on an array containing negative numbers is…",
            ["wrong — growing the window no longer only increases the sum",
             "correct but slower",
             "correct only for the 'longest' variants",
             "correct as long as the target is positive"],
            0,
            "The method depends on monotonicity: adding pushes the sum up, removing pushes "
            "it down. Negatives break both, and the answer becomes prefix sums plus a map."),
        _jq("Where do you measure the window for 'shortest valid' versus 'longest valid'?",
            ["Shortest: inside the shrink loop, while still valid. Longest: after it, once valid again",
             "Both inside the shrink loop",
             "Both after the shrink loop",
             "Shortest after, longest inside"],
            0,
            "The shrink loop runs while the window is valid in one case and while it is "
            "invalid in the other, so the moment at which the window is worth measuring "
            "flips accordingly."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m5_engine(a, queries):
    pre = _prefix(a)
    out = []
    for q in queries:
        if q[0] == 1:
            out.append(pre[q[2] + 1] - pre[q[1]])
        else:
            k = q[1]
            out.append(max(pre[i + k] - pre[i] for i in range(len(a) - k + 1)))
    return _nl(*out)


def _m5_case(a, queries):
    lines = [str(len(a)), _sp(a), str(len(queries))]
    for q in queries:
        lines.append(_sp(q))
    return _case("\n".join(lines), _m5_engine(a, queries))


_M5_CAP = _jcap(
    "Range query engine",
    """
A tiny query engine, built on one prefix-sum array.

Read `n`, the `n` values, then `q`, then `q` query lines. Each query starts
with a type code:

| Line | Meaning | Print |
|---|---|---|
| `1 l r` | range sum, inclusive | the sum of `a[l..r]` |
| `2 k` | best window | the largest sum of any `k` consecutive elements |

Print one line per query, in order.

**Build the prefix array exactly once**, before the query loop. Then *both*
query types are O(1) per window:

- a range sum is `pre[r + 1] - pre[l]`;
- a window starting at `i` with length `k` sums to `pre[i + k] - pre[i]`, so
  the best window is a single loop over `i` from `0` to `n - k`.

That second observation is the point of the capstone: **a fixed-size window is
just a range query with a fixed width**, so the prefix array serves both. You
do not need a separate sliding-window variable here at all.

Values may be negative, so seed the "best window" search from a real window,
not from `0`.
""",
    _jch("j5-cap-engine", "Range query engine", "Hard",
         "Write the whole engine where you see `____` — build the prefix array once, "
         "then dispatch on the query type.",
         _jscan(
             _RD_ARR
             + "        int[] pre = new int[n + 1];\n"
               "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
               "        int q = sc.nextInt();\n"
               "        for (int t = 0; t < q; t++) {\n"
               "            int type = sc.nextInt();\n"
               "            if (type == 1) {\n"
               "                int l = sc.nextInt();\n"
               "                int r = sc.nextInt();\n"
               "                System.out.println(pre[r + 1] - pre[l]);\n"
               "            } else {\n"
               "                int k = sc.nextInt();\n"
               "                int best = pre[k] - pre[0];\n"
               "                for (int i = 0; i + k <= n; i++) {\n"
               "                    int s = pre[i + k] - pre[i];\n"
               "                    if (s > best) best = s;\n"
               "                }\n"
               "                System.out.println(best);\n"
               "            }\n"
               "        }"),
         "        int[] pre = new int[n + 1];\n"
         "        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];\n"
         "        int q = sc.nextInt();\n"
         "        for (int t = 0; t < q; t++) {\n"
         "            int type = sc.nextInt();\n"
         "            if (type == 1) {\n"
         "                int l = sc.nextInt();\n"
         "                int r = sc.nextInt();\n"
         "                System.out.println(pre[r + 1] - pre[l]);\n"
         "            } else {\n"
         "                int k = sc.nextInt();\n"
         "                int best = pre[k] - pre[0];\n"
         "                for (int i = 0; i + k <= n; i++) {\n"
         "                    int s = pre[i + k] - pre[i];\n"
         "                    if (s > best) best = s;\n"
         "                }\n"
         "                System.out.println(best);\n"
         "            }\n"
         "        }",
         [_m5_case(a, qs)
          for (a, qs) in (([3, 1, 4, 1, 5], [[1, 0, 4], [1, 1, 3], [2, 2], [2, 5]]),
                          ([1, 2, 3], [[2, 1], [1, 0, 0], [2, 3]]),
                          ([-3, -1, -4, -1], [[2, 2], [1, 0, 3], [2, 1]]),
                          ([7], [[1, 0, 0], [2, 1]]),
                          ([2, -1, 2, -1, 2], [[2, 3], [1, 1, 3], [2, 5], [1, 4, 4]]))],
         hints=["Read the type first, then read only the operands that type needs — a `1` "
                "query has two, a `2` query has one.",
                "Range sum is `pre[r + 1] - pre[l]`.",
                "A window of length k starting at `i` sums to `pre[i + k] - pre[i]`, so loop "
                "`i` while `i + k <= n`.",
                "Seed `best` with the window at index 0 (`pre[k] - pre[0]`), never with 0 — "
                "the all-negative case is in the hidden tests.",
                "Build the prefix array once, outside the query loop; rebuilding it per query "
                "would defeat the whole exercise."]),
    example_io="stdin:  5\n        3 1 4 1 5\n        4\n        1 0 4\n        1 1 3\n"
               "        2 2\n        2 5\n\nstdout: 14\n        6\n        6\n        14",
    rubric=[
        "The prefix array is length `n + 1` with a leading 0, and is built once.",
        "Range sums use `pre[r + 1] - pre[l]` and are correct for `l = 0`.",
        "Window queries reuse the prefix array rather than re-summing each window.",
        "The window loop condition is `i + k <= n`, so it produces exactly `n - k + 1` windows.",
        "`best` is seeded from a real window, so all-negative input works.",
        "Each query prints on its own line, in input order.",
    ],
)


_MODULES.append(_jmod(
    5, 1, "Arrays, deeply",
    "Prefix sums, two pointers, sliding window",
    "The three patterns that collapse an O(n²) array answer into O(n): precompute the "
    "running totals, walk two indices under one rule, or maintain a window instead of "
    "rebuilding it.",
    """
This module closes Part 1. Everything in it is the same instinct wearing three
costumes: **do not recompute what you can carry forward**.

A prefix array carries every running total so a range question becomes one
subtraction. Two pointers carry the knowledge that the data is sorted, so one
comparison discards a whole row of possibilities. A sliding window carries the
current sum, so moving one step costs one addition and one subtraction instead
of a fresh loop.

Each one also has a precondition that makes it *wrong* rather than merely slow
when violated — prefix sums need an invertible operation, two pointers need
sorted data, sliding windows need positive values. The lessons put as much
weight on those preconditions as on the code, because that is the difference
between having memorised a pattern and understanding it.
""",
    _M5,
    capstone=_M5_CAP,
    objectives=[
        "Build a 1D prefix array with the leading zero and answer any range sum in O(1).",
        "Build a 2D prefix grid and query a rectangle with the four-term inclusion–exclusion formula.",
        "Solve pair-sum on a sorted array with two pointers, and justify each discard.",
        "Produce sorted squares in O(n) by filling the output from the back.",
        "Slide a fixed-size window with `a[i] - a[i - k]`, seeded from the first window.",
        "Grow and shrink a variable window, and say why two forward-only pointers make it O(n).",
        "State the precondition each pattern depends on, and what to use instead when it fails.",
    ],
    why="These three patterns are the difference between the O(n²) answer that ends an "
        "interview and the O(n) one that continues it. They also turn up constantly in "
        "real code — running totals in reports, rate limiters, image convolutions.",
    est_minutes=360,
    glossary=[
        _jg("prefix sum", "`pre[i]` = the sum of the first `i` elements, with `pre[0] = 0`. "
                          "Turns range sums into one subtraction."),
        _jg("range query", "A question about a contiguous slice — sum, min, count. Prefix "
                           "sums answer the invertible ones in O(1)."),
        _jg("inclusion–exclusion", "Add the overlapping parts, then subtract the part counted "
                                   "twice. The `- pre[r][c]` in the 2D build."),
        _jg("two pointers", "Two indices moving under one rule. Toward each other for pair "
                            "sums; both forward for windows."),
        _jg("monotonic", "Moving in one direction only. `left` and `right` are monotonic, "
                         "which is what makes a nested `while` still O(n)."),
        _jg("sliding window", "A contiguous range maintained incrementally — add the entering "
                              "element, subtract the leaving one."),
        _jg("fixed-size window", "A window of constant width k. Slides with "
                                 "`sum += a[i] - a[i - k]`."),
        _jg("variable-size window", "A window whose ends move independently under a validity "
                                    "condition, to find a shortest or longest range."),
        _jg("amortised", "Cheap on average across a whole run even if one step is expensive. "
                         "The shrink loop can run many times in one pass but at most n times "
                         "overall."),
        _jg("window length", "`right - left + 1` when both ends are inclusive. Write it once "
                             "rather than re-deriving it."),
    ],
    cheatsheet="""
```java
// --- 1D prefix sums -----------------------------------------------------
int[] pre = new int[n + 1];                       // n + 1, pre[0] = 0
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];

int sum = pre[r + 1] - pre[l];                    // a[l..r] inclusive
// check: l = 0, r = n-1  ->  pre[n] - pre[0]  =  the whole total

// --- 2D prefix sums -----------------------------------------------------
int[][] pre = new int[rows + 1][cols + 1];
pre[r+1][c+1] = m[r][c] + pre[r][c+1] + pre[r+1][c] - pre[r][c];

int sum = pre[r2+1][c2+1] - pre[r1][c2+1] - pre[r2+1][c1] + pre[r1][c1];

// --- two pointers, sorted array ----------------------------------------
int i = 0, j = n - 1;
while (i < j) {                                    // i < j: distinct slots
    int s = a[i] + a[j];
    if (s == target) { /* hit */ i++; j--; }
    else if (s < target) i++;                      // need more
    else j--;                                      // need less
}

// --- two pointers, fill from the back (sorted squares) -----------------
for (int p = n - 1; p >= 0; p--) {
    int L = a[i]*a[i], R = a[j]*a[j];
    if (L > R) { out[p] = L; i++; } else { out[p] = R; j--; }
}

// --- fixed-size window --------------------------------------------------
int sum = 0;
for (int i = 0; i < k; i++) sum += a[i];
int best = sum;                                    // seed from real data!
for (int i = k; i < n; i++) {
    sum += a[i] - a[i - k];                        // one in, one out
    if (sum > best) best = sum;
}
// windows: n - k + 1     window at right end i starts at i - k + 1

// --- variable window: SHORTEST with sum >= target (positive values) ----
int best = n + 1, sum = 0, left = 0;
for (int right = 0; right < n; right++) {
    sum += a[right];
    while (sum >= target) {                        // while VALID
        best = Math.min(best, right - left + 1);   // measure inside
        sum -= a[left]; left++;
    }
}

// --- variable window: LONGEST with sum <= target -----------------------
int best = 0, sum = 0, left = 0;
for (int right = 0; right < n; right++) {
    sum += a[right];
    while (sum > target && left <= right) {        // while INVALID
        sum -= a[left]; left++;
    }
    best = Math.max(best, right - left + 1);       // measure after
}
```
""",
    self_check=[
        "Can you write a prefix array and its query, and prove the formula with the `l = 0, r = n-1` check?",
        "Can you reproduce the 2D build and query, all eight `+1`s and all four signs?",
        "Can you justify, in one sentence, why the two-pointer pair search discards `a[i]` when the sum is too small?",
        "Can you explain why sorted squares fills the output backwards?",
        "Can you write the fixed-window slide and say which index just left the window?",
        "Can you explain why a nested `while` inside a `for` is still O(n) here?",
        "Can you name the precondition each of the three patterns needs, and what to use when it fails?",
    ],
    review=[
        _jq("Prefix array `pre` for `{2, 4, 6}`. What is `pre` and what is the sum of `a[1..2]`?",
            ["[0, 2, 6, 12] and 10", "[2, 6, 12] and 10", "[0, 2, 6, 12] and 6",
             "[0, 2, 4, 6] and 10"],
            0,
            "`pre` has n+1 entries starting at 0. The query is `pre[3] - pre[1]` = 12 − 2 = 10, "
            "which is 4 + 6."),
        _jq("Two-pointer pair search on `{5, 1, 9, 3}` (unsorted), target 8. What happens?",
            ["It may report no pair, even though 5 + 3 = 8 exists",
             "It finds the pair correctly",
             "It throws",
             "It finds it, but in O(n²)"],
            0,
            "The discards are only justified by sortedness. 5+3 sits in the middle of the "
            "array and the pointers can walk straight past it."),
        _jq("Fixed window, `n = 8, k = 3`, right end at `i = 5`. Which elements are in the window?",
            ["a[3], a[4], a[5]", "a[5], a[6], a[7]", "a[2], a[3], a[4]", "a[4], a[5], a[6]"],
            0,
            "The window is `i-k+1 .. i` = 3..5, and the element that just left is `a[i - k]` "
            "= a[2]."),
        _jq("A variable window over data containing negatives gives wrong answers because…",
            ["adding an element can decrease the sum, so shrinking is no longer justified",
             "the pointers can move backwards",
             "the sum overflows",
             "it doesn't — negatives are fine"],
            0,
            "The shrink rule assumes 'too big → remove from the left makes it smaller'. With "
            "negatives neither implication holds, and you need prefix sums plus a map."),
    ],
    milestone="Part 1 is done. You have the full array toolkit — traversal, grids, sorting, "
              "searching, rearranging, counting, prefix sums, two pointers and sliding "
              "windows — which between them cover the overwhelming majority of array "
              "questions you will ever be asked.",
))
