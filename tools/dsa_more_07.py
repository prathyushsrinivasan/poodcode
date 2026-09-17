# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 7 — binary search trees and shortest paths.
#
#   range-sum-bst             prune subtrees the order property rules out
#   bst-min-difference        in-order is sorted, so the answer is between neighbours
#   bst-successor             one walk down, remembering the last left turn
#   recover-bst               two swapped values are the ends of the in-order descents
#   count-shortest-paths      Dijkstra that carries a count alongside each distance
#   min-obstacle-removal      0-1 BFS: a deque instead of a heap
#   bellman-ford-negative     relax V−1 times, then once more to detect a negative cycle
#   swim-in-rising-water      Dijkstra minimising the maximum instead of the sum
# ===========================================================================

_p(
    "range-sum-bst", "Range Sum of a BST", "Easy",
    topics=["Trees"], subtopics=["BST", "Tree DFS"], companies=["Meta", "Google"],
    shape="tree_xy", ret="long", todo="DFS, skipping the left subtree when val < lo and the right when val > hi",
    description=(
        "Sum the values of all nodes of a **binary search tree** that lie in `[lo, hi]`.\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child (empty for an empty tree).\n"
        "- Line 2: `lo hi`.\n\n"
        "### Output\nThe sum."
    ),
    constraints="0 ≤ nodes ≤ 2·10^4\nValues are distinct, 1 ≤ value ≤ 10^5\n1 ≤ lo ≤ hi ≤ 10^5",
    hints=[
        "Visiting every node works in O(n). The BST property lets you skip whole subtrees.",
        "If node.val < lo, nothing in its LEFT subtree can be in range. If node.val > hi, nothing in its right subtree can.",
        "Use an explicit stack if the tree may be deep.",
    ],
    opt=("O(n)", "O(h)", "Worst case every node is in range; pruning cuts it to the nodes near the range."),
    editorial=(
        "## The one thing this teaches\n**The order property prunes.** A plain tree sum visits "
        "every node. In a BST, a node below `lo` has a left subtree that is *entirely* below `lo`, "
        "so that whole subtree can be skipped without looking.\n\n"
        "## Approach\n```java\nlong sum = 0;\nDeque<TreeNode> st = new ArrayDeque<>();\n"
        "if (root != null) st.push(root);\nwhile (!st.isEmpty()) {\n    TreeNode t = st.pop();\n"
        "    if (t.val >= lo && t.val <= hi) sum += t.val;\n"
        "    if (t.left != null && t.val > lo) st.push(t.left);     // left can hold values > lo only if t.val > lo\n"
        "    if (t.right != null && t.val < hi) st.push(t.right);\n}\n```\n\n"
        "## Pricing it honestly\nThe worst case is still O(n) — a range covering the whole tree "
        "visits everything. The pruning makes it proportional to the nodes in range plus the "
        "O(h) boundary paths, which is the same shape as a range query in any ordered structure."
    ),
    py='''
def solve(root, x, y):
    total = 0
    st = [root] if root else []
    while st:
        t = st.pop()
        if x <= t.val <= y:
            total += t.val
        if t.left and t.val > x:
            st.append(t.left)
        if t.right and t.val < y:
            st.append(t.right)
    return total
''',
    java='''
    static long solve(TreeNode root, int lo, int hi) {
        long sum = 0;
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        if (root != null) st.push(root);
        while (!st.isEmpty()) {
            TreeNode t = st.pop();
            if (t.val >= lo && t.val <= hi) sum += t.val;
            if (t.left != null && t.val > lo) st.push(t.left);
            if (t.right != null && t.val < hi) st.push(t.right);
        }
        return sum;
    }
''',
    examples=[("Example 1", "10 5 15 3 7 null 18\n7 15\n"), ("Example 2", "10 5 15 3 7 13 18 1 null 6\n6 10\n")],
    hidden=[
        ("Single node", "5\n1 10\n"),
        ("Empty tree", "\n1 2\n"),
        ("Range above every value", "4 2 6 1 3 5 7\n8 9\n"),
        ("Range covers everything", "4 2 6 1 3 5 7\n1 7\n"),
    ],
    expl=[
        "7 + 10 + 15 = 32.",
        "6 + 7 + 10 = 23.",
    ],
    prereqs=[
        ("bst", "Left subtrees hold smaller values and right subtrees larger, so out-of-range subtrees are skipped."),
        ("tree_traversal", "A DFS with an explicit stack visiting only the subtrees that can contribute."),
    ],
)

_p(
    "bst-min-difference", "Minimum Difference in a BST", "Easy",
    topics=["Trees"], subtopics=["BST", "Tree DFS"], companies=["Google"],
    shape="tree", ret="int", todo="walk in order, comparing each value with the previous one",
    description=(
        "Find the minimum absolute difference between the values of **any two nodes** of a binary "
        "search tree.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe minimum difference."
    ),
    constraints="2 ≤ nodes ≤ 10^4\n0 ≤ value ≤ 10^5, values distinct",
    hints=[
        "Comparing every pair is O(n²).",
        "An in-order traversal of a BST visits values in sorted order.",
        "In a sorted list, the closest pair is always adjacent. Keep the previous value while walking.",
    ],
    opt=("O(n)", "O(h)", "One in-order walk carrying the previous value."),
    editorial=(
        "## The one thing this teaches\n**In-order is sorted order.** Any question about "
        "neighbouring values — closest pair, duplicates, validity — becomes a question about a "
        "sorted sequence the moment you walk a BST in order, and sorted sequences are easy.\n\n"
        "## Approach\n```java\nInteger prev = null;\nint best = Integer.MAX_VALUE;\n"
        "Deque<TreeNode> st = new ArrayDeque<>();\nTreeNode cur = root;\n"
        "while (cur != null || !st.isEmpty()) {\n    while (cur != null) { st.push(cur); cur = cur.left; }\n"
        "    cur = st.pop();\n    if (prev != null) best = Math.min(best, cur.val - prev);\n"
        "    prev = cur.val;\n    cur = cur.right;\n}\n```\n\n"
        "## Why neighbours are enough\nIf `a < b < c` then `c − a > b − a`, so the pair `(a, c)` "
        "can never beat `(a, b)`. The minimum is found among adjacent values — the same argument "
        "as sorting an array and scanning neighbours, with the tree providing the sort for free.\n\n"
        "## The common wrong answer\nComparing each node only with its children misses pairs "
        "like a node and the leftmost node of its right subtree."
    ),
    py='''
def solve(root):
    st, cur = [], root
    prev = None
    best = float("inf")
    while cur or st:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        if prev is not None:
            best = min(best, cur.val - prev)
        prev = cur.val
        cur = cur.right
    return best
''',
    java='''
    static int solve(TreeNode root) {
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        TreeNode cur = root;
        Integer prev = null;
        int best = Integer.MAX_VALUE;
        while (cur != null || !st.isEmpty()) {
            while (cur != null) { st.push(cur); cur = cur.left; }
            cur = st.pop();
            if (prev != null) best = Math.min(best, cur.val - prev);
            prev = cur.val;
            cur = cur.right;
        }
        return best;
    }
''',
    examples=[("Example 1", "4 2 6 1 3\n"), ("Example 2", "1 0 48 null null 12 49\n")],
    hidden=[
        ("Three nodes", "10 5 20\n"),
        ("Left chain", "100 50 null 20 null 10\n"),
        ("Closest pair across the root", "5 1 9 null 4 7\n"),
    ],
    expl=[
        "In order: 1 2 3 4 6. Neighbours differ by 1.",
        "In order: 0 1 12 48 49 — both 0/1 and 48/49 differ by 1.",
    ],
    prereqs=[
        ("bst", "An in-order walk of a BST visits the values in sorted order."),
        ("tree_traversal", "Iterative in-order traversal with an explicit stack."),
    ],
)

_p(
    "bst-successor", "Successor in a BST", "Medium",
    topics=["Trees"], subtopics=["BST"], companies=["Microsoft", "Meta"],
    shape="tree_k", ret="int", todo="walk down: when val > k record it and go left, otherwise go right",
    description=(
        "Given a binary search tree and a value `k` (which may or may not be in the tree), find "
        "the **smallest value in the tree strictly greater than `k`**.\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child.\n- Line 2: `k`.\n\n"
        "### Output\nThe successor, or `-1` if there is none."
    ),
    constraints="1 ≤ nodes ≤ 10^4\n0 ≤ value, k ≤ 10^5, values distinct",
    hints=[
        "An in-order walk finds it in O(n). Aim for O(h).",
        "At each node: if node.val > k, it is a candidate — but something smaller might still be in its left subtree.",
        "So record it and go left; otherwise go right. The last recorded candidate is the answer.",
    ],
    opt=("O(h)", "O(1)", "One root-to-leaf walk."),
    editorial=(
        "## The one thing this teaches\n**A search that remembers its best guess.** Searching "
        "for `k` in a BST walks one path. Every node on that path larger than `k` is a successor "
        "candidate, and each later candidate is smaller than the earlier ones (it was found by "
        "going left). So the answer is simply the last candidate seen.\n\n"
        "## Approach\n```java\nint succ = -1;\nwhile (root != null) {\n"
        "    if (root.val > k) { succ = root.val; root = root.left; }\n"
        "    else root = root.right;\n}\nreturn succ;\n```\n\n"
        "## Why `k` need not be in the tree\nThe walk never tests equality. It follows the path "
        "where `k` *would* be, and the successor of a missing value is the smallest value above "
        "where it would sit — the same thing the loop computes.\n\n"
        "Swap `>` for `<` and `left` for `right` and it finds the predecessor; replace the strict "
        "comparison and it finds a ceiling. `TreeMap.higherKey` is this loop."
    ),
    py='''
def solve(root, k):
    succ = -1
    while root:
        if root.val > k:
            succ = root.val
            root = root.left
        else:
            root = root.right
    return succ
''',
    java='''
    static int solve(TreeNode root, int k) {
        int succ = -1;
        while (root != null) {
            if (root.val > k) { succ = root.val; root = root.left; }
            else root = root.right;
        }
        return succ;
    }
''',
    examples=[("Example 1", "5 3 8 2 4 7 9\n4\n"), ("Example 2", "5 3 8 2 4 7 9\n9\n")],
    hidden=[
        ("Successor is in the right subtree", "5 3 8 2 4 7 9\n5\n"),
        ("Below every value", "5 3 8 2 4 7 9\n0\n"),
        ("Value not in the tree", "5 3 8 2 4 7 9\n6\n"),
        ("Tiny tree", "2 1 3\n1\n"),
    ],
    expl=[
        "The walk records 5, then goes left to 3 and right to 4, neither above 4.",
        "Nothing is larger than 9.",
    ],
    prereqs=[
        ("bst", "Each comparison sends the search left or right, and larger values seen on the way are candidates."),
        ("binary_search", "The same 'record the candidate and narrow' shape as finding a lower bound."),
    ],
)

_p(
    "recover-bst", "Recover a BST (Find the Swapped Values)", "Medium",
    topics=["Trees"], subtopics=["BST", "Tree DFS"], companies=["Amazon", "Microsoft"],
    shape="tree", ret="String", todo="walk in order; the first descent gives the larger swapped value, the last descent the smaller",
    description=(
        "Exactly **two nodes** of a binary search tree had their values swapped by mistake. Find "
        "those two values.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe two swapped values, smaller first, separated by a space."
    ),
    constraints="2 ≤ nodes ≤ 1000\nValues are distinct.\nExactly two values are out of place.",
    hints=[
        "The in-order sequence of a valid BST is increasing. Swapping two values breaks that in one or two places.",
        "A descent is a pair prev > cur. If the swapped values were adjacent in order there is one descent; otherwise two.",
        "The first swapped value is prev at the FIRST descent; the second is cur at the LAST descent.",
    ],
    opt=("O(n)", "O(h)", "One in-order walk; Morris traversal makes the space O(1)."),
    editorial=(
        "## The one thing this teaches\n**Reduce a tree problem to a sorted-array problem.** In "
        "order, the tree is an array that should be increasing. Swapping two elements of an "
        "increasing array produces descents, and where the descents are tells you exactly which "
        "two were swapped.\n\n"
        "## The two cases\n- `1 2 **4** 3 5` — adjacent swap: one descent `4 > 3`. The values are "
        "that pair.\n"
        "- `1 **5** 3 4 **2**` — distant swap: descents `5 > 3` and `4 > 2`. The large value is the "
        "*first* descent's left side; the small value is the *last* descent's right side.\n\n"
        "One rule covers both: `first = prev` at the first descent, `second = cur` at every "
        "descent (so the last one wins).\n\n"
        "## Approach\n```java\nwhile (walking in order) {\n"
        "    if (prev != null && prev.val > cur.val) {\n"
        "        if (first == null) first = prev;\n        second = cur;\n    }\n    prev = cur;\n}\n```\n\n"
        "To *repair* the tree, swap `first.val` and `second.val`. The follow-up asks for O(1) "
        "space, which means Morris in-order traversal instead of a stack."
    ),
    py='''
def solve(root):
    st, cur = [], root
    prev = first = second = None
    while cur or st:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        if prev is not None and prev > cur.val:
            if first is None:
                first = prev
            second = cur.val
        prev = cur.val
        cur = cur.right
    return f"{min(first, second)} {max(first, second)}"
''',
    java='''
    static String solve(TreeNode root) {
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        TreeNode cur = root, prev = null, first = null, second = null;
        while (cur != null || !st.isEmpty()) {
            while (cur != null) { st.push(cur); cur = cur.left; }
            cur = st.pop();
            if (prev != null && prev.val > cur.val) {
                if (first == null) first = prev;
                second = cur;
            }
            prev = cur;
            cur = cur.right;
        }
        return Math.min(first.val, second.val) + " " + Math.max(first.val, second.val);
    }
''',
    examples=[("Example 1", "1 3 null null 2\n"), ("Example 2", "3 1 4 null null 2\n")],
    hidden=[
        ("Root swapped with a leaf", "2 3 1\n"),
        ("Distant swap", "5 8 3 2 4 7 9\n"),
        ("Adjacent in order", "5 2 6 1 3 4 7\n"),
    ],
    expl=[
        "In order the tree reads 3 2 1: 3 and 1 were swapped.",
        "In order: 1 3 2 4 — one descent, so 3 and 2 were swapped.",
    ],
    prereqs=[
        ("bst", "In a valid BST the in-order sequence is strictly increasing."),
        ("tree_traversal", "An in-order walk that tracks the previous node to find descents."),
    ],
)

_p(
    "count-shortest-paths", "Number of Shortest Paths", "Medium",
    topics=["Graphs"], subtopics=["Dijkstra", "Counting"], companies=["Google", "Amazon"],
    shape="wgraph", ret="long", todo="Dijkstra from 0 carrying ways[v]; a strictly shorter path resets it, an equal one adds",
    description=(
        "An undirected weighted graph has `n` nodes. How many **different shortest paths** lead "
        "from node `0` to node `n − 1`? Print the count modulo `10^9 + 7`.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v w`, an undirected road of length `w`.\n\n"
        "### Output\nThe number of shortest paths, mod `10^9 + 7`."
    ),
    constraints="1 ≤ n ≤ 200\n0 ≤ m ≤ n(n−1)/2\n1 ≤ w ≤ 10^9\nNode n − 1 is reachable from node 0.",
    hints=[
        "Run Dijkstra from 0. Alongside dist[v], keep ways[v]: the number of shortest paths reaching v.",
        "When relaxing u → v: a strictly shorter distance replaces ways[v] with ways[u]; an equal one adds ways[u].",
        "Only use a node once its distance is final (skip stale heap entries), or its count may still grow.",
    ],
    opt=("O((n + m) log n)", "O(n + m)", "Dijkstra with a heap; each relaxation also updates a count in O(1)."),
    editorial=(
        "## The one thing this teaches\n**Carry more than a distance.** Dijkstra processes nodes "
        "in order of final distance, so when a node is popped, every shortest path to it has "
        "already been counted. That ordering is what makes it safe to push a count forward, just "
        "as it is safe to push a distance.\n\n"
        "## Approach\n```java\nlong[] dist = new long[n];  Arrays.fill(dist, Long.MAX_VALUE);\n"
        "long[] ways = new long[n];\ndist[0] = 0; ways[0] = 1;\n"
        "// pop (d, u); skip if d > dist[u]\nfor (int[] e : adj.get(u)) {\n"
        "    long nd = d + e[1];\n"
        "    if (nd < dist[e[0]]) { dist[e[0]] = nd; ways[e[0]] = ways[u]; pq.add(...); }\n"
        "    else if (nd == dist[e[0]]) ways[e[0]] = (ways[e[0]] + ways[u]) % MOD;\n}\n```\n\n"
        "## The bug\nProcessing a stale heap entry — a node popped again with an old, larger "
        "distance — adds its count to neighbours a second time. The `d > dist[u]` skip is not an "
        "optimisation here; it is correctness.\n\n"
        "Distances need a `long`: 200 edges of 10⁹ is past `int`."
    ),
    py='''
def solve(n, edges):
    MOD = 10 ** 9 + 7
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float("inf")
    dist = [INF] * n
    ways = [0] * n
    dist[0] = 0
    ways[0] = 1
    h = [(0, 0)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                ways[v] = ways[u]
                heapq.heappush(h, (nd, v))
            elif nd == dist[v]:
                ways[v] = (ways[v] + ways[u]) % MOD
    return ways[n - 1] % MOD
''',
    java='''
    static long solve(int n, int[][] edges) {
        final long MOD = 1_000_000_007L;
        List<List<long[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new long[]{e[1], e[2]}); adj.get(e[1]).add(new long[]{e[0], e[2]}); }
        long[] dist = new long[n], ways = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[0] = 0; ways[0] = 1;
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.add(new long[]{0, 0});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            if (top[0] > dist[u]) continue;
            for (long[] e : adj.get(u)) {
                int v = (int) e[0];
                long nd = top[0] + e[1];
                if (nd < dist[v]) { dist[v] = nd; ways[v] = ways[u]; pq.add(new long[]{nd, v}); }
                else if (nd == dist[v]) ways[v] = (ways[v] + ways[u]) % MOD;
            }
        }
        return ways[n - 1] % MOD;
    }
''',
    examples=[
        ("Example 1", "7 10\n0 6 7\n0 1 2\n1 2 3\n1 3 3\n6 3 3\n3 5 1\n6 5 1\n2 5 1\n0 4 5\n4 6 2\n"),
        ("Example 2", "2 1\n1 0 10\n"),
    ],
    hidden=[
        ("Two equal routes", "3 3\n0 1 1\n1 2 1\n0 2 2\n"),
        ("Start is the end", "1 0\n"),
        ("Diamond", "4 4\n0 1 1\n0 2 1\n1 3 1\n2 3 1\n"),
        ("Diamond plus a direct road", "5 7\n0 1 1\n0 2 1\n1 3 1\n2 3 1\n3 4 1\n0 4 3\n2 4 5\n"),
    ],
    expl=[
        "The shortest distance to 6 is 7, reached four ways: directly, 0→4→6, 0→1→2→5→6, 0→1→3→5→6.",
        "One road.",
    ],
    prereqs=[
        ("dijkstra", "Nodes finalised in distance order, so counts can be pushed forward safely."),
        ("modulo", "The number of shortest paths grows exponentially and is reported modulo 1e9+7."),
    ],
)

_p(
    "min-obstacle-removal", "Minimum Obstacles to Remove", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["BFS", "Grid"], companies=["Google"],
    shape="grid", ret="int", todo="0-1 BFS: stepping onto 0 costs nothing (push front), onto 1 costs one (push back)",
    description=(
        "In a grid of `0` (empty) and `1` (obstacle), move up, down, left or right from the top-left "
        "cell to the bottom-right cell. Walking through an obstacle means removing it. What is the "
        "minimum number of obstacles to remove?\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n"
        "### Output\nThe minimum number of removals."
    ),
    constraints="1 ≤ r, c ≤ 10^3 and r·c ≤ 10^5\nThe start and end cells are 0.",
    hints=[
        "This is a shortest path where entering a cell costs 0 or 1.",
        "Dijkstra works. But with only two possible weights, a deque does the heap's job.",
        "Pop from the front. A move of cost 0 goes on the front, a move of cost 1 on the back.",
    ],
    opt=("O(r·c)", "O(r·c)", "0-1 BFS: each cell is settled once and pushed at most a small number of times."),
    editorial=(
        "## The one thing this teaches\n**0-1 BFS.** Dijkstra needs a heap because edge weights "
        "vary. With weights of only 0 and 1, the deque stays sorted by distance for free: a 0-edge "
        "keeps the same distance, so it goes to the front with the other nodes at that distance; "
        "a 1-edge is one more, so it goes to the back.\n\n"
        "## Approach\n```java\nint[][] dist = new int[r][c];   // filled with MAX\n"
        "Deque<int[]> dq = new ArrayDeque<>();\ndist[0][0] = 0;\ndq.add(new int[]{0, 0});\n"
        "while (!dq.isEmpty()) {\n    int[] cur = dq.pollFirst();\n    for (each neighbour (x, y)) {\n"
        "        int nd = dist[cur[0]][cur[1]] + (g[x][y] == '1' ? 1 : 0);\n"
        "        if (nd < dist[x][y]) {\n            dist[x][y] = nd;\n"
        "            if (g[x][y] == '1') dq.addLast(new int[]{x, y}); else dq.addFirst(new int[]{x, y});\n"
        "        }\n    }\n}\n```\n\n"
        "## Why plain BFS is wrong\nBFS counts moves, and here moves are free — a long detour "
        "around an obstacle beats a short path through one. Distances must be measured in "
        "removals, and that needs the weighted search."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    INF = float("inf")
    dist = [[INF] * c for _ in range(r)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        x, y = dq.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < r and 0 <= ny < c:
                w = 1 if g[nx][ny] == "1" else 0
                if dist[x][y] + w < dist[nx][ny]:
                    dist[nx][ny] = dist[x][y] + w
                    if w:
                        dq.append((nx, ny))
                    else:
                        dq.appendleft((nx, ny))
    return dist[r - 1][c - 1]
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length;
        int[][] dist = new int[r][c];
        for (int[] row : dist) Arrays.fill(row, Integer.MAX_VALUE);
        dist[0][0] = 0;
        ArrayDeque<int[]> dq = new ArrayDeque<>();
        dq.add(new int[]{0, 0});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!dq.isEmpty()) {
            int[] cur = dq.pollFirst();
            for (int[] d : dirs) {
                int x = cur[0] + d[0], y = cur[1] + d[1];
                if (x < 0 || y < 0 || x >= r || y >= c) continue;
                int w = g[x][y] == '1' ? 1 : 0;
                if (dist[cur[0]][cur[1]] + w < dist[x][y]) {
                    dist[x][y] = dist[cur[0]][cur[1]] + w;
                    if (w == 1) dq.addLast(new int[]{x, y}); else dq.addFirst(new int[]{x, y});
                }
            }
        }
        return dist[r - 1][c - 1];
    }
''',
    examples=[("Example 1", "3 3\n011\n110\n110\n"), ("Example 2", "3 5\n01000\n01010\n00010\n")],
    hidden=[
        ("Single cell", "1 1\n0\n"),
        ("One wall either way", "2 2\n01\n10\n"),
        ("A row of obstacles", "1 5\n01110\n"),
        ("Detour beats digging", "3 4\n0100\n0110\n0000\n"),
    ],
    expl=[
        "Every route crosses at least two obstacles.",
        "Down the left column, along to column 2, up to the top row and across to the right edge: no removals.",
    ],
    prereqs=[
        ("bfs", "A deque-based BFS where 0-cost moves go to the front and 1-cost moves to the back."),
        ("dijkstra", "The weighted shortest-path idea, with the heap replaced because only two weights exist."),
    ],
)

_p(
    "bellman-ford-negative", "Shortest Paths With Negative Edges", "Medium",
    topics=["Graphs"], subtopics=["Bellman-Ford"], companies=["Goldman Sachs", "Google"],
    shape="wgraph", ret="String", todo="relax every edge n−1 times from node 0; if one more pass still improves something, report the cycle",
    description=(
        "A directed graph has edge weights that may be **negative**. Find the shortest distance "
        "from node `0` to every node.\n\n"
        "If a **negative cycle** is reachable from node 0 — so distances can decrease forever — "
        "print `NEGATIVE CYCLE` instead.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v w`, an edge `u → v` of weight `w`.\n\n"
        "### Output\nThe `n` distances separated by spaces, `INF` for unreachable nodes — or `NEGATIVE CYCLE`."
    ),
    constraints="1 ≤ n ≤ 500\n0 ≤ m ≤ 5000\n-10^4 ≤ w ≤ 10^4",
    hints=[
        "Dijkstra is wrong with negative edges: a node it finalises can later be improved.",
        "A shortest path without cycles has at most n − 1 edges. Relaxing every edge n − 1 times finds all of them.",
        "Relax once more. Any improvement means a reachable negative cycle. Never relax from a node still at INF.",
    ],
    opt=("O(n·m)", "O(n)", "n − 1 rounds over all m edges, plus one detection round."),
    editorial=(
        "## The one thing this teaches\n**Bellman–Ford, and why it needs n − 1 rounds.** After "
        "round k, every node whose shortest path uses at most k edges has its final distance — "
        "each round extends correct paths by one edge. With n nodes a simple path has at most "
        "n − 1 edges, so n − 1 rounds suffice. If round n still improves something, the \"shortest\" "
        "path is not simple: it contains a negative cycle.\n\n"
        "## Approach\n```java\nlong[] dist = new long[n];  Arrays.fill(dist, INF);  dist[0] = 0;\n"
        "for (int round = 0; round < n - 1; round++)\n    for (int[] e : edges)\n"
        "        if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) dist[e[1]] = dist[e[0]] + e[2];\n"
        "for (int[] e : edges)\n"
        "    if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) return \"NEGATIVE CYCLE\";\n```\n\n"
        "## Two details\n- **The `INF` guard.** Without it, `INF + (−5)` is a finite-looking number "
        "and unreachable nodes \"improve\". It also means a negative cycle nobody can reach is "
        "correctly ignored.\n"
        "- **Early exit.** If a round changes nothing, later rounds cannot either; stop. That "
        "makes it fast on most inputs without changing the worst case."
    ),
    py='''
def solve(n, edges):
    INF = float("inf")
    dist = [INF] * n
    dist[0] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return "NEGATIVE CYCLE"
    return " ".join("INF" if d == INF else str(d) for d in dist)
''',
    java='''
    static String solve(int n, int[][] edges) {
        final long INF = Long.MAX_VALUE;
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        dist[0] = 0;
        for (int round = 0; round < n - 1; round++) {
            boolean changed = false;
            for (int[] e : edges)
                if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
            if (!changed) break;
        }
        for (int[] e : edges)
            if (dist[e[0]] != INF && dist[e[0]] + e[2] < dist[e[1]]) return "NEGATIVE CYCLE";
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(' '); sb.append(dist[i] == INF ? "INF" : String.valueOf(dist[i])); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4 4\n0 1 4\n0 2 5\n1 2 -3\n2 3 4\n"),
        ("Example 2", "3 3\n0 1 1\n1 2 -1\n2 1 -1\n"),
    ],
    hidden=[
        ("Unreachable node", "3 1\n0 1 -5\n"),
        ("Single node", "1 0\n"),
        ("Negative cycle nobody can reach", "4 3\n0 1 2\n2 3 -1\n3 2 -1\n"),
        ("Textbook graph", "5 10\n0 1 6\n0 3 7\n1 2 5\n1 3 8\n1 4 -4\n2 1 -2\n3 2 -3\n3 4 9\n4 0 2\n4 2 7\n"),
    ],
    expl=[
        "0 → 1 → 2 costs 4 − 3 = 1, cheaper than the direct 5. Node 3 is then 1 + 4 = 5.",
        "1 → 2 → 1 has total weight −2 and is reachable from 0.",
    ],
    prereqs=[
        ("bellman_ford", "Relaxing every edge n − 1 times, then once more to detect a negative cycle."),
        ("graph_repr", "An edge list is all Bellman–Ford needs; no adjacency list is built."),
    ],
)

_p(
    "swim-in-rising-water", "Swim in Rising Water", "Hard",
    topics=["Graphs", "Matrix"], subtopics=["Dijkstra", "Grid"], companies=["Google", "Amazon"],
    shape="matrix", ret="int", todo="Dijkstra where a path's cost is its highest cell, not its sum",
    description=(
        "An `n × n` grid gives the elevation of each cell. At time `t` the water level is `t`, and "
        "you can swim between adjacent cells (up, down, left, right) if **both** are at elevation "
        "`≤ t`. Swimming takes no time. What is the least `t` at which you can get from the "
        "top-left to the bottom-right cell?\n\n"
        "### Input\n- Line 1: `n n`.\n- Next `n` lines: `n` elevations.\n\n"
        "### Output\nThe minimum time."
    ),
    constraints="1 ≤ n ≤ 50\n0 ≤ elevation < n², all distinct",
    hints=[
        "A route is possible at time t exactly when every cell on it is at most t. So the cost of a route is its HIGHEST cell.",
        "You want the route whose maximum is smallest — a minimax path.",
        "Dijkstra still works if a path's cost is max(cost so far, next cell) instead of a sum. Binary search on t with a BFS also works.",
    ],
    opt=("O(n² log n)", "O(n²)", "Dijkstra over n² cells with a heap."),
    editorial=(
        "## The one thing this teaches\n**Dijkstra needs monotone costs, not sums.** Its proof "
        "only uses the fact that extending a path never makes it cheaper. `max(cost, next)` has "
        "that property just as `cost + weight` does with non-negative weights, so the same "
        "algorithm finds the path whose highest point is lowest.\n\n"
        "## Approach\n```java\nPriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);   // {cost, r, c}\n"
        "pq.add(new int[]{grid[0][0], 0, 0});\nseen[0][0] = true;\nwhile (true) {\n"
        "    int[] cur = pq.poll();\n    if (cur[1] == n - 1 && cur[2] == n - 1) return cur[0];\n"
        "    for (each unseen neighbour (x, y)) {\n        seen[x][y] = true;\n"
        "        pq.add(new int[]{Math.max(cur[0], grid[x][y]), x, y});\n    }\n}\n```\n\n"
        "## Two other routes to the same answer\n- **Binary search on t**: \"can I cross at time "
        "t?\" is monotone and answered by a BFS, so O(n² log n²).\n"
        "- **Union–find**: add cells in increasing elevation and stop when the corners join — "
        "Kruskal's algorithm stopped early.\n\n"
        "The start cell's own elevation counts: you cannot begin before the water reaches it."
    ),
    py='''
def solve(m):
    n = len(m)
    seen = [[False] * n for _ in range(n)]
    seen[0][0] = True
    h = [(m[0][0], 0, 0)]
    while h:
        t, x, y = heapq.heappop(h)
        if x == n - 1 and y == n - 1:
            return t
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < n and 0 <= ny < n and not seen[nx][ny]:
                seen[nx][ny] = True
                heapq.heappush(h, (max(t, m[nx][ny]), nx, ny))
    return -1
''',
    java='''
    static int solve(int[][] m) {
        int n = m.length;
        boolean[][] seen = new boolean[n][n];
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        pq.add(new int[]{m[0][0], 0, 0});
        seen[0][0] = true;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!pq.isEmpty()) {
            int[] cur = pq.poll();
            if (cur[1] == n - 1 && cur[2] == n - 1) return cur[0];
            for (int[] d : dirs) {
                int x = cur[1] + d[0], y = cur[2] + d[1];
                if (x < 0 || y < 0 || x >= n || y >= n || seen[x][y]) continue;
                seen[x][y] = true;
                pq.add(new int[]{Math.max(cur[0], m[x][y]), x, y});
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", "2 2\n0 2\n1 3\n"),
        ("Example 2", "5 5\n0 1 2 3 4\n24 23 22 21 5\n12 13 14 15 16\n11 17 18 19 20\n10 9 8 7 6\n"),
    ],
    hidden=[
        ("Single cell", "1 1\n0\n"),
        ("Go around the peak", "3 3\n0 5 4\n1 8 3\n2 7 6\n"),
        ("Start is high", "2 2\n3 0\n1 2\n"),
    ],
    expl=[
        "The bottom-right cell is 3, so nothing earlier works.",
        "The route spirals along the border and the lowest possible highest point on it is 16.",
    ],
    prereqs=[
        ("dijkstra", "Dijkstra with a path cost of 'highest cell so far', which is still monotone."),
        ("heap", "A min-heap of frontier cells ordered by that cost."),
    ],
)
