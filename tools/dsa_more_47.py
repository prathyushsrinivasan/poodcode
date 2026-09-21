# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 47 — Order & Search, part 2: binary search.
#
#   min-time-for-trips          search on the answer, with an overflow in the check
#   max-equal-portions          the mirror image: the LAST feasible value
#   sqrt-to-six-places          a real-valued answer, made exact by scaling
#   nth-divisible-number        count ≤ x by inclusion–exclusion, then search x
#   kth-in-multiplication-table count ≤ x over a table too big to build
#
# The binary-search unit had one "search on the answer" shape (minimise) and no
# value-space counting. These cover minimise, maximise, count-≤-x and a
# real-valued search, each with the boundary detail that breaks it.
# ===========================================================================


_p(
    "min-time-for-trips", "Enough Deliveries", "Medium",
    topics=["Binary Search"], subtopics=["Binary Search on the Answer", "Overflow"],
    companies=["Amazon", "Uber"],
    shape="arr_k", ret="long",
    todo="binary-search the time T; T is enough when the sum of T / time[i] reaches k (stop summing once it does)",
    description=(
        "A courier company has `n` vans. Van `i` completes one delivery every `time[i]` "
        "minutes, back to back, and all vans start at minute 0. Return the **minimum number of "
        "minutes** after which the vans have completed at least `k` deliveries in total.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` integers `time[i]`.\n\n### Output\nThe minimum "
        "time."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ k ≤ 10^7\n1 ≤ time[i] ≤ 10^7",
    hints=[
        "Given a time T, counting deliveries is easy: van i has done ⌊T / time[i]⌋ of them. And more time never means fewer deliveries — the check is monotone.",
        "So binary-search T. The lower bound is 1; a safe upper bound is `min(time) · k` — the fastest van alone gets there.",
        "The sum of ⌊T / time[i]⌋ can overflow even a long when T is huge and many times are 1. Stop adding as soon as the running total reaches k.",
    ],
    opt=("O(n log(min(time) · k))", "O(1)",
         "About 47 probes of an O(n) count."),
    editorial=(
        "## The one thing this teaches\n**Search on the answer, when checking is easy and "
        "constructing is not.** You cannot easily say *when* the k-th delivery happens, but for "
        "any T you can say *whether* k have happened — and that yes/no flips exactly once.\n\n"
        "## Approach\n```java\nlong lo = 1, hi = (long) minTime * k;       // hi is certainly enough\n"
        "while (lo < hi) {\n    long mid = lo + (hi - lo) / 2;\n"
        "    if (enough(time, mid, k)) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n\n"
        "static boolean enough(int[] time, long T, long k) {\n    long done = 0;\n"
        "    for (int t : time) {\n        done += T / t;\n"
        "        if (done >= k) return true;            // stop before it overflows\n    }\n"
        "    return false;\n}\n```\n\n"
        "## Choosing hi\nThe fastest van alone completes k deliveries by `min(time) · k`, so that "
        "time is always enough — which is what `hi` must be. `max(time) · k` also works but "
        "wastes a few probes; `k` alone is wrong whenever every van is slower than one minute.\n\n"
        "## The overflow in the check\nWith T near 10¹⁴ and 10⁵ vans of time 1, the total is "
        "10¹⁹ — past `Long.MAX_VALUE`. The early return makes it impossible: the total never "
        "exceeds k + T ≤ 10¹⁴ + 10⁷ before the function returns.\n\n"
        "## Monotonicity, stated\nIf k deliveries are done by T, they are done by T + 1: every "
        "⌊T / time[i]⌋ is non-decreasing in T. Write that sentence before the loop — it is the "
        "only thing the loop relies on."
    ),
    py='''
def solve(a, k):
    def enough(T):
        done = 0
        for t in a:
            done += T // t
            if done >= k:
                return True
        return False

    lo, hi = 1, min(a) * k
    while lo < hi:
        mid = (lo + hi) // 2
        if enough(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static boolean enough(int[] a, long T, long k) {
        long done = 0;
        for (int t : a) {
            done += T / t;
            if (done >= k) return true;
        }
        return false;
    }

    static long solve(int[] a, long k) {
        long mn = Long.MAX_VALUE;
        for (int t : a) mn = Math.min(mn, t);
        long lo = 1, hi = mn * k;
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            if (enough(a, mid, k)) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[
        ("Example 1", "3 7\n2 3 5\n"),
        ("Example 2", "2 1\n9 4\n"),
    ],
    hidden=[
        ("One van", "1 10000000\n10000000\n"),
        ("Fast vans, many of them", "5 10000000\n1 1 1 1 1\n"),
        ("Exact boundary", "2 5\n3 3\n"),
        ("Mixed", "4 20\n7 2 9 4\n"),
        ("Slow fleet", "3 3\n10000000 10000000 10000000\n"),
        ("Large k, varied", "6 9999991\n13 1 7 10000000 3 9999999\n"),
    ],
    expl=[
        "By minute 8 the vans have done 4 + 2 + 1 = 7 deliveries; at minute 7 only 3 + 2 + 1 = 6.",
        "The faster van finishes its first delivery at minute 4.",
    ],
    prereqs=[
        ("binary_search", "Binary search over time, not over an array."),
        ("overflow", "Stop the count once it reaches k, or the sum can pass 2^63."),
    ],
)


_p(
    "max-equal-portions", "Longest Equal Ribbons", "Medium",
    topics=["Binary Search"], subtopics=["Binary Search on the Answer", "Maximise the Minimum"],
    companies=["Amazon", "Google"],
    shape="arr_k", ret="long",
    todo="find the LARGEST length L with sum(a[i] / L) >= k — round mid up, or search for the first failing L",
    description=(
        "You have `n` ribbons of integer lengths `a[i]`. Cut them into **at least `k` pieces "
        "of the same integer length** (leftovers are thrown away; ribbons cannot be joined). "
        "Return the **largest** possible piece length, or `0` if even length 1 does not give "
        "`k` pieces.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` integers.\n\n### Output\nThe largest piece length."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ k ≤ 10^9\n1 ≤ a[i] ≤ 10^9",
    hints=[
        "For a length L, the number of pieces is Σ ⌊a[i] / L⌋. Longer pieces mean fewer of them, so “at least k pieces” is true for small L and false for large L.",
        "You want the **last** L where it is true. Either search with `lo = mid` on success and round `mid` up, or find the first L where it fails and subtract 1.",
        "If Σ a[i] < k, even length 1 fails — return 0. Sum the pieces in a `long`.",
    ],
    opt=("O(n log(max a))", "O(1)",
         "About 30 probes, each an O(n) count."),
    editorial=(
        "## The one thing this teaches\n**The mirror image of minimise-the-answer.** The "
        "predicate now reads `true, true, …, true, false, …` and the answer is the last true. "
        "Same loop, one branch different — and one rounding that is not optional.\n\n"
        "## Approach A: last true, rounding up\n```java\nlong lo = 0, hi = maxA;             // ok(0) is treated as true\n"
        "while (lo < hi) {\n    long mid = lo + (hi - lo + 1) / 2;  // round UP\n"
        "    if (pieces(a, mid) >= k) lo = mid; else hi = mid - 1;\n}\nreturn lo;\n```\n"
        "With a rounded-down `mid`, the range `[4, 5]` gives `mid = 4`; if it succeeds, "
        "`lo = 4` changes nothing and the loop spins forever.\n\n"
        "## Approach B: first false, minus one\nUse the ordinary lower-bound template to find "
        "the smallest L with `pieces(L) < k` in `[1, maxA + 1]`, then return that minus one. "
        "Nothing new to remember, at the price of one subtraction.\n\n"
        "## Why lo starts at 0\nZero is the answer when nothing works, and treating length 0 as "
        "feasible means the loop never has to special-case it — it simply never moves `lo`. "
        "(Do not evaluate `pieces(0)`: `mid` is always ≥ 1 inside the loop because it rounds up.)\n\n"
        "## Overflow\nThe piece count can reach 10⁵ · 10⁹ = 10¹⁴ at L = 1. Use `long`."
    ),
    py='''
def solve(a, k):
    def pieces(L):
        return sum(x // L for x in a)

    lo, hi = 0, max(a)
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2
        if pieces(mid) >= k:
            lo = mid
        else:
            hi = mid - 1
    return lo
''',
    java='''
    static long pieces(int[] a, long L) {
        long c = 0;
        for (int x : a) c += x / L;
        return c;
    }

    static long solve(int[] a, long k) {
        long lo = 0, hi = 0;
        for (int x : a) hi = Math.max(hi, x);
        while (lo < hi) {
            long mid = lo + (hi - lo + 1) / 2;
            if (pieces(a, mid) >= k) lo = mid; else hi = mid - 1;
        }
        return lo;
    }
''',
    examples=[
        ("Example 1", "3 7\n23 9 17\n"),
        ("Example 2", "2 20\n5 6\n"),
    ],
    hidden=[
        ("One ribbon, one piece", "1 1\n1000000000\n"),
        ("Exactly enough at length 1", "3 6\n1 2 3\n"),
        ("Impossible", "2 10\n4 5\n"),
        ("Many pieces", "4 1000000000\n1000000000 1000000000 1000000000 1000000000\n"),
        ("Two-element boundary", "2 3\n10 5\n"),
        ("Uneven", "5 11\n97 3 41 8 60\n"),
    ],
    expl=[
        "Length 6 gives 3 + 1 + 2 = 6 pieces — too few. Length 5 gives 4 + 1 + 3 = 8 ≥ 7.",
        "The ribbons total only 11, so 20 pieces are impossible even at length 1.",
    ],
    prereqs=[
        ("binary_search", "Last-true search: round the midpoint up so `lo = mid` always moves."),
        ("overflow", "The piece count at small L exceeds `int`."),
    ],
)


_p(
    "sqrt-to-six-places", "Square Root to Six Places", "Medium",
    topics=["Binary Search", "Math"], subtopics=["Binary Search", "Integer Scaling", "Precision"],
    companies=["Google", "Microsoft"],
    shape="n", ret="String",
    todo="binary-search the largest integer r with r·r <= n·10^12, then print r / 10^6 with exactly six decimals",
    description=(
        "Print the square root of `n`, **truncated** (not rounded) to exactly six decimal "
        "places.\n\n"
        "Do not use floating point: at six places, a `double` rounding in the wrong direction "
        "changes the last digit on some inputs, and the answer here is judged exactly.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\n`⌊√n · 10⁶⌋ / 10⁶`, written with exactly six "
        "digits after the decimal point."
    ),
    constraints="0 ≤ n ≤ 10^6",
    hints=[
        "√n truncated to six places is ⌊√n · 10⁶⌋ / 10⁶, and ⌊√n · 10⁶⌋ = ⌊√(n · 10¹²)⌋. That is an *integer* square root.",
        "n · 10¹² ≤ 10¹⁸ fits in a long. Binary-search the largest r with r · r ≤ n · 10¹²; r ≤ 10⁹, so r · r ≤ 10¹⁸ never overflows.",
        "Print `r / 1000000`, a dot, and `r % 1000000` padded with zeros to six digits.",
    ],
    opt=("O(log(n · 10¹²))", "O(1)",
         "About 60 probes of one multiplication each."),
    editorial=(
        "## The one thing this teaches\n**A real-valued answer that must be exact is an "
        "integer problem in disguise.** Scale the question until the answer is an integer, "
        "search that, and put the decimal point back when printing.\n\n"
        "## Approach\n```java\nlong target = n * 1_000_000_000_000L;       // n · 10^12 <= 10^18\n"
        "long lo = 0, hi = 1_000_000_000L;             // sqrt(10^18)\n"
        "while (lo < hi) {                             // last r with r*r <= target\n"
        "    long mid = lo + (hi - lo + 1) / 2;\n"
        "    if (mid * mid <= target) lo = mid; else hi = mid - 1;\n}\n"
        "return (lo / 1_000_000) + \".\" + String.format(\"%06d\", lo % 1_000_000);\n```\n\n"
        "## Why not `Math.sqrt`?\n`Math.sqrt` is correctly rounded, but then multiplying by 10⁶ "
        "and truncating introduces a *second* rounding. When √n · 10⁶ lies a hair below an "
        "integer, the product can round up to that integer and the truncation keeps a digit that "
        "is one too high. It happens rarely — which is the worst kind of bug.\n\n"
        "## Why not a double binary search?\nA loop on `hi - lo > 1e-7` has the same double-"
        "rounding problem at the end, and at large magnitudes an epsilon loop may never "
        "terminate. With a fixed 100 iterations it terminates; it is still not exact.\n\n"
        "## Padding\n`r % 10⁶` for √2 is 414213, but √10001 = 100.004999… gives 4999 — "
        "without zero-padding to six digits, `100.4999` would be printed instead of "
        "`100.004999`."
    ),
    py='''
def solve(n):
    target = n * 10**12
    lo, hi = 0, 10**9
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2
        if mid * mid <= target:
            lo = mid
        else:
            hi = mid - 1
    return f"{lo // 10**6}.{lo % 10**6:06d}"
''',
    java='''
    static String solve(long n) {
        long target = n * 1_000_000_000_000L;
        long lo = 0, hi = 1_000_000_000L;
        while (lo < hi) {
            long mid = lo + (hi - lo + 1) / 2;
            if (mid * mid <= target) lo = mid; else hi = mid - 1;
        }
        return (lo / 1_000_000) + "." + String.format("%06d", lo % 1_000_000);
    }
''',
    examples=[
        ("Example 1", "2\n"),
        ("Example 2", "144\n"),
    ],
    hidden=[
        ("Zero", "0\n"),
        ("One", "1\n"),
        ("Leading zeros in the fraction", "10001\n"),
        ("Just below a square", "999999\n"),
        ("Largest n", "1000000\n"),
        ("Three", "3\n"),
        ("Prime", "999983\n"),
    ],
    expl=[
        "√2 = 1.41421356…, truncated to 1.414213 — the 5 is dropped, not rounded up.",
        "144 is a perfect square: 12.000000.",
    ],
    prereqs=[
        ("binary_search", "Last r with r·r ≤ target — an integer square root."),
        ("overflow", "Scale by 10^12 only because n ≤ 10^6 keeps n·10^12 inside a long."),
    ],
)


_p(
    "nth-divisible-number", "The N-th Lucky Number", "Medium",
    topics=["Binary Search", "Math"], subtopics=["Binary Search on the Answer", "Inclusion–Exclusion", "LCM"],
    companies=["Google", "Amazon"],
    shape="three", ret="long",
    todo="count(x) = x/a + x/b − x/lcm(a, b); binary-search the smallest x with count(x) >= N",
    description=(
        "A positive integer is **lucky** if it is divisible by `a` or by `b` (or both). "
        "Return the `N`-th lucky number, counting from 1.\n\n"
        "### Input\nOne line: `N a b`.\n\n### Output\nThe `N`-th lucky number."
    ),
    constraints="1 ≤ N ≤ 10^9\n1 ≤ a, b ≤ 40000",
    hints=[
        "Generating lucky numbers one by one is O(N) — 10⁹. Instead ask: how many lucky numbers are ≤ x?",
        "Multiples of a up to x: ⌊x/a⌋. Of b: ⌊x/b⌋. Numbers divisible by both were counted twice — they are the multiples of lcm(a, b). So count(x) = ⌊x/a⌋ + ⌊x/b⌋ − ⌊x/lcm⌋.",
        "count(x) never decreases, so the N-th lucky number is the smallest x with count(x) ≥ N. Search x in [1, N · min(a, b)].",
    ],
    opt=("O(log(N · min(a, b)))", "O(1)",
         "A gcd, then about 46 probes of an O(1) count."),
    editorial=(
        "## The one thing this teaches\n**When you cannot list the candidates, count them.** "
        "The k-th element of any sorted set is the smallest x whose count(≤ x) reaches k — "
        "lower bound over values instead of indices. The whole problem is writing count(x).\n\n"
        "## count(x) by inclusion–exclusion\n```java\nlong g = gcd(a, b), l = a / g * b;          // lcm, divide first\n"
        "long count(long x) { return x / a + x / b - x / l; }\n```\n"
        "Numbers divisible by both are counted in both terms, so subtract them once. They are "
        "exactly the multiples of the **lcm** — not of a · b, which is only right when a and b "
        "are coprime.\n\n"
        "## The search\n```java\nlong lo = 1, hi = N * Math.min(a, b);\n"
        "while (lo < hi) {\n    long mid = lo + (hi - lo) / 2;\n"
        "    if (count(mid) >= N) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n```\n"
        "`hi` is safe because the multiples of the smaller of a and b alone reach N by then.\n\n"
        "## Why the answer is lucky\nThe loop never checks that `lo` is divisible by a or b. It "
        "does not need to: count jumps only at lucky numbers, so the smallest x where count "
        "first reaches N is where the N-th lucky number sits. Stopping early on `count(mid) == N` "
        "would be the bug — mid could be any of the unlucky numbers after it.\n\n"
        "## Overflow\n`a / g * b`, not `a * b / g` — the latter overflows nothing here (4·10⁴ "
        "squared is small), but it is the habit that matters when a and b reach 10⁹."
    ),
    py='''
def solve(N, a, b):
    from math import gcd
    l = a // gcd(a, b) * b

    def count(x):
        return x // a + x // b - x // l

    lo, hi = 1, N * min(a, b)
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= N:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }

    static long solve(long N, long a, long b) {
        long l = a / gcd(a, b) * b;
        long lo = 1, hi = N * Math.min(a, b);
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            long c = mid / a + mid / b - mid / l;
            if (c >= N) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[
        ("Example 1", "7 4 6\n"),
        ("Example 2", "5 3 3\n"),
    ],
    hidden=[
        ("First one", "1 7 5\n"),
        ("a divides b", "10 2 8\n"),
        ("Coprime", "100 7 11\n"),
        ("Largest N", "1000000000 40000 39999\n"),
        ("One and anything", "1000000000 1 40000\n"),
        ("Shared factor", "123456789 12 18\n"),
    ],
    expl=[
        "Lucky numbers: 4, 6, 8, 12, 16, 18, 20, … — 12 counts once even though both divide it. The 7th is 20.",
        "a and b are equal, so lucky means “multiple of 3”: the 5th is 15.",
    ],
    prereqs=[
        ("binary_search", "The N-th lucky number is the smallest x with count(x) ≥ N."),
        ("number_theory", "lcm(a, b) = a / gcd(a, b) · b counts the numbers divisible by both."),
    ],
)


_p(
    "kth-in-multiplication-table", "K-th Entry of the Times Table", "Hard",
    topics=["Binary Search"], subtopics=["Binary Search on Values", "Counting"],
    companies=["Google", "Uber"],
    shape="three", ret="long",
    todo="count(x) = sum over rows i of min(m, x / i); binary-search the smallest x with count(x) >= k",
    description=(
        "An `n × m` multiplication table has `i · j` in row `i`, column `j` (both 1-based). "
        "Write all `n · m` entries in non-decreasing order; return the `k`-th one.\n\n"
        "### Input\nOne line: `n m k`.\n\n### Output\nThe `k`-th smallest entry."
    ),
    constraints="1 ≤ n, m ≤ 100000\n1 ≤ k ≤ n · m",
    hints=[
        "The table has up to 10¹⁰ entries — you cannot build it, let alone sort it. But for a value x, you can count the entries ≤ x without building anything.",
        "Row i holds i, 2i, …, mi. The entries ≤ x in that row are the first ⌊x / i⌋ of them, capped at m. So count(x) = Σ min(m, ⌊x / i⌋) over the n rows.",
        "Binary-search the smallest x in [1, n·m] with count(x) ≥ k. Iterate rows over the smaller of n and m for speed.",
    ],
    opt=("O(min(n, m) · log(n · m))", "O(1)",
         "About 34 probes, each an O(min(n, m)) count."),
    editorial=(
        "## The one thing this teaches\n**Binary search over the value space, with a counting "
        "oracle.** The k-th smallest of anything is the smallest x such that at least k "
        "elements are ≤ x. If counting is cheap, the elements never need to exist.\n\n"
        "## Counting one row\nRow i is i·1, i·2, …, i·m — an arithmetic sequence. The entries "
        "≤ x are those with j ≤ x / i, so there are `min(m, x / i)` of them. Summing over rows is "
        "O(n); swapping n and m first (the table is symmetric) makes it O(min(n, m)).\n\n"
        "## The search\n```java\nlong lo = 1, hi = (long) n * m;\nwhile (lo < hi) {\n"
        "    long mid = lo + (hi - lo) / 2, c = 0;\n"
        "    for (long i = 1; i <= n; i++) c += Math.min(m, mid / i);\n"
        "    if (c >= k) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n```\n\n"
        "## Why the result is in the table\nNot every integer in [1, n·m] is a product i·j "
        "(e.g. a prime larger than both n and m). The count only increases at values that *are* "
        "entries, so the smallest x whose count reaches k is always an entry. This is why "
        "`>= k` with convergence is correct and stopping at `== k` is not.\n\n"
        "## Same family\n*k-th smallest pair distance* (count pairs ≤ d with two pointers), "
        "*k-th smallest in a sorted matrix* (count by walking the staircase), *k-th smallest "
        "prime fraction* — each is this loop with a different count(x)."
    ),
    py='''
def solve(n, m, k):
    if n > m:
        n, m = m, n
    lo, hi = 1, n * m
    while lo < hi:
        mid = (lo + hi) // 2
        c = 0
        for i in range(1, n + 1):
            c += min(m, mid // i)
        if c >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long solve(long n, long m, long k) {
        if (n > m) { long t = n; n = m; m = t; }
        long lo = 1, hi = n * m;
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2, c = 0;
            for (long i = 1; i <= n; i++) c += Math.min(m, mid / i);
            if (c >= k) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[
        ("Example 1", "3 4 7\n"),
        ("Example 2", "2 5 10\n"),
    ],
    hidden=[
        ("One cell", "1 1 1\n"),
        ("One row", "1 100000 77777\n"),
        ("One column", "100000 1 99999\n"),
        ("First entry", "100000 100000 1\n"),
        ("Last entry", "100000 100000 10000000000\n"),
        ("Middle of a big table", "100000 99999 4999950000\n"),
        ("Small, checkable", "5 5 13\n"),
    ],
    expl=[
        "Sorted entries: 1 2 2 3 3 4 4 6 6 8 9 12. The 7th is 4.",
        "The last of ten entries is the largest, 2 · 5 = 10.",
    ],
    prereqs=[
        ("binary_search", "Search the value x; the predicate is count(x) ≥ k."),
        ("math_digits", "Row i contributes min(m, ⌊x / i⌋) entries ≤ x."),
    ],
)
