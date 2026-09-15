# -*- coding: utf-8 -*-
# ===========================================================================
# Depth problems — authored toward the units' weight bands.
#
# exec'd inside gen_seed.py's namespace right after dsa_onramps.py, extending
# DEFS / JAVA_STARTERS / PREREQS in place and defining DEPTH_REFS.
#
# WHY THIS FILE EXISTS
#
# `tools/dsa_curriculum.py` now carries a `weight` (1-3, interview yield) per
# unit and a target problem-count band per weight. The bands are a ledger, not
# an assertion — see the comment on `_check_weight_bands` — and the four most
# under-served weight-3 units were the ones a learner would actually feel:
#
#   sliding-window    4 problems, one of them the Hard
#   binary-search     5, and nothing that searches anything but an array
#   graph-traversal   5, all single-source
#   greedy            4, and no problem whose greedy rule is *wrong*
#
# Fourteen problems, mostly Medium, each chosen because it adds an idea the
# unit did not already have rather than another instance of one it did:
#
#   sliding-window    the four window shapes — count-all, longest-valid,
#                     shortest-valid, and a window with a budget
#   binary-search     upper bound, a rotated array (sorted is not the point,
#                     monotone is), and binary search on the answer
#   graph-traversal   multi-source BFS, level-by-level BFS, and a directed
#                     walk where the undirected habits break
#   greedy            a rule that needs a ratio, a rule that is provably wrong
#                     on the wrong coin system, a reset, and a two-pointer pair
# ===========================================================================
from collections import deque

# ---------------------------------------------------------------------------
# Reference solutions (raw stdin string -> exact stdout string)
# ---------------------------------------------------------------------------


def _ls(inp):
    return inp.strip().split("\n")


def _nums(line):
    return list(map(int, line.split()))


# -- sliding window ---------------------------------------------------------

def sol_subarray_sum_at_most(inp):
    ls = _ls(inp)
    n, s = _nums(ls[0])
    a = _nums(ls[1])
    total = 0
    left = 0
    window = 0
    for r in range(n):
        window += a[r]
        while window > s:
            window -= a[left]
            left += 1
        total += r - left + 1
    return str(total)


def sol_longest_k_distinct(inp):
    ls = inp.strip("\n").split("\n")
    st = ls[0].strip()
    k = int(ls[1])
    count = {}
    left = 0
    best = 0
    for r, ch in enumerate(st):
        count[ch] = count.get(ch, 0) + 1
        while len(count) > k:
            c = st[left]
            count[c] -= 1
            if count[c] == 0:
                del count[c]
            left += 1
        best = max(best, r - left + 1)
    return str(best)


def sol_min_window_sum_atleast(inp):
    ls = _ls(inp)
    n, s = _nums(ls[0])
    a = _nums(ls[1])
    left = 0
    window = 0
    best = None
    for r in range(n):
        window += a[r]
        while window >= s:
            length = r - left + 1
            best = length if best is None else min(best, length)
            window -= a[left]
            left += 1
    return str(best if best is not None else 0)


def sol_longest_ones_k_flips(inp):
    ls = _ls(inp)
    n, k = _nums(ls[0])
    a = _nums(ls[1])
    left = 0
    zeros = 0
    best = 0
    for r in range(n):
        if a[r] == 0:
            zeros += 1
        while zeros > k:
            if a[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, r - left + 1)
    return str(best)


# -- binary search ----------------------------------------------------------

def _lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def sol_count_occurrences_sorted(inp):
    ls = _ls(inp)
    n = int(ls[0])
    a = _nums(ls[1]) if n else []
    x = int(ls[2])
    return str(_lower_bound(a, x + 1) - _lower_bound(a, x))


def sol_rotated_array_minimum(inp):
    ls = _ls(inp)
    n = int(ls[0])
    a = _nums(ls[1]) if n else []
    lo, hi = 0, n - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        else:
            hi = mid
    return str(a[lo])


def sol_min_ship_capacity(inp):
    ls = _ls(inp)
    n, d = _nums(ls[0])
    w = _nums(ls[1])

    def days_needed(cap):
        days, load = 1, 0
        for x in w:
            if load + x > cap:
                days += 1
                load = 0
            load += x
        return days

    lo, hi = max(w), sum(w)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if days_needed(mid) > d:
            lo = mid + 1
        else:
            hi = mid
    return str(lo)


# -- graph traversal --------------------------------------------------------

def sol_rotting_oranges(inp):
    ls = inp.strip("\n").split("\n")
    h, w = _nums(ls[0])
    grid = [list(ls[1 + i]) for i in range(h)]
    q = deque()
    fresh = 0
    for i in range(h):
        for j in range(w):
            if grid[i][j] == "R":
                q.append((i, j, 0))
            elif grid[i][j] == "F":
                fresh += 1
    last = 0
    while q:
        i, j, t = q.popleft()
        last = max(last, t)
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] == "F":
                grid[ni][nj] = "R"
                fresh -= 1
                q.append((ni, nj, t + 1))
    return "-1" if fresh else str(last)


def sol_reachable_within_k(inp):
    ls = _ls(inp)
    n, m, k = _nums(ls[0])
    s = int(ls[1])
    g = [[] for _ in range(n)]
    for i in range(m):
        u, v = _nums(ls[2 + i])
        g[u].append(v)
        g[v].append(u)
    dist = [-1] * n
    dist[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        if dist[u] == k:
            continue
        for v in g[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return str(sum(1 for d in dist if 0 <= d <= k) - 1)


def sol_directed_path_exists(inp):
    ls = _ls(inp)
    n, m = _nums(ls[0])
    s, t = _nums(ls[1])
    g = [[] for _ in range(n)]
    for i in range(m):
        u, v = _nums(ls[2 + i])
        g[u].append(v)            # one direction only
    seen = [False] * n
    stack = [s]
    seen[s] = True
    while stack:
        u = stack.pop()
        if u == t:
            return "YES"
        for v in g[u]:
            if not seen[v]:
                seen[v] = True
                stack.append(v)
    return "YES" if s == t else "NO"


# -- greedy -----------------------------------------------------------------

def sol_fractional_knapsack(inp):
    ls = _ls(inp)
    n, cap = _nums(ls[0])
    items = [tuple(_nums(ls[1 + i])) for i in range(n)]
    # Ratio order, descending. Scaled by 100 and rounded down so the answer is
    # an exact integer and the judge stays on exact comparison.
    items.sort(key=lambda t: (-t[0] * 10 ** 9 // t[1], t[1]))
    total = 0          # value * 100, to keep integer arithmetic exact
    left = cap
    for value, weight in items:
        if left == 0:
            break
        take = min(weight, left)
        total += value * 100 * take // weight
        left -= take
    return str(total)


def sol_greedy_coin_change(inp):
    """Greedy (largest coin first) count, and the true optimum, so the learner
    sees the two disagree on a non-canonical system."""
    ls = _ls(inp)
    n, amount = _nums(ls[0])
    coins = sorted(_nums(ls[1]), reverse=True)
    left = amount
    greedy = 0
    for c in coins:
        greedy += left // c
        left %= c
    greedy = greedy if left == 0 else -1

    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    best = -1 if dp[amount] == INF else dp[amount]
    return f"{greedy} {best}"


def sol_gas_station_start(inp):
    ls = _ls(inp)
    n = int(ls[0])
    gas = _nums(ls[1])
    cost = _nums(ls[2])
    if sum(gas) < sum(cost):
        return "-1"
    start = 0
    tank = 0
    for i in range(n):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0
    return str(start)


def sol_boats_to_save_people(inp):
    ls = _ls(inp)
    n, limit = _nums(ls[0])
    w = sorted(_nums(ls[1]))
    i, j = 0, n - 1
    boats = 0
    while i <= j:
        if w[i] + w[j] <= limit:
            i += 1
        j -= 1
        boats += 1
    return str(boats)


# ---------------------------------------------------------------------------
# Starter scaffolding
# ---------------------------------------------------------------------------

def _java_main(body):
    return (
        "import java.util.*;\n\n"
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        + body +
        "    }\n"
        "}\n"
    )


_PY_ARR2 = (
    "import sys\n\nd = sys.stdin.read().split()\n"
    "n, k = int(d[0]), int(d[1])\n"
    "a = list(map(int, d[2:2 + n]))\n\n"
)

_JS_ARR2 = (
    "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
    "const n = d[0], k = d[1], a = d.slice(2, 2 + n);\n\n"
)

_J_ARR2 = (
    "        int n = sc.nextInt(), k = sc.nextInt();\n"
    "        int[] a = new int[n];\n"
    "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
)


DEPTH_DEFS = [
    # =======================================================================
    # sliding-window — the four window shapes
    # =======================================================================
    dict(
        slug="subarray-sum-at-most", title="Count Subarrays With Sum ≤ S", difficulty="Medium",
        topics=["Arrays"], subtopics=["Sliding Window", "Counting"], companies=["Amazon"],
        description=(
            "Given an array of **non-negative** integers and a limit `S`, count the subarrays "
            "whose sum is at most `S`.\n\n"
            "### Input\n- Line 1: `n S`.\n- Line 2: `n` non-negative integers.\n\n"
            "### Output\nA single integer: how many of the `n(n+1)/2` subarrays qualify."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ S ≤ 10^14\n0 ≤ a[i] ≤ 10^9",
        hints=[
            "For a fixed right end r, the qualifying left ends form a contiguous range — find its leftmost member.",
            "As r moves right the window sum only grows, so the leftmost valid left never moves backwards.",
            "Shrink from the left while the sum exceeds S; then every left in [left, r] gives a valid subarray.",
            "That is `r - left + 1` subarrays ending at r. Sum those counts in a `long`.",
        ],
        opt=("O(n)", "O(1)",
             "Each index enters and leaves the window once, so both pointers together move at most 2n "
             "steps — which is why the nested-loop O(n²) count is avoidable."),
        editorial=(
            "## The one thing this teaches\n**Counting all valid windows**, which is the window "
            "shape people miss. The other three ask for one window (longest, shortest, a "
            "specific one); this one asks *how many*, and the trick is that you never enumerate "
            "them.\n\n"
            "## Approach\nFor each right end `r`, shrink `left` until the window sum is ≤ `S`. "
            "Now every subarray `a[i..r]` with `left ≤ i ≤ r` also has sum ≤ S, because dropping "
            "elements from a non-negative array can only reduce the sum. That is `r - left + 1` "
            "subarrays, counted in O(1).\n\n"
            "```java\nlong total = 0, window = 0;\nint left = 0;\n"
            "for (int r = 0; r < n; r++) {\n    window += a[r];\n"
            "    while (window > S) window -= a[left++];\n    total += r - left + 1;\n}\n```\n\n"
            "## Why non-negativity is in the statement\nIt is the whole licence for the "
            "algorithm. With a negative value present, shrinking the window can *increase* the "
            "sum, so `left` would have to be able to move backwards — and a window that moves "
            "both ways is not a sliding window at all. The negative-value version of this "
            "problem is solved with prefix sums and a map, which is a different unit.\n\n"
            "Count in `long`: n = 10⁵ gives about 5 × 10⁹ subarrays, well past `int`."
        ),
        ref=sol_subarray_sum_at_most,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n, S = int(d[0]), int(d[1])\n"
            "a = list(map(int, d[2:2 + n]))\n\n"
            "def solve(a, S):\n"
            "    # TODO: for each right end, shrink left until sum <= S, then add r - left + 1\n"
            "    return 0\n\nprint(solve(a, S))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean);\n"
            "const n = Number(d[0]), S = BigInt(d[1]);\n"
            "const a = d.slice(2, 2 + n).map(Number);\n\n"
            "function solve(a, S) {\n"
            "  // TODO: for each right end, shrink left until sum <= S, then add r - left + 1\n"
            "  return 0n;\n}\n\nconsole.log(solve(a, S).toString());\n"
        ),
        cases=[
            ("example", "Example 1", "4 5\n1 2 3 4\n"),
            ("example", "Example 2", "3 0\n0 0 0\n"),
            ("hidden", "Every subarray qualifies", "4 1000\n1 1 1 1\n"),
            ("hidden", "None qualifies", "3 1\n5 6 7\n"),
            ("hidden", "Zeros inflate the count", "5 3\n0 1 0 2 0\n"),
        ],
        example_expl=[
            "`[1]`, `[2]`, `[3]`, `[4]`, `[1,2]` and `[2,3]` — 6 of the 10 subarrays have "
            "sum ≤ 5. `[1,2,3]` sums to 6 and just misses.",
            "All six subarrays of three zeros sum to 0, which is ≤ 0.",
        ],
    ),
    dict(
        slug="longest-k-distinct", title="Longest Substring With ≤ K Distinct", difficulty="Medium",
        topics=["Strings"], subtopics=["Sliding Window", "Hashing"], companies=["Google"],
        description=(
            "Find the length of the longest substring containing at most `K` distinct "
            "characters.\n\n"
            "### Input\n- Line 1: the string `s` (lowercase letters, no spaces).\n"
            "- Line 2: the integer `K`.\n\n### Output\nThe maximum length, or 0 if `K` is 0."
        ),
        constraints="1 ≤ |s| ≤ 10^5\n0 ≤ K ≤ 26\ns consists of lowercase English letters.",
        hints=[
            "Keep a count per character in the window; the number of distinct characters is the map's size.",
            "Grow the right edge unconditionally, then shrink the left edge while the window is invalid.",
            "When a character's count drops to 0, REMOVE the key — otherwise the size never shrinks.",
            "Record the best length after each shrink, not before it.",
        ],
        opt=("O(n)", "O(K)",
             "Each index is added once and removed at most once; the map holds at most K + 1 keys "
             "at any moment."),
        editorial=(
            "## The one thing this teaches\n**Grow-then-repair.** The longest-valid window shape "
            "is always the same three lines: extend the right edge with no condition, shrink the "
            "left edge while the window is invalid, then record. Not \"extend if it is still "
            "valid\" — that version gets stuck, because a window that is invalid now may be the "
            "prefix of the answer once the left edge catches up.\n\n"
            "## Approach\n```java\nMap<Character,Integer> count = new HashMap<>();\n"
            "int left = 0, best = 0;\nfor (int r = 0; r < n; r++) {\n"
            "    count.merge(s.charAt(r), 1, Integer::sum);\n"
            "    while (count.size() > K) {\n        char c = s.charAt(left++);\n"
            "        if (count.merge(c, -1, Integer::sum) == 0) count.remove(c);\n    }\n"
            "    best = Math.max(best, r - left + 1);\n}\n```\n\n"
            "## The bug that is always this bug\nDecrementing a count to zero and leaving the "
            "key in the map. `count.size()` then measures \"characters ever seen in the window\" "
            "rather than \"characters currently in it\", the `while` never terminates early, and "
            "the window collapses to nothing. Remove the key, or track a separate `distinct` "
            "counter you decrement when a count hits zero.\n\n"
            "## Recognising it\n\"At most K …\" in a prompt about a contiguous stretch is the "
            "signal. The invariant is a *budget*, and the window is the largest stretch that "
            "stays inside it — which is the same shape as \"at most K zeros flipped\"."
        ),
        ref=sol_longest_k_distinct,
        starter_py=(
            "import sys\n\nlines = sys.stdin.read().split('\\n')\n"
            "s = lines[0].strip()\nK = int(lines[1])\n\n"
            "def solve(s, K):\n"
            "    # TODO: grow r, shrink left while more than K distinct, track the best length\n"
            "    return 0\n\nprint(solve(s, K))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
            "const s = L[0].trim(), K = Number(L[1]);\n\n"
            "function solve(s, K) {\n"
            "  // TODO: grow r, shrink left while more than K distinct, track the best length\n"
            "  return 0;\n}\n\nconsole.log(solve(s, K));\n"
        ),
        cases=[
            ("example", "Example 1", "eceba\n2\n"),
            ("example", "Example 2", "aaabbbccc\n2\n"),
            ("hidden", "K is zero", "abc\n0\n"),
            ("hidden", "K exceeds the alphabet used", "abcabc\n10\n"),
            ("hidden", "Single repeated character", "aaaaa\n1\n"),
        ],
        example_expl=[
            "`ece` uses two distinct characters and is the longest such substring → 3.",
            "`aaabbb` uses `a` and `b` → 6. Extending into `c` would make three.",
        ],
    ),
    dict(
        slug="min-window-sum-atleast", title="Shortest Subarray With Sum ≥ S", difficulty="Medium",
        topics=["Arrays"], subtopics=["Sliding Window"], companies=["Meta"],
        description=(
            "Given an array of **positive** integers and a target `S`, find the length of the "
            "shortest contiguous subarray whose sum is at least `S`. Print `0` if no subarray "
            "qualifies.\n\n"
            "### Input\n- Line 1: `n S`.\n- Line 2: `n` positive integers.\n\n"
            "### Output\nThe shortest qualifying length, or `0`."
        ),
        constraints="1 ≤ n ≤ 10^5\n1 ≤ S ≤ 10^14\n1 ≤ a[i] ≤ 10^9",
        hints=[
            "This is the mirror of the longest-valid window: you shrink while the window is VALID, not while it is invalid.",
            "Grow the right edge until the sum reaches S.",
            "Then, while the sum is still ≥ S, record the length and shrink from the left.",
            "Recording inside the shrink loop is what finds the shortest one rather than the first one.",
        ],
        opt=("O(n)", "O(1)",
             "Both pointers only move forward, so the total pointer movement is at most 2n "
             "regardless of how much shrinking any single step does."),
        editorial=(
            "## The one thing this teaches\nThe shrink loop's **condition is inverted** relative "
            "to the longest-window problems, and so is where you record the answer:\n\n"
            "| Asking for | Shrink while | Record |\n|---|---|---|\n"
            "| longest **valid** window | invalid | after shrinking |\n"
            "| shortest **valid** window | still valid | inside the shrink |\n\n"
            "Getting this pair the wrong way round is the single most common sliding-window "
            "error, and it does not produce a crash — it produces a plausible wrong number.\n\n"
            "## Approach\n```java\nlong window = 0;\nint left = 0, best = Integer.MAX_VALUE;\n"
            "for (int r = 0; r < n; r++) {\n    window += a[r];\n"
            "    while (window >= S) {\n        best = Math.min(best, r - left + 1);\n"
            "        window -= a[left++];\n    }\n}\n"
            "return best == Integer.MAX_VALUE ? 0 : best;\n```\n\n"
            "## Why positivity matters\nSame reason as the counting version: with a zero or "
            "negative element, shrinking need not reduce the sum, so the window can be valid, "
            "then invalid, then valid again from the same left edge — and the monotone "
            "two-pointer argument collapses. The general version needs a monotonic deque over "
            "prefix sums, which is a Hard problem in the queues unit.\n\n"
            "Sum in `long`: 10⁵ elements of 10⁹ is 10¹⁴."
        ),
        ref=sol_min_window_sum_atleast,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n, S = int(d[0]), int(d[1])\n"
            "a = list(map(int, d[2:2 + n]))\n\n"
            "def solve(a, S):\n"
            "    # TODO: grow r; while the window is STILL valid, record the length and shrink\n"
            "    return 0\n\nprint(solve(a, S))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean);\n"
            "const n = Number(d[0]), S = Number(d[1]);\n"
            "const a = d.slice(2, 2 + n).map(Number);\n\n"
            "function solve(a, S) {\n"
            "  // TODO: grow r; while the window is STILL valid, record the length and shrink\n"
            "  return 0;\n}\n\nconsole.log(solve(a, S));\n"
        ),
        cases=[
            ("example", "Example 1", "6 7\n2 3 1 2 4 3\n"),
            ("example", "Example 2", "3 100\n1 2 3\n"),
            ("hidden", "Whole array needed", "3 6\n1 2 3\n"),
            ("hidden", "Single element suffices", "5 4\n1 1 9 1 1\n"),
            ("hidden", "Target of one", "4 1\n5 5 5 5\n"),
        ],
        example_expl=[
            "`[4, 3]` sums to 7 with length 2; no single element reaches 7.",
            "The whole array sums to 6, which never reaches 100 → 0.",
        ],
    ),
    dict(
        slug="longest-ones-k-flips", title="Longest Run of Ones After K Flips", difficulty="Medium",
        topics=["Arrays"], subtopics=["Sliding Window"], companies=["Microsoft"],
        description=(
            "Given an array of 0s and 1s and a budget `K`, you may flip at most `K` zeros to "
            "ones. Print the length of the longest run of consecutive ones you can achieve.\n\n"
            "### Input\n- Line 1: `n K`.\n- Line 2: `n` values, each `0` or `1`.\n\n"
            "### Output\nThe longest achievable run of ones."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ K ≤ n\nEach a[i] is 0 or 1.",
        hints=[
            "You never need to decide which zeros to flip — only how many the window contains.",
            "Reframe it: find the longest window containing at most K zeros.",
            "Grow the right edge, counting zeros; shrink the left while the count exceeds K.",
            "You do not need a map — a single `zeros` counter is the whole window summary.",
        ],
        opt=("O(n)", "O(1)",
             "One pass with two forward-only pointers and one counter; nothing about the window "
             "needs storing beyond how many zeros are in it."),
        editorial=(
            "## The one thing this teaches\n**Reframing a construction problem as a window "
            "problem.** The prompt is about choosing which zeros to flip, which sounds like a "
            "search over subsets. It is not: any window with at most `K` zeros is achievable, "
            "and every achievable run is such a window. Once you see that, the flips vanish "
            "from the code entirely — there is no array of decisions, just a counter.\n\n"
            "Recognising that reframing is the skill. It is the same move as \"replace at most "
            "K characters\" and \"delete at most K elements\": the budget becomes the window "
            "invariant.\n\n"
            "## Approach\n```java\nint left = 0, zeros = 0, best = 0;\n"
            "for (int r = 0; r < n; r++) {\n    if (a[r] == 0) zeros++;\n"
            "    while (zeros > K) { if (a[left] == 0) zeros--; left++; }\n"
            "    best = Math.max(best, r - left + 1);\n}\n```\n\n"
            "Note the asymmetry that makes it correct: the right edge moves unconditionally and "
            "the left edge moves only to repair the invariant. `K = 0` degenerates to \"longest "
            "run of existing ones\", which is the array-scan warm-up from stage 1 — a good sign "
            "the window generalises rather than replaces it.\n\n"
            "## Variant worth noticing\nThe window never needs to *shrink below* its best size "
            "for the answer's sake, so some published solutions drop the `while` for an `if` and "
            "never shrink the window at all — the length is then a high-water mark rather than a "
            "valid window. It gives the same answer and is harder to reason about. Write the "
            "honest version."
        ),
        ref=sol_longest_ones_k_flips,
        starter_py=_PY_ARR2 + (
            "def solve(a, k):\n"
            "    # TODO: longest window containing at most k zeros\n"
            "    return 0\n\nprint(solve(a, k))\n"
        ),
        starter_js=_JS_ARR2 + (
            "function solve(a, k) {\n"
            "  // TODO: longest window containing at most k zeros\n"
            "  return 0;\n}\n\nconsole.log(solve(a, k));\n"
        ),
        cases=[
            ("example", "Example 1", "8 2\n1 1 0 1 0 1 1 0\n"),
            ("example", "Example 2", "5 0\n1 1 0 1 1\n"),
            ("hidden", "Budget covers everything", "4 4\n0 0 0 0\n"),
            ("hidden", "All ones already", "3 1\n1 1 1\n"),
            ("hidden", "Single zero, no budget", "1 0\n0\n"),
        ],
        example_expl=[
            "Flipping the zeros at indices 2 and 4 joins indices 0–6 into a run of 7. The "
            "trailing zero is out of budget.",
            "With no flips the answer is the longest existing run of ones → 2.",
        ],
    ),

    # =======================================================================
    # binary-search — upper bound, a rotated array, and the answer space
    # =======================================================================
    dict(
        slug="count-occurrences-sorted", title="Count Occurrences in a Sorted Array",
        difficulty="Medium",
        topics=["Searching"], subtopics=["Binary Search", "Lower Bound"], companies=["Bloomberg"],
        description=(
            "Given a sorted array and a value `x`, print how many times `x` appears.\n\n"
            "Do it in O(log n) — two binary searches, not one search plus a linear walk "
            "outwards, which is O(n) when the array is all `x`.\n\n"
            "### Input\n- Line 1: integer `n`.\n- Line 2: `n` sorted integers, "
            "non-decreasing.\n- Line 3: the value `x`.\n\n### Output\nThe count, possibly 0."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i], x ≤ 10^9\na is sorted non-decreasing.",
        hints=[
            "You already have lower_bound: the first index with a[i] >= x.",
            "What you need as well is the first index with a[i] > x.",
            "For integers, `a[i] > x` is the same as `a[i] >= x + 1`.",
            "So the answer is lowerBound(x + 1) - lowerBound(x), with no second function to write.",
        ],
        opt=("O(log n)", "O(1)",
             "Two independent binary searches over the same array; neither depends on the "
             "other's result, so the cost is 2·log n, not log²n."),
        editorial=(
            "## The one thing this teaches\n**Upper bound is lower bound of the next value.** "
            "Writing a second search with `<=` instead of `<` also works, but it is a second "
            "loop with its own off-by-one, and the whole point of committing to one template is "
            "not having two.\n\n"
            "## Approach\n```java\nint lo = lowerBound(a, x);       // first index >= x\n"
            "int hi = lowerBound(a, x + 1);   // first index >= x+1, i.e. first index > x\n"
            "return hi - lo;\n```\n\n"
            "When `x` is absent both searches land on the same index and the difference is 0 — "
            "no \"not found\" branch is needed, which is the payoff of asking *where does it "
            "belong* rather than *is it there*.\n\n"
            "## The overflow you have to notice\n`x + 1` overflows when `x` is `Integer."
            "MAX_VALUE`. The constraints here stop at 10⁹ so it cannot bite, but say it out "
            "loud in an interview: the general fix is to compute the upper bound directly with "
            "a `<=` comparison, or to search in `long`.\n\n"
            "## Why not expand outwards from a found index?\nBecause `[7,7,7,…,7]` with `x = 7` "
            "makes that O(n), and the reason to binary search at all was to avoid O(n). This is "
            "a real interview trap: candidates find the element in log n and then throw the "
            "guarantee away in the next three lines."
        ),
        ref=sol_count_occurrences_sorted,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\nx = int(d[1 + n])\n\n"
            "def lower_bound(a, v):\n"
            "    # TODO: first index with a[i] >= v, using the half-open loop\n"
            "    return len(a)\n\n"
            "print(lower_bound(a, x + 1) - lower_bound(a, x))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], a = d.slice(1, 1 + n), x = d[1 + n];\n\n"
            "function lowerBound(a, v) {\n"
            "  // TODO: first index with a[i] >= v, using the half-open loop\n"
            "  return a.length;\n}\n\n"
            "console.log(lowerBound(a, x + 1) - lowerBound(a, x));\n"
        ),
        cases=[
            ("example", "Example 1", "7\n1 2 2 2 5 5 9\n2\n"),
            ("example", "Example 2", "5\n1 3 5 7 9\n4\n"),
            ("hidden", "Every element matches", "5\n7 7 7 7 7\n7\n"),
            ("hidden", "Match at the end", "4\n1 2 3 9\n9\n"),
            ("hidden", "Below the whole array", "3\n5 6 7\n1\n"),
        ],
        example_expl=[
            "`2` occupies indices 1, 2 and 3 → 3.",
            "`4` is absent; both bounds land on index 2 → 0.",
        ],
    ),
    dict(
        slug="rotated-array-minimum", title="Minimum of a Rotated Sorted Array",
        difficulty="Medium",
        topics=["Searching"], subtopics=["Binary Search"], companies=["Meta"],
        description=(
            "A sorted array of **distinct** integers was rotated left an unknown number of "
            "times, so `1 2 3 4 5` might arrive as `4 5 1 2 3`. Print the minimum in "
            "O(log n).\n\n"
            "### Input\n- Line 1: integer `n`.\n- Line 2: the `n` rotated values.\n\n"
            "### Output\nThe smallest value."
        ),
        constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9, all distinct\nThe array is a rotation of a sorted array (a rotation by 0 is allowed).",
        hints=[
            "The array is not sorted, so you cannot compare a[mid] with a target — there is no target.",
            "Compare a[mid] with the LAST element instead, and ask which side the minimum must be on.",
            "If a[mid] > a[hi], everything from lo to mid is above the rotation point: the minimum is right of mid.",
            "Otherwise mid could itself be the minimum, so hi = mid. Closed range [lo, hi], loop while lo < hi.",
        ],
        opt=("O(log n)", "O(1)",
             "One probe rules out half the range because \"is the minimum to my right?\" is a "
             "monotone question, even though the array itself is not sorted."),
        editorial=(
            "## The one thing this teaches\nBinary search needs a **monotone predicate**, not a "
            "sorted array. Here nothing is sorted end to end, but the question *\"is `a[mid]` in "
            "the left (higher) run?\"* is false…false, true…true as `mid` moves left, and that "
            "is all the loop requires.\n\n"
            "## Approach\n```java\nint lo = 0, hi = n - 1;\nwhile (lo < hi) {\n"
            "    int mid = lo + (hi - lo) / 2;\n"
            "    if (a[mid] > a[hi]) lo = mid + 1;   // mid is in the high run; min is right\n"
            "    else                hi = mid;       // mid may be the min itself\n}\n"
            "return a[lo];\n```\n\n"
            "## Why compare against `a[hi]` and not `a[lo]`\nBoth can be made to work, but "
            "`a[hi]` is the comparison that needs no special case for an unrotated array. "
            "Compare with `a[lo]` and `1 2 3` takes the wrong branch, because `a[mid] > a[lo]` "
            "is true in an array whose minimum is at index 0.\n\n"
            "This is a closed range `[lo, hi]` rather than the half-open `[lo, hi)` of lower "
            "bound, and that is not sloppiness: `hi` here is a real index whose value is read, "
            "not a one-past-the-end sentinel. Notice which one a problem needs before typing.\n\n"
            "## The duplicate case\nWith duplicates allowed, `a[mid] == a[hi]` tells you "
            "nothing — `[1,1,1,0,1]` and `[1,1,1,1,1]` are indistinguishable at the midpoint — "
            "and the worst case degrades to O(n). The statement says *distinct* so that the "
            "clean argument holds; being able to say why duplicates break it is the follow-up."
        ),
        ref=sol_rotated_array_minimum,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\n\n"
            "def solve(a):\n"
            "    # TODO: closed-range binary search comparing a[mid] with a[hi]\n"
            "    return a[0]\n\nprint(solve(a))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], a = d.slice(1, 1 + n);\n\n"
            "function solve(a) {\n"
            "  // TODO: closed-range binary search comparing a[mid] with a[hi]\n"
            "  return a[0];\n}\n\nconsole.log(solve(a));\n"
        ),
        cases=[
            ("example", "Example 1", "5\n4 5 1 2 3\n"),
            ("example", "Example 2", "3\n1 2 3\n"),
            ("hidden", "Rotated by one", "4\n2 3 4 1\n"),
            ("hidden", "Single element", "1\n7\n"),
            ("hidden", "Negatives, rotated near the end", "6\n3 9 -7 -4 -1 2\n"),
        ],
        example_expl=[
            "The rotation point sits between 5 and 1; the minimum is 1.",
            "A rotation by zero. The `a[hi]` comparison handles it with no special case.",
        ],
    ),
    dict(
        slug="min-ship-capacity", title="Smallest Capacity to Ship in D Days", difficulty="Medium",
        topics=["Searching"], subtopics=["Binary Search"], companies=["Amazon"],
        description=(
            "Packages arrive on a conveyor in a fixed order and must be shipped within `D` "
            "days. Each day you load packages **in order** onto one ship until the next would "
            "exceed its capacity. Find the smallest capacity that gets everything shipped in at "
            "most `D` days.\n\n"
            "### Input\n- Line 1: `n D`.\n- Line 2: `n` package weights, in conveyor order.\n\n"
            "### Output\nThe minimum capacity."
        ),
        constraints="1 ≤ D ≤ n ≤ 10^5\n1 ≤ w[i] ≤ 500",
        hints=[
            "You are not searching the array — you are searching the capacity, which is a number between two bounds.",
            "Write `daysNeeded(cap)` first: a greedy left-to-right pass that starts a new day when the next package will not fit.",
            "`daysNeeded` is non-increasing in cap, so `daysNeeded(cap) <= D` is a monotone predicate — exactly what binary search needs.",
            "Search `[max(w), sum(w)]`: below max(w) nothing ships at all, and sum(w) always ships in one day.",
        ],
        opt=("O(n log(Σw))", "O(1)",
             "Each feasibility check is one linear pass, and the capacity range is halved each "
             "time — about 26 checks for weights summing to 5 × 10⁷."),
        editorial=(
            "## The one thing this teaches\n**Binary search on the answer**, which is the "
            "technique the `first-true-predicate` warm-up was preparing you for. The array is "
            "not the search space; the *capacity* is, and the array is only used to evaluate the "
            "predicate.\n\n"
            "Three steps, always the same:\n\n"
            "1. **Name the answer space and its bounds.** Capacity is at least `max(w)` (a "
            "single package must fit) and at most `sum(w)` (one day for everything). Getting the "
            "low bound wrong — starting at 1 — makes `daysNeeded` loop forever or lie.\n"
            "2. **Write the feasibility check.** `daysNeeded(cap)` greedily fills each day; the "
            "greedy is optimal because deferring a package that fits can only cost days.\n"
            "3. **Argue monotonicity.** A bigger ship never needs more days. That is what makes "
            "`feasible` an `FFF…TTT` predicate, and without it binary search is invalid however "
            "tidy the loop looks.\n\n"
            "## Approach\n```java\nint lo = max(w), hi = sum(w);\nwhile (lo < hi) {\n"
            "    int mid = lo + (hi - lo) / 2;\n"
            "    if (daysNeeded(mid) > D) lo = mid + 1;   // infeasible, go higher\n"
            "    else                     hi = mid;       // feasible, mid may be the answer\n}\n"
            "return lo;\n```\n\n"
            "## How to spot it in a prompt\n\"Minimum capacity / maximum minimum / smallest "
            "speed / largest gap, such that …\" — an optimisation over a single number with a "
            "checkable condition. If you can write `boolean works(x)` and convince yourself it "
            "is monotone, the rest is this loop. The hard part is never the search."
        ),
        ref=sol_min_ship_capacity,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n, D = int(d[0]), int(d[1])\n"
            "w = list(map(int, d[2:2 + n]))\n\n"
            "def days_needed(w, cap):\n"
            "    # TODO: greedy left-to-right fill; return the number of days\n"
            "    return len(w)\n\n"
            "def solve(w, D):\n"
            "    # TODO: binary search the capacity in [max(w), sum(w)]\n"
            "    return sum(w)\n\nprint(solve(w, D))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], D = d[1], w = d.slice(2, 2 + n);\n\n"
            "function daysNeeded(w, cap) {\n"
            "  // TODO: greedy left-to-right fill; return the number of days\n"
            "  return w.length;\n}\n\n"
            "function solve(w, D) {\n"
            "  // TODO: binary search the capacity in [max(w), sum(w)]\n"
            "  return w.reduce((a, b) => a + b, 0);\n}\n\nconsole.log(solve(w, D));\n"
        ),
        cases=[
            ("example", "Example 1", "10 5\n1 2 3 4 5 6 7 8 9 10\n"),
            ("example", "Example 2", "3 3\n3 2 2\n"),
            ("hidden", "One day for everything", "4 1\n1 2 3 4\n"),
            ("hidden", "One package per day", "5 5\n5 4 3 2 1\n"),
            ("hidden", "Uniform weights", "6 3\n7 7 7 7 7 7\n"),
        ],
        example_expl=[
            "Capacity 15 ships as 1-5 / 6-7 / 8 / 9 / 10 in five days; 14 needs six.",
            "Three days for three packages, so the capacity only has to hold the largest → 3.",
        ],
    ),

    # =======================================================================
    # graph-traversal — multi-source, level-by-level, and directed
    # =======================================================================
    dict(
        slug="rotting-oranges", title="Minutes Until Everything Rots", difficulty="Medium",
        topics=["Graphs", "Matrix"], subtopics=["BFS", "Grid"], companies=["Amazon"],
        description=(
            "A grid holds `R` (rotten), `F` (fresh) and `.` (empty). Every minute, each rotten "
            "cell rots its four orthogonal fresh neighbours. Print the number of minutes until "
            "no fresh cell remains, or `-1` if some fresh cell can never rot.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the grid.\n\n"
            "### Output\nThe number of minutes, `0` if there is nothing fresh to begin with, or "
            "`-1`."
        ),
        constraints="1 ≤ H, W ≤ 200\nEach character is `R`, `F` or `.`",
        hints=[
            "Rot spreads one step per minute from every rotten cell at once — that is BFS with many starting points.",
            "Push EVERY rotten cell into the queue before the loop starts, each at time 0.",
            "Then the queue is still in non-decreasing time order, so the answer is the largest time you dequeue.",
            "Count fresh cells up front and decrement as you rot them; anything left over is unreachable → -1.",
        ],
        opt=("O(H·W)", "O(H·W)",
             "Each cell is enqueued at most once. Running a separate BFS per rotten cell would "
             "be O((H·W)²) and is the mistake this problem exists to prevent."),
        editorial=(
            "## The one thing this teaches\n**Multi-source BFS.** The invariant that makes BFS "
            "give shortest distances — the queue holds cells in non-decreasing distance order — "
            "does not care how many cells you seeded it with, only that they all started at the "
            "same distance. So \"distance from the *nearest* source\" costs exactly one BFS, not "
            "one per source.\n\n"
            "## Approach\n```java\nDeque<int[]> q = new ArrayDeque<>();\nint fresh = 0;\n"
            "for each cell:\n    if (R) q.add(new int[]{i, j, 0});\n    else if (F) fresh++;\n\n"
            "int last = 0;\nwhile (!q.isEmpty()) {\n    int[] cur = q.poll();\n"
            "    last = Math.max(last, cur[2]);\n"
            "    for each fresh neighbour: mark it R, fresh--, q.add({ni, nj, cur[2] + 1});\n}\n"
            "return fresh > 0 ? -1 : last;\n```\n\n"
            "**Mark on enqueue**, as always, or a cell adjacent to two rotten cells is processed "
            "twice.\n\n"
            "## The two edge cases, and why they differ\n- **No fresh cells at all** → `0`. "
            "Nothing needs to happen, so zero minutes have to pass. Falling out of the loop with "
            "`last = 0` gets this right for free.\n"
            "- **A fresh cell walled off by `.`** → `-1`. The queue empties with `fresh > 0`. "
            "You cannot detect this from the time alone, which is why the count is kept "
            "separately.\n\n"
            "## Carrying time in the queue, or by levels\nThe alternative is to drain the queue "
            "one *level* at a time — record `q.size()`, pop exactly that many, then increment "
            "the minute. Both are correct; the level form generalises better to \"how many are "
            "within k steps\" and the per-node form is harder to get wrong. Write both once."
        ),
        ref=sol_rotting_oranges,
        starter_py=(
            "import sys\nfrom collections import deque\n\n"
            "L = sys.stdin.read().split('\\n')\n"
            "H, W = map(int, L[0].split())\n"
            "grid = [list(L[1 + i]) for i in range(H)]\n\n"
            "def solve(H, W, grid):\n"
            "    # TODO: seed the queue with EVERY 'R' at time 0, then BFS\n"
            "    return -1\n\nprint(solve(H, W, grid))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
            "const [H, W] = L[0].split(/\\s+/).map(Number);\n"
            "const grid = [];\nfor (let i = 0; i < H; i++) grid.push(L[1 + i].split(''));\n\n"
            "function solve(H, W, grid) {\n"
            "  // TODO: seed the queue with EVERY 'R' at time 0, then BFS\n"
            "  return -1;\n}\n\nconsole.log(solve(H, W, grid));\n"
        ),
        cases=[
            ("example", "Example 1", "3 3\nRFF\nFF.\n.FF\n"),
            ("example", "Example 2", "2 3\nRF.\n..F\n"),
            ("hidden", "Nothing fresh", "2 2\nR.\n.R\n"),
            ("hidden", "Two sources meet in the middle", "1 5\nRFFFR\n"),
            ("hidden", "Fresh but no rot at all", "1 2\nFF\n"),
        ],
        example_expl=[
            "The rot spreads outwards from the single source and reaches the far corner after 4 "
            "minutes.",
            "The fresh cell at the bottom-right has only empty cells beside and above it, so "
            "nothing ever reaches it → -1. The minute count alone cannot tell you that, which "
            "is why the fresh tally is kept separately.",
        ],
    ),
    dict(
        slug="reachable-within-k", title="Nodes Reachable Within K Steps", difficulty="Medium",
        topics=["Graphs"], subtopics=["BFS", "Connected Components"], companies=["Google"],
        description=(
            "Given an undirected graph and a start node `s`, count the nodes reachable from `s` "
            "in at most `K` edges. Do not count `s` itself.\n\n"
            "### Input\n- Line 1: `n m K`.\n- Line 2: the start node `s`.\n"
            "- Next `m` lines: `u v` — an undirected edge.\n\n"
            "### Output\nThe count of other nodes within distance `K`."
        ),
        constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 2·10^4\n0 ≤ K ≤ n\n0 ≤ s, u, v < n",
        hints=[
            "BFS reaches nodes in non-decreasing distance order, so you can stop early rather than exploring everything.",
            "Keep the distance per node, seeded at -1 and set to dist[u] + 1 on enqueue.",
            "Do not expand a node whose distance is already K — its neighbours would be at K + 1.",
            "Count nodes with 0 <= dist <= K, then subtract one for the start itself.",
        ],
        opt=("O(n + m)", "O(n + m)",
             "Worst case is a full traversal, but the distance cap lets the search stop at the "
             "frontier — on a large graph with small K it touches only the local neighbourhood."),
        editorial=(
            "## The one thing this teaches\n**BFS as a distance-limited search.** The queue is "
            "already ordered by distance, so \"stop at K\" is not a filter applied afterwards — "
            "it is a `continue` at the moment of expansion, and it is what makes the cost "
            "proportional to the neighbourhood rather than the graph.\n\n"
            "## Approach\n```java\nint[] dist = new int[n];\nArrays.fill(dist, -1);\n"
            "dist[s] = 0;\nDeque<Integer> q = new ArrayDeque<>();\nq.add(s);\n"
            "while (!q.isEmpty()) {\n    int u = q.poll();\n"
            "    if (dist[u] == K) continue;        // its neighbours would be K+1 away\n"
            "    for (int v : g.get(u)) if (dist[v] < 0) { dist[v] = dist[u] + 1; q.add(v); }\n}\n"
            "```\n\n"
            "The guard is `dist[u] == K`, tested when `u` is *dequeued*. Testing it on the "
            "neighbour instead (`if (dist[u] + 1 <= K)`) is equivalent and arguably clearer; "
            "what is wrong is enqueueing first and filtering the count at the end, because then "
            "the search has already walked the whole graph and K bought you nothing.\n\n"
            "## `K = 0`\nThe answer is 0: the start is excluded and nothing else is within zero "
            "edges. The guard handles it without a special case, which is a good check that the "
            "boundary is in the right place.\n\n"
            "## The level-by-level alternative\nDrain the queue `size()` at a time and stop "
            "after K rounds. It needs no distance array — a `boolean[] seen` and a running "
            "counter suffice — and it is the form to reach for when the question is about levels "
            "rather than individual distances (\"print each level\", \"the width of the "
            "widest\")."
        ),
        ref=sol_reachable_within_k,
        starter_py=(
            "import sys\nfrom collections import deque\n\n"
            "L = sys.stdin.read().strip().split('\\n')\n"
            "n, m, K = map(int, L[0].split())\n"
            "s = int(L[1])\n"
            "g = [[] for _ in range(n)]\n"
            "for i in range(m):\n"
            "    u, v = map(int, L[2 + i].split())\n    g[u].append(v)\n    g[v].append(u)\n\n"
            "def solve(n, g, s, K):\n"
            "    # TODO: BFS, refusing to expand a node already K steps away\n"
            "    return 0\n\nprint(solve(n, g, s, K))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const [n, m, K] = L[0].split(/\\s+/).map(Number);\n"
            "const s = Number(L[1]);\n"
            "const g = Array.from({ length: n }, () => []);\n"
            "for (let i = 0; i < m; i++) {\n"
            "  const [u, v] = L[2 + i].split(/\\s+/).map(Number);\n"
            "  g[u].push(v); g[v].push(u);\n}\n\n"
            "function solve(n, g, s, K) {\n"
            "  // TODO: BFS, refusing to expand a node already K steps away\n"
            "  return 0;\n}\n\nconsole.log(solve(n, g, s, K));\n"
        ),
        cases=[
            ("example", "Example 1", "6 5 2\n0\n0 1\n1 2\n2 3\n3 4\n0 5\n"),
            ("example", "Example 2", "4 2 0\n0\n0 1\n1 2\n"),
            ("hidden", "Disconnected start", "3 1 5\n2\n0 1\n"),
            ("hidden", "Star graph", "5 4 1\n0\n0 1\n0 2\n0 3\n0 4\n"),
            ("hidden", "K larger than the graph", "4 3 99\n1\n0 1\n1 2\n2 3\n"),
        ],
        example_expl=[
            "Within two edges of 0: nodes 1, 5 (distance 1) and 2 (distance 2) → 3. Node 3 is "
            "three edges away.",
            "K is 0, so nothing but the start is in range → 0.",
        ],
    ),
    dict(
        slug="directed-path-exists", title="Path Exists in a Directed Graph", difficulty="Medium",
        topics=["Graphs"], subtopics=["BFS", "Cycle Detection"], companies=["Microsoft"],
        description=(
            "Given a **directed** graph, decide whether a path exists from `s` to `t`. Print "
            "`YES` or `NO`. A node always reaches itself.\n\n"
            "### Input\n- Line 1: `n m`.\n- Line 2: `s t`.\n- Next `m` lines: `u v` — a "
            "directed edge `u → v`.\n\n### Output\n`YES` or `NO`."
        ),
        constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 5·10^4\n0 ≤ s, t, u, v < n\nThe graph may contain cycles and self-loops.",
        hints=[
            "Build the adjacency list with each edge in ONE direction only — that single character is the whole difference from the undirected version.",
            "Either BFS or DFS works; reachability does not care about distance.",
            "Mark a node seen when you push it, so a cycle cannot make the search loop forever.",
            "s reaches t when s == t, even with no edges at all.",
        ],
        opt=("O(n + m)", "O(n + m)",
             "Each node is pushed once and each directed edge examined once; the visited set is "
             "what bounds it in the presence of cycles."),
        editorial=(
            "## The one thing this teaches\nThe undirected habits break, and they break "
            "quietly:\n\n"
            "- **One-way edges.** Adding `g[v].add(u)` as well — the reflex from every "
            "undirected problem — makes the answer wrong rather than slow, and on many test "
            "cases it is *still right*, which is the worst kind of bug.\n"
            "- **Reachability is not symmetric.** `s → t` can hold while `t → s` does not. "
            "Sanity-check with an input where swapping `s` and `t` flips the answer.\n"
            "- **Cycles are not a special case.** The visited set already handles them; there is "
            "nothing to detect. Reaching for cycle detection here is a sign of reasoning about "
            "the graph rather than about the search.\n\n"
            "## Approach\n```java\nboolean[] seen = new boolean[n];\n"
            "Deque<Integer> st = new ArrayDeque<>();\nst.push(s);\nseen[s] = true;\n"
            "while (!st.isEmpty()) {\n    int u = st.pop();\n    if (u == t) return true;\n"
            "    for (int v : g.get(u)) if (!seen[v]) { seen[v] = true; st.push(v); }\n}\n"
            "return s == t;\n```\n\n"
            "An explicit stack rather than recursion, deliberately: with n = 10⁴ a chain-shaped "
            "graph is 10⁴ frames deep, which Java survives and a 10⁵-node version would not. "
            "Knowing when to unroll the recursion is part of the technique.\n\n"
            "## Why `return s == t` at the end\nIf `s == t` the loop returns true immediately on "
            "the first pop, so the trailing return is only reached when the search exhausted "
            "everything — but writing it as `s == t` rather than `false` documents the "
            "convention the statement fixes, and costs nothing."
        ),
        ref=sol_directed_path_exists,
        starter_py=(
            "import sys\n\nL = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, L[0].split())\n"
            "s, t = map(int, L[1].split())\n"
            "g = [[] for _ in range(n)]\n"
            "for i in range(m):\n"
            "    u, v = map(int, L[2 + i].split())\n    g[u].append(v)   # one direction only\n\n"
            "def solve(n, g, s, t):\n"
            "    # TODO: DFS or BFS from s with a visited set; return 'YES' or 'NO'\n"
            "    return 'NO'\n\nprint(solve(n, g, s, t))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const [n, m] = L[0].split(/\\s+/).map(Number);\n"
            "const [s, t] = L[1].split(/\\s+/).map(Number);\n"
            "const g = Array.from({ length: n }, () => []);\n"
            "for (let i = 0; i < m; i++) {\n"
            "  const [u, v] = L[2 + i].split(/\\s+/).map(Number);\n"
            "  g[u].push(v); // one direction only\n}\n\n"
            "function solve(n, g, s, t) {\n"
            "  // TODO: DFS or BFS from s with a visited set; return 'YES' or 'NO'\n"
            "  return 'NO';\n}\n\nconsole.log(solve(n, g, s, t));\n"
        ),
        cases=[
            ("example", "Example 1", "4 3\n0 3\n0 1\n1 2\n2 3\n"),
            ("example", "Example 2", "4 3\n3 0\n0 1\n1 2\n2 3\n"),
            ("hidden", "Start equals target, no edges", "2 0\n1 1\n"),
            ("hidden", "Cycle that does not reach the target", "4 3\n0 3\n0 1\n1 2\n2 0\n"),
            ("hidden", "Self loop on the path", "3 3\n0 2\n0 0\n0 1\n1 2\n"),
        ],
        example_expl=[
            "`0 → 1 → 2 → 3` → YES.",
            "The same graph, asked backwards. Every edge points the wrong way → NO. Treating "
            "the edges as undirected would answer YES.",
        ],
    ),

    # =======================================================================
    # greedy — a ratio, a rule that is wrong, a reset, and a pairing
    # =======================================================================
    dict(
        slug="fractional-knapsack", title="Fractional Knapsack", difficulty="Medium",
        topics=["Greedy"], subtopics=["Sorting"], companies=["Bloomberg"],
        description=(
            "You have a sack of capacity `C` and `n` items, each with a value and a weight. "
            "Items are **divisible**: you may take any fraction of one and get that fraction of "
            "its value. Maximise the value you carry.\n\n"
            "To keep the answer an exact integer, print the maximum value **multiplied by 100 "
            "and rounded down**.\n\n"
            "### Input\n- Line 1: `n C`.\n- Next `n` lines: `value weight`.\n\n"
            "### Output\nA single integer: ⌊100 × maximum value⌋."
        ),
        constraints="1 ≤ n ≤ 10^5\n1 ≤ C ≤ 10^9\n1 ≤ value ≤ 10^6\n1 ≤ weight ≤ 10^6",
        hints=[
            "Taking whole items in value order is wrong — a valuable but heavy item can crowd out two better ones.",
            "What you are really buying is value per unit of weight.",
            "Sort by the ratio value/weight, descending, and fill greedily.",
            "Compare ratios as `v1 * w2` vs `v2 * w1` to avoid floating point entirely.",
        ],
        opt=("O(n log n)", "O(n)",
             "The sort dominates; the fill is one pass. No dynamic programming is needed, which "
             "is the entire difference from the 0/1 version."),
        editorial=(
            "## The one thing this teaches\nThe greedy rule is over the **right quantity**. "
            "\"Most valuable first\" and \"lightest first\" are both wrong; \"best value per "
            "kilo first\" is right, and noticing that the sort key is a *derived* quantity "
            "rather than a given column is most of the difficulty.\n\n"
            "## Why it is correct\nAn exchange argument. Suppose an optimal solution leaves some "
            "capacity filled with a lower-ratio item while a higher-ratio item is only partly "
            "taken. Swap an ε of weight between them: the value strictly increases, so that "
            "solution was not optimal. Therefore an optimal solution takes items in "
            "non-increasing ratio order — which is exactly what the greedy produces.\n\n"
            "**Divisibility is what the argument needs.** You must be able to move an arbitrary "
            "ε of weight.\n\n"
            "## The contrast that matters\nMake the items indivisible and the exchange argument "
            "dies — there is no ε to move — and the greedy is provably wrong. Capacity 10 with "
            "items `(v=7,w=6)`, `(v=5,w=5)`, `(v=5,w=5)`: the best ratio is the first item at "
            "1.17, so greedy takes it and then cannot fit either of the others, finishing at 7. "
            "The optimum is the two w=5 items, for 10. 0/1 knapsack is a DP, and the boundary "
            "between the two is the standard interview follow-up. Be able to say *which "
            "property* you lost.\n\n"
            "## On the integer output\nThe ×100 is a judging convenience, not part of the "
            "algorithm: floating-point totals would need a tolerance and would hide real "
            "precision bugs. Accumulate `value * 100 * take / weight` in a `long` with integer "
            "division and compare ratios by cross-multiplication, and the whole problem stays "
            "exact."
        ),
        ref=sol_fractional_knapsack,
        starter_py=(
            "import sys\n\nL = sys.stdin.read().strip().split('\\n')\n"
            "n, C = map(int, L[0].split())\n"
            "items = [tuple(map(int, L[1 + i].split())) for i in range(n)]\n\n"
            "def solve(items, C):\n"
            "    # TODO: sort by value/weight descending, then fill; return floor(100 * value)\n"
            "    return 0\n\nprint(solve(items, C))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const [n, C] = L[0].split(/\\s+/).map(Number);\n"
            "const items = [];\n"
            "for (let i = 0; i < n; i++) items.push(L[1 + i].split(/\\s+/).map(Number));\n\n"
            "function solve(items, C) {\n"
            "  // TODO: sort by value/weight descending, then fill; return floor(100 * value)\n"
            "  return 0;\n}\n\nconsole.log(solve(items, C));\n"
        ),
        cases=[
            ("example", "Example 1", "3 5\n60 10\n100 20\n120 30\n"),
            ("example", "Example 2", "2 10\n10 1\n1 10\n"),
            ("hidden", "Capacity exceeds every item", "2 100\n5 1\n7 2\n"),
            ("hidden", "Single item, partly taken", "1 3\n100 10\n"),
            ("hidden", "Equal ratios", "3 4\n3 3\n2 2\n2 2\n"),
        ],
        example_expl=[
            "Ratios are 6, 5 and 4 per unit. Taking 5 units of the first item gives value 30 → "
            "3000.",
            "Take the whole first item (value 10, weight 1) and 9 units of the second (value "
            "0.9) → 10.9 → 1090.",
        ],
    ),
    dict(
        slug="greedy-coin-change", title="Where Greedy Coin Change Goes Wrong",
        difficulty="Medium",
        topics=["Greedy"], subtopics=["Dynamic Programming"], companies=["Adobe"],
        description=(
            "Given coin denominations and an amount, print **two** numbers: the number of coins "
            "the greedy algorithm uses (repeatedly take the largest coin that fits), and the "
            "true minimum. Print `-1` in place of either when it cannot make the amount at "
            "all.\n\n"
            "The point of printing both is that on some coin systems they differ, and on the "
            "ones you grew up with they never do.\n\n"
            "### Input\n- Line 1: `n amount`.\n- Line 2: `n` distinct denominations.\n\n"
            "### Output\nTwo space-separated integers: `greedyCount trueMinimum`."
        ),
        constraints="1 ≤ n ≤ 20\n0 ≤ amount ≤ 10^4\n1 ≤ coin ≤ 10^4, all distinct",
        hints=[
            "Greedy: sort the coins descending, take `left / coin` of each, then `left %= coin`. If anything is left over, greedy failed.",
            "True minimum: a 1-D DP over amounts, dp[a] = 1 + min over coins of dp[a - coin].",
            "dp[0] = 0, and an unreachable amount stays at infinity — print -1 for it.",
            "Greedy can fail even when a solution exists: try coins {1, 3, 4} and amount 6.",
        ],
        opt=("O(n log n + n·amount)", "O(amount)",
             "The greedy pass is dominated by the sort; the DP fills `amount` cells, each "
             "considering `n` coins. There is no faster exact method for arbitrary "
             "denominations."),
        editorial=(
            "## The one thing this teaches\n**A greedy rule is a claim that needs proof, and "
            "this one is false.** Coins {1, 3, 4}, amount 6: greedy takes 4, then 1, then 1 — "
            "three coins. The optimum is 3 + 3 — two. Nothing about the greedy loop is buggy; "
            "the *rule* is wrong.\n\n"
            "This is the most useful negative example in the unit, because greedy feels "
            "obviously right here. It is obviously right on {1, 5, 10, 25}, and every coin "
            "system you have handled is deliberately designed so that it is.\n\n"
            "## The two algorithms\n```java\n// greedy\nArrays.sort(coins);  // then walk it backwards\n"
            "int left = amount, greedy = 0;\n"
            "for (int i = n - 1; i >= 0; i--) { greedy += left / coins[i]; left %= coins[i]; }\n"
            "if (left != 0) greedy = -1;\n\n// true minimum\n"
            "int[] dp = new int[amount + 1];\nArrays.fill(dp, INF);\ndp[0] = 0;\n"
            "for (int a = 1; a <= amount; a++)\n    for (int c : coins)\n"
            "        if (c <= a && dp[a - c] != INF) dp[a] = Math.min(dp[a], dp[a - c] + 1);\n"
            "```\n\n"
            "## Greedy fails in two different ways\nBoth are worth distinguishing:\n\n"
            "1. **Suboptimal** — it makes the amount, with too many coins. {1,3,4} and 6.\n"
            "2. **Stuck** — it fails to make an amount that is makeable. Coins {3, 4}, amount 6: "
            "greedy takes 4 and cannot finish with 2, though 3 + 3 works. Greedy commits and "
            "cannot reconsider; the DP considers every last coin, which is precisely the "
            "difference.\n\n"
            "## When *is* greedy safe?\nOn a **canonical** coin system — and deciding whether a "
            "system is canonical is itself non-trivial (it can be checked in polynomial time, "
            "but not by inspection). The practical lesson: unless the problem hands you a coin "
            "system you can verify, greedy on coin change is a wrong answer waiting for the "
            "right test case."
        ),
        ref=sol_greedy_coin_change,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n, amount = int(d[0]), int(d[1])\n"
            "coins = list(map(int, d[2:2 + n]))\n\n"
            "def greedy_count(coins, amount):\n"
            "    # TODO: largest coin first; -1 if it gets stuck\n"
            "    return -1\n\n"
            "def true_min(coins, amount):\n"
            "    # TODO: 1-D DP over amounts; -1 if unreachable\n"
            "    return -1\n\n"
            "print(greedy_count(coins, amount), true_min(coins, amount))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], amount = d[1], coins = d.slice(2, 2 + n);\n\n"
            "function greedyCount(coins, amount) {\n"
            "  // TODO: largest coin first; -1 if it gets stuck\n  return -1;\n}\n\n"
            "function trueMin(coins, amount) {\n"
            "  // TODO: 1-D DP over amounts; -1 if unreachable\n  return -1;\n}\n\n"
            "console.log(greedyCount(coins, amount) + ' ' + trueMin(coins, amount));\n"
        ),
        cases=[
            ("example", "Example 1", "3 6\n1 3 4\n"),
            ("example", "Example 2", "4 63\n1 5 10 25\n"),
            ("hidden", "Greedy gets stuck where the optimum exists", "2 6\n3 4\n"),
            ("hidden", "Amount zero", "2 0\n2 5\n"),
            ("hidden", "Neither can make it", "2 7\n4 6\n"),
        ],
        example_expl=[
            "Greedy takes 4 + 1 + 1 = three coins; 3 + 3 is two. The rule is wrong, not the "
            "code.",
            "A canonical system: 25+25+10+1+1+1 is both the greedy answer and the optimum → 6 6.",
        ],
    ),
    dict(
        slug="gas-station-start", title="Gas Station Starting Point", difficulty="Medium",
        topics=["Greedy"], subtopics=["Counting"], companies=["Amazon"],
        description=(
            "There are `n` stations arranged in a circle. At station `i` you gain `gas[i]` fuel, "
            "and driving from `i` to `i+1` costs `cost[i]`. Starting with an empty tank, print "
            "the index of a station you can start from and complete the full loop, or `-1` if "
            "none exists. If several work, print the smallest such index.\n\n"
            "### Input\n- Line 1: integer `n`.\n- Line 2: `n` values `gas[i]`.\n"
            "- Line 3: `n` values `cost[i]`.\n\n### Output\nThe starting index, or `-1`."
        ),
        constraints="1 ≤ n ≤ 10^5\n0 ≤ gas[i], cost[i] ≤ 10^4\nA valid start, when one exists, is unique.",
        hints=[
            "First decide whether ANY start works: compare the total gas with the total cost.",
            "Trying every start is O(n²). One pass is enough — but you need to know what to do when the tank goes negative.",
            "If the tank drops below zero partway through a run starting at `start`, no station in that run can be the answer.",
            "So reset: `start = i + 1`, `tank = 0`, and never look back.",
        ],
        opt=("O(n)", "O(1)",
             "One pass with a running tank and a candidate start. Each station is visited once "
             "because a failed run's stations are eliminated wholesale rather than retried."),
        editorial=(
            "## The one thing this teaches\n**A greedy that discards work, with an argument for "
            "why the discarded work was doomed.** The one-pass loop is four lines; the reason it "
            "is correct is the exercise.\n\n"
            "## Approach\n```java\nif (sum(gas) < sum(cost)) return -1;\n"
            "int start = 0, tank = 0;\nfor (int i = 0; i < n; i++) {\n"
            "    tank += gas[i] - cost[i];\n"
            "    if (tank < 0) { start = i + 1; tank = 0; }\n}\nreturn start;\n```\n\n"
            "## Why the reset is safe\nSuppose starting at `start` the tank first goes negative "
            "arriving at station `i + 1`. Then for any `j` with `start ≤ j ≤ i`, starting at `j` "
            "also fails before `i + 1` — because the run from `start` to `j` had a "
            "**non-negative** partial sum (otherwise the tank would have gone negative earlier), "
            "so starting at `j` arrives at `i` with *no more* fuel than starting at `start` did. "
            "Every station in the failed run is therefore eliminated, and jumping to `i + 1` "
            "skips them all legitimately.\n\n"
            "## Why the total check is separate\nThe loop alone cannot distinguish \"the answer "
            "is `start`\" from \"nothing works and `start` is simply where the last reset "
            "happened\". If total gas ≥ total cost a valid start is guaranteed to exist, and the "
            "loop's final `start` is it. Two facts, two lines — collapsing them is where wrong "
            "solutions come from.\n\n"
            "## Relation to Kadane\nThis is the same shape as the maximum-subarray reset: a "
            "running value, and a rule for abandoning a prefix that can no longer help. Seeing "
            "the two as one idea is worth more than remembering either."
        ),
        ref=sol_gas_station_start,
        starter_py=(
            "import sys\n\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\n"
            "gas = list(map(int, L[1].split()))\n"
            "cost = list(map(int, L[2].split()))\n\n"
            "def solve(gas, cost):\n"
            "    # TODO: total check first, then one pass with a reset\n"
            "    return -1\n\nprint(solve(gas, cost))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const n = Number(L[0]);\n"
            "const gas = L[1].split(/\\s+/).map(Number);\n"
            "const cost = L[2].split(/\\s+/).map(Number);\n\n"
            "function solve(gas, cost) {\n"
            "  // TODO: total check first, then one pass with a reset\n"
            "  return -1;\n}\n\nconsole.log(solve(gas, cost));\n"
        ),
        cases=[
            ("example", "Example 1", "5\n1 2 3 4 5\n3 4 5 1 2\n"),
            ("example", "Example 2", "3\n2 3 4\n3 4 3\n"),
            ("hidden", "Start at zero", "2\n5 1\n1 5\n"),
            ("hidden", "Single station, exactly enough", "1\n5\n5\n"),
            ("hidden", "Single station, not enough", "1\n1\n5\n"),
        ],
        example_expl=[
            "Starting at index 3 the tank runs 3, 6, 4, 2, 0 — never negative. Every "
            "earlier start strands you.",
            "Total gas is 9 and total cost is 10, so no loop is possible → -1.",
        ],
    ),
    dict(
        slug="boats-to-save-people", title="Fewest Boats", difficulty="Medium",
        topics=["Greedy"], subtopics=["Two Pointers", "Sorting"], companies=["Meta"],
        description=(
            "Each boat carries **at most two** people and at most `limit` total weight. Every "
            "person's weight is at most `limit`. Print the fewest boats needed to carry "
            "everyone.\n\n"
            "### Input\n- Line 1: `n limit`.\n- Line 2: `n` weights.\n\n"
            "### Output\nThe minimum number of boats."
        ),
        constraints="1 ≤ n ≤ 10^5\n1 ≤ limit ≤ 10^5\n1 ≤ w[i] ≤ limit",
        hints=[
            "The heaviest person must travel; the only question is whether anyone rides with them.",
            "If anyone can ride with the heaviest person, the lightest person can.",
            "So sort, and pair the two ends: if w[i] + w[j] fits, both go; otherwise j goes alone.",
            "Either way `j` decreases every iteration — that is what makes it one pass.",
        ],
        opt=("O(n log n)", "O(1)",
             "The sort dominates; the pairing is a single two-pointer pass with no extra "
             "storage."),
        editorial=(
            "## The one thing this teaches\n**Greedy plus two pointers**, and an exchange "
            "argument that reads as obvious once stated: if the heaviest person can share a boat "
            "with *anybody*, they can share it with the lightest. So there is no reason to "
            "consider any other partner — pairing them costs nothing and saves a boat.\n\n"
            "## Approach\n```java\nArrays.sort(w);\nint i = 0, j = n - 1, boats = 0;\n"
            "while (i <= j) {\n    if (w[i] + w[j] <= limit) i++;   // the lightest rides along\n"
            "    j--;                                 // the heaviest goes either way\n"
            "    boats++;\n}\n```\n\n"
            "Note that `j--` and `boats++` are **outside** the branch. The heaviest person "
            "leaves on this boat regardless; the only decision is whether the lightest joins "
            "them. Putting either inside the `if` is the bug, and it is easy to make while "
            "thinking of the code as \"pair them up\" rather than \"the heaviest departs\".\n\n"
            "`i <= j` rather than `i < j`, so the last person left in the middle gets a boat.\n\n"
            "## Why not sort and fill greedily from the heavy end?\n\"Give the heaviest person a "
            "boat, then add the heaviest person who still fits\" is also correct here, and it is "
            "O(n log n) with a more complicated inner search. The two-pointer form is worth "
            "preferring because it makes the invariant visible: everything outside `[i, j]` is "
            "already on a boat.\n\n"
            "## The generalisation that breaks it\nAllow **three** people per boat and this "
            "greedy stops being optimal — the pairing argument gives you nothing about triples, "
            "and the problem becomes bin packing, which is NP-hard. \"At most two\" is not a "
            "simplification of the statement; it is the reason a polynomial answer exists."
        ),
        ref=sol_boats_to_save_people,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n, limit = int(d[0]), int(d[1])\n"
            "w = list(map(int, d[2:2 + n]))\n\n"
            "def solve(w, limit):\n"
            "    # TODO: sort, then pair the two ends\n"
            "    return len(w)\n\nprint(solve(w, limit))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], limit = d[1], w = d.slice(2, 2 + n);\n\n"
            "function solve(w, limit) {\n"
            "  // TODO: sort, then pair the two ends\n"
            "  return w.length;\n}\n\nconsole.log(solve(w, limit));\n"
        ),
        cases=[
            ("example", "Example 1", "4 3\n3 2 2 1\n"),
            ("example", "Example 2", "5 5\n1 2 3 4 5\n"),
            ("hidden", "Nobody can share", "3 4\n4 4 4\n"),
            ("hidden", "Everybody pairs", "4 10\n1 1 1 1\n"),
            ("hidden", "Odd count, middle rides alone", "3 4\n1 3 4\n"),
        ],
        example_expl=[
            "The 3 sails alone (nobody fits beside it), then 1 pairs with a 2, and the last "
            "2 sails alone → 3 boats.",
            "`(1,4)`, `(2,3)` and `(5)` → 3 boats.",
        ],
    ),
]

DEFS += DEPTH_DEFS


JAVA_STARTERS.update({
    "subarray-sum-at-most": _java_main(
        "        int n = sc.nextInt();\n"
        "        long S = sc.nextLong();\n"
        "        int[] a = new int[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
        "        long total = 0, window = 0;\n"
        "        int left = 0;\n"
        "        // TODO: for each r, shrink left while window > S, then add r - left + 1\n"
        "        System.out.println(total);\n"
    ),
    "longest-k-distinct": _java_main(
        "        String s = sc.next();\n"
        "        int K = sc.nextInt();\n"
        "        Map<Character, Integer> count = new HashMap<>();\n"
        "        int left = 0, best = 0;\n"
        "        // TODO: grow r; while count.size() > K shrink left (and REMOVE zero counts)\n"
        "        System.out.println(best);\n"
    ),
    "min-window-sum-atleast": _java_main(
        "        int n = sc.nextInt();\n"
        "        long S = sc.nextLong();\n"
        "        int[] a = new int[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
        "        long window = 0;\n"
        "        int left = 0, best = Integer.MAX_VALUE;\n"
        "        // TODO: grow r; while the window is STILL valid, record then shrink\n"
        "        System.out.println(best == Integer.MAX_VALUE ? 0 : best);\n"
    ),
    "longest-ones-k-flips": _java_main(
        _J_ARR2
        + "        int left = 0, zeros = 0, best = 0;\n"
        "        // TODO: longest window containing at most k zeros\n"
        "        System.out.println(best);\n"
    ),
    "count-occurrences-sorted": (
        "import java.util.*;\n\n"
        "public class Main {\n"
        "    static int lowerBound(int[] a, int v) {\n"
        "        // TODO: first index with a[i] >= v, using the half-open loop\n"
        "        return a.length;\n"
        "    }\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt();\n"
        "        int[] a = new int[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
        "        int x = sc.nextInt();\n"
        "        System.out.println(lowerBound(a, x + 1) - lowerBound(a, x));\n"
        "    }\n"
        "}\n"
    ),
    "rotated-array-minimum": _java_main(
        "        int n = sc.nextInt();\n"
        "        int[] a = new int[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
        "        int lo = 0, hi = n - 1;\n"
        "        // TODO: closed-range search comparing a[mid] with a[hi]\n"
        "        System.out.println(a[lo]);\n"
    ),
    "min-ship-capacity": (
        "import java.util.*;\n\n"
        "public class Main {\n"
        "    static int daysNeeded(int[] w, int cap) {\n"
        "        // TODO: greedy left-to-right fill; return the number of days\n"
        "        return w.length;\n"
        "    }\n"
        "    public static void main(String[] args) {\n"
        "        Scanner sc = new Scanner(System.in);\n"
        "        int n = sc.nextInt(), D = sc.nextInt();\n"
        "        int[] w = new int[n];\n"
        "        int lo = 0, hi = 0;\n"
        "        for (int i = 0; i < n; i++) { w[i] = sc.nextInt(); lo = Math.max(lo, w[i]); hi += w[i]; }\n"
        "        // TODO: binary search the capacity in [lo, hi] on daysNeeded(mid) <= D\n"
        "        System.out.println(hi);\n"
        "    }\n"
        "}\n"
    ),
    "rotting-oranges": _java_main(
        "        int H = sc.nextInt(), W = sc.nextInt();\n"
        "        char[][] g = new char[H][];\n"
        "        for (int i = 0; i < H; i++) g[i] = sc.next().toCharArray();\n"
        "        Deque<int[]> q = new ArrayDeque<>();\n"
        "        int fresh = 0;\n"
        "        // TODO: enqueue EVERY 'R' at time 0 and count the 'F's, then BFS\n"
        "        System.out.println(-1);\n"
    ),
    "reachable-within-k": _java_main(
        "        int n = sc.nextInt(), m = sc.nextInt(), K = sc.nextInt();\n"
        "        int s = sc.nextInt();\n"
        "        List<List<Integer>> g = new ArrayList<>();\n"
        "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
        "        for (int i = 0; i < m; i++) {\n"
        "            int u = sc.nextInt(), v = sc.nextInt();\n"
        "            g.get(u).add(v); g.get(v).add(u);\n"
        "        }\n"
        "        int[] dist = new int[n];\n"
        "        Arrays.fill(dist, -1);\n"
        "        // TODO: BFS from s, refusing to expand a node already K steps away\n"
        "        System.out.println(0);\n"
    ),
    "directed-path-exists": _java_main(
        "        int n = sc.nextInt(), m = sc.nextInt();\n"
        "        int s = sc.nextInt(), t = sc.nextInt();\n"
        "        List<List<Integer>> g = new ArrayList<>();\n"
        "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
        "        for (int i = 0; i < m; i++) {\n"
        "            int u = sc.nextInt(), v = sc.nextInt();\n"
        "            g.get(u).add(v);            // one direction only\n"
        "        }\n"
        "        // TODO: DFS with an explicit stack and a visited array\n"
        "        System.out.println(s == t ? \"YES\" : \"NO\");\n"
    ),
    "fractional-knapsack": _java_main(
        "        int n = sc.nextInt();\n"
        "        long C = sc.nextLong();\n"
        "        long[][] items = new long[n][2];   // {value, weight}\n"
        "        for (int i = 0; i < n; i++) { items[i][0] = sc.nextLong(); items[i][1] = sc.nextLong(); }\n"
        "        // TODO: sort by value/weight descending (compare v1*w2 with v2*w1), then fill\n"
        "        System.out.println(0);\n"
    ),
    "greedy-coin-change": _java_main(
        "        int n = sc.nextInt(), amount = sc.nextInt();\n"
        "        int[] coins = new int[n];\n"
        "        for (int i = 0; i < n; i++) coins[i] = sc.nextInt();\n"
        "        Arrays.sort(coins);\n"
        "        // TODO: greedy from the largest coin, then the 1-D DP for the true minimum\n"
        "        System.out.println(-1 + \" \" + -1);\n"
    ),
    "gas-station-start": _java_main(
        "        int n = sc.nextInt();\n"
        "        int[] gas = new int[n], cost = new int[n];\n"
        "        for (int i = 0; i < n; i++) gas[i] = sc.nextInt();\n"
        "        for (int i = 0; i < n; i++) cost[i] = sc.nextInt();\n"
        "        // TODO: total check first, then one pass with a reset\n"
        "        System.out.println(-1);\n"
    ),
    "boats-to-save-people": _java_main(
        "        int n = sc.nextInt(), limit = sc.nextInt();\n"
        "        int[] w = new int[n];\n"
        "        for (int i = 0; i < n; i++) w[i] = sc.nextInt();\n"
        "        Arrays.sort(w);\n"
        "        // TODO: two pointers from both ends; the heaviest departs either way\n"
        "        System.out.println(n);\n"
    ),
})


PREREQS.update({
    "subarray-sum-at-most": [
        ("sliding_window", "Counting all valid windows: for each right end, the valid left ends are a contiguous range."),
        ("iteration", "Both pointers move forward only, which is what keeps the whole count linear."),
    ],
    "longest-k-distinct": [
        ("sliding_window", "The longest-valid shape: grow unconditionally, shrink while invalid, then record."),
        ("hashing", "A count per character; the map's size is the window's distinct count, provided zero counts are removed."),
    ],
    "min-window-sum-atleast": [
        ("sliding_window", "The shortest-valid shape, whose shrink condition is the inverse of the longest-valid one."),
        ("prefix_sum", "The running window sum, and why a negative element would invalidate the two-pointer argument."),
    ],
    "longest-ones-k-flips": [
        ("sliding_window", "A budget as the window invariant: at most K zeros inside."),
        ("array_patterns", "The construction problem reduces to a window property, so the flips never appear in the code."),
    ],
    "count-occurrences-sorted": [
        ("binary_search", "Upper bound expressed as the lower bound of x + 1, so only one template is needed."),
        ("sorting", "The array's order is what makes both bounds computable in log n."),
    ],
    "rotated-array-minimum": [
        ("binary_search", "The predicate is monotone even though the array is not sorted — which is all the loop requires."),
        ("array_patterns", "Comparing a[mid] against a[hi] rather than a target, because there is no target."),
    ],
    "min-ship-capacity": [
        ("binary_search", "Binary search on the answer: the capacity is the search space and the array only evaluates the predicate."),
        ("greedy", "The feasibility check is itself a greedy fill, and it has to be optimal for the search to be valid."),
    ],
    "rotting-oranges": [
        ("bfs", "Multi-source BFS — seeding the queue with every source keeps the distance-order invariant intact."),
        ("graph_repr", "The grid is the graph; orthogonal steps are the edges."),
    ],
    "reachable-within-k": [
        ("bfs", "A distance-limited search: the cap is a refusal to expand, not a filter applied at the end."),
        ("graph_repr", "An adjacency list built from an undirected edge list."),
    ],
    "directed-path-exists": [
        ("graph_repr", "Each edge is added in ONE direction, which is the whole difference from the undirected problems."),
        ("bfs", "Reachability needs a traversal with a visited set; distance is irrelevant, so DFS is equally fine."),
    ],
    "fractional-knapsack": [
        ("greedy", "The sort key is a derived quantity (value per unit weight), and the exchange argument needs divisibility."),
        ("sorting", "Ratios compared by cross-multiplication, so the sort stays exact."),
    ],
    "greedy-coin-change": [
        ("greedy", "A greedy rule that is provably wrong, and the two distinct ways it fails."),
        ("dp", "The 1-D table considers every last coin, which is exactly what greedy refuses to do."),
    ],
    "gas-station-start": [
        ("greedy", "Abandoning a prefix, with the argument for why every station in it was already doomed."),
        ("array_patterns", "A running value plus a reset — the same shape as Kadane's algorithm."),
    ],
    "boats-to-save-people": [
        ("greedy", "If the heaviest person can share with anyone, they can share with the lightest."),
        ("two_pointers", "Converging from both ends, with the heavy end advancing on every iteration."),
    ],
})


# ---------------------------------------------------------------------------
# Reference solutions, merged into REFERENCE_SOLUTIONS so `verify_seeds` proves
# each of these is judged correctly in both shipped languages.
# ---------------------------------------------------------------------------

DEPTH_REFS = {
    "subarray-sum-at-most": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, S = int(d[0]), int(d[1])\na = list(map(int, d[2:2 + n]))\n"
            "total = 0\nwindow = 0\nleft = 0\n"
            "for r in range(n):\n"
            "    window += a[r]\n"
            "    while window > S:\n        window -= a[left]\n        left += 1\n"
            "    total += r - left + 1\n"
            "print(total)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        long S = sc.nextLong();\n"
            "        int[] a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        long total = 0, window = 0;\n"
            "        int left = 0;\n"
            "        for (int r = 0; r < n; r++) {\n"
            "            window += a[r];\n"
            "            while (window > S) window -= a[left++];\n"
            "            total += r - left + 1;\n"
            "        }\n"
            "        System.out.println(total);\n"
        ),
    },
    "longest-k-distinct": {
        "python": (
            "import sys\nL = sys.stdin.read().split('\\n')\n"
            "s = L[0].strip()\nK = int(L[1])\n"
            "count = {}\nleft = 0\nbest = 0\n"
            "for r, ch in enumerate(s):\n"
            "    count[ch] = count.get(ch, 0) + 1\n"
            "    while len(count) > K:\n"
            "        c = s[left]\n        count[c] -= 1\n"
            "        if count[c] == 0: del count[c]\n        left += 1\n"
            "    best = max(best, r - left + 1)\n"
            "print(best)\n"
        ),
        "java": _java_main(
            "        String s = sc.next();\n"
            "        int K = sc.nextInt();\n"
            "        Map<Character, Integer> count = new HashMap<>();\n"
            "        int left = 0, best = 0;\n"
            "        for (int r = 0; r < s.length(); r++) {\n"
            "            count.merge(s.charAt(r), 1, Integer::sum);\n"
            "            while (count.size() > K) {\n"
            "                char c = s.charAt(left++);\n"
            "                if (count.merge(c, -1, Integer::sum) == 0) count.remove(c);\n"
            "            }\n"
            "            best = Math.max(best, r - left + 1);\n"
            "        }\n"
            "        System.out.println(best);\n"
        ),
    },
    "min-window-sum-atleast": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, S = int(d[0]), int(d[1])\na = list(map(int, d[2:2 + n]))\n"
            "window = 0\nleft = 0\nbest = None\n"
            "for r in range(n):\n"
            "    window += a[r]\n"
            "    while window >= S:\n"
            "        L = r - left + 1\n"
            "        best = L if best is None else min(best, L)\n"
            "        window -= a[left]\n        left += 1\n"
            "print(best if best is not None else 0)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        long S = sc.nextLong();\n"
            "        int[] a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        long window = 0;\n"
            "        int left = 0, best = Integer.MAX_VALUE;\n"
            "        for (int r = 0; r < n; r++) {\n"
            "            window += a[r];\n"
            "            while (window >= S) {\n"
            "                best = Math.min(best, r - left + 1);\n"
            "                window -= a[left++];\n"
            "            }\n"
            "        }\n"
            "        System.out.println(best == Integer.MAX_VALUE ? 0 : best);\n"
        ),
    },
    "longest-ones-k-flips": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, k = int(d[0]), int(d[1])\na = list(map(int, d[2:2 + n]))\n"
            "left = 0\nzeros = 0\nbest = 0\n"
            "for r in range(n):\n"
            "    if a[r] == 0: zeros += 1\n"
            "    while zeros > k:\n"
            "        if a[left] == 0: zeros -= 1\n        left += 1\n"
            "    best = max(best, r - left + 1)\n"
            "print(best)\n"
        ),
        "java": _java_main(
            _J_ARR2
            + "        int left = 0, zeros = 0, best = 0;\n"
            "        for (int r = 0; r < n; r++) {\n"
            "            if (a[r] == 0) zeros++;\n"
            "            while (zeros > k) { if (a[left] == 0) zeros--; left++; }\n"
            "            best = Math.max(best, r - left + 1);\n"
            "        }\n"
            "        System.out.println(best);\n"
        ),
    },
    "count-occurrences-sorted": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\nx = int(d[1 + n])\n"
            "def lb(v):\n"
            "    lo, hi = 0, n\n"
            "    while lo < hi:\n        mid = lo + (hi - lo) // 2\n"
            "        if a[mid] < v: lo = mid + 1\n        else: hi = mid\n"
            "    return lo\n"
            "print(lb(x + 1) - lb(x))\n"
        ),
        "java": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static int[] a;\n"
            "    static int lowerBound(int v) {\n"
            "        int lo = 0, hi = a.length;\n"
            "        while (lo < hi) {\n"
            "            int mid = lo + (hi - lo) / 2;\n"
            "            if (a[mid] < v) lo = mid + 1; else hi = mid;\n"
            "        }\n"
            "        return lo;\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt();\n"
            "        a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        int x = sc.nextInt();\n"
            "        System.out.println(lowerBound(x + 1) - lowerBound(x));\n"
            "    }\n"
            "}\n"
        ),
    },
    "rotated-array-minimum": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\n"
            "lo, hi = 0, n - 1\n"
            "while lo < hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if a[mid] > a[hi]: lo = mid + 1\n    else: hi = mid\n"
            "print(a[lo])\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        int[] a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        int lo = 0, hi = n - 1;\n"
            "        while (lo < hi) {\n"
            "            int mid = lo + (hi - lo) / 2;\n"
            "            if (a[mid] > a[hi]) lo = mid + 1; else hi = mid;\n"
            "        }\n"
            "        System.out.println(a[lo]);\n"
        ),
    },
    "min-ship-capacity": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, D = int(d[0]), int(d[1])\nw = list(map(int, d[2:2 + n]))\n"
            "def days(cap):\n"
            "    used, load = 1, 0\n"
            "    for x in w:\n"
            "        if load + x > cap:\n            used += 1\n            load = 0\n"
            "        load += x\n"
            "    return used\n"
            "lo, hi = max(w), sum(w)\n"
            "while lo < hi:\n"
            "    mid = lo + (hi - lo) // 2\n"
            "    if days(mid) > D: lo = mid + 1\n    else: hi = mid\n"
            "print(lo)\n"
        ),
        "java": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static int[] w;\n"
            "    static int days(int cap) {\n"
            "        int used = 1, load = 0;\n"
            "        for (int x : w) {\n"
            "            if (load + x > cap) { used++; load = 0; }\n"
            "            load += x;\n"
            "        }\n"
            "        return used;\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt(), D = sc.nextInt();\n"
            "        w = new int[n];\n"
            "        int lo = 0, hi = 0;\n"
            "        for (int i = 0; i < n; i++) { w[i] = sc.nextInt(); lo = Math.max(lo, w[i]); hi += w[i]; }\n"
            "        while (lo < hi) {\n"
            "            int mid = lo + (hi - lo) / 2;\n"
            "            if (days(mid) > D) lo = mid + 1; else hi = mid;\n"
            "        }\n"
            "        System.out.println(lo);\n"
            "    }\n"
            "}\n"
        ),
    },
    "rotting-oranges": {
        "python": (
            "import sys\nfrom collections import deque\n"
            "L = sys.stdin.read().split('\\n')\n"
            "H, W = map(int, L[0].split())\n"
            "g = [list(L[1 + i]) for i in range(H)]\n"
            "q = deque()\nfresh = 0\n"
            "for i in range(H):\n"
            "    for j in range(W):\n"
            "        if g[i][j] == 'R': q.append((i, j, 0))\n"
            "        elif g[i][j] == 'F': fresh += 1\n"
            "last = 0\n"
            "while q:\n"
            "    i, j, t = q.popleft()\n"
            "    last = max(last, t)\n"
            "    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):\n"
            "        ni, nj = i + di, j + dj\n"
            "        if 0 <= ni < H and 0 <= nj < W and g[ni][nj] == 'F':\n"
            "            g[ni][nj] = 'R'\n            fresh -= 1\n            q.append((ni, nj, t + 1))\n"
            "print(-1 if fresh else last)\n"
        ),
        "java": _java_main(
            "        int H = sc.nextInt(), W = sc.nextInt();\n"
            "        char[][] g = new char[H][];\n"
            "        for (int i = 0; i < H; i++) g[i] = sc.next().toCharArray();\n"
            "        Deque<int[]> q = new ArrayDeque<>();\n"
            "        int fresh = 0;\n"
            "        for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) {\n"
            "            if (g[i][j] == 'R') q.add(new int[]{i, j, 0});\n"
            "            else if (g[i][j] == 'F') fresh++;\n"
            "        }\n"
            "        int[] dr = {-1, 1, 0, 0}, dc = {0, 0, -1, 1};\n"
            "        int last = 0;\n"
            "        while (!q.isEmpty()) {\n"
            "            int[] cur = q.poll();\n"
            "            last = Math.max(last, cur[2]);\n"
            "            for (int d = 0; d < 4; d++) {\n"
            "                int ni = cur[0] + dr[d], nj = cur[1] + dc[d];\n"
            "                if (ni < 0 || ni >= H || nj < 0 || nj >= W) continue;\n"
            "                if (g[ni][nj] != 'F') continue;\n"
            "                g[ni][nj] = 'R';\n"
            "                fresh--;\n"
            "                q.add(new int[]{ni, nj, cur[2] + 1});\n"
            "            }\n"
            "        }\n"
            "        System.out.println(fresh > 0 ? -1 : last);\n"
        ),
    },
    "reachable-within-k": {
        "python": (
            "import sys\nfrom collections import deque\n"
            "L = sys.stdin.read().strip().split('\\n')\n"
            "n, m, K = map(int, L[0].split())\n"
            "s = int(L[1])\n"
            "g = [[] for _ in range(n)]\n"
            "for i in range(m):\n"
            "    u, v = map(int, L[2 + i].split())\n    g[u].append(v)\n    g[v].append(u)\n"
            "dist = [-1] * n\ndist[s] = 0\nq = deque([s])\n"
            "while q:\n"
            "    u = q.popleft()\n"
            "    if dist[u] == K: continue\n"
            "    for v in g[u]:\n"
            "        if dist[v] < 0:\n            dist[v] = dist[u] + 1\n            q.append(v)\n"
            "print(sum(1 for d in dist if 0 <= d <= K) - 1)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt(), m = sc.nextInt(), K = sc.nextInt();\n"
            "        int s = sc.nextInt();\n"
            "        List<List<Integer>> g = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
            "        for (int i = 0; i < m; i++) {\n"
            "            int u = sc.nextInt(), v = sc.nextInt();\n"
            "            g.get(u).add(v); g.get(v).add(u);\n"
            "        }\n"
            "        int[] dist = new int[n];\n"
            "        Arrays.fill(dist, -1);\n"
            "        dist[s] = 0;\n"
            "        Deque<Integer> q = new ArrayDeque<>();\n"
            "        q.add(s);\n"
            "        while (!q.isEmpty()) {\n"
            "            int u = q.poll();\n"
            "            if (dist[u] == K) continue;\n"
            "            for (int v : g.get(u)) if (dist[v] < 0) { dist[v] = dist[u] + 1; q.add(v); }\n"
            "        }\n"
            "        int count = 0;\n"
            "        for (int d : dist) if (d >= 0 && d <= K) count++;\n"
            "        System.out.println(count - 1);\n"
        ),
    },
    "directed-path-exists": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, L[0].split())\n"
            "s, t = map(int, L[1].split())\n"
            "g = [[] for _ in range(n)]\n"
            "for i in range(m):\n"
            "    u, v = map(int, L[2 + i].split())\n    g[u].append(v)\n"
            "seen = [False] * n\nseen[s] = True\nstack = [s]\nans = 'NO'\n"
            "while stack:\n"
            "    u = stack.pop()\n"
            "    if u == t:\n        ans = 'YES'\n        break\n"
            "    for v in g[u]:\n"
            "        if not seen[v]:\n            seen[v] = True\n            stack.append(v)\n"
            "print('YES' if ans == 'YES' or s == t else 'NO')\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt(), m = sc.nextInt();\n"
            "        int s = sc.nextInt(), t = sc.nextInt();\n"
            "        List<List<Integer>> g = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
            "        for (int i = 0; i < m; i++) {\n"
            "            int u = sc.nextInt(), v = sc.nextInt();\n"
            "            g.get(u).add(v);\n"
            "        }\n"
            "        boolean[] seen = new boolean[n];\n"
            "        Deque<Integer> st = new ArrayDeque<>();\n"
            "        st.push(s);\n"
            "        seen[s] = true;\n"
            "        boolean found = false;\n"
            "        while (!st.isEmpty()) {\n"
            "            int u = st.pop();\n"
            "            if (u == t) { found = true; break; }\n"
            "            for (int v : g.get(u)) if (!seen[v]) { seen[v] = true; st.push(v); }\n"
            "        }\n"
            "        System.out.println(found || s == t ? \"YES\" : \"NO\");\n"
        ),
    },
    "fractional-knapsack": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n, C = map(int, L[0].split())\n"
            "items = [tuple(map(int, L[1 + i].split())) for i in range(n)]\n"
            "items.sort(key=lambda t: (-t[0] * 10 ** 9 // t[1], t[1]))\n"
            "total = 0\nleft = C\n"
            "for value, weight in items:\n"
            "    if left == 0: break\n"
            "    take = min(weight, left)\n"
            "    total += value * 100 * take // weight\n"
            "    left -= take\n"
            "print(total)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        long C = sc.nextLong();\n"
            "        long[][] it = new long[n][2];\n"
            "        for (int i = 0; i < n; i++) { it[i][0] = sc.nextLong(); it[i][1] = sc.nextLong(); }\n"
            "        Arrays.sort(it, (p, q) -> {\n"
            "            long l = p[0] * q[1], r = q[0] * p[1];\n"
            "            if (l != r) return Long.compare(r, l);\n"
            "            return Long.compare(p[1], q[1]);\n"
            "        });\n"
            "        long total = 0, left = C;\n"
            "        for (long[] item : it) {\n"
            "            if (left == 0) break;\n"
            "            long take = Math.min(item[1], left);\n"
            "            total += item[0] * 100 * take / item[1];\n"
            "            left -= take;\n"
            "        }\n"
            "        System.out.println(total);\n"
        ),
    },
    "greedy-coin-change": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, amount = int(d[0]), int(d[1])\n"
            "coins = sorted(map(int, d[2:2 + n]), reverse=True)\n"
            "left = amount\ngreedy = 0\n"
            "for c in coins:\n    greedy += left // c\n    left %= c\n"
            "if left: greedy = -1\n"
            "INF = float('inf')\n"
            "dp = [0] + [INF] * amount\n"
            "for a in range(1, amount + 1):\n"
            "    for c in coins:\n"
            "        if c <= a and dp[a - c] + 1 < dp[a]: dp[a] = dp[a - c] + 1\n"
            "best = -1 if dp[amount] == INF else dp[amount]\n"
            "print(greedy, best)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt(), amount = sc.nextInt();\n"
            "        int[] coins = new int[n];\n"
            "        for (int i = 0; i < n; i++) coins[i] = sc.nextInt();\n"
            "        Arrays.sort(coins);\n"
            "        int left = amount, greedy = 0;\n"
            "        for (int i = n - 1; i >= 0; i--) { greedy += left / coins[i]; left %= coins[i]; }\n"
            "        if (left != 0) greedy = -1;\n"
            "        final int INF = Integer.MAX_VALUE / 2;\n"
            "        int[] dp = new int[amount + 1];\n"
            "        Arrays.fill(dp, INF);\n"
            "        dp[0] = 0;\n"
            "        for (int a = 1; a <= amount; a++)\n"
            "            for (int c : coins)\n"
            "                if (c <= a && dp[a - c] + 1 < dp[a]) dp[a] = dp[a - c] + 1;\n"
            "        int best = dp[amount] >= INF ? -1 : dp[amount];\n"
            "        System.out.println(greedy + \" \" + best);\n"
        ),
    },
    "gas-station-start": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\n"
            "gas = list(map(int, L[1].split()))\n"
            "cost = list(map(int, L[2].split()))\n"
            "if sum(gas) < sum(cost):\n    print(-1)\nelse:\n"
            "    start = 0\n    tank = 0\n"
            "    for i in range(n):\n"
            "        tank += gas[i] - cost[i]\n"
            "        if tank < 0:\n            start = i + 1\n            tank = 0\n"
            "    print(start)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt();\n"
            "        int[] gas = new int[n], cost = new int[n];\n"
            "        for (int i = 0; i < n; i++) gas[i] = sc.nextInt();\n"
            "        for (int i = 0; i < n; i++) cost[i] = sc.nextInt();\n"
            "        long tg = 0, tc = 0;\n"
            "        for (int i = 0; i < n; i++) { tg += gas[i]; tc += cost[i]; }\n"
            "        if (tg < tc) { System.out.println(-1); return; }\n"
            "        int start = 0;\n"
            "        long tank = 0;\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            tank += gas[i] - cost[i];\n"
            "            if (tank < 0) { start = i + 1; tank = 0; }\n"
            "        }\n"
            "        System.out.println(start);\n"
        ),
    },
    "boats-to-save-people": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, limit = int(d[0]), int(d[1])\n"
            "w = sorted(map(int, d[2:2 + n]))\n"
            "i, j, boats = 0, n - 1, 0\n"
            "while i <= j:\n"
            "    if w[i] + w[j] <= limit: i += 1\n"
            "    j -= 1\n    boats += 1\n"
            "print(boats)\n"
        ),
        "java": _java_main(
            "        int n = sc.nextInt(), limit = sc.nextInt();\n"
            "        int[] w = new int[n];\n"
            "        for (int i = 0; i < n; i++) w[i] = sc.nextInt();\n"
            "        Arrays.sort(w);\n"
            "        int i = 0, j = n - 1, boats = 0;\n"
            "        while (i <= j) {\n"
            "            if (w[i] + w[j] <= limit) i++;\n"
            "            j--;\n"
            "            boats++;\n"
            "        }\n"
            "        System.out.println(boats);\n"
        ),
    },
}
