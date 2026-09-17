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

It opens with **recursion**, because the sorts worth understanding are
recursive: merge sort splits and merges, quickselect partitions and recurses
into one side. It closes with **greedy** and **intervals** — the families where
"sort, then take the best local move" is provably right, and where you learn
to check that it is.
""")


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
    ],
    interview="""
Interviewers probe recursion by asking for the complexity and then for the
iterative version. Have both ready: the recurrence that gives the time bound,
and the observation that depth is memory. And when a recursive solution is
exponential, say *why* — "the same subproblem appears on both branches, so I
will memoise" is the sentence that turns a rejected answer into an accepted one.
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
    ],
    interview="""
The sorting question in an interview is usually "you sorted; did you need to?".
Have the three alternatives ready: counting sort when the range is small, a heap
when you want the top k, quickselect when you want exactly the k-th — and be
able to *write* quickselect, because "the k-th largest in O(n)" is a common
follow-up. When a problem asks to count pairs that are out of order, say
"merge sort, counting at the merge" before anything else.
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
    ],
    interview="""
The trap is that greedy code is short, so it is tempting to write it and move
on. Interviewers are listening for the justification. Two sentences settle it:
*"sorting by end time is safe because the earliest finish leaves the most room"*,
or *"I tried to construct a case where a worse local choice pays off later and
could not"*. If neither is available, say so and switch to DP — that judgement
is itself the thing being tested.
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
    ],
    interview="""
Interval questions are a gift when you state the sort rule first: *"merging, so
I sort by start"* or *"maximum non-overlapping, so I sort by end — earliest
finish leaves the most room"*. Then raise the endpoint question before the
interviewer does — does a meeting ending at 2 clash with one starting at 2? —
because it is the ambiguity the test cases are built around.
""",
    rungs=[
        _rung("Warm up", "The overlap test, applied once.",
              ["can-attend-meetings"],
              {"can-attend-meetings": "Sort by start and compare neighbours. Decide what touching endpoints mean before you code."}),
        _rung("Core", "Merging, and the two-pointer intersection.",
              ["merge-intervals", "insert-interval", "interval-intersections"],
              {"merge-intervals": "The base operation. `Math.max` on the end, because intervals nest.",
               "insert-interval": "Three phases. Trying to write it as one loop is how this becomes hard."}),
        _rung("Variations", "Sweeps and end-time greed.",
              ["min-meeting-rooms", "car-pooling", "non-overlapping-remove", "min-arrows-balloons"],
              {"min-meeting-rooms": "Solve it twice — a ±1 sweep and a heap of end times — and notice they are the same algorithm.",
               "non-overlapping-remove": "Sort by end and keep greedily; the removals are everything you did not keep."}),
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
