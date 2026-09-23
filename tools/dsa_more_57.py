# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 57 — Trees & Graphs, part 5: weighted shortest paths.
#
#   dijkstra-path-print     the distance is half the answer: rebuild the route from dist[]
#   nearest-hospital        multi-source Dijkstra: every source starts at distance 0
#   negative-cycle-detect   Bellman-Ford's n-th round, from a virtual source
#   widest-path             Dijkstra with (max, min) in place of (min, +)
#   second-shortest-path    two slots per vertex: the best and the strictly second best
#
# Defines the shape `wgraph_set`.
# ===========================================================================

# "n m k", then m lines "u v w", then k integers
_SHAPES["wgraph_set"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m, k = d[0], d[1], d[2]\n"
       "edges = [(d[3 + 3 * i], d[4 + 3 * i], d[5 + 3 * i]) for i in range(m)]\n"
       "srcs = d[3 + 3 * m:3 + 3 * m + k]\n",
    py_params="n, edges, srcs",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]), k = Number(d[2]);\n"
       "const edges = Array.from({ length: m }, (_, i) => [0, 1, 2].map(j => Number(d[3 + 3 * i + j])));\n"
       "const srcs = d.slice(3 + 3 * m, 3 + 3 * m + k).map(Number);\n",
    js_params="n, edges, srcs",
    java="        int n = sc.nextInt(), m = sc.nextInt(), k = sc.nextInt();\n        int[][] edges = new int[m][3];\n"
         "        for (int i = 0; i < m; i++) for (int j = 0; j < 3; j++) edges[i][j] = sc.nextInt();\n"
         "        int[] srcs = new int[k];\n        for (int i = 0; i < k; i++) srcs[i] = sc.nextInt();\n",
    java_params="int n, int[][] edges, int[] srcs", java_args="n, edges, srcs",
)


def _set_case(n, edges, srcs):
    return (f"{n} {len(edges)} {len(srcs)}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges)
            + " ".join(map(str, srcs)) + "\n")


def _rand_wcase(n, m, seed, wlo, whi, directed=False):
    edges = _rand_graph(n, m, _Lcg(seed), directed=directed, wlo=wlo, whi=whi)
    return _wcase(n, edges)


_p(
    "dijkstra-path-print", "Print the Fastest Route", "Medium",
    topics=["Graph", "Shortest Path"], subtopics=["Dijkstra", "Path Reconstruction"],
    companies=["Uber", "Google", "Amazon"],
    shape="wgraph", ret="String",
    todo="Dijkstra from the TARGET; then walk from 0, always stepping to the smallest-numbered neighbour v with w + dist[v] == dist[u]",
    description=(
        "A courier travels on `n` junctions (0 to `n − 1`) joined by `m` two-way roads; road "
        "`u v w` takes `w` minutes. Print the shortest travel time from junction `0` to junction "
        "`n − 1` on the first line, and the route on the second — the junctions in order. If "
        "several routes are equally fast, print the **lexicographically smallest** sequence of "
        "junctions. If `n − 1` cannot be reached, print just `-1`.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n### Output\nThe time, then the route; or `-1`."
    ),
    constraints="2 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\n1 ≤ w ≤ 10^4",
    hints=[
        "Dijkstra gives distances. A route is recoverable from distances alone: an edge u → v is on *some* shortest route exactly when dist-from-start[u] + w + dist-to-target[v] equals the best total.",
        "Run Dijkstra from the target, so dist[v] means \"time from v to the end\". Then from 0, a step to v is on a shortest route iff w + dist[v] == dist[u].",
        "Among the valid next steps, take the smallest junction number — and repeat until you reach n − 1. Because every w ≥ 1, dist strictly falls, so the walk ends.",
    ],
    opt=("O((n + m) log n)", "O(n + m)",
         "One Dijkstra, then one pass over the adjacency lists of the route's junctions."),
    editorial=(
        "## The one thing this teaches\n**A distance array is a map of every shortest path.** "
        "Storing one `parent[]` per vertex gives *a* route; it cannot choose among ties. The "
        "distances from the target describe all shortest routes at once — an edge is usable "
        "exactly when it is \"tight\" — so a greedy walk can pick the one the question wants.\n\n"
        "## Approach\n```java\nlong[] dist = dijkstra(adj, n - 1);          // time to the target\n"
        "if (dist[0] == INF) return \"-1\";\nint u = 0;\nroute.add(0);\nwhile (u != n - 1) {\n    int next = Integer.MAX_VALUE;\n"
        "    for (int[] e : adj[u]) if (e[1] + dist[e[0]] == dist[u]) next = Math.min(next, e[0]);\n"
        "    route.add(u = next);\n}\n```\n\n"
        "## Why from the target\nWalking forwards needs to know which neighbours still lead to "
        "the target optimally — that is a statement about distances *to* the target. From the "
        "start you would only know which neighbours were reached optimally, not which lead on."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float("inf")
    dist = [INF] * n
    dist[n - 1] = 0
    pq = [(0, n - 1)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    if dist[0] == INF:
        return "-1"
    route, u = [0], 0
    while u != n - 1:
        u = min(v for v, w in adj[u] if w + dist[v] == dist[u])
        route.append(u)
    return str(dist[0]) + "\\n" + " ".join(map(str, route))
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); adj.get(e[1]).add(new int[]{e[0], e[2]}); }
        long INF = Long.MAX_VALUE / 4;
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        dist[n - 1] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.add(new long[]{0, n - 1});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            if (top[0] > dist[u]) continue;
            for (int[] e : adj.get(u))
                if (top[0] + e[1] < dist[e[0]]) { dist[e[0]] = top[0] + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
        }
        if (dist[0] >= INF) return "-1";
        StringBuilder sb = new StringBuilder();
        sb.append(dist[0]).append('\\n').append(0);
        int u = 0;
        while (u != n - 1) {
            int next = Integer.MAX_VALUE;
            for (int[] e : adj.get(u)) if (e[1] + dist[e[0]] == dist[u]) next = Math.min(next, e[0]);
            u = next;
            sb.append(' ').append(u);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _wcase(5, [(0, 1, 2), (0, 2, 4), (1, 2, 1), (2, 4, 3), (1, 3, 5), (3, 4, 1)])),
        ("Example 2", _wcase(3, [(0, 1, 7)])),
    ],
    hidden=[
        ("Direct road", _wcase(2, [(0, 1, 9)])),
        ("Tie broken by the second junction", _wcase(4, [(0, 2, 1), (0, 1, 1), (1, 3, 1), (2, 3, 1)])),
        ("Tie deep in the route", _wcase(6, [(0, 1, 1), (1, 3, 2), (1, 2, 1), (2, 3, 1), (3, 5, 4), (3, 4, 2), (4, 5, 2)])),
        ("Parallel roads", _wcase(3, [(0, 1, 5), (0, 1, 2), (1, 2, 2), (0, 2, 9)])),
        ("Grid of equal roads", _wcase(16, [(r * 4 + c, r * 4 + c + 1, 1) for r in range(4) for c in range(3)]
                                        + [(r * 4 + c, (r + 1) * 4 + c, 1) for r in range(3) for c in range(4)])),
        ("Random", _rand_wcase(300, 1200, 301, 1, 20)),
        ("Large", _rand_wcase(50000, 150000, 302, 1, 10000)),
    ],
    expl=[
        "0 → 1 → 2 → 4 takes 2 + 1 + 3 = 6; 0 → 1 → 3 → 4 takes 2 + 5 + 1 = 8.",
        "Junction 2 has no roads.",
    ],
    prereqs=[
        ("dijkstra", "Dijkstra with a heap and lazy deletion, run from the target."),
        ("greedy", "Walk forward choosing the smallest tight neighbour."),
    ],
)


_p(
    "nearest-hospital", "How Far to the Nearest Hospital", "Medium",
    topics=["Graph", "Shortest Path"], subtopics=["Dijkstra", "Multi-Source"],
    companies=["Uber", "Amazon"],
    shape="wgraph_set", ret="String",
    todo="push every hospital into the heap at distance 0, then run Dijkstra once",
    description=(
        "A region has `n` towns joined by `m` two-way roads (`u v w`, `w` minutes). Some towns "
        "have a hospital. For every town, print the travel time to the **nearest** hospital, or "
        "`-1` if no hospital can be reached.\n\n"
        "### Input\nLine 1: `n m k`.\nNext `m` lines: `u v w`.\nLast line: the `k` hospital towns.\n\n"
        "### Output\n`n` numbers on one line."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\n1 ≤ k ≤ n\n1 ≤ w ≤ 10^4",
    hints=[
        "One Dijkstra per hospital, taking the minimum, is O(k · m log n).",
        "Imagine a new town connected to every hospital by a road of length 0. Its distances are exactly the answer.",
        "You do not need to build it: start the heap with every hospital at distance 0. Run Dijkstra once.",
    ],
    opt=("O((n + m) log n)", "O(n + m)",
         "A single Dijkstra, however many hospitals there are."),
    editorial=(
        "## The one thing this teaches\n**Multi-source is one run, not k runs.** The nearest "
        "source is the shortest path from a virtual super-source — and seeding the heap with every "
        "real source at 0 *is* that super-source, already expanded.\n\n"
        "## Approach\n```java\nArrays.fill(dist, INF);\nfor (int h : hospitals) { dist[h] = 0; pq.add(new long[]{0, h}); }\n"
        "// ...the ordinary Dijkstra loop...\n```\n\n"
        "## The unweighted version\nWith every road equal this is multi-source BFS (`rotting-oranges`, "
        "`as-far-from-land`) — same idea, a queue instead of a heap."
    ),
    py='''
def solve(n, edges, srcs):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float("inf")
    dist = [INF] * n
    pq = []
    for s in srcs:
        if dist[s] != 0:
            dist[s] = 0
            pq.append((0, s))
    heapq.heapify(pq)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return " ".join(str(x) if x != INF else "-1" for x in dist)
''',
    java='''
    static String solve(int n, int[][] edges, int[] srcs) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); adj.get(e[1]).add(new int[]{e[0], e[2]}); }
        long INF = Long.MAX_VALUE / 4;
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        for (int s : srcs) if (dist[s] != 0) { dist[s] = 0; pq.add(new long[]{0, s}); }
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            if (top[0] > dist[u]) continue;
            for (int[] e : adj.get(u))
                if (top[0] + e[1] < dist[e[0]]) { dist[e[0]] = top[0] + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(dist[i] >= INF ? -1 : dist[i]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6 6 2\n0 1 4\n1 2 3\n2 3 2\n3 4 6\n4 5 1\n0 5 20\n0 4\n"),
        ("Example 2", "4 1 1\n0 1 3\n3\n"),
    ],
    hidden=[
        ("Every town a hospital", "3 2 3\n0 1 5\n1 2 5\n2 0 1\n"),
        ("Repeated hospital", "3 2 2\n0 1 5\n1 2 5\n0 0\n"),
        ("Closer through a longer route", "4 4 1\n0 1 10\n0 2 1\n2 3 1\n3 1 1\n0\n"),
        ("Random", _set_case(200, _rand_graph(200, 600, _Lcg(311), wlo=1, whi=50), [3, 77, 120, 150, 199])),
        ("Sparse", _set_case(200, _rand_graph(200, 150, _Lcg(314), wlo=1, whi=50), [5, 6])),
        ("Large", _set_case(50000, _rand_graph(50000, 120000, _Lcg(312), wlo=1, whi=10000), _lcg_ints(313, 20, 0, 49999))),
    ],
    expl=[
        "Towns 0 and 4 are hospitals. Town 1 is 4 from 0; town 2 is 7 from 0 or 8 from 4 → 7; town 3 is 6 from 4; town 5 is 1 from 4.",
        "Only town 3 has a hospital, and no road reaches it.",
    ],
    prereqs=[
        ("dijkstra", "Dijkstra's heap can start with several vertices at distance 0."),
        ("bfs", "The same idea as multi-source BFS, with weights."),
    ],
)


_p(
    "negative-cycle-detect", "Arbitrage Hunt", "Medium",
    topics=["Graph", "Shortest Path"], subtopics=["Bellman-Ford", "Negative Cycle"],
    companies=["Goldman Sachs", "Jane Street", "Google"],
    shape="wgraph", ret="String",
    todo="Bellman-Ford with every dist starting at 0 (a virtual source to all); if round n still relaxes an edge, there is a negative cycle",
    description=(
        "A trader has `n` markets and `m` one-way trades; trade `u v w` moves value from market "
        "`u` to market `v` at a cost of `w` (a negative `w` is a gain). A loop of trades whose "
        "costs add up to **less than zero** is free money. Print `YES` if such a loop exists "
        "anywhere, otherwise `NO`.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w` (directed).\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 500\n0 ≤ m ≤ 5000\n-10^4 ≤ w ≤ 10^4",
    hints=[
        "Dijkstra cannot work: with negative costs, a vertex's distance can improve after it is finalised.",
        "Bellman-Ford: relax every edge n − 1 times. Without negative cycles, every shortest path has at most n − 1 edges, so after n − 1 rounds nothing can improve.",
        "So if round n still improves something, a negative cycle exists. To find cycles anywhere (not only those reachable from vertex 0), start every dist at 0 — as if a virtual source had a 0-cost edge to each market.",
    ],
    opt=("O(n · m)", "O(n)",
         "At most n rounds over all m edges; stop early when a round changes nothing."),
    editorial=(
        "## The one thing this teaches\n**Bellman-Ford's n-th round is a detector.** Its "
        "invariant — after round k, dist is at most the best walk of ≤ k edges — means n − 1 "
        "rounds suffice when shortest paths exist. An improvement in round n is a walk of n edges "
        "beating every shorter one, which must contain a negative cycle.\n\n"
        "## Approach\n```java\nlong[] dist = new long[n];                 // all 0: the virtual source\n"
        "for (int round = 1; round <= n; round++) {\n    boolean changed = false;\n"
        "    for (int[] e : edges)\n        if (dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }\n"
        "    if (!changed) return \"NO\";\n}\nreturn \"YES\";               // still changing in round n\n```\n\n"
        "## Why zeros find every cycle\nStarting at dist[s] = 0 and INF elsewhere only sees cycles "
        "reachable from s. The zeros put every vertex at distance 0 from an imaginary source, so "
        "every cycle is reachable."
    ),
    py='''
def solve(n, edges):
    dist = [0] * n
    for _ in range(n):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return "NO"
    return "YES"
''',
    java='''
    static String solve(int n, int[][] edges) {
        long[] dist = new long[n];
        for (int round = 1; round <= n; round++) {
            boolean changed = false;
            for (int[] e : edges)
                if (dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
            if (!changed) return "NO";
        }
        return "YES";
    }
''',
    examples=[
        ("Example 1", _wcase(4, [(0, 1, 3), (1, 2, -2), (2, 3, 2), (3, 1, -1)])),
        ("Example 2", _wcase(3, [(0, 1, -5), (1, 2, -5), (2, 0, 10)])),
    ],
    hidden=[
        ("One market", "1 0\n"),
        ("Negative self-loop", _wcase(2, [(0, 1, 1), (1, 1, -1)])),
        ("Negative edges, no cycle", _wcase(4, [(0, 1, -3), (1, 2, -3), (2, 3, -3), (0, 3, -1)])),
        ("Unreachable cycle", _wcase(5, [(0, 1, 2), (3, 4, -2), (4, 3, 1)])),
        ("Zero cycle", _wcase(3, [(0, 1, 4), (1, 2, -1), (2, 0, -3)])),
        ("Long cycle", _wcase(300, [(i, (i + 1) % 300, 1 if i else -300) for i in range(300)])),
        ("Long cycle, just positive", _wcase(300, [(i, (i + 1) % 300, 1 if i else -298) for i in range(300)])),
        ("Random, no cycle", _wcase(200, [(u, v, w) for u, v, w in _rand_graph(200, 2000, _Lcg(321), directed=True, wlo=-50, whi=100) if u < v])),
        ("Random dense", _rand_wcase(300, 4000, 322, -20, 100, directed=True)),
    ],
    expl=[
        "1 → 2 → 3 → 1 costs −2 + 2 − 1 = −1.",
        "The only loop, 0 → 1 → 2 → 0, costs −5 − 5 + 10 = 0 — not below zero.",
    ],
    prereqs=[
        ("bellman_ford", "Relax every edge n − 1 times; a change in round n means a negative cycle."),
        ("graph_cycle", "A negative cycle makes \"shortest\" undefined — walk it forever."),
    ],
)


_p(
    "widest-path", "The Widest Pipe Route", "Medium",
    topics=["Graph", "Shortest Path"], subtopics=["Dijkstra", "Bottleneck Path"],
    companies=["Google", "Amazon"],
    shape="wgraph", ret="long",
    todo="Dijkstra with a MAX-heap on width: width[v] = max(width[v], min(width[u], w)); start with width[0] = infinity",
    description=(
        "Water flows from station `0` to station `n − 1` through `m` two-way pipes; pipe `u v w` "
        "carries at most `w` litres per second. A route can carry only as much as its **narrowest** "
        "pipe. Print the largest amount one route can carry, or `-1` if the stations are not "
        "connected.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n### Output\nThe widest route's capacity, or `-1`."
    ),
    constraints="2 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\n1 ≤ w ≤ 10^9",
    hints=[
        "Dijkstra's argument needs only two things: extending a route never makes it better, and routes can be compared. Both hold for width, with min in place of + and max in place of min.",
        "width[v] = best narrowest-pipe value from 0 to v. Pop the *widest* unfinished station; relax with min(width[u], w).",
        "Alternatively, add pipes from widest to narrowest with union-find and stop when 0 and n − 1 connect — the maximum spanning tree.",
    ],
    opt=("O((n + m) log n)", "O(n + m)",
         "One run of the modified Dijkstra."),
    editorial=(
        "## The one thing this teaches\n**Dijkstra is a template over (combine, compare).** "
        "Shortest paths combine with + and prefer smaller; widest paths combine with min and prefer "
        "larger. Any pair where extending a path never improves it keeps the greedy correct.\n\n"
        "## Approach\n```java\nwidth[0] = Long.MAX_VALUE;\nmaxHeap.add(new long[]{width[0], 0});\n"
        "while (!maxHeap.isEmpty()) {\n    long[] top = maxHeap.poll();\n    int u = (int) top[1];\n    if (top[0] < width[u]) continue;       // stale\n"
        "    for (int[] e : adj[u]) {\n        long cand = Math.min(width[u], e[1]);\n"
        "        if (cand > width[e[0]]) { width[e[0]] = cand; maxHeap.add(new long[]{cand, e[0]}); }\n    }\n}\n```\n\n"
        "## Two views, one answer\nThe widest route is also the path between 0 and n − 1 in the "
        "*maximum* spanning tree — the mirror image of `bottleneck-route`."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    width = [0] * n
    width[0] = float("inf")
    pq = [(-width[0], 0)]
    while pq:
        negw, u = heapq.heappop(pq)
        if -negw < width[u]:
            continue
        for v, w in adj[u]:
            cand = min(width[u], w)
            if cand > width[v]:
                width[v] = cand
                heapq.heappush(pq, (-cand, v))
    return width[n - 1] if width[n - 1] > 0 else -1
''',
    java='''
    static long solve(int n, int[][] edges) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); adj.get(e[1]).add(new int[]{e[0], e[2]}); }
        long[] width = new long[n];
        width[0] = Long.MAX_VALUE;
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(b[0], a[0]));
        pq.add(new long[]{width[0], 0});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            if (top[0] < width[u]) continue;
            for (int[] e : adj.get(u)) {
                long cand = Math.min(width[u], e[1]);
                if (cand > width[e[0]]) { width[e[0]] = cand; pq.add(new long[]{cand, e[0]}); }
            }
        }
        return width[n - 1] > 0 ? width[n - 1] : -1;
    }
''',
    examples=[
        ("Example 1", _wcase(5, [(0, 1, 5), (1, 4, 3), (0, 2, 4), (2, 3, 6), (3, 4, 4), (1, 2, 8)])),
        ("Example 2", _wcase(3, [(0, 1, 9)])),
    ],
    hidden=[
        ("One pipe", _wcase(2, [(1, 0, 1000000000)])),
        ("Parallel pipes", _wcase(2, [(0, 1, 3), (0, 1, 7), (0, 1, 5)])),
        ("Long wide way beats short narrow", _wcase(4, [(0, 3, 1), (0, 1, 9), (1, 2, 9), (2, 3, 9)])),
        ("Random", _rand_wcase(300, 900, 331, 1, 100)),
        ("Large", _rand_wcase(50000, 150000, 332, 1, 10**9)),
    ],
    expl=[
        "0 → 1 → 2 → 3 → 4 uses pipes 5, 8, 6, 4: narrowest 4. The only other way into station 4 is the 3-litre pipe from station 1, so nothing beats 4.",
        "Station 2 has no pipes.",
    ],
    prereqs=[
        ("dijkstra", "The same greedy with min for combining and max for choosing."),
        ("heap", "A max-heap on width, with lazy deletion of stale entries."),
    ],
)


_p(
    "second-shortest-path", "The Runner-Up Route", "Hard",
    topics=["Graph", "Shortest Path"], subtopics=["Dijkstra", "k Shortest Paths"],
    companies=["Google", "Uber"],
    shape="wgraph", ret="long",
    todo="keep two slots per vertex, best and second (strictly larger); a popped distance d updates best or, if strictly between, second",
    description=(
        "A tour guide wants a route from junction `0` to junction `n − 1` that is **not** the "
        "fastest one: print the length of the second-shortest route — the smallest total strictly "
        "greater than the shortest. Routes may revisit junctions and roads (going back and forth "
        "along a road is allowed). Roads are two-way. Print `-1` if no such route exists.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n### Output\nThe second-shortest length, or `-1`."
    ),
    constraints="2 ≤ n ≤ 10^4\n0 ≤ m ≤ 5·10^4\n1 ≤ w ≤ 10^4",
    hints=[
        "Every vertex needs two numbers: its shortest distance and its strictly-second-shortest.",
        "Run Dijkstra where a vertex may be popped twice. A candidate d for v: if d < best[v], the old best becomes second and d is the new best; else if best[v] < d < second[v], d becomes second.",
        "Push every improvement. The answer is second[n − 1]. Because routes may bounce back and forth, a second route exists whenever n − 1 is reachable at all.",
    ],
    opt=("O((n + m) log n)", "O(n + m)",
         "Each vertex is settled at most twice, so each edge is relaxed at most twice."),
    editorial=(
        "## The one thing this teaches\n**Widen the state, keep the algorithm.** Dijkstra's "
        "state is \"the best distance to v\". Making it \"the best two distances to v\" keeps every "
        "argument intact: the second-best route to v extends either the best or the second-best "
        "route to some neighbour.\n\n"
        "## Approach\n```java\nwhile (!pq.isEmpty()) {\n    long[] top = pq.poll();\n    int u = (int) top[1];\n    long d = top[0];\n"
        "    if (d > second[u]) continue;             // stale\n    for (int[] e : adj[u]) {\n        long nd = d + e[1];\n"
        "        int v = e[0];\n        if (nd < best[v]) { second[v] = best[v]; best[v] = nd; pq.add(new long[]{nd, v}); }\n"
        "        else if (nd > best[v] && nd < second[v]) { second[v] = nd; pq.add(new long[]{nd, v}); }\n    }\n}\n```\n\n"
        "## \"Strictly\" is the whole problem\nA second route of the *same* length is not the runner-up. "
        "`nd > best[v]` — not `>=` — is what skips ties."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float("inf")
    best = [INF] * n
    second = [INF] * n
    best[0] = 0
    pq = [(0, 0)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > second[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < best[v]:
                second[v] = best[v]
                best[v] = nd
                heapq.heappush(pq, (nd, v))
            elif best[v] < nd < second[v]:
                second[v] = nd
                heapq.heappush(pq, (nd, v))
    return second[n - 1] if second[n - 1] != INF else -1
''',
    java='''
    static long solve(int n, int[][] edges) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); adj.get(e[1]).add(new int[]{e[0], e[2]}); }
        long INF = Long.MAX_VALUE / 4;
        long[] best = new long[n], second = new long[n];
        Arrays.fill(best, INF);
        Arrays.fill(second, INF);
        best[0] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.add(new long[]{0, 0});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            long d = top[0];
            if (d > second[u]) continue;
            for (int[] e : adj.get(u)) {
                long nd = d + e[1];
                int v = e[0];
                if (nd < best[v]) { second[v] = best[v]; best[v] = nd; pq.add(new long[]{nd, v}); }
                else if (nd > best[v] && nd < second[v]) { second[v] = nd; pq.add(new long[]{nd, v}); }
            }
        }
        return second[n - 1] >= INF ? -1 : second[n - 1];
    }
''',
    examples=[
        ("Example 1", _wcase(4, [(0, 1, 2), (1, 3, 3), (0, 2, 3), (2, 3, 3), (1, 2, 1)])),
        ("Example 2", _wcase(2, [(0, 1, 4)])),
    ],
    hidden=[
        ("Unreachable", _wcase(3, [(0, 1, 1)])),
        ("Two equal shortest routes", _wcase(4, [(0, 1, 1), (1, 3, 1), (0, 2, 1), (2, 3, 1)])),
        ("Bounce is the runner-up", _wcase(3, [(0, 1, 1), (1, 2, 1)])),
        ("Parallel roads", _wcase(2, [(0, 1, 5), (0, 1, 6), (0, 1, 5)])),
        ("Random", _rand_wcase(200, 600, 341, 1, 30)),
        ("Large", _rand_wcase(10000, 50000, 342, 1, 10000)),
    ],
    expl=[
        "The shortest is 0 → 1 → 3 = 5. Next: 0 → 2 → 3 = 6.",
        "The shortest is 4; going 0 → 1 → 0 → 1 costs 12, the next possible total.",
    ],
    prereqs=[
        ("dijkstra", "Dijkstra with two distance slots per vertex."),
        ("heap", "The heap may hold a vertex several times; skip entries worse than its second slot."),
    ],
)
