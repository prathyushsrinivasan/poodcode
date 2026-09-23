# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 58 — Trees & Graphs round 2, part 1: trees, BSTs, backtracking.
#
#   distribute-coins-tree   post-order flow: every edge carries |excess of the subtree below|
#   flip-equivalent-trees   pair recursion with two ways to match the children
#   longest-zigzag-tree     each call returns two lengths: arriving from the left or the right
#   tree-diameter-general   an unrooted weighted tree: the farthest node from the farthest node
#   bst-greater-sum         reverse in-order with a running sum
#   balance-bst             in-order to a sorted list, then the middle-first build
#   two-bst-pair-sum        an ascending iterator and a descending iterator, two pointers
#   letter-tile-sequences   backtracking over letter counts, not positions
#   n-queens-boards         the queens search, printing every board
#
# Uses the shapes and generators of dsa_more_53.py / dsa_more_54.py; defines
# `tree2_k`.
# ===========================================================================

# two tree lines, then an integer
_SHAPES["tree2_k"] = dict(
    py=_TREE_PY + "root2 = build(L[1].split())\nk = int(L[2])\n", py_params="root, root2, k",
    js=_TREE_JS + "const root2 = build(L[1].trim().split(/\\s+/).filter(Boolean));\nconst k = Number(L[2]);\n",
    js_params="root, root2, k",
    java_members=_TREE_JAVA_MEMBERS,
    java=_TREE_JAVA_READ + "        TreeNode root2 = build(sc.nextLine());\n"
         "        int k = Integer.parseInt(sc.nextLine().trim());\n",
    java_params="TreeNode root, TreeNode root2, int k", java_args="root, root2, k",
)


def _coins_line(n, seed):
    """A random tree whose coin counts add up to n."""
    rng = _Lcg(seed)
    left, right = _rand_tree(n, rng)
    coins = [0] * n
    for _ in range(n):
        coins[rng.randint(0, n - 1)] += 1
    return _level_of(coins, left, right)


def _flip_pair(n, seed, same=True):
    """A random tree with distinct values, and a copy with random child swaps
    (and, if not `same`, one value changed)."""
    rng = _Lcg(seed)
    left, right = _rand_tree(n, rng)
    vals = rng.shuffle(list(range(n)))
    a = _level_of(vals, left, right)
    l2, r2 = list(left), list(right)
    for i in range(n):
        if rng.randint(0, 1):
            l2[i], r2[i] = r2[i], l2[i]
    v2 = list(vals)
    if not same:
        i, j = rng.randint(0, n - 1), rng.randint(0, n - 1)
        while j == i and n > 1:
            j = rng.randint(0, n - 1)
        if n > 1:
            v2[i], v2[j] = v2[j], v2[i]
    return a + "\n" + _level_of(v2, l2, r2) + "\n"


_p(
    "distribute-coins-tree", "Pass the Coins Around", "Medium",
    topics=["Tree"], subtopics=["Tree", "Post-order", "Tree DP"],
    companies=["Google", "Amazon"],
    shape="tree", ret="long",
    todo="post-order: excess(v) = coins(v) + excess(children) - 1; every edge moves |excess of the child side| coins",
    description=(
        "Every node of a binary tree holds some coins, and there are exactly as many coins as "
        "nodes. In one move you pass one coin along one edge (parent to child or child to parent). "
        "Print the fewest moves that leave **exactly one coin on every node**.\n\n"
        "### Input\nOne line: the tree in level order, each value being that node's coins "
        "(`null` for a missing child).\n\n### Output\nThe fewest moves."
    ),
    constraints="1 ≤ nodes ≤ 3000\n0 ≤ coins ≤ nodes, and the coins add up to the number of nodes.",
    hints=[
        "Look at one edge between a node and its parent. How many coins must cross it, in either direction?",
        "Everything below that edge must end with one coin per node. If the subtree has c coins and s nodes, exactly |c − s| coins cross the edge.",
        "So compute excess(v) = coins(v) − 1 + excess(left) + excess(right) bottom-up and add |excess| for every non-root node.",
    ],
    opt=("O(n)", "O(h)",
         "One post-order pass; each edge's flow is decided by the subtree below it."),
    editorial=(
        "## The one thing this teaches\n**Count per edge, not per move.** Simulating coins is "
        "hopeless. But every edge splits the tree in two, and the side below must end balanced — "
        "so the number of coins crossing the edge is forced: |coins below − nodes below|.\n\n"
        "## Approach\n```java\nlong moves = 0;\nint excess(TreeNode n) {             // coins − nodes in this subtree\n"
        "    if (n == null) return 0;\n    int l = excess(n.left), r = excess(n.right);\n"
        "    moves += Math.abs(l) + Math.abs(r);  // flow on the two child edges\n"
        "    return n.val - 1 + l + r;\n}\n```\n\n"
        "## Why the sum is achievable\nEach edge's flow is forced, so the total is a lower bound; "
        "moving surplus up and deficits down along each edge achieves it exactly."
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
    ex, moves = {}, 0
    for n in reversed(order):
        l = ex[n.left] if n.left else 0
        r = ex[n.right] if n.right else 0
        moves += abs(l) + abs(r)
        ex[n] = n.val - 1 + l + r
    return moves
''',
    java='''
    static long moves = 0;

    static int excess(TreeNode n) {
        if (n == null) return 0;
        int l = excess(n.left), r = excess(n.right);
        moves += Math.abs(l) + Math.abs(r);
        return n.val - 1 + l + r;
    }

    static long solve(TreeNode root) {
        excess(root);
        return moves;
    }
''',
    examples=[
        ("Example 1", "0 2 0 null 2\n"),
        ("Example 2", "1 0 0 null 3\n"),
    ],
    hidden=[
        ("One node", "1\n"),
        ("Already balanced", "1 1 1 1 1\n"),
        ("Everything at the root", "5 0 0 0 0\n"),
        ("Everything at a deep leaf", _chain_line([0, 0, 0, 0, 5], "R") + "\n"),
        ("Random", _coins_line(60, 301) + "\n"),
        ("Large", _coins_line(3000, 302) + "\n"),
    ],
    expl=[
        "The spare coin at the bottom climbs to its parent (1 move), two coins go from there to the root (2), and the root passes one to its right child (1): 4.",
        "Two spare coins climb from the bottom node to its parent (2 moves), one of them continues to the root (1), and the root sends one down to its right child (1): 4.",
    ],
    prereqs=[
        ("tree_dp", "Each node returns its subtree's surplus; the parent adds the flow on each child edge."),
        ("recursion", "A post-order pass: children first, then the node."),
    ],
)


_p(
    "flip-equivalent-trees", "Mirror Moves", "Medium",
    topics=["Tree"], subtopics=["Tree", "Recursion", "Pair Recursion"],
    companies=["Google", "Microsoft"],
    shape="tree2", ret="String",
    todo="same(a, b): both null → true; one null or values differ → false; else (children match straight) OR (children match crossed)",
    description=(
        "A **flip** swaps the left and right children of one node. Two binary trees are "
        "*flip-equivalent* if some number of flips (on any nodes) turns the first into the "
        "second. All values within a tree are distinct. Print `true` or `false`.\n\n"
        "### Input\nLine 1: the first tree in level order.\nLine 2: the second tree.\n\n"
        "### Output\n`true` or `false`."
    ),
    constraints="1 ≤ nodes in each tree ≤ 2000\nValues within one tree are distinct, 0 ≤ value ≤ 10^4",
    hints=[
        "Compare the roots first: different values can never be fixed by flipping.",
        "Then the children match either straight (left–left, right–right) or crossed (left–right, right–left).",
        "With distinct values at most one of the two pairings can have matching child values, so the recursion does not blow up.",
    ],
    opt=("O(n)", "O(h)",
         "With distinct values, each pair of nodes is compared at most a constant number of times."),
    editorial=(
        "## The one thing this teaches\n**Pair recursion with a choice.** `same-tree` recurses on "
        "(left, left) and (right, right). Allowing flips adds a second way to pair the children; "
        "the answer is the OR of the two.\n\n"
        "## Approach\n```java\nboolean eq(TreeNode a, TreeNode b) {\n    if (a == null || b == null) return a == b;\n"
        "    if (a.val != b.val) return false;\n    return (eq(a.left, b.left) && eq(a.right, b.right))\n"
        "        || (eq(a.left, b.right) && eq(a.right, b.left));\n}\n```\n\n"
        "## Why it stays linear\nThe straight pairing fails at once unless the left children have "
        "the same value (or are both null), and with distinct values only one pairing can pass that "
        "test — so each call does real work in at most one branch."
    ),
    py='''
def solve(root, root2):
    sys.setrecursionlimit(20000)

    def eq(a, b):
        if a is None or b is None:
            return a is b
        if a.val != b.val:
            return False
        return (eq(a.left, b.left) and eq(a.right, b.right)) or \\
               (eq(a.left, b.right) and eq(a.right, b.left))

    return "true" if eq(root, root2) else "false"
''',
    java='''
    static boolean eq(TreeNode a, TreeNode b) {
        if (a == null || b == null) return a == b;
        if (a.val != b.val) return false;
        return (eq(a.left, b.left) && eq(a.right, b.right))
            || (eq(a.left, b.right) && eq(a.right, b.left));
    }

    static String solve(TreeNode root, TreeNode root2) {
        return eq(root, root2) ? "true" : "false";
    }
''',
    examples=[
        ("Example 1", "4 2 7 1 3 6 9\n4 7 2 9 6 1 3\n"),
        ("Example 2", "4 2 7\n4 2 9\n"),
    ],
    hidden=[
        ("Single nodes", "5\n5\n"),
        ("Different roots", "5 1\n6 1\n"),
        ("One flip at the root", "1 2\n1 null 2\n"),
        ("Shape differs", "1 2 3 4\n1 3 2 null null null 4\n"),
        ("Random equivalent", _flip_pair(200, 311, True)),
        ("Random not equivalent", _flip_pair(200, 312, False)),
        ("Large equivalent", _flip_pair(2000, 313, True)),
    ],
    expl=[
        "Flip the root (7 goes left), flip 7 (9 before 6); 2 keeps its children in order. That is the second tree: true.",
        "The roots match and 2 matches 2, but 7 has no partner: false.",
    ],
    prereqs=[
        ("tree_traversal", "Recursing on a pair of nodes at once."),
        ("recursion", "An OR of two recursive pairings."),
    ],
)


_p(
    "longest-zigzag-tree", "The Longest Zig-Zag", "Medium",
    topics=["Tree"], subtopics=["Tree", "Tree DP", "Depth-First Search"],
    companies=["Amazon", "Meta"],
    shape="tree", ret="int",
    todo="each node returns (a, b): the longest zig-zag starting here going left first, and going right first; a = 1 + right-first of the left child",
    description=(
        "A **zig-zag** path starts at any node and moves down, alternating direction: left, right, "
        "left, … or right, left, right, …. Its length is the number of edges. Print the length of "
        "the longest zig-zag in the tree (a single node alone is 0).\n\n"
        "### Input\nOne line: the tree in level order.\n\n### Output\nThe longest zig-zag length."
    ),
    constraints="1 ≤ nodes ≤ 3000",
    hints=[
        "A zig-zag that starts at node v by going left continues from v.left by going right.",
        "So let L(v) = longest zig-zag from v whose first step is left, R(v) = the same going right. L(v) = 1 + R(v.left) if v.left exists, else 0.",
        "Compute both bottom-up; the answer is the largest L or R anywhere.",
    ],
    opt=("O(n)", "O(h)",
         "Two numbers per node, one post-order pass."),
    editorial=(
        "## The one thing this teaches\n**Return a pair when the parent needs two answers.** A "
        "node's zig-zag depends on *which way* the child continues, so each call returns both "
        "continuations and the parent picks the one that alternates.\n\n"
        "## Approach\n```java\nint best = 0;\nint[] dfs(TreeNode n) {                  // {startLeft, startRight}\n"
        "    if (n == null) return new int[]{-1, -1};\n    int[] l = dfs(n.left), r = dfs(n.right);\n"
        "    int goLeft = l[1] + 1, goRight = r[0] + 1;    // −1 + 1 = 0 when the child is null\n"
        "    best = Math.max(best, Math.max(goLeft, goRight));\n    return new int[]{goLeft, goRight};\n}\n```\n\n"
        "## The −1 trick\nReturning −1 for null makes \"1 + (−1) = 0\" the length when the "
        "step is impossible, with no special case."
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
    res, best = {}, 0
    for n in reversed(order):
        gl = res[n.left][1] + 1 if n.left else 0
        gr = res[n.right][0] + 1 if n.right else 0
        res[n] = (gl, gr)
        best = max(best, gl, gr)
    return best
''',
    java='''
    static int best = 0;

    static int[] dfs(TreeNode n) {
        if (n == null) return new int[]{-1, -1};
        int[] l = dfs(n.left), r = dfs(n.right);
        int goLeft = l[1] + 1, goRight = r[0] + 1;
        best = Math.max(best, Math.max(goLeft, goRight));
        return new int[]{goLeft, goRight};
    }

    static int solve(TreeNode root) {
        dfs(root);
        return best;
    }
''',
    examples=[
        ("Example 1", "1 2 3 null 4 null null 5 6 null 7\n"),
        ("Example 2", "1 2 3\n"),
    ],
    hidden=[
        ("One node", "1\n"),
        ("A straight chain", _chain_line([1, 2, 3, 4, 5], "L") + "\n"),
        ("A perfect zig-zag", _chain_line(list(range(1, 11)), "Z") + "\n"),
        ("Random", _rand_tree_line(200, 321, 0, 9) + "\n"),
        ("Deep zig-zag", _chain_line(list(range(2000)), "Z") + "\n"),
        ("Large", _rand_tree_line(3000, 322, 0, 9) + "\n"),
    ],
    expl=[
        "1 → left 2 → right 4 → left 5 → right 7: four edges, alternating.",
        "Every path is a single step: 1.",
    ],
    prereqs=[
        ("tree_dp", "Each node returns two values: the zig-zag going left first and going right first."),
        ("recursion", "Post-order: both children before the node."),
    ],
)


def _wtree_case(n, seed, whi):
    rng = _Lcg(seed)
    edges = [(u, v, rng.randint(1, whi)) for u, v in _rand_tree_edges(n, rng)]
    return f"{n} {n - 1}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)


_p(
    "tree-diameter-general", "The Two Farthest Villages", "Medium",
    topics=["Tree", "Graph"], subtopics=["Tree", "Diameter", "Breadth-First Search"],
    companies=["Google", "Amazon"],
    shape="wgraph", ret="long",
    todo="from any node find the farthest node a; from a find the farthest node b; dist(a, b) is the diameter",
    description=(
        "`n` villages are joined by `n − 1` roads into a tree; road `u v w` is `w` kilometres long. "
        "Print the largest distance between any two villages.\n\n"
        "### Input\nLine 1: `n m` with `m = n − 1`.\nNext `m` lines: `u v w`.\n\n### Output\nThe largest distance."
    ),
    constraints="1 ≤ n ≤ 10^5\nm = n − 1, the roads form a tree\n1 ≤ w ≤ 10^4",
    hints=[
        "Distances from one village to all others are one traversal (a tree has one path between any two villages).",
        "Claim: the village farthest from ANY start is one end of a longest path.",
        "So traverse twice: from village 0 find the farthest a; from a, the farthest distance is the answer. Use an explicit stack — the tree can be a 10⁵-long path.",
    ],
    opt=("O(n)", "O(n)",
         "Two traversals; no recursion needed."),
    editorial=(
        "## The one thing this teaches\n**The double sweep.** For trees (and only trees), the "
        "farthest vertex from any start is an endpoint of a diameter. Two traversals replace n.\n\n"
        "## Approach\n```java\nlong[] d = distancesFrom(0);             // iterative DFS or BFS\nint a = argmax(d);\n"
        "long[] e = distancesFrom(a);\nreturn max(e);\n```\n\n"
        "## Versus the rooted version\n`diameter-of-tree` works on a rooted binary tree by returning "
        "heights. This tree has no root and any degree; the same \"return one, record another\" "
        "DP works too, but the double sweep needs no rooting at all."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    def far(s):
        dist = [-1] * n
        dist[s] = 0
        st = [s]
        while st:
            u = st.pop()
            for v, w in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + w
                    st.append(v)
        a = max(range(n), key=lambda i: dist[i])
        return a, dist[a]

    a, _ = far(0)
    _, d = far(a)
    return d
''',
    java='''
    static List<List<int[]>> adj = new ArrayList<>();

    static long[] far(int n, int s) {
        long[] dist = new long[n];
        Arrays.fill(dist, -1);
        dist[s] = 0;
        ArrayDeque<Integer> st = new ArrayDeque<>();
        st.push(s);
        while (!st.isEmpty()) {
            int u = st.pop();
            for (int[] e : adj.get(u))
                if (dist[e[0]] < 0) { dist[e[0]] = dist[u] + e[1]; st.push(e[0]); }
        }
        int a = 0;
        for (int i = 1; i < n; i++) if (dist[i] > dist[a]) a = i;
        return new long[]{a, dist[a]};
    }

    static long solve(int n, int[][] edges) {
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); adj.get(e[1]).add(new int[]{e[0], e[2]}); }
        long[] first = far(n, 0);
        return far(n, (int) first[0])[1];
    }
''',
    examples=[
        ("Example 1", "6 5\n0 1 3\n1 2 4\n1 3 2\n3 4 6\n3 5 1\n"),
        ("Example 2", "2 1\n0 1 7\n"),
    ],
    hidden=[
        ("One village", "1 0\n"),
        ("A star", "5 4\n0 1 5\n0 2 9\n0 3 2\n0 4 9\n"),
        ("A path", "5 4\n0 1 1\n1 2 1\n2 3 1\n3 4 1\n"),
        ("Random", _wtree_case(200, 331, 100)),
        ("Long path", "30000 29999\n" + "".join(f"{i} {i + 1} {(i * 7) % 100 + 1}\n" for i in range(29999))),
        ("Large", _wtree_case(30000, 332, 10000)),
    ],
    expl=[
        "2 → 1 → 3 → 4 is 4 + 2 + 6 = 12 km; no pair is farther apart.",
        "The only two villages are 7 km apart.",
    ],
    prereqs=[
        ("graph_repr", "An adjacency list of (neighbour, length) pairs."),
        ("tree_basics", "A tree has exactly one path between two vertices, so one traversal gives all distances."),
    ],
)


_p(
    "bst-greater-sum", "Every Value Plus Everything Bigger", "Medium",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Reverse In-order"],
    companies=["Amazon", "Meta"],
    shape="tree_out", ret="TreeNode",
    todo="walk the BST in reverse in-order (right, node, left) keeping a running sum; add it to each node",
    description=(
        "Replace every value in a BST of **distinct** values by that value plus the sum of every "
        "larger value in the tree. The shape does not change. Print the new tree in level order.\n\n"
        "### Input\nOne line: the BST in level order.\n\n### Output\nThe new tree in level order."
    ),
    constraints="1 ≤ nodes ≤ 3000\nValues are distinct, -10^4 ≤ value ≤ 10^4",
    hints=[
        "In-order visits values smallest first. Visiting right subtree, node, left subtree visits them largest first.",
        "Keep a running sum of everything visited so far — exactly the values larger than the current one.",
        "Add the node's value to the running sum, then write the sum into the node.",
    ],
    opt=("O(n)", "O(h)",
         "One reverse in-order walk."),
    editorial=(
        "## The one thing this teaches\n**In-order runs both ways.** Right-node-left is the "
        "descending order, and a running sum over a descending walk is a suffix sum over the "
        "sorted values — computed without ever building the sorted list.\n\n"
        "## Approach\n```java\nint run = 0;\nvoid walk(TreeNode n) {\n    if (n == null) return;\n"
        "    walk(n.right);\n    run += n.val;\n    n.val = run;\n    walk(n.left);\n}\n```"
    ),
    py='''
def solve(root):
    st, cur, run = [], root, 0
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.right
        cur = st.pop()
        run += cur.val
        cur.val = run
        cur = cur.left
    return root
''',
    java='''
    static TreeNode solve(TreeNode root) {
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        TreeNode cur = root;
        int run = 0;
        while (cur != null || !st.isEmpty()) {
            while (cur != null) { st.push(cur); cur = cur.right; }
            cur = st.pop();
            run += cur.val;
            cur.val = run;
            cur = cur.left;
        }
        return root;
    }
''',
    examples=[
        ("Example 1", _bst_line([5, 2, 9, 1, 4, 7]) + "\n"),
        ("Example 2", _bst_line([3, 1]) + "\n"),
    ],
    hidden=[
        ("One node", "-5\n"),
        ("Right chain", _bst_line([1, 2, 3, 4, 5]) + "\n"),
        ("Negatives", _bst_line([0, -5, 5, -8, -2, 2, 8]) + "\n"),
        ("Random", _bst_line([v - 150 for v in _perm(300, 341)]) + "\n"),
        ("Large", _bst_line([v * 3 - 4500 for v in _perm(3000, 342)]) + "\n"),
    ],
    expl=[
        "9 has nothing larger: 9. 7 becomes 7 + 9 = 16. 5 becomes 21, 4 becomes 25, 2 becomes 27, 1 becomes 28.",
        "3 stays 3; 1 becomes 1 + 3 = 4.",
    ],
    prereqs=[
        ("bst", "Right, node, left visits a BST's values in descending order."),
        ("prefix_sum", "A running sum over the descending walk is a suffix sum of the sorted values."),
    ],
)


_p(
    "balance-bst", "Rebalance the Tree", "Medium",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Divide and Conquer"],
    companies=["Amazon", "Microsoft"],
    shape="tree_out", ret="TreeNode",
    todo="collect the values in-order (sorted), then rebuild with the lower middle of each range as its root",
    description=(
        "A BST of **distinct** values has become lopsided. Rebuild it as a height-balanced BST "
        "holding the same values: take the sorted values, and make the root of each range "
        "`[lo, hi]` the element at `(lo + hi) / 2` (the lower middle), with the left and right "
        "halves built the same way.\n\n"
        "### Input\nOne line: the BST in level order.\n\n### Output\nThe rebuilt tree in level order."
    ),
    constraints="1 ≤ nodes ≤ 3000\nValues are distinct, -10^5 ≤ value ≤ 10^5",
    hints=[
        "The in-order of a BST is its values sorted — so step one is a traversal, not a sort.",
        "Then this is `sorted-array-to-bst`.",
        "The input may be a 3000-long chain: walk it iteratively.",
    ],
    opt=("O(n)", "O(n)",
         "One in-order walk into a list, one balanced build."),
    editorial=(
        "## The one thing this teaches\n**Rebalancing is two problems you already know.** "
        "In-order flattens a BST into a sorted list without sorting; the middle-first build turns "
        "a sorted list into a balanced tree. Self-balancing trees do this incrementally with "
        "rotations; offline, the two passes are simpler.\n\n"
        "## Approach\n```java\nList<Integer> vals = inorder(root);      // sorted\nreturn build(vals, 0, vals.size() - 1);  // lower middle\n```"
    ),
    py='''
def solve(root):
    vals, st, cur = [], [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        vals.append(cur.val)
        cur = cur.right

    def build(lo, hi):
        if lo > hi:
            return None
        m = (lo + hi) // 2
        n = TreeNode(vals[m])
        n.left = build(lo, m - 1)
        n.right = build(m + 1, hi)
        return n

    return build(0, len(vals) - 1)
''',
    java='''
    static List<Integer> vals = new ArrayList<>();

    static TreeNode build(int lo, int hi) {
        if (lo > hi) return null;
        int m = (lo + hi) >>> 1;
        TreeNode n = new TreeNode(vals.get(m));
        n.left = build(lo, m - 1);
        n.right = build(m + 1, hi);
        return n;
    }

    static TreeNode solve(TreeNode root) {
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        TreeNode cur = root;
        while (cur != null || !st.isEmpty()) {
            while (cur != null) { st.push(cur); cur = cur.left; }
            cur = st.pop();
            vals.add(cur.val);
            cur = cur.right;
        }
        return build(0, vals.size() - 1);
    }
''',
    examples=[
        ("Example 1", _bst_line([1, 2, 3, 4, 5]) + "\n"),
        ("Example 2", _bst_line([8, 4, 12]) + "\n"),
    ],
    hidden=[
        ("One node", "7\n"),
        ("Left chain", _bst_line([6, 5, 4, 3, 2, 1]) + "\n"),
        ("Zig-zag", _bst_line([1, 9, 2, 8, 3, 7, 4, 6, 5]) + "\n"),
        ("Random", _bst_line(_perm(300, 351)) + "\n"),
        ("Long chain", _bst_line(list(range(3000))) + "\n"),
    ],
    expl=[
        "The chain 1 → 2 → 3 → 4 → 5 becomes 3 at the root, 1 (with 2 on its right) and 4 (with 5 on its right).",
        "Already balanced, and the rule rebuilds the same tree.",
    ],
    prereqs=[
        ("bst", "In-order produces the values sorted."),
        ("recursion", "The middle-first build on index ranges."),
    ],
)


def _two_bst_case(n1, n2, seed, k):
    rng = _Lcg(seed)
    a = rng.shuffle(list(range(-n1, 2 * n1, 3)))[:n1]
    b = rng.shuffle(list(range(-n2 + 1, 2 * n2, 2)))[:n2]
    return _bst_line(a) + "\n" + _bst_line(b) + "\n" + str(k) + "\n"


_p(
    "two-bst-pair-sum", "One From Each Tree", "Medium",
    topics=["Tree", "Binary Search Tree", "Two Pointers"], subtopics=["BST Iterator", "Two Pointers"],
    companies=["Amazon", "Google"],
    shape="tree2_k", ret="long",
    todo="an ascending iterator over the first BST and a descending one over the second; move them like two pointers on sorted arrays",
    description=(
        "Two BSTs each hold **distinct** values. Count the pairs `(a, b)` with `a` from the first "
        "tree, `b` from the second, and `a + b = k`.\n\n"
        "### Input\nLine 1: the first BST in level order.\nLine 2: the second BST.\nLine 3: `k`.\n\n"
        "### Output\nThe number of pairs."
    ),
    constraints="1 ≤ nodes in each tree ≤ 5000\nValues distinct within each tree, |value| ≤ 10^5\n|k| ≤ 2·10^5",
    hints=[
        "A hash set of one tree's values works in O(n) extra memory. Can you use the order instead?",
        "Two sorted lists and a target sum is the two-pointer pattern: one pointer at the smallest of the first, one at the largest of the second.",
        "You do not need the lists: an ascending BST iterator and a descending one (push right spines) walk them in O(h) memory.",
    ],
    opt=("O(n1 + n2)", "O(h1 + h2)",
         "Each iterator step is amortised O(1)."),
    editorial=(
        "## The one thing this teaches\n**A BST is two iterators.** Push left spines and you get "
        "ascending order; push right spines and you get descending. Two pointers on sorted data "
        "then work directly on the trees.\n\n"
        "## Approach\n```java\nwhile (a != null && b != null) {         // a ascending in tree 1, b descending in tree 2\n"
        "    int s = a.val + b.val;\n    if (s == k) { count++; a = nextAsc(); b = nextDesc(); }\n"
        "    else if (s < k) a = nextAsc();\n    else b = nextDesc();\n}\n```\n\n"
        "## Why both pointers move on a match\nValues are distinct within each tree, so a matched "
        "`a` cannot pair with any other `b`, and vice versa."
    ),
    py='''
def solve(root, root2, k):
    asc, desc = [], []

    def push_left(n):
        while n:
            asc.append(n)
            n = n.left

    def push_right(n):
        while n:
            desc.append(n)
            n = n.right

    def next_asc():
        if not asc:
            return None
        n = asc.pop()
        push_left(n.right)
        return n

    def next_desc():
        if not desc:
            return None
        n = desc.pop()
        push_right(n.left)
        return n

    push_left(root)
    push_right(root2)
    a, b, count = next_asc(), next_desc(), 0
    while a and b:
        s = a.val + b.val
        if s == k:
            count += 1
            a, b = next_asc(), next_desc()
        elif s < k:
            a = next_asc()
        else:
            b = next_desc()
    return count
''',
    java='''
    static ArrayDeque<TreeNode> asc = new ArrayDeque<>(), desc = new ArrayDeque<>();

    static TreeNode nextAsc() {
        if (asc.isEmpty()) return null;
        TreeNode n = asc.pop();
        for (TreeNode c = n.right; c != null; c = c.left) asc.push(c);
        return n;
    }

    static TreeNode nextDesc() {
        if (desc.isEmpty()) return null;
        TreeNode n = desc.pop();
        for (TreeNode c = n.left; c != null; c = c.right) desc.push(c);
        return n;
    }

    static long solve(TreeNode root, TreeNode root2, int k) {
        for (TreeNode c = root; c != null; c = c.left) asc.push(c);
        for (TreeNode c = root2; c != null; c = c.right) desc.push(c);
        TreeNode a = nextAsc(), b = nextDesc();
        long count = 0;
        while (a != null && b != null) {
            long s = (long) a.val + b.val;
            if (s == k) { count++; a = nextAsc(); b = nextDesc(); }
            else if (s < k) a = nextAsc();
            else b = nextDesc();
        }
        return count;
    }
''',
    examples=[
        ("Example 1", _bst_line([5, 2, 8, 1]) + "\n" + _bst_line([4, 3, 7, 6]) + "\n9\n"),
        ("Example 2", "3\n" + "4\n" + "1\n"),
    ],
    hidden=[
        ("Single nodes, match", "3\n4\n7\n"),
        ("Negative target", _bst_line([-5, -9, 0]) + "\n" + _bst_line([-1, -4, 2]) + "\n-9\n"),
        ("Every pair matches once", _bst_line([1, 2, 3, 4]) + "\n" + _bst_line([6, 7, 8, 9]) + "\n10\n"),
        ("Random", _two_bst_case(300, 300, 361, 30)),
        ("Large", _two_bst_case(5000, 5000, 362, 500)),
    ],
    expl=[
        "(2, 7) and (5, 4). The first tree's 1 and 8 would need 8 and 1 from the second, which it does not have.",
        "3 + 4 = 7, not 1: no pairs.",
    ],
    prereqs=[
        ("bst", "Ascending and descending BST iterators with explicit stacks."),
        ("two_pointers", "Two sorted sequences and a target sum."),
    ],
)


_p(
    "letter-tile-sequences", "Words From Tiles", "Medium",
    topics=["Backtracking"], subtopics=["Backtracking", "Counting", "Duplicates"],
    companies=["Amazon", "Google"],
    shape="str", ret="long",
    todo="count letters; recurse: for each letter with count > 0, use one (count++ result), recurse, give it back",
    description=(
        "You have some letter tiles (letters may repeat). Count the different **non-empty** "
        "sequences of letters you can lay out, using each tile at most once. Two sequences are the "
        "same if they spell the same string.\n\n"
        "### Input\nOne line: the tiles as a string of uppercase letters.\n\n### Output\nThe number of different sequences."
    ),
    constraints="1 ≤ tiles ≤ 8\nUppercase letters A–Z",
    hints=[
        "Generating sequences position by position from the *tiles* produces duplicates whenever two tiles are the same letter.",
        "Recurse over *letters* instead: keep a count per letter. At each step, try each letter that still has tiles left.",
        "Every choice extends the sequence by one, so every call (except the first) is one new, distinct sequence — count calls.",
    ],
    opt=("O(number of sequences)", "O(26 + n)",
         "Each distinct sequence is produced exactly once."),
    editorial=(
        "## The one thing this teaches\n**Deduplicate by the choice set, not by the output.** "
        "Iterating over distinct letters with counts means two equal tiles are never two different "
        "choices — the search produces each string once, with no set of seen strings.\n\n"
        "## Approach\n```java\nint count(int[] freq) {\n    int total = 0;\n    for (int c = 0; c < 26; c++) {\n"
        "        if (freq[c] == 0) continue;\n        freq[c]--;\n        total += 1 + count(freq);   // this sequence, plus every extension\n"
        "        freq[c]++;\n    }\n    return total;\n}\n```"
    ),
    py='''
def solve(s):
    freq = [0] * 26
    for ch in s:
        freq[ord(ch) - 65] += 1

    def count():
        total = 0
        for c in range(26):
            if freq[c]:
                freq[c] -= 1
                total += 1 + count()
                freq[c] += 1
        return total

    return count()
''',
    java='''
    static int[] freq = new int[26];

    static long count() {
        long total = 0;
        for (int c = 0; c < 26; c++) {
            if (freq[c] == 0) continue;
            freq[c]--;
            total += 1 + count();
            freq[c]++;
        }
        return total;
    }

    static long solve(String s) {
        for (char ch : s.toCharArray()) freq[ch - 'A']++;
        return count();
    }
''',
    examples=[
        ("Example 1", "ABB\n"),
        ("Example 2", "Z\n"),
    ],
    hidden=[
        ("All the same", "QQQQ\n"),
        ("All different", "ABCD\n"),
        ("Two pairs", "AABB\n"),
        ("Eight different", "ABCDEFGH\n"),
        ("Eight with repeats", "AAABBBCC\n"),
    ],
    expl=[
        "A, B, AB, BA, BB, ABB, BAB, BBA: 8.",
        "Just Z.",
    ],
    prereqs=[
        ("backtracking", "Choose a letter, recurse, return the tile."),
        ("hashing", "Counting tiles per letter so equal tiles are one choice."),
    ],
)


_p(
    "n-queens-boards", "Every Queens Board", "Hard",
    topics=["Backtracking"], subtopics=["Backtracking", "Constraint Placement"],
    companies=["Amazon", "Microsoft", "Google"],
    shape="n", ret="String",
    todo="place a queen row by row, trying columns left to right; track columns and both diagonals; print each full board",
    description=(
        "Place `n` queens on an `n × n` board so that no two attack each other (same row, column "
        "or diagonal). Print the number of solutions, then every solution as `n` lines of `.` and "
        "`Q`, with a line `-` before each board.\n\n"
        "List the solutions in this order: place queens row by row from the top, trying columns "
        "from left to right — the order a backtracking search finds them.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe count, then the boards."
    ),
    constraints="1 ≤ n ≤ 8",
    hints=[
        "One queen per row, so the choice at row r is only the column.",
        "A column is safe when no earlier queen shares its column, its ↘ diagonal (r − c) or its ↙ diagonal (r + c). Three boolean arrays make that O(1).",
        "Build each row's string only when a board is complete.",
    ],
    opt=("O(n!) (pruned)", "O(n)",
         "Far fewer than n! placements survive the diagonal checks: 92 boards for n = 8."),
    editorial=(
        "## The one thing this teaches\n**Constraint placement with O(1) feasibility.** The "
        "search is the backtracking template; what makes it fast is that a diagonal is a line "
        "where r − c (or r + c) is constant, so \"is it attacked?\" is three array lookups.\n\n"
        "## Approach\n```java\nvoid place(int r) {\n    if (r == n) { record(pos); return; }\n    for (int c = 0; c < n; c++) {\n"
        "        if (col[c] || d1[r - c + n] || d2[r + c]) continue;\n        col[c] = d1[r - c + n] = d2[r + c] = true;  pos[r] = c;\n"
        "        place(r + 1);\n        col[c] = d1[r - c + n] = d2[r + c] = false;\n    }\n}\n```"
    ),
    py='''
def solve(n):
    col, d1, d2 = [False] * n, [False] * (2 * n), [False] * (2 * n)
    pos, boards = [0] * n, []

    def place(r):
        if r == n:
            boards.append("\\n".join("." * c + "Q" + "." * (n - 1 - c) for c in pos))
            return
        for c in range(n):
            if col[c] or d1[r - c + n] or d2[r + c]:
                continue
            col[c] = d1[r - c + n] = d2[r + c] = True
            pos[r] = c
            place(r + 1)
            col[c] = d1[r - c + n] = d2[r + c] = False

    place(0)
    return "\\n".join([str(len(boards))] + ["-\\n" + b for b in boards])
''',
    java='''
    static int N;
    static boolean[] col, d1, d2;
    static int[] pos;
    static List<String> boards = new ArrayList<>();

    static void place(int r) {
        if (r == N) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < N; i++) {
                if (i > 0) sb.append('\\n');
                for (int c = 0; c < N; c++) sb.append(pos[i] == c ? 'Q' : '.');
            }
            boards.add(sb.toString());
            return;
        }
        for (int c = 0; c < N; c++) {
            if (col[c] || d1[r - c + N] || d2[r + c]) continue;
            col[c] = d1[r - c + N] = d2[r + c] = true;
            pos[r] = c;
            place(r + 1);
            col[c] = d1[r - c + N] = d2[r + c] = false;
        }
    }

    static String solve(long n) {
        N = (int) n;
        col = new boolean[N];
        d1 = new boolean[2 * N];
        d2 = new boolean[2 * N];
        pos = new int[N];
        place(0);
        StringBuilder out = new StringBuilder().append(boards.size());
        for (String b : boards) out.append("\\n-\\n").append(b);
        return out.toString();
    }
''',
    examples=[
        ("Example 1", "4\n"),
        ("Example 2", "3\n"),
    ],
    hidden=[
        ("One", "1\n"),
        ("Two", "2\n"),
        ("Five", "5\n"),
        ("Six", "6\n"),
        ("Eight", "8\n"),
    ],
    expl=[
        "Two boards: queens in columns 1, 3, 0, 2 and in 2, 0, 3, 1.",
        "No placement of three queens works on a 3 × 3 board.",
    ],
    prereqs=[
        ("backtracking", "One queen per row; place, recurse, remove."),
        ("pruning", "Three occupancy arrays make every feasibility check O(1)."),
    ],
)
