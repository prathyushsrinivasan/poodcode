# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 21 — a spread across the middle stages.
#
#   max-sum-circular-subarray     the wrapped answer is the total minus the minimum subarray
#   longest-common-substring      dp[i][j] = a common run ending at both positions
#   next-permutation              the longest non-increasing suffix is already at its maximum
#   majority-element-ii           at most two values can exceed n/3: Boyer–Moore with two slots
#   car-fleet                     sort by position; arrival times from the front decide the fleets
#   count-inversions              merge sort counts every cross pair while it merges
#   hand-of-straights             the smallest remaining card must start a group
#   all-nodes-distance-k          parent pointers turn the tree into an undirected graph
#   sliding-window-median         two ordered halves, rebalanced after each add and remove
#   constrained-subsequence-sum   DP whose window maximum lives in a monotonic deque
#   days-without-meetings         sort, merge, and subtract the covered days
# ===========================================================================

_p(
    "max-sum-circular-subarray", "Maximum Sum Circular Subarray", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["Kadane's Algorithm"], companies=["Amazon", "Meta"],
    shape="arr", ret="long", todo="run Kadane for the maximum and for the minimum; the wrapped best is total − minimum (unless every value is negative)",
    description=(
        "The array is **circular**: the element after the last is the first. Print the largest sum "
        "of a non-empty subarray, where a subarray may wrap around the end — but may use each "
        "element at most once.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe maximum subarray sum."
    ),
    constraints="1 ≤ n ≤ 3·10^4\n-3·10^4 ≤ a[i] ≤ 3·10^4",
    hints=[
        "A subarray that does not wrap is ordinary Kadane.",
        "A subarray that wraps leaves out a contiguous middle part. Its sum is total − (the part left out).",
        "So the best wrapping subarray is total − (minimum subarray sum). Take the larger of the two answers — unless all values are negative, where the \"wrap\" would be empty.",
    ],
    opt=("O(n)", "O(1)", "Two Kadane passes run together, plus the total."),
    editorial=(
        "## The one thing this teaches\n**Solve the complement.** A wrapping subarray is awkward "
        "to enumerate, but what it leaves out is an ordinary contiguous subarray. Maximising what "
        "you keep is minimising what you drop.\n\n"
        "## Approach\n```java\nlong total = 0, curMax = 0, bestMax = Long.MIN_VALUE, curMin = 0, bestMin = Long.MAX_VALUE;\n"
        "for (int x : a) {\n    total += x;\n"
        "    curMax = Math.max(curMax + x, x);  bestMax = Math.max(bestMax, curMax);\n"
        "    curMin = Math.min(curMin + x, x);  bestMin = Math.min(bestMin, curMin);\n}\n"
        "return bestMax < 0 ? bestMax : Math.max(bestMax, total - bestMin);\n```\n\n"
        "## The all-negative trap\nWith `-3 -2 -3`, the minimum subarray is the whole array, so "
        "`total − bestMin = 0` — the sum of an *empty* subarray, which is not allowed. When "
        "`bestMax < 0`, every value is negative and the answer is simply the largest element.\n\n"
        "## Walkthrough: 5 −3 5\nKadane (no wrap): 7. Total 7, minimum subarray −3, so the wrap "
        "gives 10: `5` at the end followed by `5` at the start."
    ),
    py='''
def solve(a):
    n = len(a)
    best = None
    for i in range(n):
        s = 0
        for length in range(1, n + 1):
            s += a[(i + length - 1) % n]
            if best is None or s > best:
                best = s
    return best
''',
    java='''
    static long solve(int[] a) {
        long total = 0, curMax = 0, bestMax = Long.MIN_VALUE, curMin = 0, bestMin = Long.MAX_VALUE;
        for (int x : a) {
            total += x;
            curMax = Math.max(curMax + x, x);
            bestMax = Math.max(bestMax, curMax);
            curMin = Math.min(curMin + x, x);
            bestMin = Math.min(bestMin, curMin);
        }
        return bestMax < 0 ? bestMax : Math.max(bestMax, total - bestMin);
    }
''',
    examples=[("Example 1", "4\n1 -2 3 -2\n"), ("Example 2", "3\n5 -3 5\n")],
    hidden=[
        ("All negative", "3\n-3 -2 -3\n"),
        ("Single element", "1\n7\n"),
        ("Wrap skips two small dips", "5\n3 -1 2 -1 4\n"),
        ("Wrap joins the ends", "4\n-2 4 -5 4\n"),
        ("Deep valleys", "5\n2 -10 3 -10 4\n"),
    ],
    expl=[
        "The best is the single 3; wrapping cannot avoid a −2.",
        "Wrapping: the last 5 and then the first 5, skipping −3.",
    ],
    prereqs=[
        ("dp", "Kadane's algorithm, run once for the maximum and once for the minimum."),
        ("complement", "The wrapped subarray is the whole array minus a contiguous middle."),
    ],
)

_p(
    "longest-common-substring", "Longest Common Substring", "Medium",
    topics=["Dynamic Programming", "Strings"], subtopics=["2D DP"], companies=["Amazon", "Microsoft"],
    shape="str2", ret="int", todo="dp[i][j] = length of the common run ending at s[i−1] and t[j−1]: dp[i−1][j−1] + 1 on a match, else 0",
    description=(
        "Print the length of the longest string that is a **substring** (contiguous) of both `s` "
        "and `t`.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `t`.\n\n"
        "### Output\nThe length, or 0 if they share no character."
    ),
    constraints="1 ≤ |s|, |t| ≤ 1000\nLowercase English letters",
    hints=[
        "Unlike a subsequence, a substring cannot skip characters — a mismatch ends the run.",
        "Define dp[i][j] as the length of the longest common substring that ENDS at s[i−1] and at t[j−1].",
        "On a match, dp[i][j] = dp[i−1][j−1] + 1; otherwise 0. The answer is the maximum entry, not the corner.",
    ],
    opt=("O(|s| · |t|)", "O(|t|)", "Each row depends only on the previous row's diagonal."),
    editorial=(
        "## The one thing this teaches\n**\"Ending here\" states reset; \"best so far\" states "
        "don't.** The longest common *subsequence* carries its best forward across mismatches. A "
        "*substring* must be contiguous, so its state is \"the run ending exactly here\" — which "
        "drops to 0 on a mismatch — and the answer is the best of all of them.\n\n"
        "## Approach\n```java\nint[] prev = new int[m + 1];\nint best = 0;\n"
        "for (int i = 1; i <= n; i++) {\n    int[] cur = new int[m + 1];\n"
        "    for (int j = 1; j <= m; j++)\n"
        "        if (s.charAt(i - 1) == t.charAt(j - 1)) { cur[j] = prev[j - 1] + 1; best = Math.max(best, cur[j]); }\n"
        "    prev = cur;\n}\nreturn best;\n```\n\n"
        "## Compared with LCS\n| | match | mismatch | answer |\n|---|---|---|---|\n"
        "| subsequence | `dp[i−1][j−1] + 1` | `max(dp[i−1][j], dp[i][j−1])` | `dp[n][m]` |\n"
        "| substring | `dp[i−1][j−1] + 1` | `0` | max over all cells |\n\n"
        "## Faster, for the curious\nA suffix automaton or binary search with rolling hashes "
        "reaches roughly O((n + m) log) — well beyond what interviews ask."
    ),
    py='''
def solve(s, t):
    for length in range(min(len(s), len(t)), 0, -1):
        pieces = {s[i:i + length] for i in range(len(s) - length + 1)}
        if any(t[j:j + length] in pieces for j in range(len(t) - length + 1)):
            return length
    return 0
''',
    java='''
    static int solve(String s, String t) {
        int n = s.length(), m = t.length(), best = 0;
        int[] prev = new int[m + 1];
        for (int i = 1; i <= n; i++) {
            int[] cur = new int[m + 1];
            for (int j = 1; j <= m; j++)
                if (s.charAt(i - 1) == t.charAt(j - 1)) { cur[j] = prev[j - 1] + 1; best = Math.max(best, cur[j]); }
            prev = cur;
        }
        return best;
    }
''',
    examples=[("Example 1", "abcdxyz\nxyzabcd\n"), ("Example 2", "zxabcdezy\nyzabcdezx\n")],
    hidden=[
        ("Nothing shared", "a\nb\n"),
        ("One inside the other", "aaaa\naa\n"),
        ("Identical", "abc\nabc\n"),
        ("Offset by one", "abab\nbaba\n"),
        ("Subsequence is longer", "axbxcx\nabc\n"),
    ],
    expl=[
        "\"abcd\" appears in both; \"xyz\" is shorter.",
        "\"abcdez\" appears in both.",
    ],
    prereqs=[
        ("dp2d", "A table over prefix lengths of both strings, with a rolling row."),
        ("string_basics", "The difference between a substring and a subsequence."),
    ],
)

_p(
    "next-permutation", "Next Permutation", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Permutations"], companies=["Google", "Meta", "Microsoft"],
    shape="arr", ret="String", todo="find the rightmost i with a[i] < a[i+1]; swap a[i] with the rightmost larger value; reverse the suffix",
    description=(
        "Rearrange the numbers into the **next** lexicographically greater permutation. If the "
        "array is already the largest arrangement, wrap around to the smallest (sorted "
        "ascending). Values may repeat.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe next permutation, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "A suffix that is non-increasing is already as large as it can be — no rearrangement of it alone helps.",
        "So find the rightmost i with a[i] < a[i+1]. Position i must grow, by as little as possible.",
        "Swap a[i] with the rightmost value in the suffix that is larger than it, then reverse the suffix to make it as small as possible.",
    ],
    opt=("O(n)", "O(1)", "Two scans from the right and one reversal, all in place."),
    editorial=(
        "## The one thing this teaches\n**Change the rightmost position that can change, by the "
        "least amount.** Lexicographic order is decided by the first difference, so the next "
        "permutation keeps the longest possible prefix and makes the smallest possible increase "
        "right after it.\n\n"
        "## Approach\n```java\nint i = n - 2;\nwhile (i >= 0 && a[i] >= a[i + 1]) i--;      // suffix a[i+1..] is non-increasing\n"
        "if (i >= 0) {\n    int j = n - 1;\n    while (a[j] <= a[i]) j--;                  // rightmost value larger than a[i]\n"
        "    swap(a, i, j);\n}\nreverse(a, i + 1, n - 1);                    // smallest arrangement of the suffix\n```\n\n"
        "## Why reverse instead of sort\nAfter the swap the suffix is still non-increasing — "
        "`a[j]` was the rightmost value above `a[i]`, so `a[i]` fits in its place without breaking "
        "the order. Reversing a non-increasing run sorts it in O(n).\n\n"
        "## The wrap\nIf no `i` exists, the whole array is non-increasing — the last permutation. "
        "Reversing all of it (with `i = −1`) gives the first."
    ),
    py='''
def solve(a):
    from itertools import permutations
    perms = sorted(set(permutations(a)))
    nxt = perms[(perms.index(tuple(a)) + 1) % len(perms)]
    return " ".join(map(str, nxt))
''',
    java='''
    static String solve(int[] a) {
        int n = a.length, i = n - 2;
        while (i >= 0 && a[i] >= a[i + 1]) i--;
        if (i >= 0) {
            int j = n - 1;
            while (a[j] <= a[i]) j--;
            int t = a[i]; a[i] = a[j]; a[j] = t;
        }
        for (int l = i + 1, r = n - 1; l < r; l++, r--) { int t = a[l]; a[l] = a[r]; a[r] = t; }
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < n; k++) { if (k > 0) sb.append(' '); sb.append(a[k]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "3\n3 2 1\n")],
    hidden=[
        ("Duplicates", "3\n1 1 5\n"),
        ("Single element", "1\n4\n"),
        ("Long suffix", "6\n1 3 5 4 2 0\n"),
        ("Last arrangement with duplicates", "4\n2 2 1 1\n"),
        ("Swap near the end", "5\n1 5 8 4 7\n"),
        ("Duplicate of the swap value", "5\n1 2 3 3 2\n"),
    ],
    expl=[
        "1 2 3 → 1 3 2: only the last two change.",
        "3 2 1 is the largest arrangement, so it wraps to 1 2 3.",
    ],
    prereqs=[
        ("two_pointers", "Scanning from the right, then reversing a suffix with two pointers."),
        ("array_patterns", "In-place swaps and reversals."),
    ],
)

_p(
    "majority-element-ii", "Majority Element II", "Medium",
    topics=["Arrays", "Hashing"], subtopics=["Boyer–Moore Voting"], companies=["Google", "Amazon"],
    shape="arr", ret="String", todo="two candidates with counters (Boyer–Moore), then a second pass to confirm each count exceeds n / 3",
    description=(
        "Print every value that appears **more than ⌊n / 3⌋ times**, in increasing order, or "
        "`NONE` if there is none.\n\n"
        "Aim for O(n) time and O(1) extra space.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe values separated by spaces, or `NONE`."
    ),
    constraints="1 ≤ n ≤ 5·10^4\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "A hash map of counts works in O(n) space.",
        "At most two values can each take more than a third of the array.",
        "Keep two candidates with counters. A new value that matches neither decrements both — cancelling one of each of three distinct values. Survivors are only candidates: count them again.",
    ],
    opt=("O(n)", "O(1)", "One voting pass and one counting pass."),
    editorial=(
        "## The one thing this teaches\n**Cancelling in groups preserves the heavy hitters.** "
        "Boyer–Moore for a majority cancels pairs of different values. For \"more than n/3\", "
        "cancel *triples* of distinct values: each cancellation removes three elements but at "
        "most one copy of any heavy value, so a value with more than n/3 copies cannot be wiped out.\n\n"
        "## Approach\n```java\nint c1 = 0, c2 = 0; long v1 = 0, v2 = 1;       // distinct placeholders\n"
        "for (int x : a) {\n    if (x == v1) c1++;\n    else if (x == v2) c2++;\n"
        "    else if (c1 == 0) { v1 = x; c1 = 1; }\n    else if (c2 == 0) { v2 = x; c2 = 1; }\n"
        "    else { c1--; c2--; }                        // cancel a triple\n}\n"
        "// second pass: count v1 and v2, keep those above n / 3\n```\n\n"
        "## Why the second pass is required\nThe vote guarantees that a heavy value survives, "
        "not that a survivor is heavy. In `1 2 3`, the vote ends with candidates that each "
        "appear once — not more than ⌊3/3⌋ = 1.\n\n"
        "## Order of the checks\nMatching a candidate must come before claiming an empty slot; "
        "otherwise a value already held in slot 1 could also be placed in slot 2 while "
        "`c2 == 0`, and both slots would hold the same value."
    ),
    py='''
def solve(a):
    from collections import Counter
    heavy = sorted(v for v, c in Counter(a).items() if c > len(a) // 3)
    return " ".join(map(str, heavy)) if heavy else "NONE"
''',
    java='''
    static String solve(int[] a) {
        int n = a.length, c1 = 0, c2 = 0;
        long v1 = Long.MIN_VALUE, v2 = Long.MAX_VALUE;
        for (int x : a) {
            if (x == v1) c1++;
            else if (x == v2) c2++;
            else if (c1 == 0) { v1 = x; c1 = 1; }
            else if (c2 == 0) { v2 = x; c2 = 1; }
            else { c1--; c2--; }
        }
        int n1 = 0, n2 = 0;
        for (int x : a) { if (x == v1) n1++; else if (x == v2) n2++; }
        List<Long> out = new ArrayList<>();
        if (n1 > n / 3) out.add(v1);
        if (n2 > n / 3) out.add(v2);
        if (out.isEmpty()) return "NONE";
        Collections.sort(out);
        StringBuilder sb = new StringBuilder();
        for (long v : out) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n3 2 3\n"), ("Example 2", "2\n1 2\n")],
    hidden=[
        ("Single element", "1\n1\n"),
        ("Exactly a third each", "6\n1 2 3 1 2 3\n"),
        ("Two heavy values", "8\n2 2 1 1 1 2 2 3\n"),
        ("Negative values", "7\n-1 -1 -1 5 5 5 0\n"),
        ("All distinct", "3\n1 2 3\n"),
    ],
    expl=[
        "⌊3/3⌋ = 1, and 3 appears twice.",
        "⌊2/3⌋ = 0, so both values, each appearing once, qualify.",
    ],
    prereqs=[
        ("hashing", "The counting baseline, and the second counting pass that confirms candidates."),
        ("array_patterns", "A voting scan that cancels groups of distinct values."),
    ],
)

_p(
    "car-fleet", "Car Fleet", "Medium",
    topics=["Stacks", "Sorting"], subtopics=["Monotonic Stack"], companies=["Google", "Amazon"],
    shape="pairs_k", ret="int", todo="sort cars by position descending; a car arriving strictly later than the fleet ahead starts a new fleet",
    description=(
        "Cars drive toward `target` on a one-lane road. Each has a starting position and a speed. "
        "A car can never pass another: when it catches up, it slows to match and the two drive on "
        "as one **fleet**. A car that catches up exactly at `target` still joins that fleet.\n\n"
        "Print the number of fleets that arrive.\n\n"
        "### Input\n- Line 1: `n target`.\n- Next `n` lines: `position speed`.\n\n"
        "### Output\nThe number of fleets."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ target ≤ 10^6\n0 ≤ position < target, positions distinct\n1 ≤ speed ≤ 10^6",
    hints=[
        "Only the car directly ahead can block a car. Process cars from the one nearest the target.",
        "Compute each car's arrival time alone: (target − position) / speed. A car that would arrive no later than the fleet ahead of it catches that fleet.",
        "Walk from the front, tracking the slowest arrival time so far. A strictly later time starts a new fleet. Compare the fractions by cross-multiplying, so equal times are exactly equal.",
    ],
    opt=("O(n log n)", "O(n)", "Sorting by position dominates; the scan is linear."),
    editorial=(
        "## The one thing this teaches\n**Sort into the order where influence flows one way.** "
        "A car is affected only by cars ahead of it. Sorted from the front, each car's fate "
        "depends on something already decided: the arrival time of the fleet just ahead.\n\n"
        "## Approach\n```java\nsort cars by position, descending;\nint fleets = 0;\n"
        "long leadDist = 0, leadSpeed = 1;          // the time of the fleet ahead, as a fraction\n"
        "for (car : cars) {\n    long dist = target - car.position;\n"
        "    // dist / speed > leadDist / leadSpeed  ⇔  dist * leadSpeed > leadDist * speed\n"
        "    if (fleets == 0 || dist * leadSpeed > leadDist * car.speed) {\n"
        "        fleets++; leadDist = dist; leadSpeed = car.speed;\n    }\n}\n```\n\n"
        "## Why the slowest time is enough\nA car that would arrive earlier than the fleet ahead "
        "catches it and then arrives *with* it — so the fleet's time does not change. Only a "
        "strictly later car becomes a new fleet, and its time becomes the one to beat. The times "
        "that matter form an increasing sequence: the monotonic stack, reduced to its top.\n\n"
        "## Exact comparison\n`999999 / 999999` and `1000000 / 1000000` are the same time, and "
        "the car must join the fleet. Cross-multiplying in 64-bit integers (products at most "
        "10^12) keeps every comparison exact. Doubles happen to be precise enough at these limits, "
        "but proving that takes longer than avoiding the question."
    ),
    py='''
def solve(p, k):
    from fractions import Fraction
    fleets = 0
    slowest = None
    for pos, speed in sorted(p, reverse=True):
        t = Fraction(k - pos, speed)
        if slowest is None or t > slowest:
            fleets += 1
            slowest = t
    return fleets
''',
    java='''
    static int solve(int[][] p, int target) {
        Arrays.sort(p, (x, y) -> Integer.compare(y[0], x[0]));
        int fleets = 0;
        long leadDist = 0, leadSpeed = 1;
        for (int[] car : p) {
            long dist = target - car[0];
            if (fleets == 0 || dist * leadSpeed > leadDist * car[1]) {
                fleets++;
                leadDist = dist;
                leadSpeed = car[1];
            }
        }
        return fleets;
    }
''',
    examples=[
        ("Example 1", "5 12\n10 2\n8 4\n0 1\n5 1\n3 3\n"),
        ("Example 2", "3 100\n0 4\n2 2\n4 1\n"),
    ],
    hidden=[
        ("Same speed never meet", "3 10\n0 1\n5 1\n8 1\n"),
        ("Meet exactly at the target", "2 10\n0 2\n5 1\n"),
        ("One car", "1 10\n3 3\n"),
        ("Chain of catches", "4 20\n0 5\n10 1\n15 5\n19 1\n"),
        ("Equal times, large numbers", "2 1000000\n0 1000000\n1 999999\n"),
    ],
    expl=[
        "10 (time 1) and 8 (time 1) meet at 12; 5 (time 7) and 3 (time 3) meet; 0 (time 12) is alone.",
        "From the front the times are 96, 49 and 25: both cars behind would arrive sooner, so they catch the car at 4.",
    ],
    prereqs=[
        ("sorting", "Ordering cars from nearest to farthest from the target."),
        ("stack", "A monotonic sequence of fleet arrival times, of which only the top is ever compared."),
    ],
)

_p(
    "count-inversions", "Count Inversions", "Hard",
    topics=["Sorting", "Divide and Conquer"], subtopics=["Merge Sort"], companies=["Amazon", "Microsoft"],
    shape="arr", ret="long", todo="merge sort; when an element of the right half is placed, every remaining left element forms an inversion with it",
    description=(
        "An **inversion** is a pair of indices `i < j` with `a[i] > a[j]`. Print the number of "
        "inversions.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of inversions."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Checking every pair is O(n²) — 5·10^9 pairs at n = 10^5.",
        "Split the array in half. Inversions are inside the left half, inside the right half, or across the halves.",
        "If both halves are sorted, merging them counts the cross pairs: when a right-half element is taken before the left half is exhausted, it is smaller than every left element still waiting.",
    ],
    opt=("O(n log n)", "O(n)", "Merge sort, with a counter added to the merge step."),
    editorial=(
        "## The one thing this teaches\n**Sorting can measure how unsorted something is.** Merge "
        "sort already compares elements across the two halves; counting at that moment tallies "
        "all cross-half inversions in linear time per level.\n\n"
        "## Approach\n```java\nlong sortCount(int[] a, int[] buf, int lo, int hi) {   // [lo, hi)\n"
        "    if (hi - lo < 2) return 0;\n    int mid = (lo + hi) >>> 1;\n"
        "    long count = sortCount(a, buf, lo, mid) + sortCount(a, buf, mid, hi);\n"
        "    int i = lo, j = mid, k = lo;\n    while (i < mid || j < hi) {\n"
        "        if (j == hi || (i < mid && a[i] <= a[j])) buf[k++] = a[i++];\n"
        "        else { count += mid - i; buf[k++] = a[j++]; }   // a[j] is below a[i..mid)\n    }\n"
        "    System.arraycopy(buf, lo, a, lo, hi - lo);\n    return count;\n}\n```\n\n"
        "## Equal values\nThe `<=` takes the left element first on a tie, so equal values are "
        "never counted — they are not inversions.\n\n"
        "## Use long\nA reversed array of 10^5 elements has n(n − 1)/2 ≈ 5·10^9 inversions, more "
        "than an int can hold."
    ),
    py='''
def solve(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])
''',
    java='''
    static long sortCount(int[] a, int[] buf, int lo, int hi) {
        if (hi - lo < 2) return 0;
        int mid = (lo + hi) >>> 1;
        long count = sortCount(a, buf, lo, mid) + sortCount(a, buf, mid, hi);
        int i = lo, j = mid, k = lo;
        while (i < mid || j < hi) {
            if (j == hi || (i < mid && a[i] <= a[j])) buf[k++] = a[i++];
            else { count += mid - i; buf[k++] = a[j++]; }
        }
        System.arraycopy(buf, lo, a, lo, hi - lo);
        return count;
    }

    static long solve(int[] a) {
        return sortCount(a, new int[a.length], 0, a.length);
    }
''',
    examples=[("Example 1", "5\n2 4 1 3 5\n"), ("Example 2", "5\n5 4 3 2 1\n")],
    hidden=[
        ("Single element", "1\n1\n"),
        ("Equal values are not inversions", "4\n1 1 1 1\n"),
        ("Repeated pattern", "6\n3 1 2 3 1 2\n"),
        ("Negative values", "4\n-1 -5 0 -5\n"),
        ("Already sorted", "5\n-3 0 2 2 9\n"),
    ],
    expl=[
        "(2, 1), (4, 1) and (4, 3).",
        "Every one of the 10 pairs is out of order.",
    ],
    prereqs=[
        ("sorting", "Merge sort, and the moment in the merge where cross-half order is compared."),
        ("recursion", "Divide and conquer: halves counted recursively, cross pairs counted while merging."),
    ],
)

_p(
    "hand-of-straights", "Hand of Straights", "Medium",
    topics=["Greedy", "Hashing", "Sorting"], subtopics=["Ordered Map"], companies=["Google", "Amazon"],
    shape="arr_k", ret="String", todo="count cards in an ordered map; the smallest remaining card must start a run of k consecutive values",
    description=(
        "Can the cards be split into groups of exactly `k` cards, each group being `k` "
        "**consecutive** values?\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` card values.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 10^4\n1 ≤ k ≤ n\n0 ≤ value ≤ 10^9",
    hints=[
        "If n is not a multiple of k, the answer is NO.",
        "Look at the smallest card. Nothing smaller exists to precede it, so it must be the first card of some group.",
        "Count the cards. Repeatedly take the smallest value with a positive count c and remove c copies of each of the next k values; if any has fewer than c copies, answer NO.",
    ],
    opt=("O(n log n)", "O(n)", "Sorting the distinct values dominates; each is visited once as a group start."),
    editorial=(
        "## The one thing this teaches\n**Find the choice that is forced.** Greedy is safe when "
        "there is no choice at all. The smallest card cannot be the second card of any group, so "
        "a group must start there — and then every card in that group is forced too.\n\n"
        "## Approach\n```java\nTreeMap<Integer, Integer> count = new TreeMap<>();\n"
        "for (int x : cards) count.merge(x, 1, Integer::sum);\n"
        "for (int start : count.keySet()) {\n    int c = count.get(start);\n    if (c == 0) continue;\n"
        "    for (int v = start; v < start + k; v++) {            // c groups start here at once\n"
        "        int have = count.getOrDefault(v, 0);\n        if (have < c) return false;\n"
        "        count.put(v, have - c);\n    }\n}\nreturn true;\n```\n\n"
        "## Starting c groups at once\nIf the smallest value has `c` copies, each copy starts its "
        "own group, so all `c` groups can be removed together — a factor of `c` fewer steps than "
        "removing groups one by one.\n\n"
        "## Why iterating keys in order is safe while updating values\nOnly the counts change, "
        "never the set of keys, so the TreeMap's key iteration is unaffected."
    ),
    py='''
def solve(a, k):
    from collections import Counter
    if len(a) % k:
        return "NO"
    left = Counter(a)
    while left:
        low = min(left)
        for v in range(low, low + k):
            if left[v] == 0:
                return "NO"
            left[v] -= 1
            if left[v] == 0:
                del left[v]
    return "YES"
''',
    java='''
    static String solve(int[] cards, long kk) {
        int k = (int) kk;
        if (cards.length % k != 0) return "NO";
        TreeMap<Integer, Integer> count = new TreeMap<>();
        for (int x : cards) count.merge(x, 1, Integer::sum);
        for (int start : count.keySet()) {
            int c = count.get(start);
            if (c == 0) continue;
            for (long v = start; v < (long) start + k; v++) {
                if (v > Integer.MAX_VALUE) return "NO";
                int have = count.getOrDefault((int) v, 0);
                if (have < c) return "NO";
                count.put((int) v, have - c);
            }
        }
        return "YES";
    }
''',
    examples=[("Example 1", "9 3\n1 2 3 6 2 3 4 7 8\n"), ("Example 2", "5 4\n1 2 3 4 5\n")],
    hidden=[
        ("Groups of one", "1 1\n5\n"),
        ("Pairs that cannot chain", "6 2\n1 1 2 2 3 3\n"),
        ("Two identical runs", "6 3\n1 1 2 2 3 3\n"),
        ("Shuffled pairs", "4 2\n1 3 2 4\n"),
        ("A gap", "3 3\n1 2 4\n"),
    ],
    expl=[
        "[1, 2, 3], [2, 3, 4], [6, 7, 8].",
        "5 cards cannot be split into groups of 4.",
    ],
    prereqs=[
        ("greedy", "The smallest remaining card is forced to start a group."),
        ("hashing", "Counting copies of each card value."),
    ],
)

_p(
    "all-nodes-distance-k", "All Nodes Distance K in a Binary Tree", "Medium",
    topics=["Trees", "BFS", "Graphs"], subtopics=["Tree to Graph"], companies=["Amazon", "Meta", "Google"],
    shape="tree_xy", ret="String", todo="record each node's parent, then BFS from the target through left, right and parent for k steps",
    description=(
        "Given a binary tree with distinct values, a `target` value in the tree and a distance "
        "`k`, print the values of all nodes exactly `k` edges from the target, in increasing "
        "order — or `NONE` if there are none.\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child.\n- Line 2: `target k`.\n\n"
        "### Output\nThe values separated by spaces, or `NONE`."
    ),
    constraints="1 ≤ nodes ≤ 500\n0 ≤ value ≤ 500, values distinct\ntarget is in the tree\n0 ≤ k ≤ 1000",
    hints=[
        "Nodes below the target are easy to reach. The hard ones are above it, or in a sibling subtree.",
        "Edges go both ways in terms of distance. A tree node only knows its children — give it its parent too.",
        "Build a parent map with one traversal, then BFS from the target to depth k, stepping to left, right and parent, never revisiting.",
    ],
    opt=("O(n)", "O(n)", "One traversal for parents, one BFS; both touch each node once."),
    editorial=(
        "## The one thing this teaches\n**A rooted tree is an undirected graph with the back "
        "edges hidden.** Distance ignores direction, so recover the missing edges — parent "
        "pointers — and the problem becomes a plain BFS.\n\n"
        "## Approach\n```java\nMap<TreeNode, TreeNode> parent = new HashMap<>();\n// DFS from root: parent.put(child, node); also find the node holding target\n"
        "Deque<TreeNode> q = new ArrayDeque<>(List.of(start));\nSet<TreeNode> seen = new HashSet<>(List.of(start));\n"
        "for (int d = 0; d < k && !q.isEmpty(); d++)\n    for (int size = q.size(); size > 0; size--) {\n"
        "        TreeNode u = q.poll();\n        for (TreeNode v : new TreeNode[]{u.left, u.right, parent.get(u)})\n"
        "            if (v != null && seen.add(v)) q.add(v);\n    }\n// q now holds exactly the nodes at distance k\n```\n\n"
        "## Why `seen` is needed\nWithout it, a node would step to its parent and straight back "
        "down, reporting nodes at the wrong distance.\n\n"
        "## Another route\nDistance between two tree nodes is `depth(u) + depth(v) − 2·depth(lca)`. "
        "Computing it for every node against the target is O(n · h) — simpler to argue, slower "
        "on deep trees."
    ),
    py='''
def solve(root, x, y):
    path_to = {}

    def walk(node, path):
        if node is None:
            return
        path = path + [node.val]
        path_to[node.val] = path
        walk(node.left, path)
        walk(node.right, path)

    walk(root, [])
    target = path_to[x]
    out = []
    for v, path in path_to.items():
        common = 0
        while common < min(len(path), len(target)) and path[common] == target[common]:
            common += 1
        if (len(path) - common) + (len(target) - common) == y:
            out.append(v)
    return " ".join(map(str, sorted(out))) if out else "NONE"
''',
    java='''
    static String solve(TreeNode root, int target, int k) {
        Map<TreeNode, TreeNode> parent = new HashMap<>();
        TreeNode start = null;
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        st.push(root);
        while (!st.isEmpty()) {
            TreeNode u = st.pop();
            if (u.val == target) start = u;
            if (u.left != null) { parent.put(u.left, u); st.push(u.left); }
            if (u.right != null) { parent.put(u.right, u); st.push(u.right); }
        }
        ArrayDeque<TreeNode> q = new ArrayDeque<>();
        Set<TreeNode> seen = new HashSet<>();
        q.add(start);
        seen.add(start);
        for (int d = 0; d < k && !q.isEmpty(); d++)
            for (int size = q.size(); size > 0; size--) {
                TreeNode u = q.poll();
                for (TreeNode v : new TreeNode[]{u.left, u.right, parent.get(u)})
                    if (v != null && seen.add(v)) q.add(v);
            }
        if (q.isEmpty()) return "NONE";
        List<Integer> vals = new ArrayList<>();
        for (TreeNode t : q) vals.add(t.val);
        Collections.sort(vals);
        StringBuilder sb = new StringBuilder();
        for (int v : vals) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3 5 1 6 2 0 8 null null 7 4\n5 2\n"),
        ("Example 2", "1\n1 3\n"),
    ],
    hidden=[
        ("Distance zero", "3 5 1 6 2 0 8 null null 7 4\n2 0\n"),
        ("Up and back down", "3 5 1 6 2 0 8 null null 7 4\n7 3\n"),
        ("Only upward", "0 1 null 3 2\n2 1\n"),
        ("Beyond the tree", "3 5 1\n5 5\n"),
        ("Leaf to leaf", "1 2 3 4 5 6 7\n4 4\n"),
    ],
    expl=[
        "Two steps down from 5: 7 and 4. Up to 3, then down: 1.",
        "The tree has one node, so nothing is 3 edges away.",
    ],
    prereqs=[
        ("bfs", "Level-by-level search that stops after k levels."),
        ("tree_traversal", "A traversal that records each node's parent."),
    ],
)

_p(
    "sliding-window-median", "Sliding Window Median", "Hard",
    topics=["Heaps", "Sliding Window"], subtopics=["Two Heaps", "Ordered Set"], companies=["Google", "Amazon"],
    shape="arr_k", ret="String", todo="keep the window split into a lower and an upper ordered half; the lower half's maximum is the median",
    description=(
        "For every window of `k` consecutive elements, print its **median**. For even `k`, print "
        "the **lower** of the two middle values — the element at index `(k − 1) / 2` of the "
        "sorted window.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe `n − k + 1` medians, separated by spaces."
    ),
    constraints="1 ≤ k ≤ n ≤ 10^5\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "Sorting every window is O(n · k log k).",
        "Split the window into a lower half and an upper half, with the lower half holding (k + 1) / 2 elements. The median is the largest element of the lower half.",
        "Each step adds one element and removes one. Heaps cannot remove arbitrary elements quickly; ordered sets of (value, index) can.",
    ],
    opt=("O(n log k)", "O(k)", "One insert, one delete and a constant number of moves per step, each O(log k)."),
    editorial=(
        "## The one thing this teaches\n**A median is the boundary between two halves.** Keep "
        "the halves balanced and the median is always at the top of the lower half — the same "
        "idea as the running median, plus deletion as elements leave the window.\n\n"
        "## Approach\n```java\n// ordered by value, then index, so equal values are distinct entries\n"
        "TreeSet<Integer> lo = new TreeSet<>(cmp), hi = new TreeSet<>(cmp);\n"
        "for (int i = 0; i < n; i++) {\n    lo.add(i); hi.add(lo.pollLast());             // insert via lo so order holds\n"
        "    if (hi.size() > lo.size()) lo.add(hi.pollFirst());\n"
        "    if (i >= k) {\n        if (!lo.remove(i - k)) hi.remove(i - k);\n"
        "        if (lo.size() < hi.size()) lo.add(hi.pollFirst());\n"
        "        if (lo.size() > hi.size() + 1) hi.add(lo.pollLast());\n    }\n"
        "    if (i >= k - 1) output a[lo.last()];\n}\n```\n\n"
        "## Why store indices\nTwo copies of the same value must be separate entries, or removing "
        "one would remove both. Ordering by `(value, index)` makes every entry unique.\n\n"
        "## With heaps instead\nTwo heaps with *lazy deletion* — mark leaving elements and pop "
        "them only when they reach a top — give the same bound, with more bookkeeping around the "
        "size counts."
    ),
    py='''
def solve(a, k):
    out = []
    for i in range(len(a) - k + 1):
        out.append(sorted(a[i:i + k])[(k - 1) // 2])
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        Comparator<Integer> cmp = (i, j) -> a[i] != a[j] ? Integer.compare(a[i], a[j]) : Integer.compare(i, j);
        TreeSet<Integer> lo = new TreeSet<>(cmp), hi = new TreeSet<>(cmp);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            lo.add(i);
            hi.add(lo.pollLast());
            if (hi.size() > lo.size()) lo.add(hi.pollFirst());
            if (i >= k) {
                if (!lo.remove(i - k)) hi.remove(i - k);
                if (lo.size() < hi.size()) lo.add(hi.pollFirst());
                if (lo.size() > hi.size() + 1) hi.add(lo.pollLast());
            }
            if (i >= k - 1) {
                if (sb.length() > 0) sb.append(' ');
                sb.append(a[lo.last()]);
            }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "8 3\n1 3 -1 -3 5 3 6 7\n"), ("Example 2", "6 2\n1 4 2 3 5 5\n")],
    hidden=[
        ("Window of one", "4 1\n5 -2 7 0\n"),
        ("Window is the whole array", "5 5\n9 1 8 2 7\n"),
        ("Duplicates leaving the window", "7 3\n2 2 2 1 1 3 3\n"),
        ("Extremes", "4 2\n2147483647 -2147483648 2147483647 -2147483648\n"),
        ("Even window, descending", "6 4\n6 5 4 3 2 1\n"),
    ],
    expl=[
        "Windows [1 3 −1], [3 −1 −3], [−1 −3 5], [−3 5 3], [5 3 6], [3 6 7] have medians 1, −1, −1, 3, 5, 6.",
        "Each window has two values; the lower one is printed: 1, 2, 2, 3, 5.",
    ],
    prereqs=[
        ("heap", "The two-halves median structure from the running median."),
        ("sliding_window", "Adding the entering element and removing the leaving one at each step."),
    ],
)

_p(
    "constrained-subsequence-sum", "Constrained Subsequence Sum", "Hard",
    topics=["Queues", "Dynamic Programming", "Sliding Window"], subtopics=["Monotonic Deque"], companies=["Google", "Amazon"],
    shape="arr_k", ret="long", todo="best[i] = a[i] + max(0, max of best over the last k indices); keep that window maximum in a decreasing deque",
    description=(
        "Choose a **non-empty** subsequence so that any two consecutive chosen indices are at most "
        "`k` apart. Print the largest possible sum.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe maximum sum."
    ),
    constraints="1 ≤ k ≤ n ≤ 10^5\n-10^4 ≤ a[i] ≤ 10^4",
    hints=[
        "Let best[i] be the largest sum of a valid subsequence ending at i. It extends the best of the previous k, or starts fresh.",
        "best[i] = a[i] + max(0, best[i−k..i−1]). Computing that maximum by scanning is O(n · k).",
        "The maximum of a sliding window is a monotonic deque: indices with decreasing best values, dropping those that fall out of range.",
    ],
    opt=("O(n)", "O(k)", "Each index enters and leaves the deque once."),
    editorial=(
        "## The one thing this teaches\n**When a DP transition is a window maximum, use the "
        "sliding-window-maximum deque.** The recurrence is simple; only the `max` over the last "
        "k values is slow, and that exact query has an amortised O(1) structure.\n\n"
        "## Approach\n```java\nlong[] best = new long[n];\nDeque<Integer> dq = new ArrayDeque<>();   // indices, best[] decreasing\n"
        "long answer = Long.MIN_VALUE;\nfor (int i = 0; i < n; i++) {\n"
        "    if (!dq.isEmpty() && dq.peekFirst() < i - k) dq.pollFirst();   // out of reach\n"
        "    best[i] = a[i] + (dq.isEmpty() ? 0 : Math.max(0, best[dq.peekFirst()]));\n"
        "    while (!dq.isEmpty() && best[dq.peekLast()] <= best[i]) dq.pollLast();\n"
        "    dq.addLast(i);\n    answer = Math.max(answer, best[i]);\n}\n```\n\n"
        "## Why max(0, …)\nA negative best-so-far should not be extended — starting fresh at `i` is "
        "better. But the subsequence must be non-empty, so an all-negative array still returns "
        "its largest element.\n\n"
        "## Walkthrough: 10 2 −10 5 20, k = 2\nbest = 10, 12, 2, 17, 37: the −10 at index 2 is "
        "skipped because index 3 is within reach of index 1. The answer is 10 + 2 + 5 + 20 = 37."
    ),
    py='''
def solve(a, k):
    best = []
    for i, x in enumerate(a):
        best.append(x + max([0] + best[max(0, i - k):i]))
    return max(best)
''',
    java='''
    static long solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        long[] best = new long[n];
        ArrayDeque<Integer> dq = new ArrayDeque<>();
        long answer = Long.MIN_VALUE;
        for (int i = 0; i < n; i++) {
            if (!dq.isEmpty() && dq.peekFirst() < i - k) dq.pollFirst();
            best[i] = a[i] + (dq.isEmpty() ? 0 : Math.max(0, best[dq.peekFirst()]));
            while (!dq.isEmpty() && best[dq.peekLast()] <= best[i]) dq.pollLast();
            dq.addLast(i);
            answer = Math.max(answer, best[i]);
        }
        return answer;
    }
''',
    examples=[
        ("Example 1", "5 2\n10 2 -10 5 20\n"),
        ("Example 2", "3 1\n-1 -2 -3\n"),
        ("Example 3", "5 2\n10 -2 -10 -5 20\n"),
    ],
    hidden=[
        ("Single negative", "1 1\n-5\n"),
        ("k = 1 means contiguous", "6 1\n1 -1 1 -1 1 -1\n"),
        ("Start late", "6 3\n-1 -1 -1 -1 -1 5\n"),
        ("Hop over dips", "7 2\n5 -1 -1 -1 5 -1 5\n"),
    ],
    expl=[
        "10 + 2 + 5 + 20: the gap from index 1 to index 3 is 2.",
        "Every value is negative; the best non-empty choice is −1 alone.",
        "Getting from 10 to 20 needs stepping stones at most 2 apart; −2 and −5 cost less than −10 alone: 10 − 2 − 5 + 20 = 23.",
    ],
    prereqs=[
        ("queue", "A monotonic deque that answers sliding-window maximum queries."),
        ("dp", "best[i] built from the best of the previous k positions."),
    ],
)

_p(
    "days-without-meetings", "Days Without Meetings", "Medium",
    topics=["Intervals", "Sorting"], subtopics=["Merge Intervals"], companies=["Amazon"],
    shape="pairs_k", ret="long", todo="sort meetings by start, merge overlaps, and subtract the covered days from the total",
    description=(
        "An employee is available on days `1` to `days`. Each meeting occupies the days from "
        "`start` to `end` inclusive; meetings may overlap. Print the number of days with **no** "
        "meeting.\n\n"
        "### Input\n- Line 1: `n days`.\n- Next `n` lines: `start end`.\n\n"
        "### Output\nThe number of free days."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ days ≤ 10^9\n1 ≤ start ≤ end ≤ days",
    hints=[
        "days can be 10^9, so marking each day is out.",
        "Overlapping meetings must not be counted twice. Sort by start and merge.",
        "While scanning sorted meetings, track the furthest covered day. A meeting starting after it opens a gap of free days.",
    ],
    opt=("O(n log n)", "O(1)", "Sorting dominates; the scan keeps one number (sorting in place)."),
    editorial=(
        "## The one thing this teaches\n**Count the gaps, not the days.** Merging intervals turns "
        "any overlapping mess into disjoint blocks; the free days are the spaces between blocks, "
        "computed in O(1) each regardless of how long they are.\n\n"
        "## Approach\n```java\nArrays.sort(m, (x, y) -> Integer.compare(x[0], y[0]));\n"
        "long free = 0;\nlong coveredUpTo = 0;                     // last day covered so far\n"
        "for (int[] meeting : m) {\n"
        "    if (meeting[0] > coveredUpTo + 1) free += meeting[0] - coveredUpTo - 1;   // a gap\n"
        "    coveredUpTo = Math.max(coveredUpTo, meeting[1]);\n}\n"
        "free += days - coveredUpTo;                  // after the last meeting\n```\n\n"
        "## The inclusive boundary\n`[1, 3]` and `[4, 6]` touch but do not overlap, and there is "
        "no free day between them: the gap test is `start > coveredUpTo + 1`, not "
        "`start > coveredUpTo`.\n\n"
        "## Why max\nA short meeting inside a long one must not pull `coveredUpTo` backwards."
    ),
    py='''
def solve(p, k):
    events = {}
    for s, e in p:
        events[s] = events.get(s, 0) + 1
        events[e + 1] = events.get(e + 1, 0) - 1
    free = 0
    active = 0
    day = 1
    for point in sorted(events):
        if active == 0:
            free += min(point, k + 1) - day
        active += events[point]
        day = point
    if active == 0 and day <= k:
        free += k + 1 - day
    return free
''',
    java='''
    static long solve(int[][] m, int days) {
        Arrays.sort(m, (x, y) -> Integer.compare(x[0], y[0]));
        long free = 0, coveredUpTo = 0;
        for (int[] meeting : m) {
            if (meeting[0] > coveredUpTo + 1) free += meeting[0] - coveredUpTo - 1;
            coveredUpTo = Math.max(coveredUpTo, meeting[1]);
        }
        return free + (days - coveredUpTo);
    }
''',
    examples=[
        ("Example 1", "3 10\n5 7\n1 3\n9 10\n"),
        ("Example 2", "2 5\n2 4\n1 3\n"),
    ],
    hidden=[
        ("Fully booked", "1 6\n1 6\n"),
        ("Huge calendar", "2 1000000000\n1 1\n1000000000 1000000000\n"),
        ("Nested and chained", "3 10\n2 3\n3 8\n4 5\n"),
        ("Touching meetings", "2 6\n1 3\n4 6\n"),
        ("Short meeting inside a long one", "3 20\n1 15\n2 3\n17 18\n"),
    ],
    expl=[
        "Days 4 and 8 are free.",
        "The meetings cover days 1–4; only day 5 is free.",
    ],
    prereqs=[
        ("intervals", "Sorting by start and merging overlapping or nested intervals."),
        ("sorting", "A comparator on the start day."),
    ],
)
