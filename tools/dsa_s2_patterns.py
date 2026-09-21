# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 2 — Cost, and the four patterns that beat it.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# This is the hinge of the whole curriculum. Stage 1 wrote correct code without
# ever asking what it cost; from here on, "it works" is only half an answer.
# The stage opens with Big-O because the four techniques that follow — hashing,
# two pointers, sliding window, prefix sums — are all answers to the SAME
# question: how do I stop re-reading data I have already seen?
#
# That framing is deliberate. Taught as four separate tricks they are four
# things to memorise; taught as four ways to reuse work they are one idea, and
# the signal table in each unit is how you pick between them.
# ---------------------------------------------------------------------------

_S2 = _stage(
    "patterns", "Cost & Core Patterns", "⚡",
    "Stop re-reading what you have already seen.",
    """
Every technique in this stage removes a nested loop, and each removes it a
different way:

| Pattern | The work it reuses |
| --- | --- |
| **Cost** | Nothing — it is how you decide *which* of the others you can afford |
| **Hashing** | *“Have I seen this value?”* — answered in O(1) instead of a scan |
| **Two pointers** | Sorted order, so neither pointer ever needs to go back |
| **Sliding window** | The previous window's answer, adjusted at both ends |
| **Prefix sums** | Every range sum, precomputed once |
| **Strings** | All four of the above, with a `char` costume and a copying trap |

Learn to recognise which one a prompt is asking for and the Medium tier stops
looking like a different sport from the Easy tier. That recognition is the
skill; the code is four short templates you will have memorised by the end of
the stage.

**The hard part is not the templates, it is telling them apart.** Six units that
all take an array and return a number, and prompts that differ by one word:
*longest* versus *shortest*, *at most k* versus *exactly k*, *subarray* versus
*subsequence*. The routing table below is that distinction written down — read
it before the units, and again after.
""",
    router=[
        _route("“does this value appear / appear twice / have a partner”",
               "hashing",
               "Membership and counting. Anything answerable by a lookup rather than a "
               "scan.",
               "“does this *range* sum to …” is prefix sums + a map, not a "
               "plain set."),
        _route("“find a pair that sums to / differs by a target”",
               "hashing",
               "One lookup for the complement. O(n) time, O(n) space, and the original "
               "indices survive.",
               "If the array is **sorted**, or O(1) space is demanded, it is two pointers "
               "instead."),
        _route("The input is **sorted**, and the answer is a pair or a triple",
               "two-pointers",
               "Sorted order lets one comparison retire a whole row of the pair table. "
               "O(1) space.",
               "Unsorted input where the answer is the original indices — sorting "
               "destroys them, so hash it."),
        _route("“in place”, “without extra space”, “remove / "
               "partition / reverse”",
               "two-pointers",
               "A read pointer and a write pointer, moving the same way. Nothing is "
               "allocated.",
               ""),
        _route("“contiguous subarray / substring”, **longest** or **shortest**",
               "sliding-window",
               "One window whose left edge never rewinds. The word *contiguous* is the "
               "signal.",
               "**Subsequence** is not contiguous — that is dynamic programming, four "
               "stages away."),
        _route("“at most k …” in a contiguous run",
               "sliding-window",
               "Validity survives shrinking, which is exactly what the window's invariant "
               "needs.",
               "“**exactly** k” is not a window: run *at most k* twice and "
               "subtract."),
        _route("“every window of size k”",
               "sliding-window",
               "Fixed width, so there is no shrink loop — add the entrant, remove the "
               "leaver.",
               "If the summary is a max or min rather than a sum, it needs a monotonic "
               "deque (queues unit)."),
        _route("“how many subarrays sum to k”, with negatives allowed",
               "prefix-sums",
               "Every subarray is a *pair of prefixes*, so a map counts them without "
               "enumerating them. Negatives are fine.",
               "All-positive values and a *longest/shortest* question is a window, which "
               "is O(1) space."),
        _route("“many range queries on an array that never changes”",
               "prefix-sums",
               "Pay O(n) once, answer each query by one subtraction.",
               "If the array **is** updated between queries, this unit cannot help — "
               "that is a Fenwick tree, in the optional stage."),
        _route("“add v to every index in [l, r]”, repeated",
               "prefix-sums",
               "A difference array: mark the two edges, prefix-sum once at the end.",
               ""),
        _route("“maximum simultaneous …”, overlapping intervals",
               "prefix-sums",
               "A ±1 sweep over the endpoints. The array is a timeline.",
               "Merging or scheduling the intervals themselves is the `intervals` unit, "
               "next stage."),
        _route("Anagrams, palindromes, character counts, common prefixes",
               "strings",
               "Array techniques with a `char` costume — plus the Java-specific traps "
               "around copying.",
               ""),
        _route("“will this pass at n = …”, “what is the complexity”",
               "complexity",
               "Read the constraint first: it tells you which of the other five shapes is "
               "affordable before you write anything.",
               ""),
    ])


# --- Unit 5 — Complexity -----------------------------------------------------

_unit(
    "complexity", "Cost: Big-O in Practice", "⏱️", _S2,
    "Count the work before you write it, and know when n² is fine.",
    weight=2,
    prereqs=["arrays-first-pass"],
    why="""
Every problem you have solved so far was small enough that nothing you wrote
could be too slow. That ends here. From this unit on, the interesting question
is never *"does it work?"* but *"does it work at n = 200,000?"* — and the answer
has to be decidable **before** you type, because a wrong choice of approach is
not something you can patch afterwards.

Big-O gets taught as a maths topic. It is really a *budgeting* topic: you are
given a constraint, you have roughly 10⁸ simple operations to spend, and the
constraint tells you which shapes of solution fit.
""",
    model="""
### Read the constraint, pick the shape

A rough but reliable table. Take the largest `n` in the constraints and read
off what you can afford:

| n up to | Budget allows | Typical approach |
| --- | --- | --- |
| 10–12 | O(n!) | Permutations, brute force |
| 20–25 | O(2ⁿ) | Subsets, bitmask DP |
| 500 | O(n³) | Triple loop, Floyd–Warshall |
| 5,000 | O(n²) | Every pair, 2-D DP |
| 10⁵–10⁶ | O(n log n) | Sort, heap, binary search |
| 10⁶–10⁷ | O(n) | One pass, hashing, two pointers |
| 10⁹+ | O(log n) or O(1) | Binary search on the answer, a formula |

Read it backwards too, and it becomes a *hint*: a constraint of `n ≤ 20` is the
setter telling you an exponential search is intended. A constraint of `n ≤ 10⁵`
is them telling you O(n²) will time out.

### Counting the work

Big-O keeps the fastest-growing term and drops constants, because at large n
nothing else matters:

- **Sequential** code adds: O(n) then O(n) is O(n). Two passes are still linear.
- **Nested** code multiplies: a loop inside a loop over the same data is O(n²).
- **Halving** is logarithmic: each step throws away half the remaining input, so
  it finishes in about log₂ n steps — 20 for a million, 30 for a billion.
- **A call inside a loop counts.** `list.contains(x)` inside a `for` is O(n²),
  and it is the most common accidental quadratic there is, because the nesting
  is hidden behind a method name.

### Amortized cost: price the loop, not the step

Counting by nesting has a blind spot, and it is the one that makes people
"optimise" code that was already linear:

```java
Deque<Integer> st = new ArrayDeque<>();
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && a[st.peek()] < a[i]) st.pop();   // a loop, inside a loop
    st.push(i);
}
```

Two nested loops, so O(n²)? No — **O(n)**. The inner `while` can only pop what
some earlier iteration pushed, and each index is pushed once. The right question
is not *"how many steps can one iteration take?"* (n, in the worst case) but
*"how many steps can the whole loop take?"* (2n: one push and one pop per index).
Divide by n and each iteration costs **O(1) amortized**.

That is the whole idea:

> **Amortized cost = total work over a sequence of operations ÷ the number of
> operations.** It is a worst case, not an average — no lucky input is assumed.

The accounting argument is always the same shape: find a quantity that each
operation pays into, and show that every expensive step spends what an earlier
cheap step deposited. For the stack, the deposit is the push.

You have already relied on this without naming it:

| Where | Why one step looks expensive | Why the sequence is cheap |
| --- | --- | --- |
| `ArrayList.add` | Occasionally copies the whole array | Doubling: n adds copy 1 + 2 + 4 + … < 2n elements, so **O(1) amortized** |
| Two pointers | The inner pointer can jump far | Neither pointer ever moves backwards — 2n moves total |
| Sliding window | One shrink can empty the window | Every element enters and leaves once |
| Monotonic stack | One iteration can pop everything | Each index is pushed once and popped once |
| Union-find | One `find` can walk a long chain | Path compression flattens it; the sequence is near-constant per call |

### Amortized is not average, and not per-call

Three different claims, often muddled:

- **Worst case per call** — `ArrayList.add` is O(n) on the call that resizes.
  True, and it is what a latency-sensitive system cares about.
- **Amortized** — n calls cost O(n) *total*, guaranteed, on every input.
- **Average case** — assumes a distribution over inputs (quickselect's O(n) is
  this kind, and an adversary can break it; amortized cannot be broken).

Say "amortized O(1)" when you mean the sequence, and be ready for the follow-up:
*"is there a single call that is slow?"* For a doubling array, yes — and that is
why a real-time system pre-sizes it.

### Space

Same counting, applied to memory you allocate. An extra array is O(n); a fixed
26-slot counter is O(1). Recursion costs stack depth even when it allocates
nothing — a recursion n deep is O(n) space.

### When O(n²) is the right answer

When n is small, when the quadratic version is obviously correct and the linear
one is delicate, or when you need a baseline to test the fast one against.
"Optimal" is defined by the constraints, not by pride.
""",
    signals=[
        _sig("`n ≤ 20`", "Exponential search (subsets, permutations)",
             "The constraint is a hint that nothing polynomial is expected."),
        _sig("`n ≤ 5,000`", "O(n²) is fine",
             "Do the simple thing; a clever linear solution is wasted effort."),
        _sig("`n ≤ 10⁵` or more", "O(n log n) at worst",
             "Quadratic will time out. Sort, hash or two-pointer it."),
        _sig("Values up to 10⁹ but few of them", "Binary search or a formula",
             "Cost tracks the count of items, not the size of the numbers."),
        _sig("A `.contains()` or `indexOf` inside a loop", "Hash it instead",
             "The hidden inner scan makes an innocent-looking loop quadratic."),
        _sig("An inner `while` that can only undo what an outer step did",
             "Count the whole loop, not one iteration",
             "Amortized O(1): each item is added once, so it can be removed once."),
    ],
    skeletons=[
        _sk("The accidental quadratic",
            "Recognise this shape — it is the single most common performance bug.",
            """
// O(n²): contains() scans the whole list on every iteration
for (int x : a) {
    if (seenList.contains(x)) { ... }
    seenList.add(x);
}

// O(n): the same logic, with a hash set
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (!seen.add(x)) { ... }   // add returns false if already present
}
""",
            "`Set.add` returning `false` is the idiomatic “I have seen this before”."),
        _sk("Counting sort / frequency array",
            "When the values are small integers or letters, counting beats sorting.",
            """
int[] freq = new int[26];               // O(1) space — 26 is a constant
for (char c : s.toCharArray()) freq[c - 'a']++;
""",
            "O(n) time, O(1) space. The alphabet is a constant, however big it feels."),
        _sk("The amortized argument, written out",
            "Whenever an inner loop can only undo work an outer step did.",
            """
// Claim: this whole loop is O(n), not O(n²).
int removed = 0;
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && shouldPop(st.peek(), a[i])) { st.pop(); removed++; }
    st.push(i);                       // <- exactly n pushes over the whole loop
}
// removed <= n, because nothing is popped that was not pushed.
// Total work = n pushes + (<= n) pops = O(n)  ->  O(1) amortized per iteration.
""",
            "Name the deposit (`push`) and the withdrawal (`pop`), then bound the deposits. "
            "That sentence is the proof, and it is what an interviewer wants to hear."),
    ],
    costs=[
        _cost("O(1)", "constant", "—", "Array index, hash lookup, arithmetic."),
        _cost("O(log n)", "~20 steps at n = 10⁶", "—", "Binary search, heap push/pop, tree descent."),
        _cost("O(n)", "10⁶ is instant", "—", "A pass. The floor for anything that must read all input."),
        _cost("O(n log n)", "10⁶ is comfortable", "—", "Sorting. The usual cost of imposing order."),
        _cost("O(n²)", "10⁴ is fine, 10⁵ is not", "—", "Every pair. Check the constraint first."),
        _cost("O(2ⁿ)", "n ≤ 25", "—", "Every subset. Only viable because n is tiny."),
        _cost("O(1) amortized", "n operations cost O(n)", "—",
              "`ArrayList.add`, a monotonic stack step. One call may still be O(n)."),
    ],
    pitfalls=[
        _pit("“Time limit exceeded” on the large test only",
             "The approach is a tier too slow — usually a hidden inner scan.",
             "Count the loops, including the ones inside library calls, then re-read the constraint."),
        _pit("Optimising code that was never the bottleneck",
             "Constant-factor tinkering inside an O(n²) algorithm.",
             "Change the shape, not the constant. O(n log n) beats a tuned O(n²) at any interesting n."),
        _pit("`String` concatenation in a loop is mysteriously slow",
             "`s += x` allocates a whole new string each time, making the loop O(n²) in "
             "total characters.",
             "Accumulate with `StringBuilder` and call `toString()` once."),
        _pit("Claiming O(n) for something that sorts",
             "Sorting is O(n log n); a single call can dominate everything around it.",
             "State the complexity of every library call you make, not just your loops."),
        _pit("Calling a monotonic-stack or sliding-window loop O(n²)",
             "The inner `while` was counted as n, when it can only remove what an outer "
             "step added.",
             "Bound the *total* removals over the whole loop, not the removals in one "
             "iteration. n additions allow at most n removals — O(n) overall."),
        _pit("Saying “amortized” when the claim is really “average case”",
             "Both mean “usually fast”, but only one of them survives an adversary.",
             "Amortized is a guarantee over a sequence on *every* input; average case "
             "assumes a distribution. Quickselect is average O(n); `ArrayList.add` is "
             "amortized O(1)."),
    ],
    lessons=["big_o", "alg_big_o", "alg_analyzing", "alg_space",
             "alg_pattern_recognition"],
    bigo=[
        _bigo(
            """
long sum = 0;
for (int i = 0; i < n; i++) sum += a[i];
""",
            "O(n)", ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "One pass, one constant-time body. The floor for any problem that has to look "
            "at every element.",
        ),
        _bigo(
            """
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[i] + a[j] == target) count++;
""",
            "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
            "n(n−1)/2 pairs. Starting the inner loop at `i + 1` halves the work and changes "
            "nothing asymptotically — a constant factor is not a complexity.",
        ),
        _bigo(
            """
while (n > 0) {
    total += n % 10;
    n /= 10;
}
""",
            "O(log n)", ["O(1)", "O(log n)", "O(n)", "O(√n)"],
            "One iteration per *digit*, so ⌊log₁₀ n⌋ + 1 — at most 10 for an `int`. Note that "
            "this is log in the **value** of n, not in the size of a collection. Calling it "
            "O(1) because it never exceeds 10 is defensible in conversation and wrong on "
            "paper; say which you mean.",
        ),
        _bigo(
            """
Arrays.sort(a);
for (int x : a) if (set.contains(x)) hits++;
""",
            "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "The sort dominates: O(n log n) + O(n) = O(n log n). The library call is where "
            "the cost is, which is exactly the habit this unit is for — price the calls, not "
            "just your own loops.",
        ),
        _bigo(
            """
for (int x : a)
    if (list.contains(x)) hits++;   // list is an ArrayList
""",
            "O(n²)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "`ArrayList.contains` is a linear scan, so an O(n) operation is nested inside an "
            "O(n) loop. This is the single most common accidental quadratic in real code, and "
            "it does not *look* nested. Swap the list for a `HashSet` and it is O(n).",
        ),
        _bigo(
            """
for (int i = 1; i < n; i *= 2)
    for (int j = 0; j < n; j++)
        work++;
""",
            "O(n log n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "The outer loop *multiplies*, so it runs log₂ n times; the inner one runs n. "
            "Nesting does not always mean squaring — read what the update does to the "
            "counter, not how many `for`s there are.",
        ),
        _bigo(
            """
static int f(int n) {
    if (n <= 1) return n;
    return f(n - 1) + f(n - 2);
}
""",
            "O(2ⁿ)", ["O(n)", "O(n²)", "O(2ⁿ)", "O(n log n)"],
            "Two branches per call and depth n, so the call tree is exponential — about 1.6ⁿ "
            "to be precise, since it is the Fibonacci recurrence. Memoise it and the same "
            "function is O(n), which is the whole DP stage in one edit.",
        ),
        _bigo(
            """
static int g(int n) {
    if (n == 0) return 0;
    return 1 + g(n - 1);
}
""",
            "O(n) time, O(n) space",
            ["O(n) time, O(1) space", "O(n) time, O(n) space",
             "O(log n) time, O(1) space", "O(1) time, O(1) space"],
            "Linear time, and linear **space** — every pending call holds a stack frame. "
            "Deep recursion is a memory cost that looks free, and at n = 10⁶ it is a "
            "`StackOverflowError` rather than a slow answer.",
        ),
        _bigo(
            """
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) sum += grid[i][j];
}
// n is the side length of an n × n grid
""",
            "O(n²), which is linear in the input size",
            ["O(n)", "O(n²), which is linear in the input size", "O(n²), and unavoidably quadratic",
             "O(n log n)"],
            "Both readings are right and the distinction matters. The grid holds n² cells, so "
            "reading all of them is O(n²) in n and O(size) in the actual input. Saying "
            "\"quadratic\" without saying *in what* is how a linear-time grid scan gets "
            "mistaken for something to optimise.",
        ),
        _bigo(
            """
int lo = 0, hi = n;
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < x) lo = mid + 1; else hi = mid;
}
""",
            "O(log n)", ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "The range halves every iteration, so ⌈log₂ n⌉ iterations — 17 for 100,000 "
            "elements. The cost of *getting* the array sorted is not counted here, and "
            "forgetting to mention it is a common way to overstate a solution.",
        ),
        _bigo(
            """
Deque<Integer> st = new ArrayDeque<>();
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && a[st.peek()] < a[i]) st.pop();
    st.push(i);
}
""",
            "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(n·√n)"],
            "Two nested loops and still linear. The `while` can only pop indices some "
            "earlier iteration pushed, and each index is pushed exactly once — so at most "
            "n pops happen across the *whole* loop, not per iteration. That is amortized "
            "O(1) per step. Counting the inner loop as n here is the classic over-estimate.",
        ),
        _bigo(
            """
List<Integer> list = new ArrayList<>();
for (int i = 0; i < n; i++) list.add(i);   // resizes by doubling when full
""",
            "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "A resize copies everything, so *one* `add` can be O(n) — but the copies happen "
            "at sizes 1, 2, 4, 8 …, and 1 + 2 + 4 + … + n < 2n. Total O(n), i.e. O(1) "
            "amortized per add. Growing by a fixed +1 instead of doubling would make the "
            "same loop genuinely O(n²).",
        ),
    ],
    checks=[
        _chk("A problem says `1 ≤ n ≤ 200000`. Is an O(n²) solution acceptable?",
             "No — that is 4×10¹⁰ operations. The constraint is telling you to find an "
             "O(n log n) or O(n) approach."),
        _chk("Why is `for (x : a) if (list.contains(x))` quadratic?",
             "`contains` on a list is itself a linear scan, so the loop nests one O(n) "
             "operation inside another. A `HashSet` makes the inner step O(1)."),
        _chk("Are two sequential O(n) passes worse than one?",
             "Not in Big-O — O(n) + O(n) = O(n). Only the constant factor differs, and "
             "clarity usually wins that trade."),
        _chk("What is the space complexity of a recursion that goes n levels deep and "
             "allocates nothing?",
             "O(n) — every pending call keeps a frame on the stack. Deep recursion is a "
             "memory cost even when it looks free."),
        _chk("`n ≤ 22` and the problem asks for every possible selection. What does that hint?",
             "That 2ⁿ ≈ 4 million is the intended cost — enumerate the subsets, and do not "
             "hunt for a polynomial trick that probably does not exist."),
        _chk("A loop over n items has an inner `while` that can pop the whole stack. "
             "Why is it O(n) and not O(n²)?",
             "Because the pops are paid for by the pushes. Each index is pushed once, so "
             "across the entire loop there are at most n pops — no single iteration's worst "
             "case can happen n times. Total work 2n, i.e. O(1) amortized per iteration."),
        _chk("What is the difference between amortized O(1) and average-case O(1)?",
             "Amortized is a guarantee about a *sequence* of operations that holds on every "
             "input; average case assumes a distribution over inputs and can be defeated by "
             "an adversary. `ArrayList.add` is amortized O(1); a hash lookup is average O(1)."),
        _chk("Is `ArrayList.add` ever slow?",
             "Yes — the call that triggers a resize copies every element, so that one call "
             "is O(n). Amortized O(1) says n adds cost O(n) in total; it does not promise "
             "any individual call is cheap. Pre-size the list if that matters."),
    ],
    interview="""
"What is the time and space complexity?" is asked in essentially every
interview, and the high-scoring version of the answer has three parts: the
complexity, *why* (the loops that produce it), and whether it is optimal
*given the constraints*. Volunteering the third part — "this is O(n log n)
because of the sort; O(n) is possible with counting since the values are
bounded" — is what separates a pass from a strong pass.
""",
    variants=[
        _var("Sequential passes",
             "Two loops one after another, not nested.",
             "A clean-up pass, then a compute pass.",
             "O(n) + O(n) = O(n)",
             "Fusing them into one loop buys a constant factor and costs clarity. Do it when "
             "profiling says to, not by reflex."),
        _var("Nested over the same data",
             "The inner loop runs over the same n as the outer one.",
             "Every pair: comparisons, sums, collisions.",
             "O(n²)",
             "Starting the inner loop at `i + 1` halves the work and changes nothing "
             "asymptotically. A constant factor is not a complexity."),
        _var("Nested over different data",
             "The inner loop runs over a *second* collection of size m.",
             "Matching two lists, a grid of r × c.",
             "O(n · m)",
             "Calling this \"n²\" is the most common imprecision in an interview answer. Say "
             "which n — and for an r × c grid, O(r·c) is *linear in the input*."),
        _var("Halving",
             "The counter is divided, not decremented.",
             "Binary search, tree descent, heap sift.",
             "O(log n)",
             "20 steps at a million, 30 at a billion. Effectively constant, and worth saying "
             "so out loud when the constraint is 10⁹."),
        _var("Multiplying counter with an inner pass",
             "The outer counter multiplies; the inner one is linear.",
             "Doubling constructions: sparse tables, binary lifting, merge sort levels.",
             "O(n log n)",
             "Two nested `for`s and *not* quadratic. Read what the update does to the counter, "
             "not how many loops there are."),
        _var("Digits or bits of a value",
             "The loop runs over `log₁₀ v` digits or `log₂ v` bits, not over n items.",
             "Digit sums, bit tricks, fast exponentiation.",
             "O(log v)",
             "This is log in the **value**, not in the size of a collection. Calling it O(1) "
             "because an `int` has at most 10 digits is defensible in conversation and wrong "
             "on paper — say which you mean."),
        _var("Hidden inner scan",
             "The inner loop is inside a method call, so the nesting is invisible.",
             "`list.contains`, `indexOf`, `String.substring`, `s += x`.",
             "O(n) × the call's own cost",
             "The single most common accidental quadratic in real code. Price every library "
             "call you make, not just the loops you typed."),
        _var("Inner loop that can only undo outer work",
             "The inner `while` removes only what an outer step added.",
             "Monotonic stacks, sliding windows, two pointers.",
             "O(1) amortized → O(n) overall",
             "Counting the inner `while` as n here over-estimates by a whole tier. Bound the "
             "*total* removals, not one iteration's worst case."),
        _var("Branching recursion",
             "Each call makes two (or k) more.",
             "Naive Fibonacci, subset enumeration, unmemoised DP.",
             "O(2ⁿ) — O(kⁿ) in general",
             "Add memoisation and the same function is O(n) or O(n²). That one edit is the "
             "entire DP stage, and it is worth recognising three stages early."),
    ],
    rewrites=[
        _rw("The accidental quadratic",
            """
// O(n²) — `contains` on a list is itself a linear scan
List<Integer> seen = new ArrayList<>();
for (int x : a) {
    if (seen.contains(x)) return true;
    seen.add(x);
}
return false;
""",
            """
// O(n) — the same logic, with a hash set
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (!seen.add(x)) return true;      // add returns false if already present
}
return false;
""",
            "`ArrayList` → `HashSet`, and `contains` + `add` collapse into one `add`.",
            """
Nothing about the *logic* changed — the same elements are inserted and the same
question is asked. What changed is the cost of asking it: `ArrayList.contains`
walks the whole list, so an O(n) operation was sitting inside an O(n) loop and
the nesting was hidden behind a method name.

This is the shape to learn to see, because it does not look nested. Any time a
loop body calls something that searches, the loop is one tier slower than it
reads.

`Set.add` returning `false` for a duplicate is the idiomatic form — it does the
lookup and the insert in one hash of the key instead of two.
""",
            ),
        _rw("Building a string in a loop",
            """
// O(n²) in total characters — each += copies everything so far
String out = "";
for (String part : parts) out += part + ",";
return out;
""",
            """
// O(n) — one buffer, appended to
StringBuilder sb = new StringBuilder();
for (String part : parts) sb.append(part).append(',');
return sb.toString();
""",
            "`String +=` → `StringBuilder.append`, with one `toString()` at the end.",
            """
Java strings are immutable, so `out += part` cannot extend `out` — it allocates
a new string and copies every character already there. Over n parts that is
1 + 2 + 3 + … characters copied, which is O(n²) in the total length.

`StringBuilder` keeps one mutable buffer and doubles it when full, so the n
appends cost O(n) **amortized** in total — the same doubling argument as
`ArrayList.add`.

The tell is any `+=` on a `String` inside a loop. On a few dozen parts it does
not matter; on 10⁵ it is the difference between instant and a timeout, and the
profiler will point at a line that looks innocent.
""",
            ),
        _rw("Sorting when counting would do",
            """
// O(n log n) — sorting to find duplicates of small values
int[] copy = a.clone();
Arrays.sort(copy);
for (int i = 1; i < copy.length; i++)
    if (copy[i] == copy[i - 1]) return copy[i];
return -1;
""",
            """
// O(n) — the values are bounded, so count them directly
int[] freq = new int[MAX_VALUE + 1];
for (int x : a)
    if (++freq[x] == 2) return x;
return -1;
""",
            "`Arrays.sort` → a frequency array indexed by the value itself.",
            """
Sorting imposes a *total order* you never needed. The question is only "has this
value appeared before", and when the values are bounded — letters, digits,
`0 … 10⁵` — the value can be the index, which makes the lookup O(1) and the
whole pass O(n).

The condition is the bound. With values up to 10⁹ the frequency array is 4 GB
and this rewrite is worse than useless; that is when a `HashMap` takes its place
and you pay a constant factor instead of a log.

This is also the one rewrite here that is *not* always a win: it trades O(1)
extra space for O(V) where V is the value range. Say the trade out loud rather
than presenting it as free.
""",
            ),
    ],
    build_it="""
### Price these three yourself, and then measure them

The goal is to stop trusting the table in this unit and start trusting an
experiment you ran.

**1. Write the timing harness.** A method that takes a `Runnable`, runs it once
to let the JIT warm up, then times it:

```java
static long millis(Runnable r) {
    r.run();                                  // warm-up — do NOT skip this
    long t = System.nanoTime();
    r.run();
    return (System.nanoTime() - t) / 1_000_000;
}
```

**2. Time three shapes** at n = 1,000 / 10,000 / 100,000 on random `int[]`s:

| Shape | What to write |
| --- | --- |
| O(n) | sum every element |
| O(n log n) | `Arrays.sort(a.clone())` |
| O(n²) | count pairs with `a[i] + a[j] == 0` |

**3. Read the ratios, not the times.** Ten times the input should cost:

- about **10×** for the linear pass;
- a little over **10×** for the sort (10 × log₁₀ of the ratio);
- about **100×** for the quadratic one.

The quadratic at n = 100,000 will take minutes. That is the point of the
exercise — stop it early and extrapolate from n = 10,000, which is itself the
skill this unit is about.

**4. Then find the surprise.** Time `list.contains` in a loop against
`set.contains` at n = 50,000. The ratio is not 2 or 10; it is in the thousands,
and the two versions look almost identical on the page.

**5. Finally, measure an amortized claim.** Append 10⁶ elements to an
`ArrayList`, then do the same to a list that grows by `+1` each time
(`Arrays.copyOf(a, a.length + 1)`). Doubling finishes instantly; +1 growth is
the same loop, genuinely O(n²), and watching it crawl is what makes "amortized
O(1)" stop being a phrase.
""",
    rungs=[
        _rung("Core", "Feel the difference between a quadratic and a linear solution on the same problem.",
              ["second-largest", "count-above-average", "count-equal-pairs", "sum-of-pair-products"],
              {"second-largest": "Solvable by sorting (O(n log n)) or by two accumulators (O(n)). Write both and compare.",
               "count-above-average": "The two-pass solution people try to avoid. It is still O(n) — that is the lesson.",
               "count-equal-pairs": "Every pair is O(n²); counting occurrences first makes it O(n). The gap here is the whole unit in one problem.",
               "sum-of-pair-products": "The nested loops are right and 5·10⁹ steps at the limit. Read the inner loop as a sum you could carry instead."}),
        _rung("Stretch", "Pay O(n log n) once to turn an O(n²) question into a linear pass.",
              ["sum-abs-differences"],
              {"sum-abs-differences": "The answer does not depend on the order of the array — so pick the order that deletes the absolute value."}),
    ],
    next_up="""
`count-equal-pairs` became linear by *counting what it had seen*. Generalise
that and you have the most useful data structure in interview programming.
""",
)


# --- Unit 6 — Hashing --------------------------------------------------------

_unit(
    "hashing", "Hashing: Trade Space for Time", "🗝️", _S2,
    "“Have I seen this?” in O(1), and everything that follows from it.",
    weight=3,
    prereqs=["arrays-first-pass", "complexity"],
    why="""
The commonest reason code is quadratic is that it searches. *For each element,
look through the rest* is two nested loops, and the inner one is almost always
asking a question a hash table can answer instantly: **have I seen this value,
and if so, where or how often?**

Hashing is the single highest-return pattern in this curriculum. It turns a
whole tier of O(n²) solutions into O(n) with a few lines, and the cost is memory
— which is nearly always the right trade.
""",
    model="""
### Three structures, three questions

| You need to know | Use | Cost |
| --- | --- | --- |
| *Have I seen x?* | `HashSet<T>` | O(1) add / contains |
| *How many times have I seen x?* | `HashMap<T, Integer>` | O(1) get / put |
| *Where did I see x?* | `HashMap<T, Integer>` value = index | O(1) |

All three are the same structure underneath. Choosing is just naming what the
value means.

### The complement trick

Two-sum is the archetype, and it generalises: **as you scan, ask whether the
partner you need has already gone past.**

```java
for (int i = 0; i < n; i++) {
    int need = target - a[i];
    if (seen.containsKey(need)) return new int[]{ seen.get(need), i };
    seen.put(a[i], i);          // AFTER the check, never before
}
```

Checking before inserting is what stops an element pairing with itself. That one
line ordering is the whole difference between right and wrong.

### Canonical forms

*Group the anagrams* is the same question as *are these equal?* once you can
reduce each item to a **canonical form** — a representative that is identical
for everything in a group. Sorted letters (`"eat"` → `"aet"`) is one; a
26-length count signature is another, and is O(n) rather than O(n log n).

The pattern is worth naming because it is how you hash something that is not
already a key: reduce it to something equal-when-equivalent, then hash *that*.

### Counting when the keys are small

If the keys are letters or small integers, an `int[]` beats a `HashMap` on every
axis — no boxing, no hashing, cache friendly:

```java
int[] freq = new int[26];
freq[c - 'a']++;
```

Reach for the map only when the key space is large or not an integer.
""",
    signals=[
        _sig("“does it contain a duplicate?”", "`HashSet`",
             "`add` returning false *is* the duplicate test."),
        _sig("“two numbers that sum to target”", "Complement map",
             "Look for `target - x` among what you have already passed."),
        _sig("“group / anagram / same letters”", "Canonical key → `HashMap<String, …>`",
             "Sorted letters or a count signature makes equivalent items share a key."),
        _sig("“most frequent”, “appears more than n/2 times”", "Frequency map",
             "Count in one pass, decide in a second."),
        _sig("“longest consecutive sequence”", "`HashSet` + start detection",
             "Membership tests replace sorting; only extend from a run's first element."),
        _sig("Keys are letters or values ≤ a few thousand", "`int[]` counter",
             "Same algorithm without boxing, hashing or allocation."),
    ],
    skeletons=[
        _sk("Seen-set",
            "Duplicates, first repeat, membership.",
            """
Set<Integer> seen = new HashSet<>();
for (int x : a) {
    if (!seen.add(x)) {         // false ⇒ x was already there
        return true;
    }
}
return false;
""",
            "`add` reports novelty and inserts in one operation — no separate `contains`."),
        _sk("Complement lookup",
            "Two-sum and every variation of “find the partner”.",
            """
Map<Integer, Integer> seen = new HashMap<>();   // value → index
for (int i = 0; i < a.length; i++) {
    Integer j = seen.get(target - a[i]);
    if (j != null) return new int[]{ j, i };
    seen.put(a[i], i);
}
""",
            "Check, then insert. Inserting first lets an element pair with itself."),
        _sk("Frequency map",
            "Counting, majority, top-k, anagram checks.",
            """
Map<Integer, Integer> freq = new HashMap<>();
for (int x : a) freq.merge(x, 1, Integer::sum);
""",
            "`merge` replaces the `getOrDefault(x, 0) + 1` dance."),
        _sk("Canonical key",
            "Grouping items that are equivalent under some transformation.",
            """
Map<String, Integer> groups = new HashMap<>();
for (String w : words) {
    char[] c = w.toCharArray();
    Arrays.sort(c);                       // the canonical form
    groups.merge(new String(c), 1, Integer::sum);
}
""",
            "A 26-int count signature is the O(n) alternative to sorting each word."),
        _sk("Longest consecutive run",
            "Sequence problems where sorting would be too slow.",
            """
Set<Integer> set = new HashSet<>(list);
int best = 0;
for (int x : set) {
    if (set.contains(x - 1)) continue;    // only start from a run's first value
    int len = 1;
    while (set.contains(x + len)) len++;
    best = Math.max(best, len);
}
""",
            "The `continue` is what keeps it O(n): each run is walked exactly once."),
    ],
    costs=[
        _cost("`HashMap` / `HashSet` get, put, contains", "O(1) average", "O(n)",
              "Worst case O(n) on adversarial keys; not a concern for these problems."),
        _cost("Building a frequency map", "O(n)", "O(k)", "k = number of distinct keys."),
        _cost("`int[]` counter", "O(n)", "O(1)", "When the key space is a fixed alphabet."),
        _cost("Sorting-based grouping", "O(n · m log m)", "O(n · m)",
              "m = item length. The count-signature version drops the log."),
    ],
    pitfalls=[
        _pit("Two-sum returns the same index twice",
             "The current element was inserted into the map before the complement check.",
             "Always check first, insert afterwards."),
        _pit("`map.get(k)` throws a `NullPointerException`",
             "A missing key returns `null`, which unboxes to an NPE when assigned to `int`.",
             "`map.getOrDefault(k, 0)`, or hold the result in an `Integer` and test for null."),
        _pit("Counting with `HashMap` is unexpectedly slow",
             "Boxing every `int` into an `Integer` allocates on the hot path.",
             "When keys are bounded and small, use an `int[]` instead."),
        _pit("Objects that should be equal end up in different buckets",
             "A custom key class overrides `equals` but not `hashCode`.",
             "Override both, or use an already-hashable canonical form such as a `String`."),
        _pit("Longest-consecutive degrades to O(n²)",
             "Every element walks its whole run, instead of only run starts doing so.",
             "Skip any `x` where `x - 1` is present."),
    ],
    lessons=["hashing", "complement", "canonical", "visited_set"],
    checks=[
        _chk("Why check the map before inserting the current element in two-sum?",
             "Otherwise `target - a[i] == a[i]` finds the element itself and reports a pair "
             "of one element with itself."),
        _chk("When is `int[26]` better than `HashMap<Character, Integer>`?",
             "Whenever the keys are a fixed small alphabet: no boxing, no hashing, better "
             "cache behaviour, and O(1) space by definition."),
        _chk("Longest-consecutive uses a set and still claims O(n). How?",
             "Each run is walked only from its smallest element — guarded by "
             "`if (set.contains(x - 1)) continue;` — so every value is visited a constant "
             "number of times overall."),
        _chk("What makes a good canonical key for grouping anagrams?",
             "Anything identical for equivalent items: sorted characters (O(m log m)) or a "
             "26-slot count signature rendered as a string (O(m))."),
        _chk("What is the worst-case complexity of a `HashMap` lookup, and why is it "
             "acceptable?",
             "O(n) if every key collides. With well-distributed hashes it is O(1) average, "
             "and Java's map switches long buckets to trees, capping it at O(log n)."),
        _chk("Why must the map be queried before the new element is inserted?",
             "Because the query is what makes every answer refer to an index strictly before "
             "the current one. Insert first and an element can pair with itself — target 6 "
             "on [3, 1] would report [0, 0]. The rule people memorise as “query before "
             "insert” is the loop invariant."),
        _chk("When is an `int[26]` the better choice over a `HashMap`?",
             "Whenever the key space is small and fixed — lowercase letters, digits, "
             "bounded small integers. Same O(n) bound, a much smaller constant, no boxing and "
             "no rehashing. The map earns its place when the keys are open-ended."),
        _chk("What makes a canonical key safe to group by?",
             "That it is injective **by construction**: two different items must not be able "
             "to produce it. A sorted string or a 26-slot count signature qualifies; a sum of "
             "character codes does not, because `ad` and `bc` both make 199."),
        _chk("Why is a hash lookup described as O(1) *average* rather than just O(1)?",
             "Because the bound depends on the keys spreading across buckets. With every key "
             "colliding, a bucket is a list and a lookup is O(n) — Java caps that at "
             "O(log n) by turning long buckets into trees, but the honest statement is still "
             "“average”."),
    ],
    interview="""
Hashing is the expected answer often enough that the interesting follow-up is
always *"now do it without extra space"*. That is your cue to look for sorting,
two pointers, or an in-place marking trick — and to say out loud what you are
giving up: sorting costs O(n log n), and marking usually destroys the input.
""",
    invariant=_inv(
        "Before index `i` is processed, the map holds an entry for **every** index "
        "`j < i` and for **no** index `j ≥ i`.",
        "Before the first iteration the prefix `a[0 … -1]` is empty and so is the map. "
        "Both sides of the sentence are vacuously true.",
        "One iteration does exactly two things, and **the order is the whole rule**: it "
        "*queries* the map first, then inserts `i`. Querying first is what makes every "
        "answer it returns refer to an index strictly before `i` — so `i` can never pair "
        "with itself. Inserting afterwards is what extends the prefix by exactly one, "
        "restoring the sentence for `i + 1`.",
        "Every ordered pair `(j, i)` with `j < i` has been offered to the map exactly "
        "once. So if a qualifying pair exists anywhere in the array, the scan saw it — "
        "which is why **one pass** is enough and a second one would find nothing new.",
        "This is why `two-sum` with a target of `6` on `[3, 3]` returns `[0, 1]` and "
        "`[3, 1]` does not return `[0, 0]`. The rule people memorise as “query before "
        "insert” is this invariant, and knowing it is the difference between recalling "
        "the order and being able to derive it.",
    ),
    variants=[
        _var("Seen set",
             "Store membership only — no value.",
             "“has this appeared before”, duplicates, cycles, visited cells.",
             "O(n) time, O(n) space",
             "`set.add(x)` already returns `false` for a duplicate. Writing "
             "`if (set.contains(x)) … else set.add(x)` hashes the key twice for the same "
             "answer."),
        _var("Frequency map",
             "Store a count instead of a flag.",
             "Anagrams, majority, “most common”, top-k.",
             "O(n) time, O(k) space for k distinct keys",
             "For a fixed small alphabet an `int[26]` beats a `HashMap` by a large constant "
             "and never rehashes. Reach for the map only when the key space is open."),
        _var("Complement lookup",
             "Store value → index, and query for `target - x` rather than for `x`.",
             "Two-sum and everything shaped like it: pairs summing, differing or "
             "XOR-ing to a target.",
             "O(n) time, O(n) space",
             "Query before insert (see the invariant). Reversing the two lines lets an "
             "element pair with itself, and it passes every test where the answer uses two "
             "different values."),
        _var("Canonical key",
             "Map each item to a *normal form*, and group by that.",
             "Group anagrams, “which of these are the same shape”, dedup by "
             "equivalence rather than by equality.",
             "O(n · c) where c is the cost of one key",
             "The key must be collision-free **by construction**, not by luck. A sorted "
             "string or a 26-slot count signature is; a sum of character codes is not — "
             "`ad` and `bc` collide."),
        _var("Prefix-state map",
             "Store a running aggregate over the prefix → where (or how often) it occurred.",
             "Subarray sums equal to k, equal numbers of 0s and 1s, subarray divisible by k.",
             "O(n) time, O(n) space",
             "Seed it with the empty prefix — `{0: 1}` when counting, `{0: -1}` when you "
             "want a length. Forgetting the seed loses exactly the subarrays that start at "
             "index 0, which most small tests do not cover."),
        _var("Last-seen index",
             "Store value → the *most recent* index, overwriting on each sight.",
             "Longest substring without repeats, “a duplicate within k indices”.",
             "O(n) time, O(k) space",
             "Overwrite; do not skip. Keeping the first occurrence answers a different "
             "question, and the window-start pointer must never move backwards — "
             "`start = max(start, seen.get(c) + 1)`."),
    ],
    rewrites=[
        _rw("Two-sum: every pair, or one pass",
            """
// O(n²) — try every pair
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[i] + a[j] == target) return new int[]{ i, j };
return new int[]{ -1, -1 };
""",
            """
// O(n) — ask the map for the partner you need
Map<Integer, Integer> seen = new HashMap<>();
for (int i = 0; i < n; i++) {
    Integer j = seen.get(target - a[i]);      // QUERY first
    if (j != null) return new int[]{ j, i };
    seen.put(a[i], i);                        // then insert
}
return new int[]{ -1, -1 };
""",
            "The inner loop becomes a single map lookup for the one value that would work.",
            """
The inner loop was not really *searching* — it already knew exactly what it
wanted. For a fixed `a[i]` only one partner value can complete the pair,
`target - a[i]`, and scanning to find it is doing a lookup the slow way.

So the edit is: stop looking for *a* partner and look up *the* partner. That is
what trades O(n) of scanning for O(1) of hashing, and it is the move the whole
unit is about.

**No answer is lost.** Every pair `(j, i)` with `j < i` is considered exactly
once — when the loop reaches `i`, the map holds precisely the earlier indices
(the invariant above). The nested version considers the same pairs in the same
grouping; it just re-derives the partner each time.

The cost moved rather than vanishing: O(1) space became O(n). When the follow-up
is "now without extra space", the answer is sort plus two pointers at
O(n log n) — which is the next unit.
""",
            ),
        _rw("Anagram check: sort, or count",
            """
// O(m log m) — sort both and compare
char[] x = s.toCharArray(), y = t.toCharArray();
Arrays.sort(x);
Arrays.sort(y);
return Arrays.equals(x, y);
""",
            """
// O(m) — one counter, incremented then decremented
if (s.length() != t.length()) return false;
int[] freq = new int[26];
for (int i = 0; i < s.length(); i++) {
    freq[s.charAt(i) - 'a']++;
    freq[t.charAt(i) - 'a']--;
}
for (int f : freq) if (f != 0) return false;
return true;
""",
            "Two sorts become one pass that adds for `s` and subtracts for `t`.",
            """
Sorting produces a canonical form and then throws all of it away except the
equality test. The cheaper canonical form for "same multiset of letters" is the
multiset itself — 26 counters.

The one-pass trick is worth noticing on its own: instead of building two count
arrays and comparing them, increment for one string and decrement for the other.
Equal multisets leave every counter at zero, so the comparison is free and the
second array never exists.

**The length guard is not an optimisation.** Without it, `"a"` and `"aa"` both
leave `freq['a']` non-zero — but `"ab"` against `"aab"` would need the loop to
run over the longer string, and the single index `i` assumes equal lengths.
Check it first and the rest of the method is safe.

This stops being the right rewrite the moment the alphabet is unbounded — full
Unicode, or arbitrary integers. Then it is a `HashMap` frequency map, which
gives up the constant factor and keeps the linear bound.
""",
            ),
    ],
    build_it="""
### Write a `HashMap` from scratch

The costs in the Toolkit stop being trivia the moment you have implemented the
thing they describe. Aim for about sixty lines.

**1. Separate chaining, fixed size.** A `Node[] buckets` of 16, each `Node`
holding `key`, `value` and `next`.

```java
private int indexFor(K key) {
    int h = key.hashCode();
    h ^= (h >>> 16);                       // spread high bits down
    return h & (buckets.length - 1);       // power-of-two modulo
}
```

Implement `put`, `get` and `remove`. `put` must **replace** when the key is
already present — the bug to make on purpose once is appending instead, so the
map silently holds two entries for one key and `get` returns whichever comes
first.

**2. Now break it.** Force every key into bucket 0 by returning `0` from
`indexFor`. The map still passes every correctness test and every operation is
now O(n). Time 10,000 `put`s both ways. That gap is what "average O(1)" is
hiding, and why a hash function that spreads is not a detail.

**3. Add resizing.** When `size > 0.75 * buckets.length`, double the array and
re-insert everything. Two things to notice:

- You cannot copy buckets across — an entry's index depends on the table
  length, so every key must be re-hashed.
- The resize is O(n) and happens at sizes 12, 24, 48 … so n insertions cost
  O(n) **amortized**: the same doubling argument as `ArrayList`, which you have
  now written twice.

**4. Implement `equals`/`hashCode` on a key class**, and then break the
contract: two objects that are `equals` but return different hash codes. Put one
in, look the other up, and watch the miss. That is the single most expensive
Java bug in this area, and seeing it once fixes it permanently.

**5. Finally, measure against `java.util.HashMap`.** Yours will be some small
multiple slower. If it is a hundred times slower, you are boxing or re-hashing
on every call — find out which.
""",
    internals="""
### What `HashMap` actually is

A **bucket array**, plus a rule for turning a key into an index into it.

```
hash = key.hashCode()
hash ^= (hash >>> 16)          // spread the high bits down
index = hash & (table.length - 1)   // cheap modulo, because length is a power of 2
```

Each bucket holds the entries whose keys landed on that index — a **collision**.
Java keeps them in a short linked list, and once a single bucket reaches **8**
entries (with a table of at least 64) it converts that list into a red-black
tree, so a pathological bucket degrades to O(log k) rather than O(k). That is
the entire reason `get` can be called O(1) with a straight face: the average
bucket is tiny, and the worst bucket is bounded.

### Load factor, and why the cost is *amortised*

`HashMap` grows when `size > capacity × 0.75`. Growing means allocating a table
of twice the length and re-indexing **every** entry, because the index depends
on `table.length`. That single insert costs O(n).

Spread over the n inserts that led to it, the cost per insert is still O(1) —
the same amortisation argument as `ArrayList` growth. It is worth being able to
say out loud, because "insert is O(1)" is false about *that* insert and true
about the sequence.

If you know the final size, `new HashMap<>(expectedSize / 0.75f + 1)` skips the
resizes entirely. Rarely decisive, occasionally the difference between passing
and timing out on 10⁶ insertions.

### What `HashMap` does *not* promise

**Any order at all.** Not insertion order, not key order, and not a stable
order across runs or across JDK versions. Code that iterates a `HashMap` and
prints is code whose output is not specified, and the judge compares text — so
this is a correctness bug, not a style one.

When order matters, say which order you mean:

| You want | Use |
|---|---|
| insertion order | `LinkedHashMap` |
| sorted by key | `TreeMap` — O(log n) per op, not O(1) |
| no order, fastest | `HashMap` |

### `hashCode` and `equals` are a pair

Two keys that are `equals` **must** have the same `hashCode`, or the map will
store both and find neither reliably. Java's `Integer`, `Long`, `String` and
`List` all honour this. A custom key class that overrides `equals` and forgets
`hashCode` is the classic silent bug — and an `int[]` used as a key is the same
bug with no override in sight, because arrays hash by identity. Use a
`List<Integer>` or a joined string instead.
""",
    rungs=[
        _rung("Warm up", "One set, one question: have I seen this before?",
              ["contains-duplicate", "two-sum-exists"],
              {"contains-duplicate": "Try it with a nested loop first, then with a set, and time both mentally against n = 10⁵."}),
        _rung("Core", "The complement trick and the frequency map.",
              ["two-sum-fn", "two-sum-indices", "two-sum-any", "valid-anagram", "first-unique-char"],
              {"two-sum-indices": "The canonical interview problem. You should be able to type this from memory.",
               "valid-anagram": "Counting beats sorting here — and the `int[26]` version is the one to remember."}),
        _rung("Variations", "Canonical keys, and counts used for a decision.",
              ["majority-element", "group-anagrams-count"],
              {"majority-element": "Counting solves it in O(n) space; look up Boyer–Moore afterwards for the O(1) version."}),
        _rung("Stretch", "A set used for membership instead of for duplicates.",
              ["longest-consecutive"],
              {"longest-consecutive": "Sorting makes it easy and O(n log n). The set version is O(n) — and the `continue` is the entire trick."}),
    ],
    next_up="""
Hashing buys speed with memory. The next unit buys it with **order** — and
spends no memory at all.
""",
)


# --- Unit 7 — Two pointers ---------------------------------------------------

_unit(
    "two-pointers", "Two Pointers", "↔️", _S2,
    "When the data is sorted, neither index ever needs to go back.",
    weight=3,
    prereqs=["arrays-first-pass"],
    why="""
Hashing costs O(n) memory. When the array is **sorted** — or can be — you can
often get the same O(n) time for O(1) space, because sortedness tells you which
direction to move. That is the whole idea: each comparison rules out a whole
range, so a pointer never has to revisit anything.

It is also the answer to the interviewer's favourite follow-up, *"can you do it
without the hash map?"*.
""",
    model="""
### Two arrangements

**Converging** — one pointer at each end, walking inward:

```java
int l = 0, r = n - 1;
while (l < r) {
    if (good(a[l], a[r])) return ...;
    else if (tooSmall) l++;
    else r--;
}
```

Correct because of an *invariant*: at every step the answer, if it exists, lies
between `l` and `r`. When the sum is too small, no pair using `a[l]` can work —
`a[l]` is already paired with the largest remaining value — so discarding it
loses nothing. Being able to state that sentence is the difference between
knowing the pattern and having memorised it.

**Same direction** — a `read` pointer that always advances and a `write`
pointer that only advances when something is kept:

```java
int write = 0;
for (int read = 0; read < n; read++) {
    if (keep(a[read])) a[write++] = a[read];
}
```

This is how every in-place filter, dedupe and compaction works, and it is
exactly the shape of `move-zeroes`.

### Reversal and palindromes

Swapping inward from both ends reverses in place in O(1) space; comparing
inward instead of swapping tests a palindrome. Same skeleton, one line changed.

### When the array is *not* sorted

You may sort it first — if the problem does not depend on original positions.
That is the trade: O(n log n) time for O(1) extra space. If indices must be
preserved, hashing is the right tool and two pointers is not.
""",
    signals=[
        _sig("“sorted array” + “find a pair”", "Converging pointers",
             "Sortedness makes each comparison discard one end."),
        _sig("“in place”, “without extra space”", "Read/write pointers",
             "Compaction needs no buffer, only a second index."),
        _sig("“reverse”, “is it a palindrome?”", "Swap or compare from both ends",
             "One skeleton, two uses."),
        _sig("“container”, “two lines”, “max area”", "Converging with a greedy move",
             "Move the limiting side; the other cannot improve while it is the bottleneck."),
        _sig("“merge two sorted …”", "One pointer per input",
             "Compare heads, take the smaller, advance that pointer."),
        _sig("Indices in the ORIGINAL order matter", "Hashing, not two pointers",
             "Sorting destroys the positions the answer is expressed in."),
    ],
    skeletons=[
        _sk("Converging pair search",
            "Two-sum on a sorted array, closest pair, container problems.",
            """
int l = 0, r = a.length - 1;
while (l < r) {
    int sum = a[l] + a[r];
    if (sum == target) return new int[]{ l, r };
    if (sum < target) l++;      // need bigger: only the left can grow
    else               r--;     // need smaller: only the right can shrink
}
""",
            "Say the invariant out loud: “if a pair exists, it is inside [l, r]”."),
        _sk("Read / write compaction",
            "Move zeroes, remove duplicates, filter in place.",
            """
int write = 0;
for (int read = 0; read < a.length; read++) {
    if (a[read] != 0) a[write++] = a[read];
}
while (write < a.length) a[write++] = 0;    // pad the tail
""",
            "`write` only advances on a keep, so it never overtakes `read`."),
        _sk("Reverse / palindrome in place",
            "Reversal, palindrome checks, rotation building blocks.",
            """
int l = 0, r = s.length - 1;
while (l < r) {
    char t = s[l]; s[l] = s[r]; s[r] = t;   // swap → reverse
    // or: if (s[l] != s[r]) return false;  // compare → palindrome
    l++; r--;
}
""",
            "`l < r` not `l <= r`: the middle element needs no partner."),
        _sk("Merge two sorted inputs",
            "Merging arrays or lists; the merge step of merge sort.",
            """
int i = 0, j = 0, k = 0;
while (i < n && j < m) out[k++] = (a[i] <= b[j]) ? a[i++] : b[j++];
while (i < n) out[k++] = a[i++];
while (j < m) out[k++] = b[j++];
""",
            "The two tail loops are not optional — exactly one of them runs."),
    ],
    costs=[
        _cost("Converging scan", "O(n)", "O(1)", "Each step retires one element."),
        _cost("Sort, then two pointers", "O(n log n)", "O(1)", "The sort dominates."),
        _cost("Hashing alternative", "O(n)", "O(n)", "Faster asymptotically; costs memory and keeps indices."),
        _cost("Merging two sorted inputs", "O(n + m)", "O(n + m)", "O(1) extra if merged in place from the back."),
    ],
    pitfalls=[
        _pit("Infinite loop",
             "A branch that advances neither pointer — usually a missing `l++` in an "
             "equality case.",
             "Every branch of the `while` must move at least one pointer."),
        _pit("The middle element is processed twice",
             "`while (l <= r)` in a swap or compare loop.",
             "Use `l < r`; a single middle element is already in place."),
        _pit("The answer's indices are wrong",
             "The array was sorted, which moved every element away from its original index.",
             "If positions matter, hash instead — or sort (value, index) pairs."),
        _pit("Compaction overwrites data it still needs",
             "`write` was advanced on every iteration rather than only on a keep.",
             "Increment `write` inside the `if`, never in the loop header."),
        _pit("Container-of-water moves the wrong side",
             "Advancing the taller line; the area is limited by the shorter one.",
             "Always move the shorter side — it is the only one that can improve."),
    ],
    lessons=["two_pointers", "alg_two_pointers", "inplace_reverse", "char_arrays"],
    checks=[
        _chk("Why is it safe to discard `a[l]` when `a[l] + a[r] < target`?",
             "Because `a[r]` is the largest value left: if `a[l]` cannot reach the target "
             "even with it, it cannot reach it with anything smaller."),
        _chk("Two pointers versus a hash map for two-sum — which and when?",
             "Sorted input or a no-extra-space requirement → two pointers (O(1) space). "
             "Unsorted input where the original indices are the answer → hashing."),
        _chk("In `move-zeroes`, why can `write` never overtake `read`?",
             "`write` advances only when an element is kept, and `read` advances every "
             "iteration, so `write ≤ read` always holds."),
        _chk("Why move the shorter line in the container problem?",
             "The area is `min(height) × width`. Narrowing loses width, so the only way to "
             "gain is a taller minimum — impossible while the short side stays."),
        _chk("State the converging-pointer invariant, and why moving a pointer is allowed.",
             "Every pair worth checking lies inside `[l, r]`. When `a[l] + a[r] < target`, "
             "`a[r]` is the largest partner `l` will ever be offered — so no pair "
             "containing `l` can reach the target, and dropping `l` cannot lose an answer. "
             "One comparison retires n candidates."),
        _chk("What breaks if the input is not sorted?",
             "The maintenance step. “`a[r]` is the best partner available” is a fact "
             "about sorted data and merely a hope otherwise, so the discard is no longer "
             "justified. The code still runs — it just returns wrong answers rather than "
             "slow ones, which is worse."),
        _chk("In the read/write compaction shape, why is writing to `a[write]` always safe?",
             "Because `write <= read` at all times: `write` advances only on an element `read` "
             "has already passed. The cell being overwritten therefore holds something already "
             "copied or already discarded."),
        _chk("Why merge two sorted arrays from the **back**?",
             "The spare capacity is at the back. Filling forwards overwrites elements of the "
             "first array that have not been read yet, so it needs a temporary copy; filling "
             "backwards from the largest element needs none and is O(1) extra space."),
    ],
    interview="""
Two pointers is the canonical *"optimise it"* answer, and the points are in the
justification, not the code. Interviewers listen for the invariant — "if a
solution exists it lies within the window, and this comparison proves the
element I am dropping cannot be part of one". Say that and the follow-up
usually stops.
""",
    invariant=_inv(
        "For converging pointers on a sorted array: **every pair worth checking lies "
        "within `[l, r]`.** No pair involving an index outside that range can be the "
        "answer.",
        "Before the first iteration `l = 0` and `r = n - 1`, so the range is the whole "
        "array and the sentence says nothing yet — which is exactly what makes it true.",
        "One iteration discards a whole *row or column* of the pair table, and the "
        "comparison is the proof that it may. With `a[l] + a[r] < target`, `a[r]` is the "
        "largest partner `l` will ever be offered, so no pair containing `l` can reach "
        "the target: dropping `l` loses nothing. Symmetrically, `> target` means `a[l]` "
        "is the smallest partner `r` can have, so `r` must go. Each step removes n "
        "candidate pairs at a cost of one comparison, and that ratio is the entire "
        "speedup.",
        "When `l >= r` the range holds no pairs at all. Combined with the invariant "
        "— every pair worth checking was inside it — the conclusion is that no "
        "qualifying pair exists anywhere.",
        "Notice what the argument needs: that `a` is **sorted**, so “largest partner "
        "available” is a fact about `a[r]` rather than a hope. On unsorted input the "
        "maintenance step is simply false, which is why the same code silently returns "
        "wrong answers rather than slow ones.",
    ),
    variants=[
        _var("Opposite ends, converging",
             "`l` starts at 0, `r` at `n - 1`; a comparison decides which one moves.",
             "Pairs in sorted data: two-sum, three-sum's inner loop, container-most-water.",
             "O(n) time, O(1) space",
             "The input must be sorted, or the discard argument does not hold. If sorting "
             "it is allowed, say the total cost out loud: O(n log n), not O(n)."),
        _var("Opposite ends, both move unconditionally",
             "Swap and step both pointers every iteration; no decision.",
             "Reversing in place, palindrome checks.",
             "O(n) time, O(1) space",
             "`while (l < r)`, never `l <= r` — the second swaps the middle element with "
             "itself on odd lengths, which is harmless for a reverse and an infinite loop "
             "if you forget to advance."),
        _var("Same direction: read and write",
             "Both pointers start at 0; `read` advances always, `write` only when an "
             "element is kept.",
             "In-place filtering: move zeroes, remove duplicates, compaction.",
             "O(n) time, O(1) space",
             "`write <= read` always, which is what makes overwriting `a[write]` safe — "
             "you can only ever clobber something already read."),
        _var("Same direction: fast and slow",
             "One pointer moves k steps for every 1 the other takes.",
             "Cycle detection, middle of a list, k-th from the end.",
             "O(n) time, O(1) space",
             "This is the linked-list unit's core tool. On an array it is usually a "
             "fixed-offset gap, which is the same idea with k = 1."),
        _var("Two sequences, one pointer each",
             "Each pointer indexes a *different* array, and the smaller front element "
             "advances.",
             "Merging sorted arrays, intersection of sorted lists, merge sort's combine.",
             "O(n + m) time, O(1) extra if merging backwards",
             "Merging forwards into one of the inputs overwrites elements you have not "
             "read. Fill from the **back**, where the spare capacity is."),
        _var("Two pointers inside a sort-first loop",
             "Sort, fix one index with an outer loop, and converge the other two.",
             "Three-sum, four-sum, closest triple.",
             "O(n²) for three-sum, O(n³) for four",
             "Skipping duplicates is not an optimisation here, it is the deduplication — "
             "skip equal values at the fixed index *and* after each successful pair."),
    ],
    rewrites=[
        _rw("Pairs in a sorted array",
            """
// O(n²) — every pair, even though the array is sorted
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        if (a[i] + a[j] == target) return new int[]{ i, j };
return new int[]{ -1, -1 };
""",
            """
// O(n) — let the order do the searching
int l = 0, r = n - 1;
while (l < r) {
    int sum = a[l] + a[r];
    if (sum == target) return new int[]{ l, r };
    if (sum < target) l++;                    // a[r] was l's best partner
    else              r--;                    // a[l] was r's best partner
}
return new int[]{ -1, -1 };
""",
            "The two nested loops become one loop with two pointers walking towards each other.",
            """
The nested version never uses the fact that `a` is sorted — it would behave
identically on shuffled input. That is the tell: **an unused precondition is
almost always the speedup.**

Sorted order means `a[r]` is the largest value `l` can be paired with. So if
`a[l] + a[r]` is *already* too small, no pair containing `l` can reach the
target, and the entire row of the pair table for `l` is dead. One comparison
retires n candidates.

**No answer is lost**, and that is the part to say out loud: a pointer is only
moved past an index after a comparison proved that index cannot participate in
any solution. The loop ends when the range is empty, so a surviving pair would
have had to be inside it.

The trade against the hashing version is the interesting bit. Hashing is O(n)
on unsorted input and costs O(n) space; this is O(1) space but needs the sort.
Given unsorted input and a request for O(1) space, the honest answer is
O(n log n) total — and the original indices are gone.
""",
            ),
        _rw("Removing elements in place",
            """
// O(n²) — each removal shifts everything after it
for (int i = 0; i < list.size(); ) {
    if (list.get(i) == 0) list.remove(i);     // System.arraycopy of the tail
    else i++;
}
""",
            """
// O(n) — one read pointer, one write pointer
int write = 0;
for (int read = 0; read < n; read++)
    if (a[read] != 0) a[write++] = a[read];
while (write < n) a[write++] = 0;             // pad, if the shape demands it
""",
            "`remove(i)` in a loop becomes a second index that only advances on a keeper.",
            """
`ArrayList.remove(i)` is O(n) — it shifts every later element down one. Removing
k elements that way costs O(n·k), and the loop reads as linear.

The rewrite stops *deleting* and starts *rebuilding*: walk the array once and
copy each survivor to the next free slot. `write` advances only on a keeper, so
`write <= read` at all times — which is precisely what makes writing to
`a[write]` safe, because that cell has already been read.

This is the same two-pointer idea as the converging version with the geometry
changed: there, the pointers close in and the comparison discards; here they
move together and the gap between them is the elements removed so far.

Both versions keep the relative order of the survivors. If order does not
matter, there is a third form — swap with the last element and shrink — which
does fewer writes and is the right answer to "remove all occurrences, order
irrelevant".
""",
            ),
    ],
    build_it="""
### Write the four shapes from an empty file

Two pointers is muscle memory, and the only way to find out whether you have it
is to type them without looking. Set a timer for twenty minutes.

**1. Reverse in place.** Three lines. Then answer, without running it: what does
`while (l <= r)` do differently on an odd-length array? Why is it harmless
*here* and not in general?

**2. `partition(int[] a, int pivot)`** — rearrange so everything `< pivot`
comes before everything `>= pivot`, and return the boundary. This is the read/write
shape, and it is also quicksort's core; you will meet it again in the sorting
unit as `quickselect`.

Then extend it to the **Dutch national flag**: three regions (`< = >`) with
*three* pointers. Write down the invariant for each region before you code it —
this one is genuinely hard to get right by intuition, and easy with the
invariant written on paper.

**3. `merge(int[] a, int m, int[] b, int n)`** into `a`, which has room at the
end. Do it forwards first and watch it clobber; then do it backwards. The
backwards version is four lines and needs no extra array, and knowing *why* is
the point: the free space is at the back, so filling from the back never
overwrites unread input.

**4. `threeSum`.** Sort, fix `i`, converge `l` and `r`. The code is short; the
deduplication is what takes the time. Get it returning distinct triples without
using a `Set`, which means skipping equal values at `i` and after each hit.

**5. Prove one of them.** Take `container-most-water` and write three sentences:
the invariant, why moving the shorter line preserves it, and what the exit
condition gives you. If you cannot write the middle sentence, you have the code
and not the technique — and the middle sentence is the one an interviewer asks
for.
""",
    rungs=[
        _rung("Warm up", "One skeleton, walked from both ends.",
              ["reverse-string", "reverse-array-fn", "is-palindrome-fn"],
              {"reverse-string": "The swap loop. `l < r`, not `l <= r`."}),
        _rung("Core", "Convergence with a decision rule, and same-direction compaction.",
              ["move-zeroes", "two-sum-sorted", "merge-sorted-arrays"],
              {"two-sum-sorted": "Compare directly with `two-sum-indices` from the hashing unit — same question, opposite trade.",
               "merge-sorted-arrays": "Try merging from the back once you have it working forwards; that is the O(1)-space version."}),
        _rung("Variations", "A greedy convergence whose correctness needs an argument.",
              ["container-most-water"],
              {"container-most-water": "Write down why moving the shorter side is safe before you code it."}),
        _rung("Stretch", "The hardest thing two pointers do: two invariants at once.",
              ["trapping-rain-water"],
              {"trapping-rain-water": "Do it with two prefix-max arrays first (easier, O(n) space), then collapse it to two pointers."}),
    ],
    next_up="""
Converging pointers handle *pairs*. When the question is about a **contiguous
run** instead, the two pointers move the same way — and that is a window.
""",
)


# --- Unit 8 — Sliding window -------------------------------------------------

_unit(
    "sliding-window", "Sliding Window", "🪟", _S2,
    "Every contiguous-subarray question, in one pass.",
    weight=3,
    prereqs=["two-pointers", "hashing"],
    why="""
*"The longest substring with …"*, *"the smallest subarray such that …"*,
*"every window of size k"* — these all look like they need to examine every
subarray, which is O(n²) starts times O(n) work. They do not. Because the
windows overlap almost completely, the answer for one window is the answer for
the last one with **one element added and maybe a few removed**.

That reuse is the whole technique, and it turns a cubic brute force into a
single pass.
""",
    model="""
### The one template

```java
int l = 0;
for (int r = 0; r < n; r++) {
    add(a[r]);                       // extend the window to the right
    while (windowIsInvalid()) {
        remove(a[l++]);              // shrink from the left until it is valid again
    }
    best = Math.max(best, r - l + 1);   // every window here is valid
}
```

Four things to fill in, and they are the whole design:

1. **What state does the window carry?** A count, a sum, a frequency map.
2. **What makes it invalid?** A duplicate, a sum over the limit, too many
   distinct values.
3. **When is the answer recorded?** After shrinking, for a *longest* question;
   inside the shrink loop, for a *shortest* one.
4. **Can the left pointer ever move backwards?** If yes, this is not a sliding
   window.

### Why it is O(n), not O(n²)

The `while` inside the `for` looks quadratic but is not: `l` only ever
increases, and it can increase at most n times in total across the whole run.
That argument — *amortised, because each element enters and leaves the window
exactly once* — is the one to say aloud in an interview.

### Fixed versus variable windows

**Fixed size k**: no `while`. Add the entering element, remove the leaving one,
record after the window is full.

```java
for (int r = 0; r < n; r++) {
    sum += a[r];
    if (r >= k) sum -= a[r - k];
    if (r >= k - 1) best = Math.max(best, sum);
}
```

**Variable size**: the `while` shrinks until valid. Longest asks for the biggest
valid window; shortest asks for the smallest, and records inside the shrink.

### The limit

Sliding window needs the property that **extending can only make things worse
and shrinking can only make them better** (monotonicity). With negative numbers
in a sum problem that breaks — adding an element can *reduce* the sum — and the
technique is simply wrong. That is when prefix sums with a hash map take over.
""",
    signals=[
        _sig("“contiguous”, “substring”, “subarray”", "A window",
             "Contiguity is the precondition — a subsequence is a different problem."),
        _sig("“longest … such that”", "Expand always, shrink while invalid, record after",
             "The answer is the largest window that is still valid."),
        _sig("“shortest / minimum window such that”", "Record inside the shrink loop",
             "You want the smallest valid window, found as you contract."),
        _sig("“every window of size k”, “average of k”", "Fixed window",
             "Add one, remove one; no `while` needed."),
        _sig("“at most k distinct / k replacements”", "Map or counter as window state",
             "The constraint is the invalidity test."),
        _sig("“maximum / minimum of every window of size k”", "A monotonic deque",
             "The window is easy; keeping its extreme in O(1) needs the queues unit."),
        _sig("Contiguous sums with NEGATIVE values", "Prefix sums + hash map",
             "Growing a window can shrink the sum, so shrinking is not monotone."),
    ],
    skeletons=[
        _sk("Variable window — longest",
            "Longest substring without repeats, longest with at most k distinct.",
            """
Map<Character, Integer> count = new HashMap<>();
int l = 0, best = 0;
for (int r = 0; r < s.length(); r++) {
    count.merge(s.charAt(r), 1, Integer::sum);
    while (count.get(s.charAt(r)) > 1) {          // invalid: a duplicate
        char c = s.charAt(l++);
        if (count.merge(c, -1, Integer::sum) == 0) count.remove(c);
    }
    best = Math.max(best, r - l + 1);
}
""",
            "Record AFTER the shrink — inside it the window is still invalid."),
        _sk("Variable window — shortest",
            "Minimum window substring, smallest subarray with sum ≥ target.",
            """
int l = 0, best = Integer.MAX_VALUE;
for (int r = 0; r < n; r++) {
    add(a[r]);
    while (valid()) {                     // note: shrink while VALID
        best = Math.min(best, r - l + 1);
        remove(a[l++]);
    }
}
""",
            "The mirror image of the longest template: the loop condition flips."),
        _sk("Fixed window of size k",
            "Rolling averages, maximum sum of k consecutive elements.",
            """
long sum = 0, best = Long.MIN_VALUE;
for (int r = 0; r < n; r++) {
    sum += a[r];
    if (r >= k) sum -= a[r - k];          // the element leaving
    if (r >= k - 1) best = Math.max(best, sum);
}
""",
            "Off-by-one central: `r >= k` removes, `r >= k - 1` records."),
    ],
    costs=[
        _cost("Variable window", "O(n)", "O(k)",
              "Each element enters and leaves once — amortised, despite the nested `while`."),
        _cost("Fixed window", "O(n)", "O(1)", "Pure add-one / remove-one."),
        _cost("Window with a frequency map", "O(n)", "O(alphabet)",
              "O(1) space when the alphabet is fixed, e.g. `int[128]`."),
        _cost("Brute force over all subarrays", "O(n²) or O(n³)", "O(1)",
              "What the window replaces."),
    ],
    pitfalls=[
        _pit("The answer is one too large or one too small",
             "Window length is `r - l + 1`, not `r - l`.",
             "Check it on a single-element window: `l == r` must give 1."),
        _pit("The longest answer includes an invalid window",
             "`best` was updated before the shrink loop ran.",
             "For *longest*, record after shrinking; for *shortest*, record inside."),
        _pit("The map keeps keys with a count of zero",
             "Decrementing without removing leaves stale keys, so `map.size()` "
             "over-reports the distinct count.",
             "Remove the key when its count hits 0, or compare counts rather than sizes."),
        _pit("Infinite loop in the shrink",
             "`l` is not incremented on some path inside the `while`.",
             "The shrink body must always advance `l`."),
        _pit("Correct on positives, wrong with negative numbers",
             "Sliding window assumes growth is monotone; negatives break that.",
             "Switch to prefix sums with a hash map of earlier prefix values."),
    ],
    lessons=["sliding_window", "alg_sliding_window"],
    checks=[
        _chk("Why is the nested `while` still O(n) overall?",
             "`l` never decreases and is bounded by n, so across the entire run the shrink "
             "loop executes at most n times in total. Each element enters and leaves once."),
        _chk("Where do you record the answer for *longest* versus *shortest*?",
             "Longest: after the shrink, when the window is valid again. Shortest: inside "
             "the shrink, while it is still valid and getting smaller."),
        _chk("Why does a sliding window fail for “subarray summing to k” with negatives?",
             "Extending the window can decrease the sum, so there is no monotone "
             "invalidity test to shrink on. Prefix sums plus a hash map handle it."),
        _chk("What is the window length when `l == r`?",
             "One — `r - l + 1`. Getting this wrong is the most common off-by-one in the "
             "whole pattern."),
        _chk("What property must the predicate have for a sliding window to work at all?",
             "Validity must survive **shrinking**: removing an element from a valid window "
             "must leave it valid. That is what guarantees the smallest valid start never "
             "moves left, which is what makes `lo` monotone and the whole loop O(n)."),
        _chk("Longest valid and shortest valid differ by exactly two edits. Which?",
             "The `while` condition is negated — shrink *while invalid* for longest, "
             "*while still valid* for shortest — and the measurement moves from after the "
             "loop to inside it, just before each removal. Swap one and not the other and you "
             "silently answer the other question."),
        _chk("Why can “exactly k distinct” not be done with one window?",
             "Because it is not preserved by shrinking: a window with exactly k distinct can "
             "drop to k − 1 when an element leaves, so the invariant fails and `lo` would "
             "need to move backwards. Express it as `atMost(k) − atMost(k-1)`, both of "
             "which are monotone."),
        _chk("In a fixed-size window, why guard the measurement with `hi >= k - 1`?",
             "Before that index the window holds fewer than k elements, so reporting its sum "
             "as a k-window's is simply wrong. It is not an optimisation — without it the "
             "first few answers are about windows that do not exist."),
        _chk("Why does a negative number break “smallest subarray with sum ≥ "
             "target”?",
             "Removing a negative *raises* the sum, so a shrunk window can become invalid and "
             "the smallest valid start is no longer monotone. The maintenance step is false, "
             "so the technique does not apply — prefix sums do."),
    ],
    interview="""
This pattern is asked by name, and the follow-up is always the complexity of
the nested loop. "O(n), because the left pointer only moves forward and each
element enters and leaves the window exactly once" is the answer being fished
for. Then be ready for *"what if there are negative numbers?"* — the honest
answer is that the window breaks and prefix sums take over.
""",
    invariant=_inv(
        "After index `hi` has been absorbed, `lo` is the **smallest** index for which "
        "the window `[lo, hi]` is still valid. Every shorter window ending at `hi` is "
        "valid too; every longer one is not.",
        "Before the first iteration the window `[0, -1]` is empty, and an empty window "
        "satisfies every predicate this technique can handle. So `lo = 0` is trivially "
        "the smallest valid start.",
        "This is the step the whole O(n) bound rests on, and it needs one property of "
        "the predicate: **validity survives shrinking**. “At most k distinct”, "
        "“no repeats”, “sum ≤ target with non-negative values” all "
        "have it; removing an element never makes such a window invalid.\n\n"
        "Given that, absorbing `a[hi + 1]` can only *break* validity, never restore it "
        "— so the new smallest valid start is at or to the **right** of the old one, "
        "and `lo` never has to move backwards. The `while` loop advances it exactly as "
        "far as it must, and stops at the first position where the window is valid "
        "again: the new minimum.",
        "Each index has served as the right edge exactly once, and for each one the "
        "longest valid window ending there was measured. Every window in the array ends "
        "*somewhere*, so the best window overall is among those measured — no "
        "candidate was skipped, despite never looking at more than two pointers.",
        "The cost argument falls straight out: `lo` and `hi` each move forward at most n "
        "times in total, so the nested `while` inside the `for` performs at most 2n "
        "pointer moves over the whole run. That is O(1) **amortized** per step, not "
        "O(n) — the same accounting as the monotonic stack in the cost unit.\n\n"
        "And it tells you exactly when the technique does not apply. Negative numbers "
        "break “sum ≤ target”, because removing a negative *raises* the sum "
        "and a shrunk window can be invalid. The maintenance step is then false, `lo` "
        "would need to move left, and the answer is prefix sums instead.",
    ),
    variants=[
        _var("Fixed width k",
             "No shrink loop at all: add the entrant, remove the leaver, every step.",
             "“maximum/average sum of every window of size k”.",
             "O(n) time, O(1) or O(k) space",
             "Only start *measuring* once the window is full (`hi >= k - 1`). Measuring "
             "from the first index reports a short window's total as if it were a full "
             "one, and the answer is right on almost every test."),
        _var("Longest valid",
             "Shrink **while invalid**; measure **after** the shrink loop.",
             "“longest substring with at most k distinct”, “no repeated "
             "characters”.",
             "O(n) time, O(k) space",
             "The measurement belongs after the `while`, where the window is valid again. "
             "Inside it, you are measuring windows you have already rejected."),
        _var("Shortest valid",
             "Shrink **while still valid**; measure **inside** the shrink loop, just "
             "before each removal.",
             "“smallest subarray with sum ≥ target”, “minimum window "
             "containing all of t”.",
             "O(n) time, O(k) space",
             "This is the same eight lines as *longest* with the `while` condition negated "
             "and the measurement moved one line. Getting the pair the wrong way round "
             "silently answers the other question — the most expensive confusion in "
             "this unit."),
        _var("Exactly k",
             "Run the *at most k* window twice: `atMost(k) - atMost(k - 1)`.",
             "“count subarrays with exactly k distinct values”, “exactly k "
             "odd numbers”.",
             "O(n) time, two passes",
             "There is no single window for “exactly”, and it is worth knowing "
             "*why*: the predicate is not preserved by shrinking, so the invariant above "
             "fails outright. Expressing it as a difference of two predicates that *are* "
             "monotone is the only fix."),
        _var("Count every valid window",
             "Instead of tracking a best, add `hi - lo + 1` after each shrink.",
             "“how many subarrays satisfy …” rather than “what is the "
             "longest”.",
             "O(n) time",
             "`hi - lo + 1` counts exactly the valid windows **ending at hi** — one "
             "per legal start. Adding 1 instead counts only the longest and quietly "
             "under-reports."),
        _var("Window with a monotonic deque",
             "The summary is a max or min, so a counter cannot maintain it.",
             "“maximum of every window of size k”, bounded-difference windows.",
             "O(n) time, O(k) space",
             "A sum can be *un-added* when an element leaves; a maximum cannot — you "
             "do not know what the second-largest was. That single asymmetry is the whole "
             "reason the deque exists. See the queues unit."),
        _var("Window over two structures at once",
             "Two counters: what the window holds, and how much of the requirement it has "
             "met.",
             "“minimum window containing every character of t”.",
             "O(n + m) time, O(alphabet) space",
             "Keep a scalar `formed` counting *satisfied requirements*, not a map "
             "comparison. Re-comparing two maps on every step turns an O(n) loop into "
             "O(n · alphabet)."),
    ],
    rewrites=[
        _rw("Recomputing the window every step",
            """
// O(n·k) — re-add all k elements at every start
long best = Long.MIN_VALUE;
for (int start = 0; start + k <= n; start++) {
    long sum = 0;
    for (int i = start; i < start + k; i++) sum += a[i];   // k reads, every time
    best = Math.max(best, sum);
}
return best;
""",
            """
// O(n) — the window is updated, not rebuilt
long sum = 0, best = Long.MIN_VALUE;
for (int hi = 0; hi < n; hi++) {
    sum += a[hi];                                 // what entered
    if (hi >= k) sum -= a[hi - k];                // what left
    if (hi >= k - 1) best = Math.max(best, sum);  // only once it is full
}
return best;
""",
            "The inner loop becomes two lines: one add for the entrant, one subtract for the leaver.",
            """
Consecutive windows overlap in `k - 1` elements. The slow version re-reads every
one of them, which is the exact re-scanning this whole stage exists to delete.

The rewrite keeps a **running summary** of the window and repairs it by the
difference between neighbouring windows: one element joined, one element left.
Two operations per step instead of k, whatever k is — the cost stops depending
on the window width entirely.

The precondition is that the summary is **invertible**: you must be able to undo
the leaver's contribution without rescanning. Sums and counts are; a maximum is
not, and that is exactly the case that needs a monotonic deque instead.

`if (hi >= k - 1)` is not an optimisation — before that point the window is
short, and reporting its sum as a k-window's is simply wrong.
""",
            ),
        _rw("Rescanning to summarise the window",
            """
// O(n²) — count distinct characters by walking the window
int best = 0;
for (int lo = 0; lo < n; lo++)
    for (int hi = lo; hi < n; hi++) {
        Set<Character> seen = new HashSet<>();
        for (int i = lo; i <= hi; i++) seen.add(s.charAt(i));   // O(n) inside O(n²)
        if (seen.size() <= k) best = Math.max(best, hi - lo + 1);
    }
return best;
""",
            """
// O(n) — one frequency map, repaired as the edges move
Map<Character, Integer> freq = new HashMap<>();
int lo = 0, best = 0;
for (int hi = 0; hi < n; hi++) {
    freq.merge(s.charAt(hi), 1, Integer::sum);
    while (freq.size() > k) {                          // shrink while INVALID
        char out = s.charAt(lo++);
        if (freq.merge(out, -1, Integer::sum) == 0) freq.remove(out);
    }
    best = Math.max(best, hi - lo + 1);                // measure once valid
}
return best;
""",
            "Three nested loops become one, with a frequency map carried across iterations.",
            """
Two separate wastes are being deleted here, and it is worth naming both.

**The summary is rebuilt from scratch** — that is the innermost loop, and the
fix is the same as the previous rewrite: repair it incrementally instead.

**Every start index is tried** — that is the outer loop, and the fix is the
invariant. Because validity survives shrinking, the smallest valid `lo` for
`hi + 1` is never to the left of the one for `hi`, so `lo` never rewinds. Most
of the O(n²) starts are not merely re-checked, they are *provably* not worth
checking.

The one line that is easy to get wrong is `freq.remove(out)` when a count hits
zero. Without it, `freq.size()` counts characters that are no longer in the
window, the shrink loop over-shrinks, and the answer comes out too small — on
long inputs only.

`while`, not `if`: absorbing one character can require several removals when the
window is full of singletons.
""",
            ),
    ],
    build_it="""
### One template, four shapes

Write the template once and then derive the rest by editing it. That derivation
is the unit; the code is nine lines.

**1. The template.**

```java
int lo = 0;
for (int hi = 0; hi < n; hi++) {
    absorb(a[hi]);
    while (/* window is invalid */) release(a[lo++]);
    // measure here
}
```

**2. `longestAtMostKDistinct(String s, int k)`.** Fill in `absorb`, `release` and
the condition with a frequency map. Delete the zero-count entries or `size()`
lies to you.

**3. `shortestSumAtLeast(int[] a, int target)`.** Change **two things**: negate
the `while` condition (shrink while *still valid*) and move the measurement
inside the loop, just before the release. Diff the two methods afterwards — if
the diff is bigger than those two edits, one of them is doing something it
should not.

**4. `countExactlyKDistinct`.** Write `countAtMost(s, k)` — same template,
accumulating `hi - lo + 1` instead of a maximum — and then return
`countAtMost(k) - countAtMost(k - 1)`. Check it against a brute-force triple
loop on every string of length ≤ 8 over the alphabet `{a, b, c}`. That sweep
takes ten lines and finds every off-by-one you have.

**5. `maxOfEveryWindow(int[] a, int k)` with a deque.** Try it first with a
plain `int max` and watch it fail: when the maximum leaves the window there is
nothing to fall back to. Then keep a deque of **indices** with decreasing
values. This is the shape the queues unit builds on.

**6. Break the invariant on purpose.** Run `shortestSumAtLeast` on an array
containing a negative number and find an input where it returns the wrong
answer. Then write the sentence that explains it — "removing a negative raises
the sum, so a shrunk window can be invalid, so `lo` would need to move left".
Being able to say *when a technique does not apply* is worth more than another
problem solved with it.
""",
    rungs=[
        _rung("Warm up", "The slide itself, with nothing else attached.",
              ["fixed-window-max-sum", "window-covering-letters"],
              {"fixed-window-max-sum": "The fixed window: add what entered, subtract what left. Two reads per step no matter how wide `k` is.",
               "window-covering-letters": "The variable right edge, with the left edge nailed to 0 — so the only new idea is maintaining a summary of what the window holds."}),
        _rung("Core", "The four window shapes — longest valid, shortest valid, and count them all.",
              ["longest-unique-substring", "longest-k-distinct", "min-window-sum-atleast",
               "subarray-sum-at-most"],
              {"longest-unique-substring": "The template problem. Type it from memory, then check where you recorded `best`.",
               "longest-k-distinct": "Grow, then repair: extend the right edge unconditionally and shrink only to restore the invariant. Remove zero counts from the map or `size()` stops meaning anything.",
               "min-window-sum-atleast": "The mirror image — shrink while the window is *still valid*, and record inside the shrink. Getting this pair backwards is the unit's most common bug.",
               "subarray-sum-at-most": "Counting all valid windows rather than finding one, which is the shape people never think to look for: `r - left + 1` per step."}),
        _rung("Variations", "A construction problem that turns out to be a window with a budget.",
              ["longest-ones-k-flips"],
              {"longest-ones-k-flips": "Nothing in the code decides *which* zeros to flip — the budget becomes the window invariant and the choices disappear. That reframing is the skill."}),
        _rung("Stretch", "A window whose validity test needs two counters.",
              ["min-window-length"],
              {"min-window-length": "The *shortest* variant, so the answer is recorded inside the shrink. Track “how many required characters are satisfied” as a single int rather than comparing whole maps."}),
    ],
    next_up="""
Windows handle contiguous runs you can grow and shrink. When the ranges are
arbitrary — or the values can be negative — you precompute instead.
""",
)


# --- Unit 9 — Prefix sums ----------------------------------------------------

_unit(
    "prefix-sums", "Prefix Sums", "➕", _S2,
    "Precompute once, answer any range in O(1).",
    weight=2,
    prereqs=["arrays-first-pass", "hashing"],
    why="""
Answering *"what is the sum of `a[l..r]`?"* by looping costs O(n), and a problem
that asks it many times is quietly quadratic. One preprocessing pass fixes it
permanently: store the running total, and every range sum becomes a single
subtraction.

The pattern then generalises past sums in two directions that are worth far more
than the base case: **prefix + hash map** solves subarray-sum counting with
negative numbers (where sliding window fails), and the same difference trick
run over a timeline is how every *"how many are active at once?"* problem is
solved.
""",
    model="""
### The identity

With `pre[i]` = sum of the first `i` elements (`pre[0] = 0`):

```
sum(a[l..r]) = pre[r + 1] − pre[l]
```

The `+1` offset and `pre[0] = 0` exist so that ranges starting at index 0 need
no special case. Use an array of size `n + 1`; the off-by-ones disappear.

### Prefix + hash map

*"How many subarrays sum to k?"* becomes a **complement** question about prefix
values: a subarray ending at `r` sums to k exactly when some earlier prefix
equals `pre[r] − k`. So count prefix values as you go:

```java
Map<Long, Integer> seen = new HashMap<>();
seen.put(0L, 1);                    // the empty prefix
long run = 0; int count = 0;
for (int x : a) {
    run += x;
    count += seen.getOrDefault(run - k, 0);
    seen.merge(run, 1, Integer::sum);
}
```

`seen.put(0L, 1)` before the loop is what lets a subarray starting at index 0 be
counted. Forgetting it is the classic bug.

This works with negative numbers, which is exactly where sliding window gave up.

### Prefix products

Product-except-self is the same idea in two directions: a prefix product from
the left and a suffix product from the right, multiplied at each index. It
avoids division, which matters because the array may contain zeros.

### Difference arrays and sweeps

To apply *"add v to every index in [l, r]"* many times, do not touch the range.
Record `diff[l] += v` and `diff[r + 1] -= v`, then take the prefix sum once at
the end: k updates become O(k + n) instead of O(k · n).

The same idea run over events (`+1` at a start, `−1` at an end, processed in
time order) answers *"the maximum number of things active at once"* — which is
the whole intervals unit in embryo.
""",
    signals=[
        _sig("“sum of the range l..r”, many queries", "Prefix array",
             "One pass up front, then O(1) per query."),
        _sig("“how many subarrays sum to k” with negatives", "Prefix + hash map",
             "Sliding window is invalid; prefix complements are not."),
        _sig("“product of all except self”, no division", "Prefix and suffix products",
             "Two passes, no division, survives zeros."),
        _sig("“add v to a range”, repeated", "Difference array",
             "Mark the endpoints, prefix-sum once at the end."),
        _sig("“maximum simultaneous …”, boarding and leaving", "Sweep of ±1 events",
             "The running total at any moment is the answer."),
        _sig("Running total requested per index", "Prefix array is literally the answer",
             "No subtraction needed."),
    ],
    skeletons=[
        _sk("Build and query",
            "Repeated range-sum questions.",
            """
long[] pre = new long[n + 1];
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];

// sum of a[l..r] inclusive:
long s = pre[r + 1] - pre[l];
""",
            "Size `n + 1` with `pre[0] = 0` removes every special case."),
        _sk("Count subarrays with a given sum",
            "Works with negative values, where a window cannot.",
            """
Map<Long, Integer> seen = new HashMap<>();
seen.put(0L, 1);                       // empty prefix — do not omit
long run = 0; int count = 0;
for (int x : a) {
    run += x;
    count += seen.getOrDefault(run - k, 0);
    seen.merge(run, 1, Integer::sum);
}
""",
            "The complement trick from the hashing unit, applied to prefixes."),
        _sk("Prefix × suffix",
            "Product (or max, or gcd) of everything except index i.",
            """
int[] res = new int[n];
int pre = 1;
for (int i = 0; i < n; i++) { res[i] = pre; pre *= a[i]; }
int suf = 1;
for (int i = n - 1; i >= 0; i--) { res[i] *= suf; suf *= a[i]; }
""",
            "No division, so a zero anywhere in the array is handled for free."),
        _sk("Difference array / sweep",
            "Many range updates, or “how many are active at once”.",
            """
int[] diff = new int[n + 1];
for (int[] u : updates) { diff[u[0]] += u[2]; diff[u[1] + 1] -= u[2]; }
int cur = 0, best = 0;
for (int i = 0; i < n; i++) { cur += diff[i]; best = Math.max(best, cur); }
""",
            "`diff[r + 1]` is why the array has n + 1 slots."),
    ],
    costs=[
        _cost("Build prefix array", "O(n)", "O(n)", "One pass."),
        _cost("Range-sum query", "O(1)", "—", "A single subtraction."),
        _cost("Prefix + hash map counting", "O(n)", "O(n)", "One pass, one map."),
        _cost("k range updates via difference array", "O(k + n)", "O(n)",
              "Versus O(k · n) if each range is touched directly."),
        _cost("Naive repeated range sums", "O(q · n)", "O(1)", "What the prefix replaces."),
    ],
    pitfalls=[
        _pit("Every range sum is off by one element",
             "The `pre[r + 1] - pre[l]` offset was written as `pre[r] - pre[l]`.",
             "Verify on a length-1 range: `sum(a[i..i])` must equal `a[i]`."),
        _pit("Subarrays starting at index 0 are never counted",
             "`seen.put(0, 1)` was omitted before the loop.",
             "Seed the map with the empty prefix."),
        _pit("The prefix sums overflow",
             "n values near 10⁹ sum well past `int` range even though each fits.",
             "Make the prefix array `long[]`."),
        _pit("Product-except-self breaks on zeros",
             "The solution divided the total product by `a[i]`.",
             "Use prefix × suffix products and never divide."),
        _pit("The sweep is one index short",
             "`diff` was allocated with n slots, so `diff[r + 1]` is out of bounds for the "
             "last range.",
             "Allocate `n + 1`."),
    ],
    lessons=["prefix_sum", "alg_prefix_sums"],
    checks=[
        _chk("Why does the prefix array have n + 1 entries?",
             "So `pre[0] = 0` represents the empty prefix, which makes ranges starting at "
             "index 0 obey the same formula as every other range."),
        _chk("Why seed the map with `(0 → 1)` when counting subarrays with sum k?",
             "A subarray that starts at index 0 needs the *empty* prefix as its left "
             "endpoint. Without the seed, every such subarray is missed."),
        _chk("Subarray sum = k, with negative numbers. Window or prefix?",
             "Prefix plus a hash map. The window relies on growth being monotone, and "
             "negatives break that assumption."),
        _chk("Why avoid division in product-except-self?",
             "A single zero makes division undefined, and two zeros make every answer zero. "
             "Prefix × suffix handles both without a special case."),
        _chk("Why is the prefix array `n + 1` long, with `prefix[0] = 0`?",
             "Because `prefix[0]` is the genuine aggregate of the empty prefix, not a "
             "placeholder. It is what makes `prefix[r+1] - prefix[l]` correct at `l = 0` with "
             "no special case — and the `if (l == 0)` that an n-length array needs is "
             "where the off-by-ones live."),
        _chk("Which aggregates can be prefix-summed, and which cannot?",
             "Any operation with an **inverse**, so a range can be recovered by undoing the "
             "prefix: sums, counts, XOR (its own inverse), products without zeros. Minimum "
             "cannot — there is nothing to subtract — which is why range-minimum "
             "needs a sparse table or a segment tree."),
        _chk("Why does the prefix-map version of “count subarrays summing to k” "
             "handle negatives when a sliding window cannot?",
             "Because it never assumes the running sum is monotone in the window's length. It "
             "pairs prefix indices by value, and that pairing is exact whatever the signs are; "
             "a window relies on shrinking being safe, which negatives break."),
        _chk("What does seeding the prefix map with `{0: 1}` buy?",
             "The subarrays that start at index 0. Their left prefix *is* the empty prefix, so "
             "without the seed the lookup for `run - k` never finds it. It is the single most "
             "common omission here, and most hand-written tests do not contain such a case."),
        _chk("Why does a difference array need `n + 1` slots?",
             "Because an update ending at the last index writes `diff[r + 1] = diff[n]`. Sizing "
             "it n forces an `if` around that write, and the `if` is the bug — the extra "
             "slot is simply never read back."),
    ],
    interview="""
Prefix sums are rarely the headline of a question — they are the step that makes
the headline tractable, which is why interviewers like them. The tell you are
expected to show is recognising that *"many range queries"* or *"count the
subarrays"* means preprocessing, and being able to say why the hash-map variant
survives negative numbers when a sliding window does not.
""",
    invariant=_inv(
        "`prefix[i]` is the aggregate of the first `i` elements — `a[0 … i-1]` — "
        "so `prefix[0]` is the aggregate of **nothing**, and the array has `n + 1` "
        "entries, not `n`.",
        "`prefix[0] = 0` is the identity of the operation (0 for sums, 1 for products, "
        "0 for XOR). It is not a placeholder: it is the genuine aggregate of the empty "
        "prefix, and every range starting at index 0 is computed against it.",
        "Each step appends exactly one element: `prefix[i + 1] = prefix[i] ⊕ a[i]`. "
        "The entry being written is always one past the one being read, so the array can "
        "be filled left to right in a single pass with no lookahead.",
        "Any range `[l, r]` is the difference of two prefixes: "
        "`prefix[r + 1] ⊖ prefix[l]`. Every range query becomes O(1), and — "
        "more importantly — *every subarray is now identified by a pair of prefix "
        "indices*, which is what lets a hash map count subarrays without enumerating "
        "them.",
        "The `n + 1` length and the leading identity are the same decision, and it is "
        "the one that removes the `if (l == 0)` special case. Off-by-one bugs in this "
        "unit are almost always a prefix array of length n with an `if` bolted on.\n\n"
        "The operation must have an **inverse** for the subtraction step. Sums, counts "
        "and XOR do (XOR is its own inverse). Minimum does not — there is nothing to "
        "subtract — which is why range-minimum needs a sparse table or a segment tree "
        "instead, and why that is a different unit.",
    ),
    variants=[
        _var("Prefix sum",
             "The aggregate is `+`; ranges come out by subtraction.",
             "Range sums, “total between l and r”, repeated queries on a fixed "
             "array.",
             "O(n) build, O(1) per query",
             "Use `long`. 10⁵ values of 10⁹ overflow an `int` prefix long before "
             "the end of the array, and the wrap is silent."),
        _var("Prefix XOR",
             "The aggregate is `^`, which is its own inverse.",
             "“XOR of a range”, subarrays XOR-ing to a target.",
             "O(n) build, O(1) per query",
             "`xor(l, r) = prefix[r+1] ^ prefix[l]` — the *same* operator does the "
             "combining and the undoing, so there is no minus sign anywhere."),
        _var("Prefix + hash map",
             "Do not store the array; store each prefix value in a map as you go.",
             "“how many subarrays sum to k”, “longest subarray summing to "
             "0”, equal counts of two symbols.",
             "O(n) time, O(n) space, one pass",
             "Seed the map with the empty prefix — `{0: 1}` to count, `{0: -1}` to "
             "measure a length. Without it you lose exactly the subarrays starting at "
             "index 0, which small tests rarely include."),
        _var("Prefix and suffix, together",
             "Two passes, one from each end, combined per index.",
             "Product of all except self, “best split point”, candy-style "
             "two-directional constraints.",
             "O(n) time, O(1) extra if written into the output",
             "This is what lets `product-except-self` avoid division and therefore survive "
             "a zero in the array. Division is the trap, not the optimisation."),
        _var("Difference array",
             "Invert it: record the *edges* of an update, then prefix-sum once at the end.",
             "“add v to every index in [l, r]” repeated q times; flight bookings.",
             "O(q + n) instead of O(q · n)",
             "`diff[r + 1] -= v` needs the array to have `n + 1` slots. Sizing it n and "
             "guarding with an `if` works and is how the off-by-one gets in."),
        _var("Sweep of ±1 events",
             "The “array” is a timeline; each interval contributes +1 at its "
             "start and −1 at its end.",
             "“maximum simultaneous …”, meeting rooms, peak occupancy.",
             "O(n log n), dominated by sorting the events",
             "Decide whether an event that ends exactly when another starts overlaps, and "
             "order the −1 before the +1 if it does not. That tie-break *is* the "
             "problem statement."),
        _var("2-D prefix sums",
             "The same idea on a grid, with inclusion–exclusion to undo the "
             "double-counted corner.",
             "Rectangle sums, “best k × k block”.",
             "O(r · c) build, O(1) per rectangle",
             "`P[r+1][c+1] = a + P[r][c+1] + P[r+1][c] - P[r][c]` — the subtraction is "
             "the overlap the two strips share. Forgetting it double-counts and the error "
             "grows with the rectangle."),
    ],
    rewrites=[
        _rw("Many range queries",
            """
int[] a;

void build(int[] input) { a = input; }            // nothing to precompute

// O(n) per query — re-add the range every time
long answer(int l, int r) {
    long sum = 0;
    for (int i = l; i <= r; i++) sum += a[i];
    return sum;
}
""",
            """
long[] prefix;

// O(n), paid once for the whole array
void build(int[] a) {
    prefix = new long[a.length + 1];              // n + 1, and prefix[0] = 0
    for (int i = 0; i < a.length; i++) prefix[i + 1] = prefix[i] + a[i];
}

// O(1) per query — one subtraction
long answer(int l, int r) { return prefix[r + 1] - prefix[l]; }
""",
            "The per-query loop is hoisted out and paid once, for the whole array.",
            """
Overlapping queries re-add the same elements. Rather than deleting the
re-reading inside one loop — which is what a window does — this pays for *all*
of it up front, once, and then every query is a subtraction.

The trade is explicit: O(n) extra memory buys O(1) queries. With one query it is
a loss; from about two onwards it wins, and at q = n it is the difference
between 10¹⁰ and 10⁵.

**The `n + 1` length is the whole ergonomic win.** With `prefix[0] = 0` meaning
"the sum of nothing", `l = 0` needs no special case — `prefix[r+1] - prefix[0]`
is already right. An n-length prefix array plus `if (l == 0)` computes the same
numbers and is where the off-by-ones live.

What breaks it is a single update: changing `a[i]` invalidates every prefix from
`i` on. Interleaved updates and queries are a Fenwick tree, in the optional
stage.
""",
            ),
        _rw("Counting subarrays with a given sum",
            """
// O(n²) — extend every start, one element at a time
int count = 0;
for (int lo = 0; lo < n; lo++) {
    long sum = 0;
    for (int hi = lo; hi < n; hi++) {
        sum += a[hi];
        if (sum == k) count++;
    }
}
return count;
""",
            """
// O(n) — every subarray is a PAIR of prefixes, so count the pairs
Map<Long, Integer> seen = new HashMap<>();
seen.put(0L, 1);                                  // the empty prefix
long sum = 0;
int count = 0;
for (int x : a) {
    sum += x;
    count += seen.getOrDefault(sum - k, 0);       // how many starts work?
    seen.merge(sum, 1, Integer::sum);
}
return count;
""",
            "The inner loop becomes a map lookup for the one prefix value that would close a subarray.",
            """
The subarray `(l, r]` sums to `k` exactly when
`prefix[r] - prefix[l] == k`, that is `prefix[l] == prefix[r] - k`. So at each
right edge there is only **one** prefix value worth having seen, and the inner
loop was searching for something it could have looked up.

This is the hashing unit's complement trick with prefix sums as the values, and
the pairing is exact: every subarray corresponds to exactly one ordered pair of
prefix indices, so counting qualifying pairs counts qualifying subarrays. The
query-before-insert order is the same invariant as there — it keeps `l < r`.

`seen.put(0L, 1)` is the empty prefix, and it is what counts subarrays that
start at index 0. Dropping that line loses exactly those, and most hand-written
tests do not contain one.

**Why not a sliding window?** A window needs validity to survive shrinking, and
with negative numbers it does not — the running sum is not monotone in the
window's length. Prefix sums never assume monotonicity, which is precisely why
this version handles negatives and the window version cannot.
""",
            ),
    ],
    build_it="""
### Build the family, and find the off-by-one before it finds you

**1. `prefix(int[] a)` returning `long[n + 1]`.** Then write
`rangeSum(l, r)` on top of it. Test `l = 0`, `l = r`, and `r = n - 1`
deliberately — those three cover every off-by-one this shape has.

Then write the n-length version with the `if (l == 0)` guard, and keep both
around. You will not use it, but having written it is why you will never argue
about which is cleaner.

**2. `productExceptSelf(int[] a)` without division.** Prefix products left to
right, suffix products right to left, multiply at each index. Then do it with
O(1) extra space by writing the prefixes into the output array and carrying the
suffix in a single variable. Test it on an array containing **two** zeros — the
division-based version cannot survive even one, and that is the point of the
exercise.

**3. `rangeAdd(int n, int[][] updates)`.** A difference array of length
`n + 1`, `+v` at `l` and `-v` at `r + 1`, one prefix pass at the end. Then
answer, on paper: why does the array need `n + 1` slots, and what exactly goes
wrong at `r = n - 1` if it does not have them?

**4. `countSubarraysSummingTo(int[] a, int k)`** with a prefix map. Check it
against the O(n²) double loop on a thousand random arrays of length ≤ 12 with
values in `[-3, 3]`. The negatives are the point — the sliding-window instinct
fails here and the random sweep is what proves it to you.

Then delete the `seen.put(0L, 1)` line and re-run the sweep. It will fail, and
the failing cases will all be subarrays starting at index 0.

**5. `maxSimultaneous(int[][] intervals)`** as a ±1 sweep. Run it twice: once
treating `[1, 5]` and `[5, 9]` as overlapping, once as not. Two sort comparators,
two different answers, and neither is more correct than the other — the
statement decides. Being able to *ask* which one is meant is the skill.

**6. 2-D prefix sums.** Build `P[r+1][c+1]` and answer rectangle queries with
inclusion–exclusion. Verify against a brute-force quadruple loop on every
rectangle of a random 6 × 6 grid. Getting the four-term formula right from
memory, with the signs in the right places, is the exercise.
""",
    rungs=[
        _rung("Warm up", "The running total, and a sweep over events.",
              ["running-sum", "bank-balance"],
              {"running-sum": "The prefix array is literally the required output."}),
        _rung("Core", "Two-directional prefixes, and the ±1 sweep.",
              ["product-except-self", "max-passengers"],
              {"product-except-self": "Solve it without division. That constraint is the entire problem.",
               "max-passengers": "A +1/−1 sweep. The same shape returns in the intervals unit as “minimum meeting rooms”."}),
        _rung("Stretch", "Prefix values as hash keys.",
              ["subarray-sum-k"],
              {"subarray-sum-k": "The hashing unit's complement trick, applied to prefix sums. Seed the map with 0 → 1."}),
    ],
    next_up="""
The array patterns are in place. Next, the same reasoning applied to text —
where the data structure is the same but the operations have their own costs.
""",
)


# --- Unit 10 — Strings -------------------------------------------------------

_unit(
    "strings", "Strings & Character Work", "🔤", _S2,
    "An array of characters, with an immutability tax.",
    weight=3,
    prereqs=["arrays-first-pass", "hashing"],
    why="""
Strings are arrays of characters, so every pattern in this stage applies
unchanged. What is new is **cost**: in Java a `String` is immutable, so every
`+=` allocates a whole new one. A loop that builds a string with `+=` is O(n²)
in total characters, and it is the most common accidental quadratic after
`list.contains`.

The other new thing is that characters are numbers. `c - 'a'` gives 0…25, which
turns letters into array indices — the trick behind every counting solution in
this unit.
""",
    model="""
### The costs that matter

| Operation | Cost | Note |
| --- | --- | --- |
| `charAt(i)` | O(1) | It is an array read |
| `length()` | O(1) | Stored, not counted |
| `substring(i, j)` | O(j − i) | **Copies** — it is not a view |
| `s + t` | O(\\|s\\| + \\|t\\|) | Allocates a new string every time |
| `StringBuilder.append` | O(1) amortised | The right tool for building |
| `equals` | O(n) | Compares content; `==` compares identity |

`substring` copying is why a naive *"check every substring"* loop is O(n³)
rather than O(n²) — the copy hides inside the comparison.

### Characters are numbers

```java
int idx = c - 'a';                    // 'a'..'z' → 0..25
char back = (char) ('a' + idx);
boolean isDigit = c >= '0' && c <= '9';
```

That mapping gives you an O(1)-space frequency table for any lowercase problem —
`int[26]` — which is faster and clearer than a `HashMap<Character, Integer>`.

### Building output

```java
StringBuilder sb = new StringBuilder();
for (...) sb.append(x);
System.out.println(sb);
```

Build once, print once. Printing inside a loop with `println` is also slow, for
the same underlying reason — each call flushes.

### Canonical forms, again

Anagrams, case-insensitive comparison and "ignore punctuation" are all the same
move: reduce each string to a canonical form and compare *those*. That is the
hashing unit's idea, and text is where it earns its keep.

### Palindromes: expand around a centre

Every palindrome has a centre, and growing outwards from it meets every
palindrome with that centre, shortest first — each one confirmed in O(1), because
the inner part was confirmed one step earlier. There are **2n − 1** centres: each
character (odd lengths) and each gap between neighbours (even lengths).

```java
for (int c = 0; c < 2 * n - 1; c++) {
    int l = c / 2, r = l + c % 2;              // even c: a letter; odd c: a gap
    while (l >= 0 && r < n && s.charAt(l) == s.charAt(r)) { /* s[l..r] is a palindrome */ l--; r++; }
}
```

O(n²) in total, O(1) memory — versus O(n³) for checking every substring. Count
inside the loop for *how many*; keep the widest for *the longest*.

### Matching: the KMP prefix function

Searching for a pattern by restarting after every mismatch is O(n·m). But after
matching k characters, the text's last k characters *are* the pattern's first k,
so a mismatch need not throw them away.

`pi[i]` = the length of the longest proper prefix of `t[0..i]` that is also a
suffix of it (a **border**). On a mismatch, fall back to the next shorter border,
`k = pi[k − 1]`, instead of to 0:

```java
int[] pi = new int[m];
for (int i = 1, k = 0; i < m; i++) {                 // the pattern against itself
    while (k > 0 && t.charAt(i) != t.charAt(k)) k = pi[k - 1];
    if (t.charAt(i) == t.charAt(k)) k++;
    pi[i] = k;
}
for (int i = 0, k = 0; i < n; i++) {                 // the pattern against the text
    while (k > 0 && s.charAt(i) != t.charAt(k)) k = pi[k - 1];
    if (s.charAt(i) == t.charAt(k)) k++;
    if (k == m) return i - m + 1;                     // or count, and set k = pi[k - 1]
}
```

The text pointer never moves back, and `k` falls at most as often as it rose, so
the search is O(n + m). The same array answers questions about one string:
`pi[n − 1]` is its longest border (*longest happy prefix*), and running it on
`s + "#" + reverse(s)` finds the longest palindromic prefix (*shortest
palindrome*).
""",
    signals=[
        _sig("“count the …” over characters", "`int[26]` or `int[128]` frequency array",
             "Letters are indices; no map needed."),
        _sig("“build the result string”", "`StringBuilder`",
             "`+=` in a loop is quadratic."),
        _sig("“is it a palindrome?”", "Two pointers over `charAt`",
             "No copying, O(1) space."),
        _sig("“same letters”, “anagram”", "Sorted characters or a count signature",
             "Canonical form, then compare or hash."),
        _sig("“run-length”, “consecutive equal characters”", "One pass with a run counter",
             "Extend-or-reset, from the arrays unit."),
        _sig("“palindromic substrings”, “longest palindrome inside”", "Expand around 2n − 1 centres",
             "O(n²) time, O(1) memory — no table needed."),
        _sig("“find the pattern”, “first occurrence”, n and m large", "KMP prefix function",
             "O(n + m); the text pointer never moves back."),
        _sig("“longest prefix that is also a suffix”", "`pi[n − 1]`",
             "The prefix function of the string itself."),
        _sig("“words”, “split on spaces”", "One pass counting transitions, or `split`",
             "Beware of repeated and leading spaces when counting manually."),
    ],
    skeletons=[
        _sk("Character frequency",
            "Anagrams, unique characters, counting letters.",
            """
int[] freq = new int[26];
for (char c : s.toCharArray()) freq[c - 'a']++;
""",
            "Use `int[128]` when the input is not guaranteed lowercase ASCII letters."),
        _sk("Build with StringBuilder",
            "Any output longer than a single value.",
            """
StringBuilder sb = new StringBuilder();
for (int i = 0; i < n; i++) {
    sb.append(part(i));
    if (i + 1 < n) sb.append(' ');
}
System.out.println(sb);
""",
            "One allocation, one print — instead of n of each."),
        _sk("Run-length scan",
            "Compression, longest run of a character, grouping neighbours.",
            """
for (int i = 0; i < s.length(); ) {
    int j = i;
    while (j < s.length() && s.charAt(j) == s.charAt(i)) j++;
    sb.append(s.charAt(i)).append(j - i);   // the run [i, j)
    i = j;
}
""",
            "The outer `for` has no increment — the inner loop is what advances `i`."),
        _sk("Vertical scan for a common prefix",
            "Longest common prefix across many strings.",
            """
for (int i = 0; i < first.length(); i++) {
    char c = first.charAt(i);
    for (String w : words)
        if (i == w.length() || w.charAt(i) != c)
            return first.substring(0, i);
}
return first;
""",
            "Compare column by column; stop at the first disagreement."),
        _sk("Expand around centre",
            "Count palindromic substrings, or find the longest.",
            """
int bestStart = 0, bestLen = 0;
for (int c = 0; c < 2 * n - 1; c++) {
    int l = c / 2, r = l + c % 2;
    while (l >= 0 && r < n && s.charAt(l) == s.charAt(r)) { l--; r++; }
    if (r - l - 1 > bestLen) { bestLen = r - l - 1; bestStart = l + 1; }
}
return s.substring(bestStart, bestStart + bestLen);
""",
            "After the loop, `l` and `r` are one step past the palindrome: its length is r − l − 1."),
        _sk("KMP search",
            "First (or every) occurrence of a pattern in O(n + m).",
            """
int[] pi = new int[m];
for (int i = 1, k = 0; i < m; i++) {
    while (k > 0 && t.charAt(i) != t.charAt(k)) k = pi[k - 1];
    if (t.charAt(i) == t.charAt(k)) k++;
    pi[i] = k;
}
for (int i = 0, k = 0; i < n; i++) {
    while (k > 0 && s.charAt(i) != t.charAt(k)) k = pi[k - 1];
    if (s.charAt(i) == t.charAt(k)) k++;
    if (k == m) return i - m + 1;
}
return -1;
""",
            "Building `pi` is the same loop as searching — the pattern matched against itself."),
    ],
    costs=[
        _cost("One pass over characters", "O(n)", "O(1)", "With an `int[26]` counter."),
        _cost("Sorting a string's characters", "O(n log n)", "O(n)",
              "The canonical form for anagram grouping — count signatures are O(n)."),
        _cost("Building with `+=` in a loop", "O(n²)", "O(n²) churn", "The bug. Use `StringBuilder`."),
        _cost("`substring(i, j)`", "O(j − i)", "O(j − i)", "A copy, not a view."),
        _cost("Expand around every centre", "O(n²)", "O(1)", "Checking every substring separately is O(n³)."),
        _cost("KMP search", "O(n + m)", "O(m)", "Naive restart-on-mismatch is O(n · m)."),
    ],
    pitfalls=[
        _pit("String building is inexplicably slow on large input",
             "`s += x` inside a loop allocates and copies the whole string each iteration.",
             "Use `StringBuilder` and convert once at the end."),
        _pit("`ArrayIndexOutOfBoundsException` in a frequency array",
             "`c - 'a'` on an uppercase letter, a digit or a space gives a negative or "
             "out-of-range index.",
             "Use `int[128]` indexed by the raw char, or normalise the case first."),
        _pit("Two identical-looking strings compare as different",
             "`==` compares references. Literals may be interned, which makes it work "
             "sometimes — the worst possible failure mode.",
             "Always `equals`."),
        _pit("The word count is one too high",
             "Splitting on a single space counts empty tokens from repeated or leading spaces.",
             "Count transitions from space to non-space, or split on `\\s+` after trimming."),
        _pit("A substring comparison loop is O(n³)",
             "Each `substring` call copies before the comparison even starts.",
             "Compare with `charAt` in place, or use indices rather than copies."),
        _pit("Even-length palindromes are missing",
             "Only the n letters were used as centres, not the n − 1 gaps.",
             "Loop over 2n − 1 centres: `l = c / 2, r = l + c % 2`."),
        _pit("KMP is still O(n · m), or misses overlapping matches",
             "On a mismatch `k` was reset to 0, or after a full match it was not set to `pi[k − 1]`.",
             "Fall back through `pi`; after a match continue from `k = pi[m − 1]`."),
    ],
    lessons=["string_basics", "canonical", "char_arrays"],
    checks=[
        _chk("Why is `result += c` inside a loop O(n²)?",
             "`String` is immutable, so each `+=` allocates a new string and copies "
             "everything built so far. Summed over n iterations that is quadratic."),
        _chk("What does `c - 'a'` give you, and when is it wrong?",
             "The 0-based index of a lowercase letter. It is wrong — silently negative or "
             "too large — for uppercase letters, digits, spaces or punctuation."),
        _chk("Is `s.substring(i, j)` O(1)?",
             "No. Modern Java copies the range, so it is O(j − i). A loop of substrings is "
             "a hidden extra factor of n."),
        _chk("Two ways to test whether two words are anagrams — and their costs?",
             "Sort both and compare: O(n log n). Count characters into `int[26]` and compare "
             "the tables: O(n). The second is preferred and also generalises to grouping."),
        _chk("Why are there 2n − 1 centres for palindromes, not n?",
             "Odd-length palindromes centre on a letter; even-length ones centre on the gap "
             "between two letters. n letters plus n − 1 gaps."),
        _chk("What does the KMP prefix function store, and why does it make the search linear?",
             "pi[i] is the longest proper prefix of t[0..i] that is also its suffix. On a "
             "mismatch the search falls back to that border instead of restarting, so the text "
             "pointer never moves back and k falls at most as often as it rose."),
        _chk("Why does expanding around centres use `2m - 1` centres and not m?",
             "Because an even-length palindrome is symmetric about the **gap** between two "
             "characters, not about a character. Expanding only from characters finds `aba` "
             "and misses `abba` — and the bug produces correct answers on every "
             "odd-length example."),
        _chk("`s.substring(i, i + m).equals(t)` versus `s.regionMatches(i, t, 0, m)` — "
             "what changes?",
             "Not the complexity: both are O(n·m) in the worst case. `substring` **copies** "
             "m characters on every iteration and then throws them away; `regionMatches` "
             "compares in place. The habit worth building is asking whether you need the "
             "substring or only need to compare it."),
        _chk("Why is summing character codes a bad key for grouping anagrams?",
             "It is not injective: `ad` and `bc` both sum to 199, so they would be grouped "
             "together. A canonical key has to be collision-free by construction — sort "
             "the characters, or use a 26-slot count signature."),
        _chk("Why does the run-length scan's outer `for` have an empty increment clause?",
             "Because the inner loop is what advances the index, past the whole run. Leaving "
             "`i++` in as well skips the first character of every run after the first, and the "
             "output is wrong only where runs repeat."),
    ],
    interview="""
String questions are rarely about strings — they are array questions wearing a
costume, plus one Java-specific trap the interviewer is watching for. Reaching
for `StringBuilder` unprompted, and saying "`substring` copies, so I will
compare in place", both register as production instincts rather than
competitive-programming ones.
""",
    internals="""
### What a Java `String` actually is

A `String` wraps a private byte array and a coder flag, and it is **immutable** —
there is no method on it that changes it. Everything that looks like a mutation
returns a new object:

```java
s.toUpperCase();      // a new String; `s` is untouched
s.trim();             // a new String
s + "x";              // a new String, and a new StringBuilder behind the scenes
```

Immutability buys thread safety, safe use as a `HashMap` key, and a cached hash
code. It costs a copy on every edit, and that cost is where nearly every
string-performance bug in this unit comes from.

### `substring` copies. It did not always.

Before Java 7, `substring` returned a view sharing the original array — O(1),
and a 10-character substring of a 10 MB string kept all 10 MB alive. That leak
was judged worse than the copy, so since Java 7 `substring` **allocates and
copies**:

| Call | Cost |
| --- | --- |
| `s.charAt(i)` | O(1), no allocation |
| `s.substring(i, j)` | O(j − i) time **and** O(j − i) memory |
| `s.regionMatches(i, t, 0, m)` | O(m) time, **no** allocation |
| `s.equals(t)` | O(m), with a length check first |

So a loop that takes a substring per iteration is allocating per iteration, and
the allocation does not show up as a nested loop in the source.

### Why `+=` in a loop is quadratic

`a + b` compiles to a `StringBuilder` — one *per expression*, not per loop. So
`out += part` inside a loop allocates a builder, copies everything accumulated
so far into it, appends, and calls `toString()` to copy it all out again. Over n
parts that is 1 + 2 + 3 + … characters: **O(n²) in the total length**, from code
that reads as linear.

`StringBuilder` keeps one `byte[]` and doubles it when full, so n appends cost
O(n) amortized — the same argument as `ArrayList.add` in the cost unit.

### Latin-1 and UTF-16, and why `char` is not a character

Since Java 9 a `String` stores one byte per character when every character fits
in Latin-1, and two bytes otherwise. That is invisible to `charAt` and it is
*not* what breaks: what breaks is that a `char` is a **UTF-16 code unit**, 16
bits. Characters outside the Basic Multilingual Plane — emoji, some CJK
extensions — occupy *two* chars, a surrogate pair.

```java
"😀".length();            // 2, not 1
"😀".charAt(0);           // half of a surrogate pair, meaningless alone
"😀".codePointCount(0, 2) // 1 — the honest count
```

Every problem in this unit says "lowercase English letters", which makes this
safe to ignore *here* and a real bug in production. Reversing a string by
swapping `char`s corrupts every emoji in it.

### `char` arithmetic

`char` promotes to `int` in arithmetic, which is what makes the array-index
trick work:

```java
int idx = c - 'a';              // 0..25, an int
char back = (char) (idx + 'a'); // the cast is required — int does not narrow implicitly
```

`'a' + 1` is the `int` 98, not the `char` `'b'`. Printing it without the cast
prints `98`, which is the most common surprise in the first ten minutes of this
unit.

### The string pool

String *literals* are interned: `"abc" == "abc"` is true because both refer to
one pooled object. `new String("abc") == "abc"` is false, and so is
`("ab" + variable) == "abc"`. This is why **`equals` is the only correct way to
compare strings** — `==` sometimes works, which is worse than never working,
because it passes in testing and fails on computed input.
""",
    variants=[
        _var("Frequency signature",
             "Reduce the string to 26 counts and compare those instead of the characters.",
             "Anagrams, “same letters”, permutation-in-string.",
             "O(m) time, O(1) space",
             "Only valid for a **fixed** alphabet. On Unicode, or on arbitrary tokens, it "
             "becomes a `HashMap` and you lose the constant factor, not the bound."),
        _var("Canonical form as a key",
             "Map each string to one normal form and group by it.",
             "Group anagrams, “which of these are the same word”.",
             "O(n · m log m) sorting each, or O(n · m) with count signatures",
             "The key must be injective by construction. Summing character codes is the "
             "classic wrong key: `ad` and `bc` both make 199."),
        _var("Two pointers over one string",
             "Walk from both ends, skipping what the problem says to ignore.",
             "Palindromes, “valid after removing non-alphanumerics”, reversing "
             "words.",
             "O(m) time, O(1) space",
             "Skipping in the *condition* rather than the body is what keeps it one loop: "
             "`while (l < r && !isLetterOrDigit(s.charAt(l))) l++;`"),
        _var("Expand around a centre",
             "For each of the `2m - 1` centres, grow outwards while the sides match.",
             "Longest palindromic substring, counting palindromic substrings.",
             "O(m²) time, O(1) space",
             "`2m - 1` centres, not m — even-length palindromes sit *between* two "
             "characters. Expanding only from characters silently misses `abba`."),
        _var("Run-length scan",
             "An outer loop with no increment; an inner loop that consumes a whole run "
             "and advances the index.",
             "Compression, longest run, grouping equal neighbours.",
             "O(m) time",
             "The outer `for` must have an empty increment clause. Leaving `i++` in as "
             "well skips the first character of every run after the first."),
        _var("Vertical scan across many strings",
             "Iterate by *column* across all n strings rather than string by string.",
             "Longest common prefix.",
             "O(total characters), and it stops early",
             "No substring is ever built, so there are no copies — the version that "
             "repeatedly shortens a candidate prefix with `substring` is O(n · m) in "
             "copying alone."),
        _var("Prefix function (KMP)",
             "Precompute the longest border of every prefix, then never move the text "
             "pointer backwards.",
             "Finding a pattern, periodicity, “is this a repeated block”.",
             "O(n + m) time, O(m) space",
             "The same loop builds `pi` and runs the search. If you have written it twice, "
             "you have written it once too often."),
    ],
    rewrites=[
        _rw("Comparing substrings",
            """
// O(n·m) in copying alone — each substring allocates
for (int i = 0; i + m <= n; i++)
    if (s.substring(i, i + m).equals(t)) return i;
return -1;
""",
            """
// O(n·m) comparisons, ZERO allocations
for (int i = 0; i + m <= n; i++)
    if (s.regionMatches(i, t, 0, m)) return i;
return -1;
""",
            "`substring(...).equals(t)` becomes `regionMatches`, which compares in place.",
            """
Both versions are O(n·m) in the worst case, and this rewrite is still worth
making — which is the useful lesson, because not every improvement is a
complexity class.

`substring` **copies**. Since Java 7 it allocates a fresh character array, so
the slow version does up to n allocations of m characters each and then throws
them all away. `regionMatches` compares the two ranges where they already are.

The habit to build is *"do I need this substring, or do I need to compare it?"*.
The same question retires most `split`/`substring`/`trim` chains in a hot loop.

For the genuine complexity win on this exact problem, the answer is the KMP
prefix function — O(n + m) by never moving the text pointer backwards. That is
in the `strings` playbook and again in the optional string-matching unit.
""",
            ),
        _rw("Are these two strings anagrams",
            """
// O(m log m) — sort both, then compare
char[] x = s.toCharArray(), y = t.toCharArray();
Arrays.sort(x);
Arrays.sort(y);
return Arrays.equals(x, y);
""",
            """
// O(m) — 26 counters, up for one string and down for the other
if (s.length() != t.length()) return false;
int[] freq = new int[26];
for (int i = 0; i < s.length(); i++) {
    freq[s.charAt(i) - 'a']++;
    freq[t.charAt(i) - 'a']--;
}
for (int f : freq) if (f != 0) return false;
return true;
""",
            "Two sorts become one pass over both strings, sharing a single counter array.",
            """
Sorting builds a total order and then uses only the equality test. The question
is "same multiset of letters", and the cheapest canonical form for a multiset is
the multiset — 26 counters.

The single-array trick is the part worth stealing: rather than building two
frequency arrays and comparing them, increment for one string and decrement for
the other. Equal multisets leave every counter at zero, so the comparison is a
scan of 26 values and the second array never exists.

The length guard is load-bearing, not defensive: the loop uses one index for
both strings and would read out of bounds without it.

Bound alphabet, bound win. On Unicode or arbitrary tokens this becomes a
`HashMap` and stays O(m) with a much larger constant — still better than
sorting, and worth saying which part of the improvement survives.
""",
            ),
    ],
    build_it="""
### Write the string toolkit without the convenience methods

The rule for this exercise: **no `substring`, no `split`, no `+` on strings
inside a loop.** Everything with `charAt`, indices and one `StringBuilder`.

**1. `reverseWords(String s)`** — collapse runs of spaces, no leading or
trailing space in the output. Do it by scanning word boundaries as index pairs
and appending, never by `split(" ")`. Then answer: what does `split(" ")` return
for `"a  b"`, and why is that a bug and not a preference?

**2. `isPalindrome(String s)`** ignoring case and non-alphanumerics, with two
pointers and no cleaned copy of the input. The skipping belongs in the `while`
conditions; if you built a filtered string first, you used O(m) space to avoid
two `if`s.

**3. `runLengthEncode(String s)`.** Outer `for` with an **empty** increment
clause, inner `while` consuming the run. Then encode a string of 10⁵ identical
characters and check the output is `a100000`, not `a1` repeated — that is the
test that catches the stray `i++`.

**4. `longestCommonPrefix(String[] words)`** by vertical scan: column 0 across
every word, then column 1, stopping at the first mismatch or the first word that
ends. Compare against the version that shortens a candidate with `substring` in
a loop, on 10⁴ words of length 100, and time both.

**5. `countPalindromicSubstrings(String s)`** by expanding around all `2m - 1`
centres. Write the centre loop before the expansion helper — getting `2m - 1`
right is the exercise, and the check is that `"abba"` reports 6, not 4.

**6. Build the KMP prefix function** for `"aabaaab"` **by hand on paper first**,
then write the loop and compare. The falling-back line
(`while (k > 0 && s.charAt(i) != s.charAt(k)) k = pi[k - 1];`) is the one that
cannot be reconstructed from intuition, and doing it on paper once is what makes
it stick.

Then use it twice: to find a pattern, and to report the smallest period as
`n - pi[n - 1]`. Two answers from one array is the reason the technique earns
its place.
""",
    rungs=[
        _rung("Warm up", "Count characters; build output properly.",
              ["count-vowels", "count-words", "password-strength"],
              {"count-words": "Decide what two consecutive spaces mean before you code — that is the bug."}),
        _rung("Core", "A pass that transforms rather than counts.",
              ["caesar-cipher", "max-nesting-depth", "run-length-encode"],
              {"caesar-cipher": "Modular arithmetic on `c - 'a'`; watch the wrap and the non-letters.",
               "run-length-encode": "The run scan, with `StringBuilder` for the output."}),
        _rung("Variations", "Comparing many strings at once.",
              ["longest-common-prefix", "longest-common-prefix-strs"],
              {"longest-common-prefix": "Vertical scan, column by column — no substring copies needed."}),
    ],
    next_up="""
That is the pattern toolkit for linear data. The next stage adds **order** —
sorting, binary search, and the greedy rules that sorted data makes provable —
starting with the recursion that the best sorting ideas are built on.
""",
)
