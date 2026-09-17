# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Where the batched problems (tools/dsa_more_*.py) sit on each unit's ladder.
#
# exec'd by tools/dsa_curriculum.py after the six stage files, in the same
# namespace, so `_UNITS` and `_rung` are defined.
#
# The stage files own each unit's teaching and its original ladder. Problems
# added in batches are placed here instead of being spliced into those files,
# so a batch is one reviewable list rather than a dozen edits scattered across
# 10 000 lines. Placement is still checked by every ladder rule in
# `_check_curriculum`: a problem put on a rung easier than its difficulty makes
# the rungs stop climbing and fails the build.
# ---------------------------------------------------------------------------


def _unit_named(key):
    for u in _UNITS:
        if u["key"] == key:
            return u
    raise AssertionError(f"dsa_placements.py: no unit {key!r}")


def _add_rung(unit, title, purpose, before=None, optional=False):
    """A new rung. A required one goes before the rung titled `before` — or, by
    default, before the first optional rung, so optional rungs stay last. An
    optional one always goes at the end."""
    u = _unit_named(unit)
    assert all(r["title"] != title for r in u["rungs"]), f"{unit}: rung {title!r} already exists"
    at = len(u["rungs"])
    if not optional:
        for i, r in enumerate(u["rungs"]):
            if (before is not None and r["title"] == before) or (before is None and r["optional"]):
                at = i
                break
    u["rungs"].insert(at, _rung(title, purpose, [], optional=optional))


def _place(unit, rung, slug, note=""):
    u = _unit_named(unit)
    for r in u["rungs"]:
        if r["title"] == rung:
            r["slugs"].append(slug)
            if note:
                r["notes"][slug] = note
            return
    raise AssertionError(f"dsa_placements.py: {unit} has no rung {rung!r}")


# ---------------------------------------------------------------- batch 1
_place("two-pointers", "Warm up", "squares-of-sorted-array",
       "The largest square is at one end or the other — so fill the answer from the back.")
_place("two-pointers", "Warm up", "valid-palindrome-alnum",
       "The palindrome check you know, with pointers that skip what does not count. Digits count.")
_place("two-pointers", "Core", "three-sum-count",
       "Fix one element and two-sum the rest. The duplicate skipping is where the bugs are.")
_place("two-pointers", "Variations", "sort-colors",
       "Three regions and one pass. Swapping in from the back does not advance `mid` — find out why.")
_place("sliding-window", "Core", "permutation-in-string",
       "A permutation is equal letter counts, and every candidate has the same length: a fixed window.")
_place("sliding-window", "Core", "longest-repeating-replacement",
       "Validity is `length − top count ≤ k`. Then it is the flips problem wearing a disguise.")
_place("sliding-window", "Variations", "subarray-product-less-k",
       "The count-all-windows shape with a product — and a `k ≤ 1` edge that breaks the naive loop.")


# ---------------------------------------------------------------- batch 2
_place("strings", "Warm up", "longest-palindrome-build",
       "Sounds like search; is counting. Pairs go on the outside and one leftover in the middle.")
_place("strings", "Core", "is-subsequence",
       "Match each character at its earliest chance — the greedy choice is always safe here.")
_place("strings", "Core", "isomorphic-strings",
       "One map is not enough. `ab` → `cc` passes the forward check.")
_place("strings", "Variations", "reverse-words",
       "The reversal is trivial; splitting `\"  a   b \"` into words correctly is the problem.")
_place("strings", "Variations", "string-to-integer",
       "A parser in phases — spaces, one sign, digits, clamp — each stopping where the next begins.")
_place("hashing", "Warm up", "happy-number",
       "A set detects a cycle in any sequence of values: stop at the first repeat.")
_place("hashing", "Warm up", "ransom-note",
       "Positions never matter, so a 26-slot count array is the whole data structure.")
_place("hashing", "Core", "unique-occurrences",
       "Count the values, then put the counts in a set and compare sizes.")
_place("hashing", "Variations", "pairs-with-difference-k",
       "Look up `x + k`. When k is 0 the partner is x itself, and the question changes.")


# ---------------------------------------------------------------- batch 3
_place("prefix-sums", "Warm up", "pivot-index",
       "The total minus the running left sum minus the element is the right sum — no second array.")
_place("prefix-sums", "Core", "contiguous-array",
       "Count 0 as −1 and it becomes a zero-sum question. Store each prefix's FIRST index.")
_place("prefix-sums", "Core", "range-addition",
       "A difference array: two point updates per range, one prefix sum at the end.")
_place("prefix-sums", "Stretch", "subarray-sums-divisible-k",
       "Equal remainders, not equal sums — and Java's `%` is negative for negative sums.")
_place("sorting", "Warm up", "custom-sort-string",
       "A custom order is a rank; with 26 letters, count instead of compare.")
_place("sorting", "Core", "largest-number",
       "No sort key exists, so compare pairs: x before y when x+y beats y+x.")
_place("sorting", "Core", "h-index",
       "Sorted descending, a paper's rank counts the papers at least as good. Then cap at n and count.")
_place("sorting", "Core", "best-meeting-point-line",
       "The median, not the mean. Step the meeting point by one and watch the total change.")
_place("bit-manipulation", "Stretch", "single-number-iii",
       "XOR gives x ^ y; any set bit of it splits the array into two Single Number problems.")


# ---------------------------------------------------------------- batch 4
_place("stacks", "Warm up", "backspace-string-compare",
       "A backspace pops. Then do it again from the back, with a counter instead of a stack.")
_place("stacks", "Core", "simplify-path",
       "Directory names on a stack; `..` pops. `...` is a name — compare whole tokens.")
_place("stacks", "Core", "decode-string",
       "Two stacks save the count and the outer text at each `[`. Counts can have two digits.")
_place("stacks", "Core", "asteroid-collision",
       "The newcomer fights the top of the stack until it loses, ties, or finds nothing to fight.")
_place("stacks", "Stretch", "sum-subarray-minimums",
       "Count each element's contribution. Strict on one side, non-strict on the other, or ties double-count.")
_place("queues-and-deques", "Warm up", "recent-calls",
       "A queue is a window over time: expire from the front, count what is left.")
_place("queues-and-deques", "Core", "first-unique-in-stream",
       "Values stop being unique mid-queue. Leave them there and discard them when they reach the front.")
_place("queues-and-deques", "Core", "jump-game-vi",
       "A DP whose transition is a sliding-window maximum — the monotonic deque again.")
_place("queues-and-deques", "Stretch", "shortest-subarray-at-least-k",
       "Negatives break the two-pointer window. A deque of prefix sums, pruned at both ends, does not break.")


# ---------------------------------------------------------------- batch 5
_place("heaps", "Core", "connect-ropes",
       "Huffman's argument: a rope is paid once per join it is in, so join the two shortest first.")
_place("heaps", "Variations", "furthest-building",
       "Give every climb a ladder provisionally; when they run out, hand the smallest climb back to bricks.")
_place("heaps", "Stretch", "trapping-rain-water-ii",
       "Flood from the border, always from the lowest wall — Dijkstra's invariant with heights.")
_place("design", "Warm up", "parking-system",
       "Name the state, then write each operation as a change to it. Everything harder is this.")
_place("design", "Core", "snapshot-array",
       "Record changes tagged by snapshot, not copies — reading an old version becomes a binary search.")
_place("design", "Variations", "leaderboard-design",
       "A hash map and a sorted multiset, updated together. Two players can share a score.")
_place("design", "Variations", "stock-price-fluctuation",
       "Corrections remove values, so a running max is not enough: a multiset, or heaps with lazy deletion.")


# ---------------------------------------------------------------- batch 6
_place("graph-traversal", "Warm up", "island-perimeter",
       "Looks like a search; is a count. Four sides per cell, minus two per shared side.")
_place("graph-traversal", "Core", "max-area-of-island",
       "The flood fill from Number of Islands, returning how many cells it marked.")
_place("graph-traversal", "Core", "surrounded-regions",
       "Flood from the border and keep what it reaches — one search instead of one per region.")
_place("graph-traversal", "Variations", "pacific-atlantic",
       "Search backwards, uphill, from each ocean at once. The comparison flips with the direction.")
_place("graph-traversal", "Variations", "open-the-lock",
       "An implicit graph: 10⁴ states whose edges are generated, never stored. Dead ends are pre-visited.")
_place("graph-traversal", "Variations", "shortest-bridge",
       "A flood fill to find one island, then a BFS seeded with all of it to measure the gap.")
_place("topological-sort", "Core", "course-order-smallest",
       "Kahn's queue is a policy: a min-heap makes the order lexicographically smallest.")
_place("topological-sort", "Core", "parallel-courses",
       "Kahn's algorithm counted in layers. Each layer is a semester; the count is the longest chain.")
_place("topological-sort", "Core", "eventual-safe-states",
       "Kahn's algorithm on the reversed graph, peeling nodes whose out-degree reaches zero.")
_place("topological-sort", "Stretch", "longest-increasing-path-grid",
       "Strictly increasing moves cannot cycle, so the grid is a DAG. Layers, or memoised DFS.")


# ---------------------------------------------------------------- batch 7
_place("bst", "Core", "range-sum-bst",
       "The order property prunes: a node below the range has a whole left subtree below it too.")
_place("bst", "Core", "bst-min-difference",
       "In-order is sorted order, and in a sorted list the closest pair is adjacent.")
_place("bst", "Variations", "bst-successor",
       "One walk down, remembering the last value larger than k. It is `TreeMap.higherKey`.")
_place("bst", "Variations", "recover-bst",
       "In order, two swapped values leave one or two descents — and where they are names the values.")
_place("shortest-paths", "Core", "count-shortest-paths",
       "Carry a count alongside each distance. Skipping stale heap entries is now a correctness rule.")
_place("shortest-paths", "Core", "min-obstacle-removal",
       "Weights of only 0 and 1: a deque replaces the heap. Plain BFS counts the wrong thing.")
_place("shortest-paths", "Core", "bellman-ford-negative",
       "n − 1 rounds of relaxing every edge, then one more to catch a negative cycle. Guard INF.")
_place("shortest-paths", "Stretch", "swim-in-rising-water",
       "Dijkstra minimising the highest cell instead of the sum — the proof only needed monotone costs.")


# ---------------------------------------------------------------- batch 8
_place("binary-search", "Warm up", "peak-of-mountain",
       "Not sorted, but `a[i] < a[i+1]` is true-then-false. That is all binary search needs.")
_place("binary-search", "Core", "search-rotated-array",
       "One half is always sorted. Ask the range question only on that half.")
_place("binary-search", "Core", "koko-eating-bananas",
       "Binary search on the answer: slow speeds fail, fast ones succeed. Ceiling division in long.")
_place("binary-search", "Variations", "min-days-for-bouquets",
       "Binary search on days, with a greedy scan as the check. `m * k` overflows an int.")
_place("binary-search", "Variations", "split-array-largest-sum",
       "Minimise the maximum by asking whether a cap is achievable — a greedy answers that.")
_place("greedy", "Warm up", "lemonade-change",
       "The only decision is how to change a $20: keep the $5s, they are the flexible bill.")
_place("greedy", "Core", "partition-labels",
       "Each part must reach the last occurrence of every letter in it. It is Merge Intervals in disguise.")
_place("greedy", "Core", "two-city-scheduling",
       "Sort by the cost of switching, a − b — not by either cost on its own.")
_place("greedy", "Variations", "valid-parenthesis-star",
       "Track the range of possible open counts. The clamp at zero is the subtle line.")
_place("greedy", "Stretch", "candy",
       "A two-sided rule, enforced one side per pass, combined with max.")


# ---------------------------------------------------------------- batch 9
_place("intervals", "Warm up", "summary-ranges",
       "Runs of consecutive values, found by comparing neighbours — in long, because the ints reach the extremes.")
_place("intervals", "Core", "remove-covered-intervals",
       "Sort by start, ties by LONGER first; then one running max end decides coverage.")
_place("intervals", "Variations", "my-calendar",
       "Accepted bookings never overlap, so only the two neighbours of a new one can clash.")
_place("intervals", "Variations", "video-stitching",
       "Covering a range with the fewest intervals is Jump Game II over time.")
_place("intervals", "Stretch", "min-interval-per-query",
       "Answer the queries in sorted order: intervals join a heap as they start and leave as they end.")
_place("dp-1d", "Core", "perfect-squares",
       "Coin change with square coins. The largest-square greedy fails on 12.")
_place("dp-1d", "Variations", "house-robber-ii",
       "Break the circle by leaving out the first house or the last one — two linear problems.")
_place("dp-1d", "Variations", "delete-and-earn",
       "Over the values instead of the positions, it is House Robber.")
_place("dp-2d", "Core", "min-path-sum",
       "Right-or-down moves make the grid a DAG; one row of state carries both predecessors.")
_place("dp-2d", "Stretch", "distinct-subsequences",
       "Count by the last choice: skip s[i] or match it. Update the row from the back, as in 0/1 knapsack.")


# ---------------------------------------------------------------- batch 10
_place("arrays-first-pass", "Variations", "leaders-in-array",
       "From the right, 'bigger than everything after it' needs one number: the maximum so far.")
_place("arrays-first-pass", "Variations", "plus-one-digits",
       "The schoolbook carry on a digit array. Only all-9s makes the number longer.")
_place("arrays-first-pass", "Variations", "set-mismatch",
       "Values in 1..n are indices in disguise: a count array finds both answers in one scan.")
_place("complexity", "Core", "pairs-divisible-60",
       "Only the remainder mod 60 matters — count the 60 kinds instead of checking pairs.")
_place("complexity", "Core", "sum-all-subarray-sums",
       "O(n³), O(n²) or O(n) for the same total, depending on whether you count subarrays or contributions.")
_place("complexity", "Stretch", "count-valid-triangles",
       "Sorting turns three inequalities into one; then fix the longest side and count pairs.")
_place("recursion", "Variations", "count-and-say",
       "A recursive definition whose recursion is a straight chain — so a loop computes it.")
_place("recursion", "Variations", "kth-symbol-grammar",
       "Recurse on the index, not the row: every symbol has one parent, and rows halve on the way up.")
_place("recursion", "Variations", "nested-list-depth-sum",
       "A recursive descent parser: one call per bracket, and the depth rides along.")
_place("recursion", "Two calls", "gray-code",
       "Two copies of the smaller answer, one reversed. The seam differs by exactly the new bit.")


# ---------------------------------------------------------------- batch 11
_add_rung("linked-lists", "Extra practice",
          "More pointer surgery, once the unit's ladder is done — optional, and counted only once started.",
          optional=True)
_place("linked-lists", "Extra practice", "remove-list-elements",
       "A dummy head makes deleting the head an ordinary deletion. Do not advance after unlinking.")
_place("linked-lists", "Extra practice", "swap-pairs",
       "Three pointer writes per pair, in an order that never loses the rest of the list.")
_place("linked-lists", "Extra practice", "rotate-list",
       "Close the list into a ring, then cut it. `k` can be two billion — take it mod n.")
_place("linked-lists", "Extra practice", "partition-list",
       "Two appended lists are stable for free. End the second one with null, or it loops.")
_place("linked-lists", "Extra practice", "sort-list",
       "Merge sort is the list's sort: split with slow/fast, merge like two sorted lists.")
_place("trees", "Extra practice", "sum-root-to-leaf",
       "Pass the number built so far down the path; add it only at leaves.")
_place("trees", "Extra practice", "count-good-nodes",
       "The whole path collapses to its maximum, carried down.")
_place("trees", "Extra practice", "max-width-binary-tree",
       "Heap-style positions measure gaps without nulls — normalise per level or they overflow.")
_place("trees", "Extra practice", "house-robber-iii",
       "Tree DP returning two values: this subtree's best with and without its root.")
_place("trees", "Extra practice", "binary-tree-tilt",
       "Return the subtree sum, accumulate the tilt on the side.")


# ---------------------------------------------------------------- batch 12
_place("backtracking", "Variations", "matchsticks-to-square",
       "Backtracking lives or dies by pruning: sort descending, and never try two equal sides.")
_add_rung("backtracking", "Extra practice",
          "More searches with pruning, once the ladder is done — optional, counted only once started.",
          optional=True)
_place("backtracking", "Extra practice", "partition-k-equal-subsets",
       "Matchsticks with k sides — plus a new cut: a failure in an empty bucket fails everywhere.")
_place("backtracking", "Extra practice", "beautiful-arrangement",
       "Check constraints while building, and build the most constrained positions first.")
_place("backtracking", "Extra practice", "unique-permutations-count",
       "Deduplicate the search, not the output: equal values must be used in index order.")
_place("tries", "Core", "map-sum-pairs",
       "Store each subtree's total in its trie node; an overwrite adds only the difference.")
_add_rung("dp-2d", "Extra practice",
          "More two-dimensional states — optional, counted only once started.", optional=True)
_place("dp-2d", "Extra practice", "longest-palindromic-subseq",
       "Interval DP over substrings — or the LCS of the string and its reverse.")
_place("dp-2d", "Extra practice", "maximal-square",
       "\"Largest square ending here\" composes from three neighbours; \"largest anywhere\" does not.")
_place("dp-2d", "Extra practice", "unique-paths-obstacles",
       "An obstacle is a zero in the recurrence, and the zero propagates by itself.")
_add_rung("dp-1d", "Extra practice",
          "More one-dimensional states — optional, counted only once started.", optional=True)
_place("dp-1d", "Extra practice", "stock-with-cooldown",
       "The trading rules are a state machine; the state machine is the DP.")
_place("dp-1d", "Extra practice", "number-of-lis",
       "Count optimal solutions alongside the optimum: better replaces, equal adds.")


# ---------------------------------------------------------------- batch 13
_place("two-pointers", "Core", "max-k-sum-pairs",
       "Two-sum until nothing is left. Every value has one possible partner, so greedy pairing is safe.")
_place("two-pointers", "Variations", "remove-duplicates-sorted-ii",
       "Compare with the kept value two places back, not the read value.")
_place("sliding-window", "Core", "max-points-from-cards",
       "Taking k from the ends leaves a window of n − k. Minimise the window instead.")
_place("sliding-window", "Core", "max-sum-distinct-window",
       "A fixed window that carries value counts alongside its sum.")
_place("sliding-window", "Variations", "count-nice-subarrays",
       "Exactly k = at most k − at most k − 1. Or: Subarray Sum Equals K on a 0/1 array.")
_place("greedy", "Variations", "wiggle-subsequence",
       "Count the turning points. The two-state DP collapses into exactly that.")
_place("binary-search", "Variations", "find-k-closest",
       "Binary search the start of a length-k window — with a signed comparison, not abs.")
_place("strings", "Variations", "zigzag-conversion",
       "Only the row of each character survives the reading. Mind the one-row case.")
_place("stacks", "Core", "remove-k-digits",
       "A monotonic stack is a greedy that can take things back. Trim leftovers from the end.")


# ---------------------------------------------------------------- batch 14
_add_rung("graph-traversal", "Extra practice",
          "More graphs in disguise, once the ladder is done — optional, counted only once started.",
          optional=True)
_place("graph-traversal", "Extra practice", "number-of-enclaves",
       "Surrounded Regions' complement again: flood the border away, count what is left.")
_place("graph-traversal", "Extra practice", "keys-and-rooms",
       "Rooms are nodes, keys are directed edges. Name the graph and it is one traversal.")
_place("graph-traversal", "Extra practice", "as-far-from-land",
       "Multi-source BFS: every land cell starts in the queue, and each water cell meets its nearest.")
_place("graph-traversal", "Extra practice", "find-town-judge",
       "No traversal at all — the answer is a statement about in-degree and out-degree.")
_place("union-find", "Extra practice", "most-stones-removed",
       "Every component can be reduced to one stone, so the answer is stones minus components.")
_add_rung("heaps", "Extra practice",
          "More heap patterns — optional, counted only once started.", optional=True)
_place("heaps", "Extra practice", "kth-smallest-sorted-matrix",
       "A heap of row fronts works; binary search on the value with a staircase count is better.")
_place("heaps", "Extra practice", "seat-reservation-manager",
       "Only returned seats need the heap — the never-used ones are a counter.")
_add_rung("design", "Extra practice",
          "More designs — optional, counted only once started.", optional=True)
_place("design", "Extra practice", "front-middle-back-queue",
       "Two deques and a size invariant make the middle an end.")
_add_rung("intervals", "Extra practice",
          "More interval sweeps — optional, counted only once started.", optional=True)
_place("intervals", "Extra practice", "max-population-year",
       "Half-open lifetimes as +1/−1 events, and a prefix sum over the years.")


# ---------------------------------------------------------------- batch 15
_add_rung("tries", "Extra practice",
          "More prefix structures — optional, counted only once started.", optional=True)
_place("tries", "Extra practice", "count-distinct-substrings",
       "Every substring is a prefix of a suffix; a trie of suffixes creates one node per distinct one.")
_place("tries", "Extra practice", "search-suggestions-system",
       "A sorted list is an implicit trie: each prefix is one contiguous block.")
_add_rung("hashing", "Extra practice",
          "More counting and canonical forms — optional, counted only once started.", optional=True)
_place("hashing", "Extra practice", "bulls-and-cows",
       "Matching with multiplicity is a minimum of counts — after taking the exact matches out.")
_place("hashing", "Extra practice", "longest-harmonious-subseq",
       "A subsequence ignores order, so it is two adjacent values and every copy of each.")
_place("hashing", "Extra practice", "duplicate-subtrees-count",
       "Serialise subtrees into canonical keys; the null markers are what make shapes distinct.")
_place("math-number-theory", "Extra practice", "excel-column-number",
       "Base 26 read left to right — with digits 1 to 26 and no zero.")
_add_rung("bit-manipulation", "Extra practice",
          "More bit-level arithmetic — optional, counted only once started.", optional=True)
_place("bit-manipulation", "Extra practice", "add-binary",
       "Schoolbook addition in base 2. The final carry is the classic bug.")
_add_rung("sliding-window", "Extra practice",
          "More window shapes — optional, counted only once started.", optional=True)
_place("sliding-window", "Extra practice", "min-swaps-group-ones",
       "Fix the target window's length, then its cost is the zeros inside. Wrap with index mod n.")
_add_rung("prefix-sums", "Extra practice",
          "More prefix reasoning — optional, counted only once started.", optional=True)
_place("prefix-sums", "Extra practice", "min-start-value",
       "A constraint on every prefix is a constraint on the lowest prefix.")
_add_rung("two-pointers", "Extra practice",
          "More converging pointers — optional, counted only once started.", optional=True)
_place("two-pointers", "Extra practice", "valid-palindrome-ii",
       "The first mismatch is the only place a deletion helps — and either side might be the one.")


# ---------------------------------------------------------------- batch 16
_place("simulation-and-matrix", "Extra practice", "spiral-matrix-ii",
       "Four shrinking boundaries make the turns implicit — no visited check needed.")
_place("simulation-and-matrix", "Extra practice", "diagonal-traverse",
       "Cells on an anti-diagonal share i + j; alternate which end you read from.")
_place("math-number-theory", "Extra practice", "multiply-strings",
       "Grade-school multiplication where the shift is index arithmetic: i + j + 1.")
_add_rung("sorting", "Extra practice",
          "More orderings — optional, counted only once started.", optional=True)
_place("sorting", "Extra practice", "maximum-gap",
       "Pigeonhole: buckets narrower than the average gap mean the answer lies between buckets.")
_place("sorting", "Extra practice", "sort-by-bits",
       "Two keys in one comparator — or packed into a single int key.")
_add_rung("stacks", "Extra practice",
          "More monotonic stacks — optional, counted only once started.", optional=True)
_place("stacks", "Extra practice", "next-greater-circular",
       "A circle is the array walked twice; push indices only on the first pass.")
_place("stacks", "Extra practice", "pattern-132",
       "Scan from the right: the stack pairs each '3' with its best '2', leaving only the '1' to find.")
_add_rung("binary-search", "Extra practice",
          "More ordered searches — optional, counted only once started.", optional=True)
_place("binary-search", "Extra practice", "search-2d-matrix-ii",
       "Start at the top-right, where every comparison discards a row or a column.")
_add_rung("greedy", "Extra practice",
          "More greedy choices — optional, counted only once started.", optional=True)
_place("greedy", "Extra practice", "max-units-on-truck",
       "Fractional knapsack with unit weights: the best boxes first.")
_add_rung("topological-sort", "Extra practice",
          "More peeling — optional, counted only once started.", optional=True)
_place("topological-sort", "Extra practice", "minimum-height-trees",
       "Peeling leaves shortens every longest path at both ends; the centre is what remains.")


# ---------------------------------------------------------------- batch 17
_add_rung("queues-and-deques", "Extra practice",
          "More queues and deques — optional, counted only once started.", optional=True)
_place("queues-and-deques", "Extra practice", "circular-deque",
       "A ring buffer: fixed storage, moving indices. Head and size, not head and tail.")
_place("queues-and-deques", "Extra practice", "dota2-senate",
       "Turn order across rounds is a queue; re-queue at index + n.")
_add_rung("recursion", "Extra practice",
          "More recursive structure — optional, counted only once started.", optional=True)
_place("recursion", "Extra practice", "ways-to-add-parentheses",
       "Split at the operator applied last; both sides are independent smaller problems.")
_place("recursion", "Extra practice", "find-kth-bit",
       "Answer a point query on a million-character string by following one position down.")
_add_rung("complexity", "Extra practice",
          "More pair counting — optional, counted only once started.", optional=True)
_place("complexity", "Extra practice", "pairs-sum-less-than-target",
       "Sort, then count a whole range of pairs in one step.")
_add_rung("bst", "Extra practice",
          "More ordered-tree walks — optional, counted only once started.", optional=True)
_place("bst", "Extra practice", "two-sum-bst",
       "In-order turns the tree into a sorted array; Two Sum II does the rest.")
_place("bst", "Extra practice", "closest-value-bst",
       "The closest value lies on the search path. State the tie rule explicitly.")
_add_rung("shortest-paths", "Extra practice",
          "More distance questions — optional, counted only once started.", optional=True)
_place("shortest-paths", "Extra practice", "city-fewest-neighbours",
       "All pairs at n = 100: Floyd–Warshall's four lines beat n Dijkstras.")
_add_rung("strings", "Extra practice",
          "More string structure — optional, counted only once started.", optional=True)
_place("strings", "Extra practice", "repeated-substring-pattern",
       "Periodic means rotation-invariant: look for s inside (s + s) trimmed at both ends.")
_place("union-find", "Extra practice", "smallest-string-with-swaps",
       "Allowed swaps permute a connected group freely; sort each group into its positions.")
_place("trees", "Extra practice", "lca-deepest-leaves",
       "Return (depth, LCA) from each subtree; equal depths on both sides make this node the answer.")


# ---------------------------------------------------------------- batch 18
_place("two-pointers", "Extra practice", "three-sum-closest",
       "3Sum's skeleton with a running best instead of a result list; no duplicate-skipping needed.")
_place("hashing", "Extra practice", "valid-sudoku",
       "Twenty-seven sets, one per row, column and box — a cell's box is (r / 3) * 3 + c / 3.")
_place("binary-search", "Extra practice", "median-two-sorted-arrays",
       "Binary-search the cut in the shorter array; the other cut follows from the half size.")
_place("dp-2d", "Extra practice", "maximal-rectangle",
       "Each row turns the grid into a histogram; the largest-rectangle stack does the rest.")
_place("dp-2d", "Extra practice", "burst-balloons",
       "Interval DP on the balloon burst last, so both sides stay independent.")
_place("dp-2d", "Extra practice", "regex-matching",
       "dp[i][j] over suffixes; a star either uses zero copies or consumes one character and stays.")
_place("graph-traversal", "Extra practice", "critical-connections",
       "Tarjan's low-link: an edge is a bridge when the child's subtree cannot climb above it.")
_place("bit-manipulation", "Extra practice", "reverse-bits",
       "Shift out of one end and into the other, thirty-two times.")
_place("trees", "Extra practice", "path-sum-iii",
       "Prefix sums along the root-to-node path, with a count map undone on the way back up.")
_place("dp-1d", "Extra practice", "target-sum",
       "Signs split the array into two groups; count subsets summing to (total + target) / 2.")


# ---------------------------------------------------------------- batch 19
_place("strings", "Extra practice", "longest-palindromic-substring",
       "Enumerate centres, not ends: 2n − 1 starting points, each growing in O(1) per step.")
_place("sorting", "Extra practice", "first-missing-positive",
       "Cyclic sort: every value in 1..n has a home index, so the array is its own hash set.")
_place("stacks", "Extra practice", "basic-calculator",
       "With only + and −, a running sum suffices; the stack saves (result, sign) at each bracket.")
_place("stacks", "Extra practice", "remove-duplicate-letters",
       "A monotonic stack whose pops are vetoed for letters that never appear again.")
_place("binary-search", "Extra practice", "single-element-sorted-array",
       "No target to compare against — search for where 'the pair at this even index is intact' turns false.")
_place("sliding-window", "Extra practice", "longest-turbulent-subarray",
       "One running length per direction of the last step; each extends the other.")
_place("greedy", "Extra practice", "queue-reconstruction-by-height",
       "Tallest first, so every later insert is invisible to the counts already satisfied.")
_place("shortest-paths", "Extra practice", "minimum-knight-moves",
       "Unweighted shortest path on an implicit, infinite graph — BFS once the search space is bounded.")


# ---------------------------------------------------------------- batch 20
_place("dp-1d", "Extra practice", "min-cost-tickets",
       "Decide the last pass bought; it looks back 1, 7 or 30 days to a smaller calendar.")
_place("dp-2d", "Extra practice", "min-insertions-palindrome",
       "Interval DP decides at the two ends — or: n minus the longest palindromic subsequence.")
_place("binary-search", "Extra practice", "kth-smallest-pair-distance",
       "Selecting the k-th of n² values is hard; counting those ≤ d is one two-pointer pass.")
_place("greedy", "Extra practice", "reduce-array-size-half",
       "Every choice costs one, so take the largest counts first; an exchange argument proves it.")
_place("bit-manipulation", "Extra practice", "sum-two-integers-bits",
       "XOR is addition without carries; AND shifted left is the carries. Repeat until none remain.")
_place("math-number-theory", "Extra practice", "excel-column-title",
       "Base 26 with digits 1..26 and no zero: subtract one before each remainder.")
_place("math-number-theory", "Extra practice", "nth-digit",
       "Skip whole blocks of equal-length numbers with arithmetic, then index into one number.")
_place("topological-sort", "Extra practice", "longest-path-dag",
       "A topological order is a DP order: every predecessor's best is final before it is used.")
_place("prefix-sums", "Extra practice", "longest-subarray-sum-k",
       "Store the earliest index of each prefix sum — the farthest left a match can start.")
_place("bst", "Extra practice", "bst-from-preorder",
       "The values mark where each subtree ends; recurse with an upper bound and emit postorder.")


# ---------------------------------------------------------------- batch 21
_place("dp-1d", "Extra practice", "max-sum-circular-subarray",
       "A wrapped subarray drops a contiguous middle: total minus the minimum subarray.")
_place("dp-2d", "Extra practice", "longest-common-substring",
       "LCS's table with a reset on mismatch; the answer is the best cell, not the corner.")
_place("two-pointers", "Extra practice", "next-permutation",
       "Change the rightmost position that can grow, by the least amount; reverse the suffix.")
_place("hashing", "Extra practice", "majority-element-ii",
       "Boyer–Moore with two slots cancels triples; a second counting pass confirms.")
_place("stacks", "Extra practice", "car-fleet",
       "From the front, arrival times that matter only increase — a monotonic stack reduced to its top.")
_place("sorting", "Extra practice", "count-inversions",
       "Merge sort counts every cross-half inversion at the moment it merges.")
_place("greedy", "Extra practice", "hand-of-straights",
       "The smallest card is forced to start a group, and so is every card in that group.")
_place("trees", "Extra practice", "all-nodes-distance-k",
       "Add parent pointers and a tree becomes an undirected graph; BFS k levels.")
_place("heaps", "Extra practice", "sliding-window-median",
       "The running median's two halves, with deletion as elements leave the window.")
_place("queues-and-deques", "Extra practice", "constrained-subsequence-sum",
       "A DP whose transition is a sliding-window maximum — answered by a monotonic deque.")
_place("intervals", "Extra practice", "days-without-meetings",
       "Merge, then count gaps in O(1) each — the calendar size never matters.")


# ---------------------------------------------------------------- batch 22
_place("tries", "Extra practice", "word-search-ii",
       "Many patterns, one board walk: the trie shares prefixes and prunes dead paths.")
_place("tries", "Extra practice", "short-encoding-of-words",
       "Reverse the words and suffixes become prefixes; only words ending at leaves pay.")
_place("tries", "Extra practice", "concatenated-words",
       "Word Break per word, with the dictionary built shortest-first so a word never uses itself.")
_place("dp-1d", "Extra practice", "longest-string-chain",
       "Generate the L predecessors of each word instead of testing all pairs.")
_place("prefix-sums", "Extra practice", "range-sum-2d",
       "Inclusion–exclusion: the corner block minus two strips plus their overlap.")
_place("prefix-sums", "Extra practice", "count-odd-sum-subarrays",
       "Only parity matters, so the prefix-sum map collapses to two counters.")
_place("topological-sort", "Extra practice", "largest-color-value",
       "Twenty-six longest paths in one topological pass; leftover nodes reveal a cycle.")
_place("union-find", "Extra practice", "remove-max-edges-traversable",
       "Shared edges first fill both spanning forests at once; private edges fill the gaps.")
_place("shortest-paths", "Extra practice", "cheapest-trip-with-discounts",
       "Dijkstra over (city, discounts used): what the greedy would forget goes into the state.")
_place("sliding-window", "Extra practice", "substring-concatenation-words",
       "Word-length chunks at each of L offsets turn a string into token windows.")


# ---------------------------------------------------------------- batch 23
_place("bit-manipulation", "Extra practice", "hamming-distance",
       "XOR marks where two numbers differ; v & (v − 1) counts the marks.")
_place("bit-manipulation", "Extra practice", "bitwise-and-of-range",
       "Only the common binary prefix of the two ends survives counting between them.")
_place("bit-manipulation", "Extra practice", "single-number-ii",
       "XOR cancels pairs; summing each bit column modulo 3 cancels triples.")
_place("bit-manipulation", "Extra practice", "max-product-word-lengths",
       "A set of 26 letters is a 26-bit integer, and disjointness is one AND.")
_place("recursion", "Extra practice", "permutation-sequence",
       "Each first digit owns (n − 1)! permutations, so division skips whole recursive branches.")
_place("recursion", "Extra practice", "predict-the-winner",
       "Minimax as a single score difference: your pick minus the opponent's best reply.")
_place("bst", "Extra practice", "verify-preorder-bst",
       "Replay the preorder with a stack of open ancestors; a right turn raises the floor.")
_place("bst", "Extra practice", "unique-bst-count",
       "Fix the root and the two sides are independent: counts multiply, roots add.")
_place("bst", "Extra practice", "largest-bst-subtree",
       "Children report (is BST, min, max, size) so each parent decides in O(1).")
_place("queues-and-deques", "Extra practice", "first-negative-in-window",
       "A queue of candidates expired from the front — the monotonic deque without back pops.")


# ---------------------------------------------------------------- batch 24
_add_rung("branching", "Extra practice",
          "More decisions — optional, counted only once started.", optional=True)
_place("branching", "Extra practice", "triangle-type",
       "Order the branches from most specific to least; the impossible case overrides all.")
_add_rung("loops-and-digits", "Extra practice",
          "More digit loops — optional, counted only once started.", optional=True)
_place("loops-and-digits", "Extra practice", "self-dividing-numbers",
       "Peel digits with % 10, and check for a zero before dividing by it.")
_place("simulation-and-matrix", "Extra practice", "lucky-numbers-matrix",
       "Row minima and column maxima once each, instead of rescanning per cell.")
_place("simulation-and-matrix", "Extra practice", "image-smoother",
       "The 3 × 3 neighbourhood loop with bounds checks, writing to a fresh matrix.")
_place("simulation-and-matrix", "Extra practice", "valid-tic-tac-toe",
       "Check invariants of turns and wins instead of replaying every game.")
_place("complexity", "Extra practice", "number-of-good-pairs",
       "Count each pair at its later index: billions of pairs in one pass.")
_place("complexity", "Extra practice", "sum-subarray-ranges",
       "Per-element contributions replace an O(n²) sweep over subarrays.")
_place("queues-and-deques", "Extra practice", "reveal-cards-increasing",
       "Run the reveal on positions, then write the sorted cards into them.")
_place("math-number-theory", "Extra practice", "count-good-numbers",
       "Independent positions multiply; square-and-multiply handles n = 10^15.")
_place("math-number-theory", "Extra practice", "fraction-to-recurring-decimal",
       "Long division has one piece of state — the remainder — so a repeat marks the period.")


# ---------------------------------------------------------------- batch 25
_place("design", "Extra practice", "exam-room",
       "Only the ends and gap midpoints can be optimal; a sorted set scans them left to right.")
_place("heaps", "Extra practice", "single-threaded-cpu",
       "Arrivals sorted by time feed a heap of ready work; jump the clock when idle.")
_place("graph-traversal", "Extra practice", "all-paths-source-target",
       "Enumerating paths in a DAG: a path list, no visited set, and sorted neighbours for sorted output.")
_place("graph-traversal", "Extra practice", "number-of-closed-islands",
       "Sink everything that touches the border, then count islands as usual.")
_place("backtracking", "Extra practice", "letter-case-permutation",
       "A binary decision per letter; trying uppercase first yields sorted output.")
_place("backtracking", "Extra practice", "combination-sum-iii",
       "Increasing digits prevent duplicates; a sorted loop breaks at the first overshoot.")
_place("intervals", "Extra practice", "meeting-rooms-iii",
       "Free rooms by number, busy rooms by end time: two heaps for two orders.")
_place("greedy", "Extra practice", "min-deletions-unique-frequencies",
       "Resolve each frequency collision with the smallest possible decrease.")
_place("strings", "Extra practice", "longest-happy-prefix",
       "The KMP prefix function falls back to borders of borders, in linear total time.")
_place("two-pointers", "Extra practice", "four-sum-count",
       "k-Sum is k − 2 loops around Two Sum, with duplicate skipping at every level.")


# ---------------------------------------------------------------- batch 26
_place("dp-2d", "Extra practice", "dungeon-game",
       "Forward DP needs two numbers per cell; backward DP needs one — the health required from here.")
_place("dp-2d", "Extra practice", "count-square-submatrices",
       "The largest square ending at a cell is also the number of squares ending there.")
_place("binary-search", "Extra practice", "magnetic-force-between-balls",
       "Maximise a minimum gap: binary search the gap, test it with a greedy placement.")
_place("sliding-window", "Extra practice", "min-operations-reduce-x",
       "Removing both ends is keeping a middle; find the longest window summing to total − x.")
_place("hashing", "Extra practice", "word-pattern",
       "A bijection needs consistency in both directions — two maps.")
_place("stacks", "Extra practice", "score-of-parentheses",
       "The stack of partial scores collapses to a depth counter: each '()' is worth 2^depth.")
_place("design", "Extra practice", "authentication-manager",
       "Increasing timestamps make insertion order the expiry order.")
_place("intervals", "Extra practice", "max-events-attended",
       "Earliest deadline first: each day, attend the open event that closes soonest.")
_place("simulation-and-matrix", "Extra practice", "robot-bounded-in-circle",
       "Judge an infinite repetition by one period's shift and rotation.")
_place("graph-traversal", "Extra practice", "jump-game-iii",
       "An array with jump rules is an implicit graph; the visited array ends the cycles.")
_place("union-find", "Extra practice", "min-swaps-couples",
       "Swaps needed = couples − cycles; union-find counts the cycles.")
_place("heaps", "Extra practice", "kth-smallest-prime-fraction",
       "Each denominator is a sorted row; a heap merges the rows to the k-th element.")


# ---------------------------------------------------------------- batch 27
_place("linked-lists", "Extra practice", "insertion-sort-list",
       "A dummy head makes every splice the same, including insertion before the first node.")
_place("linked-lists", "Extra practice", "delete-middle-node",
       "Give the fast pointer a head start so slow stops on the predecessor.")
_place("linked-lists", "Extra practice", "double-number-list",
       "A doubling carry depends only on the next digit, so no reversal is needed.")
_place("tries", "Extra practice", "maximum-xor-with-element",
       "Offline queries sorted by limit turn a filter into a stream of trie inserts.")
_place("union-find", "Extra practice", "count-unreachable-pairs",
       "Pairs across components: each size times the nodes counted before it.")
_place("dp-1d", "Extra practice", "knight-dialer",
       "The history collapses into ten counts — one per digit the knight stands on.")
_place("dp-1d", "Extra practice", "domino-tromino-tiling",
       "Ragged edges get their own state: flat boundary and one-cell protrusion.")
_place("greedy", "Extra practice", "broken-calculator",
       "Backwards, every choice is forced: halve when even, add one when odd.")
_place("graph-traversal", "Extra practice", "min-reorder-roads",
       "Traverse the tree undirected, carrying each road's real direction as a tag.")
_place("shortest-paths", "Extra practice", "reachable-nodes-subdivided",
       "Dijkstra on the compressed graph, then count what leftover moves reach inside each edge.")


# ---------------------------------------------------------------- batch 28
_place("stacks", "Extra practice", "validate-stack-sequences",
       "Simulate the stack and pop greedily: waiting only buries the value that must come next.")
_place("stacks", "Extra practice", "remove-adjacent-duplicates-k",
       "Stack runs, not characters: (letter, count) entries make chain reactions free.")
_place("dp-2d", "Extra practice", "min-falling-path-sum",
       "Three predecessors instead of two; the rolling row is unchanged.")
_place("dp-2d", "Extra practice", "min-ascii-delete-sum",
       "Edit distance with weighted deletions — same table, different costs.")
_place("backtracking", "Extra practice", "subsets-ii",
       "Skip a duplicate at the same decision level, but allow it deeper.")
_place("backtracking", "Extra practice", "unique-paths-iii",
       "Hamiltonian paths on a tiny grid: DFS with a count of cells still to cover.")
_place("math-number-theory", "Extra practice", "smallest-repunit-divisible-by-k",
       "Carry only the remainder; k states mean a repeat within k steps proves 'never'.")
_place("math-number-theory", "Extra practice", "consecutive-numbers-sum",
       "Fix the run length — at most √(2n) of them — and the start follows by division.")
_place("sorting", "Extra practice", "relative-sort-array",
       "Small values: a counting array replaces the comparator.")
_place("two-pointers", "Extra practice", "num-subsequences-sum-condition",
       "Fix the minimum; any subset of the allowed range joins it — a power of two.")
_place("hashing", "Extra practice", "longest-palindrome-two-letter",
       "Pair each word with its reverse; one self-symmetric word may take the centre.")
_place("hashing", "Extra practice", "find-players-zero-one-losses",
       "Register every player who appears, not just those with losses to count.")


# ---------------------------------------------------------------- batch 29
_place("heaps", "Extra practice", "k-weakest-rows",
       "Tie-breaks belong in the key; a bounded max-heap keeps the k smallest.")
_place("heaps", "Extra practice", "process-tasks-using-servers",
       "Free servers by weight, busy servers by time — two heaps and a clock that jumps.")
_place("greedy", "Extra practice", "bag-of-tokens",
       "Equal rewards either way: spend the cheapest, trade away the dearest.")
_place("greedy", "Extra practice", "min-taps-to-water-garden",
       "Clamp taps to intervals, store the furthest reach per start, and run Jump Game II.")
_place("sliding-window", "Extra practice", "longest-ones-after-deleting",
       "A mandatory deletion becomes a window with at most one zero, counted one short.")
_place("binary-search", "Extra practice", "find-min-rotated-duplicates",
       "When the comparison is uninformative, discard one provably redundant element.")
_place("prefix-sums", "Extra practice", "ways-to-split-array",
       "Left plus right is the total: one running sum answers both sides.")
_place("recursion", "Extra practice", "elimination-game",
       "Survivors form an arithmetic sequence; halve the problem with head, step and count.")
_place("bst", "Extra practice", "bst-floor-ceil",
       "The search path's last right turn is the floor and its last left turn the ceiling.")
_place("queues-and-deques", "Extra practice", "time-to-buy-tickets",
       "Count each person's purchases in a round-robin instead of simulating 10^14 turns.")
_place("intervals", "Extra practice", "data-stream-disjoint-intervals",
       "Keep the intervals themselves and repair at most two neighbours per insert.")
_place("tries", "Extra practice", "sum-of-prefix-scores",
       "Count words passing through each trie node; a word's path visits all its prefixes.")


# ---------------------------------------------------------------- batch 30
_add_rung("io-and-arithmetic", "Extra practice",
          "More arithmetic — optional, counted only once started.", optional=True)
_place("io-and-arithmetic", "Extra practice", "floor-division-and-modulo",
       "Truncating versus floor division: the bug appears exactly when negatives meet / and %.")
_place("branching", "Extra practice", "quadrant-of-point",
       "Boundary cases first, so the general branches can assume non-zero coordinates.")
_place("loops-and-digits", "Extra practice", "strong-number",
       "Ten possible digits, so precompute their factorials once.")
_add_rung("arrays-first-pass", "Extra practice",
          "More single passes — optional, counted only once started.", optional=True)
_place("arrays-first-pass", "Extra practice", "even-digit-numbers",
       "A tiny inner loop per element keeps the scan effectively linear.")
_place("arrays-first-pass", "Extra practice", "check-rotated-sorted",
       "Describe every rotation instead of searching for one: at most one cyclic drop.")
_place("arrays-first-pass", "Extra practice", "max-ascending-subarray-sum",
       "A running sum that resets when the order breaks.")
_place("graph-traversal", "Extra practice", "nearest-exit-maze",
       "BFS dequeues in distance order, so the first exit found is a nearest one.")
_place("simulation-and-matrix", "Extra practice", "spiral-matrix-iii",
       "Walk the ideal spiral and filter out positions outside the grid.")
_place("design", "Extra practice", "number-container-system",
       "A reverse index kept consistent: remove the stale entry before adding the new one.")
_place("shortest-paths", "Extra practice", "min-time-visit-cell-grid",
       "Waiting costs two seconds per bounce, so Dijkstra adjusts arrival times by parity.")
_place("dp-1d", "Extra practice", "solving-questions-brainpower",
       "Take-or-skip where taking jumps ahead: fill the DP from the back.")
_place("dp-1d", "Extra practice", "longest-arith-subseq-difference",
       "The predecessor's value is fixed, so a map lookup replaces LIS's inner loop.")


# ---------------------------------------------------------------- batch 31
_place("complexity", "Extra practice", "sum-odd-length-subarrays",
       "Swap the order of summation: count how many odd-length subarrays hold each element.")
_place("hashing", "Extra practice", "maximum-number-of-balloons",
       "A bottleneck is the minimum of supply divided by demand, letter by letter.")
_place("strings", "Extra practice", "shortest-palindrome",
       "A palindromic prefix is a border of s + '#' + reverse(s) — KMP finds the longest.")
_place("strings", "Extra practice", "count-binary-substrings",
       "Only run lengths matter: each adjacent pair of runs adds min(left, right).")
_place("sliding-window", "Extra practice", "count-subarrays-fixed-bounds",
       "Count by right end using the last minK, last maxK and last out-of-range index.")
_place("binary-search", "Extra practice", "search-rotated-duplicates",
       "Only the all-equal triple hides the sorted half; shrink both ends just then.")
_place("binary-search", "Extra practice", "kth-missing-positive",
       "Binary search the monotone count of missing numbers, a[i] − (i + 1).")
_place("stacks", "Extra practice", "min-add-parentheses-valid",
       "Unmatched ')' and unmatched '(' are independent; the stack shrinks to a counter.")
_place("design", "Extra practice", "smallest-infinite-set",
       "An infinite set as a counter for the untouched tail plus a sorted set of returns.")
_place("linked-lists", "Extra practice", "remove-nodes-greater-right",
       "Reverse to scan right-to-left with a running maximum, then reverse back.")
_place("trees", "Extra practice", "cousins-in-binary-tree",
       "Carry parent and depth down the traversal; cousins match on one and differ on the other.")
_place("dp-1d", "Extra practice", "last-stone-weight-ii",
       "Any smashing order is a split into two groups; minimise the difference with subset sum.")


# ---------------------------------------------------------------- batch 32
_place("hashing", "Extra practice", "jewels-and-stones",
       "Build the membership table once; every stone is then an O(1) question.")
_place("strings", "Extra practice", "rotate-string",
       "Every rotation of s is a window of s + s — doubling unwraps the circle.")
_place("two-pointers", "Extra practice", "reverse-vowels",
       "Converging pointers that skip positions not taking part in the reversal.")
_place("prefix-sums", "Extra practice", "find-highest-altitude",
       "Do not forget the empty prefix: the trip starts at altitude 0.")
_place("bit-manipulation", "Extra practice", "xor-queries-subarray",
       "XOR is its own inverse, so prefix XOR answers range queries like prefix sums.")
_place("bit-manipulation", "Extra practice", "number-complement",
       "A mask exactly as wide as the number flips only its meaningful bits.")
_place("heaps", "Extra practice", "max-product-after-k-increments",
       "Greedy by marginal gain: each increment goes to the current minimum.")
_place("trees", "Extra practice", "maximum-level-sum",
       "Drain the BFS queue one level at a time; start the best sum below any possible sum.")
_place("backtracking", "Extra practice", "max-length-unique-concatenation",
       "Subsets of words and sets of letters, both as bitmasks.")
_place("topological-sort", "Extra practice", "min-vertices-reach-all",
       "In a DAG the sources are forced and sufficient — the answer is an in-degree count.")
_place("union-find", "Extra practice", "similar-string-groups",
       "Similarity is not transitive; its closure is connected components.")
_place("greedy", "Extra practice", "maximum-swap",
       "Fix the most significant improvable digit, swapping with the last occurrence of the best one.")


# ---------------------------------------------------------------- batch 33
_place("recursion", "Extra practice", "tribonacci",
       "A recurrence with a fixed look-back needs only a fixed window of variables.")
_place("math-number-theory", "Extra practice", "sum-of-powers-of-three",
       "Distinct powers of three are base 3 with digits 0 and 1 only.")
_place("trees", "Extra practice", "sum-of-left-leaves",
       "'Left' is known to the parent, 'leaf' to the child — check from the parent.")
_place("backtracking", "Extra practice", "splitting-string-descending",
       "After the first cut every value is forced; only leading zeros leave a choice.")
_place("prefix-sums", "Extra practice", "left-right-sum-differences",
       "Left, the element and right make the total — one running sum is enough.")
_place("two-pointers", "Extra practice", "merge-strings-alternately",
       "One index over the longer length, with a bounds check per string.")
_place("greedy", "Extra practice", "min-cost-move-chips",
       "Free moves preserve parity; pay only for the smaller parity class.")
_place("binary-search", "Extra practice", "house-robber-iv",
       "Minimise a maximum: binary search the capability with a greedy feasibility check.")


# ---------------------------------------------------------------- batch 34
_place("recursion", "Extra practice", "pascal-triangle-row",
       "Update one row in place, right to left, so each old value is read before it is overwritten.")
_place("math-number-theory", "Extra practice", "bulb-switcher",
       "A bulb's final state is the parity of its divisor count — odd only for perfect squares.")
_place("intervals", "Extra practice", "teemo-attacking",
       "Sorted equal-length intervals overlap only with neighbours: sum min(duration, gap).")
_place("greedy", "Extra practice", "assign-cookies",
       "Smallest sufficient cookie for the least greedy child, justified by exchange.")
_place("arrays-first-pass", "Extra practice", "can-place-flowers",
       "Plant at the earliest valid plot; edges count as empty neighbours.")
_place("arrays-first-pass", "Extra practice", "third-maximum",
       "Three slots of distinct maxima, with a sentinel outside the int range.")
_place("greedy", "Extra practice", "partition-string-unique",
       "Cut only when a letter repeats; the rule is hereditary, so longest pieces are safe.")
_place("stacks", "Extra practice", "baseball-game",
       "'Cancel the latest' and 'read the latest two' are a stack's access pattern.")
_place("sorting", "Extra practice", "height-checker",
       "Counting sort over a tiny value range replays the expected order.")
_place("sliding-window", "Extra practice", "count-good-substrings",
       "A window of three is checked directly; the count-based window generalises it.")
