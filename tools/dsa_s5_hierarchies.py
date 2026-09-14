# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 5 — Things that branch.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# Everything so far has been linear. This stage covers the structures where an
# element has SEVERAL successors, and the one idea that makes them tractable:
# recursion. It opens with recursion on its own, deliberately, because trees,
# backtracking and DFS are all the same skill and teaching them separately is
# why people can write a tree traversal but freeze on a permutation generator.
#
# Order within the stage is a dependency chain, not a difficulty ramp: trees
# are recursion with two successors; backtracking is recursion that undoes;
# graphs are trees with cycles, which is precisely why they need a visited set;
# and the four graph units after that are the four questions worth asking about
# a graph — can I reach it, in what order, is it connected, how far is it.
# ---------------------------------------------------------------------------

_S5 = _stage(
    "hierarchies", "Recursion, Trees & Graphs", "🌳",
    "One idea — solve a smaller version — applied to everything that branches.",
    """
This is the conceptual centre of the curriculum. Every unit in it is the same
sentence with a different noun:

> Solve the smaller version, then combine.

For a **tree** the smaller versions are the two subtrees. For **backtracking**
they are "the same problem with one more choice fixed". For a **graph** they are
the neighbours — plus a visited set, because a graph can loop back on itself and
a tree cannot.

If you find yourself memorising four traversals, stop: it is one traversal,
called on whatever the successors happen to be.
""")


# --- Unit 20 — Recursion ----------------------------------------------------

_unit(
    "recursion", "Recursion", "🌀", _S5,
    "Trust the smaller call. Everything in this stage depends on it.",
    prereqs=["design"],
    why="""
Recursion is not a technique for a family of problems; it is the *notation*
every remaining unit is written in. Tree traversal, backtracking, DFS, divide
and conquer and the top-down half of dynamic programming are all one pattern:
express the answer in terms of the same function on a smaller input.

The block people hit is almost never syntax. It is refusing to **trust the
recursive call** — trying to trace the whole stack in their head instead of
assuming the smaller call is already correct and asking only what to do with its
result.
""",
    model="""
### The contract

Write a recursive function by answering three questions, in this order:

1. **What does this function promise?** One sentence, for *any* valid input.
   "`depth(node)` returns the height of the subtree rooted at `node`." If you
   cannot write that sentence, no amount of tracing will help.
2. **Base case.** The smallest input, answered without recursion. It is almost
   always `null`, empty, or zero — and it is almost always where the bug is.
3. **Recursive case.** Assume the promise holds for smaller inputs. Call, and
   combine. Do not trace.

```java
static int depth(Node node) {
    if (node == null) return 0;                       // base
    return 1 + Math.max(depth(node.left), depth(node.right));   // combine
}
```

### The cost

Each call keeps a stack frame, so a recursion n deep costs O(n) **memory** even
if it allocates nothing. Java's default stack overflows around 10,000 frames —
which is why a recursive walk over a 10⁵-long linked list crashes and an
iterative one does not.

The time cost comes from the recurrence:

| Recurrence | Solves to | Example |
| --- | --- | --- |
| `T(n) = T(n−1) + O(1)` | O(n) | Walking a list |
| `T(n) = 2T(n−1) + O(1)` | O(2ⁿ) | Naive Fibonacci |
| `T(n) = T(n/2) + O(1)` | O(log n) | Binary search, fast power |
| `T(n) = 2T(n/2) + O(n)` | O(n log n) | Merge sort |

### Divide and conquer

Split into independent halves, solve both, combine. Fast exponentiation is the
cleanest example:

```java
static long power(long b, long e) {
    if (e == 0) return 1;
    long half = power(b, e / 2);      // ONE call, not two
    return (e % 2 == 0) ? half * half : half * half * b;
}
```

Calling `power(b, e/2)` twice instead of storing it turns O(log e) into O(e).
That single line is the difference, and it is the same insight as memoisation:
never compute the same thing twice.

### When recursion repeats itself

Naive Fibonacci is O(2ⁿ) because `fib(n−2)` is recomputed on both branches. Two
fixes, and the whole DP stage is built on them:

- **Memoise**: cache each answer by argument. Top-down DP.
- **Iterate**: compute the small answers first. Bottom-up DP.

Recognising the overlap is the skill. The DP unit later is this observation with
a syllabus attached.
""",
    signals=[
        _sig("“the same problem on a smaller input”", "Recursion",
             "Subtrees, suffixes, “with one more item chosen”."),
        _sig("A tree or nested structure", "Recursion over the children",
             "The structure is already recursive; mirror it."),
        _sig("“combine the halves”", "Divide and conquer",
             "Two independent halves, then a merge step."),
        _sig("Exponent or range halves each step", "O(log n) recursion",
             "Compute the half once and reuse it."),
        _sig("The same sub-input recurs on different branches", "Memoise",
             "Overlapping subproblems is the definition of DP."),
        _sig("Depth could reach 10⁵", "Convert to iteration",
             "The call stack, not the algorithm, is what will fail."),
    ],
    skeletons=[
        _sk("The three-part shape",
            "Every recursive function you will write in this stage.",
            """
static R solve(Input x) {
    if (isBase(x)) return baseAnswer(x);      // 1. smallest case
    R sub = solve(smaller(x));                // 2. trust the call
    return combine(x, sub);                   // 3. use the result
}
""",
            "Write the one-sentence promise above the function before the body."),
        _sk("Fast exponentiation",
            "Powers, matrix powers, repeated doubling.",
            """
static long power(long b, long e, long mod) {
    if (e == 0) return 1;
    long half = power(b, e / 2, mod);      // computed ONCE
    long sq = half * half % mod;
    return (e % 2 == 0) ? sq : sq * b % mod;
}
""",
            "Two recursive calls here would make it O(e) instead of O(log e)."),
        _sk("Memoised recursion",
            "Whenever the same argument recurs across branches.",
            """
long[] memo = new long[n + 1];
Arrays.fill(memo, -1);

static long fib(int n) {
    if (n < 2) return n;
    if (memo[n] != -1) return memo[n];
    return memo[n] = fib(n - 1) + fib(n - 2);
}
""",
            "O(2ⁿ) → O(n) by adding two lines. This is top-down DP."),
    ],
    costs=[
        _cost("Linear recursion", "O(n)", "O(n) stack", "Depth is the space cost."),
        _cost("Binary recursion, no memo", "O(2ⁿ)", "O(n) stack", "Naive Fibonacci."),
        _cost("Halving recursion", "O(log n)", "O(log n)", "Fast power, binary search."),
        _cost("Divide and conquer with a linear merge", "O(n log n)", "O(n)", "Merge sort."),
        _cost("Memoised recursion", "O(states × work)", "O(states)", "Top-down DP."),
    ],
    pitfalls=[
        _pit("`StackOverflowError`",
             "Either no base case, or a legitimate recursion deeper than ~10,000 frames.",
             "Check the base case first; if the depth is genuinely large, rewrite iteratively."),
        _pit("The base case returns the wrong identity",
             "`return 0` where the combination multiplies, or `return 1` where it sums.",
             "Ask what the answer for an empty input *must* be for the combination to work."),
        _pit("An exponential runtime in something that looks linear",
             "A sub-answer is recomputed on multiple branches.",
             "Memoise, or restructure so each sub-answer is computed once."),
        _pit("Fast power is O(e) instead of O(log e)",
             "`power(b, e/2)` was written twice rather than stored.",
             "Call once, store in a local, square it."),
        _pit("A shared mutable structure leaks between branches",
             "State was modified before the call and never restored after it.",
             "Either pass immutable arguments, or undo the change — see backtracking."),
    ],
    lessons=["recursion", "alg_recursion", "alg_recurrences", "recurrence"],
    checks=[
        _chk("What are the three parts of writing a recursive function?",
             "A one-sentence promise about what it returns for any input; a base case that "
             "needs no recursion; and a recursive case that trusts the promise and combines."),
        _chk("Why does naive Fibonacci take exponential time?",
             "`fib(n-2)` is recomputed under both `fib(n-1)` and `fib(n-2)`, so the call "
             "tree branches twice at nearly every level: T(n) = T(n−1) + T(n−2)."),
        _chk("What is the space complexity of a recursion n levels deep that allocates "
             "nothing?",
             "O(n) — every pending frame stays on the call stack until it returns."),
        _chk("Why must fast exponentiation store the half-power in a variable?",
             "Calling it twice doubles the work at every level, collapsing O(log e) back to "
             "O(e). Storing it is the entire optimisation."),
    ],
    interview="""
Interviewers probe recursion by asking for the complexity and then for the
iterative version. Have both ready: the recurrence that gives the time bound,
and the observation that depth is memory. And when a recursive solution is
exponential, say *why* — "the same subproblem appears on both branches, so I
will memoise" is the sentence that turns a rejected answer into an accepted one.
""",
    rungs=[
        _rung("Core", "A recurrence you can write in one line.",
              ["nth-fibonacci", "unique-paths-count"],
              {"nth-fibonacci": "Write it naively, note it is O(2ⁿ), then memoise. That one edit is the whole DP stage in miniature.",
               "unique-paths-count": "`paths(i,j) = paths(i-1,j) + paths(i,j-1)`. Same shape, two dimensions."}),
        _rung("Variations", "Recursion that halves rather than decrements.",
              ["fast-power"],
              {"fast-power": "Store the half-power. Calling twice is the bug that makes it O(e)."}),
    ],
    next_up="""
The most common recursive structure in interviews has exactly two smaller
versions: the left subtree and the right one.
""",
)


# --- Unit 21 — Binary trees -------------------------------------------------

_unit(
    "trees", "Binary Trees", "🌲", _S5,
    "Two recursive calls and a decision about where to do the work.",
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
    ],
    interview="""
Trees are the most-asked structure in interviews, and the questions are
deliberately shallow — they want to see whether you can write a clean recursion
under mild pressure. Two habits score: stating the base case before the
recursive one, and saying the space complexity as O(h) rather than O(1),
because the stack is real. When the tree could be skewed, mention it.
""",
    rungs=[
        _rung("Warm up", "One value, computed from the children.",
              ["max-depth-tree", "count-nodes-tree", "invert-binary-tree"],
              {"max-depth-tree": "The template. Everything in this unit is a variation of these three lines."}),
        _rung("Core", "Two-node recursion, and context carried downwards.",
              ["same-tree", "symmetric-tree", "min-depth-tree", "path-sum-exists",
               "inorder-traversal", "preorder-traversal"],
              {"min-depth-tree": "The one-child case. This is the problem that catches everyone — decide what a leaf is first.",
               "symmetric-tree": "Same as `same-tree`, but compare left against right."}),
        _rung("Variations", "Anything phrased in terms of levels.",
              ["level-order-traversal", "right-side-view", "zigzag-level-order"],
              {"level-order-traversal": "The BFS template. Snapshot the queue size.",
               "zigzag-level-order": "Do not reverse the queue — reverse the collected list on alternate levels."}),
        _rung("Stretch", "Return one thing, record another.",
              ["balanced-tree", "diameter-of-tree", "lca-binary-tree", "max-path-sum"],
              {"balanced-tree": "Return the height and use −1 as a “already unbalanced” signal, so it stays a single O(n) pass.",
               "lca-binary-tree": "Return the node found below; a node that hears back from both sides is the ancestor.",
               "max-path-sum": "The hardest of the shape, and the one worth being able to rebuild from scratch."}),
    ],
    next_up="""
Add one invariant to a binary tree — left < node < right — and search becomes
O(log n).
""",
)


# --- Unit 22 — Binary search trees ------------------------------------------

_unit(
    "bst", "Binary Search Trees", "🔎", _S5,
    "One invariant, and every operation becomes a descent.",
    prereqs=["trees"],
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


# --- Unit 23 — Backtracking -------------------------------------------------

_unit(
    "backtracking", "Backtracking", "♟️", _S5,
    "Choose, explore, un-choose — and prune before you descend.",
    prereqs=["bst"],
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
    rungs=[
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


# --- Unit 24 — Graph traversal ----------------------------------------------

_unit(
    "graph-traversal", "Graph Traversal: BFS & DFS", "🕸️", _S5,
    "Trees with cycles — so you need a visited set, and BFS gives shortest paths.",
    prereqs=["backtracking"],
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
    ],
    interview="""
Graph questions are usually disguised: "can these courses be finished", "how
many groups", "fewest moves". The interview skill is *modelling* — saying out
loud what the nodes are, what the edges are, and whether they are directed —
before touching the traversal. Once that sentence exists, the code is a
template. And say why BFS: "edges are unweighted, so BFS layers are distances".
""",
    rungs=[
        _rung("Core", "Traversal on an implicit graph, then a real one.",
              ["number-of-islands", "shortest-path-binary-matrix", "bipartite-check"],
              {"number-of-islands": "One traversal per unvisited land cell. Sink the island as you go.",
               "shortest-path-binary-matrix": "BFS, because the grid is unweighted — and 8-directional, so check the direction array."}),
        _rung("Stretch", "A graph you have to build before you can walk it.",
              ["word-ladder-length"],
              {"word-ladder-length": "The nodes are words and the edges are one-letter changes. Building the adjacency efficiently (wildcard buckets) is most of the problem."}),
    ],
    next_up="""
Traversal answers “can I get there”. Direction adds a second question: is there
an order in which everything can be done at all?
""",
)


# --- Unit 25 — Topological sort ---------------------------------------------

_unit(
    "topological-sort", "Topological Sort & Cycles", "📋", _S5,
    "Order the dependencies — or prove that no order exists.",
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


# --- Unit 26 — Union-find ---------------------------------------------------

_unit(
    "union-find", "Union-Find (Disjoint Set Union)", "🧵", _S5,
    "Connectivity as a near-constant-time operation.",
    prereqs=["topological-sort"],
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
edges arrive cheapest-first, every accepted edge is safe:

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
    rungs=[
        _rung("Core", "Counting components, and the boolean return.",
              ["count-components", "number-of-provinces", "graph-valid-tree",
               "redundant-connection", "detect-cycle-undirected"],
              {"count-components": "Start at n and decrement on each successful union. Nothing else is needed.",
               "redundant-connection": "The answer is literally the first edge whose union returns false.",
               "graph-valid-tree": "Two conditions, not one: n − 1 edges and no failed union."}),
        _rung("Variations", "Sizes, weights and orderings layered on top.",
              ["largest-component-size", "satisfy-equations", "make-network-connected",
               "earliest-full-connect", "mst-total-weight"],
              {"satisfy-equations": "Union all the equalities first, then check every inequality. Order matters.",
               "earliest-full-connect": "Union in timestamp order and stop the moment the component count hits 1.",
               "mst-total-weight": "Kruskal's. Sort by weight, union greedily, stop at n − 1 edges."}),
        _rung("Stretch", "Build the edge set yourself, then run Kruskal.",
              ["min-cost-connect-points"],
              {"min-cost-connect-points": "The graph is complete and implicit — all O(n²) pairwise distances. Generate, sort, union."}),
    ],
    next_up="""
Connectivity is a yes-or-no question. The last unit of the stage asks *how far*,
once the edges stop being equal.
""",
)


# --- Unit 27 — Shortest paths -----------------------------------------------

_unit(
    "shortest-paths", "Weighted Shortest Paths", "🛣️", _S5,
    "When edges cost different amounts, BFS stops working.",
    prereqs=["union-find"],
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
    rungs=[
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
One stage left. It covers the two remaining ways to make a hard problem
tractable — commit to a local choice (greedy), or remember every subproblem
(dynamic programming) — plus the structure that makes prefixes searchable.
""",
)
