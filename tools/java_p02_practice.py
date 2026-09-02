# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 2 practice - 2D and multidimensional arrays.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[2]`.
#
# Five families, five variants each. Module 2 scope: rectangular int[r][c],
# row-major layout, row-wise and column-wise traversal, deepToString, diagonals,
# transpose, jagged arrays, 3D. Everything module 1 allowed is still allowed;
# nothing from module 3 onwards is (no Arrays.sort, no String methods, no
# helper methods beside main).
# ---------------------------------------------------------------------------


def _p2ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_MAT):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


_M_ANY = ([[1, 2, 3], [4, 5, 6]],
          [[7]],
          [[-1, 2], [3, -4]],
          [[0, 0], [0, 0]],
          [[5, 1, 9, 2]])

_M_SQ = ([[1, 2], [3, 4]],
         [[7]],
         [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
         [[-1, 0], [0, -1]],
         [[2, 0, 0], [0, 2, 0], [0, 0, 2]])


# --- Family A - row and column sweeps --------------------------------------

_P2_A = _jfam(
    "p2-sweeps", "Row sweeps and column sweeps",
    "Which index moves on the inner loop.",
    """
A 2D array in Java is an **array of arrays**. `m[r]` is a whole row — itself an
`int[]` — and `m[r][c]` is one cell. Rows come first, always.

That single fact decides everything about traversal. The natural order, the one
that matches how the rows actually sit in memory, holds the row still and walks
the columns:

```java
for (int r = 0; r < rows; r++) {          // pick a row
    for (int c = 0; c < cols; c++) {      // walk across it
        ... m[r][c] ...
    }
}
```

To go **down a column instead**, you swap which loop is outer:

```java
for (int c = 0; c < cols; c++) {          // pick a column
    for (int r = 0; r < rows; r++) {      // walk down it
        ... m[r][c] ...
    }
}
```

Notice the subscript `m[r][c]` did not change — only the loop nesting did. That
is the thing to internalise: **row-wise and column-wise differ only in which
loop is outer.** Everything else about the two is identical.

The variants below alternate between the two orders, and between accumulating
one answer for the whole grid and one answer per row.
""",
    [
        _p2ex("j2-pr-total", "Total of every cell", "Intro",
              "Print the sum of all `rows × cols` cells.",
              """
        int sum = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                sum += m[r][c];
            }
        }
        System.out.println(sum);
""",
              [_mcase(m, sum(sum(row) for row in m)) for m in _M_ANY],
              ["One accumulator for the whole grid, declared before both loops.",
               "Nesting order does not matter here — every cell is visited either way.",
               "`sum += m[r][c];` in the inner loop.",
               "Print once, after both loops have closed."]),

        _p2ex("j2-pr-row-sums", "One sum per row", "Intro",
              "Print each row's sum on its own line, in row order.",
              """
        for (int r = 0; r < rows; r++) {
            int sum = 0;
            for (int c = 0; c < cols; c++) {
                sum += m[r][c];
            }
            System.out.println(sum);
        }
""",
              [_mcase(m, _nl(*[sum(row) for row in m])) for m in _M_ANY],
              ["The accumulator moves INSIDE the outer loop — one answer per row "
               "means one accumulator per row.",
               "Declaring `sum` outside would carry the previous row's total forward.",
               "Reset it (by declaring it) at the top of each row, print it at the "
               "bottom.",
               "The `println` belongs in the outer loop, after the inner one "
               "finishes."]),

        _p2ex("j2-pr-col-sums", "One sum per column", "Easy",
              "Print each column's sum, separated by single spaces, on one line.",
              """
        for (int c = 0; c < cols; c++) {
            int sum = 0;
            for (int r = 0; r < rows; r++) {
                sum += m[r][c];
            }
            System.out.print(sum + " ");
        }
        System.out.println();
""",
              [_mcase(m, _sp([sum(row[c] for row in m) for c in range(len(m[0]))]))
               for m in _M_ANY],
              ["Columns mean the COLUMN loop is outer and the row loop is inner.",
               "The subscript is still `m[r][c]` — only the nesting flipped.",
               "Print each sum as you compute it with `System.out.print`, not "
               "`println`, so they all land on one line.",
               "`System.out.print(sum + \" \");` — the judge strips the trailing "
               "space, so the last value needs no special case.",
               "Finish with a bare `System.out.println();` to end the line."]),

        _p2ex("j2-pr-row-max", "The biggest in each row", "Easy",
              "Print the largest value of each row, separated by single spaces, on one "
              "line.",
              """
        for (int r = 0; r < rows; r++) {
            int best = m[r][0];
            for (int c = 1; c < cols; c++) {
                if (m[r][c] > best) {
                    best = m[r][c];
                }
            }
            System.out.print(best + " ");
        }
        System.out.println();
""",
              [_mcase(m, _sp([max(row) for row in m])) for m in _M_ANY],
              ["Module 1's running-extreme pattern, run once per row.",
               "Seed `best` with `m[r][0]` — the row's own first cell, never `0`. "
               "Case three has a row of `-1, 2` and a row of `3, -4`.",
               "Start the inner loop at `c = 1`, since column 0 is already the seed.",
               "Print each row's best with `System.out.print(best + \" \");`, then "
               "close the line with a bare `System.out.println();`."]),

        _p2ex("j2-pr-count-value", "How many cells hold it", "Intro",
              "Read the grid, then a value `k`. Print how many cells equal `k`.",
              """
        int k = sc.nextInt();
        int count = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (m[r][c] == k) {
                    count++;
                }
            }
        }
        System.out.println(count);
""",
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(r) for r in m) + f"\n{k}",
                     sum(row.count(k) for row in m))
               for (m, k) in (([[1, 2, 3], [4, 5, 6]], 5), ([[7]], 7),
                              ([[0, 0], [0, 0]], 0), ([[1, 2], [3, 4]], 9),
                              ([[2, 2, 2]], 2))],
              ["`k` is read after the whole grid.",
               "Every cell must be looked at, so nesting order is free.",
               "One counter for the whole grid, before both loops.",
               "Case four looks for a value that is not present and wants `0`."]),
    ])


# --- Family B - diagonals ---------------------------------------------------

_P2_B = _jfam(
    "p2-diagonals", "Diagonals",
    "When the two indices move together.",
    """
Everything in this family is **square**: `rows == cols`, called `n` below. The
input still gives you both, and every test case here is square.

A diagonal is what you get when the two subscripts stop being independent.

**The main diagonal** is every cell whose row equals its column — top-left to
bottom-right. One loop, one variable, used twice:

```java
for (int i = 0; i < n; i++) {
    ... m[i][i] ...            // (0,0), (1,1), (2,2), …
}
```

**The anti-diagonal** runs top-right to bottom-left. As the row goes down, the
column must come back:

```java
for (int i = 0; i < n; i++) {
    ... m[i][n - 1 - i] ...    // (0,n-1), (1,n-2), …, (n-1,0)
}
```

`n - 1 - i` is the same mirror expression that reversed an array in module 1.
Sanity-check it the same way: at `i = 0` it is `n - 1`, and at `i = n - 1` it
is `0`.

> On an **odd**-sized grid the two diagonals share the centre cell. If you are
> ever asked for "the sum of both diagonals", ask whether the centre should be
> counted once or twice — it is a deliberate trap in interviews. Here we count
> each diagonal independently, so the centre lands in both.
""",
    [
        _p2ex("j2-pr-diag-main", "Main diagonal sum", "Intro",
              "The grid is square. Print the sum of the cells from top-left to "
              "bottom-right.",
              """
        int sum = 0;
        for (int i = 0; i < rows; i++) {
            sum += m[i][i];
        }
        System.out.println(sum);
""",
              [_mcase(m, sum(m[i][i] for i in range(len(m)))) for m in _M_SQ],
              ["One loop, not two — a diagonal has `n` cells, not `n * n`.",
               "The row index and the column index are the same number.",
               "`sum += m[i][i];`",
               "For a 1x1 grid the diagonal is the single cell."]),

        _p2ex("j2-pr-diag-anti", "Anti-diagonal sum", "Easy",
              "Same square grid. Print the sum of the cells from top-right to "
              "bottom-left.",
              """
        int sum = 0;
        for (int i = 0; i < rows; i++) {
            sum += m[i][rows - 1 - i];
        }
        System.out.println(sum);
""",
              [_mcase(m, sum(m[i][len(m) - 1 - i] for i in range(len(m)))) for m in _M_SQ],
              ["Still one loop — only the column expression changes.",
               "As the row index rises, the column index must fall.",
               "The mirror of `i` is `n - 1 - i`, and here `n` is `rows`.",
               "`sum += m[i][rows - 1 - i];`",
               "Check the ends: at `i = 0` you want the top-RIGHT cell."]),

        _p2ex("j2-pr-diag-both", "Both diagonals", "Easy",
              "Same square grid. Print the main diagonal sum and the anti-diagonal sum "
              "on one line, separated by a space. On an odd grid the centre cell counts "
              "in both.",
              """
        int main = 0;
        int anti = 0;
        for (int i = 0; i < rows; i++) {
            main += m[i][i];
            anti += m[i][rows - 1 - i];
        }
        System.out.println(main + " " + anti);
""",
              [_mcase(m, f"{sum(m[i][i] for i in range(len(m)))} "
                        f"{sum(m[i][len(m) - 1 - i] for i in range(len(m)))}")
               for m in _M_SQ],
              ["Two accumulators, one loop — you do not need to walk the grid twice.",
               "Both updates go in the same loop body.",
               "Do not try to avoid double-counting the centre: the brief says it "
               "counts in both.",
               "Case three is 3x3, where cell `(1,1)` is `5` and lands in each sum."]),

        _p2ex("j2-pr-diag-print", "Print the diagonal", "Intro",
              "Same square grid. Print the main diagonal's values, separated by single "
              "spaces, on one line.",
              """
        for (int i = 0; i < rows; i++) {
            System.out.print(m[i][i] + " ");
        }
        System.out.println();
""",
              [_mcase(m, _sp([m[i][i] for i in range(len(m))])) for m in _M_SQ],
              ["Same single loop as the main-diagonal sum, but printing instead of "
               "adding.",
               "`System.out.print(m[i][i] + \" \");` inside the loop.",
               "Then one bare `System.out.println();` after it, to end the line.",
               "A 1x1 grid prints its single cell."]),

        _p2ex("j2-pr-symmetric", "Is it symmetric?", "Medium",
              "Same square grid. Print `true` if the grid equals its own transpose — "
              "that is, `m[i][j] == m[j][i]` for every pair — and `false` otherwise.",
              """
        boolean symmetric = true;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < rows; j++) {
                if (m[i][j] != m[j][i]) {
                    symmetric = false;
                }
            }
        }
        System.out.println(symmetric);
""",
              [_mcase(m, _jbool(all(m[i][j] == m[j][i]
                                    for i in range(len(m)) for j in range(len(m)))))
               for m in ([[1, 2], [3, 4]], [[7]], [[1, 2], [2, 1]],
                         [[1, 2, 3], [2, 5, 6], [3, 6, 9]], [[0, 1], [0, 0]])],
              ["A boolean accumulator that starts `true` and is only ever knocked "
               "down to `false`.",
               "Compare each cell with its mirror across the main diagonal: `m[i][j]` "
               "against `m[j][i]`.",
               "Never set it back to `true` inside the loop — one mismatch is fatal.",
               "The diagonal cells compare against themselves and are always equal, "
               "so they cost nothing.",
               "Case four is symmetric; case five differs at `(0,1)` versus `(1,0)`."]),
    ])


# --- Family C - reshaping ---------------------------------------------------

_P2_C = _jfam(
    "p2-reshape", "Reshaping a grid",
    "Build a new shape, or rearrange the one you have.",
    """
Two different jobs, and the first question is always which one you are doing.

**Rearranging in place** writes back into the same grid. Cheap, but the original
is gone:

```java
for (int r = 0; r < rows; r++) {
    for (int c = 0; c < cols / 2; c++) {        // note: cols / 2
        int tmp = m[r][c];
        m[r][c] = m[r][cols - 1 - c];
        m[r][cols - 1 - c] = tmp;
    }
}
```

That reverses every row. The `cols / 2` matters: run the loop to `cols` and you
swap every pair **twice**, putting the row back exactly as it started. Integer
division is doing the right thing on odd widths too — the middle element has
nowhere to go and correctly stays put.

**Building a new shape** allocates a fresh grid, and the new grid's dimensions
are usually swapped:

```java
int[][] t = new int[cols][rows];               // cols x rows, not rows x cols
for (int r = 0; r < rows; r++) {
    for (int c = 0; c < cols; c++) {
        t[c][r] = m[r][c];                     // the subscripts swap
    }
}
```

That is a **transpose**. Getting `new int[cols][rows]` the right way round is
most of the difficulty; a square grid will hide the mistake, so the cases below
are deliberately not all square.

`Arrays.deepToString(m)` prints a 2D array as `[[1, 2], [3, 4]]` — it is
`toString` that recurses into the rows. Plain `Arrays.toString` on a 2D array
prints the rows' addresses, which is never what you want.
""",
    [
        _p2ex("j2-pr-deep", "Print the grid", "Intro",
              "Print the whole grid in `Arrays.deepToString` format — "
              "`[[1, 2, 3], [4, 5, 6]]`.",
              """
        System.out.println(Arrays.deepToString(m));
""",
              [_mcase(m, _jdeep(m)) for m in _M_ANY],
              ["`Arrays.toString(m)` on a 2D array prints row addresses, not values.",
               "The helper that recurses into the rows has `deep` in its name.",
               "`Arrays.deepToString(m)`",
               "Note the exact format: outer brackets, then each row bracketed, "
               "comma-space between."]),

        _p2ex("j2-pr-transpose", "Transpose it", "Medium",
              "Build the transpose — a `cols × rows` grid where `t[c][r]` is `m[r][c]` "
              "— and print it in `Arrays.deepToString` format. Do not modify `m`.",
              """
        int[][] t = new int[cols][rows];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                t[c][r] = m[r][c];
            }
        }
        System.out.println(Arrays.deepToString(t));
""",
              [_mcase(m, _jdeep([[m[r][c] for r in range(len(m))]
                                 for c in range(len(m[0]))])) for m in _M_ANY],
              ["The result is NOT the same shape unless the grid is square.",
               "Allocate `new int[cols][rows]` — the dimensions swap.",
               "Then `t[c][r] = m[r][c];` — the subscripts swap too.",
               "Case one is 2x3 and must come out 3x2. Case five is 1x4 and must "
               "come out 4x1.",
               "You cannot do this in place on a non-square grid; there is nowhere "
               "to put the extra rows."]),

        _p2ex("j2-pr-reverse-rows", "Reverse every row in place", "Easy",
              "Reverse the order of the values within each row, in place, then print "
              "the grid in `Arrays.deepToString` format.",
              """
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols / 2; c++) {
                int tmp = m[r][c];
                m[r][c] = m[r][cols - 1 - c];
                m[r][cols - 1 - c] = tmp;
            }
        }
        System.out.println(Arrays.deepToString(m));
""",
              [_mcase([list(r) for r in m], _jdeep([list(reversed(r)) for r in m]))
               for m in _M_ANY],
              ["This is module 1's two-pointer swap, run once per row.",
               "The inner loop must stop at `cols / 2`, not `cols` — otherwise every "
               "pair is swapped twice and the row ends up unchanged.",
               "A swap needs a temporary: save `m[r][c]` before overwriting it.",
               "The partner of column `c` is `cols - 1 - c`.",
               "Odd widths are fine: integer division leaves the middle column alone, "
               "which is correct. Case five has four columns; a three-column case "
               "would keep its centre."]),

        _p2ex("j2-pr-flatten", "Flatten to one dimension", "Easy",
              "Copy every cell into a single `int[]` in row-major order — all of row 0, "
              "then all of row 1, and so on — then print it in `Arrays.toString` "
              "format.",
              """
        int[] flat = new int[rows * cols];
        int i = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                flat[i] = m[r][c];
                i++;
            }
        }
        System.out.println(Arrays.toString(flat));
""",
              [_mcase(m, _jarr([x for row in m for x in row])) for m in _M_ANY],
              ["The flat array holds `rows * cols` values.",
               "Carry a separate write cursor `i` that only ever moves forward — it "
               "is not `r` and not `c`.",
               "Declare `i` OUTSIDE both loops, or it resets on every row.",
               "Increment it after each write.",
               "Row-major means the row loop is outer, which is the natural nesting.",
               "This is a 1D array now, so print with `Arrays.toString`, not "
               "`deepToString`."]),

        _p2ex("j2-pr-flip-vertical", "Flip it top to bottom", "Easy",
              "Print the grid with its rows in reverse order — last row first — in "
              "`Arrays.deepToString` format. Build a new grid; do not modify `m`.",
              """
        int[][] f = new int[rows][cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                f[r][c] = m[rows - 1 - r][c];
            }
        }
        System.out.println(Arrays.deepToString(f));
""",
              [_mcase(m, _jdeep(list(reversed(m)))) for m in _M_ANY],
              ["The shape does not change here — `new int[rows][cols]`.",
               "Only the ROW index is mirrored; the column index is copied straight "
               "across.",
               "`f[r][c] = m[rows - 1 - r][c];`",
               "Compare with the transpose: there both subscripts moved, here only "
               "one does.",
               "A one-row grid comes out unchanged."]),
    ])


# --- Family D - grid queries ------------------------------------------------

_P2_D = _jfam(
    "p2-queries", "Asking the grid a question",
    "Search, locate and summarise across two dimensions.",
    """
Module 1's search and extreme patterns, lifted into two dimensions. The logic is
unchanged; the only new work is that a *position* is now two numbers instead of
one.

```java
int bestR = 0, bestC = 0;
for (int r = 0; r < rows; r++) {
    for (int c = 0; c < cols; c++) {
        if (m[r][c] > m[bestR][bestC]) {
            bestR = r;
            bestC = c;
        }
    }
}
```

Two things carry over from module 1 and are worth saying again:

- **Seed from a real cell,** `m[0][0]`, never from `0`. Grids of negatives are
  in the cases below for exactly this reason.
- **`>` versus `>=` decides ties** — first winner or last winner. Same one
  character, same consequence.

The one genuinely new problem is **breaking out of two loops**. `break` only
leaves the loop it is in, so a `break` in the inner loop leaves the outer one
running. The clean fix without helper methods (module 9 has those, this one does
not) is to let a flag or a sentinel suppress later work:

```java
if (foundR == -1) { ... }        // only look while nothing has been found
```

The variants below never need to stop early, so you can walk the whole grid and
keep the first or last match by choosing your comparison carefully — usually the
simpler answer anyway.
""",
    [
        _p2ex("j2-pr-locate", "Where is it?", "Easy",
              "Read the grid, then a value `k`. Print the row and column of its **first** "
              "occurrence in row-major order, separated by a space. Print `-1 -1` if it "
              "is not there.",
              """
        int k = sc.nextInt();
        int foundR = -1;
        int foundC = -1;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (m[r][c] == k && foundR == -1) {
                    foundR = r;
                    foundC = c;
                }
            }
        }
        System.out.println(foundR + " " + foundC);
""",
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(r) for r in m) + f"\n{k}",
                     next((f"{r} {c}" for r in range(len(m)) for c in range(len(m[0]))
                           if m[r][c] == k), "-1 -1"))
               for (m, k) in (([[1, 2, 3], [4, 5, 6]], 5), ([[7]], 7),
                              ([[1, 2], [3, 4]], 9), ([[2, 2], [2, 2]], 2),
                              ([[0, 1], [1, 0]], 1))],
              ["Two `-1` accumulators, so \"never assigned\" already prints `-1 -1`.",
               "Row-major order means the row loop is outer — that is what makes "
               "case four's answer `0 0`.",
               "`break` would only escape the inner loop. Instead, guard the "
               "assignment so only the first match sticks.",
               "`if (m[r][c] == k && foundR == -1)` — once `foundR` is set, later "
               "matches are ignored.",
               "Print both numbers on one line, space separated."]),

        _p2ex("j2-pr-heaviest-row", "The heaviest row", "Easy",
              "Print the index of the row with the largest sum. On a tie, print the "
              "**first** such row.",
              """
        int bestRow = 0;
        int bestSum = 0;
        for (int c = 0; c < cols; c++) {
            bestSum += m[0][c];
        }
        for (int r = 1; r < rows; r++) {
            int sum = 0;
            for (int c = 0; c < cols; c++) {
                sum += m[r][c];
            }
            if (sum > bestSum) {
                bestSum = sum;
                bestRow = r;
            }
        }
        System.out.println(bestRow);
""",
              [_mcase(m, max(range(len(m)), key=lambda r: (sum(m[r]), -r)))
               for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[-1, 2], [3, -4]],
                         [[1, 1], [1, 1]], [[5, 1], [0, 0], [3, 3]])],
              ["Two nested patterns: a per-row sum inside a running maximum.",
               "Seed the best with row 0's actual sum, not with `0` — case three has "
               "a row summing to `-1`.",
               "So compute row 0's sum first, then loop rows `1` upward.",
               "Use a strict `>` so a tie keeps the earlier row. Case four is all "
               "ties and wants `0`.",
               "Print the row INDEX, not the sum."]),

        _p2ex("j2-pr-positive-rows", "Rows that are all positive", "Easy",
              "Print how many rows have every value strictly greater than `0`.",
              """
        int count = 0;
        for (int r = 0; r < rows; r++) {
            boolean allPositive = true;
            for (int c = 0; c < cols; c++) {
                if (m[r][c] <= 0) {
                    allPositive = false;
                }
            }
            if (allPositive) {
                count++;
            }
        }
        System.out.println(count);
""",
              [_mcase(m, sum(1 for row in m if all(x > 0 for x in row)))
               for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[-1, 2], [3, 4]],
                         [[0, 1], [1, 1]], [[1], [-1], [2]])],
              ["Two accumulators at two different levels: a count for the grid, and "
               "a flag per row.",
               "The flag is declared inside the outer loop so it resets each row.",
               "It starts `true` and is only knocked down — one bad cell disqualifies "
               "the row.",
               "**Strictly** positive: `0` fails. Case four's first row contains `0` "
               "and must not count.",
               "Increment the outer count after the inner loop, not inside it."]),

        _p2ex("j2-pr-border", "Sum the border", "Medium",
              "Print the sum of the cells on the outer edge — first row, last row, "
              "first column, last column. Count each border cell exactly **once**, even "
              "though the corners belong to two edges.",
              """
        int sum = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (r == 0 || r == rows - 1 || c == 0 || c == cols - 1) {
                    sum += m[r][c];
                }
            }
        }
        System.out.println(sum);
""",
              [_mcase(m, sum(m[r][c] for r in range(len(m)) for c in range(len(m[0]))
                             if r == 0 or r == len(m) - 1 or c == 0 or c == len(m[0]) - 1))
               for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                         [[1, 1], [1, 1]], [[1, 2, 3, 4]])],
              ["The tempting approach — add the top row, the bottom row, then the two "
               "side columns — double-counts all four corners.",
               "Walk every cell instead and ask whether it is ON the border. Then "
               "each cell is visited exactly once by construction.",
               "A cell is on the border if it is in the first or last row, OR the "
               "first or last column.",
               "`if (r == 0 || r == rows - 1 || c == 0 || c == cols - 1)`",
               "In case three (3x3) only the centre `5` is excluded, giving `40`.",
               "A single-row grid is entirely border, and so is a 1x1."]),

        _p2ex("j2-pr-argmax-2d", "The biggest cell and where it is", "Medium",
              "Print the largest value in the grid, then its row, then its column, all "
              "on one line separated by spaces. On a tie, report the **first** in "
              "row-major order.",
              """
        int bestR = 0;
        int bestC = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (m[r][c] > m[bestR][bestC]) {
                    bestR = r;
                    bestC = c;
                }
            }
        }
        System.out.println(m[bestR][bestC] + " " + bestR + " " + bestC);
""",
              [_mcase(m, (lambda best: f"{m[best[0]][best[1]]} {best[0]} {best[1]}")(
                  min(((r, c) for r in range(len(m)) for c in range(len(m[0]))
                       if m[r][c] == max(max(row) for row in m)))))
               for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[-1, -2], [-3, -4]],
                         [[5, 5], [5, 5]], [[1, 9], [9, 1]])],
              ["Track the POSITION of the best, not the value — then the value is "
               "just `m[bestR][bestC]`.",
               "Seeding both indices at `0` is safe: those are indices, not values. "
               "Case three is all negative and would break a `0`-valued seed.",
               "Compare against `m[bestR][bestC]`, not against a stale copy.",
               "A strict `>` never replaces on a tie, so the first in row-major "
               "order survives. Case four wants `5 0 0`, case five wants `9 0 1`.",
               "Print value, row, column — in that order, space separated."]),
    ])


# --- Family E - jagged and 3D ------------------------------------------------

_RD_JAG = (
    "        int rows = sc.nextInt();\n"
    "        int[][] m = new int[rows][];\n"
    "        for (int r = 0; r < rows; r++) {\n"
    "            int len = sc.nextInt();\n"
    "            m[r] = new int[len];\n"
    "            for (int c = 0; c < len; c++) m[r][c] = sc.nextInt();\n"
    "        }\n"
)

_RD_3D = (
    "        int deep = sc.nextInt();\n"
    "        int rows = sc.nextInt();\n"
    "        int cols = sc.nextInt();\n"
    "        int[][][] g = new int[deep][rows][cols];\n"
    "        for (int z = 0; z < deep; z++)\n"
    "            for (int r = 0; r < rows; r++)\n"
    "                for (int c = 0; c < cols; c++) g[z][r][c] = sc.nextInt();\n"
)


def _jagcase(rows, out):
    lines = [str(len(rows))]
    for row in rows:
        lines.append(f"{len(row)} {_sp(row)}" if row else "0")
    return _case("\n".join(lines), out)


def _cube_case(cube, out):
    lines = [f"{len(cube)} {len(cube[0])} {len(cube[0][0])}"]
    for layer in cube:
        for row in layer:
            lines.append(_sp(row))
    return _case("\n".join(lines), out)


_JAG = ([[1, 2, 3], [4], [5, 6]],
        [[7]],
        [[1], [2], [3]],
        [[0, 0, 0, 0], [1]],
        [[9, 9], [1, 2, 3, 4, 5]])

_CUBE = ([[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
         [[[7]]],
         [[[1, 1], [1, 1]], [[-1, -1], [-1, -1]]],
         [[[0, 0, 0]], [[1, 2, 3]]],
         [[[2]], [[3]], [[4]]])


_P2_E = _jfam(
    "p2-jagged", "Jagged rows and three dimensions",
    "When the rows are not all the same length — and when there is a third index.",
    """
## Jagged arrays

Java has no true 2D array. `int[][]` is an array **of** `int[]`, and nothing
requires those rows to be the same length:

```java
int[][] m = new int[3][];     // three rows, none of them allocated yet
m[0] = new int[5];
m[1] = new int[2];            // rows may differ — this is a jagged array
```

The consequence for every loop you write: **there is no single `cols`.** The
width of row `r` is `m[r].length`, and reading it from the wrong row is an
`ArrayIndexOutOfBoundsException` waiting to happen.

```java
for (int r = 0; r < m.length; r++) {
    for (int c = 0; c < m[r].length; c++) {    // m[r].length, not cols
        ...
    }
}
```

Writing it this way costs nothing on a rectangular grid and is correct on a
jagged one, which is a good reason to make it your default.

## Three dimensions

A third index is not a new idea, just another level of nesting. `int[d][r][c]`
is an array of `d` grids, and `g[z]` is a whole 2D grid:

```java
for (int z = 0; z < deep; z++)
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < cols; c++)
            ... g[z][r][c] ...
```

Read the subscripts outside-in: `g[z]` picks a layer, `g[z][r]` picks a row of
that layer, `g[z][r][c]` picks a cell. The same reading works for any depth.
""",
    [
        _p2ex("j2-pr-jag-lengths", "How long is each row?", "Intro",
              "The rows have different lengths. Print each row's length, separated by "
              "single spaces, on one line.",
              """
        for (int r = 0; r < rows; r++) {
            System.out.print(m[r].length + " ");
        }
        System.out.println();
""",
              [_jagcase(j, _sp([len(row) for row in j])) for j in _JAG],
              ["Each row is its own array, with its own `.length`.",
               "`m[r].length` is the width of row `r`. `m.length` would be the number "
               "of rows.",
               "No inner loop is needed at all — you are not looking at the values.",
               "`System.out.print(m[r].length + \" \");`, then a bare "
               "`System.out.println();` to end the line."],
              read=_RD_JAG),

        _p2ex("j2-pr-jag-sum", "Total of a jagged grid", "Intro",
              "Print the sum of every value across all rows.",
              """
        int sum = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < m[r].length; c++) {
                sum += m[r][c];
            }
        }
        System.out.println(sum);
""",
              [_jagcase(j, sum(sum(row) for row in j)) for j in _JAG],
              ["The inner loop's bound must come from the row you are actually on.",
               "`c < m[r].length` — using a fixed width would run off the short rows.",
               "One accumulator for the whole structure.",
               "This is exactly the rectangular version with one expression changed, "
               "which is why writing `m[r].length` by default costs nothing."],
              read=_RD_JAG),

        _p2ex("j2-pr-jag-longest", "The longest row", "Easy",
              "Print the index of the longest row. On a tie, print the **first** such "
              "row.",
              """
        int best = 0;
        for (int r = 1; r < rows; r++) {
            if (m[r].length > m[best].length) {
                best = r;
            }
        }
        System.out.println(best);
""",
              [_jagcase(j, max(range(len(j)), key=lambda r: (len(j[r]), -r))) for j in _JAG],
              ["The running-extreme pattern again, but the thing being compared is a "
               "length rather than a value.",
               "Keep the index: `int best = 0;` then compare `m[r].length` against "
               "`m[best].length`.",
               "Strict `>` keeps the first of equal-length rows. Case three has three "
               "rows of length 1 and wants `0`.",
               "Print the index, not the length."],
              read=_RD_JAG),

        _p2ex("j2-pr-cube-sum", "Total of a cube", "Easy",
              "Read a `deep × rows × cols` block of numbers. Print the sum of every "
              "cell.",
              """
        int sum = 0;
        for (int z = 0; z < deep; z++) {
            for (int r = 0; r < rows; r++) {
                for (int c = 0; c < cols; c++) {
                    sum += g[z][r][c];
                }
            }
        }
        System.out.println(sum);
""",
              [_cube_case(cube, sum(x for layer in cube for row in layer for x in row))
               for cube in _CUBE],
              ["Three nested loops, one accumulator.",
               "The subscript order matches the declaration: `g[z][r][c]`.",
               "Nesting order does not affect the answer here, since every cell is "
               "visited.",
               "The accumulator goes before all three loops."],
              read=_RD_3D),

        _p2ex("j2-pr-cube-layers", "One sum per layer", "Easy",
              "Same cube. Print each layer's total on its own line, in layer order.",
              """
        for (int z = 0; z < deep; z++) {
            int sum = 0;
            for (int r = 0; r < rows; r++) {
                for (int c = 0; c < cols; c++) {
                    sum += g[z][r][c];
                }
            }
            System.out.println(sum);
        }
""",
              [_cube_case(cube, _nl(*[sum(x for row in layer for x in row)
                                      for layer in cube])) for cube in _CUBE],
              ["Same shape as \"one sum per row\" in family A, one level deeper.",
               "The accumulator moves inside the `z` loop — one answer per layer means "
               "one accumulator per layer.",
               "The two inner loops sum a whole 2D grid, exactly as before.",
               "Print inside the `z` loop, after the two inner loops finish.",
               "Case three has a layer of `1`s and a layer of `-1`s, so the two lines "
               "differ in sign."],
              read=_RD_3D),
    ])


_PRACTICE[2] = [_P2_A, _P2_B, _P2_C, _P2_D, _P2_E]
