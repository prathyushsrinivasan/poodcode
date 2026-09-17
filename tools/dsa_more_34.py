# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 34 — ten compact problems, mostly Easy, each with one clear idea.
#
#   pascal-triangle-row        update one row in place from right to left
#   bulb-switcher              a bulb ends on iff it has an odd number of divisors — a perfect square
#   teemo-attacking            each attack adds min(duration, gap to the next attack)
#   assign-cookies             smallest cookie that satisfies the least greedy child
#   can-place-flowers          plant greedily at the first free spot
#   third-maximum              three slots of distinct maxima, with a sentinel that cannot collide
#   partition-string-unique    start a new piece exactly when a letter repeats
#   baseball-game              the record is a stack
#   height-checker             compare with the sorted order, sorted by counting
#   count-good-substrings      a length-3 window with three distinct letters
# ===========================================================================

_p(
    "pascal-triangle-row", "Pascal's Triangle Row", "Easy",
    topics=["Dynamic Programming", "Recursion", "Math"], subtopics=["In-place Row Update"], companies=["Amazon", "Adobe"],
    shape="n", ret="String", todo="start with [1]; for each new row, update entries from right to left with row[j] += row[j − 1], then append 1",
    description=(
        "Print row `k` (0-indexed) of Pascal's triangle, where each entry is the sum of the two "
        "entries above it and every row starts and ends with 1.\n\n"
        "### Input\nOne line: `k`.\n\n"
        "### Output\nThe row, values separated by spaces."
    ),
    constraints="0 ≤ k ≤ 33",
    hints=[
        "Building the whole triangle takes O(k²) space; only the previous row is ever needed.",
        "Update a single array in place: new[j] = old[j] + old[j − 1].",
        "Go from right to left so old[j − 1] is still unchanged when new[j] is computed. Then append a 1.",
    ],
    opt=("O(k²)", "O(k)", "k rows, each updated in O(k), in one array."),
    editorial=(
        "## The one thing this teaches\n**Iterate in the direction that preserves what you still "
        "need.** Each entry depends on its own old value and its left neighbour's old value. "
        "Scanning right to left overwrites a position only after its right neighbour has used it.\n\n"
        "## Approach\n```java\nlong[] row = new long[k + 1];\nrow[0] = 1;\nfor (int i = 1; i <= k; i++)\n"
        "    for (int j = i; j >= 1; j--) row[j] += row[j - 1];   // row[i] was 0, becomes 1\n```\n\n"
        "## Why left to right fails\nComputing `row[1]` first changes it before `row[2]` reads it, "
        "so `row[2]` would add a value from the *new* row.\n\n"
        "## Closed form\nEntry j of row k is `C(k, j)`, and `C(k, j) = C(k, j − 1) · (k − j + 1) / j` "
        "builds the row directly — the division is exact at every step."
    ),
    py='''
def solve(n):
    from math import comb
    return " ".join(str(comb(n, j)) for j in range(n + 1))
''',
    java='''
    static String solve(long kk) {
        int k = (int) kk;
        long[] row = new long[k + 1];
        row[0] = 1;
        for (int i = 1; i <= k; i++)
            for (int j = i; j >= 1; j--) row[j] += row[j - 1];
        StringBuilder sb = new StringBuilder();
        for (int j = 0; j <= k; j++) { if (j > 0) sb.append(' '); sb.append(row[j]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n"), ("Example 2", "0\n"), ("Example 3", "1\n")],
    hidden=[
        ("Row four", "4\n"),
        ("Row ten", "10\n"),
        ("Largest row", "33\n"),
    ],
    expl=[
        "Row 2 is 1 2 1; adding neighbours gives 1 3 3 1.",
        "The top of the triangle.",
        "Two ones.",
    ],
    prereqs=[
        ("dp", "A one-dimensional table updated in place."),
        ("recurrence", "Each entry as the sum of two entries in the previous row."),
    ],
)

_p(
    "bulb-switcher", "Bulb Switcher", "Medium",
    topics=["Math"], subtopics=["Divisors", "Perfect Squares"], companies=["Microsoft"],
    shape="n", ret="long", todo="bulb i is toggled once per divisor of i; only perfect squares have an odd number of divisors — count them",
    description=(
        "`n` bulbs start off. In round 1 every bulb is toggled; in round 2 every 2nd bulb; in "
        "round `i` every `i`-th bulb; up to round `n`. How many bulbs are on at the end?\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe number of bulbs that are on."
    ),
    constraints="0 ≤ n ≤ 10^18",
    hints=[
        "Simulating n rounds over n bulbs is O(n²) — hopeless at 10^18.",
        "Bulb b is toggled in round i exactly when i divides b. So it ends on when b has an odd number of divisors.",
        "Divisors pair up as (d, b / d) — except when d = b / d. Only perfect squares have an unpaired divisor. Count the squares ≤ n: ⌊√n⌋.",
    ],
    opt=("O(log n)", "O(1)", "An integer square root by binary search."),
    editorial=(
        "## The one thing this teaches\n**Reduce a simulation to a property of each element.** "
        "Each bulb's final state depends only on how many times it is toggled, which is its "
        "number of divisors — and divisor counts are odd exactly for perfect squares.\n\n"
        "## Approach\n```java\nlong lo = 0, hi = 1_000_000_000L;           // largest r with r·r ≤ n\n"
        "while (lo < hi) {\n    long mid = (lo + hi + 1) / 2;\n    if (mid * mid <= n) lo = mid; else hi = mid - 1;\n}\nreturn lo;\n```\n\n"
        "## Why not Math.sqrt\n`(long) Math.sqrt(n)` can be off by one for n near 10^18, where a "
        "double cannot represent every integer. An integer binary search is exact.\n\n"
        "## Walkthrough: n = 10\nSquares 1, 4, 9 have divisors {1}, {1, 2, 4}, {1, 3, 9}. Every "
        "other bulb has an even count. Answer 3 = ⌊√10⌋."
    ),
    py='''
def solve(n):
    from math import isqrt
    return isqrt(n)
''',
    java='''
    static long solve(long n) {
        long lo = 0, hi = 1_000_000_000L;
        while (lo < hi) {
            long mid = (lo + hi + 1) / 2;
            if (mid * mid <= n) lo = mid; else hi = mid - 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "3\n"), ("Example 2", "0\n"), ("Example 3", "1\n")],
    hidden=[
        ("Perfect square", "100\n"),
        ("Just below a square", "99\n"),
        ("Largest", "1000000000000000000\n"),
        ("Just below the largest square", "999999999999999999\n"),
    ],
    expl=[
        "After round 1 all are on; round 2 turns off bulb 2; round 3 turns off bulb 3. Only bulb 1 remains.",
        "There are no bulbs.",
        "One bulb, toggled once.",
    ],
    prereqs=[
        ("math_digits", "Divisor pairs and perfect squares."),
        ("binary_search", "An exact integer square root."),
    ],
)

_p(
    "teemo-attacking", "Teemo Attacking", "Easy",
    topics=["Intervals", "Arrays"], subtopics=["Overlapping Durations"], companies=["Riot Games"],
    shape="arr_k", ret="long", todo="for each attack except the last, add min(duration, next − current); add a full duration for the last",
    description=(
        "Each attack at time `t` poisons the target for the interval `[t, t + duration)`. A new "
        "attack while poisoned **resets** the timer rather than stacking. Attack times are "
        "strictly increasing. Print the total time the target is poisoned.\n\n"
        "### Input\n- Line 1: `n duration`.\n- Line 2: the `n` attack times.\n\n"
        "### Output\nThe total poisoned time."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ time ≤ 10^9, strictly increasing\n0 ≤ duration ≤ 10^9",
    hints=[
        "This is the total length of a union of intervals.",
        "Each interval can only be cut short by the next attack, since times are sorted.",
        "Add min(duration, next time − this time) for each attack, and the full duration for the last one. Totals exceed an int.",
    ],
    opt=("O(n)", "O(1)", "One pass over consecutive attack times."),
    editorial=(
        "## The one thing this teaches\n**Sorted intervals of equal length overlap only with "
        "their neighbours.** Each attack's contribution is cut off by the next attack at most, so "
        "the union's length is a sum of local minimums — no merging structure needed.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int i = 0; i + 1 < n; i++)\n"
        "    total += Math.min(duration, (long) t[i + 1] - t[i]);\nreturn total + duration;       // the last attack runs in full\n```\n\n"
        "## Why neighbours are enough\nIf the next attack at `t[i+1]` does not cut interval i "
        "short, no later attack can — they start even later.\n\n"
        "## Duration zero\nNo time is poisoned; every `min` is 0 and the final term adds 0."
    ),
    py='''
def solve(a, k):
    total = 0
    cur_start = cur_end = None
    for t in a:
        start, end = t, t + k
        if cur_end is None or start > cur_end:
            if cur_end is not None:
                total += cur_end - cur_start
            cur_start, cur_end = start, end
        else:
            cur_end = max(cur_end, end)
    return total + (cur_end - cur_start)
''',
    java='''
    static long solve(int[] t, long duration) {
        long total = 0;
        for (int i = 0; i + 1 < t.length; i++) total += Math.min(duration, (long) t[i + 1] - t[i]);
        return total + duration;
    }
''',
    examples=[("Example 1", "2 2\n1 4\n"), ("Example 2", "2 2\n1 2\n")],
    hidden=[
        ("Single attack", "1 5\n10\n"),
        ("Zero duration", "3 0\n1 2 3\n"),
        ("Mixed gaps", "4 3\n1 2 3 10\n"),
        ("Huge values", "2 1000000000\n0 1000000000\n"),
    ],
    expl=[
        "[1, 3) and [4, 6) do not overlap: 2 + 2.",
        "[1, 3) and [2, 4) overlap: poisoned from 1 to 4.",
    ],
    prereqs=[
        ("intervals", "The length of a union of sorted intervals."),
        ("overflow", "Totals up to about 2·10^9 and beyond."),
    ],
)

_p(
    "assign-cookies", "Assign Cookies", "Easy",
    topics=["Greedy", "Sorting", "Two Pointers"], subtopics=["Matching"], companies=["Amazon"],
    shape="arr2", ret="int", todo="sort both; walk the cookies, giving each to the least greedy unsatisfied child it can satisfy",
    description=(
        "Child `i` is content with a cookie of size at least `g[i]`. Each child gets at most one "
        "cookie and each cookie goes to at most one child. Print the maximum number of content "
        "children.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: greed factors `g`.\n- Line 3: `m`.\n- Line 4: cookie sizes `s` (m may be 0).\n\n"
        "### Output\nThe maximum number of content children."
    ),
    constraints="1 ≤ n ≤ 3·10^4\n0 ≤ m ≤ 3·10^4\n1 ≤ g[i], s[j] ≤ 2^31 − 1",
    hints=[
        "A big cookie spent on an easy child might be the only one that could satisfy a greedy child.",
        "Satisfy the least greedy children first, each with the smallest cookie that works.",
        "Sort both arrays and move two pointers: if the current cookie satisfies the current child, both advance; otherwise try a bigger cookie.",
    ],
    opt=("O(n log n + m log m)", "O(1)", "Two sorts and a linear two-pointer pass."),
    editorial=(
        "## The one thing this teaches\n**Match smallest with smallest-that-fits.** Using the "
        "smallest sufficient cookie keeps every larger cookie available, and serving the least "
        "greedy child first never blocks a greedier one that could have been served instead.\n\n"
        "## Approach\n```java\nArrays.sort(g);\nArrays.sort(s);\nint child = 0;\n"
        "for (int cookie = 0; cookie < s.length && child < g.length; cookie++)\n"
        "    if (s[cookie] >= g[child]) child++;        // this cookie satisfies this child\nreturn child;\n```\n\n"
        "## The exchange argument\nTake any optimal assignment. If the least greedy child is "
        "served by some cookie other than the smallest sufficient one, swapping the two cookies "
        "keeps both assignments valid. Repeating the swap gives the greedy assignment.\n\n"
        "## Unused cookies\nA cookie too small for the current child is too small for every "
        "remaining child, since they are sorted — so skipping it is safe."
    ),
    py='''
def solve(a, b):
    import bisect
    cookies = sorted(b)
    content = 0
    for greed in sorted(a):
        i = bisect.bisect_left(cookies, greed)
        if i == len(cookies):
            break
        cookies.pop(i)
        content += 1
    return content
''',
    java='''
    static int solve(int[] g, int[] s) {
        Arrays.sort(g);
        Arrays.sort(s);
        int child = 0;
        for (int cookie = 0; cookie < s.length && child < g.length; cookie++)
            if (s[cookie] >= g[child]) child++;
        return child;
    }
''',
    examples=[("Example 1", "3\n1 2 3\n2\n1 1\n"), ("Example 2", "2\n1 2\n3\n1 2 3\n")],
    hidden=[
        ("No cookies", "1\n5\n0\n"),
        ("Cookies too small", "3\n10 9 8\n3\n5 6 7\n"),
        ("More children than cookies", "4\n1 1 1 1\n2\n1 1\n"),
        ("Unsorted input", "4\n3 1 4 2\n3\n2 5 1\n"),
    ],
    expl=[
        "Both cookies have size 1, so only the child with greed 1 is content.",
        "Cookies 1 and 2 satisfy both children.",
    ],
    prereqs=[
        ("greedy", "Smallest sufficient resource for the smallest demand, with an exchange argument."),
        ("two_pointers", "Two pointers over two sorted arrays."),
    ],
)

_p(
    "can-place-flowers", "Can Place Flowers", "Easy",
    topics=["Arrays", "Greedy"], subtopics=["Traversal"], companies=["LinkedIn", "Meta"],
    shape="arr_k", ret="String", todo="scan left to right; plant in an empty plot whose neighbours (treating the edges as empty) are both empty",
    description=(
        "A flowerbed is a row of plots, `1` for planted and `0` for empty. Flowers cannot be in "
        "adjacent plots. Can `k` new flowers be planted without breaking that rule? Print `YES` "
        "or `NO`.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: the `n` plots (the initial bed has no adjacent flowers).\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 2·10^4\n0 ≤ k ≤ n",
    hints=[
        "A plot can take a flower if it and both neighbours are empty — outside the bed counts as empty.",
        "Planting as early as possible never hurts: it only blocks the next plot, which an alternative placement would also have to consider.",
        "Scan once, planting whenever allowed (and marking the plot), and stop once k flowers are placed.",
    ],
    opt=("O(n)", "O(1)", "One scan, updating the bed in place."),
    editorial=(
        "## The one thing this teaches\n**Earliest placement is safe when each choice only "
        "affects its neighbour.** Planting at the first valid plot blocks just the next plot. Any "
        "other valid solution can shift its first new flower left to the same plot.\n\n"
        "## Approach\n```java\nint planted = 0;\nfor (int i = 0; i < n && planted < k; i++) {\n"
        "    boolean leftEmpty = i == 0 || bed[i - 1] == 0;\n    boolean rightEmpty = i == n - 1 || bed[i + 1] == 0;\n"
        "    if (bed[i] == 0 && leftEmpty && rightEmpty) { bed[i] = 1; planted++; }\n}\nreturn planted >= k;\n```\n\n"
        "## The counting view\nA run of `L` empty plots between flowers holds `(L − 1) / 2` new "
        "flowers; padding the bed with an empty plot at each end handles the edges with the same "
        "formula.\n\n"
        "## k = 0\nZero flowers always fit."
    ),
    py='''
def solve(a, k):
    padded = [0] + list(a) + [0]
    capacity, run = 0, 0
    for v in padded:
        if v == 0:
            run += 1
        else:
            capacity += max(0, (run - 1) // 2)
            run = 0
    capacity += max(0, (run - 1) // 2)
    return "YES" if capacity >= k else "NO"
''',
    java='''
    static String solve(int[] bed, long k) {
        int n = bed.length;
        long planted = 0;
        for (int i = 0; i < n && planted < k; i++) {
            boolean leftEmpty = i == 0 || bed[i - 1] == 0;
            boolean rightEmpty = i == n - 1 || bed[i + 1] == 0;
            if (bed[i] == 0 && leftEmpty && rightEmpty) { bed[i] = 1; planted++; }
        }
        return planted >= k ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "5 1\n1 0 0 0 1\n"), ("Example 2", "5 2\n1 0 0 0 1\n")],
    hidden=[
        ("Single empty plot", "1 1\n0\n"),
        ("Nothing to plant", "1 0\n1\n"),
        ("Edges count as empty", "3 2\n0 0 0\n"),
        ("Blocked by a neighbour", "2 1\n1 0\n"),
        ("Long empty bed", "7 4\n0 0 0 0 0 0 0\n"),
    ],
    expl=[
        "The middle plot is free on both sides.",
        "Only one of the three empty plots can be used.",
    ],
    prereqs=[
        ("array_patterns", "Neighbour checks with the array edges treated as empty."),
        ("greedy", "Placing at the earliest valid position."),
    ],
)

_p(
    "third-maximum", "Third Maximum Number", "Easy",
    topics=["Arrays"], subtopics=["Top Three"], companies=["Amazon"],
    shape="arr", ret="long", todo="track the three largest distinct values; skip duplicates; if fewer than three exist, return the maximum",
    description=(
        "Print the **third largest distinct** value in the array. If there are fewer than three "
        "distinct values, print the largest.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe third distinct maximum, or the maximum."
    ),
    constraints="1 ≤ n ≤ 10^4\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "Sorting and deduplicating works in O(n log n).",
        "One pass with three slots — first, second, third — updated by shifting down.",
        "Ignore a value equal to a slot. Use long slots initialised below any int, so −2^31 in the input is not mistaken for \"empty\".",
    ],
    opt=("O(n)", "O(1)", "One pass with three slots."),
    editorial=(
        "## The one thing this teaches\n**Sentinels must lie outside the input range.** Starting "
        "the slots at `Integer.MIN_VALUE` breaks when the input contains that value: it would look "
        "like an empty slot. A long below every int avoids the collision.\n\n"
        "## Approach\n```java\nlong first = Long.MIN_VALUE, second = Long.MIN_VALUE, third = Long.MIN_VALUE;\n"
        "for (int x : a) {\n    if (x == first || x == second || x == third) continue;   // distinct only\n"
        "    if (x > first) { third = second; second = first; first = x; }\n"
        "    else if (x > second) { third = second; second = x; }\n"
        "    else if (x > third) third = x;\n}\nreturn third == Long.MIN_VALUE ? first : third;\n```\n\n"
        "## Why skip equal values\n`2 2 3 1`: without the duplicate check the second 2 would push "
        "into the second slot, and the \"third maximum\" would be 2 instead of 1.\n\n"
        "## Generalising\nFor the k-th distinct maximum, a sorted set capped at k elements does "
        "the same job in O(n log k)."
    ),
    py='''
def solve(a):
    distinct = sorted(set(a), reverse=True)
    return distinct[2] if len(distinct) >= 3 else distinct[0]
''',
    java='''
    static long solve(int[] a) {
        long first = Long.MIN_VALUE, second = Long.MIN_VALUE, third = Long.MIN_VALUE;
        for (int x : a) {
            if (x == first || x == second || x == third) continue;
            if (x > first) { third = second; second = first; first = x; }
            else if (x > second) { third = second; second = x; }
            else if (x > third) third = x;
        }
        return third == Long.MIN_VALUE ? first : third;
    }
''',
    examples=[("Example 1", "3\n3 2 1\n"), ("Example 2", "2\n1 2\n"), ("Example 3", "4\n2 2 3 1\n")],
    hidden=[
        ("Smallest int is a real value", "3\n-2147483648 1 2\n"),
        ("All equal", "5\n5 5 5 5 5\n"),
        ("Many duplicates", "7\n1 1 2 2 3 3 4\n"),
        ("Single value", "1\n-7\n"),
    ],
    expl=[
        "The distinct values are 3, 2, 1.",
        "Only two distinct values, so the maximum.",
        "Distinct values 3, 2, 1 — the repeated 2 counts once.",
    ],
    prereqs=[
        ("prefix_max", "Tracking the largest values seen in one pass."),
        ("overflow", "A sentinel outside the int range."),
    ],
)

_p(
    "partition-string-unique", "Optimal Partition of String", "Medium",
    topics=["Greedy", "Hashing", "Strings"], subtopics=["Greedy Cuts"], companies=["Amazon", "Google"],
    shape="str", ret="int", todo="extend the current piece while its letters are unique; on a repeat, start a new piece with that letter",
    description=(
        "Split `s` into the fewest substrings such that **no letter repeats within a substring**. "
        "Print the number of substrings.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe minimum number of substrings."
    ),
    constraints="1 ≤ |s| ≤ 10^5\nLowercase English letters",
    hints=[
        "A DP over cut positions works, but a greedy is enough.",
        "Make each piece as long as possible: extend until the next letter already appears in the piece.",
        "Track the current piece's letters in a 26-bit mask; on a repeat, count a new piece and reset the mask to that letter.",
    ],
    opt=("O(n)", "O(1)", "One pass with a 26-bit mask."),
    editorial=(
        "## The one thing this teaches\n**Longest-first greedy for partitions with a hereditary "
        "rule.** If a substring has unique letters, so does every part of it. So cutting as late "
        "as possible never forces extra cuts later.\n\n"
        "## Approach\n```java\nint pieces = 1, mask = 0;\nfor (char ch : s.toCharArray()) {\n"
        "    int bit = 1 << (ch - 'a');\n    if ((mask & bit) != 0) { pieces++; mask = 0; }   // repeat: cut before ch\n"
        "    mask |= bit;\n}\nreturn pieces;\n```\n\n"
        "## Why greedy is optimal\nCompare with any valid partition. By induction, each greedy "
        "cut is at or after the other partition's corresponding cut — the greedy piece is the "
        "longest possible from the same start or a later one.\n\n"
        "## Walkthrough: abacaba\n`ab` | `ac` | `ab` | `a` — each cut happens when an `a` repeats: "
        "4 pieces."
    ),
    py='''
def solve(s):
    n = len(s)
    INF = float("inf")
    best = [0] + [INF] * n
    for end in range(1, n + 1):
        seen = set()
        for start in range(end - 1, -1, -1):
            if s[start] in seen:
                break
            seen.add(s[start])
            best[end] = min(best[end], best[start] + 1)
    return best[n]
''',
    java='''
    static int solve(String s) {
        int pieces = 1, mask = 0;
        for (int i = 0; i < s.length(); i++) {
            int bit = 1 << (s.charAt(i) - 'a');
            if ((mask & bit) != 0) { pieces++; mask = 0; }
            mask |= bit;
        }
        return pieces;
    }
''',
    examples=[("Example 1", "abacaba\n"), ("Example 2", "ssssss\n")],
    hidden=[
        ("Single letter", "a\n"),
        ("All distinct", "abcdef\n"),
        ("One repeat at the end", "abca\n"),
        ("Alphabet twice", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz\n"),
    ],
    expl=[
        "ab, ac, ab, a.",
        "Every piece is a single s.",
    ],
    prereqs=[
        ("greedy", "Making each piece as long as the rule allows."),
        ("bit_manip", "A 26-bit mask of the letters in the current piece."),
    ],
)

_p(
    "baseball-game", "Baseball Game", "Easy",
    topics=["Stacks", "Simulation"], subtopics=["Stack Simulation"], companies=["Amazon"],
    shape="ops", ret="long", todo="push numbers; '+' pushes the sum of the top two, 'D' pushes double the top, 'C' pops; answer the sum of the stack",
    description=(
        "Keep a record of scores. Each operation is one of:\n\n"
        "- an integer `x` — record `x`;\n- `+` — record the sum of the previous two scores;\n"
        "- `D` — record double the previous score;\n- `C` — remove the previous score.\n\n"
        "Every operation is valid when it is applied. Print the sum of the final record.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: one operation each.\n\n"
        "### Output\nThe total."
    ),
    constraints="1 ≤ q ≤ 1000\n-3·10^4 ≤ x ≤ 3·10^4",
    hints=[
        "Every operation refers to the most recent valid scores.",
        "\"Most recent, and removable\" is a stack.",
        "For '+', peek at the top two without removing them; the new score goes on top.",
    ],
    opt=("O(q)", "O(q)", "One push or pop per operation."),
    editorial=(
        "## The one thing this teaches\n**Recognise a stack by \"undo the latest\".** `C` cancels "
        "the most recent score, and `+` and `D` read the most recent ones. That access pattern is "
        "exactly what a stack provides.\n\n"
        "## Approach\n```java\nDeque<Long> st = new ArrayDeque<>();\nfor (String op : ops) {\n"
        "    switch (op) {\n        case \"+\": { long a = st.pop(), b = st.peek(); st.push(a); st.push(a + b); break; }\n"
        "        case \"D\": st.push(2 * st.peek()); break;\n        case \"C\": st.pop(); break;\n"
        "        default: st.push(Long.parseLong(op));\n    }\n}\nreturn sum of st;\n```\n\n"
        "## Reading the top two\n`ArrayDeque` has no \"second from the top\" accessor, so pop the "
        "top, peek at the next, and push the top back.\n\n"
        "## Walkthrough: 5 2 C D +\n`[5]` → `[5, 2]` → `[5]` → `[5, 10]` → `[5, 10, 15]`. Sum 30."
    ),
    py='''
def solve(ops):
    record = []
    for op in ops:
        token = op[0]
        if token == "+":
            record.append(record[-1] + record[-2])
        elif token == "D":
            record.append(2 * record[-1])
        elif token == "C":
            record.pop()
        else:
            record.append(int(token))
    return sum(record)
''',
    java='''
    static long solve(String[][] ops) {
        ArrayDeque<Long> st = new ArrayDeque<>();
        for (String[] line : ops) {
            String op = line[0];
            if (op.equals("+")) { long a = st.pop(), b = st.peek(); st.push(a); st.push(a + b); }
            else if (op.equals("D")) st.push(2 * st.peek());
            else if (op.equals("C")) st.pop();
            else st.push(Long.parseLong(op));
        }
        long total = 0;
        for (long v : st) total += v;
        return total;
    }
''',
    examples=[
        ("Example 1", "5\n5\n2\nC\nD\n+\n"),
        ("Example 2", "8\n5\n-2\n4\nC\nD\n9\n+\n+\n"),
        ("Example 3", "2\n1\nC\n"),
    ],
    hidden=[
        ("Single score", "1\n7\n"),
        ("Doubling chain", "4\n1\nD\nD\nD\n"),
        ("Cancel then add", "5\n10\n20\nC\n30\n+\n"),
    ],
    expl=[
        "Record 5, 2; cancel 2; double 5 to 10; 5 + 10 = 15. Total 30.",
        "The record ends as 5, −2, −4, 9, 5, 14: total 27.",
        "The only score is cancelled.",
    ],
    prereqs=[
        ("stack", "Push, pop and peek on the most recent values."),
        ("simulation", "Applying a list of operations in order."),
    ],
)

_p(
    "height-checker", "Height Checker", "Easy",
    topics=["Sorting", "Arrays"], subtopics=["Counting Sort"], companies=["Amazon"],
    shape="arr", ret="int", todo="build the expected order with a counting sort over heights 1..100 and count mismatched positions",
    description=(
        "Students should stand in non-decreasing order of height. Print how many positions hold "
        "a different height from the sorted order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` heights.\n\n"
        "### Output\nThe number of mismatched positions."
    ),
    constraints="1 ≤ n ≤ 100\n1 ≤ height ≤ 100",
    hints=[
        "Sort a copy and compare it with the original position by position.",
        "Heights are at most 100, so a counting sort is linear.",
        "Walk the counts from height 1 upward to generate the expected sequence while scanning the original.",
    ],
    opt=("O(n + H)", "O(H)", "Counting sort over H = 100 possible heights."),
    editorial=(
        "## The one thing this teaches\n**Counting sort when the value range is tiny.** With "
        "heights up to 100, counting occurrences and replaying them in order produces the sorted "
        "sequence without any comparisons.\n\n"
        "## Approach\n```java\nint[] count = new int[101];\nfor (int h : heights) count[h]++;\n"
        "int mismatches = 0, h = 1;\nfor (int i = 0; i < n; i++) {\n    while (count[h] == 0) h++;       // next height in sorted order\n"
        "    if (heights[i] != h) mismatches++;\n    count[h]--;\n}\n```\n\n"
        "## Why equal heights are not mismatches\nThe expected order is defined by height only, "
        "so two students of the same height are interchangeable.\n\n"
        "## Stable versus unstable\nWhich of two equal heights goes first does not change the "
        "count, so any sort works."
    ),
    py='''
def solve(a):
    return sum(1 for x, y in zip(a, sorted(a)) if x != y)
''',
    java='''
    static int solve(int[] heights) {
        int[] count = new int[101];
        for (int h : heights) count[h]++;
        int mismatches = 0, h = 1;
        for (int i = 0; i < heights.length; i++) {
            while (count[h] == 0) h++;
            if (heights[i] != h) mismatches++;
            count[h]--;
        }
        return mismatches;
    }
''',
    examples=[("Example 1", "6\n1 1 4 2 1 3\n"), ("Example 2", "5\n5 1 2 3 4\n"), ("Example 3", "5\n1 2 3 4 5\n")],
    hidden=[
        ("Single student", "1\n50\n"),
        ("Reverse order", "4\n4 3 2 1\n"),
        ("All equal", "3\n7 7 7\n"),
        ("Extremes", "3\n100 1 50\n"),
    ],
    expl=[
        "Sorted is 1 1 1 2 3 4; positions 2, 4 and 5 differ.",
        "Every position differs from 1 2 3 4 5.",
        "Already sorted.",
    ],
    prereqs=[
        ("sorting", "Counting sort over a small value range."),
        ("array_patterns", "Comparing two sequences position by position."),
    ],
)

_p(
    "count-good-substrings", "Substrings of Size Three with Distinct Characters", "Easy",
    topics=["Sliding Window", "Strings"], subtopics=["Fixed Window"], companies=["Amazon"],
    shape="str", ret="int", todo="for each window of length 3, check that its three letters are pairwise different",
    description=(
        "Print the number of substrings of length 3 whose three characters are all different. "
        "Occurrences at different positions count separately.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe count."
    ),
    constraints="1 ≤ |s| ≤ 10^5\nLowercase English letters",
    hints=[
        "There are |s| − 2 windows of length 3.",
        "For a window this small, three comparisons decide it: a ≠ b, b ≠ c, a ≠ c.",
        "For a general window size k, keep letter counts and the number of letters with count > 1 as the window slides.",
    ],
    opt=("O(n)", "O(1)", "Three comparisons per window."),
    editorial=(
        "## The one thing this teaches\n**A fixed-size window can be checked directly when it is "
        "tiny.** The general sliding-window machinery — counts updated on entry and exit — pays "
        "off for large k. For k = 3, three comparisons are simpler and just as fast.\n\n"
        "## Approach\n```java\nint count = 0;\nfor (int i = 0; i + 2 < n; i++) {\n"
        "    char a = s.charAt(i), b = s.charAt(i + 1), c = s.charAt(i + 2);\n"
        "    if (a != b && b != c && a != c) count++;\n}\n```\n\n"
        "## The general version\nFor window size k: add the entering letter's count, remove the "
        "leaving letter's count, and track how many letters currently appear more than once. A "
        "window is good when that number is 0.\n\n"
        "## Short strings\nWith fewer than three characters there are no windows, and the loop "
        "does not run."
    ),
    py='''
def solve(s):
    return sum(1 for i in range(len(s) - 2) if len(set(s[i:i + 3])) == 3)
''',
    java='''
    static int solve(String s) {
        int count = 0;
        for (int i = 0; i + 2 < s.length(); i++) {
            char a = s.charAt(i), b = s.charAt(i + 1), c = s.charAt(i + 2);
            if (a != b && b != c && a != c) count++;
        }
        return count;
    }
''',
    examples=[("Example 1", "xyzzaz\n"), ("Example 2", "aababcabc\n")],
    hidden=[
        ("Too short", "ab\n"),
        ("Exactly one window", "abc\n"),
        ("Repeated letter", "aaaa\n"),
        ("Every window good", "abcabcabc\n"),
    ],
    expl=[
        "Only xyz; yzz, zza and zaz repeat a letter.",
        "abc, bca, cab and abc.",
    ],
    prereqs=[
        ("sliding_window", "Fixed-size windows over a string."),
        ("string_basics", "Comparing characters at nearby positions."),
    ],
)
