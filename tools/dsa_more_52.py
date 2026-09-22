# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 52 — Numbers, Bits & Grids, part 3: simulation and matrices.
#
#   transpose-matrix        rows become columns — the on-ramp to index algebra
#   diagonal-sums           i == j and i + j == n - 1, and the centre counted once
#   striped-wallpaper       every cell equals its up-left neighbour (constant i - j)
#   rotate-rings            each ring is a cycle: rotate by k mod its length
#   tilt-the-board          gravity as a two-pointer compaction, four directions
#   snake-on-grid           a deque for the body, a set for collisions
#   lamp-row-after-days     10^18 steps: find the cycle, jump over it
#
# Defines three shapes: `grid_cmd` (a character grid, then a command string),
# `snake` (a board size, a list of cells, then a move string) and `str_n`
# (a token, then a long).
# ===========================================================================

# "r c", r rows of characters, then one command string
_SHAPES["grid_cmd"] = dict(
    py="d = sys.stdin.read().split()\nr, c = int(d[0]), int(d[1])\ng = [list(row) for row in d[2:2 + r]]\n"
       "cmds = d[2 + r]\n",
    py_params="g, cmds",
    js=_JS_NUMS + "const r = Number(d[0]);\nconst g = d.slice(2, 2 + r).map(row => row.split(''));\n"
       "const cmds = d[2 + r];\n",
    js_params="g, cmds",
    java="        int r = sc.nextInt(), c = sc.nextInt();\n        char[][] g = new char[r][];\n"
         "        for (int i = 0; i < r; i++) g[i] = sc.next().toCharArray();\n"
         "        String cmds = sc.next();\n",
    java_params="char[][] g, String cmds", java_args="g, cmds",
)
# "r c f", then f lines "i j", then one move string
_SHAPES["snake"] = dict(
    py="d = sys.stdin.read().split()\nr, c, f = int(d[0]), int(d[1]), int(d[2])\n"
       "food = [(int(d[3 + 2 * i]), int(d[4 + 2 * i])) for i in range(f)]\nmoves = d[3 + 2 * f]\n",
    py_params="r, c, food, moves",
    js=_JS_NUMS + "const r = Number(d[0]), c = Number(d[1]), f = Number(d[2]);\n"
       "const food = Array.from({ length: f }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n"
       "const moves = d[3 + 2 * f];\n",
    js_params="r, c, food, moves",
    java="        int r = sc.nextInt(), c = sc.nextInt(), f = sc.nextInt();\n        int[][] food = new int[f][2];\n"
         "        for (int i = 0; i < f; i++) { food[i][0] = sc.nextInt(); food[i][1] = sc.nextInt(); }\n"
         "        String moves = sc.next();\n",
    java_params="int r, int c, int[][] food, String moves", java_args="r, c, food, moves",
)
# a token, then a long
_SHAPES["str_n"] = dict(
    py="d = sys.stdin.read().split()\ns = d[0]\nk = int(d[1])\n",
    py_params="s, k",
    js=_JS_NUMS + "const s = d[0], k = Number(d[1]);\n",
    js_params="s, k",
    java="        String s = sc.next();\n        long k = sc.nextLong();\n",
    java_params="String s, long k", java_args="s, k",
)


def _mat_case(rows, k=None):
    """A `matrix` (or, with k, `matrix_k`) input from a list of rows."""
    head = f"{len(rows)} {len(rows[0])}" + ("" if k is None else f" {k}")
    return head + "\n" + "".join(" ".join(map(str, r)) + "\n" for r in rows)


_p(
    "transpose-matrix", "Flip a Table on Its Diagonal", "Intro",
    topics=["Matrix"], subtopics=["Matrix", "Index Arithmetic"],
    companies=["Amazon", "Adobe"],
    shape="matrix", ret="String",
    todo="build a c x r result with t[j][i] = m[i][j], then print it row by row",
    description=(
        "A spreadsheet has `r` rows and `c` columns. Produce its **transpose**: the table whose "
        "row `j` is the original column `j`. The result has `c` rows and `r` columns.\n\n"
        "### Input\nLine 1: `r c`.\nNext `r` lines: `c` integers each.\n\n### Output\n`c` lines of "
        "`r` integers, separated by spaces."
    ),
    constraints="1 ≤ r, c ≤ 300\n-10^9 ≤ m[i][j] ≤ 10^9",
    hints=[
        "The cell in row i, column j moves to row j, column i.",
        "The result has a different shape unless the table is square: allocate `new int[c][r]`, not `new int[r][c]`.",
        "Loop over the original (i over rows, j over columns) and write `t[j][i] = m[i][j]`.",
    ],
    opt=("O(r · c)", "O(r · c)",
         "Every cell is copied once."),
    editorial=(
        "## The one thing this teaches\n**Index algebra, stated as a rule.** Every matrix "
        "transformation in this unit is a rule of the form “(i, j) goes to (i', j')”. Transpose is "
        "the simplest: (i, j) → (j, i).\n\n"
        "## Approach\n```java\nint[][] t = new int[c][r];          // the shape swaps too\n"
        "for (int i = 0; i < r; i++)\n    for (int j = 0; j < c; j++)\n        t[j][i] = m[i][j];\n```\n\n"
        "## In place?\nOnly for a square matrix: swap `a[i][j]` with `a[j][i]` for `j > i` — "
        "starting `j` at `i + 1`, or every pair is swapped twice and nothing changes. That loop "
        "is the first half of rotating a matrix by 90°."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    return "\\n".join(" ".join(str(m[i][j]) for i in range(r)) for j in range(c))
''',
    java='''
    static String solve(int[][] m) {
        int r = m.length, c = m[0].length;
        int[][] t = new int[c][r];
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                t[j][i] = m[i][j];
        StringBuilder sb = new StringBuilder();
        for (int j = 0; j < c; j++) {
            if (j > 0) sb.append('\\n');
            for (int i = 0; i < r; i++) {
                if (i > 0) sb.append(' ');
                sb.append(t[j][i]);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _mat_case([[1, 2, 3], [4, 5, 6]])),
        ("Example 2", _mat_case([[7]])),
    ],
    hidden=[
        ("A single row", _mat_case([[5, -1, 0, 9]])),
        ("A single column", _mat_case([[1], [2], [3]])),
        ("Square", _mat_case([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
        ("Extremes", _mat_case([[-1000000000, 1000000000], [0, 42]])),
        ("Tall", _mat_case([[i * 10 + j for j in range(3)] for i in range(12)])),
    ],
    expl=[
        "Column 0 (1, 4) becomes row 0; column 1 (2, 5) row 1; column 2 (3, 6) row 2.",
        "A 1 × 1 table is its own transpose.",
    ],
    prereqs=[
        ("grid", "A cell is (row, column); transposing swaps the two."),
        ("array_patterns", "Nested loops over a 2-D array, and allocating the result's shape."),
    ],
)


_p(
    "diagonal-sums", "Both Diagonals", "Easy",
    topics=["Matrix"], subtopics=["Matrix", "Diagonals"],
    companies=["Amazon", "Apple"],
    shape="matrix", ret="long",
    todo="add m[i][i] and m[i][n - 1 - i] for every i, then subtract the centre once when n is odd",
    description=(
        "Given an `n × n` board of numbers, add up every cell on either diagonal — top-left to "
        "bottom-right, and top-right to bottom-left. A cell on both diagonals counts **once**.\n\n"
        "### Input\nLine 1: `n n`.\nNext `n` lines: `n` integers each.\n\n### Output\nThe sum."
    ),
    constraints="1 ≤ n ≤ 500\n-10^9 ≤ m[i][j] ≤ 10^9",
    hints=[
        "The main diagonal is the cells with i == j. The other is i + j == n − 1.",
        "One loop over i visits both: m[i][i] and m[i][n − 1 − i].",
        "When n is odd, the two diagonals cross at the centre (n/2, n/2) and it was added twice. Values reach 10⁹ × 1000: use long.",
    ],
    opt=("O(n)", "O(1)",
         "2n − 1 or 2n cells; the rest of the board is never read."),
    editorial=(
        "## The one thing this teaches\n**Diagonals are equations.** `i − j` is constant along a "
        "↘ diagonal and `i + j` along a ↙ one. The two main diagonals are `i − j = 0` and "
        "`i + j = n − 1`, which is all this needs; the general form keys every diagonal of a "
        "board, and it is how N-Queens tracks attacked diagonals.\n\n"
        "## Approach\n```java\nlong sum = 0;\nfor (int i = 0; i < n; i++) sum += m[i][i] + (long) m[i][n - 1 - i];\n"
        "if (n % 2 == 1) sum -= m[n / 2][n / 2];   // counted twice\n```\n\n"
        "## Cost\nO(n), not O(n²): there is no reason to visit a cell that cannot be on a diagonal."
    ),
    py='''
def solve(m):
    n = len(m)
    s = sum(m[i][i] + m[i][n - 1 - i] for i in range(n))
    if n % 2:
        s -= m[n // 2][n // 2]
    return s
''',
    java='''
    static long solve(int[][] m) {
        int n = m.length;
        long sum = 0;
        for (int i = 0; i < n; i++) sum += (long) m[i][i] + m[i][n - 1 - i];
        if (n % 2 == 1) sum -= m[n / 2][n / 2];
        return sum;
    }
''',
    examples=[
        ("Example 1", _mat_case([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
        ("Example 2", _mat_case([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])),
    ],
    hidden=[
        ("One cell", _mat_case([[-7]])),
        ("Two by two", _mat_case([[1, 2], [3, 4]])),
        ("Large values", _mat_case([[1000000000] * 5 for _ in range(5)])),
        ("Negative centre", _mat_case([[0, 0, 0], [0, -5, 0], [0, 0, 0]])),
        ("Big odd board", _mat_case([[(i * 31 + j * 17) % 1000 - 500 for j in range(101)] for i in range(101)])),
    ],
    expl=[
        "1 + 5 + 9 on one diagonal, 3 + 7 on the other (5 is shared): 25.",
        "Four cells on each diagonal and none shared: 8.",
    ],
    prereqs=[
        ("grid", "Diagonals as i == j and i + j == n − 1."),
        ("overflow", "Up to 1000 values of 10⁹ — sum in long."),
    ],
)


_p(
    "striped-wallpaper", "Striped Wallpaper", "Easy",
    topics=["Matrix"], subtopics=["Matrix", "Diagonals"],
    companies=["Google", "Meta"],
    shape="matrix", ret="String",
    todo="every cell with i > 0 and j > 0 must equal m[i - 1][j - 1]",
    description=(
        "A wallpaper design is a grid of colour codes. It is **striped** if every diagonal running "
        "from top-left to bottom-right is a single colour. Is this design striped?\n\n"
        "### Input\nLine 1: `r c`.\nNext `r` lines: `c` integers each.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ r, c ≤ 500\n0 ≤ m[i][j] ≤ 10^9",
    hints=[
        "Walking each diagonal from its start works, but it needs care at the borders.",
        "Along a ↘ diagonal, `i − j` is constant, and each cell's predecessor on it is its up-left neighbour.",
        "So the whole condition is local: every cell not in the top row or left column equals `m[i − 1][j − 1]`.",
    ],
    opt=("O(r · c)", "O(1)",
         "One comparison per cell."),
    editorial=(
        "## The one thing this teaches\n**Turn a global property into a local one.** “Every "
        "diagonal is constant” sounds like walking r + c − 1 diagonals. It is equivalent to "
        "“every cell equals its up-left neighbour”, which is one loop with one comparison — and "
        "that version streams: it needs only the previous row, so it works on a board too large "
        "to hold.\n\n"
        "## Approach\n```java\nfor (int i = 1; i < r; i++)\n    for (int j = 1; j < c; j++)\n"
        "        if (m[i][j] != m[i - 1][j - 1]) return \"NO\";\nreturn \"YES\";\n```\n\n"
        "## Why local is enough\nEquality is transitive: if every cell equals its predecessor on "
        "the diagonal, every cell equals the diagonal's first cell.\n\n"
        "## The name\nA matrix constant along its diagonals is a **Toeplitz matrix**. Keying "
        "cells by `i − j` (↘) or `i + j` (↙) is the general tool."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    for i in range(1, r):
        for j in range(1, c):
            if m[i][j] != m[i - 1][j - 1]:
                return "NO"
    return "YES"
''',
    java='''
    static String solve(int[][] m) {
        for (int i = 1; i < m.length; i++)
            for (int j = 1; j < m[0].length; j++)
                if (m[i][j] != m[i - 1][j - 1]) return "NO";
        return "YES";
    }
''',
    examples=[
        ("Example 1", _mat_case([[3, 1, 4, 1], [5, 3, 1, 4], [9, 5, 3, 1]])),
        ("Example 2", _mat_case([[2, 7], [7, 7]])),
    ],
    hidden=[
        ("One cell", _mat_case([[5]])),
        ("One row", _mat_case([[1, 2, 3, 4, 5]])),
        ("One column", _mat_case([[1], [2], [3]])),
        ("Break in the last cell", _mat_case([[1, 2, 3], [4, 1, 2], [5, 4, 9]])),
        ("Anti-diagonals constant instead", _mat_case([[1, 2, 3], [2, 3, 4], [3, 4, 5]])),
        ("Large striped", _mat_case([[((j - i) * 7919) % 1000 for j in range(200)] for i in range(150)])),
    ],
    expl=[
        "Diagonals: [9], [5, 5], [3, 3, 3], [1, 1, 1], [4, 4], [1] — each a single colour.",
        "The diagonal (0, 0), (1, 1) holds 2 and 7.",
    ],
    prereqs=[
        ("grid", "Along a ↘ diagonal, i − j is constant; the predecessor of (i, j) is (i − 1, j − 1)."),
        ("iteration", "Start both loops at 1 so the neighbour always exists."),
    ],
)


_p(
    "rotate-rings", "Turn the Rings", "Medium",
    topics=["Matrix", "Simulation"], subtopics=["Matrix", "Simulation", "Rotation"],
    companies=["Microsoft", "Amazon"],
    shape="matrix_k", ret="String",
    todo="for each ring, list its cells clockwise from its top-left corner; with s = k mod length, the cell at position p receives the value from position p + s",
    description=(
        "An `r × c` grid is made of concentric **rings**: the outer border, the border of what is "
        "left inside, and so on. Rotate **every** ring counter-clockwise by `k` steps: each value "
        "moves `k` cells along its own ring, in the counter-clockwise direction.\n\n"
        "Both `r` and `c` are even, so every ring is a full rectangle.\n\n"
        "### Input\nLine 1: `r c k`.\nNext `r` lines: `c` integers each.\n\n### Output\nThe rotated "
        "grid: `r` lines of `c` integers, separated by spaces."
    ),
    constraints="2 ≤ r, c ≤ 200 (both even)\n1 ≤ k ≤ 10^9\n0 ≤ grid[i][j] ≤ 10^9",
    hints=[
        "Doing k single steps is up to 10⁹ × the ring length. A ring of length L returns to where it started after L steps.",
        "Flatten each ring into a list, clockwise from its top-left corner: top row →, right column ↓, bottom row ←, left column ↑.",
        "Rotating counter-clockwise by s = k mod L means position p now holds what was at position p + s (mod L). Write the list back in the same order.",
    ],
    opt=("O(r · c)", "O(r · c)",
         "Every cell is read and written once, whatever k is."),
    editorial=(
        "## The one thing this teaches\n**A 2-D rotation is a 1-D rotation in disguise.** Each "
        "ring, read in order, is a cyclic array — so the whole problem is: flatten, shift by "
        "k mod L, write back. The only real work is walking a rectangle's border without "
        "visiting a corner twice.\n\n"
        "## Walking ring t\n```java\nint top = t, left = t, bot = r - 1 - t, right = c - 1 - t;\n"
        "List<int[]> cells = new ArrayList<>();\n"
        "for (int j = left; j < right; j++) cells.add(new int[]{top, j});    // top, → (not the last corner)\n"
        "for (int i = top; i < bot; i++)    cells.add(new int[]{i, right});  // right, ↓\n"
        "for (int j = right; j > left; j--) cells.add(new int[]{bot, j});    // bottom, ←\n"
        "for (int i = bot; i > top; i--)    cells.add(new int[]{i, left});   // left, ↑\n```\n\n"
        "Each edge stops one short of its last corner, which the next edge starts from — every "
        "cell exactly once.\n\n"
        "## Shift\n```java\nint L = cells.size(), s = (int) (k % L);\n"
        "for (int p = 0; p < L; p++) out[cell(p)] = g[cell((p + s) % L)];\n```\n\n"
        "## Direction check\nOn a 2 × 2 ring 1 2 / 3 4, one counter-clockwise step moves 1 down "
        "to the bottom-left: the result is 2 4 / 1 3. Test the direction on the smallest case "
        "before trusting the formula — it is the bug this problem is most likely to hide."
    ),
    py='''
def solve(m, k):
    r, c = len(m), len(m[0])
    out = [row[:] for row in m]
    for t in range(min(r, c) // 2):
        top, left, bot, right = t, t, r - 1 - t, c - 1 - t
        cells = [(top, j) for j in range(left, right)]
        cells += [(i, right) for i in range(top, bot)]
        cells += [(bot, j) for j in range(right, left, -1)]
        cells += [(i, left) for i in range(bot, top, -1)]
        L = len(cells)
        s = k % L
        for p, (i, j) in enumerate(cells):
            a, b = cells[(p + s) % L]
            out[i][j] = m[a][b]
    return "\\n".join(" ".join(map(str, row)) for row in out)
''',
    java='''
    static String solve(int[][] m, int k) {
        int r = m.length, c = m[0].length;
        int[][] out = new int[r][c];
        for (int t = 0; t < Math.min(r, c) / 2; t++) {
            int top = t, left = t, bot = r - 1 - t, right = c - 1 - t;
            List<int[]> cells = new ArrayList<>();
            for (int j = left; j < right; j++) cells.add(new int[]{top, j});
            for (int i = top; i < bot; i++) cells.add(new int[]{i, right});
            for (int j = right; j > left; j--) cells.add(new int[]{bot, j});
            for (int i = bot; i > top; i--) cells.add(new int[]{i, left});
            int L = cells.size(), s = k % L;
            for (int p = 0; p < L; p++) {
                int[] to = cells.get(p), from = cells.get((p + s) % L);
                out[to[0]][to[1]] = m[from[0]][from[1]];
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++) {
            if (i > 0) sb.append('\\n');
            for (int j = 0; j < c; j++) {
                if (j > 0) sb.append(' ');
                sb.append(out[i][j]);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _mat_case([[1, 2], [3, 4]], 1)),
        ("Example 2", _mat_case([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 2)),
    ],
    hidden=[
        ("Full turn", _mat_case([[1, 2], [3, 4]], 4)),
        ("Wide", _mat_case([[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]], 3)),
        ("Tall", _mat_case([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]], 5)),
        ("Huge k", _mat_case([[i * 6 + j for j in range(6)] for i in range(4)], 1000000003)),
        ("Different ring lengths", _mat_case([[i * 8 + j for j in range(8)] for i in range(6)], 13)),
        ("Big", _mat_case([[(i * 131 + j * 71) % 1000 for j in range(40)] for i in range(30)], 999999937)),
    ],
    expl=[
        "One counter-clockwise step: 1 moves down, 3 moves right, 4 moves up, 2 moves left.",
        "The outer ring (12 cells) moves two steps; the inner ring 6 7 / 10 11 (4 cells) moves two steps, which swaps opposite corners.",
    ],
    prereqs=[
        ("grid", "Walk a rectangle's border edge by edge, each edge stopping before its last corner."),
        ("modulo", "A cycle of length L repeats every L steps: shift by k mod L."),
    ],
)


_p(
    "tilt-the-board", "Tilt the Board", "Medium",
    topics=["Matrix", "Simulation"], subtopics=["Simulation", "Two Pointers", "Matrix"],
    companies=["Google", "Amazon"],
    shape="grid_cmd", ret="String",
    todo="for each tilt, compact every row or column toward the wall: a write pointer is the next free cell, reset past each '#'",
    description=(
        "A board holds round stones `O`, fixed walls `#` and empty cells `.`. Tilting the board in "
        "a direction makes every stone roll that way until it hits the edge, a wall, or a stone "
        "that has already stopped.\n\n"
        "Apply a sequence of tilts: `L` (left), `R` (right), `U` (up) and `D` (down). Print the "
        "final board.\n\n"
        "### Input\nLine 1: `r c`.\nNext `r` lines: the board.\nLast line: the tilts, as one "
        "string.\n\n### Output\nThe final board, `r` lines."
    ),
    constraints="1 ≤ r, c ≤ 100\n1 ≤ number of tilts ≤ 100",
    hints=[
        "Tilting left affects each row independently, and each segment between walls independently.",
        "Within a row, scan left to right with a write pointer `free` = the leftmost cell a stone could still reach. A `#` resets `free` to just past it; an `O` moves to `free` and `free` advances.",
        "The other three directions are the same scan with the loops reversed or transposed. Moving a stone means clearing its old cell first, in case it is also its new cell.",
    ],
    opt=("O(t · r · c)", "O(1)",
         "Each tilt is one linear compaction pass per row or column."),
    editorial=(
        "## The one thing this teaches\n**Gravity is a stable compaction.** Rolling every stone "
        "left is the same pass as “move zeroes to the end”: a write pointer marks the next slot, "
        "stones are written there in order, and a wall starts a new segment. No stone is moved "
        "more than once per tilt, and nothing is simulated cell by cell.\n\n"
        "## One tilt, left\n```java\nfor (int i = 0; i < r; i++) {\n    int free = 0;\n"
        "    for (int j = 0; j < c; j++) {\n        if (g[i][j] == '#') free = j + 1;\n"
        "        else if (g[i][j] == 'O') { g[i][j] = '.'; g[i][free++] = 'O'; }\n    }\n}\n```\n\n"
        "Clear first, then write: when a stone is already at `free`, the two cells are the same "
        "and the stone must survive.\n\n"
        "## The other directions\nRight: scan j from c − 1 down, `free` decreasing. Up and down: "
        "the same over columns. Writing one helper that takes a list of cells in rolling order "
        "avoids four copies of the loop — the ring walk in `rotate-rings` uses the same trick.\n\n"
        "## Why not step by step?\nMoving each stone one cell per iteration until nothing moves "
        "is O(size) iterations per tilt, each over the whole board, and the order you move them "
        "in changes the result unless you are careful. The compaction has neither problem."
    ),
    py='''
def solve(g, cmds):
    r, c = len(g), len(g[0])

    def roll(cells):
        free = 0
        for idx, (i, j) in enumerate(cells):
            if g[i][j] == "#":
                free = idx + 1
            elif g[i][j] == "O":
                g[i][j] = "."
                a, b = cells[free]
                g[a][b] = "O"
                free += 1

    for d in cmds:
        if d in "LR":
            for i in range(r):
                cells = [(i, j) for j in range(c)]
                roll(cells if d == "L" else cells[::-1])
        else:
            for j in range(c):
                cells = [(i, j) for i in range(r)]
                roll(cells if d == "U" else cells[::-1])
    return "\\n".join("".join(row) for row in g)
''',
    java='''
    static void roll(char[][] g, int[][] cells) {
        int free = 0;
        for (int idx = 0; idx < cells.length; idx++) {
            int i = cells[idx][0], j = cells[idx][1];
            if (g[i][j] == '#') free = idx + 1;
            else if (g[i][j] == 'O') {
                g[i][j] = '.';
                g[cells[free][0]][cells[free][1]] = 'O';
                free++;
            }
        }
    }

    static String solve(char[][] g, String cmds) {
        int r = g.length, c = g[0].length;
        for (char d : cmds.toCharArray()) {
            if (d == 'L' || d == 'R') {
                for (int i = 0; i < r; i++) {
                    int[][] cells = new int[c][];
                    for (int j = 0; j < c; j++) cells[j] = new int[]{i, d == 'L' ? j : c - 1 - j};
                    roll(g, cells);
                }
            } else {
                for (int j = 0; j < c; j++) {
                    int[][] cells = new int[r][];
                    for (int i = 0; i < r; i++) cells[i] = new int[]{d == 'U' ? i : r - 1 - i, j};
                    roll(g, cells);
                }
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++) {
            if (i > 0) sb.append('\\n');
            sb.append(g[i]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3 5\nO.#.O\n.O..O\nO...#\nL\n"),
        ("Example 2", "3 3\nO.O\n.#.\nO.O\nDR\n"),
    ],
    hidden=[
        ("One cell", "1 1\nO\nU\n"),
        ("Walls only", "2 2\n##\n##\nLRUD\n"),
        ("Full row", "1 4\nOOOO\nRL\n"),
        ("Column with walls", "6 1\nO\n.\n#\nO\nO\n.\nD\n"),
        ("Spin cycle", "4 4\nO..#\n.O..\n#..O\n..O.\nURDLURDL\n"),
        ("Large", "30 30\n" + "".join(
            "".join("#" if (i * 7 + j * 13) % 11 == 0 else ("O" if (i * 5 + j * 3) % 4 == 0 else ".")
                    for j in range(30)) + "\n" for i in range(30)) + "LURDDRUL" * 5 + "\n"),
    ],
    expl=[
        "Row 0: the stone left of the wall stays at 0, the one right of it rolls to column 3. Row 1: both stones roll to columns 0 and 1. Row 2 already has its stone at the edge.",
        "Down: in each outer column the lower stone is already on the bottom edge, so the upper one falls onto it and stops in row 1. Right: in row 1 the wall and the edge hold both stones; row 2 packs against the right edge.",
    ],
    prereqs=[
        ("simulation", "Apply each tilt fully before the next one."),
        ("two_pointers", "A write pointer compacts stones toward the wall in one pass."),
    ],
)


_p(
    "snake-on-grid", "Snake on a Grid", "Medium",
    topics=["Simulation", "Queue"], subtopics=["Simulation", "Deque", "Hash Set"],
    companies=["Amazon", "Microsoft"],
    shape="snake", ret="String",
    todo="body as a deque of cells plus a set for collisions; per move: out of bounds → dead; if not eating, pop the tail first; then a head in the set → dead",
    description=(
        "A snake of length 1 starts at the top-left cell `(0, 0)` of an `r × c` board. Food "
        "appears one piece at a time, at the cells given in order: when a piece is eaten, the next "
        "one appears.\n\n"
        "Each move (`U`, `D`, `L`, `R`) moves the head one cell:\n\n"
        "1. If the head leaves the board, the snake dies.\n"
        "2. If the head reaches the current food, the snake grows by one — its tail stays put — "
        "and the score goes up by one.\n"
        "3. Otherwise the tail moves forward first, so the head may enter the cell the tail just "
        "left.\n"
        "4. If the head then lands on its own body, the snake dies.\n\n"
        "### Input\nLine 1: `r c f`.\nNext `f` lines: the food cells `i j`, in order of "
        "appearance.\nLast line: the moves, as one string.\n\n### Output\n`ALIVE s` if the snake "
        "survives every move with score `s`, or `DEAD t s` if it dies on move `t` (1-based) "
        "having scored `s`."
    ),
    constraints="1 ≤ r, c ≤ 1000\n0 ≤ f ≤ 10000\n1 ≤ number of moves ≤ 100000\nA piece of food never appears on the snake, and none is at (0, 0).",
    hints=[
        "The body changes at both ends: the head is added at the front, the tail removed at the back. That is a deque.",
        "Checking “is the head on the body?” by scanning the deque is O(length) per move. Keep a hash set of occupied cells beside it.",
        "Order matters: when not eating, remove the tail from the set **before** checking the head, so chasing your own tail is legal.",
    ],
    opt=("O(moves)", "O(length)",
         "Each move is O(1) deque and hash-set work."),
    editorial=(
        "## The one thing this teaches\n**A simulation is only as fast as its state.** The rules "
        "are simple; what makes this problem pass or time out is choosing a structure for each "
        "question the rules ask. “Where is the tail?” is a deque. “Is this cell occupied?” is a "
        "set. Together each move is O(1).\n\n"
        "## Approach\n```java\nDeque<Integer> body = new ArrayDeque<>();   // cell id = i * c + j, head first\n"
        "Set<Integer> occupied = new HashSet<>();\nbody.add(0); occupied.add(0);\n"
        "for (int t = 1; t <= moves.length(); t++) {\n    // new head (hi, hj) from the move\n"
        "    if (hi < 0 || hi >= r || hj < 0 || hj >= c) return \"DEAD \" + t + \" \" + score;\n"
        "    boolean eat = fi < food.length && food[fi][0] == hi && food[fi][1] == hj;\n"
        "    if (!eat) occupied.remove(body.pollLast());     // the tail moves first\n"
        "    int id = hi * c + hj;\n"
        "    if (!occupied.add(id)) return \"DEAD \" + t + \" \" + score;\n"
        "    body.addFirst(id);\n    if (eat) { score++; fi++; }\n}\nreturn \"ALIVE \" + score;\n```\n\n"
        "## The order of the rules is the problem\nRemove the tail before testing the head, or a "
        "snake following its own tail around a square dies on a move that is legal. Encode each "
        "cell as `i * c + j` so the set holds plain integers rather than arrays (which Java would "
        "compare by identity)."
    ),
    py='''
def solve(r, c, food, moves):
    from collections import deque
    body = deque([(0, 0)])
    occ = {(0, 0)}
    fi = score = 0
    step = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    for t, mv in enumerate(moves, 1):
        di, dj = step[mv]
        hi, hj = body[0][0] + di, body[0][1] + dj
        if not (0 <= hi < r and 0 <= hj < c):
            return f"DEAD {t} {score}"
        eat = fi < len(food) and food[fi] == (hi, hj)
        if not eat:
            occ.discard(body.pop())
        if (hi, hj) in occ:
            return f"DEAD {t} {score}"
        occ.add((hi, hj))
        body.appendleft((hi, hj))
        if eat:
            score += 1
            fi += 1
    return f"ALIVE {score}"
''',
    java='''
    static String solve(int r, int c, int[][] food, String moves) {
        ArrayDeque<Integer> body = new ArrayDeque<>();
        HashSet<Integer> occupied = new HashSet<>();
        body.add(0);
        occupied.add(0);
        int fi = 0, score = 0;
        for (int t = 1; t <= moves.length(); t++) {
            char mv = moves.charAt(t - 1);
            int head = body.peekFirst(), hi = head / c, hj = head % c;
            if (mv == 'U') hi--; else if (mv == 'D') hi++; else if (mv == 'L') hj--; else hj++;
            if (hi < 0 || hi >= r || hj < 0 || hj >= c) return "DEAD " + t + " " + score;
            boolean eat = fi < food.length && food[fi][0] == hi && food[fi][1] == hj;
            if (!eat) occupied.remove(body.pollLast());
            int id = hi * c + hj;
            if (!occupied.add(id)) return "DEAD " + t + " " + score;
            body.addFirst(id);
            if (eat) { score++; fi++; }
        }
        return "ALIVE " + score;
    }
''',
    examples=[
        ("Example 1", "3 3 2\n0 2\n2 2\nRRDD\n"),
        ("Example 2", "2 3 1\n0 1\nRRU\n"),
    ],
    hidden=[
        ("No food", "2 2 0\nRDLU\n"),
        ("Chasing its tail", "2 2 1\n0 1\nRDLURDLU\n"),
        ("Bites itself", "3 3 4\n0 1\n0 2\n1 2\n1 1\nRRDLU\n"),
        ("Wall on the first move", "5 5 1\n2 2\nL\n"),
        ("Long line", "1 8 6\n0 1\n0 2\n0 3\n0 4\n0 5\n0 6\nRRRRRRR\n"),
        ("Reverse into the neck", "1 6 2\n0 1\n0 2\nRRRL\n"),
        ("Length two may reverse", "1 5 1\n0 1\nRRL\n"),
        ("Long survival", "4 4 3\n0 1\n1 1\n3 3\n" + "RDLU" * 1 + "RRRDDDLLLUUU" * 20 + "\n"),
    ],
    expl=[
        "The snake eats at (0, 2) after two moves (length 2), then at (2, 2) after four (length 3). It never hits anything: score 2.",
        "It eats at (0, 1), moves to (0, 2), then `U` leaves the board on move 3.",
    ],
    prereqs=[
        ("queue", "A deque holds the body: add the head at the front, drop the tail at the back."),
        ("hashing", "A hash set answers “is this cell occupied?” in O(1)."),
    ],
)


_p(
    "lamp-row-after-days", "Lamps After N Nights", "Hard",
    topics=["Simulation", "Bit Manipulation"], subtopics=["Simulation", "Cycle Detection", "Bitmask"],
    companies=["Google", "Amazon"],
    shape="str_n", ret="String",
    todo="encode the row as a bitmask, next = ((s << 1) ^ (s >> 1)) & full; remember the night each state was first seen, and on a repeat skip whole cycles",
    description=(
        "A row of `w` lamps is shown as a string of `0`s (off) and `1`s (on). Every night, all "
        "lamps change **at once**: a lamp is on the next morning exactly when **one** of its two "
        "neighbours is on tonight (the positions beyond the ends count as off).\n\n"
        "What does the row look like after `n` nights?\n\n"
        "### Input\nOne line: the row, then `n`.\n\n### Output\nThe row after `n` nights."
    ),
    constraints="1 ≤ w ≤ 16\n0 ≤ n ≤ 10^18",
    hints=[
        "Simulating 10¹⁸ nights directly is impossible. But there are only 2ʷ ≤ 65,536 possible rows.",
        "So some row must repeat within 2ʷ + 1 nights, and from then on the sequence cycles. Record the night each row was first seen.",
        "When night `t` produces a row first seen on night `s`, the cycle has length `t − s`. Skip (n − t) mod (t − s) more nights and stop. As a bitmask, one night is `((x << 1) ^ (x >> 1)) & (2ʷ − 1)`.",
    ],
    opt=("O(2ʷ)", "O(2ʷ)",
         "At most 2ʷ nights are simulated before a state repeats, however large n is."),
    editorial=(
        "## The one thing this teaches\n**A deterministic process on a finite state space must "
        "cycle.** Once you know that, “after 10¹⁸ steps” stops being a simulation question and "
        "becomes a bookkeeping one: find the cycle, then take n modulo its length.\n\n"
        "## One night as bit operations\nPut lamp i in bit i. A lamp's two neighbours are the "
        "bits shifted in from each side, and “exactly one is on” is XOR:\n\n"
        "```java\nint next = ((x << 1) ^ (x >> 1)) & full;   // full = (1 << w) - 1 drops bit w\n```\n\n"
        "## Cycle detection\n```java\nlong[] seen = new long[1 << w];\nArrays.fill(seen, -1);\n"
        "long t = 0;\nwhile (t < n) {\n    if (seen[x] >= 0) {                     // x was the state on night seen[x]\n"
        "        long len = t - seen[x];\n        long left = (n - t) % len;\n"
        "        for (long i = 0; i < left; i++) x = step(x);\n        return x;\n    }\n"
        "    seen[x] = t;\n    x = step(x);\n    t++;\n}\nreturn x;\n```\n\n"
        "## Why it cannot be done by recognising a pattern\nThe cycle length depends on w in an "
        "irregular way (this rule — Wolfram's rule 90 — has periods tied to the multiplicative "
        "order of 2 modulo w + 1). Let the program find it.\n\n"
        "## Cost\nAt most 2ʷ + 1 distinct states are visited before a repeat, then at most one "
        "cycle's worth of extra steps: O(2ʷ) time and an array of 2ʷ entries."
    ),
    py='''
def solve(s, k):
    w = len(s)
    full = (1 << w) - 1
    x = int(s[::-1], 2)
    seen = {}
    t = 0
    while t < k:
        if x in seen:
            left = (k - t) % (t - seen[x])
            for _ in range(left):
                x = ((x << 1) ^ (x >> 1)) & full
            break
        seen[x] = t
        x = ((x << 1) ^ (x >> 1)) & full
        t += 1
    return "".join("1" if x >> i & 1 else "0" for i in range(w))
''',
    java='''
    static String solve(String s, long n) {
        int w = s.length(), full = (1 << w) - 1, x = 0;
        for (int i = 0; i < w; i++) if (s.charAt(i) == '1') x |= 1 << i;
        long[] seen = new long[1 << w];
        Arrays.fill(seen, -1);
        long t = 0;
        while (t < n) {
            if (seen[x] >= 0) {
                long left = (n - t) % (t - seen[x]);
                for (long i = 0; i < left; i++) x = ((x << 1) ^ (x >> 1)) & full;
                break;
            }
            seen[x] = t;
            x = ((x << 1) ^ (x >> 1)) & full;
            t++;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < w; i++) sb.append((x >> i & 1) == 1 ? '1' : '0');
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "0100 1\n"),
        ("Example 2", "10000 3\n"),
    ],
    hidden=[
        ("No nights", "1011 0\n"),
        ("One lamp", "1 1000000000000000000\n"),
        ("All dark", "0000000000000000 999999999999999999\n"),
        ("Fixed width 16", "1000000000000001 1000000000000000000\n"),
        ("Width 14", "10110011100011 123456789012345678\n"),
        ("Width 12 all on", "111111111111 1000000000000000000\n"),
        ("Short cycle", "11010 17\n"),
        ("A pre-period, then a cycle", "00001 1000000000000000000\n"),
        ("Before any repeat", "1000000000 11\n"),
    ],
    expl=[
        "Lamp 0 has lamp 1 on as a neighbour, lamp 2 has lamp 1 on, lamp 1's neighbours are both off, and lamp 3's are off: 1010.",
        "10000 → 01000 → 10100 → 00010. On the third night lamp 1 has both neighbours on, and exactly-one-on means it goes dark.",
    ],
    prereqs=[
        ("simulation", "Every lamp reads tonight's row; tomorrow's is written separately."),
        ("bit_manip", "The whole row updates in one expression: ((x << 1) ^ (x >> 1)) & full."),
    ],
)
