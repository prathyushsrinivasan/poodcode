# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 59 — Trees & Graphs round 2, part 2: graphs.
#
#   count-sub-islands          flood fill on one grid, checked against another
#   alternating-colour-paths   BFS over (vertex, colour of the last edge)
#   all-ancestors-dag          ancestor sets pushed along a topological order
#   smallest-equivalent-string union-find whose root is always the smallest letter
#   gcd-connectivity           union every multiple of d, for each d above the threshold
#   max-spanning-tree          Kruskal, heaviest edge first
#   second-best-mst            swap one non-tree edge for the heaviest edge on its tree path
#   cost-within-deadline       shortest path over (vertex, time used) states
#   dag-shortest-negative      negative weights are fine on a DAG: relax in topological order
#   reachability-queries       transitive closure, one BFS per source
#
# Defines the shapes `grid_pair`, `two_sets`, `str3`, `ntq`, `wgraph_tc` and `graph_q`.
# ===========================================================================

# "r c", r rows of grid A, then r rows of grid B
_SHAPES["grid_pair"] = dict(
    py="d = sys.stdin.read().split()\nr, c = int(d[0]), int(d[1])\na = d[2:2 + r]\nb = d[2 + r:2 + 2 * r]\n",
    py_params="a, b",
    js=_JS_NUMS + "const r = Number(d[0]);\nconst a = d.slice(2, 2 + r), b = d.slice(2 + r, 2 + 2 * r);\n",
    js_params="a, b",
    java="        int r = sc.nextInt(), c = sc.nextInt();\n        String[] a = new String[r], b = new String[r];\n"
         "        for (int i = 0; i < r; i++) a[i] = sc.next();\n        for (int i = 0; i < r; i++) b[i] = sc.next();\n",
    java_params="String[] a, String[] b", java_args="a, b",
)
# "n r b", then r lines "u v" (red), then b lines "u v" (blue)
_SHAPES["two_sets"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, r, b = d[0], d[1], d[2]\n"
       "red = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(r)]\n"
       "blue = [(d[3 + 2 * r + 2 * i], d[4 + 2 * r + 2 * i]) for i in range(b)]\n",
    py_params="n, red, blue",
    js=_JS_NUMS + "const n = Number(d[0]), r = Number(d[1]), b = Number(d[2]);\n"
       "const red = Array.from({ length: r }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n"
       "const blue = Array.from({ length: b }, (_, i) => [Number(d[3 + 2 * r + 2 * i]), Number(d[4 + 2 * r + 2 * i])]);\n",
    js_params="n, red, blue",
    java="        int n = sc.nextInt(), r = sc.nextInt(), b = sc.nextInt();\n"
         "        int[][] red = new int[r][2], blue = new int[b][2];\n"
         "        for (int i = 0; i < r; i++) { red[i][0] = sc.nextInt(); red[i][1] = sc.nextInt(); }\n"
         "        for (int i = 0; i < b; i++) { blue[i][0] = sc.nextInt(); blue[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] red, int[][] blue", java_args="n, red, blue",
)
# three tokens
_SHAPES["str3"] = dict(
    py="d = sys.stdin.read().split()\ns, t, base = d[0], d[1], d[2]\n",
    py_params="s, t, base",
    js=_JS_NUMS + "const s = d[0], t = d[1], base = d[2];\n",
    js_params="s, t, base",
    java="        String s = sc.next(), t = sc.next(), base = sc.next();\n",
    java_params="String s, String t, String base", java_args="s, t, base",
)
# "n t q", then q lines "a b"
_SHAPES["ntq"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, t, q = d[0], d[1], d[2]\n"
       "queries = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(q)]\n",
    py_params="n, t, queries",
    js=_JS_NUMS + "const n = Number(d[0]), t = Number(d[1]), q = Number(d[2]);\n"
       "const queries = Array.from({ length: q }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n",
    js_params="n, t, queries",
    java="        int n = sc.nextInt(), t = sc.nextInt(), q = sc.nextInt();\n        int[][] queries = new int[q][2];\n"
         "        for (int i = 0; i < q; i++) { queries[i][0] = sc.nextInt(); queries[i][1] = sc.nextInt(); }\n",
    java_params="int n, int t, int[][] queries", java_args="n, t, queries",
)
# "n m T", then m lines "u v time cost"
_SHAPES["wgraph_tc"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m, T = d[0], d[1], d[2]\n"
       "edges = [tuple(d[3 + 4 * i:7 + 4 * i]) for i in range(m)]\n",
    py_params="n, edges, T",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), T = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2, 3].map(j => Number(d[3 + 4 * i + j])));\n",
    js_params="n, edges, T",
    java="        int n = sc.nextInt(), m = sc.nextInt(), T = sc.nextInt();\n        int[][] edges = new int[m][4];\n"
         "        for (int i = 0; i < m; i++) for (int j = 0; j < 4; j++) edges[i][j] = sc.nextInt();\n",
    java_params="int n, int[][] edges, int T", java_args="n, edges, T",
)
# "n m q", then m lines "u v", then q lines "a b"
_SHAPES["graph_q"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m, q = d[0], d[1], d[2]\n"
       "edges = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(m)]\n"
       "queries = [(d[3 + 2 * m + 2 * i], d[4 + 2 * m + 2 * i]) for i in range(q)]\n",
    py_params="n, edges, queries",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), q = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n"
       "const queries = Array.from({ length: q }, (_, i) => [Number(d[3 + 2 * m + 2 * i]), Number(d[4 + 2 * m + 2 * i])]);\n",
    js_params="n, edges, queries",
    java="        int n = sc.nextInt(), m = sc.nextInt(), q = sc.nextInt();\n        int[][] edges = new int[m][2];\n"
         "        for (int i = 0; i < m; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); }\n"
         "        int[][] queries = new int[q][2];\n"
         "        for (int i = 0; i < q; i++) { queries[i][0] = sc.nextInt(); queries[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] edges, int[][] queries", java_args="n, edges, queries",
)


def _grid_pair_case(r, c, seed, pct):
    rng = _Lcg(seed)
    a = ["".join("1" if rng.randint(1, 100) <= pct else "0" for _ in range(c)) for _ in range(r)]
    b = ["".join("1" if rng.randint(1, 100) <= pct else "0" for _ in range(c)) for _ in range(r)]
    return f"{r} {c}\n" + "\n".join(a) + "\n" + "\n".join(b) + "\n"


_p(
    "count-sub-islands", "Islands Inside Islands", "Medium",
    topics=["Graph", "Depth-First Search", "Matrix"], subtopics=["Flood Fill", "Grid"],
    companies=["Google", "Amazon"],
    shape="grid_pair", ret="int",
    todo="flood-fill each island of B; it counts if every one of its cells is also land in A",
    description=(
        "Two maps of the same `r × c` area mark land `1` and water `0`: map A from last year, map B "
        "from this year. An island of B (cells joined up, down, left or right) is a **sub-island** "
        "if every one of its cells is also land in A. Count the sub-islands of B.\n\n"
        "### Input\nLine 1: `r c`.\nNext `r` lines: map A.\nNext `r` lines: map B.\n\n"
        "### Output\nThe number of sub-islands."
    ),
    constraints="1 ≤ r, c ≤ 300",
    hints=[
        "Find B's islands with a flood fill, as in `number-of-islands`.",
        "While filling an island, check every cell against A. One water cell in A disqualifies the whole island.",
        "Do not stop the fill early when a bad cell is found — the rest of the island must still be marked, or it will be counted as a separate island later.",
    ],
    opt=("O(r · c)", "O(r · c)",
         "Every cell of B is filled once; the check against A is O(1) per cell."),
    editorial=(
        "## The one thing this teaches\n**A flood fill can compute a property of the whole "
        "component.** The fill already visits every cell of the island; AND-ing a condition "
        "across those cells answers \"is the entire island inside A?\".\n\n"
        "## Approach\n```java\nfor each cell (i, j) with B[i][j] == '1' and not seen:\n"
        "    boolean inside = true;\n    fill from (i, j) over B's land, and for every cell:\n"
        "        if (A[x][y] == '0') inside = false;      // keep filling anyway\n    if (inside) count++;\n```\n\n"
        "## The early-exit bug\nReturning as soon as one cell fails leaves the rest of that island "
        "unmarked — the outer loop then finds its remains and may count them."
    ),
    py='''
def solve(a, b):
    r, c = len(b), len(b[0])
    seen = [[False] * c for _ in range(r)]
    count = 0
    for i in range(r):
        for j in range(c):
            if b[i][j] == "1" and not seen[i][j]:
                inside, st = True, [(i, j)]
                seen[i][j] = True
                while st:
                    x, y = st.pop()
                    if a[x][y] == "0":
                        inside = False
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < r and 0 <= ny < c and b[nx][ny] == "1" and not seen[nx][ny]:
                            seen[nx][ny] = True
                            st.append((nx, ny))
                if inside:
                    count += 1
    return count
''',
    java='''
    static int solve(String[] a, String[] b) {
        int r = b.length, c = b[0].length();
        boolean[][] seen = new boolean[r][c];
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int count = 0;
        ArrayDeque<int[]> st = new ArrayDeque<>();
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                if (b[i].charAt(j) != '1' || seen[i][j]) continue;
                boolean inside = true;
                seen[i][j] = true;
                st.push(new int[]{i, j});
                while (!st.isEmpty()) {
                    int[] p = st.pop();
                    if (a[p[0]].charAt(p[1]) == '0') inside = false;
                    for (int[] d : dirs) {
                        int x = p[0] + d[0], y = p[1] + d[1];
                        if (x >= 0 && x < r && y >= 0 && y < c && b[x].charAt(y) == '1' && !seen[x][y]) {
                            seen[x][y] = true;
                            st.push(new int[]{x, y});
                        }
                    }
                }
                if (inside) count++;
            }
        return count;
    }
''',
    examples=[
        ("Example 1", "4 5\n11100\n11011\n00011\n10001\n11000\n01011\n00101\n10001\n"),
        ("Example 2", "2 3\n010\n000\n111\n000\n"),
    ],
    hidden=[
        ("One cell each", "1 1\n1\n1\n"),
        ("No land in B", "2 2\n11\n11\n00\n00\n"),
        ("One bad cell spoils an island", "1 5\n11011\n11111\n"),
        ("Identical maps", "3 3\n101\n010\n101\n101\n010\n101\n"),
        ("Random", _grid_pair_case(30, 40, 371, 55)),
        ("Large", _grid_pair_case(300, 300, 372, 60)),
    ],
    expl=[
        "B has four islands. Three — the three cells at the top left, the column on the right and the lone cell at (3, 0) — lie entirely on A's land; the lone cell at (2, 2) is water in A.",
        "B's only island covers (0, 0) and (0, 2), which are water in A.",
    ],
    prereqs=[
        ("flood_fill", "Fill each island of B once, iteratively."),
        ("grid", "Four-neighbour moves with bounds checks."),
    ],
)


_p(
    "alternating-colour-paths", "Red, Blue, Red, Blue", "Medium",
    topics=["Graph", "Breadth-First Search"], subtopics=["Breadth-First Search", "State Space"],
    companies=["Amazon", "Google"],
    shape="two_sets", ret="String",
    todo="BFS over (vertex, colour of the last edge used); from a red arrival only blue edges may follow, and vice versa",
    description=(
        "A directed graph has **red** and **blue** edges. A path is *alternating* if consecutive "
        "edges have different colours. For every vertex, print the fewest edges on an "
        "alternating path from vertex `0`, or `-1` if there is none (vertex 0 itself is `0`).\n\n"
        "### Input\nLine 1: `n r b`.\nNext `r` lines: red edges `u v`.\nNext `b` lines: blue edges `u v`.\n\n"
        "### Output\n`n` numbers on one line."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ r, b ≤ 2·10^4\nSelf-loops and repeated edges may appear.",
    hints=[
        "Plain BFS by vertex fails: reaching v by a red edge and by a blue edge allow different next steps.",
        "Make the state (vertex, colour of the edge you arrived by). From (u, red) you may only take blue edges, and vice versa.",
        "Start from both (0, red) and (0, blue) at distance 0; a vertex's answer is its smaller distance over the two states.",
    ],
    opt=("O(n + r + b)", "O(n + r + b)",
         "Two states per vertex, each edge examined once from the matching state."),
    editorial=(
        "## The one thing this teaches\n**The colour of the last edge is part of the state.** "
        "It is the smallest possible augmented state — one bit — and it turns an impossible "
        "shortest-path rule into ordinary BFS over 2n states.\n\n"
        "## Approach\n```java\n// dist[v][c]: fewest edges to reach v, arriving by colour c (0 red, 1 blue)\n"
        "dist[0][0] = dist[0][1] = 0;  queue {0,0}, {0,1}\nwhile queue not empty:\n    (u, c) = poll\n"
        "    for v in adj[1 - c][u]:                // the other colour\n        if dist[v][1 - c] unset: set to dist[u][c] + 1, push (v, 1 - c)\n"
        "answer[v] = min over c of dist[v][c]\n```"
    ),
    py='''
def solve(n, red, blue):
    adj = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for u, v in red:
        adj[0][u].append(v)
    for u, v in blue:
        adj[1][u].append(v)
    dist = [[-1, -1] for _ in range(n)]
    dist[0] = [0, 0]
    q = deque([(0, 0), (0, 1)])
    while q:
        u, c = q.popleft()
        nc = 1 - c
        for v in adj[nc][u]:
            if dist[v][nc] < 0:
                dist[v][nc] = dist[u][c] + 1
                q.append((v, nc))
    out = []
    for d0, d1 in dist:
        cand = [x for x in (d0, d1) if x >= 0]
        out.append(min(cand) if cand else -1)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int n, int[][] red, int[][] blue) {
        List<List<List<Integer>>> adj = new ArrayList<>();
        for (int c = 0; c < 2; c++) {
            List<List<Integer>> l = new ArrayList<>();
            for (int i = 0; i < n; i++) l.add(new ArrayList<>());
            adj.add(l);
        }
        for (int[] e : red) adj.get(0).get(e[0]).add(e[1]);
        for (int[] e : blue) adj.get(1).get(e[0]).add(e[1]);
        int[][] dist = new int[n][2];
        for (int[] d : dist) Arrays.fill(d, -1);
        dist[0][0] = dist[0][1] = 0;
        ArrayDeque<int[]> q = new ArrayDeque<>();
        q.add(new int[]{0, 0});
        q.add(new int[]{0, 1});
        while (!q.isEmpty()) {
            int[] s = q.poll();
            int nc = 1 - s[1];
            for (int v : adj.get(nc).get(s[0]))
                if (dist[v][nc] < 0) { dist[v][nc] = dist[s[0]][s[1]] + 1; q.add(new int[]{v, nc}); }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            int a = dist[i][0], b = dist[i][1];
            sb.append(a < 0 ? b : b < 0 ? a : Math.min(a, b));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5 3 2\n0 1\n2 3\n1 4\n1 2\n3 4\n"),
        ("Example 2", "3 2 0\n0 1\n1 2\n"),
    ],
    hidden=[
        ("One vertex", "1 0 0\n"),
        ("A red self-loop", "2 1 1\n0 0\n0 1\n"),
        ("Two colours, same edge", "3 2 2\n0 1\n1 2\n0 1\n1 2\n"),
        ("The long way alternates", "4 3 2\n0 3\n0 1\n2 3\n1 2\n3 3\n"),
        ("Random", "300 600 600\n" + "".join(f"{u} {v}\n" for u, v in _rand_graph(300, 600, _Lcg(381), directed=True))
         + "".join(f"{u} {v}\n" for u, v in _rand_graph(300, 600, _Lcg(382), directed=True))),
        ("Large", "10000 20000 20000\n" + "".join(f"{u} {v}\n" for u, v in _rand_graph(10000, 20000, _Lcg(383), directed=True))
         + "".join(f"{u} {v}\n" for u, v in _rand_graph(10000, 20000, _Lcg(384), directed=True))),
    ],
    expl=[
        "0 →red 1 →blue 2 →red 3 →blue 4. The red edge 1 → 4 would follow a red edge, so vertex 4 is four edges away, not two.",
        "Red then red is not alternating, so vertex 2 cannot be reached.",
    ],
    prereqs=[
        ("bfs", "Breadth-first search over (vertex, last colour) states."),
        ("graph_repr", "Two adjacency lists, one per colour."),
    ],
)


_p(
    "all-ancestors-dag", "Every Ancestor", "Medium",
    topics=["Graph", "Topological Sort"], subtopics=["Topological Sort", "DAG DP", "Sets"],
    companies=["Google", "Microsoft"],
    shape="graph", ret="String",
    todo="in topological order, ancestors[v] = union over edges u -> v of ancestors[u] + {u}",
    description=(
        "A DAG has `n` vertices and `m` directed edges `u v`. Vertex `a` is an **ancestor** of "
        "`v` if there is a path from `a` to `v`. For every vertex, print its ancestors in increasing "
        "order on one line, or `-` if it has none.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v`.\n\n### Output\n`n` lines."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ m ≤ 2000\nThe graph has no cycle.",
    hints=[
        "One search per vertex backwards along edges works — O(n · (n + m)).",
        "Ancestors flow forward along edges: v's ancestors are its direct predecessors plus all of *their* ancestors.",
        "Process vertices in topological order so each predecessor's set is complete before it is used. A boolean row (or a bitset) per vertex makes the union cheap.",
    ],
    opt=("O(n · (n + m))", "O(n²)",
         "Each edge merges one set of up to n ancestors; with 64-bit bitsets it is n / 64 words per edge."),
    editorial=(
        "## The one thing this teaches\n**DP in topological order can carry sets, not just numbers.** "
        "`dag-path-count` pushed a count along each edge; this pushes a set. The order guarantees "
        "every incoming set is final before it is pushed on.\n\n"
        "## Approach\n```java\nfor (int u : topoOrder)\n    for (int v : adj[u]) {\n        anc[v].set(u);\n"
        "        anc[v].or(anc[u]);            // java.util.BitSet\n    }\n```\n\n"
        "## Why not DFS from each vertex?\nIt is the same complexity without bitsets and far "
        "simpler to get right on a small graph — worth saying in an interview before offering the "
        "DP."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    anc = [0] * n                     # Python ints as bitsets
    q = deque(v for v in range(n) if indeg[v] == 0)
    while q:
        u = q.popleft()
        for v in adj[u]:
            anc[v] |= anc[u] | (1 << u)
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    out = []
    for v in range(n):
        s = [str(i) for i in range(n) if anc[v] >> i & 1]
        out.append(" ".join(s) if s else "-")
    return "\\n".join(out)
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        BitSet[] anc = new BitSet[n];
        for (int i = 0; i < n; i++) anc[i] = new BitSet(n);
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj.get(u)) {
                anc[v].set(u);
                anc[v].or(anc[u]);
                if (--indeg[v] == 0) q.add(v);
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int v = 0; v < n; v++) {
            if (v > 0) sb.append('\\n');
            if (anc[v].isEmpty()) { sb.append('-'); continue; }
            boolean first = true;
            for (int i = anc[v].nextSetBit(0); i >= 0; i = anc[v].nextSetBit(i + 1)) {
                if (!first) sb.append(' ');
                sb.append(i);
                first = false;
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _graph_case(5, [(0, 2), (1, 2), (2, 3), (4, 3)])),
        ("Example 2", _graph_case(3, [])),
    ],
    hidden=[
        ("One vertex", "1 0\n"),
        ("A chain", _graph_case(4, [(3, 2), (2, 1), (1, 0)])),
        ("A diamond", _graph_case(4, [(0, 1), (0, 2), (1, 3), (2, 3)])),
        ("Repeated edge", _graph_case(3, [(0, 1), (0, 1), (1, 2)])),
        ("Random", _graph_case(60, _rand_dag(60, 150, _Lcg(391)))),
        ("Large", _graph_case(300, _rand_dag(300, 1500, _Lcg(392)))),
    ],
    expl=[
        "3 has ancestors 0, 1, 2 (through 2) and 4; 2 has 0 and 1; 0, 1 and 4 have none.",
        "No edges: nobody has an ancestor.",
    ],
    prereqs=[
        ("topo", "Kahn's order finalises every predecessor first."),
        ("bit_manip", "A bitset per vertex makes each union a handful of word ORs."),
    ],
)


_p(
    "smallest-equivalent-string", "The Smallest Equivalent Word", "Medium",
    topics=["Union Find", "String"], subtopics=["Union Find", "Equivalence Classes"],
    companies=["Google", "Amazon"],
    shape="str3", ret="String",
    todo="union s[i] with t[i] for every i, always keeping the smaller letter as the root; then map each letter of base to its root",
    description=(
        "Two words `s` and `t` of equal length say that `s[i]` and `t[i]` are **equivalent** "
        "letters, for every `i`. Equivalence is reflexive, symmetric and transitive. Rewrite `base` "
        "by replacing each letter with the smallest letter equivalent to it.\n\n"
        "### Input\nThree words, one per line: `s`, `t`, `base` (lowercase).\n\n"
        "### Output\nThe rewritten word."
    ),
    constraints="1 ≤ |s| = |t| ≤ 1000\n1 ≤ |base| ≤ 1000",
    hints=[
        "Equivalence classes that only ever merge: union-find over 26 letters.",
        "When uniting two classes, make the smaller root letter the new root — then every class's root is its smallest letter.",
        "Replace each letter of base by find(letter).",
    ],
    opt=("O((|s| + |base|) · α(26))", "O(26)",
         "26 elements; each union and find is effectively constant."),
    editorial=(
        "## The one thing this teaches\n**Choose the root to carry the answer.** Union by size "
        "chooses the root for speed. With only 26 letters speed is irrelevant, so choose it to be "
        "the class's smallest letter — then find() *is* the answer.\n\n"
        "## Approach\n```java\nvoid union(int a, int b) {\n    a = find(a); b = find(b);\n"
        "    if (a == b) return;\n    if (a < b) parent[b] = a; else parent[a] = b;   // smaller letter is the root\n}\n```"
    ),
    py='''
def solve(s, t, base):
    parent = list(range(26))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in zip(s, t):
        ra, rb = find(ord(a) - 97), find(ord(b) - 97)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb
    return "".join(chr(find(ord(ch) - 97) + 97) for ch in base)
''',
    java='''
    static int[] parent = new int[26];

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static String solve(String s, String t, String base) {
        for (int i = 0; i < 26; i++) parent[i] = i;
        for (int i = 0; i < s.length(); i++) {
            int a = find(s.charAt(i) - 'a'), b = find(t.charAt(i) - 'a');
            if (a == b) continue;
            if (a < b) parent[b] = a; else parent[a] = b;
        }
        StringBuilder sb = new StringBuilder();
        for (char ch : base.toCharArray()) sb.append((char) ('a' + find(ch - 'a')));
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "dog\ncat\ntoad\n"),
        ("Example 2", "zzz\nyyy\nyay\n"),
    ],
    hidden=[
        ("Letters equal to themselves", "abc\nabc\nxyz\n"),
        ("A chain to a", "zyx\nyxa\nzzz\n"),
        ("Two classes", "ab\nba\nbaba\n"),
        ("Random", "".join(chr(97 + x % 26) for x in _lcg_ints(401, 300, 0, 999)) + "\n"
         + "".join(chr(97 + x % 26) for x in _lcg_ints(402, 300, 0, 999)) + "\n"
         + "".join(chr(97 + x % 26) for x in _lcg_ints(403, 500, 0, 999)) + "\n"),
        ("Sparse links", "qwerty\nasdfgh\nzxcvbnmqwertyuiopasdfghjkl\n"),
    ],
    expl=[
        "d ~ c, o ~ a, g ~ t — so t becomes g, o becomes a, a stays a, d becomes c: \"gaac\".",
        "z ~ y, so y's class is {y, z}, whose smallest letter is y itself: the word is unchanged.",
    ],
    prereqs=[
        ("union_find", "Union-find over 26 letters."),
        ("string_basics", "Mapping characters to indices 0–25 and back."),
    ],
)


_p(
    "gcd-connectivity", "Cities That Share a Factor", "Hard",
    topics=["Union Find", "Math"], subtopics=["Union Find", "Number Theory", "Sieve"],
    companies=["Google", "Amazon"],
    shape="ntq", ret="String",
    todo="for every d from t + 1 to n, union d with 2d, 3d, …; then answer each query with find(a) == find(b)",
    description=(
        "Cities are numbered `1` to `n`. Two cities are joined by a road when they share a common "
        "divisor **strictly greater than** `t`. For each query `a b`, can you drive from city `a` "
        "to city `b`?\n\n"
        "### Input\nLine 1: `n t q`.\nNext `q` lines: `a b`.\n\n### Output\nOne line of `q` characters: `1` or `0`."
    ),
    constraints="1 ≤ n ≤ 2·10^5\n0 ≤ t ≤ n\n1 ≤ q ≤ 10^5\n1 ≤ a, b ≤ n",
    hints=[
        "Building every road is O(n²) pairs. But connectivity only needs enough roads, not all of them.",
        "All multiples of a divisor d > t are pairwise connected. Uniting d with each of its multiples connects them all through d.",
        "Loop d from t + 1 to n and union d, 2d, 3d, …: n/d unions for each d, O(n log n) in total. Then each query is two finds.",
    ],
    opt=("O(n log n · α(n) + q · α(n))", "O(n)",
         "The harmonic sum n/(t+1) + n/(t+2) + … ≤ n ln n unions."),
    editorial=(
        "## The one thing this teaches\n**Union to a hub, not pairwise.** A clique of k vertices "
        "needs k − 1 unions to connect, not k²/2 — so union every member with one representative. "
        "Here the representative of the clique \"multiples of d\" is d itself.\n\n"
        "## Approach\n```java\nfor (int d = t + 1; d <= n; d++)\n    for (int m = 2 * d; m <= n; m += d)\n"
        "        union(d, m);\nfor (int[] q : queries) out.append(find(q[0]) == find(q[1]) ? '1' : '0');\n```\n\n"
        "## Why the loop is n log n\nΣ n/d for d = 1 … n is the harmonic sum, about n ln n — the "
        "same argument as the sieve of Eratosthenes."
    ),
    py='''
def solve(n, t, queries):
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for d in range(t + 1, n + 1):
        rd = find(d)
        for m in range(2 * d, n + 1, d):
            rm = find(m)
            if rm != rd:
                parent[rm] = rd
    return "".join("1" if find(a) == find(b) else "0" for a, b in queries)
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static String solve(int n, int t, int[][] queries) {
        parent = new int[n + 1];
        for (int i = 0; i <= n; i++) parent[i] = i;
        for (int d = t + 1; d <= n; d++) {
            int rd = find(d);
            for (int m = 2 * d; m <= n; m += d) {
                int rm = find(m);
                if (rm != rd) parent[rm] = rd;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int[] q : queries) sb.append(find(q[0]) == find(q[1]) ? '1' : '0');
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "10 2 4\n3 6\n4 8\n3 5\n6 9\n"),
        ("Example 2", "6 0 2\n1 5\n2 3\n"),
    ],
    hidden=[
        ("Threshold equals n", "5 5 2\n1 1\n2 4\n"),
        ("Same city", "7 3 1\n7 7\n"),
        ("Threshold 1", "12 1 4\n5 7\n2 9\n11 1\n6 10\n"),
        ("Random", "1000 7 200\n" + "".join(f"{a} {b}\n" for a, b in zip(_lcg_ints(411, 200, 1, 1000), _lcg_ints(412, 200, 1, 1000)))),
        ("Large", "200000 50 100000\n" + "".join(f"{a} {b}\n" for a, b in zip(_lcg_ints(413, 100000, 1, 200000), _lcg_ints(414, 100000, 1, 200000)))),
    ],
    expl=[
        "3 and 6 share 3 > 2; 4 and 8 share 4; 3 and 5 share nothing above 2 and no chain joins them; 6 and 9 share 3.",
        "With t = 0 every city is divisible by 1 > 0, so everything is connected.",
    ],
    prereqs=[
        ("union_find", "Connect each clique through one hub vertex."),
        ("number_theory", "Looping over the multiples of every d is a harmonic sum, n log n."),
    ],
)


_p(
    "max-spanning-tree", "The Strongest Network", "Easy",
    topics=["Graph", "Minimum Spanning Tree"], subtopics=["Kruskal", "Maximum Spanning Tree"],
    companies=["Amazon", "Microsoft"],
    shape="wgraph", ret="long",
    todo="Kruskal with the edges sorted from HEAVIEST to lightest; -1 unless n - 1 edges were taken",
    description=(
        "A budget allows exactly `n − 1` of the `m` links between `n` stations to be kept. Keep "
        "links so that every station can still reach every other, maximising the **total** "
        "strength of the kept links. Print that total, or `-1` if the stations cannot all be "
        "connected.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n### Output\nThe maximum total, or `-1`."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 10^5\n1 ≤ w ≤ 10^6",
    hints=[
        "n − 1 links that connect n stations form a spanning tree — no cycles possible. So this asks for the strongest spanning tree.",
        "Kruskal works for any order of edges: it builds the spanning tree that is best in the order it scans.",
        "Scan heaviest first. Use long for the total.",
    ],
    opt=("O(m log m)", "O(n + m)",
         "Kruskal with the comparator reversed."),
    editorial=(
        "## The one thing this teaches\n**The greedy does not care which way is \"better\".** "
        "The cut property holds with max in place of min, so sorting descending gives a maximum "
        "spanning tree — no other change.\n\n"
        "## Approach\n```java\nArrays.sort(edges, (a, b) -> Integer.compare(b[2], a[2]));   // heaviest first\n"
        "for (int[] e : edges) if (union(e[0], e[1])) { total += e[2]; taken++; }\nreturn taken == n - 1 ? total : -1;\n```"
    ),
    py='''
def solve(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = taken = 0
    for u, v, w in sorted(edges, key=lambda e: -e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            taken += 1
    return total if taken == n - 1 else -1
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static long solve(int n, int[][] edges) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        int[][] es = edges.clone();
        Arrays.sort(es, (a, b) -> Integer.compare(b[2], a[2]));
        long total = 0;
        int taken = 0;
        for (int[] e : es) {
            int ru = find(e[0]), rv = find(e[1]);
            if (ru != rv) { parent[ru] = rv; total += e[2]; taken++; }
        }
        return taken == n - 1 ? total : -1;
    }
''',
    examples=[
        ("Example 1", _wcase(4, [(0, 1, 4), (1, 2, 2), (2, 3, 7), (0, 2, 3), (1, 3, 9)])),
        ("Example 2", _wcase(3, [(0, 1, 5)])),
    ],
    hidden=[
        ("One station", "1 0\n"),
        ("Parallel links", _wcase(2, [(0, 1, 3), (0, 1, 8), (1, 0, 5)])),
        ("A triangle", _wcase(3, [(0, 1, 1), (1, 2, 2), (0, 2, 3)])),
        ("Random", _wcase(100, _connected_wgraph(100, 300, 421, 1, 1000))),
        ("Large", _wcase(10000, _connected_wgraph(10000, 60000, 422, 1, 10**6))),
    ],
    expl=[
        "Take 1-3 (9), 2-3 (7) and 0-1 (4): 20. 0-2 (3) and 1-2 (2) would close cycles.",
        "Station 2 has no link.",
    ],
    prereqs=[
        ("mst", "Kruskal with the order reversed builds a maximum spanning tree."),
        ("union_find", "Skip any link whose ends are already connected."),
    ],
)


_p(
    "second-best-mst", "The Runner-Up Network", "Hard",
    topics=["Graph", "Minimum Spanning Tree"], subtopics=["Minimum Spanning Tree", "Tree Path Maximum"],
    companies=["Google", "Microsoft"],
    shape="wgraph", ret="long",
    todo="build the MST; for each non-tree edge (u, v, w), swapping it for the heaviest tree edge on the u-v path lighter than w gives a candidate; take the smallest",
    description=(
        "A spanning tree connects all `n` vertices with `n − 1` of the `m` edges. Among all spanning "
        "trees whose total weight is **strictly greater** than the minimum, print the smallest "
        "total. Print `-1` if there is none (or if the graph is not connected).\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w` (undirected; repeated edges and self-loops may appear).\n\n"
        "### Output\nThe second-best spanning tree weight, or `-1`."
    ),
    constraints="1 ≤ n ≤ 500\n0 ≤ m ≤ 5000\n1 ≤ w ≤ 10^6",
    hints=[
        "A second-best spanning tree differs from some MST by exactly one swap: add one non-tree edge, remove one tree edge on the cycle it closes.",
        "Adding (u, v, w) closes the cycle through the MST path from u to v. Removing the heaviest edge on that path costs the least — but it must be strictly lighter than w, or the total does not change.",
        "So for every pair of vertices precompute the largest and the largest-strictly-smaller edge on their tree path (a DFS from every vertex, O(n²)), then try each non-tree edge.",
    ],
    opt=("O(m log m + n² + m)", "O(n²)",
         "One Kruskal, one DFS from each vertex over the tree, one pass over the edges."),
    editorial=(
        "## The one thing this teaches\n**Exchange arguments give you the neighbours of the "
        "optimum.** Every spanning tree can be reached from an MST by edge swaps, and the best tree "
        "that is not optimal is one swap away. The work is knowing, for any non-tree edge, the "
        "heaviest tree edge it could replace.\n\n"
        "## Approach\n```java\n// Kruskal: total W, tree adjacency, inTree[] per edge\n"
        "// for each s: DFS over the tree from s, carrying (max1, max2) — the largest and the\n"
        "//   largest strictly smaller weight on the path — into mx1[s][v], mx2[s][v]\n"
        "for each non-tree edge (u, v, w), u != v:\n    if (w > mx1[u][v]) best = min(best, W - mx1[u][v] + w);\n"
        "    else if (mx2[u][v] > 0) best = min(best, W - mx2[u][v] + w);   // w == mx1\n```\n\n"
        "## The strictness trap\nIf a non-tree edge ties with the heaviest path edge, swapping "
        "gives another *minimum* tree, not a second-best one. That is why the second maximum is "
        "kept."
    ),
    py='''
def solve(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    order = sorted(range(len(edges)), key=lambda i: edges[i][2])
    in_tree = [False] * len(edges)
    tree = [[] for _ in range(n)]
    W = taken = 0
    for i in order:
        u, v, w = edges[i]
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            in_tree[i] = True
            W += w
            taken += 1
            tree[u].append((v, w))
            tree[v].append((u, w))
    if taken != n - 1:
        return -1
    mx1 = [[0] * n for _ in range(n)]
    mx2 = [[0] * n for _ in range(n)]
    for s in range(n):
        seen = [False] * n
        seen[s] = True
        st = [(s, 0, 0)]
        while st:
            x, a, b = st.pop()
            mx1[s][x], mx2[s][x] = a, b
            for y, w in tree[x]:
                if not seen[y]:
                    seen[y] = True
                    if w > a:
                        na, nb = w, a
                    elif a > w > b:
                        na, nb = a, w
                    else:
                        na, nb = a, b
                    st.append((y, na, nb))
    best = -1
    for i, (u, v, w) in enumerate(edges):
        if in_tree[i] or u == v:
            continue
        if w > mx1[u][v]:
            cand = W - mx1[u][v] + w
        elif mx2[u][v] > 0:
            cand = W - mx2[u][v] + w
        else:
            continue
        if best < 0 or cand < best:
            best = cand
    return best
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static long solve(int n, int[][] edges) {
        int m = edges.length;
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        Integer[] order = new Integer[m];
        for (int i = 0; i < m; i++) order[i] = i;
        Arrays.sort(order, (a, b) -> Integer.compare(edges[a][2], edges[b][2]));
        boolean[] inTree = new boolean[m];
        List<List<int[]>> tree = new ArrayList<>();
        for (int i = 0; i < n; i++) tree.add(new ArrayList<>());
        long W = 0;
        int taken = 0;
        for (int i : order) {
            int u = edges[i][0], v = edges[i][1], w = edges[i][2];
            int ru = find(u), rv = find(v);
            if (ru != rv) {
                parent[ru] = rv;
                inTree[i] = true;
                W += w;
                taken++;
                tree.get(u).add(new int[]{v, w});
                tree.get(v).add(new int[]{u, w});
            }
        }
        if (taken != n - 1) return -1;
        int[][] mx1 = new int[n][n], mx2 = new int[n][n];
        for (int s = 0; s < n; s++) {
            boolean[] seen = new boolean[n];
            seen[s] = true;
            ArrayDeque<int[]> st = new ArrayDeque<>();
            st.push(new int[]{s, 0, 0});
            while (!st.isEmpty()) {
                int[] cur = st.pop();
                int x = cur[0], a = cur[1], b = cur[2];
                mx1[s][x] = a;
                mx2[s][x] = b;
                for (int[] yw : tree.get(x)) {
                    int y = yw[0], w = yw[1];
                    if (seen[y]) continue;
                    seen[y] = true;
                    int na, nb;
                    if (w > a) { na = w; nb = a; }
                    else if (w < a && w > b) { na = a; nb = w; }
                    else { na = a; nb = b; }
                    st.push(new int[]{y, na, nb});
                }
            }
        }
        long best = -1;
        for (int i = 0; i < m; i++) {
            int u = edges[i][0], v = edges[i][1], w = edges[i][2];
            if (inTree[i] || u == v) continue;
            long cand;
            if (w > mx1[u][v]) cand = W - mx1[u][v] + w;
            else if (mx2[u][v] > 0) cand = W - mx2[u][v] + w;
            else continue;
            if (best < 0 || cand < best) best = cand;
        }
        return best;
    }
''',
    examples=[
        ("Example 1", _wcase(4, [(0, 1, 1), (1, 2, 2), (2, 3, 3), (0, 3, 5), (0, 2, 4)])),
        ("Example 2", _wcase(3, [(0, 1, 1), (1, 2, 1)])),
    ],
    hidden=[
        ("One vertex", "1 0\n"),
        ("A tie is not second-best", _wcase(3, [(0, 1, 2), (1, 2, 2), (0, 2, 2)])),
        ("Ties, then a heavier edge", _wcase(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 1), (1, 3, 5)])),
        ("Parallel edge", _wcase(2, [(0, 1, 3), (0, 1, 4)])),
        ("Self-loop only", _wcase(2, [(0, 1, 3), (1, 1, 1)])),
        ("Disconnected", _wcase(4, [(0, 1, 1), (2, 3, 1), (0, 1, 2)])),
        ("Random", _wcase(60, _connected_wgraph(60, 200, 431, 1, 30))),
        ("Large", _wcase(500, _connected_wgraph(500, 4000, 432, 1, 10**6))),
    ],
    expl=[
        "The MST 0-1, 1-2, 2-3 weighs 6. Swapping in 0-2 (4) for 1-2 (2) gives 8; 0-3 (5) for 2-3 (3) gives 8 too. Either way: 8.",
        "The graph is its own only spanning tree.",
    ],
    prereqs=[
        ("mst", "Kruskal, and the exchange argument: one swap from an MST."),
        ("bfs", "A traversal of the tree from every vertex, carrying the two largest weights."),
    ],
)


def _tc_case(n, m, T, seed):
    rng = _Lcg(seed)
    edges = [(u, v, rng.randint(1, 20), rng.randint(1, 100)) for u, v in _rand_graph(n, m, rng)]
    return f"{n} {len(edges)} {T}\n" + "".join(f"{u} {v} {t} {c}\n" for u, v, t, c in edges)


_p(
    "cost-within-deadline", "Cheapest Trip Before the Deadline", "Hard",
    topics=["Graph", "Shortest Path", "Dynamic Programming"], subtopics=["State-Space Shortest Path", "Resource Constraint"],
    companies=["Uber", "Google"],
    shape="wgraph_tc", ret="long",
    todo="best[t][v] = cheapest way to be at v having used exactly t time; relax edges in increasing t (every road takes >= 1)",
    description=(
        "A courier crosses a city of `n` junctions. Road `u v time cost` (two-way) takes `time` "
        "minutes and costs `cost` in tolls. Print the smallest total toll to get from junction `0` "
        "to junction `n − 1` in **at most `T` minutes**, or `-1` if it cannot be done.\n\n"
        "### Input\nLine 1: `n m T`.\nNext `m` lines: `u v time cost`.\n\n### Output\nThe smallest toll, or `-1`."
    ),
    constraints="2 ≤ n ≤ 200\n0 ≤ m ≤ 1000\n1 ≤ T ≤ 1000\n1 ≤ time ≤ 1000, 0 ≤ cost ≤ 1000",
    hints=[
        "Cheapest ignoring time might be too slow; fastest might be too expensive. One number per junction cannot hold both.",
        "Make the state (junction, minutes used). Its best toll is well defined, and moving along a road goes from (u, t) to (v, t + time).",
        "Every road takes at least one minute, so states only move to larger t: fill best[t][v] for t = 0, 1, …, T in order. The answer is the minimum over t ≤ T of best[t][n − 1].",
    ],
    opt=("O(T · (n + m))", "O(T · n)",
         "Each (time, junction) state relaxes its roads once."),
    editorial=(
        "## The one thing this teaches\n**A resource limit is a state dimension.** \"Cheapest "
        "subject to time ≤ T\" is not a shortest path on the junctions, but it is one on (junction, "
        "time) — and because time only increases, those states can be processed in time order, "
        "like a DAG.\n\n"
        "## Approach\n```java\nlong[][] best = new long[T + 1][n];          // INF everywhere\nbest[0][0] = 0;\n"
        "for (int t = 0; t <= T; t++)\n    for (int u = 0; u < n; u++) {\n        if (best[t][u] == INF) continue;\n"
        "        for (int[] e : adj[u]) {                // {v, time, cost}\n            int nt = t + e[1];\n"
        "            if (nt <= T) best[nt][e[0]] = Math.min(best[nt][e[0]], best[t][u] + e[2]);\n        }\n    }\n"
        "answer = min over t of best[t][n - 1]\n```\n\n"
        "## Or Dijkstra over states\nWith large T and small costs, Dijkstra on cost over (junction, "
        "time) states with a pruning of dominated states works too. The time-ordered DP is simpler "
        "when T is small."
    ),
    py='''
def solve(n, edges, T):
    adj = [[] for _ in range(n)]
    for u, v, t, c in edges:
        adj[u].append((v, t, c))
        adj[v].append((u, t, c))
    INF = float("inf")
    best = [[INF] * n for _ in range(T + 1)]
    best[0][0] = 0
    for t in range(T + 1):
        row = best[t]
        for u in range(n):
            if row[u] == INF:
                continue
            for v, dt, c in adj[u]:
                nt = t + dt
                if nt <= T and row[u] + c < best[nt][v]:
                    best[nt][v] = row[u] + c
    ans = min(best[t][n - 1] for t in range(T + 1))
    return ans if ans != INF else -1
''',
    java='''
    static long solve(int n, int[][] edges, int T) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(new int[]{e[1], e[2], e[3]});
            adj.get(e[1]).add(new int[]{e[0], e[2], e[3]});
        }
        long INF = Long.MAX_VALUE / 4;
        long[][] best = new long[T + 1][n];
        for (long[] row : best) Arrays.fill(row, INF);
        best[0][0] = 0;
        for (int t = 0; t <= T; t++)
            for (int u = 0; u < n; u++) {
                if (best[t][u] == INF) continue;
                for (int[] e : adj.get(u)) {
                    int nt = t + e[1];
                    if (nt <= T && best[t][u] + e[2] < best[nt][e[0]]) best[nt][e[0]] = best[t][u] + e[2];
                }
            }
        long ans = INF;
        for (int t = 0; t <= T; t++) ans = Math.min(ans, best[t][n - 1]);
        return ans == INF ? -1 : ans;
    }
''',
    examples=[
        ("Example 1", "4 4 10\n0 1 5 1\n1 3 5 1\n0 2 2 20\n2 3 2 20\n"),
        ("Example 2", "4 4 9\n0 1 5 1\n1 3 5 1\n0 2 2 20\n2 3 2 20\n"),
    ],
    hidden=[
        ("Deadline too tight", "2 1 3\n0 1 4 0\n"),
        ("Free but slow, or fast but dear", "3 3 6\n0 2 6 50\n0 1 3 0\n1 2 4 0\n"),
        ("A detour through a toll-free loop", "4 5 12\n0 1 2 10\n1 3 2 10\n0 2 5 0\n2 3 5 0\n2 2 1 0\n"),
        ("Random", _tc_case(60, 200, 300, 441)),
        ("Large", _tc_case(200, 1000, 1000, 442)),
    ],
    expl=[
        "The cheap route 0 → 1 → 3 takes exactly 10 minutes and costs 2.",
        "With 9 minutes the cheap route is too slow; 0 → 2 → 3 takes 4 minutes and costs 40.",
    ],
    prereqs=[
        ("dijkstra", "Shortest paths over (junction, time) states."),
        ("dp", "Time only increases, so the states can be filled in time order."),
    ],
)


_p(
    "dag-shortest-negative", "Downhill With Tailwinds", "Medium",
    topics=["Graph", "Shortest Path", "Topological Sort"], subtopics=["DAG Shortest Path", "Negative Weights"],
    companies=["Google", "Amazon"],
    shape="wgraph", ret="String",
    todo="topological order, dist[0] = 0, then relax every edge in that order; negative weights are fine on a DAG",
    description=(
        "A glider route network has `n` waypoints and `m` one-way legs `u v w`; the network has no "
        "cycles. A leg costs `w` units of energy, and with a tailwind `w` can be negative. For each "
        "waypoint print the least energy needed to reach it from waypoint `0`, or `INF` if it "
        "cannot be reached.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n### Output\n`n` values on one line."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\n-10^4 ≤ w ≤ 10^4\nThe legs form no cycle.",
    hints=[
        "Dijkstra is off the table: negative weights break it. Bellman-Ford works but is O(n · m).",
        "In a DAG the order in which distances become final is known in advance: a topological order.",
        "Relax every outgoing edge of each vertex in topological order — once. Skip vertices still at INF.",
    ],
    opt=("O(n + m)", "O(n + m)",
         "One topological sort and one relaxation per edge."),
    editorial=(
        "## The one thing this teaches\n**The DAG removes the hard part.** Dijkstra needs "
        "non-negative weights and Bellman-Ford needs n rounds because, in general, you do not know "
        "which vertex is final. In a DAG, a topological order tells you — so one pass works, with "
        "any weights.\n\n"
        "## Approach\n```java\ndist[0] = 0;                                   // INF elsewhere\nfor (int u : topoOrder) {\n"
        "    if (dist[u] == INF) continue;\n    for (int[] e : adj[u]) dist[e[0]] = Math.min(dist[e[0]], dist[u] + e[1]);\n}\n```"
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v, w in edges:
        adj[u].append((v, w))
        indeg[v] += 1
    INF = float("inf")
    dist = [INF] * n
    dist[0] = 0
    q = deque(v for v in range(n) if indeg[v] == 0)
    while q:
        u = q.popleft()
        for v, w in adj[u]:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return " ".join("INF" if d == INF else str(d) for d in dist)
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); indeg[e[1]]++; }
        long INF = Long.MAX_VALUE / 4;
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        dist[0] = 0;
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int[] e : adj.get(u)) {
                if (dist[u] != INF && dist[u] + e[1] < dist[e[0]]) dist[e[0]] = dist[u] + e[1];
                if (--indeg[e[0]] == 0) q.add(e[0]);
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(dist[i] == INF ? "INF" : String.valueOf(dist[i]));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _wcase(5, [(0, 1, 4), (0, 2, 2), (2, 1, -3), (1, 3, 2), (2, 3, 5), (3, 4, -1)])),
        ("Example 2", _wcase(3, [(1, 2, -5)])),
    ],
    hidden=[
        ("One waypoint", "1 0\n"),
        ("All negative", _wcase(4, [(0, 1, -1), (1, 2, -1), (2, 3, -1), (0, 3, -2)])),
        ("Unreachable source of cheap legs", _wcase(4, [(1, 2, -100), (0, 2, 5), (2, 3, 1)])),
        ("Random", _wcase(300, [(u, v, w) for (u, v), w in zip(_rand_dag(300, 1200, _Lcg(451)), _lcg_ints(452, 1200, -100, 100))])),
        ("Large", _wcase(50000, [(u, v, w) for (u, v), w in zip(_rand_dag(50000, 150000, _Lcg(453)), _lcg_ints(454, 150000, -10000, 10000))])),
    ],
    expl=[
        "0 → 2 → 1 costs 2 − 3 = −1, beating the direct 4; then 1 → 3 is 1 and 3 → 4 is 0.",
        "Nothing leaves waypoint 0; the −5 leg starts somewhere unreachable.",
    ],
    prereqs=[
        ("topo", "A topological order finalises each waypoint before its legs are relaxed."),
        ("bellman_ford", "Why general negative weights need n rounds — and why a DAG needs one."),
    ],
)


def _reach_case(n, m, q, seed):
    rng = _Lcg(seed)
    edges = _rand_graph(n, m, rng, directed=True)
    qs = [(rng.randint(0, n - 1), rng.randint(0, n - 1)) for _ in range(q)]
    return (f"{n} {len(edges)} {q}\n" + "".join(f"{u} {v}\n" for u, v in edges)
            + "".join(f"{a} {b}\n" for a, b in qs))


_p(
    "reachability-queries", "Can You Get There From Here", "Medium",
    topics=["Graph", "Breadth-First Search"], subtopics=["Transitive Closure", "Reachability"],
    companies=["Google", "Microsoft"],
    shape="graph_q", ret="String",
    todo="precompute reach[s] with one BFS per source (or a bitset closure); answer each query by lookup",
    description=(
        "A directed graph has `n` vertices and `m` edges. For each of `q` queries `a b`, print "
        "whether `b` can be reached from `a` (a vertex always reaches itself).\n\n"
        "### Input\nLine 1: `n m q`.\nNext `m` lines: `u v`.\nNext `q` lines: `a b`.\n\n"
        "### Output\nOne line of `q` characters: `1` or `0`."
    ),
    constraints="1 ≤ n ≤ 400\n0 ≤ m ≤ 5000\n1 ≤ q ≤ 10^5",
    hints=[
        "One BFS per query is up to 10⁵ · (n + m) — too slow. But there are only n possible sources.",
        "Compute the whole reachability table once: a BFS from every vertex is n · (n + m) ≈ 2 · 10⁶.",
        "Floyd–Warshall's triple loop with booleans (reach[i][j] |= reach[i][k] && reach[k][j]) is the same table in O(n³); with bitsets it is n³ / 64.",
    ],
    opt=("O(n · (n + m) + q)", "O(n²)",
         "n BFS runs fill the table; each query is a lookup."),
    editorial=(
        "## The one thing this teaches\n**Precompute when the questions outnumber the answers.** "
        "There are only n² possible (a, b) pairs; with q far larger, computing all of them once is "
        "cheaper than answering each on demand.\n\n"
        "## Approach\n```java\nboolean[][] reach = new boolean[n][n];\nfor (int s = 0; s < n; s++) bfs(s, reach[s]);\n"
        "for (int[] qu : queries) out.append(reach[qu[0]][qu[1]] ? '1' : '0');\n```\n\n"
        "## The closure view\n`reach` is the transitive closure of the graph. Warshall's algorithm "
        "computes it with k outermost — the same loop order, and for the same reason, as "
        "Floyd–Warshall."
    ),
    py='''
def solve(n, edges, queries):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    reach = []
    for s in range(n):
        seen = [False] * n
        seen[s] = True
        st = [s]
        while st:
            u = st.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    st.append(v)
        reach.append(seen)
    return "".join("1" if reach[a][b] else "0" for a, b in queries)
''',
    java='''
    static String solve(int n, int[][] edges, int[][] queries) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        boolean[][] reach = new boolean[n][n];
        ArrayDeque<Integer> st = new ArrayDeque<>();
        for (int s = 0; s < n; s++) {
            boolean[] seen = reach[s];
            seen[s] = true;
            st.push(s);
            while (!st.isEmpty()) {
                int u = st.pop();
                for (int v : adj.get(u)) if (!seen[v]) { seen[v] = true; st.push(v); }
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int[] q : queries) sb.append(reach[q[0]][q[1]] ? '1' : '0');
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5 5 5\n0 1\n1 2\n2 0\n2 3\n4 3\n0 3\n3 0\n4 4\n1 0\n4 2\n"),
        ("Example 2", "2 0 2\n0 1\n1 1\n"),
    ],
    hidden=[
        ("One vertex", "1 0 1\n0 0\n"),
        ("A chain, both directions", "4 3 4\n0 1\n1 2\n2 3\n0 3\n3 0\n1 3\n2 1\n"),
        ("Self-loops", "3 2 3\n1 1\n1 2\n0 2\n1 2\n2 1\n"),
        ("Random", _reach_case(100, 250, 500, 461)),
        ("Large", _reach_case(400, 5000, 100000, 462)),
    ],
    expl=[
        "0, 1, 2 form a cycle that leads to 3, so 0 reaches 3 but 3 reaches nothing; 4 reaches itself; 1 reaches 0 around the cycle; 4 reaches only 3 and itself.",
        "No edges: 0 cannot reach 1, but 1 reaches itself.",
    ],
    prereqs=[
        ("bfs", "One traversal per source fills one row of the table."),
        ("graph_repr", "A directed adjacency list."),
    ],
)
