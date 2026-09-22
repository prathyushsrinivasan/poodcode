# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 4 (Numbers, Bits & Grids) — the depth layer.
#
# exec'd by tools/dsa_curriculum.py after dsa_s3_help.py, in the same
# namespace. For each of the stage's three units it attaches:
#
#   invariant, variants, rewrites, internals, build_it   (the stage-3 round-1 layer)
#   extra skeletons, signals, costs, pitfalls and checks for the new material
#   computed traces and extra Big-O drills
#   the rebuilt ladder, with the 22 problems of batches 50-52 placed
#
# Every trace row is produced by running the algorithm it describes, as in
# dsa_s3_depth.py, so a table can never disagree with the code beside it.
# ---------------------------------------------------------------------------


# ============================================================ computed traces

def _t4_ext_euclid():
    a, m = 17, 60
    r0, r1, s0, s1, t0, t1 = a, m, 1, 0, 0, 1
    rows = [["start", "—", f"{r0} = {a}·{s0} + {m}·{t0}", f"{r1} = {a}·{s1} + {m}·{t1}"]]
    step = 0
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
        step += 1
        rows.append([str(step), str(q), f"{r0} = {a}·({s0}) + {m}·({t0})",
                     f"{r1} = {a}·({s1}) + {m}·({t1})"])
    inv = s0 % m
    return _trace(
        "Extended Euclid: the inverse of 17 modulo 60",
        "Each row is a remainder written as a combination of the two inputs. The new row is the "
        "old one minus q times the other — Euclid's step, applied to the coefficients too.",
        ["Step", "q", "Row 0 (r = 17·s + 60·t)", "Row 1"],
        rows,
        f"The remainders run 17, 60, 17, 9, 8, 1, 0 — plain Euclid. When row 1 reaches 0, row 0 "
        f"says 1 = 17·({s0}) + 60·({t0}). Modulo 60 the second term vanishes, so 17·({s0}) ≡ 1, and "
        f"the inverse is {s0} mod 60 = **{inv}**. Check: 17 · {inv} = {17 * inv} = "
        f"{17 * inv // 60}·60 + 1.",
    )


def _t4_spf_sieve():
    n = 30
    spf = [0] * (n + 1)
    rows = []
    for i in range(2, n + 1):
        if spf[i]:
            continue
        got = []
        for j in range(i, n + 1, i):
            if spf[j] == 0:
                spf[j] = i
                got.append(j)
        rows.append([str(i), "prime", " ".join(map(str, got))])
        if i * i > n:
            break
    for k in range(2, n + 1):
        if spf[k] == 0:
            spf[k] = k
    rows.append(["…", "the rest are prime", "each is its own smallest factor"])
    steps = []
    y = 24
    while y > 1:
        steps.append(str(spf[y]))
        y //= spf[y]
    return _trace(
        "Smallest-prime-factor sieve to 30",
        "`spf[j]` is claimed by the first prime whose multiples reach j — which, going up, is "
        "j's smallest prime factor.",
        ["Prime i", "Status", "Numbers whose spf becomes i"],
        rows,
        f"Once i · i > 30 nothing new is claimed except the primes themselves. Factoring now "
        f"costs one lookup per prime factor: 24 → spf 2 → 12 → 2 → 6 → 2 → 3 → 3, so "
        f"24 = {' · '.join(steps)}.",
    )


def _t4_divisor_blocks():
    n = 20
    rows, total, i = [], 0, 1
    while i <= n:
        q = n // i
        j = n // q
        total += q * (j - i + 1)
        rows.append([f"{i}…{j}", str(q), f"{q} × {j - i + 1} = {q * (j - i + 1)}", str(total)])
        i = j + 1
    return _trace(
        "Σ ⌊20 / i⌋ by blocks of equal quotient",
        "For each block start i, the quotient is q = 20 / i and the block ends at j = 20 / q.",
        ["i range", "q = 20 / i", "Contribution", "Running sum"],
        rows,
        f"{len(rows)} blocks instead of 20 terms. For small i every block is one number; for "
        f"large i the blocks get long, because 20 / i changes slowly there. Fewer than 2√n "
        f"blocks in general.",
    )


def _t4_kernighan():
    x = 104
    rows, count = [], 0
    while x:
        y = x & (x - 1)
        count += 1
        rows.append([f"{x:08b}", f"{x - 1:08b}", f"{y:08b}", str(count)])
        x = y
    return _trace(
        "Kernighan's count on 104 = 01101000",
        "`x − 1` flips the lowest 1 and every 0 below it; AND-ing with x keeps the higher bits "
        "and zeroes that block.",
        ["x", "x − 1", "x & (x − 1)", "count"],
        rows,
        "Three iterations for three set bits — not eight for eight bit positions. Each row "
        "removes exactly the lowest 1, which is the invariant: count + bitCount(x) never changes.",
    )


def _t4_gosper():
    rows = []
    x = 0b00111
    for _ in range(6):
        c = x & -x
        r = x + c
        nxt = r | (((x ^ r) >> 2) // c)
        rows.append([f"{x:05b}", f"{c:05b}", f"{r:05b}", f"{nxt:05b} ({nxt})"])
        x = nxt
    return _trace(
        "Gosper's hack: 3-element subsets of 5, in order",
        "c isolates the lowest 1, r = x + c carries through the lowest block of 1s, and the "
        "leftover 1s are slid down to bit 0.",
        ["x", "c = x & −x", "r = x + c", "next"],
        rows,
        "Every value has exactly three 1s, and they come out in increasing order: 7, 11, 13, 14, "
        "19, 21, 22 — the 3-subsets of {0…4} in lexicographic order of their masks. No subset is "
        "generated and then rejected, which is the point over filtering 0 … 31 by bitCount.",
    )


def _t4_submasks():
    mask = 0b1011
    rows, sub = [], mask
    while True:
        rows.append([f"{sub:04b}", str(sub), f"({sub:04b} − 1) & 1011 = {((sub - 1) & mask) & 0xF:04b}" if sub else "stop"])
        if sub == 0:
            break
        sub = (sub - 1) & mask
    return _trace(
        "Every submask of 1011, largest first",
        "`sub = (sub − 1) & mask` steps to the next smaller submask: the − 1 borrows, and the AND "
        "throws away the bits that are not in the mask.",
        ["sub", "value", "next"],
        rows,
        "Eight submasks for three set bits (2³), visited without touching any of the 16 − 8 "
        "numbers that are not submasks. Summed over every mask of n bits this is 3ⁿ — the cost "
        "of the “iterate over submasks” bitmask DPs.",
    )


def _t4_xor_split():
    a = [4, 1, 6, 2, 4, 5]
    n = len(a)
    x = 0
    for i, v in enumerate(a, 1):
        x ^= v ^ i
    bit = x & -x
    rows, p, q = [], 0, 0
    for i, v in enumerate(a, 1):
        for val, src in ((v, "tag"), (i, "index")):
            if val & bit:
                p ^= val
            else:
                q ^= val
        rows.append([str(i), str(v), f"{p} ({p:03b})", f"{q} ({q:03b})"])
    return _trace(
        "The swapped tag: splitting dup ^ missing = " + f"{x:03b}" + " by its lowest bit",
        f"x = XOR of every tag and every index = dup ^ missing = {x}, and its lowest set bit is "
        f"{bit}. Each tag and each index goes into bucket p if it has that bit, q otherwise.",
        ["i", "tag a[i]", "p (bit set)", "q (bit clear)"],
        rows,
        f"The buckets end as {p} and {q}. Inside each, every number other than the two answers "
        f"appeared an even number of times and cancelled. 4 is among the tags, so the duplicate "
        f"is 4 and the missing tag is 3.",
    )


def _t4_spiral():
    g = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    top, bot, left, right = 0, 2, 0, 3
    rows = []
    while top <= bot and left <= right:
        seg = [g[top][j] for j in range(left, right + 1)]
        rows.append(["top →", f"[{top}..{bot}]×[{left}..{right}]", " ".join(map(str, seg))])
        top += 1
        seg = [g[i][right] for i in range(top, bot + 1)]
        rows.append(["right ↓", f"[{top}..{bot}]×[{left}..{right}]", " ".join(map(str, seg)) or "—"])
        right -= 1
        if top <= bot:
            seg = [g[bot][j] for j in range(right, left - 1, -1)]
            rows.append(["bottom ←", f"[{top}..{bot}]×[{left}..{right}]", " ".join(map(str, seg)) or "—"])
            bot -= 1
        else:
            rows.append(["bottom ←", f"[{top}..{bot}]×[{left}..{right}]", "skipped: top > bot"])
        if left <= right:
            seg = [g[i][left] for i in range(bot, top - 1, -1)]
            rows.append(["left ↑", f"[{top}..{bot}]×[{left}..{right}]", " ".join(map(str, seg)) or "—"])
            left += 1
        else:
            rows.append(["left ↑", f"[{top}..{bot}]×[{left}..{right}]", "skipped: left > right"])
    return _trace(
        "Spiral order of a 3 × 4 grid, one edge per row",
        "The rectangle column is what is still unvisited *before* the edge is walked. Each edge "
        "shrinks it by one row or one column.",
        ["Edge", "Unvisited rectangle", "Emitted"],
        rows,
        "The second lap is a single row, [1..1] × [1..2]: 6 7. After it, `top` passes `bot`, so "
        "the bottom edge is skipped — without the guard it would walk row 1 again, right to left, "
        "and emit 7 6 a second time.",
    )


def _t4_tilt_row():
    row = list("O.#.OO.O")
    rows = []
    free = 0
    for j in range(len(row)):
        ch = row[j]
        if ch == "#":
            free = j + 1
            act = f"wall: free → {free}"
        elif ch == "O":
            row[j] = "."
            row[free] = "O"
            act = f"stone to {free}, free → {free + 1}"
            free += 1
        else:
            act = "empty: nothing"
        rows.append([str(j), ch, act, "".join(row)])
    return _trace(
        "Tilting one row left: O.#.OO.O",
        "`free` is the leftmost cell a stone could still roll to. A wall resets it past itself; "
        "a stone moves to it.",
        ["j", "Cell", "Action", "Row after"],
        rows,
        "One pass, and no stone moves twice. The wall splits the row into two independent "
        "segments. Clearing the old cell before writing the new one matters at j = 0, where the "
        "stone's old and new cell are the same.",
    )


def _t4_lamp_cycle():
    s = "00001"
    w = len(s)
    full = (1 << w) - 1
    x = int(s[::-1], 2)
    seen, rows, t = {}, [], 0
    while x not in seen:
        seen[x] = t
        rows.append([str(t), "".join("1" if x >> i & 1 else "0" for i in range(w)), "first time"])
        x = ((x << 1) ^ (x >> 1)) & full
        t += 1
    start = seen[x]
    rows.append([str(t), "".join("1" if x >> i & 1 else "0" for i in range(w)),
                 f"seen on night {start}: cycle of length {t - start}"])
    n = 10 ** 18
    return _trace(
        "Lamps 00001: the first repeat",
        "Record the night each row is first seen. The first row seen twice closes a cycle.",
        ["Night", "Row", "Seen before?"],
        rows,
        f"From night {start} on, the rows repeat every {t - start} nights. For n = 10¹⁸ the "
        f"answer is the row on night {start} + (10¹⁸ − {start}) mod {t - start} = night "
        f"{start + (n - start) % (t - start)} — found after simulating {t} nights, not 10¹⁸. "
        f"The starting row is never seen again: it is a **pre-period**, which is why the skip "
        f"is (n − t) mod cycle and not n mod cycle. (Odd widths have one; for even widths "
        f"this rule is invertible, and every row lies on a cycle.)",
    )


# ================================================================ Big-O drills

_BIGO_S4 = {
    "math-number-theory": [
        _bigo("""
long result = n;
for (long p = 2; p * p <= n; p++) {
    if (n % p != 0) continue;
    while (n % p == 0) n /= p;
    result -= result / p;
}
if (n > 1) result -= result / n;
""", "O(√n)", ["O(√n)", "O(n)", "O(log n)", "O(√n · log n)"],
              """
The outer loop runs to √n at most. The inner `while` divides n down, and the total number
of divisions over the whole run is the number of prime factors counted with multiplicity —
at most log₂ n — so it adds O(log n), which √n dominates.
"""),
        _bigo("""
for (long i = 1; i <= n; ) {
    long q = n / i, j = n / q;
    sum += q * (j - i + 1);
    i = j + 1;
}
""", "O(√n)", ["O(√n)", "O(n)", "O(log n)", "O(n log n)"],
              """
Each iteration handles a whole block of i with the same quotient n / i, and there are fewer
than 2√n distinct quotients: at most √n for i ≤ √n, and for i > √n the quotient itself is
below √n.
"""),
        _bigo("""
int[] spf = new int[M + 1];
for (int i = 2; i <= M; i++) {
    if (spf[i] != 0) continue;
    for (int j = i; j <= M; j += i)
        if (spf[j] == 0) spf[j] = i;
}
""", "O(M log log M)", ["O(M log log M)", "O(M√M)", "O(M log M)", "O(M²)"],
              """
The inner loop runs M / p times for each prime p, and Σ 1/p over primes up to M is about
ln ln M. This is the sieve of Eratosthenes, storing a factor instead of a flag.
"""),
    ],
    "bit-manipulation": [
        _bigo("""
for (int mask = 0; mask < (1 << n); mask++)
    for (int sub = mask; sub > 0; sub = (sub - 1) & mask)
        work(mask, sub);
""", "O(3ⁿ)", ["O(3ⁿ)", "O(4ⁿ)", "O(2ⁿ · n)", "O(2ⁿ)"],
              """
Each element is in three states for a (mask, sub) pair: out of the mask, in the mask but
not the submask, or in both. So the pairs number 3ⁿ — far fewer than the 4ⁿ a naive double
loop over all masks would visit.
"""),
        _bigo("""
long total = 0;
for (int b = 0; b < 30; b++) {
    long ones = 0;
    for (int v : a) ones += (v >> b) & 1;
    total += ones * (n - ones) << b;
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(2ⁿ)"],
              """
30 passes of n — O(30n), and 30 is a constant (the word size), so O(n). The pairwise
version this replaces is O(n²).
"""),
        _bigo("""
int res = 0;
for (int b = 29; b >= 0; b--) {
    int cand = res | (1 << b), count = 0;
    for (int v : a) if ((v & cand) == cand) count++;
    if (count >= 2) res = cand;
}
""", "O(n · B) for B-bit values", ["O(n · B) for B-bit values", "O(n²)", "O(2^B)", "O(n log n)"],
              """
One pass over the array per bit position. With B = 30 it is 30n operations. The answer's
bits are decided greedily — no pair is ever examined directly.
"""),
    ],
    "simulation-and-matrix": [
        _bigo("""
for (int t = 0; t < k; t++)          // k single steps
    rotateRingByOne(ring);           // ring has L cells
""", "O(k · L)", ["O(k · L)", "O(L)", "O(k)", "O(k + L)"],
              """
Each single step moves every one of the L cells. With k up to 10⁹, that is hopeless — and
unnecessary, because the ring is back where it started after L steps. Shift once by
k mod L: O(L).
"""),
        _bigo("""
Map<Long, Long> seen = new HashMap<>();
long t = 0;
while (t < n && !seen.containsKey(state)) {
    seen.put(state, t++);
    state = step(state);
}
""", "O(min(n, S)) where S is the number of states", ["O(min(n, S)) where S is the number of states", "O(n)", "O(S²)", "O(log n)"],
              """
A deterministic process must repeat a state within S + 1 steps, so the loop stops after at
most S iterations even when n is 10¹⁸ — or after n, if n is smaller.
"""),
        _bigo("""
for (char d : cmds.toCharArray())        // t tilts
    for (int i = 0; i < r; i++)
        compactRow(g[i], d);             // one pass over c cells
""", "O(t · r · c)", ["O(t · r · c)", "O(t · r · c²)", "O(r · c)", "O(t · (r + c))"],
              """
Each tilt is one linear compaction per row (or column), so r · c work per tilt. Moving
stones one cell at a time until nothing moves would be O(r · c) *iterations* of an
O(r · c) pass per tilt.
"""),
    ],
}


# ================================================================ the depth

_D_MATH = dict(
    invariant=_inv(
        "Extended Euclid keeps two rows `(r, s)` with **`r ≡ a·s (mod m)`** in each, and "
        "**`gcd(r0, r1) = gcd(a, m)`**.",
        "The rows start as `(a, 1)` and `(m, 0)`: a = a·1, and m ≡ a·0 (mod m). The pair "
        "(r0, r1) is (a, m) itself, so its gcd is gcd(a, m).",
        "The new row is `row0 − q·row1` with q = r0 / r1. Both congruences are linear, so the "
        "difference satisfies one too: r0 − q·r1 ≡ a·(s0 − q·s1). And "
        "gcd(r1, r0 − q·r1) = gcd(r0, r1), because anything dividing r1 divides r0 exactly "
        "when it divides r0 − q·r1.",
        "The loop stops when r1 = 0. Then gcd(r0, 0) = r0, so r0 = gcd(a, m), and row 0 says "
        "gcd(a, m) ≡ a·s0 (mod m). When the gcd is 1, s0 is the inverse; when it is not, no "
        "inverse exists — the same loop answers both questions.",
        "Plain Euclid is the second half alone. The sieve has an invariant too: when i is "
        "reached and not crossed out, no prime below i divides it — so it is prime.",
    ),
    variants=[
        _var("Trial division", "Loop d while d · d ≤ n.",
             "One primality test, one divisor count, one divisor sum.", "O(√n)",
             "Guard n < 2 first; count d and n/d once when they are equal."),
        _var("Factorise as you go", "When d divides n, divide it out completely before d++.",
             "Prime factorisation, φ(n), radical, “distinct primes”.", "O(√n)",
             "Whatever is left above 1 at the end is one more prime."),
        _var("Sieve of Eratosthenes", "One boolean array; cross out multiples from i · i.",
             "Every prime below n; count primes.", "O(n log log n), O(n) space",
             "Compute i · i in long."),
        _var("Smallest-prime-factor sieve", "Store which prime crossed a number out.",
             "Factorise many numbers up to ~10⁷.", "O(M log log M) once, O(log x) per query",
             "An int array of 10⁷ is 40 MB — fine, but 10⁸ is not."),
        _var("Segmented sieve", "Sieve primes to √R, then cross out their multiples inside [L, R] only.",
             "Primes in a window near 10¹².", "O((R − L) log log R + √R)",
             "Start at max(p², first multiple ≥ L), and 1 is not prime."),
        _var("gcd / lcm", "Euclid's loop; lcm = a / gcd · b.",
             "Fractions, periods that line up, array-wide gcd.", "O(log min(a, b))",
             "Divide before multiplying."),
        _var("Extended Euclid", "Carry the coefficient rows through Euclid's loop.",
             "Inverse mod a composite m; a·x + b·y = gcd.", "O(log m)",
             "Normalise the coefficient into [0, m)."),
        _var("Fast power mod p", "Square the base, halve the exponent, multiply on odd bits.",
             "aᵇ mod p for b up to 10¹⁸; Fermat inverses.", "O(log b)",
             "Reduce the base before the first square."),
        _var("Factorial tables", "fact[] forward, invFact[] backward from one Fermat inverse.",
             "Many binomial coefficients mod p.", "O(N) once, O(1) each",
             "Reduce between the two products in nCr."),
        _var("Chinese remainder merge", "x = a1 + m1·t, solve m1·t ≡ a2 − a1 (mod m2) for t.",
             "Two cycles lining up; x mod several moduli.", "O(log m)",
             "gcd(m1, m2) must divide a2 − a1, or there is no solution."),
        _var("Divisor blocks", "Jump i to n / (n / i) + 1: one step per distinct quotient.",
             "Σ f(n / i), Σ over divisors of all k ≤ n.", "O(√n)",
             "The block end is n / q, not n / q + 1."),
        _var("Totient", "result −= result / p for each distinct prime p of n.",
             "Count k ≤ n coprime to n; Euler's theorem aᵠ⁽ᵐ⁾ ≡ 1.", "O(√n)",
             "It is the distinct primes that matter, not their exponents."),
    ],
    rewrites=[
        _rw("Primality: stop at the square root",
            """
static boolean isPrime(long n) {
    if (n < 2) return false;
    for (long d = 2; d < n; d++)          // n - 2 candidates
        if (n % d == 0) return false;
    return true;
}
""",
            """
static boolean isPrime(long n) {
    if (n < 2) return false;
    for (long d = 2; d * d <= n; d++)     // √n candidates
        if (n % d == 0) return false;
    return true;
}
""",
            "The loop bound `d < n` becomes `d * d <= n`.",
            """
Divisors come in pairs d × n/d, and in every pair one member is at most √n. If nothing up
to √n divides n, nothing above it can either — its partner would have been found first. At
n = 10¹², that is 10⁶ steps instead of 10¹².
"""),
        _rw("Many primes: one sieve, not n tests",
            """
int count = 0;
for (int x = 2; x < n; x++)
    if (isPrime(x)) count++;            // O(√x) each
""",
            """
boolean[] composite = new boolean[n];
int count = 0;
for (int i = 2; i < n; i++) {
    if (composite[i]) continue;
    count++;
    for (long j = (long) i * i; j < n; j += i) composite[(int) j] = true;
}
""",
            "Per-number trial division becomes crossing out multiples.",
            """
Trial division rediscovers the same small factors for every number: 2 is tried against
all n of them. The sieve does the opposite — each prime visits only its own multiples,
once — and the total is n · Σ 1/p ≈ n ln ln n instead of n√n.
"""),
        _rw("Factorise many numbers: remember the smallest factor",
            """
for (int x : queries) {                  // q queries up to 10^6
    int c = 1;
    for (int d = 2; d * d <= x; d++) { /* divide out d */ }
    ...
}
""",
            """
int[] spf = sieveSmallestFactor(MAX);    // once
for (int x : queries) {
    while (x > 1) { int p = spf[x]; /* divide out p */ x /= p; }
}
""",
            "The trial-division loop per query becomes a lookup chain in `spf`.",
            """
The sieve pays O(M log log M) once and then answers “what is the smallest prime factor of
x?” in O(1). Factoring x follows that chain, and each step at least halves x, so a query is
O(log x) instead of O(√x): 20 steps instead of 1,000 at x = 10⁶.
"""),
        _rw("Σ ⌊n / i⌋: one step per quotient, not per i",
            """
long sum = 0;
for (long i = 1; i <= n; i++) sum += n / i;     // n steps
""",
            """
long sum = 0;
for (long i = 1; i <= n; ) {
    long q = n / i, j = n / q;                   // i..j share quotient q
    sum += q * (j - i + 1);
    i = j + 1;
}
""",
            "`i++` becomes `i = n / (n / i) + 1`, and the addend is multiplied by the block length.",
            """
n / i takes fewer than 2√n distinct values, and the i that share one are contiguous. Adding
q once per block, weighted by the block's length, sums the same terms — just not one at a
time. At n = 10¹² that is 2 × 10⁶ steps instead of 10¹².
"""),
        _rw("An inverse modulo a composite",
            """
// Fermat — correct ONLY when m is prime
long inv = power(a, m - 2, m);
""",
            """
// Extended Euclid — correct for any m, and says when there is no inverse
long r0 = a, r1 = m, s0 = 1, s1 = 0;
while (r1 != 0) {
    long q = r0 / r1, t;
    t = r0 - q * r1; r0 = r1; r1 = t;
    t = s0 - q * s1; s0 = s1; s1 = t;
}
long inv = (r0 != 1) ? -1 : ((s0 % m) + m) % m;
""",
            "`power(a, m − 2)` becomes the coefficient row of Euclid's loop.",
            """
Fermat's a^(p−2) relies on a^(p−1) ≡ 1, which holds for prime p. For m = 10, 3^8 mod 10 =
1, not 7 — the formula quietly returns a wrong number. Extended Euclid never assumes a
prime: it finds a·s + m·t = gcd(a, m), so it produces the inverse when gcd = 1 and detects
that there is none when gcd > 1.
"""),
    ],
    internals="""
### Why `long`, and exactly how far it goes

A Java `long` holds up to 2⁶³ − 1 ≈ 9.22 × 10¹⁸. That one number decides most of this unit:

| Quantity | Largest value | Fits in `long`? |
| --- | --- | --- |
| a product of two residues mod 10⁹ + 7 | ≈ 10¹⁸ | yes — which is why you reduce after **every** multiplication |
| a product of three residues | ≈ 10²⁷ | no |
| lcm of two values up to 10⁹ | 10¹⁸ | yes, if you divide first |
| a · b for a, b up to 10¹² | 10²⁴ | no — needs `Math.multiplyHigh`, halving multiplication, or `BigInteger` |

`Math.floorMod(a, m)` returns a non-negative remainder for negative a, which is the
`((a % m) + m) % m` idiom as a library call. `Math.multiplyExact` throws instead of
wrapping, which is a cheap way to find an overflow while testing.

### Why Euclid is fast

Each two steps at least halve the larger number: if b ≤ a/2 then a mod b < b ≤ a/2, and if
b > a/2 then a mod b = a − b < a/2. So the loop runs at most 2 log₂ min(a, b) times —
about 60 for 64-bit values. The worst case is two consecutive Fibonacci numbers (Lamé's
theorem), where every quotient is 1.

### How many primes there are

The prime-number theorem: about n / ln n primes below n. So 78,498 primes below 10⁶,
50,847,534 below 10⁹, and the gap between consecutive primes near n averages ln n ≈ 28
at 10¹². That is why a segmented sieve over a window of 10⁶ numbers near 10¹² finds
about 36,000 primes, and why "the next prime after n" is found quickly by testing.

### `BigInteger`, when you need it

`BigInteger.valueOf(a).modInverse(BigInteger.valueOf(m))`, `.modPow(e, m)`,
`.isProbablePrime(30)` and `.gcd(...)` all exist. They are the right tool for checking your
own implementation and for numbers beyond 64 bits; they are 10–100 times slower than the
`long` versions, and an interviewer will usually want to see the loop.
""",
    build_it="""
### A number-theory toolkit, tested against brute force

Write one class, `NT`, with static methods, and a `main` that checks each one against the
slowest correct version on every input up to a few thousand.

**1. `isPrime(long n)`** by trial division. Check it against "count divisors == 2".

**2. `factor(long n)` → a map from prime to exponent.** Check that the product of pᵉ
equals n, and that every key passes `isPrime`.

**3. `sieve(int n)` and `spf(int n)`.** Check `sieve` against `isPrime` for every value,
and check that `spf[x]` divides x and is prime.

**4. `gcd`, `lcm`, `extGcd(a, b)` → {g, x, y}.** Check a·x + b·y == g, and compare g with
`BigInteger.gcd`.

**5. `inverse(a, m)`** via `extGcd`. Check a·inv % m == 1, or that gcd(a, m) > 1 when it
returns −1. Then compare with `BigInteger.modInverse` (which throws when none exists).

**6. `power(b, e, m)`** by squaring. Compare with `BigInteger.modPow` for random e up to
10¹⁸.

**7. `crt(a1, m1, a2, m2)`.** Brute force: step through a1, a1 + m1, … up to lcm and
compare.

**8. `phi(n)` and `floorSum(n)`.** Brute force both by definition for n ≤ 2000.

Keep the file. It is a snippet library for every contest problem that follows.
""",
    skeletons=[
        _sk("Extended Euclid (iterative)",
            "Inverse modulo any m; Bézout coefficients.",
            """
static long inverse(long a, long m) {          // -1 if gcd(a, m) != 1
    long r0 = a, r1 = m, s0 = 1, s1 = 0;
    while (r1 != 0) {
        long q = r0 / r1, t;
        t = r0 - q * r1; r0 = r1; r1 = t;
        t = s0 - q * s1; s0 = s1; s1 = t;
    }
    return r0 != 1 ? -1 : ((s0 % m) + m) % m;
}
""",
            "Every row satisfies r ≡ a·s (mod m); when r reaches the gcd, s is the answer."),
        _sk("Smallest-prime-factor sieve",
            "Factorise many numbers up to M.",
            """
int[] spf = new int[M + 1];
for (int i = 2; i <= M; i++)
    if (spf[i] == 0)
        for (int j = i; j <= M; j += i)
            if (spf[j] == 0) spf[j] = i;

// factor x: while (x > 1) { int p = spf[x]; x /= p; ... }
""",
            "The first prime to reach j is its smallest factor."),
        _sk("Chinese remainder, two congruences",
            "x ≡ a1 (mod m1), x ≡ a2 (mod m2).",
            """
static long crt(long a1, long m1, long a2, long m2) {
    long g = gcd(m1, m2), diff = a2 - a1;
    if (diff % g != 0) return -1;
    long M = m2 / g;
    long t = ((diff / g) % M + M) % M * inverse((m1 / g) % M, M) % M;
    return a1 + m1 * t;                          // unique modulo lcm(m1, m2)
}
""",
            "Handle M == 1 (m2 divides m1): then t = 0."),
        _sk("Divisor blocks",
            "Σ over i of something depending only on n / i.",
            """
for (long i = 1; i <= n; ) {
    long q = n / i, j = n / q;       // i..j all give quotient q
    total += q * (j - i + 1);
    i = j + 1;
}
""",
            "Fewer than 2√n iterations."),
    ],
    signals=[
        _sig("“modulo m” where m is **not** prime, and a division", "Extended Euclid inverse",
             "Fermat's x^(m−2) is only valid for prime m."),
        _sig("“factorise each of these 10⁵ numbers”", "Smallest-prime-factor sieve",
             "O(log x) per number after one sieve."),
        _sig("“how many k ≤ n with gcd(k, n) = 1”", "Euler's totient",
             "Only the distinct primes of n matter."),
        _sig("“primes between L and R”, R near 10¹²", "Segmented sieve",
             "Primes to √R cross out every composite in the window."),
        _sig("“when do the two schedules coincide?”", "Chinese remainder theorem",
             "Merge two congruences into one modulo the lcm."),
        _sig("“Σ n / i for i = 1 … n”, n up to 10¹²", "Divisor blocks",
             "One step per distinct quotient."),
    ],
    costs=[
        _cost("Extended Euclid", "O(log m)", "O(1)", "Same steps as plain Euclid."),
        _cost("SPF sieve, then factorise q numbers", "O(M log log M + q log M)", "O(M)", ""),
        _cost("Segmented sieve on [L, R]", "O((R − L) log log R + √R)", "O(√R + (R − L))", ""),
        _cost("Divisor blocks", "O(√n)", "O(1)", ""),
        _cost("CRT merge of two congruences", "O(log m)", "O(1)", ""),
    ],
    pitfalls=[
        _pit("The inverse is wrong only for some moduli",
             "Fermat's `power(a, m − 2)` was used with a composite m.",
             "Use extended Euclid, which also detects gcd(a, m) > 1."),
        _pit("The segmented sieve reports small primes as composite",
             "Crossing out started at the first multiple of p in the window, which is p itself when L ≤ p.",
             "Start at `max(p * p, (L + p - 1) / p * p)`."),
        _pit("The CRT answer is sometimes negative or too large",
             "`a2 − a1` was negative and `%` kept the sign, or t was not reduced modulo m2/g.",
             "Normalise with `((x % M) + M) % M` before multiplying."),
        _pit("Factorisation misses a large prime factor",
             "The loop stopped at √n and the leftover n > 1 was dropped.",
             "After the loop, `if (n > 1)` it is one more prime."),
    ],
    checks=[
        _chk("Why does an inverse of a modulo m exist exactly when gcd(a, m) = 1?",
             "If gcd = 1, extended Euclid gives a·x + m·y = 1, so a·x ≡ 1. If g = gcd > 1, "
             "every a·x − m·y is a multiple of g and can never be 1."),
        _chk("In the smallest-prime-factor sieve, why is the first prime to reach j its smallest factor?",
             "Primes are processed in increasing order, and each marks all its multiples; the "
             "first to reach j is the smallest prime that divides it."),
        _chk("Why does a segmented sieve only need primes up to √R?",
             "Every composite x ≤ R has a prime factor at most √x ≤ √R, so crossing out "
             "multiples of those primes removes every composite in the window."),
        _chk("How many distinct values does n / i take for i = 1 … n?",
             "Fewer than 2√n: at most √n for i ≤ √n, and for i > √n the value itself is below "
             "√n."),
        _chk("When does x ≡ a1 (mod m1), x ≡ a2 (mod m2) have a solution?",
             "Exactly when gcd(m1, m2) divides a2 − a1. Then the solution is unique modulo "
             "lcm(m1, m2)."),
    ],
    traces=[_t4_ext_euclid(), _t4_spf_sieve(), _t4_divisor_blocks()],
)


_D_BITS = dict(
    invariant=_inv(
        "In Kernighan's loop, **`count + bitCount(x)` equals the popcount of the original "
        "value**, and every iteration removes exactly one set bit.",
        "Before the loop count = 0 and x is the original value, so the sum is the popcount "
        "by definition.",
        "`x − 1` turns the lowest set bit into 0 and every 0 below it into 1, leaving higher "
        "bits alone. AND-ing with x keeps the higher bits (both have them) and zeroes the "
        "block (x has 0s where x − 1 has 1s, and vice versa). So exactly one set bit "
        "disappears while count goes up by one — the sum is unchanged.",
        "The loop stops at x = 0, where bitCount(x) = 0, so count is the popcount — after "
        "exactly popcount iterations, not 32.",
        "The XOR fold has the same shape: `acc` is always the XOR of the values seen an odd "
        "number of times so far. Pairs cancel as they complete, so at the end only the loner "
        "is left.",
    ),
    variants=[
        _var("Test / set / clear / toggle", "`(x >> i) & 1`, `x | 1 << i`, `x & ~(1 << i)`, `x ^ 1 << i`.",
             "An int as a set of up to 32 flags.", "O(1)",
             "`1L << i` once i can reach 32."),
        _var("XOR fold", "Accumulate `acc ^= v` over the array.",
             "The unpaired value; the missing number.", "O(n), O(1) space",
             "Cancels pairs only: a triple leaves a copy behind."),
        _var("XOR split", "Fold, then split everything by one set bit of the result.",
             "Two unknowns: two singles, or missing + duplicate.", "O(n), O(1) space",
             "Any set bit works; `x & -x` is the easiest to get."),
        _var("Lowest bit", "`x & -x` isolates it; `x & (x − 1)` clears it.",
             "Popcount loops, power-of-two tests, Fenwick trees.", "O(1)",
             "0 passes `(x & (x − 1)) == 0`: guard x > 0."),
        _var("Popcount DP", "`dp[i] = dp[i >> 1] + (i & 1)`.",
             "Bit counts for every i ≤ n.", "O(n)",
             "For the *sum* over 1…n with huge n, count per bit position instead."),
        _var("All subsets", "`for (mask = 0; mask < 1 << n; mask++)`.",
             "Brute force over subsets, n ≤ 20.", "O(2ⁿ · n), or O(2ⁿ) built from `mask & (mask − 1)`",
             "n = 30 is a billion masks — too many."),
        _var("All submasks", "`for (sub = mask; sub > 0; sub = (sub − 1) & mask)`.",
             "DP over subsets of a subset.", "O(3ⁿ) over all masks",
             "The empty submask is not visited by that loop — handle it separately."),
        _var("Same-size subsets in order", "Gosper's hack: `c = x & −x; r = x + c; x = r | ((x ^ r) >> 2) / c`.",
             "Every k-subset of n, in increasing order.", "O(C(n, k))",
             "Stop when x reaches 1 << n."),
        _var("Per-bit contribution", "Count ones per bit; combine counts instead of elements.",
             "Σ of pair XOR / AND / OR, total set bits over 1…n.", "O(n · B)",
             "The totals get large: multiply in long."),
        _var("Greedy from the top bit", "Try to set bit b of the answer, from high to low; keep it if achievable.",
             "Maximum AND pair, maximum XOR (with a trie).", "O(n · B)",
             "Test the whole candidate `res | 1 << b`, not bit b alone."),
        _var("Prefix XOR", "`P[i] = a[0] ^ … ^ a[i − 1]`; range XOR = P[r + 1] ^ P[l].",
             "Range XOR queries, subarrays with XOR k.", "O(n) build, O(1) query",
             "XOR of 0…n has period 4 — no array needed for consecutive integers."),
    ],
    rewrites=[
        _rw("Count set bits: one iteration per 1, not per bit",
            """
int count = 0;
for (int i = 0; i < 32; i++)
    if (((x >> i) & 1) == 1) count++;
""",
            """
int count = 0;
while (x != 0) {
    x &= x - 1;          // clears the lowest set bit
    count++;
}
""",
            "The 32-step scan becomes a loop that clears one set bit per iteration.",
            """
The scan examines every position, set or not. `x & (x − 1)` jumps straight from one set bit
to the next, so the loop runs popcount(x) times. (For negative x, `x != 0` still terminates:
the sign bit is cleared like any other.) `Integer.bitCount` does it in one instruction.
"""),
        _rw("The loner: a hash map becomes one accumulator",
            """
Map<Integer, Integer> freq = new HashMap<>();
for (int v : a) freq.merge(v, 1, Integer::sum);
for (var e : freq.entrySet())
    if (e.getValue() == 1) return e.getKey();
""",
            """
int acc = 0;
for (int v : a) acc ^= v;
return acc;
""",
            "The frequency map becomes `acc ^= v`.",
            """
XOR is associative and commutative with x ^ x = 0, so the order of the array does not
matter and every pair cancels. What the map did in O(n) space, one int does in O(1) —
but only because every other value appears an **even** number of times.
"""),
        _rw("Sum of pair XORs: count per bit, not per pair",
            """
long total = 0;
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        total += a[i] ^ a[j];
""",
            """
long total = 0;
for (int b = 0; b < 30; b++) {
    long ones = 0;
    for (int v : a) ones += (v >> b) & 1;
    total += ones * (n - ones) << b;
}
""",
            "The pair loop becomes a per-bit count of ones.",
            """
Bit b of a[i] ^ a[j] is set exactly when one of the two has it, and there are
ones · (n − ones) such pairs. Bits do not interact in XOR, so summing each bit's
contribution gives the same total as summing each pair — in 30n steps instead of n²/2.
"""),
        _rw("Subset sums: build each from a smaller mask",
            """
for (int mask = 0; mask < (1 << n); mask++) {
    long s = 0;
    for (int i = 0; i < n; i++)
        if ((mask >> i & 1) == 1) s += price[i];
    use(s);
}
""",
            """
long[] sum = new long[1 << n];
for (int mask = 1; mask < (1 << n); mask++) {
    sum[mask] = sum[mask & (mask - 1)] + price[Integer.numberOfTrailingZeros(mask)];
    use(sum[mask]);
}
""",
            "The inner loop over bits becomes one lookup of `mask & (mask − 1)`.",
            """
`mask & (mask − 1)` is mask without its lowest element, and it is a smaller number, so its
sum was already computed when the loop reaches mask. The 2ⁿ · n recomputation becomes 2ⁿ
additions — the first recurrence of bitmask DP.
"""),
        _rw("XOR of a range: a formula, not a loop",
            """
long x = 0;
for (long v = l; v <= r; v++) x ^= v;     // up to 10^18 steps
""",
            """
static long f(long n) {                     // XOR of 0..n
    long[] cycle = {n, 1, n + 1, 0};
    return n < 0 ? 0 : cycle[(int) (n & 3)];
}
long x = f(r) ^ f(l - 1);
""",
            "The loop becomes two lookups in the period-4 pattern of prefix XORs.",
            """
2k ^ (2k + 1) = 1 for every k, so XOR(0..n) is built from pairs that each contribute a 1,
and two 1s cancel. That leaves four cases by n mod 4, and XOR's self-inverse property turns
the range into a difference of two prefixes, exactly as with sums.
"""),
    ],
    internals="""
### Two's complement

A Java `int` is 32 bits, and a negative value −x is stored as `~x + 1`. So −1 is 32 ones,
`Integer.MIN_VALUE` is a 1 followed by 31 zeros, and `-x` has the same lowest set bit as x
— which is why `x & -x` isolates it.

| Expression | Bits (8-bit view) |
| --- | --- |
| `x = 12` | `00001100` |
| `-x` | `11110100` |
| `x & -x` | `00000100` |
| `x - 1` | `00001011` |
| `x & (x - 1)` | `00001000` |

### Shifts

- `<<` shifts in zeros at the bottom. It can push a 1 into the sign bit: `1 << 31` is
  `Integer.MIN_VALUE`.
- `>>` is **arithmetic**: it copies the sign bit into the vacated top bits, so −8 >> 1 is −4,
  and a negative number shifted right never reaches 0.
- `>>>` is **logical**: zeros come in at the top. Use it when the int is 32 raw bits.
- The shift count is taken **mod 32** for `int` (mod 64 for `long`): `1 << 32 == 1`,
  `1 << 33 == 2`. `1L << 40` is what you meant.

### What the JVM gives you

`Integer.bitCount`, `numberOfTrailingZeros`, `numberOfLeadingZeros`, `highestOneBit`,
`lowestOneBit` and `reverse` are **intrinsics**: the JIT compiles them to a single CPU
instruction (POPCNT, TZCNT, LZCNT). Use them in contest code; write the loops once so you
know what they do.

`java.util.BitSet` is a growable `long[]` with set operations (`and`, `or`, `xor`,
`cardinality`, `nextSetBit`). It is the right tool for a set of more than 64 flags — a sieve
over 10⁸ in 12.5 MB, for example, where a `boolean[]` would take 100 MB.

### Masks beyond 32

A `long` holds 64 flags. Beyond that, use a `long[]` (or `BitSet`) and index bit i as
`words[i >> 6] >> (i & 63) & 1`.
""",
    build_it="""
### A `Bits` utility class and a brute-force tester

**1. The four idioms** — `get(x, i)`, `set`, `clear`, `toggle` — for `long`, so i can reach
63. Test each against `BigInteger.testBit/setBit/clearBit/flipBit`.

**2. `popcount` three ways**: shifting 64 times, Kernighan, and `Long.bitCount`. Run all
three on a million random longs, including negative ones, and assert they agree.

**3. `lowestBit(x) = x & -x` and `clearLowest(x) = x & (x - 1)`.** Assert that
`clearLowest(x) + lowestBit(x) == x` for every non-zero x.

**4. Subsets.** Write `forEachSubset(n)` and `forEachSubmask(mask)`, and count how many
(mask, submask) pairs the double loop visits for n = 1 … 12. It should be 3ⁿ.

**5. Gosper's hack.** Generate every k-subset of n with it, and compare against filtering
0 … 2ⁿ − 1 by `bitCount == k`, for all n ≤ 12 and k ≤ n.

**6. A 128-flag set** as a `long[2]`, with add / remove / contains / size / iterate-in-order
using `numberOfTrailingZeros`. Compare against a `TreeSet<Integer>`.
""",
    skeletons=[
        _sk("XOR split into two unknowns",
            "Two singles among pairs; missing plus duplicate.",
            """
int x = 0;
for (int v : a) x ^= v;              // = u ^ w, the two unknowns
int bit = x & -x;                    // a bit where u and w differ
int u = 0, w = 0;
for (int v : a) {
    if ((v & bit) != 0) u ^= v; else w ^= v;
}
""",
            "Every other value still meets its partner in the same bucket."),
        _sk("Enumerate submasks",
            "DP over subsets of a subset.",
            """
for (int sub = mask; sub > 0; sub = (sub - 1) & mask) {
    // sub is a non-empty submask of mask, largest first
}
// the empty submask (0) is not visited — handle it separately
""",
            "3ⁿ in total when mask ranges over all 2ⁿ masks."),
        _sk("Gosper's hack",
            "Every k-element subset of {0 … n−1}, in order.",
            """
for (long x = (1L << k) - 1; x < (1L << n); ) {
    // use x
    long c = x & -x, r = x + c;
    x = (((r ^ x) >> 2) / c) | r;
}
""",
            "Needs k ≥ 1."),
        _sk("Per-bit contribution",
            "Sum of pair XORs (or ANDs, ORs) over all pairs.",
            """
long total = 0;
for (int b = 0; b < 30; b++) {
    long ones = 0;
    for (int v : a) ones += (v >> b) & 1;
    total += ones * (n - ones) << b;      // XOR: exactly one of the pair has bit b
}
""",
            "AND: ones·(ones−1)/2. OR: all pairs minus the zeros·(zeros−1)/2 pairs."),
        _sk("Greedy bit by bit",
            "Maximise an AND (or build an answer) from the top bit.",
            """
int res = 0;
for (int b = 29; b >= 0; b--) {
    int cand = res | (1 << b), count = 0;
    for (int v : a) if ((v & cand) == cand) count++;
    if (count >= 2) res = cand;
}
""",
            "A higher bit outweighs every lower bit together."),
    ],
    signals=[
        _sig("“every value twice, two appear once” / “one missing, one repeated”", "XOR, then split by a differing bit",
             "Each bucket XORs down to one unknown."),
        _sig("“sum of a[i] ^ a[j] over all pairs”", "Per-bit contribution",
             "ones × zeros × 2ᵇ per bit."),
        _sig("“maximum AND of a pair”", "Greedy from the top bit",
             "Keep a candidate; at least two values must contain it."),
        _sig("“the next larger number with the same number of 1s”", "Gosper's hack",
             "Five word operations."),
        _sig("“XOR of all integers from l to r”", "Period-4 prefix XOR",
             "f(r) ^ f(l − 1)."),
        _sig("“total set bits in 1 … n”, n huge", "Count per bit position",
             "Bit b is a square wave of period 2^(b+1)."),
    ],
    costs=[
        _cost("XOR split", "O(n)", "O(1)", "Two passes."),
        _cost("Subset sums from `mask & (mask − 1)`", "O(2ⁿ)", "O(2ⁿ)", "Versus O(2ⁿ · n) recomputing."),
        _cost("All submasks of all masks", "O(3ⁿ)", "O(1)", ""),
        _cost("Per-bit contribution", "O(n · B)", "O(1)", "B = 30 or 64."),
        _cost("Gosper's hack, one step", "O(1)", "O(1)", ""),
    ],
    pitfalls=[
        _pit("The pair-XOR total is negative or wrong on large inputs",
             "`ones * (n - ones) << b` was computed in `int`.",
             "Make `ones` a long, so the whole product is long."),
        _pit("The greedy bit answer is too large",
             "Each bit was tested on its own, `(v >> b & 1)`, so two different pairs supplied different bits.",
             "Test the whole candidate: `(v & cand) == cand`."),
        _pit("Submask enumeration never visits the empty set, or loops forever",
             "`sub >= 0` as the condition cycles, because `(0 − 1) & mask` is mask again.",
             "Loop while `sub > 0`, and handle 0 after the loop."),
        _pit("Bit 31 or bit 32 behaves strangely",
             "An `int` mask: bit 31 is the sign bit, and `1 << 32` is 1.",
             "Use `long` masks and `1L << i`."),
    ],
    checks=[
        _chk("Why is the number of (mask, submask) pairs over n bits 3ⁿ?",
             "Each element is independently out of the mask, in the mask only, or in both — "
             "three choices per element."),
        _chk("Why does a set bit of dup ^ missing separate them?",
             "XOR is 1 exactly where the two differ, so at that bit one has a 1 and the other "
             "a 0, and they land in different buckets."),
        _chk("Why does XOR(0 … n) repeat with period 4?",
             "2k ^ (2k + 1) = 1, so the prefix is built from 1s that cancel in pairs; n mod 4 "
             "decides whether a pair is incomplete and whether an odd 1 is left over."),
        _chk("How many pairs have bit b set in their XOR?",
             "ones · (n − ones): one member with the bit and one without."),
        _chk("What does `x & -x` return, and why?",
             "The lowest set bit of x. In two's complement −x = ~x + 1: the + 1 carries up to "
             "x's lowest 1, so x and −x agree there and disagree everywhere above it."),
    ],
    traces=[_t4_kernighan(), _t4_gosper(), _t4_submasks(), _t4_xor_split()],
)


_D_GRID = dict(
    invariant=_inv(
        "In a spiral traversal with boundaries `top, bot, left, right`, **every cell outside "
        "the rectangle `[top..bot] × [left..right]` has been emitted exactly once, in spiral "
        "order, and no cell inside it has.**",
        "Initially the rectangle is the whole grid and nothing has been emitted.",
        "Walking the top row from `left` to `right` emits exactly the rectangle's top row; "
        "`top++` then removes that row from the rectangle. The right, bottom and left edges "
        "do the same for a column, a row and a column. The guards `if (top <= bot)` and "
        "`if (left <= right)` matter because after the first two edges the rectangle may "
        "already be empty — walking an edge of an empty rectangle would emit cells that are "
        "outside it, a second time.",
        "The loop ends when `top > bot` or `left > right`: the rectangle is empty, so every "
        "cell has been emitted exactly once.",
        "The simultaneous-update rule is the other invariant of this unit: while generation "
        "t + 1 is being written, **every read hits generation t**. A copy grid makes it true "
        "by construction; an in-place encoding makes it true by keeping the old state in "
        "bits the update does not overwrite.",
    ),
    variants=[
        _var("Direction array", "`int[][] D = {{-1,0},{1,0},{0,-1},{0,1}}` and a bounds check.",
             "Robots, neighbour counts, every grid BFS.", "O(1) per step",
             "Bounds before the read."),
        _var("Copy, then swap", "Write generation t + 1 into a fresh grid.",
             "Game of Life, image smoothing — any “all cells at once”.", "O(r · c) time and space",
             "Allocate once and swap references, not a new grid per step."),
        _var("Two states per cell", "Keep old and new in one int (old in bit 0, new in bit 1).",
             "The same rules in O(1) extra space.", "O(r · c), O(1)",
             "Read `& 1` during the pass, then `>>= 1` everything at the end."),
        _var("Transpose + reverse", "Rotation as two simple permutations.",
             "Rotate 90°, flip, transpose.", "O(n²), in place for square grids",
             "Transpose only `j > i`."),
        _var("Ring walk", "Four edges, each stopping one short of its last corner.",
             "Spiral order, ring rotation, layer-by-layer processing.", "O(r · c)",
             "A single-row or single-column rectangle needs the guards."),
        _var("Diagonal keys", "Group cells by `i − j` (↘) or `i + j` (↙).",
             "Toeplitz checks, diagonal traversal, N-Queens attacks.", "O(r · c)",
             "`i − j` can be negative: offset by `c − 1` to use it as an index."),
        _var("Compaction (gravity)", "A write pointer per row or column, reset at each wall.",
             "Tilts, falling blocks, move-zeroes in 2-D.", "O(r · c) per tilt",
             "Clear the old cell before writing the new one."),
        _var("Structure per question", "A deque for order, a set for membership, a map for counts.",
             "Snake, queues of robots, anything that asks “is this cell taken?”.", "O(1) per step",
             "Encode a cell as `i * c + j` for hashing."),
        _var("Cycle detection", "Map each state to the step it was first seen; skip whole cycles.",
             "The state after 10⁹ or 10¹⁸ steps.", "O(number of states)",
             "The pre-period (steps before the cycle starts) is not part of the cycle."),
        _var("Array rotation", "Three reversals, after `k %= n`.",
             "Cyclic shifts of a row or of a flattened ring.", "O(n), O(1) space",
             "Normalise k first."),
    ],
    rewrites=[
        _rw("Rotate 90°: two simple steps instead of one hard formula",
            """
// derive where (i, j) goes, under pressure
int[][] b = new int[n][n];
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        b[j][n - 1 - i] = a[i][j];
""",
            """
for (int i = 0; i < n; i++)                     // transpose
    for (int j = i + 1; j < n; j++) {
        int t = a[i][j]; a[i][j] = a[j][i]; a[j][i] = t;
    }
for (int[] row : a)                             // reverse each row
    for (int l = 0, r = n - 1; l < r; l++, r--) {
        int t = row[l]; row[l] = row[r]; row[r] = t;
    }
""",
            "The copy through one index formula becomes transpose-then-reverse, in place.",
            """
Both are correct; the difference is which one you can reproduce without a mistake and in
O(1) extra space. (i, j) → (j, i) → (j, n − 1 − i) is the composition, so the result is the
same clockwise rotation. Counter-clockwise is transpose then reverse each *column* — or
reverse the rows first.
"""),
        _rw("Rotating a ring by k: one shift, not k steps",
            """
for (int step = 0; step < k; step++) {         // k up to 10^9
    int first = ring[0];
    for (int p = 0; p + 1 < L; p++) ring[p] = ring[p + 1];
    ring[L - 1] = first;
}
""",
            """
int s = (int) (k % L);
int[] out = new int[L];
for (int p = 0; p < L; p++) out[p] = ring[(p + s) % L];
""",
            "The k single steps become one shift by `k mod L`.",
            """
After L single steps every value is back where it started, so only k mod L steps matter —
and a shift by s is one pass that reads index p + s. O(k · L) becomes O(L).
"""),
        _rw("Too many steps: find the cycle",
            """
for (long t = 0; t < n; t++)                   // n up to 10^18
    state = step(state);
""",
            """
Map<Integer, Long> seen = new HashMap<>();
for (long t = 0; t < n; t++) {
    Long first = seen.put(state, t);
    if (first != null) {                       // state repeated: cycle of length t - first
        long left = (n - t) % (t - first);
        for (long i = 0; i < left; i++) state = step(state);
        return state;
    }
    state = step(state);
}
return state;
""",
            "The straight loop gains a `seen` map and a jump over whole cycles.",
            """
With S possible states, some state repeats within S + 1 steps, and from then on the
sequence is periodic. Stepping (n − t) mod (cycle length) more times lands on the same
state as stepping all the way to n. O(n) becomes O(S).
"""),
        _rw("Gravity: one compaction pass, not step-by-step falling",
            """
boolean moved = true;
while (moved) {                                 // repeat until stable
    moved = false;
    for (int i = 0; i < r; i++)
        for (int j = 1; j < c; j++)
            if (g[i][j] == 'O' && g[i][j - 1] == '.') {
                g[i][j - 1] = 'O'; g[i][j] = '.'; moved = true;
            }
}
""",
            """
for (int i = 0; i < r; i++) {
    int free = 0;
    for (int j = 0; j < c; j++) {
        if (g[i][j] == '#') free = j + 1;
        else if (g[i][j] == 'O') { g[i][j] = '.'; g[i][free++] = 'O'; }
    }
}
""",
            "Repeated one-cell moves become one write-pointer pass per row.",
            """
Stones never pass each other or a wall, so their final order within a segment is their
starting order, packed against the segment's left end. The write pointer places each one
directly. The repeated version can take c passes over the whole grid.
"""),
        _rw("“Is this cell on the snake?”: a set, not a scan",
            """
for (int[] part : body)                         // O(length) per move
    if (part[0] == hi && part[1] == hj) return dead;
""",
            """
if (!occupied.add(hi * c + hj)) return dead;    // O(1) per move
""",
            "The scan over the body becomes a hash-set membership test, kept in sync with the deque.",
            """
The body is needed in order (for the tail) and as a set (for collisions), so keep both —
the deque and the set change by one element at each end per move. A snake of length 10⁵
over 10⁵ moves is 10¹⁰ steps scanned and 10⁵ hashed.
"""),
    ],
    internals="""
### Row-major layout, and why loop order matters

A Java `int[][]` is an array of references to separate row arrays. Each row is contiguous
in memory; different rows are not. So

```java
for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) sum += a[i][j];   // fast
for (int j = 0; j < c; j++) for (int i = 0; i < r; i++) sum += a[i][j];   // slow
```

do the same arithmetic, but the second touches a different row — often a different cache
line — on every step. On a 4000 × 4000 grid the difference is several times. Put the row
index outside.

### `int[][]` is jagged, and `clone()` is shallow

Rows can have different lengths (`new int[3][]`, then assign each row), which is how
Pascal's triangle is stored. And `a.clone()` copies the array of *row references*: the
clone shares its rows with the original, so writing into the "copy" corrupts the original.
A real copy clones each row: `int[][] b = new int[r][]; for (i) b[i] = a[i].clone();` —
the bug behind many "my simultaneous update still reads new values" reports.

### Flattening

Cell (i, j) of an r × c grid is index `i * c + j` of a flat array, and back again with
`i = id / c, j = id % c`. A flat `int[]` is one allocation, cache-friendly, and makes a cell
a single `int` — hashable, storable in a queue, comparable. Every BFS over a grid in stage 6
can use it.

### Transformations as index maps

| Transformation | (i, j) goes to | New shape |
| --- | --- | --- |
| Transpose | (j, i) | c × r |
| Rotate 90° clockwise | (j, r − 1 − i) | c × r |
| Rotate 90° counter-clockwise | (c − 1 − j, i) | c × r |
| Rotate 180° | (r − 1 − i, c − 1 − j) | r × c |
| Flip left–right | (i, c − 1 − j) | r × c |

Each is a composition of transpose and flips — which is why the in-place square rotation is
"transpose, then reverse each row".
""",
    build_it="""
### A `Grid` helper, property-tested

Write a small class over `int[][]` and a `main` that checks each property on 1,000 random
grids of random shapes (including 1 × 1, 1 × n and n × 1):

**1. `neighbours(i, j, eight)`** returning only in-bounds cells. Property: a corner has 2
(or 3), an edge cell 3 (or 5), an interior cell 4 (or 8).

**2. `transpose`, `rotateCW`, `rotateCCW`, `flipLR`.** Properties: transposing twice is the
identity; four clockwise rotations are the identity; `rotateCW` then `rotateCCW` is the
identity; `rotateCW == flipLR ∘ transpose`.

**3. `rotateInPlace` for square grids** (transpose + reverse). Property: equals `rotateCW`.

**4. `spiral`** returning the cells in spiral order. Properties: every cell exactly once;
the first row comes out first; on a 1 × n grid it is the row itself.

**5. `rotateRings(k)`.** Properties: k = ring length is the identity; k and k + L give the
same result; rotating by k then by L − k is the identity.

**6. `flatten`/`unflatten`.** Property: round trip is the identity, and `id = i * c + j`.

**7. `stepUntilRepeat(state, step)`** — generic cycle detection. Test it on the lamp rule
against a direct loop for n ≤ 1000.
""",
    skeletons=[
        _sk("Ring walk",
            "Visit ring t of an r × c grid, clockwise, each cell once.",
            """
int top = t, left = t, bot = r - 1 - t, right = c - 1 - t;
for (int j = left; j < right; j++) visit(top, j);     // →, stop before the corner
for (int i = top; i < bot; i++)    visit(i, right);   // ↓
for (int j = right; j > left; j--) visit(bot, j);     // ←
for (int i = bot; i > top; i--)    visit(i, left);    // ↑
""",
            "Assumes the ring is a real rectangle (top < bot and left < right)."),
        _sk("Cycle detection with a jump",
            "The state after a huge number of steps.",
            """
Map<State, Long> seen = new HashMap<>();
for (long t = 0; t < n; t++) {
    Long first = seen.put(state, t);
    if (first != null) {
        long left = (n - t) % (t - first);
        while (left-- > 0) state = step(state);
        return state;
    }
    state = step(state);
}
return state;
""",
            "State must have value equality — encode it as an int, long or String."),
        _sk("Compaction toward a wall",
            "Tilting, gravity, pushing tokens to one side.",
            """
int free = 0;                                   // next cell a stone can reach
for (int j = 0; j < c; j++) {
    if (row[j] == '#') free = j + 1;
    else if (row[j] == 'O') { row[j] = '.'; row[free++] = 'O'; }
}
""",
            "Clear first, then write — the two cells may be the same."),
        _sk("Diagonal keys",
            "Group cells by diagonal.",
            """
// ↘ diagonals: i - j in [-(c-1), r-1]    ↙ diagonals: i + j in [0, r+c-2]
List<List<Integer>> down = new ArrayList<>();
for (int d = 0; d < r + c - 1; d++) down.add(new ArrayList<>());
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++)
        down.get(i - j + c - 1).add(g[i][j]);   // offset so the key is an index
""",
            "A cell's predecessor on its ↘ diagonal is (i − 1, j − 1)."),
    ],
    signals=[
        _sig("“rotate each ring / layer by k”", "Flatten the ring, shift by k mod its length",
             "A ring is a cyclic array."),
        _sig("“every diagonal is constant”, “diagonal order”", "Key cells by i − j or i + j",
             "Or compare each cell with its diagonal predecessor."),
        _sig("“tilt”, “stones roll”, “gravity”", "Compaction with a write pointer",
             "One pass per row or column."),
        _sig("“the state after 10¹⁸ steps”", "Cycle detection",
             "A finite state space must repeat."),
        _sig("“snake”, “occupied cells change at both ends”", "A deque plus a hash set",
             "Order and membership, both O(1)."),
    ],
    costs=[
        _cost("Ring rotation by k", "O(r · c)", "O(r · c)", "Independent of k."),
        _cost("Tilt (one direction)", "O(r · c)", "O(1)", "A compaction per row or column."),
        _cost("Cycle detection over S states", "O(S)", "O(S)", "Then O(cycle) to finish."),
        _cost("Snake simulation", "O(moves)", "O(length)", "Deque plus hash set."),
        _cost("Diagonal check", "O(r · c)", "O(1)", "Each cell against its predecessor."),
    ],
    pitfalls=[
        _pit("A ring rotation goes the wrong way",
             "The shift read index `p − s` instead of `p + s` (or the ring was walked counter-clockwise).",
             "Test a 2 × 2 grid with k = 1 by hand before trusting the formula."),
        _pit("Corner cells are duplicated or lost in a ring walk",
             "Each edge ran to its last corner inclusive, so the next edge started on the same cell.",
             "Stop every edge one short of its final corner."),
        _pit("A tilt deletes stones",
             "The new cell was written before the old one was cleared, and they were the same cell.",
             "Clear first, then write."),
        _pit("The cycle-detection answer is off by the pre-period",
             "The skip used n mod cycle rather than (n − t) mod cycle.",
             "Count the remaining steps from the moment the repeat was found."),
        _pit("The snake dies chasing its own tail",
             "The head was checked against the body before the tail moved.",
             "When not eating, remove the tail first, then test the head."),
        _pit("A “copy” of the grid changes with the original",
             "`grid.clone()` copied only the row references.",
             "Clone each row: `b[i] = a[i].clone()`."),
    ],
    checks=[
        _chk("Why does a deterministic process on a finite set of states eventually cycle?",
             "With S states, S + 1 steps must visit some state twice (pigeonhole), and from a "
             "repeated state the future is identical."),
        _chk("How do you rotate a ring of length L by k when k is 10⁹?",
             "Shift once by k mod L: position p takes the value from position (p + s) mod L."),
        _chk("Why is the row index the outer loop when scanning a Java 2-D array?",
             "Each row is a contiguous array; walking along a row uses consecutive memory, "
             "while walking down a column jumps between separate arrays."),
        _chk("What is the cell id of (i, j) in an r × c grid, and back?",
             "id = i · c + j; i = id / c, j = id % c. Use the column count, not the row count."),
        _chk("Why must the snake remove its tail before checking the head?",
             "The tail moves on the same step, so the cell it leaves is free for the head. "
             "Checking first would kill a snake that is legally following its tail."),
    ],
    traces=[_t4_spiral(), _t4_tilt_row(), _t4_lamp_cycle()],
)


# ================================================================== the ladders
#
# Rebuilt rather than edited: the syllabus and placement files have moved
# problems into these units over several rounds, so the stage file's rungs no
# longer describe them. Every slug the units held before is asserted to be
# somewhere below, so a problem cannot fall off a ladder unnoticed.

_S4_NEW_NOTES = {
    # number theory — the 7 new problems
    "prime-factorization": "Trial division that keeps dividing: each factor comes out completely, and whatever is left above 1 is one last prime.",
    "divisor-count-queries": "The sieve, remembering *which* prime crossed each number out — then every factorisation is a chain of lookups.",
    "coprime-count": "φ(n) from the distinct primes: `result -= result / p`. Exponents do not matter.",
    "inverse-mod-any": "Extended Euclid. The inverse exists exactly when gcd(a, m) = 1, and the same loop tells you which.",
    "two-clocks-align": "The Chinese remainder theorem with moduli that share a factor. Check that gcd divides the difference, then solve for t modulo m2/g.",
    "primes-in-window": "A segmented sieve: the primes up to √R cross out every composite in the window. Start at max(p², first multiple ≥ L).",
    "floor-quotient-sum": "Group i by the value of n / i. The same √n argument as divisor pairs, applied to quotients.",
    # number theory — problems that had no note
    "is-multiple": "One `%`. The on-ramp: divisibility is the whole unit's vocabulary.",
    "gcd": "Euclid in three lines, and the proof that it stops in O(log n) steps.",
    # bits — the 8 new problems
    "light-panel": "An int as 32 switches: set, clear, toggle and test, and bit 31 is the sign bit.",
    "range-xor": "Prefix XOR, like a prefix sum — and XOR of 0…n has period 4, so no array is needed.",
    "set-bits-up-to-n": "Count per bit position, not per number: bit b is a square wave of period 2^(b+1).",
    "next-same-popcount": "Gosper's hack. Walk it on paper once; it is how k-subsets are enumerated in order.",
    "budget-subsets": "Every subset as a mask, each sum built from `mask & (mask − 1)` — the first bitmask recurrence.",
    "missing-and-duplicate": "XOR leaves dup ^ missing. Split everything by a bit where they differ.",
    "pair-xor-total": "The contribution technique: ones × zeros × 2ᵇ per bit, no pair ever formed.",
    "max-and-pair": "Decide the answer's bits from the top, testing the whole candidate each time.",
    # bits — problems that had no note
    "power-of-two": "`x > 0 && (x & (x − 1)) == 0`. The guard is the question.",
    "single-number": "XOR everything. Say *why* it works — commutative, associative, x ^ x = 0 — before you type it.",
    # grids — the 7 new problems
    "transpose-matrix": "(i, j) → (j, i), and the result has the other shape. The on-ramp to every rotation.",
    "diagonal-sums": "Diagonals are equations: i == j and i + j == n − 1. Count the centre once.",
    "striped-wallpaper": "“Every diagonal constant” is the same as “every cell equals its up-left neighbour”.",
    "rotate-rings": "Each ring is a cyclic array: flatten it, shift by k mod its length, write it back.",
    "tilt-the-board": "Gravity is a compaction with a write pointer. Clear the old cell before writing the new one.",
    "snake-on-grid": "A deque for the body and a set for collisions — and the tail moves before the head is checked.",
    "lamp-row-after-days": "10¹⁸ nights over at most 2¹⁶ states: remember when each state was seen, and jump.",
    # grids — problems that had no note
    "rock-paper-scissors": "A rule table. Write the cases out before the `if`s.",
    "traffic-light": "A state machine with a cycle — the simplest version of the lamp problem at the end of this unit.",
    "color-bomb-explosion": "Neighbour scan on a grid; decide every cell from the *old* board.",
    "territory-capture": "Counting cells by a rule over their neighbours. Bounds before access.",
    "rotate-array-right": "Three reversals, after normalising k — the 1-D version of rotating a ring.",
    "rotate-matrix-90": "Transpose, then reverse each row. Two simple steps beat one index formula.",
    "spiral-order": "Four shrinking boundaries, and the two guards that stop a single row being emitted twice.",
}

_S4_LADDERS = {
    "math-number-theory": [
        ("Warm up", "Divisors, one number at a time.",
         ["count-divisors", "is-prime"], False),
        ("Core", "Euclid, and factorising by dividing as you go.",
         ["gcd", "prime-factorization"], False),
        ("Sieves", "Every prime below n, crossed out once.",
         ["count-primes"], False),
        ("Counting modulo a prime", "Huge counts kept exact: reduce, power, invert.",
         ["power-mod", "ncr-mod-queries"], False),
        ("Inverses and congruences", "Division modulo any m, and two cycles lining up.",
         ["inverse-mod-any", "two-clocks-align"], False),
        ("Beyond √n", "Sieves that remember, sieves over windows, and sums grouped by quotient.",
         ["divisor-count-queries", "coprime-count", "primes-in-window", "floor-quotient-sum"], True),
        ("Extra practice", "More divisibility and modular counting — more reps, no new idea.",
         None, True),
    ],
    "bit-manipulation": [
        ("Warm up", "Read and write single bits.",
         ["light-panel", "number-of-1-bits", "power-of-two"], False),
        ("Core", "XOR as a cancelling accumulator.",
         ["single-number", "missing-number"], False),
        ("Masks as sets", "Every subset as a number, each built from a smaller one.",
         ["budget-subsets", "count-bits"], False),
        ("Bit by bit", "Split by a bit, count per bit, decide bit by bit.",
         ["single-number-iii", "pair-xor-total"], False),
        ("More bit tricks", "Formulas and hacks that replace loops.",
         ["range-xor", "set-bits-up-to-n", "next-same-popcount", "missing-and-duplicate",
          "max-and-pair"], True),
        ("Extra practice", "More of the same operators on new prompts.",
         None, True),
    ],
    "simulation-and-matrix": [
        ("Warm up", "Index arithmetic, and a rule followed exactly.",
         ["transpose-matrix", "robot-grid-walk"], False),
        ("Core", "Neighbours and diagonals.",
         ["minesweeper-counts", "striped-wallpaper"], False),
        ("Variations", "Transform the whole structure without corrupting it.",
         ["rotate-array", "spiral-order", "rotate-rings"], False),
        ("Bigger machines", "Several rules at once, each with the right structure.",
         ["tilt-the-board"], False),
        ("Too many steps", "When the step count is 10¹⁸, the state space is the answer.",
         ["lamp-row-after-days"], False),
        ("More grids and machines", "Diagonals, longer rule sets and more state.",
         ["diagonal-sums", "snake-on-grid", "game-of-life-step", "valid-tic-tac-toe",
          "robot-bounded-in-circle", "set-matrix-zeroes"], True),
        ("Extra practice", "More index arithmetic, once you can already do index arithmetic.",
         None, True),
    ],
}


def _rebuild_s4_ladders():
    by_key = {u["key"]: u for u in _UNITS}
    for key, plan in _S4_LADDERS.items():
        u = by_key[key]
        before = [sl for r in u["rungs"] for sl in r["slugs"]]
        notes = {sl: n for r in u["rungs"] for sl, n in r["notes"].items()}
        named = {sl for _, _, slugs, _ in plan if slugs for sl in slugs}
        # The catch-all rung takes everything the unit held that no other rung names,
        # in the order the unit held it.
        rest = [sl for sl in before if sl not in named]
        rungs = []
        for title, purpose, slugs, optional in plan:
            slugs = list(slugs) if slugs is not None else rest
            if not slugs:
                continue
            rn = {}
            for sl in slugs:
                note = notes.get(sl) or _S4_NEW_NOTES.get(sl)
                assert note, f"{key}: {sl!r} has no rung note"
                rn[sl] = note
            rungs.append(_rung(title, purpose, slugs, rn, optional=optional))
        after = [sl for r in rungs for sl in r["slugs"]]
        lost = set(before) - set(after)
        assert not lost, f"{key}: the rebuilt ladder drops {sorted(lost)}"
        assert len(after) == len(set(after)), f"{key}: the rebuilt ladder repeats a problem"
        u["rungs"] = rungs


def _attach_s4_depth():
    by_key = {u["key"]: u for u in _UNITS}
    for key, d in (("math-number-theory", _D_MATH), ("bit-manipulation", _D_BITS),
                   ("simulation-and-matrix", _D_GRID)):
        u = by_key[key]
        u["invariant"] = d["invariant"]
        u["variants"].extend(d["variants"])
        u["rewrites"].extend(d["rewrites"])
        u["internals"] = _md(d["internals"])
        u["build_it"] = _md(d["build_it"])
        for field in ("skeletons", "signals", "costs", "pitfalls", "checks", "traces"):
            u[field].extend(d[field])
        u["bigo"].extend(_BIGO_S4[key])
    # Bits carries the representation every bitmask DP is built on, and now
    # enough problems to justify a weight-2 band.
    by_key["bit-manipulation"]["weight"] = 2


_attach_s4_depth()
_rebuild_s4_ladders()
