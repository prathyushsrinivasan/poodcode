# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Worked traces for the units that had none.
#
# exec'd by tools/dsa_curriculum.py after dsa_bigo.py, in the same namespace,
# so `_trace` and `_UNITS` are already defined. Each unit key below gets its
# traces appended.
#
# THE ROWS ARE COMPUTED, NOT TYPED
#
# The traces in the stage files were written out by hand, which is fine for a
# dozen tables and a liability for thirty: one mistyped pointer position and the
# table teaches the bug. Every trace here is produced by running the algorithm
# on the example and recording its state at each step, so a row cannot disagree
# with the code it claims to show. Only the prose — title, intro, takeaway — is
# authored, and the takeaways state facts the generated rows make checkable.
#
# Java semantics are simulated where they differ from Python's (integer
# division truncates toward zero, `int` wraps at 32 bits), because the Java
# behaviour is the thing being taught.
# ---------------------------------------------------------------------------

from collections import deque as _deque


def _fmt_list(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _code(s):
    return f"`{s}`"


# -- Java integer semantics -------------------------------------------------

def _jdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _jmod(a, b):
    return a - _jdiv(a, b) * b


def _wrap32(x):
    x &= 0xFFFFFFFF
    return x - (1 << 32) if x >= (1 << 31) else x


# ---------------------------------------------------------------- stage 1

def _t_io():
    big = 46341
    rows = [
        [_code("7 / 2"), "int", str(_jdiv(7, 2)), "Both operands are `int`, so the fraction is discarded."],
        [_code("-7 / 2"), "int", str(_jdiv(-7, 2)), "Truncates toward **zero**, not down — Python's `//` would give −4."],
        [_code("-7 % 2"), "int", str(_jmod(-7, 2)), "The remainder takes the sign of the dividend."],
        [_code("Math.floorMod(-7, 2)"), "int", str((-7) % 2), "Always in `[0, 2)` — what you want for wrapping indices."],
        [_code("7 / 2 * 2.0"), "double", f"{_jdiv(7, 2) * 2.0}", "`7 / 2` is evaluated first, as `int`, and has already lost the half."],
        [_code("7 / 2.0 * 2"), "double", f"{7 / 2.0 * 2}", "One `double` operand makes the division exact."],
        [_code(f"{big} * {big}"), "int", str(_wrap32(big * big)), "The true value is 2 147 488 281, past `Integer.MAX_VALUE`; it wraps silently."],
        [_code(f"(long) {big} * {big}"), "long", str(big * big), "The cast applies to the left operand *before* multiplying."],
        [_code(f"(long) ({big} * {big})"), "long", str(_wrap32(big * big)), "The cast applies *after* an `int` multiply that already overflowed."],
    ]
    return _trace(
        "What Java actually computes",
        "Arithmetic has no loop to step through, but it does have state: the *type* of each "
        "intermediate result. Read the expression, predict the value, then check the row.",
        ["Expression", "Type", "Value", "Why"],
        rows,
        "Every wrong row in a first submission is one of three things: integer division that "
        "happened earlier than you thought, a negative remainder, or an `int` that overflowed "
        "before it was widened. The fix is always to decide the type *before* the operation.",
    )


def _t_branching():
    def right(n):
        if n % 15 == 0:
            return "FizzBuzz"
        if n % 3 == 0:
            return "Fizz"
        if n % 5 == 0:
            return "Buzz"
        return str(n)

    def wrong(n):
        if n % 3 == 0:
            return "Fizz"
        if n % 5 == 0:
            return "Buzz"
        if n % 15 == 0:
            return "FizzBuzz"
        return str(n)

    rows = []
    for n in (3, 5, 7, 9, 10, 15, 30):
        yn = lambda b: "yes" if b else "no"
        r, w = right(n), wrong(n)
        rows.append([str(n), yn(n % 3 == 0), yn(n % 5 == 0), r,
                     w if w == r else f"**{w}**"])
    return _trace(
        "Order matters in an else-if chain: FizzBuzz, two ways",
        "Both chains test the same three conditions. The left one checks `% 15` first; the "
        "right one checks it last. The chain stops at the first true branch.",
        ["n", "n % 3 == 0", "n % 5 == 0", "15 first", "15 last"],
        rows,
        "The chains agree on every row except the ones divisible by 15, where the `% 3` branch "
        "fires first and the `% 15` branch is unreachable. When conditions overlap, the most "
        "specific one goes first — and a branch that can never run is a bug even if it compiles.",
    )


def _t_digits():
    n = 4705
    rows = []
    rev = 0
    step = 0
    while n > 0:
        step += 1
        d = n % 10
        new_rev = rev * 10 + d
        rows.append([str(step), str(n), str(d), f"{rev} × 10 + {d} = {new_rev}", str(n // 10)])
        rev = new_rev
        n //= 10
    rows.append(["end", "0", "—", f"**{rev}**", "—"])
    return _trace(
        "Reversing the digits of 4705",
        "`n % 10` peels off the last digit and `n / 10` drops it. `rev * 10 + d` appends that "
        "digit to the right of `rev`.",
        ["Step", "n", "d = n % 10", "rev", "n / 10"],
        rows,
        "Four iterations for four digits — the loop runs once per digit, which is why this is "
        "O(log n). The leading `5` of 4705 becomes the trailing digit of 5074, and the internal "
        "`0` survives because `rev * 10` shifts it into place. A *trailing* zero would vanish: "
        "reversing 4700 gives 74.",
    )


def _t_arrays():
    prices = [7, 1, 5, 3, 6, 4]
    lo = None
    best = 0
    rows = []
    for i, p in enumerate(prices):
        if lo is None or p < lo:
            lo, note = p, "new minimum — a better day to buy"
            profit = 0
        else:
            profit = p - lo
            note = "sell here?"
        if profit > best:
            best = profit
            note = "**new best**"
        rows.append([str(i), str(p), str(lo), str(profit), str(best), note])
    return _trace(
        "Best single buy/sell, one pass: prices [7, 1, 5, 3, 6, 4]",
        "Carry two numbers: the cheapest price seen so far, and the best profit seen so far. "
        "Selling on day i is only ever worth doing against the cheapest earlier day.",
        ["Day", "Price", "Min so far", "Profit if sold today", "Best", "Note"],
        rows,
        "The answer is 5 — buy at 1, sell at 6 — found without comparing any pair of days. "
        "Checking every pair is O(n²); carrying the minimum is O(n), because the only earlier "
        "day that matters is the cheapest one.",
    )


# ---------------------------------------------------------------- stage 2

def _sci(x):
    if x < 10 ** 7:
        return f"{x:,}".replace(",", " ")
    e = len(str(x)) - 1
    return f"≈ 10^{e}"


def _t_complexity():
    import math
    rows = []
    for n in (10, 20, 1000, 10 ** 5, 10 ** 6):
        lg = max(1, round(math.log2(n)))
        two = 2 ** n if n <= 20 else None
        two_s = _sci(two) if two is not None else f"≈ 10^{int(n * math.log10(2))}"
        rows.append([_sci(n), str(lg), _sci(n * lg), _sci(n * n), two_s])
    return _trace(
        "How the classes grow: steps for each input size",
        "Rough operation counts, with a budget of about 10⁸ simple steps per second as the "
        "yardstick. Read down a column to see where each class stops being feasible.",
        ["n", "log₂ n", "n log₂ n", "n²", "2ⁿ"],
        rows,
        "At n = 20, 2ⁿ is a million — fine. At n = 10⁵, n² is 10¹⁰ — a hundred seconds — while "
        "n log n is under 2·10⁶. That is why constraints are a hint: n ≤ 20 invites exponential "
        "search, n ≤ 10⁵ demands n log n or better, and n ≤ 10⁶ wants linear.",
    )


def _t_hashing():
    nums, target = [3, 8, 11, 4, 7], 15
    seen = {}
    rows = []
    for i, x in enumerate(nums):
        need = target - x
        hit = need in seen
        state = "{" + ", ".join(f"{k}→{v}" for k, v in seen.items()) + "}"
        if hit:
            rows.append([str(i), str(x), str(need), state, f"**yes, at {seen[need]}** → return [{seen[need]}, {i}]"])
            break
        rows.append([str(i), str(x), str(need), state, "no — store " + f"{x}→{i}"])
        seen[x] = i
    return _trace(
        "Two-sum with a map: nums [3, 8, 11, 4, 7], target 15",
        "For each value, ask the map whether its partner `target − x` has already been seen, "
        "*then* add the value. The map holds value → index.",
        ["i", "x", "need", "Map before the lookup", "Found?"],
        rows,
        "Four lookups, and the pair (11, 4) is found at the moment its second half arrives. "
        "Checking before inserting is what stops a value pairing with itself — with target 8, "
        "x = 4 must not find its own entry.",
    )


def _t_two_pointers():
    a, target = [1, 2, 4, 7, 11, 15], 15
    l, r = 0, len(a) - 1
    rows = []
    while l < r:
        s = a[l] + a[r]
        if s == target:
            rows.append([str(l), str(r), f"{a[l]} + {a[r]} = {s}", "**equal**", "return"])
            break
        if s < target:
            rows.append([str(l), str(r), f"{a[l]} + {a[r]} = {s}", "too small", "l++ — a[l] is too small even for the largest partner"])
            l += 1
        else:
            rows.append([str(l), str(r), f"{a[l]} + {a[r]} = {s}", "too big", "r-- — a[r] is too big even for the smallest partner"])
            r -= 1
    return _trace(
        "Pair with a target sum in a sorted array: [1, 2, 4, 7, 11, 15], target 15",
        "`l` starts at the smallest value and `r` at the largest. Each comparison rules out one "
        "value entirely — which is the whole argument for why it is correct.",
        ["l", "r", "a[l] + a[r]", "vs 15", "Move"],
        rows,
        "Four comparisons instead of the fifteen pairs. When the sum is too big, `a[r]` cannot "
        "pair with *anything* still in range, because `a[l]` is the smallest remaining — so "
        "discarding it loses nothing.",
    )


def _t_sliding_window():
    a, S = [2, 3, 1, 2, 4, 3], 7
    left = 0
    window = 0
    best = None
    rows = []
    for r in range(len(a)):
        window += a[r]
        rows.append([f"add a[{r}] = {a[r]}", f"[{left}, {r}]", str(window), "no" if window < S else "yes", "—" if best is None else str(best)])
        while window >= S:
            length = r - left + 1
            best = length if best is None else min(best, length)
            window -= a[left]
            left += 1
            rows.append([f"drop a[{left - 1}] = {a[left - 1]}", f"[{left}, {r}]" if left <= r else "empty", str(window), "no" if window < S else "yes", f"**{best}**"])
    return _trace(
        "Shortest subarray with sum ≥ 7: [2, 3, 1, 2, 4, 3]",
        "Grow the window on the right until it is valid, then shrink from the left while it "
        "stays valid, recording the length each time it is. `left` never moves back.",
        ["Step", "Window", "Sum", "≥ 7?", "Best length"],
        rows,
        "The answer is 2 — the window `[4, 3]`. Count the moves: `right` advances 6 times and "
        "`left` at most 6 times, so the nested `while` is linear in total. Every valid window "
        "is shrunk as far as it will go before `right` moves on, which is why no shorter one "
        "can be missed.",
    )


def _t_prefix_sums():
    a, k = [1, 2, 1, 2, 1], 3
    seen = {0: 1}
    run = 0
    count = 0
    rows = []
    for i, x in enumerate(a):
        run += x
        add = seen.get(run - k, 0)
        count += add
        before = "{" + ", ".join(f"{p}:{c}" for p, c in sorted(seen.items())) + "}"
        seen[run] = seen.get(run, 0) + 1
        rows.append([str(i), str(x), str(run), str(run - k), before, f"+{add}" if add else "+0", str(count)])
    return _trace(
        "Count subarrays summing to 3: [1, 2, 1, 2, 1]",
        "`run` is the prefix sum up to i. A subarray ending at i sums to k exactly when some "
        "earlier prefix equals `run − k`, so the map counts how many times each prefix has "
        "occurred. It starts holding `{0: 1}` — the empty prefix.",
        ["i", "x", "run", "run − 3", "Prefix counts before", "Added", "Count"],
        rows,
        "Four subarrays: `[1, 2]`, `[2, 1]`, `[1, 2]`, `[2, 1]`. The `{0: 1}` seed is what "
        "counts a subarray that starts at index 0 — leave it out and the first `[1, 2]` is "
        "missed.",
    )


def _t_strings():
    s = "aaabccdddd"
    out = ""
    i = 0
    rows = []
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        piece = s[i] + (str(j - i) if j - i > 1 else "")
        out += piece
        rows.append([f"[{i}, {j})", s[i], str(j - i), _code(piece), _code(out)])
        i = j
    return _trace(
        "Run-length encoding \"aaabccdddd\"",
        "Find the run starting at `i` by advancing `j` while the character repeats, emit the "
        "character and its length, then jump `i` straight to `j`.",
        ["Run [i, j)", "Char", "Length", "Emitted", "Output so far"],
        rows,
        "Four runs, ten characters, and `i` jumps to `j` each time, so every character is "
        "examined once — O(n). Setting `i++` instead of `i = j` would still produce the right "
        "first piece and then re-encode the tail of every run. Build the output with a "
        "`StringBuilder` in Java; the column is a string here only to show its state.",
    )


# ---------------------------------------------------------------- stage 3

def _t_sorting():
    a = [5, 2, 4, 6, 1, 3]
    rows = [["start", "—", _fmt_list(a), "—"]]
    for i in range(1, len(a)):
        x = a[i]
        j = i - 1
        shifts = 0
        while j >= 0 and a[j] > x:
            a[j + 1] = a[j]
            j -= 1
            shifts += 1
        a[j + 1] = x
        rows.append([str(i), str(x), _fmt_list(a), str(shifts)])
    return _trace(
        "Insertion sort: [5, 2, 4, 6, 1, 3]",
        "The prefix `a[0..i−1]` is always sorted. Take `a[i]`, shift every larger element in "
        "the prefix one place right, and drop it into the gap.",
        ["i", "Inserting", "Array after", "Shifts"],
        rows,
        "Nine shifts in total, and that number is exactly the count of *inversions* — pairs "
        "that are out of order. That is why insertion sort is O(n²) on reversed input and O(n) "
        "on nearly-sorted input, and why TimSort uses it for short runs.",
    )


def _t_gcd():
    a, b = 1071, 462
    rows = []
    while b != 0:
        rows.append([str(a), str(b), f"{a} = {a // b} × {b} + {a % b}", str(a % b)])
        a, b = b, a % b
    rows.append([str(a), "0", "b is 0", f"**gcd = {a}**"])
    return _trace(
        "Euclid's algorithm: gcd(1071, 462)",
        "`gcd(a, b) = gcd(b, a % b)`, because anything dividing both a and b also divides "
        "the remainder. Stop when b reaches 0.",
        ["a", "b", "Division", "a % b"],
        rows,
        "Three divisions from 1071 to the answer 21. The remainder is always smaller than b, "
        "and every two steps the numbers at least halve — that is the O(log min(a, b)) bound.",
    )


def _t_fast_pow():
    base, e, mod = 3, 13, 1000
    r = 1
    rows = []
    while e > 0:
        bit = e & 1
        new_r = (r * base) % mod if bit else r
        rows.append([f"{e} = {bin(e)[2:]}₂", str(bit), str(base), f"{r} × {base} = {new_r}" if bit else f"{r} (unchanged)", f"{base}² mod 1000 = {(base * base) % mod}"])
        r = new_r
        base = (base * base) % mod
        e >>= 1
    rows.append(["0", "—", "—", f"**{r}**", "—"])
    return _trace(
        "Fast exponentiation: 3¹³ mod 1000",
        "13 is `1101` in binary, so 3¹³ = 3⁸ · 3⁴ · 3¹. Square the base each step; multiply it "
        "into the result only when the current low bit of the exponent is 1.",
        ["e", "Low bit", "base (= 3^(2^step))", "result", "Next base"],
        rows,
        f"Four steps for a 4-bit exponent, and 3¹³ = 1 594 323, so the answer {pow(3, 13, 1000)} "
        "checks out. Taking `% mod` after every multiplication is what keeps the numbers from "
        "overflowing on the way — the answer is the same either way, only the intermediate "
        "values differ.",
    )


def _t_kernighan():
    x = 44
    c = 0
    rows = []
    while x != 0:
        y = x & (x - 1)
        c += 1
        rows.append([f"{x:08b}", f"{x - 1:08b}", f"{y:08b}", str(c)])
        x = y
    return _trace(
        "Counting set bits by clearing the lowest one: x = 44",
        "`x − 1` flips the lowest set bit to 0 and every 0 below it to 1. ANDing with x keeps "
        "everything above that bit and clears the rest.",
        ["x", "x − 1", "x & (x − 1)", "Bits cleared"],
        rows,
        "44 is `00101100`: three set bits, three iterations — the loop never visits the five "
        "zero bits. The same expression `x & (x − 1)` being 0 is the power-of-two test.",
    )


def _t_xor():
    a = [4, 1, 2, 1, 2]
    x = 0
    rows = []
    for v in a:
        nx = x ^ v
        rows.append([str(v), f"{x:03b}", f"{v:03b}", f"{nx:03b} ({nx})"])
        x = nx
    return _trace(
        "The element that appears once: XOR of [4, 1, 2, 1, 2]",
        "XOR is its own inverse (`v ^ v == 0`) and order does not matter, so every pair "
        "cancels no matter where its two halves sit.",
        ["Next value", "Accumulator", "Value in binary", "After XOR"],
        rows,
        "The accumulator ends at 4 — the unpaired value — after passing through states like "
        "`111` (7) that mean nothing on their own. One pass, O(1) space, no set.",
    )


def _grid_rows(m):
    return [" ".join(f"{v:>2}" for v in row) for row in m]


def _t_rotate():
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    rows = [["start"] + [_code(r) for r in _grid_rows(m)]]
    n = len(m)
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]
    rows.append(["transpose (swap m[i][j] with m[j][i])"] + [_code(r) for r in _grid_rows(m)])
    for row in m:
        row.reverse()
    rows.append(["reverse each row"] + [_code(r) for r in _grid_rows(m)])
    return _trace(
        "Rotating a matrix 90° clockwise in place",
        "Rotation is two reflections: flip across the main diagonal, then flip each row "
        "left-to-right. Neither step needs a second matrix.",
        ["Step", "Row 0", "Row 1", "Row 2"],
        rows,
        "The first column read bottom-up, `7 4 1`, has become the first row — which is what a "
        "clockwise turn does. Reversing each *column* instead of each row gives the "
        "counter-clockwise rotation. The transpose loop starts `j` at `i + 1`; starting at 0 "
        "swaps every pair twice and undoes itself.",
    )


# ---------------------------------------------------------------- stage 5

def _t_recursion():
    rows = []
    stack = []
    step = 0

    def fact(n):
        nonlocal step
        stack.append(f"fact({n})")
        step += 1
        rows.append([str(step), f"call fact({n})", " → ".join(stack), "—"])
        if n <= 1:
            result = 1
        else:
            sub = fact(n - 1)
            result = n * sub
        step += 1
        shown = " → ".join(stack)
        rows.append([str(step), f"return from fact({n})", shown,
                     "1 (base case)" if n <= 1 else f"{n} × {result // n} = **{result}**"])
        stack.pop()
        return result

    fact(4)
    return _trace(
        "The call stack of fact(4)",
        "Each call waits on the one it made. The stack column shows every frame alive at that "
        "moment, oldest on the left — the rightmost is the one running.",
        ["Step", "Event", "Stack (bottom → top)", "Value returned"],
        rows,
        "The stack grows to four frames before anything is multiplied: all the work happens "
        "on the way *back*, as each frame resumes with its child's answer. That depth is the "
        "O(n) space cost of recursion, and it is what overflows for n in the tens of thousands.",
    )


class _TNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def _t_trees():
    root = _TNode(1, _TNode(2, _TNode(4), _TNode(5)), _TNode(3, None, _TNode(6, _TNode(7))))
    q = _deque([root])
    rows = []
    level = 0
    while q:
        size = len(q)
        before = _fmt_list([n.val for n in q])
        polled = []
        for _ in range(size):
            t = q.popleft()
            polled.append(t.val)
            if t.left:
                q.append(t.left)
            if t.right:
                q.append(t.right)
        rows.append([str(level), before, str(size), _fmt_list(polled), _fmt_list([n.val for n in q])])
        level += 1
    return _trace(
        "Level-order traversal, one level per outer iteration",
        "The tree: 1 has children 2 and 3; 2 has 4 and 5; 3 has only a right child 6; 6 has a "
        "left child 7. Snapshot `q.size()` *before* polling, so children added during the "
        "level wait for the next one.",
        ["Level", "Queue at start", "size", "Polled this level", "Queue after"],
        rows,
        "Four levels, and the queue at the start of each level is exactly that level's nodes. "
        "Reading `q.size()` inside the loop condition instead of snapshotting it would mix "
        "levels as soon as a child is enqueued. The missing left child of 3 is simply skipped "
        "— no null ever enters the queue.",
    )


def _t_bst():
    keys = [50, 30, 70, 20, 40, 60, 80, 65]

    def insert(t, k):
        if t is None:
            return _TNode(k)
        if k < t.val:
            t.left = insert(t.left, k)
        else:
            t.right = insert(t.right, k)
        return t

    root = None
    for k in keys:
        root = insert(root, k)
    rows = []
    for target in (65, 45):
        t = root
        depth = 0
        while t is not None:
            if target == t.val:
                rows.append([str(target), str(depth), str(t.val), "equal", "**found**"])
                break
            go = "left" if target < t.val else "right"
            rows.append([str(target), str(depth), str(t.val), f"{target} {'<' if target < t.val else '>'} {t.val}", f"go {go}"])
            t = t.left if target < t.val else t.right
            depth += 1
        else:
            rows.append([str(target), str(depth), "null", "—", "**absent**"])
    return _trace(
        "Searching a BST built from 50, 30, 70, 20, 40, 60, 80, 65",
        "Every comparison discards a whole subtree. Two searches: one that finds its key, and "
        "one that falls off the tree where the key *would* be inserted.",
        ["Target", "Depth", "Node", "Compare", "Decision"],
        rows,
        "Each search looks at one node per level — at most the height, 3 here — rather than "
        "all 8 nodes. The failed search for 45 ends at the null right child of 40, which is "
        "exactly where `insert(45)` would put it: search and insert are the same walk.",
    )


def _t_bfs():
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
    n = 6
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = [-1] * n
    dist[0] = 0
    q = _deque([0])
    rows = []
    while q:
        u = q.popleft()
        new = []
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
                new.append(f"{v} (d={dist[v]})")
        rows.append([str(u), _fmt_list(adj[u]), ", ".join(new) if new else "—", _fmt_list(list(q)),
                     " ".join(str(d) if d >= 0 else "·" for d in dist)])
    return _trace(
        "BFS from 0, recording distances",
        "Edges: 0–1, 0–2, 1–3, 2–3, 2–4, 3–5, 4–5. A node gets its distance — and is marked "
        "seen — the moment it is *discovered*, not when it is polled.",
        ["Poll", "Neighbours", "Newly discovered", "Queue after", "dist[0..5]"],
        rows,
        "Node 3 is reachable from both 1 and 2, and it is discovered once, from 1, with "
        "distance 2; when 2 later looks at it, it is already marked. Marking on poll instead "
        "would enqueue 3 twice. Distances come out in non-decreasing order down the Poll "
        "column, which is the property that makes BFS a shortest-path algorithm.",
    )


def _t_topo():
    names = ["intro", "arrays", "hashing", "trees", "graphs", "dp"]
    edges = [(0, 1), (0, 3), (1, 2), (1, 5), (2, 4), (3, 4)]
    n = len(names)
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = _deque(i for i in range(n) if indeg[i] == 0)
    order = []
    rows = []
    while q:
        u = q.popleft()
        order.append(names[u])
        freed = []
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
                freed.append(names[v])
        rows.append([names[u], ", ".join(names[v] for v in adj[u]) or "—",
                     ", ".join(freed) or "—", _fmt_list([names[i] for i in q]),
                     " → ".join(order)])
    return _trace(
        "Kahn's algorithm on a course plan",
        "Prerequisites: intro → arrays, intro → trees, arrays → hashing, arrays → dp, "
        "hashing → graphs, trees → graphs. Start with every course that has no prerequisite; "
        "taking a course lowers the in-degree of what it unlocks.",
        ["Take", "Unlocks edges to", "Now free", "Queue after", "Order so far"],
        rows,
        "All six courses come out, so there is no cycle. `graphs` has two prerequisites and "
        "becomes free only when the *second* of them, `hashing`, is taken — the in-degree count "
        "is what makes it wait. Had a cycle existed, its courses would never reach in-degree 0 "
        "and the order would stop short.",
    )


# ---------------------------------------------------------------- stage 6

def _t_greedy():
    iv = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
    iv.sort(key=lambda x: x[1])
    end = None
    rows = []
    kept = 0
    for s, e in iv:
        if end is None or s >= end:
            kept += 1
            rows.append([f"[{s}, {e})", "—" if end is None else str(end), "yes", "**keep**", str(kept)])
            end = e
        else:
            rows.append([f"[{s}, {e})", str(end), "no", "skip — overlaps the last kept", str(kept)])
    return _trace(
        "Most non-overlapping meetings, sorted by end time",
        "Always keep the meeting that *ends* earliest among those that still fit. Sorted by "
        "end, that is simply the next one whose start is at or after the last kept end.",
        ["Meeting", "Last kept end", "Starts after it?", "Decision", "Kept"],
        rows,
        "Four meetings kept out of eleven: [1, 4), [5, 7), [8, 11), [12, 16). Sorting by "
        "*start* would keep [0, 6) first and lose one; sorting by *length* fails on other "
        "inputs. Ending earliest leaves the most room for everything after — that is the "
        "exchange argument in one sentence.",
    )


def _t_intervals():
    iv = [[8, 10], [1, 3], [15, 18], [2, 6], [9, 12]]
    iv.sort(key=lambda x: x[0])
    out = []
    rows = [["sorted by start", "—", "—", " ".join(_fmt_list(x) for x in iv)]]
    for x in iv:
        last = _fmt_list(out[-1]) if out else "—"
        if not out or out[-1][1] < x[0]:
            out.append(list(x))
            action = "no overlap — start a new interval"
        else:
            old = out[-1][1]
            out[-1][1] = max(out[-1][1], x[1])
            action = f"overlaps — extend end {old} → {out[-1][1]}"
        rows.append([_fmt_list(x), last, action, " ".join(_fmt_list(y) for y in out)])
    return _trace(
        "Merging intervals: [8, 10], [1, 3], [15, 18], [2, 6], [9, 12]",
        "After sorting by start, an interval can only overlap the *last* merged interval, so "
        "one comparison per interval is enough.",
        ["Next", "Compared with", "Action", "Merged so far"],
        rows,
        "Five intervals become three: [1, 6], [8, 12], [15, 18]. The `max` on the end matters — "
        "an interval swallowed entirely by the previous one (like [2, 4] inside [1, 6]) must "
        "not *shrink* the end. Without the sort, [1, 3] and [2, 6] are two positions apart and "
        "a single pass would miss them.",
    )


def _t_tries():
    root = {}
    total = 0
    rows = []
    for w in ("car", "cat", "cart", "care"):
        cur = root
        created = []
        for ch in w:
            if ch not in cur:
                cur[ch] = {}
                created.append(ch)
            cur = cur[ch]
        cur["$"] = True
        total += len(created)
        shared = len(w) - len(created)
        rows.append([_code(w), _code(w[:shared]) if shared else "—",
                     ", ".join(created) if created else "—", str(total)])
    # a prefix query against the finished trie
    cur = root
    for ch in "ca":
        cur = cur[ch]
    under = []

    def collect(node, pre):
        if node.get("$"):
            under.append(pre)
        for ch in sorted(k for k in node if k != "$"):
            collect(node[ch], pre + ch)

    collect(cur, "ca")
    rows.append([_code("startsWith(\"ca\")"), _code("ca"), "—", f"{total} (collects {', '.join(under)})"])
    return _trace(
        "Building a trie: car, cat, cart, care",
        "Each word walks down from the root, reusing every node its prefix already created and "
        "adding nodes only where it diverges. A flag marks the node where a word ends.",
        ["Insert", "Reused prefix", "New nodes", "Nodes in trie"],
        rows,
        "Four words, fourteen characters, and only six nodes: `c`, `a`, `r`, `t`, `t`, `e`. "
        "`cart` and `care` cost one node each because `car` was already there — and `car` "
        "is still a word, because its end flag is on the `r` node, not on a leaf. The prefix "
        "query walks two nodes and never looks at a word that does not start with `ca`.",
    )


_TRACES_BY_UNIT = {
    "io-and-arithmetic": [_t_io()],
    "branching": [_t_branching()],
    "loops-and-digits": [_t_digits()],
    "arrays-first-pass": [_t_arrays()],
    "complexity": [_t_complexity()],
    "hashing": [_t_hashing()],
    "two-pointers": [_t_two_pointers()],
    "sliding-window": [_t_sliding_window()],
    "prefix-sums": [_t_prefix_sums()],
    "strings": [_t_strings()],
    "sorting": [_t_sorting()],
    "math-number-theory": [_t_gcd(), _t_fast_pow()],
    "bit-manipulation": [_t_kernighan(), _t_xor()],
    "simulation-and-matrix": [_t_rotate()],
    "recursion": [_t_recursion()],
    "trees": [_t_trees()],
    "bst": [_t_bst()],
    "graph-traversal": [_t_bfs()],
    "topological-sort": [_t_topo()],
    "greedy": [_t_greedy()],
    "intervals": [_t_intervals()],
    "tries": [_t_tries()],
}


def _attach_traces():
    by_key = {u["key"]: u for u in _UNITS}
    for key, traces in _TRACES_BY_UNIT.items():
        assert key in by_key, f"dsa_traces.py: no unit {key!r}"
        by_key[key]["traces"].extend(traces)


_attach_traces()
