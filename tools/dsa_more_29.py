# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 29 — scheduling heaps, interval covering, searches and streams.
#
#   k-weakest-rows                  order rows by (soldier count, index)
#   process-tasks-using-servers     free servers by (weight, index); busy servers by free time
#   bag-of-tokens                   play the cheapest token up, the dearest token down
#   min-taps-to-water-garden        turn taps into reach per start point; then Jump Game II
#   longest-ones-after-deleting     a window holding at most one zero, minus the deleted element
#   find-min-rotated-duplicates     when the middle equals the right end, shrink the right end
#   ways-to-split-array             running prefix against total − prefix
#   elimination-game                track only the head, the step and the count
#   bst-floor-ceil                  one walk down: going right records a floor, left a ceiling
#   time-to-buy-tickets             people ahead buy at most t[k]; people behind at most t[k] − 1
#   data-stream-disjoint-intervals  an ordered map from start to end, merging neighbours on add
#   sum-of-prefix-scores            a trie whose nodes count how many words pass through
# ===========================================================================

_p(
    "k-weakest-rows", "The K Weakest Rows in a Matrix", "Easy",
    topics=["Heaps", "Binary Search", "Matrix"], subtopics=["Custom Ordering"], companies=["Amazon"],
    shape="matrix_k", ret="String", todo="count soldiers per row (they come first, so binary search works); order by (count, index) and take k",
    description=(
        "Each row of a 0/1 matrix lists its soldiers (1) before its civilians (0). Row `i` is "
        "**weaker** than row `j` if it has fewer soldiers, or the same number and `i < j`. Print "
        "the indices of the `k` weakest rows, weakest first.\n\n"
        "### Input\n- Line 1: `r c k`.\n- Next `r` lines: `c` values each.\n\n"
        "### Output\n`k` row indices separated by spaces."
    ),
    constraints="2 ≤ r, c ≤ 100\n1 ≤ k ≤ r",
    hints=[
        "The strength of a row is just its number of 1s.",
        "Because the 1s come first, the count is the index of the first 0 — a binary search.",
        "Sort the (count, index) pairs, or keep a max-heap of size k and evict the strongest.",
    ],
    opt=("O(r log c + r log k)", "O(k)", "A binary search per row and a bounded heap."),
    editorial=(
        "## The one thing this teaches\n**Encode tie-breaks in the comparison key.** \"Fewer "
        "soldiers, then smaller index\" is a pair compared lexicographically. Once the key is "
        "right, sorting or a heap does the rest.\n\n"
        "## Approach\n```java\nPriorityQueue<int[]> heap = new PriorityQueue<>((x, y) ->\n"
        "    x[0] != y[0] ? y[0] - x[0] : y[1] - x[1]);        // max-heap: strongest on top\n"
        "for (int i = 0; i < r; i++) {\n    heap.add(new int[]{soldiers(m[i]), i});\n"
        "    if (heap.size() > k) heap.poll();                 // drop the strongest\n}\n"
        "// pop all k and reverse to list weakest first\n```\n\n"
        "## Counting with binary search\n```java\nint soldiers(int[] row) {\n    int lo = 0, hi = row.length;\n"
        "    while (lo < hi) { int mid = (lo + hi) / 2; if (row[mid] == 1) lo = mid + 1; else hi = mid; }\n"
        "    return lo;                                         // index of the first 0\n}\n```\n\n"
        "## Why a max-heap for the smallest k\nThe heap keeps the k best candidates so far; the "
        "one to evict is the worst of them, which is exactly what a max-heap exposes."
    ),
    py='''
def solve(m, k):
    ranked = sorted(range(len(m)), key=lambda i: (sum(m[i]), i))
    return " ".join(map(str, ranked[:k]))
''',
    java='''
    static int soldiers(int[] row) {
        int lo = 0, hi = row.length;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (row[mid] == 1) lo = mid + 1; else hi = mid;
        }
        return lo;
    }

    static String solve(int[][] m, int k) {
        PriorityQueue<int[]> heap = new PriorityQueue<>((x, y) -> x[0] != y[0] ? y[0] - x[0] : y[1] - x[1]);
        for (int i = 0; i < m.length; i++) {
            heap.add(new int[]{soldiers(m[i]), i});
            if (heap.size() > k) heap.poll();
        }
        int[] out = new int[k];
        for (int i = k - 1; i >= 0; i--) out[i] = heap.poll()[1];
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < k; i++) { if (i > 0) sb.append(' '); sb.append(out[i]); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5 5 3\n1 1 0 0 0\n1 1 1 1 0\n1 0 0 0 0\n1 1 0 0 0\n1 1 1 1 1\n"),
        ("Example 2", "4 4 2\n1 0 0 0\n1 1 1 1\n1 0 0 0\n1 0 0 0\n"),
    ],
    hidden=[
        ("All rows", "3 2 3\n1 1\n0 0\n1 0\n"),
        ("Ties broken by index", "3 3 2\n1 0 0\n1 0 0\n1 0 0\n"),
        ("No soldiers at all", "2 3 1\n0 0 0\n0 0 0\n"),
        ("Full rows", "3 2 1\n1 1\n1 1\n1 0\n"),
    ],
    expl=[
        "Soldier counts are 2, 4, 1, 2, 5. The weakest are row 2 (1), then rows 0 and 3 (2 each).",
        "Rows 0, 2 and 3 have one soldier each; the two lowest indices are 0 and 2.",
    ],
    prereqs=[
        ("heap", "A bounded max-heap that keeps the k smallest keys."),
        ("binary_search", "Finding the first 0 in a row of 1s followed by 0s."),
    ],
)

_p(
    "process-tasks-using-servers", "Process Tasks Using Servers", "Medium",
    topics=["Heaps", "Simulation"], subtopics=["Two Heaps"], companies=["Amazon"],
    shape="arr2", ret="String", todo="free heap by (weight, index), busy heap by (free time, weight, index); if nothing is free, jump time to the earliest free time",
    description=(
        "Servers have weights; task `j` arrives at second `j` and runs for `tasks[j]` seconds. "
        "Tasks are assigned in order. A task goes to the free server with the **smallest weight** "
        "(then smallest index). If none is free, the task waits until a server frees up, and then "
        "the same rule applies to the servers free at that moment.\n\n"
        "Print the server index assigned to each task.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: server weights.\n- Line 3: `m`.\n- Line 4: task durations.\n\n"
        "### Output\n`m` server indices separated by spaces."
    ),
    constraints="1 ≤ n, m ≤ 2·10^5\n1 ≤ weight, duration ≤ 2·10^5",
    hints=[
        "Two questions repeat: which free server is best, and when does the next busy server finish?",
        "Keep a min-heap of free servers by (weight, index) and a min-heap of busy servers by free time.",
        "For task j at time t = max(j, time of the previous assignment): release every busy server with free time ≤ t. If none is free, set t to the earliest free time and release again. Free times can exceed an int.",
    ],
    opt=("O((n + m) log n)", "O(n)", "Each assignment and release is a heap operation."),
    editorial=(
        "## The one thing this teaches\n**Two heaps, two orderings, one clock.** Free servers are "
        "chosen by weight; busy servers come back by time. Moving servers between the heaps as "
        "the clock advances keeps both questions O(log n).\n\n"
        "## Approach\n```java\nlong time = 0;\nfor (int j = 0; j < m; j++) {\n"
        "    time = Math.max(time, j);\n    if (free.isEmpty()) time = Math.max(time, busy.peek()[0]);   // wait\n"
        "    while (!busy.isEmpty() && busy.peek()[0] <= time) free.add(release(busy.poll()));\n"
        "    int s = free.poll();\n    busy.add(new long[]{time + tasks[j], s});\n    answer[j] = s;\n}\n```\n\n"
        "## Why the clock never goes back\nTasks are assigned in order. A task delayed to time T "
        "forces every later task to be assigned at T or after.\n\n"
        "## Ties when servers come back together\nAll servers freeing at the same moment are "
        "released into the free heap before choosing, so the weight rule — not the release "
        "order — decides."
    ),
    py='''
def solve(a, b):
    free_at = [0] * len(a)
    out = []
    now = 0
    for j, duration in enumerate(b):
        now = max(now, j)
        if all(f > now for f in free_at):
            now = min(free_at)
        s = min((i for i in range(len(a)) if free_at[i] <= now), key=lambda i: (a[i], i))
        free_at[s] = now + duration
        out.append(s)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] w, int[] tasks) {
        int n = w.length, m = tasks.length;
        PriorityQueue<Integer> free = new PriorityQueue<>((x, y) -> w[x] != w[y] ? Integer.compare(w[x], w[y]) : Integer.compare(x, y));
        for (int i = 0; i < n; i++) free.add(i);
        PriorityQueue<long[]> busy = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
        long time = 0;
        StringBuilder sb = new StringBuilder();
        for (int j = 0; j < m; j++) {
            time = Math.max(time, j);
            if (free.isEmpty()) time = Math.max(time, busy.peek()[0]);
            while (!busy.isEmpty() && busy.peek()[0] <= time) free.add((int) busy.poll()[1]);
            int s = free.poll();
            busy.add(new long[]{time + tasks[j], s});
            if (j > 0) sb.append(' ');
            sb.append(s);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3\n3 3 2\n6\n1 2 3 2 1 2\n"),
        ("Example 2", "5\n5 1 4 3 2\n7\n2 1 2 4 5 2 1\n"),
    ],
    hidden=[
        ("One server queues everything", "1\n1\n3\n3 3 3\n"),
        ("Light server stays busy", "2\n2 1\n4\n5 1 1 1\n"),
        ("Equal weights", "3\n7 7 7\n4\n10 10 10 10\n"),
        ("Two free together", "2\n1 2\n3\n2 2 1\n"),
    ],
    expl=[
        "At 0 server 2 (weight 2) takes task 0; it is free again at 1 for task 1; at 2 servers 0 and 1 remain, so 0; then 2, 1, 2 as servers free up.",
        "Server 1 is lightest and takes every task it is free for; the others fill in when it is busy.",
    ],
    prereqs=[
        ("heap", "Min-heaps with composite keys for free and busy servers."),
        ("simulation", "An event clock that jumps to the next release when nothing is free."),
    ],
)

_p(
    "bag-of-tokens", "Bag of Tokens", "Medium",
    topics=["Greedy", "Two Pointers", "Sorting"], subtopics=["Two Pointers on Sorted Array"], companies=["Google"],
    shape="arr_k", ret="int", todo="sort; spend power on the cheapest token for +1 score, or trade 1 score for the most expensive token's power; track the best score",
    description=(
        "You start with `power` and score 0. Each token (value `t`) can be played **once**, in "
        "either way:\n\n"
        "- **face up**: needs power ≥ t; lose t power, gain 1 score;\n"
        "- **face down**: needs score ≥ 1; gain t power, lose 1 score.\n\n"
        "Print the maximum score reachable at any moment.\n\n"
        "### Input\n- Line 1: `n power`.\n- Line 2: the `n` token values.\n\n"
        "### Output\nThe maximum score."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ token, power ≤ 10^4",
    hints=[
        "Every face-up play gains the same 1 score — so it should cost as little power as possible.",
        "Every face-down play loses the same 1 score — so it should return as much power as possible.",
        "Sort. Play the smallest remaining token up while you can; otherwise, if you have score and more than one token remains, play the largest down. Record the best score along the way.",
    ],
    opt=("O(n log n)", "O(1)", "A sort, then two pointers moving inward."),
    editorial=(
        "## The one thing this teaches\n**When every action has the same reward, compare by "
        "cost alone.** Score changes by exactly 1 either way, so the only question is how much "
        "power moves — spend the least, receive the most. Sorting puts both extremes at the "
        "ends of the array.\n\n"
        "## Approach\n```java\nArrays.sort(tokens);\nint lo = 0, hi = n - 1, score = 0, best = 0;\n"
        "while (lo <= hi) {\n    if (power >= tokens[lo]) { power -= tokens[lo++]; best = Math.max(best, ++score); }\n"
        "    else if (score > 0 && lo < hi) { power += tokens[hi--]; score--; }\n    else break;\n}\nreturn best;\n```\n\n"
        "## Why track the best\nA final face-down play can lower the score for power that is "
        "never used. The answer is the highest score reached, not the last one.\n\n"
        "## Why `lo < hi` for face down\nTrading the very last token down gains power with "
        "nothing left to spend it on — it can only lose a point."
    ),
    py='''
def solve(a, k):
    from functools import lru_cache
    n = len(a)

    @lru_cache(maxsize=None)
    def best(used, power, score):
        result = score
        for i in range(n):
            if used >> i & 1:
                continue
            if power >= a[i]:
                result = max(result, best(used | 1 << i, power - a[i], score + 1))
            if score >= 1:
                result = max(result, best(used | 1 << i, power + a[i], score - 1))
        return result

    return best(0, k, 0)
''',
    java='''
    static int solve(int[] tokens, long p) {
        Arrays.sort(tokens);
        long power = p;
        int lo = 0, hi = tokens.length - 1, score = 0, best = 0;
        while (lo <= hi) {
            if (power >= tokens[lo]) { power -= tokens[lo++]; best = Math.max(best, ++score); }
            else if (score > 0 && lo < hi) { power += tokens[hi--]; score--; }
            else break;
        }
        return best;
    }
''',
    examples=[
        ("Example 1", "1 50\n100\n"),
        ("Example 2", "2 150\n200 100\n"),
        ("Example 3", "4 200\n100 200 300 400\n"),
    ],
    hidden=[
        ("Everything affordable", "3 100\n10 20 30\n"),
        ("No power", "3 0\n1 2 3\n"),
        ("Trade then spend", "5 25\n10 20 30 40 50\n"),
        ("Last token down would hurt", "3 5\n5 100 100\n"),
    ],
    expl=[
        "The only token costs more than the power available.",
        "Play 100 up for a score of 1; playing 200 down would drop the score back to 0.",
        "Play 100 up (score 1), 400 down (power 500, score 0), then 200 and 300 up: score 2.",
    ],
    prereqs=[
        ("greedy", "Cheapest-first spending and largest-first trading."),
        ("two_pointers", "Two pointers moving inward over a sorted array."),
    ],
)

_p(
    "min-taps-to-water-garden", "Minimum Number of Taps to Open to Water a Garden", "Hard",
    topics=["Greedy", "Dynamic Programming", "Intervals"], subtopics=["Interval Covering", "Jump Game II"], companies=["Google", "Amazon"],
    shape="arr", ret="int", todo="for each left end, store the furthest right end any tap reaches; then greedy jumps from 0 to n as in Jump Game II",
    description=(
        "A garden spans the points `0` to `n`. There are `n + 1` taps, one at each integer "
        "point; tap `i` with range `r` waters the interval `[i − r, i + r]`. Print the minimum "
        "number of taps to open so the whole garden `[0, n]` is watered, or `-1` if impossible.\n\n"
        "### Input\n- Line 1: `n + 1`, the number of taps.\n- Line 2: the `n + 1` ranges.\n\n"
        "### Output\nThe minimum number of taps, or `-1`."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ range ≤ 100",
    hints=[
        "Each tap is an interval, clamped to [0, n]. The task is to cover a segment with the fewest intervals.",
        "From a covered prefix [0, x], only intervals starting at or before x can extend it — and the best one reaches furthest.",
        "Record, for each start point, the furthest reach of any tap starting there. Then run Jump Game II: expand the window greedily, counting a tap each time you must jump past the current reach.",
    ],
    opt=("O(n + taps)", "O(n)", "One pass to build reaches, one greedy pass."),
    editorial=(
        "## The one thing this teaches\n**Interval covering is Jump Game II in disguise.** Clamp "
        "each tap to `[max(0, i − r), min(n, i + r)]` and store `reach[left] = max right`. From "
        "any covered point, the next tap to open is the one that reaches furthest — exactly the "
        "greedy that solves Jump Game II.\n\n"
        "## Approach\n```java\nint[] reach = new int[n + 1];\nfor (int i = 0; i <= n; i++) {\n"
        "    int l = Math.max(0, i - r[i]), rr = Math.min(n, i + r[i]);\n    reach[l] = Math.max(reach[l], rr);\n}\n"
        "int taps = 0, currentEnd = 0, furthest = 0;\nfor (int x = 0; x < n; x++) {\n"
        "    furthest = Math.max(furthest, reach[x]);\n    if (x == currentEnd) {                 // must open another tap here\n"
        "        if (furthest <= x) return -1;         // nothing reaches past x\n"
        "        taps++;\n        currentEnd = furthest;\n    }\n}\nreturn taps;\n```\n\n"
        "## Covering is continuous\nTaps covering `[0, 1]` and `[2, 3]` leave the open gap "
        "`(1, 2)` dry. The greedy sees this as `furthest <= x` at `x = 1`.\n\n"
        "## The DP alternative\n`best[x]` = fewest taps covering `[0, x]`, relaxed from each "
        "interval's left end in sorted order: O(n · range), simpler to prove, slower."
    ),
    py='''
def solve(a):
    n = len(a) - 1
    INF = float("inf")
    best = [INF] * (n + 1)
    best[0] = 0
    for left, right in sorted((max(0, i - r), min(n, i + r)) for i, r in enumerate(a)):
        if best[left] == INF:
            continue
        for x in range(left + 1, right + 1):
            best[x] = min(best[x], best[left] + 1)
    return -1 if best[n] == INF else best[n]
''',
    java='''
    static int solve(int[] r) {
        int n = r.length - 1;
        int[] reach = new int[n + 1];
        for (int i = 0; i <= n; i++) {
            int l = Math.max(0, i - r[i]), rr = Math.min(n, i + r[i]);
            reach[l] = Math.max(reach[l], rr);
        }
        int taps = 0, currentEnd = 0, furthest = 0;
        for (int x = 0; x < n; x++) {
            furthest = Math.max(furthest, reach[x]);
            if (x == currentEnd) {
                if (furthest <= x) return -1;
                taps++;
                currentEnd = furthest;
            }
        }
        return taps;
    }
''',
    examples=[("Example 1", "6\n3 4 1 1 0 0\n"), ("Example 2", "4\n0 0 0 0\n")],
    hidden=[
        ("Two ends", "9\n4 0 0 0 0 0 0 0 4\n"),
        ("Smallest garden", "2\n1 1\n"),
        ("One tap covers all", "6\n0 5 0 0 0 0\n"),
        ("Gap between taps", "4\n1 0 0 1\n"),
        ("Overlapping chain", "7\n1 1 1 1 1 1 1\n"),
    ],
    expl=[
        "Tap 1 with range 4 waters [−3, 5], the whole garden.",
        "No tap waters anything beyond its own point.",
    ],
    prereqs=[
        ("greedy", "Jump Game II: extend coverage as far as possible before each new choice."),
        ("intervals", "Clamping intervals to the garden and covering a segment."),
    ],
)

_p(
    "longest-ones-after-deleting", "Longest Subarray of 1s After Deleting One Element", "Medium",
    topics=["Sliding Window", "Arrays"], subtopics=["At Most One Zero"], companies=["Meta", "Yandex"],
    shape="arr", ret="int", todo="grow a window allowing at most one zero; the answer is the longest window minus one (the deleted element)",
    description=(
        "Delete **exactly one** element from a binary array. Print the length of the longest "
        "run of consecutive 1s in the result (0 if there is none).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` values, each 0 or 1.\n\n"
        "### Output\nThe longest run of 1s after one deletion."
    ),
    constraints="1 ≤ n ≤ 10^5",
    hints=[
        "Trying each deletion and rescanning is O(n²).",
        "After deleting one element, a run of 1s corresponds to a window of the original array containing at most one zero, minus the deleted cell.",
        "Slide a window that allows at most one zero. Its length minus 1 is a candidate — even when it contains no zero, since a deletion is mandatory.",
    ],
    opt=("O(n)", "O(1)", "One sliding window and a zero counter."),
    editorial=(
        "## The one thing this teaches\n**Translate the operation into a window condition.** "
        "\"Delete one element\" becomes \"a window may contain one zero, and its length counts one "
        "less\". The problem is then Max Consecutive Ones III with k = 1.\n\n"
        "## Approach\n```java\nint left = 0, zeros = 0, best = 0;\nfor (int right = 0; right < n; right++) {\n"
        "    if (a[right] == 0) zeros++;\n    while (zeros > 1) if (a[left++] == 0) zeros--;\n"
        "    best = Math.max(best, right - left);   // window length − 1\n}\nreturn best;\n```\n\n"
        "## The all-ones trap\nFor `1 1 1` the answer is 2, not 3: the deletion is not optional, "
        "so one of the 1s must go. `right − left` handles this without a special case.\n\n"
        "## Walkthrough: 0 1 1 1 0 1 1 0 1\nThe window `1 1 1 0 1 1` (indices 1–6) has one zero; "
        "deleting it leaves five 1s."
    ),
    py='''
def solve(a):
    best = 0
    for d in range(len(a)):
        rest = a[:d] + a[d + 1:]
        run = 0
        for v in rest:
            run = run + 1 if v == 1 else 0
            best = max(best, run)
    return best
''',
    java='''
    static int solve(int[] a) {
        int left = 0, zeros = 0, best = 0;
        for (int right = 0; right < a.length; right++) {
            if (a[right] == 0) zeros++;
            while (zeros > 1) if (a[left++] == 0) zeros--;
            best = Math.max(best, right - left);
        }
        return best;
    }
''',
    examples=[("Example 1", "4\n1 1 0 1\n"), ("Example 2", "9\n0 1 1 1 0 1 1 0 1\n"), ("Example 3", "3\n1 1 1\n")],
    hidden=[
        ("Single zero", "1\n0\n"),
        ("Single one", "1\n1\n"),
        ("All zeros", "5\n0 0 0 0 0\n"),
        ("Two zeros in a row", "6\n1 1 0 0 1 1\n"),
    ],
    expl=[
        "Delete the 0: 1 1 1.",
        "Delete the 0 at index 4: 1 1 1 1 1.",
        "A deletion is required, so one 1 goes.",
    ],
    prereqs=[
        ("sliding_window", "A window with at most one zero, shrinking from the left."),
        ("array_patterns", "Turning an edit operation into a condition on a subarray."),
    ],
)

_p(
    "find-min-rotated-duplicates", "Find Minimum in Rotated Sorted Array II", "Hard",
    topics=["Binary Search", "Arrays"], subtopics=["Rotated Array", "Duplicates"], companies=["Amazon", "Google"],
    shape="arr", ret="int", todo="compare a[mid] with a[hi]: greater → go right, smaller → hi = mid, equal → hi−− (one duplicate can be discarded safely)",
    description=(
        "A non-decreasing array was rotated at some unknown point, and it **may contain "
        "duplicates**. Print its minimum value.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe minimum."
    ),
    constraints="1 ≤ n ≤ 5000\n-5000 ≤ a[i] ≤ 5000",
    hints=[
        "Without duplicates, comparing a[mid] with a[hi] tells you which half holds the minimum.",
        "With duplicates, a[mid] == a[hi] says nothing: in 3 3 1 3 3 the minimum is to the left of mid, in 3 1 3 3 3 3 3 to the right.",
        "In the equal case, a[hi] has a copy at mid, so discarding a[hi] loses nothing: hi−−. That keeps correctness at the cost of O(n) in the worst case.",
    ],
    opt=("O(log n) average, O(n) worst", "O(1)", "All-equal arrays force one-step shrinking."),
    editorial=(
        "## The one thing this teaches\n**When a comparison is uninformative, make the smallest "
        "safe step.** Binary search relies on each comparison ruling out half. Equal values can "
        "hide the rotation point, so the search falls back to removing one element that is "
        "provably redundant.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n - 1;\nwhile (lo < hi) {\n    int mid = (lo + hi) / 2;\n"
        "    if (a[mid] > a[hi]) lo = mid + 1;          // rotation point is right of mid\n"
        "    else if (a[mid] < a[hi]) hi = mid;         // mid..hi is sorted; min is at mid or left\n"
        "    else hi--;                                 // a[hi] has a twin at mid\n}\nreturn a[lo];\n```\n\n"
        "## Why hi−− is safe\nIf `a[hi]` were the unique minimum, `a[mid]` would equal it and "
        "`mid < hi` — so it is not unique. Removing one copy leaves another in range.\n\n"
        "## The worst case is unavoidable\nIn `1 1 1 … 1 0 1 1 … 1`, any algorithm must look at "
        "almost every position to find the single 0, so O(n) is the true bound."
    ),
    py='''
def solve(a):
    return min(a)
''',
    java='''
    static int solve(int[] a) {
        int lo = 0, hi = a.length - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (a[mid] > a[hi]) lo = mid + 1;
            else if (a[mid] < a[hi]) hi = mid;
            else hi--;
        }
        return a[lo];
    }
''',
    examples=[("Example 1", "3\n1 3 5\n"), ("Example 2", "5\n2 2 2 0 1\n")],
    hidden=[
        ("Minimum left of the middle", "5\n3 3 1 3 3\n"),
        ("All equal", "4\n1 1 1 1\n"),
        ("Minimum hidden among equals", "7\n10 1 10 10 10 10 10\n"),
        ("Single element", "1\n-5\n"),
        ("Not rotated, with duplicates", "6\n-2 -2 0 0 4 4\n"),
    ],
    expl=[
        "Not rotated: the first element is the minimum.",
        "The rotation point is at the 0.",
    ],
    prereqs=[
        ("binary_search", "Binary search on a rotated array by comparing with the right end."),
        ("array_patterns", "Reasoning about which element can be discarded without losing the answer."),
    ],
)

_p(
    "ways-to-split-array", "Number of Ways to Split Array", "Medium",
    topics=["Prefix Sums", "Arrays"], subtopics=["Running Prefix"], companies=["Amazon"],
    shape="arr", ret="int", todo="compute the total once; walk i from 0 to n − 2 with a running prefix and compare it with total − prefix",
    description=(
        "A split at index `i` (with `0 ≤ i < n − 1`) is **valid** when the sum of `a[0..i]` is "
        "at least the sum of `a[i+1..n−1]`. Print the number of valid splits.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of valid splits."
    ),
    constraints="2 ≤ n ≤ 10^5\n-10^5 ≤ a[i] ≤ 10^5",
    hints=[
        "Summing both sides for every split is O(n²).",
        "The right side is the total minus the left side.",
        "Keep a running prefix. Sums reach 10^10 in magnitude, so use long.",
    ],
    opt=("O(n)", "O(1)", "One pass for the total, one for the running prefix."),
    editorial=(
        "## The one thing this teaches\n**Two complementary sums need only one running value.** "
        "Left + right = total, so tracking the left side gives the right side for free. No "
        "prefix array is needed.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int x : a) total += x;\nlong left = 0;\nint valid = 0;\n"
        "for (int i = 0; i < n - 1; i++) {\n    left += a[i];\n    if (left >= total - left) valid++;\n}\n```\n\n"
        "## Why the last index is excluded\nBoth parts must be non-empty, so the split after the "
        "last element is not allowed.\n\n"
        "## Use long\n10^5 values of magnitude 10^5 reach 10^10, beyond an int."
    ),
    py='''
def solve(a):
    return sum(1 for i in range(len(a) - 1) if sum(a[:i + 1]) >= sum(a[i + 1:]))
''',
    java='''
    static int solve(int[] a) {
        long total = 0;
        for (int x : a) total += x;
        long left = 0;
        int valid = 0;
        for (int i = 0; i < a.length - 1; i++) {
            left += a[i];
            if (left >= total - left) valid++;
        }
        return valid;
    }
''',
    examples=[("Example 1", "4\n10 4 -8 7\n"), ("Example 2", "4\n2 3 1 0\n")],
    hidden=[
        ("Two equal", "2\n1 1\n"),
        ("Left smaller", "2\n-1 1\n"),
        ("All zeros", "5\n0 0 0 0 0\n"),
        ("Large values", "3\n100000 -100000 100000\n"),
    ],
    expl=[
        "Splits after 10 (10 ≥ 3) and after 4 (14 ≥ −1) are valid; after −8, 6 < 7.",
        "After 2, 2 < 4. After 3, 5 ≥ 1. After 1, 6 ≥ 0.",
    ],
    prereqs=[
        ("prefix_sum", "A running prefix compared against the total minus itself."),
        ("overflow", "Sums up to 10^10 in 64-bit integers."),
    ],
)

_p(
    "elimination-game", "Elimination Game", "Medium",
    topics=["Recursion", "Math"], subtopics=["Halving"], companies=["Apple"],
    shape="n", ret="long", todo="track head, step and remaining count; the head moves on every left pass, and on a right pass only when the count is odd",
    description=(
        "Write the numbers `1` to `n`. Remove the first number and every other number after it, "
        "left to right. Then do the same from right to left, starting with the last remaining "
        "number. Keep alternating until one number remains. Print it.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe last remaining number."
    ),
    constraints="1 ≤ n ≤ 10^9",
    hints=[
        "Simulating a list of 10^9 numbers is too slow — but each pass halves the count.",
        "The survivors always form an arithmetic sequence: a head, a step (doubling each pass) and a count.",
        "The head changes on a left-to-right pass always, and on a right-to-left pass only when the count is odd (the old head gets removed).",
    ],
    opt=("O(log n)", "O(1)", "One iteration per halving."),
    editorial=(
        "## The one thing this teaches\n**Describe what survives, not every element.** After "
        "each pass the remaining numbers are evenly spaced, so three numbers — first element, "
        "spacing, count — describe the whole list, and each pass updates them in O(1).\n\n"
        "## Approach\n```java\nlong head = 1, step = 1, count = n;\nboolean leftToRight = true;\n"
        "while (count > 1) {\n    if (leftToRight || count % 2 == 1) head += step;   // the head is removed\n"
        "    step *= 2;\n    count /= 2;\n    leftToRight = !leftToRight;\n}\nreturn head;\n```\n\n"
        "## The recursive view\nAfter the first pass, `2, 4, …, 2⌊n/2⌋` remain, and the next pass "
        "runs right to left — the mirror image of the same game on ⌊n/2⌋ numbers. That gives "
        "`f(n) = 2 · (1 + ⌊n/2⌋ − f(⌊n/2⌋))`.\n\n"
        "## Walkthrough: n = 9\n`1…9` → `2 4 6 8` (head 2) → from the right, remove 8 and 4 → "
        "`2 6` (count was even, head stays) → remove 2 → `6`."
    ),
    py='''
def solve(n):
    def last(m):
        return 1 if m == 1 else 2 * (1 + m // 2 - last(m // 2))
    return last(n)
''',
    java='''
    static long solve(long n) {
        long head = 1, step = 1, count = n;
        boolean leftToRight = true;
        while (count > 1) {
            if (leftToRight || count % 2 == 1) head += step;
            step *= 2;
            count /= 2;
            leftToRight = !leftToRight;
        }
        return head;
    }
''',
    examples=[("Example 1", "9\n"), ("Example 2", "1\n")],
    hidden=[
        ("Two", "2\n"),
        ("Ten", "10\n"),
        ("Hundred", "100\n"),
        ("Largest", "1000000000\n"),
    ],
    expl=[
        "1…9 → 2 4 6 8 → 2 6 → 6.",
        "Only 1 is written.",
    ],
    prereqs=[
        ("recursion", "The game on ⌊n/2⌋ numbers, mirrored, as a subproblem."),
        ("math_digits", "Arithmetic sequences described by head, step and count."),
    ],
)

_p(
    "bst-floor-ceil", "Floor and Ceiling in a BST", "Medium",
    topics=["Trees"], subtopics=["BST"], companies=["Amazon", "Microsoft"],
    shape="tree_k", ret="String", todo="walk from the root: a value ≤ key is a floor candidate (go right), a value ≥ key is a ceiling candidate (go left)",
    description=(
        "Given a binary search tree with distinct non-negative values and a key, print the "
        "**floor** (largest value ≤ key) and the **ceiling** (smallest value ≥ key), using `-1` "
        "for one that does not exist.\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child (empty for an empty tree).\n- Line 2: `key`.\n\n"
        "### Output\n`floor ceiling`."
    ),
    constraints="0 ≤ nodes ≤ 10^4\n0 ≤ value, key ≤ 10^9",
    hints=[
        "Collecting all values in order and binary searching works in O(n).",
        "Walking down a BST follows the same path a search for the key would.",
        "At each node: if its value ≤ key, it is the best floor so far and anything better is to the right; if ≥ key, it is the best ceiling so far and anything better is to the left.",
    ],
    opt=("O(h)", "O(1)", "One root-to-leaf walk."),
    editorial=(
        "## The one thing this teaches\n**The search path already passes the neighbours.** "
        "Searching for a missing key ends at a leaf, but on the way it turned right at every "
        "smaller value and left at every larger one. The last right turn is the floor; the last "
        "left turn is the ceiling.\n\n"
        "## Approach\n```java\nlong floor = -1, ceil = -1;\nTreeNode cur = root;\nwhile (cur != null) {\n"
        "    if (cur.val == key) { floor = ceil = key; break; }\n"
        "    if (cur.val < key) { floor = cur.val; cur = cur.right; }   // a candidate; look for larger\n"
        "    else { ceil = cur.val; cur = cur.left; }                  // a candidate; look for smaller\n}\n```\n\n"
        "## Why the last candidate is the best\nEach time the walk records a floor and goes right, "
        "every later node lies between that value and the key — so a later floor candidate is "
        "always larger. The same holds for ceilings on the left.\n\n"
        "## TreeSet in practice\nJava's `TreeSet.floor` and `ceiling` do exactly this walk on a "
        "balanced tree."
    ),
    py='''
def solve(root, k):
    vals = []
    stack, cur = [], root
    while stack or cur:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        vals.append(cur.val)
        cur = cur.right
    i = bisect_right(vals, k)
    floor = vals[i - 1] if i > 0 else -1
    j = bisect_left(vals, k)
    ceil = vals[j] if j < len(vals) else -1
    return f"{floor} {ceil}"
''',
    java='''
    static String solve(TreeNode root, int key) {
        long floor = -1, ceil = -1;
        TreeNode cur = root;
        while (cur != null) {
            if (cur.val == key) { floor = key; ceil = key; break; }
            if (cur.val < key) { floor = cur.val; cur = cur.right; }
            else { ceil = cur.val; cur = cur.left; }
        }
        return floor + " " + ceil;
    }
''',
    examples=[("Example 1", "8 4 12 2 6 10 14\n5\n"), ("Example 2", "8 4 12 2 6 10 14\n8\n")],
    hidden=[
        ("Below everything", "8 4 12\n1\n"),
        ("Above everything", "8 4 12\n20\n"),
        ("Empty tree", "\n3\n"),
        ("Between deep nodes", "20 10 30 5 15 25 35 null null 12 18\n17\n"),
        ("Key zero", "0 null 5\n0\n"),
    ],
    expl=[
        "5 lies between 4 and 6.",
        "8 is in the tree, so it is both.",
    ],
    prereqs=[
        ("bst", "The BST order that makes the search path pass a key's neighbours."),
        ("binary_search", "Floor and ceiling as the two sides of a failed search."),
    ],
)

_p(
    "time-to-buy-tickets", "Time Needed to Buy Tickets", "Easy",
    topics=["Queues", "Simulation", "Arrays"], subtopics=["Counting Instead of Simulating"], companies=["Google", "Amazon"],
    shape="arr_k", ret="long", todo="person i ≤ k buys min(t[i], t[k]) tickets before k finishes; person i > k buys min(t[i], t[k] − 1)",
    description=(
        "People stand in a queue; person `i` wants `t[i]` tickets. Each second, the person at "
        "the front buys **one** ticket; if they still need more, they go to the back of the "
        "queue, otherwise they leave. Print how many seconds pass until person `k` has all of "
        "their tickets.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of seconds."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ t[i] ≤ 10^9\n0 ≤ k < n",
    hints=[
        "Simulating with a queue takes one step per ticket — up to 10^14 steps.",
        "Each second is one ticket bought by someone. Count how many tickets each person buys before person k finishes.",
        "People at or before k get through t[k] rounds with k (or leave earlier): min(t[i], t[k]). People after k get one round fewer: min(t[i], t[k] − 1).",
    ],
    opt=("O(n)", "O(1)", "One pass of min computations."),
    editorial=(
        "## The one thing this teaches\n**Count contributions instead of simulating turns.** "
        "The queue is a round-robin: in each round everyone still waiting buys one ticket. "
        "Person k finishes in round t[k], partway through it — so everyone's contribution is a "
        "simple cap.\n\n"
        "## Approach\n```java\nlong seconds = 0;\nfor (int i = 0; i < n; i++)\n"
        "    seconds += i <= k ? Math.min(t[i], t[k]) : Math.min(t[i], t[k] - 1);\nreturn seconds;\n```\n\n"
        "## Why people behind k get one round fewer\nIn round t[k], person k buys their last "
        "ticket and the clock stops — the people behind them have not had their turn in that "
        "round yet.\n\n"
        "## Use long\n10^5 people each buying up to 10^9 tickets is 10^14 seconds."
    ),
    py='''
def solve(a, k):
    queue = deque((need, i) for i, need in enumerate(a))
    seconds = 0
    while True:
        need, i = queue.popleft()
        seconds += 1
        if need == 1:
            if i == k:
                return seconds
        else:
            queue.append((need - 1, i))
''',
    java='''
    static long solve(int[] t, long kk) {
        int k = (int) kk;
        long seconds = 0;
        for (int i = 0; i < t.length; i++)
            seconds += i <= k ? Math.min(t[i], t[k]) : Math.min(t[i], t[k] - 1);
        return seconds;
    }
''',
    examples=[("Example 1", "3 2\n2 3 2\n"), ("Example 2", "4 0\n5 1 1 1\n")],
    hidden=[
        ("Alone", "1 0\n7\n"),
        ("Last of equals", "5 4\n1 1 1 1 1\n"),
        ("Middle person", "3 1\n100 100 100\n"),
        ("Short neighbours", "5 2\n1 9 4 2 8\n"),
    ],
    expl=[
        "Rounds 1 and 2 take 3 seconds each; person 2 finishes at the end of round 2: 6.",
        "The three 1s leave after round 1 (4 seconds); person 0 then buys 4 more alone: 8.",
    ],
    prereqs=[
        ("queue", "The round-robin queue whose behaviour is being counted."),
        ("overflow", "Totals up to 10^14 seconds."),
    ],
)

_p(
    "data-stream-disjoint-intervals", "Data Stream as Disjoint Intervals", "Hard",
    topics=["Design", "Intervals", "Ordered Set"], subtopics=["Merging on Insert"], companies=["Google", "Amazon"],
    shape="ops", ret="String", todo="keep a sorted map start → end; on add, merge with the interval ending at v − 1 and the one starting at v + 1",
    description=(
        "Numbers arrive one at a time. Support:\n\n"
        "- `add v` — add the non-negative integer `v` (it may repeat);\n"
        "- `get` — print the numbers seen so far as disjoint intervals in increasing order, each "
        "as `start-end`, separated by spaces (or `EMPTY`).\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: the operations.\n\n"
        "### Output\nOne line per `get`."
    ),
    constraints="1 ≤ q ≤ 3·10^4\n0 ≤ v ≤ 10^4",
    hints=[
        "Rebuilding intervals from a sorted list of all numbers on every get costs O(n).",
        "A new number either is already covered, extends an interval by one on either side, bridges two intervals, or starts a new one.",
        "Store intervals in an ordered map from start to end. The interval that could contain or touch v from the left is floorEntry(v); the one touching from the right starts at v + 1.",
    ],
    opt=("O(log k) per add, O(k) per get", "O(k)", "k disjoint intervals in a balanced ordered map."),
    editorial=(
        "## The one thing this teaches\n**Maintain the answer's shape incrementally.** Instead of "
        "recomputing intervals from raw numbers, keep the intervals themselves and repair only "
        "the neighbourhood of each new value — at most two intervals change.\n\n"
        "## Approach\n```java\nTreeMap<Integer, Integer> iv = new TreeMap<>();    // start → end\n\n"
        "void add(int v) {\n    Map.Entry<Integer, Integer> left = iv.floorEntry(v);\n"
        "    if (left != null && left.getValue() >= v) return;          // already covered\n"
        "    int start = v, end = v;\n"
        "    if (left != null && left.getValue() == v - 1) start = left.getKey();   // extend left interval\n"
        "    Integer rightEnd = iv.remove(v + 1);                        // interval starting right after v\n"
        "    if (rightEnd != null) end = rightEnd;\n    iv.put(start, end);\n}\n```\n\n"
        "## The four cases\n| before | add | after |\n|---|---|---|\n"
        "| `1-3` | `2` | `1-3` (covered) |\n| `1-3` | `4` | `1-4` |\n| `1-3 5-7` | `4` | `1-7` |\n"
        "| `1-3` | `9` | `1-3 9-9` |\n\n"
        "## Why put(start, end) handles the left merge\nWhen extending the left interval, "
        "`start` is its existing key, so `put` overwrites its end instead of adding a new entry."
    ),
    py='''
def solve(ops):
    seen = set()
    out = []
    for op in ops:
        if op[0] == "add":
            seen.add(int(op[1]))
            continue
        parts = []
        start = prev = None
        for v in sorted(seen):
            if start is None:
                start = prev = v
            elif v == prev + 1:
                prev = v
            else:
                parts.append(f"{start}-{prev}")
                start = prev = v
        if start is not None:
            parts.append(f"{start}-{prev}")
        out.append(" ".join(parts) if parts else "EMPTY")
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        TreeMap<Integer, Integer> iv = new TreeMap<>();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("add")) {
                int v = Integer.parseInt(op[1]);
                Map.Entry<Integer, Integer> left = iv.floorEntry(v);
                if (left != null && left.getValue() >= v) continue;
                int start = v, end = v;
                if (left != null && left.getValue() == v - 1) start = left.getKey();
                Integer rightEnd = iv.remove(v + 1);
                if (rightEnd != null) end = rightEnd;
                iv.put(start, end);
            } else {
                if (sb.length() > 0) sb.append('\\n');
                if (iv.isEmpty()) { sb.append("EMPTY"); continue; }
                boolean first = true;
                for (Map.Entry<Integer, Integer> e : iv.entrySet()) {
                    if (!first) sb.append(' ');
                    sb.append(e.getKey()).append('-').append(e.getValue());
                    first = false;
                }
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "10\nadd 1\nget\nadd 3\nget\nadd 7\nget\nadd 2\nget\nadd 6\nget\n"),
    ],
    hidden=[
        ("Get before any add", "2\nget\nadd 5\n"),
        ("Repeated value", "4\nadd 4\nadd 4\nadd 4\nget\n"),
        ("Bridge two intervals", "6\nadd 1\nadd 3\nget\nadd 2\nadd 0\nget\n"),
        ("Descending adds", "6\nadd 5\nadd 4\nadd 3\nadd 10\nadd 9\nget\n"),
    ],
    expl=[
        "1-1; then 1-1 3-3; then 1-1 3-3 7-7; adding 2 bridges into 1-3; adding 6 extends 7-7 to 6-7.",
    ],
    prereqs=[
        ("intervals", "Merging an interval with its neighbours."),
        ("design_ds", "An ordered map as the maintained state of a stream."),
    ],
)

_p(
    "sum-of-prefix-scores", "Sum of Prefix Scores of Strings", "Hard",
    topics=["Tries", "Strings"], subtopics=["Counting Trie"], companies=["Google"],
    shape="words", ret="String", todo="insert every word into a trie, incrementing a counter on each node passed; a word's answer is the sum of counters along its path",
    description=(
        "The **score** of a string `p` is the number of words in the list that have `p` as a "
        "prefix. For each word, print the sum of the scores of all its non-empty prefixes.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` words.\n\n"
        "### Output\n`n` numbers separated by spaces, in input order."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ word length ≤ 1000\nLowercase English letters",
    hints=[
        "Checking every prefix against every word is O(n² · L).",
        "A prefix corresponds to a trie node. Its score is the number of words whose insertion passed through that node.",
        "Insert all words, incrementing a count on each node visited. Then walk each word's path again and add up the counts.",
    ],
    opt=("O(total length)", "O(total length)", "Two passes over all characters, each a trie step."),
    editorial=(
        "## The one thing this teaches\n**Store aggregate counts on trie nodes.** A plain trie "
        "answers \"is this a prefix\". Adding one counter per node answers \"how many words share "
        "this prefix\" — and a word's path visits every one of its prefixes in order.\n\n"
        "## Approach\n```java\nclass Node { Node[] next = new Node[26]; int pass; }\n\n"
        "for (String w : words) {                 // pass 1: count\n    Node cur = root;\n"
        "    for (char ch : w.toCharArray()) {\n        if (cur.next[ch - 'a'] == null) cur.next[ch - 'a'] = new Node();\n"
        "        cur = cur.next[ch - 'a'];\n        cur.pass++;\n    }\n}\n"
        "for (String w : words) {                 // pass 2: sum along the path\n    Node cur = root; long total = 0;\n"
        "    for (char ch : w.toCharArray()) { cur = cur.next[ch - 'a']; total += cur.pass; }\n    output(total);\n}\n```\n\n"
        "## Why the word counts itself\nEvery word is a prefix of itself, so each of its prefixes "
        "scores at least 1 — its own insertion passed through every node on its path.\n\n"
        "## Walkthrough: abc ab bc b\nFor `abc`: `a` → 2 (abc, ab), `ab` → 2, `abc` → 1. Sum 5."
    ),
    py='''
def solve(words):
    out = []
    for w in words:
        total = 0
        for length in range(1, len(w) + 1):
            prefix = w[:length]
            total += sum(1 for other in words if other.startswith(prefix))
        out.append(total)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(String[] words) {
        int total = 0;
        for (String w : words) total += w.length();
        int[][] next = new int[total + 1][26];
        int[] pass = new int[total + 1];
        int nodes = 0;
        for (String w : words) {
            int cur = 0;
            for (int i = 0; i < w.length(); i++) {
                int c = w.charAt(i) - 'a';
                if (next[cur][c] == 0) next[cur][c] = ++nodes;
                cur = next[cur][c];
                pass[cur]++;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (String w : words) {
            int cur = 0;
            long sum = 0;
            for (int i = 0; i < w.length(); i++) { cur = next[cur][w.charAt(i) - 'a']; sum += pass[cur]; }
            if (sb.length() > 0) sb.append(' ');
            sb.append(sum);
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4\nabc ab bc b\n"), ("Example 2", "1\nabcd\n")],
    hidden=[
        ("Identical words", "3\na a a\n"),
        ("Nothing shared", "2\nab cd\n"),
        ("Shared two-letter prefix", "3\nabc abd abe\n"),
        ("Mixed", "4\napple app apricot banana\n"),
    ],
    expl=[
        "abc: 2 + 2 + 1 = 5. ab: 2 + 2 = 4. bc: 2 + 1 = 3. b: 2.",
        "Each of the four prefixes belongs only to abcd.",
    ],
    prereqs=[
        ("trie", "A trie whose nodes count the words passing through them."),
        ("string_basics", "Prefixes of a word, visited in order along its trie path."),
    ],
)
