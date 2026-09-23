# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 56 — Trees & Graphs, part 4: union-find and spanning trees.
#
#   islands-after-each-add       online union-find on a grid: +1 per new cell, -1 per merge
#   height-claims                weighted union-find: every node knows its offset to its root
#   first-odd-cycle              parity union-find: bipartite, one edge at a time
#   limited-weight-reachability  offline: sort the queries and the edges by weight together
#   cheapest-road-network        Kruskal, and -1 when the graph is not connected
#   power-grid-generators        the virtual node: a generator is an edge to "the grid"
#   mst-forced-edge              Kruskal with one edge taken first
#   bottleneck-route             the MST answers every minimise-the-maximum path question
#
# Defines the shapes `rc_cells`, `wgraph_q3`, `arr_wgraph` and `wgraph_uq`.
# ===========================================================================

# "r c k", then k lines "i j"
_SHAPES["rc_cells"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nr, c, k = d[0], d[1], d[2]\n"
       "cells = [(d[3 + 2 * i], d[4 + 2 * i]) for i in range(k)]\n",
    py_params="r, c, cells",
    js=_JS_NUMS + "const r = Number(d[0]), c = Number(d[1]), k = Number(d[2]);\n"
       "const cells = Array.from({ length: k }, (_, i) => [Number(d[3 + 2 * i]), Number(d[4 + 2 * i])]);\n",
    js_params="r, c, cells",
    java="        int r = sc.nextInt(), c = sc.nextInt(), k = sc.nextInt();\n        int[][] cells = new int[k][2];\n"
         "        for (int i = 0; i < k; i++) { cells[i][0] = sc.nextInt(); cells[i][1] = sc.nextInt(); }\n",
    java_params="int r, int c, int[][] cells", java_args="r, c, cells",
)
# "n m q", then m lines "u v w", then q lines "a b x"
_SHAPES["wgraph_q3"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m, q = d[0], d[1], d[2]\n"
       "edges = [(d[3 + 3 * i], d[4 + 3 * i], d[5 + 3 * i]) for i in range(m)]\n"
       "_b = 3 + 3 * m\nqueries = [(d[_b + 3 * i], d[_b + 1 + 3 * i], d[_b + 2 + 3 * i]) for i in range(q)]\n",
    py_params="n, edges, queries",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), q = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2].map(j => Number(d[3 + 3 * i + j])));\n"
       "const queries = Array.from({ length: q }, (_, i) => [0, 1, 2].map(j => Number(d[3 + 3 * m + 3 * i + j])));\n",
    js_params="n, edges, queries",
    java="        int n = sc.nextInt(), m = sc.nextInt(), q = sc.nextInt();\n        int[][] edges = new int[m][3];\n"
         "        for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n"
         "        int[][] queries = new int[q][3];\n"
         "        for (int i = 0; i < q; i++) for (int j = 0; j < 3; j++) queries[i][j] = sc.nextInt();\n",
    java_params="int n, int[][] edges, int[][] queries", java_args="n, edges, queries",
)
# "n m", then n integers, then m lines "u v w"
_SHAPES["arr_wgraph"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m = d[0], d[1]\na = d[2:2 + n]\n"
       "edges = [(d[2 + n + 3 * i], d[3 + n + 3 * i], d[4 + n + 3 * i]) for i in range(m)]\n",
    py_params="a, edges",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]);\nconst a = d.slice(2, 2 + n).map(Number);\n"
       "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2].map(j => Number(d[2 + n + 3 * i + j])));\n",
    js_params="a, edges",
    java="        int n = sc.nextInt(), m = sc.nextInt();\n        int[] a = new int[n];\n"
         "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n        int[][] edges = new int[m][3];\n"
         "        for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n",
    java_params="int[] a, int[][] edges", java_args="a, edges",
)


def _wcase(n, edges):
    return f"{n} {len(edges)}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)


def _connected_wgraph(n, extra, seed, wlo=1, whi=100):
    """A random spanning tree plus `extra` more edges — always connected."""
    rng = _Lcg(seed)
    tree = [(u, v, rng.randint(wlo, whi)) for u, v in _rand_tree_edges(n, rng)]
    more = _rand_graph(n, extra, rng, wlo=wlo, whi=whi)
    have = {(min(u, v), max(u, v)) for u, v, _ in tree}
    more = [e for e in more if (min(e[0], e[1]), max(e[0], e[1])) not in have]
    return rng.shuffle(tree + more)


_p(
    "islands-after-each-add", "Land Rising From the Sea", "Medium",
    topics=["Union Find", "Matrix"], subtopics=["Union Find", "Online Connectivity", "Grid"],
    companies=["Google", "Uber", "Amazon"],
    shape="rc_cells", ret="String",
    todo="each new land cell adds one island, then unions with each land neighbour; every union that actually merges removes one",
    description=(
        "A map of `r × c` cells starts as all water. One at a time, `k` cells rise out of the sea "
        "and become land. After each rise, print the number of **islands** — groups of land "
        "cells joined up, down, left or right. A cell may rise twice; the second time changes "
        "nothing.\n\n"
        "### Input\nLine 1: `r c k`.\nNext `k` lines: `i j`, the cell that rises (0-indexed).\n\n"
        "### Output\n`k` numbers on one line: the island count after each rise."
    ),
    constraints="1 ≤ r, c ≤ 1000, r · c ≤ 10^5\n1 ≤ k ≤ 10^5",
    hints=[
        "Recounting islands with a flood fill after every rise is O(k · r · c).",
        "Each rise can only *add* one island and *merge* existing ones. Union-find tracks merges cheaply: cell (i, j) is element i · c + j.",
        "count += 1 for the new cell; for each land neighbour, if union() actually joins two different sets, count -= 1. Skip a cell that is already land.",
    ],
    opt=("O(k · α(r·c))", "O(r · c)",
         "At most four unions per rise, each effectively constant with path compression and union by size."),
    editorial=(
        "## The one thing this teaches\n**Union-find answers connectivity while the graph grows.** "
        "BFS answers it for a fixed graph. When edges only ever appear, a DSU maintains the "
        "components incrementally, and `union` returning whether it merged is the counter's update.\n\n"
        "## Approach\n```java\nfor (int[] cell : cells) {\n    int id = cell[0] * c + cell[1];\n"
        "    if (land[id]) { out.add(count); continue; }   // already risen\n    land[id] = true;\n    count++;\n"
        "    for (int[] d : DIRS) {\n        int ni = cell[0] + d[0], nj = cell[1] + d[1];\n"
        "        if (inside && land[ni * c + nj] && union(id, ni * c + nj)) count--;\n    }\n    out.add(count);\n}\n```\n\n"
        "## Why each merge is exactly −1\nA merge joins two islands into one. Two neighbours that "
        "were already in the same island (the new cell closes a loop) make `union` return false, "
        "and the count must not move."
    ),
    py='''
def solve(r, c, cells):
    parent = list(range(r * c))
    size = [1] * (r * c)
    land = [False] * (r * c)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a == b:
            return False
        if size[a] < size[b]:
            a, b = b, a
        parent[b] = a
        size[a] += size[b]
        return True

    count, out = 0, []
    for i, j in cells:
        cid = i * c + j
        if not land[cid]:
            land[cid] = True
            count += 1
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < r and 0 <= nj < c and land[ni * c + nj] and union(cid, ni * c + nj):
                    count -= 1
        out.append(count)
    return " ".join(map(str, out))
''',
    java='''
    static int[] parent, size;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static boolean union(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (size[a] < size[b]) { int t = a; a = b; b = t; }
        parent[b] = a;
        size[a] += size[b];
        return true;
    }

    static String solve(int r, int c, int[][] cells) {
        parent = new int[r * c];
        size = new int[r * c];
        boolean[] land = new boolean[r * c];
        for (int i = 0; i < r * c; i++) { parent[i] = i; size[i] = 1; }
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int count = 0;
        StringBuilder sb = new StringBuilder();
        for (int[] cell : cells) {
            int id = cell[0] * c + cell[1];
            if (!land[id]) {
                land[id] = true;
                count++;
                for (int[] d : dirs) {
                    int ni = cell[0] + d[0], nj = cell[1] + d[1];
                    if (ni >= 0 && ni < r && nj >= 0 && nj < c && land[ni * c + nj] && union(id, ni * c + nj))
                        count--;
                }
            }
            if (sb.length() > 0) sb.append(' ');
            sb.append(count);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "3 4 6\n0 0\n0 2\n1 1\n0 1\n2 3\n1 2\n"),
        ("Example 2", "2 2 3\n1 1\n1 1\n0 0\n"),
    ],
    hidden=[
        ("One cell", "1 1 1\n0 0\n"),
        ("A ring closes", "3 3 8\n0 0\n0 1\n0 2\n1 2\n2 2\n2 1\n2 0\n1 0\n"),
        ("Centre joins four", "3 3 5\n0 1\n1 0\n1 2\n2 1\n1 1\n"),
        ("Checkerboard", "4 4 16\n" + "".join(f"{i} {j}\n" for i in range(4) for j in range(4) if (i + j) % 2 == 0)
         + "".join(f"{i} {j}\n" for i in range(4) for j in range(4) if (i + j) % 2 == 1)),
        ("One row", "1 10 10\n" + "".join(f"0 {j}\n" for j in (0, 2, 4, 6, 8, 9, 7, 5, 3, 1))),
        ("Random", "20 25 300\n" + "".join(f"{a % 20} {b % 25}\n" for a, b in zip(_lcg_ints(221, 300, 0, 99), _lcg_ints(222, 300, 0, 99)))),
        ("Large", "300 300 60000\n" + "".join(f"{a} {b}\n" for a, b in zip(_lcg_ints(223, 60000, 0, 299), _lcg_ints(224, 60000, 0, 299)))),
    ],
    expl=[
        "(0, 0), (0, 2) and (1, 1) touch only diagonally: 1, 2, 3. (0, 1) joins all three: 1. (2, 3) starts a new island: 2. (1, 2) joins the big island, not (2, 3): still 2.",
        "(1, 1) makes one island; rising again changes nothing; (0, 0) touches it only diagonally, so two islands.",
    ],
    prereqs=[
        ("union_find", "Find with path compression, union by size, and union returning whether it merged."),
        ("grid", "Cell (i, j) as the single index i · c + j."),
    ],
)


_p(
    "height-claims", "Which Claim Is the Lie?", "Hard",
    topics=["Union Find"], subtopics=["Weighted Union Find", "Consistency"],
    companies=["Google", "Microsoft"],
    shape="updates", ret="int",
    todo="weighted DSU: diff[x] = height(x) - height(parent[x]); on a claim, if a and b share a root check the implied difference, else link the roots with the right offset",
    description=(
        "Surveyors measure `n` hilltops (0 to `n − 1`). Each of `q` claims `a b d` says: hilltop "
        "`b` is exactly `d` metres higher than hilltop `a` (`d` may be negative). Claims arrive in "
        "order. Print the number (1-based) of the **first** claim that contradicts the claims "
        "before it, or `0` if they are all consistent.\n\n"
        "### Input\nLine 1: `n q`.\nNext `q` lines: `a b d`.\n\n### Output\nThe index of the first "
        "contradicting claim, or `0`."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ q ≤ 2·10^5\n0 ≤ a, b < n\n-10^4 ≤ d ≤ 10^4\nA claim with a = b is contradictory unless d = 0.",
    hints=[
        "Claims only relate hilltops; absolute heights never matter. Group hilltops whose height difference is known — union-find.",
        "Store for each node its height relative to its parent. During find, accumulate the offsets along the path, so each node learns its height relative to its root (and compress).",
        "Claim a b d: if a and b have the same root, check off[b] − off[a] == d. Otherwise attach root(b) under root(a) with offset off[a] + d − off[b].",
    ],
    opt=("O(q · α(n))", "O(n)",
         "Each claim is two finds and possibly one link."),
    editorial=(
        "## The one thing this teaches\n**Union-find can carry a value along each edge.** A "
        "plain DSU remembers *that* two things are connected. A weighted DSU also remembers "
        "*how*: each node stores its offset to its parent, and find returns the offset to the root.\n\n"
        "## Approach\n```java\nint find(int x) {                         // also sets off[x] relative to the root\n"
        "    if (parent[x] == x) return x;\n    int r = find(parent[x]);\n    off[x] += off[parent[x]];               // parent's offset is now relative to r\n"
        "    parent[x] = r;\n    return r;\n}\n// claim a b d:  h[b] - h[a] = d\nint ra = find(a), rb = find(b);\n"
        "if (ra == rb) { if (off[b] - off[a] != d) return i; }\nelse { parent[rb] = ra; off[rb] = off[a] + d - off[b]; }\n```\n\n"
        "## Where the link offset comes from\nWe need h[b] − h[a] = d with h[x] = off[x] + h[root]. "
        "After linking rb under ra: off[b] + off[rb] − off[a] = d, so off[rb] = off[a] + d − off[b].\n\n"
        "## Recursion depth\nWithout union by size a chain can be 10⁵ deep before compression — "
        "write find iteratively (two passes) or link by size."
    ),
    py='''
def solve(n, ups):
    parent = list(range(n))
    off = [0] * n

    def find(x):
        path = []
        while parent[x] != x:
            path.append(x)
            x = parent[x]
        root = x
        # offsets relative to the root, from the node nearest the root outwards
        for y in reversed(path):
            if parent[y] != root:
                off[y] += off[parent[y]]
            parent[y] = root
        return root

    for i, (a, b, d) in enumerate(ups, 1):
        ra, rb = find(a), find(b)
        if ra == rb:
            if off[b] - off[a] != d:
                return i
        else:
            parent[rb] = ra
            off[rb] = off[a] + d - off[b]
    return 0
''',
    java='''
    static int[] parent;
    static long[] off;

    static int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        // collect the path, then fix offsets from the top down
        ArrayDeque<Integer> path = new ArrayDeque<>();
        for (int y = x; parent[y] != y; y = parent[y]) path.push(y);
        while (!path.isEmpty()) {
            int y = path.pop();
            if (parent[y] != root) off[y] += off[parent[y]];
            parent[y] = root;
        }
        return root;
    }

    static int solve(int n, int[][] ups) {
        parent = new int[n];
        off = new long[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        for (int i = 0; i < ups.length; i++) {
            int a = ups[i][0], b = ups[i][1], d = ups[i][2];
            int ra = find(a), rb = find(b);
            if (ra == rb) {
                if (off[b] - off[a] != d) return i + 1;
            } else {
                parent[rb] = ra;
                off[rb] = off[a] + d - off[b];
            }
        }
        return 0;
    }
''',
    examples=[
        ("Example 1", "4 4\n0 1 5\n1 2 -3\n0 2 2\n2 3 1\n"),
        ("Example 2", "3 3\n0 1 4\n1 2 4\n2 0 -7\n"),
    ],
    hidden=[
        ("Self claim, zero", "2 2\n1 1 0\n0 1 3\n"),
        ("Self claim, nonzero", "2 2\n0 1 3\n1 1 2\n"),
        ("Reversed pair", "2 2\n0 1 6\n1 0 -6\n"),
        ("Reversed pair, wrong", "2 2\n0 1 6\n1 0 6\n"),
        ("Two groups joined late", "6 5\n0 1 1\n2 3 1\n4 5 1\n1 2 1\n0 3 4\n"),
        ("Consistent chain", "1000 999\n" + "".join(f"{i + 1} {i} -2\n" for i in range(999))),
    ],
    expl=[
        "Claims 1 and 2 put hilltop 2 at 5 − 3 = 2 above hilltop 0, which claim 3 agrees with; claim 4 is new information. All consistent.",
        "Going round 0 → 1 → 2 adds 8 metres, so 2 → 0 must be −8, not −7: claim 3.",
    ],
    prereqs=[
        ("union_find", "Find with path compression, extended to carry each node's offset to its root."),
        ("graph_cycle", "A claim inside one group closes a cycle, and a cycle's offsets must add to zero."),
    ],
)


def _height_case(n, q, seed, lie_at):
    """Consistent claims from hidden heights, with one lie at `lie_at` (1-based) if > 0."""
    rng = _Lcg(seed)
    h = [rng.randint(-5000, 5000) for _ in range(n)]
    lines = []
    for i in range(1, q + 1):
        a, b = rng.randint(0, n - 1), rng.randint(0, n - 1)
        d = h[b] - h[a]
        if i == lie_at:
            d += rng.randint(1, 5)
        lines.append(f"{a} {b} {d}")
    return f"{n} {q}\n" + "\n".join(lines) + "\n"


DEFS[-1]["cases"] += [
    ("hidden", "Random consistent", _height_case(50, 200, 231, 0)),
    ("hidden", "Random lie", _height_case(50, 200, 232, 150)),
    ("hidden", "Large lie", _height_case(100000, 200000, 233, 190000)),
]


_p(
    "first-odd-cycle", "When Two Teams Stop Working", "Hard",
    topics=["Union Find", "Graph"], subtopics=["Union Find", "Bipartite", "Parity"],
    companies=["Google", "Meta"],
    shape="graph", ret="int",
    todo="parity DSU: par[x] = side of x relative to its parent; an edge inside one set whose ends are on the same side makes an odd cycle",
    description=(
        "A coach wants to split `n` players into two teams so that every pair of **rivals** is on "
        "opposite teams. Rivalries are announced one at a time. Print the number (1-based) of the "
        "first rivalry after which **no** valid split exists any more, or `0` if a split always "
        "exists.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v`, a rivalry, in announcement order.\n\n"
        "### Output\nThe index of the first impossible rivalry, or `0`."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ m ≤ 2·10^5\nu ≠ v",
    hints=[
        "A split exists exactly when the rivalry graph has no odd cycle — it is bipartite.",
        "Re-running a BFS two-colouring after each rivalry is O(m · (n + m)). Keep the colouring *incrementally* instead.",
        "Union-find with a parity bit: each node stores whether it is on the same team as its parent. For rivals u, v: in different sets, link the roots so u and v end up on opposite sides; in the same set, they must already be on opposite sides — otherwise this rivalry closes an odd cycle.",
    ],
    opt=("O(m · α(n))", "O(n)",
         "Two finds per rivalry."),
    editorial=(
        "## The one thing this teaches\n**Parity is an offset modulo 2.** The weighted DSU of "
        "`height-claims` with every difference taken mod 2 answers \"same team or opposite?\" for "
        "any two players in a group — and a rivalry between two players already known to be on "
        "the same team is the odd cycle.\n\n"
        "## Approach\n```java\nint find(int x) {                       // par[x] becomes x's side relative to the root\n"
        "    if (parent[x] == x) return x;\n    int r = find(parent[x]);\n    par[x] ^= par[parent[x]];\n    parent[x] = r;\n    return r;\n}\n"
        "// rivals u, v\nint ru = find(u), rv = find(v);\nif (ru == rv) { if (par[u] == par[v]) return i; }\n"
        "else { parent[rv] = ru; par[rv] = par[u] ^ par[v] ^ 1; }\n```\n\n"
        "## Where `par[u] ^ par[v] ^ 1` comes from\nAfter the link v's side relative to ru is "
        "par[v] ^ par[rv]; we need it to differ from par[u], so par[rv] = par[u] ^ par[v] ^ 1."
    ),
    py='''
def solve(n, edges):
    parent = list(range(n))
    par = [0] * n

    def find(x):
        path = []
        while parent[x] != x:
            path.append(x)
            x = parent[x]
        root = x
        for y in reversed(path):
            if parent[y] != root:
                par[y] ^= par[parent[y]]
            parent[y] = root
        return root

    for i, (u, v) in enumerate(edges, 1):
        ru, rv = find(u), find(v)
        if ru == rv:
            if par[u] == par[v]:
                return i
        else:
            parent[rv] = ru
            par[rv] = par[u] ^ par[v] ^ 1
    return 0
''',
    java='''
    static int[] parent, par;

    static int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        ArrayDeque<Integer> path = new ArrayDeque<>();
        for (int y = x; parent[y] != y; y = parent[y]) path.push(y);
        while (!path.isEmpty()) {
            int y = path.pop();
            if (parent[y] != root) par[y] ^= par[parent[y]];
            parent[y] = root;
        }
        return root;
    }

    static int solve(int n, int[][] edges) {
        parent = new int[n];
        par = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        for (int i = 0; i < edges.length; i++) {
            int u = edges[i][0], v = edges[i][1];
            int ru = find(u), rv = find(v);
            if (ru == rv) {
                if (par[u] == par[v]) return i + 1;
            } else {
                parent[rv] = ru;
                par[rv] = par[u] ^ par[v] ^ 1;
            }
        }
        return 0;
    }
''',
    examples=[
        ("Example 1", _graph_case(5, [(0, 1), (1, 2), (3, 4), (2, 3), (4, 0)])),
        ("Example 2", _graph_case(4, [(0, 1), (1, 2), (2, 3), (3, 0)])),
    ],
    hidden=[
        ("Triangle", _graph_case(3, [(0, 1), (1, 2), (2, 0)])),
        ("Repeated rivalry is fine", _graph_case(2, [(0, 1), (1, 0), (0, 1)])),
        ("Two components merged oddly", _graph_case(6, [(0, 1), (2, 3), (4, 5), (1, 2), (3, 4), (5, 0), (0, 3)])),
        ("Long even cycle then a chord", _graph_case(10, [(i, (i + 1) % 10) for i in range(10)] + [(0, 2)])),
        ("Random bipartite", _graph_case(1000, [(2 * a, 2 * b + 1) for a, b in zip(_lcg_ints(241, 3000, 0, 499), _lcg_ints(242, 3000, 0, 499))])),
        ("Large, odd at the end", _graph_case(60000, [(2 * a, 2 * b + 1) for a, b in zip(_lcg_ints(243, 150000, 0, 29999), _lcg_ints(244, 150000, 0, 29999))] + [(0, 2)])),
    ],
    expl=[
        "The first four rivalries form the path 0-1-2-3-4. Rivalry 5 joins 4 and 0 — a cycle of five, which is odd.",
        "0-1-2-3-0 is a cycle of four: teams {0, 2} and {1, 3} always work.",
    ],
    prereqs=[
        ("union_find", "Union-find with a parity bit on each node, relative to its parent."),
        ("graph_cycle", "A graph can be two-coloured exactly when it has no odd cycle."),
    ],
)


_p(
    "limited-weight-reachability", "Bridges Under the Weight Limit", "Hard",
    topics=["Union Find", "Graph", "Sorting"], subtopics=["Union Find", "Offline Queries", "Sorting"],
    companies=["Google", "Amazon"],
    shape="wgraph_q3", ret="String",
    todo="sort edges by weight and queries by limit; for each query, union every edge lighter than its limit, then ask find(a) == find(b)",
    description=(
        "`n` islands are joined by `m` two-way bridges; bridge `u v w` can carry loads below "
        "`w` tonnes — a load of exactly `w` is too heavy. Each of `q` trucks `a b x` weighs `x` "
        "tonnes: can it drive from island `a` to island `b` using only bridges that can carry it "
        "(every bridge on the way must have `w > x`)?\n\n"
        "### Input\nLine 1: `n m q`.\nNext `m` lines: `u v w`.\nNext `q` lines: `a b x`.\n\n"
        "### Output\nOne line of `q` characters: `1` if truck `i` can make the trip, `0` if not."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 10^5\n1 ≤ q ≤ 10^5\n1 ≤ w, x ≤ 10^9",
    hints=[
        "One BFS per truck, ignoring light bridges, is O(q · (n + m)) — too slow.",
        "A truck of weight x may use exactly the bridges with w > x. Heavier trucks may use a subset of what lighter ones may.",
        "Answer the trucks from heaviest to lightest (offline). Keep bridges sorted by capacity, and before each truck add — union — every bridge whose capacity exceeds its weight. Then one find per truck.",
    ],
    opt=("O((m + q) log(m + q))", "O(n + m + q)",
         "Two sorts, then each bridge is unioned once and each truck costs two finds."),
    editorial=(
        "## The one thing this teaches\n**Offline: reorder the questions to suit the structure.** "
        "Union-find can add edges but never remove them. Sorting the trucks from heaviest to "
        "lightest means the usable bridges only ever *grow*, which is exactly what it supports. "
        "Remember each truck's original index so the answers go back in order.\n\n"
        "## Approach\n```java\nsort edges by w, descending;\nsort query indices by x, descending;\nint e = 0;\n"
        "for (int qi : order) {\n    while (e < m && edges[e][2] > queries[qi][2]) { union(edges[e][0], edges[e][1]); e++; }\n"
        "    ans[qi] = find(queries[qi][0]) == find(queries[qi][1]) ? '1' : '0';\n}\n```\n\n"
        "## The strict inequality\nA bridge of capacity exactly x is unusable, so the loop adds "
        "bridges with `w > x`. With `>=` every test that sits on a boundary would flip."
    ),
    py='''
def solve(n, edges, queries):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    es = sorted(edges, key=lambda e: -e[2])
    order = sorted(range(len(queries)), key=lambda i: -queries[i][2])
    ans = ["0"] * len(queries)
    e = 0
    for qi in order:
        a, b, x = queries[qi]
        while e < len(es) and es[e][2] > x:
            ra, rb = find(es[e][0]), find(es[e][1])
            if ra != rb:
                parent[ra] = rb
            e += 1
        if find(a) == find(b):
            ans[qi] = "1"
    return "".join(ans)
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static String solve(int n, int[][] edges, int[][] queries) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        int[][] es = edges.clone();
        Arrays.sort(es, (p, q) -> Integer.compare(q[2], p[2]));
        Integer[] order = new Integer[queries.length];
        for (int i = 0; i < order.length; i++) order[i] = i;
        Arrays.sort(order, (p, q) -> Integer.compare(queries[q][2], queries[p][2]));
        char[] ans = new char[queries.length];
        int e = 0;
        for (int qi : order) {
            int x = queries[qi][2];
            while (e < es.length && es[e][2] > x) {
                int ra = find(es[e][0]), rb = find(es[e][1]);
                if (ra != rb) parent[ra] = rb;
                e++;
            }
            ans[qi] = find(queries[qi][0]) == find(queries[qi][1]) ? '1' : '0';
        }
        return new String(ans);
    }
''',
    examples=[
        ("Example 1", "4 4 4\n0 1 10\n1 2 5\n2 3 8\n0 3 3\n0 2 4\n0 2 5\n3 1 4\n1 1 100\n"),
        ("Example 2", "3 0 2\n0 1 1\n2 2 1\n"),
    ],
    hidden=[
        ("Exactly the limit", "2 1 2\n0 1 7\n0 1 7\n0 1 6\n"),
        ("Parallel bridges", "2 2 3\n0 1 3\n0 1 9\n0 1 2\n0 1 5\n1 0 9\n"),
        ("Chain", "5 4 4\n0 1 9\n1 2 8\n2 3 7\n3 4 6\n0 4 5\n0 4 6\n1 3 6\n2 3 6\n"),
    ],
    expl=[
        "Truck 1 (4 t) crosses 0-1 (10) and 1-2 (5): yes. Truck 2 (5 t) cannot use 1-2 (capacity exactly 5) and 0-3 is too weak, 2-3 needs 3 first: no. Truck 3 (4 t) goes 3-2-1: yes. Truck 4 stays on island 1: yes.",
        "No bridges: truck 1 cannot leave island 0, and truck 2 is already where it is going.",
    ],
    prereqs=[
        ("union_find", "Union-find only adds edges — so order the queries so that edges only get added."),
        ("sorting", "Sort bridges and trucks by weight, keeping the trucks' original positions."),
    ],
)


def _lwr_case(n, m, q, seed, whi=10**9):
    rng = _Lcg(seed)
    edges = _rand_graph(n, m, rng, wlo=1, whi=whi)
    qs = [(rng.randint(0, n - 1), rng.randint(0, n - 1), rng.randint(1, whi)) for _ in range(q)]
    return (f"{n} {len(edges)} {q}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)
            + "".join(f"{a} {b} {x}\n" for a, b, x in qs))


DEFS[-1]["cases"] += [
    ("hidden", "Random", _lwr_case(50, 120, 200, 251, whi=100)),
    ("hidden", "Large", _lwr_case(30000, 60000, 60000, 255)),
]


_p(
    "cheapest-road-network", "Pave the Fewest Kilometres", "Easy",
    topics=["Graph", "Minimum Spanning Tree"], subtopics=["Minimum Spanning Tree", "Kruskal", "Union Find"],
    companies=["Amazon", "Microsoft"],
    shape="wgraph", ret="long",
    todo="Kruskal: sort roads by cost, take each that joins two different groups (union returns true); -1 if fewer than n - 1 were taken",
    description=(
        "A county has `n` villages and `m` dirt roads; paving road `u v w` costs `w`. Pave a set "
        "of roads so that every village can reach every other on paved roads, as cheaply as "
        "possible. Print the total cost, or `-1` if even paving everything would not connect them.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n### Output\nThe minimum total cost, or `-1`."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 10^5\n1 ≤ w ≤ 10^6",
    hints=[
        "The cheapest connected set of roads never contains a cycle — drop the most expensive road of a cycle and everything stays connected. So you want a spanning tree.",
        "Kruskal: go through the roads from cheapest to dearest and pave a road exactly when its two villages are not yet connected.",
        "Union-find answers \"already connected?\". Count the roads you pave: fewer than n − 1 means the county cannot be connected. Total cost can reach 10¹⁰ — long.",
    ],
    opt=("O(m log m)", "O(n + m)",
         "The sort dominates; the unions are nearly constant each."),
    editorial=(
        "## The one thing this teaches\n**Kruskal's algorithm, and when it says no.** The "
        "greedy is safe because of the cut property; the union-find is what makes it fast; and "
        "counting the edges taken is the connectivity check for free.\n\n"
        "## Approach\n```java\nArrays.sort(edges, (a, b) -> Integer.compare(a[2], b[2]));\nlong total = 0;\nint taken = 0;\n"
        "for (int[] e : edges)\n    if (union(e[0], e[1])) { total += e[2]; taken++; }\n"
        "return taken == n - 1 ? total : -1;\n```\n\n"
        "## One village\nZero roads are needed and the answer is 0 — `taken == n − 1` holds "
        "with both sides zero."
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
    for u, v, w in sorted(edges, key=lambda e: e[2]):
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
        Arrays.sort(es, (a, b) -> Integer.compare(a[2], b[2]));
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
        ("One village", "1 0\n"),
        ("Self road", _wcase(2, [(0, 0, 1), (0, 1, 8)])),
        ("Parallel roads", _wcase(2, [(0, 1, 9), (1, 0, 4), (0, 1, 6)])),
        ("Equal costs", _wcase(4, [(0, 1, 5), (1, 2, 5), (2, 3, 5), (3, 0, 5), (0, 2, 5)])),
        ("Random", _wcase(100, _connected_wgraph(100, 300, 261, 1, 1000))),
        ("Large", _wcase(10000, _connected_wgraph(10000, 60000, 262, 1, 10**6))),
        ("Large, disconnected", _wcase(10000, [(u, v, w) for u, v, w in _connected_wgraph(10000, 60000, 263, 1, 10**6) if (u < 5000) == (v < 5000)])),
    ],
    expl=[
        "Take 1-2 (2) and 0-2 (3); 0-1 (4) would close a cycle; 2-3 (7) connects the last village: 12.",
        "Village 2 has no road at all.",
    ],
    prereqs=[
        ("mst", "Kruskal: cheapest edge first, skipping any that would close a cycle."),
        ("union_find", "\"Would this close a cycle?\" is \"are the ends already in one set?\"."),
    ],
)


_p(
    "power-grid-generators", "Generators or Cables", "Medium",
    topics=["Graph", "Minimum Spanning Tree"], subtopics=["Minimum Spanning Tree", "Virtual Node"],
    companies=["Google", "Amazon"],
    shape="arr_wgraph", ret="long",
    todo="add a virtual node n (the power source); a generator in town i is an edge (n, i, g[i]); the answer is the MST of the n + 1 nodes",
    description=(
        "`n` towns need electricity. Town `i` can build its own generator for `g[i]`, or be "
        "connected by cable to a town that has power; laying cable `u v w` costs `w`. Power flows "
        "through any number of cables. Print the minimum total cost to give every town power.\n\n"
        "### Input\nLine 1: `n m`.\nLine 2: `n` generator costs.\nNext `m` lines: `u v w`, a possible cable.\n\n"
        "### Output\nThe minimum total cost."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 10^5\n1 ≤ g[i], w ≤ 10^5",
    hints=[
        "If generators were free in one chosen town, this would be an MST. The trouble is that the number and placement of generators is part of the answer.",
        "Invent a town n that *is* the power station. Building a generator in town i is then the same as laying a cable from n to i costing g[i].",
        "Now every town must be connected to node n — an ordinary MST on n + 1 nodes, which always exists.",
    ],
    opt=("O((n + m) log(n + m))", "O(n + m)",
         "Kruskal over m + n edges."),
    editorial=(
        "## The one thing this teaches\n**The virtual node.** Two kinds of cost — per node and "
        "per edge — do not fit one algorithm, until the per-node cost becomes an edge to a node "
        "you invent. Then the problem is exactly the MST, and its correctness comes free.\n\n"
        "## Approach\n```java\nList<int[]> all = new ArrayList<>(Arrays.asList(edges));\n"
        "for (int i = 0; i < n; i++) all.add(new int[]{n, i, g[i]});   // generator = edge to the source\n"
        "return kruskal(n + 1, all);\n```\n\n"
        "## Why at least one generator is built\nThe MST must connect node n, so at least one "
        "\"generator edge\" is in it — the model cannot cheat by powering nothing."
    ),
    py='''
def solve(a, edges):
    n = len(a)
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    allE = list(edges) + [(n, i, a[i]) for i in range(n)]
    total = 0
    for u, v, w in sorted(allE, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static long solve(int[] a, int[][] edges) {
        int n = a.length;
        parent = new int[n + 1];
        for (int i = 0; i <= n; i++) parent[i] = i;
        int[][] all = new int[edges.length + n][];
        for (int i = 0; i < edges.length; i++) all[i] = edges[i];
        for (int i = 0; i < n; i++) all[edges.length + i] = new int[]{n, i, a[i]};
        Arrays.sort(all, (p, q) -> Integer.compare(p[2], q[2]));
        long total = 0;
        for (int[] e : all) {
            int ru = find(e[0]), rv = find(e[1]);
            if (ru != rv) { parent[ru] = rv; total += e[2]; }
        }
        return total;
    }
''',
    examples=[
        ("Example 1", "4 4\n5 8 9 3\n0 1 2\n1 2 3\n2 3 6\n0 3 7\n"),
        ("Example 2", "3 1\n1 1 1\n0 1 5\n"),
    ],
    hidden=[
        ("One town", "1 0\n42\n"),
        ("Cables everywhere are cheap", "5 4\n100 100 100 100 100\n0 1 1\n1 2 1\n2 3 1\n3 4 1\n"),
        ("Two cheap generators", "6 5\n1 50 50 50 50 1\n0 1 10\n1 2 10\n2 3 10\n3 4 10\n4 5 10\n"),
    ],
    expl=[
        "Generators in towns 3 (3) and 0 (5), cables 0-1 (2) and 1-2 (3): 13.",
        "Three generators (3) beat any cable (5).",
    ],
    prereqs=[
        ("mst", "Kruskal on the graph with an extra \"power station\" node."),
        ("union_find", "The disjoint sets behind Kruskal."),
    ],
)


def _pg_case(n, m, seed, ghi=10**5, whi=10**5):
    rng = _Lcg(seed)
    g = [rng.randint(1, ghi) for _ in range(n)]
    edges = _rand_graph(n, m, rng, wlo=1, whi=whi)
    return f"{n} {len(edges)}\n" + " ".join(map(str, g)) + "\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)


DEFS[-1]["cases"] += [
    ("hidden", "Random", _pg_case(80, 200, 271, ghi=500, whi=300)),
    ("hidden", "Large", _pg_case(10000, 60000, 273)),
]


def _forced_case(n, extra, seed, k, whi):
    edges = [e for e in _connected_wgraph(n, extra, seed, 1, whi) if e[0] != e[1]]
    return f"{n} {len(edges)} {k}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)


def _wq_case(n, m, q, seed):
    rng = _Lcg(seed)
    edges = _rand_graph(n, m, rng, wlo=1, whi=10**6)
    qs = [(rng.randint(0, n - 1), rng.randint(0, n - 1)) for _ in range(q)]
    return (f"{n} {len(edges)} {q}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)
            + "".join(f"{a} {b}\n" for a, b in qs))


_p(
    "mst-forced-edge","A Road Promised in Advance", "Medium",
    topics=["Graph", "Minimum Spanning Tree"], subtopics=["Minimum Spanning Tree", "Kruskal"],
    companies=["Amazon", "Google"],
    shape="wgraph_k", ret="long",
    todo="union the forced edge first and count its cost; then run Kruskal on the rest as usual",
    description=(
        "A council must connect `n` towns with roads, cheapest total first — but road number `k` "
        "(1-based, in input order) was promised to a mayor and **must** be built. Print the "
        "cheapest total cost of a road network that connects every town and includes road `k`. "
        "The towns can always be connected.\n\n"
        "### Input\nLine 1: `n m k`.\nNext `m` lines: `u v w`.\n\n### Output\nThe minimum total cost."
    ),
    constraints="2 ≤ n ≤ 10^4\n1 ≤ m ≤ 10^5\n1 ≤ k ≤ m\n1 ≤ w ≤ 10^6\nThe graph is connected, and road k joins two different towns.",
    hints=[
        "Kruskal decides edges in order, and every edge it accepts joins two groups. What if one edge were decided before all the others?",
        "Union the promised road's two towns first and add its cost. Then run Kruskal over all roads as normal — the promised one is now \"already connected\" and is skipped.",
        "Why this is optimal: the cut property still holds for the contracted graph, where the two towns are one.",
    ],
    opt=("O(m log m)", "O(n + m)",
         "One Kruskal run with one extra union at the start."),
    editorial=(
        "## The one thing this teaches\n**Forcing an edge = contracting it.** Building road k "
        "first merges its two towns into one. The cheapest way to finish is then the MST of the "
        "contracted graph — which is exactly what Kruskal computes if its union-find already has "
        "the two towns joined.\n\n"
        "## Approach\n```java\nunion(edges[k - 1][0], edges[k - 1][1]);\nlong total = edges[k - 1][2];\n"
        "for (int[] e : sortedByWeight)\n    if (union(e[0], e[1])) total += e[2];\nreturn total;\n```\n\n"
        "## The follow-up\nThe same trick answers \"is edge e in *some* MST?\": the forced MST "
        "weight equals the plain MST weight exactly when it is. That is how `mst-critical-edges` "
        "classifies edges."
    ),
    py='''
def solve(n, edges, k):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    u, v, w = edges[k - 1]
    parent[find(u)] = find(v)
    total = w
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static long solve(int n, int[][] edges, int k) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        int[] f = edges[k - 1];
        parent[find(f[0])] = find(f[1]);
        long total = f[2];
        int[][] es = edges.clone();
        Arrays.sort(es, (a, b) -> Integer.compare(a[2], b[2]));
        for (int[] e : es) {
            int ru = find(e[0]), rv = find(e[1]);
            if (ru != rv) { parent[ru] = rv; total += e[2]; }
        }
        return total;
    }
''',
    examples=[
        ("Example 1", "4 5 5\n0 1 1\n1 2 2\n2 3 3\n3 0 4\n0 2 10\n"),
        ("Example 2", "3 3 1\n0 1 2\n1 2 2\n0 2 2\n"),
    ],
    hidden=[
        ("Already in the MST", "4 5 1\n0 1 1\n1 2 2\n2 3 3\n3 0 4\n0 2 10\n"),
        ("Two towns, pick the dear road", "2 3 2\n0 1 1\n0 1 9\n1 0 4\n"),
        ("Forced road replaces a middle edge", "5 6 6\n0 1 1\n1 2 1\n2 3 1\n3 4 1\n0 4 100\n1 3 50\n"),
        ("Random", _forced_case(60, 150, 281, 77, 500)),
        ("Large", _forced_case(10000, 50000, 282, 12345, 10**6)),
    ],
    expl=[
        "The MST (1 + 2 + 3 = 6) does not use road 5. Forcing it (10) connects 0 and 2; then 0-1 (1) and 2-3 (3) finish: 14.",
        "Every road costs 2, so any two of them: 4.",
    ],
    prereqs=[
        ("mst", "Kruskal, and why contracting an edge keeps the greedy correct."),
        ("union_find", "Union the forced edge's ends before the loop starts."),
    ],
)


_p(
    "bottleneck-route", "The Lightest Heaviest Climb", "Medium",
    topics=["Graph", "Minimum Spanning Tree"], subtopics=["Minimum Spanning Tree", "Minimax Path", "BFS"],
    companies=["Google", "Uber"],
    shape="wgraph_q", ret="String",
    todo="build the MST with Kruskal; the answer for (a, b) is the largest edge on the MST path between them (BFS on the tree), or -1 if disconnected",
    description=(
        "Hikers move between `n` huts along `m` two-way trails; trail `u v w` climbs `w` metres. "
        "A hiker cares only about the **single steepest** trail on their route. For each of `q` "
        "trips `a b`, print the smallest possible steepest climb on any route from `a` to `b` "
        "(`0` if `a = b`), or `-1` if there is no route.\n\n"
        "### Input\nLine 1: `n m q`.\nNext `m` lines: `u v w`.\nNext `q` lines: `a b`.\n\n"
        "### Output\n`q` numbers on one line."
    ),
    constraints="1 ≤ n ≤ 2000\n0 ≤ m ≤ 10^4\n1 ≤ q ≤ 1000\n1 ≤ w ≤ 10^6",
    hints=[
        "Binary search on the climb limit with a BFS per step works, per query. There is a structure that answers every query at once.",
        "Kruskal adds trails from gentlest to steepest. The moment a and b first become connected, the trail just added is the answer — and that trail lies on the MST path between them.",
        "So build the MST, then for each query walk the tree path from a to b (BFS or DFS on the tree), tracking the largest weight seen.",
    ],
    opt=("O(m log m + q · n)", "O(n + m)",
         "One Kruskal, then one tree walk per query."),
    editorial=(
        "## The one thing this teaches\n**The MST is also the minimax-path tree.** For any two "
        "vertices, the MST path between them minimises the largest edge used. The proof is the "
        "cycle property: a path using a heavier edge could swap it for an MST edge that is lighter.\n\n"
        "## Approach\n```java\nList<int[]>[] tree = kruskal(n, edges);        // adjacency of the MST\n"
        "for each query (a, b):\n    BFS from a on tree, carrying best[v] = max edge on the path to v;\n"
        "    answer = seen[b] ? best[b] : -1;\n```\n\n"
        "## With 10⁵ queries\nPrecompute binary-lifting tables of \"max edge to the 2^j-th "
        "ancestor\" on the MST (stage 8's `tree-queries`), and each query is O(log n)."
    ),
    py='''
def solve(n, edges, queries):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = [[] for _ in range(n)]
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            tree[u].append((v, w))
            tree[v].append((u, w))
    out = []
    for a, b in queries:
        best = [-1] * n
        best[a] = 0
        q = deque([a])
        while q:
            x = q.popleft()
            for y, w in tree[x]:
                if best[y] < 0 and y != a:
                    best[y] = max(best[x], w)
                    q.append(y)
        out.append(best[b])
    return " ".join(map(str, out))
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static String solve(int n, int[][] edges, int[][] queries) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        int[][] es = edges.clone();
        Arrays.sort(es, (a, b) -> Integer.compare(a[2], b[2]));
        List<List<int[]>> tree = new ArrayList<>();
        for (int i = 0; i < n; i++) tree.add(new ArrayList<>());
        for (int[] e : es) {
            int ru = find(e[0]), rv = find(e[1]);
            if (ru != rv) {
                parent[ru] = rv;
                tree.get(e[0]).add(new int[]{e[1], e[2]});
                tree.get(e[1]).add(new int[]{e[0], e[2]});
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int[] qu : queries) {
            int a = qu[0], b = qu[1];
            int[] best = new int[n];
            Arrays.fill(best, -1);
            best[a] = 0;
            ArrayDeque<Integer> q = new ArrayDeque<>();
            q.add(a);
            while (!q.isEmpty()) {
                int x = q.poll();
                for (int[] yw : tree.get(x))
                    if (best[yw[0]] < 0 && yw[0] != a) { best[yw[0]] = Math.max(best[x], yw[1]); q.add(yw[0]); }
            }
            if (sb.length() > 0) sb.append(' ');
            sb.append(best[b]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5 6 3\n0 1 4\n1 2 9\n0 2 6\n2 3 2\n3 4 8\n1 4 3\n0 3\n4 2\n1 1\n"),
        ("Example 2", "4 1 2\n0 1 5\n0 1\n2 3\n"),
    ],
    hidden=[
        ("One hut", "1 0 1\n0 0\n"),
        ("Parallel trails", "2 3 2\n0 1 9\n0 1 2\n1 0 5\n0 1\n1 0\n"),
        ("Long gentle way round", "4 4 2\n0 3 50\n0 1 10\n1 2 10\n2 3 10\n0 3\n3 1\n"),
        ("Sparse random", _wq_case(120, 110, 150, 291)),
        ("Random", _wq_case(120, 400, 150, 292)),
        ("Large", _wq_case(2000, 10000, 1000, 294)),
    ],
    expl=[
        "0 → 2 → 3 climbs 6 then 2, beating 0 → 1 → 4 → 3 (steepest 8): 6. 4 → 1 → 0 → 2 has steepest 6. Hut 1 to itself: 0.",
        "Huts 2 and 3 are not reachable from 0 or each other by any trail.",
    ],
    prereqs=[
        ("mst", "The MST path between two vertices minimises the heaviest edge on it."),
        ("bfs", "Walk the tree from a, carrying the heaviest edge so far."),
    ],
)
