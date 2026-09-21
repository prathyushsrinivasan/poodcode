# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 49 — Order & Search, round 2.
#
#   sierpinski-cell        recursion on quadrants — and the bit trick it proves
#   count-range-sums       merge-count over prefix sums, with a sliding window
#   min-max-after-splits   minimise the maximum: the answer is a cap
#   covered-by-two         a sweep that measures length, not a peak
#   patch-to-cover-range   greedy reach over sums: "everything below miss is buildable"
#
# Uses the `three` / `pairs_xy` shapes from dsa_more_46.py.
# ===========================================================================


_p(
    "sierpinski-cell", "Is the Cell Painted?", "Medium",
    topics=["Recursion"], subtopics=["Recursion", "Divide and Conquer", "Fractals"],
    companies=["Google", "Microsoft"],
    shape="pairs_k", ret="String",
    todo="halve the grid: a cell in the bottom-right quadrant is blank; otherwise recurse on (r mod half, c mod half)",
    description=(
        "An order-`k` pattern is a `2^k × 2^k` grid built like this:\n\n"
        "- Order 0 is a single painted cell.\n"
        "- Order `k` is four quadrants of size `2^(k−1)`: the **top-left, top-right and "
        "bottom-left** quadrants are each a copy of the order-`(k−1)` pattern, and the "
        "**bottom-right** quadrant is entirely blank.\n\n"
        "Answer `q` questions: is cell `(r, c)` painted? Rows and columns are 0-based from the "
        "top-left.\n\n"
        "### Input\nLine 1: `q k`.\nNext `q` lines: `r c`.\n\n### Output\nOne line per "
        "question: `1` if painted, `0` if blank."
    ),
    constraints="1 ≤ q ≤ 100000\n0 ≤ k ≤ 30\n0 ≤ r, c < 2^k",
    hints=[
        "The grid can be 2³⁰ wide — never build it. Describe cell (r, c) of order k in terms of a cell of order k − 1.",
        "Let half = 2^(k−1). If r ≥ half and c ≥ half, the cell is in the blank quadrant. Otherwise it lies in a copy of the smaller pattern, at (r mod half, c mod half).",
        "Base case: order 0 is painted. Each call halves the grid, so a question costs at most k + 1 calls.",
    ],
    opt=("O(q · k)", "O(k) stack",
         "At most k + 1 halving calls per question."),
    editorial=(
        "## The one thing this teaches\n**Recursion on the structure's own definition.** The "
        "pattern is *defined* recursively, so the question about it is answered by the same "
        "recursion: find which quadrant the cell is in, and ask the smaller pattern.\n\n"
        "## Approach\n```java\nstatic boolean painted(int k, long r, long c) {\n"
        "    if (k == 0) return true;\n    long half = 1L << (k - 1);\n"
        "    if (r >= half && c >= half) return false;         // the blank quadrant\n"
        "    return painted(k - 1, r % half, c % half);         // a copy of order k − 1\n}\n```\n\n"
        "## The promise\n*`painted(k, r, c)` says whether (r, c) is painted in the order-k "
        "pattern.* For k = 0 that is true by definition. For larger k, three quadrants are "
        "copies of order k − 1 — so trust the call — and the fourth is blank.\n\n"
        "## What the recursion proves\nEach level looks at one bit of r and one bit of c — the "
        "bit worth `half` — and fails only when *both* are 1. So the cell is painted exactly "
        "when r and c share no set bit: **`(r & c) == 0`**. This is the Sierpinski triangle, "
        "and it is Pascal's triangle mod 2 (Lucas' theorem). The one-line answer is correct; "
        "the recursion is how you would find it — and how you would convince an interviewer "
        "it is right.\n\n"
        "## Cost\nk + 1 calls per question, depth ≤ 31. Recursion depth is never a concern "
        "when every call halves the input."
    ),
    py='''
def solve(p, k):
    def painted(k, r, c):
        while k > 0:
            half = 1 << (k - 1)
            if r >= half and c >= half:
                return False
            r, c, k = r % half, c % half, k - 1
        return True
    return "\\n".join("1" if painted(k, r, c) else "0" for r, c in p)
''',
    java='''
    static boolean painted(int k, long r, long c) {
        if (k == 0) return true;
        long half = 1L << (k - 1);
        if (r >= half && c >= half) return false;
        return painted(k - 1, r % half, c % half);
    }

    static String solve(int[][] p, int k) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < p.length; i++) {
            if (i > 0) sb.append('\\n');
            sb.append(painted(k, p[i][0], p[i][1]) ? '1' : '0');
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4 2\n0 0\n1 1\n3 1\n2 3\n"),
        ("Example 2", "3 0\n0 0\n0 0\n0 0\n"),
    ],
    hidden=[
        ("Order 1, all four cells", "4 1\n0 0\n0 1\n1 0\n1 1\n"),
        ("Order 3 diagonal", "8 3\n0 0\n1 1\n2 2\n3 3\n4 4\n5 5\n6 6\n7 7\n"),
        ("Order 3 first column and row", "4 3\n7 0\n0 7\n5 2\n6 1\n"),
        ("Order 30 corners", "4 30\n0 0\n1073741823 0\n0 1073741823\n1073741823 1073741823\n"),
        ("Order 30 deep cells", "3 30\n536870912 0\n536870912 536870911\n715827882 357913941\n"),
    ],
    expl=[
        "Order 2 is 4 × 4. (0, 0) is painted. (1, 1) is the blank corner of the top-left copy, (3, 1) the blank corner of the bottom-left copy, and (2, 3) lies in the blank bottom-right quadrant.",
        "Order 0 is a single painted cell.",
    ],
    prereqs=[
        ("recursion", "The pattern is defined recursively, so the query recurses the same way."),
        ("bit_manip", "Each level examines one bit of r and c; the result is (r & c) == 0."),
    ],
)


_p(
    "count-range-sums", "Subarrays Within Bounds", "Hard",
    topics=["Sorting", "Divide and Conquer"], subtopics=["Merge Sort", "Prefix Sums", "Counting Pairs"],
    companies=["Google", "Amazon"],
    shape="arr_xy", ret="long",
    todo="prefix sums P; count pairs i < j with lo <= P[j] - P[i] <= hi by merge sort over P, using two window pointers per left element",
    description=(
        "Count the **non-empty contiguous subarrays** whose sum lies in `[lo, hi]` "
        "(inclusive).\n\n"
        "### Input\nLine 1: `n lo hi`.\nLine 2: `n` integers.\n\n### Output\nThe number of such subarrays."
    ),
    constraints="1 ≤ n ≤ 100000\n-10^9 ≤ a[i] ≤ 10^9\n-10^14 ≤ lo ≤ hi ≤ 10^14",
    hints=[
        "A subarray sum is a difference of prefix sums: sum(i..j−1) = P[j] − P[i] with P[0] = 0. So you are counting pairs i < j with lo ≤ P[j] − P[i] ≤ hi.",
        "Negative values mean no sliding window. But “pairs i < j with a condition” is merge sort's counting shape — run it on P.",
        "When both halves of P are sorted, for each P[i] in the left half the valid P[j] in the right half form a *contiguous window*: those in [P[i] + lo, P[i] + hi]. As P[i] increases the window only moves right — two pointers, O(n) per level.",
    ],
    opt=("O(n log n)", "O(n)",
         "Merge sort over n + 1 prefix sums, with a linear two-pointer count before each merge."),
    editorial=(
        "## The one thing this teaches\n**Merge-counting applies to anything you can phrase "
        "as pairs i < j.** Subarrays are pairs of prefix sums, so “count subarrays with a sum "
        "condition” becomes “count pairs of prefix sums with a difference condition” — and "
        "the condition is a *range*, so the count per element is a window, not a single "
        "pointer.\n\n"
        "## Reduction\nP[0] = 0, P[j] = a[0] + … + a[j−1]. Subarray a[i..j−1] has sum "
        "P[j] − P[i]. Count pairs 0 ≤ i < j ≤ n with lo ≤ P[j] − P[i] ≤ hi.\n\n"
        "## The crossing count\nBoth halves sorted. For each P[i] on the left, the valid P[j] "
        "on the right satisfy P[i] + lo ≤ P[j] ≤ P[i] + hi — a contiguous run in the sorted "
        "right half, `[start, end)`:\n\n```java\nint start = mid, end = mid;\n"
        "for (int i = lo; i < mid; i++) {\n"
        "    while (start < hi && P[start] - P[i] < LOW)  start++;\n"
        "    while (end   < hi && P[end]   - P[i] <= HIGH) end++;\n"
        "    count += end - start;\n}\n// then merge the halves as usual\n```\n"
        "Because the left half is increasing, both pointers only move forward.\n\n"
        "## Why not a sliding window?\nWindows need sums that grow when the window grows. "
        "With negative numbers they do not, so no pointer rule is valid. Prefix sums plus a "
        "sort are what restore an order to exploit.\n\n"
        "## Magnitudes\nPrefix sums reach 10¹⁴ and the count reaches n(n+1)/2 ≈ 5·10⁹: `long` "
        "for both.\n\n"
        "## Alternatives\nA Fenwick tree over compressed prefix sums (count earlier P[i] in "
        "[P[j] − hi, P[j] − lo]) is the same complexity with more machinery."
    ),
    py='''
def solve(a, x, y):
    P = [0]
    for v in a:
        P.append(P[-1] + v)
    buf = [0] * len(P)

    def rec(lo, hi):
        if hi - lo < 2:
            return 0
        mid = (lo + hi) // 2
        c = rec(lo, mid) + rec(mid, hi)
        s = e = mid
        for i in range(lo, mid):
            while s < hi and P[s] - P[i] < x:
                s += 1
            while e < hi and P[e] - P[i] <= y:
                e += 1
            c += e - s
        P[lo:hi] = sorted(P[lo:hi])
        return c

    return rec(0, len(P))
''',
    java='''
    static long[] P, buf;
    static long LOW, HIGH;

    static long rec(int lo, int hi) {
        if (hi - lo < 2) return 0;
        int mid = (lo + hi) >>> 1;
        long c = rec(lo, mid) + rec(mid, hi);
        int s = mid, e = mid;
        for (int i = lo; i < mid; i++) {
            while (s < hi && P[s] - P[i] < LOW) s++;
            while (e < hi && P[e] - P[i] <= HIGH) e++;
            c += e - s;
        }
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi) buf[k++] = P[i] <= P[j] ? P[i++] : P[j++];
        while (i < mid) buf[k++] = P[i++];
        while (j < hi) buf[k++] = P[j++];
        System.arraycopy(buf, lo, P, lo, hi - lo);
        return c;
    }

    static long solve(int[] a, long x, long y) {
        int n = a.length;
        P = new long[n + 1];
        for (int i = 0; i < n; i++) P[i + 1] = P[i] + a[i];
        buf = new long[n + 1];
        LOW = x; HIGH = y;
        return rec(0, n + 1);
    }
''',
    examples=[
        ("Example 1", "5 2 4\n3 -1 2 -4 5\n"),
        ("Example 2", "3 0 0\n0 0 0\n"),
    ],
    hidden=[
        ("One element inside", "1 -5 5\n3\n"),
        ("One element outside", "1 4 10\n3\n"),
        ("All negative", "4 -6 -3\n-2 -3 -1 -4\n"),
        ("Wide bounds count everything", "5 -100000000000000 100000000000000\n1 -1 1 -1 1\n"),
        ("Large values", "4 1000000000 3000000000\n1000000000 1000000000 -1000000000 1000000000\n"),
        ("Mixed", "8 -2 3\n4 -7 2 2 -1 5 -3 1\n"),
        ("2000 random values", "2000 -500 500\n" + " ".join(str(v) for v in _lcg_ints(88, 2000, -100, 100)) + "\n"),
    ],
    expl=[
        "Six subarrays qualify: [3] = 3, [3, −1] = 2, [3, −1, 2] = 4, [−1, 2, −4, 5] = 2, [2] = 2 and [2, −4, 5] = 3.",
        "All six subarrays sum to 0.",
    ],
    prereqs=[
        ("prefix_sum", "Every subarray sum is a difference of two prefix sums."),
        ("sorting", "Merge sort over the prefix sums counts the crossing pairs."),
        ("two_pointers", "The valid window in the right half only moves forward."),
    ],
)


_p(
    "min-max-after-splits", "Lighten the Heaviest Crate", "Medium",
    topics=["Binary Search"], subtopics=["Binary Search on the Answer", "Minimise the Maximum"],
    companies=["Amazon", "Google"],
    shape="arr_k", ret="long",
    todo="binary-search the cap x; a crate of weight w needs (w - 1) / x splits to get every piece <= x",
    description=(
        "Crates hold `a[i]` kilograms of sand. In one operation you split one crate into two "
        "crates with positive integer weights that add up to the original. You may perform "
        "**at most `k` operations**. Return the **smallest possible weight of the heaviest "
        "crate** afterwards.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` weights.\n\n### Output\nThe minimum achievable "
        "maximum weight."
    ),
    constraints="1 ≤ n ≤ 100000\n0 ≤ k ≤ 10^9\n1 ≤ a[i] ≤ 10^9",
    hints=[
        "Deciding *how* to split is hard. Deciding whether a cap x is achievable is easy: how many splits does it take to bring every crate down to x or less?",
        "A crate of weight w needs ⌈w / x⌉ pieces, which is ⌈w / x⌉ − 1 = (w − 1) / x splits (integer division). Sum over crates; x is achievable iff the total ≤ k.",
        "A larger cap never needs more splits, so the achievable caps form a suffix: binary-search the first one, in [1, max(a)].",
    ],
    opt=("O(n log(max a))", "O(1)",
         "About 30 probes, each an O(n) count."),
    editorial=(
        "## The one thing this teaches\n**Minimise the maximum = search the cap.** The "
        "question “what is the best final maximum?” has no direct construction, but “can "
        "every crate end up ≤ x?” is one division per crate — and it is monotone in x.\n\n"
        "## The check\nA crate of weight w must become ⌈w / x⌉ pieces, which costs one split "
        "fewer than that: `(w - 1) / x`. (Check: w = x needs 0 splits, w = x + 1 needs 1.) "
        "Splitting evenly is never worse than any other split, so this count is exact.\n\n"
        "## The search\n```java\nlong lo = 1, hi = max;\nwhile (lo < hi) {\n"
        "    long mid = lo + (hi - lo) / 2, ops = 0;\n"
        "    for (int w : a) ops += (w - 1) / mid;\n"
        "    if (ops <= k) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n```\n\n"
        "## Why not a heap?\n“Always split the heaviest crate in half” is the tempting greedy, "
        "and it is wrong: 9 with k = 2 halves to 5 + 4, then 5 → 3 + 2, leaving max 4; but "
        "splitting 9 into 3 + 3 + 3 reaches 3. The right split of a crate depends on how many "
        "splits it will eventually get — which is exactly what the cap decides.\n\n"
        "## Overflow\nThe op count can reach 10⁵ · 10⁹ = 10¹⁴ at x = 1. `long`."
    ),
    py='''
def solve(a, k):
    lo, hi = 1, max(a)
    while lo < hi:
        mid = (lo + hi) // 2
        ops = sum((w - 1) // mid for w in a)
        if ops <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long solve(int[] a, long k) {
        long lo = 1, hi = 0;
        for (int w : a) hi = Math.max(hi, w);
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2, ops = 0;
            for (int w : a) ops += (w - 1) / mid;
            if (ops <= k) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[
        ("Example 1", "1 2\n9\n"),
        ("Example 2", "3 4\n7 17 3\n"),
    ],
    hidden=[
        ("No operations", "3 0\n4 8 2\n"),
        ("Plenty of operations", "2 1000000000\n1000000000 1000000000\n"),
        ("All ones", "4 10\n1 1 1 1\n"),
        ("One huge crate", "1 999999999\n1000000000\n"),
        ("Mixed", "6 7\n12 5 30 1 9 16\n"),
    ],
    expl=[
        "Split 9 into 3 + 6, then 6 into 3 + 3: the heaviest is 3. Halving greedily (5 + 4, then 5 → 3 + 2) leaves a 4.",
        "Cap 5 needs 1 + 3 + 0 = 4 splits (7 → 2 pieces, 17 → 4 pieces). Cap 4 would need 1 + 4 + 0 = 5.",
    ],
    prereqs=[
        ("binary_search", "Minimise the maximum by searching the cap."),
        ("overflow", "The split count at small caps exceeds `int`."),
    ],
)


_p(
    "covered-by-two", "Double-Booked Minutes", "Medium",
    topics=["Intervals", "Sorting"], subtopics=["Sweep Line", "Coverage"],
    companies=["Google", "Uber"],
    shape="pairs", ret="long",
    todo="sweep ±1 events in time order; add (next time − this time) to the answer whenever at least two bookings are active",
    description=(
        "A room has `n` bookings, each `[s, e)`. Return the total length of time during "
        "which **at least two** bookings are active at once.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `s e`.\n\n### Output\nThe total double-booked length."
    ),
    constraints="1 ≤ n ≤ 200000\n0 ≤ s < e ≤ 10^9",
    hints=[
        "Merging cannot answer this — it forgets how many bookings overlapped. Keep a count instead.",
        "Events: +1 at each start, −1 at each end. Between two consecutive event times the count is constant.",
        "Sort events by time. After processing all events at time t, if the count is ≥ 2, the stretch from t to the next event time is double-booked: add its length.",
    ],
    opt=("O(n log n)", "O(n)",
         "Sort 2n events, then one pass adding stretch lengths."),
    editorial=(
        "## The one thing this teaches\n**A sweep measures lengths, not just peaks.** "
        "The count between two consecutive events is constant, so every “how long was it "
        "at least k” question is: sort the events, and add each gap whose count qualifies.\n\n"
        "## Approach\n```java\nlong[] ev = ...;          // time * 2 + (start ? 1 : 0); ends sort first\nArrays.sort(ev);\n"
        "long total = 0; int cur = 0;\nfor (int i = 0; i < ev.length; i++) {\n"
        "    cur += (ev[i] & 1) == 1 ? 1 : -1;\n"
        "    if (i + 1 < ev.length && cur >= 2) total += ev[i + 1] / 2 - ev[i] / 2;\n}\n```\n"
        "Gaps between two events at the *same* time are zero, so the order among ties does "
        "not change the total here — unlike the peak, where it does.\n\n"
        "## Generalising\nReplace `cur >= 2` by `cur >= 1` and this is the union length; by "
        "`cur == n` it is the common intersection; by `cur >= k` it is “covered by at least k”. "
        "One loop, four questions.\n\n"
        "## Magnitude\nThe answer is at most 10⁹, but keep it `long` — sums of gaps are the "
        "classic place an `int` quietly wraps when the bounds grow."
    ),
    py='''
def solve(p):
    ev = []
    for s, e in p:
        ev.append((s, 1))
        ev.append((e, -1))
    ev.sort()
    total = cur = 0
    for i, (t, d) in enumerate(ev):
        cur += d
        if i + 1 < len(ev) and cur >= 2:
            total += ev[i + 1][0] - t
    return total
''',
    java='''
    static long solve(int[][] p) {
        int n = p.length;
        long[] ev = new long[2 * n];
        for (int i = 0; i < n; i++) {
            ev[2 * i] = (long) p[i][0] * 2 + 1;
            ev[2 * i + 1] = (long) p[i][1] * 2;
        }
        Arrays.sort(ev);
        long total = 0;
        int cur = 0;
        for (int i = 0; i < ev.length; i++) {
            cur += (ev[i] & 1) == 1 ? 1 : -1;
            if (i + 1 < ev.length && cur >= 2) total += ev[i + 1] / 2 - ev[i] / 2;
        }
        return total;
    }
''',
    examples=[
        ("Example 1", "4\n1 8\n3 5\n4 10\n12 14\n"),
        ("Example 2", "3\n0 5\n5 10\n10 15\n"),
    ],
    hidden=[
        ("One booking", "1\n0 1000000000\n"),
        ("Identical", "3\n2 9\n2 9\n2 9\n"),
        ("Nested", "3\n0 100\n10 20\n50 60\n"),
        ("Chain of overlaps", "5\n0 4\n3 7\n6 10\n9 13\n12 16\n"),
        ("Large", "2\n0 1000000000\n1 1000000000\n"),
    ],
    expl=[
        "[1, 8) and [3, 5) overlap on [3, 5); [1, 8) and [4, 10) on [4, 8). Together that is [3, 8): length 5.",
        "The bookings only touch, so nothing is ever double-booked.",
    ],
    prereqs=[
        ("intervals", "A ±1 sweep: the active count is constant between events."),
        ("sorting", "Events are processed in time order."),
    ],
)


_p(
    "patch-to-cover-range", "Coins to Pay Any Amount", "Hard",
    topics=["Greedy"], subtopics=["Greedy", "Reachable Sums"],
    companies=["Google", "Amazon"],
    shape="arr_k", ret="long",
    todo="keep miss = smallest amount not yet payable (start 1); use a coin <= miss to extend, else add a coin worth miss",
    description=(
        "You hold coins with values `c[0..n-1]`, given in **non-decreasing** order. You want "
        "to be able to pay **every** amount from 1 to `m` exactly, using each coin at most "
        "once. Return the **fewest extra coins** (of any values you choose) you must add.\n\n"
        "### Input\nLine 1: `n m`.\nLine 2: `n` coin values, sorted (the line may be empty "
        "when n = 0).\n\n### Output\nThe minimum number of coins to add."
    ),
    constraints="0 ≤ n ≤ 100000\n1 ≤ c[i] ≤ 10^9\n1 ≤ m ≤ 2·10^9",
    hints=[
        "Suppose every amount in [1, miss) is payable with the coins used so far. What does one more coin of value v do to that range?",
        "If v ≤ miss, every amount in [1, miss + v) becomes payable — add v to each old amount. If v > miss, the amount miss is impossible with any remaining coin, since they are all larger.",
        "So: while miss ≤ m, use the next coin if it is ≤ miss; otherwise add a coin worth exactly `miss`, which doubles the range. Keep miss in a `long`.",
    ],
    opt=("O(n + log m)", "O(1)",
         "Each coin is used once, and each added coin at least doubles the payable range."),
    editorial=(
        "## The one thing this teaches\n**A greedy whose state is a whole range.** The "
        "invariant is *every amount in [1, miss) is payable* — a prefix of the integers, "
        "summarised by one number, like jump game's reach.\n\n"
        "## Why a coin ≤ miss extends the range to miss + v\nFor any target t in [miss, miss + v), "
        "t − v is in [0, miss) and already payable without this coin; add the coin. So the "
        "prefix grows to [1, miss + v).\n\n"
        "## Why the added coin should be exactly miss\nThe amount `miss` must be paid "
        "somehow. Every remaining coin is > miss, so the new coin must be ≤ miss — and among "
        "those, the largest (miss itself) extends the range furthest, to [1, 2·miss). A "
        "stays-ahead argument: no other choice reaches further.\n\n"
        "## Approach\n```java\nlong miss = 1; int i = 0; long added = 0;\n"
        "while (miss <= m) {\n    if (i < n && c[i] <= miss) miss += c[i++];\n"
        "    else { miss += miss; added++; }\n}\nreturn added;\n```\n\n"
        "## Overflow\nmiss can pass m ≈ 2·10⁹ before the loop ends — beyond `int`. `long`.\n\n"
        "## Cost\nEach coin is consumed once; each patch doubles miss, so there are at most "
        "log₂ m ≈ 31 patches."
    ),
    py='''
def solve(a, k):
    miss, i, added = 1, 0, 0
    while miss <= k:
        if i < len(a) and a[i] <= miss:
            miss += a[i]
            i += 1
        else:
            miss += miss
            added += 1
    return added
''',
    java='''
    static long solve(int[] a, long m) {
        long miss = 1, added = 0;
        int i = 0;
        while (miss <= m) {
            if (i < a.length && a[i] <= miss) miss += a[i++];
            else { miss += miss; added++; }
        }
        return added;
    }
''',
    examples=[
        ("Example 1", "2 10\n1 5\n"),
        ("Example 2", "4 20\n1 2 3 8\n"),
    ],
    hidden=[
        ("No coins", "0 7\n\n"),
        ("Already enough", "3 6\n1 2 3\n"),
        ("Starts too high", "2 50\n4 9\n"),
        ("Largest m, no coins", "0 2000000000\n\n"),
        ("Many ones", "6 6\n1 1 1 1 1 1\n"),
        ("Big coins", "3 2000000000\n1 1000000000 1000000000\n"),
    ],
    expl=[
        "1 covers [1, 1]. 5 is too big for miss = 2, so add a 2 (now [1, 3]) and a 4 (now [1, 7]); then 5 extends to [1, 12]. Two coins added.",
        "1, 2, 3 cover [1, 6]; 8 is too big for miss = 7, so add a 7 (now [1, 13]); 8 extends to [1, 21]. One coin added.",
    ],
    prereqs=[
        ("greedy", "Invariant: every amount below miss is payable; stays-ahead for the patch."),
        ("overflow", "miss passes 2·10^9 before the loop stops."),
    ],
)
