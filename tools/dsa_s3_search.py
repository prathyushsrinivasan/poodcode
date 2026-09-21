# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 3 — Order, and what it buys.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# Stage 2 removed nested loops by reusing work. This stage removes them by
# imposing ORDER — and it opens with recursion, because the two sorts whose
# ideas outlive the library call (merge sort and quickselect) are divide and
# conquer, and the sorting unit cannot teach them to someone who does not yet
# trust a recursive call.
#
# ORDERING: recursion → sorting → binary search → greedy → intervals.
#
# Greedy and intervals used to close the curriculum, after every graph unit,
# although neither needs anything past sorting. That placed "merge intervals"
# — one of the commonest Medium questions there is — behind Dijkstra. They now
# sit where their only prerequisite is: directly after the sort that makes
# their greedy rules provable.
# ---------------------------------------------------------------------------

_S3 = _stage(
    "order-and-search", "Order & Search", "🔢",
    "Impose order, then exploit it.",
    """
Sorting costs O(n log n) and buys you an enormous amount: binary search, two
pointers, greedy sweeps, duplicate detection and interval merging all become
available the moment the data is in order. This stage is about knowing what
that purchase is worth and when to make it.

| Unit | What order buys it |
| --- | --- |
| **Recursion** | Nothing yet — it is the notation merge sort and quickselect are written in |
| **Sorting** | Equal things adjacent, extremes at the ends, and pairs that can be *counted* while merging |
| **Binary search** | One comparison discards half — over an array, or over the answer itself |
| **Greedy** | A processing order in which the best local move is provably safe |
| **Intervals** | Overlaps that can only happen between neighbours |

It opens with **recursion**, because the sorts worth understanding are
recursive: merge sort splits and merges, quickselect partitions and recurses
into one side. It closes with **greedy** and **intervals** — the families where
"sort, then take the best local move" is provably right, and where you learn
to check that it is.

**The hard part is the near misses.** *k-th largest* is a sort, a heap or a
quickselect depending on k and on whether you need the rest of the order.
*Minimum X such that it works* is binary search on the answer — unless
"works" is not monotone. *Maximum non-overlapping* is greedy by end time — until
each interval carries a **weight**, and then it is dynamic programming. The
routing table below is those boundaries, written down.
""",
    router=[
        _route("“sort by …”, “order by frequency / a second key / a custom rule”",
               "sorting",
               "A comparator, built from `comparingInt` and `thenComparing`. The rule is "
               "the whole problem.",
               "If the rule compares *pairs* (“which of these two goes first?”) and has "
               "no key, the ordering itself needs an exchange argument — that is greedy."),
        _route("“k-th largest / smallest”, one value",
               "sorting",
               "Quickselect: O(n) average, recurses into one side of a partition.",
               "The **top k** as a set, or k-th in a *stream*, is a size-k heap (heaps "
               "unit). k-th in a sorted *matrix* or a multiplication table is binary "
               "search over values."),
        _route("“how many pairs i < j with a[i] > a[j]” (or `> 2·a[j]`, …)",
               "sorting",
               "Merge sort counts every cross-midpoint pair at the merge, in O(n log n) total.",
               "Pairs with a *sum* condition in sorted data are two pointers (stage 2)."),
        _route("Values are small integers, or fixed-width keys",
               "sorting",
               "Counting or radix sort: O(n + k) or O(d·n), with no comparisons at all.",
               "Arbitrary 64-bit values with no bound — the comparison sort is simpler "
               "and just as fast in practice."),
        _route("“sorted array” + find / insert position / count / first ≥ x",
               "binary-search",
               "Lower bound. One half-open template answers all four questions.",
               "Unsorted data queried once — a linear scan is O(n) and sorting first "
               "is O(n log n)."),
        _route("“minimum capacity / speed / days / time such that it is possible”",
               "binary-search",
               "Binary search on the answer: `feasible(x)` is easy to check and monotone in x.",
               "If feasibility is **not** monotone (possible at 5, impossible at 6), the "
               "search is invalid — usually that is DP."),
        _route("“maximise the minimum distance / gap / share”",
               "binary-search",
               "The mirror image: the *largest* x that is still feasible. Same loop, "
               "the other branch keeps `mid`.",
               ""),
        _route("“k-th smallest” over a space too big to list (pair distances, a table)",
               "binary-search",
               "Search the *value*: count how many are ≤ x, and find the first x whose "
               "count reaches k.",
               "If the space is small enough to generate, a heap or quickselect is simpler."),
        _route("A rotated sorted array, a peak, a bitonic sequence",
               "binary-search",
               "No global order, but one comparison still tells you which half to keep.",
               "With **duplicates**, that comparison can be inconclusive and the worst "
               "case degrades to O(n)."),
        _route("“recursion”, “in terms of a smaller input”, a tree or nested structure",
               "recursion",
               "Write the one-sentence promise, the base case, and the combine.",
               "If the same arguments recur on different branches, it is DP — memoise."),
        _route("“split, solve both halves, combine” — a crossing term",
               "recursion",
               "Divide and conquer. The work is the combine step across the midpoint.",
               ""),
        _route("“maximum profit / furthest reach / fewest jumps”, one pass",
               "greedy",
               "A running extreme or a furthest reach — the stays-ahead argument.",
               "When a worse move now can pay off later (coins {1, 3, 4}), greedy is "
               "wrong. Find the counterexample, then write the DP."),
        _route("“in what order should the jobs run” to minimise a total or a lateness",
               "greedy",
               "Exchange argument: compare two adjacent jobs, and sort by whichever "
               "order the swap proves is never worse.",
               "Jobs with deadlines **and** profits, where some may be skipped, still "
               "greedy — but the slot choice needs care (latest free slot)."),
        _route("“merge overlapping”, “insert into a schedule”, “total covered length”",
               "intervals",
               "Sort by **start** and build left to right; only the last merged block "
               "can overlap the next.",
               "Keeping the most intervals is the other sort — by **end**."),
        _route("“maximum non-overlapping”, “fewest removals / arrows”",
               "intervals",
               "Sort by **end**, keep greedily. The earliest finish leaves the most room.",
               "Each interval has a **weight** and you maximise total weight: greedy "
               "fails. Sort by end, binary-search the predecessor, and DP."),
        _route("“minimum rooms / platforms”, “busiest moment”",
               "intervals",
               "Peak concurrency: a ±1 sweep over sorted events, or a min-heap of ends.",
               "Release before you allocate at equal timestamps, or the peak is one "
               "too high."),
    ])


# --- Unit 11 — Recursion -----------------------------------------------------

_unit(
    "recursion", "Recursion", "🌀", _S3,
    "Trust the smaller call. Every branching technique depends on it.",
    weight=2,
    prereqs=["loops-and-digits", "complexity"],
    why="""
Recursion is not a technique for a family of problems; it is the *notation*
every remaining unit is written in. Tree traversal, backtracking, DFS, divide
and conquer and the top-down half of dynamic programming are all one pattern:
express the answer in terms of the same function on a smaller input.

The block people hit is almost never syntax. It is refusing to **trust the
recursive call** — trying to trace the whole stack in their head instead of
assuming the smaller call is already correct and asking only what to do with its
result.
""",
    model="""
### The contract

Write a recursive function by answering three questions, in this order:

1. **What does this function promise?** One sentence, for *any* valid input.
   "`depth(node)` returns the height of the subtree rooted at `node`." If you
   cannot write that sentence, no amount of tracing will help.
2. **Base case.** The smallest input, answered without recursion. It is almost
   always `null`, empty, or zero — and it is almost always where the bug is.
3. **Recursive case.** Assume the promise holds for smaller inputs. Call, and
   combine. Do not trace.

```java
static int depth(Node node) {
    if (node == null) return 0;                       // base
    return 1 + Math.max(depth(node.left), depth(node.right));   // combine
}
```

### The cost

Each call keeps a stack frame, so a recursion n deep costs O(n) **memory** even
if it allocates nothing. Java's default stack overflows around 10,000 frames —
which is why a recursive walk over a 10⁵-long linked list crashes and an
iterative one does not.

The time cost comes from the recurrence:

| Recurrence | Solves to | Example |
| --- | --- | --- |
| `T(n) = T(n−1) + O(1)` | O(n) | Walking a list |
| `T(n) = 2T(n−1) + O(1)` | O(2ⁿ) | Naive Fibonacci |
| `T(n) = T(n/2) + O(1)` | O(log n) | Binary search, fast power |
| `T(n) = 2T(n/2) + O(n)` | O(n log n) | Merge sort |

### Halving

Fast exponentiation makes one call on half the exponent:

```java
static long power(long b, long e) {
    if (e == 0) return 1;
    long half = power(b, e / 2);      // ONE call, not two
    return (e % 2 == 0) ? half * half : half * half * b;
}
```

Calling `power(b, e/2)` twice instead of storing it turns O(log e) into O(e).
That single line is the difference, and it is the same insight as memoisation:
never compute the same thing twice.

### Divide and conquer

Split into **independent** parts, solve each, combine. Merge sort is the
canonical example, and the one the sorting unit builds on:

```java
static void sort(int[] a, int[] buf, int lo, int hi) {   // sorts [lo, hi)
    if (hi - lo < 2) return;                             // base: 0 or 1 element
    int mid = (lo + hi) >>> 1;
    sort(a, buf, lo, mid);                               // trust it
    sort(a, buf, mid, hi);                               // trust it
    merge(a, buf, lo, mid, hi);                          // two-pointer merge, O(n)
}
```

Read the cost off the code: two calls on halves plus linear work is
`T(n) = 2T(n/2) + O(n)`. The recursion tree has log n levels and the merges on
each level touch every element once, so the total is O(n log n).

The halves do not have to be halves. *Different ways to add parentheses* splits
at every operator, solves both sides, and combines every pair of results — the
same three steps with a different split.

### When recursion repeats itself

Naive Fibonacci is O(2ⁿ) because `fib(n−2)` is recomputed on both branches. Two
fixes, and the whole DP stage is built on them:

- **Memoise**: cache each answer by argument. Top-down DP.
- **Iterate**: compute the small answers first. Bottom-up DP.

Recognising the overlap is the skill. The DP unit later is this observation with
a syllabus attached.

### Reading the cost: the Master theorem

Most divide-and-conquer recurrences have the shape `T(n) = a·T(n/b) + f(n)`:
`a` subproblems, each `1/b` the size, plus `f(n)` work to split and combine.
Compare `f(n)` with `n^(log_b a)`, the number of leaves in the recursion tree:

| Case | Who wins | Result | Example |
| --- | --- | --- | --- |
| `f(n)` smaller | The leaves | `O(n^(log_b a))` | `T = 4T(n/2) + n` → O(n²) |
| Equal | Every level ties | `O(n^(log_b a) · log n)` | Merge sort, `2T(n/2) + n` → O(n log n) |
| `f(n)` larger | The root | `O(f(n))` | `T = 2T(n/2) + n²` → O(n²) |

You rarely need the formal statement. The picture is enough: **total work = sum
over levels**, and you only have to decide whether the levels shrink, stay
level, or grow as you go down.

### Divide and conquer beyond sorting

The interesting part of a divide and conquer is never the split; it is the
**answer that straddles the midpoint**. Maximum subarray by halves: the best
subarray is entirely in the left half, entirely in the right, or it *crosses the
middle* — and the crossing one is the best suffix of the left glued to the best
prefix of the right, found in O(n). So `T(n) = 2T(n/2) + O(n)` = O(n log n).

Closest pair of points, counting inversions and the majority element by halves
all have the same shape: two recursive calls you trust, and one linear pass that
handles the pairs neither call could see.
""",
    signals=[
        _sig("“the same problem on a smaller input”", "Recursion",
             "Subtrees, suffixes, “with one more item chosen”."),
        _sig("A tree or nested structure", "Recursion over the children",
             "The structure is already recursive; mirror it."),
        _sig("“combine the halves”", "Divide and conquer",
             "Two independent halves, then a merge step."),
        _sig("Exponent or range halves each step", "O(log n) recursion",
             "Compute the half once and reuse it."),
        _sig("The same sub-input recurs on different branches", "Memoise",
             "Overlapping subproblems is the definition of DP."),
        _sig("Depth could reach 10⁵", "Convert to iteration",
             "The call stack, not the algorithm, is what will fail."),
    ],
    skeletons=[
        _sk("The three-part shape",
            "Every recursive function you will write from here on.",
            """
static R solve(Input x) {
    if (isBase(x)) return baseAnswer(x);      // 1. smallest case
    R sub = solve(smaller(x));                // 2. trust the call
    return combine(x, sub);                   // 3. use the result
}
""",
            "Write the one-sentence promise above the function before the body."),
        _sk("Fast exponentiation",
            "Powers, matrix powers, repeated doubling.",
            """
static long power(long b, long e, long mod) {
    if (e == 0) return 1;
    long half = power(b, e / 2, mod);      // computed ONCE
    long sq = half * half % mod;
    return (e % 2 == 0) ? sq : sq * b % mod;
}
""",
            "Two recursive calls here would make it O(e) instead of O(log e)."),
        _sk("Divide and conquer (merge sort)",
            "Sort, count across a midpoint, combine independent halves.",
            """
static void sort(int[] a, int[] buf, int lo, int hi) {    // [lo, hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    sort(a, buf, lo, mid);
    sort(a, buf, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) buf[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) buf[k++] = a[i++];
    while (j < hi)  buf[k++] = a[j++];
    System.arraycopy(buf, lo, a, lo, hi - lo);
}
""",
            "One buffer allocated by the caller. `<=` keeps equal elements in order — that is stability."),
        _sk("Memoised recursion",
            "Whenever the same argument recurs across branches.",
            """
long[] memo = new long[n + 1];
Arrays.fill(memo, -1);

static long fib(int n) {
    if (n < 2) return n;
    if (memo[n] != -1) return memo[n];
    return memo[n] = fib(n - 1) + fib(n - 2);
}
""",
            "O(2ⁿ) → O(n) by adding two lines. This is top-down DP."),
    ],
    costs=[
        _cost("Linear recursion", "O(n)", "O(n) stack", "Depth is the space cost."),
        _cost("Binary recursion, no memo", "O(2ⁿ)", "O(n) stack", "Naive Fibonacci."),
        _cost("Halving recursion", "O(log n)", "O(log n)", "Fast power, binary search."),
        _cost("Divide and conquer with a linear merge", "O(n log n)", "O(n)", "Merge sort."),
        _cost("Memoised recursion", "O(states × work)", "O(states)", "Top-down DP."),
    ],
    pitfalls=[
        _pit("`StackOverflowError`",
             "Either no base case, or a legitimate recursion deeper than ~10,000 frames.",
             "Check the base case first; if the depth is genuinely large, rewrite iteratively."),
        _pit("The base case returns the wrong identity",
             "`return 0` where the combination multiplies, or `return 1` where it sums.",
             "Ask what the answer for an empty input *must* be for the combination to work."),
        _pit("An exponential runtime in something that looks linear",
             "A sub-answer is recomputed on multiple branches.",
             "Memoise, or restructure so each sub-answer is computed once."),
        _pit("Fast power is O(e) instead of O(log e)",
             "`power(b, e/2)` was written twice rather than stored.",
             "Call once, store in a local, square it."),
        _pit("A shared mutable structure leaks between branches",
             "State was modified before the call and never restored after it.",
             "Either pass immutable arguments, or undo the change — see backtracking."),
        _pit("A divide and conquer is right on small inputs and wrong on large ones",
             "The combine step forgot the answer that crosses the midpoint.",
             "List the three places the answer can be: left, right, straddling. The third "
             "is the one you write code for."),
        _pit("A memoised recursion is still slow",
             "The memo is a `HashMap<String, …>` keyed by a string built on every call, or "
             "the sentinel collides with a real answer (0 used as “unset”).",
             "Index an array by the integer arguments; use −1 (or a separate `boolean[]`) "
             "as the “not computed” marker."),
        _pit("The recursion never shrinks on a two-element range",
             "`mid = (lo + hi) / 2` with a recursive call on `[mid, hi]` — when `hi = lo + 1`, "
             "that is the same range.",
             "Use half-open ranges and recurse on `[lo, mid)` and `[mid, hi)`; stop at size < 2."),
    ],
    lessons=["recursion", "alg_recursion", "alg_recurrences", "recurrence"],
    checks=[
        _chk("What are the three parts of writing a recursive function?",
             "A one-sentence promise about what it returns for any input; a base case that "
             "needs no recursion; and a recursive case that trusts the promise and combines."),
        _chk("Why does naive Fibonacci take exponential time?",
             "`fib(n-2)` is recomputed under both `fib(n-1)` and `fib(n-2)`, so the call "
             "tree branches twice at nearly every level: T(n) = T(n−1) + T(n−2)."),
        _chk("What is the space complexity of a recursion n levels deep that allocates "
             "nothing?",
             "O(n) — every pending frame stays on the call stack until it returns."),
        _chk("Why must fast exponentiation store the half-power in a variable?",
             "Calling it twice doubles the work at every level, collapsing O(log e) back to "
             "O(e). Storing it is the entire optimisation."),
        _chk("Why is merge sort O(n log n), read straight from its code?",
             "Two calls on halves plus a linear merge: T(n) = 2T(n/2) + O(n). There are log n "
             "levels of halving, and the merges on each level handle all n elements once."),
        _chk("What does `T(n) = 4T(n/2) + O(n)` solve to, and why?",
             "O(n²). Each level has 4× the calls on half the size, so level work doubles "
             "going down: n, 2n, 4n, … The leaves dominate — n^(log₂4) = n² of them."),
        _chk("Does writing a Java method in tail-recursive form save stack space?",
             "No. The JVM performs no tail-call elimination, so every call still keeps a "
             "frame. Tail form only makes the conversion to a loop mechanical."),
        _chk("In maximum subarray by halves, what does the combine step compute?",
             "The best subarray that *crosses* the midpoint: the best suffix sum of the left "
             "half plus the best prefix sum of the right half, in O(n). The answer is the "
             "maximum of that and the two recursive results."),
        _chk("Tower of Hanoi and naive Fibonacci both make two calls. Why can only one be "
             "memoised into polynomial time?",
             "Fibonacci's two calls share arguments, so its exponential tree has only n "
             "distinct nodes. Hanoi's output — the move list — is itself 2ⁿ − 1 long, so any "
             "algorithm that prints it is exponential."),
        _chk("When would you choose an explicit stack over recursion?",
             "When the depth can reach ~10⁴ or more (a path graph, a degenerate tree, a long "
             "list). The algorithm is unchanged; the frames move from the thread stack to "
             "the heap."),
    ],
    interview="""
Interviewers probe recursion by asking for the complexity and then for the
iterative version. Have both ready: the recurrence that gives the time bound,
and the observation that depth is memory. And when a recursive solution is
exponential, say *why* — "the same subproblem appears on both branches, so I
will memoise" is the sentence that turns a rejected answer into an accepted one.
""",
    invariant=_inv(
        "**The promise**: for every input smaller than the current one, `solve` "
        "already returns the right answer. That sentence is the recursion's invariant, "
        "and it is induction wearing a function signature.",
        "The base case establishes it: the smallest inputs are answered directly, with "
        "no call at all, so the promise holds for them without any assumption.",
        "The recursive case maintains it. Assume the promise for every strictly smaller "
        "input; the body calls only on smaller inputs and combines their answers "
        "correctly, so the promise now holds for this input too. The load-bearing word "
        "is **strictly** — a call on an input that is not smaller (`solve(n)` inside "
        "`solve(n)`, or `mid` that fails to shrink the range) breaks the chain, and the "
        "symptom is a `StackOverflowError`.",
        "The top-level call is just one more input of the size you care about. The "
        "promise holds for it, so its return value is the answer.",
        "This is why you should never trace a recursion to convince yourself it works: "
        "the trace checks one input, and the induction checks all of them. Trace only "
        "to find a bug — usually in the base case or the combine.",
    ),
    variants=[
        _var("Linear (decrement)",
             "One call on `n − 1` (or the tail of a list), then an O(1) combine.",
             "Sums, list walks, counting down. Mostly a teaching shape — a loop is better.",
             "O(n) time, O(n) stack",
             "The stack is the cost. At n = 10⁵ a Java recursion like this overflows; the "
             "loop version does not."),
        _var("Halving",
             "One call on `n / 2`, and the result is reused.",
             "Fast power, binary search written recursively, `kth-symbol-grammar`.",
             "O(log n) time and stack",
             "Store the half in a local. Two calls turns log n into n."),
        _var("Binary branching, overlapping",
             "Two calls on `n − 1` and `n − 2` (or similar) whose sub-arguments collide.",
             "Fibonacci, binomial coefficients, grid paths.",
             "O(2ⁿ) naive → O(n) or O(n²) memoised",
             "The exponential is waste, not work. Add a memo keyed by the arguments."),
        _var("Binary branching, output-sized",
             "Two calls whose results are genuinely different and all needed.",
             "Tower of Hanoi, Gray code, generating subsets.",
             "O(2ⁿ) — and that is the size of the answer",
             "No memo can help: the output itself is exponential. Say so rather than "
             "trying to optimise it."),
        _var("Divide and conquer",
             "Split into independent halves, solve both, and combine with a linear pass "
             "across the midpoint.",
             "Merge sort, counting inversions, maximum subarray by halves, closest pair.",
             "O(n log n) when the combine is O(n)",
             "The halves must be **independent**. If they share subproblems, it is DP."),
        _var("Return a list of results",
             "Each call returns *all* answers for its piece; the combine takes a product.",
             "Ways to add parentheses, unique BSTs, expression trees.",
             "Catalan-sized output",
             "Memoise on the substring or range when pieces repeat — they usually do."),
        _var("Accumulator passed down",
             "Carry the partial answer as a parameter instead of combining on the way up.",
             "Path sums, building a string, tail-recursive loops.",
             "Same time; the combine moves into the argument",
             "A mutable accumulator shared between branches must be undone after each "
             "call — that is backtracking."),
    ],
    rewrites=[
        _rw("Fibonacci, from exponential to linear",
            """
// O(2^n) — fib(n-2) is recomputed under both branches
static long fib(int n) {
    if (n < 2) return n;
    return fib(n - 1) + fib(n - 2);
}
""",
            """
// O(n) — each argument is computed once
static long[] memo = new long[91];      // fib(90) still fits in a long

static long fib(int n) {
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];
    return memo[n] = fib(n - 1) + fib(n - 2);
}
""",
            "Two lines: look the argument up before recursing, and store the result before returning.",
            """
The call tree of naive `fib(n)` has about φⁿ nodes, but only **n distinct
arguments**. Every node beyond the first for each argument is the same question
asked again.

The memo makes the second asking free. Each argument is now computed once, at
O(1) work beyond its two lookups, so the whole tree collapses to n nodes.

**No answer is lost** because `fib(k)` depends on nothing but `k` — a pure
function — so a stored result is the result. That condition is exactly what
fails when a recursion reads or mutates shared state, and why memoising a
backtracking search is usually wrong.
"""),
        _rw("Fast power: one call, not two",
            """
// O(e) — both calls compute the same half
static long power(long b, long e) {
    if (e == 0) return 1;
    if (e % 2 == 0) return power(b, e / 2) * power(b, e / 2);
    return b * power(b, e / 2) * power(b, e / 2);
}
""",
            """
// O(log e) — the half is computed once and squared
static long power(long b, long e) {
    if (e == 0) return 1;
    long half = power(b, e / 2);
    return (e % 2 == 0) ? half * half : half * half * b;
}
""",
            "The repeated call becomes a local variable.",
            """
Each level of the slow version makes two calls on half the exponent, so the
recurrence is `T(e) = 2T(e/2) + O(1)` — which is O(e), exactly the cost of
multiplying in a loop. The halving bought nothing.

Storing the result makes it `T(e) = T(e/2) + O(1)` = O(log e). It is the same
insight as memoisation, at its smallest: the two calls had the **same
argument**, so their results are equal, so one of them is waste.
"""),
        _rw("A deep recursion, made iterative",
            """
// Overflows the stack for lists of ~10^4 nodes and up
static int length(Node node) {
    if (node == null) return 0;
    return 1 + length(node.next);
}
""",
            """
// O(1) stack at any length
static int length(Node node) {
    int count = 0;
    for (Node cur = node; cur != null; cur = cur.next) count++;
    return count;
}
""",
            "The call stack becomes a loop variable, because each frame only waits to add 1.",
            """
Linear recursion stores one frame per element, so its **space** is O(n) even
though it allocates nothing. The JVM's default thread stack holds roughly
10,000–20,000 small frames; a 10⁵-node list throws `StackOverflowError`.

The recursive version does nothing after its call except `1 +`. Whenever the
work after the call is that simple, the frame can be replaced by an accumulator
and the recursion by a loop. Java does not do this for you (there is no
tail-call elimination), so you do it by hand.

When the work after the call is *not* simple — a tree with two children, a
DFS — the rewrite needs an explicit `Deque` as the stack instead.
"""),
    ],
    internals="""
### What a call actually costs

Every call pushes a **frame** onto the thread's stack: the return address, the
parameters, and every local variable. It is popped when the call returns. A
frame for a small method is tens of bytes; the default Java thread stack is
typically 512 KB–1 MB, set by `-Xss`. That puts the practical depth limit at
**about 10⁴ frames**, and less when frames are fat.

Nothing in the algorithm's Big-O mentions this, which is why it catches people:
a DFS over a 10⁵-node path graph is O(n) time and still crashes.

### Three ways out

1. **Rewrite as a loop** — whenever the work after the call is trivial (see the
   rewrites above).
2. **An explicit stack** — a `Deque<Frame>` on the heap, which holds millions of
   entries. This is how iterative DFS and iterative in-order traversal work.
3. **Run on a thread with a bigger stack** — the competitive-programming
   escape hatch:

```java
new Thread(null, () -> solve(), "main", 1 << 26).start();   // 64 MB stack
```

Correct, and occasionally the pragmatic answer, but in an interview say option
1 or 2 first.

### No tail calls in Java

A call is a *tail call* when nothing happens after it returns:
`return helper(n - 1, acc * n);`. Some languages reuse the frame for tail calls,
making such recursion O(1) space. **The JVM does not.** Writing a function in
tail-recursive style in Java changes nothing about its stack depth — it only
makes the conversion to a loop mechanical.

### Memoisation's hidden cost

A `HashMap<Long, Long>` memo boxes both key and value and hashes on every
lookup — roughly 10× slower than a `long[]` indexed by the argument. When the
arguments are small integers, use an array; when they are a pair `(i, j)`, use
a 2-D array; reach for a map only when the argument space is sparse or not an
integer range.
""",
    build_it="""
### Write these from an empty file

**1. `power(b, e, mod)`.** Recursive, then iterative (square the base, halve the
exponent, multiply in when the low bit is set). Check both against a loop for
`e` up to 1000 and against each other for `e = 10¹⁸`.

**2. Merge sort** with one caller-allocated buffer. Then add a counter to the
merge and return the number of inversions — without changing the sort.

**3. Tower of Hanoi, printing the moves.** State the promise first:
*"`hanoi(n, from, to, via)` prints the moves that transfer the top n disks from
`from` to `to`."* Then the body is three lines. Count the moves and confirm
2ⁿ − 1.

**4. Naive against memoised Fibonacci.** Time `fib(40)` both ways. Then count
the calls the naive version makes — add a static counter — and compare with
`fib(41)`. The ratio is φ ≈ 1.618.

**5. Break the stack on purpose.** Recurse over a 10⁶-long linked list, observe
the `StackOverflowError`, then fix it twice: with a loop, and by running the
same recursion on a `Thread` with a 256 MB stack. Say which you would ship.

**6. Maximum subarray by halves.** Write the O(n log n) divide and conquer with
the crossing sum, then compare with Kadane's O(n). The point is not that it is
faster — it is not — but that the crossing term is the whole technique.
""",
    rungs=[
        _rung("Core", "A recurrence you can write in one line.",
              ["nth-fibonacci", "binomial-coefficient", "unique-paths-count"],
              {"nth-fibonacci": "Write it naively, note it is O(2ⁿ), then memoise. That one edit is the whole DP stage in miniature.",
               "binomial-coefficient": "Pascal's rule, word for word. Count the calls for C(20, 10), then ask what C(60, 30) would cost.",
               "unique-paths-count": "`paths(i,j) = paths(i-1,j) + paths(i,j-1)`. Same shape, two dimensions."}),
        _rung("Variations", "Recursion that halves rather than decrements.",
              ["fast-power"],
              {"fast-power": "Store the half-power. Calling twice is the bug that makes it O(e)."}),
        _rung("Two calls", "Recursion that branches, where the exponential cost is the answer's own size.",
              ["tower-of-hanoi"],
              {"tower-of-hanoi": "Trust the smaller call. Then compare with `nth-fibonacci`: both make two calls, and only one of them can be fixed by a memo."}),
    ],
    next_up="""
Merge sort is the first algorithm here you could not write without trusting a
recursive call. The next unit asks what sorting costs, what it buys — and which
two recursive ideas are worth more than the library call.
""",
)


# --- Unit 12 — Sorting -------------------------------------------------------

_unit(
    "sorting", "Sorting & Ordering", "🔡", _S3,
    "What sorting costs, what it buys, and the two sorting ideas worth more than the call.",
    weight=2,
    prereqs=["arrays-first-pass", "complexity", "recursion"],
    why="""
You will rarely ship your own sort. You will constantly *decide whether to call
one*, and that decision is one of the most reliable dividing lines between an
O(n²) solution and an O(n log n) one. Sorting by a **derived key** — by
frequency, by the second element, with a tie-break — is the part of that call
interviews test directly, and writing the `Comparator` correctly is a small
skill with a large payoff.

But two sorting *algorithms* are worth knowing from the inside, because their
ideas solve problems no library call does. **Quickselect** is quicksort that
recurses into one side only, and finds the k-th element in O(n) average. **Merge
sort's merge** sees every pair that crosses the midpoint, so it can *count*
them — inversions, smaller-to-the-right, pairs with a condition — in O(n log n).
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

If the values are small integers, counting sort is O(n) and beats it: the
O(n log n) lower bound only binds sorts that learn from comparisons, and using a
value as an array index learns more. If you only need the k largest, a heap is
O(n log k). If you only need the k-th, quickselect is O(n) average. Sorting is
the general answer, not always the best one — and saying so is worth points.

### Quickselect

Partition around a pivot the way quicksort does, so everything smaller is on
the left and everything larger on the right. The pivot is now at its final
sorted index p. If p is the index you want, stop; otherwise recurse into **one**
side only.

```java
int select(int[] a, int lo, int hi, int k) {        // k-th smallest, 0-based, in [lo, hi]
    while (true) {
        int p = partition(a, lo, hi);                 // random pivot → its sorted index
        if (p == k) return a[p];
        if (p < k) lo = p + 1; else hi = p - 1;       // discard the other side
    }
}
```

Each round discards a constant fraction on average, so the work is
n + n/2 + n/4 + … = O(n). A pivot that is always the smallest element makes it
O(n²) — which is why the pivot is **random**.

### Merge sort, reused

The recursion unit's merge takes elements from two sorted halves. When it takes
from the **right** half while `mid − i` elements are still waiting in the left,
each of those is larger and comes earlier: `mid − i` inversions, counted in O(1).

```java
while (i < mid && j < hi) {
    if (a[i] <= a[j]) buf[k++] = a[i++];
    else { inversions += mid - i; buf[k++] = a[j++]; }
}
```

Every cross-midpoint pair is seen exactly once across the recursion, so the
count costs nothing beyond the sort itself.
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
        _sk("Quickselect",
            "The k-th smallest or largest, without sorting everything.",
            """
static final Random RNG = new Random();

static int kthSmallest(int[] a, int k) {             // 0-based k
    int lo = 0, hi = a.length - 1;
    while (true) {
        int r = lo + RNG.nextInt(hi - lo + 1);
        swap(a, r, hi);                               // random pivot, moved to the end
        int p = lo;
        for (int i = lo; i < hi; i++)
            if (a[i] < a[hi]) swap(a, i, p++);        // Lomuto partition
        swap(a, p, hi);                               // pivot lands at its sorted index
        if (p == k) return a[p];
        if (p < k) lo = p + 1; else hi = p - 1;
    }
}
""",
            "k-th largest is `kthSmallest(a, n − k)`. The random pivot is what makes O(n) the expected case."),
        _sk("Count while merging",
            "Inversions, and any \"pairs i < j with a[i] > a[j]\" count.",
            """
static long sortCount(int[] a, int[] buf, int lo, int hi) {   // [lo, hi)
    if (hi - lo < 2) return 0;
    int mid = (lo + hi) >>> 1;
    long c = sortCount(a, buf, lo, mid) + sortCount(a, buf, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) {
        if (a[i] <= a[j]) buf[k++] = a[i++];
        else { c += mid - i; buf[k++] = a[j++]; }     // a[j] jumps every a[i..mid)
    }
    while (i < mid) buf[k++] = a[i++];
    while (j < hi)  buf[k++] = a[j++];
    System.arraycopy(buf, lo, a, lo, hi - lo);
    return c;
}
""",
            "`<=`, not `<`: equal values are not an inversion. The count can reach n²/2 — use `long`."),
        _sk("Three-way partition",
            "Many duplicates; sort-colours; quicksort that survives equal keys.",
            """
int lt = lo, i = lo, gt = hi;              // [lo,lt) < p, [lt,i) == p, (gt,hi] > p
while (i <= gt) {
    if      (a[i] < p) swap(a, lt++, i++);
    else if (a[i] > p) swap(a, i, gt--);    // do NOT advance i: a[i] is unexamined
    else               i++;
}
""",
            "Four regions, and the unexamined one is `[i, gt]`. Write them above the loop."),
        _sk("LSD radix sort (non-negative ints)",
            "Fixed-width keys — O(4 · (n + 256)) with no comparisons.",
            """
int[] buf = new int[n];
for (int shift = 0; shift < 32; shift += 8) {
    int[] cnt = new int[257];
    for (int x : a) cnt[((x >>> shift) & 255) + 1]++;
    for (int d = 0; d < 256; d++) cnt[d + 1] += cnt[d];     // start of each bucket
    for (int x : a) buf[cnt[(x >>> shift) & 255]++] = x;     // stable: input order kept
    int[] t = a; a = buf; buf = t;
}
""",
            "Four stable counting passes, one byte each. Stability is what lets later passes keep earlier ones' work."),
    ],
    costs=[
        _cost("`Arrays.sort(int[])`", "O(n log n)", "O(log n)", "Quicksort; not stable."),
        _cost("`Arrays.sort(T[])` / `list.sort`", "O(n log n)", "O(n)", "Timsort; stable."),
        _cost("Counting sort", "O(n + k)", "O(k)", "k = value range."),
        _cost("k-th largest via heap", "O(n log k)", "O(k)", "Better than sorting when k ≪ n."),
        _cost("k-th largest via quickselect", "O(n) average", "O(1)", "O(n²) worst case."),
        _cost("Merge sort, counting inversions", "O(n log n)", "O(n)", "The count rides along with the merge."),
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
        _pit("Quickselect times out on sorted input",
             "The pivot is always the first or last element, so each partition removes one "
             "element and the total is O(n²).",
             "Pick the pivot at random (or shuffle once first)."),
        _pit("The inversion count is too high on inputs with duplicates",
             "The merge takes from the right half when values are equal, counting equal pairs.",
             "Take from the left on ties: `a[i] <= a[j]`."),
        _pit("Radix sort output is sorted by the last digit only",
             "A pass was not stable — it wrote buckets front to back from the wrong end, or "
             "sorted in place.",
             "Prefix-sum the counts and fill the output **from the back**, walking the input "
             "backwards."),
        _pit("Three-way partition skips elements or loops forever",
             "`i` advanced after swapping with `gt`, or the loop ran `i < gt` with an "
             "inclusive `gt`.",
             "Decide whether `gt` is inclusive, write the four regions down, and advance `i` "
             "only on the `<` and `=` branches."),
        _pit("Sorting a huge `Integer[]` is far slower than expected",
             "Boxed comparisons and a lambda call per comparison, on top of Timsort's O(n) buffer.",
             "Sort a primitive array where possible — pack `(key, index)` into a `long`."),
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
        _chk("Why is quickselect O(n) on average when quicksort is O(n log n)?",
             "After partitioning, quickselect recurses into one side only. The sizes shrink "
             "geometrically — n + n/2 + n/4 + … < 2n — instead of every level processing all n."),
        _chk("During merge sort's merge, a[j] from the right half is taken while i < mid. "
             "How many inversions does that reveal?",
             "`mid − i`: every element still waiting in the left half is larger than a[j] and "
             "sits before it in the original array."),
        _chk("Why can no comparison sort beat O(n log n)?",
             "Each comparison yields one bit, and the sort must tell apart all n! input "
             "orders, so it needs at least log₂(n!) ≈ n log₂ n comparisons."),
        _chk("Radix sort processes the least significant digit first. What property must "
             "each pass have, and why?",
             "Stability. After sorting by digit d, elements equal in d must keep the order "
             "the earlier (less significant) passes gave them — otherwise that work is lost."),
        _chk("In a three-way partition, why does the `> pivot` branch not advance `i`?",
             "It swaps `a[i]` with `a[gt]`, bringing in an element nobody has examined. "
             "Advancing `i` would skip it."),
        _chk("How do you sort by a key but still report original indices?",
             "Sort an index array (`Integer[] idx`) with a comparator that reads "
             "`a[idx[i]]` — an argsort — or sort `(value, index)` pairs."),
        _chk("Why does `largest-number` need a pairwise comparator rather than a key?",
             "Whether x goes before y depends on y: compare the concatenations `x + y` and "
             "`y + x`. There is no single number per element that captures that."),
    ],
    interview="""
The sorting question in an interview is usually "you sorted; did you need to?".
Have the three alternatives ready: counting sort when the range is small, a heap
when you want the top k, quickselect when you want exactly the k-th — and be
able to *write* quickselect, because "the k-th largest in O(n)" is a common
follow-up. When a problem asks to count pairs that are out of order, say
"merge sort, counting at the merge" before anything else.
""",
    invariant=_inv(
        "During a Lomuto partition of `a[lo..hi]` with the pivot parked at `a[hi]`: "
        "**`a[lo..p)` are all < pivot, and `a[p..i)` are all ≥ pivot.** Everything from "
        "`i` to `hi − 1` has not been looked at yet.",
        "Before the loop `p = i = lo`, so both regions are empty and the sentence is "
        "vacuously true.",
        "Look at `a[i]`. If it is ≥ pivot, it already belongs at the end of the second "
        "region: `i++` grows that region by one and nothing moves. If it is < pivot, swap "
        "it with `a[p]` — the first element of the ≥ region (or itself, if that region is "
        "empty) — and advance both `p` and `i`. The small element joins the first region, "
        "and the displaced large one moves to the end of the second. Both regions keep "
        "their property.",
        "At `i == hi` every element is classified. Swapping the pivot into `a[p]` puts it "
        "between the regions — which is exactly its position in sorted order. That is why "
        "quickselect can compare `p` with `k` and throw half away.",
        "Merge sort's merge has an invariant too: `buf[lo..k)` holds the k − lo smallest "
        "elements of both halves, in order. Every correctness argument in this unit is one "
        "of these two sentences.",
    ),
    variants=[
        _var("Library sort, natural order",
             "`Arrays.sort(a)` and then read the answer off the order.",
             "Duplicates, closest pair, k-th by index, grouping.",
             "O(n log n)",
             "Primitive sorts are unstable. If you need the original index, you have lost it."),
        _var("Sort by a derived key",
             "A `Comparator` from `comparingInt`, chained with `thenComparing`.",
             "Frequency order, custom alphabets, multi-key leaderboards.",
             "O(n log n) comparisons × key cost",
             "Precompute expensive keys once; a comparator that recomputes them runs "
             "O(n log n) times."),
        _var("Sort by a pairwise rule",
             "No key exists — the comparator decides between two items directly.",
             "Largest number (`a + b` vs `b + a`), exchange-argument schedules.",
             "O(n log n) × comparison cost",
             "Prove the rule is transitive, or the sort throws or silently misorders."),
        _var("Argsort (sort the indices)",
             "Sort `Integer[] idx` by `a[idx[i]]` instead of sorting `a`.",
             "Ranks, “original positions”, anything that needs the answer by index.",
             "O(n log n), O(n) extra",
             "The comparator reads through the array; ties need an explicit rule."),
        _var("Counting sort",
             "The value is the array index; no comparisons.",
             "Ages, grades, letters — any bounded range k.",
             "O(n + k)",
             "Only when k is O(n). A range of 10⁹ allocates 4 GB."),
        _var("Radix sort (LSD)",
             "Counting sort by one digit at a time, least significant first, stable each pass.",
             "Fixed-width integers, strings of equal length, suffix-array doubling.",
             "O(d · (n + base))",
             "Each pass **must be stable**, or earlier digits' order is destroyed."),
        _var("Bucket sort / pigeonhole",
             "Scatter values into n buckets by range, then look only at bucket boundaries.",
             "Maximum gap, uniformly spread reals, top frequencies.",
             "O(n) expected",
             "Maximum gap uses the pigeonhole bound: the answer is never inside one bucket."),
        _var("Three-way partition",
             "`< pivot | = pivot | > pivot` with three pointers.",
             "Sort colours, quicksort on many duplicates.",
             "O(n), O(1) space",
             "The `>` branch swaps in an unexamined element, so it must **not** advance `i`."),
        _var("Quickselect",
             "Partition, then recurse into the one side containing index k.",
             "k-th element, median, “closest k to the origin”.",
             "O(n) average, O(n²) worst",
             "The pivot must be random. Sorted input with a fixed pivot is the worst case."),
        _var("Merge sort with a counter",
             "Count at the merge whenever the right element wins.",
             "Inversions, reverse pairs, smaller-after-self, range-sum counts.",
             "O(n log n)",
             "For a condition that is not the sort order (`a[i] > 2·a[j]`), count in a "
             "**separate** two-pointer pass before merging."),
    ],
    rewrites=[
        _rw("A comparator that cannot overflow",
            """
// Wrong on extreme values: a - b overflows int
Arrays.sort(boxed, (a, b) -> a - b);
list.sort((p, q) -> p[1] - q[1]);
""",
            """
// Safe for every int
Arrays.sort(boxed, Integer::compare);
list.sort(Comparator.comparingInt(p -> p[1]));
""",
            "Subtraction becomes `Integer.compare` (or a `comparingInt` factory).",
            """
A comparator only needs the **sign** of its result. `a - b` has the right sign
until it overflows: `Integer.MIN_VALUE - 1` wraps to `Integer.MAX_VALUE`, so a
very small value compares as larger than everything.

The sort does not crash. It produces an order that is wrong only for inputs near
the limits, which is exactly what the hidden tests contain. `Integer.compare`
returns −1, 0 or 1 by comparison, never by arithmetic, so there is nothing to
overflow.
"""),
        _rw("The k-th largest, without sorting everything",
            """
// O(n log n) — orders all n values to read one
int[] b = a.clone();
Arrays.sort(b);
return b[b.length - k];
""",
            """
// O(n) average — partition, keep one side
int lo = 0, hi = a.length - 1, target = a.length - k;
while (true) {
    int p = partition(a, lo, hi);           // random pivot → its final index
    if (p == target) return a[p];
    if (p < target) lo = p + 1; else hi = p - 1;
}
""",
            "The full sort becomes a partition loop that discards the side not holding the target.",
            """
Sorting answers a harder question than was asked — the position of *every*
element — and pays O(n log n) for it.

After one partition the pivot sits at its final sorted index p. If `p` is not
the target, everything on the far side of `p` is irrelevant, and it is thrown
away without being ordered. With a random pivot the kept side is at most ¾ of
the range most of the time, so the work is n + ¾n + (¾)²n + … = O(n).

The sort is still the right answer when you need the order afterwards, or when
k changes between many queries.
"""),
        _rw("Counting inversions",
            """
// O(n²) — every pair
long inv = 0;
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[i] > a[j]) inv++;
""",
            """
// O(n log n) — the merge sees each crossing pair once
long sortCount(int[] a, int[] buf, int lo, int hi) {
    if (hi - lo < 2) return 0;
    int mid = (lo + hi) >>> 1;
    long c = sortCount(a, buf, lo, mid) + sortCount(a, buf, mid, hi);
    for (int i = lo, j = mid, k = lo; k < hi; k++) {
        if (j == hi || (i < mid && a[i] <= a[j])) buf[k] = a[i++];
        else { c += mid - i; buf[k] = a[j++]; }
    }
    System.arraycopy(buf, lo, a, lo, hi - lo);
    return c;
}
""",
            "The double loop becomes merge sort with a counter at the step where the right half wins.",
            """
Every pair `(i, j)` is either inside the left half, inside the right half, or
crosses the midpoint. The first two are counted by the recursive calls. The
third is where the merge helps: both halves are **sorted** by then, so when
`a[j]` from the right is taken, every element still waiting in the left —
`mid − i` of them — is larger. One addition counts all of them.

No pair is lost or double-counted because each pair is "crossing" at exactly one
level of the recursion: the level where its two indices first land in different
halves.
"""),
        _rw("Expensive keys, computed once",
            """
// The key is recomputed on every comparison: 2 · n log n popcounts
Arrays.sort(boxed, (x, y) -> {
    int bx = Integer.bitCount(x), by = Integer.bitCount(y);
    return bx != by ? Integer.compare(bx, by) : Integer.compare(x, y);
});
""",
            """
// Keys computed n times, then the sort compares longs
long[] keyed = new long[n];
for (int i = 0; i < n; i++)
    keyed[i] = ((long) Integer.bitCount(a[i]) << 32) | (a[i] & 0xffffffffL);
Arrays.sort(keyed);                                  // primitive sort, no boxing
for (int i = 0; i < n; i++) a[i] = (int) keyed[i];
""",
            "The comparator's key computation moves into a single pass that packs the key and value into one `long`.",
            """
A comparator runs about n log₂ n times — 2·10⁶ calls for n = 10⁵ — and each
call computes both keys. Precomputing moves that to n computations.

Packing `(key, value)` into one `long` goes further: the sort becomes a
primitive `long[]` sort, with no boxing and no lambda call per comparison, often
5–10× faster. It only works when both parts are non-negative and fit their bit
ranges — the mask `& 0xffffffffL` is what stops a negative value's sign bits
leaking into the key.
"""),
    ],
    internals="""
### What `Arrays.sort` actually runs

| Call | Algorithm | Stable | Worst case | Extra memory |
| --- | --- | --- | --- | --- |
| `Arrays.sort(int[])` (and every primitive) | Dual-pivot quicksort | No | O(n log n)* | O(log n) |
| `Arrays.sort(T[])`, `List.sort`, `Collections.sort` | Timsort | **Yes** | O(n log n) | O(n) |
| `Arrays.parallelSort` | Parallel merge + the above | Primitives: no | O(n log n) | O(n) |

*Modern JDKs fall back to heapsort when the quicksort recursion gets too deep,
so adversarial inputs no longer degrade primitives to O(n²).

**Why primitives may be unstable.** Stability means equal elements keep their
input order — but two equal `int`s are indistinguishable, so there is nothing to
preserve. Objects carry identity and other fields, so their sort must be stable,
and Timsort is.

### Insertion sort, hiding inside both

Below a small cutoff (tens of elements), both algorithms switch to insertion
sort. It is O(n²) but has almost no overhead and runs in cache, so on 30
elements it beats everything asymptotically better. That is also why "sort
the small subproblem with insertion sort" is a standard optimisation of your own
merge sort.

### Timsort in one paragraph

Real data is rarely random: it has **runs** — stretches already ascending or
descending. Timsort finds them, reverses the descending ones, extends short ones
with insertion sort, and merges runs from a stack under balance rules. On sorted
or nearly sorted input it is O(n). When one run keeps winning during a merge it
**gallops** — exponential then binary search — to copy a block at once.

### The Ω(n log n) lower bound

A comparison sort learns one bit per comparison. There are n! possible input
orders and it must distinguish all of them, so it needs at least log₂(n!)
comparisons, and log₂(n!) ≈ n log₂ n − 1.44n. **No comparison sort can beat
O(n log n).**

Counting sort and radix sort are not comparison sorts: indexing an array by a
value extracts many bits at once. That is how they reach O(n + k) — and why they
need a bounded key.

### Why the comparator contract matters

Timsort's merge assumes transitivity. When your comparator violates it
(`compare(a, b) < 0`, `compare(b, c) < 0` but `compare(a, c) > 0`), Timsort can
detect a contradiction mid-merge and throw `IllegalArgumentException:
Comparison method violates its general contract!` — typically only on larger
inputs, where the galloping path is taken. A comparator using `>=` for "less
than", or comparing doubles containing NaN, is the usual cause.
""",
    build_it="""
### Five sorts and a test harness

**0. The harness first.** Write `check(int[] a)`: clone, sort with your
implementation, and compare with `Arrays.sort`. Run it on 1,000 random arrays of
random length 0–50 with values in a small range (lots of duplicates) and a large
one. Every step below uses it.

**1. Insertion sort.** Shift, do not swap. Then count the shifts, and notice the
count is exactly the number of inversions — insertion sort is an inversion
counter running in O(n + inversions).

**2. Merge sort** with one buffer, then the inversion counter from the rewrites
above. Test the count against the O(n²) double loop.

**3. Quicksort with a three-way partition.** `lt`, `i`, `gt`: `< pivot` goes left
and both advance; `> pivot` swaps with `gt` and **only `gt` moves**; equal just
advances `i`. Write the invariant for all four regions before coding. Then feed
it an array of 10⁵ equal values and confirm it is not O(n²).

**4. Quickselect** on top of the same partition. Test the k-th against the
sorted array for every k.

**5. LSD radix sort** on non-negative ints, base 256, four passes, each a stable
counting sort into a buffer. Then extend it to negative values (flip the sign
bit before bucketing) and run the harness.

**6. A comparator contract tester.** Given `Comparator<T>` and a list, check
antisymmetry (`sgn(c(a,b)) == -sgn(c(b,a))`) and transitivity on all triples.
Run it on `(a, b) -> a - b` over values near `Integer.MIN_VALUE` and watch it fail.
""",
    rungs=[
        _rung("Warm up", "Order by something other than the value itself.",
              ["leaderboard-ranks", "sort-by-frequency"],
              {"leaderboard-ranks": "Two keys, one descending, and ranks that are shared on ties and then skip. Write the comparator with `Integer.compare`.",
               "sort-by-frequency": "Count first, then sort the keys by their count with a tie-break. The comparator is the whole exercise."}),
        _rung("Core", "Sort by a rule, then read the answer off the order.",
              ["kth-largest-element", "kth-smallest", "top-k-frequent"],
              # kth-largest-element and kth-smallest move to the Quickselect rung, and
              # top-k-frequent to the heaps unit, in tools/dsa_syllabus.py.
              {}),
    ],
    next_up="""
Sorted data has a superpower this unit has not used yet: you can find anything
in it in O(log n).
""",
)


# --- Unit 13 — Binary search -------------------------------------------------

_unit(
    "binary-search", "Binary Search", "🎯", _S3,
    "Halve the search space — over an array, or over the answer itself.",
    weight=3,
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

### The mirror image: maximise the minimum

"Place k cows so the closest two are as far apart as possible." Now the
predicate `ok(d)` = *"k cows fit with every gap ≥ d"* runs **true, true, …,
false** — larger distances get harder. You want the **last** true:

```java
long lo = 0, hi = MAX;                 // ok(lo) is known true
while (lo < hi) {
    long mid = lo + (hi - lo + 1) / 2;   // round UP
    if (ok(mid)) lo = mid;             // mid works: keep it, look higher
    else         hi = mid - 1;
}
return lo;
```

The `+ 1` is not decoration. With `lo = mid` on the true branch, a
downward-rounded `mid` equals `lo` on a two-element range and the loop never
ends. Rounding up makes `mid > lo` whenever `lo < hi`. Alternatively, search for
the first *false* with the usual template and subtract one — same answer, no new
template to remember.

### Search the value, count the positions

"The k-th smallest pairwise distance", "the k-th number in an n × m
multiplication table" — the candidates are far too many to list, but for any x
you can **count how many are ≤ x** quickly. That count is monotone in x, so:

> the answer is the smallest x with `count(x) ≥ k`.

That is lower bound again, over values instead of indices. The skill is
writing `count(x)` in O(n) or O(n log n) — usually with two pointers or one
division per row — instead of generating anything.

### Real numbers

A continuous answer (a square root, a best average) cannot use `lo < hi` — the
range never becomes empty. Two honest options:

- **Fixed iterations.** `for (int it = 0; it < 100; it++)` halves the range 100
  times, which is below `double` precision for any sane range. Never
  `while (hi - lo > 1e-9)`: at large magnitudes, that gap may be smaller than
  the spacing between doubles, and the loop never ends.
- **Scale to integers.** Six decimal places of `√n` is `⌊√(n · 10¹²)⌋` — an
  integer square root on a `long`, with no floating point at all, and an answer
  that is exactly reproducible.
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
        _sig("“maximise the minimum …” / “largest x such that …”", "Last-true search",
             "Round the midpoint up, or find the first false and subtract one."),
        _sig("“k-th smallest” among n² or n·m implicit values", "Binary search on the value + count ≤ x",
             "Count without listing — two pointers or one division per row."),
        _sig("An answer with decimals", "Fixed-iteration or integer-scaled search",
             "Never loop on an epsilon."),
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
        _sk("Last true (maximise the minimum)",
            "Largest distance, largest equal share, largest feasible x.",
            """
long lo = 0, hi = MAX;                    // ok(lo) must be true
while (lo < hi) {
    long mid = lo + (hi - lo + 1) / 2;    // round up, or lo = mid never moves
    if (ok(mid)) lo = mid;
    else         hi = mid - 1;
}
return lo;
""",
            "Round up. Or search for the first false and subtract one."),
        _sk("k-th smallest by counting",
            "k-th pair distance, k-th in a multiplication table, k-th in a sorted matrix.",
            """
long lo = MIN_VALUE, hi = MAX_VALUE;
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (countAtMost(mid) >= k) hi = mid;   // at least k values are <= mid
    else                       lo = mid + 1;
}
return lo;                                 // the smallest x with count >= k
""",
            "The answer is always a real candidate: the first x whose count reaches k must be one of the values."),
        _sk("Rotated sorted array: find the minimum",
            "Rotated, no duplicates — compare with the right end.",
            """
int lo = 0, hi = n - 1;                    // CLOSED: a[hi] is read
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] > a[hi]) lo = mid + 1;      // the drop is to the right of mid
    else                hi = mid;          // mid may be the minimum
}
return a[lo];
""",
            "Compare with `a[hi]`, not `a[lo]` — the right end tells you which side the drop is on in every case."),
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
        _pit("Search on the answer returns the upper bound unchanged",
             "`hi` was not actually feasible (for example `sum − 1`, or a days limit smaller "
             "than the item count), so the loop converged on it by default.",
             "Choose `hi` as a value you can prove works — or check `ok(lo)` after the loop."),
        _pit("The feasibility check overflows",
             "Counting hours or pieces with `int` — `Σ ceil(a[i] / speed)` or `Σ a[i] / x` — "
             "when there are 10⁵ terms up to 10⁹ each.",
             "Accumulate in `long`, and stop early once the count already exceeds the limit."),
        _pit("Maximise-the-minimum hangs",
             "`lo = mid` on the success branch with a rounded-down midpoint.",
             "Round up: `mid = lo + (hi - lo + 1) / 2`."),
        _pit("k-th by counting returns a value that is not in the set",
             "The loop stopped on `count(mid) == k` and returned `mid`, which may lie between "
             "two real values.",
             "Never stop early. Converge to the smallest x with `count(x) >= k`; that x is "
             "always a real candidate."),
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
        _chk("In a last-true search with `lo = mid` on success, why must `mid` round up?",
             "With `hi = lo + 1`, a rounded-down `mid` equals `lo`; if `ok(mid)` is true, "
             "`lo = mid` changes nothing and the loop never ends. `lo + (hi - lo + 1) / 2` "
             "is always > lo."),
        _chk("How do you find the k-th smallest pairwise distance without listing the "
             "n²/2 distances?",
             "Binary-search the distance d. For each d, count pairs with distance ≤ d using "
             "two pointers on the sorted array (O(n)). The answer is the smallest d whose "
             "count is ≥ k."),
        _chk("Why is `while (hi - lo > 1e-9)` dangerous for a real-valued search?",
             "At large magnitudes, adjacent doubles are further apart than 1e-9, so the "
             "range stops shrinking and the loop never ends. Use a fixed iteration count."),
        _chk("Rotated sorted array with duplicates: why can the worst case be O(n)?",
             "When `a[mid] == a[hi]`, the comparison says nothing about which side holds "
             "the drop ([1,1,1,0,1] vs [1,0,1,1,1]). The only safe move is `hi--`, which "
             "can happen n times."),
        _chk("Magnetic balls: why is the predicate “can place k balls with every gap ≥ d” "
             "monotone?",
             "Any placement valid for gap d is also valid for every smaller gap. So the "
             "feasible d form a prefix, and the answer is its last element."),
    ],
    interview="""
Binary search is where interviewers watch you handle boundaries under mild
pressure, so having one memorised template that you never modify is worth more
than cleverness. And when a problem says *"minimum X such that it is possible"*,
saying "that predicate looks monotone, so I can binary-search the answer and
just write the feasibility check" is one of the highest-signal sentences in the
whole interview vocabulary.
""",
    invariant=_inv(
        "For lower bound over `[lo, hi)`: **every index before `lo` holds a value "
        "< target, and every index from `hi` on holds a value ≥ target.** The answer — "
        "the first index ≥ target — is therefore somewhere in `[lo, hi]`.",
        "Initially `lo = 0` and `hi = n`. There is nothing before 0 and nothing at or "
        "after n, so both halves of the sentence are vacuously true.",
        "Take `mid` in `[lo, hi)`. If `a[mid] < target`, then — because the array is "
        "sorted — every index ≤ mid is < target too, so `lo = mid + 1` keeps the first "
        "half of the sentence true. Otherwise `a[mid] ≥ target`, and so is everything "
        "after it, so `hi = mid` keeps the second half true. Either way the range "
        "strictly shrinks, because `lo ≤ mid < hi`.",
        "When `lo == hi` the two halves meet: everything before `lo` is small, "
        "everything from `lo` is large. `lo` is the first index ≥ target, which is the "
        "answer — including `n` when every element is smaller.",
        "Binary search on the answer is the same sentence with `a[mid] < target` "
        "replaced by `!ok(mid)`. The argument never used anything about arrays except "
        "that the test is monotone — which is exactly why monotonicity is the one thing "
        "you must check.",
    ),
    variants=[
        _var("Lower bound",
             "First index with `a[i] >= t`. The base template.",
             "Existence, insertion point, count of smaller elements.",
             "O(log n)",
             "Check `lo < n` before reading `a[lo]`."),
        _var("Upper bound",
             "`a[mid] <= t` goes left-to-right instead of `<`.",
             "Count of a value: `upper − lower`. Last occurrence: `upper − 1`.",
             "O(log n)",
             "Or call lower bound on `t + 1` for integers — one template, two calls."),
        _var("First true (minimise)",
             "Replace the comparison with `ok(mid)`; `ok` true → `hi = mid`.",
             "Minimum capacity, speed, days, time.",
             "O(log range · cost of ok)",
             "`hi` must be a value you *know* is feasible, or the answer can be `hi` by default."),
        _var("Last true (maximise)",
             "`ok` true → `lo = mid`, and `mid` rounds **up**.",
             "Maximise the minimum distance, largest equal portion.",
             "O(log range · cost of ok)",
             "Round-down `mid` with `lo = mid` is an infinite loop."),
        _var("Count ≤ x over values",
             "The predicate is `count(x) >= k`, computed without listing candidates.",
             "k-th pair distance, k-th in a multiplication table or sorted matrix.",
             "O(log range · counting cost)",
             "The count must be exact at duplicates: `>= k`, not `== k`."),
        _var("Rotated or bitonic",
             "The comparison is against a neighbour or an end, not a target.",
             "Rotated minimum, rotated search, peak element, mountain arrays.",
             "O(log n); O(n) worst with duplicates",
             "Duplicates can make `a[mid] == a[hi]` uninformative — shrink `hi` by one."),
        _var("Real-valued",
             "No `lo < hi`: iterate a fixed 100 times, or scale to integers.",
             "Square roots, best average, geometric answers.",
             "O(iterations · check)",
             "`while (hi - lo > eps)` can fail to terminate at large magnitudes."),
        _var("Partition search",
             "Binary-search a *split point* in one array; the other's split is implied.",
             "Median of two sorted arrays, k-th of two sorted arrays.",
             "O(log min(n, m))",
             "Search the shorter array, and use ±∞ sentinels at the edges."),
    ],
    rewrites=[
        _rw("Finding the first position ≥ x",
            """
// O(n) — ignores that the array is sorted
int i = 0;
while (i < n && a[i] < x) i++;
return i;
""",
            """
// O(log n) — the same answer, by halving
int lo = 0, hi = n;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < x) lo = mid + 1; else hi = mid;
}
return lo;
""",
            "The linear scan's stopping condition becomes the binary search's comparison.",
            """
The scan and the search compute the same thing — the first index where
`a[i] < x` stops being true — and the scan even uses the same test. It just
asks it at every index in turn.

Sortedness means the test is `true, true, …, false, false`, so asking it at
the middle tells you which half contains the switch. Nothing to the left of a
`true` can be the answer, nothing to the right of a `false` can be *earlier*
than it. One question retires half the candidates.

A linear scan is still the right call for a single query on unsorted data —
sorting to enable one binary search costs more than the scan.
"""),
        _rw("Minimum capacity: try them all, or search them",
            """
// O(range · n) — test every capacity in order
for (long cap = maxWeight; ; cap++)
    if (daysNeeded(w, cap) <= days) return cap;
""",
            """
// O(log range · n) — the feasible capacities form a suffix
long lo = maxWeight, hi = totalWeight;
while (lo < hi) {
    long mid = lo + (hi - lo) / 2;
    if (daysNeeded(w, mid) <= days) hi = mid;
    else                            lo = mid + 1;
}
return lo;
""",
            "The upward scan over candidates becomes a binary search over the same candidates.",
            """
The loop is already "find the first capacity that works". It only fails on
speed: the range can be 10⁹ wide.

What makes the search legal is one sentence: *a capacity that works still works
if you make it larger* — more room per day can never need more days. So the
working capacities are a suffix of the range, and the first element of a suffix
is exactly what lower bound finds.

Proving that sentence is the entire difficulty of these problems; the code is
the template.
"""),
        _rw("Closed range with an equality branch → half-open",
            """
// Three branches, an inclusive hi, and a special "not found" case
int lo = 0, hi = n - 1, ans = -1;
while (lo <= hi) {
    int mid = (lo + hi) / 2;
    if (a[mid] == x) { ans = mid; hi = mid - 1; }   // keep looking left
    else if (a[mid] < x) lo = mid + 1;
    else hi = mid - 1;
}
return ans;                                          // first occurrence, or -1
""",
            """
// Two branches, no special cases
int lo = 0, hi = n;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < x) lo = mid + 1; else hi = mid;
}
return (lo < n && a[lo] == x) ? lo : -1;
""",
            "The equality branch merges into `hi = mid`, and the found/not-found decision moves after the loop.",
            """
The closed version is correct, but it carries an extra variable and three
branches, and each variant (first, last, insertion point) edits a different one
of them. That is where the off-by-ones live.

In the half-open version, "equal" and "greater" do the same thing — *mid might
be the answer, keep it* — so they are one branch. The loop always computes the
insertion point; existence is one comparison afterwards. Every variant is now
the same loop plus a different line after it.

The midpoint changes too: `lo + (hi - lo) / 2` instead of `(lo + hi) / 2`,
which cannot overflow.
"""),
        _rw("Real-valued search that always terminates",
            """
// May never end: at large magnitudes, hi - lo cannot drop below 1e-9
double lo = 0, hi = 1e12;
while (hi - lo > 1e-9) {
    double mid = (lo + hi) / 2;
    if (mid * mid < n) lo = mid; else hi = mid;
}
""",
            """
// Always 100 halvings — far below double precision on any range
double lo = 0, hi = 1e12;
for (int it = 0; it < 100; it++) {
    double mid = (lo + hi) / 2;
    if (mid * mid < n) lo = mid; else hi = mid;
}
""",
            "The epsilon condition becomes a fixed iteration count.",
            """
A `double` has 53 bits of mantissa. Near 10¹², consecutive doubles are about
10⁻⁴ apart, so `hi - lo` can never be 10⁻⁹: once `lo` and `hi` are neighbours,
`mid` rounds to one of them and the range stops shrinking. The loop spins
forever on exactly the large inputs.

100 iterations shrink any range by 2¹⁰⁰ — past the precision limit for every
magnitude a double can hold — and then stop. When the answer must be printed
to a fixed number of decimals and judged exactly, go further and scale to
integers (see `sqrt-to-six-places`).
"""),
    ],
    build_it="""
### Every template, from memory, then proven against a scan

**0. The oracle.** Write `lowerLinear(a, x)` — the four-line scan. It is
obviously correct, and it is what everything else is tested against.

**1. Lower bound, upper bound.** Half-open, no equality branch. Test on 10,000
random sorted arrays (length 0–20, values 0–5, so duplicates are dense) against
the scan, for every x from −1 to 6.

**2. First true and last true** over a boolean array `f` that is `false…true`
(or `true…false` for the second). Test every split point, including all-true and
all-false. Then deliberately round `mid` down in last-true and watch which input
hangs.

**3. Rotated minimum and rotated search.** Generate a sorted array of distinct
values, rotate it by every r, and check both against a scan.

**4. Integer square root** for every n up to 10⁶, and for n near 9.2·10¹⁸.
Your first version will overflow `mid * mid`; fix it by dividing (`mid <= n / mid`)
instead of widening.

**5. Minimum ship capacity** as search on the answer. Write `days(cap)`
separately and test it on its own first — nearly every bug in these problems is
in the predicate, not the loop.

**6. k-th smallest in a multiplication table.** `count(x) = Σ min(m, x / i)`. Test
against sorting the whole table for small n, m.
""",
    internals="""
### `lo + (hi - lo) / 2`, and the bug it avoids

`(lo + hi) / 2` is the obvious midpoint and it is wrong. With `lo` and `hi`
both near `Integer.MAX_VALUE`, the *sum* overflows to a negative number before
the division, and `mid` lands outside the array — an
`ArrayIndexOutOfBoundsException` on inputs that are otherwise fine.

`lo + (hi - lo) / 2` computes the same value and never forms the large sum:
`hi - lo` is at most the array's length. This is not a hypothetical. It was a
live bug in `java.util.Arrays.binarySearch` for nine years, and in the binary
search in Jon Bentley's *Programming Pearls* for twenty.

You will not hit it on an array of 10⁵ elements. You will hit it the moment you
binary-search a *value* range — "smallest capacity between 1 and 10⁹", "largest
gap" — where `lo` and `hi` are magnitudes rather than indices.

### Half-open `[lo, hi)` versus closed `[lo, hi]`

Two conventions, and mixing them is where every off-by-one lives.

| | Half-open `[lo, hi)` | Closed `[lo, hi]` |
|---|---|---|
| `hi` starts at | `n` | `n - 1` |
| `hi` is | one past the last candidate | a real index, readable |
| loop while | `lo < hi` | `lo < hi` (converging) or `lo <= hi` (searching) |
| narrowing | `hi = mid` | `hi = mid - 1` |
| answer | `lo` | `lo` |

Prefer half-open for *lower bound* questions: `hi = n` is exactly the "belongs
past the end" answer, so there is no absent case to special-case. Use closed
when `hi` is a value you actually read — `rotated-array-minimum` compares
`a[mid]` against `a[hi]`, which is meaningless if `hi` is one past the end.

### Why the loop terminates

The range shrinks every iteration, and that has to be *checked*, not assumed:

- `lo = mid + 1` always moves `lo` past `mid`. Safe.
- `hi = mid` only shrinks if `mid < hi`, which holds because
  `mid = lo + (hi - lo) / 2 < hi` whenever `lo < hi`. Safe.
- `lo = mid` — the shape people write by accident — does **not** shrink when
  `mid == lo`, which is the infinite loop. If a binary search hangs, this is
  the line.

### The cost, precisely

Each iteration halves the range, so the loop runs ⌈log₂ n⌉ times: 17 for
100,000 elements, 30 for a billion. The constant is a comparison and a
division. It is one of the few algorithms where the theoretical bound and the
wall-clock behaviour are effectively the same thing — the work is so small that
cache behaviour dominates, which is why a linear scan beats binary search below
roughly 64 elements.
""",
    traces=[
        _trace(
            "Lower bound for a MISSING value: 7 in [1, 3, 5, 9, 11, 13]",
            "The half-open range `[lo, hi)` with `hi` starting at `n = 6`. Watch that "
            "there is no equality branch — and that the loop still ends somewhere useful "
            "even though 7 is not in the array.",
            ["Iter", "[lo, hi)", "mid", "a[mid]", "a[mid] < 7 ?", "New range"],
            [
                ["1", "[0, 6)", "0 + 3 = 3", "9", "no", "hi = 3 → [0, 3)"],
                ["2", "[0, 3)", "0 + 1 = 1", "3", "**yes**", "lo = 2 → [2, 3)"],
                ["3", "[2, 3)", "2 + 0 = 2", "5", "**yes**", "lo = 3 → [3, 3)"],
                ["end", "[3, 3)", "—", "—", "—", "lo == hi → return **3**"],
            ],
            "Three iterations for six elements, and the answer is 3 — the index 7 *would* "
            "occupy. `a[3] == 9 != 7` tells you it is absent; the 3 tells you where it "
            "belongs and that exactly three elements are smaller. One loop, three "
            "questions answered.",
        ),
        _trace(
            "Binary search on the ANSWER: smallest ship capacity for 1…10 in 5 days",
            "Nothing here indexes the array. The search space is the capacity, bounded "
            "below by `max(w) = 10` (one package must fit) and above by `sum(w) = 55` "
            "(one day for everything). `days(cap)` is the predicate.",
            ["[lo, hi)", "mid capacity", "days(mid)", "≤ 5 days?", "New range"],
            [
                ["[10, 55]", "32", "2", "**yes** — feasible", "hi = 32"],
                ["[10, 32]", "21", "3", "**yes**", "hi = 21"],
                ["[10, 21]", "15", "5", "**yes** — exactly on budget", "hi = 15"],
                ["[10, 15]", "12", "6", "no — too slow", "lo = 13"],
                ["[13, 15]", "14", "6", "no", "lo = 15"],
                ["[15, 15]", "—", "—", "—", "return **15**"],
            ],
            "The predicate reads `no no no yes yes yes` as capacity grows, which is the "
            "only property the loop needs — and the whole difficulty of these problems is "
            "noticing that feasibility *is* monotone. Five probes over a range of 46, each "
            "costing one linear pass.",
        ),
    ],
    rungs=[
        _rung("Warm up", "The half-open template, on the two questions it was built for.",
              ["lower-bound-index", "first-true-predicate"],
              {"lower-bound-index": "Type the `[lo, hi)` loop once with no equality branch. Every other binary search in this unit is this loop with a different comparison.",
               "first-true-predicate": "The same loop with the array replaced by a predicate — which is what “binary search on the answer” means, written out in full."}),
        _rung("Core", "The template, and the insertion-point reading of it.",
              ["binary-search-first", "search-insert-position", "count-occurrences-sorted"],
              {"binary-search-first": "Duplicates are the point: you want the *first* match, which is exactly lower bound.",
               "search-insert-position": "The same code with nothing removed — the return value already is the insertion point.",
               "count-occurrences-sorted": "Upper bound for free: it is lower bound of `x + 1`. Two calls to one template beats two templates."}),
        _rung("Variations", "Searching a space that is not an array — or an array that is not sorted.",
              ["integer-sqrt", "rotated-array-minimum", "min-ship-capacity"],
              {"integer-sqrt": "No array anywhere. The predicate is `mid * mid > n`, and `mid * mid` must be computed in `long`.",
               "rotated-array-minimum": "The array is not sorted and there is no target. What is monotone is the *question* — and that is all the loop ever needed.",
               "min-ship-capacity": "Binary search on the answer, in full: name the bounds, write `feasible(x)`, argue it is monotone. The array only evaluates the predicate."}),
    ],
    next_up="""
Search finds *an* answer fast. The last two units of the stage ask for the
*best* one — and whether a single local decision, made in sorted order, can be
trusted to find it.
""",
)


# --- Unit 14 — Greedy --------------------------------------------------------

_unit(
    "greedy", "Greedy Algorithms", "💰", _S3,
    "Take the best local move — and be able to prove it was safe.",
    weight=3,
    prereqs=["sorting"],
    why="""
Greedy algorithms are the shortest, fastest solutions in the whole bank, and
the most dangerous. The code for "best answer" is often one pass with a running
maximum; the difficulty is entirely in knowing whether that is *correct*, because
a greedy algorithm that is wrong is wrong silently and usually passes the small
tests.

So this unit is mostly about the proof obligation. Two arguments cover almost
every case, and if you cannot make one of them, the answer is dynamic
programming.
""",
    model="""
### The two proof patterns

**Exchange argument.** Take any optimal solution. Show that you can swap one of
its choices for the greedy choice without making it worse. Therefore some
optimal solution contains the greedy choice, so taking it loses nothing.

*Buy and sell a stock*: the best profit ending today uses the lowest price seen
so far. Any optimal pair `(buy, sell)` can have its buy moved to the minimum
before `sell` without reducing the profit.

**Stays-ahead argument.** Show that after each step, the greedy solution is at
least as far along as any other. *Jump game*: track the furthest index
reachable; no other strategy can be further ahead after the same number of
indices, so if greedy cannot reach the end, nothing can.

### When greedy fails

The moment a choice that looks worse now enables something better later. Coin
change with `{1, 3, 4}` and amount 6: greedy takes 4, then 1, then 1 — three
coins. The optimum is 3 + 3 — two. Nothing in the greedy step could have seen
that, which is why the honest test is **construct a counterexample**. If you
cannot, and you can make one of the two arguments above, proceed.

### The usual shapes

| Shape | Greedy rule |
| --- | --- |
| Best profit / best difference | Track the running minimum (or maximum) |
| Reachability | Track the furthest point reachable |
| Scheduling non-overlapping items | Sort by **end** time, take greedily |
| Fewest groups covering everything | Sort by end, extend while it still covers |
| Repeatedly take the extreme | A heap (the heaps unit, stage 5) |

Sorting by **end** time rather than start is the classic result: finishing
earliest leaves the most room for everything after it.

### Greedy versus DP, in practice

Try greedy first — it is O(n) and simple. Spend sixty seconds trying to break
it. If you find a counterexample, the failure usually tells you the DP state:
*"the choice depends on how much is left"* means the remaining amount is a
dimension of the table.
""",
    signals=[
        _sig("“maximum profit from one buy and one sell”", "Running minimum",
             "Best sale today uses the cheapest day so far."),
        _sig("“can you reach the end?”", "Furthest reachable index",
             "Stays-ahead: nothing can be further along."),
        _sig("“maximum non-overlapping …”", "Sort by end time, take greedily",
             "Finishing earliest preserves the most room."),
        _sig("“fewest jumps / groups / arrows”", "Extend the current reach; count when forced",
             "Take a new group only when the current one cannot cover."),
        _sig("“repeatedly take the largest”", "Heap-driven greedy",
             "The heaps unit's loop — stage 5 covers the structure itself."),
        _sig("A local choice can be regretted later", "Not greedy — DP",
             "Construct the counterexample; it names the DP state."),
    ],
    skeletons=[
        _sk("Running extreme",
            "Best profit, largest gap, maximum difference.",
            """
int minSoFar = a[0], best = 0;
for (int x : a) {
    best = Math.max(best, x - minSoFar);     // sell today, having bought at the min
    minSoFar = Math.min(minSoFar, x);
}
""",
            "Evaluate before updating: you cannot buy and sell on the same tick."),
        _sk("Furthest reach",
            "Jump game, reachability, coverage.",
            """
int reach = 0;
for (int i = 0; i < n; i++) {
    if (i > reach) return false;             // a gap nothing can cross
    reach = Math.max(reach, i + a[i]);
}
return true;
""",
            "One pass, no memory — the stays-ahead argument in four lines."),
        _sk("Fewest groups (interval jumps)",
            "Minimum jumps, fewest arrows, fewest refuels.",
            """
int jumps = 0, curEnd = 0, farthest = 0;
for (int i = 0; i < n - 1; i++) {
    farthest = Math.max(farthest, i + a[i]);
    if (i == curEnd) { jumps++; curEnd = farthest; }   // forced to commit
}
""",
            "Count only when the current group is exhausted — that is what makes it minimal."),
        _sk("Schedule by end time",
            "Maximum non-overlapping intervals; minimum removals.",
            """
Arrays.sort(iv, (x, y) -> Integer.compare(x[1], y[1]));   // by END
int end = Integer.MIN_VALUE, kept = 0;
for (int[] v : iv)
    if (v[0] >= end) { kept++; end = v[1]; }
""",
            "By end, not by start. Sorting by start is the classic wrong answer."),
        _sk("Order by an exchange argument",
            "“In what order should the jobs run?” — minimise a weighted total.",
            """
Integer[] idx = new Integer[n];
for (int i = 0; i < n; i++) idx[i] = i;
// x before y  iff  swapping the adjacent pair (y, x) -> (x, y) never costs more
Arrays.sort(idx, (x, y) -> Long.compare((long) t[x] * w[y], (long) t[y] * w[x]));
""",
            "Derive the comparator from the adjacent swap, then cross-multiply in `long`."),
        _sk("Deadlines: latest free slot",
            "Unit-time jobs with deadlines and profits; skip some to maximise profit.",
            """
Arrays.sort(jobs, (x, y) -> Integer.compare(y[1], x[1]));   // by profit, descending
boolean[] used = new boolean[maxDeadline + 1];
for (int[] j : jobs)                                         // j = {deadline, profit}
    for (int s = j[0]; s >= 1; s--)
        if (!used[s]) { used[s] = true; total += j[1]; break; }
""",
            "Latest free slot, not earliest. O(n · D); a union-find over slots makes it near-linear."),
    ],
    costs=[
        _cost("Single-pass greedy", "O(n)", "O(1)", "Running extreme, furthest reach."),
        _cost("Sort-then-greedy", "O(n log n)", "O(1)", "Scheduling, intervals."),
        _cost("Heap-driven greedy", "O(n log n)", "O(n)", "Repeatedly take the extreme."),
        _cost("The DP alternative", "O(n · states)", "O(states)", "What you fall back to when the proof fails."),
    ],
    pitfalls=[
        _pit("Correct on the examples, wrong on a hidden test",
             "The greedy rule is not actually optimal; no counterexample was sought.",
             "Spend a minute trying to break it. Failing that, state which of the two "
             "arguments applies."),
        _pit("Intervals were sorted by start time",
             "Scheduling optimality depends on finishing earliest.",
             "Sort by end time for maximum non-overlapping selection."),
        _pit("Profit of 0 where a loss was expected (or vice versa)",
             "The problem allows no transaction, or requires exactly one — the two have "
             "different answers.",
             "Re-read whether doing nothing is permitted."),
        _pit("The running minimum is updated before it is used",
             "Buying and selling collapse onto the same element.",
             "Evaluate the candidate answer first, then update the running extreme."),
        _pit("Greedy coin change gives too many coins",
             "The denominations are not canonical.",
             "Use the coin-change DP in the knapsack unit (stage 7)."),
        _pit("Jump counting is one too many",
             "The loop ran to `n` rather than `n - 1`, counting an arrival at the end.",
             "Stop before the last index: reaching it needs no further jump."),
        _pit("An exchange comparator gives a wrong order on large inputs",
             "Ratios compared as `double`s, or cross-products computed in `int`.",
             "Cross-multiply in `long`: `Long.compare((long) t1 * w2, (long) t2 * w1)`."),
        _pit("Two-pass greedy (candy) is too low somewhere",
             "The second pass overwrote the first instead of taking the maximum.",
             "`c[i] = Math.max(c[i], c[i + 1] + 1)` on the right-to-left pass."),
        _pit("Deadline scheduling takes a job that blocks two better ones",
             "Each job was placed at the earliest free slot.",
             "Place each job at the **latest** free slot on or before its deadline — it "
             "leaves the early slots for jobs with early deadlines."),
    ],
    lessons=["greedy", "intervals", "heap_greedy"],
    checks=[
        _chk("What are the two standard ways to justify a greedy algorithm?",
             "An exchange argument (any optimal solution can be modified to contain the "
             "greedy choice without getting worse) and a stays-ahead argument (greedy is "
             "never behind any alternative after the same number of steps)."),
        _chk("Give a coin system where greedy change is wrong.",
             "`{1, 3, 4}` for amount 6: greedy gives 4+1+1 = three coins; the optimum is "
             "3+3 = two."),
        _chk("Why sort by end time rather than start time when scheduling?",
             "The interval that finishes earliest leaves the largest remaining window, so "
             "choosing it never rules out a better solution."),
        _chk("What should you do when you find a counterexample to your greedy rule?",
             "Switch to dynamic programming — and read the counterexample for the state: "
             "whatever the greedy step could not see is usually the missing dimension."),
        _chk("Jobs have processing time t and weight w. In what order should they run to "
             "minimise Σ w · finish time, and why?",
             "In increasing t/w (Smith's rule). Swapping adjacent x, y changes only their two "
             "terms: x first is better iff t_x·w_y < t_y·w_x. Compare by cross-multiplying."),
        _chk("To minimise the maximum lateness, what order and why?",
             "Earliest deadline first. If a later deadline runs just before an earlier one, "
             "swapping them does not increase either job's lateness beyond what the pair "
             "already had."),
        _chk("Why does fractional knapsack admit greedy but 0/1 knapsack does not?",
             "With fractions, any leftover capacity is filled by the best ratio remaining, "
             "so the ratio order is optimal. Whole items can leave capacity that two smaller, "
             "lower-ratio items would have used better."),
        _chk("What is a stress test, and why is it the best defence against a wrong greedy?",
             "Run the greedy and a brute force on thousands of small random inputs until they "
             "disagree. A wrong greedy rule is wrong on some small case, and this finds it "
             "mechanically."),
        _chk("Gas station: the tank goes negative at i after starting at s. Why can every "
             "start in s..i be skipped?",
             "Reaching any j in that range from s leaves a tank ≥ 0; starting at j with 0 is "
             "no better, so it also runs dry by i."),
    ],
    interview="""
The trap is that greedy code is short, so it is tempting to write it and move
on. Interviewers are listening for the justification. Two sentences settle it:
*"sorting by end time is safe because the earliest finish leaves the most room"*,
or *"I tried to construct a case where a worse local choice pays off later and
could not"*. If neither is available, say so and switch to DP — that judgement
is itself the thing being tested.
""",
    invariant=_inv(
        "For jump game's furthest-reach loop: **after processing indices `0..i`, `reach` "
        "is the furthest index reachable by *any* sequence of jumps that only takes off "
        "from those indices.** Greedy is never behind — this is the stays-ahead argument "
        "written as an invariant.",
        "Before any index is processed, only index 0 is reachable (you start there), and "
        "`reach = 0` says exactly that.",
        "At index `i ≤ reach`, `i` is itself reachable, so every landing spot "
        "`i + 1 … i + a[i]` is reachable too — and `reach = max(reach, i + a[i])` records "
        "the furthest. Nothing else can extend the reach: a jump from an index not yet "
        "processed has not happened, and a jump from an unreachable index is impossible. "
        "If `i > reach`, then no strategy at all can stand on `i`, and the loop may stop.",
        "When the loop passes the last index with `i ≤ reach` throughout, the end is "
        "reachable. If it stops at an `i > reach`, *nothing* reaches `i`, so nothing reaches "
        "the end — and the invariant is what lets you say “nothing” rather than “greedy "
        "didn't”.",
        "Exchange arguments give a different kind of invariant: *the greedy choices so far "
        "extend to some optimal solution.* The swap step is what maintains it — replacing "
        "an optimal solution's choice with the greedy one keeps it optimal.",
    ),
    variants=[
        _var("Running extreme",
             "Keep the best value seen so far; evaluate today against it, then update.",
             "Buy/sell once, max difference, best sightseeing pair.",
             "O(n), O(1)",
             "Evaluate before updating, or you pair an element with itself."),
        _var("Furthest reach",
             "Track `reach = max(reach, i + a[i])`; fail when `i > reach`.",
             "Jump game, can-you-cover, video stitching's coverage.",
             "O(n), O(1)",
             "Check `i > reach` **before** using `a[i]`."),
        _var("Level-by-level reach",
             "Count a step only when `i` reaches the current window's end.",
             "Jump game II, minimum taps, minimum refuelling stops.",
             "O(n), O(1)",
             "Stop the loop at `n − 1`: arriving needs no more jumps."),
        _var("Sort by a key, then take",
             "Sort by end, by ratio, by cost — and take in order while it fits.",
             "Activity selection, fractional knapsack, cheapest-first purchases.",
             "O(n log n)",
             "The key *is* the proof. By start and by duration both have counterexamples."),
        _var("Sort by an exchange comparator",
             "Compare two adjacent items by which order is cheaper, and sort by that.",
             "Smith's rule (t/w), minimise lateness (by deadline), largest number.",
             "O(n log n)",
             "Compare ratios by cross-multiplying in `long`, never with doubles."),
        _var("Pair the extremes",
             "Sort, then match the largest with the smallest from both ends.",
             "Boats, two-city costs, assign cookies.",
             "O(n log n)",
             "The heaviest always leaves on this step; only its partner is optional."),
        _var("Prefix reset",
             "When the running total goes negative, abandon the prefix and restart.",
             "Gas station, Kadane, max subarray.",
             "O(n), O(1)",
             "The argument is that every start inside the abandoned prefix fails too."),
        _var("Two passes",
             "One left-to-right pass for one constraint, one right-to-left for the other, "
             "then combine.",
             "Candy, trapping rain water.",
             "O(n), O(n)",
             "A single pass sees only one neighbour's constraint."),
        _var("Heap with regret",
             "Take greedily, keep the choices in a heap, and undo the worst one when a "
             "constraint breaks.",
             "Course schedule III, furthest building, max events.",
             "O(n log n)",
             "The heap lives in stage 5; the idea is greedy that may change its mind."),
    ],
    rewrites=[
        _rw("Jump game: from DP to one pass",
            """
// O(n²) — for each index, look back at every earlier one
boolean[] can = new boolean[n];
can[0] = true;
for (int i = 1; i < n; i++)
    for (int j = 0; j < i && !can[i]; j++)
        if (can[j] && j + a[j] >= i) can[i] = true;
return can[n - 1];
""",
            """
// O(n) — the reachable indices are always a prefix
int reach = 0;
for (int i = 0; i < n; i++) {
    if (i > reach) return false;
    reach = Math.max(reach, i + a[i]);
}
return true;
""",
            "The whole `can[]` table collapses to one number, because the reachable set is always `0..reach`.",
            """
The DP is correct and uses nothing but the definition. Its waste is the table:
it stores n booleans that are, it turns out, always `true, true, …, true,
false, …`. If you can reach j, you can reach everything before it — you passed
over it on the way.

A set that is always a prefix is described by its length. So the table becomes
`reach`, the inner loop becomes one `max`, and the stays-ahead invariant above
is the proof that nothing was lost.

This is the most common shape of "greedy replaces DP": the DP table has a
structure so simple that one number summarises it.
"""),
        _rw("Job order: from n! to a sort",
            """
// O(n! · n) — try every order, keep the cheapest weighted completion time
long best = Long.MAX_VALUE;
for (int[] order : allPermutations(n)) {
    long t = 0, cost = 0;
    for (int j : order) { t += time[j]; cost += weight[j] * t; }
    best = Math.min(best, cost);
}
""",
            """
// O(n log n) — the exchange argument turns into a comparator
Integer[] idx = new Integer[n];
for (int i = 0; i < n; i++) idx[i] = i;
Arrays.sort(idx, (x, y) -> Long.compare((long) time[x] * weight[y],
                                        (long) time[y] * weight[x]));
long t = 0, cost = 0;
for (int j : idx) { t += time[j]; cost += (long) weight[j] * t; }
""",
            "The search over permutations becomes a sort whose comparator is the result of swapping two neighbours.",
            """
Take any order and look at two **adjacent** jobs x then y. Swapping them changes
nothing for any other job — everyone before is unaffected, everyone after
finishes at the same time. Only the two costs move: x-first costs
`w_y · t_x` extra for y, y-first costs `w_x · t_y` extra for x.

So x should go first exactly when `t_x · w_y < t_y · w_x`. Any order violating
that has an adjacent pair that can be swapped for free improvement — so the
optimal order is sorted by this comparator. That is Smith's rule, and it is the
template for every "in what order" greedy: **compare two neighbours, then sort.**

Cross-multiplying instead of dividing keeps the comparison exact, and `long`
keeps it from overflowing.
"""),
        _rw("Gas station: from every start to one pass",
            """
// O(n²) — simulate a full lap from every start
for (int s = 0; s < n; s++) {
    long tank = 0; int k = 0;
    for (; k < n; k++) {
        tank += gas[(s + k) % n] - cost[(s + k) % n];
        if (tank < 0) break;
    }
    if (k == n) return s;
}
return -1;
""",
            """
// O(n) — a failed stretch rules out every start inside it
long total = 0, tank = 0; int start = 0;
for (int i = 0; i < n; i++) {
    long d = gas[i] - cost[i];
    total += d; tank += d;
    if (tank < 0) { start = i + 1; tank = 0; }
}
return total < 0 ? -1 : start;
""",
            "The restart from every index becomes a restart only after the index where the tank went negative.",
            """
Suppose a lap starting at s runs dry at i. Every start j between s and i fails
at or before i as well: arriving at j from s you had a tank ≥ 0, so starting
at j with an empty tank is never better. One failure retires the whole stretch
`s..i`, so the next candidate is `i + 1` — and no index is ever tried twice.

Whether *any* start works is a separate, global fact: the lap is possible iff
total gas ≥ total cost. If it is, the last surviving start is the answer.
"""),
    ],
    internals="""
### When is greedy provably right?

There is a precise answer for a large family of problems. A **matroid** is a set
system where (1) subsets of a valid set are valid, and (2) if one valid set is
larger than another, some element of the larger can be added to the smaller
while keeping it valid — the **exchange property**. For any matroid, "sort by
weight, add each element if the set stays valid" finds a maximum-weight valid
set. Kruskal's MST is this theorem applied to forests.

You will never be asked to name a matroid in an interview. But the exchange
property is exactly what your exchange argument checks, and knowing it exists
tells you greedy correctness is not luck — it is a structural property of the
constraints. When the constraints lack it (0/1 knapsack's weight limit does),
greedy fails, and the counterexample is always a case where two small items beat
one large one.

### The exchange argument, as a checklist

1. Let `G` be the greedy solution and `O` any optimal one.
2. Find the **first** place they differ.
3. Modify `O` to agree with `G` there, and show the cost does not increase.
4. Repeat: `O` now agrees with `G` on a longer prefix and is still optimal.
   Eventually `O = G`.

Step 3 is the only real work, and for ordering problems it is always the
adjacent swap in the Smith's-rule rewrite above.

### Test before you trust

A greedy rule that is wrong usually passes the examples. The professional habit
is a **stress test**: a brute force that is obviously correct (try every subset
or every order, n ≤ 8), a random input generator, and a loop that runs both
until they disagree. Ten minutes of setup, and it finds the counterexample you
could not think of — often in under a second.

```java
Random rng = new Random(1);
for (int t = 0; t < 100_000; t++) {
    int[] a = randomArray(rng, 1 + rng.nextInt(7), 10);
    if (greedy(a) != brute(a)) { System.out.println(Arrays.toString(a)); break; }
}
```
""",
    build_it="""
### Prove it, then try to break it

**1. Three rules for activity selection.** Implement "sort by start", "sort by
duration" and "sort by end". Write a brute force over all subsets (n ≤ 10) and
stress-test all three. Keep the smallest counterexample for each wrong rule and
explain it in one sentence.

**2. Greedy coin change against DP.** Write both. Stress-test on random coin
systems of 3 coins in 1..10 (always including 1). How often is greedy wrong? Now
fix the system to {1, 5, 10, 25} and confirm it never is — that system is
*canonical*.

**3. Smith's rule.** Write the brute force over permutations (n ≤ 7) and the
comparator sort. Then replace the cross-multiplication with a `double` division
and find an input where it breaks (hint: large equal ratios).

**4. Jump game, three ways.** The O(n²) DP, the furthest reach, and a BFS over
indices. Stress-test all three against each other.

**5. Write the invariant** for gas station in the four-part form (statement,
established, maintained, at exit). The "maintained" part is the claim that a
failed stretch contains no valid start; make it rigorous.
""",
    rungs=[
        _rung("Warm up", "A sort order, a local rule, and the exchange argument that joins them.",
              ["activity-selection-small"],
              {"activity-selection-small": "The canonical greedy. Produce the counterexamples that kill sorting by start time and by duration — that is how you check a rule you just invented."}),
        _rung("Core", "One pass, one running value, one proof.",
              ["best-time-buy-sell", "jump-game", "boats-to-save-people", "gas-station-start"],
              {"best-time-buy-sell": "Say the exchange argument out loud before coding. The code is four lines; the reasoning is the exercise.",
               "jump-game": "Stays-ahead. Track the furthest reachable index and fail the moment you stand past it.",
               "boats-to-save-people": "Sort, then converge from both ends. The heaviest person departs on this boat either way — putting `j--` inside the `if` is the bug.",
               "gas-station-start": "A reset, with a real argument for why the abandoned prefix was already doomed. Same shape as Kadane."}),
        _rung("Variations", "A rule over a derived quantity, and a rule that is simply wrong.",
              ["fractional-knapsack", "greedy-coin-change"],
              {"fractional-knapsack": "The sort key is value *per unit weight*, not value. Then say which property you lose when the items stop being divisible — that is the 0/1 knapsack boundary.",
               "greedy-coin-change": "The most useful negative example in the unit: on coins {1,3,4} greedy is wrong for 6, and on {3,4} it gets stuck where an answer exists. Nothing is buggy; the rule is false."}),
        _rung("Stretch", "Greedy where the counting is the subtle part.",
              ["jump-game-ii"],
              {"jump-game-ii": "Count a jump only when the current reach is exhausted, and stop before the last index."}),
    ],
    next_up="""
Intervals are the family where “sort, then be greedy” is provably right — and
where the sweep from the prefix-sums unit comes back.
""",
)


# --- Unit 15 — Intervals -----------------------------------------------------

_unit(
    "intervals", "Intervals", "📅", _S3,
    "Sort by the right endpoint, then sweep.",
    weight=3,
    prereqs=["sorting", "greedy"],
    why="""
Meetings, bookings, ranges, flights, free time — an enormous number of practical
problems are pairs of numbers with an overlap rule. Almost all of them are
solved by one decision (**sort by start, or sort by end?**) followed by a single
pass, and getting that decision right is the difference between three lines and
an hour.

The family also contains the cleanest example of the sweep from the prefix-sums
unit: turning each interval into a `+1` at its start and a `−1` at its end
answers every "how many at once" question without ever comparing intervals to
one another.
""",
    model="""
### The one decision

| Question | Sort by | Then |
| --- | --- | --- |
| Merge overlapping | **start** | Extend the current interval, or emit and restart |
| Maximum non-overlapping / fewest removals | **end** | Keep if it starts after the last kept end |
| How many overlap at once | either — use a **sweep** | `+1` at start, `−1` at end, in time order |
| Insert one interval | already sorted | Three phases: before, merged, after |
| Intersect two sorted lists | already sorted | Two pointers |

Merging wants earliest **start** because you build left to right. Scheduling
wants earliest **end** because finishing early leaves the most room. These are
different questions and the wrong sort is the single most common interval bug.

### Merging

```java
Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
List<int[]> out = new ArrayList<>();
for (int[] cur : iv) {
    int[] last = out.isEmpty() ? null : out.get(out.size() - 1);
    if (last != null && cur[0] <= last[1]) last[1] = Math.max(last[1], cur[1]);
    else out.add(cur.clone());
}
```

`Math.max` matters: the current interval may be entirely inside the previous
one, and overwriting the end would shrink it.

### The overlap test

Two intervals `[a1, a2]` and `[b1, b2]` overlap iff `a1 <= b2 && b1 <= a2`.
Whether touching endpoints count is a specification question — `[1,2]` and
`[2,3]`. Decide it from the problem statement (a meeting ending at 2 usually
does *not* clash with one starting at 2) and keep the comparison consistent.

### The sweep

```java
// minimum meeting rooms: the maximum number concurrently active
int[] starts = ..., ends = ...;
Arrays.sort(starts); Arrays.sort(ends);
int rooms = 0, best = 0, j = 0;
for (int i = 0; i < n; i++) {
    while (j < n && ends[j] <= starts[i]) { rooms--; j++; }   // frees first
    rooms++;
    best = Math.max(best, rooms);
}
```

Process an ending **before** a start at the same instant, or a room is counted
twice. The heap version — a min-heap of end times, polled while the earliest end
is ≤ the current start — is equivalent and often easier to explain.

### Two sorted lists: intersect with two pointers

The intersection of `[a1,a2]` and `[b1,b2]` is
`[max(a1,b1), min(a2,b2)]`, valid when the start is ≤ the end. Then advance
whichever interval **ends first**, because it can have no further intersections.

### Where greedy stops: weighted intervals

Give every interval a **weight** and ask for the maximum total weight of
non-overlapping intervals, and "sort by end, keep greedily" is simply wrong: one
long interval worth 100 beats three short ones worth 1 each, and nothing about
end times can see that.

The fix keeps the sort and replaces the greedy choice with a DP over it. Sort by
end; let `best[i]` be the best total using only the first i intervals. Interval
i is either skipped (`best[i-1]`) or taken, together with the best answer among
intervals that end before it starts — and since the ends are **sorted**, that
predecessor is one binary search away:

```java
// iv sorted by end; ends[i] = iv[i].end
best[0] = 0;
for (int i = 1; i <= n; i++) {
    int[] cur = iv[i - 1];
    int j = upperBound(ends, cur.start);          // # intervals ending <= start
    best[i] = Math.max(best[i - 1], best[j] + cur.weight);
}
```

O(n log n), and every piece of it is from this stage: the sort, the binary
search, and the recognition that a local rule has stopped being safe.

### Total covered length, and subtraction

Two more questions reduce to merging. The **length of the union** is the sum of
the merged blocks' lengths — merge, then add. **Removing** a range `[x, y)`
from a sorted list is the insert-interval three phases with one change: an
overlapping interval is *trimmed* to the part outside `[x, y)`, which can leave
zero, one or two pieces.
""",
    signals=[
        _sig("“merge overlapping”", "Sort by start",
             "Build left to right, extending with `max`."),
        _sig("“maximum meetings”, “fewest removals”", "Sort by end",
             "Earliest finish leaves the most room."),
        _sig("“minimum rooms / platforms / servers”", "Sweep or a min-heap of end times",
             "The answer is the peak concurrency."),
        _sig("“insert into a sorted list of intervals”", "Three phases",
             "Everything before, the merged block, everything after."),
        _sig("“intersection of two interval lists”", "Two pointers",
             "Advance whichever ends first."),
        _sig("“free time”, “gaps”", "Merge everything, then read the gaps",
             "The complement of the merged set."),
    ],
    skeletons=[
        _sk("Merge overlapping",
            "The base operation almost everything else builds on.",
            """
Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
List<int[]> out = new ArrayList<>();
for (int[] cur : iv) {
    if (!out.isEmpty() && cur[0] <= out.get(out.size() - 1)[1])
        out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
    else out.add(cur.clone());
}
""",
            "`max` on the end — the new interval may be nested inside the last."),
        _sk("Insert one interval",
            "Into an already-sorted, non-overlapping list.",
            """
int i = 0, n = iv.length;
while (i < n && iv[i][1] < ni[0]) out.add(iv[i++]);          // strictly before
while (i < n && iv[i][0] <= ni[1]) {                         // overlapping
    ni[0] = Math.min(ni[0], iv[i][0]);
    ni[1] = Math.max(ni[1], iv[i][1]);
    i++;
}
out.add(ni);
while (i < n) out.add(iv[i++]);                              // strictly after
""",
            "Three loops, each with a clear job. Do not try to fuse them."),
        _sk("Peak concurrency (heap)",
            "Minimum meeting rooms, maximum simultaneous anything.",
            """
Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
PriorityQueue<Integer> ends = new PriorityQueue<>();
for (int[] v : iv) {
    if (!ends.isEmpty() && ends.peek() <= v[0]) ends.poll();  // a room freed
    ends.offer(v[1]);
}
int rooms = ends.size();
""",
            "The heap size is the number of rooms in use; its peak is the answer. Only `offer`, `peek` and `poll` are needed here — the heaps unit (stage 5) explains why each is cheap."),
        _sk("Intersect two sorted lists",
            "Overlap of two schedules.",
            """
int i = 0, j = 0;
while (i < a.length && j < b.length) {
    int lo = Math.max(a[i][0], b[j][0]), hi = Math.min(a[i][1], b[j][1]);
    if (lo <= hi) out.add(new int[]{ lo, hi });
    if (a[i][1] < b[j][1]) i++; else j++;         // advance the earlier end
}
""",
            "Advancing the earlier end is what makes the single pass sufficient."),
    ],
    costs=[
        _cost("Sort", "O(n log n)", "O(n)", "Dominates every interval algorithm."),
        _cost("Merge / greedy scan after sorting", "O(n)", "O(n)", "One pass."),
        _cost("Sweep of ±1 events", "O(n log n)", "O(n)", "Sorting the events."),
        _cost("Heap of end times", "O(n log n)", "O(n)", "Same bound, easier to explain."),
        _cost("Insert into a sorted list", "O(n)", "O(n)", "No sort needed — it is already ordered."),
    ],
    pitfalls=[
        _pit("Maximum non-overlapping selection is too small",
             "The intervals were sorted by start time.",
             "Sort by end. This is the single most common interval mistake."),
        _pit("A merged interval is shorter than one it contains",
             "The end was overwritten rather than maximised.",
             "`last[1] = Math.max(last[1], cur[1])` — nested intervals are real."),
        _pit("One room too many",
             "A start was processed before an end at the same timestamp.",
             "Release first: use `ends[j] <= starts[i]` in the sweep."),
        _pit("Touching intervals are treated inconsistently",
             "`[1,2]` and `[2,3]` were merged in one place and separated in another.",
             "Decide from the statement whether contact counts, and use the same comparison "
             "everywhere."),
        _pit("Sorting an already-sorted input",
             "An extra O(n log n) where the list was given in order.",
             "Insert-into-sorted is O(n); check what the input guarantees."),
        _pit("The sort comparator overflows",
             "`(a, b) -> a[0] - b[0]` with coordinates near `Integer.MAX_VALUE`.",
             "`Integer.compare(a[0], b[0])`."),
        _pit("Weighted scheduling answer is too small",
             "The greedy by end time was used, or the predecessor search excluded intervals "
             "that end exactly when the current one starts.",
             "DP over intervals sorted by end, with `upperBound(ends, start)` for the "
             "predecessor count."),
        _pit("Subtracting a range deletes an interval that should have been split",
             "Only the left or the right remainder of an overlapping interval was kept.",
             "An interval overlapping `[x, y)` can leave a piece before x **and** a piece "
             "after y. Emit each if it is non-empty."),
        _pit("The ±1 sweep counts back-to-back meetings as overlapping",
             "Events at the same time were sorted with `+1` before `−1`.",
             "Tie-break by delta ascending so ends (−1) are processed first."),
    ],
    lessons=["intervals", "sorting", "heap"],
    checks=[
        _chk("Merging wants one sort order and scheduling wants another. Which and why?",
             "Merging sorts by **start**, because it builds the result left to right. "
             "Maximum non-overlapping scheduling sorts by **end**, because finishing "
             "earliest leaves the most room for what follows."),
        _chk("Write the overlap test for [a1,a2] and [b1,b2].",
             "`a1 <= b2 && b1 <= a2`. Whether the endpoints touching counts as overlap is a "
             "specification decision and must be applied consistently."),
        _chk("Why must an end event be processed before a start at the same time?",
             "Otherwise a resource that is being released at that instant is not yet "
             "available, and the peak count is one too high."),
        _chk("How do you compute free time across many busy intervals?",
             "Merge all the busy intervals, then emit the gaps between consecutive merged "
             "blocks."),
        _chk("Why is merging linear after the sort — why only compare with the last block?",
             "Blocks before the last one ended before the last block began, and every future "
             "interval starts at or after the current one. So nothing still to come can reach "
             "an earlier block."),
        _chk("Maximum total weight of non-overlapping intervals: why does sort-by-end greedy "
             "fail, and what replaces it?",
             "One heavy interval can beat several light ones that finish earlier. Sort by "
             "end and DP: `best[i] = max(best[i−1], w_i + best[p(i)])`, where p(i) is found "
             "by binary search over the sorted ends."),
        _chk("Minimum arrows to burst balloons: why sort by end and shoot at the end?",
             "The balloon ending first must be hit by some arrow at or before its end; "
             "shooting exactly at its end hits it and as many later-starting balloons as any "
             "position could."),
        _chk("How do you check a new booking against a calendar in O(log n)?",
             "Keep bookings in a `TreeMap<start, end>`. The new one clashes iff the floor "
             "entry ends after the new start, or the ceiling entry starts before the new end."),
    ],
    interview="""
Interval questions are a gift when you state the sort rule first: *"merging, so
I sort by start"* or *"maximum non-overlapping, so I sort by end — earliest
finish leaves the most room"*. Then raise the endpoint question before the
interviewer does — does a meeting ending at 2 clash with one starting at 2? —
because it is the ambiguity the test cases are built around.

The common follow-up is to add weights. Say "then greedy fails — sort by end,
binary-search each interval's predecessor, and DP" before being asked; it shows
you know where the technique's edge is.
""",
    invariant=_inv(
        "While merging intervals sorted by start: **`out` is a sorted list of disjoint "
        "blocks whose union is exactly the union of the intervals processed so far — and "
        "only the last block can overlap anything still to come.**",
        "Before the first interval, `out` is empty and nothing has been processed; the "
        "union of nothing is empty.",
        "The next interval `cur` starts at or after every processed start. So it cannot "
        "reach back past the last block's start into an earlier block — those all ended "
        "before the last block began. Either `cur` overlaps the last block, and extending "
        "that block's end to `max(end, cur.end)` covers exactly the new union; or it starts "
        "after the last block's end, and appending it as a new block keeps the list sorted "
        "and disjoint.",
        "After the last interval, `out` covers exactly the union of all of them, in sorted "
        "disjoint blocks — which is the answer, and also the input every “free time”, "
        "“covered length” and “subtract a range” question wants.",
        "The phrase *only the last block can overlap* is what makes the pass linear. It "
        "holds only because of the sort by start — sort by end and it is false.",
    ),
    variants=[
        _var("Merge",
             "Sort by start; extend the last block or start a new one.",
             "Merge overlapping, union length, free time.",
             "O(n log n)",
             "`max` on the end — the new interval may be nested inside the last."),
        _var("Insert into sorted",
             "Three loops: strictly before, overlapping (grow the new one), strictly after.",
             "Insert interval, subtract a range, add a booking.",
             "O(n), no sort",
             "The input is already sorted — re-sorting is a wasted O(n log n)."),
        _var("Keep the most (sort by end)",
             "Keep an interval if it starts at or after the last kept end.",
             "Max non-overlapping, fewest removals.",
             "O(n log n)",
             "Removals = n − kept. Sorting by start is the classic wrong answer."),
        _var("Stab with points",
             "Sort by end; shoot at the current end, skip everything it pierces.",
             "Minimum arrows, fewest points covering all intervals.",
             "O(n log n)",
             "Touching counts as pierced here — `start <= arrow`, not `<`."),
        _var("Peak concurrency",
             "±1 events sorted by time (ends before starts on ties), or a min-heap of ends.",
             "Meeting rooms, platforms, busiest moment, car pooling.",
             "O(n log n)",
             "At equal timestamps, release before allocate."),
        _var("Two lists intersect",
             "Two pointers; emit `[max start, min end]`; advance the earlier end.",
             "Interval list intersections, common free time.",
             "O(n + m)",
             "Advance by end, not by start."),
        _var("Greedy coverage",
             "Sort by start; among intervals starting within the covered prefix, take the "
             "one reaching furthest.",
             "Video stitching, minimum taps, jump game II in disguise.",
             "O(n log n)",
             "A gap (no interval starts inside the covered prefix) means −1."),
        _var("Online (a sorted map)",
             "Keep intervals in a `TreeMap` by start; check `floorEntry` and `ceilingEntry`.",
             "My calendar, range modules, disjoint intervals from a stream.",
             "O(log n) per operation",
             "Both neighbours must be checked — the previous one can reach past the new start."),
        _var("Weighted (DP)",
             "Sort by end; `best[i] = max(best[i-1], w_i + best[pred(i)])`, pred by binary search.",
             "Weighted job scheduling, max profit from non-overlapping jobs.",
             "O(n log n)",
             "The predecessor search uses **ends ≤ start** — upper bound, not lower."),
    ],
    rewrites=[
        _rw("Do any two meetings overlap?",
            """
// O(n²) — compare every pair
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (iv[i][0] < iv[j][1] && iv[j][0] < iv[i][1]) return false;
return true;
""",
            """
// O(n log n) — after sorting, only neighbours can clash
Arrays.sort(iv, Comparator.comparingInt(x -> x[0]));
for (int i = 1; i < n; i++)
    if (iv[i][0] < iv[i - 1][1]) return false;
return true;
""",
            "The all-pairs check becomes a sort by start and one comparison per neighbour.",
            """
Once intervals are sorted by start, suppose `i < j` overlap but no adjacent pair
does. Interval `i + 1` starts at or after `i`, and does not overlap `i`, so it
starts at or after `i`'s end — and so does everything after it, including `j`.
Then `j` cannot overlap `i`. Contradiction: **some overlap implies an adjacent
overlap**.

So only n − 1 pairs need checking. The same argument, generalised, is why merge
only ever compares with the last block.
"""),
        _rw("Peak concurrency: a timeline, or events",
            """
// O(n · T) time, O(T) memory — mark every unit of time
int[] busy = new int[MAX_TIME + 1];
for (int[] v : iv)
    for (int t = v[0]; t < v[1]; t++) busy[t]++;
int peak = Arrays.stream(busy).max().getAsInt();
""",
            """
// O(n log n) — only the 2n endpoints matter
int[][] ev = new int[2 * n][];
for (int i = 0; i < n; i++) {
    ev[2 * i]     = new int[]{ iv[i][0], +1 };
    ev[2 * i + 1] = new int[]{ iv[i][1], -1 };
}
Arrays.sort(ev, (x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0])
                                        : Integer.compare(x[1], y[1]));  // -1 first
int cur = 0, peak = 0;
for (int[] e : ev) peak = Math.max(peak, cur += e[1]);
""",
            "Marking every time unit becomes sorting the 2n endpoints — the count only changes there.",
            """
Between two consecutive endpoints, nothing starts or ends, so the number of
active intervals is constant. The timeline array spends most of its work
re-reading that constant.

Sorting the events visits only the moments where the count changes, which makes
the cost independent of the time range — essential when times go to 10⁹. The
difference-array version (`+1` at start, `−1` at end, prefix-sum) is the middle
ground: O(n + T), fine when T is small.

The tie rule — `−1` before `+1` at the same time — encodes "a meeting ending at
2 does not clash with one starting at 2". Flip it and back-to-back meetings
count as overlapping.
"""),
        _rw("Insert without re-sorting",
            """
// O(n log n) — append, then merge everything again
List<int[]> all = new ArrayList<>(Arrays.asList(iv));
all.add(ni);
all.sort(Comparator.comparingInt(x -> x[0]));
return merge(all);
""",
            """
// O(n) — the list was already sorted and disjoint
int i = 0;
while (i < n && iv[i][1] < ni[0]) out.add(iv[i++]);
while (i < n && iv[i][0] <= ni[1]) {
    ni[0] = Math.min(ni[0], iv[i][0]);
    ni[1] = Math.max(ni[1], iv[i][1]);
    i++;
}
out.add(ni);
while (i < n) out.add(iv[i++]);
""",
            "Re-sort-and-merge becomes three loops that exploit the order the input already has.",
            """
The re-sort discards a guarantee the input came with: sorted and disjoint. With
it, the intervals split into exactly three contiguous groups — entirely before
the new one, touching it, entirely after — and each group is one loop.

Only the middle group changes, and it collapses into the new interval by `min`
on the start and `max` on the end. Every interval is visited once, so the whole
insert is O(n), and there is no merge pass at all.
"""),
    ],
    build_it="""
### The interval toolkit, from an empty file

Represent an interval as `int[]{start, end}`, half-open `[start, end)`, and keep
that convention for every function — then touching intervals do not overlap and
the length is simply `end − start`.

**1. `overlaps(a, b)`** and **`merge(list)`**. Test merge against a brute force
that paints a boolean timeline (times 0..30) and reads the blocks back.

**2. `insert(sorted, x)`** and **`subtract(sorted, x)`** — the three phases,
the second trimming instead of growing. Test both against the timeline painter.

**3. Peak concurrency three ways**: the ±1 sweep, the heap of ends, and the
timeline array. Stress-test all three against each other on random inputs with
many shared endpoints — that is where the tie rule matters.

**4. `maxNonOverlapping` by end**, and a brute force over subsets. Then add
weights and watch the greedy fail the stress test.

**5. Weighted scheduling** with the DP and a binary-searched predecessor. The
brute force from step 4 is its oracle. Get the predecessor boundary right on
intervals that touch — `[1, 3)` and `[3, 5)` are compatible.
""",
    rungs=[
        _rung("Warm up", "The overlap test, applied once.",
              ["can-attend-meetings"],
              {"can-attend-meetings": "Sort by start and compare neighbours. Decide what touching endpoints mean before you code."}),
        _rung("Core", "Merging, and the two-pointer intersection.",
              ["merge-intervals", "insert-interval", "interval-intersections"],
              {"merge-intervals": "The base operation. `Math.max` on the end, because intervals nest.",
               "insert-interval": "Three phases. Trying to write it as one loop is how this becomes hard.",
               "interval-intersections": "Two pointers: emit `[max start, min end]` when it is non-empty, then advance whichever interval ends first — it can meet nothing else."}),
        _rung("Variations", "Sweeps and end-time greed.",
              ["min-meeting-rooms", "car-pooling", "non-overlapping-remove", "min-arrows-balloons"],
              {"min-meeting-rooms": "Solve it twice — a ±1 sweep and a heap of end times — and notice they are the same algorithm.",
               "non-overlapping-remove": "Sort by end and keep greedily; the removals are everything you did not keep.",
               "car-pooling": "Peak concurrency weighted by passengers: `+num` at pickup, `−num` at drop-off, drop-offs first at equal positions.",
               "min-arrows-balloons": "Sort by end and shoot at the first balloon's end; every balloon starting at or before it bursts. Touching counts here — `<=`, not `<`."}),
        _rung("Stretch", "Merge first, then read the complement.",
              ["employee-free-time"],
              {"employee-free-time": "Flatten every schedule, merge, and emit the gaps. A heap-based k-way merge avoids sorting everything."}),
    ],
    next_up="""
Order is done. The next stage looks inside the numbers themselves — their
factors, their remainders, their bits — and at grids, where the index
arithmetic is the whole problem.
""",
)
