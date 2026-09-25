# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 22 — searching & two pointers.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# IT DEEPENS BINARY SEARCH RATHER THAN INTRODUCING IT. Week 21 already built one
# and counted it (`w21-classes`: 4, 5, 6 … 11 steps for n = 8 … 1024), and its
# `fix` converted a linear scan over sorted data into one. So lesson 2 opens on
# "you have written this; here is why it is so easy to get wrong", and the week's
# real content is the three things week 21 did not cover:
#
#   * the two BOUNDS — first index >= x and first index > x — which is what turns
#     binary search from "find it" into a tool. Almost every real use is a bound.
#   * binary search ON THE ANSWER, where the array does not exist and the thing
#     being halved is a candidate answer with a monotonic predicate.
#   * two pointers, which is the other half of "the input is sorted, so you do not
#     have to look at everything".
#
# ---------------------------------------------------------------------------
# THE ROADMAP'S NOTE FOR THIS MONTH, now that week 21 is the month's foundation:
# each of weeks 22-24 should report an OPERATION COUNT beside its answer wherever
# the technique's whole point is being cheaper than the obvious version. This week
# does that in five exercises and in the capstone, because "two pointers is O(n)"
# is a claim, and `steps=4` next to `pairs=15` is the evidence. Nothing here
# measures elapsed time (week 17's rule, unchanged).
#
# ---------------------------------------------------------------------------
# THE OFF-BY-ONE, WHICH IS THE WEEK'S ONE GENUINELY TRICKY THING.
#
# Two loop shapes, and they are not interchangeable:
#
#   INCLUSIVE hi, for "find the value"          EXCLUSIVE hi, for a BOUND
#     let hi = xs.length - 1;                     let hi = xs.length;
#     while (lo <= hi) { … }                      while (lo < hi) { … }
#     hi = mid - 1;                               hi = mid;
#
# Mixing them is the bug, and it is silent: `while (lo < hi)` with an inclusive
# `hi` never examines the last element, so `search([1,2,3], 3)` returns -1 and
# `search([1], 1)` returns -1 — both verified, and both shipped as one `fix`,
# because a single-element array failing is the fastest way to recognise it.
#
# Mid-point overflow (`(lo + hi) / 2` exceeding the integer range) is a real bug
# in C and Java and is NOT one here — JavaScript numbers are doubles, and a
# `length` can never get near 2^53. The lesson says so explicitly rather than
# repeating advice that does not apply, and then explains where the
# `lo + (hi - lo) / 2` idiom people copy actually comes from.
# ---------------------------------------------------------------------------

# The sorted-numbers prefix this week uses everywhere. Sorting the input rather
# than trusting it is deliberate: every exercise in the week depends on order, and
# a program that assumes sortedness without establishing it teaches the wrong
# instinct.
_SORTED = _FS + (
    'const nums: readonly number[] = fs\n'
    '  .readFileSync(0, "utf8")\n'
    '  .trim()\n'
    '  .split(" ")\n'
    '  .filter((s) => s !== "")\n'
    '  .map(Number)\n'
    '  .sort((a, b) => a - b);\n'
)

_LOWER = (
    'function lowerBound(xs: readonly number[], target: number): number {\n'
    '  let lo = 0;\n'
    '  let hi = xs.length;\n'
    '  while (lo < hi) {\n'
    '    const mid = Math.floor((lo + hi) / 2);\n'
    '    if ((xs[mid] ?? 0) < target) {\n'
    '      lo = mid + 1;\n'
    '    } else {\n'
    '      hi = mid;\n    }\n  }\n'
    '  return lo;\n}\n'
)

_UPPER = (
    'function upperBound(xs: readonly number[], target: number): number {\n'
    '  let lo = 0;\n'
    '  let hi = xs.length;\n'
    '  while (lo < hi) {\n'
    '    const mid = Math.floor((lo + hi) / 2);\n'
    '    if ((xs[mid] ?? 0) <= target) {\n'
    '      lo = mid + 1;\n'
    '    } else {\n'
    '      hi = mid;\n    }\n  }\n'
    '  return lo;\n}\n'
)

# --- Week 22 --------------------------------------------------------------
_WEEKS.append(_week(
    22, 6, _M6,
    "Searching & Two Pointers",
    "When the input is sorted you do not have to look at all of it. Binary search properly — including the two bounds and searching on the answer — and the two-pointer sweeps that replace a nested loop.",
    """
Sorted input is a gift, and this week is about spending it. Two techniques, and
both turn an O(n²) or an O(n) into something smaller:

* **Binary search** — halve the search space every step. O(log n).
* **Two pointers** — one sweep with two indices instead of a nested loop. O(n).

## You have already written one of them

Week 21 built a binary search and counted it: 11 steps for 1,024 items, and one
more for every doubling. So this week does not introduce it — it covers the three
things that make it actually useful:

1. **The bounds.** "Where is this value?" is the *least* common question. The real
   ones are "where would it go?", "where does this range start?" and "how many are
   there?" — and all three are a **lower bound** or an **upper bound**.
2. **Searching on the answer.** There is no array. You are halving a range of
   *candidate answers*, and the test is a predicate that flips from false to true
   exactly once.
3. **The off-by-one.** Two loop shapes that look the same and are not. This is the
   one genuinely tricky thing in the week, and a single-element array is how you
   catch it.

## Two pointers

```ts
let lo = 0;
let hi = xs.length - 1;
while (lo < hi) {
  const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);
  if (sum === target) { … }
  else if (sum < target) { lo = lo + 1; }   // need more — the only way is right
  else { hi = hi - 1; }                      // need less — the only way is left
}
```

Every step eliminates one element **for good**, which is why it is one pass. The
whole argument rests on the array being sorted: that is what makes "I need a bigger
number, so I must move right" true.

## Counted, as the month requires

Where the point of a technique is that it is cheaper, the exercises print the step
count next to the answer. "Two pointers is O(n)" is a claim; `steps=4` beside
`pairs=15` is the evidence, and it is exactly what week 21 taught you to look at.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Say when a linear scan is the right answer",
        "Write a correct binary search, and say which loop shape you are using",
        "Recognise the off-by-one from a single-element array",
        "Say why mid-point overflow is a real bug in Java and not in TypeScript",
        "Write a lower bound and an upper bound, and say what each returns for a missing value",
        "Count occurrences, find an insertion point and answer a range query from the two bounds",
        "Recognise a problem as a binary search on the answer, and name its monotonic predicate",
        "Sweep a sorted array with two pointers from both ends",
        "Use a read pointer and a write pointer to filter in place",
        "Merge two sorted arrays in one pass",
        "Sort and then sweep, to turn an O(n³) triple loop into O(n²)",
        "Report the step count beside an answer, and say what it proves",
    ],
    why="Binary search is the most-asked and most-often-wrong interview question there is — the bug is never the idea, it is always the boundary. And two pointers is the single highest-yield pattern in the whole set: a startling number of array problems that look quadratic are one sorted sweep, and recognising that is worth more than any individual algorithm.",
    est_minutes=480,
    glossary=[
        _gloss("linear search", "Look at each element. O(n), and the right answer on unsorted or tiny input."),
        _gloss("binary search", "Halve the range each step. O(log n), and requires sorted input."),
        _gloss("invariant", "What stays true every iteration: the answer, if any, is inside [lo, hi]."),
        _gloss("inclusive hi", "`hi = length - 1` with `lo <= hi` and `hi = mid - 1`. For finding a value."),
        _gloss("exclusive hi", "`hi = length` with `lo < hi` and `hi = mid`. For finding a bound."),
        _gloss("lower bound", "The first index whose value is >= target. Where the value starts, or would go."),
        _gloss("upper bound", "The first index whose value is > target. One past where it ends."),
        _gloss("occurrence count", "upperBound - lowerBound. No scanning."),
        _gloss("insertion point", "The lower bound: insert there and the array stays sorted."),
        _gloss("search on the answer", "Binary search over candidate answers rather than over an array."),
        _gloss("monotonic predicate", "A test that is false, false, …, true, true. What makes the answer searchable."),
        _gloss("feasibility check", "The predicate itself: \"can it be done with this budget?\""),
        _gloss("two pointers", "Two indices sweeping one array, each moving only one way."),
        _gloss("opposite ends", "lo from the start, hi from the end, converging. For pair sums and palindromes."),
        _gloss("same direction", "A read pointer and a write pointer. For filtering in place."),
        _gloss("read/write pointers", "Read visits every element; write marks where the next kept one goes."),
        _gloss("in-place filter", "Compacting the kept elements to the front and returning the new length."),
        _gloss("merge", "Two sorted inputs, one output, one pass — the heart of merge sort (week 24)."),
        _gloss("sort then sweep", "Sorting first to make a two-pointer sweep possible. O(n log n) well spent."),
        _gloss("duplicate skipping", "Advancing past equal values so a solution set has no repeats."),
    ],
    cheatsheet="""
```ts
// ---- the two loop shapes. DO NOT MIX THEM. -----------------------------
// finding a VALUE — inclusive hi
let lo = 0, hi = xs.length - 1;
while (lo <= hi) {                       // <=
  const mid = Math.floor((lo + hi) / 2);
  const v = xs[mid] ?? 0;
  if (v === target) { return mid; }
  if (v < target) { lo = mid + 1; } else { hi = mid - 1; }   // mid - 1
}
return -1;

// finding a BOUND — exclusive hi
let lo = 0, hi = xs.length;              // length, not length - 1
while (lo < hi) {                        // <
  const mid = Math.floor((lo + hi) / 2);
  if ((xs[mid] ?? 0) < target) { lo = mid + 1; } else { hi = mid; }   // mid
}
return lo;                                // the LOWER bound

// `<=` in that test instead of `<` gives the UPPER bound. That is the only change.

// ---- what the bounds buy you -------------------------------------------
const first = lowerBound(xs, x);            // first index >= x
const past  = upperBound(xs, x);            // first index > x
past - first;                                // how many x there are
xs[first] === x;                             // is x present at all
lowerBound(xs, x);                           // where to insert and stay sorted
upperBound(xs, hiVal) - lowerBound(xs, loVal);   // how many in [loVal, hiVal]

// ---- search on the ANSWER ---------------------------------------------
// the predicate must be monotonic: false … false true … true
let lo = 1, hi = total;
while (lo < hi) {
  const mid = Math.floor((lo + hi) / 2);
  if (feasible(mid)) { hi = mid; } else { lo = mid + 1; }
}
return lo;                                   // the smallest feasible answer

// ---- two pointers, opposite ends -------------------------------------
let lo = 0, hi = xs.length - 1;
while (lo < hi) {
  const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);
  if (sum === target) { return [lo, hi]; }
  if (sum < target) { lo = lo + 1; } else { hi = hi - 1; }
}

// ---- two pointers, same direction: read and write ---------------------
let write = 1;
for (let read = 1; read < xs.length; read = read + 1) {
  if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {
    xs[write] = xs[read] ?? 0;
    write = write + 1;
  }
}
return write;                                // the new length; O(1) space

// ---- merge two sorted arrays ------------------------------------------
while (i < a.length && j < b.length) {
  if ((a[i] ?? 0) <= (b[j] ?? 0)) { out.push(a[i] ?? 0); i = i + 1; }
  else { out.push(b[j] ?? 0); j = j + 1; }
}
while (i < a.length) { out.push(a[i] ?? 0); i = i + 1; }    // drain both tails
while (j < b.length) { out.push(b[j] ?? 0); j = j + 1; }

// ---- sort, then sweep: triples in O(n²) ------------------------------
const xs = [...nums].sort((a, b) => a - b);
for (let i = 0; i < xs.length - 2; i = i + 1) {
  if (i > 0 && xs[i] === xs[i - 1]) { continue; }    // skip duplicate anchors
  let lo = i + 1, hi = xs.length - 1;
  while (lo < hi) { /* the two-pointer sweep above */ }
}
```
""",
    self_check=[
        "Can you say when a linear scan beats a binary search?",
        "Can you write both loop shapes from memory and say which is for what?",
        "Can you say what `while (lo < hi)` with `hi = length - 1` does to a one-element array?",
        "Can you say why mid-point overflow is not a TypeScript problem?",
        "Can you write a lower bound, and say what it returns for a value that is absent?",
        "Can you count occurrences of a value without scanning?",
        "Can you say what makes a predicate monotonic, and why that is required?",
        "Can you explain why a two-pointer sweep needs the array sorted?",
        "Can you filter an array in place with a read and a write pointer?",
        "Can you merge two sorted arrays, including both tails?",
        "Can you say why sorting first can make a problem cheaper overall?",
        "Can you say what a step count printed beside an answer proves?",
    ],
    review=[
        _q("Binary search requires…",
           ["a Map", "sorted input", "unique values", "recursion"], 1,
           "Order is what makes halving valid."),
        _q("The loop shape for finding a VALUE is…",
           ["lo < hi with hi = length", "lo <= hi with hi = length - 1", "either", "lo < hi with hi = length - 1"], 1,
           "Inclusive hi, and `hi = mid - 1`."),
        _q("The loop shape for a BOUND is…",
           ["lo <= hi with hi = length - 1", "lo < hi with hi = length", "either",
            "lo <= hi with hi = length"], 1,
           "Exclusive hi, and `hi = mid`."),
        _q("`while (lo < hi)` with `hi = length - 1` on a one-element array…",
           ["works", "never enters the loop, so it misses the only element", "crashes",
            "returns 0"], 1,
           "The fastest way to catch the bug."),
        _q("Mid-point overflow is a real bug in…",
           ["TypeScript", "Java and C, where lo + hi can exceed the integer range", "every language",
            "no language"], 1,
           "JavaScript numbers are doubles."),
        _q("A lower bound returns…",
           ["the index of the value", "the first index whose value is >= target", "-1 if absent",
            "the last index"], 1,
           "Which is also the insertion point."),
        _q("The number of occurrences of x is…",
           ["a scan", "upperBound - lowerBound", "lowerBound", "1"], 1,
           "Two searches, no scanning."),
        _q("A predicate suitable for searching on the answer must be…",
           ["fast", "monotonic — false … false true … true", "total", "pure"], 1,
           "Otherwise halving is invalid."),
        _q("A two-pointer sweep from both ends is O(n) because…",
           ["it is sorted", "each step eliminates one element permanently", "of the while",
            "of the sum"], 1,
           "The pointers only ever move towards each other."),
        _q("`if (sum < target) lo = lo + 1` is right because…",
           ["it is arbitrary", "a bigger sum can only come from a bigger left value, and the array is sorted",
            "hi is fixed", "of the loop"], 1,
           "The whole argument rests on order."),
        _q("A read pointer and a write pointer give you…",
           ["two passes", "an in-place filter, in O(1) extra space", "a merge", "a sort"], 1,
           "The write index is where the next kept element goes."),
        _q("Merging two sorted arrays needs…",
           ["one loop", "one loop plus a drain for each tail", "a sort", "recursion"], 1,
           "Forgetting a tail is the classic bug."),
        _q("Sorting first to enable a sweep costs O(n log n) and is…",
           ["never worth it", "usually a bargain against an O(n²) or O(n³) alternative",
            "free", "O(n)"], 1,
           "Week 21's table says why."),
        _q("Skipping duplicate anchors in a triple sweep prevents…",
           ["a crash", "repeated solutions in the output", "O(n³)", "an overflow"], 1,
           "Which is what makes the answer a set."),
    ],
    milestone="Interview rep #22 — a search toolkit. One sorted ledger and five different questions about it, each answered in O(log n) with the step count printed beside the answer: is this amount present, where would it go, how many are there, how many fall in a range, and which is nearest. Five questions, one algorithm, four boundary conditions that each break it differently.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w22-linear", "When a scan is the right answer",
            "Before the clever version, the honest one.",
            """
```ts
for (let i = 0; i < xs.length; i = i + 1) {
  if ((xs[i] ?? 0) === target) { return i; }
}
return -1;
```

O(n), no preconditions, impossible to get wrong. Reach for it when:

* **the input is not sorted**, and sorting it would cost more than the scan
  (sorting is O(n log n); one scan is O(n));
* **you search once.** Sorting to search once is a loss; sorting to search a
  thousand times is a bargain, and that arithmetic is the whole decision;
* **n is small.** Twelve months, seven days, a handful of tags: a scan is clearer
  and the difference is unmeasurable (week 21's last lesson);
* **you need every match**, not one — a scan is already optimal for that.

## Early exit is the only optimisation that matters

```ts
if ((xs[i] ?? 0) === target) { return i; }   // stop at the first hit
```

Best case O(1), worst case still O(n). Week 21 counted exactly this: searching for
the first element takes one step, searching for an absent one takes n.

## Two scans people write by accident

```ts
if (xs.includes(target)) { return xs.indexOf(target); }   // TWO scans
const i = xs.indexOf(target);                              // one
if (i >= 0) { … }
```

and:

```ts
const found = xs.filter((x) => x === target);   // scans ALL of it, allocates
const found = xs.find((x) => x === target);     // stops at the first
```

Neither is a complexity change — both are O(n) — but both do twice the work for no
reason, and `filter` also allocates. Week 21's habit applies: read what the call
actually does.

## The decision, in one line

> **Sorted, or searched more than a few times: binary search. Otherwise: scan.**

The rest of this week is what to do once you have decided.

> ⚠️ **Common mistakes:** binary searching an unsorted array (it silently returns
> the wrong answer); sorting to search once; and calling `includes` then `indexOf`.
""",
            warmup=[
                _q("A linear search is the right choice when…",
                   ["always", "the input is unsorted and searched once, or n is small",
                    "never", "the input is sorted"], 1,
                   "Sorting to search once is a loss."),
                _q("Early exit changes…",
                   ["the worst case", "the best case only", "both", "neither"], 1,
                   "Worst case is still O(n)."),
                _q("`xs.includes(t)` then `xs.indexOf(t)` is…",
                   ["one scan", "two scans for one answer", "O(1)", "required"], 1,
                   "Use indexOf and test the result."),
                _q("Binary searching an unsorted array…",
                   ["throws", "silently returns the wrong answer", "works", "is O(n)"], 1,
                   "Which is why the precondition matters."),
            ],
            exercises=[
                _ex("tscourse-w22-ln-1", "Scan with an early exit",
                    "Return as soon as the target is found, and report how many steps it took.",
                    _NUMS +
                    'function find(xs: readonly number[], target: number): string {\n'
                    '  let steps = 0;\n'
                    '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                    '    steps = steps + 1;\n'
                    '    if ((xs[i] ?? 0) === target) {\n'
                    '      return `found at ${i} steps=${steps}`;\n    }\n  }\n'
                    '  return `absent steps=${steps}`;\n}\n'
                    'console.log(find(nums, 3));\n',
                    '      return `found at ${i} steps=${steps}`;',
                    [("5 3 9", "found at 1 steps=2"), ("1 2", "absent steps=2")],
                    hints=["Return the index and the count at the moment of the match.",
                           "Write return `found at ${i} steps=${steps}`;"],
                    difficulty="Easy"),
                _ex("tscourse-w22-ln-2", "Best case and worst case",
                    "Search for the first element and then for an absent one, and print both counts.",
                    'function steps(xs: readonly number[], target: number): number {\n'
                    '  let n = 0;\n'
                    '  for (const x of xs) {\n'
                    '    n = n + 1;\n'
                    '    if (x === target) {\n'
                    '      return n;\n    }\n  }\n'
                    '  return n;\n}\n'
                    'const xs = [1, 2, 3, 4, 5, 6, 7, 8];\n'
                    'console.log(`best=${steps(xs, 1)} worst=${steps(xs, 99)}`);\n',
                    'console.log(`best=${steps(xs, 1)} worst=${steps(xs, 99)}`);',
                    [("", "best=1 worst=8")],
                    hints=["The first element, then something that is not there.",
                           "Write console.log(`best=${steps(xs, 1)} worst=${steps(xs, 99)}`);"],
                    difficulty="Easy"),
                _ex("tscourse-w22-ln-3", "One scan, not two",
                    "Get the index once and test it, rather than asking twice.",
                    _NUMS +
                    'const i = nums.indexOf(3);\n'
                    'console.log(i >= 0 ? `at ${i}` : "absent");\n',
                    'const i = nums.indexOf(3);', [("5 3 9", "at 1"), ("1 2", "absent")],
                    hints=["`indexOf` already answers both questions.",
                           "Write const i = nums.indexOf(3);"],
                    difficulty="Easy"),
                _ex("tscourse-w22-ln-4", "`find`, not `filter`",
                    "Stop at the first match instead of collecting every one.",
                    _NUMS +
                    'const first = nums.find((n) => n > 3);\n'
                    'console.log(first ?? -1);\n',
                    'const first = nums.find((n) => n > 3);',
                    [("1 5 7", "5"), ("1 2", "-1")],
                    hints=["The method that returns one element and stops.",
                           "Write const first = nums.find((n) => n > 3);"],
                    difficulty="Easy"),
                _ex("tscourse-w22-ln-5", "The sort-once arithmetic",
                    "Report the total cost of scanning k times against sorting once and binary searching k times.",
                    _NUMS +
                    'const n = 1024;\n'
                    'const logN = 10;\n'
                    'const k = nums[0] ?? 1;\n'
                    'const scanning = k * n;\n'
                    'const sorting = n * logN + k * logN;\n'
                    'console.log(`k=${k} scan=${scanning} sortThenSearch=${sorting} better=${scanning < sorting ? "scan" : "sort"}`);\n',
                    'const sorting = n * logN + k * logN;',
                    [("1", "k=1 scan=1024 sortThenSearch=10250 better=scan"),
                     ("100", "k=100 scan=102400 sortThenSearch=11240 better=sort")],
                    hints=["Sorting is paid once; each search after it is logarithmic.",
                           "Write const sorting = n * logN + k * logN;"],
                    difficulty="Medium"),
                _fix("tscourse-w22-ln-fix1", "Fix the binary search on unsorted input",
                     "This binary searches an array nobody sorted, and reports `absent` for a value that is right there. The algorithm is fine; its precondition is not.",
                     _FS +
                     'const nums: readonly number[] = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                     'function has(xs: readonly number[], target: number): boolean {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  while (lo <= hi) {\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    const v = xs[mid] ?? 0;\n'
                     '    if (v === target) {\n'
                     '      return true;\n    }\n'
                     '    if (v < target) {\n'
                     '      lo = mid + 1;\n'
                     '    } else {\n'
                     '      hi = mid - 1;\n    }\n  }\n'
                     '  return false;\n}\n'
                     'console.log(has(nums, 1));\n',
                     _FS +
                     'const nums: readonly number[] = fs\n'
                     '  .readFileSync(0, "utf8")\n'
                     '  .trim()\n'
                     '  .split(" ")\n'
                     '  .map(Number)\n'
                     '  .sort((a, b) => a - b);\n'
                     'function has(xs: readonly number[], target: number): boolean {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  while (lo <= hi) {\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    const v = xs[mid] ?? 0;\n'
                     '    if (v === target) {\n'
                     '      return true;\n    }\n'
                     '    if (v < target) {\n'
                     '      lo = mid + 1;\n'
                     '    } else {\n'
                     '      hi = mid - 1;\n    }\n  }\n'
                     '  return false;\n}\n'
                     'console.log(has(nums, 1));\n',
                     [("9 5 1", "true"), ("3 2", "false")],
                     hints=["Halving is only valid if everything left of the midpoint is smaller.",
                            "Nothing in the program establishes that.",
                            "Sort the input as it is read, with a numeric comparator."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`filter` instead of `find` costs…",
                   ["a complexity class", "the rest of the scan, plus an allocation", "nothing",
                    "a sort"], 1,
                   "Both are O(n); one does twice the work."),
                _q("The decision rule is…",
                   ["always binary search", "sorted or searched many times: binary search; otherwise scan",
                    "always scan", "it depends on n only"], 1,
                   "And the arithmetic is in exercise 5."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w22-binary", "Binary search, and the boundary that breaks it",
            "You wrote one in week 21. Here is why it is the most-failed question there is.",
            """
The idea is trivial: look at the middle, throw away the half that cannot contain
the answer, repeat. The bug is never the idea. It is always the boundary.

## The shape for finding a value

```ts
function search(xs: readonly number[], target: number): number {
  let lo = 0;
  let hi = xs.length - 1;          // INCLUSIVE: hi is a real index
  while (lo <= hi) {                // <=  : a range of one is still a range
    const mid = Math.floor((lo + hi) / 2);
    const v = xs[mid] ?? 0;
    if (v === target) { return mid; }
    if (v < target) { lo = mid + 1; }
    else { hi = mid - 1; }           // mid - 1: mid is ruled out
  }
  return -1;
}
```

Three things have to agree, and they are the whole lesson:

| `hi` starts at | loop test | shrink with |
|---|---|---|
| `length - 1` (inclusive) | `lo <= hi` | `hi = mid - 1` |
| `length` (exclusive) | `lo < hi` | `hi = mid` |

**Pick a row and stay in it.** Every binary search bug is a value from one row
used with the other.

## The invariant

> If the target is in the array at all, it is somewhere in `[lo, hi]`.

True before the loop, and each branch preserves it: if `xs[mid] < target` then the
target cannot be at `mid` or to its left, so `lo = mid + 1` is safe. Being able to
say that sentence is what lets you write the thing without guessing.

## The bug, and how to catch it in five seconds

```ts
while (lo < hi) { … hi = mid - 1; }    // ❌ mixed rows
```

With an inclusive `hi`, `lo < hi` exits while one element is still unexamined:

```
search([1, 2, 3], 3)  ->  -1      // should be 2
search([1], 1)        ->  -1      // should be 0
```

**A one-element array is the test.** If your binary search cannot find the only
element, the loop condition is wrong. It is the cheapest test in programming and
almost nobody writes it.

## Termination

The range must shrink every iteration, or the loop hangs. `lo = mid + 1` and
`hi = mid - 1` both exclude `mid`, so it always does. In the bound shape,
`hi = mid` does *not* exclude `mid` — which is fine there only because that loop
tests `lo < hi`, so `mid` is always strictly less than `hi` and the range still
shrinks. If you ever write `lo = mid` you have written an infinite loop.

## Mid-point overflow: not your problem here

You will see this:

```ts
const mid = lo + Math.floor((hi - lo) / 2);
```

In Java or C, `lo + hi` can exceed the maximum `int` and go negative — a famous bug
that sat in the JDK's own binary search for nine years. **In TypeScript this cannot
happen**: numbers are doubles, exact to 2^53, and an array cannot be longer than
2^32. `(lo + hi) / 2` is correct here.

The idiom is still worth recognising, because you will read it constantly and
because if you write the same algorithm in another language it becomes real again.

> ⚠️ **Common mistakes:** mixing the two rows; not testing a one-element array; and
> `lo = mid` instead of `lo = mid + 1`, which hangs.
""",
            warmup=[
                _q("With `hi = length - 1`, the loop test must be…",
                   ["lo < hi", "lo <= hi", "either", "lo !== hi"], 1,
                   "A range of one is still a range."),
                _q("With `hi = length`, you shrink with…",
                   ["hi = mid - 1", "hi = mid", "hi = mid + 1", "hi--"], 1,
                   "Exclusive hi keeps mid as the new bound."),
                _q("The five-second test for a binary search is…",
                   ["a big array", "a ONE-element array", "an empty array", "a sorted array"], 1,
                   "If it cannot find the only element, the condition is wrong."),
                _q("`lo = mid` instead of `lo = mid + 1`…",
                   ["is equivalent", "hangs — the range stops shrinking", "is faster", "returns -1"], 1,
                   "Termination depends on excluding mid."),
            ],
            exercises=[
                _ex("tscourse-w22-bs-1", "The inclusive shape",
                    "Set the upper bound so the loop test `lo <= hi` is correct.",
                    _SORTED +
                    'function search(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  while (lo <= hi) {\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    const v = xs[mid] ?? 0;\n'
                    '    if (v === target) {\n'
                    '      return mid;\n    }\n'
                    '    if (v < target) {\n'
                    '      lo = mid + 1;\n'
                    '    } else {\n'
                    '      hi = mid - 1;\n    }\n  }\n'
                    '  return -1;\n}\n'
                    'console.log(search(nums, 3));\n',
                    '  let hi = xs.length - 1;',
                    [("1 2 3 4 5", "2"), ("3", "0"), ("1 2", "-1")],
                    hints=["An inclusive bound is the last real index.",
                           "Write let hi = xs.length - 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bs-2", "Count the steps",
                    "Report how many iterations the search needed, which is the log.",
                    'function steps(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  let n = 0;\n'
                    '  while (lo <= hi) {\n'
                    '    n = n + 1;\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    const v = xs[mid] ?? 0;\n'
                    '    if (v === target) {\n'
                    '      return n;\n    }\n'
                    '    if (v < target) {\n'
                    '      lo = mid + 1;\n'
                    '    } else {\n'
                    '      hi = mid - 1;\n    }\n  }\n'
                    '  return n;\n}\n'
                    'for (const size of [8, 1024]) {\n'
                    '  const xs = Array.from({ length: size }, (_, i) => i);\n'
                    '  console.log(`n=${size} steps=${steps(xs, size - 1)}`);\n}\n',
                    '    n = n + 1;',
                    [("", "n=8 steps=4\nn=1024 steps=11")],
                    hints=["One per iteration, at the top of the loop.",
                           "Write n = n + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w22-bs-3", "Find the one element",
                    "Run the search on a single-element array — the test that catches the boundary bug.",
                    'function search(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  while (lo <= hi) {\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    const v = xs[mid] ?? 0;\n'
                    '    if (v === target) {\n'
                    '      return mid;\n    }\n'
                    '    if (v < target) {\n'
                    '      lo = mid + 1;\n'
                    '    } else {\n'
                    '      hi = mid - 1;\n    }\n  }\n'
                    '  return -1;\n}\n'
                    'console.log(`${search([7], 7)} ${search([7], 9)} ${search([], 7)}`);\n',
                    'console.log(`${search([7], 7)} ${search([7], 9)} ${search([], 7)}`);',
                    [("", "0 -1 -1")],
                    hints=["Three cases: the only element, a missing one, and an empty array.",
                           "Write console.log(`${search([7], 7)} ${search([7], 9)} ${search([], 7)}`);"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bs-4", "Rule out the midpoint",
                    "Move the lower bound past the midpoint, so the range shrinks and the loop ends.",
                    _SORTED +
                    'function search(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  while (lo <= hi) {\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    const v = xs[mid] ?? 0;\n'
                    '    if (v === target) {\n'
                    '      return mid;\n    }\n'
                    '    if (v < target) {\n'
                    '      lo = mid + 1;\n'
                    '    } else {\n'
                    '      hi = mid - 1;\n    }\n  }\n'
                    '  return -1;\n}\n'
                    'console.log(search(nums, 5));\n',
                    '      lo = mid + 1;', [("1 3 5 7", "2"), ("5", "0")],
                    hints=["`mid` has already been tested and is not the answer, so exclude it.",
                           "Write lo = mid + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bs-5", "Which row am I in",
                    "Report the three values that have to agree, for each shape.",
                    'const shapes = [\n'
                    '  "value: hi=length-1, lo<=hi, hi=mid-1",\n'
                    '  "bound: hi=length, lo<hi, hi=mid",\n'
                    '];\n'
                    'for (const s of shapes) {\n'
                    '  console.log(s);\n}\n',
                    'for (const s of shapes) {',
                    [("", "value: hi=length-1, lo<=hi, hi=mid-1\nbound: hi=length, lo<hi, hi=mid")],
                    hints=["Print each row on its own line.",
                           "Write for (const s of shapes) {"],
                    difficulty="Easy"),
                _fix("tscourse-w22-bs-fix1", "Fix the search that misses the last element",
                     "`search([1,2,3], 3)` returns -1 and so does `search([1], 1)`. The upper bound is inclusive but the loop test is `<`, so the loop exits with one element still unexamined — two rows of the table, mixed.",
                     'function search(xs: readonly number[], target: number): number {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  while (lo < hi) {\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    const v = xs[mid] ?? 0;\n'
                     '    if (v === target) {\n'
                     '      return mid;\n    }\n'
                     '    if (v < target) {\n'
                     '      lo = mid + 1;\n'
                     '    } else {\n'
                     '      hi = mid - 1;\n    }\n  }\n'
                     '  return -1;\n}\n'
                     'console.log(`${search([1, 2, 3], 3)} ${search([1], 1)}`);\n',
                     'function search(xs: readonly number[], target: number): number {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  while (lo <= hi) {\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    const v = xs[mid] ?? 0;\n'
                     '    if (v === target) {\n'
                     '      return mid;\n    }\n'
                     '    if (v < target) {\n'
                     '      lo = mid + 1;\n'
                     '    } else {\n'
                     '      hi = mid - 1;\n    }\n  }\n'
                     '  return -1;\n}\n'
                     'console.log(`${search([1, 2, 3], 3)} ${search([1], 1)}`);\n',
                     [("", "2 0")],
                     hints=["The one-element case is the giveaway: the loop never runs at all.",
                            "With an inclusive `hi`, a range where lo equals hi still contains one element.",
                            "Change the loop test to `lo <= hi`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The JDK's binary search had an overflow bug for nine years because…",
                   ["the idea is hard", "`lo + hi` can exceed Java's int range", "of sorting",
                    "of generics"], 1,
                   "Which is not possible with JavaScript doubles."),
                _q("Being able to state the invariant lets you…",
                   ["skip tests", "write the boundaries without guessing", "avoid sorting",
                    "use recursion"], 1,
                   "\"If it is here at all, it is in [lo, hi].\""),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w22-bounds", "The two bounds",
            "What binary search is actually for.",
            """
"Find the index of x" is the least useful question you can ask a sorted array. The
useful ones are:

* Where does x **start**?
* Where does x **end**?
* **How many** x are there?
* Where **would** x go?
* How many values are in **[a, b]**?

All five are answered by two functions, which differ by **one character**.

## Lower bound — the first index whose value is `>= target`

```ts
function lowerBound(xs: readonly number[], target: number): number {
  let lo = 0;
  let hi = xs.length;                       // EXCLUSIVE
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if ((xs[mid] ?? 0) < target) { lo = mid + 1; }
    else { hi = mid; }
  }
  return lo;
}
```

On `[1, 3, 3, 3, 5, 7]`:

```
lowerBound(0) = 0     // before everything
lowerBound(3) = 1     // the FIRST 3
lowerBound(4) = 4     // where a 4 would go
lowerBound(8) = 6     // past the end — note: a valid answer, not an error
```

It never returns -1. A missing value gives you the position it *would* occupy,
which is exactly what you want when inserting, and is why this is also called the
**insertion point**.

## Upper bound — the first index whose value is `> target`

```ts
    if ((xs[mid] ?? 0) <= target) { lo = mid + 1; }   // <= instead of <
```

That is the entire difference. On the same array, `upperBound(3) = 4` — one past
the last 3.

## What the pair gives you

```ts
const first = lowerBound(xs, x);
const past = upperBound(xs, x);

past - first;                   // how many x there are — no scanning
first < xs.length && xs[first] === x;    // is x present
lowerBound(xs, x);               // where to insert
upperBound(xs, b) - lowerBound(xs, a);  // how many values in [a, b]
```

That last line is worth staring at. "How many ledger entries between £5 and £20"
is two binary searches and a subtraction — O(log n) for a question that looks like
it needs a filter.

## Presence, carefully

```ts
const i = lowerBound(xs, x);
const present = i < xs.length && (xs[i] ?? 0) === x;
```

**The length check comes first.** `lowerBound` legitimately returns `xs.length`
for a value past the end, and indexing there is `undefined` — which under
`noUncheckedIndexedAccess` the compiler already made you think about, and which
without the check would compare `0 === x` and occasionally say yes.

> ⚠️ **Common mistakes:** expecting -1 for a missing value; forgetting the length
> check before comparing; and writing `<` where the upper bound needs `<=`.
""",
            warmup=[
                _q("A lower bound returns the first index whose value is…",
                   ["> target", ">= target", "=== target", "< target"], 1,
                   "Which is where the value starts, or would go."),
                _q("For a value past the end, `lowerBound` returns…",
                   ["-1", "xs.length", "0", "undefined"], 1,
                   "A valid answer, not an error."),
                _q("Upper bound differs from lower bound by…",
                   ["the loop shape", "one character: `<=` instead of `<`", "the return",
                    "the bounds"], 1,
                   "That is genuinely all."),
                _q("The count of x is…",
                   ["a scan", "upperBound(x) - lowerBound(x)", "lowerBound(x)", "1"], 1,
                   "Two searches and a subtraction."),
            ],
            exercises=[
                _ex("tscourse-w22-bd-1", "The lower bound",
                    "Move the exclusive upper bound down to the midpoint, keeping it as a candidate.",
                    _SORTED + _LOWER +
                    'console.log(lowerBound(nums, 3));\n',
                    '      hi = mid;', [("1 3 3 3 5 7", "1"), ("1 2", "2"), ("5 6", "0")],
                    hints=["The midpoint might itself be the answer, so it stays in range.",
                           "Write hi = mid;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bd-2", "The upper bound",
                    "Change one operator, so the search lands one past the last match.",
                    _SORTED + _UPPER +
                    'console.log(upperBound(nums, 3));\n',
                    '    if ((xs[mid] ?? 0) <= target) {',
                    [("1 3 3 3 5 7", "4"), ("1 2", "2"), ("3", "1")],
                    hints=["Equal values must be skipped over, not stopped at.",
                           "Write if ((xs[mid] ?? 0) <= target) {"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bd-3", "Count without scanning",
                    "Subtract the two bounds.",
                    _SORTED + _LOWER + _UPPER +
                    'const target = 3;\n'
                    'console.log(upperBound(nums, target) - lowerBound(nums, target));\n',
                    'console.log(upperBound(nums, target) - lowerBound(nums, target));',
                    [("1 3 3 3 5", "3"), ("1 2", "0"), ("3 3", "2")],
                    hints=["One past the last, minus the first.",
                           "Write console.log(upperBound(nums, target) - lowerBound(nums, target));"],
                    difficulty="Easy"),
                _ex("tscourse-w22-bd-4", "Present, safely",
                    "Check the index is in range before comparing what is there.",
                    _SORTED + _LOWER +
                    'function has(xs: readonly number[], target: number): boolean {\n'
                    '  const i = lowerBound(xs, target);\n'
                    '  return i < xs.length && (xs[i] ?? 0) === target;\n}\n'
                    'console.log(`${has(nums, 3)} ${has(nums, 99)}`);\n',
                    '  return i < xs.length && (xs[i] ?? 0) === target;',
                    [("1 3 5", "true false"), ("1 2", "false false")],
                    hints=["The bound may legitimately be one past the end.",
                           "Write return i < xs.length && (xs[i] ?? 0) === target;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bd-5", "How many in a range",
                    "Answer a range query with two bounds and a subtraction.",
                    _SORTED + _LOWER + _UPPER +
                    'function inRange(xs: readonly number[], lo: number, hi: number): number {\n'
                    '  return upperBound(xs, hi) - lowerBound(xs, lo);\n}\n'
                    'console.log(inRange(nums, 3, 7));\n',
                    '  return upperBound(xs, hi) - lowerBound(xs, lo);',
                    [("1 3 5 7 9", "3"), ("1 2", "0"), ("3 4 5 6 7", "5")],
                    hints=["One past the top of the range, minus the start of it.",
                           "Write return upperBound(xs, hi) - lowerBound(xs, lo);"],
                    difficulty="Medium"),
                _ex("tscourse-w22-bd-6", "Insert and stay sorted",
                    "Splice the new value in at its lower bound.",
                    _SORTED + _LOWER +
                    'const xs = [...nums];\n'
                    'const value = 4;\n'
                    'xs.splice(lowerBound(xs, value), 0, value);\n'
                    'console.log(xs.join(","));\n',
                    'xs.splice(lowerBound(xs, value), 0, value);',
                    [("1 3 5", "1,3,4,5"), ("9", "4,9"), ("1 2", "1,2,4")],
                    hints=["The insertion point is exactly the lower bound.",
                           "Write xs.splice(lowerBound(xs, value), 0, value);"],
                    difficulty="Medium"),
                _predict("tscourse-w22-bd-p1", "What a bound returns",
                         _LOWER +
                         'const xs: readonly number[] = [1, 3, 5];\n'
                         'const at = lowerBound(xs, 99);\n',
                         "at", "number",
                         why="The question is the TYPE, not the value — and a bound never signals absence out of band.",
                         hints=["It returns an index, always — even for a value past the end.",
                                "Write number."]),
                _fix("tscourse-w22-bd-fix1", "Fix the presence check that read past the end",
                     "`has(xs, 99)` says `true` for an array of `[1, 3, 5]`: the lower bound is 3, which is past the end, and `xs[3] ?? 0` is `0` — compared against nothing meaningful. Check the range first.",
                     _LOWER +
                     'function has(xs: readonly number[], target: number): boolean {\n'
                     '  const i = lowerBound(xs, target);\n'
                     '  return (xs[i] ?? target) === target;\n}\n'
                     'console.log(`${has([1, 3, 5], 3)} ${has([1, 3, 5], 99)}`);\n',
                     _LOWER +
                     'function has(xs: readonly number[], target: number): boolean {\n'
                     '  const i = lowerBound(xs, target);\n'
                     '  return i < xs.length && (xs[i] ?? 0) === target;\n}\n'
                     'console.log(`${has([1, 3, 5], 3)} ${has([1, 3, 5], 99)}`);\n',
                     [("", "true false")],
                     hints=["The fallback `?? target` makes the comparison true whenever the index is out of range.",
                            "A bound can legitimately be `xs.length`.",
                            "Test `i < xs.length` before looking at what is there."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("\"How many entries between 5 and 20\" costs…",
                   ["O(n)", "O(log n) — two bounds and a subtraction", "O(n log n)", "O(1)"], 1,
                   "For a question that looks like a filter."),
                _q("A lower bound never returns -1 because…",
                   ["it throws", "a missing value still has a position it would occupy", "it is 0",
                    "of the loop"], 1,
                   "Which is what makes it an insertion point."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w22-answer", "Binary search on the answer",
            "There is no array. You are halving the answer itself.",
            """
The hardest binary-search problems have no array in them at all. What is sorted is
the space of **possible answers**, and the "comparison" is a yes/no question about
a candidate.

## The shape of the problem

> Find the **smallest** budget / capacity / speed / day that **works**.

It is a binary search whenever the yes/no question is **monotonic**:

```
budget:      1      2      3      4      5      6      7
works?     false  false  false  true   true   true   true
                                  ↑
                             the answer
```

Once a budget works, every larger budget works too. That is the only requirement,
and if it does not hold you cannot halve.

## The template

```ts
let lo = 1;                              // a definitely-impossible answer, or the
let hi = total;                          // smallest, and a definitely-possible one
while (lo < hi) {                        // the BOUND shape, not the value shape
  const mid = Math.floor((lo + hi) / 2);
  if (feasible(mid)) { hi = mid; }       // it works, so the answer is <= mid
  else { lo = mid + 1; }                 // it does not, so the answer is > mid
}
return lo;                                // lo === hi === the smallest that works
```

Note it is the **bound** shape from lesson 3, not the find-a-value shape. You are
not looking for a value that is there — you are looking for the boundary between
false and true, which is exactly what a lower bound finds.

## A worked example

*The ledger has to be split across `days` days without reordering it. What is the
smallest daily limit that fits?*

```ts
function feasible(caps: readonly number[], perDay: number, days: number): boolean {
  let used = 1;
  let left = perDay;
  for (const c of caps) {
    if (c > perDay) { return false; }      // one item alone exceeds the limit
    if (c > left) { used = used + 1; left = perDay; }   // start a new day
    left = left - c;
  }
  return used <= days;
}
```

`[1,2,3,4,5]` over 2 days gives **9**; over 5 days it gives **5** (the largest
single item, which is the floor no number of days can go below). Both verified, and
both worth checking by hand — the second is the one that tells you the search
bounds were right.

## Choosing the bounds

* `lo` = the smallest answer that could *conceivably* work.
* `hi` = an answer that certainly works.

If `hi` is not certainly feasible the loop returns a wrong answer rather than
failing, which is the trap: here `hi` is the **sum** of everything, because one day
holding the whole ledger always works.

## Recognising it

Three signals, and any one is usually enough:

* the question says **"minimum … such that"** or **"maximum … such that"**;
* checking a *specific* answer is much easier than finding the best one;
* the answers are ordered, and feasibility never flips back.

That third one is the whole of it. "Is 7 enough?" being answerable in O(n) turns
"what is the smallest enough?" into O(n log answer).

> ⚠️ **Common mistakes:** a non-monotonic predicate; an upper bound that is not
> actually feasible; and using the find-a-value loop shape, which will not converge
> on a boundary.
""",
            warmup=[
                _q("Searching on the answer requires the predicate to be…",
                   ["fast", "monotonic — once true, always true", "pure", "total"], 1,
                   "Otherwise halving is invalid."),
                _q("The loop shape to use is…",
                   ["the find-a-value one", "the BOUND one (lo < hi, hi = mid)", "either",
                    "a for loop"], 1,
                   "You are finding a boundary, not a value."),
                _q("`hi` must be chosen so that…",
                   ["it is large", "it is certainly feasible", "it is the sum", "it is n"], 1,
                   "Otherwise the answer is silently wrong."),
                _q("The signal phrase is…",
                   ["\"sort the array\"", "\"the minimum X such that\"", "\"find the index\"",
                    "\"in place\""], 1,
                   "Plus: checking one answer is easy."),
            ],
            exercises=[
                _ex("tscourse-w22-an-1", "The monotonic table",
                    "Print whether each candidate works, and confirm the answer never flips back.",
                    'function works(budget: number): boolean {\n'
                    '  return budget >= 4;\n}\n'
                    'const row: string[] = [];\n'
                    'for (let b = 1; b <= 7; b = b + 1) {\n'
                    '  row.push(`${b}:${works(b) ? "T" : "F"}`);\n}\n'
                    'console.log(row.join(" "));\n',
                    '  row.push(`${b}:${works(b) ? "T" : "F"}`);',
                    [("", "1:F 2:F 3:F 4:T 5:T 6:T 7:T")],
                    hints=["One entry per candidate, with its verdict.",
                           'Write row.push(`${b}:${works(b) ? "T" : "F"}`);'],
                    difficulty="Easy"),
                _ex("tscourse-w22-an-2", "Find the boundary",
                    "Binary search for the smallest candidate that works.",
                    'function works(budget: number): boolean {\n'
                    '  return budget >= 4;\n}\n'
                    'function smallest(hiStart: number): number {\n'
                    '  let lo = 1;\n'
                    '  let hi = hiStart;\n'
                    '  while (lo < hi) {\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    if (works(mid)) {\n'
                    '      hi = mid;\n'
                    '    } else {\n'
                    '      lo = mid + 1;\n    }\n  }\n'
                    '  return lo;\n}\n'
                    'console.log(smallest(100));\n',
                    '      hi = mid;', [("", "4")],
                    hints=["A working candidate might itself be the answer, so it stays in range.",
                           "Write hi = mid;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-an-3", "The feasibility check",
                    "Start a new day when the current one cannot hold the next item.",
                    _SORTED +
                    'function feasible(caps: readonly number[], perDay: number, days: number): boolean {\n'
                    '  let used = 1;\n'
                    '  let left = perDay;\n'
                    '  for (const c of caps) {\n'
                    '    if (c > perDay) {\n'
                    '      return false;\n    }\n'
                    '    if (c > left) {\n'
                    '      used = used + 1;\n'
                    '      left = perDay;\n    }\n'
                    '    left = left - c;\n  }\n'
                    '  return used <= days;\n}\n'
                    'console.log(`${feasible(nums, 9, 2)} ${feasible(nums, 4, 2)}`);\n',
                    '    if (c > left) {\n'
                    '      used = used + 1;\n'
                    '      left = perDay;\n    }',
                    [("1 2 3 4 5", "true false")],
                    hints=["When the item does not fit in what is left, open a new day and reset the allowance.",
                           "Write if (c > left) { used = used + 1; left = perDay; }"],
                    difficulty="Medium"),
                _ex("tscourse-w22-an-4", "Search the whole thing",
                    "Set the upper bound to an answer that certainly works — one day holding everything.",
                    _SORTED +
                    'function feasible(caps: readonly number[], perDay: number, days: number): boolean {\n'
                    '  let used = 1;\n'
                    '  let left = perDay;\n'
                    '  for (const c of caps) {\n'
                    '    if (c > perDay) {\n'
                    '      return false;\n    }\n'
                    '    if (c > left) {\n'
                    '      used = used + 1;\n'
                    '      left = perDay;\n    }\n'
                    '    left = left - c;\n  }\n'
                    '  return used <= days;\n}\n'
                    'function minPerDay(caps: readonly number[], days: number): number {\n'
                    '  let lo = 1;\n'
                    '  let hi = caps.reduce((s, c) => s + c, 0);\n'
                    '  while (lo < hi) {\n'
                    '    const mid = Math.floor((lo + hi) / 2);\n'
                    '    if (feasible(caps, mid, days)) {\n'
                    '      hi = mid;\n'
                    '    } else {\n'
                    '      lo = mid + 1;\n    }\n  }\n'
                    '  return lo;\n}\n'
                    'console.log(`${minPerDay(nums, 2)} ${minPerDay(nums, 5)}`);\n',
                    '  let hi = caps.reduce((s, c) => s + c, 0);',
                    [("1 2 3 4 5", "9 5")],
                    hints=["One day carrying the entire ledger is always feasible.",
                           "Write let hi = caps.reduce((s, c) => s + c, 0);"],
                    difficulty="Hard"),
                _ex("tscourse-w22-an-5", "The floor no budget can beat",
                    "Report the largest single item, which is the smallest possible answer whatever the day count.",
                    _SORTED +
                    'let biggest = 0;\n'
                    'for (const n of nums) {\n'
                    '  biggest = Math.max(biggest, n);\n}\n'
                    'console.log(`floor=${biggest}`);\n',
                    '  biggest = Math.max(biggest, n);',
                    [("1 2 3 4 5", "floor=5"), ("7", "floor=7")],
                    hints=["No daily limit below the largest item can ever work.",
                           "Write biggest = Math.max(biggest, n);"],
                    difficulty="Easy"),
                _ex("tscourse-w22-an-6", "Count the feasibility checks",
                    "Report how many times the predicate ran, which is the log of the answer range.",
                    'let checks = 0;\n'
                    'function works(budget: number): boolean {\n'
                    '  checks = checks + 1;\n'
                    '  return budget >= 40;\n}\n'
                    'let lo = 1;\n'
                    'let hi = 1024;\n'
                    'while (lo < hi) {\n'
                    '  const mid = Math.floor((lo + hi) / 2);\n'
                    '  if (works(mid)) {\n'
                    '    hi = mid;\n'
                    '  } else {\n'
                    '    lo = mid + 1;\n  }\n}\n'
                    'console.log(`answer=${lo} checks=${checks}`);\n',
                    '  checks = checks + 1;', [("", "answer=40 checks=10")],
                    hints=["One per call to the predicate.",
                           "Write checks = checks + 1;"],
                    difficulty="Medium"),
                _fix("tscourse-w22-an-fix1", "Fix the upper bound that did not work",
                     "This reports `5` as the smallest daily limit for two days, and five does not fit — the search started from an upper bound that is not itself feasible, so it converged on the wrong side of the boundary. The template needs a `hi` that certainly works.",
                     _SORTED +
                     'function feasible(caps: readonly number[], perDay: number, days: number): boolean {\n'
                     '  let used = 1;\n'
                     '  let left = perDay;\n'
                     '  for (const c of caps) {\n'
                     '    if (c > perDay) {\n'
                     '      return false;\n    }\n'
                     '    if (c > left) {\n'
                     '      used = used + 1;\n'
                     '      left = perDay;\n    }\n'
                     '    left = left - c;\n  }\n'
                     '  return used <= days;\n}\n'
                     'function minPerDay(caps: readonly number[], days: number): number {\n'
                     '  let lo = 1;\n'
                     '  let hi = caps.length;\n'
                     '  while (lo < hi) {\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    if (feasible(caps, mid, days)) {\n'
                     '      hi = mid;\n'
                     '    } else {\n'
                     '      lo = mid + 1;\n    }\n  }\n'
                     '  return lo;\n}\n'
                     'console.log(minPerDay(nums, 2));\n',
                     _SORTED +
                     'function feasible(caps: readonly number[], perDay: number, days: number): boolean {\n'
                     '  let used = 1;\n'
                     '  let left = perDay;\n'
                     '  for (const c of caps) {\n'
                     '    if (c > perDay) {\n'
                     '      return false;\n    }\n'
                     '    if (c > left) {\n'
                     '      used = used + 1;\n'
                     '      left = perDay;\n    }\n'
                     '    left = left - c;\n  }\n'
                     '  return used <= days;\n}\n'
                     'function minPerDay(caps: readonly number[], days: number): number {\n'
                     '  let lo = 1;\n'
                     '  let hi = caps.reduce((s, c) => s + c, 0);\n'
                     '  while (lo < hi) {\n'
                     '    const mid = Math.floor((lo + hi) / 2);\n'
                     '    if (feasible(caps, mid, days)) {\n'
                     '      hi = mid;\n'
                     '    } else {\n'
                     '      lo = mid + 1;\n    }\n  }\n'
                     '  return lo;\n}\n'
                     'console.log(minPerDay(nums, 2));\n',
                     [("1 2 3 4 5", "9"), ("10 10", "10")],
                     hints=["`caps.length` is the number of items, which has nothing to do with a daily total.",
                            "The search only works if `hi` is an answer that is certainly feasible.",
                            "One day holding everything always works: use the sum."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("A non-monotonic predicate means…",
                   ["a slower search", "you cannot binary search at all", "a wrong bound",
                    "more checks"], 1,
                   "Halving depends on one flip."),
                _q("\"Is 7 enough?\" being O(n) makes \"what is the smallest enough?\"…",
                   ["O(n)", "O(n log answer)", "O(n²)", "O(log n)"], 1,
                   "One predicate run per halving."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w22-twoends", "Two pointers, from both ends",
            "One sweep instead of a nested loop.",
            """
Find two numbers in a sorted array that sum to a target. The obvious version tries
every pair — O(n²). The good version needs one pass:

```ts
let lo = 0;
let hi = xs.length - 1;
while (lo < hi) {
  const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);
  if (sum === target) { return [lo, hi]; }
  if (sum < target) { lo = lo + 1; }   // too small: the only bigger option is right
  else { hi = hi - 1; }                 // too big: the only smaller option is left
}
```

## Why it is correct, and why it needs sorting

The sum is too small. Could the answer involve `xs[lo]`? Only with something
*bigger* than `xs[hi]` — and `xs[hi]` is the largest value left. So `xs[lo]` is in
no solution at all, and discarding it loses nothing.

**That argument only works because the array is sorted.** Unsorted, "I need a
bigger number, so I move right" is false, and the whole thing collapses.

Each step eliminates one element permanently, so at most n steps: **O(n)** time,
**O(1)** space. On `[1,2,4,7,11,15]` for target 15 it takes 4 steps and finds
`4+11`; for an impossible target it takes 5 and reports none. Both are printed in
this lesson's exercises, because "O(n)" is a claim and `steps=4` is the evidence.

## The same sweep, three other problems

**Palindrome** — compare the ends, move inwards:

```ts
while (lo < hi) {
  if (text.charAt(lo) !== text.charAt(hi)) { return false; }
  lo = lo + 1;
  hi = hi - 1;
}
```

**Reverse in place** — swap the ends, move inwards. Week 21's O(1)-space reversal.

**Closest pair to a target** — the same loop, keeping the best sum seen instead of
returning on an exact match. Note it must run to `lo === hi`, since the closest
pair can turn up at any point.

## The loop condition

`lo < hi`, never `lo <= hi`. At `lo === hi` you are looking at one element twice,
which is not a pair. The one exception is when a problem genuinely allows an
element to be used with itself, and then you should say so in a comment, because
every reader will assume it is a bug.

## When it does not apply

* **Unsorted input** you must not reorder — then it is a `Set` (week 19) in O(n)
  time and O(n) space, or a sort first if reordering is allowed.
* **Indices of the original array** must be reported — sorting destroys them unless
  you carry them along.

That second point is the standard trap in "two sum": if the answer must be the
*original* indices and the input is unsorted, the two-pointer version needs extra
bookkeeping and a Map is simply better.

> ⚠️ **Common mistakes:** applying it to unsorted data; `lo <= hi` and pairing an
> element with itself; and losing the original indices to the sort.
""",
            warmup=[
                _q("The two-pointer pair-sum sweep is…",
                   ["O(n²)", "O(n) time and O(1) space", "O(n log n)", "O(1)"], 1,
                   "Each step eliminates an element permanently."),
                _q("It requires the array to be…",
                   ["unique", "sorted", "non-empty", "numeric"], 1,
                   "Otherwise 'move right for more' is false."),
                _q("The loop condition is…",
                   ["lo <= hi", "lo < hi", "lo !== hi", "lo < hi - 1"], 1,
                   "At equality you would pair an element with itself."),
                _q("If the ORIGINAL indices are required and the input is unsorted…",
                   ["sort anyway", "a Map is better — sorting destroys the indices", "use two pointers",
                    "impossible"], 1,
                   "The standard two-sum trap."),
            ],
            exercises=[
                _ex("tscourse-w22-te-1", "Move the right pointer in",
                    "When the sum is too big, the only way to get smaller is from the right.",
                    _SORTED +
                    'function pair(xs: readonly number[], target: number): string {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  let steps = 0;\n'
                    '  while (lo < hi) {\n'
                    '    steps = steps + 1;\n'
                    '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                    '    if (sum === target) {\n'
                    '      return `${xs[lo] ?? 0}+${xs[hi] ?? 0} steps=${steps}`;\n    }\n'
                    '    if (sum < target) {\n'
                    '      lo = lo + 1;\n'
                    '    } else {\n'
                    '      hi = hi - 1;\n    }\n  }\n'
                    '  return `none steps=${steps}`;\n}\n'
                    'console.log(pair(nums, 15));\n',
                    '      hi = hi - 1;',
                    [("1 2 4 7 11 15", "4+11 steps=4"), ("1 2", "none steps=1")],
                    hints=["Too big means the largest remaining value has to go.",
                           "Write hi = hi - 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-te-2", "Count what it cost",
                    "Report the steps for a target that exists and one that does not.",
                    'function steps(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  let n = 0;\n'
                    '  while (lo < hi) {\n'
                    '    n = n + 1;\n'
                    '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                    '    if (sum === target) {\n'
                    '      return n;\n    }\n'
                    '    if (sum < target) {\n'
                    '      lo = lo + 1;\n'
                    '    } else {\n'
                    '      hi = hi - 1;\n    }\n  }\n'
                    '  return n;\n}\n'
                    'const xs = [1, 2, 4, 7, 11, 15];\n'
                    'console.log(`found=${steps(xs, 15)} missing=${steps(xs, 100)} pairs=${(xs.length * (xs.length - 1)) / 2}`);\n',
                    'console.log(`found=${steps(xs, 15)} missing=${steps(xs, 100)} pairs=${(xs.length * (xs.length - 1)) / 2}`);',
                    [("", "found=4 missing=5 pairs=15")],
                    hints=["The number of pairs a nested loop would examine is n(n-1)/2.",
                           "Five steps against fifteen pairs is the whole argument."],
                    difficulty="Medium"),
                _ex("tscourse-w22-te-3", "Palindrome, from both ends",
                    "Compare the outermost characters and walk inwards.",
                    _LINE +
                    'function isPal(text: string): boolean {\n'
                    '  let lo = 0;\n'
                    '  let hi = text.length - 1;\n'
                    '  while (lo < hi) {\n'
                    '    if (text.charAt(lo) !== text.charAt(hi)) {\n'
                    '      return false;\n    }\n'
                    '    lo = lo + 1;\n'
                    '    hi = hi - 1;\n  }\n'
                    '  return true;\n}\n'
                    'console.log(isPal(line));\n',
                    '    if (text.charAt(lo) !== text.charAt(hi)) {',
                    [("racecar", "true"), ("abba", "true"), ("abc", "false")],
                    hints=["Mismatched ends mean it is not a palindrome.",
                           "Write if (text.charAt(lo) !== text.charAt(hi)) {"],
                    difficulty="Easy"),
                _ex("tscourse-w22-te-4", "Reverse by swapping ends",
                    "Swap and converge, allocating nothing.",
                    _NUMS +
                    'const xs = [...nums];\n'
                    'let lo = 0;\n'
                    'let hi = xs.length - 1;\n'
                    'while (lo < hi) {\n'
                    '  const t = xs[lo] ?? 0;\n'
                    '  xs[lo] = xs[hi] ?? 0;\n'
                    '  xs[hi] = t;\n'
                    '  lo = lo + 1;\n'
                    '  hi = hi - 1;\n}\n'
                    'console.log(xs.join(","));\n',
                    '  xs[lo] = xs[hi] ?? 0;\n  xs[hi] = t;',
                    [("1 2 3", "3,2,1"), ("1 2 3 4", "4,3,2,1")],
                    hints=["The temporary already holds the left value, so overwrite left first.",
                           "Write xs[lo] = xs[hi] ?? 0; then xs[hi] = t;"],
                    difficulty="Medium"),
                _ex("tscourse-w22-te-5", "The closest pair",
                    "Run the sweep to the end, keeping the best sum rather than returning early.",
                    _SORTED +
                    'function closest(xs: readonly number[], target: number): number {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  let best = 0;\n'
                    '  let bestGap = Number.MAX_SAFE_INTEGER;\n'
                    '  while (lo < hi) {\n'
                    '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                    '    const gap = Math.abs(sum - target);\n'
                    '    if (gap < bestGap) {\n'
                    '      bestGap = gap;\n'
                    '      best = sum;\n    }\n'
                    '    if (sum < target) {\n'
                    '      lo = lo + 1;\n'
                    '    } else {\n'
                    '      hi = hi - 1;\n    }\n  }\n'
                    '  return best;\n}\n'
                    'console.log(closest(nums, 10));\n',
                    '    if (gap < bestGap) {\n'
                    '      bestGap = gap;\n'
                    '      best = sum;\n    }',
                    [("1 2 4 7 11", "9"), ("1 2", "3")],
                    hints=["A strictly smaller gap replaces the best; equal gaps keep the first.",
                           "Write if (gap < bestGap) { bestGap = gap; best = sum; }"],
                    difficulty="Hard"),
                _fix("tscourse-w22-te-fix1", "Fix the pair that used one element twice",
                     "With `lo <= hi` the loop reaches a point where both pointers are on the same element, so `[1, 2, 4]` reports a pair summing to 8 — which is `4 + 4`, the same 4 counted twice.",
                     'function pair(xs: readonly number[], target: number): string {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  while (lo <= hi) {\n'
                     '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                     '    if (sum === target) {\n'
                     '      return `${xs[lo] ?? 0}+${xs[hi] ?? 0}`;\n    }\n'
                     '    if (sum < target) {\n'
                     '      lo = lo + 1;\n'
                     '    } else {\n'
                     '      hi = hi - 1;\n    }\n  }\n'
                     '  return "none";\n}\n'
                     'console.log(`${pair([1, 2, 4], 8)} ${pair([1, 2, 4], 5)}`);\n',
                     'function pair(xs: readonly number[], target: number): string {\n'
                     '  let lo = 0;\n'
                     '  let hi = xs.length - 1;\n'
                     '  while (lo < hi) {\n'
                     '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                     '    if (sum === target) {\n'
                     '      return `${xs[lo] ?? 0}+${xs[hi] ?? 0}`;\n    }\n'
                     '    if (sum < target) {\n'
                     '      lo = lo + 1;\n'
                     '    } else {\n'
                     '      hi = hi - 1;\n    }\n  }\n'
                     '  return "none";\n}\n'
                     'console.log(`${pair([1, 2, 4], 8)} ${pair([1, 2, 4], 5)}`);\n',
                     [("", "none 1+4")],
                     hints=["When lo equals hi, both pointers are on the same element — and that is not a pair.",
                            "One character.",
                            "Write while (lo < hi) {"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Discarding `xs[lo]` when the sum is too small is safe because…",
                   ["it is small", "nothing left is bigger than xs[hi], so xs[lo] is in no solution",
                    "of the loop", "it is sorted"], 1,
                   "The argument is the whole proof."),
                _q("The closest-pair variant must…",
                   ["return early", "run the sweep to the end", "sort again", "use a Map"], 1,
                   "The best pair can appear at any point."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w22-samedir", "Two pointers, same direction",
            "A read pointer and a write pointer.",
            """
The other two-pointer shape: both indices move forward, at different speeds.

* **read** visits every element, exactly once;
* **write** marks where the next *kept* element goes.

```ts
function dedupe(xs: number[]): number {
  if (xs.length === 0) { return 0; }
  let write = 1;                                  // xs[0] is always kept
  for (let read = 1; read < xs.length; read = read + 1) {
    if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {
      xs[write] = xs[read] ?? 0;
      write = write + 1;
    }
  }
  return write;                                    // the new length
}
```

On `[1,1,2,2,2,3]` that returns 3, with the first three slots holding `1,2,3`.

## Why it returns a length

You cannot shrink an array in place without either mutating `length` or returning
the count. The convention — used by every in-place algorithm of this shape — is to
compact the kept elements to the front and **return the new length**, leaving
whatever is past it as garbage the caller ignores:

```ts
const n = dedupe(xs);
xs.slice(0, n);              // the part that matters
```

O(n) time, **O(1) auxiliary space**, which is the point. `[...new Set(xs)]` is
shorter, clearer, and allocates — and on sorted input where space matters, this is
the version to know.

## The comparison is against the last KEPT element

`xs[write - 1]` — "the last element I decided to keep" — rather than
`xs[read - 1]`, "the previous element I looked at".

Worth being precise, because the two produce **identical answers here** and it is
easy to write the wrong one and never find out. The reason they agree is that
`write <= read` always, so the slot at `read - 1` can only have been overwritten
when `write === read`, and that write is `xs[read] = xs[read]` — a no-op. Change the
problem and that argument has to be redone from scratch.

So: write the form that says what you mean. `xs[write - 1]` is correct *because of
what it is*, and `xs[read - 1]` is correct *because of a two-line argument about
indices* — and the second kind of correctness is the kind that stops being true when
somebody edits the loop.

## The same shape, three other problems

**Move zeroes to the end** — write every non-zero, then fill the rest with zeroes.

**Partition by a predicate** — write the ones that pass; everything after `write`
failed. This is one half of quicksort (week 24).

**Keep at most k of each** — compare against `xs[write - k]` instead. The
generalisation the `write - 1` form gives you for free.

## Fast and slow is the same family

Week 20's cycle detection and middle-finding also move two pointers forward at
different speeds. The difference is only what decides the speeds: there, a fixed
ratio; here, a condition.

> ⚠️ **Common mistakes:** comparing against `xs[read - 1]`; forgetting the empty
> case; and assuming the array's `length` changed when only the return value did.
""",
            warmup=[
                _q("The write pointer marks…",
                   ["the current element", "where the next KEPT element goes", "the end",
                    "the duplicate"], 1,
                   "Read visits; write keeps."),
                _q("An in-place filter returns…",
                   ["a new array", "the new length", "void", "a boolean"], 1,
                   "The caller slices to it."),
                _q("`xs[write - 1]` is preferable to `xs[read - 1]` because…",
                   ["read - 1 gives a wrong answer here", "both work, but only one is correct for a reason you can state in a sentence",
                    "it is faster", "of types"], 1,
                   "They agree here; one agrees by accident."),
                _q("Its auxiliary space is…",
                   ["O(n)", "O(1)", "O(log n)", "O(n²)"], 1,
                   "Which is the whole reason to prefer it over a Set."),
            ],
            exercises=[
                _ex("tscourse-w22-sd-1", "De-duplicate in place",
                    "Compare against the last kept element, and advance the write pointer when you keep one.",
                    _SORTED +
                    'function dedupe(xs: number[]): number {\n'
                    '  if (xs.length === 0) {\n'
                    '    return 0;\n  }\n'
                    '  let write = 1;\n'
                    '  for (let read = 1; read < xs.length; read = read + 1) {\n'
                    '    if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {\n'
                    '      xs[write] = xs[read] ?? 0;\n'
                    '      write = write + 1;\n    }\n  }\n'
                    '  return write;\n}\n'
                    'const xs = [...nums];\n'
                    'const n = dedupe(xs);\n'
                    'console.log(`${n} ${xs.slice(0, n).join(",")}`);\n',
                    '    if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {',
                    [("1 1 2 2 2 3", "3 1,2,3"), ("5", "1 5"), ("1 2 3", "3 1,2,3")],
                    hints=["Keep it when it differs from the last thing you kept.",
                           "Write if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {"],
                    difficulty="Hard"),
                _ex("tscourse-w22-sd-2", "Move the zeroes",
                    "Write every non-zero forward, then pad the tail.",
                    _NUMS +
                    'const xs = [...nums];\n'
                    'let write = 0;\n'
                    'for (let read = 0; read < xs.length; read = read + 1) {\n'
                    '  if ((xs[read] ?? 0) !== 0) {\n'
                    '    xs[write] = xs[read] ?? 0;\n'
                    '    write = write + 1;\n  }\n}\n'
                    'while (write < xs.length) {\n'
                    '  xs[write] = 0;\n'
                    '  write = write + 1;\n}\n'
                    'console.log(xs.join(","));\n',
                    'while (write < xs.length) {\n'
                    '  xs[write] = 0;\n'
                    '  write = write + 1;\n}',
                    [("0 1 0 2 3", "1,2,3,0,0"), ("1 2", "1,2"), ("0 0", "0,0")],
                    hints=["Everything from the write pointer onwards has to become zero.",
                           "Write the while loop that fills the tail."],
                    difficulty="Medium"),
                _ex("tscourse-w22-sd-3", "Partition by a predicate",
                    "Keep the small values at the front and report how many there were.",
                    _NUMS +
                    'const xs = [...nums];\n'
                    'let write = 0;\n'
                    'for (let read = 0; read < xs.length; read = read + 1) {\n'
                    '  if ((xs[read] ?? 0) < 5) {\n'
                    '    const t = xs[write] ?? 0;\n'
                    '    xs[write] = xs[read] ?? 0;\n'
                    '    xs[read] = t;\n'
                    '    write = write + 1;\n  }\n}\n'
                    'console.log(`${write} ${xs.slice(0, write).join(",")}`);\n',
                    '    const t = xs[write] ?? 0;\n'
                    '    xs[write] = xs[read] ?? 0;\n'
                    '    xs[read] = t;',
                    [("1 9 2 8 3", "3 1,2,3"), ("9 8", "0 "), ("1 2", "2 1,2")],
                    hints=["Swap rather than overwrite, so nothing is lost.",
                           "Three lines: save, overwrite, put the saved value where it came from."],
                    difficulty="Hard"),
                _ex("tscourse-w22-sd-4", "Keep at most two of each",
                    "Compare against the element two places behind the write pointer.",
                    _SORTED +
                    'function atMostTwo(xs: number[]): number {\n'
                    '  let write = 0;\n'
                    '  for (let read = 0; read < xs.length; read = read + 1) {\n'
                    '    if (write < 2 || (xs[read] ?? 0) !== (xs[write - 2] ?? 0)) {\n'
                    '      xs[write] = xs[read] ?? 0;\n'
                    '      write = write + 1;\n    }\n  }\n'
                    '  return write;\n}\n'
                    'const xs = [...nums];\n'
                    'const n = atMostTwo(xs);\n'
                    'console.log(`${n} ${xs.slice(0, n).join(",")}`);\n',
                    '    if (write < 2 || (xs[read] ?? 0) !== (xs[write - 2] ?? 0)) {',
                    [("1 1 1 2 2 3", "5 1,1,2,2,3"), ("1 1", "2 1,1")],
                    hints=["The first two are always kept; after that, compare against two back.",
                           "Write if (write < 2 || (xs[read] ?? 0) !== (xs[write - 2] ?? 0)) {"],
                    difficulty="Hard"),
                _ex("tscourse-w22-sd-5", "Count what it allocated",
                    "Report the extra slots used, which is zero — the whole point.",
                    _SORTED +
                    'let slots = 0;\n'
                    'const xs = [...nums];\n'
                    'let write = 1;\n'
                    'for (let read = 1; read < xs.length; read = read + 1) {\n'
                    '  if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {\n'
                    '    xs[write] = xs[read] ?? 0;\n'
                    '    write = write + 1;\n  }\n}\n'
                    'console.log(`kept=${write} extraSlots=${slots}`);\n',
                    'console.log(`kept=${write} extraSlots=${slots}`);',
                    [("1 1 2 3", "kept=3 extraSlots=0")],
                    hints=["Nothing was allocated, which is what distinguishes this from a Set.",
                           "Write console.log(`kept=${write} extraSlots=${slots}`);"],
                    difficulty="Easy"),
                _fix("tscourse-w22-sd-fix1", "Fix the count for an empty array",
                     "`write` starts at 1 because the first element is always kept — except when there is no "
                     "first element. On empty input the loop never runs and the function reports **1** kept item "
                     "out of nothing. Every in-place compaction of this shape needs that guard, and it is the "
                     "case nobody tests.",
                     _SORTED +
                     'function dedupe(xs: number[]): number {\n'
                     '  let write = 1;\n'
                     '  for (let read = 1; read < xs.length; read = read + 1) {\n'
                     '    if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {\n'
                     '      xs[write] = xs[read] ?? 0;\n'
                     '      write = write + 1;\n    }\n  }\n'
                     '  return write;\n}\n'
                     'const xs = [...nums];\n'
                     'const n = dedupe(xs);\n'
                     'console.log(`${n} ${xs.slice(0, n).join(",")}`);\n',
                     _SORTED +
                     'function dedupe(xs: number[]): number {\n'
                     '  if (xs.length === 0) {\n'
                     '    return 0;\n  }\n'
                     '  let write = 1;\n'
                     '  for (let read = 1; read < xs.length; read = read + 1) {\n'
                     '    if ((xs[read] ?? 0) !== (xs[write - 1] ?? 0)) {\n'
                     '      xs[write] = xs[read] ?? 0;\n'
                     '      write = write + 1;\n    }\n  }\n'
                     '  return write;\n}\n'
                     'const xs = [...nums];\n'
                     'const n = dedupe(xs);\n'
                     'console.log(`${n} ${xs.slice(0, n).join(",")}`);\n',
                     [("", "0 "), ("1 1 2", "2 1,2"), ("5", "1 5")],
                     hints=["The starter reports 1 for an array with nothing in it.",
                            "`write = 1` assumes there is a first element to have kept.",
                            "Return 0 immediately when the array is empty."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Partitioning by a predicate is one half of…",
                   ["merge sort", "quicksort", "binary search", "a Map"], 1,
                   "Week 24 builds the other half."),
                _q("Week 20's fast-and-slow pointers are…",
                   ["unrelated", "the same family — two pointers moving forward at different speeds",
                    "opposite ends", "a sort"], 1,
                   "Only what sets the speeds differs."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w22-merge", "Merging, and sort-then-sweep",
            "Two sorted inputs in one pass, and the O(n³) that becomes O(n²).",
            """
## Merging two sorted arrays

```ts
const out: number[] = [];
let i = 0;
let j = 0;
while (i < a.length && j < b.length) {
  if ((a[i] ?? 0) <= (b[j] ?? 0)) { out.push(a[i] ?? 0); i = i + 1; }
  else { out.push(b[j] ?? 0); j = j + 1; }
}
while (i < a.length) { out.push(a[i] ?? 0); i = i + 1; }   // drain a
while (j < b.length) { out.push(b[j] ?? 0); j = j + 1; }   // drain b
```

O(n + m), one pass. Three things worth noting:

* **Both tails must be drained.** The main loop stops as soon as *either* input is
  exhausted, so one of the two tails always has something left (unless both ran out
  together). Forgetting one is the classic bug, and it is silent on inputs where
  that side happens to finish last.
* **`<=`, not `<`.** With `<=` equal elements are taken from `a` first, which makes
  the merge **stable** — equal items keep their relative order. That matters the
  moment you are merging records rather than numbers.
* **This is the heart of merge sort.** Week 24 splits, recurses, and calls exactly
  this.

The same sweep gives you the **intersection** of two sorted arrays: advance the
smaller side, and when they are equal take it and advance both.

## Sort, then sweep

If the input is not sorted and you are allowed to reorder it, **sorting to enable a
sweep is usually a bargain** — week 21's table says why: O(n log n) is within a
factor of 20 of O(n) at a million items, and O(n²) is 50,000 times worse.

The canonical case is finding triples that sum to a target. The naive version is
three nested loops, O(n³). Sorted, it is one loop around a two-pointer sweep:

```ts
const xs = [...nums].sort((a, b) => a - b);
for (let i = 0; i < xs.length - 2; i = i + 1) {
  if (i > 0 && (xs[i] ?? 0) === (xs[i - 1] ?? 0)) { continue; }   // skip dup anchors
  let lo = i + 1;
  let hi = xs.length - 1;
  while (lo < hi) {
    const sum = (xs[i] ?? 0) + (xs[lo] ?? 0) + (xs[hi] ?? 0);
    if (sum === target) {
      out.push(`${xs[i]},${xs[lo]},${xs[hi]}`);
      lo = lo + 1;
      while (lo < hi && (xs[lo] ?? 0) === (xs[lo - 1] ?? 0)) { lo = lo + 1; }  // and here
    } else if (sum < target) { lo = lo + 1; }
    else { hi = hi - 1; }
  }
}
```

**O(n²)** — an O(n) sweep inside an O(n) loop, and the sort disappears into it.

## The two duplicate skips

Both are needed, and they do different jobs:

* **The anchor skip** (`i > 0 && xs[i] === xs[i-1]`) stops the same first element
  being used twice, which would produce the same triple twice.
* **The inner skip**, after recording a hit, advances past equal values so the
  *second* element does not repeat either.

On `[-1,0,1,2,-1,-4]` for target 0 the answer is `-1,-1,2` and `-1,0,1` — and
without the anchor skip the first of those appears twice. Duplicate handling is
most of what makes this problem fiddly, and it is worth writing out once by hand.

> ⚠️ **Common mistakes:** draining only one tail; `<` instead of `<=`, losing
> stability; and either duplicate skip missing.
""",
            warmup=[
                _q("After the main merge loop you must…",
                   ["stop", "drain BOTH tails", "sort", "reverse"], 1,
                   "One side always has something left."),
                _q("`<=` rather than `<` in the merge comparison makes it…",
                   ["faster", "stable — equal items keep their order", "correct", "shorter"], 1,
                   "Which matters for records."),
                _q("Merging is the heart of…",
                   ["quicksort", "merge sort", "binary search", "a heap"], 1,
                   "Week 24 adds the splitting."),
                _q("Sort-then-sweep turns the triple-sum problem from…",
                   ["O(n²) to O(n)", "O(n³) to O(n²)", "O(n) to O(log n)", "O(n²) to O(n log n)"], 1,
                   "An O(n) sweep inside an O(n) loop."),
            ],
            exercises=[
                _ex("tscourse-w22-mg-1", "Merge two sorted arrays",
                    "Take from whichever side is smaller, and drain both tails afterwards.",
                    'function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
                    '  const out: number[] = [];\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
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
                    'console.log(merge([1, 4, 7], [2, 3, 9]).join(","));\n',
                    '  while (i < a.length && j < b.length) {',
                    [("", "1,2,3,4,7,9")],
                    hints=["The main loop runs only while BOTH sides still have elements.",
                           "Write while (i < a.length && j < b.length) {"],
                    difficulty="Medium"),
                _ex("tscourse-w22-mg-2", "Drain the other tail",
                    "Add the second drain loop, so nothing is dropped.",
                    'function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
                    '  const out: number[] = [];\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
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
                    'console.log(merge([1, 2], [3, 4, 5]).join(","));\n',
                    '  while (j < b.length) {\n'
                    '    out.push(b[j] ?? 0);\n'
                    '    j = j + 1;\n  }',
                    [("", "1,2,3,4,5")],
                    hints=["Here it is `b` that has elements left over.",
                           "Write the drain loop for j."],
                    difficulty="Medium"),
                _ex("tscourse-w22-mg-3", "Intersection of two sorted arrays",
                    "Advance the smaller side; when they match, take it and advance both.",
                    'function intersect(a: readonly number[], b: readonly number[]): readonly number[] {\n'
                    '  const out: number[] = [];\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
                    '    const x = a[i] ?? 0;\n'
                    '    const y = b[j] ?? 0;\n'
                    '    if (x === y) {\n'
                    '      out.push(x);\n'
                    '      i = i + 1;\n'
                    '      j = j + 1;\n'
                    '    } else if (x < y) {\n'
                    '      i = i + 1;\n'
                    '    } else {\n'
                    '      j = j + 1;\n    }\n  }\n'
                    '  return out;\n}\n'
                    'console.log(intersect([1, 3, 5, 7], [3, 4, 5]).join(","));\n',
                    '    if (x === y) {\n'
                    '      out.push(x);\n'
                    '      i = i + 1;\n'
                    '      j = j + 1;',
                    [("", "3,5")],
                    hints=["A match belongs in the output, and both pointers move past it.",
                           "Write the equality branch: push, then advance both."],
                    difficulty="Medium"),
                _ex("tscourse-w22-mg-4", "Count the merge's steps",
                    "Report how many elements were examined, which is n + m.",
                    'let steps = 0;\n'
                    'function merge(a: readonly number[], b: readonly number[]): number {\n'
                    '  let i = 0;\n'
                    '  let j = 0;\n'
                    '  while (i < a.length && j < b.length) {\n'
                    '    steps = steps + 1;\n'
                    '    if ((a[i] ?? 0) <= (b[j] ?? 0)) {\n'
                    '      i = i + 1;\n'
                    '    } else {\n'
                    '      j = j + 1;\n    }\n  }\n'
                    '  steps = steps + (a.length - i) + (b.length - j);\n'
                    '  return steps;\n}\n'
                    'console.log(merge([1, 4, 7], [2, 3, 9]));\n',
                    '  steps = steps + (a.length - i) + (b.length - j);',
                    [("", "6")],
                    hints=["Whatever is left in either tail is still examined once each.",
                           "Write steps = steps + (a.length - i) + (b.length - j);"],
                    difficulty="Medium"),
                _ex("tscourse-w22-mg-5", "Triples, sorted and swept",
                    "Skip a repeated anchor, so each triple appears once.",
                    _NUMS +
                    'function triples(input: readonly number[], target: number): readonly string[] {\n'
                    '  const xs = [...input].sort((a, b) => a - b);\n'
                    '  const out: string[] = [];\n'
                    '  for (let i = 0; i < xs.length - 2; i = i + 1) {\n'
                    '    if (i > 0 && (xs[i] ?? 0) === (xs[i - 1] ?? 0)) {\n'
                    '      continue;\n    }\n'
                    '    let lo = i + 1;\n'
                    '    let hi = xs.length - 1;\n'
                    '    while (lo < hi) {\n'
                    '      const sum = (xs[i] ?? 0) + (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                    '      if (sum === target) {\n'
                    '        out.push(`${xs[i] ?? 0},${xs[lo] ?? 0},${xs[hi] ?? 0}`);\n'
                    '        lo = lo + 1;\n'
                    '        while (lo < hi && (xs[lo] ?? 0) === (xs[lo - 1] ?? 0)) {\n'
                    '          lo = lo + 1;\n        }\n'
                    '      } else if (sum < target) {\n'
                    '        lo = lo + 1;\n'
                    '      } else {\n'
                    '        hi = hi - 1;\n      }\n    }\n  }\n'
                    '  return out;\n}\n'
                    'console.log(triples(nums, 0).join(" | "));\n',
                    '    if (i > 0 && (xs[i] ?? 0) === (xs[i - 1] ?? 0)) {\n'
                    '      continue;\n    }',
                    [("-1 0 1 2 -1 -4", "-1,-1,2 | -1,0,1"), ("1 2 3", "")],
                    hints=["An anchor equal to the previous one would produce the same triples again.",
                           "Guard `i > 0` first, then compare with the element before.",
                           "Write if (i > 0 && (xs[i] ?? 0) === (xs[i - 1] ?? 0)) { continue; }"],
                    difficulty="Hard"),
                _fix("tscourse-w22-mg-fix1", "Fix the merge that dropped a tail",
                     "`merge([1,2], [3,4,5])` returns `1,2` — the main loop stops the moment `a` runs out, and nothing drains what is left of `b`.",
                     'function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
                     '  const out: number[] = [];\n'
                     '  let i = 0;\n'
                     '  let j = 0;\n'
                     '  while (i < a.length && j < b.length) {\n'
                     '    if ((a[i] ?? 0) <= (b[j] ?? 0)) {\n'
                     '      out.push(a[i] ?? 0);\n'
                     '      i = i + 1;\n'
                     '    } else {\n'
                     '      out.push(b[j] ?? 0);\n'
                     '      j = j + 1;\n    }\n  }\n'
                     '  while (i < a.length) {\n'
                     '    out.push(a[i] ?? 0);\n'
                     '    i = i + 1;\n  }\n'
                     '  return out;\n}\n'
                     'console.log(merge([1, 2], [3, 4, 5]).join(","));\n',
                     'function merge(a: readonly number[], b: readonly number[]): readonly number[] {\n'
                     '  const out: number[] = [];\n'
                     '  let i = 0;\n'
                     '  let j = 0;\n'
                     '  while (i < a.length && j < b.length) {\n'
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
                     'console.log(merge([1, 2], [3, 4, 5]).join(","));\n',
                     [("", "1,2,3,4,5")],
                     hints=["Only one tail is drained, and the input was chosen so it is the wrong one.",
                            "The bug is silent whenever `a` happens to finish last.",
                            "Add the drain loop for `j`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Draining only one tail is a dangerous bug because…",
                   ["it crashes", "it is silent on inputs where that side finishes last", "it is slow",
                    "of types"], 1,
                   "Half your tests pass."),
                _q("The triple sweep needs TWO duplicate skips because…",
                   ["one is enough", "the anchor and the second element can each repeat", "of sorting",
                    "of the target"], 1,
                   "They do different jobs."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #22 — the search toolkit",
        """
One sorted ledger, five questions, each answered in O(log n) — and each printing
the number of binary-search steps it took, so the claim is evidenced rather than
asserted.

Input: the amounts on the first line, then one query per line.

```
100 250 250 250 400 900
? 250
+ 300
# 250
[ 200 500
~ 700
```

```
?  250  present at 1  steps 3
+  300  insert at 4  steps 3
#  250  count 3  steps 6
[  200  500  in range 4  steps 6
~  700  nearest 900  steps 3
Queries:  5
Steps:    21
```

**The five query types**, all built from the two bounds:

| line | question | answer |
|---|---|---|
| `? x` | is x present? | `present at <lowerBound>` or `absent` |
| `+ x` | where would x go? | `insert at <lowerBound>` |
| `# x` | how many x? | `count <upper - lower>` |
| `[ a b` | how many in [a, b]? | `in range <upper(b) - lower(a)>` |
| `~ x` | nearest value to x? | `nearest <value>` |

**What makes it a rep rather than a formatting exercise:**

1. **One instrumented `lowerBound`**, counting its own iterations into a total.
   `upperBound` is the same function with `<=`; `#` and `[` therefore cost **two**
   searches, and the step counts must show that.
2. **`~` is the interesting one.** The lower bound gives you the first value `>= x`;
   the nearest value is that one **or the one before it**, whichever is closer.
   Both ends need care: a bound of `0` has nothing before it, and a bound of
   `length` has nothing at it. Ties go to the smaller value.
3. **Presence needs the length check** before comparing (lesson 3), because the
   bound can legitimately be one past the end.

The totals line reports the query count and the summed steps. An unrecognised
query line is skipped and does not count. Empty input, or no queries, prints
`Queries:  0` and `Steps:    0`.
""",
        _ch("tscourse-w22-capstone", "Interview rep #22", "Hard",
            "Answer five kinds of query about a sorted ledger with two bounds, counting the "
            "binary-search steps each one costs.",
            _FS +
            'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
            'const xs: readonly number[] = (lines[0] ?? "")\n'
            '  .trim()\n'
            '  .split(/\\s+/)\n'
            '  .filter((s) => s !== "")\n'
            '  .map(Number)\n'
            '  .sort((a, b) => a - b);\n'
            'let steps = 0;\n'
            'function bound(target: number, inclusive: boolean): number {\n'
            '  let lo = 0;\n'
            '  let hi = xs.length;\n'
            '  while (lo < hi) {\n'
            '    steps = steps + 1;\n'
            '    const mid = Math.floor((lo + hi) / 2);\n'
            '    const v = xs[mid] ?? 0;\n'
            '    if (inclusive ? v <= target : v < target) {\n'
            '      lo = mid + 1;\n'
            '    } else {\n'
            '      hi = mid;\n    }\n  }\n'
            '  return lo;\n}\n'
            'function nearest(target: number): number {\n'
            '  const i = bound(target, false);\n'
            '  const at = i < xs.length ? xs[i] ?? 0 : Number.MAX_SAFE_INTEGER;\n'
            '  const before = i > 0 ? xs[i - 1] ?? 0 : Number.MIN_SAFE_INTEGER;\n'
            '  const gapAt = Math.abs(at - target);\n'
            '  const gapBefore = Math.abs(target - before);\n'
            '  return gapBefore <= gapAt ? before : at;\n}\n'
            'let queries = 0;\n'
            'for (const line of lines.slice(1)) {\n'
            '  const parts = line.trim().split(/\\s+/);\n'
            '  const kind = parts[0] ?? "";\n'
            '  const a = Number(parts[1] ?? "0");\n'
            '  const before = steps;\n'
            '  if (kind === "?") {\n'
            '    const i = bound(a, false);\n'
            '    const present = i < xs.length && (xs[i] ?? 0) === a;\n'
            '    queries = queries + 1;\n'
            '    console.log(`?  ${a}  ${present ? `present at ${i}` : "absent"}  steps ${steps - before}`);\n'
            '  } else if (kind === "+") {\n'
            '    const i = bound(a, false);\n'
            '    queries = queries + 1;\n'
            '    console.log(`+  ${a}  insert at ${i}  steps ${steps - before}`);\n'
            '  } else if (kind === "#") {\n'
            '    const count = bound(a, true) - bound(a, false);\n'
            '    queries = queries + 1;\n'
            '    console.log(`#  ${a}  count ${count}  steps ${steps - before}`);\n'
            '  } else if (kind === "[") {\n'
            '    const b = Number(parts[2] ?? "0");\n'
            '    const count = bound(b, true) - bound(a, false);\n'
            '    queries = queries + 1;\n'
            '    console.log(`[  ${a}  ${b}  in range ${count}  steps ${steps - before}`);\n'
            '  } else if (kind === "~") {\n'
            '    const value = xs.length === 0 ? 0 : nearest(a);\n'
            '    queries = queries + 1;\n'
            '    console.log(`~  ${a}  nearest ${value}  steps ${steps - before}`);\n  }\n}\n'
            'console.log(`Queries:  ${queries}`);\n'
            'console.log(`Steps:    ${steps}`);\n',
            'let steps = 0;\n'
            'function bound(target: number, inclusive: boolean): number {\n'
            '  let lo = 0;\n'
            '  let hi = xs.length;\n'
            '  while (lo < hi) {\n'
            '    steps = steps + 1;\n'
            '    const mid = Math.floor((lo + hi) / 2);\n'
            '    const v = xs[mid] ?? 0;\n'
            '    if (inclusive ? v <= target : v < target) {\n'
            '      lo = mid + 1;\n'
            '    } else {\n'
            '      hi = mid;\n    }\n  }\n'
            '  return lo;\n}\n'
            'function nearest(target: number): number {\n'
            '  const i = bound(target, false);\n'
            '  const at = i < xs.length ? xs[i] ?? 0 : Number.MAX_SAFE_INTEGER;\n'
            '  const before = i > 0 ? xs[i - 1] ?? 0 : Number.MIN_SAFE_INTEGER;\n'
            '  const gapAt = Math.abs(at - target);\n'
            '  const gapBefore = Math.abs(target - before);\n'
            '  return gapBefore <= gapAt ? before : at;\n}',
            [("100 250 250 250 400 900\n? 250\n+ 300\n# 250\n[ 200 500\n~ 700", "?  250  present at 1  steps 3\n+  300  insert at 4  steps 3\n#  250  count 3  steps 6\n[  200  500  in range 4  steps 6\n~  700  nearest 900  steps 3\nQueries:  5\nSteps:    21"),
             ("100 200\n? 999\n~ 100\n~ 300", "?  999  absent  steps 1\n~  100  nearest 100  steps 2\n~  300  nearest 200  steps 1\nQueries:  3\nSteps:    4"),
             ("50\n# 50\n[ 0 100", "#  50  count 1  steps 2\n[  0  100  in range 1  steps 2\nQueries:  2\nSteps:    4"),
             ("100 200\nzz 1", "Queries:  0\nSteps:    0")],
            hints=["One `bound` function with an `inclusive` flag is both bounds — the only difference is `<=` versus `<`.",
                   "Count the steps inside `bound`, and take `steps - before` around each query to report that query's share.",
                   "`#` and `[` each call `bound` twice, so their step counts are roughly double.",
                   "For `~`, the candidates are the value AT the lower bound and the one BEFORE it; guard both ends with sentinels.",
                   "Ties in `~` go to the smaller value, which is what `gapBefore <= gapAt` expresses.",
                   "Presence needs `i < xs.length` before comparing — the bound can be one past the end.",
                   "An unrecognised query falls through every branch and increments nothing."]),
        example_io="?  250  present at 1  steps 3\n+  300  insert at 4  steps 3\n#  250  count 3  steps 6\n[  200  500  in range 4  steps 6\n~  700  nearest 900  steps 3\nQueries:  5\nSteps:    21",
        rubric=["one bound function serves both bounds, differing only by the comparison",
                "every query's step count is measured, not estimated",
                "`#` and `[` visibly cost two searches",
                "`~` considers the value at the bound and the one before it, and guards both ends",
                "ties in `~` resolve to the smaller value",
                "presence is checked with the length test before the comparison",
                "the ledger is sorted as it is read rather than assumed sorted",
                "an unrecognised query line is skipped and not counted"],
        stretch=_ch("tscourse-w22-capstone-stretch", "Interview rep #22 (stretch)", "Hard",
                    "Add a `2 <target>` query: find two amounts in the ledger that sum to the "
                    "target, using a two-pointer sweep rather than a search — and report the sweep "
                    "steps beside the binary-search steps, so the two techniques' costs sit side by "
                    "side on the same data.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
                    'const xs: readonly number[] = (lines[0] ?? "")\n'
                    '  .trim()\n'
                    '  .split(/\\s+/)\n'
                    '  .filter((s) => s !== "")\n'
                    '  .map(Number)\n'
                    '  .sort((a, b) => a - b);\n'
                    'let sweepSteps = 0;\n'
                    'function pair(target: number): string {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  while (lo < hi) {\n'
                    '    sweepSteps = sweepSteps + 1;\n'
                    '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                    '    if (sum === target) {\n'
                    '      return `${xs[lo] ?? 0}+${xs[hi] ?? 0}`;\n    }\n'
                    '    if (sum < target) {\n'
                    '      lo = lo + 1;\n'
                    '    } else {\n'
                    '      hi = hi - 1;\n    }\n  }\n'
                    '  return "none";\n}\n'
                    'for (const line of lines.slice(1)) {\n'
                    '  const parts = line.trim().split(/\\s+/);\n'
                    '  if ((parts[0] ?? "") !== "2") {\n'
                    '    continue;\n  }\n'
                    '  const target = Number(parts[1] ?? "0");\n'
                    '  const before = sweepSteps;\n'
                    '  const answer = pair(target);\n'
                    '  console.log(`2  ${target}  ${answer}  sweep ${sweepSteps - before}`);\n}\n'
                    'console.log(`Pairs:    ${xs.length < 2 ? 0 : (xs.length * (xs.length - 1)) / 2}`);\n'
                    'console.log(`Sweep:    ${sweepSteps}`);\n',
                    'let sweepSteps = 0;\n'
                    'function pair(target: number): string {\n'
                    '  let lo = 0;\n'
                    '  let hi = xs.length - 1;\n'
                    '  while (lo < hi) {\n'
                    '    sweepSteps = sweepSteps + 1;\n'
                    '    const sum = (xs[lo] ?? 0) + (xs[hi] ?? 0);\n'
                    '    if (sum === target) {\n'
                    '      return `${xs[lo] ?? 0}+${xs[hi] ?? 0}`;\n    }\n'
                    '    if (sum < target) {\n'
                    '      lo = lo + 1;\n'
                    '    } else {\n'
                    '      hi = hi - 1;\n    }\n  }\n'
                    '  return "none";\n}',
                    [("100 250 400 900\n2 500\n2 1000\n2 7", "2  500  100+400  sweep 2\n2  1000  100+900  sweep 1\n2  7  none  sweep 3\nPairs:    6\nSweep:    6"),
                     ("50\n2 100", "2  100  none  sweep 0\nPairs:    0\nSweep:    0")],
                    hints=["The sweep needs no binary search at all — it is one pass from both ends.",
                           "`Pairs:` reports n(n-1)/2, which is what a nested loop would have examined.",
                           "Compare that against the sweep total: that contrast is the entire point of the query.",
                           "A ledger with fewer than two amounts has no pairs, and the sweep never enters its loop."]),
    ),
))
