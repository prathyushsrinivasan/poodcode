# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 9 — intervals and dynamic programming.
#
#   summary-ranges                 a run ends where the next value is not one more
#   remove-covered-intervals       sort by start asc, end desc; covered means end ≤ max end so far
#   my-calendar                    an ordered set: check only the neighbours of the new booking
#   video-stitching                interval covering as jump game: extend to the furthest reach
#   min-interval-per-query         offline queries + a heap of candidate intervals
#   perfect-squares                unbounded-knapsack DP over n
#   house-robber-ii                a circle is two lines: drop the first or the last house
#   delete-and-earn                bucket by value, then it is House Robber over values
#   min-path-sum                   grid DP, one row of state
#   distinct-subsequences          count matchings: skip s[i], or use it for t[j]
# ===========================================================================

_p(
    "summary-ranges", "Summary Ranges", "Easy",
    topics=["Intervals", "Arrays"], subtopics=["Intervals", "Two Pointers"], companies=["Google", "Yandex"],
    shape="arr", ret="String", todo="extend a run while the next value is exactly one more, then emit it",
    description=(
        "Given a sorted array of **distinct** integers, summarise it as the fewest ranges that "
        "cover exactly its values. Write a range of one value as `a` and a longer one as `a->b`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` sorted, distinct integers.\n\n"
        "### Output\nThe ranges, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 20\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "A range continues while the next value is exactly one more than the current one.",
        "Keep the start of the current run. When the run breaks (or the array ends), emit it.",
        "Compare with `a[i + 1] − a[i] == 1` using long arithmetic: the values span the whole int range.",
    ],
    opt=("O(n)", "O(1)", "One pass with a pointer to the start of the current run."),
    editorial=(
        "## The one thing this teaches\n**Runs are found by comparing neighbours.** Sorted input "
        "means every maximal run of consecutive values is contiguous in the array, so one pass "
        "that checks `a[i + 1] == a[i] + 1` finds every boundary.\n\n"
        "## Approach\n```java\nint i = 0;\nwhile (i < n) {\n    int start = i;\n"
        "    while (i + 1 < n && (long) a[i + 1] - a[i] == 1) i++;\n"
        "    out.add(start == i ? \"\" + a[i] : a[start] + \"->\" + a[i]);\n    i++;\n}\n```\n\n"
        "## The overflow\n`a[i] + 1` with `a[i] == Integer.MAX_VALUE` wraps to `MIN_VALUE`, and "
        "`a[i + 1] − a[i]` between the two ends of the int range overflows too. Doing the "
        "difference in `long` makes the test exact for every input."
    ),
    py='''
def solve(a):
    out = []
    i, n = 0, len(a)
    while i < n:
        start = i
        while i + 1 < n and a[i + 1] - a[i] == 1:
            i += 1
        out.append(str(a[i]) if start == i else f"{a[start]}->{a[i]}")
        i += 1
    return " ".join(out)
''',
    java='''
    static String solve(int[] a) {
        StringBuilder sb = new StringBuilder();
        int i = 0, n = a.length;
        while (i < n) {
            int start = i;
            while (i + 1 < n && (long) a[i + 1] - a[i] == 1) i++;
            if (sb.length() > 0) sb.append(' ');
            if (start == i) sb.append(a[i]);
            else sb.append(a[start]).append("->").append(a[i]);
            i++;
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "6\n0 1 2 4 5 7\n"), ("Example 2", "7\n0 2 3 4 6 8 9\n")],
    hidden=[
        ("Single value", "1\n-1\n"),
        ("Negative run", "3\n-3 -2 -1\n"),
        ("No runs", "4\n1 3 5 7\n"),
        ("Extremes of int", "3\n-2147483648 0 2147483647\n"),
    ],
    expl=[
        "Runs 0–2 and 4–5, and 7 alone.",
        "0 alone, 2–4, 6 alone, 8–9.",
    ],
    prereqs=[
        ("intervals", "Each maximal run of consecutive values is written as one range."),
        ("overflow", "Neighbour differences computed in long so the int extremes cannot wrap."),
    ],
)

_p(
    "remove-covered-intervals", "Remove Covered Intervals", "Medium",
    topics=["Intervals", "Sorting"], subtopics=["Intervals", "Sorting"], companies=["Google"],
    shape="pairs", ret="int", todo="sort by start ascending and end descending; count intervals whose end exceeds the max end so far",
    description=(
        "Interval `[a, b)` is **covered** by `[c, d)` if `c ≤ a` and `b ≤ d`. Remove every "
        "interval covered by another one and print how many remain.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `a b`.\n\n### Output\nThe number of remaining intervals."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ a < b ≤ 10^5\nAll intervals are distinct.",
    hints=[
        "Checking every pair is O(n²) — fine here, but there is a one-pass answer after sorting.",
        "Sort by start. Among equal starts, put the LONGER interval first, so it can cover the shorter ones.",
        "Walk in that order keeping the largest end seen. An interval is covered exactly when its end ≤ that maximum.",
    ],
    opt=("O(n log n)", "O(1)", "One sort with a two-key comparator, then one pass."),
    editorial=(
        "## The one thing this teaches\n**Choose the sort order so a single variable decides the "
        "question.** After sorting by start, every earlier interval starts at or before the "
        "current one, so the start condition of \"covered\" is automatic. What remains is the "
        "end condition — and one running maximum answers it.\n\n"
        "## Approach\n```java\nArrays.sort(iv, (x, y) -> x[0] != y[0] ? x[0] - y[0] : y[1] - x[1]);\n"
        "int kept = 0, maxEnd = 0;\nfor (int[] x : iv)\n"
        "    if (x[1] > maxEnd) { kept++; maxEnd = x[1]; }\n```\n\n"
        "## Why the tie-break is descending\nWith `[1, 2)` and `[1, 4)`, sorting ends ascending "
        "processes `[1, 2)` first, finds nothing covering it, and keeps it — even though `[1, 4)` "
        "does. Putting the longer interval first lets it raise `maxEnd` before the shorter one is "
        "judged."
    ),
    py='''
def solve(p):
    iv = sorted(p, key=lambda x: (x[0], -x[1]))
    kept = 0
    max_end = 0
    for a, b in iv:
        if b > max_end:
            kept += 1
            max_end = b
    return kept
''',
    java='''
    static int solve(int[][] iv) {
        Arrays.sort(iv, (x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0]) : Integer.compare(y[1], x[1]));
        int kept = 0, maxEnd = 0;
        for (int[] x : iv)
            if (x[1] > maxEnd) { kept++; maxEnd = x[1]; }
        return kept;
    }
''',
    examples=[("Example 1", "3\n1 4\n3 6\n2 8\n"), ("Example 2", "2\n1 4\n2 3\n")],
    hidden=[
        ("Single interval", "1\n0 10\n"),
        ("Same start, tie-break matters", "3\n1 2\n1 4\n3 4\n"),
        ("Mixed", "4\n3 10\n4 10\n5 11\n1 2\n"),
    ],
    expl=[
        "`[3, 6)` is covered by `[2, 8)`; the other two remain.",
        "`[2, 3)` lies inside `[1, 4)`.",
    ],
    prereqs=[
        ("intervals", "Covering as a pair of conditions on starts and ends."),
        ("sorting", "Start ascending with end descending on ties, so one running max decides coverage."),
    ],
)

_p(
    "my-calendar", "My Calendar (No Double Booking)", "Medium",
    topics=["Intervals", "Design"], subtopics=["Intervals", "Design", "Binary Search"], companies=["Google", "Uber"],
    shape="ops", ret="String", todo="keep bookings ordered by start; a new one must end before the next starts and start after the previous ends",
    description=(
        "Bookings arrive one at a time as half-open intervals `[start, end)`. Accept a booking only "
        "if it does not overlap any **accepted** booking.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: `book start end`.\n\n"
        "### Output\n`true` or `false` for each booking, one per line."
    ),
    constraints="1 ≤ q ≤ 1000\n0 ≤ start < end ≤ 10^9",
    hints=[
        "Checking against every accepted booking is O(q) per booking.",
        "Keep accepted bookings ordered by start. Only two can possibly overlap the new one: the one just before it and the one just after.",
        "In Java, a TreeMap from start to end: floorEntry(start) and ceilingEntry(start).",
    ],
    opt=("O(log q) per booking", "O(q)", "An ordered map; each booking checks two neighbours."),
    editorial=(
        "## The one thing this teaches\n**In an ordered set of disjoint intervals, only the "
        "neighbours matter.** Accepted bookings never overlap each other, so sorted by start they "
        "are also sorted by end. A new booking can only collide with the last booking starting at "
        "or before it, or the first booking starting after it.\n\n"
        "## Approach\n```java\nTreeMap<Integer, Integer> cal = new TreeMap<>();   // start -> end\n"
        "boolean book(int s, int e) {\n"
        "    Map.Entry<Integer, Integer> prev = cal.floorEntry(s), next = cal.ceilingEntry(s);\n"
        "    if (prev != null && prev.getValue() > s) return false;   // previous runs into us\n"
        "    if (next != null && next.getKey() < e) return false;     // we run into the next\n"
        "    cal.put(s, e);\n    return true;\n}\n```\n\n"
        "## Half-open intervals\n`[10, 20)` and `[20, 30)` touch but do not overlap, which is why "
        "the comparisons are strict: `prev end > s` and `next start < e`. Half-open intervals "
        "make back-to-back bookings free of special cases."
    ),
    py='''
def solve(ops):
    starts, ends = [], []
    out = []
    for op in ops:
        s, e = int(op[1]), int(op[2])
        i = bisect_left(starts, s)
        ok = (i == len(starts) or starts[i] >= e) and (i == 0 or ends[i - 1] <= s)
        if ok:
            starts.insert(i, s)
            ends.insert(i, e)
        out.append("true" if ok else "false")
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        TreeMap<Integer, Integer> cal = new TreeMap<>();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            int s = Integer.parseInt(op[1]), e = Integer.parseInt(op[2]);
            Map.Entry<Integer, Integer> prev = cal.floorEntry(s), next = cal.ceilingEntry(s);
            boolean ok = (prev == null || prev.getValue() <= s) && (next == null || next.getKey() >= e);
            if (ok) cal.put(s, e);
            if (sb.length() > 0) sb.append('\\n');
            sb.append(ok);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3\nbook 10 20\nbook 15 25\nbook 20 30\n"),
        ("Example 2", "4\nbook 5 10\nbook 1 5\nbook 10 15\nbook 4 6\n"),
    ],
    hidden=[
        ("Single booking", "1\nbook 0 1\n"),
        ("Rejected bookings are not kept", "5\nbook 47 50\nbook 33 41\nbook 39 45\nbook 33 42\nbook 25 32\n"),
        ("Same start is always a clash", "2\nbook 5 6\nbook 5 100\n"),
    ],
    expl=[
        "The second booking overlaps `[10, 20)`. The third starts exactly when the first ends.",
        "Back-to-back bookings are accepted; `[4, 6)` overlaps two of them.",
    ],
    prereqs=[
        ("intervals", "Half-open intervals and the overlap test between two of them."),
        ("bst", "An ordered map supplies the booking just before and just after a start time."),
    ],
)

_p(
    "video-stitching", "Video Stitching", "Medium",
    topics=["Intervals", "Greedy"], subtopics=["Intervals", "Greedy"], companies=["Google"],
    shape="pairs_k", ret="int", todo="for each start, record the furthest clip end; then jump-game over time, counting clips",
    description=(
        "Clips cover time ranges `[start, end]` of a sporting event and may overlap. Choose the "
        "**fewest** clips that together cover the whole event `[0, T]`.\n\n"
        "### Input\n- Line 1: `n T`.\n- Next `n` lines: `start end`.\n\n"
        "### Output\nThe minimum number of clips, or `-1` if the event cannot be covered."
    ),
    constraints="1 ≤ n ≤ 100\n0 ≤ start ≤ end ≤ 100\n1 ≤ T ≤ 100",
    hints=[
        "Covering from time 0, the first clip must start at 0 — and it should be the one reaching furthest.",
        "Generally: among clips starting at or before where coverage currently ends, take the one reaching furthest.",
        "Precompute reach[t] = furthest end of a clip starting at t. Then it is Jump Game II over time.",
    ],
    opt=("O(n + T)", "O(T)", "One pass to bucket clips by start, one sweep over time."),
    editorial=(
        "## The one thing this teaches\n**Interval covering is a jump game.** Standing at the end "
        "of the current coverage, the clips you can use are those starting at or before it, and "
        "the best one reaches furthest. That is exactly Jump Game II with `reach[t]` as the jump "
        "length from position `t`.\n\n"
        "## Approach\n```java\nint[] reach = new int[T + 1];\n"
        "for (int[] c : clips) if (c[0] <= T) reach[c[0]] = Math.max(reach[c[0]], c[1]);\n"
        "int clipsUsed = 0, covered = 0, furthest = 0;\nfor (int t = 0; t < T; t++) {\n"
        "    furthest = Math.max(furthest, reach[t]);\n"
        "    if (t == covered) {                      // must pick another clip here\n"
        "        if (furthest <= t) return -1;        // nothing extends past t: a gap\n"
        "        clipsUsed++;\n        covered = furthest;\n    }\n}\nreturn clipsUsed;\n```\n\n"
        "## Why greedy is safe\nAny solution must contain some clip covering time `covered`. Swapping "
        "it for the furthest-reaching clip available never uncovers anything and never increases "
        "the count."
    ),
    py='''
def solve(p, k):
    T = k
    reach = [0] * (T + 1)
    for a, b in p:
        if a <= T:
            reach[a] = max(reach[a], b)
    used = covered = furthest = 0
    for t in range(T):
        furthest = max(furthest, reach[t])
        if t == covered:
            if furthest <= t:
                return -1
            used += 1
            covered = furthest
    return used
''',
    java='''
    static int solve(int[][] clips, int T) {
        int[] reach = new int[T + 1];
        for (int[] c : clips) if (c[0] <= T) reach[c[0]] = Math.max(reach[c[0]], c[1]);
        int used = 0, covered = 0, furthest = 0;
        for (int t = 0; t < T; t++) {
            furthest = Math.max(furthest, reach[t]);
            if (t == covered) {
                if (furthest <= t) return -1;
                used++;
                covered = furthest;
            }
        }
        return used;
    }
''',
    examples=[
        ("Example 1", "6 10\n0 2\n4 6\n8 10\n1 9\n1 5\n5 9\n"),
        ("Example 2", "2 5\n0 1\n1 2\n"),
    ],
    hidden=[
        ("Many short clips", "16 9\n0 1\n6 8\n0 2\n5 6\n0 4\n0 3\n6 7\n1 3\n4 7\n1 4\n2 5\n2 6\n3 4\n4 5\n5 7\n6 9\n"),
        ("One clip past the end", "1 3\n0 5\n"),
        ("Unsorted input", "3 4\n1 4\n0 1\n2 3\n"),
        ("Nothing starts at zero", "2 3\n1 3\n2 3\n"),
    ],
    expl=[
        "`[0,2]`, `[1,9]`, `[8,10]`.",
        "Nothing covers time 2 to 5.",
    ],
    prereqs=[
        ("intervals", "Covering a range with the fewest intervals."),
        ("greedy", "At each coverage boundary, taking the clip that reaches furthest is optimal."),
    ],
)

_p(
    "min-interval-per-query", "Minimum Interval to Include Each Query", "Hard",
    topics=["Intervals", "Heap"], subtopics=["Intervals", "Priority Queue", "Sorting"], companies=["Google"],
    shape="pairs_q", ret="String", todo="sort intervals and queries; for each query push started intervals by size, pop ones that ended",
    description=(
        "For each query `x`, find the **size** of the smallest interval `[l, r]` with `l ≤ x ≤ r`, "
        "where the size is `r − l + 1`.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `l r`.\n- Then `q`.\n- Then `q` queries.\n\n"
        "### Output\nThe answers in the order the queries were given, separated by spaces (`-1` if none)."
    ),
    constraints="1 ≤ n, q ≤ 10^5\n1 ≤ l ≤ r ≤ 10^7\n1 ≤ x ≤ 10^7",
    hints=[
        "Scanning all intervals per query is O(n·q).",
        "Answer the queries in increasing order (remembering their original positions). Then intervals only ever START being relevant as x grows.",
        "Push every interval with l ≤ x into a min-heap keyed by size; pop from the top while its r < x. The top is the answer.",
    ],
    opt=("O((n + q) log n)", "O(n + q)", "Two sorts, and each interval enters and leaves the heap once."),
    editorial=(
        "## The one thing this teaches\n**Offline queries.** When all queries are known up front, "
        "you may answer them in whatever order is convenient and put the answers back. Sorting "
        "queries turns \"which intervals contain x?\" into a sweep where intervals are added as "
        "their start passes and discarded as their end passes.\n\n"
        "## Approach\n```java\nsort intervals by l; sort query indices by value;\n"
        "PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);   // {size, r}\n"
        "int i = 0;\nfor (int qi : sortedQueryIdx) {\n    int x = qs[qi];\n"
        "    while (i < n && iv[i][0] <= x) { pq.add(new int[]{iv[i][1] - iv[i][0] + 1, iv[i][1]}); i++; }\n"
        "    while (!pq.isEmpty() && pq.peek()[1] < x) pq.poll();     // ended before x\n"
        "    ans[qi] = pq.isEmpty() ? -1 : pq.peek()[0];\n}\n```\n\n"
        "## Why lazy popping is enough\nAn interval that ended before `x` also ended before every "
        "later query, so discarding it is permanent. And only the *top* needs to be valid: a "
        "stale interval buried under a smaller valid one never affects an answer until it "
        "surfaces, when it is removed."
    ),
    py='''
def solve(p, qs):
    iv = sorted(p)
    order = sorted(range(len(qs)), key=lambda i: qs[i])
    ans = [-1] * len(qs)
    h = []
    i = 0
    for qi in order:
        x = qs[qi]
        while i < len(iv) and iv[i][0] <= x:
            l, r = iv[i]
            heapq.heappush(h, (r - l + 1, r))
            i += 1
        while h and h[0][1] < x:
            heapq.heappop(h)
        ans[qi] = h[0][0] if h else -1
    return " ".join(map(str, ans))
''',
    java='''
    static String solve(int[][] iv, int[] qs) {
        Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
        Integer[] order = new Integer[qs.length];
        for (int i = 0; i < qs.length; i++) order[i] = i;
        Arrays.sort(order, (a, b) -> Integer.compare(qs[a], qs[b]));
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        int[] ans = new int[qs.length];
        int i = 0;
        for (int qi : order) {
            int x = qs[qi];
            while (i < iv.length && iv[i][0] <= x) { pq.add(new int[]{iv[i][1] - iv[i][0] + 1, iv[i][1]}); i++; }
            while (!pq.isEmpty() && pq.peek()[1] < x) pq.poll();
            ans[qi] = pq.isEmpty() ? -1 : pq.peek()[0];
        }
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < ans.length; k++) { if (k > 0) sb.append(' '); sb.append(ans[k]); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4\n1 4\n2 4\n3 6\n4 4\n4\n2 3 4 5\n"),
        ("Example 2", "4\n2 3\n2 5\n1 8\n20 25\n4\n2 19 5 22\n"),
    ],
    hidden=[
        ("Point interval", "1\n5 5\n3\n4 5 6\n"),
        ("Nested intervals", "2\n1 10\n3 4\n3\n3 5 10\n"),
        ("Queries out of order", "3\n1 3\n5 9\n2 6\n4\n9 1 4 7\n"),
    ],
    expl=[
        "Query 4 is inside `[4, 4]` (size 1); query 5 only inside `[3, 6]` (size 4).",
        "19 is in no interval.",
    ],
    prereqs=[
        ("heap", "A min-heap of started intervals by size, with ended ones removed lazily from the top."),
        ("sorting", "Answering queries in sorted order and writing each answer back to its original position."),
    ],
)

_p(
    "perfect-squares", "Perfect Squares", "Medium",
    topics=["Dynamic Programming", "Math"], subtopics=["1D DP"], companies=["Google", "Adobe"],
    shape="n", ret="int", todo="dp[x] = 1 + min(dp[x − s²]) over squares s² ≤ x",
    description=(
        "What is the fewest perfect squares (1, 4, 9, 16, …) that sum to `n`?\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe minimum count."
    ),
    constraints="1 ≤ n ≤ 10^4",
    hints=[
        "Greedily taking the largest square fails: 12 = 9 + 1 + 1 + 1, but 4 + 4 + 4 is shorter.",
        "The last square used is some s². Then the rest is the same problem for n − s².",
        "dp[0] = 0 and dp[x] = 1 + min over s with s² ≤ x of dp[x − s²]. Fill x upward.",
    ],
    opt=("O(n√n)", "O(n)", "n states, each trying at most √n squares."),
    editorial=(
        "## The one thing this teaches\n**Coin change with the coins generated.** The squares are "
        "the coin denominations, each usable any number of times, and the question is the fewest "
        "coins. The recurrence is the same one-dimensional DP over the amount.\n\n"
        "## Approach\n```java\nint[] dp = new int[n + 1];\nArrays.fill(dp, Integer.MAX_VALUE);\ndp[0] = 0;\n"
        "for (int x = 1; x <= n; x++)\n    for (int s = 1; s * s <= x; s++)\n"
        "        dp[x] = Math.min(dp[x], dp[x - s * s] + 1);\nreturn dp[n];\n```\n\n"
        "## Why greedy fails\nTaking the largest square that fits is the coin-change greedy, and "
        "the squares are not a coin system where greedy works: 12 greedily is `9+1+1+1` (4), "
        "optimally `4+4+4` (3).\n\n"
        "## The number theory answer\nLagrange: every integer is a sum of at most four squares, "
        "and Legendre characterises exactly which need four. That gives O(√n) — worth mentioning, "
        "not worth deriving in an interview."
    ),
    py='''
def solve(n):
    dp = [0] + [10 ** 9] * n
    for x in range(1, n + 1):
        s = 1
        while s * s <= x:
            dp[x] = min(dp[x], dp[x - s * s] + 1)
            s += 1
    return dp[n]
''',
    java='''
    static int solve(long nn) {
        int n = (int) nn;
        int[] dp = new int[n + 1];
        Arrays.fill(dp, Integer.MAX_VALUE);
        dp[0] = 0;
        for (int x = 1; x <= n; x++)
            for (int s = 1; s * s <= x; s++)
                dp[x] = Math.min(dp[x], dp[x - s * s] + 1);
        return dp[n];
    }
''',
    examples=[("Example 1", "12\n"), ("Example 2", "13\n")],
    hidden=[
        ("One", "1\n"),
        ("Needs four", "7\n"),
        ("A perfect square", "10000\n"),
        ("Three", "43\n"),
    ],
    expl=[
        "4 + 4 + 4.",
        "4 + 9.",
    ],
    prereqs=[
        ("dp", "dp over the target value, trying every square as the last term."),
        ("greedy", "The largest-square-first greedy fails here, which is why DP is needed."),
    ],
)

_p(
    "house-robber-ii", "House Robber II (Houses in a Circle)", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP"], companies=["Microsoft", "Amazon"],
    shape="arr", ret="long", todo="run House Robber on houses 0..n−2 and on 1..n−1; take the better",
    description=(
        "Houses stand in a **circle**, so the first and last are neighbours. You cannot rob two "
        "adjacent houses. What is the most money you can take?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` amounts.\n\n### Output\nThe maximum total."
    ),
    constraints="1 ≤ n ≤ 100\n0 ≤ amount ≤ 1000",
    hints=[
        "In a line, this is House Robber: best[i] = max(best[i−1], best[i−2] + a[i]).",
        "The circle only adds one constraint: not both the first and the last house.",
        "So either the first house is skipped or the last one is. Solve both lines and take the max. One house is a special case.",
    ],
    opt=("O(n)", "O(1)", "Two linear House Robber passes with rolling variables."),
    editorial=(
        "## The one thing this teaches\n**Break a cycle by fixing one decision.** A circular "
        "constraint has no starting point for a left-to-right DP. But in any valid choice, house "
        "0 or house n−1 is left out — so the answer is the better of two *linear* problems, each "
        "with one end removed.\n\n"
        "## Approach\n```java\nif (n == 1) return a[0];\nreturn Math.max(rob(a, 0, n - 2), rob(a, 1, n - 1));\n\n"
        "long rob(int[] a, int lo, int hi) {\n    long prev = 0, cur = 0;          // best up to i-2, i-1\n"
        "    for (int i = lo; i <= hi; i++) {\n        long next = Math.max(cur, prev + a[i]);\n"
        "        prev = cur;\n        cur = next;\n    }\n    return cur;\n}\n```\n\n"
        "## The overlap is fine\nBoth subproblems may skip *both* ends; that choice is counted "
        "twice, which does not matter for a maximum. The single-house case needs handling "
        "because removing an end from a one-house circle leaves nothing."
    ),
    py='''
def solve(a):
    if len(a) == 1:
        return a[0]

    def rob(xs):
        prev = cur = 0
        for x in xs:
            prev, cur = cur, max(cur, prev + x)
        return cur

    return max(rob(a[:-1]), rob(a[1:]))
''',
    java='''
    static long rob(int[] a, int lo, int hi) {
        long prev = 0, cur = 0;
        for (int i = lo; i <= hi; i++) {
            long next = Math.max(cur, prev + a[i]);
            prev = cur;
            cur = next;
        }
        return cur;
    }

    static long solve(int[] a) {
        int n = a.length;
        if (n == 1) return a[0];
        return Math.max(rob(a, 0, n - 2), rob(a, 1, n - 1));
    }
''',
    examples=[("Example 1", "3\n2 3 2\n"), ("Example 2", "4\n1 2 3 1\n")],
    hidden=[
        ("One house", "1\n5\n"),
        ("Two houses", "2\n1 9\n"),
        ("Line answer would use both ends", "5\n2 7 9 3 1\n"),
        ("Ends are the prize", "6\n5 1 1 5 1 1\n"),
    ],
    expl=[
        "Houses 0 and 2 are neighbours in the circle, so the best is house 1 alone.",
        "Houses 0 and 2: 1 + 3.",
    ],
    prereqs=[
        ("dp", "House Robber's two-state recurrence, run over a range."),
        ("array_patterns", "Removing one end turns the circle into a line."),
    ],
)

_p(
    "delete-and-earn", "Delete and Earn", "Medium",
    topics=["Dynamic Programming", "Hashing"], subtopics=["1D DP", "Counting"], companies=["Meta", "Amazon"],
    shape="arr", ret="long", todo="total points per value; then House Robber over values 0..max",
    description=(
        "Pick an element `x` to earn `x` points; every element equal to `x − 1` or `x + 1` is then "
        "deleted without earning anything. Repeat until the array is empty. What is the most you "
        "can earn?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe maximum points."
    ),
    constraints="1 ≤ n ≤ 2·10^4\n1 ≤ a[i] ≤ 10^4",
    hints=[
        "If you take one copy of x, you might as well take all copies — their neighbours are already gone.",
        "So each value v is worth v × count(v), and taking v forbids v − 1 and v + 1.",
        "That is House Robber over the values 1…max, with points[v] as the houses.",
    ],
    opt=("O(n + M)", "O(M)", "Bucket points by value, then a rolling DP over values up to the maximum M."),
    editorial=(
        "## The one thing this teaches\n**Re-index the problem until you recognise it.** Over the "
        "array positions this looks new. Over the *values* it is House Robber: adjacent values "
        "exclude each other, and each value is worth everything it contains.\n\n"
        "## Approach\n```java\nlong[] points = new long[max + 1];\nfor (int x : a) points[x] += x;\n"
        "long prev = 0, cur = 0;\nfor (int v = 0; v <= max; v++) {\n"
        "    long next = Math.max(cur, prev + points[v]);\n    prev = cur;\n    cur = next;\n}\nreturn cur;\n```\n\n"
        "## Why taking all copies is safe\nOnce one `x` is taken, every `x − 1` and `x + 1` is "
        "deleted, so the remaining copies of `x` have no one left to hurt. Choosing a value is "
        "all-or-nothing, which is what lets a single number, `points[x]`, represent it.\n\n"
        "When values are huge and sparse, sort the distinct values instead and treat two as "
        "adjacent only if they differ by exactly 1."
    ),
    py='''
def solve(a):
    m = max(a)
    points = [0] * (m + 1)
    for x in a:
        points[x] += x
    prev = cur = 0
    for p in points:
        prev, cur = cur, max(cur, prev + p)
    return cur
''',
    java='''
    static long solve(int[] a) {
        int max = 0;
        for (int x : a) max = Math.max(max, x);
        long[] points = new long[max + 1];
        for (int x : a) points[x] += x;
        long prev = 0, cur = 0;
        for (int v = 0; v <= max; v++) {
            long next = Math.max(cur, prev + points[v]);
            prev = cur;
            cur = next;
        }
        return cur;
    }
''',
    examples=[("Example 1", "3\n3 4 2\n"), ("Example 2", "6\n2 2 3 3 3 4\n")],
    hidden=[
        ("Single element", "1\n1\n"),
        ("Many small copies", "5\n1 1 1 2 4\n"),
        ("Consecutive run", "4\n10 11 12 13\n"),
        ("Gaps free both sides", "4\n1 3 5 7\n"),
    ],
    expl=[
        "Take 4 (deleting 3), then 2: 6.",
        "Take all three 3s (deleting the 2s and the 4): 9.",
    ],
    prereqs=[
        ("dp", "House Robber's recurrence over values instead of positions."),
        ("hashing", "Bucketing total points by value."),
    ],
)

_p(
    "min-path-sum", "Minimum Path Sum", "Medium",
    topics=["Dynamic Programming", "Matrix"], subtopics=["2D DP", "Grid"], companies=["Amazon", "Goldman Sachs"],
    shape="matrix", ret="long", todo="dp[i][j] = cell + min(from above, from the left); one row of state suffices",
    description=(
        "Move from the top-left to the bottom-right cell of a grid of non-negative numbers, only "
        "**right** or **down**. Minimise the sum of the numbers on the path.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` integers.\n\n### Output\nThe minimum path sum."
    ),
    constraints="1 ≤ r, c ≤ 200\n0 ≤ value ≤ 200",
    hints=[
        "A path reaches (i, j) either from (i − 1, j) or from (i, j − 1).",
        "So best[i][j] = grid[i][j] + min(best[i−1][j], best[i][j−1]), with the first row and column having only one option.",
        "Row i only needs row i − 1: keep one array and update it left to right.",
    ],
    opt=("O(r·c)", "O(c)", "One pass over the grid with a single row of DP state."),
    editorial=(
        "## The one thing this teaches\n**Grid DP, and rolling it to one row.** Because moves only "
        "go right or down, the best path to a cell depends only on the cell above and the cell to "
        "the left — both computed earlier in row-major order.\n\n"
        "## Approach\n```java\nlong[] dp = new long[c];\nfor (int i = 0; i < r; i++)\n"
        "    for (int j = 0; j < c; j++) {\n"
        "        if (i == 0 && j == 0) dp[j] = g[0][0];\n"
        "        else if (i == 0) dp[j] = dp[j - 1] + g[i][j];             // only from the left\n"
        "        else if (j == 0) dp[j] = dp[j] + g[i][j];                 // only from above\n"
        "        else dp[j] = Math.min(dp[j], dp[j - 1]) + g[i][j];\n    }\nreturn dp[c - 1];\n```\n\n"
        "Before the update, `dp[j]` still holds row `i − 1` (above); `dp[j − 1]` has already "
        "been updated to row `i` (left). One array carries both.\n\n"
        "## Why not Dijkstra\nIt would work, since values are non-negative. But with right/down "
        "moves the grid is a DAG, and a DAG's shortest path is a single pass in topological order "
        "— here, simply reading order."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    dp = [0] * c
    for i in range(r):
        for j in range(c):
            if i == 0 and j == 0:
                dp[j] = m[0][0]
            elif i == 0:
                dp[j] = dp[j - 1] + m[i][j]
            elif j == 0:
                dp[j] = dp[j] + m[i][j]
            else:
                dp[j] = min(dp[j], dp[j - 1]) + m[i][j]
    return dp[c - 1]
''',
    java='''
    static long solve(int[][] g) {
        int r = g.length, c = g[0].length;
        long[] dp = new long[c];
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                if (i == 0 && j == 0) dp[j] = g[0][0];
                else if (i == 0) dp[j] = dp[j - 1] + g[i][j];
                else if (j == 0) dp[j] = dp[j] + g[i][j];
                else dp[j] = Math.min(dp[j], dp[j - 1]) + g[i][j];
            }
        return dp[c - 1];
    }
''',
    examples=[("Example 1", "3 3\n1 3 1\n1 5 1\n4 2 1\n"), ("Example 2", "2 3\n1 2 3\n4 5 6\n")],
    hidden=[
        ("Single cell", "1 1\n0\n"),
        ("Single row", "1 4\n1 2 3 4\n"),
        ("Single column", "3 1\n5\n5\n5\n"),
        ("Detour through zeros", "3 3\n0 9 9\n0 9 9\n0 0 0\n"),
    ],
    expl=[
        "1 → 3 → 1 → 1 → 1 = 7.",
        "1 → 2 → 3 → 6 = 12.",
    ],
    prereqs=[
        ("dp2d", "Each cell's best path comes from the cell above or to the left."),
        ("grid", "Handling the first row and first column, which have only one predecessor."),
    ],
)

_p(
    "distinct-subsequences", "Distinct Subsequences", "Hard",
    topics=["Dynamic Programming", "Strings"], subtopics=["2D DP"], companies=["Google", "Bloomberg"],
    shape="str2", ret="long", todo="dp[j] = ways to form t[:j]; for each char of s, update j from the back when s[i] == t[j−1]",
    description=(
        "In how many different ways can `t` be obtained as a **subsequence** of `s` — that is, by "
        "choosing a set of positions in `s` whose letters, in order, spell `t`? Print the count "
        "modulo `10^9 + 7`.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `t`.\n\n### Output\nThe number of ways, mod `10^9 + 7`."
    ),
    constraints="1 ≤ |s|, |t| ≤ 1000\nBoth consist of English letters.",
    hints=[
        "Let ways[i][j] be the number of ways to form t[:j] from s[:i].",
        "The letter s[i−1] is either not used (ways[i−1][j]) or, if it equals t[j−1], used as the last letter (ways[i−1][j−1]).",
        "ways[i][0] = 1 (the empty target). With one row, update j from high to low so ways[i−1][j−1] is not overwritten first.",
    ],
    opt=("O(|s|·|t|)", "O(|t|)", "One pass over s, updating a row of |t| + 1 counts from the back."),
    editorial=(
        "## The one thing this teaches\n**Counting DP splits on the last choice.** Every way to "
        "form `t[:j]` from `s[:i]` either ignores `s[i−1]` or uses it to match `t[j−1]`. The two "
        "sets are disjoint, so their counts add:\n\n"
        "`ways[i][j] = ways[i−1][j] + (s[i−1] == t[j−1] ? ways[i−1][j−1] : 0)`\n\n"
        "## Approach — one row\n```java\nlong[] ways = new long[m + 1];\nways[0] = 1;\n"
        "for (int i = 0; i < n; i++)\n    for (int j = m; j >= 1; j--)          // back to front!\n"
        "        if (s.charAt(i) == t.charAt(j - 1)) ways[j] = (ways[j] + ways[j - 1]) % MOD;\n"
        "return ways[m];\n```\n\n"
        "## Why backwards\nThe update needs the *previous row's* `ways[j − 1]`. Iterating `j` "
        "upward overwrites it first, and a single `s` letter gets used twice — `s = \"a\"`, "
        "`t = \"aa\"` would count 1 instead of 0. The same reason 0/1 knapsack iterates capacity "
        "downward.\n\n"
        "## Why a modulus\nThe count grows exponentially — `s` of 1000 `a`s and `t` of 500 `a`s "
        "is C(1000, 500) — so even a `long` cannot hold it."
    ),
    py='''
def solve(s, t):
    MOD = 10 ** 9 + 7
    m = len(t)
    ways = [1] + [0] * m
    for ch in s:
        for j in range(m, 0, -1):
            if ch == t[j - 1]:
                ways[j] = (ways[j] + ways[j - 1]) % MOD
    return ways[m]
''',
    java='''
    static long solve(String s, String t) {
        final long MOD = 1_000_000_007L;
        int n = s.length(), m = t.length();
        long[] ways = new long[m + 1];
        ways[0] = 1;
        for (int i = 0; i < n; i++)
            for (int j = m; j >= 1; j--)
                if (s.charAt(i) == t.charAt(j - 1)) ways[j] = (ways[j] + ways[j - 1]) % MOD;
        return ways[m];
    }
''',
    examples=[("Example 1", "rabbbit\nrabbit\n"), ("Example 2", "babgbag\nbag\n")],
    hidden=[
        ("Target longer than source", "abc\nabcd\n"),
        ("Choose two of four", "aaaa\naa\n"),
        ("Single letter", "a\na\n"),
        ("No match", "xyz\nb\n"),
        ("Letter used once only", "a\naa\n"),
    ],
    expl=[
        "Any one of the three `b`s can be the one left out.",
        "Five different position sets spell `bag`.",
    ],
    prereqs=[
        ("dp2d", "A table over prefixes of both strings, reduced to one row updated from the back."),
        ("modulo", "The count grows exponentially and is reported modulo 1e9+7."),
    ],
)
