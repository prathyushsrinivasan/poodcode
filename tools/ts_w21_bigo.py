# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 21 — Big-O & complexity.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ===========================================================================
# THE PROBLEM TS_ROADMAP FLAGGED, AND HOW IT IS SOLVED.
# ===========================================================================
#
# "This week has almost nothing to judge. Complexity is a reasoning skill, and
#  the course's grading model is run-it-and-compare-stdout."
#
# The roadmap listed three options in preference order: lean on warmups and
# quizzes; write exercises that MEASURE (count operations into a counter and
# print it, so the shape of the growth is the output); or add a fifth exercise
# kind. The second option is the whole week, and by the time this was authored it
# was no longer a guess — weeks 18 and 19 had already proved the technique:
#
#   week 18  draining a shift-based queue costs 3+2+1+0 = 6 element moves
#   week 18  the head-index queue prints `moves 0`
#   week 19  the quadratic de-duplication prints `comparisons 4`; the Set, 0
#
# So **every exercise in this week instruments an algorithm and prints a count.**
# That is not a workaround for the judge, it is the better lesson: "O(n²)" is a
# label, and `n=4 ops=6 / n=8 ops=28 / n=16 ops=120` is the thing the label names.
# A learner who has watched a count quadruple when n doubles understands growth in
# a way that reciting the classes never produces.
#
# No fifth exercise kind was needed.
#
# ===========================================================================
# THE RULE THIS WEEK SHARES WITH WEEK 17: NOTHING PRINTS A DURATION.
#
# Not one program measures time. Counts are exact integers, identical on every
# machine; a millisecond reading is noise on small inputs and a judge timeout on
# large ones. Every "how expensive is this?" question in this week is answered in
# operations, and the sizes are chosen so the arithmetic is checkable by hand:
#
#   linear         n=4,8,16   ->  4, 8, 16          (doubles)
#   quadratic      n=4,8,16   ->  6, 28, 120        (~quadruples)
#   binary search  n=8..1024  ->  4, 5, 6, … 11     (+1 per doubling)
#   fib(n) calls   n=5,10,15  ->  15, 177, 1973     (explodes)
#
# The capstone turns that into the actual skill: run an algorithm at n and at 2n,
# take the ratio of the counts, and name the class. That is how you identify a
# complexity empirically, and it is a deterministic program.
#
# ===========================================================================
# WHAT THIS WEEK MUST NOT DO, also from the roadmap: "do not pad it with
# unrelated coding". Every algorithm instrumented here is one the course has
# already written — week 18's shift and monotonic stack, week 19's includes-scan
# and Map lookup, week 20's tree recursion and traversals. The week adds no new
# algorithms at all; it measures the ones the learner already owns, which is also
# why it can afford to be this dense.
# ---------------------------------------------------------------------------

# Build an array of n numbers. Used by nearly every exercise, because the whole
# week is "run this at several sizes and compare".
_SIZES = (
    'function sized(n: number): readonly number[] {\n'
    '  return Array.from({ length: n }, (_, i) => i + 1);\n}\n'
)

# --- Week 21 --------------------------------------------------------------
_WEEKS.append(_week(
    21, 6, _M6,
    "Big-O & Complexity",
    "What it costs when the input gets bigger — counted, not timed. Instrument the algorithms you already wrote, watch the numbers grow, and learn to name the shape.",
    """
Big-O is not about speed. It is about **how the cost grows when the input grows**,
and that is a different question with a much more useful answer.

## Counted, never timed

Every exercise this week instruments an algorithm and prints the number of
operations it performed. Nothing measures milliseconds — a millisecond reading is
noise on a small input, and the machine's mood on a large one. A count is exact:

```
n=4  ops=6
n=8  ops=28
n=16 ops=120
```

Double n, and the count roughly **quadruples**. That is what "O(n²)" means, and
seeing the numbers is worth more than the label.

## The three questions

1. **What is the cost?** Count the operations for a given n.
2. **How does it grow?** Double n and look at what happens to the count.
3. **Which class is that?** ×1 is constant, ×2 is linear, +1 is logarithmic, ×4
   is quadratic, and if it explodes it is exponential.

Question 3 is the only one anybody asks in an interview, and it is the easiest of
the three once you can do the first two.

## Nothing new to learn here

Every algorithm this week measures is one you have already written: week 18's
`shift()` and its monotonic stack, week 19's `includes` scan and its Map lookup,
week 20's tree recursion and traversals. This week does not add algorithms — it
puts a counter inside the ones you own, which is also why there is so much of it.

⏱️ Budget about **seven hours**. Lighter than month 5, and heavier on reading.
""",
    objectives=[
        "Say what Big-O describes, and what it deliberately ignores",
        "Instrument an algorithm with an operation counter",
        "Read a growth class off a table of counts by doubling n",
        "Say why constants and lower-order terms are dropped",
        "Name the seven classes in order, with an example of each you have written",
        "Say what a halving loop's count does when n doubles",
        "Combine complexities: sequential adds, nested multiplies",
        "Spot a hidden O(n) inside a loop — `includes`, `shift`, string concatenation",
        "Distinguish auxiliary space from total space, and count a recursion's depth",
        "Say what amortised O(1) means and give two examples from this course",
        "Say why worst case is the default, and give an input that triggers one",
        "State the complexity of unfamiliar code, in both time and space",
    ],
    why="\"What's the complexity?\" is the follow-up to every interview answer, and a wrong answer undoes a correct implementation. More usefully: the two worst performance bugs in this course so far — a queue built on `shift` and a de-duplication built on `includes` — were both invisible in the code and obvious in the counts. Complexity is the skill that makes them visible before production does.",
    est_minutes=420,
    glossary=[
        _gloss("Big-O", "An upper bound on growth, ignoring constants and lower-order terms."),
        _gloss("growth", "How the cost changes when the input changes. The only thing Big-O describes."),
        _gloss("operation count", "The measurable stand-in for cost: how many times the inner step ran."),
        _gloss("doubling test", "Run at n and 2n; the ratio of the counts names the class."),
        _gloss("O(1)", "Constant. The count does not change with n."),
        _gloss("O(log n)", "Logarithmic. Doubling n adds ONE step. Binary search."),
        _gloss("O(n)", "Linear. Doubling n doubles the count. One pass."),
        _gloss("O(n log n)", "Doubling n a little more than doubles the count. A good sort."),
        _gloss("O(n²)", "Quadratic. Doubling n quadruples the count. Nested loops over the same data."),
        _gloss("O(2^n)", "Exponential. Adding ONE to n doubles the count. Naive fib, all subsets."),
        _gloss("O(n!)", "Factorial. All permutations. Hopeless beyond about ten."),
        _gloss("dropping constants", "O(3n) is O(n): a constant factor does not change the shape."),
        _gloss("lower-order terms", "O(n² + n) is O(n²): the bigger term wins as n grows."),
        _gloss("sequential composition", "Two steps in a row: add the costs, keep the larger."),
        _gloss("nested composition", "A loop inside a loop: multiply the costs."),
        _gloss("hidden O(n)", "An innocent-looking call that scans — `includes`, `indexOf`, `shift`, `+=` on a string."),
        _gloss("auxiliary space", "Extra memory the algorithm allocates, not counting the input."),
        _gloss("recursion stack", "One frame per pending call. A recursion's depth IS space."),
        _gloss("in-place", "O(1) auxiliary space: the input is rearranged rather than copied."),
        _gloss("amortised O(1)", "Each operation is O(1) on average, even if one occasionally does more."),
        _gloss("average case", "The cost on typical input. What a hash map's O(1) really is."),
        _gloss("worst case", "The cost on the most inconvenient input. The default, because it is a guarantee."),
        _gloss("adversarial input", "Input chosen to trigger the worst case — sorted data into a naive BST."),
    ],
    cheatsheet="""
```ts
// ---- instrument it, then double n --------------------------------------
let ops = 0;
for (let i = 0; i < n; i = i + 1) {
  for (let j = i + 1; j < n; j = j + 1) { ops = ops + 1; }
}
// n=4 ops=6 · n=8 ops=28 · n=16 ops=120   ⇒ ×4 per doubling ⇒ O(n²)

// ---- the doubling test, as a table ------------------------------------
//   count ratio ≈ 1     O(1)
//   count ratio ≈ +1     O(log n)      (an ADDED step, not a multiple)
//   count ratio ≈ 2     O(n)
//   count ratio ≈ 2.2   O(n log n)
//   count ratio ≈ 4     O(n²)
//   count ratio ≈ 2 per +1 of n         O(2^n)

// ---- the classes, with something you have written --------------------
// O(1)        map.get, stack.push, an index access
// O(log n)    binary search — n=1024 takes 11 steps
// O(n)        one pass: sum, a Set built from an array
// O(n log n)  sort()
// O(n²)       includes inside a loop (week 19); shift in a loop (week 18)
// O(2^n)      fib(n) without memoisation — fib(15) makes 1,973 calls
// O(n!)       every permutation

// ---- combining ---------------------------------------------------------
sortIt(xs);  scanIt(xs);          // O(n log n) + O(n)  =  O(n log n)
for (…n…) { for (…n…) { … } }      // O(n) × O(n)        =  O(n²)
for (…n…) { for (…3…) { … } }      // O(n) × O(1)        =  O(n)
while (n > 1) { n = n / 2; }        //                       O(log n)

// ---- the hidden O(n)s to watch for ------------------------------------
if (seen.includes(x))              // O(n) — use a Set            (week 19)
queue.shift()                      // O(n) — use a head index     (week 18)
out = out + ch                     // O(n) copy — collect and join
arr.unshift(x)                     // O(n)

// ---- space -------------------------------------------------------------
function sum(xs: readonly number[]): number { … }        // O(1) auxiliary
function doubled(xs: readonly number[]): number[] { … }  // O(n) auxiliary
function depth(t: T | null): number { … }                 // O(h) — the stack

// ---- amortised, average, worst ----------------------------------------
arr.push(x)          // amortised O(1) — occasionally reallocates
map.get(k)           // O(1) AVERAGE, O(n) worst (every key colliding)
quicksort            // O(n log n) average, O(n²) worst
naive BST insert     // O(log n) balanced, O(n) on SORTED input  (week 20)
```
""",
    self_check=[
        "Can you say what Big-O describes and what it ignores?",
        "Can you put a counter into a nested loop and predict the count for n=4?",
        "Can you name the class from a table of counts, by doubling n?",
        "Can you say why O(3n + 7) is O(n)?",
        "Can you say what a halving loop's count does when n doubles?",
        "Can you give the seven classes in order, fastest-growing last?",
        "Can you say what two sequential O(n) passes cost, and two nested ones?",
        "Can you name three innocent-looking calls that are secretly O(n)?",
        "Can you say what the auxiliary space of a recursive tree walk is?",
        "Can you explain amortised O(1) with an example from this course?",
        "Can you give an input that turns a BST's O(log n) into O(n)?",
        "Can you state the time and space complexity of a function you have never seen?",
    ],
    review=[
        _q("Big-O describes…",
           ["how fast code runs", "how the cost grows as the input grows", "memory only",
            "the average case"], 1,
           "Growth, not speed."),
        _q("Doubling n and seeing the count quadruple means…",
           ["O(n)", "O(n²)", "O(log n)", "O(1)"], 1,
           "Two doublings of n multiply a quadratic count by four."),
        _q("Doubling n and seeing the count go UP BY ONE means…",
           ["O(n)", "O(log n)", "O(1)", "O(n²)"], 1,
           "Binary search: 1024 items take 11 steps."),
        _q("O(3n + 7) is…",
           ["O(3n)", "O(n)", "O(n + 7)", "O(1)"], 1,
           "Constants and lower terms do not change the shape."),
        _q("Two O(n) passes one after another are…",
           ["O(n²)", "O(n)", "O(2n) and that is different", "O(log n)"], 1,
           "Sequential adds, and the constant drops."),
        _q("An O(n) loop containing an O(n) loop is…",
           ["O(n)", "O(n²)", "O(n log n)", "O(2n)"], 1,
           "Nested multiplies."),
        _q("`seen.includes(x)` inside a loop over n items is…",
           ["O(n)", "O(n²) overall", "O(1)", "O(log n)"], 1,
           "Week 19's quadratic de-duplication."),
        _q("`queue.shift()` in a drain loop is…",
           ["O(n)", "O(n²) overall", "O(1)", "free"], 1,
           "Week 18 counted the moves."),
        _q("`out = out + ch` in a loop is…",
           ["O(n)", "O(n²) — each concatenation copies what is already there", "O(1)",
            "O(log n)"], 1,
           "Collect into an array and join."),
        _q("Auxiliary space is…",
           ["all memory used", "the extra memory, not counting the input", "the stack only",
            "the heap only"], 1,
           "Which is why an in-place algorithm is O(1)."),
        _q("A recursive tree walk's auxiliary space is…",
           ["O(1)", "O(h) — one stack frame per level", "O(n²)", "O(n) always"], 1,
           "Depth, not node count."),
        _q("`arr.push(x)` is…",
           ["always O(1)", "amortised O(1) — it occasionally reallocates", "O(n)", "O(log n)"], 1,
           "The cost is spread across many pushes."),
        _q("A Map lookup is O(1)…",
           ["always", "on average; the worst case is O(n)", "never", "only for strings"], 1,
           "Which is why worst case and average case are different questions."),
        _q("Inserting 1,2,3,4,5 in order into a naive BST gives…",
           ["O(log n)", "O(n) — it degenerates into a list", "O(1)", "O(n log n)"], 1,
           "Week 20's warning, stated as a complexity."),
        _q("Worst case is the default because…",
           ["it is easier", "it is a guarantee; an average is a hope about your input",
            "it is faster", "of tradition"], 1,
           "And adversarial input is a real thing."),
        _q("`fib(15)` without memoisation makes how many calls?",
           ["15", "1,973", "225", "30"], 1,
           "Exponential growth, counted."),
    ],
    milestone="The interview reps begin. From here the weekly capstone is a timed problem in the week's technique rather than another feature of Budget Buddy — and this one is the tool the rest of them will be judged by: an instrumented harness that runs an algorithm at n and at 2n, takes the ratio of the operation counts, and names the growth class from it.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w21-why", "Growth, not speed",
            "What the notation is for, and what it throws away.",
            """
Two implementations of the same thing. Which is faster?

The honest answer is "it depends on the machine, the input, the JIT, what else is
running, and how big the input is" — and the only part of that which is a property
of the *algorithm* is the last one. So that is the part we measure:

> **Big-O describes how the cost grows as the input grows.**

## Counted, not timed

```ts
let ops = 0;
for (const x of xs) { ops = ops + 1; }
```

`ops` is exact, reproducible, and the same on every machine. A stopwatch is none of
those things on a small input. Every exercise this week counts.

## What it throws away, and why that is a feature

**Constants.** O(3n) is written O(n). A version doing three operations per element
is three times slower than one doing one — and it is *still* linear, so doubling the
input still doubles the work. The shape is what survives; the constant is what you
measure with a profiler, later, if it matters.

**Lower-order terms.** O(n² + n) is O(n²), because at n = 1,000 the `n²` term is a
million and the `n` term is a thousand. The big term drowns the small one.

**Everything about small inputs.** O(n²) beats O(n log n) for n = 5, routinely.
Big-O is a statement about *large* n, which is exactly the regime where you cannot
test your way to the answer.

## What this buys you

You can answer "will this still work at a million rows?" from reading the code.
That is the whole value, and it is why the question follows every interview answer.

```
O(n)   at a million rows:  a million operations.     Fine.
O(n²)  at a million rows:  a trillion operations.    Not fine.
```

The difference between those two is often one line — a `Set` instead of an
`includes`, or a head index instead of a `shift`. You have already fixed both.

## The notation, briefly

* **O(f)** — grows no faster than f. The one everybody uses.
* **Ω(f)** — grows no slower than f.
* **Θ(f)** — both: grows exactly like f.

In practice people say "O(n)" when they mean Θ(n), and nobody minds. Knowing the
distinction exists is enough.

> ⚠️ **Common mistakes:** treating Big-O as a speed measurement; keeping constants
> ("O(2n)"); and choosing an asymptotically better algorithm for an input that is
> always tiny.
""",
            warmup=[
                _q("Big-O measures…",
                   ["milliseconds", "how cost grows with input size", "memory", "lines of code"], 1,
                   "Growth."),
                _q("O(3n + 7) is written…",
                   ["O(3n)", "O(n)", "O(n+7)", "O(3)"], 1,
                   "Constants and lower terms go."),
                _q("Counting operations rather than timing is better because…",
                   ["it is easier", "the count is exact and identical on every machine",
                    "it is faster", "of the judge"], 1,
                   "Both, but the first reason is the real one."),
                _q("At n = 5, an O(n²) algorithm…",
                   ["is always worse", "may well be faster than an O(n log n) one", "is the same",
                    "cannot run"], 1,
                   "Big-O is a statement about large n."),
            ],
            exercises=[
                _ex("tscourse-w21-wh-1", "Count a single pass",
                    "Increment the counter once per element, then report both the answer and the cost.",
                    _NUMS +
                    'let ops = 0;\n'
                    'let total = 0;\n'
                    'for (const n of nums) {\n'
                    '  ops = ops + 1;\n'
                    '  total = total + n;\n}\n'
                    'console.log(`total=${total} ops=${ops}`);\n',
                    '  ops = ops + 1;',
                    [("1 2 3 4", "total=10 ops=4"), ("5", "total=5 ops=1")],
                    hints=["One operation per element visited.",
                           "Write ops = ops + 1;"]),
                _ex("tscourse-w21-wh-2", "Three operations per element",
                    "Count every step, and notice the count is three times the length — and still linear.",
                    _NUMS +
                    'let ops = 0;\n'
                    'let total = 0;\n'
                    'for (const n of nums) {\n'
                    '  ops = ops + 3;\n'
                    '  total = total + n * 2 - 1;\n}\n'
                    'console.log(`ops=${ops} perItem=${nums.length === 0 ? 0 : ops / nums.length}`);\n',
                    '  ops = ops + 3;',
                    [("1 2 3", "ops=9 perItem=3"), ("1 2 3 4 5 6", "ops=18 perItem=3")],
                    hints=["Three operations happen per element, so the counter goes up by three.",
                           "Write ops = ops + 3;"],
                    difficulty="Easy"),
                _ex("tscourse-w21-wh-3", "The count doubles when n doubles",
                    "Run the same pass at three sizes and print a table.",
                    _SIZES +
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (const _x of sized(n)) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  return ops;\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    'for (const n of [4, 8, 16]) {',
                    [("", "n=4 ops=4\nn=8 ops=8\nn=16 ops=16")],
                    hints=["Three sizes, each double the last.",
                           "Write for (const n of [4, 8, 16]) {"],
                    difficulty="Easy"),
                _ex("tscourse-w21-wh-4", "Lower-order terms drown",
                    "Report both terms at two sizes, and watch the smaller one stop mattering.",
                    'function terms(n: number): string {\n'
                    '  const big = n * n;\n'
                    '  const small = n;\n'
                    '  return `n=${n} n2=${big} n=${small} share=${Math.round((small / (big + small)) * 100)}%`;\n}\n'
                    'console.log(terms(10));\n'
                    'console.log(terms(1000));\n',
                    '  return `n=${n} n2=${big} n=${small} share=${Math.round((small / (big + small)) * 100)}%`;',
                    [("", "n=10 n2=100 n=10 share=9%\nn=1000 n2=1000000 n=1000 share=0%")],
                    hints=["The linear term's share of the total is what shrinks.",
                           "Build the template with all four values."],
                    difficulty="Medium"),
                _ex("tscourse-w21-wh-5", "A million rows, both ways",
                    "Report what each class costs at a million, to see why the distinction matters.",
                    'const n = 1000000;\n'
                    'console.log(`linear=${n}`);\n'
                    'console.log(`quadratic=${n * n}`);\n',
                    'console.log(`quadratic=${n * n}`);',
                    [("", "linear=1000000\nquadratic=1000000000000")],
                    hints=["n times n.",
                           "Write console.log(`quadratic=${n * n}`);"],
                    difficulty="Easy"),
                _fix("tscourse-w21-wh-fix1", "Fix the counter that was outside the work",
                     "This reports `ops=1` for every input: the counter sits outside the loop, so it measures how many times the loop was *entered* rather than how many times the body ran.",
                     _NUMS +
                     'let ops = 0;\n'
                     'let total = 0;\n'
                     'ops = ops + 1;\n'
                     'for (const n of nums) {\n'
                     '  total = total + n;\n}\n'
                     'console.log(`total=${total} ops=${ops}`);\n',
                     _NUMS +
                     'let ops = 0;\n'
                     'let total = 0;\n'
                     'for (const n of nums) {\n'
                     '  ops = ops + 1;\n'
                     '  total = total + n;\n}\n'
                     'console.log(`total=${total} ops=${ops}`);\n',
                     [("1 2 3 4", "total=10 ops=4"), ("7", "total=7 ops=1")],
                     hints=["The count has to grow with the input, and this one never does.",
                            "The operation being counted happens once per element.",
                            "Move the increment inside the loop body."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Θ(n) versus O(n) is the difference between…",
                   ["nothing", "'grows exactly like n' and 'grows no faster than n'", "time and space",
                    "average and worst"], 1,
                   "Everyone says O and means Θ."),
                _q("The value of complexity analysis is…",
                   ["elegance", "answering 'will this work at a million rows?' by reading the code",
                    "speed", "interviews only"], 1,
                   "You cannot test your way to it."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w21-count", "The doubling test",
            "Run it at n and at 2n, and the ratio tells you the class.",
            """
You do not have to derive a complexity from first principles. You can **measure**
it:

1. Instrument the algorithm with an operation counter.
2. Run it at n, then at 2n.
3. Look at the ratio of the counts.

| ratio when n doubles | class |
|---|---|
| ≈ 1 (unchanged) | O(1) |
| **+1** (one more step) | O(log n) |
| ≈ 2 | O(n) |
| ≈ 2.2 | O(n log n) |
| ≈ 4 | O(n²) |
| ≈ 8 | O(n³) |
| doubles when n goes up by **one** | O(2^n) |

Note that O(log n) is the odd one out: it does not *multiply* the count, it **adds
a step**. Binary search on 1,024 items takes 11 steps; on 2,048 it takes 12.

## Two loops, counted

```ts
let ops = 0;
for (let i = 0; i < n; i = i + 1) {
  for (let j = i + 1; j < n; j = j + 1) {
    ops = ops + 1;
  }
}
```

```
n=4  ops=6
n=8  ops=28
n=16 ops=120
```

6 → 28 is ×4.7; 28 → 120 is ×4.3. Both close to 4, and the ratio approaches 4 as n
grows — that is O(n²), even though the inner loop starts at `i + 1` rather than 0
and the count is `n(n-1)/2` rather than `n²`. The constant ½ is exactly what Big-O
drops.

## Why the ratios are approximate at small n

`n(n-1)/2` at n=4 is 6 and at n=8 is 28, and 28/6 is 4.67 rather than 4.00. The
lower-order term is still visible at these sizes; it fades as n grows. So read the
ratio as "about 4, and trending towards 4", not as an exact figure — which is also
why the capstone classifies with **bands** rather than exact matches.

## Instrumenting well

Three rules that keep a count meaningful:

* **Count the operation that dominates**, usually the comparison or the array
  access in the innermost loop. Counting *everything* is noise.
* **Put the counter where the work is.** A counter outside the loop measures
  nothing, which is lesson 1's `fix`.
* **Reset it between runs**, or the second measurement includes the first.

That last one is its own `fix` in this lesson, because it produces a table that
looks plausible and is wrong.

> ⚠️ **Common mistakes:** forgetting to reset the counter between sizes; counting
> an operation that is not in the inner loop; and expecting exact ratios at n=4.
""",
            warmup=[
                _q("A count that goes 4, 8, 16 as n doubles is…",
                   ["O(1)", "O(n)", "O(n²)", "O(log n)"], 1,
                   "The ratio is 2."),
                _q("A count that goes 6, 28, 120 as n doubles is…",
                   ["O(n)", "O(n²)", "O(n log n)", "O(2^n)"], 1,
                   "The ratio is about 4."),
                _q("A count that goes 4, 5, 6 as n doubles is…",
                   ["O(n)", "O(log n)", "O(1)", "O(n²)"], 1,
                   "It ADDS a step rather than multiplying."),
                _q("Counting `n(n-1)/2` operations is…",
                   ["O(n)", "O(n²) — the ½ is a dropped constant", "O(n log n)", "O(1)"], 1,
                   "Exactly what Big-O throws away."),
            ],
            exercises=[
                _ex("tscourse-w21-ct-1", "Count every pair",
                    "Start the inner loop after the outer one, so each pair is counted once.",
                    'let ops = 0;\n'
                    'function pairs(n: number): void {\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    for (let j = i + 1; j < n; j = j + 1) {\n'
                    '      ops = ops + 1;\n    }\n  }\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  ops = 0;\n'
                    '  pairs(n);\n'
                    '  console.log(`n=${n} ops=${ops}`);\n}\n',
                    '    for (let j = i + 1; j < n; j = j + 1) {',
                    [("", "n=4 ops=6\nn=8 ops=28\nn=16 ops=120")],
                    hints=["Each pair should be counted once, so the inner index starts past the outer one.",
                           "Write for (let j = i + 1; j < n; j = j + 1) {"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ct-2", "Reset between runs",
                    "Clear the counter before each size, so the table measures one run at a time.",
                    'let ops = 0;\n'
                    'function scan(n: number): void {\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    ops = ops + 1;\n  }\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  ops = 0;\n'
                    '  scan(n);\n'
                    '  console.log(`n=${n} ops=${ops}`);\n}\n',
                    '  ops = 0;', [("", "n=4 ops=4\nn=8 ops=8\nn=16 ops=16")],
                    hints=["Before the run, not after it.",
                           "Write ops = 0; as the first statement in the loop."],
                    difficulty="Easy"),
                _ex("tscourse-w21-ct-3", "Report the ratio",
                    "Divide the bigger count by the smaller one, which is the number that names the class.",
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    for (let j = 0; j < n; j = j + 1) {\n'
                    '      ops = ops + 1;\n    }\n  }\n'
                    '  return ops;\n}\n'
                    'const small = cost(16);\n'
                    'const big = cost(32);\n'
                    'console.log(`${small} ${big} ratio=${big / small}`);\n',
                    'console.log(`${small} ${big} ratio=${big / small}`);',
                    [("", "256 1024 ratio=4")],
                    hints=["The ratio of the two counts.",
                           "Write console.log(`${small} ${big} ratio=${big / small}`);"],
                    difficulty="Easy"),
                _ex("tscourse-w21-ct-4", "Halving adds one step",
                    "Count the iterations of a loop that halves, and watch the count grow by one per doubling.",
                    'function steps(n: number): number {\n'
                    '  let count = 0;\n'
                    '  let left = n;\n'
                    '  while (left > 1) {\n'
                    '    left = Math.floor(left / 2);\n'
                    '    count = count + 1;\n  }\n'
                    '  return count;\n}\n'
                    'for (const n of [8, 16, 32, 1024]) {\n'
                    '  console.log(`n=${n} steps=${steps(n)}`);\n}\n',
                    '    left = Math.floor(left / 2);',
                    [("", "n=8 steps=3\nn=16 steps=4\nn=32 steps=5\nn=1024 steps=10")],
                    hints=["Each iteration discards half of what is left.",
                           "Write left = Math.floor(left / 2);"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ct-5", "An inner loop that is not n",
                    "The inner loop runs a fixed three times, so the whole thing is still linear — count it and see.",
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    for (let j = 0; j < 3; j = j + 1) {\n'
                    '      ops = ops + 1;\n    }\n  }\n'
                    '  return ops;\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    '    for (let j = 0; j < 3; j = j + 1) {',
                    [("", "n=4 ops=12\nn=8 ops=24\nn=16 ops=48")],
                    hints=["The inner bound is a constant, not n.",
                           "Write for (let j = 0; j < 3; j = j + 1) {"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ct-6", "Name the class from the ratio",
                    "Classify by which band the ratio falls into.",
                    _NUMS +
                    'function classify(ratio: number): string {\n'
                    '  if (ratio < 1.5) {\n'
                    '    return "O(1)";\n  }\n'
                    '  if (ratio < 2.5) {\n'
                    '    return "O(n)";\n  }\n'
                    '  if (ratio < 3.5) {\n'
                    '    return "O(n log n)";\n  }\n'
                    '  return "O(n^2)";\n}\n'
                    'for (const r of nums) {\n'
                    '  console.log(`${r} -> ${classify(r)}`);\n}\n',
                    '  if (ratio < 2.5) {\n    return "O(n)";\n  }',
                    [("1 2 3 4", "1 -> O(1)\n2 -> O(n)\n3 -> O(n log n)\n4 -> O(n^2)")],
                    hints=["A doubling of the count means linear.",
                           'Write if (ratio < 2.5) { return "O(n)"; }'],
                    difficulty="Medium"),
                _fix("tscourse-w21-ct-fix1", "Fix the table that never reset",
                     "This prints `n=4 ops=4`, `n=8 ops=12`, `n=16 ops=28` — the counts accumulate across runs, so the table looks superlinear for an algorithm that is a single pass. Each measurement has to start from zero.",
                     'let ops = 0;\n'
                     'function scan(n: number): void {\n'
                     '  for (let i = 0; i < n; i = i + 1) {\n'
                     '    ops = ops + 1;\n  }\n}\n'
                     'for (const n of [4, 8, 16]) {\n'
                     '  scan(n);\n'
                     '  console.log(`n=${n} ops=${ops}`);\n}\n',
                     'let ops = 0;\n'
                     'function scan(n: number): void {\n'
                     '  for (let i = 0; i < n; i = i + 1) {\n'
                     '    ops = ops + 1;\n  }\n}\n'
                     'for (const n of [4, 8, 16]) {\n'
                     '  ops = 0;\n'
                     '  scan(n);\n'
                     '  console.log(`n=${n} ops=${ops}`);\n}\n',
                     [("", "n=4 ops=4\nn=8 ops=8\nn=16 ops=16")],
                     hints=["4, 12, 28 are running totals: 4, then 4+8, then 4+8+16.",
                            "A measurement that includes the previous measurement is not a measurement.",
                            "Reset the counter before each run."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The ratio 28/6 at n=4→8 is 4.67 rather than 4 because…",
                   ["the count is wrong", "the lower-order term is still visible at small n",
                    "it is O(n log n)", "of rounding"], 1,
                   "It trends towards 4 as n grows."),
                _q("You should count…",
                   ["every statement", "the operation that dominates, usually in the innermost loop",
                    "function calls", "lines"], 1,
                   "Counting everything is noise."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w21-classes", "The classes, each one measured",
            "Seven shapes, and something you have already written in each.",
            """
In order, slowest-growing first. Every example is code from an earlier week.

## O(1) — constant

The count does not depend on n at all.

```ts
map.get(key);        stack.push(x);        xs[0];        xs.length;
```

## O(log n) — logarithmic

Each step throws away **half** the remaining input, so the count is how many times
n can be halved.

```
n=8 steps=4 · n=16 steps=5 · n=32 steps=6 · n=1024 steps=11
```

Binary search. Doubling the input adds **one** step — which is why an O(log n)
algorithm barely notices the difference between a thousand items and a billion.

## O(n) — linear

One pass.

```ts
for (const x of xs) { … }          // sum, max, a Set built from an array
```

## O(n log n) — linearithmic

A log-many passes over everything, which is what a good sort costs.

```ts
xs.sort();          // n log n comparisons
```

Sorting first and then scanning is `O(n log n) + O(n)` = **O(n log n)**, and that
is usually a bargain: sorting to make a problem easy is one of the most reliable
moves there is.

## O(n²) — quadratic

Every element against every other element.

```ts
if (unique.includes(x)) { … }      // week 19: O(n) inside an O(n) loop
queue.shift();                      // week 18: the same shape
```

Both were bugs, and in both cases the fix was a different data structure rather
than a cleverer loop.

## O(2^n) — exponential

Adding **one** to n *doubles* the work.

```
fib(5) calls=15 · fib(10) calls=177 · fib(15) calls=1973
```

Naive `fib` recomputes the same subproblems for ever. Week 26 fixes exactly this
with memoisation, and it is the reason dynamic programming exists.

## O(n!) — factorial

Every ordering of n things. 10 items is 3.6 million; 20 is more than there are
grains of sand. Week 25's permutations live here, which is why pruning matters.

## The one comparison worth memorising

At n = 1,000,000:

| | operations |
|---|---|
| O(log n) | 20 |
| O(n) | 1,000,000 |
| O(n log n) | 20,000,000 |
| O(n²) | 1,000,000,000,000 |

O(n) to O(n log n) is a 20× difference. O(n log n) to O(n²) is a 50,000× one. That
is why "can I get rid of the nested loop?" is the first question to ask, and
"can I avoid the sort?" is nearly never worth asking.

> ⚠️ **Common mistakes:** calling a halving loop O(n); assuming a sort is expensive
> enough to avoid; and not recognising an exponential recursion when you have
> written one.
""",
            warmup=[
                _q("Binary search on 1,024 items takes about…",
                   ["1,024 steps", "11 steps", "10,000 steps", "1 step"], 1,
                   "log₂(1024) is 10."),
                _q("An O(log n) algorithm, given twice the input, does…",
                   ["twice the work", "one more step", "four times the work", "the same"], 1,
                   "Which is why it scales almost indefinitely."),
                _q("`xs.sort()` is…",
                   ["O(n)", "O(n log n)", "O(n²)", "O(1)"], 1,
                   "And sorting to simplify a problem is usually a bargain."),
                _q("Naive `fib` is exponential because…",
                   ["recursion is slow", "it recomputes the same subproblems repeatedly",
                    "of the stack", "of addition"], 1,
                   "Week 26 fixes it with memoisation."),
            ],
            exercises=[
                _ex("tscourse-w21-cl-1", "O(1), counted",
                    "The count must not depend on n at all.",
                    'function cost(n: number): number {\n'
                    '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                    '  let ops = 0;\n'
                    '  ops = ops + 1;\n'
                    '  const first = xs[0] ?? 0;\n'
                    '  return ops + first * 0;\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    '  ops = ops + 1;', [("", "n=4 ops=1\nn=8 ops=1\nn=16 ops=1")],
                    hints=["One access, whatever the size.",
                           "Write ops = ops + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w21-cl-2", "Binary search, counted",
                    "Halve the range each step, and report how many steps it took.",
                    'function steps(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  let count = 0;\n'
                    '  while (lo <= hi) {\n'
                    '    count = count + 1;\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    const v = xs[mid] ?? 0;\n'
                    '    if (v === target) {\n'
                    '      return count;\n    }\n'
                    '    if (v < target) {\n'
                    '      lo = mid + 1;\n'
                    '    } else {\n'
                    '      hi = mid - 1;\n    }\n  }\n'
                    '  return count;\n}\n'
                    'for (const n of [8, 16, 32, 1024]) {\n'
                    '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                    '  console.log(`n=${n} steps=${steps(xs, n - 1)}`);\n}\n',
                    '    const mid = Math.floor((lo + hi) / 2);',
                    [("", "n=8 steps=4\nn=16 steps=5\nn=32 steps=6\nn=1024 steps=11")],
                    hints=["The midpoint of the current range, rounded down.",
                           "Write const mid = Math.floor((lo + hi) / 2);"],
                    difficulty="Medium"),
                _ex("tscourse-w21-cl-3", "Exponential, counted",
                    "Count the calls the naive recursion makes, and watch them explode.",
                    'let calls = 0;\n'
                    'function fib(n: number): number {\n'
                    '  calls = calls + 1;\n'
                    '  return n < 2 ? n : fib(n - 1) + fib(n - 2);\n}\n'
                    'for (const n of [5, 10, 15]) {\n'
                    '  calls = 0;\n'
                    '  fib(n);\n'
                    '  console.log(`n=${n} calls=${calls}`);\n}\n',
                    '  calls = calls + 1;',
                    [("", "n=5 calls=15\nn=10 calls=177\nn=15 calls=1973")],
                    hints=["One per call, at the top of the function.",
                           "Write calls = calls + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w21-cl-4", "Sort then scan",
                    "Count the comparisons the sort makes and the passes the scan makes, separately.",
                    _NUMS +
                    'let comparisons = 0;\n'
                    'const sorted = [...nums].sort((a, b) => {\n'
                    '  comparisons = comparisons + 1;\n'
                    '  return a - b;\n});\n'
                    'let passes = 0;\n'
                    'for (const _n of sorted) {\n'
                    '  passes = passes + 1;\n}\n'
                    'console.log(`sorted=${sorted.join(",")} comparisons>0=${comparisons > 0} passes=${passes}`);\n',
                    'const sorted = [...nums].sort((a, b) => {',
                    [("3 1 2", "sorted=1,2,3 comparisons>0=true passes=3"),
                     ("5", "sorted=5 comparisons>0=false passes=1")],
                    hints=["Sort a copy, with a comparator that counts each comparison.",
                           "Write const sorted = [...nums].sort((a, b) => {"],
                    difficulty="Medium"),
                _ex("tscourse-w21-cl-5", "The million-row table",
                    "Report what each class costs at a million, using the halving count for the log.",
                    'const n = 1000000;\n'
                    'let logN = 0;\n'
                    'let left = n;\n'
                    'while (left > 1) {\n'
                    '  left = Math.floor(left / 2);\n'
                    '  logN = logN + 1;\n}\n'
                    'console.log(`log=${logN}`);\n'
                    'console.log(`n=${n}`);\n'
                    'console.log(`nlogn=${n * logN}`);\n',
                    'console.log(`nlogn=${n * logN}`);',
                    [("", "log=19\nn=1000000\nnlogn=19000000")],
                    hints=["n multiplied by the halving count.",
                           "Write console.log(`nlogn=${n * logN}`);"],
                    difficulty="Easy"),
                _ex("tscourse-w21-cl-6", "Factorial growth",
                    "Count the orderings of n things, and see where it stops being usable.",
                    _NUMS +
                    'function factorial(n: number): number {\n'
                    '  let out = 1;\n'
                    '  for (let i = 2; i <= n; i = i + 1) {\n'
                    '    out = out * i;\n  }\n'
                    '  return out;\n}\n'
                    'for (const n of nums) {\n'
                    '  console.log(`${n}! = ${factorial(n)}`);\n}\n',
                    '    out = out * i;',
                    [("3 5 10", "3! = 6\n5! = 120\n10! = 3628800")],
                    hints=["Multiply by each number in turn.",
                           "Write out = out * i;"],
                    difficulty="Easy"),
                _fix("tscourse-w21-cl-fix1", "Fix the search that forgot it was sorted",
                     "This is a linear scan over sorted data: on 1,024 items it takes 1,024 steps where a binary search takes 11. The input is sorted — use that.",
                     'function steps(xs: readonly number[], target: number): number {\n'
                     '  let count = 0;\n'
                     '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                     '    count = count + 1;\n'
                     '    if ((xs[i] ?? 0) === target) {\n'
                     '      return count;\n    }\n  }\n'
                     '  return count;\n}\n'
                     'for (const n of [8, 1024]) {\n'
                     '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                     '  console.log(`n=${n} steps=${steps(xs, n - 1)}`);\n}\n',
                     'function steps(xs: readonly number[], target: number): number {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  let count = 0;\n'
                     '  while (lo <= hi) {\n'
                     '    count = count + 1;\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    const v = xs[mid] ?? 0;\n'
                     '    if (v === target) {\n'
                     '      return count;\n    }\n'
                     '    if (v < target) {\n'
                     '      lo = mid + 1;\n'
                     '    } else {\n'
                     '      hi = mid - 1;\n    }\n  }\n'
                     '  return count;\n}\n'
                     'for (const n of [8, 1024]) {\n'
                     '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                     '  console.log(`n=${n} steps=${steps(xs, n - 1)}`);\n}\n',
                     [("", "n=8 steps=4\nn=1024 steps=11")],
                     hints=["The target here is the LAST element, which is the linear scan's worst case.",
                            "Sorted input means you can discard half the range on every comparison.",
                            "Keep `lo` and `hi`, test the midpoint, and move whichever bound the comparison rules out."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("At a million rows, O(n) → O(n log n) is a factor of about…",
                   ["2", "20", "1,000", "50,000"], 1,
                   "Which is why sorting is usually affordable."),
                _q("At a million rows, O(n log n) → O(n²) is a factor of about…",
                   ["20", "1,000", "50,000", "2"], 2,
                   "Which is why the nested loop is the thing to remove."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w21-rules", "Combining, and the costs that hide",
            "Add for sequential, multiply for nested — and look inside the calls.",
            """
## The two rules

**Sequential: add, then keep the larger.**

```ts
sortIt(xs);        // O(n log n)
scanIt(xs);        // O(n)
// total: O(n log n) + O(n) = O(n log n)
```

**Nested: multiply.**

```ts
for (…n…) {            // O(n)
  for (…n…) { … }      // × O(n)
}                       // = O(n²)
```

And the case people get wrong in the other direction:

```ts
for (…n…) {            // O(n)
  for (…3…) { … }      // × O(1) — the bound is a CONSTANT
}                       // = O(n), not O(n²)
```

What matters is whether the inner bound depends on n. `for (j = 0; j < 3; …)` does
not, so it is a constant factor, and constant factors are dropped.

## A shrinking inner loop is still quadratic

```ts
for (let i = 0; i < n; i = i + 1) {
  for (let j = i + 1; j < n; j = j + 1) { … }
}
```

The inner loop runs n-1 times, then n-2, … down to 0, for a total of `n(n-1)/2`.
That is a quadratic with a constant of ½, and Big-O drops the ½. Lesson 2 counted
it: 6, 28, 120.

## The costs that hide inside a call

This is where real code goes wrong, because the expensive part does not *look* like
a loop:

| looks O(1) | is | fix |
|---|---|---|
| `xs.includes(v)` | **O(n)** | a `Set` (week 19) |
| `xs.indexOf(v)` | **O(n)** | a `Map` (week 19) |
| `queue.shift()` | **O(n)** | a head index (week 18) |
| `xs.unshift(v)` | **O(n)** | push and reverse at the end |
| `out = out + ch` | **O(n)** copy | collect into an array and `join` |
| `xs.splice(i, 1)` | **O(n)** | rethink the structure |

Any one of those inside a loop over n is an O(n²) algorithm that reads like a
linear one. Both of this course's performance bugs so far were exactly this.

## The string one is worth counting

```ts
let out = "";
for (let i = 0; i < n; i = i + 1) {
  out = out + "x";       // copies the whole string so far
}
```

```
n=4 copied=6 · n=8 copied=28
```

The same triangular numbers as week 18's queue drain, for the same reason: each
step copies everything that came before it. (JavaScript engines optimise this
particular pattern heavily in practice — but the shape is real, and
`array.push` + `join` is both faster and clearer.)

## Reading complexity off code

A checklist that gets it right nearly always:

1. What is n? (Which input does the cost depend on?)
2. What is the innermost repeated operation?
3. How many times does it run, in terms of n?
4. **Does any call inside the loop hide a loop of its own?**

Step 4 is the one people skip, and it is the one that matters.

> ⚠️ **Common mistakes:** multiplying by a constant inner bound; calling a shrinking
> nested loop O(n); and trusting a method name not to hide a scan.
""",
            warmup=[
                _q("O(n log n) followed by O(n) is…",
                   ["O(n² log n)", "O(n log n)", "O(n)", "O(2n log n)"], 1,
                   "Sequential adds; the larger wins."),
                _q("An O(n) loop containing a loop bounded by 3 is…",
                   ["O(3n)", "O(n)", "O(n²)", "O(1)"], 1,
                   "A constant inner bound is a constant factor."),
                _q("`for (j = i + 1; j < n; …)` inside `for (i = 0; i < n; …)` is…",
                   ["O(n)", "O(n²)", "O(n log n)", "O(n/2)"], 1,
                   "n(n-1)/2, and the ½ is dropped."),
                _q("`xs.includes(v)` is…",
                   ["O(1)", "O(n)", "O(log n)", "free"], 1,
                   "A scan, wearing a method name."),
            ],
            exercises=[
                _ex("tscourse-w21-ru-1", "A constant inner bound",
                    "Bound the inner loop by a constant, so the whole thing stays linear.",
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    for (let j = 0; j < 4; j = j + 1) {\n'
                    '      ops = ops + 1;\n    }\n  }\n'
                    '  return ops;\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    '    for (let j = 0; j < 4; j = j + 1) {',
                    [("", "n=4 ops=16\nn=8 ops=32\nn=16 ops=64")],
                    hints=["Four, not n — the counts should double, not quadruple.",
                           "Write for (let j = 0; j < 4; j = j + 1) {"],
                    difficulty="Easy"),
                _ex("tscourse-w21-ru-2", "Sequential, not nested",
                    "Run the two passes one after the other, so the cost adds rather than multiplies.",
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  return ops;\n}\n'
                    'for (const n of [4, 8, 16]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    ops = ops + 1;\n  }',
                    [("", "n=4 ops=8\nn=8 ops=16\nn=16 ops=32")],
                    hints=["Two loops at the same level, not one inside the other.",
                           "The counts should be 2n — still linear."],
                    difficulty="Medium"),
                _ex("tscourse-w21-ru-3", "Count the hidden scan",
                    "`includes` is a loop. Count what it really costs by adding the length it has to scan.",
                    _WORDS +
                    'let comparisons = 0;\n'
                    'const unique: string[] = [];\n'
                    'for (const w of words) {\n'
                    '  comparisons = comparisons + unique.length;\n'
                    '  if (!unique.includes(w)) {\n'
                    '    unique.push(w);\n  }\n}\n'
                    'console.log(`unique=${unique.length} comparisons=${comparisons}`);\n',
                    '  comparisons = comparisons + unique.length;',
                    [("a b c d", "unique=4 comparisons=6"), ("a a a", "unique=1 comparisons=2")],
                    hints=["Each `includes` scans everything collected so far.",
                           "Write comparisons = comparisons + unique.length;"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ru-4", "The string concatenation cost",
                    "Add the length being copied before each concatenation, and see the triangular numbers.",
                    'let copied = 0;\n'
                    'function build(n: number): string {\n'
                    '  let out = "";\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    copied = copied + out.length;\n'
                    '    out = out + "x";\n  }\n'
                    '  return out;\n}\n'
                    'for (const n of [4, 8]) {\n'
                    '  copied = 0;\n'
                    '  build(n);\n'
                    '  console.log(`n=${n} copied=${copied}`);\n}\n',
                    '    copied = copied + out.length;',
                    [("", "n=4 copied=6\nn=8 copied=28")],
                    hints=["Before appending, the whole existing string has to be copied.",
                           "Write copied = copied + out.length;"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ru-5", "…and the version that does not copy",
                    "Collect into an array and join once, so nothing is copied per step.",
                    'let copied = 0;\n'
                    'function build(n: number): string {\n'
                    '  const parts: string[] = [];\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    parts.push("x");\n  }\n'
                    '  return parts.join("");\n}\n'
                    'for (const n of [4, 8]) {\n'
                    '  copied = 0;\n'
                    '  console.log(`n=${n} len=${build(n).length} copied=${copied}`);\n}\n',
                    '  return parts.join("");',
                    [("", "n=4 len=4 copied=0\nn=8 len=8 copied=0")],
                    hints=["One join at the end, instead of a copy per step.",
                           'Write return parts.join("");'],
                    difficulty="Easy"),
                _ex("tscourse-w21-ru-6", "State the complexity",
                    "Classify each described shape by its rule.",
                    _NUMS +
                    'function shapeOf(kind: number): string {\n'
                    '  if (kind === 1) {\n'
                    '    return "O(n)";\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return "O(n^2)";\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return "O(n)";\n  }\n'
                    '  return "O(n log n)";\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} ${shapeOf(k)}`);\n}\n',
                    '  if (kind === 3) {\n    return "O(n)";\n  }',
                    [("1 2 3 4", "1 O(n)\n2 O(n^2)\n3 O(n)\n4 O(n log n)")],
                    hints=["Shape 3 is a loop over n containing a loop bounded by a constant.",
                           'Write if (kind === 3) { return "O(n)"; }'],
                    difficulty="Medium"),
                _fix("tscourse-w21-ru-fix1", "Fix the quadratic that looked linear",
                     "One loop over n, so this reads as linear — and the count is 6, 28, 120 for n=4, 8, 16, because `indexOf` scans the whole array every time. Replace the lookup, not the loop.",
                     'function cost(n: number): number {\n'
                     '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                     '  let comparisons = 0;\n'
                     '  const seen: number[] = [];\n'
                     '  for (const x of xs) {\n'
                     '    comparisons = comparisons + seen.length;\n'
                     '    if (seen.indexOf(x) < 0) {\n'
                     '      seen.push(x);\n    }\n  }\n'
                     '  return comparisons;\n}\n'
                     'for (const n of [4, 8, 16]) {\n'
                     '  console.log(`n=${n} comparisons=${cost(n)}`);\n}\n',
                     'function cost(n: number): number {\n'
                     '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                     '  let comparisons = 0;\n'
                     '  const seen = new Set<number>();\n'
                     '  for (const x of xs) {\n'
                     '    if (!seen.has(x)) {\n'
                     '      seen.add(x);\n    }\n  }\n'
                     '  return comparisons;\n}\n'
                     'for (const n of [4, 8, 16]) {\n'
                     '  console.log(`n=${n} comparisons=${cost(n)}`);\n}\n',
                     [("", "n=4 comparisons=0\nn=8 comparisons=0\nn=16 comparisons=0")],
                     hints=["The visible loop is linear; the cost is in the call inside it.",
                            "Week 19's structure answers membership without comparing against everything.",
                            "With a Set there is nothing left to count, so the comparison count is zero."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The checklist step people skip is…",
                   ["what is n", "whether a call inside the loop hides a loop", "the innermost operation",
                    "counting"], 1,
                   "And it is the one that finds the real bugs."),
                _q("`out = out + ch` in a loop copies…",
                   ["one character", "everything accumulated so far, every time", "nothing",
                    "the array"], 1,
                   "The same triangular numbers as week 18's queue."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w21-space", "Space",
            "The other axis, and the one the recursion stack lives on.",
            """
Time is not the only cost. **Space complexity** is how much memory the algorithm
needs as the input grows, and it is measured the same way.

## Auxiliary versus total

* **Total space** includes the input. An algorithm taking an array of n numbers is
  at least O(n).
* **Auxiliary space** is the *extra* memory the algorithm allocates.

When people say "O(1) space" they mean **auxiliary** — the input does not count,
because you did not choose to have it.

```ts
function sum(xs: readonly number[]): number {       // O(1) auxiliary
  let total = 0;
  for (const x of xs) { total = total + x; }
  return total;
}
function doubled(xs: readonly number[]): number[] {  // O(n) auxiliary
  return xs.map((x) => x * 2);
}
```

## In-place

An algorithm that rearranges its input rather than building a new one is
**in-place**, and that is what buys O(1):

```ts
// in-place reversal — O(1) auxiliary
for (let i = 0, j = xs.length - 1; i < j; i = i + 1, j = j - 1) {
  const t = xs[i] ?? 0;
  xs[i] = xs[j] ?? 0;
  xs[j] = t;
}
[...xs].reverse();      // O(n) auxiliary — a copy
```

The trade is honest: in-place is cheaper and destroys the input, which week 13
spent a whole week arguing against. "Cheaper" is not automatically "better", and
`readonly` is usually worth the copy.

## The recursion stack is space

This is the one people forget. Every pending call holds a frame:

```ts
function depth(t: T | null): number {                 // O(h) auxiliary,
  if (t === null) { return 0; }                        // where h is the HEIGHT
  return 1 + Math.max(depth(t.left), depth(t.right));
}
```

A balanced tree of a million nodes is about 20 deep, so this is fine. A
**degenerate** tree — week 20's BST built from sorted input — is a million deep,
and the program dies:

```
RangeError: Maximum call stack size exceeded
```

Node's limit is on the order of ten thousand frames. So "how deep can this recurse?"
is a real question with a real failure mode, and it is why week 25 covers turning a
recursion into a loop.

Note that an *iterative* traversal has the same complexity — week 20's explicit
stack holds the same number of nodes. What changes is that a heap-allocated array
can grow to millions where the call stack cannot.

## The usual trade

Time and space trade against each other, constantly:

| | time | space |
|---|---|---|
| naive `fib` | O(2^n) | O(n) stack |
| memoised `fib` | O(n) | O(n) table |
| a `Set` of seen items | O(n) total | O(n) |
| the two-pointer version | O(n) | O(1) |

Week 26 is that first trade, in detail. Recognising that a Map is buying you time
with memory is most of what "space-time tradeoff" means.

> ⚠️ **Common mistakes:** counting the input in "O(1) space"; forgetting the
> recursion stack; and treating in-place as free when it destroys the caller's data.
""",
            warmup=[
                _q("\"O(1) space\" normally means…",
                   ["no memory at all", "O(1) AUXILIARY — the input does not count", "one byte",
                    "no allocation"], 1,
                   "You did not choose to have the input."),
                _q("A recursive tree walk's auxiliary space is…",
                   ["O(1)", "O(h), the height", "O(n) always", "O(n²)"], 1,
                   "One frame per pending call."),
                _q("A degenerate BST of a million nodes recursed over gives…",
                   ["a slow answer", "RangeError: Maximum call stack size exceeded", "O(log n)",
                    "the right answer"], 1,
                   "Node allows on the order of ten thousand frames."),
                _q("Memoising `fib` trades…",
                   ["nothing", "memory for time", "time for memory", "space for space"], 1,
                   "O(2^n) time becomes O(n) time and an O(n) table."),
            ],
            exercises=[
                _ex("tscourse-w21-sp-1", "Constant auxiliary space",
                    "Accumulate into a single variable, so nothing scales with n.",
                    _NUMS +
                    'let allocated = 0;\n'
                    'let total = 0;\n'
                    'for (const n of nums) {\n'
                    '  total = total + n;\n}\n'
                    'console.log(`total=${total} extraSlots=${allocated}`);\n',
                    '  total = total + n;',
                    [("1 2 3", "total=6 extraSlots=0"), ("9", "total=9 extraSlots=0")],
                    hints=["One accumulator, no new array.",
                           "Write total = total + n;"],
                    difficulty="Easy"),
                _ex("tscourse-w21-sp-2", "Linear auxiliary space, counted",
                    "Count the slots the copy allocates, one per element.",
                    _NUMS +
                    'let slots = 0;\n'
                    'const out: number[] = [];\n'
                    'for (const n of nums) {\n'
                    '  out.push(n * 2);\n'
                    '  slots = slots + 1;\n}\n'
                    'console.log(`out=${out.join(",")} slots=${slots}`);\n',
                    '  slots = slots + 1;',
                    [("1 2 3", "out=2,4,6 slots=3"), ("5", "out=10 slots=1")],
                    hints=["One new slot per element pushed.",
                           "Write slots = slots + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w21-sp-3", "Reverse in place",
                    "Swap from both ends towards the middle, allocating nothing.",
                    _NUMS +
                    'const xs = [...nums];\n'
                    'let slots = 0;\n'
                    'for (let i = 0, j = xs.length - 1; i < j; i = i + 1, j = j - 1) {\n'
                    '  const t = xs[i] ?? 0;\n'
                    '  xs[i] = xs[j] ?? 0;\n'
                    '  xs[j] = t;\n}\n'
                    'console.log(`${xs.join(",")} slots=${slots}`);\n',
                    'for (let i = 0, j = xs.length - 1; i < j; i = i + 1, j = j - 1) {',
                    [("1 2 3", "3,2,1 slots=0"), ("1 2 3 4", "4,3,2,1 slots=0")],
                    hints=["Two indices moving towards each other, stopping when they meet.",
                           "Write for (let i = 0, j = xs.length - 1; i < j; i = i + 1, j = j - 1) {"],
                    difficulty="Medium"),
                _ex("tscourse-w21-sp-4", "Measure the recursion depth",
                    "Track how deep the calls go, which is the auxiliary space the stack uses.",
                    _NUMS +
                    'let depth = 0;\n'
                    'let maxDepth = 0;\n'
                    'function total(xs: readonly number[], i: number): number {\n'
                    '  depth = depth + 1;\n'
                    '  maxDepth = Math.max(maxDepth, depth);\n'
                    '  const answer = i >= xs.length ? 0 : (xs[i] ?? 0) + total(xs, i + 1);\n'
                    '  depth = depth - 1;\n'
                    '  return answer;\n}\n'
                    'console.log(`total=${total(nums, 0)} maxDepth=${maxDepth}`);\n',
                    '  maxDepth = Math.max(maxDepth, depth);',
                    [("1 2 3", "total=6 maxDepth=4"), ("5", "total=5 maxDepth=2")],
                    hints=["Record the high-water mark right after going one level deeper.",
                           "Write maxDepth = Math.max(maxDepth, depth);"],
                    difficulty="Medium"),
                _ex("tscourse-w21-sp-5", "The depth limit is real",
                    "Recurse deep enough to hit Node's stack limit, and catch the error it throws.",
                    'function deep(n: number): number {\n'
                    '  return n === 0 ? 0 : 1 + deep(n - 1);\n}\n'
                    'try {\n'
                    '  deep(1000000);\n'
                    '  console.log("no limit");\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof RangeError ? "RangeError" : "other");\n}\n',
                    '} catch (err) {', [("", "RangeError")],
                    hints=["A million frames is far past what the call stack can hold.",
                           "Write } catch (err) {"],
                    difficulty="Medium"),
                _ex("tscourse-w21-sp-6", "Trading memory for time",
                    "Memoise the recursion in a Map, and count the calls it saves.",
                    _NUMS +
                    'let calls = 0;\n'
                    'const memo = new Map<number, number>();\n'
                    'function fib(n: number): number {\n'
                    '  calls = calls + 1;\n'
                    '  const hit = memo.get(n);\n'
                    '  if (hit !== undefined) {\n'
                    '    return hit;\n  }\n'
                    '  const answer = n < 2 ? n : fib(n - 1) + fib(n - 2);\n'
                    '  memo.set(n, answer);\n'
                    '  return answer;\n}\n'
                    'const n = nums[0] ?? 0;\n'
                    'console.log(`fib(${n})=${fib(n)} calls=${calls} memo=${memo.size}`);\n',
                    '  const hit = memo.get(n);\n'
                    '  if (hit !== undefined) {\n'
                    '    return hit;\n  }',
                    [("15", "fib(15)=610 calls=29 memo=16"), ("10", "fib(10)=55 calls=19 memo=11")],
                    hints=["Look in the table before doing any work.",
                           "Week 19's read-or-miss: `memo.get(n)`, and return it if it is there.",
                           "Compare 29 calls against the 1,973 the naive version made."],
                    difficulty="Hard"),
                _fix("tscourse-w21-sp-fix1", "Fix the space that was not constant",
                     "This claims O(1) auxiliary space and allocates a whole copy to get the maximum. Track the best as you go instead — the answer is the same and the extra slots drop to zero.",
                     _NUMS +
                     'let slots = 0;\n'
                     'const copy: number[] = [];\n'
                     'for (const n of nums) {\n'
                     '  copy.push(n);\n'
                     '  slots = slots + 1;\n}\n'
                     'copy.sort((a, b) => b - a);\n'
                     'console.log(`max=${copy[0] ?? 0} slots=${slots}`);\n',
                     _NUMS +
                     'let slots = 0;\n'
                     'let max = 0;\n'
                     'for (const n of nums) {\n'
                     '  max = Math.max(max, n);\n}\n'
                     'console.log(`max=${max} slots=${slots}`);\n',
                     [("3 1 4", "max=4 slots=0"), ("7", "max=7 slots=0")],
                     hints=["Copying and sorting to find one value is O(n) space and O(n log n) time.",
                            "One variable is enough to hold the largest seen so far.",
                            "The whole loop body becomes `max = Math.max(max, n);`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("An iterative traversal's space complexity versus the recursive one is…",
                   ["better", "the same order — but a heap array can grow where the call stack cannot",
                    "worse", "O(1)"], 1,
                   "Which is the real reason to convert."),
                _q("In-place is not automatically better because…",
                   ["it is slower", "it destroys the caller's data — week 13's argument", "of types",
                    "of space"], 1,
                   "`readonly` is usually worth the copy."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w21-cases", "Best, average, worst — and amortised",
            "Four different questions, and which one is a promise.",
            """
"What is the complexity of a Map lookup?" has more than one correct answer, and
they are answers to different questions.

## The three cases

* **Best case** — the most convenient input. Almost never interesting: every
  algorithm has a lucky input.
* **Average case** — typical input. What a hash map's famous O(1) actually is.
* **Worst case** — the most inconvenient input. **The default**, because it is the
  only one that is a *guarantee*.

```ts
xs.includes(v);        // best O(1) — it is the first element
                        // worst O(n) — it is last, or absent
map.get(k);            // average O(1) — worst O(n), if every key collides
quicksort(xs);          // average O(n log n) — worst O(n²), on sorted input
naiveBstInsert(t, v);   // O(log n) balanced — O(n) on sorted input (week 20)
```

When somebody says a complexity without qualifying it, they mean worst case,
**except** for hash tables, where everybody says O(1) and means average. That
inconsistency is a convention, not a rule, and it is worth being explicit when it
matters.

## Adversarial input is real

The worst case matters because input is not always accidental. Sorted data arriving
at a naive BST is the common accident; a deliberately-chosen set of colliding keys
is an actual denial-of-service technique that real hash-table implementations
defend against with randomised hashing. "The worst case never happens" is a
statement about your users, and it is only as true as your least friendly user.

## Amortised

Different from average, and the distinction is worth having:

* **Average** — over the *distribution of inputs*.
* **Amortised** — over a *sequence of operations*, where one expensive step pays
  for many cheap ones.

```ts
xs.push(v);           // amortised O(1): occasionally the array is reallocated
                       // and everything copied — but only every n pushes, so the
                       // cost spread over n pushes is constant
```

Two more from this course:

* **Week 18's head-index queue with compaction** — one O(n) compaction every O(n)
  dequeues, so O(1) amortised.
* **Week 18's two-stack queue** — each element moves across exactly once, so the
  expensive pour is paid for by the cheap pops that follow.

The accounting is the same in all three: **count the total work over the whole
sequence, then divide.** An operation that is occasionally O(n) can still be O(1)
amortised, and that is not a weasel — it is a stronger statement than "usually
fast", because it bounds the total.

## What to say in an interview

> "Average O(1), worst case O(n) if every key hashes to the same bucket. In
> practice O(1)."

Three clauses: the useful number, the honest caveat, the practical conclusion. That
answer is better than either "O(1)" or "well, it depends" on its own.

> ⚠️ **Common mistakes:** quoting the average case as though it were a guarantee;
> confusing amortised with average; and assuming the worst case is hypothetical.
""",
            warmup=[
                _q("An unqualified complexity normally means…",
                   ["best case", "worst case", "average case", "amortised"], 1,
                   "Except for hash tables, by convention."),
                _q("A hash map's O(1) is…",
                   ["worst case", "average case", "amortised", "best case"], 1,
                   "The worst case is O(n)."),
                _q("Amortised is averaged over…",
                   ["inputs", "a sequence of operations", "machines", "time"], 1,
                   "One expensive step paying for many cheap ones."),
                _q("`arr.push` is amortised O(1) because…",
                   ["it never reallocates", "a reallocation happens only every n pushes, so the cost per push is constant",
                    "it is native", "arrays are fixed"], 1,
                   "Count the total, then divide."),
            ],
            exercises=[
                _ex("tscourse-w21-ca-1", "Best and worst, counted",
                    "Search for the first element and then for a missing one, and report both costs.",
                    'function steps(xs: readonly number[], target: number): number {\n'
                    '  let count = 0;\n'
                    '  for (const x of xs) {\n'
                    '    count = count + 1;\n'
                    '    if (x === target) {\n'
                    '      return count;\n    }\n  }\n'
                    '  return count;\n}\n'
                    'const xs = [1, 2, 3, 4, 5, 6, 7, 8];\n'
                    'console.log(`best=${steps(xs, 1)} worst=${steps(xs, 99)}`);\n',
                    'console.log(`best=${steps(xs, 1)} worst=${steps(xs, 99)}`);',
                    [("", "best=1 worst=8")],
                    hints=["The first element is the lucky case; an absent one is the unlucky one.",
                           "Write console.log(`best=${steps(xs, 1)} worst=${steps(xs, 99)}`);"],
                    difficulty="Easy"),
                _ex("tscourse-w21-ca-2", "Sorted input is the worst case",
                    "Insert ascending values into a naive BST and measure the depth it reaches.",
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'function depth(t: T | null): number {\n'
                    '  if (t === null) {\n'
                    '    return 0;\n  }\n'
                    '  return 1 + Math.max(depth(t.left), depth(t.right));\n}\n'
                    'function depthFor(order: readonly number[]): number {\n'
                    '  let root: T | null = null;\n'
                    '  for (const n of order) {\n'
                    '    root = insert(root, n);\n  }\n'
                    '  return depth(root);\n}\n'
                    'console.log(`sorted=${depthFor([1, 2, 3, 4, 5, 6, 7])}`);\n'
                    'console.log(`balanced=${depthFor([4, 2, 6, 1, 3, 5, 7])}`);\n',
                    'console.log(`sorted=${depthFor([1, 2, 3, 4, 5, 6, 7])}`);',
                    [("", "sorted=7\nbalanced=3")],
                    hints=["Ascending input sends every node down the right-hand side.",
                           "Write console.log(`sorted=${depthFor([1, 2, 3, 4, 5, 6, 7])}`);"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ca-3", "Amortised, counted over a sequence",
                    "Count the copies a doubling array makes across many pushes, and divide.",
                    'let copies = 0;\n'
                    'let capacity = 1;\n'
                    'let size = 0;\n'
                    'function push(): void {\n'
                    '  if (size === capacity) {\n'
                    '    copies = copies + size;\n'
                    '    capacity = capacity * 2;\n  }\n'
                    '  size = size + 1;\n}\n'
                    'for (let i = 0; i < 16; i = i + 1) {\n'
                    '  push();\n}\n'
                    'console.log(`pushes=16 copies=${copies} perPush=${copies / 16}`);\n',
                    '    copies = copies + size;\n'
                    '    capacity = capacity * 2;',
                    [("", "pushes=16 copies=15 perPush=0.9375")],
                    hints=["A reallocation copies everything currently stored, then doubles the capacity.",
                           "Fifteen copies across sixteen pushes is under one per push — that is amortised O(1)."],
                    difficulty="Hard"),
                _ex("tscourse-w21-ca-4", "Average versus worst for a lookup",
                    "Count the comparisons a bucketed lookup makes when every key collides.",
                    'const buckets: string[][] = [[], [], [], []];\n'
                    'function badHash(_key: string): number {\n'
                    '  return 0;\n}\n'
                    'let comparisons = 0;\n'
                    'function add(key: string): void {\n'
                    '  const b = buckets[badHash(key)] ?? [];\n'
                    '  b.push(key);\n}\n'
                    'function has(key: string): boolean {\n'
                    '  const b = buckets[badHash(key)] ?? [];\n'
                    '  for (const k of b) {\n'
                    '    comparisons = comparisons + 1;\n'
                    '    if (k === key) {\n'
                    '      return true;\n    }\n  }\n'
                    '  return false;\n}\n'
                    'for (const k of ["a", "b", "c", "d"]) {\n'
                    '  add(k);\n}\n'
                    'console.log(`${has("d")} comparisons=${comparisons}`);\n',
                    '    comparisons = comparisons + 1;',
                    [("", "true comparisons=4")],
                    hints=["Every key landing in one bucket makes the lookup a linear scan.",
                           "Write comparisons = comparisons + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w21-ca-5", "The three-clause answer",
                    "Print the answer to give in an interview: the number, the caveat, the conclusion.",
                    'const answer = [\n'
                    '  "average O(1)",\n'
                    '  "worst O(n) if every key collides",\n'
                    '  "in practice O(1)",\n'
                    '];\n'
                    'console.log(answer.join("; "));\n',
                    'console.log(answer.join("; "));',
                    [("", "average O(1); worst O(n) if every key collides; in practice O(1)")],
                    hints=["Three clauses, joined.",
                           'Write console.log(answer.join("; "));'],
                    difficulty="Easy"),
                _fix("tscourse-w21-ca-fix1", "Fix the worst case that was measured as the best",
                     "This reports the linear search as costing one step, because it always looks for the first element. A worst-case measurement has to use worst-case input — the value that is not there.",
                     'function steps(xs: readonly number[], target: number): number {\n'
                     '  let count = 0;\n'
                     '  for (const x of xs) {\n'
                     '    count = count + 1;\n'
                     '    if (x === target) {\n'
                     '      return count;\n    }\n  }\n'
                     '  return count;\n}\n'
                     'for (const n of [4, 8, 16]) {\n'
                     '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                     '  console.log(`n=${n} worst=${steps(xs, 0)}`);\n}\n',
                     'function steps(xs: readonly number[], target: number): number {\n'
                     '  let count = 0;\n'
                     '  for (const x of xs) {\n'
                     '    count = count + 1;\n'
                     '    if (x === target) {\n'
                     '      return count;\n    }\n  }\n'
                     '  return count;\n}\n'
                     'for (const n of [4, 8, 16]) {\n'
                     '  const xs = Array.from({ length: n }, (_, i) => i);\n'
                     '  console.log(`n=${n} worst=${steps(xs, -1)}`);\n}\n',
                     [("", "n=4 worst=4\nn=8 worst=8\nn=16 worst=16")],
                     hints=["`0` is the FIRST element of every one of these arrays.",
                            "The worst case for a linear search is a target that is never found.",
                            "Search for a value that cannot be in the array."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Colliding hash keys as a denial-of-service technique is…",
                   ["theoretical", "real, and defended against with randomised hashing", "impossible",
                    "a bug"], 1,
                   "Which is why the worst case is not hypothetical."),
                _q("Amortised O(1) is a stronger statement than \"usually fast\" because…",
                   ["it is shorter", "it bounds the TOTAL work over the sequence", "it is average",
                    "it is worst case"], 1,
                   "Count the total, then divide."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w21-read", "Reading it off unfamiliar code",
            "The interview skill, which is a checklist.",
            """
You will be shown code you have not seen and asked what it costs. This is
mechanical:

1. **What is n?** Which input does the cost depend on? Sometimes there are two —
   `n` rows and `m` columns — and the answer is O(n·m), not O(n²).
2. **What is the innermost repeated operation?**
3. **How many times does it run, in terms of n?**
4. **Does any call in that loop hide a loop?** (`includes`, `shift`, `indexOf`,
   string `+`, `splice`, a sort.)
5. **What is allocated?** That is the space answer.
6. **Is there a worse input than the one in front of you?**

## Worked: two inputs

```ts
function pairs(rows: readonly string[], cols: readonly string[]): number {
  let n = 0;
  for (const r of rows) {
    for (const c of cols) { n = n + r.length + c.length; }
  }
  return n;
}
```

n is `rows.length`, m is `cols.length`. The body runs n·m times. **O(n·m)**, and
saying O(n²) here is wrong unless the two are known to be equal.

## Worked: the hidden sort

```ts
function topOf(xs: readonly number[]): number {
  const sorted = [...xs].sort((a, b) => b - a);
  return sorted[0] ?? 0;
}
```

One line, no visible loop, **O(n log n)** time and **O(n)** space — for something a
single pass does in O(n) time and O(1) space. This is the most common real-world
version of the question, and it is lesson 5's `fix`.

## Worked: the loop that is not linear

```ts
for (let i = 1; i < n; i = i * 2) { … }
```

The index *multiplies*, so the loop runs log₂(n) times. **O(log n)**. Compare
`i = i + 2`, which runs n/2 times and is O(n) — a constant factor, dropped.

## Stating it well

Say the time, then the space, then the caveat:

> "O(n log n) time because of the sort, O(n) space for the copy — and it could be
> O(n) time and O(1) space with a single pass, since we only need the maximum."

That last clause is the one that gets you the job. Recognising the cost is table
stakes; knowing what to do about it is the point.

## And the sanity check

Before answering, ask: **is n actually large?** An O(n²) pass over a fixed list of
twelve months is correct, clear and fast. The best complexity answer sometimes
ends "…and it does not matter here".

> ⚠️ **Common mistakes:** saying O(n²) for two different inputs; missing a sort
> inside a helper; and optimising a loop over a list that will never exceed twenty
> items.
""",
            warmup=[
                _q("Nested loops over two DIFFERENT inputs are…",
                   ["O(n²)", "O(n·m)", "O(n)", "O(n + m)"], 1,
                   "Unless the two are known to be equal."),
                _q("`for (i = 1; i < n; i = i * 2)` runs…",
                   ["n times", "log₂(n) times", "n/2 times", "twice"], 1,
                   "The index multiplies."),
                _q("`for (i = 0; i < n; i = i + 2)` is…",
                   ["O(log n)", "O(n)", "O(n/2) and that is different", "O(1)"], 1,
                   "A constant factor, dropped."),
                _q("Sorting to get a maximum costs…",
                   ["O(n)", "O(n log n) time and O(n) space, for something a pass does in O(n)/O(1)",
                    "O(1)", "nothing"], 1,
                   "The commonest real version of this question."),
            ],
            exercises=[
                _ex("tscourse-w21-rd-1", "Two inputs, counted",
                    "Count the body's executions for a pair of different-sized inputs.",
                    'function cost(n: number, m: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    for (let j = 0; j < m; j = j + 1) {\n'
                    '      ops = ops + 1;\n    }\n  }\n'
                    '  return ops;\n}\n'
                    'console.log(`4x8=${cost(4, 8)} 8x8=${cost(8, 8)} 8x16=${cost(8, 16)}`);\n',
                    'console.log(`4x8=${cost(4, 8)} 8x8=${cost(8, 8)} 8x16=${cost(8, 16)}`);',
                    [("", "4x8=32 8x8=64 8x16=128")],
                    hints=["The count is the product of the two sizes.",
                           "Write console.log(`4x8=${cost(4, 8)} 8x8=${cost(8, 8)} 8x16=${cost(8, 16)}`);"],
                    difficulty="Easy"),
                _ex("tscourse-w21-rd-2", "The multiplying index",
                    "Advance by doubling, so the loop runs a logarithmic number of times.",
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 1; i < n; i = i * 2) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  return ops;\n}\n'
                    'for (const n of [8, 16, 32, 1024]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    '  for (let i = 1; i < n; i = i * 2) {',
                    [("", "n=8 ops=3\nn=16 ops=4\nn=32 ops=5\nn=1024 ops=10")],
                    hints=["The index doubles rather than incrementing.",
                           "Write for (let i = 1; i < n; i = i * 2) {"],
                    difficulty="Medium"),
                _ex("tscourse-w21-rd-3", "Adding two is still linear",
                    "Step by two, and confirm the count still doubles when n does.",
                    'function cost(n: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < n; i = i + 2) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  return ops;\n}\n'
                    'for (const n of [8, 16, 32]) {\n'
                    '  console.log(`n=${n} ops=${cost(n)}`);\n}\n',
                    '  for (let i = 0; i < n; i = i + 2) {',
                    [("", "n=8 ops=4\nn=16 ops=8\nn=32 ops=16")],
                    hints=["Half as many iterations as n, which is a constant factor.",
                           "Write for (let i = 0; i < n; i = i + 2) {"],
                    difficulty="Easy"),
                _ex("tscourse-w21-rd-4", "Find the hidden sort",
                    "Replace the sort-and-take-first with the single pass it was standing in for.",
                    _NUMS +
                    'let ops = 0;\n'
                    'let max = 0;\n'
                    'for (const n of nums) {\n'
                    '  ops = ops + 1;\n'
                    '  max = Math.max(max, n);\n}\n'
                    'console.log(`max=${max} ops=${ops}`);\n',
                    '  max = Math.max(max, n);',
                    [("3 1 4 1 5", "max=5 ops=5"), ("7", "max=7 ops=1")],
                    hints=["One comparison per element, no copy and no sort.",
                           "Write max = Math.max(max, n);"],
                    difficulty="Easy"),
                _ex("tscourse-w21-rd-5", "Say it in full",
                    "Report time, space and the improvement — the three-part answer.",
                    'const verdict = [\n'
                    '  "time O(n log n) from the sort",\n'
                    '  "space O(n) for the copy",\n'
                    '  "one pass would be O(n) time and O(1) space",\n'
                    '];\n'
                    'for (const part of verdict) {\n'
                    '  console.log(part);\n}\n',
                    'for (const part of verdict) {',
                    [("", "time O(n log n) from the sort\nspace O(n) for the copy\none pass would be O(n) time and O(1) space")],
                    hints=["Print each clause on its own line.",
                           "Write for (const part of verdict) {"],
                    difficulty="Easy"),
                _ex("tscourse-w21-rd-6", "…and when it does not matter",
                    "A quadratic pass over twelve months is fine. Count it and say so.",
                    'const MONTHS = 12;\n'
                    'let ops = 0;\n'
                    'for (let i = 0; i < MONTHS; i = i + 1) {\n'
                    '  for (let j = 0; j < MONTHS; j = j + 1) {\n'
                    '    ops = ops + 1;\n  }\n}\n'
                    'console.log(`ops=${ops} verdict=${ops < 1000 ? "fine" : "rethink"}`);\n',
                    'console.log(`ops=${ops} verdict=${ops < 1000 ? "fine" : "rethink"}`);',
                    [("", "ops=144 verdict=fine")],
                    hints=["144 operations is nothing, whatever its growth class.",
                           'Write console.log(`ops=${ops} verdict=${ops < 1000 ? "fine" : "rethink"}`);'],
                    difficulty="Easy"),
                _fix("tscourse-w21-rd-fix1", "Fix the answer that said O(n²)",
                     "The classifier reports `O(n^2)` for a nested loop over two *different* inputs, which is only right when the two happen to be the same size. Report the honest product.",
                     'function describe(n: number, m: number): string {\n'
                     '  let ops = 0;\n'
                     '  for (let i = 0; i < n; i = i + 1) {\n'
                     '    for (let j = 0; j < m; j = j + 1) {\n'
                     '      ops = ops + 1;\n    }\n  }\n'
                     '  return `ops=${ops} class=O(n^2)`;\n}\n'
                     'console.log(describe(4, 8));\n'
                     'console.log(describe(8, 2));\n',
                     'function describe(n: number, m: number): string {\n'
                     '  let ops = 0;\n'
                     '  for (let i = 0; i < n; i = i + 1) {\n'
                     '    for (let j = 0; j < m; j = j + 1) {\n'
                     '      ops = ops + 1;\n    }\n  }\n'
                     '  return `ops=${ops} class=O(n*m)`;\n}\n'
                     'console.log(describe(4, 8));\n'
                     'console.log(describe(8, 2));\n',
                     [("", "ops=32 class=O(n*m)\nops=16 class=O(n*m)")],
                     hints=["The two loops are bounded by different things.",
                            "Doubling only `m` doubles the count, which no n² can describe.",
                            "Report the product of the two sizes."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("The clause that gets you the job is…",
                   ["the class", "what you would do about it", "the space", "the caveat"], 1,
                   "Recognising the cost is table stakes."),
                _q("A complexity answer may legitimately end…",
                   ["with a number", "\"…and it does not matter here\"", "with a caveat",
                    "with the space"], 1,
                   "When n is bounded and small."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #21 — the complexity report",
        """
This is the first of the **interview reps**. Budget Buddy's arc ended last week;
from here the capstone is a timed problem in the week's technique, and this one
builds the instrument the rest of the course is measured with.

Write a harness that runs four instrumented algorithms at `n` and at `2n`, and
names each one's growth class from the ratio of the operation counts.

Input: one line, the base size `n`.

```
16
```

```
sum             16       32  ratio 2.00  O(n)
binary           5        6  ratio 1.20  O(log n)
pairs          120      496  ratio 4.13  O(n^2)
dedupe         120      496  ratio 4.13  O(n^2)
Slowest:      pairs
```

**The four algorithms**, each counting its own dominant operation:

1. `sum` — one pass over n numbers. Count the additions.
2. `binary` — binary search for the last element of a sorted array of n. Count the
   iterations.
3. `pairs` — every unordered pair: `for i`, `for j = i + 1`. Count the inner steps.
4. `dedupe` — week 19's quadratic de-duplication: for each element, count the
   length of the accumulated array that `includes` would scan.

**The classifier**, from the ratio of the count at 2n to the count at n:

| ratio | class |
|---|---|
| < 1.2 | `O(1)` |
| < 1.5 | `O(log n)` |
| < 2.5 | `O(n)` |
| < 3.5 | `O(n log n)` |
| otherwise | `O(n^2)` |

Bands rather than exact matches, because at these sizes the lower-order terms are
still visible — `pairs` at 16→32 gives 4.13, not 4.00, and that is the honest
number rather than a bug.

**The format:** the name padded to 10, then each count padded to 8, then
`ratio X.XX` to two decimals, then the class. `Slowest:` names the algorithm with
the highest ratio, ties broken by the order above.

`n` of 0 or a non-numeric line means no measurement is possible: print
`n must be at least 2` and nothing else.
""",
        _ch("tscourse-w21-capstone", "Interview rep #21", "Hard",
            "Instrument four algorithms, run each at n and 2n, and name its growth class from "
            "the ratio of the counts.",
            _FS +
            'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
            'function sized(size: number): readonly number[] {\n'
            '  return Array.from({ length: size }, (_, i) => i + 1);\n}\n'
            'function sumOps(size: number): number {\n'
            '  let ops = 0;\n'
            '  let total = 0;\n'
            '  for (const x of sized(size)) {\n'
            '    ops = ops + 1;\n'
            '    total = total + x;\n  }\n'
            '  return ops + total * 0;\n}\n'
            'function binaryOps(size: number): number {\n'
            '  const xs = sized(size);\n'
            '  const target = size;\n'
            '  let lo = 0;\n'
            '  let hi = xs.length - 1;\n'
            '  let ops = 0;\n'
            '  while (lo <= hi) {\n'
            '    ops = ops + 1;\n'
            '    const mid = Math.floor((lo + hi) / 2);\n'
            '    const v = xs[mid] ?? 0;\n'
            '    if (v === target) {\n'
            '      return ops;\n    }\n'
            '    if (v < target) {\n'
            '      lo = mid + 1;\n'
            '    } else {\n'
            '      hi = mid - 1;\n    }\n  }\n'
            '  return ops;\n}\n'
            'function pairOps(size: number): number {\n'
            '  let ops = 0;\n'
            '  for (let i = 0; i < size; i = i + 1) {\n'
            '    for (let j = i + 1; j < size; j = j + 1) {\n'
            '      ops = ops + 1;\n    }\n  }\n'
            '  return ops;\n}\n'
            'function dedupeOps(size: number): number {\n'
            '  let ops = 0;\n'
            '  const seen: number[] = [];\n'
            '  for (const x of sized(size)) {\n'
            '    ops = ops + seen.length;\n'
            '    if (!seen.includes(x)) {\n'
            '      seen.push(x);\n    }\n  }\n'
            '  return ops;\n}\n'
            'function classify(ratio: number): string {\n'
            '  if (ratio < 1.2) {\n'
            '    return "O(1)";\n  }\n'
            '  if (ratio < 1.5) {\n'
            '    return "O(log n)";\n  }\n'
            '  if (ratio < 2.5) {\n'
            '    return "O(n)";\n  }\n'
            '  if (ratio < 3.5) {\n'
            '    return "O(n log n)";\n  }\n'
            '  return "O(n^2)";\n}\n'
            'if (!Number.isFinite(n) || n < 2) {\n'
            '  console.log("n must be at least 2");\n'
            '} else {\n'
            '  const algorithms: readonly [string, (size: number) => number][] = [\n'
            '    ["sum", sumOps],\n'
            '    ["binary", binaryOps],\n'
            '    ["pairs", pairOps],\n'
            '    ["dedupe", dedupeOps],\n'
            '  ];\n'
            '  let slowest = "none";\n'
            '  let worstRatio = -1;\n'
            '  for (const [name, run] of algorithms) {\n'
            '    const small = run(n);\n'
            '    const big = run(n * 2);\n'
            '    const ratio = small === 0 ? 1 : big / small;\n'
            '    if (ratio > worstRatio) {\n'
            '      slowest = name;\n      worstRatio = ratio;\n    }\n'
            '    console.log(\n'
            '      `${name.padEnd(10)}${String(small).padStart(8)} ${String(big).padStart(8)}` +\n'
            '        `  ratio ${ratio.toFixed(2)}  ${classify(ratio)}`,\n'
            '    );\n  }\n'
            '  console.log(`Slowest:      ${slowest}`);\n}\n',
            'function classify(ratio: number): string {\n'
            '  if (ratio < 1.2) {\n'
            '    return "O(1)";\n  }\n'
            '  if (ratio < 1.5) {\n'
            '    return "O(log n)";\n  }\n'
            '  if (ratio < 2.5) {\n'
            '    return "O(n)";\n  }\n'
            '  if (ratio < 3.5) {\n'
            '    return "O(n log n)";\n  }\n'
            '  return "O(n^2)";\n}\n'
            'if (!Number.isFinite(n) || n < 2) {\n'
            '  console.log("n must be at least 2");\n'
            '} else {\n'
            '  const algorithms: readonly [string, (size: number) => number][] = [\n'
            '    ["sum", sumOps],\n'
            '    ["binary", binaryOps],\n'
            '    ["pairs", pairOps],\n'
            '    ["dedupe", dedupeOps],\n'
            '  ];\n'
            '  let slowest = "none";\n'
            '  let worstRatio = -1;\n'
            '  for (const [name, run] of algorithms) {\n'
            '    const small = run(n);\n'
            '    const big = run(n * 2);\n'
            '    const ratio = small === 0 ? 1 : big / small;\n'
            '    if (ratio > worstRatio) {\n'
            '      slowest = name;\n      worstRatio = ratio;\n    }\n'
            '    console.log(\n'
            '      `${name.padEnd(10)}${String(small).padStart(8)} ${String(big).padStart(8)}` +\n'
            '        `  ratio ${ratio.toFixed(2)}  ${classify(ratio)}`,\n'
            '    );\n  }\n'
            '  console.log(`Slowest:      ${slowest}`);\n}',
            [("16",
               "sum             16       32  ratio 2.00  O(n)\nbinary           5        6  ratio 1.20  O(log n)\npairs          120      496  ratio 4.13  O(n^2)\ndedupe         120      496  ratio 4.13  O(n^2)\nSlowest:      pairs"), ("4",
               "sum              4        8  ratio 2.00  O(n)\nbinary           3        4  ratio 1.33  O(log n)\npairs            6       28  ratio 4.67  O(n^2)\ndedupe           6       28  ratio 4.67  O(n^2)\nSlowest:      pairs"), ("1", "n must be at least 2"),
             ("oops", "n must be at least 2")],
            hints=["Each `*Ops` function returns a COUNT, never a duration — nothing in this program measures time.",
                   "Run each algorithm twice: once at n, once at 2n, and take the ratio of the two counts.",
                   "The bands are deliberately wide: `pairs` at 16→32 gives 4.13, not 4.00, because the lower-order term is still visible.",
                   "`ratio.toFixed(2)` for the two decimals; `padEnd(10)` for the name and `padStart(8)` for each count.",
                   "A strict `>` on the slowest comparison keeps the FIRST of any tie, which is why the order of the array matters.",
                   "Guard `n` with `Number.isFinite` before anything else — `Number(\"oops\")` is NaN, and NaN fails every comparison."]),
        example_io="sum             16       32  ratio 2.00  O(n)\nbinary           5        6  ratio 1.20  O(log n)\npairs          120      496  ratio 4.13  O(n^2)\ndedupe         120      496  ratio 4.13  O(n^2)\nSlowest:      pairs",
        rubric=["every measurement is a count of operations; nothing measures elapsed time",
                "each algorithm is run at n and at 2n, and the class comes from the ratio",
                "the classifier uses bands, and the code says why exact ratios are not expected",
                "the counters are reset (or local) per run, so no measurement includes another",
                "`binary` searches for the last element, which is its worst case",
                "`dedupe` counts the length `includes` would scan, not one per element",
                "non-numeric and too-small input print the guard message and nothing else",
                "columns line up through padEnd/padStart rather than hand-spacing"],
        stretch=_ch("tscourse-w21-capstone-stretch", "Interview rep #21 (stretch)", "Hard",
                    "Add a third data point. Run each algorithm at n, 2n and 4n and report BOTH "
                    "ratios, then flag any algorithm whose two ratios disagree by more than 0.5 as "
                    "`unstable` — which is how you notice that a measurement at small n has not "
                    "settled down yet. Print the classification from the SECOND ratio, since it is "
                    "the more trustworthy one.",
                    _FS +
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'function pairOps(size: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < size; i = i + 1) {\n'
                    '    for (let j = i + 1; j < size; j = j + 1) {\n'
                    '      ops = ops + 1;\n    }\n  }\n'
                    '  return ops;\n}\n'
                    'function sumOps(size: number): number {\n'
                    '  let ops = 0;\n'
                    '  for (let i = 0; i < size; i = i + 1) {\n'
                    '    ops = ops + 1;\n  }\n'
                    '  return ops;\n}\n'
                    'function classify(ratio: number): string {\n'
                    '  if (ratio < 1.5) {\n'
                    '    return "O(log n)";\n  }\n'
                    '  if (ratio < 2.5) {\n'
                    '    return "O(n)";\n  }\n'
                    '  if (ratio < 3.5) {\n'
                    '    return "O(n log n)";\n  }\n'
                    '  return "O(n^2)";\n}\n'
                    'function report(name: string, run: (size: number) => number): void {\n'
                    '  const a = run(n);\n'
                    '  const b = run(n * 2);\n'
                    '  const c = run(n * 4);\n'
                    '  const r1 = a === 0 ? 1 : b / a;\n'
                    '  const r2 = b === 0 ? 1 : c / b;\n'
                    '  const unstable = Math.abs(r1 - r2) > 0.5;\n'
                    '  console.log(\n'
                    '    `${name.padEnd(10)}${r1.toFixed(2)} ${r2.toFixed(2)}  ${classify(r2)}` +\n'
                    '      `${unstable ? "  unstable" : ""}`,\n'
                    '  );\n}\n'
                    'if (!Number.isFinite(n) || n < 2) {\n'
                    '  console.log("n must be at least 2");\n'
                    '} else {\n'
                    '  report("sum", sumOps);\n'
                    '  report("pairs", pairOps);\n}\n',
                    'function report(name: string, run: (size: number) => number): void {\n'
                    '  const a = run(n);\n'
                    '  const b = run(n * 2);\n'
                    '  const c = run(n * 4);\n'
                    '  const r1 = a === 0 ? 1 : b / a;\n'
                    '  const r2 = b === 0 ? 1 : c / b;\n'
                    '  const unstable = Math.abs(r1 - r2) > 0.5;\n'
                    '  console.log(\n'
                    '    `${name.padEnd(10)}${r1.toFixed(2)} ${r2.toFixed(2)}  ${classify(r2)}` +\n'
                    '      `${unstable ? "  unstable" : ""}`,\n'
                    '  );\n}',
                    [("4", "sum       2.00 2.00  O(n)\npairs     4.67 4.29  O(n^2)"), ("16", "sum       2.00 2.00  O(n)\npairs     4.13 4.06  O(n^2)"), ("1", "n must be at least 2")],
                    hints=["Three runs per algorithm, and two consecutive ratios between them.",
                           "The later ratio is the more trustworthy one, because the lower-order terms have faded.",
                           "`Math.abs(r1 - r2) > 0.5` is the instability test.",
                           "At n=4 the quadratic's ratios are 4.67 and 4.29 — a gap of 0.38, so not flagged."]),
    ),
))
