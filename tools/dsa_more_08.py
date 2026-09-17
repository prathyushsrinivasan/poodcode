# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 8 — binary search and greedy.
#
#   peak-of-mountain              binary search on a slope, not on a value
#   search-rotated-array          one half is always sorted — decide which, then check it
#   koko-eating-bananas           binary search on the answer with a ceiling-division check
#   min-days-for-bouquets         binary search on time; the check is a greedy scan
#   split-array-largest-sum       binary search on the answer, greedy feasibility, Hard
#   lemonade-change               greedy with a choice: give the $10 before two $5s
#   partition-labels              extend each part to the last occurrence of what it contains
#   two-city-scheduling           sort by the cost of choosing one side over the other
#   valid-parenthesis-star        track a RANGE of possible open counts
#   candy                         two passes, each enforcing one side of the rule
# ===========================================================================

_p(
    "peak-of-mountain", "Peak Index in a Mountain Array", "Easy",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search"], companies=["Google", "Amazon"],
    shape="arr", ret="int", todo="binary search: if a[mid] < a[mid+1] the peak is to the right, else at mid or left",
    description=(
        "A **mountain array** strictly increases to a single peak and then strictly decreases. "
        "Find the index of the peak in O(log n).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the mountain array.\n\n### Output\nThe peak's index."
    ),
    constraints="3 ≤ n ≤ 10^5\nThe array is a valid mountain: the peak is neither the first nor the last element.",
    hints=[
        "There is no target value to search for — but there is a direction.",
        "Compare a[mid] with a[mid + 1]: if it is rising, the peak is strictly to the right.",
        "Otherwise the peak is at mid or to its left. Shrink [lo, hi] until lo == hi.",
    ],
    opt=("O(log n)", "O(1)", "The predicate 'a[i] < a[i+1]' is true then false, so binary search finds where it flips."),
    editorial=(
        "## The one thing this teaches\n**Binary search needs a monotone predicate, not a sorted "
        "array.** The mountain is not sorted, but `a[i] < a[i + 1]` reads `true true … true false "
        "… false` along it, and the peak is the first `false`. That is First True in a Monotone "
        "Predicate, again.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n - 1;\nwhile (lo < hi) {\n"
        "    int mid = (lo + hi) >>> 1;\n"
        "    if (a[mid] < a[mid + 1]) lo = mid + 1;     // still climbing\n"
        "    else hi = mid;                             // at or past the peak\n}\nreturn lo;\n```\n\n"
        "`mid + 1` is always in range because `mid < hi` inside the loop.\n\n"
        "## Where it goes next\nFind Peak Element drops the \"single peak\" guarantee and still "
        "works — any local peak is found — and searching a bitonic array for a target is two "
        "binary searches on either side of this one."
    ),
    py='''
def solve(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    java='''
    static int solve(int[] a) {
        int lo = 0, hi = a.length - 1;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] < a[mid + 1]) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }
''',
    examples=[("Example 1", "3\n0 1 0\n"), ("Example 2", "4\n0 10 5 2\n")],
    hidden=[
        ("Peak near the end", "6\n1 2 3 4 5 1\n"),
        ("Peak near the start", "6\n1 9 8 7 6 5\n"),
        ("Long climb", "7\n3 5 7 9 11 10 2\n"),
    ],
    expl=[
        "The middle element is the peak.",
        "10 at index 1.",
    ],
    prereqs=[
        ("binary_search", "Searching for where a monotone predicate — 'still rising' — turns false."),
        ("array_patterns", "Comparing an element with its neighbour to decide which side the peak is on."),
    ],
)

_p(
    "search-rotated-array", "Search in a Rotated Sorted Array", "Medium",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search"], companies=["Meta", "Microsoft", "Amazon"],
    shape="arr_k", ret="int", todo="at each mid, one half is sorted; check whether the target lies in that half",
    description=(
        "A sorted array of **distinct** integers was rotated at an unknown pivot "
        "(`[0,1,2,4,5,6,7]` might become `[4,5,6,7,0,1,2]`). Find the index of `target` in "
        "O(log n).\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: the rotated array.\n\n"
        "### Output\nThe index of `target`, or `-1`."
    ),
    constraints="1 ≤ n ≤ 5000\n-10^4 ≤ a[i], target ≤ 10^4\nValues are distinct.",
    hints=[
        "Finding the rotation point first and then binary-searching one side works — in two searches.",
        "In one search: split at mid. At least one of [lo, mid] and [mid, hi] is sorted — compare a[lo] with a[mid] to know which.",
        "If the target lies within the sorted half's range, search there; otherwise search the other half.",
    ],
    opt=("O(log n)", "O(1)", "One binary search; each step discards half."),
    editorial=(
        "## The one thing this teaches\n**When the whole is not sorted, find the part that is.** "
        "A rotation breaks order in exactly one place, so any split leaves at least one side "
        "untouched by the break. On that side a range check is reliable; on the other it is not "
        "— so ask the question only where it can be answered.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n - 1;\nwhile (lo <= hi) {\n    int mid = (lo + hi) >>> 1;\n"
        "    if (a[mid] == target) return mid;\n"
        "    if (a[lo] <= a[mid]) {                                   // left half sorted\n"
        "        if (a[lo] <= target && target < a[mid]) hi = mid - 1;\n        else lo = mid + 1;\n"
        "    } else {                                                 // right half sorted\n"
        "        if (a[mid] < target && target <= a[hi]) lo = mid + 1;\n        else hi = mid - 1;\n"
        "    }\n}\nreturn -1;\n```\n\n"
        "## The `<=` in `a[lo] <= a[mid]`\nWhen `lo == mid` (two elements left), the left \"half\" "
        "is a single element and is sorted. A strict `<` misclassifies it and searches the wrong "
        "side. Distinct values are what make this test sufficient; with duplicates, `a[lo] == "
        "a[mid]` says nothing and the worst case becomes O(n)."
    ),
    py='''
def solve(a, k):
    target = k
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
''',
    java='''
    static int solve(int[] a, long target) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] == target) return mid;
            if (a[lo] <= a[mid]) {
                if (a[lo] <= target && target < a[mid]) hi = mid - 1;
                else lo = mid + 1;
            } else {
                if (a[mid] < target && target <= a[hi]) lo = mid + 1;
                else hi = mid - 1;
            }
        }
        return -1;
    }
''',
    examples=[("Example 1", "7 0\n4 5 6 7 0 1 2\n"), ("Example 2", "7 3\n4 5 6 7 0 1 2\n")],
    hidden=[
        ("Single element, missing", "1 0\n1\n"),
        ("Two elements", "2 1\n3 1\n"),
        ("Not rotated", "5 4\n1 2 3 4 5\n"),
        ("Target at the pivot", "6 10\n30 40 50 10 20 25\n"),
    ],
    expl=[
        "0 is at index 4.",
        "3 is not in the array.",
    ],
    prereqs=[
        ("binary_search", "Discarding half the range each step, using the half that is known to be sorted."),
        ("array_patterns", "A rotation leaves at most one break in order, so one side of any split is intact."),
    ],
)

_p(
    "koko-eating-bananas", "Koko Eating Bananas", "Medium",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search"], companies=["Google", "Airbnb"],
    shape="arr_k", ret="long", todo="binary search the speed in [1, max pile]; hours at speed s is the sum of ceil(pile / s)",
    description=(
        "Koko has piles of bananas and `h` hours. Each hour she picks one pile and eats up to `k` "
        "bananas from it (if the pile has fewer, she eats them all and waits out the hour). What "
        "is the **minimum** eating speed `k` that finishes every pile within `h` hours?\n\n"
        "### Input\n- Line 1: `n h`.\n- Line 2: the `n` pile sizes.\n\n### Output\nThe minimum speed."
    ),
    constraints="1 ≤ n ≤ 10^4\nn ≤ h ≤ 10^9\n1 ≤ pile ≤ 10^9",
    hints=[
        "At speed s, a pile of p takes ceil(p / s) hours. Summing that over the piles tells you whether s is fast enough.",
        "If speed s is fast enough, every faster speed is too — feasibility is monotone in s.",
        "Binary search s over [1, max pile]. Compute ceil(p / s) as (p + s − 1) / s in long arithmetic.",
    ],
    opt=("O(n log M)", "O(1)", "log M speeds tried, each checked in O(n), where M is the largest pile."),
    editorial=(
        "## The one thing this teaches\n**Binary search on the answer.** The array is not sorted "
        "and nothing is being looked up. What is monotone is the *answer space*: slow speeds fail, "
        "fast speeds succeed, and somewhere is the first speed that succeeds.\n\n"
        "## Approach\n```java\nlong lo = 1, hi = maxPile;\nwhile (lo < hi) {\n"
        "    long mid = lo + (hi - lo) / 2;\n"
        "    if (hoursAt(mid) <= h) hi = mid;      // fast enough; try slower\n    else lo = mid + 1;\n}\nreturn lo;\n\n"
        "long hoursAt(long s) {\n    long total = 0;\n"
        "    for (int p : piles) total += (p + s - 1) / s;\n    return total;\n}\n```\n\n"
        "## The bounds\nSpeed `maxPile` always works, since each pile takes one hour and `h ≥ n`. "
        "Speed 1 is the least that could. Anything above `maxPile` is never the minimum.\n\n"
        "## The overflow\n`p + s − 1` with `p` and `s` near 10⁹ exceeds an `int`, and the total "
        "hours at low speed can reach 10⁴ · 10⁹. Both need `long`."
    ),
    py='''
def solve(a, k):
    h = k
    lo, hi = 1, max(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum((p + mid - 1) // mid for p in a) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long solve(int[] piles, long h) {
        long lo = 1, hi = 0;
        for (int p : piles) hi = Math.max(hi, p);
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            long hours = 0;
            for (int p : piles) hours += (p + mid - 1) / mid;
            if (hours <= h) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "4 8\n3 6 7 11\n"), ("Example 2", "5 5\n30 11 23 4 20\n")],
    hidden=[
        ("Lots of time", "5 6\n30 11 23 4 20\n"),
        ("Single pile, one hour", "1 1\n1000000000\n"),
        ("Hours far exceed piles", "3 1000000000\n1000000000 1000000000 1000000000\n"),
        ("All ones", "4 4\n1 1 1 1\n"),
    ],
    expl=[
        "At speed 4: 1 + 2 + 2 + 3 = 8 hours. Speed 3 needs 10.",
        "With one hour per pile, the speed must be the largest pile.",
    ],
    prereqs=[
        ("binary_search", "Binary search over possible speeds, using a monotone 'fast enough' check."),
        ("overflow", "Ceiling division and hour totals computed in long."),
    ],
)

_p(
    "min-days-for-bouquets", "Minimum Days to Make Bouquets", "Medium",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search", "Greedy"], companies=["Google", "Amazon"],
    shape="arr_xy", ret="long", todo="binary search the day; on day d, greedily count runs of k bloomed flowers",
    description=(
        "Flower `i` blooms on day `bloom[i]` and stays bloomed. A bouquet needs `k` **adjacent** "
        "bloomed flowers, and each flower can be in one bouquet. What is the earliest day you can "
        "make `m` bouquets?\n\n"
        "### Input\n- Line 1: `n m k`.\n- Line 2: the `n` bloom days.\n\n"
        "### Output\nThe earliest day, or `-1` if `m` bouquets can never be made."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ bloom[i] ≤ 10^9\n1 ≤ m ≤ 10^6\n1 ≤ k ≤ n",
    hints=[
        "If m·k > n there are not enough flowers, ever: −1. (m·k can overflow an int.)",
        "Whether day d is enough is monotone in d: more days, more bloomed flowers.",
        "To check day d, scan left to right counting consecutive bloomed flowers; every time the run reaches k, make a bouquet and reset.",
    ],
    opt=("O(n log D)", "O(1)", "log D candidate days over [min bloom, max bloom], each checked in one pass."),
    editorial=(
        "## The one thing this teaches\n**The check inside a binary search can itself be "
        "greedy.** Deciding whether day `d` suffices is a small problem of its own — packing runs "
        "of bloomed flowers into bouquets — and taking a bouquet the moment a run reaches `k` is "
        "optimal, because leaving flowers unused never helps a later bouquet.\n\n"
        "## Approach\n```java\nif ((long) m * k > n) return -1;\nlong lo = minBloom, hi = maxBloom;\n"
        "while (lo < hi) {\n    long mid = lo + (hi - lo) / 2;\n"
        "    if (bouquetsOn(mid) >= m) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n\n"
        "long bouquetsOn(long day) {\n    long made = 0; int run = 0;\n"
        "    for (int b : bloom) {\n        run = b <= day ? run + 1 : 0;\n"
        "        if (run == k) { made++; run = 0; }\n    }\n    return made;\n}\n```\n\n"
        "## Why the answer is one of the bloom days\nNothing changes between two consecutive "
        "bloom days, so the earliest working day is always some `bloom[i]` — which is why "
        "searching `[min, max]` of the bloom days, not `[1, 10⁹]`, is enough (and both work)."
    ),
    py='''
def solve(a, x, y):
    m, k = x, y
    if m * k > len(a):
        return -1

    def made(day):
        count = run = 0
        for b in a:
            run = run + 1 if b <= day else 0
            if run == k:
                count += 1
                run = 0
        return count

    lo, hi = min(a), max(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if made(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long solve(int[] bloom, long m, long k) {
        if (m * k > bloom.length) return -1;
        long lo = Long.MAX_VALUE, hi = 0;
        for (int b : bloom) { lo = Math.min(lo, b); hi = Math.max(hi, b); }
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            long made = 0;
            int run = 0;
            for (int b : bloom) {
                run = b <= mid ? run + 1 : 0;
                if (run == k) { made++; run = 0; }
            }
            if (made >= m) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "5 3 1\n1 10 3 10 2\n"), ("Example 2", "5 3 2\n1 10 3 10 2\n")],
    hidden=[
        ("Adjacency matters", "7 2 3\n7 7 7 7 12 7 7\n"),
        ("Late single flower", "1 1 1\n1000000000\n"),
        ("Exactly enough flowers", "6 2 3\n1 2 3 4 5 6\n"),
        ("Runs reset", "6 1 3\n1 9 1 1 9 1\n"),
    ],
    expl=[
        "On day 3, flowers 0, 2 and 4 have bloomed: three one-flower bouquets.",
        "Six flowers are needed and only five exist.",
    ],
    prereqs=[
        ("binary_search", "Binary search over days with a monotone 'enough bouquets' check."),
        ("greedy", "Inside the check, closing a bouquet as soon as a run reaches k is optimal."),
    ],
)

_p(
    "split-array-largest-sum", "Split Array Largest Sum", "Hard",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search", "Greedy"], companies=["Google", "Meta", "Amazon"],
    shape="arr_k", ret="long", todo="binary search the largest allowed sum; greedily count how many pieces that forces",
    description=(
        "Split the array into `k` **non-empty contiguous** parts so that the **largest** part sum "
        "is as small as possible. Print that smallest possible largest sum.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` non-negative integers.\n\n"
        "### Output\nThe minimised largest part sum."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ k ≤ min(50, n)\n0 ≤ a[i] ≤ 10^6",
    hints=[
        "Guess a cap S. Greedily extend each part until adding the next element would exceed S; count the parts.",
        "If that greedy needs at most k parts, cap S is achievable — and so is every larger cap.",
        "Binary search S between max(a) (no part can be smaller) and sum(a) (one part).",
    ],
    opt=("O(n log Σ)", "O(1)", "log(sum) caps tried, each checked by one greedy pass."),
    editorial=(
        "## The one thing this teaches\n**Turn \"minimise the maximum\" into \"is this maximum "
        "achievable?\"** The optimisation is hard to attack directly; the decision version — can "
        "every part stay at or under S using at most k parts? — has a greedy answer, and it is "
        "monotone in S. That combination is binary search on the answer.\n\n"
        "## Approach\n```java\nlong lo = max(a), hi = sum(a);\nwhile (lo < hi) {\n"
        "    long mid = lo + (hi - lo) / 2;\n    if (partsNeeded(mid) <= k) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n\n"
        "int partsNeeded(long cap) {\n    int parts = 1; long cur = 0;\n"
        "    for (int x : a) {\n        if (cur + x > cap) { parts++; cur = 0; }\n        cur += x;\n    }\n    return parts;\n}\n```\n\n"
        "## Why \"at most k\" and not \"exactly k\"\nIf the greedy uses fewer than k parts, a "
        "longer part can always be split further without increasing the maximum (n ≥ k "
        "guarantees there are enough elements). So fewer parts is still a yes.\n\n"
        "## Why the greedy check is right\nFor a fixed cap, making each part as long as allowed "
        "never needs more parts than any other valid split — ending a part early only pushes "
        "elements into later parts.\n\n"
        "The DP over (prefix, parts) solves it in O(k·n²) and is worth knowing as the slower route."
    ),
    py='''
def solve(a, k):
    def parts(cap):
        count, cur = 1, 0
        for x in a:
            if cur + x > cap:
                count += 1
                cur = 0
            cur += x
        return count

    lo, hi = max(a), sum(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if parts(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
''',
    java='''
    static long solve(int[] a, long k) {
        long lo = 0, hi = 0;
        for (int x : a) { lo = Math.max(lo, x); hi += x; }
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            int parts = 1;
            long cur = 0;
            for (int x : a) {
                if (cur + x > mid) { parts++; cur = 0; }
                cur += x;
            }
            if (parts <= k) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "5 2\n7 2 5 10 8\n"), ("Example 2", "5 2\n1 2 3 4 5\n")],
    hidden=[
        ("One part", "4 1\n1 4 4 2\n"),
        ("As many parts as elements", "4 4\n1 4 4 2\n"),
        ("Zeros", "5 3\n0 0 0 0 5\n"),
        ("Big values", "3 2\n1000000 1000000 1000000\n"),
    ],
    expl=[
        "`[7, 2, 5]` and `[10, 8]`: sums 14 and 18. No split does better than 18.",
        "`[1, 2, 3]` and `[4, 5]`: largest sum 9.",
    ],
    prereqs=[
        ("binary_search", "Binary search over the cap on part sums, using a monotone feasibility check."),
        ("greedy", "For a fixed cap, making each part as long as possible minimises the number of parts."),
    ],
)

_p(
    "lemonade-change", "Lemonade Change", "Easy",
    topics=["Greedy", "Simulation"], subtopics=["Greedy", "Simulation"], companies=["Amazon"],
    shape="arr", ret="String", todo="count $5 and $10 bills; for $20 prefer giving $10 + $5 over three $5s",
    description=(
        "Lemonade costs $5. Customers queue up and each pays with a $5, $10 or $20 bill. You start "
        "with no change. Can you give every customer correct change, in order?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` bills.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 10^5\nEach bill is 5, 10 or 20.",
    hints=[
        "Only $5 and $10 bills are ever useful as change. Count them.",
        "A $10 needs one $5 back. A $20 needs $15: either a $10 and a $5, or three $5s.",
        "When both work, give the $10 — a $5 can serve any later customer, a $10 cannot.",
    ],
    opt=("O(n)", "O(1)", "Two counters updated once per customer."),
    editorial=(
        "## The one thing this teaches\n**Greedy means keeping the most flexible resource.** "
        "The only real decision is how to change a $20. Both options are correct *now*; the "
        "difference is what they leave. A $5 can make change for a $10 or a $20, a $10 only helps "
        "with a $20, so spend the $10.\n\n"
        "## Approach\n```java\nint fives = 0, tens = 0;\nfor (int b : bills) {\n"
        "    if (b == 5) fives++;\n"
        "    else if (b == 10) { if (fives == 0) return \"NO\"; fives--; tens++; }\n"
        "    else if (tens > 0 && fives > 0) { tens--; fives--; }\n"
        "    else if (fives >= 3) fives -= 3;\n    else return \"NO\";\n}\nreturn \"YES\";\n```\n\n"
        "## The order that punishes the other choice\n`5 5 5 5 10 20 10 10`: before the $20 you "
        "hold three $5s and a $10. Paying `10 + 5` leaves two $5s, enough for both final $10s. "
        "Paying three $5s leaves only the $10, and the next customer cannot be served."
    ),
    py='''
def solve(a):
    fives = tens = 0
    for b in a:
        if b == 5:
            fives += 1
        elif b == 10:
            if fives == 0:
                return "NO"
            fives -= 1
            tens += 1
        elif tens > 0 and fives > 0:
            tens -= 1
            fives -= 1
        elif fives >= 3:
            fives -= 3
        else:
            return "NO"
    return "YES"
''',
    java='''
    static String solve(int[] bills) {
        int fives = 0, tens = 0;
        for (int b : bills) {
            if (b == 5) fives++;
            else if (b == 10) { if (fives == 0) return "NO"; fives--; tens++; }
            else if (tens > 0 && fives > 0) { tens--; fives--; }
            else if (fives >= 3) fives -= 3;
            else return "NO";
        }
        return "YES";
    }
''',
    examples=[("Example 1", "5\n5 5 5 10 20\n"), ("Example 2", "5\n5 5 10 10 20\n")],
    hidden=[
        ("First customer pays big", "1\n10\n"),
        ("Greedy choice matters", "8\n5 5 5 5 10 20 10 10\n"),
        ("Three fives for a twenty", "4\n5 5 5 20\n"),
        ("Only fives", "3\n5 5 5\n"),
    ],
    expl=[
        "Change for the $10 is a $5; change for the $20 is the $10 and a $5.",
        "After two $10s there is no $5 left for the $20.",
    ],
    prereqs=[
        ("greedy", "Spending the less flexible bill first keeps later options open."),
        ("simulation", "Processing customers in order with two counters."),
    ],
)

_p(
    "partition-labels", "Partition Labels", "Medium",
    topics=["Greedy", "Strings"], subtopics=["Greedy", "Two Pointers"], companies=["Amazon", "Meta"],
    shape="str", ret="String", todo="record each letter's last index; extend the current part to the furthest last index seen",
    description=(
        "Split a string into as **many** parts as possible so that each letter appears in at most "
        "one part. Print the sizes of the parts, in order.\n\n"
        "### Input\nOne line: `s`.\n\n### Output\nThe part sizes, separated by spaces."
    ),
    constraints="1 ≤ |s| ≤ 500\ns consists of lowercase English letters.",
    hints=[
        "A part that contains a letter must extend at least to that letter's LAST occurrence.",
        "Precompute last[c] for every letter.",
        "Walk the string, extending end = max(end, last[s[i]]). When i reaches end, the part is closed.",
    ],
    opt=("O(n)", "O(1)", "One pass for last occurrences and one to cut; the table has 26 entries."),
    editorial=(
        "## The one thing this teaches\n**Close a part at the first moment it is allowed.** A part "
        "starting at `start` must reach the last occurrence of every letter inside it. Growing "
        "`end` to cover each letter as it is met, and cutting as soon as `i == end`, gives the "
        "shortest valid first part — and a shortest first part leaves the most room for more "
        "parts.\n\n"
        "## Approach\n```java\nint[] last = new int[26];\nfor (int i = 0; i < n; i++) last[s.charAt(i) - 'a'] = i;\n"
        "int start = 0, end = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    end = Math.max(end, last[s.charAt(i) - 'a']);\n"
        "    if (i == end) { sizes.add(end - start + 1); start = i + 1; }\n}\n```\n\n"
        "## It is merging intervals\nEach letter spans `[first, last]`. Parts are the merged "
        "groups of overlapping spans — the sweep above is Merge Intervals with the intervals "
        "already in order of start."
    ),
    py='''
def solve(s):
    last = {ch: i for i, ch in enumerate(s)}
    sizes = []
    start = end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:
            sizes.append(end - start + 1)
            start = i + 1
    return " ".join(map(str, sizes))
''',
    java='''
    static String solve(String s) {
        int n = s.length();
        int[] last = new int[26];
        for (int i = 0; i < n; i++) last[s.charAt(i) - 'a'] = i;
        StringBuilder sb = new StringBuilder();
        int start = 0, end = 0;
        for (int i = 0; i < n; i++) {
            end = Math.max(end, last[s.charAt(i) - 'a']);
            if (i == end) {
                if (sb.length() > 0) sb.append(' ');
                sb.append(end - start + 1);
                start = i + 1;
            }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "ababcbacadefegdehijhklij\n"), ("Example 2", "eccbbbbdec\n")],
    hidden=[
        ("Single letter", "a\n"),
        ("All distinct", "abcd\n"),
        ("One letter spans everything", "abca\n"),
    ],
    expl=[
        "`ababcbaca`, `defegde`, `hijhklij`: 9, 7, 8.",
        "`e` appears at both ends, so everything is one part.",
    ],
    prereqs=[
        ("greedy", "Cutting a part at the first index where it is allowed maximises the number of parts."),
        ("intervals", "Each letter's first-to-last span is an interval; parts are merged overlapping spans."),
    ],
)

_p(
    "two-city-scheduling", "Two City Scheduling", "Medium",
    topics=["Greedy", "Sorting"], subtopics=["Greedy", "Sorting"], companies=["Bloomberg"],
    shape="pairs", ret="long", todo="sort people by costA − costB; send the first half to A and the rest to B",
    description=(
        "`2m` people must be flown to interviews, **exactly half** to city A and half to city B. "
        "Person `i` costs `a_i` to fly to A and `b_i` to fly to B. Minimise the total cost.\n\n"
        "### Input\n- Line 1: `2m`.\n- Next `2m` lines: `a b`.\n\n### Output\nThe minimum total cost."
    ),
    constraints="2 ≤ 2m ≤ 100 (even)\n1 ≤ a_i, b_i ≤ 1000",
    hints=[
        "Imagine everyone flies to B first. Moving person i to A changes the total by a_i − b_i.",
        "Exactly m people must move. Which m moves save the most — or cost the least?",
        "Sort by a_i − b_i and move the m smallest.",
    ],
    opt=("O(n log n)", "O(1)", "One sort by the cost difference."),
    editorial=(
        "## The one thing this teaches\n**Sort by the marginal cost of the decision.** Sorting by "
        "cheapest A cost, or cheapest overall, fails: what matters is how much *more* one choice "
        "costs than the other. Starting from \"everyone to B\", each person has a fixed price "
        "`a − b` for switching to A, and the best m switches are the m cheapest.\n\n"
        "## Approach\n```java\nArrays.sort(p, (x, y) -> Integer.compare(x[0] - x[1], y[0] - y[1]));\n"
        "long total = 0;\nfor (int i = 0; i < n; i++) total += i < n / 2 ? p[i][0] : p[i][1];\n```\n\n"
        "## Why it is optimal\nThe total is `Σb + Σ(a − b)` over the people sent to A. `Σb` is "
        "fixed, so minimising the total is exactly choosing the m smallest differences — no "
        "exchange argument needed beyond that rewrite."
    ),
    py='''
def solve(p):
    q = sorted(p, key=lambda x: x[0] - x[1])
    half = len(q) // 2
    return sum(a for a, _ in q[:half]) + sum(b for _, b in q[half:])
''',
    java='''
    static long solve(int[][] p) {
        Arrays.sort(p, (x, y) -> Integer.compare(x[0] - x[1], y[0] - y[1]));
        long total = 0;
        for (int i = 0; i < p.length; i++) total += i < p.length / 2 ? p[i][0] : p[i][1];
        return total;
    }
''',
    examples=[("Example 1", "4\n10 20\n30 200\n400 50\n30 20\n"), ("Example 2", "2\n5 7\n9 3\n")],
    hidden=[
        ("Everyone prefers A", "4\n1 100\n2 100\n3 100\n4 100\n"),
        ("Cheapest A is a trap", "4\n1 2\n100 500\n2 1\n50 51\n"),
        ("Ties", "2\n10 10\n10 10\n"),
    ],
    expl=[
        "Send people 0 and 1 to A (10 + 30) and 2 and 3 to B (50 + 20): 110.",
        "Person 0 to A for 5, person 1 to B for 3.",
    ],
    prereqs=[
        ("greedy", "Choosing by the marginal cost of switching, not by either cost alone."),
        ("sorting", "Sorting people by a − b puts the cheapest switches first."),
    ],
)

_p(
    "valid-parenthesis-star", "Valid Parenthesis String (with *)", "Medium",
    topics=["Greedy", "Strings"], subtopics=["Greedy", "Stack"], companies=["Meta", "Amazon"],
    shape="str", ret="String", todo="track the lowest and highest possible open count; * widens the range",
    description=(
        "A string contains `(`, `)` and `*`. Each `*` may be treated as `(`, `)` or nothing. Can the "
        "string be made into a valid parentheses string?\n\n"
        "### Input\nOne line: `s`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s| ≤ 100\ns consists of '(', ')' and '*'.",
    hints=[
        "Trying all 3^k choices for the stars is exponential.",
        "Instead of one open count, keep a RANGE [lo, hi] of open counts that some choice could give.",
        "`(` adds 1 to both, `)` subtracts 1 from both, `*` does lo−1 and hi+1. If hi < 0, fail; clamp lo at 0. At the end, valid iff lo == 0.",
    ],
    opt=("O(n)", "O(1)", "Two integers updated per character."),
    editorial=(
        "## The one thing this teaches\n**Track the set of possible states, not one state.** "
        "Without stars, one counter of open brackets decides validity. With stars the counter "
        "could be several values at once — but the possible values always form a contiguous "
        "range, so two numbers describe all of them.\n\n"
        "## Approach\n```java\nint lo = 0, hi = 0;          // min and max possible open brackets\n"
        "for (char c : s.toCharArray()) {\n"
        "    if (c == '(') { lo++; hi++; }\n    else if (c == ')') { lo--; hi--; }\n"
        "    else { lo--; hi++; }            // ')' or '(' or nothing\n"
        "    if (hi < 0) return \"NO\";      // too many ')' even with every * as '('\n"
        "    lo = Math.max(lo, 0);         // a count below 0 is not a real option\n}\n"
        "return lo == 0 ? \"YES\" : \"NO\";\n```\n\n"
        "## The clamp\n`lo` going negative means \"some choice closed more than was open\" — that "
        "choice is invalid, so it is removed from the range rather than kept. Without the clamp, "
        "`**((` ends with `lo == 0` — two stars closing brackets that were never opened, "
        "cancelled out by the two opens after them — and is wrongly accepted."
    ),
    py='''
def solve(s):
    lo = hi = 0
    for ch in s:
        if ch == "(":
            lo += 1
            hi += 1
        elif ch == ")":
            lo -= 1
            hi -= 1
        else:
            lo -= 1
            hi += 1
        if hi < 0:
            return "NO"
        lo = max(lo, 0)
    return "YES" if lo == 0 else "NO"
''',
    java='''
    static String solve(String s) {
        int lo = 0, hi = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(') { lo++; hi++; }
            else if (c == ')') { lo--; hi--; }
            else { lo--; hi++; }
            if (hi < 0) return "NO";
            lo = Math.max(lo, 0);
        }
        return lo == 0 ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "(*)\n"), ("Example 2", "(*))\n")],
    hidden=[
        ("Close before open", ")(\n"),
        ("Star cannot rescue the order", "*)(\n"),
        ("Stars as nothing", "(**\n"),
        ("Too many opens", "(((*)\n"),
        ("The clamp matters", "**((\n"),
    ],
    expl=[
        "Treat `*` as nothing.",
        "Treat `*` as `(`: `(())`.",
    ],
    prereqs=[
        ("greedy", "Maintaining the range of achievable open counts instead of branching on each star."),
        ("stack", "The single-bracket-type check collapses a stack to a counter; the range generalises it."),
    ],
)

_p(
    "candy", "Candy", "Hard",
    topics=["Greedy", "Arrays"], subtopics=["Greedy"], companies=["Amazon", "Google"],
    shape="arr", ret="long", todo="left-to-right pass for the left neighbour rule, right-to-left for the right, take the max",
    description=(
        "Children stand in a line with ratings. Give candies so that every child gets **at least "
        "one**, and a child with a **higher rating than a neighbour** gets **more candies than "
        "that neighbour**. Find the minimum total.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` ratings.\n\n### Output\nThe minimum number of candies."
    ),
    constraints="1 ≤ n ≤ 2·10^4\n0 ≤ rating ≤ 2·10^4",
    hints=[
        "Each child has two constraints, one per neighbour. Satisfy them one direction at a time.",
        "Left to right: if ratings[i] > ratings[i−1], left[i] = left[i−1] + 1, else 1.",
        "Right to left the same way. Each child needs max(left[i], right[i]).",
    ],
    opt=("O(n)", "O(n)", "Two linear passes; the right pass can reuse one array and a running value."),
    editorial=(
        "## The one thing this teaches\n**Split a two-sided constraint into two one-sided ones.** "
        "A single left-to-right pass can only react to the neighbour it has seen; a decreasing "
        "run like `5 4 3 2 1` needs information flowing from the right. Two passes each enforce "
        "one side exactly, and taking the maximum satisfies both without adding anything extra.\n\n"
        "## Approach\n```java\nint[] c = new int[n];\nArrays.fill(c, 1);\n"
        "for (int i = 1; i < n; i++) if (r[i] > r[i - 1]) c[i] = c[i - 1] + 1;\n"
        "for (int i = n - 2; i >= 0; i--) if (r[i] > r[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);\n"
        "long total = 0;\nfor (int x : c) total += x;\n```\n\n"
        "## Why it is minimal\nAfter the left pass, `c[i]` is the smallest value satisfying every "
        "left constraint along the increasing run ending at i; the right pass likewise for the "
        "right. Any valid assignment must be at least both, so the max is a lower bound — and it "
        "is achieved.\n\n"
        "## Equal ratings\nNeighbours with equal ratings impose nothing: `1 2 2` needs `1 2 1`, "
        "total 4."
    ),
    py='''
def solve(a):
    n = len(a)
    c = [1] * n
    for i in range(1, n):
        if a[i] > a[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if a[i] > a[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)
''',
    java='''
    static long solve(int[] r) {
        int n = r.length;
        int[] c = new int[n];
        Arrays.fill(c, 1);
        for (int i = 1; i < n; i++) if (r[i] > r[i - 1]) c[i] = c[i - 1] + 1;
        for (int i = n - 2; i >= 0; i--) if (r[i] > r[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);
        long total = 0;
        for (int x : c) total += x;
        return total;
    }
''',
    examples=[("Example 1", "3\n1 0 2\n"), ("Example 2", "3\n1 2 2\n")],
    hidden=[
        ("Single child", "1\n7\n"),
        ("Strictly decreasing", "5\n5 4 3 2 1\n"),
        ("Valley then peak", "7\n1 3 4 5 2 1 0\n"),
        ("All equal", "4\n3 3 3 3\n"),
    ],
    expl=[
        "2, 1, 2 candies.",
        "1, 2, 1 — equal neighbours need nothing.",
    ],
    prereqs=[
        ("greedy", "Satisfying each side's constraint with the fewest candies, then combining with max."),
        ("array_patterns", "A forward and a backward pass over the same array."),
    ],
)
