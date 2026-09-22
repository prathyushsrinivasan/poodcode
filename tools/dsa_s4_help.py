# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 4 (Numbers, Bits & Grids) — the help layer, the labs and the drills.
#
# exec'd by tools/dsa_curriculum.py after dsa_s4_depth.py, in the same
# namespace. Attaches, by unit key:
#
#   quizzes     spot-the-bug / predict-the-result drills (see `_quiz`)
#   stuck       triage for the moment before any code exists (see `_stuck`)
#   edge_cases  pasteable inputs worth testing before submitting (see `_edge`)
#   walkthrough one problem solved start to finish (see `_walk`)
#   lab         the interactive playground (see `_lab`)
#   drills      "work it out by hand" cards, typed and graded (see `_calc`)
#
# plus the stage cheat sheet and a "say it out loud" script appended to each
# unit's interview section.
#
# When these were authored, every quiz and drill answer was confirmed by
# executing a Python twin of it, and every edge-case input was run through its
# problem's reference solution. That was a one-off check, not a test — re-run
# it by hand when changing an answer.
# ---------------------------------------------------------------------------


# ========================================================== math & number theory

_H_MATH = dict(
    quizzes=[
        _quiz("bug",
              "`lcm(6_000_000_000L, 4_000_000_000L)` should be 12,000,000,000 and is not. Which change fixes it?",
              r"""
static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }

static long lcm(long a, long b) {
    return a * b / gcd(a, b);
}
""",
              "Divide first: `a / gcd(a, b) * b`",
              ["Divide first: `a / gcd(a, b) * b`",
               "Wrap the product in `Math.abs`",
               "Swap the arguments: `gcd(b, a)`",
               "Make `gcd` iterative"],
              """
`a * b` is 2.4 × 10¹⁹, past `Long.MAX_VALUE` ≈ 9.2 × 10¹⁸, so it wraps before the division
ever happens. The gcd divides `a` exactly, so `a / gcd(a, b)` loses nothing, and multiplying
by `b` afterwards produces only the answer — which fits.
"""),
        _quiz("bug",
              "`total` and `bad` are both already reduced modulo 10⁹ + 7, yet the printed answer is sometimes negative. Which change fixes it?",
              r"""
static final long MOD = 1_000_000_007L;

long good = (total - bad) % MOD;
System.out.println(good);
""",
              "`((total - bad) % MOD + MOD) % MOD`",
              ["`((total - bad) % MOD + MOD) % MOD`",
               "`Math.abs(total - bad) % MOD`",
               "Reduce `bad` again before subtracting",
               "Compute `good` in `int`"],
              """
Reduced values can be in either order: total = 3 and bad = 10 are both valid residues, and
3 − 10 = −7. Java's `%` keeps the sign of the left operand, so the result is −7, not
10⁹. Adding MOD before the final `%` lifts it into [0, MOD). `Math.abs` gives 7 — the wrong
residue.
"""),
        _quiz("bug",
              "With `n = 100_000` this throws `ArrayIndexOutOfBoundsException`. Which change fixes it?",
              r"""
boolean[] composite = new boolean[n];
int count = 0;
for (int i = 2; i < n; i++) {
    if (composite[i]) continue;
    count++;
    for (int j = i * i; j < n; j += i) composite[j] = true;
}
""",
              "Compute the start in `long`: `for (long j = (long) i * i; …)`",
              ["Compute the start in `long`: `for (long j = (long) i * i; …)`",
               "Start the inner loop at `j = 2 * i`",
               "Loop `i` only while `i * i < n`, still in `int`",
               "Allocate `new boolean[n + 1]`"],
              """
The first prime above 46,340 is 46,349, and 46,349² = 2,148,229,801 — past
`Integer.MAX_VALUE`. It wraps to a negative number, which passes `j < n`, and
`composite[negative]` throws. Doing the multiplication in `long` fixes it. Starting at `2 * i`
also avoids the overflow, but re-crosses numbers already crossed and is slower.
"""),
        _quiz("bug",
              "`power(1_000_000_000_000_000_000L, 2)` returns the wrong residue. Which change fixes it?",
              r"""
static final long MOD = 1_000_000_007L;

static long power(long b, long e) {
    long r = 1;
    for (; e > 0; e >>= 1, b = b * b % MOD)
        if ((e & 1) == 1) r = r * b % MOD;
    return r;
}
""",
              "Add `b %= MOD;` before the loop",
              ["Add `b %= MOD;` before the loop",
               "Use `e >>>= 1` instead of `e >>= 1`",
               "Reduce `r` once more before returning",
               "Start with `r = b`"],
              """
The first squaring computes (10¹⁸)², about 10³⁶, which overflows long completely. The
product of two values below MOD is below 10¹⁸ and fits — but only once the base has been
reduced. One `b %= MOD` at the top makes every later multiplication safe.
"""),
        _quiz("predict",
              "What does `inverse(4, 10)` return?",
              r"""
static long inverse(long a, long m) {
    long r0 = a, r1 = m, s0 = 1, s1 = 0;
    while (r1 != 0) {
        long q = r0 / r1, t;
        t = r0 - q * r1; r0 = r1; r1 = t;
        t = s0 - q * s1; s0 = s1; s1 = t;
    }
    return r0 != 1 ? -1 : ((s0 % m) + m) % m;
}
""",
              "`-1`",
              ["`-1`", "`3`", "`8`", "`0`"],
              """
The loop ends with r0 = gcd(4, 10) = 2, not 1. No x satisfies 4x ≡ 1 (mod 10): 4x is always
even, and every number ≡ 1 mod 10 is odd. The same loop that finds inverses also detects
their absence — Fermat's `4^8 mod 10` would return 6 and be silently wrong.
"""),
        _quiz("predict",
              "How many times does the loop body run for `n = 10`?",
              r"""
long sum = 0;
for (long i = 1; i <= n; ) {
    long q = n / i, j = n / q;
    sum += q * (j - i + 1);
    i = j + 1;
}
""",
              "5",
              ["5", "10", "3", "4"],
              """
The blocks are i = 1 (q = 10), 2 (q = 5), 3 (q = 3), 4…5 (q = 2) and 6…10 (q = 1) — five
distinct quotients, so five iterations. The sum is 10 + 5 + 3 + 4 + 5 = 27.
"""),
    ],
    stuck=[
        _stuck("A number up to 10¹² or 10¹⁸, and you cannot loop to it",
               "Is the question about its **divisors** (loop to √n) or its **digits / bits** (loop over log n positions)? Nothing sensible loops to n itself."),
        _stuck("Many numbers, each needing factorising or a primality test",
               "What is the largest value? Up to ~10⁷, sieve once and look answers up. Beyond that, √x per number, or a segmented sieve over the range you need."),
        _stuck("The answer is “huge, give it modulo p”",
               "Where does the count come from — a product, a sum, a binomial? Reduce after each operation; if there is a division, is p prime (Fermat) or not (extended Euclid)?"),
        _stuck("Two repeating schedules, and “when do they coincide?”",
               "Can you write each as x ≡ a (mod m)? Then it is the Chinese remainder theorem — check gcd(m1, m2) divides a2 − a1 first."),
        _stuck("A sum over i = 1 … n of something involving n / i",
               "How many different values does n / i take? Fewer than 2√n — group by the value."),
        _stuck("“How many numbers ≤ n are divisible by a or b?”",
               "Can you count each set with n / a and subtract the overlap n / lcm(a, b)? Inclusion–exclusion, with lcm computed dividing first."),
    ],
    edge_cases=[
        _edge("is-prime", "One is not prime", "1\n", "A primality test with no `n < 2` guard returns true."),
        _edge("count-divisors", "A perfect square", "36\n", "Counting d and n / d twice when d = 6: 10 instead of 9."),
        _edge("prime-factorization", "A prime above √n remains", "2000000014\n",
              "Stopping the loop at √n and forgetting the leftover factor 1000000007."),
        _edge("prime-factorization", "A large prime", "999999999989\n",
              "A loop to n instead of √n: 10¹² iterations and a timeout."),
        _edge("power-mod", "Base far above the modulus", "1000000000000000000 2\n",
              "Squaring the base before reducing it overflows long."),
        _edge("inverse-mod-any", "No inverse exists", "2\n4 10\n6 9\n",
              "Using Fermat's power(a, m − 2) with a composite m returns a number instead of −1."),
        _edge("two-clocks-align", "The moduli share a factor", "1 4 2 6\n",
              "Assuming coprime moduli: gcd = 2 does not divide 1, so there is no answer, not a wrong one."),
        _edge("two-clocks-align", "One modulus divides the other", "3 4 11 12\n",
              "m2 / g = 1 means t is 0 — an inverse modulo 1 must not be computed blindly."),
        _edge("primes-in-window", "The window starts at 1", "1 30\n",
              "1 is never crossed out and is counted as prime; or small primes are crossed out by themselves."),
        _edge("floor-quotient-sum", "The largest n", "1000000000000\n",
              "A loop over every i: 10¹² steps. And an `int` block end overflows."),
    ],
    walkthrough=_walk("two-clocks-align", "When do the two buses meet?", [
        """
Bus A arrives at a1, a1 + m1, …; bus B at a2, a2 + m2, …. Find the earliest common minute,
or −1. Both periods go up to 10⁹, so the answer can be as large as lcm(m1, m2) ≈ 10¹⁸.

Restate it: find the smallest x ≥ 0 with **x ≡ a1 (mod m1)** and **x ≡ a2 (mod m2)**.
""",
        """
“Two things that repeat with different periods, when do they line up?” is a pair of
congruences — number theory, and specifically the **Chinese remainder theorem**. The size
(10⁹ periods, 10¹⁸ answer) rules out walking the timetables.
""",
        """
Walk A's timetable and test each arrival against B:

```java
for (long x = a1; x < m1 * m2; x += m1)
    if (x % m2 == a2) return x;
return -1;
```

Correct, and up to m2 = 10⁹ iterations. It is still the right thing to write first — as the
**oracle** you will test the fast version against on small periods.
""",
        """
Every x on A's timetable is a1 + m1·t. It is on B's when

m1·t ≡ a2 − a1 (mod m2).

That is a *linear congruence in t*. With g = gcd(m1, m2), the left side is always a
multiple of g modulo m2, so there is a solution only if **g divides a2 − a1**. If it does,
divide everything by g:

(m1/g)·t ≡ (a2 − a1)/g (mod m2/g),

and now m1/g is coprime to m2/g, so it has an inverse — extended Euclid. The smallest
t ≥ 0 gives the smallest x.
""",
        """
```java
static long solve(long a1, long m1, long a2, long m2) {
    long g = gcd(m1, m2), diff = a2 - a1;
    if (diff % g != 0) return -1;
    long M = m2 / g;
    if (M == 1) return a1;                        // m2 divides m1: t = 0
    long rhs = ((diff / g) % M + M) % M;          // diff may be negative
    long t = rhs * inverse((m1 / g) % M, M) % M;  // both factors < M ≤ 10⁹
    return a1 + m1 * t;                           // < lcm ≤ 10¹⁸
}
```

The two overflow arguments are in the comments: rhs and the inverse are below M, so their
product is below 10¹⁸; and m1·t < m1·M = lcm.
""",
        """
Cases that each break something:

| Input | Expected | What it catches |
| --- | --- | --- |
| `2 3 3 5` | 8 | the ordinary coprime case |
| `1 4 2 6` | −1 | gcd 2 does not divide 1 |
| `3 4 1 6` | 7 | non-coprime but solvable |
| `3 4 11 12` | 11 | M = 1 |
| `999999999 1000000000 999999998 999999999` | 999999998999999999 | the answer near 10¹⁸ |

Then run the brute force against it on every a1 < m1 ≤ 60, a2 < m2 ≤ 60.

**Cost:** one gcd and one extended Euclid — O(log min(m1, m2)) time, O(1) space.
""",
    ]),
    interview_script="""
### Say it out loud

- *"Divisors pair up around √n, so I only loop to √n — that is a million steps at 10¹²."*
- *"I'll keep every intermediate below p by reducing after each multiplication; two values
  below 10⁹ + 7 multiply to under 2⁶³."*
- *"To divide modulo p I multiply by the inverse. p is prime here, so that's p^(p−2); if it
  weren't, I'd use extended Euclid."*
- *"Before combining the congruences I check that the gcd of the moduli divides the
  difference — otherwise there's no solution at all."*
""",
    lab=_lab("modular", """
Type any `a`, `b` and `m`. The lab shows gcd and lcm, the extended-Euclid table that
produces `a⁻¹ mod m` (or proves there is none), `aᵇ mod m` with every square-and-multiply
step, and the factorisation and φ of `m`. Try a composite `m` where Fermat's inverse would
lie, and a base far larger than `m`.
""", [
        ("Inverse of 17 mod 60", {"a": 17, "b": 5, "m": 60}),
        ("No inverse: 4 mod 10", {"a": 4, "b": 3, "m": 10}),
        ("Fermat vs Euclid, m = 10", {"a": 3, "b": 8, "m": 10}),
        ("Big exponent mod 10⁹ + 7", {"a": 2, "b": 1000000006, "m": 1000000007}),
        ("Huge base", {"a": "1000000000000000000", "b": 2, "m": 1000000007}),
        ("Highly composite m", {"a": 7, "b": 12, "m": 720720}),
    ]),
    drills=[
        _calc("How many divisors does 360 have?", "24",
              "360 = 2³ · 3² · 5, so (3 + 1)(2 + 1)(1 + 1) = 24."),
        _calc("What is gcd(84, 120)?", "12",
              "120 = 1·84 + 36, 84 = 2·36 + 12, 36 = 3·12 + 0. The last non-zero remainder is 12."),
        _calc("What is lcm(21, 6)?", "42", "21 / gcd(21, 6) · 6 = 21 / 3 · 6 = 42."),
        _calc("What is 3⁻¹ mod 11?", "4", "3 · 4 = 12 = 11 + 1. (Fermat: 3⁹ mod 11 = 4 as well.)"),
        _calc("What is 7⁻¹ mod 26? (Type −1 if there is none.)", "15",
              "7 · 15 = 105 = 4 · 26 + 1. gcd(7, 26) = 1, so it exists.", accept=["15"]),
        _calc("What is 6⁻¹ mod 9? (Type −1 if there is none.)", "-1",
              "gcd(6, 9) = 3 ≠ 1, so 6x is always a multiple of 3 modulo 9 and never 1.",
              accept=["−1", "none"]),
        _calc("What is 2¹⁰ mod 1000?", "24", "1024 mod 1000 = 24."),
        _calc("What is φ(36)?", "12", "36 = 2² · 3², so 36 · (1 − 1/2)(1 − 1/3) = 12."),
        _calc("How many primes are there below 30?", "10",
              "2, 3, 5, 7, 11, 13, 17, 19, 23, 29."),
        _calc("What is (7 − 13) % 5 in Java?", "-1",
              "−6 = −1 · 5 − 1: Java truncates toward zero, so the remainder keeps the sign of −6. `Math.floorMod(-6, 5)` is 4.",
              accept=["−1"]),
        _calc("Solve x ≡ 2 (mod 3), x ≡ 3 (mod 5). Smallest x ≥ 0?", "8",
              "x = 2 + 3t, and 2 + 3t ≡ 3 (mod 5) gives 3t ≡ 1, t ≡ 2. So x = 8."),
        _calc("What is Σ ⌊10 / i⌋ for i = 1 … 10?", "27",
              "10 + 5 + 3 + 2 + 2 + 1 + 1 + 1 + 1 + 1 = 27."),
    ],
)


# ========================================================== bit manipulation

_H_BITS = dict(
    quizzes=[
        _quiz("bug",
              "Choosing element 40 sets bit 8 of the mask instead. Which change fixes it?",
              r"""
long mask = 0;
for (int i : chosen)          // i in 0..62
    mask |= 1 << i;
""",
              "`mask |= 1L << i`",
              ["`mask |= 1L << i`",
               "`mask |= (long) (1 << i)`",
               "`mask ^= 1 << i`",
               "`mask |= 1 << (i % 64)`"],
              """
`1 << i` is an **int** shift, and Java takes an int's shift count modulo 32 — so `1 << 40`
is `1 << 8` = 256. Casting the result to long afterwards is too late. `1L` makes the shift a
long shift, whose count is taken modulo 64.
"""),
        _quiz("predict",
              "What does this print?",
              r"""
System.out.println((-8 >> 1) + " " + (-8 >>> 28));
""",
              "`-4 15`",
              ["`-4 15`", "`4 15`", "`-4 -1`", "`2147483644 15`"],
              """
−8 is `11111111 11111111 11111111 11111000`. `>>` copies the sign bit in from the top, so
`−8 >> 1` is −4. `>>>` shifts zeros in, so `>>> 28` leaves the top four bits, `1111`, at the
bottom: 15.
"""),
        _quiz("predict",
              "What does this print?",
              r"""
int x = 40;
System.out.println((x & -x) + " " + (x & (x - 1)));
""",
              "`8 32`",
              ["`8 32`", "`8 40`", "`32 8`", "`40 8`"],
              """
40 = `101000`. `x & -x` isolates the lowest set bit, `001000` = 8. `x & (x − 1)` clears it,
leaving `100000` = 32. Their sum is always x.
"""),
        _quiz("bug",
              "This reports `true` for two inputs that are not powers of two. Which change fixes it?",
              r"""
static boolean isPowerOfTwo(int x) {
    return (x & (x - 1)) == 0;
}
""",
              "Guard it: `x > 0 && (x & (x - 1)) == 0`",
              ["Guard it: `x > 0 && (x & (x - 1)) == 0`",
               "Use `(x | (x - 1)) == 0`",
               "Use `(x & -x) == 0`",
               "Use `>>>` instead of subtraction"],
              """
For x = 0, `0 & −1` is 0. For `Integer.MIN_VALUE` (a single 1 in the sign bit), x − 1 is
`Integer.MAX_VALUE` — all the other bits — and the AND is 0 again. Neither is a power of
two; `x > 0` excludes both.
"""),
        _quiz("bug",
              "This loop over the submasks of `mask` never terminates. Which change fixes it?",
              r"""
for (int sub = mask; sub >= 0; sub = (sub - 1) & mask) {
    visit(sub);
}
""",
              "Loop while `sub > 0`, and visit the empty submask separately",
              ["Loop while `sub > 0`, and visit the empty submask separately",
               "Step with `sub = (sub - 1) | mask`",
               "Step with `sub = sub - 1`",
               "Start at `sub = mask - 1`"],
              """
After visiting 0, the step computes `(0 − 1) & mask` = `−1 & mask` = mask — back to the
start. `sub >= 0` is always true, so the loop cycles forever. Stop at `sub > 0` and handle
the empty set once after the loop. `sub − 1` alone would visit non-submasks.
"""),
        _quiz("predict",
              "What does this return for `a = {5, 5, 3}`?",
              r"""
long total = 0;
int n = a.length;
for (int b = 0; b < 30; b++) {
    long ones = 0;
    for (int v : a) ones += (v >> b) & 1;
    total += ones * (n - ones) << b;
}
return total;
""",
              "12",
              ["12", "6", "0", "18"],
              """
The pairs are 5 ^ 5 = 0, 5 ^ 3 = 6, 5 ^ 3 = 6: 12. Per bit: bit 0 is set in all three
(3 · 0 = 0 pairs), bit 1 only in 3 (1 · 2 = 2 pairs, worth 2 each = 4), bit 2 in both 5s
(2 · 1 = 2 pairs, worth 4 each = 8). 4 + 8 = 12.
"""),
    ],
    stuck=[
        _stuck("“Every element appears k times except one”",
               "Is k even? Then XOR cancels them. If k is odd (3, 5 …), count each bit position modulo k instead."),
        _stuck("Two unknown values mixed together in one XOR",
               "Which bit is 1 in their XOR? Split everything by that bit, and each half has one unknown."),
        _stuck("A sum or maximum over **all pairs**, n = 10⁵",
               "Do the bits act independently in this operation? For XOR, AND and OR they do — count per bit."),
        _stuck("“Maximise” an AND / OR / XOR",
               "Is a higher bit worth more than all lower bits together? Then decide bits from the top, one at a time."),
        _stuck("A choice for each of n ≤ 20 items",
               "Can a subset be a mask? Then there are only 2ⁿ ≈ 10⁶ of them — try them all, building each from a smaller mask."),
        _stuck("A formula over 1 … n with n = 10¹⁸",
               "What does bit b do as the numbers count up? It is a square wave with period 2^(b+1) — count it with a division."),
    ],
    edge_cases=[
        _edge("power-of-two", "Zero", "0\n", "`(x & (x − 1)) == 0` without the `x > 0` guard says true."),
        _edge("power-of-two", "The most negative int", "-2147483648\n",
              "A single set bit in the sign position also passes the unguarded test."),
        _edge("light-panel", "The sign bit", "3\non 31\nshow\ncheck 31\n",
              "An `int` panel prints −2147483648 instead of 2147483648."),
        _edge("single-number-iii", "Negative values", "4\n-3 7 -3 -8\n",
              "Splitting on `x & -x` works for negatives, but a split on `x > 0` does not."),
        _edge("budget-subsets", "Budget zero", "3 0\n5 6 7\n",
              "Forgetting the empty subset: the answer is 1, not 0."),
        _edge("budget-subsets", "Totals past int", "5 3000000000\n1000000000 1000000000 1000000000 999999999 2\n",
              "Subset sums above 2³¹ in an `int` array wrap negative and count as affordable."),
        _edge("pair-xor-total", "Values at the top of the range", "4\n0 1073741823 0 1073741823\n",
              "`ones * (n − ones)` in int, or the shift done before widening to long."),
        _edge("missing-and-duplicate", "Missing the first tag", "5\n2 3 4 5 5\n",
              "Mixing up which bucket is the duplicate: check which value actually appears."),
        _edge("range-xor", "l = 0", "0 7\n", "f(l − 1) with l = 0 must be 0, not f(−1) from the table."),
        _edge("next-same-popcount", "A single set bit", "562949953421312\n",
              "Counting up from n + 1 takes 2⁴⁹ steps; Gosper's hack answers at once."),
    ],
    walkthrough=_walk("pair-xor-total", "Total of all pair XORs", [
        """
For every pair i < j, compute `a[i] ^ a[j]`, and report the sum. n is up to 10⁵ and values
are below 2³⁰.

The size matters immediately: there are n(n − 1)/2 ≈ 5 × 10⁹ pairs.
""",
        """
“Over all pairs”, with a bitwise operator, and far too many pairs to visit: that is the
**contribution technique** from bit manipulation. Ask what each *bit* contributes, not what
each *pair* contributes.
""",
        """
```java
long total = 0;
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        total += a[i] ^ a[j];
```

O(n²): 5 × 10⁹ XORs. Keep it — it is the oracle for n ≤ 200.
""",
        """
XOR works on each bit position independently. Bit b of `a[i] ^ a[j]` is 1 exactly when one
of the two numbers has bit b and the other does not.

If `ones` of the n numbers have bit b, then the pairs with bit b set in their XOR are the
pairs with one number from each group: **ones × (n − ones)**. Each contributes 2ᵇ.

So the total is Σ over b of ones_b · (n − ones_b) · 2ᵇ — thirty counts, and no pair ever
formed.
""",
        """
```java
static long solve(int[] a) {
    long n = a.length, total = 0;
    for (int b = 0; b < 30; b++) {
        long ones = 0;
        for (int v : a) ones += (v >> b) & 1;
        total += ones * (n - ones) * (1L << b);
    }
    return total;
}
```

`n` and `ones` are `long`, so the product is computed in long from the start.
""",
        """
| Input | Expected | What it catches |
| --- | --- | --- |
| `3` / `1 2 3` | 6 | the basic count |
| `4` / `5 5 5 5` | 0 | equal values contribute nothing |
| `1` / `7` | 0 | no pairs at all |
| `100000` values half 0, half 2³⁰ − 1 | 2684354557500000000 | the int overflow |

Compare with the O(n²) oracle on a thousand random arrays of size ≤ 50.

**Cost:** O(30 · n) time, O(1) space. The total peaks near 5.4 × 10¹⁸, inside a long's
9.2 × 10¹⁸.
""",
    ]),
    interview_script="""
### Say it out loud

- *"XOR is associative and commutative and x ^ x is 0, so every pair cancels and only the
  unpaired value survives."*
- *"There are too many pairs, but the bits are independent — so I'll count, for each bit,
  how many pairs have it set: ones times zeros."*
- *"A higher bit is worth more than all the lower bits together, so I decide the answer from
  the top bit down."*
- *"The mask can reach bit 40, so I'll shift a `1L`, not a `1`."*
""",
    lab=_lab("bits", """
Type two integers `a` and `b` and a shift `k`. The lab shows each as 32 bits (two's
complement), every operator's result with the changed bits highlighted, and the lowest-bit
idioms. Try a negative number, `k = 32`, and a power of two.
""", [
        ("13 and 11", {"a": 13, "b": 11, "k": 2}),
        ("Lowest bit of 40", {"a": 40, "b": 39, "k": 3}),
        ("A negative number", {"a": -8, "b": 7, "k": 1}),
        ("Shift by 32", {"a": 1, "b": 0, "k": 32}),
        ("The sign bit", {"a": -2147483648, "b": 2147483647, "k": 31}),
        ("Gosper step on 92", {"a": 92, "b": 4, "k": 2}),
    ]),
    drills=[
        _calc("What is 13 & 11?", "9", "1101 & 1011 = 1001 = 9."),
        _calc("What is 13 | 11?", "15", "1101 | 1011 = 1111 = 15."),
        _calc("What is 13 ^ 11?", "6", "1101 ^ 1011 = 0110 = 6."),
        _calc("What is 40 & -40?", "8", "40 = 101000; the lowest set bit is 1000 = 8."),
        _calc("What is 40 & (40 - 1)?", "32", "40 & 39 = 101000 & 100111 = 100000 = 32."),
        _calc("What is `1 << 33` for an `int` in Java?", "2",
              "The shift count is taken mod 32, so it is 1 << 1."),
        _calc("What is `-1 >>> 28`?", "15", "−1 is 32 ones; shifting 28 zeros in leaves the top four ones: 1111 = 15."),
        _calc("What is `Integer.bitCount(255)`?", "8", "255 = 11111111."),
        _calc("What is the XOR of all integers from 0 to 10?", "11",
              "10 mod 4 = 2, so the formula gives n + 1 = 11."),
        _calc("How many non-empty submasks does the mask 1011 have?", "7",
              "Three set bits give 2³ = 8 submasks, one of which is empty."),
        _calc("What is the next number after 92 with the same number of set bits?", "99",
              "92 = 1011100 → 1100011 = 99 (Gosper's hack)."),
        _calc("What is the sum of a[i] ^ a[j] over all pairs of {1, 2, 3}?", "6",
              "1^2 + 1^3 + 2^3 = 3 + 2 + 1 = 6."),
    ],
)


# ======================================================= simulation & matrices

_H_GRID = dict(
    quizzes=[
        _quiz("bug",
              "This is meant to rotate a square matrix 90° clockwise, but the result is only mirrored left-to-right. Which change fixes it?",
              r"""
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++) {
        int t = a[i][j]; a[i][j] = a[j][i]; a[j][i] = t;
    }
for (int[] row : a)
    for (int l = 0, r = n - 1; l < r; l++, r--) {
        int t = row[l]; row[l] = row[r]; row[r] = t;
    }
""",
              "The transpose's inner loop must start at `j = i + 1`",
              ["The transpose's inner loop must start at `j = i + 1`",
               "Reverse each column instead of each row",
               "Reverse the rows before transposing",
               "Swap `a[j][i]` with `a[i][j]` in the other order"],
              """
With `j` from 0, every pair (i, j) is swapped when visited as (i, j) and swapped back when
visited as (j, i) — the "transpose" is the identity. Only the row reversal takes effect,
which is a mirror. Start at `j = i + 1` so each pair is swapped once.
"""),
        _quiz("bug",
              "On the 1 × 3 grid `1 2 3` this prints `1 2 3 2 1`. Which change fixes it?",
              r"""
int top = 0, bot = rows - 1, left = 0, right = cols - 1;
while (top <= bot && left <= right) {
    for (int j = left; j <= right; j++) out.add(a[top][j]);
    top++;
    for (int i = top; i <= bot; i++) out.add(a[i][right]);
    right--;
    for (int j = right; j >= left; j--) out.add(a[bot][j]);
    bot--;
    for (int i = bot; i >= top; i--) out.add(a[i][left]);
    left++;
}
""",
              "Guard the bottom edge with `if (top <= bot)` and the left edge with `if (left <= right)`",
              ["Guard the bottom edge with `if (top <= bot)` and the left edge with `if (left <= right)`",
               "Make the loop condition `top < bot && left < right`",
               "Walk the right edge from `top - 1`",
               "Decrement `right` before walking the top row"],
              """
After the top row, `top` is 1 and `bot` is 0 — the rectangle is already empty. The bottom
edge still walks row `bot = 0` from right to left and emits 2 1 again. Re-check the bounds
before the two return edges. Tightening the loop condition instead skips single rows
entirely.
"""),
        _quiz("predict",
              "In a 3 × 3 clockwise rotation, where does the value at row 0, column 1 end up?",
              r"""
int[][] b = new int[n][n];
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        b[j][n - 1 - i] = a[i][j];
""",
              "(1, 2)",
              ["(1, 2)", "(2, 1)", "(1, 0)", "(0, 1)"],
              """
(i, j) = (0, 1) goes to (j, n − 1 − i) = (1, 2): the top edge's middle becomes the right
edge's middle. Check it against the picture — the top row of a clockwise-rotated grid ends
up as its right column.
"""),
        _quiz("bug",
              "One generation of the Game of Life comes out wrong from the second row onwards. What is the bug?",
              r"""
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++) {
        int live = liveNeighbours(g, i, j);
        g[i][j] = (live == 3 || (live == 2 && g[i][j] == 1)) ? 1 : 0;
    }
""",
              "Cells are updated in place, so later cells count neighbours from the new generation",
              ["Cells are updated in place, so later cells count neighbours from the new generation",
               "The rule should read `live == 2 || live == 3` for every cell",
               "The loops must run columns before rows",
               "`liveNeighbours` must skip the diagonal neighbours"],
              """
Cell (1, j) counts (0, j − 1 … j + 1), which were already overwritten. Every cell must read
generation t. Write into a separate grid and swap, or encode old and new state in the same
cell (old in bit 0, new in bit 1) and shift at the end.
"""),
        _quiz("bug",
              "The copy is meant to keep the old generation, but `next` and `g` change together. Which change fixes it?",
              r"""
int[][] next = g.clone();
for (int i = 0; i < r; i++)
    for (int j = 0; j < c; j++)
        next[i][j] = rule(g, i, j);
""",
              "Clone each row: `next[i] = g[i].clone()`",
              ["Clone each row: `next[i] = g[i].clone()`",
               "Use `Arrays.copyOf(g, r)`",
               "Declare `next` as `final`",
               "Iterate `j` in the outer loop"],
              """
`clone()` on an `int[][]` copies the outer array — an array of **references to the same row
arrays**. Writing `next[i][j]` writes into `g[i]`. `Arrays.copyOf` has the same problem. A
2-D copy clones every row.
"""),
        _quiz("predict",
              "With `step(x) = (x * x + 1) % 10`, starting from 3, what does this print for `n = 1000`?",
              r"""
Map<Integer, Integer> seen = new HashMap<>();
int x = 3;
for (int t = 0; t < n; t++) {
    Integer first = seen.put(x, t);
    if (first != null) {
        int left = (n - t) % (t - first);
        for (int i = 0; i < left; i++) x = step(x);
        break;
    }
    x = step(x);
}
System.out.println(x);
""",
              "5",
              ["5", "3", "0", "7"],
              """
3 → 0 → 1 → 2 → 5 → 6 → 7 → 0. The state 0 is seen at t = 1 and again at t = 7: a cycle of
length 6 after a pre-period of 1. (1000 − 7) mod 6 = 3 more steps from 0: 1, 2, 5. Using
1000 mod 6 instead of (n − t) mod 6 would land on the wrong state.
"""),
    ],
    stuck=[
        _stuck("A matrix transformation (rotate, flip, reflect)",
               "Where does cell (i, j) go? Write it as (i, j) → (i′, j′), check two corners by hand, then see if it is a composition of transpose and flips."),
        _stuck("“Every cell updates at once”",
               "Does the rule read neighbours? Then every read must see the old grid — a copy or a two-state encoding."),
        _stuck("A rotation or shift by a huge k",
               "After how many steps is it back to the start? Take k modulo that length."),
        _stuck("“After n steps”, n = 10⁹ or more",
               "How many distinct states are there? If it is finite, the sequence cycles — find where."),
        _stuck("A game with several rules (snake, robot, tilt)",
               "What questions does each rule ask every step — “what's at the tail?”, “is this cell occupied?” — and what structure answers each in O(1)?"),
        _stuck("A traversal in a strange order (spiral, diagonal, zigzag)",
               "What stays constant along one leg of the order — a row, a column, i − j, i + j? Loop over that."),
    ],
    edge_cases=[
        _edge("transpose-matrix", "A single row", "1 4\n5 -1 0 9\n",
              "Allocating the result as r × c instead of c × r."),
        _edge("spiral-order", "A single row", "1 3\n123\n",
              "No guard on the return edges: the row is emitted twice."),
        _edge("spiral-order", "A single column", "3 1\n1\n2\n3\n",
              "No guard on the left edge after the right one."),
        _edge("rotate-array", "k larger than n", "3\n1 2 3\n10\n",
              "Not reducing k mod n: the reversal bounds go out of range."),
        _edge("rotate-rings", "k a multiple of the ring length", "2 2 4\n1 2\n3 4\n",
              "A full turn must leave the grid unchanged."),
        _edge("rotate-rings", "Rings of different lengths", "4 6 7\n0 1 2 3 4 5\n6 7 8 9 10 11\n12 13 14 15 16 17\n18 19 20 21 22 23\n",
              "Using one shift for every ring instead of k mod each ring's own length."),
        _edge("tilt-the-board", "A stone already against the wall", "1 3\nO.O\nL\n",
              "Writing the stone before clearing its cell deletes it when old and new are the same."),
        _edge("snake-on-grid", "Chasing its own tail", "2 2 1\n0 1\nRDLURDLU\n",
              "Checking the head before the tail moves kills a legal snake."),
        _edge("snake-on-grid", "Reversing into the neck", "1 6 2\n0 1\n0 2\nRRRL\n",
              "A length-3 snake reversing must die — its neck is not the tail."),
        _edge("lamp-row-after-days", "Zero nights", "1011 0\n", "The loop must not step even once."),
        _edge("lamp-row-after-days", "A pre-period before the cycle", "00001 1000000000000000000\n",
              "Taking n mod cycle instead of (n − t) mod cycle."),
    ],
    walkthrough=_walk("lamp-row-after-days", "Lamps after N nights", [
        """
A row of w ≤ 16 lamps. Each night every lamp becomes on exactly when **one** of its two
neighbours was on (outside the row counts as off). Print the row after n nights, with n up
to 10¹⁸.
""",
        """
“Every cell updates at once, from its neighbours” is **simulation** — and “after 10¹⁸
steps” is the near miss in this unit's router: not a loop, but **cycle detection**, because
the state space is finite (2¹⁶ rows).
""",
        """
```java
for (long t = 0; t < n; t++) {
    char[] next = new char[w];
    for (int i = 0; i < w; i++) {
        int l = i > 0 && row[i - 1] == '1' ? 1 : 0;
        int r = i + 1 < w && row[i + 1] == '1' ? 1 : 0;
        next[i] = (l ^ r) == 1 ? '1' : '0';
    }
    row = next;
}
```

Correct — it reads tonight's row and writes a new one, so every lamp sees the same night.
It is also 10¹⁸ · w steps. Keep it as the oracle for n ≤ 1000.
""",
        """
Two observations.

**One night is one expression.** Put lamp i in bit i. The neighbours of every lamp at once
are `x << 1` and `x >> 1`, and "exactly one is on" is XOR: `((x << 1) ^ (x >> 1)) & full`,
where `full = (1 << w) − 1` drops the bit that shifted out of the row.

**The sequence must cycle.** There are only 2ʷ rows, so within 2ʷ + 1 nights some row
repeats, and the future from a repeated row is the same as before. Record the night each
row is first seen; when night t produces a row first seen on night s, the cycle length is
t − s, and only (n − t) mod (t − s) more nights matter.
""",
        """
```java
static String solve(String s, long n) {
    int w = s.length(), full = (1 << w) - 1, x = 0;
    for (int i = 0; i < w; i++) if (s.charAt(i) == '1') x |= 1 << i;
    long[] seen = new long[1 << w];
    Arrays.fill(seen, -1);
    for (long t = 0; t < n; t++) {
        if (seen[x] >= 0) {
            long left = (n - t) % (t - seen[x]);
            for (long i = 0; i < left; i++) x = ((x << 1) ^ (x >> 1)) & full;
            break;
        }
        seen[x] = t;
        x = ((x << 1) ^ (x >> 1)) & full;
    }
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < w; i++) sb.append((x >> i & 1) == 1 ? '1' : '0');
    return sb.toString();
}
```

An array of 2¹⁶ longs replaces a hash map, because the state is already a small integer.
""",
        """
| Input | Expected | What it catches |
| --- | --- | --- |
| `0100 1` | 1010 | one night, both ends |
| `10000 3` | 00010 | a lamp with both neighbours on goes dark |
| `1011 0` | 1011 | no steps at all |
| `00001 1000000000000000000` | 10100 | skipping by (n − t) mod cycle, not n mod cycle |
| `1000000000000001 1000000000000000000` | 0000111111110000 | width 16, the full mask |

Compare against the direct loop for every row of width ≤ 8 and n ≤ 600.

**Cost:** at most 2ʷ + 1 nights before a repeat, then less than one cycle more — O(2ʷ)
time and space, independent of n.
""",
    ]),
    interview_script="""
### Say it out loud

- *"Every cell reads the old generation, so I'll write into a copy and swap — I can encode
  both states in one cell if you want O(1) space."*
- *"Rotation is transpose then reverse each row; let me check a corner: (0, 0) should end up
  at (0, n − 1)."*
- *"For the spiral I'll keep four boundaries and re-check them before the two return
  edges — that's where a single row gets printed twice."*
- *"n is 10¹⁸ but there are only 2¹⁶ states, so it has to cycle; I'll record when I first
  see each state and jump."*
""",
    lab=_lab("grid", """
Pick a grid size and click any cell. The lab shows its 4- and 8-neighbours (clipped at the
border), where it goes under each rotation, flip and the transpose, its diagonal keys
`i − j` and `i + j`, its ring, its flattened id `i · c + j`, and its position in spiral
order.
""", [
        ("Corner of a 4 × 5", {"rows": 4, "cols": 5, "i": 0, "j": 0}),
        ("Interior of a 5 × 5", {"rows": 5, "cols": 5, "i": 2, "j": 2}),
        ("Edge of a 3 × 6", {"rows": 3, "cols": 6, "i": 0, "j": 3}),
        ("A single row", {"rows": 1, "cols": 6, "i": 0, "j": 2}),
        ("Inner ring of a 6 × 8", {"rows": 6, "cols": 8, "i": 2, "j": 5}),
    ]),
    drills=[
        _calc("In a 4 × 5 grid, what is the flattened id `i · cols + j` of cell (2, 3)?", "13",
              "2 · 5 + 3 = 13. The multiplier is the number of **columns**."),
        _calc("In a 4 × 5 grid, which cell has flattened id 17? Answer as `i j`.", "3 2",
              "i = 17 / 5 = 3, j = 17 % 5 = 2.", accept=["(3, 2)", "3,2"]),
        _calc("In a 4 × 4 grid rotated 90° clockwise, where does cell (1, 3) go? Answer as `i j`.", "3 2",
              "(i, j) → (j, n − 1 − i) = (3, 4 − 1 − 1) = (3, 2).", accept=["(3, 2)", "3,2"]),
        _calc("Transposing a 3 × 7 matrix: where does cell (2, 5) go? Answer as `i j`.", "5 2",
              "(i, j) → (j, i).", accept=["(5, 2)", "5,2"]),
        _calc("How many cells does the outer ring of a 4 × 6 grid have?", "16",
              "2 · (4 + 6) − 4 = 16: two rows of 6 and two columns of 4, minus the 4 corners counted twice."),
        _calc("A cell in the interior of a grid has how many 8-directional neighbours, and a corner cell?", "8 3",
              "Interior: all eight. Corner: right, down and the diagonal between them.",
              accept=["8, 3", "8,3"]),
        _calc("How many ↘ diagonals (constant i − j) does a 3 × 5 grid have?", "7",
              "r + c − 1 = 7: i − j runs from −4 to 2."),
        _calc("Spiral order of the 3 × 3 grid 1 2 3 / 4 5 6 / 7 8 9 — what is the 6th value?", "8",
              "1 2 3 6 9 8 7 4 5: the 6th is 8."),
        _calc("A ring of 12 cells is rotated by k = 1,000,000,000. By how many single steps does it effectively move?", "4",
              "10⁹ mod 12 = 4."),
        _calc("Rotate the array 1 2 3 4 5 right by 7. What is the new first element?", "4",
              "7 mod 5 = 2, so the last two elements come to the front: 4 5 1 2 3."),
        _calc("Lamps 10000 after one night (a lamp is on when exactly one neighbour was on)?", "01000",
              "Only lamp 1 has exactly one lit neighbour (lamp 0)."),
    ],
)


_S4_CHEATSHEET = r"""
### Which unit?

| The prompt says… | Unit | Template |
| --- | --- | --- |
| prime, divisors, gcd, factorise, “modulo 10⁹ + 7” | Math & number theory | √n loop · sieve · Euclid · reduce every step |
| appears twice / missing, set bits, subsets of ≤ 20, AND / OR / XOR over pairs | Bit manipulation | XOR fold · `x & (x − 1)` · masks · per-bit counts |
| grid, rotate, spiral, “each step every cell”, a game to play out | Simulation & matrices | direction array · copy then swap · transpose + reverse · cycle detection |

### The templates

```java
// Number theory
for (long d = 2; d * d <= n; d++) while (n % d == 0) { n /= d; /* factor d */ }   // leftover n > 1 is prime
static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }             // lcm = a / gcd * b
static long power(long b, long e, long m) { long r = 1; b %= m;
    for (; e > 0; e >>= 1, b = b * b % m) if ((e & 1) == 1) r = r * b % m; return r; }
long r0 = a, r1 = m, s0 = 1, s1 = 0;                                                // inverse mod any m
while (r1 != 0) { long q = r0 / r1, t = r0 - q * r1; r0 = r1; r1 = t; t = s0 - q * s1; s0 = s1; s1 = t; }

// Bits
x & (x - 1)   /* clear lowest */      x & -x   /* lowest bit */      1L << i   /* past bit 31 */
for (int sub = mask; sub > 0; sub = (sub - 1) & mask) { }                          // submasks
total += ones * (n - ones) << b;                                                    // pair XOR, per bit

// Grids
int[][] D = {{-1,0},{1,0},{0,-1},{0,1}};  if (ni < 0 || ni >= r || nj < 0 || nj >= c) continue;
transpose (j > i) then reverse each row   // rotate 90° clockwise, in place
Long first = seen.put(state, t); if (first != null) skip (n - t) % (t - first) steps;
```

### The six bugs that fail hidden tests

1. `n < 2` not guarded — 1 reported prime; `x > 0` not guarded — 0 reported a power of two.
2. `i * i`, `a * b`, `1 << k` in `int` — overflow, wrong shift, silent wrap.
3. `(a − b) % MOD` negative in Java — add MOD before the final `%`.
4. Fermat's inverse with a composite modulus — use extended Euclid.
5. Updating a grid in place while reading neighbours — every read must see generation t.
6. A spiral or ring walk without the re-check — a single row or column visited twice.

### Costs to quote

| | Time | Space |
| --- | --- | --- |
| Trial division / factorise / φ | O(√n) | O(1) |
| Sieve / SPF sieve to n | O(n log log n) | O(n) |
| gcd, extended Euclid, fast power | O(log n) | O(1) |
| XOR fold, per-bit counts | O(n), O(n · 30) | O(1) |
| All subsets / all submasks | O(2ⁿ) / O(3ⁿ) | O(2ⁿ) if stored |
| Grid pass, rotation, spiral | O(r · c) | O(1) in place |
| Cycle detection over S states | O(S) | O(S) |
"""


def _attach_s4_help():
    by_key = {u["key"]: u for u in _UNITS}
    for key, h in {
        "math-number-theory": _H_MATH,
        "bit-manipulation": _H_BITS,
        "simulation-and-matrix": _H_GRID,
    }.items():
        u = by_key[key]
        u["quizzes"].extend(h["quizzes"])
        u["stuck"].extend(h["stuck"])
        u["edge_cases"].extend(h["edge_cases"])
        u["walkthrough"] = h["walkthrough"]
        u["interview"] = u["interview"].rstrip() + "\n\n" + _md(h["interview_script"])
        u["lab"] = h["lab"]
        u["drills"].extend(h["drills"])
    for st in _STAGES:
        if st["key"] == "numbers-and-grids":
            st["cheatsheet"] = _md(_S4_CHEATSHEET)


_attach_s4_help()
