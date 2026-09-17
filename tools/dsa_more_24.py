# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 24 — foundations to middle: branching, digits, matrices, counting.
#
#   triangle-type                  order the checks so each branch assumes the ones before
#   self-dividing-numbers          peel digits with % 10, rejecting zeros first
#   lucky-numbers-matrix           row minima and column maxima, computed once each
#   image-smoother                 clamp the 3 × 3 neighbourhood at the borders
#   valid-tic-tac-toe              counts and winners must agree with alternating turns
#   number-of-good-pairs           a value seen c times before adds c pairs
#   sum-subarray-ranges            sum of maxima minus sum of minima, via contribution counting
#   reveal-cards-increasing        simulate the reveal on positions, then fill them in order
#   count-good-numbers             independent positions multiply; fast power for n = 10^15
#   fraction-to-recurring-decimal  long division repeats exactly when a remainder repeats
# ===========================================================================

_p(
    "triangle-type", "Triangle Type", "Easy",
    topics=["Math"], subtopics=["Conditionals"], companies=["Amazon"],
    shape="arr", ret="String", todo="reject impossible triangles first; then all equal, then any two equal, otherwise scalene",
    description=(
        "Three side lengths are given. Print:\n\n"
        "- `None` if they cannot form a triangle (the two shorter sides must add up to **more** than the longest),\n"
        "- `Equilateral` if all three sides are equal,\n"
        "- `Isosceles` if exactly two are equal,\n"
        "- `Scalene` otherwise.\n\n"
        "### Input\n- Line 1: `3`.\n- Line 2: the three side lengths.\n\n"
        "### Output\nOne of the four words."
    ),
    constraints="1 ≤ side ≤ 10^9",
    hints=[
        "Which check must come first? An equal-sided shape that cannot close is still not a triangle.",
        "The triangle inequality only needs one comparison if you know which side is longest: a + b > c with c the largest.",
        "After that, test all-equal before any-two-equal — otherwise an equilateral triangle would be reported as isosceles.",
    ],
    opt=("O(1)", "O(1)", "A handful of comparisons."),
    editorial=(
        "## The one thing this teaches\n**Order branches from most specific to least.** "
        "`Equilateral` is a special case of \"two sides equal\", so it must be tested first; and "
        "\"not a triangle\" overrides everything, so it comes before both.\n\n"
        "## Approach\n```java\nlong a = s[0], b = s[1], c = s[2];\n"
        "if (a + b <= c || a + c <= b || b + c <= a) return \"None\";\n"
        "if (a == b && b == c) return \"Equilateral\";\n"
        "if (a == b || b == c || a == c) return \"Isosceles\";\nreturn \"Scalene\";\n```\n\n"
        "## Degenerate triangles\n`1 2 3` has `1 + 2 = 3`: the three points lie on a line. "
        "The inequality is strict, so this is `None`.\n\n"
        "## Use long\nWith sides up to 10^9, `a + b` can reach 2·10^9 — past the largest int."
    ),
    py='''
def solve(a):
    x, y, z = sorted(a)
    if x + y <= z:
        return "None"
    distinct = len(set(a))
    return {1: "Equilateral", 2: "Isosceles", 3: "Scalene"}[distinct]
''',
    java='''
    static String solve(int[] s) {
        long a = s[0], b = s[1], c = s[2];
        if (a + b <= c || a + c <= b || b + c <= a) return "None";
        if (a == b && b == c) return "Equilateral";
        if (a == b || b == c || a == c) return "Isosceles";
        return "Scalene";
    }
''',
    examples=[("Example 1", "3\n3 3 3\n"), ("Example 2", "3\n3 4 5\n")],
    hidden=[
        ("Two equal", "3\n5 5 8\n"),
        ("Degenerate", "3\n1 2 3\n"),
        ("Equal sides that cannot close", "3\n2 2 5\n"),
        ("Long side first", "3\n10 3 4\n"),
        ("Near overflow", "3\n1000000000 1000000000 1000000000\n"),
    ],
    expl=[
        "All three sides are equal.",
        "3 + 4 > 5 and no two sides are equal.",
    ],
    prereqs=[
        ("iteration", "An if / else-if chain where each branch may assume the earlier ones failed."),
        ("overflow", "Adding two sides of up to 10^9."),
    ],
)

_p(
    "self-dividing-numbers", "Self Dividing Numbers", "Easy",
    topics=["Math"], subtopics=["Digits"], companies=["Adobe"],
    shape="two", ret="String", todo="for each number, peel digits with % 10: a zero digit, or one that does not divide the number, rejects it",
    description=(
        "A **self-dividing number** contains no zero digit and is divisible by every one of its "
        "digits — for example 128 (divisible by 1, 2 and 8). Print every self-dividing number "
        "from `left` to `right`, inclusive.\n\n"
        "### Input\nOne line: `left right`.\n\n"
        "### Output\nThe numbers in increasing order, separated by spaces — or `NONE`."
    ),
    constraints="1 ≤ left ≤ right ≤ 10^4",
    hints=[
        "Test each number in the range separately.",
        "The last digit of v is v % 10, and v / 10 removes it.",
        "Check for a zero digit before using it as a divisor — n % 0 is an error.",
    ],
    opt=("O((right − left) · log right)", "O(1)", "Each number has at most five digits to test."),
    editorial=(
        "## The one thing this teaches\n**Peel digits with `% 10` and `/ 10`, and guard the "
        "divisor.** Digit loops are the bread and butter of number problems; the one trap here is "
        "a zero digit, which must be rejected before it is used in `n % d`.\n\n"
        "## Approach\n```java\nboolean selfDividing(int n) {\n    for (int v = n; v > 0; v /= 10) {\n"
        "        int d = v % 10;\n        if (d == 0 || n % d != 0) return false;   // order matters: d == 0 first\n    }\n"
        "    return true;\n}\n```\n\n"
        "## Why `d == 0` must come first\n`||` stops at the first true operand. With `d == 0` "
        "checked first, `n % d` is never evaluated for a zero digit — swap them and the program "
        "throws `ArithmeticException` on 10."
    ),
    py='''
def solve(x, y):
    out = [v for v in range(x, y + 1) if "0" not in str(v) and all(v % int(ch) == 0 for ch in str(v))]
    return " ".join(map(str, out)) if out else "NONE"
''',
    java='''
    static boolean selfDividing(long n) {
        for (long v = n; v > 0; v /= 10) {
            long d = v % 10;
            if (d == 0 || n % d != 0) return false;
        }
        return true;
    }

    static String solve(long left, long right) {
        StringBuilder sb = new StringBuilder();
        for (long n = left; n <= right; n++)
            if (selfDividing(n)) { if (sb.length() > 0) sb.append(' '); sb.append(n); }
        return sb.length() == 0 ? "NONE" : sb.toString();
    }
''',
    examples=[("Example 1", "1 22\n"), ("Example 2", "47 85\n")],
    hidden=[
        ("Single zero-containing number", "10 10\n"),
        ("Three digits", "100 130\n"),
        ("Top of the range", "9999 10000\n"),
        ("Single digit", "7 7\n"),
    ],
    expl=[
        "Every single digit qualifies; then 11, 12, 15 and 22. Numbers such as 10 and 20 contain a zero.",
        "48 (by 4 and 8), 55, 66 and 77.",
    ],
    prereqs=[
        ("math_digits", "Extracting digits with % 10 and / 10."),
        ("iteration", "Short-circuit evaluation to guard a division."),
    ],
)

_p(
    "lucky-numbers-matrix", "Lucky Numbers in a Matrix", "Easy",
    topics=["Arrays", "Matrix"], subtopics=["Row and Column Extremes"], companies=["Amazon"],
    shape="matrix", ret="String", todo="compute each row's minimum and each column's maximum once; a cell equal to both is lucky",
    description=(
        "A matrix holds **distinct** numbers. A number is **lucky** if it is the minimum of its "
        "row and the maximum of its column. Print all lucky numbers in increasing order, or `NONE`.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers each.\n\n"
        "### Output\nThe lucky numbers, or `NONE`."
    ),
    constraints="1 ≤ r, c ≤ 50\n1 ≤ value ≤ 10^5, all distinct",
    hints=[
        "Scanning the row and the column for every cell costs O(r · c · (r + c)).",
        "Every cell's test uses the same row minima and column maxima. Compute them once.",
        "Then a cell is lucky when m[i][j] == rowMin[i] and m[i][j] == colMax[j].",
    ],
    opt=("O(r · c)", "O(r + c)", "Two passes to fill the extremes, one to test."),
    editorial=(
        "## The one thing this teaches\n**Precompute what every check shares.** The naive test "
        "rescans a row and a column per cell. Those scans repeat the same work r · c times; "
        "storing one minimum per row and one maximum per column removes the repetition.\n\n"
        "## Approach\n```java\nint[] rowMin = new int[r], colMax = new int[c];\nArrays.fill(rowMin, Integer.MAX_VALUE);\n"
        "for (int i = 0; i < r; i++)\n    for (int j = 0; j < c; j++) {\n"
        "        rowMin[i] = Math.min(rowMin[i], m[i][j]);\n        colMax[j] = Math.max(colMax[j], m[i][j]);\n    }\n"
        "// lucky: m[i][j] == rowMin[i] && m[i][j] == colMax[j]\n```\n\n"
        "## At most one\nWith distinct values there is never more than one lucky number. If `a` "
        "(row i, column j) and `b` (row k, column l) were both lucky, `a ≤ m[i][l] ≤ b` and "
        "`b ≤ m[k][j] ≤ a`, so `a = b`."
    ),
    py='''
def solve(m):
    out = []
    for i, row in enumerate(m):
        for j, v in enumerate(row):
            if v == min(row) and v == max(r[j] for r in m):
                out.append(v)
    return " ".join(map(str, sorted(out))) if out else "NONE"
''',
    java='''
    static String solve(int[][] m) {
        int r = m.length, c = m[0].length;
        int[] rowMin = new int[r], colMax = new int[c];
        Arrays.fill(rowMin, Integer.MAX_VALUE);
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                rowMin[i] = Math.min(rowMin[i], m[i][j]);
                colMax[j] = Math.max(colMax[j], m[i][j]);
            }
        List<Integer> out = new ArrayList<>();
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if (m[i][j] == rowMin[i] && m[i][j] == colMax[j]) out.add(m[i][j]);
        if (out.isEmpty()) return "NONE";
        Collections.sort(out);
        StringBuilder sb = new StringBuilder();
        for (int v : out) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3 3\n3 7 8\n9 11 13\n15 16 17\n"),
        ("Example 2", "3 4\n1 10 4 2\n9 3 8 7\n15 16 17 12\n"),
    ],
    hidden=[
        ("Single cell", "1 1\n5\n"),
        ("None", "2 2\n1 4\n3 2\n"),
        ("Bottom-right", "2 2\n1 2\n4 3\n"),
        ("Single row", "1 4\n9 2 7 5\n"),
    ],
    expl=[
        "15 is the smallest in its row and the largest in its column.",
        "12 is the smallest of 15 16 17 12 and the largest of 2 7 12.",
    ],
    prereqs=[
        ("grid", "Row and column indexing in a 2D array."),
        ("prefix_max", "Running minima and maxima, one per row and one per column."),
    ],
)

_p(
    "image-smoother", "Image Smoother", "Easy",
    topics=["Arrays", "Matrix", "Simulation"], subtopics=["Neighbourhood"], companies=["Amazon"],
    shape="matrix", ret="String", todo="for each cell, sum the in-bounds cells of its 3 × 3 block and divide by how many there were (rounding down)",
    description=(
        "Smooth a grayscale image: each output pixel is the **average, rounded down**, of the "
        "pixel and its up-to-8 neighbours that lie inside the image. Every output value is "
        "computed from the **original** image.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers each.\n\n"
        "### Output\n`r` lines of `c` integers."
    ),
    constraints="1 ≤ r, c ≤ 200\n0 ≤ pixel ≤ 255",
    hints=[
        "Corner pixels have 4 cells in their block, edge pixels 6, inner pixels 9.",
        "Loop over the offsets −1..1 in both directions and skip positions outside the image, counting the ones you keep.",
        "Write into a new matrix — updating in place would feed already-smoothed values into later cells.",
    ],
    opt=("O(r · c)", "O(r · c)", "Nine neighbours per cell; a separate output matrix."),
    editorial=(
        "## The one thing this teaches\n**Neighbourhood loops need a bounds check and a separate "
        "output.** Both mistakes are silent: an out-of-range read crashes only at the borders, "
        "and in-place updates give plausible-looking but wrong numbers.\n\n"
        "## Approach\n```java\nint[][] out = new int[r][c];\nfor (int i = 0; i < r; i++)\n"
        "    for (int j = 0; j < c; j++) {\n        int sum = 0, count = 0;\n"
        "        for (int di = -1; di <= 1; di++)\n            for (int dj = -1; dj <= 1; dj++) {\n"
        "                int x = i + di, y = j + dj;\n"
        "                if (x < 0 || y < 0 || x >= r || y >= c) continue;\n"
        "                sum += m[x][y]; count++;\n            }\n"
        "        out[i][j] = sum / count;\n    }\n```\n\n"
        "## The same shape elsewhere\nGame of Life, Minesweeper counts and blur filters all use "
        "this loop. Only the rule applied to the neighbours changes."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    out = []
    for i in range(r):
        row = []
        for j in range(c):
            block = [m[x][y] for x in range(max(0, i - 1), min(r, i + 2)) for y in range(max(0, j - 1), min(c, j + 2))]
            row.append(sum(block) // len(block))
        out.append(" ".join(map(str, row)))
    return "\\n".join(out)
''',
    java='''
    static String solve(int[][] m) {
        int r = m.length, c = m[0].length;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                int sum = 0, count = 0;
                for (int di = -1; di <= 1; di++)
                    for (int dj = -1; dj <= 1; dj++) {
                        int x = i + di, y = j + dj;
                        if (x < 0 || y < 0 || x >= r || y >= c) continue;
                        sum += m[x][y];
                        count++;
                    }
                if (j > 0) sb.append(' ');
                sb.append(sum / count);
            }
            if (i < r - 1) sb.append('\\n');
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3 3\n1 1 1\n1 0 1\n1 1 1\n"),
        ("Example 2", "3 3\n100 200 100\n200 50 200\n100 200 100\n"),
    ],
    hidden=[
        ("Single pixel", "1 1\n7\n"),
        ("Single row", "1 4\n10 20 30 40\n"),
        ("Single column", "3 1\n255\n0\n255\n"),
        ("Rectangle", "2 3\n0 255 0\n255 0 255\n"),
    ],
    expl=[
        "The centre averages 8/9 → 0; the corners average 3/4 → 0; the edges average 5/6 → 0.",
        "The top-left corner averages (100 + 200 + 200 + 50) / 4 = 137; the centre averages all nine cells, 1250 / 9 = 138.",
    ],
    prereqs=[
        ("grid", "Neighbour offsets with bounds checks."),
        ("simulation", "Reading from the original and writing to a new matrix."),
    ],
)

_p(
    "valid-tic-tac-toe", "Valid Tic-Tac-Toe State", "Medium",
    topics=["Simulation", "Matrix"], subtopics=["Game Rules"], companies=["Microsoft", "Amazon"],
    shape="grid", ret="String", todo="count X and O, find who has a line; X moves first and the game stops at the first win",
    description=(
        "A 3 × 3 board shows `X`, `O` and `.` (empty). Print `YES` if the position can occur in a "
        "real game, otherwise `NO`.\n\n"
        "Players alternate, **X moves first**, and the game ends immediately when a player "
        "completes a row, column or diagonal (or the board is full).\n\n"
        "### Input\n- Line 1: `3 3`.\n- Next 3 lines: the rows.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="The board is 3 × 3 and contains only X, O and .",
    hints=[
        "Since X starts and turns alternate, the counts must satisfy x == o or x == o + 1.",
        "If X has a line, X made the last move: x == o + 1. If O has a line, O made the last move: x == o.",
        "Those rules also rule out both players winning, since the two count conditions cannot hold together. A double line for one player is fine — one move can complete two.",
    ],
    opt=("O(1)", "O(1)", "Nine cells and eight lines to check."),
    editorial=(
        "## The one thing this teaches\n**Validate a state by its invariants, not by replaying "
        "history.** Searching every game that could lead here works (there are only 5478 "
        "reachable boards), but three facts about turns and wins decide it directly.\n\n"
        "## Approach\n```java\nint x = count('X'), o = count('O');\n"
        "if (o > x || x > o + 1) return false;          // alternating turns, X first\n"
        "boolean xWins = wins('X'), oWins = wins('O');\n"
        "if (xWins && x != o + 1) return false;         // X's win must be X's last move\n"
        "if (oWins && x != o) return false;             // O's win must be O's last move\nreturn true;\n```\n\n"
        "## Why both-win is already excluded\n`xWins` needs `x == o + 1` and `oWins` needs "
        "`x == o`. Both cannot hold, so a board where both players have lines always fails one of "
        "the checks.\n\n"
        "## Two lines at once\n`XXX / XOO / XOO` is legal: X's fifth move, in the corner, "
        "completes the top row and the left column simultaneously."
    ),
    py='''
def solve(g):
    board = "".join("".join(row) for row in g)
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

    def won(b):
        return any(b[i] != "." and b[i] == b[j] == b[k] for i, j, k in lines)

    seen = {"........."}
    frontier = ["........."]
    while frontier:
        nxt = []
        for b in frontier:
            if won(b):
                continue
            player = "X" if b.count("X") == b.count("O") else "O"
            for i in range(9):
                if b[i] == ".":
                    nb = b[:i] + player + b[i + 1:]
                    if nb not in seen:
                        seen.add(nb)
                        nxt.append(nb)
        frontier = nxt
    return "YES" if board in seen else "NO"
''',
    java='''
    static boolean wins(char[][] g, char p) {
        for (int i = 0; i < 3; i++) {
            if (g[i][0] == p && g[i][1] == p && g[i][2] == p) return true;
            if (g[0][i] == p && g[1][i] == p && g[2][i] == p) return true;
        }
        return (g[0][0] == p && g[1][1] == p && g[2][2] == p) || (g[0][2] == p && g[1][1] == p && g[2][0] == p);
    }

    static String solve(char[][] g) {
        int x = 0, o = 0;
        for (char[] row : g) for (char ch : row) { if (ch == 'X') x++; else if (ch == 'O') o++; }
        if (o > x || x > o + 1) return "NO";
        if (wins(g, 'X') && x != o + 1) return "NO";
        if (wins(g, 'O') && x != o) return "NO";
        return "YES";
    }
''',
    examples=[
        ("Example 1", "3 3\nO..\n...\n...\n"),
        ("Example 2", "3 3\nXOX\n.X.\n...\n"),
        ("Example 3", "3 3\nXOX\nO.O\nXOX\n"),
    ],
    hidden=[
        ("Empty board", "3 3\n...\n...\n...\n"),
        ("O moved after X won", "3 3\nXXX\nOO.\nO..\n"),
        ("Both have lines", "3 3\nXXX\n...\nOOO\n"),
        ("X wins cleanly", "3 3\nXXX\nOO.\n...\n"),
        ("O wins cleanly", "3 3\nXX.\nOOO\nX..\n"),
        ("One move, two lines", "3 3\nXXX\nXOO\nXOO\n"),
    ],
    expl=[
        "O cannot move first.",
        "X has three marks to O's one — X moved twice in a row.",
        "Four of each plus the centre empty: X has one more move to make, and nobody has a line.",
    ],
    prereqs=[
        ("simulation", "Encoding the rules of a game as checks on a board."),
        ("grid", "Scanning rows, columns and diagonals of a small matrix."),
    ],
)

_p(
    "number-of-good-pairs", "Number of Good Pairs", "Easy",
    topics=["Hashing", "Arrays"], subtopics=["Counting"], companies=["Amazon", "Microsoft"],
    shape="arr", ret="long", todo="walk once with a count map; each value pairs with every earlier copy of itself",
    description=(
        "A pair `(i, j)` is **good** if `i < j` and `a[i] == a[j]`. Print the number of good "
        "pairs.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of good pairs."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Two nested loops check n(n − 1)/2 pairs — 5·10^9 at n = 10^5.",
        "When you reach a value that has appeared c times before, it forms exactly c new good pairs.",
        "Keep a count map. Add count[x] to the answer, then increment count[x]. Use long — all-equal input gives about 5·10^9 pairs.",
    ],
    opt=("O(n)", "O(n)", "One pass with a hash map."),
    editorial=(
        "## The one thing this teaches\n**Count pairs by their second element.** Every pair is "
        "discovered exactly once — at its later index — by asking how many matching partners "
        "came before. That turns an O(n²) enumeration into one pass.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> seen = new HashMap<>();\nlong pairs = 0;\n"
        "for (int x : a) {\n    int c = seen.getOrDefault(x, 0);\n    pairs += c;            // x pairs with each earlier copy\n"
        "    seen.put(x, c + 1);\n}\n```\n\n"
        "## The closed form\nA value appearing `c` times contributes `c(c − 1)/2` pairs — the "
        "same total, computed after counting. The running version is the same sum `0 + 1 + … + (c − 1)`, "
        "added one term at a time.\n\n"
        "## Why this is a complexity lesson\nThe answer can be 5·10^9, far more than the "
        "10^5 steps the algorithm takes. Counting pairs does not require visiting them."
    ),
    py='''
def solve(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] == a[j])
''',
    java='''
    static long solve(int[] a) {
        HashMap<Integer, Integer> seen = new HashMap<>();
        long pairs = 0;
        for (int x : a) {
            int c = seen.getOrDefault(x, 0);
            pairs += c;
            seen.put(x, c + 1);
        }
        return pairs;
    }
''',
    examples=[("Example 1", "6\n1 2 3 1 1 3\n"), ("Example 2", "4\n1 1 1 1\n")],
    hidden=[
        ("All distinct", "3\n1 2 3\n"),
        ("Single element", "1\n5\n"),
        ("Negative values", "5\n-1 -1 2 -1 2\n"),
        ("Two groups", "6\n7 7 7 8 8 8\n"),
    ],
    expl=[
        "The three 1s form 3 pairs and the two 3s form 1: 4.",
        "Four equal values form 4 · 3 / 2 = 6 pairs.",
    ],
    prereqs=[
        ("hashing", "A running count per value."),
        ("big_o", "Counting n² pairs without enumerating them."),
    ],
)

_p(
    "sum-subarray-ranges", "Sum of Subarray Ranges", "Medium",
    topics=["Stacks", "Arrays"], subtopics=["Monotonic Stack", "Contribution Technique"], companies=["Amazon", "Google"],
    shape="arr", ret="long", todo="sum of subarray maxima minus sum of subarray minima; each element's share comes from its previous and next greater (or smaller)",
    description=(
        "The **range** of a subarray is its maximum minus its minimum. Print the sum of the "
        "ranges of all non-empty subarrays.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe sum."
    ),
    constraints="1 ≤ n ≤ 1000\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Extending each start to the right while tracking max and min is O(n²) — fast enough at n = 1000. Can you do O(n)?",
        "The sum of ranges is (sum of all subarray maxima) − (sum of all subarray minima). Those split apart.",
        "a[i] is the maximum of (i − prevGreater) · (nextGreaterOrEqual − i) subarrays. Monotonic stacks give both boundaries in one pass.",
    ],
    opt=("O(n)", "O(n)", "Two monotonic-stack passes: one for maxima, one for minima."),
    editorial=(
        "## The one thing this teaches\n**Sum over subarrays by asking what each element "
        "contributes.** Instead of visiting n² subarrays, count for each element how many "
        "subarrays it is the maximum of — a product of how far it can stretch left and right.\n\n"
        "## Approach (the maxima half)\n```java\nlong sumMax = 0;\nDeque<Integer> st = new ArrayDeque<>();\n"
        "for (int i = 0; i <= n; i++) {\n    while (!st.isEmpty() && (i == n || a[st.peek()] <= a[i])) {\n"
        "        int mid = st.pop();\n        int left = st.isEmpty() ? -1 : st.peek();\n"
        "        sumMax += (long) a[mid] * (mid - left) * (i - mid);   // mid is the max of that many subarrays\n    }\n"
        "    st.push(i);\n}\n// sumMin: the same with >=, then answer = sumMax − sumMin\n```\n\n"
        "## Ties\nWith equal values, each subarray must be credited to exactly one of them. "
        "Popping on `<=` makes the *rightmost* equal element the owner — whichever rule you "
        "choose, the left side must be strict and the right side not, or vice versa.\n\n"
        "## Walkthrough: 1 2 3\nSubarray maxima sum: 1 + 2 + 3 + 2 + 3 + 3 = 14. Minima: "
        "1 + 2 + 3 + 1 + 2 + 1 = 10. Ranges sum to 4."
    ),
    py='''
def solve(a):
    total = 0
    for i in range(len(a)):
        hi = lo = a[i]
        for j in range(i, len(a)):
            hi = max(hi, a[j])
            lo = min(lo, a[j])
            total += hi - lo
    return total
''',
    java='''
    static long contribution(int[] a, boolean max) {
        int n = a.length;
        long sum = 0;
        ArrayDeque<Integer> st = new ArrayDeque<>();
        for (int i = 0; i <= n; i++) {
            while (!st.isEmpty() && (i == n || (max ? a[st.peek()] <= a[i] : a[st.peek()] >= a[i]))) {
                int mid = st.pop();
                int left = st.isEmpty() ? -1 : st.peek();
                sum += (long) a[mid] * (mid - left) * (i - mid);
            }
            st.push(i);
        }
        return sum;
    }

    static long solve(int[] a) {
        return contribution(a, true) - contribution(a, false);
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "3\n1 3 3\n"), ("Example 3", "5\n4 -2 -3 4 1\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All equal", "4\n2 2 2 2\n"),
        ("Zigzag", "4\n5 1 4 2\n"),
        ("Extremes", "3\n1000000000 -1000000000 1000000000\n"),
    ],
    expl=[
        "Ranges: [1] 0, [2] 0, [3] 0, [1 2] 1, [2 3] 1, [1 2 3] 2. Total 4.",
        "Ranges: [1 3] 2, [3 3] 0, [1 3 3] 2; single elements add 0. Total 4.",
        "Summing max − min over all 15 subarrays gives 59.",
    ],
    prereqs=[
        ("stack", "Monotonic stacks that find the previous and next greater or smaller element."),
        ("big_o", "Replacing an O(n²) enumeration with per-element contributions."),
    ],
)

_p(
    "reveal-cards-increasing", "Reveal Cards in Increasing Order", "Medium",
    topics=["Queues", "Simulation", "Sorting"], subtopics=["Queue Simulation"], companies=["Google"],
    shape="arr", ret="String", todo="simulate the reveal on a queue of positions; the i-th revealed position receives the i-th smallest card",
    description=(
        "Cards with distinct values will be revealed like this: reveal the top card and remove "
        "it; if cards remain, move the next top card to the bottom; repeat until the deck is "
        "empty.\n\n"
        "Arrange the deck (top first) so that the cards are **revealed in increasing order**.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` card values.\n\n"
        "### Output\nThe deck from top to bottom, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ value ≤ 10^6, all distinct",
    hints=[
        "The reveal order of positions does not depend on the card values — only on n.",
        "Simulate the process on a queue of positions 0..n−1: take the front (revealed), then move the next front to the back.",
        "The k-th position revealed must hold the k-th smallest card. Sort the cards and write them into those positions.",
    ],
    opt=("O(n log n)", "O(n)", "Sorting dominates; the simulation is O(n) queue operations."),
    editorial=(
        "## The one thing this teaches\n**Simulate the process on positions, then fill in the "
        "values.** The procedure moves cards around without looking at them, so running it on "
        "placeholder indices reveals where each value must go.\n\n"
        "## Approach\n```java\nArrays.sort(cards);\nDeque<Integer> q = new ArrayDeque<>();\n"
        "for (int i = 0; i < n; i++) q.add(i);\nint[] deck = new int[n];\n"
        "for (int card : cards) {\n    deck[q.poll()] = card;             // this position is revealed next\n"
        "    if (!q.isEmpty()) q.add(q.poll()); // the following one goes to the bottom\n}\n```\n\n"
        "## The reverse construction\nAlternatively build the deck backwards from the largest "
        "card: before placing each card on top, move the bottom card to the top — the reveal "
        "steps undone in reverse order.\n\n"
        "## Walkthrough (Example 1)\nSorted: 2 3 5 7 11 13 17. Positions are revealed in the order "
        "0, 2, 4, 6, 3, 1, 5, so deck[0] = 2, deck[2] = 3, deck[4] = 5, deck[6] = 7, deck[3] = 11, "
        "deck[1] = 13, deck[5] = 17."
    ),
    py='''
def solve(a):
    dq = deque()
    for card in sorted(a, reverse=True):
        if dq:
            dq.appendleft(dq.pop())
        dq.appendleft(card)
    return " ".join(map(str, dq))
''',
    java='''
    static String solve(int[] cards) {
        int n = cards.length;
        Arrays.sort(cards);
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < n; i++) q.add(i);
        int[] deck = new int[n];
        for (int card : cards) {
            deck[q.poll()] = card;
            if (!q.isEmpty()) q.add(q.poll());
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(' '); sb.append(deck[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "7\n17 13 11 2 3 5 7\n"), ("Example 2", "2\n1 1000\n")],
    hidden=[
        ("One card", "1\n5\n"),
        ("Four cards", "4\n4 3 2 1\n"),
        ("Five cards", "5\n10 20 30 40 50\n"),
        ("Six cards", "6\n6 5 4 3 2 1\n"),
    ],
    expl=[
        "Reveal 2, move 13 down; reveal 3, move 11; reveal 5, move 17; reveal 7, move 13; reveal 11, move 17; reveal 13; reveal 17.",
        "Reveal 1, move 1000 to the bottom, reveal 1000.",
    ],
    prereqs=[
        ("queue", "A FIFO queue that replays the reveal-and-move-to-bottom process."),
        ("sorting", "Assigning sorted values to positions in reveal order."),
    ],
)

_p(
    "count-good-numbers", "Count Good Numbers", "Medium",
    topics=["Math"], subtopics=["Fast Exponentiation", "Counting"], companies=["Google"],
    shape="n", ret="long", todo="5 choices at each even index and 4 at each odd index: 5^ceil(n/2) · 4^floor(n/2) mod 10^9+7, with fast power",
    description=(
        "A digit string (leading zeros allowed) is **good** if every digit at an **even index** "
        "(0-based) is even — 0, 2, 4, 6 or 8 — and every digit at an **odd index** is prime — "
        "2, 3, 5 or 7. Print the number of good digit strings of length `n`, modulo `10^9 + 7`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe count modulo 10^9 + 7."
    ),
    constraints="1 ≤ n ≤ 10^15",
    hints=[
        "Each position is chosen independently, so the choices multiply.",
        "There are ⌈n / 2⌉ even indices (5 choices each) and ⌊n / 2⌋ odd indices (4 choices each).",
        "n is up to 10^15 — multiplying one factor at a time is too slow. Square-and-multiply computes x^e in O(log e).",
    ],
    opt=("O(log n)", "O(1)", "Two fast exponentiations."),
    editorial=(
        "## The one thing this teaches\n**Independent choices multiply; huge exponents need "
        "squaring.** The counting is one line — the multiplication principle. The engineering is "
        "raising to a power of 10^15 without 10^15 multiplications.\n\n"
        "## Approach\n```java\nstatic final long MOD = 1_000_000_007L;\n\nlong power(long base, long e) {\n"
        "    long result = 1;\n    base %= MOD;\n    while (e > 0) {\n"
        "        if ((e & 1) == 1) result = result * base % MOD;\n        base = base * base % MOD;   // base^(2^k)\n"
        "        e >>= 1;\n    }\n    return result;\n}\n\n"
        "return power(5, (n + 1) / 2) * power(4, n / 2) % MOD;\n```\n\n"
        "## Why the products stay in range\nBoth factors are below 10^9 + 7, so their product is "
        "below about 1.0·10^18 — inside a signed 64-bit long (up to 9.2·10^18). Reduce after every "
        "multiplication.\n\n"
        "## Walkthrough: n = 4\nIndices 0 and 2 are even (5 · 5), indices 1 and 3 are odd "
        "(4 · 4): 25 · 16 = 400."
    ),
    py='''
def solve(n):
    MOD = 10**9 + 7
    return pow(5, (n + 1) // 2, MOD) * pow(4, n // 2, MOD) % MOD
''',
    java='''
    static final long MOD = 1_000_000_007L;

    static long power(long base, long e) {
        long result = 1;
        base %= MOD;
        while (e > 0) {
            if ((e & 1) == 1) result = result * base % MOD;
            base = base * base % MOD;
            e >>= 1;
        }
        return result;
    }

    static long solve(long n) {
        return power(5, (n + 1) / 2) * power(4, n / 2) % MOD;
    }
''',
    examples=[("Example 1", "1\n"), ("Example 2", "4\n"), ("Example 3", "50\n")],
    hidden=[
        ("Two digits", "2\n"),
        ("Three digits", "3\n"),
        ("Enormous length", "1000000000000000\n"),
        ("Odd enormous length", "999999999999999\n"),
    ],
    expl=[
        "The single digit sits at index 0: 0, 2, 4, 6 or 8.",
        "5 · 4 · 5 · 4 = 400.",
        "5^25 · 4^25, reduced modulo 10^9 + 7.",
    ],
    prereqs=[
        ("modulo", "Reducing after every multiplication to stay inside 64 bits."),
        ("recurrence", "Square-and-multiply: x^e from x^(e/2)."),
    ],
)

_p(
    "fraction-to-recurring-decimal", "Fraction to Recurring Decimal", "Medium",
    topics=["Math", "Hashing", "Strings"], subtopics=["Long Division"], companies=["Google", "Meta"],
    shape="two", ret="String", todo="long division on absolute values; remember the output position of each remainder — a repeat marks the cycle",
    description=(
        "Print the fraction `numerator / denominator` as a decimal. If the fractional part "
        "repeats, enclose the repeating block in parentheses — for example `1/6` is `0.1(6)` and "
        "`4/333` is `0.(012)`. Integers print with no decimal point.\n\n"
        "### Input\nOne line: `numerator denominator`.\n\n"
        "### Output\nThe decimal representation."
    ),
    constraints="-2^31 ≤ numerator, denominator ≤ 2^31 − 1\ndenominator ≠ 0",
    hints=[
        "Do long division by hand: the next digit is (remainder · 10) / denominator, and the remainder becomes (remainder · 10) % denominator.",
        "The digits depend only on the remainder. Once a remainder repeats, the digits from its first appearance repeat forever.",
        "Map each remainder to the position in the output where its digit was written. On a repeat, insert '(' at that position and append ')'. Handle the sign separately, with longs.",
    ],
    opt=("O(denominator)", "O(denominator)", "At most |denominator| distinct remainders before one repeats."),
    editorial=(
        "## The one thing this teaches\n**A deterministic process with finite state must cycle — "
        "detect it with a map from state to time.** In long division the only state is the "
        "remainder, which is below the denominator. Seeing a remainder twice means the digits "
        "between are the period.\n\n"
        "## Approach\n```java\nif (num == 0) return \"0\";\nStringBuilder sb = new StringBuilder();\n"
        "if ((num < 0) ^ (den < 0)) sb.append('-');\nlong n = Math.abs((long) num), d = Math.abs((long) den);\n"
        "sb.append(n / d);\nlong rem = n % d;\nif (rem == 0) return sb.toString();\nsb.append('.');\n"
        "Map<Long, Integer> at = new HashMap<>();\nwhile (rem != 0) {\n"
        "    if (at.containsKey(rem)) { sb.insert(at.get(rem), '('); sb.append(')'); break; }\n"
        "    at.put(rem, sb.length());\n    rem *= 10;\n    sb.append(rem / d);\n    rem %= d;\n}\n```\n\n"
        "## Three traps\n- **Sign**: `-50 / 8` and `50 / -8` are both negative, `0 / -5` is just `0`.\n"
        "- **Overflow**: `Math.abs(-2147483648)` is still negative as an int. Convert to long first.\n"
        "- **Where the cycle starts**: `1/6 = 0.1(6)`, not `0.(16)`. The map records *where* each "
        "remainder was first seen, so the parenthesis goes exactly there."
    ),
    py='''
def solve(x, y):
    if x == 0:
        return "0"
    sign = "-" if (x < 0) != (y < 0) else ""
    x, y = abs(x), abs(y)
    whole, rem = divmod(x, y)
    if rem == 0:
        return sign + str(whole)
    digits, remainders = [], []
    while rem != 0 and rem not in remainders:
        remainders.append(rem)
        q, rem = divmod(rem * 10, y)
        digits.append(str(q))
    if rem == 0:
        return f"{sign}{whole}." + "".join(digits)
    start = remainders.index(rem)
    return f"{sign}{whole}." + "".join(digits[:start]) + "(" + "".join(digits[start:]) + ")"
''',
    java='''
    static String solve(long num, long den) {
        if (num == 0) return "0";
        StringBuilder sb = new StringBuilder();
        if ((num < 0) ^ (den < 0)) sb.append('-');
        long n = Math.abs(num), d = Math.abs(den);
        sb.append(n / d);
        long rem = n % d;
        if (rem == 0) return sb.toString();
        sb.append('.');
        HashMap<Long, Integer> at = new HashMap<>();
        while (rem != 0) {
            if (at.containsKey(rem)) { sb.insert((int) at.get(rem), '('); sb.append(')'); break; }
            at.put(rem, sb.length());
            rem *= 10;
            sb.append(rem / d);
            rem %= d;
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "1 2\n"), ("Example 2", "2 1\n"), ("Example 3", "4 333\n")],
    hidden=[
        ("Negative terminating", "-50 8\n"),
        ("Delayed cycle", "1 6\n"),
        ("Overflow on abs", "-2147483648 -1\n"),
        ("Zero over negative", "0 -5\n"),
        ("Negative with delayed cycle", "7 -12\n"),
        ("Long period", "1 7\n"),
    ],
    expl=[
        "1 / 2 = 0.5, which terminates.",
        "An integer: no decimal point.",
        "4 / 333 = 0.012012012…, so the block 012 repeats from the first decimal place.",
    ],
    prereqs=[
        ("hashing", "A map from remainder to the output position where it first appeared."),
        ("overflow", "Taking the absolute value of −2^31 in 64-bit arithmetic."),
    ],
)
