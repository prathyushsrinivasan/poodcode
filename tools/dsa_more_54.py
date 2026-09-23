# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 54 — Trees & Graphs, part 2: binary search trees and backtracking.
#
#   sorted-array-to-bst     the middle is the root — a balanced build in O(n)
#   bst-mode                in-order is sorted, so equal values are adjacent: count runs
#   bst-delete              the three cases, and the in-order successor
#   trim-bst                the invariant says which whole subtree survives
#   merge-two-bsts          two in-order iterators, merged like two sorted arrays
#   binary-strings-n        the smallest search tree there is: two choices per level
#   partition-k-equal       k buckets, biggest first, and never try two equal buckets
#   map-colorings-count     constraint search: a colour is legal if no neighbour has it
#   word-break-sentences    split a string, pruned by "can the rest be split at all?"
#   expression-target-count operators between digits, carrying the last product
#
# Uses the shapes and generators from dsa_more_53.py; defines `graph_k`.
# ===========================================================================

# "n m k", then m lines "u v"
_SHAPES["graph_k"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m, k = d[0], d[1], d[2]\n"
       "edges = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(m)]\n",
    py_params="n, edges, k",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), k = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n",
    js_params="n, edges, k",
    java="        int n = sc.nextInt(), m = sc.nextInt(), k = sc.nextInt();\n        int[][] edges = new int[m][2];\n"
         "        for (int i = 0; i < m; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] edges, int k", java_args="n, edges, k",
)


def _graph_k_case(n, edges, k):
    """"n m k" + edge lines."""
    return f"{n} {len(edges)} {k}\n" + "".join(f"{u} {v}\n" for u, v in edges)


def _bst_line(inserts):
    """The level-order line of the BST built by inserting `inserts` in order.
    Equal values go left, so in-order is non-decreasing either way."""
    n = len(inserts)
    left, right = [-1] * n, [-1] * n
    for i in range(1, n):
        x = 0
        while True:
            if inserts[i] <= inserts[x]:
                if left[x] < 0:
                    left[x] = i
                    break
                x = left[x]
            else:
                if right[x] < 0:
                    right[x] = i
                    break
                x = right[x]
    return _level_of(inserts, left, right)


def _perm(n, seed, lo=1):
    return _Lcg(seed).shuffle(list(range(lo, lo + n)))


_p(
    "sorted-array-to-bst", "Balance From a Sorted List", "Easy",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Divide and Conquer"],
    companies=["Amazon", "Microsoft", "Apple"],
    shape="arr_tree", ret="TreeNode",
    todo="the middle element (lo + hi) / 2 is the root; build the left half and the right half recursively",
    description=(
        "Build a **height-balanced** binary search tree from a strictly increasing list. Use this "
        "rule so the answer is unique: the root of a range `[lo, hi]` is the element at index "
        "`(lo + hi) / 2` (integer division — the *lower* middle), its left subtree is built from "
        "`[lo, mid − 1]` and its right from `[mid + 1, hi]`.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` strictly increasing integers.\n\n### Output\nThe tree "
        "in level order, `null` for a missing child, trailing `null`s removed."
    ),
    constraints="1 ≤ n ≤ 10^4\n-10^9 ≤ a[i] ≤ 10^9, strictly increasing",
    hints=[
        "In-order of a BST is sorted, so the sorted list *is* the in-order. Any element can be the root; the middle one splits the rest evenly.",
        "Recurse on the two halves. Each half is again sorted, so the same rule applies.",
        "Pass indices, not sub-arrays: copying halves costs O(n log n).",
    ],
    opt=("O(n)", "O(log n)",
         "Each element becomes one node; the recursion is as deep as the balanced tree."),
    editorial=(
        "## The one thing this teaches\n**Balance is chosen, not repaired.** Inserting sorted "
        "values one by one builds a chain; building from the middle builds a tree of height "
        "⌈log₂(n + 1)⌉ in one pass.\n\n"
        "## Approach\n```java\nTreeNode build(int lo, int hi) {\n    if (lo > hi) return null;\n"
        "    int mid = (lo + hi) >>> 1;\n    TreeNode n = new TreeNode(a[mid]);\n"
        "    n.left = build(lo, mid - 1);\n    n.right = build(mid + 1, hi);\n    return n;\n}\n```\n\n"
        "## Why the two halves differ by at most one\nA range of length L puts ⌊(L − 1)/2⌋ on the "
        "left and ⌈(L − 1)/2⌉ on the right. By induction every subtree's height is ⌈log₂(size + 1)⌉, "
        "so sibling heights differ by at most one."
    ),
    py='''
def solve(a):
    def build(lo, hi):
        if lo > hi:
            return None
        m = (lo + hi) // 2
        n = TreeNode(a[m])
        n.left = build(lo, m - 1)
        n.right = build(m + 1, hi)
        return n
    return build(0, len(a) - 1)
''',
    java='''
    static int[] A;

    static TreeNode build(int lo, int hi) {
        if (lo > hi) return null;
        int m = (lo + hi) >>> 1;
        TreeNode n = new TreeNode(A[m]);
        n.left = build(lo, m - 1);
        n.right = build(m + 1, hi);
        return n;
    }

    static TreeNode solve(int[] a) {
        A = a;
        return build(0, a.length - 1);
    }
''',
    examples=[
        ("Example 1", "6\n-7 -2 0 4 9 13\n"),
        ("Example 2", "1\n5\n"),
    ],
    hidden=[
        ("Two", "2\n1 2\n"),
        ("Three", "3\n10 20 30\n"),
        ("Seven", "7\n1 2 3 4 5 6 7\n"),
        ("Eight", "8\n1 2 3 4 5 6 7 8\n"),
        ("Extremes", "4\n-1000000000 -1 1 1000000000\n"),
        ("Large", "10000\n" + " ".join(str(3 * i - 15000) for i in range(10000)) + "\n"),
    ],
    expl=[
        "The middle of six is index 2 (value 0). Left of it, -7 -2 has lower middle -7; right, 4 9 13 has middle 9.",
        "A single element is a single node.",
    ],
    prereqs=[
        ("bst", "In-order of a BST is sorted, so any element can root the tree and the middle balances it."),
        ("recursion", "Build each half with the same rule, passing index ranges."),
    ],
)


_p(
    "bst-mode", "Most Common Value in a BST", "Easy",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "In-order Traversal"],
    companies=["Google", "Amazon"],
    shape="tree", ret="String",
    todo="walk in-order (values come out sorted, so equal values are adjacent); count each run and keep the best",
    description=(
        "A binary search tree may hold **repeated** values: everything in a node's left subtree is "
        "`≤` the node, and everything in its right subtree is `≥` it. Print every value that "
        "occurs the **most** times, in increasing order.\n\n"
        "### Input\nOne line: the tree in level order (`null` for a missing child).\n\n"
        "### Output\nThe most frequent value(s), separated by spaces."
    ),
    constraints="1 ≤ nodes ≤ 5000\n-10^5 ≤ value ≤ 10^5\nThe tree is a valid BST under the ≤ / ≥ rule.",
    hints=[
        "A hash map of counts works, but ignores that this is a BST.",
        "In-order visits the values in non-decreasing order, so all copies of a value arrive one after another.",
        "Track the previous value and the current run length. When a run beats the best, reset the answer list; when it ties, append.",
    ],
    opt=("O(n)", "O(h)",
         "One in-order walk; apart from the answer, only the previous value and two counters."),
    editorial=(
        "## The one thing this teaches\n**Sorted order makes counting a scan.** In a sorted "
        "sequence, equal values are adjacent — so \"most frequent\" is \"longest run\", and a run "
        "needs two variables, not a map.\n\n"
        "## Approach\n```java\nvoid visit(int v) {                 // called in-order\n"
        "    run = (v == prev) ? run + 1 : 1;\n    prev = v;\n"
        "    if (run > best) { best = run; modes.clear(); }\n    if (run == best) modes.add(v);\n}\n```\n\n"
        "Because values arrive in increasing order, the modes are already sorted."
    ),
    py='''
def solve(root):
    modes, prev, run, best = [], None, 0, 0
    st, cur = [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        v = cur.val
        run = run + 1 if v == prev else 1
        prev = v
        if run > best:
            best, modes = run, []
        if run == best:
            modes.append(v)
        cur = cur.right
    return " ".join(map(str, modes))
''',
    java='''
    static String solve(TreeNode root) {
        List<Integer> modes = new ArrayList<>();
        Integer prev = null;
        int run = 0, best = 0;
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        TreeNode cur = root;
        while (cur != null || !st.isEmpty()) {
            while (cur != null) { st.push(cur); cur = cur.left; }
            cur = st.pop();
            int v = cur.val;
            run = (prev != null && prev == v) ? run + 1 : 1;
            prev = v;
            if (run > best) { best = run; modes.clear(); }
            if (run == best) modes.add(v);
            cur = cur.right;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < modes.size(); i++) {
            if (i > 0) sb.append(' ');
            sb.append(modes.get(i));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _bst_line([6, 3, 8, 3, 8, 3, 9]) + "\n"),
        ("Example 2", _bst_line([4, 2, 7]) + "\n"),
    ],
    hidden=[
        ("One node", "5\n"),
        ("All equal", _bst_line([2, 2, 2, 2]) + "\n"),
        ("Two tied modes", _bst_line([5, 1, 9, 1, 9]) + "\n"),
        ("Negative mode", _bst_line([0, -3, 4, -3, 2]) + "\n"),
        ("Random", _bst_line([v % 7 for v in _perm(60, 101)]) + "\n"),
        ("Large", _bst_line([v % 400 - 200 for v in _perm(5000, 102)]) + "\n"),
    ],
    expl=[
        "3 appears three times; 8 twice; 6 and 9 once.",
        "Every value appears once, so all three are modes.",
    ],
    prereqs=[
        ("bst", "In-order walks a BST's values in sorted order, so equal values are adjacent."),
        ("tree_traversal", "An iterative in-order walk with an explicit stack."),
    ],
)


_p(
    "bst-delete", "Remove Keys From a BST", "Medium",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Deletion"],
    companies=["Amazon", "Microsoft", "Uber"],
    shape="tree_keys_out", ret="TreeNode",
    todo="descend to the key; 0 or 1 child -> replace the node by that child; 2 children -> copy the in-order successor's value in, then delete the successor from the right subtree",
    description=(
        "Delete keys from a binary search tree of **distinct** values, one after another. A key "
        "that is not in the tree is ignored.\n\n"
        "Use this rule so the result is unique: a node with **two** children takes the value of its "
        "**in-order successor** (the smallest value in its right subtree), and that successor is "
        "then deleted from the right subtree. A node with one child is replaced by that child; a "
        "leaf simply disappears.\n\n"
        "### Input\nLine 1: the tree in level order (`null` for a missing child).\nLine 2: `k`.\n"
        "Line 3: the `k` keys to delete, in order.\n\n### Output\nThe final tree in level order "
        "(trailing `null`s removed), or `EMPTY` if nothing is left."
    ),
    constraints="1 ≤ nodes ≤ 3000\n1 ≤ k ≤ 3000\nValues are distinct, -10^5 ≤ value ≤ 10^5",
    hints=[
        "First find the node: an ordinary BST descent. Return the (possibly new) root of each subtree so the parent can re-link.",
        "No children: return null. One child: return that child — it takes the node's place and stays a valid BST.",
        "Two children: the successor is the leftmost node of the right subtree. Copy its value into the node, then delete that value from the right subtree — where it has no left child, so it is the easy case.",
    ],
    opt=("O(k · h)", "O(h)",
         "Each deletion is one descent plus, at most, one walk down to the successor."),
    editorial=(
        "## The one thing this teaches\n**The invariant decides the repair.** Removing a node "
        "leaves a hole; whatever fills it must be larger than everything on its left and smaller "
        "than everything on its right. The in-order successor is exactly that value.\n\n"
        "## Approach\n```java\nTreeNode delete(TreeNode n, int key) {\n    if (n == null) return null;\n"
        "    if (key < n.val) n.left = delete(n.left, key);\n    else if (key > n.val) n.right = delete(n.right, key);\n"
        "    else {\n        if (n.left == null) return n.right;          // 0 or 1 child\n"
        "        if (n.right == null) return n.left;\n        TreeNode s = n.right;\n"
        "        while (s.left != null) s = s.left;          // successor\n        n.val = s.val;\n"
        "        n.right = delete(n.right, s.val);            // it has no left child\n    }\n    return n;\n}\n```\n\n"
        "## Why return the subtree\nThe node being removed may be the root of the whole tree. "
        "Returning the new subtree root and assigning it to the parent's pointer handles that case "
        "with no special code."
    ),
    py='''
def solve(root, keys):
    sys.setrecursionlimit(20000)

    def delete(n, key):
        if n is None:
            return None
        if key < n.val:
            n.left = delete(n.left, key)
        elif key > n.val:
            n.right = delete(n.right, key)
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

    for key in keys:
        root = delete(root, key)
    return root
''',
    java='''
    static TreeNode delete(TreeNode n, int key) {
        if (n == null) return null;
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

    static TreeNode solve(TreeNode root, int[] keys) {
        for (int key : keys) root = delete(root, key);
        return root;
    }
''',
    examples=[
        ("Example 1", _bst_line([50, 30, 70, 20, 40, 60, 80]) + "\n1\n30\n"),
        ("Example 2", _bst_line([10, 5, 15]) + "\n3\n99 10 5\n"),
    ],
    hidden=[
        ("Delete the only node", "7\n1\n7\n"),
        ("A leaf", _bst_line([8, 4, 12]) + "\n1\n12\n"),
        ("One child", _bst_line([8, 4, 2]) + "\n1\n4\n"),
        ("Successor with a right child", _bst_line([20, 10, 40, 30, 50, 35]) + "\n1\n20\n"),
        ("Delete everything", _bst_line([3, 1, 5, 2, 4]) + "\n5\n3 1 5 2 4\n"),
        ("Missing keys", _bst_line([3, 1, 5]) + "\n3\n0 2 6\n"),
        ("Random", _bst_line(_perm(200, 111)) + "\n60\n" + " ".join(map(str, _perm(250, 112)[:60])) + "\n"),
        ("Chain", _bst_line(list(range(1, 2001))) + "\n5\n1 1000 2000 500 1500\n"),
        ("Large", _bst_line(_perm(3000, 113)) + "\n1500\n" + " ".join(map(str, _perm(3000, 114)[:1500])) + "\n"),
    ],
    expl=[
        "30 has two children, so it takes its successor's value, 40, and the old 40 leaf is removed.",
        "99 is not in the tree. Deleting 10 promotes 15 (its successor); deleting 5 leaves just 15.",
    ],
    prereqs=[
        ("bst", "The in-order successor is the smallest value larger than the node — the leftmost node of its right subtree."),
        ("recursion", "Each call returns the new root of its subtree so the parent can re-link it."),
    ],
)


_p(
    "trim-bst", "Keep Only the Range", "Medium",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Recursion"],
    companies=["Amazon", "Bloomberg"],
    shape="tree_lohi_out", ret="TreeNode",
    todo="a node below lo: its whole left subtree is below lo too, so return trim(right); above hi: return trim(left); inside: trim both children",
    description=(
        "Remove every node whose value lies outside `[lo, hi]` from a binary search tree of "
        "**distinct** values, keeping every surviving node's relative placement: if `x` was below "
        "`y` before, it is still below `y` afterwards. That makes the result unique.\n\n"
        "### Input\nLine 1: the tree in level order (`null` for a missing child).\nLine 2: `lo hi`.\n\n"
        "### Output\nThe trimmed tree in level order (trailing `null`s removed), or `EMPTY`."
    ),
    constraints="1 ≤ nodes ≤ 3000\nValues are distinct, 0 ≤ value ≤ 10^5\n0 ≤ lo ≤ hi ≤ 10^5",
    hints=[
        "If a node is below `lo`, so is its entire left subtree — the BST invariant says so. Nothing there survives.",
        "Its right subtree may still hold values in range. So a too-small node is replaced by its trimmed right subtree.",
        "Symmetrically for a too-large node. A node inside the range keeps its place and trims both children.",
    ],
    opt=("O(n)", "O(h)",
         "Each node is examined at most once; discarded subtrees are skipped without being visited."),
    editorial=(
        "## The one thing this teaches\n**The invariant discards whole subtrees.** A plain tree "
        "would force you to inspect every node. In a BST, one comparison at a node tells you the "
        "fate of one of its subtrees entirely.\n\n"
        "## Approach\n```java\nTreeNode trim(TreeNode n) {\n    if (n == null) return null;\n"
        "    if (n.val < lo) return trim(n.right);   // n and its left subtree are all too small\n"
        "    if (n.val > hi) return trim(n.left);    // n and its right subtree are all too big\n"
        "    n.left = trim(n.left);\n    n.right = trim(n.right);\n    return n;\n}\n```\n\n"
        "## Why the result is still a BST\nA surviving node only ever gets a replacement child "
        "from inside the subtree it already had on that side, so every value stays on the same "
        "side of every ancestor."
    ),
    py='''
def solve(root, lo, hi):
    sys.setrecursionlimit(20000)

    def trim(n):
        if n is None:
            return None
        if n.val < lo:
            return trim(n.right)
        if n.val > hi:
            return trim(n.left)
        n.left = trim(n.left)
        n.right = trim(n.right)
        return n

    return trim(root)
''',
    java='''
    static int LO, HI;

    static TreeNode trim(TreeNode n) {
        if (n == null) return null;
        if (n.val < LO) return trim(n.right);
        if (n.val > HI) return trim(n.left);
        n.left = trim(n.left);
        n.right = trim(n.right);
        return n;
    }

    static TreeNode solve(TreeNode root, int lo, int hi) {
        LO = lo;
        HI = hi;
        return trim(root);
    }
''',
    examples=[
        ("Example 1", _bst_line([12, 5, 20, 2, 8, 15, 25, 7]) + "\n6 16\n"),
        ("Example 2", _bst_line([4, 2, 6]) + "\n10 20\n"),
    ],
    hidden=[
        ("Everything survives", _bst_line([4, 2, 6, 1, 3]) + "\n0 100\n"),
        ("Only the root", _bst_line([4, 2, 6]) + "\n4 4\n"),
        ("The root goes, a child takes over", _bst_line([10, 5, 15, 3, 7]) + "\n4 8\n"),
        ("Deep replacement", _bst_line([50, 10, 60, 5, 40, 30, 45, 35]) + "\n31 46\n"),
        ("Random", _bst_line(_perm(300, 121)) + "\n80 190\n"),
        ("Chain", _bst_line(list(range(1, 2001))) + "\n700 1300\n"),
        ("Large", _bst_line(_perm(3000, 122, lo=0)) + "\n1000 2000\n"),
    ],
    expl=[
        "2 goes (so does nothing else on its side), 5 goes and 8 takes its place with 7 below it; 20 and 25 go, and 15 takes 20's place.",
        "No value lies in [10, 20].",
    ],
    prereqs=[
        ("bst", "A node below the range has its whole left subtree below the range too."),
        ("recursion", "Return the trimmed subtree, and let the parent re-link it."),
    ],
)


_p(
    "merge-two-bsts", "Merge Two Sorted Trees", "Medium",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Iterator", "Merge"],
    companies=["Amazon", "Meta"],
    shape="tree2", ret="String",
    todo="run two iterative in-order walks side by side and always take the smaller current value — the merge step of merge sort",
    description=(
        "Two binary search trees each hold some integers (a value may repeat across the trees, or "
        "within one, with `≤` to the left and `≥` to the right). Print **all** the values in "
        "non-decreasing order.\n\n"
        "### Input\nLine 1: the first tree in level order (`null` for a missing child).\nLine 2: "
        "the second tree (it may be the single token `null`, an empty tree).\n\n"
        "### Output\nAll the values, separated by spaces."
    ),
    constraints="1 ≤ nodes in the first tree ≤ 5000\n0 ≤ nodes in the second tree ≤ 5000\n-10^5 ≤ value ≤ 10^5",
    hints=[
        "Concatenating both trees and sorting works in O(n log n) — but each tree already hands you its values sorted.",
        "An iterative in-order walk can be paused after any value: keep one explicit stack per tree.",
        "Peek at both stacks' tops and advance the smaller one. When one tree runs out, drain the other.",
    ],
    opt=("O(n + m)", "O(h1 + h2)",
         "Every node is pushed and popped once; each stack holds at most one root path."),
    editorial=(
        "## The one thing this teaches\n**A BST is a sorted sequence you can pause.** The BST "
        "iterator (a stack of the left spine) produces the next smallest value in amortised O(1) "
        "— so two of them can be merged exactly like two sorted arrays.\n\n"
        "## Approach\n```java\npushLeft(a, r1); pushLeft(b, r2);\nwhile (!a.isEmpty() || !b.isEmpty()) {\n"
        "    Deque<TreeNode> s = b.isEmpty() || (!a.isEmpty() && a.peek().val <= b.peek().val) ? a : b;\n"
        "    TreeNode n = s.pop();\n    out.add(n.val);\n    pushLeft(s, n.right);\n}\n```\n\n"
        "## Versus flatten-and-sort\nBoth are fine for 10⁴ values; the merge uses O(h) extra "
        "memory instead of O(n) and never compares values that are already in order."
    ),
    py='''
def solve(root, root2):
    def push(st, n):
        while n:
            st.append(n)
            n = n.left
    a, b, out = [], [], []
    push(a, root)
    push(b, root2)
    while a or b:
        s = a if not b or (a and a[-1].val <= b[-1].val) else b
        n = s.pop()
        out.append(n.val)
        push(s, n.right)
    return " ".join(map(str, out))
''',
    java='''
    static void push(ArrayDeque<TreeNode> st, TreeNode n) {
        for (; n != null; n = n.left) st.push(n);
    }

    static String solve(TreeNode root, TreeNode root2) {
        ArrayDeque<TreeNode> a = new ArrayDeque<>(), b = new ArrayDeque<>();
        push(a, root);
        push(b, root2);
        StringBuilder sb = new StringBuilder();
        while (!a.isEmpty() || !b.isEmpty()) {
            ArrayDeque<TreeNode> s = b.isEmpty() || (!a.isEmpty() && a.peek().val <= b.peek().val) ? a : b;
            TreeNode n = s.pop();
            if (sb.length() > 0) sb.append(' ');
            sb.append(n.val);
            push(s, n.right);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _two_trees(_bst_line([5, 2, 9]), _bst_line([4, 1, 7, 8]))),
        ("Example 2", _two_trees(_bst_line([3, 3, 6]), "null")),
    ],
    hidden=[
        ("Single nodes", _two_trees("1", "1")),
        ("Interleaved", _two_trees(_bst_line([4, 2, 6, 1, 3, 5, 7]), _bst_line([4, 2, 6, 1, 3, 5, 7]))),
        ("Disjoint ranges", _two_trees(_bst_line([3, 1, 2]), _bst_line([10, 20, 30]))),
        ("Negative", _two_trees(_bst_line([-5, -10, 0]), _bst_line([-7, -8, -6]))),
        ("Chains", _two_trees(_bst_line(list(range(0, 2000, 2))), _bst_line(list(range(1999, 0, -2))))),
        ("Large", _two_trees(_bst_line([v - 2500 for v in _perm(5000, 131)]), _bst_line([v % 1000 for v in _perm(5000, 132)]))),
    ],
    expl=[
        "The first tree gives 2 5 9, the second 1 4 7 8; merged: 1 2 4 5 7 8 9.",
        "The second tree is empty; the first holds 3, 3 and 6.",
    ],
    prereqs=[
        ("bst", "In-order walks a BST in sorted order, and the iterative walk can pause between values."),
        ("two_pointers", "Merging two sorted sequences by always taking the smaller head."),
    ],
)


_p(
    "binary-strings-n", "Every Row of Switches", "Intro",
    topics=["Backtracking", "Recursion"], subtopics=["Backtracking", "Recursion", "Generation"],
    companies=["Amazon", "TCS"],
    shape="n", ret="String",
    todo="fill position i with '0', recurse, then with '1', recurse; print the row when all n positions are filled",
    description=(
        "A panel has `n` switches in a row, each off (`0`) or on (`1`). Print every possible "
        "setting of the panel, one per line, in increasing order (as binary numbers — so "
        "`00…0` first and `11…1` last).\n\n"
        "### Input\nOne integer `n`.\n\n### Output\n`2^n` lines, each a string of `n` characters."
    ),
    constraints="1 ≤ n ≤ 12",
    hints=[
        "Decide the switches left to right. At each position there are two choices, and after choosing you decide the rest the same way.",
        "Keep one `char[]` of length n. Set position i, recurse to i + 1, and when i == n print the whole array.",
        "Trying `0` before `1` at every position produces the settings in increasing order automatically.",
    ],
    opt=("O(2ⁿ · n)", "O(n)",
         "2ⁿ settings, each printed in n characters; the recursion is n deep."),
    editorial=(
        "## The one thing this teaches\n**The shape of every backtracking search.** A decision "
        "per level, a recursive call per choice, and output at the bottom. The search tree here "
        "is complete: two branches per level, 2ⁿ leaves.\n\n"
        "## Approach\n```java\nvoid gen(int i) {\n    if (i == n) { out.append(buf).append('\\n'); return; }\n"
        "    buf[i] = '0'; gen(i + 1);\n    buf[i] = '1'; gen(i + 1);\n}\n```\n\n"
        "## Where is the undo?\nThere is none, because the next choice *overwrites* position i. "
        "That only works for a fixed-length array; with a growing `List` you would have to remove "
        "the last element — the undo step of the next problems."
    ),
    py='''
def solve(n):
    out, buf = [], ["0"] * n

    def gen(i):
        if i == n:
            out.append("".join(buf))
            return
        buf[i] = "0"
        gen(i + 1)
        buf[i] = "1"
        gen(i + 1)

    gen(0)
    return "\\n".join(out)
''',
    java='''
    static char[] buf;
    static StringBuilder out = new StringBuilder();

    static void gen(int i) {
        if (i == buf.length) {
            if (out.length() > 0) out.append('\\n');
            out.append(buf);
            return;
        }
        buf[i] = '0';
        gen(i + 1);
        buf[i] = '1';
        gen(i + 1);
    }

    static String solve(long n) {
        buf = new char[(int) n];
        gen(0);
        return out.toString();
    }
''',
    examples=[
        ("Example 1", "2\n"),
        ("Example 2", "3\n"),
    ],
    hidden=[
        ("One switch", "1\n"),
        ("Four", "4\n"),
        ("Seven", "7\n"),
        ("Twelve", "12\n"),
    ],
    expl=[
        "Two switches: 00, 01, 10, 11.",
        "Three switches: eight settings from 000 to 111.",
    ],
    prereqs=[
        ("recursion", "One call per position, two recursive calls per call."),
        ("backtracking", "Choose, explore, and — here — overwrite instead of undo."),
    ],
)


_p(
    "partition-k-equal", "Split the Loot Evenly", "Medium",
    topics=["Backtracking"], subtopics=["Backtracking", "Pruning", "Bitmask"],
    companies=["Google", "Amazon", "Meta"],
    shape="arr_k", ret="String",
    todo="target = sum / k; place items largest first into k buckets; skip a bucket whose current load equals an earlier bucket's",
    description=(
        "`k` friends want to split `n` treasures so that every friend gets the **same total "
        "value**. Every treasure must go to exactly one friend. Print `true` if it is possible, "
        "otherwise `false`.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` positive integers, the values.\n\n### Output\n"
        "`true` or `false`."
    ),
    constraints="1 ≤ k ≤ n ≤ 16\n1 ≤ value ≤ 10^4",
    hints=[
        "If the total is not divisible by k, or one treasure is worth more than total / k, the answer is false immediately.",
        "Place the treasures one at a time, trying each friend (bucket) that still has room. Sort largest first: big items fail fast.",
        "Two buckets with the same current load are interchangeable — trying the second one repeats the first's search. Skip it. This single rule is what makes the search finish.",
    ],
    opt=("O(kⁿ) worst case, far less with pruning", "O(n + k)",
         "The search tree is pruned by capacity, by sorting, and by skipping equal buckets. (A 2ⁿ · n bitmask DP also works.)"),
    editorial=(
        "## The one thing this teaches\n**Symmetry pruning.** Without it the search tries every "
        "labelling of the buckets — k! copies of each real partition. The bucket loop only needs "
        "to try each *distinct* load once.\n\n"
        "## Approach\n```java\nboolean place(int i) {                  // items sorted descending\n"
        "    if (i == n) return true;              // all placed, every bucket == target\n"
        "    for (int b = 0; b < k; b++) {\n        if (load[b] + a[i] > target) continue;\n"
        "        if (b > 0 && load[b] == load[b - 1]) continue;   // same as a bucket we tried\n"
        "        load[b] += a[i];\n        if (place(i + 1)) return true;\n        load[b] -= a[i];\n"
        "        if (load[b] == 0) break;          // an empty bucket failed: every empty one will\n    }\n"
        "    return false;\n}\n```\n\n"
        "## Why all buckets are full at the end\nEvery item was placed, no bucket exceeds the target, "
        "and the loads add up to k · target — so none can be below it either."
    ),
    py='''
def solve(a, k):
    total = sum(a)
    if total % k:
        return "false"
    t = total // k
    if max(a) > t:
        return "false"
    n = len(a)
    # bitmask DP: fill[mask] = load of the bucket being filled, or -1 if unreachable
    fill = [-1] * (1 << n)
    fill[0] = 0
    for mask in range(1 << n):
        if fill[mask] < 0:
            continue
        for i in range(n):
            if not mask >> i & 1 and fill[mask] + a[i] <= t:
                nxt = mask | 1 << i
                if fill[nxt] < 0:
                    fill[nxt] = (fill[mask] + a[i]) % t
    return "true" if fill[(1 << n) - 1] == 0 else "false"
''',
    java='''
    static int[] A, load;
    static int T, K;

    static boolean place(int i) {
        if (i == A.length) return true;
        for (int b = 0; b < K; b++) {
            if (load[b] + A[i] > T) continue;
            if (b > 0 && load[b] == load[b - 1]) continue;
            load[b] += A[i];
            if (place(i + 1)) return true;
            load[b] -= A[i];
            if (load[b] == 0) break;
        }
        return false;
    }

    static String solve(int[] a, long k) {
        int total = 0, mx = 0;
        for (int v : a) { total += v; mx = Math.max(mx, v); }
        K = (int) k;
        if (total % K != 0) return "false";
        T = total / K;
        if (mx > T) return "false";
        Integer[] boxed = new Integer[a.length];
        for (int i = 0; i < a.length; i++) boxed[i] = a[i];
        Arrays.sort(boxed, Collections.reverseOrder());
        A = new int[a.length];
        for (int i = 0; i < a.length; i++) A[i] = boxed[i];
        load = new int[K];
        return place(0) ? "true" : "false";
    }
''',
    examples=[
        ("Example 1", "6 3\n7 2 5 3 4 3\n"),
        ("Example 2", "4 2\n3 5 1 3\n"),
    ],
    hidden=[
        ("One friend", "3 1\n5 9 2\n"),
        ("Everyone gets one", "4 4\n6 6 6 6\n"),
        ("Not divisible", "3 2\n1 1 1\n"),
        ("One item too big", "4 2\n9 1 1 1\n"),
        ("Greedy fails", "6 2\n6 5 4 3 1 1\n"),
        ("Sixteen equal", "16 8\n" + " ".join(["3"] * 16) + "\n"),
        ("Sixteen, impossible", "16 4\n" + " ".join(map(str, [10] * 15 + [18])) + "\n"),
        ("Sixteen, tight", "16 4\n" + " ".join(map(str, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])) + "\n"),
        ("Sixteen random", "16 5\n" + " ".join(map(str, _lcg_ints(141, 16, 1, 40))) + "\n"),
    ],
    expl=[
        "The total is 24, so each friend needs 8. The 7 would need a 1 to reach 8, and there is none: false.",
        "The total is 12, so each needs 6: {5, 1} and {3, 3}.",
    ],
    prereqs=[
        ("backtracking", "Try each bucket for the next item, undo, and try the next."),
        ("pruning", "Capacity, largest-first ordering, and skipping equal buckets."),
    ],
)


_p(
    "map-colorings-count", "Colour the Map", "Medium",
    topics=["Backtracking", "Graph"], subtopics=["Backtracking", "Graph Coloring", "Constraint Search"],
    companies=["Google", "Microsoft"],
    shape="graph_k", ret="long",
    todo="colour regions 0..n-1 in order; for each, try every colour no already-coloured neighbour uses; count complete colourings",
    description=(
        "A map has `n` regions; some pairs share a border. Using `k` colours, how many ways can "
        "the regions be coloured so that no two bordering regions share a colour? Two colourings "
        "are different if any region gets a different colour.\n\n"
        "### Input\nLine 1: `n m k`.\nNext `m` lines: `u v`, a border between regions `u` and `v` "
        "(0-indexed).\n\n### Output\nThe number of valid colourings."
    ),
    constraints="1 ≤ n ≤ 10\n0 ≤ m ≤ 45, no repeated borders, no region borders itself\n1 ≤ k ≤ 4",
    hints=[
        "Colour the regions in index order. A colour is legal for region i if none of its already-coloured neighbours has it.",
        "When all n are coloured, count one. Return the sum over every legal colour of the count below it.",
        "Pruning is built in: an illegal colour is never descended into. Uncoloured neighbours do not constrain anything yet.",
    ],
    opt=("O(kⁿ) worst case", "O(n + m)",
         "At most kⁿ leaves, and far fewer when borders forbid colours early."),
    editorial=(
        "## The one thing this teaches\n**Feasibility pruning on a constraint graph.** The "
        "choices are colours, the constraint is \"differs from every coloured neighbour\", and the "
        "check happens *before* descending — so an impossible prefix never grows.\n\n"
        "## Approach\n```java\nlong count(int i) {\n    if (i == n) return 1;\n    long ways = 0;\n"
        "    for (int c = 0; c < k; c++) {\n        boolean ok = true;\n"
        "        for (int j : adj[i]) if (j < i && colour[j] == c) { ok = false; break; }\n"
        "        if (!ok) continue;\n        colour[i] = c;\n        ways += count(i + 1);\n    }\n"
        "    return ways;\n}\n```\n\n"
        "## Counting, not listing\nThe same search, returning a number. A triangle with 3 colours "
        "has 3 · 2 · 1 = 6 colourings; with 2 colours, none — the search discovers that by "
        "running out of colours at the third region."
    ),
    py='''
def solve(n, edges, k):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def count(i):
        if i == n:
            return 1
        ways = 0
        for c in range(k):
            if all(colour[j] != c for j in adj[i] if j < i):
                colour[i] = c
                ways += count(i + 1)
        colour[i] = -1
        return ways

    return count(0)
''',
    java='''
    static List<Integer>[] adj;
    static int[] colour;
    static int N, K;

    static long count(int i) {
        if (i == N) return 1;
        long ways = 0;
        for (int c = 0; c < K; c++) {
            boolean ok = true;
            for (int j : adj[i]) if (j < i && colour[j] == c) { ok = false; break; }
            if (!ok) continue;
            colour[i] = c;
            ways += count(i + 1);
        }
        colour[i] = -1;
        return ways;
    }

    @SuppressWarnings("unchecked")
    static long solve(int n, int[][] edges, int k) {
        N = n;
        K = k;
        adj = new List[n];
        for (int i = 0; i < n; i++) adj[i] = new ArrayList<>();
        for (int[] e : edges) { adj[e[0]].add(e[1]); adj[e[1]].add(e[0]); }
        colour = new int[n];
        Arrays.fill(colour, -1);
        return count(0);
    }
''',
    examples=[
        ("Example 1", "3 3 3\n0 1\n1 2\n2 0\n"),
        ("Example 2", "4 3 2\n0 1\n1 2\n2 3\n"),
    ],
    hidden=[
        ("One region", "1 0 4\n"),
        ("No borders", "5 0 3\n"),
        ("Triangle, two colours", "3 3 2\n0 1\n1 2\n0 2\n"),
        ("Four-cycle", "4 4 3\n0 1\n1 2\n2 3\n3 0\n"),
        ("Complete on four, four colours", "4 6 4\n0 1\n0 2\n0 3\n1 2\n1 3\n2 3\n"),
        ("Wheel", "6 10 4\n0 1\n0 2\n0 3\n0 4\n0 5\n1 2\n2 3\n3 4\n4 5\n5 1\n"),
        ("Random", _graph_k_case(10, _rand_graph(10, 15, _Lcg(151)), 4)),
        ("Dense", _graph_k_case(10, _rand_graph(10, 30, _Lcg(152)), 4)),
        ("Sparse ten", _graph_k_case(10, _rand_graph(10, 6, _Lcg(153)), 3)),
    ],
    expl=[
        "A triangle needs three different colours: 3 · 2 · 1 = 6 ways.",
        "A path of four with two colours alternates: pick the first region's colour, and the rest are forced — 2 ways.",
    ],
    prereqs=[
        ("backtracking", "Assign a colour, recurse, and move to the next colour on the way back."),
        ("graph_repr", "An adjacency list, so each region's neighbours can be checked."),
    ],
)


_p(
    "word-break-sentences", "Every Way to Read It", "Hard",
    topics=["Backtracking", "Dynamic Programming", "String"], subtopics=["Backtracking", "Memoization", "String"],
    companies=["Google", "Amazon", "Meta"],
    shape="str_list", ret="String",
    todo="first compute ok[i] = 'the suffix from i can be split'; then backtrack from 0, only stepping to positions j with ok[j]",
    description=(
        "A message lost its spaces. Given the string and a dictionary, print **every** way to "
        "put spaces back so that each piece is a dictionary word (a word may be used any number "
        "of times). Print the sentences in lexicographic order, one per line, or `NONE` if there "
        "are none.\n\n"
        "### Input\nLine 1: the string `s` (lowercase letters).\nLine 2: `d`, the number of "
        "dictionary words.\nNext `d` tokens: the words.\n\n### Output\nThe sentences, or `NONE`."
    ),
    constraints="1 ≤ |s| ≤ 24\n1 ≤ d ≤ 15, 1 ≤ word length ≤ 10\nThe number of sentences is at most 2000.",
    hints=[
        "Backtracking: at position i, try every word that s starts with at i, and recurse from the end of that word.",
        "Without pruning, a string like aaaa…ab explores exponentially many dead prefixes that can never finish.",
        "Compute ok[i] = \"s[i..] can be split\" right to left first (a word-break DP). Then only step to positions j where ok[j] is true — every branch you enter produces at least one sentence.",
    ],
    opt=("O(n² + total output)", "O(n + output)",
         "The DP is O(n² · d) at most; with it, the search does no work that does not end in a sentence."),
    editorial=(
        "## The one thing this teaches\n**Prune with a precomputed feasibility table.** Listing "
        "all answers is output-bound — you cannot beat the output size. What you *can* remove is "
        "every branch that produces nothing, and one right-to-left DP tells you exactly which "
        "positions are dead.\n\n"
        "## Approach\n```java\nok[n] = true;\nfor (int i = n - 1; i >= 0; i--)\n"
        "    for (String w : dict) if (s.startsWith(w, i) && ok[i + w.length()]) { ok[i] = true; break; }\n\n"
        "void dfs(int i) {\n    if (i == n) { out.add(String.join(\" \", path)); return; }\n"
        "    for (String w : dict)\n        if (s.startsWith(w, i) && ok[i + w.length()]) {\n"
        "            path.add(w); dfs(i + w.length()); path.remove(path.size() - 1);\n        }\n}\n```\n"
        "Sort the collected sentences at the end.\n\n"
        "## The adversarial input\n`aaaaaaaaaaaaaaaaaaaaaab` with words a, aa, aaa: millions of "
        "prefixes, zero sentences. With `ok[]`, the search never starts."
    ),
    py='''
def solve(s, words):
    n = len(s)
    dict_ = sorted(set(words))
    ok = [False] * (n + 1)
    ok[n] = True
    for i in range(n - 1, -1, -1):
        ok[i] = any(s.startswith(w, i) and ok[i + len(w)] for w in dict_)
    out, path = [], []

    def dfs(i):
        if i == n:
            out.append(" ".join(path))
            return
        for w in dict_:
            if s.startswith(w, i) and ok[i + len(w)]:
                path.append(w)
                dfs(i + len(w))
                path.pop()

    if ok[0]:
        dfs(0)
    return "\\n".join(sorted(out)) if out else "NONE"
''',
    java='''
    static String S;
    static String[] D;
    static boolean[] ok;
    static List<String> out = new ArrayList<>();
    static List<String> path = new ArrayList<>();

    static void dfs(int i) {
        if (i == S.length()) { out.add(String.join(" ", path)); return; }
        for (String w : D)
            if (S.startsWith(w, i) && ok[i + w.length()]) {
                path.add(w);
                dfs(i + w.length());
                path.remove(path.size() - 1);
            }
    }

    static String solve(String s, String[] words) {
        S = s;
        D = new TreeSet<>(Arrays.asList(words)).toArray(new String[0]);
        int n = s.length();
        ok = new boolean[n + 1];
        ok[n] = true;
        for (int i = n - 1; i >= 0; i--)
            for (String w : D)
                if (s.startsWith(w, i) && ok[i + w.length()]) { ok[i] = true; break; }
        if (ok[0]) dfs(0);
        if (out.isEmpty()) return "NONE";
        Collections.sort(out);
        return String.join("\\n", out);
    }
''',
    examples=[
        ("Example 1", "icecreamcone\n5 ice cream icecream cone am\n"),
        ("Example 2", "snowman\n3 snow mango sno\n"),
    ],
    hidden=[
        ("One word", "a\n1 a\n"),
        ("Repeated word", "abab\n2 ab a\n"),
        ("The adversarial dead end", "aaaaaaaaaaaaaaaaaaaaaaab\n3 a aa aaa\n"),
        ("Duplicate dictionary words", "gogo\n3 go go og\n"),
        ("Many sentences", "aaaaaaaaaa\n3 a aa aaa\n"),
        ("Overlapping words", "catsanddogs\n6 cat cats and sand dog dogs\n"),
        ("Long", "penpineapplepenapple\n6 apple pen applepen pine pineapple app\n"),
    ],
    expl=[
        "\"ice cream cone\" and \"icecream cone\" — sorted, the space (which sorts before letters) puts \"ice cream cone\" first.",
        "\"sno\" leaves \"wman\" and \"snow\" leaves \"man\"; neither can be finished.",
    ],
    prereqs=[
        ("backtracking", "Try every word that fits at the current position, recurse, and pop it."),
        ("dp", "A right-to-left table of which suffixes can be split, used to prune the search."),
    ],
)


_p(
    "expression-target-count", "Make the Number", "Hard",
    topics=["Backtracking", "Math"], subtopics=["Backtracking", "Expression Evaluation"],
    companies=["Google", "Meta", "Amazon"],
    shape="str_n", ret="long",
    todo="choose where the next operand ends and which operator precedes it; carry (value so far, last term) so '*' can undo the last term",
    description=(
        "A string of digits sits on a whiteboard. Between any two adjacent digits you may write "
        "`+`, `-`, `*`, or nothing (which glues the digits into one number). Count the ways to do "
        "this so that the expression, evaluated with the usual precedence (`*` before `+` and "
        "`-`), equals `target`.\n\n"
        "A number with more than one digit may not start with `0` (`05` is not allowed; `0` is). "
        "No operator may go before the first digit.\n\n"
        "### Input\nLine 1: the digit string and `target`, separated by a space.\n\n### Output\n"
        "The number of expressions."
    ),
    constraints="1 ≤ length ≤ 10\n-10^10 ≤ target ≤ 10^10",
    hints=[
        "Recurse over where the next operand ends. The first operand has no operator; each later one tries `+`, `-` and `*`.",
        "Multiplication binds tighter, so you cannot just keep a running total. Keep the running value *and* the last added term.",
        "For `*`: value − last + last · x, and the new last term is last · x. For `-`, the last term is −x. Use long: 10-digit operands overflow int.",
    ],
    opt=("O(4ⁿ⁻¹ · n)", "O(n)",
         "Every gap takes one of four choices; each leaf costs O(1) with the (value, last) trick."),
    editorial=(
        "## The one thing this teaches\n**Carry exactly the state the next step needs.** "
        "Re-evaluating each finished expression from its text costs O(n) per leaf and is easy to "
        "get wrong. Carrying (value, last) makes every step O(1) and puts precedence in one line.\n\n"
        "## Approach\n```java\nlong count(int i, long value, long last) {\n    if (i == n) return value == target ? 1 : 0;\n"
        "    long ways = 0, x = 0;\n    for (int j = i; j < n; j++) {\n        if (j > i && s.charAt(i) == '0') break;   // no leading zeros\n"
        "        x = x * 10 + (s.charAt(j) - '0');\n        if (i == 0) ways += count(j + 1, x, x);\n        else {\n"
        "            ways += count(j + 1, value + x, x);\n            ways += count(j + 1, value - x, -x);\n"
        "            ways += count(j + 1, value - last + last * x, last * x);\n        }\n    }\n    return ways;\n}\n```\n\n"
        "## Why `value − last + last · x`\nThe previous term was already added. Multiplying binds "
        "it to x, so take it back out and add the product instead."
    ),
    py='''
def solve(s, k):
    n, target = len(s), k

    def count(i, value, last):
        if i == n:
            return 1 if value == target else 0
        ways, x = 0, 0
        for j in range(i, n):
            if j > i and s[i] == "0":
                break
            x = x * 10 + int(s[j])
            if i == 0:
                ways += count(j + 1, x, x)
            else:
                ways += count(j + 1, value + x, x)
                ways += count(j + 1, value - x, -x)
                ways += count(j + 1, value - last + last * x, last * x)
        return ways

    return count(0, 0, 0)
''',
    java='''
    static String S;
    static long TARGET;

    static long count(int i, long value, long last) {
        int n = S.length();
        if (i == n) return value == TARGET ? 1 : 0;
        long ways = 0, x = 0;
        for (int j = i; j < n; j++) {
            if (j > i && S.charAt(i) == '0') break;
            x = x * 10 + (S.charAt(j) - '0');
            if (i == 0) ways += count(j + 1, x, x);
            else {
                ways += count(j + 1, value + x, x);
                ways += count(j + 1, value - x, -x);
                ways += count(j + 1, value - last + last * x, last * x);
            }
        }
        return ways;
    }

    static long solve(String s, long k) {
        S = s;
        TARGET = k;
        return count(0, 0, 0);
    }
''',
    examples=[
        ("Example 1", "124 6\n"),
        ("Example 2", "303 3\n"),
    ],
    hidden=[
        ("One digit, match", "7 7\n"),
        ("One digit, no match", "7 8\n"),
        ("Zeros", "000 0\n"),
        ("Glue only", "9999999999 9999999999\n"),
        ("Negative target", "12345 -13\n"),
        ("Ten digits", "1234567890 45\n"),
        ("Ten ones", "1111111111 1\n"),
        ("Zeros inside", "1050201 10\n"),
    ],
    expl=[
        "Only 1 * 2 + 4 reaches 6. For instance 1 + 2 + 4 = 7, 12 − 4 = 8 and 1 + 2 * 4 = 9.",
        "3 + 0 * 3, 3 − 0 * 3 and 3 * 0 + 3. Gluing 0 and 3 into 03 is not allowed.",
    ],
    prereqs=[
        ("backtracking", "At each gap, choose an operator (or glue) and recurse."),
        ("overflow", "Operands of up to ten digits and their products need long."),
    ],
)
