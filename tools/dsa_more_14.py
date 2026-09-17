# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 14 — extra practice across graphs, union-find, heaps, design, intervals.
#
#   number-of-enclaves          flood the border's land away, count what is left
#   keys-and-rooms              reachability from room 0 in a directed graph
#   as-far-from-land            multi-source BFS from every land cell at once
#   find-town-judge             in-degree minus out-degree
#   most-stones-removed         each component can be reduced to one stone
#   kth-smallest-sorted-matrix  binary search on the value, counting with a staircase walk
#   seat-reservation-manager    a min-heap of freed seats plus a pointer to never-used ones
#   front-middle-back-queue     two deques kept balanced
#   max-population-year         a difference array over years
# ===========================================================================

_p(
    "number-of-enclaves", "Number of Enclaves", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["Flood Fill", "Grid"], companies=["Google", "Amazon"],
    shape="grid", ret="int", todo="flood fill from every border land cell, erasing it; count the land that remains",
    description=(
        "In a grid of `1` (land) and `0` (sea), you may walk between adjacent land cells (up, down, "
        "left, right) and off the grid from any border cell. Count the land cells from which you "
        "**cannot** walk off the grid.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n### Output\nThe number of enclosed land cells."
    ),
    constraints="1 ≤ r, c ≤ 500",
    hints=[
        "A land cell can escape exactly when it is connected to a land cell on the border.",
        "So flood fill from every border land cell and erase what you reach.",
        "Whatever land is left is enclosed — just count it.",
    ],
    opt=("O(r·c)", "O(r·c)", "Each cell is flooded at most once."),
    editorial=(
        "## The one thing this teaches\n**The same complement as Surrounded Regions.** Checking "
        "each island for a border cell means exploring it anyway; flooding from the border once "
        "removes every island that escapes, and the answer is a count of what survives.\n\n"
        "## Approach\n```java\nfor (each border cell (i, j) with '1') flood(i, j);   // sets reached cells to '0'\n"
        "int count = 0;\nfor (each cell) if (g[i][j] == '1') count++;\n```\n\n"
        "Use an explicit stack for the flood: a 500×500 snake of land recurses 250 000 frames deep."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    st = []
    for i in range(r):
        for j in range(c):
            if (i in (0, r - 1) or j in (0, c - 1)) and g[i][j] == "1":
                g[i][j] = "0"
                st.append((i, j))
    while st:
        x, y = st.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < r and 0 <= ny < c and g[nx][ny] == "1":
                g[nx][ny] = "0"
                st.append((nx, ny))
    return sum(row.count("1") for row in g)
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length;
        ArrayDeque<int[]> st = new ArrayDeque<>();
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if ((i == 0 || j == 0 || i == r - 1 || j == c - 1) && g[i][j] == '1') { g[i][j] = '0'; st.push(new int[]{i, j}); }
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!st.isEmpty()) {
            int[] cur = st.pop();
            for (int[] d : dirs) {
                int x = cur[0] + d[0], y = cur[1] + d[1];
                if (x >= 0 && y >= 0 && x < r && y < c && g[x][y] == '1') { g[x][y] = '0'; st.push(new int[]{x, y}); }
            }
        }
        int count = 0;
        for (char[] row : g) for (char ch : row) if (ch == '1') count++;
        return count;
    }
''',
    examples=[("Example 1", "4 4\n0000\n1010\n0110\n0000\n"), ("Example 2", "4 4\n0110\n0010\n0010\n0000\n")],
    hidden=[
        ("Single cell", "1 1\n1\n"),
        ("Enclosed block", "5 5\n00000\n01110\n01110\n01110\n00000\n"),
        ("Corridor to the edge", "3 5\n00000\n01111\n00000\n"),
    ],
    expl=[
        "The land at (1,2), (2,1) and (2,2) is enclosed; (1,0) is on the border.",
        "All the land connects to the top edge.",
    ],
    prereqs=[
        ("flood_fill", "A flood from the border land erases everything that can escape."),
        ("grid", "Border cells found by their row or column index."),
    ],
)

_p(
    "keys-and-rooms", "Keys and Rooms", "Medium",
    topics=["Graphs"], subtopics=["BFS", "Connected Components"], companies=["Amazon", "Google"],
    shape="graph", ret="String", todo="DFS or BFS from room 0 along key edges; check every room was reached",
    description=(
        "There are `n` rooms; only room `0` is unlocked. Each pair `u v` means room `u` contains "
        "the key to room `v`. Entering a room lets you take all its keys. Can you visit every "
        "room?\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ m ≤ 3000\n0 ≤ u, v < n",
    hints=[
        "A key from u to v is a directed edge u → v.",
        "Visiting every room means every node is reachable from node 0.",
        "One traversal from 0 with a visited array; compare the visited count with n.",
    ],
    opt=("O(n + m)", "O(n + m)", "One traversal."),
    editorial=(
        "## The one thing this teaches\n**Recognising a graph in a story.** Rooms are nodes, keys "
        "are directed edges, and \"can I visit every room\" is \"is every node reachable from 0\". "
        "Once named, it is the most basic traversal there is.\n\n"
        "## Approach\n```java\nboolean[] seen = new boolean[n];\nDeque<Integer> st = new ArrayDeque<>();\n"
        "st.push(0); seen[0] = true; int visited = 1;\nwhile (!st.isEmpty()) {\n    int u = st.pop();\n"
        "    for (int v : keys.get(u)) if (!seen[v]) { seen[v] = true; visited++; st.push(v); }\n}\n"
        "return visited == n ? \"YES\" : \"NO\";\n```\n\n"
        "## Directed, not undirected\nA key to room 3 in room 1 does not mean room 3 opens room 1. "
        "Adding edges both ways answers a different, easier question."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    seen = [False] * n
    seen[0] = True
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                q.append(v)
    return "YES" if all(seen) else "NO"
''',
    java='''
    static String solve(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        boolean[] seen = new boolean[n];
        ArrayDeque<Integer> st = new ArrayDeque<>();
        st.push(0);
        seen[0] = true;
        int visited = 1;
        while (!st.isEmpty()) {
            int u = st.pop();
            for (int v : adj.get(u)) if (!seen[v]) { seen[v] = true; visited++; st.push(v); }
        }
        return visited == n ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "4 3\n0 1\n1 2\n2 3\n"), ("Example 2", "4 4\n0 1\n0 3\n1 0\n3 1\n")],
    hidden=[
        ("Single room", "1 0\n"),
        ("Key points backwards", "2 1\n1 0\n"),
        ("Keys found late", "5 5\n0 4\n4 3\n3 2\n2 1\n1 1\n"),
    ],
    expl=[
        "Each room holds the next key.",
        "No room holds the key to room 2.",
    ],
    prereqs=[
        ("graph_repr", "Keys as directed edges in an adjacency list."),
        ("visited_set", "A traversal from room 0 counting the rooms it reaches."),
    ],
)

_p(
    "as-far-from-land", "As Far From Land as Possible", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["BFS", "Grid"], companies=["Amazon", "Google"],
    shape="grid", ret="int", todo="multi-source BFS from all land cells; the last water cell reached is the answer",
    description=(
        "In a grid of `1` (land) and `0` (water), find the water cell whose distance to the "
        "**nearest** land cell is largest, and print that distance. Distance is Manhattan: moves "
        "up, down, left or right.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n"
        "### Output\nThe maximum distance, or `-1` if there is no land or no water."
    ),
    constraints="1 ≤ r, c ≤ 100",
    hints=[
        "A BFS from each water cell to its nearest land is O((r·c)²).",
        "Start ONE BFS with every land cell in the queue at distance 0.",
        "Each water cell is reached first from its nearest land. The distance of the last cell reached is the answer.",
    ],
    opt=("O(r·c)", "O(r·c)", "One multi-source BFS."),
    editorial=(
        "## The one thing this teaches\n**Multi-source BFS computes nearest-source distances for "
        "everyone at once.** Putting all sources in the queue at distance 0 is equivalent to "
        "adding a super-source connected to each of them; BFS layers then expand outward from "
        "all land simultaneously, and each cell is claimed by its closest land.\n\n"
        "## Approach\n```java\nfor (each land cell) q.add(cell);          // distance 0\n"
        "if (q.isEmpty() || q.size() == r * c) return -1;\nint dist = -1;\nwhile (!q.isEmpty()) {\n"
        "    dist++;\n    for (int k = q.size(); k > 0; k--) {\n        int[] cur = q.poll();\n"
        "        for (each water neighbour) { mark it land; q.add(it); }\n    }\n}\nreturn dist;\n```\n\n"
        "## Counting layers\nThe loop runs once per BFS layer; the first layer is the land itself "
        "(distance 0), so starting the counter at −1 makes the final value the distance of the "
        "farthest layer."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    dist = [[-1] * c for _ in range(r)]
    q = deque()
    for i in range(r):
        for j in range(c):
            if g[i][j] == "1":
                dist[i][j] = 0
                q.append((i, j))
    if not q or len(q) == r * c:
        return -1
    best = 0
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < r and 0 <= ny < c and dist[nx][ny] == -1:
                dist[nx][ny] = dist[x][y] + 1
                best = max(best, dist[nx][ny])
                q.append((nx, ny))
    return best
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length;
        ArrayDeque<int[]> q = new ArrayDeque<>();
        for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) if (g[i][j] == '1') q.add(new int[]{i, j});
        if (q.isEmpty() || q.size() == r * c) return -1;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int dist = -1;
        while (!q.isEmpty()) {
            dist++;
            for (int k = q.size(); k > 0; k--) {
                int[] cur = q.poll();
                for (int[] d : dirs) {
                    int x = cur[0] + d[0], y = cur[1] + d[1];
                    if (x >= 0 && y >= 0 && x < r && y < c && g[x][y] == '0') { g[x][y] = '1'; q.add(new int[]{x, y}); }
                }
            }
        }
        return dist;
    }
''',
    examples=[("Example 1", "3 3\n101\n000\n101\n"), ("Example 2", "3 3\n100\n000\n000\n")],
    hidden=[
        ("No land", "2 2\n00\n00\n"),
        ("No water", "2 2\n11\n11\n"),
        ("Two coasts", "1 7\n1000001\n"),
    ],
    expl=[
        "The centre is 2 from every corner.",
        "The far corner is 4 from the only land.",
    ],
    prereqs=[
        ("bfs", "A multi-source BFS started from every land cell at once."),
        ("grid", "Expanding to up, down, left and right neighbours within bounds."),
    ],
)

_p(
    "find-town-judge", "Find the Town Judge", "Easy",
    topics=["Graphs"], subtopics=["Counting"], companies=["Amazon", "Arista"],
    shape="graph", ret="int", todo="count trusts given and received; the judge receives n − 1 and gives 0",
    description=(
        "People are labelled `1` to `n`. A pair `a b` means `a` trusts `b`. The **town judge**, if "
        "one exists, trusts nobody and is trusted by everybody else. Find the judge.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `a b`.\n\n### Output\nThe judge's label, or `-1`."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ m ≤ 10^4\n1 ≤ a, b ≤ n, a ≠ b, no repeated pairs",
    hints=[
        "No traversal is needed — only how many edges enter and leave each person.",
        "The judge has in-degree n − 1 and out-degree 0.",
        "One score per person: +1 for trust received, −1 for trust given. The judge alone scores n − 1.",
    ],
    opt=("O(n + m)", "O(n)", "One pass over the pairs and one over the people."),
    editorial=(
        "## The one thing this teaches\n**Some graph questions are about degrees, not paths.** "
        "\"Trusted by everyone else and trusts no one\" is a statement about in-degree and "
        "out-degree. No adjacency list is needed.\n\n"
        "## Approach\n```java\nint[] score = new int[n + 1];\nfor (int[] t : trust) { score[t[0]]--; score[t[1]]++; }\n"
        "for (int p = 1; p <= n; p++) if (score[p] == n - 1) return p;\nreturn -1;\n```\n\n"
        "## Why one score is enough\nThe maximum in-degree is n − 1. A score of n − 1 therefore "
        "needs in-degree n − 1 *and* out-degree 0 — any trust given would pull it below. And at "
        "most one person can be trusted by all others while trusting none.\n\n"
        "With `n = 1` and no pairs, the lone person is the judge: score 0 = n − 1."
    ),
    py='''
def solve(n, edges):
    trusts = [0] * (n + 1)
    trusted = [0] * (n + 1)
    for a, b in edges:
        trusts[a] += 1
        trusted[b] += 1
    for p in range(1, n + 1):
        if trusts[p] == 0 and trusted[p] == n - 1:
            return p
    return -1
''',
    java='''
    static int solve(int n, int[][] trust) {
        int[] score = new int[n + 1];
        for (int[] t : trust) { score[t[0]]--; score[t[1]]++; }
        for (int p = 1; p <= n; p++) if (score[p] == n - 1) return p;
        return -1;
    }
''',
    examples=[("Example 1", "2 1\n1 2\n"), ("Example 2", "3 3\n1 3\n2 3\n3 1\n")],
    hidden=[
        ("Alone in town", "1 0\n"),
        ("Not trusted by everyone", "3 1\n1 3\n"),
        ("Four people", "4 5\n1 3\n1 4\n2 3\n2 4\n4 3\n"),
    ],
    expl=[
        "Person 2 is trusted by 1 and trusts nobody.",
        "Person 3 is trusted by both others but trusts person 1.",
    ],
    prereqs=[
        ("graph_repr", "In-degree and out-degree counted directly from the edge list."),
        ("hashing", "A score array indexed by person."),
    ],
)

_p(
    "most-stones-removed", "Most Stones Removed With Same Row or Column", "Medium",
    topics=["Graphs", "Data Structures"], subtopics=["Union-Find", "Connected Components"], companies=["Google", "Meta"],
    shape="pairs", ret="int", todo="union each stone with others sharing a row or column; answer = stones − components",
    description=(
        "Stones sit at distinct integer points. A stone may be removed if another **remaining** "
        "stone shares its row or its column. What is the maximum number of stones you can remove?\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `x y`.\n\n### Output\nThe maximum number of removals."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ x, y ≤ 10^4\nNo two stones share a point.",
    hints=[
        "Connect stones that share a row or column. Removals never cross between connected components.",
        "In a connected component, you can remove stones in reverse BFS order until one is left.",
        "So the answer is n − (number of components). Union-find: union a row node with a column node for each stone.",
    ],
    opt=("O(n · α(n))", "O(n)", "One union per stone, joining its row and its column."),
    editorial=(
        "## The one thing this teaches\n**The answer is a property of components.** Any connected "
        "group of stones can be removed down to exactly one — pick a root, and remove stones "
        "farthest from it first, so each still has a neighbour when removed. Different "
        "components never help each other. So the count is `n − components`.\n\n"
        "## Approach — rows and columns as nodes\nInstead of comparing every pair of stones, make "
        "each row and each column a node, and let each stone union its row with its column:\n\n"
        "```java\nint find(int x) { return parent[x] == x ? x : (parent[x] = find(parent[x])); }\n"
        "for (int[] s : stones) union(s[0], s[1] + 10001);     // columns offset past the rows\n"
        "// components = number of distinct roots among the nodes stones actually use\n```\n\n"
        "Two stones sharing a row share that row node, so they end in one component without ever "
        "being compared. O(n α(n)) instead of O(n²)."
    ),
    py='''
def solve(p):
    n = len(p)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if p[i][0] == p[j][0] or p[i][1] == p[j][1]:
                parent[find(i)] = find(j)
    components = len({find(i) for i in range(n)})
    return n - components
''',
    java='''
    static int[] parent = new int[20002];

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static int solve(int[][] stones) {
        for (int i = 0; i < parent.length; i++) parent[i] = i;
        for (int[] s : stones) parent[find(s[0])] = find(s[1] + 10001);
        Set<Integer> roots = new HashSet<>();
        for (int[] s : stones) roots.add(find(s[0]));
        return stones.length - roots.size();
    }
''',
    examples=[("Example 1", "6\n0 0\n0 1\n1 0\n1 2\n2 1\n2 2\n"), ("Example 2", "5\n0 0\n0 2\n1 1\n2 0\n2 2\n")],
    hidden=[
        ("Single stone", "1\n0 0\n"),
        ("Nothing shares a line", "3\n0 0\n1 1\n2 2\n"),
        ("One long row", "4\n3 0\n3 5\n3 9\n3 10000\n"),
    ],
    expl=[
        "All six stones form one component: five can go.",
        "The four corners form one component and (1, 1) is alone: 5 − 2 = 3 removals.",
    ],
    prereqs=[
        ("union_find", "Unioning rows with columns to form components without comparing stone pairs."),
        ("graph_repr", "Rows and columns as nodes, each stone an edge between its row and its column."),
    ],
)

_p(
    "kth-smallest-sorted-matrix", "K-th Smallest Element in a Sorted Matrix", "Medium",
    topics=["Heap", "Binary Search"], subtopics=["Binary Search", "Priority Queue"], companies=["Google", "Meta", "Amazon"],
    shape="matrix_k", ret="long", todo="binary search the value; count entries ≤ mid with a staircase walk from the bottom-left",
    description=(
        "Every row and every column of an `n × n` matrix is sorted ascending. Find the `k`-th "
        "smallest element (counting duplicates).\n\n"
        "### Input\n- Line 1: `n n k`.\n- Next `n` lines: `n` integers.\n\n### Output\nThe `k`-th smallest value."
    ),
    constraints="1 ≤ n ≤ 300\n-10^9 ≤ value ≤ 10^9\n1 ≤ k ≤ n²",
    hints=[
        "A min-heap seeded with each row's first element, popped k times, works in O(k log n).",
        "Better: binary search on the VALUE. For a candidate v, count the entries ≤ v.",
        "Counting is O(n): start at the bottom-left; if the entry ≤ v, add row+1 entries and move right, else move up.",
    ],
    opt=("O(n log(max − min))", "O(1)", "About 32 binary-search steps over the value range, each an O(n) staircase count."),
    editorial=(
        "## The one thing this teaches\n**Binary search on the answer, with a counting check.** "
        "\"How many entries are ≤ v?\" is monotone in v, and in a matrix sorted both ways it can be "
        "answered in O(n) by walking a staircase. The k-th smallest is the smallest v whose count "
        "reaches k.\n\n"
        "## Approach\n```java\nlong lo = m[0][0], hi = m[n - 1][n - 1];\nwhile (lo < hi) {\n"
        "    long mid = lo + (hi - lo) / 2;          // careful with negatives: use floor division\n"
        "    if (countAtMost(mid) >= k) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n\n"
        "long countAtMost(long v) {\n    long count = 0;\n    int i = n - 1, j = 0;\n"
        "    while (i >= 0 && j < n) {\n        if (m[i][j] <= v) { count += i + 1; j++; }   // whole column above is ≤ v\n"
        "        else i--;\n    }\n    return count;\n}\n```\n\n"
        "## Why the answer is in the matrix\nThe search finds the smallest v with count ≥ k. Any "
        "such minimal v must be a value that occurs — between two consecutive matrix values the "
        "count does not change.\n\n"
        "## Negatives\n`(lo + hi) / 2` rounds toward zero in Java; with negative bounds that can "
        "loop forever. `lo + (hi − lo) / 2` with `hi − lo ≥ 0` always rounds down."
    ),
    py='''
def solve(m, k):
    n = len(m)
    h = [(m[i][0], i, 0) for i in range(n)]
    heapq.heapify(h)
    val = None
    for _ in range(k):
        val, i, j = heapq.heappop(h)
        if j + 1 < len(m[i]):
            heapq.heappush(h, (m[i][j + 1], i, j + 1))
    return val
''',
    java='''
    static long solve(int[][] m, int k) {
        int n = m.length;
        long lo = m[0][0], hi = m[n - 1][n - 1];
        while (lo < hi) {
            long mid = lo + (hi - lo) / 2;
            long count = 0;
            int i = n - 1, j = 0;
            while (i >= 0 && j < n) {
                if (m[i][j] <= mid) { count += i + 1; j++; }
                else i--;
            }
            if (count >= k) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "3 3 8\n1 5 9\n10 11 13\n12 13 15\n"), ("Example 2", "1 1 1\n-5\n")],
    hidden=[
        ("Duplicates count", "2 2 2\n1 2\n1 3\n"),
        ("Last element", "2 2 4\n1 2\n3 4\n"),
        ("Negative values", "3 3 5\n-9 -5 0\n-4 -1 3\n-2 2 8\n"),
        ("Large values", "2 2 3\n-1000000000 0\n0 1000000000\n"),
    ],
    expl=[
        "Sorted: 1 5 9 10 11 12 13 13 15 — the eighth is 13.",
        "One element.",
    ],
    prereqs=[
        ("binary_search", "Binary search over values with a monotone 'how many are at most v' count."),
        ("heap", "The alternative: a min-heap of row fronts, popped k times."),
    ],
)

_p(
    "seat-reservation-manager", "Seat Reservation Manager", "Medium",
    topics=["Heap", "Design"], subtopics=["Priority Queue", "Design"], companies=["Dropbox"],
    shape="ops", ret="String", todo="a min-heap of unreserved seats that were freed, plus the next never-used seat",
    description=(
        "Seats are numbered `1` to `n`, all initially free.\n\n"
        "- `init n` — the first operation.\n"
        "- `reserve` — reserve the **smallest-numbered** free seat and print its number.\n"
        "- `unreserve s` — free seat `s` (which is currently reserved).\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: operations.\n\n### Output\nOne line per `reserve`."
    ),
    constraints="2 ≤ q ≤ 10^5\n1 ≤ n ≤ 10^5\nEvery reserve has a free seat available; every unreserve names a reserved seat.",
    hints=[
        "Putting all n seats in a min-heap up front costs O(n) even if few are ever used.",
        "Seats never used so far are always the numbers above some counter — no heap needed for them.",
        "Keep a min-heap only for seats that were freed. Reserve takes the smaller of the heap's top and the counter.",
    ],
    opt=("O(log n) per operation", "O(n)", "Heap operations only on returned seats."),
    editorial=(
        "## The one thing this teaches\n**Only store what does not follow a pattern.** The free "
        "seats are \"every number above `next`\" plus a scattered set of returned seats. The first "
        "part is one integer; only the scattered part needs a heap.\n\n"
        "## Approach\n```java\nPriorityQueue<Integer> freed = new PriorityQueue<>();\nint next = 1;\n\n"
        "int reserve() {\n    if (!freed.isEmpty()) return freed.poll();   // every freed seat is < next\n"
        "    return next++;\n}\nvoid unreserve(int s) { freed.add(s); }\n```\n\n"
        "## Why the heap's top always wins\nA seat can only be freed after being reserved, and "
        "every reserved seat is below `next`. So whenever the heap is non-empty, its smallest "
        "element is smaller than `next` — no comparison needed."
    ),
    py='''
def solve(ops):
    freed = []
    nxt = 1
    out = []
    for op in ops[1:]:
        if op[0] == "reserve":
            if freed:
                out.append(str(heapq.heappop(freed)))
            else:
                out.append(str(nxt))
                nxt += 1
        else:
            heapq.heappush(freed, int(op[1]))
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        int n = Integer.parseInt(ops[0][1]);
        PriorityQueue<Integer> free = new PriorityQueue<>();
        for (int s = 1; s <= n; s++) free.add(s);
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < ops.length; i++) {
            if (ops[i][0].equals("reserve")) {
                if (sb.length() > 0) sb.append('\\n');
                sb.append(free.poll());
            } else free.add(Integer.parseInt(ops[i][1]));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "9\ninit 5\nreserve\nreserve\nunreserve 2\nreserve\nreserve\nreserve\nreserve\nunreserve 5\n"),
        ("Example 2", "4\ninit 1\nreserve\nunreserve 1\nreserve\n"),
    ],
    hidden=[
        ("Several returns", "8\ninit 6\nreserve\nreserve\nreserve\nunreserve 3\nunreserve 1\nreserve\nreserve\n"),
        ("Return the newest", "6\ninit 3\nreserve\nreserve\nunreserve 2\nreserve\nreserve\n"),
    ],
    expl=[
        "1, 2; seat 2 returns and is taken again; then 3, 4, 5.",
        "The only seat, reserved twice.",
    ],
    prereqs=[
        ("heap", "A min-heap of the seats that were returned."),
        ("design_ds", "A counter for never-used seats replaces most of the heap."),
    ],
)

_p(
    "front-middle-back-queue", "Design Front Middle Back Queue", "Medium",
    topics=["Design", "Data Structures"], subtopics=["Queue", "Design"], companies=["Amazon"],
    shape="ops", ret="String", todo="two deques: left holds the front half, right the back half, with right.size in {left, left+1}",
    description=(
        "Design a queue supporting pushes and pops at the **front**, the **middle** and the "
        "**back**:\n\n"
        "- `pushFront v`, `pushMiddle v`, `pushBack v`.\n"
        "- `popFront`, `popMiddle`, `popBack` — print the removed value, or `-1` if empty.\n\n"
        "`pushMiddle` inserts at index ⌊len / 2⌋, so `[1, 2, 3, 4]` becomes `[1, 2, 9, 3, 4]`. "
        "`popMiddle` removes index ⌊(len − 1) / 2⌋, so from `[1, 2, 3, 4]` it removes `2`.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: operations.\n\n### Output\nOne line per pop."
    ),
    constraints="1 ≤ q ≤ 1000\n1 ≤ v ≤ 10^9",
    hints=[
        "A single list makes the middle operations O(n). Split the queue into two halves.",
        "Keep left and right deques with right.size() equal to left.size() or left.size() + 1.",
        "After every operation, move one element across the boundary if the sizes break that rule.",
    ],
    opt=("O(1) per operation", "O(n)", "Each operation touches the ends of two deques and rebalances by at most one move."),
    editorial=(
        "## The one thing this teaches\n**Split a structure so the hard position becomes an end.** "
        "Deques are O(1) only at their ends. Cutting the queue in two at the middle makes \"the "
        "middle\" the end of one half, and a size invariant decides which half.\n\n"
        "## The invariant\n`right.size()` is `left.size()` or `left.size() + 1`. With that fixed, "
        "the middle positions are always at the boundary:\n"
        "- **pushMiddle** (index ⌊len/2⌋): if the halves are equal it becomes the first of "
        "`right`; if `right` is longer it becomes the last of `left`.\n"
        "- **popMiddle** (index ⌊(len−1)/2⌋): if the halves are equal it is the last of `left`; "
        "otherwise the first of `right`.\n"
        "- The front and back pushes and pops use the outer ends, and may break the invariant.\n\n"
        "## Approach\n```java\nvoid balance() {\n"
        "    if (left.size() > right.size()) right.addFirst(left.pollLast());\n"
        "    else if (right.size() > left.size() + 1) left.addLast(right.pollFirst());\n}\n```\n\n"
        "Every operation ends with `balance()`. Getting the invariant right is the whole problem; "
        "the operations are one line each."
    ),
    py='''
def solve(ops):
    q = []
    out = []
    for op in ops:
        name = op[0]
        if name == "pushFront":
            q.insert(0, int(op[1]))
        elif name == "pushBack":
            q.append(int(op[1]))
        elif name == "pushMiddle":
            q.insert(len(q) // 2, int(op[1]))
        elif name == "popFront":
            out.append(str(q.pop(0)) if q else "-1")
        elif name == "popBack":
            out.append(str(q.pop()) if q else "-1")
        else:
            out.append(str(q.pop((len(q) - 1) // 2)) if q else "-1")
    return "\\n".join(out)
''',
    java='''
    static ArrayDeque<Integer> left = new ArrayDeque<>(), right = new ArrayDeque<>();

    static void balance() {
        if (left.size() > right.size()) right.addFirst(left.pollLast());
        else if (right.size() > left.size() + 1) left.addLast(right.pollFirst());
    }

    static String solve(String[][] ops) {
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            String name = op[0];
            Integer popped = null;
            boolean isPop = name.startsWith("pop");
            switch (name) {
                case "pushFront": left.addFirst(Integer.parseInt(op[1])); break;
                case "pushBack": right.addLast(Integer.parseInt(op[1])); break;
                case "pushMiddle":
                    if (left.size() < right.size()) left.addLast(Integer.parseInt(op[1]));
                    else right.addFirst(Integer.parseInt(op[1]));
                    break;
                case "popFront":
                    if (!left.isEmpty()) popped = left.pollFirst();
                    else if (!right.isEmpty()) popped = right.pollFirst();
                    break;
                case "popBack":
                    if (!right.isEmpty()) popped = right.pollLast();
                    break;
                default:
                    if (left.size() == right.size()) popped = left.pollLast();
                    else popped = right.pollFirst();
            }
            balance();
            if (isPop) {
                if (sb.length() > 0) sb.append('\\n');
                sb.append(popped == null ? -1 : popped);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "9\npushFront 1\npushBack 2\npushMiddle 3\npushMiddle 4\npopFront\npopMiddle\npopMiddle\npopBack\npopFront\n"),
        ("Example 2", "4\npushMiddle 5\npopMiddle\npopFront\npopBack\n"),
    ],
    hidden=[
        ("Middle of an even queue", "6\npushBack 1\npushBack 2\npushBack 3\npushBack 4\npushMiddle 9\npopMiddle\n"),
        ("Alternating ends", "7\npushFront 1\npushFront 2\npushBack 3\npopMiddle\npopMiddle\npopFront\npopBack\n"),
    ],
    expl=[
        "The queue grows [1] → [1,2] → [1,3,2] → [1,4,3,2]. popFront takes 1; popMiddle of [4,3,2] takes 3; popMiddle of [4,2] takes 4; popBack takes 2; then it is empty.",
        "5 is pushed and popped; the queue is then empty.",
    ],
    prereqs=[
        ("queue", "Deques that are O(1) at both ends."),
        ("design_ds", "A size invariant between two halves that makes the middle an end."),
    ],
)

_p(
    "max-population-year", "Maximum Population Year", "Easy",
    topics=["Intervals", "Arrays"], subtopics=["Intervals", "Prefix Sum"], companies=["Amazon"],
    shape="pairs", ret="int", todo="+1 at each birth year, −1 at each death year; prefix-sum over years and take the earliest max",
    description=(
        "Each person lives from their birth year up to, **but not including**, their death year. "
        "Find the earliest year with the largest population.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `birth death`.\n\n### Output\nThe earliest year with maximum population."
    ),
    constraints="1 ≤ n ≤ 100\n1950 ≤ birth < death ≤ 2050",
    hints=[
        "Counting the living for every year and every person is O(years · n) — fine here, but there is a neater way.",
        "Record changes: population rises by 1 at a birth year and falls by 1 at a death year.",
        "A running sum over the years gives each year's population. Keep the first year where it is strictly larger than the best so far.",
    ],
    opt=("O(n + Y)", "O(Y)", "One difference array over the Y = 101 possible years."),
    editorial=(
        "## The one thing this teaches\n**Intervals as +1/−1 events.** A half-open interval "
        "`[birth, death)` adds 1 at `birth` and removes it at `death`. A prefix sum over those "
        "events gives the count at every point — the difference array from Range Addition, with "
        "every update adding 1.\n\n"
        "## Approach\n```java\nint[] delta = new int[102];\nfor (int[] p : people) { delta[p[0] - 1950]++; delta[p[1] - 1950]--; }\n"
        "int run = 0, best = 0, year = 1950;\nfor (int i = 0; i < 101; i++) {\n    run += delta[i];\n"
        "    if (run > best) { best = run; year = 1950 + i; }\n}\n```\n\n"
        "## Half-open\nA person who dies in 1970 is not counted in 1970, so the −1 lands *at* the "
        "death year. And `>` rather than `>=` keeps the earliest year on ties."
    ),
    py='''
def solve(p):
    best_year, best = 1950, 0
    for year in range(1950, 2051):
        alive = sum(1 for b, d in p if b <= year < d)
        if alive > best:
            best, best_year = alive, year
    return best_year
''',
    java='''
    static int solve(int[][] people) {
        int[] delta = new int[102];
        for (int[] p : people) { delta[p[0] - 1950]++; delta[p[1] - 1950]--; }
        int run = 0, best = 0, year = 1950;
        for (int i = 0; i < 101; i++) {
            run += delta[i];
            if (run > best) { best = run; year = 1950 + i; }
        }
        return year;
    }
''',
    examples=[("Example 1", "2\n1993 1999\n2000 2010\n"), ("Example 2", "3\n1950 1961\n1960 1971\n1970 1981\n")],
    hidden=[
        ("Single person", "1\n2000 2001\n"),
        ("Death year excluded", "2\n1990 2000\n2000 2010\n"),
        ("Nested lifetimes", "3\n1950 2050\n1980 1990\n1985 1986\n"),
    ],
    expl=[
        "Nobody overlaps, so 1993, the first year anyone is alive.",
        "1960 has two people alive (the first dies in 1961); so does 1970, but 1960 is earlier.",
    ],
    prereqs=[
        ("intervals", "Half-open lifetimes turned into +1 and −1 events."),
        ("prefix_sum", "A running sum over the events gives the population of each year."),
    ],
)
