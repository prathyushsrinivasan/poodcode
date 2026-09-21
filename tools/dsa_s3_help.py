# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 3 (Order & Search) — the help layer.
#
# exec'd by tools/dsa_curriculum.py after dsa_s3_depth.py, in the same
# namespace. Attaches, by unit key:
#
#   quizzes     spot-the-bug / predict-the-result drills (see `_quiz`)
#   stuck       triage for the moment before any code exists (see `_stuck`)
#   edge_cases  pasteable inputs worth testing before submitting (see `_edge`)
#   walkthrough one problem solved start to finish (see `_walk`)
#
# plus the stage cheat sheet and a "say it out loud" script appended to each
# unit's interview section.
#
# When these were authored, every quiz answer was confirmed by executing a
# Python twin of its snippet, and every edge-case input was run through its
# problem's reference solution (or matched against its stored examples, for
# the older problems that have none). That was a one-off check, not a test —
# re-run it by hand when changing an answer.
# ---------------------------------------------------------------------------


# =================================================================== recursion

_H_RECURSION = dict(
    quizzes=[
        _quiz("bug",
              "`sort(a, 0, n)` never returns on any array with at least one element. Which change fixes it?",
              r"""
static void sort(int[] a, int lo, int hi) {   // sorts [lo, hi)
    if (hi - lo < 1) return;
    int mid = (lo + hi) >>> 1;
    sort(a, lo, mid);
    sort(a, mid, hi);
    merge(a, lo, mid, hi);
}
""",
              "The base case must be `hi - lo < 2`",
              ["The base case must be `hi - lo < 2`",
               "The second call must be `sort(a, mid + 1, hi)`",
               "`mid` must be `(lo + hi) / 2 + 1`",
               "`merge` must run before the two recursive calls"],
              """
With one element, `hi = lo + 1`, so `mid = lo`. The first call gets the empty range
`[lo, lo)` and returns, but the second call is `sort(a, lo, hi)` — **the same range
again**. The recursion never shrinks. A one-element range is already sorted, so it
has to be a base case: stop at `hi - lo < 2`.

`mid + 1` looks like a fix but skips element `mid` entirely in a half-open range.
"""),
        _quiz("bug",
              "`ways(9999)` is correct but never finishes. Why?",
              r"""
static long[] memo = new long[10001];
// ordered ways to write n as a sum of 4s and 6s
static long ways(int n) {
    if (n == 0) return 1;
    if (n < 0) return 0;
    if (memo[n] != 0) return memo[n];
    return memo[n] = ways(n - 4) + ways(n - 6);
}
""",
              "0 is a real answer (every odd n), so those states are never treated as cached",
              ["0 is a real answer (every odd n), so those states are never treated as cached",
               "The memo array is too small for n = 9999",
               "The base case `n < 0` should return 1",
               "`long` overflows, so the recursion loops"],
              """
4s and 6s only make even numbers, so `ways(n) = 0` for every odd n — and `0` is also
the "not computed yet" marker. Every odd state looks uncached forever, and the call
tree for an odd argument stays exponential.

Use a separate marker that cannot be an answer: fill the memo with `-1`, or keep a
`boolean[] done`.
"""),
        _quiz("predict",
              "What does `f(4071)` print?",
              r"""
static void f(int n) {
    if (n == 0) return;
    System.out.print(n % 10);
    f(n / 10);
}
""",
              "`1704`",
              ["`1704`", "`4071`", "`407`", "`0714`"],
              """
The print runs **before** the call, on the way down, so digits come out last-first:
1, 7, 0, 4. Move the print below the call and the same digits come out on the way
back up, in order — `4071`. That one line's position is the whole of
`to-base-recursive`.
"""),
        _quiz("predict",
              "How many calls does the naive `fib(5)` make in total, counting the first?",
              r"""
static long fib(int n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}
""",
              "15",
              ["15", "5", "8", "31"],
              """
Let C(n) be the number of calls: C(0) = C(1) = 1 and C(n) = 1 + C(n − 1) + C(n − 2).
So C(2) = 3, C(3) = 5, C(4) = 9, C(5) = 15. The count grows like Fibonacci itself —
about 1.6ⁿ — while only six distinct arguments ever appear. That gap is what a memo
removes.
"""),
        _quiz("bug",
              "The moves this prints are illegal — a larger disk lands on a smaller one. Which change fixes it?",
              r"""
static void hanoi(int n, char from, char to, char via) {
    if (n == 0) return;
    hanoi(n - 1, from, to, via);
    System.out.println(n + " " + from + " " + to);
    hanoi(n - 1, via, to, from);
}
""",
              "The first call must be `hanoi(n - 1, from, via, to)`",
              ["The first call must be `hanoi(n - 1, from, via, to)`",
               "The second call must be `hanoi(n - 1, via, from, to)`",
               "The base case must be `n == 1`",
               "The print must come before the first call"],
              """
State the promise: *`hanoi(k, from, to, via)` moves the top k disks from `from` to
`to`*. To move disk n, the n − 1 disks above it must first go **out of the way** —
to `via` — so the first call's target is `via`, using `to` as the spare. As written
it stacks them on `to`, exactly where disk n is about to go.
"""),
        _quiz("predict",
              "Merge sort on n = 1,000,000 elements, recursing on halves. Roughly how deep does the call stack get?",
              r"""
static void sort(int[] a, int[] buf, int lo, int hi) {
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    sort(a, buf, lo, mid);
    sort(a, buf, mid, hi);
    merge(a, buf, lo, mid, hi);
}
""",
              "About 20 frames",
              ["About 20 frames", "About 1,000 frames", "About 500,000 frames", "About 1,000,000 frames"],
              """
Each level halves the range, so the depth is ⌈log₂ 10⁶⌉ ≈ 20 — and the two calls at
a level run one *after* the other, so they never stack. Merge sort's recursion is
harmless; a recursion that shrinks by **one** per call (a list walk, Josephus) is
the kind that reaches 10⁶ frames and overflows.
"""),
    ],
    stuck=[
        _stuck("I do not know what the function should return",
               "Write its promise as one sentence: *for any input of this shape, it returns …*. "
               "If you cannot finish the sentence, the parameters are wrong — you usually need one "
               "more (an index, a bound, a partial result)."),
        _stuck("I cannot find the base case",
               "What is the smallest input whose answer is obvious — 0, empty, one element, a "
               "leaf? Then check the combine step works when the sub-answer *is* that base value."),
        _stuck("I do not see how to make the problem smaller",
               "Try the three standard cuts: remove one element (first or last), halve it, or split "
               "at every possible point. Keep whichever leaves a problem of the **same shape**."),
        _stuck("I keep tracing the calls and losing my place",
               "Stop tracing. Assume the smaller call already returns the right answer and write "
               "only what you do with it. Trace only to debug one failing input, two levels deep."),
        _stuck("It is correct but far too slow",
               "Print the arguments on entry. The same arguments twice means memoise. A depth close "
               "to n with n near 10⁵ means rewrite it as a loop."),
        _stuck("I can solve each half but not the whole (divide and conquer)",
               "List the three places the answer can be: left half, right half, straddling the "
               "middle. The straddling case is the only new code — write it on its own."),
    ],
    edge_cases=[
        _edge("fast-power", "Exponent zero", "7\n0\n",
              "A base case written as `e == 1`, or one that returns the base instead of 1."),
        _edge("fast-power", "Exponent one", "5\n1\n",
              "The odd branch — `half * half * b` with `half = power(b, 0) = 1`."),
        _edge("nth-fibonacci", "n = 0", "0\n",
              "A base case that only handles `n == 1`, recursing into negative n."),
        _edge("merge-sort-array", "A single element", "1\n42\n",
              "A base case of `hi - lo < 1`, which recurses forever on one element."),
        _edge("merge-sort-array", "Negatives and repeats", "6\n3 -1 3 -1 0 3\n",
              "A merge that forgets to copy the leftover tail of one half."),
        _edge("josephus-survivor", "A million people", "1000000 2\n",
              "The recursive recurrence — it needs 10⁶ stack frames and throws `StackOverflowError`."),
        _edge("to-base-recursive", "x = 0", "0 2\n",
              "A base case of `x == 0 → \"\"`, which prints nothing for zero."),
        _edge("closest-pair-points", "Two identical points", "3\n5 5\n5 5\n-3 7\n",
              "A strip test using `<=`, or a combine that forgets distance 0 is possible."),
    ],
    walkthrough=_walk(
        "josephus-survivor", "Last One Standing — from simulation to a one-line recurrence",
        [
            """
*n people in a circle; count k, the k-th leaves; repeat; who survives?* Constraints:
n ≤ 10⁶, k ≤ 10⁹. Output one number. The answer depends only on n and k — no array
of data at all, which is the first hint that the answer has a formula-like
structure.
""",
            """
"The answer for n in terms of the answer for n − 1" is the recursion signal. After
one removal the circle is a smaller instance of the same problem — only the
numbering has shifted. That is exactly the shape the recursion unit teaches:
*same problem, smaller input*.
""",
            """
Simulate: keep a list, remove index `(i + k − 1) % size`, repeat. Each removal from
an `ArrayList` is O(n), so the whole thing is O(n²) — 10¹² at n = 10⁶. Too slow, but
worth writing: it is the oracle you will test the fast version against.
""",
            """
Number positions from 0. The first to leave is at `(k − 1) mod n`; counting resumes
at `k mod n`. Relabel that person as 0 and you have a circle of n − 1 people whose
survivor is J(n − 1) **in the new numbering**. Shifting back adds k:

```
J(1) = 0
J(n) = (J(n − 1) + k) mod n
```

The recursion is correct and 10⁶ frames deep, which Java's stack will not hold. The
work happens after the call, so the loop that computes J(1), J(2), … in order is
the same computation, bottom-up.
""",
            """
```java
static long solve(long n, long k) {
    long pos = 0;                       // J(1) = 0
    for (long m = 2; m <= n; m++)
        pos = (pos + k) % m;            // J(m) from J(m − 1)
    return pos + 1;                     // back to 1-based
}
```
""",
            """
- `1 5` → 1 (one person). `6 2` → 5 (check against the simulation by hand).
- `5 1000000000` — k far larger than n; the `% m` handles it, and `long` keeps
  `pos + k` safe.
- `1000000 2` — the case the recursive version dies on.

**Cost:** O(n) time, O(1) space. Diff it against the simulation for every n ≤ 50 and
k ≤ 10 before trusting it.
""",
        ]),
    interview_script="""
### Say it out loud

- *"Let me state what this function returns for any input: …"* — say the promise
  before the base case.
- *"The recurrence is T(n) = …, which gives O(…)"* — price it from the code.
- *"The same arguments recur on different branches, so I'll memoise on (…)."*
- *"The depth is n, so at 10⁵ I'd convert this to a loop or an explicit stack."*
""",
)


# ===================================================================== sorting

_H_SORTING = dict(
    quizzes=[
        _quiz("bug",
              "Values range over the full `int` range. On some inputs the output is not sorted. Which change fixes it?",
              r"""
Integer[] boxed = ...;
Arrays.sort(boxed, (x, y) -> x - y);
""",
              "Compare with `Integer.compare(x, y)`",
              ["Compare with `Integer.compare(x, y)`",
               "Write `y - x` and reverse the result",
               "Chain `.thenComparing(Comparator.naturalOrder())`",
               "Nothing — subtraction is exact for `int`"],
              """
`x - y` overflows when the values are far apart: `-2_000_000_000 - 2_000_000_000`
wraps to a positive number, so a very small value compares as larger. The sort does
not crash; it silently misorders. `Integer.compare` returns only the sign.
"""),
        _quiz("bug",
              "This three-way partition sometimes leaves a large value in the middle region. Which change fixes it?",
              r"""
int lt = lo, i = lo, gt = hi;          // [lo,lt) < p, [lt,i) == p, (gt,hi] > p
while (i <= gt) {
    if      (a[i] < p) swap(a, lt++, i++);
    else if (a[i] > p) swap(a, i++, gt--);
    else               i++;
}
""",
              "The `> p` branch must not advance `i`",
              ["The `> p` branch must not advance `i`",
               "The `< p` branch must not advance `i`",
               "The loop must run while `i < gt`",
               "`lt` must start at `lo + 1`"],
              """
Swapping with `gt` brings in `a[gt]` — an element **nobody has looked at yet**.
Advancing `i` skips it, so if it was large it stays in the middle. The `< p` branch
is different: what arrives from `lt` is already known to equal `p`, so advancing is
safe there.
"""),
        _quiz("predict",
              "After this Lomuto partition of `a = [3, 8, 1, 9, 4, 6]` with `lo = 0, hi = 5`, what are `p` and the array?",
              r"""
int pivot = a[hi], p = lo;
for (int i = lo; i < hi; i++)
    if (a[i] < pivot) swap(a, i, p++);
swap(a, p, hi);
""",
              "`p = 3`, `[3, 1, 4, 6, 8, 9]`",
              ["`p = 3`, `[3, 1, 4, 6, 8, 9]`",
               "`p = 3`, `[1, 3, 4, 6, 8, 9]`",
               "`p = 2`, `[3, 1, 4, 6, 9, 8]`",
               "`p = 3`, `[3, 1, 4, 6, 9, 8]`"],
              """
The small values 3, 1, 4 are swapped to the front in the order they are met, giving
`[3, 1, 4, 9, 8, 6]` with `p = 3`; the final swap puts 6 there. Neither side is
sorted — partitioning only promises *smaller left, larger right* — which is why the
`[1, 3, 4, …]` option is wrong.
"""),
        _quiz("bug",
              "For `[2, 2, 2]` this returns 3; the correct inversion count is 0. Which change fixes it?",
              r"""
while (i < mid && j < hi) {
    if (a[i] < a[j]) buf[k++] = a[i++];
    else { count += mid - i; buf[k++] = a[j++]; }
}
""",
              "Take from the left on ties: `a[i] <= a[j]`",
              ["Take from the left on ties: `a[i] <= a[j]`",
               "Add `mid - i + 1` instead of `mid - i`",
               "Add `j - mid` instead of `mid - i`",
               "Declare `count` as `long`"],
              """
With `<`, an equal pair goes to the `else` branch and is counted as an inversion.
Equal values are not out of order, so ties must take the left element. (`long` is
also needed on large inputs, but it is not this bug — the count here is 3, not a
wrapped negative.)
"""),
        _quiz("predict",
              "What does `w` contain afterwards?",
              r"""
List<String> w = new ArrayList<>(List.of("bb", "a", "cc", "b", "aa"));
w.sort(Comparator.comparingInt(String::length));
""",
              "`[a, b, bb, cc, aa]`",
              ["`[a, b, bb, cc, aa]`", "`[a, b, aa, bb, cc]`", "`[b, a, aa, bb, cc]`",
               "It depends on the JVM"],
              """
`List.sort` is Timsort, which is **stable**: equal keys keep their input order. The
length-2 strings appear as `bb, cc, aa` in the input, so they stay that way. Sorting
alphabetically inside each length would need `.thenComparing(Comparator.naturalOrder())`.
"""),
        _quiz("predict",
              "What does this build from `{\"3\", \"30\", \"34\"}`?",
              r"""
String[] s = {"3", "30", "34"};
Arrays.sort(s, (x, y) -> (y + x).compareTo(x + y));
String result = String.join("", s);
""",
              "`34330`",
              ["`34330`", "`34303`", "`33430`", "`30334`"],
              """
The comparator puts x first when `x + y > y + x`. `"34" + "3" = "343"` beats `"334"`,
so 34 precedes 3; `"3" + "30" = "330"` beats `"303"`, so 3 precedes 30. The order is
34, 3, 30 → `34330`. No key per element could produce this — the rule needs both
items at once.
"""),
    ],
    stuck=[
        _stuck("I do not know whether to sort at all",
               "What would be true if the input were sorted — duplicates adjacent, extremes at the "
               "ends, a monotone test? If that is the whole problem, sort. If the answer needs the "
               "original positions, sort indices, or hash instead."),
        _stuck("I cannot write the comparator",
               "Take two concrete items and decide by hand which goes first. The rule you used is "
               "the comparator. If you had to look at both at once (not one number each), it is a "
               "pairwise rule like `largest-number`."),
        _stuck("I need the k-th element and sorting feels wasteful",
               "Do you need the whole order? Just the k-th → quickselect. The top k → a size-k "
               "heap. Small bounded values → counting."),
        _stuck("I have to count pairs i < j with some condition",
               "If the condition is monotone inside two sorted halves, merge sort counts the "
               "crossing pairs. If not, a Fenwick tree over compressed values."),
        _stuck("The values are small integers",
               "Is the range k about n or less? Then index an array by the value — counting "
               "sort, O(n + k), no comparisons."),
        _stuck("The statement's tie rule is confusing",
               "Write the tie rule as a second key with `thenComparing`. If the statement gives "
               "none, check the output cannot depend on it."),
    ],
    edge_cases=[
        _edge("count-inversions", "All values equal", "4\n7 7 7 7\n",
              "A merge that uses `<` and counts equal pairs as inversions."),
        _edge("count-inversions", "Strictly decreasing", "6\n6 5 4 3 2 1\n",
              "A count that misses crossing pairs — every one of the 15 pairs is an inversion."),
        _edge("largest-number", "All zeros", "3\n0 0 0\n",
              "Returning `000` instead of `0`."),
        _edge("kth-largest-element", "k = n (the minimum)", "5 1 4\n3\n",
              "Quickselect targeting index k instead of n − k."),
        _edge("kth-largest-element", "All duplicates", "3 3 3 3\n2\n",
              "A two-way partition that degrades, or a dedupe that should not happen."),
        _edge("radix-pass-by-pass", "Largest value is 0", "3\n0 0 0\n",
              "Counting digits of the maximum as 0 and printing no passes."),
        _edge("important-reverse-pairs", "The int extremes", "2\n2147483647 -2147483648\n",
              "`2 * a[j]` in `int`, which wraps."),
        _edge("rank-transform", "Negatives and ties", "5\n-3 7 -3 0 7\n",
              "Competition ranks (1 4 1 3 4) instead of dense ranks (1 3 1 2 3)."),
    ],
    walkthrough=_walk(
        "count-inversions", "Count Inversions — from all pairs to merge sort",
        [
            """
*Count pairs i < j with a[i] > a[j].* n can be large, and the count can be as big as
n(n − 1)/2 — so it needs a `long` before anything else is decided.
""",
            """
"Pairs i < j with a condition" plus "n too large for all pairs" routes to the
sorting unit's merge-counting rung. (With a *sum* condition in sorted data, it
would be two pointers instead.)
""",
            """
```java
long inv = 0;
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[i] > a[j]) inv++;
```
O(n²). Keep it: it is the oracle.
""",
            """
Every pair is inside the left half, inside the right half, or crosses the middle.
The recursive calls count the first two. For crossing pairs, both halves are
**sorted** by the time the merge runs: when `a[j]` from the right is taken while
`mid − i` left elements are still waiting, each of those is larger and earlier —
`mid − i` inversions in one addition. Each pair crosses at exactly one level, so
nothing is counted twice.
""",
            """
```java
static long sortCount(int[] a, int[] buf, int lo, int hi) {   // [lo, hi)
    if (hi - lo < 2) return 0;
    int mid = (lo + hi) >>> 1;
    long c = sortCount(a, buf, lo, mid) + sortCount(a, buf, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) {
        if (a[i] <= a[j]) buf[k++] = a[i++];        // ties are not inversions
        else { c += mid - i; buf[k++] = a[j++]; }
    }
    while (i < mid) buf[k++] = a[i++];
    while (j < hi)  buf[k++] = a[j++];
    System.arraycopy(buf, lo, a, lo, hi - lo);
    return c;
}
```
""",
            """
- `5 / 2 4 1 3 5` → 3. `4 / 7 7 7 7` → 0 (the `<=`). `6 / 6 5 4 3 2 1` → 15.
- Random arrays of length ≤ 10 against the O(n²) loop, a thousand times.

**Cost:** O(n log n) time, O(n) for the buffer. The count adds nothing asymptotically
to the sort it rides on.
""",
        ]),
    interview_script="""
### Say it out loud

- *"Do I need the whole order? If only the k-th, quickselect is O(n) average."*
- *"I'll use `Integer.compare`, not subtraction — subtraction overflows."*
- *"`Arrays.sort` on primitives isn't stable; I need stability here, so I'll sort
  objects (or pack the key and index into a long)."*
- *"Counting out-of-order pairs: merge sort, adding `mid − i` when the right side
  wins."*
""",
)


# =============================================================== binary search

_H_BINARY = dict(
    quizzes=[
        _quiz("bug",
              "This \"largest x with ok(x)\" search hangs on some inputs. Which change fixes it?",
              r"""
long lo = 0, hi = MAX;                 // ok(lo) is true
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (ok(mid)) lo = mid;
    else         hi = mid - 1;
}
return lo;
""",
              "Round the midpoint up: `lo + (hi - lo + 1) / 2`",
              ["Round the midpoint up: `lo + (hi - lo + 1) / 2`",
               "Change the loop to `while (lo <= hi)`",
               "Use `hi = mid` instead of `hi = mid - 1`",
               "Start `lo` at 1"],
              """
When `hi = lo + 1`, a rounded-down `mid` equals `lo`. If `ok(mid)` is true,
`lo = mid` changes nothing and the loop spins. Rounding up makes `mid > lo` whenever
`lo < hi`, so both branches shrink the range.
"""),
        _quiz("bug",
              "For `a = [1, 2, 3]` and `x = 10` this returns 2; the insertion point is 3. Which change fixes it?",
              r"""
int lo = 0, hi = n - 1;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < x) lo = mid + 1;
    else            hi = mid;
}
return lo;
""",
              "Start with `hi = n`, so the answer `n` is reachable",
              ["Start with `hi = n`, so the answer `n` is reachable",
               "Loop while `lo <= hi`",
               "Use `a[mid] <= x`",
               "Return `lo + 1`"],
              """
The half-open template's answer lives in `[lo, hi]`, and "everything is smaller"
means the answer is `n`. Starting at `hi = n - 1` makes `n` unreachable. `return
lo + 1` would break every other input.
"""),
        _quiz("bug",
              "Koko: piles and speeds up to 10⁹. The search sometimes returns a speed that is too slow. Which change fixes it?",
              r"""
static boolean ok(int[] piles, int k, long h) {
    long hours = 0;
    for (int p : piles) hours += (p + k - 1) / k;    // ceil(p / k)
    return hours <= h;
}
""",
              "`p + k - 1` overflows `int`; use `(p - 1) / k + 1` or compute in `long`",
              ["`p + k - 1` overflows `int`; use `(p - 1) / k + 1` or compute in `long`",
               "Use `Math.ceil(p / k)`",
               "`hours` must be an `int`",
               "The comparison must be `hours < h`"],
              """
With p and k near 10⁹, `p + k - 1` is about 2·10⁹ — past `Integer.MAX_VALUE` — and
wraps negative, so a pile seems to take negative hours and a slow speed looks
feasible. `Math.ceil(p / k)` is its own classic bug: `p / k` is integer division, so
it is already rounded down before `ceil` sees it.
"""),
        _quiz("predict",
              "For `a = [1, 3, 5, 5, 5, 8]`, what do `lowerBound(5)` and `upperBound(5)` return?",
              r"""
// lowerBound: first index with a[i] >= x
// upperBound: first index with a[i] >  x
""",
              "2 and 5",
              ["2 and 5", "2 and 4", "3 and 5", "4 and 5"],
              """
The first 5 is at index 2; the first value greater than 5 is 8, at index 5. The
count of 5s is `5 − 2 = 3`, and the last 5 is at `upperBound − 1 = 4` — which is why
"2 and 4" is the tempting wrong answer.
"""),
        _quiz("bug",
              "For the unrotated `[1, 2, 3, 4, 5]` this returns 4. Which change fixes it?",
              r"""
int lo = 0, hi = n - 1;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] > a[lo]) lo = mid + 1;
    else                hi = mid;
}
return a[lo];                          // the minimum
""",
              "Compare with the right end: `a[mid] > a[hi]`",
              ["Compare with the right end: `a[mid] > a[hi]`",
               "Use `a[mid] >= a[lo]`",
               "Start with `hi = n`",
               "Return `a[hi]`"],
              """
`a[mid] > a[lo]` says the left part is sorted — but not whether the drop is to the
right. On an unrotated array there is no drop at all, and the loop walks away from
the minimum. `a[mid] > a[hi]` is informative in every case: true means the drop is
right of `mid`, false means `mid..hi` is sorted and the minimum is at or before `mid`.
"""),
        _quiz("predict",
              "In the k-th smallest search over a 3 × 4 multiplication table, what does `count(6)` return?",
              r"""
long count(long x) {                 // n = 3 rows, m = 4 columns
    long c = 0;
    for (int i = 1; i <= 3; i++) c += Math.min(4, x / i);
    return c;
}
""",
              "9",
              ["9", "8", "7", "12"],
              """
Row 1 holds 1, 2, 3, 4 (4 values ≤ 6), row 2 holds 2, 4, 6, 8 (3), row 3 holds 3, 6,
9, 12 (2): 4 + 3 + 2 = 9. The cap `min(m, …)` matters on row 1, where `6 / 1 = 6`
would otherwise count columns that do not exist.
"""),
    ],
    stuck=[
        _stuck("There is no sorted array anywhere in the problem",
               "Is there a yes/no question about a number x — capacity, speed, day, distance — "
               "whose answer flips once as x grows? Then binary-search x."),
        _stuck("I cannot tell whether the predicate is monotone",
               "Assume x works. Does x + 1 obviously work too — more capacity, more time, more "
               "room? If you can say why in one sentence, it is monotone."),
        _stuck("I do not know the bounds",
               "`lo` = the smallest value that could be the answer. `hi` = one you can *prove* "
               "works (the sum, the max, max · k). Write both down before the loop."),
        _stuck("Minimise or maximise — which template?",
               "Draw the predicate as `F F F T T T` or `T T T F F F`. You want the first T "
               "(minimise) or the last T (maximise — round the midpoint up)."),
        _stuck("I need the k-th of something far too big to list",
               "Can you count how many candidates are ≤ x without listing them? Then search x "
               "for the first count ≥ k."),
        _stuck("It is off by one somewhere",
               "Run arrays of length 0, 1 and 2, with the target absent, first and last. Those "
               "six runs catch almost every boundary bug."),
    ],
    edge_cases=[
        _edge("lower-bound-index", "x larger than everything", "3\n1 2 3\n10\n",
              "`hi = n - 1`, which cannot return the insertion point n."),
        _edge("lower-bound-index", "x smaller than everything", "3\n5 6 7\n-4\n",
              "A search that assumes some element is < x."),
        _edge("lower-bound-index", "Every element equal to x", "4\n2 2 2 2\n2\n",
              "Returning *a* match instead of the first one."),
        _edge("koko-eating-bananas", "Hours equal to piles", "3 3\n30 11 23\n",
              "An upper bound below the largest pile."),
        _edge("koko-eating-bananas", "Huge piles", "2 2\n1000000000 1000000000\n",
              "`(p + k - 1) / k` overflowing `int`."),
        _edge("search-rotated-array", "Not rotated at all", "5 5\n1 2 3 4 5\n",
              "Logic that assumes a drop exists somewhere."),
        _edge("min-time-for-trips", "One slow van, many deliveries", "1 10000000\n10000000\n",
              "An `int` answer — it is 10¹⁴."),
        _edge("max-equal-portions", "Impossible even at length 1", "2 10\n4 5\n",
              "Returning 1 instead of 0 when the total is below k."),
    ],
    walkthrough=_walk(
        "min-ship-capacity", "Minimum Ship Capacity — searching the answer",
        [
            """
*Packages in fixed order, loaded day by day onto a ship of capacity C; find the
smallest C that ships everything within D days.* No sorted array, no target value —
and the answer is a single number between two obvious extremes.
""",
            """
"**Minimum** capacity **such that** it is possible" is the stage router's
search-on-the-answer row. Check the precondition before anything else: if C works,
does C + 1? Yes — a bigger ship never needs *more* days. Monotone, so binary search
applies.
""",
            """
Try every capacity from `max(w)` upward and return the first that fits in D days.
Each check is one greedy pass, O(n), but the range can be 10⁹ wide: O(n · range).
""",
            """
The feasible capacities form a **suffix** of the range: `F F F … T T T`. The first
T is a lower bound over capacities. Bounds: `lo = max(w)` (the heaviest package
must fit), `hi = sum(w)` (everything in one day always works). The whole difficulty
is the monotonicity sentence; the loop is the template.
""",
            """
```java
static int days(int[] w, long cap) {
    int d = 1; long load = 0;
    for (int x : w) {
        if (load + x > cap) { d++; load = 0; }
        load += x;
    }
    return d;
}

long lo = max, hi = sum;                    // lo may be the answer; hi certainly works
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (days(w, mid) <= D) hi = mid;        // feasible: look lower
    else                   lo = mid + 1;
}
return lo;
```
""",
            """
- `10 5 / 1 … 10` → 15. D = 1 → the sum. D = n → the max.
- One package: the answer is its weight.
- Test `days()` alone first — nearly every bug here is in the predicate, not the loop.

**Cost:** O(n · log(sum)) — about 30 greedy passes. `load` and the bounds are `long`.
""",
        ]),
    interview_script="""
### Say it out loud

- *"If capacity C works, C + 1 works too — so feasibility is monotone and I can
  binary-search C."*
- *"Bounds: at least the max (it must fit), at most the sum (one day)."*
- *"Half-open `[lo, hi)`, no equality branch: the loop returns the first position
  where the test turns true."*
- *"`lo + (hi − lo) / 2`, so the midpoint can't overflow."*
""",
)


# ====================================================================== greedy

_H_GREEDY = dict(
    quizzes=[
        _quiz("bug",
              "For `[2, 3, 1, 1, 4]` this returns 3; the fewest jumps is 2. Which change fixes it?",
              r"""
int jumps = 0, curEnd = 0, far = 0;
for (int i = 0; i < n; i++) {
    far = Math.max(far, i + a[i]);
    if (i == curEnd) { jumps++; curEnd = far; }
}
return jumps;
""",
              "Loop to `n - 1`: standing on the last index needs no jump",
              ["Loop to `n - 1`: standing on the last index needs no jump",
               "Update `far` after the `if`",
               "Start `curEnd` at -1",
               "Count a jump whenever `far` grows"],
              """
The window after two jumps ends at index 4 — the last index. When the loop reaches
`i = 4 = curEnd` it counts a third jump to go beyond it. Stopping at `n − 2` means
arriving at the end is never mistaken for needing to leave it.
"""),
        _quiz("bug",
              "This keeps too few meetings on some inputs. Which change fixes it?",
              r"""
Arrays.sort(iv, (x, y) -> Integer.compare(x[0], y[0]));   // by start
int end = Integer.MIN_VALUE, kept = 0;
for (int[] v : iv)
    if (v[0] >= end) { kept++; end = v[1]; }
""",
              "Sort by end time instead of start time",
              ["Sort by end time instead of start time",
               "Use `v[0] > end`",
               "Sort by length",
               "Start `end` at 0"],
              """
`[0, 100]` starts first, so it is kept — and blocks `[1, 2]`, `[3, 4]`, … Sorting by
**end** takes the meeting that frees the room soonest, which the exchange argument
shows is never worse. Sorting by length also fails: `[4, 7]` can be short and still
block `[1, 5]` and `[6, 10]`.
"""),
        _quiz("bug",
              "With total gas below total cost, this still returns a start index. Which change fixes it?",
              r"""
int tank = 0, start = 0;
for (int i = 0; i < n; i++) {
    tank += gas[i] - cost[i];
    if (tank < 0) { start = i + 1; tank = 0; }
}
return start;
""",
              "Also sum `gas − cost` over the whole lap and return -1 if it is negative",
              ["Also sum `gas − cost` over the whole lap and return -1 if it is negative",
               "Reset `tank` to `gas[i]` instead of 0",
               "Loop twice around the circle",
               "Return `start % n`"],
              """
The reset argument proves that *if* a valid start exists, it is the last surviving
candidate. Whether one exists is a separate global fact: total gas ≥ total cost.
Without that check the loop happily returns an index from which the lap fails.
"""),
        _quiz("bug",
              "Candy: for ratings `[1, 3, 4, 5, 2]` this gives 9 candies; the correct total is 11. Which change fixes it?",
              r"""
Arrays.fill(c, 1);
for (int i = 1; i < n; i++)      if (r[i] > r[i - 1]) c[i] = c[i - 1] + 1;
for (int i = n - 2; i >= 0; i--) if (r[i] > r[i + 1]) c[i] = c[i + 1] + 1;
""",
              "Take the maximum in the second pass: `c[i] = Math.max(c[i], c[i + 1] + 1)`",
              ["Take the maximum in the second pass: `c[i] = Math.max(c[i], c[i + 1] + 1)`",
               "Run the right-to-left pass first",
               "Start every child at 0",
               "Use `>=` in both comparisons"],
              """
After the first pass, `c = [1, 2, 3, 4, 1]`. The second pass sees 5 > 2 and writes
`c[3] = 2`, destroying the 4 that the left neighbour required. Taking the max keeps
both constraints: `[1, 2, 3, 4, 1]` → total 11.
"""),
        _quiz("predict",
              "Coins `{4, 3, 1}` and amount 6. What does this return, and what is the true minimum?",
              r"""
int count = 0;
for (int c : new int[]{4, 3, 1}) {    // largest first
    count += amount / c;
    amount %= c;
}
""",
              "It returns 3; the minimum is 2",
              ["It returns 3; the minimum is 2", "It returns 2; the minimum is 2",
               "It returns 3; the minimum is 3", "It returns 6; the minimum is 2"],
              """
Greedy takes 4, then 1 + 1: three coins. Two 3s make 6 with two. Nothing is buggy —
the rule is false for this coin system, which is why coin change is DP. The
counterexample names the missing state: *how much is left* matters.
"""),
        _quiz("predict",
              "Jobs as (time, weight): A = (3, 1), B = (1, 1), C = (2, 4). In what order does this comparator run them?",
              r"""
Arrays.sort(jobs, (x, y) -> Long.compare((long) x.t * y.w, (long) y.t * x.w));
""",
              "C, B, A",
              ["C, B, A", "B, C, A", "A, B, C", "C, A, B"],
              """
The comparator orders by t/w: A = 3, B = 1, C = 0.5. So C (short and heavy) first,
then B, then A. Shortest-first would put B before C and cost more: B, C costs
1·1 + 4·3 = 13 for that pair, while C, B costs 4·2 + 1·3 = 11.
"""),
    ],
    stuck=[
        _stuck("I do not know whether greedy is even right here",
               "Spend two minutes trying to break your rule on inputs of size 3 or 4. If a "
               "worse-looking move now can enable a better one later, it is DP."),
        _stuck("I do not know which key to sort by",
               "Try each candidate — start, end, length, value, ratio — on a two-item example "
               "where they disagree. Keep the one you can defend with a swap."),
        _stuck("“In what order should the jobs run?”",
               "Take two adjacent jobs and write the cost of both orders. The difference between "
               "the two costs *is* your comparator."),
        _stuck("“Fewest jumps / taps / refuels to cover everything”",
               "Think in levels: from everything reachable in k steps, how far can step k + 1 "
               "reach? Count a step only when the current level runs out."),
        _stuck("Each element has constraints on both neighbours",
               "Satisfy the left constraint in one pass, the right in a reverse pass, and "
               "combine the two with `max`."),
        _stuck("It passes the examples but fails hidden tests",
               "Write a brute force over all orders or subsets for n ≤ 8 and a random stress "
               "loop. It finds the counterexample in seconds."),
    ],
    edge_cases=[
        _edge("jump-game", "A single element that is 0", "0\n",
              "Returning false because you cannot move — you are already at the end."),
        _edge("jump-game", "A zero you cannot jump over", "3 2 1 0 4\n",
              "Updating `reach` from an index that was never reachable."),
        _edge("jump-game-ii", "Already at the end", "0\n",
              "Counting a jump when `n = 1`."),
        _edge("gas-station-start", "Not enough gas overall", "3\n2 3 4\n3 4 3\n",
              "Returning the last candidate without checking total gas ≥ total cost."),
        _edge("best-time-buy-sell", "Prices only fall", "5 4 3 2 1\n",
              "Returning a negative profit instead of 0."),
        _edge("cheapest-first-budget", "Budget exactly used up", "3 6\n1 2 3\n",
              "A `>=` where `>` belongs, stopping one item early."),
        _edge("job-deadlines-profit", "Earliest free slot is wrong", "2\n2 10\n1 9\n",
              "Placing the 10-profit job in slot 1 and losing the 9."),
        _edge("min-max-lateness", "Everything is due at time 0", "3\n2 0\n3 0\n1 0\n",
              "A lateness that is not clamped at 0, or a wrong order among equal deadlines."),
    ],
    walkthrough=_walk(
        "weighted-completion-order", "Order the Repairs — an exchange argument becomes a comparator",
        [
            """
*One technician, n repairs; repair i takes t_i hours and costs w_i per hour its
customer waits. Minimise Σ w_i · C_i.* n up to 10⁵, so n! orders is out of the
question — the answer is an **order**.
""",
            """
"In what order should the jobs run to minimise a total?" is the greedy router's
exchange-argument row. The sort key is not given; it has to be derived.
""",
            """
Try all permutations: O(n! · n). Write it for n ≤ 7 — it is the oracle, and running
it on a few examples is how you *discover* the rule rather than guess it.
""",
            """
Compare two **adjacent** jobs x then y. Everyone before them is unaffected, and so
is everyone after (the pair takes t_x + t_y either way). Only their own two costs
change:

- x first: y waits an extra t_x → extra cost w_y · t_x
- y first: x waits an extra t_y → extra cost w_x · t_y

So x goes first iff **t_x · w_y < t_y · w_x** — equivalently t_x / w_x < t_y / w_y.
Any order violating it has an adjacent pair whose swap strictly helps, so the
optimum is sorted by this rule.
""",
            """
```java
Integer[] idx = new Integer[n];
for (int i = 0; i < n; i++) idx[i] = i;
Arrays.sort(idx, (x, y) -> Long.compare((long) t[x] * w[y], (long) t[y] * w[x]));
long time = 0, cost = 0;
for (int j : idx) { time += t[j]; cost += (long) w[j] * time; }
return cost;
```
Cross-multiplied, not divided: exact, and no `double` can make the comparator
inconsistent.
""",
            """
- `3 / 3 1 / 1 2 / 2 2` → 14. Equal weights → shortest first. Equal times →
  heaviest first.
- Stress-test against the permutation brute force for n ≤ 7.

**Cost:** O(n log n). The total reaches 10¹⁶, so `long` for `time` and `cost`.
""",
        ]),
    interview_script="""
### Say it out loud

- *"Let me check whether greedy is safe: I'll try to build a case where the local
  choice loses."*
- *"Exchange argument: swapping two adjacent jobs changes only their costs, and
  x-first wins when t_x · w_y < t_y · w_x."*
- *"Stays ahead: after each index my reach is at least any strategy's."*
- *"If I find a counterexample, I'll switch to DP — the counterexample tells me the
  state."*
""",
)


# =================================================================== intervals

_H_INTERVALS = dict(
    quizzes=[
        _quiz("bug",
              "For `[1, 10], [2, 3]` this outputs `[1, 3]`. Which change fixes it?",
              r"""
for (int[] cur : iv) {                       // sorted by start
    int[] last = out.isEmpty() ? null : out.get(out.size() - 1);
    if (last != null && cur[0] <= last[1]) last[1] = cur[1];
    else out.add(cur.clone());
}
""",
              "Extend with `last[1] = Math.max(last[1], cur[1])`",
              ["Extend with `last[1] = Math.max(last[1], cur[1])`",
               "Sort by end instead of start",
               "Use `cur[0] < last[1]`",
               "Add `cur` instead of a clone"],
              """
`[2, 3]` is **nested** inside `[1, 10]`. Overwriting the end shrinks the merged block
to `[1, 3]` and loses 3–10. The end of a merged block is the largest end seen, not
the latest.
"""),
        _quiz("bug",
              "Back-to-back meetings `[0, 5)` and `[5, 10)` report 2 rooms. Which change fixes it?",
              r"""
// ev = {time, delta}: +1 at a start, -1 at an end
Arrays.sort(ev, (x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0])
                                        : Integer.compare(y[1], x[1]));
int cur = 0, peak = 0;
for (int[] e : ev) peak = Math.max(peak, cur += e[1]);
""",
              "At equal times sort `-1` first: `Integer.compare(x[1], y[1])`",
              ["At equal times sort `-1` first: `Integer.compare(x[1], y[1])`",
               "Take the peak before adding the delta",
               "Put the end event at `end + 1`",
               "Sort by delta only"],
              """
The tie-break puts `+1` before `-1`, so at time 5 the new meeting is counted before
the old one releases its room: the count briefly reads 2. Ascending delta processes
ends first. (Moving ends to `end + 1` would make touching meetings overlap on
purpose — the opposite of what half-open intervals mean.)
"""),
        _quiz("bug",
              "Intersecting two sorted interval lists, this misses some intersections. Which change fixes it?",
              r"""
while (i < a.length && j < b.length) {
    int lo = Math.max(a[i][0], b[j][0]), hi = Math.min(a[i][1], b[j][1]);
    if (lo <= hi) out.add(new int[]{ lo, hi });
    if (a[i][0] < b[j][0]) i++; else j++;
}
""",
              "Advance whichever interval ends first: `if (a[i][1] < b[j][1]) i++`",
              ["Advance whichever interval ends first: `if (a[i][1] < b[j][1]) i++`",
               "Advance both pointers every time",
               "Use `lo < hi`",
               "Sort both lists by end first"],
              """
The interval that ends first can meet nothing further in the other list; the one
that ends later might. Advancing by *start* can discard the long interval while it
still has intersections ahead — `a = [0, 10]`, `b = [1, 2], [5, 6]` loses `[5, 6]`.
"""),
        _quiz("predict",
              "Closed intervals, touching ones merged. What does merging `[1, 4], [6, 8], [2, 3], [8, 9]` give?",
              r"""
Arrays.sort(iv, (x, y) -> Integer.compare(x[0], y[0]));
// extend the last block while cur[0] <= last[1], with max on the end
""",
              "`[1, 4], [6, 9]`",
              ["`[1, 4], [6, 9]`", "`[1, 3], [6, 9]`", "`[1, 4], [6, 8], [8, 9]`", "`[1, 9]`"],
              """
Sorted: `[1, 4], [2, 3], [6, 8], [8, 9]`. `[2, 3]` is nested (the max keeps 4),
`[6, 8]` starts a new block because 6 > 4, and `[8, 9]` touches it — `8 <= 8` — so
the block becomes `[6, 9]`.
"""),
        _quiz("predict",
              "Balloons `[1, 6], [2, 8], [7, 12], [10, 16]`: sort by end and shoot at each unburst balloon's end. How many arrows?",
              r"""
Arrays.sort(b, (x, y) -> Integer.compare(x[1], y[1]));
long arrow = Long.MIN_VALUE; int arrows = 0;
for (int[] x : b)
    if (x[0] > arrow) { arrows++; arrow = x[1]; }
""",
              "2",
              ["2", "1", "3", "4"],
              """
The arrow at 6 bursts `[1, 6]` and `[2, 8]` (2 ≤ 6). `[7, 12]` starts after 6, so a
second arrow goes at 12 — bursting `[10, 16]` too. Two arrows.
"""),
        _quiz("bug",
              "Weighted bookings: `[0, 5) w=1` and `[5, 10) w=1` should give 2, but this gives 1. Which change fixes it?",
              r"""
// b sorted by end; ends[i] = b[i].end
for (int i = 1; i <= n; i++) {
    int j = lowerBound(ends, b[i - 1].start);   // # ends < start
    best[i] = Math.max(best[i - 1], b[i - 1].w + best[j]);
}
""",
              "Use `upperBound` — bookings ending exactly at `start` are compatible",
              ["Use `upperBound` — bookings ending exactly at `start` are compatible",
               "Sort by start instead of end",
               "Use `best[j - 1]`",
               "Take `best[i] = best[i - 1] + w` when they do not overlap"],
              """
`lowerBound(ends, 5)` counts ends **< 5**, excluding `[0, 5)`, whose end is exactly
5 — yet a booking ending at 5 and one starting at 5 do not overlap. The compatible
prefix is the ends **≤ start**, which is the upper bound.
"""),
    ],
    stuck=[
        _stuck("Sort by start, or by end?",
               "Building a union, merging, inserting: **start**. Keeping as many as possible, "
               "fewest removals, fewest arrows: **end**. How many at one moment: neither — events."),
        _stuck("Do touching intervals overlap?",
               "Find the sentence in the statement; if it is silent, read the examples. Encode "
               "the answer in one comparison (`<` or `<=`) and use it everywhere."),
        _stuck("There are too many pairs to compare",
               "After sorting by start, can an interval overlap anything except the block just "
               "before it? That is why one linear pass suffices."),
        _stuck("I need “how many at the same time”",
               "Turn each interval into +1 at its start and −1 at its end. Sort the events "
               "(ends first on ties) and sweep a counter."),
        _stuck("The intervals carry values or weights",
               "Greedy by end fails. Sort by end, DP over prefixes, and binary-search the last "
               "compatible interval."),
        _stuck("Bookings arrive one at a time",
               "Keep a `TreeMap` by start. A new booking can only clash with its floor and "
               "ceiling neighbours — check those two."),
    ],
    edge_cases=[
        _edge("covered-length-union", "Nested inside another", "3\n0 10\n2 3\n4 5\n",
              "Overwriting the end instead of taking the max."),
        _edge("covered-length-union", "Touching end to start", "2\n1 3\n3 5\n",
              "Double-counting or dropping the shared point."),
        _edge("busiest-moment", "Back to back, never overlapping", "3\n0 5\n5 10\n10 15\n",
              "Processing starts before ends at equal times — it reports 2."),
        _edge("subtract-interval", "Cut inside a single block", "1 3 6\n0 10\n",
              "Keeping only one side of a block that should split in two."),
        _edge("subtract-interval", "Cut removes everything", "2 0 100\n10 20\n30 40\n",
              "Printing an empty line instead of `empty`."),
        _edge("weighted-job-scheduling", "Back-to-back bookings", "3\n0 5 1\n5 10 1\n10 15 1\n",
              "A predecessor search that excludes an end equal to the start."),
        _edge("weighted-job-scheduling", "One heavy booking beats three light ones",
              "4\n0 10 100\n0 2 30\n2 5 30\n5 10 30\n",
              "Greedy by end time — it picks the three light ones."),
        _edge("merge-intervals", "A single interval", "5\n7\n",
              "A merge loop that only emits a block when the *next* interval starts."),
    ],
    walkthrough=_walk(
        "weighted-job-scheduling", "Most Valuable Bookings — where greedy stops",
        [
            """
*Requests `[s, e)` with payments w; accept non-overlapping ones to maximise the
total.* Touching is allowed. n up to 10⁵, so no subset enumeration.
""",
            """
It looks like the intervals router's "maximum non-overlapping" row — sort by end,
keep greedily. But that row's near miss is exactly this: **weights**. Maximising
the *count* and maximising the *weight* are different problems.
""",
            """
Try every subset and keep the best compatible one: O(2ⁿ · n). Then try the greedy
by end and find the counterexample: `[0, 10) w=100` against `[0, 2)`, `[2, 5)`,
`[5, 10)` at 30 each. Greedy keeps the three short ones (90); the answer is 100.
""",
            """
Keep the sort by end — it still makes every compatible set a **prefix**. Let
`best[i]` be the best total using only the first i bookings. Booking i is either
skipped (`best[i − 1]`) or taken together with the best of the bookings that end at
or before its start. Those are a prefix of length p(i), found by binary search:

```
best[i] = max(best[i − 1], w_i + best[p(i)])
```
""",
            """
```java
Arrays.sort(b, (x, y) -> Integer.compare(x[1], y[1]));        // by end
int[] ends = new int[n];
for (int i = 0; i < n; i++) ends[i] = b[i][1];
long[] best = new long[n + 1];
for (int i = 1; i <= n; i++) {
    int s = b[i - 1][0], lo = 0, hi = n;                       // # ends <= s
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (ends[mid] <= s) lo = mid + 1; else hi = mid;
    }
    best[i] = Math.max(best[i - 1], b[i - 1][2] + best[lo]);
}
return best[n];
```
""",
            """
- Back to back (`0 5 1 / 5 10 1 / 10 15 1`) → 3: checks the `<=` in the search.
- The heavy-versus-light case → 100: checks you did not fall back to greedy.
- Identical intervals → the heaviest one.

**Cost:** O(n log n) — the sort, plus one binary search per booking. Totals reach
10¹⁴: `long`.
""",
        ]),
    interview_script="""
### Say it out loud

- *"Merging, so I sort by start; the end of a merged block is a max, because
  intervals nest."*
- *"Maximum non-overlapping, so I sort by end — the earliest finish leaves the most
  room."*
- *"Does a meeting ending at 2 clash with one starting at 2? I'll assume not
  unless you say otherwise."*
- *"With weights, greedy fails; sort by end, binary-search the predecessor, and
  DP."*
""",
)


_S3_CHEATSHEET = r"""
### Which unit?

| The prompt says… | Unit | Template |
| --- | --- | --- |
| same problem on a smaller input, a tree, “split and combine” | Recursion | promise → base → trust the call → combine |
| k-th element, custom order, count out-of-order pairs | Sorting | comparator · quickselect · merge-count |
| sorted + find/insert/count, or “minimum X such that” | Binary search | half-open lower bound · search the answer |
| best local move, one pass, “in what order” | Greedy | running extreme · reach · exchange comparator |
| overlapping ranges, rooms, schedules | Intervals | sort by start (merge) or end (keep) · ±1 sweep |

### The templates

```java
// Recursion — divide and conquer
static long solve(int lo, int hi) {                 // [lo, hi)
    if (hi - lo < 2) return base(lo, hi);
    int mid = (lo + hi) >>> 1;
    return combine(solve(lo, mid), solve(mid, hi), crossing(lo, mid, hi));
}

// Sorting — safe comparator, and quickselect's loop
list.sort(Comparator.comparingInt((int[] x) -> x[1]).thenComparingInt(x -> x[0]));
while (true) { int p = partition(a, lo, hi); if (p == k) return a[p]; if (p < k) lo = p + 1; else hi = p - 1; }

// Binary search — first true (minimise)            // last true: mid rounds UP, ok → lo = mid
long lo = LO, hi = HI;
while (lo < hi) { long mid = lo + (hi - lo) / 2; if (ok(mid)) hi = mid; else lo = mid + 1; }

// Greedy — furthest reach, and an exchange comparator
for (int i = 0; i < n; i++) { if (i > reach) return false; reach = Math.max(reach, i + a[i]); }
Arrays.sort(idx, (x, y) -> Long.compare((long) t[x] * w[y], (long) t[y] * w[x]));

// Intervals — merge (by start) and keep-most (by end)
if (!out.isEmpty() && cur[0] <= last[1]) last[1] = Math.max(last[1], cur[1]); else out.add(cur);
if (v[0] >= end) { kept++; end = v[1]; }
```

### The six bugs that fail hidden tests

1. `(a, b) -> a - b` — overflows; use `Integer.compare`.
2. `hi = n - 1` in a half-open search — the insertion point `n` becomes unreachable.
3. Last-true search with a rounded-down `mid` — infinite loop.
4. Sum of `T / t[i]` or `(p + k − 1) / k` in `int` — overflow makes an infeasible
   answer look feasible.
5. Merge with `last[1] = cur[1]` — nested intervals shrink the block.
6. Starts before ends at equal times in a sweep — one room too many.

### Costs to quote

| | Time | Space |
| --- | --- | --- |
| Sort | O(n log n) | O(log n) primitives, O(n) objects |
| Quickselect | O(n) average | O(1) |
| Merge-count pairs | O(n log n) | O(n) |
| Binary search / on the answer | O(log n) / O(log range · check) | O(1) |
| Sort-then-greedy, merge, sweep | O(n log n) | O(n) |
| Weighted intervals | O(n log n) | O(n) |
"""


def _attach_s3_help():
    by_key = {u["key"]: u for u in _UNITS}
    for key, h in {
        "recursion": _H_RECURSION,
        "sorting": _H_SORTING,
        "binary-search": _H_BINARY,
        "greedy": _H_GREEDY,
        "intervals": _H_INTERVALS,
    }.items():
        u = by_key[key]
        u["quizzes"].extend(h["quizzes"])
        u["stuck"].extend(h["stuck"])
        u["edge_cases"].extend(h["edge_cases"])
        u["walkthrough"] = h["walkthrough"]
        u["interview"] = u["interview"].rstrip() + "\n\n" + _md(h["interview_script"])
    for st in _STAGES:
        if st["key"] == "order-and-search":
            st["cheatsheet"] = _md(_S3_CHEATSHEET)


_attach_s3_help()
