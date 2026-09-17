# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 16 — extra practice: matrices, maths, sorting, stacks, search, greedy, trees.
#
#   spiral-matrix-ii             fill layer by layer with four shrinking boundaries
#   diagonal-traverse            cells on a diagonal share i + j; alternate direction
#   multiply-strings             grade-school multiplication into a digit array
#   maximum-gap                  pigeonhole buckets beat sorting
#   sort-by-bits                 a two-key comparator: popcount, then value
#   next-greater-circular        walk the array twice with a monotonic stack
#   pattern-132                  scan from the right, keeping the best "2" below the stack
#   search-2d-matrix-ii          the staircase from the top-right corner
#   max-units-on-truck           take boxes with the most units first
#   minimum-height-trees         peel leaves layer by layer until one or two nodes remain
# ===========================================================================

_p(
    "spiral-matrix-ii", "Spiral Matrix II", "Medium",
    topics=["Matrix", "Simulation"], subtopics=["Simulation", "Grid"], companies=["Microsoft", "Amazon"],
    shape="n", ret="String", todo="write 1..n² along the top row, right column, bottom row, left column; shrink the bounds",
    description=(
        "Fill an `n × n` matrix with `1` to `n²` in clockwise spiral order, starting at the top-left.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe matrix: `n` lines of `n` space-separated values."
    ),
    constraints="1 ≤ n ≤ 20",
    hints=[
        "Keep four boundaries: top, bottom, left, right.",
        "Fill the top row left to right, then top++; the right column top to bottom, then right--; and so on.",
        "Stop when the boundaries cross. For odd n the centre is filled by the last top-row pass.",
    ],
    opt=("O(n²)", "O(n²)", "Each cell is written once."),
    editorial=(
        "## The one thing this teaches\n**Boundaries, not direction vectors.** Simulating a turning "
        "walker needs a \"visited\" check to know when to turn. Four shrinking boundaries make the "
        "turns implicit: each side of the current ring is one loop, and finishing it moves that "
        "boundary inward.\n\n"
        "## Approach\n```java\nint top = 0, bottom = n - 1, left = 0, right = n - 1, v = 1;\n"
        "while (top <= bottom && left <= right) {\n"
        "    for (int j = left; j <= right; j++) m[top][j] = v++;\n    top++;\n"
        "    for (int i = top; i <= bottom; i++) m[i][right] = v++;\n    right--;\n"
        "    for (int j = right; j >= left && top <= bottom; j--) m[bottom][j] = v++;\n    bottom--;\n"
        "    for (int i = bottom; i >= top && left <= right; i--) m[i][left] = v++;\n    left++;\n}\n```\n\n"
        "## The guards on the last two loops\nAfter the top row and right column, the ring may have "
        "collapsed to a single row or column. The `top <= bottom` and `left <= right` checks stop "
        "the bottom and left passes from writing it a second time — which matters for Spiral "
        "Order on rectangles more than for squares."
    ),
    py='''
def solve(n):
    m = [[0] * n for _ in range(n)]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    i = j = d = 0
    for v in range(1, n * n + 1):
        m[i][j] = v
        ni, nj = i + dirs[d][0], j + dirs[d][1]
        if not (0 <= ni < n and 0 <= nj < n and m[ni][nj] == 0):
            d = (d + 1) % 4
            ni, nj = i + dirs[d][0], j + dirs[d][1]
        i, j = ni, nj
    return "\\n".join(" ".join(map(str, row)) for row in m)
''',
    java='''
    static String solve(long nn) {
        int n = (int) nn;
        int[][] m = new int[n][n];
        int top = 0, bottom = n - 1, left = 0, right = n - 1, v = 1;
        while (top <= bottom && left <= right) {
            for (int j = left; j <= right; j++) m[top][j] = v++;
            top++;
            for (int i = top; i <= bottom; i++) m[i][right] = v++;
            right--;
            for (int j = right; j >= left && top <= bottom; j--) m[bottom][j] = v++;
            bottom--;
            for (int i = bottom; i >= top && left <= right; i--) m[i][left] = v++;
            left++;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append('\\n');
            for (int j = 0; j < n; j++) { if (j > 0) sb.append(' '); sb.append(m[i][j]); }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n"), ("Example 2", "1\n")],
    hidden=[("Two", "2\n"), ("Four", "4\n"), ("Five", "5\n")],
    expl=[
        "The outer ring holds 1 to 8 and the centre holds 9.",
        "A single cell.",
    ],
    prereqs=[
        ("simulation", "Walking the ring with four boundaries that shrink after each side."),
        ("grid", "Writing into a 2-D array row and column by index."),
    ],
)

_p(
    "diagonal-traverse", "Diagonal Traverse", "Medium",
    topics=["Matrix", "Simulation"], subtopics=["Simulation", "Grid"], companies=["Google", "Meta"],
    shape="matrix", ret="String", todo="visit diagonals by d = i + j; odd d goes down-left, even d goes up-right",
    description=(
        "Read a matrix along its anti-diagonals in a zigzag: the first diagonal up-right, the next "
        "down-left, and so on, starting at the top-left cell.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers.\n\n### Output\nAll values in zigzag diagonal order."
    ),
    constraints="1 ≤ r, c ≤ 10^4 and r·c ≤ 10^4",
    hints=[
        "Every cell on one anti-diagonal has the same i + j.",
        "Diagonal d runs from (min(d, r−1), d − min(d, r−1)) up-right to (d − min(d, c−1), min(d, c−1)).",
        "Read even diagonals bottom-left to top-right and odd diagonals the other way.",
    ],
    opt=("O(r·c)", "O(1)", "Each cell is read once; no grouping structure is needed."),
    editorial=(
        "## The one thing this teaches\n**Index arithmetic names the diagonal.** `i + j` is "
        "constant along an anti-diagonal, so diagonals can be enumerated by `d` from 0 to "
        "`r + c − 2`, each with a computable start and end. The zigzag is just which end you start "
        "from.\n\n"
        "## Approach\n```java\nfor (int d = 0; d <= r + c - 2; d++) {\n"
        "    int iLo = Math.max(0, d - (c - 1)), iHi = Math.min(d, r - 1);\n"
        "    if (d % 2 == 0) for (int i = iHi; i >= iLo; i--) out.add(m[i][d - i]);   // up-right\n"
        "    else            for (int i = iLo; i <= iHi; i++) out.add(m[i][d - i]);   // down-left\n}\n```\n\n"
        "## The grouping alternative\nBucket every cell by `i + j`, then reverse every even bucket. "
        "Simpler to see, O(r·c) extra space — and a fine first version."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    groups = defaultdict(list)
    for i in range(r):
        for j in range(c):
            groups[i + j].append(m[i][j])
    out = []
    for d in range(r + c - 1):
        out.extend(reversed(groups[d]) if d % 2 == 0 else groups[d])
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[][] m) {
        int r = m.length, c = m[0].length;
        StringBuilder sb = new StringBuilder();
        for (int d = 0; d <= r + c - 2; d++) {
            int iLo = Math.max(0, d - (c - 1)), iHi = Math.min(d, r - 1);
            if (d % 2 == 0) for (int i = iHi; i >= iLo; i--) { if (sb.length() > 0) sb.append(' '); sb.append(m[i][d - i]); }
            else for (int i = iLo; i <= iHi; i++) { if (sb.length() > 0) sb.append(' '); sb.append(m[i][d - i]); }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3 3\n1 2 3\n4 5 6\n7 8 9\n"), ("Example 2", "2 2\n1 2\n3 4\n")],
    hidden=[
        ("Single row", "1 3\n1 2 3\n"),
        ("Single column", "3 1\n1\n2\n3\n"),
        ("Wide", "2 3\n1 2 3\n4 5 6\n"),
        ("Tall", "3 2\n1 2\n3 4\n5 6\n"),
    ],
    expl=[
        "Diagonals `1`, `2 4`, `7 5 3`, `6 8`, `9`, alternating direction.",
        "`1`, then `2 3`, then `4`.",
    ],
    prereqs=[
        ("grid", "Cells on one anti-diagonal share i + j."),
        ("simulation", "Alternating the reading direction per diagonal."),
    ],
)

_p(
    "multiply-strings", "Multiply Strings", "Medium",
    topics=["Math", "Strings"], subtopics=["Digits", "Simulation"], companies=["Meta", "Microsoft"],
    shape="str2", ret="String", todo="digit i of a times digit j of b adds into position i + j + 1; then carry and strip zeros",
    description=(
        "Multiply two non-negative integers given as decimal strings, without converting them to "
        "big-integer types.\n\n"
        "### Input\n- Line 1: `a`.\n- Line 2: `b`.\n\n### Output\nThe product, without leading zeros."
    ),
    constraints="1 ≤ |a|, |b| ≤ 200\nBoth are decimal strings without leading zeros (except \"0\").",
    hints=[
        "The product of an m-digit and an n-digit number has at most m + n digits.",
        "The digit at index i of a times the digit at index j of b contributes to result index i + j + 1 (0 is the most significant).",
        "Accumulate all products first, then sweep from the right carrying. Strip leading zeros; an all-zero result is \"0\".",
    ],
    opt=("O(m·n)", "O(m + n)", "Every digit pair is multiplied once into a result array."),
    editorial=(
        "## The one thing this teaches\n**Grade-school multiplication, positioned by index.** On "
        "paper you shift each partial product left by one place per digit of the multiplier. In an "
        "array, that shift is arithmetic on indices: digit `i` of `a` and digit `j` of `b` land at "
        "`i + j + 1`, with the carry going to `i + j`.\n\n"
        "## Approach\n```java\nint[] res = new int[m + n];\nfor (int i = m - 1; i >= 0; i--)\n"
        "    for (int j = n - 1; j >= 0; j--) {\n"
        "        int sum = (a.charAt(i) - '0') * (b.charAt(j) - '0') + res[i + j + 1];\n"
        "        res[i + j + 1] = sum % 10;\n        res[i + j] += sum / 10;\n    }\n"
        "// skip leading zeros, build the string; if nothing is left, return \"0\"\n```\n\n"
        "## Why iterate from the right\nProcessing less significant pairs first means the carry "
        "written into `res[i + j]` is folded in when that position is next touched, so no separate "
        "carry pass is needed.\n\n"
        "## Zero\n`0 × 52` produces `res = [0, 0, 0]`. Stripping leading zeros leaves nothing, and "
        "the answer is `\"0\"`, not the empty string."
    ),
    py='''
def solve(s, t):
    return str(int(s) * int(t))
''',
    java='''
    static String solve(String a, String b) {
        int m = a.length(), n = b.length();
        int[] res = new int[m + n];
        for (int i = m - 1; i >= 0; i--)
            for (int j = n - 1; j >= 0; j--) {
                int sum = (a.charAt(i) - '0') * (b.charAt(j) - '0') + res[i + j + 1];
                res[i + j + 1] = sum % 10;
                res[i + j] += sum / 10;
            }
        StringBuilder sb = new StringBuilder();
        for (int d : res) if (!(sb.length() == 0 && d == 0)) sb.append(d);
        return sb.length() == 0 ? "0" : sb.toString();
    }
''',
    examples=[("Example 1", "2\n3\n"), ("Example 2", "123\n456\n")],
    hidden=[
        ("Zero", "0\n52\n"),
        ("Carries everywhere", "999\n999\n"),
        ("Beyond a long", "123456789123456789123456789\n987654321987654321\n"),
    ],
    expl=[
        "2 × 3 = 6.",
        "123 × 456 = 56088.",
    ],
    prereqs=[
        ("math_digits", "Digit-by-digit multiplication with carries."),
        ("overflow", "The operands are longer than any primitive type, so no conversion is possible."),
    ],
)

_p(
    "maximum-gap", "Maximum Gap", "Hard",
    topics=["Searching & Sorting", "Arrays"], subtopics=["Sorting"], companies=["Amazon", "Google"],
    shape="arr", ret="long", todo="n−1 buckets of width ceil((max−min)/(n−1)); the gap is between buckets, from a max to the next min",
    description=(
        "Find the largest difference between two **successive** elements of the array in sorted "
        "order, in linear time. With fewer than two elements, print 0.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` non-negative integers.\n\n### Output\nThe maximum gap."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "Sorting and scanning neighbours is O(n log n). Aim for O(n).",
        "With n values spread over [min, max], the average gap is (max − min)/(n − 1), so the maximum gap is at least that.",
        "Use buckets of that width: two values in the same bucket are closer than the answer, so only compare each bucket's min with the previous non-empty bucket's max.",
    ],
    opt=("O(n)", "O(n)", "One pass to bucket each value by (value − min) / width, one pass over the buckets."),
    editorial=(
        "## The one thing this teaches\n**The pigeonhole principle as an algorithm.** The largest "
        "gap is at least the average gap, `(max − min) / (n − 1)`. Choose buckets narrower than "
        "that, and no gap *inside* a bucket can be the answer — so each bucket only needs its min "
        "and max, and the answer is found between neighbouring non-empty buckets.\n\n"
        "## Approach\n```java\nint width = Math.max(1, (int) Math.ceil((double) (max - min) / (n - 1)));\n"
        "int k = (max - min) / width + 1;\n// bucketMin[k], bucketMax[k], seen[k]\n"
        "for (int x : a) { int b = (x - min) / width; update min/max of bucket b; }\n"
        "long prevMax = min, best = 0;\nfor (int b = 0; b < k; b++) if (seen[b]) {\n"
        "    best = Math.max(best, bucketMin[b] - prevMax);\n    prevMax = bucketMax[b];\n}\n```\n\n"
        "## Why the width guard\nIf every value is equal, `max − min` is 0 and the width would be 0 "
        "— a division by zero. A width of at least 1 puts everything in one bucket and returns 0.\n\n"
        "Radix sort also gives O(n) for bounded integers; buckets are the argument worth being able "
        "to make out loud."
    ),
    py='''
def solve(a):
    if len(a) < 2:
        return 0
    s = sorted(a)
    return max(s[i + 1] - s[i] for i in range(len(s) - 1))
''',
    java='''
    static long solve(int[] a) {
        int n = a.length;
        if (n < 2) return 0;
        int min = Integer.MAX_VALUE, max = Integer.MIN_VALUE;
        for (int x : a) { min = Math.min(min, x); max = Math.max(max, x); }
        if (min == max) return 0;
        int width = Math.max(1, (int) Math.ceil((double) (max - min) / (n - 1)));
        int k = (max - min) / width + 1;
        int[] bMin = new int[k], bMax = new int[k];
        boolean[] seen = new boolean[k];
        Arrays.fill(bMin, Integer.MAX_VALUE);
        Arrays.fill(bMax, Integer.MIN_VALUE);
        for (int x : a) {
            int b = (x - min) / width;
            seen[b] = true;
            bMin[b] = Math.min(bMin[b], x);
            bMax[b] = Math.max(bMax[b], x);
        }
        long prevMax = min, best = 0;
        for (int b = 0; b < k; b++) {
            if (!seen[b]) continue;
            best = Math.max(best, (long) bMin[b] - prevMax);
            prevMax = bMax[b];
        }
        return best;
    }
''',
    examples=[("Example 1", "4\n3 6 9 1\n"), ("Example 2", "1\n10\n")],
    hidden=[
        ("Two far apart", "2\n1 1000000000\n"),
        ("All equal", "5\n1 1 1 1 1\n"),
        ("Clusters", "6\n100 3 2 1 50 49\n"),
        ("Gap inside the range", "5\n1 2 3 100 101\n"),
    ],
    expl=[
        "Sorted `1 3 6 9`: every gap is 3.",
        "One element has no successor.",
    ],
    prereqs=[
        ("sorting", "Bucketing values by range instead of comparing them."),
        ("math_digits", "The pigeonhole bound: the largest gap is at least the average gap."),
    ],
)

_p(
    "sort-by-bits", "Sort Integers by Number of 1 Bits", "Easy",
    topics=["Sorting", "Bit Manipulation"], subtopics=["Sorting", "Bit Manipulation"], companies=["Amazon"],
    shape="arr", ret="String", todo="sort by (popcount, value)",
    description=(
        "Sort the integers by the number of `1` bits in their binary representation; break ties by "
        "the value itself, ascending.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` non-negative integers.\n\n### Output\nThe sorted values."
    ),
    constraints="1 ≤ n ≤ 500\n0 ≤ a[i] ≤ 10^4",
    hints=[
        "This is a sort with a two-part key.",
        "In Java, `Integer.bitCount(x)` counts the 1 bits.",
        "Sort boxed Integers with a comparator — or sort by `bitCount(x) * 100001 + x` as a single int key.",
    ],
    opt=("O(n log n)", "O(n)", "One comparison sort; each key costs O(1)."),
    editorial=(
        "## The one thing this teaches\n**Two keys, one comparator — or one combined key.** "
        "`Comparator.comparingInt(Integer::bitCount).thenComparingInt(x -> x)` states the rule "
        "directly. Because both parts are small non-negative integers, they can also be packed into "
        "one number whose natural order is the required order.\n\n"
        "## Approach\n```java\nInteger[] b = boxed(a);\n"
        "Arrays.sort(b, Comparator.comparingInt((Integer x) -> Integer.bitCount(x)).thenComparingInt(x -> x));\n```\n\n"
        "## The packed key\nWith values below 10⁴ + 1, `bitCount(x) * 10001 + x` preserves both "
        "orders: a larger bit count always wins, and within a bit count the value decides. That "
        "sorts a primitive `int[]` with no boxing, then recovers `x` as `key % 10001`."
    ),
    py='''
def solve(a):
    return " ".join(map(str, sorted(a, key=lambda x: (bin(x).count("1"), x))))
''',
    java='''
    static String solve(int[] a) {
        int[] key = new int[a.length];
        for (int i = 0; i < a.length; i++) key[i] = Integer.bitCount(a[i]) * 10001 + a[i];
        Arrays.sort(key);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < key.length; i++) { if (i > 0) sb.append(' '); sb.append(key[i] % 10001); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "9\n0 1 2 3 4 5 6 7 8\n"), ("Example 2", "11\n1024 512 256 128 64 32 16 8 4 2 1\n")],
    hidden=[
        ("Single value", "1\n7\n"),
        ("Duplicates", "4\n3 3 5 6\n"),
        ("Mixed", "5\n10 100 1000 10000 7\n"),
    ],
    expl=[
        "0 has no bits; 1 2 4 8 have one; 3 5 6 have two; 7 has three.",
        "All powers of two have one bit, so the order is by value.",
    ],
    prereqs=[
        ("sorting", "A comparator with a tie-break, or a packed single key."),
        ("bit_manip", "Counting set bits with Integer.bitCount."),
    ],
)

_p(
    "next-greater-circular", "Next Greater Element II (Circular)", "Medium",
    topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google"],
    shape="arr", ret="String", todo="walk indices 0..2n−1 (mod n) with a monotonic stack of unresolved indices",
    description=(
        "In a **circular** array, the next greater element of `a[i]` is the first larger value found "
        "by moving right from `i` and wrapping around. Print it for each element, or `-1`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe `n` answers."
    ),
    constraints="1 ≤ n ≤ 10^4\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Without the wrap, this is the monotonic-stack template.",
        "The wrap only matters for elements still unresolved at the end — walk the array a second time to resolve them.",
        "Loop i from 0 to 2n − 1 using a[i % n]; push indices only during the first pass.",
    ],
    opt=("O(n)", "O(n)", "Each index is pushed once and popped at most once across both passes."),
    editorial=(
        "## The one thing this teaches\n**A circle is the array twice.** Anything to the right of "
        "`i` in the circle appears to the right of `i` in `a + a`. Running the monotonic stack over "
        "the doubled sequence — without actually copying it — resolves wrap-around answers.\n\n"
        "## Approach\n```java\nint[] ans = new int[n];\nArrays.fill(ans, -1);\nDeque<Integer> st = new ArrayDeque<>();\n"
        "for (int i = 0; i < 2 * n; i++) {\n    int x = a[i % n];\n"
        "    while (!st.isEmpty() && a[st.peek()] < x) ans[st.pop()] = x;\n"
        "    if (i < n) st.push(i);\n}\n```\n\n"
        "## Why push only in the first pass\nThe second pass exists to *answer* old indices, not to "
        "create new questions. Pushing again would try to resolve each index twice. The maximum "
        "element — and any copy of it — is never popped and keeps its −1."
    ),
    py='''
def solve(a):
    n = len(a)
    out = []
    for i in range(n):
        ans = -1
        for step in range(1, n):
            if a[(i + step) % n] > a[i]:
                ans = a[(i + step) % n]
                break
        out.append(ans)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] a) {
        int n = a.length;
        long[] ans = new long[n];
        Arrays.fill(ans, -1);
        int[] st = new int[n];
        int top = 0;
        for (int i = 0; i < 2 * n; i++) {
            int x = a[i % n];
            while (top > 0 && a[st[top - 1]] < x) ans[st[--top]] = x;
            if (i < n) st[top++] = i;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(' '); sb.append(ans[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n1 2 1\n"), ("Example 2", "5\n1 2 3 4 3\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All equal", "4\n5 5 5 5\n"),
        ("Decreasing wraps to the front", "5\n5 4 3 2 1\n"),
        ("Negative values", "4\n-3 -1 -2 -5\n"),
    ],
    expl=[
        "The last 1 wraps around to find 2.",
        "The final 3 wraps to 4; the 4 has nothing larger.",
    ],
    prereqs=[
        ("stack", "The monotonic stack of unresolved indices."),
        ("modulo", "Index mod n walks the circle twice without copying the array."),
    ],
)

_p(
    "pattern-132", "132 Pattern", "Medium",
    topics=["Stack", "Arrays"], subtopics=["Monotonic Stack"], companies=["Amazon", "Google"],
    shape="arr", ret="String", todo="scan right to left; stack holds candidate 3s; popped values become the best 2; any value below it is the 1",
    description=(
        "Is there a **132 pattern**: indices `i < j < k` with `a[i] < a[k] < a[j]`?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 2·10^5\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "For a fixed middle j, the best i is the smallest value to its left. That handles the '1'.",
        "Scan from the right. Keep a stack of possible '3's, decreasing. When a larger value arrives, pop the smaller ones — each popped value is a valid '2' for the new '3'.",
        "Keep the largest such '2' seen. If the current value is below it, it is the '1': YES.",
    ],
    opt=("O(n)", "O(n)", "Each value is pushed and popped at most once in the right-to-left scan."),
    editorial=(
        "## The one thing this teaches\n**Scan in the direction that fixes the hard part.** The "
        "pattern has three roles. Scanning right to left, the stack pairs each '3' with the best "
        "'2' to its right — the largest value smaller than it — so only the '1' remains to be "
        "found, and it is simply any value below that '2'.\n\n"
        "## Approach\n```java\nlong two = Long.MIN_VALUE;         // best '2' so far\nDeque<Integer> st = new ArrayDeque<>();\n"
        "for (int i = n - 1; i >= 0; i--) {\n    if (a[i] < two) return \"YES\";   // a[i] is the '1'\n"
        "    while (!st.isEmpty() && st.peek() < a[i]) two = st.pop();   // a[i] is a '3' for these\n"
        "    st.push(a[i]);\n}\nreturn \"NO\";\n```\n\n"
        "## Why the last popped value is the best '2'\nThe stack is decreasing from bottom to top, "
        "so the values popped for a given `a[i]` increase; the last one is the largest value below "
        "`a[i]` among those to its right. A larger '2' gives the '1' the most room.\n\n"
        "The O(n²) version — prefix minimum as the '1' and a scan for the '2' — is the honest first "
        "answer."
    ),
    py='''
def solve(a):
    n = len(a)
    low = a[0]
    for j in range(1, n):
        if a[j] > low:
            for k in range(j + 1, n):
                if low < a[k] < a[j]:
                    return "YES"
        low = min(low, a[j])
    return "NO"
''',
    java='''
    static String solve(int[] a) {
        long two = Long.MIN_VALUE;
        ArrayDeque<Integer> st = new ArrayDeque<>();
        for (int i = a.length - 1; i >= 0; i--) {
            if (a[i] < two) return "YES";
            while (!st.isEmpty() && st.peek() < a[i]) two = st.pop();
            st.push(a[i]);
        }
        return "NO";
    }
''',
    examples=[("Example 1", "4\n1 2 3 4\n"), ("Example 2", "4\n3 1 4 2\n")],
    hidden=[
        ("Negatives", "4\n-1 3 2 0\n"),
        ("Equal ends", "3\n1 0 1\n"),
        ("Pattern late", "5\n3 5 0 3 4\n"),
        ("Too short", "2\n1 2\n"),
    ],
    expl=[
        "Strictly increasing, so a later value is never below an earlier larger one.",
        "`1 4 2` is the pattern.",
    ],
    prereqs=[
        ("stack", "A decreasing stack scanned right to left, where popped values become candidate '2's."),
        ("prefix_max", "The brute-force version uses a running minimum as the '1'."),
    ],
)

_p(
    "search-2d-matrix-ii", "Search a 2D Matrix II", "Medium",
    topics=["Binary Search", "Matrix"], subtopics=["Binary Search", "Two Pointers"], companies=["Amazon", "Microsoft"],
    shape="matrix_k", ret="String", todo="start at the top-right; move left if the cell is too big, down if too small",
    description=(
        "Each row of the matrix is sorted left to right and each column top to bottom. Is `target` "
        "in the matrix?\n\n"
        "### Input\n- Line 1: `r c target`.\n- Next `r` lines: `c` integers.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ r, c ≤ 300\n-10^9 ≤ value, target ≤ 10^9",
    hints=[
        "Binary search on each row is O(r log c). There is an O(r + c) walk.",
        "Start at the top-right corner: everything left is smaller, everything below is larger.",
        "If the cell is bigger than the target, its column is too big from here down — move left. If smaller, its row is too small — move down.",
    ],
    opt=("O(r + c)", "O(1)", "Each step discards a whole row or a whole column."),
    editorial=(
        "## The one thing this teaches\n**Start where one comparison eliminates something.** At the "
        "top-left, both neighbours are larger and a comparison tells you nothing about direction. "
        "At the top-right, left is smaller and down is larger, so every comparison rules out an "
        "entire row or column.\n\n"
        "## Approach\n```java\nint i = 0, j = c - 1;\nwhile (i < r && j >= 0) {\n"
        "    if (m[i][j] == target) return \"YES\";\n"
        "    if (m[i][j] > target) j--;        // the rest of column j is even bigger\n"
        "    else i++;                         // the rest of row i is even smaller\n}\nreturn \"NO\";\n```\n\n"
        "## Why it is not a binary search\nThe matrix is not globally sorted — a row's last element "
        "can exceed the next row's first — so treating it as one sorted array (Search a 2D Matrix I) "
        "fails. The staircase uses exactly the order that is guaranteed."
    ),
    py='''
def solve(m, k):
    return "YES" if any(k in row for row in m) else "NO"
''',
    java='''
    static String solve(int[][] m, int target) {
        int i = 0, j = m[0].length - 1;
        while (i < m.length && j >= 0) {
            if (m[i][j] == target) return "YES";
            if (m[i][j] > target) j--;
            else i++;
        }
        return "NO";
    }
''',
    examples=[
        ("Example 1", "5 5 5\n1 4 7 11 15\n2 5 8 12 19\n3 6 9 16 22\n10 13 14 17 24\n18 21 23 26 30\n"),
        ("Example 2", "5 5 20\n1 4 7 11 15\n2 5 8 12 19\n3 6 9 16 22\n10 13 14 17 24\n18 21 23 26 30\n"),
    ],
    hidden=[
        ("Single cell", "1 1 1\n1\n"),
        ("Missing between values", "2 2 3\n1 2\n4 5\n"),
        ("Negatives, bottom-left", "3 3 1\n-5 -1 3\n-2 0 4\n1 2 6\n"),
        ("Not globally sorted", "2 3 4\n1 5 9\n2 6 10\n"),
    ],
    expl=[
        "5 is at row 1, column 1.",
        "20 falls between 19 and 21 and is not present.",
    ],
    prereqs=[
        ("binary_search", "Discarding part of the search space with each comparison."),
        ("two_pointers", "A row pointer and a column pointer that only move down and left."),
    ],
)

_p(
    "max-units-on-truck", "Maximum Units on a Truck", "Easy",
    topics=["Greedy", "Sorting"], subtopics=["Greedy", "Sorting"], companies=["Amazon"],
    shape="pairs_k", ret="long", todo="sort box types by units per box, descending; load as many as fit",
    description=(
        "Box type `i` has `count` boxes, each holding `units` units. A truck can carry at most `k` "
        "**boxes**. Maximise the total units loaded.\n\n"
        "### Input\n- Line 1: `n k`.\n- Next `n` lines: `count units`.\n\n### Output\nThe maximum total units."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ count, units ≤ 1000\n1 ≤ k ≤ 10^6",
    hints=[
        "Every box takes the same space, so a box is worth exactly its units.",
        "Load the most valuable boxes first.",
        "Sort by units descending and take min(count, space left) of each type.",
    ],
    opt=("O(n log n)", "O(1)", "One sort; counting sort over units ≤ 1000 makes it O(n + 1000)."),
    editorial=(
        "## The one thing this teaches\n**When every item costs the same, take the best items.** "
        "This is fractional knapsack with unit weights: the capacity is counted in boxes, and all "
        "boxes weigh one, so value per weight is just units per box.\n\n"
        "## Approach\n```java\nArrays.sort(types, (x, y) -> y[1] - x[1]);\nlong total = 0;\n"
        "for (int[] t : types) {\n    int take = Math.min(t[0], k);\n    total += (long) take * t[1];\n"
        "    k -= take;\n    if (k == 0) break;\n}\n```\n\n"
        "## Why greedy is safe here\nSwapping any loaded box for an unloaded box with more units "
        "never hurts, and boxes of one type are interchangeable — so there is no combination effect "
        "for a smarter choice to exploit. Unequal box sizes would make it 0/1 knapsack."
    ),
    py='''
def solve(p, k):
    total = 0
    for count, units in sorted(p, key=lambda t: -t[1]):
        take = min(count, k)
        total += take * units
        k -= take
        if k == 0:
            break
    return total
''',
    java='''
    static long solve(int[][] types, int k) {
        long[] byUnits = new long[1001];
        for (int[] t : types) byUnits[t[1]] += t[0];
        long total = 0, space = k;
        for (int u = 1000; u >= 1 && space > 0; u--) {
            long take = Math.min(byUnits[u], space);
            total += take * u;
            space -= take;
        }
        return total;
    }
''',
    examples=[("Example 1", "3 4\n1 3\n2 2\n3 1\n"), ("Example 2", "4 10\n5 10\n2 5\n4 7\n3 9\n")],
    hidden=[
        ("One type", "1 1\n5 5\n"),
        ("Truck bigger than supply", "2 100\n1 1\n1 2\n"),
        ("Best type last", "2 3\n2 1\n2 5\n"),
    ],
    expl=[
        "One 3-unit box and two 2-unit boxes, plus one 1-unit box: 3 + 4 + 1 = 8.",
        "Five 10-unit boxes, three 9-unit boxes and two 7-unit boxes: 50 + 27 + 14 = 91.",
    ],
    prereqs=[
        ("greedy", "With equal box sizes, the most valuable boxes first is optimal."),
        ("sorting", "Ordering box types by units per box — or counting sort, since units ≤ 1000."),
    ],
)

_p(
    "minimum-height-trees", "Minimum Height Trees", "Medium",
    topics=["Graphs", "Trees"], subtopics=["Topological Sort", "BFS"], companies=["Google", "Snapchat"],
    shape="graph", ret="String", todo="repeatedly remove all current leaves (degree 1) until at most two nodes remain",
    description=(
        "A tree with `n` nodes is given by its `n − 1` undirected edges. Choosing a node as the root "
        "gives the tree a height. Find **all** roots that minimise the height.\n\n"
        "### Input\n- Line 1: `n m` (m = n − 1).\n- Next `m` lines: `u v`.\n\n"
        "### Output\nThe roots of minimum height trees, in increasing order."
    ),
    constraints="1 ≤ n ≤ 2·10^4\nThe edges form a tree.",
    hints=[
        "Trying every root with a BFS is O(n²).",
        "The best roots are the middle of the longest path — far from every leaf.",
        "Peel leaves: remove all degree-1 nodes at once, update degrees, repeat until one or two nodes remain.",
    ],
    opt=("O(n)", "O(n)", "Each node is removed once; each edge decrements one degree once."),
    editorial=(
        "## The one thing this teaches\n**Kahn's algorithm on an undirected tree finds its centre.** "
        "Removing every leaf shortens every longest path by two — one from each end — without "
        "changing its middle. Repeating until one or two nodes remain leaves exactly the middle "
        "of the longest path, which is where the height is smallest.\n\n"
        "## Approach\n```java\nif (n == 1) return [0];\nint[] deg = new int[n];  // plus adjacency lists\n"
        "Deque<Integer> leaves = all nodes with deg == 1;\nint remaining = n;\n"
        "while (remaining > 2) {\n    remaining -= leaves.size();\n"
        "    for (int k = leaves.size(); k > 0; k--) {\n        int leaf = leaves.poll();\n"
        "        for (int nb : adj.get(leaf)) if (--deg[nb] == 1) leaves.add(nb);\n    }\n}\n"
        "return the nodes left in leaves, sorted;\n```\n\n"
        "## Why at most two\nA path with an odd number of nodes has one middle node; an even one has "
        "two. Every tree's centre is one node or two adjacent nodes."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    def height(root):
        dist = [-1] * n
        dist[root] = 0
        q = deque([root])
        best = 0
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    best = max(best, dist[v])
                    q.append(v)
        return best

    heights = [height(i) for i in range(n)]
    low = min(heights)
    return " ".join(str(i) for i in range(n) if heights[i] == low)
''',
    java='''
    static String solve(int n, int[][] edges) {
        if (n == 1) return "0";
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] deg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); deg[e[0]]++; deg[e[1]]++; }
        ArrayDeque<Integer> leaves = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (deg[i] == 1) leaves.add(i);
        int remaining = n;
        while (remaining > 2) {
            remaining -= leaves.size();
            for (int k = leaves.size(); k > 0; k--) {
                int leaf = leaves.poll();
                for (int nb : adj.get(leaf)) if (--deg[nb] == 1) leaves.add(nb);
            }
        }
        List<Integer> res = new ArrayList<>(leaves);
        Collections.sort(res);
        StringBuilder sb = new StringBuilder();
        for (int x : res) { if (sb.length() > 0) sb.append(' '); sb.append(x); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4 3\n1 0\n1 2\n1 3\n"), ("Example 2", "6 5\n3 0\n3 1\n3 2\n3 4\n5 4\n")],
    hidden=[
        ("Single node", "1 0\n"),
        ("Two nodes", "2 1\n0 1\n"),
        ("A path of five", "5 4\n0 1\n1 2\n2 3\n3 4\n"),
        ("A path of six", "6 5\n0 1\n1 2\n2 3\n3 4\n4 5\n"),
    ],
    expl=[
        "Node 1 is adjacent to everything: height 1.",
        "Rooting at 3 or at 4 gives height 2.",
    ],
    prereqs=[
        ("topo", "Kahn-style peeling of degree-1 nodes, layer by layer."),
        ("tree_basics", "A tree's centre is the middle of its longest path: one node or two."),
    ],
)
