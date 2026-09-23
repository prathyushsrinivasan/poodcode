# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 55 — Trees & Graphs, part 3: traversal and topological order.
#
#   bfs-levels              the BFS template, printing every distance
#   board-game-fewest-rolls BFS over an implicit graph: squares and die rolls
#   grid-k-breaks           BFS over (cell, walls broken) — an augmented state
#   keys-and-doors-bfs      BFS over (cell, keys held) — the state is a bitmask
#   semester-levels         Kahn's algorithm, layer by layer
#   unique-topo-order       Kahn with a question: was the queue ever wider than one?
#   dag-path-count          DP in topological order: paths add
#   critical-path-time      DP in topological order: finish times take the max
#
# Defines the shapes `n_pairs`, `grid_k` and `arr_graph`.
# ===========================================================================

# "n j", then j lines "a b"
_SHAPES["n_pairs"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, j = d[0], d[1]\n"
       "p = [(d[2 + 2 * i], d[3 + 2 * i]) for i in range(j)]\n",
    py_params="n, p",
    js=_JS_NUMS + "const n = Number(d[0]), j = Number(d[1]);\n"
       "const p = Array.from({ length: j }, (_, i) => [Number(d[2 + 2 * i]), Number(d[3 + 2 * i])]);\n",
    js_params="n, p",
    java="        int n = sc.nextInt(), j = sc.nextInt();\n        int[][] p = new int[j][2];\n"
         "        for (int i = 0; i < j; i++) { p[i][0] = sc.nextInt(); p[i][1] = sc.nextInt(); }\n",
    java_params="int n, int[][] p", java_args="n, p",
)
# "r c k", then r rows of characters
_SHAPES["grid_k"] = dict(
    py="d = sys.stdin.read().split()\nr, c, k = int(d[0]), int(d[1]), int(d[2])\ng = [list(row) for row in d[3:3 + r]]\n",
    py_params="g, k",
    js=_JS_NUMS + "const r = Number(d[0]), k = Number(d[2]);\nconst g = d.slice(3, 3 + r).map(row => row.split(''));\n",
    js_params="g, k",
    java="        int r = sc.nextInt(), c = sc.nextInt(), k = sc.nextInt();\n        char[][] g = new char[r][];\n"
         "        for (int i = 0; i < r; i++) g[i] = sc.next().toCharArray();\n",
    java_params="char[][] g, int k", java_args="g, k",
)
# "n m", then n integers, then m lines "u v"
_SHAPES["arr_graph"] = dict(
    py="d = list(map(int, sys.stdin.read().split()))\nn, m = d[0], d[1]\na = d[2:2 + n]\n"
       "edges = [(d[2 + n + 2 * i], d[3 + n + 2 * i]) for i in range(m)]\n",
    py_params="a, edges",
    js=_JS_NUMS + "const n = Number(d[0]), m = Number(d[1]);\nconst a = d.slice(2, 2 + n).map(Number);\n"
       "const edges = Array.from({ length: m }, (_, i) => [Number(d[2 + n + 2 * i]), Number(d[3 + n + 2 * i])]);\n",
    js_params="a, edges",
    java="        int n = sc.nextInt(), m = sc.nextInt();\n        int[] a = new int[n];\n"
         "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n        int[][] edges = new int[m][2];\n"
         "        for (int i = 0; i < m; i++) { edges[i][0] = sc.nextInt(); edges[i][1] = sc.nextInt(); }\n",
    java_params="int[] a, int[][] edges", java_args="a, edges",
)


def _rand_dag(n, m, rng):
    """m distinct edges u -> v with u before v in a hidden random order."""
    order = rng.shuffle(list(range(n)))
    pos = {v: i for i, v in enumerate(order)}
    seen, edges, tries = set(), [], 0
    while len(edges) < m and tries < 50 * m + 100:
        tries += 1
        u, v = rng.randint(0, n - 1), rng.randint(0, n - 1)
        if u == v:
            continue
        if pos[u] > pos[v]:
            u, v = v, u
        if (u, v) in seen:
            continue
        seen.add((u, v))
        edges.append((u, v))
    return edges


def _arr_graph_case(vals, edges):
    return (f"{len(vals)} {len(edges)}\n" + " ".join(map(str, vals)) + "\n"
            + "".join(f"{u} {v}\n" for u, v in edges))


def _board_case(n, count, seed, back_pct=50):
    """A board of n squares with `count` shortcuts obeying the statement: distinct
    starts, no start at 1 or n, and no shortcut ending where another starts."""
    rng = _Lcg(seed)
    starts, ends, out = set(), set(), []
    tries = 0
    while len(out) < count and tries < 100 * count:
        tries += 1
        a = rng.randint(2, n - 1)
        if a in starts or a in ends:
            continue
        if rng.randint(1, 100) <= back_pct:
            b = rng.randint(1, a - 1)
        else:
            b = rng.randint(a + 1, n)
        if b in starts or b == a:
            continue
        starts.add(a)
        ends.add(b)
        out.append((a, b))
    return f"{n} {len(out)}\n" + "".join(f"{a} {b}\n" for a, b in out)


def _grid_case(rows, k=None):
    head = f"{len(rows)} {len(rows[0])}" + ("" if k is None else f" {k}")
    return head + "\n" + "\n".join(rows) + "\n"


def _rand_grid(r, c, seed, wall_pct):
    rng = _Lcg(seed)
    g = [["#" if rng.randint(1, 100) <= wall_pct else "." for _ in range(c)] for _ in range(r)]
    g[0][0] = g[r - 1][c - 1] = "."
    return ["".join(row) for row in g]


_p(
    "bfs-levels", "How Far Is Everyone", "Easy",
    topics=["Graph", "Breadth-First Search"], subtopics=["Graph", "Breadth-First Search", "Shortest Path"],
    companies=["Amazon", "Microsoft"],
    shape="graph", ret="String",
    todo="BFS from 0 with dist[] initialised to -1; dist[v] = dist[u] + 1 when v is first discovered",
    description=(
        "A friendship network has `n` people (0 to `n − 1`) and `m` friendships, each between two "
        "people. For every person, print how many friendship hops they are from person `0`, or "
        "`-1` if they cannot be reached at all.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v`, a friendship (it goes both ways).\n\n"
        "### Output\n`n` numbers on one line: the distances of people 0, 1, …, n − 1."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\nThere may be repeated friendships.",
    hints=[
        "Every hop costs the same, so breadth-first search finds shortest distances.",
        "Build an adjacency list first. Then start a queue at 0 with dist[0] = 0 and every other distance −1.",
        "Set dist[v] the moment v is first *discovered* (pushed), not when it is popped — then the −1 doubles as the visited set.",
    ],
    opt=("O(n + m)", "O(n + m)",
         "Every vertex is enqueued once and every edge examined twice."),
    editorial=(
        "## The one thing this teaches\n**The BFS template, and why it gives distances.** The "
        "queue releases vertices in order of distance — all the 1s, then all the 2s — so the "
        "first time a vertex is reached is along a shortest path.\n\n"
        "## Approach\n```java\nint[] dist = new int[n];\nArrays.fill(dist, -1);\ndist[0] = 0;\n"
        "ArrayDeque<Integer> q = new ArrayDeque<>(List.of(0));\nwhile (!q.isEmpty()) {\n    int u = q.poll();\n"
        "    for (int v : adj.get(u))\n        if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); }\n}\n```\n\n"
        "## Mark on push, not on pop\nMarking on pop lets the same vertex be pushed by several "
        "neighbours before it is ever popped — the answer survives, but the queue can grow to "
        "O(m) and the running time with it."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = [-1] * n
    dist[0] = 0
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return " ".join(map(str, dist))
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
        int[] dist = new int[n];
        Arrays.fill(dist, -1);
        dist[0] = 0;
        ArrayDeque<Integer> q = new ArrayDeque<>();
        q.add(0);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj.get(u))
                if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(dist[i]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _graph_case(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)])),
        ("Example 2", _graph_case(4, [(1, 2), (2, 3)])),
    ],
    hidden=[
        ("Alone", "1 0\n"),
        ("Repeated friendship", _graph_case(3, [(0, 1), (1, 0), (1, 2), (2, 1)])),
        ("A cycle", _graph_case(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)])),
        ("Two groups", _graph_case(7, [(0, 1), (1, 2), (3, 4), (4, 5), (5, 6)])),
        ("Random", _graph_case(200, _rand_graph(200, 300, _Lcg(161)))),
        ("Long path", _graph_case(30000, [(i, i + 1) for i in range(29999)])),
        ("Large random", _graph_case(30000, _rand_graph(30000, 60000, _Lcg(162)))),
    ],
    expl=[
        "0's friends 1 and 2 are one hop away; 3 is two (through either); 4 is three; 5 has no friendships at all.",
        "Nobody is connected to 0.",
    ],
    prereqs=[
        ("bfs", "A queue releases vertices in order of distance."),
        ("graph_repr", "An adjacency list built from the edge list, both directions."),
    ],
)


_p(
    "board-game-fewest-rolls", "Race Across the Board", "Medium",
    topics=["Graph", "Breadth-First Search"], subtopics=["Breadth-First Search", "Implicit Graph"],
    companies=["Amazon", "Meta"],
    shape="n_pairs", ret="int",
    todo="BFS over squares: from s, each roll d in 1..6 lands on s + d, then follows a shortcut if one starts there",
    description=(
        "A board game has squares `1` to `n`. You start on square `1` and win on square `n`. Each "
        "turn you roll a die and move forward `1` to `6` squares (you choose the roll — the "
        "question is the best case). You may not move past square `n`.\n\n"
        "Some squares start a **shortcut** `a → b`: landing on `a` moves you straight to `b`, which "
        "may be ahead (a ladder) or behind (a chute). A shortcut is followed once — no shortcut "
        "starts at the end of another, or at square `1` or `n`.\n\n"
        "Print the fewest turns needed to reach square `n`, or `-1` if it cannot be reached.\n\n"
        "### Input\nLine 1: `n j`.\nNext `j` lines: `a b`, a shortcut.\n\n### Output\nThe fewest turns, or `-1`."
    ),
    constraints="2 ≤ n ≤ 10^5\n0 ≤ j ≤ n / 2\nShortcut starts are distinct.",
    hints=[
        "Squares are vertices and rolls are edges. Every roll costs one turn, so the fewest turns is a BFS distance.",
        "From square s the neighbours are s + 1 … s + 6 (not past n), each replaced by its shortcut's end if a shortcut starts there.",
        "Mark the square you end up on (after the shortcut) as visited — that is where you actually stand.",
    ],
    opt=("O(n)", "O(n)",
         "Each square is enqueued at most once and has at most six out-edges."),
    editorial=(
        "## The one thing this teaches\n**The graph is implicit.** Nothing hands you an edge "
        "list: the edges are a rule (\"roll 1 to 6, then follow the shortcut\"), applied when a "
        "square is popped. Recognising a BFS in a game is most of the problem.\n\n"
        "## Approach\n```java\nint[] jump = new int[n + 1];               // 0 = no shortcut\n"
        "int[] dist = new int[n + 1];\nArrays.fill(dist, -1);\ndist[1] = 0;\nqueue.add(1);\n"
        "while (!queue.isEmpty()) {\n    int s = queue.poll();\n    for (int d = 1; d <= 6 && s + d <= n; d++) {\n"
        "        int t = jump[s + d] != 0 ? jump[s + d] : s + d;\n        if (dist[t] == -1) { dist[t] = dist[s] + 1; queue.add(t); }\n"
        "    }\n}\nreturn dist[n];\n```\n\n"
        "## Why not greedy?\n\"Always take the longest ladder in reach\" fails when that ladder "
        "leads to a stretch full of chutes. BFS considers every square at each distance, so it "
        "cannot be trapped."
    ),
    py='''
def solve(n, p):
    jump = [0] * (n + 1)
    for a, b in p:
        jump[a] = b
    dist = [-1] * (n + 1)
    dist[1] = 0
    q = deque([1])
    while q:
        s = q.popleft()
        for d in range(1, 7):
            if s + d > n:
                break
            t = jump[s + d] or s + d
            if dist[t] == -1:
                dist[t] = dist[s] + 1
                q.append(t)
    return dist[n]
''',
    java='''
    static int solve(int n, int[][] p) {
        int[] jump = new int[n + 1];
        for (int[] e : p) jump[e[0]] = e[1];
        int[] dist = new int[n + 1];
        Arrays.fill(dist, -1);
        dist[1] = 0;
        ArrayDeque<Integer> q = new ArrayDeque<>();
        q.add(1);
        while (!q.isEmpty()) {
            int s = q.poll();
            for (int d = 1; d <= 6 && s + d <= n; d++) {
                int t = jump[s + d] != 0 ? jump[s + d] : s + d;
                if (dist[t] == -1) { dist[t] = dist[s] + 1; q.add(t); }
            }
        }
        return dist[n];
    }
''',
    examples=[
        ("Example 1", "20 2\n3 15\n17 4\n"),
        ("Example 2", "12 6\n2 1\n3 1\n4 1\n5 1\n6 1\n7 1\n"),
    ],
    hidden=[
        ("Two squares", "2 0\n"),
        ("Plain board", "100 0\n"),
        ("Ladder to the end", "30 1\n2 30\n"),
        ("Tempting ladder into chutes", "40 7\n2 20\n21 3\n22 3\n23 3\n24 3\n25 3\n26 3\n"),
        ("Walled off", "15 6\n8 2\n9 2\n10 2\n11 2\n12 2\n13 2\n"),
        ("Random", _board_case(500, 60, 165)),
        ("Mostly chutes", _board_case(300, 120, 166, back_pct=85)),
        ("Large", _board_case(100000, 1000, 167)),
    ],
    expl=[
        "Roll 2 to land on 3 and ride to 15, then 5 to reach 20: two turns.",
        "Squares 2 to 7 all send you back to 1, and no roll reaches past 7: −1.",
    ],
    prereqs=[
        ("bfs", "Every roll costs one turn, so the fewest turns is a breadth-first distance."),
        ("graph_repr", "The edges are a rule applied on the fly, not a stored list."),
    ],
)


_p(
    "grid-k-breaks", "Tunnel Through at Most k Walls", "Hard",
    topics=["Graph", "Breadth-First Search", "Matrix"], subtopics=["Breadth-First Search", "State Space", "Grid"],
    companies=["Google", "Amazon"],
    shape="grid_k", ret="int",
    todo="BFS over states (row, col, walls broken so far); a wall cell costs one break; keep the fewest breaks seen per cell to prune",
    description=(
        "A mine is an `r × c` grid of open cells `.` and rock `#`. A digger starts at the top-left "
        "cell and wants the bottom-right cell, moving up, down, left or right one cell per step. "
        "It may drill through **at most `k`** rock cells on the way (entering a rock cell drills it; "
        "each costs one of the `k`).\n\n"
        "Print the fewest steps, or `-1` if it is impossible.\n\n"
        "### Input\nLine 1: `r c k`.\nNext `r` lines: the grid. The two corners are always open.\n\n"
        "### Output\nThe fewest steps, or `-1`."
    ),
    constraints="1 ≤ r, c ≤ 40\n0 ≤ k ≤ r · c",
    hints=[
        "A cell alone is not enough state: reaching it having drilled 1 wall is not the same as reaching it having drilled 3.",
        "BFS over (row, col, used). Every move is one step, so the first time the target is popped is optimal.",
        "Prune: if a cell was already reached with fewer (or equal) walls used, a later visit with more is useless. Keep best[r][c] = fewest walls used to reach it. And k ≥ r + c − 2 means the straight path always works.",
    ],
    opt=("O(r · c · k)", "O(r · c · k)",
         "At most k + 1 states per cell, each with four moves; the pruning usually visits far fewer."),
    editorial=(
        "## The one thing this teaches\n**When the same place can be \"better\" or \"worse\", the "
        "place is not the state.** BFS needs every state reached for the first time to be reached "
        "optimally. Two arrivals at one cell with different walls left are different futures, so "
        "the state is (cell, walls used).\n\n"
        "## Approach\n```java\n// queue of {r, c, used}; best[r][c] = fewest walls used to arrive\n"
        "while (!q.isEmpty()) {\n    for (int size = q.size(); size-- > 0; ) {\n        int[] s = q.poll();\n"
        "        if (s[0] == R - 1 && s[1] == C - 1) return steps;\n        for (int[] d : DIRS) {\n"
        "            int nr = s[0] + d[0], nc = s[1] + d[1];\n            if (out of bounds) continue;\n"
        "            int nu = s[2] + (g[nr][nc] == '#' ? 1 : 0);\n            if (nu > k || nu >= best[nr][nc]) continue;\n"
        "            best[nr][nc] = nu;\n            q.add(new int[]{nr, nc, nu});\n        }\n    }\n    steps++;\n}\n```\n\n"
        "## Why `nu >= best` is a safe prune\nA state arriving later in BFS has taken at least as "
        "many steps. If it has also used at least as many walls, it is dominated: anything it can "
        "do, the earlier state could do with fewer steps."
    ),
    py='''
def solve(g, k):
    r, c = len(g), len(g[0])
    if k >= r + c - 2:
        return r + c - 2
    INF = float("inf")
    best = [[INF] * c for _ in range(r)]
    best[0][0] = 0
    q = deque([(0, 0, 0)])
    steps = 0
    while q:
        for _ in range(len(q)):
            i, j, used = q.popleft()
            if i == r - 1 and j == c - 1:
                return steps
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < r and 0 <= nj < c:
                    nu = used + (g[ni][nj] == "#")
                    if nu <= k and nu < best[ni][nj]:
                        best[ni][nj] = nu
                        q.append((ni, nj, nu))
        steps += 1
    return -1
''',
    java='''
    static int solve(char[][] g, int k) {
        int R = g.length, C = g[0].length;
        if (k >= R + C - 2) return R + C - 2;
        int[][] best = new int[R][C];
        for (int[] row : best) Arrays.fill(row, Integer.MAX_VALUE);
        best[0][0] = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        ArrayDeque<int[]> q = new ArrayDeque<>();
        q.add(new int[]{0, 0, 0});
        int steps = 0;
        while (!q.isEmpty()) {
            for (int size = q.size(); size-- > 0; ) {
                int[] s = q.poll();
                if (s[0] == R - 1 && s[1] == C - 1) return steps;
                for (int[] d : dirs) {
                    int nr = s[0] + d[0], nc = s[1] + d[1];
                    if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
                    int nu = s[2] + (g[nr][nc] == '#' ? 1 : 0);
                    if (nu > k || nu >= best[nr][nc]) continue;
                    best[nr][nc] = nu;
                    q.add(new int[]{nr, nc, nu});
                }
            }
            steps++;
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", _grid_case(["..#..", "#.#.#", "..##.", "#...#", "####."], 1)),
        ("Example 2", _grid_case([".##", "###", "##."], 1)),
    ],
    hidden=[
        ("One cell", _grid_case(["."], 0)),
        ("No drilling needed", _grid_case(["...", "...", "..."], 0)),
        ("k = 0 blocked", _grid_case([".#", "#."], 0)),
        ("A long detour or one wall", _grid_case([".#...", ".#.#.", ".#.#.", ".#.#.", "...#."], 1)),
        ("Big k shortcut", _grid_case(_rand_grid(10, 10, 171, 70), 30)),
        ("Random", _grid_case(_rand_grid(20, 20, 172, 35), 3)),
        ("Dense rock", _grid_case(_rand_grid(40, 40, 173, 60), 6)),
        ("Large sparse", _grid_case(_rand_grid(40, 40, 174, 25), 2)),
    ],
    expl=[
        "Down the open cells of column 1, then along row 3, drilling only the rock at (4, 3): 8 steps, as short as any corner-to-corner walk can be.",
        "Every route from corner to corner crosses at least two rock cells, and k is 1.",
    ],
    prereqs=[
        ("bfs", "Breadth-first over states, where a state is (row, column, walls used)."),
        ("grid", "Four-directional moves, bounds checked before access."),
    ],
)


_p(
    "keys-and-doors-bfs", "Collect Every Key", "Hard",
    topics=["Graph", "Breadth-First Search", "Bit Manipulation"], subtopics=["Breadth-First Search", "Bitmask", "State Space"],
    companies=["Google", "Airbnb"],
    shape="grid", ret="int",
    todo="BFS over (row, col, keys) with keys a bitmask; a door needs its key's bit; the answer is the first time keys == all",
    description=(
        "A vault is an `r × c` grid: `@` is the start, `.` is floor, `#` is wall, a lowercase "
        "letter `a`–`f` is a **key**, and the matching uppercase letter is its **door**. You move "
        "up, down, left or right one cell per step. Walking onto a key picks it up; a door can be "
        "passed only once you hold its key.\n\n"
        "Print the fewest steps needed to hold **every** key in the vault, or `-1` if that is "
        "impossible.\n\n"
        "### Input\nLine 1: `r c`.\nNext `r` lines: the grid. Each key appears at most once, and "
        "the keys present are exactly the first few letters (`a`, `a b`, `a b c`, …).\n\n"
        "### Output\nThe fewest steps, or `-1`."
    ),
    constraints="1 ≤ r, c ≤ 30\nAt most 6 keys\nExactly one `@`",
    hints=[
        "Standing on a cell with key a is a different situation from standing there without it. The state is (cell, set of keys held).",
        "With at most 6 keys, the set is a 6-bit mask: 64 masks per cell, so at most 30 · 30 · 64 states.",
        "BFS over states. Entering a key cell ORs its bit in; entering a door cell is allowed only if its bit is set. Stop when the mask has every bit.",
    ],
    opt=("O(r · c · 2^K)", "O(r · c · 2^K)",
         "Each (cell, mask) state is visited once; K ≤ 6."),
    editorial=(
        "## The one thing this teaches\n**The visited set is over states, not cells.** Plain "
        "grid BFS marks cells. Here you may need to walk back through a cell after picking up a "
        "key — so the same cell must be visitable once per key set.\n\n"
        "## Approach\n```java\nboolean[][][] seen = new boolean[R][C][1 << K];\nq.add(new int[]{sr, sc, 0});\n"
        "seen[sr][sc][0] = true;\nfor (int steps = 0; !q.isEmpty(); steps++)\n    for (int size = q.size(); size-- > 0; ) {\n"
        "        int[] s = q.poll();\n        if (s[2] == ALL) return steps;\n        for (int[] d : DIRS) {\n"
        "            int nr = s[0] + d[0], nc = s[1] + d[1];\n            if (outside || g[nr][nc] == '#') continue;\n"
        "            char ch = g[nr][nc];\n            if (isUpper(ch) && (s[2] >> (ch - 'A') & 1) == 0) continue;   // locked\n"
        "            int mask = isLower(ch) ? s[2] | 1 << (ch - 'a') : s[2];\n"
        "            if (!seen[nr][nc][mask]) { seen[nr][nc][mask] = true; q.add(new int[]{nr, nc, mask}); }\n        }\n    }\n"
        "return -1;\n```\n\n"
        "## Counting the keys\nThe number of keys K is the number of lowercase letters in the grid; "
        "ALL = (1 << K) − 1."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    K = 0
    for i in range(r):
        for j in range(c):
            if g[i][j] == "@":
                si, sj = i, j
            elif "a" <= g[i][j] <= "f":
                K += 1
    ALL = (1 << K) - 1
    seen = set([(si, sj, 0)])
    q = deque([(si, sj, 0)])
    steps = 0
    while q:
        for _ in range(len(q)):
            i, j, mask = q.popleft()
            if mask == ALL:
                return steps
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if not (0 <= ni < r and 0 <= nj < c) or g[ni][nj] == "#":
                    continue
                ch = g[ni][nj]
                if "A" <= ch <= "F" and not mask >> (ord(ch) - 65) & 1:
                    continue
                nm = mask | (1 << (ord(ch) - 97)) if "a" <= ch <= "f" else mask
                if (ni, nj, nm) not in seen:
                    seen.add((ni, nj, nm))
                    q.append((ni, nj, nm))
        steps += 1
    return -1
''',
    java='''
    static int solve(char[][] g) {
        int R = g.length, C = g[0].length, K = 0, sr = 0, sc = 0;
        for (int i = 0; i < R; i++)
            for (int j = 0; j < C; j++) {
                if (g[i][j] == '@') { sr = i; sc = j; }
                else if (g[i][j] >= 'a' && g[i][j] <= 'f') K++;
            }
        int all = (1 << K) - 1;
        boolean[][][] seen = new boolean[R][C][1 << K];
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        ArrayDeque<int[]> q = new ArrayDeque<>();
        q.add(new int[]{sr, sc, 0});
        seen[sr][sc][0] = true;
        for (int steps = 0; !q.isEmpty(); steps++) {
            for (int size = q.size(); size-- > 0; ) {
                int[] s = q.poll();
                if (s[2] == all) return steps;
                for (int[] d : dirs) {
                    int nr = s[0] + d[0], nc = s[1] + d[1];
                    if (nr < 0 || nr >= R || nc < 0 || nc >= C || g[nr][nc] == '#') continue;
                    char ch = g[nr][nc];
                    if (ch >= 'A' && ch <= 'F' && ((s[2] >> (ch - 'A')) & 1) == 0) continue;
                    int mask = (ch >= 'a' && ch <= 'f') ? s[2] | (1 << (ch - 'a')) : s[2];
                    if (!seen[nr][nc][mask]) { seen[nr][nc][mask] = true; q.add(new int[]{nr, nc, mask}); }
                }
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", _grid_case(["@..a.", "###A#", "b...."])),
        ("Example 2", _grid_case(["@#a", ".#.", "..#"])),
    ],
    hidden=[
        ("No keys", _grid_case(["@.."])),
        ("One key next door", _grid_case(["@a"])),
        ("Back and forth", _grid_case(["b.A.@.a"])),
        ("Key behind its own door", _grid_case(["@.A.a"])),
        ("Chain of doors", _grid_case(["@a#.....", ".A#.###.", ".b#B#c..", "#####C##", "d..D...."])),
        ("Six keys", _grid_case(["@.a.#..f", "##.#.##.", "b..A.B.c", "#.###.#.", "d.C..D.e", "..#E..F."])),
        ("Open room", _grid_case(["a......b", "........", "...@....", "........", "c......d"])),
        ("Big maze", _grid_case([
            "@.....#.......................",
            "#####.#.#####.###############.",
            "....#.#.#...#.#.............#.",
            ".##.#.#.#.#.#.#.###########.#.",
            ".#a.#...#.#...#.#.........#.#.",
            ".####A###.#####.#.#######.#.#.",
            "......#...#.....#.#.....#.#.#.",
            "#####.#.###.#####.#.###.#.#.#.",
            "#...#.#...#.#.....#.#b#.#.#.#.",
            "#.#.#.###.#.#.#####.#B#.#.#.#.",
            "#.#...#...#.#.....#.#...#...#.",
            "#.#####.###.#####.#.#####.###.",
            "#.......#c......#.#.......#...",
            "#########C#####.#.#########.#.",
            "d..............D#...........#.",
        ])),
    ],
    expl=[
        "Walk right to key a (3 steps), back through the floor... the fewest steps that end holding both a and b.",
        "The key sits behind walls on every side you can reach: −1.",
    ],
    prereqs=[
        ("bfs", "Breadth-first search over (cell, keys held) states."),
        ("bit_manip", "The set of keys is a bitmask: OR a bit in, test a bit for a door."),
    ],
)


_p(
    "semester-levels", "Which Semester for Each Course", "Easy",
    topics=["Graph", "Topological Sort"], subtopics=["Topological Sort", "Kahn's Algorithm", "Layers"],
    companies=["Amazon", "Google"],
    shape="graph", ret="String",
    todo="Kahn's algorithm one layer at a time: every course whose in-degree is 0 now goes in this semester",
    description=(
        "A degree has `n` courses (0 to `n − 1`) and `m` rules `u v`: course `u` must be finished "
        "in an **earlier** semester than course `v`. Any number of courses can be taken in one "
        "semester. The rules contain no cycle.\n\n"
        "Taking each course as early as possible, print the semester (starting at 1) in which each "
        "course is taken.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v`.\n\n### Output\n`n` numbers on one line: the "
        "semesters of courses 0, 1, …, n − 1."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\nThe rules form no cycle (a repeated rule is possible).",
    hints=[
        "A course with no prerequisites goes in semester 1.",
        "Kahn's algorithm, but drain the queue one layer at a time: every course whose in-degree reaches 0 while processing semester s is taken in semester s + 1.",
        "Equivalently: sem[v] = 1 + max(sem[u]) over its prerequisites u — a longest-path DP in topological order.",
    ],
    opt=("O(n + m)", "O(n + m)",
         "Each course enters the queue once and each rule is relaxed once."),
    editorial=(
        "## The one thing this teaches\n**Kahn's queue, read in layers.** Draining the queue "
        "`size` items at a time — the level-order trick from trees — splits the topological order "
        "into rounds, and the round number is the answer.\n\n"
        "## Approach\n```java\nfor (int v = 0; v < n; v++) if (indeg[v] == 0) { sem[v] = 1; q.add(v); }\n"
        "while (!q.isEmpty()) {\n    int u = q.poll();\n    for (int v : adj[u])\n"
        "        if (--indeg[v] == 0) { sem[v] = sem[u] + 1; q.add(v); }\n}\n```\n\n"
        "## Why `sem[u] + 1` is the maximum\nv's in-degree reaches 0 when its *last* prerequisite "
        "is processed, and Kahn processes courses in non-decreasing semester order — so that last "
        "one has the largest semester."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    sem = [0] * n
    q = deque()
    for v in range(n):
        if indeg[v] == 0:
            sem[v] = 1
            q.append(v)
    while q:
        u = q.popleft()
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                sem[v] = sem[u] + 1
                q.append(v)
    return " ".join(map(str, sem))
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n], sem = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) { sem[v] = 1; q.add(v); }
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj.get(u))
                if (--indeg[v] == 0) { sem[v] = sem[u] + 1; q.add(v); }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(sem[i]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _graph_case(5, [(0, 2), (1, 2), (2, 3), (1, 4)])),
        ("Example 2", _graph_case(3, [])),
    ],
    hidden=[
        ("One course", "1 0\n"),
        ("A chain", _graph_case(5, [(3, 1), (1, 4), (4, 0), (0, 2)])),
        ("A diamond", _graph_case(4, [(0, 1), (0, 2), (1, 3), (2, 3)])),
        ("Repeated rule", _graph_case(3, [(0, 1), (0, 1), (1, 2)])),
        ("Long rule and short rule", _graph_case(5, [(0, 1), (1, 2), (2, 3), (0, 4), (3, 4)])),
        ("Random", _graph_case(300, _rand_dag(300, 900, _Lcg(181)))),
        ("Large", _graph_case(50000, _rand_dag(50000, 120000, _Lcg(182)))),
    ],
    expl=[
        "0 and 1 have no prerequisites (semester 1); 2 and 4 follow them (2); 3 follows 2 (3).",
        "No rules: everything in semester 1.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm: repeatedly take the courses with no unfinished prerequisites."),
        ("indegree", "In-degree counts the prerequisites not yet taken."),
    ],
)


_p(
    "unique-topo-order", "Is There Only One Order?", "Medium",
    topics=["Graph", "Topological Sort"], subtopics=["Topological Sort", "Kahn's Algorithm"],
    companies=["Google", "Amazon"],
    shape="graph", ret="String",
    todo="run Kahn; if the queue ever holds two vertices the order is not unique; if fewer than n come out there is a cycle",
    description=(
        "`n` tasks (0 to `n − 1`) and `m` rules `u v` meaning task `u` must come before task `v`. "
        "Decide which case holds:\n\n"
        "- the rules contain a cycle, so no order exists — print `CYCLE`;\n"
        "- exactly one order satisfies every rule — print it, tasks separated by spaces;\n"
        "- several orders do — print `MANY`.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v`.\n\n### Output\n`CYCLE`, the unique order, or `MANY`."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5",
    hints=[
        "Kahn's algorithm produces *an* order. The question is whether it ever had a choice.",
        "A choice exists exactly when the queue holds two or more vertices at once: either could go next.",
        "Check for a cycle first (fewer than n vertices output) — a cyclic graph has no order at all, even if the queue never widened.",
    ],
    opt=("O(n + m)", "O(n + m)",
         "One run of Kahn's algorithm."),
    editorial=(
        "## The one thing this teaches\n**The queue's width is information.** Kahn's queue "
        "holds exactly the tasks that could go next. Width one at every step means no choice was "
        "ever made; width two means two different orders exist.\n\n"
        "## Approach\n```java\nboolean unique = true;\nwhile (!q.isEmpty()) {\n    if (q.size() > 1) unique = false;\n"
        "    int u = q.poll();\n    order.add(u);\n    for (int v : adj[u]) if (--indeg[v] == 0) q.add(v);\n}\n"
        "if (order.size() < n) return \"CYCLE\";\nreturn unique ? join(order) : \"MANY\";\n```\n\n"
        "## Another way to see it\nThe order is unique exactly when consecutive tasks in it are "
        "always joined by a rule — the order is a Hamiltonian path of the DAG."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)
    order, unique = [], True
    while q:
        if len(q) > 1:
            unique = False
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(order) < n:
        return "CYCLE"
    return " ".join(map(str, order)) if unique else "MANY"
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);
        List<Integer> order = new ArrayList<>();
        boolean unique = true;
        while (!q.isEmpty()) {
            if (q.size() > 1) unique = false;
            int u = q.poll();
            order.add(u);
            for (int v : adj.get(u)) if (--indeg[v] == 0) q.add(v);
        }
        if (order.size() < n) return "CYCLE";
        if (!unique) return "MANY";
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(order.get(i));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", _graph_case(4, [(2, 0), (0, 3), (3, 1), (2, 3)])),
        ("Example 2", _graph_case(3, [(0, 1), (0, 2)])),
    ],
    hidden=[
        ("One task", "1 0\n"),
        ("Two free tasks", "2 0\n"),
        ("A cycle", _graph_case(3, [(0, 1), (1, 2), (2, 0)])),
        ("Cycle with a unique prefix", _graph_case(4, [(0, 1), (1, 2), (2, 3), (3, 2)])),
        ("A self-contained chain", _graph_case(6, [(5, 4), (4, 3), (3, 2), (2, 1), (1, 0)])),
        ("Chain plus shortcut rules", _graph_case(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5), (1, 4)])),
        ("Large unique", _graph_case(40000, [(i, i + 1) for i in range(39999)] + [(i, i + 7) for i in range(0, 39990, 3)])),
        ("Large many", _graph_case(40000, _rand_dag(40000, 80000, _Lcg(191)))),
    ],
    expl=[
        "2 must come first (nothing precedes it), then 0, then 3, then 1 — never a choice.",
        "After 0, either 1 or 2 could go next.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm, and what the queue holds at each step."),
        ("graph_cycle", "Fewer than n tasks output means the rules contain a cycle."),
    ],
)


_p(
    "dag-path-count", "Count the Routes Downhill", "Medium",
    topics=["Graph", "Topological Sort", "Dynamic Programming"], subtopics=["DAG DP", "Topological Sort", "Counting"],
    companies=["Google", "Microsoft"],
    shape="graph", ret="long",
    todo="topological order, ways[0] = 1, then ways[v] += ways[u] for every edge u -> v in that order; answer ways[n-1] mod 1e9+7",
    description=(
        "A ski resort has `n` stations (0 to `n − 1`) and `m` one-way slopes `u v` from station `u` "
        "down to station `v`. Slopes only go downhill, so there are no cycles. Count the different "
        "routes from station `0` to station `n − 1`, modulo `1 000 000 007`. Two routes differ if "
        "they use a different sequence of slopes (two parallel slopes count separately).\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v`.\n\n### Output\nThe number of routes modulo 10⁹ + 7."
    ),
    constraints="2 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\nThe slopes form no cycle.",
    hints=[
        "The number of routes to v is the sum, over slopes u → v, of the number of routes to u.",
        "That sum is only ready once every u pointing at v is final — process stations in topological order.",
        "ways[0] = 1. Reduce modulo 10⁹ + 7 after each addition. The count can be astronomically large without it.",
    ],
    opt=("O(n + m)", "O(n)",
         "One topological sort, then each slope contributes one addition."),
    editorial=(
        "## The one thing this teaches\n**DP on a DAG = DP in topological order.** A DP needs "
        "its dependencies computed first. On a DAG the dependency order *is* a topological order, "
        "so Kahn's algorithm doubles as the DP's loop.\n\n"
        "## Approach\n```java\nlong[] ways = new long[n];\nways[0] = 1;\n"
        "for (int u : topoOrder)                      // Kahn's output\n    for (int v : adj[u])\n"
        "        ways[v] = (ways[v] + ways[u]) % MOD;\nreturn ways[n - 1];\n```\n\n"
        "## Why not DFS with memo?\nIt works too — memoised `count(u)` = Σ count(v). But a 10⁵-long "
        "chain of slopes is 10⁵ frames of recursion. The Kahn loop has no stack at all."
    ),
    py='''
def solve(n, edges):
    MOD = 10**9 + 7
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)
    ways = [0] * n
    ways[0] = 1
    while q:
        u = q.popleft()
        for v in adj[u]:
            ways[v] = (ways[v] + ways[u]) % MOD
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return ways[n - 1]
''',
    java='''
    static long solve(int n, int[][] edges) {
        final long MOD = 1_000_000_007L;
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);
        long[] ways = new long[n];
        ways[0] = 1;
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj.get(u)) {
                ways[v] = (ways[v] + ways[u]) % MOD;
                if (--indeg[v] == 0) q.add(v);
            }
        }
        return ways[n - 1];
    }
''',
    examples=[
        ("Example 1", _graph_case(5, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (1, 4)])),
        ("Example 2", _graph_case(3, [(1, 2)])),
    ],
    hidden=[
        ("Direct slope", _graph_case(2, [(0, 1)])),
        ("Parallel slopes", _graph_case(2, [(0, 1), (0, 1), (0, 1)])),
        ("Unreachable", _graph_case(4, [(0, 1), (2, 3)])),
        ("Other sources", _graph_case(5, [(3, 0), (3, 4), (0, 1), (1, 4), (2, 1)])),
        ("Ladder of diamonds", _graph_case(61, [e for i in range(0, 60, 2) for e in ((i, i + 1), (i, i + 2), (i + 1, i + 2), (i + 1, i + 2))])),
        ("Huge count", _graph_case(200, [(i, j) for i in range(200) for j in range(i + 1, min(200, i + 4))])),
        ("Large", _graph_case(50000, sorted(_rand_dag(50000, 150000, _Lcg(201)) + [(i, i + 1) for i in range(0, 49999, 5)]))),
    ],
    expl=[
        "0→1→3→4, 0→2→3→4 and 0→1→4: three routes.",
        "No slope leaves station 0.",
    ],
    prereqs=[
        ("topo", "A topological order visits every station after all stations that slope into it."),
        ("modulo", "Reduce after each addition to keep the count in a long."),
    ],
)


_p(
    "critical-path-time", "The Project's Critical Path", "Medium",
    topics=["Graph", "Topological Sort", "Dynamic Programming"], subtopics=["DAG DP", "Critical Path", "Scheduling"],
    companies=["Amazon", "Microsoft", "Oracle"],
    shape="arr_graph", ret="long",
    todo="finish[v] = dur[v] + max(finish[u]) over prerequisites u, computed in topological order; the answer is the largest finish",
    description=(
        "A project has `n` tasks; task `i` takes `dur[i]` days. Rules `u v` say task `v` cannot "
        "start until task `u` has finished. With as many workers as you like, independent tasks "
        "run at the same time. The rules contain no cycle.\n\n"
        "Print the fewest days in which the whole project can be finished.\n\n"
        "### Input\nLine 1: `n m`.\nLine 2: `n` durations.\nNext `m` lines: `u v`.\n\n"
        "### Output\nThe minimum total number of days."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\n1 ≤ dur[i] ≤ 10^4\nThe rules form no cycle.",
    hints=[
        "A task starts the moment its *last* prerequisite finishes: start[v] = max(finish[u]).",
        "So finish[v] = dur[v] + max over prerequisites of finish[u] — a longest-path DP, computed in topological order.",
        "The project ends when the last task does: the answer is max(finish). Sum of durations along the longest chain can reach 10⁹ — long is safe.",
    ],
    opt=("O(n + m)", "O(n + m)",
         "One Kahn pass, relaxing each rule once."),
    editorial=(
        "## The one thing this teaches\n**Longest path is easy on a DAG.** On a general graph "
        "the longest path is NP-hard; on a DAG it is one DP in topological order — and it is "
        "exactly the scheduling question \"how long must this take?\". The chain that achieves it "
        "is the **critical path**: delay any task on it and the project slips.\n\n"
        "## Approach\n```java\nlong[] start = new long[n];               // earliest start\n"
        "for (int u : topoOrder) {\n    long fin = start[u] + dur[u];\n    best = Math.max(best, fin);\n"
        "    for (int v : adj[u]) start[v] = Math.max(start[v], fin);\n}\nreturn best;\n```\n\n"
        "## The contrast with `semester-levels`\nThat problem is the same DP with every duration "
        "equal to 1. Different durations are why you cannot simply count layers."
    ),
    py='''
def solve(a, edges):
    n = len(a)
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    start = [0] * n
    q = deque(v for v in range(n) if indeg[v] == 0)
    best = 0
    while q:
        u = q.popleft()
        fin = start[u] + a[u]
        best = max(best, fin)
        for v in adj[u]:
            start[v] = max(start[v], fin)
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return best
''',
    java='''
    static long solve(int[] a, int[][] edges) {
        int n = a.length;
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); indeg[e[1]]++; }
        long[] start = new long[n];
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int v = 0; v < n; v++) if (indeg[v] == 0) q.add(v);
        long best = 0;
        while (!q.isEmpty()) {
            int u = q.poll();
            long fin = start[u] + a[u];
            best = Math.max(best, fin);
            for (int v : adj.get(u)) {
                start[v] = Math.max(start[v], fin);
                if (--indeg[v] == 0) q.add(v);
            }
        }
        return best;
    }
''',
    examples=[
        ("Example 1", "5 5\n3 2 4 1 5\n0 2\n1 2\n2 3\n1 4\n4 3\n"),
        ("Example 2", "3 0\n7 2 9\n"),
    ],
    hidden=[
        ("One task", "1 0\n10\n"),
        ("A chain", "4 3\n1 2 3 4\n0 1\n1 2\n2 3\n"),
        ("Short chain, long task", "4 2\n1 1 1 50\n0 1\n1 2\n"),
        ("Diamond", "4 4\n5 1 9 2\n0 1\n0 2\n1 3\n2 3\n"),
        ("Random", _arr_graph_case(_lcg_ints(211, 300, 1, 10000), _rand_dag(300, 900, _Lcg(212)))),
        ("Large", _arr_graph_case(_lcg_ints(213, 50000, 1, 10000), _rand_dag(50000, 120000, _Lcg(214)))),
    ],
    expl=[
        "Task 2 starts after 0 (3 days) and 1 (2 days), so at day 3 and ends at day 7; task 4 ends at day 7 too; task 3 ends at day 8.",
        "No rules: everything runs at once, and the longest task, 9 days, decides.",
    ],
    prereqs=[
        ("topo", "A topological order finalises each task's start after all of its prerequisites."),
        ("dp", "finish[v] = dur[v] + max(finish of its prerequisites)."),
    ],
)
