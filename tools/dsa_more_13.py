# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 13 — the last required slots: two pointers, windows, and friends.
#
#   max-k-sum-pairs                sort, then pair from both ends
#   remove-duplicates-sorted-ii    a write pointer compared two places back
#   max-points-from-cards          taking k from the ends = leaving a window of n − k
#   max-sum-distinct-window        a fixed window that also tracks duplicates
#   count-nice-subarrays           exactly k = at most k − at most (k − 1)
#   wiggle-subsequence             count direction changes, greedily
#   find-k-closest                 binary search for the left edge of a length-k window
#   zigzag-conversion              simulate the row index bouncing between 0 and numRows − 1
#   remove-k-digits                a monotonic stack that pops bigger digits while k lasts
# ===========================================================================

_p(
    "max-k-sum-pairs", "Max Number of K-Sum Pairs", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers", "Sorting"], companies=["Google", "Amazon"],
    shape="arr_k", ret="long", todo="sort; with pointers at both ends, a matching pair counts and both move inward",
    description=(
        "In one operation, remove two numbers whose sum is `k`. What is the maximum number of "
        "operations?\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` positive integers.\n\n### Output\nThe maximum number of operations."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^9\n1 ≤ k ≤ 10^9",
    hints=[
        "Each number can pair with only one value, k − x, so greedily pairing never blocks a better pairing.",
        "Sort, and put pointers at both ends: a sum below k needs a bigger left value, above k a smaller right value.",
        "A match removes both — count it and move both pointers. (A hash map of unmatched values also works in O(n).)",
    ],
    opt=("O(n log n)", "O(1)", "A sort and one converging two-pointer pass."),
    editorial=(
        "## The one thing this teaches\n**Two-sum, repeated until nothing is left.** Every number "
        "has exactly one possible partner value, so pairing greedily can never steal a partner "
        "that a better arrangement needed. That makes the count a single pass.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nint l = 0, r = n - 1;\nlong ops = 0;\nwhile (l < r) {\n"
        "    long s = (long) a[l] + a[r];\n    if (s == k) { ops++; l++; r--; }\n"
        "    else if (s < k) l++;\n    else r--;\n}\n```\n\n"
        "## The hash map version\nKeep counts of unmatched values; for each `x`, if `k − x` has a "
        "positive count, pair them and decrement, otherwise record `x`. O(n) and no sort.\n\n"
        "## The overflow\nTwo values near 10⁹ sum past `int` — compare the sum in `long`."
    ),
    py='''
def solve(a, k):
    a = sorted(a)
    l, r = 0, len(a) - 1
    ops = 0
    while l < r:
        s = a[l] + a[r]
        if s == k:
            ops += 1
            l += 1
            r -= 1
        elif s < k:
            l += 1
        else:
            r -= 1
    return ops
''',
    java='''
    static long solve(int[] a, long k) {
        Map<Long, Integer> unmatched = new HashMap<>();
        long ops = 0;
        for (int x : a) {
            long need = k - x;
            Integer c = unmatched.get(need);
            if (c != null && c > 0) { unmatched.put(need, c - 1); ops++; }
            else unmatched.merge((long) x, 1, Integer::sum);
        }
        return ops;
    }
''',
    examples=[("Example 1", "4 5\n1 2 3 4\n"), ("Example 2", "5 6\n3 1 3 4 3\n")],
    hidden=[
        ("Single number", "1 2\n1\n"),
        ("Self-pairs", "6 4\n2 2 2 2 2 2\n"),
        ("Leftover middle", "5 10\n5 5 5 1 9\n"),
        ("Large values", "2 2000000000\n1000000000 1000000000\n"),
    ],
    expl=[
        "Remove (1, 4) and (2, 3).",
        "Only one (3, 3) pair; the third 3 has no partner left.",
    ],
    prereqs=[
        ("two_pointers", "Converging pointers on a sorted array, pairing from both ends."),
        ("complement", "Each value's only possible partner is k − x."),
    ],
)

_p(
    "remove-duplicates-sorted-ii", "Remove Duplicates from Sorted Array II", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers"], companies=["Meta", "Microsoft"],
    shape="arr", ret="String", todo="write a[i] unless it equals the value two places behind the write pointer",
    description=(
        "A sorted array may contain many copies of a value. Remove extras **in place** so that each "
        "value appears **at most twice**, keeping the order, and print what remains.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` sorted integers.\n\n"
        "### Output\nThe kept values, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 3·10^4\n-10^4 ≤ a[i] ≤ 10^4, sorted",
    hints=[
        "A write pointer w marks the end of the kept prefix; a read pointer scans everything.",
        "Because the array is sorted, a third copy of a value would equal the value TWO places behind w.",
        "Keep a[i] when w < 2 or a[i] != a[w − 2]. Generalise: at most m copies compares with a[w − m].",
    ],
    opt=("O(n)", "O(1)", "One pass; the kept prefix is written over the array itself."),
    editorial=(
        "## The one thing this teaches\n**Compare with what you kept, not with what you read.** The "
        "question \"is this a third copy?\" is about the *output*: if the last two kept values are "
        "both equal to `a[i]`, it is. Since the output is sorted, checking the kept value two "
        "places back answers it.\n\n"
        "## Approach\n```java\nint w = 0;\nfor (int x : a)\n    if (w < 2 || x != a[w - 2]) a[w++] = x;\n// a[0..w) is the answer\n```\n\n"
        "## Why not compare with `a[i − 2]`\nThe read side still holds values the write side has "
        "overwritten, or has not. Comparing with `a[i − 2]` checks the *input*, and the input "
        "`1 1 1 1` has `a[3] == a[1]` — the check works by accident there and fails on "
        "`1 1 1 2 2 2`, where the kept prefix and the read positions drift apart.\n\n"
        "The same line with `2` replaced by `1` is Remove Duplicates from Sorted Array."
    ),
    py='''
def solve(a):
    w = 0
    for x in a:
        if w < 2 or x != a[w - 2]:
            a[w] = x
            w += 1
    return " ".join(map(str, a[:w]))
''',
    java='''
    static String solve(int[] a) {
        int w = 0;
        for (int i = 0; i < a.length; i++)
            if (w < 2 || a[i] != a[w - 2]) a[w++] = a[i];
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < w; i++) { if (i > 0) sb.append(' '); sb.append(a[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "6\n1 1 1 2 2 3\n"), ("Example 2", "9\n0 0 1 1 1 1 2 3 3\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All equal", "4\n2 2 2 2\n"),
        ("No duplicates", "3\n1 2 3\n"),
        ("Runs of three", "6\n1 1 1 2 2 2\n"),
    ],
    expl=[
        "The third 1 is removed.",
        "Two of the four 1s are removed.",
    ],
    prereqs=[
        ("two_pointers", "A read pointer and a write pointer over the same array."),
        ("array_patterns", "In-place compaction that compares against the kept output."),
    ],
)

_p(
    "max-points-from-cards", "Maximum Points From Cards", "Medium",
    topics=["Arrays", "Sliding Window"], subtopics=["Sliding Window", "Fixed Window"], companies=["Google", "Amazon"],
    shape="arr_k", ret="long", todo="the cards NOT taken form a window of n − k; minimise its sum",
    description=(
        "Cards lie in a row. Take exactly `k` cards, each time from the **left or right end**. "
        "Maximise the total of the cards taken.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: the `n` card values.\n\n### Output\nThe maximum total."
    ),
    constraints="1 ≤ k ≤ n ≤ 10^5\n1 ≤ value ≤ 10^4",
    hints=[
        "Whatever order you take them in, you end with some i cards from the left and k − i from the right.",
        "The cards you did NOT take are a contiguous block of length n − k in the middle.",
        "Maximising what you take is minimising that block. Slide a window of length n − k and take the smallest sum.",
    ],
    opt=("O(n)", "O(1)", "One fixed-size window pass."),
    editorial=(
        "## The one thing this teaches\n**Look at the complement.** Taking from both ends is "
        "awkward to enumerate as a choice sequence, but what is *left behind* is simple: one "
        "contiguous window of length n − k. The best take is the total minus the smallest such "
        "window.\n\n"
        "## Approach\n```java\nint w = n - k;\nlong total = 0, win = 0;\n"
        "for (int i = 0; i < n; i++) total += a[i];\nfor (int i = 0; i < w; i++) win += a[i];\n"
        "long minWin = win;\nfor (int i = w; i < n; i++) {\n    win += a[i] - a[i - w];\n"
        "    minWin = Math.min(minWin, win);\n}\nreturn total - minWin;\n```\n\n"
        "When `k == n` the window is empty, its sum 0, and the answer is the total.\n\n"
        "## The direct version\nTry every split: `i` from the left and `k − i` from the right, "
        "using prefix and suffix sums. Also O(n), and a good check on the complement argument."
    ),
    py='''
def solve(a, k):
    n = len(a)
    w = n - k
    total = sum(a)
    win = sum(a[:w])
    best = win
    for i in range(w, n):
        win += a[i] - a[i - w]
        best = min(best, win)
    return total - best
''',
    java='''
    static long solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        long[] pre = new long[n + 1];
        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
        long best = 0;
        for (int left = 0; left <= k; left++) {
            long take = pre[left] + (pre[n] - pre[n - (k - left)]);
            best = Math.max(best, take);
        }
        return best;
    }
''',
    examples=[("Example 1", "7 3\n1 2 3 4 5 6 1\n"), ("Example 2", "3 2\n2 2 2\n")],
    hidden=[
        ("Take everything", "7 7\n9 7 7 9 7 7 9\n"),
        ("Big card out of reach", "5 1\n1 1000 1 1 1\n"),
        ("Split between ends", "8 3\n1 79 80 1 1 1 200 1\n"),
    ],
    expl=[
        "Take the three cards on the right: 6 + 5 + 1 = 12.",
        "Any two cards: 4.",
    ],
    prereqs=[
        ("sliding_window", "A fixed window of the cards left behind, slid across the row."),
        ("prefix_sum", "Equivalently, prefix and suffix sums for each left/right split."),
    ],
)

_p(
    "max-sum-distinct-window", "Maximum Sum of Distinct Subarrays With Length K", "Medium",
    topics=["Arrays", "Sliding Window"], subtopics=["Sliding Window", "Hashing"], companies=["Amazon"],
    shape="arr_k", ret="long", todo="slide a window of length k with a running sum and value counts; score it only when all counts are 1",
    description=(
        "Among all subarrays of length exactly `k` whose elements are **all distinct**, find the "
        "largest sum.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe largest sum, or `0` if no such subarray exists."
    ),
    constraints="1 ≤ k ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^5",
    hints=[
        "A fixed window of length k: add the entering element, remove the leaving one.",
        "Track counts of values in the window and how many values currently occur more than once.",
        "The window qualifies exactly when that duplicate count is 0.",
    ],
    opt=("O(n)", "O(k)", "One pass; the count map holds at most k values."),
    editorial=(
        "## The one thing this teaches\n**A window can carry more than a sum.** The fixed-window "
        "template maintains one aggregate by adding and removing. Anything that supports add and "
        "remove in O(1) — here, a count per value and the number of repeated values — rides "
        "along for free.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> cnt = new HashMap<>();\nlong sum = 0, best = 0;\nint dups = 0;\n"
        "for (int i = 0; i < n; i++) {\n    sum += a[i];\n    if (cnt.merge(a[i], 1, Integer::sum) == 2) dups++;\n"
        "    if (i >= k) {\n        sum -= a[i - k];\n"
        "        if (cnt.merge(a[i - k], -1, Integer::sum) == 1) dups--;\n    }\n"
        "    if (i >= k - 1 && dups == 0) best = Math.max(best, sum);\n}\n```\n\n"
        "## Counting duplicates, not scanning for them\nChecking `cnt.size() == k` works too, if "
        "keys that drop to zero are removed. The `dups` counter changes exactly when a count "
        "crosses 1↔2, which keeps the test O(1) without deleting keys."
    ),
    py='''
def solve(a, k):
    cnt = defaultdict(int)
    total = best = 0
    for i, x in enumerate(a):
        total += x
        cnt[x] += 1
        if i >= k:
            y = a[i - k]
            total -= y
            cnt[y] -= 1
            if cnt[y] == 0:
                del cnt[y]
        if i >= k - 1 and len(cnt) == k:
            best = max(best, total)
    return best
''',
    java='''
    static long solve(int[] a, long kk) {
        int k = (int) kk;
        Map<Integer, Integer> cnt = new HashMap<>();
        long sum = 0, best = 0;
        int dups = 0;
        for (int i = 0; i < a.length; i++) {
            sum += a[i];
            if (cnt.merge(a[i], 1, Integer::sum) == 2) dups++;
            if (i >= k) {
                sum -= a[i - k];
                if (cnt.merge(a[i - k], -1, Integer::sum) == 1) dups--;
            }
            if (i >= k - 1 && dups == 0) best = Math.max(best, sum);
        }
        return best;
    }
''',
    examples=[("Example 1", "7 3\n1 5 4 2 9 9 9\n"), ("Example 2", "3 3\n4 4 4\n")],
    hidden=[
        ("Single element", "1 1\n7\n"),
        ("Distinct only at the end", "5 2\n1 1 1 1 2\n"),
        ("No qualifying window", "6 3\n5 3 3 1 1 5\n"),
        ("Triple copy leaves slowly", "6 2\n4 4 4 1 2 3\n"),
    ],
    expl=[
        "`[4, 2, 9]` sums to 15; the windows with two 9s do not count.",
        "Every window repeats a value.",
    ],
    prereqs=[
        ("sliding_window", "A fixed window updated by one entering and one leaving element."),
        ("hashing", "Value counts inside the window, with a counter of repeated values."),
    ],
)

_p(
    "count-nice-subarrays", "Count Subarrays With Exactly K Odd Numbers", "Medium",
    topics=["Arrays", "Sliding Window"], subtopics=["Sliding Window", "Counting"], companies=["Amazon", "Roblox"],
    shape="arr_k", ret="long", todo="count windows with at most k odds, minus those with at most k − 1",
    description=(
        "Count the contiguous subarrays that contain **exactly** `k` odd numbers.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` positive integers.\n\n### Output\nThe number of subarrays."
    ),
    constraints="1 ≤ n ≤ 5·10^4\n1 ≤ a[i] ≤ 10^5\n1 ≤ k ≤ n",
    hints=[
        "\"At most k odds\" is a window you can slide: shrink while there are more than k.",
        "\"Exactly k\" is not monotone in the same way — but exactly(k) = atMost(k) − atMost(k − 1).",
        "atMost(m) counts, for each right end, r − left + 1 windows. Alternatively: prefix counts of odd numbers and a frequency table.",
    ],
    opt=("O(n)", "O(1)", "Two passes of the count-all-windows template."),
    editorial=(
        "## The one thing this teaches\n**Exactly = at most − at most one less.** Windows with "
        "\"at most k\" of something shrink and grow monotonically, so the count-all-windows "
        "template applies. \"Exactly k\" does not, but it is the difference of two quantities that "
        "do.\n\n"
        "## Approach\n```java\nlong atMost(int[] a, int m) {\n    if (m < 0) return 0;\n"
        "    long count = 0;\n    int left = 0, odds = 0;\n    for (int r = 0; r < a.length; r++) {\n"
        "        odds += a[r] & 1;\n        while (odds > m) odds -= a[left++] & 1;\n"
        "        count += r - left + 1;\n    }\n    return count;\n}\nanswer = atMost(a, k) - atMost(a, k - 1);\n```\n\n"
        "## The prefix-count view\nReplace each number by 1 if odd and 0 if even, and it is "
        "Subarray Sum Equals K on a 0/1 array: count earlier prefixes equal to `run − k`. Same "
        "answer, and it generalises to arrays with negatives, where the window version does not."
    ),
    py='''
def solve(a, k):
    seen = defaultdict(int)
    seen[0] = 1
    run = 0
    count = 0
    for x in a:
        run += x & 1
        count += seen[run - k]
        seen[run] += 1
    return count
''',
    java='''
    static long atMost(int[] a, long m) {
        if (m < 0) return 0;
        long count = 0;
        int left = 0, odds = 0;
        for (int r = 0; r < a.length; r++) {
            odds += a[r] & 1;
            while (odds > m) odds -= a[left++] & 1;
            count += r - left + 1;
        }
        return count;
    }

    static long solve(int[] a, long k) {
        return atMost(a, k) - atMost(a, k - 1);
    }
''',
    examples=[("Example 1", "5 3\n1 1 2 1 1\n"), ("Example 2", "3 1\n2 4 6\n")],
    hidden=[
        ("Evens widen the count", "10 2\n2 2 2 1 2 2 1 2 2 2\n"),
        ("Single odd", "1 1\n1\n"),
        ("All odd", "5 2\n1 1 1 1 1\n"),
    ],
    expl=[
        "`[1,1,2,1]` and `[1,2,1,1]`.",
        "There are no odd numbers.",
    ],
    prereqs=[
        ("sliding_window", "The count-all-windows template for 'at most m odd numbers'."),
        ("prefix_sum", "Equivalently, prefix counts of odd numbers with a frequency table."),
    ],
)

_p(
    "wiggle-subsequence", "Wiggle Subsequence", "Medium",
    topics=["Greedy", "Arrays"], subtopics=["Greedy"], companies=["Microsoft", "Amazon"],
    shape="arr", ret="int", todo="track the best wiggle length ending on an up step and on a down step",
    description=(
        "A **wiggle sequence** has differences between consecutive elements that strictly "
        "alternate between positive and negative (a single element, or two different elements, "
        "also count). Find the length of the longest wiggle **subsequence**.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe maximum length."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ a[i] ≤ 1000",
    hints=[
        "Keep two numbers: the longest wiggle ending with an up step, and with a down step.",
        "If a[i] > a[i − 1], an up step extends the best down-ending sequence: up = down + 1. Symmetrically for down.",
        "Equal neighbours change nothing. Greedily, the answer is 1 + the number of direction changes in the non-flat differences.",
    ],
    opt=("O(n)", "O(1)", "Two counters updated per element."),
    editorial=(
        "## The one thing this teaches\n**A DP that collapses to two numbers — and then to a "
        "greedy.** The O(n²) DP asks, for each i, the longest wiggle ending at i going up or down. "
        "But the best up-ending length never decreases along the array, so two running values "
        "suffice.\n\n"
        "## Approach\n```java\nint up = 1, down = 1;\nfor (int i = 1; i < n; i++) {\n"
        "    if (a[i] > a[i - 1]) up = down + 1;\n    else if (a[i] < a[i - 1]) down = up + 1;\n}\n"
        "return Math.max(up, down);\n```\n\n"
        "## The greedy reading\nIn a run of rising values, only the peak matters: it is the best "
        "place to turn around. So the answer counts the turning points — every change of "
        "direction in the differences, ignoring zeros — plus one."
    ),
    py='''
def solve(a):
    if len(a) < 2:
        return len(a)
    count = 1
    prev = 0
    for i in range(1, len(a)):
        d = a[i] - a[i - 1]
        if (d > 0 and prev <= 0) or (d < 0 and prev >= 0):
            count += 1
            prev = d
    return count
''',
    java='''
    static int solve(int[] a) {
        int up = 1, down = 1;
        for (int i = 1; i < a.length; i++) {
            if (a[i] > a[i - 1]) up = down + 1;
            else if (a[i] < a[i - 1]) down = up + 1;
        }
        return Math.max(up, down);
    }
''',
    examples=[("Example 1", "6\n1 7 4 9 2 5\n"), ("Example 2", "10\n1 17 5 10 13 15 10 5 16 8\n")],
    hidden=[
        ("Monotone", "9\n1 2 3 4 5 6 7 8 9\n"),
        ("Single element", "1\n0\n"),
        ("All equal", "4\n3 3 3 3\n"),
        ("Two different", "2\n1 2\n"),
        ("Flat stretches", "7\n1 1 5 5 2 2 8\n"),
    ],
    expl=[
        "The whole array already wiggles.",
        "For example `1 17 10 13 10 16 8`.",
    ],
    prereqs=[
        ("greedy", "Counting direction changes, since the peak of a run is always the best turning point."),
        ("dp", "The two-state DP (ending up, ending down) that the greedy simplifies."),
    ],
)

_p(
    "find-k-closest", "Find K Closest Elements", "Medium",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search", "Two Pointers"], companies=["Meta", "Amazon", "Uber"],
    shape="arr_xy", ret="String", todo="binary search the left edge i of the answer window in [0, n − k]",
    description=(
        "From a sorted array, choose the `k` elements closest to `x`, and print them in ascending "
        "order. When two elements are equally close, the **smaller** one is closer.\n\n"
        "### Input\n- Line 1: `n k x`.\n- Line 2: the `n` sorted integers.\n\n"
        "### Output\nThe `k` chosen elements in ascending order."
    ),
    constraints="1 ≤ k ≤ n ≤ 10^4\n-10^4 ≤ a[i], x ≤ 10^4, a sorted",
    hints=[
        "The answer is always a contiguous window of length k.",
        "Binary search its left edge i in [0, n − k]: compare x − a[mid] with a[mid + k] − x.",
        "If x − a[mid] > a[mid + k] − x, the window should move right (lo = mid + 1); otherwise hi = mid.",
    ],
    opt=("O(log(n − k) + k)", "O(1)", "A binary search over window starts, then copying k elements."),
    editorial=(
        "## The one thing this teaches\n**Binary search over windows.** The k closest elements are "
        "contiguous in a sorted array, so the question becomes \"where does the window start?\" — "
        "and comparing the two elements that a shift would swap (`a[mid]` leaving, `a[mid + k]` "
        "entering) tells you which way to move.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n - k;\nwhile (lo < hi) {\n    int mid = (lo + hi) >>> 1;\n"
        "    if (x - a[mid] > a[mid + k] - x) lo = mid + 1;   // a[mid+k] is strictly closer\n"
        "    else hi = mid;\n}\n// answer: a[lo .. lo + k)\n```\n\n"
        "## Why no `Math.abs`\nUsing `|x − a[mid]| > |a[mid + k] − x|` fails when duplicates make "
        "the two compared elements equal: with `a = [1, 1, 2, 2, 2, 2, 2, 3, 3]`, k = 3, x = 3 it "
        "returns `[2, 2, 2]` instead of `[2, 3, 3]`. The signed comparison says exactly whether "
        "shifting right improves the window, including the tie rule.\n\n"
        "## The simple alternative\nTwo pointers at the ends, dropping the farther end until k "
        "remain: O(n − k), no subtle comparisons."
    ),
    py='''
def solve(a, x, y):
    k, target = x, y
    chosen = sorted(a, key=lambda v: (abs(v - target), v))[:k]
    return " ".join(map(str, sorted(chosen)))
''',
    java='''
    static String solve(int[] a, long kk, long x) {
        int k = (int) kk, lo = 0, hi = a.length - k;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (x - a[mid] > a[mid + k] - x) lo = mid + 1;
            else hi = mid;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = lo; i < lo + k; i++) { if (i > lo) sb.append(' '); sb.append(a[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "5 4 3\n1 2 3 4 5\n"), ("Example 2", "5 4 -1\n1 2 3 4 5\n")],
    hidden=[
        ("Single element", "1 1 100\n5\n"),
        ("Tie goes to the smaller", "5 2 3\n1 2 4 5 6\n"),
        ("Duplicates defeat an abs comparison", "9 3 3\n1 1 2 2 2 2 2 3 3\n"),
        ("Target past the end", "6 3 20\n1 1 2 3 4 7\n"),
    ],
    expl=[
        "Distances 2 1 0 1 2: the 5 loses its tie with the 1.",
        "x is left of everything, so the four smallest.",
    ],
    prereqs=[
        ("binary_search", "Searching for the start of a length-k window with a signed comparison."),
        ("two_pointers", "The alternative: shrink from whichever end is farther."),
    ],
)

_p(
    "zigzag-conversion", "Zigzag Conversion", "Medium",
    topics=["Strings", "Simulation"], subtopics=["Simulation"], companies=["Amazon", "Adobe"],
    shape="str_k", ret="String", todo="append each character to its row while the row index bounces between 0 and rows − 1",
    description=(
        "Write a string in a zigzag over `numRows` rows — down the first column, diagonally up to "
        "the top, down again — and read it row by row.\n\n"
        "`PAYPALISHIRING` over 3 rows:\n\n```\nP   A   H   N\nA P L S I I G\nY   I   R\n```\n"
        "reads `PAHNAPLSIIGYIR`.\n\n"
        "### Input\n- Line 1: `s` (no spaces).\n- Line 2: `numRows`.\n\n### Output\nThe row-by-row reading."
    ),
    constraints="1 ≤ |s| ≤ 1000\n1 ≤ numRows ≤ 1000\ns contains letters, ',' and '.'.",
    hints=[
        "You never need the grid — only which row each character lands in.",
        "Walk the string with a row index that moves down by 1 and flips direction at the top and bottom rows.",
        "Append each character to a StringBuilder for its row, then join the rows. One row is a special case: no bouncing.",
    ],
    opt=("O(n)", "O(n)", "Each character is appended to one of the row builders."),
    editorial=(
        "## The one thing this teaches\n**Simulate only what the output needs.** The picture has "
        "columns and spaces, but reading row by row discards them. What survives is the order of "
        "characters within each row — and that is just \"which row did this character land in\".\n\n"
        "## Approach\n```java\nif (rows == 1) return s;\nStringBuilder[] row = new StringBuilder[rows];   // each initialised\n"
        "int r = 0, step = 1;\nfor (char c : s.toCharArray()) {\n    row[r].append(c);\n"
        "    if (r == 0) step = 1;\n    else if (r == rows - 1) step = -1;\n    r += step;\n}\n"
        "return String.join(\"\", row);\n```\n\n"
        "## The closed form\nThe pattern repeats every `2·rows − 2` characters. Row 0 takes indices "
        "`0, cycle, 2·cycle…`; a middle row `i` takes `j·cycle ± i`. It is faster in theory and "
        "slower to get right.\n\n"
        "## The one-row case\nWith one row, `r == 0` and `r == rows − 1` are both true and the step "
        "flips every character, sending `r` out of range. Return `s` first."
    ),
    py='''
def solve(s, k):
    rows = k
    if rows == 1 or rows >= len(s):
        return s
    cycle = 2 * rows - 2
    out = []
    for r in range(rows):
        for j in range(0, len(s), cycle):
            if j + r < len(s):
                out.append(s[j + r])
            if 0 < r < rows - 1 and j + cycle - r < len(s):
                out.append(s[j + cycle - r])
    return "".join(out)
''',
    java='''
    static String solve(String s, int rows) {
        if (rows == 1) return s;
        StringBuilder[] row = new StringBuilder[Math.min(rows, s.length())];
        for (int i = 0; i < row.length; i++) row[i] = new StringBuilder();
        int r = 0, step = 1;
        for (int i = 0; i < s.length(); i++) {
            row[r].append(s.charAt(i));
            if (r == 0) step = 1;
            else if (r == row.length - 1) step = -1;
            r += step;
        }
        StringBuilder out = new StringBuilder();
        for (StringBuilder b : row) out.append(b);
        return out.toString();
    }
''',
    examples=[("Example 1", "PAYPALISHIRING\n3\n"), ("Example 2", "PAYPALISHIRING\n4\n")],
    hidden=[
        ("One row", "AB\n1\n"),
        ("Two rows", "ABCD\n2\n"),
        ("More rows than letters", "ABC\n5\n"),
        ("Punctuation", "a.b,c.d\n3\n"),
    ],
    expl=[
        "Rows `PAHN`, `APLSIIG`, `YIR`.",
        "Rows `PIN`, `ALSIG`, `YAHR`, `PI`.",
    ],
    prereqs=[
        ("simulation", "Tracking only the row index as it bounces between the top and bottom rows."),
        ("string_basics", "One StringBuilder per row, concatenated at the end."),
    ],
)

_p(
    "remove-k-digits", "Remove K Digits", "Medium",
    topics=["Stack", "Greedy"], subtopics=["Monotonic Stack", "Greedy"], companies=["Google", "Amazon"],
    shape="str_k", ret="String", todo="keep digits on a stack; pop a larger top while removals remain; trim zeros",
    description=(
        "Remove exactly `k` digits from the number `num` so that the remaining number is as "
        "**small** as possible. Print it without leading zeros (`0` if nothing remains).\n\n"
        "### Input\n- Line 1: `num`.\n- Line 2: `k`.\n\n### Output\nThe smallest possible number."
    ),
    constraints="1 ≤ k ≤ |num| ≤ 10^5\nnum has no leading zeros (unless it is 0).",
    hints=[
        "Earlier digits matter most. If a digit is larger than the one after it, removing it makes the number smaller.",
        "Scan left to right with a stack: while removals remain and the top is larger than the current digit, pop.",
        "If removals remain at the end, drop them from the end (the stack is non-decreasing). Then strip leading zeros.",
    ],
    opt=("O(n)", "O(n)", "Each digit is pushed once and popped at most once."),
    editorial=(
        "## The one thing this teaches\n**A monotonic stack is a greedy that can take things "
        "back.** The most significant position should hold the smallest digit you can afford. Each "
        "new digit asks: is the digit before me bigger, and can I still remove one? If so, "
        "removing it improves every number that follows.\n\n"
        "## Approach\n```java\nStringBuilder st = new StringBuilder();\nfor (char c : num.toCharArray()) {\n"
        "    while (k > 0 && st.length() > 0 && st.charAt(st.length() - 1) > c) {\n"
        "        st.setLength(st.length() - 1);\n        k--;\n    }\n    st.append(c);\n}\n"
        "st.setLength(st.length() - k);                  // remaining removals come off the end\n"
        "int i = 0;\nwhile (i < st.length() - 1 && st.charAt(i) == '0') i++;   // leading zeros\n"
        "return st.substring(i);\n```\n\n"
        "## Why the end\nAfter the scan the stack never decreases. Removing any digit of a "
        "non-decreasing number is best done at the end, where it costs the least.\n\n"
        "## The zeros\n`10200` with k = 1 removes the 1 and leaves `0200`, which is `200`. Removing "
        "everything leaves nothing, which is `0`."
    ),
    py='''
def solve(s, k):
    st = []
    for ch in s:
        while k > 0 and st and st[-1] > ch:
            st.pop()
            k -= 1
        st.append(ch)
    if k:
        st = st[:-k]
    res = "".join(st).lstrip("0")
    return res if res else "0"
''',
    java='''
    static String solve(String num, int k) {
        StringBuilder st = new StringBuilder();
        for (int i = 0; i < num.length(); i++) {
            char c = num.charAt(i);
            while (k > 0 && st.length() > 0 && st.charAt(st.length() - 1) > c) { st.setLength(st.length() - 1); k--; }
            st.append(c);
        }
        st.setLength(Math.max(0, st.length() - k));
        int i = 0;
        while (i < st.length() - 1 && st.charAt(i) == '0') i++;
        String res = st.substring(i);
        return res.isEmpty() ? "0" : res;
    }
''',
    examples=[("Example 1", "1432219\n3\n"), ("Example 2", "10200\n1\n")],
    hidden=[
        ("Remove everything", "10\n2\n"),
        ("Single digit", "9\n1\n"),
        ("Non-decreasing input", "112\n1\n"),
        ("Zeros after removal", "1234567890\n9\n"),
        ("Equal digits are not popped", "5337\n2\n"),
    ],
    expl=[
        "Remove 4, 3 and 2 to get 1219.",
        "Remove the 1; the leading zero goes: 200.",
    ],
    prereqs=[
        ("stack", "A stack of kept digits that pops larger digits while removals remain."),
        ("greedy", "Making the most significant digits as small as possible first."),
    ],
)
