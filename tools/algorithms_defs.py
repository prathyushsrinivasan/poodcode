# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Language-agnostic Algorithms Learn track.
#
# This file is exec()'d inside gen_seed.py's namespace (see the hook after the
# Japanese track). It extends CONCEPTS / CATEGORY / LESSONS in place with a set
# of concepts that teach *the algorithm itself* — intuition, pseudocode, cost,
# invariants, and when to reach for it — rather than any single language's
# syntax. Every concept is marked  "language": "algorithms"  so the Learn tab's
# language toggle shows them under their own 🧠 Algorithms view, next to Java,
# TypeScript and Japanese.
#
# WHY IT NEEDS NO CODE JUDGE:
#   These concepts are graded through two features that do NOT run code:
#     * a Markdown lesson (pseudocode, complexity, worked trace tables),
#     * multiple-choice self-check quizzes (`quiz`, graded client-side by the
#       chosen option index),
#   plus curated pointers into the real problem bank (`practice`, resolved by
#   slug in the frontend). So there is no SEED_VERSION / SQLite impact — the
#   catalog is embedded JSON, rebuilt by `python tools/gen_seed.py`.
#
# TABLE / MARKDOWN NOTE:
#   The renderer is react-markdown + remark-gfm WITHOUT rehype-raw, so raw HTML
#   never renders and a literal '|' must never appear inside a table cell. Use
#   fenced code blocks for pseudocode.
#
# This file covers Tier 0 (Foundations) and Tier 1 (Core Techniques).
# ---------------------------------------------------------------------------

ALG_LANG = "algorithms"


def _q(question, options, answer, explanation):
    """One multiple-choice quiz question. `answer` is the 0-based index of the
    correct option; asserted in range so a typo fails the build, not the app."""
    assert len(options) >= 2, f"quiz needs >=2 options: {question!r}"
    assert 0 <= answer < len(options), f"quiz answer out of range: {question!r}"
    assert explanation, f"quiz needs an explanation: {question!r}"
    return {
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def _p(slug, note=""):
    """A curated Library problem to practice a concept on (resolved by slug)."""
    return {"slug": slug, "note": note}


def _alg(key, name, category, what, deep, glance, lesson, quiz=None, practice=None):
    """Register one language-agnostic algorithm concept."""
    assert key not in CONCEPTS, f"algorithms: duplicate concept key {key!r}"
    CONCEPTS[key] = {
        "name": name,
        "what": what,
        "deep": deep,
        "java": glance,          # shown in the accent "At a glance" card
        "language": ALG_LANG,
        "quiz": quiz or [],
        "practice": practice or [],
    }
    CATEGORY[key] = category
    LESSONS[key] = lesson.strip() + "\n"
    EXERCISES.setdefault(key, [])   # no code drills — this track is language-agnostic


CAT_FOUND = "Algo: Foundations"
CAT_SEARCH = "Algo: Searching & Scanning"
CAT_SORT = "Algo: Sorting"
CAT_RECUR = "Algo: Recursion"


# ===========================================================================
# TIER 0 — FOUNDATIONS
# ===========================================================================

# --- 0.1 What is an algorithm? --------------------------------------------
_alg(
    "alg_what_is",
    "What Is an Algorithm?",
    CAT_FOUND,
    "A precise recipe that turns input into the right output — and the two yardsticks we judge it by.",
    "An algorithm is a finite, unambiguous sequence of steps that transforms an "
    "input into a desired output. Every step must be well-defined and the whole "
    "thing must eventually stop. We judge an algorithm on two axes: is it "
    "correct (does it produce the right answer for every valid input?) and is it "
    "efficient (how does its time and memory grow as the input grows?). "
    "Correctness comes first — a fast wrong answer is worthless — but among "
    "correct solutions we prefer the one that scales.",
    "**Correctness** — right answer on *every* valid input, edge cases included.\n\n"
    "**Efficiency** — how time & memory grow with input size *n*.\n\n"
    "A good solution is *correct first, efficient second*.",
    """
An **algorithm** is a finite list of unambiguous steps that turns an *input*
into the correct *output*. Three properties make it an algorithm rather than
just "some code":

1. **Finiteness** — it terminates after a finite number of steps.
2. **Definiteness** — every step is precisely defined; no "do the obvious thing".
3. **Effectiveness** — each step is simple enough to actually be carried out.

## The two yardsticks

Every algorithm is judged on two independent axes:

- **Correctness** — does it give the right answer for *every* valid input,
  including the awkward edge cases (empty input, one element, all-equal,
  negatives, the largest allowed value)?
- **Efficiency** — how do its running time and memory use *grow* as the input
  grows? This is what [Big-O notation](#) captures.

> Correctness always wins ties. A blazing-fast function that's wrong on empty
> input is worse than a slow one that's always right. Get it correct, *then*
> make it fast.

## A tiny example — is a number even?

```text
function isEven(n):
    return (n mod 2) == 0
```

Trace it on a few inputs to convince yourself it's correct:

| Input n | n mod 2 | Output |
|---|---|---|
| 4 | 0 | true |
| 7 | 1 | false |
| 0 | 0 | true |
| -3 | depends on language's mod | ⚠️ careful |

That last row is the whole game: an algorithm is only correct once you've
pinned down the awkward cases. In some languages `-3 mod 2` is `-1`, not `1` —
so `== 0` still works here, but *thinking about it* is the habit that separates
a correct solution from a lucky one.

## The engineering loop

When you meet a problem, work in this order:

1. **Understand** the exact input, output, and constraints.
2. Find *a* correct approach (even a brute-force one).
3. **Analyze** its cost.
4. **Improve** the cost only if the constraints demand it.

The rest of this track gives you the vocabulary for steps 3 and 4, then a
toolbox of techniques for step 4.

### Key takeaways
- An algorithm = finite + definite + effective steps from input to output.
- Judge it on **correctness** and **efficiency**, in that priority order.
- Edge cases are part of correctness, not an afterthought.
""",
    quiz=[
        _q(
            "Which pair of properties do we use to judge an algorithm?",
            ["Length and readability", "Correctness and efficiency",
             "Language and framework", "Number of lines and comments"],
            1,
            "We ask two things of every algorithm: does it produce the right answer for all valid inputs (correctness), and how well does it scale (efficiency)?",
        ),
        _q(
            "You have two solutions: A is very fast but crashes on empty input; B is slower but always correct. Which is preferable as a starting point?",
            ["A, because speed matters most",
             "B, because correctness comes before efficiency",
             "Whichever is shorter",
             "They are equally good"],
            1,
            "A wrong-but-fast answer is worthless. Correctness is the first requirement; you optimize only among solutions that are already correct.",
        ),
        _q(
            "Which of these disqualifies a procedure from being an algorithm?",
            ["It uses a loop",
             "It might never terminate on some inputs",
             "It calls another function",
             "It uses more than O(1) memory"],
            1,
            "An algorithm must be finite — it has to terminate. A procedure that can loop forever on some input is not an algorithm.",
        ),
        _q(
            "Why do we care about how cost grows with input size n rather than the raw time in seconds?",
            ["Seconds are hard to spell",
             "Raw time depends on the machine, language, and load; growth rate is intrinsic to the algorithm",
             "Growth rate is always smaller",
             "Seconds only matter for sorting"],
            1,
            "Wall-clock time varies with hardware and language. The *growth rate* (Big-O) is a property of the algorithm itself, so it's what we reason about.",
        ),
    ],
    practice=[
        _p("even-or-odd", "The isEven example above, as a runnable problem."),
        _p("larger-of-two", "The simplest 'correct on every input' warm-up — mind the equal case."),
        _p("print-greeting", "Input in, exact output out: the whole shape of an algorithm."),
    ],
)


# --- 0.2 Big-O notation ----------------------------------------------------
_alg(
    "alg_big_o",
    "Big-O Notation",
    CAT_FOUND,
    "The language for how an algorithm's cost grows — drop the constants, keep the shape.",
    "Big-O describes the growth rate of an algorithm's cost as the input size n "
    "grows toward infinity. We keep only the fastest-growing term and drop "
    "constant factors, because for large n those dominate everything else: "
    "3n + 100 and n/2 are both O(n). The point isn't to predict exact "
    "runtimes — it's to compare how algorithms *scale* so you can tell an O(n) "
    "solution from an O(n^2) one before you ever run them.",
    "Keep the **dominant term**, drop **constants & lower terms**.\n\n"
    "`3n^2 + 5n + 9  →  O(n^2)`\n\n"
    "Ranking (best→worst): `O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n) < O(n!)`",
    """
**Big-O notation** answers one question: *as the input gets big, how fast does
the work grow?* It deliberately throws away detail so you can compare
algorithms without a stopwatch.

Two rules produce every Big-O you'll write:

1. **Drop constant factors.** `500n` and `n` both scale linearly → `O(n)`.
2. **Keep only the dominant term.** For large *n*, `n^2` dwarfs `n`, which
   dwarfs `1`. So `n^2 + 3n + 7 → O(n^2)`.

Why is this fair? Because we care about *large* inputs. At n = 1,000,000 an
O(n^2) algorithm does a trillion steps while an O(n) one does a million — the
constants are irrelevant next to that gap.

## The growth-rate ladder

From best to worst, the classes you meet constantly:

| Big-O | Name | Doubling n does what? | Typical source |
|---|---|---|---|
| O(1) | constant | nothing | array index, hash lookup |
| O(log n) | logarithmic | +1 step | binary search, balanced tree |
| O(n) | linear | doubles | one pass over the data |
| O(n log n) | linearithmic | a bit more than doubles | good sorting |
| O(n^2) | quadratic | ×4 | nested loop over all pairs |
| O(2^n) | exponential | squares | trying every subset |
| O(n!) | factorial | explodes | trying every ordering |

## Feel the difference

How many steps for each class as *n* grows:

| n | O(log n) | O(n) | O(n log n) | O(n^2) | O(2^n) |
|---|---|---|---|---|---|
| 10 | 3 | 10 | 33 | 100 | 1,024 |
| 100 | 7 | 100 | 664 | 10,000 | huge |
| 1,000 | 10 | 1,000 | 9,966 | 1,000,000 | astronomical |

The lesson: an O(n^2) algorithm is fine at n = 100 and hopeless at n = 100,000.
Reading the constraint on *n* in a problem often tells you which complexity
class you need to hit.

## O, Θ, Ω in one breath

- **O(f)** — an *upper* bound: grows *no faster* than f (the common one).
- **Ω(f)** — a *lower* bound: grows *at least* as fast as f.
- **Θ(f)** — both: grows *exactly* like f.

In interviews "Big-O" almost always means the worst-case upper bound, Θ in
spirit. Say "O(n)" and you'll be understood.

### Common pitfalls
- **Constants inside the same class don't matter, but the *class* does.** Two
  passes is still O(n); a nested pass is O(n^2).
- `O(log n)` has no base — `log₂` and `log₁₀` differ by a constant factor, which
  Big-O drops.
- Adding sequential phases *adds* (take the max: `O(n) + O(n log n) = O(n log n)`);
  nesting loops *multiplies* (`O(n) · O(n) = O(n^2)`).

### Key takeaways
- Drop constants, keep the dominant term.
- Memorize the ladder `1 < log n < n < n log n < n^2 < 2^n < n!`.
- The constraint on *n* hints at the complexity class you must reach.
""",
    quiz=[
        _q(
            "Simplify: 4n^2 + 100n + 3000 in Big-O.",
            ["O(n)", "O(n^2)", "O(4n^2)", "O(n^2 + n)"],
            1,
            "Keep only the dominant term (n^2) and drop constant factors and lower-order terms → O(n^2).",
        ),
        _q(
            "An algorithm makes two separate full passes over an array of size n, one after the other. Its complexity is:",
            ["O(n^2)", "O(2n) which is O(n)", "O(n log n)", "O(1)"],
            1,
            "Sequential phases add: n + n = 2n, and constant factors drop, so it's O(n). Nesting (not sequencing) would give O(n^2).",
        ),
        _q(
            "Which growth rate is best (scales best) for large n?",
            ["O(n^2)", "O(n log n)", "O(log n)", "O(n)"],
            2,
            "Order is O(log n) < O(n) < O(n log n) < O(n^2). Logarithmic grows slowest, so it scales best.",
        ),
        _q(
            "You combine an O(n) step followed by an O(n log n) sort. Total complexity?",
            ["O(n^2 log n)", "O(n log n)", "O(n)", "O(log n)"],
            1,
            "Sequential steps add, and the sum is dominated by the larger term: O(n) + O(n log n) = O(n log n).",
        ),
        _q(
            "Doubling n roughly quadruples the running time. Which class is this?",
            ["O(log n)", "O(n)", "O(n^2)", "O(2^n)"],
            2,
            "For O(n^2), replacing n with 2n gives (2n)^2 = 4n^2 — four times the work. That ×4 fingerprint means quadratic.",
        ),
        _q(
            "The problem says n can be up to 200,000 and the time limit is tight. Which target complexity is the safe aim?",
            ["O(n^2) — about 4×10^10 operations",
             "O(n log n) or better",
             "O(2^n)",
             "O(n!)"],
            1,
            "At n = 2×10^5, O(n^2) is ~4×10^10 operations — far too slow. O(n log n) (~3.5 million) comfortably fits, so aim there or better.",
        ),
    ],
    practice=[
        _p("array-sum", "One pass — the canonical O(n)."),
        _p("binary-search-first", "O(log n): each step halves the search space."),
        _p("contains-duplicate", "Compare the O(n^2) all-pairs idea with the O(n) hashing idea."),
    ],
)


# --- 0.3 Analyzing loops & recursion --------------------------------------
_alg(
    "alg_analyzing",
    "Analyzing Loops & Recursion",
    CAT_FOUND,
    "Read code and derive its Big-O — from nested loops to amortized costs.",
    "Deriving an algorithm's complexity is a mechanical skill once you know the "
    "rules: a loop that runs n times is O(n); nesting multiplies; a loop that "
    "halves its range each step is O(log n). Recursion costs (number of calls) × "
    "(work per call). And some operations look expensive but are cheap on "
    "average — an amortized cost — like appending to a dynamic array that "
    "occasionally doubles. This lesson turns 'staring at code' into a repeatable "
    "counting procedure.",
    "**Sequential** → add. **Nested** → multiply. **Halving** → log n.\n\n"
    "Recursion cost = (number of calls) × (work per call).\n\n"
    "**Amortized** = average per operation over a worst-case sequence.",
    """
Complexity analysis is just *counting the steps as a function of n*. Here's the
whole toolkit.

## Rule 1 — a simple loop is linear

```text
for i in 0 .. n-1:      # runs n times
    do O(1) work
```
→ **O(n)**. The body's constant work times n iterations.

## Rule 2 — nested loops multiply

```text
for i in 0 .. n-1:          # n times
    for j in 0 .. n-1:      #   n times each
        do O(1) work
```
→ **O(n · n) = O(n^2)**. Each extra nested level over the full range multiplies
by another n.

Watch the *bounds*, though. This one is **not** n^2:

```text
for i in 0 .. n-1:
    for j in i+1 .. n-1:   # shrinks: n-1, n-2, ... 1
        do O(1) work
```
The inner loop runs `(n-1) + (n-2) + ... + 1 = n(n-1)/2` times → still
**O(n^2)**, because n²/2 drops its constant. All-pairs work is quadratic even
when you only touch each pair once.

## Rule 3 — halving the range is logarithmic

```text
while n > 1:
    n = n / 2      # 16 → 8 → 4 → 2 → 1
```
Halving until you hit 1 takes about **log₂ n** steps → **O(log n)**. This is the
heartbeat of [binary search](#).

## Rule 4 — recursion = calls × work-per-call

Count how many times the function is invoked, and how much work each invocation
does *outside* its recursive calls.

```text
function sum(list, i):
    if i == length(list): return 0
    return list[i] + sum(list, i+1)
```
n calls, O(1) each → **O(n)** time. But also **O(n) space** — n stack frames are
alive at once (see [Recursion & the Call Stack](#)).

A recurrence like `T(n) = 2·T(n/2) + O(n)` (two half-size calls plus linear
merging) solves to **O(n log n)** — that's merge sort. The
[Recurrences & Master Theorem](#) lesson makes this systematic.

## Best / worst / average case

The same algorithm can have different costs depending on the *input*, not just
its size:

| Case | Meaning | Linear search example |
|---|---|---|
| Best | luckiest input | O(1) — target is first |
| Worst | unluckiest input | O(n) — target is last / absent |
| Average | expected over inputs | O(n) — on average n/2 checks |

By default "the complexity" means **worst case** unless stated otherwise.

## Amortized cost — cheap on average

Some single operations are occasionally expensive but rare enough to be cheap
*per operation over a long run*. Appending to a dynamic array is the classic:
usually O(1), but when it's full it doubles (an O(n) copy). Because doublings
are rare, the **amortized** cost of append is **O(1)**.

| Append # | Capacity | Cost |
|---|---|---|
| 1 | 1 → grow | O(1) |
| 2 | 2 → grow | O(1)+copy |
| 3–4 | 4 | O(1) |
| 5–8 | 8 | O(1) |

Total work for n appends is ~2n → **O(1) amortized each**.

### Common pitfalls
- A nested loop whose inner bound *shrinks* is still O(n^2), not O(n).
- `log` sneaks in whenever a quantity is repeatedly halved or doubled.
- Don't confuse *amortized* (average over a sequence, worst-case-safe) with
  *average-case* (expected over random inputs).

### Key takeaways
- Sequential adds, nested multiplies, halving gives log n.
- Recursion cost = calls × work-per-call; mind the stack space too.
- "Complexity" defaults to worst case; some cheap-looking ops are only cheap
  *amortized*.
""",
    quiz=[
        _q(
            "What is the time complexity of two nested loops that each run from 0 to n-1?",
            ["O(n)", "O(2n)", "O(n^2)", "O(log n)"],
            2,
            "Nesting multiplies: n iterations × n iterations = n^2 → O(n^2).",
        ),
        _q(
            "The inner loop runs from i+1 to n-1 (shrinking as i grows). Overall complexity?",
            ["O(n) — because the inner loop shrinks",
             "O(n^2) — the total is n(n-1)/2, still quadratic",
             "O(n log n)",
             "O(log n)"],
            1,
            "Summing the shrinking bounds gives n(n-1)/2 ≈ n²/2. Dropping the constant, that's still O(n^2) — all-pairs work.",
        ),
        _q(
            "A loop that repeatedly halves n until it reaches 1 runs in:",
            ["O(n)", "O(n/2)", "O(log n)", "O(1)"],
            2,
            "Halving 16→8→4→2→1 takes log₂ n steps, so it's O(log n).",
        ),
        _q(
            "For the recurrence T(n) = 2·T(n/2) + O(n), the total time is:",
            ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            1,
            "Two half-size subproblems plus linear work per level, over log n levels of n total work, gives O(n log n) — the merge-sort recurrence.",
        ),
        _q(
            "Appending to a dynamic array that doubles when full has which amortized cost per append?",
            ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
            2,
            "Occasional O(n) doublings are rare enough that n appends cost ~2n total, i.e. O(1) amortized each.",
        ),
        _q(
            "Unless stated otherwise, 'the time complexity' of an algorithm refers to its:",
            ["Best case", "Average case", "Worst case", "Amortized case"],
            2,
            "By convention, an unqualified complexity is the worst case — the guarantee that holds for every input of size n.",
        ),
    ],
    practice=[
        _p("contains-duplicate", "Reason about the nested-loop O(n^2) vs. the hashing O(n)."),
        _p("binary-search-first", "Prove to yourself the halving loop is O(log n)."),
        _p("array-sum", "The textbook single O(n) pass."),
    ],
)


# --- 0.4 Space complexity & tradeoffs -------------------------------------
_alg(
    "alg_space",
    "Space Complexity & Tradeoffs",
    CAT_FOUND,
    "Count the extra memory an algorithm needs — and trade memory for speed on purpose.",
    "Space complexity measures the *extra* memory an algorithm uses as a "
    "function of n, beyond the input itself. A hash set of everything seen is "
    "O(n) space; a couple of index variables are O(1) — 'in place'. Recursion "
    "quietly costs O(depth) in stack frames. The deep idea is the time–space "
    "tradeoff: you can very often buy speed with memory (a lookup table, a "
    "cache, a precomputed prefix array) or save memory at the cost of time. "
    "Knowing which way to trade is half of optimization.",
    "**Auxiliary space** = extra memory beyond the input, as a function of n.\n\n"
    "`O(1)` = in place · `O(n)` = a set/array of everything · recursion = `O(depth)`.\n\n"
    "**Time–space tradeoff:** spend memory to save time (or vice-versa).",
    """
**Space complexity** is Big-O for memory: how much *extra* storage an algorithm
needs as *n* grows. We usually mean **auxiliary space** — memory beyond the
input you were given.

## Reading space off code

| Pattern | Auxiliary space |
|---|---|
| A few scalar variables (counters, pointers) | O(1) — "in place" |
| A copy of the array, or a set/map of all elements | O(n) |
| A 2-D table of size n×n (e.g. some DP) | O(n^2) |
| Recursion n levels deep | O(n) for the call stack |

That last row surprises people: recursion isn't free. Each pending call keeps a
stack frame alive, so recursing to depth *d* costs **O(d)** memory even if each
frame is tiny. A recursive sum over n elements is O(n) *space*, while the loop
version is O(1).

## The time–space tradeoff

The central bargain of algorithms: **you can usually trade one resource for the
other.** Spend memory to go faster, or accept slower code to fit in less memory.

Classic example — *"have I seen this value before?"*

```text
# O(n^2) time, O(1) space: re-scan for each element
for each x in list:
    for each y in earlier part of list:
        if x == y: return true

# O(n) time, O(n) space: remember what you've seen
seen = empty set
for each x in list:
    if x in seen: return true
    add x to seen
```

The second version spends **O(n) memory** to cut the time from **O(n^2) to
O(n)**. That is the tradeoff, made on purpose.

Other everyday trades:
- **Prefix sums** — precompute an O(n) array so each range-sum query is O(1)
  instead of O(n).
- **Memoization / caching** — store subresults so you never recompute them
  (turns exponential recursion into polynomial).
- **Lookup tables** — precompute answers to avoid recomputing on the fly.

## When space is the constraint

Sometimes memory is the scarce resource and you trade the other way: process a
huge file in a **streaming** pass (O(1) space, maybe more time), reverse an
array **in place** instead of building a copy, or use an iterative loop to avoid
deep-recursion stack space.

### Common pitfalls
- Forgetting recursion's **O(depth)** stack cost when you claim "O(1) space".
- Counting the input itself as auxiliary space — usually we don't; we count the
  *extra* memory.
- Building a whole copy when an in-place two-pointer swap would do.

### Key takeaways
- Space complexity = extra memory vs. n; O(1) is "in place", O(n) is "remember
  everything".
- Recursion costs O(depth) in stack frames.
- Optimization is often just *choosing which way to trade time for space*.
""",
    quiz=[
        _q(
            "You store every element you've seen in a hash set while scanning an array of size n. Auxiliary space is:",
            ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
            2,
            "The set can hold up to n distinct elements, so it uses O(n) extra memory.",
        ),
        _q(
            "A recursive function that recurses to a depth of n uses how much space just for the call stack?",
            ["O(1) — recursion is free", "O(log n)", "O(n)", "O(n^2)"],
            2,
            "Each pending call keeps a stack frame alive, so depth-n recursion costs O(n) stack space even with tiny frames.",
        ),
        _q(
            "The 'seen set' trick turns an O(n^2)-time duplicate check into O(n) time. What is it spending to do that?",
            ["Nothing", "O(n) extra memory", "O(n^2) extra memory", "CPU cache only"],
            1,
            "It's a time–space tradeoff: O(n) extra memory (the set) buys the drop from O(n^2) to O(n) time.",
        ),
        _q(
            "Reversing an array 'in place' with two pointers uses how much auxiliary space?",
            ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
            0,
            "In-place means only a constant number of extra variables (the two indices and a temp) → O(1) auxiliary space.",
        ),
        _q(
            "Precomputing a prefix-sum array so each range-sum query is O(1) is an example of:",
            ["Saving memory at the cost of time",
             "Spending O(n) memory to make queries faster",
             "Reducing both time and space to zero",
             "An in-place algorithm"],
            1,
            "You build an O(n) array once so that later queries drop from O(n) to O(1) — spending memory to buy query speed.",
        ),
    ],
    practice=[
        _p("contains-duplicate", "The O(n) space / O(n) time set trick in action."),
        _p("reverse-string", "In-place two-pointer reversal — O(1) auxiliary space."),
        _p("running-sum", "Prefix sums: spend O(n) memory to answer range questions fast."),
    ],
)


# --- 0.5 Pattern recognition ----------------------------------------------
_alg(
    "alg_pattern_recognition",
    "Reading a Problem → Picking a Technique",
    CAT_FOUND,
    "The single most useful skill: map the *signals* in a problem statement to the right tool.",
    "Experienced problem-solvers don't try every technique — they read the "
    "problem and recognize signals that point to a specific tool. 'Sorted "
    "array' whispers binary search or two pointers. 'Contiguous subarray' means "
    "sliding window or prefix sums. 'All combinations / permutations' means "
    "backtracking. 'Shortest path in an unweighted graph' means BFS. This "
    "lesson is a decision cheat-sheet: learn the signal→tool mapping and most "
    "problems announce their own solution.",
    "Read the **signal words** in the statement, then reach for the matching tool:\n\n"
    "*sorted* → binary search / two pointers · *contiguous subarray* → sliding window / prefix sums · "
    "*all combinations* → backtracking · *shortest unweighted path* → BFS.",
    """
The hardest part of a problem is usually *knowing which technique applies*. Good
news: problem statements leak their intended approach through **signal words**.
Train yourself to read for them.

## The signal → technique cheat-sheet

| If the problem says… | Reach for… | Why |
|---|---|---|
| "**sorted** array" / "find a pair/target" | Binary search, or two pointers | Sortedness lets you discard half, or move from both ends |
| "**contiguous** subarray / substring" | Sliding window, or prefix sums | A window grows/shrinks over a run; prefix sums answer range totals |
| "**subarray/range sum**" queries | Prefix sums | Precompute once, answer each query in O(1) |
| "**k-th largest / smallest**", "top k" | Heap (priority queue) | A heap keeps the k best without full sorting |
| "**all** subsets / permutations / combinations" | Backtracking | You must explore the whole decision tree |
| "**shortest path**", unweighted grid/graph | BFS | BFS explores in rings of increasing distance |
| "shortest path with **weights**" | Dijkstra | Greedy expansion by smallest known distance |
| "**overlapping** subproblems", "min/max ways to…" | Dynamic programming | Reuse subresults instead of recomputing |
| "**next greater / smaller** element" | Monotonic stack | The stack keeps candidates in sorted order |
| "detect a **cycle**", "connected groups" | Union-Find, or DFS | Track connectivity / revisits |
| "does a valid **X** exist / is it feasible?" | Binary search **on the answer**, or greedy | Monotonic feasibility → binary search the threshold |

## A worked read

> "Given a **sorted** array and a target, return the **two indices** whose
> values sum to the target."

Signals: *sorted* + *find a pair summing to a target*. → **Two pointers**: start
one pointer at each end; if the sum is too big move the right pointer left, too
small move the left pointer right. O(n), no extra memory.

> "Find the length of the **longest contiguous substring** without repeating
> characters."

Signals: *longest contiguous substring* + a validity condition. → **Sliding
window**: expand the right edge, and when a repeat appears, shrink the left edge
until it's valid again. O(n).

## The general procedure

1. **Restate** the input, output, and constraints in your own words.
2. **Look at the size of n** — it caps your complexity (see [Big-O](#)). n ≤ 20
   invites exponential/backtracking; n ≤ 10^5 wants O(n log n) or better.
3. **Scan for signal words** and match them above.
4. Sketch the **brute force** first; then let the signals guide you to the
   improvement.

## When nothing matches

Fall back to fundamentals: can you **sort** to expose structure? Can a **hash
map** turn a search into O(1)? Can you **precompute** something once and reuse
it? These three — sort, hash, precompute — unlock a huge fraction of problems.

### Key takeaways
- Problems announce their technique through signal words — learn the mapping.
- The constraint on *n* narrows the complexity class before you pick a tool.
- When stuck, try to *sort*, *hash*, or *precompute*.
""",
    quiz=[
        _q(
            "A problem gives you a SORTED array and asks for a pair summing to a target. The signal points to:",
            ["Backtracking", "Two pointers (or binary search)", "BFS", "A heap"],
            1,
            "'Sorted' plus 'find a pair' is the classic two-pointers signal: move inward from both ends based on the current sum.",
        ),
        _q(
            "'Longest contiguous subarray/substring satisfying a condition' most strongly signals:",
            ["Dynamic programming", "Union-Find", "Sliding window", "Binary search"],
            2,
            "A contiguous run with a validity condition is the sliding-window fingerprint: grow the right edge, shrink the left when it becomes invalid.",
        ),
        _q(
            "You must return the k largest elements of a big stream. Best-matched tool?",
            ["Sort the whole stream every time", "A heap / priority queue of size k", "Backtracking", "Prefix sums"],
            1,
            "A size-k heap keeps the top k without fully sorting everything — the standard 'top k' technique.",
        ),
        _q(
            "The problem asks for ALL permutations of a set. This signals:",
            ["Greedy", "Backtracking", "Binary search", "Sliding window"],
            1,
            "'All arrangements/combinations/subsets' means you must explore the full decision tree — that's backtracking.",
        ),
        _q(
            "Constraints say n ≤ 20 and you must consider every subset. What complexity is acceptable here?",
            ["Only O(n) is allowed",
             "Exponential like O(2^n) is fine because n is tiny",
             "O(n log n) is required",
             "O(1) is required"],
            1,
            "Small n (≤ ~20) is a hint that an exponential/backtracking solution (2^20 ≈ 10^6) is intended and fast enough.",
        ),
        _q(
            "Shortest path in an UNWEIGHTED grid or graph is the signal for:",
            ["Dijkstra", "BFS", "DFS", "A heap"],
            1,
            "BFS explores in rings of increasing distance, so the first time it reaches a node is via a shortest (fewest-edges) path.",
        ),
    ],
    practice=[
        _p("two-sum-sorted", "Read the signals: sorted + find a pair → two pointers."),
        _p("longest-unique-substring", "Contiguous + validity condition → sliding window."),
        _p("number-of-islands", "Connected groups in a grid → BFS/DFS flood fill."),
    ],
)


# ===========================================================================
# TIER 1 — CORE TECHNIQUES
# ===========================================================================

# --- 1.1 Linear search -----------------------------------------------------
_alg(
    "alg_linear_search",
    "Linear Search & Scanning",
    CAT_SEARCH,
    "The humble one-pass scan — and why it's often exactly the right answer.",
    "Linear search walks the collection one element at a time until it finds "
    "what it wants (or runs out). It's O(n) and needs no preparation — no "
    "sorting, no extra structure. It's the baseline every other search improves "
    "on, but it's also the *correct* choice for unsorted data, single queries, "
    "and the running-aggregate pattern (max, min, sum, count) that shows up "
    "everywhere. Master the clean scan before you reach for anything fancier.",
    "Walk every element once, keep what you need.\n\n"
    "```\nfor x in list:\n    update running answer with x\n```\n\n"
    "**O(n) time, O(1) space.** No sorting or setup required.",
    """
**Linear search** (a *scan*) examines elements one by one from start to end. It's
the simplest search there is and the honest baseline for everything else.

```text
function find(list, target):
    for i in 0 .. length(list)-1:
        if list[i] == target:
            return i        # found it
    return -1               # not present
```

- **Time:** O(n) worst case (target last or absent), O(1) best case.
- **Space:** O(1).
- **Requires:** nothing — works on unsorted data with no preprocessing.

## The running-aggregate pattern

Most "scan" problems aren't literally searching for a value — they sweep once
while maintaining a *running answer*: a max, min, sum, count, or best-so-far.

```text
function maximum(list):
    best = list[0]
    for i in 1 .. length(list)-1:
        if list[i] > best:
            best = list[i]
    return best
```

Trace `maximum([3, 9, 2, 9, 5])`:

| i | list[i] | best before | best after |
|---|---|---|---|
| 1 | 9 | 3 | 9 |
| 2 | 2 | 9 | 9 |
| 3 | 9 | 9 | 9 |
| 4 | 5 | 9 | 9 |

Result: **9**. One pass, O(n), O(1). The same skeleton computes a sum (start at
0, add each), a count (start at 0, add 1 when a condition holds), or "best so
far" for many greedy problems.

## When linear search is the right tool

- The data is **unsorted** and you'll query it **once** — sorting first (O(n log
  n)) would cost more than the single O(n) scan.
- You need a **running aggregate** (max/min/sum/count).
- The collection is **small**, where clarity beats cleverness.

## When to reach past it

- **Repeated** lookups on the same data → build a **hash set/map** once (O(n)),
  then each lookup is O(1).
- The data is (or can be) **sorted** and you'll query many times → [binary
  search](#) at O(log n).

### Common pitfalls
- Initializing `best` to 0 for a max over possibly-negative numbers — start from
  the first element instead.
- Returning early on the *first* match when the problem wants the *last* or
  *all* matches.
- Off-by-one on the loop bound (`< length`, not `<= length`).

### Key takeaways
- Linear search is O(n), needs no setup, and is correct on unsorted data.
- The running-aggregate skeleton (max/min/sum/count in one pass) is everywhere.
- Reach for hashing or binary search only when you'll query repeatedly.
""",
    quiz=[
        _q(
            "What is the worst-case time complexity of linear search over n elements?",
            ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
            2,
            "In the worst case the target is last or absent, so you examine all n elements → O(n).",
        ),
        _q(
            "Linear search requires the data to be sorted first.",
            ["True", "False"],
            1,
            "False — linear search works on unsorted data with no preprocessing. That's one of its main advantages.",
        ),
        _q(
            "For finding the maximum of a list that may contain negative numbers, what should `best` start as?",
            ["0", "The first element of the list", "Negative one", "The last element only"],
            1,
            "Starting at 0 breaks on all-negative lists (it would wrongly return 0). Initialize best to the first element.",
        ),
        _q(
            "You will search the SAME unsorted array thousands of times for different targets. Better than repeated linear search:",
            ["Nothing beats linear search",
             "Build a hash set once (O(n)), then each lookup is O(1)",
             "Reverse the array first",
             "Use two pointers"],
            1,
            "Repeated membership queries are the signal to preprocess into a hash set: O(n) once, then O(1) per lookup.",
        ),
        _q(
            "The 'running aggregate' scan (max/min/sum/count in one pass) has what space complexity?",
            ["O(n)", "O(1)", "O(log n)", "O(n^2)"],
            1,
            "It keeps only a constant number of accumulator variables, so O(1) auxiliary space.",
        ),
    ],
    practice=[
        _p("array-maximum", "The running-max skeleton, exactly."),
        _p("array-minimum", "Same pattern, flipped comparison."),
        _p("count-vowels", "A running count in one scan."),
        _p("max-consecutive-ones", "Running best-so-far over a streak."),
    ],
)


# --- 1.2 Binary search -----------------------------------------------------
_alg(
    "alg_binary_search",
    "Binary Search",
    CAT_SEARCH,
    "Halve the search space every step — O(log n) — and the powerful 'binary search on the answer' trick.",
    "Binary search finds a target in a sorted array in O(log n) by repeatedly "
    "discarding half the remaining range: check the middle, then recurse into "
    "the half that must contain the target. The prerequisite is a monotonic "
    "structure — sortedness, or any property that flips from false to true once "
    "and never back. That second idea, 'binary search on the answer', is a "
    "superpower: when feasibility is monotonic in some threshold, you can binary "
    "search the threshold itself even when there's no array to search.",
    "**Needs a sorted / monotonic space.** Each step halves it → **O(log n)**.\n\n"
    "```\nlo, hi = 0, n-1\nwhile lo <= hi:\n    mid = lo + (hi-lo)/2\n    if a[mid] == t: return mid\n    if a[mid] < t: lo = mid+1\n    else: hi = mid-1\n```",
    """
**Binary search** locates a target in a **sorted** array by halving the search
range each step. Because the range shrinks geometrically, it finishes in about
log₂ n comparisons — 20 steps for a million elements.

```text
function binarySearch(a, target):
    lo = 0
    hi = length(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) / 2      # avoids overflow vs. (lo+hi)/2
        if a[mid] == target: return mid
        else if a[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
```

Trace a search for **7** in `[1, 3, 5, 7, 9, 11]` (indices 0–5):

| lo | hi | mid | a[mid] | vs 7 | action |
|---|---|---|---|---|---|
| 0 | 5 | 2 | 5 | too small | lo = 3 |
| 3 | 5 | 4 | 9 | too big | hi = 3 |
| 3 | 3 | 3 | 7 | equal | return 3 |

Three comparisons instead of four — and the gap explodes with size: at n =
1,000,000 it's ~20 steps versus a million.

## The one prerequisite: monotonicity

Binary search works whenever the space is **monotonic** — the "is my answer to
the right?" question flips from *no* to *yes* exactly once. A sorted array is the
obvious case, but so is any predicate that's false, false, …, true, true, ….

## Binary search on the answer

Here's the leap. Suppose you can't search an array, but you can *ask a
yes/no feasibility question* about a candidate answer, and that answer is
**monotonic**: if X works, everything ≥ X works too. Then binary search the
**answer** itself.

> "What's the *minimum* capacity a ship needs to move all packages within D
> days?" Feasibility ("can capacity C finish in D days?") is monotonic: bigger
> C is always at least as feasible. So binary search C between the largest single
> package and the total weight, testing feasibility at each mid.

```text
lo = lowest possible answer
hi = highest possible answer
while lo < hi:
    mid = lo + (hi - lo) / 2
    if feasible(mid): hi = mid       # mid works — try smaller
    else:             lo = mid + 1   # mid fails — need larger
return lo
```

This converts many "minimize the maximum / maximize the minimum" problems from
hard into O(n log(range)).

## Boundary variants

Real problems often want the **first** or **last** index satisfying a condition
(first occurrence, insertion point, lower/upper bound), not just *any* match.
The trick is to keep searching after a hit instead of returning: on a match,
record it and move `hi = mid - 1` (for the first occurrence) to look further
left.

### Common pitfalls
- **Forgetting the array must be sorted** — binary search on unsorted data is
  simply wrong.
- **Overflow**: use `mid = lo + (hi - lo)/2`, not `(lo + hi)/2`, in fixed-width
  integer languages.
- **Infinite loops**: make sure the range strictly shrinks every iteration
  (`lo = mid + 1` / `hi = mid - 1`, or a careful `lo < hi` form).
- Off-by-one between the `lo <= hi` and `lo < hi` templates — pick one and know
  why.

### Key takeaways
- Binary search needs a **monotonic** space and runs in **O(log n)**.
- Compute mid overflow-safely and always shrink the range.
- "Binary search on the answer" solves feasibility-threshold problems even with
  no array in sight.
""",
    quiz=[
        _q(
            "What must be true of the array for standard binary search to be correct?",
            ["It must contain no duplicates", "It must be sorted (monotonic)",
             "It must have even length", "It must contain the target"],
            1,
            "Binary search relies on order to decide which half to discard. On unsorted data it gives wrong answers.",
        ),
        _q(
            "How many comparisons does binary search need in the worst case for n = 1,000,000?",
            ["About 1,000,000", "About 1,000", "About 20", "About 6"],
            2,
            "log₂(1,000,000) ≈ 20, so ~20 halving steps — that's the whole point of O(log n).",
        ),
        _q(
            "Why compute mid = lo + (hi - lo)/2 instead of (lo + hi)/2?",
            ["It's faster", "It avoids integer overflow when lo+hi is large",
             "It searches the right half", "It's required by the sorted order"],
            1,
            "In fixed-width integer languages lo+hi can overflow; lo + (hi-lo)/2 computes the same midpoint without that risk.",
        ),
        _q(
            "'Binary search on the answer' applies when…",
            ["The array is already sorted",
             "Feasibility is monotonic in the candidate answer (if X works, so does every larger X)",
             "There are no duplicates",
             "n is small"],
            1,
            "If the yes/no feasibility of a candidate answer flips once (monotonic), you can binary search the answer value itself.",
        ),
        _q(
            "A binary search loop keeps running forever. The most likely cause is:",
            ["The array is too big",
             "The range doesn't strictly shrink each iteration (e.g. lo = mid instead of mid+1)",
             "The target is negative",
             "Using O(log n)"],
            1,
            "If lo or hi can stay put (lo = mid with lo==mid), the range never shrinks and the loop spins. Always move past mid.",
        ),
        _q(
            "To find the FIRST occurrence of a value (not just any), on a match you should:",
            ["Return immediately",
             "Record the index and keep searching the left half (hi = mid - 1)",
             "Keep searching the right half",
             "Restart from lo = 0"],
            1,
            "Don't stop at the first hit — record it and continue left to find an earlier occurrence; the last recorded index is the first occurrence.",
        ),
    ],
    practice=[
        _p("binary-search-first", "First-occurrence variant — the boundary template."),
        _p("search-insert-position", "Lower-bound / insertion-point binary search."),
        _p("two-sum-sorted", "Binary search or two pointers on a sorted array."),
        _p("is-sorted", "Check the prerequisite that makes binary search legal."),
    ],
)


# --- 1.3 Two pointers ------------------------------------------------------
_alg(
    "alg_two_pointers",
    "Two Pointers",
    CAT_SEARCH,
    "Two indices moving through the data to replace a nested loop with a single O(n) pass.",
    "The two-pointer technique keeps two indices into a sequence and moves them "
    "based on a rule, collapsing what looks like an O(n^2) all-pairs search into "
    "one O(n) pass. There are two main flavors: converging pointers from both "
    "ends (great on sorted data — pair sums, palindromes, reversing) and "
    "same-direction slow/fast pointers (deduplication, partitioning, cycle "
    "detection). The magic is that each pointer only moves forward, so the total "
    "work is linear.",
    "Two indices, each moving forward → **O(n)**, usually **O(1)** space.\n\n"
    "**Converging** (both ends, sorted): pair sums, palindrome, reverse.\n"
    "**Slow/fast** (same direction): dedupe, partition, detect a cycle.",
    """
**Two pointers** keeps two indices walking through a sequence, advancing them by
a rule until they meet or finish. It turns many O(n^2) "check all pairs" problems
into a single **O(n)** pass with **O(1)** extra space.

## Flavor 1 — converging pointers (from both ends)

Best on **sorted** data. Start `left` at the front and `right` at the back, then
move the pair inward based on what you observe.

*Pair that sums to a target in a sorted array:*

```text
left = 0
right = length(a) - 1
while left < right:
    s = a[left] + a[right]
    if s == target: return (left, right)
    if s < target:  left = left + 1     # need a bigger sum
    else:           right = right - 1   # need a smaller sum
return none
```

Trace target **10** on `[1, 3, 4, 6, 8, 9]`:

| left | right | a[left]+a[right] | vs 10 | move |
|---|---|---|---|---|
| 0 | 5 | 1+9 = 10 | equal | return (0,5) |

If instead target were **12**: `1+9=10` too small → left++, `3+9=12` → found.
Each step throws away one candidate end, so it's O(n).

The same converging idea reverses an array in place and checks a palindrome
(compare ends, walk inward).

## Flavor 2 — slow/fast pointers (same direction)

Both pointers move forward, but at different speeds or under different rules. The
**slow** pointer marks where the "good" prefix ends; the **fast** pointer scans
ahead.

*Remove duplicates from a sorted array in place:*

```text
slow = 0
for fast in 1 .. length(a)-1:
    if a[fast] != a[slow]:
        slow = slow + 1
        a[slow] = a[fast]
return slow + 1        # length of the deduped prefix
```

The slow pointer builds the answer in place while fast races ahead — O(n) time,
O(1) space. The same shape partitions an array (move all zeros to the end,
Dutch-flag partitioning) and, with a fast pointer moving twice as fast, detects a
cycle in a linked list (Floyd's algorithm).

## Why it's linear

Each pointer only ever moves **forward** (or they only move **inward**). Across
the whole run each index advances at most n times, so the total work is O(n) —
no matter that there are two of them.

### Common pitfalls
- Using converging pointers on **unsorted** data for a pair-sum — it needs sorted
  order (or switch to a hash set).
- Moving the **wrong** pointer in the converging template (grow the sum by moving
  `left` right, shrink it by moving `right` left).
- Forgetting the loop guard `left < right`, causing the pointers to cross.

### Key takeaways
- Two pointers replaces an O(n^2) pair scan with an O(n) pass, O(1) space.
- Converging (both ends) suits sorted pair/palindrome/reverse problems.
- Slow/fast (same direction) suits dedupe, partition, and cycle detection.
""",
    quiz=[
        _q(
            "The converging two-pointer technique (one at each end) assumes the array is:",
            ["Unsorted", "Sorted", "All positive", "A power of two in length"],
            1,
            "Converging pointers rely on order: a too-small sum means move left inward, too-big means move right inward. That logic needs a sorted array.",
        ),
        _q(
            "In a sorted-array pair-sum search, the current sum is LESS than the target. You should:",
            ["Move the right pointer left", "Move the left pointer right",
             "Move both inward", "Return not-found"],
            1,
            "To increase the sum, advance the left pointer to a larger value. Moving right inward would shrink the sum further.",
        ),
        _q(
            "Why is two pointers O(n) even though there are two indices?",
            ["Because n is small",
             "Because each pointer only moves forward/inward, advancing at most n times total",
             "Because it uses recursion",
             "Because the array is sorted"],
            1,
            "Neither pointer ever backtracks, so across the whole run each advances ≤ n times — linear total work.",
        ),
        _q(
            "Which problem fits the SLOW/FAST (same-direction) variant rather than converging ends?",
            ["Check if a string is a palindrome",
             "Remove duplicates from a sorted array in place",
             "Find a pair summing to a target in a sorted array",
             "Reverse an array in place"],
            1,
            "In-place dedup uses a slow pointer marking the deduped prefix and a fast pointer scanning ahead — a same-direction pattern.",
        ),
        _q(
            "Detecting a cycle in a linked list with Floyd's algorithm uses:",
            ["Two pointers at opposite ends",
             "A slow pointer and a fast pointer moving twice as fast",
             "Binary search",
             "A prefix-sum array"],
            1,
            "Floyd's tortoise-and-hare moves one pointer 1 step and the other 2 steps; if there's a cycle they eventually meet.",
        ),
    ],
    practice=[
        _p("two-sum-sorted", "Converging pointers on a sorted array."),
        _p("is-palindrome-fn", "Compare from both ends, walk inward."),
        _p("reverse-string", "In-place reversal with converging pointers."),
        _p("merge-sorted-arrays", "Two pointers advancing through two sorted inputs."),
    ],
)


# --- 1.4 Sliding window ----------------------------------------------------
_alg(
    "alg_sliding_window",
    "Sliding Window",
    CAT_SEARCH,
    "A window that grows and shrinks over a contiguous run — turning O(n·k) into O(n).",
    "The sliding-window technique maintains a contiguous window over an array or "
    "string and slides it across in one pass, adding elements on the right and "
    "removing them on the left, while keeping a running summary of what's inside. "
    "It answers questions about contiguous subarrays/substrings — longest, "
    "shortest, sum, count — in O(n) instead of recomputing each window from "
    "scratch. Windows come in two kinds: fixed size (k) and variable size "
    "(expand until valid, then contract).",
    "One contiguous window slid across the data → **O(n)**.\n\n"
    "**Fixed k:** add right, drop left, keep size k.\n"
    "**Variable:** expand right; while invalid, shrink left; track best.",
    """
A **sliding window** is a contiguous range `[left, right]` over an array or
string that moves across the data in a single pass. Instead of recomputing each
window from scratch (O(n·k)), you *update* a running summary as the window moves
— O(1) per step, **O(n)** overall.

Reach for it whenever the problem is about a **contiguous** subarray or substring:
longest, shortest, sum, average, or count satisfying a condition.

## Fixed-size window (size k)

Slide a window of constant width k: when it moves one step right, add the new
right element and remove the old left one.

*Maximum sum of any k consecutive elements:*

```text
windowSum = sum of first k elements
best = windowSum
for right in k .. n-1:
    windowSum = windowSum + a[right] - a[right - k]   # add new, drop old
    best = max(best, windowSum)
return best
```

Trace k = 3 on `[2, 1, 5, 1, 3, 2]`:

| right | added | dropped | windowSum | best |
|---|---|---|---|---|
| (init) | 2,1,5 | — | 8 | 8 |
| 3 | 1 | 2 | 7 | 8 |
| 4 | 3 | 1 | 9 | 9 |
| 5 | 2 | 5 | 6 | 9 |

Answer **9** (the window `[5,1,3]`), in one O(n) pass — no re-summing.

## Variable-size window (expand / contract)

When the window size isn't fixed, grow the right edge to include more, and
shrink the left edge whenever the window becomes **invalid**, tracking the best
valid window seen.

*Longest substring with no repeating character:*

```text
left = 0
seen = empty set
best = 0
for right in 0 .. n-1:
    while a[right] is in seen:         # window became invalid
        remove a[left] from seen
        left = left + 1
    add a[right] to seen
    best = max(best, right - left + 1)
return best
```

Both edges only ever move **right**, so even with the inner `while`, each index
enters and leaves the window at most once → **O(n)** total.

## The mental template

1. Expand `right` by one, updating the running summary.
2. While the window violates the constraint, shrink from `left`.
3. Record the answer (a length, a sum, a count) for the current valid window.

### Common pitfalls
- Recomputing the whole window each step — that's O(n·k) and defeats the purpose;
  *update incrementally*.
- Forgetting to remove the left element's contribution when it leaves the window.
- Using a window for a **non-contiguous** requirement — windows only model
  contiguous runs.

### Key takeaways
- Sliding window handles **contiguous** subarray/substring questions in O(n).
- Fixed windows add-right/drop-left; variable windows expand then contract.
- Both pointers move only forward, which is why it stays linear.
""",
    quiz=[
        _q(
            "Sliding window is the right tool when the problem concerns a … subarray or substring.",
            ["sorted", "contiguous", "reversed", "unique"],
            1,
            "Windows model contiguous runs. If the elements needn't be adjacent, a window doesn't apply.",
        ),
        _q(
            "When a fixed-size window of width k slides one step to the right, you should:",
            ["Recompute the sum of all k elements",
             "Add the new right element and subtract the element that just left",
             "Sort the window",
             "Reset the sum to zero"],
            1,
            "Incremental update is the whole point: +new right, −old left keeps each step O(1) instead of O(k).",
        ),
        _q(
            "In a variable-size window, when the window becomes INVALID you should:",
            ["Expand the right edge further",
             "Shrink from the left until it's valid again",
             "Return the current answer",
             "Start over from index 0"],
            1,
            "Contract from the left to restore validity, then continue expanding right — that's the expand/contract pattern.",
        ),
        _q(
            "Why is the variable-size window O(n) despite the inner while-loop that shrinks left?",
            ["Because n is small",
             "Because each index enters and leaves the window at most once, so total moves are ≤ 2n",
             "Because it sorts first",
             "Because the window is fixed size"],
            1,
            "left and right each advance at most n times over the whole run, so the combined work is linear even with the inner loop.",
        ),
        _q(
            "Recomputing each window from scratch instead of updating incrementally makes a size-k window cost:",
            ["O(n)", "O(n·k)", "O(log n)", "O(1)"],
            1,
            "Recomputing k elements for each of ~n positions is O(n·k) — the incremental update is what brings it down to O(n).",
        ),
    ],
    practice=[
        _p("longest-unique-substring", "The canonical variable-size window."),
        _p("max-consecutive-ones", "A window over a run of 1s."),
        _p("subarray-sum-k", "Contiguous-sum question — window / prefix-sum territory."),
        _p("sliding-window-maximum", "A window with a monotonic-deque summary."),
    ],
)


# --- 1.5 Prefix sums -------------------------------------------------------
_alg(
    "alg_prefix_sums",
    "Prefix Sums & Difference Arrays",
    CAT_SEARCH,
    "Precompute cumulative totals once so any range-sum query is O(1).",
    "A prefix-sum array stores the running total up to each index, so the sum of "
    "any range [i, j] becomes a single subtraction: prefix[j+1] − prefix[i]. You "
    "pay O(n) once to build it, then answer unlimited range-sum queries in O(1) "
    "each — a classic time–space tradeoff. The mirror-image idea, a difference "
    "array, lets you apply many range *updates* in O(1) each and reconstruct the "
    "final array once. Together they turn repeated range work from O(n) per "
    "query into O(1).",
    "Build `prefix[k] = a[0]+…+a[k-1]` once in O(n).\n\n"
    "Range sum `[i..j]` = `prefix[j+1] - prefix[i]`  → **O(1) per query**.\n\n"
    "**Difference array:** O(1) range *updates*, reconstruct once.",
    """
A **prefix-sum** (cumulative-sum) array lets you answer "what's the sum of
elements from index i to j?" in **O(1)** after an **O(n)** setup — instead of
re-adding the range (O(n)) for every query.

## Building it

Define `prefix[0] = 0` and `prefix[k] = a[0] + a[1] + … + a[k-1]`. Each entry is
the previous one plus the next element:

```text
prefix[0] = 0
for k in 1 .. n:
    prefix[k] = prefix[k-1] + a[k-1]
```

For `a = [3, 1, 4, 1, 5]`:

| k | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| prefix[k] | 0 | 3 | 4 | 8 | 9 | 14 |

## Querying a range in O(1)

The sum of `a[i..j]` (inclusive) is just a subtraction:

```text
rangeSum(i, j) = prefix[j+1] - prefix[i]
```

Sum of `a[1..3]` = `prefix[4] - prefix[1]` = `9 - 3` = **6** (that's `1+4+1`). No
loop — one subtraction, regardless of how wide the range is. The `prefix[0]=0`
sentinel is what makes the `i = 0` case work without a special branch.

## Why it's a tradeoff

You spend **O(n) memory** and one **O(n) build** so that each of possibly
millions of range queries drops from **O(n)** to **O(1)**. If you'll query the
data more than a couple of times, it pays for itself immediately.

## Prefix sums + hashing

A powerful combo: "how many subarrays sum to k?" Since `sum(i..j) =
prefix[j+1] - prefix[i]`, a range sums to k exactly when `prefix[j+1] - k`
equals some earlier prefix. Count earlier prefixes in a hash map as you go →
O(n) instead of O(n^2).

## The mirror: difference arrays (range updates)

If instead you need to *add v to every element in `[i, j]`* many times, a
**difference array** does each update in O(1): add v at index i, subtract v at
index j+1, and take a prefix sum at the end to materialize the result.

```text
diff[i]   += v
diff[j+1] -= v
# after all updates:
a = prefix sum of diff
```

Many range-add operations become O(1) each plus one O(n) final pass.

### Common pitfalls
- Off-by-one in the query: with a size-(n+1) prefix and the 0-sentinel, the
  formula is `prefix[j+1] - prefix[i]`. Write it once, trust it.
- Overflow: cumulative sums grow large — use a wide enough integer type.
- Reaching for prefix sums on a **single** query — a plain O(n) scan is simpler
  and just as fast; prefix sums win on *repeated* queries.

### Key takeaways
- O(n) build → O(1) range-sum queries via one subtraction.
- The 0-sentinel (`prefix[0]=0`) removes the i=0 edge case.
- Difference arrays are the dual: O(1) range *updates*, reconstruct once.
""",
    quiz=[
        _q(
            "With prefix[0]=0 and prefix[k]=a[0]+…+a[k-1], the sum of a[i..j] inclusive equals:",
            ["prefix[j] - prefix[i]", "prefix[j+1] - prefix[i]",
             "prefix[j] - prefix[i-1]", "prefix[i] - prefix[j+1]"],
            1,
            "With the 0-sentinel and size-(n+1) prefix, rangeSum(i,j) = prefix[j+1] - prefix[i].",
        ),
        _q(
            "After an O(n) build, each range-sum query costs:",
            ["O(n)", "O(log n)", "O(1)", "O(n^2)"],
            2,
            "A range sum is a single subtraction of two prefix entries → O(1) per query.",
        ),
        _q(
            "Prefix sums are most worth it when you…",
            ["ask for exactly one range sum",
             "ask for many range sums over the same array",
             "need to sort the array",
             "have negative numbers"],
            1,
            "The O(n) setup pays off across repeated queries. For a single query, a plain O(n) scan is simpler and equally fast.",
        ),
        _q(
            "What does the prefix[0] = 0 sentinel buy you?",
            ["Faster queries", "It removes the special case when the range starts at index 0",
             "Less memory", "Sorted order"],
            1,
            "The 0-sentinel makes prefix[j+1] - prefix[i] correct even when i = 0, avoiding a separate branch.",
        ),
        _q(
            "To apply many 'add v to every element in [i, j]' updates efficiently, use:",
            ["A prefix-sum array queried repeatedly",
             "A difference array: diff[i] += v, diff[j+1] -= v, then prefix-sum once",
             "Binary search",
             "A sliding window"],
            1,
            "A difference array records each range-add in O(1) at the two endpoints, then one prefix-sum pass reconstructs the final array.",
        ),
    ],
    practice=[
        _p("running-sum", "Build the prefix-sum array itself."),
        _p("subarray-sum-k", "Prefix sums + hashing to count subarrays summing to k."),
        _p("prefix-counts", "Cumulative counts, the same idea on frequencies."),
    ],
)


# ===========================================================================
# TIER 1 — SORTING
# ===========================================================================

# --- 1.6 Quadratic sorts ---------------------------------------------------
_alg(
    "alg_sorting_basics",
    "Quadratic Sorts (Bubble, Insertion, Selection)",
    CAT_SORT,
    "The O(n^2) sorts — slow at scale, but the clearest way to understand what sorting *is*.",
    "The three elementary sorts — bubble, selection, and insertion — all run in "
    "O(n^2) and are too slow for large inputs, but they're worth knowing cold. "
    "They teach the mechanics of ordering, they're simple and in-place, and "
    "insertion sort is genuinely the best choice for tiny or nearly-sorted "
    "arrays (real libraries switch to it for small subarrays). Understanding why "
    "they're quadratic is also the clearest possible motivation for the O(n log "
    "n) sorts that follow.",
    "All three are **O(n^2)** time, **O(1)** space, in place.\n\n"
    "**Bubble:** swap adjacent out-of-order pairs, repeat.\n"
    "**Selection:** pick the min, place it, repeat.\n"
    "**Insertion:** grow a sorted prefix, inserting each new item.",
    """
Three classic sorts run in **O(n^2)**. You won't use them on big inputs, but they
build intuition, they're all **in place** (O(1) extra space), and one of them
(insertion) is the right tool for small or nearly-sorted data.

## Selection sort — pick the smallest, repeat

Find the minimum of the unsorted part and swap it into place.

```text
for i in 0 .. n-1:
    m = index of minimum of a[i..n-1]
    swap a[i], a[m]
```

Always ~n²/2 comparisons regardless of input → **O(n^2)** best, average, and
worst. Minimal *swaps* (n of them), which occasionally matters.

## Bubble sort — swap adjacent pairs

Repeatedly pass through, swapping neighbors that are out of order; the largest
"bubbles" to the end each pass.

```text
repeat:
    swapped = false
    for i in 0 .. n-2:
        if a[i] > a[i+1]:
            swap a[i], a[i+1]
            swapped = true
    until not swapped
```

With the `swapped` flag, an already-sorted array is detected in **O(n)** (best
case); otherwise **O(n^2)**. Mostly of teaching value.

## Insertion sort — grow a sorted prefix

Keep `a[0..i-1]` sorted; take the next element and slide it left into place, like
sorting a hand of cards.

```text
for i in 1 .. n-1:
    key = a[i]
    j = i - 1
    while j >= 0 and a[j] > key:
        a[j+1] = a[j]     # shift right
        j = j - 1
    a[j+1] = key
```

Trace `[5, 2, 4, 1]`:

| after i | array |
|---|---|
| i=1 | [2, 5, 4, 1] |
| i=2 | [2, 4, 5, 1] |
| i=3 | [1, 2, 4, 5] |

**O(n^2)** worst case, but **O(n)** on already-sorted or nearly-sorted input, and
very low overhead — which is why production sorts (like Timsort) fall back to
insertion sort for small runs.

## Stability

A sort is **stable** if equal elements keep their original relative order.
Insertion and bubble are stable; selection sort is not (a swap can leap an equal
element over another). Stability matters when you sort by one key but want ties
to preserve a previous ordering.

| Sort | Best | Avg | Worst | Space | Stable? |
|---|---|---|---|---|---|
| Selection | O(n^2) | O(n^2) | O(n^2) | O(1) | no |
| Bubble | O(n) | O(n^2) | O(n^2) | O(1) | yes |
| Insertion | O(n) | O(n^2) | O(n^2) | O(1) | yes |

### Common pitfalls
- Using these on large n — 100,000 elements is ~10^10 operations, far too slow.
- Assuming selection sort is stable — it isn't.
- Forgetting bubble sort's early-exit flag, losing its one redeeming best case.

### Key takeaways
- All three are O(n^2), in place; know them for intuition, not for scale.
- Insertion sort shines on **small** or **nearly-sorted** data (O(n) best case).
- Stability (preserving ties' order) distinguishes them: insertion/bubble yes,
  selection no.
""",
    quiz=[
        _q(
            "What is the worst-case time complexity of bubble, selection, and insertion sort?",
            ["O(n log n)", "O(n)", "O(n^2)", "O(log n)"],
            2,
            "All three elementary sorts are O(n^2) in the worst case — that's why they don't scale.",
        ),
        _q(
            "Which quadratic sort is the best practical choice for a small or nearly-sorted array?",
            ["Selection sort", "Bubble sort", "Insertion sort", "None — always use merge sort"],
            2,
            "Insertion sort runs in O(n) on nearly-sorted data with tiny overhead, which is why libraries use it for small runs.",
        ),
        _q(
            "A sort is 'stable' when…",
            ["it never crashes",
             "equal elements keep their original relative order",
             "it uses O(1) space",
             "it's faster than O(n log n)"],
            1,
            "Stability means equal keys retain their prior order — important when sorting by a secondary key.",
        ),
        _q(
            "Which of these elementary sorts is NOT stable?",
            ["Insertion sort", "Bubble sort", "Selection sort", "All are stable"],
            2,
            "Selection sort's long-distance swaps can reorder equal elements, so it is not stable.",
        ),
        _q(
            "All three quadratic sorts share which space complexity?",
            ["O(n)", "O(1) — they sort in place", "O(n log n)", "O(n^2)"],
            1,
            "Bubble, selection, and insertion sort rearrange the array in place using only O(1) extra memory.",
        ),
    ],
    practice=[
        _p("is-sorted", "Verify order — the postcondition every sort must achieve."),
        _p("sort-by-frequency", "Sorting with a custom key and tie-breaking (stability matters)."),
    ],
)


# --- 1.7 Efficient sorts ---------------------------------------------------
_alg(
    "alg_efficient_sorts",
    "Efficient Sorts (Merge, Quick, Heap)",
    CAT_SORT,
    "The O(n log n) workhorses — and why comparison sorting can't beat n log n.",
    "Merge sort, quicksort, and heapsort all sort in O(n log n), the best "
    "possible for comparison-based sorting. Merge sort splits, sorts halves, and "
    "merges — a clean divide-and-conquer that's stable and guarantees O(n log n) "
    "but needs O(n) scratch space. Quicksort partitions around a pivot; it's "
    "usually fastest in practice and in place, but a bad pivot degrades it to "
    "O(n^2). Heapsort sorts in place with a guaranteed O(n log n) using a heap. "
    "Knowing their tradeoffs is standard interview fare.",
    "All three: **O(n log n)** (comparison-sort optimum).\n\n"
    "**Merge:** stable, O(n) space, guaranteed n log n.\n"
    "**Quick:** in place, fastest in practice, O(n^2) worst case.\n"
    "**Heap:** in place, guaranteed n log n, not stable.",
    """
Three sorts achieve **O(n log n)** — the provable floor for any sort that works
by comparing elements. Each makes a different tradeoff.

## Merge sort — divide, sort, merge

Split the array in half, recursively sort each half, then **merge** the two
sorted halves in linear time.

```text
function mergeSort(a):
    if length(a) <= 1: return a
    mid = length(a) / 2
    left  = mergeSort(a[0..mid-1])
    right = mergeSort(a[mid..end])
    return merge(left, right)      # two-pointer merge, O(n)
```

Its cost is the recurrence `T(n) = 2·T(n/2) + O(n)` → **O(n log n)** (log n
levels, O(n) merging per level). It's **stable** and its worst case is also
O(n log n), but merging needs **O(n)** scratch space.

## Quicksort — partition around a pivot

Choose a **pivot**, partition the array so smaller elements go left and larger go
right, then recursively sort each side.

```text
function quickSort(a, lo, hi):
    if lo >= hi: return
    p = partition(a, lo, hi)   # pivot lands in its final spot
    quickSort(a, lo, p-1)
    quickSort(a, p+1, hi)
```

- **Average:** O(n log n), and typically the **fastest in practice** (great
  cache behavior, in place, O(log n) stack).
- **Worst:** O(n^2) when pivots are consistently bad (e.g. always the smallest —
  which happens on already-sorted input with a naive first-element pivot).
- Mitigation: choose the pivot **randomly** or as the median-of-three, which
  makes the worst case astronomically unlikely.

Quicksort is generally **not stable**.

## Heapsort — sort with a heap

Build a max-heap in O(n), then repeatedly extract the maximum (O(log n) each) and
place it at the end.

```text
build a max-heap from a
for end in n-1 .. 1:
    swap a[0], a[end]        # biggest to its final slot
    sift-down a[0] within a[0..end-1]
```

**Guaranteed O(n log n)**, **in place** (O(1) extra), but **not stable** and
usually a bit slower than quicksort due to cache-unfriendly jumps.

## The n log n lower bound

Any comparison sort must distinguish all n! possible orderings using yes/no
comparisons. A binary decision tree tall enough to have n! leaves has height
≥ log₂(n!) ≈ n log n. So **no comparison sort can beat O(n log n)** — merge and
heap *reach* that floor. (To go faster you must stop comparing — see
[non-comparison sorts](#).)

## Choosing between them

| Sort | Time (avg / worst) | Space | Stable | Pick it when |
|---|---|---|---|---|
| Merge | n log n / n log n | O(n) | yes | you need stability or guaranteed n log n; linked lists |
| Quick | n log n / n^2 | O(log n) | no | general in-memory speed (most libraries' default) |
| Heap | n log n / n log n | O(1) | no | you need in-place + a hard worst-case guarantee |

### Common pitfalls
- Claiming quicksort is "always O(n log n)" — its worst case is O(n^2) without
  pivot randomization.
- Forgetting merge sort's O(n) auxiliary space.
- Assuming any of the three (except merge) is stable.

### Key takeaways
- Merge/quick/heap all hit O(n log n); comparison sorting can't do better.
- Merge = stable + guaranteed but O(n) space; quick = fastest but O(n^2) worst;
  heap = in-place + guaranteed but not stable.
- Randomize quicksort's pivot to dodge the worst case.
""",
    quiz=[
        _q(
            "What is the best worst-case time achievable by any comparison-based sort?",
            ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            1,
            "Distinguishing all n! orderings by comparisons needs ≥ log₂(n!) ≈ n log n comparisons — so O(n log n) is the floor.",
        ),
        _q(
            "Quicksort's worst-case time complexity is:",
            ["O(n log n)", "O(n)", "O(n^2)", "O(1)"],
            2,
            "With consistently bad pivots (e.g. already-sorted input, naive pivot), partitions are maximally unbalanced → O(n^2).",
        ),
        _q(
            "Which sort is stable AND guarantees O(n log n), at the cost of O(n) extra space?",
            ["Quicksort", "Heapsort", "Merge sort", "Selection sort"],
            2,
            "Merge sort is stable with a guaranteed O(n log n), but its merge step needs O(n) scratch space.",
        ),
        _q(
            "Which sort is in-place (O(1) extra) with a guaranteed O(n log n), but not stable?",
            ["Merge sort", "Heapsort", "Insertion sort", "Bubble sort"],
            1,
            "Heapsort sorts in place with a hard O(n log n) guarantee, but its heap operations reorder equal elements → not stable.",
        ),
        _q(
            "How do you make quicksort's O(n^2) worst case astronomically unlikely?",
            ["Sort the array first",
             "Choose the pivot randomly (or median-of-three)",
             "Use more memory",
             "Switch to recursion"],
            1,
            "A randomized or median-of-three pivot makes consistently bad partitions vanishingly improbable, keeping it near O(n log n).",
        ),
        _q(
            "Merge sort's cost comes from the recurrence T(n) = 2·T(n/2) + O(n). That solves to:",
            ["O(n)", "O(n^2)", "O(n log n)", "O(log n)"],
            2,
            "log n levels of recursion, each doing O(n) merging, gives O(n log n).",
        ),
    ],
    practice=[
        _p("merge-sorted-arrays", "The linear merge step at the heart of merge sort."),
        _p("merge-two-sorted-lists", "Merging on linked lists — merge sort's core move."),
        _p("merge-k-sorted", "Generalize merging with a heap — ties sorting to priority queues."),
        _p("sort-by-frequency", "Apply a full sort with a custom comparator."),
    ],
)


# --- 1.8 Non-comparison sorts ---------------------------------------------
_alg(
    "alg_non_comparison_sorts",
    "Non-Comparison Sorts (Counting, Radix, Bucket)",
    CAT_SORT,
    "Beat the n log n barrier by not comparing at all — when the keys are small integers.",
    "Comparison sorts are stuck at O(n log n), but if you stop comparing you can "
    "go faster. Counting sort tallies how many of each key value there are and "
    "rebuilds the array from the tally — O(n + k) for keys in a small range k. "
    "Radix sort applies counting sort digit by digit to sort large integers or "
    "strings in O(d·(n+k)). Bucket sort scatters uniformly-distributed values "
    "into buckets, sorts each, and concatenates. These win only under conditions "
    "(small integer keys, known range) — but when they apply they're linear.",
    "Skip comparisons → beat O(n log n) when keys are small integers.\n\n"
    "**Counting:** tally each value, rebuild → O(n + k).\n"
    "**Radix:** counting sort per digit → O(d·(n+k)).\n"
    "**Bucket:** scatter, sort buckets, concatenate.",
    """
Comparison sorts can't beat **O(n log n)** — but that bound only applies to
algorithms that *compare* elements. If your keys are small integers (or short
strings), you can sort by **counting** or **bucketing** and reach **linear** time.

## Counting sort — tally and rebuild

If every key is an integer in `[0, k)`, count how many times each value appears,
then write the values back out in order.

```text
count = array of k zeros
for x in a: count[x] += 1
out = empty
for v in 0 .. k-1:
    append v to out, count[v] times
```

Trace `a = [2, 0, 2, 1, 0]`, k = 3:

| value v | 0 | 1 | 2 |
|---|---|---|---|
| count | 2 | 1 | 2 |

Rebuild → `[0, 0, 1, 2, 2]`. Cost **O(n + k)**: linear when k is comparable to n.
Made stable by walking prefix sums of the counts — the version radix sort needs.

## Radix sort — sort digit by digit

To sort large integers (where k would be huge), sort by each **digit**, least
significant first, using a *stable* counting sort at each step. After processing
all d digits, the array is fully sorted.

```text
for each digit position from least to most significant:
    stable-counting-sort a by that digit
```

Cost **O(d·(n + b))** for d digits in base b — effectively **linear** when d is
small (fixed-width integers). Stability at each digit pass is essential, or
earlier digits' work is lost.

## Bucket sort — scatter, sort, gather

For values spread roughly **uniformly** over a range, split the range into n
buckets, drop each value into its bucket, sort each bucket (small, often
insertion sort), then concatenate.

```text
create n empty buckets spanning the value range
for x in a: put x in its bucket
sort each bucket
concatenate buckets in order
```

**O(n)** expected when the distribution is uniform (buckets stay tiny); degrades
if everything lands in one bucket.

## The catch — these aren't free lunches

They win **only under conditions**:

| Sort | Needs | Time | Space |
|---|---|---|---|
| Counting | integer keys in a small range k | O(n + k) | O(n + k) |
| Radix | fixed-width integer/string keys | O(d·(n + b)) | O(n + b) |
| Bucket | roughly uniform distribution | O(n) expected | O(n) |

If keys are huge, arbitrary, or must be compared by a custom rule, fall back to
an **O(n log n)** comparison sort. And note the extra **space** cost — none of
these is in place.

### Common pitfalls
- Using counting sort when k ≫ n (e.g. 32-bit keys) — the O(k) count array
  dominates. Use radix instead.
- Forgetting radix sort's counting passes must be **stable**, or the sort breaks.
- Assuming bucket sort stays linear on skewed (non-uniform) data — it doesn't.

### Key takeaways
- Not comparing lets you beat O(n log n) — but only for small-integer / uniform
  keys.
- Counting = tally+rebuild O(n+k); radix = stable counting per digit; bucket =
  scatter/sort/gather.
- They trade O(n)-ish extra space and only apply under their conditions.
""",
    quiz=[
        _q(
            "How can non-comparison sorts beat the O(n log n) comparison-sort lower bound?",
            ["They use faster comparisons",
             "They don't compare elements at all — they count or bucket by key value",
             "They use recursion",
             "They only work on sorted data"],
            1,
            "The n log n bound only applies to comparison-based sorting. Counting/radix/bucket sort by key value without comparing, so the bound doesn't bind them.",
        ),
        _q(
            "Counting sort's time complexity for n integers in the range [0, k) is:",
            ["O(n log n)", "O(n + k)", "O(n^2)", "O(k^2)"],
            1,
            "You do O(n) work to tally and O(k) to walk the value range → O(n + k). It's linear when k is comparable to n.",
        ),
        _q(
            "When is counting sort a BAD choice?",
            ["When keys are 0..9",
             "When the key range k is enormous compared to n (e.g. 32-bit integers)",
             "When the array is small",
             "When keys are integers"],
            1,
            "If k ≫ n, the O(k) count array dominates and wastes space/time. Radix sort handles large integer keys instead.",
        ),
        _q(
            "Radix sort requires that the per-digit counting sort be:",
            ["In place", "Stable", "Recursive", "Comparison-based"],
            1,
            "Each digit pass must preserve the order established by previous (less significant) digits — that requires a stable sort.",
        ),
        _q(
            "Bucket sort achieves expected O(n) time under what assumption about the input?",
            ["It's already sorted",
             "The values are roughly uniformly distributed across the range",
             "It contains no duplicates",
             "n is a power of two"],
            1,
            "Uniform distribution keeps each bucket tiny, so sorting all buckets is linear. Skewed data can pile into one bucket and degrade it.",
        ),
    ],
    practice=[
        _p("sort-by-frequency", "Frequency tallies — the counting-sort mindset."),
        _p("prefix-counts", "Cumulative counts, exactly the stable-counting-sort machinery."),
        _p("group-anagrams-count", "Bucketing by a canonical key."),
    ],
)


# ===========================================================================
# TIER 1 — RECURSION
# ===========================================================================

# --- 1.9 Recursion & the call stack ---------------------------------------
_alg(
    "alg_recursion",
    "Recursion & the Call Stack",
    CAT_RECUR,
    "A function that calls itself — with a base case, a smaller subproblem, and a real memory cost.",
    "Recursion solves a problem by reducing it to a smaller instance of the same "
    "problem, until it hits a base case that's trivially solvable. Every correct "
    "recursion has two parts: one or more base cases (when to stop) and a "
    "recursive case that makes progress toward them. Under the hood, each call "
    "gets a stack frame, so recursion depth d costs O(d) memory — and infinite "
    "or too-deep recursion overflows the stack. Recursion is the natural shape "
    "for trees, divide-and-conquer, and backtracking; every recursion can also "
    "be rewritten as a loop.",
    "**Base case** (stop) + **recursive case** (shrink toward it).\n\n"
    "```\nf(n):\n  if base case: return answer\n  return combine(f(smaller))\n```\n\n"
    "Depth d costs **O(d)** stack space. No base case → stack overflow.",
    """
**Recursion** is when a function solves a problem by calling itself on a
**smaller** version of the same problem, stopping at a **base case** it can
answer directly.

Every correct recursion has exactly two ingredients:

1. **Base case** — the smallest input, solved without recursing. *When to stop.*
2. **Recursive case** — reduce the problem toward the base case and combine.
   *How to make progress.*

Miss the base case (or fail to shrink toward it) and the recursion never stops —
a **stack overflow**.

```text
function factorial(n):
    if n <= 1: return 1          # base case
    return n * factorial(n - 1)  # recursive case: smaller n
```

## How the call stack works

Each call gets a **stack frame** holding its local state, pushed when the call
starts and popped when it returns. `factorial(4)` builds this tower before
anything returns:

```text
factorial(4)  -> 4 * factorial(3)
                     3 * factorial(2)
                         2 * factorial(1)
                             returns 1
                         returns 2
                     returns 6
                 returns 24
```

Four frames are alive at the deepest point. That's the key cost: **recursion of
depth d uses O(d) memory** for the stack, even when each frame is tiny. Deep
recursion (say depth 10^6) can overflow the stack where an equivalent loop would
be fine.

## Trusting the recursion ("the leap of faith")

Don't trace every level in your head. Instead: assume the recursive call
**already returns the correct answer for the smaller input**, and just write the
step that combines it. If the base case is right and each step makes correct
progress, the whole thing is correct by induction.

## Where recursion is the natural fit

- **Trees** — a tree is defined recursively (a node with subtrees), so traversals
  are naturally recursive.
- **Divide and conquer** — merge sort, quicksort, binary search all split into
  self-similar subproblems.
- **Backtracking** — explore choices, recurse, undo — the shape of permutations,
  subsets, and search.

## Recursion ↔ iteration

Any recursion can be rewritten as a loop (sometimes using an explicit stack), and
vice versa. The recursive `factorial` above is O(n) time and **O(n) space** (the
stack); the loop version is O(n) time and **O(1) space**. Choose recursion for
clarity on self-similar structure; choose iteration when depth or stack space is
a concern.

*Tail recursion* — where the recursive call is the very last action — can be
turned into a loop automatically by some languages (no growing stack), but many
mainstream languages don't guarantee this optimization.

### Common pitfalls
- **No base case**, or a recursive call that doesn't move toward it → infinite
  recursion / stack overflow.
- Forgetting recursion's **O(depth) stack cost** when analyzing space.
- Re-solving the same subproblem exponentially (naive Fibonacci) — fix with
  **memoization** (see the DP track).

### Key takeaways
- Every recursion = base case + a step that shrinks toward it.
- Each call costs a stack frame → O(depth) space; too deep overflows.
- Natural for trees, divide-and-conquer, and backtracking; convertible to loops.
""",
    quiz=[
        _q(
            "What two ingredients does every correct recursive function need?",
            ["A loop and a counter",
             "A base case and a recursive case that shrinks toward it",
             "A hash map and a set",
             "Two pointers"],
            1,
            "A base case tells it when to stop; the recursive case must make progress toward that base case, or it never terminates.",
        ),
        _q(
            "Recursion of depth d uses how much memory just for the call stack?",
            ["O(1)", "O(log d)", "O(d)", "O(d^2)"],
            2,
            "Each pending call keeps a live stack frame, so depth-d recursion costs O(d) stack space.",
        ),
        _q(
            "A recursive function with no reachable base case will most likely:",
            ["Return 0", "Overflow the stack", "Run in O(1)", "Sort the input"],
            1,
            "Without a base case (or without progressing toward it), it recurses forever, exhausting the stack — a stack overflow.",
        ),
        _q(
            "The recursive factorial uses O(n) space while the loop version uses O(1). The extra space in the recursive one is:",
            ["The output array", "The call stack of n frames", "A hash set", "The input"],
            1,
            "The recursion stacks n frames before any returns, costing O(n); the loop keeps a single accumulator, O(1).",
        ),
        _q(
            "Which problem shape is MOST naturally expressed with recursion?",
            ["Summing a flat array", "Traversing a tree", "Reading one line of input", "Swapping two variables"],
            1,
            "Trees are defined recursively (a node plus subtrees), so recursive traversal mirrors the structure directly.",
        ),
        _q(
            "The 'leap of faith' when writing recursion means:",
            ["Skip the base case",
             "Assume the recursive call already correctly solves the smaller subproblem, and just combine it",
             "Never test your code",
             "Always use a loop instead"],
            1,
            "You trust that the recursion handles the smaller input correctly and focus on the combine step — correctness then follows by induction.",
        ),
    ],
    practice=[
        _p("factorial", "The textbook base-case + recursive-case example."),
        _p("nth-fibonacci", "Naive recursion here is exponential — motivates memoization."),
        _p("sum-to-n", "Recurse: sum(n) = n + sum(n-1)."),
        _p("countdown", "Simple recursion that shrinks toward a base case."),
        _p("gcd", "Euclid's algorithm — recursion that shrinks fast."),
    ],
)


# --- 1.10 Recurrences & the Master Theorem --------------------------------
_alg(
    "alg_recurrences",
    "Recurrences & the Master Theorem",
    CAT_RECUR,
    "Turn a recursive algorithm's structure into its Big-O — mechanically.",
    "A recurrence expresses a recursive algorithm's running time in terms of "
    "itself: T(n) = a·T(n/b) + f(n) means 'a subproblems of size n/b, plus f(n) "
    "work to split and combine'. The Master Theorem reads off the answer by "
    "comparing the work of the recursive calls against f(n): whichever dominates "
    "wins, and if they balance you get an extra log factor. It instantly gives "
    "you O(n log n) for merge sort, O(n) for linear-work divide-and-conquer, and "
    "O(log n) for binary search — without unrolling anything by hand.",
    "`T(n) = a·T(n/b) + f(n)`  → compare `n^(log_b a)` against `f(n)`:\n\n"
    "leaves win → `O(n^{log_b a})` · balanced → `O(f(n)·log n)` · root wins → `O(f(n))`.\n\n"
    "Merge sort `2T(n/2)+O(n)` → **O(n log n)**.",
    """
A **recurrence** describes a recursive algorithm's cost in terms of smaller
inputs. Most divide-and-conquer algorithms fit the shape:

```text
T(n) = a · T(n / b) + f(n)
```

- **a** — how many recursive subproblems you make,
- **n / b** — the size of each subproblem,
- **f(n)** — the work to divide and combine *outside* the recursive calls.

## The intuition: a tree of work

Picture the recursion as a tree. Each level splits the work; the question is
whether most of the total work happens near the **root** (the top combine step),
is spread **evenly** across levels, or piles up in the **leaves** (the many tiny
base cases). The Master Theorem just formalizes which of the three it is.

The deciding quantity is **n^(log_b a)** — the number of leaves — compared
against **f(n)**, the per-level combine work.

## The Master Theorem (three cases)

Let `c = log_b a`. Compare `f(n)` with `n^c`:

| Case | Condition | Result | Who dominates |
|---|---|---|---|
| 1 | f(n) grows slower than n^c | T(n) = O(n^c) | the leaves |
| 2 | f(n) ≈ n^c | T(n) = O(n^c · log n) | balanced (log factor) |
| 3 | f(n) grows faster than n^c | T(n) = O(f(n)) | the root work |

## Worked examples

**Merge sort:** `T(n) = 2·T(n/2) + O(n)`. Here a=2, b=2, so c = log₂2 = 1, and
n^c = n. f(n) = n ≈ n^c → **Case 2** → **O(n log n)**. ✓

**Binary search:** `T(n) = 1·T(n/2) + O(1)`. a=1, b=2, c = log₂1 = 0, n^c = 1.
f(n) = 1 ≈ n^0 → **Case 2** → **O(1 · log n) = O(log n)**. ✓

**Linear-work split (e.g. some tree algorithms):** `T(n) = 2·T(n/2) + O(1)`.
c = 1, n^c = n, f(n) = 1 grows slower → **Case 1** → **O(n)**.

**Heavy combine:** `T(n) = 2·T(n/2) + O(n^2)`. c = 1, f(n) = n² grows faster →
**Case 3** → **O(n^2)**.

## When the Master Theorem doesn't apply

It needs the clean `a·T(n/b) + f(n)` form with equal-sized subproblems. It does
**not** directly cover:
- **Unequal splits** like `T(n) = T(n/3) + T(2n/3) + O(n)` (quicksort-style) —
  use a recursion tree or substitution.
- **Subtract-and-conquer** like `T(n) = T(n-1) + O(1)` (linear recursion) — that
  one just unrolls to **O(n)** directly.
- f(n) that sits *between* cases (a log-factor gap) — needs the extended theorem.

## The by-hand fallback: unrolling

When in doubt, expand a few levels and spot the pattern. `T(n) = T(n-1) + O(1)`
unrolls to `O(1) + O(1) + … (n times) = O(n)`. `T(n) = 2·T(n-1) + O(1)` doubles
each level → `O(2^n)` (the naive-Fibonacci / all-subsets blowup).

### Common pitfalls
- Plugging a **subtract**-form recurrence (`T(n-1)`) into the Master Theorem,
  which is for **divide** forms (`T(n/b)`).
- Miscomputing `log_b a` (for merge sort it's log₂2 = 1, not 2).
- Forgetting that Case 2 is the one that *adds the log factor*.

### Key takeaways
- Model divide-and-conquer as `T(n) = a·T(n/b) + f(n)`.
- Compare f(n) to n^(log_b a): leaves win, balanced adds a log, or the root wins.
- Merge sort → O(n log n), binary search → O(log n), linear recursion → O(n).
""",
    quiz=[
        _q(
            "In the recurrence T(n) = a·T(n/b) + f(n), what does f(n) represent?",
            ["The number of subproblems",
             "The work to divide and combine outside the recursive calls",
             "The base case value",
             "The recursion depth"],
            1,
            "f(n) is the non-recursive work per call — splitting the input and combining subresults. a and n/b describe the recursive calls.",
        ),
        _q(
            "Merge sort is T(n) = 2·T(n/2) + O(n). By the Master Theorem this is:",
            ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            1,
            "log₂2 = 1 so n^c = n, and f(n) = n matches it → Case 2 → O(n log n).",
        ),
        _q(
            "Binary search is T(n) = T(n/2) + O(1). This solves to:",
            ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            1,
            "a=1, b=2 gives n^0 = 1, and f(n)=O(1) matches → Case 2 → O(1·log n) = O(log n).",
        ),
        _q(
            "The Master Theorem in the a·T(n/b)+f(n) form does NOT directly apply to which recurrence?",
            ["T(n) = 2T(n/2) + O(n)",
             "T(n) = T(n-1) + O(1)",
             "T(n) = 4T(n/2) + O(n)",
             "T(n) = T(n/2) + O(1)"],
            1,
            "T(n-1) is a subtract-and-conquer form, not a divide form (n/b). The Master Theorem is for divide recurrences; this one just unrolls to O(n).",
        ),
        _q(
            "T(n) = 2·T(n-1) + O(1) unrolls to which complexity?",
            ["O(n)", "O(n log n)", "O(2^n)", "O(n^2)"],
            2,
            "Doubling the number of calls at each of n levels gives 2^n total — the classic exponential blowup of naive branching recursion.",
        ),
        _q(
            "In the Master Theorem, which case ADDS a logarithmic factor to the result?",
            ["Case 1 (leaves dominate)",
             "Case 2 (f(n) balances n^{log_b a})",
             "Case 3 (root work dominates)",
             "None of them"],
            1,
            "Case 2 is the balanced case where per-level work is equal across log n levels, contributing the extra log factor (e.g. n log n).",
        ),
    ],
    practice=[
        _p("nth-fibonacci", "Naive recursion T(n)=T(n-1)+T(n-2) → exponential; see the blowup."),
        _p("binary-search-first", "T(n)=T(n/2)+O(1) → O(log n) in practice."),
        _p("merge-sorted-arrays", "The O(n) combine step of the merge-sort recurrence."),
        _p("climbing-stairs", "A recurrence you can either explode or memoize."),
    ],
)
