# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 (Trees & Graphs) — the help layer, part 2: topological sort,
# union-find, minimum spanning trees and shortest paths; the stage cheat
# sheet; and the step that attaches both help files.
#
# exec'd by tools/dsa_curriculum.py right after dsa_s6_help.py, whose `_c6_*`
# helpers it reuses. As there, every work-it-out answer is computed.
# ---------------------------------------------------------------------------


# ============================================================ computing kit

def _c6_kahn(n, edges, smallest=False):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    ready = [v for v in range(n) if indeg[v] == 0]
    out = []
    while ready:
        if smallest:
            ready.sort()
        u = ready.pop(0)
        out.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return out


def _c6_semesters(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    sem = [1 if indeg[v] == 0 else 0 for v in range(n)]
    q = _dq(v for v in range(n) if indeg[v] == 0)
    while q:
        u = q.popleft()
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                sem[v] = sem[u] + 1
                q.append(v)
    return sem


def _c6_paths(n, edges, s, t):
    order = _c6_kahn(n, edges)
    ways = [0] * n
    ways[s] = 1
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    for u in order:
        for v in adj[u]:
            ways[v] += ways[u]
    return ways[t]


def _c6_count_topo(n, edges):
    from itertools import permutations as _perm
    return sum(1 for p in _perm(range(n))
               if all(p.index(u) < p.index(v) for u, v in edges))


def _c6_dsu_trace(n, edges):
    """Union by size (ties: the second root goes under the first), with path
    compression. Returns parent[] after all unions and the component count."""
    parent, size = list(range(n)), [1] * n

    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r

    for u, v in edges:
        a, b = find(u), find(v)
        if a == b:
            continue
        if size[a] < size[b]:
            a, b = b, a
        parent[b] = a
        size[a] += size[b]
    after = list(parent)          # before the counting finds compress anything else
    return after, len({find(x) for x in range(n)})


def _c6_kruskal(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    total, taken = 0, []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        a, b = find(u), find(v)
        if a != b:
            parent[a] = b
            total += w
            taken.append((u, v, w))
    return total, taken


def _c6_prim_order(n, edges, s):
    adj = _c6_adj(n, edges, False)
    best = [float("inf")] * n
    best[s] = 0
    done, order = [False] * n, []
    for _ in range(n):
        u = min((x for x in range(n) if not done[x]), key=lambda x: (best[x], x))
        done[u] = True
        order.append(u)
        for v, w in adj[u]:
            if not done[v] and w < best[v]:
                best[v] = w
    return order


def _c6_dijkstra(n, edges, s, directed=True):
    adj = _c6_adj(n, edges, directed)
    INF = float("inf")
    dist = [INF] * n
    dist[s] = 0
    pq, order = [(0, s)], []
    while pq:
        d, u = _hq.heappop(pq)
        if d > dist[u]:
            continue
        order.append(u)
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                _hq.heappush(pq, (dist[v], v))
    return dist, order


def _c6_floyd(n, edges):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def _c6_dist_str(dist):
    return " ".join("∞" if x == float("inf") else str(x) for x in dist)


# ============================================================ topological sort

_TP_N = 6
_TP_E = [(0, 2), (1, 2), (2, 3), (1, 4), (4, 3), (3, 5)]


_H6_TOPO = dict(
    quizzes=[
        _quiz("bug", "The course plan 0→1, 1→2, 2→1 has a cycle, yet this prints an order. Which check is missing?",
              r"""
for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);
while (!q.isEmpty()) {
    int u = q.poll();
    order.add(u);
    for (int v : adj[u]) if (--indeg[v] == 0) q.add(v);
}
return order;
""",
              "`if (order.size() < n) return CYCLE;` before returning",
              ["`if (order.size() < n) return CYCLE;` before returning",
               "Start the queue with vertex 0 only",
               "Decrement `indeg[u]` as well",
               "Use a stack instead of a queue"],
              """
Vertices on (or behind) a cycle never reach in-degree 0, so Kahn silently leaves them out. The
output is only an order of *everything* if all n vertices came out. Stack or queue changes
which order, not whether one exists.
"""),
        _quiz("bug", "DFS-based ordering prints 2 0 1 for the rules 0→1, 1→2 — reversed. What is wrong?",
              r"""
void dfs(int u) {
    seen[u] = true;
    for (int v : adj[u]) if (!seen[v]) dfs(v);
    order.add(u);                      // post-order
}
// for every unseen v: dfs(v);  print order
""",
              "Post-order lists a vertex after its descendants; print it reversed",
              ["Post-order lists a vertex after its descendants; print it reversed",
               "Add `u` before the loop instead",
               "Sort `order` at the end",
               "Run the DFS on the reversed graph and print pre-order"],
              """
A vertex finishes after everything reachable from it, so post-order puts every vertex *after*
its descendants — the reverse of a topological order. (Pre-order is not a topological order:
0→2, 1→2 with DFS from 0 gives 0 2 1, placing 2 before 1.)
"""),
        _quiz("predict", "Kahn with a FIFO queue on 0→2, 1→2, 2→3, 1→4, 4→3, 3→5. What order comes out?",
              r"""
// initial queue in index order; neighbours in edge order
""",
              " ".join(map(str, _c6_kahn(_TP_N, _TP_E))),
              [" ".join(map(str, _c6_kahn(_TP_N, _TP_E))), "0 1 2 3 4 5", "1 0 4 2 3 5", "0 2 1 4 3 5"],
              """
Start with 0 and 1 (in-degree 0). Taking 0 frees nothing (2 still waits for 1); taking 1 frees
2 and 4; then 2 (3 still waits for 4), then 4 frees 3, then 5. \"0 1 2 3 4 5\" puts 3 before 4,
which breaks the rule 4→3.
"""),
        _quiz("predict", "How many different valid orders does the DAG 0→1, 0→2, 1→3, 2→3 have?",
              r"""
// count every permutation that respects all four rules
""",
              str(_c6_count_topo(4, [(0, 1), (0, 2), (1, 3), (2, 3)])),
              [str(_c6_count_topo(4, [(0, 1), (0, 2), (1, 3), (2, 3)])), "1", "4", "24"],
              """
0 must be first and 3 last; 1 and 2 can go in either order: 0 1 2 3 and 0 2 1 3. Kahn's queue
holds both 1 and 2 at once — the sign the order is not unique.
"""),
        _quiz("bug", "Counting routes 0 → t gives too small a number on some DAGs. Why?",
              r"""
long[] ways = new long[n];
ways[0] = 1;
for (int u = 0; u < n; u++)              // vertices in index order
    for (int v : adj[u]) ways[v] += ways[u];
""",
              "Index order is not a topological order; a vertex's count may be pushed before it is complete",
              ["Index order is not a topological order; a vertex's count may be pushed before it is complete",
               "ways[0] should start at 0",
               "It needs a modulo",
               "Edges should be relaxed from v to u"],
              """
If an edge 3 → 1 exists, vertex 1's count is pushed onward (when u = 1) before 3 has added to
it (when u = 3). Processing in topological order guarantees every incoming edge has delivered
before a vertex pushes. The modulo matters for overflow, not for this bug.
"""),
        _quiz("model", "Tasks have durations and \"x must finish before y starts\" rules; with unlimited workers, when does the project end?",
              """
durations: 3 2 4 1 5
rules: 0→2, 1→2, 2→3, 1→4, 4→3
""",
              "Longest path in a DAG — DP in topological order with max (the critical path)",
              ["Longest path in a DAG — DP in topological order with max (the critical path)",
               "Sum of all durations",
               "Dijkstra from the first task",
               "The number of Kahn layers"],
              """
A task starts when its last prerequisite ends, so finish[v] = dur[v] + max(finish[u]). The sum
assumes one worker; layers assume every duration is 1; Dijkstra minimises, and the project is
as long as its *longest* chain.
"""),
    ],
    stuck=[
        _stuck("“Before”, “after”, “depends on”, “prerequisite”",
               "Which direction is each edge? Write one rule as u → v and check it means \"u first\"."),
        _stuck("It asks whether all tasks can be done",
               "Is that \"is there a cycle?\" — Kahn outputs fewer than n vertices exactly when there is."),
        _stuck("It asks for a count, a longest chain or a total time",
               "Is it a DP whose dependencies are the edges? Then run it in topological order."),
        _stuck("The graph is not given, only examples of ordered data",
               "Which adjacent pair reveals one edge? (Sorted words: the first differing letter.)"),
        _stuck("It wants the smallest order, or asks whether the order is unique",
               "What is in Kahn's queue at each step — a heap for smallest, its width for uniqueness?"),
        _stuck("Recursion depth worries",
               "Kahn needs no recursion at all — prefer it over DFS ordering on 10⁵ vertices."),
    ],
    edge_cases=[
        _edge("semester-levels", "No rules", "3 0\n", "Leaving courses at semester 0."),
        _edge("semester-levels", "A long rule and a short rule into one course", "5 5\n0 1\n1 2\n2 3\n0 4\n3 4\n",
              "Taking the semester from the first prerequisite instead of the last."),
        _edge("semester-levels", "A repeated rule", "3 3\n0 1\n0 1\n1 2\n", "Decrementing in-degree once per distinct rule only."),
        _edge("unique-topo-order", "A cycle with a unique prefix", "4 4\n0 1\n1 2\n2 3\n3 2\n",
              "Reporting the partial order as unique instead of CYCLE."),
        _edge("unique-topo-order", "Two free tasks", "2 0\n", "Missing that the queue starts with width two."),
        _edge("dag-path-count", "Parallel slopes", "2 3\n0 1\n0 1\n0 1\n", "Deduplicating edges: each slope is a separate route."),
        _edge("dag-path-count", "Unreachable end", "4 2\n0 1\n2 3\n", "Counting routes from every source, not just 0."),
        _edge("dag-path-count", "Other sources feed the target", "5 5\n3 0\n3 4\n0 1\n1 4\n2 1\n",
              "Starting ways[] at 1 for every in-degree-0 station."),
        _edge("critical-path-time", "Short chain, long task", "4 2\n1 1 1 50\n0 1\n1 2\n",
              "Answering with the finish of the last task in the order instead of the maximum."),
        _edge("critical-path-time", "One task", "1 0\n10\n", "Returning 0 when nothing depends on anything."),
    ],
    walkthrough=_walk("critical-path-time", "The project's critical path", [
        """
n tasks with durations, and rules \"u before v\". Unlimited workers. How many days until the
whole project is done? n up to 10⁵.
""",
        """
\"u must finish before v starts\" with no cycles is a DAG — topological sort. The question is a
longest chain weighted by durations: DAG DP.
""",
        """
Simulate day by day: each day, start every task whose prerequisites are done; advance. With
durations up to 10⁴ and 10⁵ tasks, that is up to 10⁹ days of simulation. Or: repeat \"relax
every rule\" until nothing changes — O(n · m).
""",
        """
A task can start the moment its **last** prerequisite finishes:

start[v] = max over u → v of (start[u] + dur[u]).

That is a DP whose dependencies are exactly the edges, so it can be evaluated in any
topological order — and Kahn produces one while also making sure each start[v] has received
every incoming value before v is used. The answer is the largest start + duration.
""",
        """
```java
long best = 0;
while (!q.isEmpty()) {
    int u = q.poll();
    long fin = start[u] + dur[u];
    best = Math.max(best, fin);
    for (int v : adj[u]) {
        start[v] = Math.max(start[v], fin);
        if (--indeg[v] == 0) q.add(v);
    }
}
return best;
```
""",
        """
| Input | Expected | Catches |
| --- | --- | --- |
| one task | its duration | the empty-rule case |
| no rules | the longest task | parallelism |
| a chain | the sum | sequencing |
| short chain beside a long task | the long task | max, not the last finish |
| a diamond 5 → {1, 9} → 2 | 16 | max over prerequisites |

**Cost:** O(n + m) time and memory; `long` finish times (10⁵ · 10⁴ = 10⁹ fits an int only
barely, and sums of chains could exceed it in a variant).
""",
    ]),
    interview_script="""
### Say it out loud

- *"Rules become directed edges u → v meaning u first; then Kahn's algorithm: a queue of
  vertices with in-degree 0."*
- *"If fewer than n vertices come out, the rest are on or behind a cycle — that's my
  feasibility check."*
- *"The DP runs in topological order, so every vertex's value is complete before it is
  used — O(V + E)."*
- *"For the smallest order I'd swap the queue for a min-heap: O(V log V + E)."*
""",
    lab=_lab("graph", """
Directed graphs. Run **Kahn's algorithm** and watch the in-degree array and the queue: a
vertex enters the queue the moment its last prerequisite is taken, and a queue wider than one
means the order is not unique. Switch to **DFS** to see finish times — the reverse finish order
is also a topological order — and a back edge the moment there is a cycle.
""", [
        ("Course plan (Kahn)", {"n": 6, "edges": "0 2\n1 2\n2 3\n1 4\n4 3\n3 5", "directed": "yes", "source": 0, "algo": "kahn"}),
        ("Same plan, DFS finish times", {"n": 6, "edges": "0 2\n1 2\n2 3\n1 4\n4 3\n3 5", "directed": "yes", "source": 0, "algo": "dfs"}),
        ("A unique order", {"n": 5, "edges": "0 1\n1 2\n2 3\n3 4\n0 2", "directed": "yes", "source": 0, "algo": "kahn"}),
        ("A cycle blocks Kahn", {"n": 5, "edges": "0 1\n1 2\n2 3\n3 1\n3 4", "directed": "yes", "source": 0, "algo": "kahn"}),
        ("…and DFS finds the back edge", {"n": 5, "edges": "0 1\n1 2\n2 3\n3 1\n3 4", "directed": "yes", "source": 0, "algo": "dfs"}),
    ]),
    drills=[
        _calc("Kahn (FIFO, index order) on 0→2, 1→2, 2→3, 1→4, 4→3, 3→5 — the order?",
              " ".join(map(str, _c6_kahn(_TP_N, _TP_E))), "0 and 1 start free; 1 frees 2 and 4; 4 frees 3; 3 frees 5."),
        _calc("Semester of each course 0…5 for the same rules?",
              " ".join(map(str, _c6_semesters(_TP_N, _TP_E))),
              "0, 1: first semester; 2, 4: second; 3 waits for both: third; 5: fourth."),
        _calc("How many valid orders does 0→1, 0→2, 1→3, 2→3 have?",
              str(_c6_count_topo(4, [(0, 1), (0, 2), (1, 3), (2, 3)])), "1 and 2 can swap; 0 is first and 3 last."),
        _calc("How many valid orders do 4 tasks with no rules have?", "24", "Any permutation: 4! = 24."),
        _calc("Routes from 0 to 5 in 0→1, 0→2, 1→3, 2→3, 1→4, 3→4, 3→5, 4→5?",
              str(_c6_paths(6, [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (3, 4), (3, 5), (4, 5)], 0, 5)),
              "ways: 0:1, 1:1, 2:1, 3:2, 4:3, 5:5."),
        _calc("Critical path: durations 3 2 4 1 5, rules 0→2, 1→2, 2→3, 1→4, 4→3. Days?", "8",
              "2 finishes at 3 + 4 = 7; 4 finishes at 2 + 5 = 7; 3 starts at 7 and ends at 8."),
        _calc("Smallest-first order (min-heap) for 3→0, 2→0, 1→2?",
              " ".join(map(str, _c6_kahn(4, [(3, 0), (2, 0), (1, 2)], smallest=True))),
              "Free at the start: 1 and 3 → take 1; then 2 frees; take 2; then 3; then 0."),
        _calc("A DAG has 5 vertices in one chain plus 3 isolated vertices. How many Kahn layers (semesters)?", "5",
              "The chain needs 5 layers; the isolated vertices all sit in layer 1."),
    ],
)


# ============================================================ union-find

_UF_E = [(0, 1), (2, 3), (1, 3), (4, 5), (5, 4), (6, 5)]
_UF_PARENT, _UF_COMPS = _c6_dsu_trace(7, _UF_E)


_H6_UF = dict(
    quizzes=[
        _quiz("bug", "The component count is wrong whenever an edge joins two vertices already connected. Why?",
              r"""
int comps = n;
for (int[] e : edges) {
    union(e[0], e[1]);          // void union(...)
    comps--;
}
""",
              "Only decrement when the union actually merged two sets — make `union` return a boolean",
              ["Only decrement when the union actually merged two sets — make `union` return a boolean",
               "Start comps at n − 1",
               "Call find before union",
               "Union by size fixes it"],
              """
An edge inside one component merges nothing, so the count must not move. `union` returning
\"did I merge?\" is the idiom — it also detects the edge that closes a cycle.
"""),
        _quiz("bug", "This union makes find() slow — trees grow into long chains. What is wrong?",
              r"""
void union(int a, int b) {
    parent[a] = b;                      // link a under b
}
""",
              "It links the elements, not their roots: `parent[find(a)] = find(b)` (and link small under large)",
              ["It links the elements, not their roots: `parent[find(a)] = find(b)` (and link small under large)",
               "It should be `parent[b] = a`",
               "It needs path compression inside union",
               "Nothing — union is always O(1)"],
              """
Setting parent[a] overwrites a's link to its old root, splitting a's old set — a correctness
bug, not just a speed one. Link root to root, and hang the smaller tree under the larger to
keep heights logarithmic.
"""),
        _quiz("predict", "After these unions with union by size (ties: the second root goes under the first) and path compression, how many components remain on 7 elements?",
              """
union(0, 1); union(2, 3); union(1, 3); union(4, 5); union(5, 4); union(6, 5);
""",
              str(_UF_COMPS),
              [str(_UF_COMPS), "3", "1", "4"],
              """
{0, 1, 2, 3} and {4, 5, 6}. union(5, 4) finds them already joined and changes nothing — the
boolean return would be false there.
"""),
        _quiz("bug", "A weighted DSU (off[x] = value(x) − value(parent[x])) reports false contradictions once paths get longer than two. Which change fixes find?",
              r"""
int find(int x) {
    if (parent[x] == x) return x;
    off[x] += off[parent[x]];         // add the parent's offset…
    parent[x] = find(parent[x]);      // …then compress
    return parent[x];
}
""",
              "Compress the parent first, then add: `int p = parent[x]; parent[x] = find(p); off[x] += off[p];`",
              ["Compress the parent first, then add: `int p = parent[x]; parent[x] = find(p); off[x] += off[p];`",
               "Subtract off[parent[x]] instead of adding it",
               "Remove path compression — offsets cannot survive it",
               "Add off[x] to off[parent[x]] instead"],
              """
Before `find(parent[x])` runs, off[parent[x]] is relative to the parent's *old* parent, not to
the root — so x only picks up one level of offset. Compress the parent first; its offset is
then relative to the root, and adding it makes x's relative to the root too. Compression is
fine once the order is right.
"""),
        _quiz("model", "Accounts share e-mail addresses; merge accounts that share any address, transitively. Which model?",
              """
alice: a@x, b@x
bob:   c@x
alice: b@x, d@x
""",
              "Union-find over addresses (union each account's addresses together), then group by root",
              ["Union-find over addresses (union each account's addresses together), then group by root",
               "Sort the accounts by name",
               "Topological sort of the addresses",
               "Dijkstra between addresses"],
              """
\"Shares any address, transitively\" is connectivity; the groups are components. DSU builds them
in one pass over the address lists. Names cannot decide it — two different people can share a
name.
"""),
        _quiz("model", "Queries \"can a reach b using only roads rated for at least w tonnes?\" arrive for 10⁵ different w. Which approach?",
              """
n, m, q up to 1e5
edge: u v capacity      query: a b w
""",
              "Offline: sort queries by w descending, add edges by capacity as w drops, answer with find()",
              ["Offline: sort queries by w descending, add edges by capacity as w drops, answer with find()",
               "A BFS per query",
               "One Dijkstra from every vertex",
               "Union-find that deletes light edges per query"],
              """
A heavier truck may use a subset of the roads a lighter one may, so handling trucks from
heaviest to lightest only ever *adds* roads — which is exactly what union-find supports. A BFS
per query is O(q · (n + m)); DSU cannot delete.
"""),
    ],
    stuck=[
        _stuck("“Are these connected?” asked many times",
               "Is the graph only ever growing? Then union-find answers each question with two finds."),
        _stuck("Groups that merge by some rule (shared e-mail, same row, equal values)",
               "What is an element, and which pairs get unioned? The groups are the roots."),
        _stuck("It counts something after each addition",
               "Can each addition change the count by a fixed amount — +1 new, −1 per successful union?"),
        _stuck("Relations carry a number (\"3 more than\", \"opposite team\")",
               "Can each node store its offset to its parent, so two nodes in one set give their difference?"),
        _stuck("Queries involve removing edges or a threshold",
               "Can the queries be reordered so edges are only ever added? Sort them, and remember original positions."),
        _stuck("Is this an MST in disguise?",
               "Cheapest set of edges that connects everything → Kruskal, which is union-find over sorted edges."),
    ],
    edge_cases=[
        _edge("islands-after-each-add", "The same cell rises twice", "2 2 3\n1 1\n1 1\n0 0\n",
              "Counting a second island for a cell that is already land."),
        _edge("islands-after-each-add", "A ring closes on itself", "3 3 8\n0 0\n0 1\n0 2\n1 2\n2 2\n2 1\n2 0\n1 0\n",
              "Decrementing when both neighbours are already in one island."),
        _edge("islands-after-each-add", "The centre joins four islands", "3 3 5\n0 1\n1 0\n1 2\n2 1\n1 1\n",
              "Decrementing once per neighbour instead of once per distinct island."),
        _edge("height-claims", "A claim about one hilltop", "2 2\n0 1 3\n1 1 2\n",
              "Accepting h[1] − h[1] = 2."),
        _edge("height-claims", "The same claim reversed", "2 2\n0 1 6\n1 0 -6\n",
              "Flipping the sign of the offset when the roots are swapped."),
        _edge("first-odd-cycle", "A repeated rivalry", "2 3\n0 1\n1 0\n0 1\n",
              "Treating a repeated edge as a new cycle."),
        _edge("first-odd-cycle", "Three pairs joined into an even ring, then a chord", "6 7\n0 1\n2 3\n4 5\n1 2\n3 4\n5 0\n0 3\n",
              "Linking roots without the parity offset reports a false odd cycle — every cycle here is even (answer 0)."),
        _edge("limited-weight-reachability", "Capacity exactly the truck's weight", "2 1 2\n0 1 7\n0 1 7\n0 1 6\n",
              "Using `>=` where the statement needs `>`."),
        _edge("limited-weight-reachability", "Same island", "3 0 2\n0 1 1\n2 2 1\n",
              "Answering no for a trip that goes nowhere."),
    ],
    walkthrough=_walk("height-claims", "Which claim is the lie?", [
        """
Claims \"b is d higher than a\" arrive in order; find the first one that contradicts the ones
before it. Up to 2 · 10⁵ claims on 10⁵ hilltops.
""",
        """
Claims link hilltops into groups whose relative heights are fixed — a partition that only
grows, so union-find; and each link carries a number, so a **weighted** union-find.
""",
        """
After each claim, BFS the claims graph assigning heights, and look for a clash: O(q · (n + q))
— hopeless at 2 · 10⁵, and useful only as an oracle.
""",
        """
Store off[x] = h[x] − h[parent[x]]. After `find(x)` compresses x onto its root r, off[x]
becomes h[x] − h[r]. Then for a claim a b d:

- same root: the claim is consistent iff off[b] − off[a] = d;
- different roots ra, rb: hang rb under ra so that h[b] − h[a] = d, which needs
  off[rb] = off[a] + d − off[b].

The only delicate part is compression: when x is re-pointed at the root, off[x] must add its
parent's offset *after* the parent itself is relative to the root.
""",
        """
```java
int find(int x) {
    int root = x;
    while (parent[root] != root) root = parent[root];
    Deque<Integer> path = new ArrayDeque<>();
    for (int y = x; parent[y] != y; y = parent[y]) path.push(y);
    while (!path.isEmpty()) {                    // nearest the root first
        int y = path.pop();
        if (parent[y] != root) off[y] += off[parent[y]];
        parent[y] = root;
    }
    return root;
}
for (int i = 0; i < q; i++) {
    int ra = find(a[i]), rb = find(b[i]);
    if (ra == rb) { if (off[b[i]] - off[a[i]] != d[i]) return i + 1; }
    else { parent[rb] = ra; off[rb] = off[a[i]] + d[i] - off[b[i]]; }
}
return 0;
```
""",
        """
| Input | Expected | Catches |
| --- | --- | --- |
| `0 1 5 / 1 2 −3 / 0 2 2` | 0 | a consistent triangle |
| `0 1 4 / 1 2 4 / 2 0 −7` | 3 | a cycle that does not sum to 0 |
| `1 1 0` then `1 1 2` | 2 | self-claims |
| `0 1 6 / 1 0 −6` | 0 | the sign when roots are swapped |
| a 10⁵ chain | 0 | recursion depth in find |

**Cost:** O(q · α(n)) with union by size, O(q log n) with compression alone — either is fast.
""",
    ]),
    interview_script="""
### Say it out loud

- *"Connectivity that only grows is union-find: find with path compression, union by size —
  effectively O(1) each."*
- *"union returns whether it merged, so the component count and cycle detection come free."*
- *"Here each link carries a difference, so I store an offset to the parent and fix it up
  during compression."*
- *"Union-find can't delete, so I'll answer the queries offline in an order that only adds
  edges."*
""",
    lab=_lab("graph", """
Run **union-find** over an edge list: one row per union, with the parent and size arrays after
it. Watch a smaller tree hang under a larger one, an edge inside one set come back `false`
(that edge closes a cycle), and the component count fall. Then run **Kruskal** on a weighted
list — union-find deciding which edges to keep.
""", [
        ("Components", {"n": 7, "edges": "0 1\n2 3\n1 3\n4 5\n5 4\n6 5", "directed": "no", "source": 0, "algo": "dsu"}),
        ("A cycle-closing edge", {"n": 4, "edges": "0 1\n1 2\n2 3\n3 0", "directed": "no", "source": 0, "algo": "dsu"}),
        ("Union by size keeps it flat", {"n": 8, "edges": "0 1\n2 3\n0 2\n4 5\n6 7\n4 6\n0 4", "directed": "no", "source": 0, "algo": "dsu"}),
        ("Kruskal is union-find", {"n": 5, "edges": "0 1 4\n1 2 2\n2 3 7\n0 2 3\n1 3 9\n3 4 1", "directed": "no", "source": 0, "algo": "kruskal"}),
    ]),
    drills=[
        _calc("Union by size (ties: second root under the first), with compression, on 7 elements: union(0,1), (2,3), (1,3), (4,5), (5,4), (6,5). Final parent[]?",
              " ".join(map(str, _UF_PARENT)),
              "0 roots {0,1}; 2 roots {2,3}; union(1,3) hangs root 2 under 0 — 3 still points at 2, since no find has "
              "walked through it since; 4 roots {4,5}; union(5,4) does nothing; 6 goes under the larger root 4."),
        _calc("How many components after those unions?", str(_UF_COMPS), "{0, 1, 2, 3} and {4, 5, 6}."),
        _calc("n = 10 elements, 7 successful unions. How many components?", "3", "Each successful union removes one: 10 − 7."),
        _calc("A graph with 6 vertices and 8 edges is connected. How many edges close a cycle when unioned in any order?",
              "3", "A spanning tree uses 5 edges; the other 8 − 5 = 3 each find their ends already connected."),
        _calc("Weighted DSU: off[a] = 2, off[b] = 7 (both relative to the same root). What is h[b] − h[a]?",
              "5", "h[b] − h[a] = (off[b] + h[root]) − (off[a] + h[root]) = 7 − 2."),
        _calc("Claims h1 − h0 = 5, h2 − h1 = −3. What must h2 − h0 be?", "2", "5 + (−3)."),
        _calc("Parity DSU: par[u] = 1, par[v] = 0, different roots. After linking rv under ru for the rivalry u–v, what is par[rv]?",
              "0", "par[rv] = par[u] ^ par[v] ^ 1 = 1 ^ 0 ^ 1 = 0."),
        _calc("Make-network-connected: 6 computers, 5 cables, 2 components. Is it possible? (yes / no)", "yes",
              "Needed: components − 1 = 1 cable. Spare: 5 − (6 − 2) = 1. Enough."),
    ],
)


# ============================================================ MST

_M_N = 5
_M_E = [(0, 1, 4), (1, 2, 2), (2, 3, 7), (0, 2, 3), (1, 3, 9), (3, 4, 1)]
_M_TOTAL, _M_TAKEN = _c6_kruskal(_M_N, _M_E)


_H6_MST = dict(
    quizzes=[
        _quiz("bug", "Kruskal returns a total for a graph that is not connected. What check is missing?",
              r"""
long total = 0;
for (int[] e : sortedEdges)
    if (union(e[0], e[1])) total += e[2];
return total;
""",
              "Count the successful unions and return −1 unless there were n − 1",
              ["Count the successful unions and return −1 unless there were n − 1",
               "Sort in descending order",
               "Also add the rejected edges",
               "Start total at the smallest weight"],
              """
On a disconnected graph Kruskal happily builds a spanning *forest* and returns its weight. A
spanning tree has exactly n − 1 edges; fewer means some vertex was never reached.
"""),
        _quiz("bug", "Lazy Prim adds some vertices twice and the total is too large. What is missing?",
              r"""
pq.add(new int[]{0, 0});                       // {weight, vertex}
while (!pq.isEmpty()) {
    int[] t = pq.poll();
    total += t[0];
    inTree[t[1]] = true;
    for (int[] e : adj[t[1]]) if (!inTree[e[0]]) pq.add(new int[]{e[1], e[0]});
}
""",
              "`if (inTree[t[1]]) continue;` right after polling",
              ["`if (inTree[t[1]]) continue;` right after polling",
               "Use a max-heap",
               "Mark inTree when pushing instead",
               "Add total only for the first edge"],
              """
The heap can hold several entries for one vertex (one per tree neighbour). Only the first one
popped — the cheapest — joins the tree; the rest are stale and must be skipped. Marking on push
would lock a vertex to the first, possibly expensive, edge seen.
"""),
        _quiz("predict", "Kruskal on 0-1 (4), 1-2 (2), 2-3 (7), 0-2 (3), 1-3 (9), 3-4 (1). Total weight?",
              r"""
// sort by weight; take an edge iff its ends are in different sets
""",
              str(_M_TOTAL),
              [str(_M_TOTAL), "17", "10", "26"],
              """
Sorted: 3-4 (1) take, 1-2 (2) take, 0-2 (3) take, 0-1 (4) skip — 0 and 1 are already joined
through 2 — then 2-3 (7) take. 1 + 2 + 3 + 7 = 13.
"""),
        _quiz("predict", "In that MST, what is the heaviest edge on the tree path from 1 to 4 — the smallest possible \"steepest step\" between them?",
              r"""
// MST edges: 3-4 (1), 1-2 (2), 0-2 (3), 2-3 (7)
""",
              "7",
              ["7", "9", "2", "4"],
              """
The tree path is 1 → 2 → 3 → 4 with weights 2, 7, 1, so its heaviest edge is 7. The direct
edge 1-3 weighs 9, and 0-1 (4) does not help. No route between 1 and 4 in the original graph
has a smaller maximum — the MST path is the minimax path.
"""),
        _quiz("model", "Villages can each dig a well (cost w[i]) or pipe water from a neighbour (cost p[i][j]). Cheapest way to water every village?",
              """
wells: 5 8 9 3
pipes: 0-1 2, 1-2 3, 2-3 6, 0-3 7
""",
              "Add a virtual source joined to each village by an edge of cost w[i]; the answer is the MST",
              ["Add a virtual source joined to each village by an edge of cost w[i]; the answer is the MST",
               "Dig the cheapest well, then an MST of the pipes",
               "Dijkstra from the cheapest well",
               "Take every well whose cost beats its cheapest pipe"],
              """
A well is a pipe from an imaginary reservoir. Then every valid plan is a spanning tree of n + 1
vertices and the cheapest is the MST. One cheapest well is wrong when two cheap wells beat a
long pipe; the local rule ignores how pipes combine.
"""),
        _quiz("model", "Minimise the steepest single climb on a route from hut a to hut b; 10⁴ queries.",
              """
trails: u v climb   (undirected)
queries: a b
""",
              "Build the MST once; each answer is the largest edge on the MST path between a and b",
              ["Build the MST once; each answer is the largest edge on the MST path between a and b",
               "Dijkstra per query, summing climbs",
               "BFS per query",
               "Floyd–Warshall with sums"],
              """
The MST path minimises the maximum edge between any two vertices (the cycle property). Summing
answers a different question; BFS ignores weights.
"""),
    ],
    stuck=[
        _stuck("“Connect all … at minimum total cost”",
               "Is it a spanning tree — every vertex joined, no need for a particular route? Then Kruskal or Prim."),
        _stuck("Each vertex can also be served on its own (a well, a generator, a free server)",
               "Can that option be an edge to an invented vertex?"),
        _stuck("The graph is implicit — points in the plane, every pair connected",
               "V² edges: is dense Prim (O(V²), no edge list) better than sorting them for Kruskal?"),
        _stuck("A question about one edge — must it be used, can it be used?",
               "What happens to the MST weight if you force it (union first) or forbid it (skip it)?"),
        _stuck("It minimises the largest edge, not the sum",
               "Is the answer the MST path — or \"the first Kruskal edge that connects them\"?"),
        _stuck("Kruskal or Prim?",
               "Do you have an edge list (Kruskal) or adjacency lists / a formula for weights (Prim)?"),
    ],
    edge_cases=[
        _edge("cheapest-road-network", "One village", "1 0\n", "Returning −1 because zero edges were taken."),
        _edge("cheapest-road-network", "A self-road", "2 2\n0 0 1\n0 1 8\n", "Counting a loop as a connection."),
        _edge("cheapest-road-network", "Disconnected", "3 1\n0 1 5\n", "Returning 5 for a forest."),
        _edge("cheapest-road-network", "Parallel roads", "2 3\n0 1 9\n1 0 4\n0 1 6\n", "Taking the first road instead of the cheapest."),
        _edge("power-grid-generators", "Generators beat every cable", "3 1\n1 1 1\n0 1 5\n",
              "Forcing at least one cable."),
        _edge("power-grid-generators", "One town", "1 0\n42\n", "Forgetting that a lone town still needs a generator."),
        _edge("mst-forced-edge", "The forced road is already in the MST", "4 5 1\n0 1 1\n1 2 2\n2 3 3\n3 0 4\n0 2 10\n",
              "Adding its weight twice."),
        _edge("mst-forced-edge", "Two towns, the dear road forced", "2 3 2\n0 1 1\n0 1 9\n1 0 4\n",
              "Letting the cheaper parallel road in as well."),
        _edge("bottleneck-route", "A hut to itself", "1 0 1\n0 0\n", "Returning −1 instead of 0."),
        _edge("bottleneck-route", "The long gentle way round", "4 4 2\n0 3 50\n0 1 10\n1 2 10\n2 3 10\n0 3\n3 1\n",
              "Taking the direct trail because it is one hop."),
    ],
    walkthrough=_walk("power-grid-generators", "Generators or cables", [
        """
Each town can build a generator (cost g[i]) or be cabled to a powered town (cost w per
cable). Minimum total so every town has power.
""",
        """
\"Everything connected, cheapest total\" is a spanning-tree question — MST. The per-town option
is the twist.
""",
        """
Try every subset of towns to hold generators; for each, contract those towns together and take
an MST of the rest. 2ⁿ subsets — only for n ≤ 15, as an oracle.
""",
        """
Invent town n, \"the grid\". Building a generator in town i is exactly a cable from n to i
costing g[i]: power reaches i from the grid either way. Now a valid plan is any set of edges
connecting all n + 1 towns, and the cheapest is the MST of the augmented graph. It must contain
at least one generator edge, because node n must be connected.
""",
        """
```java
int[][] all = new int[edges.length + n][];
for (int i = 0; i < edges.length; i++) all[i] = edges[i];
for (int i = 0; i < n; i++) all[edges.length + i] = new int[]{n, i, g[i]};
Arrays.sort(all, (p, q) -> Integer.compare(p[2], q[2]));
long total = 0;
for (int[] e : all) if (union(e[0], e[1])) total += e[2];      // DSU of size n + 1
return total;
```
""",
        """
| Input | Expected | Catches |
| --- | --- | --- |
| one town, cost 42 | 42 | a lone town still needs power |
| cheap cables, dear generators | one generator + cables | the virtual edge is taken once |
| cheap generators | all generators | cables are optional |
| generators at both ends of a long line | 2 + cables | two generators can beat a long cable |

**Cost:** Kruskal over m + n edges: O((m + n) log(m + n)).
""",
    ]),
    interview_script="""
### Say it out loud

- *"Connect everything at minimum total cost is an MST; I'll use Kruskal: sort edges, take an
  edge if union() says its ends were apart."*
- *"It's correct by the cut property: the cheapest edge across any cut is in some MST."*
- *"The per-node cost becomes an edge to a virtual node, so it's still just an MST."*
- *"O(E log E) for the sort; for a complete graph of points I'd use the O(V²) array Prim."*
""",
    lab=_lab("graph", """
Weighted, undirected graphs. Run **Kruskal** to watch edges come off the sorted list and be
taken or skipped (skipped means the ends were already connected — the edge would close a
cycle); run **Prim** from the source to watch one tree grow by its cheapest outgoing link.
Both end at the same weight.
""", [
        ("Kruskal", {"n": 5, "edges": "0 1 4\n1 2 2\n2 3 7\n0 2 3\n1 3 9\n3 4 1", "directed": "no", "source": 0, "algo": "kruskal"}),
        ("Prim, same graph", {"n": 5, "edges": "0 1 4\n1 2 2\n2 3 7\n0 2 3\n1 3 9\n3 4 1", "directed": "no", "source": 0, "algo": "prim"}),
        ("Virtual power station (node 4)", {"n": 5, "edges": "0 1 2\n1 2 3\n2 3 6\n0 3 7\n4 0 5\n4 1 8\n4 2 9\n4 3 3", "directed": "no", "source": 4, "algo": "kruskal"}),
        ("Not connected", {"n": 5, "edges": "0 1 1\n1 2 2\n3 4 3", "directed": "no", "source": 0, "algo": "kruskal"}),
        ("Ties", {"n": 4, "edges": "0 1 5\n1 2 5\n2 3 5\n3 0 5\n0 2 5", "directed": "no", "source": 0, "algo": "kruskal"}),
    ]),
    drills=[
        _calc("Kruskal on 0-1 (4), 1-2 (2), 2-3 (7), 0-2 (3), 1-3 (9), 3-4 (1). MST weight?", str(_M_TOTAL),
              "Take 3-4, 1-2, 0-2, skip 0-1, take 2-3."),
        _calc("Which edge of that graph is the first one Kruskal skips? (u-v)", "0-1",
              "After 3-4, 1-2 and 0-2, vertices 0 and 1 are already joined through 2.", accept=["0 1", "1-0"]),
        _calc("Prim from 0 on the same graph: order in which vertices join the tree?",
              " ".join(map(str, _c6_prim_order(_M_N, _M_E, 0))),
              "0; then 2 (3); then 1 (2); then 3 (7 via 2); then 4 (1)."),
        _calc("How many edges does a spanning tree of 12 vertices have?", "11", "n − 1."),
        _calc("A complete graph on 1000 points: how many edges would Kruskal have to sort?", "499500",
              "1000 · 999 / 2 = 499,500 — why dense Prim, at O(V²) with no edge list, wins there.", accept=["499,500"]),
        _calc("Generators 5 8 9 3, cables 0-1 (2), 1-2 (3), 2-3 (6), 0-3 (7). Minimum cost?",
              str(_c6_kruskal(5, [(0, 1, 2), (1, 2, 3), (2, 3, 6), (0, 3, 7), (4, 0, 5), (4, 1, 8), (4, 2, 9), (4, 3, 3)])[0]),
              "Virtual node 4: take 0-1 (2), 1-2 (3), 4-3 (3), 4-0 (5)."),
        _calc("In that weighted graph (0-1 4, 1-2 2, 2-3 7, 0-2 3, 1-3 9, 3-4 1), what is the smallest possible steepest edge on a route from 0 to 4?",
              "7", "The MST path 0 → 2 → 3 → 4 uses 3, 7, 1: the bottleneck is 7."),
        _calc("Forced edge 1-3 (9) in the same graph: MST weight including it?",
              str(9 + _c6_kruskal(5, [(1, 3, 0)] + [e for e in _M_E if (e[0], e[1]) != (1, 3)])[0]),
              "Contract 1-3 (9); then 3-4 (1), 1-2 (2), 0-2 (3): 15."),
    ],
)


# ============================================================ shortest paths

_S_N = 4
_S_E = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
_S_DIST, _S_ORDER = _c6_dijkstra(_S_N, _S_E, 0)


_H6_SP = dict(
    quizzes=[
        _quiz("bug", "Dijkstra gives the right distances but runs far too slowly on large graphs. What is missing?",
              r"""
while (!pq.isEmpty()) {
    long[] t = pq.poll();
    int u = (int) t[1];
    for (int[] e : adj[u])
        if (t[0] + e[1] < dist[e[0]]) { dist[e[0]] = t[0] + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
}
""",
              "`if (t[0] > dist[u]) continue;` — skip stale entries",
              ["`if (t[0] > dist[u]) continue;` — skip stale entries",
               "Use a max-heap",
               "Mark vertices visited when pushed",
               "Initialise dist to 0"],
              """
Without the stale check, every out-of-date copy of a vertex re-relaxes all its edges. The
distances end up right (only improvements are written), but the work can blow up. Marking on
push would be wrong: a vertex's first tentative distance is not necessarily its final one.
"""),
        _quiz("bug", "Distances come out as large negative numbers on a graph with unreachable vertices. Why?",
              r"""
int INF = Integer.MAX_VALUE;
int[] dist = new int[n]; Arrays.fill(dist, INF);
// ... relax: if (dist[u] + w < dist[v]) dist[v] = dist[u] + w;
""",
              "`INF + w` overflows to a negative number; use long and INF = Long.MAX_VALUE / 4 (or skip INF sources)",
              ["`INF + w` overflows to a negative number; use long and INF = Long.MAX_VALUE / 4 (or skip INF sources)",
               "Arrays.fill does not work on int arrays",
               "Unreachable vertices must be removed first",
               "The comparison should be `<=`"],
              """
Integer.MAX_VALUE + 1 wraps to Integer.MIN_VALUE, which then looks like a fantastically short
path. Leave headroom in the infinity, and use long for sums anyway.
"""),
        _quiz("predict", "Dijkstra from 0 on 0→1 (4), 0→2 (1), 2→1 (2), 1→3 (1), 2→3 (5). Final dist[]?",
              r"""
// directed; lazy deletion; ties broken by vertex number
""",
              _c6_dist_str(_S_DIST),
              [_c6_dist_str(_S_DIST), "0 4 1 5", "0 3 1 6", "0 4 1 6"],
              """
0 settles at 0; 2 at 1 (relaxing 1 to 3 and 3 to 6); 1 at 3 (relaxing 3 to 4); 3 at 4. The
direct 0→1 edge of 4 is beaten by 0→2→1 = 3.
"""),
        _quiz("bug", "Floyd–Warshall returns distances that are too large on some graphs. What is wrong?",
              r"""
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        for (int k = 0; k < n; k++)
            d[i][j] = Math.min(d[i][j], d[i][k] + d[k][j]);
""",
              "The intermediate vertex k must be the OUTER loop",
              ["The intermediate vertex k must be the OUTER loop",
               "It needs `<=` in the min",
               "d[i][i] must start at infinity",
               "It must run n times"],
              """
With k outermost, after iteration k every pair has its best path using intermediates {0..k}.
With k innermost, d[i][j] is finalised before d[i][k] and d[k][j] have been improved — so
paths needing several intermediates are missed.
"""),
        _quiz("model", "Flights with prices; find the cheapest route from A to B using at most k stops.",
              """
flights: u v price      (directed)
k = 2
""",
              "Bellman-Ford limited to k + 1 rounds (copying dist each round), or Dijkstra over (city, stops) states",
              ["Bellman-Ford limited to k + 1 rounds (copying dist each round), or Dijkstra over (city, stops) states",
               "Plain Dijkstra, then check the stop count",
               "BFS on the number of stops",
               "Kruskal on the prices"],
              """
The cheapest route overall may use too many stops, and plain Dijkstra keeps only the cheapest
arrival per city. Round k of Bellman-Ford is exactly \"best with at most k edges\" — as long as
each round reads the previous round's copy.
"""),
        _quiz("model", "Every house needs its distance to the nearest fire station along weighted roads.",
              """
roads: u v minutes
stations: 3 17 42
""",
              "One Dijkstra with every station in the heap at distance 0",
              ["One Dijkstra with every station in the heap at distance 0",
               "One Dijkstra per station, then the minimum",
               "BFS from every house",
               "Floyd–Warshall, then scan"],
              """
Multi-source Dijkstra: a virtual source with 0-length roads to every station. One run instead of
one per station; Floyd is O(V³) for a question with one answer per vertex.
"""),
    ],
    stuck=[
        _stuck("Weights, and “cheapest / fastest / shortest”",
               "Are the weights all equal (BFS), 0 or 1 (0-1 BFS), non-negative (Dijkstra) or possibly negative (Bellman-Ford)?"),
        _stuck("A limit on something besides the distance — stops, fuel, coupons",
               "Can that limit go into the state: (vertex, stops used)?"),
        _stuck("Many sources, or the nearest of several targets",
               "Can all sources start in the heap at 0? Or can you run from the target on the reversed graph?"),
        _stuck("It asks for the route, not just the length",
               "Record parent[] on each relaxation — or walk tight edges using distances from the target."),
        _stuck("It maximises something along the path (capacity, probability)",
               "Does extending a path never make it better? Then Dijkstra with a different combine (min, ×) and a max-heap."),
        _stuck("Every pair of vertices",
               "Is V small enough for O(V³) Floyd–Warshall (≈ 400), or do you need V runs of Dijkstra?"),
    ],
    edge_cases=[
        _edge("dijkstra-path-print", "Unreachable", "3 1\n0 1 7\n", "Printing a route to a vertex never reached."),
        _edge("dijkstra-path-print", "A tie decided at the second junction", "4 4\n0 2 1\n0 1 1\n1 3 1\n2 3 1\n",
              "Taking the first-discovered route instead of the smallest sequence."),
        _edge("dijkstra-path-print", "Parallel roads", "3 4\n0 1 5\n0 1 2\n1 2 2\n0 2 9\n",
              "Keeping only the first road between two junctions."),
        _edge("nearest-hospital", "Every town a hospital", "3 2 3\n0 1 5\n1 2 5\n2 0 1\n", "Anything but all zeros."),
        _edge("nearest-hospital", "Unreachable towns", "4 1 1\n0 1 3\n3\n", "Printing a huge number instead of −1."),
        _edge("negative-cycle-detect", "A zero-weight cycle", "3 3\n0 1 4\n1 2 -1\n2 0 -3\n", "Treating ≤ 0 as negative."),
        _edge("negative-cycle-detect", "A cycle unreachable from 0", "5 3\n0 1 2\n3 4 -2\n4 3 1\n",
              "Starting only vertex 0 at distance 0."),
        _edge("negative-cycle-detect", "A negative self-loop", "2 2\n0 1 1\n1 1 -1\n", "Ignoring loops."),
        _edge("widest-path", "Parallel pipes", "2 3\n0 1 3\n0 1 7\n0 1 5\n", "Keeping the first pipe instead of the widest."),
        _edge("widest-path", "The long wide way", "4 4\n0 3 1\n0 1 9\n1 2 9\n2 3 9\n", "Preferring fewer pipes."),
        _edge("second-shortest-path", "Only one road", "2 1\n0 1 4\n", "Returning −1 — bouncing back and forth gives 12."),
        _edge("second-shortest-path", "Two equal shortest routes", "4 4\n0 1 1\n1 3 1\n0 2 1\n2 3 1\n",
              "Returning the tie as the second shortest."),
    ],
    walkthrough=_walk("second-shortest-path", "The runner-up route", [
        """
Roads with travel times; find the smallest route length from 0 to n − 1 that is strictly
greater than the shortest. Routes may revisit junctions. n up to 10⁴, m up to 5 · 10⁴.
""",
        """
Weighted, non-negative, \"shortest-something\" — Dijkstra territory (shortest paths). The twist,
\"second best\", is a state question: keep more than one distance per vertex.
""",
        """
Remove each edge of the shortest path in turn and rerun Dijkstra, taking the best result.
That misses routes that *revisit* (the bounce 0 → 1 → 0 → 1 on a single road), and costs one
Dijkstra per edge. Better as a cross-check than as a solution.
""",
        """
Give each vertex two slots: best and second (strictly larger). A popped (d, u) relaxes each
edge to v with nd = d + w:

- nd < best[v]: the old best becomes second, nd becomes best;
- best[v] < nd < second[v]: nd becomes second;
- otherwise nothing.

Push on every improvement. The second-best route to v extends the best or second-best route to
some neighbour, so both slots are found by the same greedy argument as Dijkstra's — and each
vertex is expanded at most twice.
""",
        """
```java
best[0] = 0; pq.add(new long[]{0, 0});
while (!pq.isEmpty()) {
    long[] t = pq.poll();
    int u = (int) t[1];
    long d = t[0];
    if (d > second[u]) continue;
    for (int[] e : adj[u]) {
        long nd = d + e[1];
        int v = e[0];
        if (nd < best[v]) { second[v] = best[v]; best[v] = nd; pq.add(new long[]{nd, v}); }
        else if (nd > best[v] && nd < second[v]) { second[v] = nd; pq.add(new long[]{nd, v}); }
    }
}
return second[n - 1] == INF ? -1 : second[n - 1];
```
""",
        """
| Input | Expected | Catches |
| --- | --- | --- |
| one road of 4 | 12 | revisits are allowed |
| two equal shortest routes | shortest + 2 | ties are not the runner-up |
| unreachable | −1 | the INF check |
| parallel roads 5, 6, 5 | 6 | a strictly larger parallel road |

**Cost:** O((V + E) log V) — at most two expansions per vertex.
""",
    ]),
    interview_script="""
### Say it out loud

- *"Non-negative weights, so Dijkstra with a binary heap. Java's PriorityQueue has no
  decrease-key, so I push duplicates and skip stale entries when popping."*
- *"Distances are long, with infinity well below Long.MAX_VALUE so adding a weight can't
  wrap."*
- *"If weights could be negative I'd switch to Bellman-Ford — and a change in round n means a
  negative cycle."*
- *"O((V + E) log V); for all pairs on a small graph, Floyd–Warshall in O(V³) with k as the
  outer loop."*
""",
    lab=_lab("graph", """
Weighted graphs. Run **Dijkstra** and scrub through the pops: the heap (including stale copies
that get skipped), the distances, and the shortest-path tree in colour. Run **Bellman-Ford** to
see rounds of relaxation — and, on a graph with a negative cycle, the round that still
improves. Try Dijkstra on the negative-edge preset to see why it is not allowed.
""", [
        ("Dijkstra", {"n": 4, "edges": "0 1 4\n0 2 1\n2 1 2\n1 3 1\n2 3 5", "directed": "yes", "source": 0, "algo": "dijkstra"}),
        ("Dijkstra, undirected", {"n": 6, "edges": "0 1 7\n0 2 9\n0 5 14\n1 2 10\n1 3 15\n2 3 11\n2 5 2\n3 4 6\n4 5 9", "directed": "no", "source": 0, "algo": "dijkstra"}),
        ("Bellman-Ford rounds", {"n": 5, "edges": "0 1 6\n0 2 7\n1 2 8\n1 3 5\n1 4 -4\n2 3 -3\n2 4 9\n3 1 -2\n4 3 7", "directed": "yes", "source": 0, "algo": "bellman"}),
        ("A negative cycle", {"n": 4, "edges": "0 1 3\n1 2 -2\n2 3 2\n3 1 -1", "directed": "yes", "source": 0, "algo": "bellman"}),
        ("Why Dijkstra needs w ≥ 0", {"n": 4, "edges": "0 1 1\n0 2 5\n2 1 -10\n1 3 1", "directed": "yes", "source": 0, "algo": "dijkstra"}),
        ("BFS is Dijkstra with w = 1", {"n": 6, "edges": "0 1\n0 2\n1 3\n2 3\n3 4\n4 5", "directed": "no", "source": 0, "algo": "bfs"}),
    ]),
    drills=[
        _calc("Dijkstra from 0 on 0→1 (4), 0→2 (1), 2→1 (2), 1→3 (1), 2→3 (5): final dist[]?",
              _c6_dist_str(_S_DIST), "0 → 2 → 1 → 3 is the shortest route to 3."),
        _calc("In what order are vertices settled (popped fresh) in that run?", " ".join(map(str, _S_ORDER)),
              "By final distance: 0 (0), 2 (1), 1 (3), 3 (4)."),
        _calc("Bellman-Ford needs at most how many rounds on a graph of 50 vertices without negative cycles?", "49",
              "A shortest path has at most V − 1 edges."),
        _calc("Floyd–Warshall on 0→1 (3), 1→2 (−2), 0→2 (4), 2→0 (1): what is d[1][0]?",
              str(_c6_floyd(3, [(0, 1, 3), (1, 2, -2), (0, 2, 4), (2, 0, 1)])[1][0]),
              "1 → 2 → 0 = −2 + 1 = −1."),
        _calc("0-1 BFS: an edge of weight 0 goes to which end of the deque? (front / back)", "front",
              "It does not increase the distance, so it belongs with the current layer."),
        _calc("Widest path: pipes 0-1 (5), 1-2 (8), 2-3 (6), 3-4 (4), 1-4 (3), 0-2 (4). Best capacity 0 → 4?", "4",
              "0 → 1 → 2 → 3 → 4 has narrowest pipe 4; the direct route through 1-4 is capped at 3."),
        _calc("Second shortest from 0 to 3: roads 0-1 (2), 1-3 (3), 0-2 (3), 2-3 (3), 1-2 (1). Length?", "6",
              "Shortest 0-1-3 = 5; next 0-2-3 = 6 (0-1-2-3 is 6 as well)."),
        _calc("A path of 10⁵ edges each weighing 10⁹: what is the largest distance, as a power of ten?", "10^14",
              "10⁵ · 10⁹ — far past int's 2.1 · 10⁹, so distances are long.", accept=["1e14", "100000000000000", "10¹⁴"]),
    ],
)


# ============================================================ the cheat sheet

_S6_CHEATSHEET = r"""
### Templates

```java
// Trees
int f(TreeNode n) { if (n == null) return BASE; int l = f(n.left), r = f(n.right); return combine(n, l, r); }
for (int size = q.size(); size-- > 0; ) { TreeNode n = q.poll(); /* children */ }   // one level
boolean valid(TreeNode n, long lo, long hi)                                           // BST bounds

// Backtracking
void dfs(int start) { record(copy(path)); for (int i = start; i < n; i++) { path.add(a[i]); dfs(i + 1); path.remove(path.size() - 1); } }
if (i > start && a[i] == a[i - 1]) continue;     // duplicates at one depth
if (a[i] > rem) break;                           // sorted input

// Graphs
dist[s] = 0; q.add(s); while (!q.isEmpty()) { int u = q.poll(); for (int v : adj[u]) if (dist[v] < 0) { dist[v] = dist[u] + 1; q.add(v); } }
for (v) if (indeg[v] == 0) q.add(v);  … if (--indeg[v] == 0) q.add(v);  // Kahn; order.size() < n → cycle
int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }       // DSU (halving)
for (int[] e : sortedByW) if (union(e[0], e[1])) total += e[2];          // Kruskal
if (t[0] > dist[u]) continue;                                             // Dijkstra: skip stale
for (k) for (i) for (j) d[i][j] = min(d[i][j], d[i][k] + d[k][j]);       // Floyd: k OUTER
```

### The eight bugs that fail hidden tests

1. A leaf is `left == null && right == null` — not `n == null`.
2. `q.size()` read inside the level loop instead of once before it.
3. BST validation by comparing children only — carry (lo, hi), in `long`.
4. `result.add(path)` instead of a copy; an `apply` without its mirror `undo`.
5. BFS marking on pop — duplicates flood the queue; a visited set per cell when the state needs more.
6. Two-colour visited for cycles in a *directed* graph — use grey/black.
7. `union` without a boolean; Kruskal without checking n − 1 edges.
8. Dijkstra with a negative edge, an `int` infinity that overflows, or no stale-entry check.

### Costs to quote

| | Time | Space |
| --- | --- | --- |
| Tree traversal / tree DP | O(n) | O(h) stack |
| BST search / insert / delete | O(h) | O(1)–O(h) |
| Subsets / permutations | O(2ⁿ · n) / O(n! · n) | O(n) |
| BFS / DFS | O(V + E) | O(V) |
| Kahn / DAG DP | O(V + E) | O(V) |
| Union-find, m operations | O(m · α(n)) | O(n) |
| Kruskal / Prim (heap) / Prim (array) | O(E log E) / O(E log V) / O(V²) | O(V + E) |
| Dijkstra / Bellman-Ford / Floyd | O((V + E) log V) / O(V · E) / O(V³) | O(V + E) / O(V) / O(V²) |
"""


def _attach_s6_help():
    by_key = {u["key"]: u for u in _UNITS}
    for key, h in {
        "trees": _H6_TREES, "bst": _H6_BST, "backtracking": _H6_BACKTRACK,
        "graph-traversal": _H6_GRAPH, "topological-sort": _H6_TOPO, "union-find": _H6_UF,
        "mst": _H6_MST, "shortest-paths": _H6_SP,
    }.items():
        u = by_key[key]
        u["quizzes"].extend(h["quizzes"])
        u["stuck"].extend(h["stuck"])
        u["edge_cases"].extend(h["edge_cases"])
        u["walkthrough"] = h["walkthrough"]
        u["interview"] = u["interview"].rstrip() + "\n\n" + _md(h["interview_script"])
        u["lab"] = h["lab"]
        u["drills"].extend(h["drills"])
    for st in _STAGES:
        if st["key"] == "hierarchies":
            st["cheatsheet"] = _md(_S6_CHEATSHEET)


_attach_s6_help()
