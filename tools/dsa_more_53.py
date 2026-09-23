# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 53 — Trees & Graphs, part 1: binary trees.
#
#   leaf-similar-trees      two trees, one leaf sequence each — a traversal as a stream
#   vertical-order-tree     columns keyed by offset, ordered by (row, value)
#   tree-postorder-inorder  rebuild from post-order: the root is LAST, build right first
#   flatten-tree-to-list    re-wire in place into a pre-order chain, no extra list
#   max-ancestor-difference top-down: carry the min and max seen on the path
#   path-sum-list           backtracking on a tree: push, recurse, pop
#   boundary-of-tree        three walks glued together, with the leaf rule in each
#   sum-of-distances-tree   rerooting: one pass down for sizes, one pass for answers
#   tree-cameras            greedy post-order with three states
#
# Also defines the tree shapes the stage-6 batches share (`tree2`, `tree_out`,
# `post_in`, `arr_tree`, `tree_lohi_out`, `tree_keys_out`) and deterministic
# generators for random trees and graphs (`_Lcg`, `_rand_tree`, `_level_of`,
# `_rand_graph`), so hidden cases are stable across machines.
# ===========================================================================


class _Lcg:
    """The curriculum's fixed LCG, so generated cases never depend on Python's
    `random` implementation."""

    def __init__(self, seed):
        self.s = seed

    def next(self):
        self.s = (self.s * 1103515245 + 12345) % (1 << 31)
        return self.s

    def randint(self, lo, hi):
        # The high bits: an LCG modulo a power of two has short cycles in its
        # low bits, so `s % small` repeats far too soon.
        return lo + (self.next() >> 8) % (hi - lo + 1)

    def shuffle(self, a):
        for i in range(len(a) - 1, 0, -1):
            j = self.randint(0, i)
            a[i], a[j] = a[j], a[i]
        return a


def _rand_tree(n, rng, skew=0):
    """A random binary tree on nodes 0 .. n-1 with root 0, as (left, right)
    child arrays. `skew` > 0 prefers attaching to the most recent node, which
    makes deep trees."""
    left, right = [-1] * n, [-1] * n
    free = [(0, 0), (0, 1)]
    for i in range(1, n):
        if skew and rng.randint(1, 100) <= skew:
            k = len(free) - 1 - rng.randint(0, 1)
        else:
            k = rng.randint(0, len(free) - 1)
        p, side = free[k]
        free[k] = free[-1]
        free.pop()
        (left if side == 0 else right)[p] = i
        free.append((i, 0))
        free.append((i, 1))
    return left, right


def _level_of(vals, left, right, root=0):
    """Level-order encoding with `null`s, trailing nulls trimmed."""
    if root < 0:
        return "null"
    out, q, i = [], [root], 0
    while i < len(q):
        x = q[i]
        i += 1
        if x < 0:
            out.append("null")
            continue
        out.append(str(vals[x]))
        q.append(left[x])
        q.append(right[x])
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def _rand_tree_line(n, seed, lo, hi, skew=0, distinct=False):
    rng = _Lcg(seed)
    left, right = _rand_tree(n, rng, skew)
    if distinct:
        vals = rng.shuffle(list(range(lo, lo + n)))
    else:
        vals = [rng.randint(lo, hi) for _ in range(n)]
    return _level_of(vals, left, right)


def _chain_line(vals, side):
    """A tree that is a single path; `side` is 'L', 'R' or 'Z' (zig-zag)."""
    n = len(vals)
    left, right = [-1] * n, [-1] * n
    for i in range(n - 1):
        s = side if side != "Z" else ("L" if i % 2 == 0 else "R")
        (left if s == "L" else right)[i] = i + 1
    return _level_of(vals, left, right)


def _rand_tree_edges(n, rng):
    """A random unrooted tree on 0 .. n-1 as an edge list (random labels)."""
    perm = rng.shuffle(list(range(n)))
    edges = []
    for i in range(1, n):
        p = rng.randint(max(0, i - 1 - rng.randint(0, i - 1)), i - 1)
        a, b = perm[i], perm[p]
        edges.append((a, b) if rng.randint(0, 1) else (b, a))
    return rng.shuffle(edges)


def _rand_graph(n, m, rng, directed=False, wlo=None, whi=None, simple=True):
    """m random edges on 0 .. n-1 (no self-loops; no parallel edges if `simple`)."""
    seen, edges = set(), []
    tries = 0
    while len(edges) < m and tries < 50 * m + 100:
        tries += 1
        u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
        if u == v:
            continue
        key = (u, v) if directed else (min(u, v), max(u, v))
        if simple and key in seen:
            continue
        seen.add(key)
        if wlo is None:
            edges.append((u, v))
        else:
            edges.append((u, v, rng.randint(wlo, whi)))
    return edges


def _graph_case(n, edges, extra=""):
    """"n m" + edge lines (+ an optional trailing block)."""
    return (f"{n} {len(edges)}\n" + "".join(" ".join(map(str, e)) + "\n" for e in edges)
            + extra)


# ------------------------------------------------------------------ shapes

_LEVEL_PY = _TREE_CLASS_PY[_TREE_CLASS_PY.index("def level"):]
_LEVEL_JS = _TREE_CLASS_JS[_TREE_CLASS_JS.index("function level"):]
_LEVEL_JAVA = _TREE_CLASS_JAVA[_TREE_CLASS_JAVA.index("    static String level"):]

# two tree lines
_SHAPES["tree2"] = dict(
    py=_TREE_PY + "root2 = build(L[1].split() if len(L) > 1 else [])\n", py_params="root, root2",
    js=_TREE_JS + "const root2 = build((L[1] || '').trim().split(/\\s+/).filter(Boolean));\n",
    js_params="root, root2",
    java_members=_TREE_JAVA_MEMBERS,
    java=_TREE_JAVA_READ + '        TreeNode root2 = build(sc.hasNextLine() ? sc.nextLine() : "");\n',
    java_params="TreeNode root, TreeNode root2", java_args="root, root2",
)
# a tree line in, a tree out (printed in level order)
_SHAPES["tree_out"] = dict(
    py=_LEVEL_PY + "\n" + _TREE_PY, py_params="root",
    js=_TREE_JS + _LEVEL_JS, js_params="root",
    java_members=_TREE_JAVA_MEMBERS + "\n" + _LEVEL_JAVA, java=_TREE_JAVA_READ,
    java_params="TreeNode root", java_args="root", wrap="level",
)
# a tree line, then "lo hi"; a tree out
_SHAPES["tree_lohi_out"] = dict(
    py=_LEVEL_PY + "\n" + _TREE_PY + "lo, hi = map(int, L[1].split())\n", py_params="root, lo, hi",
    js=_TREE_JS + _LEVEL_JS + "const [lo, hi] = L[1].trim().split(/\\s+/).map(Number);\n",
    js_params="root, lo, hi",
    java_members=_TREE_JAVA_MEMBERS + "\n" + _LEVEL_JAVA,
    java=_TREE_JAVA_READ + "        int lo = sc.nextInt(), hi = sc.nextInt();\n",
    java_params="TreeNode root, int lo, int hi", java_args="root, lo, hi", wrap="level",
)
# a tree line, then k, then k keys on one line; a tree out
_SHAPES["tree_keys_out"] = dict(
    py=_LEVEL_PY + "\n" + _TREE_PY + "k = int(L[1])\nkeys = list(map(int, L[2].split()))[:k]\n",
    py_params="root, keys",
    js=_TREE_JS + _LEVEL_JS + "const k = Number(L[1]);\n"
       "const keys = L[2].trim().split(/\\s+/).map(Number).slice(0, k);\n",
    js_params="root, keys",
    java_members=_TREE_JAVA_MEMBERS + "\n" + _LEVEL_JAVA,
    java=_TREE_JAVA_READ + "        int k = Integer.parseInt(sc.nextLine().trim());\n"
         "        int[] keys = new int[k];\n        for (int i = 0; i < k; i++) keys[i] = sc.nextInt();\n",
    java_params="TreeNode root, int[] keys", java_args="root, keys", wrap="level",
)
# n, then the post-order, then the in-order; a tree out
_SHAPES["post_in"] = dict(
    py=_TREE_CLASS_PY + "\nd = list(map(int, sys.stdin.read().split()))\nn = d[0]\n"
       "post = d[1:1 + n]\nino = d[1 + n:1 + 2 * n]\n",
    py_params="post, ino",
    js=_TREE_CLASS_JS + _JS_NUMS + "const n = Number(d[0]);\n"
       "const post = d.slice(1, 1 + n).map(Number);\nconst ino = d.slice(1 + n, 1 + 2 * n).map(Number);\n",
    js_params="post, ino",
    java_members=_TREE_CLASS_JAVA,
    java="        int n = sc.nextInt();\n        int[] post = new int[n], ino = new int[n];\n"
         "        for (int i = 0; i < n; i++) post[i] = sc.nextInt();\n"
         "        for (int i = 0; i < n; i++) ino[i] = sc.nextInt();\n",
    java_params="int[] post, int[] ino", java_args="post, ino", wrap="level",
)
# n, then n integers; a tree out
_SHAPES["arr_tree"] = dict(
    py=_TREE_CLASS_PY + "\nd = sys.stdin.read().split()\nn = int(d[0])\na = list(map(int, d[1:1 + n]))\n",
    py_params="a",
    js=_TREE_CLASS_JS + _JS_NUMS + "const n = Number(d[0]);\nconst a = d.slice(1, 1 + n).map(Number);\n",
    js_params="a",
    java_members=_TREE_CLASS_JAVA,
    java="        int n = sc.nextInt();\n        int[] a = new int[n];\n"
         "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n",
    java_params="int[] a", java_args="a", wrap="level",
)


def _two_trees(a, b):
    return a + "\n" + b + "\n"


# ------------------------------------------------------------------ problems

_p(
    "leaf-similar-trees", "Same Leaves, Different Trees", "Easy",
    topics=["Tree"], subtopics=["Tree", "Depth-First Search"],
    companies=["Google", "Amazon"],
    shape="tree2", ret="String",
    todo="collect each tree's leaves left to right (a leaf has no children) and compare the two lists",
    description=(
        "Two gardeners each planted a binary tree. Reading a tree's **leaves** from left to right "
        "gives its *leaf sequence*. Print `true` if the two trees have the same leaf sequence, "
        "otherwise `false`. The shapes may be completely different.\n\n"
        "A leaf is a node with **no** children.\n\n"
        "### Input\nLine 1: the first tree in level order (`null` for a missing child).\n"
        "Line 2: the second tree, same encoding.\n\n### Output\n`true` or `false`."
    ),
    constraints="1 ≤ nodes in each tree ≤ 2000\n0 ≤ value ≤ 10^4",
    hints=[
        "Any depth-first order that visits the left subtree before the right one meets the leaves left to right.",
        "Collect each tree's leaves into a list, then compare the lists — including their lengths.",
        "Iteratively: push the right child before the left one so the left is popped first.",
    ],
    opt=("O(n1 + n2)", "O(n1 + n2)",
         "Each tree is walked once; the two leaf lists are stored and compared."),
    editorial=(
        "## The one thing this teaches\n**A traversal is a stream.** The question is not about "
        "shape at all: it is \"do two walks produce the same sequence of events?\" Any "
        "left-before-right depth-first walk emits the leaves in left-to-right order.\n\n"
        "## Approach\n```java\nstatic void leaves(TreeNode n, List<Integer> out) {\n"
        "    if (n == null) return;\n    if (n.left == null && n.right == null) { out.add(n.val); return; }\n"
        "    leaves(n.left, out);\n    leaves(n.right, out);\n}\n```\n"
        "Compare the two lists with `equals` — which also compares their lengths.\n\n"
        "## Follow-up\nWith two explicit stacks you can produce the leaves lazily, one at a time, "
        "and stop at the first mismatch: O(h) memory instead of O(leaves)."
    ),
    py='''
def solve(root, root2):
    def leaves(r):
        out, st = [], [r] if r else []
        while st:
            n = st.pop()
            if n.left is None and n.right is None:
                out.append(n.val)
            if n.right:
                st.append(n.right)
            if n.left:
                st.append(n.left)
        return out
    return "true" if leaves(root) == leaves(root2) else "false"
''',
    java='''
    static List<Integer> leaves(TreeNode r) {
        List<Integer> out = new ArrayList<>();
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        if (r != null) st.push(r);
        while (!st.isEmpty()) {
            TreeNode n = st.pop();
            if (n.left == null && n.right == null) out.add(n.val);
            if (n.right != null) st.push(n.right);
            if (n.left != null) st.push(n.left);
        }
        return out;
    }

    static String solve(TreeNode root, TreeNode root2) {
        return leaves(root).equals(leaves(root2)) ? "true" : "false";
    }
''',
    examples=[
        ("Example 1", _two_trees("5 2 8 1 3 null 9", "7 1 6 null null 3 9")),
        ("Example 2", _two_trees("4 2 6", "4 6 2")),
    ],
    hidden=[
        ("Single nodes, equal", _two_trees("3", "3")),
        ("Single nodes, different", _two_trees("3", "4")),
        ("One tree has an extra leaf", _two_trees("1 2 3", "1 2 3 null null 4 5")),
        ("Same leaves, a chain against a bush", _two_trees("9 8 null 7 null 6", "1 6")),
        ("Same multiset, different order", _two_trees("1 2 3 4 5", "1 2 3 5 4")),
        ("Large equal", _two_trees(_rand_tree_line(1500, 11, 0, 9), _rand_tree_line(1500, 11, 0, 9))),
        ("Large different", _two_trees(_rand_tree_line(1500, 12, 0, 9), _rand_tree_line(1500, 13, 0, 9))),
    ],
    expl=[
        "The first tree's leaves are 1, 3, 9; the second's are 1, 3, 9 as well: true.",
        "Leaves 2, 6 against 6, 2 — the same values in a different order: false.",
    ],
    prereqs=[
        ("tree_traversal", "A left-before-right depth-first walk meets the leaves in left-to-right order."),
        ("tree_basics", "A leaf has no children; a node with one child is not a leaf."),
    ],
)


_p(
    "vertical-order-tree", "Columns of a Tree", "Medium",
    topics=["Tree"], subtopics=["Tree", "Breadth-First Search", "Hash Map"],
    companies=["Meta", "Amazon", "Microsoft"],
    shape="tree", ret="String",
    todo="give the root column 0, left child col - 1, right child col + 1; group by column, order each by (depth, value)",
    description=(
        "Draw a binary tree on paper with the root in **column 0**; a left child sits one column "
        "to the left of its parent and a right child one column to the right. Every node is also "
        "on a **row** equal to its depth (the root is row 0).\n\n"
        "Print the columns from leftmost to rightmost, one per line. Within a column, list nodes "
        "top to bottom by row; nodes on the **same row and column** are listed by value, smallest "
        "first.\n\n"
        "### Input\nOne line: the tree in level order (`null` for a missing child).\n\n"
        "### Output\nOne line per column, values separated by spaces."
    ),
    constraints="1 ≤ nodes ≤ 3000\n-10^5 ≤ value ≤ 10^5",
    hints=[
        "Each node gets a (row, column) pair from its parent's: left is (r + 1, c − 1), right is (r + 1, c + 1).",
        "Collect (row, value) into a map from column to list. A TreeMap keeps the columns sorted for you.",
        "Sort each column's list by row, then by value. A BFS already visits rows in order, but not values within a row.",
    ],
    opt=("O(n log n)", "O(n)",
         "Every node is visited once; sorting the columns costs n log n in total."),
    editorial=(
        "## The one thing this teaches\n**A tree walk can carry coordinates.** Nothing about "
        "columns is stored in the tree. The parent hands each child its position — a top-down "
        "parameter — and a map groups nodes by one coordinate.\n\n"
        "## Approach\n```java\nTreeMap<Integer, List<int[]>> cols = new TreeMap<>();   // col -> (row, value)\n"
        "// BFS carrying (node, row, col)\ncols.computeIfAbsent(col, k -> new ArrayList<>()).add(new int[]{row, n.val});\n"
        "if (n.left != null)  push(n.left,  row + 1, col - 1);\nif (n.right != null) push(n.right, row + 1, col + 1);\n"
        "// then sort each column by row, then value\n```\n\n"
        "## The tie rule is the problem\nTwo nodes can share a row *and* a column (a left-right "
        "grandchild and a right-left grandchild both land on column 0, row 2). BFS order alone "
        "would list them by who was reached first; the statement asks for value order, so sort."
    ),
    py='''
def solve(root):
    cols = defaultdict(list)
    q = deque([(root, 0, 0)])
    while q:
        node, r, c = q.popleft()
        cols[c].append((r, node.val))
        if node.left:
            q.append((node.left, r + 1, c - 1))
        if node.right:
            q.append((node.right, r + 1, c + 1))
    return "\\n".join(" ".join(str(v) for _, v in sorted(cols[c])) for c in sorted(cols))
''',
    java='''
    static String solve(TreeNode root) {
        TreeMap<Integer, List<int[]>> cols = new TreeMap<>();
        ArrayDeque<TreeNode> qn = new ArrayDeque<>();
        ArrayDeque<int[]> qp = new ArrayDeque<>();
        qn.add(root);
        qp.add(new int[]{0, 0});
        while (!qn.isEmpty()) {
            TreeNode n = qn.poll();
            int[] p = qp.poll();
            cols.computeIfAbsent(p[1], k -> new ArrayList<>()).add(new int[]{p[0], n.val});
            if (n.left != null) { qn.add(n.left); qp.add(new int[]{p[0] + 1, p[1] - 1}); }
            if (n.right != null) { qn.add(n.right); qp.add(new int[]{p[0] + 1, p[1] + 1}); }
        }
        StringBuilder sb = new StringBuilder();
        for (List<int[]> col : cols.values()) {
            col.sort((a, b) -> a[0] != b[0] ? Integer.compare(a[0], b[0]) : Integer.compare(a[1], b[1]));
            if (sb.length() > 0) sb.append('\\n');
            for (int i = 0; i < col.size(); i++) {
                if (i > 0) sb.append(' ');
                sb.append(col.get(i)[1]);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "10 4 16 null 7 12 20\n"),
        ("Example 2", "1 2 3 4 6 5 7\n"),
    ],
    hidden=[
        ("One node", "42\n"),
        ("Left chain", _chain_line([5, 4, 3, 2, 1], "L") + "\n"),
        ("Zig-zag", _chain_line([1, 2, 3, 4, 5, 6], "Z") + "\n"),
        ("Tie broken by value", "0 1 2 3 9 8 4\n"),
        ("Negative values", "-1 -2 -3 -4 -5 -6 -7\n"),
        ("Random", _rand_tree_line(60, 21, -50, 50) + "\n"),
        ("Large", _rand_tree_line(3000, 22, -100000, 100000) + "\n"),
    ],
    expl=[
        "Columns −1: 4; 0: 10, 7, 12 (7 and 12 share row 2, so by value); 1: 16; 2: 20.",
        "Column 0 holds 1 (row 0), then 6 and 5 on row 2 — listed by value as 5 6.",
    ],
    prereqs=[
        ("tree_traversal", "A BFS (or DFS) that carries each node's row and column down from its parent."),
        ("hashing", "Group nodes by column in a map; a TreeMap keeps the columns in order."),
    ],
)


def _post_in_case(n, seed, skew=0):
    rng = _Lcg(seed)
    left, right = _rand_tree(n, rng, skew)
    vals = rng.shuffle(list(range(1, n + 1)))
    post, ino = [], []

    def walk(x):  # iterative to stay safe on deep trees
        st = [(x, 0)]
        while st:
            y, s = st.pop()
            if y < 0:
                continue
            if s == 0:
                st.append((y, 1))
                st.append((left[y], 0))
            elif s == 1:
                ino.append(vals[y])
                st.append((y, 2))
                st.append((right[y], 0))
            else:
                post.append(vals[y])

    walk(0)
    return f"{n}\n{' '.join(map(str, post))}\n{' '.join(map(str, ino))}\n"


_p(
    "tree-postorder-inorder", "Rebuild From the Last Visit", "Medium",
    topics=["Tree"], subtopics=["Tree", "Recursion", "Divide and Conquer"],
    companies=["Microsoft", "Amazon", "Bloomberg"],
    shape="post_in", ret="TreeNode",
    todo="the last post-order value is the root; its in-order position splits the rest — build the RIGHT subtree first",
    description=(
        "A binary tree with **distinct** values was walked twice: once in **post-order** "
        "(left, right, root) and once in **in-order** (left, root, right). Rebuild the tree and "
        "print it in level order.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the post-order (`n` values).\nLine 3: the in-order "
        "(`n` values).\n\n### Output\nThe tree in level order, `null` for a missing child, trailing "
        "`null`s removed."
    ),
    constraints="1 ≤ n ≤ 3000\nValues are distinct, 0 ≤ value ≤ 10^5\nThe two orders describe the same tree.",
    hints=[
        "The root is the **last** value of the post-order.",
        "Its position in the in-order splits the in-order into the left subtree (before) and the right subtree (after).",
        "Consume the post-order from the back: after the root come the right subtree's values, then the left's — so build right first. A value → index map makes each split O(1).",
    ],
    opt=("O(n)", "O(n)",
         "One map lookup per node; the recursion is as deep as the tree."),
    editorial=(
        "## The one thing this teaches\n**Which end the root is on decides the build order.** "
        "Pre-order is root, left, right, so a shared index walking forward builds left first. "
        "Post-order is left, right, root — read it *backwards* and it is root, right, left, so the "
        "right subtree must be built first.\n\n"
        "## Approach\n```java\nint idx = n - 1;                          // walks the post-order backwards\n"
        "TreeNode build(int lo, int hi) {           // in-order range\n    if (lo > hi) return null;\n"
        "    TreeNode root = new TreeNode(post[idx--]);\n    int m = pos.get(root.val);\n"
        "    root.right = build(m + 1, hi);         // RIGHT first\n    root.left = build(lo, m - 1);\n"
        "    return root;\n}\n```\n\n"
        "## The classic bug\nBuilding left first with a backwards index hands the left subtree the "
        "right subtree's values. It still produces *a* tree — just not this one."
    ),
    py='''
def solve(post, ino):
    sys.setrecursionlimit(20000)
    pos = {v: i for i, v in enumerate(ino)}
    idx = [len(post) - 1]

    def build(lo, hi):
        if lo > hi:
            return None
        v = post[idx[0]]
        idx[0] -= 1
        node = TreeNode(v)
        m = pos[v]
        node.right = build(m + 1, hi)
        node.left = build(lo, m - 1)
        return node

    return build(0, len(ino) - 1)
''',
    java='''
    static int idx;
    static int[] P;
    static Map<Integer, Integer> pos = new HashMap<>();

    static TreeNode build(int lo, int hi) {
        if (lo > hi) return null;
        TreeNode root = new TreeNode(P[idx--]);
        int m = pos.get(root.val);
        root.right = build(m + 1, hi);
        root.left = build(lo, m - 1);
        return root;
    }

    static TreeNode solve(int[] post, int[] ino) {
        P = post;
        idx = post.length - 1;
        for (int i = 0; i < ino.length; i++) pos.put(ino[i], i);
        return build(0, ino.length - 1);
    }
''',
    examples=[
        ("Example 1", "5\n2 6 5 9 7\n2 7 5 6 9\n"),
        ("Example 2", "3\n3 2 1\n1 2 3\n"),
    ],
    hidden=[
        ("One node", "1\n4\n4\n"),
        ("Left chain", "4\n1 2 3 4\n1 2 3 4\n"),
        ("Right chain", "4\n4 3 2 1\n1 2 3 4\n"),
        ("Full tree", "7\n1 3 2 5 7 6 4\n1 2 3 4 5 6 7\n"),
        ("Random", _post_in_case(40, 31)),
        ("Deep", _post_in_case(2500, 32, skew=90)),
        ("Large", _post_in_case(3000, 33)),
    ],
    expl=[
        "7 is last, so it is the root; in-order puts 2 left of it and 5 6 9 right. 9 is the right subtree's root, and so on.",
        "Each value is its predecessor's right child: a right-leaning chain 1 → 2 → 3.",
    ],
    prereqs=[
        ("tree_traversal", "Post-order visits the root last; in-order puts it between its subtrees."),
        ("recursion", "Build a subtree from a range of the in-order, recursing on both sides."),
    ],
)


_p(
    "flatten-tree-to-list", "Flatten a Tree Into a Chain", "Medium",
    topics=["Tree", "Linked List"], subtopics=["Tree", "In-Place", "Pre-order"],
    companies=["Meta", "Microsoft", "Amazon"],
    shape="tree_out", ret="TreeNode",
    todo="for each node with a left child, splice the left subtree between the node and its right subtree (rightmost of left -> old right)",
    description=(
        "Re-wire a binary tree **in place** into a chain: every node's `left` becomes `null`, and "
        "following `right` pointers from the root visits the nodes in **pre-order** (root, left "
        "subtree, right subtree).\n\n"
        "Print the resulting tree in level order — so the output is the chain, with a `null` for "
        "each empty `left`.\n\n"
        "### Input\nOne line: the tree in level order (`null` for a missing child).\n\n"
        "### Output\nThe flattened tree in level order, trailing `null`s removed."
    ),
    constraints="1 ≤ nodes ≤ 3000\n-10^4 ≤ value ≤ 10^4",
    hints=[
        "The easy version: collect the pre-order into a list, then re-link. That uses O(n) extra memory — try to avoid it.",
        "For a node with a left child: find the rightmost node of the left subtree. The old right subtree comes right after it in pre-order.",
        "So: rightmost.right = node.right; node.right = node.left; node.left = null; then move to node.right. Each edge is walked a constant number of times.",
    ],
    opt=("O(n)", "O(1)",
         "The splice walks each left subtree's right spine; every node is on at most one such walk as it is spliced."),
    editorial=(
        "## The one thing this teaches\n**Pre-order is root, left, right — and the only thing out "
        "of place is the left subtree.** If the left subtree is already a chain, inserting it "
        "between the node and its right subtree is three pointer writes.\n\n"
        "## Approach (O(1) extra space)\n```java\nTreeNode cur = root;\nwhile (cur != null) {\n"
        "    if (cur.left != null) {\n        TreeNode p = cur.left;\n        while (p.right != null) p = p.right;   // pre-order predecessor of cur.right\n"
        "        p.right = cur.right;\n        cur.right = cur.left;\n        cur.left = null;\n    }\n"
        "    cur = cur.right;\n}\n```\n\n"
        "This is the same splice Morris traversal uses — it just never undoes it.\n\n"
        "## Why it is linear\nThe inner walk goes down the right spine of `cur.left`. Once spliced, "
        "those nodes are behind `cur` on the chain and are never the start of another inner walk."
    ),
    py='''
def solve(root):
    cur = root
    while cur:
        if cur.left:
            p = cur.left
            while p.right:
                p = p.right
            p.right = cur.right
            cur.right = cur.left
            cur.left = None
        cur = cur.right
    return root
''',
    java='''
    static TreeNode solve(TreeNode root) {
        TreeNode cur = root;
        while (cur != null) {
            if (cur.left != null) {
                TreeNode p = cur.left;
                while (p.right != null) p = p.right;
                p.right = cur.right;
                cur.right = cur.left;
                cur.left = null;
            }
            cur = cur.right;
        }
        return root;
    }
''',
    examples=[
        ("Example 1", "4 7 2 9 1 null 3\n"),
        ("Example 2", "7 null 8\n"),
    ],
    hidden=[
        ("One node", "3\n"),
        ("Left chain", _chain_line([1, 2, 3, 4], "L") + "\n"),
        ("Zig-zag", _chain_line([1, 2, 3, 4, 5], "Z") + "\n"),
        ("Full", "1 2 3 4 5 6 7\n"),
        ("Random", _rand_tree_line(50, 41, -9, 9) + "\n"),
        ("Large", _rand_tree_line(3000, 42, -10000, 10000) + "\n"),
    ],
    expl=[
        "Pre-order is 4 7 9 1 2 3, so the chain is 4 → 7 → 9 → 1 → 2 → 3 along right pointers.",
        "Already a chain with no left children: unchanged.",
    ],
    prereqs=[
        ("tree_traversal", "Pre-order: the node, then its whole left subtree, then its right subtree."),
        ("list_basics", "Re-linking pointers in place, like splicing a linked list."),
    ],
)


_p(
    "max-ancestor-difference", "Widest Family Gap", "Medium",
    topics=["Tree"], subtopics=["Tree", "Depth-First Search", "Top-Down"],
    companies=["Amazon", "Meta"],
    shape="tree", ret="int",
    todo="walk down carrying the smallest and largest value on the path from the root; the answer is the largest hi - lo seen",
    description=(
        "In a family tree, every node holds an age. For any node `a` and any node `d` below it "
        "(a descendant — a child, grandchild, …), the **gap** is `|a.val − d.val|`. Print the "
        "largest gap in the tree. A tree with one node has no pairs: print `0`.\n\n"
        "### Input\nOne line: the tree in level order (`null` for a missing child).\n\n"
        "### Output\nThe largest gap."
    ),
    constraints="1 ≤ nodes ≤ 3000\n-10^5 ≤ value ≤ 10^5",
    hints=[
        "For a fixed descendant d, the best ancestor is either the smallest or the largest value on its root path.",
        "So carry (min, max) of the path down the tree — a top-down parameter.",
        "At every node, update min and max with its value; the path's max − min is a candidate answer.",
    ],
    opt=("O(n)", "O(h)",
         "One visit per node; the explicit stack (or recursion) holds one root path."),
    editorial=(
        "## The one thing this teaches\n**Carry what the parent knew.** Comparing every ancestor "
        "with every descendant is O(n · h). But the only ancestors that can win are the extremes "
        "of the path — so pass the path's min and max down instead of the path itself.\n\n"
        "## Approach\n```java\nstatic int best(TreeNode n, int lo, int hi) {\n    if (n == null) return hi - lo;\n"
        "    lo = Math.min(lo, n.val);\n    hi = Math.max(hi, n.val);\n"
        "    return Math.max(best(n.left, lo, hi), best(n.right, lo, hi));\n}\n"
        "// best(root, root.val, root.val)\n```\n\n"
        "## Why hi − lo is enough\nThe min and the max on one root path are an ancestor and a "
        "descendant of each other (one path is a chain), so their difference is a real gap."
    ),
    py='''
def solve(root):
    best = 0
    st = [(root, root.val, root.val)]
    while st:
        n, lo, hi = st.pop()
        lo, hi = min(lo, n.val), max(hi, n.val)
        best = max(best, hi - lo)
        if n.left:
            st.append((n.left, lo, hi))
        if n.right:
            st.append((n.right, lo, hi))
    return best
''',
    java='''
    static int solve(TreeNode root) {
        int best = 0;
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        ArrayDeque<int[]> bounds = new ArrayDeque<>();
        st.push(root);
        bounds.push(new int[]{root.val, root.val});
        while (!st.isEmpty()) {
            TreeNode n = st.pop();
            int[] b = bounds.pop();
            int lo = Math.min(b[0], n.val), hi = Math.max(b[1], n.val);
            best = Math.max(best, hi - lo);
            if (n.left != null) { st.push(n.left); bounds.push(new int[]{lo, hi}); }
            if (n.right != null) { st.push(n.right); bounds.push(new int[]{lo, hi}); }
        }
        return best;
    }
''',
    examples=[
        ("Example 1", "9 4 12 2 7 null 15 null null 5 8 11\n"),
        ("Example 2", "4 null 6 null 1 3\n"),
    ],
    hidden=[
        ("One node", "5\n"),
        ("Siblings do not count", "50 0 100\n"),
        ("Gap at the bottom", _chain_line([0, 1, 2, 3, -100000], "R") + "\n"),
        ("All equal", "7 7 7 7 7\n"),
        ("Negatives", "-5 -100000 100000\n"),
        ("Random", _rand_tree_line(80, 51, -1000, 1000) + "\n"),
        ("Deep", _rand_tree_line(3000, 52, -100000, 100000, skew=95) + "\n"),
    ],
    expl=[
        "9 is an ancestor of 2: |9 − 2| = 7. No ancestor–descendant pair differs by more.",
        "The path 4 → 6 → 1 → 3 has min 1 and max 6: the gap is 5.",
    ],
    prereqs=[
        ("tree_traversal", "A top-down walk that passes the path's min and max to each child."),
        ("tree_basics", "Ancestors are the nodes on the path from the root."),
    ],
)


_p(
    "path-sum-list", "Every Road That Adds Up", "Medium",
    topics=["Tree", "Backtracking"], subtopics=["Tree", "Backtracking", "Depth-First Search"],
    companies=["Amazon", "Meta", "Bloomberg"],
    shape="tree_k", ret="String",
    todo="DFS with a shared path list: push the node, recurse into both children, pop; record a copy at a leaf whose sum is k",
    description=(
        "List every **root-to-leaf** path whose values add up to exactly `k`. Print one path per "
        "line (values separated by spaces), in left-to-right order of their leaves. If there are "
        "none, print `NONE`.\n\n"
        "Values may be negative, so a path that has already passed `k` can still come back.\n\n"
        "### Input\nLine 1: the tree in level order (`null` for a missing child).\nLine 2: `k`.\n\n"
        "### Output\nThe paths, or `NONE`."
    ),
    constraints="1 ≤ nodes ≤ 2000\n-1000 ≤ value ≤ 1000\n-10^6 ≤ k ≤ 10^6",
    hints=[
        "This is `path-sum-exists`, except you must remember the path — so keep one list and push/pop around the recursion.",
        "Check the sum only at a leaf (no children). A node with one child is not the end of a path.",
        "Record a *copy* (or a joined string) of the path: the list keeps changing after you record it.",
    ],
    opt=("O(n · h)", "O(h)",
         "Each node is visited once; each recorded path costs up to h to copy out."),
    editorial=(
        "## The one thing this teaches\n**Backtracking on a structure that already exists.** "
        "The tree fixes the choices; the shared `path` list is the only state, and every "
        "`add` needs a mirror `remove` on the way out.\n\n"
        "## Approach\n```java\nvoid dfs(TreeNode n, int rem) {\n    if (n == null) return;\n"
        "    path.add(n.val);                            // choose\n    rem -= n.val;\n"
        "    if (n.left == null && n.right == null) {\n        if (rem == 0) out.add(join(path));       // record a copy\n"
        "    } else {\n        dfs(n.left, rem);\n        dfs(n.right, rem);\n    }\n"
        "    path.remove(path.size() - 1);               // un-choose\n}\n```\n\n"
        "## No pruning here\nWith negative values a running sum above `k` can still fall back to it, "
        "so a `if (rem < 0) return;` cut would lose answers — a rule that only holds for "
        "non-negative inputs."
    ),
    py='''
def solve(root, k):
    sys.setrecursionlimit(20000)
    out, path = [], []

    def dfs(n, rem):
        if n is None:
            return
        path.append(n.val)
        rem -= n.val
        if n.left is None and n.right is None:
            if rem == 0:
                out.append(" ".join(map(str, path)))
        else:
            dfs(n.left, rem)
            dfs(n.right, rem)
        path.pop()

    dfs(root, k)
    return "\\n".join(out) if out else "NONE"
''',
    java='''
    static List<Integer> path = new ArrayList<>();
    static StringBuilder out = new StringBuilder();

    static void dfs(TreeNode n, int rem) {
        if (n == null) return;
        path.add(n.val);
        rem -= n.val;
        if (n.left == null && n.right == null) {
            if (rem == 0) {
                if (out.length() > 0) out.append('\\n');
                for (int i = 0; i < path.size(); i++) {
                    if (i > 0) out.append(' ');
                    out.append(path.get(i));
                }
            }
        } else {
            dfs(n.left, rem);
            dfs(n.right, rem);
        }
        path.remove(path.size() - 1);
    }

    static String solve(TreeNode root, int k) {
        dfs(root, k);
        return out.length() == 0 ? "NONE" : out.toString();
    }
''',
    examples=[
        ("Example 1", "6 3 9 2 4 null 1 1 null 3\n16\n"),
        ("Example 2", "1 2 3\n5\n"),
    ],
    hidden=[
        ("One node, match", "-4\n-4\n"),
        ("One node, no match", "4\n5\n"),
        ("A one-child node is not a leaf", "5 2\n5\n"),
        ("Negative detour", "1 -2 3 4 null null null 3\n6\n"),
        ("Many zero paths", "0 0 0 0 0 0 0\n0\n"),
        ("Random", _rand_tree_line(200, 61, -3, 3) + "\n2\n"),
        ("Deep", _rand_tree_line(2000, 62, -2, 2, skew=95) + "\n0\n"),
    ],
    expl=[
        "6 → 3 → 4 → 3 and 6 → 9 → 1 both add up to 16; the third path, 6 → 3 → 2 → 1, adds up to 12.",
        "The root-to-leaf sums are 3 and 4; neither is 5.",
    ],
    prereqs=[
        ("backtracking", "Push before the recursive calls, pop after — the path is shared state."),
        ("tree_traversal", "Root-to-leaf paths, and what counts as a leaf."),
    ],
)


_p(
    "boundary-of-tree", "Walk the Outline", "Medium",
    topics=["Tree"], subtopics=["Tree", "Depth-First Search"],
    companies=["Amazon", "Microsoft", "Google"],
    shape="tree", ret="String",
    todo="root, then the left boundary without leaves, then every leaf left to right, then the right boundary bottom-up without leaves",
    description=(
        "Print a binary tree's **outline**, counter-clockwise from the root:\n\n"
        "1. The root.\n2. The **left boundary**: start at the root's left child and repeatedly "
        "step to the left child, or to the right child when there is no left one. Stop *before* a "
        "leaf. (Empty if the root has no left child.)\n3. Every **leaf**, left to right.\n"
        "4. The **right boundary**: start at the root's right child and repeatedly step to the "
        "right child, or the left when there is no right one; stop before a leaf, and print it "
        "**bottom-up**. (Empty if the root has no right child.)\n\n"
        "A leaf has no children. The root is never counted as a leaf, so a one-node tree prints "
        "just the root.\n\n"
        "### Input\nOne line: the tree in level order (`null` for a missing child).\n\n"
        "### Output\nThe outline, values separated by spaces."
    ),
    constraints="1 ≤ nodes ≤ 3000\n-10^4 ≤ value ≤ 10^4",
    hints=[
        "Do it as three separate walks and concatenate: left boundary, leaves, right boundary reversed.",
        "Each boundary walk is a loop, not a recursion: take the preferred child if it exists, else the other one.",
        "The leaf rule is in all three walks: boundary walks stop before a leaf, and the leaf walk is the only place leaves are printed. That is what stops a node being printed twice.",
    ],
    opt=("O(n)", "O(h)",
         "The leaf walk visits every node; the boundary walks are each one root-to-leaf path."),
    editorial=(
        "## The one thing this teaches\n**Split a messy walk into clean ones.** One clever "
        "traversal that prints the outline is easy to get wrong; three simple walks, each with "
        "one rule, are easy to get right.\n\n"
        "## Approach\n```java\nout.add(root.val);\nif (isLeaf(root)) return;\n"
        "for (TreeNode n = root.left; n != null && !isLeaf(n); n = n.left != null ? n.left : n.right)\n"
        "    out.add(n.val);                       // left boundary, top-down\n"
        "addLeaves(root);                         // left-to-right DFS, leaves only (not the root)\n"
        "List<Integer> right = new ArrayList<>();\n"
        "for (TreeNode n = root.right; n != null && !isLeaf(n); n = n.right != null ? n.right : n.left)\n"
        "    right.add(n.val);\nCollections.reverse(right);             // bottom-up\nout.addAll(right);\n```\n\n"
        "## The double-count traps\nA leaf at the end of the left boundary, a root with one child, "
        "and a one-node tree: each is handled by \"boundaries stop before leaves\" and \"the root "
        "is not a leaf\"."
    ),
    py='''
def solve(root):
    def leaf(n):
        return n.left is None and n.right is None
    if leaf(root):
        return str(root.val)
    out = [root.val]
    n = root.left
    while n and not leaf(n):
        out.append(n.val)
        n = n.left if n.left else n.right
    st, leaves = [root], []
    while st:
        x = st.pop()
        if leaf(x):
            leaves.append(x.val)
        if x.right:
            st.append(x.right)
        if x.left:
            st.append(x.left)
    out += leaves
    right, n = [], root.right
    while n and not leaf(n):
        right.append(n.val)
        n = n.right if n.right else n.left
    out += reversed(right)
    return " ".join(map(str, out))
''',
    java='''
    static boolean leaf(TreeNode n) { return n.left == null && n.right == null; }

    static String solve(TreeNode root) {
        if (leaf(root)) return String.valueOf(root.val);
        List<Integer> out = new ArrayList<>();
        out.add(root.val);
        for (TreeNode n = root.left; n != null && !leaf(n); n = n.left != null ? n.left : n.right)
            out.add(n.val);
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        st.push(root);
        while (!st.isEmpty()) {
            TreeNode x = st.pop();
            if (leaf(x)) out.add(x.val);
            if (x.right != null) st.push(x.right);
            if (x.left != null) st.push(x.left);
        }
        List<Integer> right = new ArrayList<>();
        for (TreeNode n = root.right; n != null && !leaf(n); n = n.right != null ? n.right : n.left)
            right.add(n.val);
        Collections.reverse(right);
        out.addAll(right);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < out.size(); i++) {
            if (i > 0) sb.append(' ');
            sb.append(out.get(i));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "20 11 30 3 14 25 null null null 12 16 22 27\n"),
        ("Example 2", "5 null 8 6 9\n"),
    ],
    hidden=[
        ("One node", "9\n"),
        ("Root and one leaf", "1 2\n"),
        ("Left chain", _chain_line([1, 2, 3, 4], "L") + "\n"),
        ("Right chain", _chain_line([1, 2, 3, 4], "R") + "\n"),
        ("Zig-zag", _chain_line([1, 2, 3, 4, 5, 6], "Z") + "\n"),
        ("Full", "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n"),
        ("Random", _rand_tree_line(100, 71, -99, 99) + "\n"),
        ("Large", _rand_tree_line(3000, 72, -10000, 10000) + "\n"),
    ],
    expl=[
        "Root 20; left boundary 11 (it stops before the leaf 3); leaves 3 12 16 22 27; right boundary 30, 25 read bottom-up as 25 30.",
        "No left child, so no left boundary; leaves 6 9; the right boundary is just 8.",
    ],
    prereqs=[
        ("tree_traversal", "A left-to-right DFS that emits only the leaves."),
        ("tree_basics", "What a leaf is, and why the root is treated separately."),
    ],
)


_p(
    "sum-of-distances-tree", "Total Travel From Every Town", "Hard",
    topics=["Tree", "Dynamic Programming"], subtopics=["Tree", "Rerooting", "Tree DP"],
    companies=["Google", "Amazon"],
    shape="graph", ret="String",
    todo="root at 0: compute subtree sizes and the sum from 0 bottom-up; then ans[child] = ans[parent] - size[child] + (n - size[child])",
    description=(
        "`n` towns are joined by `n − 1` roads into a tree (every town reachable, no loops). "
        "Every road is one unit long. For **every** town, print the sum of its distances to all "
        "other towns.\n\n"
        "### Input\nLine 1: `n m` with `m = n − 1`.\nNext `m` lines: `u v`, a road between towns "
        "`u` and `v` (0-indexed).\n\n### Output\n`n` numbers on one line: the sums for towns "
        "0, 1, …, n − 1."
    ),
    constraints="1 ≤ n ≤ 10^5\nm = n − 1, and the roads form a tree.",
    hints=[
        "One BFS per town is O(n²). Try to get every answer from a neighbour's answer instead.",
        "Root the tree at 0. With size[v] = the number of towns in v's subtree, the sum for 0 is a bottom-up DP: down[p] += down[c] + size[c].",
        "Moving from a parent p to a child c: the size[c] towns in c's subtree get 1 closer, the other n − size[c] get 1 farther. So ans[c] = ans[p] − size[c] + (n − size[c]).",
    ],
    opt=("O(n)", "O(n)",
         "Two passes over a BFS order — one bottom-up, one top-down."),
    editorial=(
        "## The one thing this teaches\n**Rerooting.** Some tree questions ask for an answer *at "
        "every node as if it were the root*. Solving it once is a normal tree DP; the trick is "
        "that moving the root across one edge changes the answer by a formula, so all n answers "
        "cost one more pass.\n\n"
        "## Pass 1 — root at 0, bottom-up\n`size[v]` counts v's subtree. `down[v]` is the sum of "
        "distances from v to its subtree: `down[p] = Σ (down[c] + size[c])` — every node below c is "
        "one step farther from p than from c.\n\n"
        "## Pass 2 — top-down\n`ans[0] = down[0]`. For a child c of p:\n\n"
        "```\nans[c] = ans[p] − size[c] + (n − size[c])\n```\n\n"
        "## Iterative, because n = 10⁵\nA path-shaped tree is 10⁵ deep. Take a BFS order once, "
        "run pass 1 over it backwards and pass 2 forwards — no recursion at all. Sums reach "
        "about n²/2 = 5·10⁹: use `long`."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    seen = [False] * n
    seen[0] = True
    order = [0]
    for u in order:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                order.append(v)
    size = [1] * n
    down = [0] * n
    for u in reversed(order):
        p = parent[u]
        if p >= 0:
            size[p] += size[u]
            down[p] += down[u] + size[u]
    ans = [0] * n
    ans[0] = down[0]
    for u in order[1:]:
        ans[u] = ans[parent[u]] - size[u] + (n - size[u])
    return " ".join(map(str, ans))
''',
    java='''
    static String solve(int n, int[][] edges) {
        int[] deg = new int[n];
        for (int[] e : edges) { deg[e[0]]++; deg[e[1]]++; }
        int[][] adj = new int[n][];
        for (int i = 0; i < n; i++) adj[i] = new int[deg[i]];
        int[] fill = new int[n];
        for (int[] e : edges) { adj[e[0]][fill[e[0]]++] = e[1]; adj[e[1]][fill[e[1]]++] = e[0]; }
        int[] parent = new int[n], order = new int[n];
        Arrays.fill(parent, -1);
        boolean[] seen = new boolean[n];
        seen[0] = true;
        int head = 0, tail = 0;
        order[tail++] = 0;
        while (head < tail) {
            int u = order[head++];
            for (int v : adj[u]) if (!seen[v]) { seen[v] = true; parent[v] = u; order[tail++] = v; }
        }
        long[] size = new long[n], down = new long[n], ans = new long[n];
        Arrays.fill(size, 1);
        for (int i = n - 1; i >= 1; i--) {
            int u = order[i], p = parent[u];
            size[p] += size[u];
            down[p] += down[u] + size[u];
        }
        ans[0] = down[0];
        for (int i = 1; i < n; i++) {
            int u = order[i];
            ans[u] = ans[parent[u]] - size[u] + (n - size[u]);
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(ans[i]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _graph_case(5, [(0, 1), (0, 2), (2, 3), (2, 4)])),
        ("Example 2", _graph_case(2, [(1, 0)])),
    ],
    hidden=[
        ("One town", "1 0\n"),
        ("A path", _graph_case(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])),
        ("A star", _graph_case(6, [(3, 0), (3, 1), (3, 2), (3, 4), (3, 5)])),
        ("Random", _graph_case(40, _rand_tree_edges(40, _Lcg(81)))),
        ("Long path", _graph_case(20000, [(i, i + 1) for i in range(19999)])),
        ("Large random", _graph_case(20000, _rand_tree_edges(20000, _Lcg(82)))),
    ],
    expl=[
        "From town 0: 1 + 1 + 2 + 2 = 6. From town 3: 2 (to 0) + 3 (to 1) + 1 + 2 = 8.",
        "Each town is one road from the other.",
    ],
    prereqs=[
        ("tree_dp", "A bottom-up pass for subtree sizes and sums, then a top-down pass that moves the root."),
        ("bfs", "A BFS order gives parents before children, so both passes need no recursion."),
    ],
)


_p(
    "tree-cameras", "Guard Every Room", "Hard",
    topics=["Tree", "Greedy"], subtopics=["Tree", "Greedy", "Tree DP", "Post-order"],
    companies=["Google", "Meta", "Amazon"],
    shape="tree", ret="int",
    todo="post-order with three states per node: NOT_COVERED, HAS_GUARD, COVERED; a null child counts as COVERED",
    description=(
        "A museum's rooms form a binary tree. A guard placed in a room watches that room, its "
        "parent and its children. Print the **fewest guards** needed so that every room is "
        "watched.\n\n"
        "### Input\nOne line: the tree in level order (`null` for a missing child). The values are "
        "room numbers and do not matter.\n\n### Output\nThe minimum number of guards."
    ),
    constraints="1 ≤ nodes ≤ 3000",
    hints=[
        "Never put a guard on a leaf: its parent watches everything the leaf would, and more.",
        "Work bottom-up. Each node reports one of three states to its parent: not watched yet, has a guard, or watched without a guard.",
        "If any child is not watched, this node *must* hold a guard. Else if any child has a guard, this node is watched. Else it is not watched — leave it for its parent. A null child counts as watched. At the end, an unwatched root needs a guard of its own.",
    ],
    opt=("O(n)", "O(h)",
         "One post-order pass with a constant-size state per node."),
    editorial=(
        "## The one thing this teaches\n**Greedy from the leaves up.** The deepest unwatched "
        "node has one best cover: a guard on its parent, which watches it, its siblings and the "
        "grandparent. Deciding bottom-up makes that choice everywhere at once.\n\n"
        "## Three states\n```java\n// 0 = not watched, 1 = has a guard, 2 = watched, no guard\n"
        "int dfs(TreeNode n) {\n    if (n == null) return 2;                 // nothing to watch\n"
        "    int l = dfs(n.left), r = dfs(n.right);\n    if (l == 0 || r == 0) { guards++; return 1; }\n"
        "    if (l == 1 || r == 1) return 2;\n    return 0;                                // the parent must cover it\n}\n"
        "// answer = guards + (dfs(root) == 0 ? 1 : 0)\n```\n\n"
        "## Why null is \"watched\"\nIf null returned \"not watched\", every leaf would get a guard — "
        "the exact opposite of the greedy."
    ),
    py='''
def solve(root):
    order, st = [], [root]
    while st:
        n = st.pop()
        order.append(n)
        if n.left:
            st.append(n.left)
        if n.right:
            st.append(n.right)
    state, guards = {}, 0
    for n in reversed(order):
        l = state[n.left] if n.left else 2
        r = state[n.right] if n.right else 2
        if l == 0 or r == 0:
            guards += 1
            state[n] = 1
        elif l == 1 or r == 1:
            state[n] = 2
        else:
            state[n] = 0
    return guards + (1 if state[root] == 0 else 0)
''',
    java='''
    static int solve(TreeNode root) {
        List<TreeNode> order = new ArrayList<>();
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        st.push(root);
        while (!st.isEmpty()) {
            TreeNode n = st.pop();
            order.add(n);
            if (n.left != null) st.push(n.left);
            if (n.right != null) st.push(n.right);
        }
        Map<TreeNode, Integer> state = new HashMap<>();
        int guards = 0;
        for (int i = order.size() - 1; i >= 0; i--) {
            TreeNode n = order.get(i);
            int l = n.left != null ? state.get(n.left) : 2;
            int r = n.right != null ? state.get(n.right) : 2;
            int s;
            if (l == 0 || r == 0) { guards++; s = 1; }
            else if (l == 1 || r == 1) s = 2;
            else s = 0;
            state.put(n, s);
        }
        return guards + (state.get(root) == 0 ? 1 : 0);
    }
''',
    examples=[
        ("Example 1", "0 0 0 0 null null 0\n"),
        ("Example 2", "0 null 0 0 null 0 null 0\n"),
    ],
    hidden=[
        ("One room", "0\n"),
        ("Two rooms", "0 0\n"),
        ("Three in a line", _chain_line([0, 0, 0], "R") + "\n"),
        ("Full depth 3", " ".join(["0"] * 15) + "\n"),
        ("Long path", _chain_line([0] * 1000, "Z") + "\n"),
        ("Random", _rand_tree_line(120, 91, 0, 0) + "\n"),
        ("Large", _rand_tree_line(3000, 92, 0, 0) + "\n"),
    ],
    expl=[
        "One guard on each of the root's children: each watches the root, itself and its own child.",
        "A chain of five rooms: guards in the 2nd and 4th rooms from the top watch all five.",
    ],
    prereqs=[
        ("tree_dp", "Each node returns a small state to its parent — a post-order DP."),
        ("greedy", "Covering the deepest unwatched node from its parent is never worse."),
    ],
)
