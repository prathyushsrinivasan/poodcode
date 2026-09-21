# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The syllabus roadmap, applied to the ladders.
#
# exec'd by tools/dsa_curriculum.py after dsa_placements.py, in the same
# namespace, so `_UNITS`, `_rung`, `_add_rung` and `_place` are defined.
#
# The stage files own each unit's teaching and dsa_placements.py records where
# the batched problems first landed. This file records the *re-homing* the
# syllabus audit asked for — a problem taught by the wrong unit, a technique
# with no rung, a unit whose required ladder outgrew its weight — as one list
# of moves rather than a dozen silent edits to rungs defined elsewhere.
#
# Every move is still checked by `_check_curriculum`: a problem moved onto a
# rung easier than itself stops the rungs climbing and fails the build.
# ---------------------------------------------------------------------------


def _rung_named(unit, title):
    for r in _unit_named(unit)["rungs"]:
        if r["title"] == title:
            return r
    raise AssertionError(f"dsa_syllabus.py: {unit} has no rung {title!r}")


def _move(slug, unit, rung, note=None):
    """Take `slug` off whichever rung holds it and put it on `unit`/`rung`.

    The old note travels with it unless a new one is given — a note written for
    one rung's purpose is usually still true on another, and when it is not the
    call site says so."""
    old_note = ""
    found = False
    for u in _UNITS:
        for r in u["rungs"]:
            if slug in r["slugs"]:
                r["slugs"].remove(slug)
                old_note = r["notes"].pop(slug, "")
                found = True
    assert found, f"dsa_syllabus.py: {slug!r} is not on any rung"
    _place(unit, rung, slug, old_note if note is None else note)


def _drop_empty_rungs():
    for u in _UNITS:
        u["rungs"] = [r for r in u["rungs"] if r["slugs"]]


# ======================================================================= strings
# Palindromes and pattern matching had problems (Extra practice) and no
# teaching. They now have a required rung, and the unit's lightest drills make
# room for it so its required ladder stays inside the weight band.

_add_rung("strings", "Palindromes & matching",
          "Two string algorithms with names: expand around a centre, and the KMP prefix function.")
_place("strings", "Palindromes & matching", "find-pattern-index",
       "The prefix function, then one pass that never moves the text pointer backwards. Build `pi` by hand for `abcaby` first.")
_place("strings", "Palindromes & matching", "count-palindromic-substrings",
       "2n − 1 centres, not n. `abba` has no middle letter, and expanding only from letters misses it.")
_move("longest-palindromic-substring", "strings", "Palindromes & matching",
      "The counting loop again, keeping the widest expansion instead of a tally.")
_move("longest-happy-prefix", "strings", "Palindromes & matching",
      "The answer is `pi[n − 1]` — the prefix function of the string itself, read at its last index.")
_move("shortest-palindrome", "strings", "Palindromes & matching",
      "Run the prefix function on `s + \"#\" + reverse(s)`: the longest palindromic prefix is its last value. The `#` stops a match running across the join.")

for _slug in ("password-strength", "count-words", "max-nesting-depth",
              "longest-common-prefix-strs", "zigzag-conversion"):
    _move(_slug, "strings", "Extra practice")


# ===================================================================== recursion
# Divide and conquer was a section of the model with no rung. Merge sort is its
# canonical example, and `ways-to-add-parentheses` — split at every operator,
# solve both sides, combine — was already in the bank.

_add_rung("recursion", "Divide and conquer",
          "Split into independent halves, solve both, combine — the recurrence T(n) = 2T(n/2) + O(n) as code.")
_place("recursion", "Divide and conquer", "merge-sort-array",
       "Trust both recursive calls, then merge with two pointers. Count the levels: log n of them, each merging n elements in total.")
_move("ways-to-add-parentheses", "recursion", "Divide and conquer",
      "Split at every operator, solve each side into a list of values, combine every pair. Divide and conquer where the halves are not halves.")

for _slug in ("count-and-say", "nested-list-depth-sum"):
    _move(_slug, "recursion", "Extra practice")


# ======================================================================= sorting
# The unit taught calling a sort and repeated two heaps problems. It now teaches
# the algorithms whose ideas outlive the library call: a sort that does not
# compare, quickselect, and merge sort's merge reused to count.

_place("sorting", "Warm up", "counting-sort-ages",
       "No comparisons at all: the value is the index. O(n + k) because k = 151.")
_add_rung("sorting", "Quickselect",
          "The k-th element in O(n) average — partition once, recurse into one side only.")
_move("kth-largest-element", "sorting", "Quickselect",
      "Solve it by sorting first, then with quickselect: partition around a random pivot and recurse into the side that holds index n − k.")
_move("kth-smallest", "sorting", "Quickselect",
      "The same partition, a different target index. A random pivot is what keeps the worst case away.")
_add_rung("sorting", "Merge sort, reused",
          "The merge step sees every pair that crosses the midpoint — so it can count them.")
_move("count-inversions", "sorting", "Merge sort, reused",
      "Merge sort from the recursion unit. When the right half's element is taken first, it jumps every remaining element of the left half: add `mid − i`.")
_move("top-k-frequent", "heaps", "Extra practice",
      "Counting, then a size-k heap of (count, value). The heaps-unit answer to what the sorting unit solved by sorting everything.")
_move("best-meeting-point-line", "sorting", "Extra practice")


# ============================================================ math-number-theory
# "Return the answer modulo 10^9 + 7" is in every counting DP and was taught
# nowhere. The sieve moves onto the required ladder beside the prime test.

_move("count-primes", "math-number-theory", "Core",
      "The sieve: cross out multiples starting from p², and the whole range costs O(n log log n).")
_add_rung("math-number-theory", "Counting modulo a prime",
          "Reduce after every product, exponentiate by squaring, and divide by multiplying with an inverse.")
_place("math-number-theory", "Counting modulo a prime", "power-mod",
       "Reduce the base before the first square — (10^18)² does not fit in a long.")
_move("count-good-numbers", "math-number-theory", "Counting modulo a prime",
      "5^even · 4^odd, with exponents near 10^15: two power-mods and one product, reduced.")
_place("math-number-theory", "Counting modulo a prime", "ncr-mod-queries",
       "Factorials once, one Fermat inverse at the top, the rest walking down. Then each query is three lookups.")
_move("perfect-number", "math-number-theory", "Extra practice")

# ==================================================================== linked lists
# Copying a structure whose nodes point sideways, and splicing one list into
# another, had no rung — although both are staples, and both are the old → new
# map that cloning a graph needs in stage 6.

_add_rung("linked-lists", "Pointer mapping",
          "Copy and splice structures whose nodes point somewhere other than next.",
          before="Stretch")
_place("linked-lists", "Pointer mapping", "copy-list-random-pointer",
       "Create every copy first, recording original → copy; then set next and random through the map. Weaving the copies in makes it O(1) space.")
_place("linked-lists", "Pointer mapping", "flatten-multilevel-list",
       "A splice needs the child list's tail. Have the recursion return it — then list the four pointer writes before coding.")
for _slug in ("odd-even-list", "list-get-nth"):
    _move(_slug, "linked-lists", "Extra practice")


# =========================================================================== trees
# Building a tree and writing one down were absent: no construction from
# traversals, no serialisation. Both are recursion that builds.

_add_rung("trees", "Build and walk",
          "Recursion that constructs a tree, and a traversal that records its shape.",
          before="Stretch")
_place("trees", "Build and walk", "serialize-tree-preorder",
       "Preorder with a `#` for every null child. Count the tokens: 2n + 1, always.")
_place("trees", "Build and walk", "deserialize-tree-preorder",
       "The same walk, reading one token per call. One shared index, and the left subtree before the right.")
_place("trees", "Build and walk", "build-tree-preorder-inorder",
       "Preorder names the root; its inorder position splits the rest. A value → index map keeps it O(n).")
for _slug in ("min-depth-tree", "zigzag-level-order", "balanced-tree"):
    _move(_slug, "trees", "Extra practice")


# ============================================================================= bst
# `TreeMap` was described in prose and practised nowhere, and the iterator — the
# in-order walk paused between calls — had no problem at all.

_add_rung("bst", "Iterators & ordered maps",
          "Pause an in-order walk, and let a TreeSet answer \"what is nearest?\".")
_place("bst", "Iterators & ordered maps", "floor-ceiling-queries",
       "`floor` and `ceiling` on a TreeSet, both O(log n) and both null when absent.")
_place("bst", "Iterators & ordered maps", "bst-iterator",
       "The iterative in-order loop, with its stack kept between calls. Push the left spine; next() pops and pushes the right child's spine.")
_place("bst", "Iterators & ordered maps", "nearby-almost-duplicate",
       "A sliding window you have to search: keep it in a TreeSet and ask for the ceiling of value − t. Work in long.")
for _slug in ("bst-successor", "recover-bst", "bst-insert"):
    _move(_slug, "bst", "Extra practice")


# ================================================================= graph traversal

_place("graph-traversal", "Variations", "clone-graph",
       "The visited set and the old → new map are one map. Record a node's copy before exploring from it.")
_move("reachable-within-k", "graph-traversal", "Extra practice")


# ================================================================== shortest paths
# Floyd–Warshall was a row in the "choosing" table, practised by nothing.

_add_rung("shortest-paths", "All pairs",
          "Every pair at once, when V is small — including negative edges.",
          before="Stretch")
_move("city-fewest-neighbours", "shortest-paths", "All pairs",
      "Floyd–Warshall, then count per city within the threshold. Ties go to the larger index.")
_place("shortest-paths", "All pairs", "floyd-warshall-queries",
       "k in the OUTER loop, and skip unreachable intermediates so INF plus a negative edge is never a path.")
for _slug in ("count-shortest-paths", "path-minimum-effort"):
    _move(_slug, "shortest-paths", "Extra practice")


# ============================================================== dynamic programming
# DP was two units split by the number of indices, which is not how the problems
# divide: the knapsack lived half in each, and interval and state-machine DP had
# no rung. The new units are defined in dsa_s7_dp.py with their new problems;
# the existing problems move here.

for _slug, _note in (
    ("coin-change", "Unbounded: coins outside, amounts ascending, an `amount + 1` sentinel for infinity."),
    ("coin-change-ways", "The same loops summing, base case 1 — and coins outside, so each combination is counted once."),
    ("perfect-squares", "Coin change whose coins are the squares up to n. O(n√n)."),
    ("target-sum", "Algebra first: the plus-group must sum to (total + target) / 2. Then count subsets, descending."),
):
    _move(_slug, "dp-knapsack", "Core", _note)
for _slug, _note in (
    ("last-stone-weight-ii", "Split the stones into two groups as equal as possible: the largest reachable sum ≤ total / 2."),
):
    _move(_slug, "dp-knapsack", "Variations", _note)
# Taken off dp-2d's Stretch rung in the stage file itself, so placed rather than moved.
_place("dp-knapsack", "Variations", "partition-equal-subset-sum",
       "Reachability of total / 2. An odd total is impossible — return before allocating.")

for _slug, _note in (
    ("stock-with-cooldown", "A third state, \"just sold\", that can only rest. Copy yesterday's values before updating."),
    ("longest-palindromic-subseq", "Match the two ends and shrink, or drop one end. Fill by length."),
    ("predict-the-winner", "Store the score difference for the player to move: max(a[i] − dp[i+1][j], a[j] − dp[i][j−1])."),
):
    _move(_slug, "dp-intervals-states", "Core", _note)
for _slug, _note in (
    ("burst-balloons", "Choose the LAST balloon burst in (i, j), so its neighbours are the fixed ends. Pad with 1s."),
    ("min-insertions-palindrome", "n minus the longest palindromic subsequence — the characters left without a partner."),
):
    _move(_slug, "dp-intervals-states", "Stretch", _note)
_place("dp-intervals-states", "Stretch", "longest-palindrome-length",
       "Interval DP over the ends, filled by length. Expanding around each centre also works — write both.")

_move("number-of-lis", "dp-2d", "Extra practice")


# ============================================================ beyond the core (optional)
# Problems whose technique no core unit teaches. Their new units are defined in
# dsa_s8_beyond.py with the batch-38 problems; these two were already in the bank.

_move("critical-connections", "advanced-graphs", "Stretch",
      "Bridges: the same low-link DFS as articulation points, with `low[v] > disc[u]` — strictly greater.")
_move("partition-k-equal-subsets", "bitmask-dp", "Core",
      "dp[mask] = fill of the group being built; add an item only if it fits, and wrap to 0 when a group completes.")


# ================================================== Order & Search, round 2
# Batches 46–48 add 22 problems that teach what the expanded stage-3 units now
# model: work after the call, a recursion too deep for the stack, divide and
# conquer's crossing term, radix passes, merge-counting with a condition,
# last-true and count-≤-x searches, exchange-argument orderings, and weighted
# interval scheduling. Each unit's required ladder stays inside its weight band
# by moving the problem each new one supersedes to Extra practice — nothing is
# deleted, and every move keeps its note.

def _extras(unit, *slugs):
    for _slug in slugs:
        _move(_slug, unit, "Extra practice")


# --- recursion (9 required)
_add_rung("recursion", "Warm up",
          "Where the work sits relative to the call decides the order it happens in.",
          before="Core")
_place("recursion", "Warm up", "to-base-recursive",
       "Append the last digit *after* the recursive call and the digits come out in order. Move the line above the call and watch them reverse.")
_place("recursion", "Variations", "mulmod-by-halving",
       "Fast power with × replaced by +. Write the one-line overflow argument — every value stays below 2m — before the code.")
_add_rung("recursion", "Too deep for the stack",
          "A correct recursion n frames deep, and the loop that computes the same thing.",
          before="Divide and conquer")
_place("recursion", "Too deep for the stack", "josephus-survivor",
       "The recurrence is one line. Write it recursively, run n = 10⁶, read the StackOverflowError — then compute the same values smallest-first in a loop.")
_place("recursion", "Divide and conquer", "closest-pair-points",
       "Trust both halves; the whole algorithm is the strip. Say why each point checks only a handful of neighbours above it.")
_extras("recursion", "unique-paths-count", "kth-symbol-grammar", "gray-code", "ways-to-add-parentheses")

# --- sorting (9 required)
_place("sorting", "Warm up", "rank-transform",
       "Sort a copy, dedupe, binary-search each original value. Compare with leaderboard-ranks: dense ranks versus competition ranks.")
_move("kth-smallest", "sorting", "Extra practice")
_place("sorting", "Quickselect", "moves-to-median",
       "Prove the median is optimal first (moving the target up helps while more values are above it). Then find it with quickselect.")
_add_rung("sorting", "Non-comparison sorts",
          "Sorting without comparing: the value, or one digit of it, is the index.",
          before="Merge sort, reused")
_place("sorting", "Non-comparison sorts", "radix-pass-by-pass",
       "Each pass is a stable counting sort on one digit. Print after every pass and check the invariant: sorted by the last p digits.")
_place("sorting", "Merge sort, reused", "important-reverse-pairs",
       "Count in a separate two-pointer pass before merging — the merge compares a[i] with a[j], not with 2·a[j]. And 2·a[j] needs a long.")
_extras("sorting", "leaderboard-ranks", "custom-sort-string", "h-index")

# --- binary search (14 required)
_place("binary-search", "Core", "min-time-for-trips",
       "The first search on the answer: `enough(T)` is a sum of T / time[i]. Stop the sum at k, or it overflows a long.")
_move("search-rotated-array", "binary-search", "Variations")
_place("binary-search", "Variations", "sqrt-to-six-places",
       "Scale the question until the answer is an integer: ⌊√(n·10¹²)⌋. No doubles anywhere, and the output is exact.")
_add_rung("binary-search", "Maximise the minimum, minimise the maximum",
          "The predicate runs the other way, or the answer is the last true — same loop, one branch changed.",
          before="Extra practice")
_place("binary-search", "Maximise the minimum, minimise the maximum", "max-equal-portions",
       "Last true: `lo = mid` on success, so `mid` must round up. Or find the first failing length and subtract one.")
_move("magnetic-force-between-balls", "binary-search", "Maximise the minimum, minimise the maximum",
      "Place balls greedily left to right inside `ok(d)`. Feasible gaps form a prefix; you want its last element.")
_move("split-array-largest-sum", "binary-search", "Maximise the minimum, minimise the maximum",
      "The mirror image: minimise the largest part. `ok(cap)` = the greedy split needs ≤ k parts, which gets easier as cap grows.")
_add_rung("binary-search", "Count ≤ x over values",
          "The k-th of something too large to list: count how many are ≤ x, and search x.",
          before="Extra practice")
_place("binary-search", "Count ≤ x over values", "nth-divisible-number",
       "count(x) = x/a + x/b − x/lcm. The answer is the smallest x with count ≥ N — never stop early on == N.")
_place("binary-search", "Count ≤ x over values", "kth-in-multiplication-table",
       "Row i holds min(m, x / i) entries ≤ x. The table has 10¹⁰ cells and is never built.")
_extras("binary-search", "peak-of-mountain", "search-insert-position", "count-occurrences-sorted",
        "integer-sqrt", "min-days-for-bouquets", "find-k-closest")

# --- greedy (14 required)
_place("greedy", "Warm up", "cheapest-first-budget",
       "Say the exchange argument before coding: swap any pricier item for a skipped cheaper one and the basket still fits.")
_place("greedy", "Variations", "make-values-unique",
       "Sort, then raise each value only as far as its predecessor forces. Raising further never helps anything after it.")
_add_rung("greedy", "Order by exchange argument",
          "“In what order?” — compare two adjacent items, and sort by whichever order the swap proves is never worse.",
          before="Stretch")
_place("greedy", "Order by exchange argument", "weighted-completion-order",
       "Derive the comparator from the adjacent swap: x first iff t_x·w_y < t_y·w_x. Cross-multiply in long.")
_place("greedy", "Order by exchange argument", "min-max-lateness",
       "Shortest-first is the wrong key. Show that swapping an inverted pair of deadlines never raises the maximum.")
_place("greedy", "Order by exchange argument", "job-deadlines-profit",
       "Profit order, and the LATEST free slot. Then solve it again with a heap of kept profits and compare.")
_extras("greedy", "lemonade-change", "partition-labels", "two-city-scheduling",
        "valid-parenthesis-star", "wiggle-subsequence")

# --- intervals (13 required)
_place("intervals", "Warm up", "covered-length-union",
       "Merge, then add the blocks. `max` on the end, and remember the last block after the loop.")
_place("intervals", "Core", "subtract-interval",
       "Insert-interval turned inside out: keep [a, min(b, x)) and [max(a, y), b) when non-empty. No sort — the input is already ordered.")
_place("intervals", "Variations", "busiest-moment",
       "The ±1 sweep, recording the time whenever the count sets a new record. Pack (time, type) into one long so ends sort first.")
_add_rung("intervals", "When greedy stops working",
          "Weights break every local rule. Keep the sort by end; replace the greedy choice with a max.",
          before="Extra practice")
_place("intervals", "When greedy stops working", "weighted-job-scheduling",
       "best[i] = max(best[i−1], w_i + best[p(i)]), with p(i) an upper bound over the sorted ends. Upper, so back-to-back bookings combine.")
_extras("intervals", "summary-ranges", "remove-covered-intervals", "video-stitching",
        "my-calendar", "min-interval-per-query")


# --- round 2 (batch 49). Every required ladder is at or near its weight band,
# so four of the five join Extra practice; `covered-by-two` takes the one free
# required slot in intervals.
_place("recursion", "Extra practice", "sierpinski-cell",
       "Recurse on the quadrant the cell is in. Then look at which bits each level tested — the answer collapses to `(r & c) == 0`.")
_place("sorting", "Extra practice", "count-range-sums",
       "Subarrays are pairs of prefix sums. Merge-count them, with a *window* of valid partners per left element instead of a single pointer.")
_place("binary-search", "Extra practice", "min-max-after-splits",
       "Search the cap: a crate of weight w needs (w − 1) / x splits. Halving the heaviest crate greedily is the wrong answer — find the counterexample.")
_place("intervals", "Variations", "covered-by-two",
       "The sweep again, measuring the gaps where the count is at least 2. Change the threshold and the same loop gives the union or the intersection.")
_place("greedy", "Extra practice", "patch-to-cover-range",
       "Invariant: every amount below `miss` is payable. A coin ≤ miss extends it; otherwise add a coin worth `miss` and double it.")


_drop_empty_rungs()
