# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 (Trees & Graphs) — the help layer, part 1: binary trees, BSTs,
# backtracking and graph traversal.
#
# exec'd by tools/dsa_curriculum.py after dsa_s6_depth2.py; dsa_s6_help2.py
# holds the other four units, the stage cheat sheet and the attach step. Per
# unit: quizzes (bug / predict / model), stuck triage, edge cases, a worked
# solution, an interview script, a lab and "work it out" cards.
#
# Every work-it-out answer below is COMPUTED by running the algorithm (the
# `_c6_*` helpers), and every "predict" quiz asserts its authored answer
# against a Python twin, so a card cannot state a wrong number. Edge-case
# inputs were run through their problems' references when authored.
# ---------------------------------------------------------------------------


# ============================================================ computing kit

def _c6_orders(line):
    pre, ino, post, lvl = _t6_orders(_t6_build(line))
    return [" ".join(map(str, x)) for x in (pre, ino, post, lvl)]


def _c6_adj(n, edges, directed):
    adj = [[] for _ in range(n)]
    for e in edges:
        u, v = e[0], e[1]
        w = e[2] if len(e) > 2 else 1
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))
    return adj


def _c6_bfs(n, edges, s, directed=False):
    adj = _c6_adj(n, edges, directed)
    dist = [-1] * n
    dist[s] = 0
    q = _dq([s])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v, _ in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist, order


def _c6_dfs_order(n, edges, s, directed=False):
    adj = _c6_adj(n, edges, directed)
    seen, out = [False] * n, []

    def go(u):
        seen[u] = True
        out.append(u)
        for v, _ in adj[u]:
            if not seen[v]:
                go(v)

    go(s)
    return out


def _c6_subsets_count(a, target):
    from itertools import combinations as _comb
    return sum(1 for r in range(len(a) + 1) for c in _comb(a, r) if sum(c) == target)


# ============================================================ trees

_T_EX = "7 3 9 1 5 8 10"
_T_ORD = _c6_orders(_T_EX)
_T_SKEW = "1 2 null 3 4 null null 5"
_T_SKEW_ORD = _c6_orders(_T_SKEW)


def _c6_diameter(line):
    root = _t6_build(line)
    best = [0]

    def h(n):
        if n is None:
            return 0
        l, r = h(n.left), h(n.right)
        best[0] = max(best[0], l + r)
        return 1 + max(l, r)

    h(root)
    return best[0]


def _c6_vertical(line):
    root = _t6_build(line)
    cols = {}
    q = _dq([(root, 0, 0)])
    while q:
        n, r, c = q.popleft()
        cols.setdefault(c, []).append((r, n.val))
        for ch, dc in ((n.left, -1), (n.right, 1)):
            if ch:
                q.append((ch, r + 1, c + dc))
    return min(cols), max(cols), len(cols)


_H6_TREES = dict(
    quizzes=[
        _quiz("bug", "`minDepth` returns 1 for the tree `1 2` (a root with one left child). It should be 2. Which change fixes it?",
              r"""
static int minDepth(TreeNode n) {
    if (n == null) return 0;
    return 1 + Math.min(minDepth(n.left), minDepth(n.right));
}
""",
              "When one child is null, recurse only into the other: `if (n.left == null) return 1 + minDepth(n.right);` and symmetrically",
              ["When one child is null, recurse only into the other: `if (n.left == null) return 1 + minDepth(n.right);` and symmetrically",
               "Use `Math.max` instead of `Math.min`",
               "Return 1 for `n == null`",
               "Start the recursion at `root.left`"],
              """
The missing right child returns 0, and `min` picks it — as if the root were a leaf. A leaf
is a node with *no* children; a node with one child must go down the side that exists.
`max` would compute the height instead, and returning 1 for null makes every depth one too
large.
"""),
        _quiz("bug", "The diameter of `1 2 null 3 4 null null 5` is 3 (the path 3-2-4-5), but this prints 4. What is wrong?",
              r"""
int best = 0;
int height(TreeNode n) {
    if (n == null) return 0;
    int l = height(n.left), r = height(n.right);
    best = Math.max(best, l + r + 1);
    return 1 + Math.max(l, r);
}
""",
              "`l + r + 1` counts nodes on the path; the diameter counts edges, so record `l + r`",
              ["`l + r + 1` counts nodes on the path; the diameter counts edges, so record `l + r`",
               "The recursion should return `l + r`",
               "`best` should be updated after the return",
               "Height of null should be −1"],
              """
With height counted in nodes, `l + r` is the number of edges on the longest path through n
(each side contributes its height in edges plus the edge to n). Adding 1 counts the nodes
instead. (Returning −1 for null with `l + r + 2` is the equivalent edge-counted form.)
"""),
        _quiz("predict", f"What does in-order print for `{_T_SKEW}`?",
              f"""
// level order: {_T_SKEW}
void in(TreeNode n) {{
    if (n == null) return;
    in(n.left);
    System.out.print(n.val + " ");
    in(n.right);
}}
""",
              _T_SKEW_ORD[1],
              [_T_SKEW_ORD[1], _T_SKEW_ORD[0], _T_SKEW_ORD[2], "3 2 4 5 1"],
              f"""
The tree: 1 has left child 2; 2 has children 3 and 4; 4 has a left child 5. In-order visits
left subtree, node, right subtree — so 5 comes *before* its parent 4: {_T_SKEW_ORD[1]}.
(Pre-order is {_T_SKEW_ORD[0]}; post-order is {_T_SKEW_ORD[2]}.)
"""),
        _quiz("bug", "Rebuilding from post-order and in-order produces the wrong tree. Which change fixes it?",
              r"""
TreeNode build(int lo, int hi) {           // idx starts at n - 1
    if (lo > hi) return null;
    TreeNode root = new TreeNode(post[idx--]);
    int m = pos.get(root.val);
    root.left = build(lo, m - 1);
    root.right = build(m + 1, hi);
    return root;
}
""",
              "Build `root.right` before `root.left`",
              ["Build `root.right` before `root.left`",
               "Start idx at 0 and increment it",
               "Use `m` instead of `m - 1` for the left range",
               "Look the root up in the post-order instead"],
              """
Walking post-order backwards visits root, then the right subtree, then the left. The shared
index must be consumed in that order, so the right subtree is built first. Starting at 0
would read the leftmost leaf as the root.
"""),
        _quiz("predict", "How many guards does the greedy place on a path of 7 rooms (a chain)?",
              r"""
// 0 = unwatched, 1 = guard, 2 = watched; null counts as watched
int dfs(TreeNode n) {
    if (n == null) return 2;
    int l = dfs(n.left), r = dfs(n.right);
    if (l == 0 || r == 0) { guards++; return 1; }
    return (l == 1 || r == 1) ? 2 : 0;
}
// answer = guards + (dfs(root) == 0 ? 1 : 0)
""",
              "3",
              ["3", "2", "4", "7"],
              """
From the bottom: room 7 unwatched → room 6 takes a guard → room 5 watched → room 4
unwatched → room 3 takes a guard → room 2 watched → room 1 unwatched, and as the root it
takes a guard of its own. Guards in rooms 6, 3 and 1: three. ⌈7 / 3⌉ = 3 is the known
bound for a path.
"""),
        _quiz("bug", "Level-order sums come out wrong: level 1's sum includes level 2's nodes. What is wrong?",
              r"""
while (!q.isEmpty()) {
    long sum = 0;
    for (int i = 0; i < q.size(); i++) {
        TreeNode n = q.poll();
        sum += n.val;
        if (n.left != null) q.add(n.left);
        if (n.right != null) q.add(n.right);
    }
    sums.add(sum);
}
""",
              "Read `q.size()` once into a variable before the loop",
              ["Read `q.size()` once into a variable before the loop",
               "Use a stack instead of a queue",
               "Add the children before polling",
               "Reset `sum` inside the for loop"],
              """
`q.size()` is re-evaluated every iteration, and the queue grows as children are added — so
the loop keeps going into the next level. Snapshot the size first; it is the only record of
where this level ends.
"""),
    ],
    stuck=[
        _stuck("The answer at a node depends on its subtrees",
               "What must each child *return* for the parent to finish? Write that sentence, then the null case that makes it true at a leaf."),
        _stuck("The answer is a path that can bend anywhere",
               "Can the function return the best *one-sided* path and record the two-sided one in a field?"),
        _stuck("It asks for levels, rows, or “the view from the side”",
               "Is it a BFS with a frozen level size — or a DFS carrying (row, col) down?"),
        _stuck("It asks for an answer for every node as the root",
               "Can you compute it for root 0, then find how it changes when the root moves one edge?"),
        _stuck("You need the path itself, not just its sum",
               "Keep one list, push before recursing, pop after — and record a copy at the leaf."),
        _stuck("The tree may be 10⁵ deep",
               "Will recursion overflow? Take a BFS order and run your passes over it backwards (children first) and forwards (parents first)."),
    ],
    edge_cases=[
        _edge("leaf-similar-trees", "One tree has an extra leaf at the end", "1 2 3\n1 2 3 null null 4 5\n",
              "Comparing leaves pairwise until one list ends, and forgetting to compare lengths."),
        _edge("vertical-order-tree", "Two nodes in one row and column", "0 1 2 3 9 8 4\n",
              "Leaving them in BFS order instead of sorting by value."),
        _edge("tree-postorder-inorder", "A left chain", "4\n1 2 3 4\n1 2 3 4\n",
              "Building the left subtree first while walking post-order backwards."),
        _edge("flatten-tree-to-list", "Already a right chain", "7 null 8\n",
              "An in-place splice that assumes a left child exists."),
        _edge("max-ancestor-difference", "Siblings are far apart but unrelated", "50 0 100\n",
              "Comparing all pairs, not ancestor–descendant pairs."),
        _edge("path-sum-list", "A one-child node is not a leaf", "5 2\n5\n",
              "Treating the root as a leaf because its right child is null."),
        _edge("path-sum-list", "Negative values come back to the target", "1 -2 3 4 null null null 3\n6\n",
              "Pruning when the running sum passes k — only valid for non-negative values."),
        _edge("boundary-of-tree", "One node", "9\n", "Printing the root twice — once as the root and once as a leaf."),
        _edge("boundary-of-tree", "No left child", "5 null 8 6 9\n",
              "Walking a left boundary that does not exist and printing the right side twice."),
        _edge("sum-of-distances-tree", "One town", "1 0\n", "Reading a first edge that is not there."),
        _edge("tree-cameras", "One room", "0\n", "Returning 0 guards because the root came back \"unwatched\" and was not counted."),
    ],
    walkthrough=_walk("sum-of-distances-tree", "Total travel from every town", [
        """
n towns form a tree with unit-length roads. For every town print the sum of its distances to
all others; n is up to 10⁵.

Restate: for each vertex v, compute Σ dist(v, u) over all u.
""",
        """
\"For every node, as if it were the root\" is the rerooting signal (trees unit), and the tree
shape (n − 1 edges, connected) rules out anything cyclic. n = 10⁵ rules out a BFS per town.
""",
        """
One BFS per town:

```java
for (int s = 0; s < n; s++) ans[s] = sumOfBfsDistances(s);   // O(n) each
```

O(n²) = 10¹⁰ at the limit — but it is the oracle for small random trees.
""",
        """
Root the tree at 0. Let size[v] be the number of towns in v's subtree. Moving the root from a
parent p to its child c changes every distance by exactly one: the size[c] towns on c's side
get one step closer, and the other n − size[c] get one step farther:

ans[c] = ans[p] − size[c] + (n − size[c]).

So all answers follow from ans[0], which is an ordinary bottom-up DP:
down[p] = Σ (down[c] + size[c]).
""",
        """
```java
// BFS order from 0 gives parents before children: no recursion needed
for (int i = n - 1; i >= 1; i--) {              // pass 1, bottom-up
    int u = order[i], p = parent[u];
    size[p] += size[u];
    down[p] += down[u] + size[u];
}
ans[0] = down[0];
for (int i = 1; i < n; i++) {                   // pass 2, top-down
    int u = order[i];
    ans[u] = ans[parent[u]] - size[u] + (n - size[u]);
}
```

`long` for size, down and ans: a path of 10⁵ gives sums near 5 · 10⁹.
""",
        """
| Input | Expected | What it catches |
| --- | --- | --- |
| `1 0` | `0` | no edges to read |
| a path of 3: `3 2 / 0 1 / 1 2` | `3 2 3` | the middle is cheapest |
| a star centred on 3 | centre 5, leaves 9 | size[c] = 1 everywhere |
| a 10⁵ path | ends ≈ 5 · 10⁹ | int overflow; recursion depth |

Then compare against the O(n²) oracle on 200 random trees of up to 12 towns.

**Cost:** two passes over a BFS order — O(n) time and memory.
""",
    ]),
    interview_script="""
### Say it out loud

- *"Base case first: the empty tree returns 0, which makes a leaf come out as 1."*
- *"This function returns the height and records the diameter in a field — the answer can
  bend through a node, but only one side can continue up to the parent."*
- *"Space is O(h) for the recursion stack: O(log n) if balanced, O(n) if it degenerates —
  so for 10⁵ nodes I'd go iterative."*
- *"For an answer at every root I compute it once and reroot: each edge changes the answer by
  a formula, so it's O(n) total."*
""",
    lab=_lab("tree", """
Type a tree in level order (`null` for a missing child). The lab draws it with every node at
its in-order position, and shows the four traversal orders, the height, leaves and diameter,
whether it is height-balanced, and whether it is a valid BST. Click a node for its depth,
height, subtree size and the interval a BST would allow it. Type a value to see the descent a
BST search would take.
""", [
        ("A perfect BST", {"tree": "8 4 12 2 6 10 14", "value": 5}),
        ("Diameter off the root", {"tree": "1 2 null 3 4 5 null null 6", "value": 0}),
        ("A chain (height = n)", {"tree": "1 null 2 null 3 null 4 null 5", "value": 3}),
        ("Zig-zag", {"tree": "1 2 null null 3 4 null null 5", "value": 0}),
        ("Full, depth 4", {"tree": "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15", "value": 0}),
    ]),
    drills=[
        _calc(f"Pre-order of `{_T_EX}`?", _T_ORD[0],
              "Node, then its whole left subtree, then its right subtree."),
        _calc(f"In-order of `{_T_EX}`?", _T_ORD[1],
              "Left subtree, node, right subtree — this tree is a BST, so it comes out sorted."),
        _calc(f"Post-order of `{_T_EX}`?", _T_ORD[2],
              "Both subtrees before the node: the root comes last."),
        _calc(f"Post-order of `{_T_SKEW}`?", _T_SKEW_ORD[2],
              "3, then 5 (under 4), then 4, then 2, then the root."),
        _calc(f"Height (in nodes) of `{_T_SKEW}`?", str(_t6_height(_t6_build(_T_SKEW))),
              "The longest root path is 1 → 2 → 4 → 5."),
        _calc(f"Diameter (in edges) of `{_T_SKEW}`?", str(_c6_diameter(_T_SKEW)),
              "3 – 2 – 4 – 5 (or 1 – 2 – 4 – 5): three edges. The best path need not bend through the root."),
        _calc("How many nodes does a perfect binary tree of height 5 (in nodes) have?", "31",
              "2⁵ − 1 = 31: each level doubles, 1 + 2 + 4 + 8 + 16."),
        _calc("In a tree of 4 nodes, how many edges are there?", "3",
              "Every node except the root has exactly one edge to its parent: n − 1."),
        _calc(f"How many columns does the vertical order of `{_T_EX}` have?",
              str(_c6_vertical(_T_EX)[2]),
              "Columns −2 (1), −1 (3), 0 (7, 5, 8), 1 (9), 2 (10)."),
        _calc("Rerooting: n = 10, a child c has size[c] = 3 and its parent's answer is 20. What is ans[c]?",
              "24", "ans[c] = ans[p] − size[c] + (n − size[c]) = 20 − 3 + 7 = 24."),
    ],
)


# ============================================================ BSTs

_B_INS = [50, 30, 70, 20, 40, 60, 80]


def _c6_bst_line(vals):
    return _t6_level(_t6_bst(vals))


def _c6_bst_delete(vals, key):
    root = _t6_bst(vals)

    def delete(n, k):
        if n is None:
            return None
        if k < n.val:
            n.left = delete(n.left, k)
        elif k > n.val:
            n.right = delete(n.right, k)
        else:
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            s = n.right
            while s.left:
                s = s.left
            n.val = s.val
            n.right = delete(n.right, s.val)
        return n

    return _t6_level(delete(root, key))


def _c6_sorted_build(a):
    def build(lo, hi):
        if lo > hi:
            return None
        m = (lo + hi) // 2
        n = _TN(a[m])
        n.left = build(lo, m - 1)
        n.right = build(m + 1, hi)
        return n

    return _t6_level(build(0, len(a) - 1))


_H6_BST = dict(
    quizzes=[
        _quiz("bug", "This validator accepts `5 3 8 null null 4 9`, which is not a BST. Why?",
              r"""
static boolean valid(TreeNode n) {
    if (n == null) return true;
    if (n.left != null && n.left.val >= n.val) return false;
    if (n.right != null && n.right.val <= n.val) return false;
    return valid(n.left) && valid(n.right);
}
""",
              "It compares each node only with its children; 4 is in 5's right subtree and must be > 5",
              ["It compares each node only with its children; 4 is in 5's right subtree and must be > 5",
               "It should use `>` instead of `>=`",
               "It must also check that the tree is balanced",
               "Null children should return false"],
              """
The BST rule is about whole subtrees. 4 < 8 satisfies its parent, but it sits in the root's
right subtree, where everything must exceed 5. Pass the allowed interval (lo, hi) down, or
check that in-order is strictly increasing.
"""),
        _quiz("bug", "After `delete(root, 30)` on a node with two children, the value 35 now appears twice. What was forgotten?",
              r"""
TreeNode s = n.right;
while (s.left != null) s = s.left;
n.val = s.val;
return n;
""",
              "Deleting the successor from the right subtree: `n.right = delete(n.right, s.val);`",
              ["Deleting the successor from the right subtree: `n.right = delete(n.right, s.val);`",
               "Returning `n.right` instead of `n`",
               "Walking `s.right` instead of `s.left`",
               "Copying `n.val` into `s` instead"],
              """
Copying the successor's value up fills the hole, but the successor node is still there — a
duplicate. Remove it from the right subtree, where it has no left child, so it is the easy
one-or-zero-children case.
"""),
        _quiz("predict", f"Deleting 50 (the root) from the BST built by inserting {', '.join(map(str, _B_INS))}. What is the level order afterwards?",
              r"""
// two children: copy in the in-order successor, then delete it from the right subtree
""",
              _c6_bst_delete(_B_INS, 50),
              [_c6_bst_delete(_B_INS, 50), "40 30 70 20 null 60 80", "70 30 80 20 40 60", "60 30 80 20 40 70"],
              """
The successor of 50 is the leftmost node of its right subtree, 60. 60 moves up to the root
and the old 60 leaf disappears. (Using the predecessor, 40, gives the second option — also a
valid BST, but not what this rule produces.)
"""),
        _quiz("predict", "What level order does the middle-first build give for `1 2 3 4 5 6`?",
              r"""
TreeNode build(int lo, int hi) {
    if (lo > hi) return null;
    int mid = (lo + hi) >>> 1;          // lower middle
    TreeNode n = new TreeNode(a[mid]);
    n.left = build(lo, mid - 1);
    n.right = build(mid + 1, hi);
    return n;
}
""",
              _c6_sorted_build([1, 2, 3, 4, 5, 6]),
              [_c6_sorted_build([1, 2, 3, 4, 5, 6]), "4 2 6 1 3 5", "3 2 5 1 null 4 6", "1 null 2 null 3 null 4 null 5 null 6"],
              """
Index (0 + 5) / 2 = 2 → 3 is the root. Left half [1, 2] → 1 (lower middle) with 2 on its
right; right half [4, 5, 6] → 5 with 4 and 6. The upper middle would give 4 2 6 1 3 5.
"""),
        _quiz("bug", "`trim(root, 6, 16)` on the BST `12 5 20 2 8 15 25 7` loses 8 and 7, which are in range. What is wrong?",
              r"""
TreeNode trim(TreeNode n, int lo, int hi) {
    if (n == null) return null;
    if (n.val < lo) return null;            // too small: drop it
    if (n.val > hi) return null;            // too big: drop it
    n.left = trim(n.left, lo, hi);
    n.right = trim(n.right, lo, hi);
    return n;
}
""",
              "A too-small node must return `trim(n.right, lo, hi)` (and a too-big one `trim(n.left, lo, hi)`), not null",
              ["A too-small node must return `trim(n.right, lo, hi)` (and a too-big one `trim(n.left, lo, hi)`), not null",
               "Trim the children before checking the node",
               "Use `<=` and `>=`",
               "Return `n.left` when the node is too small"],
              """
Only one side of an out-of-range node is condemned. 5 is too small, and so is everything in
its left subtree (2) — but its right subtree holds 8 and 7, which are in range. Return the
trimmed surviving side, and it takes 5's place under 12.
"""),
        _quiz("predict", "An iterative in-order on the BST `8 4 12 2 6` stops at k = 3. What does it return?",
              r"""
Deque<TreeNode> st = new ArrayDeque<>();
for (TreeNode cur = root; ; ) {
    while (cur != null) { st.push(cur); cur = cur.left; }
    cur = st.pop();
    if (--k == 0) return cur.val;
    cur = cur.right;
}
""",
              "6", ["6", "4", "8", "12"],
              """
In-order is 2, 4, 6, 8, 12. The third value visited is 6 — and the loop never touches 8's
right subtree.
"""),
    ],
    stuck=[
        _stuck("It says BST and asks for an order, a rank or a range",
               "Can an in-order walk (sorted) or a pruned descent answer it without visiting every node?"),
        _stuck("A node must be removed or replaced",
               "Which of the three cases is it — no child, one child, two children? For two, who is the in-order successor?"),
        _stuck("You are checking a BST property",
               "What interval (lo, hi) does each node inherit from its ancestors? Check against that, not against the children."),
        _stuck("Two BSTs, or a BST and a sorted list",
               "Can you treat each as a sorted stream (an iterator) and merge them?"),
        _stuck("The input is sorted and you must build a tree",
               "Which element should be the root so both sides are the same size?"),
        _stuck("Values may repeat",
               "Which side do duplicates go? And in in-order, equal values are adjacent — can you count runs?"),
    ],
    edge_cases=[
        _edge("sorted-array-to-bst", "Two elements", "2\n1 2\n",
              "Using the upper middle: the answer's root would be 2, not 1."),
        _edge("sorted-array-to-bst", "Extreme values", "4\n-1000000000 -1 1 1000000000\n",
              "Computing the middle as (a[lo] + a[hi]) / 2 — values, not indices."),
        _edge("bst-mode", "Every value is a mode", _c6_bst_line([4, 2, 7]) + "\n",
              "Returning only the first value that reaches the best count."),
        _edge("bst-mode", "All equal", _c6_bst_line([2, 2, 2, 2]) + "\n",
              "A run counter that never resets its best."),
        _edge("bst-delete", "Delete the only node", "7\n1\n7\n",
              "Not returning the new root — the tree must print EMPTY."),
        _edge("bst-delete", "The successor has a right child", _c6_bst_line([20, 10, 40, 30, 50, 35]) + "\n1\n20\n",
              "Detaching the successor without re-linking its right subtree."),
        _edge("bst-delete", "Keys that are not in the tree", _c6_bst_line([3, 1, 5]) + "\n3\n0 2 6\n",
              "Crashing on a null child when the key is missing."),
        _edge("trim-bst", "The root goes and a child takes over", _c6_bst_line([10, 5, 15, 3, 7]) + "\n4 8\n",
              "Keeping the root because a child is in range."),
        _edge("trim-bst", "Nothing in range", _c6_bst_line([4, 2, 6]) + "\n10 20\n",
              "Printing an empty line instead of EMPTY."),
        _edge("merge-two-bsts", "The second tree is empty", _c6_bst_line([3, 3, 6]) + "\nnull\n",
              "Peeking at an empty stack."),
    ],
    walkthrough=_walk("bst-delete", "Remove keys from a BST", [
        """
Delete keys one after another from a BST of distinct values; ignore missing keys; a node with
two children takes its in-order successor's value. Print the result in level order.
""",
        """
\"Delete from a BST\" is a descent plus a repair, and the repair must keep the invariant —
the BST unit. The size (3000 nodes, 3000 keys) allows O(h) per key.
""",
        """
Rebuild from scratch: collect all values, drop the deleted ones, insert the rest into a fresh
BST. O(n) per deletion — and it gives a *different* shape from the one the statement defines,
so it is not even correct here. The shape is part of the answer.
""",
        """
Every deletion is one of three cases:

- **no children** — the node simply goes (return null to the parent);
- **one child** — the child takes its place, and it already satisfies every interval the
  node did;
- **two children** — the value that can fill the hole must exceed everything on the left and
  undercut everything on the right: the **in-order successor**, the leftmost node of the
  right subtree. Copy it in, then delete it from the right subtree — where it has no left
  child, so that deletion is the easy case.

Returning the new subtree root from every call handles \"the node is the root\" for free.
""",
        """
```java
static TreeNode delete(TreeNode n, int key) {
    if (n == null) return null;                       // key not present
    if (key < n.val) n.left = delete(n.left, key);
    else if (key > n.val) n.right = delete(n.right, key);
    else {
        if (n.left == null) return n.right;
        if (n.right == null) return n.left;
        TreeNode s = n.right;
        while (s.left != null) s = s.left;
        n.val = s.val;
        n.right = delete(n.right, s.val);
    }
    return n;
}
// for (int key : keys) root = delete(root, key);
```
""",
        """
| Case | Catches |
| --- | --- |
| delete the only node | returning the new root (EMPTY) |
| delete a leaf, then its parent | the one-child splice |
| successor with a right child | re-linking below the successor |
| a missing key | the null descent |
| delete everything in random order | all three cases, repeatedly |

Check against a `TreeSet`: after each deletion, the in-order must equal the set's iteration.

**Cost:** O(h) per key — O(k log n) on a random tree, O(k · n) on a chain.
""",
    ]),
    interview_script="""
### Say it out loud

- *"The invariant is on whole subtrees, so I carry an interval (lo, hi) down, with long
  bounds so Integer.MIN_VALUE is still a legal key."*
- *"In-order of a BST is sorted — k-th smallest is an in-order that stops at k, O(h + k)."*
- *"Deletion has three cases; with two children I copy the successor in and delete it from
  the right subtree, where it has at most one child."*
- *"Everything here is O(h). In production I'd use a TreeMap, which keeps h at O(log n)."*
""",
    lab=_lab("tree", """
Type a BST in level order, or break one on purpose. The lab says whether it is valid — and if
not, which node falls outside the interval its ancestors impose, and what that interval is.
Type a value to watch the search descend and see where an insert would attach. Click nodes to
read their intervals.
""", [
        ("A BST", {"tree": _c6_bst_line(_B_INS), "value": 65}),
        ("The classic trap", {"tree": "5 3 8 null null 4 9", "value": 4}),
        ("Duplicate on the wrong side", {"tree": "5 3 7 null 5", "value": 5}),
        ("Sorted inserts: a chain", {"tree": "1 null 2 null 3 null 4 null 5 null 6", "value": 7}),
        ("Balanced from sorted 1..15", {"tree": _c6_sorted_build(list(range(1, 16))), "value": 11}),
    ]),
    drills=[
        _calc(f"Insert {', '.join(map(str, [40, 20, 60, 10, 30, 50, 70, 35]))} into an empty BST. Level order?",
              _c6_bst_line([40, 20, 60, 10, 30, 50, 70, 35]),
              "Each value descends by comparison to the null it falls off; 35 ends up as 30's right child."),
        _calc("In the BST `8 4 12 2 6 10 14`, what is the in-order successor of 8?", "10",
              "The leftmost node of 8's right subtree: 12 → 10."),
        _calc("In the BST `8 4 12 2 6 10 14`, what is the in-order successor of 6?", "8",
              "6 has no right subtree, so the successor is the nearest ancestor for which 6 is in the left subtree: 8."),
        _calc("How many nodes does a search for 13 visit in `8 4 12 2 6 10 14`?", "3",
              "8 → 12 → 14, then 14's left child is null: not found after 3 comparisons."),
        _calc(f"Level order after deleting 30 from the BST built by inserting {', '.join(map(str, _B_INS))}?",
              _c6_bst_delete(_B_INS, 30),
              "30 has two children; its successor 40 (a leaf) moves up."),
        _calc("Level order of the balanced BST built from `1 2 3 4 5 6 7` (lower middle)?",
              _c6_sorted_build([1, 2, 3, 4, 5, 6, 7]), "4 is the middle; 2 and 6 are the middles of the halves."),
        _calc("What is the height (in nodes) of the balanced BST built from 1 … 100?", "7",
              "⌈log₂(101)⌉ = 7: a tree of height 6 holds at most 63 nodes, height 7 up to 127."),
        _calc("What interval (lo, hi) must a node satisfy if it is the left child of 20, which is the right child of 10?",
              "(10, 20)", "Going right from 10 sets lo = 10; going left from 20 sets hi = 20.",
              accept=["10 20", "10, 20"]),
        _calc("A BST was built by inserting 1, 2, …, 1000 in order. What is its height (in nodes)?", "1000",
              "Every key becomes the right child of the previous one: a chain."),
    ],
)


# ============================================================ backtracking

def _c6_comb_sum_count(cands, target):
    cands = sorted(cands)
    out = [0]

    def dfs(start, rem):
        if rem == 0:
            out[0] += 1
            return
        for i in range(start, len(cands)):
            if cands[i] > rem:
                break
            dfs(i, rem - cands[i])

    dfs(0, target)
    return out[0]


def _c6_calls_subsets(n):
    return 2 ** (n + 1) - 1


def _c6_nqueens(n):
    cols, d1, d2 = set(), set(), set()
    cnt = [0]

    def place(r):
        if r == n:
            cnt[0] += 1
            return
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c)
            place(r + 1)
            cols.discard(c); d1.discard(r - c); d2.discard(r + c)

    place(0)
    return cnt[0]


def _c6_colourings(n, edges, k):
    from itertools import product as _prod
    return sum(1 for c in _prod(range(k), repeat=n) if all(c[u] != c[v] for u, v in edges))


_H6_BACKTRACK = dict(
    quizzes=[
        _quiz("bug", "Every list in `result` comes out empty. Which change fixes it?",
              r"""
void dfs(int start, List<Integer> cur) {
    result.add(cur);
    for (int i = start; i < a.length; i++) {
        cur.add(a[i]);
        dfs(i + 1, cur);
        cur.remove(cur.size() - 1);
    }
}
""",
              "Record a copy: `result.add(new ArrayList<>(cur));`",
              ["Record a copy: `result.add(new ArrayList<>(cur));`",
               "Remove the `cur.remove` line",
               "Recurse with `i` instead of `i + 1`",
               "Declare `cur` inside the loop"],
              """
`result` holds many references to one list, which the undo steps empty by the time the search
ends. Snapshot it when recording. Deleting the undo would instead leak finished choices into
later branches.
"""),
        _quiz("bug", "With input `1 2 2`, the subsets list contains `[1, 2]` twice. Which line fixes it (after sorting)?",
              r"""
Arrays.sort(a);
void dfs(int start) {
    result.add(new ArrayList<>(cur));
    for (int i = start; i < a.length; i++) {
        // ← here
        cur.add(a[i]); dfs(i + 1); cur.remove(cur.size() - 1);
    }
}
""",
              "`if (i > start && a[i] == a[i - 1]) continue;`",
              ["`if (i > start && a[i] == a[i - 1]) continue;`",
               "`if (i > 0 && a[i] == a[i - 1]) continue;`",
               "`if (cur.contains(a[i])) continue;`",
               "Use a HashSet for `result`"],
              """
Two equal values *at the same depth* open identical branches; skip all but the first. The
`i > 0` version also skips a value that is the first choice at a deeper level, losing
`[1, 2, 2]`. A HashSet of results works but still does the duplicate work.
"""),
        _quiz("predict", "How many times is `dfs` called in total to generate all subsets of 4 elements?",
              r"""
void dfs(int i) {                 // include / exclude element i
    if (i == n) { record(); return; }
    cur.add(a[i]); dfs(i + 1); cur.remove(cur.size() - 1);
    dfs(i + 1);
}
// dfs(0) with n = 4
""",
              str(_c6_calls_subsets(4)),
              [str(_c6_calls_subsets(4)), "16", "15", "32"],
              """
A full binary tree of depth 4: 2⁴ = 16 leaves plus 15 internal calls = 31 = 2⁵ − 1. The 16
leaves are the subsets; the internal calls are the price of reaching them.
"""),
        _quiz("predict", "How many combinations does this count for candidates `2 3 6 7`, target 7?",
              r"""
void dfs(int start, int rem) {          // candidates sorted
    if (rem == 0) { count++; return; }
    for (int i = start; i < c.length; i++) {
        if (c[i] > rem) break;
        dfs(i, rem - c[i]);             // reuse allowed
    }
}
""",
              str(_c6_comb_sum_count([2, 3, 6, 7], 7)),
              [str(_c6_comb_sum_count([2, 3, 6, 7], 7)), "3", "1", "4"],
              """
{2, 2, 3} and {7}. Recursing with `i` (not `i + 1`) allows reuse, and starting at `start`
keeps each combination in one order — {3, 2, 2} is never produced separately.
"""),
        _quiz("predict", "How many ways can 5 queens be placed on a 5 × 5 board so none attack?",
              r"""
void place(int row) {
    if (row == n) { count++; return; }
    for (int c = 0; c < n; c++)
        if (!cols[c] && !d1[row - c + n] && !d2[row + c]) {
            set(row, c); place(row + 1); clear(row, c);
        }
}
""",
              str(_c6_nqueens(5)),
              [str(_c6_nqueens(5)), "4", "2", "40"],
              """
10. The sequence for n = 1…8 is 1, 0, 0, 2, 10, 4, 40, 92 — worth knowing as a regression
test for your own solver.
"""),
        _quiz("model", "Twelve people must be seated at tables of four so that the three sums of their scores match, n ≤ 16. Which model fits?",
              """
scores: 9 4 7 2 ...   (12 values)
tables: 3, each seating exactly 4
""",
              "Backtracking into k buckets (largest first, skip equal loads) — or a bitmask DP over subsets",
              ["Backtracking into k buckets (largest first, skip equal loads) — or a bitmask DP over subsets",
               "Sort and deal round-robin — a greedy",
               "Dijkstra over table loads",
               "A sliding window over the sorted scores"],
              """
It is a partition into k equal groups, with n ≤ 16 announcing that exponential search is
expected. Greedy dealing fails on inputs like 6 5 4 3 1 1 into two groups. The table size is
an extra constraint on each bucket's count, checked the same way as its sum.
"""),
    ],
    stuck=[
        _stuck("n ≤ 20 (or 10, or 16) and it asks for all ways, or any way",
               "What is one *choice*? Write choose / explore / un-choose before any logic."),
        _stuck("Subsets or permutations?",
               "Does order matter? No → a `start` index. Yes → a `used[]` array."),
        _stuck("It is correct but too slow",
               "What partial state can already never succeed? Sort so the check becomes a `break`."),
        _stuck("Duplicate answers appear",
               "Are equal values at the same depth opening identical branches? Sort, then skip them."),
        _stuck("The search tries the same thing under different labels",
               "Are the buckets / colours / slots interchangeable? Try only the first of each equal group."),
        _stuck("It only asks how many",
               "Do different branches reach the same (index, remaining) state? Then memoise — it has become a DP."),
    ],
    edge_cases=[
        _edge("binary-strings-n", "One switch", "1\n", "An off-by-one that prints length-0 strings."),
        _edge("partition-k-equal", "Not divisible", "3 2\n1 1 1\n", "Searching at all when total % k ≠ 0."),
        _edge("partition-k-equal", "One item too big", "4 2\n9 1 1 1\n", "Missing the max > target check, then searching."),
        _edge("partition-k-equal", "Greedy fails", "6 2\n6 5 4 3 1 1\n",
              "Filling buckets greedily: 6 + 3 then 5 + 4 + 1 + 1 overflows; the answer is {6, 4}, {5, 3, 1, 1}."),
        _edge("partition-k-equal", "Sixteen equal values", "16 8\n" + " ".join(["3"] * 16) + "\n",
              "No symmetry pruning: the search re-tries every relabelling of the buckets."),
        _edge("map-colorings-count", "One colour, no borders", "3 0 1\n", "Returning 0 — one colouring exists."),
        _edge("map-colorings-count", "Triangle with two colours", "3 3 2\n0 1\n1 2\n0 2\n", "Counting partial colourings."),
        _edge("word-break-sentences", "The adversarial dead end", "aaaaaaaaaaaaaaaaaaaaaaab\n3 a aa aaa\n",
              "No feasibility table: millions of prefixes, zero sentences."),
        _edge("word-break-sentences", "Duplicate dictionary words", "gogo\n3 go go og\n",
              "Printing each sentence twice."),
        _edge("expression-target-count", "Leading zeros", "105 5\n", "Allowing 05 as an operand."),
        _edge("expression-target-count", "A ten-digit operand", "9999999999 9999999999\n", "int overflow."),
    ],
    walkthrough=_walk("partition-k-equal", "Split the loot evenly", [
        """
n ≤ 16 values, k friends: can every value go to one friend so all totals are equal?
""",
        """
\"n ≤ 16\" plus \"split into groups\" says exponential search is expected — backtracking (or a
bitmask DP, stage 8). There is no greedy: 6 5 4 3 1 1 into two groups defeats every obvious
rule.
""",
        """
Try every assignment of items to friends:

```java
boolean assign(int i) {
    if (i == n) return allEqual(load);
    for (int b = 0; b < k; b++) { load[b] += a[i]; if (assign(i + 1)) return true; load[b] -= a[i]; }
    return false;
}
```

kⁿ leaves — 4¹⁶ ≈ 4 · 10⁹. Correct, as an oracle for n ≤ 8.
""",
        """
Three prunes, each removing whole subtrees:

1. **Capacity**: the target is total / k; never let a bucket exceed it (and reject at once if
   total % k ≠ 0 or max > target).
2. **Largest first**: sort descending, so big items fail early, near the root, where a failure
   cuts the most.
3. **Symmetry**: buckets are unlabelled. If bucket b has the same load as bucket b − 1, putting
   the item there repeats that search — skip it. And if placing an item in an *empty* bucket
   failed, every other empty bucket fails too — stop.

With all three, the answer comes back in a few thousand calls even at n = 16.
""",
        """
```java
boolean place(int i) {
    if (i == n) return true;                          // loads sum to k·T, none exceeds T
    for (int b = 0; b < k; b++) {
        if (load[b] + a[i] > T) continue;
        if (b > 0 && load[b] == load[b - 1]) continue;
        load[b] += a[i];
        if (place(i + 1)) return true;
        load[b] -= a[i];
        if (load[b] == 0) break;
    }
    return false;
}
```
""",
        """
| Input | Expected | Catches |
| --- | --- | --- |
| `3 2 / 1 1 1` | false | total % k |
| `4 2 / 9 1 1 1` | false | max > target |
| `6 2 / 6 5 4 3 1 1` | true | greedy thinking |
| sixteen 3s into 8 | true | missing symmetry pruning (time) |
| `16 4`, fifteen 10s and an 18 | false | exhaustive failure is still fast |

Cross-check with the brute force (or a bitmask DP) on 200 random small inputs.

**Cost:** O(kⁿ) worst case, O(n + k) memory; in practice the prunes make it fast.
""",
    ]),
    interview_script="""
### Say it out loud

- *"n is at most 16, so exponential is expected — I'll backtrack and prune."*
- *"The template is choose, explore, un-choose; apply and undo are exact mirrors."*
- *"I sort first so that once a candidate is too big I can break, not continue."*
- *"Complexity: 2ⁿ subsets times n to copy each answer, O(n) extra space for the path."*
""",
    lab=_lab("search", """
Type up to ten integers and pick a search. The lab runs it and shows the event log — every
choose, undo, emit and prune, indented by depth — the answers in the order they appear, and
**how many calls the search made with and without pruning**. Switch pruning off to see the
same answers cost more.
""", [
        ("Subsets of 1 2 3", {"items": "1 2 3", "k": 0, "target": 0, "mode": "subsets"}),
        ("5 choose 3", {"items": "1 2 3 4 5", "k": 3, "target": 0, "mode": "combinations"}),
        ("Permutations of 1 2 3", {"items": "1 2 3", "k": 0, "target": 0, "mode": "permutations"}),
        ("Combination sum: 2 3 5 → 8", {"items": "2 3 5", "k": 0, "target": 8, "mode": "combsum"}),
        ("Subset sum: pruning pays", {"items": "3 34 4 12 5 2 7 9", "k": 0, "target": 16, "mode": "subsetsum"}),
    ]),
    drills=[
        _calc("How many subsets does a set of 6 elements have?", "64", "2⁶: each element is in or out."),
        _calc("How many 3-element combinations of 7 items?", "35", "C(7, 3) = 7 · 6 · 5 / 3! = 35."),
        _calc("How many permutations of 5 distinct items?", "120", "5! = 120."),
        _calc("How many distinct permutations of `1 1 2`?", "3", "3! / 2! = 3: 112, 121, 211."),
        _calc("How many combinations (reuse allowed, order ignored) of `2 3 5` sum to 8?",
              str(_c6_comb_sum_count([2, 3, 5], 8)), "{2, 2, 2, 2}, {2, 3, 3}, {3, 5}."),
        _calc("How many subsets of `3 1 4 2 5` sum to 6?", str(_c6_subsets_count([3, 1, 4, 2, 5], 6)),
              "{1, 5}, {4, 2}, {1, 3, 2}: three."),
        _calc("How many binary strings of length 5 have no two adjacent 1s?", "13",
              "The count follows Fibonacci: f(1) = 2, f(2) = 3, f(n) = f(n − 1) + f(n − 2): 2, 3, 5, 8, 13."),
        _calc("In how many ways can 6 queens be placed on a 6 × 6 board?", str(_c6_nqueens(6)),
              "Only four — fewer than for n = 5, which has 10."),
        _calc("How many proper 3-colourings does a path of 4 regions have?",
              str(_c6_colourings(4, [(0, 1), (1, 2), (2, 3)], 3)),
              "3 for the first region, then 2 for each next: 3 · 2³ = 24."),
        _calc("How many calls does the include/exclude subset recursion make for n = 10?",
              str(_c6_calls_subsets(10)), "A full binary tree with 2¹⁰ leaves: 2¹¹ − 1 calls."),
    ],
)


# ============================================================ graph traversal

_G_EDGES = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (5, 6)]
_G_N = 7
_G_DIST, _G_BFS = _c6_bfs(_G_N, _G_EDGES, 0)
_G_DFS = _c6_dfs_order(_G_N, _G_EDGES, 0)


def _c6_components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for u, v in edges:
        parent[find(u)] = find(v)
    return len({find(x) for x in range(n)})


def _c6_board(n, jumps):
    jump = dict(jumps)
    dist = [-1] * (n + 1)
    dist[1] = 0
    q = _dq([1])
    while q:
        s = q.popleft()
        for d in range(1, 7):
            if s + d > n:
                break
            t = jump.get(s + d, s + d)
            if dist[t] < 0:
                dist[t] = dist[s] + 1
                q.append(t)
    return dist[n]


_H6_GRAPH = dict(
    quizzes=[
        _quiz("bug", "On a large grid the BFS queue grows to millions and the run times out, though the answer is right. Why?",
              r"""
q.add(start);
while (!q.isEmpty()) {
    int[] c = q.poll();
    seen[c[0]][c[1]] = true;
    for (int[] d : DIRS) {
        int r = c[0] + d[0], k = c[1] + d[1];
        if (inside(r, k) && !seen[r][k] && open(r, k)) q.add(new int[]{r, k});
    }
}
""",
              "Cells are marked when popped, so each is queued once per neighbour; mark them when pushed",
              ["Cells are marked when popped, so each is queued once per neighbour; mark them when pushed",
               "ArrayDeque is too slow; use LinkedList",
               "DIRS should include diagonals",
               "The start cell is never marked, so the search loops"],
              """
Between being discovered and being popped, a cell can be discovered again by each of its
other neighbours — up to four copies of every cell in the queue. Marking on push makes the
first discovery the only one. (The start is marked when popped here, so it does not loop.)
"""),
        _quiz("bug", "This cycle check reports a cycle in the directed graph 0→1, 0→2, 1→2, which has none. Why?",
              r"""
boolean dfs(int u) {
    if (seen[u]) return true;               // seen before → cycle
    seen[u] = true;
    for (int v : adj[u]) if (dfs(v)) return true;
    return false;
}
""",
              "Two states cannot tell \"on the current path\" from \"finished\"; use three colours and only a grey neighbour is a cycle",
              ["Two states cannot tell \"on the current path\" from \"finished\"; use three colours and only a grey neighbour is a cycle",
               "It should unmark `seen[u]` before returning",
               "The graph must be made undirected first",
               "It must start the DFS from every vertex"],
              """
0 → 1 → 2 finishes 2; then 0 → 2 reaches a *finished* vertex, which is harmless (a forward
edge). Only an edge to a vertex still on the recursion stack closes a cycle. Unmarking on
return would fix correctness but make the search exponential.
"""),
        _quiz("predict", "BFS from 0 on the undirected graph 0-1, 0-2, 1-3, 2-3, 3-4, 5-6. What is dist[] (−1 unreachable)?",
              r"""
int[] dist = new int[7]; Arrays.fill(dist, -1);
dist[0] = 0; q.add(0);
while (!q.isEmpty()) { int u = q.poll();
    for (int v : adj[u]) if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); } }
""",
              " ".join(map(str, _G_DIST)),
              [" ".join(map(str, _G_DIST)), "0 1 1 2 3 0 0", "0 1 2 2 3 -1 -1", "0 1 1 3 4 -1 -1"],
              """
1 and 2 are one hop from 0, 3 is two (through either), 4 is three. 5 and 6 form a separate
component, so they stay −1 — not 0.
"""),
        _quiz("model", "A knight starts on one square of a chessboard with some blocked squares. Fewest moves to reach the target?",
              """
8 x 8 board, '#' = blocked
start (0, 0), target (7, 7)
""",
              "BFS: squares are vertices, the eight knight moves are edges",
              ["BFS: squares are vertices, the eight knight moves are edges",
               "Dijkstra with the knight's Manhattan distance as weights",
               "DFS, taking the first path found",
               "Union-find over reachable squares"],
              """
Every move costs one, so the fewest moves is an unweighted shortest path — BFS on the implicit
graph. DFS finds *a* path, not the shortest; union-find answers reachability, not distance.
"""),
        _quiz("model", "A maze has keys a–f and matching doors A–F. Fewest steps to collect all keys?",
              """
@..a.
###A#
b....
""",
              "BFS over states (cell, set of keys held), the set as a bitmask",
              ["BFS over states (cell, set of keys held), the set as a bitmask",
               "BFS over cells with one visited[][] array",
               "Dijkstra where doors cost more",
               "Try every order of keys, BFS between them, and take the best"],
              """
Standing in a cell with key a is a different situation from standing there without it, so the
visited set must include the keys — 2⁶ = 64 copies of the grid at most. Plain cell BFS forbids
the walk back through a cell after picking up a key. The key-order approach works (6! orders)
but is slower and harder to get right.
"""),
        _quiz("predict", "Board of 20 squares, shortcuts 3→15 and 17→4, die rolls 1–6. Fewest turns from 1 to 20?",
              r"""
// BFS over squares; landing on a shortcut's start moves you to its end
""",
              str(_c6_board(20, [(3, 15), (17, 4)])),
              [str(_c6_board(20, [(3, 15), (17, 4)])), "3", "4", "1"],
              """
Roll 2 (land on 3, ride to 15), then roll 5 to reach 20. Two turns. Avoiding 17 matters:
it would drop you back to 4.
"""),
    ],
    stuck=[
        _stuck("It talks about islands, regions, rooms or spreading",
               "What is a vertex, and which cells are its neighbours? Then it is BFS or DFS with a visited set."),
        _stuck("“Fewest moves / steps / turns”",
               "Does every move cost the same? Then BFS; the first time you reach the target is optimal."),
        _stuck("A plain BFS gives the wrong answer on some inputs",
               "Can the same cell be reached in two situations with different futures (keys, walls left, direction)? Add that to the state."),
        _stuck("Several starting points",
               "Could all of them start in the queue at distance 0 — one BFS instead of many?"),
        _stuck("A directed graph and “is there a cycle?”",
               "Two-state visited is not enough: which vertices are on the current recursion stack?"),
        _stuck("The graph is not given — only a rule for moving",
               "Generate neighbours when popping. How will you encode a state as an int or a string for the visited set?"),
    ],
    edge_cases=[
        _edge("bfs-levels", "Nobody else is reachable", "4 2\n1 2\n2 3\n", "Printing 0 instead of −1 for unreachable people."),
        _edge("bfs-levels", "Repeated friendships", "3 4\n0 1\n1 0\n1 2\n2 1\n", "Counting a repeated edge as a new hop."),
        _edge("bfs-levels", "One person", "1 0\n", "Reading edges that are not there."),
        _edge("board-game-fewest-rolls", "Two squares", "2 0\n", "Looping past square n."),
        _edge("board-game-fewest-rolls", "Every roll sends you back", "12 6\n2 1\n3 1\n4 1\n5 1\n6 1\n7 1\n",
              "Not returning −1 when square n is unreachable."),
        _edge("board-game-fewest-rolls", "A wall of six chutes", "40 7\n2 20\n21 3\n22 3\n23 3\n24 3\n25 3\n26 3\n",
              "Assuming the board can always be crossed: squares 21–26 all send you back, and no roll jumps six squares at once — −1."),
        _edge("grid-k-breaks", "k = 0 and the way is blocked", "2 2 0\n.#\n#.\n", "Allowing one wall anyway."),
        _edge("grid-k-breaks", "A detour versus one wall", "5 5 1\n.#...\n.#.#.\n.#.#.\n.#.#.\n...#.\n",
              "Visited per cell: the walled path marks cells the detour needs."),
        _edge("keys-and-doors-bfs", "A key behind its own door", "1 5\n@.A.a\n", "Walking through a locked door."),
        _edge("keys-and-doors-bfs", "Back and forth", "1 7\nb.A.@.a\n", "Visited per cell forbids walking back with the key."),
        _edge("keys-and-doors-bfs", "No keys at all", "1 3\n@..\n", "Returning −1 instead of 0."),
    ],
    walkthrough=_walk("keys-and-doors-bfs", "Collect every key", [
        """
A grid with a start, walls, up to six keys and their doors. Fewest steps until you hold every
key. Grids up to 30 × 30.
""",
        """
\"Fewest steps\" on a grid with unit moves is BFS (graph traversal). The twist — doors that open
only once a key is held — means the *situation*, not the cell, is the vertex: an augmented
state.
""",
        """
Try every order of keys (6! = 720), and BFS between consecutive keys with the doors you can
open by then. Correct, but it re-runs BFS thousands of times and gets fiddly (a BFS leg may
need to pick up a key it passes). Keep it as an oracle for tiny grids.
""",
        """
A state is (row, col, keys held). The keys held are a set of at most 6 — a 6-bit mask, so
at most 30 · 30 · 64 = 57,600 states. From a state, each of four moves:

- into a wall or off the grid: not allowed;
- into a door whose key bit is 0: not allowed;
- into a key: the mask gains that bit.

Every move costs one step, so BFS over states finds the fewest steps to *any* state whose
mask is full. The visited set is `seen[r][c][mask]`.
""",
        """
```java
int all = (1 << K) - 1;
boolean[][][] seen = new boolean[R][C][1 << K];
q.add(new int[]{sr, sc, 0}); seen[sr][sc][0] = true;
for (int steps = 0; !q.isEmpty(); steps++)
    for (int size = q.size(); size-- > 0; ) {
        int[] s = q.poll();
        if (s[2] == all) return steps;
        for (int[] d : DIRS) {
            int r = s[0] + d[0], c = s[1] + d[1];
            if (r < 0 || r >= R || c < 0 || c >= C || g[r][c] == '#') continue;
            char ch = g[r][c];
            if (ch >= 'A' && ch <= 'F' && ((s[2] >> (ch - 'A')) & 1) == 0) continue;
            int m = (ch >= 'a' && ch <= 'f') ? s[2] | 1 << (ch - 'a') : s[2];
            if (!seen[r][c][m]) { seen[r][c][m] = true; q.add(new int[]{r, c, m}); }
        }
    }
return -1;
```
""",
        """
| Grid | Expected | Catches |
| --- | --- | --- |
| `@..` | 0 | K = 0: the full mask is 0 at the start |
| `@a` | 1 | the pick-up bit |
| `@.A.a` | −1 | locked doors |
| `b.A.@.a` | 8 | revisiting cells with more keys |
| six keys and doors | — | the full 64-mask state space |

**Cost:** O(R · C · 2^K) time and memory — 57,600 states here.
""",
    ]),
    interview_script="""
### Say it out loud

- *"Every move costs one, so BFS; the first time I pop the target, that's the fewest moves."*
- *"I mark cells when I push them, not when I pop them, so nothing is queued twice."*
- *"Here the same cell can be reached with different keys, so my state is (cell, mask) —
  64 times the grid, which is still small."*
- *"O(V + E) time; for a grid that's O(rows · cols), and BFS avoids the recursion depth a
  DFS flood fill would hit on 10⁶ cells."*
""",
    lab=_lab("graph", """
Type an edge list (`u v`, or `u v w` for weighted) and pick an algorithm. The graph is drawn on
a circle; drag the step slider to watch the run — the current vertex, the finished ones, the
edges chosen so far (the BFS tree, the DFS tree), and the queue, stack and colours at that
moment. Try DFS on a directed graph with a cycle to see a back edge appear.
""", [
        ("BFS: distances", {"n": 7, "edges": "0 1\n0 2\n1 3\n2 3\n3 4\n5 6", "directed": "no", "source": 0, "algo": "bfs"}),
        ("DFS: a directed cycle", {"n": 6, "edges": "0 1\n1 2\n2 0\n1 3\n0 3\n4 3\n4 5", "directed": "yes", "source": 0, "algo": "dfs"}),
        ("DFS: an undirected tree", {"n": 6, "edges": "0 1\n0 2\n1 3\n1 4\n2 5", "directed": "no", "source": 0, "algo": "dfs"}),
        ("BFS on an odd cycle", {"n": 5, "edges": "0 1\n1 2\n2 3\n3 4\n4 0", "directed": "no", "source": 0, "algo": "bfs"}),
        ("Components by union-find", {"n": 8, "edges": "0 1\n2 3\n1 2\n4 5\n6 7\n5 4", "directed": "no", "source": 0, "algo": "dsu"}),
    ]),
    drills=[
        _calc("BFS from 0 on 0-1, 0-2, 1-3, 2-3, 3-4, 5-6 (adjacency in that order). Visit order?",
              " ".join(map(str, _G_BFS)), "0, then its neighbours 1 and 2, then 3 (found from 1), then 4."),
        _calc("Recursive DFS from 0 on the same graph (neighbours in edge order). Visit order?",
              " ".join(map(str, _G_DFS)), "0 → 1 → 3 → 2 (3's next unvisited neighbour) → back to 3 → 4."),
        _calc("How many connected components does that 7-vertex graph have?", str(_c6_components(_G_N, _G_EDGES)),
              "{0, 1, 2, 3, 4} and {5, 6}."),
        _calc("How many edges does an undirected graph with 6 vertices have at most (no loops, no repeats)?", "15",
              "C(6, 2) = 6 · 5 / 2 = 15."),
        _calc("A 4 × 5 grid: how many 4-neighbour edges does it have?", "31",
              "Horizontal 4 · 4 = 16, vertical 3 · 5 = 15."),
        _calc("Keys-and-doors with 5 keys on a 20 × 20 grid: how many states at most?", "12800",
              "20 · 20 · 2⁵ = 12,800.", accept=["12,800"]),
        _calc("A cycle of 7 vertices: is it bipartite? (yes / no)", "no",
              "An odd cycle cannot be two-coloured: going round, the colours must alternate an odd number of times."),
        _calc("Board of 30 squares, one shortcut 2 → 30. Fewest turns?", str(_c6_board(30, [(2, 30)])),
              "Roll 1 to land on 2 and ride straight to 30."),
        _calc("Rotting oranges: fresh cells at distances 1, 3, 3 and 4 from the nearest rotten one. Minutes until all rot?",
              "4", "Multi-source BFS: the answer is the largest distance."),
    ],
)
