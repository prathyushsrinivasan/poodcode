# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 23 — sliding window & prefix sums.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THE MONTH'S IDIOM, WHICH TS_ROADMAP NOW REQUIRES OF THIS WEEK SPECIFICALLY:
# "a sliding window that does not show the count it saved over the nested loop has
# not made its argument." So lesson 1 ships BOTH versions of the same problem and
# prints both operation counts — 11 against 15 on a seven-element array, and the
# gap widens with the window size. Five more exercises and the capstone count too.
# Nothing measures elapsed time (week 17's rule).
#
# ---------------------------------------------------------------------------
# WHAT THIS WEEK LEANS ON, AND WHERE IT CAME FROM
#
#   week 19's Map          every window that tracks "what is inside it" is a Map
#                          of counts, and `(m.get(k) ?? 0) + 1` is the idiom
#   week 19's Map again    prefix-sum-plus-Map is lesson 5, and it is the single
#                          highest-yield trick in the whole month
#   week 21's counting      the rolling-versus-recompute contrast IS week 21's
#                          doubling test, applied to one problem
#   week 22's two pointers  a variable-size window is two pointers moving the same
#                          direction, with a condition deciding when the left one
#                          moves — stated explicitly in lesson 2, because a learner
#                          who has just done week 22 should recognise the shape
#                          rather than meet it again as something new
#
# ---------------------------------------------------------------------------
# THE ONE BOUNDARY DETAIL, and it is the source of every prefix-sum bug:
#
#   THE PREFIX ARRAY IS ONE LONGER THAN THE INPUT, and starts with 0.
#
#       xs      =    [1, 2, 3, 4, 5]
#       prefix  = [0, 1, 3, 6, 10, 15]
#       rangeSum(lo, hi) = prefix[hi + 1] - prefix[lo]
#
# The leading 0 is the sentinel that removes the `lo === 0` special case, and
# `hi + 1` is what makes the range inclusive. Drop the sentinel and you need a
# conditional; use `prefix[hi]` instead of `prefix[hi + 1]` and you silently get the
# sum of `[lo, hi - 1]`, which is the shipped `fix` (verified: it answers 9 where
# the answer is 12).
# ---------------------------------------------------------------------------

_PREFIX = (
    'function prefixOf(xs: readonly number[]): readonly number[] {\n'
    '  const prefix: number[] = [0];\n'
    '  for (const x of xs) {\n'
    '    prefix.push((prefix[prefix.length - 1] ?? 0) + x);\n  }\n'
    '  return prefix;\n}\n'
)

# --- Week 23 --------------------------------------------------------------
_WEEKS.append(_week(
    23, 6, _M6,
    "Sliding Window & Prefix Sums",
    "Two ways to stop recomputing: carry the answer as the window moves, or precompute every prefix once and answer any range by subtraction.",
    """
Both techniques this week exist for the same reason: **the obvious solution
recomputes what it already knew.**

## The sliding window

"The largest sum of any three consecutive amounts." The obvious version adds up
every window from scratch. But consecutive windows overlap almost entirely:

```
[1, 4, 2] 10  2  3  1     sum = 7
 1 [4, 2, 10] 2  3  1     sum = 16   ← 7 - 1 + 10. Two operations, not three.
```

**Add what entered, subtract what left.** O(n) instead of O(n·k), and lesson 1
prints both counts so the claim is evidenced.

## Prefix sums

"The total between day 3 and day 7", asked a thousand times. Precompute the running
total once:

```
xs     =    [1, 2, 3,  4,  5]
prefix = [0, 1, 3, 6, 10, 15]
```

and then **any** range is one subtraction:

```ts
rangeSum(lo, hi) = prefix[hi + 1] - prefix[lo]
```

O(n) once, then **O(1) per query, for ever**. That trade — pay once, answer
cheaply — is one of the most reliable moves in programming.

## And the two combined

Prefix sums plus week 19's `Map` answers "how many subarrays sum to exactly k?" in
one pass. It is the highest-yield single trick in this month, and lesson 5 is it.

## What you already know

A variable-size window is **two pointers moving the same direction** (week 22),
with a condition deciding when the left one catches up. Every window that tracks
what is inside it is a **Map of counts** (week 19). You are assembling parts, not
learning new ones.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Say what both techniques avoid recomputing",
        "Slide a fixed-size window by adding one element and subtracting another",
        "Show the operation count a rolling window saves over recomputing",
        "Grow and shrink a variable-size window, and state its invariant",
        "Say why a variable window is O(n) despite a loop inside a loop",
        "Track a window's contents with a Map of counts",
        "Answer 'exactly k' by subtracting two 'at most k' answers",
        "Build a prefix-sum array with its sentinel, and say what the sentinel removes",
        "Answer an inclusive range query with one subtraction",
        "Count subarrays summing to a target with prefix sums and a Map",
        "Apply many range updates in O(1) each with a difference array",
        "Choose between a window, a prefix sum and a difference array",
    ],
    why="These two patterns cover an enormous share of array problems, and both are recognisable from the shape of the question: 'consecutive' or 'contiguous' means a window; 'range' or 'between i and j, repeatedly' means a prefix sum. Recognising which you are looking at is most of the work, and the implementations are short once you have.",
    est_minutes=480,
    glossary=[
        _gloss("sliding window", "A contiguous range that moves through the array, carrying its own answer."),
        _gloss("fixed window", "Constant size k. One element enters and one leaves per step."),
        _gloss("variable window", "The size changes: grow at the right, shrink from the left while a condition is violated."),
        _gloss("rolling update", "sum = sum + entering - leaving. The whole idea of a window."),
        _gloss("window invariant", "What is true of the window at the end of every step. What makes the answer correct."),
        _gloss("shrink loop", "The inner `while` that restores the invariant. Amortised O(1) per step."),
        _gloss("prefix sum", "prefix[i] is the total of the first i elements. One longer than the input."),
        _gloss("sentinel 0", "prefix[0] = 0, which removes the `lo === 0` special case."),
        _gloss("range query", "prefix[hi + 1] - prefix[lo] — inclusive, O(1)."),
        _gloss("precompute", "Pay O(n) once so every later query is cheap. The trade this week is built on."),
        _gloss("running sum", "The prefix total as you walk, without storing the array."),
        _gloss("complement", "running - target — the earlier prefix that would make this subarray sum to target."),
        _gloss("difference array", "Store the CHANGES; one pass turns them back into values."),
        _gloss("range update", "Add to a whole range in O(1): +amount at lo, -amount just past hi."),
        _gloss("at most k", "A window constrained by a count. Subtract two of them to get 'exactly k'."),
        _gloss("contiguous", "The word in the problem statement that means 'window'."),
    ],
    cheatsheet="""
```ts
// ---- fixed window: add what enters, subtract what leaves ---------------
let sum = 0;
for (let i = 0; i < k; i = i + 1) { sum = sum + (xs[i] ?? 0); }   // the first one
let best = sum;
for (let i = k; i < xs.length; i = i + 1) {
  sum = sum + (xs[i] ?? 0) - (xs[i - k] ?? 0);      // TWO operations per step
  best = Math.max(best, sum);
}
// O(n) rather than O(n·k). The saving grows with k.

// ---- variable window: grow right, shrink left while invalid -----------
let start = 0;
let sum = 0;
let best = 0;
for (let end = 0; end < xs.length; end = end + 1) {
  sum = sum + (xs[end] ?? 0);                       // grow
  while (sum > budget && start <= end) {
    sum = sum - (xs[start] ?? 0);                   // shrink
    start = start + 1;
  }
  best = Math.max(best, end - start + 1);           // the window is valid HERE
}
// still O(n): `start` only ever moves forward, so the inner loop runs n times TOTAL

// ---- a window that tracks its contents (week 19) ---------------------
counts.set(v, (counts.get(v) ?? 0) + 1);            // entering
const left = (counts.get(out) ?? 0) - 1;            // leaving
if (left === 0) { counts.delete(out); } else { counts.set(out, left); }
counts.size;                                         // distinct values in the window

// exactly k distinct  =  atMost(k) - atMost(k - 1)

// ---- prefix sums: ONE LONGER than the input, starting at 0 -----------
const prefix: number[] = [0];
for (const x of xs) { prefix.push((prefix[prefix.length - 1] ?? 0) + x); }
// xs     =    [1, 2, 3,  4,  5]
// prefix = [0, 1, 3, 6, 10, 15]
const inclusive = (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);   // O(1), any range

// ---- prefix + Map: count subarrays summing to target ----------------
const seen = new Map<number, number>();
seen.set(0, 1);                                      // the empty prefix. REQUIRED.
let running = 0;
let count = 0;
for (const x of xs) {
  running = running + x;
  count = count + (seen.get(running - target) ?? 0);          // the complement
  seen.set(running, (seen.get(running) ?? 0) + 1);
}

// ---- difference array: many range updates, O(1) each ---------------
const diff: number[] = new Array(n + 1).fill(0);
diff[lo] = (diff[lo] ?? 0) + amount;
diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;         // n + 1 long, so this is safe
let running = 0;
for (let i = 0; i < n; i = i + 1) {                  // one pass to materialise
  running = running + (diff[i] ?? 0);
  out.push(running);
}

// ---- which one ---------------------------------------------------------
// "contiguous" / "consecutive" / "longest … such that"   -> window
// "sum between i and j", asked repeatedly                 -> prefix sums
// "count subarrays with …"                                -> prefix + Map
// many range UPDATES, read once at the end                -> difference array
```
""",
    self_check=[
        "Can you say what both techniques stop you recomputing?",
        "Can you slide a fixed window with two operations per step?",
        "Can you say how many operations the rolling version saves, and why it grows with k?",
        "Can you state a variable window's invariant?",
        "Can you say why the shrink loop does not make it O(n²)?",
        "Can you track the distinct values in a window?",
        "Can you get 'exactly k' from two 'at most k' answers?",
        "Can you build a prefix array and say why it is one longer than the input?",
        "Can you say what the leading 0 removes the need for?",
        "Can you write the inclusive range query from memory?",
        "Can you say why the subarray-count Map must start with `{0: 1}`?",
        "Can you apply a range update in O(1) and say where the -amount goes?",
        "Can you pick the right technique from the wording of a question?",
    ],
    review=[
        _q("A sliding window avoids…",
           ["sorting", "recomputing the overlap between consecutive windows", "allocation",
            "recursion"], 1,
           "Add what entered, subtract what left."),
        _q("Sliding a fixed window costs, per step…",
           ["k operations", "two operations", "one", "log k"], 1,
           "Which is why it is O(n) rather than O(n·k)."),
        _q("A variable window shrinks…",
           ["always", "while the invariant is violated", "never", "once per step"], 1,
           "Grow at the right, shrink from the left."),
        _q("The shrink loop keeps the whole thing O(n) because…",
           ["it is short", "`start` only moves forward, so it runs n times in total",
            "of the Map", "it is amortised over k"], 1,
           "Total work, not per-iteration work."),
        _q("The distinct values in a window are tracked with…",
           ["an array", "a Map of counts, deleting a key when it reaches 0", "a Set alone",
            "a sort"], 1,
           "The count is what tells you when to delete."),
        _q("\"Exactly k distinct\" equals…",
           ["atMost(k)", "atMost(k) - atMost(k-1)", "atMost(k) + atMost(k-1)", "k"], 1,
           "A genuinely useful trick."),
        _q("A prefix array for n elements has…",
           ["n entries", "n + 1 entries", "n - 1", "2n"], 1,
           "The leading 0 is one of them."),
        _q("The leading 0 exists to…",
           ["mark the start", "remove the `lo === 0` special case", "make it sorted",
            "save memory"], 1,
           "A sentinel, exactly like week 20's."),
        _q("The inclusive range sum is…",
           ["prefix[hi] - prefix[lo]", "prefix[hi + 1] - prefix[lo]", "prefix[hi] - prefix[lo - 1]",
            "prefix[hi + 1] - prefix[lo + 1]"], 1,
           "`hi + 1` is what makes it inclusive."),
        _q("`prefix[hi] - prefix[lo]` gives…",
           ["the right answer", "the sum of [lo, hi - 1] — silently one short", "an error",
            "zero"], 1,
           "The commonest prefix-sum bug."),
        _q("In the subarray-count Map, `seen.set(0, 1)` before the loop accounts for…",
           ["nothing", "the empty prefix — subarrays that start at index 0", "the first element",
            "the target"], 1,
           "Leave it out and you miss every subarray starting at the beginning."),
        _q("A difference array stores…",
           ["the values", "the CHANGES, turned back into values by one pass", "the prefix sums",
            "the ranges"], 1,
           "Which makes a range update O(1)."),
        _q("A range update writes…",
           ["+amount at every index", "+amount at lo and -amount just past hi", "+amount at lo only",
            "-amount at hi"], 1,
           "Two writes, whatever the range's length."),
        _q("\"Count the subarrays with sum k\" points at…",
           ["a window", "prefix sums plus a Map", "a sort", "a difference array"], 1,
           "A window does not work when values can be negative."),
    ],
    milestone="Interview rep #23 — the ledger analytics report. One pass builds a prefix-sum table; from it the report answers a range total in O(1), the best k-day window, the longest run that stays inside a budget, and the number of stretches that total exactly a target — each with the operations it cost, so every claim about cost is evidenced on the page.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w23-fixed", "The fixed window",
            "Add what entered, subtract what left.",
            """
"The largest total of any `k` consecutive amounts."

The obvious version recomputes each window:

```ts
for (let i = 0; i + k <= xs.length; i = i + 1) {
  let sum = 0;
  for (let j = i; j < i + k; j = j + 1) { sum = sum + (xs[j] ?? 0); }   // k adds
  best = Math.max(best, sum);
}
```

**O(n·k)** — and every window after the first shares `k - 1` elements with the one
before it, so almost all of that work is a repeat.

## The window

```ts
let sum = 0;
for (let i = 0; i < k; i = i + 1) { sum = sum + (xs[i] ?? 0); }    // the first window
let best = sum;
for (let i = k; i < xs.length; i = i + 1) {
  sum = sum + (xs[i] ?? 0) - (xs[i - k] ?? 0);      // enters, leaves
  best = Math.max(best, sum);
}
```

**O(n)**, two operations per step regardless of `k`.

## The counts, since this is month 6

On `[1, 4, 2, 10, 2, 3, 1]` with k = 3:

```
recompute:  ops=15
rolling:    ops=11
```

Both find 16. The saving looks small because `k` is small — and that is the point
worth seeing: the recompute cost is `(n - k + 1) × k` and the rolling cost is
`k + 2(n - k)`, so at k = 3 it is 15 against 11, and at k = 100 with n = 1,000 it is
**90,100 against 1,900**. The window's cost barely moves when `k` grows; the
recompute's is proportional to it.

## The two indices

`i` is the element **entering**; `i - k` is the element **leaving**. Getting that
pair wrong by one is the whole difficulty of a fixed window, and the check is
arithmetic: when `i === k`, the window should cover `1 … k`, so the departing
element is index `0` — which is `i - k`. ✓

## Not just a sum

Anything you can add and subtract slides: a total, a count of matching elements, a
running product (with care over zeroes). Anything you *cannot* undo does not — a
maximum is the classic example. Removing the largest element from a window does not
tell you the new largest, which is why "maximum in every window" needs week 18's
**monotonic deque** rather than a rolling value.

> ⚠️ **Common mistakes:** `i - k + 1` for the departing index; forgetting to seed
> the first window before the loop; and trying to slide a maximum.
""",
            warmup=[
                _q("Sliding a fixed window costs, per step…",
                   ["k operations", "two", "one", "k + 1"], 1,
                   "One entering, one leaving."),
                _q("Recomputing every window is…",
                   ["O(n)", "O(n·k)", "O(n log n)", "O(k)"], 1,
                   "Almost all of it a repeat."),
                _q("When `i === k`, the element leaving the window is at…",
                   ["i - k + 1", "i - k", "i - 1", "0 always"], 1,
                   "Which happens to be 0 on that first step."),
                _q("A maximum cannot be slid because…",
                   ["it is slow", "removing the largest does not tell you the new largest",
                    "of types", "it can"], 1,
                   "That is what a monotonic deque is for."),
            ],
            exercises=[
                _ex("tscourse-w23-fx-1", "Seed the first window",
                    "Total the first k elements before the sliding starts.",
                    _NUMS +
                    'const k = 3;\n'
                    'let sum = 0;\n'
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0);\n}\n'
                    'console.log(sum);\n',
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0);\n}',
                    [("1 4 2 10", "7"), ("5 5 5 5", "15")],
                    hints=["The first window is indices 0 up to k - 1.",
                           "Write the loop that adds those k elements."],
                    difficulty="Easy"),
                _ex("tscourse-w23-fx-2", "Slide it",
                    "Add the entering element and subtract the departing one.",
                    _NUMS +
                    'const k = 3;\n'
                    'let sum = 0;\n'
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0);\n}\n'
                    'let best = sum;\n'
                    'for (let i = k; i < nums.length; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0) - (nums[i - k] ?? 0);\n'
                    '  best = Math.max(best, sum);\n}\n'
                    'console.log(best);\n',
                    '  sum = sum + (nums[i] ?? 0) - (nums[i - k] ?? 0);',
                    [("1 4 2 10 2 3 1", "16"), ("1 1 1", "3")],
                    hints=["`i` is entering; `i - k` is leaving.",
                           "Write sum = sum + (nums[i] ?? 0) - (nums[i - k] ?? 0);"],
                    difficulty="Medium"),
                _ex("tscourse-w23-fx-3", "Count both versions",
                    "Report the operations the rolling window performs, against what recomputing would.",
                    'const xs = [1, 4, 2, 10, 2, 3, 1];\n'
                    'const k = 3;\n'
                    'let rolling = 0;\n'
                    'let sum = 0;\n'
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  sum = sum + (xs[i] ?? 0);\n'
                    '  rolling = rolling + 1;\n}\n'
                    'let best = sum;\n'
                    'for (let i = k; i < xs.length; i = i + 1) {\n'
                    '  sum = sum + (xs[i] ?? 0) - (xs[i - k] ?? 0);\n'
                    '  rolling = rolling + 2;\n'
                    '  best = Math.max(best, sum);\n}\n'
                    'const recompute = (xs.length - k + 1) * k;\n'
                    'console.log(`best=${best} rolling=${rolling} recompute=${recompute}`);\n',
                    'const recompute = (xs.length - k + 1) * k;',
                    [("", "best=16 rolling=11 recompute=15")],
                    hints=["The number of windows, times the size of each.",
                           "Write const recompute = (xs.length - k + 1) * k;"],
                    difficulty="Medium"),
                _ex("tscourse-w23-fx-4", "The saving at scale",
                    "Report both costs for n = 1000 and k = 100, where the gap is the real story.",
                    'const n = 1000;\n'
                    'const k = 100;\n'
                    'const recompute = (n - k + 1) * k;\n'
                    'const rolling = k + 2 * (n - k);\n'
                    'console.log(`recompute=${recompute} rolling=${rolling}`);\n',
                    'const rolling = k + 2 * (n - k);',
                    [("", "recompute=90100 rolling=1900")],
                    hints=["Seeding costs k; every step after that costs two.",
                           "Write const rolling = k + 2 * (n - k);"],
                    difficulty="Easy"),
                _ex("tscourse-w23-fx-5", "The window average",
                    "Report the best average rather than the best total, to two decimals.",
                    _NUMS +
                    'const k = 2;\n'
                    'let sum = 0;\n'
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0);\n}\n'
                    'let best = sum;\n'
                    'for (let i = k; i < nums.length; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0) - (nums[i - k] ?? 0);\n'
                    '  best = Math.max(best, sum);\n}\n'
                    'console.log((best / k).toFixed(2));\n',
                    'console.log((best / k).toFixed(2));',
                    [("1 4 2 10", "6.00"), ("3 3", "3.00")],
                    hints=["The best total divided by the window size.",
                           "Write console.log((best / k).toFixed(2));"],
                    difficulty="Easy"),
                _ex("tscourse-w23-fx-6", "Count what matches, in a window",
                    "Slide a count rather than a sum: how many elements in the window exceed 2.",
                    _NUMS +
                    'const k = 3;\n'
                    'function big(v: number): number {\n'
                    '  return v > 2 ? 1 : 0;\n}\n'
                    'let inWindow = 0;\n'
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  inWindow = inWindow + big(nums[i] ?? 0);\n}\n'
                    'let best = inWindow;\n'
                    'for (let i = k; i < nums.length; i = i + 1) {\n'
                    '  inWindow = inWindow + big(nums[i] ?? 0) - big(nums[i - k] ?? 0);\n'
                    '  best = Math.max(best, inWindow);\n}\n'
                    'console.log(best);\n',
                    '  inWindow = inWindow + big(nums[i] ?? 0) - big(nums[i - k] ?? 0);',
                    [("1 4 5 1 1 9", "2"), ("1 1 1", "0")],
                    hints=["A count slides exactly like a sum, using 0 or 1 per element.",
                           "Write inWindow = inWindow + big(nums[i] ?? 0) - big(nums[i - k] ?? 0);"],
                    difficulty="Medium"),
                _fix("tscourse-w23-fx-fix1", "Fix the departing index",
                     "This reports 18 where the answer is 16: the departing element is taken as `i - k + 1`, which is one *inside* the window, so the element that actually left is never subtracted and one that is still there is removed twice over.",
                     _NUMS +
                     'const k = 3;\n'
                     'let sum = 0;\n'
                     'for (let i = 0; i < k; i = i + 1) {\n'
                     '  sum = sum + (nums[i] ?? 0);\n}\n'
                     'let best = sum;\n'
                     'for (let i = k; i < nums.length; i = i + 1) {\n'
                     '  sum = sum + (nums[i] ?? 0) - (nums[i - k + 1] ?? 0);\n'
                     '  best = Math.max(best, sum);\n}\n'
                     'console.log(best);\n',
                     _NUMS +
                     'const k = 3;\n'
                     'let sum = 0;\n'
                     'for (let i = 0; i < k; i = i + 1) {\n'
                     '  sum = sum + (nums[i] ?? 0);\n}\n'
                     'let best = sum;\n'
                     'for (let i = k; i < nums.length; i = i + 1) {\n'
                     '  sum = sum + (nums[i] ?? 0) - (nums[i - k] ?? 0);\n'
                     '  best = Math.max(best, sum);\n}\n'
                     'console.log(best);\n',
                     [("1 4 2 10 2 3 1", "16"), ("1 1 1 1", "3")],
                     hints=["At the first sliding step `i === k`, so the element leaving is index 0.",
                            "`i - k + 1` is 1 at that point — an element still inside the window.",
                            "Write nums[i - k]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The rolling cost is `k + 2(n - k)`, which as k grows…",
                   ["grows with k", "barely changes", "doubles", "is O(n·k)"], 1,
                   "Where the recompute cost is proportional to k."),
                _q("Sliding a running product needs care because…",
                   ["it is slow", "a zero cannot be divided back out", "of types", "it cannot slide"], 1,
                   "Undoing is what makes a value slidable."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w23-variable", "The variable window",
            "Grow at the right, shrink from the left while the invariant is broken.",
            """
When the window's size is not given — "the **longest** run whose total stays within
budget" — the shape changes:

```ts
let start = 0;
let sum = 0;
let best = 0;
for (let end = 0; end < xs.length; end = end + 1) {
  sum = sum + (xs[end] ?? 0);                      // 1. grow
  while (sum > budget && start <= end) {
    sum = sum - (xs[start] ?? 0);                  // 2. shrink until valid
    start = start + 1;
  }
  best = Math.max(best, end - start + 1);          // 3. the window is valid HERE
}
```

Three steps, in that order, every iteration. Write them in that order and the thing
works; reorder them and it does not.

## The invariant

> At the point where `best` is updated, the window `[start, end]` satisfies the
> condition.

That is what makes the answer correct, and stating it is how you decide where the
`best` update goes: **after** the shrink loop, never inside it.

## Why it is still O(n)

There is a `while` inside a `for`, which looks quadratic and is not. Count the total
work instead (week 21's habit): `end` advances n times, and `start` **only ever
moves forward** — so across the entire run the inner loop can execute at most n
times *in total*, not n times per iteration. Two pointers, n steps, **O(n)**.

This is exactly week 22's same-direction two pointers, with a condition rather than
a fixed rule deciding when the left one moves. If it feels familiar, it should.

## This one is two pointers you have already met

| | week 22 | week 23 |
|---|---|---|
| left moves when | the element is kept | the invariant is broken |
| the answer is | a compacted array | the best window seen |

## `start <= end` in the shrink condition

It guards the case where a **single element on its own** already breaks the
condition — an amount larger than the whole budget. Without it, `start` runs past
`end` and the width goes negative. With it, the window legitimately becomes empty
and `best` is not updated. Verified: `longestUnder([10, 1], 5)` is 1, not 0 and not
2, because the `1` alone fits.

## When a window does not work

The technique needs the condition to be **monotonic in the window**: growing the
window can only ever make it more broken. That holds for a sum of **non-negative**
numbers and fails the moment a negative value appears — adding an element can then
*reduce* the sum, so a window that was too big might become valid again, and
shrinking from the left was the wrong move.

That is precisely why lesson 5's subarray counting uses prefix sums and a Map
instead: it makes no monotonicity assumption at all, and works with negatives.

> ⚠️ **Common mistakes:** updating `best` inside the shrink loop; forgetting
> `start <= end`; and using a window on data with negative values.
""",
            warmup=[
                _q("The three steps per iteration are…",
                   ["shrink, grow, record", "grow, shrink, record", "record, grow, shrink",
                    "grow, record, shrink"], 1,
                   "Record only once the window is valid again."),
                _q("`best` is updated…",
                   ["inside the shrink loop", "after it", "before growing", "twice"], 1,
                   "The invariant only holds there."),
                _q("It stays O(n) because…",
                   ["the inner loop is short", "`start` only moves forward, so the inner loop runs n times in TOTAL",
                    "of the Map", "k is small"], 1,
                   "Total work, not nesting."),
                _q("A window fails on negative values because…",
                   ["of types", "growing can reduce the sum, so the condition is not monotonic",
                    "of the shrink", "it does not"], 1,
                   "Prefix sums plus a Map handle that case."),
            ],
            exercises=[
                _ex("tscourse-w23-vr-1", "Shrink until valid",
                    "Remove elements from the left while the window's total exceeds the budget.",
                    _NUMS +
                    'const budget = 7;\n'
                    'let start = 0;\n'
                    'let sum = 0;\n'
                    'let best = 0;\n'
                    'for (let end = 0; end < nums.length; end = end + 1) {\n'
                    '  sum = sum + (nums[end] ?? 0);\n'
                    '  while (sum > budget && start <= end) {\n'
                    '    sum = sum - (nums[start] ?? 0);\n'
                    '    start = start + 1;\n  }\n'
                    '  best = Math.max(best, end - start + 1);\n}\n'
                    'console.log(best);\n',
                    '  while (sum > budget && start <= end) {\n'
                    '    sum = sum - (nums[start] ?? 0);\n'
                    '    start = start + 1;\n  }',
                    [("1 2 3 4 5", "3"), ("10 1", "1"), ("1 1 1", "3")],
                    hints=["Keep removing from the left until the total fits.",
                           "The guard `start <= end` handles a single element that is too big on its own."],
                    difficulty="Hard"),
                _ex("tscourse-w23-vr-2", "Record after the shrink",
                    "Update the best width where the invariant holds.",
                    _NUMS +
                    'const budget = 7;\n'
                    'let start = 0;\n'
                    'let sum = 0;\n'
                    'let best = 0;\n'
                    'for (let end = 0; end < nums.length; end = end + 1) {\n'
                    '  sum = sum + (nums[end] ?? 0);\n'
                    '  while (sum > budget && start <= end) {\n'
                    '    sum = sum - (nums[start] ?? 0);\n'
                    '    start = start + 1;\n  }\n'
                    '  best = Math.max(best, end - start + 1);\n}\n'
                    'console.log(best);\n',
                    '  best = Math.max(best, end - start + 1);',
                    [("1 2 3 4 5", "3"), ("7", "1")],
                    hints=["The width of an inclusive range is end - start + 1.",
                           "Write best = Math.max(best, end - start + 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w23-vr-3", "Count the total inner steps",
                    "Report how many times the shrink loop ran altogether, and compare it to n.",
                    _NUMS +
                    'const budget = 5;\n'
                    'let start = 0;\n'
                    'let sum = 0;\n'
                    'let shrinks = 0;\n'
                    'for (let end = 0; end < nums.length; end = end + 1) {\n'
                    '  sum = sum + (nums[end] ?? 0);\n'
                    '  while (sum > budget && start <= end) {\n'
                    '    sum = sum - (nums[start] ?? 0);\n'
                    '    start = start + 1;\n'
                    '    shrinks = shrinks + 1;\n  }\n}\n'
                    'console.log(`n=${nums.length} shrinks=${shrinks}`);\n',
                    '    shrinks = shrinks + 1;',
                    [("1 2 3 4 5", "n=5 shrinks=4"), ("1 1", "n=2 shrinks=0")],
                    hints=["One per element removed from the left, across the whole run.",
                           "Write shrinks = shrinks + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w23-vr-4", "The smallest window that reaches a target",
                    "Shrink while the window is still large enough, keeping the narrowest that qualifies.",
                    _NUMS +
                    'const target = 7;\n'
                    'let start = 0;\n'
                    'let sum = 0;\n'
                    'let best = Number.MAX_SAFE_INTEGER;\n'
                    'for (let end = 0; end < nums.length; end = end + 1) {\n'
                    '  sum = sum + (nums[end] ?? 0);\n'
                    '  while (sum >= target) {\n'
                    '    best = Math.min(best, end - start + 1);\n'
                    '    sum = sum - (nums[start] ?? 0);\n'
                    '    start = start + 1;\n  }\n}\n'
                    'console.log(best === Number.MAX_SAFE_INTEGER ? 0 : best);\n',
                    '    best = Math.min(best, end - start + 1);',
                    [("2 3 1 2 4 3", "2"), ("1 1", "0"), ("7", "1")],
                    hints=["Here the window is recorded INSIDE the loop, because the condition being met is what qualifies it.",
                           "Write best = Math.min(best, end - start + 1);"],
                    difficulty="Hard"),
                _ex("tscourse-w23-vr-5", "Longest run of small amounts",
                    "A window whose condition is per-element rather than a total.",
                    _NUMS +
                    'let start = 0;\n'
                    'let best = 0;\n'
                    'for (let end = 0; end < nums.length; end = end + 1) {\n'
                    '  if ((nums[end] ?? 0) > 3) {\n'
                    '    start = end + 1;\n  }\n'
                    '  best = Math.max(best, end - start + 1);\n}\n'
                    'console.log(best);\n',
                    '    start = end + 1;',
                    [("1 2 9 1 2 3", "3"), ("9 9", "0"), ("1 2", "2")],
                    hints=["A disqualifying element means the window must restart after it.",
                           "Write start = end + 1;"],
                    difficulty="Medium"),
                _fix("tscourse-w23-vr-fix1", "Fix the record inside the shrink loop",
                     "This reports 5 for a budget of 7 — a width that never satisfied the budget at all. `best` is updated before the shrink loop has restored the invariant, so it measures windows that were too big.",
                     _NUMS +
                     'const budget = 7;\n'
                     'let start = 0;\n'
                     'let sum = 0;\n'
                     'let best = 0;\n'
                     'for (let end = 0; end < nums.length; end = end + 1) {\n'
                     '  sum = sum + (nums[end] ?? 0);\n'
                     '  best = Math.max(best, end - start + 1);\n'
                     '  while (sum > budget && start <= end) {\n'
                     '    sum = sum - (nums[start] ?? 0);\n'
                     '    start = start + 1;\n  }\n}\n'
                     'console.log(best);\n',
                     _NUMS +
                     'const budget = 7;\n'
                     'let start = 0;\n'
                     'let sum = 0;\n'
                     'let best = 0;\n'
                     'for (let end = 0; end < nums.length; end = end + 1) {\n'
                     '  sum = sum + (nums[end] ?? 0);\n'
                     '  while (sum > budget && start <= end) {\n'
                     '    sum = sum - (nums[start] ?? 0);\n'
                     '    start = start + 1;\n  }\n'
                     '  best = Math.max(best, end - start + 1);\n}\n'
                     'console.log(best);\n',
                     [("1 2 3 4 5", "3"), ("10 1", "1")],
                     hints=["At the moment `best` is read, the window has just grown and may be invalid.",
                            "The invariant only holds after the shrink loop.",
                            "Move the `best` update below the while loop."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`start <= end` in the shrink condition guards…",
                   ["an empty array", "a single element that already breaks the condition",
                    "the budget", "nothing"], 1,
                   "Otherwise the width goes negative."),
                _q("For the SMALLEST window reaching a target, `best` is recorded…",
                   ["after the loop", "inside the shrink loop, because meeting the condition is what qualifies it",
                    "before growing", "never"], 1,
                   "The mirror image of the longest-window case."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w23-counts", "A window that remembers what is in it",
            "Week 19's Map, inside week 22's two pointers.",
            """
When the condition is about the window's **contents** rather than its total, the
window carries a `Map` of counts.

## Entering and leaving

```ts
counts.set(v, (counts.get(v) ?? 0) + 1);            // entering — week 19's idiom

const left = (counts.get(out) ?? 0) - 1;            // leaving
if (left === 0) { counts.delete(out); }              // delete, do not leave a 0
else { counts.set(out, left); }
```

**The delete is load-bearing.** `counts.size` is how you know how many *distinct*
values are in the window, and a key sitting at zero would be counted. This is the
one place where "set it to 0" and "remove it" are genuinely different.

## Longest stretch with no repeat

```ts
const lastSeen = new Map<string, number>();
let start = 0;
let best = 0;
for (let i = 0; i < text.length; i = i + 1) {
  const ch = text.charAt(i);
  const prev = lastSeen.get(ch);
  if (prev !== undefined && prev >= start) {
    start = prev + 1;                 // jump the window past the earlier copy
  }
  lastSeen.set(ch, i);
  best = Math.max(best, i - start + 1);
}
```

Note `prev >= start`: a character seen *before* the window began is not a repeat
inside it, and that check is the only subtle line. Storing the **last index** rather
than a count lets `start` jump straight there instead of shrinking one at a time —
still O(n), and less code.

On `"abcabcbb"` the answer is 3; on `"bbbbb"` it is 1; on `"pwwkew"` it is 3.

## At most k distinct, and then exactly k

```ts
while (counts.size > k) { /* remove from the left */ }
total = total + (end - start + 1);      // every window ending at `end` is valid
```

That `total +=` line counts **subarrays**, not width: if the window `[start, end]`
is valid, so is every window ending at `end` that starts at or after `start` —
which is `end - start + 1` of them.

And then the trick worth remembering:

> **exactly k  =  atMost(k) − atMost(k − 1)**

Because "at most k" includes every window with fewer, so subtracting "at most k−1"
leaves precisely those with k. On `[1,2,1,2,3]`: atMost(2) is 12, atMost(1) is 5,
so exactly-2 is **7**. Two runs of the same function, no third algorithm.

That pattern — compute a cumulative answer twice and subtract — appears all over
counting problems, and it is the same arithmetic as week 22's
`upperBound − lowerBound`.

> ⚠️ **Common mistakes:** leaving a zero count in the Map; forgetting
> `prev >= start`; and adding 1 to the total instead of `end - start + 1`.
""",
            warmup=[
                _q("When a value leaves the window and its count hits 0 you must…",
                   ["set it to 0", "delete the key", "ignore it", "reset the Map"], 1,
                   "Or `size` counts it."),
                _q("`prev >= start` checks that…",
                   ["the character exists", "the earlier copy is INSIDE the current window",
                    "the window is valid", "start moved"], 1,
                   "A copy before the window is not a repeat."),
                _q("`total = total + (end - start + 1)` counts…",
                   ["the width", "every valid subarray ending at `end`", "distinct values",
                    "one window"], 1,
                   "Which is how you count subarrays rather than measure one."),
                _q("Exactly k distinct equals…",
                   ["atMost(k)", "atMost(k) - atMost(k-1)", "k", "atLeast(k)"], 1,
                   "Two runs and a subtraction."),
            ],
            exercises=[
                _ex("tscourse-w23-ct-1", "Jump past the repeat",
                    "When the character was already seen inside the window, move the start past it.",
                    _LINE +
                    'const lastSeen = new Map<string, number>();\n'
                    'let start = 0;\n'
                    'let best = 0;\n'
                    'for (let i = 0; i < line.length; i = i + 1) {\n'
                    '  const ch = line.charAt(i);\n'
                    '  const prev = lastSeen.get(ch);\n'
                    '  if (prev !== undefined && prev >= start) {\n'
                    '    start = prev + 1;\n  }\n'
                    '  lastSeen.set(ch, i);\n'
                    '  best = Math.max(best, i - start + 1);\n}\n'
                    'console.log(best);\n',
                    '  if (prev !== undefined && prev >= start) {\n'
                    '    start = prev + 1;\n  }',
                    [("abcabcbb", "3"), ("bbbbb", "1"), ("pwwkew", "3")],
                    hints=["Only a copy at or after `start` is a repeat within the window.",
                           "Move the window to begin just after the earlier copy."],
                    difficulty="Hard"),
                _ex("tscourse-w23-ct-2", "Delete the exhausted key",
                    "Remove the key entirely when its count reaches zero, so `size` stays honest.",
                    _NUMS +
                    'const counts = new Map<number, number>();\n'
                    'for (const n of nums) {\n'
                    '  counts.set(n, (counts.get(n) ?? 0) + 1);\n}\n'
                    'const first = nums[0] ?? 0;\n'
                    'const left = (counts.get(first) ?? 0) - 1;\n'
                    'if (left === 0) {\n'
                    '  counts.delete(first);\n'
                    '} else {\n'
                    '  counts.set(first, left);\n}\n'
                    'console.log(counts.size);\n',
                    'if (left === 0) {\n'
                    '  counts.delete(first);\n'
                    '} else {\n'
                    '  counts.set(first, left);\n}',
                    [("1 2 3", "2"), ("1 1 2", "2")],
                    hints=["A zero left in the Map would still be counted by `size`.",
                           "Delete when it reaches zero, otherwise store the decremented count."],
                    difficulty="Medium"),
                _ex("tscourse-w23-ct-3", "At most k distinct",
                    "Count every valid subarray ending at each position.",
                    _NUMS +
                    'function atMost(xs: readonly number[], k: number): number {\n'
                    '  const counts = new Map<number, number>();\n'
                    '  let start = 0;\n'
                    '  let total = 0;\n'
                    '  for (let end = 0; end < xs.length; end = end + 1) {\n'
                    '    const v = xs[end] ?? 0;\n'
                    '    counts.set(v, (counts.get(v) ?? 0) + 1);\n'
                    '    while (counts.size > k) {\n'
                    '      const out = xs[start] ?? 0;\n'
                    '      const left = (counts.get(out) ?? 0) - 1;\n'
                    '      if (left === 0) {\n'
                    '        counts.delete(out);\n'
                    '      } else {\n'
                    '        counts.set(out, left);\n      }\n'
                    '      start = start + 1;\n    }\n'
                    '    total = total + (end - start + 1);\n  }\n'
                    '  return total;\n}\n'
                    'console.log(atMost(nums, 2));\n',
                    '    total = total + (end - start + 1);',
                    [("1 2 1 2 3", "12"), ("1 1", "3")],
                    hints=["Every window ending here and starting at or after `start` is valid.",
                           "Write total = total + (end - start + 1);"],
                    difficulty="Hard"),
                _ex("tscourse-w23-ct-4", "Exactly k, by subtraction",
                    "Run the same function twice and subtract.",
                    _NUMS +
                    'function atMost(xs: readonly number[], k: number): number {\n'
                    '  const counts = new Map<number, number>();\n'
                    '  let start = 0;\n'
                    '  let total = 0;\n'
                    '  for (let end = 0; end < xs.length; end = end + 1) {\n'
                    '    const v = xs[end] ?? 0;\n'
                    '    counts.set(v, (counts.get(v) ?? 0) + 1);\n'
                    '    while (counts.size > k) {\n'
                    '      const out = xs[start] ?? 0;\n'
                    '      const left = (counts.get(out) ?? 0) - 1;\n'
                    '      if (left === 0) {\n'
                    '        counts.delete(out);\n'
                    '      } else {\n'
                    '        counts.set(out, left);\n      }\n'
                    '      start = start + 1;\n    }\n'
                    '    total = total + (end - start + 1);\n  }\n'
                    '  return total;\n}\n'
                    'console.log(atMost(nums, 2) - atMost(nums, 1));\n',
                    'console.log(atMost(nums, 2) - atMost(nums, 1));',
                    [("1 2 1 2 3", "7"), ("1 1", "0")],
                    hints=["At most two, minus at most one.",
                           "Write console.log(atMost(nums, 2) - atMost(nums, 1));"],
                    difficulty="Medium"),
                _ex("tscourse-w23-ct-5", "The most frequent value in the window",
                    "Track the running maximum count as elements enter, which is enough for a fixed window.",
                    _WORDS +
                    'const counts = new Map<string, number>();\n'
                    'let mostCommon = 0;\n'
                    'for (const w of words) {\n'
                    '  const n = (counts.get(w) ?? 0) + 1;\n'
                    '  counts.set(w, n);\n'
                    '  mostCommon = Math.max(mostCommon, n);\n}\n'
                    'console.log(`${counts.size} ${mostCommon}`);\n',
                    '  mostCommon = Math.max(mostCommon, n);',
                    [("a b a c a", "3 3"), ("x", "1 1")],
                    hints=["The new count for this value may be the largest seen.",
                           "Write mostCommon = Math.max(mostCommon, n);"],
                    difficulty="Easy"),
                _fix("tscourse-w23-ct-fix1", "Fix the zero left in the Map",
                     "This reports 3 distinct values in a window that holds two, because a key whose count dropped to zero was stored rather than removed — and `size` counts keys, not totals.",
                     _NUMS +
                     'const counts = new Map<number, number>();\n'
                     'for (const n of nums) {\n'
                     '  counts.set(n, (counts.get(n) ?? 0) + 1);\n}\n'
                     'const first = nums[0] ?? 0;\n'
                     'counts.set(first, (counts.get(first) ?? 0) - 1);\n'
                     'console.log(counts.size);\n',
                     _NUMS +
                     'const counts = new Map<number, number>();\n'
                     'for (const n of nums) {\n'
                     '  counts.set(n, (counts.get(n) ?? 0) + 1);\n}\n'
                     'const first = nums[0] ?? 0;\n'
                     'const left = (counts.get(first) ?? 0) - 1;\n'
                     'if (left === 0) {\n'
                     '  counts.delete(first);\n'
                     '} else {\n'
                     '  counts.set(first, left);\n}\n'
                     'console.log(counts.size);\n',
                     [("1 2 3", "2"), ("1 1 2", "2")],
                     hints=["`size` is the number of KEYS, and a key holding 0 is still a key.",
                            "Decide before storing: is the new count zero?",
                            "Delete the key in that case."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Storing the last INDEX rather than a count lets you…",
                   ["use less memory", "jump `start` straight past the earlier copy", "sort",
                    "avoid the Map"], 1,
                   "Still O(n), and less code."),
                _q("\"Compute a cumulative answer twice and subtract\" also describes…",
                   ["binary search", "week 22's upperBound - lowerBound", "a window", "a sort"], 1,
                   "The same arithmetic in a different costume."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w23-prefix", "Prefix sums",
            "Pay O(n) once; answer every range in O(1) for ever.",
            """
"The total between index 3 and index 7." Once, a loop is fine. A thousand times,
precompute:

```ts
const prefix: number[] = [0];                       // the sentinel
for (const x of xs) {
  prefix.push((prefix[prefix.length - 1] ?? 0) + x);
}
```

```
xs     =    [1, 2, 3,  4,  5]
prefix = [0, 1, 3, 6, 10, 15]
```

`prefix[i]` is the total of the **first i elements** — so `prefix[0]` is 0 (no
elements) and `prefix[5]` is everything.

## The query

```ts
function rangeSum(lo: number, hi: number): number {    // INCLUSIVE both ends
  return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);
}
```

`rangeSum(1, 3)` is `prefix[4] - prefix[1]` = 10 − 1 = **9**, which is 2+3+4. ✓

Two details, and between them they are every prefix-sum bug:

* **`hi + 1`, not `hi`.** The prefix at `hi + 1` includes element `hi`, which is
  what "inclusive" means. Using `prefix[hi]` gives you the sum of `[lo, hi-1]` —
  one element short, and it looks plausible.
* **The leading 0 is why `lo` needs no adjustment.** Without the sentinel,
  `rangeSum(0, hi)` would need a special case (`lo === 0 ? prefix[hi] : …`). The
  sentinel is one array slot that deletes a branch, which is the same trade as week
  20's sentinel node.

## The trade

| | build | per query |
|---|---|---|
| loop each time | — | O(n) |
| prefix sums | O(n) once | **O(1)** |

Worth it from the second query onwards, and it is **not** free: the array is O(n)
extra space, and it is **invalidated by any change to the input**. A prefix sum is
for data you read far more often than you write — and when writes dominate, lesson
6's difference array inverts exactly this trade.

## Beyond sums

The same construction works for anything with an inverse: a running count, a
running XOR, a product without zeroes. It does **not** work for a maximum — you
cannot un-max — which is the same limitation as the sliding window, and the reason
range-maximum queries need a different structure entirely.

> ⚠️ **Common mistakes:** `prefix[hi]` instead of `prefix[hi + 1]`; omitting the
> sentinel and needing a branch; and using a stale prefix array after the input
> changed.
""",
            warmup=[
                _q("A prefix array for n elements has…",
                   ["n entries", "n + 1", "n - 1", "2n"], 1,
                   "The sentinel is the extra one."),
                _q("The inclusive range sum is…",
                   ["prefix[hi] - prefix[lo]", "prefix[hi + 1] - prefix[lo]",
                    "prefix[hi] - prefix[lo - 1]", "prefix[hi] + prefix[lo]"], 1,
                   "`hi + 1` includes element hi."),
                _q("The leading 0 removes…",
                   ["a loop", "the `lo === 0` special case", "the sum", "an allocation"], 1,
                   "One slot instead of a branch."),
                _q("A prefix array is invalidated by…",
                   ["a query", "any change to the input", "nothing", "a sort"], 1,
                   "It is for read-heavy data."),
            ],
            exercises=[
                _ex("tscourse-w23-pf-1", "Build it with its sentinel",
                    "Start the array at zero, then push each running total.",
                    _NUMS + _PREFIX +
                    'console.log(prefixOf(nums).join(","));\n',
                    '  const prefix: number[] = [0];',
                    [("1 2 3 4 5", "0,1,3,6,10,15"), ("7", "0,7")],
                    hints=["The first entry is the total of no elements.",
                           "Write const prefix: number[] = [0];"],
                    difficulty="Easy"),
                _ex("tscourse-w23-pf-2", "The inclusive query",
                    "Subtract the prefix before the range from the prefix through its end.",
                    _NUMS + _PREFIX +
                    'const prefix = prefixOf(nums);\n'
                    'function rangeSum(lo: number, hi: number): number {\n'
                    '  return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);\n}\n'
                    'console.log(`${rangeSum(0, nums.length - 1)} ${rangeSum(1, 3)}`);\n',
                    '  return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);',
                    # The exercise queries rangeSum(1, 3), so every case needs at
                    # least four elements for that range to exist.
                    [("1 2 3 4 5", "15 9"), ("2 4 6 8", "20 18")],
                    hints=["The prefix at `hi + 1` already includes element `hi`.",
                           "Write return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);"],
                    difficulty="Medium"),
                _ex("tscourse-w23-pf-3", "Many queries, one build",
                    "Answer three ranges from the same table and report how many builds it took.",
                    _NUMS + _PREFIX +
                    'let builds = 0;\n'
                    'builds = builds + 1;\n'
                    'const prefix = prefixOf(nums);\n'
                    'function rangeSum(lo: number, hi: number): number {\n'
                    '  return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);\n}\n'
                    'console.log(`${rangeSum(0, 1)} ${rangeSum(1, 2)} ${rangeSum(0, 2)} builds=${builds}`);\n',
                    'console.log(`${rangeSum(0, 1)} ${rangeSum(1, 2)} ${rangeSum(0, 2)} builds=${builds}`);',
                    [("1 2 3", "3 5 6 builds=1"), ("5 5 5", "10 10 15 builds=1")],
                    hints=["Three queries, one build — which is the entire argument.",
                           "Write the log line with all four values."],
                    difficulty="Easy"),
                _ex("tscourse-w23-pf-4", "A prefix count",
                    "Build a prefix over 0s and 1s, so a range query counts matching elements.",
                    _NUMS +
                    'const prefix: number[] = [0];\n'
                    'for (const n of nums) {\n'
                    '  prefix.push((prefix[prefix.length - 1] ?? 0) + (n > 2 ? 1 : 0));\n}\n'
                    'function countBig(lo: number, hi: number): number {\n'
                    '  return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);\n}\n'
                    'console.log(`${countBig(0, nums.length - 1)} ${countBig(0, 1)}`);\n',
                    '  prefix.push((prefix[prefix.length - 1] ?? 0) + (n > 2 ? 1 : 0));',
                    [("1 4 5 1", "2 1"), ("9 9", "2 2")],
                    hints=["Contribute 1 for a matching element and 0 otherwise.",
                           "Write prefix.push((prefix[prefix.length - 1] ?? 0) + (n > 2 ? 1 : 0));"],
                    difficulty="Medium"),
                _ex("tscourse-w23-pf-5", "The average of a range",
                    "Divide the range total by its width, to two decimals.",
                    _NUMS + _PREFIX +
                    'const prefix = prefixOf(nums);\n'
                    'function rangeAvg(lo: number, hi: number): string {\n'
                    '  const total = (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);\n'
                    '  return (total / (hi - lo + 1)).toFixed(2);\n}\n'
                    'console.log(rangeAvg(0, nums.length - 1));\n',
                    '  return (total / (hi - lo + 1)).toFixed(2);',
                    [("1 2 3", "2.00"), ("2 4", "3.00")],
                    hints=["An inclusive range has hi - lo + 1 elements.",
                           "Write return (total / (hi - lo + 1)).toFixed(2);"],
                    difficulty="Medium"),
                _fix("tscourse-w23-pf-fix1", "Fix the range that was one short",
                     "`rangeSum(1, 3)` on `[1,2,3,4,5]` reports 6 where the answer is 9. `prefix[hi]` is the total *before* element `hi`, so the last element of the range is left out every time.",
                     _NUMS + _PREFIX +
                     'const prefix = prefixOf(nums);\n'
                     'function rangeSum(lo: number, hi: number): number {\n'
                     '  return (prefix[hi] ?? 0) - (prefix[lo] ?? 0);\n}\n'
                     'console.log(rangeSum(1, 3));\n',
                     _NUMS + _PREFIX +
                     'const prefix = prefixOf(nums);\n'
                     'function rangeSum(lo: number, hi: number): number {\n'
                     '  return (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);\n}\n'
                     'console.log(rangeSum(1, 3));\n',
                     [("1 2 3 4 5", "9"), ("5 5 5 5", "15")],
                     hints=["The prefix array is offset by one from the input, and the query has to account for it.",
                            "`prefix[hi]` totals the first `hi` elements — which stops just before element `hi`.",
                            "Write prefix[hi + 1]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Prefix sums do not work for a maximum because…",
                   ["they are slow", "you cannot un-max — there is no inverse", "of the sentinel",
                    "of types"], 1,
                   "The same limitation as a sliding window."),
                _q("Prefix sums are the wrong choice when…",
                   ["there are many queries", "writes dominate reads", "the array is large",
                    "values are negative"], 1,
                   "Which is what lesson 6 inverts."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w23-submap", "Prefix sums plus a Map",
            "The highest-yield trick in the month.",
            """
"How many contiguous stretches sum to exactly `k`?"

A window cannot do it: the values may be negative, so growing the window can reduce
the sum and the condition is not monotonic (lesson 2). But there is a one-pass
answer, and it is the combination this whole month has been building towards.

## The idea

A subarray `(i, j]` sums to `k` exactly when

```
running(j) - running(i) === k        ⇔        running(i) === running(j) - k
```

So as you walk, keep a **Map of every running total you have seen and how often**.
At each step, the number of subarrays *ending here* with sum `k` is the number of
times `running - k` has been seen before.

```ts
const seen = new Map<number, number>();
seen.set(0, 1);                                   // the empty prefix. REQUIRED.
let running = 0;
let count = 0;
for (const x of xs) {
  running = running + x;
  count = count + (seen.get(running - k) ?? 0);    // the complement
  seen.set(running, (seen.get(running) ?? 0) + 1);
}
```

One pass, **O(n)** time and O(n) space, and it handles negative values without a
thought.

## `seen.set(0, 1)` is not optional

It records that a running total of 0 has occurred once — **before any element**.
Without it, every subarray that starts at index 0 is missed, because for those
`running - k` is exactly 0 and nothing would have registered it. On `[1,2,3]` with
k = 3 the answer is 2 (`[1,2]` and `[3]`); omit that line and you get 1.

This is the single most commonly forgotten line in the pattern, and the empty prefix
is what it stands for — the same sentinel idea as lesson 4's leading zero.

## The order matters

Look up the complement **before** recording the current total. Reverse them and a
`k` of 0 counts each element as a subarray with itself.

## Verified answers

```
[1,1,1] k=2                  ->  2
[1,2,3] k=3                  ->  2
[3,4,7,2,-3,1,4,2] k=7       ->  4      ← the negative makes a window impossible
```

That third one is the case to remember: `-3` in the data rules out the sliding
window entirely, and this pattern does not care.

## The family

The same shape solves a surprising range once you see it:

* **A subarray divisible by k** — key on `running % k` instead of `running`.
* **The longest subarray summing to k** — store the *first* index each total
  appeared at, rather than a count.
* **Equal numbers of two things** — map one to +1 and the other to −1, then count
  subarrays summing to 0.

All three are "prefix, complement, Map". Recognising that is worth more than any one
of them.

> ⚠️ **Common mistakes:** omitting `seen.set(0, 1)`; recording before looking up;
> and reaching for a sliding window on data with negatives.
""",
            warmup=[
                _q("A subarray sums to k exactly when…",
                   ["running === k", "running(j) - running(i) === k for some earlier i",
                    "the window fits", "k is positive"], 1,
                   "Which is a lookup for `running - k`."),
                _q("`seen.set(0, 1)` before the loop accounts for…",
                   ["the target", "the empty prefix — subarrays starting at index 0", "the first element",
                    "nothing"], 1,
                   "Omit it and you undercount."),
                _q("Look up the complement…",
                   ["after recording", "before recording the current total", "twice", "at the end"], 1,
                   "Or k = 0 counts each element with itself."),
                _q("This works with negative values where a window does not, because…",
                   ["it is faster", "it assumes no monotonicity at all", "of the Map",
                    "of the sentinel"], 1,
                   "That is the whole reason it exists."),
            ],
            exercises=[
                _ex("tscourse-w23-sm-1", "Seed the empty prefix",
                    "Record that a running total of zero has been seen once, before the walk begins.",
                    _NUMS +
                    'const target = 3;\n'
                    'const seen = new Map<number, number>();\n'
                    'seen.set(0, 1);\n'
                    'let running = 0;\n'
                    'let count = 0;\n'
                    'for (const x of nums) {\n'
                    '  running = running + x;\n'
                    '  count = count + (seen.get(running - target) ?? 0);\n'
                    '  seen.set(running, (seen.get(running) ?? 0) + 1);\n}\n'
                    'console.log(count);\n',
                    'seen.set(0, 1);',
                    [("1 2 3", "2"), ("3", "1"), ("1 1", "0")],
                    hints=["Before any element, the running total is zero and that has happened once.",
                           "Write seen.set(0, 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w23-sm-2", "Look up the complement",
                    "Count how many earlier running totals would make a subarray ending here sum to the target.",
                    _NUMS +
                    'const target = 2;\n'
                    'const seen = new Map<number, number>();\n'
                    'seen.set(0, 1);\n'
                    'let running = 0;\n'
                    'let count = 0;\n'
                    'for (const x of nums) {\n'
                    '  running = running + x;\n'
                    '  count = count + (seen.get(running - target) ?? 0);\n'
                    '  seen.set(running, (seen.get(running) ?? 0) + 1);\n}\n'
                    'console.log(count);\n',
                    '  count = count + (seen.get(running - target) ?? 0);',
                    [("1 1 1", "2"), ("2 2", "2")],
                    hints=["The complement is the running total minus the target.",
                           "Write count = count + (seen.get(running - target) ?? 0);"],
                    difficulty="Medium"),
                _ex("tscourse-w23-sm-3", "With a negative in the data",
                    "Run the same pass on data a sliding window could not handle.",
                    _NUMS +
                    'const target = 7;\n'
                    'const seen = new Map<number, number>();\n'
                    'seen.set(0, 1);\n'
                    'let running = 0;\n'
                    'let count = 0;\n'
                    'for (const x of nums) {\n'
                    '  running = running + x;\n'
                    '  count = count + (seen.get(running - target) ?? 0);\n'
                    '  seen.set(running, (seen.get(running) ?? 0) + 1);\n}\n'
                    'console.log(`count=${count}`);\n',
                    '  seen.set(running, (seen.get(running) ?? 0) + 1);',
                    [("3 4 7 2 -3 1 4 2", "count=4"), ("7 -7 7", "count=3")],
                    hints=["Record the current running total, incrementing how often it has occurred.",
                           "Write seen.set(running, (seen.get(running) ?? 0) + 1);"],
                    difficulty="Hard"),
                _ex("tscourse-w23-sm-4", "Divisible by k",
                    "Key on the remainder instead of the total, and count subarrays divisible by k.",
                    _NUMS +
                    'const k = 3;\n'
                    'const seen = new Map<number, number>();\n'
                    'seen.set(0, 1);\n'
                    'let running = 0;\n'
                    'let count = 0;\n'
                    'for (const x of nums) {\n'
                    '  running = running + x;\n'
                    '  const key = ((running % k) + k) % k;\n'
                    '  count = count + (seen.get(key) ?? 0);\n'
                    '  seen.set(key, (seen.get(key) ?? 0) + 1);\n}\n'
                    'console.log(count);\n',
                    '  const key = ((running % k) + k) % k;',
                    [("3 6 9", "6"), ("1 2 3", "3")],
                    hints=["JavaScript's `%` can be negative, so normalise it into 0…k-1.",
                           "Write const key = ((running % k) + k) % k;"],
                    difficulty="Hard"),
                _ex("tscourse-w23-sm-5", "The longest one, not the count",
                    "Store the first index each running total appeared at, so the width can be measured.",
                    _NUMS +
                    'const target = 3;\n'
                    'const firstAt = new Map<number, number>();\n'
                    'firstAt.set(0, -1);\n'
                    'let running = 0;\n'
                    'let best = 0;\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  running = running + (nums[i] ?? 0);\n'
                    '  const at = firstAt.get(running - target);\n'
                    '  if (at !== undefined) {\n'
                    '    best = Math.max(best, i - at);\n  }\n'
                    '  if (!firstAt.has(running)) {\n'
                    '    firstAt.set(running, i);\n  }\n}\n'
                    'console.log(best);\n',
                    '  if (!firstAt.has(running)) {\n'
                    '    firstAt.set(running, i);\n  }',
                    [("1 2 3", "2"), ("3 0 0", "3"), ("1 1", "0")],
                    hints=["Only the FIRST occurrence of a total gives the widest span, so do not overwrite it.",
                           "Write if (!firstAt.has(running)) { firstAt.set(running, i); }"],
                    difficulty="Hard"),
                _fix("tscourse-w23-sm-fix1", "Fix the missing empty prefix",
                     "On `[1,2,3]` with a target of 3 this reports 1 where the answer is 2. The subarray `[1,2]` starts at index 0, and nothing ever recorded that a running total of zero had occurred before the walk began.",
                     _NUMS +
                     'const target = 3;\n'
                     'const seen = new Map<number, number>();\n'
                     'let running = 0;\n'
                     'let count = 0;\n'
                     'for (const x of nums) {\n'
                     '  running = running + x;\n'
                     '  count = count + (seen.get(running - target) ?? 0);\n'
                     '  seen.set(running, (seen.get(running) ?? 0) + 1);\n}\n'
                     'console.log(count);\n',
                     _NUMS +
                     'const target = 3;\n'
                     'const seen = new Map<number, number>();\n'
                     'seen.set(0, 1);\n'
                     'let running = 0;\n'
                     'let count = 0;\n'
                     'for (const x of nums) {\n'
                     '  running = running + x;\n'
                     '  count = count + (seen.get(running - target) ?? 0);\n'
                     '  seen.set(running, (seen.get(running) ?? 0) + 1);\n}\n'
                     'console.log(count);\n',
                     [("1 2 3", "2"), ("3", "1"), ("1 2", "1")],
                     hints=["Every subarray that begins at index 0 needs a complement of exactly 0.",
                            "Nothing in the loop can ever have registered that.",
                            "Seed the Map with `0` seen once, before the loop."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("\"Equal numbers of two things\" becomes this pattern by…",
                   ["sorting", "mapping one to +1 and the other to -1, then counting sums of 0",
                    "using a window", "a prefix array"], 1,
                   "Prefix, complement, Map."),
                _q("For the LONGEST subarray you store…",
                   ["a count", "the FIRST index each total appeared at", "the last index",
                    "the width"], 1,
                   "And you must not overwrite it."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w23-diff", "Difference arrays",
            "Prefix sums, run backwards: cheap writes instead of cheap reads.",
            """
A prefix sum makes **reads** cheap. Sometimes it is the **writes** that repeat:

> "Add £5 to days 1–3." "Add £3 to days 2–4." A hundred times. Then tell me the
> totals.

Applying each update element by element is O(range) per update. A **difference
array** makes each one two writes.

## The idea

Store the **changes**, not the values:

```ts
const diff: number[] = new Array(n + 1).fill(0);    // n + 1 long, deliberately

function addRange(lo: number, hi: number, amount: number): void {
  diff[lo] = (diff[lo] ?? 0) + amount;              // from here, add it
  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;      // from just past here, stop
}
```

Then **one pass** turns the changes back into values — which is a running sum,
i.e. a prefix sum:

```ts
let running = 0;
for (let i = 0; i < n; i = i + 1) {
  running = running + (diff[i] ?? 0);
  out.push(running);
}
```

Two updates on a 5-element array — `addRange(0, 2, 5)` and `addRange(1, 3, 3)` —
give `5, 8, 8, 3, 0`. Worth tracing by hand once: the `-5` at index 3 and the `-3`
at index 4 are what turn the ranges off.

## Why the array is `n + 1` long

`hi + 1` can be `n` — for a range that runs to the last element. Making the array
one longer means that write always has somewhere to go, and the extra slot is simply
never read. A sentinel again, exactly like lesson 4's leading zero and week 20's
sentinel node: **one wasted slot in exchange for deleting a branch.** Three
appearances of the same idea in this course is not a coincidence — it is worth
recognising as a technique.

## The trade, against lesson 4

| | build | update a range | read one value |
|---|---|---|---|
| plain array | — | O(range) | O(1) |
| prefix sums | O(n) | **O(n) rebuild** | O(1) range query |
| difference array | — | **O(1)** | O(n) to materialise |

They are mirror images. Prefix sums: pay once, read cheaply, writes are expensive.
Difference array: write cheaply, pay once at the end to read.

**The decision is which one repeats.** Many reads: prefix. Many writes then one
read: difference. Both repeating: a segment tree, which is well outside this course
but is worth knowing the name of.

> ⚠️ **Common mistakes:** an array of length `n` rather than `n + 1`; forgetting the
> negative at `hi + 1`; and reading `diff` directly instead of materialising it.
""",
            warmup=[
                _q("A difference array stores…",
                   ["the values", "the changes", "the prefix sums", "the ranges"], 1,
                   "One pass turns them into values."),
                _q("A range update writes…",
                   ["every element", "+amount at lo and -amount at hi + 1", "+amount at lo",
                    "-amount at hi"], 1,
                   "Two writes, any range length."),
                _q("The array is n + 1 long because…",
                   ["of the sentinel value", "`hi + 1` can be n, for a range reaching the last element",
                    "of the sum", "of rounding"], 1,
                   "One wasted slot instead of a branch."),
                _q("Materialising the values is…",
                   ["a sort", "a running sum — a prefix sum", "a scan for each", "free"], 1,
                   "Which is why the two techniques are mirror images."),
            ],
            exercises=[
                _ex("tscourse-w23-df-1", "Turn the range off",
                    "Subtract the amount just past the end of the range.",
                    'const n = 5;\n'
                    'const diff: number[] = new Array(n + 1).fill(0);\n'
                    'function addRange(lo: number, hi: number, amount: number): void {\n'
                    '  diff[lo] = (diff[lo] ?? 0) + amount;\n'
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;\n}\n'
                    'addRange(0, 2, 5);\n'
                    'const out: number[] = [];\n'
                    'let running = 0;\n'
                    'for (let i = 0; i < n; i = i + 1) {\n'
                    '  running = running + (diff[i] ?? 0);\n'
                    '  out.push(running);\n}\n'
                    'console.log(out.join(","));\n',
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;',
                    [("", "5,5,5,0,0")],
                    hints=["The change stops applying at the index just after the range.",
                           "Write diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;"],
                    difficulty="Medium"),
                _ex("tscourse-w23-df-2", "Materialise with a running sum",
                    "Accumulate the changes into values in one pass.",
                    'const n = 5;\n'
                    'const diff: number[] = new Array(n + 1).fill(0);\n'
                    'function addRange(lo: number, hi: number, amount: number): void {\n'
                    '  diff[lo] = (diff[lo] ?? 0) + amount;\n'
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;\n}\n'
                    'addRange(0, 2, 5);\n'
                    'addRange(1, 3, 3);\n'
                    'const out: number[] = [];\n'
                    'let running = 0;\n'
                    'for (let i = 0; i < n; i = i + 1) {\n'
                    '  running = running + (diff[i] ?? 0);\n'
                    '  out.push(running);\n}\n'
                    'console.log(out.join(","));\n',
                    '  running = running + (diff[i] ?? 0);\n'
                    '  out.push(running);',
                    [("", "5,8,8,3,0")],
                    hints=["Carry the running total forward and record it at each index.",
                           "Two lines: add this index's change, then push the total."],
                    difficulty="Medium"),
                _ex("tscourse-w23-df-3", "A range reaching the last element",
                    "Update right to the end, which is why the array has a spare slot.",
                    'const n = 4;\n'
                    'const diff: number[] = new Array(n + 1).fill(0);\n'
                    'function addRange(lo: number, hi: number, amount: number): void {\n'
                    '  diff[lo] = (diff[lo] ?? 0) + amount;\n'
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;\n}\n'
                    'addRange(0, n - 1, 2);\n'
                    'const out: number[] = [];\n'
                    'let running = 0;\n'
                    'for (let i = 0; i < n; i = i + 1) {\n'
                    '  running = running + (diff[i] ?? 0);\n'
                    '  out.push(running);\n}\n'
                    'console.log(`${out.join(",")} spare=${diff[n] ?? 0}`);\n',
                    'addRange(0, n - 1, 2);', [("", "2,2,2,2 spare=-2")],
                    hints=["The whole array is the range, so `hi` is the last index.",
                           "Write addRange(0, n - 1, 2);"],
                    difficulty="Medium"),
                _ex("tscourse-w23-df-4", "Count the writes",
                    "Report the writes the difference array performed against what element-by-element updates would have cost.",
                    'const n = 100;\n'
                    'const updates = 50;\n'
                    'const rangeWidth = 40;\n'
                    'const diffWrites = updates * 2 + n;\n'
                    'const naiveWrites = updates * rangeWidth;\n'
                    'console.log(`diff=${diffWrites} naive=${naiveWrites}`);\n',
                    'const diffWrites = updates * 2 + n;',
                    [("", "diff=200 naive=2000")],
                    hints=["Two writes per update, plus one pass to materialise.",
                           "Write const diffWrites = updates * 2 + n;"],
                    difficulty="Easy"),
                _ex("tscourse-w23-df-5", "Many updates from stdin",
                    "Apply one range update per pair of input numbers, then materialise.",
                    _NUMS +
                    'const n = 6;\n'
                    'const diff: number[] = new Array(n + 1).fill(0);\n'
                    'for (let i = 0; i + 1 < nums.length; i = i + 2) {\n'
                    '  const lo = nums[i] ?? 0;\n'
                    '  const hi = nums[i + 1] ?? 0;\n'
                    '  diff[lo] = (diff[lo] ?? 0) + 1;\n'
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - 1;\n}\n'
                    'const out: number[] = [];\n'
                    'let running = 0;\n'
                    'for (let i = 0; i < n; i = i + 1) {\n'
                    '  running = running + (diff[i] ?? 0);\n'
                    '  out.push(running);\n}\n'
                    'console.log(out.join(","));\n',
                    'for (let i = 0; i + 1 < nums.length; i = i + 2) {',
                    [("0 2 1 3", "1,2,2,1,0,0"), ("0 5", "1,1,1,1,1,1")],
                    hints=["Each pair of numbers is one range, so step two at a time.",
                           "Write for (let i = 0; i + 1 < nums.length; i = i + 2) {"],
                    difficulty="Medium"),
                # NOT the "array one slot too short" bug, which was tried first and
                # does not work as an exercise: `new Array(n)` followed by a write at
                # index `n` simply GROWS the array, so both versions print the same
                # length and the buggy starter passes. The observable bug in this
                # shape is the missing second write.
                _fix("tscourse-w23-df-fix1", "Fix the range that never turned off",
                     "Every adjustment is applied from its start index onwards and never stopped, so the "
                     "amounts leak all the way to the end: this prints `5,8,8,8,8` where it should print "
                     "`5,8,8,3,0`. A range update is TWO writes, and only one of them is here.",
                     'const n = 5;\n'
                     'const diff: number[] = new Array(n + 1).fill(0);\n'
                     'function addRange(lo: number, hi: number, amount: number): void {\n'
                     '  diff[lo] = (diff[lo] ?? 0) + amount;\n}\n'
                     'addRange(0, 2, 5);\n'
                     'addRange(1, 3, 3);\n'
                     'const out: number[] = [];\n'
                     'let running = 0;\n'
                     'for (let i = 0; i < n; i = i + 1) {\n'
                     '  running = running + (diff[i] ?? 0);\n'
                     '  out.push(running);\n}\n'
                     'console.log(out.join(","));\n',
                     'const n = 5;\n'
                     'const diff: number[] = new Array(n + 1).fill(0);\n'
                     'function addRange(lo: number, hi: number, amount: number): void {\n'
                     '  diff[lo] = (diff[lo] ?? 0) + amount;\n'
                     '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;\n}\n'
                     'addRange(0, 2, 5);\n'
                     'addRange(1, 3, 3);\n'
                     'const out: number[] = [];\n'
                     'let running = 0;\n'
                     'for (let i = 0; i < n; i = i + 1) {\n'
                     '  running = running + (diff[i] ?? 0);\n'
                     '  out.push(running);\n}\n'
                     'console.log(out.join(","));\n',
                     [("", "5,8,8,3,0")],
                     hints=["The running sum carries each amount forward for ever, because nothing cancels it.",
                            "A range update marks where the change starts AND where it stops applying.",
                            "Subtract the amount at `hi + 1` — which is why the array is `n + 1` long."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Prefix sums and difference arrays are…",
                   ["the same", "mirror images: cheap reads versus cheap writes", "unrelated",
                    "both O(n) per query"], 1,
                   "The decision is which operation repeats."),
                _q("When BOTH reads and writes repeat you want…",
                   ["a prefix array", "a segment tree", "a Map", "a window"], 1,
                   "Outside this course, but worth knowing the name."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w23-choose", "Choosing, from the wording",
            "The question usually tells you which one.",
            """
Four techniques, and the problem statement nearly always gives it away.

| the wording | the technique |
|---|---|
| "**consecutive**", "**contiguous**", "**longest … such that**" | a window |
| a fixed count — "any **k** days" | a **fixed** window |
| "longest/shortest … such that" | a **variable** window |
| "sum **between** i and j", asked repeatedly | **prefix sums** |
| "**count** the subarrays with …" | prefix sums **+ a Map** |
| many range **updates**, read once at the end | a **difference array** |

## The two questions that decide it

**1. Is the answer about a contiguous stretch?** If not, none of these apply —
sort it, or use a Map.

**2. Are the values all non-negative?**

* **Yes** → a window works, and is O(1) space.
* **No** → a window does **not** work (lesson 2), and prefix-sums-plus-Map does.

That second question is the one people skip, and it is the difference between a
solution and a solution that passes the sample and fails the hidden tests.

## Worked, briefly

> *"The largest total of any 7 consecutive days."* Contiguous, fixed size → fixed
> window. O(n), O(1) space.

> *"The longest run of days whose total stays under the budget."* Contiguous,
> variable size, amounts non-negative → variable window.

> *"The total for days 10–20, and then for 30–40, and then…"* Repeated ranges →
> prefix sums.

> *"How many stretches total exactly £50?"* Counting subarrays, and refunds mean
> negatives → prefix + Map.

> *"Apply 200 range adjustments, then print every day."* Writes dominate →
> difference array.

## And the honest last word

All five are O(n)-ish and all five are short. The skill this week teaches is not the
implementations — it is reading a question and knowing, before writing anything,
which of the five it is. That recognition is what an interviewer is actually
testing, and it is why the table above is worth more than any single exercise in
the week.

> ⚠️ **Common mistakes:** a window on data with negatives; prefix sums for data
> that keeps changing; and a difference array when the reads are what repeat.
""",
            warmup=[
                _q("\"Contiguous\" in a problem statement suggests…",
                   ["a sort", "a window", "a Map", "recursion"], 1,
                   "Along with 'consecutive' and 'longest … such that'."),
                _q("Repeated range totals suggest…",
                   ["a window", "prefix sums", "a difference array", "a sort"], 1,
                   "Pay once, read cheaply."),
                _q("Negative values rule out…",
                   ["prefix sums", "a sliding window", "a Map", "a difference array"], 1,
                   "The condition stops being monotonic."),
                _q("Many updates and one read at the end suggests…",
                   ["prefix sums", "a difference array", "a window", "a Set"], 1,
                   "Cheap writes."),
            ],
            exercises=[
                _ex("tscourse-w23-ch-1", "Pick the technique",
                    "Classify each wording by the technique it points at.",
                    _NUMS +
                    'function techniqueFor(kind: number): string {\n'
                    '  if (kind === 1) {\n'
                    '    return "fixed window";\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return "variable window";\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return "prefix sums";\n  }\n'
                    '  if (kind === 4) {\n'
                    '    return "prefix + map";\n  }\n'
                    '  return "difference array";\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} ${techniqueFor(k)}`);\n}\n',
                    '  if (kind === 4) {\n    return "prefix + map";\n  }',
                    [("1 2 3 4 5",
                      "1 fixed window\n2 variable window\n3 prefix sums\n4 prefix + map\n5 difference array")],
                    hints=["Kind 4 is counting subarrays, which needs the Map.",
                           'Write if (kind === 4) { return "prefix + map"; }'],
                    difficulty="Easy"),
                _ex("tscourse-w23-ch-2", "The monotonicity question",
                    "Report whether a sliding window is safe, which depends on there being no negative value.",
                    _NUMS +
                    'let hasNegative = false;\n'
                    'for (const n of nums) {\n'
                    '  if (n < 0) {\n'
                    '    hasNegative = true;\n  }\n}\n'
                    'console.log(hasNegative ? "prefix + map" : "window");\n',
                    'console.log(hasNegative ? "prefix + map" : "window");',
                    [("1 2 3", "window"), ("1 -2 3", "prefix + map")],
                    hints=["A single negative value rules the window out.",
                           'Write console.log(hasNegative ? "prefix + map" : "window");'],
                    difficulty="Easy"),
                _ex("tscourse-w23-ch-3", "Reads or writes",
                    "Choose between prefix sums and a difference array from which operation repeats.",
                    _NUMS +
                    'const reads = nums[0] ?? 0;\n'
                    'const writes = nums[1] ?? 0;\n'
                    'console.log(reads >= writes ? "prefix sums" : "difference array");\n',
                    'console.log(reads >= writes ? "prefix sums" : "difference array");',
                    [("100 5", "prefix sums"), ("5 100", "difference array")],
                    hints=["Whichever operation dominates decides.",
                           'Write console.log(reads >= writes ? "prefix sums" : "difference array");'],
                    difficulty="Easy"),
                _ex("tscourse-w23-ch-4", "The space each one costs",
                    "Report the auxiliary space of each technique, in the notation of week 21.",
                    'const costs = [\n'
                    '  "window: O(1)",\n'
                    '  "window with counts: O(k)",\n'
                    '  "prefix sums: O(n)",\n'
                    '  "prefix + map: O(n)",\n'
                    '  "difference array: O(n)",\n'
                    '];\n'
                    'for (const c of costs) {\n'
                    '  console.log(c);\n}\n',
                    'for (const c of costs) {',
                    [("", "window: O(1)\nwindow with counts: O(k)\nprefix sums: O(n)\nprefix + map: O(n)\ndifference array: O(n)")],
                    hints=["Print each on its own line.",
                           "Write for (const c of costs) {"],
                    difficulty="Easy"),
                _ex("tscourse-w23-ch-5", "Two techniques, one answer",
                    "Solve the same fixed-window question both ways and confirm they agree.",
                    _NUMS + _PREFIX +
                    'const k = 2;\n'
                    'const prefix = prefixOf(nums);\n'
                    'let viaPrefix = 0;\n'
                    'for (let i = 0; i + k <= nums.length; i = i + 1) {\n'
                    '  viaPrefix = Math.max(viaPrefix, (prefix[i + k] ?? 0) - (prefix[i] ?? 0));\n}\n'
                    'let sum = 0;\n'
                    'for (let i = 0; i < k; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0);\n}\n'
                    'let viaWindow = sum;\n'
                    'for (let i = k; i < nums.length; i = i + 1) {\n'
                    '  sum = sum + (nums[i] ?? 0) - (nums[i - k] ?? 0);\n'
                    '  viaWindow = Math.max(viaWindow, sum);\n}\n'
                    'console.log(`${viaPrefix} ${viaWindow} agree=${viaPrefix === viaWindow}`);\n',
                    '  viaPrefix = Math.max(viaPrefix, (prefix[i + k] ?? 0) - (prefix[i] ?? 0));',
                    [("1 4 2 10", "12 12 agree=true"), ("3 3 3", "6 6 agree=true")],
                    hints=["A k-window starting at i is the prefix range [i, i + k - 1] — which is prefix[i + k] - prefix[i].",
                           "Write viaPrefix = Math.max(viaPrefix, (prefix[i + k] ?? 0) - (prefix[i] ?? 0));"],
                    difficulty="Hard"),
                _fix("tscourse-w23-ch-fix1", "Fix the window used on negative data",
                     "The shrink loop assumes that removing an element always reduces the total, which a "
                     "negative value breaks. On `[5, -5, 1]` with a budget of 1 it reports **2**, and the "
                     "answer is **3** — the whole array totals 1, so it qualifies, but the window threw the "
                     "leading 5 away before the -5 could pay for it. With negatives there is no monotonicity "
                     "to exploit, so every range has to be considered.\n\n"
                     "*(Finding an input that breaks it takes care: on `[1, -2, 3]` the window happens to "
                     "get the right answer, which is exactly what makes this bug dangerous.)*",
                     _NUMS +
                     'const budget = 1;\n'
                     'let start = 0;\n'
                     'let sum = 0;\n'
                     'let best = 0;\n'
                     'for (let end = 0; end < nums.length; end = end + 1) {\n'
                     '  sum = sum + (nums[end] ?? 0);\n'
                     '  while (sum > budget && start <= end) {\n'
                     '    sum = sum - (nums[start] ?? 0);\n'
                     '    start = start + 1;\n  }\n'
                     '  best = Math.max(best, end - start + 1);\n}\n'
                     'console.log(best);\n',
                     _NUMS + _PREFIX +
                     'const budget = 1;\n'
                     'const prefix = prefixOf(nums);\n'
                     'let best = 0;\n'
                     'for (let lo = 0; lo < nums.length; lo = lo + 1) {\n'
                     '  for (let hi = lo; hi < nums.length; hi = hi + 1) {\n'
                     '    const total = (prefix[hi + 1] ?? 0) - (prefix[lo] ?? 0);\n'
                     '    if (total <= budget) {\n'
                     '      best = Math.max(best, hi - lo + 1);\n    }\n  }\n}\n'
                     'console.log(best);\n',
                     [("5 -5 1", "3"), ("1 1 1", "1")],
                     hints=["The window's correctness depends on growing it never reducing the total.",
                            "With negatives there is no monotonicity to exploit, so every range has to be considered.",
                            "A prefix-sum table makes each of those ranges an O(1) subtraction — O(n²) overall, and correct."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("The skill this week teaches is…",
                   ["the implementations", "reading a question and knowing which of the five it is",
                    "counting", "the Map"], 1,
                   "All five are short once chosen."),
                _q("If the answer is not about a contiguous stretch…",
                   ["use a window", "none of these apply — sort it, or use a Map", "use prefix sums",
                    "use a difference array"], 1,
                   "The first question to ask."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #23 — the ledger analytics report",
        """
Four questions about one ledger, each answered with the right technique from this
week, and each printing the operations it cost.

Input: the daily amounts on the first line, then `k budget target` on the second.

```
3 1 4 1 5 9 2 6
3 10 10
```

```
Total:     31  ops 8
Best 3:    17  ops 13
Longest:    4  ops 14
Exactly:    1  ops 8
```

**The four answers:**

1. **Total** — the whole ledger, from the prefix-sum table. `ops` is the number of
   pushes the table cost to build (n), and it is the one build every later answer
   reuses.
2. **Best k** — the largest total of any `k` consecutive days, by **sliding
   window**: `k` operations to seed plus 2 per step.
3. **Longest** — the longest run whose total stays within `budget`, by **variable
   window**: one operation per element entering, plus one per element leaving.
4. **Exactly** — how many contiguous stretches total exactly `target`, by
   **prefix sums plus a Map**: one operation per element.

**What makes it a rep:**

* **Four techniques, one program**, each chosen for its question rather than
  applied uniformly — which is lesson 7's point made executable.
* **Every count is measured**, not calculated from a formula. The whole month's
  habit.
* **The boundaries are all reachable from the tests:** a `k` larger than the
  ledger (no window exists, so `Best k` is 0 with 0 ops), a budget smaller than
  every single day (`Longest` is 0), and a target no stretch reaches (`Exactly` is
  0 — and the Map still has to be seeded with the empty prefix or the answer is
  wrong whenever a stretch *does* start at day one).

Column format: the label padded to 10, the number padded to 3, then `  ops N`.

Empty input, or a missing second line, prints all four lines with zeros.
""",
        _ch("tscourse-w23-capstone", "Interview rep #23", "Hard",
            "Answer four questions about one ledger with four different techniques, each "
            "reporting the operations it cost.",
            _FS +
            'const lines = fs.readFileSync(0, "utf8").split("\\n");\n'
            'const xs: readonly number[] = (lines[0] ?? "")\n'
            '  .trim()\n'
            '  .split(/\\s+/)\n'
            '  .filter((s) => s !== "")\n'
            '  .map(Number);\n'
            'const params: readonly number[] = (lines[1] ?? "")\n'
            '  .trim()\n'
            '  .split(/\\s+/)\n'
            '  .filter((s) => s !== "")\n'
            '  .map(Number);\n'
            'const k = params[0] ?? 0;\n'
            'const budget = params[1] ?? 0;\n'
            'const target = params[2] ?? 0;\n'
            'function row(label: string, value: number, ops: number): string {\n'
            '  return `${(label + ":").padEnd(10)}${String(value).padStart(3)}  ops ${ops}`;\n}\n'
            'let buildOps = 0;\n'
            'const prefix: number[] = [0];\n'
            'for (const x of xs) {\n'
            '  prefix.push((prefix[prefix.length - 1] ?? 0) + x);\n'
            '  buildOps = buildOps + 1;\n}\n'
            'console.log(row("Total", prefix[prefix.length - 1] ?? 0, buildOps));\n'
            'let windowOps = 0;\n'
            'let bestK = 0;\n'
            'if (k > 0 && k <= xs.length) {\n'
            '  let sum = 0;\n'
            '  for (let i = 0; i < k; i = i + 1) {\n'
            '    sum = sum + (xs[i] ?? 0);\n'
            '    windowOps = windowOps + 1;\n  }\n'
            '  bestK = sum;\n'
            '  for (let i = k; i < xs.length; i = i + 1) {\n'
            '    sum = sum + (xs[i] ?? 0) - (xs[i - k] ?? 0);\n'
            '    windowOps = windowOps + 2;\n'
            '    bestK = Math.max(bestK, sum);\n  }\n}\n'
            'console.log(row("Best " + String(k), bestK, windowOps));\n'
            'let varOps = 0;\n'
            'let start = 0;\n'
            'let running = 0;\n'
            'let longest = 0;\n'
            'for (let end = 0; end < xs.length; end = end + 1) {\n'
            '  running = running + (xs[end] ?? 0);\n'
            '  varOps = varOps + 1;\n'
            '  while (running > budget && start <= end) {\n'
            '    running = running - (xs[start] ?? 0);\n'
            '    start = start + 1;\n'
            '    varOps = varOps + 1;\n  }\n'
            '  longest = Math.max(longest, end - start + 1);\n}\n'
            'console.log(row("Longest", longest, varOps));\n'
            'let mapOps = 0;\n'
            'const seen = new Map<number, number>();\n'
            'seen.set(0, 1);\n'
            'let total = 0;\n'
            'let exactly = 0;\n'
            'for (const x of xs) {\n'
            '  total = total + x;\n'
            '  exactly = exactly + (seen.get(total - target) ?? 0);\n'
            '  seen.set(total, (seen.get(total) ?? 0) + 1);\n'
            '  mapOps = mapOps + 1;\n}\n'
            'console.log(row("Exactly", exactly, mapOps));\n',
            'let windowOps = 0;\n'
            'let bestK = 0;\n'
            'if (k > 0 && k <= xs.length) {\n'
            '  let sum = 0;\n'
            '  for (let i = 0; i < k; i = i + 1) {\n'
            '    sum = sum + (xs[i] ?? 0);\n'
            '    windowOps = windowOps + 1;\n  }\n'
            '  bestK = sum;\n'
            '  for (let i = k; i < xs.length; i = i + 1) {\n'
            '    sum = sum + (xs[i] ?? 0) - (xs[i - k] ?? 0);\n'
            '    windowOps = windowOps + 2;\n'
            '    bestK = Math.max(bestK, sum);\n  }\n}\n'
            'console.log(row("Best " + String(k), bestK, windowOps));\n'
            'let varOps = 0;\n'
            'let start = 0;\n'
            'let running = 0;\n'
            'let longest = 0;\n'
            'for (let end = 0; end < xs.length; end = end + 1) {\n'
            '  running = running + (xs[end] ?? 0);\n'
            '  varOps = varOps + 1;\n'
            '  while (running > budget && start <= end) {\n'
            '    running = running - (xs[start] ?? 0);\n'
            '    start = start + 1;\n'
            '    varOps = varOps + 1;\n  }\n'
            '  longest = Math.max(longest, end - start + 1);\n}\n'
            'console.log(row("Longest", longest, varOps));\n'
            'let mapOps = 0;\n'
            'const seen = new Map<number, number>();\n'
            'seen.set(0, 1);\n'
            'let total = 0;\n'
            'let exactly = 0;\n'
            'for (const x of xs) {\n'
            '  total = total + x;\n'
            '  exactly = exactly + (seen.get(total - target) ?? 0);\n'
            '  seen.set(total, (seen.get(total) ?? 0) + 1);\n'
            '  mapOps = mapOps + 1;\n}\n'
            'console.log(row("Exactly", exactly, mapOps));',
            [("3 1 4 1 5 9 2 6\n3 10 10", "Total:     31  ops 8\nBest 3:    17  ops 13\nLongest:    4  ops 14\nExactly:    1  ops 8"),
             ("1 2 3\n2 3 3", "Total:      6  ops 3\nBest 2:     5  ops 4\nLongest:    2  ops 5\nExactly:    2  ops 3"),
             ("5 5\n9 1 5", "Total:     10  ops 2\nBest 9:     0  ops 0\nLongest:    0  ops 4\nExactly:    2  ops 2"),
             ("", "Total:      0  ops 0\nBest 0:     0  ops 0\nLongest:    0  ops 0\nExactly:    0  ops 0")],
            hints=["Build the prefix table once; the Total line reports what that build cost.",
                   "The fixed window costs k to seed and 2 per slide — count those separately, not with a formula.",
                   "The variable window counts one op per element entering and one per element leaving, so its total is a measurement of the amortisation.",
                   "`seen.set(0, 1)` is required, and the third test is what catches its absence.",
                   "A `k` larger than the ledger means no window exists: report 0 with 0 ops rather than guessing.",
                   "The label for the second row includes k itself, so build it with string concatenation before padding."]),
        example_io="Total:     31  ops 8\nBest 3:    17  ops 13\nLongest:    4  ops 14\nExactly:    1  ops 8",
        rubric=["four techniques, each chosen for its own question rather than applied uniformly",
                "every operation count is measured as the algorithm runs, never computed from a formula",
                "the prefix table is built once and the Total line reports that build",
                "the fixed window seeds with k operations and slides with two",
                "the subarray-count Map is seeded with the empty prefix",
                "a k larger than the ledger reports zero with zero operations",
                "no index access is asserted with `!`",
                "empty input prints all four rows with zeros"],
        stretch=_ch("tscourse-w23-capstone-stretch", "Interview rep #23 (stretch)", "Hard",
                    "Add a fifth answer using the week's last technique: apply a series of range "
                    "adjustments with a **difference array**, then report the largest adjusted day "
                    "and the writes it took. Each later input line is `lo hi amount`. Report the "
                    "difference array's write count against what element-by-element updates would "
                    "have cost, so the two appear side by side.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
                    'const xs: readonly number[] = (lines[0] ?? "")\n'
                    '  .trim()\n'
                    '  .split(/\\s+/)\n'
                    '  .filter((s) => s !== "")\n'
                    '  .map(Number);\n'
                    'const n = xs.length;\n'
                    'const diff: number[] = new Array(n + 1).fill(0);\n'
                    'let writes = 0;\n'
                    'let naive = 0;\n'
                    'for (const line of lines.slice(1)) {\n'
                    '  const parts = line.trim().split(/\\s+/).map(Number);\n'
                    '  if (parts.length !== 3) {\n'
                    '    continue;\n  }\n'
                    '  const lo = Math.max(0, parts[0] ?? 0);\n'
                    '  const hi = Math.min(n - 1, parts[1] ?? 0);\n'
                    '  const amount = parts[2] ?? 0;\n'
                    '  if (lo > hi) {\n'
                    '    continue;\n  }\n'
                    '  diff[lo] = (diff[lo] ?? 0) + amount;\n'
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;\n'
                    '  writes = writes + 2;\n'
                    '  naive = naive + (hi - lo + 1);\n}\n'
                    'let running = 0;\n'
                    'let biggest = 0;\n'
                    'for (let i = 0; i < n; i = i + 1) {\n'
                    '  running = running + (diff[i] ?? 0);\n'
                    '  biggest = Math.max(biggest, (xs[i] ?? 0) + running);\n'
                    '  writes = writes + 1;\n}\n'
                    'console.log(`Biggest:  ${String(biggest).padStart(3)}`);\n'
                    'console.log(`Writes:   ${String(writes).padStart(3)}  naive ${naive}`);\n',
                    'for (const line of lines.slice(1)) {\n'
                    '  const parts = line.trim().split(/\\s+/).map(Number);\n'
                    '  if (parts.length !== 3) {\n'
                    '    continue;\n  }\n'
                    '  const lo = Math.max(0, parts[0] ?? 0);\n'
                    '  const hi = Math.min(n - 1, parts[1] ?? 0);\n'
                    '  const amount = parts[2] ?? 0;\n'
                    '  if (lo > hi) {\n'
                    '    continue;\n  }\n'
                    '  diff[lo] = (diff[lo] ?? 0) + amount;\n'
                    '  diff[hi + 1] = (diff[hi + 1] ?? 0) - amount;\n'
                    '  writes = writes + 2;\n'
                    '  naive = naive + (hi - lo + 1);\n}',
                    [("1 1 1 1 1\n0 4 10\n1 2 5", "Biggest:   16\nWrites:     9  naive 7"),
                     ("5 5\n0 1 1", "Biggest:    6\nWrites:     4  naive 2"),
                     ("3", "Biggest:    3\nWrites:     1  naive 0")],
                    hints=["Two writes per adjustment, whatever the range's width — that is the entire point.",
                           "Clamp `lo` and `hi` into the array, and skip an adjustment whose range inverts after clamping.",
                           "The materialising pass counts as one write per day, and it happens once however many adjustments there were.",
                           "`naive` accumulates the width of each range, which is what updating element by element would have cost \u2014 and on these tiny inputs it is SMALLER, because two adjustments over five days cannot amortise the materialising pass. That is the honest result, and it is the same lesson week 21 taught: a technique's advantage is a statement about large inputs."]),
    ),
))
