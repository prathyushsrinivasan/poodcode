# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 3 — Searching and sorting by hand.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# This is the first module where the ALGORITHM is the content rather than the
# syntax. Every sort here is written out longhand before `Arrays.sort` is even
# mentioned, because "I would call Arrays.sort" is a correct answer that no
# interviewer accepts and no debugging session is helped by.
#
# The Python mirrors below (_bubble_*, _selection_*, _insertion_*) exist so the
# multi-line trace outputs are COMPUTED. Hand-typing "the array after pass 3"
# for five test cases is how wrong expected output gets shipped.
# ---------------------------------------------------------------------------

_M3 = []


# --- Python mirrors, so every expected output is computed --------------------

def _bubble_sorted(a):
    a = list(a)
    n = len(a)
    for p in range(n - 1):
        for i in range(n - 1 - p):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
    return a


def _bubble_trace(a):
    """One `Arrays.toString` line per pass — the whole point of the drill."""
    a = list(a)
    n = len(a)
    out = []
    for p in range(n - 1):
        for i in range(n - 1 - p):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
        out.append(_jarr(a))
    return _nl(*out)


def _bubble_early(a):
    """Sorted array, then the number of passes an early-exit bubble sort ran."""
    a = list(a)
    n = len(a)
    passes = 0
    for p in range(n - 1):
        swapped = False
        for i in range(n - 1 - p):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        passes += 1
        if not swapped:
            break
    return _nl(_jarr(a), passes)


def _bubble_swaps(a):
    a = list(a)
    n = len(a)
    swaps = 0
    for p in range(n - 1):
        for i in range(n - 1 - p):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swaps += 1
    return swaps


def _selection_trace(a):
    a = list(a)
    n = len(a)
    out = []
    for i in range(n - 1):
        lo = i
        for j in range(i + 1, n):
            if a[j] < a[lo]:
                lo = j
        a[i], a[lo] = a[lo], a[i]
        out.append(_jarr(a))
    return _nl(*out)


def _selection_desc(a):
    a = list(a)
    n = len(a)
    for i in range(n - 1):
        hi = i
        for j in range(i + 1, n):
            if a[j] > a[hi]:
                hi = j
        a[i], a[hi] = a[hi], a[i]
    return a


def _insertion_shifts(a):
    a = list(a)
    shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
            shifts += 1
        a[j + 1] = key
    return _nl(_jarr(a), shifts)


def _bsearch(a, target):
    """The index a textbook binary search lands on. The test arrays are
    duplicate-free, so this is unambiguous."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def _lower_bound(a, target):
    return sum(1 for x in a if x < target)


def _java_bsearch(a, target):
    """`Arrays.binarySearch` semantics: the index if present, otherwise
    `-(insertion point) - 1`."""
    i = _bsearch(a, target)
    return i if i >= 0 else -_lower_bound(a, target) - 1


def _is_sorted(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


# --- 3.1 Binary search ------------------------------------------------------

_M3.append(_jlesson(
    "m3-binary", "Binary search",
    "Halve the range every step — and get the four fiddly details right.",
    """
Linear search looks at everything. Binary search throws away half the array on
every comparison, so it finds a value among a million in about **20** steps
instead of a million. The price is a precondition you must state out loud:
**the array has to be sorted.**

```java
int lo = 0, hi = a.length - 1, idx = -1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == target)      { idx = mid; break; }
    else if (a[mid] < target)  lo = mid + 1;      // answer is to the RIGHT
    else                       hi = mid - 1;      // answer is to the LEFT
}
```

Four details, each of which is a bug if you get it wrong.

**`lo <= hi`, not `lo < hi`.** When the range narrows to one element, `lo`
equals `hi` — and that element still has to be checked. `lo < hi` skips it, so
the search fails whenever the answer is the last candidate standing.

**`mid = lo + (hi - lo) / 2`, not `(lo + hi) / 2`.** For large indices
`lo + hi` can overflow `int` and go negative, which then throws. Java's own
`Arrays.binarySearch` had this bug until 2006, in code that had been proof-read
for twenty years. The rewritten form can never overflow, costs nothing, and
signals to an interviewer that you know why.

**`mid + 1` and `mid - 1`, not `mid`.** You have just proved `a[mid]` is not
the target, so leaving it in the range makes no progress — and when the range
is two elements wide, `hi = mid` loops forever.

**Halving is what makes it O(log n).** Each step discards half the remaining
candidates: n → n/2 → n/4 → … → 1. That takes log₂(n) steps — about 20 for a
million, about 30 for a billion.

**The related shape: lower bound.** "Where would this value go?" — the first
index whose value is `>= target` — is the same loop with a half-open range and
no early exit:

```java
int lo = 0, hi = a.length;              // hi is one PAST the end
while (lo < hi) {                        // strict <, because hi is exclusive
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < target) lo = mid + 1;
    else hi = mid;                       // keep mid: it might be the answer
}
// lo is now the insertion point, and also the count of values < target
```
""",
    warmup=[
        _jq("`a = {1, 3, 5, 7}`, target `7`, and the loop condition is `while (lo < hi)`. What is printed?",
            ["-1", "3", "2", "It loops forever"],
            0,
            "The range narrows to lo == hi == 3, and `lo < hi` is false, so index 3 is never "
            "examined. Binary search needs `lo <= hi`."),
        _jq("Why write `mid = lo + (hi - lo) / 2` instead of `(lo + hi) / 2`?",
            ["`lo + hi` can overflow int on a large array and go negative",
             "It is faster", "`(lo + hi) / 2` rounds the wrong way",
             "It isn't — the two are identical in every way"],
            0,
            "For indices past ~1 billion the sum wraps negative, and `a[negative]` throws. "
            "`hi - lo` is always small, so the rewritten form is safe."),
    ],
    exercises=[
        _je("j3-bin-mid", "The safe midpoint",
            "The array arrives **sorted**. Print the index of `target`, or `-1`. "
            "Replace `____` with the line that computes the midpoint — write the "
            "overflow-safe form.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int lo = 0;\n"
                  "        int hi = n - 1;\n"
                  "        int idx = -1;\n"
                  "        while (lo <= hi) {\n"
                  "            int mid = lo + (hi - lo) / 2;\n"
                  "            if (a[mid] == target) { idx = mid; break; }\n"
                  "            else if (a[mid] < target) lo = mid + 1;\n"
                  "            else hi = mid - 1;\n"
                  "        }\n"
                  "        System.out.println(idx);"),
            "int mid = lo + (hi - lo) / 2;",
            [_akcase(a, t, _bsearch(a, t))
             for (a, t) in (([1, 3, 5, 7, 9], 7), ([1, 3, 5, 7, 9], 1),
                            ([1, 3, 5, 7, 9], 4), ([2], 2))],
            hints=["Start from `lo` and add half the distance to `hi`.",
                   "`hi - lo` is the width of the range.",
                   "`int mid = lo + (hi - lo) / 2;`"]),

        _je("j3-bin-branch", "Which half survives",
            "Same search, but the branch that discards the left half is missing. "
            "Replace `____` with it — you have just proved `a[mid]` is too small.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        int lo = 0;\n"
                  "        int hi = n - 1;\n"
                  "        int idx = -1;\n"
                  "        while (lo <= hi) {\n"
                  "            int mid = lo + (hi - lo) / 2;\n"
                  "            if (a[mid] == target) { idx = mid; break; }\n"
                  "            else if (a[mid] < target) lo = mid + 1;\n"
                  "            else hi = mid - 1;\n"
                  "        }\n"
                  "        System.out.println(idx);"),
            "else if (a[mid] < target) lo = mid + 1;",
            [_akcase(a, t, _bsearch(a, t))
             for (a, t) in (([1, 3, 5, 7, 9], 9), ([1, 3, 5, 7, 9], 3),
                            ([1, 3, 5, 7, 9], 8), ([10, 20], 20))],
            hints=["If the middle value is smaller than the target, the answer is to its right.",
                   "So the new lower bound is just past `mid`.",
                   "`else if (a[mid] < target) lo = mid + 1;`"],
            difficulty="Medium"),

        _jfix("j3-bin-strict", "It misses the last candidate",
              "This binary search works most of the time but returns `-1` for values "
              "that sit at the very edge of the search — try `{1, 3, 5, 7}` looking "
              "for `7`. One comparison operator is wrong.",
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int lo = 0;\n"
                    "        int hi = n - 1;\n"
                    "        int idx = -1;\n"
                    "        while (lo < hi) {\n"
                    "            int mid = lo + (hi - lo) / 2;\n"
                    "            if (a[mid] == target) { idx = mid; break; }\n"
                    "            else if (a[mid] < target) lo = mid + 1;\n"
                    "            else hi = mid - 1;\n"
                    "        }\n"
                    "        System.out.println(idx);"),
              _jscan(
                  _RD_ARR
                  + "        int target = sc.nextInt();\n"
                    "        int lo = 0;\n"
                    "        int hi = n - 1;\n"
                    "        int idx = -1;\n"
                    "        while (lo <= hi) {\n"
                    "            int mid = lo + (hi - lo) / 2;\n"
                    "            if (a[mid] == target) { idx = mid; break; }\n"
                    "            else if (a[mid] < target) lo = mid + 1;\n"
                    "            else hi = mid - 1;\n"
                    "        }\n"
                    "        System.out.println(idx);"),
              [_akcase(a, t, _bsearch(a, t))
               for (a, t) in (([1, 3, 5, 7], 7), ([1, 3, 5, 7], 1),
                              ([5], 5), ([1, 3, 5, 7], 6))],
              hints=["What happens when the range narrows to exactly one element?",
                     "At that point `lo == hi`, and that element has not been checked yet.",
                     "`while (lo <= hi)`"]),

        _jch("j3-bin-lower", "Where would it go?", "Hard",
             "The array is sorted. Print the **insertion point** of `target` — the "
             "first index whose value is `>= target`, or `n` if every value is "
             "smaller. This is also the count of values strictly less than `target`. "
             "Use a binary search (half-open range), not a scan. Write the whole "
             "block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int target = sc.nextInt();\n"
                   "        int lo = 0;\n"
                   "        int hi = n;\n"
                   "        while (lo < hi) {\n"
                   "            int mid = lo + (hi - lo) / 2;\n"
                   "            if (a[mid] < target) lo = mid + 1;\n"
                   "            else hi = mid;\n"
                   "        }\n"
                   "        System.out.println(lo);"),
             "        int lo = 0;\n"
             "        int hi = n;\n"
             "        while (lo < hi) {\n"
             "            int mid = lo + (hi - lo) / 2;\n"
             "            if (a[mid] < target) lo = mid + 1;\n"
             "            else hi = mid;\n"
             "        }\n"
             "        System.out.println(lo);",
             [_akcase(a, t, _lower_bound(a, t))
              for (a, t) in (([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 4),
                             ([1, 3, 5, 7, 9], 0), ([1, 3, 5, 7, 9], 100),
                             ([2, 2, 2, 8], 2))],
             hints=["`hi` starts at `n`, one past the end — so the loop condition is `lo < hi`.",
                    "There is no early exit and no `== target` branch: you want a position, "
                    "not a hit.",
                    "When `a[mid] >= target`, `mid` might itself be the answer, so `hi = mid` "
                    "— not `mid - 1`.",
                    "When the loop ends, `lo == hi` and that is the answer."]),
    ],
    quiz=[
        _jq("Roughly how many comparisons does binary search need on a sorted array of 1,000,000?",
            ["About 20", "About 1,000", "About 500,000", "1,000,000"],
            0,
            "log₂(1,000,000) ≈ 20. Each comparison halves the candidates, and 2²⁰ is just "
            "over a million."),
        _jq("Your binary search sets `hi = mid` in the 'go left' branch. What happens?",
            ["It can loop forever once the range is two elements wide",
             "It returns the wrong index but terminates",
             "Nothing — it is equivalent",
             "It throws ArrayIndexOutOfBoundsException"],
            0,
            "With lo=0, hi=1, mid computes to 0; if the answer is left, `hi = mid` leaves the "
            "range unchanged and nothing ever shrinks. `mid - 1` guarantees progress."),
    ],
))

# --- 3.2 Bubble sort --------------------------------------------------------

_M3.append(_jlesson(
    "m3-bubble", "Bubble sort",
    "Compare neighbours, swap when out of order, repeat — and stop early when you can.",
    """
Bubble sort is the one everybody learns and nobody ships. It is here because
its *shape* — compare adjacent pairs, swap, repeat — is the simplest correct
sort, and because the early-exit variant is a genuinely instructive
optimisation.

```java
for (int pass = 0; pass < n - 1; pass++) {
    for (int i = 0; i < n - 1 - pass; i++) {
        if (a[i] > a[i + 1]) {
            int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;
        }
    }
}
```

**Why the largest element ends up at the end.** In one inner pass, any element
bigger than its right-hand neighbour keeps getting carried right. The biggest
one can never be stopped, so after pass 0 it is parked at index `n-1`. After
pass 1 the second-biggest is at `n-2`, and so on — the tail grows sorted from
the right.

**Why the inner bound is `n - 1 - pass`.** The last `pass` slots are already
final. Comparing them again is not wrong, just wasted — and writing the bound
proves you understand the invariant.

**Why `n - 1` passes, not `n`.** Once `n - 1` elements are in their final
places, the remaining one has nowhere else to be.

**The early exit.** If a whole pass makes no swaps, the array is sorted and
every remaining pass would do nothing:

```java
for (int pass = 0; pass < n - 1; pass++) {
    boolean swapped = false;
    for (int i = 0; i < n - 1 - pass; i++) {
        if (a[i] > a[i + 1]) { /* swap */ swapped = true; }
    }
    if (!swapped) break;
}
```

That single flag turns the **best case from O(n²) into O(n)**: an
already-sorted array is confirmed in one pass. It is the only reason anyone
ever defends bubble sort.

**Cost.** Worst and average O(n²) comparisons, O(n²) swaps. Best case O(n)
*with* the flag, O(n²) without. Space O(1) — it sorts in place. It is
**stable**: equal elements never jump over each other, because the swap only
fires on a strict `>`.
""",
    warmup=[
        _jq("`{5, 1, 4, 2}` after **one** full inner pass of bubble sort is…",
            ["[1, 4, 2, 5]", "[1, 2, 4, 5]", "[5, 4, 2, 1]", "[1, 5, 4, 2]"],
            0,
            "5>1 swap → [1,5,4,2]; 5>4 swap → [1,4,5,2]; 5>2 swap → [1,4,2,5]. The largest "
            "element has bubbled to the end, which is the guarantee of one pass."),
        _jq("What does the `swapped` flag change?",
            ["The best case drops from O(n²) to O(n)",
             "The worst case drops to O(n log n)",
             "It makes the sort stable",
             "It removes the need for a temp variable"],
            0,
            "A pass with no swaps proves the array is sorted, so you can stop. The worst "
            "case is untouched — reversed input still swaps on every comparison."),
    ],
    exercises=[
        _je("j3-bub-swap", "Swap the neighbours",
            "Sort the array with bubble sort and print it. Replace `____` with the "
            "body that exchanges `a[i]` and `a[i + 1]`.",
            _jscan(
                _RD_ARR
                + "        for (int pass = 0; pass < n - 1; pass++) {\n"
                  "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                  "                if (a[i] > a[i + 1]) {\n"
                  "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
                  "                }\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;",
            [_acase(a, _jarr(sorted(a)))
             for a in ([5, 1, 4, 2], [3, 2, 1], [1, 2, 3], [7], [4, 4, 2, 2])],
            hints=["Module 1's three-line swap, with `i` and `i + 1`.",
                   "You need a temp, or you lose one of the two values.",
                   "`int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;`"]),

        _je("j3-bub-bound", "Stop where the sorted tail begins",
            "Same sort, but write the inner loop's bound so it skips the elements "
            "already parked at the end. Replace `____` with the inner `for` header.",
            _jscan(
                _RD_ARR
                + "        for (int pass = 0; pass < n - 1; pass++) {\n"
                  "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                  "                if (a[i] > a[i + 1]) {\n"
                  "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
                  "                }\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "for (int i = 0; i < n - 1 - pass; i++) {",
            [_acase(a, _jarr(sorted(a)))
             for a in ([5, 1, 4, 2], [9, 8, 7, 6, 5], [1], [2, 1])],
            hints=["After `pass` passes, that many elements are final at the tail.",
                   "You also stop one early because the loop looks at `a[i + 1]`.",
                   "`for (int i = 0; i < n - 1 - pass; i++) {`"],
            difficulty="Medium"),

        _je("j3-bub-trace", "Watch it happen",
            "Print the array after **every** pass, one `Arrays.toString` line per "
            "pass, so you can see the sorted tail grow. Replace `____` with the "
            "print statement — think about where it belongs.",
            _jscan(
                _RD_ARR
                + "        for (int pass = 0; pass < n - 1; pass++) {\n"
                  "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                  "                if (a[i] > a[i + 1]) {\n"
                  "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
                  "                }\n"
                  "            }\n"
                  "            System.out.println(Arrays.toString(a));\n"
                  "        }"),
            "            System.out.println(Arrays.toString(a));",
            [_acase(a, _bubble_trace(a))
             for a in ([5, 1, 4, 2], [3, 2, 1], [1, 2, 3, 4])],
            hints=["One line per pass means printing in the outer loop.",
                   "After the inner loop has finished, not inside it.",
                   "`System.out.println(Arrays.toString(a));` as the last statement of the "
                   "outer loop body."]),

        _jfix("j3-bub-clobber", "The swap that loses a value",
              "This bubble sort fills the array with duplicates instead of sorting "
              "it. The comparison is fine; the swap is not.",
              _jscan(
                  _RD_ARR
                  + "        for (int pass = 0; pass < n - 1; pass++) {\n"
                    "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                    "                if (a[i] > a[i + 1]) {\n"
                    "                    a[i] = a[i + 1];\n"
                    "                    a[i + 1] = a[i];\n"
                    "                }\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              _jscan(
                  _RD_ARR
                  + "        for (int pass = 0; pass < n - 1; pass++) {\n"
                    "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                    "                if (a[i] > a[i + 1]) {\n"
                    "                    int t = a[i];\n"
                    "                    a[i] = a[i + 1];\n"
                    "                    a[i + 1] = t;\n"
                    "                }\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              [_acase(a, _jarr(sorted(a))) for a in ([5, 1, 4, 2], [3, 1], [2, 2, 1])],
              hints=["Trace the two assignments with a[i]=5, a[i+1]=1.",
                     "The first line overwrites the value the second line needs.",
                     "Save it first: `int t = a[i];`"]),

        _jch("j3-bub-early", "Stop as soon as it is sorted", "Medium",
             "Bubble sort with an early exit. Print two lines: the sorted array, then "
             "the **number of passes actually performed** (count a pass as soon as its "
             "inner loop finishes, including the final pass that makes no swaps). "
             "An already-sorted array should report `1`. Write the whole block where "
             "you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int passes = 0;\n"
                   "        for (int pass = 0; pass < n - 1; pass++) {\n"
                   "            boolean swapped = false;\n"
                   "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                   "                if (a[i] > a[i + 1]) {\n"
                   "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
                   "                    swapped = true;\n"
                   "                }\n"
                   "            }\n"
                   "            passes++;\n"
                   "            if (!swapped) break;\n"
                   "        }\n"
                   "        System.out.println(Arrays.toString(a));\n"
                   "        System.out.println(passes);"),
             "        int passes = 0;\n"
             "        for (int pass = 0; pass < n - 1; pass++) {\n"
             "            boolean swapped = false;\n"
             "            for (int i = 0; i < n - 1 - pass; i++) {\n"
             "                if (a[i] > a[i + 1]) {\n"
             "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
             "                    swapped = true;\n"
             "                }\n"
             "            }\n"
             "            passes++;\n"
             "            if (!swapped) break;\n"
             "        }\n"
             "        System.out.println(Arrays.toString(a));\n"
             "        System.out.println(passes);",
             [_acase(a, _bubble_early(a))
              for a in ([1, 2, 3, 4], [5, 1, 4, 2], [4, 3, 2, 1], [2, 1], [6])],
             hints=["`boolean swapped = false;` goes at the top of each pass — it has to reset.",
                    "Set it to `true` inside the `if`, next to the swap.",
                    "Increment `passes` after the inner loop, then `if (!swapped) break;`.",
                    "With n = 1 the outer loop never runs, so `passes` stays 0 — that is "
                    "correct, there was nothing to do."]),
    ],
    quiz=[
        _jq("Why is `n - 1 - pass` the right inner bound rather than `n - 1`?",
            ["The last `pass` elements are already in their final positions",
             "It prevents an ArrayIndexOutOfBoundsException",
             "It makes the sort stable",
             "It is required for the early exit to work"],
            0,
            "`n - 1` would still sort correctly, just with wasted comparisons. The tighter "
            "bound encodes the invariant that the tail is finished."),
        _jq("Bubble sort is stable. Which detail makes it so?",
            ["The swap fires only on strict `>`, so equal elements never cross",
             "It compares adjacent pairs",
             "It sorts in place",
             "The early-exit flag"],
            0,
            "Change `>` to `>=` and equal elements start swapping past each other — the sort "
            "stays correct but stops being stable."),
    ],
))

# --- 3.3 Selection sort -----------------------------------------------------

_M3.append(_jlesson(
    "m3-selection", "Selection sort",
    "Find the smallest of what's left, put it where it belongs, repeat.",
    """
Selection sort builds the answer from the **front**. On round `i`, it finds the
smallest element in `a[i..n-1]` and swaps it into position `i`.

```java
for (int i = 0; i < n - 1; i++) {
    int min = i;                                  // assume position i wins
    for (int j = i + 1; j < n; j++) {
        if (a[j] < a[min]) min = j;               // module 1's argmin, on a slice
    }
    int t = a[i]; a[i] = a[min]; a[min] = t;      // one swap per round
}
```

**`int min = i;` — not `0`, and not `i + 1`.** It is a *candidate index*, and
the natural candidate is the first unsorted slot. Seeding it with `0` is the
classic bug: after the first round, position 0 is finished and can never be the
minimum of the remaining slice again.

**Exactly `n - 1` swaps, always.** That is its one genuine selling point. If
writes are expensive — flash memory, a network — selection sort moves the least
data of any simple sort. Bubble sort can do O(n²) swaps on the same input.

**Comparisons are always O(n²),** even on sorted input: (n-1) + (n-2) + … + 1 =
n(n-1)/2. There is no early exit, because you cannot know an element is the
minimum without checking every remaining candidate.

**It is NOT stable.** The long-range swap can throw an equal element past its
twin. In `{2a, 2b, 1}` the swap of `1` into position 0 sends `2a` to the back,
behind `2b`. Interviewers like this one because "selection sort is unstable"
sounds arbitrary until you trace exactly this three-element case.

**Descending is one character.** Track a maximum instead: `if (a[j] > a[max])`.
""",
    warmup=[
        _jq("`{29, 10, 14, 37}` after the first round of selection sort is…",
            ["[10, 29, 14, 37]", "[10, 14, 29, 37]", "[29, 10, 14, 37]", "[10, 37, 14, 29]"],
            0,
            "The minimum (10, at index 1) is swapped with index 0, so 29 goes to index 1. "
            "One swap per round, and it is a *swap*, not a shift."),
        _jq("How many swaps does selection sort perform on an already-sorted array of 5 elements?",
            ["4 — one per round, even though each swaps an element with itself",
             "0", "10", "5"],
            0,
            "The textbook version swaps unconditionally, `n - 1` times. Guarding with "
            "`if (min != i)` skips the no-ops, but the comparison count is unchanged."),
    ],
    exercises=[
        _je("j3-sel-argmin", "Find the smallest of the rest",
            "Selection sort, with the inner scan hollowed out. Replace `____` with "
            "the line that keeps `min` pointing at the smallest element seen so far "
            "in the unsorted part.",
            _jscan(
                _RD_ARR
                + "        for (int i = 0; i < n - 1; i++) {\n"
                  "            int min = i;\n"
                  "            for (int j = i + 1; j < n; j++) {\n"
                  "                if (a[j] < a[min]) min = j;\n"
                  "            }\n"
                  "            int t = a[i]; a[i] = a[min]; a[min] = t;\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "if (a[j] < a[min]) min = j;",
            [_acase(a, _jarr(sorted(a)))
             for a in ([29, 10, 14, 37], [3, 2, 1], [1, 2, 3], [5], [4, 4, 1])],
            hints=["`min` holds an index, so the value at it is `a[min]`.",
                   "Compare values; assign indices.",
                   "`if (a[j] < a[min]) min = j;`"]),

        _je("j3-sel-trace", "One round at a time",
            "Print the array after each round, so you can watch the sorted prefix "
            "grow from the left. Replace `____` with the print statement, in the "
            "right place.",
            _jscan(
                _RD_ARR
                + "        for (int i = 0; i < n - 1; i++) {\n"
                  "            int min = i;\n"
                  "            for (int j = i + 1; j < n; j++) {\n"
                  "                if (a[j] < a[min]) min = j;\n"
                  "            }\n"
                  "            int t = a[i]; a[i] = a[min]; a[min] = t;\n"
                  "            System.out.println(Arrays.toString(a));\n"
                  "        }"),
            "            System.out.println(Arrays.toString(a));",
            [_acase(a, _selection_trace(a))
             for a in ([29, 10, 14, 37], [3, 2, 1], [1, 2, 3, 4])],
            hints=["A round ends after the swap, not after the inner loop.",
                   "So the print is the last statement of the outer loop body.",
                   "`System.out.println(Arrays.toString(a));`"]),

        _jfix("j3-sel-seed", "The candidate that never moves",
              "This selection sort gets the first element right and then scrambles "
              "the rest. Look at how the candidate index is seeded.",
              _jscan(
                  _RD_ARR
                  + "        for (int i = 0; i < n - 1; i++) {\n"
                    "            int min = 0;\n"
                    "            for (int j = i + 1; j < n; j++) {\n"
                    "                if (a[j] < a[min]) min = j;\n"
                    "            }\n"
                    "            int t = a[i]; a[i] = a[min]; a[min] = t;\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              _jscan(
                  _RD_ARR
                  + "        for (int i = 0; i < n - 1; i++) {\n"
                    "            int min = i;\n"
                    "            for (int j = i + 1; j < n; j++) {\n"
                    "                if (a[j] < a[min]) min = j;\n"
                    "            }\n"
                    "            int t = a[i]; a[i] = a[min]; a[min] = t;\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              [_acase(a, _jarr(sorted(a)))
               for a in ([3, 1, 2], [29, 10, 14, 37], [5, 4, 3, 2, 1])],
              hints=["After round 0, index 0 is finished. Should it still be a candidate?",
                     "The candidate should be the first slot of the *unsorted* part.",
                     "`int min = i;`"]),

        _jch("j3-sel-desc", "Sort it the other way", "Easy",
             "Write selection sort that produces **descending** order — largest "
             "first. It is the same algorithm with the comparison flipped. Write the "
             "whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        for (int i = 0; i < n - 1; i++) {\n"
                   "            int max = i;\n"
                   "            for (int j = i + 1; j < n; j++) {\n"
                   "                if (a[j] > a[max]) max = j;\n"
                   "            }\n"
                   "            int t = a[i]; a[i] = a[max]; a[max] = t;\n"
                   "        }\n"
                   "        System.out.println(Arrays.toString(a));"),
             "        for (int i = 0; i < n - 1; i++) {\n"
             "            int max = i;\n"
             "            for (int j = i + 1; j < n; j++) {\n"
             "                if (a[j] > a[max]) max = j;\n"
             "            }\n"
             "            int t = a[i]; a[i] = a[max]; a[max] = t;\n"
             "        }\n"
             "        System.out.println(Arrays.toString(a));",
             [_acase(a, _jarr(_selection_desc(a)))
              for a in ([29, 10, 14, 37], [1, 2, 3], [5], [2, 2, 9, 1])],
             hints=["Seed the candidate with `i` exactly as before.",
                    "Only the comparison changes: `>` instead of `<`.",
                    "The swap is unchanged — you are still putting the winner at position `i`."]),
    ],
    quiz=[
        _jq("What is selection sort's one real advantage over bubble and insertion sort?",
            ["It performs at most n - 1 swaps, so it writes the least data",
             "It is stable", "Its best case is O(n)", "It uses no extra memory"],
            0,
            "All three are in-place, and selection sort is neither stable nor fast on sorted "
            "input. Minimal writes is the whole case for it."),
        _jq("Trace selection sort on `{2a, 2b, 1}` (the letters just mark identity). Where does 2a end up?",
            ["Behind 2b — which is why selection sort is not stable",
             "In front of 2b, as it started",
             "It depends on the JVM",
             "The array is unchanged"],
            0,
            "Round 0 swaps 1 into index 0, sending 2a to index 2 — past 2b. Equal elements "
            "changed relative order, so the sort is unstable."),
    ],
))

# --- 3.4 Insertion sort -----------------------------------------------------

_M3.append(_jlesson(
    "m3-insertion", "Insertion sort",
    "How you sort a hand of cards — and the only O(n²) sort worth keeping.",
    """
Take the next element, slide it left past everything bigger, drop it in. It is
literally how people sort a hand of playing cards.

```java
for (int i = 1; i < n; i++) {              // start at 1: a[0] alone is sorted
    int key = a[i];                         // lift the card out
    int j = i - 1;
    while (j >= 0 && a[j] > key) {          // shift bigger elements RIGHT
        a[j + 1] = a[j];
        j--;
    }
    a[j + 1] = key;                         // drop it into the gap
}
```

**The invariant:** `a[0..i-1]` is always sorted. Each round grows that sorted
prefix by one.

**It shifts, it does not swap.** `key` is saved *before* the loop, so the slot
it came from is free to be overwritten. That is why there is no temp inside the
loop, and why insertion sort does about half the writes of a swap-based version.

**`j >= 0 && a[j] > key` — in that order.** Java's `&&` short-circuits: if
`j >= 0` is false, `a[j]` is never evaluated. Write the conditions the other way
round and the moment `key` is smaller than everything, `j` reaches `-1` and
`a[-1]` throws. This is *the* classic insertion-sort bug and the reason
short-circuit evaluation is worth understanding rather than memorising.

**`a[j + 1] = key`, not `a[j] = key`.** The loop exits with `j` sitting one
position *before* the gap — either because `a[j] <= key` or because `j` fell off
the front — so the gap is at `j + 1`.

**Cost.** Worst case O(n²) (reversed input shifts everything every time).
Best case **O(n)**: on sorted input the `while` fails immediately and each
round is one comparison. Average O(n²), but with a very small constant.

**Why it survives in real libraries.** It is stable (`>` not `>=`), in place,
and genuinely the fastest thing there is for small or nearly-sorted arrays —
which is why production quicksorts, Java's included, switch to insertion sort
once a partition gets small.
""",
    warmup=[
        _jq("Why does the loop condition have to be `j >= 0 && a[j] > key` and not `a[j] > key && j >= 0`?",
            ["`&&` short-circuits left to right, so the bounds check must come first",
             "Java evaluates conditions right to left",
             "They are equivalent",
             "Because `key` may be negative"],
            0,
            "With the checks reversed, an element smaller than everything drives `j` to -1 "
            "and `a[-1]` is evaluated before the guard — ArrayIndexOutOfBoundsException."),
        _jq("Insertion sort on an already-sorted array of n elements costs…",
            ["O(n) — the while loop fails on its first test every round",
             "O(n²) regardless",
             "O(n log n)",
             "O(1)"],
            0,
            "Each round does one comparison and no shifts. That best case is why libraries "
            "fall back to insertion sort for small or nearly-sorted ranges."),
    ],
    exercises=[
        _je("j3-ins-while", "Slide the bigger ones right",
            "Insertion sort with the shifting loop's header missing. Replace `____` "
            "with the `while` condition — mind the order of the two tests.",
            _jscan(
                _RD_ARR
                + "        for (int i = 1; i < n; i++) {\n"
                  "            int key = a[i];\n"
                  "            int j = i - 1;\n"
                  "            while (j >= 0 && a[j] > key) {\n"
                  "                a[j + 1] = a[j];\n"
                  "                j--;\n"
                  "            }\n"
                  "            a[j + 1] = key;\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "while (j >= 0 && a[j] > key) {",
            [_acase(a, _jarr(sorted(a)))
             for a in ([5, 2, 4, 6, 1], [3, 2, 1], [1, 2, 3], [7], [2, 2, 1])],
            hints=["Two conditions joined with `&&`.",
                   "The bounds check has to be first, or `a[j]` is read at j = -1.",
                   "`while (j >= 0 && a[j] > key) {`"],
            difficulty="Medium"),

        _je("j3-ins-drop", "Drop it in the gap",
            "The shifting loop has finished and `j` is sitting just before the gap. "
            "Replace `____` with the line that places `key`.",
            _jscan(
                _RD_ARR
                + "        for (int i = 1; i < n; i++) {\n"
                  "            int key = a[i];\n"
                  "            int j = i - 1;\n"
                  "            while (j >= 0 && a[j] > key) {\n"
                  "                a[j + 1] = a[j];\n"
                  "                j--;\n"
                  "            }\n"
                  "            a[j + 1] = key;\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));"),
            "a[j + 1] = key;",
            [_acase(a, _jarr(sorted(a)))
             for a in ([5, 2, 4, 6, 1], [9, 1], [1, 3, 2])],
            hints=["The loop stopped because `a[j]` is small enough — so `j` is not the gap.",
                   "The gap is one slot to the right of `j`.",
                   "`a[j + 1] = key;`"]),

        _jfix("j3-ins-order", "The guard that comes too late",
              "This insertion sort works until the smallest element is not already at "
              "the front, and then throws `ArrayIndexOutOfBoundsException`. Two "
              "conditions are in the wrong order.",
              _jscan(
                  _RD_ARR
                  + "        for (int i = 1; i < n; i++) {\n"
                    "            int key = a[i];\n"
                    "            int j = i - 1;\n"
                    "            while (a[j] > key && j >= 0) {\n"
                    "                a[j + 1] = a[j];\n"
                    "                j--;\n"
                    "            }\n"
                    "            a[j + 1] = key;\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              _jscan(
                  _RD_ARR
                  + "        for (int i = 1; i < n; i++) {\n"
                    "            int key = a[i];\n"
                    "            int j = i - 1;\n"
                    "            while (j >= 0 && a[j] > key) {\n"
                    "                a[j + 1] = a[j];\n"
                    "                j--;\n"
                    "            }\n"
                    "            a[j + 1] = key;\n"
                    "        }\n"
                    "        System.out.println(Arrays.toString(a));"),
              [_acase(a, _jarr(sorted(a)))
               for a in ([5, 1], [3, 2, 1], [4, 5, 6, 0])],
              hints=["What is `a[j]` when `j` has just been decremented to -1?",
                     "`&&` stops evaluating as soon as the left side is false — so put the "
                     "cheap, protective test on the left.",
                     "`while (j >= 0 && a[j] > key) {`"]),

        _jch("j3-ins-shifts", "Count the work", "Medium",
             "Run insertion sort, then print two lines: the sorted array, and the "
             "total number of **shifts** performed (each `a[j + 1] = a[j];` counts as "
             "one). An already-sorted array should report `0`. Write the whole block "
             "where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int shifts = 0;\n"
                   "        for (int i = 1; i < n; i++) {\n"
                   "            int key = a[i];\n"
                   "            int j = i - 1;\n"
                   "            while (j >= 0 && a[j] > key) {\n"
                   "                a[j + 1] = a[j];\n"
                   "                j--;\n"
                   "                shifts++;\n"
                   "            }\n"
                   "            a[j + 1] = key;\n"
                   "        }\n"
                   "        System.out.println(Arrays.toString(a));\n"
                   "        System.out.println(shifts);"),
             "        int shifts = 0;\n"
             "        for (int i = 1; i < n; i++) {\n"
             "            int key = a[i];\n"
             "            int j = i - 1;\n"
             "            while (j >= 0 && a[j] > key) {\n"
             "                a[j + 1] = a[j];\n"
             "                j--;\n"
             "                shifts++;\n"
             "            }\n"
             "            a[j + 1] = key;\n"
             "        }\n"
             "        System.out.println(Arrays.toString(a));\n"
             "        System.out.println(shifts);",
             [_acase(a, _insertion_shifts(a))
              for a in ([5, 2, 4, 6, 1], [1, 2, 3, 4], [4, 3, 2, 1], [7], [2, 1])],
             hints=["Declare the counter before the outer loop so it survives every round.",
                    "Increment it inside the `while`, next to the shift.",
                    "Dropping `key` into the gap is not a shift — do not count it.",
                    "Reversed input of length n does n(n-1)/2 shifts; sorted input does 0."]),
    ],
    quiz=[
        _jq("Why does insertion sort shift rather than swap?",
            ["`key` is already saved, so each element needs only one write instead of three",
             "Swapping would break stability",
             "Shifting is required to keep it in place",
             "There is no difference"],
            0,
            "A swap is three assignments; a shift is one. Lifting `key` out first frees the "
            "slot, so the whole run of bigger elements moves with one write each."),
        _jq("Java's own `Arrays.sort` falls back to insertion sort for small ranges. Why?",
            ["Its constant factor is tiny and its best case is O(n), so it wins below ~40 elements",
             "Because it is the only stable sort",
             "Because quicksort cannot sort fewer than 40 elements",
             "To save memory"],
            0,
            "Asymptotics only decide large inputs. For a short, nearly-sorted range, "
            "insertion sort's simple loop beats the bookkeeping of a divide-and-conquer sort."),
    ],
))

# --- 3.5 Comparing them -----------------------------------------------------

_M3.append(_jlesson(
    "m3-compare", "Choosing between them",
    "Complexity, stability, and the answers an interviewer is listening for.",
    """
| | Best | Average | Worst | Swaps/writes | Stable | Extra space |
|---|---|---|---|---|---|---|
| **Bubble** (with flag) | O(n) | O(n²) | O(n²) | O(n²) | ✅ | O(1) |
| **Selection** | O(n²) | O(n²) | O(n²) | **O(n)** | ❌ | O(1) |
| **Insertion** | **O(n)** | O(n²) | O(n²) | O(n²) writes | ✅ | O(1) |
| `Arrays.sort` (primitives) | O(n log n) | O(n log n) | O(n log n)* | — | ❌ | O(log n) |

\\* Dual-pivot quicksort is O(n²) in adversarial theory; Java's implementation
detects the pathological case and falls back.

**"Stable" means equal elements keep their original relative order.** It sounds
academic until you sort a table twice: sort by name, then by department, and a
stable sort leaves each department's names still alphabetical. An unstable sort
scrambles them, and you have to sort by a composite key instead.

Bubble and insertion are stable because they only ever move an element past a
**strictly** greater one. Selection is unstable because its long-range swap can
throw an element clean past its equal twin.

**In place** means O(1) extra memory — all three of these qualify. Merge sort
does not; it needs a second array.

**The comparison count for all three worst cases is the same** — n(n-1)/2,
about n²/2. On a 10,000-element array that is 50 million comparisons versus
about 130,000 for an O(n log n) sort. The gap is not a detail.

**How to answer "which sort would you use?"** — "`Arrays.sort`, which is
dual-pivot quicksort for primitives and a stable TimSort for objects. If I had
to hand-write one, insertion sort: it is stable, in place, and O(n) on nearly
sorted data. I would only hand-write a sort at all if I needed a property the
library does not give me."

**Detecting "already sorted" is O(n)** and worth knowing on its own — it is the
best case of bubble and insertion sort in one line, and it is the check that
lets you skip work entirely:

```java
boolean sorted = true;
for (int i = 0; i + 1 < n; i++) if (a[i] > a[i + 1]) sorted = false;
```
""",
    warmup=[
        _jq("You sort employees by name, then by department. Which sort keeps each department alphabetical?",
            ["A stable sort — it preserves the relative order of equal keys",
             "Any sort, as long as it is O(n log n)",
             "Selection sort",
             "None; you must sort by a combined key"],
            0,
            "That is exactly what stability buys you, and it is why `Arrays.sort` uses a "
            "stable TimSort for object arrays."),
        _jq("Which of the three hand-written sorts has the best *best* case?",
            ["Insertion sort — O(n) on sorted input",
             "Selection sort — O(n) because it swaps least",
             "Bubble sort without the flag",
             "They all have the same best case"],
            0,
            "Insertion sort's inner `while` fails immediately on sorted data. Selection sort "
            "has no early exit at all — it is O(n²) even on perfect input."),
    ],
    exercises=[
        _je("j3-cmp-sorted", "Is it already sorted?",
            "Print `true` when the array is in non-decreasing order, otherwise "
            "`false`. Replace `____` with the check inside the loop.",
            _jscan(
                _RD_ARR
                + "        boolean sorted = true;\n"
                  "        for (int i = 0; i + 1 < n; i++) {\n"
                  "            if (a[i] > a[i + 1]) sorted = false;\n"
                  "        }\n"
                  "        System.out.println(sorted);"),
            "if (a[i] > a[i + 1]) sorted = false;",
            [_acase(a, _jbool(_is_sorted(a)))
             for a in ([1, 2, 3], [1, 3, 2], [2, 2, 2], [5], [3, 2, 1])],
            hints=["Sorted means every element is <= the one after it.",
                   "So a *violation* is a strictly greater neighbour.",
                   "`if (a[i] > a[i + 1]) sorted = false;` — note `>`, not `>=`, so equal "
                   "neighbours are fine."],
            difficulty="Intro"),

        _je("j3-cmp-comparisons", "Count the comparisons",
            "Bubble sort without the early exit always performs the same number of "
            "comparisons, whatever the data. Sort the array, then print that count "
            "on a second line. Replace `____` with the counter increment.",
            _jscan(
                _RD_ARR
                + "        int comps = 0;\n"
                  "        for (int pass = 0; pass < n - 1; pass++) {\n"
                  "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                  "                comps++;\n"
                  "                if (a[i] > a[i + 1]) {\n"
                  "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
                  "                }\n"
                  "            }\n"
                  "        }\n"
                  "        System.out.println(Arrays.toString(a));\n"
                  "        System.out.println(comps);"),
            "                comps++;",
            [_acase(a, _nl(_jarr(sorted(a)), len(a) * (len(a) - 1) // 2))
             for a in ([5, 1, 4, 2], [1, 2, 3], [4, 3, 2, 1], [6])],
            hints=["A comparison happens once per inner-loop iteration.",
                   "Count it before the `if`, so it counts even when no swap follows.",
                   "`comps++;` — and notice the total is always n(n-1)/2, whatever the input."]),

        _jch("j3-cmp-swaps", "Count the inversions", "Medium",
             "Sort with bubble sort and print two lines: the sorted array, then the "
             "number of **swaps** performed. That number is the array's *inversion "
             "count* — how many pairs were in the wrong order to begin with — so it "
             "is 0 for sorted input and n(n-1)/2 for reversed input. Write the whole "
             "block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int swaps = 0;\n"
                   "        for (int pass = 0; pass < n - 1; pass++) {\n"
                   "            for (int i = 0; i < n - 1 - pass; i++) {\n"
                   "                if (a[i] > a[i + 1]) {\n"
                   "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
                   "                    swaps++;\n"
                   "                }\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(Arrays.toString(a));\n"
                   "        System.out.println(swaps);"),
             "        int swaps = 0;\n"
             "        for (int pass = 0; pass < n - 1; pass++) {\n"
             "            for (int i = 0; i < n - 1 - pass; i++) {\n"
             "                if (a[i] > a[i + 1]) {\n"
             "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
             "                    swaps++;\n"
             "                }\n"
             "            }\n"
             "        }\n"
             "        System.out.println(Arrays.toString(a));\n"
             "        System.out.println(swaps);",
             [_acase(a, _nl(_jarr(sorted(a)), _bubble_swaps(a)))
              for a in ([5, 1, 4, 2], [1, 2, 3, 4], [4, 3, 2, 1], [2, 1], [9])],
             hints=["The counter goes outside both loops; the increment goes inside the `if`.",
                    "Only count when the swap actually happens.",
                    "Sanity check: reversed input of length 4 gives 6 — every one of the "
                    "4×3/2 pairs was inverted."]),
    ],
    quiz=[
        _jq("All three hand-written sorts are O(n²) on average. Why prefer insertion sort?",
            ["It is stable, in place, and O(n) on nearly-sorted data with a small constant",
             "Because it does the fewest swaps",
             "Because it is the only one that works on negative numbers",
             "Because it is O(n log n) in practice"],
            0,
            "Selection sort does fewest *writes* but has no good case. Insertion sort is the "
            "one real libraries actually keep, as the small-range fallback inside quicksort."),
        _jq("An O(n²) sort on 10,000 elements does ~50 million comparisons. An O(n log n) sort does…",
            ["~130,000", "~50 million as well", "~10,000", "~1 million"],
            0,
            "10,000 × log₂(10,000) ≈ 10,000 × 13.3 ≈ 133,000 — several hundred times less "
            "work. That ratio grows with n."),
    ],
))

# --- 3.6 The library versions ----------------------------------------------

_M3.append(_jlesson(
    "m3-library", "`Arrays.sort` and `Arrays.binarySearch`",
    "What you would actually ship — and the return value that surprises everyone.",
    """
Now that you can write them, use the library.

```java
Arrays.sort(a);                       // ascending, in place, whole array
Arrays.sort(a, from, to);             // just that range — half-open, as always
int i = Arrays.binarySearch(a, 42);   // REQUIRES a sorted array
```

**`Arrays.sort` on primitives is a dual-pivot quicksort** — O(n log n), in
place, and *not* stable. Stability is meaningless for `int`s (two 5s are
indistinguishable), which is exactly why they can use the faster unstable
algorithm. For object arrays Java uses **TimSort**, which *is* stable, because
there two equal-comparing objects can still be different objects.

**There is no `Arrays.sort(a, reverse)` for primitives.** No comparator can be
supplied for an `int[]`. To sort descending you either sort ascending and then
reverse (module 4), or sort an `Integer[]` with a comparator (Part 6 of the
roadmap). Being able to say *why* — comparators need objects, and `int` is not
one — is a common interview follow-up.

**`Arrays.binarySearch`'s return value is the sharp edge.** Found: the index.
Not found: **`-(insertion point) - 1`** — a negative number encoding where the
value *would* go.

```java
int[] a = {10, 20, 30};
Arrays.binarySearch(a, 20);   //  1
Arrays.binarySearch(a, 25);   // -3   because it belongs at index 2: -(2) - 1
Arrays.binarySearch(a, 5);    // -1   belongs at index 0: -(0) - 1
```

Why not plain `-1`? Because "not found, and here is where to insert it" is
strictly more information, and the negative encoding fits it in one `int`. To
recover the insertion point: `int ip = -result - 1;`. To just test presence:
`if (result >= 0)`.

**On an unsorted array the result is meaningless** — not an exception, just a
wrong answer. Same trap as your hand-written version, and the reason
`Arrays.sort` and `Arrays.binarySearch` almost always appear together.
""",
    warmup=[
        _jq("`int[] a = {10, 20, 30}; System.out.println(Arrays.binarySearch(a, 25));`",
            ["-3", "-1", "2", "It throws"],
            0,
            "Not found, and 25 would be inserted at index 2, so the result is -(2) - 1 = -3. "
            "Recover the insertion point with `-result - 1`."),
        _jq("Why does Java use an unstable sort for `int[]` but a stable one for `Object[]`?",
            ["Two equal ints are indistinguishable, so stability buys nothing and costs speed",
             "Because `int[]` cannot be sorted stably",
             "Because object sorts are always slower anyway",
             "It uses the same algorithm for both"],
            0,
            "Stability only matters when equal-comparing elements carry other differences. "
            "Primitives carry none, so the faster unstable quicksort is free."),
    ],
    exercises=[
        _je("j3-lib-sort", "Let the library do it",
            "Sort the array ascending and print it — with one call, not a loop. "
            "Replace `____`.",
            _jscan(_RD_ARR
                   + "        Arrays.sort(a);\n"
                     "        System.out.println(Arrays.toString(a));"),
            "Arrays.sort(a);",
            [_acase(a, _jarr(sorted(a)))
             for a in ([5, 1, 4, 2], [3, 3, 1], [9], [-2, 7, -8])],
            hints=["It lives on `Arrays` and sorts in place.",
                   "It returns nothing — the array itself changes.",
                   "`Arrays.sort(a);`"],
            difficulty="Intro"),

        _je("j3-lib-search", "The library's binary search",
            "Sort the array, then print `Arrays.binarySearch(a, target)` **exactly as "
            "it comes back** — including the negative encoding when the value is "
            "missing. Replace `____` with the call.",
            _jscan(
                _RD_ARR
                + "        int target = sc.nextInt();\n"
                  "        Arrays.sort(a);\n"
                  "        System.out.println(Arrays.binarySearch(a, target));"),
            "Arrays.binarySearch(a, target)",
            [_akcase(a, t, _java_bsearch(sorted(a), t))
             for (a, t) in (([30, 10, 20], 20), ([30, 10, 20], 25),
                            ([30, 10, 20], 5), ([30, 10, 20], 40), ([7], 7))],
            hints=["Two arguments: the sorted array and the value.",
                   "Do not try to normalise the result to -1 — print what it returns.",
                   "`Arrays.binarySearch(a, target)`"]),

        _je("j3-lib-range", "Sort part of it",
            "Sort only the range from index `from` up to (but not including) `to`, "
            "leaving the rest alone, then print the whole array. Replace `____`.",
            _jscan(
                _RD_ARR
                + "        int from = sc.nextInt();\n"
                  "        int to = sc.nextInt();\n"
                  "        Arrays.sort(a, from, to);\n"
                  "        System.out.println(Arrays.toString(a));"),
            "Arrays.sort(a, from, to);",
            [_case(f"{len(a)}\n{_sp(a)}\n{f_}\n{t}",
                   _jarr(a[:f_] + sorted(a[f_:t]) + a[t:]))
             for (a, f_, t) in (([5, 3, 1, 4, 2], 1, 4),
                                ([5, 3, 1, 4, 2], 0, 5),
                                ([9, 8, 7], 0, 2))],
            hints=["The three-argument overload takes the array and the two bounds.",
                   "Half-open, like every range in Java: `to` is excluded.",
                   "`Arrays.sort(a, from, to);`"]),

        _jch("j3-lib-kth", "The k-th smallest", "Easy",
             "Read the array and then `k` (0-based). Print the k-th smallest element "
             "— sort first, then index. Write the whole block where you see `____`.",
             _jscan(
                 _RD_ARR
                 + "        int k = sc.nextInt();\n"
                   "        Arrays.sort(a);\n"
                   "        System.out.println(a[k]);"),
             "        Arrays.sort(a);\n"
             "        System.out.println(a[k]);",
             [_akcase(a, k, sorted(a)[k])
              for (a, k) in (([5, 1, 4, 2], 0), ([5, 1, 4, 2], 3),
                             ([5, 1, 4, 2], 2), ([7], 0), ([3, 3, 1], 1))],
             hints=["Two lines: sort, then index.",
                    "k is 0-based, so k = 0 is the smallest.",
                    "Sorting to answer one query is O(n log n); a selection algorithm could "
                    "do it in O(n), which is the follow-up an interviewer will ask for."]),
    ],
    quiz=[
        _jq("`Arrays.binarySearch` on an UNSORTED array does what?",
            ["Returns a meaningless value — no exception, just a wrong answer",
             "Throws IllegalArgumentException",
             "Sorts the array first, then searches",
             "Falls back to a linear scan"],
            0,
            "The precondition is unchecked, because checking it would cost O(n) and defeat "
            "the point. Sorting first is your responsibility."),
        _jq("You need `int[]` sorted descending. What is the honest approach?",
            ["Sort ascending, then reverse it in place",
             "Arrays.sort(a, Collections.reverseOrder())",
             "Arrays.sort(a, false)",
             "Arrays.sortDescending(a)"],
            0,
            "Comparators only work on object arrays, and `int` is not an object. Sorting "
            "ascending and reversing is O(n log n + n) — module 4 writes the reversal."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m3_report(a, target):
    s = sorted(a)
    return _nl(
        f"sorted={_jarr(s)}",
        f"swaps={_bubble_swaps(a)}",
        f"index={_bsearch(s, target)}",
        f"less={_lower_bound(s, target)}",
    )


_M3_CAP = _jcap(
    "Sort, then search",
    """
The two halves of this module, wired together — which is how they always appear
in real code: you sort so that you can binary search.

Read the array, then a `target`. Print four lines:

```
sorted=<the sorted array, in Arrays.toString form>
swaps=<how many swaps your bubble sort performed>
index=<the target's index after sorting, or -1>
less=<how many elements are strictly less than target>
```

Rules:

- **Sort it yourself** with bubble sort, counting swaps as you go. `Arrays.sort`
  would not give you the swap count, and the count is the point.
- **`index` uses your own binary search**, not `Arrays.binarySearch` — so a
  miss is plain `-1`, not the negative encoding. All the test arrays are
  duplicate-free, so the index is unambiguous.
- **`less` is a lower bound**: the number of elements strictly below `target`.
  Do it with the half-open binary search from lesson 3.1 rather than a scan.

Sanity check on the sample below: `{5, 1, 4, 2}` needs 4 swaps to sort, `4`
lands at index 2 once sorted, and 2 elements (1 and 2) are below it.
""",
    _jch("j3-cap-sortsearch", "Sort, then search", "Hard",
         "Write the whole program where you see `____` — bubble sort with a swap "
         "counter, then two binary searches over the sorted array.",
         _jscan(
             _RD_ARR
             + "        int target = sc.nextInt();\n"
               "        int swaps = 0;\n"
               "        for (int pass = 0; pass < n - 1; pass++) {\n"
               "            for (int i = 0; i < n - 1 - pass; i++) {\n"
               "                if (a[i] > a[i + 1]) {\n"
               "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
               "                    swaps++;\n"
               "                }\n"
               "            }\n"
               "        }\n"
               '        System.out.println("sorted=" + Arrays.toString(a));\n'
               '        System.out.println("swaps=" + swaps);\n'
               "        int lo = 0;\n"
               "        int hi = n - 1;\n"
               "        int idx = -1;\n"
               "        while (lo <= hi) {\n"
               "            int mid = lo + (hi - lo) / 2;\n"
               "            if (a[mid] == target) { idx = mid; break; }\n"
               "            else if (a[mid] < target) lo = mid + 1;\n"
               "            else hi = mid - 1;\n"
               "        }\n"
               '        System.out.println("index=" + idx);\n'
               "        int lb = 0;\n"
               "        int ub = n;\n"
               "        while (lb < ub) {\n"
               "            int mid = lb + (ub - lb) / 2;\n"
               "            if (a[mid] < target) lb = mid + 1;\n"
               "            else ub = mid;\n"
               "        }\n"
               '        System.out.println("less=" + lb);'),
         "        int swaps = 0;\n"
         "        for (int pass = 0; pass < n - 1; pass++) {\n"
         "            for (int i = 0; i < n - 1 - pass; i++) {\n"
         "                if (a[i] > a[i + 1]) {\n"
         "                    int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;\n"
         "                    swaps++;\n"
         "                }\n"
         "            }\n"
         "        }\n"
         '        System.out.println("sorted=" + Arrays.toString(a));\n'
         '        System.out.println("swaps=" + swaps);\n'
         "        int lo = 0;\n"
         "        int hi = n - 1;\n"
         "        int idx = -1;\n"
         "        while (lo <= hi) {\n"
         "            int mid = lo + (hi - lo) / 2;\n"
         "            if (a[mid] == target) { idx = mid; break; }\n"
         "            else if (a[mid] < target) lo = mid + 1;\n"
         "            else hi = mid - 1;\n"
         "        }\n"
         '        System.out.println("index=" + idx);\n'
         "        int lb = 0;\n"
         "        int ub = n;\n"
         "        while (lb < ub) {\n"
         "            int mid = lb + (ub - lb) / 2;\n"
         "            if (a[mid] < target) lb = mid + 1;\n"
         "            else ub = mid;\n"
         "        }\n"
         '        System.out.println("less=" + lb);',
         [_akcase(a, t, _m3_report(a, t))
          for (a, t) in (([5, 1, 4, 2], 4), ([5, 1, 4, 2], 3), ([1, 2, 3, 4], 1),
                         ([9, 7, 5, 3, 1], 5), ([8], 8), ([8], 2))],
         hints=["Do it in four stages and print each line as soon as you have it.",
                "The swap counter is declared before both sorting loops.",
                "The first search is the `lo <= hi` form with an early exit; it reports -1 "
                "when the target is absent.",
                "The second is the half-open `lo < hi` form with `hi = n` and no early exit; "
                "its answer is `lo` when the loop ends.",
                "The two searches use different loop conditions on purpose — do not try to "
                "share one loop between them."]),
    example_io="stdin:  4\n        5 1 4 2\n        4\n\n"
               "stdout: sorted=[1, 2, 4, 5]\n        swaps=4\n        index=2\n        less=2",
    rubric=[
        "The sort is hand-written bubble sort with a working swap count, not `Arrays.sort`.",
        "The swap counter increments inside the `if`, so sorted input reports 0.",
        "The exact search uses `lo <= hi` and reports plain `-1` on a miss.",
        "The lower-bound search uses `hi = n`, `lo < hi`, and `hi = mid` — not `mid - 1`.",
        "Both searches compute `mid` in the overflow-safe form.",
        "It survives a one-element array and a target that is absent at either end.",
    ],
)


_MODULES.append(_jmod(
    3, 1, "Arrays, deeply",
    "Searching and sorting by hand",
    "Write binary search and all three elementary sorts from memory, know exactly "
    "what each costs and whether it is stable, and then know when to throw them away "
    "and call `Arrays.sort`.",
    """
This is the first module where the algorithm, not the syntax, is the difficulty.
Everything here is written longhand before the library equivalent is even
mentioned — because "I'd call `Arrays.sort`" is the right answer in production
and the wrong answer in an interview, and because you cannot debug a sort you
have never taken apart.

Every one of these five algorithms is built from module 1's moves: a swap, an
argmin, a running comparison. What is new is the **loop invariant** — the
sentence that says what is true after each pass — and the discipline of getting
the boundaries exactly right.
""",
    _M3,
    capstone=_M3_CAP,
    objectives=[
        "Write binary search from memory with `lo <= hi`, an overflow-safe midpoint, and `mid ± 1`.",
        "Write the half-open lower-bound search and explain why its loop condition differs.",
        "Write bubble, selection and insertion sort from memory, including bubble's early exit.",
        "State each sort's best/average/worst cost, its swap count, and whether it is stable.",
        "Explain why `j >= 0` has to come first in insertion sort's `while`.",
        "Use `Arrays.sort` and `Arrays.binarySearch`, and decode the negative not-found value.",
    ],
    why="Sorting and searching are the two things every interview reaches for, and the "
        "two places boundary bugs hide best. They are also the foundation of module 4 "
        "(rotation, duplicates) and module 5 (two pointers), both of which assume "
        "sorted data.",
    est_minutes=330,
    glossary=[
        _jg("precondition", "Something that must already be true for an algorithm to be "
                            "correct. Binary search's is 'the array is sorted'."),
        _jg("loop invariant", "A statement true before and after every pass. Bubble sort's: "
                              "'the last `pass` elements are final'."),
        _jg("O(log n)", "Cost that grows by one step each time the input doubles. Binary "
                        "search over a billion elements is about 30 comparisons."),
        _jg("stable sort", "One that never changes the relative order of equal-comparing "
                           "elements. Bubble and insertion are; selection is not."),
        _jg("in place", "Uses O(1) extra memory. All three hand-written sorts qualify; merge "
                        "sort does not."),
        _jg("inversion", "A pair of positions that are out of order. Bubble sort's swap count "
                         "is exactly the number of inversions."),
        _jg("lower bound", "The first index whose value is `>= target` — equivalently, the "
                           "count of values strictly less than it."),
        _jg("insertion point", "Where a missing value would go to keep the array sorted. "
                               "`Arrays.binarySearch` returns `-(insertion point) - 1`."),
        _jg("short-circuit evaluation", "`&&` stops as soon as the left side is false, which "
                                        "is what makes `j >= 0 && a[j] > key` safe."),
        _jg("dual-pivot quicksort", "The O(n log n), unstable, in-place algorithm "
                                    "`Arrays.sort` uses for primitive arrays."),
    ],
    cheatsheet="""
```java
// --- binary search: exact match ----------------------------------------
int lo = 0, hi = n - 1, idx = -1;
while (lo <= hi) {                        // <= : the last candidate counts
    int mid = lo + (hi - lo) / 2;         // overflow-safe midpoint
    if (a[mid] == target) { idx = mid; break; }
    else if (a[mid] < target) lo = mid + 1;
    else hi = mid - 1;                    // mid ± 1, or it never terminates
}

// --- binary search: lower bound / insertion point ----------------------
int lo = 0, hi = n;                       // hi is EXCLUSIVE
while (lo < hi) {                          // strict <
    int mid = lo + (hi - lo) / 2;
    if (a[mid] < target) lo = mid + 1;
    else hi = mid;                         // keep mid — it may be the answer
}
// lo == insertion point == count of values < target

// --- bubble sort (stable, best O(n) with the flag) ---------------------
for (int pass = 0; pass < n - 1; pass++) {
    boolean swapped = false;
    for (int i = 0; i < n - 1 - pass; i++)        // tail is already final
        if (a[i] > a[i + 1]) {
            int t = a[i]; a[i] = a[i + 1]; a[i + 1] = t;
            swapped = true;
        }
    if (!swapped) break;
}

// --- selection sort (unstable, exactly n-1 swaps) ----------------------
for (int i = 0; i < n - 1; i++) {
    int min = i;                                   // seed with i, NOT 0
    for (int j = i + 1; j < n; j++) if (a[j] < a[min]) min = j;
    int t = a[i]; a[i] = a[min]; a[min] = t;
}

// --- insertion sort (stable, best O(n), shifts not swaps) --------------
for (int i = 1; i < n; i++) {
    int key = a[i];
    int j = i - 1;
    while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }   // guard FIRST
    a[j + 1] = key;
}

// --- the library --------------------------------------------------------
Arrays.sort(a);                 // dual-pivot quicksort, O(n log n), unstable
Arrays.sort(a, from, to);       // half-open range
Arrays.binarySearch(a, x);      // index, or -(insertion point) - 1
int ip = -result - 1;           // recover the insertion point
```
""",
    self_check=[
        "Can you write binary search from a blank editor and get `<=`, `mid ± 1` and the midpoint right first try?",
        "Can you say what breaks if binary search uses `lo < hi`, and give an input that shows it?",
        "Can you write all three sorts from memory without looking back at the lesson?",
        "Can you state, for each sort, its best case, its swap count, and whether it is stable?",
        "Can you explain the `{2a, 2b, 1}` trace that proves selection sort is unstable?",
        "Do you know why insertion sort's `while` puts `j >= 0` on the left?",
        "Can you decode `-3` from `Arrays.binarySearch` back into an insertion point?",
    ],
    review=[
        _jq("Binary search with `mid = (lo + hi) / 2` on a 3-billion-element array…",
            ["can overflow int, producing a negative index and an exception",
             "is fine — Java promotes to long automatically",
             "is slower but correct",
             "throws OutOfMemoryError first, so it never matters"],
            0,
            "`lo + hi` exceeds `Integer.MAX_VALUE` and wraps negative. This exact bug lived "
            "in the JDK for nine years."),
        _jq("Which sort would you hand-write for an array of 20 nearly-sorted values?",
            ["Insertion sort — near O(n) on nearly-sorted data, stable, tiny constant",
             "Selection sort — fewest swaps",
             "Bubble sort — simplest to write",
             "None; always call Arrays.sort"],
            0,
            "This is exactly the case Java's own library falls back to insertion sort for. "
            "(In real code you would of course still call `Arrays.sort`.)"),
        _jq("`Arrays.binarySearch(a, x)` returns `-1`. What do you know?",
            ["x is absent and belongs at index 0 — it is smaller than everything",
             "x is at index 1",
             "x is absent and belongs at the end",
             "The array was not sorted"],
            0,
            "-(insertion point) - 1 = -1 means insertion point 0. A plain 'not found' would "
            "have been indistinguishable from index 0, which is why the encoding exists."),
        _jq("Bubble sort reports 0 swaps. What does that tell you about the input?",
            ["It was already sorted", "It was reversed", "It had duplicates",
             "Nothing — the count is independent of the input"],
            0,
            "The swap count equals the inversion count, so zero swaps means zero pairs out "
            "of order. With the `swapped` flag, that input costs a single O(n) pass."),
    ],
    milestone="You can write binary search and three sorts from memory, defend each one's "
              "cost and stability, and explain to an interviewer why you would still call "
              "`Arrays.sort` in production.",
))
