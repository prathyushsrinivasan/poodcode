# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 3 — Order, numbers and bits.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# Stage 2 removed nested loops by reusing work. This stage removes them by
# imposing ORDER — sorting, then exploiting sortedness with binary search — and
# then covers the two "small" topics that are really about representation:
# number theory (what you can compute from a number without looking at it
# digit by digit) and bit manipulation (the same array patterns, on 32 slots
# that live inside a single int).
#
# The matrix/simulation unit closes the stage because it needs no new
# technique at all: it is index arithmetic under pressure, and the discipline
# it teaches — write the transformation down before you code it — is what
# makes the grid traversals in stage 5 tractable.
# ---------------------------------------------------------------------------

_S3 = _stage(
    "search-and-sort", "Order, Numbers & Bits", "🔢",
    "Impose order, then exploit it.",
    """
Sorting costs O(n log n) and buys you an enormous amount: binary search, two
pointers, greedy sweeps, duplicate detection and interval merging all become
available the moment the data is in order. This stage is about knowing what
that purchase is worth and when to make it.

It closes with two units that look like trivia and are not. **Number theory**
is where an O(√n) or O(log n) idea replaces a loop over every value — the first
time the *size of a number* and the *size of the input* clearly part ways. And
**bit manipulation** is the same set of array patterns applied to 32 flags
packed into one `int`, which is how sets get represented when they have to be
fast.
""")


# --- Unit 11 — Sorting ------------------------------------------------------

_unit(
    "sorting", "Sorting & Ordering", "🔡", _S3,
    "What sorting costs, what it buys, and how to sort by something else.",
    prereqs=["arrays-first-pass", "complexity"],
    why="""
You will almost never implement a sort. You will constantly *decide whether to
call one*, and that decision is one of the most reliable dividing lines between
an O(n²) solution and an O(n log n) one.

The other half of this unit is the part interviews actually test: sorting by a
**derived key** — by frequency, by the second element, by a rule with a
tie-break. That is a `Comparator`, and writing one correctly (including not
writing `a - b` for large values) is a small skill with a large payoff.
""",
    model="""
### What a sort costs

`Arrays.sort` on primitives is a dual-pivot quicksort: O(n log n) average, no
extra memory, **not stable**. On objects it is Timsort: O(n log n) worst case,
O(n) extra memory, and **stable** — equal elements keep their relative order.
That difference matters when you sort twice to get a tie-break.

### What it buys

| After sorting | You can |
| --- | --- |
| Duplicates are adjacent | Detect them in one pass |
| Extremes are at the ends | Answer k-th smallest/largest by index |
| Order is monotone | Binary search |
| Intervals share a start order | Merge and sweep them |
| Pairs are directional | Converge two pointers |

### Sorting by a key

```java
Integer[] a = ...;                         // objects, not int[]
Arrays.sort(a, (x, y) -> freq.get(x) - freq.get(y));   // ← subtraction: risky
Arrays.sort(a, Comparator.comparingInt(freq::get));    // ← safe
```

Never subtract inside a comparator unless the values are provably small:
`Integer.MIN_VALUE - 1` overflows and reverses the sign, which corrupts the
sort silently. `Comparator.comparingInt` and `Integer.compare` are safe.

Descending, and with a tie-break:

```java
Arrays.sort(a, Comparator
    .comparingInt(freq::get).reversed()
    .thenComparing(Comparator.naturalOrder()));
```

A comparator must be **consistent**: if `c(x, y) < 0` then `c(y, x) > 0`, and
the relation must be transitive. An inconsistent comparator does not merely
produce a wrong order — Java detects some cases and throws.

### When not to sort

If the values are small integers, counting sort is O(n) and beats it. If you
only need the k largest, a heap is O(n log k). If you only need the k-th,
quickselect is O(n) average. Sorting is the general answer, not always the best
one — and saying so is worth points.
""",
    signals=[
        _sig("“k-th largest / smallest”", "Sort, or a heap, or quickselect",
             "Sorting is O(n log n); a size-k heap is O(n log k); quickselect O(n) average."),
        _sig("“by frequency”, “most common”", "Count, then sort by the count",
             "Two phases: build the map, then order its entries."),
        _sig("“group the equal ones”", "Sort to make them adjacent",
             "Or hash them — hashing is O(n) and sorting is O(n log n)."),
        _sig("Values are small integers or letters", "Counting sort",
             "O(n + k) beats O(n log n) when k is bounded."),
        _sig("“can they all attend?”, intervals", "Sort by start time",
             "Ordering is the precondition for every interval sweep."),
        _sig("Ties must break a particular way", "`thenComparing`", "Chain, never nest `if`s."),
    ],
    skeletons=[
        _sk("Sort and scan",
            "Duplicates, closest pair, k-th by index.",
            """
Arrays.sort(a);
for (int i = 1; i < a.length; i++) {
    if (a[i] == a[i - 1]) { /* duplicate */ }
}
int kthLargest = a[a.length - k];
""",
            "Sortedness makes “equal” mean “adjacent”."),
        _sk("Sort by a derived key",
            "By frequency, by a field, by a computed score.",
            """
Map<Integer, Integer> freq = new HashMap<>();
for (int x : a) freq.merge(x, 1, Integer::sum);

List<Integer> keys = new ArrayList<>(freq.keySet());
keys.sort(Comparator.comparingInt(freq::get).reversed()
                    .thenComparing(Comparator.naturalOrder()));
""",
            "`comparingInt` instead of a subtraction; `thenComparing` for the tie-break."),
        _sk("Counting sort",
            "Small bounded values — O(n), not O(n log n).",
            """
int[] count = new int[MAX + 1];
for (int x : a) count[x]++;
int i = 0;
for (int v = 0; v <= MAX; v++)
    while (count[v]-- > 0) a[i++] = v;
""",
            "Only viable when the value range is comparable to n."),
    ],
    costs=[
        _cost("`Arrays.sort(int[])`", "O(n log n)", "O(log n)", "Quicksort; not stable."),
        _cost("`Arrays.sort(T[])` / `list.sort`", "O(n log n)", "O(n)", "Timsort; stable."),
        _cost("Counting sort", "O(n + k)", "O(k)", "k = value range."),
        _cost("k-th largest via heap", "O(n log k)", "O(k)", "Better than sorting when k ≪ n."),
        _cost("k-th largest via quickselect", "O(n) average", "O(1)", "O(n²) worst case."),
    ],
    pitfalls=[
        _pit("The sorted order is subtly wrong on extreme values",
             "A comparator written as `a - b`, which overflows when the values are far apart.",
             "`Integer.compare(a, b)` or `Comparator.comparingInt(...)`."),
        _pit("“Comparison method violates its general contract!”",
             "The comparator is inconsistent — often a `>=` where `>` was meant, or NaN "
             "in a double comparison.",
             "Make it antisymmetric and transitive; prefer the `Comparator` factories."),
        _pit("Sorting destroys the answer",
             "The problem asks for original indices, which sorting moves.",
             "Sort index pairs, or use hashing instead."),
        _pit("`Arrays.sort` on `int[]` is not stable and the tie-break is lost",
             "Primitive sorts give no stability guarantee.",
             "Box to `Integer[]` and sort with a comparator when order among equals matters."),
        _pit("Sorting to find one element",
             "O(n log n) spent where a single O(n) pass — or a size-k heap — would do.",
             "Ask what you actually need: the max, the top k, or the whole order."),
    ],
    lessons=["sorting", "alg_sorting_basics", "alg_efficient_sorts", "alg_non_comparison_sorts"],
    checks=[
        _chk("Why is `(a, b) -> a - b` a dangerous comparator?",
             "The subtraction can overflow `int` for far-apart values and flip its sign, "
             "silently corrupting the order. `Integer.compare` cannot."),
        _chk("When does counting sort beat a comparison sort?",
             "When the value range k is O(n) or smaller — it is O(n + k), and comparison "
             "sorts cannot beat O(n log n) in general."),
        _chk("You need only the 5 largest of 10⁶ values. Sort?",
             "No. A size-5 min-heap is O(n log k) ≈ O(n), and uses O(k) memory instead of "
             "ordering the whole array."),
        _chk("What does stability mean, and when do you need it?",
             "Equal elements keep their input order. You need it when you sort by one key "
             "and rely on a previous sort to break ties."),
    ],
    interview="""
The sorting question in an interview is almost never "implement quicksort" — it
is "you sorted; did you need to?". Have the three alternatives ready: counting
sort when the range is small, a heap when you want the top k, quickselect when
you want exactly the k-th. Naming the trade-off unprompted is the answer they
are listening for.
""",
    rungs=[
        _rung("Warm up", "Order by something other than the value itself.",
              ["sort-by-frequency"],
              {"sort-by-frequency": "Count first, then sort the keys by their count with a tie-break. The comparator is the whole exercise."}),
        _rung("Core", "Selection problems, where sorting is the baseline and not the best answer.",
              ["kth-largest-element", "kth-smallest", "top-k-frequent"],
              {"kth-largest-element": "Solve by sorting first, then come back after the heaps unit and do it in O(n log k).",
               "top-k-frequent": "Counting plus ordering — the pattern behind almost every “most common” question."}),
    ],
    next_up="""
Sorted data has a superpower this unit has not used yet: you can find anything
in it in O(log n).
""",
)


# --- Unit 12 — Binary search ------------------------------------------------

_unit(
    "binary-search", "Binary Search", "🎯", _S3,
    "Halve the search space — over an array, or over the answer itself.",
    prereqs=["sorting", "complexity"],
    why="""
Binary search is the cheapest big win in algorithms: 20 steps to find one value
among a million, 30 among a billion. Everyone knows the idea. Almost nobody
writes it correctly first time, because the bugs are all in the boundaries —
`<` versus `<=`, `mid` versus `mid + 1`, and the loop that never terminates.

The reason it deserves a unit rather than a paragraph is the second form:
**binary search on the answer**. When a problem asks for the smallest value
that satisfies a monotone predicate, you can binary-search the answer space
even when there is no array at all. That reframing turns a family of apparently
hard problems into ten-line solutions.
""",
    model="""
### Stop writing "find the target"

Write **lower bound** instead: *the first index whose value is ≥ target*. It
answers "does it exist?", "where would I insert it?", "how many are smaller?"
and "what is the first one ≥ x?" — all with one template that has no special
cases.

```java
int lo = 0, hi = n;                 // hi is EXCLUSIVE
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;   // overflow-safe midpoint
    if (a[mid] < target) lo = mid + 1;   // mid cannot be the answer
    else                 hi = mid;       // mid might be the answer
}
return lo;                          // in [0, n]; n means "all are smaller"
```

Why it terminates: `mid < hi` always, so `hi = mid` strictly shrinks the range,
and `lo = mid + 1` obviously does. Why it is correct: the invariant is
*"everything before `lo` is < target, everything from `hi` on is ≥ target"*,
which is preserved by both branches and, at `lo == hi`, is the answer.

Half-open bounds (`hi = n`, not `n - 1`) are what remove the special cases. Use
them.

### Binary search on the answer

If a predicate `ok(x)` is **monotone** — false, false, …, false, true, true, …
— you can binary-search x itself:

```java
long lo = 0, hi = UPPER_BOUND;
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (ok(mid)) hi = mid;          // mid works: look for something smaller
    else         lo = mid + 1;      // mid fails: the answer is larger
}
return lo;                          // the smallest x with ok(x)
```

Integer square root is the toy case: `ok(x)` is `x * x > n`, and the answer is
one before the first x that satisfies it. The pattern scales to "minimum
capacity", "minimum speed", "minimum time" problems — anything where checking a
candidate is easy but constructing the optimum is not.

The only question worth asking is: **is the predicate really monotone?** If
`ok(5)` is true but `ok(6)` is false, the search is invalid.
""",
    signals=[
        _sig("“sorted array” + “find / count / insert”", "Lower bound",
             "One template answers all four questions."),
        _sig("“first / smallest x such that …”", "Binary search on the answer",
             "Provided the predicate is monotone in x."),
        _sig("“minimum capacity / speed / time that works”", "Binary search on the answer",
             "Checking a candidate is easy; finding the optimum directly is not."),
        _sig("n up to 10⁹ but the answer is a single number", "Binary search",
             "O(log n) is the only thing that fits that constraint."),
        _sig("The array is rotated or has a peak", "Binary search on a local comparison",
             "Monotone *enough*: one comparison still discards half."),
    ],
    skeletons=[
        _sk("Lower bound (first index ≥ target)",
            "The one template to memorise. Everything else is built from it.",
            """
int lo = 0, hi = a.length;          // exclusive upper bound
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < target) lo = mid + 1;
    else                 hi = mid;
}
return lo;                          // insertion point; a[lo] == target ⇒ found
""",
            "`a[lo] == target` (after checking `lo < n`) is the existence test."),
        _sk("Binary search on the answer",
            "Smallest feasible value when feasibility is monotone.",
            """
long lo = 0, hi = 2_000_000_000L;
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (feasible(mid)) hi = mid;
    else               lo = mid + 1;
}
return lo;
""",
            "Choose `hi` as a value that is certainly feasible, then prove monotonicity."),
        _sk("Upper bound (first index > target)",
            "Counting occurrences: `upper(t) - lower(t)`.",
            """
int lo = 0, hi = a.length;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] <= target) lo = mid + 1;   // the only change: <= instead of <
    else                  hi = mid;
}
""",
            "One character apart from lower bound, and that is the whole difference."),
    ],
    costs=[
        _cost("Binary search", "O(log n)", "O(1)", "20 steps at n = 10⁶; 30 at 10⁹."),
        _cost("Sort then search once", "O(n log n)", "O(1)", "A linear scan would have been cheaper."),
        _cost("Sort then search q times", "O((n + q) log n)", "O(1)", "Where preprocessing pays off."),
        _cost("Binary search on the answer", "O(log(range) · check)", "O(1)",
              "The feasibility check dominates."),
    ],
    pitfalls=[
        _pit("The loop never terminates",
             "`lo = mid` on a branch where `mid == lo`, so the range stops shrinking.",
             "One branch must use `mid + 1`. With half-open bounds the template is safe."),
        _pit("`mid` overflows on large indices",
             "`(lo + hi) / 2` can exceed `int` range when both are large.",
             "`lo + (hi - lo) / 2`."),
        _pit("Off by one on the found index",
             "Mixing inclusive `hi = n - 1` with a half-open template.",
             "Pick half-open (`hi = n`) and keep it everywhere."),
        _pit("Binary search on a non-monotone predicate",
             "The feasibility test is true, then false, then true again.",
             "Prove the monotonicity in a sentence before writing the loop."),
        _pit("Searching an unsorted array",
             "The precondition was never checked.",
             "Sort first (and account for the O(n log n)), or use hashing."),
    ],
    lessons=["binary_search", "alg_binary_search", "alg_linear_search"],
    checks=[
        _chk("What exactly does the lower-bound template return when the target is absent?",
             "The insertion point — the index where the target would go to keep the array "
             "sorted. It can be `n`, meaning every element is smaller."),
        _chk("Why is `lo + (hi - lo) / 2` preferred over `(lo + hi) / 2`?",
             "The sum can overflow `int` when both indices are large; the difference cannot."),
        _chk("How do you count occurrences of a value with binary search?",
             "`upperBound(t) - lowerBound(t)` — the two templates differ by a single "
             "`<` versus `<=`."),
        _chk("What has to be true to binary-search the *answer* rather than an array?",
             "The feasibility predicate must be monotone: once it becomes true it stays "
             "true as the candidate grows (or the reverse, consistently)."),
    ],
    interview="""
Binary search is where interviewers watch you handle boundaries under mild
pressure, so having one memorised template that you never modify is worth more
than cleverness. And when a problem says *"minimum X such that it is possible"*,
saying "that predicate looks monotone, so I can binary-search the answer and
just write the feasibility check" is one of the highest-signal sentences in the
whole interview vocabulary.
""",
    rungs=[
        _rung("Core", "The template, and the insertion-point reading of it.",
              ["binary-search-first", "search-insert-position"],
              {"binary-search-first": "Duplicates are the point: you want the *first* match, which is exactly lower bound.",
               "search-insert-position": "The same code with nothing removed — the return value already is the insertion point."}),
        _rung("Variations", "Searching a space that is not an array.",
              ["integer-sqrt"],
              {"integer-sqrt": "No array anywhere. The predicate is `mid * mid > n`, and `mid * mid` must be computed in `long`."}),
    ],
    next_up="""
Both remaining units in this stage are about the *representation* of a number
rather than a collection of them — first its factors, then its bits.
""",
)


# --- Unit 13 — Math and number theory ---------------------------------------

_unit(
    "math-number-theory", "Math & Number Theory", "🧮", _S3,
    "Divisors, primes and gcd — in O(√n) and O(log n), not O(n).",
    prereqs=["loops-and-digits"],
    why="""
Number-theory problems are the clearest example of the distinction that Big-O
makes and casual thinking does not: the difference between *how many numbers
you have* and *how large a number is*. Testing whether n is prime by trying
every candidate below it is O(n); stopping at √n is O(√n), and for n = 10⁹ that
is the difference between a billion operations and thirty thousand.

The two facts this unit is built on — trial division up to √n, and Euclid's
algorithm — carry a surprising amount of weight, and both have one-line proofs
worth knowing.
""",
    model="""
### Divisors come in pairs

If `d` divides `n`, so does `n / d`, and one of the pair is always ≤ √n. So
every divisor question is answered by a loop to √n:

```java
for (long d = 1; d * d <= n; d++) {
    if (n % d == 0) {
        count += (d == n / d) ? 1 : 2;     // perfect square counts once
    }
}
```

**Primality** is the same loop with an early exit: n is prime if nothing in
`2 … √n` divides it. Handle `n < 2` first — 0 and 1 are not prime, and that
special case is the most common wrong answer.

`d * d <= n` rather than `d <= Math.sqrt(n)`: exact integer arithmetic, no
floating-point rounding at the boundary.

### Counting primes: the sieve

For *all* primes below n, trial division per number is O(n√n). The Sieve of
Eratosthenes is O(n log log n) — effectively linear:

```java
boolean[] composite = new boolean[n];
for (int i = 2; (long) i * i < n; i++)
    if (!composite[i])
        for (long j = (long) i * i; j < n; j += i)
            composite[(int) j] = true;
```

Start crossing out at `i * i`, because every smaller multiple of `i` already has
a smaller prime factor and was crossed out earlier. Note the `long` in the inner
loop: `i * i` overflows `int` for i beyond ~46,000.

### Euclid's algorithm

```java
static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }
```

Correct because any common divisor of `a` and `b` also divides `a % b`, so the
set of common divisors never changes. Fast because the remainder at least halves
every two steps: O(log min(a, b)).

From it: `lcm(a, b) = a / gcd(a, b) * b` — **divide before multiplying**, or the
product overflows on the way.

`gcd` over an array is a fold: `g = gcd(g, x)` starting from 0, since
`gcd(0, x) = x`.

### Modular arithmetic

Addition and multiplication distribute over `%`, so you can reduce at every step
and never overflow:

```java
result = (result * base) % MOD;      // both operands must be long
```

Subtraction needs care: `(a - b) % MOD` can be negative in Java, so write
`((a - b) % MOD + MOD) % MOD`.
""",
    signals=[
        _sig("“is it prime?”, “how many divisors?”", "Loop to √n",
             "Divisors pair up around the square root."),
        _sig("“all primes below n”", "Sieve of Eratosthenes",
             "O(n log log n) beats n separate primality tests."),
        _sig("“simplify the fraction”, “common divisor”", "Euclid's gcd",
             "O(log n), and lcm follows from it."),
        _sig("“answer modulo 10⁹+7”", "Reduce at every step",
             "Keeps everything inside `long` with no overflow."),
        _sig("“fewest coins” with standard denominations", "Greedy, largest first",
             "Only valid for canonical systems — otherwise it is a DP problem."),
        _sig("“a^b with huge b”", "Fast exponentiation by squaring",
             "O(log b); see the recursion unit."),
    ],
    skeletons=[
        _sk("Trial division to √n",
            "Primality, divisor counting, divisor sums.",
            """
static boolean isPrime(long n) {
    if (n < 2) return false;
    for (long d = 2; d * d <= n; d++)
        if (n % d == 0) return false;
    return true;
}
""",
            "`d * d <= n` keeps it in exact integer arithmetic."),
        _sk("Sieve of Eratosthenes",
            "Every prime below n, once.",
            """
boolean[] composite = new boolean[n];
int count = 0;
for (int i = 2; i < n; i++) {
    if (composite[i]) continue;
    count++;
    for (long j = (long) i * i; j < n; j += i) composite[(int) j] = true;
}
""",
            "Start at `i * i`, and compute it in `long`."),
        _sk("Euclid's gcd (and lcm)",
            "Fractions, common periods, array-wide gcd.",
            """
static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }

long lcm = a / gcd(a, b) * b;      // divide FIRST to avoid overflow
""",
            "Fold with `g = gcd(g, x)` from 0 to get the gcd of a whole array."),
        _sk("Greedy change with canonical coins",
            "US/EU denominations, where greedy is provably optimal.",
            """
int[] coins = {25, 10, 5, 1};
int used = 0;
for (int c : coins) { used += amount / c; amount %= c; }
""",
            "Valid only for canonical systems — `{1, 3, 4}` and amount 6 defeats it."),
    ],
    costs=[
        _cost("Trial division", "O(√n)", "O(1)", "~31,623 steps at n = 10⁹."),
        _cost("Sieve to n", "O(n log log n)", "O(n)", "Effectively linear."),
        _cost("Euclid's gcd", "O(log min(a, b))", "O(1)", "O(log n) stack if recursive."),
        _cost("Fast exponentiation", "O(log b)", "O(1)", "See the recursion unit."),
        _cost("Naive primality to n", "O(n)", "O(1)", "The version to stop writing."),
    ],
    pitfalls=[
        _pit("1 is reported as prime",
             "The `n < 2` guard is missing.",
             "Handle 0 and 1 before the loop; both are non-prime by definition."),
        _pit("The divisor count is one too high for perfect squares",
             "`d` and `n / d` are the same number when `d * d == n`, and both were counted.",
             "Add 1 rather than 2 in that case."),
        _pit("The sieve overflows or silently skips",
             "`i * i` computed in `int` wraps negative for i beyond ~46,340.",
             "Compute the inner start in `long`."),
        _pit("`lcm` overflows",
             "`a * b` was computed before dividing by the gcd.",
             "`a / gcd(a, b) * b` — the division is exact, so ordering is safe."),
        _pit("A modular result comes out negative",
             "Java's `%` keeps the sign of the left operand after a subtraction.",
             "`((x % MOD) + MOD) % MOD`."),
        _pit("Greedy change returns too many coins",
             "The denominations are not canonical, so greedy is not optimal.",
             "Use the coin-change DP from the DP unit."),
    ],
    lessons=["number_theory", "math_digits", "modulo"],
    checks=[
        _chk("Why is it enough to test divisors up to √n?",
             "Divisors pair as `d × n/d`, and in every pair one member is ≤ √n. A factor "
             "above √n therefore implies one below it, already tested."),
        _chk("Why does the sieve's inner loop start at `i * i`?",
             "Every multiple `i·k` with `k < i` has a prime factor smaller than `i` and was "
             "crossed out when that factor was processed."),
        _chk("Why is `gcd(a, b) == gcd(b, a % b)`?",
             "Any common divisor of `a` and `b` divides `a - qb = a % b`, and conversely, so "
             "the set of common divisors is unchanged. The remainder shrinks fast, giving "
             "O(log n)."),
        _chk("Why compute `lcm` as `a / gcd * b` rather than `a * b / gcd`?",
             "`a * b` can overflow before the division happens. Dividing first is exact "
             "because the gcd divides `a`."),
        _chk("When is greedy coin change correct?",
             "Only for canonical denomination systems such as `{1, 5, 10, 25}`. For "
             "arbitrary coin sets it can be wrong, and dynamic programming is required."),
    ],
    interview="""
Pure number theory is rare in interviews, but √n and gcd show up as *steps*
inside larger problems — and the follow-up is always "why is that enough?".
Both proofs above are one sentence long, and being able to produce them
distinguishes someone who knows the trick from someone who knows why it works.
""",
    rungs=[
        _rung("Warm up", "Divisibility, and a greedy that happens to be optimal.",
              ["is-multiple", "count-divisors", "us-coins-change"],
              {"count-divisors": "The √n loop, including the perfect-square case that is counted once, not twice.",
               "us-coins-change": "Greedy works here because the denominations are canonical. Note *why*, because the coin-change DP later is the same problem without that property."}),
        _rung("Core", "Trial division and Euclid.",
              ["gcd", "is-prime", "perfect-number"],
              {"is-prime": "Guard `n < 2` first, then loop while `d * d <= n`.",
               "perfect-number": "A divisor-sum problem: collect both members of each divisor pair in the same √n loop."}),
        _rung("Variations", "Batch versions of both.",
              ["count-primes", "gcd-of-array"],
              {"count-primes": "The sieve. Testing each number separately is the O(n√n) solution you are replacing.",
               "gcd-of-array": "A fold. `gcd(0, x) == x` makes 0 the right starting accumulator."}),
    ],
    next_up="""
One more representation to go: the bits an integer is actually made of.
""",
)


# --- Unit 14 — Bit manipulation ---------------------------------------------

_unit(
    "bit-manipulation", "Bit Manipulation", "🔟", _S3,
    "32 flags in one int, and the XOR trick that cancels pairs.",
    prereqs=["loops-and-digits"],
    why="""
An `int` is 32 booleans. Once you see it that way, a set of up to 32 elements
becomes a single number you can compare, hash, store in an array and pass
around for free — which is the foundation of bitmask dynamic programming later,
and the reason subset enumeration is written the way it is.

The immediate payoff is smaller and sharper: **XOR cancels pairs**. Problems
that look like they need a hash map — "every element appears twice except one" —
collapse to a single accumulator and O(1) space.
""",
    model="""
### The operators

| Expression | Meaning |
| --- | --- |
| `a & b` | 1 where **both** are 1 — masking, testing |
| `a \\| b` | 1 where **either** is 1 — setting |
| `a ^ b` | 1 where they **differ** — toggling, cancelling |
| `~a` | flip every bit |
| `a << k` | multiply by 2ᵏ |
| `a >> k` | divide by 2ᵏ, **sign-extending** |
| `a >>> k` | divide by 2ᵏ, shifting in zeros |

### The four idioms

```java
boolean isSet = (x & (1 << i)) != 0;   // test bit i
x |= (1 << i);                         // set bit i
x &= ~(1 << i);                        // clear bit i
x ^= (1 << i);                         // toggle bit i
```

### Why XOR is special

Three properties, and every XOR trick follows from them:

- `x ^ x == 0` — a value cancels itself
- `x ^ 0 == x` — zero is the identity
- it is commutative and associative — **order does not matter**

So XOR-ing an entire array where every value appears twice except one leaves
exactly the odd one out. Same idea for the missing number in `0…n`: XOR the
indices and the values together and everything pairs off but the absentee.

### Two more worth memorising

```java
x & (x - 1)     // clears the lowest set bit
x & -x          // isolates the lowest set bit
```

`x & (x - 1) == 0` tests for a power of two (plus a `x > 0` guard, because 0
passes and is not one). Repeatedly clearing the lowest set bit counts the bits
in O(number of set bits) — Kernighan's algorithm.

### Counting bits for every number

`countBits[i] = countBits[i >> 1] + (i & 1)`: i without its last bit, plus that
bit. That is a one-line DP, and it is the bridge to the DP stage.

### The traps

Shifts on `int` use only the low 5 bits of the count, so `1 << 32` is `1`, not
0. Use `1L << k` whenever k can reach 32. And `>>` sign-extends, so a negative
value shifted right stays negative forever — use `>>>` when you are treating
the int as raw bits.
""",
    signals=[
        _sig("“every element appears twice except one”", "XOR the whole array",
             "Pairs cancel; the survivor is the answer. O(1) space."),
        _sig("“the missing number from 0…n”", "XOR indices with values",
             "Or use the sum formula — XOR cannot overflow."),
        _sig("“count the set bits”", "`x & (x - 1)` in a loop, or `Integer.bitCount`",
             "Clears one set bit per iteration."),
        _sig("“is it a power of two?”", "`x > 0 && (x & (x - 1)) == 0`",
             "A power of two has exactly one set bit."),
        _sig("“all subsets”, n ≤ 20ish", "Iterate masks `0 … (1 << n) - 1`",
             "Each mask is one subset; bit i means element i is in."),
        _sig("“for every i from 0 to n, count bits”", "`dp[i] = dp[i >> 1] + (i & 1)`",
             "One pass, and your first DP recurrence."),
    ],
    skeletons=[
        _sk("XOR fold",
            "The unpaired element; the missing number.",
            """
int x = 0;
for (int v : a) x ^= v;      // pairs cancel, the loner remains
""",
            "For “missing from 0…n”, also XOR in every index."),
        _sk("Kernighan bit count",
            "Population count, Hamming weight.",
            """
int count = 0;
while (x != 0) { x &= (x - 1); count++; }   // clears the lowest set bit
""",
            "Loops once per *set* bit, not once per bit."),
        _sk("Test / set / clear",
            "Using an int as a set of up to 32 elements.",
            """
boolean has = (mask & (1 << i)) != 0;
mask |= (1 << i);
mask &= ~(1 << i);
""",
            "`1L << i` when i may reach 32 or beyond."),
        _sk("Enumerate all subsets",
            "Brute force over subsets when n ≤ ~20.",
            """
for (int mask = 0; mask < (1 << n); mask++) {
    for (int i = 0; i < n; i++)
        if ((mask & (1 << i)) != 0) { /* element i is in this subset */ }
}
""",
            "2ⁿ · n total. The backtracking unit builds the same subsets recursively."),
    ],
    costs=[
        _cost("Any single bit operation", "O(1)", "O(1)", "One machine instruction."),
        _cost("XOR fold over an array", "O(n)", "O(1)", "Beats a hash map's O(n) space."),
        _cost("Kernighan count", "O(set bits)", "O(1)", "≤ 32 iterations."),
        _cost("`dp[i] = dp[i >> 1] + (i & 1)` for all i ≤ n", "O(n)", "O(n)", "One pass."),
        _cost("Enumerating all subsets", "O(2ⁿ · n)", "O(1)", "Only for n ≤ ~20."),
    ],
    pitfalls=[
        _pit("`1 << 32` gives 1 instead of 0",
             "Java masks the shift count to 5 bits for `int` (6 for `long`).",
             "Use `1L << k` whenever k can reach 32."),
        _pit("A right shift of a negative number never reaches 0",
             "`>>` sign-extends, so the sign bit keeps refilling.",
             "Use `>>>` when treating the value as raw bits."),
        _pit("A test of `x & mask == 0` behaves oddly",
             "`==` binds tighter than `&` in Java, so it parses as `x & (mask == 0)`.",
             "Parenthesise: `(x & mask) == 0`."),
        _pit("0 is reported as a power of two",
             "`(x & (x - 1)) == 0` is true for 0.",
             "Add the `x > 0` guard."),
        _pit("XOR gives the wrong answer when values repeat three times",
             "XOR cancels *pairs*; a triple leaves one copy behind.",
             "Use counting (or bitwise counts mod 3) when the multiplicity is not two."),
    ],
    lessons=["bit_manip"],
    checks=[
        _chk("Why does XOR-ing an array where every value appears twice leave the loner?",
             "XOR is commutative and associative and `x ^ x == 0`, so order is irrelevant "
             "and every pair annihilates, leaving `0 ^ loner`."),
        _chk("What does `x & (x - 1)` do, and what does it test?",
             "It clears the lowest set bit. Being 0 afterwards means x had exactly one set "
             "bit — a power of two, given `x > 0`."),
        _chk("Why is `1 << 32` equal to 1 in Java?",
             "Shift counts on `int` are taken modulo 32, so 32 becomes 0. Use `1L << 32`."),
        _chk("Explain `dp[i] = dp[i >> 1] + (i & 1)`.",
             "`i >> 1` is i without its lowest bit — a smaller, already-computed value — and "
             "`i & 1` adds that bit back. It is a recurrence, i.e. dynamic programming."),
    ],
    interview="""
Bit tricks are a bonus, not a core competency: the wrong move is opening with
one where a hash map is clearer. The right move is offering it as the follow-up
— *"if you want O(1) space and each value appears exactly twice, XOR does it"* —
and being able to say why the algebra works.
""",
    rungs=[
        _rung("Warm up", "Read the bits of a single number.",
              ["number-of-1-bits", "power-of-two"],
              {"number-of-1-bits": "Do it with Kernighan's `x &= x - 1` rather than shifting 32 times."}),
        _rung("Core", "XOR as a cancelling accumulator.",
              ["single-number", "missing-number"],
              {"missing-number": "Two solutions: the sum formula and the XOR fold. XOR cannot overflow, which is the argument for it."}),
        _rung("Stretch", "Bits as a recurrence.",
              ["count-bits"],
              {"count-bits": "`dp[i] = dp[i >> 1] + (i & 1)`. Your first dynamic program, hiding inside a bit problem."}),
    ],
    next_up="""
One unit left in this stage, and it introduces no new technique at all — only
the index discipline that grid problems demand.
""",
)


# --- Unit 15 — Simulation and matrices --------------------------------------

_unit(
    "simulation-and-matrix", "Simulation & Matrices", "🎛️", _S3,
    "Follow the rules exactly, on a grid, without breaking your own indices.",
    prereqs=["arrays-first-pass", "loops-and-digits"],
    why="""
Some problems have no trick. They describe a process — a robot walking, cells
updating, a matrix rotating — and the work is to execute it *exactly*, which is
harder than it sounds because the failure mode is subtle: you overwrite a value
you still needed, or you update a cell and then read it again in the same step.

This unit is also where 2-D index arithmetic becomes automatic. The neighbour
loop, the bounds check and the transpose-then-reverse identity are the
vocabulary that every grid traversal in stage 5 assumes you already have.
""",
    model="""
### Grid vocabulary

```java
int rows = g.length, cols = g[0].length;

int[][] DIRS = {{-1,0},{1,0},{0,-1},{0,1}};        // 4-directional
for (int[] d : DIRS) {
    int ni = i + d[0], nj = j + d[1];
    if (ni < 0 || ni >= rows || nj < 0 || nj >= cols) continue;   // bounds FIRST
    ...
}
```

The bounds check comes **before** the read, always. Eight neighbours is the same
loop with `{-1,0,1} × {-1,0,1}` minus the `(0,0)` centre.

### The in-place trap

When the update rule reads neighbours, updating a cell immediately corrupts the
reads of its neighbours. Three ways out, in increasing order of cleverness:

1. **Write to a copy**, then swap. Always correct, costs O(n·m).
2. **Two passes with an encoding**: store both old and new state in one cell
   (e.g. old value + 2 × new value), then divide out on a second pass. O(1)
   extra space.
3. **Mark in the margins**: use row 0 and column 0 as flags, as in
   `set-matrix-zeroes`. Cheapest and the easiest to get wrong.

Start with the copy. Do the clever version only when asked for O(1) space, and
say why it works before you write it.

### Rotation

Rotating a square matrix 90° clockwise:

```
transpose (swap a[i][j] with a[j][i], j > i)  →  reverse each row
```

Writing the two-step identity down is far more reliable than trying to derive
`a[j][n-1-i]` under pressure.

### Spiral traversal

Keep four boundaries — `top`, `bottom`, `left`, `right` — walk one edge, then
move that boundary inward. The subtlety is that after the top row and right
column, you must re-check `top <= bottom` and `left <= right` before walking
back, or a single remaining row is emitted twice.

### Rotating an array by k

Three reversals: reverse the whole thing, reverse the first k, reverse the rest.
O(1) space and no modular index juggling. Normalise `k %= n` first, or the
reversal bounds go out of range.
""",
    signals=[
        _sig("“each step, every cell becomes …”", "Copy, or encode two states in one cell",
             "Simultaneous updates cannot be done in place naively."),
        _sig("“rotate the matrix 90°”", "Transpose, then reverse each row",
             "Two simple steps beat one hard index formula."),
        _sig("“spiral order”", "Four shrinking boundaries",
             "Re-check the bounds between the two return edges."),
        _sig("“rotate the array by k”", "Three reversals",
             "O(1) space; normalise `k %= n` first."),
        _sig("“count neighbours”, “adjacent cells”", "A direction array + bounds check",
             "Same loop for 4- and 8-connectivity."),
        _sig("“simulate n steps”, n large", "Look for a cycle",
             "States repeat; simulating 10⁹ steps directly will not finish."),
    ],
    skeletons=[
        _sk("Neighbour scan",
            "Counting mines, flood fills, any adjacency rule.",
            """
static final int[][] DIRS = {{-1,0},{1,0},{0,-1},{0,1}};

for (int[] d : DIRS) {
    int ni = i + d[0], nj = j + d[1];
    if (ni < 0 || ni >= rows || nj < 0 || nj >= cols) continue;
    // safe to read g[ni][nj]
}
""",
            "Bounds before access, every time. This exact loop reappears in every grid BFS."),
        _sk("Simultaneous update via a copy",
            "Game of Life and every “all cells update at once” rule.",
            """
int[][] next = new int[rows][cols];
for (int i = 0; i < rows; i++)
    for (int j = 0; j < cols; j++)
        next[i][j] = rule(g, i, j);      // reads ONLY the old grid
g = next;
""",
            "Correct by construction. Optimise to in-place encoding only if asked."),
        _sk("Rotate 90° clockwise",
            "Square matrix rotation, in place.",
            """
for (int i = 0; i < n; i++)                     // transpose
    for (int j = i + 1; j < n; j++) {
        int t = a[i][j]; a[i][j] = a[j][i]; a[j][i] = t;
    }
for (int[] row : a) {                           // reverse each row
    for (int l = 0, r = n - 1; l < r; l++, r--) {
        int t = row[l]; row[l] = row[r]; row[r] = t;
    }
}
""",
            "`j = i + 1` — transposing the whole square swaps everything back."),
        _sk("Rotate an array by k",
            "Cyclic shift, O(1) space.",
            """
k %= n;
reverse(a, 0, n - 1);
reverse(a, 0, k - 1);
reverse(a, k, n - 1);
""",
            "Without `k %= n` the second reversal can run off the end."),
        _sk("Spiral boundaries",
            "Spiral order, layer-by-layer traversal.",
            """
int top = 0, bot = rows - 1, left = 0, right = cols - 1;
while (top <= bot && left <= right) {
    for (int j = left; j <= right; j++) out.add(a[top][j]);
    top++;
    for (int i = top; i <= bot; i++) out.add(a[i][right]);
    right--;
    if (top <= bot) { for (int j = right; j >= left; j--) out.add(a[bot][j]); bot--; }
    if (left <= right) { for (int i = bot; i >= top; i--) out.add(a[i][left]); left++; }
}
""",
            "The two guarded edges are where single-row and single-column matrices break."),
    ],
    costs=[
        _cost("Full grid pass", "O(rows · cols)", "O(1)", "The floor for grid problems."),
        _cost("Neighbour scan per cell", "O(rows · cols · 8)", "O(1)", "The 8 is a constant."),
        _cost("Simultaneous update with a copy", "O(rows · cols)", "O(rows · cols)", "Always correct."),
        _cost("Same, encoded in place", "O(rows · cols)", "O(1)", "Two passes, one encoding trick."),
        _cost("Array rotation by three reversals", "O(n)", "O(1)", "Versus O(n) extra with a buffer."),
    ],
    pitfalls=[
        _pit("`ArrayIndexOutOfBoundsException` at an edge cell",
             "A neighbour was read before its coordinates were bounds-checked.",
             "Check `ni`/`nj` first, then access."),
        _pit("The simulation drifts after the first step",
             "Cells were updated in place, so later cells read already-updated neighbours.",
             "Write into a copy, or encode old and new state in the same cell."),
        _pit("The rotated matrix is a mirror image",
             "The transpose loop ran over all `j` rather than `j > i`, swapping twice.",
             "Start the inner loop at `i + 1`."),
        _pit("Spiral order repeats the middle row",
             "The bottom and left edges were walked without re-checking the shrunk bounds.",
             "Guard both return edges with `if (top <= bot)` and `if (left <= right)`."),
        _pit("Rotating by k crashes or does nothing",
             "`k` was larger than `n`, or negative.",
             "`k = ((k % n) + n) % n` before the reversals."),
        _pit("Simulating a huge step count times out",
             "The process was executed literally when it is eventually periodic.",
             "Detect the repeated state and jump ahead by whole cycles."),
    ],
    lessons=["grid", "simulation"],
    checks=[
        _chk("Why can Game of Life not be updated in place naively?",
             "The rule reads a cell's neighbours; overwriting a cell makes later cells read "
             "the new value instead of the old. Every cell must see the same generation."),
        _chk("Give the two-step identity for a 90° clockwise rotation.",
             "Transpose (swap `a[i][j]` with `a[j][i]` for `j > i`), then reverse each row."),
        _chk("Why does rotating an array by k use three reversals?",
             "Reversing the whole array puts the last k elements at the front but backwards; "
             "reversing each of the two blocks restores their internal order. O(1) space."),
        _chk("What breaks in a spiral traversal of a single-row matrix?",
             "Without re-checking `top <= bot` before the bottom edge, the same row is "
             "emitted twice — once left-to-right, once right-to-left."),
    ],
    interview="""
Simulation questions look easy and eliminate people, because the grader is
exact and the specification has more cases than it first appears. The winning
approach is visible discipline: restate the rule, name the update order,
enumerate the edge cases (first row, last column, 1×n grid), *then* type. And
when asked for O(1) space, explain the encoding before writing it.
""",
    rungs=[
        _rung("Warm up", "Follow a small rule exactly.",
              ["rock-paper-scissors", "traffic-light", "robot-grid-walk"],
              {"robot-grid-walk": "The direction array, and a bounds check that has to come first."}),
        _rung("Core", "Neighbour counting on a grid.",
              ["minesweeper-counts", "color-bomb-explosion", "territory-capture"],
              {"minesweeper-counts": "Eight neighbours, bounds-checked. This loop is the ancestor of every flood fill in stage 5."}),
        _rung("Variations", "Transform the whole structure without corrupting it.",
              ["rotate-array", "rotate-array-right", "set-matrix-zeroes"],
              {"rotate-array": "Three reversals. Try the k-buffer version too and compare the space.",
               "set-matrix-zeroes": "The marking trap: record which rows and columns to clear *before* clearing any of them."}),
        _rung("Stretch", "Index arithmetic with nothing to hide behind.",
              ["rotate-matrix-90", "spiral-order", "game-of-life-step"],
              {"game-of-life-step": "Do the copy version first. The in-place encoding is the follow-up, not the entry price."}),
    ],
    next_up="""
Every technique so far has worked on data laid out in a line. The next stage
introduces structures that impose their own shape — and with it, their own
operations.
""",
)
