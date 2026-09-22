# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 50 — Numbers, Bits & Grids, part 1: number theory.
#
#   prime-factorization     trial division that divides as it goes
#   divisor-count-queries   the smallest-prime-factor sieve: factor in O(log x)
#   coprime-count           Euler's totient from the factorisation
#   inverse-mod-any         extended Euclid: inverses when m is not prime
#   two-clocks-align        the Chinese remainder theorem, moduli not coprime
#   primes-in-window        a segmented sieve over a window near 10^12
#   floor-quotient-sum      sum of n / i in O(sqrt n): the divisor blocks
#
# Defines the `quad` shape (four integers). Later stage-4 batches may use it.
# ===========================================================================

# four integers, on one line or several
_SHAPES["quad"] = dict(
    py="d = sys.stdin.read().split()\nx, y, z, w = int(d[0]), int(d[1]), int(d[2]), int(d[3])\n",
    py_params="x, y, z, w",
    js=_JS_NUMS + "const x = Number(d[0]), y = Number(d[1]), z = Number(d[2]), w = Number(d[3]);\n",
    js_params="x, y, z, w",
    java="        long x = sc.nextLong(), y = sc.nextLong(), z = sc.nextLong(), w = sc.nextLong();\n",
    java_params="long x, long y, long z, long w", java_args="x, y, z, w",
)


_p(
    "prime-factorization", "Prime Factor Breakdown", "Easy",
    topics=["Math"], subtopics=["Number Theory", "Prime Factorization", "Trial Division"],
    companies=["Amazon", "Adobe"],
    shape="n", ret="String",
    todo="divide out each d from 2 while d * d <= n, counting the exponent; whatever is left above 1 is one last prime",
    description=(
        "Write `n` as a product of primes.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nOne line per distinct prime factor, in "
        "increasing order: the prime `p` and its exponent `e`, separated by a space."
    ),
    constraints="2 ≤ n ≤ 10^12",
    hints=[
        "Try divisors d = 2, 3, 4, … . When d divides n, divide it out *completely*, counting how many times.",
        "Because every smaller prime has already been divided out, a composite d can never divide what is left — so every d that divides is prime.",
        "Stop when d · d > n. If what remains is greater than 1, it is a single prime above √n with exponent 1.",
    ],
    opt=("O(√n)", "O(1)",
         "At most √n candidate divisors, and n only shrinks."),
    editorial=(
        "## The one thing this teaches\n**Divide as you go.** Trial division for primality asks "
        "“does anything divide n?”. Factorisation keeps asking after the answer is yes: divide "
        "the factor out completely, and carry on with what is left.\n\n"
        "## Approach\n```java\nfor (long d = 2; d * d <= n; d++) {\n"
        "    if (n % d != 0) continue;\n    int e = 0;\n"
        "    while (n % d == 0) { n /= d; e++; }\n    out.add(d + \" \" + e);\n}\n"
        "if (n > 1) out.add(n + \" 1\");        // one prime above the square root\n```\n\n"
        "## Why every d that divides is prime\nWhen d is reached, every prime below d has "
        "already been divided out. A composite d has a prime factor below it, which is gone, so "
        "d cannot divide what remains.\n\n"
        "## Why the leftover is prime\nIf the loop stops with n > 1, n has no factor ≤ √n "
        "(for the *current* n), so it is prime. At most one such factor can exist: two primes "
        "above √n would multiply to more than n.\n\n"
        "## Cost\nO(√n) in the worst case — n prime — which is 10⁶ steps at n = 10¹². A number "
        "with small factors shrinks fast and finishes far sooner."
    ),
    py='''
def solve(n):
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            out.append(f"{d} {e}")
        d += 1
    if n > 1:
        out.append(f"{n} 1")
    return "\\n".join(out)
''',
    java='''
    static String solve(long n) {
        StringBuilder sb = new StringBuilder();
        for (long d = 2; d * d <= n; d++) {
            if (n % d != 0) continue;
            int e = 0;
            while (n % d == 0) { n /= d; e++; }
            if (sb.length() > 0) sb.append('\\n');
            sb.append(d).append(' ').append(e);
        }
        if (n > 1) {
            if (sb.length() > 0) sb.append('\\n');
            sb.append(n).append(" 1");
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "360\n"),
        ("Example 2", "97\n"),
    ],
    hidden=[
        ("Smallest", "2\n"),
        ("A power of two", "1099511627776\n"),
        ("Square of a prime", "1018081\n"),
        ("Large prime", "999999999989\n"),
        ("Square of a large prime", "999966000289\n"),
        ("Many small primes", "200560490130\n"),
        ("Prime above the root", "2000000014\n"),
    ],
    expl=[
        "360 = 2³ · 3² · 5.",
        "97 is prime: nothing from 2 to 9 divides it.",
    ],
    prereqs=[
        ("number_theory", "Trial division to √n, dividing each factor out completely as it is found."),
        ("math_digits", "`n % d` and `n /= d` on a long."),
    ],
)


_p(
    "divisor-count-queries", "Divisor Counts, Many at Once", "Medium",
    topics=["Math"], subtopics=["Number Theory", "Sieve", "Smallest Prime Factor"],
    companies=["Google", "Codeforces-style"],
    shape="arr", ret="String",
    todo="sieve the smallest prime factor of every value up to max(a); factor each query by repeatedly dividing by spf, multiplying (e + 1)",
    description=(
        "For each of `n` numbers, report how many positive divisors it has.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nOne line: the `n` divisor "
        "counts, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ a[i] ≤ 1000000",
    hints=[
        "A √x loop per number is up to 10⁵ × 10³ = 10⁸ steps. Share the work instead.",
        "If x = p₁^e₁ · p₂^e₂ · …, the number of divisors is (e₁ + 1)(e₂ + 1)… — each divisor picks an exponent for each prime.",
        "Sieve once: spf[v] = the smallest prime dividing v. Then factoring x is `while (x > 1) { p = spf[x]; x /= p; … }` — O(log x) steps.",
    ],
    opt=("O(M log log M + n log M)", "O(M)",
         "One smallest-prime-factor sieve up to M = max(a), then O(log x) per query."),
    editorial=(
        "## The one thing this teaches\n**The sieve can remember *which* prime crossed a number "
        "out.** A boolean sieve answers “is it prime?”. Storing the smallest prime factor "
        "instead answers “what is its factorisation?”, in O(log x) per number, for every number "
        "up to M.\n\n"
        "## The SPF sieve\n```java\nint[] spf = new int[M + 1];\n"
        "for (int i = 2; i <= M; i++) {\n    if (spf[i] != 0) continue;              // i is prime\n"
        "    for (int j = i; j <= M; j += i)\n        if (spf[j] == 0) spf[j] = i;         // first prime to reach j is its smallest\n}\n```\n\n"
        "## Counting divisors from the factorisation\n```java\nint count = 1;\n"
        "while (x > 1) {\n    int p = spf[x], e = 0;\n    while (x % p == 0) { x /= p; e++; }\n"
        "    count *= e + 1;\n}\n```\n\n"
        "Each divisor chooses an exponent 0…eᵢ for each prime independently, hence the product.\n\n"
        "## Cost\nThe sieve is O(M log log M). Each query divides x down to 1, and every division "
        "at least halves it: O(log x). Total well under 10⁷ steps."
    ),
    py='''
def solve(a):
    m = max(a)
    spf = list(range(m + 1))
    i = 2
    while i * i <= m:
        if spf[i] == i:
            for j in range(i * i, m + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    out = []
    for x in a:
        c = 1
        while x > 1:
            p = spf[x]
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            c *= e + 1
        out.append(c)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] a) {
        int m = 1;
        for (int x : a) m = Math.max(m, x);
        int[] spf = new int[m + 1];
        for (int i = 2; i <= m; i++) {
            if (spf[i] != 0) continue;
            for (int j = i; j <= m; j += i)
                if (spf[j] == 0) spf[j] = i;
        }
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < a.length; k++) {
            int x = a[k], c = 1;
            while (x > 1) {
                int p = spf[x], e = 0;
                while (x % p == 0) { x /= p; e++; }
                c *= e + 1;
            }
            if (k > 0) sb.append(' ');
            sb.append(c);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n1 12 7 36 100\n"),
        ("Example 2", "3\n2 4 8\n"),
    ],
    hidden=[
        ("Just one", "1\n1\n"),
        ("Primes", "6\n2 3 5 7 11 13\n"),
        ("Highly composite", "4\n720720 997920 831600 1000000\n"),
        ("Large prime", "2\n999983 999979\n"),
        ("Mixed", "8\n30 64 81 97 210 1024 2310 999999\n"),
        ("Many values", str(2000) + "\n" + " ".join(str(v) for v in _lcg_ints(4242, 2000, 1, 1000000)) + "\n"),
    ],
    expl=[
        "1 has one divisor; 12 = 2²·3 has 3·2 = 6; 7 has 2; 36 = 2²·3² has 9; 100 = 2²·5² has 9.",
        "2, 4 and 8 are 2¹, 2², 2³: 2, 3 and 4 divisors.",
    ],
    prereqs=[
        ("number_theory", "The sieve of Eratosthenes, storing the smallest prime factor instead of a flag."),
        ("arithmetic", "The divisor-count formula: the product of (exponent + 1)."),
    ],
)


_p(
    "coprime-count", "How Many Are Coprime?", "Medium",
    topics=["Math"], subtopics=["Number Theory", "Euler's Totient", "Prime Factorization"],
    companies=["Google", "Bloomberg"],
    shape="n", ret="long",
    todo="factor n by trial division; for each distinct prime p, result -= result / p",
    description=(
        "Count the integers `k` with `1 ≤ k ≤ n` that share no factor with `n` other than 1 — "
        "that is, `gcd(k, n) = 1`.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe count."
    ),
    constraints="1 ≤ n ≤ 10^12",
    hints=[
        "Counting gcd(k, n) for every k is O(n log n) — far too slow at 10¹².",
        "Which k are *not* coprime? Those divisible by some prime factor of n. Only the distinct primes of n matter.",
        "For each distinct prime p of n, exactly a 1/p fraction of the survivors is divisible by p. So start from n and apply `result -= result / p` per prime.",
    ],
    opt=("O(√n)", "O(1)",
         "Trial-division factorisation; the product formula is one step per distinct prime."),
    editorial=(
        "## The one thing this teaches\n**Count the complement through the factorisation.** "
        "φ(n) — Euler's totient — depends only on n's distinct primes:\n\n"
        "φ(n) = n · ∏ (1 − 1/p) over the distinct primes p dividing n.\n\n"
        "## Approach\n```java\nlong result = n;\nfor (long p = 2; p * p <= n; p++) {\n"
        "    if (n % p != 0) continue;\n    while (n % p == 0) n /= p;\n"
        "    result -= result / p;              // remove the multiples of p\n}\n"
        "if (n > 1) result -= result / n;       // one prime above the square root\n```\n\n"
        "`result -= result / p` is `result · (1 − 1/p)` in exact integer arithmetic: result is "
        "always divisible by p at that point, because it still contains p's full power from n.\n\n"
        "## Why the product formula\nBy the Chinese remainder theorem, choosing k mod n is the "
        "same as choosing k mod each prime power independently, and k is coprime to pᵉ exactly "
        "when p ∤ k — a (1 − 1/p) fraction.\n\n"
        "## Where it is used\nFermat's inverse generalises to Euler's: a^φ(m) ≡ 1 (mod m) when "
        "gcd(a, m) = 1. And the number of reduced fractions with denominator n is φ(n)."
    ),
    py='''
def solve(n):
    res = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            res -= res // p
        p += 1
    if n > 1:
        res -= res // n
    return res
''',
    java='''
    static long solve(long n) {
        long res = n;
        for (long p = 2; p * p <= n; p++) {
            if (n % p != 0) continue;
            while (n % p == 0) n /= p;
            res -= res / p;
        }
        if (n > 1) res -= res / n;
        return res;
    }
''',
    examples=[
        ("Example 1", "12\n"),
        ("Example 2", "13\n"),
    ],
    hidden=[
        ("One", "1\n"),
        ("Two", "2\n"),
        ("Prime power", "1024\n"),
        ("Square-free", "30030\n"),
        ("Large prime", "999999999989\n"),
        ("Large composite", "963761198400\n"),
        ("Square of a large prime", "999966000289\n"),
    ],
    expl=[
        "1, 5, 7 and 11 are coprime to 12: φ(12) = 12 · (1 − 1/2)(1 − 1/3) = 4.",
        "13 is prime, so every k from 1 to 12 is coprime to it; 13 itself is not.",
    ],
    prereqs=[
        ("number_theory", "Factorise by trial division; φ depends only on the distinct primes."),
        ("arithmetic", "`result -= result / p` is multiplying by (1 − 1/p) without fractions."),
    ],
)


_p(
    "inverse-mod-any", "Undo the Multiplication", "Medium",
    topics=["Math"], subtopics=["Number Theory", "Extended Euclidean Algorithm", "Modular Inverse"],
    companies=["Google", "Microsoft"],
    shape="pairs", ret="String",
    todo="extended Euclid on (a, m): if gcd != 1 print -1, else normalise the coefficient of a into [0, m)",
    description=(
        "Multiplying by `a` modulo `m` can sometimes be undone: there may be an `x` with "
        "`a · x ≡ 1 (mod m)`. For each query, find the one with `0 ≤ x < m`, or report that none "
        "exists. The modulus is **not** necessarily prime.\n\n"
        "### Input\nLine 1: `q`.\nNext `q` lines: `a m`.\n\n### Output\nOne line per query: `x`, "
        "or `-1` if no inverse exists."
    ),
    constraints="1 ≤ q ≤ 100000\n1 ≤ a ≤ 10^9\n2 ≤ m ≤ 10^9",
    hints=[
        "Fermat's `a^(m−2)` only works when m is prime. Here it is not.",
        "An inverse exists exactly when gcd(a, m) = 1. Euclid's algorithm can do more than find the gcd: it can find x, y with a·x + m·y = gcd(a, m).",
        "Run Euclid while carrying the coefficients: each remainder r is kept as a combination `a·s + m·t`. When the remainder reaches gcd = 1, the coefficient of a is the inverse — normalise it into [0, m).",
    ],
    opt=("O(q log m)", "O(1)",
         "The extended Euclidean algorithm takes the same O(log m) steps as plain Euclid."),
    editorial=(
        "## The one thing this teaches\n**Euclid can explain its answer.** Every remainder it "
        "produces is a combination of the two inputs, so tracking the combination costs nothing "
        "extra — and the combination that equals gcd(a, m) is Bézout's identity, "
        "a·x + m·y = gcd(a, m). When the gcd is 1, reducing mod m kills the m·y term and leaves "
        "a·x ≡ 1.\n\n"
        "## Approach (iterative)\n```java\nlong r0 = a, r1 = m, s0 = 1, s1 = 0;   // r = a·s + m·(…)\n"
        "while (r1 != 0) {\n    long q = r0 / r1;\n"
        "    long r2 = r0 - q * r1; r0 = r1; r1 = r2;\n"
        "    long s2 = s0 - q * s1; s0 = s1; s1 = s2;\n}\n"
        "if (r0 != 1) return -1;                  // gcd(a, m) > 1: no inverse\n"
        "return ((s0 % m) + m) % m;\n```\n\n"
        "## The invariant\nBoth rows always satisfy `r = a·s (mod m)`. It holds for the start "
        "rows (a = a·1, m = a·0 mod m), and a new row is the old row minus q times the other, "
        "which preserves it. At the end r0 = gcd, so a·s0 ≡ gcd (mod m).\n\n"
        "## Why no inverse when gcd > 1\nIf g = gcd(a, m) > 1 then a·x − m·y is always a "
        "multiple of g, so it can never equal 1.\n\n"
        "## Cost\nO(log m) per query; the coefficients stay below m in absolute value."
    ),
    py='''
def solve(p):
    out = []
    for a, m in p:
        r0, r1, s0, s1 = a, m, 1, 0
        while r1:
            q = r0 // r1
            r0, r1 = r1, r0 - q * r1
            s0, s1 = s1, s0 - q * s1
        out.append(str(s0 % m) if r0 == 1 else "-1")
    return "\\n".join(out)
''',
    java='''
    static String solve(int[][] p) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < p.length; i++) {
            long a = p[i][0], m = p[i][1];
            long r0 = a, r1 = m, s0 = 1, s1 = 0;
            while (r1 != 0) {
                long q = r0 / r1;
                long r2 = r0 - q * r1; r0 = r1; r1 = r2;
                long s2 = s0 - q * s1; s0 = s1; s1 = s2;
            }
            if (i > 0) sb.append('\\n');
            sb.append(r0 == 1 ? ((s0 % m) + m) % m : -1);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3\n3 10\n4 10\n7 26\n"),
        ("Example 2", "2\n1 2\n5 12\n"),
    ],
    hidden=[
        ("a is a multiple of m", "2\n12 6\n1000000000 1000000000\n"),
        ("a larger than m", "3\n17 5\n1000000000 999999999\n999999999 1000000000\n"),
        ("Prime modulus", "2\n2 999999937\n123456789 999999937\n"),
        ("Powers of two", "4\n3 1024\n5 1024\n6 1024\n1023 1024\n"),
        ("Consecutive numbers", "3\n999999998 999999999\n500000000 999999999\n2 3\n"),
        ("Many queries", str(400) + "\n" + "\n".join(f"{a} {m}" for a, m in zip(_lcg_ints(77, 400, 1, 1000000000), _lcg_ints(78, 400, 2, 1000000000))) + "\n"),
    ],
    expl=[
        "3 · 7 = 21 ≡ 1 (mod 10). 4 shares the factor 2 with 10, so no inverse. 7 · 15 = 105 = 4 · 26 + 1.",
        "Anything times 1 is itself mod 2. 5 · 5 = 25 ≡ 1 (mod 12).",
    ],
    prereqs=[
        ("number_theory", "Euclid's algorithm, extended to carry the coefficient of a."),
        ("modulo", "Normalise a possibly negative coefficient with `((x % m) + m) % m`."),
    ],
)


_p(
    "two-clocks-align", "When Do the Two Buses Meet?", "Hard",
    topics=["Math"], subtopics=["Number Theory", "Chinese Remainder Theorem", "Extended Euclidean Algorithm"],
    companies=["Google", "Jane Street"],
    shape="quad", ret="long",
    todo="g = gcd(m1, m2); if (a2 - a1) % g != 0 → -1; else t = ((a2 - a1) / g) * inverse(m1 / g mod m2 / g) mod (m2 / g), and x = a1 + m1 * t",
    description=(
        "Bus A arrives at minutes `a1, a1 + m1, a1 + 2·m1, …` and bus B at minutes "
        "`a2, a2 + m2, a2 + 2·m2, …`. Find the earliest minute at which both arrive, or report "
        "that they never do.\n\n"
        "### Input\nOne line: `a1 m1 a2 m2`.\n\n### Output\nThe earliest common minute, or `-1`."
    ),
    constraints="1 ≤ m1, m2 ≤ 10^9\n0 ≤ a1 < m1\n0 ≤ a2 < m2",
    hints=[
        "You want x with x ≡ a1 (mod m1) and x ≡ a2 (mod m2). Walking A's arrivals one by one can take up to m2 steps — 10⁹.",
        "Write x = a1 + m1·t. Then you need m1·t ≡ a2 − a1 (mod m2). Let g = gcd(m1, m2): if g does not divide a2 − a1, there is no solution.",
        "Otherwise divide everything by g: (m1/g)·t ≡ (a2 − a1)/g (mod m2/g), where m1/g is now invertible. Solve for t with the extended-Euclid inverse, take t in [0, m2/g), and x = a1 + m1·t is below lcm(m1, m2) ≤ 10¹⁸.",
    ],
    opt=("O(log min(m1, m2))", "O(1)",
         "One gcd and one extended-Euclid inverse."),
    editorial=(
        "## The one thing this teaches\n**Two congruences merge into one.** The Chinese "
        "remainder theorem says that x ≡ a1 (mod m1), x ≡ a2 (mod m2) has either no solution or "
        "exactly one solution modulo lcm(m1, m2). This problem is that merge — including the case "
        "the textbook skips, where the moduli share a factor.\n\n"
        "## Derivation\nEvery x on bus A's timetable is a1 + m1·t. It is on B's when\n\n"
        "m1·t ≡ a2 − a1 (mod m2).\n\n"
        "Let g = gcd(m1, m2). The left side is a multiple of g modulo m2, so a solution needs "
        "g | (a2 − a1). If it does, divide through by g:\n\n"
        "(m1/g)·t ≡ (a2 − a1)/g (mod m2/g),\n\n"
        "and now gcd(m1/g, m2/g) = 1, so m1/g has an inverse modulo m2/g.\n\n"
        "```java\nlong g = gcd(m1, m2), diff = a2 - a1;\nif (diff % g != 0) return -1;\n"
        "long M = m2 / g;\nlong rhs = ((diff / g) % M + M) % M;\n"
        "long t = rhs * inverse((m1 / g) % M, M) % M;   // both factors < M ≤ 10⁹\n"
        "return a1 + m1 * t;                            // < lcm ≤ 10¹⁸\n```\n\n"
        "## Why it is the earliest\nt is the smallest non-negative solution modulo M, and "
        "consecutive solutions for x differ by m1·M = lcm(m1, m2). So x = a1 + m1·t is the "
        "smallest x ≥ a1 on both timetables — and nothing below a1 is on A's.\n\n"
        "## Overflow check\nrhs and the inverse are both below M ≤ 10⁹, so their product is "
        "below 10¹⁸. m1·t < m1·M = lcm ≤ 10¹⁸. Both fit in a `long`; nothing needs `BigInteger`."
    ),
    py='''
def solve(a1, m1, a2, m2):
    from math import gcd
    g = gcd(m1, m2)
    diff = a2 - a1
    if diff % g:
        return -1
    M = m2 // g
    if M == 1:
        return a1
    t = (diff // g) % M * pow(m1 // g % M, -1, M) % M
    return a1 + m1 * t
''',
    java='''
    static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }

    static long inverse(long a, long m) {
        long r0 = a, r1 = m, s0 = 1, s1 = 0;
        while (r1 != 0) {
            long q = r0 / r1;
            long r2 = r0 - q * r1; r0 = r1; r1 = r2;
            long s2 = s0 - q * s1; s0 = s1; s1 = s2;
        }
        return ((s0 % m) + m) % m;
    }

    static long solve(long a1, long m1, long a2, long m2) {
        long g = gcd(m1, m2), diff = a2 - a1;
        if (diff % g != 0) return -1;
        long M = m2 / g;
        if (M == 1) return a1;
        long rhs = ((diff / g) % M + M) % M;
        long t = rhs * inverse((m1 / g) % M, M) % M;
        return a1 + m1 * t;
    }
''',
    examples=[
        ("Example 1", "2 3 3 5\n"),
        ("Example 2", "1 4 2 6\n"),
        ("Example 3", "3 4 1 6\n"),
    ],
    hidden=[
        ("Same bus", "5 7 5 7\n"),
        ("One divides the other", "3 4 11 12\n"),
        ("Conflict when one divides the other", "1 4 2 12\n"),
        ("Every minute", "0 1 999999999 1000000000\n"),
        ("Large coprime", "999999999 1000000000 999999998 999999999\n"),
        ("Large with common factor", "123456789 600000000 423456789 900000000\n"),
        ("Large, common factor, no meeting", "123456788 999999998 456789 499999999\n"),
        ("Near 10^18", "0 999999937 999999936 999999929\n"),
        ("Common factor, no meeting", "1 1000000000 0 500000000\n"),
    ],
    expl=[
        "A arrives at 2, 5, 8, 11, … and B at 3, 8, 13, … — both at minute 8.",
        "A arrives only at odd minutes and B only at even ones (1 + 4t is odd, 2 + 6t is even): they never meet.",
        "A: 3, 7, 11, 15, 19, … B: 1, 7, 13, … gcd(4, 6) = 2 divides 1 − 3, and the first meeting is 7.",
    ],
    prereqs=[
        ("number_theory", "gcd decides whether a solution exists; extended Euclid inverts m1/g modulo m2/g."),
        ("overflow", "Keep every product of two residues below 10¹⁸ so it fits in a long."),
    ],
)


_p(
    "primes-in-window", "Primes in a Window", "Hard",
    topics=["Math"], subtopics=["Number Theory", "Segmented Sieve"],
    companies=["Google", "SPOJ-style"],
    shape="two", ret="long",
    todo="sieve primes up to sqrt(R); for each, cross out its multiples inside [L, R] starting at max(p*p, first multiple >= L); count survivors (1 is not prime)",
    description=(
        "Count the primes `p` with `L ≤ p ≤ R`.\n\n"
        "### Input\nOne line: `L R`.\n\n### Output\nThe number of primes in the window."
    ),
    constraints="1 ≤ L ≤ R ≤ 10^12\nR − L ≤ 1000000",
    hints=[
        "A sieve up to R needs 10¹² flags. Testing each number by trial division is 10⁶ × 10⁶.",
        "A composite x ≤ R has a prime factor ≤ √R ≤ 10⁶. So the only primes you need are those up to √R — sieve them normally.",
        "Keep one flag per number in the window. For each small prime p, cross out its multiples inside [L, R]: start at max(p·p, the first multiple of p that is ≥ L). Everything left, except 1, is prime.",
    ],
    opt=("O((R − L) log log R + √R log log √R)", "O(√R + (R − L))",
         "A small sieve to √R, then each small prime marks its multiples in the window."),
    editorial=(
        "## The one thing this teaches\n**A sieve only needs its crossing-out primes, not its "
        "whole range.** Every composite has a prime factor at most its square root, so the "
        "primes up to √R are enough to cross out every composite in *any* window below R — and "
        "the window can be allocated on its own.\n\n"
        "## Approach\n```java\nint lim = (int) Math.sqrt(R) + 1;\n"
        "boolean[] small = sieve(lim);                // ordinary sieve to √R\n"
        "boolean[] comp = new boolean[(int) (R - L + 1)];\n"
        "for (int p = 2; p <= lim; p++) {\n    if (small[p]) continue;                   // p is not prime\n"
        "    long start = Math.max((long) p * p, (L + p - 1) / p * p);\n"
        "    for (long x = start; x <= R; x += p) comp[(int) (x - L)] = true;\n}\n"
        "long count = 0;\nfor (long x = L; x <= R; x++) if (x >= 2 && !comp[(int) (x - L)]) count++;\n```\n\n"
        "## The two details that decide correctness\n- **Start at max(p², first multiple ≥ L)**, "
        "not at the first multiple ≥ L: when L ≤ p, the first multiple is p itself, and p must "
        "survive.\n- **1 is not prime.** It is never crossed out, so exclude it explicitly.\n\n"
        "## Cost\nThe small sieve is 10⁶ flags. Each small prime p visits (R − L)/p window cells, "
        "and Σ 1/p over primes ≤ 10⁶ is about 3, so the window marking is a few million steps."
    ),
    py='''
def solve(L, R):
    from math import isqrt
    lim = isqrt(R) + 1
    small = bytearray([1]) * (lim + 1)
    small[0] = small[1] = 0
    for i in range(2, isqrt(lim) + 1):
        if small[i]:
            small[i * i::i] = bytes(len(range(i * i, lim + 1, i)))
    seg = bytearray([1]) * (R - L + 1)
    for p in range(2, lim + 1):
        if not small[p]:
            continue
        start = max(p * p, (L + p - 1) // p * p)
        if start > R:
            continue
        seg[start - L::p] = bytes(len(range(start - L, R - L + 1, p)))
    if L <= 1:
        seg[1 - L] = 0
    return sum(seg)
''',
    java='''
    static long solve(long L, long R) {
        int lim = (int) Math.sqrt((double) R) + 1;
        boolean[] notPrime = new boolean[lim + 1];
        notPrime[0] = notPrime[1] = true;
        for (int i = 2; (long) i * i <= lim; i++)
            if (!notPrime[i])
                for (int j = i * i; j <= lim; j += i) notPrime[j] = true;
        boolean[] comp = new boolean[(int) (R - L + 1)];
        for (int p = 2; p <= lim; p++) {
            if (notPrime[p]) continue;
            long start = Math.max((long) p * p, (L + p - 1) / p * p);
            for (long x = start; x <= R; x += p) comp[(int) (x - L)] = true;
        }
        long count = 0;
        for (long x = L; x <= R; x++) if (x >= 2 && !comp[(int) (x - L)]) count++;
        return count;
    }
''',
    examples=[
        ("Example 1", "1 30\n"),
        ("Example 2", "100 120\n"),
    ],
    hidden=[
        ("Just one", "1 1\n"),
        ("Just two", "2 2\n"),
        ("A single composite", "999999999999 999999999999\n"),
        ("A single large prime", "999999999989 999999999989\n"),
        ("Small primes inside the window", "2 1000\n"),
        ("Full window near 10^12", "999999000000 1000000000000\n"),
        ("Full window from 1", "1 1000001\n"),
        ("Mid-range window", "123456789012 123457789012\n"),
    ],
    expl=[
        "2, 3, 5, 7, 11, 13, 17, 19, 23 and 29 — ten primes.",
        "101, 103, 107, 109 and 113.",
    ],
    prereqs=[
        ("number_theory", "The sieve of Eratosthenes, and the fact that every composite has a prime factor ≤ its square root."),
        ("overflow", "Window offsets are `x − L` in long, cast to int only once they are known to be small."),
    ],
)


_p(
    "floor-quotient-sum", "Sum of Floor Quotients", "Hard",
    topics=["Math"], subtopics=["Number Theory", "Divisor Blocks", "Square Root Decomposition"],
    companies=["Google", "Codeforces-style"],
    shape="n", ret="long",
    todo="walk i in blocks: q = n / i is constant for i up to j = n / q; add q * (j - i + 1) and jump to i = j + 1",
    description=(
        "Compute `⌊n/1⌋ + ⌊n/2⌋ + ⌊n/3⌋ + … + ⌊n/n⌋`, where `⌊x⌋` is integer division rounding "
        "down.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe sum."
    ),
    constraints="1 ≤ n ≤ 10^12",
    hints=[
        "A loop over i is 10¹² steps. But how many *different* values does n / i take?",
        "For i ≤ √n there are at most √n values of i. For i > √n, n / i < √n — so at most √n different quotients. Fewer than 2√n distinct values in total.",
        "The i sharing a quotient form a contiguous block: if q = n / i, the last i with that quotient is j = n / q. Add q · (j − i + 1) and jump straight to i = j + 1.",
    ],
    opt=("O(√n)", "O(1)",
         "At most 2√n blocks of equal quotient."),
    editorial=(
        "## The one thing this teaches\n**Group by the answer, not by the input.** ⌊n/i⌋ takes "
        "fewer than 2√n distinct values as i runs to n, and each value is taken on a contiguous "
        "run of i. Summing per run instead of per i turns O(n) into O(√n) — the same √n "
        "argument as divisor pairs, applied to quotients.\n\n"
        "## Approach\n```java\nlong sum = 0;\nfor (long i = 1; i <= n; ) {\n"
        "    long q = n / i;\n    long j = n / q;                 // last i with the same quotient\n"
        "    sum += q * (j - i + 1);\n    i = j + 1;\n}\n```\n\n"
        "## Why j = n / q is the end of the block\nFor i' ≥ i, ⌊n/i'⌋ ≥ q exactly when i' ≤ n/q. "
        "So the largest i' still giving q is ⌊n/q⌋.\n\n"
        "## A second way to see the same number\nThe sum counts pairs (i, k) with i · k ≤ n — "
        "lattice points under the hyperbola. Counting by symmetry about i = k gives "
        "`2 · Σ_{i ≤ √n} ⌊n/i⌋ − ⌊√n⌋²`, also O(√n). It is the number of divisors summed over "
        "1…n, too: each pair (i, k) is a divisor i of the number i·k.\n\n"
        "## Size\nThe sum is about n ln n ≈ 2.8 · 10¹³ at n = 10¹²: `long`, with room to spare."
    ),
    py='''
def solve(n):
    from math import isqrt
    k = isqrt(n)
    return 2 * sum(n // i for i in range(1, k + 1)) - k * k
''',
    java='''
    static long solve(long n) {
        long sum = 0;
        for (long i = 1; i <= n; ) {
            long q = n / i;
            long j = n / q;
            sum += q * (j - i + 1);
            i = j + 1;
        }
        return sum;
    }
''',
    examples=[
        ("Example 1", "5\n"),
        ("Example 2", "10\n"),
    ],
    hidden=[
        ("One", "1\n"),
        ("Two", "2\n"),
        ("A perfect square", "1000000\n"),
        ("One below a square", "999999\n"),
        ("Ten to the ninth", "1000000000\n"),
        ("Largest", "1000000000000\n"),
        ("Odd large", "987654321987\n"),
    ],
    expl=[
        "5 + 2 + 1 + 1 + 1 = 10.",
        "10 + 5 + 3 + 2 + 2 + 1 + 1 + 1 + 1 + 1 = 27.",
    ],
    prereqs=[
        ("number_theory", "Divisor pairs: n / i takes fewer than 2√n distinct values."),
        ("math_digits", "Integer division rounds down; the block end is n / (n / i)."),
    ],
)
