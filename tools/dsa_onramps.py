# -*- coding: utf-8 -*-
# ===========================================================================
# On-ramps — the entry problem each starved unit was missing.
#
# exec'd inside gen_seed.py's namespace (before `out` is built), so it extends
# DEFS and JAVA_STARTERS in place like expansion_defs.py does.
#
# WHY THIS FILE EXISTS
#
# The DSA curriculum labels each unit's first rung "Warm up", but for a dozen
# units that label was decoration: `backtracking` opened at Medium and stayed
# there for ten problems, `union-find` had eleven problems and not one Easy,
# `dp-2d` opened on a Medium and then went straight to four Hards. The bank's
# accidental distribution — assembled problem-by-problem, never audited per
# unit — was deciding where each technique began.
#
# A first rung that opens at the unit's ceiling is not a warm-up, it is a wall.
# Someone meeting union-find for the first time should count components on six
# nodes with union-by-size and nothing else, *then* be asked whether a graph is
# a valid tree. The problems here are that first step: each one is the technique
# with every complication removed, so the skeleton on the unit page is provably
# enough to solve it.
#
# DESIGN RULES
#
#   1. EASY, AND HONESTLY EASY. Each is solvable with the unit's own skeleton,
#      typed once, on inputs small enough to check by hand.
#   2. NO NEW IDEAS. An on-ramp never introduces a second technique. The
#      shortest-paths warm-up is BFS on an unweighted grid precisely because it
#      is Dijkstra with the priority queue deleted.
#   3. ONE THING IT TEACHES, stated in the editorial as the sentence the
#      problem exists to make true.
#   4. TINY, VISIBLE INPUTS. Bounds are deliberately small (n ≤ 200, grids
#      ≤ 50×50) so the learner can trace the algorithm on the sample rather
#      than trusting it.
#
# Encoding follows the rest of the bank's 1-D stdin/stdout model: graphs as
# `n` plus an edge list, grids as `H W` plus H rows.
# ===========================================================================
from collections import deque

# ---------------------------------------------------------------------------
# Reference solutions. Each takes the raw stdin string and returns the exact
# stdout the judge will compare against, so the bundled expected outputs are
# computed rather than eyeballed.
# ---------------------------------------------------------------------------


def _ints(s):
    return list(map(int, s.split()))


def sol_fixed_window_max(inp):
    ls = inp.strip().split("\n")
    n, k = _ints(ls[0])
    a = _ints(ls[1])
    window = sum(a[:k])
    best = window
    for r in range(k, n):
        window += a[r] - a[r - k]
        best = max(best, window)
    return str(best)


def sol_window_covers_set(inp):
    """Length of the shortest PREFIX of `s` that contains every required
    character. The left edge never moves — shrinking it to find the shortest
    window anywhere is the Hard problem this warms up for."""
    ls = inp.strip("\n").split("\n")
    s = ls[0].strip()
    need = set(ls[1].strip())
    have = set()
    for r, ch in enumerate(s):
        have.add(ch)
        if need <= have:
            return str(r + 1)
    return "-1"


def sol_lower_bound(inp):
    ls = inp.strip().split("\n")
    n = int(ls[0])
    a = _ints(ls[1]) if n else []
    x = int(ls[2])
    lo, hi = 0, n
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return str(lo)


def sol_first_true(inp):
    """`f(i)` is monotone false…false,true…true; find the first true index."""
    ls = inp.strip().split("\n")
    n = int(ls[0])
    flags = ls[1].split()
    lo, hi = 0, n
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if flags[mid] == "F":
            lo = mid + 1
        else:
            hi = mid
    return str(lo if lo < n else -1)


def sol_balanced_brackets_depth(inp):
    s = inp.strip()
    depth = 0
    best = 0
    for c in s:
        if c == "(":
            depth += 1
            best = max(best, depth)
        elif c == ")":
            if depth == 0:
                return "-1"
            depth -= 1
    return str(best) if depth == 0 else "-1"


def _adj(n, edges):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    return g


def _read_graph(inp):
    ls = inp.strip().split("\n")
    n, m = _ints(ls[0])
    edges = [tuple(_ints(ls[1 + i])) for i in range(m)]
    return n, edges


def sol_count_components_bfs(inp):
    n, edges = _read_graph(inp)
    g = _adj(n, edges)
    seen = [False] * n
    comps = 0
    for s in range(n):
        if seen[s]:
            continue
        comps += 1
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for v in g[u]:
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
    return str(comps)


def sol_has_cycle_directed_small(inp):
    ls = inp.strip().split("\n")
    n, m = _ints(ls[0])
    indeg = [0] * n
    g = [[] for _ in range(n)]
    for i in range(m):
        u, v = _ints(ls[1 + i])
        g[u].append(v)
        indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    removed = 0
    while q:
        u = q.popleft()
        removed += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return "YES" if removed < n else "NO"


def sol_grid_bfs_distance(inp):
    ls = inp.strip("\n").split("\n")
    h, w = _ints(ls[0])
    grid = [ls[1 + i] for i in range(h)]
    start = goal = None
    for i in range(h):
        for j in range(w):
            if grid[i][j] == "S":
                start = (i, j)
            elif grid[i][j] == "G":
                goal = (i, j)
    dist = [[-1] * w for _ in range(h)]
    dist[start[0]][start[1]] = 0
    q = deque([start])
    while q:
        i, j = q.popleft()
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] != "#" and dist[ni][nj] < 0:
                dist[ni][nj] = dist[i][j] + 1
                q.append((ni, nj))
    return str(dist[goal[0]][goal[1]])


def sol_union_by_size_components(inp):
    n, edges = _read_graph(inp)
    parent = list(range(n))
    size = [1] * n

    def find(x):
        while parent[x] != x:      # no compression — that is the next rung
            x = parent[x]
        return x

    comps = n
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            continue
        if size[ru] < size[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        size[ru] += size[rv]
        comps -= 1
    return str(comps)


def sol_subsets_small(inp):
    ls = inp.strip().split("\n")
    n = int(ls[0])
    a = _ints(ls[1]) if n else []
    out = []

    def rec(i, chosen):
        if i == n:
            out.append(" ".join(map(str, chosen)) if chosen else "-")
            return
        rec(i + 1, chosen)               # skip a[i]
        chosen.append(a[i])
        rec(i + 1, chosen)               # take a[i]
        chosen.pop()                     # UNDO — the line backtracking is about

    rec(0, [])
    return "\n".join(sorted(out))


def sol_ways_to_climb(inp):
    """Steps of 1 or 2 — the smallest honest 1-D table."""
    n = int(inp.strip())
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        dp[i] = dp[i - 1] + (dp[i - 2] if i >= 2 else 0)
    return " ".join(str(dp[i]) for i in range(n + 1))


def sol_grid_paths_open(inp):
    h, w = _ints(inp.strip())
    dp = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            if i == 0 and j == 0:
                dp[i][j] = 1
            else:
                dp[i][j] = (dp[i - 1][j] if i else 0) + (dp[i][j - 1] if j else 0)
    return "\n".join(" ".join(str(x) for x in row) for row in dp)


def sol_trie_exact_lookup(inp):
    ls = inp.strip().split("\n")
    n = int(ls[0])
    words = ls[1:1 + n]
    q = int(ls[1 + n])
    queries = ls[2 + n:2 + n + q]
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = True
    res = []
    for t in queries:
        node = root
        ok = True
        for ch in t:
            if ch not in node:
                ok = False
                break
            node = node[ch]
        res.append("YES" if ok and "$" in node else "NO")
    return "\n".join(res)


def sol_activity_selection(inp):
    ls = inp.strip().split("\n")
    n = int(ls[0])
    jobs = sorted(tuple(_ints(ls[1 + i])) for i in range(n))
    jobs = sorted(jobs, key=lambda t: t[1])      # earliest finish first
    count = 0
    last_end = -10 ** 9
    for s, e in jobs:
        if s >= last_end:
            count += 1
            last_end = e
    return str(count)


# ---------------------------------------------------------------------------
# Shared starter scaffolding. Each on-ramp ships a Java starter as well as
# Python/JS, because the curriculum's skeletons are Java and an on-ramp whose
# starter is in another language is not an on-ramp.
# ---------------------------------------------------------------------------

_JAVA_SCANNER = (
    "import java.util.*;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "{body}"
    "    }\n"
    "}\n"
)


def _java(body):
    return _JAVA_SCANNER.replace("{body}", body)


_J_ARRAY_READ = (
    "        int n = sc.nextInt();\n"
    "        int[] a = new int[n];\n"
    "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
)

_J_GRAPH_READ = (
    "        int n = sc.nextInt(), m = sc.nextInt();\n"
    "        List<List<Integer>> g = new ArrayList<>();\n"
    "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
    "        for (int i = 0; i < m; i++) {\n"
    "            int u = sc.nextInt(), v = sc.nextInt();\n"
    "            g.get(u).add(v);\n"
    "            g.get(v).add(u);\n"
    "        }\n"
)


ONRAMP_DEFS = [
    # -- sliding-window ----------------------------------------------------
    dict(
        slug="fixed-window-max-sum", title="Fixed Window Maximum Sum", difficulty="Easy",
        topics=["Arrays"], subtopics=["Sliding Window", "Fixed Window"], companies=["Amazon"],
        description=(
            "Given an array and a window width `k`, find the largest sum of any `k` "
            "**consecutive** elements.\n\n"
            "The point is the *slide*: compute the first window's sum by adding `k` values, "
            "then move the window one step at a time by adding the element that entered and "
            "subtracting the one that left. Recomputing each window from scratch is O(n·k); "
            "sliding is O(n).\n\n"
            "### Input\n- Line 1: `n k`.\n- Line 2: `n` space-separated integers.\n\n"
            "### Output\nA single integer: the maximum window sum."
        ),
        constraints="1 ≤ k ≤ n ≤ 200\n-1000 ≤ a[i] ≤ 1000",
        hints=[
            "Sum the first k elements to get the starting window.",
            "Moving right by one adds a[r] and removes a[r - k] — two operations, not k.",
            "Track the best sum seen after every slide, including the first window.",
            "`window += a[r] - a[r - k];  best = Math.max(best, window);`",
        ],
        opt=("O(n)", "O(1)",
             "Each element enters the window once and leaves once, so the total work is linear; "
             "only the running sum and the best sum are stored."),
        editorial=(
            "## The one thing this teaches\nA window sum is *maintained*, not recomputed.\n\n"
            "## Approach\nAdd `a[0..k-1]` to get the first window and record it as the best. "
            "Then for each `r` from `k` to `n-1`, do `window += a[r] - a[r-k]` and update the "
            "best. Two array reads per step, regardless of how wide the window is.\n\n"
            "Seed `best` from the first window, not from `0` — with negative values `0` is a "
            "sum no window may ever reach, and the answer comes out wrong silently."
        ),
        ref=sol_fixed_window_max,
        starter_py=(
            "import sys\n\ndata = sys.stdin.read().split()\n"
            "n, k = int(data[0]), int(data[1])\n"
            "a = list(map(int, data[2:2 + n]))\n\n"
            "def solve(a, k):\n"
            "    # TODO: sum the first window, then slide it\n"
            "    return 0\n\nprint(solve(a, k))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], k = d[1], a = d.slice(2, 2 + n);\n\n"
            "function solve(a, k) {\n  // TODO: sum the first window, then slide it\n  return 0;\n}\n\n"
            "console.log(solve(a, k));\n"
        ),
        cases=[
            ("example", "Example 1", "6 3\n1 2 5 1 1 1\n"),
            ("example", "Example 2", "5 2\n-3 -1 -4 -1 -5\n"),
            ("hidden", "Whole array is the window", "4 4\n1 2 3 4\n"),
            ("hidden", "Width one", "5 1\n-2 7 -3 4 0\n"),
            ("hidden", "All negative, width three", "5 3\n-5 -5 -5 -5 -1\n"),
        ],
        example_expl=[
            "The window `2 5 1` sums to 8, which beats every other width-3 window.",
            "`-3 -1` sums to -4; every other width-2 window is smaller. A `0` seed would "
            "wrongly report 0.",
        ],
    ),
    dict(
        slug="window-covering-letters", title="Prefix Covering a Letter Set", difficulty="Easy",
        topics=["Strings"], subtopics=["Sliding Window"], companies=["Google"],
        description=(
            "Given a string `s` and a small set of required characters, find the length of the "
            "**window starting at index 0** that first contains every required character at "
            "least once.\n\n"
            "Concretely: grow the right edge from the start of the string until the window "
            "covers the set, then print the window's length. The left edge never moves — "
            "shrinking it to find the *shortest* such window is the Hard problem this warms "
            "up for.\n\n"
            "### Input\n- Line 1: the string `s` (lowercase letters, no spaces).\n"
            "- Line 2: the required characters, as one string with no repeats.\n\n"
            "### Output\nThe length of that window, or `-1` if `s` never covers the set."
        ),
        constraints="1 ≤ |s| ≤ 200\n1 ≤ |required| ≤ 6\nBoth lines are lowercase English letters.",
        hints=[
            "Keep a count per character in the current window, and a count of how many required characters are satisfied.",
            "Extend the right edge one character at a time.",
            "A character becomes newly satisfied when its count goes from 0 to 1 and it is required.",
            "Stop the moment satisfied == required.size() and print r + 1.",
        ],
        opt=("O(|s|)", "O(1)",
             "One left-to-right pass; the counts are bounded by the 26-letter alphabet."),
        editorial=(
            "## The one thing this teaches\nA window is described by a *summary* of what it "
            "holds — here, how many required characters it covers — updated as the edge moves, "
            "never rescanned.\n\n"
            "## Approach\nCount the required characters into a `need` map. Walk `r` from 0, "
            "incrementing `have[s[r]]`; when `have[c]` reaches 1 for a required `c`, increment "
            "`satisfied`. The answer is `r + 1` at the first `r` where `satisfied` equals the "
            "number of distinct required characters. If the loop ends first, print `-1`.\n\n"
            "Rescanning the window on every step would also be correct and would also be "
            "O(n·26) here — the reason to maintain the summary is that the shortest-window "
            "version, where the left edge moves too, has no rescan cheap enough to survive."
        ),
        ref=sol_window_covers_set,
        starter_py=(
            "import sys\n\nlines = sys.stdin.read().split('\\n')\n"
            "s, req = lines[0].strip(), lines[1].strip()\n\n"
            "def solve(s, req):\n"
            "    # TODO: grow the right edge until every character of req is inside\n"
            "    return -1\n\nprint(solve(s, req))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
            "const s = L[0].trim(), req = L[1].trim();\n\n"
            "function solve(s, req) {\n"
            "  // TODO: grow the right edge until every character of req is inside\n"
            "  return -1;\n}\n\nconsole.log(solve(s, req));\n"
        ),
        cases=[
            ("example", "Example 1", "abcxyz\nxa\n"),
            ("example", "Example 2", "aabbcc\nabc\n"),
            ("hidden", "Immediately covered", "z\nz\n"),
            ("hidden", "Never covered", "aaaa\nab\n"),
            ("hidden", "Last character completes it", "bbbbba\nab\n"),
        ],
        example_expl=[
            "`abcx` is the first prefix holding both `x` and `a` → length 4.",
            "`aabbc` is the first prefix holding `a`, `b` and `c` → length 5.",
        ],
    ),

    # -- binary-search -----------------------------------------------------
    dict(
        slug="lower-bound-index", title="Lower Bound", difficulty="Easy",
        topics=["Searching"], subtopics=["Binary Search", "Lower Bound"], companies=["Microsoft"],
        description=(
            "Given a **sorted** array and a value `x`, print the index of the first element "
            "that is **greater than or equal to** `x`. If no element qualifies, print `n`.\n\n"
            "This is `lower_bound`, and it is the only binary search worth memorising: it "
            "answers *\"where does x belong?\"*, which subsumes *\"is x present?\"* (check "
            "`a[i] == x` afterwards), *\"how many are smaller?\"* (the index itself) and "
            "*\"where do I insert it?\"*\n\n"
            "### Input\n- Line 1: integer `n`.\n- Line 2: `n` sorted integers, "
            "non-decreasing.\n- Line 3: the value `x`.\n\n"
            "### Output\nA single integer index in `0 … n`."
        ),
        constraints="1 ≤ n ≤ 200\n-1000 ≤ a[i], x ≤ 1000\na is sorted non-decreasing and may contain duplicates.",
        hints=[
            "Search the half-open range [lo, hi) with hi starting at n, not n - 1.",
            "The answer can legitimately be n, which is why hi starts one past the end.",
            "If a[mid] < x the answer is right of mid, so lo = mid + 1; otherwise hi = mid.",
            "Loop while lo < hi and return lo. The loop never needs an equality case.",
        ],
        opt=("O(log n)", "O(1)",
             "Each iteration halves the candidate range; only three indices are stored."),
        editorial=(
            "## The one thing this teaches\nBinary search on a **half-open** range `[lo, hi)` "
            "has no off-by-one to get wrong: `lo` is the first index that might be the answer, "
            "`hi` is one past the last, and the loop ends when they meet.\n\n"
            "## Approach\n```java\nint lo = 0, hi = n;\nwhile (lo < hi) {\n"
            "    int mid = lo + (hi - lo) / 2;\n"
            "    if (a[mid] < x) lo = mid + 1;   // mid cannot be the answer\n"
            "    else            hi = mid;       // mid might be\n}\nreturn lo;\n```\n\n"
            "Note what is *absent*: no `a[mid] == x` branch. The three-case version is where "
            "the classic off-by-one lives, because \"found it\" and \"first one at least as "
            "large\" are different questions and mixing them loses duplicates.\n\n"
            "`mid = lo + (hi - lo) / 2` rather than `(lo + hi) / 2` — the latter overflows "
            "`int` once the indices are large, which is a real bug in real libraries."
        ),
        ref=sol_lower_bound,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\nx = int(d[1 + n])\n\n"
            "def solve(a, x):\n"
            "    # TODO: half-open binary search; return the first index with a[i] >= x\n"
            "    return len(a)\n\nprint(solve(a, x))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], a = d.slice(1, 1 + n), x = d[1 + n];\n\n"
            "function solve(a, x) {\n"
            "  // TODO: half-open binary search; return the first index with a[i] >= x\n"
            "  return a.length;\n}\n\nconsole.log(solve(a, x));\n"
        ),
        cases=[
            ("example", "Example 1", "6\n1 3 3 5 8 9\n3\n"),
            ("example", "Example 2", "5\n2 4 6 8 10\n7\n"),
            ("hidden", "Larger than everything", "4\n1 2 3 4\n99\n"),
            ("hidden", "Smaller than everything", "4\n1 2 3 4\n-5\n"),
            ("hidden", "All duplicates of the target", "5\n7 7 7 7 7\n7\n"),
        ],
        example_expl=[
            "The first element ≥ 3 is at index 1 — the *first* of the two 3s, which is what "
            "lower bound means.",
            "No element equals 7; the first one larger is 8 at index 3.",
        ],
    ),
    dict(
        slug="first-true-predicate", title="First True in a Monotone Predicate", difficulty="Easy",
        topics=["Searching"], subtopics=["Binary Search"], companies=["Meta"],
        description=(
            "You are given the values of a predicate `f(0), f(1), … , f(n-1)` as a row of `F` "
            "and `T` characters. The predicate is **monotone**: once it turns `T` it never "
            "returns to `F`.\n\n"
            "Print the smallest index where it is `T`, or `-1` if it is `F` everywhere.\n\n"
            "This is the shape *every* \"binary search on the answer\" problem reduces to: "
            "the array is not the thing you search, the predicate is. Seeing it written out as "
            "`FFFTTT` once makes the next ten problems recognisable.\n\n"
            "### Input\n- Line 1: integer `n`.\n"
            "- Line 2: `n` space-separated characters, each `F` or `T`, non-decreasing in the "
            "sense that no `F` follows a `T`.\n\n### Output\nThe first `T` index, or `-1`."
        ),
        constraints="1 ≤ n ≤ 200\nEach token is `F` or `T`; all `F`s precede all `T`s.",
        hints=[
            "You are not searching for a value — you are searching for a boundary.",
            "Use the same half-open range as lower bound: [0, n).",
            "`F` at mid means the boundary is strictly right: lo = mid + 1. `T` means hi = mid.",
            "After the loop, lo is n when everything was F — that is the -1 case.",
        ],
        opt=("O(log n)", "O(1)",
             "The monotonicity is what licenses discarding half the range on one probe; "
             "without it, no binary search is valid and the answer needs a linear scan."),
        editorial=(
            "## The one thing this teaches\nBinary search needs **monotonicity**, not "
            "sortedness. A sorted array is just the most familiar monotone predicate "
            "(`a[i] >= x`).\n\n"
            "## Approach\nIdentical to lower bound with `a[mid] < x` replaced by "
            "`f(mid) == false`:\n\n```java\nint lo = 0, hi = n;\nwhile (lo < hi) {\n"
            "    int mid = lo + (hi - lo) / 2;\n"
            "    if (!f(mid)) lo = mid + 1;\n    else         hi = mid;\n}\n"
            "return lo < n ? lo : -1;\n```\n\n"
            "## Why it matters later\n\"Smallest capacity that ships in D days\", \"smallest "
            "speed that finishes in time\", \"largest minimum gap\" — all of them are this "
            "loop with `f` replaced by a feasibility check. The hard part of those problems is "
            "never the search; it is noticing that feasibility is monotone."
        ),
        ref=sol_first_true,
        starter_py=(
            "import sys\n\nlines = sys.stdin.read().split('\\n')\n"
            "n = int(lines[0])\nflags = lines[1].split()\n\n"
            "def f(i):\n    return flags[i] == 'T'\n\n"
            "def solve(n):\n"
            "    # TODO: half-open binary search for the first index where f is true\n"
            "    return -1\n\nprint(solve(n))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
            "const n = Number(L[0]), flags = L[1].trim().split(/\\s+/);\n"
            "const f = (i) => flags[i] === 'T';\n\n"
            "function solve(n) {\n"
            "  // TODO: half-open binary search for the first index where f is true\n"
            "  return -1;\n}\n\nconsole.log(solve(n));\n"
        ),
        cases=[
            ("example", "Example 1", "6\nF F F T T T\n"),
            ("example", "Example 2", "4\nF F F F\n"),
            ("hidden", "True from the start", "3\nT T T\n"),
            ("hidden", "Single false", "1\nF\n"),
            ("hidden", "Boundary at the last index", "5\nF F F F T\n"),
        ],
        example_expl=[
            "The predicate first holds at index 3.",
            "It never holds, so the answer is -1.",
        ],
    ),

    # -- stacks ------------------------------------------------------------
    dict(
        slug="max-bracket-depth", title="Maximum Bracket Depth", difficulty="Easy",
        topics=["Data Structures", "Strings"], subtopics=["Stack"], companies=["Adobe"],
        description=(
            "A string contains only `(` and `)`. Print the maximum nesting depth if the string "
            "is balanced, or `-1` if it is not.\n\n"
            "With one bracket type you do not need to store anything — a counter *is* the "
            "stack, and seeing that is the point. The moment a second bracket type appears "
            "(`[`, `{`) the counter stops working and you need the real stack, which is the "
            "next rung.\n\n"
            "### Input\nA single line: a string of `(` and `)`, length ≥ 1.\n\n"
            "### Output\nThe maximum depth, or `-1` if unbalanced."
        ),
        constraints="1 ≤ |s| ≤ 200\ns contains only the characters `(` and `)`.",
        hints=[
            "Walk the string keeping a running depth: `(` increments, `)` decrements.",
            "Track the largest depth the counter ever reaches.",
            "A `)` when the depth is already 0 means a close with nothing open — unbalanced.",
            "Ending with depth > 0 means brackets were left open — also unbalanced.",
        ],
        opt=("O(n)", "O(1)",
             "One pass; with a single bracket type the stack's *height* is all that matters, "
             "so a counter replaces it and the space drops from O(n) to O(1)."),
        editorial=(
            "## The one thing this teaches\nA stack answers \"what is the most recent "
            "unmatched thing?\" — and when every item on it would be identical, the only "
            "information left is its height, which is a single `int`.\n\n"
            "## Approach\n`depth++` on `(`, `depth--` on `)`, tracking `best = max(best, "
            "depth)` after each open. Two failure conditions, and both are easy to forget:\n\n"
            "- `depth` goes negative → a `)` arrived with nothing to match. Return -1 "
            "immediately; the rest of the string cannot repair it.\n"
            "- `depth != 0` at the end → opens were never closed.\n\n"
            "## Why the next rung needs a real stack\nWith `(`, `[` and `{`, the counter "
            "cannot tell you that `([)]` is wrong — the height is right at every step and the "
            "*identities* are not. That is exactly the information a stack keeps and a counter "
            "throws away."
        ),
        ref=sol_balanced_brackets_depth,
        starter_py=(
            "s = input().strip()\n\n"
            "def solve(s):\n"
            "    # TODO: return the maximum depth, or -1 if unbalanced\n"
            "    return -1\n\nprint(solve(s))\n"
        ),
        starter_js=(
            "const s = require('fs').readFileSync(0, 'utf8').trim();\n\n"
            "function solve(s) {\n"
            "  // TODO: return the maximum depth, or -1 if unbalanced\n"
            "  return -1;\n}\n\nconsole.log(solve(s));\n"
        ),
        cases=[
            ("example", "Example 1", "((()))\n"),
            ("example", "Example 2", "()(()\n"),
            ("hidden", "Flat pairs", "()()()\n"),
            ("hidden", "Close before open", ")(\n"),
            ("hidden", "Deep then flat", "(((())))()\n"),
        ],
        example_expl=[
            "Three opens before any close → depth 3.",
            "The final `(` is never closed, so the string is unbalanced.",
        ],
    ),

    # -- graph-traversal ---------------------------------------------------
    dict(
        slug="count-connected-components", title="Count Connected Components", difficulty="Easy",
        topics=["Graphs"], subtopics=["BFS", "Connected Components"],
        companies=["Amazon"],
        description=(
            "An undirected graph has `n` nodes numbered `0 … n-1` and `m` edges. Print the "
            "number of connected components.\n\n"
            "This is the whole of graph traversal with nothing else attached: build an "
            "adjacency list, loop over every node, and start a BFS from each node you have not "
            "seen. Each BFS that *starts* is one component.\n\n"
            "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v` — an undirected edge.\n\n"
            "### Output\nA single integer: the number of components."
        ),
        constraints="1 ≤ n ≤ 200\n0 ≤ m ≤ 400\n0 ≤ u, v < n\nEdges may repeat; self-loops may appear.",
        hints=[
            "Build `List<List<Integer>>` adjacency: each edge is added in BOTH directions.",
            "Keep one `boolean[] seen` for the whole run — not one per BFS.",
            "Loop s from 0 to n-1; if `seen[s]` is false, that is a new component: count it and BFS from s.",
            "Mark a node seen when you ENQUEUE it, not when you dequeue it, or it enters the queue twice.",
        ],
        opt=("O(n + m)", "O(n + m)",
             "Every node is enqueued once and every edge inspected twice (once from each end); "
             "the adjacency list dominates the space."),
        editorial=(
            "## The one thing this teaches\nThe outer loop. A single BFS explores one "
            "component; *counting* components needs the `for (s = 0; s < n; s++)` wrapper "
            "around it, and forgetting that wrapper is the most common way this is got wrong "
            "— it silently reports 1 on a disconnected graph.\n\n"
            "## Approach\n```java\nboolean[] seen = new boolean[n];\nint comps = 0;\n"
            "for (int s = 0; s < n; s++) {\n    if (seen[s]) continue;\n    comps++;\n"
            "    seen[s] = true;\n    Deque<Integer> q = new ArrayDeque<>();\n    q.add(s);\n"
            "    while (!q.isEmpty()) {\n        int u = q.poll();\n"
            "        for (int v : g.get(u)) if (!seen[v]) { seen[v] = true; q.add(v); }\n"
            "    }\n}\n```\n\n"
            "**Mark on enqueue.** If you instead mark when you dequeue, a node reachable from "
            "two already-queued nodes gets added twice. On a small graph that is merely "
            "wasteful; on a dense one it is exponential blow-up, and the symptom is a timeout "
            "rather than a wrong answer.\n\n"
            "A self-loop and a repeated edge are both harmless here precisely because `seen` "
            "is checked before enqueueing — worth confirming on the hidden tests rather than "
            "special-casing."
        ),
        ref=sol_count_components_bfs,
        starter_py=(
            "import sys\nfrom collections import deque\n\n"
            "lines = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, lines[0].split())\n"
            "g = [[] for _ in range(n)]\n"
            "for i in range(m):\n"
            "    u, v = map(int, lines[1 + i].split())\n"
            "    g[u].append(v)\n    g[v].append(u)\n\n"
            "def solve(n, g):\n"
            "    # TODO: BFS from every unseen node; count the starts\n"
            "    return 0\n\nprint(solve(n, g))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const [n, m] = L[0].split(/\\s+/).map(Number);\n"
            "const g = Array.from({ length: n }, () => []);\n"
            "for (let i = 0; i < m; i++) {\n"
            "  const [u, v] = L[1 + i].split(/\\s+/).map(Number);\n"
            "  g[u].push(v); g[v].push(u);\n}\n\n"
            "function solve(n, g) {\n"
            "  // TODO: BFS from every unseen node; count the starts\n"
            "  return 0;\n}\n\nconsole.log(solve(n, g));\n"
        ),
        cases=[
            ("example", "Example 1", "6 4\n0 1\n1 2\n3 4\n4 5\n"),
            ("example", "Example 2", "4 0\n"),
            ("hidden", "One chain", "5 4\n0 1\n1 2\n2 3\n3 4\n"),
            ("hidden", "Self loop and duplicate edge", "3 3\n0 0\n1 2\n1 2\n"),
            ("hidden", "Single node", "1 0\n"),
        ],
        example_expl=[
            "`{0,1,2}` and `{3,4,5}` → 2 components.",
            "With no edges every node is its own component → 4.",
        ],
    ),

    # -- topological-sort --------------------------------------------------
    dict(
        slug="detect-cycle-tiny-dag", title="Cycle in a Directed Graph", difficulty="Easy",
        topics=["Graphs"], subtopics=["Topological Sort", "Cycle Detection"],
        companies=["Google"],
        description=(
            "A directed graph has `n` nodes and `m` edges. Print `YES` if it contains a cycle "
            "and `NO` if it is a DAG.\n\n"
            "Kahn's algorithm answers this as a by-product: repeatedly remove a node with "
            "in-degree 0. If you manage to remove all `n`, the graph was acyclic; whatever is "
            "left when the queue empties is a cycle, because every remaining node still has an "
            "incoming edge from another remaining node.\n\n"
            "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v` — a directed edge `u → v`.\n\n"
            "### Output\n`YES` if a cycle exists, otherwise `NO`."
        ),
        constraints="1 ≤ n ≤ 200\n0 ≤ m ≤ 400\n0 ≤ u, v < n\nA self-loop `u u` counts as a cycle.",
        hints=[
            "Compute in-degree for every node: `indeg[v]++` for each edge u → v.",
            "Seed a queue with every node whose in-degree is 0.",
            "Removing u decrements the in-degree of each neighbour; a neighbour reaching 0 joins the queue.",
            "Count how many nodes you removed. Fewer than n means a cycle.",
        ],
        opt=("O(n + m)", "O(n + m)",
             "Each node enters the queue at most once and each edge is decremented once."),
        editorial=(
            "## The one thing this teaches\nA topological sort and a cycle check are the same "
            "algorithm. You do not need a second traversal to decide acyclicity — you need to "
            "count what the first one managed to output.\n\n"
            "## Approach\n```java\nint[] indeg = new int[n];\nfor each edge u → v: indeg[v]++;\n"
            "Deque<Integer> q = new ArrayDeque<>();\n"
            "for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);\nint removed = 0;\n"
            "while (!q.isEmpty()) {\n    int u = q.poll();\n    removed++;\n"
            "    for (int v : g.get(u)) if (--indeg[v] == 0) q.add(v);\n}\n"
            "return removed < n;   // true ⇒ cycle\n```\n\n"
            "## Why the leftovers are a cycle\nWhen the queue empties, every unremoved node "
            "has in-degree ≥ 1, and its incoming edge must come from another unremoved node "
            "(removed nodes already decremented their edges). Follow those edges backwards "
            "from any leftover node: the set is finite, so you must revisit a node — that is a "
            "cycle. This argument is worth being able to say out loud; it is the standard "
            "follow-up question.\n\n"
            "A self-loop `u → u` gives `u` in-degree 1 that nothing can ever decrement, so it "
            "is caught with no special case."
        ),
        ref=sol_has_cycle_directed_small,
        starter_py=(
            "import sys\nfrom collections import deque\n\n"
            "lines = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, lines[0].split())\n"
            "g = [[] for _ in range(n)]\nindeg = [0] * n\n"
            "for i in range(m):\n"
            "    u, v = map(int, lines[1 + i].split())\n"
            "    g[u].append(v)\n    indeg[v] += 1\n\n"
            "def solve(n, g, indeg):\n"
            "    # TODO: Kahn's algorithm; return 'YES' if fewer than n nodes come out\n"
            "    return 'NO'\n\nprint(solve(n, g, indeg))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const [n, m] = L[0].split(/\\s+/).map(Number);\n"
            "const g = Array.from({ length: n }, () => []);\n"
            "const indeg = new Array(n).fill(0);\n"
            "for (let i = 0; i < m; i++) {\n"
            "  const [u, v] = L[1 + i].split(/\\s+/).map(Number);\n"
            "  g[u].push(v); indeg[v]++;\n}\n\n"
            "function solve(n, g, indeg) {\n"
            "  // TODO: Kahn's algorithm; return 'YES' if fewer than n nodes come out\n"
            "  return 'NO';\n}\n\nconsole.log(solve(n, g, indeg));\n"
        ),
        cases=[
            ("example", "Example 1", "3 3\n0 1\n1 2\n2 0\n"),
            ("example", "Example 2", "4 3\n0 1\n0 2\n1 3\n"),
            ("hidden", "Self loop", "2 1\n1 1\n"),
            ("hidden", "No edges", "3 0\n"),
            ("hidden", "Cycle in one component only", "5 4\n0 1\n2 3\n3 4\n4 2\n"),
        ],
        example_expl=[
            "`0 → 1 → 2 → 0` is a cycle, so nothing ever has in-degree 0 → YES.",
            "A tree-shaped DAG; all four nodes come out of the queue → NO.",
        ],
    ),

    # -- shortest-paths ----------------------------------------------------
    dict(
        slug="grid-bfs-distance", title="Grid Distance by BFS", difficulty="Easy",
        topics=["Graphs", "Matrix"], subtopics=["BFS", "Grid"], companies=["Meta"],
        description=(
            "A grid of `H` rows and `W` columns contains `.` (open), `#` (wall), one `S` "
            "(start) and one `G` (goal). Moving one step up, down, left or right onto an open "
            "cell costs 1. Print the fewest steps from `S` to `G`, or `-1` if unreachable.\n\n"
            "Every edge here costs the same, which is exactly why plain BFS is optimal and "
            "Dijkstra would be wasted: BFS visits cells in non-decreasing distance order for "
            "free, because a FIFO queue *is* a priority queue when every priority is one more "
            "than the last.\n\n"
            "### Input\n- Line 1: `H W`.\n- Next `H` lines: the grid, each a string of length `W`.\n\n"
            "### Output\nThe minimum number of steps, or `-1`."
        ),
        constraints="1 ≤ H, W ≤ 50\nExactly one `S` and exactly one `G`.\nOther characters are `.` or `#`.",
        hints=[
            "Treat each open cell as a node and each orthogonal step as an edge of weight 1.",
            "Keep a `dist[H][W]` filled with -1 as both the distance table and the visited marker.",
            "Set dist when you ENQUEUE a cell: dist[ni][nj] = dist[i][j] + 1.",
            "The four steps are `{-1,0},{1,0},{0,-1},{0,1}` — check bounds before reading the cell.",
        ],
        opt=("O(H·W)", "O(H·W)",
             "Each cell is enqueued at most once and has at most four neighbours, so the work "
             "is linear in the number of cells."),
        editorial=(
            "## The one thing this teaches\nBFS is the unweighted shortest path, and the "
            "reason is worth stating precisely: the queue holds cells in non-decreasing "
            "distance order, so the first time a cell is reached is via a shortest path. "
            "Nothing needs re-relaxing, and nothing needs a heap.\n\n"
            "## Approach\nInitialise `dist` to -1 everywhere, set `dist[S] = 0`, push `S`. Pop "
            "a cell, and for each of the four neighbours that is in bounds, not a `#`, and "
            "still -1, set its distance to one more and push it. Answer is `dist[G]`, which is "
            "still -1 if the goal was never reached.\n\n"
            "**The `dist` array is the visited set.** Keeping a separate `boolean[][] visited` "
            "is not wrong, but it is a second thing to keep in sync, and the classic bug is "
            "setting one and not the other.\n\n"
            "## Why weights change the algorithm\nMake one cell cost 5 to enter and the "
            "invariant dies: a cell reached early via an expensive route may be reachable more "
            "cheaply later, so the first arrival is no longer final. Restoring \"process in "
            "non-decreasing distance order\" then needs an actual priority queue — that is "
            "Dijkstra, and it is the only difference between it and this loop."
        ),
        ref=sol_grid_bfs_distance,
        starter_py=(
            "import sys\nfrom collections import deque\n\n"
            "L = sys.stdin.read().split('\\n')\n"
            "H, W = map(int, L[0].split())\n"
            "grid = [L[1 + i] for i in range(H)]\n\n"
            "def solve(H, W, grid):\n"
            "    # TODO: BFS from S; return dist at G, or -1\n"
            "    return -1\n\nprint(solve(H, W, grid))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
            "const [H, W] = L[0].split(/\\s+/).map(Number);\n"
            "const grid = [];\nfor (let i = 0; i < H; i++) grid.push(L[1 + i]);\n\n"
            "function solve(H, W, grid) {\n"
            "  // TODO: BFS from S; return dist at G, or -1\n"
            "  return -1;\n}\n\nconsole.log(solve(H, W, grid));\n"
        ),
        cases=[
            ("example", "Example 1", "3 4\nS..#\n.#..\n...G\n"),
            ("example", "Example 2", "3 3\nS.#\n##.\n..G\n"),
            ("hidden", "Adjacent", "1 2\nSG\n"),
            ("hidden", "Straight corridor", "1 5\nS...G\n"),
            ("hidden", "Walled off", "2 3\nS#G\n.#.\n"),
        ],
        example_expl=[
            "One shortest route is right, down, down, right, right → 5 steps.",
            "The wall row blocks every path from S to G → -1.",
        ],
    ),

    # -- union-find --------------------------------------------------------
    dict(
        slug="union-by-size-components", title="Components with Union by Size", difficulty="Easy",
        topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon"],
        description=(
            "Start with `n` singleton sets `0 … n-1` and apply `m` unions. Print how many sets "
            "remain.\n\n"
            "Write `find` as a **plain walk to the root** and `union` with **union by size** "
            "only — no path compression. That restriction is the point: with union by size "
            "alone the trees are already O(log n) deep, and knowing that is what makes path "
            "compression an optimisation rather than a magic incantation you cannot justify.\n\n"
            "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v` — union the sets containing "
            "`u` and `v`.\n\n### Output\nThe number of disjoint sets remaining."
        ),
        constraints="1 ≤ n ≤ 200\n0 ≤ m ≤ 400\n0 ≤ u, v < n\nA union of two already-joined elements is a no-op.",
        hints=[
            "`parent[i] = i` and `size[i] = 1` to start; keep a counter at n.",
            "`find(x)`: `while (parent[x] != x) x = parent[x]; return x;`",
            "If the two roots are equal, do nothing — including not decrementing the counter.",
            "Otherwise hang the SMALLER root under the larger, add its size, and decrement the counter.",
        ],
        opt=("O(m log n)", "O(n)",
             "Union by size keeps every tree at depth O(log n) — an element's depth only grows "
             "when its tree is merged into one at least as large, which can happen at most "
             "log₂n times — so each find costs O(log n)."),
        editorial=(
            "## The one thing this teaches\nThe component count is maintained by the *unions*, "
            "not recomputed by a traversal. Start at `n` and decrement exactly once per union "
            "that actually merged two different roots.\n\n"
            "## Approach\n```java\nint[] parent = new int[n], size = new int[n];\n"
            "for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }\nint comps = n;\n\n"
            "int find(int x) { while (parent[x] != x) x = parent[x]; return x; }\n\n"
            "for each edge (u, v) {\n    int a = find(u), b = find(v);\n"
            "    if (a == b) continue;                 // already together\n"
            "    if (size[a] < size[b]) { int t = a; a = b; b = t; }\n"
            "    parent[b] = a;\n    size[a] += size[b];\n    comps--;\n}\n```\n\n"
            "## Why by size, and why it is enough\nLink roots arbitrarily and an adversary "
            "builds a 200-long chain, making `find` O(n). Always hanging the smaller tree "
            "under the larger means an element's depth increases only when its tree merges "
            "into one at least as big — so the tree it lives in at least doubles. A tree can "
            "double at most log₂n times, so depth stays O(log n) **without any compression at "
            "all**.\n\n"
            "Path compression then flattens what the walk already found, taking the amortised "
            "cost to near-constant. Add it on the next rung, and you will be able to say what "
            "it bought."
        ),
        ref=sol_union_by_size_components,
        starter_py=(
            "import sys\n\nlines = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, lines[0].split())\n"
            "edges = [tuple(map(int, lines[1 + i].split())) for i in range(m)]\n\n"
            "def solve(n, edges):\n"
            "    parent = list(range(n))\n    size = [1] * n\n"
            "    # TODO: plain find (no compression) + union by size; return the set count\n"
            "    return n\n\nprint(solve(n, edges))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const [n, m] = L[0].split(/\\s+/).map(Number);\n"
            "const edges = [];\nfor (let i = 0; i < m; i++) edges.push(L[1 + i].split(/\\s+/).map(Number));\n\n"
            "function solve(n, edges) {\n"
            "  const parent = Array.from({ length: n }, (_, i) => i);\n"
            "  const size = new Array(n).fill(1);\n"
            "  // TODO: plain find (no compression) + union by size; return the set count\n"
            "  return n;\n}\n\nconsole.log(solve(n, edges));\n"
        ),
        cases=[
            ("example", "Example 1", "6 3\n0 1\n1 2\n4 5\n"),
            ("example", "Example 2", "4 4\n0 1\n1 0\n0 1\n2 3\n"),
            ("hidden", "No unions", "5 0\n"),
            ("hidden", "Everything joined", "4 3\n0 1\n1 2\n2 3\n"),
            ("hidden", "Self union", "3 1\n1 1\n"),
        ],
        example_expl=[
            "Sets become `{0,1,2}`, `{3}`, `{4,5}` → 3.",
            "Three of the four unions are redundant; only `{0,1}` and `{2,3}` merge → 2.",
        ],
    ),

    # -- backtracking ------------------------------------------------------
    dict(
        slug="all-subsets-small", title="All Subsets of a Tiny Array", difficulty="Easy",
        topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Microsoft"],
        description=(
            "Print every subset of an array of at most 4 distinct integers.\n\n"
            "Each element is a binary choice — **skip it** or **take it** — so the recursion "
            "has exactly two branches and a base case of \"no elements left\". Four elements "
            "means 16 subsets, which is few enough to check every line by hand against your "
            "own trace.\n\n"
            "### Input\n- Line 1: integer `n` (1 ≤ n ≤ 4).\n- Line 2: `n` distinct integers.\n\n"
            "### Output\nAll `2^n` subsets, one per line, each as its elements in input order "
            "separated by single spaces. Print `-` for the empty subset. **Sort the lines "
            "lexicographically as text** before printing, so the output is unique."
        ),
        constraints="1 ≤ n ≤ 4\n-99 ≤ a[i] ≤ 99, all distinct",
        hints=[
            "Recurse on an index: `rec(i, chosen)` decides what to do with a[i].",
            "Two calls: `rec(i + 1, chosen)` without a[i], then add a[i] and `rec(i + 1, chosen)`.",
            "The base case i == n emits the current `chosen` list — that is where output happens.",
            "After the 'take' branch returns, REMOVE a[i] from chosen. That removal is the whole lesson.",
        ],
        opt=("O(2^n · n)", "O(n)",
             "There are 2^n subsets and writing one costs O(n); the recursion depth — and so "
             "the shared `chosen` list — is only O(n), which is the payoff for undoing instead "
             "of copying."),
        editorial=(
            "## The one thing this teaches\n**The undo.** Backtracking is depth-first search "
            "over a tree of partial answers, and it reuses one mutable list for every node of "
            "that tree. That only works if each branch leaves the list exactly as it found "
            "it:\n\n```java\nvoid rec(int i, List<Integer> chosen) {\n"
            "    if (i == n) { emit(chosen); return; }\n"
            "    rec(i + 1, chosen);          // skip a[i]\n"
            "    chosen.add(a[i]);\n"
            "    rec(i + 1, chosen);          // take a[i]\n"
            "    chosen.remove(chosen.size() - 1);   // UNDO\n}\n```\n\n"
            "Delete that last line and the output is nonsense — every later subset inherits "
            "elements from a branch that already finished. Every backtracking bug you will hit "
            "for the next ten problems is a missing or misplaced undo.\n\n"
            "## Why not just copy the list?\nYou can: pass `new ArrayList<>(chosen)` down and "
            "delete the undo. It is easier to get right and it costs O(n) per node instead of "
            "O(1), which multiplies the whole search by n. For n=4 nobody cares; for n-queens "
            "on an 8×8 board it is the difference between instant and slow. Learn the undo "
            "here, where a wrong answer is 16 lines you can read.\n\n"
            "## On the sort\nThe recursion emits subsets in a deterministic order already, but "
            "*which* order depends on whether you branch skip-first or take-first. Sorting the "
            "lines as text means either choice passes, so the problem grades your recursion "
            "rather than your branch order."
        ),
        ref=sol_subsets_small,
        starter_py=(
            "import sys\n\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\n\n"
            "def solve(a):\n"
            "    out = []\n"
            "    # TODO: rec(i, chosen) with skip / take / UNDO; append one string per subset\n"
            "    return sorted(out)\n\nprint('\\n'.join(solve(a)))\n"
        ),
        starter_js=(
            "const d = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean).map(Number);\n"
            "const n = d[0], a = d.slice(1, 1 + n);\n\n"
            "function solve(a) {\n  const out = [];\n"
            "  // TODO: rec(i, chosen) with skip / take / UNDO; push one string per subset\n"
            "  return out.sort();\n}\n\nconsole.log(solve(a).join('\\n'));\n"
        ),
        cases=[
            ("example", "Example 1", "2\n1 2\n"),
            ("example", "Example 2", "3\n5 1 9\n"),
            ("hidden", "Single element", "1\n7\n"),
            ("hidden", "Four elements", "4\n1 2 3 4\n"),
            ("hidden", "Negatives", "2\n-3 4\n"),
        ],
        example_expl=[
            "Four subsets: the empty one (`-`), `1`, `1 2` and `2`, sorted as text.",
            "Eight subsets of `{5, 1, 9}`, each printed in input order and then sorted as text.",
        ],
    ),

    # -- dp-1d -------------------------------------------------------------
    dict(
        slug="stair-ways-table", title="Stair Ways — Print the Table", difficulty="Easy",
        topics=["Recursion & DP"], subtopics=["Dynamic Programming", "1D DP"], companies=["Adobe"],
        description=(
            "You climb a staircase of `n` steps, moving 1 or 2 steps at a time. Print the "
            "number of distinct ways to reach **every** step from 0 to `n`.\n\n"
            "Printing the whole table rather than only `dp[n]` is deliberate: it forces you to "
            "fill the array in order and makes the recurrence visible in the output. If your "
            "row reads `1 1 2 3 5 8` you can see Fibonacci appear, and you will recognise it "
            "in the next six problems.\n\n"
            "### Input\nA single integer `n`.\n\n### Output\n`n + 1` space-separated integers: "
            "`dp[0] dp[1] … dp[n]`, where `dp[i]` is the number of ways to reach step `i`."
        ),
        constraints="0 ≤ n ≤ 40",
        hints=[
            "There is exactly one way to be at the bottom before moving: dp[0] = 1.",
            "To land on step i you arrived from i-1 (a 1-step) or i-2 (a 2-step).",
            "So dp[i] = dp[i-1] + dp[i-2], with dp[i-2] omitted when i < 2.",
            "Fill i from 1 upward — every value you read is already final.",
        ],
        opt=("O(n)", "O(n)",
             "One pass over the table, each cell computed from two already-final cells; the "
             "table itself is the space, and only the last two entries are needed if you do "
             "not have to print it."),
        editorial=(
            "## The one thing this teaches\nThe three questions that define every 1-D DP, "
            "asked once where the answers are obvious:\n\n"
            "1. **What does `dp[i]` mean?** \"The number of ways to reach step i.\" Say it in "
            "words before typing. Half of all DP bugs are a table whose meaning changed "
                "halfway through the loop.\n"
            "2. **What is the recurrence?** The last move was a 1-step or a 2-step, and those "
            "cases do not overlap, so the counts add: `dp[i] = dp[i-1] + dp[i-2]`.\n"
            "3. **What is the base case, and why?** `dp[0] = 1` — there is exactly one way to "
            "stand at the bottom having made no moves. Setting it to 0 makes the whole table 0; "
            "this is the single most common error in the unit.\n\n"
            "## Approach\n```java\nlong[] dp = new long[n + 1];\ndp[0] = 1;\n"
            "for (int i = 1; i <= n; i++) {\n    dp[i] = dp[i - 1] + (i >= 2 ? dp[i - 2] : 0);\n}\n"
            "```\n\n"
            "**Order matters and is not arbitrary.** `dp[i]` reads smaller indices, so a "
            "left-to-right fill guarantees every value read is already final. That is the whole "
            "content of \"bottom-up\".\n\n"
            "## From recursion to table\nThe same recurrence written as a function recomputes "
            "`stairs(i-2)` exponentially often. Memoising it gives the same numbers in the same "
            "order this loop produces them — the table *is* the memo, with the recursion "
            "unrolled. Doing that conversion by hand once is the build-it exercise on the unit "
            "page."
        ),
        ref=sol_ways_to_climb,
        starter_py=(
            "n = int(input())\n\n"
            "def solve(n):\n"
            "    dp = [0] * (n + 1)\n"
            "    # TODO: dp[0] = 1, then fill left to right\n"
            "    return dp\n\nprint(' '.join(map(str, solve(n))))\n"
        ),
        starter_js=(
            "const n = Number(require('fs').readFileSync(0, 'utf8').trim());\n\n"
            "function solve(n) {\n  const dp = new Array(n + 1).fill(0);\n"
            "  // TODO: dp[0] = 1, then fill left to right\n  return dp;\n}\n\n"
            "console.log(solve(n).join(' '));\n"
        ),
        cases=[
            ("example", "Example 1", "5\n"),
            ("example", "Example 2", "0\n"),
            ("hidden", "One step", "1\n"),
            ("hidden", "Two steps", "2\n"),
            ("hidden", "Forty steps", "40\n"),
        ],
        example_expl=[
            "`1 1 2 3 5 8` — Fibonacci, shifted. There are 8 ways to climb 5 steps.",
            "With no steps to climb the table is just `dp[0] = 1`.",
        ],
    ),

    # -- dp-2d -------------------------------------------------------------
    dict(
        slug="grid-paths-table", title="Grid Paths — Print the Table", difficulty="Easy",
        topics=["Recursion & DP"], subtopics=["Dynamic Programming", "2D DP", "Grid"], companies=["Amazon"],
        description=(
            "You start at the top-left of an `H × W` grid and may only move **right** or "
            "**down**. There are no obstacles. Print the full table of path counts: the number "
            "of distinct routes from the start to each cell.\n\n"
            "Printing the table rather than one number is the point. A 2-D DP is a 1-D DP with "
            "a second index, and the only new question is *the order the cells are filled in* "
            "— which the printed grid makes visible.\n\n"
            "### Input\nA single line: `H W`.\n\n"
            "### Output\n`H` lines of `W` space-separated integers: row `i` holds the path "
            "counts for `dp[i][0] … dp[i][W-1]`."
        ),
        constraints="1 ≤ H, W ≤ 15",
        hints=[
            "dp[0][0] = 1 — one way to be where you started.",
            "Any other cell is entered from above or from the left, and those routes are distinct.",
            "dp[i][j] = dp[i-1][j] + dp[i][j-1], dropping a term when the index is off the grid.",
            "Fill row by row, left to right, so both cells you read are already final.",
        ],
        opt=("O(H·W)", "O(H·W)",
             "Each cell is computed once from two neighbours; the table dominates the space, "
             "and can be reduced to one row if only the final value is needed."),
        editorial=(
            "## The one thing this teaches\n**Fill order.** In 1-D, \"left to right\" is the "
            "only choice. In 2-D there are several, and the recurrence decides which are "
            "legal: `dp[i][j]` reads `dp[i-1][j]` and `dp[i][j-1]`, so any order that visits "
            "both before `(i, j)` works — row by row, or column by column, but not diagonally "
            "outward from the far corner.\n\n"
            "## Approach\n```java\nlong[][] dp = new long[H][W];\n"
            "for (int i = 0; i < H; i++)\n    for (int j = 0; j < W; j++) {\n"
            "        if (i == 0 && j == 0) { dp[i][j] = 1; continue; }\n"
            "        dp[i][j] = (i > 0 ? dp[i - 1][j] : 0) + (j > 0 ? dp[i][j - 1] : 0);\n"
            "    }\n```\n\n"
            "The first row and column come out all 1s without being special-cased, because the "
            "missing term contributes 0. Pre-filling them by hand is also fine and is arguably "
            "clearer — what is *not* fine is pre-filling them and then letting the general "
            "loop overwrite them.\n\n"
            "## What the table is for\nThe printed grid is not decoration. Reading it "
            "*backwards* from the bottom-right reconstructs an actual path: at each cell, the "
            "neighbour whose value you came from tells you the last move. Path counting and "
            "path reconstruction use the same table, and the unit's trace walks that second "
            "read.\n\n"
            "## Adding one obstacle\nSet an obstacle's cell to 0 and skip it in the loop, and "
            "the recurrence handles the rest — every route through it disappears automatically. "
            "That is the next rung."
        ),
        ref=sol_grid_paths_open,
        starter_py=(
            "H, W = map(int, input().split())\n\n"
            "def solve(H, W):\n"
            "    dp = [[0] * W for _ in range(H)]\n"
            "    # TODO: dp[0][0] = 1, then fill row by row\n"
            "    return dp\n\n"
            "for row in solve(H, W):\n    print(' '.join(map(str, row)))\n"
        ),
        starter_js=(
            "const [H, W] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n\n"
            "function solve(H, W) {\n"
            "  const dp = Array.from({ length: H }, () => new Array(W).fill(0));\n"
            "  // TODO: dp[0][0] = 1, then fill row by row\n  return dp;\n}\n\n"
            "console.log(solve(H, W).map((r) => r.join(' ')).join('\\n'));\n"
        ),
        cases=[
            ("example", "Example 1", "3 3\n"),
            ("example", "Example 2", "1 4\n"),
            ("hidden", "Single cell", "1 1\n"),
            ("hidden", "Tall and narrow", "5 1\n"),
            ("hidden", "Largest allowed", "15 15\n"),
        ],
        example_expl=[
            "Rows `1 1 1`, `1 2 3`, `1 3 6` — six routes to the far corner.",
            "With one row there is a single route to every cell.",
        ],
    ),

    # -- tries -------------------------------------------------------------
    dict(
        slug="trie-insert-lookup", title="Trie: Insert and Exact Lookup", difficulty="Easy",
        topics=["Data Structures", "Strings"], subtopics=["Trie"], companies=["Google"],
        description=(
            "Insert `n` words into a trie, then answer `q` queries: for each, print `YES` if "
            "the **whole word** was inserted and `NO` otherwise.\n\n"
            "Only these two operations — no prefix counting, no wildcards, no deletion. The "
            "thing to get right is the one design decision a trie makes: a node is a "
            "*position in a set of strings*, and it needs a flag saying whether a word ends "
            "there, separate from whether it has children.\n\n"
            "### Input\n- Line 1: integer `n`.\n- Next `n` lines: one word each.\n"
            "- Next line: integer `q`.\n- Next `q` lines: one query word each.\n\n"
            "### Output\n`q` lines of `YES` or `NO`."
        ),
        constraints="1 ≤ n, q ≤ 100\n1 ≤ word length ≤ 20\nWords are lowercase English letters. Words may repeat.",
        hints=[
            "A node holds `Node[] children = new Node[26]` and a `boolean isWord`.",
            "Insert: walk character by character, creating a child where one is missing; set isWord at the end.",
            "Search: walk the same way, but return NO the moment a child is missing.",
            "Reaching the end of the query is not enough — the final node's isWord must be true.",
        ],
        opt=("O(total characters)", "O(total characters · 26)",
             "Insert and lookup each cost one step per character of the word, independent of "
             "how many words the trie holds — that independence is the whole reason to build "
             "one."),
        editorial=(
            "## The one thing this teaches\n`isWord` is not the same as \"has no children\". "
            "Insert `car` and `card`: the node at `car` has a child, and `car` is still a word. "
            "Insert only `card`, and the node at `car` exists but is not a word. Lookup must "
            "check the flag, never childlessness.\n\n"
            "## Approach\n```java\nclass Node { Node[] next = new Node[26]; boolean isWord; }\n\n"
            "void insert(String w) {\n    Node cur = root;\n"
            "    for (char c : w.toCharArray()) {\n        int k = c - 'a';\n"
            "        if (cur.next[k] == null) cur.next[k] = new Node();\n"
            "        cur = cur.next[k];\n    }\n    cur.isWord = true;\n}\n\n"
            "boolean search(String w) {\n    Node cur = root;\n"
            "    for (char c : w.toCharArray()) {\n        int k = c - 'a';\n"
            "        if (cur.next[k] == null) return false;\n        cur = cur.next[k];\n    }\n"
            "    return cur.isWord;\n}\n```\n\n"
            "Inserting the same word twice is harmless — the walk finds existing nodes and "
            "sets an already-true flag.\n\n"
            "## Why not a HashSet?\nFor *exact* lookup, a `HashSet<String>` is better: less "
            "code, less memory, O(length) hashing. A trie earns its keep only when the "
            "question is about **prefixes** — how many words start with `ca`, what is the "
            "longest stored prefix of this string, walk every completion — because those read "
            "the shared path a hash set destroys. This problem exists to build the structure, "
            "not to justify it; the justification is the next rung."
        ),
        ref=sol_trie_exact_lookup,
        starter_py=(
            "import sys\n\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\nwords = L[1:1 + n]\n"
            "q = int(L[1 + n])\nqueries = L[2 + n:2 + n + q]\n\n"
            "def solve(words, queries):\n"
            "    root = {}\n"
            "    # TODO: insert each word (mark the end), then look each query up exactly\n"
            "    return ['NO'] * len(queries)\n\n"
            "print('\\n'.join(solve(words, queries)))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const n = Number(L[0]);\nconst words = L.slice(1, 1 + n);\n"
            "const q = Number(L[1 + n]);\nconst queries = L.slice(2 + n, 2 + n + q);\n\n"
            "function solve(words, queries) {\n  const root = {};\n"
            "  // TODO: insert each word (mark the end), then look each query up exactly\n"
            "  return queries.map(() => 'NO');\n}\n\n"
            "console.log(solve(words, queries).join('\\n'));\n"
        ),
        cases=[
            ("example", "Example 1", "3\ncar\ncard\ncat\n4\ncar\nca\ncard\ncot\n"),
            ("example", "Example 2", "1\napple\n2\napple\napp\n"),
            ("hidden", "Repeated insert", "2\nab\nab\n1\nab\n"),
            ("hidden", "Query longer than any word", "1\na\n1\nabc\n"),
            ("hidden", "Single letters", "3\na\nb\nc\n3\nc\nd\na\n"),
        ],
        example_expl=[
            "`car` and `card` were both inserted → YES. `ca` is only a prefix → NO. `cot` "
            "leaves the trie at `c` → NO.",
            "`app` is a prefix of `apple` but was never inserted as a word — this is exactly "
            "the case `isWord` exists for.",
        ],
    ),

    # -- greedy ------------------------------------------------------------
    dict(
        slug="activity-selection-small", title="Activity Selection", difficulty="Easy",
        topics=["Greedy", "Intervals"], subtopics=["Earliest Finish"], companies=["Bloomberg"],
        description=(
            "You are given `n` activities, each with a start and an end time. You can only do "
            "one at a time, and an activity that starts exactly when another ends is fine. "
            "Print the largest number of activities you can complete.\n\n"
            "### Input\n- Line 1: integer `n`.\n- Next `n` lines: `s e` with `s < e`.\n\n"
            "### Output\nA single integer: the maximum count."
        ),
        constraints="1 ≤ n ≤ 200\n0 ≤ s < e ≤ 10000",
        hints=[
            "Sorting by start time does not work — one long early activity blocks the rest.",
            "Sorting by duration does not work either; find a 3-activity counterexample.",
            "Sort by END time, then take every activity that starts at or after the last end.",
            "One pass after the sort: `if (s >= lastEnd) { count++; lastEnd = e; }`",
        ],
        opt=("O(n log n)", "O(n)",
             "The sort dominates; the selection itself is one linear pass with a single "
             "variable of state."),
        editorial=(
            "## The one thing this teaches\nA greedy algorithm is a **sort order plus a local "
            "rule**, and the sort order is the entire algorithm. Get it wrong and no amount of "
            "care in the loop recovers.\n\n"
            "## Approach\nSort by end time ascending. Walk the list keeping `lastEnd`, "
            "initially `-infinity`. Take an activity when `s >= lastEnd`, and set "
            "`lastEnd = e`.\n\n"
            "## Why earliest-finish is correct\nAmong all activities compatible with what you "
            "have taken, the one that ends first leaves the *largest possible remaining time "
            "window*, and it occupies exactly one slot like any other choice. So there is "
            "always an optimal solution that starts with it — swap the first activity of any "
            "optimal solution for the earliest-finishing one and the rest still fits. Induct "
            "on what remains.\n\n"
            "That exchange argument is what an interviewer is asking for when they say \"why "
            "is greedy correct here?\", and it is the part candidates skip.\n\n"
            "## The orders that fail\n- **By start time**: `(0,100), (1,2), (3,4)` takes 1 "
            "instead of 2.\n"
            "- **By duration**: `(0,5), (4,6), (5,10)` takes the short middle one and gets 1 "
            "instead of 2.\n\n"
            "Being able to produce those two counterexamples on demand is worth more than "
            "remembering the rule, because it is how you check a greedy rule you have just "
            "invented under pressure."
        ),
        ref=sol_activity_selection,
        starter_py=(
            "import sys\n\nlines = sys.stdin.read().strip().split('\\n')\n"
            "n = int(lines[0])\n"
            "jobs = [tuple(map(int, lines[1 + i].split())) for i in range(n)]\n\n"
            "def solve(jobs):\n"
            "    # TODO: sort by end time, then take every job starting at or after lastEnd\n"
            "    return 0\n\nprint(solve(jobs))\n"
        ),
        starter_js=(
            "const L = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
            "const n = Number(L[0]);\nconst jobs = [];\n"
            "for (let i = 0; i < n; i++) jobs.push(L[1 + i].split(/\\s+/).map(Number));\n\n"
            "function solve(jobs) {\n"
            "  // TODO: sort by end time, then take every job starting at or after lastEnd\n"
            "  return 0;\n}\n\nconsole.log(solve(jobs));\n"
        ),
        cases=[
            ("example", "Example 1", "4\n0 100\n1 2\n3 4\n5 6\n"),
            ("example", "Example 2", "3\n0 5\n4 6\n5 10\n"),
            ("hidden", "Single activity", "1\n0 1\n"),
            ("hidden", "Touching ends are compatible", "3\n0 1\n1 2\n2 3\n"),
            ("hidden", "All overlap", "3\n0 10\n1 9\n2 8\n"),
        ],
        example_expl=[
            "`(1,2)`, `(3,4)`, `(5,6)` → 3. Sorting by start time would take `(0,100)` and "
            "stop at 1.",
            "`(0,5)` then `(5,10)` → 2. Sorting by duration would take `(4,6)` and stop at 1.",
        ],
    ),
]

DEFS += ONRAMP_DEFS

# Prerequisite concepts, per the bank's contract (`verify_seeds` asserts every
# problem has at least one). Each `how` line says what the learner will actually
# use the concept *for* in this problem, not merely that it is related — an
# on-ramp's prerequisites are the closest thing it has to a syllabus.
PREREQS.update({
    "fixed-window-max-sum": [
        ("iteration", "One left-to-right pass over the array, carrying a running value."),
        ("sliding_window", "The window is maintained by adding what entered and subtracting what left, never recomputed."),
    ],
    "window-covering-letters": [
        ("sliding_window", "The right edge grows while a summary of the window's contents is kept up to date."),
        ("hashing", "A count per character, so \"does the window cover the set?\" is O(1) to answer."),
    ],
    "lower-bound-index": [
        ("binary_search", "The half-open `[lo, hi)` loop with no equality branch — the only binary search worth memorising."),
        ("sorting", "The array is sorted, which is what licenses discarding half the range on one probe."),
    ],
    "first-true-predicate": [
        ("binary_search", "The same loop with the array replaced by a predicate, which is what \"binary search on the answer\" means."),
        ("conditionals", "The monotone predicate is a boolean function of the index; reasoning about it is case analysis."),
    ],
    "max-bracket-depth": [
        ("stack", "With one bracket type the only information a stack would hold is its height, so a counter replaces it."),
        ("char_arrays", "Walking a string character by character and branching on each one."),
    ],
    "count-connected-components": [
        ("graph_repr", "Build the adjacency list first — each undirected edge is added in both directions."),
        ("bfs", "One BFS explores one component; the outer loop over unseen nodes is what counts them."),
    ],
    "detect-cycle-tiny-dag": [
        ("topo", "Kahn's algorithm, run for its by-product: how many nodes it managed to remove."),
        ("graph_cycle", "Whatever the queue leaves behind must contain a cycle, and you should be able to say why."),
    ],
    "grid-bfs-distance": [
        ("bfs", "A FIFO queue visits cells in non-decreasing distance order, which is why BFS is optimal when every edge costs 1."),
        ("graph_repr", "The grid is the graph: cells are nodes and orthogonal steps are the edges."),
    ],
    "union-by-size-components": [
        ("union_find", "Plain `find` plus union by size — enough on its own to cap the tree depth at O(log n)."),
        ("iteration", "The component count is maintained by the unions rather than recomputed at the end."),
    ],
    "all-subsets-small": [
        ("recursion", "Each element is a two-branch decision, so the recursion is skip-then-take with a base case at the end of the array."),
        ("backtracking", "One shared list is reused across the whole search tree, which only works if every branch undoes what it added."),
    ],
    "stair-ways-table": [
        ("dp", "State, recurrence, base case — asked once where all three answers are obvious."),
        ("recurrence", "`dp[i] = dp[i-1] + dp[i-2]`, because the last move was a 1-step or a 2-step and those cases do not overlap."),
    ],
    "grid-paths-table": [
        ("dp2d", "A 1-D table with a second index; the only new question is which fill orders the recurrence permits."),
        ("dp", "The table's meaning has to be stated before the loop is written, exactly as in 1-D."),
    ],
    "trie-insert-lookup": [
        ("trie", "Insert and exact lookup, and the `isWord` flag that is not the same as \"has no children\"."),
        ("char_arrays", "Both operations walk the query one character at a time, mapping it to a child index."),
    ],
    "activity-selection-small": [
        ("greedy", "A sort order plus a local rule — and the exchange argument that proves the pair correct."),
        ("intervals", "Sorting by end time is the move that makes almost every interval problem tractable."),
    ],
})

JAVA_STARTERS.update({
    "fixed-window-max-sum": _java(
        _J_ARRAY_READ.replace("int n = sc.nextInt();", "int n = sc.nextInt(), k = sc.nextInt();")
        + "        // TODO: sum the first k elements, then slide the window one step at a time\n"
        "        System.out.println(0);\n"
    ),
    "window-covering-letters": _java(
        "        String s = sc.next();\n"
        "        String req = sc.next();\n"
        "        // TODO: grow the right edge until every character of req is inside the window\n"
        "        System.out.println(-1);\n"
    ),
    "lower-bound-index": _java(
        _J_ARRAY_READ
        + "        int x = sc.nextInt();\n"
        "        int lo = 0, hi = n;\n"
        "        // TODO: while (lo < hi) narrow the half-open range [lo, hi)\n"
        "        System.out.println(lo);\n"
    ),
    "first-true-predicate": _java(
        "        int n = sc.nextInt();\n"
        "        boolean[] f = new boolean[n];\n"
        "        for (int i = 0; i < n; i++) f[i] = sc.next().equals(\"T\");\n"
        "        int lo = 0, hi = n;\n"
        "        // TODO: same half-open search, with !f[mid] playing the role of a[mid] < x\n"
        "        System.out.println(lo < n ? lo : -1);\n"
    ),
    "max-bracket-depth": _java(
        "        String s = sc.next();\n"
        "        // TODO: a counter is the stack here. Track the max, and reject depth < 0\n"
        "        System.out.println(-1);\n"
    ),
    "count-connected-components": _java(
        _J_GRAPH_READ
        + "        boolean[] seen = new boolean[n];\n"
        "        int comps = 0;\n"
        "        // TODO: for every unseen s, count a component and BFS from it\n"
        "        //       (mark a node seen when you ENQUEUE it)\n"
        "        System.out.println(comps);\n"
    ),
    "detect-cycle-tiny-dag": _java(
        "        int n = sc.nextInt(), m = sc.nextInt();\n"
        "        List<List<Integer>> g = new ArrayList<>();\n"
        "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
        "        int[] indeg = new int[n];\n"
        "        for (int i = 0; i < m; i++) {\n"
        "            int u = sc.nextInt(), v = sc.nextInt();\n"
        "            g.get(u).add(v);\n"
        "            indeg[v]++;\n"
        "        }\n"
        "        // TODO: Kahn — seed the queue with in-degree 0, count how many come out\n"
        "        System.out.println(\"NO\");\n"
    ),
    "grid-bfs-distance": _java(
        "        int H = sc.nextInt(), W = sc.nextInt();\n"
        "        char[][] g = new char[H][];\n"
        "        for (int i = 0; i < H; i++) g[i] = sc.next().toCharArray();\n"
        "        int[][] dist = new int[H][W];\n"
        "        for (int[] row : dist) Arrays.fill(row, -1);\n"
        "        int[] dr = {-1, 1, 0, 0}, dc = {0, 0, -1, 1};\n"
        "        // TODO: find S, BFS with dist doubling as the visited marker, print dist at G\n"
        "        System.out.println(-1);\n"
    ),
    "union-by-size-components": _java(
        "        int n = sc.nextInt(), m = sc.nextInt();\n"
        "        int[] parent = new int[n], size = new int[n];\n"
        "        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }\n"
        "        int comps = n;\n"
        "        // TODO: find by plain walk (no compression); union the smaller root under the larger\n"
        "        for (int i = 0; i < m; i++) {\n"
        "            int u = sc.nextInt(), v = sc.nextInt();\n"
        "        }\n"
        "        System.out.println(comps);\n"
    ),
    "all-subsets-small": _java(
        "        int n = sc.nextInt();\n"
        "        int[] a = new int[n];\n"
        "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
        "        List<String> out = new ArrayList<>();\n"
        "        // TODO: rec(i, chosen) — skip a[i], then take a[i], then UNDO the take\n"
        "        Collections.sort(out);\n"
        "        System.out.println(String.join(\"\\n\", out));\n"
    ),
    "stair-ways-table": _java(
        "        int n = sc.nextInt();\n"
        "        long[] dp = new long[n + 1];\n"
        "        // TODO: dp[0] = 1, then fill i = 1..n from dp[i-1] and dp[i-2]\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i = 0; i <= n; i++) { if (i > 0) sb.append(' '); sb.append(dp[i]); }\n"
        "        System.out.println(sb.toString());\n"
    ),
    "grid-paths-table": _java(
        "        int H = sc.nextInt(), W = sc.nextInt();\n"
        "        long[][] dp = new long[H][W];\n"
        "        // TODO: dp[0][0] = 1, then fill row by row from above and from the left\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i = 0; i < H; i++) {\n"
        "            for (int j = 0; j < W; j++) { if (j > 0) sb.append(' '); sb.append(dp[i][j]); }\n"
        "            sb.append('\\n');\n"
        "        }\n"
        "        System.out.print(sb);\n"
    ),
    "trie-insert-lookup": _java(
        "        int n = sc.nextInt();\n"
        "        String[] words = new String[n];\n"
        "        for (int i = 0; i < n; i++) words[i] = sc.next();\n"
        "        int q = sc.nextInt();\n"
        "        String[] queries = new String[q];\n"
        "        for (int i = 0; i < q; i++) queries[i] = sc.next();\n"
        "        // TODO: build a Node { Node[] next = new Node[26]; boolean isWord; } trie,\n"
        "        //       insert every word, then answer each query on isWord\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int i = 0; i < q; i++) sb.append(\"NO\").append('\\n');\n"
        "        System.out.print(sb);\n"
    ),
    "activity-selection-small": _java(
        "        int n = sc.nextInt();\n"
        "        int[][] jobs = new int[n][2];\n"
        "        for (int i = 0; i < n; i++) { jobs[i][0] = sc.nextInt(); jobs[i][1] = sc.nextInt(); }\n"
        "        // TODO: sort by end time, then take every job starting at or after lastEnd\n"
        "        System.out.println(0);\n"
    ),
})


# ---------------------------------------------------------------------------
# Reference solutions in each shipped language, merged into REFERENCE_SOLUTIONS
# so `verify_seeds` proves each on-ramp is actually solvable by the judge — an
# entry problem whose tests are wrong is worse than no entry problem.
# ---------------------------------------------------------------------------

ONRAMP_REFS = {
    "fixed-window-max-sum": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n, k = int(d[0]), int(d[1])\na = list(map(int, d[2:2 + n]))\n"
            "w = sum(a[:k])\nbest = w\n"
            "for r in range(k, n):\n    w += a[r] - a[r - k]\n    best = max(best, w)\n"
            "print(best)\n"
        ),
        "java": _java(
            "        int n = sc.nextInt(), k = sc.nextInt();\n"
            "        int[] a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        long w = 0;\n"
            "        for (int i = 0; i < k; i++) w += a[i];\n"
            "        long best = w;\n"
            "        for (int r = k; r < n; r++) { w += a[r] - a[r - k]; best = Math.max(best, w); }\n"
            "        System.out.println(best);\n"
        ),
    },
    "lower-bound-index": {
        "python": (
            "import sys\nd = sys.stdin.read().split()\n"
            "n = int(d[0])\na = list(map(int, d[1:1 + n]))\nx = int(d[1 + n])\n"
            "lo, hi = 0, n\n"
            "while lo < hi:\n    mid = lo + (hi - lo) // 2\n"
            "    if a[mid] < x: lo = mid + 1\n    else: hi = mid\n"
            "print(lo)\n"
        ),
        "java": _java(
            "        int n = sc.nextInt();\n"
            "        int[] a = new int[n];\n"
            "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
            "        int x = sc.nextInt();\n"
            "        int lo = 0, hi = n;\n"
            "        while (lo < hi) {\n"
            "            int mid = lo + (hi - lo) / 2;\n"
            "            if (a[mid] < x) lo = mid + 1; else hi = mid;\n"
            "        }\n"
            "        System.out.println(lo);\n"
        ),
    },
    "count-connected-components": {
        "python": (
            "import sys\nfrom collections import deque\n"
            "L = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, L[0].split())\n"
            "g = [[] for _ in range(n)]\n"
            "for i in range(m):\n"
            "    u, v = map(int, L[1 + i].split())\n    g[u].append(v)\n    g[v].append(u)\n"
            "seen = [False] * n\ncomps = 0\n"
            "for s in range(n):\n"
            "    if seen[s]: continue\n    comps += 1\n    seen[s] = True\n"
            "    q = deque([s])\n"
            "    while q:\n        u = q.popleft()\n"
            "        for v in g[u]:\n            if not seen[v]:\n                seen[v] = True\n"
            "                q.append(v)\n"
            "print(comps)\n"
        ),
        "java": _java(
            "        int n = sc.nextInt(), m = sc.nextInt();\n"
            "        List<List<Integer>> g = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) g.add(new ArrayList<>());\n"
            "        for (int i = 0; i < m; i++) {\n"
            "            int u = sc.nextInt(), v = sc.nextInt();\n"
            "            g.get(u).add(v); g.get(v).add(u);\n"
            "        }\n"
            "        boolean[] seen = new boolean[n];\n"
            "        int comps = 0;\n"
            "        for (int s = 0; s < n; s++) {\n"
            "            if (seen[s]) continue;\n"
            "            comps++; seen[s] = true;\n"
            "            Deque<Integer> q = new ArrayDeque<>();\n"
            "            q.add(s);\n"
            "            while (!q.isEmpty()) {\n"
            "                int u = q.poll();\n"
            "                for (int v : g.get(u)) if (!seen[v]) { seen[v] = true; q.add(v); }\n"
            "            }\n"
            "        }\n"
            "        System.out.println(comps);\n"
        ),
    },
    "grid-bfs-distance": {
        "python": (
            "import sys\nfrom collections import deque\n"
            "L = sys.stdin.read().split('\\n')\n"
            "H, W = map(int, L[0].split())\n"
            "g = [L[1 + i] for i in range(H)]\n"
            "dist = [[-1] * W for _ in range(H)]\n"
            "si = sj = gi = gj = 0\n"
            "for i in range(H):\n"
            "    for j in range(W):\n"
            "        if g[i][j] == 'S': si, sj = i, j\n"
            "        elif g[i][j] == 'G': gi, gj = i, j\n"
            "dist[si][sj] = 0\nq = deque([(si, sj)])\n"
            "while q:\n    i, j = q.popleft()\n"
            "    for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):\n"
            "        ni, nj = i + di, j + dj\n"
            "        if 0 <= ni < H and 0 <= nj < W and g[ni][nj] != '#' and dist[ni][nj] < 0:\n"
            "            dist[ni][nj] = dist[i][j] + 1\n            q.append((ni, nj))\n"
            "print(dist[gi][gj])\n"
        ),
        "java": _java(
            "        int H = sc.nextInt(), W = sc.nextInt();\n"
            "        char[][] g = new char[H][];\n"
            "        for (int i = 0; i < H; i++) g[i] = sc.next().toCharArray();\n"
            "        int[][] dist = new int[H][W];\n"
            "        for (int[] row : dist) Arrays.fill(row, -1);\n"
            "        int si = 0, sj = 0, gi = 0, gj = 0;\n"
            "        for (int i = 0; i < H; i++) for (int j = 0; j < W; j++) {\n"
            "            if (g[i][j] == 'S') { si = i; sj = j; }\n"
            "            else if (g[i][j] == 'G') { gi = i; gj = j; }\n"
            "        }\n"
            "        int[] dr = {-1, 1, 0, 0}, dc = {0, 0, -1, 1};\n"
            "        dist[si][sj] = 0;\n"
            "        Deque<int[]> q = new ArrayDeque<>();\n"
            "        q.add(new int[]{si, sj});\n"
            "        while (!q.isEmpty()) {\n"
            "            int[] cur = q.poll();\n"
            "            for (int d = 0; d < 4; d++) {\n"
            "                int ni = cur[0] + dr[d], nj = cur[1] + dc[d];\n"
            "                if (ni < 0 || ni >= H || nj < 0 || nj >= W) continue;\n"
            "                if (g[ni][nj] == '#' || dist[ni][nj] >= 0) continue;\n"
            "                dist[ni][nj] = dist[cur[0]][cur[1]] + 1;\n"
            "                q.add(new int[]{ni, nj});\n"
            "            }\n"
            "        }\n"
            "        System.out.println(dist[gi][gj]);\n"
        ),
    },
    "union-by-size-components": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n, m = map(int, L[0].split())\n"
            "parent = list(range(n))\nsize = [1] * n\ncomps = n\n"
            "def find(x):\n    while parent[x] != x: x = parent[x]\n    return x\n"
            "for i in range(m):\n"
            "    u, v = map(int, L[1 + i].split())\n"
            "    a, b = find(u), find(v)\n"
            "    if a == b: continue\n"
            "    if size[a] < size[b]: a, b = b, a\n"
            "    parent[b] = a\n    size[a] += size[b]\n    comps -= 1\n"
            "print(comps)\n"
        ),
        "java": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static int[] parent, size;\n"
            "    static int find(int x) { while (parent[x] != x) x = parent[x]; return x; }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt(), m = sc.nextInt();\n"
            "        parent = new int[n]; size = new int[n];\n"
            "        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }\n"
            "        int comps = n;\n"
            "        for (int i = 0; i < m; i++) {\n"
            "            int a = find(sc.nextInt()), b = find(sc.nextInt());\n"
            "            if (a == b) continue;\n"
            "            if (size[a] < size[b]) { int t = a; a = b; b = t; }\n"
            "            parent[b] = a; size[a] += size[b]; comps--;\n"
            "        }\n"
            "        System.out.println(comps);\n"
            "    }\n"
            "}\n"
        ),
    },
    "stair-ways-table": {
        "python": (
            "n = int(input())\ndp = [0] * (n + 1)\ndp[0] = 1\n"
            "for i in range(1, n + 1):\n    dp[i] = dp[i - 1] + (dp[i - 2] if i >= 2 else 0)\n"
            "print(' '.join(map(str, dp)))\n"
        ),
        "java": _java(
            "        int n = sc.nextInt();\n"
            "        long[] dp = new long[n + 1];\n"
            "        dp[0] = 1;\n"
            "        for (int i = 1; i <= n; i++) dp[i] = dp[i - 1] + (i >= 2 ? dp[i - 2] : 0);\n"
            "        StringBuilder sb = new StringBuilder();\n"
            "        for (int i = 0; i <= n; i++) { if (i > 0) sb.append(' '); sb.append(dp[i]); }\n"
            "        System.out.println(sb.toString());\n"
        ),
    },
    "trie-insert-lookup": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\nwords = L[1:1 + n]\n"
            "q = int(L[1 + n])\nqueries = L[2 + n:2 + n + q]\n"
            "root = {}\n"
            "for w in words:\n"
            "    node = root\n"
            "    for ch in w: node = node.setdefault(ch, {})\n"
            "    node['$'] = True\n"
            "res = []\n"
            "for t in queries:\n"
            "    node = root\n    ok = True\n"
            "    for ch in t:\n"
            "        if ch not in node: ok = False; break\n"
            "        node = node[ch]\n"
            "    res.append('YES' if ok and '$' in node else 'NO')\n"
            "print('\\n'.join(res))\n"
        ),
        "java": (
            "import java.util.*;\n\n"
            "public class Main {\n"
            "    static class Node { Node[] next = new Node[26]; boolean isWord; }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        int n = sc.nextInt();\n"
            "        Node root = new Node();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            String w = sc.next();\n"
            "            Node cur = root;\n"
            "            for (char c : w.toCharArray()) {\n"
            "                int k = c - 'a';\n"
            "                if (cur.next[k] == null) cur.next[k] = new Node();\n"
            "                cur = cur.next[k];\n"
            "            }\n"
            "            cur.isWord = true;\n"
            "        }\n"
            "        int q = sc.nextInt();\n"
            "        StringBuilder sb = new StringBuilder();\n"
            "        for (int i = 0; i < q; i++) {\n"
            "            String t = sc.next();\n"
            "            Node cur = root;\n"
            "            boolean ok = true;\n"
            "            for (char c : t.toCharArray()) {\n"
            "                int k = c - 'a';\n"
            "                if (cur.next[k] == null) { ok = false; break; }\n"
            "                cur = cur.next[k];\n"
            "            }\n"
            "            sb.append(ok && cur.isWord ? \"YES\" : \"NO\").append('\\n');\n"
            "        }\n"
            "        System.out.print(sb);\n"
            "    }\n"
            "}\n"
        ),
    },
    "activity-selection-small": {
        "python": (
            "import sys\nL = sys.stdin.read().strip().split('\\n')\n"
            "n = int(L[0])\n"
            "jobs = sorted((tuple(map(int, L[1 + i].split())) for i in range(n)), key=lambda t: t[1])\n"
            "count = 0\nlast = -10 ** 9\n"
            "for s, e in jobs:\n"
            "    if s >= last:\n        count += 1\n        last = e\n"
            "print(count)\n"
        ),
        "java": _java(
            "        int n = sc.nextInt();\n"
            "        int[][] jobs = new int[n][2];\n"
            "        for (int i = 0; i < n; i++) { jobs[i][0] = sc.nextInt(); jobs[i][1] = sc.nextInt(); }\n"
            "        Arrays.sort(jobs, (p, q) -> Integer.compare(p[1], q[1]));\n"
            "        int count = 0, last = Integer.MIN_VALUE;\n"
            "        for (int[] j : jobs) if (j[0] >= last) { count++; last = j[1]; }\n"
            "        System.out.println(count);\n"
        ),
    },
}
