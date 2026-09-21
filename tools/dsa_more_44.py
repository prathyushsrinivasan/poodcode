# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 44 — randomized algorithms, made exactly judgeable.
#
#   weighted-random-picks    sampling from a distribution: prefix sums + binary search
#   shuffle-fisher-yates     the correct shuffle, and the off-by-one that biases it
#   reservoir-sample-stream  a uniform sample of a stream of unknown length
#   miller-rabin-primality   Monte Carlo, then a witness set that makes it certain
#
# A JUDGE CANNOT CHECK A RANDOM ANSWER, so every statement here pins the
# generator: a fixed linear congruential generator with a fixed seed, specified
# in the problem. The algorithm is unchanged and the reasoning about it is
# unchanged; only the coin flips are reproducible, which is also exactly how you
# would write a test for randomized code in production.
#
#   s = (s * 1103515245 + 12345) mod 2^31,  s starts at 12345,  next() -> s
#
# That fits a Java `long` before the mask and a Python int always, so the two
# references agree bit for bit.
# ===========================================================================

_LCG_SPEC = (
    "### The generator\nSo the answer can be checked, randomness comes from this exact "
    "generator. Its state `s` starts at `12345`, and each call updates and returns it:\n\n"
    "```\ns = (s * 1103515245 + 12345) mod 2^31\nnext() = s\n```\n\n"
    "`s * 1103515245` stays below 2⁶¹, so a 64-bit integer holds it before the "
    "`mod`."
)

_p(
    "weighted-random-picks", "Loaded Dice", "Easy",
    topics=["Arrays", "Math"], subtopics=["Randomized Algorithms", "Prefix Sums", "Binary Search"],
    companies=["Amazon", "Meta"],
    shape="arr_k", ret="String",
    todo="prefix-sum the weights once; for each draw take r = next() mod total and binary-search the first prefix greater than r",
    description=(
        "A prize wheel has `n` segments; segment `i` has width `w[i]`, so it is chosen with "
        "probability `w[i] / Σw`. Spin it `T` times and print which segment came up each "
        "time.\n\n"
        "A spin picks the segment containing the point `r = next() mod Σw`, measuring from "
        "0 along the segments in order: segment 0 covers `[0, w[0])`, segment 1 covers "
        "`[w[0], w[0]+w[1])`, and so on.\n\n" + _LCG_SPEC + "\n\n"
        "### Input\nLine 1: `n T`.\nLine 2: `n` positive integers, the widths.\n\n"
        "### Output\nThe `T` chosen segment numbers, separated by single spaces, on one line."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ T ≤ 100000\n1 ≤ w[i]\nΣw ≤ 10^6",
    hints=[
        "Building an array with w[i] copies of i is correct and uses Σw memory — fine at 10⁶, useless at 10¹².",
        "Take the prefix sums of the widths once. Segment i owns the half-open range [prefix[i], prefix[i+1]).",
        "Now each spin is a search: the first index whose prefix *strictly exceeds* r. That is `upper_bound` over the prefix array, O(log n) per spin.",
    ],
    opt=("O(n + T log n)", "O(n)",
         "One prefix-sum pass, then a binary search per draw."),
    editorial=(
        "## The one thing this teaches\n**Sampling from a distribution is a search, not a "
        "loop.** Turn the weights into a ruler (prefix sums), pick a point on it uniformly, and "
        "find which interval swallowed it.\n\n"
        "## Approach\n```java\nlong[] prefix = new long[n + 1];\n"
        "for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + w[i];\n"
        "long total = prefix[n];\n\nfor (int t = 0; t < T; t++) {\n"
        "    long r = next() % total;\n"
        "    int lo = 0, hi = n - 1;                  // first i with prefix[i+1] > r\n"
        "    while (lo < hi) {\n        int mid = (lo + hi) >>> 1;\n"
        "        if (prefix[mid + 1] > r) hi = mid; else lo = mid + 1;\n    }\n"
        "    out.append(lo);\n}\n```\n\n"
        "## Why the intervals are half-open\n`[prefix[i], prefix[i+1])` gives segment i exactly "
        "`w[i]` integers and leaves no point owned by two segments or by none. Closed intervals "
        "double-count every boundary, and a weight of zero would silently become a weight of "
        "one.\n\n"
        "## `>` and not `>=`\nThe boundary point `prefix[i+1]` belongs to segment i+1, so the "
        "predicate that must flip is *strictly greater*. Using `>=` shifts every answer by one "
        "at the boundaries — a bug that appears in maybe one draw in a thousand, which is "
        "the worst kind.\n\n"
        "## Where the randomness went\nThe algorithm is unchanged by fixing the generator: it "
        "consumes one uniform integer per draw and does not care where it came from. That "
        "separation — the algorithm, and the source of randomness — is also how you make "
        "randomized production code testable: inject the generator.\n\n"
        "## The alternative worth knowing\nWalker's **alias method** answers each draw in O(1) "
        "after an O(n) build, using two arrays instead of one. Worth the name if you are asked "
        "to draw millions of samples from a fixed distribution."
    ),
    py='''
def solve(a, k):
    T = int(k)
    n = len(a)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + a[i]
    total = prefix[n]
    s = 12345
    out = []
    for _ in range(T):
        s = (s * 1103515245 + 12345) % (1 << 31)
        r = s % total
        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if prefix[mid + 1] > r:
                hi = mid
            else:
                lo = mid + 1
        out.append(str(lo))
    return " ".join(out)
''',
    java='''
    static long solve_seed;

    static long nextRand() {
        solve_seed = (solve_seed * 1103515245L + 12345L) & 0x7FFFFFFFL;
        return solve_seed;
    }

    static String solve(int[] a, long k) {
        int n = a.length, T = (int) k;
        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];
        long total = prefix[n];
        solve_seed = 12345L;
        StringBuilder sb = new StringBuilder();
        for (int t = 0; t < T; t++) {
            long r = nextRand() % total;
            int lo = 0, hi = n - 1;
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (prefix[mid + 1] > r) hi = mid; else lo = mid + 1;
            }
            if (t > 0) sb.append(' ');
            sb.append(lo);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3 5\n1 1 1\n"),
        ("Example 2", "2 6\n9 1\n"),
    ],
    hidden=[
        ("One segment", "1 4\n7\n"),
        ("A single spin", "4 1\n1 2 3 4\n"),
        ("Very lopsided", "3 10\n1 1 999\n"),
        ("Many equal segments", "8 12\n5 5 5 5 5 5 5 5\n"),
        ("Many spins", "5 50\n3 1 4 1 5\n"),
    ],
    expl=[
        "Three equal segments, so each spin lands on whichever third of [0, 3) the generator points at.",
        "Segment 0 covers [0, 9) and segment 1 only [9, 10), so segment 1 is rare.",
    ],
    prereqs=[
        ("prefix_sum", "Widths turned into boundaries."),
        ("binary_search", "The first boundary past a point."),
        ("modulo", "A uniform integer reduced into a range."),
    ],
)


_p(
    "shuffle-fisher-yates", "Shuffle the Deck", "Medium",
    topics=["Arrays", "Math"], subtopics=["Randomized Algorithms", "Fisher-Yates", "In-Place"],
    companies=["Google", "Amazon", "Meta"],
    shape="arr", ret="String",
    todo="walk i from n-1 down to 1, draw j = next() mod (i + 1), and swap a[i] with a[j]",
    description=(
        "Shuffle a deck of `n` cards with the **Fisher–Yates** algorithm, run exactly as "
        "written here:\n\n"
        "```\nfor i = n-1 down to 1:\n    j = next() mod (i + 1)      // 0 <= j <= i\n"
        "    swap a[i] and a[j]\n```\n\n" + _LCG_SPEC + "\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers, the deck in order.\n\n"
        "### Output\nThe shuffled deck, separated by single spaces, on one line."
    ),
    constraints="1 ≤ n ≤ 100000\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Sorting by a random key works and costs O(n log n). Fisher–Yates is O(n) and needs no extra array.",
        "The loop maintains an invariant: after step i, positions i … n-1 hold a uniformly random selection, in a uniformly random order, and positions 0 … i-1 are still the unshuffled pool.",
        "The range of j is `0 … i` inclusive — a card may be swapped with itself. Excluding that possibility is the classic bug, and it makes the shuffle measurably biased.",
    ],
    opt=("O(n)", "O(1)",
         "One draw and one swap per card, in place."),
    editorial=(
        "## The one thing this teaches\n**Fisher–Yates is the only shuffle worth "
        "memorising**, and the reason is its invariant, not its speed.\n\n"
        "## Approach\n```java\nfor (int i = n - 1; i >= 1; i--) {\n"
        "    int j = (int) (next() % (i + 1));   // inclusive of i\n"
        "    int t = a[i]; a[i] = a[j]; a[j] = t;\n}\n```\n\n"
        "## Why it is uniform\nPosition n−1 gets any of the n cards with probability 1/n. "
        "Given that, position n−2 gets any of the remaining n−1 with probability "
        "1/(n−1). Multiplying down, every one of the n! orders has probability exactly "
        "1/n!. Each step is an independent choice from the shrinking pool, which is precisely "
        "what listing a permutation means.\n\n"
        "## The bug that looks harmless\nDrawing `j` from `0 … n-1` every time instead of "
        "`0 … i` produces nⁿ equally likely execution paths mapped onto n! orders. Since "
        "n! does not divide nⁿ for n > 2, some orders *must* be more likely than others. "
        "For n = 3 the counts come out 4/27 and 5/27 — a 25% bias that no amount of "
        "eyeballing the output will reveal, and that a chi-squared test finds instantly.\n\n"
        "## Which end to walk\nDownwards (swapping into the back) and upwards (`j` in "
        "`i … n-1`, swapping into the front) are both correct. Mixing them up — walking down "
        "while drawing from `i … n-1` — is the biased version again.\n\n"
        "## Las Vegas\nThis is a **Las Vegas** algorithm: the output is always a valid "
        "permutation, and the randomness only decides *which*. Contrast the last problem in this "
        "unit, where the randomness can decide whether the answer is right."
    ),
    py='''
def solve(a):
    b = list(a)
    s = 12345
    for i in range(len(b) - 1, 0, -1):
        s = (s * 1103515245 + 12345) % (1 << 31)
        j = s % (i + 1)
        b[i], b[j] = b[j], b[i]
    return " ".join(str(x) for x in b)
''',
    java='''
    static long shuffle_seed;

    static long nextShuffle() {
        shuffle_seed = (shuffle_seed * 1103515245L + 12345L) & 0x7FFFFFFFL;
        return shuffle_seed;
    }

    static String solve(int[] a) {
        int n = a.length;
        int[] b = Arrays.copyOf(a, n);
        shuffle_seed = 12345L;
        for (int i = n - 1; i >= 1; i--) {
            int j = (int) (nextShuffle() % (i + 1));
            int t = b[i]; b[i] = b[j]; b[j] = t;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(b[i]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n1 2 3 4 5\n"),
        ("Example 2", "1\n42\n"),
    ],
    hidden=[
        ("Two cards", "2\n10 20\n"),
        ("Repeated values", "6\n7 7 7 1 1 1\n"),
        ("Negative values", "4\n-1 -2 -3 -4\n"),
        ("A longer deck", "12\n1 2 3 4 5 6 7 8 9 10 11 12\n"),
        ("Extreme values", "3\n1000000000 -1000000000 0\n"),
    ],
    expl=[
        "Four draws, one per position from the back: each picks a card from the still-unshuffled prefix and swaps it into place.",
        "A one-card deck has nothing to swap, so the loop never runs.",
    ],
    prereqs=[
        ("array_patterns", "An in-place swap."),
        ("modulo", "A draw reduced into a shrinking range."),
        ("inplace_reverse", "Walking an array from the back."),
    ],
)


_p(
    "reservoir-sample-stream", "Keep k From a Firehose", "Medium",
    topics=["Arrays", "Math"], subtopics=["Randomized Algorithms", "Reservoir Sampling", "Streaming"],
    companies=["Google", "Meta", "Amazon"],
    shape="arr_k", ret="String",
    todo="fill the first k slots, then for each later item i draw j = next() mod (i + 1) and overwrite slot j when j < k",
    description=(
        "Log lines arrive one at a time and you may keep only `k` of them. Keep a uniformly "
        "random sample: after every item, each line seen so far must be equally likely to be in "
        "your `k` slots. You may not store the stream and you are not told its length in "
        "advance.\n\n"
        "Run **reservoir sampling** exactly as written here:\n\n"
        "```\nfor i = 0 .. n-1:\n    if i < k:  slot[i] = a[i]\n    else:\n"
        "        j = next() mod (i + 1)\n        if j < k:  slot[j] = a[i]\n```\n\n"
        + _LCG_SPEC + "\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` integers, the stream in order.\n\n"
        "### Output\nThe `k` slots in slot order, separated by single spaces. If `k ≥ n`, "
        "print the whole stream unchanged."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ k ≤ 100000\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Collecting everything and picking at the end needs O(n) memory and the length in advance — both of which the problem forbids.",
        "Keep the first k items. For item i (0-based, i ≥ k), it should end up in the sample with probability k / (i + 1).",
        "Draw `j` uniformly from `0 … i`. The chance that `j < k` is exactly k / (i + 1) — so use j both as the coin and as the slot to overwrite.",
    ],
    opt=("O(n)", "O(k)",
         "One draw per item past the first k; memory is the reservoir and nothing else."),
    editorial=(
        "## The one thing this teaches\n**A uniform sample of a stream you cannot store, in one "
        "pass.** The trick is that the same random number serves as both the acceptance test and "
        "the eviction choice.\n\n"
        "## Why each item survives with probability k/n\nItem i (0-based) enters with "
        "probability k/(i+1). It is then evicted at step t > i only if that step accepts "
        "(probability k/(t+1)) *and* picks i's slot (probability 1/k) — so it survives step "
        "t with probability 1 − 1/(t+1) = t/(t+1). Multiply:\n\n"
        "> `k/(i+1) · (i+1)/(i+2) · (i+2)/(i+3) · … · (n-1)/n = k/n`\n\n"
        "The telescoping is the proof, and the fact that it lands on k/n for *every* i is what "
        "uniform means.\n\n"
        "## The two jobs of one draw\n`j = next() mod (i + 1)` is uniform on `0 … i`. The event "
        "`j < k` has probability exactly k/(i+1) — the acceptance test. And given acceptance, "
        "`j` is uniform on `0 … k-1` — the eviction choice. Drawing two numbers instead is "
        "not wrong, but it is twice the work and the standard form of the algorithm is this "
        "one.\n\n"
        "## The warm-up is not a special case\n`i < k` fills the reservoir. Treating it as "
        "\"accept with probability k/(i+1)\" would give a probability above 1 — the formula "
        "only starts being a probability once the reservoir is full.\n\n"
        "## Where it is used\nSampling log lines at fixed memory, picking a random node from a "
        "linked list in one pass, choosing a random line of a file without reading it twice. "
        "Whenever the population size is unknown *and* memory is bounded, this is the answer."
    ),
    py='''
def solve(a, k):
    k = int(k)
    n = len(a)
    if k >= n:
        return " ".join(str(x) for x in a)
    slot = [0] * k
    s = 12345
    for i in range(n):
        if i < k:
            slot[i] = a[i]
        else:
            s = (s * 1103515245 + 12345) % (1 << 31)
            j = s % (i + 1)
            if j < k:
                slot[j] = a[i]
    return " ".join(str(x) for x in slot)
''',
    java='''
    static long res_seed;

    static long nextRes() {
        res_seed = (res_seed * 1103515245L + 12345L) & 0x7FFFFFFFL;
        return res_seed;
    }

    static String solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        StringBuilder sb = new StringBuilder();
        if (k >= n) {
            for (int i = 0; i < n; i++) { if (i > 0) sb.append(' '); sb.append(a[i]); }
            return sb.toString();
        }
        int[] slot = new int[k];
        res_seed = 12345L;
        for (int i = 0; i < n; i++) {
            if (i < k) {
                slot[i] = a[i];
            } else {
                int j = (int) (nextRes() % (i + 1));
                if (j < k) slot[j] = a[i];
            }
        }
        for (int i = 0; i < k; i++) { if (i > 0) sb.append(' '); sb.append(slot[i]); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "8 3\n1 2 3 4 5 6 7 8\n"),
        ("Example 2", "3 5\n9 8 7\n"),
    ],
    hidden=[
        ("A single slot", "10 1\n1 2 3 4 5 6 7 8 9 10\n"),
        ("Reservoir exactly the stream length", "4 4\n5 6 7 8\n"),
        ("Negative values", "6 2\n-1 -2 -3 -4 -5 -6\n"),
        ("A long stream, small reservoir", "40 4\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40\n"),
        ("Repeated values", "7 3\n4 4 4 4 4 4 4\n"),
    ],
    expl=[
        "The first three items fill the slots; each of the remaining five gets a chance to evict one of them, with the chance shrinking as the stream grows.",
        "The reservoir is larger than the stream, so everything is kept.",
    ],
    prereqs=[
        ("array_patterns", "A fixed-size buffer overwritten in place."),
        ("modulo", "A uniform draw from 0 to i."),
        ("iteration", "One pass, no second look at the data."),
    ],
)


_p(
    "miller-rabin-primality", "Probably Prime, Definitely Prime", "Hard",
    topics=["Math"], subtopics=["Miller-Rabin", "Randomized Algorithms", "Modular Arithmetic"],
    companies=["Google", "Jane Street"],
    shape="larr", ret="String",
    todo="write n-1 as d * 2^r; for each base a, check a^d = 1 or a^(d*2^i) = n-1 for some i < r; use the fixed witness set",
    description=(
        "For each of `q` numbers, print `PRIME` or `COMPOSITE`.\n\n"
        "The numbers reach 10¹⁸, so trial division to √n is 10⁹ steps per "
        "number. Use the **Miller–Rabin** test with the twelve bases\n\n"
        "`2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37`\n\n"
        "which is known to decide primality exactly for every number below "
        "3.3 × 10²⁴.\n\n"
        "### Input\nLine 1: `q`.\nLine 2: `q` integers.\n\n"
        "### Output\nOne line per number: `PRIME` or `COMPOSITE`. (`0` and `1` are neither "
        "prime nor composite in the usual sense; print `COMPOSITE` for them.)"
    ),
    constraints="1 ≤ q ≤ 100\n0 ≤ a[i] ≤ 10^18",
    hints=[
        "Fermat's little theorem says a^(n-1) = 1 mod n when n is prime — but Carmichael numbers like 561 pass that for every coprime base, so the test alone is not enough.",
        "Miller–Rabin strengthens it. Write n-1 = d·2^r with d odd. If n is prime, the square roots of 1 mod n are only ±1, so the sequence a^d, a^(2d), a^(4d) … must reach 1 *through* n-1.",
        "So a base a is a witness that n is composite unless a^d = 1 or one of a^(d·2^i) equals n-1. Test the twelve given bases; if none witnesses, n is prime.",
    ],
    opt=("O(q · 12 · log n)", "O(1)",
         "Twelve modular exponentiations per number, each about 60 squarings."),
    editorial=(
        "## The one thing this teaches\n**A Monte Carlo algorithm and how to stop it being "
        "one.** Miller–Rabin with random bases can be wrong (it may call a composite prime), "
        "with probability below 4⁻ᵏ. With a *fixed, verified* set of bases it is not "
        "probabilistic at all below a known bound — the randomness was replaced by somebody "
        "else's exhaustive search.\n\n"
        "## The test\n```java\nstatic boolean isPrime(long n) {\n"
        "    if (n < 2) return false;\n"
        "    for (long p : new long[]{2,3,5,7,11,13,17,19,23,29,31,37})\n"
        "        if (n % p == 0) return n == p;          // small primes, and the bases themselves\n"
        "    long d = n - 1;\n    int r = 0;\n"
        "    while ((d & 1) == 0) { d >>= 1; r++; }      // n - 1 = d * 2^r, d odd\n\n"
        "    for (long a : BASES) {\n        long x = powMod(a, d, n);\n"
        "        if (x == 1 || x == n - 1) continue;     // this base says nothing\n"
        "        boolean witness = true;\n"
        "        for (int i = 1; i < r; i++) {\n            x = mulMod(x, x, n);\n"
        "            if (x == n - 1) { witness = false; break; }\n        }\n"
        "        if (witness) return false;              // proof that n is composite\n    }\n"
        "    return true;\n}\n```\n\n"
        "## Why squaring down to 1 must pass through n-1\nIn a field, `x² = 1` has exactly "
        "two solutions, 1 and −1. Z/nZ is a field only when n is prime. So if the sequence "
        "of repeated squares reaches 1 without the previous value being n−1, a non-trivial "
        "square root of 1 exists — and that is a *proof* that n is composite. A witness is "
        "not evidence; it is a certificate.\n\n"
        "## Why Fermat alone fails\n561 = 3·11·17 satisfies a⁵⁶⁰ = 1 for "
        "every a coprime to it. Carmichael numbers are Fermat liars for every base, and there "
        "are infinitely many. Miller–Rabin catches 561 immediately, because the extra "
        "square-root condition is not something a composite can fake for many bases.\n\n"
        "## The multiplication trap\n`a * b % n` overflows a 64-bit integer as soon as n passes "
        "about 3·10⁹ — and it fails *silently*, giving a wrong answer for large "
        "inputs only. Use 128-bit multiplication, `Math.multiplyHigh`, `BigInteger`, or "
        "Python's unbounded integers. This is the single thing that breaks a correct-looking "
        "implementation at 10¹⁸.\n\n"
        "## Las Vegas versus Monte Carlo, in one line\nA Las Vegas algorithm is always right and "
        "randomly slow (quickselect, the shuffle above). A Monte Carlo algorithm is always fast "
        "and randomly wrong (Miller–Rabin with random bases). Knowing which one you are "
        "shipping determines whether you need a fallback."
    ),
    py='''
def solve(a):
    BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)

    def is_prime(n):
        if n < 2:
            return False
        for p in BASES:
            if n % p == 0:
                return n == p
        d = n - 1
        r = 0
        while d % 2 == 0:
            d //= 2
            r += 1
        for base in BASES:
            x = pow(base, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = x * x % n
                if x == n - 1:
                    break
            else:
                return False
        return True

    return "\\n".join("PRIME" if is_prime(v) else "COMPOSITE" for v in a)
''',
    java='''
    static final long[] BASES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};

    static boolean isPrime(long n) {
        if (n < 2) return false;
        for (long p : BASES) if (n % p == 0) return n == p;
        long d = n - 1;
        int r = 0;
        while ((d & 1L) == 0L) { d >>= 1; r++; }
        java.math.BigInteger big = java.math.BigInteger.valueOf(n);
        java.math.BigInteger dd = java.math.BigInteger.valueOf(d);
        for (long base : BASES) {
            java.math.BigInteger x = java.math.BigInteger.valueOf(base).modPow(dd, big);
            if (x.equals(java.math.BigInteger.ONE) || x.equals(big.subtract(java.math.BigInteger.ONE)))
                continue;
            boolean witness = true;
            for (int i = 1; i < r; i++) {
                x = x.multiply(x).mod(big);
                if (x.equals(big.subtract(java.math.BigInteger.ONE))) { witness = false; break; }
            }
            if (witness) return false;
        }
        return true;
    }

    static String solve(long[] a) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < a.length; i++) {
            if (i > 0) sb.append('\\n');
            sb.append(isPrime(a[i]) ? "PRIME" : "COMPOSITE");
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n2 15 97 561 1000003\n"),
        ("Example 2", "3\n0 1 4\n"),
    ],
    hidden=[
        ("Carmichael numbers, which fool Fermat", "4\n561 1105 1729 2465\n"),
        ("Squares of primes", "4\n9 49 1000003 1000006000009\n"),
        ("Large primes", "3\n999999000001 1000000007 2147483647\n"),
        ("The largest inputs", "4\n1000000000000000003 999999999999999989 1000000000000000000 999999999999999999\n"),
        ("A run of small numbers", "10\n2 3 4 5 6 7 8 9 10 11\n"),
    ],
    expl=[
        "2 and 97 are prime; 15 = 3·5; 561 = 3·11·17 is a Carmichael number that passes the plain Fermat test but not this one; 1000003 is prime.",
        "0 and 1 are not prime, and 4 = 2·2.",
    ],
    prereqs=[
        ("number_theory", "Fermat's little theorem, and why it is not sufficient."),
        ("modulo", "Modular exponentiation by squaring."),
        ("overflow", "a·b mod n past 3·10^9 needs more than 64 bits."),
    ],
)
