# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 39 — the roadmap's tree-query gap: preprocess once, answer q times.
#
#   ancestor-queries      Euler tour: a subtree is a contiguous [tin, tout)
#   kth-ancestor-queries  binary lifting: jump 2^k at a time
#   tree-lca-queries      the same table, used to meet in the middle
#   tree-path-distance    depth[a] + depth[b] - 2 * depth[lca], on a weighted tree
#
# `trees` already teaches the O(n) one-off LCA recursion. Everything here is the
# other question: the tree is fixed and the queries keep coming, so the work
# moves out of the query and into a preprocessing pass.
# ===========================================================================

_p(
    "ancestor-queries", "Is It Above You?", "Easy",
    topics=["Trees", "Graphs"], subtopics=["Euler Tour", "DFS", "Tree Queries"],
    companies=["Amazon", "Google"],
    shape="tree_q", ret="String",
    todo="one DFS recording tin[v] and tout[v]; a is an ancestor of b iff tin[a] <= tin[b] and tout[b] <= tout[a]",
    description=(
        "A company org chart is a tree of `n` employees numbered `0 … n-1`, rooted at the "
        "founder, employee `0`. For each of `q` questions `a b`, answer whether `a` is **above** "
        "`b` in the chart — that is, whether `a` lies on the path from the founder down to `b`. "
        "Everybody counts as being above themselves.\n\n"
        "### Input\nLine 1: `n q`.\nNext `n-1` lines: `u v`, an edge of the tree.\n"
        "Next `q` lines: `a b`.\n\n"
        "### Output\nOne line per question: `YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ q ≤ 200000\n0 ≤ u, v, a, b < n\nThe edges form a tree.",
    hints=[
        "Walking up from b to the root answers one question, but a chain of 200000 employees with 200000 questions makes that 4·10¹⁰ steps.",
        "Do a single DFS from the root and stamp each node twice: `tin[v]` when you arrive, `tout[v]` when you leave. Every descendant of v is entered *and* left between those two stamps.",
        "So the subtree of `a` is exactly the nodes whose interval nests inside a's: `tin[a] ≤ tin[b]` and `tout[b] ≤ tout[a]`. Two comparisons per question.",
    ],
    opt=("O(n + q)", "O(n)",
         "One DFS to stamp entry and exit times, then two integer comparisons per question."),
    editorial=(
        "## The one thing this teaches\n**A DFS flattens a tree into an array, and a subtree "
        "becomes a contiguous range of it.** That is the Euler tour, and it converts \"is this "
        "inside that subtree?\" — a walk — into \"does this interval nest inside that one?\" "
        "— two comparisons.\n\n"
        "## Approach\n```java\nint timer = 0;\nvoid dfs(int u, int parent) {\n"
        "    tin[u] = timer++;\n    for (int w : g[u]) if (w != parent) dfs(w, u);\n"
        "    tout[u] = timer++;\n}\n\nboolean isAncestor(int a, int b) {\n"
        "    return tin[a] <= tin[b] && tout[b] <= tout[a];\n}\n```\n\n"
        "## Why it is correct\nA DFS leaves `u` only after it has entered and left every node "
        "below `u`, so every descendant's whole interval sits inside `[tin[u], tout[u]]`. A node "
        "*not* below `u` is either entered before `u` was and left before `u` was entered, or "
        "entered after `u` was left — disjoint either way. Nesting and descent are the same "
        "relation.\n\n"
        "## Watch the recursion depth\nA path graph of 200000 nodes recurses 200000 deep, which "
        "overflows the default Java stack. The reference uses an explicit stack; a recursive "
        "version needs a thread with a bigger stack.\n\n"
        "## What this unlocks\nOnce a subtree is a range, every array technique applies to it: "
        "subtree sums become prefix sums, subtree updates become range updates, and a "
        "\"k-th in subtree\" query becomes a range query."
    ),
    py='''
def solve(n, edges, queries):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    tin = [0] * n
    tout = [0] * n
    timer = 0
    st = [(0, -1, 0)]
    while st:
        u, p, state = st.pop()
        if state == 0:
            tin[u] = timer
            timer += 1
            st.append((u, p, 1))
            for w in reversed(g[u]):
                if w != p:
                    st.append((w, u, 0))
        else:
            tout[u] = timer
            timer += 1
    out = []
    for a, b in queries:
        out.append("YES" if tin[a] <= tin[b] and tout[b] <= tout[a] else "NO")
    return "\\n".join(out)
''',
    java='''
    static String solve(int n, int[][] edges, int[][] queries) {
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        int[] tin = new int[n], tout = new int[n], parent = new int[n], iter = new int[n];
        int timer = 0;
        int[] stack = new int[n + 1];
        int top = 0;
        stack[top] = 0;
        parent[0] = -1;
        tin[0] = timer++;
        while (top >= 0) {
            int u = stack[top];
            if (iter[u] < g.get(u).size()) {
                int w = g.get(u).get(iter[u]++);
                if (w == parent[u]) continue;
                parent[w] = u;
                tin[w] = timer++;
                stack[++top] = w;
            } else {
                tout[u] = timer++;
                top--;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < queries.length; i++) {
            int a = queries[i][0], b = queries[i][1];
            if (i > 0) sb.append('\\n');
            sb.append(tin[a] <= tin[b] && tout[b] <= tout[a] ? "YES" : "NO");
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "7 5\n0 1\n0 2\n1 3\n1 4\n2 5\n5 6\n0 6\n1 5\n2 6\n3 3\n4 1\n"),
        ("Example 2", "2 2\n0 1\n1 0\n0 1\n"),
    ],
    hidden=[
        ("Single node", "1 1\n0 0\n"),
        ("A chain", "5 4\n0 1\n1 2\n2 3\n3 4\n0 4\n4 0\n2 3\n3 1\n"),
        ("A star", "5 4\n0 1\n0 2\n0 3\n0 4\n1 2\n0 3\n2 2\n4 0\n"),
        ("Two deep branches", "9 6\n0 1\n1 2\n2 3\n0 4\n4 5\n5 6\n6 7\n0 8\n1 3\n4 3\n0 7\n5 7\n8 8\n3 2\n"),
    ],
    expl=[
        "6 sits under 5 under 2 under the founder, so 0 and 2 are both above it. 1 and 5 are in different branches. Everyone is above themselves.",
        "The founder is above employee 1, and employee 1 is above nobody but itself.",
    ],
    prereqs=[
        ("tree_traversal", "A DFS that does work on the way in and on the way out."),
        ("intervals", "Containment of one interval in another."),
    ],
)


_p(
    "kth-ancestor-queries", "Climb k Levels", "Medium",
    topics=["Trees", "Dynamic Programming"], subtopics=["Binary Lifting", "Tree Queries"],
    companies=["Google", "Meta"],
    shape="tree_q", ret="String",
    todo="up[0][v] = parent; up[k][v] = up[k-1][up[k-1][v]]; then read the bits of k and jump",
    description=(
        "The same org chart: a tree of `n` employees rooted at `0`. Each of `q` questions is "
        "`a k`, and asks who sits exactly `k` levels above employee `a`. The 0-th ancestor of "
        "a node is the node itself. If there is no such employee (the climb runs past the "
        "founder), answer `-1`.\n\n"
        "### Input\nLine 1: `n q`.\nNext `n-1` lines: `u v`, an edge of the tree.\n"
        "Next `q` lines: `a k`.\n\n"
        "### Output\nOne line per question: the ancestor's number, or `-1`."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ q ≤ 200000\n0 ≤ a < n\n0 ≤ k ≤ n\nThe edges form a tree.",
    hints=[
        "Following parent pointers k times is O(k) per question, and a chain of 200000 nodes makes that far too slow.",
        "Precompute jumps of *power-of-two* length: `up[0][v]` is v's parent, and `up[j][v]` is the node 2^j levels up — which is 2^(j-1) levels up, twice.",
        "Every k is a sum of distinct powers of two. Walk the bits of k: when bit j is set, jump with up[j]. At most 18 jumps for n = 200000.",
    ],
    opt=("O((n + q) log n)", "O(n log n)",
         "A table of log n jump levels, built once; each question reads the bits of k."),
    editorial=(
        "## The one thing this teaches\n**Binary lifting: precompute the jumps of length 1, 2, "
        "4, 8 … and any jump becomes at most log n of them.** It is exponentiation by "
        "squaring, applied to \"follow a pointer\" instead of \"multiply\".\n\n"
        "## Approach\n```java\nint LOG = 1;\nwhile ((1 << LOG) < n) LOG++;\nLOG++;\n\n"
        "int[][] up = new int[LOG][n];\nup[0] = parent;                       // -1 at the root\n"
        "for (int j = 1; j < LOG; j++)\n    for (int v = 0; v < n; v++) {\n"
        "        int mid = up[j - 1][v];\n        up[j][v] = mid < 0 ? -1 : up[j - 1][mid];\n"
        "    }\n\nint jump(int v, int k) {\n"
        "    for (int j = 0; k > 0 && v >= 0; j++, k >>= 1)\n"
        "        if ((k & 1) == 1) v = up[j][v];\n    return v;\n}\n```\n\n"
        "## Why the table is built level by level\n`up[j]` needs `up[j-1]` *complete*, because a "
        "2^j jump is two 2^(j-1) jumps and the second one starts wherever the first landed. "
        "Filling j in the outer loop guarantees that; swapping the loops does not.\n\n"
        "## The -1 sentinel\nOnce a jump runs off the top, everything above it is also off the "
        "top, so `-1` has to absorb further jumps rather than crash — hence the "
        "`mid < 0 ? -1 : …` in the build and the `v >= 0` in the loop.\n\n"
        "## Why powers of two\nAny k written in binary is a sum of distinct powers of two, so "
        "any climb is a sequence of at most ⌈log₂ n⌉ precomputed jumps. Storing "
        "*every* jump length would be O(n²) memory; storing the powers is O(n log n) and "
        "spans all of them."
    ),
    py='''
def solve(n, edges, queries):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    LOG = 1
    while (1 << LOG) < max(2, n):
        LOG += 1
    LOG += 1
    par = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for w in g[u]:
            if not seen[w]:
                seen[w] = True
                par[w] = u
                order.append(w)
    up = [par]
    for j in range(1, LOG):
        prev = up[j - 1]
        cur = [-1] * n
        for v in range(n):
            mid = prev[v]
            cur[v] = -1 if mid < 0 else prev[mid]
        up.append(cur)
    out = []
    for a, k in queries:
        v, rest, j = a, k, 0
        while rest > 0 and v >= 0:
            if j >= LOG:
                v = -1
                break
            if rest & 1:
                v = up[j][v]
            rest >>= 1
            j += 1
        out.append(str(v if v is not None and v >= 0 else -1))
    return "\\n".join(out)
''',
    java='''
    static String solve(int n, int[][] edges, int[][] queries) {
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        int LOG = 1;
        while ((1 << LOG) < Math.max(2, n)) LOG++;
        LOG++;
        int[][] up = new int[LOG][n];
        for (int[] row : up) Arrays.fill(row, -1);
        int[] order = new int[n];
        boolean[] seen = new boolean[n];
        int head = 0, tail = 0;
        order[tail++] = 0;
        seen[0] = true;
        while (head < tail) {
            int u = order[head++];
            for (int w : g.get(u)) if (!seen[w]) { seen[w] = true; up[0][w] = u; order[tail++] = w; }
        }
        for (int j = 1; j < LOG; j++)
            for (int v = 0; v < n; v++) {
                int mid = up[j - 1][v];
                up[j][v] = mid < 0 ? -1 : up[j - 1][mid];
            }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < queries.length; i++) {
            int v = queries[i][0];
            long rest = queries[i][1];
            for (int j = 0; rest > 0 && v >= 0; j++, rest >>= 1) {
                if (j >= LOG) { v = -1; break; }
                if ((rest & 1L) == 1L) v = up[j][v];
            }
            if (i > 0) sb.append('\\n');
            sb.append(Math.max(v, -1));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "7 5\n0 1\n0 2\n1 3\n1 4\n2 5\n5 6\n6 1\n6 2\n6 3\n6 4\n3 0\n"),
        ("Example 2", "3 3\n0 1\n1 2\n2 1\n2 2\n2 3\n"),
    ],
    hidden=[
        ("Single node", "1 2\n0 0\n0 1\n"),
        ("A chain, every jump length", "6 6\n0 1\n1 2\n2 3\n3 4\n4 5\n5 1\n5 2\n5 3\n5 4\n5 5\n5 6\n"),
        ("A star", "5 4\n0 1\n0 2\n0 3\n0 4\n3 1\n3 2\n0 1\n4 0\n"),
        ("Branching, climbs that cross the root", "9 6\n0 1\n1 2\n2 3\n0 4\n4 5\n5 6\n6 7\n0 8\n3 2\n7 3\n7 4\n8 1\n3 3\n3 4\n"),
    ],
    expl=[
        "6's chain upward is 5, 2, 0 — so one level up is 5, two is 2, three is the founder, and four runs off the top. The 0-th ancestor of 3 is 3 itself.",
        "Employee 2's parent is 1 and its grandparent is 0; three levels up does not exist.",
    ],
    prereqs=[
        ("tree_basics", "Parent pointers and depth in a rooted tree."),
        ("bit_manip", "Reading a number one bit at a time."),
        ("dp", "A table where level j is built from level j-1."),
    ],
)


_p(
    "tree-lca-queries", "Where Two Paths Meet", "Medium",
    topics=["Trees", "Dynamic Programming"], subtopics=["Binary Lifting", "LCA", "Tree Queries"],
    companies=["Google", "Amazon", "Meta"],
    shape="tree_q", ret="String",
    todo="binary lifting: level the deeper node, then jump both up together whenever the ancestors differ",
    description=(
        "A tree of `n` nodes rooted at `0`. For each of `q` queries `a b`, print their **lowest "
        "common ancestor**: the deepest node that is an ancestor of both. A node counts as an "
        "ancestor of itself, so the answer to `a a` is `a`.\n\n"
        "### Input\nLine 1: `n q`.\nNext `n-1` lines: `u v`, an edge of the tree.\n"
        "Next `q` lines: `a b`.\n\n"
        "### Output\nOne line per query: the LCA."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ q ≤ 200000\n0 ≤ a, b < n\nThe edges form a tree.",
    hints=[
        "The one-query recursion from the trees unit is O(n). With 200000 queries that is 4·10¹⁰ steps — the tree is fixed, so preprocess it instead.",
        "Two nodes at the same depth reach their LCA at the same moment. So first lift the deeper one until the depths match — that is a k-th-ancestor jump.",
        "Now walk the jump table from the largest power down: if `up[j][a] != up[j][b]`, the LCA is still above, so take the jump. When no jump is safe, the parent is the answer.",
    ],
    opt=("O((n + q) log n)", "O(n log n)",
         "One binary-lifting table; each query levels the deeper node and then descends the powers."),
    editorial=(
        "## The one thing this teaches\n**Binary search, on a path instead of an array.** The "
        "ancestors of `a` split into two runs: those that are *not* ancestors of `b`, then those "
        "that are. Walking the jump table from the largest power down finds that boundary in "
        "log n steps.\n\n"
        "## Approach\n```java\nint lca(int a, int b) {\n"
        "    if (depth[a] < depth[b]) { int t = a; a = b; b = t; }\n"
        "    a = jump(a, depth[a] - depth[b]);            // level them\n"
        "    if (a == b) return a;                        // b was an ancestor of a\n"
        "    for (int j = LOG - 1; j >= 0; j--)\n"
        "        if (up[j][a] != up[j][b]) { a = up[j][a]; b = up[j][b]; }\n"
        "    return up[0][a];\n}\n```\n\n"
        "## Why it descends from the largest jump\nThe invariant is *`a` and `b` are still "
        "strictly below the LCA*. A jump is taken only when it keeps them different — "
        "`up[j][a] != up[j][b]` means 2^j levels up is still below the meeting point. Starting "
        "from the biggest power and halving makes the total climb any distance at all, in "
        "log n steps: the same reason binary search works.\n\n"
        "## Why the answer is the parent, not the node\nWhen no jump keeps them apart, `a` and "
        "`b` are the two distinct children of the meeting point, one step below it. So the LCA "
        "is `up[0][a]`.\n\n"
        "## The case the loop cannot handle\nIf `b` is an ancestor of `a`, levelling makes "
        "`a == b`, and the loop below would never run. That early return is not an optimisation "
        "— without it the function returns the LCA's parent."
    ),
    py='''
def solve(n, edges, queries):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
        g[v].append(u)
    LOG = 1
    while (1 << LOG) < max(2, n):
        LOG += 1
    LOG += 1
    par = [-1] * n
    depth = [0] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for w in g[u]:
            if not seen[w]:
                seen[w] = True
                par[w] = u
                depth[w] = depth[u] + 1
                order.append(w)
    up = [par]
    for j in range(1, LOG):
        prev = up[j - 1]
        cur = [-1] * n
        for v in range(n):
            mid = prev[v]
            cur[v] = -1 if mid < 0 else prev[mid]
        up.append(cur)

    def jump(v, k):
        j = 0
        while k > 0 and v >= 0:
            if k & 1:
                v = up[j][v]
            k >>= 1
            j += 1
        return v

    out = []
    for a, b in queries:
        if depth[a] < depth[b]:
            a, b = b, a
        a = jump(a, depth[a] - depth[b])
        if a == b:
            out.append(str(a))
            continue
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a = up[j][a]
                b = up[j][b]
        out.append(str(up[0][a]))
    return "\\n".join(out)
''',
    java='''
    static String solve(int n, int[][] edges, int[][] queries) {
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        int LOG = 1;
        while ((1 << LOG) < Math.max(2, n)) LOG++;
        LOG++;
        int[][] up = new int[LOG][n];
        for (int[] row : up) Arrays.fill(row, -1);
        int[] depth = new int[n];
        int[] order = new int[n];
        boolean[] seen = new boolean[n];
        int head = 0, tail = 0;
        order[tail++] = 0;
        seen[0] = true;
        while (head < tail) {
            int u = order[head++];
            for (int w : g.get(u)) if (!seen[w]) {
                seen[w] = true; up[0][w] = u; depth[w] = depth[u] + 1; order[tail++] = w;
            }
        }
        for (int j = 1; j < LOG; j++)
            for (int v = 0; v < n; v++) {
                int mid = up[j - 1][v];
                up[j][v] = mid < 0 ? -1 : up[j - 1][mid];
            }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < queries.length; i++) {
            int a = queries[i][0], b = queries[i][1];
            if (depth[a] < depth[b]) { int t = a; a = b; b = t; }
            int diff = depth[a] - depth[b];
            for (int j = 0; diff > 0; j++, diff >>= 1) if ((diff & 1) == 1) a = up[j][a];
            int ans;
            if (a == b) {
                ans = a;
            } else {
                for (int j = LOG - 1; j >= 0; j--)
                    if (up[j][a] != up[j][b]) { a = up[j][a]; b = up[j][b]; }
                ans = up[0][a];
            }
            if (i > 0) sb.append('\\n');
            sb.append(ans);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "7 4\n0 1\n0 2\n1 3\n1 4\n2 5\n5 6\n3 4\n3 6\n5 6\n1 4\n"),
        ("Example 2", "3 2\n0 1\n1 2\n1 2\n0 2\n"),
    ],
    hidden=[
        ("Single node", "1 1\n0 0\n"),
        ("A chain: the shallower node is always the answer", "6 5\n0 1\n1 2\n2 3\n3 4\n4 5\n5 0\n5 3\n2 4\n1 1\n0 5\n"),
        ("A star: everything meets at the root", "5 4\n0 1\n0 2\n0 3\n0 4\n1 2\n3 4\n2 2\n0 4\n"),
        ("Two deep branches", "11 6\n0 1\n1 2\n2 3\n3 4\n0 5\n5 6\n6 7\n1 8\n8 9\n9 10\n4 10\n4 7\n10 9\n7 5\n3 9\n2 2\n"),
    ],
    expl=[
        "3 and 4 are siblings under 1. 3 and 6 are in different branches of the root. 5 is an ancestor of 6, so it is its own answer with 6.",
        "1 is 2's parent, so the meeting point is 1; from the root, it is the root.",
    ],
    prereqs=[
        ("tree_basics", "Depth, and the ancestor chain of a node."),
        ("binary_search", "Descending the powers to find a boundary."),
        ("dp", "The jump table, built level by level."),
    ],
)


_p(
    "tree-path-distance", "How Far Apart?", "Hard",
    topics=["Trees", "Graphs"], subtopics=["Binary Lifting", "LCA", "Weighted Trees"],
    companies=["Google", "Uber"],
    shape="wtree_q", ret="String",
    todo="root the tree, record dist-from-root; answer = d[a] + d[b] - 2 * d[lca(a, b)]",
    description=(
        "A road network with no loops: `n` towns and `n-1` two-way roads, so there is exactly "
        "one route between any two towns. For each of `q` queries `a b`, print the total length "
        "of the route from town `a` to town `b`.\n\n"
        "### Input\nLine 1: `n q`.\nNext `n-1` lines: `u v w` — a road between `u` and `v` "
        "of length `w`.\nNext `q` lines: `a b`.\n\n"
        "### Output\nOne line per query: the distance."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ q ≤ 200000\n1 ≤ w ≤ 10^9\n0 ≤ a, b < n\nThe roads form a tree.",
    hints=[
        "Running a BFS or Dijkstra per query is O(n) per query. The network never changes — all of that work can happen once.",
        "Root the tree anywhere and record `d[v]`, the distance from the root. The route from a to b goes up to their lowest common ancestor and back down.",
        "So the shared prefix from the root is counted twice and must be removed twice: `d[a] + d[b] - 2·d[lca(a, b)]`. Find the LCA by binary lifting.",
    ],
    opt=("O((n + q) log n)", "O(n log n)",
         "One rooting pass for depths and root distances, a binary-lifting table, then O(log n) per query."),
    editorial=(
        "## The one thing this teaches\n**On a tree, every path decomposes at the LCA.** Once "
        "you can find the meeting point in O(log n), any additive quantity along a path — "
        "length, edge count, sum of tolls — is three precomputed numbers combined by "
        "inclusion–exclusion.\n\n"
        "## Approach\n```java\n// one pass from the root: depth[v] in EDGES, dist[v] in LENGTH\n"
        "long answer(int a, int b) {\n    int m = lca(a, b);\n"
        "    return dist[a] + dist[b] - 2 * dist[m];\n}\n```\n\n"
        "## Why subtract twice\nThe route root→a and the route root→b share exactly the "
        "stretch root→lca. Adding the two routes counts that stretch twice while the real "
        "path uses it zero times, so it comes off twice. The same identity with `depth` instead "
        "of `dist` counts *edges* on the path.\n\n"
        "## Two different depths\nThe LCA search must climb by **edge count**, not by length — "
        "a long edge is still one level. Keep `depth` (an `int`, for levelling and jumping) and "
        "`dist` (a `long`, for the answer) as separate arrays. Levelling by `dist` is the "
        "bug this problem is built to catch.\n\n"
        "## Overflow\n200000 edges of length 10⁹ make a path worth 2·10¹⁴. `int` "
        "overflows at 2·10⁹, so every distance is a `long`."
    ),
    py='''
def solve(n, edges, queries):
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))
    LOG = 1
    while (1 << LOG) < max(2, n):
        LOG += 1
    LOG += 1
    par = [-1] * n
    depth = [0] * n
    dist = [0] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for w, cost in g[u]:
            if not seen[w]:
                seen[w] = True
                par[w] = u
                depth[w] = depth[u] + 1
                dist[w] = dist[u] + cost
                order.append(w)
    up = [par]
    for j in range(1, LOG):
        prev = up[j - 1]
        cur = [-1] * n
        for v in range(n):
            mid = prev[v]
            cur[v] = -1 if mid < 0 else prev[mid]
        up.append(cur)

    def lca(a, b):
        if depth[a] < depth[b]:
            a, b = b, a
        diff = depth[a] - depth[b]
        j = 0
        while diff > 0:
            if diff & 1:
                a = up[j][a]
            diff >>= 1
            j += 1
        if a == b:
            return a
        for j in range(LOG - 1, -1, -1):
            if up[j][a] != up[j][b]:
                a = up[j][a]
                b = up[j][b]
        return up[0][a]

    out = []
    for a, b in queries:
        m = lca(a, b)
        out.append(str(dist[a] + dist[b] - 2 * dist[m]))
    return "\\n".join(out)
''',
    java='''
    static String solve(int n, int[][] edges, int[][] queries) {
        int[] head = new int[n], nxt = new int[2 * Math.max(1, n - 1)];
        int[] to = new int[2 * Math.max(1, n - 1)], cost = new int[2 * Math.max(1, n - 1)];
        Arrays.fill(head, -1);
        int ec = 0;
        for (int[] e : edges) {
            to[ec] = e[1]; cost[ec] = e[2]; nxt[ec] = head[e[0]]; head[e[0]] = ec++;
            to[ec] = e[0]; cost[ec] = e[2]; nxt[ec] = head[e[1]]; head[e[1]] = ec++;
        }
        int LOG = 1;
        while ((1 << LOG) < Math.max(2, n)) LOG++;
        LOG++;
        int[][] up = new int[LOG][n];
        for (int[] row : up) Arrays.fill(row, -1);
        int[] depth = new int[n];
        long[] dist = new long[n];
        int[] order = new int[n];
        boolean[] seen = new boolean[n];
        int h = 0, t = 0;
        order[t++] = 0;
        seen[0] = true;
        while (h < t) {
            int u = order[h++];
            for (int e = head[u]; e != -1; e = nxt[e]) {
                int w = to[e];
                if (seen[w]) continue;
                seen[w] = true;
                up[0][w] = u;
                depth[w] = depth[u] + 1;
                dist[w] = dist[u] + cost[e];
                order[t++] = w;
            }
        }
        for (int j = 1; j < LOG; j++)
            for (int v = 0; v < n; v++) {
                int mid = up[j - 1][v];
                up[j][v] = mid < 0 ? -1 : up[j - 1][mid];
            }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < queries.length; i++) {
            int a = queries[i][0], b = queries[i][1];
            int x = a, y = b;
            if (depth[x] < depth[y]) { int tmp = x; x = y; y = tmp; }
            int diff = depth[x] - depth[y];
            for (int j = 0; diff > 0; j++, diff >>= 1) if ((diff & 1) == 1) x = up[j][x];
            int m;
            if (x == y) {
                m = x;
            } else {
                for (int j = LOG - 1; j >= 0; j--)
                    if (up[j][x] != up[j][y]) { x = up[j][x]; y = up[j][y]; }
                m = up[0][x];
            }
            if (i > 0) sb.append('\\n');
            sb.append(dist[a] + dist[b] - 2 * dist[m]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6 4\n0 1 4\n0 2 2\n1 3 7\n2 4 1\n2 5 3\n3 4\n4 5\n1 1\n0 3\n"),
        ("Example 2", "2 2\n0 1 9\n0 1\n1 1\n"),
    ],
    hidden=[
        ("Single town", "1 1\n0 0\n"),
        ("A chain, long roads", "5 4\n0 1 1000000000\n1 2 1000000000\n2 3 1000000000\n3 4 1000000000\n0 4\n1 3\n4 4\n2 0\n"),
        ("A star", "5 4\n0 1 5\n0 2 6\n0 3 7\n0 4 8\n1 2\n3 4\n1 0\n4 4\n"),
        ("Deep branches meeting low", "9 5\n0 1 2\n1 2 3\n2 3 4\n2 4 5\n0 5 6\n5 6 7\n6 7 8\n0 8 9\n3 4\n3 7\n8 4\n7 6\n1 3\n"),
    ],
    expl=[
        "3→1→0→2→4 is 7 + 4 + 2 + 1 = 14. 4 and 5 meet at town 2: 1 + 3 = 4. A town is zero from itself, and 0→1→3 is 4 + 7 = 11.",
        "One road of length 9 between the two towns; zero to stay put.",
    ],
    prereqs=[
        ("tree_basics", "Rooting a tree and measuring from the root."),
        ("bfs", "One pass that fixes parent, depth and distance."),
        ("prefix_sum", "Inclusion-exclusion: the shared prefix counted twice, removed twice."),
        ("overflow", "10^9 per edge over a long path needs a long."),
    ],
)
