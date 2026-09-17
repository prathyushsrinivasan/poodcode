# DSA Curriculum — syllabus roadmap, round 2

**Scope:** what the curriculum teaches and in what order — not the judge, the UI
or the practice mechanics.

**Round 1 is done** (2026-09-17). It:
- moved greedy and intervals next to sorting, and recursion ahead of the sorts;
- split DP into four units and added MST;
- added rungs for KMP and palindromes, tree building, `TreeMap`, pointer mapping,
  all-pairs shortest paths and modular counting;
- added an optional stage 8 (string matching, range queries, advanced graphs,
  bitmask DP);
- added 38 problems and re-homed 7.

The moves are recorded in `tools/dsa_syllabus.py`.

**This round** audits the result: 7 core stages, 36 units, an optional stage of
4 units, 653 problems (`dsa_curriculum.json`, 2026-09-18). The evidence comes
from three checks:
- every rung's problems against the unit's own teaching text
  (`why`, `model`, `skeletons`, `signals`, `checks`);
- a slug search for staple interview topics;
- per-unit counts of difficulty, rungs, checks and on-ramps.

The same generator lints apply to every change: each problem is placed once,
prerequisites point backwards, rungs climb, and optional stages come last.

---

## 1. Order

### 1.1 Tries sit in the DP stage, and stages 6–7 are overloaded

`tries` is unit 35 of 36, in "Dynamic Programming & Design", but its only
prerequisites are `trees` and `strings`. It has nothing to do with DP. Its
Extra-practice problem `word-search-ii` is trie **plus backtracking**, which
makes backtracking its natural neighbour.

The two stages around it are also the largest in the course:

| Stage | Units | Contents |
|---|---|---|
| 6. Trees & Graphs | 8 | two tree families and five graph units |
| 7. DP & Design | 6 | four DP units, tries, design |

**Split stage 6** into:
- **Trees & Search:** trees · bst · tries · backtracking
- **Graphs:** graph traversal · topological sort · union-find · MST · shortest paths

This leaves stage 8 as DP ×4 + design. The core becomes **8 stages** with the
same 36 units, and no stage has more than 6.

### 1.2 Stage 2 requires two Hard KMP problems before any Medium stage 3 material

The strings unit's "Palindromes & matching" rung makes `longest-happy-prefix`
(Hard) and `shortest-palindrome` (Hard) **required**, in stage 2, just after the
first sliding-window unit. The technique is taught there and the lints pass, but
this is the steepest wall on the whole early path.

**Keep** `find-pattern-index`, `count-palindromic-substrings` and
`longest-palindromic-substring` required. **Move** the two Hards to Extra
practice, where they stay reachable and taught.

### 1.3 Problems placed before their prerequisites

| Problem | Placed in | Needs | Taught in | Fix |
|---|---|---|---|---|
| `hand-of-straights` | greedy (stage 3), extra | ordered map (`TreeMap`) | bst, stage 6 | move to bst · Extra practice |
| `data-stream-disjoint-intervals` | intervals (stage 3), extra | ordered map | bst, stage 6 | move to bst · Extra practice |
| `meeting-rooms-iii` | intervals (stage 3), extra | two heaps | heaps, stage 5 | move to heaps · Extra practice |
| `num-subsequences-sum-condition` | two pointers (stage 2), extra | powers of two mod p | math, stage 4 | move to math · Extra practice |
| `min-meeting-rooms` | intervals (stage 3), **required** | a min-heap *or* a ±1 sweep | sweep: prefix sums; heap: stage 5 | keep, and make the sweep the taught answer in the intervals model; the heap version stays a note |

---

## 2. Practised but never taught

Each of these problems needs a named technique that its unit's text never
mentions (checked by searching the unit's teaching fields). The first two are on
**required** rungs.

| Problem | Unit · rung | Technique | Fix |
|---|---|---|---|
| `majority-element` | hashing · Variations (**required**) | Boyer–Moore voting | model section + skeleton + check in hashing |
| `sum-subarray-minimums` | stacks · Stretch (**required**) | contribution counting: previous/next smaller × span | model section in stacks — it is the monotonic stack's best use and is never named |
| `sum-subarray-ranges`, `sum-odd-length-subarrays` | complexity · extra | contribution counting | a short "count each element's contribution" section in complexity; point forward to stacks |
| `house-robber-iii` | trees · extra | tree DP returning a pair (take, skip) | a tree-DP rung in trees (see 3.4) |
| `longest-path-dag`, `largest-color-value` | topological sort · extra | DP in topological order | model section + skeleton in topo: relax `dp[v]` as vertices come off the queue |
| `range-sum-2d` | prefix sums · extra | 2-D prefix sums and inclusion–exclusion | model section + skeleton in prefix sums |
| `xor-queries-subarray` | bit manipulation · extra | prefix XOR | one paragraph in bits (XOR is its own inverse, so prefix XOR works like prefix sums) |
| `next-permutation` | two pointers · extra | find the pivot, swap with its successor, reverse the suffix | model section in two pointers |
| `unique-bst-count` | bst · extra | Catalan recurrence (choose the root, multiply the sides) | a check + note in bst, linked forward to DP |
| `median-two-sorted-arrays` | binary search · extra | binary search on a partition | model section in binary search |
| `all-nodes-distance-k` | trees · extra | tree → graph via a parent map, then BFS | model paragraph in trees |

Two **signals name techniques that are taught nowhere**:
- **Meet in the middle.** Bitmask DP's routing table says "n up to 40 → meet in
  the middle".
- **Matrix powers.** The recursion unit's fast-power skeleton lists "matrix
  powers" as a use.

Either teach them (§5) or remove the claims.

---

## 3. Topics missing from the core

### 3.1 BFS with extra state

Stateful search appears only in the *optional* bitmask unit
(`shortest-path-visit-all`). The core graph units never put anything besides the
vertex in a BFS or Dijkstra state. That is a staple Medium/Hard pattern:
- a grid where you may break k walls: state `(cell, walls left)`
- a maze with keys and doors
- the cheapest route with k discounts: state `(city, discounts used)`

`cheapest-trip-with-discounts` is already in shortest paths' Extra practice,
untaught.

**Add** a "Search with extra state" rung to `graph-traversal`:
- a new Medium: shortest grid path with k wall-breaks;
- a new Hard: keys and doors.

**Promote** `cheapest-trip-with-discounts` to a shortest-paths rung, and teach
"the state is everything the future depends on" in both units.

### 3.2 Randomised structures and sampling

There is no randomised problem anywhere. Design's Big-O drill even explains
"how an O(1) `getRandom` set is built", with no problem that builds one. Three
are staples:
- **Randomised set:** insert/delete/getRandom in O(1) — a hash map plus an
  array with swap-delete. Belongs in design.
- **Random pick with weight:** prefix sums + binary search. Belongs in binary
  search or prefix sums.
- **Reservoir sampling:** pick uniformly from a stream of unknown length.
  Belongs in the optional stage or linked lists.

**Judging constraint:** the random draws must be part of the *input*, so the
expected output stays deterministic (for example "the next draws are r₁ … r_k").

### 3.3 BST deletion and balanced construction

- **Deletion.** The bst unit's `why` promises "search, insertion and deletion",
  but there is no deletion problem and no skeleton for the two-children case
  (replace with the in-order successor).
- **Balanced construction.** There is no "sorted array → height-balanced BST",
  the natural divide-and-conquer bridge from stage 3.

**Add** both problems (Medium and Easy) and a deletion skeleton.

### 3.4 Tree patterns without a rung

- **Tree DP.** Returning two values per subtree (take/skip, or "best through
  me" vs "best ending at me") is the idea behind `diameter-of-tree`,
  `max-path-sum` and `house-robber-iii`. The first two sit in a generic
  "Stretch" rung and the third in Extra practice. **Name it:** a "Tree DP" rung
  with a skeleton that returns a pair.
- **N-ary trees.** No problem uses them. One Easy (N-ary level order or max
  depth) shows the recursion does not care how many children there are.
- **Tree as a graph.** A parent map turns a tree into an undirected graph
  (`all-nodes-distance-k`) — see §2.

### 3.5 Iterator and stream designs

The design unit has no iterator problem (`bst-iterator` is the only one in the
bank). **Add** a peeking iterator and a flatten-nested-list iterator: "hold the
next element before it is asked for" is a standard design pattern.

### 3.6 Expression evaluation with precedence

The stacks unit signals "operand stack, operator stack", and `basic-calculator`
(Hard, extra) needs it, but nothing teaches operator precedence.

**Add:**
- a Medium calculator with `+ − × ÷` and no parentheses;
- a model section on handling precedence with a pending term.

---

## 4. Balance and depth inside units

### 4.1 Units with no easy way in

`mst` (2 Medium + 2 Hard) and `range-queries` (2 Medium + 2 Hard) open straight
at Medium. The four-problem exemption keeps the lint quiet, but a first
Kruskal or Fenwick problem should be small.

**Add** one Easy opener each:
- Kruskal on a handful of cities;
- Fenwick with point updates and prefix sums on a tiny array.

### 4.2 The round-1 splits left thin teaching

| Unit | Checks | Signals | Internals / build-it |
|---|---|---|---|
| `dp-1d` | **3** (lost 2 to the knapsack unit) | 5 | build-it only |
| `dp-2d` | 4 | **4** | none |
| `dp-knapsack`, `dp-intervals-states` | 5 | 6 | none |
| `mst` | 5 | 6 | none |

The target for each:
- at least **5 checks** and **6 signals** per unit;
- a **build-it** for each new DP unit — fill the table by hand on the unit's
  trace example, then roll it to one row;
- **internals** for MST: why union-find makes Kruskal near-linear after the sort,
  and why array Prim beats heap Prim on dense graphs.

### 4.3 The optional units have no surplus

Each optional unit has 4–5 problems and **zero** Extra practice. One technique
with one Hard is not enough reps to make it stick.

**Add** 2–3 Extra-practice problems per optional unit, for example:
- **String matching:** repeated substring via Z, string periods.
- **Range queries:** count of range sums, 2-D Fenwick.
- **Advanced graphs:** bridges as their own problem, 2-SAT-lite SCC.
- **Bitmask DP:** fair distribution, TSP returning to start.

---

## 5. The optional stage: what else belongs there

Still optional — rare in interviews, but each closes a claim the core already
makes (§2) or a well-known gap:

| Unit (new) | Covers | Evidence |
|---|---|---|
| **Advanced trees** | LCA by binary lifting, k-th ancestor, Euler tour for subtree queries | nothing in the bank; `lca-binary-tree` is O(n) per query only |
| **Math beyond the core** | matrix exponentiation (linear recurrences), cross-product geometry basics, expected value | "matrix powers" named in recursion and practised nowhere; no geometry or probability anywhere |

**Add to existing optional units:**
- meet in the middle, as a rung in `bitmask-dp` (its own signal promises it);
- digit DP, as a rung in `bitmask-dp` or a small unit of its own.

---

## 6. Proposed map

Legend: **new** = new unit · *moved* = existing unit in a new place ·
+ = new rung or teaching in an existing unit.

| Stage | Units |
|---|---|
| 1. Foundations | io-and-arithmetic · branching · loops-and-digits · arrays-first-pass |
| 2. Cost & core patterns | complexity (+ contribution counting) · hashing (+ Boyer–Moore) · two-pointers (+ next permutation) · sliding-window · prefix-sums (+ 2-D, + weighted random pick) · strings (KMP Hards → extra) |
| 3. Order & search | recursion · sorting · binary-search (+ partition search) · greedy · intervals (sweep-first rooms) |
| 4. Numbers, bits & grids | math-number-theory · bit-manipulation (+ prefix XOR) · simulation-and-matrix |
| 5. Linear structures | stacks (+ contribution, + precedence) · queues-and-deques · linked-lists · heaps |
| 6. Trees & search | trees (+ tree DP, + N-ary, + parent map) · bst (+ deletion, + balanced build) · *tries* · backtracking |
| 7. Graphs | graph-traversal (+ state BFS) · topological-sort (+ DAG DP) · union-find · mst (+ Easy opener, + internals) · shortest-paths (+ state Dijkstra) |
| 8. DP & design | dp-1d · dp-knapsack · dp-2d · dp-intervals-states *(each + checks, build-it)* · design (+ randomised set, + iterators) |
| 9. Beyond the core *(optional)* | string-matching · range-queries (+ Easy opener) · advanced-graphs · bitmask-dp (+ meet in the middle) · **advanced trees** · **math beyond the core** *(each + Extra practice)* |

The core stays at 36 units, now in 8 stages; the optional stage grows from 4
units to 6.

**New problems:** about **14 core** (§3: 2 state search, 3 randomised, 2 BST,
1 tree DP, 1 N-ary, 2 iterators, 1 calculator; §4.1: 2 openers) and about
**14 optional** (§4.3 extras, §5 units). Every one needs Python and Java
references run through the real judge.

## Order of work

1. **Moves only:** 1.1, 1.2, 1.3. These are stage split, re-homing and
   demotions — no new content, no new problems. `dsa_syllabus.py` plus one new
   stage file.
2. **Teach the orphans (§2).** Text, skeletons and checks in existing units; no
   new problems. Start with the two on required rungs.
3. **Deepen the thin units (§4.2)**, while the DP and MST units are fresh.
4. **Add the missing core topics (§3)**, with their problems — state search and
   BST deletion first, since they are the most asked.
5. **Openers and the optional stage (§4.1, §4.3, §5).**
