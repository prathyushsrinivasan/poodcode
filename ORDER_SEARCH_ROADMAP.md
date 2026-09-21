# Order & Search — expansion roadmap

Stage 3 of the DSA Curriculum (`tools/dsa_s3_search.py`): **Recursion → Sorting →
Binary Search → Greedy → Intervals**. 5 units, 112 problems as of SEED_VERSION 12.

## Audit: where the stage stands

| Depth layer | Stage 2 (Patterns) | Stage 3 (Order & Search) |
| --- | --- | --- |
| Stage router (`_route`) | 13 rows | **none** |
| Loop invariant (`_inv`) | 4 / 6 units | **0 / 5** |
| Variant family (`_var`) | 6 / 6 | **0 / 5** |
| Slow → fast rewrites (`_rw`) | 6 / 6 | **0 / 5** |
| Build it from scratch | 6 / 6 | **0 / 5** |
| Internals | 2 / 6 | 1 / 5 (binary search) |
| Worked traces | ≥ 1 each | 1–2 each |
| Big-O drills | ≥ 4 each | 5 each |

Other gaps found while reading the units:

- Three ladder problems have **no rung note**: `interval-intersections`,
  `car-pooling` and `min-arrows-balloons`. Every other problem gets its note from
  the stage file or from `dsa_placements.py`.
- **Recursion** never covers the Master theorem, the JVM call stack (`-Xss`, and
  the lack of tail calls), or divide and conquer beyond merge sort. The unit
  opens at *Core*.
- **Sorting** has no radix or bucket sort rung, although `maximum-gap` needs one
  and sits in Extra practice. Nothing covers the comparison lower bound, Timsort
  internals, stable argsort, three-way partitioning, or merge-counting with a
  non-trivial condition.
- **Binary search** has no "maximise the minimum" rung (`magnetic-force` is
  extra), no real-valued search, no "count ≤ x" search over a value space, and no
  on-ramp for search on the answer (Koko is the first).
- **Greedy** covers the exchange argument in prose but has no problems in the
  ordering-by-comparator family: Smith's rule, deadlines, lateness. There is no
  stress-test (brute force against greedy) workflow either.
- **Intervals** never reaches the point where greedy fails: weighted interval
  scheduling, which is the bridge into DP. It has no union-length or
  interval-subtraction problems, and no on-ramp simpler than meeting rooms.

## Status: implemented (SEED_VERSION 13)

Every item below shipped, with these deviations:

- **Recursion's new problems changed.** The bank already had `digital-root`
  and `maximum-subarray`, so `digit-sum-recursive`, `max-subarray-halves` and
  `majority-by-halves` became `to-base-recursive` (E, work after the call),
  `josephus-survivor` (M, a recursion too deep for the stack) and
  `mulmod-by-halving` (M, fast power with + instead of ×).
  `closest-pair-points` shipped as planned. Maximum subarray by halves is now a
  worked trace, not a problem.
- **The sorting problem is `radix-pass-by-pass`**, not `radix-sort-numbers`.
  It prints the order after every pass, so a sort that is not a stable LSD
  radix sort cannot pass it.
- **Intervals has no internals section.** It was never in the plan's list.
  Greedy gained one (matroids, the exchange checklist, stress testing).
- **Rung notes**: the audit's "~40 missing" was wrong — only 3 were, and all 3
  are now written.

| Unit | Required / total problems | Traces | Big-O | Checks | Invariant · Variants · Rewrites · Build-it |
| --- | --- | --- | --- | --- | --- |
| Recursion | 9 / 20 | 3 | 8 | 10 | ✓ · 7 · 3 · ✓ (+ internals) |
| Sorting | 9 / 19 | 3 | 8 | 11 | ✓ · 10 · 4 · ✓ (+ internals) |
| Binary search | 14 / 28 | 4 | 8 | 9 | ✓ · 8 · 4 · ✓ |
| Greedy | 14 / 31 | 3 | 8 | 9 | ✓ · 9 · 3 · ✓ (+ internals) |
| Intervals | 13 / 24 | 3 | 8 | 8 | ✓ · 9 · 3 · ✓ |

Each unit's required ladder stays inside its weight band. For each new
problem, the problem it supersedes moved to Extra practice, with its note kept.
New traces are *computed* (`tools/dsa_s3_depth.py` runs each algorithm to
produce its rows).

**Verification.** Python and Java references agree on every case of all 22
new problems. Brute-force oracles agree on hundreds of random small inputs per
problem. `verify_dsa_curriculum` passes, with the lint sets extended in both
Python and Rust. `VERIFY_SLUGS=…` now lets `verify_seeds` judge a single batch.

## The list

### A. Stage level
1. **Stage router**: about 16 `_route` rows mapping prompt shape to unit, each
   with its `not_when` near miss (k-th → sort, heap or quickselect; "minimum X
   such that" → binary search on the answer, unless the predicate is not
   monotone; "maximum non-overlapping" → intervals by end; weighted version →
   DP).
2. **Stage goal rewrite**: a "what order buys" table for each unit, as stage 2
   has, plus a paragraph on the confusable pairs.
3. Lint coverage: add all five units to `_NEEDS_INVARIANT`, `_NEEDS_VARIANTS`,
   `_NEEDS_REWRITES` and `_NEEDS_BUILD_IT`, and add `sorting` and `recursion`
   to `_NEEDS_INTERNALS`. Mirror these in `verify_dsa_curriculum.rs`, so the
   depth cannot be lost later.

### B. Recursion
4. **Invariant** as induction: the promise is the statement, the base case
   establishes it, the recursive case maintains it, and the top call gives the
   answer at exit.
5. **Variants**: linear, halving, binary branching, divide and conquer,
   memoised, accumulator-passing, and "build a list of results"
   (parenthesisations).
6. **Rewrites**: naive Fibonacci → memo; `power` called twice → once; a
   recursive list walk → iterative (depth as a memory bug).
7. **Internals**: stack frames, the JVM default stack, a `Thread` with a larger
   stack, the lack of tail-call elimination in Java, and the Master theorem's
   three cases.
8. **Build it**: power, merge sort, a Hanoi move list, and memo-fib timed
   against naive.
9. **Traces**: the fast-power call chain and the Hanoi call tree.
10. **Model**: a Master theorem section and a "divide and conquer beyond
    sorting" section (a cross-midpoint combine).
11. New problems: `max-subarray-halves` (M, D&C with the crossing sum),
    `majority-by-halves` (M, D&C majority), `closest-pair-points` (H, the
    classic strip argument), `digit-sum-recursive` (I, on-ramp).
12. New rung **Beyond sorting: combine across the middle**.
13. Notes for every rung item, plus extra checks, pitfalls and Big-O items.

### C. Sorting
14. **Invariant**: the Lomuto partition regions `[lo, p) < pivot`,
    `[p, i) ≥ pivot`.
15. **Variants**: library sort, comparator key, argsort, counting, radix,
    bucket, three-way partition, quickselect, merge-count, and top-k by heap.
16. **Rewrites**: subtraction comparator → `Integer.compare`; sort for the k-th
    → quickselect; O(n²) inversion count → merge-count; a key recomputed inside
    the comparator → keys computed once.
17. **Internals**: dual-pivot quicksort, Timsort (runs, galloping, stability),
    insertion sort below 47 elements, the log₂(n!) comparison lower bound, and
    why primitives are sorted unstably.
18. **Build it**: insertion sort, merge sort, three-way quicksort, counting
    sort, LSD radix sort, and a comparator contract tester.
19. **Traces**: a Lomuto partition step by step, and radix passes.
20. New rungs: **Non-comparison sorts** (radix, `maximum-gap`) and **Merge
    counting with a condition** (reverse pairs).
21. New problems: `rank-transform` (E, argsort and ties), `radix-sort-numbers`
    (M), `important-reverse-pairs` (H, merge-count on `a[i] > 2·a[j]`),
    `moves-to-median` (M, quickselect median).
22. Notes, checks, pitfalls and Big-O items.

### D. Binary search
23. **Invariant**: stated formally, with all four parts.
24. **Variants**: lower bound, upper bound, last true, min-feasible,
    max-feasible, rotated, peak, count ≤ x over a value space, real-valued via
    scaling, and partition search (the median of two arrays).
25. **Rewrites**: linear scan → lower bound; try every capacity → search on the
    answer; closed interval plus equality branch → half-open; `while (hi - lo > eps)`
    → a fixed iteration count or integer scaling.
26. **Build it**: all templates from an empty file, then a property test
    against a linear scan.
27. **Traces**: rotated-array minimum; maximise the minimum distance.
28. New rungs: **Maximise the minimum** and **Count ≤ x over a value space**.
29. New problems: `min-time-for-trips` (M, on-ramp for search on the answer),
    `max-equal-portions` (M, maximise), `sqrt-to-six-places` (M, real-valued
    made exact), `nth-divisible-number` (M, count plus inclusion–exclusion),
    `kth-in-multiplication-table` (H, count ≤ x).
30. Notes, checks, pitfalls and Big-O items.

### E. Greedy
31. **Invariant**: stays ahead (the reach after i steps ≥ any strategy's).
32. **Variants**: running extreme, furthest reach, sort by end, sort by ratio,
    exchange-comparator ordering, two ends, reset (gas station), heap regret,
    and two passes (candy).
33. **Rewrites**: DP jump game O(n²) → reach; try every order n! → exchange
    sort; O(n²) gas station → one pass with reset.
34. **Internals**: when greedy is provably right (the matroid intuition, the
    exchange lemma), and a brute-force stress harness.
35. **Build it**: write a greedy, a brute force, and a random stress loop, then
    break a wrong greedy with it.
36. **Traces**: a Jump Game II window trace and a gas-station reset trace.
37. New rung **Order by exchange argument**.
38. New problems: `cheapest-first-budget` (E, on-ramp), `weighted-completion-order`
    (M, Smith's rule with cross-multiplication), `min-max-lateness` (M, by
    deadline), `job-deadlines-profit` (M, latest free slot), `make-values-unique`
    (M, sort and push up).
39. Notes, checks, pitfalls and Big-O items.

### F. Intervals
40. **Invariant**: merge (the output is sorted and disjoint, and only the last
    block can touch the next interval).
41. **Variants**: merge, insert, schedule by end, stab with points, peak
    concurrency, intersection, greedy coverage, complement, online calendar,
    and weighted (DP boundary).
42. **Rewrites**: pairwise overlap O(n²) → sort and scan; a timeline array
    O(T) → an event sweep; insert by re-sorting → three phases.
43. **Build it**: merge, insert, rooms two ways, intersect, and weighted
    scheduling.
44. **Traces**: the ±1 sweep for rooms, and insert-interval phases.
45. New rung **When greedy stops working** (weighted scheduling).
46. New problems: `covered-length-union` (E), `subtract-interval` (M),
    `busiest-moment` (M), `weighted-job-scheduling` (H, sort by end, binary
    search the predecessor, DP).
47. Notes, checks, pitfalls and Big-O items.

### G. Finishing
48. Place every new problem, and keep rung difficulty climbing and the weight
    bands sensible.
49. Bump `SEED_VERSION`, regenerate, and run `verify_dsa_curriculum` plus
    in-process Python-against-Java agreement on each new problem.
50. Update `DSA_ROADMAP.md` and the curriculum memory.

---

# Round 2: features, polish and help

Round 1 filled in the depth layer the stage was missing. Round 2 adds **new
kinds of help** that no unit in the curriculum has yet. They are built as
generic unit and stage fields, so any stage can adopt them later, and they are
authored for all five Order & Search units first.

## What is still missing

- **Nothing makes you find a bug.** Every drill asks you to recall
  (self-checks), price (Big-O) or classify (family drill). None of them shows
  broken code and asks what is wrong — although "one-character boundary bug" is
  this stage's commonest failure.
- **No help before the first line of code.** Pitfalls are indexed by the
  symptom after a failed run. Nothing helps the learner who has read the
  prompt and has no idea.
- **No edge-case list to test against.** Hidden tests fail on empty input, all
  duplicates, `Integer.MIN_VALUE` and touching intervals. Nothing names those
  cases before you submit.
- **No complete solved example.** The model explains the technique and the
  ladder hands you problems. Nothing shows a single problem going from prompt
  to route, brute force, insight, code and test.
- **No one-page summary.** The templates are spread across five pages.

## The list

### Features (generator → lint → `models.rs` → `types.ts` → UI)
1. **Spot the bug / predict the state** (`quizzes`). Multiple-choice drills,
   graded and scheduled like the Big-O cards (`dsa-quiz:<unit>:<i>`), counted
   in the Review tab's deck. There are two kinds: `bug` (which line is wrong,
   and why) and `predict` (what the code outputs or leaves behind).
2. **Stuck? Try this** (`stuck`). A triage table for the moment before any
   code exists: *if you cannot see X, ask Y*. It goes on the Toolkit tab.
3. **Test before you submit** (`edge_cases`). Each case comes with a
   ready-to-paste input and the bug it exposes, plus a copy button. It goes on
   the Practice tab.
4. **Worked solution, start to finish** (`walkthrough`). One canonical problem
   per unit, narrated through six fixed steps: read, route, brute force,
   insight, code, and test and price. It links to the problem and goes on the
   Learn tab.
5. **Stage cheat sheet** (`cheatsheet` on `_stage`). The whole stage's
   templates on one page, shown collapsible on the Library stage panel.
6. **Lints**: `_NEEDS_HELP` requires quizzes (≥ 4), stuck (≥ 4), edge cases
   (≥ 4) and a walkthrough on every Order & Search unit, mirrored in
   `verify_dsa_curriculum.rs`. Quiz answers must be among their options.

### Content
7. About 30 quiz items, 28 stuck rows, 28 edge cases, 5 walkthroughs and the
   stage cheat sheet.
8. Five more computed traces: the Hanoi call tree, the three-way partition,
   lower bound over duplicates, candy's two passes, and insert-interval's three
   phases.
9. Interview sections gain "say this out loud" scripts: the sentences to use
   when stating the approach, the invariant and the complexity.
10. New problems:
    - `count-range-sums` (H, merge-count with a window over prefix sums)
    - `covered-by-two` (M, sweep for coverage ≥ 2)
    - `min-max-after-splits` (M, minimise the maximum)
    - `sierpinski-cell` (M, recursion on quadrants)
    - `min-increments-to-cover` (M, greedy patching)
11. Docs and memory updated.

## Round 2 status: implemented (SEED_VERSION 14)

All 11 items shipped.

| Unit | Required / total | Traces | Quizzes | Stuck | Edge cases | Worked solution |
| --- | --- | --- | --- | --- | --- | --- |
| Recursion | 9 / 21 | 4 | 6 | 6 | 8 | `josephus-survivor` |
| Sorting | 9 / 20 | 4 | 6 | 6 | 8 | `count-inversions` |
| Binary search | 14 / 29 | 5 | 6 | 6 | 8 | `min-ship-capacity` |
| Greedy | 14 / 32 | 4 | 6 | 6 | 8 | `weighted-completion-order` |
| Intervals | 14 / 25 | 4 | 6 | 6 | 8 | `weighted-job-scheduling` |

**Where each feature appears**

- The quizzes appear under the Review tab as **Spot the bug, predict the
  result**. They use the new `ChoiceCard`, which the Big-O cards now share,
  and they count toward the tab's due badge.
- The stuck table appears under the Toolkit tab as **Stuck before the first
  line?**.
- The edge cases appear under the Practice tab as **Test before you submit**,
  with the problem's slug and a copy button on each case.
- The worked solution appears under the Learn tab, with a link to open its
  problem.
- The cheat sheet sits on the Library stage panel as **The whole stage on one
  page**.

**Changes to the plan**

- Edge cases gained a `slug` field. It ties each input to a problem on the
  unit's ladder, which the lint enforces, so the input format is real.
- The greedy problem is `patch-to-cover-range`, not `min-increments-to-cover`.
- The ladders were full, so four of the five new problems went to Extra
  practice. `covered-by-two` took the one free required slot, in Intervals.

**Verification**

- The generator lints (`_NEEDS_HELP`) pass, and so does their Rust mirror
  `units_that_need_help_carry_it`.
- `tsc` passes, as do the 315 vitest tests.
- The quiz, stuck, edge-case, walkthrough and cheat-sheet sections were
  checked rendering in the mock dev server, with no console errors.
- Every quiz answer was confirmed by executing a Python twin of its snippet.
- Every edge-case input was run through its problem's reference solution, or
  matched against stored examples for older problems that have no reference.
- The 5 new problems: Python and Java references agree on every case, the
  real judge accepts both, and brute-force oracles agree on 400 random inputs
  each.
