# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 37 — the syllabus roadmap, stage 7: the DP families that had no rung.
#
#   knapsack-01-max-value     the 0/1 knapsack itself: capacity as a dimension, iterated downwards
#   count-subsets-sum-k       the same table counting instead of maximising — modulo a prime
#   stock-buy-sell-unlimited  two states, holding and not holding, updated every day
#   stock-with-fee            the same machine with a cost on one transition
#   min-score-triangulation   interval DP: choose the triangle on edge (i, j), split in two
# ===========================================================================

_p(
    "knapsack-01-max-value", "Pack the Most Valuable Bag", "Easy",
    topics=["Dynamic Programming"], subtopics=["0/1 Knapsack"], companies=["Amazon", "Google"],
    shape="pairs_k", ret="long", todo="best[c] = best value within capacity c; for each item, update c from high to low so the item is used at most once",
    description=(
        "You have `n` items, each with a weight and a value, and a bag that holds a total weight of "
        "at most `W`. Each item is taken whole or not at all. Print the largest total value that fits.\n\n"
        "### Input\nLine 1: `n W`.\nNext `n` lines: `weight value`.\n\n"
        "### Output\nThe maximum total value."
    ),
    constraints="1 ≤ n ≤ 100\n1 ≤ W ≤ 10^4\n1 ≤ weight ≤ 10^4\n0 ≤ value ≤ 10^6",
    hints=[
        "Taking the best value-per-weight first fails when items cannot be split — try weights 3, 2, 2 with values 5, 3, 3 and W = 4.",
        "For each item there are two choices: skip it, or take it and lose its weight from the capacity. The state is (items considered, capacity left).",
        "Roll it into one array: best[c] = max(best[c], best[c − w] + v). Loop c from W down to w, so best[c − w] still means \"without this item\".",
    ],
    opt=("O(n · W)", "O(W)", "One pass per item over the capacities, from high to low, in a single array."),
    editorial=(
        "## The one thing this teaches\n**When a choice consumes a resource, the amount left is a "
        "dimension of the state.** Greedy by value-per-weight is optimal only when items can be "
        "split. Whole items need `best[c]` for every capacity `c`.\n\n"
        "## Approach\n```java\nlong[] best = new long[W + 1];               // best value within capacity c\n"
        "for (int[] item : items) {\n    int w = item[0], v = item[1];\n"
        "    for (int c = W; c >= w; c--)                  // DOWNWARDS: each item once\n"
        "        best[c] = Math.max(best[c], best[c - w] + v);\n}\nreturn best[W];\n```\n\n"
        "## Why downwards\nGoing upwards, `best[c − w]` may already include this item, so the same "
        "item gets packed again — that is the *unbounded* knapsack. The loop direction is the whole "
        "difference between the two problems.\n\n"
        "## The table this rolls up\n`dp[i][c] = max(dp[i−1][c], dp[i−1][c−w] + v)`. Row i reads only "
        "row i − 1, so one row is enough if you do not overwrite what you still need."
    ),
    py='''
def solve(p, k):
    best = [0] * (k + 1)
    for w, v in p:
        for c in range(k, w - 1, -1):
            if best[c - w] + v > best[c]:
                best[c] = best[c - w] + v
    return best[k]
''',
    java='''
    static long solve(int[][] p, int W) {
        int n = p.length;
        long[][] dp = new long[n + 1][W + 1];
        for (int i = 1; i <= n; i++) {
            int w = p[i - 1][0], v = p[i - 1][1];
            for (int c = 0; c <= W; c++) {
                dp[i][c] = dp[i - 1][c];
                if (c >= w) dp[i][c] = Math.max(dp[i][c], dp[i - 1][c - w] + v);
            }
        }
        return dp[n][W];
    }
''',
    examples=[("Example 1", "3 4\n3 5\n2 3\n2 3\n"), ("Example 2", "2 1\n2 10\n3 20\n")],
    hidden=[
        ("Everything fits", "3 100\n10 1\n20 2\n30 3\n"),
        ("One heavy valuable item", "3 10\n10 100\n4 30\n5 40\n"),
        ("Exact fill beats near fill", "4 7\n3 4\n4 5\n2 3\n5 7\n"),
        ("Zero-value items", "2 5\n1 0\n2 0\n"),
    ],
    expl=[
        "The weight-3 item is worth the most per unit, but it leaves room for nothing else. The two weight-2 items fit together for 6.",
        "Nothing fits in a bag of capacity 1.",
    ],
    prereqs=[
        ("dp", "A table indexed by a remaining resource."),
        ("dp2d", "A two-dimensional recurrence rolled into one array."),
    ],
)

_p(
    "count-subsets-sum-k", "Count Subsets With a Given Sum", "Medium",
    topics=["Dynamic Programming", "Math"], subtopics=["0/1 Knapsack", "Counting", "Modular Arithmetic"], companies=["Google", "Microsoft"],
    shape="arr_k", ret="long", todo="ways[s] = number of subsets reaching sum s; for each value, add ways[s − x] into ways[s] from high s to low, mod 1e9+7",
    description=(
        "Count the subsets of the array whose elements sum to exactly `k`. Elements at different "
        "indices are different, even if equal in value. The count can be huge: print it modulo "
        "10^9 + 7.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` positive integers.\n\n"
        "### Output\nThe number of subsets, modulo 1 000 000 007."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ k ≤ 10^4\n1 ≤ a[i] ≤ 1000",
    hints=[
        "There are 2^n subsets — hopeless at n = 1000.",
        "This is the 0/1 knapsack with the question changed: not \"the best value within capacity c\" but \"how many ways to reach exactly s\".",
        "ways[0] = 1 (the empty subset). For each x, for s from k down to x: ways[s] = (ways[s] + ways[s − x]) mod p.",
    ],
    opt=("O(n · k)", "O(k)", "The 0/1 knapsack loop, summing counts instead of taking a maximum, reduced mod p."),
    editorial=(
        "## The one thing this teaches\n**The knapsack table answers several questions, and the "
        "combine step decides which.** `max` gives the best value; `or` gives whether a sum is "
        "reachable; `+` gives how many ways. The loops do not change.\n\n"
        "## Approach\n```java\nfinal long MOD = 1_000_000_007L;\nlong[] ways = new long[k + 1];\n"
        "ways[0] = 1;                                   // the empty subset\n"
        "for (int x : a)\n    for (int s = k; s >= x; s--)               // downwards: each element once\n"
        "        ways[s] = (ways[s] + ways[s - x]) % MOD;\nreturn ways[k];\n```\n\n"
        "## Why the base case is 1, not 0\n`ways[0] = 1` says \"there is one way to reach 0: take "
        "nothing\". Every count is built by extending that one way. With 0 the whole table stays 0.\n\n"
        "## Where the modulus goes\nReduce after every addition. Two values below p add to below 2p, "
        "which fits comfortably in a `long` — but a thousand unreduced additions may not."
    ),
    py='''
def solve(a, k):
    MOD = 1_000_000_007
    ways = [0] * (k + 1)
    ways[0] = 1
    for x in a:
        for s in range(k, x - 1, -1):
            ways[s] = (ways[s] + ways[s - x]) % MOD
    return ways[k]
''',
    java='''
    static long solve(int[] a, long kk) {
        final long MOD = 1_000_000_007L;
        int k = (int) kk;
        long[] prev = new long[k + 1];
        prev[0] = 1;
        for (int x : a) {
            long[] cur = prev.clone();
            for (int s = x; s <= k; s++) cur[s] = (cur[s] + prev[s - x]) % MOD;
            prev = cur;
        }
        return prev[k];
    }
''',
    examples=[("Example 1", "5 6\n1 2 3 4 5\n"), ("Example 2", "4 2\n1 1 1 1\n")],
    hidden=[
        ("Unreachable", "3 100\n1 2 3\n"),
        ("The whole array", "4 10\n1 2 3 4\n"),
        ("A single element", "1 7\n7\n"),
        ("Large count needs the modulus", "40 20\n1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1\n"),
    ],
    expl=[
        "{1, 5}, {2, 4} and {1, 2, 3} each sum to 6.",
        "Any two of the four 1s: C(4, 2) = 6 subsets.",
    ],
    prereqs=[
        ("dp", "The 0/1 knapsack table, with counts instead of values."),
        ("modulo", "Reducing after every addition."),
    ],
)

_p(
    "stock-buy-sell-unlimited", "Trade as Often as You Like", "Easy",
    topics=["Dynamic Programming", "Greedy"], subtopics=["State Machine DP"], companies=["Amazon", "Bloomberg"],
    shape="arr", ret="long", todo="track two states per day — best cash while holding a share and while not holding — and update both from yesterday's",
    description=(
        "You know a stock's price for each of `n` days. You may buy and sell as many times as you "
        "like, but you can hold **at most one share** at a time (sell before buying again). Print "
        "the maximum profit.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` prices.\n\n"
        "### Output\nThe maximum profit (0 if no trade helps)."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ price ≤ 10^4",
    hints=[
        "On any day you are in one of two situations: holding a share, or not.",
        "free = max(free, hold + price) — stay free, or sell today. hold = max(hold, free − price) — keep holding, or buy today.",
        "Start with free = 0 and hold = −∞ (you cannot hold before buying). The answer is free after the last day.",
    ],
    opt=("O(n)", "O(1)", "Two numbers — the best cash holding and not holding — updated once per day."),
    editorial=(
        "## The one thing this teaches\n**When the choices depend on your situation, make the "
        "situation the state.** The day alone is not enough: whether you may sell depends on whether "
        "you hold. Two states per day, each with its transitions, and the problem is a small machine.\n\n"
        "## Approach\n```java\nlong free = 0, hold = Long.MIN_VALUE / 2;     // cash if not holding / holding\n"
        "for (int p : prices) {\n    long prevFree = free;\n"
        "    free = Math.max(free, hold + p);            // rest, or sell\n"
        "    hold = Math.max(hold, prevFree - p);        // rest, or buy\n}\nreturn free;\n```\n\n"
        "## The greedy shortcut, and why the machine matters\nHere the answer is also the sum of every "
        "positive day-to-day rise. But add a cooldown after selling, or a fee per trade, and the "
        "shortcut breaks while the machine only gains a state or a cost on one arrow.\n\n"
        "## Why `prevFree`\nUpdating `free` first and then using it in `hold` lets you sell and buy on "
        "the same day. Here that happens to be harmless; with a fee or a cooldown it is a bug."
    ),
    py='''
def solve(a):
    free, hold = 0, float("-inf")
    for p in a:
        free, hold = max(free, hold + p), max(hold, free - p)
    return free
''',
    java='''
    static long solve(int[] a) {
        long profit = 0;
        for (int i = 1; i < a.length; i++)
            if (a[i] > a[i - 1]) profit += a[i] - a[i - 1];
        return profit;
    }
''',
    examples=[("Example 1", "6\n3 8 2 6 9 4\n"), ("Example 2", "4\n9 7 4 1\n")],
    hidden=[
        ("One day", "1\n5\n"),
        ("Strictly rising", "5\n1 2 3 4 5\n"),
        ("Flat", "4\n6 6 6 6\n"),
        ("Zig-zag", "8\n1 10 1 10 1 10 1 10\n"),
    ],
    expl=[
        "Buy at 3, sell at 8 (+5); buy at 2, sell at 9 (+7). Total 12.",
        "The price only falls, so the best is not to trade.",
    ],
    prereqs=[
        ("dp", "A small number of states per step, each built from the previous step's."),
        ("greedy", "Why summing every rise works here, and stops working with a fee."),
    ],
)

_p(
    "stock-with-fee", "Trading With a Fee", "Medium",
    topics=["Dynamic Programming"], subtopics=["State Machine DP"], companies=["Meta", "Bloomberg"],
    shape="arr_k", ret="long", todo="the holding / not-holding machine, subtracting the fee on the sell transition",
    description=(
        "As in *Trade as Often as You Like*, you may make any number of trades and hold at most one "
        "share — but every completed trade costs a fixed `fee`, charged when you sell. Print the "
        "maximum profit.\n\n"
        "### Input\nLine 1: `n fee`.\nLine 2: the `n` prices.\n\n"
        "### Output\nThe maximum profit (0 if no trade helps)."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ fee ≤ 10^4\n1 ≤ price ≤ 10^5",
    hints=[
        "Summing every positive rise now pays the fee on each small rise — and many small trades can lose to one long one.",
        "Keep the same two states. Only the sell arrow changes: free = max(free, hold + price − fee).",
        "hold = max(hold, prevFree − price). Use yesterday's `free`, so a sale and a purchase on the same day do not interact.",
    ],
    opt=("O(n)", "O(1)", "The two-state machine with the fee on one transition."),
    editorial=(
        "## The one thing this teaches\n**A rule change is an edge change, not a new algorithm.** The "
        "fee attaches to the \"sell\" transition of the same two-state machine; nothing else moves. "
        "The greedy \"sum every rise\" breaks here, which is why the machine is worth learning.\n\n"
        "## Approach\n```java\nlong free = 0, hold = -prices[0];\nfor (int i = 1; i < n; i++) {\n"
        "    long prevFree = free;\n    free = Math.max(free, hold + prices[i] - fee);   // sell, paying the fee\n"
        "    hold = Math.max(hold, prevFree - prices[i]);       // buy\n}\nreturn free;\n```\n\n"
        "## Why greedy fails\nPrices 1 3 2 8 with fee 2: trading each rise earns (3−1−2) + (8−2−2) = 4, "
        "but buying at 1 and selling at 8 earns 8−1−2 = 5. The machine keeps the \"hold\" option "
        "open through the dip, and greedy cannot.\n\n"
        "## The family\n| Rule | Change to the machine |\n| --- | --- |\n| Fee per trade | subtract on sell |\n"
        "| Cooldown after selling | a third state, \"just sold\" |\n| At most k trades | a state per trade count |"
    ),
    py='''
def solve(a, k):
    fee = k
    free, hold = 0, -a[0]
    for p in a[1:]:
        free, hold = max(free, hold + p - fee), max(hold, free - p)
    return free
''',
    java='''
    static long solve(int[] a, long fee) {
        int n = a.length;
        long[] free = new long[n], hold = new long[n];
        hold[0] = -a[0];
        for (int i = 1; i < n; i++) {
            free[i] = Math.max(free[i - 1], hold[i - 1] + a[i] - fee);
            hold[i] = Math.max(hold[i - 1], free[i - 1] - a[i]);
        }
        return free[n - 1];
    }
''',
    examples=[("Example 1", "4 2\n1 3 2 8\n"), ("Example 2", "5 10\n4 9 6 12 5\n")],
    hidden=[
        ("No fee", "6 0\n3 8 2 6 9 4\n"),
        ("Fee kills every trade", "3 100\n1 50 99\n"),
        ("Two separate trades", "6 1\n1 5 5 1 5 9\n"),
        ("One day", "1 3\n7\n"),
    ],
    expl=[
        "Trading each rise earns (3 − 1 − 2) + (8 − 2 − 2) = 4; one trade from 1 to 8 earns 8 − 1 − 2 = 5.",
        "The best single trade, 4 → 12, earns 8 − 10 < 0. Doing nothing is best.",
    ],
    prereqs=[
        ("dp", "Holding and not-holding states, updated per day."),
        ("greedy", "The counterexample that shows why the fee breaks \"sum every rise\"."),
    ],
)

_p(
    "min-score-triangulation", "Cheapest Triangulation", "Medium",
    topics=["Dynamic Programming"], subtopics=["Interval DP"], companies=["Uber", "Google"],
    shape="arr", ret="long", todo="dp[i][j] = min over k in (i, j) of dp[i][k] + dp[k][j] + v[i]·v[k]·v[j]; fill by increasing length",
    description=(
        "A convex polygon has `n` vertices labelled with values `v[0] … v[n−1]` in order around it. "
        "Cut it into `n − 2` triangles using non-crossing diagonals. A triangle scores the "
        "**product** of its three vertex values. Print the minimum total score.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` vertex values.\n\n"
        "### Output\nThe minimum total score."
    ),
    constraints="3 ≤ n ≤ 50\n1 ≤ v[i] ≤ 100",
    hints=[
        "Whatever the triangulation, the edge from vertex 0 to vertex n − 1 belongs to exactly one triangle. Its third vertex k is somewhere in between.",
        "Choosing k splits the polygon into two smaller polygons, i..k and k..j, that are triangulated independently.",
        "dp[i][j] = min over i < k < j of dp[i][k] + dp[k][j] + v[i]·v[k]·v[j], with dp[i][i+1] = 0. Fill in order of increasing j − i.",
    ],
    opt=("O(n³)", "O(n²)", "O(n²) intervals, each trying O(n) split points."),
    editorial=(
        "## The one thing this teaches\n**Interval DP: pick the piece that must exist, and split "
        "around it.** The state is a contiguous range `[i, j]`; the transition chooses where the range "
        "splits; the fill order is by length, so both halves are always ready.\n\n"
        "## Approach\n```java\nlong[][] dp = new long[n][n];                 // dp[i][i+1] = 0: an edge, no triangle\n"
        "for (int len = 2; len < n; len++)             // j − i\n    for (int i = 0; i + len < n; i++) {\n"
        "        int j = i + len;\n        dp[i][j] = Long.MAX_VALUE;\n"
        "        for (int k = i + 1; k < j; k++)           // the third vertex on edge (i, j)\n"
        "            dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j] + (long) v[i] * v[k] * v[j]);\n    }\n"
        "return dp[0][n - 1];\n```\n\n"
        "## Why fill by length\n`dp[i][k]` and `dp[k][j]` are both shorter than `[i, j]`. Looping i "
        "and j in plain nested order would read entries that are not filled yet.\n\n"
        "## The same shape elsewhere\nMatrix-chain multiplication, bursting balloons, and the "
        "cheapest way to merge adjacent piles are this loop with a different cost in the middle."
    ),
    py='''
def solve(a):
    from functools import lru_cache
    n = len(a)

    @lru_cache(maxsize=None)
    def best(i, j):
        if j - i < 2:
            return 0
        return min(best(i, k) + best(k, j) + a[i] * a[k] * a[j] for k in range(i + 1, j))

    return best(0, n - 1)
''',
    java='''
    static long solve(int[] v) {
        int n = v.length;
        long[][] dp = new long[n][n];
        for (int len = 2; len < n; len++)
            for (int i = 0; i + len < n; i++) {
                int j = i + len;
                dp[i][j] = Long.MAX_VALUE;
                for (int k = i + 1; k < j; k++)
                    dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j] + (long) v[i] * v[k] * v[j]);
            }
        return dp[0][n - 1];
    }
''',
    examples=[("Example 1", "3\n2 5 7\n"), ("Example 2", "4\n4 1 5 2\n")],
    hidden=[
        ("Square of equals", "4\n3 3 3 3\n"),
        ("Pentagon", "5\n1 3 1 4 1\n"),
        ("One large vertex", "6\n1 1 100 1 1 1\n"),
        ("Larger values", "6\n100 99 98 97 96 95\n"),
    ],
    expl=[
        "A triangle has only one triangulation: 2 · 5 · 7 = 70.",
        "The diagonal 1–3 gives triangles (4, 1, 2) and (1, 5, 2): 8 + 10 = 18. The other diagonal gives 20 + 40 = 60.",
    ],
    prereqs=[
        ("dp2d", "A table over ranges [i, j], filled by increasing length."),
        ("recurrence", "Choosing a split point and combining two independent halves."),
    ],
)
