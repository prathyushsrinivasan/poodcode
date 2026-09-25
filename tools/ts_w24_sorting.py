# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 24 — sorting.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# WHAT THIS WEEK INHERITS, AND THEREFORE DOES NOT RE-TEACH
#
#   week 6    `.sort` with a comparator, the text-sort trap, "sort mutates"
#   week 19   the multi-key comparator `b[1] - a[1] || a[0].localeCompare(b[0])`
#   week 20   recursion, on trees — merge sort and quicksort are its next use
#   week 21   counting operations instead of timing; best/worst case
#   week 22   THE MERGE (both tail drains, `<=` for stability) and the partition
#             by a predicate. Merge sort here splits, recurses and calls the
#             merge; it does not write it again from nothing.
#   week 23   prefix sums — which is exactly how a STABLE counting sort decides
#             where each record goes (lesson 4 says so)
#
# So the week opens on how the sorts work rather than on whether to sort, and
# its last lesson is a choosing table, the same shape as week 23's.
#
# ---------------------------------------------------------------------------
# THE MONTH'S IDIOM: every algorithm reports its comparisons. The sizes are
# chosen so the counts are checkable by hand:
#
#   selection sort, n=8, any input               28 = 8·7/2   (it cannot tell)
#   insertion sort, n=8, sorted / reversed        7 / 28      (it can)
#   merge sort, n=8/16/32, sorted                12 / 32 / 80
#   merge sort, n=8, worst case [1,5,3,7,2,6,4,8]   17
#   quicksort (last-element pivot), n=16, sorted  120         (the worst case)
#   the comparison lower bound ceil(log2 n!)      5 / 16 / 45  for n = 4 / 8 / 16
#
# Nothing measures elapsed time (week 17's rule, extended by week 21).
#
# ---------------------------------------------------------------------------
# TWO RUNTIME FACTS THE WEEK IS BUILT ON, both verified against the judge's Node:
#
#   1. A comparator that never returns a NEGATIVE number — `a > b ? 1 : 0` —
#      type-checks and does not sort at all: `[3, 1, 2]` comes back `3,1,2`.
#      The engine only moves an element when told it belongs EARLIER. That is a
#      runnable `fix`, and far better than a lecture on the comparator contract.
#   2. A comparator returning a BOOLEAN — `(a, b) => a > b` — is TS2345, because
#      `sort`'s parameter is `(a: T, b: T) => number`. At run time the same
#      program also leaves `[3, 1, 2]` untouched, which the lesson mentions so the
#      compile error reads as a rescue rather than a pedantry.
#
# `readonly number[]` has no `.sort` (TS2339) — the type system's version of
# week 6's "sort mutates" warning — and `toSorted` is the non-mutating answer.
# It is gated at 24 in `_SCOPE_RULES`, verified absent from weeks 1-23.
#
# Quicksort's instability is shown on ONE concrete input, because stability is a
# guarantee and instability can only ever be exhibited: on `ann 2, bo 1, cy 2,
# dee 1` the last-element-pivot partition puts `dee` before `bo`.
# ---------------------------------------------------------------------------

_SWAP = (
    'function swap(xs: number[], i: number, j: number): void {\n'
    '  const t = xs[i] ?? 0;\n'
    '  xs[i] = xs[j] ?? 0;\n'
    '  xs[j] = t;\n}\n'
)

_UPDOWN = (
    'const up = Array.from({ length: 8 }, (_, i) => i + 1);\n'
    'const down = Array.from({ length: 8 }, (_, i) => 8 - i);\n'
)

# Merge sort with a comparison counter. The merge is week 22's, verbatim apart
# from the counter.
_MERGE = (
    'let cmp = 0;\n'
    'function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
    '  const out: number[] = [];\n'
    '  let i = 0;\n'
    '  let j = 0;\n'
    '  while (i < a.length && j < b.length) {\n'
    '    cmp = cmp + 1;\n'
    '    if ((a[i] ?? 0) <= (b[j] ?? 0)) {\n'
    '      out.push(a[i] ?? 0);\n'
    '      i = i + 1;\n'
    '    } else {\n'
    '      out.push(b[j] ?? 0);\n'
    '      j = j + 1;\n    }\n  }\n'
    '  while (i < a.length) {\n'
    '    out.push(a[i] ?? 0);\n'
    '    i = i + 1;\n  }\n'
    '  while (j < b.length) {\n'
    '    out.push(b[j] ?? 0);\n'
    '    j = j + 1;\n  }\n'
    '  return out;\n}\n'
)
_MSORT = (
    'function mergeSort(xs: readonly number[]): readonly number[] {\n'
    '  if (xs.length <= 1) {\n'
    '    return xs;\n  }\n'
    '  const mid = Math.floor(xs.length / 2);\n'
    '  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));\n}\n'
)

# Quicksort, Lomuto partition, last element as the pivot, with a counter.
_PART = (
    'let cmp = 0;\n'
    'function partition(xs: number[], lo: number, hi: number): number {\n'
    '  const pivot = xs[hi] ?? 0;\n'
    '  let i = lo;\n'
    '  for (let j = lo; j < hi; j = j + 1) {\n'
    '    cmp = cmp + 1;\n'
    '    if ((xs[j] ?? 0) < pivot) {\n'
    '      swap(xs, i, j);\n'
    '      i = i + 1;\n    }\n  }\n'
    '  swap(xs, i, hi);\n'
    '  return i;\n}\n'
)
_QUICK = (
    'function quick(xs: number[], lo: number, hi: number): void {\n'
    '  if (lo >= hi) {\n'
    '    return;\n  }\n'
    '  const p = partition(xs, lo, hi);\n'
    '  quick(xs, lo, p - 1);\n'
    '  quick(xs, p + 1, hi);\n}\n'
)

# Records for the stability lessons: `name:score` words on one line.
_ROWS = (
    'interface Row {\n'
    '  readonly name: string;\n'
    '  readonly score: number;\n}\n'
    'const rows: readonly Row[] = words.map((w) => {\n'
    '  const [name, score] = w.split(":");\n'
    '  return { name: name ?? "", score: Number(score ?? "0") };\n});\n'
    'function at(rs: readonly Row[], i: number): Row {\n'
    '  return rs[i] ?? { name: "", score: 0 };\n}\n'
)

# Counting sort over 0..max.
_COUNTING = (
    'function countingSort(xs: readonly number[]): readonly number[] {\n'
    '  const max = Math.max(...xs);\n'
    '  const counts: number[] = new Array(max + 1).fill(0);\n'
    '  for (const x of xs) {\n'
    '    counts[x] = (counts[x] ?? 0) + 1;\n  }\n'
    '  const out: number[] = [];\n'
    '  for (let v = 0; v <= max; v = v + 1) {\n'
    '    for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
    '      out.push(v);\n    }\n  }\n'
    '  return out;\n}\n'
)


# --- Week 24 --------------------------------------------------------------
_WEEKS.append(_week(
    24, 6, _M6,
    "Sorting",
    "How the sorts actually work — and what each one costs, counted — so that the built-in stops being magic and sorting becomes a tool you reach for on purpose.",
    """
You have called `.sort` since week 6. This week opens it up.

## Why learn algorithms you will not write

Because every one of them is a lesson in something else:

| sort | what it actually teaches |
|---|---|
| selection | an algorithm whose cost **ignores** its input |
| insertion | one whose cost **depends** on it — best and worst case, made visible |
| merge | divide and conquer, and where the `log n` comes from |
| quick | partitioning, pivots, and an average case that is not the worst case |
| counting | that `n log n` is a limit on **comparing**, not on sorting |

And one practical reason: interviewers ask. Not usually "write quicksort", but
"why is the built-in stable", "what is the worst case", "can you do better than
`n log n` here" — questions you can only answer if you have taken one apart.

## Counted, as always this month

Every algorithm this week prints its **comparisons**. On eight elements,
already sorted:

```
selection  cmp 28
insertion  cmp  7
merge      cmp 12
quick      cmp 28     ← the last-element pivot's worst case
```

Four sorts, one input, four very different stories — and the numbers tell them.

## What you already own

Week 22 wrote **the merge** (both tail drains, `<=` for stability) and **the
partition** (keep the ones that pass). Merge sort is that merge plus recursion;
quicksort is that partition plus recursion. Week 20 taught the recursion. You are
assembling, not starting over.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Write selection and insertion sort, and count what each compares",
        "Say why selection sort's cost ignores the input and insertion sort's does not",
        "Write merge sort by splitting, recursing and calling week 22's merge",
        "Say where merge sort's log n comes from, and what it costs in space",
        "Partition around a pivot, and write quicksort on top of it",
        "Show quicksort's worst case with a count, and remove it with a better pivot",
        "Sort without comparing, with counting sort, and say when that is allowed",
        "State the n log n lower bound and what it applies to",
        "Write a comparator that obeys the contract, and sort by several keys",
        "Say what 'stable' means, which sorts are, and rely on it",
        "Sort without mutating, with a copy or `toSorted`",
        "Use sorting to make a question easy: neighbours, groups, medians, clashes",
        "Choose a sort from the shape of the data",
    ],
    why="Sorting is the most reused idea in algorithms: half the problems in the next month start with 'sort it first'. Knowing how the sorts work is what lets you answer the questions interviewers really ask about them — stability, worst cases, and when n log n can be beaten — and it is the cleanest place in the course to see divide-and-conquer.",
    est_minutes=480,
    glossary=[
        _gloss("comparison sort", "A sort that learns the order only by comparing two elements at a time."),
        _gloss("selection sort", "Repeatedly select the smallest remaining element. Always n(n-1)/2 comparisons."),
        _gloss("insertion sort", "Insert each element into the sorted prefix before it. n-1 comparisons on sorted input."),
        _gloss("adaptive", "Cheaper on input that is already nearly in order. Insertion sort is; selection is not."),
        _gloss("merge sort", "Split in half, sort each half recursively, merge. O(n log n) always, O(n) extra space."),
        _gloss("divide and conquer", "Split a problem into smaller copies of itself, solve those, combine."),
        _gloss("quicksort", "Partition around a pivot, then sort each side. O(n log n) on average, O(n²) worst."),
        _gloss("pivot", "The element a partition compares everything else against."),
        _gloss("partition", "Rearrange so everything before the pivot is smaller and everything after is not."),
        _gloss("quickselect", "Partition, then recurse into only the side that holds the k-th element. O(n) on average."),
        _gloss("counting sort", "Tally each value, then emit the tallies in order. O(n + k), no comparisons."),
        _gloss("lower bound", "No comparison sort can beat ceil(log2 n!) comparisons in the worst case — about n log n."),
        _gloss("stable", "Equal elements keep their original relative order."),
        _gloss("in place", "Sorts inside the array it was given, using O(1) or O(log n) extra space."),
        _gloss("comparator", "(a, b) => negative if a comes first, positive if b does, 0 if either will do."),
        _gloss("toSorted", "The non-mutating sort: returns a sorted copy and leaves the original alone."),
    ],
    cheatsheet="""
```ts
// ---- insertion sort: shift the bigger ones right, drop v in the gap -------
for (let i = 1; i < xs.length; i = i + 1) {
  const v = xs[i] ?? 0;                           // SAVE it — the shift overwrites xs[i]
  let j = i - 1;
  while (j >= 0 && (xs[j] ?? 0) > v) {
    xs[j + 1] = xs[j] ?? 0;
    j = j - 1;
  }
  xs[j + 1] = v;
}
// sorted input: n - 1 comparisons. reversed: n(n-1)/2.

// ---- merge sort: split, recurse, merge (week 22's merge) ---------------
function mergeSort(xs: readonly number[]): readonly number[] {
  if (xs.length <= 1) { return xs; }              // <= 1, never === 0
  const mid = Math.floor(xs.length / 2);
  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));
}
// O(n log n) always. O(n) extra space. Stable, because the merge uses <=.

// ---- quicksort: Lomuto partition, last element as pivot ---------------
function partition(xs: number[], lo: number, hi: number): number {
  const pivot = xs[hi] ?? 0;
  let i = lo;                                      // next slot for a "smaller"
  for (let j = lo; j < hi; j = j + 1) {
    if ((xs[j] ?? 0) < pivot) { swap(xs, i, j); i = i + 1; }
  }
  swap(xs, i, hi);                                 // pivot to its final place
  return i;
}
function quick(xs: number[], lo: number, hi: number): void {
  if (lo >= hi) { return; }
  const p = partition(xs, lo, hi);
  quick(xs, lo, p - 1);                            // p - 1, NOT p: the pivot is done
  quick(xs, p + 1, hi);
}
// average O(n log n); sorted input with a last-element pivot is O(n²).
// swap(xs, Math.floor((lo + hi) / 2), hi) first — a middle pivot — fixes that case.

// ---- counting sort: small integer range, no comparisons ---------------
const counts: number[] = new Array(max + 1).fill(0);
for (const x of xs) { counts[x] = (counts[x] ?? 0) + 1; }
for (let v = 0; v <= max; v = v + 1) { /* emit v, counts[v] times */ }
// O(n + k). Negative values: index by x - min.

// ---- the built-in, properly -------------------------------------------
[...xs].sort((a, b) => a - b);                     // ascending; copy first
xs.toSorted((a, b) => b - a);                      // descending, no mutation
rows.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));
// negative: a first · positive: b first · 0: either. NEVER a boolean.
// Stable since ES2019 — so sorting by name, THEN by score, orders ties by name.
```

| | best | average | worst | extra space | stable |
|---|---|---|---|---|---|
| selection | n² | n² | n² | 1 | no |
| insertion | **n** | n² | n² | 1 | yes |
| merge | n log n | n log n | n log n | n | yes |
| quick | n log n | n log n | **n²** | log n | no |
| counting | n + k | n + k | n + k | n + k | yes |
| built-in | n | n log n | n log n | n | **yes** |
""",
    self_check=[
        "Can you write insertion sort from memory, and say why `v` must be saved?",
        "Can you say why selection sort does 28 comparisons on any 8 elements?",
        "Can you say what makes insertion sort cheap on nearly sorted input?",
        "Can you write merge sort using week 22's merge?",
        "Can you say where the log n in merge sort comes from?",
        "Can you say why the base case must be `length <= 1`?",
        "Can you partition around a pivot and say what `i` means?",
        "Can you name the input that makes last-element quicksort quadratic, and fix it?",
        "Can you find the k-th smallest without sorting everything?",
        "Can you say when counting sort beats n log n, and when it is a bad idea?",
        "Can you write a comparator for two keys, one descending?",
        "Can you say what stable means and which of the five sorts are?",
        "Can you sort without disturbing the original array?",
        "Can you turn 'closest pair' or 'any clash?' into a sort and a sweep?",
    ],
    review=[
        _q("Selection sort on 8 elements, already sorted, compares…",
           ["7 times", "28 times", "8 times", "0 times"], 1,
           "n(n-1)/2, whatever the input. It cannot tell."),
        _q("Insertion sort on 8 already-sorted elements compares…",
           ["28 times", "7 times", "0 times", "64 times"], 1,
           "One comparison per element: each finds its place immediately."),
        _q("Insertion sort saves `v = xs[i]` before shifting because…",
           ["it is faster", "the first shift overwrites xs[i]", "of types", "it is stable"], 1,
           "Forget it and the element is lost — the output fills with copies."),
        _q("Merge sort's log n is…",
           ["the merge", "the number of times n can be halved — the depth of the recursion", "the pivot",
            "the space"], 1,
           "Each level does O(n) merging; there are log n levels."),
        _q("Merge sort's base case must be `length <= 1` because…",
           ["of speed", "a one-element array split in half gives [] and itself — for ever",
            "empty arrays are rare", "of stability"], 1,
           "`=== 0` recurses until the stack runs out."),
        _q("Merge sort is stable because…",
           ["it recurses", "the merge takes from the LEFT on a tie (`<=`)", "it copies", "it is O(n log n)"], 1,
           "Week 22's `<=`, earning its keep."),
        _q("After a Lomuto partition returns p…",
           ["recurse on [lo, p] and [p, hi]", "recurse on [lo, p-1] and [p+1, hi] — the pivot is finished",
            "stop", "recurse on [lo, hi]"], 1,
           "Including p again can recurse for ever."),
        _q("Last-element quicksort on already-sorted input is…",
           ["O(n)", "O(n²) — every partition peels off one element", "O(n log n)", "O(log n)"], 1,
           "120 comparisons on 16 elements, the same as selection sort."),
        _q("Quickselect finds the k-th smallest in…",
           ["O(n log n)", "O(n) on average — it recurses into ONE side", "O(k)", "O(1)"], 1,
           "It is quicksort that throws half the work away."),
        _q("Counting sort beats n log n because…",
           ["it is clever", "it never compares — the lower bound only applies to comparison sorts",
            "it is in place", "it is stable"], 1,
           "It uses the values as addresses instead."),
        _q("A comparator returns…",
           ["true if a comes first", "negative if a comes first, positive if b does, 0 for a tie",
            "a or b", "the larger"], 1,
           "A boolean is TS2345, and at run time it does not sort."),
        _q("`(a, b) => a > b ? 1 : 0` as a comparator…",
           ["sorts ascending", "type-checks and does not sort — it never says 'a comes first'",
            "sorts descending", "throws"], 1,
           "The engine only moves an element when the answer is negative."),
        _q("The built-in `sort` is…",
           ["unstable", "stable, guaranteed since ES2019", "stable for numbers only", "stable in Chrome only"], 1,
           "Which is why sorting by two keys in two passes works."),
        _q("`readonly number[]` has no `.sort` because…",
           ["of a bug", "sort mutates, and the type promised not to", "it is slow", "it is generic"], 1,
           "Copy it, or use `toSorted`."),
        _q("\"Is any pair closer than 5?\" after sorting needs…",
           ["every pair", "only adjacent pairs", "a Map", "binary search"], 1,
           "The closest pair in sorted order are neighbours."),
    ],
    milestone="Interview rep #24 — the sort bench. One input, five sorts written by hand — insertion, selection, merge, quick and counting — each checked against the built-in and each reporting what it cost. The bench names the cheapest, and the tests are chosen so that each sort takes a turn at looking good and at looking bad.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w24-simple", "The two sorts you could invent",
            "Selection and insertion — and why one of them notices sorted input.",
            """
Ask someone to sort a hand of cards and they will do one of two things.

## Selection sort — find the smallest, put it first, repeat

```ts
for (let i = 0; i < xs.length - 1; i = i + 1) {
  let min = i;
  for (let j = i + 1; j < xs.length; j = j + 1) {
    if ((xs[j] ?? 0) < (xs[min] ?? 0)) { min = j; }
  }
  swap(xs, i, min);
}
```

`swap` needs the usual care under `noUncheckedIndexedAccess`: read both slots
with a `?? 0`, then write.

The comparisons are `(n-1) + (n-2) + … + 1` = **n(n-1)/2** — 28 for eight
elements. And that is true of *any* eight elements, sorted, reversed or shuffled:
the inner loop always scans the whole remainder, because it cannot know the
smallest is already in front until it has looked at everything. **Its cost ignores
its input.**

## Insertion sort — take the next card, slide it into place

```ts
for (let i = 1; i < xs.length; i = i + 1) {
  const v = xs[i] ?? 0;                     // save it FIRST
  let j = i - 1;
  while (j >= 0 && (xs[j] ?? 0) > v) {
    xs[j + 1] = xs[j] ?? 0;                 // shift the bigger one right
    j = j - 1;
  }
  xs[j + 1] = v;                            // drop it into the gap
}
```

Everything left of `i` is sorted; each step extends that sorted prefix by one.

Now count:

```
already sorted:  cmp  7      each element finds its place at once
reversed:        cmp 28      each element travels all the way to the front
```

**Its cost depends on its input.** That is week 21's best case and worst case,
and here they are as two numbers from the same code. The word for this is
**adaptive**, and it is why insertion sort is not a toy: real library sorts switch
to it for short runs and nearly-ordered data, where it beats anything cleverer.

## The saved `v`

The first shift writes `xs[i] = xs[i - 1]`, so if you read `xs[i]` *after* the
loop starts, the element you were inserting is gone. Saving it is not tidiness —
it is the algorithm.

## And bubble sort?

Swap adjacent pairs until nothing moves. It is also O(n²), it is adaptive only
with an extra flag, and it does more writes than either of these. It is famous for
being taught, not for being used — you can skip it.

> ⚠️ **Common mistakes:** reading `xs[i]` after the shift instead of the saved
> `v`; stopping selection's inner loop one short (`j < xs.length - 1`); and
> assuming O(n²) means "always slow" — insertion sort on sorted input is linear.
""",
            warmup=[
                _q("Selection sort on 8 elements compares how many times?",
                   ["8", "28", "64", "it depends on the input"], 1,
                   "7 + 6 + … + 1, always."),
                _q("Insertion sort on already-sorted input is…",
                   ["O(n²)", "O(n)", "O(log n)", "O(n log n)"], 1,
                   "One comparison per element."),
                _q("\"Adaptive\" means…",
                   ["it uses less memory", "it is cheaper when the input is nearly sorted", "it is stable",
                    "it is recursive"], 1,
                   "Insertion is; selection is not."),
                _q("Insertion sort saves `v` before shifting because…",
                   ["style", "the first shift overwrites xs[i]", "types", "speed"], 1,
                   "Without it the element is lost."),
            ],
            exercises=[
                _ex("tscourse-w24-sl-1", "Find the smallest of the rest",
                    "Complete selection sort's inner step: remember where the smallest remaining element is.",
                    _NUMS + _SWAP +
                    'function selectionSort(xs: number[]): void {\n'
                    '  for (let i = 0; i < xs.length - 1; i = i + 1) {\n'
                    '    let min = i;\n'
                    '    for (let j = i + 1; j < xs.length; j = j + 1) {\n'
                    '      if ((xs[j] ?? 0) < (xs[min] ?? 0)) {\n'
                    '        min = j;\n      }\n    }\n'
                    '    swap(xs, i, min);\n  }\n}\n'
                    'selectionSort(nums);\n'
                    'console.log(nums.join(","));\n',
                    '      if ((xs[j] ?? 0) < (xs[min] ?? 0)) {\n'
                    '        min = j;\n      }',
                    [("5 2 4 1 3", "1,2,3,4,5"), ("2 1", "1,2"), ("7", "7")],
                    hints=["Compare each remaining element with the smallest found so far.",
                           "When it is smaller, remember its index in `min`."],
                    difficulty="Easy"),
                _ex("tscourse-w24-sl-2", "Selection sort cannot tell",
                    "Count selection sort's comparisons on sorted and on reversed input.",
                    _SWAP +
                    'let cmp = 0;\n'
                    'function selectionSort(xs: number[]): void {\n'
                    '  for (let i = 0; i < xs.length - 1; i = i + 1) {\n'
                    '    let min = i;\n'
                    '    for (let j = i + 1; j < xs.length; j = j + 1) {\n'
                    '      cmp = cmp + 1;\n'
                    '      if ((xs[j] ?? 0) < (xs[min] ?? 0)) {\n'
                    '        min = j;\n      }\n    }\n'
                    '    swap(xs, i, min);\n  }\n}\n'
                    + _UPDOWN +
                    'selectionSort(up);\n'
                    'const sortedCmp = cmp;\n'
                    'cmp = 0;\n'
                    'selectionSort(down);\n'
                    'console.log(`sorted=${sortedCmp} reversed=${cmp}`);\n',
                    '      cmp = cmp + 1;',
                    [("", "sorted=28 reversed=28")],
                    hints=["Count once per comparison — that is, once per pass of the inner loop.",
                           "Write cmp = cmp + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w24-sl-3", "Shift the bigger ones right",
                    "Complete insertion sort's inner loop.",
                    _NUMS +
                    'function insertionSort(xs: number[]): void {\n'
                    '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                    '    const v = xs[i] ?? 0;\n'
                    '    let j = i - 1;\n'
                    '    while (j >= 0 && (xs[j] ?? 0) > v) {\n'
                    '      xs[j + 1] = xs[j] ?? 0;\n'
                    '      j = j - 1;\n    }\n'
                    '    xs[j + 1] = v;\n  }\n}\n'
                    'insertionSort(nums);\n'
                    'console.log(nums.join(","));\n',
                    '    while (j >= 0 && (xs[j] ?? 0) > v) {\n'
                    '      xs[j + 1] = xs[j] ?? 0;\n'
                    '      j = j - 1;\n    }',
                    [("5 2 4 1 3", "1,2,3,4,5"), ("3 3 1", "1,3,3"), ("1", "1")],
                    hints=["Keep moving left while the element there is bigger than `v`.",
                           "Each step copies xs[j] one place right, then moves j left."],
                    difficulty="Medium"),
                _ex("tscourse-w24-sl-4", "Insertion sort can tell",
                    "Count insertion sort's comparisons on sorted and on reversed input.",
                    'let cmp = 0;\n'
                    'function greater(a: number, b: number): boolean {\n'
                    '  cmp = cmp + 1;\n'
                    '  return a > b;\n}\n'
                    'function insertionSort(xs: number[]): void {\n'
                    '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                    '    const v = xs[i] ?? 0;\n'
                    '    let j = i - 1;\n'
                    '    while (j >= 0 && greater(xs[j] ?? 0, v)) {\n'
                    '      xs[j + 1] = xs[j] ?? 0;\n'
                    '      j = j - 1;\n    }\n'
                    '    xs[j + 1] = v;\n  }\n}\n'
                    + _UPDOWN +
                    'insertionSort(up);\n'
                    'const sortedCmp = cmp;\n'
                    'cmp = 0;\n'
                    'insertionSort(down);\n'
                    'console.log(`sorted=${sortedCmp} reversed=${cmp}`);\n',
                    '    while (j >= 0 && greater(xs[j] ?? 0, v)) {',
                    [("", "sorted=7 reversed=28")],
                    hints=["Route the comparison through `greater`, so every one is counted.",
                           "`&&` short-circuits: when j is -1, nothing is compared — and nothing is counted.",
                           "Write while (j >= 0 && greater(xs[j] ?? 0, v)) {"],
                    difficulty="Medium"),
                _ex("tscourse-w24-sl-5", "Nearly sorted is nearly free",
                    "Drop the saved value into the gap, and see what one out-of-place element costs.",
                    _NUMS +
                    'let cmp = 0;\n'
                    'function greater(a: number, b: number): boolean {\n'
                    '  cmp = cmp + 1;\n'
                    '  return a > b;\n}\n'
                    'function insertionSort(xs: number[]): void {\n'
                    '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                    '    const v = xs[i] ?? 0;\n'
                    '    let j = i - 1;\n'
                    '    while (j >= 0 && greater(xs[j] ?? 0, v)) {\n'
                    '      xs[j + 1] = xs[j] ?? 0;\n'
                    '      j = j - 1;\n    }\n'
                    '    xs[j + 1] = v;\n  }\n}\n'
                    'insertionSort(nums);\n'
                    'console.log(`n=${nums.length} cmp=${cmp} ${nums.join(",")}`);\n',
                    '    xs[j + 1] = v;',
                    [("1 2 3 5 4 6 7 8", "n=8 cmp=8 1,2,3,4,5,6,7,8"),
                     ("3 2 1", "n=3 cmp=3 1,2,3")],
                    hints=["The loop stopped with j one place LEFT of the gap.",
                           "Write xs[j + 1] = v;"],
                    difficulty="Medium"),
                _fn("tscourse-w24-sl-6", "Write insertion sort",
                    "Return a sorted **copy** of `xs`, using insertion sort. Leave the argument untouched — "
                    "copy it first, then sort the copy in place.",
                    "insertionSorted", [("xs", "readonly number[]", "number[]")], "number[]",
                    'const out = [...xs];\n'
                    'for (let i = 1; i < out.length; i = i + 1) {\n'
                    '  const v = out[i] ?? 0;\n'
                    '  let j = i - 1;\n'
                    '  while (j >= 0 && (out[j] ?? 0) > v) {\n'
                    '    out[j + 1] = out[j] ?? 0;\n'
                    '    j = j - 1;\n  }\n'
                    '  out[j + 1] = v;\n}\n'
                    'return out;\n',
                    [("5 2 4 1 3", "1 2 3 4 5"), ("9 -1 9 0", "-1 0 9 9"), ("7", "7")],
                    hints=["`[...xs]` gives you a mutable copy to work on.",
                           "Save the element, shift the bigger ones right, drop it into the gap.",
                           "Return the copy."],
                    difficulty="Medium"),
                _fix("tscourse-w24-sl-fix1", "Fix the element that got overwritten",
                     "This prints `3,3,3` for `3 1 2`. The loop compares against `xs[i]` and drops `xs[i]` into the gap — but the first shift has already written over `xs[i]`, so the element being inserted is lost.",
                     _NUMS +
                     'function insertionSort(xs: number[]): void {\n'
                     '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                     '    let j = i - 1;\n'
                     '    while (j >= 0 && (xs[j] ?? 0) > (xs[i] ?? 0)) {\n'
                     '      xs[j + 1] = xs[j] ?? 0;\n'
                     '      j = j - 1;\n    }\n'
                     '    xs[j + 1] = xs[i] ?? 0;\n  }\n}\n'
                     'insertionSort(nums);\n'
                     'console.log(nums.join(","));\n',
                     _NUMS +
                     'function insertionSort(xs: number[]): void {\n'
                     '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                     '    const v = xs[i] ?? 0;\n'
                     '    let j = i - 1;\n'
                     '    while (j >= 0 && (xs[j] ?? 0) > v) {\n'
                     '      xs[j + 1] = xs[j] ?? 0;\n'
                     '      j = j - 1;\n    }\n'
                     '    xs[j + 1] = v;\n  }\n}\n'
                     'insertionSort(nums);\n'
                     'console.log(nums.join(","));\n',
                     [("3 1 2", "1,2,3"), ("5 4 3 2 1", "1,2,3,4,5")],
                     hints=["When j is i - 1, the first shift writes to xs[i].",
                            "Read the element ONCE, before the loop, into a const.",
                            "Use that saved value in both the comparison and the final write."],
                     difficulty="Medium"),
                _fix("tscourse-w24-sl-fix2", "Fix the scan that stops one short",
                     "This prints `2,3,1` for `3 2 1`: the inner loop stops at `xs.length - 1`, so the last element is never a candidate for the smallest — and a small value at the end stays there.",
                     _NUMS + _SWAP +
                     'function selectionSort(xs: number[]): void {\n'
                     '  for (let i = 0; i < xs.length - 1; i = i + 1) {\n'
                     '    let min = i;\n'
                     '    for (let j = i + 1; j < xs.length - 1; j = j + 1) {\n'
                     '      if ((xs[j] ?? 0) < (xs[min] ?? 0)) {\n'
                     '        min = j;\n      }\n    }\n'
                     '    swap(xs, i, min);\n  }\n}\n'
                     'selectionSort(nums);\n'
                     'console.log(nums.join(","));\n',
                     _NUMS + _SWAP +
                     'function selectionSort(xs: number[]): void {\n'
                     '  for (let i = 0; i < xs.length - 1; i = i + 1) {\n'
                     '    let min = i;\n'
                     '    for (let j = i + 1; j < xs.length; j = j + 1) {\n'
                     '      if ((xs[j] ?? 0) < (xs[min] ?? 0)) {\n'
                     '        min = j;\n      }\n    }\n'
                     '    swap(xs, i, min);\n  }\n}\n'
                     'selectionSort(nums);\n'
                     'console.log(nums.join(","));\n',
                     [("3 2 1", "1,2,3"), ("2 9 1", "1,2,9")],
                     hints=["The OUTER loop may stop one short — the last element is placed by elimination.",
                            "The INNER loop may not: it must look at every remaining element.",
                            "Write j < xs.length."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why do library sorts still use insertion sort?",
                   ["tradition", "on short or nearly sorted runs it beats cleverer sorts", "it is stable only",
                    "they do not"], 1,
                   "Adaptive and tiny constant factors."),
                _q("Selection sort's OUTER loop may stop at `length - 1` because…",
                   ["of speed", "the last element is in place once all the others are", "of types",
                    "it cannot"], 1,
                   "Its inner loop has no such excuse."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w24-merge", "Merge sort",
            "Split, recurse, and call the merge you wrote in week 22.",
            """
Week 22 merged two sorted arrays in one pass. Merge sort is the observation that
**an array of one element is already sorted** — so split until you have those, and
merge your way back up.

```ts
function mergeSort(xs: readonly number[]): readonly number[] {
  if (xs.length <= 1) { return xs; }                    // already sorted
  const mid = Math.floor(xs.length / 2);
  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));
}
```

Three lines of new code. The merge is week 22's, word for word.

## Where the log n comes from

```
[5 2 4 1 3 8 7 6]                 one array of 8
[5 2 4 1]   [3 8 7 6]             two of 4
[5 2] [4 1] [3 8] [7 6]           four of 2
[5][2][4][1][3][8][7][6]          eight of 1      ← log2 8 = 3 splits
```

Each *level* merges all n elements once, so each level costs O(n). And there are
**log n levels**, because that is how many times n can be halved. **n per level ×
log n levels = O(n log n)** — the whole analysis, and it holds for every input:
merge sort has no bad case.

## The counts

Sorted input, where every merge finishes one side early:

```
n=8   cmp=12      n log n = 24
n=16  cmp=32      n log n = 64
n=32  cmp=80      n log n = 160
```

Double n and the count goes up by a bit more than double — the signature of
n log n, between week 21's linear and quadratic rows. The **worst** case, where
every merge has to interleave to the very end, is `[1, 5, 3, 7, 2, 6, 4, 8]`: 17
comparisons, against 28 for insertion sort's worst.

## The base case is `<= 1`, and nothing else will do

Write `=== 0` and a one-element array splits into `[]` and **itself**, which
splits into `[]` and itself, until the stack runs out — week 20's `RangeError`. A
recursion must make the problem *strictly smaller* on every call, and splitting one
element does not.

## The costs merge sort does not hide

* **O(n) extra space.** Every merge builds a new array. Quicksort, next lesson,
  sorts in place; this is what you trade for merge sort's guarantee.
* **Stable** — because week 22's merge takes from the left on a tie (`<=`). Sort
  records by score, and two with the same score come out in the order they went
  in. Change `<=` to `<` and that silently stops being true.

> ⚠️ **Common mistakes:** a base case of `=== 0`; `<` in the merge, losing
> stability; and splitting at `mid + 1` or `mid - 1`, which leaves one side empty.
""",
            warmup=[
                _q("Merge sort's depth of recursion is about…",
                   ["n", "log n", "n²", "1"], 1,
                   "How many times n can be halved."),
                _q("Each level of merge sort costs…",
                   ["O(1)", "O(n) — every element is merged once", "O(log n)", "O(n²)"], 1,
                   "n per level × log n levels."),
                _q("Merge sort's worst case is…",
                   ["O(n²)", "O(n log n) — it has no bad input", "O(n)", "O(log n)"], 1,
                   "Its guarantee, paid for with space."),
                _q("Merge sort's extra space is…",
                   ["O(1)", "O(n)", "O(log n)", "O(n²)"], 1,
                   "Every merge builds a new array."),
            ],
            exercises=[
                _ex("tscourse-w24-ms-1", "The case that stops the recursion",
                    "An array of zero or one elements is already sorted. Say so.",
                    _NUMS + _MERGE + _MSORT +
                    'console.log(mergeSort(nums).join(","));\n',
                    '  if (xs.length <= 1) {\n'
                    '    return xs;\n  }',
                    [("5 2 4 1 3", "1,2,3,4,5"), ("8", "8"), ("2 1", "1,2")],
                    hints=["Return the array unchanged when there is nothing to sort.",
                           "`<= 1`, not `=== 0` — a single element must stop the recursion too."],
                    difficulty="Easy"),
                _ex("tscourse-w24-ms-2", "Split in the middle",
                    "Choose the split point so both halves are non-empty.",
                    _NUMS + _MERGE +
                    'function mergeSort(xs: readonly number[]): readonly number[] {\n'
                    '  if (xs.length <= 1) {\n'
                    '    return xs;\n  }\n'
                    '  const mid = Math.floor(xs.length / 2);\n'
                    '  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));\n}\n'
                    'console.log(mergeSort(nums).join(","));\n',
                    '  const mid = Math.floor(xs.length / 2);',
                    [("4 3 2 1", "1,2,3,4"), ("9 7 8", "7,8,9")],
                    hints=["Half the length, rounded down.",
                           "Write const mid = Math.floor(xs.length / 2);"],
                    difficulty="Easy"),
                _ex("tscourse-w24-ms-3", "Sort both halves, then merge them",
                    "The recursive step: the whole algorithm in one line.",
                    _NUMS + _MERGE +
                    'function mergeSort(xs: readonly number[]): readonly number[] {\n'
                    '  if (xs.length <= 1) {\n'
                    '    return xs;\n  }\n'
                    '  const mid = Math.floor(xs.length / 2);\n'
                    '  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));\n}\n'
                    'console.log(mergeSort(nums).join(","));\n',
                    '  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));',
                    [("9 7 8", "7,8,9"), ("2 2 1", "1,2,2"), ("6 5 4 3 2 1", "1,2,3,4,5,6")],
                    hints=["`xs.slice(0, mid)` and `xs.slice(mid)` are the halves.",
                           "Sort each recursively, and merge the results."],
                    difficulty="Medium"),
                _ex("tscourse-w24-ms-4", "n log n, counted",
                    "Put merge sort's count beside n log n at three sizes.",
                    _MERGE + _MSORT +
                    'for (const n of [8, 16, 32]) {\n'
                    '  cmp = 0;\n'
                    '  mergeSort(Array.from({ length: n }, (_, i) => i + 1));\n'
                    '  const nlogn = n * Math.log2(n);\n'
                    '  console.log(`n=${n} cmp=${cmp} nlogn=${nlogn}`);\n}\n',
                    '  const nlogn = n * Math.log2(n);',
                    [("", "n=8 cmp=12 nlogn=24\nn=16 cmp=32 nlogn=64\nn=32 cmp=80 nlogn=160")],
                    hints=["`Math.log2` gives the number of halvings.",
                           "Write const nlogn = n * Math.log2(n);"],
                    difficulty="Easy"),
                _ex("tscourse-w24-ms-5", "The worst case, and it is still fine",
                    "Count one comparison per step of the merge's main loop, and try the input that interleaves every merge.",
                    _NUMS +
                    'let cmp = 0;\n'
                    'function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
                    '  const out: number[] = [];\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
                    '    cmp = cmp + 1;\n'
                    '    if ((a[i] ?? 0) <= (b[j] ?? 0)) {\n'
                    '      out.push(a[i] ?? 0);\n'
                    '      i = i + 1;\n'
                    '    } else {\n'
                    '      out.push(b[j] ?? 0);\n'
                    '      j = j + 1;\n    }\n  }\n'
                    '  return [...out, ...a.slice(i), ...b.slice(j)];\n}\n'
                    + _MSORT +
                    'mergeSort(nums);\n'
                    'console.log(cmp);\n',
                    '    cmp = cmp + 1;',
                    [("1 5 3 7 2 6 4 8", "17"), ("1 2 3 4 5 6 7 8", "12"), ("8 7 6 5 4 3 2 1", "12")],
                    hints=["One comparison happens per pass of the main `while` loop.",
                           "The drains compare nothing — here they are one line, `...a.slice(i), ...b.slice(j)`, and only one of the two is ever non-empty.",
                           "Write cmp = cmp + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w24-ms-6", "Stable, because of one character",
                    "Merge records by score so that equal scores keep their input order.",
                    _WORDS + _ROWS +
                    'function mergeRows(a: readonly Row[], b: readonly Row[]): readonly Row[] {\n'
                    '  const out: Row[] = [];\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
                    '    if (at(a, i).score <= at(b, j).score) {\n'
                    '      out.push(at(a, i));\n'
                    '      i = i + 1;\n'
                    '    } else {\n'
                    '      out.push(at(b, j));\n'
                    '      j = j + 1;\n    }\n  }\n'
                    '  return [...out, ...a.slice(i), ...b.slice(j)];\n}\n'
                    'function sortRows(rs: readonly Row[]): readonly Row[] {\n'
                    '  if (rs.length <= 1) {\n'
                    '    return rs;\n  }\n'
                    '  const mid = Math.floor(rs.length / 2);\n'
                    '  return mergeRows(sortRows(rs.slice(0, mid)), sortRows(rs.slice(mid)));\n}\n'
                    'console.log(sortRows(rows).map((r) => r.name).join(" "));\n',
                    '    if (at(a, i).score <= at(b, j).score) {',
                    [("ann:2 bo:1 cy:2 dee:1", "bo dee ann cy"), ("x:1 y:1 z:1", "x y z")],
                    hints=["On a tie, take from the LEFT half — it came first in the input.",
                           "Write if (at(a, i).score <= at(b, j).score) {"],
                    difficulty="Medium"),
                _fix("tscourse-w24-ms-fix1", "Fix the merge that lost stability",
                     "This prints `dee bo cy ann` for `ann:2 bo:1 cy:2 dee:1`. The scores are in order — but `bo` came before `dee` in the input and now comes after, because on a tie the merge takes from the RIGHT half. Nothing crashes and every score is in order, which is exactly why this bug survives.",
                     _WORDS + _ROWS +
                     'function mergeRows(a: readonly Row[], b: readonly Row[]): readonly Row[] {\n'
                     '  const out: Row[] = [];\n'
                     '  let i = 0;\n'
                     '  let j = 0;\n'
                     '  while (i < a.length && j < b.length) {\n'
                     '    if (at(a, i).score < at(b, j).score) {\n'
                     '      out.push(at(a, i));\n'
                     '      i = i + 1;\n'
                     '    } else {\n'
                     '      out.push(at(b, j));\n'
                     '      j = j + 1;\n    }\n  }\n'
                     '  return [...out, ...a.slice(i), ...b.slice(j)];\n}\n'
                     'function sortRows(rs: readonly Row[]): readonly Row[] {\n'
                     '  if (rs.length <= 1) {\n'
                     '    return rs;\n  }\n'
                     '  const mid = Math.floor(rs.length / 2);\n'
                     '  return mergeRows(sortRows(rs.slice(0, mid)), sortRows(rs.slice(mid)));\n}\n'
                     'console.log(sortRows(rows).map((r) => r.name).join(" "));\n',
                     _WORDS + _ROWS +
                     'function mergeRows(a: readonly Row[], b: readonly Row[]): readonly Row[] {\n'
                     '  const out: Row[] = [];\n'
                     '  let i = 0;\n'
                     '  let j = 0;\n'
                     '  while (i < a.length && j < b.length) {\n'
                     '    if (at(a, i).score <= at(b, j).score) {\n'
                     '      out.push(at(a, i));\n'
                     '      i = i + 1;\n'
                     '    } else {\n'
                     '      out.push(at(b, j));\n'
                     '      j = j + 1;\n    }\n  }\n'
                     '  return [...out, ...a.slice(i), ...b.slice(j)];\n}\n'
                     'function sortRows(rs: readonly Row[]): readonly Row[] {\n'
                     '  if (rs.length <= 1) {\n'
                     '    return rs;\n  }\n'
                     '  const mid = Math.floor(rs.length / 2);\n'
                     '  return mergeRows(sortRows(rs.slice(0, mid)), sortRows(rs.slice(mid)));\n}\n'
                     'console.log(sortRows(rows).map((r) => r.name).join(" "));\n',
                     [("ann:2 bo:1 cy:2 dee:1", "bo dee ann cy"), ("x:1 y:1", "x y")],
                     hints=["Look at what happens when the two scores are EQUAL.",
                            "With `<`, a tie falls through to the else branch and takes from the right.",
                            "Use `<=`."],
                     difficulty="Medium"),
                _fix("tscourse-w24-ms-fix2", "Fix the recursion that never ends",
                     "This dies with `RangeError: Maximum call stack size exceeded`. The base case only catches an EMPTY array — and a one-element array splits into `[]` and itself, which splits into `[]` and itself, for ever.",
                     _NUMS + _MERGE +
                     'function mergeSort(xs: readonly number[]): readonly number[] {\n'
                     '  if (xs.length === 0) {\n'
                     '    return xs;\n  }\n'
                     '  const mid = Math.floor(xs.length / 2);\n'
                     '  return merge(mergeSort(xs.slice(0, mid)), mergeSort(xs.slice(mid)));\n}\n'
                     'console.log(mergeSort(nums).join(","));\n',
                     _NUMS + _MERGE + _MSORT +
                     'console.log(mergeSort(nums).join(","));\n',
                     [("3 1 2", "1,2,3"), ("5", "5")],
                     hints=["Work out `mid` for a one-element array, then what the two slices are.",
                            "A recursive call must be on something strictly smaller.",
                            "Stop at `xs.length <= 1`."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why does merge sort split rather than, say, peel off one element at a time?",
                   ["style", "halving gives log n levels; peeling one off gives n levels — O(n²)",
                    "it is stable", "it uses less space"], 1,
                   "The halving is where the log comes from."),
                _q("The worst case for merge sort's comparisons on 8 elements is…",
                   ["28", "17", "12", "8"], 1,
                   "Every merge interleaves to the end: [1,5,3,7,2,6,4,8]."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w24-quick", "Quicksort",
            "Partition around a pivot — and meet the input that ruins it.",
            """
Merge sort does its work on the way **back up** (the merge). Quicksort does it on
the way **down**: rearrange the array so everything smaller than a chosen **pivot**
sits to its left and everything else to its right. The pivot is then in its final
place for ever, and each side is a smaller copy of the same problem.

## The partition (Lomuto)

```ts
function partition(xs: number[], lo: number, hi: number): number {
  const pivot = xs[hi] ?? 0;          // the last element
  let i = lo;                          // where the next "smaller" goes
  for (let j = lo; j < hi; j = j + 1) {
    if ((xs[j] ?? 0) < pivot) { swap(xs, i, j); i = i + 1; }
  }
  swap(xs, i, hi);                     // the pivot moves into the gap
  return i;                            // ...and this is where it lives now
}
```

That is week 22's partition-by-predicate — "write the ones that pass; everything
after `write` failed" — with the predicate being `< pivot`, and one final swap.

`partition([5, 2, 4, 1, 3])` with pivot 3 gives `[2, 1, 3, 5, 4]` and returns 2:
the 3 is finished.

## The recursion

```ts
function quick(xs: number[], lo: number, hi: number): void {
  if (lo >= hi) { return; }
  const p = partition(xs, lo, hi);
  quick(xs, lo, p - 1);                // p - 1: the pivot is done
  quick(xs, p + 1, hi);
}
```

**In place** — no new arrays, just swaps — which is quicksort's advantage over
merge sort. Its extra space is only the recursion's stack.

## The bad case, counted

With the last element as pivot, look at what already-sorted input does: the pivot
is the **largest** element, so the partition puts *everything* on one side and
the recursion peels off one element per call.

```
n=16, mixed:    cmp 64
n=16, sorted:   cmp 120     = 16·15/2 — selection sort's number
```

O(n²), on the input you would think was easiest. And sorted input is not rare —
"sort it again after adding one item" is everyday code.

## The fix is a better pivot

Swap the **middle** element to the end before partitioning:

```ts
swap(xs, Math.floor((lo + hi) / 2), hi);
```

On sorted input the middle is the median, every split is even, and the count
drops from **120 to 38**. (Next lesson proves no comparison sort can *guarantee*
fewer than 45 on sixteen elements. No contradiction: that floor is about the worst
input, and sorted input with a middle pivot is quicksort's best one.) It does not remove the worst case — some
input still hits it — but it moves it away from the inputs people actually have.
(A *random* pivot makes the worst case astronomically unlikely, but it also makes
the counts differ from run to run, which is why this course does not use one.)

## Not stable

The partition's long-distance swaps jump equal elements past each other. On
`ann 2, bo 1, cy 2, dee 1` sorted by score, quicksort puts `dee` before `bo`. Merge
sort never does that. Lesson 7 is where that decides something.

## Quickselect: half of quicksort

"The k-th smallest" does not need the whole array sorted. Partition, and the pivot
lands at index `p`. If `p === k` you are done; otherwise the answer is on **one**
side, so recurse into only that one. Throwing half the work away each time makes
it **O(n) on average** — cheaper than sorting at all.

> ⚠️ **Common mistakes:** recursing on `p` instead of `p - 1` (the pivot again,
> for ever); `<=` in the partition, which piles duplicates on one side; and a
> last-element pivot on data that arrives sorted.
""",
            warmup=[
                _q("After partitioning, the pivot is…",
                   ["at the end", "in its final sorted position", "at the start", "removed"], 1,
                   "Which is why the recursion skips it."),
                _q("Quicksort's extra space is…",
                   ["O(n)", "O(log n) on average — just the recursion", "O(1) exactly", "O(n²)"], 1,
                   "It sorts in place."),
                _q("Last-element quicksort on sorted input is…",
                   ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], 1,
                   "The pivot is always the largest."),
                _q("Quickselect is O(n) on average because…",
                   ["it sorts", "it recurses into ONE side only", "it is in place", "it uses a Map"], 1,
                   "n + n/2 + n/4 + … = 2n."),
            ],
            exercises=[
                _ex("tscourse-w24-qs-1", "Keep the smaller ones on the left",
                    "Complete the partition's loop: move each element smaller than the pivot into the next slot.",
                    _NUMS + _SWAP +
                    'function partition(xs: number[], lo: number, hi: number): number {\n'
                    '  const pivot = xs[hi] ?? 0;\n'
                    '  let i = lo;\n'
                    '  for (let j = lo; j < hi; j = j + 1) {\n'
                    '    if ((xs[j] ?? 0) < pivot) {\n'
                    '      swap(xs, i, j);\n'
                    '      i = i + 1;\n    }\n  }\n'
                    '  swap(xs, i, hi);\n'
                    '  return i;\n}\n'
                    + _QUICK +
                    'quick(nums, 0, nums.length - 1);\n'
                    'console.log(nums.join(","));\n',
                    '    if ((xs[j] ?? 0) < pivot) {\n'
                    '      swap(xs, i, j);\n'
                    '      i = i + 1;\n    }',
                    [("5 2 4 1 3", "1,2,3,4,5"), ("2 2 1", "1,2,2"), ("9", "9")],
                    hints=["`i` is where the next smaller element goes.",
                           "When xs[j] is smaller than the pivot, swap it into slot i and advance i."],
                    difficulty="Medium"),
                _ex("tscourse-w24-qs-2", "Put the pivot where it belongs",
                    "Finish one partition and report where the pivot landed.",
                    _NUMS + _SWAP +
                    'function partition(xs: number[], lo: number, hi: number): number {\n'
                    '  const pivot = xs[hi] ?? 0;\n'
                    '  let i = lo;\n'
                    '  for (let j = lo; j < hi; j = j + 1) {\n'
                    '    if ((xs[j] ?? 0) < pivot) {\n'
                    '      swap(xs, i, j);\n'
                    '      i = i + 1;\n    }\n  }\n'
                    '  swap(xs, i, hi);\n'
                    '  return i;\n}\n'
                    'const p = partition(nums, 0, nums.length - 1);\n'
                    'console.log(`p=${p} ${nums.join(",")}`);\n',
                    '  swap(xs, i, hi);',
                    [("5 2 4 1 3", "p=2 2,1,3,5,4"), ("1 2 3", "p=2 1,2,3"), ("3 2 1", "p=0 1,2,3")],
                    hints=["Everything before `i` is smaller than the pivot, so the pivot goes at `i`.",
                           "Write swap(xs, i, hi);"],
                    difficulty="Easy"),
                _ex("tscourse-w24-qs-3", "Recurse around it",
                    "Sort both sides of the pivot, leaving the pivot itself alone.",
                    _NUMS + _SWAP + _PART +
                    'function quick(xs: number[], lo: number, hi: number): void {\n'
                    '  if (lo >= hi) {\n'
                    '    return;\n  }\n'
                    '  const p = partition(xs, lo, hi);\n'
                    '  quick(xs, lo, p - 1);\n'
                    '  quick(xs, p + 1, hi);\n}\n'
                    'quick(nums, 0, nums.length - 1);\n'
                    'console.log(nums.join(","));\n',
                    '  quick(xs, lo, p - 1);\n'
                    '  quick(xs, p + 1, hi);',
                    [("5 2 4 1 3", "1,2,3,4,5"), ("4 4 4", "4,4,4"), ("6 5 4 3 2 1", "1,2,3,4,5,6")],
                    hints=["The pivot at p is finished. The left side ends just before it; the right starts just after.",
                           "Write quick(xs, lo, p - 1); then quick(xs, p + 1, hi);"],
                    difficulty="Medium"),
                _ex("tscourse-w24-qs-4", "The input that ruins it",
                    "Count quicksort's comparisons on mixed input and on sorted input of the same size.",
                    _SWAP + _PART + _QUICK +
                    'const mixed = [5, 3, 8, 1, 9, 2, 7, 4, 6, 12, 10, 16, 11, 14, 13, 15];\n'
                    'const sorted = Array.from({ length: 16 }, (_, i) => i + 1);\n'
                    'quick(mixed, 0, mixed.length - 1);\n'
                    'const mixedCmp = cmp;\n'
                    'cmp = 0;\n'
                    'quick(sorted, 0, sorted.length - 1);\n'
                    'console.log(`mixed=${mixedCmp} sorted=${cmp} worst=${(16 * 15) / 2}`);\n',
                    'quick(sorted, 0, sorted.length - 1);',
                    [("", "mixed=64 sorted=120 worst=120")],
                    hints=["Sort the already-sorted array the same way, after resetting the counter.",
                           "Write quick(sorted, 0, sorted.length - 1);"],
                    difficulty="Easy"),
                _ex("tscourse-w24-qs-5", "A middle pivot",
                    "Swap the middle element into the pivot's slot before partitioning, and watch sorted input stop being the worst case.",
                    _SWAP +
                    'let cmp = 0;\n'
                    'function partition(xs: number[], lo: number, hi: number): number {\n'
                    '  swap(xs, Math.floor((lo + hi) / 2), hi);\n'
                    '  const pivot = xs[hi] ?? 0;\n'
                    '  let i = lo;\n'
                    '  for (let j = lo; j < hi; j = j + 1) {\n'
                    '    cmp = cmp + 1;\n'
                    '    if ((xs[j] ?? 0) < pivot) {\n'
                    '      swap(xs, i, j);\n'
                    '      i = i + 1;\n    }\n  }\n'
                    '  swap(xs, i, hi);\n'
                    '  return i;\n}\n'
                    + _QUICK +
                    'const sorted = Array.from({ length: 16 }, (_, i) => i + 1);\n'
                    'quick(sorted, 0, sorted.length - 1);\n'
                    'console.log(`sorted=${cmp} ok=${sorted.join(",") === "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"}`);\n',
                    '  swap(xs, Math.floor((lo + hi) / 2), hi);',
                    [("", "sorted=38 ok=true")],
                    hints=["The partition still takes its pivot from `hi` — so move the middle element there first.",
                           "Write swap(xs, Math.floor((lo + hi) / 2), hi);"],
                    difficulty="Medium"),
                _ex("tscourse-w24-qs-6", "Quickselect",
                    "Find the k-th smallest (counting from 0) by partitioning and keeping only the side that holds it.",
                    _NUMS + _SWAP +
                    'function partition(xs: number[], lo: number, hi: number): number {\n'
                    '  const pivot = xs[hi] ?? 0;\n'
                    '  let i = lo;\n'
                    '  for (let j = lo; j < hi; j = j + 1) {\n'
                    '    if ((xs[j] ?? 0) < pivot) {\n'
                    '      swap(xs, i, j);\n'
                    '      i = i + 1;\n    }\n  }\n'
                    '  swap(xs, i, hi);\n'
                    '  return i;\n}\n'
                    'function select(xs: number[], k: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  while (lo < hi) {\n'
                    '    const p = partition(xs, lo, hi);\n'
                    '    if (p === k) {\n'
                    '      return xs[p] ?? 0;\n    }\n'
                    '    if (p < k) {\n'
                    '      lo = p + 1;\n'
                    '    } else {\n'
                    '      hi = p - 1;\n    }\n  }\n'
                    '  return xs[lo] ?? 0;\n}\n'
                    'console.log(select(nums, 2));\n',
                    '    if (p < k) {\n'
                    '      lo = p + 1;\n'
                    '    } else {\n'
                    '      hi = p - 1;\n    }',
                    [("5 2 4 1 3", "3"), ("9 8 7 6 5", "7"), ("1 1 1", "1")],
                    hints=["If the pivot landed left of k, the answer is to its right — and vice versa.",
                           "Move `lo` past the pivot, or `hi` before it. Never both."],
                    difficulty="Hard"),
                _fix("tscourse-w24-qs-fix1", "Fix the recursion that includes the pivot",
                     "This dies with `RangeError: Maximum call stack size exceeded`. The left recursion covers `[lo, p]` — the pivot included — and the pivot is the largest thing in that range, so partitioning it returns `p` again, and again.",
                     _NUMS + _SWAP + _PART +
                     'function quick(xs: number[], lo: number, hi: number): void {\n'
                     '  if (lo >= hi) {\n'
                     '    return;\n  }\n'
                     '  const p = partition(xs, lo, hi);\n'
                     '  quick(xs, lo, p);\n'
                     '  quick(xs, p + 1, hi);\n}\n'
                     'quick(nums, 0, nums.length - 1);\n'
                     'console.log(nums.join(","));\n',
                     _NUMS + _SWAP + _PART + _QUICK +
                     'quick(nums, 0, nums.length - 1);\n'
                     'console.log(nums.join(","));\n',
                     [("5 2 4 1 3", "1,2,3,4,5"), ("2 1", "1,2")],
                     hints=["After the partition, the element at p is in its final place.",
                            "A recursive call must exclude it, or the range never shrinks.",
                            "Write quick(xs, lo, p - 1);"],
                     difficulty="Medium"),
                _fix("tscourse-w24-qs-fix2", "Fix the pivot that sorted input defeats",
                     "The requirement is fewer than 60 comparisons on 16 already-sorted items, and this reports `cmp=120 over budget`. Nothing is wrong with the ORDER it produces — the bug is the cost, and the cause is the pivot: on sorted input the last element is always the largest.",
                     _SWAP + _PART + _QUICK +
                     'const sorted = Array.from({ length: 16 }, (_, i) => i + 1);\n'
                     'quick(sorted, 0, sorted.length - 1);\n'
                     'console.log(`cmp=${cmp} ${cmp < 60 ? "ok" : "over budget"}`);\n',
                     _SWAP +
                     'let cmp = 0;\n'
                     'function partition(xs: number[], lo: number, hi: number): number {\n'
                     '  swap(xs, Math.floor((lo + hi) / 2), hi);\n'
                     '  const pivot = xs[hi] ?? 0;\n'
                     '  let i = lo;\n'
                     '  for (let j = lo; j < hi; j = j + 1) {\n'
                     '    cmp = cmp + 1;\n'
                     '    if ((xs[j] ?? 0) < pivot) {\n'
                     '      swap(xs, i, j);\n'
                     '      i = i + 1;\n    }\n  }\n'
                     '  swap(xs, i, hi);\n'
                     '  return i;\n}\n'
                     + _QUICK +
                     'const sorted = Array.from({ length: 16 }, (_, i) => i + 1);\n'
                     'quick(sorted, 0, sorted.length - 1);\n'
                     'console.log(`cmp=${cmp} ${cmp < 60 ? "ok" : "over budget"}`);\n',
                     [("", "cmp=38 ok")],
                     hints=["Every partition peels off exactly one element — the pivot is always the maximum.",
                            "A pivot from the middle of a sorted range is its median.",
                            "At the start of partition, swap(xs, Math.floor((lo + hi) / 2), hi);"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Merge sort works on the way up; quicksort works…",
                   ["also on the way up", "on the way down — the partition happens before the recursion",
                    "not at all", "in parallel"], 1,
                   "The pivot is placed before either side is sorted."),
                _q("A random pivot is avoided in this course because…",
                   ["it is slow", "the counts would differ from run to run", "it is wrong", "of types"], 1,
                   "Deterministic output is the judge's whole contract."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w24-counting", "Sorting without comparing",
            "Counting sort, and the n log n limit it steps around.",
            """
## The limit

Every sort so far learns the order by asking "is `a` before `b`?". There are
`n!` possible orders of n elements, and each yes/no answer can at best halve the
ones still possible — so the worst case needs at least **⌈log₂ n!⌉** comparisons:

```
n=4    at least  5      (4! = 24 orders)
n=8    at least 16      (8! = 40,320)
n=16   at least 45
```

`log₂ n!` grows like **n log n**. That is the proof that no comparison sort can
beat O(n log n) — and merge sort, at 17 on its worst eight elements against a floor
of 16, is almost exactly as good as possible.

## Stepping around it

The bound is about **comparing**. If the values are small integers, you do not
need to compare them — you can use them as **array indexes**:

```ts
const counts: number[] = new Array(max + 1).fill(0);
for (const x of xs) { counts[x] = (counts[x] ?? 0) + 1; }      // tally
const out: number[] = [];
for (let v = 0; v <= max; v = v + 1) {                           // emit in order
  for (let c = 0; c < (counts[v] ?? 0); c = c + 1) { out.push(v); }
}
```

**O(n + k)**, where k is the range of values, and not a single comparison. Ages,
grades, star ratings, days of the month: counting sort is the right tool, and it
is linear.

## When it is the wrong tool

The `+ k` is not decoration. Two numbers, `5` and `1000`: that is 2 tallies and
**1,001** buckets to walk. The cost is the *range*, not the count, and a sort of
three timestamps would walk billions of empty buckets. Counting sort is for **small
integer ranges** — and it cannot sort strings or fractions at all.

## Negative values

`counts[-2]` does not index an array: it sets a *property* named `"-2"`, which the
`0 … max` loop never visits — so negative values **silently disappear**. The fix is
an offset: index by `x - min`, emit `v + min`.

## A stable version, from week 23

To sort *records* by a small key (students by grade), tallies are not enough —
you need to know where each record *goes*. That is a **prefix sum** over the
counts: the number of records with a smaller key is exactly where the first record
with this key belongs.

```
grades  = [2, 0, 2, 1]
counts  = [1, 1, 2]          (one 0, one 1, two 2s)
starts  = [0, 1, 2]          prefix sums — where each grade's block begins
```

Walk the input **in order**, placing each record at `starts[grade]` and bumping
it. Equal grades land in input order: stable. Week 23's leading-zero prefix array,
doing a completely different job.

> ⚠️ **Common mistakes:** emitting `v < max` and losing the largest value;
> negative values without an offset; and counting sort on a huge range.
""",
            warmup=[
                _q("No comparison sort can beat…",
                   ["O(n)", "about n log n comparisons in the worst case", "O(n²)", "O(log n)"], 1,
                   "Each answer at best halves n! possible orders."),
                _q("Counting sort runs in…",
                   ["O(n log n)", "O(n + k), k being the range of values", "O(n²)", "O(k²)"], 1,
                   "Tally, then walk the range."),
                _q("Counting sort gets round the lower bound by…",
                   ["cheating", "never comparing — using values as indexes", "being unstable", "recursion"], 1,
                   "The bound only applies to comparisons."),
                _q("`counts[-2] = 1` on an array…",
                   ["throws", "sets a property the index loop never visits", "writes index 0", "is a type error"], 1,
                   "Negative values silently vanish."),
            ],
            exercises=[
                _ex("tscourse-w24-cs-1", "Tally",
                    "Count how many times each value occurs.",
                    _NUMS + _COUNTING +
                    'console.log(countingSort(nums).join(","));\n',
                    '    counts[x] = (counts[x] ?? 0) + 1;',
                    [("3 1 2 1 0", "0,1,1,2,3"), ("4 4", "4,4")],
                    hints=["The value is the index; the entry is how many times it occurred.",
                           "Write counts[x] = (counts[x] ?? 0) + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w24-cs-2", "Emit in order",
                    "Walk the values in order and output each one as many times as it was counted.",
                    _NUMS + _COUNTING +
                    'console.log(countingSort(nums).join(","));\n',
                    '    for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
                    '      out.push(v);\n    }',
                    [("3 1 2 1 0", "0,1,1,2,3"), ("2 0 2", "0,2,2")],
                    hints=["`counts[v]` says how many copies of v to output.",
                           "An inner loop that pushes v that many times."],
                    difficulty="Medium"),
                _ex("tscourse-w24-cs-3", "The cost is the range",
                    "Count counting sort's steps: one per tally and one per bucket walked.",
                    _NUMS +
                    'const max = Math.max(...nums);\n'
                    'const counts: number[] = new Array(max + 1).fill(0);\n'
                    'let ops = 0;\n'
                    'for (const x of nums) {\n'
                    '  counts[x] = (counts[x] ?? 0) + 1;\n'
                    '  ops = ops + 1;\n}\n'
                    'const out: number[] = [];\n'
                    'for (let v = 0; v <= max; v = v + 1) {\n'
                    '  ops = ops + 1;\n'
                    '  for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
                    '    out.push(v);\n  }\n}\n'
                    'console.log(`n=${nums.length} ops=${ops} comparisons=0`);\n',
                    'for (let v = 0; v <= max; v = v + 1) {',
                    [("3 1 2 1 0", "n=5 ops=9 comparisons=0"), ("5 1000", "n=2 ops=1003 comparisons=0")],
                    hints=["Every bucket from 0 to max is visited, empty or not.",
                           "Write for (let v = 0; v <= max; v = v + 1) {"],
                    difficulty="Easy"),
                _ex("tscourse-w24-cs-4", "Where each record goes",
                    "Turn the counts into starting positions with a prefix sum, so records can be placed stably.",
                    _WORDS + _ROWS +
                    'const counts: number[] = [0, 0, 0, 0];\n'
                    'for (const r of rows) {\n'
                    '  counts[r.score] = (counts[r.score] ?? 0) + 1;\n}\n'
                    'const starts: number[] = [0];\n'
                    'for (let g = 1; g < counts.length; g = g + 1) {\n'
                    '  starts.push((starts[g - 1] ?? 0) + (counts[g - 1] ?? 0));\n}\n'
                    'const out: Row[] = new Array(rows.length);\n'
                    'for (const r of rows) {\n'
                    '  const slot = starts[r.score] ?? 0;\n'
                    '  out[slot] = r;\n'
                    '  starts[r.score] = slot + 1;\n}\n'
                    'console.log(out.map((r) => r.name).join(" "));\n',
                    '  starts.push((starts[g - 1] ?? 0) + (counts[g - 1] ?? 0));',
                    [("ann:2 bo:0 cy:2 dee:1", "bo dee ann cy"), ("a:3 b:3 c:0", "c a b")],
                    hints=["A grade's block starts where the previous grade's block started, plus how many that grade had.",
                           "Write starts.push((starts[g - 1] ?? 0) + (counts[g - 1] ?? 0));"],
                    difficulty="Hard"),
                _ex("tscourse-w24-cs-5", "The floor under every comparison sort",
                    "Compute ⌈log₂ n!⌉ — the fewest comparisons any comparison sort can guarantee.",
                    'for (const n of [4, 8, 16]) {\n'
                    '  let bits = 0;\n'
                    '  for (let i = 2; i <= n; i = i + 1) {\n'
                    '    bits = bits + Math.log2(i);\n  }\n'
                    '  console.log(`n=${n} atLeast=${Math.ceil(bits)}`);\n}\n',
                    '    bits = bits + Math.log2(i);',
                    [("", "n=4 atLeast=5\nn=8 atLeast=16\nn=16 atLeast=45")],
                    hints=["log₂(n!) = log₂ 2 + log₂ 3 + … + log₂ n — a sum, so no giant factorial is ever built.",
                           "Write bits = bits + Math.log2(i);"],
                    difficulty="Medium"),
                _fix("tscourse-w24-cs-fix1", "Fix the largest value that vanished",
                     "This prints `0,1,1,2` for `3 1 2 1 0` — the 3 is gone. The emit loop stops at `v < max`, so the bucket for the largest value is never walked.",
                     _NUMS +
                     'const max = Math.max(...nums);\n'
                     'const counts: number[] = new Array(max + 1).fill(0);\n'
                     'for (const x of nums) {\n'
                     '  counts[x] = (counts[x] ?? 0) + 1;\n}\n'
                     'const out: number[] = [];\n'
                     'for (let v = 0; v < max; v = v + 1) {\n'
                     '  for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
                     '    out.push(v);\n  }\n}\n'
                     'console.log(out.join(","));\n',
                     _NUMS +
                     'const max = Math.max(...nums);\n'
                     'const counts: number[] = new Array(max + 1).fill(0);\n'
                     'for (const x of nums) {\n'
                     '  counts[x] = (counts[x] ?? 0) + 1;\n}\n'
                     'const out: number[] = [];\n'
                     'for (let v = 0; v <= max; v = v + 1) {\n'
                     '  for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
                     '    out.push(v);\n  }\n}\n'
                     'console.log(out.join(","));\n',
                     [("3 1 2 1 0", "0,1,1,2,3"), ("7", "7")],
                     hints=["The array was made `max + 1` long so that `max` itself has a bucket.",
                            "The walk has to reach that bucket.",
                            "Write v <= max."],
                     difficulty="Easy"),
                _fix("tscourse-w24-cs-fix2", "Fix the negative values that disappeared",
                     "This prints `0,3` for `-2 3 0`. `counts[-2]` is not an array slot — it creates a property named `\"-2\"`, which the walk from 0 never visits. Nothing throws; the value is just gone.",
                     _NUMS +
                     'const max = Math.max(...nums);\n'
                     'const counts: number[] = new Array(max + 1).fill(0);\n'
                     'for (const x of nums) {\n'
                     '  counts[x] = (counts[x] ?? 0) + 1;\n}\n'
                     'const out: number[] = [];\n'
                     'for (let v = 0; v <= max; v = v + 1) {\n'
                     '  for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
                     '    out.push(v);\n  }\n}\n'
                     'console.log(out.join(","));\n',
                     _NUMS +
                     'const min = Math.min(...nums);\n'
                     'const max = Math.max(...nums);\n'
                     'const counts: number[] = new Array(max - min + 1).fill(0);\n'
                     'for (const x of nums) {\n'
                     '  counts[x - min] = (counts[x - min] ?? 0) + 1;\n}\n'
                     'const out: number[] = [];\n'
                     'for (let v = 0; v <= max - min; v = v + 1) {\n'
                     '  for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
                     '    out.push(v + min);\n  }\n}\n'
                     'console.log(out.join(","));\n',
                     [("-2 3 0", "-2,0,3"), ("-1 -1 -5", "-5,-1,-1"), ("2 1", "1,2")],
                     hints=["Shift every value so the smallest one lands at index 0.",
                            "Index by `x - min`, size the array `max - min + 1`.",
                            "Shift back when emitting: push `v + min`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Merge sort's 17 comparisons on its worst 8 elements, against a floor of 16, shows…",
                   ["it is slow", "it is within one comparison of the best possible", "the floor is wrong",
                    "counting sort is better"], 1,
                   "n log n is not just good; it is nearly optimal."),
                _q("A stable counting sort places records using…",
                   ["a Map", "prefix sums of the counts — week 23", "binary search", "a stack"], 1,
                   "Where each key's block starts."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w24-builtin", "The built-in sort, properly",
            "The comparator contract, stability you can rely on, and sorting without mutating.",
            """
You will almost always call the built-in. Four things about it are worth knowing
exactly.

## 1. The comparator contract

```ts
(a, b) => negative   // a comes first
(a, b) => positive   // b comes first
(a, b) => 0          // either order will do
```

`a - b` is ascending, `b - a` descending. And the contract is not a suggestion.

**A comparator that never returns a negative does not sort.** This compiles:

```ts
[3, 1, 2].sort((a, b) => (a > b ? 1 : 0));   // [3, 1, 2] — untouched
```

The engine only moves an element when told it belongs *earlier*, and this
comparator never says that. No error, no warning — the array comes back as it
went in. It looks like a sort and it is not one.

**A comparator returning a boolean is rejected**, which is the compiler saving
you from the same bug:

```
TS2345: Argument of type '(a: number, b: number) => boolean' is not
        assignable to parameter of type '(a: number, b: number) => number'.
```

Run it anyway and `[3, 1, 2]` comes back unsorted too.

## 2. Several keys

Week 19 wrote the idiom: compare the first key, and when that is a tie (`0`),
fall through with `||` to the next.

```ts
rows.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));
```

Score descending, then name A-Z. `||` works because `0` is falsy and any other
number is not.

## 3. Stability is guaranteed

Since ES2019 the built-in `sort` **must** be stable. That gives you a second way to
sort by several keys: sort by the *least* important key first, then by the most
important. The second sort keeps the first one's order among its ties:

```ts
rows.sort((a, b) => a.name.localeCompare(b.name));   // secondary first
rows.sort((a, b) => b.score - a.score);              // primary last
```

Same result as the `||` version. Do them in the other order and the name sort
wins, which is the classic mistake.

## 4. `sort` mutates — so do not, unless you mean to

Week 6's warning, now with the type system's help. `readonly number[]` **has no
`.sort` method**:

```
TS2339: Property 'sort' does not exist on type 'readonly number[]'.
```

That is not a gap in the types, it *is* the type: `sort` mutates, and `readonly`
promised nothing would. Two answers:

```ts
const a = [...xs].sort((x, y) => x - y);      // copy, then sort the copy
const b = xs.toSorted((x, y) => x - y);       // the same thing, in one call
```

`toSorted` returns a new **mutable** array — `number[]`, not `readonly number[]` —
because the copy is yours.

> ⚠️ **Common mistakes:** a comparator that returns a boolean, or never returns a
> negative; sorting the keys in the wrong order when relying on stability; and
> sorting an array someone else is still reading.
""",
            warmup=[
                _q("A comparator returning a negative number means…",
                   ["b first", "a first", "equal", "an error"], 1,
                   "a - b is negative when a is smaller: ascending."),
                _q("`[3, 1, 2].sort((a, b) => (a > b ? 1 : 0))` gives…",
                   ["[1, 2, 3]", "[3, 1, 2] — untouched", "[3, 2, 1]", "an error"], 1,
                   "It never says 'a comes first'."),
                _q("The built-in sort is stable…",
                   ["sometimes", "always, since ES2019", "for numbers only", "never"], 1,
                   "Which you can rely on."),
                _q("`toSorted` returns…",
                   ["nothing", "a sorted copy, leaving the original alone", "the same array", "a readonly array"], 1,
                   "The non-mutating sort."),
            ],
            exercises=[
                _ex("tscourse-w24-bi-1", "Descending",
                    "Sort largest first.",
                    _NUMS +
                    'const sorted = [...nums].sort((a, b) => b - a);\n'
                    'console.log(sorted.join(","));\n',
                    'const sorted = [...nums].sort((a, b) => b - a);',
                    [("3 10 2", "10,3,2"), ("1 1 5", "5,1,1")],
                    hints=["Positive means b comes first — so b - a puts bigger values first.",
                           "Write const sorted = [...nums].sort((a, b) => b - a);"],
                    difficulty="Easy"),
                _ex("tscourse-w24-bi-2", "Two keys in one comparator",
                    "Highest score first; on a tie, alphabetical by name.",
                    _WORDS + _ROWS +
                    'const sorted = [...rows].sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));\n'
                    'console.log(sorted.map((r) => r.name).join(" "));\n',
                    'const sorted = [...rows].sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));',
                    [("cy:2 ann:2 bo:3", "bo ann cy"), ("dee:1 cal:1 al:1", "al cal dee")],
                    hints=["The first key decides; `||` falls through to the second only when the first is 0.",
                           "Write const sorted = [...rows].sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));"],
                    difficulty="Medium"),
                _ex("tscourse-w24-bi-3", "Two keys in two passes",
                    "Rely on stability: sort by the secondary key, then by the primary one.",
                    _WORDS + _ROWS +
                    'const sorted = [...rows];\n'
                    'sorted.sort((a, b) => a.name.localeCompare(b.name));\n'
                    'sorted.sort((a, b) => b.score - a.score);\n'
                    'console.log(sorted.map((r) => r.name).join(" "));\n',
                    'sorted.sort((a, b) => b.score - a.score);',
                    [("cy:2 ann:2 bo:3", "bo ann cy"), ("dee:1 cal:1 al:1", "al cal dee")],
                    hints=["The LAST sort is the most important key.",
                           "Write sorted.sort((a, b) => b.score - a.score);"],
                    difficulty="Medium"),
                _ex("tscourse-w24-bi-4", "Sort without touching the original",
                    "Get a sorted copy in one call.",
                    _NUMS +
                    'const sorted = nums.toSorted((a, b) => a - b);\n'
                    'console.log(`${nums.join(",")} | ${sorted.join(",")}`);\n',
                    'const sorted = nums.toSorted((a, b) => a - b);',
                    [("3 1 2", "3,1,2 | 1,2,3"), ("9 8", "9,8 | 8,9")],
                    hints=["`toSorted` takes the same comparator as `sort` and returns a new array.",
                           "Write const sorted = nums.toSorted((a, b) => a - b);"],
                    difficulty="Easy"),
                _predict("tscourse-w24-bi-p1", "What a sorted copy is",
                         'const names: readonly string[] = ["cy", "ann", "bo"];\n'
                         'const sorted = names.toSorted();\n',
                         "sorted", "string[]",
                         why="The input is `readonly` — is the copy?",
                         hints=["A copy belongs to whoever made it.",
                                "Write string[]."]),
                _diagnose("tscourse-w24-bi-d1", "The comparator that answered a question",
                          "TS2345: Argument of type '(a: number, b: number) => boolean' is not assignable to parameter of type '(a: number, b: number) => number'.",
                          _NUMS +
                          'const sorted = [...nums].sort((a, b) => a > b);\n'
                          'console.log(sorted.join(","));\n',
                          _NUMS +
                          'const sorted = [...nums].sort((a, b) => a - b);\n'
                          'console.log(sorted.join(","));\n',
                          [("3 1 2", "1,2,3"), ("5 4 6", "4,5,6")],
                          hints=["A comparator answers 'which comes first, and by how much?' with a NUMBER.",
                                 "`true` and `false` cannot say 'a first', 'b first' AND 'tie'.",
                                 "Write (a, b) => a - b."],
                          difficulty="Easy"),
                _diagnose("tscourse-w24-bi-d2", "Sorting what was promised read-only",
                          "TS2339: Property 'sort' does not exist on type 'readonly number[]'.",
                          'const prices: readonly number[] = [30, 10, 20];\n'
                          'const sorted = prices.sort((a, b) => a - b);\n'
                          'console.log(`${sorted.join(",")} from ${prices.join(",")}`);\n',
                          'const prices: readonly number[] = [30, 10, 20];\n'
                          'const sorted = prices.toSorted((a, b) => a - b);\n'
                          'console.log(`${sorted.join(",")} from ${prices.join(",")}`);\n',
                          [("", "10,20,30 from 30,10,20")],
                          hints=["`sort` rearranges the array it is called on — the one thing `readonly` rules out.",
                                 "You want a sorted copy, not a sorted original.",
                                 "Use toSorted (or [...prices].sort)."],
                          difficulty="Easy"),
                _fix("tscourse-w24-bi-fix1", "Fix the comparator that never says 'first'",
                     "This compiles, runs, and prints `3,1,2` for `3 1 2` — unsorted. The comparator returns 1 or 0 and never a negative number, and the engine only moves an element when told it belongs earlier.",
                     _NUMS +
                     'const sorted = [...nums].sort((a, b) => (a > b ? 1 : 0));\n'
                     'console.log(sorted.join(","));\n',
                     _NUMS +
                     'const sorted = [...nums].sort((a, b) => a - b);\n'
                     'console.log(sorted.join(","));\n',
                     [("3 1 2", "1,2,3"), ("5 4 3 2 1", "1,2,3,4,5")],
                     hints=["A comparator has three answers, and this one only gives two of them.",
                            "Negative must mean 'a comes first'.",
                            "Write (a, b) => a - b."],
                     difficulty="Easy"),
                _fix("tscourse-w24-bi-fix2", "Fix the report that sorted its own input",
                     "The second line should echo the prices as entered, and prints them sorted: `sort` rearranged `nums` itself, and `sorted` is the same array under another name.",
                     _NUMS +
                     'const sorted = nums.sort((a, b) => a - b);\n'
                     'console.log(`lowest ${sorted[0] ?? 0}`);\n'
                     'console.log(`as entered ${nums.join(",")}`);\n',
                     _NUMS +
                     'const sorted = nums.toSorted((a, b) => a - b);\n'
                     'console.log(`lowest ${sorted[0] ?? 0}`);\n'
                     'console.log(`as entered ${nums.join(",")}`);\n',
                     [("30 10 20", "lowest 10\nas entered 30,10,20")],
                     hints=["`sort` returns the array it was called on — not a new one.",
                            "Sort a copy instead.",
                            "Use nums.toSorted(...) or [...nums].sort(...)."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Sorting by name and then by score, relying on stability, orders…",
                   ["by name", "by score, with ties by name", "randomly", "by score, ties reversed"], 1,
                   "The last sort is the primary key."),
                _q("`||` works for tie-breaking because…",
                   ["it is a sort feature", "0 is falsy, so only a tie falls through", "it compares strings",
                    "it is stable"], 1,
                   "Any non-zero result stands."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w24-tool", "Sorting as a tool",
            "Sort first, and a hard question becomes a question about neighbours.",
            """
The most useful thing about sorting is not the sorted array. It is what the
sorted array makes **easy**. After a sort, related things are **next to each
other**, and a question about all pairs becomes a question about neighbours.

## Closest pair

"The smallest gap between any two values." Every pair: n(n-1)/2 comparisons. But
in sorted order the closest two values are always **adjacent** — anything in
between would be closer to one of them — so:

```ts
const s = [...xs].sort((a, b) => a - b);
let best = Infinity;
for (let i = 1; i < s.length; i = i + 1) {
  best = Math.min(best, (s[i] ?? 0) - (s[i - 1] ?? 0));
}
```

O(n log n) for the sort plus **n - 1** comparisons, against n(n-1)/2. Four values:
6 against 3. A thousand: 499,500 against 999.

## Duplicates, groups, clashes — all neighbours

* **Any duplicate?** Sorted, two equal values are adjacent. (Week 19's `Set` is
  O(n) and simpler — but sorting uses no extra memory, and it also tells you *how
  many* of each, in order.)
* **Group anagrams.** Sort each word's *letters* and use that as a `Map` key:
  `listen`, `silent` and `enlist` all become `eilnst`. Sorting as a way to compute
  a canonical key — the same trick as week 19's canonical-key function.
* **Do any bookings clash?** Sort by start time; a clash can only be between a
  booking and the one right after it. (Week 28 turns this into a whole topic.)

## Order statistics

* **The median** is the middle of the sorted array — or the average of the two
  middles when the length is even.
* **The k-th largest** is `s[s.length - k]`.

Both are O(n log n) this way. Lesson 3's quickselect does the k-th in O(n) average
when that matters; sorting is the version you can write in an interview in thirty
seconds and explain in ten.

## Default sort, one more time

Every one of these needs a **numeric** comparator. Week 6's trap — `sort()` with no
comparator sorts `100, 25, 3, 9` as text — is at its most dangerous here, because
the program still produces a plausible-looking number.

> ⚠️ **Common mistakes:** sorting without a comparator; taking the median of
> unsorted data; and comparing every pair when neighbours would do.
""",
            warmup=[
                _q("After sorting, the closest pair of values is always…",
                   ["the first two", "some adjacent pair", "the ends", "anywhere"], 1,
                   "Anything between them would be closer."),
                _q("Anagrams share…",
                   ["a length only", "the same letters in sorted order", "a first letter", "a Set"], 1,
                   "Sort the letters to get the key."),
                _q("The median of 4 sorted values is…",
                   ["the 2nd", "the average of the 2nd and 3rd", "the 3rd", "the mean"], 1,
                   "Two middles when the length is even."),
                _q("To check whether any bookings clash, after sorting by start…",
                   ["check every pair", "check each booking against the next", "binary search", "use a Map"], 1,
                   "Neighbours again."),
            ],
            exercises=[
                _ex("tscourse-w24-tl-1", "The closest pair",
                    "Sort, then compare each value only with its neighbour.",
                    _NUMS +
                    'const s = [...nums].sort((a, b) => a - b);\n'
                    'let best = Number.MAX_SAFE_INTEGER;\n'
                    'for (let i = 1; i < s.length; i = i + 1) {\n'
                    '  best = Math.min(best, (s[i] ?? 0) - (s[i - 1] ?? 0));\n}\n'
                    'console.log(best);\n',
                    '  best = Math.min(best, (s[i] ?? 0) - (s[i - 1] ?? 0));',
                    [("10 3 7 1", "2"), ("5 5", "0"), ("100 25 3 9", "6")],
                    hints=["In sorted order the gap is always this element minus the one before.",
                           "Write best = Math.min(best, (s[i] ?? 0) - (s[i - 1] ?? 0));"],
                    difficulty="Easy"),
                _ex("tscourse-w24-tl-2", "What sorting saved",
                    "Report every-pair comparisons against the neighbour comparisons a sort makes possible.",
                    _NUMS +
                    'const n = nums.length;\n'
                    'const pairs = (n * (n - 1)) / 2;\n'
                    'const neighbours = n - 1;\n'
                    'console.log(`pairs=${pairs} neighbours=${neighbours}`);\n',
                    'const pairs = (n * (n - 1)) / 2;',
                    [("10 3 7 1", "pairs=6 neighbours=3"), ("1 2", "pairs=1 neighbours=1")],
                    hints=["Every value against every later value.",
                           "Write const pairs = (n * (n - 1)) / 2;"],
                    difficulty="Easy"),
                _ex("tscourse-w24-tl-3", "Group the anagrams",
                    "Use each word's letters, sorted, as its group key.",
                    _WORDS +
                    'const groups = new Map<string, string[]>();\n'
                    'for (const w of words) {\n'
                    '  const key = [...w].sort().join("");\n'
                    '  const group = groups.get(key) ?? [];\n'
                    '  group.push(w);\n'
                    '  groups.set(key, group);\n}\n'
                    'for (const group of groups.values()) {\n'
                    '  console.log(group.join(","));\n}\n',
                    '  const key = [...w].sort().join("");',
                    [("listen google silent enlist", "listen,silent,enlist\ngoogle"),
                     ("ab ba c", "ab,ba\nc")],
                    hints=["Spread the word into letters, sort them, join them back.",
                           "Single letters sort correctly as text — no comparator needed here.",
                           'Write const key = [...w].sort().join("");'],
                    difficulty="Medium"),
                _ex("tscourse-w24-tl-4", "The median",
                    "The middle value — or, for an even count, the average of the two middles.",
                    _NUMS +
                    'const s = [...nums].sort((a, b) => a - b);\n'
                    'const mid = Math.floor(s.length / 2);\n'
                    'const median = s.length % 2 === 1\n'
                    '  ? (s[mid] ?? 0)\n'
                    '  : ((s[mid - 1] ?? 0) + (s[mid] ?? 0)) / 2;\n'
                    'console.log(median);\n',
                    '  : ((s[mid - 1] ?? 0) + (s[mid] ?? 0)) / 2;',
                    [("5 1 3", "3"), ("4 1 3 2", "2.5"), ("10 20", "15")],
                    hints=["For an even length, `mid` is the upper of the two middles.",
                           "Average s[mid - 1] and s[mid]."],
                    difficulty="Medium"),
                _ex("tscourse-w24-tl-5", "The k-th largest",
                    "Count k from the top of the sorted array.",
                    _NUMS +
                    'const k = 2;\n'
                    'const s = [...nums].sort((a, b) => a - b);\n'
                    'console.log(s[s.length - k] ?? 0);\n',
                    'console.log(s[s.length - k] ?? 0);',
                    [("3 9 5", "5"), ("4 4 1", "4")],
                    hints=["The largest is at s.length - 1, the second largest one before it.",
                           "Write console.log(s[s.length - k] ?? 0);"],
                    difficulty="Easy"),
                _ex("tscourse-w24-tl-6", "Do any bookings clash?",
                    "Sort the bookings by start time, so a clash can only be between neighbours.",
                    _WORDS +
                    'interface Booking {\n'
                    '  readonly start: number;\n'
                    '  readonly end: number;\n}\n'
                    'const bookings: Booking[] = words.map((w) => {\n'
                    '  const [start, end] = w.split("-");\n'
                    '  return { start: Number(start ?? "0"), end: Number(end ?? "0") };\n});\n'
                    'bookings.sort((a, b) => a.start - b.start);\n'
                    'let clash = false;\n'
                    'for (let i = 1; i < bookings.length; i = i + 1) {\n'
                    '  const prev = bookings[i - 1];\n'
                    '  const cur = bookings[i];\n'
                    '  if (prev !== undefined && cur !== undefined && prev.end > cur.start) {\n'
                    '    clash = true;\n  }\n}\n'
                    'console.log(clash ? "clash" : "fits");\n',
                    'bookings.sort((a, b) => a.start - b.start);',
                    [("1-3 5-6 2-4", "clash"), ("5-6 1-2 2-3", "fits"), ("1-9", "fits")],
                    hints=["Order by the start time, earliest first.",
                           "Write bookings.sort((a, b) => a.start - b.start);"],
                    difficulty="Medium"),
                _fix("tscourse-w24-tl-fix1", "Fix the gap that came out negative",
                     "This reports a smallest gap of `-75` for `100 25 3 9`. A gap cannot be negative — the values were sorted as TEXT (`\"100\" < \"25\" < \"3\" < \"9\"`), so the neighbours are not in numeric order.",
                     _NUMS +
                     'const s = [...nums].sort();\n'
                     'let best = Number.MAX_SAFE_INTEGER;\n'
                     'for (let i = 1; i < s.length; i = i + 1) {\n'
                     '  best = Math.min(best, (s[i] ?? 0) - (s[i - 1] ?? 0));\n}\n'
                     'console.log(best);\n',
                     _NUMS +
                     'const s = [...nums].sort((a, b) => a - b);\n'
                     'let best = Number.MAX_SAFE_INTEGER;\n'
                     'for (let i = 1; i < s.length; i = i + 1) {\n'
                     '  best = Math.min(best, (s[i] ?? 0) - (s[i - 1] ?? 0));\n}\n'
                     'console.log(best);\n',
                     [("100 25 3 9", "6"), ("10 3 7 1", "2")],
                     hints=["With no comparator, `sort` compares the values as strings.",
                            "Week 6's trap, in a place where the wrong answer still looks like a number.",
                            "Write .sort((a, b) => a - b)."],
                     difficulty="Easy"),
                _fix("tscourse-w24-tl-fix2", "Fix the median of unsorted data",
                     "This reports `1` as the median of `5 1 3`, which is simply the middle of the input as typed. A median is the middle of the values IN ORDER.",
                     _NUMS +
                     'const mid = Math.floor(nums.length / 2);\n'
                     'console.log(nums[mid] ?? 0);\n',
                     _NUMS +
                     'const s = [...nums].sort((a, b) => a - b);\n'
                     'const mid = Math.floor(s.length / 2);\n'
                     'console.log(s[mid] ?? 0);\n',
                     [("5 1 3", "3"), ("9 7 8", "8")],
                     hints=["The position of the median only means something once the values are ordered.",
                            "Sort a copy numerically first.",
                            "Then take the middle of the copy."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Sorting a word's letters to get a key is the same idea as…",
                   ["binary search", "week 19's canonical-key function", "a prefix sum", "a heap"], 1,
                   "Many inputs, one representative."),
                _q("Checking for duplicates, a Set is O(n) and sorting is O(n log n). Sorting still wins when…",
                   ["never", "memory is tight, or you also want the values in order", "the values are strings",
                    "n is small"], 1,
                   "Different costs, not a strict ranking."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w24-choose", "Choosing a sort",
            "Usually the built-in — and knowing exactly when it is not.",
            """
## The table

| | best | average | worst | extra space | stable | adaptive |
|---|---|---|---|---|---|---|
| selection | n² | n² | n² | 1 | no | no |
| insertion | **n** | n² | n² | 1 | yes | **yes** |
| merge | n log n | n log n | n log n | n | yes | no |
| quick | n log n | n log n | **n²** | log n | no | no |
| counting | n + k | n + k | n + k | n + k | yes | — |

## The honest default

**Use the built-in.** It is stable, it is O(n log n) in the worst case, and it is
adaptive: engines use a hybrid (TimSort in V8) that finds already-sorted runs and
**merges** them, falling back to **insertion sort** on short stretches — this
week's two best ideas, combined. You will not beat it with a hand-written
quicksort.

## When not

* **Small integer range** (ages, grades, ratings) → **counting sort**. O(n + k),
  and genuinely faster than any comparison sort.
* **You need only the smallest few, not the full order** → don't sort everything.
  k passes of selection cost about k·n; quickselect costs n on average.
* **The data is already sorted, or nearly** → check first. An O(n) scan that
  finds nothing to do is the cheapest sort there is.
* **Ties must keep their input order** → a **stable** sort: the built-in, merge,
  insertion or counting. **Never quicksort.**

## Why an interviewer asks

"Which sort would you use?" is almost never about quicksort versus merge sort in
the abstract. It is a question about *this* data: its range, its order, its size,
and whether equal elements are distinguishable. Answer from the table, name the
property that decided it, and you have answered the real question.

> ⚠️ **Common mistakes:** writing a sort when the built-in would do; using an
> unstable sort on records whose ties matter; and sorting everything to find three
> values.
""",
            warmup=[
                _q("The built-in sort is a hybrid of…",
                   ["quick and heap", "merge and insertion", "selection and counting", "bubble and quick"], 1,
                   "TimSort, in V8."),
                _q("For exam grades 0-100, the fastest sort is…",
                   ["quicksort", "counting sort", "merge sort", "insertion sort"], 1,
                   "A small integer range."),
                _q("When ties must keep their order, never use…",
                   ["merge sort", "quicksort", "the built-in", "insertion sort"], 1,
                   "It is not stable."),
                _q("To find the 3 smallest of a million values…",
                   ["sort them all", "don't sort everything — select them", "use counting sort", "use a Set"], 1,
                   "k passes, or quickselect."),
            ],
            exercises=[
                _ex("tscourse-w24-ch-1", "Read the table back",
                    "Report which of the five sorts are stable.",
                    'const sorts: readonly [string, boolean][] = [\n'
                    '  ["selection", false],\n'
                    '  ["insertion", true],\n'
                    '  ["merge", true],\n'
                    '  ["quick", false],\n'
                    '  ["counting", true],\n'
                    '];\n'
                    'const stable = sorts.filter(([, isStable]) => isStable).map(([name]) => name);\n'
                    'console.log(stable.join(","));\n',
                    'const stable = sorts.filter(([, isStable]) => isStable).map(([name]) => name);',
                    [("", "insertion,merge,counting")],
                    hints=["Keep the entries whose flag is true, then keep only their names.",
                           "Write const stable = sorts.filter(([, isStable]) => isStable).map(([name]) => name);"],
                    difficulty="Medium"),
                _ex("tscourse-w24-ch-2", "Choose from the shape of the data",
                    "Map each situation to the sort that fits it.",
                    _NUMS +
                    'function choose(situation: number): string {\n'
                    '  if (situation === 1) {\n'
                    '    return "counting";\n  }\n'
                    '  if (situation === 2) {\n'
                    '    return "insertion";\n  }\n'
                    '  if (situation === 3) {\n'
                    '    return "stable";\n  }\n'
                    '  return "built-in";\n}\n'
                    'for (const s of nums) {\n'
                    '  console.log(`${s} ${choose(s)}`);\n}\n',
                    '  if (situation === 2) {\n'
                    '    return "insertion";\n  }',
                    [("1 2 3 4", "1 counting\n2 insertion\n3 stable\n4 built-in")],
                    hints=["Situation 2 is 'nearly sorted already' — which sort is adaptive?",
                           'Write if (situation === 2) { return "insertion"; }'],
                    difficulty="Easy"),
                _ex("tscourse-w24-ch-3", "The smallest few, without sorting everything",
                    "Run only k passes of selection sort and count what that saves.",
                    _SWAP +
                    'let cmp = 0;\n'
                    'function smallest(xs: number[], k: number): readonly number[] {\n'
                    '  for (let i = 0; i < k; i = i + 1) {\n'
                    '    let min = i;\n'
                    '    for (let j = i + 1; j < xs.length; j = j + 1) {\n'
                    '      cmp = cmp + 1;\n'
                    '      if ((xs[j] ?? 0) < (xs[min] ?? 0)) {\n'
                    '        min = j;\n      }\n    }\n'
                    '    swap(xs, i, min);\n  }\n'
                    '  return xs.slice(0, k);\n}\n'
                    'const xs = Array.from({ length: 16 }, (_, i) => 16 - i);\n'
                    'const top = smallest(xs, 3);\n'
                    'console.log(`${top.join(",")} cmp=${cmp} full=${(16 * 15) / 2}`);\n',
                    '  for (let i = 0; i < k; i = i + 1) {',
                    [("", "1,2,3 cmp=42 full=120")],
                    hints=["Selection sort places the smallest remaining value on every pass — so stop after k passes.",
                           "Write for (let i = 0; i < k; i = i + 1) {"],
                    difficulty="Medium"),
                _ex("tscourse-w24-ch-4", "The cheapest sort is the one you skip",
                    "Check in one pass whether the data is already in order.",
                    _NUMS +
                    'let inOrder = true;\n'
                    'for (let i = 1; i < nums.length; i = i + 1) {\n'
                    '  if ((nums[i] ?? 0) < (nums[i - 1] ?? 0)) {\n'
                    '    inOrder = false;\n  }\n}\n'
                    'console.log(inOrder ? `already sorted, ${nums.length - 1} checks` : "needs sorting");\n',
                    '  if ((nums[i] ?? 0) < (nums[i - 1] ?? 0)) {',
                    [("1 2 2 5", "already sorted, 3 checks"), ("2 1", "needs sorting")],
                    hints=["Out of order means some element is smaller than the one before it.",
                           "Equal neighbours are fine.",
                           "Write if ((nums[i] ?? 0) < (nums[i - 1] ?? 0)) {"],
                    difficulty="Easy"),
                _fix("tscourse-w24-ch-fix1", "Fix the leaderboard that reshuffled its ties",
                     "The rule is: lowest score first, and players with the same score stay in sign-up order. For `ann:2 bo:1 cy:2 dee:1` this prints `dee bo ann cy` — `dee` signed up after `bo` and now comes first. Quicksort is not stable, and no fix to its comparisons will make it so. Choose a sort that is.",
                     _WORDS + _ROWS +
                     'function swapRows(rs: Row[], i: number, j: number): void {\n'
                     '  const t = at(rs, i);\n'
                     '  rs[i] = at(rs, j);\n'
                     '  rs[j] = t;\n}\n'
                     'function quick(rs: Row[], lo: number, hi: number): void {\n'
                     '  if (lo >= hi) {\n'
                     '    return;\n  }\n'
                     '  const pivot = at(rs, hi).score;\n'
                     '  let i = lo;\n'
                     '  for (let j = lo; j < hi; j = j + 1) {\n'
                     '    if (at(rs, j).score < pivot) {\n'
                     '      swapRows(rs, i, j);\n'
                     '      i = i + 1;\n    }\n  }\n'
                     '  swapRows(rs, i, hi);\n'
                     '  quick(rs, lo, i - 1);\n'
                     '  quick(rs, i + 1, hi);\n}\n'
                     'const board = [...rows];\n'
                     'quick(board, 0, board.length - 1);\n'
                     'console.log(board.map((r) => r.name).join(" "));\n',
                     _WORDS + _ROWS +
                     'const board = [...rows].sort((a, b) => a.score - b.score);\n'
                     'console.log(board.map((r) => r.name).join(" "));\n',
                     [("ann:2 bo:1 cy:2 dee:1", "bo dee ann cy"), ("x:1 y:1 z:0", "z x y")],
                     hints=["The scores come out in order; it is the TIES that are wrong.",
                            "Stability is a property of the algorithm, not of the comparator.",
                            "The built-in sort is guaranteed stable: [...rows].sort((a, b) => a.score - b.score)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("\"Which sort would you use?\" is really a question about…",
                   ["your favourite", "the data: range, order, size, and whether ties matter", "speed only",
                    "memory only"], 1,
                   "Name the property that decided it."),
                _q("You can beat the built-in sort with a hand-written quicksort…",
                   ["usually", "almost never — it is a tuned hybrid of merge and insertion", "always",
                    "on strings"], 1,
                   "The exceptions are special data, not better code."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #24 — the sort bench",
        """
Five sorts, written by hand, run on the same input — each checked against the
built-in and each reporting what it cost.

Input: one line of non-negative integers.

```
5 1 4 1 3 9
```

```
Sorted:    1 1 3 4 5 9
Insertion: cmp  10
Selection: cmp  15
Merge:     cmp  10
Quick:     cmp  11
Counting:  ops  22
Agree:     yes
Fewest:    insertion
```

**The rows:**

* **Insertion**, **Selection**, **Merge**, **Quick** — each sorts its own copy and
  counts its comparisons: insertion one per test of the shift loop, selection one
  per inner step, merge one per step of the merge's main loop, quick one per step
  of the partition loop (Lomuto, last element as pivot).
* **Counting** reports `ops`, not `cmp`, because it never compares: one step per
  element to find the maximum, one per tally, and one per bucket walked from 0 to
  the maximum. A different currency — which is the point of printing it
  separately.
* **Agree** is `yes` when all five outputs equal the built-in's.
* **Fewest** names the comparison sort with the fewest comparisons — counting is
  not eligible — taking the earliest in the list order above on a tie.

**What makes it a rep:** the tests are chosen so each sort takes a turn at looking
good and looking bad. Already-sorted input makes insertion sort the cheapest and
last-element quicksort as bad as selection sort; reversed input makes insertion sort
as bad as it gets; and a single wide value makes counting sort walk a thousand
empty buckets.

Column format: the label and its colon padded to 11, then `cmp` or `ops`, a space,
and the count padded to 3. Empty input prints `Sorted:    (empty)`, zeros
throughout, `Agree:     yes` and `Fewest:    insertion`.
""",
        _ch("tscourse-w24-capstone", "Interview rep #24", "Hard",
            "Write five sorts, run each on the input, check each against the built-in, and report "
            "what each cost.",
            _FS +
            'const xs: readonly number[] = fs.readFileSync(0, "utf8")\n'
            '  .trim()\n'
            '  .split(/\\s+/)\n'
            '  .filter((s) => s !== "")\n'
            '  .map(Number);\n'
            'interface Run {\n'
            '  readonly out: readonly number[];\n'
            '  readonly cost: number;\n}\n'
            'function swap(ys: number[], i: number, j: number): void {\n'
            '  const t = ys[i] ?? 0;\n'
            '  ys[i] = ys[j] ?? 0;\n'
            '  ys[j] = t;\n}\n'
            'function insertion(input: readonly number[]): Run {\n'
            '  const ys = [...input];\n'
            '  let cost = 0;\n'
            '  const greater = (a: number, b: number): boolean => {\n'
            '    cost = cost + 1;\n'
            '    return a > b;\n'
            '  };\n'
            '  for (let i = 1; i < ys.length; i = i + 1) {\n'
            '    const v = ys[i] ?? 0;\n'
            '    let j = i - 1;\n'
            '    while (j >= 0 && greater(ys[j] ?? 0, v)) {\n'
            '      ys[j + 1] = ys[j] ?? 0;\n'
            '      j = j - 1;\n    }\n'
            '    ys[j + 1] = v;\n  }\n'
            '  return { out: ys, cost };\n}\n'
            'function selection(input: readonly number[]): Run {\n'
            '  const ys = [...input];\n'
            '  let cost = 0;\n'
            '  for (let i = 0; i < ys.length - 1; i = i + 1) {\n'
            '    let min = i;\n'
            '    for (let j = i + 1; j < ys.length; j = j + 1) {\n'
            '      cost = cost + 1;\n'
            '      if ((ys[j] ?? 0) < (ys[min] ?? 0)) {\n'
            '        min = j;\n      }\n    }\n'
            '    swap(ys, i, min);\n  }\n'
            '  return { out: ys, cost };\n}\n'
            'function mergeRun(input: readonly number[]): Run {\n'
            '  let cost = 0;\n'
            '  function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
            '    const out: number[] = [];\n'
            '    let i = 0;\n'
            '    let j = 0;\n'
            '    while (i < a.length && j < b.length) {\n'
            '      cost = cost + 1;\n'
            '      if ((a[i] ?? 0) <= (b[j] ?? 0)) {\n'
            '        out.push(a[i] ?? 0);\n'
            '        i = i + 1;\n'
            '      } else {\n'
            '        out.push(b[j] ?? 0);\n'
            '        j = j + 1;\n      }\n    }\n'
            '    return [...out, ...a.slice(i), ...b.slice(j)];\n  }\n'
            '  function sort(ys: readonly number[]): readonly number[] {\n'
            '    if (ys.length <= 1) {\n'
            '      return ys;\n    }\n'
            '    const mid = Math.floor(ys.length / 2);\n'
            '    return merge(sort(ys.slice(0, mid)), sort(ys.slice(mid)));\n  }\n'
            '  const out = sort(input);\n'
            '  return { out, cost };\n}\n'
            'function quickRun(input: readonly number[]): Run {\n'
            '  const ys = [...input];\n'
            '  let cost = 0;\n'
            '  function sort(lo: number, hi: number): void {\n'
            '    if (lo >= hi) {\n'
            '      return;\n    }\n'
            '    const pivot = ys[hi] ?? 0;\n'
            '    let i = lo;\n'
            '    for (let j = lo; j < hi; j = j + 1) {\n'
            '      cost = cost + 1;\n'
            '      if ((ys[j] ?? 0) < pivot) {\n'
            '        swap(ys, i, j);\n'
            '        i = i + 1;\n      }\n    }\n'
            '    swap(ys, i, hi);\n'
            '    sort(lo, i - 1);\n'
            '    sort(i + 1, hi);\n  }\n'
            '  sort(0, ys.length - 1);\n'
            '  return { out: ys, cost };\n}\n'
            'function countingRun(input: readonly number[]): Run {\n'
            '  let cost = 0;\n'
            '  let max = -1;\n'
            '  for (const x of input) {\n'
            '    max = Math.max(max, x);\n'
            '    cost = cost + 1;\n  }\n'
            '  const counts: number[] = new Array(max + 1).fill(0);\n'
            '  for (const x of input) {\n'
            '    counts[x] = (counts[x] ?? 0) + 1;\n'
            '    cost = cost + 1;\n  }\n'
            '  const out: number[] = [];\n'
            '  for (let v = 0; v <= max; v = v + 1) {\n'
            '    cost = cost + 1;\n'
            '    for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
            '      out.push(v);\n    }\n  }\n'
            '  return { out, cost };\n}\n'
            'function row(label: string, text: string): string {\n'
            '  return `${(label + ":").padEnd(11)}${text}`;\n}\n'
            'const want = [...xs].sort((a, b) => a - b).join(",");\n'
            'const compared: readonly [string, Run][] = [\n'
            '  ["Insertion", insertion(xs)],\n'
            '  ["Selection", selection(xs)],\n'
            '  ["Merge", mergeRun(xs)],\n'
            '  ["Quick", quickRun(xs)],\n'
            '];\n'
            'const counted = countingRun(xs);\n'
            'console.log(row("Sorted", xs.length === 0 ? "(empty)" : [...xs].sort((a, b) => a - b).join(" ")));\n'
            'for (const [label, run] of compared) {\n'
            '  console.log(row(label, `cmp ${String(run.cost).padStart(3)}`));\n}\n'
            'console.log(row("Counting", `ops ${String(counted.cost).padStart(3)}`));\n'
            'const agree = [...compared.map(([, run]) => run), counted].every((run) => run.out.join(",") === want);\n'
            'console.log(row("Agree", agree ? "yes" : "no"));\n'
            'let fewest = "insertion";\n'
            'let fewestCost = Number.MAX_SAFE_INTEGER;\n'
            'for (const [label, run] of compared) {\n'
            '  if (run.cost < fewestCost) {\n'
            '    fewest = label.toLowerCase();\n'
            '    fewestCost = run.cost;\n  }\n}\n'
            'console.log(row("Fewest", fewest));\n',
            'function insertion(input: readonly number[]): Run {\n'
            '  const ys = [...input];\n'
            '  let cost = 0;\n'
            '  const greater = (a: number, b: number): boolean => {\n'
            '    cost = cost + 1;\n'
            '    return a > b;\n'
            '  };\n'
            '  for (let i = 1; i < ys.length; i = i + 1) {\n'
            '    const v = ys[i] ?? 0;\n'
            '    let j = i - 1;\n'
            '    while (j >= 0 && greater(ys[j] ?? 0, v)) {\n'
            '      ys[j + 1] = ys[j] ?? 0;\n'
            '      j = j - 1;\n    }\n'
            '    ys[j + 1] = v;\n  }\n'
            '  return { out: ys, cost };\n}\n'
            'function selection(input: readonly number[]): Run {\n'
            '  const ys = [...input];\n'
            '  let cost = 0;\n'
            '  for (let i = 0; i < ys.length - 1; i = i + 1) {\n'
            '    let min = i;\n'
            '    for (let j = i + 1; j < ys.length; j = j + 1) {\n'
            '      cost = cost + 1;\n'
            '      if ((ys[j] ?? 0) < (ys[min] ?? 0)) {\n'
            '        min = j;\n      }\n    }\n'
            '    swap(ys, i, min);\n  }\n'
            '  return { out: ys, cost };\n}\n'
            'function mergeRun(input: readonly number[]): Run {\n'
            '  let cost = 0;\n'
            '  function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
            '    const out: number[] = [];\n'
            '    let i = 0;\n'
            '    let j = 0;\n'
            '    while (i < a.length && j < b.length) {\n'
            '      cost = cost + 1;\n'
            '      if ((a[i] ?? 0) <= (b[j] ?? 0)) {\n'
            '        out.push(a[i] ?? 0);\n'
            '        i = i + 1;\n'
            '      } else {\n'
            '        out.push(b[j] ?? 0);\n'
            '        j = j + 1;\n      }\n    }\n'
            '    return [...out, ...a.slice(i), ...b.slice(j)];\n  }\n'
            '  function sort(ys: readonly number[]): readonly number[] {\n'
            '    if (ys.length <= 1) {\n'
            '      return ys;\n    }\n'
            '    const mid = Math.floor(ys.length / 2);\n'
            '    return merge(sort(ys.slice(0, mid)), sort(ys.slice(mid)));\n  }\n'
            '  const out = sort(input);\n'
            '  return { out, cost };\n}\n'
            'function quickRun(input: readonly number[]): Run {\n'
            '  const ys = [...input];\n'
            '  let cost = 0;\n'
            '  function sort(lo: number, hi: number): void {\n'
            '    if (lo >= hi) {\n'
            '      return;\n    }\n'
            '    const pivot = ys[hi] ?? 0;\n'
            '    let i = lo;\n'
            '    for (let j = lo; j < hi; j = j + 1) {\n'
            '      cost = cost + 1;\n'
            '      if ((ys[j] ?? 0) < pivot) {\n'
            '        swap(ys, i, j);\n'
            '        i = i + 1;\n      }\n    }\n'
            '    swap(ys, i, hi);\n'
            '    sort(lo, i - 1);\n'
            '    sort(i + 1, hi);\n  }\n'
            '  sort(0, ys.length - 1);\n'
            '  return { out: ys, cost };\n}\n'
            'function countingRun(input: readonly number[]): Run {\n'
            '  let cost = 0;\n'
            '  let max = -1;\n'
            '  for (const x of input) {\n'
            '    max = Math.max(max, x);\n'
            '    cost = cost + 1;\n  }\n'
            '  const counts: number[] = new Array(max + 1).fill(0);\n'
            '  for (const x of input) {\n'
            '    counts[x] = (counts[x] ?? 0) + 1;\n'
            '    cost = cost + 1;\n  }\n'
            '  const out: number[] = [];\n'
            '  for (let v = 0; v <= max; v = v + 1) {\n'
            '    cost = cost + 1;\n'
            '    for (let c = 0; c < (counts[v] ?? 0); c = c + 1) {\n'
            '      out.push(v);\n    }\n  }\n'
            '  return { out, cost };\n}',
            [("5 1 4 1 3 9",
              "Sorted:    1 1 3 4 5 9\nInsertion: cmp  10\nSelection: cmp  15\nMerge:     cmp  10\n"
              "Quick:     cmp  11\nCounting:  ops  22\nAgree:     yes\nFewest:    insertion"),
             ("1 2 3 4 5 6 7 8",
              "Sorted:    1 2 3 4 5 6 7 8\nInsertion: cmp   7\nSelection: cmp  28\nMerge:     cmp  12\n"
              "Quick:     cmp  28\nCounting:  ops  25\nAgree:     yes\nFewest:    insertion"),
             ("8 7 6 5 4 3 2 1",
              "Sorted:    1 2 3 4 5 6 7 8\nInsertion: cmp  28\nSelection: cmp  28\nMerge:     cmp  12\n"
              "Quick:     cmp  28\nCounting:  ops  25\nAgree:     yes\nFewest:    merge"),
             ("3 1000 2",
              "Sorted:    2 3 1000\nInsertion: cmp   3\nSelection: cmp   3\nMerge:     cmp   3\n"
              "Quick:     cmp   3\nCounting:  ops 1007\nAgree:     yes\nFewest:    insertion"),
             ("", "Sorted:    (empty)\nInsertion: cmp   0\nSelection: cmp   0\nMerge:     cmp   0\n"
              "Quick:     cmp   0\nCounting:  ops   0\nAgree:     yes\nFewest:    insertion")],
            hints=["Each sort works on its own copy — `[...input]` — so they all see the same data.",
                   "Count inside the algorithm as it runs, never from a formula: the tests are chosen so a formula gets at least one wrong.",
                   "For insertion sort, route the shift-loop test through a small counting function; `&&` then skips the count when j reaches -1.",
                   "Counting sort's cost has three parts: the max scan, the tallies, and every bucket from 0 to max.",
                   "Fewest: walk the four comparison sorts in order and replace only on a STRICTLY smaller count, so a tie keeps the earlier one.",
                   "An empty input has no maximum: start `max` at -1 and the bucket walk does nothing."]),
        example_io="Sorted:    1 1 3 4 5 9\nInsertion: cmp  10\nSelection: cmp  15\nMerge:     cmp  10\nQuick:     cmp  11\nCounting:  ops  22\nAgree:     yes\nFewest:    insertion",
        rubric=["five sorts written by hand, each on its own copy of the input",
                "every count measured as the algorithm runs, never computed from a formula",
                "merge sort's base case is `length <= 1`, and its merge takes from the left on a tie",
                "quicksort recurses on `p - 1` and `p + 1`, never on the pivot again",
                "counting sort reports its cost separately, as ops rather than comparisons",
                "every output is checked against the built-in sort",
                "a tie for fewest keeps the earlier sort",
                "no index access is asserted with `!`",
                "empty input prints every row with zeros"],
        stretch=_ch("tscourse-w24-capstone-stretch", "Interview rep #24 (stretch)", "Hard",
                    "Bench **stability** instead of cost. Each input line is `name score`. Sort the rows by "
                    "score, ascending, with insertion sort, merge sort and quicksort (Lomuto, last element as "
                    "pivot), and for each print the names in the order it produced followed by `ties kept` "
                    "if every pair of equal scores is still in input order, or `ties reordered` if any pair "
                    "is not. Label padded to 11 as before, then the names separated by spaces, two spaces, "
                    "and the verdict.",
                    _FS +
                    'interface Row {\n'
                    '  readonly name: string;\n'
                    '  readonly score: number;\n'
                    '  readonly at: number;\n}\n'
                    'const rows: readonly Row[] = fs.readFileSync(0, "utf8")\n'
                    '  .split("\\n")\n'
                    '  .map((l) => l.trim())\n'
                    '  .filter((l) => l !== "")\n'
                    '  .map((l, at) => {\n'
                    '    const [name, score] = l.split(/\\s+/);\n'
                    '    return { name: name ?? "", score: Number(score ?? "0"), at };\n'
                    '  });\n'
                    'function pick(rs: readonly Row[], i: number): Row {\n'
                    '  return rs[i] ?? { name: "", score: 0, at: 0 };\n}\n'
                    'function insertion(input: readonly Row[]): readonly Row[] {\n'
                    '  const rs = [...input];\n'
                    '  for (let i = 1; i < rs.length; i = i + 1) {\n'
                    '    const v = pick(rs, i);\n'
                    '    let j = i - 1;\n'
                    '    while (j >= 0 && pick(rs, j).score > v.score) {\n'
                    '      rs[j + 1] = pick(rs, j);\n'
                    '      j = j - 1;\n    }\n'
                    '    rs[j + 1] = v;\n  }\n'
                    '  return rs;\n}\n'
                    'function mergeSort(rs: readonly Row[]): readonly Row[] {\n'
                    '  if (rs.length <= 1) {\n'
                    '    return rs;\n  }\n'
                    '  const mid = Math.floor(rs.length / 2);\n'
                    '  const a = mergeSort(rs.slice(0, mid));\n'
                    '  const b = mergeSort(rs.slice(mid));\n'
                    '  const out: Row[] = [];\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
                    '    if (pick(a, i).score <= pick(b, j).score) {\n'
                    '      out.push(pick(a, i));\n'
                    '      i = i + 1;\n'
                    '    } else {\n'
                    '      out.push(pick(b, j));\n'
                    '      j = j + 1;\n    }\n  }\n'
                    '  return [...out, ...a.slice(i), ...b.slice(j)];\n}\n'
                    'function quick(input: readonly Row[]): readonly Row[] {\n'
                    '  const rs = [...input];\n'
                    '  function swap(i: number, j: number): void {\n'
                    '    const t = pick(rs, i);\n'
                    '    rs[i] = pick(rs, j);\n'
                    '    rs[j] = t;\n  }\n'
                    '  function sort(lo: number, hi: number): void {\n'
                    '    if (lo >= hi) {\n'
                    '      return;\n    }\n'
                    '    const pivot = pick(rs, hi).score;\n'
                    '    let i = lo;\n'
                    '    for (let j = lo; j < hi; j = j + 1) {\n'
                    '      if (pick(rs, j).score < pivot) {\n'
                    '        swap(i, j);\n'
                    '        i = i + 1;\n      }\n    }\n'
                    '    swap(i, hi);\n'
                    '    sort(lo, i - 1);\n'
                    '    sort(i + 1, hi);\n  }\n'
                    '  sort(0, rs.length - 1);\n'
                    '  return rs;\n}\n'
                    'function tiesKept(rs: readonly Row[]): boolean {\n'
                    '  for (let i = 1; i < rs.length; i = i + 1) {\n'
                    '    const a = pick(rs, i - 1);\n'
                    '    const b = pick(rs, i);\n'
                    '    if (a.score === b.score && a.at > b.at) {\n'
                    '      return false;\n    }\n  }\n'
                    '  return true;\n}\n'
                    'const benches: readonly [string, readonly Row[]][] = [\n'
                    '  ["Insertion", insertion(rows)],\n'
                    '  ["Merge", mergeSort(rows)],\n'
                    '  ["Quick", quick(rows)],\n'
                    '];\n'
                    'for (const [label, sorted] of benches) {\n'
                    '  const names = sorted.map((r) => r.name).join(" ");\n'
                    '  const verdict = tiesKept(sorted) ? "ties kept" : "ties reordered";\n'
                    '  console.log(`${(label + ":").padEnd(11)}${names}  ${verdict}`);\n}\n',
                    'function tiesKept(rs: readonly Row[]): boolean {\n'
                    '  for (let i = 1; i < rs.length; i = i + 1) {\n'
                    '    const a = pick(rs, i - 1);\n'
                    '    const b = pick(rs, i);\n'
                    '    if (a.score === b.score && a.at > b.at) {\n'
                    '      return false;\n    }\n  }\n'
                    '  return true;\n}',
                    [("ann 2\nbo 1\ncy 2\ndee 1",
                      "Insertion: bo dee ann cy  ties kept\nMerge:     bo dee ann cy  ties kept\n"
                      "Quick:     dee bo ann cy  ties reordered"),
                     ("a 1\nb 2",
                      "Insertion: a b  ties kept\nMerge:     a b  ties kept\nQuick:     a b  ties kept"),
                     ("solo 5",
                      "Insertion: solo  ties kept\nMerge:     solo  ties kept\nQuick:     solo  ties kept")],
                    hints=["Record each row's input position (`at`) when you parse it — stability is a statement about positions, and names can repeat.",
                           "Only NEIGHBOURS need checking: if every adjacent tie is in input order, all ties are.",
                           "`ties kept` on one input does not prove a sort stable — the second test shows quicksort keeping its ties. Stability is a guarantee; only its absence can be shown by example.",
                           "Label padded to 11, names, TWO spaces, verdict."]),
    ),
))
