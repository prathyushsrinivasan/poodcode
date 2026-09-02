# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 3 practice - searching and sorting by hand.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[3]`.
#
# Module 3 scope: binary search, bubble/selection/insertion sort, stability and
# pass counts, and (newly allowed at this module) Arrays.sort and
# Arrays.binarySearch. Still no String methods, no StringBuilder, no helper
# methods beside main, no recursion.
#
# The trace variants below print the array after each pass, so their Python
# mirrors must reproduce the EXACT algorithm the hints describe - a different
# but equally correct bubble sort would produce different intermediate lines.
# ---------------------------------------------------------------------------


def _p3ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_ARR):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


# Unsorted inputs used across the sorting families.
_S_ARR = ([5, 2, 9, 1], [3], [4, 3, 2, 1], [1, 2, 3, 4], [2, 1, 2, 1, 2])

# Sorted inputs for the binary-search family (the precondition is the point).
_B_ARR = ([1, 3, 5, 7, 9], [42], [-5, -2, 0, 4], [2, 2, 2, 2], [1, 2, 3, 4, 5, 6])


# --- Family A - binary search -----------------------------------------------

def _bin_steps(a, k):
    """Iterations of the standard half-open-free lo/hi binary search below."""
    lo, hi, steps = 0, len(a) - 1, 0
    while lo <= hi:
        steps += 1
        mid = lo + (hi - lo) // 2
        if a[mid] == k:
            return steps
        if a[mid] < k:
            lo = mid + 1
        else:
            hi = mid - 1
    return steps


def _bin_find(a, k):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if a[mid] == k:
            return mid
        if a[mid] < k:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


_P3_A = _jfam(
    "p3-binary", "Binary search, five ways",
    "Halve the range until it is empty.",
    """
Binary search is the payoff for having sorted data, and it is asked about
constantly — usually with one of its three classic bugs.

```java
int lo = 0, hi = n - 1;
while (lo <= hi) {                       // <=, not <
    int mid = lo + (hi - lo) / 2;        // not (lo + hi) / 2
    if (a[mid] == k) { found = mid; break; }
    if (a[mid] < k) lo = mid + 1;        // + 1 / - 1, not mid
    else            hi = mid - 1;
}
```

**The three bugs, all of which the cases below catch:**

1. **`while (lo < hi)`** never examines the final one-element range, so a target
   sitting at the very edge is missed. It must be `<=`.
2. **`(lo + hi) / 2`** can overflow `int` for large indices. `lo + (hi - lo) / 2`
   is arithmetically identical and cannot. It costs nothing, so always write it.
3. **`lo = mid`** instead of `lo = mid + 1` loops forever once the range is two
   wide, because `mid` keeps landing on `lo`. Every branch must *shrink* the
   range, and `mid` has already been tested — so exclude it.

**The precondition is not optional.** Binary search on unsorted data does not
"mostly work"; it returns nonsense. Every array in this family arrives already
sorted, which is exactly why family E ends by sorting first.

The last two variants ask for **lower bound** and **upper bound** — where a
value *would* go rather than where it is. That generalisation is what real APIs
give you (`Arrays.binarySearch` returns `-(insertionPoint) - 1` on a miss for
precisely this reason), and it handles duplicates, which plain equality search
does not.
""",
    [
        _p3ex("j3-pr-bin-find", "Find it, or say -1", "Easy",
              "The array is already sorted ascending. Read it, then a target `k`. Print "
              "the index where `k` sits, or `-1` if it is absent.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n - 1;
        int found = -1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] == k) {
                found = mid;
                break;
            }
            if (a[mid] < k) {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        System.out.println(found);
""",
              [_akcase(a, k, _bin_find(a, k))
               for (a, k) in (([1, 3, 5, 7, 9], 7), ([1, 3, 5, 7, 9], 1),
                              ([1, 3, 5, 7, 9], 9), ([1, 3, 5, 7, 9], 4), ([42], 42))],
              ["`hi` starts at the last index, `n - 1`, not at `n`.",
               "The loop condition is `lo <= hi`. With `<` the last single-element "
               "range is never examined, and cases two and three sit at the edges.",
               "Compute the midpoint as `lo + (hi - lo) / 2` — overflow-proof, and "
               "the same number as `(lo + hi) / 2`.",
               "`mid` has already been compared, so exclude it: `lo = mid + 1` or "
               "`hi = mid - 1`. Assigning `mid` itself loops forever.",
               "Case four searches for a value that is not present and wants `-1`."]),

        _p3ex("j3-pr-bin-steps", "How many probes did it take?", "Medium",
              "Same sorted array and target `k`. Print how many times the loop body "
              "ran — that is, how many midpoints were examined — whether or not `k` was "
              "found.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n - 1;
        int steps = 0;
        while (lo <= hi) {
            steps++;
            int mid = lo + (hi - lo) / 2;
            if (a[mid] == k) {
                break;
            }
            if (a[mid] < k) {
                lo = mid + 1;
            } else {
                hi = mid - 1;
            }
        }
        System.out.println(steps);
""",
              [_akcase(a, k, _bin_steps(a, k))
               for (a, k) in (([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 1),
                              ([1, 3, 5, 7, 9], 4), ([42], 99),
                              ([1, 2, 3, 4, 5, 6], 6))],
              ["Same search, with a counter.",
               "Increment at the TOP of the loop body, before testing — every entry "
               "into the body is one probe.",
               "Do not increment after the `break`, or a hit is undercounted.",
               "Case one finds the target on the very first probe, so the answer "
               "is `1`.",
               "A miss keeps halving until the range is empty — that is the "
               "log2(n)-ish worst case this variant is here to make visible."]),

        _p3ex("j3-pr-lower-bound", "Where would it go?", "Medium",
              "Same sorted array and `k`. Print the **first** index whose value is "
              "greater than or equal to `k`. If every value is smaller, print `n`.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] < k) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        System.out.println(lo);
""",
              [_akcase(a, k, sum(1 for x in a if x < k))
               for (a, k) in (([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 4),
                              ([1, 3, 5, 7, 9], 10), ([2, 2, 2, 2], 2),
                              ([1, 3, 5, 7, 9], 0))],
              ["This one is NOT the equality search with a tweak — the range is "
               "half-open. Start `hi` at `n`, not `n - 1`.",
               "The condition becomes `lo < hi`, and the answer is `lo` when the "
               "loop ends.",
               "There is no `== k` branch at all. Only two cases: `a[mid] < k` moves "
               "`lo` past mid, anything else keeps mid as a candidate with `hi = mid`.",
               "`hi = mid`, NOT `mid - 1` — mid might be the answer, so it must stay "
               "in the range.",
               "With duplicates it lands on the FIRST of them: case four wants `0`.",
               "If everything is smaller, `lo` walks all the way to `n`, which is the "
               "answer case three wants."]),

        _p3ex("j3-pr-upper-bound", "Just past the last one", "Medium",
              "Same sorted array and `k`. Print the first index whose value is "
              "**strictly greater** than `k` — one past the last occurrence of `k`. "
              "If no value exceeds `k`, print `n`.",
              """
        int k = sc.nextInt();
        int lo = 0;
        int hi = n;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] <= k) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        System.out.println(lo);
""",
              [_akcase(a, k, sum(1 for x in a if x <= k))
               for (a, k) in (([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 4),
                              ([1, 3, 5, 7, 9], 9), ([2, 2, 2, 2], 2),
                              ([1, 3, 5, 7, 9], 0))],
              ["Identical to lower bound except for one character in the comparison.",
               "Lower bound pushes `lo` past everything `< k`; upper bound pushes it "
               "past everything `<= k`.",
               "So the test becomes `a[mid] <= k`.",
               "With duplicates it lands one PAST the last of them: case four wants "
               "`4`, where lower bound wanted `0`.",
               "The difference between the two answers is exactly how many times `k` "
               "occurs — which is how you count occurrences in O(log n)."]),

        _p3ex("j3-pr-lib-search", "What the library returns", "Easy",
              "Same sorted array and `k`. Call `Arrays.binarySearch(a, k)` and print its "
              "raw return value — including the negative number it gives on a miss.",
              """
        int k = sc.nextInt();
        System.out.println(Arrays.binarySearch(a, k));
""",
              [_akcase(a, k, (a.index(k) if k in a
                              else -(sum(1 for x in a if x < k)) - 1))
               for (a, k) in (([1, 3, 5, 7, 9], 7), ([1, 3, 5, 7, 9], 4),
                              ([1, 3, 5, 7, 9], 0), ([1, 3, 5, 7, 9], 10),
                              ([42], 42))],
              ["One line — do not reimplement the search.",
               "On a hit it returns the index, like your own version.",
               "On a MISS it does not return `-1`. It returns "
               "`-(insertion point) - 1`.",
               "The insertion point is the lower bound you just wrote. For `4` in "
               "`1 3 5 7 9` that is index 2, so the answer is `-3`.",
               "The `-1` offset exists so that a miss at index 0 is `-1` rather than "
               "`-0`, which would be indistinguishable from a hit.",
               "The array must be sorted or the result is undefined — it is here."]),
    ])


# --- Family B - bubble sort -------------------------------------------------

def _bubble_pass(a):
    """One pass of bubble sort over the whole array."""
    b = list(a)
    for i in range(len(b) - 1):
        if b[i] > b[i + 1]:
            b[i], b[i + 1] = b[i + 1], b[i]
    return b


def _bubble_full(a, desc=False):
    b = list(a)
    n = len(b)
    for p in range(n - 1):
        for i in range(n - 1 - p):
            worse = b[i] < b[i + 1] if desc else b[i] > b[i + 1]
            if worse:
                b[i], b[i + 1] = b[i + 1], b[i]
    return b


def _bubble_trace(a):
    """The array after each of the n-1 passes, shrinking bound, no early exit."""
    b = list(a)
    n = len(b)
    out = []
    for p in range(n - 1):
        for i in range(n - 1 - p):
            if b[i] > b[i + 1]:
                b[i], b[i + 1] = b[i + 1], b[i]
        out.append(_jarr(b))
    return out


def _bubble_passes(a):
    """Passes performed with an early exit, counting the final no-swap pass."""
    b = list(a)
    n = len(b)
    passes = 0
    for p in range(n - 1):
        passes += 1
        swapped = False
        for i in range(n - 1 - p):
            if b[i] > b[i + 1]:
                b[i], b[i + 1] = b[i + 1], b[i]
                swapped = True
        if not swapped:
            break
    return passes


def _bubble_swaps(a):
    b = list(a)
    n = len(b)
    swaps = 0
    for p in range(n - 1):
        for i in range(n - 1 - p):
            if b[i] > b[i + 1]:
                b[i], b[i + 1] = b[i + 1], b[i]
                swaps += 1
    return swaps


_P3_B = _jfam(
    "p3-bubble", "Bubble sort",
    "Compare neighbours, swap, repeat.",
    """
Bubble sort compares **adjacent** pairs and swaps them if they are out of order.
After one full pass the largest element has been carried all the way to the end
— it "bubbled" up — so the next pass can stop one place earlier.

```java
for (int pass = 0; pass < n - 1; pass++) {
    for (int i = 0; i < n - 1 - pass; i++) {      // note: - pass
        if (a[i] > a[i + 1]) {
            int tmp = a[i];
            a[i] = a[i + 1];
            a[i + 1] = tmp;
        }
    }
}
```

Three details worth having in your fingers:

- **`i < n - 1 - pass`.** The `- 1` keeps `a[i + 1]` in bounds; the `- pass`
  skips the tail that is already finished. Dropping the `- pass` still sorts
  correctly, just wastefully — dropping the `- 1` throws
  `ArrayIndexOutOfBoundsException`.
- **The swap needs a temporary.** `a[i] = a[i + 1]; a[i + 1] = a[i];` destroys
  the first value and duplicates the second.
- **Early exit.** If a pass makes no swaps, the array is sorted and every
  remaining pass is wasted. A `boolean swapped` flag turns bubble sort's best
  case from O(n²) into O(n) — which is its one genuine advantage over selection
  sort.

Every variant below uses **exactly this algorithm**, so the traces and the
counts line up. A different-but-correct bubble sort would give different
intermediate output.
""",
    [
        _p3ex("j3-pr-bub-one", "One pass only", "Easy",
              "Perform exactly **one** full bubble pass over the array — compare every "
              "adjacent pair once, left to right, swapping when out of order — then "
              "print the result in `Arrays.toString` format.",
              """
        for (int i = 0; i < n - 1; i++) {
            if (a[i] > a[i + 1]) {
                int tmp = a[i];
                a[i] = a[i + 1];
                a[i + 1] = tmp;
            }
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(_bubble_pass(a))) for a in _S_ARR],
              ["One loop, not two — this is a single pass.",
               "Stop at `i < n - 1` so `a[i + 1]` stays in bounds.",
               "Swap with a temporary: save `a[i]` first.",
               "After one pass the array is usually NOT sorted; the largest value has "
               "just reached the end. Case one gives `[2, 5, 1, 9]`."]),

        _p3ex("j3-pr-bub-full", "Sort it", "Easy",
              "Bubble sort the whole array ascending, then print it in "
              "`Arrays.toString` format. Do not call `Arrays.sort`.",
              """
        for (int pass = 0; pass < n - 1; pass++) {
            for (int i = 0; i < n - 1 - pass; i++) {
                if (a[i] > a[i + 1]) {
                    int tmp = a[i];
                    a[i] = a[i + 1];
                    a[i + 1] = tmp;
                }
            }
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(sorted(a))) for a in _S_ARR],
              ["Wrap the single pass in an outer loop that runs `n - 1` times.",
               "Each completed pass finishes one more element at the tail, so the "
               "inner bound can shrink: `i < n - 1 - pass`.",
               "The `- pass` is an optimisation, not a correctness fix — but the "
               "`- 1` is required to stay in bounds.",
               "A single-element array needs no passes at all, and `n - 1` is `0`, "
               "so the loop correctly does nothing."]),

        _p3ex("j3-pr-bub-trace", "Watch each pass", "Medium",
              "Bubble sort ascending, but print the whole array in `Arrays.toString` "
              "format **after every pass**, one line per pass. Use the shrinking inner "
              "bound `i < n - 1 - pass`, and run all `n - 1` passes with no early exit.",
              """
        for (int pass = 0; pass < n - 1; pass++) {
            for (int i = 0; i < n - 1 - pass; i++) {
                if (a[i] > a[i + 1]) {
                    int tmp = a[i];
                    a[i] = a[i + 1];
                    a[i + 1] = tmp;
                }
            }
            System.out.println(Arrays.toString(a));
        }
""",
              [_acase(list(a), _nl(*_bubble_trace(a))) for a in _S_ARR],
              ["The `println` goes in the OUTER loop, after the inner loop closes — "
               "one line per pass, not per comparison.",
               "Run all `n - 1` passes even once it is sorted; this variant has no "
               "early exit, so a sorted input still prints `n - 1` identical lines.",
               "A one-element array prints nothing at all, because there are zero "
               "passes. Case two checks that.",
               "Watch the largest value reach the end on line one, the second largest "
               "on line two, and so on — that is the invariant made visible."]),

        _p3ex("j3-pr-bub-passes", "How few passes were needed?", "Medium",
              "Bubble sort with an **early exit**: if a pass makes no swaps at all, "
              "stop. Print how many passes actually ran, counting the final pass that "
              "detected no swaps. Print only the number, not the array.",
              """
        int passes = 0;
        for (int pass = 0; pass < n - 1; pass++) {
            passes++;
            boolean swapped = false;
            for (int i = 0; i < n - 1 - pass; i++) {
                if (a[i] > a[i + 1]) {
                    int tmp = a[i];
                    a[i] = a[i + 1];
                    a[i + 1] = tmp;
                    swapped = true;
                }
            }
            if (!swapped) {
                break;
            }
        }
        System.out.println(passes);
""",
              [_acase(list(a), _bubble_passes(a)) for a in _S_ARR],
              ["The flag is declared INSIDE the outer loop so it resets each pass.",
               "Set it to `true` wherever you swap, and never back to `false` within "
               "a pass.",
               "Count the pass at the top of the body, so the detecting pass is "
               "included.",
               "`if (!swapped) break;` at the bottom of the outer loop.",
               "An already-sorted array (case four) makes no swaps on its first pass, "
               "so the answer is `1` — this is what makes bubble sort O(n) at best.",
               "A one-element array runs zero passes and prints `0`."]),

        _p3ex("j3-pr-bub-swaps", "Count the swaps", "Medium",
              "Bubble sort ascending with the shrinking bound and **no** early exit. "
              "Print the total number of swaps performed. (It equals the number of "
              "inversions in the input.)",
              """
        int swaps = 0;
        for (int pass = 0; pass < n - 1; pass++) {
            for (int i = 0; i < n - 1 - pass; i++) {
                if (a[i] > a[i + 1]) {
                    int tmp = a[i];
                    a[i] = a[i + 1];
                    a[i + 1] = tmp;
                    swaps++;
                }
            }
        }
        System.out.println(swaps);
""",
              [_acase(list(a), _bubble_swaps(a)) for a in _S_ARR],
              ["One counter for the whole sort, declared before both loops.",
               "Increment it inside the `if`, next to the swap — not once per "
               "comparison.",
               "A sorted array needs zero swaps; a reversed one needs the maximum, "
               "`n * (n - 1) / 2`. Case three is reversed with `n = 4`, so `6`.",
               "This count is exactly the number of inversions — pairs that are out "
               "of order — because each adjacent swap fixes exactly one."]),
    ])


# --- Family C - selection sort ----------------------------------------------

def _selection_trace(a):
    b = list(a)
    n = len(b)
    out = []
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if b[j] < b[m]:
                m = j
        b[i], b[m] = b[m], b[i]
        out.append(_jarr(b))
    return out


def _selection_swaps(a):
    b = list(a)
    n = len(b)
    swaps = 0
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if b[j] < b[m]:
                m = j
        if m != i:
            b[i], b[m] = b[m], b[i]
            swaps += 1
    return swaps


_P3_C = _jfam(
    "p3-selection", "Selection sort",
    "Find the smallest of what is left, put it in place.",
    """
Selection sort keeps a sorted prefix on the left. Each round it scans the
**unsorted remainder** for the smallest value and swaps it into the next slot:

```java
for (int i = 0; i < n - 1; i++) {
    int min = i;                          // seed with the slot being filled
    for (int j = i + 1; j < n; j++) {     // scan the REST
        if (a[j] < a[min]) min = j;
    }
    int tmp = a[i]; a[i] = a[min]; a[min] = tmp;
}
```

It is module 1's running-minimum, run once per position — except it tracks the
**index** rather than the value, because it has to swap.

**Seed `min` with `i`, not with `0`.** Seeding with `0` compares against an
already-sorted element and the sort silently breaks after the first round.

The interesting property is the **swap count**. Selection sort performs at most
`n - 1` swaps regardless of input, because each round places exactly one
element. Bubble sort, on the same reversed array, performs `n(n-1)/2`. Both are
O(n²) in *comparisons*, but if writes are expensive — flash memory, say —
selection sort is dramatically better. That difference is the reason to know
both.

Its weakness is the mirror image: it has **no best case**. A sorted array still
costs a full scan every round, where bubble sort's early exit finishes in one
pass.
""",
    [
        _p3ex("j3-pr-sel-full", "Sort it", "Easy",
              "Selection sort the array ascending, then print it in `Arrays.toString` "
              "format. Do not call `Arrays.sort`.",
              """
        for (int i = 0; i < n - 1; i++) {
            int min = i;
            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[min]) {
                    min = j;
                }
            }
            int tmp = a[i];
            a[i] = a[min];
            a[min] = tmp;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(sorted(a))) for a in _S_ARR],
              ["Track the INDEX of the smallest, not its value — you need the index "
               "to swap.",
               "Seed `min = i`, the slot you are about to fill. Seeding `0` breaks "
               "after the first round.",
               "The inner scan starts at `j = i + 1`; everything before `i` is "
               "already finished.",
               "Swap `a[i]` and `a[min]` after the inner loop, not inside it."]),

        _p3ex("j3-pr-sel-trace", "One round at a time", "Medium",
              "Selection sort ascending, printing the whole array in `Arrays.toString` "
              "format after **each round** — that is, after each swap into position "
              "`i`. Swap unconditionally, even when the smallest is already in place.",
              """
        for (int i = 0; i < n - 1; i++) {
            int min = i;
            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[min]) {
                    min = j;
                }
            }
            int tmp = a[i];
            a[i] = a[min];
            a[min] = tmp;
            System.out.println(Arrays.toString(a));
        }
""",
              [_acase(list(a), _nl(*_selection_trace(a))) for a in _S_ARR],
              ["Print in the outer loop, after the swap.",
               "There are `n - 1` rounds, so `n - 1` lines — a one-element array "
               "prints nothing.",
               "Swap even when `min == i`; a self-swap is harmless and keeps the "
               "output count predictable.",
               "The sorted prefix grows by one element per line, and everything left "
               "of position `i` never moves again."]),

        _p3ex("j3-pr-sel-swaps", "Count the real swaps", "Medium",
              "Selection sort ascending, but skip the swap when the smallest element "
              "is already in place. Print how many swaps actually happened.",
              """
        int swaps = 0;
        for (int i = 0; i < n - 1; i++) {
            int min = i;
            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[min]) {
                    min = j;
                }
            }
            if (min != i) {
                int tmp = a[i];
                a[i] = a[min];
                a[min] = tmp;
                swaps++;
            }
        }
        System.out.println(swaps);
""",
              [_acase(list(a), _selection_swaps(a)) for a in _S_ARR],
              ["Guard the swap with `if (min != i)`.",
               "Count only inside that guard.",
               "An already-sorted array needs zero swaps (case four), even though it "
               "still does every comparison — selection sort has no early exit.",
               "The answer can never exceed `n - 1`, however scrambled the input. "
               "Compare that with the bubble-sort swap count on the same reversed "
               "array in case three: 2 here versus 6 there."]),

        _p3ex("j3-pr-sel-desc", "Sort it the other way", "Easy",
              "Selection sort the array **descending** — largest first — then print it "
              "in `Arrays.toString` format.",
              """
        for (int i = 0; i < n - 1; i++) {
            int best = i;
            for (int j = i + 1; j < n; j++) {
                if (a[j] > a[best]) {
                    best = j;
                }
            }
            int tmp = a[i];
            a[i] = a[best];
            a[best] = tmp;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(sorted(a, reverse=True))) for a in _S_ARR],
              ["Exactly the ascending sort with one character changed.",
               "Selecting the LARGEST of the rest instead of the smallest means "
               "`a[j] > a[best]`.",
               "Nothing else moves — the seeding, the scan range and the swap are "
               "identical.",
               "This is why sorting code is usually parameterised by a comparison: "
               "the direction is one operator, not a second algorithm."]),

        _p3ex("j3-pr-sel-kth", "The k-th smallest", "Medium",
              "Read the array, then `k` (1-based). Print the k-th smallest value — "
              "without sorting the whole array. Run only `k` rounds of selection.",
              """
        int k = sc.nextInt();
        for (int i = 0; i < k; i++) {
            int min = i;
            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[min]) {
                    min = j;
                }
            }
            int tmp = a[i];
            a[i] = a[min];
            a[min] = tmp;
        }
        System.out.println(a[k - 1]);
""",
              [_akcase(a, k, sorted(a)[k - 1])
               for (a, k) in (([5, 2, 9, 1], 1), ([5, 2, 9, 1], 3), ([3], 1),
                              ([4, 3, 2, 1], 4), ([2, 1, 2, 1, 2], 2))],
              ["Selection sort places one final element per round, so after `k` "
               "rounds the first `k` slots are correct.",
               "You therefore only need the outer loop to run `k` times, not "
               "`n - 1`.",
               "`k` is 1-based but indices are 0-based, so the answer is `a[k - 1]`.",
               "This is why selection sort is the natural way to get a partial "
               "sort: the work is O(k * n) rather than O(n log n).",
               "Case four asks for the 4th smallest of four values — the maximum."]),
    ])


# --- Family D - insertion sort ----------------------------------------------

def _insertion_trace(a):
    b = list(a)
    out = []
    for i in range(1, len(b)):
        key = b[i]
        j = i - 1
        while j >= 0 and b[j] > key:
            b[j + 1] = b[j]
            j -= 1
        b[j + 1] = key
        out.append(_jarr(b))
    return out


def _insertion_shifts(a):
    b = list(a)
    shifts = 0
    for i in range(1, len(b)):
        key = b[i]
        j = i - 1
        while j >= 0 and b[j] > key:
            b[j + 1] = b[j]
            j -= 1
            shifts += 1
        b[j + 1] = key
    return shifts


_P3_D = _jfam(
    "p3-insertion", "Insertion sort",
    "Slide each new value back into a sorted prefix.",
    """
Insertion sort is how people sort a hand of cards. The prefix `a[0..i-1]` is
already in order; take `a[i]`, slide everything bigger one place right, and drop
it into the gap.

```java
for (int i = 1; i < n; i++) {            // start at 1 — a[0] alone is sorted
    int key = a[i];                      // SAVE it before overwriting anything
    int j = i - 1;
    while (j >= 0 && a[j] > key) {       // j >= 0 FIRST — short-circuit matters
        a[j + 1] = a[j];                 // slide right
        j--;
    }
    a[j + 1] = key;                      // drop into the gap
}
```

Three things go wrong here, reliably:

- **Forgetting `key`.** The first slide overwrites `a[i]`. If you did not save
  it, it is gone.
- **Ordering the `while` guard wrong.** `a[j] > key && j >= 0` throws
  `ArrayIndexOutOfBoundsException` the moment `j` reaches `-1`, because Java
  evaluates left to right and `&&` only short-circuits *after* the left side.
  The bounds check must come first.
- **`a[j + 1] = key`, not `a[j] = key`.** The loop exits one step past the
  landing spot — either because `a[j]` is small enough or because `j` fell off
  the front.

Insertion sort is the one O(n²) sort that is genuinely useful: it is **stable**,
**in place**, and **O(n) on nearly-sorted data** — which is why real library
sorts switch to it for small or almost-ordered ranges.
""",
    [
        _p3ex("j3-pr-ins-full", "Sort it", "Easy",
              "Insertion sort the array ascending, then print it in `Arrays.toString` "
              "format. Do not call `Arrays.sort`.",
              """
        for (int i = 1; i < n; i++) {
            int key = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
            }
            a[j + 1] = key;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(sorted(a))) for a in _S_ARR],
              ["Start the outer loop at `i = 1` — a single element is already a "
               "sorted prefix.",
               "Save `a[i]` into `key` before the sliding starts, or the first slide "
               "destroys it.",
               "Guard the while with `j >= 0` FIRST, then `a[j] > key`.",
               "The landing slot is `j + 1`, not `j`, because the loop exits one "
               "past it."]),

        _p3ex("j3-pr-ins-trace", "After each insertion", "Medium",
              "Insertion sort ascending, printing the whole array in `Arrays.toString` "
              "format after each element has been inserted — one line per outer "
              "iteration.",
              """
        for (int i = 1; i < n; i++) {
            int key = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
            }
            a[j + 1] = key;
            System.out.println(Arrays.toString(a));
        }
""",
              [_acase(list(a), _nl(*_insertion_trace(a))) for a in _S_ARR],
              ["Print at the bottom of the outer loop, after the key has landed.",
               "There are `n - 1` insertions, so `n - 1` lines; a one-element array "
               "prints nothing.",
               "Notice the sorted prefix growing from the left, and that the tail "
               "beyond `i` is untouched — that is the difference from selection "
               "sort's trace, where the tail is the messy part."]),

        _p3ex("j3-pr-ins-shifts", "Count the sliding", "Medium",
              "Insertion sort ascending. Print the total number of **shifts** — how "
              "many times a value was moved one place right by the inner loop. The "
              "final drop into the gap does not count.",
              """
        int shifts = 0;
        for (int i = 1; i < n; i++) {
            int key = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
                shifts++;
            }
            a[j + 1] = key;
        }
        System.out.println(shifts);
""",
              [_acase(list(a), _insertion_shifts(a)) for a in _S_ARR],
              ["Count inside the `while`, once per slide.",
               "Do not count `a[j + 1] = key;` — that is the drop, not a shift.",
               "A sorted array shifts nothing at all (case four gives `0`) because "
               "the while condition fails immediately — this is the O(n) best case.",
               "A reversed array shifts the maximum, `n * (n - 1) / 2`; case three "
               "gives `6`.",
               "The shift count equals the inversion count, the same quantity bubble "
               "sort's swap count measured."]),

        _p3ex("j3-pr-ins-one", "Insert one value", "Easy",
              "The array arrives **already sorted** ascending. Read it, then a value "
              "`k`. Produce a new array of length `n + 1` with `k` slid into its correct "
              "place, and print it in `Arrays.toString` format.",
              """
        int k = sc.nextInt();
        int[] out = Arrays.copyOf(a, n + 1);
        int j = n - 1;
        while (j >= 0 && out[j] > k) {
            out[j + 1] = out[j];
            j--;
        }
        out[j + 1] = k;
        System.out.println(Arrays.toString(out));
""",
              [_akcase(a, k, _jarr(sorted(list(a) + [k])))
               for (a, k) in (([1, 3, 5, 7], 4), ([1, 3, 5, 7], 0),
                              ([1, 3, 5, 7], 9), ([42], 42), ([2, 2, 2], 2))],
              ["This is the INNER half of insertion sort on its own — the motion the "
               "whole algorithm repeats.",
               "Make room first: `Arrays.copyOf(a, n + 1)` gives a slot at the end.",
               "Slide from the last real element, `j = n - 1`, while it is bigger "
               "than `k`.",
               "Same guard order: `j >= 0 && out[j] > k`.",
               "Drop at `j + 1`. Case two puts `0` at the very front, which is where "
               "`j` falling to `-1` lands it.",
               "Using `>` rather than `>=` stops sliding at an equal value, which is "
               "what makes insertion sort stable."]),

        _p3ex("j3-pr-ins-sorted", "Is it already sorted?", "Intro",
              "Print `true` if the array is already in non-decreasing order, `false` "
              "otherwise. Equal neighbours are fine.",
              """
        boolean sorted = true;
        for (int i = 1; i < n; i++) {
            if (a[i - 1] > a[i]) {
                sorted = false;
            }
        }
        System.out.println(sorted);
""",
              [_acase(list(a), _jbool(all(a[i - 1] <= a[i] for i in range(1, len(a)))))
               for a in _S_ARR],
              ["This is the check insertion sort's best case relies on.",
               "Compare each element with the one before it — start at `i = 1`.",
               "**Non-decreasing** means equal neighbours are allowed, so the "
               "failing test is a strict `>`.",
               "A one-element array is trivially sorted and must print `true`.",
               "Case five has repeated values out of order and is `false`."]),
    ])


# --- Family E - the library, and choosing -----------------------------------

_P3_E = _jfam(
    "p3-library", "Letting the library sort",
    "`Arrays.sort`, and the things it does not do.",
    """
Everything above is worth being able to write, and almost nothing above is worth
*using*. In real code you call:

```java
Arrays.sort(a);                 // sorts the whole array, in place, ascending
Arrays.sort(a, from, to);       // sorts a[from]..a[to-1] — `to` is exclusive
```

For `int[]` this is a dual-pivot quicksort — O(n log n) average, and far faster
than anything you would hand-write.

Three things it will not do for you, all drilled below:

- **It sorts in place.** The original order is destroyed. If you need it,
  `Arrays.copyOf` first — module 1's aliasing lesson, with consequences.
- **There is no descending `Arrays.sort` for `int[]`.** No overload takes a
  comparator, because `Comparator` works on objects and `int` is a primitive.
  Sort ascending and reverse, which is O(n log n) either way.
- **It does not tell you anything.** Sorting is usually a *step*: sort, then
  binary search; sort, then take the median; sort, then walk for duplicates.

> **The interview framing:** being asked to "sort this" almost never means
> "call `Arrays.sort`" — it means the interviewer wants to watch you write one.
> Being asked to *solve a problem* that happens to need sorting almost always
> does mean call it. Knowing which question you are being asked is the skill.
""",
    [
        _p3ex("j3-pr-lib-sort", "Let the library do it", "Intro",
              "Sort the array ascending using the library, then print it in "
              "`Arrays.toString` format.",
              """
        Arrays.sort(a);
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(sorted(a))) for a in _S_ARR],
              ["One call, no loops.",
               "`Arrays.sort` sorts IN PLACE and returns nothing.",
               "So call it as a statement — `a = Arrays.sort(a)` does not compile.",
               "Then print `a` itself with `Arrays.toString`."]),

        _p3ex("j3-pr-lib-keep", "Sort a copy, keep the original", "Easy",
              "Print the array in its original order on the first line, and a sorted "
              "copy on the second — both in `Arrays.toString` format. The original must "
              "not be modified.",
              """
        int[] sorted = Arrays.copyOf(a, n);
        Arrays.sort(sorted);
        System.out.println(Arrays.toString(a));
        System.out.println(Arrays.toString(sorted));
""",
              [_acase(list(a), _nl(_jarr(a), _jarr(sorted(a)))) for a in _S_ARR],
              ["`Arrays.sort(a)` would destroy the order you still need.",
               "`int[] copy = a;` is an alias, not a copy — sorting through it sorts "
               "`a` too. That is module 1's lesson biting for real.",
               "`Arrays.copyOf(a, n)` gives a genuinely separate array.",
               "Sort the copy, print `a` first, then the copy."]),

        _p3ex("j3-pr-lib-desc", "Descending", "Easy",
              "Print the array sorted **descending** in `Arrays.toString` format. There "
              "is no descending `Arrays.sort` for `int[]`, so sort ascending and then "
              "reverse in place.",
              """
        Arrays.sort(a);
        for (int i = 0; i < n / 2; i++) {
            int tmp = a[i];
            a[i] = a[n - 1 - i];
            a[n - 1 - i] = tmp;
        }
        System.out.println(Arrays.toString(a));
""",
              [_acase(list(a), _jarr(sorted(a, reverse=True))) for a in _S_ARR],
              ["Sort ascending first with the library call.",
               "Then reverse with module 1's two-pointer swap.",
               "The loop must stop at `n / 2`, or every pair is swapped twice and "
               "you get the ascending order back.",
               "The partner of `i` is `n - 1 - i`.",
               "Integer division handles odd lengths correctly — the middle element "
               "stays put, which is right."]),

        _p3ex("j3-pr-lib-median", "The median", "Medium",
              "Print the median. For an odd count that is the middle value; for an even "
              "count it is the integer average of the two middle values, "
              "`(lo + hi) / 2` with `int` division.",
              """
        Arrays.sort(a);
        if (n % 2 == 1) {
            System.out.println(a[n / 2]);
        } else {
            System.out.println((a[n / 2 - 1] + a[n / 2]) / 2);
        }
""",
              [_acase(list(a), (sorted(a)[len(a) // 2] if len(a) % 2 == 1
                                else _jdiv(sorted(a)[len(a) // 2 - 1]
                                           + sorted(a)[len(a) // 2], 2)))
               for a in ([5, 2, 9, 1], [3], [4, 3, 2, 1], [1, 2, 3, 4, 5],
                         [2, 1, 2, 1, 2])],
              ["A median is only meaningful on sorted data, so sort first.",
               "For odd `n` the middle index is `n / 2` — integer division already "
               "rounds down to the right place.",
               "For even `n` the two middles are `n / 2 - 1` and `n / 2`.",
               "Average them with `int` division, as the brief says — no rounding, "
               "no doubles.",
               "Case two is a single element, which is its own median."]),

        _p3ex("j3-pr-lib-dupe", "Any duplicates?", "Medium",
              "Print `true` if any value appears more than once, `false` otherwise. Sort "
              "first, then a single pass is enough.",
              """
        Arrays.sort(a);
        boolean dupe = false;
        for (int i = 1; i < n; i++) {
            if (a[i] == a[i - 1]) {
                dupe = true;
            }
        }
        System.out.println(dupe);
""",
              [_acase(list(a), _jbool(len(set(a)) != len(a)))
               for a in ([5, 2, 9, 1], [3], [2, 1, 2], [1, 2, 3, 4],
                         [2, 1, 2, 1, 2])],
              ["Comparing every pair would be O(n^2). Sorting first makes duplicates "
               "ADJACENT, so one pass finds them.",
               "Sort, then compare each element with its predecessor.",
               "Start the scan at `i = 1`.",
               "A one-element array has no pairs at all and must print `false`.",
               "Total cost is O(n log n) for the sort plus O(n) for the scan — the "
               "standard 'sort first, then the problem is easy' move."]),
    ])


_PRACTICE[3] = [_P3_A, _P3_B, _P3_C, _P3_D, _P3_E]
