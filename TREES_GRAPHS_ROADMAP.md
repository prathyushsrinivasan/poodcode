# Trees & Graphs — expansion roadmap

Stage 6 of the DSA Curriculum (`tools/dsa_s6_hierarchies.py`): **Binary Trees →
Binary Search Trees → Backtracking → Graph Traversal → Topological Sort →
Union-Find → Minimum Spanning Trees → Weighted Shortest Paths**. 8 units, 142
problems as of SEED_VERSION 15.

## Audit: where the stage stands

Stages 3 and 4 each went through a depth round and a help round (see
`ORDER_SEARCH_ROADMAP.md`, `NUMBERS_BITS_GRIDS_ROADMAP.md`). Stage 6 — the
conceptual centre of the course, and the stage with the most units — had
neither.

| Layer | Stage 4 (after its round) | Stage 6 today |
| --- | --- | --- |
| Stage router (`_route`) | 17 rows | **none** |
| Stage cheat sheet | yes | **none** |
| Loop invariant (`_inv`) | 3 / 3 | **0 / 8** |
| Variant family (`_var`) | 3 / 3 | **0 / 8** |
| Slow → fast rewrites (`_rw`) | 3 / 3 | **0 / 8** |
| Internals | 3 / 3 | 1 / 8 (`trees`) |
| Build it from scratch | 3 / 3 | 1 / 8 (`union-find`) |
| Worked traces | 4–6 each | 1–2 each |
| Big-O drills | 8 each | 5 each |
| Spot-the-bug quizzes | 6 each | **0** |
| Stuck triage | 6 each | **0** |
| Edge cases | 10 each | **0** |
| Worked solution | 1 each | **0** |
| Interactive lab | 3 / 3 | **0 / 8** |
| Work-it-out cards | 11–12 each | **0** |

Other gaps found while reading the units:

- **Trees** has no vertical/boundary views, no rebuild from post-order, no
  in-place flattening, no top-down "carry min and max" problem, no path
  *listing* (backtracking on a tree), and nothing past the (take, skip) pair —
  no **rerooting** and no greedy tree cover.
- **BSTs** never delete, never build a balanced tree from sorted data, never
  trim by a range, never merge two trees, and never handle duplicates.
- **Backtracking** has no Intro on-ramp, no partition-into-k search, no
  constraint colouring, and no problem where the search has to be cached or
  counted over a string split with operators.
- **Graph traversal** has a one-problem stretch rung, and nothing on BFS over
  an *augmented state* (cell + keys, cell + walls broken) — the idea behind
  half of the hard BFS problems.
- **Topological sort** never asks whether the order is unique, never counts
  paths in a DAG, never schedules with durations (the critical path), and never
  prints per-node levels.
- **Union-find** has one Variations problem and nothing on the three ideas
  that make it more than a component counter: **online** grids, **weighted /
  parity** DSU and **offline** queries sorted by a threshold.
- **MST** is four problems with no on-ramp, no virtual-node trick, no forced
  edge and no bottleneck (minimax) path.
- **Shortest paths** never reconstructs a path, never runs multi-source
  Dijkstra, never *reports* a negative cycle, never maximises a bottleneck and
  never finds a second-shortest path.

## New features (generic fields, authored for this stage first)

1. **Tree lab** (`_lab("tree", …)`, fields `tree`, `value`). Type a tree in
   the level-order encoding every problem uses; the page draws it and shows,
   live: pre/in/post/level order, height, size, leaves, diameter, whether it is
   a valid BST (and the first node that breaks the range, with the range it
   broke), whether it is balanced, and the descent path an insert or search for
   `value` would take. Click a node: its depth, height, subtree size, allowed
   BST interval and root path.
2. **Graph lab** (`_lab("graph", …)`, fields `n`, `edges`, `directed`,
   `source`, `algo`). Type an edge list (`u v` or `u v w`); the page draws the
   graph on a circle and runs one of **BFS, DFS, Kahn, union-find, Kruskal,
   Prim, Dijkstra, Bellman-Ford** — with a **step scrubber**: drag through the
   algorithm's events and see the queue / stack / heap / parent array and the
   highlighted edges at that moment. One lab, reused by the six graph units with
   different presets.
3. **Search lab** (`_lab("search", …)`, fields `items`, `k`, `target`,
   `mode`). Subsets, k-combinations, permutations or combination-sum over the
   typed items: the event log (choose / explore / undo / emit / prune), the
   answers, and **the number of calls with and without pruning**, so "pruning is
   the whole game" is a number rather than a claim.
4. **"Model it" quizzes** — a third quiz kind, `model`, beside `bug` and
   `predict`. A word problem is given; the options are graph models ("nodes are
   cells, edges are king moves, BFS") and exactly one is right. Recognising the
   graph in a story is the skill the graph units assume and never drill.
5. **Work-it-out cards** for every unit, every answer **computed by running
   the algorithm** in the authoring file rather than typed by hand — an
   inorder, a BFS distance, a topological order, a DSU parent array, an MST
   weight, a Dijkstra distance.

All go through the four layers (generator helper → lint → `models.rs` →
`types.ts` → UI), with Rust mirrors of the lints.

## The list

### A. Stage level
1. **Stage router**: ~20 `_route` rows with `not_when` near misses (tree
   recursion vs level BFS; BST descent vs full traversal; subsets vs
   permutations vs "count only" DP; BFS vs Dijkstra vs 0-1 BFS; union-find vs
   DFS for connectivity; Kahn vs DFS colouring; Kruskal vs Prim; Dijkstra vs
   Bellman-Ford vs Floyd).
2. **Stage cheat sheet**: every template on one page, the bugs that fail hidden
   tests, and the costs to quote.
3. **Lint coverage**: all eight units into `_NEEDS_INVARIANT`,
   `_NEEDS_VARIANTS`, `_NEEDS_REWRITES`, `_NEEDS_INTERNALS`, `_NEEDS_BUILD_IT`,
   `_NEEDS_HELP`, `_NEEDS_LAB`, `_NEEDS_DRILLS`, mirrored in
   `verify_dsa_curriculum.rs`.

### B. Binary trees
4. **Invariant**: structural induction — "the call returns the right answer
   for the subtree it was given", with `null` as the base and the combine step
   as the maintenance; plus BFS's "the queue holds exactly one level".
5. **Variants** (≥ 10): bottom-up aggregate, top-down parameter, return one /
   record another, pair recursion, level BFS, column/vertical keys, rebuild from
   two orders, serialise with nulls, rerooting, greedy post-order cover,
   iterative traversal with an explicit stack, Morris traversal.
6. **Rewrites**: height recomputed per node (O(n²) balance check) → one pass
   with −1; list-then-scan diameter → return/record; recursive → explicit
   stack; per-root distance sums (O(n²)) → rerooting; indexOf in the rebuild →
   a map.
7. **Build it**: a `Trees` toolkit (build from level order, serialise, the four
   orders recursively and iteratively, height, diameter), property-tested.
8. **Traces**: iterative in-order stack, rerooting's two passes, the camera
   states bubbling up.
9. **New problems**: `vertical-order-tree` (M), `leaf-similar-trees` (E),
   `tree-postorder-inorder` (M), `flatten-tree-to-list` (M),
   `max-ancestor-difference` (M), `path-sum-list` (M), `boundary-of-tree` (M),
   `sum-of-distances-tree` (H), `tree-cameras` (H).
10. New rungs **Views and orders**, **Top-down and paths**, **Whole-tree
    answers** (optional).

### C. Binary search trees
11. **Invariant**: every node carries an open interval `(lo, hi)` and its value
    lies in it; descending left sets `hi`, right sets `lo`.
12. **Variants**: search/insert, delete (three cases), range-pruned walk,
    validate by bounds, validate by in-order, k-th by in-order, split point LCA,
    iterator, build balanced from sorted, trim, merge by two iterators,
    duplicates by count.
13. **Rewrites**: full traversal for a range sum → prune by bounds; collect
    in-order then index → stop at k; sort two in-order lists → merge two
    iterators; insert sorted keys one by one → build from the middle.
14. **Internals**: what `TreeMap` actually is (red-black, colour bit, ≤ 2·log
    height), why deletion needs the successor, why sorted inserts degenerate.
15. **Build it**: a `BST` class with insert / delete / floor / ceiling / rank /
    iterator, tested against a `TreeSet`.
16. **Traces**: deletion of a two-child node, building from a sorted array.
17. **New problems**: `sorted-array-to-bst` (E), `bst-mode` (E), `bst-delete`
    (M), `trim-bst` (M), `merge-two-bsts` (M).

### D. Backtracking
18. **Invariant**: on entry to `dfs`, the shared state holds exactly the
    choices on the path from the root of the search tree to this frame.
19. **Variants**: subsets, k-combinations, permutations, combination-sum
    (reuse), dedup by sort + skip, grid mark/unmark, constraint placement
    (queens, colouring), partition into k buckets, split a string, insert
    operators, count vs list vs decide.
20. **Rewrites**: filter all 2ⁿ subsets → prune on the partial; recount
    conflicts per placement → O(1) sets; `continue` → `break` after a sort;
    k-bucket search without symmetry breaking → skip equal buckets.
21. **Internals**: the recursion tree's size (why 2ⁿ, n!, C(n, k)), stack
    depth, why copying the answer is the `· n`.
22. **Build it**: a generic `Search` harness (choose / undo callbacks) that
    produces subsets, combinations and permutations, tested against counts.
23. **Traces**: pruned combination-sum, k-bucket partition.
24. **New problems**: `binary-strings-n` (I, on-ramp), `partition-k-equal`
    (M), `map-colorings-count` (M), `word-break-sentences` (H),
    `expression-target-count` (H).

### E. Graph traversal
25. **Invariant**: BFS — the queue holds vertices of at most two consecutive
    distances, in non-decreasing order, so a vertex's first discovery is its
    distance.
26. **Variants**: adjacency list vs grid, single / multi-source BFS, DFS for
    components, bipartite colouring, BFS with an augmented state, BFS on an
    implicit board, early exit, bidirectional BFS, clone with a map.
27. **Rewrites**: mark on pop → mark on push; one BFS per source → one
    multi-source BFS; adjacency matrix → list; (cell) state → (cell, mask).
28. **Internals**: adjacency list layouts (`List<Integer>[]`, CSR arrays),
    `ArrayDeque` vs `LinkedList`, recursion depth on a 10⁶ grid.
29. **Build it**: a `Graph` class (list + CSR), BFS/DFS iterative, component
    labelling, tested on random graphs.
30. **Traces**: BFS with the queue per step, the (cell, keys) state BFS.
31. **New problems**: `bfs-levels` (E), `board-game-fewest-rolls` (M),
    `grid-k-breaks` (H), `keys-and-doors-bfs` (H).

### F. Topological sort
32. **Invariant**: Kahn — every vertex in the queue has all its predecessors
    already output.
33. **Variants**: Kahn, DFS post-order, cycle by colours, smallest-first
    (heap), uniqueness (queue size 1), layers (semesters), DAG DP (longest
    path, path counts, critical path).
34. **Rewrites**: repeated scans for in-degree 0 → a queue; recursive path
    count → DP in topological order.
35. **Internals**: why the reversed DFS finish order is topological; the
    in-degree array as the whole state.
36. **Build it**: Kahn + DFS order + a checker that validates any order.
37. **Traces**: Kahn's queue, and DP over the order.
38. **New problems**: `semester-levels` (E), `unique-topo-order` (M),
    `dag-path-count` (M), `critical-path-time` (M).

### G. Union-find
39. **Invariant**: `find(x) == find(y)` exactly when x and y were joined by
    some sequence of unions — path compression and union by size only change
    the tree shapes, never the partition.
40. **Variants**: plain, by size, with component count, with sizes, grid
    cells, online (add cells), weighted offsets, parity (bipartite online),
    offline by threshold, Kruskal.
41. **Rewrites**: BFS per query → DSU; relabel-all union → trees; answer each
    threshold query with a fresh DSU → sort queries and edges together.
42. **Internals**: inverse Ackermann in one paragraph, why rollback forbids
    compression.
43. **Traces**: the offset DSU, and offline queries.
44. **New problems**: `islands-after-each-add` (M), `height-claims` (H),
    `first-odd-cycle` (H), `limited-weight-reachability` (H).

### H. Minimum spanning trees
45. **Invariant**: the chosen edges are always a subset of *some* MST (the cut
    property keeps it true).
46. **Variants**: Kruskal, Prim with a heap, dense Prim, virtual node, forced
    edge, maximum spanning tree, bottleneck path, MST uniqueness / critical
    edges.
47. **Rewrites**: try every spanning tree → Kruskal; Prim with a heap on a
    dense graph → the O(n²) array.
48. **Internals**: cut and cycle properties, why ties do not matter for the
    weight.
49. **Build it**: Kruskal + Prim, cross-checked on random graphs.
50. **Traces**: Prim's heap.
51. **New problems**: `cheapest-road-network` (E, on-ramp),
    `power-grid-generators` (M), `mst-forced-edge` (M), `bottleneck-route` (M).
52. Weight stays 1; the unit gains an on-ramp so it can exceed four problems.

### I. Shortest paths
53. **Invariant**: Dijkstra — every popped (non-stale) vertex has its final
    distance; Bellman-Ford — after round k, `dist` is at most the best path of
    ≤ k edges.
54. **Variants**: BFS, 0-1 BFS, Dijkstra, multi-source, path reconstruction,
    widest path, state-augmented Dijkstra, second-shortest, Bellman-Ford with a
    cycle report, SPFA (and why not), Floyd–Warshall.
55. **Rewrites**: array scan for the minimum → heap; decrease-key → lazy
    deletion; one Dijkstra per source → one multi-source run.
56. **Internals**: `PriorityQueue` has no decrease-key; `long` distances; why
    Floyd's `k` loop is outermost.
57. **Build it**: Dijkstra + Bellman-Ford + Floyd, cross-checked.
58. **Traces**: Bellman-Ford rounds, second-shortest's two slots.
59. **New problems**: `dijkstra-path-print` (M), `nearest-hospital` (M),
    `negative-cycle-detect` (M), `widest-path` (M), `second-shortest-path`
    (H).

### J. Per unit, the help layer
60. For all eight units: ≥ 6 quizzes (bug / predict / model), 6 stuck rows,
    ≥ 8 edge cases (run through the reference), a six-step worked solution, an
    interview script, a lab with presets and ≥ 8 computed work-it-out cards,
    ≥ 8 Big-O drills.

### K. Finishing
61. Rung notes for every problem, including every new one.
62. Keep rungs climbing and the weight bands sensible (new problems mostly on
    optional rungs, as in stage 4).
63. Bump `SEED_VERSION`, regenerate, `verify_dsa_curriculum`, Python-vs-Java
    agreement, brute-force oracles, `VERIFY_SLUGS=… verify_seeds` on the batch.
64. Front end: tree / graph / search labs, the model quiz kind, vitest for the
    pure helpers, `tsc`, `vite build`, checked in the dev server.
65. Update `DSA_ROADMAP.md` and the curriculum memory.

## Status: round 1 implemented (SEED_VERSION 16)

All 65 items shipped, with one trim: item 6 lists five tree rewrites and four were
written — the "list-then-scan diameter" one duplicated the *return one, record another*
variant and skeleton. The stage went from 142 to 182 problems (771 in the bank).

| Unit | Required / total | Traces | Big-O | Quizzes | Stuck | Edge cases | Work-it-out cards | Lab | Worked solution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Binary Trees | 14 / 39 | 4 | 8 | 6 | 6 | 11 | 10 | `tree` | `sum-of-distances-tree` |
| Binary Search Trees | 9 / 24 | 3 | 8 | 6 | 6 | 10 | 9 | `tree` | `bst-delete` |
| Backtracking | 14 / 27 | 4 | 8 | 6 | 6 | 11 | 10 | `search` | `partition-k-equal` |
| Graph Traversal | 14 / 28 | 3 | 8 | 6 | 6 | 11 | 9 | `graph` | `keys-and-doors-bfs` |
| Topological Sort | 9 / 17 | 3 | 8 | 6 | 6 | 10 | 8 | `graph` | `critical-path-time` |
| Union-Find | 9 / 20 | 4 | 8 | 6 | 6 | 9 | 8 | `graph` | `height-claims` |
| Minimum Spanning Trees | 6 / 8 | 3 | 8 | 6 | 6 | 10 | 8 | `graph` | `power-grid-generators` |
| Weighted Shortest Paths | 9 / 20 | 3 | 8 | 6 | 6 | 12 | 8 | `graph` | `second-shortest-path` |

Every unit also gained an invariant, 9–12 variants, 2–4 rewrites, internals (trees kept
its own), a build-it exercise (union-find kept its own), and new skeletons, signals, costs,
pitfalls and checks. The stage has a 21-row router and a cheat sheet, and every unit sits
inside its weight band.

**Where the files are**

- Problems: `tools/dsa_more_53.py` … `dsa_more_57.py` (40 problems; new shapes `tree2`,
  `tree_out`, `tree_lohi_out`, `tree_keys_out`, `post_in`, `arr_tree`, `graph_k`, `n_pairs`,
  `grid_k`, `arr_graph`, `rc_cells`, `wgraph_q3`, `arr_wgraph`, `wgraph_set`, and the LCG
  generators `_rand_tree` / `_rand_graph` / `_rand_tree_edges`).
- Depth: `tools/dsa_s6_depth.py` (trees, BSTs, backtracking, graph traversal) and
  `dsa_s6_depth2.py` (the other four units, the rebuilt ladders, the router).
- Help: `tools/dsa_s6_help.py` and `dsa_s6_help2.py` (quizzes, stuck, edge cases,
  walkthroughs, labs, drills, cheat sheet).
- Labs: `src/lib/graphLab.ts` (pure, 28 vitest tests) rendered by `TreeLab`, `GraphLab` and
  `SearchLab` in `src/components/UnitLab.tsx`, styled by `.lab-*` classes in
  `src/styles/parts/curriculum.css`.

**Changes to the plan**

- Most new problems went to new optional rungs (**Views and orders**, **Top-down and
  paths**, **Whole-tree answers**, **Changing the tree**, **Using the order**, **Harder
  searches**, **Search over states**, **Reading more from the order**, **More layers**,
  **More from one tree**, **Dijkstra, reshaped**), because five of the eight units were
  already at the top of their bands. The required ladders changed only where a new problem
  was a better on-ramp or stretch: `binary-strings-n` and `bfs-levels`, `semester-levels`
  open their units; `grid-k-breaks`, `islands-after-each-add` and `height-claims` joined the
  required ladder, and `restore-ip-addresses`, `max-area-of-island`, `eventual-safe-states`
  moved to Extra practice to make room.
- MST now opens with an Easy problem (`cheapest-road-network`), which lets it grow past four
  problems; it stays weight 1.
- The LCG helper uses the generator's high bits: `s % small` on an LCG modulo 2³¹ cycles far
  too soon in its low bits, which silently produced random graphs with too few edges.
- `tools/verify_snippets.py` cannot wrap most stage-6 fragments (they mix members and
  statements, and reference surrounding variables) — true of the pre-existing stage-6
  skeletons as well. Only its `foundations patterns` scope is CI-gated. Two fragments that
  contained English pseudo-lines were rewritten as real Java.

**Verification**

- For all 40 new problems the Python and Java references agree on every case, the real
  judge accepts both (`VERIFY_SLUGS=… cargo test --test verify_seeds`, 110 s), and brute-force
  oracles agree on 120–300 random small inputs each for 26 of them (the rest are
  pointer-rewiring or order problems checked by the two independent references).
- Generator lints (all eight units added to every `_NEEDS_*` set, plus `_LAB_CHOICES`) and
  their Rust mirrors pass: `verify_dsa_curriculum`, 7/7.
- Every work-it-out answer and every "predict" answer is computed by running the algorithm in
  the authoring file; every edge-case input was run through its problem's reference.
- `tsc` passes; 357 vitest tests (28 new for `lib/graphLab.ts`); `vite build`. The three labs
  and the "Model it" quiz label were checked in the mock dev server with no console errors.

---

# Round 2 — the list

Round 1 gave every unit the full depth and help layers. Round 2 makes the labs
do more of the teaching, adds the interviewer's "what if…?" twist as its own
field, and fills the problem gaps round 1 left.

### A. Features
1. **Tree lab annotations** — pick a per-node quantity (depth, height, subtree
   size, subtree sum, best downward gain, the house-robber (take, skip) pair, the
   camera state) and see it written on every node: the tree DP made visible.
2. **Tree lab operations** — insert, delete (in-order successor) and rotate
   left / right at the selected node, each rewriting the tree field, so a BST can
   be built, broken and rebalanced by hand.
3. **Graph lab algorithms** — `bipartite` (two-colouring BFS that stops at the
   first clash), `zeroone` (0-1 BFS with the deque shown), `floyd` (the distance
   matrix after each k).
4. **Maze lab** (`maze` kind: `grid`, `algo`) — type a grid with `S`, `T`, `#`;
   BFS distances shown on every cell, the shortest path traced, multi-source
   mode for several `S`, and flood fill; stepping through the frontier. Needs a
   second lab on a unit, so units gain **`extra_labs`** (four layers).
5. **"What if…?" follow-ups** (`_follow(q, a)` → `followups`) — the twist an
   interviewer adds after you solve it ("the tree is huge — recursion?", "weights
   can be negative?", "edges are deleted instead of added?"), with the answer
   behind a reveal. Four layers, lint `_NEEDS_FOLLOWUPS`, ≥ 5 per stage-6 unit.

### B. Content
6. One more computed trace for graph traversal (multi-source BFS), topological
   sort (DFS finish order), MST (forced edge) and shortest paths (0-1 BFS).
7. Two more quizzes per unit (≥ 8), including more `model` quizzes.
8. Work-it-out cards to ≥ 10 per unit.

### C. New problems (19)
9. Trees: `distribute-coins-tree` (M), `flip-equivalent-trees` (M),
   `longest-zigzag-tree` (M), `tree-diameter-general` (M, two BFS).
10. BSTs: `bst-greater-sum` (M, reverse in-order), `balance-bst` (M),
    `two-bst-pair-sum` (M, two iterators).
11. Backtracking: `letter-tile-sequences` (M), `n-queens-boards` (H).
12. Graph traversal: `count-sub-islands` (M), `alternating-colour-paths` (M,
    state BFS).
13. Topological sort: `all-ancestors-dag` (M).
14. Union-find: `smallest-equivalent-string` (M), `gcd-connectivity` (H).
15. MST: `max-spanning-tree` (E), `second-best-mst` (H).
16. Shortest paths: `max-probability-path` (M), `dag-shortest-negative` (M),
    `reachability-queries` (M, transitive closure).

### D. Finishing
17. Place and note every new problem; bands; `SEED_VERSION` 17; Python-vs-Java,
    oracles, `VERIFY_SLUGS` judge run; vitest for the new pure helpers; dev-server
    check; docs and memory.

## Status: round 2 implemented (SEED_VERSION 17)

All 17 items shipped. The stage went from 182 to 201 problems (790 in the bank); every
unit now carries 8 quizzes, 10 work-it-out cards, 5–6 follow-ups and 3–4 traces.

- **Problems**: `tools/dsa_more_58.py` (trees, BSTs, backtracking) and `dsa_more_59.py`
  (graphs); new shapes `tree2_k`, `grid_pair`, `two_sets`, `str3`, `ntq`, `wgraph_tc`,
  `graph_q`. The plan's `max-probability-path` became **`cost-within-deadline`** — the
  batch kit has no float judge mode, and a (vertex, time) state search teaches more.
- **Content**: `tools/dsa_s6_round2.py` (follow-ups, traces, quizzes, drills, presets, the
  maze lab). The first trees quiz's answer is recomputed by a Python twin, and maze presets
  that promise a route are checked for one at generation time — an early draft of "Around
  the wall" was sealed shut and only the lab caught it.
- **Features**: `extra_labs` and `followups` are new unit fields through all four layers
  (`_follow`, lint `_NEEDS_FOLLOWUPS` / Rust `units_that_need_followups_carry_them`,
  `models.rs` `Followup`, `types.ts`, the "What if…?" section). Graph lab gained
  `bipartite`, `zeroone`, `floyd`; tree lab gained per-node annotations (`note` preset field)
  and insert / delete / rotate buttons; new `maze` lab kind. All in `src/lib/graphLab.ts`.

**Verification**: Python and Java agree on every case of all 19 problems and the real judge
accepts both (56 s); brute-force oracles agree on 150–250 random inputs for 14 of them;
`verify_dsa_curriculum` 8/8; 374 vitest tests (17 new); `tsc`; `vite build`; the maze, tree
edits, annotations and follow-ups checked in the mock dev server with no console errors.
(After regenerating seeds, restart the mock dev server — Vite keeps serving the old JSON.)

---

# Round 3 — the list

A problem round: patterns the stage teaches in prose but no problem forces.

1. `count-univalue-subtrees` (M) — bottom-up boolean plus a counter.
2. `insufficient-nodes-prune` (M) — top-down sum in, bottom-up "keep me?" out; the root may go.
3. `bst-range-count` (E) — the pruned range walk, counting.
4. `inorder-predecessor` (M) — the mirror of the successor, by descent, with no parent pointers.
5. `max-unique-split` (M) — backtracking over string splits with a used-set.
6. `split-into-fibonacci` (M) — the first two numbers fix everything; no leading zeros, int overflow.
7. `gene-mutation-steps` (M) — BFS over strings restricted to a bank.
8. `regions-by-slashes` (M) — each cell split into four triangles, union-find.
9. `portal-maze` (M) — grid BFS where a letter teleports to its twin.
10. Place, note, verify (Python-vs-Java, oracles, real judge), `SEED_VERSION` 18, docs.

## Status: round 3 implemented (SEED_VERSION 18)

All nine problems shipped in `tools/dsa_more_60.py` (new shapes `tree_k_out`, `str2_list`) and
sit on the optional rungs of their units; the stage has 210 problems, the bank 799. Python and
Java agree on every case, the real judge accepts both (24 s), and brute-force oracles agree on
250 random inputs for six of them — including a pixel-rasterising check for
`regions-by-slashes`. Two drafted examples were unsolvable or matched well-known published
examples and were replaced before shipping.
