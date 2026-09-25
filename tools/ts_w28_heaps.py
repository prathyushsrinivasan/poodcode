# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 28 — heaps & intervals.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# WHY THE WEEK OPENS WHERE IT DOES: week 27 ended on an O(V²) Dijkstra whose step 1
# — "the smallest item, repeatedly, as items arrive" — was done by scanning, and
# counted. The heap is the answer to that cost, the same move weeks 18 → 19 made.
#
# THE CLASS. TS_ROADMAP: "Heaps need a generic priority queue class — another
# dependency on week 11." It is `MinHeap<T>` with a comparator, and it obeys the
# rule the roadmap's trap 1 records: **no parameter properties** — they do not run
# in strip-only mode — so every field is declared the long way and assigned in the
# constructor. The class never needs `!`: comparisons go through `less(i, j)`,
# which reads both slots and treats a missing one as "not less".
#
# DETERMINISM. A heap is not stable, so two correct heaps can pop equal-priority
# items in different orders. Every exercise that pops records breaks ties in its
# comparator (by name), so the output is the same for every correct heap.
#
# INTERVALS use half-open [start, end): a meeting ending at 2 and one starting at 2
# do not overlap. Where merging would join touching blocks (the capstone's busy
# time), the prompt says so explicitly. The tie rule for the sweep line (ends
# before starts at the same time) is a shipped `fix`, because getting it wrong
# double-counts rooms without any other symptom.
# ---------------------------------------------------------------------------

_HEAP = (
    'class MinHeap<T> {\n'
    '  private readonly items: T[] = [];\n'
    '  private readonly before: (a: T, b: T) => number;\n'
    '  compares = 0;\n'
    '  constructor(before: (a: T, b: T) => number) {\n'
    '    this.before = before;\n  }\n'
    '  get size(): number {\n'
    '    return this.items.length;\n  }\n'
    '  peek(): T | undefined {\n'
    '    return this.items[0];\n  }\n'
    '  private less(i: number, j: number): boolean {\n'
    '    const a = this.items[i];\n'
    '    const b = this.items[j];\n'
    '    this.compares = this.compares + 1;\n'
    '    return a !== undefined && b !== undefined && this.before(a, b) < 0;\n  }\n'
    '  private swap(i: number, j: number): void {\n'
    '    const a = this.items[i];\n'
    '    const b = this.items[j];\n'
    '    if (a === undefined || b === undefined) {\n'
    '      return;\n    }\n'
    '    this.items[i] = b;\n'
    '    this.items[j] = a;\n  }\n'
    '  push(x: T): void {\n'
    '    this.items.push(x);\n'
    '    let i = this.items.length - 1;\n'
    '    while (i > 0) {\n'
    '      const parent = Math.floor((i - 1) / 2);\n'
    '      if (!this.less(i, parent)) {\n'
    '        return;\n      }\n'
    '      this.swap(i, parent);\n'
    '      i = parent;\n    }\n  }\n'
    '  pop(): T | undefined {\n'
    '    const top = this.items[0];\n'
    '    const last = this.items.pop();\n'
    '    if (this.items.length > 0 && last !== undefined) {\n'
    '      this.items[0] = last;\n'
    '      let i = 0;\n'
    '      for (;;) {\n'
    '        const left = 2 * i + 1;\n'
    '        const right = left + 1;\n'
    '        let best = i;\n'
    '        if (left < this.items.length && this.less(left, best)) {\n'
    '          best = left;\n        }\n'
    '        if (right < this.items.length && this.less(right, best)) {\n'
    '          best = right;\n        }\n'
    '        if (best === i) {\n'
    '          break;\n        }\n'
    '        this.swap(i, best);\n'
    '        i = best;\n      }\n    }\n'
    '    return top;\n  }\n'
    '  toArray(): readonly T[] {\n'
    '    return [...this.items];\n  }\n}\n'
)

# Intervals as `start-end` words.
_IVALS = (
    'interface Iv {\n'
    '  readonly start: number;\n'
    '  readonly end: number;\n}\n'
    'const ivs: Iv[] = words.filter((w) => w !== "").map((w) => {\n'
    '  const [s, e] = w.split("-").map(Number);\n'
    '  return { start: s ?? 0, end: e ?? 0 };\n});\n'
    'function show(xs: readonly Iv[]): string {\n'
    '  return xs.map((x) => `${x.start}-${x.end}`).join(" ");\n}\n'
)


def _heap_with(old, new):
    """The heap source with one line replaced — for the `fix` starters."""
    assert old in _HEAP, old
    return _HEAP.replace(old, new, 1)


# --- Week 28 --------------------------------------------------------------
_WEEKS.append(_week(
    28, 7, _M7,
    "Heaps & Intervals",
    "Week 27's Dijkstra scanned for the smallest item every time. A heap hands it over in O(log n). Then intervals — sort, sweep, and a heap of end times — and the one greedy that is provably right.",
    """
Week 27 ended on a cost. Dijkstra needs, over and over, **the smallest item among
those waiting** — and items keep arriving. Scanning an array for it is O(n) a time.
Keeping the array sorted makes finding it O(1) but every insert O(n).

A **heap** does both in **O(log n)**. It is the data structure behind every
"priority queue", and there is no built-in one in JavaScript — so you will write it,
as a generic class, once.

## What a heap is

A binary tree where **every parent is ≤ its children** — so the smallest is always
at the root — and which is **complete**: filled level by level, left to right. That
shape is what lets it live in a plain array with no pointers at all:

```
            1                 index:  0  1  2  3  4  5
          /   \\                value:  1  3  2  7  4  9
         3     2
        / \\   /              parent(i)   = floor((i - 1) / 2)
       7   4 9               children(i) = 2i + 1, 2i + 2
```

A complete tree of n items is about log₂ n levels deep, and each operation walks one
root-to-leaf path. That is the whole reason it is fast.

## The second half: intervals

"Merge overlapping meetings", "how many rooms?", "the most meetings one person can
attend." Every one starts the same way — **sort by start** (or end), then **sweep** —
and the rooms question uses a heap of end times. It is week 24's sorting, week 22's
sweep and this week's heap on the same data.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Say what a heap guarantees, and what it does not",
        "Map a complete binary tree onto an array: parent and child indexes",
        "Write a generic MinHeap<T> class with a comparator, without parameter properties",
        "Push with sift-up and pop with sift-down, and say why each is O(log n)",
        "Turn a min-heap into a max-heap by changing only the comparator",
        "Keep the k largest items with a size-k min-heap",
        "Merge k sorted lists with a heap",
        "Run Dijkstra with a heap, skipping stale entries",
        "Merge overlapping intervals after sorting by start",
        "Count the rooms a schedule needs, with a heap or a sweep line",
        "Order sweep-line events correctly at equal times",
        "Pick the most non-overlapping intervals greedily by earliest end, and say why it is right",
    ],
    why="Heaps and intervals are two of the most common interview topics after graphs and DP, and they meet in the middle: 'meeting rooms', 'top k', 'merge k lists' and 'Dijkstra' all reach for a priority queue. Writing the heap yourself — as a typed, generic class — is also the course's last big piece of class design before the type-level month.",
    est_minutes=480,
    glossary=[
        _gloss("priority queue", "Hand back the smallest (or most urgent) item next, however items arrive."),
        _gloss("heap", "A complete binary tree where every parent is ≤ its children. The usual priority queue."),
        _gloss("heap property", "parent ≤ child, everywhere. Says nothing about siblings."),
        _gloss("complete tree", "Filled level by level, left to right — so it fits in an array with no gaps."),
        _gloss("sift up", "After a push: swap the new item with its parent while it is smaller."),
        _gloss("sift down", "After a pop: move the last item to the root and swap it with its smaller child."),
        _gloss("min-heap / max-heap", "The same structure with the comparator flipped."),
        _gloss("heapsort", "Push everything, pop everything: O(n log n), in place if done in the array."),
        _gloss("top-k", "Keep a size-k min-heap: its root is the smallest of the k largest."),
        _gloss("lazy deletion", "Leave outdated heap entries in place and skip them when popped."),
        _gloss("interval", "A [start, end) range. Half-open: a meeting ending at 2 does not clash with one starting at 2."),
        _gloss("merge intervals", "Sort by start; extend the current block while the next one overlaps it."),
        _gloss("sweep line", "Turn intervals into +1/-1 events, sort them, and walk through time."),
        _gloss("interval scheduling", "The most non-overlapping intervals: greedily take the one that ENDS first."),
    ],
    cheatsheet="""
```ts
// ---- a generic min-heap: fields the long way (no parameter properties) ----
class MinHeap<T> {
  private readonly items: T[] = [];
  private readonly before: (a: T, b: T) => number;
  constructor(before: (a: T, b: T) => number) { this.before = before; }
  get size(): number { return this.items.length; }
  peek(): T | undefined { return this.items[0]; }
  push(x: T): void { /* append, then sift UP */ }
  pop(): T | undefined { /* take root, move last to root, sift DOWN */ }
}
// parent(i) = Math.floor((i - 1) / 2)     children: 2i + 1, 2i + 2

new MinHeap<number>((a, b) => a - b);            // min-heap
new MinHeap<number>((a, b) => b - a);            // max-heap — only the comparator
new MinHeap<Job>((a, b) => a.pri - b.pri || a.name.localeCompare(b.name));  // ties broken

// ---- top-k largest: a min-heap of size k -------------------------------
for (const x of xs) { heap.push(x); if (heap.size > k) { heap.pop(); } }
// heap.peek() is the k-th largest

// ---- Dijkstra with a heap: skip stale entries ---------------------------
const top = heap.pop();
if (top.d > dist[top.node]) { continue; }        // an outdated entry

// ---- intervals: [start, end), sort first ---------------------------------
xs.sort((a, b) => a.start - b.start);
if (next.start <= cur.end) { cur.end = Math.max(cur.end, next.end); }   // merge

// rooms: a heap of end times
if (ends.size > 0 && (ends.peek() ?? 0) <= m.start) { ends.pop(); }   // a room freed
ends.push(m.end);                                 // rooms = the largest size seen

// sweep: +1 at start, -1 at end; at equal times the END comes first
events.sort((a, b) => a.t - b.t || a.delta - b.delta);

// the most non-overlapping: sort by END, take each that starts after the last taken
```

| operation | heap | sorted array | unsorted array |
|---|---|---|---|
| push | **log n** | n | 1 |
| smallest | 1 | 1 | n |
| pop smallest | **log n** | 1 (from the end) | n |
""",
    self_check=[
        "Can you state the heap property, and what it says nothing about?",
        "Can you give the parent and children of index i?",
        "Can you write a generic class without parameter properties?",
        "Can you write sift-up and sift-down from memory?",
        "Can you say why push and pop are O(log n)?",
        "Can you make a max-heap from a min-heap?",
        "Can you keep the k largest of a stream in O(n log k)?",
        "Can you say what a stale entry is in heap-based Dijkstra?",
        "Can you merge overlapping intervals, including one inside another?",
        "Can you count meeting rooms two ways?",
        "Can you say which event comes first when a meeting ends as another starts?",
        "Can you pick the most non-overlapping meetings, and say why earliest END and not earliest start?",
    ],
    review=[
        _q("A min-heap guarantees…",
           ["the array is sorted", "every parent is ≤ its children, so the root is the smallest",
            "siblings are ordered", "O(1) pop"], 1,
           "Nothing about siblings."),
        _q("In the array layout, the parent of index i is…",
           ["i / 2", "Math.floor((i - 1) / 2)", "i - 1", "2i + 1"], 1,
           "Children are 2i + 1 and 2i + 2."),
        _q("Push and pop are O(log n) because…",
           ["they sort", "each walks one path of a tree about log n deep", "of the comparator",
            "arrays are fast"], 1,
           "A complete tree is shallow."),
        _q("The class avoids `constructor(private readonly before: …)` because…",
           ["style", "parameter properties do not run in strip-only mode", "it is slower", "it is not generic"], 1,
           "Trap 1 in the roadmap."),
        _q("A max-heap is made from a min-heap by…",
           ["rewriting it", "flipping the comparator", "reversing the array", "popping twice"], 1,
           "(a, b) => b - a."),
        _q("The k largest of n items, with a heap, costs…",
           ["O(n²)", "O(n log k)", "O(k)", "O(n log n) always"], 1,
           "A heap of size k."),
        _q("In lazy-deletion Dijkstra, a popped entry with d > dist[node]…",
           ["is an error", "is outdated and is skipped", "is relaxed again", "ends the search"], 1,
           "A better route was already found."),
        _q("Merging intervals begins by…",
           ["sorting by end", "sorting by start", "a heap", "nothing"], 1,
           "Then one sweep."),
        _q("[1, 10] and [2, 3] merge to…",
           ["1-3", "1-10", "2-10", "two blocks"], 1,
           "Math.max of the ends."),
        _q("With half-open intervals, [1, 2) and [2, 3)…",
           ["overlap", "do not overlap", "are equal", "merge into 1-2"], 1,
           "One ends as the other starts."),
        _q("In the sweep line, at equal times…",
           ["starts first", "ends first — or touching meetings count as a clash", "either", "neither"], 1,
           "A room frees before it is reused."),
        _q("The most non-overlapping meetings are chosen by sorting on…",
           ["start", "end — earliest finish leaves the most room", "length", "nothing"], 1,
           "And this greedy is provably optimal."),
    ],
    milestone="Interview rep #28 — the scheduler. One list of meetings, three questions: the merged busy blocks, how many rooms the day needs (a heap of end times), and the most meetings one person could attend (the earliest-end greedy). Sorting, a sweep and a heap on the same data — and the end of Month 7.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w28-shape", "A tree in an array",
            "The heap property, and the index arithmetic that replaces pointers.",
            """
A **min-heap** keeps one promise: **every parent is less than or equal to its
children.** Follow any path down from the root and the values never decrease, so the
root is the smallest thing in the heap.

It promises **nothing** about siblings, or about anything not on the same path.
`[1, 3, 2, 7, 4, 9]` is a heap; it is not sorted, and it does not need to be. That
laziness is what makes it cheap: a sorted array must fix *everything* after an
insert, a heap only one path.

## No pointers

Week 20's trees had `left` and `right` fields. A heap is always a **complete** tree —
every level full except possibly the last, which fills left to right — so the nodes
can simply be numbered level by level and stored in an array:

```
parent(i)  = Math.floor((i - 1) / 2)
left(i)    = 2 * i + 1
right(i)   = 2 * i + 2
```

Index 4's parent is 1; index 1's children are 3 and 4. No gaps, no null children,
no allocation per node.

## How tall

A complete tree with n nodes has `Math.floor(Math.log2(n)) + 1` levels: a thousand
items is 10 levels, a million is 20. Push and pop each walk at most one
root-to-leaf path, so each is **O(log n)**.

## Checking the property

An array is a heap exactly when every index `i > 0` satisfies
`a[parent(i)] <= a[i]`. That one loop is also the best test you can write for your
own heap class.

> ⚠️ **Common mistakes:** `i / 2` for the parent (that is the 1-based formula);
> expecting a heap's array to be sorted; and forgetting that "min" and "max" are
> only a comparator apart.
""",
            warmup=[
                _q("In a min-heap, the root is…",
                   ["the largest", "the smallest", "the median", "the newest"], 1,
                   "Every path from it only increases."),
                _q("A heap's array is sorted…",
                   ["always", "not necessarily — only parent ≤ child is promised", "when full", "never"], 1,
                   "Siblings are unordered."),
                _q("The children of index 1 are…",
                   ["2 and 3", "3 and 4", "1 and 2", "4 and 5"], 1,
                   "2i + 1 and 2i + 2."),
                _q("A heap of a million items is about how many levels deep?",
                   ["1,000", "20", "1,000,000", "6"], 1,
                   "log₂ of a million."),
            ],
            exercises=[
                _ex("tscourse-w28-sh-1", "Where the parent is",
                    "Report the parent and children of an index.",
                    _LINE +
                    'const i = Number(line);\n'
                    'const parent = Math.floor((i - 1) / 2);\n'
                    'console.log(`parent ${i === 0 ? "none" : parent} children ${2 * i + 1} ${2 * i + 2}`);\n',
                    'const parent = Math.floor((i - 1) / 2);',
                    [("4", "parent 1 children 9 10"), ("1", "parent 0 children 3 4"), ("0", "parent none children 1 2")],
                    hints=["Children of p are 2p + 1 and 2p + 2 — invert that.",
                           "Write const parent = Math.floor((i - 1) / 2);"],
                    difficulty="Easy"),
                _ex("tscourse-w28-sh-2", "Is it a heap?",
                    "Check that every element is at least as large as its parent.",
                    _NUMS +
                    'let ok = true;\n'
                    'for (let i = 1; i < nums.length; i = i + 1) {\n'
                    '  const parent = Math.floor((i - 1) / 2);\n'
                    '  if ((nums[parent] ?? 0) > (nums[i] ?? 0)) {\n'
                    '    ok = false;\n  }\n}\n'
                    'console.log(ok);\n',
                    '  if ((nums[parent] ?? 0) > (nums[i] ?? 0)) {\n'
                    '    ok = false;\n  }',
                    [("1 3 2 7 4 9", "true"), ("1 3 2 0", "false"), ("5", "true")],
                    hints=["A violation is a parent that is larger than its child.",
                           "if ((nums[parent] ?? 0) > (nums[i] ?? 0)) { ok = false; }"],
                    difficulty="Easy"),
                _ex("tscourse-w28-sh-3", "How tall",
                    "Report how many levels a heap of n items has.",
                    _LINE +
                    'const n = Number(line);\n'
                    'const levels = n === 0 ? 0 : Math.floor(Math.log2(n)) + 1;\n'
                    'console.log(levels);\n',
                    'const levels = n === 0 ? 0 : Math.floor(Math.log2(n)) + 1;',
                    [("1000", "10"), ("1000000", "20"), ("7", "3"), ("8", "4")],
                    hints=["Level k holds 2^k items, so n items need about log₂ n levels.",
                           "Write const levels = n === 0 ? 0 : Math.floor(Math.log2(n)) + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w28-sh-4", "Siblings are not ordered",
                    "Report whether a valid heap is also sorted — for two heaps that are both valid.",
                    'function isHeap(xs: readonly number[]): boolean {\n'
                    '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                    '    if ((xs[Math.floor((i - 1) / 2)] ?? 0) > (xs[i] ?? 0)) {\n'
                    '      return false;\n    }\n  }\n'
                    '  return true;\n}\n'
                    'function isSorted(xs: readonly number[]): boolean {\n'
                    '  for (let i = 1; i < xs.length; i = i + 1) {\n'
                    '    if ((xs[i - 1] ?? 0) > (xs[i] ?? 0)) {\n'
                    '      return false;\n    }\n  }\n'
                    '  return true;\n}\n'
                    'for (const xs of [[1, 2, 3, 4], [1, 3, 2, 7, 4, 9]]) {\n'
                    '  console.log(`heap=${isHeap(xs)} sorted=${isSorted(xs)}`);\n}\n',
                    '    if ((xs[i - 1] ?? 0) > (xs[i] ?? 0)) {',
                    [("", "heap=true sorted=true\nheap=true sorted=false")],
                    hints=["Sorted means every element is at least the one before it.",
                           "Write if ((xs[i - 1] ?? 0) > (xs[i] ?? 0)) {"],
                    difficulty="Easy"),
            ],
            quiz=[
                _q("Why does a heap not need pointers?",
                   ["it is small", "it is complete, so level-order numbering leaves no gaps", "it is sorted",
                    "it uses a Map"], 1,
                   "Indexes are enough."),
                _q("`i / 2` as the parent formula belongs to…",
                   ["0-based arrays", "1-based numbering, where the root is 1", "max-heaps", "nothing"], 1,
                   "In 0-based arrays it is floor((i - 1) / 2)."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w28-class", "The heap as a class",
            "Push, sift up, pop, sift down — generic, typed, and with no parameter properties.",
            """
Here is the whole class. Every exercise this week uses it.

```ts
class MinHeap<T> {
  private readonly items: T[] = [];
  private readonly before: (a: T, b: T) => number;

  constructor(before: (a: T, b: T) => number) {
    this.before = before;                       // the long way — see below
  }

  get size(): number { return this.items.length; }
  peek(): T | undefined { return this.items[0]; }
  ...
}
```

**Generic** (week 10), so one class serves numbers, records and `[distance, node]`
pairs; the **comparator** says what "smaller" means, exactly like `sort`'s.

## Why the constructor is written out

`constructor(private readonly before: …) {}` would be shorter, and it type-checks —
and then the program dies with `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`, because a
parameter property *emits code* and the judge only strips types (week 11). The
roadmap records this as the trap that cost the most time, and it is the reason every
class in a runnable exercise declares its fields separately.

## Push: sift up

Append at the end — the only place a complete tree can grow — then, while the new
item is smaller than its parent, swap them:

```ts
this.items.push(x);
let i = this.items.length - 1;
while (i > 0) {
  const parent = Math.floor((i - 1) / 2);
  if (!this.less(i, parent)) { return; }
  this.swap(i, parent);
  i = parent;
}
```

## Pop: sift down

Take the root. Move the **last** item into the root's place (the tree stays
complete), then, while it is larger than its **smaller** child, swap them:

```ts
let best = i;
if (left < n && this.less(left, best)) { best = left; }
if (right < n && this.less(right, best)) { best = right; }
if (best === i) { break; }
this.swap(i, best);
i = best;
```

It must be the *smaller* child: swapping with the larger one would put a larger
value above a smaller sibling, and break the property one level down.

## Typed without `!`

`this.items[i]` is `T | undefined`, and a generic `T` has no default to fall back
to. The class routes every comparison through `less(i, j)`, which reads both slots
and answers "not less" if either is missing — so no non-null assertion is needed
anywhere.

## Max-heaps for free

`new MinHeap<number>((a, b) => b - a)` is a max-heap. No second class.

> ⚠️ **Common mistakes:** a parameter property in the constructor; sifting down
> into the larger child; and comparing records without a tie-breaker, so equal
> priorities come out in an order the tests cannot predict.
""",
            warmup=[
                _q("A pushed item is first placed…",
                   ["at the root", "at the end of the array", "in sorted position", "anywhere"], 1,
                   "Then it sifts up."),
                _q("After popping, the root's place is filled by…",
                   ["the smaller child", "the LAST item, which then sifts down", "nothing", "the pushed item"], 1,
                   "So the tree stays complete."),
                _q("Sift-down swaps with…",
                   ["the larger child", "the smaller child", "the parent", "either"], 1,
                   "Or the property breaks one level down."),
                _q("A max-heap needs…",
                   ["a new class", "the comparator (a, b) => b - a", "a reversed array", "two heaps"], 1,
                   "One class, two comparators."),
            ],
            exercises=[
                _ex("tscourse-w28-cl-1", "Sift up",
                    "Swap the new item with its parent while it is smaller.",
                    _NUMS + _HEAP +
                    'const heap = new MinHeap<number>((a, b) => a - b);\n'
                    'for (const x of nums) {\n'
                    '  heap.push(x);\n}\n'
                    'console.log(heap.toArray().join(" "));\n',
                    '      if (!this.less(i, parent)) {\n'
                    '        return;\n      }\n'
                    '      this.swap(i, parent);\n'
                    '      i = parent;',
                    [("5 3 8 1", "1 3 8 5"), ("1 2 3", "1 2 3"), ("3 2 1", "1 3 2")],
                    hints=["Stop as soon as the item is not smaller than its parent.",
                           "Otherwise swap them and continue from the parent's index."],
                    difficulty="Medium"),
                _ex("tscourse-w28-cl-2", "Sift down into the smaller child",
                    "Pick the smaller of the two children (if they exist) as the candidate to swap with.",
                    _NUMS + _HEAP +
                    'const heap = new MinHeap<number>((a, b) => a - b);\n'
                    'for (const x of nums) {\n'
                    '  heap.push(x);\n}\n'
                    'const out: number[] = [];\n'
                    'while (heap.size > 0) {\n'
                    '  out.push(heap.pop() ?? 0);\n}\n'
                    'console.log(out.join(" "));\n',
                    '        if (left < this.items.length && this.less(left, best)) {\n'
                    '          best = left;\n        }\n'
                    '        if (right < this.items.length && this.less(right, best)) {\n'
                    '          best = right;\n        }',
                    [("5 1 4 2 3", "1 2 3 4 5"), ("9 9 1", "1 9 9"), ("7", "7")],
                    hints=["Start with best = i, then let each existing child that is smaller take its place.",
                           "Check the index is in range before comparing."],
                    difficulty="Hard"),
                _ex("tscourse-w28-cl-3", "Largest first",
                    "Make a max-heap by changing only the comparator.",
                    _NUMS + _HEAP +
                    'const heap = new MinHeap<number>((a, b) => b - a);\n'
                    'for (const x of nums) {\n'
                    '  heap.push(x);\n}\n'
                    'console.log(`${heap.pop() ?? 0} ${heap.pop() ?? 0}`);\n',
                    'const heap = new MinHeap<number>((a, b) => b - a);',
                    [("3 9 4 7", "9 7"), ("1 1 2", "2 1")],
                    hints=["'Before' means 'comes out first'. Larger values should come out first.",
                           "Write const heap = new MinHeap<number>((a, b) => b - a);"],
                    difficulty="Easy"),
                _ex("tscourse-w28-cl-4", "Records, with a tie-break",
                    "Order jobs by priority, and by name when priorities are equal, so the order is fully determined.",
                    _WORDS + _HEAP +
                    'interface Job {\n'
                    '  readonly name: string;\n'
                    '  readonly pri: number;\n}\n'
                    'const heap = new MinHeap<Job>((a, b) => a.pri - b.pri || a.name.localeCompare(b.name));\n'
                    'for (const w of words) {\n'
                    '  const [name, pri] = w.split(":");\n'
                    '  heap.push({ name: name ?? "", pri: Number(pri ?? "0") });\n}\n'
                    'const out: string[] = [];\n'
                    'while (heap.size > 0) {\n'
                    '  out.push(heap.pop()?.name ?? "");\n}\n'
                    'console.log(out.join(" "));\n',
                    'const heap = new MinHeap<Job>((a, b) => a.pri - b.pri || a.name.localeCompare(b.name));',
                    [("deploy:2 alert:1 backup:2 audit:1", "alert audit backup deploy"), ("x:5", "x")],
                    hints=["Priority first; when that is 0, fall through with || to the name — week 19's idiom.",
                           "A heap is not stable, so without the tie-break equal priorities could come out either way."],
                    difficulty="Medium"),
                _ex("tscourse-w28-cl-5", "Count the work",
                    "Push n items in ascending and in descending order, and count the comparisons each costs.",
                    _HEAP +
                    'const n = 15;\n'
                    'const up = new MinHeap<number>((a, b) => a - b);\n'
                    'for (let i = 1; i <= n; i = i + 1) {\n'
                    '  up.push(i);\n}\n'
                    'const down = new MinHeap<number>((a, b) => a - b);\n'
                    'for (let i = n; i >= 1; i = i - 1) {\n'
                    '  down.push(i);\n}\n'
                    'console.log(`ascending=${up.compares} descending=${down.compares}`);\n',
                    'for (let i = n; i >= 1; i = i - 1) {\n'
                    '  down.push(i);\n}',
                    [("", "ascending=14 descending=34")],
                    hints=["Each descending item is the new smallest, so it sifts all the way to the root.",
                           "Push n, n - 1, … 1 into the second heap."],
                    difficulty="Easy"),
                _diagnose("tscourse-w28-cl-d1", "The wrong kind of item",
                          "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.",
                          _LINE + _HEAP +
                          'const heap = new MinHeap<number>((a, b) => a - b);\n'
                          'for (const part of line.split(" ")) {\n'
                          '  heap.push(part);\n}\n'
                          'console.log(heap.peek() ?? 0);\n',
                          _LINE + _HEAP +
                          'const heap = new MinHeap<number>((a, b) => a - b);\n'
                          'for (const part of line.split(" ")) {\n'
                          '  heap.push(Number(part));\n}\n'
                          'console.log(heap.peek() ?? 0);\n',
                          [("5 2 9", "2")],
                          hints=["The heap was created for numbers. What is `part`?",
                                 "Convert at the boundary, before it enters the heap.",
                                 "heap.push(Number(part));"],
                          difficulty="Easy"),
                _fix("tscourse-w28-cl-fix1", "Fix the sift-down that chose the larger child",
                     "Popping `5 1 4 2 3` should give `1 2 3 4 5`. This gives `1 3 4 2 5`: when the moved item sinks, it swaps with the LARGER child, which puts a larger value above a smaller sibling and breaks the heap one level down.",
                     _NUMS +
                     _heap_with('        if (left < this.items.length && this.less(left, best)) {\n'
                                '          best = left;\n        }\n'
                                '        if (right < this.items.length && this.less(right, best)) {\n'
                                '          best = right;\n        }',
                                '        if (left < this.items.length) {\n'
                                '          best = left;\n        }\n'
                                '        if (right < this.items.length && this.less(left, right)) {\n'
                                '          best = right;\n        }\n'
                                '        if (best !== i && !this.less(best, i)) {\n'
                                '          best = i;\n        }') +
                     'const heap = new MinHeap<number>((a, b) => a - b);\n'
                     'for (const x of nums) {\n'
                     '  heap.push(x);\n}\n'
                     'const out: number[] = [];\n'
                     'while (heap.size > 0) {\n'
                     '  out.push(heap.pop() ?? 0);\n}\n'
                     'console.log(out.join(" "));\n',
                     _NUMS + _HEAP +
                     'const heap = new MinHeap<number>((a, b) => a - b);\n'
                     'for (const x of nums) {\n'
                     '  heap.push(x);\n}\n'
                     'const out: number[] = [];\n'
                     'while (heap.size > 0) {\n'
                     '  out.push(heap.pop() ?? 0);\n}\n'
                     'console.log(out.join(" "));\n',
                     [("5 1 4 2 3", "1 2 3 4 5"), ("8 6 7 5 3 0 9", "0 3 5 6 7 8 9")],
                     hints=["Which child should rise to take the sinking item's place?",
                            "The one that is smaller — otherwise it ends up above a smaller sibling.",
                            "Start from best = i and replace it with a child only when that child is LESS than best."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("`less(i, j)` returns false when a slot is missing, so…",
                   ["it crashes", "the class needs no `!` anywhere", "it is slower", "pop fails"], 1,
                   "Typed without assertions."),
                _q("Pushing already-ascending items costs about one comparison each because…",
                   ["luck", "each new item is at least its parent, so it never moves", "of the comparator",
                    "the heap is sorted"], 1,
                   "14 for 15 items."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w28-uses", "What heaps are for",
            "Top-k, merging sorted streams, and Dijkstra at full speed.",
            """
## The k largest, in O(n log k)

Keep a **min**-heap of size k. Push every item; whenever the heap grows past k, pop
the smallest. What survives is the k largest, and the root is the k-th largest:

```ts
for (const x of xs) {
  heap.push(x);
  if (heap.size > k) { heap.pop(); }
}
```

Counter-intuitive the first time — a *min*-heap to keep the *largest* — but the root
is exactly the item that should be evicted next. The heap never holds more than k
items, so each operation is O(log k): for the ten largest of a million, that is about
3 comparisons per item instead of 20.

## Merging k sorted lists

Week 22 merged **two** sorted arrays. For k of them, put the **front** of each list
in a heap; pop the smallest, output it, and push the next item from the same list.
The heap never holds more than k items: O(N log k) for N items in total.

## Dijkstra, properly

Week 27's step 1 — find the unsettled node with the smallest distance — becomes a
`pop`. When a relaxation improves `dist[v]`, **push** `[newDistance, v]`. That leaves
the older, larger entry for v still in the heap; when it is eventually popped, its
distance is larger than `dist[v]`, so it is **stale** and skipped:

```ts
const top = heap.pop();
if (top.d > (dist[top.node] ?? Infinity)) { continue; }     // outdated
```

This is **lazy deletion**: cheaper than finding and removing the old entry, and it
costs at most one extra pop per edge. O((V + E) log V) instead of O(V²).

> ⚠️ **Common mistakes:** a max-heap for top-k largest (it evicts the wrong end);
> forgetting to push the next item from the same list; and not skipping stale
> Dijkstra entries.
""",
            warmup=[
                _q("The k largest items are kept with…",
                   ["a max-heap of size n", "a min-heap of size k", "a sorted array", "a Set"], 1,
                   "Its root is the next to evict."),
                _q("After the stream, the top-k heap's root is…",
                   ["the largest", "the k-th largest", "the smallest overall", "the median"], 1,
                   "The smallest of the k largest."),
                _q("Merging k sorted lists keeps in the heap…",
                   ["everything", "one item per list — its current front", "k² items", "the largest"], 1,
                   "At most k at a time."),
                _q("A stale Dijkstra entry is one whose distance is…",
                   ["smaller than dist[node]", "larger than dist[node] — a better one was found", "equal", "infinite"], 1,
                   "Skip it."),
            ],
            exercises=[
                _ex("tscourse-w28-us-1", "Keep only k",
                    "Evict the smallest whenever the heap holds more than k.",
                    _NUMS + _HEAP +
                    'const k = 3;\n'
                    'const heap = new MinHeap<number>((a, b) => a - b);\n'
                    'for (const x of nums) {\n'
                    '  heap.push(x);\n'
                    '  if (heap.size > k) {\n'
                    '    heap.pop();\n  }\n}\n'
                    'const top = [...heap.toArray()].sort((a, b) => b - a);\n'
                    'console.log(`${top.join(" ")} | kth=${heap.peek() ?? 0}`);\n',
                    '  if (heap.size > k) {\n'
                    '    heap.pop();\n  }',
                    [("3 1 5 12 2 11", "12 11 5 | kth=5"), ("4 4 4 4", "4 4 4 | kth=4")],
                    hints=["The heap may grow to k + 1 for a moment; the smallest of those is not in the top k.",
                           "if (heap.size > k) { heap.pop(); }"],
                    difficulty="Medium"),
                _ex("tscourse-w28-us-2", "Merge k sorted lists",
                    "After taking a list's front item, push that list's next item.",
                    _FS + _HEAP +
                    'const lists: readonly (readonly number[])[] = fs.readFileSync(0, "utf8")\n'
                    '  .trim()\n'
                    '  .split("\\n")\n'
                    '  .map((l) => l.trim().split(/\\s+/).filter((s) => s !== "").map(Number));\n'
                    'interface Front {\n'
                    '  readonly value: number;\n'
                    '  readonly list: number;\n'
                    '  readonly pos: number;\n}\n'
                    'const heap = new MinHeap<Front>((a, b) => a.value - b.value || a.list - b.list);\n'
                    'lists.forEach((xs, list) => {\n'
                    '  const first = xs[0];\n'
                    '  if (first !== undefined) {\n'
                    '    heap.push({ value: first, list, pos: 0 });\n  }\n});\n'
                    'const out: number[] = [];\n'
                    'while (heap.size > 0) {\n'
                    '  const f = heap.pop();\n'
                    '  if (f === undefined) {\n'
                    '    break;\n  }\n'
                    '  out.push(f.value);\n'
                    '  const next = lists[f.list]?.[f.pos + 1];\n'
                    '  if (next !== undefined) {\n'
                    '    heap.push({ value: next, list: f.list, pos: f.pos + 1 });\n  }\n}\n'
                    'console.log(out.join(" "));\n',
                    '  const next = lists[f.list]?.[f.pos + 1];\n'
                    '  if (next !== undefined) {\n'
                    '    heap.push({ value: next, list: f.list, pos: f.pos + 1 });\n  }',
                    [("1 4 7\n2 5 8\n3 6 9", "1 2 3 4 5 6 7 8 9"), ("1 3\n2", "1 2 3")],
                    hints=["The list the popped item came from now has a new front — if it has anything left.",
                           "Look up position pos + 1 in that list, and push it when it exists."],
                    difficulty="Hard"),
                _ex("tscourse-w28-us-3", "Dijkstra with a heap",
                    "Skip a popped entry whose distance is larger than the best already known.",
                    _FS + _HEAP +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const n = Number(lines[0] ?? "0");\n'
                    'const adj: (readonly [number, number])[][] = Array.from({ length: n }, (): (readonly [number, number])[] => []);\n'
                    'for (const l of lines.slice(1)) {\n'
                    '  const [u, v, w] = l.trim().split(/\\s+/).map(Number);\n'
                    '  if (u === undefined || v === undefined || w === undefined) {\n'
                    '    continue;\n  }\n'
                    '  adj[u]?.push([v, w]);\n'
                    '  adj[v]?.push([u, w]);\n}\n'
                    'const dist = new Array<number>(n).fill(Infinity);\n'
                    'dist[0] = 0;\n'
                    'const heap = new MinHeap<readonly [number, number]>((a, b) => a[0] - b[0] || a[1] - b[1]);\n'
                    'heap.push([0, 0]);\n'
                    'let settled = 0;\n'
                    'while (heap.size > 0) {\n'
                    '  const top = heap.pop();\n'
                    '  if (top === undefined) {\n'
                    '    break;\n  }\n'
                    '  const [d, u] = top;\n'
                    '  if (d > (dist[u] ?? Infinity)) {\n'
                    '    continue;\n  }\n'
                    '  settled = settled + 1;\n'
                    '  for (const [v, w] of adj[u] ?? []) {\n'
                    '    if (d + w < (dist[v] ?? Infinity)) {\n'
                    '      dist[v] = d + w;\n'
                    '      heap.push([d + w, v]);\n    }\n  }\n}\n'
                    'console.log(`${dist.map((x) => (x === Infinity ? "-" : String(x))).join(" ")} settled=${settled}`);\n',
                    '  if (d > (dist[u] ?? Infinity)) {\n'
                    '    continue;\n  }',
                    [("4\n0 1 4\n0 2 1\n2 1 1\n1 3 1", "0 2 1 3 settled=4"), ("3\n0 1 5", "0 5 - settled=2")],
                    hints=["A later, cheaper route to u was already found and pushed; this entry is outdated.",
                           "if (d > (dist[u] ?? Infinity)) { continue; }"],
                    difficulty="Hard"),
                _fix("tscourse-w28-us-fix1", "Fix the top-k that kept the smallest",
                     "The three largest of `3 1 5 12 2 11` are 12, 11 and 5. This reports 3, 2 and 1: it uses a MAX-heap, so the item it evicts at every step is the largest — the opposite of what it should throw away.",
                     _NUMS + _HEAP +
                     'const k = 3;\n'
                     'const heap = new MinHeap<number>((a, b) => b - a);\n'
                     'for (const x of nums) {\n'
                     '  heap.push(x);\n'
                     '  if (heap.size > k) {\n'
                     '    heap.pop();\n  }\n}\n'
                     'console.log([...heap.toArray()].sort((a, b) => b - a).join(" "));\n',
                     _NUMS + _HEAP +
                     'const k = 3;\n'
                     'const heap = new MinHeap<number>((a, b) => a - b);\n'
                     'for (const x of nums) {\n'
                     '  heap.push(x);\n'
                     '  if (heap.size > k) {\n'
                     '    heap.pop();\n  }\n}\n'
                     'console.log([...heap.toArray()].sort((a, b) => b - a).join(" "));\n',
                     [("3 1 5 12 2 11", "12 11 5"), ("9 8 7 6", "9 8 7")],
                     hints=["Which item should leave when the heap holds k + 1?",
                            "The smallest of them — so the smallest must be at the root.",
                            "Use a min-heap: (a, b) => a - b."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is lazy deletion cheaper than removing the old entry?",
                   ["it is not", "finding an arbitrary entry in a heap is O(n); skipping it later is O(1)",
                    "it uses less memory", "the heap is sorted"], 1,
                   "A heap only knows its root."),
                _q("Heap-based Dijkstra costs…",
                   ["O(V²)", "O((V + E) log V)", "O(E)", "O(V log E²)"], 1,
                   "A pop or push per edge, each log V."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w28-merge", "Intervals: sort, then sweep",
            "Merging overlapping ranges — and the interval hiding inside another.",
            """
An **interval** is a start and an end. This week they are **half-open**,
`[start, end)`: a meeting from 1 to 2 and one from 2 to 3 do not clash, because the
first has ended when the second starts. State the convention every time; it is the
source of most interval bugs.

## Merging overlaps

"Combine every set of overlapping meetings into one busy block."

1. **Sort by start.** Now any interval that overlaps the current block must come
   next — nothing later can start earlier.
2. **Sweep.** If the next interval starts before the current block ends, extend the
   block; otherwise the block is finished, and the next interval starts a new one.

```ts
xs.sort((a, b) => a.start - b.start);
for (const x of xs) {
  const last = out[out.length - 1];
  if (last !== undefined && x.start <= last.end) {
    last.end = Math.max(last.end, x.end);          // extend
  } else {
    out.push({ ...x });                             // a new block
  }
}
```

`1-3 2-6 8-10 15-18` → `1-6 8-10 15-18`.

## The two details

* **`Math.max`, not `x.end`.** `1-10` followed by `2-3` must stay `1-10`. Taking the
  newcomer's end would shrink the block to `1-3` — an interval *inside* another is
  the case every quick implementation gets wrong.
* **`<=` or `<`?** With `<=`, touching blocks (`1-2`, `2-3`) merge into `1-3`, which is
  right for "busy time". With `<`, they stay separate, which is right for "do these
  meetings clash". Same code, one character, and the question decides.

## A second sweep: intersections

Two sorted lists of free times; when is everyone free? Week 22's two pointers: the
overlap of the current pair is `[max(starts), min(ends))`, and whichever interval ends
first is finished, so advance its pointer.

> ⚠️ **Common mistakes:** merging unsorted input; `x.end` instead of `Math.max`;
> and not deciding what touching means.
""",
            warmup=[
                _q("Merging intervals starts by…",
                   ["sorting by end", "sorting by start", "a heap", "nothing"], 1,
                   "Then one pass."),
                _q("`1-10` then `2-3` should merge to…",
                   ["1-3", "1-10", "2-10", "1-13"], 1,
                   "Math.max of the ends."),
                _q("With `x.start <= last.end`, the blocks `1-2` and `2-3`…",
                   ["stay separate", "merge into 1-3", "vanish", "error"], 1,
                   "`<` would keep them apart."),
                _q("The intersection of [1, 5) and [3, 8) is…",
                   ["[1, 8)", "[3, 5)", "empty", "[1, 3)"], 1,
                   "max of starts, min of ends."),
            ],
            exercises=[
                _ex("tscourse-w28-mg-1", "Extend or start a new block",
                    "After sorting by start, extend the last block when the next interval overlaps it.",
                    _WORDS + _IVALS +
                    'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                    'const out: { start: number; end: number }[] = [];\n'
                    'for (const x of sorted) {\n'
                    '  const last = out[out.length - 1];\n'
                    '  if (last !== undefined && x.start <= last.end) {\n'
                    '    last.end = Math.max(last.end, x.end);\n'
                    '  } else {\n'
                    '    out.push({ ...x });\n  }\n}\n'
                    'console.log(show(out));\n',
                    '  if (last !== undefined && x.start <= last.end) {\n'
                    '    last.end = Math.max(last.end, x.end);\n'
                    '  } else {\n'
                    '    out.push({ ...x });\n  }',
                    [("1-3 2-6 8-10 15-18", "1-6 8-10 15-18"), ("1-4 4-5", "1-5"), ("5-6 1-2", "1-2 5-6")],
                    hints=["An interval starting at or before the block's end belongs to that block.",
                           "Extend with Math.max; otherwise push a copy as a new block."],
                    difficulty="Medium"),
                _ex("tscourse-w28-mg-2", "How much time is covered",
                    "Merge, then add up the lengths of the merged blocks.",
                    _WORDS + _IVALS +
                    'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                    'const out: { start: number; end: number }[] = [];\n'
                    'for (const x of sorted) {\n'
                    '  const last = out[out.length - 1];\n'
                    '  if (last !== undefined && x.start <= last.end) {\n'
                    '    last.end = Math.max(last.end, x.end);\n'
                    '  } else {\n'
                    '    out.push({ ...x });\n  }\n}\n'
                    'const covered = out.reduce((sum, x) => sum + (x.end - x.start), 0);\n'
                    'console.log(covered);\n',
                    'const covered = out.reduce((sum, x) => sum + (x.end - x.start), 0);',
                    [("1-3 2-6 8-10", "7"), ("0-10 2-3", "10")],
                    hints=["After merging, no two blocks overlap, so their lengths simply add.",
                           "Write const covered = out.reduce((sum, x) => sum + (x.end - x.start), 0);"],
                    difficulty="Easy"),
                _ex("tscourse-w28-mg-3", "When are both free?",
                    "Intersect two sorted lists of intervals with two pointers.",
                    _FS +
                    'interface Iv {\n'
                    '  readonly start: number;\n'
                    '  readonly end: number;\n}\n'
                    'function parse(l: string): readonly Iv[] {\n'
                    '  return l.trim().split(/\\s+/).filter((w) => w !== "").map((w) => {\n'
                    '    const [s, e] = w.split("-").map(Number);\n'
                    '    return { start: s ?? 0, end: e ?? 0 };\n  });\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").split("\\n");\n'
                    'const a = parse(lines[0] ?? "");\n'
                    'const b = parse(lines[1] ?? "");\n'
                    'const out: string[] = [];\n'
                    'let i = 0;\n'
                    'let j = 0;\n'
                    'while (i < a.length && j < b.length) {\n'
                    '  const x = a[i];\n'
                    '  const y = b[j];\n'
                    '  if (x === undefined || y === undefined) {\n'
                    '    break;\n  }\n'
                    '  const lo = Math.max(x.start, y.start);\n'
                    '  const hi = Math.min(x.end, y.end);\n'
                    '  if (lo < hi) {\n'
                    '    out.push(`${lo}-${hi}`);\n  }\n'
                    '  if (x.end < y.end) {\n'
                    '    i = i + 1;\n'
                    '  } else {\n'
                    '    j = j + 1;\n  }\n}\n'
                    'console.log(out.length === 0 ? "never" : out.join(" "));\n',
                    '  if (x.end < y.end) {\n'
                    '    i = i + 1;\n'
                    '  } else {\n'
                    '    j = j + 1;\n  }',
                    [("0-2 5-10 13-23\n1-5 8-12 15-24", "1-2 8-10 15-23"), ("1-2\n3-4", "never")],
                    hints=["Whichever interval ends first cannot overlap anything later in the other list.",
                           "Advance the pointer of the interval that ends first."],
                    difficulty="Hard"),
                _fix("tscourse-w28-mg-fix1", "Fix the block that shrank",
                     "`1-10 2-3 4-12` is one busy block, `1-12`. This reports `1-3 4-12`: when `2-3` is merged into `1-10`, the block's end is set to 3 — the newcomer's end — though `1-10` still runs to 10.",
                     _WORDS + _IVALS +
                     'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                     'const out: { start: number; end: number }[] = [];\n'
                     'for (const x of sorted) {\n'
                     '  const last = out[out.length - 1];\n'
                     '  if (last !== undefined && x.start <= last.end) {\n'
                     '    last.end = x.end;\n'
                     '  } else {\n'
                     '    out.push({ ...x });\n  }\n}\n'
                     'console.log(show(out));\n',
                     _WORDS + _IVALS +
                     'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                     'const out: { start: number; end: number }[] = [];\n'
                     'for (const x of sorted) {\n'
                     '  const last = out[out.length - 1];\n'
                     '  if (last !== undefined && x.start <= last.end) {\n'
                     '    last.end = Math.max(last.end, x.end);\n'
                     '  } else {\n'
                     '    out.push({ ...x });\n  }\n}\n'
                     'console.log(show(out));\n',
                     [("1-10 2-3 4-12", "1-12"), ("1-5 2-3", "1-5")],
                     hints=["What if the new interval lies entirely inside the block?",
                            "The block ends at whichever end is later.",
                            "last.end = Math.max(last.end, x.end);"],
                     difficulty="Medium"),
                _fix("tscourse-w28-mg-fix2", "Fix the merge that skipped the sort",
                     "`8-10 1-3 2-6` is two blocks, `1-6 8-10`. This prints only `8-10`: `1-3` and `2-6` both start before that block ends, so each is swallowed into it. The sweep assumes nothing later can start earlier, which is only true once the intervals are sorted by start.",
                     _WORDS + _IVALS +
                     'const out: { start: number; end: number }[] = [];\n'
                     'for (const x of ivs) {\n'
                     '  const last = out[out.length - 1];\n'
                     '  if (last !== undefined && x.start <= last.end) {\n'
                     '    last.end = Math.max(last.end, x.end);\n'
                     '  } else {\n'
                     '    out.push({ ...x });\n  }\n}\n'
                     'console.log(show(out));\n',
                     _WORDS + _IVALS +
                     'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                     'const out: { start: number; end: number }[] = [];\n'
                     'for (const x of sorted) {\n'
                     '  const last = out[out.length - 1];\n'
                     '  if (last !== undefined && x.start <= last.end) {\n'
                     '    last.end = Math.max(last.end, x.end);\n'
                     '  } else {\n'
                     '    out.push({ ...x });\n  }\n}\n'
                     'console.log(show(out));\n',
                     [("8-10 1-3 2-6", "1-6 8-10"), ("5-7 1-6", "1-7")],
                     hints=["The sweep only compares with the LAST block. When is that enough?",
                            "Only when every later interval starts no earlier than this one.",
                            "Sort a copy by start before sweeping."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why does sorting by start make one comparison with the last block enough?",
                   ["it does not", "no later interval can start earlier, so only the latest block can overlap it",
                    "blocks are small", "of Math.max"], 1,
                   "The whole correctness argument."),
                _q("For 'do any two meetings clash?', touching intervals should…",
                   ["clash", "not clash — use `<`", "merge", "be removed"], 1,
                   "Half-open intervals."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w28-rooms", "How many rooms",
            "A heap of end times, or a sweep line — and the tie that decides the answer.",
            """
"Given every meeting, how many rooms does the day need?" — the most meetings in
progress at any one moment.

## With a heap of end times

Sort meetings by start. Keep a **min-heap of the end times** of meetings currently
holding a room. For each meeting: if the earliest-ending meeting has finished by the
time this one starts, its room is free — pop it. Then push this meeting's end.

```ts
for (const m of sorted) {
  if (ends.size > 0 && (ends.peek() ?? 0) <= m.start) { ends.pop(); }
  ends.push(m.end);
  rooms = Math.max(rooms, ends.size);
}
```

`0-30 5-10 15-20` needs **2** rooms. The heap's root is always "the next room to
free up", which is exactly what a heap is for.

## With a sweep line

Turn every meeting into two **events**: `+1` at its start, `-1` at its end. Sort the
events by time and walk through them, keeping a running count; the peak is the
answer. No heap at all — just week 24's sort and a counter.

## The tie

What if one meeting ends at 2 and another starts at 2? With half-open intervals they
do not clash, so the `-1` must be processed **before** the `+1`:

```ts
events.sort((a, b) => a.t - b.t || a.delta - b.delta);   // -1 sorts before +1
```

Process the start first and the count briefly reaches 2 — one room too many,
reported with total confidence. It is the classic sweep-line bug, and a single
tie-break in the comparator is the whole fix.

> ⚠️ **Common mistakes:** ends after starts at equal times; forgetting to sort by
> start before the heap version; and `<` instead of `<=` when freeing a room.
""",
            warmup=[
                _q("The rooms heap holds…",
                   ["start times", "end times of meetings currently holding a room", "durations", "rooms"], 1,
                   "Its root frees next."),
                _q("A room can be reused when…",
                   ["always", "the earliest end is ≤ the new meeting's start", "a meeting starts", "never"], 1,
                   "Half-open intervals."),
                _q("A sweep line turns each meeting into…",
                   ["one event", "a +1 at its start and a -1 at its end", "a heap entry", "a pair of rooms"], 1,
                   "Then sort and count."),
                _q("At equal times the sweep must process…",
                   ["starts first", "ends first", "either", "neither"], 1,
                   "A room frees before it is taken again."),
            ],
            exercises=[
                _ex("tscourse-w28-rm-1", "Free a room, take a room",
                    "Pop the earliest end if that meeting has finished, then push this meeting's end.",
                    _WORDS + _IVALS + _HEAP +
                    'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                    'const ends = new MinHeap<number>((a, b) => a - b);\n'
                    'let rooms = 0;\n'
                    'for (const m of sorted) {\n'
                    '  if (ends.size > 0 && (ends.peek() ?? 0) <= m.start) {\n'
                    '    ends.pop();\n  }\n'
                    '  ends.push(m.end);\n'
                    '  rooms = Math.max(rooms, ends.size);\n}\n'
                    'console.log(rooms);\n',
                    '  if (ends.size > 0 && (ends.peek() ?? 0) <= m.start) {\n'
                    '    ends.pop();\n  }',
                    [("0-30 5-10 15-20", "2"), ("7-10 2-4", "1"), ("1-5 2-6 3-7", "3"), ("1-2 2-3", "1")],
                    hints=["The heap's root is the meeting that frees its room soonest.",
                           "If it has ended by m.start, that room is free: pop it."],
                    difficulty="Medium"),
                _ex("tscourse-w28-rm-2", "Events, ends first",
                    "Sort the +1/-1 events by time, with ends before starts when times are equal.",
                    _WORDS + _IVALS +
                    'const events: { t: number; delta: number }[] = [];\n'
                    'for (const m of ivs) {\n'
                    '  events.push({ t: m.start, delta: 1 });\n'
                    '  events.push({ t: m.end, delta: -1 });\n}\n'
                    'events.sort((a, b) => a.t - b.t || a.delta - b.delta);\n'
                    'let now = 0;\n'
                    'let peak = 0;\n'
                    'for (const e of events) {\n'
                    '  now = now + e.delta;\n'
                    '  peak = Math.max(peak, now);\n}\n'
                    'console.log(peak);\n',
                    'events.sort((a, b) => a.t - b.t || a.delta - b.delta);',
                    [("0-30 5-10 15-20", "2"), ("1-2 2-3 3-4", "1"), ("1-5 2-6 3-7", "3")],
                    hints=["Time first; on a tie, -1 sorts before +1 because it is smaller.",
                           "Write events.sort((a, b) => a.t - b.t || a.delta - b.delta);"],
                    difficulty="Medium"),
                _ex("tscourse-w28-rm-3", "The busiest moment",
                    "Report when the peak is first reached, as well as how high it is.",
                    _WORDS + _IVALS +
                    'const events: { t: number; delta: number }[] = [];\n'
                    'for (const m of ivs) {\n'
                    '  events.push({ t: m.start, delta: 1 });\n'
                    '  events.push({ t: m.end, delta: -1 });\n}\n'
                    'events.sort((a, b) => a.t - b.t || a.delta - b.delta);\n'
                    'let now = 0;\n'
                    'let peak = 0;\n'
                    'let when = 0;\n'
                    'for (const e of events) {\n'
                    '  now = now + e.delta;\n'
                    '  if (now > peak) {\n'
                    '    peak = now;\n'
                    '    when = e.t;\n  }\n}\n'
                    'console.log(`${peak} at ${when}`);\n',
                    '  if (now > peak) {\n'
                    '    peak = now;\n'
                    '    when = e.t;\n  }',
                    [("1-5 2-6 3-7", "3 at 3"), ("0-30 5-10 15-20", "2 at 5")],
                    hints=["A strictly higher count is a new peak; remember its time.",
                           "`>` rather than `>=` keeps the FIRST moment the peak is reached."],
                    difficulty="Easy"),
                _fix("tscourse-w28-rm-fix1", "Fix the room that was needed twice",
                     "`1-2 2-3 3-4` runs back to back and needs one room. This says 2: the events are sorted by time alone, and at time 2 the start happens to be processed before the end — so for an instant both meetings seem to be running.",
                     _WORDS + _IVALS +
                     'const events: { t: number; delta: number }[] = [];\n'
                     'for (const m of ivs) {\n'
                     '  events.push({ t: m.start, delta: 1 });\n'
                     '  events.push({ t: m.end, delta: -1 });\n}\n'
                     'events.sort((a, b) => a.t - b.t || b.delta - a.delta);\n'
                     'let now = 0;\n'
                     'let peak = 0;\n'
                     'for (const e of events) {\n'
                     '  now = now + e.delta;\n'
                     '  peak = Math.max(peak, now);\n}\n'
                     'console.log(peak);\n',
                     _WORDS + _IVALS +
                     'const events: { t: number; delta: number }[] = [];\n'
                     'for (const m of ivs) {\n'
                     '  events.push({ t: m.start, delta: 1 });\n'
                     '  events.push({ t: m.end, delta: -1 });\n}\n'
                     'events.sort((a, b) => a.t - b.t || a.delta - b.delta);\n'
                     'let now = 0;\n'
                     'let peak = 0;\n'
                     'for (const e of events) {\n'
                     '  now = now + e.delta;\n'
                     '  peak = Math.max(peak, now);\n}\n'
                     'console.log(peak);\n',
                     [("1-2 2-3 3-4", "1"), ("0-30 5-10 15-20", "2")],
                     hints=["At time 2, one meeting ends and one starts. Which should the count see first?",
                            "Half-open: the first has ended before the second starts.",
                            "Tie-break so -1 comes first: a.delta - b.delta."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The heap and sweep versions of 'rooms' both cost…",
                   ["O(n)", "O(n log n) — the sort dominates", "O(n²)", "O(log n)"], 1,
                   "Sorting, then linear-ish work."),
                _q("Why does `ends.peek() <= m.start` use `<=`?",
                   ["style", "a meeting ending as another starts frees its room — half-open", "speed", "types"], 1,
                   "The same convention as the tie-break."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w28-greedy", "The greedy that is provably right",
            "The most non-overlapping meetings: sort by END.",
            """
Week 26 showed greedy coin change failing. Here is a greedy that **never** fails —
and the reason is worth knowing, because "is this greedy safe?" is an interview
question in its own right.

## Interval scheduling

"One person, many meetings. What is the most they can attend?"

**Sort by end time. Take a meeting whenever it starts at or after the last one you
took ended.**

```ts
xs.sort((a, b) => a.end - b.end);
let lastEnd = -Infinity;
for (const x of xs) {
  if (x.start >= lastEnd) { count = count + 1; lastEnd = x.end; }
}
```

`1-2 2-3 3-4 1-3` → **3** (1-2, 2-3, 3-4).

## Why earliest END

Whatever the best schedule is, swap its first meeting for the one that **ends
earliest** overall. That cannot clash with anything the best schedule does next —
it ends no later than the meeting it replaced — so the schedule is still valid and
no shorter. Repeat the argument for each subsequent choice. The greedy choice is
always part of *some* optimal answer, which is exactly what makes a greedy safe.
(This is called an **exchange argument**.)

## Why not earliest start, or shortest

* **Earliest start** takes `1-10` first on `1-10 2-3 4-5`, and attends one meeting
  where two were possible.
* **Shortest** takes `4-6` first on `1-5 4-6 5-10` — and it clashes with both others.

Each failure is a one-line counter-example, which is the fastest way to reject a
greedy rule — and a correct greedy survives every one you can find.

## The flip side

"The fewest meetings to cancel so the rest do not overlap" is the same problem:
`n − (the most you can keep)`.

> ⚠️ **Common mistakes:** sorting by start; forgetting that a meeting starting
> exactly when the last ended is fine (`>=`); and trusting a greedy rule without a
> counter-example hunt.
""",
            warmup=[
                _q("The most non-overlapping meetings: sort by…",
                   ["start", "end", "length", "nothing"], 1,
                   "Earliest finish leaves the most room."),
                _q("Sorting by start fails on…",
                   ["nothing", "one long meeting that starts first and blocks several short ones", "ties",
                    "empty input"], 1,
                   "1-10 2-3 4-5."),
                _q("An exchange argument shows…",
                   ["a bug", "the greedy choice is part of some optimal answer", "the running time", "stability"], 1,
                   "Swap it into the best schedule; nothing breaks."),
                _q("The fewest meetings to cancel is…",
                   ["the most you can keep", "n minus the most you can keep", "n", "0"], 1,
                   "The same problem, flipped."),
            ],
            exercises=[
                _ex("tscourse-w28-gr-1", "Earliest end first",
                    "Sort meetings by end time before choosing greedily.",
                    _WORDS + _IVALS +
                    'const sorted = [...ivs].sort((a, b) => a.end - b.end);\n'
                    'let lastEnd = -Infinity;\n'
                    'const taken: Iv[] = [];\n'
                    'for (const x of sorted) {\n'
                    '  if (x.start >= lastEnd) {\n'
                    '    taken.push(x);\n'
                    '    lastEnd = x.end;\n  }\n}\n'
                    'console.log(`${taken.length}: ${show(taken)}`);\n',
                    'const sorted = [...ivs].sort((a, b) => a.end - b.end);',
                    [("1-2 2-3 3-4 1-3", "3: 1-2 2-3 3-4"), ("1-10 2-3 4-5", "2: 2-3 4-5")],
                    hints=["The meeting that ends first leaves the most time for the rest.",
                           "Write const sorted = [...ivs].sort((a, b) => a.end - b.end);"],
                    difficulty="Medium"),
                _ex("tscourse-w28-gr-2", "Fewest to cancel",
                    "Report how many meetings must go so that none of the rest overlap.",
                    _WORDS + _IVALS +
                    'const sorted = [...ivs].sort((a, b) => a.end - b.end);\n'
                    'let lastEnd = -Infinity;\n'
                    'let kept = 0;\n'
                    'for (const x of sorted) {\n'
                    '  if (x.start >= lastEnd) {\n'
                    '    kept = kept + 1;\n'
                    '    lastEnd = x.end;\n  }\n}\n'
                    'console.log(ivs.length - kept);\n',
                    'console.log(ivs.length - kept);',
                    [("1-2 2-3 3-4 1-3", "1"), ("1-2 1-2 1-2", "2"), ("1-2 2-3", "0")],
                    hints=["Cancel everything the greedy did not keep.",
                           "Write console.log(ivs.length - kept);"],
                    difficulty="Easy"),
                _ex("tscourse-w28-gr-3", "Counter-examples",
                    "Run three greedy rules on the same inputs and report how many meetings each attends.",
                    _WORDS + _IVALS +
                    'function attend(order: readonly Iv[]): number {\n'
                    '  const taken: Iv[] = [];\n'
                    '  for (const x of order) {\n'
                    '    if (taken.every((t) => x.start >= t.end || x.end <= t.start)) {\n'
                    '      taken.push(x);\n    }\n  }\n'
                    '  return taken.length;\n}\n'
                    'const byStart = attend([...ivs].sort((a, b) => a.start - b.start));\n'
                    'const byLength = attend([...ivs].sort((a, b) => a.end - a.start - (b.end - b.start)));\n'
                    'const byEnd = attend([...ivs].sort((a, b) => a.end - b.end));\n'
                    'console.log(`start=${byStart} shortest=${byLength} end=${byEnd}`);\n',
                    'const byEnd = attend([...ivs].sort((a, b) => a.end - b.end));',
                    [("1-10 2-3 4-5", "start=1 shortest=2 end=2"), ("1-5 4-6 5-10", "start=2 shortest=1 end=2")],
                    hints=["The third rule is the one that is always right.",
                           "Write const byEnd = attend([...ivs].sort((a, b) => a.end - b.end));"],
                    difficulty="Medium"),
                _ex("tscourse-w28-gr-4", "Which tool",
                    "Map each interval question to its technique.",
                    _NUMS +
                    'function technique(kind: number): string {\n'
                    '  if (kind === 1) {\n'
                    '    return "sort by start, merge";\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return "heap of end times";\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return "sort by end, greedy";\n  }\n'
                    '  return "two pointers";\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} ${technique(k)}`);\n}\n',
                    '  if (kind === 3) {\n'
                    '    return "sort by end, greedy";\n  }',
                    [("1 2 3 4", "1 sort by start, merge\n2 heap of end times\n3 sort by end, greedy\n4 two pointers")],
                    hints=["Kind 3 is 'the most meetings one person can attend'.",
                           'Write if (kind === 3) { return "sort by end, greedy"; }'],
                    difficulty="Easy"),
                _fix("tscourse-w28-gr-fix1", "Fix the greedy that took the long meeting",
                     "On `1-10 2-3 4-5` one person can attend two meetings. This says 1: it sorts by START, takes `1-10` because it begins first, and that one meeting blocks both of the others.",
                     _WORDS + _IVALS +
                     'const sorted = [...ivs].sort((a, b) => a.start - b.start);\n'
                     'let lastEnd = -Infinity;\n'
                     'let kept = 0;\n'
                     'for (const x of sorted) {\n'
                     '  if (x.start >= lastEnd) {\n'
                     '    kept = kept + 1;\n'
                     '    lastEnd = x.end;\n  }\n}\n'
                     'console.log(kept);\n',
                     _WORDS + _IVALS +
                     'const sorted = [...ivs].sort((a, b) => a.end - b.end);\n'
                     'let lastEnd = -Infinity;\n'
                     'let kept = 0;\n'
                     'for (const x of sorted) {\n'
                     '  if (x.start >= lastEnd) {\n'
                     '    kept = kept + 1;\n'
                     '    lastEnd = x.end;\n  }\n}\n'
                     'console.log(kept);\n',
                     [("1-10 2-3 4-5", "2"), ("1-2 2-3 3-4 1-3", "3")],
                     hints=["Starting first says nothing about how much time a meeting uses up.",
                            "The safe choice is the one that FINISHES first.",
                            "Sort by end: (a, b) => a.end - b.end."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is greedy right here and wrong for coins 1, 3, 4?",
                   ["luck", "here an exchange argument proves the greedy choice is safe; for those coins no such argument exists",
                    "intervals are sorted", "coins are numbers"], 1,
                   "A greedy needs a proof."),
                _q("`x.start >= lastEnd` uses `>=` because…",
                   ["style", "a meeting may start exactly when the last one ended", "of sorting", "types"], 1,
                   "Half-open again."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w28-review", "Month 7, assembled",
            "Which of four months' tools a question is asking for.",
            """
Month 7 added four ideas to month 6's toolkit. Together they cover most of what a
coding interview asks.

| the question says | the tool | week |
|---|---|---|
| "all …", "every …" | backtracking | 25 |
| "how many ways", "fewest", "longest", with repeated subproblems | DP | 26 |
| "reachable", "fewest steps", "order with prerequisites" | BFS / DFS / topo | 27 |
| "the smallest so far, repeatedly", "top k", "cheapest path" | heap | 28 |
| "overlapping ranges", "rooms", "the most that fit" | sort + sweep (+ heap) | 28 |

## Heapsort, for completeness

Push everything into a heap and pop it all back out: sorted, in O(n log n). Done
**inside the array** (build the heap in place, then repeatedly swap the root to the
end), it needs no extra memory at all — the one O(n log n), O(1)-space sort in week
24's table that was missing. It is not stable, and in practice the built-in beats it;
it matters as the reason "a heap is a sort you can stop early".

## The running median

A stream of numbers; after each one, the median so far. Keep **two heaps**: a
max-heap of the smaller half and a min-heap of the larger half, balanced so their
sizes differ by at most one. The median is a root, or the average of the two roots.
Each number costs O(log n). It is the stretch goal of this week's capstone, and the
single best example of why a heap's cheap `peek` matters.

> ⚠️ **Common mistakes:** reaching for sorting when the data keeps arriving; a
> heap when a single sort would do; and unbalanced median heaps.
""",
            warmup=[
                _q("\"The cheapest route through a weighted graph\" is…",
                   ["BFS", "Dijkstra with a heap", "DP only", "backtracking"], 1,
                   "Weeks 27 and 28."),
                _q("Heapsort's extra space, done in the array, is…",
                   ["O(n)", "O(1)", "O(log n)", "O(n²)"], 1,
                   "The missing row of week 24's table."),
                _q("The running median uses…",
                   ["one heap", "two heaps, one per half", "a sorted array", "a Set"], 1,
                   "Balanced to within one."),
                _q("When all the data is known up front and you need everything in order…",
                   ["use a heap", "just sort it", "use DP", "use BFS"], 1,
                   "A heap earns its place when data keeps arriving."),
            ],
            exercises=[
                _ex("tscourse-w28-rv-1", "Heapsort",
                    "Push everything, pop everything.",
                    _NUMS + _HEAP +
                    'const heap = new MinHeap<number>((a, b) => a - b);\n'
                    'for (const x of nums) {\n'
                    '  heap.push(x);\n}\n'
                    'const out: number[] = [];\n'
                    'while (heap.size > 0) {\n'
                    '  out.push(heap.pop() ?? 0);\n}\n'
                    'console.log(out.join(" "));\n',
                    'while (heap.size > 0) {\n'
                    '  out.push(heap.pop() ?? 0);\n}',
                    [("5 1 4 2 3", "1 2 3 4 5"), ("2 2 1", "1 2 2")],
                    hints=["Each pop hands back the smallest remaining item.",
                           "Pop until the heap is empty, collecting as you go."],
                    difficulty="Easy"),
                _ex("tscourse-w28-rv-2", "Name the week",
                    "Map each question to the week whose tool answers it.",
                    _NUMS +
                    'function week(kind: number): number {\n'
                    '  if (kind === 1) {\n'
                    '    return 25;\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return 26;\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return 27;\n  }\n'
                    '  return 28;\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} week ${week(k)}`);\n}\n',
                    '  if (kind === 2) {\n'
                    '    return 26;\n  }',
                    [("1 2 3 4", "1 week 25\n2 week 26\n3 week 27\n4 week 28")],
                    hints=["Kind 2 is 'how many ways', with repeated subproblems.",
                           "Write if (kind === 2) { return 26; }"],
                    difficulty="Easy"),
                _ex("tscourse-w28-rv-3", "The next job, whenever it arrives",
                    "Jobs arrive over time; at each `run`, start the highest-priority job waiting.",
                    _WORDS + _HEAP +
                    'interface Job {\n'
                    '  readonly name: string;\n'
                    '  readonly pri: number;\n}\n'
                    'const waiting = new MinHeap<Job>((a, b) => b.pri - a.pri || a.name.localeCompare(b.name));\n'
                    'const ran: string[] = [];\n'
                    'for (const w of words) {\n'
                    '  if (w === "run") {\n'
                    '    const next = waiting.pop();\n'
                    '    ran.push(next?.name ?? "idle");\n'
                    '  } else {\n'
                    '    const [name, pri] = w.split(":");\n'
                    '    waiting.push({ name: name ?? "", pri: Number(pri ?? "0") });\n  }\n}\n'
                    'console.log(ran.join(" "));\n',
                    'const waiting = new MinHeap<Job>((a, b) => b.pri - a.pri || a.name.localeCompare(b.name));',
                    [("a:1 b:5 run c:3 run run run", "b c a idle"), ("x:2 y:2 run run", "x y")],
                    hints=["HIGHEST priority first, so the comparator is reversed; ties by name.",
                           "Write const waiting = new MinHeap<Job>((a, b) => b.pri - a.pri || a.name.localeCompare(b.name));"],
                    difficulty="Medium"),
            ],
            quiz=[
                _q("A heap is 'a sort you can stop early' because…",
                   ["it is fast", "the first k pops give the k smallest without ordering the rest", "it is stable",
                    "it is in place"], 1,
                   "O(n + k log n) with an in-place build."),
                _q("Month 7's four new tools are…",
                   ["loops, arrays, maps, sets", "backtracking, DP, graph search, heaps and intervals",
                    "sorting, searching, windows, prefix sums", "classes, generics, modules, async"], 1,
                   "Weeks 25-28."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #28 — the scheduler",
        """
One day's meetings, three questions.

Input: one meeting per line, `start end`, in any order.

```
1 3
2 6
8 10
9 12
15 18
```

```
Busy:      1-6 8-12 15-18
Rooms:     2
Attend:    3  1-3 8-10 15-18
```

**The rows:**

* **Busy** — the merged busy blocks, in order. Blocks that merely **touch** (`1-2`
  and `2-3`) merge, because the time is continuously busy.
* **Rooms** — the most meetings in progress at once, using a **min-heap of end
  times**. Meetings are half-open: one ending at 2 and one starting at 2 can share a
  room.
* **Attend** — the most meetings one person can attend, by the earliest-end greedy,
  followed by the meetings it chose. On equal end times, the earlier start is
  preferred.

An empty input prints `Busy:      none`, `Rooms:     0` and `Attend:    0  none`.

Label padded to 11; the Attend count and its list are separated by two spaces.

**What makes it a rep:** three techniques from the week on one dataset — sort and
merge, a heap of end times, and the one greedy that is provably right — and the tests
include back-to-back meetings, where the three answers treat touching differently on
purpose.
""",
        _ch("tscourse-w28-capstone", "Interview rep #28", "Hard",
            "Report the merged busy blocks, the rooms needed, and the most meetings one person "
            "can attend.",
            _FS + _HEAP +
            'interface Meeting {\n'
            '  readonly start: number;\n'
            '  readonly end: number;\n}\n'
            'const meetings: readonly Meeting[] = fs.readFileSync(0, "utf8")\n'
            '  .split("\\n")\n'
            '  .map((l) => l.trim())\n'
            '  .filter((l) => l !== "")\n'
            '  .map((l) => {\n'
            '    const [s, e] = l.split(/\\s+/).map(Number);\n'
            '    return { start: s ?? 0, end: e ?? 0 };\n'
            '  });\n'
            'function row(label: string, text: string): string {\n'
            '  return `${(label + ":").padEnd(11)}${text}`;\n}\n'
            'function show(xs: readonly Meeting[]): string {\n'
            '  return xs.length === 0 ? "none" : xs.map((m) => `${m.start}-${m.end}`).join(" ");\n}\n'
            'const byStart = [...meetings].sort((a, b) => a.start - b.start || a.end - b.end);\n'
            'const busy: { start: number; end: number }[] = [];\n'
            'for (const m of byStart) {\n'
            '  const last = busy[busy.length - 1];\n'
            '  if (last !== undefined && m.start <= last.end) {\n'
            '    last.end = Math.max(last.end, m.end);\n'
            '  } else {\n'
            '    busy.push({ ...m });\n  }\n}\n'
            'console.log(row("Busy", show(busy)));\n'
            'const ends = new MinHeap<number>((a, b) => a - b);\n'
            'let rooms = 0;\n'
            'for (const m of byStart) {\n'
            '  if (ends.size > 0 && (ends.peek() ?? 0) <= m.start) {\n'
            '    ends.pop();\n  }\n'
            '  ends.push(m.end);\n'
            '  rooms = Math.max(rooms, ends.size);\n}\n'
            'console.log(row("Rooms", String(rooms)));\n'
            'const byEnd = [...meetings].sort((a, b) => a.end - b.end || a.start - b.start);\n'
            'const taken: Meeting[] = [];\n'
            'let lastEnd = -Infinity;\n'
            'for (const m of byEnd) {\n'
            '  if (m.start >= lastEnd) {\n'
            '    taken.push(m);\n'
            '    lastEnd = m.end;\n  }\n}\n'
            'console.log(row("Attend", `${taken.length}  ${show(taken)}`));\n',
            'const byStart = [...meetings].sort((a, b) => a.start - b.start || a.end - b.end);\n'
            'const busy: { start: number; end: number }[] = [];\n'
            'for (const m of byStart) {\n'
            '  const last = busy[busy.length - 1];\n'
            '  if (last !== undefined && m.start <= last.end) {\n'
            '    last.end = Math.max(last.end, m.end);\n'
            '  } else {\n'
            '    busy.push({ ...m });\n  }\n}\n'
            'console.log(row("Busy", show(busy)));\n'
            'const ends = new MinHeap<number>((a, b) => a - b);\n'
            'let rooms = 0;\n'
            'for (const m of byStart) {\n'
            '  if (ends.size > 0 && (ends.peek() ?? 0) <= m.start) {\n'
            '    ends.pop();\n  }\n'
            '  ends.push(m.end);\n'
            '  rooms = Math.max(rooms, ends.size);\n}\n'
            'console.log(row("Rooms", String(rooms)));\n'
            'const byEnd = [...meetings].sort((a, b) => a.end - b.end || a.start - b.start);\n'
            'const taken: Meeting[] = [];\n'
            'let lastEnd = -Infinity;\n'
            'for (const m of byEnd) {\n'
            '  if (m.start >= lastEnd) {\n'
            '    taken.push(m);\n'
            '    lastEnd = m.end;\n  }\n}\n'
            'console.log(row("Attend", `${taken.length}  ${show(taken)}`));',
            [("1 3\n2 6\n8 10\n9 12\n15 18",
              "Busy:      1-6 8-12 15-18\nRooms:     2\nAttend:    3  1-3 8-10 15-18"),
             ("1 2\n2 3\n3 4", "Busy:      1-4\nRooms:     1\nAttend:    3  1-2 2-3 3-4"),
             ("0 30\n5 10\n15 20\n5 25",
              "Busy:      0-30\nRooms:     3\nAttend:    2  5-10 15-20"),
             ("", "Busy:      none\nRooms:     0\nAttend:    0  none")],
            hints=["Sort once by start for Busy and Rooms, and once by end for Attend.",
                   "Busy merges with `<=`, so touching blocks join; Rooms frees a room when the earliest end is `<=` the new start.",
                   "The rooms heap holds END times of meetings still running; its size after each push is the rooms in use.",
                   "Attend takes a meeting when it starts at or after the last chosen meeting's end.",
                   "The second test is three back-to-back meetings: one busy block, one room, and all three attended."]),
        example_io="Busy:      1-6 8-12 15-18\nRooms:     2\nAttend:    3  1-3 8-10 15-18",
        rubric=["the heap is the week's MinHeap class, with no parameter properties",
                "busy blocks are merged after sorting by start, with Math.max for contained meetings",
                "rooms come from a min-heap of end times, freeing a room on `<=`",
                "the attend greedy sorts by end and is not replaced by sorting on start",
                "touching meetings are handled as the brief states, per question",
                "empty input prints all three rows",
                "no index access is asserted with `!`"],
        stretch=_ch("tscourse-w28-capstone-stretch", "Interview rep #28 (stretch)", "Hard",
                    "The running median. Read a stream of numbers and, after each one, print the median of "
                    "everything so far — space-separated on one line. Keep two heaps: a max-heap of the "
                    "smaller half and a min-heap of the larger half, rebalanced so the lower half is never "
                    "smaller than the upper and never more than one larger. An even count's median is the "
                    "average of the two roots.",
                    _NUMS + _HEAP +
                    'const low = new MinHeap<number>((a, b) => b - a);\n'
                    'const high = new MinHeap<number>((a, b) => a - b);\n'
                    'const medians: number[] = [];\n'
                    'for (const x of nums) {\n'
                    '  if (low.size === 0 || x <= (low.peek() ?? 0)) {\n'
                    '    low.push(x);\n'
                    '  } else {\n'
                    '    high.push(x);\n  }\n'
                    '  if (low.size > high.size + 1) {\n'
                    '    high.push(low.pop() ?? 0);\n'
                    '  } else if (high.size > low.size) {\n'
                    '    low.push(high.pop() ?? 0);\n  }\n'
                    '  medians.push(low.size > high.size ? (low.peek() ?? 0) : ((low.peek() ?? 0) + (high.peek() ?? 0)) / 2);\n}\n'
                    'console.log(medians.join(" "));\n',
                    'const medians: number[] = [];\n'
                    'for (const x of nums) {\n'
                    '  if (low.size === 0 || x <= (low.peek() ?? 0)) {\n'
                    '    low.push(x);\n'
                    '  } else {\n'
                    '    high.push(x);\n  }\n'
                    '  if (low.size > high.size + 1) {\n'
                    '    high.push(low.pop() ?? 0);\n'
                    '  } else if (high.size > low.size) {\n'
                    '    low.push(high.pop() ?? 0);\n  }\n'
                    '  medians.push(low.size > high.size ? (low.peek() ?? 0) : ((low.peek() ?? 0) + (high.peek() ?? 0)) / 2);\n}',
                    [("5 15 1 3", "5 10 5 4"), ("2 4 6 8 10", "2 3 4 5 6"), ("7", "7")],
                    hints=["The lower half is a MAX-heap: its root is the largest of the small numbers.",
                           "Insert into the lower half if x is no bigger than its root; otherwise the upper half.",
                           "Then move one root across if the sizes drift apart.",
                           "Odd count: the median is the lower half's root. Even: average the two roots."]),
    ),
))
