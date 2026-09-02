# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 5 practice - prefix sums, two pointers, sliding window.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[5]`.
#
# Module 5 scope: 1D and 2D prefix sums, range-sum queries, the two-pointer
# technique on sorted arrays, fixed and variable sliding windows. Arrays.sort is
# available (module 3). Still no String methods, no StringBuilder, no helper
# methods beside main, no recursion, no collections.
# ---------------------------------------------------------------------------


def _p5ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_ARR):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


_P_ARR = ([1, 2, 3, 4], [7], [-1, 2, -3, 4], [5, 5, 5, 5], [2, -1, 3, -2, 4])


def _prefix(a):
    """p[0] = 0, p[i+1] = p[i] + a[i]. Length n+1."""
    p = [0]
    for x in a:
        p.append(p[-1] + x)
    return p


# --- Family A - 1D prefix sums ----------------------------------------------

_RD_ARR_LR = _RD_ARR + ("        int l = sc.nextInt();\n"
                        "        int r = sc.nextInt();\n")


_P5_A = _jfam(
    "p5-prefix", "Prefix sums",
    "Pay O(n) once, answer every range in O(1).",
    """
A **prefix sum** array stores the running total: `p[i]` is the sum of the first
`i` elements. The convention that makes everything else easy is to give it
length `n + 1` and let `p[0]` be `0`:

```java
int[] p = new int[n + 1];
p[0] = 0;
for (int i = 0; i < n; i++) {
    p[i + 1] = p[i] + a[i];
}
```

Now the sum of **any** range is one subtraction:

```java
sum of a[l..r] (inclusive)  ==  p[r + 1] - p[l]
```

Building it costs O(n) once; every query afterwards is O(1). For `q` queries
that turns O(n·q) into O(n + q), which is the entire point.

**Why the extra leading zero matters.** Without it, a range starting at index 0
needs a special case (`l == 0 ? p[r] : p[r] - p[l-1]`). With it, `p[l]` is `0`
when `l` is `0` and the single formula covers everything. Off-by-one bugs in
prefix sums are almost always a missing `p[0] = 0`.

The `+ 1` in `p[r + 1]` is the other half: `p[k]` is the sum of the first `k`
elements — indices `0..k-1` — so to *include* index `r` you need `p[r + 1]`.
Say that out loud once and the formula stops being something to memorise.

> **Overflow.** Sums grow much faster than elements. Real prefix arrays are
> usually `long[]`. The cases here are small enough for `int`, but the habit is
> worth forming.
""",
    [
        _p5ex("j5-pr-build", "Build the prefix array", "Intro",
              "Build the prefix-sum array of length `n + 1` with `p[0] = 0`, then print "
              "it in `Arrays.toString` format.",
              """
        int[] p = new int[n + 1];
        for (int i = 0; i < n; i++) {
            p[i + 1] = p[i] + a[i];
        }
        System.out.println(Arrays.toString(p));
""",
              [_acase(list(a), _jarr(_prefix(a))) for a in _P_ARR],
              ["The prefix array is ONE LONGER than the input.",
               "`p[0]` is `0`, and Java has already put a zero there for you.",
               "Each next entry is the previous one plus the current element: "
               "`p[i + 1] = p[i] + a[i];`",
               "So the printed array always starts with `0` and ends with the total "
               "of everything."]),

        _p5ex("j5-pr-range", "Sum of one range", "Easy",
              "Read the array, then `l` and `r` (0-based, inclusive, always valid). "
              "Build a prefix array and print the sum of `a[l..r]` using one "
              "subtraction.",
              """
        int[] p = new int[n + 1];
        for (int i = 0; i < n; i++) {
            p[i + 1] = p[i] + a[i];
        }
        System.out.println(p[r + 1] - p[l]);
""",
              [_case(f"{len(a)}\n{_sp(a)}\n{l} {r}", sum(a[l:r + 1]))
               for (a, l, r) in (([1, 2, 3, 4], 1, 2), ([1, 2, 3, 4], 0, 3),
                                 ([7], 0, 0), ([-1, 2, -3, 4], 0, 1),
                                 ([2, -1, 3, -2, 4], 2, 4))],
              ["Build the prefix array first, exactly as in the previous variant.",
               "The range is INCLUSIVE of `r`, so you need the prefix one past it.",
               "`p[r + 1] - p[l]`.",
               "Because `p[0]` is `0`, a range starting at index `0` needs no special "
               "case — case two and case four both start there.",
               "Do not loop from `l` to `r` adding; the whole point is the O(1) "
               "answer."],
              read=_RD_ARR_LR),

        _p5ex("j5-pr-queries", "Answer many ranges", "Medium",
              "Read the array, then `q`, then `q` lines each holding an `l` and an `r` "
              "(0-based, inclusive). Print each range's sum on its own line. Build the "
              "prefix array once.",
              """
        int[] p = new int[n + 1];
        for (int i = 0; i < n; i++) {
            p[i + 1] = p[i] + a[i];
        }
        int q = sc.nextInt();
        for (int j = 0; j < q; j++) {
            int l = sc.nextInt();
            int r = sc.nextInt();
            System.out.println(p[r + 1] - p[l]);
        }
""",
              [_case(f"{len(a)}\n{_sp(a)}\n{len(qs)}\n"
                     + "\n".join(f"{l} {r}" for (l, r) in qs),
                     _nl(*[sum(a[l:r + 1]) for (l, r) in qs]))
               for (a, qs) in (([1, 2, 3, 4], [(0, 0), (1, 2), (0, 3)]),
                               ([7], [(0, 0)]),
                               ([-1, 2, -3, 4], [(0, 3), (2, 2)]),
                               ([5, 5, 5, 5], [(1, 3), (0, 1), (2, 2), (0, 3)]),
                               ([2, -1, 3, -2, 4], [(1, 3)]))],
              ["Build the prefix array ONCE, before reading the queries — that is "
               "the whole saving.",
               "Then each query is a single subtraction and a `println`.",
               "`q` is read after the array, and each query is two more integers.",
               "This is O(n + q) instead of O(n * q). With a large `q` the difference "
               "is the difference between passing and timing out."],
              read=_RD_ARR),

        _p5ex("j5-pr-equilibrium", "The balance point", "Medium",
              "Print the smallest index `i` where the sum of everything strictly before "
              "`i` equals the sum of everything strictly after `i`. Print `-1` if there "
              "is no such index.",
              """
        int total = 0;
        for (int i = 0; i < n; i++) {
            total += a[i];
        }
        int left = 0;
        int answer = -1;
        for (int i = 0; i < n; i++) {
            int right = total - left - a[i];
            if (left == right && answer == -1) {
                answer = i;
            }
            left += a[i];
        }
        System.out.println(answer);
""",
              [_acase(list(a), next((i for i in range(len(a))
                                     if sum(a[:i]) == sum(a[i + 1:])), -1))
               for a in ([1, 2, 3, 3], [7], [1, 2, 3], [0, 0, 0], [-1, 2, -3, 4])],
              ["You do not need a whole prefix array — a running left sum is enough.",
               "Get the grand total in a first pass.",
               "Then for each `i`, the right-hand sum is "
               "`total - left - a[i]` — everything that is neither counted on the "
               "left nor the element itself.",
               "Update `left` AFTER the comparison, not before.",
               "A single element has empty sums on both sides, so index `0` is a "
               "balance point — case two answers `0`.",
               "Guard with `answer == -1` so the smallest index wins."]),

        _p5ex("j5-pr-max-subarray", "Best contiguous run", "Hard",
              "Print the largest sum obtainable from any non-empty contiguous "
              "subarray. Values may be negative.",
              """
        int best = a[0];
        int here = a[0];
        for (int i = 1; i < n; i++) {
            if (here < 0) {
                here = a[i];
            } else {
                here = here + a[i];
            }
            if (here > best) {
                best = here;
            }
        }
        System.out.println(best);
""",
              [_acase(list(a), max(sum(a[i:j])
                                   for i in range(len(a))
                                   for j in range(i + 1, len(a) + 1)))
               for a in ([1, 2, 3, 4], [7], [-1, 2, -3, 4], [-5, -2, -9],
                         [2, -1, 3, -2, 4])],
              ["This is Kadane's algorithm, and it is the single most-asked array "
               "question there is.",
               "Carry two things: the best sum ending exactly HERE, and the best "
               "seen anywhere.",
               "At each step, either extend the previous run or start fresh at "
               "`a[i]` — and starting fresh is right exactly when the previous run "
               "had gone negative.",
               "Seed BOTH with `a[0]`, never with `0`. Case four is all negative, "
               "and a `0` seed would wrongly answer `0` for a subarray that must be "
               "non-empty.",
               "Update `best` after updating `here`, every iteration.",
               "It is O(n) with O(1) space; the prefix-sum route would be O(n^2)."]),
    ])


# --- Family B - 2D prefix sums ----------------------------------------------

def _prefix2(m):
    r, c = len(m), len(m[0])
    p = [[0] * (c + 1) for _ in range(r + 1)]
    for i in range(r):
        for j in range(c):
            p[i + 1][j + 1] = m[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j]
    return p


def _sub_sum(m, r1, c1, r2, c2):
    return sum(m[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))


_M5 = ([[1, 2], [3, 4]],
       [[5]],
       [[1, 2, 3], [4, 5, 6]],
       [[-1, 2], [3, -4]],
       [[1, 1, 1], [1, 1, 1], [1, 1, 1]])


_P5_B = _jfam(
    "p5-prefix2d", "Prefix sums in two dimensions",
    "Inclusion and exclusion on a grid.",
    """
The same idea one dimension up. `p[i][j]` holds the sum of the whole rectangle
from `(0,0)` to `(i-1, j-1)` — again with a zero row and a zero column so no
query needs a special case.

Building it uses **inclusion-exclusion**: the rectangle above plus the rectangle
to the left double-counts their overlap, so subtract it back out once.

```java
int[][] p = new int[rows + 1][cols + 1];
for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
        p[i + 1][j + 1] = m[i][j]
                        + p[i][j + 1]      // everything above
                        + p[i + 1][j]      // everything to the left
                        - p[i][j];         // the overlap, counted twice
    }
}
```

Querying reverses the same reasoning. The sum of the rectangle with corners
`(r1,c1)` and `(r2,c2)`, both inclusive, is:

```java
p[r2 + 1][c2 + 1]
  - p[r1][c2 + 1]        // strip above
  - p[r2 + 1][c1]        // strip to the left
  + p[r1][c1];           // that corner was removed twice, so add it back
```

**The `+ p[r1][c1]` is the step everyone forgets.** Draw the four rectangles
once on paper and the sign pattern stops being arbitrary: two subtractions
overlap in the top-left block, so it comes off twice and has to go back on once.

Build is O(rows·cols); every query afterwards is O(1), whatever its size.
""",
    [
        _p5ex("j5-pr-2d-build", "Build the 2D prefix grid", "Medium",
              "Build the `(rows+1) x (cols+1)` prefix grid with a zero first row and "
              "column, then print it in `Arrays.deepToString` format.",
              """
        int[][] p = new int[rows + 1][cols + 1];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                p[i + 1][j + 1] = m[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j];
            }
        }
        System.out.println(Arrays.deepToString(p));
""",
              [_mcase(m, _jdeep(_prefix2(m))) for m in _M5],
              ["The prefix grid has one extra row AND one extra column.",
               "Java zeroes them for you, so row 0 and column 0 are already right.",
               "Each cell is its own value, plus the cell above, plus the cell to "
               "the left, minus the one diagonally up-left.",
               "That last subtraction removes the overlap the two additions "
               "double-counted.",
               "Print with `deepToString`, since this is a 2D array."],
              read=_RD_MAT),

        _p5ex("j5-pr-2d-query", "Sum of one rectangle", "Medium",
              "Read the grid, then `r1 c1 r2 c2` — the top-left and bottom-right "
              "corners, both inclusive and always valid. Print the sum of that "
              "rectangle using a prefix grid.",
              """
        int[][] p = new int[rows + 1][cols + 1];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                p[i + 1][j + 1] = m[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j];
            }
        }
        System.out.println(p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1]);
""",
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m)
                     + f"\n{r1} {c1} {r2} {c2}", _sub_sum(m, r1, c1, r2, c2))
               for (m, r1, c1, r2, c2) in (([[1, 2], [3, 4]], 0, 0, 1, 1),
                                           ([[1, 2], [3, 4]], 1, 1, 1, 1),
                                           ([[5]], 0, 0, 0, 0),
                                           ([[1, 2, 3], [4, 5, 6]], 0, 1, 1, 2),
                                           ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 1, 0, 2, 1))],
              ["Build the prefix grid first.",
               "Both corners are inclusive, so the bottom-right prefix index is "
               "`[r2 + 1][c2 + 1]`.",
               "Subtract the strip above, `p[r1][c2 + 1]`, and the strip to the "
               "left, `p[r2 + 1][c1]`.",
               "Then ADD BACK `p[r1][c1]`, which those two subtractions both "
               "removed.",
               "Case three is a single cell, and the formula still works."],
              read=_RD_MAT + "        int r1 = sc.nextInt();\n"
                             "        int c1 = sc.nextInt();\n"
                             "        int r2 = sc.nextInt();\n"
                             "        int c2 = sc.nextInt();\n"),

        _p5ex("j5-pr-2d-row-band", "Sum of a band of rows", "Easy",
              "Read the grid, then `r1` and `r2` (inclusive). Print the total of every "
              "cell in rows `r1` through `r2`.",
              """
        int[][] p = new int[rows + 1][cols + 1];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                p[i + 1][j + 1] = m[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j];
            }
        }
        System.out.println(p[r2 + 1][cols] - p[r1][cols]);
""",
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m)
                     + f"\n{r1} {r2}", _sub_sum(m, r1, 0, r2, len(m[0]) - 1))
               for (m, r1, r2) in (([[1, 2], [3, 4]], 0, 1), ([[1, 2], [3, 4]], 1, 1),
                                   ([[5]], 0, 0), ([[1, 2, 3], [4, 5, 6]], 0, 0),
                                   ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 1, 2))],
              ["A band of full rows is just a rectangle whose columns span "
               "everything.",
               "So `c1` is `0` and `c2` is `cols - 1`.",
               "Substituting those into the four-term formula collapses two terms to "
               "zero, because column `0` of the prefix grid is all zeros.",
               "What is left is `p[r2 + 1][cols] - p[r1][cols]` — exactly the 1D "
               "formula, applied to row totals."],
              read=_RD_MAT + "        int r1 = sc.nextInt();\n"
                             "        int r2 = sc.nextInt();\n"),

        _p5ex("j5-pr-2d-square", "Sum of a k-by-k square", "Medium",
              "Read the grid, then `k`, then `r` and `c` — the top-left corner of a "
              "`k x k` square that always fits. Print its total.",
              """
        int[][] p = new int[rows + 1][cols + 1];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                p[i + 1][j + 1] = m[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j];
            }
        }
        System.out.println(p[r + k][c + k] - p[r][c + k] - p[r + k][c] + p[r][c]);
""",
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m)
                     + f"\n{k}\n{r} {c}", _sub_sum(m, r, c, r + k - 1, c + k - 1))
               for (m, k, r, c) in (([[1, 2], [3, 4]], 2, 0, 0),
                                    ([[1, 2], [3, 4]], 1, 1, 0),
                                    ([[5]], 1, 0, 0),
                                    ([[1, 2, 3], [4, 5, 6]], 2, 0, 1),
                                    ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], 3, 0, 0))],
              ["A `k x k` square at `(r, c)` has its bottom-right corner at "
               "`(r + k - 1, c + k - 1)`.",
               "Plugging that into the inclusive formula turns every `+ 1` into "
               "`+ k`, which is why this version looks tidier than the general one.",
               "`p[r + k][c + k] - p[r][c + k] - p[r + k][c] + p[r][c]`.",
               "Case one is the whole 2x2 grid; case five the whole 3x3."],
              read=_RD_MAT + "        int k = sc.nextInt();\n"
                             "        int r = sc.nextInt();\n"
                             "        int c = sc.nextInt();\n"),

        _p5ex("j5-pr-2d-best-square", "The heaviest k-by-k square", "Hard",
              "Read the grid, then `k` (which always fits). Print the largest total of "
              "any `k x k` square in the grid.",
              """
        int[][] p = new int[rows + 1][cols + 1];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                p[i + 1][j + 1] = m[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j];
            }
        }
        int best = p[k][k] - p[0][k] - p[k][0] + p[0][0];
        for (int r = 0; r + k <= rows; r++) {
            for (int c = 0; c + k <= cols; c++) {
                int sum = p[r + k][c + k] - p[r][c + k] - p[r + k][c] + p[r][c];
                if (sum > best) {
                    best = sum;
                }
            }
        }
        System.out.println(best);
""",
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m)
                     + f"\n{k}",
                     max(_sub_sum(m, r, c, r + k - 1, c + k - 1)
                         for r in range(len(m) - k + 1)
                         for c in range(len(m[0]) - k + 1)))
               for (m, k) in (([[1, 2], [3, 4]], 1), ([[1, 2], [3, 4]], 2),
                              ([[5]], 1), ([[1, 2, 3], [4, 5, 6]], 2),
                              ([[-1, 2], [3, -4]], 1))],
              ["Build the prefix grid once, then every candidate square costs O(1).",
               "The top-left corner can be any `(r, c)` with `r + k <= rows` and "
               "`c + k <= cols`.",
               "Seed `best` with the square at `(0, 0)` — never with `0`, since "
               "case five has an all-negative option and a genuine answer of `3`.",
               "Reuse the same four-term formula inside the loop.",
               "Without prefix sums this would be O(rows * cols * k^2); with them it "
               "is O(rows * cols)."],
              read=_RD_MAT + "        int k = sc.nextInt();\n"),
    ])


# --- Family C - two pointers on sorted arrays --------------------------------

_SORTED = ([1, 2, 3, 4, 6], [7], [1, 1, 2, 2], [-3, -1, 0, 2, 5], [2, 4])


def _two_sum_pair(a, k):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        s = a[lo] + a[hi]
        if s == k:
            return (lo, hi)
        if s < k:
            lo += 1
        else:
            hi -= 1
    return None


_P5_C = _jfam(
    "p5-twopointer", "Two pointers on sorted data",
    "One from each end, and the sum tells you which to move.",
    """
When an array is **sorted**, a pair search does not need two nested loops. Start
one pointer at each end and let the comparison decide which one moves:

```java
int lo = 0, hi = n - 1;
while (lo < hi) {
    int sum = a[lo] + a[hi];
    if (sum == k) { ...found... break; }
    if (sum < k) lo++;      // need MORE  -> raise the small end
    else         hi--;      // need LESS  -> lower the big end
}
```

**Why moving is safe** is the part worth being able to say out loud. If
`a[lo] + a[hi] < k`, then `a[lo]` paired with *anything* still available is also
too small — `a[hi]` is the largest thing left. So `a[lo]` cannot be part of any
solution and discarding it loses nothing. That argument is the whole proof, and
it is what interviewers want to hear.

The result is O(n) after sorting, against O(n²) for the nested loop, with O(1)
extra space.

**The precondition is sortedness**, so on unsorted input you sort first — which
costs O(n log n) and makes the whole thing O(n log n). (A hash set does it in
O(n) without sorting, but that is Part 6.)

Every array in this family arrives already sorted ascending.
""",
    [
        _p5ex("j5-pr-pair-exists", "Is there a pair?", "Easy",
              "The array is sorted ascending. Read it, then `k`. Print `true` if some "
              "two **different** positions hold values summing to `k`, `false` "
              "otherwise.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n - 1;
        boolean found = false;
        while (lo < hi) {
            int sum = a[lo] + a[hi];
            if (sum == k) {
                found = true;
                break;
            }
            if (sum < k) {
                lo++;
            } else {
                hi--;
            }
        }
        System.out.println(found);
""",
              [_akcase(a, k, _jbool(_two_sum_pair(a, k) is not None))
               for (a, k) in (([1, 2, 3, 4, 6], 10), ([1, 2, 3, 4, 6], 11),
                              ([7], 14), ([1, 1, 2, 2], 2),
                              ([-3, -1, 0, 2, 5], 2))],
              ["Do not use nested loops — the array being sorted is the whole gift.",
               "`lo` starts at `0`, `hi` at `n - 1`, and the loop runs while "
               "`lo < hi`.",
               "Too small a sum means the small end must rise: `lo++`. Too large "
               "means the big end must fall: `hi--`.",
               "`lo < hi` (not `<=`) is what enforces 'two different positions' — "
               "case three cannot pair `7` with itself and must print `false`.",
               "Case four pairs the two `1`s, which are different positions holding "
               "equal values, so `true`."]),

        _p5ex("j5-pr-pair-indices", "Which two?", "Easy",
              "Same input. Print the two indices whose values sum to `k`, smaller index "
              "first, separated by a space. Print `-1 -1` if there is no such pair. If "
              "several pairs work, print the one this two-pointer walk finds first.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n - 1;
        int foundLo = -1;
        int foundHi = -1;
        while (lo < hi) {
            int sum = a[lo] + a[hi];
            if (sum == k) {
                foundLo = lo;
                foundHi = hi;
                break;
            }
            if (sum < k) {
                lo++;
            } else {
                hi--;
            }
        }
        System.out.println(foundLo + " " + foundHi);
""",
              [_akcase(a, k, (lambda pr: f"{pr[0]} {pr[1]}" if pr else "-1 -1")(
                  _two_sum_pair(a, k)))
               for (a, k) in (([1, 2, 3, 4, 6], 10), ([1, 2, 3, 4, 6], 11),
                              ([7], 14), ([1, 1, 2, 2], 3),
                              ([-3, -1, 0, 2, 5], 2))],
              ["Identical walk, but remember WHERE the pointers were when they hit.",
               "Two `-1` accumulators, so 'never found' prints `-1 -1`.",
               "`break` on the first hit so the recorded pair is the first one this "
               "walk reaches.",
               "`lo` is always the smaller index by construction, so no ordering "
               "work is needed at the end."]),

        _p5ex("j5-pr-count-pairs", "How many pairs?", "Medium",
              "Same input. Print how many **index pairs** `(i, j)` with `i < j` have "
              "`a[i] + a[j] == k`. Duplicate values count separately.",
              """
        int k = sc.nextInt();
        int count = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (a[i] + a[j] == k) {
                    count++;
                }
            }
        }
        System.out.println(count);
""",
              [_akcase(a, k, sum(1 for i in range(len(a)) for j in range(i + 1, len(a))
                                 if a[i] + a[j] == k))
               for (a, k) in (([1, 2, 3, 4, 6], 7), ([1, 1, 2, 2], 3),
                              ([7], 14), ([1, 1, 1, 1], 2),
                              ([-3, -1, 0, 2, 5], 2))],
              ["Counting every pair is the one job the simple two-pointer walk does "
               "NOT do directly — with duplicates it would need careful block "
               "counting.",
               "The honest O(n^2) double loop is the right answer at this stage, and "
               "saying so is part of the skill.",
               "Inner loop starts at `j = i + 1`, which enforces `i < j` and stops "
               "each pair being counted twice.",
               "Case four is four `1`s summing to `2`, giving all six pairs.",
               "Knowing WHEN the clever technique does not apply is as useful as "
               "knowing the technique."]),

        _p5ex("j5-pr-closest", "Closest to the target", "Hard",
              "Same input, and `n >= 2`. Print the pair sum that comes closest to `k`. "
              "If two sums are equally close, print the smaller one.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n - 1;
        int best = a[0] + a[1];
        while (lo < hi) {
            int sum = a[lo] + a[hi];
            int d = sum - k;
            if (d < 0) {
                d = -d;
            }
            int bd = best - k;
            if (bd < 0) {
                bd = -bd;
            }
            if (d < bd || (d == bd && sum < best)) {
                best = sum;
            }
            if (sum < k) {
                lo++;
            } else {
                hi--;
            }
        }
        System.out.println(best);
""",
              [_akcase(a, k, min((abs(a[i] + a[j] - k), a[i] + a[j])
                                 for i in range(len(a))
                                 for j in range(i + 1, len(a)))[1])
               for (a, k) in (([1, 2, 3, 4, 6], 11), ([1, 2, 3, 4, 6], 5),
                              ([2, 4], 100), ([1, 1, 2, 2], 3),
                              ([-3, -1, 0, 2, 5], 0))],
              ["The same walk, but instead of stopping on an exact hit you track the "
               "closest sum seen.",
               "Distance is `|sum - k|`; without `Math.abs` (fine to use, but easy "
               "to write) just negate when negative.",
               "Seed `best` with a real pair — `a[0] + a[1]` — never with `0`.",
               "The tie rule needs an explicit second clause: replace when strictly "
               "closer, OR equally close and smaller.",
               "Keep moving the pointers by the same rule as before, even after "
               "updating `best`.",
               "Case five has sums equally distant from `0` on either side, so the "
               "tie rule decides."]),

        _p5ex("j5-pr-merge", "Merge two sorted arrays", "Medium",
              "Both arrays arrive sorted ascending. Merge them into one sorted array "
              "and print it in `Arrays.toString` format. Do not call `Arrays.sort` — "
              "walk both with one pointer each.",
              """
        int[] out = new int[n + m];
        int i = 0;
        int j = 0;
        int w = 0;
        while (i < n && j < m) {
            if (a[i] <= b[j]) {
                out[w] = a[i];
                i++;
            } else {
                out[w] = b[j];
                j++;
            }
            w++;
        }
        while (i < n) {
            out[w] = a[i];
            i++;
            w++;
        }
        while (j < m) {
            out[w] = b[j];
            j++;
            w++;
        }
        System.out.println(Arrays.toString(out));
""",
              [_a2case(a, b, _jarr(sorted(list(a) + list(b))))
               for (a, b) in (([1, 3, 5], [2, 4, 6]), ([1, 2], [3, 4]),
                              ([5], [1]), ([1, 1], [1, 1]),
                              ([-3, 0], [-1, 2, 5]))],
              ["Two read pointers, one write pointer — this is the merge step of "
               "merge sort.",
               "The main loop runs only while BOTH still have elements.",
               "Take whichever front value is smaller. Using `<=` rather than `<` "
               "keeps equal values in their original relative order, which is what "
               "makes merge sort stable.",
               "When one runs out, the other's remainder is already sorted — drain "
               "it with two follow-up loops.",
               "Exactly one of those two loops will actually run.",
               "Total cost is O(n + m), where sorting the concatenation would be "
               "O((n+m) log(n+m))."],
              read=_RD_ARR2),
    ])


# --- Family D - fixed-size sliding window ------------------------------------

def _win_sums(a, k):
    return [sum(a[i:i + k]) for i in range(len(a) - k + 1)]


_W_CASES = (([1, 2, 3, 4], 2), ([7], 1), ([1, 2, 3, 4, 5], 3),
            ([5, 5, 5, 5], 2), ([-1, 2, -3, 4], 2))


_P5_D = _jfam(
    "p5-window", "The fixed-size sliding window",
    "Add the one entering, subtract the one leaving.",
    """
To find the best sum among all windows of width `k`, the naive route re-adds `k`
values for every position — O(n·k). But consecutive windows overlap in `k - 1`
elements, and recomputing what you already know is the waste:

```java
int sum = 0;
for (int i = 0; i < k; i++) sum += a[i];      // the first window, in full
int best = sum;

for (int i = k; i < n; i++) {
    sum += a[i];                               // the element entering
    sum -= a[i - k];                           // the element leaving
    if (sum > best) best = sum;
}
```

O(n), one pass, O(1) extra space.

**The index that goes wrong is `i - k`.** When the window's new right edge is
`i`, the window covers `a[i-k+1 .. i]`, so the element that just fell off the
left is `a[i - k]`. Check it on a small case rather than trusting it: with
`k = 2` and `i = 2`, the window is `a[1..2]` and the departed element is `a[0]`.

**Seed with the first window, not with zero.** Same reason as every running
maximum so far: negative data. Case five in each variant is there to catch it.

The loop starts at `i = k`, because windows `0..k-1` were consumed building the
first sum.
""",
    [
        _p5ex("j5-pr-win-max", "Best window", "Medium",
              "Read the array, then the window width `k` (always between `1` and `n`). "
              "Print the largest sum of any `k` consecutive elements.",
              """
        int k = sc.nextInt();
        int sum = 0;
        for (int i = 0; i < k; i++) {
            sum += a[i];
        }
        int best = sum;
        for (int i = k; i < n; i++) {
            sum += a[i];
            sum -= a[i - k];
            if (sum > best) {
                best = sum;
            }
        }
        System.out.println(best);
""",
              [_akcase(a, k, max(_win_sums(a, k))) for (a, k) in _W_CASES],
              ["Build the FIRST window's sum with its own small loop.",
               "Seed `best` from that sum — case five is partly negative and a `0` "
               "seed would be wrong.",
               "Then slide: the entering element is `a[i]`, the leaving one is "
               "`a[i - k]`.",
               "Start the sliding loop at `i = k`.",
               "When `k == n` there is only one window and the loop never runs, "
               "which is correct."]),

        _p5ex("j5-pr-win-min", "Worst window", "Easy",
              "Same input. Print the **smallest** sum of any `k` consecutive elements.",
              """
        int k = sc.nextInt();
        int sum = 0;
        for (int i = 0; i < k; i++) {
            sum += a[i];
        }
        int best = sum;
        for (int i = k; i < n; i++) {
            sum += a[i];
            sum -= a[i - k];
            if (sum < best) {
                best = sum;
            }
        }
        System.out.println(best);
""",
              [_akcase(a, k, min(_win_sums(a, k))) for (a, k) in _W_CASES],
              ["Identical to the previous variant with one operator flipped.",
               "The sliding arithmetic does not change at all — only the comparison "
               "does.",
               "Still seed from the first window.",
               "This is the same point family B of module 1 made: direction is one "
               "character, not a new algorithm."]),

        _p5ex("j5-pr-win-all", "Every window sum", "Easy",
              "Same input. Print the sum of each window in left-to-right order, "
              "separated by single spaces, on one line.",
              """
        int k = sc.nextInt();
        int sum = 0;
        for (int i = 0; i < k; i++) {
            sum += a[i];
        }
        System.out.print(sum + " ");
        for (int i = k; i < n; i++) {
            sum += a[i];
            sum -= a[i - k];
            System.out.print(sum + " ");
        }
        System.out.println();
""",
              [_akcase(a, k, _sp(_win_sums(a, k))) for (a, k) in _W_CASES],
              ["There are exactly `n - k + 1` windows, so that many numbers get "
               "printed.",
               "Print the first window's sum before the sliding loop starts.",
               "Then print once per slide.",
               "Use `System.out.print` with a trailing space and finish with a bare "
               "`println()`.",
               "Case two has `k == n`, so only one number is printed."]),

        _p5ex("j5-pr-win-count", "Windows over the line", "Medium",
              "Read the array, then `k`, then a threshold `t`. Print how many windows "
              "of width `k` have a sum **strictly greater** than `t`.",
              """
        int k = sc.nextInt();
        int t = sc.nextInt();
        int sum = 0;
        for (int i = 0; i < k; i++) {
            sum += a[i];
        }
        int count = 0;
        if (sum > t) {
            count++;
        }
        for (int i = k; i < n; i++) {
            sum += a[i];
            sum -= a[i - k];
            if (sum > t) {
                count++;
            }
        }
        System.out.println(count);
""",
              [_case(f"{len(a)}\n{_sp(a)}\n{k}\n{t}",
                     sum(1 for s in _win_sums(a, k) if s > t))
               for (a, k, t) in (([1, 2, 3, 4], 2, 4), ([7], 1, 7),
                                 ([1, 2, 3, 4, 5], 3, 8), ([5, 5, 5, 5], 2, 100),
                                 ([-1, 2, -3, 4], 2, 0))],
              ["Do not forget to test the FIRST window before the sliding loop — it "
               "is a window too.",
               "That is the single most common bug in this shape: `n - k` windows "
               "counted instead of `n - k + 1`.",
               "Strictly greater is `>`. Case two has a window sum exactly equal to "
               "`t` and must count `0`.",
               "Case four has a threshold nothing reaches, so `0` again."]),

        _p5ex("j5-pr-win-where", "Where is the best window?", "Medium",
              "Same input as the first variant. Print the **starting index** of the "
              "window with the largest sum. On a tie, print the leftmost such window.",
              """
        int k = sc.nextInt();
        int sum = 0;
        for (int i = 0; i < k; i++) {
            sum += a[i];
        }
        int best = sum;
        int bestStart = 0;
        for (int i = k; i < n; i++) {
            sum += a[i];
            sum -= a[i - k];
            if (sum > best) {
                best = sum;
                bestStart = i - k + 1;
            }
        }
        System.out.println(bestStart);
""",
              [_akcase(a, k, _win_sums(a, k).index(max(_win_sums(a, k))))
               for (a, k) in _W_CASES],
              ["Track the start index alongside the best sum.",
               "When the right edge is `i`, the window starts at `i - k + 1`. Check "
               "it: with `k = 2` and `i = 2`, the window is `a[1..2]`, so the start "
               "is `1`.",
               "Seed `bestStart` at `0`, the first window.",
               "A strict `>` keeps the leftmost of equal-scoring windows — case four "
               "is all fives and must answer `0`."]),
    ])


# --- Family E - variable-size sliding window ---------------------------------

def _shortest_at_least(a, t):
    best = 0
    s = 0
    lo = 0
    for hi in range(len(a)):
        s += a[hi]
        while s >= t:
            width = hi - lo + 1
            if best == 0 or width < best:
                best = width
            s -= a[lo]
            lo += 1
    return best


def _longest_at_most(a, t):
    best = 0
    s = 0
    lo = 0
    for hi in range(len(a)):
        s += a[hi]
        while s > t and lo <= hi:
            s -= a[lo]
            lo += 1
        if s <= t:
            best = max(best, hi - lo + 1)
    return best


def _count_at_most(a, t):
    total = 0
    s = 0
    lo = 0
    for hi in range(len(a)):
        s += a[hi]
        while s > t and lo <= hi:
            s -= a[lo]
            lo += 1
        total += hi - lo + 1
    return total


_POS = ([2, 3, 1, 2, 4], [7], [1, 1, 1, 1], [5, 1, 3], [4, 2, 2, 1, 3])


def _longest_run(a, keep_going):
    """Longest run where `keep_going(prev, cur)` holds between neighbours."""
    best = 1
    run = 1
    for i in range(1, len(a)):
        run = run + 1 if keep_going(a[i - 1], a[i]) else 1
        best = max(best, run)
    return best


_P5_E = _jfam(
    "p5-varwindow", "The variable-size window",
    "Grow on the right, shrink on the left.",
    """
When the window's width is not fixed but its *contents* must satisfy a
condition, the shape changes: the right edge always advances, and the left edge
catches up only as far as it must.

```java
int lo = 0, sum = 0, best = 0;
for (int hi = 0; hi < n; hi++) {
    sum += a[hi];                       // grow right
    while (sum > t) {                   // shrink left until legal again
        sum -= a[lo];
        lo++;
    }
    // a[lo..hi] is now the longest legal window ending at hi
    if (hi - lo + 1 > best) best = hi - lo + 1;
}
```

**This is O(n), not O(n²)**, even though there is a loop inside a loop. Each
index enters the window once and leaves at most once, so the inner `while` runs
at most `n` times *in total* across the whole outer loop. Being able to give
that amortised argument is the point of the technique.

**It relies on the values being non-negative.** Extending the window then only
ever *increases* the sum, which is what makes "shrink until legal" correct. With
negative values the property breaks and you need prefix sums plus a map instead.
Every array in this family is positive for exactly that reason.

**The window width is `hi - lo + 1`.** Get that wrong by one and every answer is
wrong by one. Check it when `lo == hi`: one element, and the formula gives `1`.
""",
    [
        _p5ex("j5-pr-shortest", "Shortest run that reaches the target", "Hard",
              "All values are positive. Read the array, then `t`. Print the length of "
              "the shortest contiguous run whose sum is **at least** `t`, or `0` if no "
              "run reaches it.",
              """
        int t = sc.nextInt();
        int lo = 0;
        int sum = 0;
        int best = 0;
        for (int hi = 0; hi < n; hi++) {
            sum += a[hi];
            while (sum >= t) {
                int width = hi - lo + 1;
                if (best == 0 || width < best) {
                    best = width;
                }
                sum -= a[lo];
                lo++;
            }
        }
        System.out.println(best);
""",
              [_akcase(a, t, _shortest_at_least(a, t))
               for (a, t) in (([2, 3, 1, 2, 4], 7), ([7], 7), ([1, 1, 1, 1], 100),
                              ([5, 1, 3], 5), ([4, 2, 2, 1, 3], 8))],
              ["Grow the window by adding `a[hi]` every iteration.",
               "Then, while the window is already good enough, record its width and "
               "shrink from the left — a shorter window might still qualify.",
               "The shrink loop is `while`, not `if`: several elements may need to "
               "leave.",
               "`best == 0` doubles as 'nothing found yet', which is why the guard "
               "reads `best == 0 || width < best`.",
               "Case three can never reach the target and must print `0`.",
               "Width is `hi - lo + 1`."]),

        _p5ex("j5-pr-longest", "Longest run under the limit", "Hard",
              "All values are positive. Read the array, then `t`. Print the length of "
              "the longest contiguous run whose sum is **at most** `t`. Print `0` if "
              "even a single element exceeds `t`.",
              """
        int t = sc.nextInt();
        int lo = 0;
        int sum = 0;
        int best = 0;
        for (int hi = 0; hi < n; hi++) {
            sum += a[hi];
            while (sum > t && lo <= hi) {
                sum -= a[lo];
                lo++;
            }
            if (sum <= t && hi - lo + 1 > best) {
                best = hi - lo + 1;
            }
        }
        System.out.println(best);
""",
              [_akcase(a, t, _longest_at_most(a, t))
               for (a, t) in (([2, 3, 1, 2, 4], 7), ([7], 7), ([1, 1, 1, 1], 100),
                              ([5, 1, 3], 2), ([4, 2, 2, 1, 3], 5))],
              ["The mirror of the previous one: shrink only while the window is "
               "ILLEGAL, then measure.",
               "The shrink guard needs `lo <= hi` as well, so a single element bigger "
               "than `t` can empty the window instead of running off the end.",
               "After shrinking, the window may be empty — check `sum <= t` before "
               "recording.",
               "Case four has every element or pair over the limit except `1`, so "
               "the answer is `1`.",
               "Case three fits everything and answers `4`."]),

        _p5ex("j5-pr-count-windows", "How many runs stay under?", "Hard",
              "All values are positive. Read the array, then `t`. Print how many "
              "contiguous non-empty runs have a sum of at most `t`.",
              """
        int t = sc.nextInt();
        int lo = 0;
        int sum = 0;
        int total = 0;
        for (int hi = 0; hi < n; hi++) {
            sum += a[hi];
            while (sum > t && lo <= hi) {
                sum -= a[lo];
                lo++;
            }
            total += hi - lo + 1;
        }
        System.out.println(total);
""",
              [_akcase(a, t, _count_at_most(a, t))
               for (a, t) in (([2, 3, 1, 2, 4], 7), ([7], 7), ([1, 1, 1, 1], 100),
                              ([5, 1, 3], 2), ([4, 2, 2, 1, 3], 5))],
              ["The counting trick: once `a[lo..hi]` is the longest legal window "
               "ending at `hi`, EVERY suffix of it is also legal.",
               "There are exactly `hi - lo + 1` such runs ending at `hi`.",
               "So add that width to a running total each iteration, instead of "
               "tracking a maximum.",
               "That converts an O(n^2) enumeration into O(n).",
               "When the window is empty the width is `0`, which correctly "
               "contributes nothing."]),

        _p5ex("j5-pr-longest-equal", "Longest run of one value", "Easy",
              "Print the length of the longest run of consecutive equal values.",
              """
        int best = 1;
        int run = 1;
        for (int i = 1; i < n; i++) {
            if (a[i] == a[i - 1]) {
                run++;
            } else {
                run = 1;
            }
            if (run > best) {
                best = run;
            }
        }
        System.out.println(best);
""",
              [_acase(list(a), _longest_run(a, lambda p, c: p == c))
               for a in ([1, 1, 2, 2, 2], [7], [1, 2, 3], [4, 4, 4, 4],
                         [1, 1, 2, 1, 1, 1])],
              ["A run only ever extends from the element immediately before, so a "
               "single pass with two counters is enough.",
               "`run` resets to `1`, not `0`, when the value changes — the current "
               "element already starts a new run.",
               "Seed both `best` and `run` at `1`, which is also the right answer "
               "for a one-element array.",
               "Update `best` every iteration, after adjusting `run`.",
               "Case five's longest run is the three `1`s at the end, not the two at "
               "the start."]),

        _p5ex("j5-pr-longest-increasing", "Longest climb", "Medium",
              "Print the length of the longest strictly increasing contiguous run.",
              """
        int best = 1;
        int run = 1;
        for (int i = 1; i < n; i++) {
            if (a[i] > a[i - 1]) {
                run++;
            } else {
                run = 1;
            }
            if (run > best) {
                best = run;
            }
        }
        System.out.println(best);
""",
              [_acase(list(a), _longest_run(a, lambda p, c: c > p))
               for a in ([1, 2, 3, 1], [7], [3, 2, 1], [1, 2, 2, 3, 4],
                         [5, 6, 1, 2, 3, 4])],
              ["Identical to the previous variant with one comparison changed.",
               "**Strictly** increasing means `a[i] > a[i - 1]`; equal neighbours "
               "break the run.",
               "Case four has a repeated `2`, so the climb restarts there and the "
               "answer is `3`, not `4`.",
               "A decreasing array has no climb longer than a single element, so "
               "case three answers `1`.",
               "Seeding both counters at `1` is what makes that come out right "
               "without a special case."]),
    ])


_PRACTICE[5] = [_P5_A, _P5_B, _P5_C, _P5_D, _P5_E]
