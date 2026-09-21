# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 3 (Order & Search) depth: worked traces, computed rather than typed,
# and the extra Big-O drills added with them.
#
# exec'd by tools/dsa_curriculum.py after dsa_traces.py, in the same namespace.
# Every row below is produced by running the algorithm it describes, so a table
# can never disagree with the code beside it — the failure mode of hand-typed
# traces, where one arithmetic slip teaches the wrong invariant.
# ---------------------------------------------------------------------------


def _t3_fast_power():
    rows = []

    def power(b, e, depth):
        rows.append([str(len(rows) + 1), "· " * depth + f"call power({b}, {e})",
                     "base case" if e == 0 else f"needs power({b}, {e // 2})", "—"])
        if e == 0:
            rows.append([str(len(rows) + 1), "· " * depth + f"return from power({b}, 0)",
                         "—", "**1**"])
            return 1
        half = power(b, e // 2, depth + 1)
        res = half * half * (b if e % 2 else 1)
        how = f"{half}² × {b}" if e % 2 else f"{half}²"
        rows.append([str(len(rows) + 1), "· " * depth + f"return from power({b}, {e})",
                     f"e = {e} is {'odd' if e % 2 else 'even'}", f"{how} = **{res}**"])
        return res

    power(3, 13, 0)
    return _trace(
        "Fast power: power(3, 13), one call per level",
        "Each call halves the exponent and makes **one** recursive call. The odd levels "
        "multiply in one extra factor of the base.",
        ["Step", "Event", "Why", "Value"],
        rows,
        "Thirteen is 1101 in binary, and the chain of calls reads its bits: 13 → 6 → 3 → "
        "1 → 0 is five frames, ⌊log₂ 13⌋ + 2. The odd exponents (13, 3, 1) are exactly the "
        "1-bits. Calling `power(b, e/2)` twice would double the calls at every level: "
        "1 + 2 + 4 + 8 + 16 = 31 calls instead of 5.",
    )


def _t3_max_subarray_halves():
    a = [2, -5, 6, -1, 3, -7, 4, 1]
    rows = []

    def best(lo, hi):                       # [lo, hi)
        if hi - lo == 1:
            return a[lo]
        mid = (lo + hi) // 2
        left = best(lo, mid)
        right = best(mid, hi)
        s, suf = 0, float("-inf")
        for i in range(mid - 1, lo - 1, -1):
            s += a[i]
            suf = max(suf, s)
        s, pre = 0, float("-inf")
        for i in range(mid, hi):
            s += a[i]
            pre = max(pre, s)
        cross = suf + pre
        res = max(left, right, cross)
        rows.append([f"a[{lo}..{hi - 1}] = {a[lo:hi]}", str(left), str(right),
                     f"{suf} + {pre} = {cross}", f"**{res}**"])
        return res

    best(0, len(a))
    return _trace(
        "Maximum subarray by halves on [2, −5, 6, −1, 3, −7, 4, 1]",
        "Each row is one divide-and-conquer node, in the order it *returns* (children "
        "first). The crossing column is the best suffix of the left half plus the best "
        "prefix of the right — the only part of the answer neither recursive call can see.",
        ["Range", "Left best", "Right best", "Crossing (suffix + prefix)", "Node answer"],
        rows,
        "The winner, 6 − 1 + 3 = 8, lies in neither half: it straddles the midpoint between "
        "indices 3 and 4, so neither recursive call at the root can see it. Only the root's "
        "crossing term finds it — the best left suffix (6 − 1 = 5) plus the best right prefix "
        "(3). Each level does O(n) crossing work over log n levels: O(n log n).",
    )


def _t3_lomuto():
    a = [7, 2, 9, 4, 1, 8, 5]
    pivot = a[-1]
    rows = []
    p = 0
    for i in range(len(a) - 1):
        if a[i] < pivot:
            action = f"{a[i]} < {pivot}: swap a[{i}] ↔ a[{p}], p → {p + 1}"
            a[i], a[p] = a[p], a[i]
            p += 1
        else:
            action = f"{a[i]} ≥ {pivot}: leave it"
        rows.append([str(i), action, " ".join(map(str, a)), str(p)])
    a[p], a[-1] = a[-1], a[p]
    rows.append(["end", f"swap pivot into a[{p}]", " ".join(map(str, a)), f"**{p}**"])
    return _trace(
        "Lomuto partition of [7, 2, 9, 4, 1, 8, 5] around the last element, 5",
        "`p` is the boundary: `a[0..p)` holds everything found so far that is < 5. `i` "
        "scans left to right; a small element is swapped to the boundary and the boundary "
        "moves.",
        ["i", "Decision", "Array after", "p"],
        rows,
        "The pivot lands at index 3 and never moves again: three smaller values to its left, "
        "three larger to its right, neither side sorted. Quickselect asking for index 3 stops "
        "here; asking for index 5 throws away `2 4 1 5` and partitions only `9 8 7`.",
    )


def _t3_radix():
    a = [512, 38, 207, 91, 450, 26, 873]
    rows = [["start", "—", " ".join(f"{x:03d}" for x in a)]]
    for d, name in ((1, "ones"), (10, "tens"), (100, "hundreds")):
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // d) % 10].append(x)
        a = [x for b in buckets for x in b]
        rows.append([name, "stable by digit", " ".join(f"{x:03d}" for x in a)])
    return _trace(
        "LSD radix sort, base 10: [512, 38, 207, 91, 450, 26, 873]",
        "Three stable passes, least significant digit first. Each pass looks at one digit "
        "only, and keeps equal digits in the order the previous pass left them.",
        ["Pass", "Rule", "Order after the pass (zero-padded)"],
        rows,
        "After the tens pass, the last two digits read 07, 12, 26, 38, 50, 73, 91 — in order. "
        "The hundreds pass then moves 026, 038 and 091 (all hundreds digit 0) to the front "
        "and, being stable, keeps them in exactly that order. An unstable pass could emit 091 "
        "before 026 and undo both earlier passes. Three passes of O(n + 10), and not one "
        "comparison between two numbers.",
    )


def _t3_max_min_distance():
    pos = [1, 4, 9, 12, 17, 20]
    k = 3

    def ok(d):
        placed, last = 1, pos[0]
        for x in pos[1:]:
            if x - last >= d:
                placed, last = placed + 1, x
        return placed >= k

    rows = []
    lo, hi = 1, pos[-1] - pos[0]
    while lo < hi:
        mid = lo + (hi - lo + 1) // 2
        good = ok(mid)
        rows.append([f"[{lo}, {hi}]", str(mid), "**yes**" if good else "no",
                     f"lo = {mid}" if good else f"hi = {mid - 1}"])
        if good:
            lo = mid
        else:
            hi = mid - 1
    rows.append([f"[{lo}, {hi}]", "—", "—", f"return **{lo}**"])
    return _trace(
        "Maximise the minimum gap: 3 balls at positions [1, 4, 9, 12, 17, 20]",
        "`ok(d)` places balls greedily left to right, each at the first position ≥ d past "
        "the previous one, and asks whether 3 fit. Larger d is harder, so the predicate reads "
        "`yes … yes no … no` — and we want the **last** yes. The midpoint rounds up.",
        ["[lo, hi]", "mid (rounded up)", "3 balls fit?", "New range"],
        rows,
        "Balls at 1, 9 and 17 give gaps 8 and 8. At d = 9 the second ball must wait until 12, "
        "and the third would need 21. Had `mid` rounded down, the range [8, 9] would compute "
        "mid = 8, succeed, set lo = 8 — and never move again.",
    )


def _t3_rotated_min():
    a = [15, 18, 22, 3, 6, 9, 12]
    rows = []
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] > a[hi]:
            rows.append([f"[{lo}, {hi}]", f"{mid} → {a[mid]}", str(a[hi]),
                         f"{a[mid]} > {a[hi]}: the drop is right of mid", f"lo = {mid + 1}"])
            lo = mid + 1
        else:
            rows.append([f"[{lo}, {hi}]", f"{mid} → {a[mid]}", str(a[hi]),
                         f"{a[mid]} ≤ {a[hi]}: mid..hi is sorted", f"hi = {mid}"])
            hi = mid
    rows.append([f"[{lo}, {hi}]", "—", "—", "—", f"return a[{lo}] = **{a[lo]}**"])
    return _trace(
        "Minimum of a rotated array: [15, 18, 22, 3, 6, 9, 12]",
        "A **closed** range, because `a[hi]` is read. The comparison is not against a target "
        "but against the right end, which tells you on which side of `mid` the drop lies.",
        ["[lo, hi]", "mid → a[mid]", "a[hi]", "Reasoning", "New range"],
        rows,
        "No target, and the array is not sorted — but the question “is the drop to my right?” "
        "is monotone along the array, and that is all binary search needs. Comparing with "
        "`a[lo]` instead fails on an unrotated array, where `a[mid] > a[lo]` and the minimum "
        "is at the far left.",
    )


def _t3_jump_game_ii():
    a = [2, 3, 1, 1, 4, 1, 2, 1]
    rows = []
    jumps = cur_end = far = 0
    for i in range(len(a) - 1):
        far = max(far, i + a[i])
        note = "—"
        if i == cur_end:
            jumps += 1
            cur_end = far
            note = f"window exhausted: jump **#{jumps}**, new window ends at {cur_end}"
        rows.append([str(i), str(a[i]), str(far), str(cur_end), note])
    return _trace(
        "Jump game II on [2, 3, 1, 1, 4, 1, 2, 1]",
        "Think of BFS levels: every index reachable with j jumps forms a window, and the next "
        "window ends at the furthest point any of them reaches. A jump is counted only when "
        "the scan reaches the end of the current window.",
        ["i", "a[i]", "furthest", "window end", "Event"],
        rows,
        "Three jumps: 0 → 1 → 4 → 7. The loop stops at index n − 2, because standing on the "
        "last index needs no further jump — running to n − 1 would count a phantom jump "
        "whenever the last window ends exactly there.",
    )


def _t3_gas_station():
    gas = [3, 1, 2, 5, 4]
    cost = [4, 2, 1, 3, 3]
    rows = []
    total = tank = start = 0
    for i in range(len(gas)):
        d = gas[i] - cost[i]
        total += d
        tank += d
        if tank < 0:
            rows.append([str(i), f"{gas[i]} − {cost[i]} = {d}", str(tank), str(total),
                         f"dry: every start in {start}..{i} fails → start = {i + 1}"])
            start, tank = i + 1, 0
        else:
            rows.append([str(i), f"{gas[i]} − {cost[i]} = {d}", str(tank), str(total), "—"])
    rows.append(["end", "—", "—", str(total),
                 f"total ≥ 0, so start **{start}** works" if total >= 0 else "total < 0: **−1**"])
    return _trace(
        "Gas station: gas [3, 1, 2, 5, 4], cost [4, 2, 1, 3, 3]",
        "One pass. `tank` is the fuel since the current candidate start; when it goes "
        "negative, the candidate and everything since it is ruled out at once.",
        ["i", "gain", "tank", "total", "Event"],
        rows,
        "Two resets retire stations 0 and 1 without ever simulating a lap from them. The "
        "global total (+2) proves a valid start exists, and the last candidate standing is "
        "it: from 2, the tank reads 1, 3, 4, 3, 2 around the loop and never dips below zero.",
    )


def _t3_room_sweep():
    iv = [(1, 4), (2, 6), (3, 7), (4, 8), (6, 9), (7, 10)]
    ev = sorted([(s, +1) for s, _ in iv] + [(e, -1) for _, e in iv])
    rows = []
    cur = peak = 0
    for t, dlt in ev:
        cur += dlt
        peak = max(peak, cur)
        rows.append([str(t), "end −1" if dlt < 0 else "start +1", str(cur), str(peak)])
    return _trace(
        "Minimum rooms by a ±1 sweep: [1,4) [2,6) [3,7) [4,8) [6,9) [7,10)",
        "Twelve events sorted by time; at equal times the −1 sorts first (−1 < +1), so a "
        "room freed at 4 is reusable by a meeting starting at 4.",
        ["time", "event", "rooms in use", "peak"],
        rows,
        "Three rooms suffice. Now flip the tie rule: at time 4, [4,8) would be counted before "
        "[1,4) is released, the count would briefly read 4, and the answer would claim four "
        "rooms for a schedule that fits in three. Every peak-concurrency bug with "
        "back-to-back bookings is that one tie.",
    )


def _t3_weighted_intervals():
    import bisect
    iv = sorted([(1, 4, 5), (3, 6, 6), (5, 8, 5), (2, 10, 15), (7, 11, 4), (9, 12, 3)],
                key=lambda x: x[1])
    ends = [e for _, e, _ in iv]
    best = [0]
    rows = []
    for i, (s, e, w) in enumerate(iv, 1):
        j = bisect.bisect_right(ends, s)
        take = best[j] + w
        skip = best[i - 1]
        best.append(max(take, skip))
        rows.append([f"[{s}, {e}) w={w}", str(j), f"best[{j}] + {w} = {take}",
                     f"best[{i - 1}] = {skip}", f"**{best[-1]}**"])
    return _trace(
        "Weighted interval scheduling, sorted by end",
        "`best[i]` is the most weight using only the first i intervals. `p` counts the "
        "intervals ending at or before this one's start — one binary search over the "
        "sorted ends — and they are exactly the ones compatible with taking it.",
        ["Interval", "p = # ends ≤ start", "Take it", "Skip it", "best[i]"],
        rows,
        "The answer is 15: [2,10) alone. Greedy by end time keeps [1,4), [5,8) and [9,12) — "
        "three intervals, the most of any selection, but worth only 13. Maximising the "
        "*count* and maximising the *weight* are different problems. The sort and the binary "
        "search are the same as always; only the choice became a `max`.",
    )


def _t3_hanoi():
    rows = []

    def hanoi(n, fr, to, via, depth):
        if n == 0:
            return
        hanoi(n - 1, fr, via, to, depth + 1)
        rows.append([str(len(rows) + 1), "· " * depth + f"hanoi({n}, {fr}→{to})",
                     f"disk {n}: {fr} → {to}"])
        hanoi(n - 1, via, to, fr, depth + 1)

    hanoi(3, "A", "C", "B", 0)
    return _trace(
        "Tower of Hanoi, n = 3: which call prints each move",
        "Each row is one printed move, tagged with the call that printed it; the dots are "
        "that call's depth. A call prints only *between* its two recursive calls.",
        ["#", "Printed by", "Disk and pegs"],
        rows,
        "Seven moves, 2³ − 1. Disk 3 moves exactly once, in the middle, printed by the root; "
        "disk 1 moves on every odd step. Read it as the promise, not the trace: move 2 disks "
        "out of the way, move disk 3, move 2 disks back on top. No memo can shorten this — "
        "the output itself is exponential.",
    )


def _t3_three_way():
    a = [4, 9, 4, 1, 7, 4, 2]
    p = 4
    lt, i, gt = 0, 0, len(a) - 1
    rows = []
    while i <= gt:
        x = a[i]
        if x < p:
            a[lt], a[i] = a[i], a[lt]
            act = f"{x} < 4: swap into the < region, lt++ i++"
            lt += 1
            i += 1
        elif x > p:
            a[i], a[gt] = a[gt], a[i]
            act = f"{x} > 4: swap with a[{gt}], gt-- (i stays)"
            gt -= 1
        else:
            act = f"{x} = 4: i++"
            i += 1
        rows.append([act, " ".join(map(str, a)), str(lt), str(i), str(gt)])
    return _trace(
        "Three-way partition of [4, 9, 4, 1, 7, 4, 2] around 4",
        "Four regions: `[0, lt)` < 4, `[lt, i)` = 4, `[i, gt]` unexamined, `(gt, end]` > 4. "
        "The loop ends when the unexamined region is empty.",
        ["Decision", "Array after", "lt", "i", "gt"],
        rows,
        "All three 4s end up together in the middle, `[lt, i)`, and quicksort never touches "
        "them again. Watch the rows where a large value is swapped in from `gt`: `i` does not "
        "move, because the value that arrives there has not been looked at.",
    )


def _t3_lower_bound_dups():
    a = [2, 4, 4, 4, 4, 7, 9]
    x = 4
    lo, hi = 0, len(a)
    rows = []
    while lo < hi:
        mid = lo + (hi - lo) // 2
        small = a[mid] < x
        rows.append([f"[{lo}, {hi})", str(mid), str(a[mid]), "**yes**" if small else "no",
                     f"lo = {mid + 1}" if small else f"hi = {mid}"])
        if small:
            lo = mid + 1
        else:
            hi = mid
    rows.append([f"[{lo}, {hi})", "—", "—", "—", f"return **{lo}**"])
    return _trace(
        "Lower bound over duplicates: the first 4 in [2, 4, 4, 4, 4, 7, 9]",
        "The first probe lands on a 4 — in the middle of the run. A search with an equality "
        "branch would stop there; lower bound treats `=` like `>` and keeps going left.",
        ["[lo, hi)", "mid", "a[mid]", "a[mid] < 4 ?", "New range"],
        rows,
        "The answer is index 1, the *first* 4, although the first probe found the one at "
        "index 3. “Equal” shrinks `hi` because an equal element *might* be the answer but "
        "something earlier might be too. Upper bound (`<=`) would return 5, and 5 − 1 = 4 "
        "copies.",
    )


def _t3_candy():
    r = [1, 3, 4, 5, 2]
    n = len(r)
    left = [1] * n
    for i in range(1, n):
        if r[i] > r[i - 1]:
            left[i] = left[i - 1] + 1
    right = [1] * n
    for i in range(n - 2, -1, -1):
        if r[i] > r[i + 1]:
            right[i] = right[i + 1] + 1
    rows = [[str(i), str(r[i]), str(left[i]), str(right[i]), f"**{max(left[i], right[i])}**"]
            for i in range(n)]
    rows.append(["total", "—", str(sum(left)), str(sum(right)),
                 f"**{sum(max(x, y) for x, y in zip(left, right))}**"])
    return _trace(
        "Candy, two passes: ratings [1, 3, 4, 5, 2]",
        "Every child gets at least 1, and more than any neighbour with a lower rating. The "
        "left pass satisfies left neighbours only, the right pass right neighbours only.",
        ["i", "rating", "left pass", "right pass", "max"],
        rows,
        "Child 3 (rating 5) needs 4 because of its left side and only 2 because of its right. "
        "The `max` keeps both constraints: 11 candies. A single pass — or a second pass that "
        "overwrites instead of taking the max — gives 9 and leaves child 3 with fewer than "
        "child 2.",
    )


def _t3_insert_interval():
    iv = [(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)]
    ns, ne = 4, 9
    rows = []
    i, n = 0, len(iv)
    out = []
    while i < n and iv[i][1] < ns:
        out.append(iv[i])
        rows.append(["1 — before", f"[{iv[i][0]}, {iv[i][1]}]", f"ends at {iv[i][1]} < 4: copy",
                     f"[{ns}, {ne}]"])
        i += 1
    while i < n and iv[i][0] <= ne:
        ns, ne = min(ns, iv[i][0]), max(ne, iv[i][1])
        rows.append(["2 — overlap", f"[{iv[i][0]}, {iv[i][1]}]", "overlaps: absorb",
                     f"[{ns}, {ne}]"])
        i += 1
    out.append((ns, ne))
    rows.append(["", "—", "emit the grown interval", f"**[{ns}, {ne}]**"])
    while i < n:
        out.append(iv[i])
        rows.append(["3 — after", f"[{iv[i][0]}, {iv[i][1]}]", "starts after the new end: copy",
                     f"[{ns}, {ne}]"])
        i += 1
    return _trace(
        "Insert [4, 9] into [1,2] [3,5] [6,7] [8,10] [12,16]",
        "The list is already sorted and disjoint, so it splits into three runs: entirely "
        "before the new interval, touching it, entirely after. One loop each.",
        ["Phase", "Interval", "Decision", "New interval so far"],
        rows,
        "Three intervals collapse into [3, 10] — `min` on the start (3 < 4) and `max` on the "
        "end (10 > 9). Every interval is read once and nothing is sorted: O(n). Written as a "
        "single loop with flags, this is where people lose an hour.",
    )


def _attach_s3_traces():
    by_key = {u["key"]: u for u in _UNITS}
    for key, traces in {
        "recursion": [_t3_fast_power(), _t3_max_subarray_halves(), _t3_hanoi()],
        "sorting": [_t3_lomuto(), _t3_three_way(), _t3_radix()],
        "binary-search": [_t3_lower_bound_dups(), _t3_max_min_distance(), _t3_rotated_min()],
        "greedy": [_t3_jump_game_ii(), _t3_gas_station(), _t3_candy()],
        "intervals": [_t3_insert_interval(), _t3_room_sweep(), _t3_weighted_intervals()],
    }.items():
        by_key[key]["traces"].extend(traces)


_attach_s3_traces()


# ---------------------------------------------------------------------------
# Big-O drills. Each unit already carries five in dsa_bigo.py; these add the
# shapes the expanded units now teach — the Master theorem's three cases, the
# degenerate pivots, search over a value space, exchange sorts and weighted DP.
# ---------------------------------------------------------------------------

_BIGO_S3 = {
    "recursion": [
        _bigo(r"""
void f(int n) {
    if (n <= 1) return;
    for (int i = 0; i < n; i++) work();       // O(1) each
    f(n / 2); f(n / 2); f(n / 2); f(n / 2);
}
""", "O(n²)", ["O(n log n)", "O(n²)", "O(n² log n)", "O(4ⁿ)"],
            "`T(n) = 4T(n/2) + n`. Level k has 4ᵏ calls of size n/2ᵏ, so it does 2ᵏ·n work — "
            "the levels *grow* going down, and the leaves win: n^(log₂4) = n². Merge sort's "
            "levels tie because it makes 2 calls, not 4."),
        _bigo(r"""
void f(int n) {
    if (n <= 1) return;
    for (int i = 0; i < n; i++) work();       // O(1) each
    f(n / 2);
}
""", "O(n)", ["O(log n)", "O(n)", "O(n log n)", "O(n²)"],
            "`T(n) = T(n/2) + n` = n + n/2 + n/4 + … < 2n. One call per level means the work "
            "shrinks geometrically, and the root's loop dominates. This is quickselect's "
            "expected-case shape."),
        _bigo(r"""
String rev(String s) {
    if (s.isEmpty()) return s;
    return rev(s.substring(1)) + s.charAt(0);   // s has length n
}
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
            "n levels, and each copies a substring and builds a new string of up to n "
            "characters: 1 + 2 + … + n. The recursion looks linear; the copying is quadratic. "
            "A `char[]` swapped from both ends is O(n)."),
    ],
    "sorting": [
        _bigo(r"""
// a is ALREADY SORTED; the pivot is always a[hi]
int kth(int[] a, int lo, int hi, int k) {
    int p = lomutoPartition(a, lo, hi);        // O(hi - lo)
    if (p == k) return a[p];
    return p < k ? kth(a, p + 1, hi, k) : kth(a, lo, p - 1, k);
}
// called as kth(a, 0, n - 1, 0)
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "On sorted input the last element is the maximum, so each partition places it at "
            "`hi` and removes only one element: n + (n−1) + … = O(n²). A random pivot restores "
            "the O(n) expectation."),
        _bigo(r"""
int[] buf = new int[n];                     // n non-negative ints
for (int shift = 0; shift < 32; shift += 8) {
    int[] cnt = new int[257];
    for (int x : a) cnt[((x >>> shift) & 255) + 1]++;
    for (int d = 0; d < 256; d++) cnt[d + 1] += cnt[d];
    for (int x : a) buf[cnt[(x >>> shift) & 255]++] = x;
    int[] t = a; a = buf; buf = t;
}
""", "O(n)", ["O(n)", "O(n log n)", "O(32·n log n)", "O(n²)"],
            "Four passes, each O(n + 256). The number of passes depends on the key *width*, not "
            "on n, so it is O(n) — which is how radix sort sidesteps the n log n bound: it "
            "never compares two elements."),
        _bigo(r"""
// Lomuto quicksort; every element of a is EQUAL
void qs(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int p = lomutoPartition(a, lo, hi);      // "< pivot" goes left
    qs(a, lo, p - 1); qs(a, p + 1, hi);
}
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(n³)"],
            "No element is `< pivot`, so the pivot always lands at `lo` and the right side has "
            "n − 1 elements. Duplicates degrade a two-way partition to the sorted-input worst "
            "case; a three-way partition puts every equal value in the middle and finishes in "
            "one O(n) pass."),
    ],
    "binary-search": [
        _bigo(r"""
long lo = 1, hi = (long) n * m;              // k-th smallest in an n × m table
while (lo < hi) {
    long mid = lo + (hi - lo) / 2, cnt = 0;
    for (int i = 1; i <= n; i++) cnt += Math.min(m, mid / i);
    if (cnt >= k) hi = mid; else lo = mid + 1;
}
""", "O(n log(n·m))", ["O(n·m)", "O(n log(n·m))", "O(n·m log(n·m))", "O(log(n·m))"],
            "log₂(n·m) probes, each counting with one division per row. The table itself — "
            "n·m entries — is never built, which is the entire point when n·m is 10¹⁰."),
        _bigo(r"""
double lo = 0, hi = 1e9;
for (int it = 0; it < 100; it++) {           // fixed iteration count
    double mid = (lo + hi) / 2;
    if (check(a, mid)) hi = mid; else lo = mid; // check is O(n)
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(100ⁿ)"],
            "100 is a constant, so this is 100·n = O(n). The precision is fixed by the "
            "iteration count, not by n — which is exactly why a fixed count is safer than an "
            "epsilon test."),
        _bigo(r"""
// rotated sorted array WITH duplicates, e.g. [2,2,2,...,2,0,2,2]
int lo = 0, hi = n - 1;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] > a[hi]) lo = mid + 1;
    else if (a[mid] < a[hi]) hi = mid;
    else hi--;                                // cannot tell which side
}
""", "O(n)", ["O(log n)", "O(√n)", "O(n)", "O(n log n)"],
            "When `a[mid] == a[hi]` the comparison is uninformative and the range shrinks by one. "
            "On an array of equal values with one dip, that happens almost every step. No "
            "algorithm can do better in the worst case — the dip could be anywhere, and only "
            "reading it finds it."),
    ],
    "greedy": [
        _bigo(r"""
Integer[] idx = new Integer[n];
for (int i = 0; i < n; i++) idx[i] = i;
Arrays.sort(idx, (x, y) -> Long.compare((long) t[x] * w[y], (long) t[y] * w[x]));
long time = 0, cost = 0;
for (int j : idx) { time += t[j]; cost += (long) w[j] * time; }
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(n!)"],
            "The exchange argument replaces the search over n! orders by one comparator sort. "
            "The pass afterwards is O(n)."),
        _bigo(r"""
// n jobs sorted by profit desc; each takes the latest free slot <= its deadline
boolean[] used = new boolean[D + 1];         // D = the largest deadline
for (int[] j : jobs)
    for (int s = j[0]; s >= 1; s--)
        if (!used[s]) { used[s] = true; total += j[1]; break; }
""", "O(n·D)", ["O(n log n)", "O(n·D)", "O(D log D)", "O(n²·D)"],
            "A backwards scan of up to D slots per job (the sort before it, O(n log n), is "
            "dominated). With n and D both 10⁵ that is 10¹⁰; a union-find mapping each slot to "
            "the latest free one at or before it makes each lookup near O(1)."),
        _bigo(r"""
int[] c = new int[n];
Arrays.fill(c, 1);
for (int i = 1; i < n; i++)      if (r[i] > r[i - 1]) c[i] = c[i - 1] + 1;
for (int i = n - 2; i >= 0; i--) if (r[i] > r[i + 1]) c[i] = Math.max(c[i], c[i + 1] + 1);
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "Two linear passes: one satisfies every left-neighbour constraint, the other every "
            "right one, and `max` keeps both. The O(n²) alternative — repeat a single pass until "
            "nothing changes — does the same work up to n times."),
    ],
    "intervals": [
        _bigo(r"""
// iv sorted by end; ends[] = their ends
for (int i = 1; i <= n; i++) {
    int j = upperBound(ends, iv[i - 1][0]);   // binary search
    best[i] = Math.max(best[i - 1], best[j] + iv[i - 1][2]);
}
""", "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
            "One binary search per interval, on top of the O(n log n) sort. Trying every "
            "subset would be O(2ⁿ); the sorted ends are what make the predecessor a search "
            "instead of a scan."),
        _bigo(r"""
// the same DP, finding the predecessor by scanning back
for (int i = 1; i <= n; i++) {
    int j = i - 1;
    while (j > 0 && iv[j - 1][1] > iv[i - 1][0]) j--;
    best[i] = Math.max(best[i - 1], best[j] + iv[i - 1][2]);
}
""", "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(n³)"],
            "The scan can walk back over every earlier interval — for example when all of them "
            "overlap the current one. Correct, and quadratic; the ends are sorted, so the scan "
            "should be a binary search."),
        _bigo(r"""
TreeMap<Integer, Integer> cal = new TreeMap<>();   // start -> end
for (int[] b : bookings) {                         // q bookings
    Map.Entry<Integer, Integer> lo = cal.floorEntry(b[0]), hi = cal.ceilingEntry(b[0]);
    if ((lo == null || lo.getValue() <= b[0]) && (hi == null || hi.getKey() >= b[1]))
        cal.put(b[0], b[1]);
}
""", "O(q log q)", ["O(q)", "O(q log q)", "O(q²)", "O(q² log q)"],
            "Each booking does two neighbour lookups and at most one insert in a balanced tree "
            "holding at most q entries: O(log q) each. Checking every existing booking instead "
            "is O(q²)."),
    ],
}


def _attach_s3_bigo():
    by_key = {u["key"]: u for u in _UNITS}
    for key, items in _BIGO_S3.items():
        by_key[key]["bigo"].extend(items)


_attach_s3_bigo()
