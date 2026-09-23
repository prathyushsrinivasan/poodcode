# DSA Curriculum — the topic list, all 107 covered

Your list, marked against what the app's **DSA Curriculum** (Library tab,
`seeds/dsa_curriculum.json`) teaches. It was **85 taught, 7 partial, 14 absent**
when you handed it over; it is now **8 stages, 46 units,
799 problems** and every line is checked. Stages 3, 4 and 6 have since been
expanded in depth — see `ORDER_SEARCH_ROADMAP.md`, `NUMBERS_BITS_GRIDS_ROADMAP.md` and
`TREES_GRAPHS_ROADMAP.md`.

| Mark | Meaning |
| --- | --- |
| ☑ | **Taught** — the unit has a model, a skeleton, signals and a rung of problems for it |

Your list has 107 lines and **106 distinct topics** — *Tree DP* is written
twice, once under the graph group and once under DP, and it is checked in both
places. Lines in **bold** are the ones that were open and have just been built;
[What changed](#what-changed) has the detail.

---

## The list

☑ Big O — `complexity` (stage 2) — plus a Big-O drill set in every one of the 40 units
☑ Space complexity — `complexity` — recursion stack vs auxiliary array
☑ Arrays — `arrays-first-pass` (stage 1), 19 problems
☑ Strings — `strings` (stage 2), 22 problems
☑ HashMap — `hashing` (stage 2)
☑ HashSet — `hashing`
☑ Sorting — `sorting` (stage 3) — comparators, counting and radix sort, quickselect, merge-counting
☑ Two pointers — `two-pointers` (stage 2), 21 problems
☑ Sliding window — `sliding-window` (stage 2), 21 problems
☑ Prefix sum — `prefix-sums` (stage 2)
☑ Difference array — `prefix-sums` — “Difference arrays and sweeps”
☑ Binary search — `binary-search` (stage 3), 28 problems — lower bound, search on the answer, maximise-the-minimum, count ≤ x
☑ Binary search on answer — `binary-search` — the whole “Variations” rung is built on it
☑ Recursion — `recursion` (stage 3)
☑ Backtracking — `backtracking` (stage 6), 22 problems
☑ Linked list — `linked-lists` (stage 5), 25 problems
☑ Fast/slow pointers — `linked-lists` — cycle detection, middle, k-th from the end
☑ Stack — `stacks` (stage 5)
☑ Queue — `queues-and-deques` (stage 5)
☑ Deque — `queues-and-deques`
☑ Monotonic stack — `stacks` — next greater, spans, contribution counting
☑ Monotonic queue — `queues-and-deques` + `sliding-window`
☑ Heap — `heaps` (stage 5), 23 problems
☑ PriorityQueue — `heaps` — internals, sift up/down, build-it-yourself
☑ Binary tree — `trees` (stage 6), 30 problems
☑ Tree DFS — `trees` — pre/in/post order, bottom-up aggregates
☑ Tree BFS — `trees` — level order, right side view, max width
☑ BST — `bst` (stage 6)
☑ Balanced BST — `bst` — the balance caveat, and the `TreeMap`/`TreeSet` rung
☑ Trie — `tries` (stage 7), 16 problems

☑ Graph representation — `graph-traversal` (stage 6) — adjacency list vs matrix
☑ Directed graphs — `graph-traversal`, `topological-sort`
☑ Undirected graphs — `graph-traversal`, `union-find`
☑ Weighted graphs — `shortest-paths`, `mst`
☑ DFS — `graph-traversal`
☑ BFS — `graph-traversal`
☑ Grid DFS — `graph-traversal` — flood fill; `simulation-and-matrix` for the indexing
☑ Grid BFS — `graph-traversal` — shortest hops on a grid
☑ Multi-source BFS — `graph-traversal` — seed the queue with every source
☑ **0-1 BFS** — `shortest-paths` — a model section, a skeleton, and `min-obstacle-removal`, which was already on the Core rung
☑ Dijkstra — `shortest-paths` (stage 6)
☑ Bellman-Ford — `shortest-paths` — negatives and hop limits
☑ Floyd-Warshall — `shortest-paths` — the “All pairs” rung
☑ DSU — `union-find` (stage 6), 16 problems
☑ Kruskal — `mst` (stage 6)
☑ Prim — `mst`
☑ Topological sort — `topological-sort` (stage 6) — Kahn and DFS colouring
☑ DAG DP — `topological-sort` — relax in topological order
☑ SCC — `advanced-graphs` (stage 8) — Tarjan low-links and Kosaraju
☑ Bridges — `advanced-graphs`
☑ Articulation points — `advanced-graphs`
☑ **LCA** — `trees` (the O(n) recursion), `bst` (the O(h) descent) and **`tree-queries`** for repeated queries on a fixed tree
☑ **Binary lifting** — **`tree-queries`** — the 2^j jump table, used for k-th ancestor, LCA and path distance
☑ **Euler tour** — **`tree-queries`** — tin/tout stamping, so a subtree becomes a contiguous range
☑ Tree diameter — `trees` — two-pass, and the one-pass return-vs-record shape
☑ Tree DP — `trees` — the (take, skip) pair return

☑ DP fundamentals — `dp-1d` (stage 7) — state, transition, order, base case
☑ 1D DP — `dp-1d`, 18 problems
☑ 2D DP — `dp-2d` (stage 7)
☑ Knapsack — `dp-knapsack` (stage 7)
☑ Subset sum — `dp-knapsack`
☑ Coin change — `dp-knapsack` — bounded vs unbounded, and the loop order that separates them
☑ LCS — `dp-2d`
☑ LIS — `dp-1d` — the O(n²) table and the O(n log n) patience version
☑ Edit distance — `dp-2d`
☑ Interval DP — `dp-intervals-states` (stage 7)
☑ Tree DP — `trees` — the (take, skip) pair return
☑ Bitmask DP — `bitmask-dp` (stage 8)
☑ **Digit DP** — **`dp-advanced`** — (position, tight, what the condition needs), over two problems
☑ Game DP — `dp-intervals-states` — score *difference*, not score
☑ **DP optimization** — **`dp-advanced`** — monotonic-deque DP and meet in the middle, with convex-hull trick and divide-and-conquer optimisation named and given their conditions

☑ Greedy — `greedy` (stage 3), 31 problems — including exchange-argument orderings
☑ Interval scheduling — `intervals` (stage 3) — earliest finish time, and weighted scheduling (DP)
☑ Sweep line — `intervals` + `prefix-sums`
☑ Fenwick Tree — `range-queries` (stage 8)
☑ Segment Tree — `range-queries`
☑ **Lazy Segment Tree** — `range-queries` — a model section, `apply`/`push` skeletons, and `range-assign-range-sum`
☑ **Sparse Table** — `range-queries` — a model section, a skeleton, and `sparse-table-range-min`

☑ Bit manipulation — `bit-manipulation` (stage 4), 15 problems
☑ XOR — `bit-manipulation` — self-inverse, prefix XOR, pairing off
☑ Bitmask — `bit-manipulation`, `backtracking`, `bitmask-dp`
☑ Subsets — `bit-manipulation` — enumerate 0 … 2ⁿ−1
☑ Submasks — `bit-manipulation` + `bitmask-dp` — `s = (s - 1) & m`
☑ **Gray code** — **`advanced-bits`** — the reflected construction, `i ^ (i >> 1)`, and the prefix-XOR inverse
☑ **XOR basis** — **`advanced-bits`** — Gaussian elimination over GF(2): maximum, rank, membership, k-th smallest

☑ GCD — `math-number-theory` (stage 4)
☑ LCM — `math-number-theory`
☑ Sieve — `math-number-theory`
☑ Prime factorization — `math-number-theory` — trial division to √n
☑ Modular arithmetic — `math-number-theory` — the “Counting modulo a prime” rung
☑ Fast exponentiation — `math-number-theory` + `recursion`
☑ Modular inverse — `math-number-theory` — Fermat, x^(p−2)
☑ Combinatorics — `math-number-theory` — factorial tables, nCr mod p

☑ KMP — `strings` (the prefix function) + `string-matching` (stage 8)
☑ Z algorithm — `string-matching`
☑ Rolling hash — `string-matching`
☑ **Suffix array** — `string-matching` — construction by doubling, practised by `suffix-array-order`
☑ **LCP** — `string-matching` — the LCP array and Kasai's linear pass, practised by `distinct-substrings-large`

☑ **Computational geometry** — **`geometry`** — a unit built entirely on the integer cross product
☑ **Cross product** — **`geometry`** — sign for orientation, magnitude for area; `turn-directions`
☑ **Line intersection** — **`geometry`** — four orientation signs plus the collinear cases; `count-crossing-segments`
☑ **Convex hull** — **`geometry`** — Andrew's monotone chain; `convex-hull-points`

☑ **Max flow** — **`flows-and-matching`** — Edmonds–Karp, with paired reverse edges
☑ **Min cut** — **`flows-and-matching`** — max-flow min-cut, both directions of the proof; `min-cut-capacity` is stated as a cut and solved as a flow
☑ **Bipartite matching** — **`flows-and-matching`** — augmenting paths, Kuhn, König, and the DAG path-cover reduction

☑ **Amortized analysis** — `complexity` (stage 2) — a model section, a doubling-array trace, two drills, a skeleton, pitfalls and four self-checks
☑ **Randomized algorithms** — **`randomized`** — expected vs amortized vs average, Las Vegas vs Monte Carlo, shuffling, weighted sampling, reservoir sampling, Miller–Rabin

---

## What changed

The gap was not random: with one exception it was the **outer ring** of
competitive programming, which is what the optional stage 8 (*Beyond the Core*)
exists to hold. The seven core stages were already complete, so nothing in them
was reshuffled — stage 8 grew from 4 units to 10, and the one genuinely-core
item went where it belonged.

### One correction to the audit

**0-1 BFS** was marked ◪ “no problem to practise it on”. That was
wrong: `min-obstacle-removal` was already on `shortest-paths`' **Core** rung, and
its editorial teaches 0-1 BFS properly. The real gap was only the unit page,
which named the technique in two tables and never gave it a model section or a
skeleton. Both are now there, with two self-checks — and no new problem was
needed.

### Amortized analysis → `complexity` (stage 2)

The one item that was not stage-8 material. Every later unit already leaned on
it — the monotonic stack's “each element is pushed and popped once”,
union-find's inverse Ackermann, the dynamic array's doubling — and the word
appeared in no unit. It is a *cost* idea, so it went in the cost unit: a model
section, an `ArrayList`-doubling trace showing total-work-÷-calls flattening
out, a skeleton for writing the accounting argument, two Big-O drills, three
pitfalls (including amortized-vs-average) and four self-checks. **No new
problems** — it re-prices problems already solved.

### Stage 8, from 4 units to 10

| # | Unit | | Covers |
| --- | --- | --- | --- |
| 1 | `string-matching` | **extended** | + suffix array (doubling), + LCP array (Kasai) |
| 2 | `range-queries` | **extended** | + sparse table, + lazy propagation, + an Easy on-ramp; weight 1 → 2 |
| 3 | `advanced-graphs` | unchanged | SCC, bridges, articulation points, Euler paths |
| 4 | `bitmask-dp` | unchanged | subsets as state |
| 5 | `tree-queries` | **new** | Euler tour, binary lifting, LCA, path distance |
| 6 | `advanced-bits` | **new** | Gray code, XOR basis |
| 7 | `dp-advanced` | **new** | digit DP, monotonic-deque DP, meet in the middle |
| 8 | `flows-and-matching` | **new** | augmenting paths, Kuhn, Edmonds–Karp, max-flow min-cut, König |
| 9 | `geometry` | **new** | cross product, shoelace, segment intersection, convex hull |
| 10 | `randomized` | **new** | expected vs amortized, Las Vegas vs Monte Carlo, sampling, Miller–Rabin |

### 29 new problems

The curriculum is not a second problem bank — `_check_curriculum` asserts
that every problem it schedules exists in `seeds/problems.json` and is placed
exactly once. So a new unit is **problems first**, each fully authored
(description, constraints, three hints, editorial, Python *and* Java references,
six to nine test cases whose expected output is the Python reference *run*).

| Batch | Problems |
| --- | --- |
| `dsa_more_39.py` | `ancestor-queries`, `kth-ancestor-queries`, `tree-lca-queries`, `tree-path-distance` |
| `dsa_more_40.py` | `gray-code-sequence`, `max-xor-subset`, `count-distinct-xor-values`, `kth-smallest-subset-xor` |
| `dsa_more_41.py` | `count-digit-free-numbers`, `digit-sum-divisible-count`, `min-cost-jump-window`, `subset-sum-closest-below` |
| `dsa_more_42.py` | `assign-all-workers`, `bipartite-max-matching`, `min-cut-capacity`, `min-path-cover-dag` |
| `dsa_more_43.py` | `turn-directions`, `polygon-area-doubled`, `count-crossing-segments`, `convex-hull-points` |
| `dsa_more_44.py` | `weighted-random-picks`, `shuffle-fisher-yates`, `reservoir-sample-stream`, `miller-rabin-primality` |
| `dsa_more_45.py` | `static-range-sums`, `sparse-table-range-min`, `range-assign-range-sum`, `suffix-array-order`, `distinct-substrings-large` |

Bank **653 → 682**; curriculum **40 → 46 units**; reference solution sets
**466 → 495**.

Four new input shapes in `tools/dsa_more_kit3.py`: `tree_q` and `wtree_q` (a
tree reads n − 1 edges, so `m` is not input and cannot be got wrong),
`bipartite` (one number cannot say where the split is) and `larr` (the `arr`
shape reads with `sc.nextInt()`, which silently refuses the 10¹⁸ values
Miller–Rabin needs).

### Judging randomness

A judge cannot check a random answer, so the four `randomized` problems pin the
generator — a fixed LCG with a fixed seed, written into each statement:

```
s = (s * 1103515245 + 12345) mod 2^31,   s starts at 12345,   next() = s
```

The algorithms and the reasoning about them are unchanged; only the coin flips
are reproducible. That is also how you would test randomized code at work, and
the unit says so: inject the generator.

### Also worth knowing

- `range-queries` had **7 problems and opened at Medium**, which trips the
  on-ramp lint (a unit with more than four problems must open Intro or Easy).
  `static-range-sums` is the on-ramp, and it earns its place: it is the baseline
  every other structure in the unit is measured against.
- `count-distinct-substrings` already existed as a **trie** problem, O(n²).
  It was not moved. `distinct-substrings-large` is the same question at
  |s| ≤ 10⁵, where the trie dies, and each problem points at the other.
- Every generator lint still passes unchanged: each problem placed exactly once,
  prerequisites pointing backwards, rungs climbing, optional stages last, every
  unit inside its weight band.
