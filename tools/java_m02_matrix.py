# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 2 — 2D and multidimensional arrays.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# The through-line is that Java has no true 2D array: `int[][]` is an array of
# references to `int[]` rows. Every surprising thing in this module — why
# `m[0].length` is the width, why rows can have different lengths, why a
# shallow copy shares rows — falls straight out of that one fact.
# ---------------------------------------------------------------------------

_M2 = []

# A jagged-array reader, and the matching case builder. Rectangular exercises
# use `_RD_MAT` / `_mcase` from java_course.py; these are for lesson 2.5.
_RD_JAG = (
    "        int rows = sc.nextInt();\n"
    "        int[][] m = new int[rows][];\n"
    "        for (int r = 0; r < rows; r++) {\n"
    "            int len = sc.nextInt();\n"
    "            m[r] = new int[len];\n"
    "            for (int c = 0; c < len; c++) m[r][c] = sc.nextInt();\n"
    "        }\n"
)


def _jagcase(rows, out):
    """stdin = row count, then one `len v1 v2 …` line per row."""
    lines = [str(len(rows))] + [f"{len(r)} {_sp(r)}".rstrip() for r in rows]
    return _case("\n".join(lines), out)


def _transpose(m):
    return [[m[r][c] for r in range(len(m))] for c in range(len(m[0]))]


# --- 2.1 The shape of a 2D array -------------------------------------------

_M2.append(_jlesson(
    "m2-shape", "There is no 2D array",
    "`int[][]` is an array of row references — and everything odd about it follows.",
    """
Java does not have a 2D array. It has an array whose elements are themselves
arrays. `new int[3][4]` allocates **four** objects: one outer array of length 3
holding three references, and three `int[4]` rows.

```java
int[][] m = new int[3][4];
m.length        // 3  — the number of ROWS
m[0].length     // 4  — the width of row 0
```

There is no `m.width`. The width is a property of a row, not of `m`, which is
why the second one has to go through `m[0]`.

**Consequences you will meet immediately:**

- Rows can have **different lengths**. `new int[3][]` allocates the outer array
  only, and every row starts as `null` until you assign one. That is lesson 2.5.
- The inner loop bound should be `m[r].length`, not `m[0].length` — the two
  agree only for rectangular data, and the day they disagree you get a crash
  or silent truncation.
- `Arrays.copyOf(m, m.length)` copies the *references*, so the copy shares
  every row. Module 1's aliasing lesson, one level up.

**Making one.**

```java
int[][] a = new int[2][3];                    // 2 rows of 3, all zeros
int[][] b = {{1, 2, 3}, {4, 5, 6}};           // literal
int[][] c = new int[3][];                     // 3 null rows, fill them yourself
```

**Printing one.** `Arrays.toString(m)` is useless here — it prints the rows'
default `toString`, i.e. three `[I@…` tags. You want:

```java
System.out.println(Arrays.deepToString(m));   // [[1, 2, 3], [4, 5, 6]]
```

`deep` means "recurse into nested arrays". There is an `Arrays.deepEquals` for
the same reason.

**Indexing reads row-then-column: `m[r][c]`.** Writing `m[c][r]` on a
non-square matrix throws; on a square one it silently gives you the wrong cell,
which is worse.
""",
    warmup=[
        _jq("```java\nint[][] m = new int[3][4];\nSystem.out.println(m.length + \" \" + m[0].length);\n```",
            ["3 4", "4 3", "12 12", "3 3"],
            0,
            "`m.length` is the number of rows (3). The width lives on a row, so you ask "
            "`m[0]` for it (4). There is no `m.width`."),
        _jq("What does `System.out.println(Arrays.toString(new int[][]{{1,2},{3,4}}));` print?",
            ["Something like `[[I@1b6d, [I@42a5]`", "`[[1, 2], [3, 4]]`", "`[1, 2, 3, 4]`",
             "It does not compile"],
            0,
            "`toString` stringifies each element — and each element is an `int[]`, which has "
            "no useful `toString`. Use `Arrays.deepToString`."),
    ],
    exercises=[
        _je("j2-shape-dims", "How big is it?",
            "The grid is already read in. Replace `____` so the program prints its "
            "dimensions as `rows cols` — but get the numbers **from the array "
            "itself**, not from the `rows` and `cols` variables.",
            _jscan(_RD_MAT + '        System.out.println(m.length + " " + m[0].length);'),
            'm.length + " " + m[0].length',
            [_mcase(m, f"{len(m)} {len(m[0])}")
             for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[1, 2], [3, 4], [5, 6]])],
            hints=["The row count is a field on the outer array.",
                   "The width belongs to a row, so ask a row for it.",
                   '`m.length + " " + m[0].length`'],
            difficulty="Intro"),

        _je("j2-shape-deep", "Print it properly",
            "Print the whole grid in one go, in the `[[1, 2], [3, 4]]` shape. "
            "`Arrays.toString` will not do it — replace `____` with the call that will.",
            _jscan(_RD_MAT + "        System.out.println(Arrays.deepToString(m));"),
            "Arrays.deepToString(m)",
            [_mcase(m, _jdeep(m))
             for m in ([[1, 2], [3, 4]], [[5]], [[1, 2, 3], [4, 5, 6]])],
            hints=["There is a `deep` variant for nested arrays.",
                   "It recurses into each row instead of calling the row's `toString`.",
                   "`Arrays.deepToString(m)`"],
            difficulty="Intro"),

        _je("j2-shape-cell", "Row then column",
            "After the grid, the input has a row index `r` and a column index `c`. "
            "Replace `____` with the expression that reads that cell.",
            _jscan(
                _RD_MAT
                + "        int r = sc.nextInt();\n"
                  "        int c = sc.nextInt();\n"
                  "        System.out.println(m[r][c]);"),
            "m[r][c]",
            [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m) + f"\n{r}\n{c}",
                   m[r][c])
             for (m, r, c) in (([[1, 2, 3], [4, 5, 6]], 1, 2),
                               ([[1, 2, 3], [4, 5, 6]], 0, 0),
                               ([[9, 8], [7, 6], [5, 4]], 2, 1))],
            hints=["The first bracket picks the row.",
                   "The second bracket picks the column within that row.",
                   "`m[r][c]`"],
            difficulty="Intro"),

        _jfix("j2-shape-swapped", "Indices the wrong way round",
              "This should print the cell at row `r`, column `c`, but it crashes with "
              "`ArrayIndexOutOfBoundsException` on a non-square grid. Fix it.",
              _jscan(
                  _RD_MAT
                  + "        int r = sc.nextInt();\n"
                    "        int c = sc.nextInt();\n"
                    "        System.out.println(m[c][r]);"),
              _jscan(
                  _RD_MAT
                  + "        int r = sc.nextInt();\n"
                    "        int c = sc.nextInt();\n"
                    "        System.out.println(m[r][c]);"),
              [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m) + f"\n{r}\n{c}",
                     m[r][c])
               for (m, r, c) in (([[1, 2, 3], [4, 5, 6]], 1, 2),
                                 ([[1, 2, 3, 4], [5, 6, 7, 8]], 0, 3))],
              hints=["Which bracket picks the row?",
                     "`m` is an array of rows, so the outer index must be the row.",
                     "`m[r][c]`, not `m[c][r]`."]),

        _jch("j2-shape-identity", "Build an identity matrix", "Easy",
             "Read a single number `n` and print the `n × n` identity matrix — 1s "
             "down the main diagonal, 0s everywhere else — using "
             "`Arrays.deepToString`. For `n = 3` that is `[[1, 0, 0], [0, 1, 0], "
             "[0, 0, 1]]`. Write the whole block where you see `____`.",
             _jscan(
                 "        int n = sc.nextInt();\n"
                 "        int[][] id = new int[n][n];\n"
                 "        for (int i = 0; i < n; i++) id[i][i] = 1;\n"
                 "        System.out.println(Arrays.deepToString(id));"),
             "        int[][] id = new int[n][n];\n"
             "        for (int i = 0; i < n; i++) id[i][i] = 1;\n"
             "        System.out.println(Arrays.deepToString(id));",
             [_case(n, _jdeep([[1 if i == j else 0 for j in range(n)] for i in range(n)]))
              for n in (3, 1, 4)],
             hints=["Every slot already starts at 0 — you only have to write the 1s.",
                    "The diagonal is where the row index equals the column index.",
                    "One loop is enough: `id[i][i] = 1;`"]),
    ],
    quiz=[
        _jq("How many objects does `new int[3][4]` allocate?",
            ["Four: the outer array plus three rows", "One", "Twelve", "Three"],
            0,
            "One `int[][]` of length 3 holding three references, plus the three `int[4]` "
            "rows it points at."),
        _jq("Why is `m[r].length` safer than `m[0].length` as an inner-loop bound?",
            ["Rows can have different lengths, and `m[r].length` is right for the row you are on",
             "`m[0].length` is a compile error",
             "It is not — they are always equal",
             "`m[0]` might be null but `m[r]` never is"],
            0,
            "For rectangular data they agree. For a jagged array `m[0].length` either "
            "truncates the long rows or runs off the end of the short ones."),
    ],
))

# --- 2.2 Traversal ----------------------------------------------------------

_M2.append(_jlesson(
    "m2-traverse", "Nested loops, row-major and column-major",
    "Which loop is outer decides the visiting order — and sometimes the speed.",
    """
Two nested loops, and the only real decision is which one goes outside.

**Row-major — the default, and the one to reach for.**

```java
for (int r = 0; r < m.length; r++) {
    for (int c = 0; c < m[r].length; c++) {
        System.out.print(m[r][c] + " ");
    }
    System.out.println();          // end the row
}
```

Visits `m[0][0], m[0][1], … m[1][0], …`. That is also the order the values sit
in memory (each row is one contiguous `int[]`), so it is the cache-friendly
order. On a big matrix, row-major is measurably faster than column-major for
exactly this reason — a nice thing to mention in an interview.

**Column-major — swap which loop is outer.**

```java
for (int c = 0; c < m[0].length; c++) {
    for (int r = 0; r < m.length; r++) {
        System.out.print(m[r][c] + " ");
    }
    System.out.println();          // end the column
}
```

Note that `m[r][c]` is **unchanged**. You do not swap the indices; you swap the
loops. Swapping the indices instead is the bug from lesson 2.1.

**Printing a grid** is the one place `System.out.print` beats `println`: print
the cells with a trailing space, then a bare `System.out.println()` to end the
row. The judge trims trailing whitespace on each line, so you do not have to
fuss over the final separator.

**The bound trap.** With the column loop outside, `m[0].length` is doing double
duty as "the width" — fine for rectangular data, wrong for jagged. If the data
might be jagged, column-major traversal needs a guard, which is a good reason
to prefer row-major whenever you have the choice.
""",
    warmup=[
        _jq("For `{{1,2,3},{4,5,6}}`, in what order does a **row-major** walk visit the values?",
            ["1 2 3 4 5 6", "1 4 2 5 3 6", "6 5 4 3 2 1", "1 2 4 5 3 6"],
            0,
            "The outer loop holds the row still while the inner loop sweeps the columns, so "
            "you finish row 0 before starting row 1."),
        _jq("To walk column-major, what changes?",
            ["Which loop is outer — the expression stays `m[r][c]`",
             "The expression becomes `m[c][r]`",
             "Both the loop order and the expression",
             "You have to transpose the matrix first"],
            0,
            "`m[r][c]` always means 'row r, column c'. Only the visiting order changes, and "
            "that is decided by which loop is outside."),
    ],
    exercises=[
        _je("j2-trav-rows", "Print the grid",
            "Print the grid back, one row per line, values separated by spaces. "
            "Replace `____` with the inner loop that prints a single row.",
            _jscan(
                _RD_MAT
                + "        for (int r = 0; r < rows; r++) {\n"
                  '            for (int c = 0; c < m[r].length; c++) System.out.print(m[r][c] + " ");\n'
                  "            System.out.println();\n"
                  "        }"),
            '            for (int c = 0; c < m[r].length; c++) System.out.print(m[r][c] + " ");',
            [_mcase(m, _nl(*[_sp(row) for row in m]))
             for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[1, 2], [3, 4], [5, 6]])],
            hints=["The outer loop already fixes the row — you sweep the columns.",
                   "Use `System.out.print` so the row stays on one line.",
                   'The bound is `m[r].length`, and the body is `System.out.print(m[r][c] + " ");`']),

        _je("j2-trav-cols", "Column by column",
            "Print the grid **column-major**: one line per column, holding the "
            "column still and sweeping the rows. For `{{1,2,3},{4,5,6}}` print "
            "`1 4`, then `2 5`, then `3 6`. Replace `____` with the outer loop header.",
            _jscan(
                _RD_MAT
                + "        for (int c = 0; c < cols; c++) {\n"
                  '            for (int r = 0; r < rows; r++) System.out.print(m[r][c] + " ");\n'
                  "            System.out.println();\n"
                  "        }"),
            "for (int c = 0; c < cols; c++) {",
            [_mcase(m, _nl(*[_sp(col) for col in _transpose(m)]))
             for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[1, 2], [3, 4], [5, 6]])],
            hints=["The column index has to be the one that changes slowest.",
                   "Same shape as any `for` header — it is the variable that differs.",
                   "`for (int c = 0; c < cols; c++) {`"]),

        _jfix("j2-trav-bounds", "The wrong bound",
              "This should print the sum of every cell. It works on square grids and "
              "crashes on wide ones, because the inner loop is bounded by the number "
              "of **rows**. Fix the bound.",
              _jscan(
                  _RD_MAT
                  + "        int sum = 0;\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < rows; c++) sum += m[r][c];\n"
                    "        }\n"
                    "        System.out.println(sum);"),
              _jscan(
                  _RD_MAT
                  + "        int sum = 0;\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < cols; c++) sum += m[r][c];\n"
                    "        }\n"
                    "        System.out.println(sum);"),
              [_mcase(m, sum(sum(row) for row in m))
               for m in ([[1, 2, 3], [4, 5, 6]], [[1, 2, 3, 4]], [[1, 2], [3, 4]])],
              hints=["Look at what the inner loop compares against.",
                     "The inner loop is walking columns, so it needs the column count.",
                     "`c < cols` (or `c < m[r].length`)."]),

        _jch("j2-trav-count", "Count what's above the line", "Easy",
             "After the grid the input has a threshold `t`. Print how many cells are "
             "**strictly greater** than `t`. Write the whole block where you see `____`.",
             _jscan(
                 _RD_MAT
                 + "        int t = sc.nextInt();\n"
                   "        int count = 0;\n"
                   "        for (int r = 0; r < rows; r++) {\n"
                   "            for (int c = 0; c < cols; c++) {\n"
                   "                if (m[r][c] > t) count++;\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(count);"),
             "        int count = 0;\n"
             "        for (int r = 0; r < rows; r++) {\n"
             "            for (int c = 0; c < cols; c++) {\n"
             "                if (m[r][c] > t) count++;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(count);",
             [_case(f"{len(m)} {len(m[0])}\n" + "\n".join(_sp(row) for row in m) + f"\n{t}",
                    sum(1 for row in m for v in row if v > t))
              for (m, t) in (([[1, 5, 3], [8, 2, 9]], 4),
                             ([[1, 1], [1, 1]], 1),
                             ([[-3, -1], [0, 4]], -2))],
             hints=["Two nested loops and one counter declared outside both.",
                    "Strictly greater — a cell equal to `t` does not count.",
                    "Declare `count` before the loops, or it resets on every row."]),
    ],
    quiz=[
        _jq("Why is row-major traversal usually faster than column-major on a large matrix?",
            ["Each row is one contiguous array, so row-major reads sequential memory",
             "The JIT special-cases the variable name `r`",
             "Column-major recomputes `m[0].length` every pass",
             "It isn't — they are identical"],
            0,
            "A row is a single `int[]` laid out contiguously. Row-major walks straight "
            "through it; column-major jumps between rows on every step, defeating the cache."),
        _jq("Column-major traversal bounded by `m[0].length` breaks on which input?",
            ["A jagged array whose later rows are longer than row 0",
             "Any array with more rows than columns",
             "An array of one row",
             "It never breaks"],
            0,
            "It silently ignores the extra cells in the longer rows. Row-major with "
            "`m[r].length` handles jagged data without a special case."),
    ],
))

# --- 2.3 Aggregates over a grid --------------------------------------------


def _rowsums(m):
    return [sum(r) for r in m]


def _colsums(m):
    return [sum(col) for col in _transpose(m)]


def _maxcell(m):
    best = (m[0][0], 0, 0)
    for r in range(len(m)):
        for c in range(len(m[r])):
            if m[r][c] > best[0]:
                best = (m[r][c], r, c)
    return best


_M2.append(_jlesson(
    "m2-aggregate", "Row sums, column sums, and the biggest cell",
    "The same one-pass patterns as module 1, with an extra loop around them.",
    """
Every aggregate from module 1 works here; you just decide **where the
accumulator lives**.

**One accumulator for the whole grid** — declare it before both loops:

```java
int sum = 0;
for (int r = 0; r < m.length; r++)
    for (int c = 0; c < m[r].length; c++)
        sum += m[r][c];
```

**One accumulator per row** — declare it inside the outer loop, so it resets:

```java
for (int r = 0; r < m.length; r++) {
    int rowSum = 0;                       // resets each row — that is the point
    for (int c = 0; c < m[r].length; c++) rowSum += m[r][c];
    System.out.println(rowSum);
}
```

Putting `int rowSum = 0;` outside the outer loop is one of the most common
bugs in this module: you get running totals instead of row totals, and the last
number is right, which makes it look almost correct.

**One accumulator per column** — you cannot reset it inside a row-major walk,
so use an array of accumulators:

```java
int[] colSum = new int[m[0].length];
for (int r = 0; r < m.length; r++)
    for (int c = 0; c < m[r].length; c++)
        colSum[c] += m[r][c];             // note: indexed by c
```

That trick — **an array of counters indexed by something other than the loop
variable** — comes back as frequency counting in module 4. Get used to it here.

**Tracking a cell's position** means keeping three variables in step:

```java
int best = m[0][0], bestR = 0, bestC = 0;
for (int r = 0; r < m.length; r++)
    for (int c = 0; c < m[r].length; c++)
        if (m[r][c] > best) { best = m[r][c]; bestR = r; bestC = c; }
```

Strict `>` keeps the **first** maximum in row-major order — same tie rule as
module 1.
""",
    warmup=[
        _jq("Where must `int rowSum = 0;` go, to print one total per row?",
            ["Inside the outer loop, before the inner loop",
             "Before both loops",
             "Inside the inner loop",
             "After both loops"],
            0,
            "It has to reset once per row. Before both loops it accumulates across rows; "
            "inside the inner loop it resets on every cell and every total prints as the "
            "last cell."),
        _jq("Why do column sums need an `int[]` rather than a single `int`?",
            ["A row-major walk touches every column before finishing any of them",
             "Because columns can be jagged",
             "They don't — a single int works",
             "To avoid integer overflow"],
            0,
            "In row-major order you visit column 0, then 1, then 2, then back to column 0 "
            "on the next row — so all the column totals have to be in flight at once."),
    ],
    exercises=[
        _je("j2-agg-rowsum", "One total per row",
            "Print the sum of each row, one per line. Replace `____` with the line "
            "that declares the per-row accumulator — think carefully about where it "
            "has to live.",
            _jscan(
                _RD_MAT
                + "        for (int r = 0; r < rows; r++) {\n"
                  "            int rowSum = 0;\n"
                  "            for (int c = 0; c < cols; c++) rowSum += m[r][c];\n"
                  "            System.out.println(rowSum);\n"
                  "        }"),
            "            int rowSum = 0;",
            [_mcase(m, _nl(*_rowsums(m)))
             for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[-1, 1], [10, -10], [0, 0]])],
            hints=["It has to start at 0 again for every row.",
                   "That means declaring it inside the outer loop.",
                   "`int rowSum = 0;`"]),

        _je("j2-agg-colsum", "One total per column",
            "Print the column sums on one line, space separated. The accumulator "
            "array is already allocated — replace `____` with the statement that "
            "adds the current cell into the right column's total.",
            _jscan(
                _RD_MAT
                + "        int[] colSum = new int[cols];\n"
                  "        for (int r = 0; r < rows; r++) {\n"
                  "            for (int c = 0; c < cols; c++) colSum[c] += m[r][c];\n"
                  "        }\n"
                  '        for (int c = 0; c < cols; c++) System.out.print(colSum[c] + " ");\n'
                  "        System.out.println();"),
            "colSum[c] += m[r][c];",
            [_mcase(m, _sp(_colsums(m)))
             for m in ([[1, 2, 3], [4, 5, 6]], [[7]], [[-1, 1], [10, -10], [0, 0]])],
            hints=["Which index selects the column's slot?",
                   "The accumulator is indexed by `c`, not by `r`.",
                   "`colSum[c] += m[r][c];`"]),

        _je("j2-agg-maxcell", "The biggest cell and where it is",
            "Print the largest value and its coordinates as `value row col` (the "
            "first one, scanning row-major). Replace `____` with the body that "
            "updates all three trackers together.",
            _jscan(
                _RD_MAT
                + "        int best = m[0][0];\n"
                  "        int bestR = 0;\n"
                  "        int bestC = 0;\n"
                  "        for (int r = 0; r < rows; r++) {\n"
                  "            for (int c = 0; c < cols; c++) {\n"
                  "                if (m[r][c] > best) { best = m[r][c]; bestR = r; bestC = c; }\n"
                  "            }\n"
                  "        }\n"
                  '        System.out.println(best + " " + bestR + " " + bestC);'),
            "if (m[r][c] > best) { best = m[r][c]; bestR = r; bestC = c; }",
            [_mcase(m, "%d %d %d" % _maxcell(m))
             for m in ([[1, 9, 3], [4, 5, 6]], [[-5, -2], [-9, -3]], [[7]],
                       [[4, 4], [4, 4]])],
            hints=["Three assignments have to happen together, inside one `if`.",
                   "Braces matter — without them only the first assignment is guarded.",
                   "`if (m[r][c] > best) { best = m[r][c]; bestR = r; bestC = c; }`"],
            difficulty="Medium"),

        _jfix("j2-agg-running", "Row totals that keep growing",
              "This should print each row's sum. On `{{1,2},{3,4}}` it prints `3` "
              "then `10` instead of `3` then `7` — the totals are accumulating across "
              "rows. Fix it.",
              _jscan(
                  _RD_MAT
                  + "        int rowSum = 0;\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < cols; c++) rowSum += m[r][c];\n"
                    "            System.out.println(rowSum);\n"
                    "        }"),
              _jscan(
                  _RD_MAT
                  + "        for (int r = 0; r < rows; r++) {\n"
                    "            int rowSum = 0;\n"
                    "            for (int c = 0; c < cols; c++) rowSum += m[r][c];\n"
                    "            System.out.println(rowSum);\n"
                    "        }"),
              [_mcase(m, _nl(*_rowsums(m)))
               for m in ([[1, 2], [3, 4]], [[5, 5, 5], [1, 1, 1], [0, 0, 0]])],
              hints=["When does `rowSum` go back to zero?",
                     "It is declared once, before any row starts.",
                     "Move `int rowSum = 0;` inside the outer loop."]),
    ],
    quiz=[
        _jq("`int[] colSum = new int[cols];` then `colSum[c] += m[r][c];` — why index by `c`?",
            ["Because the slot represents a column, and `c` identifies the column",
             "Because `r` might be out of range",
             "Because the array was allocated with `cols`, so only `c` compiles",
             "It should be `colSum[r]` — the lesson is wrong"],
            0,
            "The accumulator array has one slot per column, so the index has to be the "
            "column number. `colSum[r]` would compile whenever rows <= cols and give "
            "nonsense — a nasty class of bug."),
        _jq("With strict `>` in the max-cell scan, which cell wins when two share the maximum?",
            ["The one reached first in row-major order",
             "The last one", "The one nearest the top-right", "It is undefined"],
            0,
            "A later equal value fails `>`, so nothing moves. Use `>=` if you want the last."),
    ],
))

# --- 2.4 Diagonals and transpose -------------------------------------------

_M2.append(_jlesson(
    "m2-diagonal", "Diagonals, transpose, symmetry",
    "The index relationships worth memorising, and the in-place swap that goes wrong.",
    """
Square matrices come with a small vocabulary of index relationships. Learn the
three, and most matrix questions become one loop.

**The main diagonal is `r == c`:** `m[0][0], m[1][1], m[2][2], …`

```java
int sum = 0;
for (int i = 0; i < n; i++) sum += m[i][i];      // ONE loop, not two
```

**The anti-diagonal is `r + c == n - 1`:** top-right to bottom-left.

```java
int sum = 0;
for (int i = 0; i < n; i++) sum += m[i][n - 1 - i];
```

For odd `n` the two diagonals share the centre cell, which is the standard
follow-up question ("now sum both diagonals without double-counting the
middle").

**The transpose flips rows and columns: `t[c][r] = m[r][c]`.** It works for
any shape, but the result has the shape reversed, so it needs a **new** array:

```java
int[][] t = new int[cols][rows];                  // note the swapped dimensions
for (int r = 0; r < rows; r++)
    for (int c = 0; c < cols; c++)
        t[c][r] = m[r][c];
```

**Transposing in place** is only possible for a square matrix, and it has a
famous trap:

```java
for (int r = 0; r < n; r++)
    for (int c = r + 1; c < n; c++) {             // c = r + 1, NOT c = 0
        int t = m[r][c]; m[r][c] = m[c][r]; m[c][r] = t;
    }
```

If the inner loop starts at `0`, every pair gets swapped **twice** — once as
`(r, c)` and once as `(c, r)` — and the matrix comes back exactly as it
started. It is a silent, total no-op, and it catches almost everybody once.
Starting at `r + 1` visits each pair once and skips the diagonal, which never
needs to move.

**Symmetry** is transpose-equality without building the transpose:
`m[r][c] == m[c][r]` for every `r < c`. Same upper-triangle loop.
""",
    warmup=[
        _jq("For a 4×4 matrix, which cells are on the anti-diagonal?",
            ["[0][3], [1][2], [2][1], [3][0]",
             "[0][0], [1][1], [2][2], [3][3]",
             "[3][3], [2][2], [1][1], [0][0]",
             "[0][3], [1][3], [2][3], [3][3]"],
            0,
            "The anti-diagonal runs top-right to bottom-left, where `r + c == n - 1` — here "
            "`r + c == 3`."),
        _jq("An in-place transpose whose inner loop runs `for (int c = 0; c < n; c++)` produces…",
            ["the original matrix, unchanged",
             "the correct transpose",
             "an ArrayIndexOutOfBoundsException",
             "a matrix with the diagonal zeroed"],
            0,
            "Each pair is swapped once as (r,c) and again as (c,r), so every swap is undone. "
            "The fix is to start the inner loop at `r + 1`."),
    ],
    exercises=[
        _je("j2-diag-main", "Sum the main diagonal",
            "The grid is square. Print the sum of its main diagonal with a **single** "
            "loop. Replace `____` with the cell being added.",
            _jscan(
                _RD_MAT
                + "        int sum = 0;\n"
                  "        for (int i = 0; i < rows; i++) sum += m[i][i];\n"
                  "        System.out.println(sum);"),
            "m[i][i]",
            [_mcase(m, sum(m[i][i] for i in range(len(m))))
             for m in ([[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[5]])],
            hints=["On the main diagonal the row index and the column index are equal.",
                   "So both brackets get the same variable.",
                   "`m[i][i]`"],
            difficulty="Intro"),

        _je("j2-diag-anti", "Sum the anti-diagonal",
            "Same square grid, but sum the **anti**-diagonal — top-right down to "
            "bottom-left. Replace `____` with the cell being added.",
            _jscan(
                _RD_MAT
                + "        int sum = 0;\n"
                  "        for (int i = 0; i < rows; i++) sum += m[i][rows - 1 - i];\n"
                  "        System.out.println(sum);"),
            "m[i][rows - 1 - i]",
            [_mcase(m, sum(m[i][len(m) - 1 - i] for i in range(len(m))))
             for m in ([[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[5]])],
            hints=["The row and column indices have to add up to `n - 1`.",
                   "So if the row is `i`, the column is `n - 1 - i`.",
                   "`m[i][rows - 1 - i]`"]),

        _je("j2-diag-transpose", "Transpose into a new grid",
            "Build the transpose of a (possibly rectangular) grid and print it with "
            "`Arrays.deepToString`. The destination is already allocated with the "
            "dimensions swapped — replace `____` with the assignment that fills it.",
            _jscan(
                _RD_MAT
                + "        int[][] t = new int[cols][rows];\n"
                  "        for (int r = 0; r < rows; r++) {\n"
                  "            for (int c = 0; c < cols; c++) t[c][r] = m[r][c];\n"
                  "        }\n"
                  "        System.out.println(Arrays.deepToString(t));"),
            "t[c][r] = m[r][c];",
            [_mcase(m, _jdeep(_transpose(m)))
             for m in ([[1, 2, 3], [4, 5, 6]], [[1, 2], [3, 4]], [[7]])],
            hints=["The destination's indices are the source's, reversed.",
                   "Read from `m[r][c]`, write to the flipped position.",
                   "`t[c][r] = m[r][c];`"],
            difficulty="Medium"),

        _jfix("j2-diag-inplace", "The transpose that does nothing",
              "This transposes a square grid in place — except it prints the grid "
              "back exactly as it came in. One character in the inner loop is wrong. "
              "Fix it.",
              _jscan(
                  _RD_MAT
                  + "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < rows; c++) {\n"
                    "                int t = m[r][c];\n"
                    "                m[r][c] = m[c][r];\n"
                    "                m[c][r] = t;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(Arrays.deepToString(m));"),
              _jscan(
                  _RD_MAT
                  + "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = r + 1; c < rows; c++) {\n"
                    "                int t = m[r][c];\n"
                    "                m[r][c] = m[c][r];\n"
                    "                m[c][r] = t;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(Arrays.deepToString(m));"),
              [_mcase(m, _jdeep(_transpose(m)))
               for m in ([[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]])],
              hints=["Trace the pair (0,1) and then the pair (1,0). What happens to it?",
                     "Every swap is being performed twice, which undoes it.",
                     "Visit each pair once: start the inner loop at `r + 1`."],
              difficulty="Medium"),

        _jch("j2-diag-symmetric", "Is it symmetric?", "Medium",
             "Print `true` when the square grid equals its own transpose (that is, "
             "`m[r][c] == m[c][r]` for every pair), otherwise `false`. Do it without "
             "building the transpose. Write the whole block where you see `____`.",
             _jscan(
                 _RD_MAT
                 + "        boolean symmetric = true;\n"
                   "        for (int r = 0; r < rows; r++) {\n"
                   "            for (int c = r + 1; c < rows; c++) {\n"
                   "                if (m[r][c] != m[c][r]) symmetric = false;\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(symmetric);"),
             "        boolean symmetric = true;\n"
             "        for (int r = 0; r < rows; r++) {\n"
             "            for (int c = r + 1; c < rows; c++) {\n"
             "                if (m[r][c] != m[c][r]) symmetric = false;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(symmetric);",
             [_mcase(m, _jbool(all(m[r][c] == m[c][r]
                                   for r in range(len(m)) for c in range(len(m)))))
              for m in ([[1, 2], [2, 1]], [[1, 2], [3, 4]],
                        [[1, 7, 3], [7, 4, 5], [3, 5, 9]], [[5]])],
             hints=["Start optimistic: `boolean symmetric = true;` and let a mismatch knock it down.",
                    "Only the upper triangle needs checking — `c` from `r + 1` — because every "
                    "pair appears there exactly once.",
                    "The diagonal is always equal to itself, so it never needs a check."]),
    ],
    quiz=[
        _jq("Why can a rectangular matrix not be transposed in place?",
            ["The result has different dimensions, and an array's shape is fixed",
             "Because the diagonal is undefined",
             "It can, with a third loop",
             "Because `m[c][r]` always throws"],
            0,
            "Transposing a 2×3 gives a 3×2. There is nowhere to put it inside the original "
            "object, so you allocate `new int[cols][rows]`."),
        _jq("For an odd-sized square matrix, what do the two diagonals share?",
            ["The centre cell", "Nothing", "The whole first row", "Two cells"],
            0,
            "At `i == n/2` both `m[i][i]` and `m[i][n-1-i]` are the same cell — so 'sum both "
            "diagonals' has to subtract it once."),
    ],
))

# --- 2.5 Jagged and 3D arrays ----------------------------------------------

_M2.append(_jlesson(
    "m2-jagged", "Jagged and three-dimensional arrays",
    "Rows of different lengths, and what `new int[2][3][4]` really builds.",
    """
Because a 2D array is an array of row *references*, nothing requires the rows
to be the same length. An array with uneven rows is called **jagged**, and it
is often the honest shape for real data — a class where each student has a
different number of marks, a triangle, a calendar's weeks.

```java
int[][] rows = new int[3][];      // outer only: three NULL row references
rows[0] = new int[2];             // now row 0 exists, length 2
rows[1] = new int[5];             // row 1, length 5
rows[2] = new int[1];
```

Leaving out the second dimension is the whole trick: `new int[3][]` is legal,
`new int[][3]` is not. Until you assign a row, it is `null`, and touching it is
a `NullPointerException` rather than an out-of-bounds.

**A jagged literal** looks exactly how you would hope:

```java
int[][] tri = {{1}, {1, 1}, {1, 2, 1}};
```

**Traversing jagged data has one rule:** bound the inner loop with
`m[r].length`. `m[0].length` is not the width, because there is no width.

```java
for (int r = 0; r < m.length; r++)
    for (int c = 0; c < m[r].length; c++)     // per-row bound
        sum += m[r][c];
```

The enhanced `for` handles this for free, which is one of the few places it is
strictly nicer:

```java
for (int[] row : m)
    for (int x : row) sum += x;
```

**Three dimensions** is the same idea again. `new int[2][3][4]` is an array of
2 references to `int[3][4]` grids, each of which is 3 references to `int[4]`
rows — 24 `int` slots in total, plus 9 array objects. You index it
`cube[layer][row][col]`, and `Arrays.deepToString` still prints it.

In practice you meet 3D arrays as "a stack of grids" (frames of an image, days
of a week of a month). Past three dimensions, the honest answer in real code is
a class with named fields — which is Part 4 of the roadmap.
""",
    warmup=[
        _jq("Which of these compiles?",
            ["int[][] a = new int[3][];", "int[][] a = new int[][3];",
             "int[][] a = new int[][];", "int[][] a = new int[3][4][5];"],
            0,
            "You may leave later dimensions unspecified, never earlier ones — the outer "
            "array has to know how many references to hold."),
        _jq("`int[][] m = new int[3][];` — what is `m[0]`?",
            ["null", "an empty int[]", "int[0]", "It throws immediately"],
            0,
            "Only the outer array was allocated. Its slots hold the default for an object "
            "type, which is `null` — so `m[0].length` is a NullPointerException."),
    ],
    exercises=[
        _je("j2-jag-lengths", "How long is each row?",
            "The input describes a jagged grid: a row count, then for each row its "
            "length followed by its values. Print each row's length, one per line. "
            "Replace `____` with the expression for the current row's length.",
            _jscan(_RD_JAG
                   + "        for (int r = 0; r < rows; r++) System.out.println(m[r].length);"),
            "m[r].length",
            [_jagcase(g, _nl(*[len(r) for r in g]))
             for g in ([[1, 2], [3, 4, 5], [6]], [[9]], [[1], [2], [3]])],
            hints=["Each row is its own array with its own length.",
                   "Ask row `r` for it.",
                   "`m[r].length`"],
            difficulty="Intro"),

        _je("j2-jag-sum", "Total a jagged grid",
            "Sum every value in the jagged grid. Replace `____` with the inner loop "
            "header — the bound is the part that matters.",
            _jscan(
                _RD_JAG
                + "        int sum = 0;\n"
                  "        for (int r = 0; r < rows; r++) {\n"
                  "            for (int c = 0; c < m[r].length; c++) sum += m[r][c];\n"
                  "        }\n"
                  "        System.out.println(sum);"),
            "for (int c = 0; c < m[r].length; c++)",
            [_jagcase(g, sum(v for row in g for v in row))
             for g in ([[1, 2], [3, 4, 5], [6]], [[9]], [[-1, -2, -3], [10]])],
            hints=["`m[0].length` would be wrong — the rows are different lengths.",
                   "Bound the inner loop by the row you are actually on.",
                   "`for (int c = 0; c < m[r].length; c++)`"]),

        _jfix("j2-jag-bound", "Bounded by the wrong row",
              "This should total a jagged grid. It crashes (or quietly misses values) "
              "because the inner loop is bounded by row 0's length. Fix it.",
              _jscan(
                  _RD_JAG
                  + "        int sum = 0;\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < m[0].length; c++) sum += m[r][c];\n"
                    "        }\n"
                    "        System.out.println(sum);"),
              _jscan(
                  _RD_JAG
                  + "        int sum = 0;\n"
                    "        for (int r = 0; r < rows; r++) {\n"
                    "            for (int c = 0; c < m[r].length; c++) sum += m[r][c];\n"
                    "        }\n"
                    "        System.out.println(sum);"),
              [_jagcase(g, sum(v for row in g for v in row))
               for g in ([[1], [2, 3, 4]], [[5, 5], [1], [2, 2, 2]])],
              hints=["Row 0's length is not every row's length.",
                     "The bound must depend on `r`.",
                     "`c < m[r].length`"]),

        _jch("j2-jag-triangle", "Build a triangle", "Medium",
             "Read `n` and build a jagged grid where row `i` has `i + 1` slots, each "
             "holding `i + 1`. For `n = 3` that is `[[1], [2, 2], [3, 3, 3]]`. Print "
             "it with `Arrays.deepToString`. Write the whole block where you see `____`.",
             _jscan(
                 "        int n = sc.nextInt();\n"
                 "        int[][] tri = new int[n][];\n"
                 "        for (int i = 0; i < n; i++) {\n"
                 "            tri[i] = new int[i + 1];\n"
                 "            for (int c = 0; c < tri[i].length; c++) tri[i][c] = i + 1;\n"
                 "        }\n"
                 "        System.out.println(Arrays.deepToString(tri));"),
             "        int[][] tri = new int[n][];\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            tri[i] = new int[i + 1];\n"
             "            for (int c = 0; c < tri[i].length; c++) tri[i][c] = i + 1;\n"
             "        }\n"
             "        System.out.println(Arrays.deepToString(tri));",
             [_case(n, _jdeep([[i + 1] * (i + 1) for i in range(n)])) for n in (3, 1, 5)],
             hints=["`new int[n][]` gives you n null rows — allocate each one yourself.",
                    "Row `i` needs `new int[i + 1]`.",
                    "Fill it before moving on: every slot of row `i` holds `i + 1`."]),

        _jch("j2-3d-count", "Count a cube", "Easy",
             "Read three numbers `x y z`, allocate a `new int[x][y][z]`, write the "
             "value `1` into every cell with three nested loops, then print the total "
             "of every cell (which should be `x * y * z`). Do it by summing, not by "
             "multiplying. Write the whole block where you see `____`.",
             _jscan(
                 "        int x = sc.nextInt();\n"
                 "        int y = sc.nextInt();\n"
                 "        int z = sc.nextInt();\n"
                 "        int[][][] cube = new int[x][y][z];\n"
                 "        for (int i = 0; i < x; i++)\n"
                 "            for (int j = 0; j < y; j++)\n"
                 "                for (int k = 0; k < z; k++) cube[i][j][k] = 1;\n"
                 "        int total = 0;\n"
                 "        for (int i = 0; i < x; i++)\n"
                 "            for (int j = 0; j < y; j++)\n"
                 "                for (int k = 0; k < z; k++) total += cube[i][j][k];\n"
                 "        System.out.println(total);"),
             "        int[][][] cube = new int[x][y][z];\n"
             "        for (int i = 0; i < x; i++)\n"
             "            for (int j = 0; j < y; j++)\n"
             "                for (int k = 0; k < z; k++) cube[i][j][k] = 1;\n"
             "        int total = 0;\n"
             "        for (int i = 0; i < x; i++)\n"
             "            for (int j = 0; j < y; j++)\n"
             "                for (int k = 0; k < z; k++) total += cube[i][j][k];\n"
             "        System.out.println(total);",
             [_case(f"{x} {y} {z}", x * y * z)
              for (x, y, z) in ((2, 3, 4), (1, 1, 1), (3, 1, 5))],
             hints=["`int[][][] cube = new int[x][y][z];`",
                    "Three nested loops to write, three more to read — or one pair if you "
                    "prefer, but write it out the long way first.",
                    "Index it `cube[i][j][k]` — outermost dimension first."]),
    ],
    quiz=[
        _jq("`int[][] m = {{1}, {1, 1}, {1, 2, 1}};` — what is `m.length` and `m[2].length`?",
            ["3 and 3", "3 and 1", "6 and 3", "It does not compile — rows must match"],
            0,
            "Three rows, and the third row holds three values. Jagged literals are perfectly "
            "legal; nothing requires the rows to match."),
        _jq("How many `int` slots does `new int[2][3][4]` allocate?",
            ["24", "9", "234", "12"],
            0,
            "2 × 3 × 4 = 24 ints, held in 6 `int[4]` rows, held in 2 `int[3][4]` grids, held "
            "in one outer array."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m2_report(m):
    rows, cols = len(m), len(m[0])
    best, br, bc = _maxcell(m)
    diag = (str(sum(m[i][i] for i in range(rows))) if rows == cols else "none")
    return _nl(
        f"total={sum(sum(r) for r in m)}",
        f"rowsums={_sp(_rowsums(m))}",
        f"colsums={_sp(_colsums(m))}",
        f"max={best} {br} {bc}",
        f"diag={diag}",
    )


_M2_CAP = _jcap(
    "Matrix report",
    """
Everything in module 2, in one program.

Read `rows`, `cols`, then the grid. Print a five-line report, in exactly this
order:

```
total=<sum of every cell>
rowsums=<each row's total, space separated>
colsums=<each column's total, space separated>
max=<largest value> <its row> <its column>
diag=<main-diagonal sum, or the word `none` when the grid is not square>
```

The pieces you need are all from this module: a grand accumulator declared
before both loops, a per-row accumulator declared inside the outer loop, an
array of accumulators indexed by column, a three-variable max tracker, and the
single-loop diagonal.

Two details the hidden cases check:

- **`max` reports the first maximum in row-major order** — use strict `>`.
- **`diag=none` for a non-square grid.** The main diagonal is only defined when
  `rows == cols`; print the literal word `none` rather than a number.
""",
    _jch("j2-cap-report", "Matrix report", "Medium",
         "Write the whole report where you see `____` — five lines, in the order "
         "`total`, `rowsums`, `colsums`, `max`, `diag`.",
         _jscan(
             _RD_MAT
             + "        int total = 0;\n"
               "        for (int r = 0; r < rows; r++)\n"
               "            for (int c = 0; c < cols; c++) total += m[r][c];\n"
               '        System.out.println("total=" + total);\n'
               '        System.out.print("rowsums=");\n'
               "        for (int r = 0; r < rows; r++) {\n"
               "            int rowSum = 0;\n"
               "            for (int c = 0; c < cols; c++) rowSum += m[r][c];\n"
               '            System.out.print(rowSum + " ");\n'
               "        }\n"
               "        System.out.println();\n"
               "        int[] colSum = new int[cols];\n"
               "        for (int r = 0; r < rows; r++)\n"
               "            for (int c = 0; c < cols; c++) colSum[c] += m[r][c];\n"
               '        System.out.print("colsums=");\n'
               '        for (int c = 0; c < cols; c++) System.out.print(colSum[c] + " ");\n'
               "        System.out.println();\n"
               "        int best = m[0][0];\n"
               "        int bestR = 0;\n"
               "        int bestC = 0;\n"
               "        for (int r = 0; r < rows; r++) {\n"
               "            for (int c = 0; c < cols; c++) {\n"
               "                if (m[r][c] > best) { best = m[r][c]; bestR = r; bestC = c; }\n"
               "            }\n"
               "        }\n"
               '        System.out.println("max=" + best + " " + bestR + " " + bestC);\n'
               "        if (rows == cols) {\n"
               "            int diag = 0;\n"
               "            for (int i = 0; i < rows; i++) diag += m[i][i];\n"
               '            System.out.println("diag=" + diag);\n'
               "        } else {\n"
               '            System.out.println("diag=none");\n'
               "        }"),
         "        int total = 0;\n"
         "        for (int r = 0; r < rows; r++)\n"
         "            for (int c = 0; c < cols; c++) total += m[r][c];\n"
         '        System.out.println("total=" + total);\n'
         '        System.out.print("rowsums=");\n'
         "        for (int r = 0; r < rows; r++) {\n"
         "            int rowSum = 0;\n"
         "            for (int c = 0; c < cols; c++) rowSum += m[r][c];\n"
         '            System.out.print(rowSum + " ");\n'
         "        }\n"
         "        System.out.println();\n"
         "        int[] colSum = new int[cols];\n"
         "        for (int r = 0; r < rows; r++)\n"
         "            for (int c = 0; c < cols; c++) colSum[c] += m[r][c];\n"
         '        System.out.print("colsums=");\n'
         '        for (int c = 0; c < cols; c++) System.out.print(colSum[c] + " ");\n'
         "        System.out.println();\n"
         "        int best = m[0][0];\n"
         "        int bestR = 0;\n"
         "        int bestC = 0;\n"
         "        for (int r = 0; r < rows; r++) {\n"
         "            for (int c = 0; c < cols; c++) {\n"
         "                if (m[r][c] > best) { best = m[r][c]; bestR = r; bestC = c; }\n"
         "            }\n"
         "        }\n"
         '        System.out.println("max=" + best + " " + bestR + " " + bestC);\n'
         "        if (rows == cols) {\n"
         "            int diag = 0;\n"
         "            for (int i = 0; i < rows; i++) diag += m[i][i];\n"
         '            System.out.println("diag=" + diag);\n'
         "        } else {\n"
         '            System.out.println("diag=none");\n'
         "        }",
         [_mcase(m, _m2_report(m))
          for m in ([[1, 2, 3], [4, 5, 6]],
                    [[1, 2], [3, 4]],
                    [[7]],
                    [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]],
                    [[5, 5], [5, 5], [5, 5]])],
         hints=["Five separate concerns — write and test them one line of output at a time.",
                'For the space-separated lines, `System.out.print("rowsums=")` first, then '
                "the values, then a bare `System.out.println()`.",
                "`colsums` needs an `int[cols]` of accumulators indexed by `c`.",
                "`max` uses strict `>` so ties keep the earliest cell in row-major order.",
                "Guard the diagonal with `if (rows == cols)`, else print `diag=none`."]),
    example_io="stdin:  2 3\n        1 2 3\n        4 5 6\n\n"
               "stdout: total=21\n        rowsums=6 15\n        colsums=5 7 9\n"
               "        max=6 1 2\n        diag=none",
    rubric=[
        "`total` is accumulated once, before both loops.",
        "`rowsums` resets per row — the numbers are row totals, not running totals.",
        "`colsums` uses an array of accumulators indexed by column.",
        "`max` reports value, row and column, and keeps the first of a tie.",
        "`diag` prints `none`, not `0`, when the grid is not square.",
        "It survives a 1×1 grid and an all-negative grid.",
    ],
)


_MODULES.append(_jmod(
    2, 1, "Arrays, deeply",
    "2D and multidimensional arrays",
    "Get comfortable with grids: know that `int[][]` is an array of rows, walk it "
    "in either order without swapping your indices, aggregate by row and by column, "
    "and handle diagonals, transposes and jagged data.",
    """
Java has no 2D array — it has arrays of arrays. Almost everything that
surprises people about grids follows from that single fact, so this module
leans on it hard: `m.length` versus `m[0].length`, per-row bounds, jagged rows,
and why a shallow copy of a grid still shares its rows.

The mechanical skills — nested loops, an accumulator per row, an array of
accumulators per column, the diagonal index relationships — come back verbatim
in module 5 as 2D prefix sums.
""",
    _M2,
    capstone=_M2_CAP,
    objectives=[
        "Explain what `new int[3][4]` allocates and why `m[0].length` is the width.",
        "Print a grid legibly with `Arrays.deepToString`, and know why `toString` fails.",
        "Traverse row-major and column-major on purpose, and say which is faster and why.",
        "Aggregate a grid three ways: one total, one total per row, one total per column.",
        "Sum either diagonal in a single loop, and transpose a matrix in and out of place.",
        "Build and traverse jagged arrays with per-row bounds, and index a 3D array.",
    ],
    why="Grids are the shape of images, boards, spreadsheets, adjacency matrices and "
        "DP tables. Interview questions about matrices are usually not hard — they are "
        "index-discipline tests, and this module is that discipline.",
    est_minutes=300,
    glossary=[
        _jg("int[][]", "An array whose elements are `int[]` references. Java has no true "
                       "rectangular 2D array type."),
        _jg("row-major", "Traversal (and memory layout) where the column index changes "
                         "fastest: `m[0][0], m[0][1], m[0][2], m[1][0]…`"),
        _jg("column-major", "Traversal where the row index changes fastest. Same `m[r][c]` "
                            "expression — you swap the loops, not the indices."),
        _jg("jagged array", "A 2D array whose rows have different lengths. Made with "
                            "`new int[rows][]`, then a row assigned per slot."),
        _jg("main diagonal", "The cells where `r == c`, top-left to bottom-right."),
        _jg("anti-diagonal", "The cells where `r + c == n - 1`, top-right to bottom-left."),
        _jg("transpose", "The matrix with rows and columns exchanged: `t[c][r] = m[r][c]`. "
                         "A rectangular transpose needs a new array."),
        _jg("symmetric matrix", "A square matrix equal to its own transpose — "
                                "`m[r][c] == m[c][r]` for every pair."),
        _jg("Arrays.deepToString", "Prints nested arrays by recursing into them. Plain "
                                   "`toString` prints each row's `[I@…` tag instead."),
    ],
    cheatsheet="""
```java
// --- create -------------------------------------------------------------
int[][] a = new int[2][3];              // rectangular, zero-filled
int[][] b = {{1, 2, 3}, {4, 5, 6}};     // literal
int[][] j = new int[3][];               // jagged: 3 NULL rows
j[0] = new int[2];                       // ...allocate each row yourself
int[][][] cube = new int[2][3][4];       // 24 ints

a.length          // number of ROWS
a[r].length       // width of row r  (use this, not a[0].length)

// --- print --------------------------------------------------------------
Arrays.deepToString(a)                   // [[1, 2, 3], [4, 5, 6]]
Arrays.toString(a)                       // [[I@1b6d, [I@42a5   <- useless

// --- traverse -----------------------------------------------------------
for (int r = 0; r < a.length; r++)                  // ROW-MAJOR (prefer this)
    for (int c = 0; c < a[r].length; c++) { ... }

for (int c = 0; c < a[0].length; c++)               // COLUMN-MAJOR
    for (int r = 0; r < a.length; r++) { ... }      // a[r][c] either way!

for (int[] row : a) for (int x : row) { ... }       // read-only, jagged-safe

// --- aggregate ----------------------------------------------------------
int total = 0;                    // before BOTH loops
int rowSum = 0;                   // inside the OUTER loop  (resets per row)
int[] colSum = new int[cols];     // one accumulator per column, indexed by c

// --- diagonals (square only) -------------------------------------------
for (int i = 0; i < n; i++) main += m[i][i];             // r == c
for (int i = 0; i < n; i++) anti += m[i][n - 1 - i];     // r + c == n - 1

// --- transpose ----------------------------------------------------------
int[][] t = new int[cols][rows];                   // dimensions SWAPPED
for (r) for (c) t[c][r] = m[r][c];

for (int r = 0; r < n; r++)                        // in place, square only
    for (int c = r + 1; c < n; c++) {              // c = r + 1, or it no-ops
        int tmp = m[r][c]; m[r][c] = m[c][r]; m[c][r] = tmp;
    }
```
""",
    self_check=[
        "Can you say what `new int[3][]` allocates, and what `m[0]` holds straight afterwards?",
        "Can you write a column-major traversal without accidentally writing `m[c][r]`?",
        "Do you know where `int rowSum = 0;` goes, and what happens if you put it one level out?",
        "Can you explain why column sums need an array of accumulators?",
        "Can you write the anti-diagonal index expression without deriving it on paper?",
        "Can you say why an in-place transpose starts its inner loop at `r + 1`?",
        "Would you bound an inner loop with `m[0].length` on data you did not create?",
    ],
    review=[
        _jq("`int[][] m = new int[2][3];` — which of these throws?",
            ["m[2][0]", "m[1][2]", "m[0][0]", "m[1][0]"],
            0,
            "There are 2 rows, so the valid row indices are 0 and 1. Column indices run 0..2."),
        _jq("You are handed a jagged `int[][]`. Which inner-loop bound is always correct?",
            ["m[r].length", "m[0].length", "m.length", "cols, read from the input"],
            0,
            "Only the row you are on knows its own length. Everything else is an assumption "
            "that jagged data breaks."),
        _jq("What does `int[] alias = m[0];` give you?",
            ["A second name for row 0 — writing through it changes the grid",
             "A copy of row 0", "A compile error", "The first element of the grid"],
            0,
            "`m[0]` *is* a reference to the row array, so assigning it aliases exactly as in "
            "module 1. `m[0].clone()` would copy."),
        _jq("Sum both diagonals of a 5×5 matrix. What has to be handled specially?",
            ["The centre cell, which is on both diagonals",
             "The corners, which are counted twice",
             "Nothing — the two loops are independent",
             "The whole middle row"],
            0,
            "For odd n, `m[n/2][n/2]` satisfies both `r == c` and `r + c == n - 1`, so adding "
            "both diagonals counts it twice."),
    ],
    milestone="You can build, traverse, aggregate and transform grids — including jagged "
              "ones — without ever having to stop and work out which bracket is the row.",
))
