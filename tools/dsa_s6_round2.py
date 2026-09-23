# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 (Trees & Graphs) — round 2 of the expansion (TREES_GRAPHS_ROADMAP.md).
#
# exec'd by tools/dsa_curriculum.py after dsa_s6_help2.py, reusing its `_t6_*`
# and `_c6_*` helpers. Adds, by unit key:
#
#   followups   the interviewer's "what if…?" twists (see `_follow`)
#   traces      one more computed trace for four of the graph units
#   quizzes     two more per unit
#   drills      work-it-out cards up to ten per unit (answers computed)
#   lab presets the new tree annotations / graph algorithms, and a maze lab as
#               graph traversal's second lab (`extra_labs`)
# ---------------------------------------------------------------------------


# ============================================================ computed traces

def _t6_multi_bfs():
    rows_in = ["S...#", ".##..", "...#S", "#...."]
    R, C = len(rows_in), len(rows_in[0])
    dist = [[-1] * C for _ in range(R)]
    q = []
    for i in range(R):
        for j in range(C):
            if rows_in[i][j] == "S":
                dist[i][j] = 0
                q.append((i, j))
    rows, head, layer = [], 0, 0
    frontier = list(q)
    while frontier:
        rows.append([str(layer), " ".join(f"({i},{j})" for i, j in frontier)])
        nxt = []
        for i, j in frontier:
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < R and 0 <= nj < C and rows_in[ni][nj] != "#" and dist[ni][nj] < 0:
                    dist[ni][nj] = layer + 1
                    nxt.append((ni, nj))
        frontier = nxt
        layer += 1
    far = max(max(r) for r in dist)
    return _trace(
        "Multi-source BFS from both S cells",
        f"The grid {' / '.join(rows_in)}. Both sources start in the queue at distance 0, so each "
        f"layer grows from both at once.",
        ["Distance", "Cells first reached at that distance"],
        rows,
        f"The farthest open cell is {far} steps from its nearest S. One BFS did the work of two — "
        f"and gave each cell its distance to the *nearest* source, which two separate runs would "
        f"only give after a cell-by-cell minimum.",
    )


def _t6_dfs_finish_order():
    n, edges = 6, [(0, 2), (1, 2), (2, 3), (1, 4), (4, 3), (3, 5)]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    seen, finish, rows = [False] * n, [], []

    def dfs(u):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                dfs(v)
        finish.append(u)
        rows.append([str(len(finish)), f"finish {u}", _j(finish), _j(list(reversed(finish)))])

    for s in range(n):
        if not seen[s]:
            dfs(s)
    return _trace(
        "Topological order from DFS finish times",
        "Same course plan as Kahn's trace: 0→2, 1→2, 2→3, 1→4, 4→3, 3→5. DFS from 0, then from "
        "the next unvisited vertex; a vertex is appended when all its descendants are finished.",
        ["#", "Event", "Finish order so far", "Reversed (a topological order)"],
        rows,
        f"Reversed finish order {_j(list(reversed(finish)))} puts every course before the ones that "
        f"need it — a different valid order from Kahn's {_j(_c6_kahn(n, edges))}. Both are right; a "
        f"DAG usually has many.",
    )


def _t6_forced_edge():
    n = 4
    edges = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 0, 4), (0, 2, 10)]
    forced = 4
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    u, v, w = edges[forced]
    parent[find(u)] = find(v)
    total = w
    rows = [[f"{u}-{v} ({w})", "forced: union first", str(total)]]
    for a, b, c in sorted(edges, key=lambda e: e[2]):
        ra, rb = find(a), find(b)
        if ra == rb:
            rows.append([f"{a}-{b} ({c})", "skip — ends already connected", str(total)])
        else:
            parent[ra] = rb
            total += c
            rows.append([f"{a}-{b} ({c})", "take", str(total)])
    plain = _c6_kruskal(n, edges)[0]
    return _trace(
        "Kruskal with a forced edge",
        "Edges 0-1 (1), 1-2 (2), 2-3 (3), 3-0 (4), 0-2 (10); the road 0-2 must be built. Unioning "
        "it first contracts 0 and 2 into one town; then Kruskal runs as usual.",
        ["Edge", "Decision", "Total"],
        rows,
        f"{total} with the forced road, against {plain} for the plain MST. When the loop reaches "
        f"0-2 itself it is skipped automatically — its ends were joined before the loop began, so "
        f"its weight is counted exactly once.",
    )


def _t6_zero_one():
    n = 5
    edges = [(0, 1, 1), (0, 2, 0), (2, 1, 0), (1, 3, 1), (2, 4, 1), (4, 3, 0)]
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    INF = float("inf")
    dist = [INF] * n
    dist[0] = 0
    dq = _dq([0])
    done = [False] * n
    rows = []
    while dq:
        u = dq.popleft()
        if done[u]:
            rows.append([f"{u} (stale)", "—", _j(list(dq)), " ".join("∞" if d == INF else str(d) for d in dist)])
            continue
        done[u] = True
        acts = []
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                if w == 0:
                    dq.appendleft(v)
                    acts.append(f"{v}←{dist[v]} front")
                else:
                    dq.append(v)
                    acts.append(f"{v}←{dist[v]} back")
        rows.append([str(u), ", ".join(acts) if acts else "—", _j(list(dq)),
                     " ".join("∞" if d == INF else str(d) for d in dist)])
    return _trace(
        "0-1 BFS: weight 0 to the front, weight 1 to the back",
        "Directed edges 0→1 (1), 0→2 (0), 2→1 (0), 1→3 (1), 2→4 (1), 4→3 (0). The deque always "
        "holds at most two distances, d and d + 1, in order — Dijkstra's heap with only two values.",
        ["Pop", "Relaxations", "Deque after", "dist"],
        rows,
        f"dist = {' '.join(str(d) for d in dist)}. Vertex 1 is reached at cost 1 through 0→1 and "
        f"then at cost 0 through 0→2→1; the second arrival goes to the *front* and wins. O(V + E), "
        f"no heap.",
    )


# ================================================================ follow-ups

_F6 = {
    "trees": [
        _follow("The tree has 10⁶ nodes in a single chain. What breaks, and what do you change?",
                "Recursion is 10⁶ frames deep and throws `StackOverflowError`. Walk it iteratively — "
                "an explicit `Deque` for DFS, or a BFS order processed backwards for bottom-up DP — or "
                "run the solver on a thread with a large stack."),
        _follow("Diameter: what if edges have weights (possibly lengths ≥ 1)?",
                "Return the longest *weighted* downward path instead of the height, and record "
                "left + right through each node. With negative weights, drop negative branches with "
                "`max(0, …)` — exactly the max-path-sum shape."),
        _follow("Level order: what if you must print it bottom-up?",
                "Collect the levels as usual and reverse the list of levels at the end — not the "
                "values within each level. Or push each level list to the front of a deque."),
        _follow("LCA: what if you get 10⁵ LCA queries on the same tree?",
                "Preprocess once — binary lifting (O(n log n) table, O(log n) per query) or an Euler "
                "tour plus a sparse table (O(1) per query). Stage 8's `tree-queries` unit builds both."),
        _follow("Serialise: what if the tree is n-ary instead of binary?",
                "Write each node's value and its number of children, pre-order; reading back, each "
                "call reads a value and a count and recurses that many times. No null markers needed."),
        _follow("Max path sum: what if the path must start at the root?",
                "Then there is no \"bend\": it is a top-down (or single return value) recursion — "
                "best(n) = n.val + max(0, best(left), best(right)) — and nothing is recorded in a field."),
    ],
    "bst": [
        _follow("What if the BST must stay balanced under 10⁵ inserts and deletes?",
                "Use a self-balancing tree — `TreeMap` / `TreeSet` in Java (red-black). Hand-rolled: an "
                "AVL or treap. The operations stay the same descent; the rotations keep h = O(log n)."),
        _follow("k-th smallest: what if the tree changes between queries?",
                "Store each node's subtree size and update it on insert and delete. Then k-th smallest "
                "is one descent: compare k with size(left) + 1 and go left, stop, or go right with "
                "k − size(left) − 1."),
        _follow("Validate: what if duplicates are allowed on the left (≤)?",
                "Make the bound on the left side inclusive: a left descendant may equal its ancestor, "
                "so check lo < val ≤ hi for left descents — and decide the convention before coding."),
        _follow("What if you need \"how many keys are below x?\" and TreeMap is all you have?",
                "`headMap(x).size()` is O(n) — it walks the view. For many rank queries use an "
                "order-statistic tree, or compress the keys and use a Fenwick tree (stage 8)."),
        _follow("Merge two BSTs into one balanced BST — what is the cost?",
                "Two in-order walks (O(n + m)), merge the two sorted lists (O(n + m)), then the "
                "middle-first build (O(n + m)). Inserting one tree's values into the other is "
                "O(m log(n + m)) at best and O(m · (n + m)) if it degenerates."),
    ],
    "backtracking": [
        _follow("Only the count is needed, not the list. What changes?",
                "Return counts instead of recording copies — the `· n` output factor disappears. If "
                "different branches reach the same (index, remaining) state, memoise: the search has "
                "become a DP."),
        _follow("n grows from 12 to 40 for subset sum. What now?",
                "2⁴⁰ is too many, but 2²⁰ is fine: **meet in the middle**. Enumerate each half's subset "
                "sums (2²⁰ each), sort one, and for each sum in the other binary-search the complement. "
                "O(2^(n/2) · n)."),
        _follow("Permutations of a string with repeated letters, without duplicates?",
                "Sort, then at each depth skip a letter equal to the previous one when the previous one "
                "is unused (`i > 0 && s[i] == s[i-1] && !used[i-1]`) — or recurse over letter counts, as "
                "in `letter-tile-sequences`."),
        _follow("N-queens: just one solution for n = 1000?",
                "Backtracking is hopeless at n = 1000. There are explicit constructions (for n not "
                "2 or 3), or min-conflicts local search, which finds a solution in near-linear time in "
                "practice."),
        _follow("Word search with 10⁴ words on one board?",
                "Do not run one search per word. Put the words in a trie and run one DFS per cell, "
                "descending the trie as you walk — stage 7's word-search-with-a-trie pattern."),
    ],
    "graph-traversal": [
        _follow("The grid is 10⁴ × 10⁴. What breaks?",
                "Recursion depth (use BFS or an explicit stack), memory (10⁸ cells: a `boolean[][]` "
                "is 100 MB — use a `BitSet` or mark in place), and time budget (every cell once is "
                "still 10⁸ operations)."),
        _follow("Shortest path, but moving diagonally is allowed too?",
                "Still BFS if every move costs one — add the four diagonal offsets. If diagonals cost "
                "√2, weights differ: Dijkstra (or A* with the octile distance as heuristic)."),
        _follow("Count islands, but the map is too big to hold — rows arrive one at a time.",
                "Union-find over the current and previous row only: union within a row, union with "
                "the cell above, and count a component as finished when it does not reach the next "
                "row. Memory is O(width)."),
        _follow("Word ladder: the dictionary has 10⁵ words of length 10. How do you find neighbours fast?",
                "Do not compare every pair. For each word, generate its 10 wildcard patterns "
                "(`h*t`, `*it`, …) and bucket words by pattern; neighbours share a bucket. Then run "
                "BFS — bidirectionally, to shrink the frontier."),
        _follow("Is the graph bipartite — and if not, show the odd cycle?",
                "When BFS finds an edge u–v with equal colours, walk parent pointers up from u and v "
                "until they meet at their lowest common ancestor; the two paths plus u–v form an odd "
                "cycle."),
    ],
    "topological-sort": [
        _follow("Among all valid orders, return the lexicographically smallest.",
                "Replace Kahn's queue with a min-heap: at each step take the smallest free vertex. "
                "O(V log V + E)."),
        _follow("With at most k courses per semester, what is the minimum number of semesters?",
                "The greedy (take any k free courses) is wrong — which ones you take matters. For "
                "n ≤ 15 it is a bitmask DP over the set of courses taken; in general it is NP-hard."),
        _follow("Detect the cycle and print it, not just say one exists.",
                "Three-colour DFS with parent pointers: when an edge u → v hits a grey v, walk parent "
                "pointers from u back to v — that is the cycle."),
        _follow("Rules arrive one at a time; after each, is the plan still acyclic?",
                "Adding u → v creates a cycle iff v already reaches u. For small graphs, a DFS per "
                "rule; for large ones, incremental topological-order maintenance (e.g. Pearce–Kelly)."),
        _follow("Longest path in a DAG — why not negate the weights and run Dijkstra?",
                "Negated weights are negative, which Dijkstra cannot handle. On a DAG you do not need "
                "it: relax in topological order with max (or with min on the negated weights)."),
    ],
    "union-find": [
        _follow("Edges are also *removed* between queries. What now?",
                "DSU cannot delete. If all queries are known: process them offline in reverse "
                "(deletions become additions), or divide and conquer over time with a rollback DSU "
                "(union by size, no compression)."),
        _follow("What if you need the actual members of each group at the end?",
                "One pass: bucket every element by find(x). Or keep a linked list per root and splice "
                "the lists on union (O(1) with head/tail pointers)."),
        _follow("Why not just path compression, without union by size?",
                "Compression alone is O(log n) amortised; the combination is O(α(n)). And if you ever "
                "need rollback, compression is out and union by size is what keeps finds at O(log n)."),
        _follow("Weighted DSU: the relation is a ratio (a / b = 2.5), not a difference.",
                "Store multiplicative weights: w[x] = value(x) / value(parent[x]); compress by "
                "multiplying along the path, and link with w[rb] = w[a] · ratio / w[b]. Same structure, "
                "× in place of +."),
        _follow("Could BFS do the job of union-find here?",
                "For one static graph and one question, yes — components by BFS are O(V + E). Union-find "
                "wins when edges arrive over time and questions interleave with them."),
    ],
    "mst": [
        _follow("The edge weights change one at a time; keep the MST current.",
                "If a tree edge gets cheaper, nothing changes; if a non-tree edge gets cheaper, add it "
                "and drop the heaviest edge on the cycle it closes. The other two cases are symmetric. "
                "Each is a path-maximum query on the tree."),
        _follow("Is the MST unique?",
                "It is unique iff, for every non-tree edge, it is strictly heavier than every edge on "
                "the tree path between its ends. Equivalently: the second-best MST is strictly heavier."),
        _follow("10⁵ points in the plane, complete graph with Euclidean weights?",
                "5 · 10⁹ edges is too many to sort. The MST is contained in the Delaunay triangulation "
                "(O(n) edges), computable in O(n log n); for Manhattan distance, a sweep yields O(n) "
                "candidate edges."),
        _follow("Minimise the maximum edge, not the sum — is the MST still right?",
                "Yes: every MST is also a minimum bottleneck spanning tree. (The converse fails — a "
                "bottleneck tree need not have minimum total.)"),
        _follow("Directed graph: cheapest set of edges so every vertex is reachable from the root?",
                "That is a minimum **arborescence**, not an MST — Kruskal and Prim fail on directed "
                "edges. Chu–Liu/Edmonds solves it in O(V · E)."),
    ],
    "shortest-paths": [
        _follow("Some edges are negative but there is no negative cycle, and V = 10⁴. Bellman-Ford is too slow for all pairs — what then?",
                "Johnson's algorithm: one Bellman-Ford from a virtual source gives potentials h; "
                "reweight w'(u, v) = w + h(u) − h(v) ≥ 0; then run Dijkstra from every vertex."),
        _follow("You only need the path to ONE target on a huge grid.",
                "A* search: Dijkstra ordered by dist + heuristic, where the heuristic (Manhattan "
                "distance on a grid) never overestimates. It explores far fewer cells toward the target."),
        _follow("Dijkstra, but also count the number of shortest paths.",
                "Keep ways[v]: on a strict improvement set ways[v] = ways[u]; on a tie add ways[u]. "
                "Process in pop order — `count-shortest-paths` does exactly this."),
        _follow("Edges have both a cost and a time; minimise cost subject to time ≤ T.",
                "The limit becomes part of the state — (vertex, time used) — and a shortest path over "
                "states, or a DP in time order when every edge takes positive time. "
                "`cost-within-deadline` is this problem."),
        _follow("Why not use BFS on a weighted graph by splitting an edge of weight w into w unit edges?",
                "It is correct, and it is exactly what Dijkstra simulates efficiently. With weights up "
                "to 10⁹ the split graph is astronomically large; with weights 0/1 or tiny integers, the "
                "idea becomes 0-1 BFS or a bucket queue (Dial's algorithm)."),
    ],
}


# ================================================================ quizzes

_Q6 = {
    "trees": [
        _quiz("predict", "With \"show on each node: house robber take/skip\", what does the root of `3 4 5 1 3 null 1` show?",
              """
// take = val + Σ skip(children);  skip = Σ max(take, skip) over children
""",
              "9/7", ["9/7", "7/9", "8/7", "9/8"],
              """
Leaves: 1 → 1/0, 3 → 3/0, 1 → 1/0. Node 4: take 4 + 0 + 0 = 4, skip max(1,0) + max(3,0) = 4.
Node 5: take 5, skip 1. Root: take 3 + skip(4) + skip(5) = 3 + 4 + 1 = 8? — no: 3 + 4 + 1 = 8
would be the take; recompute: skip(4) = 4 and skip(5) = 1, so take = 8… The lab computes it —
see the note below.
"""),
        _quiz("model", "An org chart: each employee may attend a party, but no one attends together with their direct manager. Maximise the total fun score.",
              """
tree of 10^5 employees, fun[i] >= 0
""",
              "Tree DP returning (take, skip) per employee — the house-robber pattern on a tree",
              ["Tree DP returning (take, skip) per employee — the house-robber pattern on a tree",
               "Greedy: invite everyone on even levels",
               "BFS from the CEO, alternating levels",
               "Backtracking over all subsets"],
              """
\"No parent–child pair both chosen\" is an independent set on a tree. Each node returns the best
with itself taken (children skipped) and with itself skipped (children free). Level parity is a
valid choice but not an optimal one; 2ⁿ subsets is hopeless.
"""),
    ],
    "bst": [
        _quiz("predict", "Rotate left at the root of the BST `50 30 70 20 40 60 80`. The new level order?",
              """
// rotate left at x: y = x.right; x.right = y.left; y.left = x
""",
              "70 50 80 30 60 null null 20 40",
              ["70 50 80 30 60 null null 20 40", "30 20 50 null null 40 70 null null 60 80",
               "70 80 50 null null 30 60 20 40", "60 50 70 30 null null 80 20 40"],
              """
70 comes up as the root; 50 becomes its left child and keeps 30 on its left; 70's old left
child, 60, becomes 50's right child. The in-order is still 20 30 40 50 60 70 80 — a rotation
never changes it.
"""),
        _quiz("model", "Stock prices arrive in a stream; after each, report how many earlier prices were lower.",
              """
prices: 10^5 values, online
""",
              "An order-statistic BST (or a Fenwick tree over compressed prices): rank of each new value",
              ["An order-statistic BST (or a Fenwick tree over compressed prices): rank of each new value",
               "A HashMap of counts",
               "Sort all prices once at the end",
               "A monotonic stack"],
              """
Each answer is a rank query in a set that keeps growing — a BST with subtree sizes answers it
in O(log n). A hash map has no order; sorting at the end loses the online answers; a monotonic
stack answers \"nearest smaller\", not \"how many smaller\".
"""),
    ],
    "backtracking": [
        _quiz("predict", "How many distinct non-empty sequences can be laid out with the tiles `AAB`?",
              """
int count() {                      // freq[] per letter
    int total = 0;
    for (int c = 0; c < 26; c++) if (freq[c] > 0) { freq[c]--; total += 1 + count(); freq[c]++; }
    return total;
}
""",
              "8", ["8", "9", "15", "6"],
              """
A, B, AA, AB, BA, AAB, ABA, BAA. Recursing over distinct letters never counts the two A tiles as
different choices, so no sequence appears twice.
"""),
        _quiz("model", "Assign 12 exam papers to 3 markers so the heaviest workload is as small as possible; n ≤ 12.",
              """
paper times: 12 values
markers: 3
""",
              "Backtracking into buckets with a bound (prune when a load reaches the best so far), or binary search on the answer + a feasibility search",
              ["Backtracking into buckets with a bound (prune when a load reaches the best so far), or binary search on the answer + a feasibility search",
               "Sort and hand each paper to the least-loaded marker (always optimal)",
               "Dijkstra over loads",
               "Topological sort of the papers"],
              """
The least-loaded greedy is a good heuristic but not optimal (3, 3, 2, 2, 2 into 2 gives 7, the
optimum is 6). n ≤ 12 invites a search: branch and bound on the maximum load, with the same
symmetry pruning as the equal-partition problem.
"""),
    ],
    "graph-traversal": [
        _quiz("predict", "Multi-source BFS on the row `S...S`: what distance does the middle cell get?",
              """
// every S starts in the queue at distance 0
""",
              "2", ["2", "4", "0", "1"],
              """
The middle cell is two steps from each S. A single-source BFS from the left S would say 2 as
well — but the cell next to the right S would get 3 instead of 1.
"""),
        _quiz("model", "A lock with four wheels (0000–9999); some codes are forbidden. Fewest single-wheel turns from 0000 to the target?",
              """
start 0000, target 0202, deadends: 0201 0101 0102 1212 2002
""",
              "BFS over the 10⁴ codes; neighbours are the 8 single-wheel turns",
              ["BFS over the 10⁴ codes; neighbours are the 8 single-wheel turns",
               "Turn each wheel directly to its target digit",
               "Dijkstra with the digit difference as weight",
               "Backtracking over all 4-digit codes"],
              """
Each turn costs one, and the forbidden codes make the direct route unusable, so it is an
unweighted shortest path on an implicit graph of 10⁴ states — BFS, marking deadends as visited
up front.
"""),
    ],
    "topological-sort": [
        _quiz("predict", "Reverse DFS finish order on 0→2, 1→2, 2→3, 1→4, 4→3, 3→5 (DFS from 0 first, then 1, …; neighbours in edge order)?",
              """
void dfs(int u) { seen[u] = true; for (int v : adj[u]) if (!seen[v]) dfs(v); finish.add(u); }
""",
              _j(list(reversed([5, 3, 2, 0, 4, 1]))),
              [_j(list(reversed([5, 3, 2, 0, 4, 1]))), "0 1 2 4 3 5", "5 3 2 0 4 1", "0 2 3 5 1 4"],
              """
DFS from 0 finishes 5, 3, 2, 0; DFS from 1 finishes 4, then 1. Reversed: 1 4 0 2 3 5 — every
rule points forward. The un-reversed list is the classic mistake.
"""),
        _quiz("model", "Given a sorted list of words in an unknown alphabet, recover the letter order.",
              """
words: wrt wrf er ett rftt
""",
              "Build edges from the first differing letter of each adjacent pair, then topologically sort the letters",
              ["Build edges from the first differing letter of each adjacent pair, then topologically sort the letters",
               "Sort the letters by first appearance",
               "Union-find over letters that appear together",
               "Dijkstra from the first letter"],
              """
Only adjacent words give information, and only at their first differing position (t before f,
w before e, r before t, e before r). The letters and these rules form a DAG; any topological order
is a valid alphabet (and a cycle means the input is inconsistent).
"""),
    ],
    "union-find": [
        _quiz("predict", "Smallest-letter roots: after uniting d–c, o–a, g–t, what does `toad` become?",
              """
// union keeps the smaller letter as the root; each letter maps to find(letter)
""",
              "gaac", ["gaac", "toad", "caag", "gaad"],
              """
t ~ g → g; o ~ a → a; a → a; d ~ c → c. \"gaac\". Choosing the root as the class's smallest letter
makes find() the answer directly.
"""),
        _quiz("model", "Cities 1…n, roads between any two cities that share a factor above t; answer 10⁵ \"connected?\" queries.",
              """
n = 2 * 10^5, t given, q = 10^5
""",
              "Union every multiple of d with d, for each d > t — O(n log n) unions — then find() per query",
              ["Union every multiple of d with d, for each d > t — O(n log n) unions — then find() per query",
               "Build every road, then BFS per query",
               "Compute gcd for each query pair",
               "Floyd–Warshall over the cities"],
              """
The multiples of d form a clique, and a clique needs only a spanning star to be connected. The
harmonic sum keeps the unions at n ln n. gcd of the query pair alone misses indirect routes
(4 and 9 are connected through 6 when t = 1).
"""),
    ],
    "mst": [
        _quiz("predict", "Maximum spanning tree of 0-1 (4), 1-2 (2), 2-3 (7), 0-2 (3), 1-3 (9): total weight?",
              """
// Kruskal, heaviest edge first
""",
              "20", ["20", "13", "25", "16"],
              """
Take 1-3 (9), 2-3 (7), 0-1 (4); 0-2 (3) and 1-2 (2) would close cycles. 9 + 7 + 4 = 20.
"""),
        _quiz("model", "Split n customers into k clusters so that the closest pair of clusters is as far apart as possible.",
              """
points: n, k clusters
""",
              "Kruskal, stopping when k components remain; the next edge Kruskal would take is the spacing",
              ["Kruskal, stopping when k components remain; the next edge Kruskal would take is the spacing",
               "k-means",
               "Dijkstra from k random points",
               "Sort points by x and cut into k blocks"],
              """
Single-linkage clustering is partial Kruskal: merging the closest pair of groups n − k times
leaves k clusters whose minimum separation is maximal (the cut property again).
"""),
    ],
    "shortest-paths": [
        _quiz("predict", "0-1 BFS on 0→1 (1), 0→2 (0), 2→1 (0), 1→3 (1), 2→4 (1), 4→3 (0): dist[3]?",
              """
// weight 0 → push front, weight 1 → push back
""",
              "1", ["1", "2", "0", "3"],
              """
0 → 2 (0) → 1 (0) → 3 (1) costs 1; so does 0 → 2 → 4 (1) → 3 (0). Nothing costs 0: every
route to 3 uses one weight-1 edge.
"""),
        _quiz("bug", "Floyd–Warshall reports d[i][j] = −2147483647 for pairs that are not connected. Why?",
              """
int INF = Integer.MAX_VALUE;
// ... d[i][j] = Math.min(d[i][j], d[i][k] + d[k][j]);
""",
              "INF + INF overflows to a negative number; use a smaller INF (e.g. 10⁹ in int, or long) or skip INF entries",
              ["INF + INF overflows to a negative number; use a smaller INF (e.g. 10⁹ in int, or long) or skip INF entries",
               "k must be the inner loop",
               "d[i][i] must start at INF",
               "Floyd cannot handle disconnected graphs"],
              """
Two \"infinite\" distances added together wrap around below zero, and `min` happily keeps the
result. Pick an INF with headroom (below MAX / 2) or `continue` when d[i][k] or d[k][j] is INF.
"""),
    ],
}

# The first trees quiz above had its answer worked out by hand in the prompt; recompute it so
# the card can never state a wrong number, and rewrite the explanation from the computed values.
def _c6_rob(line):
    root = _t6_build(line)

    def go(n):
        if n is None:
            return 0, 0
        lt, ls = go(n.left)
        rt, rs = go(n.right)
        return n.val + ls + rs, max(lt, ls) + max(rt, rs)

    return go(root)


_ROB_LINE = "3 4 5 1 3 null 1"
_rt, _rs = _c6_rob(_ROB_LINE)
_Q6["trees"][0] = _quiz(
    "predict",
    f"With \"show on each node: house robber take/skip\", what does the root of `{_ROB_LINE}` show?",
    """
// take = val + Σ skip(children);  skip = Σ max(take, skip) over children
""",
    f"{_rt}/{_rs}", [f"{_rt}/{_rs}", f"{_rs}/{_rt}", f"{_rt + 1}/{_rs}", f"{_rt}/{_rs + 2}"],
    f"""
Leaves 1, 3 and 1 show 1/0, 3/0, 1/0. Node 4 (children 1 and 3): take 4, skip 1 + 3 = 4. Node 5
(child 1): take 5, skip 1. The root: take 3 + skip(4) + skip(5) = 3 + 4 + 1 = {_rt}; skip
max(4, 4) + max(5, 1) = {_rs}. The answer to the robber problem is max = {max(_rt, _rs)}.
""")


# ================================================================ drills

def _c6_flood_regions(rows):
    R, C = len(rows), len(rows[0])
    seen = [[False] * C for _ in range(R)]
    k = 0
    for i in range(R):
        for j in range(C):
            if rows[i][j] != "#" and not seen[i][j]:
                k += 1
                st = [(i, j)]
                seen[i][j] = True
                while st:
                    x, y = st.pop()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < R and 0 <= ny < C and rows[nx][ny] != "#" and not seen[nx][ny]:
                            seen[nx][ny] = True
                            st.append((nx, ny))
    return k


_D6 = {
    "bst": [
        _calc("Rotate right at the root of the BST `8 4 12 2 6`. Level order?", "4 2 8 null null 6 12",
              "4 comes up; 8 becomes its right child and takes 4's old right child 6 as its left."),
    ],
    "graph-traversal": [
        _calc("How many open regions does the maze `..#.. / ###.. / .#...` have?",
              str(_c6_flood_regions(["..#..", "###..", ".#..."])),
              "Top-left pair, the right-hand block, and the lone bottom-left cell."),
    ],
    "topological-sort": [
        _calc("Reverse DFS finish order for 0→2, 1→2, 2→3, 1→4, 4→3, 3→5 (DFS from 0 first)?",
              "1 4 0 2 3 5", "Finish order 5 3 2 0 4 1, reversed."),
        _calc("How many edges can a DAG on 6 vertices have at most?", "15",
              "Order the vertices; every pair can have one edge pointing forward: C(6, 2)."),
    ],
    "union-find": [
        _calc("gcd-connectivity with n = 10, t = 2: are 4 and 9 connected? (yes / no)", "no",
              "Divisors above 2 give cliques {3, 6, 9}, {4, 8}, {5, 10}, {6}, {7}, … — 4 and 9 share no chain.",
              accept=["No"]),
        _calc("Smallest-equivalent: unite a–z, z–q, b–c. What does `quiz` become?", "auia",
              "q ~ z ~ a → a; u, i unchanged; z → a."),
    ],
    "mst": [
        _calc("Maximum spanning tree of 0-1 (4), 1-2 (2), 2-3 (7), 0-2 (3), 1-3 (9)?", "20",
              "Kruskal heaviest first: 9, 7, 4."),
        _calc("Second-best spanning tree of 0-1 (1), 1-2 (2), 2-3 (3), 3-0 (5), 0-2 (4)?", "8",
              "MST 6; swap 0-2 (4) for 1-2 (2) or 3-0 (5) for 2-3 (3): 8."),
    ],
    "shortest-paths": [
        _calc("0-1 BFS on 0→1 (1), 0→2 (0), 2→1 (0), 1→3 (1), 2→4 (1), 4→3 (0): dist[] for 0…4?",
              "0 0 0 1 1", "0 → 2 → 1 is free; 3 and 4 need one weight-1 edge each."),
        _calc("Floyd–Warshall on 0→1 (4), 1→2 (1), 0→2 (7): d[0][2]?", "5", "Through 1: 4 + 1."),
    ],
}


# ================================================================ labs

_MAZE_LAB = _lab("maze", """
Type a maze (`#` walls, `S` start, `T` target; any other character is open floor). **BFS**
numbers every cell with its distance from S and traces the shortest path to T; **multi-source**
starts from every S at once; **flood fill** numbers the open regions. Drag the slider to watch
the frontier grow one layer at a time.
""", [
    ("Around the wall", {"grid": "S...#....\n.##.#.##.\n.#..#..#.\n.#.###.#.\n........T", "walk": "bfs"}),
    ("No way through", {"grid": "S..#...\n...#...\n...#..T", "walk": "bfs"}),
    ("Two sources", {"grid": "S.......\n.##..##.\n........\n.......S", "walk": "multi"}),
    ("Count the rooms", {"grid": "...#....\n...#.##.\n####.#..\n...#.###\n...#....", "walk": "flood"}),
])

def _c6_maze_reachable(grid):
    rows = grid.split("\n")
    cells = [(i, j) for i, r in enumerate(rows) for j, ch in enumerate(r)]
    s = next(c for c in cells if rows[c[0]][c[1]] == "S")
    t = next((c for c in cells if rows[c[0]][c[1]] == "T"), None)
    seen, st = {s}, [s]
    while st:
        i, j = st.pop()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < len(rows) and 0 <= nj < len(rows[0]) and rows[ni][nj] != "#" and (ni, nj) not in seen:
                seen.add((ni, nj))
                st.append((ni, nj))
    return t is not None and t in seen


# A preset whose label promises a route must have one (an earlier draft of
# "Around the wall" was sealed shut and nothing noticed until the lab said so).
for _p6 in _MAZE_LAB["presets"]:
    if _p6["values"]["walk"] == "bfs":
        _want = not _p6["label"].startswith("No way")
        assert _c6_maze_reachable(_p6["values"]["grid"]) == _want, \
            f"maze preset {_p6['label']!r}: reachable should be {_want}"


_TREE_PRESETS_R2 = {
    "trees": [
        ("House robber, take / skip", {"tree": "3 4 5 1 3 null 1", "value": 0, "note": "rob"}),
        ("Max path sum: each node's gain", {"tree": "-10 9 20 null null 15 7", "value": 0, "note": "gain"}),
        ("Cameras, bottom-up", {"tree": "0 0 null 0 0 null null 0 0", "value": 0, "note": "camera"}),
        ("Subtree sizes", {"tree": "1 2 3 4 5 6 7 8", "value": 0, "note": "size"}),
    ],
    "bst": [
        ("Rotate me (select 30, rotate right)", {"tree": "50 30 70 20 40 60 80", "value": 45, "note": "height"}),
        ("Build by inserting", {"tree": "null", "value": 50, "note": "depth"}),
    ],
}

_GRAPH_PRESETS_R2 = {
    "graph-traversal": [
        ("Two-colouring: even cycle", {"n": 6, "edges": "0 1\n1 2\n2 3\n3 4\n4 5\n5 0", "directed": "no", "source": 0, "algo": "bipartite"}),
        ("Two-colouring: odd cycle", {"n": 5, "edges": "0 1\n1 2\n2 3\n3 4\n4 0", "directed": "no", "source": 0, "algo": "bipartite"}),
    ],
    "shortest-paths": [
        ("0-1 BFS", {"n": 5, "edges": "0 1 1\n0 2 0\n2 1 0\n1 3 1\n2 4 1\n4 3 0", "directed": "yes", "source": 0, "algo": "zeroone"}),
        ("Floyd–Warshall", {"n": 4, "edges": "0 1 3\n1 2 -2\n0 2 4\n2 0 1\n2 3 2", "directed": "yes", "source": 0, "algo": "floyd"}),
    ],
}


def _attach_s6_round2():
    by_key = {u["key"]: u for u in _UNITS}
    for key, fs in _F6.items():
        by_key[key]["followups"].extend(fs)
    for key, qs in _Q6.items():
        by_key[key]["quizzes"].extend(qs)
    for key, ds in _D6.items():
        by_key[key]["drills"].extend(ds)
    by_key["graph-traversal"]["traces"].append(_t6_multi_bfs())
    by_key["topological-sort"]["traces"].append(_t6_dfs_finish_order())
    by_key["mst"]["traces"].append(_t6_forced_edge())
    by_key["shortest-paths"]["traces"].append(_t6_zero_one())
    by_key["graph-traversal"]["extra_labs"].append(_MAZE_LAB)
    for key, presets in {**_TREE_PRESETS_R2, **_GRAPH_PRESETS_R2}.items():
        lab = by_key[key]["lab"]
        extra = _lab(lab["kind"], lab["intro"], presets)["presets"]
        lab["presets"].extend(extra)


_attach_s6_round2()
