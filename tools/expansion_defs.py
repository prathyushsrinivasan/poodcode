# -*- coding: utf-8 -*-
# ===========================================================================
# Poodcode syllabus expansion — exec'd inside gen_seed.py's namespace.
#
# Adds nine interview domains end-to-end: Trees, Linked Lists, Backtracking,
# Heaps, Intervals, Design/DS, Union-Find, Advanced Graphs, Tries. Extends the
# generator's existing structures in place:
#   CONCEPTS / CATEGORY / LESSONS / EXERCISES / PREREQS / PATTERN_FROM
#   HARNESS_DEFS (function problems) and DEFS (raw stdin/stdout problems)
#   JAVA_STARTERS (raw-problem Java starters)
# and defines:
#   EXPANSION_REFS  -> merged into REFERENCE_SOLUTIONS (verify_seeds trust)
#   FLASHCARDS      -> emitted to flashcards.json (seeded at launch)
#
# The execution model is 1-D stdin/stdout, so structures are encoded:
#   * trees      -> string[] level-order with "null" tokens (+ TreeNode helpers)
#   * linked list-> int[] of values
#   * graphs     -> parallel arrays  int n, int[] u, int[] v (, int[] w)
#   * intervals  -> parallel arrays  int[] starts, int[] ends
#   * design/DS  -> operation stream (raw DEFS)
#   * generate-* -> checker judge (any correct/complete set accepted)
# ===========================================================================
from collections import deque

EXPANSION_REFS = {}
FLASHCARDS = []

# ---------------------------------------------------------------------------
# Tree helpers (Python oracles + Java/Python learner scaffolding)
# ---------------------------------------------------------------------------

class _TN:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None


def _build_tree(tokens):
    """Level-order token list (with 'null') -> root _TN (or None)."""
    toks = list(tokens)
    if not toks or toks[0] == "null":
        return None
    root = _TN(int(toks[0]))
    q = deque([root])
    i = 1
    n = len(toks)
    while q and i < n:
        node = q.popleft()
        if i < n and toks[i] != "null":
            node.l = _TN(int(toks[i]))
            q.append(node.l)
        i += 1
        if i < n and toks[i] != "null":
            node.r = _TN(int(toks[i]))
            q.append(node.r)
        i += 1
    return root


def _ser_tree(root):
    """Root -> level-order token list, trailing 'null's trimmed."""
    if not root:
        return []
    out = []
    q = deque([root])
    while q:
        n = q.popleft()
        if n is None:
            out.append("null")
            continue
        out.append(str(n.v))
        q.append(n.l)
        q.append(n.r)
    while out and out[-1] == "null":
        out.pop()
    return out


# Java scaffolding: a TreeUtil with build()/ser(), reusable by starters + refs.
_TREE_PRELUDE_JAVA = (
    "import java.util.*;\n"
    "class TreeNode { int val; TreeNode left, right; TreeNode(int v){ val = v; } }\n"
    "class TreeUtil {\n"
    "    static TreeNode build(String[] a) {\n"
    "        if (a.length == 0 || a[0].equals(\"null\")) return null;\n"
    "        TreeNode root = new TreeNode(Integer.parseInt(a[0]));\n"
    "        ArrayDeque<TreeNode> q = new ArrayDeque<>(); q.add(root);\n"
    "        int i = 1;\n"
    "        while (!q.isEmpty() && i < a.length) {\n"
    "            TreeNode n = q.poll();\n"
    "            if (i < a.length && !a[i].equals(\"null\")) { n.left = new TreeNode(Integer.parseInt(a[i])); q.add(n.left); } i++;\n"
    "            if (i < a.length && !a[i].equals(\"null\")) { n.right = new TreeNode(Integer.parseInt(a[i])); q.add(n.right); } i++;\n"
    "        }\n"
    "        return root;\n"
    "    }\n"
    "    static String[] ser(TreeNode root) {\n"
    "        List<String> out = new ArrayList<>();\n"
    "        if (root == null) return new String[0];\n"
    "        LinkedList<TreeNode> q = new LinkedList<>(); q.add(root);\n"
    "        while (!q.isEmpty()) {\n"
    "            TreeNode n = q.poll();\n"
    "            if (n == null) { out.add(\"null\"); continue; }\n"
    "            out.add(String.valueOf(n.val)); q.add(n.left); q.add(n.right);\n"
    "        }\n"
    "        while (!out.isEmpty() && out.get(out.size()-1).equals(\"null\")) out.remove(out.size()-1);\n"
    "        return out.toArray(new String[0]);\n"
    "    }\n"
    "}\n"
)

_TREE_PRELUDE_PY = (
    "from collections import deque\n"
    "class TreeNode:\n"
    "    def __init__(self, v): self.val = v; self.left = None; self.right = None\n"
    "def build_tree(a):\n"
    "    if not a or a[0] == 'null': return None\n"
    "    root = TreeNode(int(a[0])); q = deque([root]); i = 1\n"
    "    while q and i < len(a):\n"
    "        n = q.popleft()\n"
    "        if i < len(a) and a[i] != 'null': n.left = TreeNode(int(a[i])); q.append(n.left)\n"
    "        i += 1\n"
    "        if i < len(a) and a[i] != 'null': n.right = TreeNode(int(a[i])); q.append(n.right)\n"
    "        i += 1\n"
    "    return root\n"
    "def ser_tree(root):\n"
    "    if not root: return []\n"
    "    out = []; q = deque([root])\n"
    "    while q:\n"
    "        n = q.popleft()\n"
    "        if n is None: out.append('null'); continue\n"
    "        out.append(str(n.val)); q.append(n.left); q.append(n.right)\n"
    "    while out and out[-1] == 'null': out.pop()\n"
    "    return out\n"
)


def _tree_starters(spec, note="TODO: implement"):
    """Java + Python starter that ships TreeNode + build helpers for a harness
    tree problem, building the first string[] param into `root`."""
    jparams = ", ".join("%s %s" % (_JAVA_TY[p["type"]], p["name"]) for p in spec["params"])
    jbuild = ""
    pbuild = ""
    for p in spec["params"]:
        if p["type"] == "string[]":
            jbuild = "        TreeNode root = TreeUtil.build(%s);\n" % p["name"]
            pbuild = "    root = build_tree(%s)\n" % p["name"]
            break
    java = (
        _TREE_PRELUDE_JAVA
        + "class Solution {\n"
        + "    %s %s(%s) {\n" % (_JAVA_TY[spec["returns"]], spec["name"], jparams)
        + jbuild
        + "        // %s\n        return %s;\n    }\n}\n" % (note, _java_default(spec["returns"]))
    )
    pparams = ", ".join(p["name"] for p in spec["params"])
    python = (
        _TREE_PRELUDE_PY
        + "def %s(%s):\n" % (spec["name"], pparams)
        + pbuild
        + "    # %s\n    return %s\n" % (note, _py_default(spec["returns"]))
    )
    return java, python


# ---------------------------------------------------------------------------
# Operation-stream scaffolding (design / data-structure problems, raw DEFS).
# Input: line 1 = number of operations Q; next Q lines = "OP arg...".
# Output: one line per query op (commands that mutate print nothing).
# ---------------------------------------------------------------------------

def _ops_starters(class_hint):
    java = (
        "import java.util.*;\n"
        "import java.io.*;\n"
        "public class Main {\n"
        "    // %s\n" % class_hint
        + "    public static void main(String[] args) throws IOException {\n"
        "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n"
        "        int q = Integer.parseInt(br.readLine().trim());\n"
        "        StringBuilder sb = new StringBuilder();\n"
        "        for (int k = 0; k < q; k++) {\n"
        "            StringTokenizer st = new StringTokenizer(br.readLine());\n"
        "            String op = st.nextToken();\n"
        "            // TODO: handle each op; append query results (one per line) to sb\n"
        "        }\n"
        "        System.out.print(sb);\n"
        "    }\n"
        "}\n"
    )
    py = (
        "import sys\n"
        "def main():\n"
        "    data = sys.stdin.read().split('\\n')\n"
        "    q = int(data[0])\n"
        "    out = []\n"
        "    # %s\n" % class_hint
        + "    for k in range(1, q + 1):\n"
        "        parts = data[k].split()\n"
        "        op = parts[0]; args = parts[1:]\n"
        "        # TODO: handle each op; append query results to out\n"
        "    sys.stdout.write('\\n'.join(out))\n"
        "main()\n"
    )
    js = (
        "const L = require('fs').readFileSync(0,'utf8').split('\\n');\n"
        "const q = parseInt(L[0]);\n"
        "const out = [];\n"
        "for (let k = 1; k <= q; k++) {\n"
        "  const parts = L[k].split(' ');\n"
        "  const op = parts[0], args = parts.slice(1);\n"
        "  // TODO: handle each op; push query results to out\n"
        "}\n"
        "console.log(out.join('\\n'));\n"
    )
    return java, py, js


# ---------------------------------------------------------------------------
# Exercise (Learn drill) tree scaffolding: a self-contained Java program that
# reads one level-order line of tokens, builds a tree, and computes. Reused by
# blanking a single line.
# ---------------------------------------------------------------------------
_EXJ_TREE_HEAD = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static class TreeNode { int val; TreeNode left, right; TreeNode(int v){ val = v; } }\n"
    "    static TreeNode build(String[] a) {\n"
    "        if (a.length == 0 || a[0].equals(\"null\")) return null;\n"
    "        TreeNode root = new TreeNode(Integer.parseInt(a[0]));\n"
    "        ArrayDeque<TreeNode> q = new ArrayDeque<>(); q.add(root); int i = 1;\n"
    "        while (!q.isEmpty() && i < a.length) {\n"
    "            TreeNode n = q.poll();\n"
    "            if (i < a.length && !a[i].equals(\"null\")) { n.left = new TreeNode(Integer.parseInt(a[i])); q.add(n.left); } i++;\n"
    "            if (i < a.length && !a[i].equals(\"null\")) { n.right = new TreeNode(Integer.parseInt(a[i])); q.add(n.right); } i++;\n"
    "        }\n"
    "        return root;\n"
    "    }\n"
)


# ===========================================================================
# DOMAIN 1 — TREES & BSTs
# ===========================================================================

def _t_depth(n):
    return 0 if n is None else 1 + max(_t_depth(n.l), _t_depth(n.r))


def _t_min_depth(n):
    if n is None:
        return 0
    if n.l is None and n.r is None:
        return 1
    if n.l is None:
        return 1 + _t_min_depth(n.r)
    if n.r is None:
        return 1 + _t_min_depth(n.l)
    return 1 + min(_t_min_depth(n.l), _t_min_depth(n.r))


def _t_count(n):
    return 0 if n is None else 1 + _t_count(n.l) + _t_count(n.r)


def _t_invert(n):
    if n is None:
        return None
    n.l, n.r = _t_invert(n.r), _t_invert(n.l)
    return n


def _t_same(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None or a.v != b.v:
        return False
    return _t_same(a.l, b.l) and _t_same(a.r, b.r)


def _t_mirror(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None or a.v != b.v:
        return False
    return _t_mirror(a.l, b.r) and _t_mirror(a.r, b.l)


def _t_inorder(n, out):
    if n is None:
        return
    _t_inorder(n.l, out)
    out.append(n.v)
    _t_inorder(n.r, out)


def _t_preorder(n, out):
    if n is None:
        return
    out.append(n.v)
    _t_preorder(n.l, out)
    _t_preorder(n.r, out)


def _t_levels(root):
    res = []
    if not root:
        return res
    q = deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft()
            level.append(n.v)
            if n.l:
                q.append(n.l)
            if n.r:
                q.append(n.r)
        res.append(level)
    return res


def _t_level_flat(root):
    out = []
    for lv in _t_levels(root):
        out.extend(lv)
    return out


def _t_right_view(root):
    return [lv[-1] for lv in _t_levels(root)]


def _t_zigzag(root):
    out = []
    for i, lv in enumerate(_t_levels(root)):
        out.extend(lv if i % 2 == 0 else lv[::-1])
    return out


def _t_path_sum(n, target):
    if n is None:
        return False
    if n.l is None and n.r is None:
        return n.v == target
    return _t_path_sum(n.l, target - n.v) or _t_path_sum(n.r, target - n.v)


def _t_balanced(n):
    def h(x):
        if x is None:
            return 0
        lh = h(x.l)
        if lh < 0:
            return -1
        rh = h(x.r)
        if rh < 0:
            return -1
        if abs(lh - rh) > 1:
            return -1
        return 1 + max(lh, rh)
    return h(n) >= 0


def _t_diameter(root):
    best = [0]

    def h(n):
        if n is None:
            return 0
        lh = h(n.l)
        rh = h(n.r)
        best[0] = max(best[0], lh + rh)
        return 1 + max(lh, rh)
    h(root)
    return best[0]


def _t_max_path_sum(root):
    best = [-10 ** 9]

    def gain(n):
        if n is None:
            return 0
        lg = max(gain(n.l), 0)
        rg = max(gain(n.r), 0)
        best[0] = max(best[0], n.v + lg + rg)
        return n.v + max(lg, rg)
    gain(root)
    return best[0]


def _t_valid_bst(root):
    def ok(n, lo, hi):
        if n is None:
            return True
        if not (lo < n.v < hi):
            return False
        return ok(n.l, lo, n.v) and ok(n.r, n.v, hi)
    return ok(root, -(10 ** 18), 10 ** 18)


def _t_bst_search(root, v):
    n = root
    while n:
        if n.v == v:
            return True
        n = n.l if v < n.v else n.r
    return False


def _t_bst_insert(root, v):
    if root is None:
        return _TN(v)
    n = root
    while True:
        if v < n.v:
            if n.l is None:
                n.l = _TN(v)
                break
            n = n.l
        else:
            if n.r is None:
                n.r = _TN(v)
                break
            n = n.r
    return root


def _t_kth_smallest(root, k):
    out = []
    _t_inorder(root, out)
    return out[k - 1]


def _t_lca_bst(root, p, q):
    n = root
    while n:
        if p < n.v and q < n.v:
            n = n.l
        elif p > n.v and q > n.v:
            n = n.r
        else:
            return n.v
    return -1


def _t_lca_binary(root, p, q):
    def dfs(n):
        if n is None:
            return None
        if n.v == p or n.v == q:
            return n
        L = dfs(n.l)
        R = dfs(n.r)
        if L and R:
            return n
        return L or R
    r = dfs(root)
    return r.v if r else -1


def _bt(toks):
    return _build_tree(toks)


_SPEC_TREE = lambda extra=None, ret="int": {  # noqa: E731
    "name": "solve",
    "params": [{"name": "level", "type": "string[]"}] + (extra or []),
    "returns": ret,
}

# Some sample trees (token lists) reused across cases.
_TREE_A = ["3", "9", "20", "null", "null", "15", "7"]
_TREE_B = ["1", "2", "2", "3", "4", "4", "3"]
_BST_A = ["5", "3", "8", "2", "4", "7", "9"]


def _tree_def(slug, title, diff, extra, ret, fn, desc, hints, opt, editorial,
              cases, companies, subtopics, example_expl, note="TODO: implement"):
    spec = _SPEC_TREE(extra, ret)
    sj, sp = _tree_starters(spec, note)
    return dict(
        slug=slug, title=title, difficulty=diff,
        topics=["Trees"], subtopics=subtopics, companies=companies,
        description=desc, constraints="Nodes are given in level order; `null` marks a missing child.\n0 ≤ number of nodes ≤ 2000.",
        hints=hints, opt=opt, editorial=editorial,
        spec=spec, fn=fn, starter_py=sp, starter_java=sj,
        cases=cases, example_expl=example_expl,
    )


HARNESS_DEFS += [
    _tree_def(
        "max-depth-tree", "Maximum Depth of Binary Tree", "Easy",
        None, "int", lambda t: _t_depth(_bt(t)),
        "Return the **maximum depth** (number of nodes on the longest root-to-leaf path) of a binary tree given in level order.",
        ["The depth of a node is 1 + the deeper of its two children.",
         "An empty subtree has depth 0.",
         "Recurse into left and right, take the max, add 1.",
         "`return 1 + max(depth(left), depth(right));`"],
        ("O(n)", "O(h)", "Visit every node once; recursion uses stack proportional to height h."),
        "## Approach\nPost-order recursion: depth(node) = 1 + max(depth(left), depth(right)); an empty node is 0.",
        [("example", "Balanced-ish", (_TREE_A,)), ("example", "Single node", (["1"],)),
         ("hidden", "Left chain", (["1", "2", "null", "3"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Full", (["1", "2", "3", "4", "5", "6", "7"],))],
        ["Amazon", "LinkedIn"], ["Tree DFS"],
        ["Longest path 3->20->15 (or ->7) has 3 nodes.", "One node has depth 1."],
    ),
    _tree_def(
        "min-depth-tree", "Minimum Depth of Binary Tree", "Easy",
        None, "int", lambda t: _t_min_depth(_bt(t)),
        "Return the **minimum depth**: the number of nodes on the shortest path from the root down to the nearest **leaf**.",
        ["A leaf is a node with no children.",
         "Careful: a node with only one child is NOT a leaf — you must go down the existing side.",
         "min over children that exist, +1.",
         "If one child is null, recurse only into the other."],
        ("O(n)", "O(h)", "Each node visited once."),
        "## Approach\nIf a node has one missing child, the min depth goes through the present child (a null child is not a shortest path to a leaf).",
        [("example", "Balanced-ish", (_TREE_A,)), ("example", "One-sided", (["2", "null", "3", "null", "4"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Full", (["1", "2", "3", "4", "5", "6", "7"],))],
        ["Facebook", "Amazon"], ["Tree BFS"],
        ["Nearest leaf is 9, at depth 2.", "The only leaf is at depth 3 down the right chain."],
    ),
    _tree_def(
        "count-nodes-tree", "Count Complete Tree Nodes", "Easy",
        None, "int", lambda t: _t_count(_bt(t)),
        "Return the total **number of nodes** in the tree.",
        ["Every node contributes 1.", "count = 1 + count(left) + count(right).", "An empty subtree contributes 0.",
         "A simple DFS counts them all."],
        ("O(n)", "O(h)", "Visit each node once."),
        "## Approach\ncount(node) = node ? 1 + count(left) + count(right) : 0.",
        [("example", "Seven nodes", (["1", "2", "3", "4", "5", "6", "7"],)), ("example", "Single", (["1"],)),
         ("hidden", "Empty", ([],)), ("hidden", "Chain", (["1", "2", "null", "3"],)),
         ("hidden", "Sparse", (_TREE_A,))],
        ["Google"], ["Tree DFS"],
        ["A full tree of height 3 has 7 nodes.", "One node."],
    ),
    _tree_def(
        "invert-binary-tree", "Invert Binary Tree", "Easy",
        None, "string[]", lambda t: _ser_tree(_t_invert(_bt(t))),
        "**Mirror** the tree: swap the left and right child of every node. Return the inverted tree in level order.",
        ["Swap the two children of each node.", "Recurse into both sides.",
         "Order of swap vs recurse doesn't matter as long as every node is swapped.",
         "`node.left, node.right = invert(node.right), invert(node.left);`"],
        ("O(n)", "O(h)", "One swap per node."),
        "## Approach\nRecursively swap children. Return the root; the harness serializes it back to level order.",
        [("example", "Small", (["4", "2", "7", "1", "3", "6", "9"],)), ("example", "Single", (["1"],)),
         ("hidden", "Empty", ([],)), ("hidden", "Two", (["1", "2"],)),
         ("hidden", "Sparse", (_TREE_A,))],
        ["Google", "Amazon"], ["Tree DFS"],
        ["Mirrors to 4,7,2,9,6,3,1.", "A single node is unchanged."],
        note="swap children, recurse, return root",
    ),
    dict(
        slug="same-tree", title="Same Tree", difficulty="Easy",
        topics=["Trees"], subtopics=["Tree DFS"], companies=["Bloomberg"],
        description="Return `true` if two binary trees (each given in level order) are structurally identical **and** have equal node values.",
        constraints="Two level-order token lists; `null` marks missing children.",
        hints=["Compare roots, then recurse on (a.left,b.left) and (a.right,b.right).",
               "Both null at once → equal here.", "One null but not the other → not the same.",
               "Values must match at every position."],
        opt=("O(n)", "O(h)", "Each pair of nodes compared once."),
        editorial="## Approach\nParallel DFS: equal iff both null, or both non-null with equal value and equal subtrees.",
        spec={"name": "solve", "params": [{"name": "a", "type": "string[]"}, {"name": "b", "type": "string[]"}], "returns": "bool"},
        fn=lambda a, b: _t_same(_bt(a), _bt(b)),
        starter_java=_TREE_PRELUDE_JAVA + "class Solution {\n    boolean solve(String[] a, String[] b) {\n        TreeNode ra = TreeUtil.build(a), rb = TreeUtil.build(b);\n        // TODO\n        return false;\n    }\n}\n",
        starter_py=_TREE_PRELUDE_PY + "def solve(a, b):\n    ra = build_tree(a); rb = build_tree(b)\n    # TODO\n    return False\n",
        cases=[("example", "Equal", (_TREE_B, _TREE_B)), ("example", "Differ", (["1", "2"], ["1", "null", "2"])),
               ("hidden", "Shape diff", (["1", "2", "3"], ["1", "2", "null", "3"])), ("hidden", "Value diff", (["1", "2", "3"], ["1", "2", "4"])),
               ("hidden", "Same single", (["7"], ["7"]))],
        example_expl=["Identical structure and values.", "Same values but different shape."],
    ),
    _tree_def(
        "symmetric-tree", "Symmetric Tree", "Easy",
        None, "bool", lambda t: (lambda r: _t_mirror(r.l, r.r) if r else True)(_bt(t)),
        "Return `true` if the tree is a **mirror image of itself** around its center.",
        ["Compare the left subtree against the right subtree as mirrors.",
         "mirror(a,b): values equal AND mirror(a.left,b.right) AND mirror(a.right,b.left).",
         "An empty tree is symmetric.", "Note the crossed recursion (left vs right)."],
        ("O(n)", "O(h)", "Each mirrored pair compared once."),
        "## Approach\nCheck mirror(root.left, root.right): outer pairs with outer, inner with inner.",
        [("example", "Symmetric", (_TREE_B,)), ("example", "Not", (["1", "2", "2", "null", "3", "null", "3"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Two same", (["1", "2", "2"],))],
        ["Amazon", "LinkedIn"], ["Tree DFS"],
        ["Left and right subtrees mirror each other.", "The 3s break the mirror."],
    ),
    _tree_def(
        "inorder-traversal", "Binary Tree Inorder Traversal", "Easy",
        None, "int[]", lambda t: (lambda o: (_t_inorder(_bt(t), o), o)[1])([]),
        "Return the node values from an **inorder** (left, root, right) traversal.",
        ["Recurse left, visit the node, recurse right.",
         "Append the value between the two recursive calls.",
         "For a BST this yields sorted order.",
         "An iterative stack version also works."],
        ("O(n)", "O(h)", "Visit each node once."),
        "## Approach\ninorder(node): inorder(left); output node; inorder(right).",
        [("example", "Small", (["1", "null", "2", "3"],)), ("example", "BST", (_BST_A,)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Left chain", (["3", "2", "null", "1"],))],
        ["Microsoft"], ["Tree DFS"],
        ["Inorder is 1,3,2.", "Inorder of a BST is sorted: 2,3,4,5,7,8,9."],
        note="inorder: left, node, right",
    ),
    _tree_def(
        "preorder-traversal", "Binary Tree Preorder Traversal", "Easy",
        None, "int[]", lambda t: (lambda o: (_t_preorder(_bt(t), o), o)[1])([]),
        "Return the node values from a **preorder** (root, left, right) traversal.",
        ["Visit the node first, then recurse left, then right.",
         "Append the value before the recursive calls.",
         "Preorder can rebuild the tree structure when combined with inorder.",
         "An explicit stack gives an iterative version."],
        ("O(n)", "O(h)", "Visit each node once."),
        "## Approach\npreorder(node): output node; preorder(left); preorder(right).",
        [("example", "Small", (["1", "null", "2", "3"],)), ("example", "Full", (["1", "2", "3", "4", "5"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "BST", (_BST_A,))],
        ["Microsoft"], ["Tree DFS"],
        ["Preorder is 1,2,3.", "Preorder is 1,2,4,5,3."],
        note="preorder: node, left, right",
    ),
    _tree_def(
        "level-order-traversal", "Binary Tree Level Order Traversal", "Medium",
        None, "int[]", lambda t: _t_level_flat(_bt(t)),
        "Return node values in **level order** (top to bottom, left to right within each level), flattened into a single list.",
        ["Use a queue (BFS).", "Process the tree level by level.",
         "Dequeue a node, record its value, enqueue its children.",
         "Flatten all levels top-down, left-to-right."],
        ("O(n)", "O(w)", "BFS visits each node once; queue holds at most one level (width w)."),
        "## Approach\nBFS with a queue; append each dequeued value; enqueue non-null children.",
        [("example", "Balanced-ish", (_TREE_A,)), ("example", "Full", (["1", "2", "3", "4", "5", "6", "7"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Chain", (["1", "2", "null", "3"],))],
        ["Amazon", "Microsoft", "Facebook"], ["Tree BFS"],
        ["Levels 3 | 9,20 | 15,7 flatten to 3,9,20,15,7.", "1,2,3,4,5,6,7."],
    ),
    _tree_def(
        "right-side-view", "Binary Tree Right Side View", "Medium",
        None, "int[]", lambda t: _t_right_view(_bt(t)),
        "Return the values you would see looking at the tree from the **right side**, top to bottom (the last node of each level).",
        ["BFS level by level; take the last node of each level.",
         "Or DFS right-first, recording the first node seen at each new depth.",
         "One value per level.", "The rightmost node of each level is visible."],
        ("O(n)", "O(w)", "BFS over all nodes."),
        "## Approach\nBFS; for each level append the last dequeued value.",
        [("example", "Small", (["1", "2", "3", "null", "5", "null", "4"],)), ("example", "Left chain", (["1", "2", "null", "3"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Full", (["1", "2", "3", "4", "5", "6", "7"],))],
        ["Facebook", "Amazon"], ["Tree BFS"],
        ["Right side sees 1,3,4.", "Only-left tree still shows 1,2,3 from the right."],
    ),
    _tree_def(
        "zigzag-level-order", "Zigzag Level Order Traversal", "Medium",
        None, "int[]", lambda t: _t_zigzag(_bt(t)),
        "Return node values level by level, but **alternating direction**: level 0 left-to-right, level 1 right-to-left, and so on. Flatten the result.",
        ["Do a normal BFS to collect each level.",
         "Reverse every other level before appending.",
         "Track a boolean that flips each level.",
         "Level index even → forward, odd → reversed."],
        ("O(n)", "O(w)", "BFS then reverse alternate levels."),
        "## Approach\nBFS into levels; reverse odd-indexed levels; flatten.",
        [("example", "Balanced-ish", (_TREE_A,)), ("example", "Full", (["1", "2", "3", "4", "5", "6", "7"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Two levels", (["1", "2", "3"],))],
        ["Amazon", "Microsoft"], ["Tree BFS"],
        ["3 | 20,9 | 15,7 → 3,20,9,15,7.", "1 | 3,2 | 4,5,6,7 → 1,3,2,4,5,6,7."],
    ),
    _tree_def(
        "path-sum-exists", "Path Sum", "Easy",
        [{"name": "target", "type": "int"}], "bool", lambda t, target: _t_path_sum(_bt(t), target),
        "Return `true` if the tree has a **root-to-leaf path** whose node values add up to `target`.",
        ["Subtract the current node's value and recurse.",
         "At a leaf, success iff the remaining target equals the leaf value.",
         "Try both children; either succeeding is enough.",
         "An empty tree has no path."],
        ("O(n)", "O(h)", "Each node visited once."),
        "## Approach\nDFS carrying the remaining target; at a leaf check equality.",
        [("example", "Has path", (_TREE_A, 12)), ("example", "No path", (_TREE_A, 100)),
         ("hidden", "Single hit", (["7"], 7)), ("hidden", "Single miss", (["7"], 3)),
         ("hidden", "Empty", ([], 0))],
        ["Amazon"], ["Tree DFS"],
        ["3+9 = 12 reaches a leaf.", "No root-to-leaf path sums to 100."],
        note="subtract node value, recurse to a leaf",
    ),
    _tree_def(
        "balanced-tree", "Balanced Binary Tree", "Medium",
        None, "bool", lambda t: _t_balanced(_bt(t)),
        "Return `true` if the tree is **height-balanced**: for every node the heights of its two subtrees differ by at most 1.",
        ["Compute height, but bubble up a 'not balanced' signal.",
         "Use -1 as a sentinel meaning 'already unbalanced'.",
         "If |leftH - rightH| > 1, propagate failure.",
         "One post-order pass avoids recomputing heights."],
        ("O(n)", "O(h)", "Single post-order pass."),
        "## Approach\nReturn subtree height, or -1 once any node is unbalanced; short-circuit upward.",
        [("example", "Balanced", (["1", "2", "3", "4", "5", "6", "7"],)), ("example", "Skewed", (["1", "2", "null", "3", "null", "4"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Sparse ok", (_TREE_A,))],
        ["Amazon", "Bloomberg"], ["Tree DFS"],
        ["A full tree is balanced.", "The left chain is too deep on one side."],
    ),
    _tree_def(
        "diameter-of-tree", "Diameter of Binary Tree", "Medium",
        None, "int", lambda t: _t_diameter(_bt(t)),
        "Return the **diameter**: the number of edges on the longest path between any two nodes (the path need not pass through the root).",
        ["At each node, the longest through-path = leftHeight + rightHeight (in edges).",
         "Track a global maximum while computing heights.",
         "Height in edges: empty = 0, leaf = 0 below it... use node-height carefully.",
         "Return the best left+right seen anywhere."],
        ("O(n)", "O(h)", "One post-order pass with a running best."),
        "## Approach\nDFS returning height; update best = max(best, leftH + rightH) at every node.",
        [("example", "Small", (["1", "2", "3", "4", "5"],)), ("example", "Chain", (["1", "2", "null", "3"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Balanced", (["1", "2", "3", "4", "5", "6", "7"],))],
        ["Facebook", "Amazon"], ["Tree DFS"],
        ["Path 4-2-1-3 (or 5-2-1-3) has 3 edges.", "A 3-node chain has diameter 2."],
    ),
    _tree_def(
        "max-path-sum", "Binary Tree Maximum Path Sum", "Hard",
        None, "int", lambda t: _t_max_path_sum(_bt(t)),
        "A path is any sequence of connected nodes; it need not pass through the root and cannot reuse a node. Return the **maximum path sum** (values may be negative).",
        ["At each node the best 'through' path = node + max(0,leftGain) + max(0,rightGain).",
         "Clamp negative child gains to 0 (skip that side).",
         "Return upward only node + max(leftGain,rightGain) — a path can't branch above.",
         "Track a global maximum of the through-path."],
        ("O(n)", "O(h)", "One post-order pass."),
        "## Approach\ngain(node) returns the best downward path; update a global best with the split path node+leftGain+rightGain.",
        [("example", "Simple", (["1", "2", "3"],)), ("example", "Negatives", (["-10", "9", "20", "null", "null", "15", "7"],)),
         ("hidden", "Single negative", (["-3"],)), ("hidden", "Single", (["5"],)),
         ("hidden", "All positive", (["1", "2", "3", "4", "5", "6", "7"],))],
        ["Facebook", "Amazon", "Google"], ["Tree DFS"],
        ["2+1+3 = 6.", "15+20+7 = 42 (skip the -10 root)."],
    ),
    _tree_def(
        "validate-bst", "Validate Binary Search Tree", "Medium",
        None, "bool", lambda t: _t_valid_bst(_bt(t)),
        "Return `true` if the tree is a valid **binary search tree**: every node is greater than all nodes in its left subtree and less than all in its right subtree.",
        ["A node value must lie in an open (low, high) range.",
         "Going left tightens the upper bound to the node's value; going right raises the lower bound.",
         "Checking only immediate children is NOT enough.",
         "An inorder traversal must be strictly increasing."],
        ("O(n)", "O(h)", "One pass with propagated bounds."),
        "## Approach\nRecurse carrying (low, high); each node must satisfy low < val < high; tighten bounds descending.",
        [("example", "Valid", (_BST_A,)), ("example", "Invalid", (["5", "1", "4", "null", "null", "3", "6"],)),
         ("hidden", "Single", (["1"],)), ("hidden", "Empty", ([],)),
         ("hidden", "Equal breaks", (["2", "2", "2"],))],
        ["Amazon", "Microsoft", "Facebook"], ["BST"],
        ["Every node respects the BST order.", "4's subtree has 3 < 4 on the wrong side of 5."],
    ),
    _tree_def(
        "bst-search", "Search in a BST", "Easy",
        [{"name": "v", "type": "int"}], "bool", lambda t, v: _t_bst_search(_bt(t), v),
        "Given a BST, return `true` if a node with value `v` exists.",
        ["Compare v with the current node.", "Go left if v is smaller, right if larger.",
         "Found when equal; missing when you fall off the tree.",
         "O(height) — no need to scan everything."],
        ("O(h)", "O(1)", "Follow one root-to-leaf path."),
        "## Approach\nWalk down: if v < node go left else go right, stop on a match.",
        [("example", "Present", (_BST_A, 7)), ("example", "Absent", (_BST_A, 6)),
         ("hidden", "Root", (_BST_A, 5)), ("hidden", "Single miss", (["1"], 2)),
         ("hidden", "Leaf", (_BST_A, 9))],
        ["Amazon"], ["BST"],
        ["7 is in the right subtree.", "6 is not present."],
        note="go left when v < node.val, else right",
    ),
    _tree_def(
        "bst-insert", "Insert into a BST", "Medium",
        [{"name": "v", "type": "int"}], "string[]", lambda t, v: _ser_tree(_t_bst_insert(_bt(t), v)),
        "Insert value `v` into the BST and return the resulting tree in level order. Any valid BST insertion (as a new leaf) is expected.",
        ["Walk down as if searching for v.", "When the needed child is null, attach the new node there.",
         "Smaller values go left, larger go right.", "Insertion happens at a leaf position."],
        ("O(h)", "O(h)", "One root-to-leaf descent."),
        "## Approach\nDescend choosing left/right by comparison; attach a new leaf where the path runs off.",
        [("example", "Insert 6", (_BST_A, 6)), ("example", "Insert into empty", ([], 4)),
         ("hidden", "Insert 1", (_BST_A, 1)), ("hidden", "Insert 10", (_BST_A, 10)),
         ("hidden", "Single", (["5"], 3))],
        ["Amazon"], ["BST"],
        ["6 attaches under 7's left.", "First node becomes the root."],
        note="descend, attach new leaf where child is null, return root",
    ),
    _tree_def(
        "kth-smallest-bst", "Kth Smallest Element in a BST", "Medium",
        [{"name": "k", "type": "int"}], "int", lambda t, k: _t_kth_smallest(_bt(t), k),
        "Return the **k-th smallest** value (1-indexed) in the BST.",
        ["Inorder traversal of a BST yields sorted order.",
         "Stop after visiting k nodes.",
         "The k-th visited value in inorder is the answer.",
         "An iterative inorder with a stack can early-exit."],
        ("O(h + k)", "O(h)", "Inorder until the k-th node."),
        "## Approach\nInorder traverse; the k-th value emitted is the answer.",
        [("example", "k=3", (_BST_A, 3)), ("example", "k=1", (_BST_A, 1)),
         ("hidden", "Max", (_BST_A, 7)), ("hidden", "Single", (["5"], 1)),
         ("hidden", "k=5", (_BST_A, 5))],
        ["Amazon", "Google"], ["BST"],
        ["Sorted 2,3,4,5,7,8,9 → 3rd is 4.", "Smallest is 2."],
    ),
    _tree_def(
        "lca-bst", "Lowest Common Ancestor of a BST", "Medium",
        [{"name": "p", "type": "int"}, {"name": "q", "type": "int"}], "int", lambda t, p, q: _t_lca_bst(_bt(t), p, q),
        "Given a BST and two present values `p` and `q`, return the value of their **lowest common ancestor**.",
        ["Use the BST order to decide direction.",
         "If both p and q are less than the node, go left; if both greater, go right.",
         "Otherwise the node is the split point — the LCA.",
         "No need to search both subtrees."],
        ("O(h)", "O(1)", "Single descent to the split node."),
        "## Approach\nDescend while p and q are on the same side; the first node between them is the LCA.",
        [("example", "Split", (_BST_A, 2, 4)), ("example", "Ancestor is one", (_BST_A, 3, 4)),
         ("hidden", "Across root", (_BST_A, 2, 9)), ("hidden", "Same-ish", (_BST_A, 7, 9)),
         ("hidden", "Root split", (_BST_A, 4, 8))],
        ["Amazon", "Facebook"], ["BST"],
        ["2 and 4 split at 3.", "3 is an ancestor of 4 and itself."],
        note="both < node → left; both > node → right; else this node",
    ),
    _tree_def(
        "lca-binary-tree", "Lowest Common Ancestor of a Binary Tree", "Medium",
        [{"name": "p", "type": "int"}, {"name": "q", "type": "int"}], "int", lambda t, p, q: _t_lca_binary(_bt(t), p, q),
        "Given a binary tree (values unique) and two present values `p` and `q`, return the value of their **lowest common ancestor**.",
        ["Recurse; report up if you find p or q (or the node itself).",
         "A node whose left and right both report a find is the LCA.",
         "If only one side reports, bubble that up.",
         "Works without BST ordering."],
        ("O(n)", "O(h)", "One post-order pass."),
        "## Approach\nDFS returns a found node upward; the node where both sides return non-null is the LCA.",
        [("example", "Deep split", (["3", "5", "1", "6", "2", "0", "8"], 6, 2)), ("example", "Ancestor", (["3", "5", "1", "6", "2", "0", "8"], 5, 2)),
         ("hidden", "Root", (["3", "5", "1"], 5, 1)), ("hidden", "Far apart", (["3", "5", "1", "6", "2", "0", "8"], 6, 8)),
         ("hidden", "Single-ish", (["1", "2"], 1, 2))],
        ["Facebook", "Amazon", "Microsoft"], ["Tree DFS"],
        ["6 and 2 meet at 5.", "5 is an ancestor of 2."],
        note="return found node up; where both sides return, that's the LCA",
    ),
]

# --- Trees: concepts + lessons ---------------------------------------------
CONCEPTS.update({
    "tree_basics": {
        "name": "Binary Trees",
        "what": "Nodes each linking to a left and right child, forming a hierarchy with one root and leaves at the bottom.",
        "deep": "A binary tree is defined recursively: a node plus a left subtree and a right subtree. Most tree algorithms are one recursive function whose base case is the empty subtree (null). The height is the longest root-to-leaf chain; balanced trees keep it near log n.",
        "java": "class TreeNode { int val; TreeNode left, right; }. Recurse with a helper; the base case is `if (node == null) return ...;`.",
    },
    "tree_traversal": {
        "name": "Tree Traversals (DFS & BFS)",
        "what": "The orders in which you visit nodes: preorder, inorder, postorder (DFS) and level-order (BFS).",
        "deep": "DFS uses the call stack (or an explicit stack): preorder visits the node before its children, inorder goes left-node-right (sorted for a BST), postorder visits children first (needed when a node's answer depends on its subtrees). BFS uses a queue to sweep level by level — the tool for shortest-depth and per-level questions.",
        "java": "DFS: a recursive helper. BFS: an ArrayDeque<TreeNode> queue, processing one level (queue.size() nodes) at a time.",
    },
    "bst": {
        "name": "Binary Search Trees",
        "what": "A binary tree with the ordering invariant left < node < right, giving O(height) search, insert, and delete.",
        "deep": "The BST invariant turns a tree into a searchable structure: at each node you discard half the remaining tree by comparing with the target, just like binary search. Inorder traversal emits values in sorted order. Validity depends on a value range, not just immediate children.",
        "java": "Descend with `if (v < node.val) node = node.left; else node = node.right;`. Validate by passing down a (low, high) bound.",
    },
    "tree_dp": {
        "name": "Tree DP (Postorder Aggregation)",
        "what": "Computing an answer for each node from the answers of its subtrees in one bottom-up pass.",
        "deep": "When a node's result needs information from below (height, whether balanced, best path), compute it postorder: recurse into both children, combine their returned values, and often update a global best. Returning one value up while recording another (like the split path in diameter / max-path-sum) is the signature move.",
        "java": "A recursive helper that returns the 'upward' value (e.g. height) and updates a shared field (an int[1] or class member) with the combined 'through' value.",
    },
})
CATEGORY.update({
    "tree_basics": "Trees", "tree_traversal": "Trees", "bst": "Trees", "tree_dp": "Trees",
})
PATTERN_FROM.update({
    "Tree DFS": "Trees", "Tree BFS": "Trees", "BST": "Trees", "Trie": "Trie",
})

LESSONS.update({
    "tree_basics": (
        "# Binary Trees\n\n"
        "A **binary tree** is either empty (`null`) or a node holding a value plus a **left** and **right** subtree — each itself a binary tree. That recursive shape is why almost every tree algorithm is a recursive function whose base case is `null`.\n\n"
        "```java\n"
        "class TreeNode { int val; TreeNode left, right; TreeNode(int v){ val = v; } }\n\n"
        "int size(TreeNode n) {\n"
        "    if (n == null) return 0;            // base case\n"
        "    return 1 + size(n.left) + size(n.right);\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Any time the input is a hierarchy: parents/children, folders, expression trees. Signals: *'root'*, *'leaf'*, *'subtree'*, *'depth/height'*.\n\n"
        "## Serialization used here\n"
        "Problems give the tree in **level order** with `null` for missing children, e.g. `3 9 20 null null 15 7`:\n\n"
        "| token | 3 | 9 | 20 | null | null | 15 | 7 |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| role | root | 3.left | 3.right | 9.left | 9.right | 20.left | 20.right |\n\n"
        "The starter ships a `build()` helper so you can focus on the algorithm."
    ),
    "tree_traversal": (
        "# Tree Traversals\n\n"
        "Four orders, two engines.\n\n"
        "- **DFS (stack / recursion)** — *preorder* `node,left,right`; *inorder* `left,node,right`; *postorder* `left,right,node`.\n"
        "- **BFS (queue)** — *level order*, one row at a time.\n\n"
        "```java\n"
        "void inorder(TreeNode n, List<Integer> out) {\n"
        "    if (n == null) return;\n"
        "    inorder(n.left, out);\n"
        "    out.add(n.val);        // between the two calls\n"
        "    inorder(n.right, out);\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "| Signal in the prompt | Use |\n"
        "|---|---|\n"
        "| 'sorted order', BST values | **inorder** |\n"
        "| copy / serialize / prefix | **preorder** |\n"
        "| answer depends on subtrees | **postorder** |\n"
        "| 'level', 'shallowest', 'each row' | **BFS** |\n\n"
        "## Simulated solve — BFS level order of `1 2 3 4 5`\n"
        "| step | queue | emitted |\n"
        "|---|---|---|\n"
        "| start | [1] | |\n"
        "| pop 1 | [2,3] | 1 |\n"
        "| pop 2 | [3,4,5] | 1,2 |\n"
        "| pop 3 | [4,5] | 1,2,3 |\n"
        "| pop 4,5 | [] | 1,2,3,4,5 |\n"
    ),
    "bst": (
        "# Binary Search Trees\n\n"
        "A BST keeps **left < node < right** at *every* node. That single invariant makes search behave like binary search — one comparison discards half the tree.\n\n"
        "```java\n"
        "boolean search(TreeNode n, int v) {\n"
        "    while (n != null) {\n"
        "        if (n.val == v) return true;\n"
        "        n = (v < n.val) ? n.left : n.right;   // discard half\n"
        "    }\n"
        "    return false;\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'sorted tree'*, *'kth smallest'*, *'validate BST'*, *'range'*. Inorder of a BST is **sorted** — many BST problems are 'do X to a sorted stream'.\n\n"
        "## The validation trap\n"
        "Checking only immediate children is wrong. A node deep on the left must still be below an ancestor. Carry a **range**:\n\n"
        "| node | allowed (low, high) |\n"
        "|---|---|\n"
        "| root 5 | (-inf, +inf) |\n"
        "| left 3 | (-inf, 5) |\n"
        "| 3.right 4 | (3, 5) |\n"
        "| right 8 | (5, +inf) |\n"
    ),
    "tree_dp": (
        "# Tree DP — Postorder Aggregation\n\n"
        "When a node's answer depends on its subtrees, compute **bottom-up**: recurse both sides, then combine. The trick in problems like *diameter* and *max path sum* is returning **one** value upward while recording **another** globally.\n\n"
        "```java\n"
        "int best = 0;\n"
        "int height(TreeNode n) {          // returns height, updates diameter\n"
        "    if (n == null) return 0;\n"
        "    int L = height(n.left), R = height(n.right);\n"
        "    best = Math.max(best, L + R);  // path THROUGH n (can't go up)\n"
        "    return 1 + Math.max(L, R);     // value handed to the parent\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'longest path'*, *'balanced'*, *'diameter'*, *'max path sum'*, *'sum of subtree'*. If the answer can bend at a node but a parent can only take one side, you need the return-one / record-other split.\n\n"
        "## Simulated solve — diameter of `1 2 3 4 5`\n"
        "| node | L | R | best=max(best,L+R) | returns |\n"
        "|---|---|---|---|---|\n"
        "| 4 | 0 | 0 | 0 | 1 |\n"
        "| 5 | 0 | 0 | 0 | 1 |\n"
        "| 2 | 1 | 1 | 2 | 2 |\n"
        "| 3 | 0 | 0 | 2 | 1 |\n"
        "| 1 | 2 | 1 | 3 | 3 |\n"
    ),
})

# --- Trees: Learn drills ----------------------------------------------------
_EX_MAXDEPTH = _EXJ_TREE_HEAD + (
    "    static int depth(TreeNode n) {\n"
    "        if (n == null) return 0;\n"
    "        return 1 + Math.max(depth(n.left), depth(n.right));\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
    "        String[] a = line.trim().isEmpty() ? new String[0] : line.trim().split(\"\\\\s+\");\n"
    "        System.out.println(depth(build(a)));\n"
    "    }\n}\n"
)
_EX_INORDER = _EXJ_TREE_HEAD + (
    "    static void inorder(TreeNode n, List<Integer> out) {\n"
    "        if (n == null) return;\n"
    "        inorder(n.left, out);\n"
    "        out.add(n.val);\n"
    "        inorder(n.right, out);\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
    "        String[] a = line.trim().isEmpty() ? new String[0] : line.trim().split(\"\\\\s+\");\n"
    "        List<Integer> out = new ArrayList<>();\n"
    "        inorder(build(a), out);\n"
    "        StringBuilder sb = new StringBuilder();\n"
    "        for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append(' '); sb.append(out.get(i)); }\n"
    "        System.out.println(sb.toString());\n"
    "    }\n}\n"
)
_EX_BSTSEARCH = _EXJ_TREE_HEAD + (
    "    static boolean search(TreeNode n, int v) {\n"
    "        while (n != null) {\n"
    "            if (n.val == v) return true;\n"
    "            n = (v < n.val) ? n.left : n.right;\n"
    "        }\n"
    "        return false;\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        String line = sc.nextLine();\n"
    "        int v = Integer.parseInt(sc.nextLine().trim());\n"
    "        String[] a = line.trim().isEmpty() ? new String[0] : line.trim().split(\"\\\\s+\");\n"
    "        System.out.println(search(build(a), v) ? \"true\" : \"false\");\n"
    "    }\n}\n"
)
_EX_DIAMETER = _EXJ_TREE_HEAD + (
    "    static int best = 0;\n"
    "    static int height(TreeNode n) {\n"
    "        if (n == null) return 0;\n"
    "        int L = height(n.left), R = height(n.right);\n"
    "        best = Math.max(best, L + R);\n"
    "        return 1 + Math.max(L, R);\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        String line = sc.hasNextLine() ? sc.nextLine() : \"\";\n"
    "        String[] a = line.trim().isEmpty() ? new String[0] : line.trim().split(\"\\\\s+\");\n"
    "        height(build(a));\n"
    "        System.out.println(best);\n"
    "    }\n}\n"
)
EXERCISES.update({
    "tree_basics": [
        ex("tree_basics-size", "Count the nodes",
           "The recursion is set up. Fill the blank so `depth` returns 1 plus the deeper child (this drill measures height).",
           _EX_MAXDEPTH, ["1 + Math.max(depth(n.left), depth(n.right))"],
           [("3 9 20 null null 15 7", "3"), ("1", "1"), ("1 2 null 3", "3")],
           hint="Height = 1 + the taller of the two subtrees.", source_slug="max-depth-tree"),
        ex("tree_basics-base", "The base case",
           "Every tree recursion needs a base case. Fill the blank so an empty subtree contributes height 0.",
           _EX_MAXDEPTH, ["if (n == null) return 0;"],
           [("1 2 3", "2"), ("1", "1"), ("", "0")],
           hint="When the node is null there is nothing below it — return 0.", source_slug="max-depth-tree"),
    ],
    "tree_traversal": [
        ex("tree_traversal-inorder-visit", "Inorder: visit between",
           "Inorder is left, node, right. Fill the blank so the node's value is recorded between the two recursive calls.",
           _EX_INORDER, ["out.add(n.val);"],
           [("1 null 2 3", "1 3 2"), ("5 3 8 2 4 7 9", "2 3 4 5 7 8 9"), ("1", "1")],
           hint="Append n.val between inorder(left) and inorder(right).", source_slug="inorder-traversal"),
        ex("tree_traversal-inorder-left", "Inorder: recurse left first",
           "Fill the blank so the traversal descends into the left subtree before recording the node.",
           _EX_INORDER, ["inorder(n.left, out);"],
           [("5 3 8 2 4 7 9", "2 3 4 5 7 8 9"), ("2 1", "1 2"), ("1", "1")],
           hint="Go all the way left before you emit anything.", source_slug="inorder-traversal"),
    ],
    "bst": [
        ex("bst-descend", "Descend a BST",
           "Fill the blank so the search goes left when `v` is smaller than the node, otherwise right.",
           _EX_BSTSEARCH, ["n = (v < n.val) ? n.left : n.right;"],
           [("5 3 8 2 4 7 9\n7", "true"), ("5 3 8 2 4 7 9\n6", "false"), ("5\n5", "true")],
           hint="Compare v with n.val to pick the child.", source_slug="bst-search"),
    ],
    "tree_dp": [
        ex("tree_dp-through", "Path through a node",
           "The height recursion is written. Fill the blank so `best` records the longest path *through* the current node (left height + right height).",
           _EX_DIAMETER, ["best = Math.max(best, L + R);"],
           [("1 2 3 4 5", "3"), ("1 2 null 3", "2"), ("1", "0")],
           hint="A path bending at n uses both sides: L + R edges.", source_slug="diameter-of-tree"),
        ex("tree_dp-return", "What to hand the parent",
           "Fill the blank so `height` returns the value a parent needs: 1 plus the taller side.",
           _EX_DIAMETER, ["return 1 + Math.max(L, R);"],
           [("1 2 3 4 5", "3"), ("1", "0"), ("1 2 3", "2")],
           hint="A parent can only extend one side, so return the taller child + 1.", source_slug="diameter-of-tree"),
    ],
})

PREREQS.update({
    "max-depth-tree": [("tree_basics", "The height recursion is the base tree DFS."), ("recursion", "Base case null → 0.")],
    "min-depth-tree": [("tree_traversal", "BFS finds the shallowest leaf fastest."), ("tree_basics", "Mind one-child nodes.")],
    "count-nodes-tree": [("tree_basics", "1 + count(left) + count(right).")],
    "invert-binary-tree": [("tree_traversal", "Swap during any traversal."), ("recursion", "Recurse both children.")],
    "same-tree": [("tree_traversal", "Parallel DFS over both trees.")],
    "symmetric-tree": [("tree_traversal", "Mirror comparison crosses sides.")],
    "inorder-traversal": [("tree_traversal", "Left, node, right.")],
    "preorder-traversal": [("tree_traversal", "Node, left, right.")],
    "level-order-traversal": [("tree_traversal", "BFS with a queue."), ("queue", "One level per outer step.")],
    "right-side-view": [("tree_traversal", "Last node of each BFS level.")],
    "zigzag-level-order": [("tree_traversal", "Reverse alternate levels.")],
    "path-sum-exists": [("tree_basics", "Carry the remaining target down."), ("recursion", "Leaf check.")],
    "balanced-tree": [("tree_dp", "Bubble up a -1 sentinel.")],
    "diameter-of-tree": [("tree_dp", "best = L + R while returning height.")],
    "max-path-sum": [("tree_dp", "Clamp negative gains; split at each node."), ("recursion", "Post-order.")],
    "validate-bst": [("bst", "Carry a (low, high) range."), ("tree_traversal", "Or check inorder is increasing.")],
    "bst-search": [("bst", "Compare and pick a child.")],
    "bst-insert": [("bst", "Attach a new leaf at the search's end.")],
    "kth-smallest-bst": [("bst", "Inorder is sorted."), ("tree_traversal", "Stop after k.")],
    "lca-bst": [("bst", "Split point by comparison.")],
    "lca-binary-tree": [("tree_dp", "Both sides return → this node."), ("recursion", "Post-order search.")],
})

FLASHCARDS += [
    ("Tree question — which traversal for 'sorted values' in a BST?", "Inorder (left, node, right) emits BST values in sorted order.", "seed:tree_traversal"),
    ("Tree question — 'shallowest leaf' / per-level answer?", "BFS with a queue, one level at a time.", "seed:tree_traversal"),
    ("Validate a BST — why isn't checking children enough?", "A node must respect ancestors too; carry a (low, high) range down.", "seed:bst"),
    ("Diameter / max-path-sum trick?", "Postorder: RETURN one side up (height/gain), RECORD both sides (L+R) in a global best.", "seed:tree_dp"),
    ("Lowest common ancestor in a plain binary tree?", "DFS; the node where left and right subtrees each return a target is the LCA.", "seed:tree_dp"),
]

# --- Trees: references (verify_seeds trust) --------------------------------
_REF_MAXDEPTH_J = _TREE_PRELUDE_JAVA + "class Solution {\n    int solve(String[] level) {\n        return depth(TreeUtil.build(level));\n    }\n    int depth(TreeNode n) { return n == null ? 0 : 1 + Math.max(depth(n.left), depth(n.right)); }\n}\n"
_REF_MAXDEPTH_P = _TREE_PRELUDE_PY + "def solve(level):\n    def d(n):\n        return 0 if n is None else 1 + max(d(n.left), d(n.right))\n    return d(build_tree(level))\n"

EXPANSION_REFS.update({
    "max-depth-tree": {"java": _REF_MAXDEPTH_J, "python": _REF_MAXDEPTH_P},
    "invert-binary-tree": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    String[] solve(String[] level) {\n        return TreeUtil.ser(inv(TreeUtil.build(level)));\n    }\n    TreeNode inv(TreeNode n){ if(n==null) return null; TreeNode t=n.left; n.left=inv(n.right); n.right=inv(t); return n; }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level):\n    def inv(n):\n        if n is None: return None\n        n.left, n.right = inv(n.right), inv(n.left)\n        return n\n    return ser_tree(inv(build_tree(level)))\n",
    },
    "same-tree": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    boolean solve(String[] a, String[] b){ return eq(TreeUtil.build(a), TreeUtil.build(b)); }\n    boolean eq(TreeNode x, TreeNode y){ if(x==null&&y==null) return true; if(x==null||y==null||x.val!=y.val) return false; return eq(x.left,y.left)&&eq(x.right,y.right); }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(a, b):\n    def eq(x, y):\n        if x is None and y is None: return True\n        if x is None or y is None or x.val != y.val: return False\n        return eq(x.left, y.left) and eq(x.right, y.right)\n    return eq(build_tree(a), build_tree(b))\n",
    },
    "inorder-traversal": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    int[] solve(String[] level){ List<Integer> o=new ArrayList<>(); go(TreeUtil.build(level),o); int[] r=new int[o.size()]; for(int i=0;i<r.length;i++) r[i]=o.get(i); return r; }\n    void go(TreeNode n, List<Integer> o){ if(n==null) return; go(n.left,o); o.add(n.val); go(n.right,o); }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level):\n    o=[]\n    def go(n):\n        if n is None: return\n        go(n.left); o.append(n.val); go(n.right)\n    go(build_tree(level)); return o\n",
    },
    "validate-bst": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    boolean solve(String[] level){ return ok(TreeUtil.build(level), Long.MIN_VALUE, Long.MAX_VALUE); }\n    boolean ok(TreeNode n, long lo, long hi){ if(n==null) return true; if(!(lo<n.val && n.val<hi)) return false; return ok(n.left,lo,n.val)&&ok(n.right,n.val,hi); }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level):\n    def ok(n, lo, hi):\n        if n is None: return True\n        if not (lo < n.val < hi): return False\n        return ok(n.left, lo, n.val) and ok(n.right, n.val, hi)\n    return ok(build_tree(level), -(10**18), 10**18)\n",
    },
    "level-order-traversal": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    int[] solve(String[] level){ TreeNode r=TreeUtil.build(level); List<Integer> o=new ArrayList<>(); if(r==null) return new int[0]; ArrayDeque<TreeNode> q=new ArrayDeque<>(); q.add(r); while(!q.isEmpty()){ TreeNode n=q.poll(); o.add(n.val); if(n.left!=null) q.add(n.left); if(n.right!=null) q.add(n.right);} int[] a=new int[o.size()]; for(int i=0;i<a.length;i++) a[i]=o.get(i); return a; }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level):\n    r=build_tree(level)\n    if not r: return []\n    o=[]; q=deque([r])\n    while q:\n        n=q.popleft(); o.append(n.val)\n        if n.left: q.append(n.left)\n        if n.right: q.append(n.right)\n    return o\n",
    },
    "diameter-of-tree": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    int best=0;\n    int solve(String[] level){ h(TreeUtil.build(level)); return best; }\n    int h(TreeNode n){ if(n==null) return 0; int L=h(n.left), R=h(n.right); best=Math.max(best,L+R); return 1+Math.max(L,R); }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level):\n    best=[0]\n    def h(n):\n        if n is None: return 0\n        L=h(n.left); R=h(n.right); best[0]=max(best[0],L+R); return 1+max(L,R)\n    h(build_tree(level)); return best[0]\n",
    },
    "lca-binary-tree": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    int p,q;\n    int solve(String[] level, int p, int q){ this.p=p; this.q=q; TreeNode r=dfs(TreeUtil.build(level)); return r==null?-1:r.val; }\n    TreeNode dfs(TreeNode n){ if(n==null) return null; if(n.val==p||n.val==q) return n; TreeNode L=dfs(n.left), R=dfs(n.right); if(L!=null&&R!=null) return n; return L!=null?L:R; }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level, p, q):\n    def dfs(n):\n        if n is None: return None\n        if n.val in (p, q): return n\n        L=dfs(n.left); R=dfs(n.right)\n        if L and R: return n\n        return L or R\n    r=dfs(build_tree(level)); return r.val if r else -1\n",
    },
    "kth-smallest-bst": {
        "java": _TREE_PRELUDE_JAVA + "class Solution {\n    int solve(String[] level, int k){ List<Integer> o=new ArrayList<>(); go(TreeUtil.build(level),o); return o.get(k-1); }\n    void go(TreeNode n, List<Integer> o){ if(n==null) return; go(n.left,o); o.add(n.val); go(n.right,o); }\n}\n",
        "python": _TREE_PRELUDE_PY + "def solve(level, k):\n    o=[]\n    def go(n):\n        if n is None: return\n        go(n.left); o.append(n.val); go(n.right)\n    go(build_tree(level)); return o[k-1]\n",
    },
})

# ===========================================================================
# DOMAIN 2 — LINKED LISTS   (encoded as int[] values; cycles add int pos)
# ===========================================================================

_LIST_PRELUDE_JAVA = (
    "import java.util.*;\n"
    "class ListNode { int val; ListNode next; ListNode(int v){ val = v; } }\n"
    "class ListUtil {\n"
    "    static ListNode build(int[] a){ ListNode dummy=new ListNode(0), t=dummy; for(int x:a){ t.next=new ListNode(x); t=t.next; } return dummy.next; }\n"
    "    static int[] ser(ListNode h){ List<Integer> o=new ArrayList<>(); while(h!=null){ o.add(h.val); h=h.next; } int[] r=new int[o.size()]; for(int i=0;i<r.length;i++) r[i]=o.get(i); return r; }\n"
    "    static ListNode buildCycle(int[] a, int pos){ ListNode dummy=new ListNode(0), t=dummy, cyc=null; int idx=0; for(int x:a){ t.next=new ListNode(x); t=t.next; if(idx==pos) cyc=t; idx++; } if(pos>=0) t.next=cyc; return dummy.next; }\n"
    "    static int indexOf(ListNode h, ListNode target){ int i=0; while(h!=null){ if(h==target) return i; h=h.next; i++; } return -1; }\n"
    "}\n"
)
_LIST_PRELUDE_PY = (
    "class ListNode:\n"
    "    def __init__(self, v): self.val = v; self.next = None\n"
    "def build_list(a):\n"
    "    dummy = ListNode(0); t = dummy\n"
    "    for x in a: t.next = ListNode(x); t = t.next\n"
    "    return dummy.next\n"
    "def ser_list(h):\n"
    "    o = []\n"
    "    while h: o.append(h.val); h = h.next\n"
    "    return o\n"
    "def build_cycle(a, pos):\n"
    "    dummy = ListNode(0); t = dummy; cyc = None\n"
    "    for i, x in enumerate(a):\n"
    "        t.next = ListNode(x); t = t.next\n"
    "        if i == pos: cyc = t\n"
    "    if pos >= 0 and t: t.next = cyc\n"
    "    return dummy.next\n"
)


def _list_starters(spec, note="TODO: implement", cyclic=False):
    jparams = ", ".join("%s %s" % (_JAVA_TY[p["type"]], p["name"]) for p in spec["params"])
    pparams = ", ".join(p["name"] for p in spec["params"])
    first = spec["params"][0]["name"]
    if cyclic:
        sec = spec["params"][1]["name"]
        jbuild = "        ListNode head = ListUtil.buildCycle(%s, %s);\n" % (first, sec)
        pbuild = "    head = build_cycle(%s, %s)\n" % (first, sec)
    else:
        jbuild = "        ListNode head = ListUtil.build(%s);\n" % first
        pbuild = "    head = build_list(%s)\n" % first
    java = (_LIST_PRELUDE_JAVA + "class Solution {\n"
            + "    %s %s(%s) {\n" % (_JAVA_TY[spec["returns"]], spec["name"], jparams)
            + jbuild + "        // %s\n        return %s;\n    }\n}\n" % (note, _java_default(spec["returns"])))
    python = (_LIST_PRELUDE_PY + "def %s(%s):\n" % (spec["name"], pparams)
              + pbuild + "    # %s\n    return %s\n" % (note, _py_default(spec["returns"])))
    return java, python


def _ll_dedup(v):
    out = []
    for x in v:
        if not out or out[-1] != x:
            out.append(x)
    return out


def _ll_merge(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out


def _ll_remove_nth(v, n):
    if n <= 0 or n > len(v):
        return list(v)
    idx = len(v) - n
    return v[:idx] + v[idx + 1:]


def _ll_odd_even(v):
    return v[0::2] + v[1::2]


def _ll_add(a, b):
    na = sum(d * (10 ** i) for i, d in enumerate(a))
    nb = sum(d * (10 ** i) for i, d in enumerate(b))
    s = na + nb
    if s == 0:
        return [0]
    out = []
    while s > 0:
        out.append(s % 10); s //= 10
    return out


def _ll_reorder(v):
    i, j = 0, len(v) - 1
    out = []
    turn = True
    while i <= j:
        if turn:
            out.append(v[i]); i += 1
        else:
            out.append(v[j]); j -= 1
        turn = not turn
    return out


def _ll_rkg(v, k):
    out = []
    n = len(v)
    i = 0
    while i + k <= n and k > 1:
        out.extend(v[i:i + k][::-1]); i += k
    out.extend(v[i:])
    return out


def _lspec(extra=None, ret="int[]"):
    return {"name": "solve", "params": [{"name": "vals", "type": "int[]"}] + (extra or []), "returns": ret}


def _list_def(slug, title, diff, extra, ret, fn, desc, hints, opt, editorial,
              cases, companies, subtopics, example_expl, note="TODO: implement", cyclic=False):
    spec = _lspec(extra, ret)
    sj, sp = _list_starters(spec, note, cyclic)
    return dict(
        slug=slug, title=title, difficulty=diff,
        topics=["Linked Lists"], subtopics=subtopics, companies=companies,
        description=desc,
        constraints="The list values are given as an array; the starter builds the nodes for you.\n0 ≤ length ≤ 10^4.",
        hints=hints, opt=opt, editorial=editorial,
        spec=spec, fn=fn, starter_py=sp, starter_java=sj,
        cases=cases, example_expl=example_expl,
    )


HARNESS_DEFS += [
    _list_def(
        "list-length", "Length of a Linked List", "Intro",
        None, "int", lambda v: len(v),
        "Return the number of nodes in the linked list.",
        ["Walk from the head following `next` until null.", "Count each node you pass.",
         "No size field — you must traverse.", "`while (node != null) { count++; node = node.next; }`"],
        ("O(n)", "O(1)", "One traversal."),
        "## Approach\nWalk the list with a pointer, counting nodes until you hit null.",
        [("example", "Four", ([1, 2, 3, 4],)), ("example", "Empty", ([],)),
         ("hidden", "One", ([9],)), ("hidden", "Repeats", ([5, 5, 5],)), ("hidden", "Longer", ([1, 2, 3, 4, 5, 6],))],
        ["Amazon"], ["Traversal"], ["Four nodes.", "Empty list has length 0."],
        note="walk with node = node.next, counting",
    ),
    _list_def(
        "list-get-nth", "Get Nth Node Value", "Intro",
        [{"name": "k", "type": "int"}], "int", lambda v, k: v[k - 1],
        "Return the value of the **k-th** node (1-indexed).",
        ["Step forward k-1 times from the head.", "Then read the current node's value.",
         "No random access — walk node by node.", "Guaranteed 1 ≤ k ≤ length."],
        ("O(k)", "O(1)", "Advance k-1 steps."),
        "## Approach\nAdvance a pointer k-1 times, then return its value.",
        [("example", "3rd", ([10, 20, 30, 40], 3)), ("example", "1st", ([7], 1)),
         ("hidden", "Last", ([1, 2, 3], 3)), ("hidden", "Second", ([5, 6], 2)), ("hidden", "Mid", ([1, 2, 3, 4, 5], 4))],
        ["Amazon"], ["Traversal"], ["3rd node holds 30.", "1st node holds 7."],
        note="advance k-1 steps, then read node.val",
    ),
    _list_def(
        "reverse-linked-list", "Reverse Linked List", "Easy",
        None, "int[]", lambda v: v[::-1],
        "**Reverse** the linked list and return the values of the new list.",
        ["Keep three pointers: prev, cur, next.", "Save cur.next before you overwrite it.",
         "Point cur.next back to prev, then advance both.", "`cur.next = prev; prev = cur; cur = next;`"],
        ("O(n)", "O(1)", "One pass, pointers rewired in place."),
        "## Approach\nIterate with prev/cur; reverse each link; prev ends as the new head.",
        [("example", "Four", ([1, 2, 3, 4],)), ("example", "One", ([5],)),
         ("hidden", "Empty", ([],)), ("hidden", "Two", ([9, 8],)), ("hidden", "Longer", ([1, 1, 2, 3, 5, 8],))],
        ["Amazon", "Microsoft", "Apple"], ["In-place Reversal"],
        ["[1,2,3,4] → [4,3,2,1].", "A single node is unchanged."],
        note="prev/cur/next three-pointer reversal",
    ),
    _list_def(
        "middle-of-list", "Middle of the Linked List", "Easy",
        None, "int", lambda v: v[len(v) // 2],
        "Return the value of the **middle** node. For an even count, return the **second** of the two middle nodes.",
        ["Advance a slow pointer by 1 and a fast pointer by 2.", "When fast falls off the end, slow is at the middle.",
         "For even length this lands on the second middle.", "`while (fast != null && fast.next != null)`"],
        ("O(n)", "O(1)", "Single fast/slow pass."),
        "## Approach\nFast/slow pointers; when fast reaches the end, slow is the middle.",
        [("example", "Odd", ([1, 2, 3, 4, 5],)), ("example", "Even", ([1, 2, 3, 4, 5, 6],)),
         ("hidden", "One", ([7],)), ("hidden", "Two", ([1, 2],)), ("hidden", "Three", ([9, 8, 7],))],
        ["Amazon", "Google"], ["Fast & Slow"],
        ["Middle of 5 nodes is the 3rd, value 3.", "Second middle of 6 is the 4th, value 4."],
        note="slow += 1, fast += 2; return slow.val",
    ),
    _list_def(
        "remove-duplicates-sorted-list", "Remove Duplicates from Sorted List", "Easy",
        None, "int[]", _ll_dedup,
        "The list is **sorted**. Remove nodes with duplicate values so each value appears once; return the remaining values.",
        ["Because it's sorted, duplicates are adjacent.", "Compare each node with the next.",
         "Skip a node whose value equals the current one.", "Splice out duplicates by relinking next."],
        ("O(n)", "O(1)", "One pass, relinking."),
        "## Approach\nWalk the list; when node.val == node.next.val, unlink the next node.",
        [("example", "Dupes", ([1, 1, 2, 3, 3],)), ("example", "None", ([1, 2, 3],)),
         ("hidden", "All same", ([4, 4, 4],)), ("hidden", "Empty", ([],)), ("hidden", "Pairs", ([1, 1, 2, 2, 3, 3],))],
        ["Microsoft"], ["Traversal"],
        ["[1,1,2,3,3] → [1,2,3].", "Already unique."],
        note="skip node when node.val == node.next.val",
    ),
    dict(
        slug="merge-two-sorted-lists", title="Merge Two Sorted Lists", difficulty="Easy",
        topics=["Linked Lists"], subtopics=["Dummy Head"], companies=["Amazon", "Microsoft", "Apple"],
        description="Merge two **sorted** linked lists into one sorted list and return its values.",
        constraints="Both inputs are sorted ascending.\n0 ≤ each length ≤ 10^4.",
        hints=["Use a dummy head to simplify appending.", "Compare the two front nodes; attach the smaller.",
               "Advance the list you took from.", "Append the leftover tail when one list empties."],
        opt=("O(n+m)", "O(1)", "Each node is spliced once behind a dummy head."),
        editorial="## Approach\nDummy head + tail pointer; repeatedly attach the smaller front node, then the remaining tail.",
        spec={"name": "solve", "params": [{"name": "a", "type": "int[]"}, {"name": "b", "type": "int[]"}], "returns": "int[]"},
        fn=lambda a, b: _ll_merge(a, b),
        starter_java=_LIST_PRELUDE_JAVA + "class Solution {\n    int[] solve(int[] a, int[] b) {\n        ListNode ha = ListUtil.build(a), hb = ListUtil.build(b);\n        // TODO: merge with a dummy head\n        return new int[]{};\n    }\n}\n",
        starter_py=_LIST_PRELUDE_PY + "def solve(a, b):\n    ha = build_list(a); hb = build_list(b)\n    # TODO: merge with a dummy head\n    return []\n",
        cases=[("example", "Interleave", ([1, 2, 4], [1, 3, 4])), ("example", "One empty", ([], [0])),
               ("hidden", "First empty", ([], [1])), ("hidden", "Disjoint", ([1, 2, 3], [4, 5, 6])), ("hidden", "Overlap", ([2, 2], [1, 2]))],
        example_expl=["Merges to 1,1,2,3,4,4.", "Only the non-empty list remains."],
    ),
    _list_def(
        "remove-nth-from-end", "Remove Nth Node From End of List", "Medium",
        [{"name": "n", "type": "int"}], "int[]", lambda v, n: _ll_remove_nth(v, n),
        "Remove the **n-th node from the end** (1-indexed) and return the remaining values.",
        ["Use two pointers a gap of n apart.", "Advance the lead pointer n steps first.",
         "Move both until the lead hits the end.", "A dummy head handles removing the head cleanly."],
        ("O(n)", "O(1)", "Single pass with a gap of n."),
        "## Approach\nAdvance a fast pointer n nodes ahead, then move fast and slow together; slow stops before the target.",
        [("example", "2nd from end", ([1, 2, 3, 4, 5], 2)), ("example", "Head", ([1, 2], 2)),
         ("hidden", "Only node", ([7], 1)), ("hidden", "Last", ([1, 2, 3], 1)), ("hidden", "First of many", ([1, 2, 3, 4], 4))],
        ["Facebook", "Amazon"], ["Fast & Slow"],
        ["Removes the 4, leaving [1,2,3,5].", "Removes the head, leaving [2]."],
        note="gap of n between fast and slow",
    ),
    _list_def(
        "palindrome-linked-list", "Palindrome Linked List", "Medium",
        None, "bool", lambda v: v == v[::-1],
        "Return `true` if the linked list reads the same forwards and backwards.",
        ["Find the middle with fast/slow.", "Reverse the second half.",
         "Compare the two halves node by node.", "O(1) space if you rewire instead of copying."],
        ("O(n)", "O(1)", "Middle + reverse-half + compare, all in place."),
        "## Approach\nFast/slow to the middle, reverse the second half, then walk both halves comparing values.",
        [("example", "Palindrome", ([1, 2, 2, 1],)), ("example", "Not", ([1, 2, 3],)),
         ("hidden", "Single", ([1],)), ("hidden", "Odd palindrome", ([1, 2, 1],)), ("hidden", "Empty", ([],))],
        ["Amazon", "Facebook"], ["Fast & Slow"],
        ["[1,2,2,1] mirrors itself.", "[1,2,3] does not."],
        note="middle via fast/slow, reverse half, compare",
    ),
    _list_def(
        "odd-even-list", "Odd Even Linked List", "Medium",
        None, "int[]", _ll_odd_even,
        "Group all nodes at **odd positions** (1st, 3rd, 5th, …) followed by all nodes at **even positions**, preserving relative order. Return the values.",
        ["Group by node position (1-indexed), not by value.", "Weave two chains: odd-indexed and even-indexed.",
         "Keep an odd tail and an even tail.", "Finally link the odd tail to the even head."],
        ("O(n)", "O(1)", "One pass rewiring into two interleaved chains."),
        "## Approach\nMaintain odd and even sub-lists; stitch odd→even at the end.",
        [("example", "Five", ([1, 2, 3, 4, 5],)), ("example", "Six", ([2, 1, 3, 5, 6, 4],)),
         ("hidden", "One", ([7],)), ("hidden", "Two", ([1, 2],)), ("hidden", "Empty", ([],))],
        ["Microsoft"], ["Traversal"],
        ["Positions 1,3,5 then 2,4 → 1,3,5,2,4.", "→ 2,3,6,1,5,4."],
        note="odd-position chain then even-position chain",
    ),
    dict(
        slug="add-two-numbers-list", title="Add Two Numbers", difficulty="Medium",
        topics=["Linked Lists"], subtopics=["Traversal"], companies=["Amazon", "Microsoft", "Bloomberg"],
        description=("Two non-negative numbers are stored as linked lists with the **least-significant digit first** "
                     "(so `342` is `2 -> 4 -> 3`). Return their sum as a list in the same order."),
        constraints="Each node holds a single digit 0–9.\nNo leading zeros except the number 0 itself.",
        hints=["Add digit by digit from the heads, carrying overflow.", "The carry is sum / 10; the digit is sum % 10.",
               "Continue while either list has digits or a carry remains.", "Build the result with a dummy head."],
        opt=("O(n)", "O(n)", "One pass over both lists with a carry."),
        editorial="## Approach\nWalk both lists together; at each step add the two digits plus carry, emit sum%10, keep sum/10 as carry.",
        spec={"name": "solve", "params": [{"name": "a", "type": "int[]"}, {"name": "b", "type": "int[]"}], "returns": "int[]"},
        fn=lambda a, b: _ll_add(a, b),
        starter_java=_LIST_PRELUDE_JAVA + "class Solution {\n    int[] solve(int[] a, int[] b) {\n        ListNode ha = ListUtil.build(a), hb = ListUtil.build(b);\n        // TODO: add digit by digit with a carry\n        return new int[]{};\n    }\n}\n",
        starter_py=_LIST_PRELUDE_PY + "def solve(a, b):\n    ha = build_list(a); hb = build_list(b)\n    # TODO: add digit by digit with a carry\n    return []\n",
        cases=[("example", "342+465", ([2, 4, 3], [5, 6, 4])), ("example", "Carry out", ([9, 9], [1])),
               ("hidden", "Zero", ([0], [0])), ("hidden", "Diff length", ([1], [9, 9, 9])), ("hidden", "No carry", ([1, 2], [3, 4]))],
        example_expl=["342 + 465 = 807 → 7,0,8.", "99 + 1 = 100 → 0,0,1."],
    ),
    _list_def(
        "has-cycle", "Linked List Cycle", "Medium",
        [{"name": "pos", "type": "int"}], "bool", lambda v, pos: pos != -1 and len(v) > 0,
        ("Return `true` if the linked list contains a **cycle**. Input is the node values plus `pos`, the 0-based index "
         "the tail's `next` points back to (or `-1` for no cycle). The starter builds the (possibly cyclic) list for you."),
        ["Use Floyd's tortoise and hare.", "Slow moves 1, fast moves 2.",
         "If they ever meet, there's a cycle.", "If fast reaches null, there is none."],
        ("O(n)", "O(1)", "Two pointers meet inside any cycle."),
        "## Approach\nFloyd's cycle detection: advance slow by 1 and fast by 2; a meeting implies a cycle.",
        [("example", "Cycle at 1", ([3, 2, 0, -4], 1)), ("example", "No cycle", ([1, 2], -1)),
         ("hidden", "Self loop", ([1], 0)), ("hidden", "Single no cycle", ([1], -1)), ("hidden", "Cycle at 0", ([1, 2, 3], 0))],
        ["Amazon", "Microsoft"], ["Fast & Slow"],
        ["Tail links back to index 1 → cycle.", "pos = -1 → no cycle."],
        note="Floyd fast/slow; meeting means a cycle", cyclic=True,
    ),
    _list_def(
        "cycle-start-index", "Linked List Cycle II", "Medium",
        [{"name": "pos", "type": "int"}], "int", lambda v, pos: pos if (pos != -1 and len(v) > 0) else -1,
        ("Return the **0-based index** of the node where the cycle begins, or `-1` if there is none. Input is the values "
         "plus `pos` (where the tail links back). The starter builds the list; you must find the entry node."),
        ["First detect the meeting point with fast/slow.", "Then reset one pointer to the head.",
         "Advance both by 1; they meet at the cycle's start.", "Report that node's index from the head."],
        ("O(n)", "O(1)", "Floyd phase 1 (meet) + phase 2 (find entry)."),
        "## Approach\nAfter slow/fast meet, move one pointer to head and step both by 1; they converge on the cycle entry.",
        [("example", "Entry at 1", ([3, 2, 0, -4], 1)), ("example", "No cycle", ([1, 2, 3], -1)),
         ("hidden", "Entry 0", ([1, 2], 0)), ("hidden", "Self", ([5], 0)), ("hidden", "Entry 2", ([1, 2, 3, 4], 2))],
        ["Amazon", "Google"], ["Fast & Slow"],
        ["Cycle enters at index 1.", "No cycle → -1."],
        note="Floyd phase 2: reset to head, step both by 1", cyclic=True,
    ),
    _list_def(
        "reorder-list", "Reorder List", "Medium",
        None, "int[]", _ll_reorder,
        "Reorder the list as L0 → Ln → L1 → Ln-1 → L2 → … (first, last, second, second-last, …). Return the values.",
        ["Find the middle with fast/slow.", "Reverse the second half.",
         "Merge the two halves alternately.", "Combine three classic sub-steps."],
        ("O(n)", "O(1)", "Middle + reverse + interleave, in place."),
        "## Approach\nSplit at the middle, reverse the tail, then weave the front and reversed-back alternately.",
        [("example", "Four", ([1, 2, 3, 4],)), ("example", "Five", ([1, 2, 3, 4, 5],)),
         ("hidden", "One", ([1],)), ("hidden", "Two", ([1, 2],)), ("hidden", "Three", ([1, 2, 3],))],
        ["Facebook", "Amazon"], ["Fast & Slow"],
        ["[1,2,3,4] → 1,4,2,3.", "[1,2,3,4,5] → 1,5,2,4,3."],
        note="middle + reverse second half + interleave",
    ),
    _list_def(
        "reverse-k-group", "Reverse Nodes in k-Group", "Hard",
        [{"name": "k", "type": "int"}], "int[]", lambda v, k: _ll_rkg(v, k),
        "Reverse the nodes of the list **k at a time**. Any leftover group of fewer than k nodes stays in original order. Return the values.",
        ["Reverse each block of exactly k nodes.", "Check there are k nodes left before reversing a block.",
         "A group smaller than k is left as-is.", "Careful pointer surgery links reversed blocks together."],
        ("O(n)", "O(1)", "Each node reversed at most once."),
        "## Approach\nWalk in blocks of k: if k nodes remain, reverse them and connect to the previous block; otherwise stop.",
        [("example", "k=2", ([1, 2, 3, 4, 5], 2)), ("example", "k=3", ([1, 2, 3, 4, 5], 3)),
         ("hidden", "k=1", ([1, 2, 3], 1)), ("hidden", "Exact", ([1, 2, 3, 4], 2)), ("hidden", "k>n", ([1, 2], 3))],
        ["Facebook", "Amazon", "Google"], ["In-place Reversal"],
        ["[1,2,3,4,5],k=2 → 2,1,4,3,5.", "k=3 → 3,2,1,4,5."],
        note="reverse full blocks of k, leave remainder",
    ),
]

CONCEPTS.update({
    "list_basics": {
        "name": "Linked Lists",
        "what": "A chain of nodes where each holds a value and a pointer to the next node; the dummy-head trick simplifies edits.",
        "deep": "Unlike arrays, linked lists give O(1) insertion/removal once you hold the right node but no random access — you must walk from the head. Most bugs come from losing a pointer before you use it (save node.next first) or from special-casing the head, which a sentinel 'dummy' node removes.",
        "java": "class ListNode { int val; ListNode next; }. Use a dummy head: ListNode dummy = new ListNode(0); build/append behind a tail pointer, return dummy.next.",
    },
    "list_reversal": {
        "name": "In-place List Reversal",
        "what": "Flipping the direction of `next` pointers using a rolling prev/cur/next trio.",
        "deep": "Reversal is the backbone of palindrome checks, reorder, and k-group problems. The invariant: prev is the already-reversed prefix, cur is the next node to flip. You must cache cur.next before overwriting it, or you lose the rest of the list.",
        "java": "ListNode prev=null, cur=head; while(cur!=null){ ListNode nx=cur.next; cur.next=prev; prev=cur; cur=nx; } return prev;",
    },
    "fast_slow": {
        "name": "Fast & Slow Pointers",
        "what": "Two pointers advancing at different speeds to find a midpoint, a cycle, or the k-th-from-end node in one pass.",
        "deep": "Because the fast pointer covers twice the ground, it reaches the end when the slow pointer is halfway — the middle. In a cycle the fast pointer laps the slow one, so they must eventually meet (Floyd). Resetting one pointer to the head after a meeting locates the cycle's entry.",
        "java": "ListNode slow=head, fast=head; while(fast!=null && fast.next!=null){ slow=slow.next; fast=fast.next.next; }",
    },
})
CATEGORY.update({"list_basics": "Linked Lists", "list_reversal": "Linked Lists", "fast_slow": "Linked Lists"})
PATTERN_FROM.update({
    "In-place Reversal": "Linked List Reversal", "Fast & Slow": "Fast & Slow Pointers",
    "Dummy Head": "Linked List", "Traversal": "Traversal",
})

LESSONS.update({
    "list_basics": (
        "# Linked Lists\n\n"
        "A linked list is a chain of **nodes**, each holding a value and a reference to the **next** node. You reach any node only by walking from the head — there is no indexing.\n\n"
        "```java\n"
        "class ListNode { int val; ListNode next; ListNode(int v){ val = v; } }\n\n"
        "// Build behind a DUMMY head so appends need no special case:\n"
        "ListNode dummy = new ListNode(0), tail = dummy;\n"
        "for (int x : values) { tail.next = new ListNode(x); tail = tail.next; }\n"
        "ListNode head = dummy.next;\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'reverse the list'*, *'remove the nth node'*, *'merge sorted lists'*, *'detect a cycle'*, O(1) insert/delete.\n\n"
        "## The two survival rules\n"
        "1. **Cache `next` before you overwrite it** — otherwise the rest of the list is lost.\n"
        "2. **Use a dummy head** whenever the real head might be removed or reassigned, so you never special-case it."
    ),
    "list_reversal": (
        "# In-place Reversal\n\n"
        "Reverse a list by walking it once, flipping each `next` to point backwards.\n\n"
        "```java\n"
        "ListNode prev = null, cur = head;\n"
        "while (cur != null) {\n"
        "    ListNode next = cur.next;  // 1. cache\n"
        "    cur.next = prev;           // 2. flip\n"
        "    prev = cur;                // 3. advance prev\n"
        "    cur = next;                // 4. advance cur\n"
        "}\n"
        "return prev;                   // new head\n"
        "```\n\n"
        "## Simulated solve — reversing `1 2 3`\n"
        "| step | prev | cur | list so far |\n"
        "|---|---|---|---|\n"
        "| start | null | 1 | 1→2→3 |\n"
        "| after 1 | 1 | 2 | 1→null, 2→3 |\n"
        "| after 2 | 2 | 3 | 2→1→null |\n"
        "| after 3 | 3 | null | 3→2→1→null |\n\n"
        "## When to reach for this\n"
        "Reversal underlies **palindrome check**, **reorder list**, and **reverse-in-k-groups** — any time you must consume the list back-to-front in O(1) space."
    ),
    "fast_slow": (
        "# Fast & Slow Pointers\n\n"
        "Move one pointer twice as fast as the other. Two payoffs fall out for free:\n\n"
        "```java\n"
        "ListNode slow = head, fast = head;\n"
        "while (fast != null && fast.next != null) {\n"
        "    slow = slow.next;          // +1\n"
        "    fast = fast.next.next;     // +2\n"
        "}\n"
        "// slow is now the MIDDLE (second middle if even length)\n"
        "```\n\n"
        "## When to reach for this\n"
        "| Signal | Technique |\n"
        "|---|---|\n"
        "| 'middle of the list' | fast/slow, return slow |\n"
        "| 'does it have a cycle' | Floyd — do they meet? |\n"
        "| 'where does the cycle start' | meet, then reset one to head, step both by 1 |\n"
        "| 'nth node from the end' | gap of n, then move together |\n\n"
        "## Why cycle detection works\n"
        "Inside a loop the fast pointer gains one position on the slow pointer each step, so the gap shrinks to 0 — they **must** meet. If `fast` hits null, the list is straight."
    ),
})

_EXJ_LIST_HEAD = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static class ListNode { int val; ListNode next; ListNode(int v){ val = v; } }\n"
    "    static ListNode build(int[] a){ ListNode dummy=new ListNode(0), t=dummy; for(int x:a){ t.next=new ListNode(x); t=t.next; } return dummy.next; }\n"
    "    static int[] readInts(Scanner sc){ String line = sc.hasNextLine() ? sc.nextLine() : \"\"; line = line.trim(); if (line.isEmpty()) return new int[0]; String[] t = line.split(\"\\\\s+\"); int[] a = new int[t.length]; for (int i=0;i<t.length;i++) a[i]=Integer.parseInt(t[i]); return a; }\n"
)
_EX_LL_REVERSE = _EXJ_LIST_HEAD + (
    "    static ListNode reverse(ListNode head){\n"
    "        ListNode prev = null, cur = head;\n"
    "        while (cur != null) {\n"
    "            ListNode next = cur.next;\n"
    "            cur.next = prev;\n"
    "            prev = cur;\n"
    "            cur = next;\n"
    "        }\n"
    "        return prev;\n"
    "    }\n"
    "    public static void main(String[] args){\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        ListNode h = reverse(build(readInts(sc)));\n"
    "        StringBuilder sb = new StringBuilder();\n"
    "        while (h != null) { if (sb.length()>0) sb.append(' '); sb.append(h.val); h = h.next; }\n"
    "        System.out.println(sb.toString());\n"
    "    }\n}\n"
)
_EX_LL_MIDDLE = _EXJ_LIST_HEAD + (
    "    static int middle(ListNode head){\n"
    "        ListNode slow = head, fast = head;\n"
    "        while (fast != null && fast.next != null) {\n"
    "            slow = slow.next;\n"
    "            fast = fast.next.next;\n"
    "        }\n"
    "        return slow.val;\n"
    "    }\n"
    "    public static void main(String[] args){\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        System.out.println(middle(build(readInts(sc))));\n"
    "    }\n}\n"
)
_EX_LL_BUILD = _EXJ_LIST_HEAD + (
    "    static ListNode buildAppend(int[] a){\n"
    "        ListNode dummy = new ListNode(0), t = dummy;\n"
    "        for (int x : a) {\n"
    "            t.next = new ListNode(x);\n"
    "            t = t.next;\n"
    "        }\n"
    "        return dummy.next;\n"
    "    }\n"
    "    public static void main(String[] args){\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        ListNode h = buildAppend(readInts(sc));\n"
    "        StringBuilder sb = new StringBuilder();\n"
    "        while (h != null) { if (sb.length()>0) sb.append(' '); sb.append(h.val); h = h.next; }\n"
    "        System.out.println(sb.toString());\n"
    "    }\n}\n"
)
EXERCISES.update({
    "list_basics": [
        ex("list_basics-append", "Append behind the tail",
           "Building a list behind a dummy head. Fill the blank so a new node is linked after the current tail.",
           _EX_LL_BUILD, ["t.next = new ListNode(x);"],
           [("1 2 3", "1 2 3"), ("5", "5"), ("", "")],
           hint="Link the new node onto t.next.", source_slug="reverse-linked-list"),
        ex("list_basics-advance", "Advance the tail",
           "Fill the blank so the tail pointer moves onto the node you just appended.",
           _EX_LL_BUILD, ["t = t.next;"],
           [("4 5 6", "4 5 6"), ("9", "9"), ("1 1 1", "1 1 1")],
           hint="After appending, the tail is the new last node.", source_slug="reverse-linked-list"),
    ],
    "list_reversal": [
        ex("list_reversal-flip", "Flip the link",
           "The three-pointer reversal is set up. Fill the blank so the current node points back to prev.",
           _EX_LL_REVERSE, ["cur.next = prev;"],
           [("1 2 3 4", "4 3 2 1"), ("5", "5"), ("9 8", "8 9")],
           hint="Reverse the arrow: cur.next should become prev.", source_slug="reverse-linked-list"),
        ex("list_reversal-cache", "Cache before you flip",
           "Fill the blank so the rest of the list is saved before the link is overwritten.",
           _EX_LL_REVERSE, ["ListNode next = cur.next;"],
           [("1 2 3", "3 2 1"), ("1", "1"), ("2 4 6 8", "8 6 4 2")],
           hint="Save cur.next into a temp before cur.next = prev destroys it.", source_slug="reverse-linked-list"),
    ],
    "fast_slow": [
        ex("fast_slow-jump", "Fast pointer jumps two",
           "Fast/slow midpoint finder. Fill the blank so the fast pointer advances two nodes per step.",
           _EX_LL_MIDDLE, ["fast = fast.next.next;"],
           [("1 2 3 4 5", "3"), ("1 2 3 4 5 6", "4"), ("7", "7")],
           hint="Two hops: fast.next.next.", source_slug="middle-of-list"),
        ex("fast_slow-guard", "Guard the double hop",
           "Fill the blank with the loop condition that keeps the two-step jump safe.",
           _EX_LL_MIDDLE, ["fast != null && fast.next != null"],
           [("1 2 3", "2"), ("1 2 3 4", "3"), ("1", "1")],
           hint="Both fast and fast.next must exist before fast.next.next.", source_slug="middle-of-list"),
    ],
})

PREREQS.update({
    "list-length": [("list_basics", "Walk with node = node.next.")],
    "list-get-nth": [("list_basics", "Advance k-1 steps.")],
    "reverse-linked-list": [("list_reversal", "prev/cur/next flip."), ("list_basics", "Cache next first.")],
    "middle-of-list": [("fast_slow", "Slow lands at the middle.")],
    "remove-duplicates-sorted-list": [("list_basics", "Relink past duplicates.")],
    "merge-two-sorted-lists": [("list_basics", "Dummy head + tail."), ("two_pointers", "Compare the two fronts.")],
    "remove-nth-from-end": [("fast_slow", "Gap of n."), ("list_basics", "Dummy head for the head case.")],
    "palindrome-linked-list": [("fast_slow", "Find the middle."), ("list_reversal", "Reverse the second half.")],
    "odd-even-list": [("list_basics", "Weave two chains.")],
    "add-two-numbers-list": [("list_basics", "Dummy head."), ("math_digits", "Carry = sum / 10.")],
    "has-cycle": [("fast_slow", "Floyd meeting.")],
    "cycle-start-index": [("fast_slow", "Reset to head after meeting.")],
    "reorder-list": [("fast_slow", "Split at middle."), ("list_reversal", "Reverse the tail.")],
    "reverse-k-group": [("list_reversal", "Reverse fixed blocks."), ("list_basics", "Stitch blocks together.")],
})

FLASHCARDS += [
    ("Reverse a linked list in O(1) space?", "Rolling prev/cur/next: cache next, flip cur.next=prev, advance both; return prev.", "seed:list_reversal"),
    ("Find the middle of a linked list in one pass?", "Fast/slow: slow+=1, fast+=2; when fast ends, slow is the middle.", "seed:fast_slow"),
    ("Detect a cycle in a linked list?", "Floyd's tortoise & hare — if fast (2x) ever meets slow (1x), there's a cycle.", "seed:fast_slow"),
    ("Find where a cycle starts?", "After the fast/slow meeting, reset one pointer to head; step both by 1; they meet at the entry.", "seed:fast_slow"),
    ("Why use a dummy head node?", "It removes the special case when the real head is removed or reassigned.", "seed:list_basics"),
]

_REF_REVLIST_J = _LIST_PRELUDE_JAVA + "class Solution {\n    int[] solve(int[] vals) {\n        ListNode prev=null, cur=ListUtil.build(vals);\n        while(cur!=null){ ListNode nx=cur.next; cur.next=prev; prev=cur; cur=nx; }\n        return ListUtil.ser(prev);\n    }\n}\n"
_REF_REVLIST_P = _LIST_PRELUDE_PY + "def solve(vals):\n    prev=None; cur=build_list(vals)\n    while cur:\n        nx=cur.next; cur.next=prev; prev=cur; cur=nx\n    return ser_list(prev)\n"
EXPANSION_REFS.update({
    "reverse-linked-list": {"java": _REF_REVLIST_J, "python": _REF_REVLIST_P},
    "middle-of-list": {
        "java": _LIST_PRELUDE_JAVA + "class Solution {\n    int solve(int[] vals){ ListNode slow=ListUtil.build(vals), fast=slow; while(fast!=null&&fast.next!=null){ slow=slow.next; fast=fast.next.next; } return slow.val; }\n}\n",
        "python": _LIST_PRELUDE_PY + "def solve(vals):\n    slow=build_list(vals); fast=slow\n    while fast and fast.next:\n        slow=slow.next; fast=fast.next.next\n    return slow.val\n",
    },
    "merge-two-sorted-lists": {
        "java": _LIST_PRELUDE_JAVA + "class Solution {\n    int[] solve(int[] a, int[] b){ ListNode ha=ListUtil.build(a), hb=ListUtil.build(b), dummy=new ListNode(0), t=dummy; while(ha!=null&&hb!=null){ if(ha.val<=hb.val){ t.next=ha; ha=ha.next; } else { t.next=hb; hb=hb.next; } t=t.next; } t.next = (ha!=null)?ha:hb; return ListUtil.ser(dummy.next); }\n}\n",
        "python": _LIST_PRELUDE_PY + "def solve(a, b):\n    ha=build_list(a); hb=build_list(b); dummy=ListNode(0); t=dummy\n    while ha and hb:\n        if ha.val<=hb.val: t.next=ha; ha=ha.next\n        else: t.next=hb; hb=hb.next\n        t=t.next\n    t.next = ha if ha else hb\n    return ser_list(dummy.next)\n",
    },
    "has-cycle": {
        "java": _LIST_PRELUDE_JAVA + "class Solution {\n    boolean solve(int[] vals, int pos){ ListNode slow=ListUtil.buildCycle(vals,pos), fast=slow; while(fast!=null&&fast.next!=null){ slow=slow.next; fast=fast.next.next; if(slow==fast) return true; } return false; }\n}\n",
        "python": _LIST_PRELUDE_PY + "def solve(vals, pos):\n    slow=build_cycle(vals,pos); fast=slow\n    while fast and fast.next:\n        slow=slow.next; fast=fast.next.next\n        if slow is fast: return True\n    return False\n",
    },
    "cycle-start-index": {
        "java": _LIST_PRELUDE_JAVA + "class Solution {\n    int solve(int[] vals, int pos){ ListNode head=ListUtil.buildCycle(vals,pos), slow=head, fast=head; boolean cyc=false; while(fast!=null&&fast.next!=null){ slow=slow.next; fast=fast.next.next; if(slow==fast){ cyc=true; break; } } if(!cyc) return -1; slow=head; while(slow!=fast){ slow=slow.next; fast=fast.next; } return ListUtil.indexOf(head, slow); }\n}\n",
        "python": _LIST_PRELUDE_PY + "def solve(vals, pos):\n    head=build_cycle(vals,pos); slow=head; fast=head; cyc=False\n    while fast and fast.next:\n        slow=slow.next; fast=fast.next.next\n        if slow is fast: cyc=True; break\n    if not cyc: return -1\n    slow=head\n    while slow is not fast:\n        slow=slow.next; fast=fast.next\n    i=0; n=head\n    while n is not slow: n=n.next; i+=1\n    return i\n",
    },
    "palindrome-linked-list": {
        "java": _LIST_PRELUDE_JAVA + "class Solution {\n    int[] rev(int[] v){ return v; }\n    boolean solve(int[] vals){ ListNode h=ListUtil.build(vals); int[] a=ListUtil.ser(h); int i=0,j=a.length-1; while(i<j){ if(a[i]!=a[j]) return false; i++; j--; } return true; }\n}\n",
        "python": _LIST_PRELUDE_PY + "def solve(vals):\n    a=ser_list(build_list(vals)); return a==a[::-1]\n",
    },
    "add-two-numbers-list": {
        "java": _LIST_PRELUDE_JAVA + "class Solution {\n    int[] solve(int[] a, int[] b){ ListNode x=ListUtil.build(a), y=ListUtil.build(b), dummy=new ListNode(0), t=dummy; int carry=0; while(x!=null||y!=null||carry>0){ int s=carry; if(x!=null){ s+=x.val; x=x.next; } if(y!=null){ s+=y.val; y=y.next; } t.next=new ListNode(s%10); t=t.next; carry=s/10; } return ListUtil.ser(dummy.next); }\n}\n",
        "python": _LIST_PRELUDE_PY + "def solve(a, b):\n    x=build_list(a); y=build_list(b); dummy=ListNode(0); t=dummy; carry=0\n    while x or y or carry:\n        s=carry\n        if x: s+=x.val; x=x.next\n        if y: s+=y.val; y=y.next\n        t.next=ListNode(s%10); t=t.next; carry=s//10\n    return ser_list(dummy.next)\n",
    },
})

# ===========================================================================
# DOMAIN 3 — BACKTRACKING   (exact counting/decision + checker generate-all)
# ===========================================================================
import itertools as _it
import math as _math


def _bt_count_paths(m, n):
    return _math.comb(m + n - 2, m - 1)


def _bt_subset_sum_count(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for x in nums:
        for a in range(target, x - 1, -1):
            dp[a] += dp[a - x]
    return dp[target]


def _bt_combo_sum_count(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in nums:
        for a in range(c, target + 1):
            dp[a] += dp[a - c]
    return dp[target]


def _bt_palindrome_partitions(s):
    from functools import lru_cache

    @lru_cache(None)
    def f(i):
        if i == len(s):
            return 1
        total = 0
        for j in range(i + 1, len(s) + 1):
            seg = s[i:j]
            if seg == seg[::-1]:
                total += f(j)
        return total
    return f(0)


def _bt_word_search(grid, word):
    R = len(grid)
    C = len(grid[0]) if R else 0
    grid = [list(row) for row in grid]

    def dfs(r, c, i, seen):
        if i == len(word):
            return True
        if r < 0 or r >= R or c < 0 or c >= C or (r, c) in seen or grid[r][c] != word[i]:
            return False
        seen.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if dfs(r + dr, c + dc, i + 1, seen):
                seen.discard((r, c))
                return True
        seen.discard((r, c))
        return False
    for r in range(R):
        for c in range(C):
            if dfs(r, c, 0, set()):
                return True
    return False


def _bt_nqueens(n):
    full = (1 << n) - 1

    def go(cols, d1, d2):
        if cols == full:
            return 1
        avail = full & ~(cols | d1 | d2)
        t = 0
        while avail:
            p = avail & (-avail)
            avail -= p
            t += go(cols | p, (d1 | p) << 1, (d2 | p) >> 1)
        return t
    return go(0, 0, 0)


def _bt_sudoku_solvable(board):
    g = [list(row) for row in board]

    def ok(r, c, ch):
        for i in range(9):
            if g[r][i] == ch or g[i][c] == ch:
                return False
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if g[i][j] == ch:
                    return False
        return True

    def solve():
        for r in range(9):
            for c in range(9):
                if g[r][c] == '.':
                    for d in "123456789":
                        if ok(r, c, d):
                            g[r][c] = d
                            if solve():
                                return True
                            g[r][c] = '.'
                    return False
        return True
    # reject boards whose givens already conflict
    for r in range(9):
        for c in range(9):
            if g[r][c] != '.':
                ch = g[r][c]
                g[r][c] = '.'
                if not ok(r, c, ch):
                    g[r][c] = ch
                    return False
                g[r][c] = ch
    return solve()


def _enc_subsets(nums):
    res = []
    for r in range(len(nums) + 1):
        for c in _it.combinations(nums, r):
            res.append("-" if not c else ",".join(map(str, c)))
    return res


def _enc_perms(nums):
    return [",".join(map(str, p)) for p in _it.permutations(nums)]


def _enc_combos(n, k):
    return [",".join(map(str, c)) for c in _it.combinations(range(1, n + 1), k)]


def _gen_parens(n):
    res = []

    def go(s, o, c):
        if len(s) == 2 * n:
            res.append(s)
            return
        if o < n:
            go(s + "(", o + 1, c)
        if c < o:
            go(s + ")", o, c + 1)
    go("", 0, 0)
    return res


_PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def _gen_letter(digits):
    if not digits:
        return []
    groups = [_PHONE[d] for d in digits]
    return ["".join(p) for p in _it.product(*groups)]


def _gen_ip(s):
    exp = []
    n = len(s)

    def ok(seg):
        if not seg or len(seg) > 3:
            return False
        if len(seg) > 1 and seg[0] == '0':
            return False
        return 0 <= int(seg) <= 255
    for a in range(1, 4):
        for b in range(1, 4):
            for c in range(1, 4):
                d = n - a - b - c
                if d < 1 or d > 3:
                    continue
                p = [s[:a], s[a:a + b], s[a + b:a + b + c], s[a + b + c:]]
                if all(ok(x) for x in p):
                    exp.append(".".join(p))
    return exp


_CHK_SUBSETS = (
    "def check(inp, out):\n"
    "    import itertools\n"
    "    lines = inp.split('\\n')\n"
    "    nums = list(map(int, lines[0].split())) if lines and lines[0].strip() else []\n"
    "    toks = out.split()\n"
    "    got = set()\n"
    "    for t in toks:\n"
    "        got.add(() if t == '-' else tuple(sorted(map(int, t.split(',')))))\n"
    "    exp = set()\n"
    "    for r in range(len(nums)+1):\n"
    "        for c in itertools.combinations(sorted(nums), r):\n"
    "            exp.add(tuple(c))\n"
    "    return got == exp and len(toks) == len(exp)\n"
)
_CHK_PERMS = (
    "def check(inp, out):\n"
    "    import itertools\n"
    "    lines = inp.split('\\n')\n"
    "    nums = list(map(int, lines[0].split())) if lines and lines[0].strip() else []\n"
    "    toks = out.split()\n"
    "    got = [tuple(map(int, t.split(','))) for t in toks]\n"
    "    exp = set(itertools.permutations(nums))\n"
    "    return set(got) == exp and len(got) == len(exp)\n"
)
_CHK_COMBOS = (
    "def check(inp, out):\n"
    "    import itertools\n"
    "    lines = inp.split('\\n')\n"
    "    n = int(lines[0]); k = int(lines[1])\n"
    "    toks = out.split()\n"
    "    got = set(tuple(sorted(map(int, t.split(',')))) for t in toks)\n"
    "    exp = set(itertools.combinations(range(1, n+1), k))\n"
    "    return got == exp and len(toks) == len(exp)\n"
)
_CHK_PARENS = (
    "def check(inp, out):\n"
    "    n = int(inp.split('\\n')[0])\n"
    "    toks = out.split()\n"
    "    res = set()\n"
    "    def go(s, o, c):\n"
    "        if len(s) == 2*n:\n"
    "            res.add(s); return\n"
    "        if o < n: go(s+'(', o+1, c)\n"
    "        if c < o: go(s+')', o, c+1)\n"
    "    go('', 0, 0)\n"
    "    return set(toks) == res and len(toks) == len(res)\n"
)
_CHK_LETTER = (
    "def check(inp, out):\n"
    "    import itertools\n"
    "    digits = inp.split('\\n')[0].strip()\n"
    "    m = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}\n"
    "    toks = out.split()\n"
    "    if digits == '':\n"
    "        return len(toks) == 0\n"
    "    groups = [m[d] for d in digits]\n"
    "    exp = set(''.join(p) for p in itertools.product(*groups))\n"
    "    return set(toks) == exp and len(toks) == len(exp)\n"
)
_CHK_IP = (
    "def check(inp, out):\n"
    "    s = inp.split('\\n')[0].strip()\n"
    "    toks = out.split()\n"
    "    exp = set(); n = len(s)\n"
    "    def ok(seg):\n"
    "        if not seg or len(seg) > 3: return False\n"
    "        if len(seg) > 1 and seg[0] == '0': return False\n"
    "        return 0 <= int(seg) <= 255\n"
    "    for a in range(1,4):\n"
    "        for b in range(1,4):\n"
    "            for c in range(1,4):\n"
    "                d = n - a - b - c\n"
    "                if d < 1 or d > 3: continue\n"
    "                p = [s[:a], s[a:a+b], s[a+b:a+b+c], s[a+b+c:]]\n"
    "                if all(ok(x) for x in p): exp.add('.'.join(p))\n"
    "    return set(toks) == exp and len(toks) == len(exp)\n"
)

_SUDOKU_OK = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]
_SUDOKU_BAD = ["55..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]

HARNESS_DEFS += [
    dict(slug="unique-paths-count", title="Unique Paths", difficulty="Easy",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon", "Bloomberg"],
         description="A robot starts at the top-left of an `m x n` grid and may only move **right** or **down**. Return the number of distinct paths to the bottom-right corner.",
         constraints="1 ≤ m, n ≤ 20.",
         hints=["Each path is a sequence of moves; the count has optimal substructure.",
                "paths(m,n) = paths(m-1,n) + paths(m,n-1).", "Base: a single row or column has exactly one path.",
                "It's also the binomial C(m+n-2, m-1)."],
         opt=("O(m*n)", "O(n)", "DP over the grid; each cell sums the cell above and to the left."),
         editorial="## Approach\nCount paths with paths(i,j) = paths(i-1,j) + paths(i,j-1); the grid edges are all 1.",
         spec={"name": "solve", "params": [{"name": "m", "type": "int"}, {"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda m, n: _bt_count_paths(m, n),
         cases=[("example", "3x7", (3, 7)), ("example", "3x2", (3, 2)),
                ("hidden", "1x1", (1, 1)), ("hidden", "Square", (4, 4)), ("hidden", "Line", (1, 10))],
         example_expl=["28 distinct paths on a 3x7 grid.", "3 paths on a 3x2 grid."]),
    dict(slug="subset-sum-count", title="Count Subsets with Target Sum", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon"],
         description="Given non-negative integers `nums` and a `target`, count how many **subsets** (each element used at most once) sum exactly to `target`.",
         constraints="1 ≤ n ≤ 20\n0 ≤ nums[i], target ≤ 1000.",
         hints=["Each element is either taken or skipped — a binary decision tree.",
                "count = count(skip a[i]) + count(take a[i]).", "The base case is reaching the end with remaining == 0.",
                "Memoize on (index, remaining) to avoid the exponential blow-up."],
         opt=("O(n*target)", "O(target)", "0/1 knapsack counting DP."),
         editorial="## Approach\nBacktrack take/skip each element, or run the 0/1 subset-sum counting DP dp[a] += dp[a - x].",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int"},
         fn=lambda nums, target: _bt_subset_sum_count(nums, target),
         cases=[("example", "Basic", ([1, 2, 3, 4], 5)), ("example", "Zeroes", ([2, 3, 5], 5)),
                ("hidden", "Empty target", ([1, 2, 3], 0)), ("hidden", "None", ([1, 2], 8)), ("hidden", "Dup values", ([1, 1, 1, 1], 2))],
         example_expl=["{1,4} and {2,3} → 2 subsets.", "{2,3} and {5} → 2 subsets."]),
    dict(slug="combination-sum-count", title="Count Combination Sums", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking", "Pruning"], companies=["Amazon", "Bloomberg"],
         description="Given distinct positive `nums` and a `target`, count the number of **combinations** (order-independent, each number reusable unlimited times) that sum to `target`.",
         constraints="1 ≤ n ≤ 20\n1 ≤ nums[i] ≤ 100\n1 ≤ target ≤ 500.",
         hints=["A combination is a multiset — order doesn't matter, so fix an order via a start index.",
                "Recurse allowing the same index again (reuse).", "Sort and prune once a candidate exceeds the remaining target.",
                "Equivalent to the order-independent coin-change ways DP."],
         opt=("O(n*target)", "O(target)", "Unbounded knapsack counting: dp[a] += dp[a - coin], coins outer."),
         editorial="## Approach\nUse a start index to keep combinations order-free; recurse with reuse. DP: iterate coins outer, dp[a] += dp[a-coin].",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "returns": "int"},
         fn=lambda nums, target: _bt_combo_sum_count(nums, target),
         cases=[("example", "Coins", ([2, 3, 6, 7], 7)), ("example", "Reuse", ([2, 3, 5], 8)),
                ("hidden", "Single", ([1], 4)), ("hidden", "None", ([5, 7], 3)), ("hidden", "Exact", ([2, 4], 6))],
         example_expl=["[2,2,3] and [7] → 2.", "[3,5] and [2,3,3] and [2,2,2,2] → 3."]),
    dict(slug="palindrome-partition-count", title="Count Palindromic Partitions", difficulty="Medium",
         topics=["Recursion & DP", "Strings"], subtopics=["Backtracking"], companies=["Amazon"],
         description="Count the number of ways to split string `s` so that **every** part is a palindrome.",
         constraints="1 ≤ |s| ≤ 16\nLowercase letters.",
         hints=["At each position, try every prefix that is a palindrome, then recurse on the rest.",
                "ways(i) = sum over palindromic s[i:j] of ways(j).", "Base: reaching the end is one complete partition.",
                "Memoize on the start index."],
         opt=("O(n^2)", "O(n)", "Backtrack over palindromic prefixes with memoization on the start index."),
         editorial="## Approach\nRecurse from index i: for each j where s[i:j] is a palindrome add ways(j); ways(n)=1.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "int"},
         fn=lambda s: _bt_palindrome_partitions(s),
         cases=[("example", "aab", ("aab",)), ("example", "aaa", ("aaa",)),
                ("hidden", "Single", ("a",)), ("hidden", "No split needed", ("abc",)), ("hidden", "Racecar", ("racecar",))],
         example_expl=["'a|a|b' and 'aa|b' → 2 partitions.", "'a|a|a', 'aa|a'... 4 partitions of 'aaa'."]),
    dict(slug="word-search", title="Word Search", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon", "Microsoft", "Facebook"],
         description=("Given a grid of letters (each row is one token) and a `word`, return `true` if the word can be formed "
                      "by a path of **orthogonally adjacent** cells, using each cell at most once."),
         constraints="1 ≤ rows, cols ≤ 6\nRows are equal-length uppercase strings.",
         hints=["From every cell that matches word[0], start a DFS.",
                "Mark the cell visited before recursing, unmark after (backtrack).",
                "Move up/down/left/right, matching the next letter.", "Success when the whole word is matched."],
         opt=("O(R*C*4^L)", "O(L)", "DFS from each cell with visited-marking backtracking (L = word length)."),
         editorial="## Approach\nDFS with backtracking: mark a cell used, try the four neighbours for the next letter, then unmark.",
         spec={"name": "solve", "params": [{"name": "grid", "type": "string[]"}, {"name": "word", "type": "string"}], "returns": "bool"},
         fn=lambda grid, word: _bt_word_search(grid, word),
         cases=[("example", "Found", (["ABCE", "SFCS", "ADEE"], "ABCCED")), ("example", "Missing", (["ABCE", "SFCS", "ADEE"], "ABCB")),
                ("hidden", "Single cell", (["A"], "A")), ("hidden", "Reuse blocked", (["AB", "CD"], "ABDC")), ("hidden", "Down", (["AB", "CD"], "AC"))],
         example_expl=["A-B-C-C-E-D snakes through the grid.", "ABCB would reuse a cell — not allowed."]),
    dict(slug="n-queens-count", title="N-Queens (count solutions)", difficulty="Hard",
         topics=["Recursion & DP"], subtopics=["Backtracking", "Pruning"], companies=["Amazon", "Google"],
         description="Return the number of ways to place `n` non-attacking queens on an `n x n` board.",
         constraints="1 ≤ n ≤ 12.",
         hints=["Place one queen per row.", "Track occupied columns and both diagonals.",
                "Backtrack: try each safe column, recurse to the next row.", "Bitmasks make the safety check O(1)."],
         opt=("O(n!)", "O(n)", "Row-by-row backtracking with column/diagonal bitmasks pruning conflicts."),
         editorial="## Approach\nRecurse row by row; keep bitmasks of used columns and diagonals; count when all rows are filled.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _bt_nqueens(n),
         cases=[("example", "n=4", (4,)), ("example", "n=1", (1,)),
                ("hidden", "n=2", (2,)), ("hidden", "n=6", (6,)), ("hidden", "n=8", (8,))],
         example_expl=["4-queens has 2 solutions.", "1-queen has 1."]),
    dict(slug="sudoku-solvable", title="Sudoku Solvable?", difficulty="Hard",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Uber"],
         description=("A 9x9 Sudoku board is given as 9 row tokens; `.` marks a blank. Return `true` if the board can be "
                      "completed to a valid solution (each row, column, and 3x3 box holding 1–9 once)."),
         constraints="Exactly 9 rows of 9 characters from '1'-'9' and '.'.",
         hints=["Find an empty cell, try digits 1–9 that don't conflict.",
                "Recurse; if you get stuck, undo and try the next digit.",
                "Check row, column, and the 3x3 box for conflicts.", "Reject boards whose givens already clash."],
         opt=("O(9^blanks)", "O(1)", "Constraint-propagation backtracking over blank cells."),
         editorial="## Approach\nBacktracking: fill the first blank with each legal digit, recurse, undo on failure. First check the given cells don't already conflict.",
         spec={"name": "solve", "params": [{"name": "board", "type": "string[]"}], "returns": "bool"},
         fn=lambda board: _bt_sudoku_solvable(board),
         cases=[("example", "Solvable", (_SUDOKU_OK,)), ("example", "Conflict", (_SUDOKU_BAD,)),
                ("hidden", "Solvable again", (_SUDOKU_OK,)), ("hidden", "Bad again", (_SUDOKU_BAD,))],
         example_expl=["A standard puzzle completes.", "Two 5s in the first row — impossible."]),
    # ---- generate-all (checker judged) ----
    dict(slug="generate-subsets", title="Generate All Subsets (Power Set)", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon", "Facebook"],
         description=("Return **every** subset of the distinct integers `nums`. Encode each subset as its comma-joined "
                      "values (any element order); use `-` for the empty subset. Any complete, duplicate-free listing is accepted."),
         constraints="1 ≤ n ≤ 12, distinct values.",
         hints=["There are 2^n subsets — one binary choice per element.",
                "Backtrack: include or exclude each element (choose / un-choose).",
                "Or map each bitmask 0..2^n-1 to a subset.", "Emit `-` for the empty set so it isn't lost."],
         opt=("O(n*2^n)", "O(n)", "Every element is in or out — enumerate all 2^n choices."),
         editorial="## Approach\nStandard subsets backtracking (choose/un-choose) or bitmask enumeration; output each as comma-joined, `-` for empty.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "string[]"},
         fn=lambda nums: _enc_subsets(nums), judge_mode="checker", checker=_CHK_SUBSETS,
         cases=[("example", "Three", ([1, 2, 3],)), ("example", "One", ([7],)),
                ("hidden", "Two", ([1, 2],)), ("hidden", "Four", ([1, 2, 3, 4],)), ("hidden", "Distinct", ([5, 9, 2],))],
         example_expl=["8 subsets of {1,2,3}, including the empty set as `-`.", "Subsets are `-` and `7`."]),
    dict(slug="generate-permutations", title="Generate All Permutations", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon", "Microsoft"],
         description=("Return **every** permutation of the distinct integers `nums`. Encode each permutation as its "
                      "comma-joined values in order. Any complete, duplicate-free listing is accepted."),
         constraints="1 ≤ n ≤ 7, distinct values.",
         hints=["Build a permutation position by position.", "Track which values are already used.",
                "Choose an unused value, recurse, then un-choose (backtrack).", "There are n! permutations."],
         opt=("O(n*n!)", "O(n)", "Backtracking with a used[] set; n! leaves."),
         editorial="## Approach\nBacktrack: at each step pick an unused value, append it, recurse, then remove it (the choose / un-choose pair).",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "string[]"},
         fn=lambda nums: _enc_perms(nums), judge_mode="checker", checker=_CHK_PERMS,
         cases=[("example", "Three", ([1, 2, 3],)), ("example", "One", ([5],)),
                ("hidden", "Two", ([1, 2],)), ("hidden", "Distinct", ([4, 7, 9],)), ("hidden", "Four", ([1, 2, 3, 4],))],
         example_expl=["6 permutations of 1,2,3.", "A single value has one permutation."]),
    dict(slug="combinations-nk", title="Combinations of n choose k", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Google"],
         description=("Return **all** combinations of `k` numbers chosen from `1..n`. Encode each as its comma-joined "
                      "values in increasing order. Any complete, duplicate-free listing is accepted."),
         constraints="1 ≤ k ≤ n ≤ 12.",
         hints=["Build combinations with a start index so they stay increasing.",
                "Pick the next value ≥ the previous one.", "Stop a branch once it can't reach size k.",
                "There are C(n,k) combinations."],
         opt=("O(k*C(n,k))", "O(k)", "Backtracking with a start index enforcing increasing order."),
         editorial="## Approach\nRecurse from a start value; append the next chosen number and recurse with start+1 until size k.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "k", "type": "int"}], "returns": "string[]"},
         fn=lambda n, k: _enc_combos(n, k), judge_mode="checker", checker=_CHK_COMBOS,
         cases=[("example", "4 choose 2", (4, 2)), ("example", "3 choose 1", (3, 1)),
                ("hidden", "n=k", (3, 3)), ("hidden", "5 choose 3", (5, 3)), ("hidden", "k=2", (5, 2))],
         example_expl=["6 pairs from {1,2,3,4}.", "Singletons 1,2,3."]),
    dict(slug="generate-parentheses", title="Generate Parentheses", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon", "Google", "Facebook"],
         description="Return **all** well-formed strings of `n` pairs of parentheses. Any complete, duplicate-free listing is accepted.",
         constraints="1 ≤ n ≤ 8.",
         hints=["Build the string one bracket at a time.", "You may add '(' while opens < n.",
                "You may add ')' only while closes < opens.", "Stop at length 2n — that's a valid string."],
         opt=("O(4^n / sqrt(n))", "O(n)", "Backtracking constrained by open/close counts (Catalan many)."),
         editorial="## Approach\nBacktrack with counts of opens and closes: add '(' if opens<n, add ')' if closes<opens; record at length 2n.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "string[]"},
         fn=lambda n: _gen_parens(n), judge_mode="checker", checker=_CHK_PARENS,
         cases=[("example", "n=3", (3,)), ("example", "n=1", (1,)),
                ("hidden", "n=2", (2,)), ("hidden", "n=4", (4,)), ("hidden", "n=5", (5,))],
         example_expl=["5 combinations for 3 pairs.", "Just `()`."]),
    dict(slug="letter-combinations-phone", title="Letter Combinations of a Phone Number", difficulty="Medium",
         topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Amazon", "Google"],
         description=("Given a string of digits 2–9, return **all** letter strings it could spell on a phone keypad "
                      "(2=abc, 3=def, …, 9=wxyz). Any complete, duplicate-free listing is accepted."),
         constraints="0 ≤ |digits| ≤ 4, digits from '2'..'9'.",
         hints=["Each digit maps to 3–4 letters.", "Combine choices across digits (Cartesian product).",
                "Backtrack one digit at a time, appending a letter.", "Empty input → no combinations."],
         opt=("O(4^d * d)", "O(d)", "Backtracking over the keypad letters of each digit."),
         editorial="## Approach\nRecurse digit by digit; for each letter of the current digit, append and recurse to the next digit.",
         spec={"name": "solve", "params": [{"name": "digits", "type": "string"}], "returns": "string[]"},
         fn=lambda digits: _gen_letter(digits), judge_mode="checker", checker=_CHK_LETTER,
         cases=[("example", "23", ("23",)), ("example", "2", ("2",)),
                ("hidden", "9", ("9",)), ("hidden", "234", ("234",)), ("hidden", "77", ("77",))],
         example_expl=["ad, ae, af, bd, ... cf — 9 strings.", "a, b, c."]),
    dict(slug="restore-ip-addresses", title="Restore IP Addresses", difficulty="Medium",
         topics=["Recursion & DP", "Strings"], subtopics=["Backtracking"], companies=["Amazon", "Facebook"],
         description=("Given a digit string `s`, return **all** valid IPv4 addresses obtainable by inserting three dots. "
                      "Each of the four parts is 0–255 with no leading zeros. Any complete, duplicate-free listing is accepted."),
         constraints="4 ≤ |s| ≤ 12, digits only.",
         hints=["Split into exactly four parts.", "Each part is 1–3 digits, value ≤ 255.",
                "Reject parts with a leading zero (unless the part is '0').", "Backtrack over the three cut positions."],
         opt=("O(1)", "O(1)", "At most 3*3*3 placements of the three dots to validate."),
         editorial="## Approach\nTry each length 1–3 for the four segments; validate range and leading zeros; collect the valid dotted forms.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "string[]"},
         fn=lambda s: _gen_ip(s), judge_mode="checker", checker=_CHK_IP,
         cases=[("example", "25525511135", ("25525511135",)), ("example", "0000", ("0000",)),
                ("hidden", "101023", ("101023",)), ("hidden", "1111", ("1111",)), ("hidden", "12121212", ("12121212",))],
         example_expl=["255.255.11.135 and 255.255.111.35.", "Only 0.0.0.0."]),
]

CONCEPTS.update({
    "backtracking": {
        "name": "Backtracking",
        "what": "Systematically building candidates one choice at a time, undoing a choice when it can't lead to a solution.",
        "deep": "Backtracking is DFS over a decision tree. The template is choose → explore → un-choose: append a choice, recurse, then remove it so the next choice starts clean. It enumerates subsets, permutations, combinations, and constraint solutions (N-queens, Sudoku). Cost is roughly the number of leaves, so it needs small n.",
        "java": "A recursive helper carrying the partial solution (often a List you add()/remove() from) and the current position/used-set; add to results at a complete state.",
    },
    "pruning": {
        "name": "Pruning",
        "what": "Cutting off branches of the search that cannot possibly succeed, so backtracking stays fast.",
        "deep": "The difference between a passing and a timing-out backtracker is usually pruning: sort inputs so you can 'break' once a candidate exceeds the target, skip duplicate choices to avoid repeated work, and check feasibility bounds before recursing. Good pruning shrinks an exponential tree dramatically.",
        "java": "Sort first; inside the loop `if (candidate > remaining) break;` and `if (i > start && a[i] == a[i-1]) continue;` to skip duplicates.",
    },
})
CATEGORY.update({"backtracking": "Recursion & DP", "pruning": "Recursion & DP"})
PATTERN_FROM.update({"Backtracking": "Backtracking", "Pruning": "Backtracking", "Decision Tree": "Backtracking"})

LESSONS.update({
    "backtracking": (
        "# Backtracking\n\n"
        "Backtracking is depth-first search over a tree of **choices**. The template never changes:\n\n"
        "```java\n"
        "void backtrack(List<Integer> path, /* state */) {\n"
        "    if (isComplete(path)) { results.add(new ArrayList<>(path)); return; }\n"
        "    for (int choice : options(state)) {\n"
        "        path.add(choice);        // 1. choose\n"
        "        backtrack(path, next);   // 2. explore\n"
        "        path.remove(path.size()-1); // 3. UN-choose\n"
        "    }\n"
        "}\n"
        "```\n\n"
        "The `remove` is the whole trick — it restores state so the next choice explores a clean branch.\n\n"
        "## When to reach for this\n"
        "Signals: *'generate all…'*, *'how many ways'*, *'all combinations/permutations/subsets'*, constraint puzzles (N-queens, Sudoku, word search). n is always small — exponential is expected.\n\n"
        "## Simulated solve — subsets of `[1,2]`\n"
        "| path | action |\n"
        "|---|---|\n"
        "| [] | record [] |\n"
        "| [1] | choose 1, record [1] |\n"
        "| [1,2] | choose 2, record [1,2] |\n"
        "| [1] | un-choose 2 |\n"
        "| [] | un-choose 1 |\n"
        "| [2] | choose 2, record [2] |\n"
    ),
    "pruning": (
        "# Pruning\n\n"
        "A correct backtracker can still time out. **Pruning** cuts branches that can't yield a solution.\n\n"
        "```java\n"
        "Arrays.sort(a);\n"
        "void go(int start, int remaining) {\n"
        "    if (remaining == 0) { count++; return; }\n"
        "    for (int i = start; i < a.length; i++) {\n"
        "        if (a[i] > remaining) break;      // sorted → nothing later fits\n"
        "        if (i > start && a[i] == a[i-1]) continue; // skip duplicate choice\n"
        "        go(i, remaining - a[i]);\n"
        "    }\n"
        "}\n"
        "```\n\n"
        "## Three standard cuts\n"
        "| Cut | Why it's safe |\n"
        "|---|---|\n"
        "| sort + `break` when candidate > remaining | everything after is even bigger |\n"
        "| skip `a[i]==a[i-1]` at the same depth | avoids generating a duplicate result |\n"
        "| bound check before recursing | prune impossible sub-trees early |\n"
    ),
})

_EX_BT_SUBSET = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static int count = 0;\n"
    "    static void go(int[] a, int i, int rem) {\n"
    "        if (i == a.length) { if (rem == 0) count++; return; }\n"
    "        go(a, i + 1, rem);\n"
    "        go(a, i + 1, rem - a[i]);\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt(); int[] a = new int[n];\n"
    "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
    "        int target = sc.nextInt();\n"
    "        go(a, 0, target);\n"
    "        System.out.println(count);\n"
    "    }\n}\n"
)
_EX_BT_PRUNE = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static int count = 0;\n"
    "    static void go(int[] a, int start, int rem) {\n"
    "        if (rem == 0) { count++; return; }\n"
    "        for (int i = start; i < a.length; i++) {\n"
    "            if (a[i] > rem) break;\n"
    "            go(a, i, rem - a[i]);\n"
    "        }\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt(); int[] a = new int[n];\n"
    "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
    "        int target = sc.nextInt();\n"
    "        Arrays.sort(a);\n"
    "        go(a, 0, target);\n"
    "        System.out.println(count);\n"
    "    }\n}\n"
)
EXERCISES.update({
    "backtracking": [
        ex("backtracking-take", "The 'take' branch",
           "Counting subsets that sum to target. Fill the blank so the second recursive call **takes** a[i] (reducing the remaining target).",
           _EX_BT_SUBSET, ["go(a, i + 1, rem - a[i]);"],
           [("4\n1 2 3 4\n5", "2"), ("3\n2 3 5\n5", "2"), ("3\n1 2 3\n0", "1")],
           hint="Taking a[i] subtracts it from the remaining target.", source_slug="subset-sum-count"),
        ex("backtracking-base", "The base case",
           "Fill the blank so a completed choice counts only when the remaining target hit exactly zero.",
           _EX_BT_SUBSET, ["if (rem == 0) count++;"],
           [("4\n1 2 3 4\n5", "2"), ("2\n1 2\n8", "0"), ("3\n1 2 3\n6", "1")],
           hint="At the end of the array, success means nothing left to reach.", source_slug="subset-sum-count"),
    ],
    "pruning": [
        ex("pruning-break", "Prune the sorted branch",
           "Combination-sum counting on a sorted array. Fill the blank so the loop stops once a candidate is bigger than the remaining target.",
           _EX_BT_PRUNE, ["if (a[i] > rem) break;"],
           [("4\n2 3 6 7\n7", "2"), ("3\n2 3 5\n8", "3"), ("2\n2 4\n6", "2")],
           hint="Sorted array — once a[i] exceeds rem, every later value does too.", source_slug="combination-sum-count"),
    ],
})

PREREQS.update({
    "unique-paths-count": [("recursion", "paths = up + left."), ("dp", "Memoize the grid.")],
    "subset-sum-count": [("backtracking", "Take/skip each element."), ("dp", "0/1 knapsack counting.")],
    "combination-sum-count": [("backtracking", "Start index keeps combinations ordered."), ("pruning", "Break past the target.")],
    "palindrome-partition-count": [("backtracking", "Recurse on palindromic prefixes."), ("recursion", "Memoize the start index.")],
    "word-search": [("backtracking", "Mark/unmark cells."), ("recursion", "DFS the four neighbours.")],
    "n-queens-count": [("backtracking", "One queen per row."), ("pruning", "Column/diagonal masks.")],
    "sudoku-solvable": [("backtracking", "Fill a blank, recurse, undo."), ("pruning", "Skip conflicting digits.")],
    "generate-subsets": [("backtracking", "Choose / un-choose each element.")],
    "generate-permutations": [("backtracking", "Track used values; un-choose after recursing.")],
    "combinations-nk": [("backtracking", "Start index for increasing order.")],
    "generate-parentheses": [("backtracking", "Constrain adds by open/close counts.")],
    "letter-combinations-phone": [("backtracking", "Cartesian product over digit letters.")],
    "restore-ip-addresses": [("backtracking", "Place three dots."), ("string_basics", "Validate each segment.")],
})

FLASHCARDS += [
    ("Backtracking template?", "choose → explore → un-choose: add a choice, recurse, then remove it to restore state.", "seed:backtracking"),
    ("Prompt says 'generate all subsets/permutations/combinations' — technique?", "Backtracking (DFS over the decision tree); n is small so exponential is fine.", "seed:backtracking"),
    ("Backtracker times out — first fix?", "Prune: sort + break past the target, and skip duplicate choices at the same depth.", "seed:pruning"),
    ("Word search / N-queens / Sudoku share what shape?", "Constraint backtracking: try a placement, recurse, undo on conflict.", "seed:backtracking"),
]

EXPANSION_REFS.update({
    "subset-sum-count": {
        "java": "class Solution {\n    int solve(int[] nums, int target){ int[] dp=new int[target+1]; dp[0]=1; for(int x:nums) for(int a=target;a>=x;a--) dp[a]+=dp[a-x]; return dp[target]; }\n}\n",
        "python": "def solve(nums, target):\n    dp=[0]*(target+1); dp[0]=1\n    for x in nums:\n        for a in range(target, x-1, -1): dp[a]+=dp[a-x]\n    return dp[target]\n",
    },
    "n-queens-count": {
        "java": "class Solution {\n    int n;\n    int solve(int n){ this.n=n; return go(0,0,0,0); }\n    int go(int r,int cols,int d1,int d2){ int full=(1<<n)-1; if(cols==full) return 1; int avail=full & ~(cols|d1|d2); int t=0; while(avail!=0){ int p=avail&(-avail); avail-=p; t+=go(r+1, cols|p, (d1|p)<<1, (d2|p)>>1); } return t; }\n}\n",
        "python": "def solve(n):\n    full=(1<<n)-1\n    def go(cols,d1,d2):\n        if cols==full: return 1\n        avail=full & ~(cols|d1|d2); t=0\n        while avail:\n            p=avail&(-avail); avail-=p; t+=go(cols|p,(d1|p)<<1,(d2|p)>>1)\n        return t\n    return go(0,0,0)\n",
    },
    "word-search": {
        "java": "class Solution {\n    char[][] g; int R,C; String w;\n    boolean solve(String[] grid, String word){ R=grid.length; C=R>0?grid[0].length():0; g=new char[R][]; for(int i=0;i<R;i++) g[i]=grid[i].toCharArray(); w=word; boolean[][] s=new boolean[R][C]; for(int r=0;r<R;r++) for(int c=0;c<C;c++) if(dfs(r,c,0,s)) return true; return false; }\n    boolean dfs(int r,int c,int i,boolean[][] s){ if(i==w.length()) return true; if(r<0||r>=R||c<0||c>=C||s[r][c]||g[r][c]!=w.charAt(i)) return false; s[r][c]=true; boolean ok=dfs(r+1,c,i+1,s)||dfs(r-1,c,i+1,s)||dfs(r,c+1,i+1,s)||dfs(r,c-1,i+1,s); s[r][c]=false; return ok; }\n}\n",
        "python": "def solve(grid, word):\n    g=[list(r) for r in grid]; R=len(g); C=len(g[0]) if R else 0\n    def dfs(r,c,i,seen):\n        if i==len(word): return True\n        if r<0 or r>=R or c<0 or c>=C or (r,c) in seen or g[r][c]!=word[i]: return False\n        seen.add((r,c))\n        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):\n            if dfs(r+dr,c+dc,i+1,seen): seen.discard((r,c)); return True\n        seen.discard((r,c)); return False\n    for r in range(R):\n        for c in range(C):\n            if dfs(r,c,0,set()): return True\n    return False\n",
    },
    "generate-parentheses": {
        "java": "import java.util.*;\nclass Solution {\n    String[] solve(int n){ List<String> res=new ArrayList<>(); go(new StringBuilder(),0,0,n,res); return res.toArray(new String[0]); }\n    void go(StringBuilder s,int o,int c,int n,List<String> res){ if(s.length()==2*n){ res.add(s.toString()); return; } if(o<n){ s.append('('); go(s,o+1,c,n,res); s.deleteCharAt(s.length()-1);} if(c<o){ s.append(')'); go(s,o,c+1,n,res); s.deleteCharAt(s.length()-1);} }\n}\n",
        "python": "def solve(n):\n    res=[]\n    def go(s,o,c):\n        if len(s)==2*n: res.append(s); return\n        if o<n: go(s+'(',o+1,c)\n        if c<o: go(s+')',o,c+1)\n    go('',0,0); return res\n",
    },
    "generate-subsets": {
        "java": "import java.util.*;\nclass Solution {\n    String[] solve(int[] nums){ List<String> res=new ArrayList<>(); int n=nums.length; for(int mask=0; mask<(1<<n); mask++){ StringBuilder sb=new StringBuilder(); for(int i=0;i<n;i++) if((mask&(1<<i))!=0){ if(sb.length()>0) sb.append(','); sb.append(nums[i]); } res.add(sb.length()==0?\"-\":sb.toString()); } return res.toArray(new String[0]); }\n}\n",
        "python": "def solve(nums):\n    res=[]; n=len(nums)\n    for mask in range(1<<n):\n        cur=[str(nums[i]) for i in range(n) if mask&(1<<i)]\n        res.append('-' if not cur else ','.join(cur))\n    return res\n",
    },
})

# ===========================================================================
# DOMAIN 4 — HEAP / PRIORITY-QUEUE PATTERNS
# ===========================================================================
import heapq as _hq


def _hp_last_stone(st):
    h = [-x for x in st]
    _hq.heapify(h)
    while len(h) > 1:
        a = -_hq.heappop(h)
        b = -_hq.heappop(h)
        if a != b:
            _hq.heappush(h, -(a - b))
    return -h[0] if h else 0


def _hp_kth_largest(nums, k):
    return sorted(nums)[-k]


def _hp_k_closest(xs, ys, k):
    d = sorted(x * x + y * y for x, y in zip(xs, ys))
    return d[:k]


def _hp_sort_by_freq(s):
    from collections import Counter
    c = Counter(s)
    order = sorted(c.keys(), key=lambda ch: (-c[ch], ch))
    return "".join(ch * c[ch] for ch in order)


def _hp_top_k_words(words, k):
    from collections import Counter
    c = Counter(words)
    order = sorted(c.keys(), key=lambda w: (-c[w], w))
    return order[:k]


def _hp_task(tasks, n):
    from collections import Counter
    c = Counter(tasks)
    mx = max(c.values())
    num_max = sum(1 for v in c.values() if v == mx)
    return max(len(tasks), (mx - 1) * (n + 1) + num_max)


def _hp_reorganize(s):
    from collections import Counter
    c = Counter(s)
    n = len(s)
    if max(c.values()) > (n + 1) // 2:
        return ""
    h = [(-v, ch) for ch, v in c.items()]
    _hq.heapify(h)
    res = []
    prev = None
    while h:
        v, ch = _hq.heappop(h)
        res.append(ch)
        if prev and prev[0] < 0:
            _hq.heappush(h, prev)
        prev = (v + 1, ch)
    return "".join(res)


def _hp_ugly(n):
    dp = [1] * n
    i2 = i3 = i5 = 0
    for i in range(1, n):
        nxt = min(dp[i2] * 2, dp[i3] * 3, dp[i5] * 5)
        dp[i] = nxt
        if nxt == dp[i2] * 2:
            i2 += 1
        if nxt == dp[i3] * 3:
            i3 += 1
        if nxt == dp[i5] * 5:
            i5 += 1
    return dp[n - 1]


_CHK_REORG = (
    "def check(inp, out):\n"
    "    from collections import Counter\n"
    "    s = inp.split('\\n')[0].strip()\n"
    "    o = out.strip()\n"
    "    n = len(s)\n"
    "    feasible = (max(Counter(s).values()) <= (n + 1) // 2) if s else True\n"
    "    if not feasible:\n"
    "        return o == ''\n"
    "    if Counter(o) != Counter(s):\n"
    "        return False\n"
    "    for i in range(1, len(o)):\n"
    "        if o[i] == o[i-1]:\n"
    "            return False\n"
    "    return True\n"
)

HARNESS_DEFS += [
    dict(slug="last-stone-weight", title="Last Stone Weight", difficulty="Easy",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Amazon"],
         description=("Each turn, smash the two **heaviest** stones together; if they differ, the difference goes back. "
                      "Return the weight of the last remaining stone (or 0 if none remain)."),
         constraints="1 ≤ n ≤ 30\n1 ≤ weight ≤ 1000.",
         hints=["You repeatedly need the two largest values.", "A max-heap gives the largest in O(log n).",
                "Pop two, push back their difference if non-zero.", "Continue until 0 or 1 stones remain."],
         opt=("O(n log n)", "O(n)", "Each smash is two pops and a push on a max-heap."),
         editorial="## Approach\nMax-heap; repeatedly pop the two largest, push back their difference; the root at the end is the answer.",
         spec={"name": "solve", "params": [{"name": "stones", "type": "int[]"}], "returns": "int"},
         fn=lambda stones: _hp_last_stone(stones),
         cases=[("example", "Classic", ([2, 7, 4, 1, 8, 1],)), ("example", "All pairs", ([1, 1],)),
                ("hidden", "Single", ([5],)), ("hidden", "Cancel", ([3, 3, 2],)), ("hidden", "Large", ([10, 4, 3, 2, 1],))],
         example_expl=["Smashes down to a single stone of weight 1.", "1 and 1 cancel → 0."]),
    dict(slug="kth-largest-in-array", title="Kth Largest Element in an Array", difficulty="Medium",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Amazon", "Facebook"],
         description="Return the **k-th largest** element (by value, not distinct) in the array.",
         constraints="1 ≤ k ≤ n ≤ 10^4.",
         hints=["A min-heap of size k keeps the k largest seen so far.", "When the heap exceeds k, pop the smallest.",
                "Its root is then the k-th largest.", "Quickselect gives O(n) average as a follow-up."],
         opt=("O(n log k)", "O(k)", "Maintain a size-k min-heap; the root is the k-th largest."),
         editorial="## Approach\nKeep a min-heap of size k; after inserting all elements the root is the k-th largest. (Quickselect is O(n) average.)",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int"},
         fn=lambda nums, k: _hp_kth_largest(nums, k),
         cases=[("example", "k=2", ([3, 2, 1, 5, 6, 4], 2)), ("example", "k=4", ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)),
                ("hidden", "k=1", ([1], 1)), ("hidden", "All same", ([2, 2, 2], 2)), ("hidden", "Largest", ([7, 6, 5], 1))],
         example_expl=["2nd largest of the array is 5.", "4th largest is 4."]),
    dict(slug="k-closest-distances", title="K Closest Points (distances)", difficulty="Medium",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Amazon", "Facebook"],
         description=("Points are given as parallel arrays `xs`, `ys`. Return the **squared distances** from the origin of "
                      "the `k` closest points, sorted ascending. (Squared distance avoids floating point; sorting makes the answer unique.)"),
         constraints="1 ≤ k ≤ n ≤ 10^4.",
         hints=["Squared distance x*x + y*y preserves ordering — skip the square root.",
                "A max-heap of size k keeps the k smallest.", "Or just sort all distances and take the first k.",
                "Return them sorted ascending."],
         opt=("O(n log k)", "O(k)", "Size-k max-heap of squared distances (or full sort)."),
         editorial="## Approach\nCompute squared distances, keep the k smallest with a max-heap (or sort), return them sorted.",
         spec={"name": "solve", "params": [{"name": "xs", "type": "int[]"}, {"name": "ys", "type": "int[]"}, {"name": "k", "type": "int"}], "returns": "int[]"},
         fn=lambda xs, ys, k: _hp_k_closest(xs, ys, k),
         cases=[("example", "Two", ([1, -2, 3], [3, 2, -1], 2)), ("example", "One", ([1, 3], [3, 3], 1)),
                ("hidden", "All", ([0, 1], [0, 1], 2)), ("hidden", "Origin", ([0], [0], 1)), ("hidden", "Ties", ([1, -1, 1], [1, 1, -1], 2))],
         example_expl=["Squared distances 10,8,10 → two closest 8,10.", "Closest squared distance is 18."]),
    dict(slug="sort-by-frequency", title="Sort Characters By Frequency", difficulty="Easy",
         topics=["Data Structures", "Strings"], subtopics=["Priority Queue", "Counting"], companies=["Amazon", "Google"],
         description=("Rearrange the characters of `s` in **decreasing frequency**. Break ties by **ascending character** so the "
                      "answer is unique."),
         constraints="1 ≤ |s| ≤ 10^4\nLetters and digits.",
         hints=["Count each character's frequency.", "Order characters by frequency descending.",
                "Break ties by the character itself (ascending) for a unique answer.", "Emit each character freq times."],
         opt=("O(n + a log a)", "O(a)", "Count then sort the distinct characters (alphabet a)."),
         editorial="## Approach\nCount frequencies; sort distinct chars by (-freq, char); output each repeated freq times.",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "string"},
         fn=lambda s: _hp_sort_by_freq(s),
         cases=[("example", "tree", ("tree",)), ("example", "cccaaa", ("cccaaa",)),
                ("hidden", "Single", ("a",)), ("hidden", "Tie", ("bca",)), ("hidden", "Digits", ("2211",))],
         example_expl=["'ee' then 'r','t' (tie → ascending) → 'eert'.", "'aaaccc' by tie rule (a before c)."]),
    dict(slug="top-k-frequent-words", title="Top K Frequent Words", difficulty="Medium",
         topics=["Data Structures", "Strings"], subtopics=["Priority Queue", "Counting"], companies=["Amazon", "Bloomberg"],
         description=("Given `words` and `k`, return the `k` most frequent words, ordered by **frequency descending**; break ties "
                      "**lexicographically** (ascending)."),
         constraints="1 ≤ k ≤ number of distinct words.",
         hints=["Count word frequencies.", "Sort by frequency descending, then word ascending.",
                "Take the first k.", "A heap of size k also works with the right comparator."],
         opt=("O(n log k)", "O(n)", "Count, then a size-k heap or a full sort with the tie rule."),
         editorial="## Approach\nCount; sort keys by (-freq, word); return the first k.",
         spec={"name": "solve", "params": [{"name": "words", "type": "string[]"}, {"name": "k", "type": "int"}], "returns": "string[]"},
         fn=lambda words, k: _hp_top_k_words(words, k),
         cases=[("example", "Two", (["i", "love", "code", "i", "love", "you"], 2)), ("example", "Tie", (["a", "b", "c", "a", "b", "a", "c"], 2)),
                ("hidden", "One", (["apple"], 1)), ("hidden", "All", (["x", "y", "z"], 3)), ("hidden", "Freq", (["dog", "cat", "dog", "cat", "dog"], 1))],
         example_expl=["'i' and 'love' both appear twice → i, love (tie by word).", "a(3), b(2) → a, b."]),
    dict(slug="task-scheduler", title="Task Scheduler", difficulty="Medium",
         topics=["Data Structures"], subtopics=["Priority Queue", "Greedy"], companies=["Facebook", "Amazon"],
         description=("`tasks` is a string of task letters; identical tasks need at least `n` intervals of cooldown between "
                      "them. Return the **minimum number of intervals** (including idles) to finish all tasks."),
         constraints="1 ≤ |tasks| ≤ 10^4\n0 ≤ n ≤ 100.",
         hints=["The most frequent task dictates the skeleton.", "Lay out max-frequency tasks separated by n gaps.",
                "Fill gaps with other tasks or idles.", "Answer = max(len(tasks), (maxFreq-1)*(n+1) + countOfMax)."],
         opt=("O(n)", "O(1)", "Greedy formula from the maximum frequency and how many share it."),
         editorial="## Approach\nThe busiest task forms (maxFreq-1) blocks of size (n+1) plus a final row of the maxima; the answer never dips below len(tasks).",
         spec={"name": "solve", "params": [{"name": "tasks", "type": "string"}, {"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda tasks, n: _hp_task(tasks, n),
         cases=[("example", "AAABBB n=2", ("AAABBB", 2)), ("example", "No cooldown", ("AAABBB", 0)),
                ("hidden", "Single", ("A", 5)), ("hidden", "Many idle", ("AAAA", 3)), ("hidden", "Mixed", ("AABBCC", 1))],
         example_expl=["A B idle A B idle A B → 8.", "n=0 → just 6."]),
    dict(slug="ugly-number-ii", title="Ugly Number II", difficulty="Medium",
         topics=["Data Structures", "Math"], subtopics=["Priority Queue"], companies=["Amazon"],
         description="An **ugly number** has only 2, 3, and 5 as prime factors (1 counts). Return the `n`-th ugly number (1-indexed).",
         constraints="1 ≤ n ≤ 1690.",
         hints=["Every ugly number is a previous ugly number times 2, 3, or 5.",
                "Keep three pointers into the sequence, one per multiplier.",
                "The next ugly number is the min of the three candidates.",
                "Advance every pointer whose candidate equals that min (to skip duplicates)."],
         opt=("O(n)", "O(n)", "Three-pointer merge of the ×2, ×3, ×5 streams."),
         editorial="## Approach\nBuild the sequence: next = min(dp[i2]*2, dp[i3]*3, dp[i5]*5); advance each pointer matching the min.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}], "returns": "int"},
         fn=lambda n: _hp_ugly(n),
         cases=[("example", "n=10", (10,)), ("example", "n=1", (1,)),
                ("hidden", "n=7", (7,)), ("hidden", "n=15", (15,)), ("hidden", "n=100", (100,))],
         example_expl=["The 10th ugly number is 12.", "The 1st is 1."]),
    dict(slug="reorganize-string", title="Reorganize String", difficulty="Medium",
         topics=["Data Structures", "Strings"], subtopics=["Priority Queue", "Greedy"], companies=["Amazon", "Google"],
         description=("Rearrange `s` so that **no two adjacent characters are the same**. Return any valid arrangement, or an "
                      "empty string if it's impossible. A special judge accepts any correct rearrangement."),
         constraints="1 ≤ |s| ≤ 500\nLowercase letters.",
         hints=["Impossible iff some character's count exceeds (n+1)/2.",
                "Always place the currently most frequent character that isn't the one you just placed.",
                "A max-heap by remaining count drives the greedy.", "Hold the just-used character aside for one step."],
         opt=("O(n log a)", "O(a)", "Greedy: repeatedly place the most frequent non-repeating character."),
         editorial="## Approach\nMax-heap by count; each step pop the top, append it, and re-insert the previously used char (now cooled down).",
         spec={"name": "solve", "params": [{"name": "s", "type": "string"}], "returns": "string"},
         fn=lambda s: _hp_reorganize(s), judge_mode="checker", checker=_CHK_REORG,
         cases=[("example", "Possible", ("aab",)), ("example", "Impossible", ("aaab",)),
                ("hidden", "All same", ("aaaa",)), ("hidden", "Balanced", ("aabbcc",)), ("hidden", "Single", ("a",))],
         example_expl=["'aba' is a valid arrangement.", "Too many a's → empty string."]),
]

# ---- raw op-stream / multi-list heap problems ----

def _sol_kth_stream(inp):
    L = inp.split('\n')
    k = int(L[0].split()[0])
    initial = list(map(int, L[1].split())) if len(L) > 1 and L[1].strip() else []
    q = int(L[2])
    h = []
    for x in initial:
        _hq.heappush(h, x)
        if len(h) > k:
            _hq.heappop(h)
    out = []
    for i in range(q):
        x = int(L[3 + i])
        _hq.heappush(h, x)
        if len(h) > k:
            _hq.heappop(h)
        out.append(str(h[0]))
    return "\n".join(out)


def _sol_merge_k(inp):
    L = inp.split('\n')
    k = int(L[0])
    allv = []
    for i in range(1, k + 1):
        if i < len(L) and L[i].strip():
            allv += list(map(int, L[i].split()))
    allv.sort()
    return " ".join(map(str, allv))


def _sol_median(inp):
    import bisect
    L = inp.split('\n')
    q = int(L[0])
    arr = []
    out = []
    for i in range(1, q + 1):
        parts = L[i].split()
        if parts[0] == "add":
            bisect.insort(arr, int(parts[1]))
        else:
            m = len(arr)
            med = arr[m // 2] if m % 2 else (arr[m // 2 - 1] + arr[m // 2]) / 2
            out.append("%.1f" % med)
    return "\n".join(out)


def _sol_srange(inp):
    L = inp.split('\n')
    k = int(L[0])
    lists = [list(map(int, L[1 + i].split())) for i in range(k)]
    h = []
    cur_max = -(10 ** 18)
    for i, lst in enumerate(lists):
        _hq.heappush(h, (lst[0], i, 0))
        cur_max = max(cur_max, lst[0])
    best = (-(10 ** 18), 10 ** 18)
    while True:
        v, i, j = _hq.heappop(h)
        if (cur_max - v < best[1] - best[0]) or (cur_max - v == best[1] - best[0] and v < best[0]):
            best = (v, cur_max)
        if j + 1 == len(lists[i]):
            break
        nv = lists[i][j + 1]
        cur_max = max(cur_max, nv)
        _hq.heappush(h, (nv, i, j + 1))
    return "%d %d" % (best[0], best[1])


def _raw_starters(hint, ret_hint=""):
    java = ("import java.util.*;\nimport java.io.*;\npublic class Main {\n"
            "    public static void main(String[] a) throws IOException {\n"
            "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n"
            "        // " + hint + "\n"
            "        // TODO: read input, compute, print" + (" " + ret_hint if ret_hint else "") + "\n"
            "    }\n}\n")
    py = ("import sys\ndef main():\n    data = sys.stdin.read().split('\\n')\n    # " + hint + "\n    # TODO\nmain()\n")
    js = ("const L = require('fs').readFileSync(0,'utf8').split('\\n');\n// " + hint + "\n// TODO\n")
    return java, py, js


_KS_J, _KS_P, _KS_JS = _raw_starters("line1: k; line2: initial numbers; line3: Q; then Q integers to add")
_MK_J, _MK_P, _MK_JS = _raw_starters("line1: k; next k lines: each a sorted list")
_MD_J, _MD_P, _MD_JS = _raw_starters("line1: Q; next Q lines: 'add x' or 'median'; print each median to one decimal")
_SR_J, _SR_P, _SR_JS = _raw_starters("line1: k; next k lines: sorted lists")

DEFS += [
    dict(slug="kth-largest-in-stream", title="Kth Largest in a Stream", difficulty="Easy",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Amazon"],
         description=("Maintain the k-th largest value in a growing stream.\n\n"
                      "### Input\n- Line 1: `k`.\n- Line 2: the initial numbers (space-separated; may be blank).\n"
                      "- Line 3: `Q`, the number of additions.\n- Next `Q` lines: an integer to add.\n\n"
                      "### Output\nAfter each addition, the k-th largest value so far (one per line)."),
         constraints="1 ≤ k ≤ 10^4\nThere are always at least k elements after each add.",
         hints=["Keep a min-heap holding only the k largest elements.", "On add, push, then pop if the size exceeds k.",
                "The heap root is the k-th largest.", "Each query is O(log k)."],
         opt=("O((m+Q) log k)", "O(k)", "Size-k min-heap; root is the answer after every add."),
         editorial="## Approach\nA size-k min-heap: push each value, evict the smallest when size > k, and read the root as the k-th largest.",
         ref=_sol_kth_stream, starter_py=_KS_P, starter_js=_KS_JS,
         cases=[("example", "k=3", "3\n4 5 8 2\n3\n3\n5\n10\n"), ("example", "k=1", "1\n\n2\n5\n7\n"),
                ("hidden", "k=2", "2\n1 2\n2\n3\n4\n"), ("hidden", "Repeats", "2\n5 5\n1\n5\n")],
         example_expl=["After adding 3,5,10 the 3rd-largest is 4,5,5.", "1st largest tracks the running max."]),
    dict(slug="merge-k-sorted", title="Merge k Sorted Lists", difficulty="Hard",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Amazon", "Google", "Facebook"],
         description=("Merge `k` sorted lists into one sorted list.\n\n"
                      "### Input\n- Line 1: `k`.\n- Next `k` lines: each a sorted list of integers (space-separated; may be blank).\n\n"
                      "### Output\nThe merged sorted list on one line (blank line if everything is empty)."),
         constraints="0 ≤ total elements ≤ 10^5.",
         hints=["A min-heap of the k list-heads yields the global minimum each step.",
                "Pop the smallest, then push the next element from that list.",
                "Total work is O(N log k).", "Or concatenate and sort for O(N log N)."],
         opt=("O(N log k)", "O(k)", "Min-heap over the current front of each list."),
         editorial="## Approach\nPush the head of each list into a min-heap keyed by value; repeatedly pop the smallest and push its successor.",
         ref=_sol_merge_k, starter_py=_MK_P, starter_js=_MK_JS,
         cases=[("example", "Three lists", "3\n1 4 5\n1 3 4\n2 6\n"), ("example", "With empty", "2\n\n1 2 3\n"),
                ("hidden", "All empty", "2\n\n\n"), ("hidden", "One list", "1\n5 10 15\n"), ("hidden", "Interleave", "2\n1 3 5\n2 4 6\n")],
         example_expl=["Merges to 1 1 2 3 4 4 5 6.", "Only the non-empty list remains."]),
    dict(slug="median-from-stream", title="Find Median from Data Stream", difficulty="Hard",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Amazon", "Google", "Facebook"],
         description=("Support adding numbers and querying the running median.\n\n"
                      "### Input\n- Line 1: `Q`.\n- Next `Q` lines: `add x` to insert `x`, or `median` to query.\n\n"
                      "### Output\nFor each `median` query, the current median printed to **one decimal place**."),
         constraints="1 ≤ Q ≤ 10^5.",
         hints=["Keep a max-heap for the lower half and a min-heap for the upper half.",
                "Balance so their sizes differ by at most 1.",
                "Odd count → the larger heap's top; even → average of the two tops.",
                "Each add is O(log n); each query is O(1)."],
         opt=("O(log n) per add", "O(n)", "Two heaps split the data at the median."),
         editorial="## Approach\nTwo heaps: a max-heap (low half) and a min-heap (high half). Keep them balanced; the median is the top(s).",
         ref=_sol_median, starter_py=_MD_P, starter_js=_MD_JS,
         cases=[("example", "Mixed", "5\nadd 1\nadd 2\nmedian\nadd 3\nmedian\n"), ("example", "Even", "3\nadd 4\nadd 2\nmedian\n"),
                ("hidden", "Single", "2\nadd 7\nmedian\n"), ("hidden", "Growing", "6\nadd 5\nadd 1\nadd 3\nmedian\nadd 2\nmedian\n")],
         example_expl=["Median of {1,2} is 1.5, of {1,2,3} is 2.0.", "Median of {2,4} is 3.0."]),
    dict(slug="smallest-range-k-lists", title="Smallest Range Covering k Lists", difficulty="Hard",
         topics=["Data Structures"], subtopics=["Priority Queue"], companies=["Google"],
         description=("Find the smallest range `[a, b]` that includes at least one number from each of the `k` sorted lists. "
                      "Among equal-width ranges, choose the one with the smallest start.\n\n"
                      "### Input\n- Line 1: `k`.\n- Next `k` lines: sorted lists (space-separated, non-empty).\n\n"
                      "### Output\n`a b` — the range bounds."),
         constraints="1 ≤ k ≤ 3500\nAll lists are non-empty and sorted.",
         hints=["Merge the lists with a min-heap; track the current maximum across the fronts.",
                "The range is [heap min, current max].", "Advance the list that owns the minimum.",
                "Stop when any list is exhausted."],
         opt=("O(N log k)", "O(k)", "Min-heap sweep keeping one element from each list in the window."),
         editorial="## Approach\nHeap of one element per list; the window is [min, max]. Pop the min, record the range, push the next from that list; stop when a list ends.",
         ref=_sol_srange, starter_py=_SR_P, starter_js=_SR_JS,
         cases=[("example", "Three", "3\n4 10 15 24 26\n0 9 12 20\n5 18 22 30\n"), ("example", "Simple", "2\n1 2 3\n2 3 4\n"),
                ("hidden", "Singletons", "3\n1\n2\n3\n"), ("hidden", "Same", "2\n5 5\n5 5\n"), ("hidden", "Overlap", "2\n1 5 9\n4 6\n")],
         example_expl=["[20,24] covers one from each list.", "[2,2] covers all three lists."]),
]
JAVA_STARTERS.update({
    "kth-largest-in-stream": _KS_J, "merge-k-sorted": _MK_J,
    "median-from-stream": _MD_J, "smallest-range-k-lists": _SR_J,
})

CONCEPTS.update({
    "top_k": {
        "name": "Top-K with a Heap",
        "what": "Keeping only the k best elements in a size-k heap so the answer stays available in O(log k) per item.",
        "deep": "For 'k largest / k most frequent / k closest' you never need to sort everything. A min-heap of size k holds the current k largest: push each element and, if the heap grows past k, pop the smallest. The root is then the k-th best. It streams in one pass with O(k) memory.",
        "java": "PriorityQueue<Integer> pq = new PriorityQueue<>(); for (int x : a){ pq.offer(x); if (pq.size() > k) pq.poll(); }  // pq.peek() = k-th largest",
    },
    "two_heaps": {
        "name": "Two Heaps (Running Median)",
        "what": "Splitting data into a max-heap of the lower half and a min-heap of the upper half to read the median in O(1).",
        "deep": "Balance two heaps so the low half (max-heap) and high half (min-heap) differ in size by at most one. The median is the larger heap's top, or the average of both tops when sizes are equal. Insertion rebalances in O(log n). The same shape solves 'schedule to balance load' problems.",
        "java": "PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder()), hi = new PriorityQueue<>(); insert into lo, push lo.poll() to hi, rebalance if hi bigger.",
    },
    "heap_greedy": {
        "name": "Greedy with a Heap",
        "what": "Repeatedly acting on the current extreme element, re-inserting updated state, to make a globally good sequence of choices.",
        "deep": "When each step should take the largest (or smallest) remaining item and then modify it, a heap keeps that extreme at your fingertips: last-stone-weight, reorganize-string, and task scheduling all pop the max, transform it, and push it back. Correctness rests on the greedy exchange argument that the local extreme is always safe to take.",
        "java": "A PriorityQueue keyed by the quantity you greedily extremize; loop poll → update → offer until done.",
    },
})
CATEGORY.update({"top_k": "Data Structures", "two_heaps": "Data Structures", "heap_greedy": "Data Structures"})
PATTERN_FROM.update({"Priority Queue": "Heap / Priority Queue", "Top-K": "Heap / Priority Queue", "Two Heaps": "Heap / Priority Queue"})

LESSONS.update({
    "top_k": (
        "# Top-K with a Heap\n\n"
        "'Give me the k largest / most frequent / closest' never needs a full sort. Keep a **size-k min-heap**: the k best seen so far live inside it, and the smallest of them sits at the root ready to be evicted.\n\n"
        "```java\n"
        "PriorityQueue<Integer> pq = new PriorityQueue<>(); // min-heap\n"
        "for (int x : nums) {\n"
        "    pq.offer(x);\n"
        "    if (pq.size() > k) pq.poll();   // drop the smallest\n"
        "}\n"
        "int kthLargest = pq.peek();          // root = k-th largest\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'k largest'*, *'k most frequent'*, *'k closest'*, *'top k'*. Full sort is O(n log n); the heap is O(n log k) and streams.\n\n"
        "## Simulated solve — 2nd largest of `[3,2,1,5,6,4]`\n"
        "| x | heap (size ≤ 2) |\n"
        "|---|---|\n"
        "| 3 | [3] |\n"
        "| 2 | [2,3] |\n"
        "| 1 | [2,3] (1 popped) |\n"
        "| 5 | [3,5] |\n"
        "| 6 | [5,6] |\n"
        "| 4 | [5,6] → root **5** |\n"
    ),
    "two_heaps": (
        "# Two Heaps — Running Median\n\n"
        "Split the numbers into two halves and keep each in a heap facing the middle:\n\n"
        "```java\n"
        "PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder()); // low half, max on top\n"
        "PriorityQueue<Integer> hi = new PriorityQueue<>();                            // high half, min on top\n"
        "void add(int x){\n"
        "    lo.offer(x);\n"
        "    hi.offer(lo.poll());              // funnel the biggest low into hi\n"
        "    if (hi.size() > lo.size()) lo.offer(hi.poll()); // rebalance\n"
        "}\n"
        "double median(){ return lo.size() > hi.size() ? lo.peek() : (lo.peek() + hi.peek()) / 2.0; }\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'median of a stream'*, *'balance two groups'*, *'kth from each side'*. The invariant — `lo` never smaller than `hi`, sizes within one — is the whole trick.\n\n"
        "## Simulated solve — medians while adding 1,2,3\n"
        "| add | lo (max) | hi (min) | median |\n"
        "|---|---|---|---|\n"
        "| 1 | [1] | [] | 1.0 |\n"
        "| 2 | [1] | [2] | 1.5 |\n"
        "| 3 | [2,1] | [3] | 2.0 |\n"
    ),
    "heap_greedy": (
        "# Greedy with a Heap\n\n"
        "When every step should grab the current **extreme**, transform it, and put it back, a heap keeps that extreme O(log n) away.\n\n"
        "```java\n"
        "PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());\n"
        "for (int s : stones) pq.offer(s);\n"
        "while (pq.size() > 1) {\n"
        "    int a = pq.poll(), b = pq.poll();   // two heaviest\n"
        "    if (a != b) pq.offer(a - b);          // push the remainder back\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'repeatedly take the largest/most-frequent'*, *'smash / merge the two biggest'*, *'schedule the busiest first'* — last-stone-weight, reorganize-string, task-scheduler.\n\n"
        "## Why the greedy is safe\n"
        "Taking the extreme now never blocks a better future: any solution can be rearranged to make the same extreme choice first without getting worse (an exchange argument)."
    ),
})

_EX_HEAP_TOPK = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt(); int[] a = new int[n];\n"
    "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
    "        int k = sc.nextInt();\n"
    "        PriorityQueue<Integer> pq = new PriorityQueue<>();\n"
    "        for (int x : a) {\n"
    "            pq.offer(x);\n"
    "            if (pq.size() > k) pq.poll();\n"
    "        }\n"
    "        System.out.println(pq.peek());\n"
    "    }\n}\n"
)
_EX_HEAP_MEDIAN = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt();\n"
    "        PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder());\n"
    "        PriorityQueue<Integer> hi = new PriorityQueue<>();\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            int x = sc.nextInt();\n"
    "            lo.offer(x);\n"
    "            hi.offer(lo.poll());\n"
    "            if (hi.size() > lo.size()) lo.offer(hi.poll());\n"
    "        }\n"
    "        double m = lo.size() > hi.size() ? (double) lo.peek() : (lo.peek() + hi.peek()) / 2.0;\n"
    "        System.out.println(String.format(java.util.Locale.US, \"%.1f\", m));\n"
    "    }\n}\n"
)
EXERCISES.update({
    "top_k": [
        ex("top_k-evict", "Evict past size k",
           "Find the k-th largest with a size-k min-heap. Fill the blank so the heap drops its smallest once it exceeds k.",
           _EX_HEAP_TOPK, ["if (pq.size() > k) pq.poll();"],
           [("6 3 2 1 5 6 4 2", "5"), ("3 7 6 5 1", "7"), ("1 9 1", "9")],
           hint="When size exceeds k, the smallest can't be in the top k — poll it.", source_slug="kth-largest-in-array"),
        ex("top_k-root", "Read the answer",
           "Fill the blank so the program prints the heap root — the k-th largest.",
           _EX_HEAP_TOPK, ["System.out.println(pq.peek());"],
           [("6 3 2 1 5 6 4 2", "5"), ("4 4 3 2 1 2", "3"), ("4 2 5 6 1 2", "5")],
           hint="The min of the k largest is the k-th largest — pq.peek().", source_slug="kth-largest-in-array"),
    ],
    "two_heaps": [
        ex("two_heaps-balance", "Rebalance the heaps",
           "Running median with two heaps. Fill the blank so the heaps never differ in size by more than one.",
           _EX_HEAP_MEDIAN, ["if (hi.size() > lo.size()) lo.offer(hi.poll());"],
           [("3 1 2 3", "2.0"), ("4 1 2 3 4", "2.5"), ("1 5", "5.0")],
           hint="If the high heap grew larger, move its top back to the low heap.", source_slug="median-from-stream"),
    ],
})

PREREQS.update({
    "last-stone-weight": [("heap", "Max-heap of the two heaviest."), ("heap_greedy", "Pop-transform-push.")],
    "kth-largest-in-array": [("top_k", "Size-k min-heap."), ("heap", "peek is the answer.")],
    "k-closest-distances": [("top_k", "Keep the k smallest distances."), ("sorting", "Or sort all distances.")],
    "sort-by-frequency": [("hashing", "Count characters."), ("sorting", "Order by frequency, tie by char.")],
    "top-k-frequent-words": [("top_k", "Heap or sort by (-freq, word)."), ("hashing", "Count words.")],
    "task-scheduler": [("heap_greedy", "Most frequent task shapes the schedule."), ("greedy", "Fill gaps.")],
    "ugly-number-ii": [("dp", "Three-pointer merge."), ("heap", "Or a min-heap of candidates.")],
    "reorganize-string": [("heap_greedy", "Place the most frequent non-repeating char."), ("hashing", "Counts.")],
    "kth-largest-in-stream": [("top_k", "Size-k min-heap on a stream.")],
    "merge-k-sorted": [("heap", "Min-heap over the k fronts.")],
    "median-from-stream": [("two_heaps", "Low max-heap + high min-heap.")],
    "smallest-range-k-lists": [("heap", "Min-heap sweep across lists."), ("sliding_window", "Window [min,max] across fronts.")],
})

FLASHCARDS += [
    ("'k largest / most frequent / closest' — technique?", "Size-k heap (min-heap for k largest): push, pop when size>k; root is the k-th best. O(n log k).", "seed:top_k"),
    ("Running median of a stream?", "Two heaps: max-heap (low half) + min-heap (high half), kept balanced; median is the top(s).", "seed:two_heaps"),
    ("'Repeatedly take the biggest and modify it' — technique?", "Greedy with a heap: poll the extreme, transform, offer it back (last-stone, reorganize, scheduler).", "seed:heap_greedy"),
    ("Merge k sorted lists efficiently?", "Min-heap of the k current fronts; pop the min, push its successor. O(N log k).", "seed:heap_greedy"),
]

EXPANSION_REFS.update({
    "last-stone-weight": {
        "java": "import java.util.*;\nclass Solution {\n    int solve(int[] stones){ PriorityQueue<Integer> pq=new PriorityQueue<>(Collections.reverseOrder()); for(int s:stones) pq.offer(s); while(pq.size()>1){ int a=pq.poll(), b=pq.poll(); if(a!=b) pq.offer(a-b); } return pq.isEmpty()?0:pq.peek(); }\n}\n",
        "python": "import heapq\ndef solve(stones):\n    h=[-x for x in stones]; heapq.heapify(h)\n    while len(h)>1:\n        a=-heapq.heappop(h); b=-heapq.heappop(h)\n        if a!=b: heapq.heappush(h,-(a-b))\n    return -h[0] if h else 0\n",
    },
    "kth-largest-in-array": {
        "java": "import java.util.*;\nclass Solution {\n    int solve(int[] nums, int k){ PriorityQueue<Integer> pq=new PriorityQueue<>(); for(int x:nums){ pq.offer(x); if(pq.size()>k) pq.poll(); } return pq.peek(); }\n}\n",
        "python": "import heapq\ndef solve(nums, k):\n    h=[]\n    for x in nums:\n        heapq.heappush(h,x)\n        if len(h)>k: heapq.heappop(h)\n    return h[0]\n",
    },
    "ugly-number-ii": {
        "java": "class Solution {\n    int solve(int n){ int[] dp=new int[n]; dp[0]=1; int i2=0,i3=0,i5=0; for(int i=1;i<n;i++){ int nx=Math.min(dp[i2]*2, Math.min(dp[i3]*3, dp[i5]*5)); dp[i]=nx; if(nx==dp[i2]*2) i2++; if(nx==dp[i3]*3) i3++; if(nx==dp[i5]*5) i5++; } return dp[n-1]; }\n}\n",
        "python": "def solve(n):\n    dp=[1]*n; i2=i3=i5=0\n    for i in range(1,n):\n        nx=min(dp[i2]*2, dp[i3]*3, dp[i5]*5); dp[i]=nx\n        if nx==dp[i2]*2: i2+=1\n        if nx==dp[i3]*3: i3+=1\n        if nx==dp[i5]*5: i5+=1\n    return dp[n-1]\n",
    },
    "reorganize-string": {
        "java": "import java.util.*;\nclass Solution {\n    String solve(String s){ int[] cnt=new int[26]; for(char c:s.toCharArray()) cnt[c-'a']++; int n=s.length(); for(int v:cnt) if(v>(n+1)/2) return \"\"; PriorityQueue<int[]> pq=new PriorityQueue<>((x,y)->y[1]-x[1]); for(int i=0;i<26;i++) if(cnt[i]>0) pq.offer(new int[]{i,cnt[i]}); StringBuilder sb=new StringBuilder(); int[] prev=null; while(!pq.isEmpty()){ int[] cur=pq.poll(); sb.append((char)('a'+cur[0])); if(prev!=null && prev[1]>0) pq.offer(prev); cur[1]--; prev=cur; } return sb.toString(); }\n}\n",
        "python": "import heapq\nfrom collections import Counter\ndef solve(s):\n    c=Counter(s); n=len(s)\n    if max(c.values())>(n+1)//2: return ''\n    h=[(-v,ch) for ch,v in c.items()]; heapq.heapify(h)\n    res=[]; prev=None\n    while h:\n        v,ch=heapq.heappop(h); res.append(ch)\n        if prev and prev[0]<0: heapq.heappush(h,prev)\n        prev=(v+1,ch)\n    return ''.join(res)\n",
    },
    "merge-k-sorted": {
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    public static void main(String[] a) throws IOException {\n        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));\n        int k=Integer.parseInt(br.readLine().trim()); List<Integer> all=new ArrayList<>();\n        for(int i=0;i<k;i++){ String ln=br.readLine(); if(ln==null) ln=\"\"; ln=ln.trim(); if(!ln.isEmpty()){ for(String t:ln.split(\"\\\\s+\")) all.add(Integer.parseInt(t)); } }\n        Collections.sort(all); StringBuilder sb=new StringBuilder(); for(int i=0;i<all.size();i++){ if(i>0) sb.append(' '); sb.append(all.get(i)); } System.out.println(sb.toString());\n    }\n}\n",
        "python": "import sys\ndef main():\n    L=sys.stdin.read().split('\\n'); k=int(L[0]); allv=[]\n    for i in range(1,k+1):\n        if i<len(L) and L[i].strip(): allv+=list(map(int,L[i].split()))\n    allv.sort(); print(' '.join(map(str,allv)))\nmain()\n",
    },
    "median-from-stream": {
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    public static void main(String[] a) throws IOException {\n        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));\n        int q=Integer.parseInt(br.readLine().trim());\n        PriorityQueue<Integer> lo=new PriorityQueue<>(Collections.reverseOrder()), hi=new PriorityQueue<>();\n        StringBuilder sb=new StringBuilder();\n        for(int i=0;i<q;i++){ StringTokenizer st=new StringTokenizer(br.readLine()); String op=st.nextToken(); if(op.equals(\"add\")){ int x=Integer.parseInt(st.nextToken()); lo.offer(x); hi.offer(lo.poll()); if(hi.size()>lo.size()) lo.offer(hi.poll()); } else { double m = lo.size()>hi.size() ? (double)lo.peek() : (lo.peek()+hi.peek())/2.0; sb.append(String.format(Locale.US, \"%.1f\", m)).append('\\n'); } }\n        System.out.print(sb);\n    }\n}\n",
        "python": "import sys, bisect\ndef main():\n    L=sys.stdin.read().split('\\n'); q=int(L[0]); arr=[]; out=[]\n    for i in range(1,q+1):\n        p=L[i].split()\n        if p[0]=='add': bisect.insort(arr,int(p[1]))\n        else:\n            m=len(arr); med=arr[m//2] if m%2 else (arr[m//2-1]+arr[m//2])/2; out.append('%.1f'%med)\n    sys.stdout.write('\\n'.join(out))\nmain()\n",
    },
})

# ===========================================================================
# DOMAIN 5 — INTERVALS   (parallel arrays: int[] starts, int[] ends)
# ===========================================================================
_NEG = -(10 ** 18)


def _iv_can_attend(s, e):
    iv = sorted(zip(s, e))
    for i in range(1, len(iv)):
        if iv[i][0] < iv[i - 1][1]:
            return False
    return True


def _iv_merge(s, e):
    merged = []
    for a, b in sorted(zip(s, e)):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    out = []
    for a, b in merged:
        out += [a, b]
    return out


def _iv_insert(s, e, ns, ne):
    iv = sorted(list(zip(s, e)) + [(ns, ne)])
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    out = []
    for a, b in merged:
        out += [a, b]
    return out


def _iv_min_rooms(s, e):
    ss = sorted(s)
    ee = sorted(e)
    i = j = cur = best = 0
    while i < len(ss):
        if ss[i] < ee[j]:
            cur += 1
            best = max(best, cur)
            i += 1
        else:
            cur -= 1
            j += 1
    return best


def _iv_non_overlap(s, e):
    count = 0
    end = _NEG
    for a, b in sorted(zip(s, e), key=lambda p: p[1]):
        if a >= end:
            end = b
        else:
            count += 1
    return count


def _iv_arrows(s, e):
    arrows = 0
    end = _NEG
    for a, b in sorted(zip(s, e), key=lambda p: p[1]):
        if a > end:
            arrows += 1
            end = b
    return arrows


def _iv_inter(a_s, a_e, b_s, b_e):
    A = sorted(zip(a_s, a_e))
    B = sorted(zip(b_s, b_e))
    i = j = 0
    out = []
    while i < len(A) and j < len(B):
        lo = max(A[i][0], B[j][0])
        hi = min(A[i][1], B[j][1])
        if lo <= hi:
            out += [lo, hi]
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1
    return out


def _iv_carpool(frm, to, num, cap):
    from collections import defaultdict
    d = defaultdict(int)
    for f, t, n in zip(frm, to, num):
        d[f] += n
        d[t] -= n
    cur = 0
    for loc in sorted(d):
        cur += d[loc]
        if cur > cap:
            return False
    return True


def _iv_free(s, e):
    merged = []
    for a, b in sorted(zip(s, e)):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    out = []
    for i in range(1, len(merged)):
        out += [merged[i - 1][1], merged[i][0]]
    return out


HARNESS_DEFS += [
    dict(slug="can-attend-meetings", title="Meeting Rooms", difficulty="Easy",
         topics=["Searching & Sorting"], subtopics=["Sorting", "Intervals"], companies=["Amazon", "Facebook"],
         description=("Meetings are given as parallel arrays `starts` and `ends`. Return `true` if a single person could "
                      "attend **all** of them (no two overlap)."),
         constraints="0 ≤ n ≤ 10^4\nstarts[i] < ends[i].",
         hints=["Sort the meetings by start time.", "Overlap exists if a meeting starts before the previous one ends.",
                "One linear scan after sorting suffices.", "Touching (end == next start) is allowed."],
         opt=("O(n log n)", "O(n)", "Sort by start, then check adjacent pairs."),
         editorial="## Approach\nSort by start; if any meeting's start is before the previous end, they overlap.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}], "returns": "bool"},
         fn=lambda starts, ends: _iv_can_attend(starts, ends),
         cases=[("example", "Overlap", ([0, 5, 15], [30, 10, 20])), ("example", "Clear", ([7, 2], [10, 4])),
                ("hidden", "Touching", ([1, 2], [2, 3])), ("hidden", "Single", ([5], [6])), ("hidden", "Nested", ([1, 2], [10, 3]))],
         example_expl=["[0,30] overlaps [5,10] → false.", "[2,4] then [7,10] don't overlap → true."]),
    dict(slug="merge-intervals", title="Merge Intervals", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Sorting", "Intervals"], companies=["Amazon", "Google", "Facebook"],
         description=("Merge all overlapping intervals (given as parallel `starts`/`ends`). Return the merged intervals "
                      "flattened as `s1 e1 s2 e2 …`, sorted by start."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Sort intervals by start.", "Walk through; if the current start ≤ last merged end, extend it.",
                "Otherwise begin a new interval.", "Extend by taking the max of the two ends."],
         opt=("O(n log n)", "O(n)", "Sort by start, then a single merging sweep."),
         editorial="## Approach\nSort by start; keep a running interval, extending its end while the next start overlaps, else emit and restart.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}], "returns": "int[]"},
         fn=lambda starts, ends: _iv_merge(starts, ends),
         cases=[("example", "Overlaps", ([1, 2, 8, 15], [3, 6, 10, 18])), ("example", "Touching", ([1, 4], [4, 5])),
                ("hidden", "Single", ([5], [7])), ("hidden", "Nested", ([1, 2, 3], [10, 4, 5])), ("hidden", "Disjoint", ([1, 5], [2, 6]))],
         example_expl=["[1,3]&[2,6]→[1,6]; [8,10]; [15,18].", "[1,4]&[4,5]→[1,5]."]),
    dict(slug="insert-interval", title="Insert Interval", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Intervals"], companies=["Google", "Amazon"],
         description=("Given sorted, non-overlapping intervals (`starts`/`ends`) and a new interval `[ns, ne]`, insert it and "
                      "merge as needed. Return the result flattened."),
         constraints="0 ≤ n ≤ 10^4\nExisting intervals are sorted and disjoint.",
         hints=["Add the intervals ending before the new one starts unchanged.",
                "Merge everything overlapping the new interval into it.",
                "Then add the remaining intervals.", "Or just insert and re-run a merge."],
         opt=("O(n)", "O(n)", "Single pass in three phases (before / merge / after)."),
         editorial="## Approach\nEmit intervals strictly before the new one, absorb all overlaps into it, then emit the rest.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}, {"name": "ns", "type": "int"}, {"name": "ne", "type": "int"}], "returns": "int[]"},
         fn=lambda starts, ends, ns, ne: _iv_insert(starts, ends, ns, ne),
         cases=[("example", "Merge middle", ([1, 3, 6, 8], [2, 5, 7, 10], 4, 9)), ("example", "Into empty", ([], [], 2, 5)),
                ("hidden", "At front", ([3, 6], [5, 9], 1, 2)), ("hidden", "At end", ([1, 3], [2, 5], 6, 8)), ("hidden", "Absorb all", ([2, 5], [3, 7], 1, 10))],
         example_expl=["[4,9] merges [3,5],[6,7],[8,10] → [1,2] [3,10].", "Just [2,5]."]),
    dict(slug="min-meeting-rooms", title="Meeting Rooms II", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Intervals", "Sweep Line"], companies=["Amazon", "Google", "Facebook"],
         description=("Given meeting `starts`/`ends`, return the **minimum number of rooms** needed so no two concurrent "
                      "meetings share a room."),
         constraints="0 ≤ n ≤ 10^4.",
         hints=["The answer is the maximum number of meetings active at once.",
                "Sort start times and end times separately.", "Sweep: a start needs a room, an end frees one.",
                "Track the running count and its maximum."],
         opt=("O(n log n)", "O(n)", "Sort starts/ends, sweep with two pointers tracking concurrency."),
         editorial="## Approach\nSort starts and ends; advance a start pointer (need a room) or an end pointer (free one); the peak concurrency is the answer.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}], "returns": "int"},
         fn=lambda starts, ends: _iv_min_rooms(starts, ends),
         cases=[("example", "Overlap 2", ([0, 5, 15], [30, 10, 20])), ("example", "No overlap", ([1, 5], [4, 8])),
                ("hidden", "All overlap", ([1, 2, 3], [10, 10, 10])), ("hidden", "Single", ([1], [2])), ("hidden", "Chain", ([1, 3, 5], [4, 6, 8]))],
         example_expl=["[0,30] overlaps both others → 2 rooms.", "Sequential meetings → 1 room."]),
    dict(slug="non-overlapping-remove", title="Non-overlapping Intervals", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Greedy", "Intervals"], companies=["Amazon", "Bloomberg"],
         description=("Given intervals (`starts`/`ends`), return the **minimum number to remove** so the rest are "
                      "non-overlapping."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Greedy: keep as many as possible by always taking the interval that ends earliest.",
                "Sort by end time.", "Keep an interval only if it starts at or after the last kept end.",
                "Removed = total − kept."],
         opt=("O(n log n)", "O(1)", "Greedy by earliest end maximizes the kept set."),
         editorial="## Approach\nSort by end; greedily keep intervals that don't overlap the last kept one; removals are the rest.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}], "returns": "int"},
         fn=lambda starts, ends: _iv_non_overlap(starts, ends),
         cases=[("example", "One overlap", ([1, 2, 3, 1], [2, 3, 4, 3])), ("example", "None", ([1, 3], [2, 4])),
                ("hidden", "All same", ([1, 1, 1], [2, 2, 2])), ("hidden", "Single", ([1], [2])), ("hidden", "Chain", ([1, 2, 3], [2, 3, 4]))],
         example_expl=["Remove [1,3] to make the rest disjoint → 1.", "Already disjoint → 0."]),
    dict(slug="min-arrows-balloons", title="Minimum Arrows to Burst Balloons", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Greedy", "Intervals"], companies=["Amazon"],
         description=("Balloons span `[start, end]` on a wall (parallel arrays). An arrow at position x bursts every balloon "
                      "with start ≤ x ≤ end. Return the **minimum arrows** to burst them all."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Sort balloons by end coordinate.", "Shoot an arrow at the end of the first un-burst balloon.",
                "That arrow also bursts every later balloon starting before it.", "Count a new arrow whenever a balloon starts past the last arrow."],
         opt=("O(n log n)", "O(1)", "Greedy: one arrow per group of overlapping balloons, chosen at the earliest end."),
         editorial="## Approach\nSort by end; place an arrow at each new balloon's end that isn't already covered.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}], "returns": "int"},
         fn=lambda starts, ends: _iv_arrows(starts, ends),
         cases=[("example", "Two groups", ([10, 1, 3, 5], [16, 6, 6, 10])), ("example", "All overlap", ([1, 2, 3], [10, 10, 10])),
                ("hidden", "Disjoint", ([1, 4, 7], [2, 5, 8])), ("hidden", "Single", ([5], [9])), ("hidden", "Touching", ([1, 2], [2, 3]))],
         example_expl=["Arrows at 6 and 12 (or so) → 2.", "One arrow bursts all three → 1."]),
    dict(slug="interval-intersections", title="Interval List Intersections", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Two Pointers", "Intervals"], companies=["Facebook", "Google"],
         description=("Two lists of sorted, disjoint intervals are given as `aStarts/aEnds` and `bStarts/bEnds`. Return their "
                      "pairwise **intersections**, flattened `s1 e1 s2 e2 …`."),
         constraints="0 ≤ each list length ≤ 10^4.",
         hints=["Use two pointers, one per list.", "The overlap of two intervals is [max(starts), min(ends)].",
                "It's valid only if max(starts) ≤ min(ends).", "Advance the interval that ends first."],
         opt=("O(m+n)", "O(1)", "Merge-style two-pointer sweep over both lists."),
         editorial="## Approach\nAt each step intersect the two current intervals; emit if non-empty; advance whichever ends first.",
         spec={"name": "solve", "params": [{"name": "aStarts", "type": "int[]"}, {"name": "aEnds", "type": "int[]"}, {"name": "bStarts", "type": "int[]"}, {"name": "bEnds", "type": "int[]"}], "returns": "int[]"},
         fn=lambda a_s, a_e, b_s, b_e: _iv_inter(a_s, a_e, b_s, b_e),
         cases=[("example", "Classic", ([0, 5, 13, 24], [2, 10, 23, 25], [1, 18], [5, 20])), ("example", "Touch", ([1], [5], [5], [8])),
                ("hidden", "No overlap", ([1], [2], [3], [4])), ("hidden", "Contained", ([1], [10], [3], [5])), ("hidden", "Multiple", ([1, 6], [4, 9], [2, 7], [5, 10]))],
         example_expl=["Intersections [1,2] [5,5] [13,20] [24,23→none]…", "Touch at 5 → [5,5]."]),
    dict(slug="car-pooling", title="Car Pooling", difficulty="Medium",
         topics=["Searching & Sorting"], subtopics=["Sweep Line", "Intervals"], companies=["Amazon"],
         description=("A car of capacity `cap` drives east. Trips are parallel arrays `from`, `to`, `num` (passengers picked "
                      "up at `from`, dropped at `to`). Return `true` if the car never exceeds capacity."),
         constraints="1 ≤ trips ≤ 10^4\n0 ≤ from < to.",
         hints=["Turn each trip into +num at `from` and −num at `to` (a difference array).",
                "Process locations in increasing order.", "Keep a running passenger count.",
                "Fail the moment it exceeds capacity."],
         opt=("O(n log n)", "O(n)", "Difference-array sweep over pickup/dropoff points."),
         editorial="## Approach\nAdd num at each pickup and subtract at each dropoff; sweep positions left to right; if the running load ever exceeds cap, return false.",
         spec={"name": "solve", "params": [{"name": "from", "type": "int[]"}, {"name": "to", "type": "int[]"}, {"name": "num", "type": "int[]"}, {"name": "cap", "type": "int"}], "returns": "bool"},
         fn=lambda frm, to, num, cap: _iv_carpool(frm, to, num, cap),
         cases=[("example", "Overflows", ([1, 3], [5, 7], [3, 4], 5)), ("example", "Fits", ([2, 4], [5, 6], [3, 3], 6)),
                ("hidden", "Exact", ([0], [1], [5], 5)), ("hidden", "Sequential", ([1, 5], [5, 9], [4, 4], 4)), ("hidden", "Over", ([0], [2], [4], 3))],
         example_expl=["3+4 overlap on [3,5] exceeds 5 → false.", "Peaks at 6 ≤ 6 → true."]),
    dict(slug="employee-free-time", title="Employee Free Time", difficulty="Hard",
         topics=["Searching & Sorting"], subtopics=["Intervals", "Sweep Line"], companies=["Google", "Facebook"],
         description=("Given everyone's busy intervals pooled together (`starts`/`ends`), return the **common free gaps** "
                      "between the merged busy periods, flattened. (Free time before the first or after the last busy period is not reported.)"),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Merge all busy intervals first.", "The gaps between consecutive merged intervals are free time.",
                "A gap exists only when one interval ends before the next begins.", "Ignore the unbounded time before/after."],
         opt=("O(n log n)", "O(n)", "Merge intervals, then read the gaps between them."),
         editorial="## Approach\nMerge all busy intervals; each gap [prev.end, next.start] between consecutive merged intervals is free time.",
         spec={"name": "solve", "params": [{"name": "starts", "type": "int[]"}, {"name": "ends", "type": "int[]"}], "returns": "int[]"},
         fn=lambda starts, ends: _iv_free(starts, ends),
         cases=[("example", "One gap", ([1, 5, 6], [3, 6, 8]), ), ("example", "Two gaps", ([1, 9, 15], [4, 12, 20])),
                ("hidden", "No gap", ([1, 2], [3, 4]), ), ("hidden", "Fully overlapping", ([1, 2], [10, 3])), ("hidden", "Three", ([1, 4, 7], [2, 5, 8]))],
         example_expl=["Busy [1,3][5,8] → free [3,5].", "Free [4,9] and [12,15]."]),
]

CONCEPTS.update({
    "intervals": {
        "name": "Interval Scheduling",
        "what": "Reasoning about ranges [start, end] by sorting on the right endpoint and testing overlap with a[end] ≥ b[start].",
        "deep": "Interval problems fall into two moves: sort by START to merge or scan overlaps, or sort by END for greedy 'keep the most / fewest' results (activity selection, arrows, non-overlapping). A sweep line — process all endpoints in order, +1 on a start and −1 on an end — answers 'maximum concurrent' questions like minimum meeting rooms.",
        "java": "int[][] iv; Arrays.sort(iv, (a,b) -> a[0]-b[0]); // by start, or a[1]-b[1] for greedy by end. Overlap: a[1] >= b[0] (or > for point-touching rules).",
    },
})
CATEGORY.update({"intervals": "Searching & Sorting"})
PATTERN_FROM.update({"Intervals": "Intervals", "Sweep Line": "Intervals"})

LESSONS.update({
    "intervals": (
        "# Interval Scheduling\n\n"
        "Two sorts unlock almost every interval problem:\n\n"
        "- **Sort by start** → merge overlaps, scan for conflicts.\n"
        "- **Sort by end** → greedy 'keep the most non-overlapping' (activity selection, arrows, remove-to-disjoint).\n\n"
        "```java\n"
        "int[][] iv = /* pair up starts[i], ends[i] */;\n"
        "Arrays.sort(iv, (a, b) -> a[0] - b[0]);        // by start\n"
        "List<int[]> merged = new ArrayList<>();\n"
        "for (int[] cur : iv) {\n"
        "    if (!merged.isEmpty() && cur[0] <= merged.get(merged.size()-1)[1])\n"
        "        merged.get(merged.size()-1)[1] = Math.max(merged.get(merged.size()-1)[1], cur[1]);\n"
        "    else merged.add(cur);\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "| Signal | Sort by | Move |\n"
        "|---|---|---|\n"
        "| 'merge', 'can attend all' | start | extend / conflict-check |\n"
        "| 'max non-overlapping', 'fewest arrows' | end | greedy keep |\n"
        "| 'minimum rooms', 'max concurrent' | endpoints | sweep +1/−1 |\n\n"
        "## Simulated solve — merge `[1,3] [2,6] [8,10]`\n"
        "| interval | merged so far |\n"
        "|---|---|\n"
        "| [1,3] | [1,3] |\n"
        "| [2,6] | [1,6] (2 ≤ 3, extend) |\n"
        "| [8,10] | [1,6] [8,10] (8 > 6, new) |\n"
    ),
})

_EX_IV_HEAD = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt();\n"
    "        int[][] iv = new int[n][2];\n"
    "        for (int i = 0; i < n; i++) { iv[i][0] = sc.nextInt(); iv[i][1] = sc.nextInt(); }\n"
    "        Arrays.sort(iv, (a, b) -> a[0] - b[0]);\n"
)
_EX_IV_ATTEND = _EX_IV_HEAD + (
    "        boolean ok = true;\n"
    "        for (int i = 1; i < n; i++)\n"
    "            if (iv[i][0] < iv[i - 1][1]) ok = false;\n"
    "        System.out.println(ok ? \"true\" : \"false\");\n"
    "    }\n}\n"
)
_EX_IV_MERGE = _EX_IV_HEAD + (
    "        List<int[]> merged = new ArrayList<>();\n"
    "        for (int[] cur : iv) {\n"
    "            if (!merged.isEmpty() && cur[0] <= merged.get(merged.size() - 1)[1])\n"
    "                merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], cur[1]);\n"
    "            else merged.add(new int[]{cur[0], cur[1]});\n"
    "        }\n"
    "        StringBuilder sb = new StringBuilder();\n"
    "        for (int[] m : merged) { if (sb.length() > 0) sb.append(' '); sb.append(m[0]).append(' ').append(m[1]); }\n"
    "        System.out.println(sb.toString());\n"
    "    }\n}\n"
)
EXERCISES.update({
    "intervals": [
        ex("intervals-overlap", "The overlap test",
           "Meetings are sorted by start. Fill the blank so overlap is detected when a meeting starts before the previous one ends.",
           _EX_IV_ATTEND, ["if (iv[i][0] < iv[i - 1][1]) ok = false;"],
           [("3\n0 30 5 10 15 20", "false"), ("2\n7 10 2 4", "true"), ("2\n1 2 2 3", "true")],
           hint="Overlap: current start is before the previous end.", source_slug="can-attend-meetings"),
        ex("intervals-extend", "Extend the merged interval",
           "Merging sorted intervals. Fill the blank so an overlapping interval extends the current one to the farther end.",
           _EX_IV_MERGE, ["merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], cur[1]);"],
           [("4\n1 3 2 6 8 10 15 18", "1 6 8 10 15 18"), ("2\n1 4 4 5", "1 5"), ("1\n5 7", "5 7")],
           hint="Take the max of the two ends so the merged interval covers both.", source_slug="merge-intervals"),
        ex("intervals-sort", "Sort by start",
           "Fill the blank with the comparator that orders intervals by ascending start time.",
           _EX_IV_MERGE, ["(a, b) -> a[0] - b[0]"],
           [("3\n8 10 1 3 2 6", "1 6 8 10"), ("2\n5 6 1 2", "1 2 5 6"), ("1\n1 9", "1 9")],
           hint="Compare the start fields a[0] and b[0].", source_slug="merge-intervals"),
    ],
})

PREREQS.update({
    "can-attend-meetings": [("intervals", "Sort by start, check adjacent overlap."), ("sorting", "Order the meetings.")],
    "merge-intervals": [("intervals", "Sort by start, extend overlaps.")],
    "insert-interval": [("intervals", "Three-phase merge around the new interval.")],
    "min-meeting-rooms": [("intervals", "Sweep endpoints for max concurrency."), ("sorting", "Sort starts and ends.")],
    "non-overlapping-remove": [("intervals", "Greedy by earliest end."), ("greedy", "Keep the most compatible.")],
    "min-arrows-balloons": [("intervals", "One arrow per overlap group by end."), ("greedy", "Shoot at earliest end.")],
    "interval-intersections": [("intervals", "Overlap = [max start, min end]."), ("two_pointers", "Advance the earlier end.")],
    "car-pooling": [("intervals", "Difference array over positions."), ("prefix_sum", "Running load.")],
    "employee-free-time": [("intervals", "Merge busy, read the gaps.")],
})

FLASHCARDS += [
    ("Interval problem — sort by start or by end?", "By START to merge/scan overlaps; by END for greedy 'keep the most non-overlapping'.", "seed:intervals"),
    ("Two intervals [a1,b1],[a2,b2] overlap when?", "a1 <= b2 AND a2 <= b1 (use < / > if touching endpoints don't count).", "seed:intervals"),
    ("Minimum meeting rooms / max concurrent intervals?", "Sweep line: sort starts and ends; +1 on a start, -1 on an end; answer is the peak count.", "seed:intervals"),
    ("Fewest arrows / max non-overlapping intervals?", "Greedy: sort by end, take an interval whenever it starts after the last kept end.", "seed:intervals"),
]

EXPANSION_REFS.update({
    "merge-intervals": {
        "java": "import java.util.*;\nclass Solution {\n    int[] solve(int[] starts, int[] ends){ int n=starts.length; int[][] iv=new int[n][2]; for(int i=0;i<n;i++){ iv[i][0]=starts[i]; iv[i][1]=ends[i]; } Arrays.sort(iv,(a,b)->a[0]-b[0]); List<int[]> m=new ArrayList<>(); for(int[] c:iv){ if(!m.isEmpty() && c[0]<=m.get(m.size()-1)[1]) m.get(m.size()-1)[1]=Math.max(m.get(m.size()-1)[1],c[1]); else m.add(new int[]{c[0],c[1]}); } int[] r=new int[m.size()*2]; int i=0; for(int[] x:m){ r[i++]=x[0]; r[i++]=x[1]; } return r; }\n}\n",
        "python": "def solve(starts, ends):\n    m=[]\n    for a,b in sorted(zip(starts,ends)):\n        if m and a<=m[-1][1]: m[-1][1]=max(m[-1][1],b)\n        else: m.append([a,b])\n    out=[]\n    for a,b in m: out+=[a,b]\n    return out\n",
    },
    "min-meeting-rooms": {
        "java": "import java.util.*;\nclass Solution {\n    int solve(int[] starts, int[] ends){ int[] s=starts.clone(), e=ends.clone(); Arrays.sort(s); Arrays.sort(e); int i=0,j=0,cur=0,best=0; while(i<s.length){ if(s[i]<e[j]){ cur++; best=Math.max(best,cur); i++; } else { cur--; j++; } } return best; }\n}\n",
        "python": "def solve(starts, ends):\n    s=sorted(starts); e=sorted(ends); i=j=cur=best=0\n    while i<len(s):\n        if s[i]<e[j]: cur+=1; best=max(best,cur); i+=1\n        else: cur-=1; j+=1\n    return best\n",
    },
    "non-overlapping-remove": {
        "java": "import java.util.*;\nclass Solution {\n    int solve(int[] starts, int[] ends){ int n=starts.length; int[][] iv=new int[n][2]; for(int i=0;i<n;i++){ iv[i][0]=starts[i]; iv[i][1]=ends[i]; } Arrays.sort(iv,(a,b)->a[1]-b[1]); int count=0; long end=Long.MIN_VALUE; for(int[] c:iv){ if(c[0]>=end) end=c[1]; else count++; } return count; }\n}\n",
        "python": "def solve(starts, ends):\n    count=0; end=-(10**18)\n    for a,b in sorted(zip(starts,ends), key=lambda p:p[1]):\n        if a>=end: end=b\n        else: count+=1\n    return count\n",
    },
})

# ===========================================================================
# DOMAIN 6 — DESIGN / DATA STRUCTURES   (operation-stream raw DEFS)
# I/O contract: line 1 = number of operations Q; next Q lines "OP args...";
# print one line per query op (mutating ops print nothing).
# ===========================================================================

def _design_def(slug, title, diff, desc, constraints, hints, opt, editorial,
                ref, cases, example_expl, companies, subtopics, hint_ops):
    j, p, js = _ops_starters(hint_ops)
    JAVA_STARTERS[slug] = j
    return dict(slug=slug, title=title, difficulty=diff, topics=["Design"], subtopics=subtopics,
                companies=companies, description=desc, constraints=constraints, hints=hints,
                opt=opt, editorial=editorial, ref=ref, starter_py=p, starter_js=js,
                cases=cases, example_expl=example_expl)


def _ops(inp):
    L = inp.split('\n')
    q = int(L[0])
    return [L[i].split() for i in range(1, q + 1)]


def _sol_min_stack(inp):
    st = []
    mn = []
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "push":
            x = int(p[1])
            st.append(x)
            mn.append(x if not mn else min(mn[-1], x))
        elif op == "pop":
            st.pop()
            mn.pop()
        elif op == "top":
            out.append(str(st[-1]))
        elif op == "getMin":
            out.append(str(mn[-1]))
    return "\n".join(out)


def _sol_queue_stacks(inp):
    from collections import deque
    q = deque()
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "push":
            q.append(int(p[1]))
        elif op == "pop":
            out.append(str(q.popleft()))
        elif op == "peek":
            out.append(str(q[0]))
        elif op == "empty":
            out.append("true" if not q else "false")
    return "\n".join(out)


def _sol_stack_queues(inp):
    s = []
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "push":
            s.append(int(p[1]))
        elif op == "pop":
            out.append(str(s.pop()))
        elif op == "top":
            out.append(str(s[-1]))
        elif op == "empty":
            out.append("true" if not s else "false")
    return "\n".join(out)


def _sol_hashmap(inp):
    m = {}
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "put":
            m[int(p[1])] = int(p[2])
        elif op == "get":
            out.append(str(m.get(int(p[1]), -1)))
        elif op == "remove":
            m.pop(int(p[1]), None)
    return "\n".join(out)


def _sol_hashset(inp):
    s = set()
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "add":
            s.add(int(p[1]))
        elif op == "contains":
            out.append("true" if int(p[1]) in s else "false")
        elif op == "remove":
            s.discard(int(p[1]))
    return "\n".join(out)


def _sol_circ_queue(inp):
    cap = 0
    buf = []
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "cap":
            cap = int(p[1])
        elif op == "enQueue":
            if len(buf) < cap:
                buf.append(int(p[1]))
                out.append("true")
            else:
                out.append("false")
        elif op == "deQueue":
            if buf:
                buf.pop(0)
                out.append("true")
            else:
                out.append("false")
        elif op == "Front":
            out.append(str(buf[0]) if buf else "-1")
        elif op == "Rear":
            out.append(str(buf[-1]) if buf else "-1")
        elif op == "isEmpty":
            out.append("true" if not buf else "false")
        elif op == "isFull":
            out.append("true" if len(buf) == cap else "false")
    return "\n".join(out)


def _sol_browser(inp):
    hist = []
    cur = 0
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "home":
            hist = [p[1]]
            cur = 0
        elif op == "visit":
            del hist[cur + 1:]
            hist.append(p[1])
            cur = len(hist) - 1
        elif op == "back":
            cur = max(0, cur - int(p[1]))
            out.append(hist[cur])
        elif op == "forward":
            cur = min(len(hist) - 1, cur + int(p[1]))
            out.append(hist[cur])
    return "\n".join(out)


def _sol_lru(inp):
    from collections import OrderedDict
    cap = 0
    od = OrderedDict()
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "cap":
            cap = int(p[1])
        elif op == "put":
            k, v = int(p[1]), int(p[2])
            if k in od:
                od.move_to_end(k)
            od[k] = v
            if len(od) > cap:
                od.popitem(last=False)
        elif op == "get":
            k = int(p[1])
            if k in od:
                od.move_to_end(k)
                out.append(str(od[k]))
            else:
                out.append("-1")
    return "\n".join(out)


def _sol_lfu(inp):
    from collections import defaultdict, OrderedDict
    cap = 0
    val = {}
    freq = {}
    buckets = defaultdict(OrderedDict)
    minf = 0
    out = []

    def touch(k):
        nonlocal minf
        f = freq[k]
        del buckets[f][k]
        if not buckets[f]:
            del buckets[f]
            if minf == f:
                minf += 1
        freq[k] = f + 1
        buckets[f + 1][k] = None

    for p in _ops(inp):
        op = p[0]
        if op == "cap":
            cap = int(p[1])
        elif op == "get":
            k = int(p[1])
            if k in val and cap > 0:
                touch(k)
                out.append(str(val[k]))
            else:
                out.append("-1")
        elif op == "put":
            k, v = int(p[1]), int(p[2])
            if cap == 0:
                continue
            if k in val:
                val[k] = v
                touch(k)
                continue
            if len(val) >= cap:
                ek, _ = buckets[minf].popitem(last=False)
                del val[ek]
                del freq[ek]
            val[k] = v
            freq[k] = 1
            buckets[1][k] = None
            minf = 1
    return "\n".join(out)


def _sol_time_kv(inp):
    from collections import defaultdict
    import bisect
    store = defaultdict(list)
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "set":
            store[p[1]].append((int(p[3]), p[2]))
        elif op == "get":
            arr = store.get(p[1], [])
            ts = int(p[2])
            idx = bisect.bisect_right([t for t, _ in arr], ts) - 1
            out.append(arr[idx][1] if idx >= 0 else "null")
    return "\n".join(out)


def _sol_design_list(inp):
    a = []
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "addAtHead":
            a.insert(0, int(p[1]))
        elif op == "addAtTail":
            a.append(int(p[1]))
        elif op == "addAtIndex":
            i, x = int(p[1]), int(p[2])
            if 0 <= i <= len(a):
                a.insert(i, x)
        elif op == "deleteAtIndex":
            i = int(p[1])
            if 0 <= i < len(a):
                a.pop(i)
        elif op == "get":
            i = int(p[1])
            out.append(str(a[i]) if 0 <= i < len(a) else "-1")
    return "\n".join(out)


def _sol_twitter(inp):
    from collections import defaultdict
    tweets = defaultdict(list)
    follows = defaultdict(set)
    clock = [0]
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "postTweet":
            u, tid = int(p[1]), int(p[2])
            clock[0] += 1
            tweets[u].append((clock[0], tid))
        elif op == "follow":
            follows[int(p[1])].add(int(p[2]))
        elif op == "unfollow":
            follows[int(p[1])].discard(int(p[2]))
        elif op == "getNewsFeed":
            u = int(p[1])
            users = follows[u] | {u}
            cand = []
            for usr in users:
                cand += tweets[usr]
            cand.sort(reverse=True)
            feed = [str(tid) for _, tid in cand[:10]]
            out.append(" ".join(feed) if feed else "empty")
    return "\n".join(out)


def _sol_spanner(inp):
    st = []
    out = []
    for p in _ops(inp):
        if p[0] == "next":
            price = int(p[1])
            span = 1
            while st and st[-1][0] <= price:
                span += st.pop()[1]
            st.append((price, span))
            out.append(str(span))
    return "\n".join(out)


def _sol_hits(inp):
    from collections import deque
    dq = deque()
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "hit":
            dq.append(int(p[1]))
        elif op == "get":
            t = int(p[1])
            while dq and dq[0] <= t - 300:
                dq.popleft()
            out.append(str(len(dq)))
    return "\n".join(out)


DEFS += [
    _design_def("min-stack", "Min Stack", "Medium",
                ("Design a stack that also returns its minimum in O(1).\n\n### Operations\n`push x`, `pop`, "
                 "`top` (print top), `getMin` (print the minimum).\n\n### I/O\nLine 1: number of operations `Q`; "
                 "next `Q` lines: one operation. Print one line per `top`/`getMin`."),
                "1 ≤ Q ≤ 10^5.",
                ["Store the running minimum alongside each pushed value.",
                 "Each stack entry remembers the min of the stack below it.", "pop removes both value and its paired min.",
                 "All four operations are O(1)."],
                ("O(1) per op", "O(n)", "Pair each value with the minimum at that depth."),
                "## Approach\nKeep two stacks (or a stack of pairs): the value and the minimum seen up to that push. getMin reads the top min.",
                _sol_min_stack,
                [("example", "Track min", "6\npush 2\npush 1\ngetMin\npop\ntop\ngetMin"), ("example", "Single", "3\npush 5\ntop\ngetMin"),
                 ("hidden", "Descending", "6\npush 3\npush 2\npush 1\ngetMin\npop\ngetMin"), ("hidden", "Ties", "5\npush 2\npush 2\ngetMin\npop\ngetMin")],
                ["min is 1, then after pop top=2 and min=2.", "top and min are both 5."],
                ["Amazon", "Bloomberg"], ["Stack"], "line1: Q; then push x / pop / top / getMin"),
    _design_def("implement-queue-stacks", "Implement Queue using Stacks", "Easy",
                ("Implement a FIFO queue.\n\n### Operations\n`push x`, `pop` (print removed), `peek` (print front), "
                 "`empty` (print true/false).\n\n### I/O\nLine 1: `Q`; then the operations. One line per query."),
                "1 ≤ Q ≤ 10^4.",
                ["Use two stacks: an 'in' stack and an 'out' stack.",
                 "Push goes to 'in'.", "When 'out' is empty, pour 'in' into it (reversing order).",
                 "Amortized O(1) per operation."],
                ("O(1) amortized", "O(n)", "Two stacks; each element moves between them at most once."),
                "## Approach\nPush to an input stack; for pop/peek, if the output stack is empty transfer everything from input (reversing), then use its top.",
                _sol_queue_stacks,
                [("example", "FIFO", "6\npush 1\npush 2\npeek\npop\npop\nempty"), ("example", "Empty", "2\npush 9\nempty"),
                 ("hidden", "Interleaved", "6\npush 1\npop\npush 2\npush 3\npop\npeek"), ("hidden", "Single", "2\npush 7\npop")],
                ["Front is 1; pops give 1 then 2; then empty=true.", "Not empty → false."],
                ["Microsoft", "Amazon"], ["Stack", "Queue"], "line1: Q; then push x / pop / peek / empty"),
    _design_def("implement-stack-queues", "Implement Stack using Queues", "Easy",
                ("Implement a LIFO stack.\n\n### Operations\n`push x`, `pop` (print removed), `top` (print top), "
                 "`empty` (print true/false).\n\n### I/O\nLine 1: `Q`; then operations. One line per query."),
                "1 ≤ Q ≤ 10^4.",
                ["A single queue can behave like a stack.", "After pushing, rotate the queue so the new element is at the front.",
                 "Then pop/top act on the front.", "Push becomes O(n), the rest O(1)."],
                ("O(n) push", "O(n)", "Rotate the queue on push so the newest is at the front."),
                "## Approach\nOn push, enqueue then rotate the earlier elements behind it so the front is always the newest.",
                _sol_stack_queues,
                [("example", "LIFO", "6\npush 1\npush 2\ntop\npop\npop\nempty"), ("example", "Empty", "2\npush 3\nempty"),
                 ("hidden", "Mixed", "6\npush 1\npush 2\npush 3\npop\ntop\npop"), ("hidden", "Single", "2\npush 8\ntop")],
                ["Top is 2; pops give 2 then 1; empty=true.", "Not empty → false."],
                ["Amazon"], ["Stack", "Queue"], "line1: Q; then push x / pop / top / empty"),
    _design_def("design-hashmap", "Design HashMap", "Easy",
                ("Design a key→value map without a built-in one.\n\n### Operations\n`put k v`, `get k` (print value or -1), "
                 "`remove k`.\n\n### I/O\nLine 1: `Q`; then operations. One line per `get`."),
                "0 ≤ k, v ≤ 10^6.",
                ["Use an array of buckets indexed by a hash of the key.",
                 "Each bucket is a list of (key, value) pairs (chaining).", "get scans the bucket for the key.",
                 "remove deletes the matching pair."],
                ("O(1) average", "O(n)", "Bucket array with chaining on collisions."),
                "## Approach\nHash the key into a bucket; store/find/remove (key,value) pairs within the bucket's list.",
                _sol_hashmap,
                [("example", "Basic", "5\nput 1 10\nput 2 20\nget 1\nremove 1\nget 1"), ("example", "Miss", "2\nput 5 50\nget 9"),
                 ("hidden", "Overwrite", "4\nput 3 1\nput 3 2\nget 3\nget 4"), ("hidden", "Remove missing", "3\nremove 1\nput 1 7\nget 1")],
                ["get 1 → 10, then removed → -1.", "Absent key → -1."],
                ["Amazon"], ["Hashing"], "line1: Q; then put k v / get k / remove k"),
    _design_def("design-hashset", "Design HashSet", "Easy",
                ("Design a set of integers.\n\n### Operations\n`add x`, `contains x` (print true/false), `remove x`.\n\n"
                 "### I/O\nLine 1: `Q`; then operations. One line per `contains`."),
                "0 ≤ x ≤ 10^6.",
                ["Buckets indexed by a hash of the value.", "add inserts if absent; contains scans the bucket.",
                 "remove deletes from the bucket.", "A boolean array works if the range is small."],
                ("O(1) average", "O(n)", "Bucketed membership with chaining."),
                "## Approach\nHash into buckets; add/contains/remove operate on the bucket's list.",
                _sol_hashset,
                [("example", "Basic", "5\nadd 1\nadd 2\ncontains 1\nremove 2\ncontains 2"), ("example", "Miss", "2\nadd 5\ncontains 9"),
                 ("hidden", "Dup add", "4\nadd 3\nadd 3\ncontains 3\nremove 3"), ("hidden", "Remove missing", "3\nremove 1\nadd 1\ncontains 1")],
                ["Contains 1 → true; after removing 2 → false.", "Absent → false."],
                ["Amazon"], ["Hashing"], "line1: Q; then add x / contains x / remove x"),
    _design_def("design-circular-queue", "Design Circular Queue", "Medium",
                ("A ring buffer of fixed capacity.\n\n### Operations\nFirst op `cap c` sets capacity, then `enQueue x` "
                 "(print true/false), `deQueue` (print true/false), `Front` (value or -1), `Rear` (value or -1), "
                 "`isEmpty`, `isFull` (true/false).\n\n### I/O\nLine 1: `Q`; then operations. One line per query."),
                "1 ≤ c ≤ 1000.",
                ["Store elements in a fixed array with head and tail indices modulo capacity.",
                 "Track the current size to distinguish empty from full.", "Wrap indices with % capacity.",
                 "enQueue/deQueue fail when full/empty."],
                ("O(1) per op", "O(c)", "Modular head/tail indices over a fixed buffer."),
                "## Approach\nArray + head + size; enqueue at (head+size)%cap, dequeue advances head; front/rear read the ends.",
                _sol_circ_queue,
                [("example", "Wrap", "8\ncap 3\nenQueue 1\nenQueue 2\nenQueue 3\nenQueue 4\nRear\ndeQueue\nenQueue 4"),
                 ("example", "Empty", "3\ncap 2\nFront\nisEmpty"),
                 ("hidden", "Full", "5\ncap 2\nenQueue 1\nenQueue 2\nisFull\nenQueue 3"),
                 ("hidden", "Cycle", "6\ncap 2\nenQueue 5\ndeQueue\nenQueue 6\nFront\nRear")],
                ["4th enQueue fails; Rear=3; then space frees.", "Empty → Front -1, isEmpty true."],
                ["Amazon"], ["Queue"], "line1: Q; first op 'cap c'; then enQueue/deQueue/Front/Rear/isEmpty/isFull"),
    _design_def("browser-history", "Design Browser History", "Medium",
                ("Model back/forward navigation.\n\n### Operations\nFirst op `home url` sets the start page, then "
                 "`visit url` (clears forward history), `back k` (go back up to k, print the current url), `forward k` "
                 "(go forward up to k, print the current url). URLs are single tokens.\n\n### I/O\nLine 1: `Q`; then operations."),
                "1 ≤ Q ≤ 10^4.",
                ["Keep a list of pages and an index of the current one.", "visit truncates everything after the current page.",
                 "back/forward move the index, clamped to the ends.", "A dynamic array beats a doubly-linked list here."],
                ("O(1) amortized", "O(n)", "Array of history with a current pointer."),
                "## Approach\nList + current index. visit drops the forward tail and appends; back/forward clamp the index to [0, size-1].",
                _sol_browser,
                [("example", "Navigate", "6\nhome A\nvisit B\nvisit C\nback 1\nback 1\nforward 1"),
                 ("example", "Overshoot", "4\nhome X\nvisit Y\nback 5\nforward 5"),
                 ("hidden", "Visit clears forward", "6\nhome A\nvisit B\nback 1\nvisit C\nforward 1\nback 1"),
                 ("hidden", "Stay", "3\nhome P\nback 1\nforward 1")],
                ["back to B, back to A, forward to B.", "Clamps to X then Y."],
                ["Amazon", "Google"], ["Design"], "line1: Q; first op 'home url'; then visit url / back k / forward k"),
    _design_def("lru-cache", "LRU Cache", "Medium",
                ("A fixed-capacity cache evicting the **least recently used** entry.\n\n### Operations\nFirst op `cap c`, "
                 "then `put k v` and `get k` (print value or -1). Any get or put counts as a use.\n\n### I/O\nLine 1: `Q`; "
                 "then operations. One line per `get`."),
                "1 ≤ c ≤ 3000.",
                ["Need O(1) lookup and O(1) recency updates.", "Combine a hash map with a doubly-linked list.",
                 "On access, move the node to the front (most recent).", "Evict from the back when over capacity."],
                ("O(1) per op", "O(c)", "Hash map to nodes + doubly-linked list for recency order."),
                "## Approach\nHashMap<key,node> + doubly-linked list ordered by recency; touch moves a node to the front, eviction removes the tail.",
                _sol_lru,
                [("example", "Evict", "8\ncap 2\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nput 4 4\nget 1"),
                 ("example", "Update", "5\ncap 2\nput 1 1\nput 1 10\nget 1\nget 2"),
                 ("hidden", "Cap 1", "6\ncap 1\nput 1 1\nput 2 2\nget 1\nget 2\nput 2 5"),
                 ("hidden", "Reuse keeps", "7\ncap 2\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 1\nget 2")],
                ["get1=1; adding 3 evicts 2 (get2=-1); adding 4 evicts 3? no, evicts 1 → get1=-1.", "Update in place → get1=10, get2=-1."],
                ["Amazon", "Facebook", "Google"], ["Design", "Hashing"], "line1: Q; first op 'cap c'; then put k v / get k"),
    _design_def("lfu-cache", "LFU Cache", "Hard",
                ("A fixed-capacity cache evicting the **least frequently used** entry (ties broken by least recently "
                 "used).\n\n### Operations\nFirst op `cap c`, then `put k v` and `get k` (print value or -1).\n\n"
                 "### I/O\nLine 1: `Q`; then operations. One line per `get`."),
                "0 ≤ c ≤ 10^4.",
                ["Track a use-frequency per key.", "Group keys by frequency; within a group keep recency order.",
                 "Maintain the current minimum frequency for O(1) eviction.", "Every get/put bumps the key's frequency."],
                ("O(1) per op", "O(c)", "Frequency buckets, each an ordered map by recency; a min-frequency pointer."),
                "## Approach\nMaps key→value and key→freq, plus freq→ordered keys. On use, move the key up a frequency bucket; evict from the min-frequency bucket's oldest entry.",
                _sol_lfu,
                [("example", "Evict LFU", "10\ncap 2\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2\nget 3\nput 4 4\nget 1\nget 3"),
                 ("example", "Update", "5\ncap 2\nput 1 1\nput 1 5\nget 1\nget 2"),
                 ("hidden", "Cap 0", "3\ncap 0\nput 1 1\nget 1"),
                 ("hidden", "Tie by recency", "8\ncap 2\nput 1 1\nput 2 2\nget 1\nget 2\nput 3 3\nget 1\nget 3")],
                ["get2=-1 (evicted as LFU); later get1=-1, get3=3.", "Update keeps → get1=5, get2=-1."],
                ["Amazon", "Google"], ["Design", "Hashing"], "line1: Q; first op 'cap c'; then put k v / get k"),
    _design_def("time-based-kv", "Time Based Key-Value Store", "Medium",
                ("Store values under a key stamped with a time, and query the latest value at or before a time.\n\n"
                 "### Operations\n`set key value timestamp` (timestamps increase per key), `get key timestamp` (print the "
                 "value with the largest stamp ≤ timestamp, or `null`). Keys/values are single tokens.\n\n### I/O\nLine 1: `Q`; then operations."),
                "1 ≤ Q ≤ 10^5.",
                ["Store, per key, a list of (timestamp, value) in increasing time.",
                 "get does a binary search for the rightmost timestamp ≤ query.",
                 "If none is ≤ query, return null.", "Appends keep the list sorted since stamps increase."],
                ("O(log n) per get", "O(n)", "Per-key sorted list + binary search."),
                "## Approach\nAppend (ts, value) per key; on get, binary search for the greatest ts ≤ query.",
                _sol_time_kv,
                [("example", "Lookup", "5\nset foo bar 1\nget foo 1\nget foo 3\nset foo baz 4\nget foo 4"),
                 ("example", "Before", "2\nset a x 5\nget a 1"),
                 ("hidden", "Missing key", "2\nset a x 1\nget b 1"),
                 ("hidden", "Latest", "4\nset k v1 1\nset k v2 2\nget k 5\nget k 2")],
                ["bar at t1 and t3; baz at t4.", "Query before any set → null."],
                ["Amazon", "Google"], ["Binary Search", "Hashing"], "line1: Q; then set key value ts / get key ts"),
    _design_def("design-linked-list", "Design Linked List", "Medium",
                ("Implement a singly linked list by index.\n\n### Operations\n`addAtHead x`, `addAtTail x`, "
                 "`addAtIndex i x` (insert before index i; if i==size append; ignore if i>size), `deleteAtIndex i` "
                 "(ignore if invalid), `get i` (print the value or -1).\n\n### I/O\nLine 1: `Q`; then operations. One line per `get`."),
                "0 ≤ Q ≤ 10^4.",
                ["Track the head and the size.", "addAtIndex walks i steps and splices in a node.",
                 "Guard indices: get/delete return/ignore when out of range.", "A dummy head simplifies index 0."],
                ("O(index) per op", "O(n)", "Standard singly-linked-list index operations."),
                "## Approach\nMaintain head + size; walk to the position for index ops; validate bounds on get/delete.",
                _sol_design_list,
                [("example", "Build", "6\naddAtHead 1\naddAtTail 3\naddAtIndex 1 2\nget 1\ndeleteAtIndex 1\nget 1"),
                 ("example", "Bounds", "3\naddAtHead 5\nget 3\nget 0"),
                 ("hidden", "Empty get", "2\nget 0\naddAtTail 9"),
                 ("hidden", "Delete head", "5\naddAtHead 1\naddAtHead 2\ndeleteAtIndex 0\nget 0\nget 1")],
                ["List 1,2,3 → get1=2; after delete → get1=3.", "Out of range → -1, then 5."],
                ["Amazon"], ["Design"], "line1: Q; then addAtHead x / addAtTail x / addAtIndex i x / deleteAtIndex i / get i"),
    _design_def("design-twitter", "Design Twitter", "Medium",
                ("A tiny social feed.\n\n### Operations\n`postTweet userId tweetId`, `follow a b`, `unfollow a b`, "
                 "`getNewsFeed userId` (print the up to 10 most recent tweet ids from the user and everyone they follow, "
                 "most recent first, space-separated; print `empty` if none).\n\n### I/O\nLine 1: `Q`; then operations."),
                "1 ≤ Q ≤ 10^4.",
                ["Stamp each tweet with a global increasing time.", "A feed merges the user's own and followees' tweets.",
                 "Take the 10 most recent by timestamp.", "A heap merges the timelines efficiently."],
                ("O(follows + tweets log) per feed", "O(n)", "Timestamped tweets merged newest-first (heap or sort)."),
                "## Approach\nStore tweets per user with a global clock; getNewsFeed gathers the user + followees and returns the 10 latest by time.",
                _sol_twitter,
                [("example", "Feed", "5\npostTweet 1 5\ngetNewsFeed 1\nfollow 1 2\npostTweet 2 6\ngetNewsFeed 1"),
                 ("example", "Unfollow", "6\npostTweet 1 5\nfollow 1 2\npostTweet 2 6\nunfollow 1 2\ngetNewsFeed 1\ngetNewsFeed 2"),
                 ("hidden", "Empty", "1\ngetNewsFeed 9"),
                 ("hidden", "Own only", "3\npostTweet 3 1\npostTweet 3 2\ngetNewsFeed 3")],
                ["Feed shows 5, then 6 5 after following 2.", "After unfollow, user 1 sees only 5."],
                ["Amazon", "Twitter"], ["Design", "Priority Queue"], "line1: Q; then postTweet u t / follow a b / unfollow a b / getNewsFeed u"),
    _design_def("stock-spanner", "Online Stock Span", "Medium",
                ("Stream daily stock prices; report each day's **span**: the number of consecutive days up to today whose "
                 "price was ≤ today's.\n\n### Operations\n`next price` (print the span for that day).\n\n### I/O\nLine 1: `Q`; "
                 "then operations, one per line."),
                "1 ≤ Q ≤ 10^4.",
                ["Use a monotonic decreasing stack of (price, span).", "Pop while the top price ≤ today's, accumulating spans.",
                 "Push today's price with the accumulated span.", "Amortized O(1) per day."],
                ("O(1) amortized", "O(n)", "Monotonic stack collapsing spans of cheaper days."),
                "## Approach\nStack of (price, span); on each price, pop all entries ≤ it summing their spans, then push (price, 1+summed).",
                _sol_spanner,
                [("example", "Classic", "7\nnext 100\nnext 80\nnext 60\nnext 70\nnext 60\nnext 75\nnext 85"),
                 ("example", "Rising", "3\nnext 1\nnext 2\nnext 3"),
                 ("hidden", "Falling", "3\nnext 5\nnext 4\nnext 3"),
                 ("hidden", "Equal", "3\nnext 5\nnext 5\nnext 5")],
                ["Spans 1 1 1 2 1 4 6.", "Each higher day extends: 1 2 3."],
                ["Amazon"], ["Stack"], "line1: Q; then next price"),
    _design_def("hit-counter", "Design Hit Counter", "Medium",
                ("Count hits within the trailing 300-second window.\n\n### Operations\n`hit t` (record a hit at time t), "
                 "`get t` (print the number of hits in the interval (t-300, t]). Times are non-decreasing.\n\n### I/O\n"
                 "Line 1: `Q`; then operations."),
                "1 ≤ Q ≤ 10^4.",
                ["Keep hit timestamps in a queue.", "On a query, drop timestamps older than t-300 from the front.",
                 "The remaining count is the answer.", "Because times are non-decreasing, old hits only leave from the front."],
                ("O(1) amortized", "O(w)", "Sliding-window queue of recent timestamps."),
                "## Approach\nQueue of timestamps; each query evicts entries ≤ t-300 from the front, then returns the queue size.",
                _sol_hits,
                [("example", "Window", "6\nhit 1\nhit 2\nhit 300\nget 300\nget 301\nget 302"),
                 ("example", "Expire", "4\nhit 1\nget 300\nget 301\nget 400"),
                 ("hidden", "Burst", "5\nhit 5\nhit 5\nhit 5\nget 5\nget 306"),
                 ("hidden", "None", "1\nget 100")],
                ["3 hits within 300; at 301 the first expires → 2; at 302 → 1.", "1 within window, then 0."],
                ["Dropbox", "Amazon"], ["Queue", "Sliding Window"], "line1: Q; then hit t / get t"),
]

CONCEPTS.update({
    "design_ds": {
        "name": "Design / Data-Structure Problems",
        "what": "Building a class with a required set of operations by choosing structures whose costs match the operation profile.",
        "deep": "'Design X' problems test whether you can pick the right combination of primitives: a hash map for O(1) lookup, a doubly-linked list for O(1) reordering (LRU), two stacks for a queue, a monotonic stack for spans, a heap for top-k feeds. The skill is mapping each required operation to a data structure that makes it cheap, and reasoning about amortized cost when one operation occasionally does more work.",
        "java": "Compose java.util building blocks: HashMap, ArrayDeque (stack/queue), LinkedHashMap (LRU-ish), PriorityQueue, and a hand-rolled doubly-linked list when you need O(1) node moves.",
    },
})
CATEGORY.update({"design_ds": "Data Structures"})
PATTERN_FROM.update({"Design": "Design"})

LESSONS.update({
    "design_ds": (
        "# Design / Data-Structure Problems\n\n"
        "A 'design' problem hands you a list of operations and asks for a class where each is fast. The whole game is **matching each operation to a structure that makes it cheap**.\n\n"
        "| Requirement | Reach for |\n"
        "|---|---|\n"
        "| O(1) key lookup | HashMap |\n"
        "| O(1) move-to-front / reorder | doubly-linked list |\n"
        "| FIFO from LIFO | two stacks (amortized O(1)) |\n"
        "| 'span' / 'next greater' | monotonic stack |\n"
        "| 'k most recent / frequent' | heap or freq buckets |\n"
        "| min alongside a stack | pair each value with the running min |\n\n"
        "## The classic: LRU cache\n"
        "```java\n"
        "// HashMap<key,node> for O(1) find + doubly-linked list for O(1) recency\n"
        "void get(int k){ if(map.has(k)){ moveToFront(node); return node.val; } return -1; }\n"
        "void put(int k,int v){ upsert; moveToFront(node); if(size>cap) removeTail(); }\n"
        "```\n\n"
        "## The I/O contract used here\n"
        "Every design problem is driven by an **operation stream**: line 1 is the count `Q`, then one operation per line; your program prints a line only for the *query* operations. Parse the op name, dispatch, and buffer the outputs."
    ),
})

_EX_DS_MINSTACK = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int q = sc.nextInt();\n"
    "        Deque<int[]> st = new ArrayDeque<>();\n"
    "        StringBuilder sb = new StringBuilder();\n"
    "        for (int i = 0; i < q; i++) {\n"
    "            String op = sc.next();\n"
    "            if (op.equals(\"push\")) {\n"
    "                int x = sc.nextInt();\n"
    "                int mn = st.isEmpty() ? x : Math.min(st.peek()[1], x);\n"
    "                st.push(new int[]{x, mn});\n"
    "            } else if (op.equals(\"pop\")) {\n"
    "                st.pop();\n"
    "            } else if (op.equals(\"top\")) {\n"
    "                sb.append(st.peek()[0]).append('\\n');\n"
    "            } else if (op.equals(\"getMin\")) {\n"
    "                sb.append(st.peek()[1]).append('\\n');\n"
    "            }\n"
    "        }\n"
    "        System.out.print(sb);\n"
    "    }\n}\n"
)
EXERCISES.update({
    "design_ds": [
        ex("design_ds-minpair", "Pair each value with the min",
           "Min Stack. Fill the blank so each pushed value stores the minimum of itself and the current top's min.",
           _EX_DS_MINSTACK, ["int mn = st.isEmpty() ? x : Math.min(st.peek()[1], x);"],
           [("6\npush 2\npush 1\ngetMin\npop\ntop\ngetMin", "1\n2\n2"), ("3\npush 5\ntop\ngetMin", "5\n5"), ("4\npush 3\npush 4\ngetMin\ntop", "3\n4")],
           hint="The new min is min(x, previous min) — or x if the stack was empty.", source_slug="min-stack"),
        ex("design_ds-getmin", "Read the stored min",
           "Fill the blank so `getMin` prints the minimum stored alongside the current top.",
           _EX_DS_MINSTACK, ["sb.append(st.peek()[1]).append('\\n');"],
           [("4\npush 2\npush 1\ngetMin\ngetMin", "1\n1"), ("3\npush 9\npush 3\ngetMin", "3"), ("2\npush 4\ngetMin", "4")],
           hint="Index [1] of the top pair holds the running minimum.", source_slug="min-stack"),
    ],
})

PREREQS.update({
    "min-stack": [("design_ds", "Pair each value with the running min."), ("stack", "LIFO with O(1) ops.")],
    "implement-queue-stacks": [("design_ds", "Two stacks give amortized FIFO."), ("stack", "Transfer on demand.")],
    "implement-stack-queues": [("design_ds", "Rotate a queue to fake LIFO."), ("queue", "Front is newest.")],
    "design-hashmap": [("design_ds", "Bucket array + chaining."), ("hashing", "Hash the key.")],
    "design-hashset": [("design_ds", "Bucketed membership."), ("hashing", "Hash the value.")],
    "design-circular-queue": [("design_ds", "Modular head/tail over a fixed buffer."), ("queue", "Ring buffer.")],
    "browser-history": [("design_ds", "Array + current index; visit truncates forward.")],
    "lru-cache": [("design_ds", "HashMap + doubly-linked list."), ("hashing", "O(1) lookup.")],
    "lfu-cache": [("design_ds", "Frequency buckets + min-freq pointer.")],
    "time-based-kv": [("design_ds", "Per-key sorted history."), ("binary_search", "Rightmost ts ≤ query.")],
    "design-linked-list": [("design_ds", "Index walk with a dummy head."), ("list_basics", "Splice nodes.")],
    "design-twitter": [("design_ds", "Timestamped tweets, merge newest-first."), ("heap", "Top-10 feed.")],
    "stock-spanner": [("design_ds", "Monotonic stack of (price, span)."), ("stack", "Collapse cheaper days.")],
    "hit-counter": [("design_ds", "Sliding-window queue of timestamps."), ("queue", "Evict old from the front.")],
})

FLASHCARDS += [
    ("Design a cache that evicts least-recently-used?", "HashMap<key,node> for O(1) find + doubly-linked list for O(1) move-to-front; evict the tail.", "seed:design_ds"),
    ("Min Stack — O(1) getMin?", "Push pairs (value, min-so-far); getMin reads the top's stored min.", "seed:design_ds"),
    ("Queue from two stacks?", "Push to 'in'; when 'out' is empty pour 'in' into it (reversing). Amortized O(1).", "seed:design_ds"),
    ("'Design X' — how to approach?", "Map each required op to a structure that makes it cheap (hashmap=lookup, DLL=reorder, heap=top-k, monotonic stack=span).", "seed:design_ds"),
]

EXPANSION_REFS.update({
    "min-stack": {
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    public static void main(String[] a) throws IOException {\n        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));\n        int q=Integer.parseInt(br.readLine().trim());\n        Deque<int[]> st=new ArrayDeque<>(); StringBuilder sb=new StringBuilder();\n        for(int i=0;i<q;i++){ StringTokenizer t=new StringTokenizer(br.readLine()); String op=t.nextToken();\n            if(op.equals(\"push\")){ int x=Integer.parseInt(t.nextToken()); int mn=st.isEmpty()?x:Math.min(st.peek()[1],x); st.push(new int[]{x,mn}); }\n            else if(op.equals(\"pop\")) st.pop();\n            else if(op.equals(\"top\")) sb.append(st.peek()[0]).append('\\n');\n            else if(op.equals(\"getMin\")) sb.append(st.peek()[1]).append('\\n'); }\n        System.out.print(sb);\n    }\n}\n",
        "python": "import sys\ndef main():\n    L=sys.stdin.read().split('\\n'); q=int(L[0]); st=[]; mn=[]; out=[]\n    for i in range(1,q+1):\n        p=L[i].split(); op=p[0]\n        if op=='push': x=int(p[1]); st.append(x); mn.append(x if not mn else min(mn[-1],x))\n        elif op=='pop': st.pop(); mn.pop()\n        elif op=='top': out.append(str(st[-1]))\n        elif op=='getMin': out.append(str(mn[-1]))\n    sys.stdout.write('\\n'.join(out))\nmain()\n",
    },
    "lru-cache": {
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    public static void main(String[] a) throws IOException {\n        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));\n        int q=Integer.parseInt(br.readLine().trim()); int cap=0;\n        LinkedHashMap<Integer,Integer> od=new LinkedHashMap<>(); StringBuilder sb=new StringBuilder();\n        for(int i=0;i<q;i++){ StringTokenizer t=new StringTokenizer(br.readLine()); String op=t.nextToken();\n            if(op.equals(\"cap\")) cap=Integer.parseInt(t.nextToken());\n            else if(op.equals(\"put\")){ int k=Integer.parseInt(t.nextToken()), v=Integer.parseInt(t.nextToken()); if(od.containsKey(k)) od.remove(k); od.put(k,v); if(od.size()>cap){ int oldest=od.keySet().iterator().next(); od.remove(oldest); } }\n            else if(op.equals(\"get\")){ int k=Integer.parseInt(t.nextToken()); if(od.containsKey(k)){ int v=od.remove(k); od.put(k,v); sb.append(v).append('\\n'); } else sb.append(-1).append('\\n'); } }\n        System.out.print(sb);\n    }\n}\n",
        "python": "import sys\nfrom collections import OrderedDict\ndef main():\n    L=sys.stdin.read().split('\\n'); q=int(L[0]); cap=0; od=OrderedDict(); out=[]\n    for i in range(1,q+1):\n        p=L[i].split(); op=p[0]\n        if op=='cap': cap=int(p[1])\n        elif op=='put':\n            k,v=int(p[1]),int(p[2])\n            if k in od: od.move_to_end(k)\n            od[k]=v\n            if len(od)>cap: od.popitem(last=False)\n        elif op=='get':\n            k=int(p[1])\n            if k in od: od.move_to_end(k); out.append(str(od[k]))\n            else: out.append('-1')\n    sys.stdout.write('\\n'.join(out))\nmain()\n",
    },
    "design-hashmap": {
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    public static void main(String[] a) throws IOException {\n        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));\n        int q=Integer.parseInt(br.readLine().trim()); HashMap<Integer,Integer> m=new HashMap<>(); StringBuilder sb=new StringBuilder();\n        for(int i=0;i<q;i++){ StringTokenizer t=new StringTokenizer(br.readLine()); String op=t.nextToken();\n            if(op.equals(\"put\")){ int k=Integer.parseInt(t.nextToken()), v=Integer.parseInt(t.nextToken()); m.put(k,v); }\n            else if(op.equals(\"get\")){ int k=Integer.parseInt(t.nextToken()); sb.append(m.getOrDefault(k,-1)).append('\\n'); }\n            else if(op.equals(\"remove\")){ m.remove(Integer.parseInt(t.nextToken())); } }\n        System.out.print(sb);\n    }\n}\n",
        "python": "import sys\ndef main():\n    L=sys.stdin.read().split('\\n'); q=int(L[0]); m={}; out=[]\n    for i in range(1,q+1):\n        p=L[i].split(); op=p[0]\n        if op=='put': m[int(p[1])]=int(p[2])\n        elif op=='get': out.append(str(m.get(int(p[1]),-1)))\n        elif op=='remove': m.pop(int(p[1]),None)\n    sys.stdout.write('\\n'.join(out))\nmain()\n",
    },
})

# ===========================================================================
# DOMAIN 7 — UNION-FIND (DSU)   (parallel arrays: int n, int[] u, int[] v)
# ===========================================================================

class _DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.sz = [1] * n
        self.cnt = n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.sz[ra] < self.sz[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.sz[ra] += self.sz[rb]
        self.cnt -= 1
        return True


def _uf_components(n, u, v):
    d = _DSU(n)
    for a, b in zip(u, v):
        d.union(a, b)
    return d.cnt


def _uf_valid_tree(n, u, v):
    if len(u) != n - 1:
        return False
    d = _DSU(n)
    for a, b in zip(u, v):
        if not d.union(a, b):
            return False
    return d.cnt == 1


def _uf_redundant(u, v):
    n = max(max(u), max(v)) + 1
    d = _DSU(n)
    for a, b in zip(u, v):
        if not d.union(a, b):
            return [a, b]
    return [-1, -1]


def _uf_largest(n, u, v):
    d = _DSU(n)
    for a, b in zip(u, v):
        d.union(a, b)
    return max(d.sz[d.find(i)] for i in range(n))


def _uf_earliest(n, u, v, times):
    edges = sorted(zip(times, u, v))
    d = _DSU(n)
    for t, a, b in edges:
        d.union(a, b)
        if d.cnt == 1:
            return t
    return -1


def _uf_satisfy(a, b, eq):
    n = max(max(a), max(b)) + 1
    d = _DSU(n)
    for x, y, e in zip(a, b, eq):
        if e == 1:
            d.union(x, y)
    for x, y, e in zip(a, b, eq):
        if e == 0 and d.find(x) == d.find(y):
            return False
    return True


def _uf_make_connected(n, u, v):
    if len(u) < n - 1:
        return -1
    d = _DSU(n)
    for a, b in zip(u, v):
        d.union(a, b)
    return d.cnt - 1


HARNESS_DEFS += [
    dict(slug="count-components", title="Number of Connected Components", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon", "Google"],
         description=("An undirected graph has `n` nodes (0..n-1) and edges given as parallel arrays `u`, `v`. Return the "
                      "number of **connected components**."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Start with n components, one per node.", "Union the endpoints of each edge.",
                "Each successful union merges two components into one.", "The remaining count is the answer."],
         opt=("O((n+e) α(n))", "O(n)", "Union-Find with path compression and union by size."),
         editorial="## Approach\nUnion-Find: begin with n groups; each edge that joins two different groups decrements the count.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "int"},
         fn=lambda n, u, v: _uf_components(n, u, v),
         cases=[("example", "Two groups", (5, [0, 1, 3], [1, 2, 4])), ("example", "One chain", (4, [0, 1, 2], [1, 2, 3])),
                ("hidden", "Self edges", (3, [0, 1], [0, 1])), ("hidden", "All isolated-ish", (5, [0], [1])), ("hidden", "Full", (4, [0, 0, 0], [1, 2, 3]))],
         example_expl=["{0,1,2} and {3,4} → 2 components.", "All four connected → 1."]),
    dict(slug="number-of-provinces", title="Number of Provinces", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon"],
         description=("Cities 0..n-1 have direct friendships given as parallel arrays `u`, `v`. A **province** is a maximal "
                      "group of directly or indirectly connected cities. Return the number of provinces."),
         constraints="1 ≤ n ≤ 200.",
         hints=["Friendship is transitive — a classic connectivity problem.", "Union friends together.",
                "Count distinct roots at the end.", "Union-Find or DFS both work."],
         opt=("O((n+e) α(n))", "O(n)", "Union-Find over the friendship pairs."),
         editorial="## Approach\nUnion each friendship; the number of distinct sets is the number of provinces.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "int"},
         fn=lambda n, u, v: _uf_components(n, u, v),
         cases=[("example", "Two", (3, [0], [1])), ("example", "All", (3, [0, 1], [1, 2])),
                ("hidden", "Isolated", (4, [0], [1])), ("hidden", "Chain", (5, [0, 1, 2, 3], [1, 2, 3, 4])), ("hidden", "Pairs", (4, [0, 2], [1, 3]))],
         example_expl=["{0,1} and {2} → 2 provinces.", "All linked → 1."]),
    dict(slug="graph-valid-tree", title="Graph Valid Tree", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Google", "Facebook"],
         description=("Given `n` nodes and undirected edges (`u`, `v`), return `true` if they form a **valid tree**: fully "
                      "connected and acyclic."),
         constraints="1 ≤ n ≤ 2000.",
         hints=["A tree on n nodes has exactly n-1 edges.", "Union endpoints; a union that finds them already joined is a cycle.",
                "No cycles AND one component means a tree.", "Check the edge count first as a shortcut."],
         opt=("O((n+e) α(n))", "O(n)", "Union-Find detecting cycles; verify a single component."),
         editorial="## Approach\nIf edges != n-1 it can't be a tree. Otherwise union all; a repeat within a set is a cycle. Valid iff no cycle and one component.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "bool"},
         fn=lambda n, u, v: _uf_valid_tree(n, u, v),
         cases=[("example", "Tree", (5, [0, 0, 0, 0], [1, 2, 3, 4])), ("example", "Cycle", (4, [0, 1, 2, 3], [1, 2, 3, 1])),
                ("hidden", "Disconnected", (4, [0, 2], [1, 3])), ("hidden", "Single", (1, [0], [0])), ("hidden", "Path", (3, [0, 1], [1, 2]))],
         example_expl=["Star with 4 edges on 5 nodes → tree.", "Extra edge closes a cycle → not a tree."]),
    dict(slug="redundant-connection", title="Redundant Connection", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon", "Google"],
         description=("A tree on nodes 1..n had one extra edge added, creating a single cycle. Edges arrive as parallel "
                      "arrays `u`, `v`. Return the edge (as `a b`) that closes the cycle — the last such edge if there were a choice."),
         constraints="3 ≤ n ≤ 1000.",
         hints=["Add edges one by one with Union-Find.", "The first edge whose endpoints are already connected is the cycle-closer.",
                "Because there's exactly one extra edge, that edge is the answer.", "Return it in the given order."],
         opt=("O(n α(n))", "O(n)", "Union-Find; the edge that fails to union is redundant."),
         editorial="## Approach\nUnion edges in order; the edge whose two endpoints are already in the same set is the redundant one.",
         spec={"name": "solve", "params": [{"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "int[]"},
         fn=lambda u, v: _uf_redundant(u, v),
         cases=[("example", "Triangle", ([1, 2, 3], [2, 3, 1])), ("example", "Later cycle", ([1, 2, 3, 1, 4], [2, 3, 4, 4, 5])),
                ("hidden", "Small", ([1, 2, 1], [2, 3, 3])), ("hidden", "Star plus", ([1, 1, 2, 3], [2, 3, 3, 1])), ("hidden", "Chain cycle", ([1, 2, 3, 4], [2, 3, 4, 2]))],
         example_expl=["Edge [3,1] closes the triangle.", "[1,4] connects two already-linked nodes."]),
    dict(slug="largest-component-size", title="Largest Connected Component", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Google"],
         description=("Given `n` nodes and undirected edges (`u`, `v`), return the size of the **largest** connected component."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Track a size for each set root.", "Union by size keeps the size at the root.",
                "After all unions, scan roots for the maximum size.", "A single node is a component of size 1."],
         opt=("O((n+e) α(n))", "O(n)", "Union-Find maintaining subtree sizes."),
         editorial="## Approach\nUnion by size; the largest root size after processing all edges is the answer.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "int"},
         fn=lambda n, u, v: _uf_largest(n, u, v),
         cases=[("example", "Big group", (6, [0, 1, 2, 4], [1, 2, 3, 5])), ("example", "All", (4, [0, 1, 2], [1, 2, 3])),
                ("hidden", "Isolated", (5, [0], [1])), ("hidden", "Two pairs", (4, [0, 2], [1, 3])), ("hidden", "Single edge", (3, [0], [1]))],
         example_expl=["{0,1,2,3} size 4 beats {4,5}.", "All connected → 4."]),
    dict(slug="earliest-full-connect", title="Earliest Moment Everyone Connects", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon"],
         description=("`n` people start as strangers. Friendships form at given times: parallel arrays `u`, `v`, `times`. "
                      "Return the earliest time at which **everyone** is connected (directly or indirectly), or -1 if never."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Process friendships in increasing time order.", "Union each pair; watch the component count.",
                "The moment the count drops to 1, everyone is connected.", "If it never reaches 1, return -1."],
         opt=("O(e log e)", "O(n)", "Sort edges by time, union until one component remains."),
         editorial="## Approach\nSort by time; union each friendship; return the timestamp that merges the last two components.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}, {"name": "times", "type": "int[]"}], "returns": "int"},
         fn=lambda n, u, v, times: _uf_earliest(n, u, v, times),
         cases=[("example", "Connects", (6, [0, 3, 2, 5, 5], [1, 4, 3, 3, 4], [1, 2, 4, 6, 3])), ("example", "Never", (4, [0, 1], [1, 2], [1, 2])),
                ("hidden", "Immediate", (2, [0], [1], [5])), ("hidden", "Ordered", (3, [0, 1], [1, 2], [10, 20])), ("hidden", "Unsorted", (3, [1, 0], [2, 1], [5, 1]))],
         example_expl=["All six connected by time 6.", "Node 3 is never reached → -1."]),
    dict(slug="satisfy-equations", title="Satisfiability of Equality Equations", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Facebook"],
         description=("Variables are integers. Constraints are parallel arrays `a`, `b`, `eq` where `eq[i]=1` means "
                      "`a[i]==b[i]` and `eq[i]=0` means `a[i]!=b[i]`. Return `true` if all constraints can hold at once."),
         constraints="1 ≤ number of constraints ≤ 10^4.",
         hints=["Union all the equality constraints first.", "Then check every inequality.",
                "If an inequality's two variables share a set, it's unsatisfiable.", "Equalities are transitive — perfect for Union-Find."],
         opt=("O(n α(n))", "O(n)", "Union equalities, then verify no inequality is within a set."),
         editorial="## Approach\nUnion all `==` pairs; if any `!=` pair is already in the same set, return false; otherwise true.",
         spec={"name": "solve", "params": [{"name": "a", "type": "int[]"}, {"name": "b", "type": "int[]"}, {"name": "eq", "type": "int[]"}], "returns": "bool"},
         fn=lambda a, b, eq: _uf_satisfy(a, b, eq),
         cases=[("example", "Contradiction", ([0, 0], [1, 1], [1, 0])), ("example", "OK", ([0, 1], [1, 2], [1, 1])),
                ("hidden", "Chain break", ([0, 1, 0], [1, 2, 2], [1, 1, 0])), ("hidden", "All equal", ([0, 1], [1, 2], [1, 1])), ("hidden", "Simple neq", ([0], [1], [0]))],
         example_expl=["a==b and a!=b contradict → false.", "0==1 and 1==2 is consistent → true."]),
    dict(slug="make-network-connected", title="Number of Operations to Make Network Connected", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon"],
         description=("`n` computers are wired with cables (`u`, `v`). You may unplug any cable and reuse it elsewhere. "
                      "Return the minimum number of moves to connect all computers, or -1 if there aren't enough cables."),
         constraints="1 ≤ n ≤ 10^5.",
         hints=["You need at least n-1 cables to connect n computers.",
                "Extra cables (those forming cycles) are the ones you can move.",
                "Moves needed = number of components - 1.", "If cables < n-1, it's impossible."],
         opt=("O((n+e) α(n))", "O(n)", "Union-Find: components-1 moves, if enough cables exist."),
         editorial="## Approach\nIf edges < n-1 return -1; otherwise the answer is (number of components − 1), reusing redundant cables.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "int"},
         fn=lambda n, u, v: _uf_make_connected(n, u, v),
         cases=[("example", "One move", (4, [0, 0, 1, 3], [1, 2, 2, 1])), ("example", "Too few", (6, [0, 1], [1, 2])),
                ("hidden", "Already", (3, [0, 1], [1, 2]), ), ("hidden", "Two moves", (6, [0, 1, 2, 4], [1, 2, 0, 5])), ("hidden", "Enough", (5, [0, 1, 2, 3, 0], [1, 2, 3, 4, 2]))],
         example_expl=["Redundant cable reconnects node 3 → 1 move.", "Only 2 cables for 6 nodes → -1."]),
]

CONCEPTS.update({
    "union_find": {
        "name": "Union-Find (DSU)",
        "what": "A disjoint-set structure that merges groups and answers 'same group?' in near-constant time.",
        "deep": "Each element points to a parent; a set is a tree with a representative root. `find` follows parents to the root and, with path compression, flattens the tree; `union` links one root under another, and union-by-size/rank keeps trees shallow. Together they give near-O(1) amortized operations — the go-to for connectivity, cycle detection in undirected graphs, and Kruskal's MST.",
        "java": "int[] parent, size; find flattens: while(parent[x]!=x){ parent[x]=parent[parent[x]]; x=parent[x]; } union links smaller under larger.",
    },
})
CATEGORY.update({"union_find": "Graphs"})
PATTERN_FROM.update({"Union-Find": "Union-Find"})

LESSONS.update({
    "union_find": (
        "# Union-Find (Disjoint Set Union)\n\n"
        "Union-Find answers **'are these two in the same group?'** and **'merge these groups'** in near-constant time. Every element points at a parent; each group is a tree with a root that names it.\n\n"
        "```java\n"
        "int[] parent, size;\n"
        "int find(int x) {\n"
        "    while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } // path compression\n"
        "    return x;\n"
        "}\n"
        "boolean union(int a, int b) {\n"
        "    int ra = find(a), rb = find(b);\n"
        "    if (ra == rb) return false;              // already together (a cycle!)\n"
        "    if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }\n"
        "    parent[rb] = ra; size[ra] += size[rb];    // union by size\n"
        "    return true;\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'connected components'*, *'provinces / friend circles'*, *'valid tree'*, *'redundant edge / cycle in an undirected graph'*, *'accounts merge'*, and Kruskal's MST.\n\n"
        "## Simulated solve — components of edges (0-1)(1-2)(3-4) on n=5\n"
        "| edge | action | components |\n"
        "|---|---|---|\n"
        "| start | 5 singletons | 5 |\n"
        "| 0-1 | union | 4 |\n"
        "| 1-2 | union | 3 |\n"
        "| 3-4 | union | 2 |\n\n"
        "A `union` that returns false (roots already equal) means you just found a **cycle**."
    ),
})

_EX_UF = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static int[] parent;\n"
    "    static int find(int x) {\n"
    "        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }\n"
    "        return x;\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt(), m = sc.nextInt();\n"
    "        parent = new int[n];\n"
    "        for (int i = 0; i < n; i++) parent[i] = i;\n"
    "        int count = n;\n"
    "        for (int i = 0; i < m; i++) {\n"
    "            int u = sc.nextInt(), v = sc.nextInt();\n"
    "            int ru = find(u), rv = find(v);\n"
    "            if (ru != rv) { parent[ru] = rv; count--; }\n"
    "        }\n"
    "        System.out.println(count);\n"
    "    }\n}\n"
)
EXERCISES.update({
    "union_find": [
        ex("union_find-find", "Path compression",
           "Union-Find counting components. Fill the blank so `find` flattens the tree while walking to the root.",
           _EX_UF, ["parent[x] = parent[parent[x]];"],
           [("5 3\n0 1\n1 2\n3 4", "2"), ("4 3\n0 1\n1 2\n2 3", "1"), ("3 0", "3")],
           hint="Point x at its grandparent to shorten the path.", source_slug="count-components"),
        ex("union_find-union", "Merge two sets",
           "Fill the blank so joining two different roots links one under the other and drops the component count.",
           _EX_UF, ["if (ru != rv) { parent[ru] = rv; count--; }"],
           [("5 3\n0 1\n1 2\n3 4", "2"), ("4 4\n0 1\n1 2\n2 3\n3 0", "1"), ("6 2\n0 1\n2 3", "4")],
           hint="Only merge when the roots differ; then one fewer component.", source_slug="count-components"),
    ],
})

PREREQS.update({
    "count-components": [("union_find", "Union edges, count sets."), ("graph_repr", "Nodes and edges.")],
    "number-of-provinces": [("union_find", "Friend circles are components.")],
    "graph-valid-tree": [("union_find", "No cycle + one component."), ("graph_repr", "n-1 edges.")],
    "redundant-connection": [("union_find", "The edge that fails to union closes a cycle.")],
    "largest-component-size": [("union_find", "Union by size; read the biggest root.")],
    "earliest-full-connect": [("union_find", "Union in time order until one set."), ("sorting", "Sort by time.")],
    "satisfy-equations": [("union_find", "Union ==, then check !=.")],
    "make-network-connected": [("union_find", "Moves = components - 1.")],
})

FLASHCARDS += [
    ("Prompt: 'connected components / provinces / valid tree / redundant edge' — technique?", "Union-Find (DSU): union endpoints; a union that finds them already joined is a cycle.", "seed:union_find"),
    ("Union-Find near-O(1) — which two optimizations?", "Path compression in find + union by size/rank.", "seed:union_find"),
    ("Detect a cycle in an UNDIRECTED graph?", "Union-Find: if an edge's endpoints already share a root, it closes a cycle.", "seed:union_find"),
    ("Min edges to connect n nodes given components?", "components - 1 (if you have at least n-1 edges total).", "seed:union_find"),
]

EXPANSION_REFS.update({
    "count-components": {
        "java": "class Solution {\n    int[] p;\n    int find(int x){ while(p[x]!=x){ p[x]=p[p[x]]; x=p[x]; } return x; }\n    int solve(int n, int[] u, int[] v){ p=new int[n]; for(int i=0;i<n;i++) p[i]=i; int cnt=n; for(int i=0;i<u.length;i++){ int a=find(u[i]), b=find(v[i]); if(a!=b){ p[a]=b; cnt--; } } return cnt; }\n}\n",
        "python": "def solve(n, u, v):\n    p=list(range(n))\n    def f(x):\n        while p[x]!=x: p[x]=p[p[x]]; x=p[x]\n        return x\n    cnt=n\n    for a,b in zip(u,v):\n        ra,rb=f(a),f(b)\n        if ra!=rb: p[ra]=rb; cnt-=1\n    return cnt\n",
    },
    "redundant-connection": {
        "java": "class Solution {\n    int[] p;\n    int find(int x){ while(p[x]!=x){ p[x]=p[p[x]]; x=p[x]; } return x; }\n    int[] solve(int[] u, int[] v){ int n=0; for(int x:u) n=Math.max(n,x); for(int x:v) n=Math.max(n,x); p=new int[n+1]; for(int i=0;i<=n;i++) p[i]=i; for(int i=0;i<u.length;i++){ int a=find(u[i]), b=find(v[i]); if(a==b) return new int[]{u[i],v[i]}; p[a]=b; } return new int[]{-1,-1}; }\n}\n",
        "python": "def solve(u, v):\n    n=max(max(u),max(v))+1; p=list(range(n))\n    def f(x):\n        while p[x]!=x: p[x]=p[p[x]]; x=p[x]\n        return x\n    for a,b in zip(u,v):\n        ra,rb=f(a),f(b)\n        if ra==rb: return [a,b]\n        p[ra]=rb\n    return [-1,-1]\n",
    },
    "graph-valid-tree": {
        "java": "class Solution {\n    int[] p;\n    int find(int x){ while(p[x]!=x){ p[x]=p[p[x]]; x=p[x]; } return x; }\n    boolean solve(int n, int[] u, int[] v){ if(u.length!=n-1) return false; p=new int[n]; for(int i=0;i<n;i++) p[i]=i; int cnt=n; for(int i=0;i<u.length;i++){ int a=find(u[i]), b=find(v[i]); if(a==b) return false; p[a]=b; cnt--; } return cnt==1; }\n}\n",
        "python": "def solve(n, u, v):\n    if len(u)!=n-1: return False\n    p=list(range(n))\n    def f(x):\n        while p[x]!=x: p[x]=p[p[x]]; x=p[x]\n        return x\n    cnt=n\n    for a,b in zip(u,v):\n        ra,rb=f(a),f(b)\n        if ra==rb: return False\n        p[ra]=rb; cnt-=1\n    return cnt==1\n",
    },
})

# ===========================================================================
# DOMAIN 8 — ADVANCED GRAPHS   (weighted parallel arrays + raw grids)
# ===========================================================================
_INF = float("inf")


def _g_network_delay(n, u, v, w, src):
    adj = [[] for _ in range(n)]
    for a, b, wt in zip(u, v, w):
        adj[a].append((b, wt))
    dist = [_INF] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, x = _hq.heappop(pq)
        if d > dist[x]:
            continue
        for y, wt in adj[x]:
            if d + wt < dist[y]:
                dist[y] = d + wt
                _hq.heappush(pq, (dist[y], y))
    m = max(dist)
    return m if m < _INF else -1


def _g_cheapest(n, u, v, w, src, dst, k):
    dist = [_INF] * n
    dist[src] = 0
    for _ in range(k + 1):
        nd = dist[:]
        for a, b, wt in zip(u, v, w):
            if dist[a] + wt < nd[b]:
                nd[b] = dist[a] + wt
        dist = nd
    return dist[dst] if dist[dst] < _INF else -1


def _g_mst(n, u, v, w):
    d = _DSU(n)
    total = 0
    for wt, a, b in sorted(zip(w, u, v)):
        if d.union(a, b):
            total += wt
    return total if d.cnt == 1 else -1


def _g_connect_points(xs, ys):
    n = len(xs)
    in_tree = [False] * n
    total = 0
    cnt = 0
    pq = [(0, 0)]
    while pq and cnt < n:
        c, x = _hq.heappop(pq)
        if in_tree[x]:
            continue
        in_tree[x] = True
        total += c
        cnt += 1
        for y in range(n):
            if not in_tree[y]:
                _hq.heappush(pq, (abs(xs[x] - xs[y]) + abs(ys[x] - ys[y]), y))
    return total


def _g_cycle_dir(n, u, v):
    adj = [[] for _ in range(n)]
    for a, b in zip(u, v):
        adj[a].append(b)
    color = [0] * n

    def dfs(x):
        color[x] = 1
        for y in adj[x]:
            if color[y] == 1:
                return True
            if color[y] == 0 and dfs(y):
                return True
        color[x] = 2
        return False
    return any(color[i] == 0 and dfs(i) for i in range(n))


def _g_cycle_undir(n, u, v):
    d = _DSU(n)
    for a, b in zip(u, v):
        if not d.union(a, b):
            return True
    return False


def _g_course(n, u, v):
    return not _g_cycle_dir(n, u, v)


def _g_bipartite(n, u, v):
    from collections import deque
    adj = [[] for _ in range(n)]
    for a, b in zip(u, v):
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    for s in range(n):
        if color[s] == -1:
            color[s] = 0
            q = deque([s])
            while q:
                x = q.popleft()
                for y in adj[x]:
                    if color[y] == -1:
                        color[y] = color[x] ^ 1
                        q.append(y)
                    elif color[y] == color[x]:
                        return False
    return True


def _g_word_ladder(begin, end, words):
    from collections import deque
    ws = set(words)
    if end not in ws:
        return 0
    q = deque([(begin, 1)])
    seen = {begin}
    while q:
        w, d = q.popleft()
        if w == end:
            return d
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nw = w[:i] + c + w[i + 1:]
                if nw in ws and nw not in seen:
                    seen.add(nw)
                    q.append((nw, d + 1))
    return 0


def _g_alien(words):
    from collections import defaultdict
    chars = set("".join(words))
    adj = defaultdict(set)
    indeg = {c: 0 for c in chars}
    for a, b in zip(words, words[1:]):
        ml = min(len(a), len(b))
        found = False
        for i in range(ml):
            if a[i] != b[i]:
                if b[i] not in adj[a[i]]:
                    adj[a[i]].add(b[i])
                    indeg[b[i]] += 1
                found = True
                break
        if not found and len(a) > len(b):
            return ""
    heap = [c for c in chars if indeg[c] == 0]
    _hq.heapify(heap)
    out = []
    while heap:
        c = _hq.heappop(heap)
        out.append(c)
        for nb in sorted(adj[c]):
            indeg[nb] -= 1
            if indeg[nb] == 0:
                _hq.heappush(heap, nb)
    return "".join(out) if len(out) == len(chars) else ""


def _sol_shortest_binary(inp):
    from collections import deque
    L = inp.split('\n')
    H, W = map(int, L[0].split())
    g = [L[1 + i] for i in range(H)]
    if g[0][0] != '0' or g[H - 1][W - 1] != '0':
        return "-1"
    q = deque([(0, 0, 1)])
    seen = {(0, 0)}
    while q:
        r, c, d = q.popleft()
        if r == H - 1 and c == W - 1:
            return str(d)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < H and 0 <= nc < W and (nr, nc) not in seen and g[nr][nc] == '0':
                    seen.add((nr, nc))
                    q.append((nr, nc, d + 1))
    return "-1"


def _sol_min_effort(inp):
    L = inp.split('\n')
    H, W = map(int, L[0].split())
    g = [list(map(int, L[1 + i].split())) for i in range(H)]
    effort = [[_INF] * W for _ in range(H)]
    effort[0][0] = 0
    pq = [(0, 0, 0)]
    while pq:
        e, r, c = _hq.heappop(pq)
        if r == H - 1 and c == W - 1:
            return str(e)
        if e > effort[r][c]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W:
                ne = max(e, abs(g[nr][nc] - g[r][c]))
                if ne < effort[nr][nc]:
                    effort[nr][nc] = ne
                    _hq.heappush(pq, (ne, nr, nc))
    return "0"


HARNESS_DEFS += [
    dict(slug="network-delay-time", title="Network Delay Time", difficulty="Medium",
         topics=["Graphs"], subtopics=["Dijkstra"], companies=["Amazon", "Google"],
         description=("A directed weighted graph on nodes 0..n-1 is given as parallel arrays `u`, `v`, `w` (edge u→v with "
                      "travel time w). A signal starts at `src`. Return the time for **all** nodes to receive it, or -1 if some node can't."),
         constraints="1 ≤ n ≤ 100\nweights ≥ 0.",
         hints=["Shortest travel time from src to every node — that's Dijkstra.",
                "Use a min-heap keyed by distance.", "The answer is the maximum of all shortest distances.",
                "If any node stays unreachable, return -1."],
         opt=("O(E log V)", "O(V+E)", "Dijkstra from the source; answer is the farthest shortest-distance."),
         editorial="## Approach\nDijkstra from src; if every node is reachable, the answer is the largest shortest distance; else -1.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}, {"name": "w", "type": "int[]"}, {"name": "src", "type": "int"}], "returns": "int"},
         fn=lambda n, u, v, w, src: _g_network_delay(n, u, v, w, src),
         cases=[("example", "Reaches all", (4, [0, 0, 1, 2], [1, 2, 3, 3], [1, 4, 1, 1], 0)),
                ("example", "Unreachable", (3, [0], [1], [5], 0)),
                ("hidden", "Chain", (4, [0, 1, 2], [1, 2, 3], [2, 2, 2], 0)), ("hidden", "Single", (1, [0], [0], [0], 0)), ("hidden", "Branch", (3, [0, 0], [1, 2], [3, 1], 0))],
         example_expl=["Farthest shortest path from 0 is 2 (0→1→3).", "Node 2 unreachable → -1."]),
    dict(slug="cheapest-flights-k-stops", title="Cheapest Flights Within K Stops", difficulty="Medium",
         topics=["Graphs"], subtopics=["Bellman-Ford"], companies=["Amazon", "Google"],
         description=("Directed weighted flights are given as `u`, `v`, `w`. Return the cheapest price from `src` to `dst` "
                      "using at most `k` stops (so at most k+1 flights), or -1 if impossible."),
         constraints="1 ≤ n ≤ 100\n0 ≤ k < n.",
         hints=["Limit the number of edges — plain Dijkstra doesn't bound hops.",
                "Bellman-Ford relaxes all edges k+1 times.", "Use a snapshot of distances each round so one round adds one edge.",
                "The dst distance after k+1 rounds is the answer."],
         opt=("O(k*E)", "O(V)", "Bellman-Ford limited to k+1 relaxation rounds."),
         editorial="## Approach\nRelax all edges k+1 times using the previous round's distances (a copy), so each round extends paths by exactly one flight.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}, {"name": "w", "type": "int[]"}, {"name": "src", "type": "int"}, {"name": "dst", "type": "int"}, {"name": "k", "type": "int"}], "returns": "int"},
         fn=lambda n, u, v, w, src, dst, k: _g_cheapest(n, u, v, w, src, dst, k),
         cases=[("example", "One stop", (4, [0, 0, 1, 2], [1, 2, 2, 3], [100, 500, 100, 100], 0, 3, 1)), ("example", "Direct only", (3, [0, 1], [1, 2], [100, 100], 0, 2, 0)),
                ("hidden", "No route", (3, [0], [1], [50], 0, 2, 1)), ("hidden", "Cheapest hops", (3, [0, 0, 1], [1, 2, 2], [5, 100, 5], 0, 2, 1)), ("hidden", "Zero stops", (2, [0], [1], [7], 0, 1, 0))],
         example_expl=["0→1→2→3 within 1 stop? Only 0→2→3 = 600 within 1 stop.", "0 stops → must be direct; none → -1."]),
    dict(slug="mst-total-weight", title="Minimum Spanning Tree Weight", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon", "Google"],
         description=("Given an undirected weighted graph (`u`, `v`, `w`) on `n` nodes, return the total weight of a "
                      "**minimum spanning tree**, or -1 if the graph isn't connected."),
         constraints="1 ≤ n ≤ 10^4.",
         hints=["Kruskal: sort edges by weight, add each if it joins two components.",
                "Union-Find detects whether an edge would form a cycle.",
                "Stop when n-1 edges are chosen.", "Disconnected graph → no spanning tree."],
         opt=("O(E log E)", "O(n)", "Kruskal: sort edges, union non-cyclic ones."),
         editorial="## Approach\nKruskal: sort edges ascending; add an edge if its endpoints are in different sets; sum the chosen weights.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}, {"name": "w", "type": "int[]"}], "returns": "int"},
         fn=lambda n, u, v, w: _g_mst(n, u, v, w),
         cases=[("example", "Square", (4, [0, 0, 1, 2, 1], [1, 2, 2, 3, 3], [1, 4, 2, 3, 5], )), ("example", "Triangle", (3, [0, 1, 0], [1, 2, 2], [1, 2, 3])),
                ("hidden", "Disconnected", (4, [0, 2], [1, 3], [1, 1])), ("hidden", "Line", (3, [0, 1], [1, 2], [5, 5])), ("hidden", "Pick cheap", (3, [0, 0, 1], [1, 2, 2], [10, 10, 1]))],
         example_expl=["MST uses weights 1+2+3 = 6.", "Cheapest two edges 1+2 = 3."]),
    dict(slug="min-cost-connect-points", title="Min Cost to Connect All Points", difficulty="Hard",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon", "Google"],
         description=("Points on a plane are given as parallel arrays `xs`, `ys`. The cost to connect two points is their "
                      "**Manhattan distance** |x1-x2|+|y1-y2|. Return the minimum cost to connect all points."),
         constraints="1 ≤ number of points ≤ 1000.",
         hints=["This is an MST on a complete graph.", "Edge weight = Manhattan distance between two points.",
                "Prim's algorithm avoids materializing all O(n^2) edges up front.", "Grow a tree, always adding the cheapest edge to a new point."],
         opt=("O(n^2)", "O(n)", "Prim's MST on the complete Manhattan graph."),
         editorial="## Approach\nPrim: start anywhere, repeatedly attach the nearest not-yet-connected point (Manhattan distance), summing the costs.",
         spec={"name": "solve", "params": [{"name": "xs", "type": "int[]"}, {"name": "ys", "type": "int[]"}], "returns": "int"},
         fn=lambda xs, ys: _g_connect_points(xs, ys),
         cases=[("example", "Five points", ([0, 2, 3, 0, 1], [0, 2, 10, -4, -1])), ("example", "Two", ([0, 3], [0, 4])),
                ("hidden", "Single", ([5], [5])), ("hidden", "Square", ([0, 0, 1, 1], [0, 1, 0, 1])), ("hidden", "Line", ([0, 1, 2], [0, 0, 0]))],
         example_expl=["Minimum spanning cost is 20.", "One edge of length 7."]),
    dict(slug="detect-cycle-directed", title="Detect Cycle in a Directed Graph", difficulty="Medium",
         topics=["Graphs"], subtopics=["Cycle Detection"], companies=["Amazon", "Google"],
         description=("A directed graph on `n` nodes has edges `u`→`v`. Return `true` if it contains a **cycle**."),
         constraints="1 ≤ n ≤ 2000.",
         hints=["DFS with three states: unvisited, in-progress, done.",
                "A back-edge to an in-progress node means a cycle.", "Mark done after exploring all descendants.",
                "Kahn's topological sort can also detect it (leftover nodes)."],
         opt=("O(V+E)", "O(V)", "DFS 3-coloring detects a back edge."),
         editorial="## Approach\nColor nodes white/gray/black; during DFS, an edge to a gray (in-stack) node is a cycle.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "bool"},
         fn=lambda n, u, v: _g_cycle_dir(n, u, v),
         cases=[("example", "Cycle", (3, [0, 1, 2], [1, 2, 0])), ("example", "DAG", (3, [0, 1], [1, 2])),
                ("hidden", "Self loop", (2, [0], [0])), ("hidden", "Tree-ish", (4, [0, 0, 1], [1, 2, 3])), ("hidden", "Back edge", (4, [0, 1, 2, 3], [1, 2, 3, 1]))],
         example_expl=["0→1→2→0 is a cycle → true.", "Acyclic → false."]),
    dict(slug="detect-cycle-undirected", title="Detect Cycle in an Undirected Graph", difficulty="Medium",
         topics=["Graphs"], subtopics=["Union-Find"], companies=["Amazon"],
         description=("An undirected graph on `n` nodes has edges (`u`, `v`). Return `true` if it contains a **cycle**."),
         constraints="1 ≤ n ≤ 2000.",
         hints=["Union endpoints one edge at a time.", "If both endpoints are already in the same set, this edge closes a cycle.",
                "Union-Find handles it in near-linear time.", "DFS tracking the parent also works."],
         opt=("O((n+e) α(n))", "O(n)", "Union-Find: an edge inside a set is a cycle."),
         editorial="## Approach\nUnion each edge; the first edge whose endpoints already share a root proves a cycle.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "bool"},
         fn=lambda n, u, v: _g_cycle_undir(n, u, v),
         cases=[("example", "Cycle", (3, [0, 1, 2], [1, 2, 0])), ("example", "Tree", (4, [0, 0, 0], [1, 2, 3])),
                ("hidden", "Two comps", (5, [0, 2, 3], [1, 3, 4])), ("hidden", "Square", (4, [0, 1, 2, 3], [1, 2, 3, 0])), ("hidden", "Path", (3, [0, 1], [1, 2]))],
         example_expl=["Triangle → true.", "A star is acyclic → false."]),
    dict(slug="course-schedule-possible", title="Course Schedule", difficulty="Medium",
         topics=["Graphs"], subtopics=["Topological Sort", "Cycle Detection"], companies=["Amazon", "Facebook", "Google"],
         description=("There are `n` courses. Prerequisite pairs mean edge `u`→`v` (take u before v), given as parallel "
                      "arrays. Return `true` if you can finish all courses (the prerequisites have no cycle)."),
         constraints="1 ≤ n ≤ 2000.",
         hints=["You can finish iff the prerequisite graph is acyclic.",
                "Topologically sort, or detect a cycle with DFS.", "Kahn's algorithm: repeatedly remove zero-indegree nodes.",
                "If any node remains, there's a cycle."],
         opt=("O(V+E)", "O(V)", "Topological sort / cycle detection over the prerequisite graph."),
         editorial="## Approach\nAll courses are finishable exactly when the directed prerequisite graph has no cycle (a valid topological order exists).",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "bool"},
         fn=lambda n, u, v: _g_course(n, u, v),
         cases=[("example", "Doable", (2, [0], [1])), ("example", "Cycle", (2, [0, 1], [1, 0])),
                ("hidden", "Chain", (4, [0, 1, 2], [1, 2, 3])), ("hidden", "Self", (2, [0], [0])), ("hidden", "Diamond", (4, [0, 0, 1, 2], [1, 2, 3, 3]))],
         example_expl=["0 before 1 → finishable.", "Mutual prerequisites → impossible."]),
    dict(slug="bipartite-check", title="Is Graph Bipartite?", difficulty="Medium",
         topics=["Graphs"], subtopics=["BFS"], companies=["Amazon", "Facebook"],
         description=("Given an undirected graph on `n` nodes (edges `u`, `v`), return `true` if it is **bipartite** — the "
                      "nodes can be 2-colored so every edge joins different colors."),
         constraints="1 ≤ n ≤ 2000.",
         hints=["Try to 2-color the graph with BFS or DFS.", "Color a node, then its neighbours the opposite color.",
                "A conflict (same color on both ends of an edge) means not bipartite.", "Handle each connected component."],
         opt=("O(V+E)", "O(V)", "BFS/DFS 2-coloring across components."),
         editorial="## Approach\n2-color via BFS; if a neighbour already has the same color as the current node, it isn't bipartite.",
         spec={"name": "solve", "params": [{"name": "n", "type": "int"}, {"name": "u", "type": "int[]"}, {"name": "v", "type": "int[]"}], "returns": "bool"},
         fn=lambda n, u, v: _g_bipartite(n, u, v),
         cases=[("example", "Even cycle", (4, [0, 1, 2, 3], [1, 2, 3, 0])), ("example", "Odd cycle", (3, [0, 1, 2], [1, 2, 0])),
                ("hidden", "Tree", (4, [0, 0, 0], [1, 2, 3])), ("hidden", "Two comps", (5, [0, 2], [1, 3])), ("hidden", "Triangle+", (4, [0, 1, 2, 0], [1, 2, 0, 3]))],
         example_expl=["A 4-cycle 2-colors cleanly → true.", "An odd cycle can't → false."]),
    dict(slug="word-ladder-length", title="Word Ladder", difficulty="Hard",
         topics=["Graphs", "Strings"], subtopics=["BFS"], companies=["Amazon", "Facebook", "Google"],
         description=("Transform `begin` into `end` changing one letter at a time, where every intermediate word must be in "
                      "`words`. Return the number of words in the shortest such sequence (including both ends), or 0 if impossible."),
         constraints="All words share the same length; 1 ≤ |words| ≤ 5000.",
         hints=["Words are nodes; an edge joins words differing by one letter.",
                "Shortest transformation = BFS from begin.", "Generate neighbours by trying each position × 26 letters.",
                "Return the BFS depth when you reach end."],
         opt=("O(N*L*26)", "O(N*L)", "BFS over the implicit one-letter-change graph."),
         editorial="## Approach\nBFS from begin; neighbours are dictionary words one letter away; the depth at which end appears is the ladder length.",
         spec={"name": "solve", "params": [{"name": "begin", "type": "string"}, {"name": "end", "type": "string"}, {"name": "words", "type": "string[]"}], "returns": "int"},
         fn=lambda begin, end, words: _g_word_ladder(begin, end, words),
         cases=[("example", "Classic", ("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])), ("example", "No end", ("hit", "cog", ["hot", "dot", "dog", "lot", "log"])),
                ("hidden", "Direct", ("a", "c", ["a", "b", "c"])), ("hidden", "Two step", ("ab", "cd", ["ad", "cd"])), ("hidden", "Same-ish", ("hot", "dot", ["dot", "hot"]))],
         example_expl=["hit→hot→dot→dog→cog = 5 words.", "cog not in the list → 0."]),
    dict(slug="alien-dictionary-order", title="Alien Dictionary", difficulty="Hard",
         topics=["Graphs", "Strings"], subtopics=["Topological Sort"], companies=["Amazon", "Facebook", "Google"],
         description=("Given a list of `words` sorted by an unknown alphabet's rules, return the **lexicographically smallest** "
                      "valid ordering of the letters that appear, or an empty string if the ordering is invalid (contradictory)."),
         constraints="1 ≤ |words| ≤ 1000.",
         hints=["Adjacent words reveal the first differing letter's order.",
                "Build a graph of letter-before-letter constraints.",
                "Topologically sort; break ties by picking the smallest available letter (a min-heap).",
                "A cycle (or a prefix violation) means no valid order → empty string."],
         opt=("O(C + edges)", "O(C)", "Kahn's topological sort with a min-heap for lexicographic tie-breaks."),
         editorial="## Approach\nDerive edges from the first differing letter of adjacent words; Kahn's algorithm with a min-heap yields the smallest valid order; a leftover letter means a cycle.",
         spec={"name": "solve", "params": [{"name": "words", "type": "string[]"}], "returns": "string"},
         fn=lambda words: _g_alien(words),
         cases=[("example", "Order", (["wrt", "wrf", "er", "ett", "rftt"],)), ("example", "Simple", (["ab", "adc"],)),
                ("hidden", "Invalid prefix", (["abc", "ab"],)), ("hidden", "Single", (["z", "x"],)), ("hidden", "Chain", (["a", "b", "c"],))],
         example_expl=["A valid smallest order of w,r,t,f,e is derived.", "a<d then b<c gives 'abcd'."]),
]

DEFS += [
    dict(slug="shortest-path-binary-matrix", title="Shortest Path in Binary Matrix", difficulty="Medium",
         topics=["Graphs"], subtopics=["BFS", "Grid"], companies=["Amazon"],
         description=("Find the shortest **clear path** from the top-left to the bottom-right of a 0/1 grid, moving in 8 "
                      "directions through `0` cells only. Path length is the number of visited cells; return -1 if none.\n\n"
                      "### Input\n- Line 1: `H W`.\n- Next `H` lines: rows of `0`/`1` (no spaces).\n\n### Output\nThe path length, or -1."),
         constraints="1 ≤ H, W ≤ 100.",
         hints=["Unweighted shortest path → BFS.", "From each cell you may step to any of its 8 neighbours.",
                "Only enter cells equal to 0.", "Count cells (not edges) along the path."],
         opt=("O(H*W)", "O(H*W)", "BFS over clear cells with 8-directional moves."),
         editorial="## Approach\nBFS from (0,0) if it's clear; expand to 8 neighbours that are 0 and unvisited; the depth at the goal is the answer.",
         ref=_sol_shortest_binary, starter_py=_raw_starters("line1: H W; next H lines: rows of 0/1")[1], starter_js=_raw_starters("line1: H W; next H lines: rows of 0/1")[2],
         cases=[("example", "Open", "3 3\n000\n110\n010"), ("example", "Blocked", "2 2\n01\n10"),
                ("hidden", "Single", "1 1\n0"), ("hidden", "Wall", "2 2\n00\n01"), ("hidden", "Diagonal", "3 3\n000\n111\n000")],
         example_expl=["Shortest clear path visits 4 cells.", "Start/goal blocked pattern → -1."]),
    dict(slug="path-minimum-effort", title="Path With Minimum Effort", difficulty="Medium",
         topics=["Graphs"], subtopics=["Dijkstra", "Grid"], companies=["Amazon", "Google"],
         description=("From the top-left to the bottom-right of a height grid (4-directional moves), the **effort** of a path "
                      "is the maximum absolute height difference between consecutive cells. Return the minimum possible effort.\n\n"
                      "### Input\n- Line 1: `H W`.\n- Next `H` lines: `W` space-separated heights.\n\n### Output\nThe minimum effort."),
         constraints="1 ≤ H, W ≤ 100.",
         hints=["Minimize the maximum edge weight along a path.",
                "Dijkstra where a path's cost is the max edge, not the sum.",
                "Relax with newEffort = max(effort, |height diff|).", "The first time you pop the goal is the answer."],
         opt=("O(H*W log(H*W))", "O(H*W)", "Dijkstra where the path cost is the maximum step difference."),
         editorial="## Approach\nDijkstra on the grid; a neighbour's tentative effort is max(current effort, |height difference|); take the min at the goal.",
         ref=_sol_min_effort, starter_py=_raw_starters("line1: H W; next H lines: W heights")[1], starter_js=_raw_starters("line1: H W; next H lines: W heights")[2],
         cases=[("example", "Small", "3 3\n1 2 2\n3 8 2\n5 3 5"), ("example", "Flat", "2 2\n1 1\n1 1"),
                ("hidden", "Single", "1 1\n5"), ("hidden", "Row", "1 4\n1 10 6 7"), ("hidden", "Climb", "2 2\n1 2\n2 3")],
         example_expl=["Route along the low ridge has effort 2.", "Flat grid → effort 0."]),
]
JAVA_STARTERS.update({
    "shortest-path-binary-matrix": _raw_starters("line1: H W; next H lines: rows of 0/1")[0],
    "path-minimum-effort": _raw_starters("line1: H W; next H lines: W heights")[0],
})

CONCEPTS.update({
    "dijkstra": {
        "name": "Dijkstra's Shortest Path",
        "what": "Single-source shortest paths on non-negative weighted graphs using a min-heap of tentative distances.",
        "deep": "Dijkstra grows a set of finalized nodes: repeatedly pop the closest unfinalized node from a min-heap and relax its outgoing edges (if dist[x]+w < dist[y], update). Because weights are non-negative, once a node is popped its distance is final. It's the default for 'shortest / cheapest path with weights' and generalizes to grids (path with minimum effort).",
        "java": "PriorityQueue<long[]> pq keyed by distance; long[] dist filled with a large sentinel; skip stale pops with if (d > dist[x]) continue;.",
    },
    "bellman_ford": {
        "name": "Bellman-Ford",
        "what": "Shortest paths that tolerate negative weights or a hop limit by relaxing all edges V-1 (or k+1) times.",
        "deep": "Where Dijkstra fails (negative edges) or where you must bound the number of edges (at most k stops), Bellman-Ford helps: each round relaxes every edge once, so after r rounds you know the best path using at most r edges. Using a snapshot of the previous round's distances enforces the exact hop limit.",
        "java": "int[] dist; for (round) { int[] nd = dist.clone(); for each edge relax into nd; dist = nd; }",
    },
    "mst": {
        "name": "Minimum Spanning Tree",
        "what": "The cheapest set of edges connecting all nodes, built greedily by Kruskal (sort + union) or Prim (grow a tree).",
        "deep": "Kruskal sorts edges ascending and adds each that joins two different components (Union-Find), stopping at n-1 edges. Prim grows one tree, always attaching the cheapest edge to a new node via a min-heap. On dense/complete graphs (points on a plane) Prim's O(n^2) avoids listing all edges.",
        "java": "Kruskal: sort edges, Union-Find to skip cycles. Prim: PriorityQueue of (cost, node), a boolean inTree[].",
    },
    "graph_cycle": {
        "name": "Cycle Detection & Topological Sort",
        "what": "Finding cycles (or a valid ordering) in directed graphs with DFS 3-coloring or Kahn's indegree algorithm.",
        "deep": "In a DIRECTED graph, DFS colors nodes white/gray/black; an edge to a gray (still-on-the-stack) node is a back-edge — a cycle. Equivalently, Kahn's algorithm repeatedly removes indegree-0 nodes; if some remain, a cycle exists. A graph with no cycle has a topological order (course schedule, build order, alien dictionary). In UNDIRECTED graphs, Union-Find or parent-aware DFS finds cycles.",
        "java": "Directed: int[] color (0/1/2) DFS. Kahn: int[] indeg, a queue of indegree-0 nodes, count popped == n means acyclic.",
    },
})
CATEGORY.update({"dijkstra": "Graphs", "bellman_ford": "Graphs", "mst": "Graphs", "graph_cycle": "Graphs"})
PATTERN_FROM.update({"Bellman-Ford": "Bellman-Ford", "Cycle Detection": "Topological Sort"})

LESSONS.update({
    "dijkstra": (
        "# Dijkstra's Shortest Path\n\n"
        "Dijkstra finds the shortest distance from one source to every node when **weights are non-negative**. Keep a min-heap of `(distance, node)`; the first time you pop a node its distance is final.\n\n"
        "```java\n"
        "long[] dist = new long[n]; Arrays.fill(dist, Long.MAX_VALUE); dist[src] = 0;\n"
        "PriorityQueue<long[]> pq = new PriorityQueue<>((a,b) -> Long.compare(a[0], b[0]));\n"
        "pq.offer(new long[]{0, src});\n"
        "while (!pq.isEmpty()) {\n"
        "    long[] cur = pq.poll(); long d = cur[0]; int x = (int) cur[1];\n"
        "    if (d > dist[x]) continue;                 // stale entry\n"
        "    for (int[] e : adj[x]) {                    // e = {to, weight}\n"
        "        if (d + e[1] < dist[e[0]]) { dist[e[0]] = d + e[1]; pq.offer(new long[]{dist[e[0]], e[0]}); }\n"
        "    }\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'shortest / cheapest path'*, *'minimum time to reach'*, weighted grids ('minimum effort'). Non-negative weights only — otherwise use Bellman-Ford.\n\n"
        "## Simulated solve — from 0, edges 0→1(4) 0→2(1) 2→1(2)\n"
        "| pop | dist after relax |\n"
        "|---|---|\n"
        "| (0,0) | [0, 4, 1] |\n"
        "| (1,2) | [0, 3, 1] (2→1 gives 3) |\n"
        "| (3,1) | final [0,3,1] |\n"
    ),
    "bellman_ford": (
        "# Bellman-Ford\n\n"
        "When edges can be negative, or you must cap the number of hops, relax **all edges** repeatedly.\n\n"
        "```java\n"
        "int[] dist = new int[n]; Arrays.fill(dist, INF); dist[src] = 0;\n"
        "for (int round = 0; round <= k; round++) {   // k+1 rounds = at most k stops\n"
        "    int[] nd = dist.clone();                  // snapshot: exactly one more edge\n"
        "    for (int[] e : edges)                      // e = {u, v, w}\n"
        "        if (dist[e[0]] + e[2] < nd[e[1]]) nd[e[1]] = dist[e[0]] + e[2];\n"
        "    dist = nd;\n"
        "}\n"
        "```\n\n"
        "## When to reach for this\n"
        "Signals: *'at most k stops'*, *'negative weights'*, *'detect a negative cycle'*. The `clone()` snapshot is what enforces the exact hop limit — without it, one round could chain many edges."
    ),
    "mst": (
        "# Minimum Spanning Tree\n\n"
        "Connect every node for the least total edge weight. Two greedy builds:\n\n"
        "**Kruskal** — sort edges, add each that doesn't form a cycle (Union-Find):\n"
        "```java\n"
        "Arrays.sort(edges, (a,b) -> a[2] - b[2]);\n"
        "for (int[] e : edges) if (union(e[0], e[1])) total += e[2];  // skip cycles\n"
        "```\n\n"
        "**Prim** — grow one tree, always adding the cheapest edge to a new node (min-heap). Better on dense/complete graphs (e.g. connecting points on a plane).\n\n"
        "## When to reach for this\n"
        "Signals: *'connect all at minimum cost'*, *'minimum spanning tree'*, *'cheapest network'*. Kruskal pairs naturally with Union-Find; Prim with a heap."
    ),
    "graph_cycle": (
        "# Cycle Detection & Topological Sort\n\n"
        "In a **directed** graph, color nodes as you DFS. An edge into a node still on the recursion stack is a **back edge** — a cycle.\n\n"
        "```java\n"
        "int[] color = new int[n];  // 0 white, 1 gray (on stack), 2 black\n"
        "boolean dfs(int x) {\n"
        "    color[x] = 1;\n"
        "    for (int y : adj[x]) {\n"
        "        if (color[y] == 1) return true;         // back edge → cycle\n"
        "        if (color[y] == 0 && dfs(y)) return true;\n"
        "    }\n"
        "    color[x] = 2; return false;\n"
        "}\n"
        "```\n\n"
        "## Kahn's topological sort (the acyclic case)\n"
        "Repeatedly remove indegree-0 nodes; if you emit all n, the graph is acyclic and you have a valid order (course schedule, build order, alien dictionary). Fewer than n → a cycle.\n\n"
        "## When to reach for this\n"
        "Signals: *'can you finish / order the tasks'*, *'prerequisites'*, *'build order'*, *'detect a cycle'*. Undirected graphs use Union-Find or parent-aware DFS instead."
    ),
})

_EX_G_HEAD = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt(), m = sc.nextInt(), src = sc.nextInt();\n"
    "        List<int[]>[] adj = new List[n];\n"
    "        for (int i = 0; i < n; i++) adj[i] = new ArrayList<>();\n"
    "        for (int i = 0; i < m; i++) { int u = sc.nextInt(), v = sc.nextInt(), w = sc.nextInt(); adj[u].add(new int[]{v, w}); }\n"
)
_EX_G_DIJKSTRA = _EX_G_HEAD + (
    "        long[] dist = new long[n];\n"
    "        Arrays.fill(dist, Long.MAX_VALUE);\n"
    "        dist[src] = 0;\n"
    "        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));\n"
    "        pq.offer(new long[]{0, src});\n"
    "        while (!pq.isEmpty()) {\n"
    "            long[] cur = pq.poll(); long d = cur[0]; int x = (int) cur[1];\n"
    "            if (d > dist[x]) continue;\n"
    "            for (int[] e : adj[x]) {\n"
    "                if (d + e[1] < dist[e[0]]) { dist[e[0]] = d + e[1]; pq.offer(new long[]{dist[e[0]], e[0]}); }\n"
    "            }\n"
    "        }\n"
    "        System.out.println(dist[n - 1] == Long.MAX_VALUE ? -1 : dist[n - 1]);\n"
    "    }\n}\n"
)
_EX_G_CHEAD = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static List<Integer>[] adj;\n"
    "    static int[] color;\n"
    "    static boolean dfs(int x) {\n"
    "        color[x] = 1;\n"
    "        for (int y : adj[x]) {\n"
    "            if (color[y] == 1) return true;\n"
    "            if (color[y] == 0 && dfs(y)) return true;\n"
    "        }\n"
    "        color[x] = 2;\n"
    "        return false;\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt(), m = sc.nextInt();\n"
    "        adj = new List[n]; for (int i = 0; i < n; i++) adj[i] = new ArrayList<>();\n"
    "        for (int i = 0; i < m; i++) { int u = sc.nextInt(), v = sc.nextInt(); adj[u].add(v); }\n"
    "        color = new int[n];\n"
    "        boolean cyc = false;\n"
    "        for (int i = 0; i < n; i++) if (color[i] == 0 && dfs(i)) cyc = true;\n"
    "        System.out.println(cyc ? \"true\" : \"false\");\n"
    "    }\n}\n"
)
EXERCISES.update({
    "dijkstra": [
        ex("dijkstra-relax", "Relax an edge",
           "Dijkstra from a source. Fill the blank so a shorter route to a neighbour updates its distance and re-queues it.",
           _EX_G_DIJKSTRA, ["if (d + e[1] < dist[e[0]]) { dist[e[0]] = d + e[1]; pq.offer(new long[]{dist[e[0]], e[0]}); }"],
           [("4 4 0\n0 1 4\n0 2 1\n2 1 2\n1 3 1", "4"), ("3 2 0\n0 1 5\n1 2 5", "10"), ("2 1 0\n0 1 7", "7")],
           hint="If d + weight beats the stored distance, update and push the neighbour.", source_slug="network-delay-time"),
        ex("dijkstra-stale", "Skip stale heap entries",
           "Fill the blank so an outdated (already-improved) heap entry is ignored when popped.",
           _EX_G_DIJKSTRA, ["if (d > dist[x]) continue;"],
           [("4 4 0\n0 1 4\n0 2 1\n2 1 2\n1 3 1", "4"), ("3 3 0\n0 1 1\n0 2 5\n1 2 1", "2"), ("2 1 0\n0 1 3", "3")],
           hint="If the popped distance is worse than the best known, this entry is stale — skip it.", source_slug="network-delay-time"),
    ],
    "graph_cycle": [
        ex("graph_cycle-back", "Spot the back edge",
           "Directed cycle detection with 3-coloring. Fill the blank so reaching a node still on the DFS stack reports a cycle.",
           _EX_G_CHEAD, ["if (color[y] == 1) return true;"],
           [("3 3\n0 1\n1 2\n2 0", "true"), ("3 2\n0 1\n1 2", "false"), ("2 1\n0 0", "true")],
           hint="Gray (color 1) means the node is still on the current path — a back edge.", source_slug="detect-cycle-directed"),
    ],
})

PREREQS.update({
    "network-delay-time": [("dijkstra", "Min-heap relaxation from the source."), ("graph_repr", "Adjacency list.")],
    "cheapest-flights-k-stops": [("bellman_ford", "k+1 rounds with a snapshot.")],
    "mst-total-weight": [("mst", "Kruskal sorts edges, unions non-cycles."), ("union_find", "Cycle check.")],
    "min-cost-connect-points": [("mst", "Prim on a complete Manhattan graph."), ("heap", "Nearest new point.")],
    "detect-cycle-directed": [("graph_cycle", "3-color DFS back edge.")],
    "detect-cycle-undirected": [("union_find", "Edge inside a set is a cycle.")],
    "course-schedule-possible": [("graph_cycle", "Finishable iff acyclic."), ("topo", "Kahn's order.")],
    "bipartite-check": [("bfs", "2-color the components."), ("graph_repr", "Undirected adjacency.")],
    "word-ladder-length": [("bfs", "Shortest transformation."), ("string_basics", "One-letter neighbours.")],
    "alien-dictionary-order": [("topo", "Order letters by constraints."), ("graph_cycle", "Cycle → invalid.")],
    "shortest-path-binary-matrix": [("bfs", "Unweighted shortest path."), ("grid", "8-directional moves.")],
    "path-minimum-effort": [("dijkstra", "Minimize the max step."), ("grid", "4-directional relaxation.")],
})

FLASHCARDS += [
    ("Shortest path with non-negative weights?", "Dijkstra: min-heap of (dist,node); pop the closest, relax edges; skip stale pops.", "seed:dijkstra"),
    ("Shortest path with 'at most k stops' or negative edges?", "Bellman-Ford: relax all edges k+1 times using a snapshot of the previous round.", "seed:bellman_ford"),
    ("Connect all nodes at minimum total cost?", "Minimum Spanning Tree — Kruskal (sort + union-find) or Prim (grow a tree with a heap).", "seed:mst"),
    ("Detect a cycle in a DIRECTED graph / order tasks?", "DFS 3-coloring (gray = on stack → cycle) or Kahn's topological sort (leftover nodes = cycle).", "seed:graph_cycle"),
]

EXPANSION_REFS.update({
    "network-delay-time": {
        "java": "import java.util.*;\nclass Solution {\n    int solve(int n, int[] u, int[] v, int[] w, int src){ List<int[]>[] adj=new List[n]; for(int i=0;i<n;i++) adj[i]=new ArrayList<>(); for(int i=0;i<u.length;i++) adj[u[i]].add(new int[]{v[i],w[i]}); long[] dist=new long[n]; Arrays.fill(dist,Long.MAX_VALUE); dist[src]=0; PriorityQueue<long[]> pq=new PriorityQueue<>((a,b)->Long.compare(a[0],b[0])); pq.offer(new long[]{0,src}); while(!pq.isEmpty()){ long[] c=pq.poll(); long d=c[0]; int x=(int)c[1]; if(d>dist[x]) continue; for(int[] e:adj[x]) if(d+e[1]<dist[e[0]]){ dist[e[0]]=d+e[1]; pq.offer(new long[]{dist[e[0]],e[0]}); } } long m=0; for(long dd:dist){ if(dd==Long.MAX_VALUE) return -1; m=Math.max(m,dd); } return (int)m; }\n}\n",
        "python": "import heapq\ndef solve(n, u, v, w, src):\n    adj=[[] for _ in range(n)]\n    for a,b,wt in zip(u,v,w): adj[a].append((b,wt))\n    INF=float('inf'); dist=[INF]*n; dist[src]=0; pq=[(0,src)]\n    while pq:\n        d,x=heapq.heappop(pq)\n        if d>dist[x]: continue\n        for y,wt in adj[x]:\n            if d+wt<dist[y]: dist[y]=d+wt; heapq.heappush(pq,(dist[y],y))\n    m=max(dist)\n    return m if m<INF else -1\n",
    },
    "mst-total-weight": {
        "java": "import java.util.*;\nclass Solution {\n    int[] p;\n    int find(int x){ while(p[x]!=x){ p[x]=p[p[x]]; x=p[x]; } return x; }\n    int solve(int n, int[] u, int[] v, int[] w){ Integer[] idx=new Integer[u.length]; for(int i=0;i<idx.length;i++) idx[i]=i; Arrays.sort(idx,(a,b)->w[a]-w[b]); p=new int[n]; for(int i=0;i<n;i++) p[i]=i; int total=0, used=0; for(int i:idx){ int a=find(u[i]), b=find(v[i]); if(a!=b){ p[a]=b; total+=w[i]; used++; } } return used==n-1?total:-1; }\n}\n",
        "python": "def solve(n, u, v, w):\n    p=list(range(n))\n    def f(x):\n        while p[x]!=x: p[x]=p[p[x]]; x=p[x]\n        return x\n    total=0; used=0\n    for wt,a,b in sorted(zip(w,u,v)):\n        ra,rb=f(a),f(b)\n        if ra!=rb: p[ra]=rb; total+=wt; used+=1\n    return total if used==n-1 else -1\n",
    },
    "bipartite-check": {
        "java": "import java.util.*;\nclass Solution {\n    boolean solve(int n, int[] u, int[] v){ List<Integer>[] adj=new List[n]; for(int i=0;i<n;i++) adj[i]=new ArrayList<>(); for(int i=0;i<u.length;i++){ adj[u[i]].add(v[i]); adj[v[i]].add(u[i]); } int[] col=new int[n]; Arrays.fill(col,-1); for(int s=0;s<n;s++){ if(col[s]==-1){ col[s]=0; ArrayDeque<Integer> q=new ArrayDeque<>(); q.add(s); while(!q.isEmpty()){ int x=q.poll(); for(int y:adj[x]){ if(col[y]==-1){ col[y]=col[x]^1; q.add(y); } else if(col[y]==col[x]) return false; } } } } return true; }\n}\n",
        "python": "from collections import deque\ndef solve(n, u, v):\n    adj=[[] for _ in range(n)]\n    for a,b in zip(u,v): adj[a].append(b); adj[b].append(a)\n    col=[-1]*n\n    for s in range(n):\n        if col[s]==-1:\n            col[s]=0; q=deque([s])\n            while q:\n                x=q.popleft()\n                for y in adj[x]:\n                    if col[y]==-1: col[y]=col[x]^1; q.append(y)\n                    elif col[y]==col[x]: return False\n    return True\n",
    },
})

# ===========================================================================
# DOMAIN 9 — TRIES (PREFIX TREES)
# ===========================================================================

def _tr_lcp(strs):
    if not strs:
        return ""
    pre = strs[0]
    for s in strs[1:]:
        while not s.startswith(pre):
            pre = pre[:-1]
            if not pre:
                return ""
    return pre


def _tr_word_in_dict(words, queries):
    ws = set(words)
    return [1 if q in ws else 0 for q in queries]


def _tr_prefix_counts(words, prefixes):
    return [sum(1 for w in words if w.startswith(p)) for p in prefixes]


def _tr_replace(roots, sentence):
    rs = set(roots)
    out = []
    for w in sentence:
        rep = w
        for k in range(1, len(w) + 1):
            if w[:k] in rs:
                rep = w[:k]
                break
        out.append(rep)
    return " ".join(out)


def _tr_longest_word(words):
    ws = set(words)
    best = ""
    for w in sorted(words):
        if all(w[:k] in ws for k in range(1, len(w))):
            if len(w) > len(best):
                best = w
    return best


def _tr_max_xor(nums):
    best = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            best = max(best, nums[i] ^ nums[j])
    return best


def _sol_trie_ops(inp):
    words = set()
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "insert":
            words.add(p[1])
        elif op == "search":
            out.append("true" if p[1] in words else "false")
        elif op == "startsWith":
            out.append("true" if any(w.startswith(p[1]) for w in words) else "false")
    return "\n".join(out)


def _sol_word_dict(inp):
    import re
    words = set()
    out = []
    for p in _ops(inp):
        op = p[0]
        if op == "addWord":
            words.add(p[1])
        elif op == "search":
            rx = re.compile("^" + p[1] + "$")
            out.append("true" if any(rx.match(w) for w in words) else "false")
    return "\n".join(out)


HARNESS_DEFS += [
    dict(slug="longest-common-prefix-strs", title="Longest Common Prefix", difficulty="Easy",
         topics=["Strings"], subtopics=["Trie"], companies=["Amazon", "Google"],
         description="Return the longest common prefix shared by all the given strings (empty string if there is none).",
         constraints="1 ≤ number of strings ≤ 200\nlowercase letters.",
         hints=["The common prefix can only shrink as you consider more words.",
                "Start with the first word as the candidate prefix.",
                "Trim it until it prefixes the next word.", "A trie's single-child chain from the root gives the same answer."],
         opt=("O(total chars)", "O(1)", "Shrink a candidate prefix against each word."),
         editorial="## Approach\nHold a candidate prefix; for each word, trim the candidate until the word starts with it.",
         spec={"name": "solve", "params": [{"name": "strs", "type": "string[]"}], "returns": "string"},
         fn=lambda strs: _tr_lcp(strs),
         cases=[("example", "Common", (["flower", "flow", "flight"],)), ("example", "None", (["dog", "racecar", "car"],)),
                ("hidden", "All same", (["ab", "ab", "ab"],)), ("hidden", "Single", (["solo"],)), ("hidden", "One char", (["a", "ab", "abc"],))],
         example_expl=["'fl' prefixes all three.", "No shared prefix → empty."]),
    dict(slug="word-in-dictionary", title="Word Lookups in a Dictionary", difficulty="Medium",
         topics=["Data Structures", "Strings"], subtopics=["Trie"], companies=["Amazon"],
         description=("Build a dictionary from `words`, then answer each query in `queries`: return `1` if the query is an "
                      "exact word in the dictionary, else `0`. Return the answers as an array."),
         constraints="1 ≤ |words|, |queries| ≤ 10^4.",
         hints=["Insert every word into a trie (or hash set).", "Each query walks the trie letter by letter.",
                "A match requires ending on a word-terminal node.", "Return 1/0 per query."],
         opt=("O(total chars)", "O(total chars)", "Trie membership per query."),
         editorial="## Approach\nInsert words into a trie; a query matches if its path exists and ends on a word-end node.",
         spec={"name": "solve", "params": [{"name": "words", "type": "string[]"}, {"name": "queries", "type": "string[]"}], "returns": "int[]"},
         fn=lambda words, queries: _tr_word_in_dict(words, queries),
         cases=[("example", "Mixed", (["apple", "app", "apply"], ["app", "appl", "apply"])), ("example", "Miss", (["cat"], ["dog"])),
                ("hidden", "Prefix not word", (["abc"], ["ab", "abc"])), ("hidden", "All hit", (["x", "y"], ["x", "y"])), ("hidden", "Empty-ish", (["a"], ["a", "b"]))],
         example_expl=["app and apply are words (1), appl is not (0).", "dog absent → 0."]),
    dict(slug="prefix-counts", title="Count Words With Each Prefix", difficulty="Medium",
         topics=["Data Structures", "Strings"], subtopics=["Trie"], companies=["Amazon", "Bloomberg"],
         description=("Given `words` and `prefixes`, return for each prefix how many words start with it."),
         constraints="1 ≤ |words|, |prefixes| ≤ 10^4.",
         hints=["A trie node can store how many words pass through it.",
                "Increment a counter at every node along each inserted word.",
                "A prefix query reads the counter at the prefix's end node.", "Missing prefix → 0."],
         opt=("O(total chars)", "O(total chars)", "Trie with a pass-through count per node."),
         editorial="## Approach\nStore a count at each trie node (words passing through). A prefix's answer is the count at the node where the prefix ends.",
         spec={"name": "solve", "params": [{"name": "words", "type": "string[]"}, {"name": "prefixes", "type": "string[]"}], "returns": "int[]"},
         fn=lambda words, prefixes: _tr_prefix_counts(words, prefixes),
         cases=[("example", "Counts", (["apple", "app", "apricot", "banana"], ["ap", "app", "b"])), ("example", "None", (["cat"], ["do"])),
                ("hidden", "Full word", (["abc", "abcd"], ["abc"])), ("hidden", "All", (["a", "ab", "abc"], ["a"])), ("hidden", "Empty prefix count", (["x", "y"], ["z"]))],
         example_expl=["ap→3, app→2, b→1.", "No word starts with 'do' → 0."]),
    dict(slug="replace-words-roots", title="Replace Words", difficulty="Medium",
         topics=["Data Structures", "Strings"], subtopics=["Trie"], companies=["Amazon"],
         description=("Given dictionary `roots` and a `sentence` (array of words), replace every word by the **shortest root** "
                      "that is a prefix of it; leave a word unchanged if no root applies. Return the sentence as a single string."),
         constraints="1 ≤ sizes ≤ 10^4\nlowercase letters.",
         hints=["Put the roots in a trie.", "For each word, walk the trie until you hit a root-end node.",
                "The first (shortest) root that terminates wins.", "Join the transformed words with spaces."],
         opt=("O(total chars)", "O(total chars)", "Trie walk per word to the earliest root end."),
         editorial="## Approach\nInsert roots into a trie; for each word, follow letters until reaching a root terminal — that prefix replaces the word.",
         spec={"name": "solve", "params": [{"name": "roots", "type": "string[]"}, {"name": "sentence", "type": "string[]"}], "returns": "string"},
         fn=lambda roots, sentence: _tr_replace(roots, sentence),
         cases=[("example", "Battery", (["cat", "bat", "rat"], ["the", "cattle", "was", "rattled", "by", "the", "battery"])), ("example", "None", (["xyz"], ["hello", "world"])),
                ("hidden", "Shortest wins", (["a", "aa"], ["aaaa"])), ("hidden", "Exact", (["cat"], ["cat"])), ("hidden", "Mixed", (["b"], ["ba", "cd"]))],
         example_expl=["cattle→cat, rattled→rat, battery→bat.", "No roots apply → unchanged."]),
    dict(slug="longest-buildable-word", title="Longest Word Built One Char at a Time", difficulty="Medium",
         topics=["Data Structures", "Strings"], subtopics=["Trie"], companies=["Google"],
         description=("Return the longest word in `words` that can be built one character at a time, where every prefix is "
                      "also a word in the list. If several qualify, return the **lexicographically smallest**."),
         constraints="1 ≤ |words| ≤ 10^4.",
         hints=["A word qualifies only if all its prefixes are present.",
                "A trie makes 'is every prefix a word?' a single walk.",
                "Sort words so the lexicographically smallest is found first.", "Track the longest qualifying word."],
         opt=("O(total chars)", "O(total chars)", "Trie/hash-set prefix check over sorted words."),
         editorial="## Approach\nSort the words; keep the longest one whose every proper prefix is also in the set (ties broken by sort order).",
         spec={"name": "solve", "params": [{"name": "words", "type": "string[]"}], "returns": "string"},
         fn=lambda words: _tr_longest_word(words),
         cases=[("example", "Build", (["w", "wo", "wor", "worl", "world"],)), ("example", "Tie", (["a", "banana", "app", "appl", "ap", "apply", "apple"],)),
                ("hidden", "None buildable", (["abc", "bcd"],)), ("hidden", "Single", (["x"],)), ("hidden", "Two roots", (["a", "ab", "b", "bc"],))],
         example_expl=["Every prefix present → 'world'.", "'apple' and 'apply' qualify; 'apple' is smaller."]),
    dict(slug="max-xor-pair", title="Maximum XOR of Two Numbers", difficulty="Hard",
         topics=["Data Structures", "Bit Manipulation"], subtopics=["Trie"], companies=["Amazon", "Google"],
         description="Return the maximum value of `nums[i] XOR nums[j]` over all pairs.",
         constraints="1 ≤ n ≤ 2*10^4\n0 ≤ nums[i] ≤ 2^31 - 1.",
         hints=["Insert numbers' bits (high to low) into a binary trie.",
                "For each number, greedily walk toward the opposite bit to maximize XOR.",
                "Each step that can differ adds a 1 to that bit of the result.",
                "The brute-force O(n^2) also works for small inputs."],
         opt=("O(n * 32)", "O(n * 32)", "Binary trie of bits; greedily pick opposite bits per number."),
         editorial="## Approach\nBuild a bitwise trie; for each number, descend choosing the opposite bit when available to maximize the XOR.",
         spec={"name": "solve", "params": [{"name": "nums", "type": "int[]"}], "returns": "int"},
         fn=lambda nums: _tr_max_xor(nums),
         cases=[("example", "Classic", ([3, 10, 5, 25, 2, 8],)), ("example", "Two", ([1, 2],)),
                ("hidden", "Same", ([7, 7, 7],)), ("hidden", "Zeros", ([0, 0, 1],)), ("hidden", "Powers", ([1, 2, 4, 8],))],
         example_expl=["5 XOR 25 = 28 is the max.", "1 XOR 2 = 3."]),
]

DEFS += [
    dict(slug="implement-trie-ops", title="Implement Trie (Prefix Tree)", difficulty="Medium",
         topics=["Data Structures"], subtopics=["Trie"], companies=["Amazon", "Google", "Microsoft"],
         description=("Implement a trie supporting insert, exact search, and prefix search.\n\n### Operations\n"
                      "`insert w`, `search w` (print true/false — exact word), `startsWith p` (print true/false — any word "
                      "with that prefix).\n\n### I/O\nLine 1: `Q`; then operations. One line per `search`/`startsWith`."),
         constraints="1 ≤ Q ≤ 10^4\nlowercase words.",
         hints=["Each node has up to 26 children and an is-word flag.",
                "insert walks/creates nodes for each character, marking the last as a word.",
                "search must land on a word-end node; startsWith just needs the path to exist.",
                "All operations are O(word length)."],
         opt=("O(L) per op", "O(total chars)", "26-way trie with an is-word flag."),
         editorial="## Approach\nNodes hold children + isWord. insert creates the path and marks the end; search checks isWord at the end; startsWith checks the path exists.",
         ref=_sol_trie_ops, starter_py=_ops_starters("line1: Q; then insert w / search w / startsWith p")[1], starter_js=_ops_starters("line1: Q; then insert w / search w / startsWith p")[2],
         cases=[("example", "Basic", "6\ninsert apple\nsearch apple\nsearch app\nstartsWith app\ninsert app\nsearch app"),
                ("example", "Prefix", "4\ninsert abc\nstartsWith ab\nsearch ab\nstartsWith abc"),
                ("hidden", "Miss", "3\ninsert cat\nsearch dog\nstartsWith c"),
                ("hidden", "Rebuild", "5\ninsert a\ninsert ab\nsearch a\nsearch ab\nstartsWith abc")],
         example_expl=["apple true; app false then true after insert; startsWith app true.", "ab is a prefix but not a word."]),
    dict(slug="word-dictionary-wildcard", title="Add and Search Word (wildcards)", difficulty="Hard",
         topics=["Data Structures"], subtopics=["Trie"], companies=["Amazon", "Facebook"],
         description=("A dictionary supporting wildcard search.\n\n### Operations\n`addWord w`, `search w` — where `w` may "
                      "contain `.` matching **any single letter**; print true/false.\n\n### I/O\nLine 1: `Q`; then operations. "
                      "One line per `search`."),
         constraints="1 ≤ Q ≤ 10^4\nletters and '.'.",
         hints=["Store words in a trie.", "For a normal letter, descend that child.",
                "For '.', recurse into every child.", "Match succeeds only if you end on a word node."],
         opt=("O(26^dots * L)", "O(total chars)", "Trie DFS branching on '.' wildcards."),
         editorial="## Approach\nTrie of words; search DFS follows the exact child for a letter and tries all children for '.', requiring a word-end at the last character.",
         ref=_sol_word_dict, starter_py=_ops_starters("line1: Q; then addWord w / search w (w may contain '.')")[1], starter_js=_ops_starters("line1: Q; then addWord w / search w (w may contain '.')")[2],
         cases=[("example", "Wildcard", "6\naddWord bad\naddWord dad\naddWord mad\nsearch pad\nsearch bad\nsearch .ad"),
                ("example", "Multi dot", "4\naddWord cat\naddWord cot\nsearch c.t\nsearch c.."),
                ("hidden", "No match", "3\naddWord a\nsearch b\nsearch ."),
                ("hidden", "Exact", "3\naddWord hello\nsearch hello\nsearch hell.")],
         example_expl=["pad absent; bad present; .ad matches bad/dad/mad.", "c.t matches cat and cot."]),
]
JAVA_STARTERS.update({
    "implement-trie-ops": _ops_starters("line1: Q; then insert w / search w / startsWith p")[0],
    "word-dictionary-wildcard": _ops_starters("line1: Q; then addWord w / search w (w may contain '.')")[0],
})

CONCEPTS.update({
    "trie": {
        "name": "Trie (Prefix Tree)",
        "what": "A tree where each edge is a character, so shared prefixes share a path — giving O(word length) insert and lookup.",
        "deep": "Each node has up to 26 children and an is-word flag. Words that share a prefix share the nodes along it, which is what makes tries shine at prefix queries: autocomplete, 'count words with prefix', word search with wildcards, and even maximum-XOR via a binary trie. The cost of any operation is the length of the word, independent of how many words are stored.",
        "java": "class Node { Node[] ch = new Node[26]; boolean end; } — index by c-'a'; insert walks/creates, search checks end, startsWith checks the path exists.",
    },
})
CATEGORY.update({"trie": "Data Structures"})

LESSONS.update({
    "trie": (
        "# Trie (Prefix Tree)\n\n"
        "A trie stores words along **paths of characters**. Words sharing a prefix share the nodes for that prefix, so every operation costs only the length of the word — never the size of the dictionary.\n\n"
        "```java\n"
        "class Node { Node[] ch = new Node[26]; boolean end; }\n"
        "Node root = new Node();\n"
        "void insert(String w){\n"
        "    Node n = root;\n"
        "    for (char c : w.toCharArray()) {\n"
        "        int i = c - 'a';\n"
        "        if (n.ch[i] == null) n.ch[i] = new Node();  // create child\n"
        "        n = n.ch[i];\n"
        "    }\n"
        "    n.end = true;                                    // mark word end\n"
        "}\n"
        "```\n\n"
        "## search vs startsWith\n"
        "| Query | Succeeds when |\n"
        "|---|---|\n"
        "| `search(w)` | the path exists **and** the last node has `end == true` |\n"
        "| `startsWith(p)` | the path exists (end flag irrelevant) |\n\n"
        "## When to reach for this\n"
        "Signals: *'prefix'*, *'autocomplete / suggestions'*, *'dictionary of words'*, *'words with wildcard'*, and 'maximum XOR' (a binary trie of bits).\n\n"
        "## Simulated solve — insert 'app', 'apple', search 'app'\n"
        "| step | path |\n"
        "|---|---|\n"
        "| insert app | root-a-p-p (p.end=true) |\n"
        "| insert apple | reuse a-p-p, add l-e (e.end=true) |\n"
        "| search app | walk a-p-p, end==true → **true** |\n"
        "| search ap | walk a-p, end==false → **false** |\n"
    ),
})

_EXJ_TRIE = (
    "import java.util.*;\n"
    "public class Main {\n"
    "    static class Node { Map<Character,Node> ch = new HashMap<>(); boolean end; }\n"
    "    static Node root = new Node();\n"
    "    static void insert(String w) {\n"
    "        Node n = root;\n"
    "        for (char c : w.toCharArray()) {\n"
    "            n.ch.putIfAbsent(c, new Node());\n"
    "            n = n.ch.get(c);\n"
    "        }\n"
    "        n.end = true;\n"
    "    }\n"
    "    static boolean search(String w) {\n"
    "        Node n = root;\n"
    "        for (char c : w.toCharArray()) {\n"
    "            if (!n.ch.containsKey(c)) return false;\n"
    "            n = n.ch.get(c);\n"
    "        }\n"
    "        return n.end;\n"
    "    }\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt();\n"
    "        for (int i = 0; i < n; i++) insert(sc.next());\n"
    "        int q = sc.nextInt();\n"
    "        StringBuilder sb = new StringBuilder();\n"
    "        for (int i = 0; i < q; i++) { sb.append(search(sc.next()) ? 1 : 0); if (i < q - 1) sb.append('\\n'); }\n"
    "        System.out.println(sb.toString());\n"
    "    }\n}\n"
)
EXERCISES.update({
    "trie": [
        ex("trie-insert", "Create the child",
           "Trie insert. Fill the blank so a missing child node is created before descending into it.",
           _EXJ_TRIE, ["n.ch.putIfAbsent(c, new Node());"],
           [("3 cat car dog\n2 car cow", "1\n0"), ("1 a\n1 a", "1"), ("2 ab abc\n2 ab abcd", "1\n0")],
           hint="Add a new Node for c only if one doesn't already exist.", source_slug="implement-trie-ops"),
        ex("trie-search", "Walk or fail",
           "Trie search. Fill the blank so search returns false the moment a character path is missing.",
           _EXJ_TRIE, ["if (!n.ch.containsKey(c)) return false;"],
           [("2 cat car\n2 ca cat", "0\n1"), ("1 hi\n1 hix", "0"), ("2 a ab\n2 a ab", "1\n1")],
           hint="If the current node has no child for c, the word can't be present.", source_slug="implement-trie-ops"),
        ex("trie-end", "Mark the word end",
           "Fill the blank so the final node of an inserted word is flagged as a complete word.",
           _EXJ_TRIE, ["n.end = true;"],
           [("2 ca cat\n2 ca cab", "1\n0"), ("1 x\n1 x", "1"), ("2 go gone\n2 go gon", "1\n0")],
           hint="After walking the word, set end = true on the last node.", source_slug="implement-trie-ops"),
    ],
})

PREREQS.update({
    "longest-common-prefix-strs": [("trie", "Single-child chain from the root."), ("string_basics", "Trim a candidate.")],
    "word-in-dictionary": [("trie", "Exact membership by path + end flag.")],
    "prefix-counts": [("trie", "Pass-through count per node.")],
    "replace-words-roots": [("trie", "Walk to the earliest root end.")],
    "longest-buildable-word": [("trie", "Every prefix must be a word."), ("sorting", "Lexicographic tie-break.")],
    "max-xor-pair": [("trie", "Binary trie of bits."), ("bit_manip", "Greedy opposite bits.")],
    "implement-trie-ops": [("trie", "insert / search / startsWith on a 26-way tree.")],
    "word-dictionary-wildcard": [("trie", "DFS branching on '.'."), ("recursion", "Try all children for a wildcard.")],
}) if "bit_manip" in CONCEPTS else PREREQS.update({
    "longest-common-prefix-strs": [("trie", "Single-child chain from the root."), ("string_basics", "Trim a candidate.")],
    "word-in-dictionary": [("trie", "Exact membership by path + end flag.")],
    "prefix-counts": [("trie", "Pass-through count per node.")],
    "replace-words-roots": [("trie", "Walk to the earliest root end.")],
    "longest-buildable-word": [("trie", "Every prefix must be a word."), ("sorting", "Lexicographic tie-break.")],
    "max-xor-pair": [("trie", "Binary trie of bits.")],
    "implement-trie-ops": [("trie", "insert / search / startsWith on a 26-way tree.")],
    "word-dictionary-wildcard": [("trie", "DFS branching on '.'."), ("recursion", "Try all children for a wildcard.")],
})

FLASHCARDS += [
    ("Prompt mentions 'prefix / autocomplete / dictionary of words' — structure?", "Trie (prefix tree): edges are characters; O(word length) insert/search independent of dictionary size.", "seed:trie"),
    ("Trie search vs startsWith — difference?", "search needs the path AND end==true; startsWith only needs the path to exist.", "seed:trie"),
    ("Wildcard '.' word search?", "Trie DFS: exact child for a letter, recurse into ALL children for '.'.", "seed:trie"),
    ("Maximum XOR of two numbers in a set?", "Binary trie of bits (high→low); for each number greedily walk toward the opposite bit.", "seed:trie"),
]

EXPANSION_REFS.update({
    "implement-trie-ops": {
        "java": "import java.util.*;\nimport java.io.*;\npublic class Main {\n    static class Node { Node[] ch=new Node[26]; boolean end; }\n    static Node root=new Node();\n    static void insert(String w){ Node n=root; for(char c:w.toCharArray()){ int i=c-'a'; if(n.ch[i]==null) n.ch[i]=new Node(); n=n.ch[i]; } n.end=true; }\n    static Node walk(String w){ Node n=root; for(char c:w.toCharArray()){ int i=c-'a'; if(n.ch[i]==null) return null; n=n.ch[i]; } return n; }\n    public static void main(String[] a) throws IOException {\n        BufferedReader br=new BufferedReader(new InputStreamReader(System.in));\n        int q=Integer.parseInt(br.readLine().trim()); StringBuilder sb=new StringBuilder();\n        for(int i=0;i<q;i++){ StringTokenizer t=new StringTokenizer(br.readLine()); String op=t.nextToken(), w=t.nextToken();\n            if(op.equals(\"insert\")) insert(w);\n            else if(op.equals(\"search\")){ Node n=walk(w); sb.append(n!=null&&n.end?\"true\":\"false\").append('\\n'); }\n            else { Node n=walk(w); sb.append(n!=null?\"true\":\"false\").append('\\n'); } }\n        System.out.print(sb);\n    }\n}\n",
        "python": "import sys\ndef main():\n    L=sys.stdin.read().split('\\n'); q=int(L[0]); words=set(); out=[]\n    for i in range(1,q+1):\n        p=L[i].split(); op=p[0]\n        if op=='insert': words.add(p[1])\n        elif op=='search': out.append('true' if p[1] in words else 'false')\n        else: out.append('true' if any(w.startswith(p[1]) for w in words) else 'false')\n    sys.stdout.write('\\n'.join(out))\nmain()\n",
    },
    "word-in-dictionary": {
        "java": "import java.util.*;\nclass Solution {\n    int[] solve(String[] words, String[] queries){ Set<String> s=new HashSet<>(Arrays.asList(words)); int[] r=new int[queries.length]; for(int i=0;i<queries.length;i++) r[i]=s.contains(queries[i])?1:0; return r; }\n}\n",
        "python": "def solve(words, queries):\n    s=set(words)\n    return [1 if q in s else 0 for q in queries]\n",
    },
    "max-xor-pair": {
        "java": "class Solution {\n    int solve(int[] nums){ int best=0; for(int i=0;i<nums.length;i++) for(int j=i+1;j<nums.length;j++) best=Math.max(best, nums[i]^nums[j]); return best; }\n}\n",
        "python": "def solve(nums):\n    best=0\n    for i in range(len(nums)):\n        for j in range(i+1,len(nums)):\n            best=max(best, nums[i]^nums[j])\n    return best\n",
    },
})

# === END EXPANSION ===
