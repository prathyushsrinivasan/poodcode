# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 46 — Order & Search, part 1: recursion and sorting.
#
#   to-base-recursive        work AFTER the call: digits come out in order
#   josephus-survivor        a one-line recurrence too deep to recurse on
#   mulmod-by-halving        fast power's shape, with + instead of ×
#   closest-pair-points      divide and conquer whose combine is the whole idea
#   rank-transform           argsort, and ties that share a rank
#   radix-pass-by-pass       LSD radix sort, shown one stable pass at a time
#   moves-to-median          the median minimises Σ|x − m|; quickselect finds it
#   important-reverse-pairs  merge-count with a condition that is not the order
#
# Also defines three input shapes the stage-3 batches share: `three` (three
# integers), `triples` (n lines of three) and `pairs_xy` (n pairs plus a range).
# ===========================================================================

# three integers, on one line or several
_SHAPES["three"] = dict(
    py="d = sys.stdin.read().split()\nx, y, z = int(d[0]), int(d[1]), int(d[2])\n",
    py_params="x, y, z",
    js=_JS_NUMS + "const x = Number(d[0]), y = Number(d[1]), z = Number(d[2]);\n",
    js_params="x, y, z",
    java="        long x = sc.nextLong(), y = sc.nextLong(), z = sc.nextLong();\n",
    java_params="long x, long y, long z", java_args="x, y, z",
)
# n, then n lines "a b c"
_SHAPES["triples"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn = d[0]\n"
       "t = [(d[1 + 3 * i], d[2 + 3 * i], d[3 + 3 * i]) for i in range(n)]\n",
    py_params="t",
    js=_JS_NUMS + "const n = Number(d[0]);\n"
       "const t = Array.from({ length: n }, (_, i) => [0, 1, 2].map(j => Number(d[1 + 3 * i + j])));\n",
    js_params="t",
    java="        int n = sc.nextInt();\n        int[][] t = new int[n][3];\n"
         "        for (int i = 0; i < n; i++) for (int j = 0; j < 3; j++) t[i][j] = sc.nextInt();\n",
    java_params="int[][] t", java_args="t",
)
# "n x y", then n lines "a b"
_SHAPES["pairs_xy"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, x, y = d[0], d[1], d[2]\n"
       "p = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(n)]\n",
    py_params="p, x, y",
    js=_JS_NUMS + "const n = Number(d[0]), x = Number(d[1]), y = Number(d[2]);\n"
       "const p = Array.from({ length: n }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n",
    js_params="p, x, y",
    java="        int n = sc.nextInt(), x = sc.nextInt(), y = sc.nextInt();\n        int[][] p = new int[n][2];\n"
         "        for (int i = 0; i < n; i++) { p[i][0] = sc.nextInt(); p[i][1] = sc.nextInt(); }\n",
    java_params="int[][] p, int x, int y", java_args="p, x, y",
)


def _lcg_ints(seed, n, lo, hi):
    """Deterministic pseudo-random ints for generated hidden cases (same LCG as the
    randomized-algorithm problems), so the case text is stable across runs."""
    s, out = seed, []
    for _ in range(n):
        s = (s * 1103515245 + 12345) % (1 << 31)
        out.append(lo + s % (hi - lo + 1))
    return out


# ------------------------------------------------------------------ recursion

_p(
    "to-base-recursive", "Write It in Base b", "Easy",
    topics=["Recursion"], subtopics=["Recursion", "Number Bases"],
    companies=["Amazon", "Microsoft"],
    shape="two", ret="String",
    todo="write the digits of x / b first (the recursive call), then the digit x % b",
    description=(
        "Write the non-negative integer `x` in base `b`, using the digits `0-9` and then "
        "`A-F` for bases above 10.\n\n"
        "The natural loop — take `x % b`, divide, repeat — produces the digits **backwards**. "
        "Solve it recursively so that they come out in the right order without reversing "
        "anything.\n\n"
        "### Input\nOne line: `x b`.\n\n### Output\n`x` in base `b`, with no leading zeros "
        "(`0` is written `0`)."
    ),
    constraints="0 ≤ x ≤ 10^18\n2 ≤ b ≤ 16",
    hints=[
        "The last digit of x in base b is `x % b`. Everything before it is x / b, written in base b.",
        "So: write `x / b` first — a recursive call on a smaller number — and *then* append the last digit. The order of the two lines is the whole trick.",
        "Base case: a single digit (x < b) is written as itself. That also handles x = 0 without a special case.",
    ],
    opt=("O(log_b x)", "O(log_b x)",
         "One call per digit; the stack holds one frame per digit, at most 60 for base 2."),
    editorial=(
        "## The one thing this teaches\n**Where the work sits relative to the call decides the "
        "order.** Work before the recursive call happens on the way *down*; work after it happens "
        "on the way *back up*, in reverse. Printing digits after the call prints them "
        "most-significant first.\n\n"
        "## Approach\n```java\nstatic final String DIG = \"0123456789ABCDEF\";\n\n"
        "static void write(long x, int b, StringBuilder out) {\n"
        "    if (x >= b) write(x / b, b, out);   // everything but the last digit\n"
        "    out.append(DIG.charAt((int) (x % b)));  // then the last digit\n}\n```\n\n"
        "## The promise\n*`write(x, b)` appends x in base b.* Assume it for `x / b`, which is "
        "smaller; appending the final digit then completes x. That is the entire correctness "
        "argument, and it never traces a single call.\n\n"
        "## Why not the loop?\nThe loop is fine — push `x % b` into a `StringBuilder` and "
        "`reverse()` at the end. The recursion is the same algorithm with the call stack doing "
        "the reversal, and it is the smallest example of a pattern you will use constantly: "
        "in-order traversal, printing a path from the root, and Hanoi's move list all depend on "
        "doing the work *after* the call.\n\n"
        "## Depth\nAt most 60 digits (10¹⁸ < 2⁶⁰), so the recursion is at most 60 frames deep. "
        "Contrast with a recursion over n elements, which is where stack depth becomes a real "
        "constraint."
    ),
    py='''
def solve(x, b):
    DIG = "0123456789ABCDEF"
    out = []

    def write(v):
        if v >= b:
            write(v // b)
        out.append(DIG[v % b])

    write(x)
    return "".join(out)
''',
    java='''
    static final String DIG = "0123456789ABCDEF";

    static void write(long x, long b, StringBuilder out) {
        if (x >= b) write(x / b, b, out);
        out.append(DIG.charAt((int) (x % b)));
    }

    static String solve(long x, long b) {
        StringBuilder out = new StringBuilder();
        write(x, b, out);
        return out.toString();
    }
''',
    examples=[
        ("Example 1", "37 2\n"),
        ("Example 2", "48879 16\n"),
    ],
    hidden=[
        ("Zero", "0 7\n"),
        ("A single digit", "9 10\n"),
        ("Exactly the base", "16 16\n"),
        ("Largest value, binary", "1000000000000000000 2\n"),
        ("Largest value, hex", "1000000000000000000 16\n"),
        ("Base 3", "728 3\n"),
        ("Base 12 with letters", "143 12\n"),
    ],
    expl=[
        "37 = 32 + 4 + 1, so its bits are 100101.",
        "48879 = 11·16³ + 14·16² + 14·16 + 15, which spells BEEF.",
    ],
    prereqs=[
        ("recursion", "The digits come out in order because the append runs after the recursive call returns."),
        ("math_digits", "`x % b` is the last digit in base b and `x / b` removes it."),
    ],
)


_p(
    "josephus-survivor", "Last One Standing", "Medium",
    topics=["Recursion", "Math"], subtopics=["Recursion", "Recurrence", "Josephus"],
    companies=["Google", "Amazon"],
    shape="two", ret="long",
    todo="J(1) = 0; J(m) = (J(m - 1) + k) % m — compute it bottom-up so the depth cannot overflow",
    description=(
        "`n` people stand in a circle, numbered `1` to `n`. Starting from person 1, count "
        "`k` people clockwise (counting the starting person as 1); the `k`-th person leaves "
        "the circle. Counting resumes from the next person still standing. Repeat until one "
        "person remains.\n\n"
        "Return the **number of the survivor**.\n\n"
        "### Input\nOne line: `n k`.\n\n### Output\nThe survivor's number."
    ),
    constraints="1 ≤ n ≤ 10^6\n1 ≤ k ≤ 10^9",
    hints=[
        "Simulating with a list is O(n·k) or O(n²). Look for a recurrence instead: relate the survivor of n people to the survivor of n − 1.",
        "After the first removal, n − 1 people remain, and counting restarts just after the removed one — which is position k (0-based) in the old numbering. So the problem of size n − 1 is the old circle, *shifted by k*.",
        "With 0-based positions: J(1) = 0 and J(m) = (J(m − 1) + k) mod m. The answer is J(n) + 1. And with n up to 10⁶, compute it with a loop — the recursion would be a million frames deep.",
    ],
    opt=("O(n)", "O(1)",
         "The recurrence evaluated bottom-up: one addition and one `%` per circle size."),
    editorial=(
        "## The one thing this teaches\n**A correct recursion can still be the wrong program.** "
        "The recurrence is one line and obviously right; written recursively, it needs a "
        "million stack frames and dies with `StackOverflowError` long before n = 10⁶.\n\n"
        "## The recurrence\nNumber positions 0 … m − 1. The first person to leave is at "
        "position `(k − 1) mod m`. Counting resumes at the next position, `k mod m`, so relabel "
        "that person as 0 and the rest follow: this is a circle of m − 1 people, and its "
        "survivor J(m − 1) is in the *new* numbering. Converting back adds the shift:\n\n"
        "```\nJ(1) = 0\nJ(m) = (J(m − 1) + k) mod m\n```\n\n"
        "## Recursive, then iterative\n```java\n// correct, and overflows the stack at n ≈ 10^4\n"
        "static long j(long m, long k) { return m == 1 ? 0 : (j(m - 1, k) + k) % m; }\n\n"
        "// the same recurrence, smallest first\nlong pos = 0;\n"
        "for (long m = 2; m <= n; m++) pos = (pos + k) % m;\nreturn pos + 1;\n```\n\n"
        "The loop computes J(2), J(3), … in exactly the order the recursion would have "
        "*returned* them. Every linear recursion whose work happens after the call converts this "
        "way, and it is what the DP stage calls *bottom-up*.\n\n"
        "## Overflow\n`pos + k` reaches about 10⁶ + 10⁹, which fits an `int` — barely. Use "
        "`long` and stop worrying.\n\n"
        "## Why not simulate?\nAn `ArrayList` removal is O(n), so simulation is O(n²) = 10¹² at "
        "the limit. A circular linked list is O(n·k). The recurrence never builds the circle at "
        "all."
    ),
    py='''
def solve(n, k):
    pos = 0
    for m in range(2, n + 1):
        pos = (pos + k) % m
    return pos + 1
''',
    java='''
    static long solve(long n, long k) {
        long pos = 0;
        for (long m = 2; m <= n; m++) pos = (pos + k) % m;
        return pos + 1;
    }
''',
    examples=[
        ("Example 1", "6 2\n"),
        ("Example 2", "9 4\n"),
    ],
    hidden=[
        ("One person", "1 5\n"),
        ("k = 1: the last in line survives", "10 1\n"),
        ("Two people", "2 3\n"),
        ("k larger than n", "5 1000000000\n"),
        ("Large n", "1000000 3\n"),
        ("Large n and k", "1000000 999999937\n"),
        ("Power of two with k = 2", "1024 2\n"),
    ],
    expl=[
        "People leave in the order 2, 4, 6, 3, 1; person 5 survives.",
        "People leave in the order 4, 8, 3, 9, 6, 5, 7, 2; person 1 survives.",
    ],
    prereqs=[
        ("recursion", "The survivor of n people is defined in terms of the survivor of n − 1."),
        ("recurrence", "J(m) = (J(m − 1) + k) mod m, evaluated smallest first."),
        ("modulo", "Positions wrap around the circle."),
    ],
)


_p(
    "mulmod-by-halving", "Multiply Without Overflow", "Medium",
    topics=["Recursion", "Math"], subtopics=["Halving Recursion", "Modular Arithmetic", "Overflow"],
    companies=["Google", "Bloomberg"],
    shape="three", ret="long",
    todo="mul(a, b) = 2·mul(a, b / 2) (+ a when b is odd), reducing mod m after every step",
    description=(
        "Compute `(a · b) mod m`.\n\n"
        "All three numbers can be as large as 10¹⁸, so `a * b` overflows a 64-bit integer "
        "long before the `% m`. Do it with additions only, using the same halving idea as fast "
        "exponentiation.\n\n"
        "### Input\nOne line: `a b m`.\n\n### Output\n`(a · b) mod m`."
    ),
    constraints="0 ≤ a, b ≤ 10^18\n1 ≤ m ≤ 10^18",
    hints=[
        "a · b = a + a + … + a (b times). Adding one at a time is O(b) — far too slow for b = 10¹⁸.",
        "Halve b: a · b = 2 · (a · ⌊b/2⌋), plus one extra a when b is odd. That is fast power with × replaced by +.",
        "Reduce a mod m first. Then every intermediate value is < m ≤ 10¹⁸, and doubling it stays below 2·10¹⁸ < 9.2·10¹⁸ — it fits in a long.",
    ],
    opt=("O(log b)", "O(log b)",
         "One recursive call per bit of b; each does a doubling and at most one addition."),
    editorial=(
        "## The one thing this teaches\n**Fast power is not about powers.** It is halving "
        "recursion over any associative operation. Replace × by + and it computes a product "
        "using only additions — which matters when the product itself does not fit.\n\n"
        "## Approach\n```java\nstatic long mul(long a, long b, long m) {   // a < m\n"
        "    if (b == 0) return 0;\n"
        "    long half = mul(a, b / 2, m);             // ONE call\n"
        "    long r = (half + half) % m;               // < 2m <= 2e18, fits\n"
        "    if (b % 2 == 1) r = (r + a) % m;\n"
        "    return r;\n}\n// solve: mul(a % m, b, m)\n```\n\n"
        "## The overflow argument\nEvery value the function returns is < m. Doubling it gives "
        "< 2m ≤ 2·10¹⁸, and `Long.MAX_VALUE` ≈ 9.22·10¹⁸, so `half + half` cannot overflow; "
        "neither can `r + a`, which is < 2m as well. That argument is the entire point — "
        "write it before you write the code.\n\n"
        "## The same bug as fast power\nCalling `mul(a, b / 2, m)` twice instead of storing it "
        "turns O(log b) into O(b): 10¹⁸ operations.\n\n"
        "## In practice\nJava offers `Math.multiplyHigh` (the top 64 bits of the 128-bit "
        "product) and `BigInteger`; C++ has `__int128`. They are faster. This is the technique "
        "that works everywhere, and it is the building block of Miller–Rabin primality testing "
        "on 64-bit numbers."
    ),
    py='''
def solve(a, b, m):
    a %= m
    # iterative form of the halving recursion (same order of operations)
    bits = bin(b)[2:] if b else ""
    r = 0
    for bit in bits:
        r = (r + r) % m
        if bit == "1":
            r = (r + a) % m
    return r
''',
    java='''
    static long mul(long a, long b, long m) {
        if (b == 0) return 0;
        long half = mul(a, b / 2, m);
        long r = (half + half) % m;
        if (b % 2 == 1) r = (r + a) % m;
        return r;
    }

    static long solve(long a, long b, long m) {
        return mul(a % m, b, m);
    }
''',
    examples=[
        ("Example 1", "123456789 987654321 1000000007\n"),
        ("Example 2", "1000000000000000000 1000000000000000000 999999999999999989\n"),
    ],
    hidden=[
        ("Zero factor", "0 123 7\n"),
        ("Zero other factor", "55 0 7\n"),
        ("Modulus one", "999 999 1\n"),
        ("Small, checkable", "12 13 100\n"),
        ("a larger than m", "1000000000000000000 3 7\n"),
        ("Both near the limit", "999999999999999999 999999999999999998 1000000000000000000\n"),
        ("Power-of-two modulus", "987654321987654321 123456789123456789 1152921504606846976\n"),
    ],
    expl=[
        "The true product is about 1.2·10¹⁷, which happens to fit — but the method does not rely on that.",
        "Here a · b = 10³⁶, far past any 64-bit type. Halving b keeps every intermediate below 2·10¹⁸.",
    ],
    prereqs=[
        ("recursion", "Halving recursion: one call on b / 2, stored and reused."),
        ("overflow", "The bound 2m ≤ 2·10¹⁸ < 2⁶³ is what makes every step safe."),
        ("modulo", "Reduce after every addition so values stay below m."),
    ],
)


def _closest_ref():
    return '''
def solve(p):
    pts = sorted(p)
    INF = float("inf")

    def d2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    def rec(lo, hi):                         # pts[lo:hi] sorted by x; returns (best, by_y)
        if hi - lo <= 3:
            best = INF
            for i in range(lo, hi):
                for j in range(i + 1, hi):
                    best = min(best, d2(pts[i], pts[j]))
            return best, sorted(pts[lo:hi], key=lambda q: q[1])
        mid = (lo + hi) // 2
        midx = pts[mid][0]
        bl, yl = rec(lo, mid)
        br, yr = rec(mid, hi)
        best = min(bl, br)
        merged, i, j = [], 0, 0
        while i < len(yl) and j < len(yr):
            if yl[i][1] <= yr[j][1]:
                merged.append(yl[i]); i += 1
            else:
                merged.append(yr[j]); j += 1
        merged += yl[i:] + yr[j:]
        strip = [q for q in merged if (q[0] - midx) ** 2 < best]
        for i in range(len(strip)):
            for j in range(i + 1, len(strip)):
                if (strip[j][1] - strip[i][1]) ** 2 >= best:
                    break
                best = min(best, d2(strip[i], strip[j]))
        return best, merged

    return rec(0, len(pts))[0]
'''


def _closest_big():
    xs = _lcg_ints(7, 3000, -10**9, 10**9)
    ys = _lcg_ints(11, 3000, -10**9, 10**9)
    return "3000\n" + "".join(f"{x} {y}\n" for x, y in zip(xs, ys))


def _closest_grid():
    pts = [(i * 1000, j * 1000) for i in range(40) for j in range(40)]
    pts.append((17 * 1000 + 3, 22 * 1000 + 4))
    return f"{len(pts)}\n" + "".join(f"{x} {y}\n" for x, y in pts)


_p(
    "closest-pair-points", "Two Closest Towers", "Hard",
    topics=["Divide and Conquer", "Geometry"], subtopics=["Divide and Conquer", "Closest Pair", "Sorting"],
    companies=["Google", "Uber"],
    shape="pairs", ret="long",
    todo="sort by x, solve each half, then check only the strip of width √best around the midline, sorted by y",
    description=(
        "`n` radio towers stand at integer points `(x, y)` on a map. Return the **squared** "
        "Euclidean distance between the two closest towers.\n\n"
        "Two towers may share a location, in which case the answer is 0.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `x y`.\n\n### Output\nThe smallest "
        "`(x1 − x2)² + (y1 − y2)²` over all pairs."
    ),
    constraints="2 ≤ n ≤ 100000\n-10^9 ≤ x, y ≤ 10^9",
    hints=[
        "Checking every pair is O(n²) = 5·10⁹ at the limit. Split the points by x at the median and solve each half recursively.",
        "Let δ be the better of the two halves' answers. A pair that crosses the midline and beats δ must have both points within √δ of the line — keep only that *strip*.",
        "Sort the strip by y. Each point then needs comparing only with the next few points above it: once the y-gap alone reaches √δ, nothing further up can win. A packing argument caps it at 7.",
    ],
    opt=("O(n log n)", "O(n)",
         "Two recursive halves plus a linear strip scan, with the y-order produced by merging on the way up."),
    editorial=(
        "## The one thing this teaches\n**In divide and conquer, the combine step is the "
        "algorithm.** The two recursive calls are trusted and free; the only new idea is how to "
        "find a pair that crosses the midline without checking all n²/4 of them.\n\n"
        "## Approach\n1. Sort by x. Split at the middle index; the midline is `x = pts[mid].x`.\n"
        "2. Recursively find δ_L and δ_R. Let δ = min of them (squared).\n"
        "3. The **strip**: points whose squared horizontal distance to the midline is < δ. Any "
        "better crossing pair lies inside it.\n"
        "4. Walk the strip in increasing y. For each point, compare with following points only "
        "while their y-gap² is < δ.\n\n"
        "## Why step 4 is linear\nAll points on one side of the midline are at least √δ apart. "
        "A √δ × 2√δ box above a point, spanning both sides, can hold at most 8 points under that "
        "constraint — so the inner loop runs a constant number of times per point.\n\n"
        "## Keeping it O(n log n)\nSorting the strip by y at every level would be O(n log² n) "
        "— acceptable, in fact. The textbook version does better by having each call **return "
        "its points sorted by y**, merged from its children exactly like merge sort. The "
        "recursion then sorts by y as a side effect.\n\n"
        "## Squared distances\nWorking with `dx² + dy²` avoids `sqrt` and floating point "
        "entirely. Coordinates up to 10⁹ give squared distances up to 8·10¹⁸ — inside `long` "
        "(9.22·10¹⁸), with no room to spare; compute `dx` as a `long` before squaring.\n\n"
        "## Duplicates\nTwo identical points give δ = 0, and the strip condition `< 0` then "
        "admits nothing — correct, since nothing beats 0."
    ),
    py=_closest_ref(),
    java='''
    static long[][] P;
    static long[][] buf;

    static long d2(long[] a, long[] b) {
        long dx = a[0] - b[0], dy = a[1] - b[1];
        return dx * dx + dy * dy;
    }

    // P[lo..hi) sorted by x on entry; sorted by y on exit
    static long rec(int lo, int hi) {
        if (hi - lo <= 3) {
            long best = Long.MAX_VALUE;
            for (int i = lo; i < hi; i++)
                for (int j = i + 1; j < hi; j++) best = Math.min(best, d2(P[i], P[j]));
            Arrays.sort(P, lo, hi, (u, v) -> Long.compare(u[1], v[1]));
            return best;
        }
        int mid = (lo + hi) >>> 1;
        long midx = P[mid][0];
        long best = Math.min(rec(lo, mid), rec(mid, hi));
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi) buf[k++] = P[i][1] <= P[j][1] ? P[i++] : P[j++];
        while (i < mid) buf[k++] = P[i++];
        while (j < hi) buf[k++] = P[j++];
        System.arraycopy(buf, lo, P, lo, hi - lo);
        int s = 0;
        long[][] strip = new long[hi - lo][];
        for (int t = lo; t < hi; t++) {
            long dx = P[t][0] - midx;
            if (dx * dx < best) strip[s++] = P[t];
        }
        for (int a = 0; a < s; a++)
            for (int b = a + 1; b < s; b++) {
                long dy = strip[b][1] - strip[a][1];
                if (dy * dy >= best) break;
                best = Math.min(best, d2(strip[a], strip[b]));
            }
        return best;
    }

    static long solve(int[][] p) {
        int n = p.length;
        P = new long[n][];
        for (int i = 0; i < n; i++) P[i] = new long[]{ p[i][0], p[i][1] };
        Arrays.sort(P, (u, v) -> u[0] != v[0] ? Long.compare(u[0], v[0]) : Long.compare(u[1], v[1]));
        buf = new long[n][];
        return rec(0, n);
    }
''',
    examples=[
        ("Example 1", "5\n0 0\n7 3\n2 9\n6 1\n-4 5\n"),
        ("Example 2", "4\n10 10\n-3 8\n10 10\n25 -6\n"),
    ],
    hidden=[
        ("Two points", "2\n-1000000000 -1000000000\n1000000000 1000000000\n"),
        ("Collinear on x", "6\n0 0\n0 10\n0 3\n0 21\n0 15\n0 28\n"),
        ("Collinear on y", "5\n9 4\n1 4\n14 4\n6 4\n20 4\n"),
        ("Pair straddles the midline", "6\n0 0\n1 50\n2 100\n3 0\n4 50\n5 100\n"),
        ("Grid plus one intruder", _closest_grid()),
        ("3000 random points", _closest_big()),
    ],
    expl=[
        "(7, 3) and (6, 1) differ by 1 and 2, so the squared distance is 1 + 4 = 5.",
        "Two towers share (10, 10), so the answer is 0.",
    ],
    prereqs=[
        ("recursion", "Divide and conquer: split at the median x and trust both halves."),
        ("sorting", "Sort by x once; each call returns its points merged by y."),
        ("overflow", "Squared distances reach 8·10¹⁸ — compute in `long`."),
    ],
)


# -------------------------------------------------------------------- sorting

_p(
    "rank-transform", "Replace Each Value With Its Rank", "Easy",
    topics=["Sorting", "Arrays"], subtopics=["Sorting", "Ranking", "Coordinate Compression"],
    companies=["Amazon", "Google"],
    shape="arr", ret="String",
    todo="sort a copy, deduplicate it, and replace each value with 1 + its index in the distinct sorted values",
    description=(
        "Replace every element with its **rank**: 1 for the smallest value, 2 for the next "
        "distinct value, and so on. Equal values share a rank, and ranks have **no gaps**.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nThe `n` ranks, "
        "space-separated, in the original order."
    ),
    constraints="1 ≤ n ≤ 200000\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Sorting destroys the original order, and the output needs it. So sort a *copy*.",
        "In the sorted copy, walk once and assign a new rank each time the value changes.",
        "Then map each original value to its rank — a hash map, or a binary search into the deduplicated sorted array.",
    ],
    opt=("O(n log n)", "O(n)",
         "One sort of a copy, one pass to assign ranks, one lookup per element."),
    editorial=(
        "## The one thing this teaches\n**Sort a copy when the answer is reported in the "
        "original order.** This is *coordinate compression*: map arbitrary values onto 1…k while "
        "preserving their order — the first step of every Fenwick-tree-over-values solution.\n\n"
        "## Approach\n```java\nint[] s = a.clone();\nArrays.sort(s);\nint k = 0;\n"
        "for (int i = 0; i < n; i++)\n    if (i == 0 || s[i] != s[i - 1]) s[k++] = s[i];  // dedupe in place\n"
        "for (int i = 0; i < n; i++)\n"
        "    out[i] = Arrays.binarySearch(s, 0, k, a[i]) + 1;\n```\n\n"
        "## Dense ranks versus competition ranks\nThis problem uses **dense** ranks (1, 2, 2, "
        "3): the rank counts *distinct* smaller values. `leaderboard-ranks` uses **competition** "
        "ranks (1, 2, 2, 4): the rank counts *all* elements that beat you. Read which one is "
        "asked for; they differ exactly at ties.\n\n"
        "## Hash map or binary search?\nBoth are fine. The binary search version needs no "
        "boxing and no extra structure beyond the sorted array — and it is the standard "
        "compression idiom, because the same sorted array later answers “what value has rank "
        "r?” by indexing."
    ),
    py='''
def solve(a):
    s = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(s)}
    return " ".join(str(rank[x]) for x in a)
''',
    java='''
    static String solve(int[] a) {
        int n = a.length;
        int[] s = a.clone();
        Arrays.sort(s);
        int k = 0;
        for (int i = 0; i < n; i++)
            if (i == 0 || s[i] != s[i - 1]) s[k++] = s[i];
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(Arrays.binarySearch(s, 0, k, a[i]) + 1);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6\n40 -7 12 40 3 12\n"),
        ("Example 2", "4\n5 5 5 5\n"),
    ],
    hidden=[
        ("One element", "1\n-1000000000\n"),
        ("Already sorted, distinct", "5\n1 2 3 4 5\n"),
        ("Descending", "5\n9 7 5 3 1\n"),
        ("Extremes", "4\n1000000000 -1000000000 0 1000000000\n"),
        ("Many ties", "8\n3 1 3 1 2 2 3 1\n"),
    ],
    expl=[
        "The distinct values in order are −7, 3, 12, 40, so they get ranks 1, 2, 3, 4.",
        "Every value is equal, so every rank is 1.",
    ],
    prereqs=[
        ("sorting", "Sort a copy, so the original order survives for the output."),
        ("binary_search", "Each value's rank is its position in the deduplicated sorted array."),
    ],
)


_p(
    "radix-pass-by-pass", "Radix Sort, One Pass at a Time", "Medium",
    topics=["Sorting"], subtopics=["Radix Sort", "Counting Sort", "Stability"],
    companies=["Google", "Microsoft"],
    shape="arr", ret="String",
    todo="for each decimal digit from the ones upward, stably bucket the current order by that digit and record the order",
    description=(
        "Sort the numbers with **least-significant-digit radix sort in base 10**, and show "
        "your work.\n\n"
        "Let `D` be the number of decimal digits in the largest value (`0` has one digit). "
        "Perform `D` passes: pass 1 orders by the ones digit, pass 2 by the tens digit, and so "
        "on. Each pass must be **stable** — numbers with the same digit keep the order the "
        "previous pass left them in.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` non-negative integers.\n\n### Output\n`D` lines: "
        "the whole array after each pass, space-separated."
    ),
    constraints="1 ≤ n ≤ 20000\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "One pass: ten buckets, 0 to 9. Walk the current order from left to right and drop each number into the bucket of its current digit. Then read the buckets out in order 0 → 9.",
        "Walking left to right and appending to the back of each bucket is what makes the pass stable.",
        "The digit for pass p (1-based) is `(x / 10^(p−1)) % 10`. After the last pass the array is fully sorted — check that your final line is.",
    ],
    opt=("O(D · (n + 10))", "O(n)",
         "D stable counting passes; the output itself is D · n numbers."),
    editorial=(
        "## The one thing this teaches\n**Stability is not a nicety; it is the algorithm.** "
        "Each pass sorts on one digit only, and the order it leaves among equal digits is the "
        "work of every earlier pass. An unstable pass throws that work away.\n\n"
        "## One pass, as counting sort\n```java\nint[] cnt = new int[11];\n"
        "for (int x : a) cnt[(int) (x / exp % 10) + 1]++;\n"
        "for (int d = 0; d < 10; d++) cnt[d + 1] += cnt[d];      // bucket starts\n"
        "for (int x : a) out[cnt[(int) (x / exp % 10)]++] = x;  // left to right: stable\n"
        "```\n\n"
        "## Why least significant first?\nAfter pass p, the array is sorted by the last p "
        "digits. Pass p + 1 sorts by digit p + 1, and for numbers that tie on it, stability keeps "
        "them in last-p-digits order — so now they are sorted by the last p + 1 digits. That is "
        "the invariant, and it only holds because each pass is stable.\n\n"
        "## Cost\nD passes of O(n + base). For 32-bit keys in base 256 that is 4 passes, "
        "independent of n — O(n) overall, beating the Ω(n log n) comparison bound because the "
        "algorithm never compares two keys.\n\n"
        "## Where it shows up\nSuffix-array construction by prefix doubling sorts pairs of ranks "
        "with two radix passes; sorting 64-bit ids or IPv4 addresses in bulk is radix sort's "
        "home ground."
    ),
    py='''
def solve(a):
    D = len(str(max(a)))
    lines = []
    exp = 1
    for _ in range(D):
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // exp) % 10].append(x)
        a = [x for b in buckets for x in b]
        lines.append(" ".join(map(str, a)))
        exp *= 10
    return "\\n".join(lines)
''',
    java='''
    static String solve(int[] a) {
        int n = a.length, mx = 0;
        for (int x : a) mx = Math.max(mx, x);
        int D = String.valueOf(mx).length();
        int[] out = new int[n];
        StringBuilder sb = new StringBuilder();
        long exp = 1;
        for (int p = 0; p < D; p++) {
            int[] cnt = new int[11];
            for (int x : a) cnt[(int) (x / exp % 10) + 1]++;
            for (int d = 0; d < 10; d++) cnt[d + 1] += cnt[d];
            for (int x : a) out[cnt[(int) (x / exp % 10)]++] = x;
            int[] t = a; a = out; out = t;
            if (p > 0) sb.append('\\n');
            for (int i = 0; i < n; i++) {
                if (i > 0) sb.append(' ');
                sb.append(a[i]);
            }
            exp *= 10;
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "7\n512 38 207 91 450 26 873\n"),
        ("Example 2", "5\n5 3 8 3 0\n"),
    ],
    hidden=[
        ("All zeros", "3\n0 0 0\n"),
        ("One element", "1\n1000000000\n"),
        ("Stability on equal digits", "6\n21 11 31 12 22 32\n"),
        ("Mixed widths", "8\n7 70 700 7000 77 707 770 1\n"),
        ("Already sorted", "5\n10 20 30 40 50\n"),
        ("Ten-digit maximum", "4\n1000000000 999999999 5 123456789\n"),
    ],
    expl=[
        "Three-digit maximum, so three passes. After the tens pass the last two digits are in order; the hundreds pass finishes the sort.",
        "Every value has one digit, so a single pass sorts them. The two 3s keep their input order.",
    ],
    prereqs=[
        ("alg_non_comparison_sorts", "Radix sort is repeated counting sort, one digit per pass."),
        ("sorting", "Stability: equal digits keep the previous pass's order."),
    ],
)


_p(
    "moves-to-median", "Level the Shelf", "Medium",
    topics=["Sorting", "Math"], subtopics=["Median", "Quickselect", "Sorting"],
    companies=["Amazon", "Google"],
    shape="arr", ret="long",
    todo="find the median (sort, or quickselect) and add up |a[i] - median|",
    description=(
        "Books on a shelf have heights `a[0..n-1]`. In one move you can raise or lower one "
        "book's height by 1 (by adding or removing a spacer). Return the **minimum number of "
        "moves** to make every height equal.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nThe minimum total moves."
    ),
    constraints="1 ≤ n ≤ 200000\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "If everything ends at height m, the cost is Σ |a[i] − m|. Which m minimises that?",
        "Move m up by one: every element below m costs one more, every element above costs one less. So moving up helps while more elements are above than below — the best m has half on each side. That is the **median**.",
        "Sorting finds it in O(n log n); quickselect in O(n) on average. The total can reach 2·10⁵ · 2·10⁹ — use `long`.",
    ],
    opt=("O(n) average", "O(1) extra",
         "Quickselect for the median, then one pass summing distances."),
    editorial=(
        "## The one thing this teaches\n**The median minimises the sum of absolute "
        "deviations** (the mean minimises the sum of *squared* deviations — a different "
        "question). Once you know which statistic you need, finding it is quickselect.\n\n"
        "## Why the median\nLet m be the target and L, R the number of elements strictly below "
        "and above it. Raising m by 1 changes the cost by L − R. While R > L, raising helps; "
        "while L > R, lowering helps. The cost is minimised where neither helps: half the "
        "elements on each side. For even n, **any** m between the two middle values is optimal, "
        "so either middle element works.\n\n"
        "## Approach\n```java\nint k = n / 2;\nint m = quickselect(a, k);   // or: sort, then a[n / 2]\n"
        "long moves = 0;\nfor (int x : a) moves += Math.abs((long) x - m);\n```\n\n"
        "## Quickselect, not sort\nSorting is O(n log n) and perfectly acceptable here. "
        "Quickselect answers the one question asked — the element at index n/2 — in O(n) "
        "expected time by recursing into one side of each partition. Use a **random pivot**, or "
        "adversarial input (already sorted) makes it O(n²).\n\n"
        "## Overflow\n`x - m` can be 2·10⁹ — outside `int` — before `Math.abs` even runs. "
        "Cast first: `(long) x - m`."
    ),
    py='''
def solve(a):
    s = sorted(a)
    m = s[len(s) // 2]
    return sum(abs(x - m) for x in a)
''',
    java='''
    static final Random RNG = new Random(12345);

    static void swap(int[] a, int i, int j) { int t = a[i]; a[i] = a[j]; a[j] = t; }

    static int select(int[] a, int k) {
        int lo = 0, hi = a.length - 1;
        while (true) {
            if (lo == hi) return a[lo];
            swap(a, lo + RNG.nextInt(hi - lo + 1), hi);
            int pivot = a[hi];
            // three-way partition so runs of equal values cannot degrade it
            int lt = lo, i = lo, gt = hi;
            while (i <= gt) {
                if (a[i] < pivot) swap(a, lt++, i++);
                else if (a[i] > pivot) swap(a, i, gt--);
                else i++;
            }
            if (k < lt) hi = lt - 1;
            else if (k > gt) lo = gt + 1;
            else return pivot;
        }
    }

    static long solve(int[] a) {
        int m = select(a.clone(), a.length / 2);
        long moves = 0;
        for (int x : a) moves += Math.abs((long) x - m);
        return moves;
    }
''',
    examples=[
        ("Example 1", "5\n4 9 1 7 4\n"),
        ("Example 2", "4\n10 2 6 8\n"),
    ],
    hidden=[
        ("One book", "1\n42\n"),
        ("Already level", "4\n7 7 7 7\n"),
        ("Extremes", "2\n-1000000000 1000000000\n"),
        ("Large total", "6\n-1000000000 -1000000000 -1000000000 1000000000 1000000000 1000000000\n"),
        ("Sorted input", "7\n1 2 3 4 5 6 7\n"),
        ("Duplicates everywhere", "9\n5 1 5 1 5 1 5 1 5\n"),
    ],
    expl=[
        "The median is 4. Moves: 0 + 5 + 3 + 3 + 0 = 11.",
        "Any target between 6 and 8 costs 10 — for example 6: 4 + 4 + 0 + 2.",
    ],
    prereqs=[
        ("sorting", "Quickselect: partition, then keep only the side holding index n/2."),
        ("overflow", "The distances and their sum exceed `int`."),
    ],
)


def _reverse_pairs_big():
    vals = _lcg_ints(2024, 4000, -2147483648, 2147483647)
    return "4000\n" + " ".join(map(str, vals)) + "\n"


_p(
    "important-reverse-pairs", "Pairs More Than Twice as Large", "Hard",
    topics=["Sorting", "Divide and Conquer"], subtopics=["Merge Sort", "Counting Pairs", "Overflow"],
    companies=["Google", "Amazon"],
    shape="arr", ret="long",
    todo="merge sort; before each merge, count pairs with a[i] > 2·a[j] using a two-pointer pass over the sorted halves",
    description=(
        "Count the pairs of indices `i < j` with **`a[i] > 2 · a[j]`**.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nThe number of such pairs."
    ),
    constraints="1 ≤ n ≤ 100000\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "All pairs is O(n²) = 5·10⁹ at the limit. Every pair i < j either lies inside one half of the array or crosses the midpoint — divide and conquer.",
        "Once both halves are sorted, count the crossing pairs with two pointers: for each i in the left half, advance j in the right half while `a[i] > 2·a[j]`. Since the left half is increasing, j never moves back.",
        "Count **before** merging, in a separate pass: the merge itself compares a[i] with a[j], not with 2·a[j]. And compute `2L * a[j]` — 2·(2³¹ − 1) does not fit in an int.",
    ],
    opt=("O(n log n)", "O(n)",
         "Merge sort, plus one linear two-pointer counting pass per merge."),
    editorial=(
        "## The one thing this teaches\n**Merge sort counts pairs for any condition that is "
        "monotone in both halves — but the count and the merge are separate passes when the "
        "condition is not the sort order.** For plain inversions (`a[i] > a[j]`) you can count "
        "while merging. For `a[i] > 2·a[j]` you cannot: the merge decides by `a[i] ≤ a[j]`, "
        "which says nothing about 2·a[j].\n\n"
        "## Approach\n```java\nlong sortCount(long[] a, long[] buf, int lo, int hi) {   // [lo, hi)\n"
        "    if (hi - lo < 2) return 0;\n    int mid = (lo + hi) >>> 1;\n"
        "    long c = sortCount(a, buf, lo, mid) + sortCount(a, buf, mid, hi);\n"
        "    for (int i = lo, j = mid; i < mid; i++) {           // count first\n"
        "        while (j < hi && a[i] > 2 * a[j]) j++;\n"
        "        c += j - mid;\n    }\n"
        "    merge(a, buf, lo, mid, hi);                          // then merge\n    return c;\n}\n```\n\n"
        "## Why the two pointers never go back\nBoth halves are sorted. If `a[i] > 2·a[j]`, then "
        "the larger `a[i+1]` beats that `a[j]` too, so j for i + 1 starts where j for i stopped. "
        "The counting pass is O(n) per level; log n levels make O(n log n).\n\n"
        "## Overflow\n`2 * a[j]` with `a[j] = 2³¹ − 1` is 2³² − 2, and with `a[j] = −2³¹` it is "
        "−2³². Neither fits in an `int`. Store the array as `long`, or write `2L * a[j]`.\n\n"
        "## The count can be large\nUp to n(n − 1)/2 ≈ 5·10⁹ pairs — return a `long`.\n\n"
        "## Alternatives\nA Fenwick tree over compressed values also works: walk left to "
        "right, and for each a[j] count earlier elements > 2·a[j]. Same complexity, more "
        "machinery; merge sort needs nothing but the sort."
    ),
    py='''
def solve(a):
    a = list(a)
    buf = [0] * len(a)

    def rec(lo, hi):
        if hi - lo < 2:
            return 0
        mid = (lo + hi) // 2
        c = rec(lo, mid) + rec(mid, hi)
        j = mid
        for i in range(lo, mid):
            while j < hi and a[i] > 2 * a[j]:
                j += 1
            c += j - mid
        i, j, k = lo, mid, lo
        while i < mid and j < hi:
            if a[i] <= a[j]:
                buf[k] = a[i]; i += 1
            else:
                buf[k] = a[j]; j += 1
            k += 1
        while i < mid:
            buf[k] = a[i]; i += 1; k += 1
        while j < hi:
            buf[k] = a[j]; j += 1; k += 1
        a[lo:hi] = buf[lo:hi]
        return c

    return rec(0, len(a))
''',
    java='''
    static long rec(long[] a, long[] buf, int lo, int hi) {
        if (hi - lo < 2) return 0;
        int mid = (lo + hi) >>> 1;
        long c = rec(a, buf, lo, mid) + rec(a, buf, mid, hi);
        for (int i = lo, j = mid; i < mid; i++) {
            while (j < hi && a[i] > 2 * a[j]) j++;
            c += j - mid;
        }
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi) buf[k++] = a[i] <= a[j] ? a[i++] : a[j++];
        while (i < mid) buf[k++] = a[i++];
        while (j < hi) buf[k++] = a[j++];
        System.arraycopy(buf, lo, a, lo, hi - lo);
        return c;
    }

    static long solve(int[] a) {
        int n = a.length;
        long[] b = new long[n];
        for (int i = 0; i < n; i++) b[i] = a[i];
        return rec(b, new long[n], 0, n);
    }
''',
    examples=[
        ("Example 1", "5\n9 2 7 3 1\n"),
        ("Example 2", "4\n-6 -2 -5 4\n"),
    ],
    hidden=[
        ("One element", "1\n5\n"),
        ("Exactly twice is not enough", "4\n8 4 2 1\n"),
        ("Increasing", "5\n1 2 3 4 5\n"),
        ("Int extremes", "4\n2147483647 1073741823 -2147483648 -1073741825\n"),
        ("All equal negatives", "5\n-3 -3 -3 -3 -3\n"),
        ("Zeros and signs", "6\n0 -1 0 1 0 -1\n"),
        ("4000 random ints", _reverse_pairs_big()),
    ],
    expl=[
        "Six pairs qualify: (9, 2), (9, 3), (9, 1), (7, 3), (7, 1) and (3, 1). (2, 1) does not — 2 is exactly twice 1, not more.",
        "Doubling a negative makes it smaller: −6 > 2·(−5) = −10 and −2 > −10. Nothing beats 2·4 = 8. Two pairs.",
    ],
    prereqs=[
        ("sorting", "Merge sort: both halves sorted before the crossing pairs are counted."),
        ("two_pointers", "For sorted halves, the right pointer only ever moves forward."),
        ("overflow", "2·a[j] leaves the `int` range at the extremes."),
    ],
)
