# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 — Things that branch.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# Everything so far has been linear. This stage covers the structures where an
# element has SEVERAL successors. The idea that makes them tractable, recursion,
# is taught in stage 3 — it moved there because merge sort and quickselect need
# it — so this stage opens straight on trees.
#
# Order within the stage is a dependency chain, not a difficulty ramp: trees
# are recursion with two successors; backtracking is recursion that undoes;
# graphs are trees with cycles, which is precisely why they need a visited set;
# and the graph units after that are the questions worth asking about a graph —
# can I reach it, in what order, is it connected, what is the cheapest way to
# connect it, how far is it.
# ---------------------------------------------------------------------------

_S6 = _stage(
    "hierarchies", "Trees & Graphs", "🌳",
    "One idea — solve a smaller version — applied to everything that branches.",
    """
This is the conceptual centre of the curriculum, and it runs on the recursion
from stage 3. Every unit in it is the same sentence with a different noun:

> Solve the smaller version, then combine.

For a **tree** the smaller versions are the two subtrees. For **backtracking**
they are "the same problem with one more choice fixed". For a **graph** they are
the neighbours — plus a visited set, because a graph can loop back on itself and
a tree cannot.

If you find yourself memorising four traversals, stop: it is one traversal,
called on whatever the successors happen to be.
""")


# --- Unit 23 — Binary trees --------------------------------------------------

_unit(
    "trees", "Binary Trees", "🌲", _S6,
    "Two recursive calls and a decision about where to do the work.",
    weight=3,
    prereqs=["recursion"],
    why="""
A binary tree is the friendliest recursive structure there is: no cycles, at
most two children, and a natural base case at `null`. That is why it dominates
interview question banks — it tests recursion without any of the bookkeeping a
graph demands.

Almost every tree problem is one of two shapes. Either you ask each subtree for
a value and combine the answers (**bottom-up**), or you carry information down
from the root as you descend (**top-down**). Being able to say which one a
problem needs, before writing anything, is the skill this unit builds.
""",
    model="""
### The shape

```java
class TreeNode { int val; TreeNode left, right; }
```

`null` is the empty tree and the base case of essentially every function here.

### Bottom-up: ask the children

```java
static int height(TreeNode n) {
    if (n == null) return 0;
    return 1 + Math.max(height(n.left), height(n.right));
}
```

The recursion returns a value that the parent combines. Height, node count,
balance, diameter and maximum path sum are all this shape — and the harder ones
share a trick: **return one thing and record another**. Diameter needs the
height from each call, but the answer is the best path *seen anywhere*, so the
function returns height and updates a field for the answer.

### Top-down: carry context down

```java
static boolean hasPath(TreeNode n, int remaining) {
    if (n == null) return false;
    remaining -= n.val;
    if (n.left == null && n.right == null) return remaining == 0;
    return hasPath(n.left, remaining) || hasPath(n.right, remaining);
}
```

Here the parameter carries what the parent knew. Path sums, depth tracking and
BST range validation are all top-down.

A leaf is `left == null && right == null` — **not** `n == null`. Conflating
them is the reason min-depth is the most-failed easy tree problem: a node with
one child is not a leaf, and returning `min(0, depth(other))` gives 0.

### The three depth-first orders

```java
visit(n); go(left); go(right);      // pre-order  — root first  (copy, serialise)
go(left); visit(n); go(right);      // in-order   — sorted, for a BST
go(left); go(right); visit(n);      // post-order — children first (delete, aggregate)
```

Same traversal, three positions for the work. Choose by asking *when* the node's
value is needed relative to its children's.

### Breadth-first: level order

Everything phrased in terms of **levels** — level order, right-side view,
zigzag, minimum depth on a wide tree — is a queue, not recursion:

```java
Queue<TreeNode> q = new ArrayDeque<>();
q.add(root);
while (!q.isEmpty()) {
    int size = q.size();               // freeze this level's width
    for (int i = 0; i < size; i++) {
        TreeNode n = q.poll();
        if (n.left != null) q.add(n.left);
        if (n.right != null) q.add(n.right);
    }
}
```

Capturing `q.size()` before the inner loop is what separates one level from the
next. Without it you cannot tell where a level ends.

### Building and serialising

A traversal of *values* loses the shape: preorder `1 2` could be 2-as-left or
2-as-right. Two ways to keep it:

- **Write the nulls.** A preorder walk that writes `#` for every missing child is
  unambiguous, because every subtree then says where it ends. Reading it back is
  the same walk, consuming one token per call:

  ```java
  TreeNode read(String[] t) {          // pos is a shared index
      String tok = t[pos++];
      if (tok.equals("#")) return null;
      TreeNode n = new TreeNode(Integer.parseInt(tok));
      n.left = read(t);                  // consumes exactly the left subtree
      n.right = read(t);
      return n;
  }
  ```

- **Use two traversals.** With distinct values, preorder names the root and
  inorder splits everything else around it. A value → inorder-index map makes
  each split O(1), so the rebuild is O(n).

Both are recursion that *builds* rather than inspects — and both depend on the
left subtree being handled completely before the right one starts.
""",
    signals=[
        _sig("“depth”, “count”, “sum of the subtree”", "Bottom-up recursion",
             "Each node's answer is built from its children's."),
        _sig("“path from the root”, “running total”", "Top-down with a parameter",
             "Context flows downward."),
        _sig("“level by level”, “each row”, “right side view”", "BFS with a queue",
             "Freeze `q.size()` to delimit the level."),
        _sig("“sorted order” from a BST", "In-order traversal",
             "In-order on a BST is ascending by definition."),
        _sig("“diameter”, “longest path”, “max path sum”", "Return one value, record another",
             "The answer is global; the return value is local."),
        _sig("“are these two trees the same / mirrored?”", "Recurse on two nodes at once",
             "The function takes a pair and compares structurally."),
    ],
    skeletons=[
        _sk("Bottom-up aggregate",
            "Height, count, sum, balance.",
            """
static int height(TreeNode n) {
    if (n == null) return 0;
    return 1 + Math.max(height(n.left), height(n.right));
}
""",
            "`null` → 0 is the identity that makes the `1 +` correct at a leaf."),
        _sk("Return one value, record another",
            "Diameter, maximum path sum — any “best anywhere” question.",
            """
int best = 0;

int gain(TreeNode n) {                  // returns: best downward path from n
    if (n == null) return 0;
    int l = Math.max(0, gain(n.left));  // negative contributions are dropped
    int r = Math.max(0, gain(n.right));
    best = Math.max(best, l + r + n.val);   // the answer may bend through n
    return n.val + Math.max(l, r);          // but only one side can be returned
}
""",
            "The distinction between what is returned and what is recorded is the whole idea."),
        _sk("Level-order BFS",
            "Level lists, right-side view, zigzag, level sums.",
            """
Queue<TreeNode> q = new ArrayDeque<>();
if (root != null) q.add(root);
while (!q.isEmpty()) {
    int size = q.size();
    for (int i = 0; i < size; i++) {
        TreeNode n = q.poll();
        if (i == size - 1) rightmost.add(n.val);     // right-side view
        if (n.left != null) q.add(n.left);
        if (n.right != null) q.add(n.right);
    }
}
""",
            "Snapshot `size` first — the queue grows while you drain it."),
        _sk("Compare two trees at once",
            "Same tree, symmetric tree, subtree checks.",
            """
static boolean same(TreeNode a, TreeNode b) {
    if (a == null || b == null) return a == b;      // both null ⇒ equal
    return a.val == b.val && same(a.left, b.left) && same(a.right, b.right);
}
""",
            "For symmetry, compare `a.left` with `b.right` instead."),
        _sk("Rebuild from preorder + inorder",
            "Construct a tree from two traversals (distinct values).",
            """
int preIdx = 0;
Map<Integer, Integer> pos = new HashMap<>();      // value -> inorder index

TreeNode build(int[] pre, int lo, int hi) {        // inorder range [lo, hi]
    if (lo > hi) return null;
    TreeNode root = new TreeNode(pre[preIdx++]);
    int m = pos.get(root.val);
    root.left = build(pre, lo, m - 1);            // LEFT first: preorder order
    root.right = build(pre, m + 1, hi);
    return root;
}
""",
            "Without the map, finding each root in the inorder makes it O(n²) on a skewed tree."),
    ],
    costs=[
        _cost("Any full traversal", "O(n)", "O(h)", "h = height; the recursion stack."),
        _cost("Balanced tree height", "h = O(log n)", "—", "Skewed trees degrade to O(n)."),
        _cost("BFS level order", "O(n)", "O(width)", "Up to n/2 nodes on the last level."),
        _cost("Recursive traversal on a skewed tree", "O(n)", "O(n) stack",
              "10⁵ nodes in a line will overflow the stack."),
    ],
    pitfalls=[
        _pit("Minimum depth returns 1 for a tree that is a single chain",
             "A node with one child was treated as a leaf.",
             "A leaf is `left == null && right == null`. With one child, recurse only into "
             "the side that exists."),
        _pit("`NullPointerException` in the recursive case",
             "The `null` base case is missing or comes after a field access.",
             "Test `n == null` as the first line of every tree function."),
        _pit("Diameter is computed as the height",
             "The function returned the answer instead of the value its parent needs.",
             "Return the downward height; record the through-node best in a field."),
        _pit("Level boundaries are lost in BFS",
             "`q.size()` was read inside the loop, after nodes had already been added.",
             "Snapshot the size before draining the level."),
        _pit("Maximum path sum is dragged down by a negative subtree",
             "A negative child contribution was included instead of being dropped.",
             "`Math.max(0, gain(child))` — an unhelpful branch contributes nothing."),
        _pit("`StackOverflowError` on a large tree",
             "The tree is effectively a linked list, so recursion is n deep.",
             "Convert to an explicit stack, or use BFS."),
    ],
    lessons=["tree_basics", "tree_traversal", "tree_dp"],
    checks=[
        _chk("How do you tell a leaf from a null child, and why does it matter?",
             "A leaf has both children null; a null node is the absence of a node. Minimum "
             "depth is wrong whenever the two are conflated, because a one-child node would "
             "report a depth of 0 through its missing side."),
        _chk("When is the work done in pre-, in-, and post-order?",
             "Pre: before the children (copying, serialising). In: between them (sorted "
             "order on a BST). Post: after both (deleting, aggregating from below)."),
        _chk("Why does level-order BFS snapshot `q.size()`?",
             "The loop adds the next level's nodes while draining the current one. The "
             "captured size is the only record of where this level ends."),
        _chk("In the max-path-sum skeleton, why do the returned value and the recorded "
             "value differ?",
             "A path through a node may use both children, but a path that continues to the "
             "parent may use only one. So the record considers `l + r + val` while the "
             "return is `val + max(l, r)`."),
        _chk("Why does a serialisation need a marker for every null child?",
             "Values alone do not fix the shape — `1 2` could put 2 on either side. With a "
             "marker for each null, every subtree's tokens end unambiguously, so one "
             "preorder walk can read the tree back."),
        _chk("When rebuilding from preorder and inorder, why must the left subtree be built first?",
             "The preorder lists root, then the entire left subtree, then the right. A shared "
             "preorder index only lines up if the recursion consumes them in that order."),
    ],
    interview="""
Trees are the most-asked structure in interviews, and the questions are
deliberately shallow — they want to see whether you can write a clean recursion
under mild pressure. Two habits score: stating the base case before the
recursive one, and saying the space complexity as O(h) rather than O(1),
because the stack is real. When the tree could be skewed, mention it.
""",
    internals="""
### A tree's cost is its *shape*, not its size

Every recursion in this unit visits each node once, so the **time** is O(n) no
matter what. What the shape decides is the **stack depth**, and that is the
number that bites:

```
balanced (n = 15)            skewed (n = 15)
      8                      1
   4     12                   2
 2  6  10  14                  3
1 3 5 7 9 11 13 15              4  …  15

height 4 = ⌊log₂ n⌋ + 1      height 15 = n
```

A recursive traversal uses one JVM stack frame per level. At height 15 nobody
notices; at height 10⁵ — a linked-list-shaped tree, which is what you get by
inserting sorted keys into an unbalanced BST — you get a
`StackOverflowError`, not a wrong answer and not a timeout. The default thread
stack holds roughly 10⁴–10⁵ frames depending on frame size, so this is a real
limit at competitive-programming sizes.

The fix when it matters is an explicit stack (`Deque<TreeNode>`), which moves
the frames onto the heap. Worth knowing you *can*; not worth doing by default,
because the recursive version is three lines and the iterative one is twelve.

### What balancing buys, and what it costs

A **self-balancing** tree does extra work on insert and delete to keep the
height at O(log n): AVL rotates aggressively and stays very balanced; red-black
rotates less and allows up to 2× the minimum height. Java's `TreeMap` and
`TreeSet` are red-black trees.

| | Unbalanced BST | Balanced BST (`TreeMap`) | `HashMap` |
|---|---|---|---|
| search / insert | O(h) — O(log n) typical, **O(n) worst** | O(log n) guaranteed | O(1) average |
| in-order = sorted | yes | yes | **no order at all** |
| first / last / floor / ceiling | O(h) | O(log n) | not supported |
| overhead | pointers only | pointers + a colour bit + rotations | bucket array |

The trade is stated in one line: a hash map is faster and forgets order; a
balanced tree is slower and remembers it. Choose on whether you will ever ask
*"what is the next key after this one?"*

### Why a binary tree at all

The branching factor is what makes the height logarithmic — `log₂ n` levels to
reach n nodes. Widening the node to hold many keys gives `log_B n` levels,
which barely helps in memory (log₂ 10⁶ = 20, log₁₀₀ 10⁶ = 3) but matters
enormously on disk, where each level is a seek. That is a B-tree, and it is why
every database index is one and no in-memory `Map` is.
""",
    rungs=[
        _rung("Warm up", "One value, computed from the children.",
              ["max-depth-tree", "count-nodes-tree", "invert-binary-tree"],
              {"max-depth-tree": "The template. Everything in this unit is a variation of these three lines."}),
        _rung("Core", "Two-node recursion, and context carried downwards.",
              ["same-tree", "min-depth-tree", "path-sum-exists", "inorder-traversal"],
              {"min-depth-tree": "The one-child case. This is the problem that catches everyone — decide what a leaf is first.",
               "inorder-traversal": "Learn this one properly: it is the walk that comes out sorted on a BST, which is the next unit's whole invariant."}),
        _rung("Variations", "Anything phrased in terms of levels.",
              ["level-order-traversal", "right-side-view", "zigzag-level-order"],
              {"level-order-traversal": "The BFS template. Snapshot the queue size.",
               "zigzag-level-order": "Do not reverse the queue — reverse the collected list on alternate levels."}),
        _rung("Stretch", "Return one thing, record another.",
              ["balanced-tree", "diameter-of-tree", "lca-binary-tree", "max-path-sum"],
              {"balanced-tree": "Return the height and use −1 as a “already unbalanced” signal, so it stays a single O(n) pass.",
               "lca-binary-tree": "Return the node found below; a node that hears back from both sides is the ancestor.",
               "max-path-sum": "The hardest of the shape, and the one worth being able to rebuild from scratch."}),
        _extra("Extra practice", "The same two recursions with one line moved — reps, not new ideas.",
               ["preorder-traversal", "symmetric-tree"],
               {"preorder-traversal": "Identical to the inorder walk with one line relocated. Worth writing once to see that the *order of the visit* is the only difference between the three traversals; not worth waiting on.",
                "symmetric-tree": "`same-tree` with the recursion crossed over: compare left against right. Genuinely the same problem."}),
    ],
    next_up="""
Add one invariant to a binary tree — left < node < right — and search becomes
O(log n).
""",
)


# --- Unit 24 — Binary search trees -------------------------------------------

_unit(
    "bst", "Binary Search Trees", "🔎", _S6,
    "One invariant, and every operation becomes a descent.",
    weight=2,
    prereqs=["trees", "binary-search"],
    why="""
A BST is a binary tree with a promise: everything in the left subtree is
smaller, everything in the right is larger. That single rule turns search,
insertion and deletion into a walk down one path — O(h), which is O(log n) when
the tree is balanced.

The reason it gets its own unit is that the invariant is **global, not local**.
Checking only that each node sits between its two children is the most common
wrong answer to *"is this a valid BST?"*, and understanding why is worth more
than the code.
""",
    model="""
### The invariant

For every node: **all** values in its left subtree are less than it, and **all**
values in its right subtree are greater. Not just the immediate children — the
entire subtree.

```
      5
     / \\
    3   8
       / \\
      4   9      ← 4 < 5, so it must not be in the right subtree
```

Every child-versus-parent comparison here passes. The tree is still invalid.

### Searching is a descent

```java
while (node != null && node.val != target)
    node = (target < node.val) ? node.left : node.right;
```

Each comparison discards a whole subtree — it is binary search, expressed as a
structure.

### Validation needs a range

The correct check carries the interval a node is allowed to live in:

```java
static boolean valid(TreeNode n, long lo, long hi) {
    if (n == null) return true;
    if (n.val <= lo || n.val >= hi) return false;
    return valid(n.left, lo, n.val) && valid(n.right, n.val, hi);
}
// call with (root, Long.MIN_VALUE, Long.MAX_VALUE)
```

Descending left tightens the upper bound; descending right tightens the lower
one. `long` bounds avoid an overflow when a node holds `Integer.MIN_VALUE`.

The alternative: an in-order traversal must produce strictly increasing values.
That is often the cleanest implementation and is worth saying aloud.

### In-order is sorted

That is the defining consequence. It gives you the k-th smallest for free —
traverse in order and stop after k visits, O(h + k) rather than O(n):

```java
// iterative in-order, so you can stop early
Deque<TreeNode> st = new ArrayDeque<>();
TreeNode cur = root;
while (cur != null || !st.isEmpty()) {
    while (cur != null) { st.push(cur); cur = cur.left; }
    cur = st.pop();
    if (--k == 0) return cur.val;
    cur = cur.right;
}
```

### Lowest common ancestor, the easy way

In a BST you do not search. Walk from the root: if both targets are smaller, go
left; if both are larger, go right; otherwise you are standing on the split
point, which is the LCA. O(h), no recursion needed.

### The balance caveat

All of this is O(h), and h is O(log n) only if the tree is balanced. Insert
sorted data into a plain BST and you get a linked list with O(n) operations.
Self-balancing trees (red-black, AVL) fix it — in Java, `TreeMap` is that
structure, and is what you should reach for in practice.

### Pausing an in-order walk: the iterator

The iterative in-order loop above keeps its place on an explicit stack, so it
can stop after one value and resume later. That is a BST iterator: push the left
spine of the root; `next()` pops a node and pushes the left spine of its right
child. Each node is pushed and popped once over the whole iteration, so `next`
is O(1) *amortised* and the stack never holds more than one path — O(h) memory.

### `TreeMap` and `TreeSet` as tools

A balanced BST you do not write answers the question a hash map cannot: *what is
nearest?*

| Call | Returns | Cost |
| --- | --- | --- |
| `floor(x)` / `floorKey(x)` | largest ≤ x, or null | O(log n) |
| `ceiling(x)` / `ceilingKey(x)` | smallest ≥ x, or null | O(log n) |
| `lower(x)` / `higher(x)` | strictly below / above | O(log n) |
| `first()` / `last()` | the extremes | O(log n) |

Use it whenever a problem needs a sorted collection *and* inserts or deletes
between queries: a sliding window you must search ("is any value within t?"),
bookings you must check for overlap, a leaderboard that keeps changing.
""",
    signals=[
        _sig("“search / insert in a BST”", "Descend by comparison",
             "Each step discards one subtree."),
        _sig("“is this a valid BST?”", "Range check, or in-order must increase",
             "Comparing only with the children is wrong."),
        _sig("“k-th smallest”", "In-order traversal, stop at k",
             "O(h + k), not O(n)."),
        _sig("“lowest common ancestor” in a BST", "Walk to the split point",
             "Where the two targets diverge is the answer."),
        _sig("“sorted order”, “range query”", "In-order, pruned by the bounds",
             "Skip subtrees that cannot intersect the range."),
        _sig("Insertions arrive sorted", "Beware: the tree degenerates",
             "O(n) per operation. Use a balanced map in practice."),
    ],
    skeletons=[
        _sk("Search / insert",
            "The two basic operations, iteratively.",
            """
TreeNode cur = root, parent = null;
while (cur != null) {
    parent = cur;
    if (target == cur.val) return cur;
    cur = (target < cur.val) ? cur.left : cur.right;
}
// for insert: attach the new node under `parent` on the side you fell off
""",
            "Iterative avoids the stack entirely; the tree may be deep."),
        _sk("Validate with bounds",
            "The correct BST validity check.",
            """
static boolean valid(TreeNode n, long lo, long hi) {
    if (n == null) return true;
    if (n.val <= lo || n.val >= hi) return false;
    return valid(n.left, lo, n.val) && valid(n.right, n.val, hi);
}
""",
            "`long` bounds, because a node may legitimately hold `Integer.MIN_VALUE`."),
        _sk("k-th smallest (early-exit in-order)",
            "Order statistics on a BST.",
            """
Deque<TreeNode> st = new ArrayDeque<>();
TreeNode cur = root;
while (cur != null || !st.isEmpty()) {
    while (cur != null) { st.push(cur); cur = cur.left; }
    cur = st.pop();
    if (--k == 0) return cur.val;
    cur = cur.right;
}
""",
            "The iterative form is what makes stopping early possible."),
        _sk("LCA in a BST",
            "Lowest common ancestor, without any searching.",
            """
while (root != null) {
    if (p < root.val && q < root.val)       root = root.left;
    else if (p > root.val && q > root.val)  root = root.right;
    else return root;                        // the split point
}
""",
            "O(h), no recursion, no extra memory."),
        _sk("BST iterator",
            "Sorted values one at a time, O(h) memory.",
            """
class BSTIterator {
    private final Deque<TreeNode> st = new ArrayDeque<>();
    BSTIterator(TreeNode root) { pushLeft(root); }
    private void pushLeft(TreeNode n) { for (; n != null; n = n.left) st.push(n); }
    boolean hasNext() { return !st.isEmpty(); }
    int next() {
        TreeNode n = st.pop();
        pushLeft(n.right);                 // the successor's subtree
        return n.val;
    }
}
""",
            "Amortised O(1): every node is pushed once and popped once in total."),
        _sk("Nearest values with TreeSet",
            "Floor/ceiling queries; searching a changing window.",
            """
TreeSet<Long> window = new TreeSet<>();
for (int j = 0; j < n; j++) {
    Long c = window.ceiling((long) a[j] - t);    // smallest value >= a[j] - t
    if (c != null && c <= (long) a[j] + t) return true;
    window.add((long) a[j]);
    if (j >= k) window.remove((long) a[j - k]);  // keep the last k
}
""",
            "`long`, because `a[j] - t` overflows `int` at the extremes."),
    ],
    costs=[
        _cost("Search / insert / delete", "O(h)", "O(1) iterative", "h = log n when balanced."),
        _cost("Validate", "O(n)", "O(h)", "Every node must be checked."),
        _cost("k-th smallest", "O(h + k)", "O(h)", "In-order with an early exit."),
        _cost("LCA", "O(h)", "O(1)", "A single descent."),
        _cost("Degenerate (sorted inserts)", "O(n) per op", "O(n)", "The tree became a list."),
    ],
    pitfalls=[
        _pit("An invalid tree passes validation",
             "Only parent-child pairs were compared; the invariant applies to whole subtrees.",
             "Carry `(lo, hi)` bounds down, or verify that in-order output is strictly "
             "increasing."),
        _pit("Validation overflows at the extremes",
             "`Integer.MIN_VALUE` as a sentinel collides with a real node value.",
             "Use `long` bounds, or pass `Integer` objects and treat null as unbounded."),
        _pit("Duplicates break the search",
             "The BST rule says nothing about equal values.",
             "Decide a convention (duplicates to the right, or store a count per node) and "
             "apply it everywhere."),
        _pit("Every operation is O(n)",
             "Values were inserted in sorted order, so the tree is a chain.",
             "Use a self-balancing structure — `TreeMap` in Java."),
        _pit("k-th smallest traverses the whole tree",
             "A recursive in-order collected everything into a list first.",
             "Use the iterative form and stop the moment the counter reaches zero."),
    ],
    lessons=["bst", "tree_traversal", "binary_search"],
    checks=[
        _chk("Why is “each node is between its children” not a valid BST check?",
             "The invariant covers whole subtrees. A node deep in the right subtree can be "
             "smaller than the root while satisfying every local comparison."),
        _chk("What does an in-order traversal of a BST produce?",
             "The values in strictly ascending order — which is both the definition of "
             "validity and the mechanism for k-th smallest."),
        _chk("How do you find the LCA of two values in a BST without searching?",
             "Descend while both targets are on the same side. The first node where they "
             "split — or which equals one of them — is the LCA."),
        _chk("When is a BST *not* O(log n)?",
             "When it is unbalanced. Sorted insertions produce a chain, making every "
             "operation O(n). Balanced variants (or `TreeMap`) restore the bound."),
        _chk("Why is a BST iterator's `next()` O(1) amortised when one call can push a long spine?",
             "Across a full iteration every node is pushed exactly once and popped exactly "
             "once — 2n stack operations for n calls."),
        _chk("What can a `TreeSet` answer that a `HashSet` cannot?",
             "Order questions: the nearest value at or below x (`floor`), at or above x "
             "(`ceiling`), and the extremes — each in O(log n), with inserts and deletes in between."),
    ],
    interview="""
The BST question that separates candidates is validation, and the tell is
whether you reach for bounds or for local comparisons. Offer both correct
approaches — the range recursion and "in-order must be increasing" — and then
note the practical point: in production this is a `TreeMap`, because a hand-rolled
BST degenerates on sorted input.
""",
    rungs=[
        _rung("Core", "The descent.",
              ["bst-search"],
              {"bst-search": "Write it iteratively. There is no reason to spend stack on a straight-line walk."}),
        _rung("Variations", "The invariant, used and checked.",
              ["bst-insert", "validate-bst", "lca-bst", "kth-smallest-bst"],
              {"validate-bst": "Try the naive child-comparison version first and build the counterexample that defeats it.",
               "kth-smallest-bst": "Iterative in-order with an early exit — O(h + k), not O(n)."}),
    ],
    next_up="""
Trees recurse over a structure that already exists. Backtracking recurses over
one it *builds* — and has to take apart again.
""",
)


# --- Unit 25 — Backtracking --------------------------------------------------

_unit(
    "backtracking", "Backtracking", "♟️", _S6,
    "Choose, explore, un-choose — and prune before you descend.",
    weight=3,
    prereqs=["recursion", "strings"],
    why="""
Some problems have no formula: you must search the space of possibilities.
Subsets, permutations, partitions, placements, puzzles — the answer is found by
trying, and the only thing keeping it feasible is **pruning**, cutting off
branches that cannot lead to a solution before you walk them.

Backtracking is recursion plus one new obligation: the state is *shared*, so
every change you make before a recursive call must be undone after it. That
single discipline is what the unit is really teaching.
""",
    model="""
### The template

```java
void backtrack(State s) {
    if (isComplete(s)) { record(s); return; }
    for (Choice c : choices(s)) {
        if (!isValid(s, c)) continue;   // prune: never descend into a dead branch
        apply(s, c);                    // choose
        backtrack(s);                   // explore
        undo(s, c);                     // un-choose  ← the line people forget
    }
}
```

`apply` and `undo` must be exact mirrors. If `apply` appends to a list, `undo`
removes the **last** element. If `apply` sets `used[i] = true`, `undo` sets it
back to false. Every bug in this unit is an asymmetry between those two lines.

### Subsets versus permutations versus combinations

The difference is entirely in what `choices(s)` returns:

| Want | Loop over | Guard |
| --- | --- | --- |
| **Subsets** | `i` from `start` to n | recurse with `start = i + 1` |
| **Combinations** (choose k) | same, plus a size check | stop when `size == k` |
| **Permutations** | every index | a `used[]` array |
| **Combination sum** (reuse allowed) | same, from `start` | recurse with `start = i`, not `i + 1` |

`start` is what stops subsets from being generated in every order; `used[]` is
what lets permutations use every position exactly once. Choosing between them
*is* the problem.

### Pruning is the whole game

Without pruning, this is brute force with extra steps. Three kinds worth
knowing:

- **Feasibility**: the partial state already violates a constraint (a repeated
  queen's column) — stop now.
- **Bound**: the best possible completion still cannot beat the current answer —
  stop now.
- **Symmetry**: two branches are equivalent (skipping duplicate values at the
  same depth) — explore one.

Sorting the input first is often what makes pruning possible: once sorted, the
moment a running sum exceeds the target you can `break` rather than `continue`,
because everything after is larger.

### Complexity, honestly

Subsets are O(2ⁿ · n), permutations O(n! · n) — the `· n` is the cost of copying
each completed answer out. These numbers are why n is always tiny in these
problems, and quoting them is how you show you know the search is exponential by
nature rather than by accident.

### Grids

Word search is backtracking on a grid: mark the cell visited, recurse to the
four neighbours, unmark on the way out. Mutating the grid in place (a sentinel
character) and restoring it afterwards is the standard O(1)-space visited set.
""",
    signals=[
        _sig("“all subsets / all combinations”", "`start` index recursion",
             "The index stops re-generating the same set in another order."),
        _sig("“all permutations / arrangements”", "`used[]` flags",
             "Every position is available at every depth, once."),
        _sig("“all ways to …”, “count the ways” with n ≤ 20", "Backtracking",
             "The constraint is the setter telling you exponential is expected."),
        _sig("“place k items such that no two conflict”", "Backtracking with feasibility pruning",
             "N-queens, Sudoku, scheduling."),
        _sig("“find a word in a grid”", "DFS + mark/unmark",
             "The grid itself is the visited set."),
        _sig("Duplicates in the input and duplicate answers forbidden", "Sort, then skip equals at the same depth",
             "`if (i > start && a[i] == a[i-1]) continue;`"),
    ],
    skeletons=[
        _sk("Subsets / combinations",
            "Every subset, or every k-subset.",
            """
void dfs(int start, List<Integer> cur) {
    result.add(new ArrayList<>(cur));         // copy — cur keeps mutating
    for (int i = start; i < a.length; i++) {
        cur.add(a[i]);                        // choose
        dfs(i + 1, cur);                      // explore (i + 1 ⇒ no reuse)
        cur.remove(cur.size() - 1);           // un-choose
    }
}
""",
            "`dfs(i, cur)` instead of `i + 1` allows reuse — that is combination-sum."),
        _sk("Permutations",
            "Every ordering.",
            """
void dfs(List<Integer> cur, boolean[] used) {
    if (cur.size() == a.length) { result.add(new ArrayList<>(cur)); return; }
    for (int i = 0; i < a.length; i++) {
        if (used[i]) continue;
        used[i] = true;  cur.add(a[i]);
        dfs(cur, used);
        cur.remove(cur.size() - 1);  used[i] = false;     // both undone
    }
}
""",
            "Two things applied, two things undone, in mirror order."),
        _sk("Prune with a sorted input",
            "Combination sum, subset sum, partition problems.",
            """
Arrays.sort(a);
void dfs(int start, int remaining) {
    if (remaining == 0) { count++; return; }
    for (int i = start; i < a.length; i++) {
        if (a[i] > remaining) break;                       // sorted ⇒ all later are worse
        if (i > start && a[i] == a[i - 1]) continue;       // skip duplicate branches
        dfs(i + 1, remaining - a[i]);
    }
}
""",
            "`break` rather than `continue` is the payoff for sorting."),
        _sk("Grid DFS with mark / unmark",
            "Word search, path finding with reuse forbidden.",
            """
boolean dfs(int i, int j, int k) {
    if (k == word.length()) return true;
    if (i < 0 || i >= rows || j < 0 || j >= cols) return false;
    if (g[i][j] != word.charAt(k)) return false;

    char saved = g[i][j];
    g[i][j] = '#';                                  // mark visited
    boolean found = dfs(i+1, j, k+1) || dfs(i-1, j, k+1)
                 || dfs(i, j+1, k+1) || dfs(i, j-1, k+1);
    g[i][j] = saved;                                // restore — always
    return found;
}
""",
            "Restore on *every* exit path, including the successful one."),
    ],
    costs=[
        _cost("All subsets", "O(2ⁿ · n)", "O(n)", "The `· n` is copying each answer out."),
        _cost("All permutations", "O(n! · n)", "O(n)", "n ≤ 10 in practice."),
        _cost("Combinations C(n, k)", "O(C(n,k) · k)", "O(k)", "Far smaller than 2ⁿ for small k."),
        _cost("N-queens", "much better than O(nⁿ)", "O(n)", "Pruning is what makes it finish."),
        _cost("Grid word search", "O(rows · cols · 4^len)", "O(len)", "Pruned hard by the character check."),
    ],
    pitfalls=[
        _pit("Every result in the output list is identical (or empty)",
             "The mutable working list was stored by reference instead of copied.",
             "`result.add(new ArrayList<>(cur))` — take a snapshot."),
        _pit("Results leak between branches",
             "The `undo` step is missing, or does not mirror the `apply`.",
             "Every mutation before the recursive call needs an exact inverse after it."),
        _pit("Subsets are generated in every order (duplicates)",
             "The loop restarts from 0 instead of from `start`.",
             "Pass `i + 1` (or `i` for reuse) as the next `start`."),
        _pit("Duplicate answers when the input has repeated values",
             "Equal values at the same depth each opened their own branch.",
             "Sort first, then `if (i > start && a[i] == a[i-1]) continue;`"),
        _pit("The grid search never terminates or revisits cells",
             "The cell was not marked, or was not restored on an early return.",
             "Mark before recursing, restore on every return path."),
        _pit("It times out even though the logic is right",
             "No pruning — the entire space is being explored.",
             "Add a feasibility check before descending, and sort so you can `break`."),
    ],
    lessons=["backtracking", "pruning", "recursion"],
    checks=[
        _chk("Why must the result be copied when recording an answer?",
             "The working list is mutated on the way back up. Storing the reference means "
             "every recorded answer ends up pointing at the same, eventually-empty list."),
        _chk("What distinguishes subset generation from permutation generation?",
             "Subsets pass a `start` index so each element is considered once in a fixed "
             "order. Permutations consider every index at every depth, excluded only by a "
             "`used[]` flag."),
        _chk("How do you avoid duplicate results when the input contains repeats?",
             "Sort, then at each depth skip a value equal to the previous one: "
             "`if (i > start && a[i] == a[i-1]) continue;`. Equal values at the same depth "
             "generate identical branches."),
        _chk("What is the complexity of generating all subsets, and why the extra factor?",
             "O(2ⁿ · n): there are 2ⁿ subsets, and copying each one out costs up to n."),
        _chk("Why does sorting the candidates enable a `break` rather than a `continue`?",
             "Once sorted, if the current candidate already exceeds what remains, so does "
             "every later one — the whole tail of the loop is dead."),
    ],
    interview="""
Backtracking is graded on structure, not cleverness. Write the four lines —
choose, explore, un-choose, record — before filling in any logic, and the
interviewer can follow you. Then volunteer the complexity (2ⁿ or n!) and the
pruning: *"I will sort first so I can break early, and skip equal values at the
same depth to avoid duplicates"* covers everything they were going to ask.
""",
    traces=[
        _trace(
            "Every frame of subsets([5, 1]) — including the undos",
            "One row per *event*, not per call, so the push / explore / undo cycle is "
            "visible. `chosen` is a single mutable list shared by the whole search tree, "
            "which is the only reason the space is O(n) instead of O(2ⁿ · n).",
            ["#", "Frame", "Action", "`chosen` after", "Emitted"],
            [
                ["1", "rec(0)", "skip a[0] = 5 → recurse", "[]", "—"],
                ["2", "rec(1)", "skip a[1] = 1 → recurse", "[]", "—"],
                ["3", "rec(2)", "i == n → emit", "[]", "`-`"],
                ["4", "rec(1)", "take a[1] = 1 → **add**", "[1]", "—"],
                ["5", "rec(2)", "i == n → emit", "[1]", "`1`"],
                ["6", "rec(1)", "**UNDO** — pop 1", "[]", "—"],
                ["7", "rec(0)", "take a[0] = 5 → **add**", "[5]", "—"],
                ["8", "rec(1)", "skip a[1] → recurse", "[5]", "—"],
                ["9", "rec(2)", "i == n → emit", "[5]", "`5`"],
                ["10", "rec(1)", "take a[1] = 1 → **add**", "[5, 1]", "—"],
                ["11", "rec(2)", "i == n → emit", "[5, 1]", "`5 1`"],
                ["12", "rec(1)", "**UNDO** — pop 1", "[5]", "—"],
                ["13", "rec(0)", "**UNDO** — pop 5", "[]", "—"],
            ],
            "Four subsets, two adds per element, and **one undo for every add** — always "
            "at the moment the take-branch returns, never anywhere else. Note row 13: the "
            "final undo restores `chosen` for a caller that does not exist, and leaving it "
            "out would still pass this test. Write it anyway; the frame above you in a "
            "real problem is not always the root.",
        ),
        _trace(
            "The same run with the undo DELETED",
            "This is the bug, executed. Nothing crashes and the output length is even "
            "right — the *contents* are quietly wrong, which is why a missing undo can "
            "survive a casual read of the code.",
            ["#", "Frame", "Action", "`chosen` after", "Emitted"],
            [
                ["1-3", "rec(0) → rec(1) → rec(2)", "skip, skip, emit", "[]", "`-`"],
                ["4-5", "rec(1) → rec(2)", "take 1, emit", "[1]", "`1`"],
                ["6", "rec(1)", "returns — **1 is never popped**", "[1]", "—"],
                ["7", "rec(0)", "take 5 → add, onto a dirty list", "[1, 5]", "—"],
                ["8-9", "rec(1) → rec(2)", "skip, emit", "[1, 5]", "`1 5` ← wrong"],
                ["10-11", "rec(1) → rec(2)", "take 1 again, emit", "[1, 5, 1]", "`1 5 1` ← wrong"],
            ],
            "`5` alone never appears, `1` appears twice in one subset, and the output is "
            "`-`, `1`, `1 5`, `1 5 1` — four lines, as expected, two of them nonsense. "
            "Every backtracking bug for the next ten problems is this, and the symptom is "
            "always an answer that contains something from a branch that already finished.",
        ),
    ],
    rungs=[
        _rung("Warm up", "Sixteen answers you can check by hand, and one line that matters.",
              ["all-subsets-small"],
              {"all-subsets-small": "Four elements, so every wrong answer is readable. Delete the undo on purpose once and look at what comes out."}),
        _rung("Core", "The template, with the three choice-set variants.",
              ["generate-subsets", "combinations-nk", "generate-permutations"],
              {"generate-subsets": "Type the four lines from memory. Everything else in this unit is this with a different guard.",
               "generate-permutations": "The `used[]` array. Undo both mutations, in mirror order."}),
        _rung("Variations", "Counting instead of listing, and constrained construction.",
              ["subset-sum-count", "combination-sum-count", "generate-parentheses",
               "letter-combinations-phone"],
              {"combination-sum-count": "Reuse is allowed, so recurse with `i`, not `i + 1`. One character, entirely different problem.",
               "generate-parentheses": "Pure feasibility pruning: never close more than you have opened."}),
        _rung("Stretch", "Pruning is the difference between finishing and not.",
              ["palindrome-partition-count", "restore-ip-addresses", "word-search",
               "n-queens-count", "sudoku-solvable"],
              {"word-search": "Mark and restore the grid cell. Restoring on the success path too is the bug to avoid.",
               "n-queens-count": "Track occupied columns and both diagonals as sets, so validity is O(1) rather than O(n).",
               "sudoku-solvable": "Choose the most-constrained empty cell first — a heuristic that turns minutes into milliseconds."}),
    ],
    next_up="""
Backtracking explores a tree it invents. A graph is the same exploration on a
structure that can loop back on itself — which changes exactly one thing.
""",
)


# --- Unit 26 — Graph traversal -----------------------------------------------

_unit(
    "graph-traversal", "Graph Traversal: BFS & DFS", "🕸️", _S6,
    "Trees with cycles — so you need a visited set, and BFS gives shortest paths.",
    weight=3,
    prereqs=["queues-and-deques", "recursion"],
    why="""
A graph is the general case of everything in this stage. A tree is a graph
without cycles; a grid is a graph whose neighbours are implicit; a dependency
list is a graph with direction. Once you can traverse one, an entire category of
word problems — islands, regions, spreading, reachability, shortest hops —
becomes the same twenty lines.

Exactly one thing changes from tree traversal: a graph can return to where it
has been, so you must remember where you have been. Forget the visited set and
the program does not give a wrong answer — it runs forever.
""",
    model="""
### Representing a graph

| Form | Use when |
| --- | --- |
| Adjacency list `List<Integer>[]` | Almost always — sparse, O(V + E) memory |
| Adjacency matrix `boolean[][]` | V is small (≤ ~1000) and you need O(1) edge tests |
| Implicit (a grid) | Neighbours are computed, never stored |

```java
List<List<Integer>> g = new ArrayList<>();
for (int i = 0; i < n; i++) g.add(new ArrayList<>());
for (int[] e : edges) {
    g.get(e[0]).add(e[1]);
    g.get(e[1]).add(e[0]);       // omit this line for a directed graph
}
```

### BFS — layer by layer

```java
Queue<Integer> q = new ArrayDeque<>();
boolean[] seen = new boolean[n];
q.add(src); seen[src] = true;
int dist = 0;
while (!q.isEmpty()) {
    int size = q.size();                 // one whole layer
    for (int i = 0; i < size; i++) {
        int u = q.poll();
        for (int v : g.get(u))
            if (!seen[v]) { seen[v] = true; q.add(v); }
    }
    dist++;
}
```

**BFS finds shortest paths in unweighted graphs**, because it reaches every node
in order of hop count. That is the single most useful fact about it — and note
where it comes from: it is a property of the **queue**, not of the graph.
Arrival order is distance order, exactly as the queues unit argued. Swap the
queue for a stack and the same code is a DFS that finds *a* path rather than the
shortest one; swap it for a `PriorityQueue` and you have Dijkstra.

**Mark visited when you enqueue, not when you dequeue.** Marking on dequeue lets
the same node be added several times before it is processed, which quietly turns
O(V + E) into something much worse.

### DFS — as deep as possible

```java
void dfs(int u) {
    seen[u] = true;
    for (int v : g.get(u)) if (!seen[v]) dfs(v);
}
```

DFS answers *connectivity* questions — components, flood fill, cycle detection,
topological order. It does **not** give shortest paths. Use an explicit stack
when depth could exceed ~10⁴.

### Grids are graphs

A cell `(i, j)` has up to four neighbours. Nothing else changes — the direction
array from the simulation unit is the adjacency list:

```java
for (int[] d : DIRS) {
    int ni = i + d[0], nj = j + d[1];
    if (ni < 0 || ni >= rows || nj < 0 || nj >= cols) continue;
    if (seen[ni][nj] || g[ni][nj] == '0') continue;
    ...
}
```

Counting islands is: for every unvisited land cell, run one traversal and add
one to the count. The traversal is what erases the whole island.

### Multi-source BFS

Start with *every* source already in the queue. Rotting oranges, distance to the
nearest zero, fire spreading — one pass gives the distance from the nearest
source to every cell, at no extra cost.

### Bipartite checking

Two-colour the graph during a traversal: colour each neighbour the opposite of
the current node. A conflict means an odd-length cycle, so the graph is not
bipartite. It is BFS with an `int[] colour` instead of a `boolean[] seen`.

### Cloning a graph

Copy every node reachable from a start node, with neighbour lists pointing at
copies. The traversal needs a visited set; the copy needs an old → new map. They
are the same map: *create a node's copy the first time you see it*, and a cycle
finds the existing copy instead of recursing forever.
""",
    signals=[
        _sig("“shortest path”, “fewest steps”, unweighted", "BFS",
             "Layer order is hop order. This is the headline fact."),
        _sig("“connected components”, “islands”, “regions”", "DFS or BFS from each unvisited node",
             "One traversal consumes one component."),
        _sig("“can I reach …?”", "Either traversal",
             "Only reachability matters, so the order does not."),
        _sig("“spreads from several places at once”", "Multi-source BFS",
             "Seed the queue with every source."),
        _sig("“two groups with no edge inside a group”", "Two-colouring during traversal",
             "A conflict proves an odd cycle."),
        _sig("Edges have DIFFERENT weights", "Not BFS — Dijkstra",
             "Layer order stops matching distance order."),
    ],
    skeletons=[
        _sk("BFS with distance",
            "Shortest hops, level counting, spreading.",
            """
Queue<Integer> q = new ArrayDeque<>();
int[] dist = new int[n];
Arrays.fill(dist, -1);
q.add(src); dist[src] = 0;
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : g.get(u))
        if (dist[v] == -1) {          // unvisited ⇒ mark AND enqueue together
            dist[v] = dist[u] + 1;
            q.add(v);
        }
}
""",
            "`dist` doubles as the visited set, which removes a whole class of bugs."),
        _sk("DFS over components",
            "Counting islands, regions, connected groups.",
            """
int components = 0;
for (int i = 0; i < n; i++) {
    if (seen[i]) continue;
    components++;
    dfs(i);            // consumes this entire component
}
""",
            "The count of traversals started is the count of components."),
        _sk("Grid traversal",
            "Islands, flood fill, shortest path on a grid.",
            """
static final int[][] DIRS = {{1,0},{-1,0},{0,1},{0,-1}};

void fill(int i, int j) {
    if (i < 0 || i >= rows || j < 0 || j >= cols) return;
    if (g[i][j] != '1') return;          // water, or already consumed
    g[i][j] = '0';                       // mark by mutating — no visited array
    for (int[] d : DIRS) fill(i + d[0], j + d[1]);
}
""",
            "Sinking the island as you go is the standard O(1)-extra-space visited set."),
        _sk("Multi-source BFS",
            "Nearest source for every cell, in one pass.",
            """
for (int[] s : sources) { q.add(s); dist[s[0]][s[1]] = 0; }
while (!q.isEmpty()) { /* ordinary BFS from here */ }
""",
            "Seeding all sources at distance 0 makes layer k mean “k from the nearest”."),
        _sk("Two-colouring",
            "Bipartite check.",
            """
int[] colour = new int[n];
Arrays.fill(colour, -1);
colour[src] = 0;
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : g.get(u)) {
        if (colour[v] == -1) { colour[v] = 1 - colour[u]; q.add(v); }
        else if (colour[v] == colour[u]) return false;    // odd cycle
    }
}
""",
            "Run it from every uncoloured node — the graph may be disconnected."),
        _sk("Clone a graph",
            "Deep copy of everything reachable from one node.",
            """
Map<Node, Node> copy = new HashMap<>();          // also the visited set
copy.put(start, new Node(start.val));
Deque<Node> q = new ArrayDeque<>(List.of(start));
while (!q.isEmpty()) {
    Node u = q.poll();
    for (Node v : u.neighbors) {
        if (!copy.containsKey(v)) { copy.put(v, new Node(v.val)); q.add(v); }
        copy.get(u).neighbors.add(copy.get(v));
    }
}
return copy.get(start);
""",
            "Record the copy before exploring from it — otherwise a cycle copies forever."),
    ],
    costs=[
        _cost("BFS / DFS", "O(V + E)", "O(V)", "Each node and edge handled once."),
        _cost("Grid traversal", "O(rows · cols)", "O(rows · cols)", "Queue or recursion depth."),
        _cost("Adjacency matrix traversal", "O(V²)", "O(V²)", "Only for dense or small graphs."),
        _cost("Multi-source BFS", "O(V + E)", "O(V)", "No more expensive than single-source."),
        _cost("Recursive DFS on a large graph", "O(V + E)", "O(V) stack", "Overflows past ~10⁴ depth."),
    ],
    pitfalls=[
        _pit("The program hangs or loops forever",
             "No visited set, so a cycle is traversed indefinitely.",
             "Mark nodes visited; this is the one difference from tree traversal."),
        _pit("BFS is much slower than expected",
             "Nodes were marked visited on dequeue, so duplicates piled up in the queue.",
             "Mark on enqueue, in the same statement that adds them."),
        _pit("BFS returns a path that is not shortest",
             "The edges have different weights, where BFS assumes all are 1.",
             "Use Dijkstra for weighted graphs."),
        _pit("Only part of the graph is visited",
             "The traversal was started from one node, but the graph is disconnected.",
             "Loop over all nodes and start a traversal from each unvisited one."),
        _pit("`StackOverflowError` on a large grid",
             "Recursive DFS went ~10⁵ deep on a snake-shaped region.",
             "Use BFS with a queue, or DFS with an explicit stack."),
        _pit("A neighbour read throws out of bounds",
             "The bounds test came after the array access.",
             "Bounds first, then the value check."),
    ],
    lessons=["graph_repr", "bfs", "flood_fill", "visited_set"],
    checks=[
        _chk("Why does BFS give shortest paths but DFS does not?",
             "BFS visits nodes in order of hop count, so the first time it reaches a node it "
             "has used the fewest possible edges. DFS may reach it by a long detour first."),
        _chk("Why mark nodes visited on enqueue rather than on dequeue?",
             "Otherwise a node with several incoming edges is enqueued multiple times before "
             "being processed, inflating the queue and the running time."),
        _chk("What is the only structural difference between traversing a tree and a graph?",
             "The visited set. A tree cannot revisit a node; a graph can, and without the set "
             "the traversal never terminates."),
        _chk("How does multi-source BFS give the distance to the *nearest* source?",
             "All sources start at distance 0 in the queue, so the layered expansion reaches "
             "each node at the minimum distance over all of them."),
        _chk("What does a colour conflict during two-colouring prove?",
             "That an odd-length cycle exists, and therefore the graph is not bipartite."),
        _chk("Cloning a graph: why is the old → new map enough to stop cycles?",
             "A node's copy is recorded the first time it is seen, so meeting it again along a "
             "cycle finds the existing copy and links to it instead of copying again."),
    ],
    interview="""
Graph questions are usually disguised: "can these courses be finished", "how
many groups", "fewest moves". The interview skill is *modelling* — saying out
loud what the nodes are, what the edges are, and whether they are directed —
before touching the traversal. Once that sentence exists, the code is a
template. And say why BFS: "edges are unweighted, so BFS layers are distances".
""",
    rungs=[
        _rung("Warm up", "One BFS, and the outer loop that turns it into an answer.",
              ["count-connected-components"],
              {"count-connected-components": "The whole unit with nothing else attached: adjacency list, one shared `seen`, and a BFS started from every node you have not reached yet."}),
        _rung("Core", "Traversal on an implicit graph, then a real one, then a directed one.",
              ["number-of-islands", "shortest-path-binary-matrix", "bipartite-check",
               "directed-path-exists"],
              {"number-of-islands": "One traversal per unvisited land cell. Sink the island as you go.",
               "shortest-path-binary-matrix": "BFS, because the grid is unweighted — and 8-directional, so check the direction array.",
               "directed-path-exists": "One-way edges, where every undirected reflex is wrong — and wrong on *some* inputs only, which is worse. Check that swapping `s` and `t` can flip your answer."}),
        _rung("Variations", "One BFS, many sources — and one BFS that stops early.",
              ["rotting-oranges", "reachable-within-k"],
              {"rotting-oranges": "Seed the queue with *every* rotten cell at time 0. The distance-order invariant does not care how many sources there were, only that they started together.",
               "reachable-within-k": "The cap is a refusal to expand, not a filter at the end — otherwise K bought you nothing and you walked the whole graph anyway."}),
        _rung("Stretch", "A graph you have to build before you can walk it.",
              ["word-ladder-length"],
              {"word-ladder-length": "The nodes are words and the edges are one-letter changes. Building the adjacency efficiently (wildcard buckets) is most of the problem."}),
    ],
    next_up="""
Traversal answers “can I get there”. Direction adds a second question: is there
an order in which everything can be done at all?
""",
)


# --- Unit 27 — Topological sort ----------------------------------------------

_unit(
    "topological-sort", "Topological Sort & Cycles", "📋", _S6,
    "Order the dependencies — or prove that no order exists.",
    weight=2,
    prereqs=["graph-traversal"],
    why="""
Anything with prerequisites is a directed graph: courses, build targets,
package installs, task schedules. Two questions matter, and they are the same
question: **in what order can these be done?** and **is it possible at all?** —
because the only thing that makes it impossible is a cycle.

Kahn's algorithm answers both at once, which is why it is the standard tool: it
produces the order, and if it cannot place every node, the leftovers are exactly
the nodes trapped in a cycle.
""",
    model="""
### Kahn's algorithm (BFS on in-degrees)

The in-degree of a node is how many prerequisites it still has. A node with
in-degree 0 is ready.

```java
int[] indeg = new int[n];
for (int u = 0; u < n; u++)
    for (int v : g.get(u)) indeg[v]++;

Queue<Integer> q = new ArrayDeque<>();
for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);

List<Integer> order = new ArrayList<>();
while (!q.isEmpty()) {
    int u = q.poll();
    order.add(u);
    for (int v : g.get(u))
        if (--indeg[v] == 0) q.add(v);     // its last prerequisite just cleared
}
boolean possible = order.size() == n;      // ← the cycle test, free
```

`order.size() == n` is the whole cycle detection. Nodes in a cycle never reach
in-degree 0, so they are never enqueued. No separate check is needed.

**Edge direction matters and is the most common bug.** "To take B you must first
take A" means the edge runs **A → B**, and B's in-degree counts A. Writing it
backwards produces a valid-looking topological order of the reversed graph.

### DFS with three colours

The alternative, and the one that detects cycles in a graph you are not
ordering:

```java
// 0 = unvisited, 1 = in progress (on the current path), 2 = finished
boolean hasCycle(int u) {
    if (state[u] == 1) return true;      // back edge — a cycle
    if (state[u] == 2) return false;     // already fully explored
    state[u] = 1;
    for (int v : g.get(u)) if (hasCycle(v)) return true;
    state[u] = 2;                        // leaving: mark finished
    return false;
}
```

Two states are not enough. A node already *finished* is fine to meet again; a
node still *in progress* means you have looped back onto your own path. The
topological order is the finish order, reversed.

### Undirected graphs are different

In an undirected graph every edge looks like a back edge from the child's point
of view — you can always walk back to your parent. A cycle exists only if you
reach an already-visited node that is **not** your parent. Union-find (next
unit) is usually the cleaner tool there.

### Uniqueness and lexicographic order

If the queue ever holds more than one ready node, several valid orders exist.
Swap the queue for a `PriorityQueue` and you get the lexicographically smallest
one — which is how "the alien alphabet" style problems are usually specified.
""",
    signals=[
        _sig("“prerequisites”, “before”, “depends on”", "Topological sort",
             "The wording is literally a directed edge."),
        _sig("“can all tasks be finished?”", "Kahn's, then `order.size() == n`",
             "Failure means a cycle."),
        _sig("“build order”, “course schedule”", "Kahn's algorithm",
             "The order comes out of the queue."),
        _sig("“deduce the alphabet from sorted words”", "Build edges from adjacent pairs, then topo-sort",
             "The first differing character gives one edge per pair."),
        _sig("“does this directed graph have a cycle?”", "Three-colour DFS",
             "An in-progress node reached again is a back edge."),
        _sig("“smallest valid order”", "Kahn's with a priority queue",
             "Ready nodes are taken in sorted order."),
    ],
    skeletons=[
        _sk("Kahn's algorithm",
            "Ordering, and cycle detection, in one pass.",
            """
int[] indeg = new int[n];
for (int u = 0; u < n; u++) for (int v : g.get(u)) indeg[v]++;

Deque<Integer> q = new ArrayDeque<>();
for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);

int placed = 0;
while (!q.isEmpty()) {
    int u = q.poll(); placed++;
    for (int v : g.get(u)) if (--indeg[v] == 0) q.add(v);
}
return placed == n;                 // false ⇒ a cycle exists
""",
            "Everything hangs on the edge direction: prerequisite → dependent."),
        _sk("Three-colour cycle detection",
            "Directed cycles, when no ordering is wanted.",
            """
int[] state = new int[n];           // 0 new, 1 in progress, 2 done

boolean cycle(int u) {
    if (state[u] == 1) return true;
    if (state[u] == 2) return false;
    state[u] = 1;
    for (int v : g.get(u)) if (cycle(v)) return true;
    state[u] = 2;
    return false;
}
""",
            "Two states would report a false cycle on any diamond-shaped graph."),
        _sk("Build the graph from ordered words",
            "Alien dictionary and similar inference problems.",
            """
for (int i = 0; i + 1 < words.length; i++) {
    String a = words[i], b = words[i + 1];
    int len = Math.min(a.length(), b.length()), k = 0;
    while (k < len && a.charAt(k) == b.charAt(k)) k++;
    if (k < len) addEdge(a.charAt(k), b.charAt(k));       // exactly one edge
    else if (a.length() > b.length()) return "";          // invalid: prefix after longer
}
""",
            "Only the FIRST differing character yields information."),
    ],
    costs=[
        _cost("Kahn's algorithm", "O(V + E)", "O(V)", "One pass over nodes and edges."),
        _cost("Kahn's with a priority queue", "O(V log V + E)", "O(V)", "For lexicographic order."),
        _cost("Three-colour DFS", "O(V + E)", "O(V)", "Plus recursion depth."),
        _cost("Building in-degrees", "O(V + E)", "O(V)", "One pass over the adjacency lists."),
    ],
    pitfalls=[
        _pit("A valid schedule is reported as impossible (or vice versa)",
             "The edges were added in the wrong direction.",
             "“A before B” is the edge A → B, and increments B's in-degree. Write one "
             "example out before coding."),
        _pit("A cycle is missed",
             "The `order.size() == n` check was omitted after Kahn's.",
             "Kahn's silently produces a partial order when a cycle exists — the size check "
             "*is* the detection."),
        _pit("A false cycle is reported by DFS",
             "Only two states were used, so a node reached twice by different paths looked "
             "like a back edge.",
             "Use three states; only *in progress* indicates a cycle."),
        _pit("Undirected cycle detection reports a cycle on every edge",
             "Walking back to the parent was counted as revisiting.",
             "Skip the parent, or use union-find."),
        _pit("Isolated nodes are dropped from the order",
             "Only nodes appearing in edges were initialised.",
             "Initialise every node from 0 to n−1, including those with no edges."),
        _pit("The alien-alphabet answer is wrong for prefixes",
             "`[\"abc\", \"ab\"]` is invalid input but was silently accepted.",
             "If one word is a prefix of the previous and shorter, there is no valid order."),
    ],
    lessons=["topo", "indegree", "graph_cycle"],
    checks=[
        _chk("How does Kahn's algorithm detect a cycle for free?",
             "Nodes inside a cycle never reach in-degree 0, so they are never enqueued. If "
             "fewer than n nodes come out, the remainder form a cycle."),
        _chk("If B requires A, which way does the edge point?",
             "A → B. A is the prerequisite, so completing A decrements B's in-degree."),
        _chk("Why does DFS cycle detection need three states rather than two?",
             "A finished node may legitimately be reached again through another path. Only a "
             "node still on the current recursion path — *in progress* — indicates a cycle."),
        _chk("When does a topological order fail to be unique?",
             "Whenever more than one node has in-degree 0 at the same time. A priority queue "
             "then selects the lexicographically smallest valid order."),
    ],
    interview="""
Course-schedule questions are the most common graph problem in interviews, and
they are graded on the modelling sentence, not the algorithm: *"nodes are
courses, an edge from prerequisite to dependent, and the question is whether a
topological order covering all nodes exists"*. Say that, write Kahn's, then note
that the size check is the cycle detection. That is a complete answer in three
minutes.
""",
    rungs=[
        _rung("Warm up", "Kahn on six nodes, asking only whether it finished.",
              ["detect-cycle-tiny-dag"],
              {"detect-cycle-tiny-dag": "The sort and the cycle check are one algorithm. Be able to say *why* the leftovers must contain a cycle — it is the standard follow-up."}),
        _rung("Core", "Build the graph, count in-degrees, drain the queue.",
              ["course-schedule", "course-schedule-possible", "detect-cycle-directed"],
              {"course-schedule": "Write one example's edge directions down on paper before coding. That is where the bug lives.",
               "detect-cycle-directed": "Do it both ways — Kahn's size check and three-colour DFS — and note that they are the same fact."}),
        _rung("Stretch", "Infer the graph before you can sort it.",
              ["alien-dictionary-order"],
              {"alien-dictionary-order": "Only the first differing character of each adjacent pair is evidence. Handle the invalid-prefix case explicitly."}),
    ],
    next_up="""
Direction answers “in what order”. The next unit answers “what is joined to
what” — and does it faster than any traversal.
""",
)


# --- Unit 28 — Union-find ----------------------------------------------------

_unit(
    "union-find", "Union-Find (Disjoint Set Union)", "🧵", _S6,
    "Connectivity as a near-constant-time operation.",
    weight=2,
    prereqs=["graph-traversal"],
    why="""
"Are these two nodes connected?" can be answered by a traversal — O(V + E) per
query, which is hopeless when the edges arrive one at a time and the question is
asked after each. Union-find answers it in effectively constant time, and it
handles edges being *added* (never removed) perfectly.

That fits an entire family of problems: counting components as edges appear,
detecting the edge that creates a cycle, grouping equivalent things, and
Kruskal's minimum spanning tree. Once you recognise "connectivity, incremental"
the implementation is fifteen lines you should know by heart.
""",
    model="""
### The structure

Every element points at a parent. A root points at itself, and the root is the
name of the set.

```java
int[] parent = new int[n], size = new int[n];
for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }

int find(int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];   // path halving — flattens as it walks
        x = parent[x];
    }
    return x;
}

boolean union(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra == rb) return false;                  // already together ⇒ this edge closes a cycle
    if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
    parent[rb] = ra;                             // smaller tree under larger
    size[ra] += size[rb];
    return true;
}
```

### The two optimisations are not optional

- **Path compression** — point nodes directly at the root as you find them.
- **Union by size (or rank)** — always hang the smaller tree under the larger.

Without both, a sequence of unions can build a chain and every `find` becomes
O(n). With both, the amortised cost is O(α(n)), where α is the inverse Ackermann
function and is below 5 for any n you will ever see — effectively constant.

### `union` returning a boolean is the whole trick

If `union(a, b)` returns false, the two were **already connected**, so this edge
closes a cycle. That single return value answers:

- *Is this edge redundant?* → false means yes.
- *Does the graph have a cycle?* → any false during construction.
- *Is it a valid tree?* → n − 1 edges and no false.
- *How many components?* → start at n and decrement on every true.

### Kruskal's MST

Sort the edges by weight and add each one whose `union` returns true. Because
edges arrive cheapest-first, every accepted edge is safe (the next unit,
*Minimum Spanning Trees*, proves why and compares it with Prim):

```java
Arrays.sort(edges, (x, y) -> Integer.compare(x[2], y[2]));
long total = 0; int used = 0;
for (int[] e : edges)
    if (union(e[0], e[1])) { total += e[2]; if (++used == n - 1) break; }
```

### What it cannot do

Union-find only ever **merges**. There is no efficient `split`, and it cannot
answer questions about *paths* — only about membership. If you need the distance
between two nodes, or the edges of the path, traverse.

Direction is also invisible to it: union-find models undirected connectivity. A
directed graph's cycles need the previous unit.
""",
    signals=[
        _sig("“connected components” with edges given as a list", "Union-find",
             "Start at n components and decrement on each successful union."),
        _sig("“which edge creates a cycle?”", "The first `union` that returns false",
             "Already-connected means this edge is redundant."),
        _sig("“is it a valid tree?”", "n − 1 edges and no failed union",
             "Both conditions are needed: acyclic *and* connected."),
        _sig("“minimum cost to connect everything”", "Kruskal: sort edges, union greedily",
             "Union-find is what makes the greedy safe."),
        _sig("“group equivalent items”, “accounts merge”", "Union-find over the identifiers",
             "Equivalence classes are exactly disjoint sets."),
        _sig("“earliest time everyone is connected”", "Union in timestamp order",
             "Stop when the component count reaches 1."),
    ],
    skeletons=[
        _sk("The whole structure",
            "Memorise this; it is short and it never changes.",
            """
int[] parent, size;
int components;

void init(int n) {
    parent = new int[n]; size = new int[n]; components = n;
    for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
}

int find(int x) {
    while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
    return x;
}

boolean union(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra == rb) return false;
    if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
    parent[rb] = ra; size[ra] += size[rb]; components--;
    return true;
}
""",
            "Both optimisations included. Neither is optional."),
        _sk("Kruskal's MST",
            "Minimum spanning tree, minimum connection cost.",
            """
Arrays.sort(edges, (x, y) -> Integer.compare(x[2], y[2]));
long total = 0; int used = 0;
for (int[] e : edges) {
    if (union(e[0], e[1])) {
        total += e[2];
        if (++used == n - 1) break;         // a spanning tree is complete
    }
}
""",
            "Sorting dominates: O(E log E)."),
        _sk("Grid cells as union-find elements",
            "Islands, percolation, regions given as a grid.",
            """
int id(int i, int j) { return i * cols + j; }     // flatten 2-D to 1-D
// then union(id(i, j), id(ni, nj)) for each adjacent pair
""",
            "Flattening the coordinates is the only adaptation needed."),
    ],
    costs=[
        _cost("find / union (both optimisations)", "O(α(n)) ≈ O(1)", "O(n)", "α < 5 for any real n."),
        _cost("find without path compression", "O(n) worst case", "O(n)", "The chain case."),
        _cost("Kruskal's MST", "O(E log E)", "O(V)", "The sort dominates."),
        _cost("m operations on n elements", "O(m · α(n))", "O(n)", "Effectively linear."),
        _cost("Equivalent BFS per query", "O(V + E) each", "O(V)", "What union-find replaces."),
    ],
    pitfalls=[
        _pit("Every operation degrades to O(n)",
             "Path compression or union-by-size was skipped, so the structure became a chain.",
             "Include both; they are four lines and they are the algorithm."),
        _pit("The component count is wrong",
             "It was decremented on every union call rather than only on successful ones.",
             "Decrement inside the `if`, using the boolean return."),
        _pit("A cycle is missed",
             "`union` was called without inspecting its return value.",
             "`if (!union(a, b)) { /* this edge closes a cycle */ }`"),
        _pit("A graph is called a tree when it is a forest",
             "Only the edge count was checked, not connectivity.",
             "A tree needs exactly n − 1 edges *and* a single component."),
        _pit("Union-find used on a directed graph",
             "It models undirected connectivity only and ignores direction entirely.",
             "Use topological sort or three-colour DFS for directed cycles."),
        _pit("A recursive `find` overflows the stack",
             "Deep chains before compression takes effect.",
             "Write `find` iteratively, as above."),
    ],
    lessons=["union_find", "mst", "graph_cycle"],
    checks=[
        _chk("What do path compression and union by size each contribute?",
             "Compression flattens the tree while searching; union by size stops tall trees "
             "forming. Together they give O(α(n)) amortised — without both, O(n) is possible."),
        _chk("What does `union(a, b)` returning false tell you?",
             "The two were already in the same set, so this edge is redundant and closes a "
             "cycle. It is simultaneously the cycle test, the redundancy test and the "
             "component counter."),
        _chk("How do you check whether an edge list forms a valid tree?",
             "Exactly n − 1 edges, and every union succeeds (so no cycle) — which together "
             "imply a single connected component."),
        _chk("Why does Kruskal's algorithm work?",
             "Edges are considered cheapest first, so the first edge joining two components "
             "is the cheapest possible connection between them and is always safe to take."),
        _chk("When is union-find the wrong tool?",
             "When sets must be split, when direction matters, or when the question is about "
             "the path between nodes rather than mere membership."),
    ],
    interview="""
Union-find is a strong signal precisely because it is not the obvious answer.
When edges arrive incrementally and the question is connectivity, naming DSU
and quoting "effectively constant, α(n) amortised" reads as fluency. Be ready
for the comparison: a traversal answers the same question in O(V + E) *per
query*, which is why DSU wins as soon as there is more than one query.
""",
    traces=[
        _trace(
            "Union by size on 6 nodes: (0,1), (2,3), (1,3), (4,5)",
            "`parent[i] == i` means i is a root. No path compression yet — `find` is a "
            "plain walk, so the depth column is exactly what each later `find` will cost.",
            ["Union", "find(u), find(v)", "size[a], size[b]", "Smaller hangs under larger",
             "parent[] after", "Sets"],
            [
                ["(0, 1)", "0, 1", "1, 1", "tie → 1 under 0; size[0] = 2",
                 "[0, **0**, 2, 3, 4, 5]", "5"],
                ["(2, 3)", "2, 3", "1, 1", "tie → 3 under 2; size[2] = 2",
                 "[0, 0, 2, **2**, 4, 5]", "4"],
                ["(1, 3)", "**0**, **2**", "2, 2", "tie → 2 under 0; size[0] = 4",
                 "[0, 0, **0**, 2, 4, 5]", "3"],
                ["(4, 5)", "4, 5", "1, 1", "tie → 5 under 4; size[4] = 2",
                 "[0, 0, 0, 2, 4, **4**]", "2"],
            ],
            "Union (1,3) is the interesting one: neither 1 nor 3 is a root, so the work is "
            "on their *roots*. The count starts at n and drops by one per union that "
            "actually merged — never recomputed by a traversal. Node 3 now sits two hops "
            "from its root, which is the most this forest ever gets: union by size alone "
            "caps depth at O(log n), with no compression anywhere.",
        ),
        _trace(
            "The same forest, then find(3) with and without compression",
            "Forest: `0 ← {1, 2}` and `2 ← {3}`. Path compression is not a different "
            "algorithm — it is the same walk, which then repoints everything it passed "
            "directly at the root. Watch the array flatten.",
            ["find(3)", "Nodes visited", "parent[] afterwards", "Next find(3) visits"],
            [
                ["no compression, 1st call", "3 → 2 → 0", "[0, 0, 0, **2**, 4, 4]", "3 nodes"],
                ["no compression, 2nd call", "3 → 2 → 0", "[0, 0, 0, **2**, 4, 4]", "3 nodes — forever"],
                ["with compression, 1st call", "3 → 2 → 0, then repoint 3", "[0, 0, 0, **0**, 4, 4]", "2 nodes"],
                ["with compression, 2nd call", "3 → 0", "[0, 0, 0, 0, 4, 4]", "2 nodes"],
            ],
            "The flattening is a value in an array changing — `parent[3]` going from 2 to "
            "0 — not a claim in a comment. Compression charges the first `find` for a walk "
            "it was doing anyway and makes every later one on that path shorter, which is "
            "why the bound is *amortised* α(n) rather than per-operation constant.",
        ),
    ],
    build_it="""
### Write it from scratch, in about thirty lines

Do not skip this one. Union-Find is the smallest structure in the curriculum
whose costs are genuinely surprising, and typing it is the only thing that
turns "near-constant amortised" from a phrase into a fact you own.

```java
class DSU {
    private final int[] parent;
    private final int[] size;
    private int components;

    DSU(int n) {
        parent = new int[n];
        size = new int[n];
        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }
        components = n;
    }

    int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];   // path halving
            x = parent[x];
        }
        return x;
    }

    boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;          // already together
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;
        size[ra] += size[rb];
        components--;
        return true;
    }

    boolean connected(int a, int b) { return find(a) == find(b); }
    int components() { return components; }
    int sizeOf(int x) { return size[find(x)]; }
}
```

### Four things to notice while typing it

1. **`union` returns a boolean.** `false` means the two were already joined, and
   several problems in this unit *are* that return value —
   `redundant-connection` is literally the first edge whose union returns false.
   A `void union` throws the answer away.
2. **`size` is only meaningful at a root.** `sizeOf` therefore calls `find`
   first. Reading `size[x]` for a non-root x is the bug that makes
   `largest-component-size` wrong on exactly the inputs where it matters.
3. **Path halving, not full compression.** `parent[x] = parent[parent[x]]`
   flattens the path as it walks, in one pass and with no recursion. Full
   compression needs either a second pass or a recursive `find` — and the
   asymptotics are the same. Write the loop.
4. **`components` is maintained, never computed.** Start at n, decrement inside
   the successful branch of `union`. Any code that counts distinct roots with a
   loop over all n nodes has turned an O(1) query into an O(n) one.

### Then break it deliberately

- Delete the size comparison and always link `rb` under `ra`. Then union
  `(0,1), (1,2), (2,3), …` in order and print the depth of the deepest node:
  you have built a linked list, and `find` is O(n).
- Delete the path halving but keep union by size. The depth stays O(log n) —
  which is the point of the warm-up problem, and the reason compression is an
  optimisation you can justify rather than a ritual you copy.
""",
    rungs=[
        _rung("Warm up", "Union by size alone, so path compression is an optimisation rather than an incantation.",
              ["union-by-size-components"],
              {"union-by-size-components": "Plain walk to the root, no compression. Union by size already caps the depth at O(log n) — knowing that is what lets you justify compression on the next rung."}),
        _rung("Core", "Counting components, and the boolean return.",
              ["count-components", "number-of-provinces", "graph-valid-tree",
               "redundant-connection", "detect-cycle-undirected"],
              {"count-components": "Start at n and decrement on each successful union. Nothing else is needed.",
               "redundant-connection": "The answer is literally the first edge whose union returns false.",
               "graph-valid-tree": "Two conditions, not one: n − 1 edges and no failed union."}),
        _rung("Variations", "A layering that is genuinely a new idea.",
              ["satisfy-equations"],
              {"satisfy-equations": "Union all the equalities first, then check every inequality. Order matters."}),
        _extra("Extra practice", "Sizes and orderings layered on the same union — reps, not new ideas.",
               ["largest-component-size", "make-network-connected", "earliest-full-connect"],
               {"earliest-full-connect": "Union in timestamp order and stop the moment the component count hits 1. A nice problem; not one that stands between you and shortest paths."}),
    ],
    next_up="""
A failed `union` rejects an edge that would close a cycle. Feed the edges in
order of weight and that one rule builds the cheapest network connecting
everything — the next unit.
""",
)


# --- Unit 29 — Minimum spanning trees ----------------------------------------

_unit(
    "mst", "Minimum Spanning Trees", "🌉", _S6,
    "Connect everything as cheaply as possible — and know why the cheap edge is safe.",
    weight=1,
    prereqs=["union-find", "heaps"],
    why="""
*"Connect every city with the least total road"*, *"wire every building"*,
*"cheapest network that reaches every node"* — a minimum spanning tree is the
answer, and two short algorithms find it: Kruskal, which you have already half
written in the union-find unit, and Prim, which is Dijkstra with a different
number in the heap.

What deserves a unit is not the code but the **reason it works**. Both are
greedy, and greedy is only safe with a proof. The proof here — the cut property —
is one sentence, it answers every "why is this edge allowed?" question, and it
tells you which of the two algorithms to use on a given graph.
""",
    model="""
### What a spanning tree is

A connected, undirected graph with V vertices has many spanning trees: subsets of
exactly V − 1 edges that connect everything with no cycle. A **minimum** spanning
tree is one with the smallest total weight. It exists only if the graph is
connected; otherwise you get a minimum spanning *forest*.

### The cut property — why greedy is safe

Split the vertices into any two groups. Among the edges crossing between them,
the cheapest one belongs to some minimum spanning tree.

Why: take an MST that does not use that edge e. Adding e creates a cycle, and
that cycle must cross the split a second time, through some edge f that is no
cheaper than e. Swap f for e: still a spanning tree, no heavier. So some MST
contains e. This is the exchange argument from the greedy unit, with a graph in it.

### Kruskal: cheapest edge that joins two groups

Sort all edges by weight. Take each one whose endpoints are in *different*
components, merging them; skip the ones that would close a cycle. The union-find
`union` returning false is exactly "would close a cycle".

```java
Arrays.sort(edges, Comparator.comparingInt(e -> e[2]));
long total = 0; int used = 0;
for (int[] e : edges)
    if (dsu.union(e[0], e[1])) { total += e[2]; if (++used == n - 1) break; }
return used == n - 1 ? total : -1;        // -1: the graph was not connected
```

Each accepted edge is the cheapest one crossing the cut between its two
components, so the cut property says it is safe.

### Prim: grow one tree

Start from any vertex. Repeatedly add the cheapest edge leaving the tree. The cut
is \"tree versus everything else\", so every edge Prim adds is safe for the same
reason.

With a heap (sparse graphs) it is Dijkstra's loop with the edge weight in place
of the path length:

```java
pq.add(new int[]{0, start});                         // {weight to join, vertex}
while (!pq.isEmpty()) {
    int[] top = pq.poll();
    int w = top[0], u = top[1];
    if (inTree[u]) continue;                         // stale entry — skip it
    inTree[u] = true; total += w;
    for (int[] e : adj.get(u))
        if (!inTree[e[0]]) pq.add(new int[]{e[1], e[0]});
}
```

With a plain array (dense graphs, every pair an edge) keep `best[v]` — the
cheapest edge from v to the tree — scan for the minimum and update from the new
vertex's row. That is O(V²) with no heap at all.

### Which one

| Graph | Use | Cost |
| --- | --- | --- |
| Edge list, sparse | Kruskal | O(E log E) |
| Adjacency lists, sparse | Prim with a heap | O(E log V) |
| Complete or dense (E ≈ V²) | Prim with an array | O(V²) |

On a complete graph of points, Kruskal sorts V²/2 edges — O(V² log V) — while
array Prim is O(V²), which is as fast as reading the edges at all.

### Questions about edges, not just the total

*Is this edge in every MST? In some?* Change the input and re-run: an edge is
**critical** if the best tree without it is heavier; **pseudo-critical** if
forcing it in still achieves the minimum. Two Kruskal passes per edge, over a
list sorted once.
""",
    signals=[
        _sig("“connect all …, minimum total cost”", "Minimum spanning tree",
             "Not shortest paths: MST minimises the sum of all chosen edges, not a route."),
        _sig("An edge list", "Kruskal with union-find",
             "Sort once; `union` returning false is the cycle check."),
        _sig("Points in the plane, every pair allowed", "Prim with an array, O(V²)",
             "The graph is complete — do not generate and sort V²/2 edges."),
        _sig("“is this edge necessary / usable?”", "Exclude it, force it, compare the weight",
             "Critical: excluding raises the weight. Pseudo-critical: forcing keeps it."),
        _sig("Some connections are already built (cost 0)", "Union them first, then Kruskal",
             "Pre-merged components are just a head start for the same loop."),
        _sig("“shortest route from A to B”", "Not an MST — Dijkstra",
             "The MST path between two vertices is not the shortest path between them."),
    ],
    skeletons=[
        _sk("Kruskal",
            "Edge lists; the default MST.",
            """
long kruskal(int n, int[][] edges) {             // edges: {u, v, w}
    Arrays.sort(edges, Comparator.comparingInt(e -> e[2]));
    DSU dsu = new DSU(n);
    long total = 0;
    int used = 0;
    for (int[] e : edges) {
        if (dsu.union(e[0], e[1])) {
            total += e[2];
            if (++used == n - 1) break;
        }
    }
    return used == n - 1 ? total : -1;           // -1: disconnected
}
""",
            "The DSU from the union-find unit, unchanged. `long` total: V − 1 weights can overflow `int`."),
        _sk("Prim with a heap",
            "Adjacency lists, sparse graphs.",
            """
long prim(List<List<int[]>> adj, int n) {        // adj.get(u): {v, w}
    boolean[] in = new boolean[n];
    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(x -> x[0]));
    pq.add(new int[]{0, 0});
    long total = 0;
    int added = 0;
    while (!pq.isEmpty() && added < n) {
        int[] top = pq.poll();
        int u = top[1];
        if (in[u]) continue;                     // lazy deletion
        in[u] = true;
        total += top[0];
        added++;
        for (int[] e : adj.get(u)) if (!in[e[0]]) pq.add(new int[]{e[1], e[0]});
    }
    return added == n ? total : -1;
}
""",
            "Dijkstra's loop with `w` where Dijkstra has `dist[u] + w`."),
        _sk("Prim with an array",
            "Complete or dense graphs: O(V²), no heap.",
            """
long primDense(long[][] cost, int n) {
    long[] best = new long[n];
    boolean[] in = new boolean[n];
    Arrays.fill(best, Long.MAX_VALUE);
    best[0] = 0;
    long total = 0;
    for (int round = 0; round < n; round++) {
        int u = -1;
        for (int v = 0; v < n; v++)
            if (!in[v] && (u == -1 || best[v] < best[u])) u = v;
        in[u] = true;
        total += best[u];
        for (int v = 0; v < n; v++)
            if (!in[v] && cost[u][v] < best[v]) best[v] = cost[u][v];
    }
    return total;
}
""",
            "Compute `cost[u][v]` on the fly for points instead of storing the matrix."),
    ],
    traces=[
        _trace(
            "Kruskal on 5 vertices",
            "Edges sorted by weight: 0–2 (1), 1–2 (2), 3–4 (3), 0–1 (4), 1–3 (5), 2–3 (8), "
            "2–4 (9). Each row is one edge considered; the groups are the union-find "
            "components after it.",
            ["Edge", "Weight", "Endpoints already joined?", "Action", "Groups after", "Total"],
            [
                ["0–2", "1", "no", "take", "{0,2} {1} {3} {4}", "1"],
                ["1–2", "2", "no", "take", "{0,1,2} {3} {4}", "3"],
                ["3–4", "3", "no", "take", "{0,1,2} {3,4}", "6"],
                ["0–1", "4", "**yes** — both in {0,1,2}", "skip (would close 0–1–2)", "{0,1,2} {3,4}", "6"],
                ["1–3", "5", "no", "take — 4 edges = V − 1, stop", "{0,1,2,3,4}", "**11**"],
            ],
            "Edge 0–1 is cheaper than 1–3 and still rejected: it only connects vertices that "
            "are already connected. The 8 and 9 edges are never looked at, because the tree "
            "was complete after V − 1 acceptances.",
        ),
        _trace(
            "Prim from vertex 0, same graph",
            "`best[v]` is the cheapest edge from v into the tree so far (∞ if none). Each round "
            "adds the cheapest outside vertex, then lowers its neighbours' `best`.",
            ["Round", "Added (via weight)", "best[1]", "best[2]", "best[3]", "best[4]", "Total"],
            [
                ["start", "0 (0)", "4", "1", "∞", "∞", "0"],
                ["1", "2 (1)", "**2**", "—", "**8**", "**9**", "1"],
                ["2", "1 (2)", "—", "—", "**5**", "9", "3"],
                ["3", "3 (5)", "—", "—", "—", "**3**", "8"],
                ["4", "4 (3)", "—", "—", "—", "—", "**11**"],
            ],
            "Same total, different order: Prim adds the weight-5 edge before the weight-3 one, "
            "because 3–4 does not touch the tree until vertex 3 is in it. Kruskal thinks in "
            "global edge order, Prim in \"cheapest way out of the tree I have\" — and the cut "
            "property makes both correct.",
        ),
    ],
    costs=[
        _cost("Kruskal", "O(E log E)", "O(V + E)", "The sort dominates; the unions are ≈ O(E)."),
        _cost("Prim, binary heap", "O(E log V)", "O(V + E)", "Lazy deletion: up to E heap entries."),
        _cost("Prim, array", "O(V²)", "O(V)", "Best for complete graphs."),
        _cost("Kruskal on n points, all pairs", "O(n² log n)", "O(n²)", "Why array Prim wins there."),
        _cost("Critical / pseudo-critical edges", "O(E² · α(V))", "O(V + E)", "Two Kruskal passes per edge, sorted once."),
    ],
    pitfalls=[
        _pit("The MST weight is too small",
             "The graph is disconnected, and the loop added fewer than V − 1 edges without noticing.",
             "Count accepted edges; fewer than V − 1 means no spanning tree exists."),
        _pit("Prim adds a vertex twice",
             "A stale heap entry for an already-added vertex was not skipped.",
             "`if (inTree[u]) continue;` straight after polling."),
        _pit("Minimum spanning tree used for a shortest path",
             "The path between two vertices inside an MST is not the shortest path between them.",
             "MST minimises total edge weight; for A-to-B distance use Dijkstra."),
        _pit("Time limit on a complete graph of points",
             "All V²/2 edges were generated and sorted for Kruskal.",
             "Array Prim, computing each distance when it is needed: O(V²)."),
        _pit("The total overflows",
             "V − 1 weights summed in an `int`.",
             "Accumulate in `long`."),
        _pit("An edge that is in every MST is reported as merely usable",
             "The \"forced\" test ran before the \"excluded\" test, and a critical edge passes both.",
             "Test critical (exclude it) first; only a non-critical edge can be pseudo-critical."),
    ],
    lessons=["mst", "union_find", "greedy", "heap"],
    checks=[
        _chk("State the cut property, and explain why it makes Kruskal and Prim correct.",
             "For any split of the vertices, the cheapest edge crossing it is in some MST. "
             "Kruskal's accepted edge is the cheapest crossing the cut between its two "
             "components; Prim's is the cheapest crossing tree-versus-rest."),
        _chk("Kruskal or Prim for 2,000 points where every pair can be connected?",
             "Array Prim: O(V²) ≈ 4·10⁶. Kruskal would sort ~2·10⁶ edges for O(V² log V), and "
             "has to store them all."),
        _chk("How is heap-based Prim different from Dijkstra?",
             "Only in the key pushed: Prim pushes the edge weight w, Dijkstra pushes "
             "dist[u] + w. Same loop, same stale-entry skip."),
        _chk("How do you tell that a graph has no spanning tree?",
             "Kruskal accepts fewer than V − 1 edges, or Prim adds fewer than V vertices."),
        _chk("How do you decide whether an edge is in every MST?",
             "Run Kruskal without it. If the weight rises (or the graph disconnects), every MST "
             "needs it."),
    ],
    bigo=[
        _bigo(r"""
Arrays.sort(edges, Comparator.comparingInt(e -> e[2]));   // E edges, V vertices
for (int[] e : edges)
    if (dsu.union(e[0], e[1])) total += e[2];            // path compression + union by size
""", "O(E log E)", ["O(E log E)", "O(E · V)", "O(E · α(V))", "O(V²)"],
            "The unions are nearly free — O(E · α(V)) together — so the sort dominates. "
            "O(E log E) and O(E log V) are the same class, since E ≤ V²."),
        _bigo(r"""
for (int round = 0; round < n; round++) {        // n vertices, complete graph
    int u = argminOutside(best, in);             // scans all n
    in[u] = true;
    for (int v = 0; v < n; v++) best[v] = Math.min(best[v], dist(u, v));
}
""", "O(n²)", ["O(n²)", "O(n² log n)", "O(n³)", "O(n log n)"],
            "n rounds, each two O(n) scans. No heap and no sort: for a complete graph this is "
            "optimal, since there are n²/2 edges to consider at all."),
        _bigo(r"""
List<int[]> edges = new ArrayList<>();           // n points
for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++)
        edges.add(new int[]{i, j, manhattan(i, j)});
edges.sort(Comparator.comparingInt(e -> e[2]));
""", "O(n² log n)", ["O(n² log n)", "O(n²)", "O(n log n)", "O(n³)"],
            "n²/2 edges, sorted: O(n² log n²) = O(n² log n) time, plus O(n²) memory. Array "
            "Prim avoids both."),
        _bigo(r"""
// edges pre-sorted once; kruskal(skip, force) is one pass with a fresh DSU
for (int e = 0; e < m; e++) {
    if (kruskal(e, -1) > base) critical.add(e);
    else if (kruskal(-1, e) == base) pseudo.add(e);
}
""", "O(m² · α(n))", ["O(m² · α(n))", "O(m log m)", "O(m² log m)", "O(n · m)"],
            "Up to two linear Kruskal passes per edge. Sorting inside `kruskal` would make it "
            "O(m² log m) — sort once, outside the loop."),
        _bigo(r"""
PriorityQueue<int[]> pq = ...;                   // lazy Prim: V vertices, E edges
while (!pq.isEmpty()) {
    int[] top = pq.poll();
    if (in[top[1]]) continue;
    in[top[1]] = true;
    for (int[] e : adj.get(top[1])) if (!in[e[0]]) pq.add(new int[]{e[1], e[0]});
}
""", "O(E log V)", ["O(E log V)", "O(V log V)", "O(V · E)", "O(E + V)"],
            "Every edge can be pushed once from each end, so the heap sees O(E) operations of "
            "O(log E) = O(log V) each. Stale entries cost a poll, not a wrong answer."),
    ],
    interview="""
Name the problem before the algorithm: "this is a minimum spanning tree, not a
shortest path — we pay for every edge we build, not for one route". Then pick by
density out loud: Kruskal for an edge list, array Prim when every pair is an
edge. The follow-up is almost always "why is the greedy choice safe?", and the
cut property is the one-sentence answer.
""",
    rungs=[
        _rung("Core", "Kruskal and Prim, each where it fits best.",
              ["mst-total-weight", "prim-dense-graph"],
              {"mst-total-weight": "Kruskal with the DSU from the last unit. Count accepted edges: fewer than n − 1 means no tree.",
               "prim-dense-graph": "Every pair is an edge, so skip the heap: an array of best costs, an O(n) scan and an O(n) update per round."}),
        _rung("Stretch", "An implicit graph, and questions about individual edges.",
              ["min-cost-connect-points", "mst-critical-edges"],
              {"min-cost-connect-points": "The graph is complete and implicit. Kruskal works; array Prim is O(n²) and never builds the edge list — try both.",
               "mst-critical-edges": "Sort once, then exclude each edge and force each edge. Test critical before pseudo-critical."}),
    ],
    next_up="""
Spanning trees pay for every edge. The last unit of the stage pays only for the
route from one vertex to another — and the weights decide which algorithm is
even correct.
""",
)


# --- Unit 30 — Shortest paths ------------------------------------------------

_unit(
    "shortest-paths", "Weighted Shortest Paths", "🛣️", _S6,
    "When edges cost different amounts, BFS stops working.",
    weight=2,
    prereqs=["graph-traversal", "heaps"],
    why="""
BFS finds shortest paths because every edge costs 1, so layer order is distance
order. Give the edges different weights and that collapses: a path of two cheap
edges can beat one expensive edge, and BFS will have committed to the wrong one.

The fix is to visit nodes in order of **distance** rather than hop count, which
means a priority queue instead of a plain queue. That is Dijkstra's algorithm —
BFS with the queue swapped — and it covers nearly every weighted-path problem
you will meet. The two exceptions, negative edges and a hop limit, are what
Bellman-Ford is for.
""",
    model="""
### Dijkstra: BFS with a priority queue

```java
long[] dist = new long[n];
Arrays.fill(dist, Long.MAX_VALUE);
dist[src] = 0;

PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
pq.add(new long[]{ 0, src });

while (!pq.isEmpty()) {
    long[] top = pq.poll();
    long d = top[0]; int u = (int) top[1];
    if (d > dist[u]) continue;              // stale entry — lazy deletion
    for (int[] e : g.get(u)) {              // e = { to, weight }
        long nd = d + e[1];
        if (nd < dist[e[0]]) {
            dist[e[0]] = nd;
            pq.add(new long[]{ nd, e[0] });
        }
    }
}
```

Three details carry the whole algorithm:

1. **The heap is ordered by distance, not by insertion.** That is the only
   change from BFS, and it is what makes the first arrival optimal.
2. **`if (d > dist[u]) continue;`** — instead of updating an entry's priority
   (which a binary heap cannot do cheaply), push a new one and ignore the stale
   copy when it surfaces. This is the lazy deletion from the heaps unit.
3. **Once a node is polled with its final distance, it is settled.** No later
   path can improve it — *provided all weights are non-negative*.

### Why non-negative weights are required

The settled-forever argument assumes extending a path can only make it longer.
A negative edge breaks that: a node already finalised could be improved by a
later, cheaper route. Dijkstra will not notice, and will return a wrong answer
with no warning.

### Bellman-Ford: relax everything, n − 1 times

```java
long[] dist = new long[n];
Arrays.fill(dist, INF); dist[src] = 0;

for (int round = 0; round < n - 1; round++)
    for (int[] e : edges)
        if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]])
            dist[e[1]] = dist[e[0]] + e[2];
```

O(V · E) and slower, but it handles negative edges — and one more round that
still improves something proves a negative cycle exists.

Its other use is the one that appears in interviews: **"at most k stops"**. Run
exactly k + 1 rounds, each relaxing from a *snapshot* of the previous round's
distances. The snapshot is essential — without it, one round can chain several
edges together and use more hops than allowed.

### Dijkstra variants

The algorithm does not care what "distance" means, only that combining is
monotone. Swap the relaxation rule and you get a different problem:

| Relax with | Answers |
| --- | --- |
| `d + w` | Shortest total distance |
| `max(d, w)` | Minimise the **largest** edge on the path (minimum effort) |
| `d × p` | Maximise a probability (with a max-heap) |

### Choosing

| Situation | Use |
| --- | --- |
| Unweighted | BFS — O(V + E), no heap needed |
| Weights 0 or 1 | 0-1 BFS with a deque |
| Non-negative weights | Dijkstra — O(E log V) |
| Negative edges | Bellman-Ford — O(V · E) |
| At most k edges | Bellman-Ford, k + 1 rounds, with a snapshot |
| All pairs, V small | Floyd–Warshall — O(V³) |
""",
    signals=[
        _sig("“shortest path”, weights all equal", "BFS",
             "No heap needed; do not over-engineer."),
        _sig("“minimum cost / time”, non-negative weights", "Dijkstra",
             "The priority queue is the only change from BFS."),
        _sig("“at most k stops / moves”", "Bellman-Ford, k + 1 rounds",
             "Relax from a snapshot so one round adds one hop."),
        _sig("Negative weights anywhere", "Bellman-Ford",
             "Dijkstra is silently wrong with negative edges."),
        _sig("“minimise the maximum edge”", "Dijkstra with `max` relaxation",
             "The path cost is the worst step, not the sum."),
        _sig("“shortest path between every pair”, V ≤ 400", "Floyd–Warshall",
             "O(V³) and ten lines."),
    ],
    skeletons=[
        _sk("Dijkstra",
            "The default weighted shortest path.",
            """
long[] dist = new long[n];
Arrays.fill(dist, Long.MAX_VALUE);
dist[src] = 0;
PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
pq.add(new long[]{ 0, src });

while (!pq.isEmpty()) {
    long[] cur = pq.poll();
    int u = (int) cur[1];
    if (cur[0] > dist[u]) continue;                 // stale
    for (int[] e : g.get(u)) {
        long nd = cur[0] + e[1];
        if (nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{ nd, e[0] }); }
    }
}
""",
            "The stale check replaces decrease-key, which a binary heap cannot do cheaply."),
        _sk("Dijkstra on a grid with a different cost rule",
            "Minimum effort: the path's cost is its worst step.",
            """
long nd = Math.max(cur[0], Math.abs(h[ni][nj] - h[i][j]));
if (nd < dist[ni][nj]) { dist[ni][nj] = nd; pq.add(new long[]{ nd, ni, nj }); }
""",
            "Only the relaxation changes; the rest of the algorithm is untouched."),
        _sk("Bellman-Ford with a hop limit",
            "“At most k stops”.",
            """
long[] dist = new long[n];
Arrays.fill(dist, INF); dist[src] = 0;

for (int round = 0; round <= k; round++) {
    long[] prev = dist.clone();                      // ← the snapshot
    for (int[] e : flights)
        if (prev[e[0]] != INF)
            dist[e[1]] = Math.min(dist[e[1]], prev[e[0]] + e[2]);
}
""",
            "Without the clone, one round can chain several flights and exceed k."),
        _sk("Floyd–Warshall",
            "All-pairs shortest paths for small V.",
            """
for (int k = 0; k < n; k++)
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
""",
            "The `k` loop must be outermost — it is the set of allowed intermediates."),
    ],
    costs=[
        _cost("BFS (unweighted)", "O(V + E)", "O(V)", "Nothing beats it when it applies."),
        _cost("Dijkstra with a binary heap", "O(E log V)", "O(V + E)", "The standard choice."),
        _cost("Bellman-Ford", "O(V · E)", "O(V)", "Handles negatives; also hop limits."),
        _cost("Floyd–Warshall", "O(V³)", "O(V²)", "All pairs; V ≤ ~400."),
        _cost("0-1 BFS", "O(V + E)", "O(V)", "Deque: push front for 0, back for 1."),
    ],
    pitfalls=[
        _pit("Dijkstra returns a wrong distance",
             "The graph has a negative edge, which breaks the settled-forever argument.",
             "Use Bellman-Ford when any weight can be negative."),
        _pit("Dijkstra is far slower than expected",
             "Stale heap entries are processed instead of skipped.",
             "`if (d > dist[u]) continue;` immediately after the poll."),
        _pit("The distances overflow",
             "`INF + weight` wrapped around to a negative number.",
             "Use `long`, and skip relaxation from nodes still at infinity."),
        _pit("“At most k stops” gives a path with more than k",
             "Relaxation read the array being written, chaining edges within one round.",
             "Relax from a cloned snapshot of the previous round."),
        _pit("Floyd–Warshall produces nonsense",
             "The `k` loop was not outermost.",
             "Order is k, then i, then j — k is the set of permitted intermediate nodes."),
        _pit("A heap is used where BFS would do",
             "All weights are 1, so the priority queue is pure overhead.",
             "Check the weights before reaching for Dijkstra."),
    ],
    lessons=["dijkstra", "bellman_ford", "bfs", "heap"],
    checks=[
        _chk("Why does BFS fail on a weighted graph?",
             "BFS visits in hop order, which only equals distance order when every edge "
             "costs the same. Two cheap edges can beat one expensive one."),
        _chk("What exactly does `if (d > dist[u]) continue;` do?",
             "It discards stale heap entries left behind by an improved distance — lazy "
             "deletion, used because a binary heap has no cheap decrease-key."),
        _chk("Why is Dijkstra invalid with negative edges?",
             "It relies on a node's distance being final once polled. A negative edge can "
             "improve an already-settled node, and Dijkstra never revisits it."),
        _chk("Why must the “at most k stops” variant relax from a snapshot?",
             "Otherwise updates made earlier in the same round are read later in it, "
             "chaining multiple edges into what should be a single-hop round."),
        _chk("How do you adapt Dijkstra to minimise the *largest* edge on a path?",
             "Replace the relaxation `d + w` with `max(d, w)`. The algorithm only requires "
             "that the combining function be monotone."),
    ],
    interview="""
Say which algorithm and *why the cheaper one does not apply*: "weights differ,
so BFS would not be correct — Dijkstra, O(E log V)". Then have the two follow-ups
ready, because they are always the same: negative edges (Bellman-Ford) and a hop
limit (Bellman-Ford with k + 1 rounds and a snapshot). Knowing that Dijkstra is
"BFS with a priority queue" is also the cleanest way to explain it under time
pressure.
""",
    traces=[
        _trace(
            "Dijkstra on 0→1 (4), 0→2 (1), 2→1 (2), 1→3 (1), 2→3 (5)",
            "The queue holds `(distance, node)` pairs, smallest first. The column that "
            "matters is the third one: an entry is **stale** when the distance it carries "
            "is worse than the best already known for that node, and skipping those is "
            "what keeps the loop correct without any ability to delete from the heap.",
            ["Pop", "d vs dist[u]", "Verdict", "Relaxations", "Queue after (d, node)"],
            [
                ["(0, 0)", "0 = dist[0]", "settle 0", "dist[1] = 4, dist[2] = 1",
                 "(1,2), (4,1)"],
                ["(1, 2)", "1 = dist[2]", "settle 2", "1 → 1+2 = **3** < 4; 3 → 1+5 = **6**",
                 "(3,1), (4,1), (6,3)"],
                ["(3, 1)", "3 = dist[1]", "settle 1", "3 → 3+1 = **4** < 6",
                 "(4,1), (4,3), (6,3)"],
                ["(4, 1)", "4 > dist[1] = 3", "**STALE — skip**", "none", "(4,3), (6,3)"],
                ["(4, 3)", "4 = dist[3]", "settle 3", "no outgoing edges", "(6,3)"],
                ["(6, 3)", "6 > dist[3] = 4", "**STALE — skip**", "none", "(empty)"],
            ],
            "Six pops for four nodes: two of them were obsolete entries left behind when a "
            "shorter route was found later. Java's `PriorityQueue` has no decrease-key, so "
            "the standard move is to push a *second* entry and let the stale one be "
            "discarded on arrival — which is why the queue can hold O(E) entries rather "
            "than O(V), and why the bound is O(E log E). Delete the staleness check and "
            "you re-settle node 1 with a worse distance and relax from it again; on a "
            "larger graph that is a wrong answer, not just wasted work.",
        ),
    ],
    rungs=[
        _rung("Warm up", "Dijkstra with the priority queue deleted.",
              ["grid-bfs-distance"],
              {"grid-bfs-distance": "All edges cost 1, so a FIFO queue already visits cells in non-decreasing distance order. Make one cell cost 5 and that invariant dies — the heap is what restores it."}),
        _rung("Core", "Dijkstra, and the two relaxation variants.",
              ["network-delay-time", "path-minimum-effort", "cheapest-flights-k-stops"],
              {"network-delay-time": "Plain Dijkstra: the answer is the maximum finalised distance, and unreachable means −1.",
               "path-minimum-effort": "Same algorithm, `max` relaxation. Worth doing to prove the template is not about addition.",
               "cheapest-flights-k-stops": "Bellman-Ford with k + 1 rounds. The snapshot clone is the entire problem."}),
        _rung("Stretch", "Build the graph and run it end to end.",
              ["dijkstra-shortest-path"],
              {"dijkstra-shortest-path": "The full implementation from an edge list, with the stale check and `long` distances."}),
    ],
    next_up="""
One core stage left. When no greedy choice is safe, the only affordable way to
consider every option is to never solve the same subproblem twice — dynamic
programming — and the stage ends by combining every structure so far in design.
""",
)
