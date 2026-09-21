# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 8, continued — the six units the 107-topic roadmap asked for.
#
# exec()'d by tools/dsa_curriculum.py immediately after dsa_s8_beyond.py, into
# the same namespace, so `_S8`, `_unit`, `_rung` and friends are defined and the
# units land in the OPTIONAL stage, after the four that were already there.
#
# Why a second file rather than more of the first: dsa_s8_beyond.py is already
# a thousand lines for four units, and unit order is file exec order — appending
# here keeps the existing four in place and adds six after them, with no risk of
# an edit in the middle silently reordering the stage.
#
# Each closes a gap the audit in DSA_ROADMAP.md named:
#
#   tree-queries         LCA, binary lifting, Euler tour
#   advanced-bits        Gray code, XOR basis
#   dp-advanced          digit DP, DP optimisation, meet in the middle
#   flows-and-matching   max flow, min cut, bipartite matching
#   geometry             cross product, line intersection, convex hull
#   randomized           expected vs worst case, Las Vegas vs Monte Carlo, sampling
# ---------------------------------------------------------------------------


# --- Unit 41 — Tree queries --------------------------------------------------

_unit(
    "tree-queries", "Tree Queries: LCA & Binary Lifting", "🪜", _S8,
    "Preprocess a fixed tree once, then answer thousands of questions in O(log n).",
    weight=1,
    prereqs=["trees", "graph-traversal", "bit-manipulation"],
    why="""
The `trees` unit finds a lowest common ancestor in O(n): recurse, and the node
that hears back from both sides is the answer. That is the right algorithm for
**one** query.

Now the tree stops changing and the questions keep coming — a hundred thousand
of them. O(n) each is 10¹⁰ steps, and every one of those traversals re-derives
facts about the same tree. The fix is the one this whole stage is about: move
the work out of the query and into a preprocessing pass.

Two preprocessing ideas cover almost everything anyone asks about a static tree.
""",
    model="""
### Euler tour: a subtree is a contiguous range

Do one DFS from the root, stamping a counter twice per node — on the way in and
on the way out:

```java
int timer = 0;
void dfs(int u, int parent) {
    tin[u] = timer++;
    for (int w : g[u]) if (w != parent) dfs(w, u);
    tout[u] = timer++;
}
```

A DFS leaves `u` only after entering and leaving everything below it, so every
descendant's interval nests inside `[tin[u], tout[u]]`. Therefore:

```java
boolean isAncestor(int a, int b) {
    return tin[a] <= tin[b] && tout[b] <= tout[a];
}
```

Descent has become **interval containment**, and a subtree has become a
contiguous range of the tour — which means every array technique from stages 2
and 5 now applies to subtrees. Subtree sums become prefix sums; subtree updates
become range updates on a Fenwick tree.

### Binary lifting: jumps of 1, 2, 4, 8 …

Store, for every node, where you land after climbing 2^j levels:

```java
up[0][v] = parent[v];                       // -1 at the root
up[j][v] = up[j-1][ up[j-1][v] ];           // 2^j = 2^(j-1), twice
```

`up[j]` needs `up[j-1]` **complete**, so j must be the outer loop. Then any
climb of k levels is the set bits of k:

```java
int jump(int v, int k) {
    for (int j = 0; k > 0 && v >= 0; j++, k >>= 1)
        if ((k & 1) == 1) v = up[j][v];
    return v;
}
```

O(n log n) memory, O(log n) per jump. It is exponentiation by squaring with
"follow a pointer" in place of "multiply" — and the same table shape as the
sparse table in the previous unit.

### LCA, as a binary search on the path

```java
int lca(int a, int b) {
    if (depth[a] < depth[b]) { int t = a; a = b; b = t; }
    a = jump(a, depth[a] - depth[b]);            // level them first
    if (a == b) return a;                        // b was an ancestor of a
    for (int j = LOG - 1; j >= 0; j--)
        if (up[j][a] != up[j][b]) { a = up[j][a]; b = up[j][b]; }
    return up[0][a];                             // one below the meeting point
}
```

The ancestors of `a` split into a run that are not ancestors of `b` and a run
that are. Descending the powers finds that boundary in log n steps — binary
search, on a path instead of an array.

The early `a == b` return is not an optimisation. Without it the loop never runs
and the function returns the LCA's *parent*.

### Path quantities

Root the tree and record `dist[v]` from the root. Then for anything additive
along a path:

> `path(a, b) = dist[a] + dist[b] − 2 · dist[lca(a, b)]`

The stretch from the root to the LCA is counted twice by the two root-paths and
used zero times by the real path, so it comes off twice. With `depth` instead of
`dist`, the same formula counts **edges**.

Keep `depth` (edge count, for levelling and jumping) and `dist` (length, for the
answer) as separate arrays. Levelling by `dist` is the bug this idea is most
often broken by.
""",
    signals=[
        _sig("“q queries on a tree that never changes”", "Preprocess, do not traverse",
             "O(n) per query times 10⁵ queries is the thing to avoid."),
        _sig("“is u an ancestor of v?”, “is v in u's subtree?”", "Euler tour tin/tout",
             "Descent becomes interval containment: two comparisons."),
        _sig("“the k-th ancestor”, “k levels up”", "Binary lifting",
             "Any k is a sum of powers of two."),
        _sig("“lowest common ancestor”, repeatedly", "Level, then descend the powers",
             "O(log n) after an O(n log n) build."),
        _sig("“distance between two nodes” on a tree", "dist[a] + dist[b] − 2·dist[lca]",
             "Every tree path decomposes at the LCA."),
        _sig("“sum over a subtree”, with updates", "Euler tour + Fenwick tree",
             "The subtree is a contiguous range, so the previous unit applies."),
        _sig("A single LCA query, once", "The O(n) recursion in `trees`",
             "Do not build a jump table for one question."),
    ],
    skeletons=[
        _sk("Euler tour, iteratively",
            "Ancestor tests, subtree ranges. Iterative because a path graph recurses n deep.",
            """
int[] tin = new int[n], tout = new int[n], parent = new int[n], iter = new int[n];
int timer = 0, top = 0;
int[] stack = new int[n + 1];
stack[0] = root; parent[root] = -1; tin[root] = timer++;
while (top >= 0) {
    int u = stack[top];
    if (iter[u] < g[u].size()) {
        int w = g[u].get(iter[u]++);
        if (w == parent[u]) continue;
        parent[w] = u;
        tin[w] = timer++;
        stack[++top] = w;
    } else {
        tout[u] = timer++;
        top--;
    }
}
""",
            "`iter[u]` is how far through u's neighbours the walk has got — the explicit form of "
            "\"where the for-loop was\" when the call stack is gone."),
        _sk("Binary lifting table",
            "k-th ancestor, LCA, and anything else that climbs.",
            """
int LOG = 1;
while ((1 << LOG) < n) LOG++;
LOG++;

int[][] up = new int[LOG][n];
for (int[] row : up) Arrays.fill(row, -1);
// BFS or DFS from the root fills up[0][v] = parent and depth[v]
for (int j = 1; j < LOG; j++)
    for (int v = 0; v < n; v++) {
        int mid = up[j - 1][v];
        up[j][v] = mid < 0 ? -1 : up[j - 1][mid];
    }
""",
            "The `-1` sentinel must absorb further jumps, or climbing past the root crashes."),
        _sk("LCA",
            "The meeting point of two nodes, in O(log n).",
            """
int lca(int a, int b) {
    if (depth[a] < depth[b]) { int t = a; a = b; b = t; }
    for (int j = 0, d = depth[a] - depth[b]; d > 0; j++, d >>= 1)
        if ((d & 1) == 1) a = up[j][a];
    if (a == b) return a;
    for (int j = LOG - 1; j >= 0; j--)
        if (up[j][a] != up[j][b]) { a = up[j][a]; b = up[j][b]; }
    return up[0][a];
}
""",
            "Two loops: one levels, one descends the powers. Neither is optional."),
    ],
    traces=[
        _trace(
            "Binary lifting on a chain 0 ← 1 ← 2 ← 3 ← 4 ← 5",
            "`up[j][v]` is where v lands after climbing 2^j levels, or −1 off the top. Each "
            "row is built from the one above it: climb 2^(j−1), then climb it again.",
            ["j", "up[j][0]", "up[j][1]", "up[j][2]", "up[j][3]", "up[j][4]", "up[j][5]"],
            [
                ["0 (parent)", "−1", "0", "1", "2", "3", "4"],
                ["1 (2 up)", "−1", "−1", "0", "1", "2", "3"],
                ["2 (4 up)", "−1", "−1", "−1", "−1", "0", "1"],
                ["3 (8 up)", "−1", "−1", "−1", "−1", "−1", "−1"],
            ],
            "To climb 5 from node 5: 5 = 101₂, so take the j = 0 jump (5 → 4) and the "
            "j = 2 jump (4 → 0). Two lookups instead of five steps — and on a chain of "
            "200000 nodes, eighteen instead of 200000. Notice how −1 absorbs: once a jump "
            "runs off the top, every longer jump does too.",
        ),
        _trace(
            "Euler tour of a small tree, and the ancestor test",
            "The tree is 0 → {1, 2}, 1 → {3, 4}, 2 → {5}. One DFS, stamping on the "
            "way in and on the way out.",
            ["node", "tin", "tout", "interval", "inside 1's interval?"],
            [
                ["0", "0", "11", "[0, 11]", "no — it contains 1's"],
                ["1", "1", "6", "[1, 6]", "itself"],
                ["3", "2", "3", "[2, 3]", "**yes**"],
                ["4", "4", "5", "[4, 5]", "**yes**"],
                ["2", "7", "10", "[7, 10]", "no — disjoint"],
                ["5", "8", "9", "[8, 9]", "no — disjoint"],
            ],
            "Node 1's subtree is exactly the nodes whose interval nests inside [1, 6], and those "
            "are exactly the entries with tin between 1 and 6 — a contiguous block of the "
            "tour. \"Is a above b\" is now `tin[a] <= tin[b] && tout[b] <= tout[a]`, with no "
            "walking at all.",
        ),
    ],
    costs=[
        _cost("Euler tour (one DFS)", "O(n)", "O(n)", "Two stamps per node."),
        _cost("Ancestor test", "O(1)", "—", "Two integer comparisons."),
        _cost("Binary lifting build", "O(n log n)", "O(n log n)", "18 levels at n = 2·10⁵."),
        _cost("k-th ancestor / LCA", "O(log n)", "O(1)", "One bit of k per step."),
        _cost("Path distance", "O(log n)", "O(1)", "One LCA plus three array reads."),
        _cost("Naive LCA per query", "O(n)", "O(n)", "Correct, and 10¹⁰ steps at 10⁵ queries."),
    ],
    pitfalls=[
        _pit("StackOverflowError on a large tree",
             "A recursive DFS on a path graph of 200000 nodes recurses 200000 deep.",
             "Use an explicit stack, or a BFS if you only need parents and depths."),
        _pit("LCA returns the parent of the right answer",
             "The `if (a == b) return a;` after levelling is missing, so when b is an ancestor "
             "of a the descending loop never runs and the final `up[0][a]` goes one too far.",
             "Return immediately when levelling makes them equal."),
        _pit("Climbing past the root crashes or returns garbage",
             "`up[j][v]` was indexed with v = −1.",
             "Make −1 absorbing in the build (`mid < 0 ? -1 : …`) and guard `v >= 0` in "
             "the jump loop."),
        _pit("The jump table is wrong for j ≥ 2",
             "The loops were nested the wrong way, so `up[j-1]` was not yet complete when "
             "`up[j]` read it.",
             "j must be the outer loop and v the inner one."),
        _pit("Distances on a weighted tree are wrong",
             "The LCA search levelled by `dist` (length) rather than `depth` (edge count).",
             "Keep both arrays. A long edge is still exactly one level."),
        _pit("Path lengths overflow",
             "200000 edges of 10⁹ reach 2·10¹⁴.",
             "`dist` is a `long`; `depth` can stay an `int`."),
    ],
    lessons=["tree_basics", "tree_traversal", "bit_manip"],
    checks=[
        _chk("Why does a DFS's entry/exit stamping turn \"is a an ancestor of b\" into two "
             "comparisons?",
             "Because a DFS leaves a node only after entering and leaving everything below it, "
             "so every descendant's [tin, tout] interval nests inside the ancestor's, and every "
             "non-descendant's is disjoint. Nesting and descent are the same relation."),
        _chk("Why does binary lifting store only powers of two?",
             "Because every k is a sum of distinct powers of two, so any climb is at most "
             "⌈log₂ n⌉ of them. Storing every jump length would be O(n²) "
             "memory; the powers span all of them in O(n log n)."),
        _chk("In the LCA descent, why take a jump only when `up[j][a] != up[j][b]`?",
             "The invariant is that a and b stay strictly below the LCA. Different ancestors "
             "2^j up means that jump lands below the meeting point, so it is safe. When no jump "
             "keeps them apart, they are the two children of the LCA and the answer is their "
             "parent."),
        _chk("What is the distance between a and b on a weighted tree rooted anywhere?",
             "`dist[a] + dist[b] − 2·dist[lca(a, b)]`. The two root-paths share exactly "
             "the root-to-LCA stretch, which the real path does not use, so it is removed twice."),
        _chk("You need one LCA, once, on a tree of 1000 nodes. What do you write?",
             "The O(n) recursion from the `trees` unit. Building an O(n log n) table to answer "
             "a single question is slower and twenty more lines."),
    ],
    bigo=[
        _bigo(r"""
for (int j = 1; j < LOG; j++)                   // LOG = ceil(log2 n) + 1
    for (int v = 0; v < n; v++)
        up[j][v] = up[j-1][v] < 0 ? -1 : up[j-1][up[j-1][v]];
""", "O(n log n)", ["O(n log n)", "O(n)", "O(n²)", "O(log n)"],
            "log n levels of n entries, each filled with two array reads. The memory is the "
            "same O(n log n) — 18 int arrays of 200000 is about 14 MB, which is the real "
            "limit on this technique."),
        _bigo(r"""
int v = a;                                      // k-th ancestor, binary lifting
for (int j = 0; k > 0 && v >= 0; j++, k >>= 1)
    if ((k & 1) == 1) v = up[j][v];
""", "O(log k)", ["O(log k)", "O(k)", "O(n)", "O(1)"],
            "One iteration per bit of k, and at most one array read each. The naive version "
            "follows k parent pointers, which is O(k) — the same answer, 200000 times "
            "slower on a chain."),
        _bigo(r"""
for (int q = 0; q < Q; q++)                     // one LCA per query, naive
    answer[q] = lcaByWalkingUp(a[q], b[q]);     // O(n) each
""", "O(Q·n)", ["O(Q·n)", "O(Q log n)", "O(n log n)", "O(Q + n)"],
            "This is the thing the unit exists to replace: at Q = n = 2·10⁵ it is "
            "4·10¹⁰ steps. Preprocessing costs O(n log n) once and makes each "
            "query O(log n), for 4·10⁶ in total."),
        _bigo(r"""
int timer = 0;                                  // Euler tour
void dfs(int u, int p) {
    tin[u] = timer++;
    for (int w : g[u]) if (w != p) dfs(w, u);
    tout[u] = timer++;
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(n + m log n)"],
            "A tree has n − 1 edges, each looked at twice (once from each end), and each "
            "node is stamped twice. The ancestor test it enables is then O(1) — all the "
            "work happened here."),
        _bigo(r"""
// subtree sum with updates, after an Euler tour
fenwick.add(tin[v], delta);                     // point update at v's entry time
long subtreeSum = fenwick.range(tin[u], tout[u]);
""", "O(log n)", ["O(log n)", "O(n)", "O(1)", "O(n log n)"],
            "Because the tour makes a subtree contiguous, a subtree query is an ordinary range "
            "query — the previous unit's Fenwick tree, unchanged. Recomputing a subtree sum "
            "by traversal would be O(n) per query."),
    ],
    interview="""
Say the two-part answer out loud: *"a single LCA is an O(n) recursion; q queries
on a fixed tree is binary lifting, O(n log n) to build and O(log n) each."*
Naming both, and choosing between them from the constraint, is the whole
signal — reaching straight for the jump table on a one-query problem reads as
memorisation.

For anything about subtrees, say "Euler tour" early: it converts the question
into an array question the interviewer already knows you can answer.
""",
    rungs=[
        _rung("Warm up", "One DFS, and descent becomes interval containment.",
              ["ancestor-queries"],
              {"ancestor-queries": "Write the iterative tour — the recursive one overflows on a chain of 200000. Stamp on the way in *and* out; only one of the two stamps is not enough."}),
        _rung("Core", "The jump table, then the search that uses it.",
              ["kth-ancestor-queries", "tree-lca-queries"],
              {"kth-ancestor-queries": "Build `up` before you use it, and check the loop nesting: j outside, v inside.",
               "tree-lca-queries": "Level first, then descend from the largest power. Test a case where one node is an ancestor of the other — that is the early return."}),
        _rung("Stretch", "Two arrays, one for levelling and one for the answer.",
              ["tree-path-distance"],
              {"tree-path-distance": "`depth` in edges for the climbing, `dist` in length for the answer. Mixing them up gives right answers on unweighted trees only."}),
    ],
    next_up="""
Powers of two, used to jump. The next unit uses the bits themselves as the
object of study: a code where neighbours differ in one bit, and a basis for
everything a set of numbers can XOR to.
""",
)


# --- Unit 42 — Advanced bits -------------------------------------------------

_unit(
    "advanced-bits", "Gray Codes & XOR Bases", "🔀", _S8,
    "Orders where one bit changes, and the linear algebra hiding inside XOR.",
    weight=1,
    prereqs=["bit-manipulation", "math-number-theory", "bitmask-dp"],
    why="""
The `bit-manipulation` unit treats a number as a bag of flags: set one, clear
one, count them, enumerate the subsets. Two questions escape that view entirely.

**"Visit every configuration, changing one thing at a time."** The subsets in
numeric order do not do this — 3 to 4 flips three bits. There is an order that
does, it is easy to write, and it is why a rotary encoder cannot misread.

**"What can a set of numbers XOR to?"** 2ⁿ subsets, and for n = 100,000 the
answer is not enumeration. XOR is addition without carries, which makes the
numbers *vectors over GF(2)* — and a set of vectors has a basis of at most 30.
Maximum, count and k-th smallest all fall out of it.
""",
    model="""
### Gray code

The **reflected binary code** lists all n-bit numbers so that consecutive
entries differ in exactly one bit:

```
G(n) = G(n-1),  then  reverse(G(n-1)) with bit n-1 set
```

Mirroring is what makes the join between the halves a single flip of the new
bit. The closed form of the same sequence needs no recursion:

```java
int gray(int i) { return i ^ (i >> 1); }
```

Why that works: adding 1 to `i` flips a run of trailing 1s to 0s and the 0 above
them to 1. In `i ^ (i >> 1)` each output bit is `bit_k(i) XOR bit_{k+1}(i)`, so
adjacent changes in that run cancel in pairs and exactly one survives.

Going back is a prefix XOR — encoding is a difference, decoding is its running
sum:

```java
int index(int g) { for (int s = 1; s < 32; s <<= 1) g ^= g >> s; return g; }
```

A Gray code is a Hamiltonian path on the hypercube. Whenever a problem says
"change one thing at a time" over all configurations, this is the order.

### XOR is a vector space

XOR has no carries, so bit k of the result depends only on bit k of the inputs.
That makes each number a vector over **GF(2)** (the field with two elements),
with XOR as addition and `x ^ x = 0` as "every element is its own inverse".

Everything from linear algebra then applies. A set of numbers has a **span** —
the values reachable as XORs of subsets — and a **basis** for it of at most 30
vectors, whatever n is.

### Building the basis

Keep at most one vector per leading bit:

```java
long[] basis = new long[31];                  // basis[b] has leading bit b, or 0
for (long x : a) {
    long cur = x;
    for (int b = 30; b >= 0; b--) {
        if (((cur >> b) & 1) == 0) continue;
        if (basis[b] == 0) { basis[b] = cur; break; }   // a new direction
        cur ^= basis[b];                                // reduce, keep looking
    }
    // cur == 0 means x was already reachable and adds nothing
}
```

This is Gaussian elimination, with XOR as the row operation. The number of
non-zero entries is the **rank**, r.

### What the basis answers

| Question | Answer |
| --- | --- |
| Largest achievable XOR | greedily XOR in `basis[b]` from the top whenever it raises the value |
| How many distinct values | exactly `2^r` |
| Is x achievable? | reduce x by the basis; achievable iff it reduces to 0 |
| k-th smallest value | fully reduce the basis, sort, and read the bits of k − 1 |

**Why 2^r.** Every reachable value is an XOR of basis vectors, so there are at
most 2^r. And no two distinct basis subsets collide: if `XOR(S) = XOR(T)` then
`XOR(S △ T) = 0` with `S △ T` non-empty, which independence forbids. At most and
at least, so exactly.

**Why greedy gives the maximum.** Each basis vector owns a distinct leading bit,
so XOR-ing `basis[b]` in flips bit b and touches nothing above it. Turning on
the highest available bit can never be regretted.

### The reduced basis, and counting

For the k-th smallest, clear each pivot bit out of every *other* vector:

```java
for (int b = 0; b <= 30; b++) {
    if (basis[b] == 0) continue;
    for (int h = b + 1; h <= 30; h++)
        if (((basis[h] >> b) & 1) == 1) basis[h] ^= basis[b];
}
```

Now each pivot lives in exactly one vector, so including vector i strictly
*raises* the value and disturbs no earlier choice. Sort the survivors ascending
and the 2^r values, in order, are indexed by the binary representation of the
position — the basis has become a counter. The answer is `k − 1` read as a mask,
because the smallest value is 0 from the empty subset.
""",
    signals=[
        _sig("“visit every state, changing one thing at a time”", "Gray code, `i ^ (i >> 1)`",
             "A Hamiltonian path on the hypercube."),
        _sig("A sensor or encoder that must not misread mid-transition", "Gray code",
             "One bit changing means a mid-change read is one of the two neighbours."),
        _sig("“maximum XOR of any subset”", "XOR basis, then greedy from the top bit",
             "2ⁿ subsets, at most 30 basis vectors."),
        _sig("“how many distinct XOR values”", "2 to the power of the rank",
             "The span is a subspace; its size is structural."),
        _sig("“can these numbers XOR to x?”", "Reduce x by the basis, check for 0",
             "Membership in the span."),
        _sig("“k-th smallest XOR value”", "Reduced basis, sorted, indexed by k − 1",
             "Reduction makes the order match binary counting."),
        _sig("Maximum XOR of a **pair** from the array", "A binary trie, not a basis",
             "Different question: a pair, not a subset. See `tries`."),
    ],
    skeletons=[
        _sk("Gray code, both directions",
            "Enumerating configurations; converting a reading to an index.",
            """
int gray(int i)  { return i ^ (i >> 1); }        // index -> code

int index(int g) {                               // code -> index
    for (int s = 1; s < 32; s <<= 1) g ^= g >> s;
    return g;
}

for (int i = 0; i < (1 << n); i++) visit(gray(i));
""",
            "Encoding is a difference of adjacent bits; decoding is their prefix XOR."),
        _sk("XOR basis (insert and maximise)",
            "Maximum subset XOR, reachability, rank.",
            """
long[] basis = new long[31];

boolean insert(long x) {                         // true if x added a new direction
    for (int b = 30; b >= 0; b--) {
        if (((x >> b) & 1) == 0) continue;
        if (basis[b] == 0) { basis[b] = x; return true; }
        x ^= basis[b];
    }
    return false;                                // x was already in the span
}

long maximum() {
    long best = 0;
    for (int b = 30; b >= 0; b--)
        if (basis[b] != 0 && (best ^ basis[b]) > best) best ^= basis[b];
    return best;
}
""",
            "`insert` returning false is also the membership test: x is reachable iff it reduces "
            "to 0."),
        _sk("Full reduction, for ordering",
            "k-th smallest achievable XOR.",
            """
for (int b = 0; b <= 30; b++) {
    if (basis[b] == 0) continue;
    for (int h = b + 1; h <= 30; h++)
        if (basis[h] != 0 && ((basis[h] >> b) & 1) == 1) basis[h] ^= basis[b];
}
long[] v = nonZeroAscending(basis);              // r vectors, distinct pivots
if (k > (1L << v.length)) return -1;

long ans = 0, idx = k - 1;                       // k is 1-based; 0 is the smallest value
for (int i = 0; i < v.length; i++)
    if (((idx >> i) & 1) == 1) ans ^= v[i];
""",
            "`1L`, not `1` — with r = 30 the count is a billion and an `int` shift is about "
            "to go negative."),
    ],
    traces=[
        _trace(
            "Building the XOR basis of {6, 5, 3, 8}",
            "`cur` is the value being reduced; it is stored at its leading bit if that slot is "
            "free, and XOR-ed with the occupant otherwise. `6 = 110`, `5 = 101`, `3 = 011`, "
            "`8 = 1000`.",
            ["x", "reduction", "outcome", "basis after (bit: value)"],
            [
                ["6 = 110", "leading bit 2 free", "stored", "2: 110"],
                ["5 = 101", "bit 2 taken → 101 ^ 110 = 011; bit 1 free", "stored", "2: 110, 1: 011"],
                ["3 = 011", "bit 1 taken → 011 ^ 011 = 000", "**absorbed**", "2: 110, 1: 011"],
                ["8 = 1000", "leading bit 3 free", "stored", "3: 1000, 2: 110, 1: 011"],
            ],
            "Rank 3, so exactly 2³ = 8 distinct values are reachable from four numbers. "
            "3 was absorbed because 6 ^ 5 = 3 already — it is in the span and adds nothing, "
            "which is why n can be 100000 while the basis never exceeds 30 entries. The maximum "
            "is built greedily from the top: 1000, then ^110 = 1110, then ^011 = 1101 = 13.",
        ),
        _trace(
            "The 3-bit Gray code, and why each step is one flip",
            "`g = i ^ (i >> 1)`. The last column is the bit that changed from the row above.",
            ["i", "i in binary", "gray(i)", "binary", "bit changed"],
            [
                ["0", "000", "0", "000", "—"],
                ["1", "001", "1", "001", "bit 0"],
                ["2", "010", "3", "011", "bit 1"],
                ["3", "011", "2", "010", "bit 0"],
                ["4", "100", "6", "110", "bit 2"],
                ["5", "101", "7", "111", "bit 0"],
                ["6", "110", "5", "101", "bit 1"],
                ["7", "111", "4", "100", "bit 0"],
            ],
            "Every step changes exactly one bit, including 3 → 4 where the *index* changed "
            "three bits at once. The first four codes are the 2-bit Gray code; the last four are "
            "it reversed with bit 2 set — the reflection, visible in the table.",
        ),
    ],
    costs=[
        _cost("gray(i) / index(g)", "O(1) / O(log W)", "O(1)", "W = word size; five shifts for 32 bits."),
        _cost("Enumerate an n-bit Gray code", "O(2ⁿ)", "O(1)", "Output-bound; nothing is stored."),
        _cost("Basis insert", "O(B)", "O(B)", "B = 30 bit positions."),
        _cost("Build a basis from n values", "O(n·B)", "O(B)", "3·10⁶ steps at n = 10⁵."),
        _cost("Maximum / membership", "O(B)", "O(1)", "One pass down the basis."),
        _cost("Full reduction", "O(B²)", "O(B)", "900 steps, regardless of n."),
        _cost("Enumerating subsets instead", "O(2ⁿ)", "O(1)", "What the basis replaces."),
    ],
    pitfalls=[
        _pit("The Gray code sequence repeats or skips values",
             "`i ^ (i << 1)` instead of `i >> 1`, or the loop ran to n instead of 2ⁿ.",
             "Shift **right**, and iterate i over 0 … 2ⁿ − 1."),
        _pit("The basis misses a value that is clearly reachable",
             "The reduction stopped at the first occupied slot instead of XOR-ing and continuing.",
             "On a collision, `cur ^= basis[b]` and keep scanning downwards; only an empty slot "
             "ends the loop."),
        _pit("The maximum comes out too small",
             "The greedy walked upwards from bit 0.",
             "Walk from the top bit down. A high bit is worth more than every lower bit "
             "combined, so it must be decided first."),
        _pit("The k-th smallest is out of order",
             "The basis was not fully reduced, so XOR-ing in a vector could clear a bit an "
             "earlier vector had set.",
             "Reduce until each pivot appears in exactly one vector, then sort ascending. Only "
             "then does mask order match value order."),
        _pit("The k-th smallest is off by one",
             "`k` was used as the mask directly.",
             "The smallest value is 0, from the empty subset, so the mask is `k - 1`."),
        _pit("2^r compared against k gives nonsense",
             "`1 << r` with r = 30 or 31 in `int` arithmetic.",
             "`1L << r`. The comparison is the only place the count appears, so an overflow "
             "there answers −1 for every k."),
    ],
    lessons=["bit_manip", "number_theory"],
    checks=[
        _chk("Why does `i ^ (i >> 1)` produce a sequence where neighbours differ in one bit?",
             "Adding 1 to i flips a run of trailing 1s and the 0 above them. In the XOR each "
             "output bit is the difference of two adjacent input bits, so within that run the "
             "changes cancel in pairs and exactly one survives."),
        _chk("Why does a set of 100000 numbers have a basis of at most 30 vectors?",
             "Because the values are below 2³⁰, so as vectors over GF(2) they live in a "
             "30-dimensional space. At most 30 can be independent; every other value is already "
             "an XOR of those and reduces to 0."),
        _chk("Why is the number of distinct subset XORs exactly 2^r?",
             "At most 2^r because every value is an XOR of basis vectors. At least 2^r because "
             "two distinct basis subsets with the same XOR would make their symmetric "
             "difference a non-empty combination XOR-ing to 0, contradicting independence."),
        _chk("Why is the greedy maximum optimal?",
             "Each basis vector owns a distinct leading bit, so XOR-ing it in flips that bit and "
             "nothing above it. A value with bit b set beats every value without it, whatever "
             "the lower bits do — so taking the highest available bit is never a mistake."),
        _chk("What does full reduction buy that an ordinary basis does not?",
             "It makes each pivot bit appear in exactly one vector, so including a vector always "
             "increases the value. That turns the sorted list of 2^r reachable values into "
             "binary counting over the sorted basis — which is what makes \"k-th smallest\" "
             "a lookup rather than a search."),
        _chk("\"Maximum XOR of any two elements\" — basis or trie?",
             "Trie. A basis answers questions about *subsets*; a pair is a different object. "
             "Insert the numbers into a binary trie and walk each one down the opposite branch."),
    ],
    bigo=[
        _bigo(r"""
for (long x : a) {                              // n values, B = 30 bit positions
    long cur = x;
    for (int b = B - 1; b >= 0; b--) {
        if (((cur >> b) & 1) == 0) continue;
        if (basis[b] == 0) { basis[b] = cur; break; }
        cur ^= basis[b];
    }
}
""", "O(n·B)", ["O(n·B)", "O(n)", "O(2ⁿ)", "O(n·B²)"],
            "Each value is reduced against at most B basis vectors, and B is 30 — a "
            "constant, but one worth naming because it is where the work is. Enumerating the "
            "subsets instead is O(2ⁿ), which at n = 10⁵ is not a number."),
        _bigo(r"""
Set<Long> seen = new HashSet<>();               // all subset XORs, by enumeration
for (int mask = 0; mask < (1 << n); mask++) {
    long x = 0;
    for (int i = 0; i < n; i++) if ((mask >> i & 1) == 1) x ^= a[i];
    seen.add(x);
}
""", "O(n·2ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(n²)", "O(n log n)"],
            "2ⁿ masks, each rebuilt from scratch in O(n). Iterating submasks smartly gets it "
            "to O(2ⁿ); the basis gets the *count* to O(n·B) without ever listing a "
            "value."),
        _bigo(r"""
for (int b = 0; b < B; b++) {                   // full reduction
    if (basis[b] == 0) continue;
    for (int h = b + 1; h < B; h++)
        if (((basis[h] >> b) & 1) == 1) basis[h] ^= basis[b];
}
""", "O(B²)", ["O(B²)", "O(n·B)", "O(B)", "O(n²)"],
            "900 operations at B = 30, independent of n. It is free next to the build — "
            "which is why \"k-th smallest\" costs no more than \"maximum\" once you know the "
            "trick."),
        _bigo(r"""
for (int i = 0; i < (1 << n); i++)              // emit the n-bit Gray code
    out.append(i ^ (i >> 1));
""", "O(2ⁿ)", ["O(2ⁿ)", "O(n·2ⁿ)", "O(n)", "O(n²)"],
            "One XOR and one shift per entry, and there are 2ⁿ entries — the output "
            "itself is the cost. The recursive \"list, then mirrored list\" construction builds "
            "the same sequence with O(2ⁿ) extra memory; the closed form needs none."),
        _bigo(r"""
long best = 0;                                  // maximum, given the basis
for (int b = B - 1; b >= 0; b--)
    if (basis[b] != 0 && (best ^ basis[b]) > best) best ^= basis[b];
""", "O(B)", ["O(B)", "O(n)", "O(n·B)", "O(2^B)"],
            "Thirty steps, whatever n was. All of the cost is in the build; the queries are "
            "free — the same shape as every other precompute-then-answer structure in this "
            "stage."),
    ],
    interview="""
The tell for a basis is *"any subset"* plus a large n. Say the reframing out
loud — "XOR has no carries, so these are vectors over GF(2) and I want a basis" —
and the rest is Gaussian elimination, which the interviewer already believes you
can do.

Do not confuse it with the trie question. "Maximum XOR of a **pair**" is a trie;
"maximum XOR of a **subset**" is a basis. Getting that distinction right in the
first sentence is most of the score.
""",
    rungs=[
        _rung("Warm up", "An order where one thing changes at a time.",
              ["gray-code-sequence"],
              {"gray-code-sequence": "Write the mirrored construction for n = 3 by hand first, then check it against `i ^ (i >> 1)`. Seeing them agree is the point."}),
        _rung("Core", "The basis, and what its size alone tells you.",
              ["max-xor-subset", "count-distinct-xor-values"],
              {"max-xor-subset": "Build the basis, then walk down from the top bit. Try a set containing a duplicate and watch it get absorbed.",
               "count-distinct-xor-values": "The same build; the answer is 2 to the rank. If you find yourself storing values in a set, the structure has not landed yet."}),
        _rung("Stretch", "Reduction, which turns the span into a sorted list.",
              ["kth-smallest-subset-xor"],
              {"kth-smallest-subset-xor": "Reduce fully, sort, index by k − 1. Check k = 1 gives 0 and k = 2^r + 1 gives −1 before anything else."}),
    ],
    next_up="""
Numbers as vectors. The next unit changes the *shape* of a DP state instead —
digits rather than items — and then attacks the cost of a transition rather than
the number of states.
""",
)


# --- Unit 43 — Advanced DP ---------------------------------------------------

_unit(
    "dp-advanced", "DP Beyond the Table: Digits, Windows & Halves", "🧮", _S8,
    "Change what the state is, then make each transition cheaper.",
    weight=1,
    prereqs=["dp-1d", "dp-knapsack", "queues-and-deques"],
    why="""
Stage 7 covers DP over indices, capacities, grids, pairs of sequences, intervals
and state machines. All six share a shape: the state is a position in the input,
and the transition is a short loop.

Three common problems break that shape, and each breaks it differently:

- **"How many integers in [1, N] …"** with N up to 10¹⁸. There is no array to
  index. The state has to be the *digits*.
- **`dp[i] = a[i] + min(dp[i-k] … dp[i-1])`** with n and k both 10⁵. The states
  are fine; the transition is O(k) and that is the whole cost.
- **n ≤ 40, and a capacity too large to index.** Neither 2ⁿ nor the knapsack
  table fits — but 2ⁿ/² does.

Each fix is worth knowing on its own, and together they are what people mean by
"DP optimisation".
""",
    model="""
### Digit DP

When the bound is a *number* rather than a count, run the DP over its decimal
digits — at most 19 of them — left to right. The state is:

> **(position, still tight, whatever the condition needs)**

`tight` means every digit so far equals N's, so the next digit is capped at N's;
once you go strictly below, every remaining position is free and the count
becomes a clean precomputed table.

```java
long count = 0;
for (int i = 0; i < D; i++) {
    int cap = s[i] - '0';
    for (int d = 0; d < cap; d++)          // the first position that goes below N
        count += free[D - i - 1][stateAfter(d)];
    if (deadEnd(cap)) return count;        // N's own prefix is illegal; tight branch dies
    carryState(cap);                       // stay tight
}
return count + (stateIsGood() ? 1 : 0);    // N itself
```

`free[len][state]` is "ways to fill `len` unconstrained positions and end in
`state`", built once by a small recurrence.

The third piece of state is whatever the question needs, and nothing more:
digit sum → the sum **mod k**; no digit 7 → nothing at all; strictly increasing
digits → the previous digit; distinct digits → a 10-bit mask. A fourth flag,
`started`, is needed only when leading zeros differ from real zeros.

### Optimising a transition: the monotonic deque

```java
dp[i] = a[i] + min(dp[i - k] … dp[i - 1]);    // O(n·k) as written
```

The inner `min` is over a **sliding window** of the dp array — the same window
that moves one step right when i does. Keep a deque of indices whose dp values
increase from front to back:

```java
Deque<Integer> dq = new ArrayDeque<>();
dq.addLast(0);
for (int i = 1; i < n; i++) {
    while (dq.peekFirst() < i - k) dq.pollFirst();        // left the window
    dp[i] = a[i] + dp[dq.peekFirst()];                    // the window minimum
    while (!dq.isEmpty() && dp[dq.peekLast()] >= dp[i]) dq.pollLast();
    dq.addLast(i);
}
```

A candidate `j < i` with `dp[j] >= dp[i]` is **dominated**: it expires sooner
and is never better. Discarding dominated candidates is the whole idea, and it
is the same discipline as a monotonic stack. Each index is pushed once and
popped once, so the two nested `while`s are O(1) amortized and the loop is O(n).

The recurrence did not change. Only the speed of evaluating it did — which is
what "DP optimisation" always means.

> The heavier members of the family are the same idea with a different notion of
> dominated: **convex hull trick** when the transition is `min over j of
> (m_j · x + c_j)`, and **divide-and-conquer optimisation** when the optimal
> split point is monotone in i. Both discard candidates no future i can want.

### Meet in the middle

When n ≈ 40, 2ⁿ ≈ 10¹² is hopeless and 2ⁿ/² ≈ 10⁶ is instant. Split the items
in half, enumerate every subset of each half, and pair the halves with a sort
and a binary search instead of another loop:

```java
long[] left  = allSubsetSums(a, 0, n / 2);
long[] right = allSubsetSums(a, n / 2, n);
Arrays.sort(right);
for (long s : left)
    best = max(best, s + largestAtMost(right, W - s));
```

Every subset is a left subset together with a right subset, independently, so
nothing is missed and nothing is counted twice.

### Reading the constraint

| Constraint | Technique |
| --- | --- |
| Bound is a *number* up to 10¹⁸ | Digit DP |
| n ≤ 20 | Plain 2ⁿ enumeration |
| n ≤ 40, capacity huge | Meet in the middle |
| n ≤ 10⁵, capacity small | The knapsack table |
| n, k ≤ 10⁵ and the transition is a window min/max | Monotonic deque |

The same-looking question gets four different answers, and the constraint line
is what chooses.
""",
    signals=[
        _sig("“how many integers in [L, R] such that …”, R huge",
             "Digit DP, and answer(R) − answer(L − 1)",
             "19 positions instead of 10¹⁸ candidates."),
        _sig("A digit condition that depends on all digits so far", "Carry it *reduced*",
             "Digit sum → sum mod k; distinct digits → a 10-bit mask."),
        _sig("`dp[i] = f(a[i]) + min/max over a window of dp`", "Monotonic deque",
             "The transition is a sliding-window extremum."),
        _sig("The transition is `min over j of (m_j · x_i + c_j)`", "Convex hull trick",
             "Lines, and only the lower envelope can ever win."),
        _sig("The optimal split point never moves left as i grows", "Divide-and-conquer optimisation",
             "Monotone argmin turns O(n²) into O(n log n)."),
        _sig("`n ≤ 40` and the value range rules out a table", "Meet in the middle",
             "2⁴⁰ is hopeless; two halves of 2²⁰ are not."),
        _sig("`n ≤ 20`", "Plain subset enumeration",
             "Do not split what already fits."),
    ],
    skeletons=[
        _sk("Digit DP with a carried residue",
            "“Count x ≤ N whose digits satisfy …”.",
            """
char[] s = Long.toString(N).toCharArray();
int D = s.length;

long[][] free = new long[D + 1][k];              // ways to fill len free positions -> residue
free[0][0] = 1;
for (int len = 1; len <= D; len++)
    for (int r = 0; r < k; r++)
        for (int d = 0; d <= 9; d++)
            free[len][r] += free[len - 1][((r - d) % k + k) % k];

long count = 0;
int sum = 0;
for (int i = 0; i < D; i++) {
    int cap = s[i] - '0';
    for (int d = 0; d < cap; d++)
        count += free[D - i - 1][((-(sum + d)) % k + k) % k];
    sum += cap;
}
if (sum % k == 0) count++;                       // N itself
""",
            "`((x % k) + k) % k` — Java's `%` keeps the sign, and a negative index throws."),
        _sk("Window-minimum DP",
            "A transition that is a min or max over the last k states.",
            """
Deque<Integer> dq = new ArrayDeque<>();
long[] dp = new long[n];
dp[0] = a[0];
dq.addLast(0);
for (int i = 1; i < n; i++) {
    while (dq.peekFirst() < i - k) dq.pollFirst();
    dp[i] = a[i] + dp[dq.peekFirst()];
    while (!dq.isEmpty() && dp[dq.peekLast()] >= dp[i]) dq.pollLast();
    dq.addLast(i);
}
""",
            "Flip the comparison for a maximum. The deque holds *indices*, so the window test "
            "can be done at all."),
        _sk("Meet in the middle",
            "n around 40, with a range too big to index.",
            """
static long[] subsetSums(int[] a, int from, int to) {
    int m = to - from;
    long[] res = new long[1 << m];
    for (int mask = 1; mask < (1 << m); mask++) {
        int low = Integer.numberOfTrailingZeros(mask);
        res[mask] = res[mask & (mask - 1)] + a[from + low];   // one add per mask
    }
    return res;
}
""",
            "`mask & (mask - 1)` clears the lowest set bit, so each sum is built from an already "
            "computed one — O(2ᵐ) total instead of O(m·2ᵐ)."),
    ],
    traces=[
        _trace(
            "The window-minimum deque on dp = [1, 6, 2, 9, 3] with k = 2",
            "`dp[i] = a[i] + min(dp[i-2], dp[i-1])` for a = [1, 5, 2, 9, 3]. The deque holds "
            "indices with increasing dp; the front is always the window's minimum.",
            ["i", "window", "deque before", "dp[i]", "popped from back", "deque after"],
            [
                ["0", "—", "[]", "**1**", "—", "[0:1]"],
                ["1", "dp[0]", "[0:1]", "5 + 1 = **6**", "none (1 < 6)", "[0:1, 1:6]"],
                ["2", "dp[0], dp[1]", "[0:1, 1:6]", "2 + 1 = **3**", "1:6 (6 ≥ 3)", "[0:1, 2:3]"],
                ["3", "dp[1], dp[2]", "[0:1, 2:3]", "9 + 3 = **12**", "none (3 < 12)", "[2:3, 3:12]"],
                ["4", "dp[2], dp[3]", "[2:3, 3:12]", "3 + 3 = **6**", "3:12 (12 ≥ 6)", "[2:3, 4:6]"],
            ],
            "At i = 3 index 0 left the window and was dropped from the front; at i = 2 index 1 "
            "was dropped from the *back* because dp[1] = 6 can never beat dp[2] = 3 and expires "
            "first. Five indices, five pushes, three pops — that is why two nested `while`s "
            "inside a `for` are O(n) and not O(n·k).",
        ),
    ],
    costs=[
        _cost("Digit DP", "O(D · states · 10)", "O(D · states)", "D ≤ 19, whatever N is."),
        _cost("Window-min DP", "O(n)", "O(k)", "Amortized O(1) per state."),
        _cost("The same DP, written directly", "O(n·k)", "O(n)", "10¹⁰ at n = k = 10⁵."),
        _cost("Meet in the middle", "O(2^(n/2) · n)", "O(2^(n/2))", "n = 40 → about 10⁶ per half."),
        _cost("Plain subset enumeration", "O(2ⁿ)", "O(1)", "Fine to n ≈ 20, hopeless at 40."),
        _cost("Convex hull trick", "O(n) or O(n log n)", "O(n)", "For `min(mⱼ·x + cⱼ)` transitions."),
    ],
    pitfalls=[
        _pit("A digit DP is off by exactly one",
             "The walk counts 0 … N and the question asks for 1 … N — or N itself "
             "was never added after the loop.",
             "Count [0, N], then subtract the x = 0 case if it qualifies; add N separately if "
             "the tight branch survived to the end."),
        _pit("`ArrayIndexOutOfBoundsException: -1` in a digit DP",
             "A residue was computed with Java's `%`, which returns a negative result for a "
             "negative left operand.",
             "`((x % k) + k) % k`. Python's `%` does not do this, which is how the same logic "
             "passes in one language and throws in the other."),
        _pit("A `started` flag was added and the count changed",
             "Leading zeros only need distinguishing when the condition cares about them.",
             "For “no digit 7” a leading zero is harmless, so no flag is needed. For "
             "“digits strictly increasing” it is essential. Add it when the condition "
             "asks, not by reflex."),
        _pit("The deque returns a stale minimum",
             "Indices that have left the window are dropped only when the deque is non-empty, "
             "or the front check runs after the read.",
             "Drop from the front *before* reading `dp[dq.peekFirst()]`, every iteration."),
        _pit("The deque stores values instead of indices",
             "Then there is no way to tell whether the front has expired.",
             "Store indices and compare them to `i - k`; look the value up when you need it."),
        _pit("Meet in the middle overflows or misses the empty subset",
             "An `int` accumulator, or halves enumerated from mask 1.",
             "Sums are `long`, and both halves must include mask 0 — “take nothing from "
             "this side” is a legal choice."),
    ],
    lessons=["dp", "dp2d", "math_digits", "sliding_window"],
    checks=[
        _chk("What are the three pieces of a digit DP's state?",
             "Position, whether the prefix is still equal to the bound's ('tight'), and whatever "
             "the condition needs — reduced as far as possible, e.g. the digit sum **mod k** "
             "rather than the sum. A `started` flag is a fourth, needed only when leading zeros "
             "must be told from real ones."),
        _chk("Once a digit DP goes strictly below N, why is the rest a lookup?",
             "Because every remaining position is unconstrained, so the number of completions "
             "depends only on how many positions are left and which state they must reach — "
             "a table computed once, independent of N."),
        _chk("Why is a loop containing an inner `while` that can empty the deque still O(n)?",
             "Each index is pushed exactly once, so it can be popped at most once. Over the "
             "whole loop there are at most n pops, not n per iteration — O(1) amortized."),
        _chk("In the window-minimum deque, why is it safe to pop from the back?",
             "A candidate j < i with dp[j] >= dp[i] is dominated: it leaves the window earlier "
             "*and* is never smaller, so no future i can prefer it. Dominated candidates are "
             "exactly what a monotonic structure throws away."),
        _chk("When does `n <= 40` mean meet in the middle rather than a knapsack table?",
             "When the other dimension — capacity, target sum — is too large to index. "
             "A small capacity means the O(n·W) table whatever n is; a huge one with n "
             "around 40 means splitting into halves of 2²⁰."),
        _chk("Does a DP optimisation change the recurrence?",
             "No. The states and the transitions are identical; only the cost of *evaluating* a "
             "transition changes. That is why the first step is always to write the slow "
             "recurrence and check it on small inputs."),
    ],
    bigo=[
        _bigo(r"""
for (int i = 1; i < n; i++)                     // dp[i] = a[i] + min(dp[i-k..i-1])
    for (int j = Math.max(0, i - k); j < i; j++)
        dp[i] = Math.min(dp[i], a[i] + dp[j]);
""", "O(n·k)", ["O(n·k)", "O(n)", "O(n log n)", "O(n²)"],
            "n states, each scanning k predecessors. At n = k = 10⁵ that is 10¹⁰. "
            "The deque version computes the identical dp array in O(n) — same recurrence, "
            "different evaluation."),
        _bigo(r"""
Deque<Integer> dq = new ArrayDeque<>();          // the same recurrence, optimised
for (int i = 1; i < n; i++) {
    while (dq.peekFirst() < i - k) dq.pollFirst();
    dp[i] = a[i] + dp[dq.peekFirst()];
    while (!dq.isEmpty() && dp[dq.peekLast()] >= dp[i]) dq.pollLast();
    dq.addLast(i);
}
""", "O(n)", ["O(n)", "O(n log k)", "O(n·k)", "O(n log n)"],
            "Two nested `while`s and still linear: each index is pushed once and popped once, "
            "so both loops together run at most 2n times over the whole `for`. Amortized O(1) "
            "per state."),
        _bigo(r"""
long count = 0;                                  // digit DP over N, D digits, k residues
for (int i = 0; i < D; i++)
    for (int d = 0; d < 10; d++)
        count += free[D - i - 1][someResidue(d)];
// plus building free[D][k] with D * k * 10 work
""", "O(D·k)", ["O(D·k)", "O(N)", "O(log N)", "O(D·k·10^D)"],
            "D ≤ 19 and k ≤ 100, so about 19000 steps — and completely independent "
            "of N. That independence is the point: the same code costs the same at N = 100 and "
            "N = 10¹⁸."),
        _bigo(r"""
long[] left = allSubsetSums(a, 0, n / 2);        // n = 40
long[] right = allSubsetSums(a, n / 2, n);
Arrays.sort(right);
for (long s : left) binarySearch(right, W - s);
""", "O(2^(n/2) · n)", ["O(2^(n/2) · n)", "O(2ⁿ)", "O(n·W)", "O(2^(n/2))"],
            "Each half has 2²⁰ ≈ 10⁶ sums; the sort is O(2ⁿ/² log "
            "2ⁿ/²) = O(2ⁿ/² · n/2) and the searches match it. Halving the "
            "exponent turns 10¹² into 2·10⁷."),
        _bigo(r"""
for (int mask = 1; mask < (1 << m); mask++) {    // all subset sums of one half
    int low = Integer.numberOfTrailingZeros(mask);
    res[mask] = res[mask & (mask - 1)] + a[low];
}
""", "O(2ᵐ)", ["O(2ᵐ)", "O(m·2ᵐ)", "O(3ᵐ)", "O(2ᵐ log m)"],
            "One addition per mask, because `mask & (mask - 1)` is a mask already computed — "
            "it is strictly smaller. Summing each mask's bits from scratch would be "
            "O(m·2ᵐ), twenty times slower for the same answer."),
    ],
    interview="""
Do the slow version first, out loud: *"the recurrence is dp[i] = a[i] + min over
the last k, which is O(n·k)"*. Then optimise it. Jumping straight to a deque
without stating the recurrence it evaluates reads as a memorised trick, and it is
also how people end up optimising a recurrence that was wrong.

For counting problems, the constraint is the whole hint. `N ≤ 10¹⁸` said out
loud as *"so the DP is over the 19 digits, not over the values"* is most of the
answer before any code.
""",
    rungs=[
        _rung("Warm up", "The bound is a number, so the DP runs over its digits.",
              ["count-digit-free-numbers"],
              {"count-digit-free-numbers": "Two pieces of state and no third. Then find the base-9 shortcut, and notice it does not survive the condition changing — which is why the DP is worth writing."}),
        _rung("Core", "A third piece of state, and a transition made cheaper.",
              ["digit-sum-divisible-count", "min-cost-jump-window"],
              {"digit-sum-divisible-count": "Carry the digit sum *mod k*. Watch Java's negative `%` — it is the one that throws.",
               "min-cost-jump-window": "Write the O(n·k) version first and keep it as an oracle; then replace the inner loop with a deque and diff the two dp arrays."}),
        _rung("Stretch", "Halve the exponent.",
              ["subset-sum-closest-below"],
              {"subset-sum-closest-below": "Read the constraint before the statement: n ≤ 40 with a capacity of 10¹⁸ has exactly one intended answer."}),
    ],
    next_up="""
Optimising a search over subsets. The next unit is about a search the core
course cannot express at all: pairing things up, and the flow-versus-cut duality
underneath it.
""",
)


# --- Unit 44 — Flows and matching --------------------------------------------

_unit(
    "flows-and-matching", "Flows, Cuts & Matchings", "🔗", _S8,
    "Pair things up, and the duality that says when you cannot do better.",
    weight=1,
    prereqs=["graph-traversal", "backtracking", "greedy"],
    why="""
"Assign these to those" is one of the most common shapes a real problem takes —
workers to shifts, students to projects, rows to columns — and nothing in the
core course can do it. `graph-traversal` two-colours a graph and calls it
bipartite, which answers a different question entirely.

Greedy fails, and fails in an instructive way: give each worker their first
available task and worker 0 may take the only task worker 1 can do. The repair
is the **augmenting path** — displace the current holder and ask *it* to move —
and it is the engine under every algorithm in this unit.

The same idea, with capacities instead of single slots, is **max flow**. And max
flow has a twin: the cheapest set of edges whose removal disconnects source from
sink. Two questions, one computation.
""",
    model="""
### Augmenting paths

Keep a partial matching. To add a left vertex `u`:

```java
boolean place(int u, boolean[] tried) {
    for (int v : adj[u]) {
        if (tried[v]) continue;
        tried[v] = true;                                 // once per SEARCH
        if (owner[v] == -1 || place(owner[v], tried)) {  // free, or its owner can move
            owner[v] = u;
            return true;
        }
    }
    return false;
}
```

A successful search never reduces the number of matched pairs — it reroutes
several and adds exactly one. `tried` is reset for every search: within one
search it stops two vertices bouncing a slot between them; across searches,
resetting is what allows an earlier decision to be undone.

**Kuhn's algorithm** is just this, run once per left vertex:

```java
for (int u = 0; u < nl; u++) if (place(u, new boolean[nr])) pairs++;
```

One pass is enough, because augmenting never un-matches anybody: a vertex that
cannot be matched now cannot become matchable later.

**Berge's theorem** is why the result is optimal. Take the symmetric difference
of your matching and any larger one; it splits into alternating paths and
cycles, and a larger matching forces one component to be an augmenting path for
yours. No augmenting path, no larger matching.

### Max flow

Give the edges capacities. Repeatedly find a source→sink path with spare
capacity and push as much as its tightest edge allows:

```java
while (bfsFindsAugmentingPath()) {
    push = min capacity along the path;
    for each edge e on the path { cap[e] -= push; cap[e ^ 1] += push; }
    flow += push;
}
```

Store edges in **pairs**, so edge `e` and its reverse are `e` and `e ^ 1`. The
reverse edge is what lets a later path undo part of an earlier decision — and
because it is an ordinary edge, "undo" needs no special case at all. Without it
the greedy sticks below the maximum.

Using **BFS** for the path is what makes this Edmonds–Karp rather than
Ford–Fulkerson, and it bounds the rounds at O(V·E) independent of the
capacities. With DFS, two edges of capacity 10⁹ either side of a bridge of
capacity 1 can take a billion alternating pushes.

### Max-flow min-cut

> The maximum flow from s to t equals the minimum total capacity of a set of
> edges whose removal leaves no s→t path.

Both halves are short. *Any* cut bounds *any* flow, because everything reaching
the sink crosses it. And when no augmenting path remains, the vertices still
reachable from s in the residual network form a cut whose forward edges are all
saturated and whose backward edges are all empty — so its capacity *equals* the
flow. A flow meeting a cut certifies both.

This is why a question phrased as "the cheapest way to disconnect" is answered
by computing a flow.

### König and the reductions

On a **bipartite** graph the same duality specialises:

| Quantity | Equals |
| --- | --- |
| Maximum matching | Minimum vertex cover (König) |
| Maximum independent set | `nl + nr − matching` |
| Minimum path cover of a **DAG** | `n − matching` on the split graph |

The last one is the reduction worth practising. Split every vertex into an
"out" copy on the left and an "in" copy on the right; an edge `u → v` becomes
`out(u) — in(v)`. A matching is then a set of edges no vertex leaves twice and
none enters twice — a set of vertex-disjoint paths. Start from n one-vertex
paths; each matched edge glues two of them together.

Acyclicity matters: in a general digraph the matched edges could form a cycle,
which joins k paths with k edges instead of k − 1 and breaks the count.
""",
    signals=[
        _sig("“assign each X to a distinct Y”", "Bipartite matching",
             "Greedy fails; augmenting paths repair it."),
        _sig("“the most pairs that can be formed at once”", "Kuhn's algorithm",
             "One augmenting search per left vertex."),
        _sig("“can every X be assigned?”", "Matching size == nl",
             "A `NO` means some k of them share fewer than k options (Hall)."),
        _sig("“cheapest set of edges to disconnect s from t”", "Max flow",
             "Min cut = max flow; compute the flow."),
        _sig("Capacities, a single source and a single sink", "Edmonds–Karp",
             "BFS for the path bounds the rounds independently of capacity."),
        _sig("“fewest chains / paths covering everything”, on a DAG", "n − max matching",
             "Split each vertex into out and in copies."),
        _sig("“fewest rows and columns covering every marked cell”", "König: minimum vertex cover = maximum matching",
             "The dual, in disguise."),
        _sig("Several sources or several sinks", "Add a super-source and super-sink",
             "Infinite-capacity edges to the real ones."),
    ],
    skeletons=[
        _sk("Kuhn's algorithm",
            "Maximum bipartite matching.",
            """
int[] owner = new int[nr];                       // which left vertex holds each right vertex
Arrays.fill(owner, -1);

boolean place(int u, boolean[] tried) {
    for (int v : adj[u]) {
        if (tried[v]) continue;
        tried[v] = true;
        if (owner[v] == -1 || place(owner[v], tried)) { owner[v] = u; return true; }
    }
    return false;
}

int pairs = 0;
for (int u = 0; u < nl; u++) if (place(u, new boolean[nr])) pairs++;
""",
            "`tried` is per search, not global. A fresh array each time is what lets earlier "
            "decisions be revisited."),
        _sk("Edmonds–Karp",
            "Max flow, and therefore min cut.",
            """
// edges stored in pairs: e and e ^ 1 are each other's reverse
int addEdge(int u, int v, long c) {
    to[ec] = v; cap[ec] = c; g[u].add(ec++);
    to[ec] = u; cap[ec] = 0; g[v].add(ec++);     // reverse, capacity 0
    return ec - 2;
}

long maxFlow(int s, int t) {
    long flow = 0;
    while (true) {
        int[] par = new int[n];
        Arrays.fill(par, -1);
        par[s] = -2;
        Deque<Integer> q = new ArrayDeque<>();
        q.add(s);
        while (!q.isEmpty() && par[t] == -1) {
            int u = q.poll();
            for (int e : g[u]) if (cap[e] > 0 && par[to[e]] == -1) { par[to[e]] = e; q.add(to[e]); }
        }
        if (par[t] == -1) return flow;
        long push = Long.MAX_VALUE;
        for (int v = t; v != s; v = to[par[v] ^ 1]) push = Math.min(push, cap[par[v]]);
        for (int v = t; v != s; v = to[par[v] ^ 1]) { cap[par[v]] -= push; cap[par[v] ^ 1] += push; }
        flow += push;
    }
}
""",
            "`to[e ^ 1]` is the edge's *source*, which is how the path is walked backwards "
            "without storing it."),
        _sk("Minimum path cover of a DAG",
            "“Fewest chains covering every vertex.”",
            """
// out(u) on the left, in(v) on the right, one edge per arc
for (int[] arc : arcs) adj[arc[0]].add(arc[1]);
return n - kuhn(n, n, adj);
""",
            "Only valid because the graph is acyclic: a cycle among the matched edges would "
            "make the arithmetic wrong."),
    ],
    traces=[
        _trace(
            "An augmenting path that displaces two workers",
            "Worker 0 can do task A only; worker 1 can do A or B; worker 2 can do B or C. "
            "Placing them in order forces two displacements.",
            ["step", "who is searching", "wants", "state of that task", "result", "assignment after"],
            [
                ["1", "worker 0", "A", "free", "takes it", "A←0"],
                ["2", "worker 1", "A", "held by 0", "ask 0 to move", "A←0"],
                ["3", "  → worker 0", "—", "A already tried this search", "**fails**", "A←0"],
                ["4", "worker 1", "B", "free", "takes it", "A←0, B←1"],
                ["5", "worker 2", "B", "held by 1", "ask 1 to move", "A←0, B←1"],
                ["6", "  → worker 1", "C", "free", "1 moves to C", "A←0, C←1"],
                ["7", "worker 2", "B", "now free", "takes it", "**A←0, B←2, C←1**"],
            ],
            "Step 3 is why `tried` exists: without it worker 0 would try A again forever. Steps "
            "5–7 are the augmenting path — worker 1 was moved, not evicted, so the "
            "count went from 2 to 3 and never dipped. Greedy without displacement would have "
            "stopped at two pairs.",
        ),
    ],
    costs=[
        _cost("Kuhn's algorithm", "O(V · E)", "O(V + E)", "Fine to about 10⁵ edges."),
        _cost("Hopcroft–Karp", "O(E · √V)", "O(V + E)", "Many shortest augmenting paths at once."),
        _cost("Edmonds–Karp", "O(V · E²)", "O(V + E)", "Independent of the capacities."),
        _cost("Dinic's algorithm", "O(V² · E)", "O(V + E)", "O(E√V) on unit capacities."),
        _cost("Ford–Fulkerson with DFS", "O(E · maxflow)", "O(V + E)", "Capacity-dependent; avoid."),
        _cost("Minimum path cover of a DAG", "O(V · E)", "O(V + E)", "One matching, then n − it."),
    ],
    pitfalls=[
        _pit("The matching search loops forever",
             "The `tried` array is not marked before recursing, so two vertices pass a slot back "
             "and forth.",
             "Mark `tried[v] = true` *before* the recursive call, every time."),
        _pit("The matching is too small",
             "`tried` is shared across searches instead of reset per left vertex.",
             "A fresh array per search. Sharing it forbids exactly the rerouting the algorithm "
             "depends on."),
        _pit("Max flow stops below the true maximum",
             "No reverse edges, so an early greedy path can never be partly undone.",
             "Add every edge with a paired reverse of capacity 0, and push flow back along it."),
        _pit("Max flow is correct but times out on big capacities",
             "The augmenting path is found by DFS, so the number of rounds tracks the capacity "
             "values.",
             "Use BFS (Edmonds–Karp), or Dinic. The bound then depends only on V and E."),
        _pit("Flow values overflow",
             "Thousands of edges with capacities near 10⁹.",
             "Capacities, the bottleneck and the total are all `long`."),
        _pit("`n − matching` gives the wrong path cover",
             "The graph has a cycle, so the matched arcs can form a closed loop.",
             "The identity holds for DAGs only. Check acyclicity, or say so when you state the "
             "reduction."),
    ],
    lessons=["graph_repr", "bfs", "backtracking"],
    checks=[
        _chk("Why does greedy matching fail, and what exactly repairs it?",
             "Greedy can hand a vertex the only option some later vertex has. The repair is the "
             "augmenting path: instead of giving up, ask the current holder to move somewhere "
             "else, recursively. That reroutes existing pairs and adds exactly one."),
        _chk("Why is one pass over the left vertices enough for Kuhn's algorithm?",
             "Because augmenting never un-matches anybody — it only reroutes. So a vertex "
             "that has no augmenting path now will not gain one later, and retrying it would "
             "find the same failure."),
        _chk("What does a reverse edge mean in a flow network?",
             "Permission to undo. Pushing flow along it cancels flow previously pushed the other "
             "way, so 'change my mind about an earlier path' becomes an ordinary augmenting "
             "path with no special case."),
        _chk("State the max-flow min-cut theorem and say why it is true.",
             "The maximum flow equals the minimum cut capacity. Any cut bounds any flow, since "
             "all flow crosses it. And when no augmenting path remains, the set reachable from s "
             "in the residual graph is a cut with every forward edge saturated and every "
             "backward edge empty — so its capacity equals the flow, and both are optimal."),
        _chk("Why is the minimum path cover of a DAG `n − maximum matching`?",
             "Split each vertex into an out-copy and an in-copy. A matching is a set of arcs no "
             "vertex leaves or enters twice — a set of disjoint paths. Starting from n "
             "single-vertex paths, each matched arc merges two, so the count drops by the "
             "matching size. Acyclicity is what stops the matched arcs forming a cycle."),
        _chk("How do you handle several sources and several sinks?",
             "Add a super-source with infinite-capacity edges to every real source, and a "
             "super-sink fed by every real sink. The max flow between them is the answer, and "
             "the model is unchanged."),
    ],
    bigo=[
        _bigo(r"""
for (int u = 0; u < nl; u++)                    // Kuhn: V left vertices, E edges
    place(u, new boolean[nr]);                  // one DFS over the edges
""", "O(V·E)", ["O(V·E)", "O(E)", "O(V + E)", "O(V²·E)"],
            "One augmenting search per left vertex, and each walks each edge at most once. "
            "Hopcroft–Karp finds many shortest augmenting paths per phase and gets "
            "O(E√V) — worth the name when Kuhn measurably stalls."),
        _bigo(r"""
while (bfsFindsPath()) {                        // Edmonds-Karp
    push = bottleneck(path);
    applyAlongPath(push);
}
""", "O(V·E²)", ["O(V·E²)", "O(E·maxflow)", "O(V + E)", "O(V²)"],
            "Each BFS is O(E), and taking a *shortest* augmenting path bounds the number of "
            "rounds at O(V·E) — with no reference to the capacities. The same loop with "
            "DFS is O(E·maxflow), which a bridge of capacity 1 between two edges of "
            "capacity 10⁹ turns into a billion rounds."),
        _bigo(r"""
for (int u = 0; u < n; u++)                     // "can every X be assigned?" by brute force
    for (int subset = 0; subset < (1 << n); subset++)
        checkHallsCondition(subset);
""", "O(n·2ⁿ)", ["O(n·2ⁿ)", "O(n²)", "O(n·E)", "O(2ⁿ)"],
            "Hall's theorem is the right *explanation* and the wrong *algorithm*: verifying it "
            "directly means looking at every subset of one side. The matching answers the same "
            "question in O(V·E) and, on failure, the unreachable set names the offending "
            "group for free."),
        _bigo(r"""
long matched = kuhn(n, n, splitGraph);          // minimum path cover of a DAG
return n - matched;
""", "O(V·E)", ["O(V·E)", "O(V + E)", "O(V²)", "O(2^V)"],
            "The reduction itself is free — building the split graph is one pass over the "
            "arcs — so the cost is exactly the matching's. That is what makes recognising "
            "the reduction worth more than any implementation."),
        _bigo(r"""
for (int e : allEdges)                          // min cut by trying every subset of edges
    for (int subset = 0; subset < (1 << m); subset++)
        if (disconnects(subset)) best = min(best, capacity(subset));
""", "O(2ᵐ·(V+E))", ["O(2ᵐ·(V+E))", "O(m²)", "O(V·E²)", "O(m log m)"],
            "The definition of a min cut is exponential to check. Max-flow min-cut replaces it "
            "with a polynomial computation of a completely different quantity — which is why "
            "the theorem, not the algorithm, is the thing to remember."),
    ],
    interview="""
Two sentences win this whole area. The first is the reframing: *"this is a
bipartite matching — the workers on one side, the shifts on the other."* The
second is the bound: *"maximum matching equals minimum vertex cover here, so the
answer is also the fewest people I need to cover every requirement."*

For anything phrased as cutting or separating, say *"min cut equals max flow"*
before writing code, and then compute the flow.

Almost nobody is asked to implement Dinic's algorithm from scratch. Being able
to *spot* a flow problem, state the model (what are the vertices, what are the
capacities) and name the right algorithm is what is actually being tested.
""",
    rungs=[
        _rung("Warm up", "Greedy fails; displacement fixes it.",
              ["assign-all-workers"],
              {"assign-all-workers": "Write the recursion and trace the displacement chain by hand on the 2×2 case. Then take `tried` out and watch it loop — that is what it is for."}),
        _rung("Core", "The same search, counted; and the same idea with capacities.",
              ["bipartite-max-matching", "min-cut-capacity"],
              {"bipartite-max-matching": "Kuhn is the warm-up with the failure counted instead of fatal. Be able to say why one pass suffices.",
               "min-cut-capacity": "The statement is a cut and the code is a flow. Store edges in pairs so `e ^ 1` is the reverse, and use BFS for the path."}),
        _rung("Stretch", "A matching where nothing mentions matching.",
              ["min-path-cover-dag"],
              {"min-path-cover-dag": "Split each vertex in two, match, subtract. Then work out what goes wrong if the graph has a cycle — that is the follow-up question."}),
    ],
    next_up="""
Pairing and cutting. The next unit changes domain entirely: points in the plane,
where the whole toolkit is one integer expression.
""",
)


# --- Unit 45 — Geometry ------------------------------------------------------

_unit(
    "geometry", "Computational Geometry", "📐", _S8,
    "One integer expression — the cross product — and everything built on it.",
    weight=1,
    prereqs=["sorting", "stacks", "math-number-theory"],
    why="""
Geometry problems look like they need trigonometry, and they nearly never do.
Angles bring `atan2`, degrees, and comparisons of floating-point numbers that
should be equal and are not — and an epsilon whose correct value depends on the
input scale.

Almost every elementary geometry question is instead the **sign** or the
**magnitude** of one integer expression. Which way did I turn, is this point
left of that line, do these segments cross, what is this polygon's area, which
points are on the hull: all the same two multiplications and a subtraction.

Learn it once, with its sign convention and its overflow, and the rest is
bookkeeping.
""",
    model="""
### The cross product

For points A, B, C:

```java
static long cross(long ax, long ay, long bx, long by, long cx, long cy) {
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
}
```

It is the z-component of the 3-D cross product of AB and AC, laid flat.

- **Sign** — orientation. Positive means C is to the **left** of AB: the turn
  A→B→C is counter-clockwise. Negative is a right turn, zero is collinear.
- **Magnitude** — twice the area of triangle ABC.

Say which convention you are using. With y upwards, positive is
counter-clockwise; on a screen, where y grows downwards, the same number means
clockwise.

### Stay in integers

With coordinates up to 10⁶ the differences reach 2·10⁶ and the product 4·10¹², so
**cast to `long` before multiplying**. `(bx - ax) * (cy - ay)` with `int`
operands overflows before the assignment and the sign that comes out is
arbitrary. This is the most common geometry bug and it never shows up on small
tests.

And avoid doubles wherever you can: a cross product of exactly 0 means
collinear, but in floating point it means "about 10⁻¹³".

### Area: the shoelace formula

The cross product, summed around a loop:

```java
long twiceArea = 0;
for (int i = 0; i < n; i++) {
    int j = (i + 1) % n;
    twiceArea += (long) p[i][0] * p[j][1] - (long) p[j][0] * p[i][1];
}
```

Each term is twice the signed area of the triangle (origin, corner i, corner
i+1). Signed areas telescope, so whatever a triangle covers outside the polygon
is covered again with the opposite sign — which is why this works for
non-convex polygons and why the origin's position does not matter.

The result is **positive for counter-clockwise** input and negative for
clockwise, so the raw sum also reports the polygon's orientation. Problems ask
for `2A` because the true area may be a half-integer.

### Segment intersection, without solving for the point

The intersection *point* needs division and floating point. Whether an
intersection *exists* needs four integer signs:

```java
int o1 = sign(cross(a, b, c)), o2 = sign(cross(a, b, d));
int o3 = sign(cross(c, d, a)), o4 = sign(cross(c, d, b));
if (o1 != o2 && o3 != o4) return true;          // they cross in their interiors
```

Both conditions are needed: either alone allows one segment to miss the other's
span entirely.

That test misses every case with a zero — a shared endpoint, a T-junction, an
endpoint lying on the other segment, two collinear overlapping segments. Those
need a bounding-box check, valid **only because collinearity is already known**:

```java
if (o1 == 0 && onSegment(a, b, c)) return true;    // and the other three
```

On its own the box test is wrong: (1,1) is inside the bounding box of
(0,0)–(2,0) and nowhere near the segment. The zero cross product supplies the
missing half of the claim.

### Convex hull: Andrew's monotone chain

Sort the distinct points by x, then y. Sweep left to right building the lower
boundary with a stack, popping whenever the last two entries and the new point
do not turn left; then sweep right to left for the upper boundary.

```java
for (int[] q : pts) {
    while (k >= 2 && cross(hull[k-2], hull[k-1], q) <= 0) k--;
    hull[k++] = q;
}
```

Same discipline as a monotonic stack: discard candidates a later candidate has
made irrelevant, with "turns the wrong way" as the domination test.

**`<= 0` or `< 0`** is the whole difference between "corners only" and "every
point on the boundary". `<=` pops a collinear middle point and gives the minimal
hull. The statement decides which is wanted, and getting it backwards is how
this fails on a test with three points in a line.

Each chain's last point is the other chain's first, so drop both before
concatenating. Handle one point, two points and all-collinear before the chains.
""",
    signals=[
        _sig("“left or right”, “clockwise”, “which way does it turn”",
             "The sign of the cross product",
             "Exact, and no trigonometry."),
        _sig("“area of a polygon”, convex or not", "Shoelace formula",
             "Signed triangles from the origin, telescoping."),
        _sig("“do these segments intersect”", "Four orientation signs, plus collinear cases",
             "Never solve for the point."),
        _sig("“smallest convex shape containing all points”", "Monotone chain",
             "Sort, then two stack sweeps."),
        _sig("“is this point inside the polygon”", "Ray casting, or cross products for a convex one",
             "Convex: the point must be on the same side of every edge."),
        _sig("Coordinates are integers", "Keep everything in `long`",
             "Exact comparison beats any epsilon."),
        _sig("Distances are compared, not printed", "Compare squared distances",
             "No square root, so no floating point at all."),
    ],
    skeletons=[
        _sk("The primitive",
            "Everything in this unit.",
            """
static long cross(long ax, long ay, long bx, long by, long cx, long cy) {
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
}
static int sign(long v) { return v > 0 ? 1 : v < 0 ? -1 : 0; }
""",
            "Take `long` parameters so the subtraction and the product are both 64-bit — "
            "casting the result is too late."),
        _sk("Segment intersection",
            "Crossing, touching, and overlapping.",
            """
static boolean onSegment(int[] a, int[] b, int[] c) {   // assumes c is collinear with ab
    return Math.min(a[0], b[0]) <= c[0] && c[0] <= Math.max(a[0], b[0])
        && Math.min(a[1], b[1]) <= c[1] && c[1] <= Math.max(a[1], b[1]);
}

static boolean intersect(int[] a, int[] b, int[] c, int[] d) {
    int o1 = sign(cross(a, b, c)), o2 = sign(cross(a, b, d));
    int o3 = sign(cross(c, d, a)), o4 = sign(cross(c, d, b));
    if (o1 != o2 && o3 != o4) return true;
    if (o1 == 0 && onSegment(a, b, c)) return true;
    if (o2 == 0 && onSegment(a, b, d)) return true;
    if (o3 == 0 && onSegment(c, d, a)) return true;
    if (o4 == 0 && onSegment(c, d, b)) return true;
    return false;
}
""",
            "The four collinear branches are not edge cases to skip — they are half the "
            "problem, and a degenerate point-segment is handled entirely by them."),
        _sk("Convex hull (monotone chain)",
            "The minimal enclosing convex polygon, counter-clockwise.",
            """
sortByXThenY(pts);                               // distinct points
int k = 0;
long[][] hull = new long[2 * pts.length][];
for (long[] q : pts) {                           // lower chain
    while (k >= 2 && cross(hull[k-2], hull[k-1], q) <= 0) k--;
    hull[k++] = q;
}
int lower = k + 1;
for (int i = pts.length - 2; i >= 0; i--) {      // upper chain
    long[] q = pts[i];
    while (k >= lower && cross(hull[k-2], hull[k-1], q) <= 0) k--;
    hull[k++] = q;
}
// hull[0 .. k-2] is the hull; hull[k-1] repeats hull[0]
""",
            "`<= 0` excludes collinear points. Use `< 0` when the statement wants every boundary "
            "point."),
    ],
    traces=[
        _trace(
            "The lower hull of (0,0), (1,3), (2,1), (3,4), (4,0)",
            "Points sorted by x. A point is pushed, then the stack is popped while the last "
            "turn is not a left turn — the middle point is then inside or on the boundary.",
            ["new point", "stack before", "cross of last two with it", "popped", "stack after"],
            [
                ["(0,0)", "[]", "—", "—", "[(0,0)]"],
                ["(1,3)", "[(0,0)]", "— (fewer than two)", "—", "[(0,0), (1,3)]"],
                ["(2,1)", "[(0,0), (1,3)]", "cross = −5 ≤ 0", "**(1,3)**", "[(0,0), (2,1)]"],
                ["(3,4)", "[(0,0), (2,1)]", "cross = +6 > 0", "none", "[(0,0), (2,1), (3,4)]"],
                ["(4,0)", "[(0,0), (2,1), (3,4)]", "cross = −11 ≤ 0", "**(3,4)**", "[(0,0), (2,1)]"],
                ["(4,0) again", "[(0,0), (2,1)]", "cross = −4 ≤ 0", "**(2,1)**", "[(0,0), (4,0)]"],
            ],
            "(1,3) and (3,4) are above the lower boundary and are popped; (2,1) survives one "
            "round and then goes too, because (0,0)→(2,1)→(4,0) is a right turn. The "
            "lower hull is (0,0)–(4,0) — a straight line, since no point dips below it. "
            "Five pushes and three pops: each point enters and leaves at most once, which is why "
            "the sweep is O(n) after the sort.",
        ),
    ],
    costs=[
        _cost("Cross product / orientation", "O(1)", "O(1)", "Two multiplications, one subtraction."),
        _cost("Shoelace area", "O(n)", "O(1)", "One pass around the boundary."),
        _cost("Segment intersection test", "O(1)", "O(1)", "Four orientations plus box checks."),
        _cost("All intersecting pairs, naively", "O(n²)", "O(1)", "Fine to a few thousand segments."),
        _cost("All intersecting pairs, sweep line", "O((n + k) log n)", "O(n)", "k = intersections found."),
        _cost("Convex hull (monotone chain)", "O(n log n)", "O(n)", "Sort, then two linear sweeps."),
    ],
    pitfalls=[
        _pit("Orientation is wrong on large coordinates only",
             "`(bx - ax) * (cy - ay)` with `int` operands overflows before the result is widened.",
             "Cast to `long` **before** multiplying, or take `long` parameters. This is the "
             "single most common bug here and small tests never catch it."),
        _pit("Collinear points are sometimes detected and sometimes not",
             "The cross product was computed in `double`, so exact zero became 10⁻¹³.",
             "Integer input means integer arithmetic. Reach for an epsilon only when the input "
             "itself is floating point."),
        _pit("Two segments that obviously touch are reported as not intersecting",
             "Only the strict four-sign test was written, so every collinear case is missed.",
             "Add the four `o == 0 && onSegment(...)` branches. Shared endpoints and T-junctions "
             "are the common inputs, not the rare ones."),
        _pit("A bounding-box test says two far-apart segments touch",
             "The box check was used without first establishing collinearity.",
             "It is only valid under `o == 0`. Alone it tests the boxes, not the segments."),
        _pit("The convex hull includes points in the middle of an edge",
             "The pop condition is `< 0` when the statement asks for corners only.",
             "`<= 0` pops collinear points. Decide which the statement wants before writing the "
             "comparison."),
        _pit("The hull is missing points, or repeats one",
             "Each chain's endpoints are shared, or a degenerate input went through the chains.",
             "Drop each chain's last point before concatenating, and handle one point, two "
             "points and all-collinear separately."),
        _pit("The polygon area comes out negative",
             "The corners were listed clockwise — which is information, not an error.",
             "Take the absolute value at the end, and remember the sign told you the "
             "orientation."),
    ],
    lessons=["sorting", "stack", "arithmetic"],
    checks=[
        _chk("What do the sign and the magnitude of `cross(A, B, C)` mean?",
             "The sign is the orientation of A→B→C: positive is a left turn "
             "(counter-clockwise, with y upwards), negative a right turn, zero collinear. The "
             "magnitude is twice the area of triangle ABC."),
        _chk("Why compute a cross product in `long` when the coordinates fit in an `int`?",
             "The differences reach 2·10⁶ and their product 4·10¹², past "
             "`int`. `int * int` overflows *before* any widening, so the sign that comes out is "
             "arbitrary — and only on large inputs."),
        _chk("Why does the shoelace formula work for a non-convex polygon?",
             "Each term is the *signed* area of a triangle from the origin to one edge. Regions "
             "outside the polygon are swept once in each direction by different edges and cancel, "
             "leaving exactly the enclosed area — no convexity is assumed anywhere."),
        _chk("Why not just solve for the intersection point of two segments?",
             "It needs division, a special case for parallel segments, and floating-point "
             "comparison to decide whether the point lies within both. Four integer orientation "
             "signs answer the yes/no question exactly and with none of that."),
        _chk("Why is a bounding-box check valid for a collinear point and wrong in general?",
             "Collinearity already fixes the point to the segment's line; the box then only has "
             "to bound it along that line. Without collinearity the box says nothing — "
             "(1,1) is inside the box of (0,0)–(2,0) and not on it."),
        _chk("In a convex hull sweep, what is the difference between popping on `<= 0` and `< 0`?",
             "`<= 0` also pops points that are exactly collinear, giving only the corners. `< 0` "
             "keeps them, giving every point on the boundary. The statement decides, and it is "
             "the usual source of a wrong answer on a collinear test."),
    ],
    bigo=[
        _bigo(r"""
for (int i = 0; i < n; i++) {                   // shoelace
    int j = (i + 1) % n;
    s += (long) p[i][0] * p[j][1] - (long) p[j][0] * p[i][1];
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "One pass and two multiplications per edge. It is worth noting that this is O(n) "
            "for *any* simple polygon — triangulating a non-convex one first, which is the "
            "instinct, is both harder and slower."),
        _bigo(r"""
sortByXThenY(pts);                              // monotone chain
for (long[] q : pts) {
    while (k >= 2 && cross(hull[k-2], hull[k-1], q) <= 0) k--;
    hull[k++] = q;
}
""", "O(n log n)", ["O(n log n)", "O(n)", "O(n²)", "O(n log² n)"],
            "The sort dominates. The sweep itself is O(n): each point is pushed once, so it can "
            "be popped at most once, and the inner `while` is O(1) amortized — the same "
            "argument as a monotonic stack."),
        _bigo(r"""
for (int i = 0; i < k; i++)                     // every pair of k segments
    for (int j = i + 1; j < k; j++)
        if (intersect(s[i], s[j])) count++;
""", "O(k²)", ["O(k²)", "O(k log k)", "O(k)", "O(k² log k)"],
            "Each test is O(1), so the pairs are the whole cost — fine to a few thousand "
            "segments. Bentley–Ottmann's sweep line reports the k intersections in "
            "O((n + k) log n), which only wins when the intersections are few."),
        _bigo(r"""
double best = 1e18;                              // closest pair, brute force
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        best = Math.min(best, dist2(p[i], p[j]));
""", "O(n²)", ["O(n²)", "O(n log n)", "O(n log² n)", "O(n)"],
            "Every pair. The divide-and-conquer closest-pair algorithm is O(n log n), and note "
            "that `dist2` compares *squared* distances — comparing squares avoids the "
            "square root and stays exact on integer input."),
        _bigo(r"""
boolean insideConvex(int[][] poly, int[] q) {   // n-gon, given counter-clockwise
    for (int i = 0; i < n; i++)
        if (cross(poly[i], poly[(i+1) % n], q) < 0) return false;
    return true;
}
""", "O(n)", ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "One orientation test per edge. For a *convex* polygon this can be done in "
            "O(log n) by binary searching the fan of triangles from one vertex — which "
            "matters when many points are tested against one fixed polygon."),
    ],
    interview="""
Open by taking trigonometry off the table: *"I'll do this with cross products,
so it stays in integers and collinear is exact."* That one sentence pre-empts
the entire class of follow-up questions about precision.

Then be explicit about the sign convention and about the `long`. Interviewers
ask "what if the coordinates are up to 10⁹?" precisely to see whether you
noticed the overflow.
""",
    rungs=[
        _rung("Warm up", "The primitive, and nothing else.",
              ["turn-directions"],
              {"turn-directions": "Compute one cross product per interior point and read the sign. Write out the sign convention on paper first — half the failures here are a flipped L and R."}),
        _rung("Core", "The same expression summed, and the same expression compared.",
              ["polygon-area-doubled", "count-crossing-segments"],
              {"polygon-area-doubled": "Shoelace. Try it on a non-convex polygon and on one listed clockwise, and watch the sign carry the orientation.",
               "count-crossing-segments": "Write the strict four-sign test first, watch it miss a shared endpoint, then add the collinear branches. Doing it in that order is what makes them memorable."}),
        _rung("Stretch", "Sort, then sweep with a stack.",
              ["convex-hull-points"],
              {"convex-hull-points": "Andrew's monotone chain. Get the two degenerate inputs right before the general case: all points equal, and all points collinear."}),
    ],
    next_up="""
Exact integer geometry. The last unit goes the other way — algorithms that are
deliberately *not* deterministic, and how to reason about them anyway.
""",
)


# --- Unit 46 — Randomized algorithms -----------------------------------------

_unit(
    "randomized", "Randomized Algorithms", "🎲", _S8,
    "Expected versus worst case, Las Vegas versus Monte Carlo, and how to sample.",
    weight=1,
    prereqs=["sorting", "binary-search", "math-number-theory"],
    why="""
Randomness has turned up three times already without ever being the subject.
Quickselect picks a **random** pivot, and the `sorting` unit says why. Hashing
assumes keys spread out. `string-matching` accepts a rolling hash whose equal
values might be a collision.

Each of those is a different bargain, and the words for them are worth having:

- **Expected time.** Quickselect is O(n) on average and O(n²) on a pivot
  sequence an adversary chose — but randomising the pivot means the adversary
  chooses the *input*, not the *coins*.
- **Amortized time** is a different guarantee entirely: it holds on every input,
  because it is arithmetic over a sequence rather than a claim about a
  distribution. Mixing these two up is the most common error in this area.
- **Las Vegas** algorithms are always right and randomly slow. **Monte Carlo**
  algorithms are always fast and occasionally wrong.

Plus a practical skill the core course never covers: sampling. Drawing from a
weighted distribution, shuffling correctly, and sampling a stream whose length
you do not know.
""",
    model="""
### Expected, worst, amortized, average

| Claim | Means | Defeated by |
| --- | --- | --- |
| Worst case O(f) | every input, every run | nothing |
| **Amortized** O(f) | n operations cost O(n·f) *total*, on every input | nothing |
| **Expected** O(f) | average over the algorithm's own coin flips, on every input | nothing — you own the coins |
| **Average case** O(f) | average over a distribution of inputs | an adversary who picks the input |

Expected and average sound alike and are not. Quicksort with a **fixed** pivot
is average O(n log n) and an adversary can feed it the killer input every time.
Quicksort with a **random** pivot is expected O(n log n) on *every* input,
including that one — the randomness moved out of the input and into the
algorithm, where the adversary cannot reach it.

### Las Vegas versus Monte Carlo

- **Las Vegas** — output always correct, running time random. Randomised
  quickselect, the shuffle below, Rabin's closest-pair. Safe to ship without a
  fallback; the only risk is latency.
- **Monte Carlo** — running time bounded, output occasionally wrong.
  Miller–Rabin with random bases, a rolling hash trusted without verification,
  Karger's min cut. Needs an error budget, and usually a verification pass.

You can often convert: run a Monte Carlo algorithm until a *check* passes and
you have a Las Vegas one — which is exactly what "verify the characters when the
hashes match" does to Rabin–Karp.

### Fisher–Yates

```java
for (int i = n - 1; i >= 1; i--) {
    int j = rng.nextInt(i + 1);        // 0 <= j <= i, INCLUSIVE
    swap(a, i, j);
}
```

Uniform because position n−1 receives any of the n cards with probability 1/n,
then position n−2 any of the remaining n−1 with probability 1/(n−1), and so on:
every one of the n! orders has probability exactly 1/n!.

Drawing `j` from `0 … n-1` every time instead gives nⁿ equally likely execution
paths mapped onto n! outcomes. n! does not divide nⁿ for n > 2, so some orders
*must* be more likely — for n = 3 the counts are 4/27 and 5/27, a 25% bias that
eyeballing the output will never reveal.

### Sampling from a distribution

Prefix-sum the weights, draw a point uniformly on the total, and binary-search
which half-open interval `[prefix[i], prefix[i+1])` swallowed it. O(log n) per
draw after an O(n) build; Walker's alias method gets it to O(1).

### Reservoir sampling

k items from a stream of unknown length, in one pass and O(k) memory:

```java
for (int i = 0; i < n; i++) {
    if (i < k) slot[i] = a[i];
    else {
        int j = rng.nextInt(i + 1);
        if (j < k) slot[j] = a[i];
    }
}
```

One draw does both jobs: `j < k` happens with probability exactly k/(i+1) — the
acceptance test — and given acceptance, `j` is uniform on the slots — the
eviction choice.

Item i survives with probability

`k/(i+1) · (i+1)/(i+2) · … · (n-1)/n = k/n`

and the telescoping landing on k/n for *every* i is what uniform means.

### Miller–Rabin, and derandomising it

Write `n − 1 = d·2^r` with d odd. If n is prime, the only square roots of 1 are
±1, so the sequence `a^d, a^2d, a^4d …` must reach 1 *through* n−1. A base that
breaks that is a **certificate** that n is composite — not evidence, a proof.

With random bases it is Monte Carlo, wrong with probability under 4^−k. With the
fixed set `{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}` it is *exact* below
3.3·10²⁴: the randomness was replaced by somebody else's exhaustive search.

Plain Fermat is not enough — Carmichael numbers like 561 satisfy `a^(n−1) = 1`
for every coprime base, and there are infinitely many of them.

### Testing randomized code

Inject the generator. The algorithm consumes uniform integers and does not care
where they come from, so a fixed seed makes every run reproducible without
changing a line of the logic. That separation is why the problems in this unit
can be judged at all, and it is also how you would write these tests at work.
""",
    signals=[
        _sig("“pick one at random, weighted”", "Prefix sums + binary search",
             "Or the alias method for O(1) draws."),
        _sig("“shuffle”, “random permutation”", "Fisher–Yates, inclusive range",
             "Sorting by a random key is O(n log n) for the same result."),
        _sig("“unknown length”, “stream”, “bounded memory”", "Reservoir sampling",
             "One pass, O(k) memory, provably uniform."),
        _sig("Primality beyond 10⁹", "Miller–Rabin with fixed bases",
             "Trial division to √n is 10⁹ steps at 10¹⁸."),
        _sig("A worst case an adversary could construct", "Randomise the choice, not the input",
             "Random pivot, randomised hash seed."),
        _sig("“with high probability” in a statement", "A Monte Carlo answer is acceptable",
             "Say the error probability out loud."),
        _sig("Hash equality used as a final answer", "Verify, or use two moduli",
             "That verification is what makes it Las Vegas."),
    ],
    skeletons=[
        _sk("Fisher–Yates",
            "A uniformly random permutation, in place.",
            """
for (int i = n - 1; i >= 1; i--) {
    int j = rng.nextInt(i + 1);                  // inclusive of i: j may equal i
    int t = a[i]; a[i] = a[j]; a[j] = t;
}
""",
            "Drawing from `0 … n-1` instead of `0 … i` is the classic biased version, and the "
            "bias is invisible without a statistical test."),
        _sk("Weighted sampling",
            "Draw index i with probability w[i] / Σw.",
            """
long[] prefix = new long[n + 1];
for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + w[i];

int draw() {
    long r = nextUniform(prefix[n]);             // 0 <= r < total
    int lo = 0, hi = n - 1;                      // first i with prefix[i+1] > r
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (prefix[mid + 1] > r) hi = mid; else lo = mid + 1;
    }
    return lo;
}
""",
            "Half-open intervals `[prefix[i], prefix[i+1])`, and the predicate is strictly "
            "greater — `>=` shifts the answer at every boundary."),
        _sk("Reservoir sampling",
            "k uniform samples from a stream of unknown length.",
            """
for (int i = 0; i < n; i++) {
    if (i < k) { slot[i] = a[i]; continue; }     // fill first; not a special case to fold in
    int j = rng.nextInt(i + 1);
    if (j < k) slot[j] = a[i];                   // j is both the coin and the victim
}
""",
            "The same draw supplies the acceptance probability k/(i+1) and the uniform eviction "
            "choice."),
        _sk("Miller–Rabin with fixed bases",
            "Exact primality to 3.3·10²⁴.",
            """
static final long[] BASES = {2,3,5,7,11,13,17,19,23,29,31,37};

static boolean isPrime(long n) {
    if (n < 2) return false;
    for (long p : BASES) if (n % p == 0) return n == p;
    long d = n - 1; int r = 0;
    while ((d & 1) == 0) { d >>= 1; r++; }
    for (long a : BASES) {
        long x = powMod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        boolean witness = true;
        for (int i = 1; i < r; i++) {
            x = mulMod(x, x, n);
            if (x == n - 1) { witness = false; break; }
        }
        if (witness) return false;
    }
    return true;
}
""",
            "`mulMod` must not be `a * b % n` — that overflows 64 bits past about "
            "3·10⁹ and fails silently."),
    ],
    traces=[
        _trace(
            "Why the naive shuffle is biased, on three cards",
            "Both versions draw two random numbers. Fisher–Yates draws j from 0…i "
            "(3 × 2 = 6 paths); the naive one draws j from 0…2 every time "
            "(3 × 3 = 9 paths). Counting how many paths reach each of the 3! = 6 orders:",
            ["order of ABC", "Fisher–Yates paths (of 6)", "probability", "naive paths (of 27)", "probability"],
            [
                ["ABC", "1", "1/6", "4", "**4/27**"],
                ["ACB", "1", "1/6", "5", "**5/27**"],
                ["BAC", "1", "1/6", "5", "**5/27**"],
                ["BCA", "1", "1/6", "5", "**5/27**"],
                ["CAB", "1", "1/6", "4", "**4/27**"],
                ["CBA", "1", "1/6", "4", "**4/27**"],
            ],
            "1/6 ≈ 0.167 against 4/27 ≈ 0.148 and 5/27 ≈ 0.185 — a 25% spread. "
            "The reason is arithmetic, not implementation: the naive version has 3³ = 27 "
            "equally likely execution paths to distribute over 6 outcomes, and 6 does not divide "
            "27. Any shuffle whose number of paths is not a multiple of n! is biased, and no "
            "amount of looking at the output will show it.",
        ),
        _trace(
            "Reservoir sampling, k = 2, over a stream of five",
            "Slots are filled by the first two items; each later item i is accepted with "
            "probability 2/(i+1). The last column is the probability item i is in the final "
            "reservoir, which must end at 2/5 for every item.",
            ["i", "item", "draw j from", "accepted if", "P(accept)", "P(in final sample)"],
            [
                ["0", "A", "—", "always (fills slot 0)", "1", "2/5"],
                ["1", "B", "—", "always (fills slot 1)", "1", "2/5"],
                ["2", "C", "0…2", "j < 2", "2/3", "2/5"],
                ["3", "D", "0…3", "j < 2", "2/4", "2/5"],
                ["4", "E", "0…4", "j < 2", "2/5", "2/5"],
            ],
            "Item C enters with probability 2/3, then survives step 3 with probability 3/4 and "
            "step 4 with probability 4/5: 2/3 · 3/4 · 4/5 = 2/5. The denominators "
            "cancel against the next numerator — the telescoping is the proof, and it "
            "lands on k/n for every item, which is what uniform means.",
        ),
    ],
    costs=[
        _cost("Fisher–Yates", "O(n)", "O(1)", "One draw and one swap per element."),
        _cost("Weighted draw", "O(log n)", "O(n)", "O(1) with the alias method."),
        _cost("Reservoir sampling", "O(n)", "O(k)", "One pass; length not needed in advance."),
        _cost("Quickselect, random pivot", "O(n) expected", "O(1)", "O(n²) worst case, on the coins not the input."),
        _cost("Miller–Rabin", "O(k log³ n)", "O(1)", "12 bases, ~60 squarings each."),
        _cost("Trial division to √n", "O(√n)", "O(1)", "10⁹ steps at n = 10¹⁸."),
    ],
    pitfalls=[
        _pit("A shuffle looks fine and is measurably biased",
             "`j` was drawn from the whole array each iteration instead of `0 … i`.",
             "The range must shrink. nⁿ execution paths cannot divide evenly among n! "
             "outcomes."),
        _pit("Calling an amortized bound “expected”, or the reverse",
             "They are different guarantees.",
             "Amortized is arithmetic over a sequence and holds on every input; expected is an "
             "average over the algorithm's coin flips. `ArrayList.add` is amortized O(1); "
             "quickselect is expected O(n)."),
        _pit("A randomized algorithm is slow on one particular input, every time",
             "The “random” choice is derived from the input — a fixed pivot "
             "position, or a hash seed baked into the binary.",
             "Draw from a real generator. The whole point is that the adversary picks the "
             "input and you pick the coins."),
        _pit("Sampling is skewed towards the first or last element",
             "Half-open intervals were mixed with closed ones, or the binary search used `>=` "
             "where `>` was meant.",
             "`[prefix[i], prefix[i+1])`, first index with `prefix[i+1] > r`."),
        _pit("Miller–Rabin gives wrong answers above about 3·10⁹",
             "`a * b % n` overflowed 64 bits, silently.",
             "128-bit multiplication, `Math.multiplyHigh`, `BigInteger`, or Python integers."),
        _pit("A composite passes a Fermat test on every base tried",
             "It is a Carmichael number — 561, 1105, 1729 — and Fermat cannot see them.",
             "Use the Miller–Rabin square-root condition, which they do not satisfy."),
        _pit("The randomized tests are flaky in CI",
             "The generator is seeded from the clock.",
             "Inject the generator and fix the seed in tests. The algorithm is unchanged; only "
             "the coin flips become reproducible."),
    ],
    lessons=["sorting", "binary_search", "modulo", "number_theory"],
    checks=[
        _chk("What is the difference between expected time and average-case time?",
             "Expected time averages over the algorithm's own coin flips and therefore holds on "
             "*every* input; average case averages over a distribution of inputs and can be "
             "defeated by an adversary who picks a bad one. Randomising the pivot is exactly the "
             "move from the second guarantee to the first."),
        _chk("And how is amortized different from both?",
             "Amortized is not probabilistic at all: it is total work over a sequence of "
             "operations divided by their number, and it holds on every input with no "
             "randomness involved. `ArrayList.add` is amortized O(1); quickselect is expected "
             "O(n)."),
        _chk("Las Vegas or Monte Carlo — which is which, and why does it matter?",
             "Las Vegas is always correct with random running time (randomised quickselect, "
             "Fisher–Yates). Monte Carlo is always fast with a small chance of being wrong "
             "(Miller–Rabin with random bases, an unverified rolling hash). It matters "
             "because one needs a latency budget and the other needs an error budget and usually "
             "a verification pass."),
        _chk("Why is drawing `j` from the whole array in a shuffle biased?",
             "It produces nⁿ equally likely execution paths for n! outcomes, and n! does not "
             "divide nⁿ for n > 2 — so some orders must be reachable by more paths. For "
             "n = 3 the probabilities come out 4/27 and 5/27 instead of 1/6."),
        _chk("In reservoir sampling, why does one random number do two jobs?",
             "`j = rng.nextInt(i + 1)` is uniform on 0…i. The event `j < k` has probability "
             "exactly k/(i+1), which is the acceptance test; and conditioned on that, j is "
             "uniform on the k slots, which is the eviction choice."),
        _chk("How does Miller–Rabin stop being probabilistic?",
             "By fixing the bases. With the twelve smallest primes as bases the test is known — "
             "by exhaustive verification — to be exact for every n below 3.3·10²⁴, "
             "so no randomness is left in it."),
        _chk("Why is a Fermat test not enough?",
             "Carmichael numbers satisfy a^(n−1) = 1 mod n for every base coprime to n, and "
             "there are infinitely many. Miller–Rabin adds the square-root condition, which "
             "they fail."),
    ],
    bigo=[
        _bigo(r"""
for (int i = n - 1; i >= 1; i--) {              // Fisher-Yates
    int j = rng.nextInt(i + 1);
    swap(a, i, j);
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
            "One draw and one swap per element, in place. Sorting by a random key gives the "
            "same distribution for O(n log n) and O(n) extra memory — correct, and strictly "
            "worse."),
        _bigo(r"""
static int kth(int[] a, int k) {                // randomised quickselect
    while (true) {
        int p = partition(a, randomPivot());    // O(size of the current range)
        if (p == k) return a[p];
        if (p < k) lo = p + 1; else hi = p - 1;
    }
}
""", "O(n) expected", ["O(n) expected", "O(n log n)", "O(n²) expected", "O(log n)"],
            "A random pivot discards a constant fraction on average, so the work is "
            "n + n/2 + n/4 + … = O(n). The worst case is still O(n²) — but it now "
            "depends on the coin flips, which an adversary choosing the input cannot control."),
        _bigo(r"""
for (int t = 0; t < T; t++) {                   // T weighted draws over n options
    long r = nextUniform(total);
    out[t] = binarySearchPrefix(prefix, r);
}
""", "O(n + T log n)", ["O(n + T log n)", "O(T·n)", "O(n log n)", "O(T)"],
            "One prefix-sum pass, then a binary search per draw. Walker's alias method makes "
            "each draw O(1) after an O(n) build, which is what a simulation drawing millions of "
            "samples wants."),
        _bigo(r"""
for (long a : BASES)                             // Miller-Rabin, 12 fixed bases
    if (isWitness(a, n)) return false;           // one modular exponentiation each
""", "O(log³ n)", ["O(log³ n)", "O(√n)", "O(log n)", "O(n)"],
            "Twelve exponentiations of about log n squarings each, and a 128-bit modular "
            "multiply is O(log² n) in the bit length — microseconds at n = "
            "10¹⁸. Trial division to √n is 10⁹ steps for the same answer."),
        _bigo(r"""
List<String> all = new ArrayList<>();            // sample k lines of a file
for (String line : file) all.add(line);
Collections.shuffle(all);
return all.subList(0, k);
""", "O(n) time, O(n) space", ["O(n) time, O(k) space", "O(n) time, O(n) space",
                              "O(n log n) time, O(n) space", "O(k) time, O(k) space"],
            "Correct, and it stores the whole file — impossible for a stream, and wasteful "
            "for a large one. Reservoir sampling gets the same distribution in one pass with "
            "O(k) memory and without knowing n in advance."),
    ],
    interview="""
Use the vocabulary precisely; it is most of what is being tested here. *"Expected
O(n), because the pivot is random — the worst case is still O(n²) but an
adversary would have to guess my coin flips"* is a complete, senior-sounding
answer to "how fast is quickselect?".

When you use a hash to compare things, volunteer the collision caveat and what
you would do about it. Saying "and I'd verify the characters on a match, which
makes it Las Vegas rather than Monte Carlo" unprompted is the strongest version
of that answer.
""",
    rungs=[
        _rung("Warm up", "Drawing from a distribution that is not uniform.",
              ["weighted-random-picks"],
              {"weighted-random-picks": "Prefix sums and a binary search. Check the boundaries: `>` not `>=`, and half-open intervals."}),
        _rung("Core", "The two sampling algorithms worth knowing by heart.",
              ["shuffle-fisher-yates", "reservoir-sample-stream"],
              {"shuffle-fisher-yates": "Write the biased version too, run both 100000 times on three elements, and count the orders. Seeing 4/27 against 1/6 is worth more than the proof.",
               "reservoir-sample-stream": "One draw does the accepting and the evicting. Derive the telescoping product for k = 1 before you code it."}),
        _rung("Stretch", "Monte Carlo, and how it stops being Monte Carlo.",
              ["miller-rabin-primality"],
              {"miller-rabin-primality": "Try a plain Fermat test on 561 first and watch it pass. Then add the square-root condition. Do not use `a * b % n`."}),
    ],
    next_up="""
That is everything beyond the core, and the end of the curriculum: eight stages,
forty-six units. From here the work is revision — the stage-end mixed sets, and
the stretch rungs re-solved from memory, without the unit page open.
""",
)
