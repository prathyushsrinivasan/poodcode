# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 41 — the DP families stage 7 never reaches.
#
#   count-digit-free-numbers   digit DP: the state is (position, still tight)
#   digit-sum-divisible-count  digit DP with a carried residue
#   min-cost-jump-window       an O(n*k) recurrence made O(n) by a monotonic deque
#   subset-sum-closest-below   meet in the middle: 2^40 -> 2 * 2^20
#
# Stage 7 teaches DP over indices, capacities, grids, pairs of sequences,
# intervals and state machines. What it never does is change the *shape* of the
# state (digits instead of items) or attack the constant factor of the
# transition, which is what these four are for.
# ===========================================================================

_p(
    "count-digit-free-numbers", "Numbers Without a Seven", "Easy",
    topics=["Dynamic Programming", "Math"], subtopics=["Digit DP", "Counting"],
    companies=["Google", "Amazon"],
    shape="n", ret="long",
    todo="walk the digits of N left to right; at each position count the digits below the current one freely, then continue along the prefix that matches N",
    description=(
        "A hotel skips every room number containing the digit `7`. Given `N`, count how many "
        "integers from `1` to `N` inclusive do **not** contain the digit `7` anywhere in their "
        "decimal form.\n\n"
        "### Input\nOne line: `N`.\n\n"
        "### Output\nThe count."
    ),
    constraints="1 ≤ N ≤ 10^18",
    hints=[
        "Looping to N is impossible at 10¹⁸ — the answer has to be built from the *digits* of N, of which there are at most 19.",
        "Go left to right over the digits of N, tracking one bit of state: is the prefix built so far still exactly equal to N's prefix (“tight”), or already strictly below it?",
        "Once you are strictly below, every remaining position is free: 9 choices each (0-9 without 7). So the whole answer is a sum of 9^(remaining) terms, one per position where you first go below N.",
    ],
    opt=("O(D · 10)", "O(D)",
         "D ≤ 19 digits, ten choices at each — constant, whatever N is."),
    editorial=(
        "## The one thing this teaches\n**When the bound is a number rather than a count, the DP "
        "runs over its digits.** 10¹⁸ candidates become 19 positions, and the only state "
        "worth carrying is whether you are still hugging the bound.\n\n"
        "## The state\n`(position, tight)`. `tight` means every digit chosen so far equals N's, "
        "so the next digit is capped at N's digit; otherwise it is capped at 9. The moment you "
        "pick something smaller, `tight` is false forever after — and that is the whole point, "
        "because from then on the count is a clean power.\n\n"
        "## Approach\n```java\nchar[] s = Long.toString(N).toCharArray();\n"
        "long[] pow9 = new long[s.length + 1];\npow9[0] = 1;\n"
        "for (int i = 1; i <= s.length; i++) pow9[i] = pow9[i - 1] * 9;\n\n"
        "long count = 0;                       // counts 0 .. N, subtract the 0 at the end\n"
        "for (int i = 0; i < s.length; i++) {\n    int cap = s[i] - '0';\n"
        "    for (int d = 0; d < cap; d++)     // first position that goes strictly below N\n"
        "        if (d != 7) count += pow9[s.length - i - 1];\n"
        "    if (cap == 7) return count;       // N's own prefix is dead; nothing stays tight\n"
        "}\nreturn count + 1 - 1;               // + 1 for N itself, - 1 for the number 0\n```\n\n"
        "## Why the loop can return early\nIf N's own digit is a 7, no number can match N's "
        "prefix that far and still be legal, so the tight branch dies and everything already "
        "counted is the answer.\n\n"
        "## Leading zeros\nThey are harmless here: a leading zero is not a 7, so counting "
        "`0 … N` and subtracting the single number 0 is exact. A problem about *increasing* "
        "digits, or about the number of digits, needs a third piece of state — `started` — "
        "to tell a leading zero from a real one.\n\n"
        "## The other way to see it\nThis particular problem is also base conversion: the "
        "legal numbers, in order, are exactly the base-9 numbers with 7 and 8 remapped. Digit DP "
        "is the version that survives the question getting harder — as it does in the next "
        "problem."
    ),
    py='''
def solve(n):
    s = str(int(n))
    L = len(s)
    pow9 = [1] * (L + 1)
    for i in range(1, L + 1):
        pow9[i] = pow9[i - 1] * 9
    count = 0
    tight = True
    for i, ch in enumerate(s):
        cap = int(ch)
        for d in range(cap):
            if d != 7:
                count += pow9[L - i - 1]
        if cap == 7:
            tight = False
            break
    if tight:
        count += 1
    return count - 1
''',
    java='''
    static long solve(long n) {
        char[] s = Long.toString(n).toCharArray();
        int L = s.length;
        long[] pow9 = new long[L + 1];
        pow9[0] = 1;
        for (int i = 1; i <= L; i++) pow9[i] = pow9[i - 1] * 9;
        long count = 0;
        boolean tight = true;
        for (int i = 0; i < L; i++) {
            int cap = s[i] - '0';
            for (int d = 0; d < cap; d++)
                if (d != 7) count += pow9[L - i - 1];
            if (cap == 7) { tight = false; break; }
        }
        if (tight) count++;
        return count - 1;
    }
''',
    examples=[("Example 1", "20\n"), ("Example 2", "77\n")],
    hidden=[
        ("The smallest input", "1\n"),
        ("Just below a seven", "6\n"),
        ("Exactly seven", "7\n"),
        ("A round power of ten", "1000\n"),
        ("Sevens in the middle", "5730\n"),
        ("The largest input", "1000000000000000000\n"),
    ],
    expl=[
        "Of 1 … 20, only 7 and 17 contain a seven, so 18 remain.",
        "The numbers 7, 17, 27, 37, 47, 57, 67 and 70 … 77 are all out — 15 of them — leaving 62.",
    ],
    prereqs=[
        ("math_digits", "Taking a number apart one decimal digit at a time."),
        ("dp", "Counting by splitting on the first place two things differ."),
    ],
)


_p(
    "digit-sum-divisible-count", "Digits That Add Up", "Medium",
    topics=["Dynamic Programming", "Math"], subtopics=["Digit DP", "Counting", "Modular Arithmetic"],
    companies=["Google", "Microsoft"],
    shape="two", ret="long",
    todo="digit DP with state (position, tight, digit sum mod k); count the free suffixes with a table over residues",
    description=(
        "Count the integers from `1` to `N` inclusive whose digits add up to a multiple of `k`. "
        "For example `k = 3` and `x = 51` counts, because `5 + 1 = 6`.\n\n"
        "### Input\nOne line: `N k`.\n\n"
        "### Output\nThe count."
    ),
    constraints="1 ≤ N ≤ 10^18\n1 ≤ k ≤ 100",
    hints=[
        "The previous problem's state was (position, tight). Here the condition depends on everything chosen so far — but only through one number: the digit sum so far, modulo k.",
        "So carry that residue. `ways[r]` = how many ways to fill the remaining positions so the rest of the digits add up to r mod k — that table depends only on how many positions are left.",
        "Precompute `free[len][r]` for len = 0 .. 19: `free[0][0] = 1`, and `free[len][r] = sum over d of free[len-1][(r - d) mod k]`. Then walk N's digits exactly as before.",
    ],
    opt=("O(D · k · 10)", "O(D · k)",
         "D ≤ 19 positions, k residues, ten digits — about 19000 steps regardless of N."),
    editorial=(
        "## The one thing this teaches\n**Digit DP carries whatever the condition needs, and "
        "nothing else.** \"Digits sum to a multiple of k\" does not need the sum — it needs "
        "the sum *mod k*, which is at most 100 values instead of 171.\n\n"
        "## The free table\nOnce a prefix is strictly below N, the rest is unconstrained, so the "
        "count depends only on how many positions remain and which residue they must supply:\n"
        "```java\nlong[][] free = new long[D + 1][k];\nfree[0][0] = 1;\n"
        "for (int len = 1; len <= D; len++)\n    for (int r = 0; r < k; r++)\n"
        "        for (int d = 0; d <= 9; d++)\n"
        "            free[len][r] += free[len - 1][((r - d) % k + k) % k];\n```\n\n"
        "## Walking the bound\n```java\nlong count = 0;\nint sum = 0;\n"
        "for (int i = 0; i < D; i++) {\n    int cap = s[i] - '0';\n"
        "    for (int d = 0; d < cap; d++) {                 // go below N here\n"
        "        int need = ((0 - (sum + d)) % k + k) % k;   // what the rest must supply\n"
        "        count += free[D - i - 1][need];\n    }\n    sum += cap;                    "
        "     // stay tight\n}\nif (sum % k == 0) count++;                            // N itself\n"
        "if (0 % k == 0) count--;                              // drop the number 0\n```\n\n"
        "## Why Java's `%` needs the double fix\n`(0 - 7) % 3` is `-1` in Java, and `free[len][-1]` "
        "throws. `((x % k) + k) % k` is the idiom; the `+ k` before the second `%` is what makes "
        "it non-negative. Python's `%` already returns a non-negative result for a positive "
        "modulus, which is exactly the kind of difference that makes a solution pass in one "
        "language and crash in the other.\n\n"
        "## Subtracting zero\nThe walk counts `0 … N`, and 0's digit sum is 0, a multiple of "
        "every k. The range starts at 1, so it always comes off.\n\n"
        "## The general shape\nEvery digit DP is (position, tight, *the thing the condition "
        "needs*). Swap the residue for \"the previous digit\" and you count numbers with "
        "non-decreasing digits; swap it for a bitmask and you count numbers with distinct "
        "digits."
    ),
    py='''
def solve(x, y):
    n, k = int(x), int(y)
    s = str(n)
    D = len(s)
    free = [[0] * k for _ in range(D + 1)]
    free[0][0] = 1
    for length in range(1, D + 1):
        row = free[length]
        prev = free[length - 1]
        for r in range(k):
            total = 0
            for d in range(10):
                total += prev[(r - d) % k]
            row[r] = total
    count = 0
    ssum = 0
    for i, ch in enumerate(s):
        cap = int(ch)
        for d in range(cap):
            need = (-(ssum + d)) % k
            count += free[D - i - 1][need]
        ssum += cap
    if ssum % k == 0:
        count += 1
    return count - 1
''',
    java='''
    static long solve(long x, long y) {
        char[] s = Long.toString(x).toCharArray();
        int k = (int) y, D = s.length;
        long[][] free = new long[D + 1][k];
        free[0][0] = 1;
        for (int len = 1; len <= D; len++)
            for (int r = 0; r < k; r++) {
                long total = 0;
                for (int d = 0; d <= 9; d++) total += free[len - 1][((r - d) % k + k) % k];
                free[len][r] = total;
            }
        long count = 0;
        int sum = 0;
        for (int i = 0; i < D; i++) {
            int cap = s[i] - '0';
            for (int d = 0; d < cap; d++) {
                int need = ((-(sum + d)) % k + k) % k;
                count += free[D - i - 1][need];
            }
            sum += cap;
        }
        if (sum % k == 0) count++;
        return count - 1;
    }
''',
    examples=[("Example 1", "20 3\n"), ("Example 2", "100 10\n")],
    hidden=[
        ("Every number counts", "50 1\n"),
        ("Only multiples of nine's digit sum", "99 9\n"),
        ("A modulus no digit sum can reach twice", "9 7\n"),
        ("Large N, small k", "1000000000000000000 3\n"),
        ("Large N, large k", "1000000000000000000 97\n"),
        ("Tiny range", "1 2\n"),
    ],
    expl=[
        "3, 6, 9, 12, 15 and 18 have digit sums 3, 6, 9, 3, 6, 9 — six numbers.",
        "Only 19, 28, 37, 46, 55, 64, 73, 82, 91 have digit sum exactly 10, and 100 has digit sum 1.",
    ],
    prereqs=[
        ("math_digits", "The digits of a number, left to right."),
        ("modulo", "Carrying a residue instead of the value itself."),
        ("dp", "A table over (positions left, residue needed)."),
    ],
)


_p(
    "min-cost-jump-window", "Stepping Stones", "Medium",
    topics=["Dynamic Programming"], subtopics=["Monotonic Deque", "Sliding Window", "DP Optimization"],
    companies=["Google", "Meta"],
    shape="arr_k", ret="long",
    todo="dp[i] = a[i] + min(dp[i-k .. i-1]); keep that minimum in a deque of increasing dp values",
    description=(
        "Stones numbered `0 … n-1` cross a river. Standing on stone `i` costs `a[i]` — which "
        "may be negative, if the stone is a rest point. You start on stone `0` and finish on "
        "stone `n-1`, and from a stone you may jump forward by 1 up to `k` places.\n\n"
        "Print the minimum total cost, counting both the first and the last stone.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe minimum total cost."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ k ≤ n\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "The recurrence is easy: `dp[i] = a[i] + min(dp[i-k] … dp[i-1])`. Written directly that is O(n·k), which is 10¹⁰ at the limits.",
        "The inner `min` is a minimum over a sliding window of the dp array — the same window that moves one step right each time i does.",
        "Keep a deque of indices whose dp values increase from front to back. Drop the front when it falls out of the window; drop from the back anything no smaller than the value you are about to add. The front is always the window's minimum.",
    ],
    opt=("O(n)", "O(k)",
         "Every index enters and leaves the deque once, so the inner loops are O(1) amortized."),
    editorial=(
        "## The one thing this teaches\n**When a DP transition is a minimum over a moving "
        "window, the window structure removes the k.** The recurrence does not change — only "
        "how fast you can evaluate it. That is what \"DP optimisation\" means.\n\n"
        "## Approach\n```java\nDeque<Integer> dq = new ArrayDeque<>();   // indices, dp increasing\n"
        "long[] dp = new long[n];\ndp[0] = a[0];\ndq.addLast(0);\n"
        "for (int i = 1; i < n; i++) {\n"
        "    while (dq.peekFirst() < i - k) dq.pollFirst();      // left the window\n"
        "    dp[i] = a[i] + dp[dq.peekFirst()];                  // the window minimum\n"
        "    while (!dq.isEmpty() && dp[dq.peekLast()] >= dp[i]) dq.pollLast();\n"
        "    dq.addLast(i);\n}\nreturn dp[n - 1];\n```\n\n"
        "## Why dropping from the back is safe\nIf `dp[j] >= dp[i]` and `j < i`, then j leaves "
        "the window before i does and is never smaller — so j can never be the answer while i "
        "is present. It is dominated, and dominated candidates are exactly what a monotonic "
        "structure discards.\n\n"
        "## Why this is O(n) and not O(n·k)\nTwo nested `while`s inside a `for` and still "
        "linear: each index is pushed once and can therefore be popped at most once, so the "
        "pops total n over the whole loop. That is the amortized argument from the complexity "
        "unit, in the place it pays best.\n\n"
        "## Why negative costs matter\nWith all-positive stones, always jumping the full k is "
        "optimal and no DP is needed. A rest point worth −100 breaks that: it can be worth "
        "landing on a cheap stone early, and only the table knows.\n\n"
        "## The family this belongs to\nA max-plus window is the same code with the comparison "
        "flipped. When the transition is a minimum over a *value* rather than an index window, "
        "the corresponding tools are convex-hull trick and divide-and-conquer optimisation — "
        "the same idea of discarding dominated candidates, with a different notion of dominated."
    ),
    py='''
def solve(a, k):
    n = len(a)
    k = int(k)
    if n == 1:
        return a[0]
    dp = [0] * n
    dp[0] = a[0]
    dq = deque([0])
    for i in range(1, n):
        while dq[0] < i - k:
            dq.popleft()
        dp[i] = a[i] + dp[dq[0]]
        while dq and dp[dq[-1]] >= dp[i]:
            dq.pop()
        dq.append(i)
    return dp[n - 1]
''',
    java='''
    static long solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        if (n == 1) return a[0];
        long[] dp = new long[n];
        dp[0] = a[0];
        int[] dq = new int[n];
        int head = 0, tail = 0;
        dq[tail++] = 0;
        for (int i = 1; i < n; i++) {
            while (dq[head] < i - k) head++;
            dp[i] = a[i] + dp[dq[head]];
            while (tail > head && dp[dq[tail - 1]] >= dp[i]) tail--;
            dq[tail++] = i;
        }
        return dp[n - 1];
    }
''',
    examples=[
        ("Example 1", "6 2\n1 5 2 9 3 4\n"),
        ("Example 2", "5 1\n3 1 4 1 5\n"),
    ],
    hidden=[
        ("A single stone", "1 1\n42\n"),
        ("A rest point worth reaching", "6 3\n0 8 8 -100 8 0\n"),
        ("One jump reaches the end", "4 3\n5 100 100 5\n"),
        ("All negative", "7 2\n-1 -2 -3 -4 -5 -6 -7\n"),
        ("Large window, mixed signs", "10 5\n4 -3 7 -8 2 9 -1 6 -5 3\n"),
        ("Every stone must be used", "5 1\n-1000000000 -1000000000 -1000000000 -1000000000 -1000000000\n"),
    ],
    expl=[
        "0 → 2 → 4 → 5 costs 1 + 2 + 3 + 4 = 10. Jumping over stone 2 to stone 3 would pay 9.",
        "k = 1 means every stone is stepped on, so the answer is the whole sum, 14.",
    ],
    prereqs=[
        ("dp", "A linear recurrence over the indices."),
        ("sliding_window", "A window that moves one step at a time."),
        ("queue", "A deque used from both ends."),
    ],
)


_p(
    "subset-sum-closest-below", "Fill the Van", "Hard",
    topics=["Dynamic Programming", "Arrays"], subtopics=["Meet in the Middle", "Sorting", "Binary Search"],
    companies=["Google", "Jane Street"],
    shape="arr_k", ret="long",
    todo="split the items in half, enumerate every subset sum of each half, sort one side and binary-search it for the best partner",
    description=(
        "A van carries at most `W` kilograms. There are `n` crates with given weights; you may "
        "take any subset. Print the **largest total weight** that does not exceed `W` "
        "(`0` if every crate is too heavy).\n\n"
        "### Input\nLine 1: `n W`.\nLine 2: `n` integers, the weights.\n\n"
        "### Output\nThe heaviest load that fits."
    ),
    constraints="1 ≤ n ≤ 40\n1 ≤ W ≤ 10^18\n1 ≤ weight ≤ 10^9",
    hints=[
        "The knapsack table from stage 7 is O(n·W), and W is 10¹⁸ — the capacity is far too large to index. Brute force is 2⁴⁰ ≈ 10¹², also too slow.",
        "But 2²⁰ is only a million. Split the crates into two halves and enumerate *all* subset sums of each half separately.",
        "Every answer is one sum from the left plus one from the right. Sort the right-hand sums; for each left sum `s`, binary-search the largest right sum ≤ W − s.",
    ],
    opt=("O(2^(n/2) · n)", "O(2^(n/2))",
         "Two halves of about a million sums each, sorted once, then one binary search per left sum."),
    editorial=(
        "## The one thing this teaches\n**Meet in the middle: when neither the exponent nor the "
        "table is affordable, halve the exponent.** 2⁴⁰ is hopeless and 2²⁰ is "
        "instant, and the price of the trick is one sort and one binary search per candidate.\n\n"
        "## Approach\n```java\nlong[] left  = allSubsetSums(a, 0, n / 2);   // 2^(n/2) values\n"
        "long[] right = allSubsetSums(a, n / 2, n);\nArrays.sort(right);\n\nlong best = 0;\n"
        "for (long s : left) {\n    if (s > W) continue;\n"
        "    int j = upperBound(right, W - s) - 1;      // largest right sum that still fits\n"
        "    if (j >= 0) best = Math.max(best, s + right[j]);\n}\nreturn best;\n```\n\n"
        "## Why splitting is legal\nEvery subset of the crates is a subset of the left half "
        "together with a subset of the right half, independently — so enumerating each side "
        "and pairing them covers every subset exactly once. Nothing is lost; the pairing is just "
        "done by a binary search instead of by another loop.\n\n"
        "## When to reach for it\nThe tell is `n ≤ 40` (or 30-something) with a value range "
        "that rules out a DP table. `n ≤ 20` means plain 2ⁿ; `n ≤ 40` with a huge "
        "capacity means meet in the middle; a small capacity means the knapsack table, whatever "
        "n is. Three different answers to what looks like one problem.\n\n"
        "## The empty subset\nBoth halves include the sum 0, so \"take nothing from the left\" "
        "and \"take nothing at all\" are both covered. That is why the answer is 0 rather than "
        "undefined when every crate is overweight.\n\n"
        "## Overflow\n40 crates at 10⁹ is 4·10¹⁰, and W reaches 10¹⁸. "
        "Everything here is a `long`; an `int` accumulator wraps silently and produces a load "
        "that \"fits\"."
    ),
    py='''
def solve(a, k):
    from bisect import bisect_right
    W = int(k)
    half = len(a) // 2

    def sums(xs):
        res = [0]
        for x in xs:
            res += [r + x for r in res]
        return res

    left = [s for s in sums(a[:half]) if s <= W]
    right = sorted(s for s in sums(a[half:]) if s <= W)
    best = 0
    for s in left:
        j = bisect_right(right, W - s) - 1
        if j >= 0 and s + right[j] > best:
            best = s + right[j]
    return best
''',
    java='''
    static long[] subsetSums(int[] a, int from, int to) {
        int m = to - from;
        long[] res = new long[1 << m];
        for (int mask = 1; mask < (1 << m); mask++) {
            int low = Integer.numberOfTrailingZeros(mask);
            res[mask] = res[mask & (mask - 1)] + a[from + low];
        }
        return res;
    }

    static long solve(int[] a, long W) {
        int n = a.length, half = n / 2;
        long[] left = subsetSums(a, 0, half);
        long[] right = subsetSums(a, half, n);
        Arrays.sort(right);
        long best = 0;
        for (long s : left) {
            if (s > W) continue;
            long room = W - s;
            int lo = 0, hi = right.length - 1, j = -1;
            while (lo <= hi) {
                int mid = (lo + hi) >>> 1;
                if (right[mid] <= room) { j = mid; lo = mid + 1; } else hi = mid - 1;
            }
            if (j >= 0) best = Math.max(best, s + right[j]);
        }
        return best;
    }
''',
    examples=[
        ("Example 1", "5 10\n3 34 4 12 5\n"),
        ("Example 2", "4 7\n8 9 10 11\n"),
    ],
    hidden=[
        ("One crate that fits exactly", "1 5\n5\n"),
        ("Everything fits", "6 1000000000000000000\n1 2 3 4 5 6\n"),
        ("An exact fill exists", "8 100\n41 27 19 33 12 58 7 26\n"),
        ("Odd count, heavy crates", "7 1500000000\n999999999 999999999 500000001 1 2 3 999999999\n"),
        ("Thirty-six crates", "36 4000000000\n"
         "913571049 226181459 845912233 108459221 733120981 501228847 677319451 320884127 "
         "994128733 152730941 481902377 869241187 274150903 736815499 403921817 591038429 "
         "128470993 950172301 362985811 807264439 219438721 645093587 470128979 883051213 "
         "195728647 719204357 338916091 562840729 104938271 928471039 253619807 771092383 "
         "416503927 689214571 147028339 835619477\n"),
    ],
    expl=[
        "The crates that could combine are 3, 4 and 5 — 34 and 12 are already over the limit on their own. All three together weigh 12, which overshoots, so the best pair is 4 + 5 = 9.",
        "The lightest crate already weighs 8, so the van leaves empty.",
    ],
    prereqs=[
        ("bit_manip", "Enumerating every subset of a half as a bitmask."),
        ("sorting", "One side sorted so the other can be searched."),
        ("binary_search", "The largest value that still fits."),
        ("overflow", "Sums beyond 2·10⁹ need a long."),
    ],
)
