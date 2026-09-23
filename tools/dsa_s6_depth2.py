# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 (Trees & Graphs) — the depth layer, part 2: topological sort,
# union-find, minimum spanning trees and shortest paths; then the rebuilt
# ladders, the stage router and the step that attaches both parts.
#
# exec'd by tools/dsa_curriculum.py right after dsa_s6_depth.py.
# ---------------------------------------------------------------------------


# ============================================================ computed traces

def _t6_kahn_layers():
    n, edges = 6, [(0, 2), (1, 2), (2, 3), (1, 4), (4, 3), (3, 5)]
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    sem = [0] * n
    q = [v for v in range(n) if indeg[v] == 0]
    for v in q:
        sem[v] = 1
    rows, head = [], 0
    rows.append(["start", "—", _j(indeg), _j(q), "in-degree 0 → semester 1"])
    while head < len(q):
        u = q[head]
        head += 1
        freed = []
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                sem[v] = sem[u] + 1
                q.append(v)
                freed.append(f"{v} (sem {sem[v]})")
        rows.append([str(head), f"take {u} (sem {sem[u]})", _j(indeg), _j(q[head:]),
                     ", ".join(freed) if freed else "—"])
    return _trace(
        "Kahn's algorithm, reading semesters off the queue",
        "Rules 0→2, 1→2, 2→3, 1→4, 4→3, 3→5. `indeg` is listed for courses 0…5; a course "
        "enters the queue the moment its last prerequisite is taken.",
        ["#", "Take", "In-degrees after", "Queue after", "Newly free"],
        rows,
        f"Semesters {_j(sem)}. Course 3 waited for both 2 and 4; it became free when the later of "
        f"the two (in queue order) was taken — the one with the larger semester. That is why "
        f"`sem[u] + 1` at the moment of freeing is the maximum over all prerequisites.",
    )


def _t6_dag_count():
    n, edges = 6, [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (3, 4), (3, 5), (4, 5)]
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    ways = [0] * n
    ways[0] = 1
    q, head, rows = [v for v in range(n) if indeg[v] == 0], 0, []
    while head < len(q):
        u = q[head]
        head += 1
        adds = []
        for v in adj[u]:
            ways[v] += ways[u]
            adds.append(f"ways[{v}] += {ways[u] if u else 1}")
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
        rows.append([str(u), str(ways[u]), "; ".join(adds) if adds else "—", _j(ways)])
    return _trace(
        "Counting routes 0 → 5 in topological order",
        "Slopes 0→1, 0→2, 1→3, 2→3, 1→4, 3→4, 3→5, 4→5. When a station is taken from Kahn's "
        "queue its count is final, and it pushes that count along every outgoing slope.",
        ["Station", "Its final count", "Pushes", "ways[] after"],
        rows,
        f"{ways[5]} routes. A station is never pushed from before all its incoming slopes have "
        f"delivered — Kahn only releases it once its in-degree hits zero — so no count is used "
        f"before it is complete. The same loop with `max` instead of `+` is the critical path.",
    )


def _t6_offset_dsu():
    n = 4
    claims = [(0, 1, 5), (2, 3, -2), (1, 2, 4), (3, 0, -7), (0, 2, 8)]
    parent, off = list(range(n)), [0] * n

    def find(x):
        path = []
        while parent[x] != x:
            path.append(x)
            x = parent[x]
        root = x
        for y in reversed(path):
            if parent[y] != root:
                off[y] += off[parent[y]]
            parent[y] = root
        return root

    rows = []
    for i, (a, b, d) in enumerate(claims, 1):
        ra, rb = find(a), find(b)
        if ra == rb:
            verdict = "consistent" if off[b] - off[a] == d else f"**contradiction**: off[{b}] − off[{a}] = {off[b] - off[a]}"
            rows.append([str(i), f"h[{b}] − h[{a}] = {d}", f"same root {ra}", verdict, _j(parent), _j(off)])
            if "contra" in verdict:
                break
        else:
            parent[rb] = ra
            off[rb] = off[a] + d - off[b]
            rows.append([str(i), f"h[{b}] − h[{a}] = {d}", f"roots {ra}, {rb} differ",
                         f"link {rb} under {ra}, off[{rb}] = {off[a]} + {d} − {off[b]} = {off[rb]}",
                         _j(parent), _j(off)])
    return _trace(
        "Weighted union-find: height claims on four hilltops",
        "`off[x]` is h[x] − h[parent[x]]; after `find(x)`, parent[x] is the root and off[x] is "
        "x's height relative to it.",
        ["Claim", "Says", "Roots", "Action", "parent[]", "off[]"],
        rows,
        "Claim 4 is checked without any search: both ends already share a root, so their offsets "
        "to it give the implied difference in O(α(n)). A plain DSU would know they are related "
        "but not *how*.",
    )


def _t6_offline():
    n = 4
    edges = [(0, 1, 10), (1, 2, 5), (2, 3, 8), (0, 3, 3)]
    queries = [(0, 2, 4), (0, 2, 5), (3, 1, 4), (1, 1, 100)]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    es = sorted(edges, key=lambda e: -e[2])
    order = sorted(range(len(queries)), key=lambda i: -queries[i][2])
    e, rows, ans = 0, [], ["?"] * len(queries)
    for qi in order:
        a, b, x = queries[qi]
        added = []
        while e < len(es) and es[e][2] > x:
            u, v, w = es[e]
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
            added.append(f"{u}-{v} ({w})")
            e += 1
        ans[qi] = "1" if find(a) == find(b) else "0"
        rows.append([f"#{qi + 1}: {a}→{b}, {x} t", ", ".join(added) if added else "—",
                     "yes" if ans[qi] == "1" else "no"])
    return _trace(
        "Offline queries: trucks heaviest first, bridges widest first",
        "Bridges 0-1 (10), 1-2 (5), 2-3 (8), 0-3 (3). A truck of x tonnes may use bridges with "
        "capacity > x; heavier trucks come first, so the usable set only grows.",
        ["Truck (original #)", "Bridges added before it", "Can it go?"],
        rows,
        f"Answers in the original order: {''.join(ans)}. Each bridge is unioned once in total "
        f"and each truck costs two finds — the sort is what made union-find (which cannot delete) "
        f"fit a question about removing light bridges.",
    )


def _t6_virtual_node():
    g = [5, 8, 9, 3]
    cables = [(0, 1, 2), (1, 2, 3), (2, 3, 6), (0, 3, 7)]
    n = len(g)
    allE = cables + [(n, i, g[i]) for i in range(n)]
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    rows, total = [], 0
    for u, v, w in sorted(allE, key=lambda e: e[2]):
        name = f"generator in {v}" if u == n else f"cable {u}-{v}"
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            rows.append([name, str(w), "take", str(total)])
        else:
            rows.append([name, str(w), "skip — already powered together", str(total)])
    return _trace(
        "Kruskal with a virtual power station (node 4)",
        "Generator costs 5, 8, 9, 3; cables 0-1 (2), 1-2 (3), 2-3 (6), 0-3 (7). Each generator "
        "becomes an edge from node 4 to its town.",
        ["Edge", "Cost", "Decision", "Total"],
        rows,
        f"Total {total}: generators in towns 3 and 0, cables 0-1 and 1-2. The algorithm never "
        f"decided *how many* generators to build — that fell out of the MST on 5 nodes.",
    )


def _t6_bellman():
    n = 4
    edges = [(0, 1, 3), (1, 2, -2), (2, 3, 2), (3, 1, -1)]
    dist = [0] * n
    rows = []
    for rnd in range(1, n + 1):
        changes = []
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changes.append(f"{v}←{dist[v]}")
        rows.append([str(rnd), ", ".join(changes) if changes else "none", _j(dist)])
        if not changes:
            break
    last = rows[-1][1] != "none" and len(rows) == n
    return _trace(
        "Bellman-Ford from a virtual source (every dist starts at 0)",
        "Edges 0→1 (3), 1→2 (−2), 2→3 (2), 3→1 (−1), relaxed in that order each round. With "
        "4 vertices, 3 rounds must suffice if no negative cycle exists.",
        ["Round", "Improved", "dist after"],
        rows,
        ("Round 4 still improves something, so a negative cycle exists: 1 → 2 → 3 → 1 costs "
         "−2 + 2 − 1 = −1, and every lap lowers the distances again. Without the cycle the "
         "rounds would go quiet by round 3.") if last else "The rounds went quiet: no negative cycle.",
    )


def _t6_second_best():
    n = 4
    edges = [(0, 1, 2), (1, 3, 3), (0, 2, 3), (2, 3, 3), (1, 2, 1)]
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    INF = float("inf")
    best, second = [INF] * n, [INF] * n
    best[0] = 0
    pq, rows = [(0, 0)], []

    def fmt(x):
        return "∞" if x == INF else str(x)

    while pq:
        d, u = _hq.heappop(pq)
        if d > second[u]:
            continue
        ups = []
        for v, w in adj[u]:
            nd = d + w
            if nd < best[v]:
                second[v], best[v] = best[v], nd
                _hq.heappush(pq, (nd, v))
                ups.append(f"best[{v}]={nd}")
            elif best[v] < nd < second[v]:
                second[v] = nd
                _hq.heappush(pq, (nd, v))
                ups.append(f"second[{v}]={nd}")
        rows.append([f"({d}, {u})", ", ".join(ups) if ups else "—",
                     " ".join(f"{fmt(b)}/{fmt(s)}" for b, s in zip(best, second))])
        if len(rows) >= 14:
            break
    return _trace(
        "Two slots per vertex: best / second-best distances",
        "Roads 0-1 (2), 1-3 (3), 0-2 (3), 2-3 (3), 1-2 (1). Each popped (distance, vertex) may "
        "improve a neighbour's best — pushing the old best down to second — or fill a strictly "
        "larger second.",
        ["Popped", "Updates", "best/second for 0 1 2 3"],
        rows,
        f"Vertex 3 ends with best {fmt(best[3])} and second {fmt(second[3])}. Note the pops of "
        f"vertices already settled once: a vertex is expanded at most twice, once per slot, so "
        f"the run is still O((n + m) log n).",
    )


# ================================================================ Big-O drills

_BIGO_S6B = {
    "topological-sort": [
        _bigo("""
for (int u : topoOrder)                 // V vertices
    for (int v : adj[u])                // E edges in total
        ways[v] = (ways[v] + ways[u]) % MOD;
""", "O(V + E)", ["O(V + E)", "O(V · E)", "O(2^V)", "O(V²)"],
              """
Each edge is relaxed exactly once, when its source is taken. Counting paths by enumerating
them would be exponential — a DAG can have 2^(V/2) paths — but the DP never lists one.
"""),
        _bigo("""
boolean unique = true;
while (!q.isEmpty()) {
    if (q.size() > 1) unique = false;
    int u = q.poll();
    for (int v : adj[u]) if (--indeg[v] == 0) q.add(v);
}
""", "O(V + E)", ["O(V + E)", "O(V!)", "O(V² + E)", "O(V · E)"],
              """
Plain Kahn plus one comparison per step. Deciding uniqueness by listing all topological
orders would be factorial; the queue's width answers it for free.
"""),
        _bigo("""
for (int round = 0; round < V; round++)        // repeat until nothing changes
    for (int[] e : edges)
        fin[e[1]] = Math.max(fin[e[1]], fin[e[0]] + dur[e[1]]);
""", "O(V · E)", ["O(V · E)", "O(V + E)", "O(E log V)", "O(V²)"],
              """
Relaxing every edge V times is Bellman-Ford's shape — correct on a DAG, but it ignores the
order. Relaxing in topological order finishes in one pass: O(V + E).
"""),
    ],
    "union-find": [
        _bigo("""
for (int[] cell : added) {                      // k cells
    count++;
    for (int[] d : DIRS)
        if (inside && land[nb] && union(id, nb)) count--;
}
""", "O(k · α(r·c))", ["O(k · α(r·c))", "O(k · r · c)", "O(k log k)", "O((r · c)²)"],
              """
Four union attempts per added cell, each nearly constant with both optimisations. A flood fill
after every addition would be O(k · r · c).
"""),
        _bigo("""
Arrays.sort(edges, byWeightDesc);               // m edges
Arrays.sort(order, byQueryWeightDesc);          // q queries
for (int qi : order) {
    while (e < m && edges[e][2] > queries[qi][2]) union(edges[e][0], edges[e++][1]);
    ans[qi] = find(a) == find(b);
}
""", "O(m log m + q log q)", ["O(m log m + q log q)", "O(q · (n + m))", "O(q · m)", "O(n²)"],
              """
The two sorts dominate. The `while` loop is a pointer that only moves forward, so across all
queries it performs m unions in total — not m per query.
"""),
        _bigo("""
int find(int x) {                    // weighted DSU, path compression, no union by size
    if (parent[x] == x) return x;
    int r = find(parent[x]);
    off[x] += off[parent[x]];
    return parent[x] = r;
}
""", "O(log n) amortised per operation", ["O(log n) amortised per operation", "O(1) worst case", "O(n) amortised", "O(α(n)) without union by size"],
              """
Path compression alone gives O(log n) amortised; adding union by size (or rank) brings it to
O(α(n)). The offsets ride along at no extra asymptotic cost — but the recursion can be n deep
before the first compression, so write it iteratively for large n.
"""),
    ],
    "mst": [
        _bigo("""
List<int[]> all = new ArrayList<>(Arrays.asList(edges));   // m cables
for (int i = 0; i < n; i++) all.add(new int[]{n, i, g[i]}); // n generators
kruskal(n + 1, all);
""", "O((n + m) log(n + m))", ["O((n + m) log(n + m))", "O(2ⁿ · m log m)", "O(n · m)", "O(m log m)"],
              """
The virtual node adds n edges, so Kruskal sorts n + m. Trying every subset of generator towns
and running an MST for each would be exponential.
"""),
        _bigo("""
for (int[] q : queries)                 // q queries
    bfsOnTree(mst, q[0]);               // n vertices, n - 1 edges
""", "O(m log m + q · n)", ["O(m log m + q · n)", "O(q · m log m)", "O(q · n²)", "O(n + m + q)"],
              """
One Kruskal (m log m) builds the MST once; then each query walks the tree in O(n). Running a
fresh binary-search-plus-BFS per query would cost O(q · (n + m) log W).
"""),
        _bigo("""
long best = Long.MAX_VALUE;
for (int skip = 0; skip < m; skip++)          // try removing each MST edge
    best = Math.min(best, kruskalWithout(skip));
""", "O(m · m α(n)) after one sort", ["O(m · m α(n)) after one sort", "O(m log m)", "O(2^m)", "O(n · m)"],
              """
Sort once; then each of the m reruns is a linear pass of unions. This brute force is how
\"second-best MST\" and \"critical edges\" are usually solved at m ≤ 10³.
"""),
    ],
    "shortest-paths": [
        _bigo("""
for (int s : hospitals)                 // k sources
    dijkstra(s);                        // O((n + m) log n) each
""", "O(k · (n + m) log n)", ["O(k · (n + m) log n)", "O((n + m) log n)", "O(k · n)", "O(n³)"],
              """
k separate runs. Seeding one heap with all k sources at distance 0 gives every vertex its
nearest-source distance in a single O((n + m) log n) run.
"""),
        _bigo("""
// best and second slots; a vertex is expanded when popped at <= second[u]
while (!pq.isEmpty()) {
    long[] t = pq.poll();
    if (t[0] > second[(int) t[1]]) continue;
    for (int[] e : adj[(int) t[1]]) relaxTwoSlots(t[0], e);
}
""", "O((n + m) log n)", ["O((n + m) log n)", "O(n · m)", "O(2ⁿ)", "O(m²)"],
              """
Each vertex is expanded at most twice (once per slot), so each edge is relaxed at most twice
and the heap sees O(m) pushes.
"""),
        _bigo("""
for (int round = 1; round <= n; round++) {
    boolean changed = false;
    for (int[] e : edges) if (dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
    if (!changed) break;
}
""", "O(n · m)", ["O(n · m)", "O(m log n)", "O(n + m)", "O(n²)"],
              """
Up to n rounds over all m edges. The early exit helps in practice, but a negative cycle keeps
every round busy — which is exactly what the n-th round detects.
"""),
    ],
}


# ================================================================ the depth

_D6_TOPO = dict(
    invariant=_inv(
        "Kahn: **every vertex in the queue has all of its predecessors already output**, and "
        "`indeg[v]` counts v's predecessors not yet output.",
        "The queue starts with the vertices whose in-degree is 0 — they have no predecessors "
        "at all — and `indeg` is the true in-degree before anything is output.",
        "Outputting u removes it as a predecessor of each v in adj[u], so decrementing "
        "`indeg[v]` keeps the count right. A vertex joins the queue exactly when that count "
        "reaches 0 — when its last predecessor has been output.",
        "If all V vertices come out, the output lists every vertex after all of its "
        "predecessors: a topological order. If fewer come out, the rest all have a predecessor "
        "that never came out — they lie on or behind a cycle.",
        "The same invariant makes DAG DP safe: a vertex leaves the queue only after every "
        "vertex that feeds it has, so its DP value is final when it is used.",
    ),
    variants=[
        _var("Kahn (BFS)", "Queue of in-degree-0 vertices.", "An order, or cycle detection by count.",
             "O(V + E)", "Count the output."),
        _var("DFS post-order", "Push a vertex after all its descendants; reverse.",
             "An order; also finish times.", "O(V + E)", "Needs cycle checking separately."),
        _var("Three-colour cycle check", "Grey = on the stack; grey neighbour = cycle.",
             "Is there a cycle? Which vertices are safe?", "O(V + E)", "Directed graphs only."),
        _var("Smallest first", "A min-heap in place of the queue.",
             "Lexicographically smallest order.", "O(V log V + E)", "The heap changes which order, not whether."),
        _var("Uniqueness", "Watch the queue's size.", "Is exactly one order possible?",
             "O(V + E)", "Check for a cycle too."),
        _var("Layers", "Drain the queue a level at a time.", "Semesters, rounds, parallel steps.",
             "O(V + E)", "sem[v] = sem[u] + 1 when v is freed."),
        _var("Longest path / critical path", "DP in topological order with max.",
             "Project duration, longest chain.", "O(V + E)", "Weights on vertices or on edges."),
        _var("Path counting", "DP in topological order with +.", "Number of routes s → t.",
             "O(V + E)", "Reduce modulo as you add."),
        _var("Build the graph first", "Infer edges from data (adjacent words, rules).",
             "Alien alphabet, ordering constraints.", "O(total input + V + E)", "Invalid input can imply a cycle."),
        _var("Reverse the edges", "Topo-sort the reversed graph.", "Safe states, \"everything that depends on x\".",
             "O(V + E)", "Out-degree plays the in-degree's role."),
    ],
    rewrites=[
        _rw("Find the next free vertex with a queue, not a scan",
            """
for (int step = 0; step < V; step++) {
    int u = -1;
    for (int v = 0; v < V; v++)                // O(V) scan per step
        if (!done[v] && indeg[v] == 0) { u = v; break; }
    if (u < 0) return CYCLE;
    done[u] = true;
    for (int v : adj[u]) indeg[v]--;
}
""",
            """
for (int v = 0; v < V; v++) if (indeg[v] == 0) q.add(v);
while (!q.isEmpty()) {
    int u = q.poll();
    out.add(u);
    for (int v : adj[u]) if (--indeg[v] == 0) q.add(v);
}
if (out.size() < V) return CYCLE;
""",
            "Enqueue a vertex the moment its in-degree hits zero.",
            """
A vertex can only become free when one of its predecessors is output, and that is exactly the
moment we decrement it — so checking there catches every newly free vertex. The O(V²) scan
becomes O(V + E).
"""),
        _rw("Count paths by DP, not by recursion",
            """
long count(int u) {                        // exponential: re-walks shared suffixes
    if (u == target) return 1;
    long total = 0;
    for (int v : adj[u]) total += count(v);
    return total;
}
""",
            """
long[] ways = new long[V];
ways[source] = 1;
for (int u : topoOrder)
    for (int v : adj[u])
        ways[v] = (ways[v] + ways[u]) % MOD;
""",
            "Push counts forward in topological order.",
            """
The recursion recomputes count(v) once per path that reaches v — exponentially often. In
topological order each vertex's count is complete before it is used (the invariant), so each
edge adds once.
"""),
        _rw("Critical path: one pass in order, not V rounds",
            """
for (int round = 0; round < V; round++)
    for (int[] e : edges)
        start[e[1]] = Math.max(start[e[1]], start[e[0]] + dur[e[0]]);
""",
            """
for (int u : topoOrder)
    for (int v : adj[u])
        start[v] = Math.max(start[v], start[u] + dur[u]);
""",
            "Relax edges in topological order, once.",
            """
The repeated rounds wait for values to propagate along chains. In topological order every
start[u] is final before its edges are relaxed, so one pass has the same effect — O(V + E)
instead of O(V · E).
"""),
    ],
    internals="""
### Why the reversed DFS finish order is topological

In a DAG, when DFS finishes u (turns it black), every vertex reachable from u is already
black: either DFS visited it from u, or it was finished before u was entered. So **u finishes
after all of its descendants**. Listing vertices by *decreasing* finish time puts every
vertex before its descendants — a topological order. On a graph with a cycle, some edge
would point to a grey vertex; that is the three-colour check, and the reason the order is
only meaningful once the check has passed.

### The in-degree array is the whole state

Kahn's algorithm needs nothing but `indeg[]` and a queue: no colours, no recursion, no
visited set. That makes it the version to reach for when the graph is large (no stack depth)
or when you need *which* vertices are free at each step (layers, uniqueness, smallest-first).

### One topological order or many

A DAG usually has many valid orders. The number of them can be astronomical (V! for an empty
graph), so never enumerate them. Questions about the set of orders have structural answers:
the order is unique iff every consecutive pair is joined by an edge, and the smallest order
lexicographically comes from a min-heap.

### DAG DP is shortest / longest paths with the order given for free

Shortest paths on a general graph need Dijkstra or Bellman-Ford because the order in which
vertices become final is unknown. On a DAG the topological order *is* that order, so one
relaxation pass works — even with negative weights, and even for the **longest** path, which
is NP-hard on general graphs.
""",
    build_it="""
### Kahn, DFS order and a checker

**1. `kahn(V, edges)`** → an order, or null on a cycle.

**2. `dfsOrder(V, edges)`** → reversed post-order, iterative (an explicit stack of
(vertex, next-neighbour-index) pairs), plus cycle detection by colours.

**3. `isTopological(order, edges)`** → checks every edge u → v has pos[u] < pos[v] and that
the order is a permutation.

**4. Properties on 1,000 random graphs** (half DAGs built from a hidden order, half with a
planted cycle): `kahn` and `dfsOrder` agree on *whether* an order exists; both outputs pass
the checker; `kahn` with a min-heap returns the lexicographically smallest order (check
against `itertools`-style brute force for V ≤ 7).

**5. Layers and critical path**: `semesters()` and `criticalPath(dur)` — property: with all
durations 1, the critical path equals the number of semesters.
""",
    skeletons=[
        _sk("Kahn in layers",
            "Semesters, rounds, \"minimum number of steps\".",
            """
for (int v = 0; v < n; v++) if (indeg[v] == 0) { sem[v] = 1; q.add(v); }
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj[u])
        if (--indeg[v] == 0) { sem[v] = sem[u] + 1; q.add(v); }
}
""",
            "The freeing predecessor is the last one — and has the largest semester."),
        _sk("DP in topological order",
            "Path counts, longest path, critical path.",
            """
ways[src] = 1;                               // or start[] = 0 for scheduling
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj[u]) {
        ways[v] = (ways[v] + ways[u]) % MOD; // or start[v] = max(start[v], start[u] + dur[u])
        if (--indeg[v] == 0) q.add(v);
    }
}
""",
            "Kahn's loop is the DP loop."),
        _sk("Is the order unique?",
            "Exactly one valid order.",
            """
boolean unique = true;
while (!q.isEmpty()) {
    if (q.size() > 1) unique = false;
    int u = q.poll();
    order.add(u);
    for (int v : adj[u]) if (--indeg[v] == 0) q.add(v);
}
if (order.size() < n) return "CYCLE";
""",
            "Width two at any step means two orders exist."),
    ],
    signals=[
        _sig("“how many semesters / rounds at minimum”", "Kahn in layers",
             "The layer number is the longest prerequisite chain."),
        _sig("“how many ways to get from s to t” in a DAG", "Path-count DP in topological order",
             "Counts add along edges."),
        _sig("“shortest total time with unlimited workers”", "Critical path: longest path DP",
             "Each task starts when its last prerequisite ends."),
        _sig("“is there exactly one valid order?”", "Watch Kahn's queue width",
             "Never enumerate orders."),
    ],
    costs=[
        _cost("Kahn with layers", "O(V + E)", "O(V + E)", ""),
        _cost("DAG DP (count / longest)", "O(V + E)", "O(V)", "One pass in topological order."),
        _cost("Smallest-first order", "O(V log V + E)", "O(V)", "Min-heap instead of a queue."),
    ],
    pitfalls=[
        _pit("A path count is used before it is complete",
             "The DP ran in index order or DFS pre-order instead of topological order.",
             "Only push a vertex's count once Kahn releases it (in-degree 0)."),
        _pit("\"Unique\" is printed for a cyclic graph",
             "The queue never widened, but it also emptied early.",
             "Check `order.size() < n` first."),
        _pit("Critical path counts the first task twice",
             "start[] and finish[] were mixed up.",
             "Carry start times; finish = start + duration, and the answer is the max finish."),
    ],
    checks=[
        _chk("Why does `sem[v] = sem[u] + 1`, set when v is freed, give the maximum over v's prerequisites?",
             "v is freed by its last prerequisite to be output, and Kahn outputs vertices in "
             "non-decreasing semester order — so that last one has the largest semester."),
        _chk("How can you tell from Kahn's run that the topological order is unique?",
             "The queue never held more than one vertex (and all V were output)."),
        _chk("Why is the longest path easy on a DAG but hard in general?",
             "A topological order finalises every vertex before it is used, so one DP pass "
             "works; with cycles there is no such order and paths can loop."),
    ],
    traces=[_t6_kahn_layers(), _t6_dag_count()],
)


_D6_UF = dict(
    invariant=_inv(
        "`find(x) == find(y)` **exactly when x and y were joined by some sequence of `union` "
        "calls** — each set's tree contains precisely the elements of one group.",
        "Initially `parent[x] = x`: every element is the root of its own one-element tree, and "
        "no unions have happened.",
        "`union(a, b)` makes one root the child of the other, so the two trees become one and "
        "their groups merge — exactly what the union asked. Path compression re-points nodes "
        "at their root, and union by size chooses which root goes under; both change tree "
        "*shapes* only, never which root an element reaches.",
        "At any time, comparing two roots answers \"same group?\". A weighted DSU extends the "
        "sentence: `off[x]` (relative to the root, after `find`) is x's value minus the root's.",
        "The invariant is why DSU cannot delete: splitting a group would need to know which "
        "union created each link, and compression has erased that. Offline tricks reorder the "
        "questions so deletions are never needed.",
    ),
    variants=[
        _var("Plain components", "union per edge; count successful unions.",
             "Components, provinces, connectivity.", "O(m α(n))", "Components = n − successful unions."),
        _var("With sizes", "size[root] maintained on union.", "Largest group, pairs across groups.",
             "O(m α(n))", "Read size at the root only."),
        _var("Cycle detection", "`union` returns false → the edge closes a cycle.",
             "Redundant connection, valid tree.", "O(m α(n))", "Undirected graphs only."),
        _var("Grid cells", "Element i · c + j.", "Islands, regions, percolation.",
             "O(r · c α)", "Only union with land neighbours."),
        _var("Online additions", "+1 per new element, −1 per successful union.",
             "Island count after each addition.", "O(k α)", "Skip an element added twice."),
        _var("Equations / relations", "Union equalities, then check inequalities.",
             "Satisfiability of == / != constraints.", "O(m α)", "Two passes: all == first."),
        _var("Weighted (offsets)", "off[x] = value(x) − value(parent[x]).",
             "Height differences, ratios (with ×), currency.", "O(m α)", "Fix offsets during compression."),
        _var("Parity", "An offset modulo 2.", "Online bipartiteness, odd cycles.",
             "O(m α)", "Link with par[u] ^ par[v] ^ 1."),
        _var("Offline by threshold", "Sort queries and edges together; add edges as the threshold passes.",
             "Reachability under a weight limit.", "O((m + q) log)", "Keep each query's original index."),
        _var("Kruskal", "Sorted edges; take the ones that union.", "MST, bottleneck paths.",
             "O(m log m)", "Stop at n − 1 edges."),
    ],
    rewrites=[
        _rw("Repeated connectivity questions: DSU, not a BFS each",
            """
for (int[] q : queries)                          // q BFS runs
    ans.add(bfsReaches(adj, q[0], q[1]));
""",
            """
for (int[] e : edges) union(e[0], e[1]);          // once
for (int[] q : queries)
    ans.add(find(q[0]) == find(q[1]));            // ~O(1) each
""",
            "Build the partition once, then answer by comparing roots.",
            """
Connectivity is an equivalence relation, and DSU stores exactly its classes. Once every edge is
unioned, two vertices are connected iff they share a root — O(q · (V + E)) becomes
O((E + q) α(V)).
"""),
        _rw("Island counts after each addition: update, do not recount",
            """
for (int[] cell : cells) {
    grid[cell[0]][cell[1]] = 1;
    ans.add(countIslandsByFloodFill(grid));      // O(r · c) each time
}
""",
            """
for (int[] cell : cells) {
    if (land[id]) { ans.add(count); continue; }
    land[id] = true; count++;
    for (neighbour nb that is land) if (union(id, nb)) count--;
    ans.add(count);
}
""",
            "Maintain the count incrementally: +1 new, −1 per merge.",
            """
Adding one cell changes the islands only near that cell: it is a new island, and it merges
with each distinct neighbouring island. `union` returning true means \"two different islands
just became one\", so the counter is exact.
"""),
        _rw("Threshold queries: sort once, not a fresh DSU each",
            """
for (int[] q : queries) {                         // O(q · m)
    DSU d = new DSU(n);
    for (int[] e : edges) if (e[2] > q[2]) d.union(e[0], e[1]);
    ans[i] = d.find(q[0]) == d.find(q[1]);
}
""",
            """
Arrays.sort(edges, (p, r) -> Integer.compare(r[2], p[2]));           // heaviest first
Integer[] order = new Integer[q];
for (int i = 0; i < q; i++) order[i] = i;
Arrays.sort(order, (p, r) -> Integer.compare(queries[r][2], queries[p][2]));
int e = 0;
for (int qi : order) {
    while (e < m && edges[e][2] > queries[qi][2]) union(edges[e][0], edges[e++][1]);
    ans[qi] = find(queries[qi][0]) == find(queries[qi][1]);
}
""",
            "Answer the queries in the order that only ever adds edges.",
            """
The edge set usable by a lighter truck is a superset of a heavier truck's. Processing the
heaviest first, each later query only needs edges added on top — so one DSU grows through all
the queries, and the answers are stored at their original indices.
"""),
    ],
    internals="""
### α(n) in one paragraph

With union by size and path compression, m operations on n elements cost O(m · α(n)), where
α is the inverse Ackermann function. α grows so slowly that α(n) ≤ 4 for every n that fits in
the universe, so in practice each operation is constant. Either optimisation alone is not
enough for that bound: union by size alone gives O(log n) (a tree of height h has at least
2^h nodes), path compression alone gives O(log n) amortised.

### Why rollback forbids compression

Some offline algorithms need to *undo* unions (divide and conquer over time). Undo is easy if
each union changed one `parent` entry — record it and restore it. Path compression changes
many entries during `find`, which is why a **rollback DSU** uses union by size only and
accepts O(log n) finds.

### The weighted find, carefully

In a weighted DSU, `off[x]` is relative to `parent[x]`. When compression re-points x at the
root, `off[x]` must become relative to the root: add the parent's offset *after* the parent
itself has been compressed. Processing the path from the node nearest the root outwards does
exactly that — and doing it the other way round is the classic bug.

### Memory layout

Two `int[]`s — `parent` and `size` (plus `off` for the weighted form) — and nothing else. No
objects, no adjacency lists: DSU is often the fastest graph structure in Java simply because
it is two arrays.
""",
    skeletons=[
        _sk("Weighted union-find",
            "Known differences between elements: heights, potentials, ratios.",
            """
int find(int x) {                               // iterative, fixes offsets top-down
    int root = x;
    while (parent[root] != root) root = parent[root];
    Deque<Integer> path = new ArrayDeque<>();
    for (int y = x; parent[y] != y; y = parent[y]) path.push(y);
    while (!path.isEmpty()) {
        int y = path.pop();
        if (parent[y] != root) off[y] += off[parent[y]];
        parent[y] = root;
    }
    return root;
}
// claim value(b) - value(a) = d
int ra = find(a), rb = find(b);
if (ra == rb) consistent = off[b] - off[a] == d;
else { parent[rb] = ra; off[rb] = off[a] + d - off[b]; }
""",
            "Parity DSU is the same with XOR and d = 1."),
        _sk("Offline queries by threshold",
            "Reachability, components under a weight limit.",
            """
Arrays.sort(edges, (p, r) -> Integer.compare(r[2], p[2]));   // heaviest first
Integer[] order = new Integer[q];
for (int i = 0; i < q; i++) order[i] = i;
Arrays.sort(order, (p, r) -> Integer.compare(lim[r], lim[p]));   // heaviest limit first
int e = 0;
for (int qi : order) {
    while (e < m && edges[e][2] > lim[qi]) { union(edges[e][0], edges[e][1]); e++; }
    ans[qi] = find(a[qi]) == find(b[qi]);
}
""",
            "Strict or non-strict comparison — read the statement."),
        _sk("Online island count",
            "Components while elements are added.",
            """
if (!land[id]) {
    land[id] = true;
    count++;
    for (int[] d : DIRS) {
        int nb = (i + d[0]) * c + (j + d[1]);
        if (inside && land[nb] && union(id, nb)) count--;
    }
}
""",
            "An element added twice must not add another island."),
    ],
    signals=[
        _sig("“after each addition, how many groups?”", "Online DSU with a counter",
             "+1 per new element, −1 per merge."),
        _sig("“a is x more than b” / “ratio” claims, find the contradiction", "Weighted DSU",
             "Offsets along the tree give any known difference."),
        _sig("“two teams”, “rivals” arriving one by one", "Parity DSU",
             "An edge within one set with equal parity is an odd cycle."),
        _sig("“using only edges with weight < limit”, many queries", "Offline: sort both, one DSU",
             "DSU can add but not remove."),
    ],
    costs=[
        _cost("Online additions (k)", "O(k α(n))", "O(n)", ""),
        _cost("Weighted / parity DSU", "O(m α(n))", "O(n)", "One extra array."),
        _cost("Offline threshold queries", "O((m + q) log(m + q))", "O(n + m + q)", "The sorts dominate."),
    ],
    pitfalls=[
        _pit("A weighted DSU reports false contradictions after many operations",
             "Offsets were accumulated in the wrong order during compression.",
             "Fix each node's offset after its parent's: walk the path from the root side outwards."),
        _pit("Island counts go wrong when a cell is added twice",
             "The second addition counted a new island.",
             "Skip cells that are already land."),
        _pit("Offline answers come out in the wrong order",
             "The answers were appended in sorted-query order.",
             "Store each answer at its query's original index."),
    ],
    checks=[
        _chk("Why can union-find not answer \"is a connected to b if edge e is removed\"?",
             "It stores only the partition, not which union created each link — compression "
             "erased the history. Deletions are handled by reordering queries offline."),
        _chk("In a weighted DSU, what does off[x] mean after find(x)?",
             "x's value minus its root's value, because find re-pointed x at the root."),
        _chk("How does parity DSU detect an odd cycle?",
             "An edge between two vertices of the same set whose parities to the root are "
             "equal would put them on the same side — the cycle through the tree is odd."),
    ],
    traces=[_t6_offset_dsu(), _t6_offline()],
)


_D6_MST = dict(
    invariant=_inv(
        "The edges chosen so far are **a subset of some minimum spanning tree**.",
        "Before any edge is chosen, the empty set is a subset of every MST.",
        "Kruskal adds the cheapest edge e that joins two different components. Take the cut "
        "separating one of those components from everything else: e is a lightest edge "
        "crossing it, and no chosen edge crosses it. The **cut property** says some MST "
        "contains the chosen edges plus e — swap e in for whichever MST edge crosses that cut; "
        "the weight cannot rise. Prim's step is the same argument with the cut around its tree.",
        "After n − 1 edges the chosen set is spanning and a subset of an MST — so it *is* an MST.",
        "Ties only change *which* MST you get, never its weight. The cycle property is the mirror "
        "image: the heaviest edge on any cycle (strictly heaviest) is in no MST.",
    ),
    variants=[
        _var("Kruskal", "Sort edges; union the ones joining different sets.", "Sparse graphs, edge lists.",
             "O(E log E)", "Count n − 1 edges to detect disconnection."),
        _var("Prim with a heap", "Grow one tree; cheapest edge leaving it.", "Adjacency lists.",
             "O(E log V)", "Skip stale heap entries."),
        _var("Dense Prim", "An array of best connection costs, scanned each round.",
             "Complete graphs (points in the plane).", "O(V²)", "No heap needed — or wanted."),
        _var("Virtual node", "A per-vertex cost becomes an edge to an invented vertex.",
             "Generators / wells / \"or build your own\".", "O((E + V) log)", "The MST must include the new vertex."),
        _var("Forced edge", "Union it first, then Kruskal.", "An edge that must be used; is e in some MST?",
             "O(E log E)", "Add its weight once."),
        _var("Excluded edge", "Skip it during Kruskal.", "Critical edges, second-best MST.",
             "O(E²) by brute force", "Disconnection means the edge was critical."),
        _var("Maximum spanning tree", "Sort descending.", "Widest paths, max-reliability networks.",
             "O(E log E)", "Everything else is identical."),
        _var("Bottleneck (minimax) path", "The MST path minimises its heaviest edge.",
             "Minimise the steepest step, many queries.", "O(E log E + q · V)", "Build once, walk per query."),
        _var("Partial Kruskal", "Stop when k components remain.", "Clustering into k groups.",
             "O(E log E)", "The next edge is the spacing."),
    ],
    rewrites=[
        _rw("From \"try every tree\" to Kruskal",
            """
long best = Long.MAX_VALUE;
for (Set<Edge> t : allSubsetsOfSize(edges, n - 1))      // C(E, n - 1) of them
    if (spans(t)) best = Math.min(best, weight(t));
""",
            """
Arrays.sort(edges, byWeight);
long total = 0;
for (int[] e : edges)
    if (union(e[0], e[1])) total += e[2];
""",
            "Replace the search with the greedy that the cut property licenses.",
            """
The cut property guarantees every edge Kruskal accepts belongs to some MST alongside the ones
already chosen, so the greedy never has to reconsider. Exponentially many candidate trees
become one sort and E near-constant unions.
"""),
        _rw("Generators: an edge to nowhere, not a subset search",
            """
for (int mask = 1; mask < (1 << n); mask++)             // which towns get generators
    best = Math.min(best, genCost(mask) + mstWithSourcesContracted(mask));
""",
            """
for (int i = 0; i < n; i++) edges.add(new int[]{n, i, g[i]});   // virtual node n
return kruskal(n + 1, edges);
""",
            "Model each generator as an edge from a new vertex.",
            """
A powered network is exactly a spanning tree of the n + 1 vertices: every town connects to the
virtual station through cables and one generator edge. So the minimum over all generator
placements *is* the MST of the augmented graph.
"""),
    ],
    internals="""
### The cut and cycle properties

- **Cut property**: for any split of the vertices into two sides, a lightest edge crossing the
  split belongs to some MST. Kruskal and Prim are both just repeated applications of it.
- **Cycle property**: on any cycle, an edge strictly heavier than all others belongs to no MST.
  That is the \"reject\" half of Kruskal: an edge whose ends are already connected closes a
  cycle and is the heaviest on it (everything earlier was lighter).

### Ties and uniqueness

With distinct weights the MST is unique. With ties there may be several, all of the same total
weight — which is why problems ask for the weight, not the tree, unless they fix a tie rule.
An edge is in *some* MST iff forcing it does not raise the weight; in *every* MST iff removing
it raises the weight (or disconnects the graph).

### Kruskal or Prim

| | Kruskal | Prim (heap) | Prim (array) |
| --- | --- | --- | --- |
| Time | O(E log E) | O(E log V) | O(V²) |
| Needs | an edge list | adjacency lists | an adjacency matrix / a formula |
| Best for | sparse graphs | sparse graphs | complete graphs |

On a complete graph of V points, E ≈ V²/2: Kruskal is O(V² log V) just to sort, while array
Prim is O(V²) with no edge list at all.

### The MST as a bottleneck tree

Among all paths between two vertices, the MST path minimises the heaviest edge. So one MST
answers every \"minimise the worst step\" question — and a maximum spanning tree answers every
\"maximise the narrowest pipe\" question.
""",
    build_it="""
### Kruskal and Prim, cross-checked

**1. `kruskal(n, edges)`** → total weight, or −1 if disconnected.

**2. `primHeap(n, adj)`** and **`primDense(n, w[][])`** → total weight.

**3. Properties on 1,000 random connected graphs**: all three agree; the chosen edge count is
n − 1; the chosen edges form no cycle.

**4. Brute force for n ≤ 7**: enumerate all subsets of n − 1 edges, keep the spanning ones,
take the minimum — Kruskal must match.

**5. `inSomeMST(e)`** (forced-edge weight equals the MST weight) and **`inEveryMST(e)`**
(excluding e raises the weight or disconnects). Check both against the brute force.

**6. `bottleneck(a, b)`** on the MST versus binary search + BFS on the original graph.
""",
    skeletons=[
        _sk("Virtual node",
            "Per-vertex \"build your own\" costs.",
            """
List<int[]> all = new ArrayList<>(Arrays.asList(edges));
for (int i = 0; i < n; i++) all.add(new int[]{n, i, cost[i]});
all.sort((a, b) -> Integer.compare(a[2], b[2]));
// Kruskal on n + 1 vertices
""",
            "The MST always connects the virtual vertex, so at least one \"own\" is built."),
        _sk("Forced edge",
            "An edge that must be in the tree.",
            """
union(edges[k][0], edges[k][1]);
long total = edges[k][2];
for (int[] e : sortedEdges)
    if (union(e[0], e[1])) total += e[2];
""",
            "Contract first; Kruskal skips it later automatically."),
        _sk("Bottleneck queries on the MST",
            "Minimise the heaviest edge between a and b.",
            """
// tree = Kruskal's accepted edges as adjacency lists
int[] best = new int[n]; Arrays.fill(best, -1);
best[a] = 0; queue.add(a);
while (!queue.isEmpty()) {
    int x = queue.poll();
    for (int[] yw : tree[x])
        if (best[yw[0]] < 0 && yw[0] != a) { best[yw[0]] = Math.max(best[x], yw[1]); queue.add(yw[0]); }
}
// answer: best[b] (−1 if not connected)
""",
            "With many queries, binary lifting stores the max edge per jump."),
    ],
    signals=[
        _sig("“connect everything, either build X at a node or link nodes”", "Virtual node + MST",
             "The per-node cost is an edge to an invented node."),
        _sig("“this edge must be included”", "Forced-edge Kruskal",
             "Contract it, then run as usual."),
        _sig("“minimise the maximum edge on a route”", "MST path (minimax)",
             "One MST answers every pair."),
        _sig("“cheapest way to connect, or −1”", "Kruskal with an edge count",
             "Fewer than n − 1 unions means disconnected."),
    ],
    costs=[
        _cost("Kruskal with virtual node", "O((E + V) log(E + V))", "O(E + V)", ""),
        _cost("Bottleneck queries", "O(E log E + q · V)", "O(V + E)", "q tree walks."),
    ],
    pitfalls=[
        _pit("The answer ignores that the graph is disconnected",
             "Kruskal's total was returned without checking how many edges were taken.",
             "Return −1 unless exactly n − 1 unions succeeded."),
        _pit("A forced edge is counted twice",
             "It was added before the loop and again when the loop reached it.",
             "Union it before the loop: the loop then sees its ends connected and skips it."),
        _pit("Generators are all skipped",
             "The virtual node's index collided with a real town (n instead of n + 1 sized arrays).",
             "Size the DSU n + 1 and use index n for the station."),
    ],
    checks=[
        _chk("State the cut property.",
             "For any partition of the vertices, a lightest edge crossing it belongs to some MST."),
        _chk("Why does the MST path minimise the heaviest edge between two vertices?",
             "A path using a heavier edge could replace it: that edge closes a cycle with the MST "
             "path, on which it is the heaviest, so the MST path is no worse (cycle property)."),
        _chk("When is dense Prim better than Kruskal?",
             "On complete (or near-complete) graphs: O(V²) without building or sorting V²/2 edges."),
    ],
    traces=[_t6_virtual_node()],
)


_D6_SP = dict(
    invariant=_inv(
        "Dijkstra: **every vertex popped for the first time (not stale) has its final shortest "
        "distance**; every vertex still in the heap has dist = the best path found so far "
        "whose last edge leaves a finished vertex.",
        "The source is pushed with distance 0, and with non-negative weights nothing can reach "
        "it more cheaply.",
        "Pop u with the smallest tentative distance d. Any other path to u leaves the finished "
        "set at some vertex x in the heap with dist[x] ≥ d, then adds non-negative edges — so "
        "it is at least d. So d is final. Relaxing u's edges keeps every tentative distance "
        "equal to the best path through finished vertices.",
        "When the heap empties, every reachable vertex has been finished with its true distance.",
        "The argument breaks exactly where weights are negative (a later edge could make the "
        "path shorter) — which is why Bellman-Ford exists, with its own invariant: after round "
        "k, dist[v] is at most the best walk to v using ≤ k edges.",
    ),
    variants=[
        _var("BFS", "Every edge weighs 1.", "Unweighted shortest hops.", "O(V + E)", "Use Dijkstra only when weights differ."),
        _var("0-1 BFS", "Weight-0 edges to the front of a deque, weight-1 to the back.",
             "Costs of only 0 and 1.", "O(V + E)", "A vertex may be pushed twice."),
        _var("Dijkstra", "Min-heap on distance; skip stale entries.", "Non-negative weights.",
             "O((V + E) log V)", "long distances."),
        _var("Multi-source Dijkstra", "Push every source at 0.", "Nearest facility.",
             "O((V + E) log V)", "One run, not k."),
        _var("Path reconstruction", "parent[] on relaxation, or walk tight edges from dist[].",
             "Print the route; choose among ties.", "+O(V + E)", "Run from the target to walk forwards."),
        _var("Widest path", "Combine with min, compare with max.", "Maximise the bottleneck.",
             "O((V + E) log V)", "Start the source at +∞."),
        _var("State-augmented Dijkstra", "Vertex = (node, extra) — coupons used, stops left.",
             "Discounts, fuel, k stops.", "O(X (V + E) log)", "dist over states."),
        _var("k best / second best", "k slots per vertex.", "Second-shortest route.",
             "O(k (V + E) log)", "\"Strictly\" larger: skip ties."),
        _var("Bellman-Ford", "Relax all edges V − 1 times.", "Negative weights; ≤ k edges.",
             "O(V · E)", "Copy dist per round for a hop limit."),
        _var("Negative cycle detection", "A V-th round that still relaxes.",
             "Arbitrage, infeasible constraints.", "O(V · E)", "Start all at 0 to find any cycle."),
        _var("Floyd–Warshall", "dist[i][j] via k, k outermost.", "All pairs, V ≤ 400.",
             "O(V³)", "k must be the outer loop."),
    ],
    rewrites=[
        _rw("Minimum by heap, not by scan",
            """
for (int it = 0; it < V; it++) {
    int u = -1;
    for (int v = 0; v < V; v++)                    // O(V) per pick
        if (!done[v] && (u < 0 || dist[v] < dist[u])) u = v;
    done[u] = true;
    for (int[] e : adj[u]) dist[e[0]] = Math.min(dist[e[0]], dist[u] + e[1]);
}
""",
            """
pq.add(new long[]{0, src});
while (!pq.isEmpty()) {
    long[] t = pq.poll();
    int u = (int) t[1];
    if (t[0] > dist[u]) continue;                   // stale
    for (int[] e : adj[u])
        if (t[0] + e[1] < dist[e[0]]) { dist[e[0]] = t[0] + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
}
""",
            "Replace the linear minimum search with a priority queue.",
            """
Both pick the unfinished vertex with the smallest distance — the invariant needs nothing
else. The scan costs O(V) per pick (O(V²) total, right for dense graphs); the heap costs
O(log V) per push, O((V + E) log V) total, right for sparse ones.
"""),
        _rw("No decrease-key: push duplicates, skip stale",
            """
// java.util.PriorityQueue has no decrease-key:
pq.remove(oldEntry);                     // O(V) linear search!
pq.add(newEntry);
""",
            """
pq.add(new long[]{newDist, v});          // just push again
// …and when popping:
if (top[0] > dist[(int) top[1]]) continue;   // an out-of-date copy
""",
            "Allow several entries per vertex; ignore the stale ones when popped.",
            """
The newest entry has the smallest distance, so it is popped first and finishes the vertex;
later copies fail the `> dist` test and cost only a pop. At most E pushes happen, so the heap
holds O(E) entries and the run is O(E log E) = O(E log V).
"""),
        _rw("Nearest source: one Dijkstra, not k",
            """
for (int s : sources) {
    long[] d = dijkstra(s);
    for (int v = 0; v < n; v++) best[v] = Math.min(best[v], d[v]);
}
""",
            """
Arrays.fill(dist, INF);
for (int s : sources) { dist[s] = 0; pq.add(new long[]{0, s}); }
// … one Dijkstra loop
""",
            "Seed the heap with all sources at distance 0.",
            """
It is Dijkstra from a virtual vertex with 0-weight edges to each source; the invariant holds
unchanged, and each vertex is finished at its distance to the nearest source.
"""),
    ],
    internals="""
### `PriorityQueue` and the missing decrease-key

Textbook Dijkstra lowers a vertex's key inside the heap. `java.util.PriorityQueue` cannot do
that efficiently — `remove(Object)` is a linear search — so the Java idiom is **lazy
deletion**: push a new entry and skip stale ones on pop. The heap may hold up to E entries,
which costs a factor of log E instead of log V; since E ≤ V², log E ≤ 2 log V and the bound is
unchanged.

### `long` distances

A path of 10⁵ edges of weight 10⁹ is 10¹⁴ — far past `int`. Store distances in `long[]`, and
use `Long.MAX_VALUE / 4` as infinity so that `INF + w` cannot wrap around to a negative number
and look like a short path.

### Why Floyd–Warshall's k loop is outermost

`dist[i][j]` after the k-th outer iteration is the shortest path using only intermediate
vertices from {0, …, k}. That statement is only true if every pair has been updated for k
before any pair is updated for k + 1 — so k must be the outer loop. Putting it innermost
gives a plausible-looking wrong answer.

### Which algorithm

| Weights | One source | All pairs |
| --- | --- | --- |
| all 1 | BFS, O(V + E) | V × BFS |
| 0 or 1 | 0-1 BFS, O(V + E) | V × 0-1 BFS |
| non-negative | Dijkstra, O((V + E) log V) | V × Dijkstra, or Floyd for dense |
| negative, no negative cycle | Bellman-Ford, O(V · E) | Floyd, O(V³) |
| a DAG, any weights | DP in topological order, O(V + E) | — |
""",
    build_it="""
### Dijkstra, Bellman-Ford and Floyd, cross-checked

**1. `dijkstra(adj, src)`** with lazy deletion and `long` distances.

**2. `bellmanFord(n, edges, src)`** returning distances or a \"negative cycle\" flag.

**3. `floyd(n, w)`** with `k` outermost.

**4. Properties on 1,000 random graphs** (non-negative weights): all three agree from every
source; `dijkstra` from a vertex equals BFS when every weight is 1; `0-1 BFS` equals
`dijkstra` when weights are 0/1.

**5. Negative weights**: `bellmanFord` agrees with `floyd`; plant a negative cycle and check
both detect it (Floyd: some dist[i][i] < 0).

**6. `route(src, dst)`**: reconstruct a path and check its length equals the distance and
every edge on it is tight.
""",
    skeletons=[
        _sk("Multi-source Dijkstra",
            "Distance to the nearest of several sources.",
            """
Arrays.fill(dist, INF);
for (int s : sources) if (dist[s] != 0) { dist[s] = 0; pq.add(new long[]{0, s}); }
while (!pq.isEmpty()) {
    long[] t = pq.poll();
    int u = (int) t[1];
    if (t[0] > dist[u]) continue;
    for (int[] e : adj[u])
        if (t[0] + e[1] < dist[e[0]]) { dist[e[0]] = t[0] + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
}
""",
            "Repeated sources must not be pushed twice at 0 — harmless, but wasteful."),
        _sk("Walk the tight edges",
            "Reconstruct a shortest route, choosing among ties.",
            """
long[] toT = dijkstra(adj, target);          // distances TO the target
int u = source;
route.add(u);
while (u != target) {
    int next = Integer.MAX_VALUE;
    for (int[] e : adj[u]) if (e[1] + toT[e[0]] == toT[u]) next = Math.min(next, e[0]);
    route.add(u = next);
}
""",
            "Needs positive weights so the walk strictly approaches the target."),
        _sk("Second-shortest with two slots",
            "The strictly second-best distance.",
            """
while (!pq.isEmpty()) {
    long[] t = pq.poll();
    int u = (int) t[1];
    if (t[0] > second[u]) continue;
    for (int[] e : adj[u]) {
        long nd = t[0] + e[1];
        int v = e[0];
        if (nd < best[v]) { second[v] = best[v]; best[v] = nd; pq.add(new long[]{nd, v}); }
        else if (nd > best[v] && nd < second[v]) { second[v] = nd; pq.add(new long[]{nd, v}); }
    }
}
""",
            "`nd > best[v]` — strictly — or ties become the runner-up."),
        _sk("Negative-cycle detection",
            "Is there any negative cycle at all?",
            """
long[] dist = new long[n];                  // all 0: a virtual source
for (int round = 1; round <= n; round++) {
    boolean changed = false;
    for (int[] e : edges)
        if (dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
    if (!changed) return false;
}
return true;
""",
            "Round n improving anything means a negative cycle."),
    ],
    signals=[
        _sig("“print the route”, “which way”", "Dijkstra + walk tight edges (or parent[])",
             "Distances describe every shortest path."),
        _sig("“nearest hospital / store / exit” for every vertex", "Multi-source Dijkstra",
             "All sources at 0."),
        _sig("“maximise the minimum capacity on the route”", "Widest-path Dijkstra (or max spanning tree)",
             "min to combine, max to compare."),
        _sig("“second-best”, “strictly longer than the shortest”", "Two slots per vertex",
             "Each vertex expanded at most twice."),
        _sig("“free money loop”, “arbitrage”, “infeasible constraints”", "Bellman-Ford's n-th round",
             "Start every dist at 0."),
    ],
    costs=[
        _cost("Multi-source Dijkstra", "O((V + E) log V)", "O(V + E)", ""),
        _cost("Second-shortest", "O((V + E) log V)", "O(V + E)", "Two slots."),
        _cost("Negative-cycle check", "O(V · E)", "O(V)", "Early exit when quiet."),
    ],
    pitfalls=[
        _pit("The second-shortest answer equals the shortest",
             "A tie was accepted as the second slot.",
             "Only accept nd with best[v] < nd < second[v]."),
        _pit("A negative cycle far from vertex 0 is missed",
             "dist started at INF everywhere except the source.",
             "Start every distance at 0 (a virtual source to all), or run from every component."),
        _pit("Path reconstruction loops forever",
             "Zero-weight edges let the tight-edge walk go back and forth.",
             "With zero weights, walk a parent[] array (or require w ≥ 1)."),
    ],
    checks=[
        _chk("Why does Dijkstra fail with a negative edge?",
             "A popped vertex is assumed final because later edges only add; a negative edge "
             "can make a longer path shorter after the vertex was finalised."),
        _chk("How do you find a negative cycle anywhere in the graph with Bellman-Ford?",
             "Start every dist at 0 and run n rounds; any improvement in round n proves a cycle."),
        _chk("Why run Dijkstra from the target to print the lexicographically smallest route?",
             "Walking forwards needs, at each junction, which neighbours still lead to the target "
             "optimally — a fact about distances *to* the target."),
    ],
    traces=[_t6_bellman(), _t6_second_best()],
)


# ================================================================== the ladders
#
# Rebuilt rather than edited, as in dsa_s4_depth.py: the syllabus and placement
# files moved problems into these units over several rounds. Every slug the
# units held before is asserted to be somewhere below.

_S6_NEW_NOTES = {
    # trees
    "leaf-similar-trees": "A traversal is a stream: any left-before-right walk meets the leaves in order.",
    "vertical-order-tree": "Carry (row, col) down from the parent; the tie rule inside one cell is the whole difficulty.",
    "tree-postorder-inorder": "Post-order backwards is root, right, left — so build the right subtree first.",
    "flatten-tree-to-list": "Splice the left subtree between a node and its right subtree: three pointer writes, O(1) memory.",
    "max-ancestor-difference": "Pass the path's min and max down; the answer is the widest gap on any root path.",
    "path-sum-list": "Backtracking on a tree: push, recurse both ways, pop — and record a copy.",
    "boundary-of-tree": "Three simple walks beat one clever one. Leaves are printed in exactly one of them.",
    "sum-of-distances-tree": "Rerooting: one bottom-up pass for sizes, one top-down pass moving the root an edge at a time.",
    "tree-cameras": "Three states per node, decided bottom-up; a null child is already watched.",
    # bst
    "sorted-array-to-bst": "The middle of the range is the root. Balance is chosen, not repaired.",
    "bst-mode": "In-order makes equal values adjacent: count runs, keep the longest.",
    "bst-delete": "0 or 1 child: splice. 2 children: copy the in-order successor in, then delete it below.",
    "trim-bst": "A node below the range condemns its whole left subtree — return the trimmed right one.",
    "merge-two-bsts": "Two BST iterators merged like two sorted arrays.",
    # backtracking
    "binary-strings-n": "The smallest search tree there is: two choices per level, 2ⁿ leaves.",
    "partition-k-equal": "Largest items first, and never try a bucket whose load equals the previous one.",
    "map-colorings-count": "Check a colour against already-coloured neighbours before descending.",
    "word-break-sentences": "A right-to-left word-break table first; then the search enters only branches that finish.",
    "expression-target-count": "Carry (value, last) so `*` can take the last term back out.",
    # graph traversal
    "bfs-levels": "The BFS template, printing dist[] — and −1 doubling as the visited set.",
    "board-game-fewest-rolls": "The edges are a rule: roll 1–6, then follow the shortcut. Mark where you land.",
    "grid-k-breaks": "The state is (cell, walls broken). A cell reached with fewer breaks dominates.",
    "keys-and-doors-bfs": "The visited set is over (cell, keys held) — a bitmask of at most 64 values.",
    # topological sort
    "semester-levels": "Kahn in layers: a course's semester is one more than its freeing prerequisite's.",
    "unique-topo-order": "The order is unique exactly when Kahn's queue never holds two vertices.",
    "dag-path-count": "Kahn's loop is the DP loop: push each station's count along its slopes.",
    "critical-path-time": "The longest path in a DAG, computed in topological order with max.",
    # union-find
    "islands-after-each-add": "+1 for the new cell, −1 for every union that actually merges.",
    "height-claims": "Weighted union-find: offsets to the root make every known difference an O(α) lookup.",
    "first-odd-cycle": "Parity union-find: a rivalry inside one group on the same side is the odd cycle.",
    "limited-weight-reachability": "Offline: heaviest trucks first, so the usable bridges only ever grow.",
    # mst
    "cheapest-road-network": "Kruskal, and −1 when fewer than n − 1 roads were taken.",
    "power-grid-generators": "A generator is a cable to an invented power station. Then it is just an MST.",
    "mst-forced-edge": "Union the promised road first; Kruskal does the rest.",
    "bottleneck-route": "The MST path minimises the steepest step. Build once, walk per query.",
    # shortest paths
    "dijkstra-path-print": "Dijkstra from the target, then walk tight edges choosing the smallest junction.",
    "nearest-hospital": "Every hospital in the heap at distance 0: one run, not k.",
    "negative-cycle-detect": "Start every distance at 0; improvement in round n means a negative cycle.",
    "widest-path": "Dijkstra with min to combine and max to choose.",
    "second-shortest-path": "Two slots per vertex; strictly larger for the second.",
    # round 2
    "distribute-coins-tree": "Count per edge, not per move: each edge carries |coins − nodes| of the subtree below it.",
    "flip-equivalent-trees": "Pair recursion with a choice: children match straight or crossed.",
    "longest-zigzag-tree": "Return two lengths — continuing left, continuing right — and let the parent pick the alternating one.",
    "tree-diameter-general": "The double sweep: the farthest vertex from anywhere is an end of a diameter.",
    "bst-greater-sum": "Right, node, left is descending order; a running sum over it is a suffix sum.",
    "balance-bst": "In-order to a sorted list, then the middle-first build — two problems you already know.",
    "two-bst-pair-sum": "An ascending iterator and a descending one: two pointers on two trees.",
    "letter-tile-sequences": "Choose among distinct letters with counts, so equal tiles are never two choices.",
    "n-queens-boards": "The queens search, printing every board — three occupancy arrays keep each check O(1).",
    "count-sub-islands": "A flood fill that ANDs a condition over the whole island — and keeps filling after it fails.",
    "alternating-colour-paths": "The last edge's colour is part of the state: BFS over 2n states.",
    "all-ancestors-dag": "DP in topological order carrying a set (a bitset) instead of a number.",
    "dag-shortest-negative": "On a DAG, one pass in topological order handles negative weights.",
    "smallest-equivalent-string": "Choose the root to carry the answer: the smallest letter of each class.",
    "gcd-connectivity": "Union each clique through one hub: every multiple of d with d itself.",
    "max-spanning-tree": "Kruskal with the sort reversed.",
    "second-best-mst": "One swap from an MST: a non-tree edge in, the heaviest strictly lighter path edge out.",
    "cost-within-deadline": "A resource limit becomes a state dimension: (junction, minutes used).",
    "reachability-queries": "More questions than answers: precompute the whole reachability table once.",
    # round 3
    "count-univalue-subtrees": "Return a boolean, count the trues — and call both children before combining.",
    "insufficient-nodes-prune": "The sum flows down, the verdict flows up; a node whose children all fail goes too.",
    "bst-range-count": "The pruned range walk: go left only if there can be smaller in-range values, right likewise.",
    "inorder-predecessor": "One descent; every right turn records a candidate, and the last one wins.",
    "max-unique-split": "Split points with a used-set, and a bound: count + remaining ≤ best means stop.",
    "split-into-fibonacci": "Only the first two numbers are choices; everything after is forced verification.",
    "gene-mutation-steps": "Generate the 3L one-letter neighbours and test them against the bank.",
    "regions-by-slashes": "Split each tile into four triangles; then it is a component count.",
    "portal-maze": "A portal is one more unit-cost edge; BFS does not care that it is not adjacent.",
}

# Problems that were already on these ladders without a rung note.
_S6_OLD_NOTES = {
    "count-nodes-tree": "One plus the two subtree counts. (For a complete tree, compare the leftmost and rightmost depths to skip whole perfect subtrees.)",
    "invert-binary-tree": "Swap the children, then recurse — or recurse, then swap. Either order works; say why.",
    "same-tree": "Recurse on two nodes at once. Both null is equal; one null is not.",
    "path-sum-exists": "Top-down: subtract as you descend and test only at a real leaf.",
    "right-side-view": "Level BFS, keeping the last node of each level — or a DFS that visits right first and records depth firsts.",
    "diameter-of-tree": "Return the height, record left + right at every node. The answer need not pass through the root.",
    "lca-bst": "Walk down while both values are on one side; the split point is the answer.",
    "bst-insert": "Descend to the null where the value belongs and attach it there — the invariant tells you the only place.",
    "combinations-nk": "Subsets with a size cap; prune when too few elements remain to reach k.",
    "subset-sum-count": "Include or exclude each element; with positive values, sort and break early.",
    "letter-combinations-phone": "One level per digit, one branch per letter. The output size is the cost.",
    "palindrome-partition-count": "Choose where the next palindrome ends; a precomputed palindrome table makes each check O(1).",
    "restore-ip-addresses": "Four pieces, each 0–255 without leading zeros. Prune on the length that remains.",
    "bipartite-check": "Two-colour every component; a neighbour with your colour is an odd cycle.",
    "course-schedule-possible": "Kahn's algorithm, and compare the output count with n.",
    "number-of-provinces": "Components from an adjacency matrix: union every 1, count the roots.",
    "detect-cycle-undirected": "An edge whose ends already share a root closes a cycle.",
    "largest-component-size": "Union by size, then read the largest size at a root.",
    "make-network-connected": "Spare cables = edges − (n − components). Enough spares to join the components, or −1.",
}

_S6_LADDERS = {
    "trees": [
        ("Warm up", "One value, computed from the children.",
         ["max-depth-tree", "count-nodes-tree", "invert-binary-tree"], False),
        ("Core", "Two-node recursion, and context carried downwards.",
         ["same-tree", "path-sum-exists", "inorder-traversal"], False),
        ("Variations", "Anything phrased in terms of levels.",
         ["level-order-traversal", "right-side-view"], False),
        ("Build and walk", "Write a tree down, and read it back.",
         ["serialize-tree-preorder", "deserialize-tree-preorder", "build-tree-preorder-inorder"], False),
        ("Stretch", "Return one thing, record another.",
         ["diameter-of-tree", "lca-binary-tree", "max-path-sum"], False),
        ("Views and orders", "Coordinates, outlines, the other rebuild, and a tree rewired in place.",
         ["leaf-similar-trees", "vertical-order-tree", "boundary-of-tree", "tree-postorder-inorder",
          "flatten-tree-to-list", "flip-equivalent-trees"], True),
        ("Top-down and paths", "Carry the path, or the path's extremes, down the tree.",
         ["max-ancestor-difference", "path-sum-list", "longest-zigzag-tree", "count-univalue-subtrees",
          "insufficient-nodes-prune"], True),
        ("Whole-tree answers", "Flows, rerooting, greedy covers and unrooted diameters — tree DP past the (take, skip) pair.",
         ["distribute-coins-tree", "tree-diameter-general", "sum-of-distances-tree", "tree-cameras"], True),
        ("Extra practice", "The same recursions with one line moved — reps, not new ideas.", None, True),
    ],
    "bst": [
        ("Core", "The descent, and the in-order walk.",
         ["bst-search", "range-sum-bst", "bst-min-difference"], False),
        ("Variations", "The invariant, used and checked.",
         ["validate-bst", "lca-bst", "kth-smallest-bst"], False),
        ("Iterators & ordered maps", "A paused in-order, and TreeMap as a tool.",
         ["floor-ceiling-queries", "bst-iterator", "nearby-almost-duplicate"], False),
        ("Changing the tree", "Build, delete and trim without breaking the invariant.",
         ["sorted-array-to-bst", "bst-insert", "bst-delete", "trim-bst", "balance-bst"], True),
        ("Using the order", "In-order as a sorted stream, forwards and backwards: runs, merges, suffix sums, two pointers.",
         ["bst-range-count", "bst-mode", "inorder-predecessor", "merge-two-bsts", "bst-greater-sum",
          "two-bst-pair-sum"], True),
        ("Extra practice", "More descents and more in-order walks.", None, True),
    ],
    "backtracking": [
        ("Warm up", "Answers you can check by hand, and the line that matters.",
         ["binary-strings-n", "all-subsets-small"], False),
        ("Core", "The template, with the three choice-set variants.",
         ["generate-subsets", "combinations-nk", "generate-permutations"], False),
        ("Variations", "Counting instead of listing, and constrained construction.",
         ["subset-sum-count", "combination-sum-count", "generate-parentheses",
          "letter-combinations-phone", "matchsticks-to-square"], False),
        ("Stretch", "Pruning is the difference between finishing and not.",
         ["palindrome-partition-count", "word-search", "n-queens-count", "sudoku-solvable"], False),
        ("Harder searches", "Symmetry, constraints, pruning tables and carried state.",
         ["letter-tile-sequences", "max-unique-split", "split-into-fibonacci", "partition-k-equal",
          "map-colorings-count", "word-break-sentences", "expression-target-count", "n-queens-boards"], True),
        ("Extra practice", "The same four lines on new prompts.", None, True),
    ],
    "graph-traversal": [
        ("Warm up", "One BFS, and the outer loop that turns it into an answer.",
         ["bfs-levels", "count-connected-components", "island-perimeter"], False),
        ("Core", "Traversal on an implicit graph, then a real one, then a directed one.",
         ["number-of-islands", "shortest-path-binary-matrix", "bipartite-check", "directed-path-exists",
          "surrounded-regions"], False),
        ("Variations", "One BFS, many sources — and one BFS that stops early.",
         ["rotting-oranges", "pacific-atlantic", "shortest-bridge", "clone-graph"], False),
        ("Stretch", "Build the graph, or widen the state, before you can walk it.",
         ["word-ladder-length", "grid-k-breaks"], False),
        ("Search over states", "The vertex is a situation, not a place.",
         ["board-game-fewest-rolls", "open-the-lock", "gene-mutation-steps", "portal-maze",
          "alternating-colour-paths", "keys-and-doors-bfs"], True),
        ("Components with a condition", "A flood fill that computes something about the whole component.",
         ["count-sub-islands"], True),
        ("Extra practice", "More grids and more graphs — reps of the same two loops.", None, True),
    ],
    "topological-sort": [
        ("Warm up", "Kahn on a handful of vertices.",
         ["detect-cycle-tiny-dag", "semester-levels"], False),
        ("Core", "Build the graph, count in-degrees, drain the queue.",
         ["course-schedule", "course-schedule-possible", "detect-cycle-directed", "course-order-smallest",
          "parallel-courses"], False),
        ("Stretch", "Infer the graph before you can sort it.",
         ["alien-dictionary-order", "longest-increasing-path-grid"], False),
        ("Reading more from the order", "Uniqueness, path counts and the critical path — DP in topological order.",
         ["unique-topo-order", "dag-path-count", "critical-path-time", "all-ancestors-dag",
          "dag-shortest-negative"], True),
        ("Extra practice", "More orders, more DAG DP.", None, True),
    ],
    "union-find": [
        ("Warm up", "Union by size alone, so path compression is an optimisation rather than an incantation.",
         ["union-by-size-components"], False),
        ("Core", "Counting components, and the boolean return.",
         ["count-components", "number-of-provinces", "graph-valid-tree", "redundant-connection",
          "detect-cycle-undirected"], False),
        ("Variations", "Relations and a grid that grows.",
         ["satisfy-equations", "islands-after-each-add"], False),
        ("Stretch", "Union-find that carries a value along every edge.",
         ["height-claims"], False),
        ("More layers", "Parity, and queries answered in a better order.",
         ["smallest-equivalent-string", "regions-by-slashes", "first-odd-cycle",
          "limited-weight-reachability", "gcd-connectivity"], True),
        ("Extra practice", "Sizes and orderings layered on the same union — reps, not new ideas.", None, True),
    ],
    "mst": [
        ("Warm up", "Kruskal, and the answer when the county cannot be connected.",
         ["cheapest-road-network"], False),
        ("Core", "Kruskal and Prim, each where it fits best.",
         ["mst-total-weight", "prim-dense-graph"], False),
        ("Variations", "Change the graph, not the algorithm.",
         ["power-grid-generators"], False),
        ("Stretch", "An implicit graph, and questions about individual edges.",
         ["min-cost-connect-points", "mst-critical-edges"], False),
        ("More from one tree", "Maximum trees, forced edges, minimax paths and the runner-up tree.",
         ["max-spanning-tree", "mst-forced-edge", "bottleneck-route", "second-best-mst"], True),
    ],
    "shortest-paths": [
        ("Warm up", "Dijkstra with the priority queue deleted.",
         ["grid-bfs-distance"], False),
        ("Core", "Dijkstra, and the two relaxation variants.",
         ["network-delay-time", "cheapest-flights-k-stops", "min-obstacle-removal", "bellman-ford-negative"], False),
        ("All pairs", "Every source at once.",
         ["city-fewest-neighbours", "floyd-warshall-queries"], False),
        ("Stretch", "Build the graph and run it end to end.",
         ["dijkstra-shortest-path", "swim-in-rising-water"], False),
        ("Dijkstra, reshaped", "Routes, many sources, bottlenecks, runners-up, deadlines and negative cycles.",
         ["dijkstra-path-print", "nearest-hospital", "widest-path", "negative-cycle-detect",
          "second-shortest-path", "cost-within-deadline"], True),
        ("Every pair at once", "When the questions outnumber the answers, precompute the table.",
         ["reachability-queries"], True),
        ("Extra practice", "More weighted graphs on the same loop.", None, True),
    ],
}


def _rebuild_s6_ladders():
    by_key = {u["key"]: u for u in _UNITS}
    placed_new = {sl for plan in _S6_LADDERS.values() for _, _, slugs, _ in plan if slugs for sl in slugs}
    for key, plan in _S6_LADDERS.items():
        u = by_key[key]
        before = [sl for r in u["rungs"] for sl in r["slugs"]]
        notes = {sl: n for r in u["rungs"] for sl, n in r["notes"].items()}
        named = {sl for _, _, slugs, _ in plan if slugs for sl in slugs}
        rest = [sl for sl in before if sl not in named]
        rungs = []
        for title, purpose, slugs, optional in plan:
            slugs = list(slugs) if slugs is not None else rest
            if not slugs:
                continue
            rn = {}
            for sl in slugs:
                note = notes.get(sl) or _S6_NEW_NOTES.get(sl) or _S6_OLD_NOTES.get(sl)
                assert note, f"{key}: {sl!r} has no rung note"
                rn[sl] = note
            rungs.append(_rung(title, purpose, slugs, rn, optional=optional))
        after = [sl for r in rungs for sl in r["slugs"]]
        lost = set(before) - set(after)
        assert not lost, f"{key}: the rebuilt ladder drops {sorted(lost)}"
        assert len(after) == len(set(after)), f"{key}: the rebuilt ladder repeats a problem"
        # a slug named in a plan must have come from this unit or be brand new
        u["rungs"] = rungs
    return placed_new


# ================================================================== the router

_S6_ROUTER = [
    _route("An answer about a subtree — height, size, sum, balanced?", "trees",
           "Each node's answer is built from its children's: bottom-up recursion.",
           "If it says “sorted”, “k-th smallest” or “range” and the tree is a BST, the invariant does the work — BSTs."),
    _route("“level by level”, “right side view”, “zigzag”", "trees",
           "Levels are BFS with a frozen queue size.",
           "“Shortest number of moves” on a grid or network is graph BFS, not tree BFS."),
    _route("A best path that may bend anywhere — diameter, max path sum", "trees",
           "Return the one-sided value, record the two-sided one.",
           "If the path must start at the root, it is a top-down parameter."),
    _route("An answer for every node as if it were the root", "trees",
           "Rerooting: two passes, not n traversals.", "A single root → a plain tree DP."),
    _route("Search, insert, delete, floor/ceiling on ordered keys", "bst",
           "Every operation is one descent.",
           "Keys that never need order (just membership) → a HashSet, not a BST."),
    _route("“is this a valid BST?”, “recover two swapped nodes”", "bst",
           "Bounds carried down, or in-order must increase.",
           "Checking each node against its children only is the wrong answer."),
    _route("“k-th smallest”, “merge two BSTs”, “iterate in order”", "bst",
           "In-order is sorted, and pausable with a stack.",
           "k-th smallest of an unsorted array is quickselect (stage 3)."),
    _route("“all subsets / permutations / combinations”, n ≤ 20", "backtracking",
           "Exponential is expected; choose, explore, un-choose.",
           "“How many” with overlapping states → DP (stage 7), not listing."),
    _route("Place items under constraints — queens, colours, buckets, Sudoku", "backtracking",
           "Feasibility checked before descending.",
           "One valid assignment with a greedy rule → greedy, not search."),
    _route("Split a string / digits into valid pieces", "backtracking",
           "Choose where the next piece ends.",
           "Only “can it be split?” → a word-break DP, no listing."),
    _route("Islands, regions, reachability, fewest hops (unweighted)", "graph-traversal",
           "BFS for distance, DFS or BFS for components.",
           "Weights that differ → shortest paths."),
    _route("“keys and doors”, “at most k walls”, a game's fewest moves", "graph-traversal",
           "BFS over a state that includes the extra information.",
           "If moves cost different amounts, Dijkstra over the same states."),
    _route("Prerequisites, build order, “which comes first”", "topological-sort",
           "Kahn's queue of in-degree-0 vertices.",
           "Undirected “is it connected?” is union-find or BFS."),
    _route("Count paths / longest path / critical time in a DAG", "topological-sort",
           "DP in topological order.",
           "On a graph with cycles, longest path is not polynomial — look for a DAG in disguise."),
    _route("“are a and b connected?” while edges are added", "union-find",
           "find(a) == find(b) after each union.",
           "Edges also removed → offline reordering, or a different structure."),
    _route("Relations with values — “a is 3 more than b”, rivals on opposite teams", "union-find",
           "Weighted or parity union-find.",
           "Inequalities between arbitrary pairs (a < b) are a topological sort, not a DSU."),
    _route("Connect everything as cheaply as possible", "mst",
           "Kruskal or Prim.",
           "Cheapest route between two specific vertices → shortest paths, not an MST."),
    _route("“minimise the maximum edge on the route”", "mst",
           "The MST path is the minimax path.",
           "“Minimise the sum” → Dijkstra."),
    _route("Fewest total cost / time between vertices, weights ≥ 0", "shortest-paths",
           "Dijkstra with a heap.",
           "All weights 1 → BFS; only 0 and 1 → 0-1 BFS."),
    _route("Negative weights, “at most k edges”, arbitrage", "shortest-paths",
           "Bellman-Ford's rounds.",
           "Negative weights on a DAG → one DP pass in topological order."),
    _route("Every pair of vertices, V ≤ 400", "shortest-paths",
           "Floyd–Warshall.",
           "V in the thousands → V runs of Dijkstra (or BFS)."),
]


def _attach_s6_depth():
    by_key = {u["key"]: u for u in _UNITS}
    for key, d in (("trees", _D6_TREES), ("bst", _D6_BST), ("backtracking", _D6_BACKTRACK),
                   ("graph-traversal", _D6_GRAPH), ("topological-sort", _D6_TOPO),
                   ("union-find", _D6_UF), ("mst", _D6_MST), ("shortest-paths", _D6_SP)):
        u = by_key[key]
        u["invariant"] = d["invariant"]
        u["variants"].extend(d["variants"])
        u["rewrites"].extend(d["rewrites"])
        if d.get("internals"):
            # trees already has internals of its own; the others gain theirs here
            u["internals"] = _md(d["internals"]) if not u["internals"].strip() else u["internals"]
        if d.get("build_it"):
            if not u["build_it"].strip():
                u["build_it"] = _md(d["build_it"])
        for field in ("skeletons", "signals", "costs", "pitfalls", "checks", "traces"):
            u[field].extend(d[field])
        u["bigo"].extend({**_BIGO_S6A, **_BIGO_S6B}[key])
    for st in _STAGES:
        if st["key"] == "hierarchies":
            st["router"] = list(_S6_ROUTER)


_attach_s6_depth()
_rebuild_s6_ladders()
