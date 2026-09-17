# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 5 — heaps and data-structure design.
#
#   connect-ropes                  always merge the two cheapest (Huffman's shape)
#   furthest-building              spend ladders on the largest climbs, via a min-heap of them
#   trapping-rain-water-ii         a min-heap flood from the border inward
#   parking-system                 the smallest design: state plus operations
#   snapshot-array                 per-index history + binary search, instead of copying
#   leaderboard-design             a map of scores and a sorted multiset of them
#   stock-price-fluctuation        corrections invalidate old answers: lazy heaps or a multiset
# ===========================================================================

_p(
    "connect-ropes", "Connect Ropes at Minimum Cost", "Medium",
    topics=["Heap", "Greedy"], subtopics=["Priority Queue", "Greedy"], companies=["Amazon"],
    shape="arr", ret="long", todo="repeatedly join the two shortest ropes, paying their combined length",
    description=(
        "Joining two ropes of lengths `x` and `y` costs `x + y` and produces one rope of that "
        "length. Join all the ropes into one at the **minimum total cost**.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` rope lengths.\n\n### Output\nThe minimum total cost."
    ),
    constraints="1 ≤ n ≤ 10^4\n1 ≤ length ≤ 10^4",
    hints=[
        "A rope's length is paid again every time a rope containing it is joined. Short ropes should be joined early.",
        "Greedy: always join the two shortest ropes available.",
        "The shortest two change after every join — keep lengths in a min-heap.",
    ],
    opt=("O(n log n)", "O(n)", "n − 1 joins, each two polls and one offer on a heap of at most n ropes."),
    editorial=(
        "## The one thing this teaches\n**Huffman's argument.** Each original rope is paid once "
        "for every join it takes part in, i.e. its *depth* in the tree of joins. Minimising the "
        "total means the longest ropes should be shallowest — so the two shortest should be "
        "joined first, and the argument repeats on the smaller problem.\n\n"
        "## Approach\n```java\nPriorityQueue<Long> pq = new PriorityQueue<>();\n"
        "for (int x : a) pq.offer((long) x);\nlong cost = 0;\nwhile (pq.size() > 1) {\n"
        "    long joined = pq.poll() + pq.poll();\n    cost += joined;\n    pq.offer(joined);\n}\n```\n\n"
        "## Why a heap and not a sort\nAfter one join the new rope may be longer than several "
        "unjoined ones, so a one-time sort is out of date immediately. Re-sorting per join is "
        "O(n² log n); the heap keeps \"the two smallest\" available in O(log n).\n\n"
        "The same structure builds Huffman codes, with letter frequencies in place of lengths."
    ),
    py='''
def solve(a):
    h = list(a)
    heapq.heapify(h)
    cost = 0
    while len(h) > 1:
        joined = heapq.heappop(h) + heapq.heappop(h)
        cost += joined
        heapq.heappush(h, joined)
    return cost
''',
    java='''
    static long solve(int[] a) {
        PriorityQueue<Long> pq = new PriorityQueue<>();
        for (int x : a) pq.offer((long) x);
        long cost = 0;
        while (pq.size() > 1) {
            long joined = pq.poll() + pq.poll();
            cost += joined;
            pq.offer(joined);
        }
        return cost;
    }
''',
    examples=[("Example 1", "4\n4 3 2 6\n"), ("Example 2", "1\n5\n")],
    hidden=[
        ("Three ropes", "3\n1 2 3\n"),
        ("Equal ropes", "5\n1 1 1 1 1\n"),
        ("Two long ropes", "2\n1000 1000\n"),
        ("Sorted order is a trap", "4\n1 2 3 100\n"),
    ],
    expl=[
        "2+3 = 5, then 4+5 = 9, then 6+9 = 15: total 29.",
        "One rope needs no joins.",
    ],
    prereqs=[
        ("heap", "A min-heap keeps the two shortest ropes available after every join."),
        ("greedy", "Joining the two shortest first is optimal by the Huffman exchange argument."),
    ],
)

_p(
    "furthest-building", "Furthest Building You Can Reach", "Medium",
    topics=["Heap", "Greedy"], subtopics=["Priority Queue", "Greedy"], companies=["Google", "Amazon"],
    shape="arr_xy", ret="int", todo="put each climb in a min-heap of ladder climbs; when it overflows, pay the smallest with bricks",
    description=(
        "You walk from building 0 to the right. Moving to a **lower or equal** building is free. "
        "Climbing up by `d` needs either `d` bricks or one ladder. Given `bricks` and `ladders`, "
        "how far can you get?\n\n"
        "### Input\n- Line 1: `n bricks ladders`.\n- Line 2: the `n` building heights.\n\n"
        "### Output\nThe index of the furthest building you can reach."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ height ≤ 10^6\n0 ≤ bricks ≤ 10^9\n0 ≤ ladders ≤ n",
    hints=[
        "A ladder is worth the same whatever it covers, so ladders should cover the largest climbs.",
        "You do not know the largest climbs in advance. Tentatively give every climb a ladder, keeping them in a min-heap.",
        "When there are more climbs than ladders, take back the smallest one and pay for it in bricks. If bricks run out, stop.",
    ],
    opt=("O(n log L)", "O(L)", "The heap holds at most ladders + 1 climbs."),
    editorial=(
        "## The one thing this teaches\n**Decide greedily, and revise the cheapest decision.** "
        "Assigning ladders as climbs arrive is wrong (a big climb may come later), and knowing "
        "the future is not allowed. The heap lets you hand every climb a ladder *provisionally* "
        "and, when you run out, reassign the smallest of them to bricks — which is the choice "
        "you would have made with hindsight.\n\n"
        "## Approach\n```java\nPriorityQueue<Integer> ladderClimbs = new PriorityQueue<>();\n"
        "for (int i = 0; i + 1 < n; i++) {\n    int d = h[i + 1] - h[i];\n    if (d <= 0) continue;\n"
        "    ladderClimbs.offer(d);\n"
        "    if (ladderClimbs.size() > ladders) {\n"
        "        bricks -= ladderClimbs.poll();       // smallest climb goes to bricks\n"
        "        if (bricks < 0) return i;\n    }\n}\nreturn n - 1;\n```\n\n"
        "## Why it is optimal\nAt every point, the heap holds the `ladders` largest climbs so far "
        "and bricks have paid for all the others — the minimum brick spend possible for this "
        "prefix. If even that minimum exceeds the bricks, no strategy gets past building `i`."
    ),
    py='''
def solve(a, x, y):
    bricks, ladders = x, y
    h = []
    for i in range(len(a) - 1):
        d = a[i + 1] - a[i]
        if d <= 0:
            continue
        heapq.heappush(h, d)
        if len(h) > ladders:
            bricks -= heapq.heappop(h)
            if bricks < 0:
                return i
    return len(a) - 1
''',
    java='''
    static int solve(int[] h, long bricks, long ladders) {
        PriorityQueue<Integer> climbs = new PriorityQueue<>();
        for (int i = 0; i + 1 < h.length; i++) {
            int d = h[i + 1] - h[i];
            if (d <= 0) continue;
            climbs.offer(d);
            if (climbs.size() > ladders) {
                bricks -= climbs.poll();
                if (bricks < 0) return i;
            }
        }
        return h.length - 1;
    }
''',
    examples=[("Example 1", "7 5 1\n4 2 7 6 9 14 12\n"), ("Example 2", "9 10 2\n4 12 2 7 3 18 20 3 19\n")],
    hidden=[
        ("No ladders", "4 17 0\n14 3 19 3\n"),
        ("Single building", "1 0 0\n5\n"),
        ("Stuck at the first climb", "5 0 0\n1 2 3 4 5\n"),
        ("Ladder saved for the big climb", "5 3 1\n1 5 1 2 3\n"),
    ],
    expl=[
        "Bricks for 2→7 (5), the ladder for 6→9, and no way up 9→14. Furthest: index 4.",
        "Ladders for the two biggest climbs and bricks for the rest reach index 7.",
    ],
    prereqs=[
        ("heap", "A min-heap of the climbs currently covered by ladders, so the smallest can be given back."),
        ("greedy", "Ladders on the largest climbs seen so far is the cheapest assignment of every prefix."),
    ],
)

_p(
    "trapping-rain-water-ii", "Trapping Rain Water II", "Hard",
    topics=["Heap", "Matrix"], subtopics=["Priority Queue", "BFS"], companies=["Google", "Airbnb"],
    shape="matrix", ret="long", todo="push the border into a min-heap; always expand the lowest wall, filling lower neighbours",
    description=(
        "A grid gives the height of each unit cell. After it rains, how much water is trapped? "
        "Water escapes over the border, so a cell holds water only up to the lowest wall around "
        "every path out.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: `c` heights.\n\n### Output\nThe total volume trapped."
    ),
    constraints="1 ≤ r, c ≤ 200\n0 ≤ height ≤ 2·10^4",
    hints=[
        "The 1-D version uses the max to the left and right. In 2-D a cell has infinitely many escape paths — you need the lowest barrier among all of them.",
        "Border cells hold nothing, and they are the initial walls. Put them in a min-heap by height.",
        "Pop the lowest wall; each unvisited neighbour holds max(0, wall − height) and becomes a wall of height max(wall, height).",
    ],
    opt=("O(rc log(rc))", "O(rc)", "Every cell enters the heap once; Dijkstra-like expansion from the border."),
    editorial=(
        "## The one thing this teaches\n**Flood from the outside, lowest wall first.** Water "
        "leaves through the lowest point of the boundary around it. If you always process the "
        "lowest wall on the current boundary, then the first time you reach a cell, that wall "
        "*is* the lowest barrier between the cell and the outside — the same invariant that makes "
        "Dijkstra correct.\n\n"
        "## Approach\n```java\nPriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> x[0] - y[0]);   // {height, r, c}\n"
        "// push every border cell, mark visited\nlong water = 0;\nwhile (!pq.isEmpty()) {\n"
        "    int[] cur = pq.poll();\n    for (each neighbour (nr, nc) not visited) {\n"
        "        visited[nr][nc] = true;\n"
        "        water += Math.max(0, cur[0] - h[nr][nc]);\n"
        "        pq.offer(new int[]{Math.max(cur[0], h[nr][nc]), nr, nc});\n    }\n}\n```\n\n"
        "## The key line\nThe neighbour is pushed with height `max(wall, own height)`: once filled, "
        "its water surface acts as a wall for the cells beyond it. Pushing its bare height would "
        "let water \"leak\" through a cell that is itself underwater."
    ),
    py='''
def solve(m):
    r, c = len(m), len(m[0])
    seen = [[False] * c for _ in range(r)]
    h = []
    for i in range(r):
        for j in range(c):
            if i == 0 or j == 0 or i == r - 1 or j == c - 1:
                heapq.heappush(h, (m[i][j], i, j))
                seen[i][j] = True
    water = 0
    while h:
        wall, i, j = heapq.heappop(h)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < r and 0 <= nj < c and not seen[ni][nj]:
                seen[ni][nj] = True
                water += max(0, wall - m[ni][nj])
                heapq.heappush(h, (max(wall, m[ni][nj]), ni, nj))
    return water
''',
    java='''
    static long solve(int[][] m) {
        int r = m.length, c = m[0].length;
        boolean[][] seen = new boolean[r][c];
        PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> Integer.compare(x[0], y[0]));
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if (i == 0 || j == 0 || i == r - 1 || j == c - 1) { pq.offer(new int[]{m[i][j], i, j}); seen[i][j] = true; }
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        long water = 0;
        while (!pq.isEmpty()) {
            int[] cur = pq.poll();
            for (int[] d : dirs) {
                int ni = cur[1] + d[0], nj = cur[2] + d[1];
                if (ni < 0 || nj < 0 || ni >= r || nj >= c || seen[ni][nj]) continue;
                seen[ni][nj] = true;
                water += Math.max(0, cur[0] - m[ni][nj]);
                pq.offer(new int[]{Math.max(cur[0], m[ni][nj]), ni, nj});
            }
        }
        return water;
    }
''',
    examples=[
        ("Example 1", "3 6\n1 4 3 1 3 2\n3 2 1 3 2 4\n2 3 3 2 3 1\n"),
        ("Example 2", "5 5\n3 3 3 3 3\n3 2 2 2 3\n3 2 1 2 3\n3 2 2 2 3\n3 3 3 3 3\n"),
    ],
    hidden=[
        ("Single cell", "1 1\n5\n"),
        ("No interior", "2 2\n1 1\n1 1\n"),
        ("A low corner is only diagonal, so no leak", "3 3\n5 5 5\n5 1 5\n5 5 4\n"),
        ("Deep pool", "4 4\n9 9 9 9\n9 1 1 9\n9 1 1 9\n9 9 9 9\n"),
    ],
    expl=[
        "Two pockets hold 1 unit and one holds 2: 4 in total.",
        "The pool fills to height 3: eight cells of depth 1 and the centre of depth 2 = 10.",
    ],
    prereqs=[
        ("heap", "A min-heap of boundary walls, always expanding from the lowest."),
        ("bfs", "Expanding the visited region one neighbour at a time, from the border inward."),
    ],
)

_p(
    "parking-system", "Design a Parking System", "Easy",
    topics=["Design"], subtopics=["Design", "Simulation"], companies=["Amazon"],
    shape="ops", ret="String", todo="keep a counter per car type; each add succeeds only if that counter is positive",
    description=(
        "A parking lot has a fixed number of **big**, **medium** and **small** slots. A car can only "
        "park in a slot of its own type.\n\n"
        "### Input\n- Line 1: `q`, the number of operations.\n"
        "- The first operation is `init big medium small`.\n"
        "- Each later one is `add t`, where `t` is 1 (big), 2 (medium) or 3 (small).\n\n"
        "### Output\nFor each `add`, `true` if the car parked, otherwise `false` — one per line."
    ),
    constraints="2 ≤ q ≤ 1000\n0 ≤ slots of each type ≤ 1000",
    hints=[
        "The whole state is three numbers.",
        "An array indexed by car type avoids three nearly identical branches.",
        "Decrement only when the car actually parks.",
    ],
    opt=("O(1) per operation", "O(1)", "Three counters."),
    editorial=(
        "## The one thing this teaches\n**Design problems are state plus operations.** Before any "
        "clever structure, name the state (three counts) and write each operation as a change to "
        "it. Harder design problems are this with a state that has to answer queries quickly.\n\n"
        "## Approach\n```java\nint[] free = new int[4];                  // index by car type\n"
        "boolean addCar(int type) {\n"
        "    if (free[type] == 0) return false;\n    free[type]--;\n    return true;\n}\n```\n\n"
        "Indexing by type instead of `if (type == 1) … else if (type == 2) …` means the three "
        "cases cannot drift apart when one of them is edited."
    ),
    py='''
def solve(ops):
    free = [0] + [int(x) for x in ops[0][1:4]]
    out = []
    for op in ops[1:]:
        t = int(op[1])
        if free[t] > 0:
            free[t] -= 1
            out.append("true")
        else:
            out.append("false")
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        int[] free = new int[4];
        for (int i = 1; i <= 3; i++) free[i] = Integer.parseInt(ops[0][i]);
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < ops.length; i++) {
            int t = Integer.parseInt(ops[i][1]);
            if (sb.length() > 0) sb.append('\\n');
            if (free[t] > 0) { free[t]--; sb.append("true"); }
            else sb.append("false");
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\ninit 1 1 0\nadd 1\nadd 2\nadd 3\nadd 1\n"),
        ("Example 2", "4\ninit 0 2 0\nadd 2\nadd 2\nadd 2\n"),
    ],
    hidden=[
        ("No slots at all", "2\ninit 0 0 0\nadd 3\n"),
        ("Mixed", "6\ninit 2 0 1\nadd 1\nadd 3\nadd 1\nadd 1\nadd 3\n"),
    ],
    expl=[
        "One big and one medium slot: the small car and the second big car are turned away.",
        "Two medium slots, three medium cars.",
    ],
    prereqs=[
        ("design_ds", "The state is three counters; each operation reads and updates one."),
        ("simulation", "Processing operations in order and reporting each result."),
    ],
)

_p(
    "snapshot-array", "Snapshot Array", "Medium",
    topics=["Design", "Binary Search"], subtopics=["Design", "Binary Search"], companies=["Google", "Uber"],
    shape="ops", ret="String", todo="store (snap id, value) changes per index; get binary-searches the last change at or before the snap",
    description=(
        "Design an array of `n` integers (initially 0) that supports snapshots:\n\n"
        "- `set i v` — set index `i` to `v`.\n"
        "- `snap` — take a snapshot; print its id (0, 1, 2, …).\n"
        "- `get i s` — print the value index `i` had when snapshot `s` was taken.\n\n"
        "### Input\n- Line 1: `q`.\n- The first operation is `init n`; the rest are as above.\n\n"
        "### Output\nOne line for each `snap` and each `get`."
    ),
    constraints="2 ≤ q ≤ 5·10^4\n1 ≤ n ≤ 5·10^4\n0 ≤ v ≤ 10^9\nEvery `get` names a snapshot already taken.",
    hints=[
        "Copying the array on every snap is O(n) per snap — too slow when snaps are frequent.",
        "Store only changes: for each index, a list of (snap id at the time of the set, value).",
        "A get at snapshot s wants the last change with id ≤ s — binary search. Several sets before one snap overwrite each other.",
    ],
    opt=("O(log S) get, O(1) set and snap", "O(n + sets)", "Per-index change lists; a get binary-searches one of them."),
    editorial=(
        "## The one thing this teaches\n**Version history instead of copies.** A snapshot of the "
        "whole array is mostly identical to the previous one. Recording only *changes*, tagged "
        "with the version they belong to, makes a snapshot free and turns reading an old version "
        "into \"find the last change at or before this version\" — a binary search.\n\n"
        "## Approach\n```java\nList<int[]>[] hist;          // per index: {snapId, value}, ids increasing\nint snapId = 0;\n\n"
        "void set(int i, int v) {\n    List<int[]> h = hist[i];\n"
        "    if (!h.isEmpty() && h.get(h.size() - 1)[0] == snapId) h.get(h.size() - 1)[1] = v;\n"
        "    else h.add(new int[]{snapId, v});\n}\nint snap() { return snapId++; }\n"
        "int get(int i, int s) {  // last entry with id <= s, else 0\n    ... binary search ...\n}\n```\n\n"
        "## Two details\n- Sets between the same two snaps collapse into one entry — otherwise a "
        "get must find the *last* of several equal ids.\n"
        "- An index never set before snapshot `s` is 0. Seeding each list with `{-1, 0}` removes "
        "that special case.\n\n"
        "This is the idea behind persistent data structures and database MVCC: readers of an old "
        "version never block, and nothing is copied."
    ),
    py='''
def solve(ops):
    n = int(ops[0][1])
    ids = [[-1] for _ in range(n)]
    vals = [[0] for _ in range(n)]
    snap_id = 0
    out = []
    for op in ops[1:]:
        if op[0] == "set":
            i, v = int(op[1]), int(op[2])
            if ids[i][-1] == snap_id:
                vals[i][-1] = v
            else:
                ids[i].append(snap_id)
                vals[i].append(v)
        elif op[0] == "snap":
            out.append(str(snap_id))
            snap_id += 1
        else:
            i, s = int(op[1]), int(op[2])
            k = bisect_right(ids[i], s) - 1
            out.append(str(vals[i][k]))
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        int n = Integer.parseInt(ops[0][1]);
        List<List<int[]>> hist = new ArrayList<>();
        for (int i = 0; i < n; i++) { List<int[]> h = new ArrayList<>(); h.add(new int[]{-1, 0}); hist.add(h); }
        int snapId = 0;
        StringBuilder sb = new StringBuilder();
        for (int k = 1; k < ops.length; k++) {
            String[] op = ops[k];
            if (op[0].equals("set")) {
                int i = Integer.parseInt(op[1]), v = Integer.parseInt(op[2]);
                List<int[]> h = hist.get(i);
                if (h.get(h.size() - 1)[0] == snapId) h.get(h.size() - 1)[1] = v;
                else h.add(new int[]{snapId, v});
            } else if (op[0].equals("snap")) {
                if (sb.length() > 0) sb.append('\\n');
                sb.append(snapId++);
            } else {
                int i = Integer.parseInt(op[1]), s = Integer.parseInt(op[2]);
                List<int[]> h = hist.get(i);
                int lo = 0, hi = h.size();
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (h.get(mid)[0] <= s) lo = mid + 1; else hi = mid;
                }
                if (sb.length() > 0) sb.append('\\n');
                sb.append(h.get(lo - 1)[1]);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\ninit 3\nset 0 5\nsnap\nset 0 6\nget 0 0\n"),
        ("Example 2", "7\ninit 1\nsnap\nsnap\nset 0 4\nsnap\nget 0 1\nget 0 2\n"),
    ],
    hidden=[
        ("Overwrite before a snap", "6\ninit 2\nset 1 3\nset 1 9\nsnap\nget 1 0\nget 0 0\n"),
        ("Value carried through snaps", "8\ninit 1\nset 0 7\nsnap\nsnap\nsnap\nget 0 2\nset 0 1\nget 0 0\n"),
    ],
    expl=[
        "The snap prints 0; the value at snapshot 0 was 5, even though it is now 6.",
        "Snaps 0, 1 and 2; the 4 was set after snapshot 1, so it appears only in snapshot 2.",
    ],
    prereqs=[
        ("design_ds", "Per-index change lists tagged with the snapshot they belong to."),
        ("binary_search", "Finding the last change at or before a snapshot id."),
    ],
)

_p(
    "leaderboard-design", "Design a Leaderboard", "Medium",
    topics=["Design", "Hashing"], subtopics=["Design", "Hashing", "Sorting"], companies=["Bloomberg", "Wayfair"],
    shape="ops", ret="String", todo="keep player → score and a sorted multiset of scores; top K walks the largest K",
    description=(
        "Design a leaderboard:\n\n"
        "- `add p s` — add `s` to player `p`'s score (a new player starts at 0).\n"
        "- `top k` — print the sum of the `k` highest scores.\n"
        "- `reset p` — remove player `p` from the leaderboard.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: operations.\n\n"
        "### Output\nOne line per `top`."
    ),
    constraints="1 ≤ q ≤ 10^4\n1 ≤ p ≤ 10^4\n1 ≤ s ≤ 100\n`top k` has 1 ≤ k ≤ current player count; `reset` names a current player.",
    hints=[
        "A map from player to score handles add and reset. Top K needs the scores in order.",
        "Sorting every score on each `top` is O(n log n) per query.",
        "Keep a TreeMap from score to how many players have it; top K walks it from the largest.",
    ],
    opt=("O(log n) add/reset, O(K log n) top", "O(n)", "A hash map of players and a sorted multiset of their scores."),
    editorial=(
        "## The one thing this teaches\n**Two structures, kept in step.** The hash map answers "
        "\"what is this player's score?\"; the sorted multiset answers \"what are the largest "
        "scores?\". Neither answers both, so every change updates both — and the bug is always "
        "an update that touches only one.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> score = new HashMap<>();\n"
        "TreeMap<Integer, Integer> counts = new TreeMap<>(Collections.reverseOrder());\n\n"
        "void add(int p, int s) {\n    Integer old = score.get(p);\n"
        "    if (old != null) remove(counts, old);         // take the old score out first\n"
        "    score.put(p, (old == null ? 0 : old) + s);\n    counts.merge(score.get(p), 1, Integer::sum);\n}\n"
        "int top(int k) {\n    int sum = 0;\n"
        "    for (var e : counts.entrySet()) {\n        int take = Math.min(k, e.getValue());\n"
        "        sum += take * e.getKey();\n        if ((k -= take) == 0) break;\n    }\n    return sum;\n}\n```\n\n"
        "## Multiset, not set\nTwo players can share a score. A `TreeSet<Integer>` would store "
        "that score once and `top` would undercount. Mapping each score to how many players hold "
        "it is how a multiset is spelled in Java."
    ),
    py='''
def solve(ops):
    score = {}
    out = []
    for op in ops:
        if op[0] == "add":
            p, s = int(op[1]), int(op[2])
            score[p] = score.get(p, 0) + s
        elif op[0] == "reset":
            score.pop(int(op[1]), None)
        else:
            k = int(op[1])
            out.append(str(sum(sorted(score.values(), reverse=True)[:k])))
    return "\\n".join(out)
''',
    java='''
    static void dec(TreeMap<Integer, Integer> counts, int v) {
        if (counts.merge(v, -1, Integer::sum) == 0) counts.remove(v);
    }

    static String solve(String[][] ops) {
        Map<Integer, Integer> score = new HashMap<>();
        TreeMap<Integer, Integer> counts = new TreeMap<>(Collections.reverseOrder());
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("add")) {
                int p = Integer.parseInt(op[1]), s = Integer.parseInt(op[2]);
                Integer old = score.get(p);
                if (old != null) dec(counts, old);
                int now = (old == null ? 0 : old) + s;
                score.put(p, now);
                counts.merge(now, 1, Integer::sum);
            } else if (op[0].equals("reset")) {
                Integer old = score.remove(Integer.parseInt(op[1]));
                if (old != null) dec(counts, old);
            } else {
                int k = Integer.parseInt(op[1]);
                long sum = 0;
                for (Map.Entry<Integer, Integer> e : counts.entrySet()) {
                    int take = Math.min(k, e.getValue());
                    sum += (long) take * e.getKey();
                    k -= take;
                    if (k == 0) break;
                }
                if (sb.length() > 0) sb.append('\\n');
                sb.append(sum);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "10\nadd 1 73\nadd 2 56\nadd 3 39\nadd 4 51\nadd 5 4\ntop 1\nreset 1\nreset 2\nadd 2 51\ntop 3\n"),
        ("Example 2", "6\nadd 1 5\nadd 2 5\nadd 3 5\ntop 2\nadd 3 1\ntop 1\n"),
    ],
    hidden=[
        ("Scores accumulate", "3\nadd 7 10\nadd 7 5\ntop 1\n"),
        ("Reset then re-add", "7\nadd 1 50\nadd 2 40\nreset 1\ntop 1\nadd 1 10\ntop 2\ntop 1\n"),
    ],
    expl=[
        "Top 1 is 73. After the resets, player 2 returns with 51: the top three are 51, 51 and 39 = 141.",
        "Three players tie on 5 — a set of scores would count that 5 once. Then player 3 leads with 6.",
    ],
    prereqs=[
        ("design_ds", "A hash map and a sorted multiset that every operation keeps consistent."),
        ("hashing", "Player scores looked up and updated in O(1)."),
    ],
)

_p(
    "stock-price-fluctuation", "Stock Price Fluctuation", "Medium",
    topics=["Design", "Heap"], subtopics=["Design", "Priority Queue"], companies=["Google", "Amazon"],
    shape="ops", ret="String", todo="map timestamp → price, track the latest timestamp, keep a sorted multiset of prices",
    description=(
        "Prices arrive as `update t p` records, **out of order**, and a record for a timestamp "
        "already seen *corrects* the earlier price.\n\n"
        "- `update t p` — the price at time `t` is `p`.\n"
        "- `current` — print the price at the latest timestamp.\n"
        "- `maximum` / `minimum` — print the highest / lowest price across all timestamps.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: operations.\n\n"
        "### Output\nOne line per query."
    ),
    constraints="1 ≤ q ≤ 10^5\n1 ≤ t, p ≤ 10^9\nEvery query comes after at least one update.",
    hints=[
        "A map from timestamp to price handles corrections; the latest timestamp is a running maximum.",
        "The maximum price must forget a price that was corrected away.",
        "Either keep a TreeMap of price → count (decrement the old price on a correction), or two heaps of (price, timestamp) and discard stale tops lazily.",
    ],
    opt=("O(log n) per operation", "O(n)", "A hash map of prices by time and a sorted multiset of current prices."),
    editorial=(
        "## The one thing this teaches\n**Corrections invalidate cached answers.** Without "
        "corrections a running max would do. With them, the old maximum can disappear, so the "
        "structure must support *removing* a value — a multiset, or a heap with lazy deletion.\n\n"
        "## Approach — a multiset\n```java\nMap<Integer, Integer> priceAt = new HashMap<>();\n"
        "TreeMap<Integer, Integer> prices = new TreeMap<>();     // price -> how many timestamps\nint latest = 0;\n\n"
        "void update(int t, int p) {\n    Integer old = priceAt.put(t, p);\n"
        "    if (old != null && prices.merge(old, -1, Integer::sum) == 0) prices.remove(old);\n"
        "    prices.merge(p, 1, Integer::sum);\n    latest = Math.max(latest, t);\n}\n"
        "int current() { return priceAt.get(latest); }\nint maximum() { return prices.lastKey(); }\n```\n\n"
        "## Approach — lazy heaps\nPush `(price, t)` into a max-heap on every update. When asked "
        "for the maximum, pop while the top's price no longer equals `priceAt.get(t)` — that entry "
        "was corrected. Each pushed entry is popped at most once, so it is O(log n) amortised, "
        "and it is the same lazy deletion as in \"first unique number\".\n\n"
        "## Counts matter\nTwo timestamps can share a price. Removing the price entirely when one "
        "of them is corrected would lose the other — the count is what prevents that."
    ),
    py='''
def solve(ops):
    price_at = {}
    latest = 0
    hi, lo = [], []
    out = []
    for op in ops:
        if op[0] == "update":
            t, p = int(op[1]), int(op[2])
            price_at[t] = p
            latest = max(latest, t)
            heapq.heappush(hi, (-p, t))
            heapq.heappush(lo, (p, t))
        elif op[0] == "current":
            out.append(str(price_at[latest]))
        elif op[0] == "maximum":
            while price_at[hi[0][1]] != -hi[0][0]:
                heapq.heappop(hi)
            out.append(str(-hi[0][0]))
        else:
            while price_at[lo[0][1]] != lo[0][0]:
                heapq.heappop(lo)
            out.append(str(lo[0][0]))
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        Map<Integer, Integer> priceAt = new HashMap<>();
        TreeMap<Integer, Integer> prices = new TreeMap<>();
        int latest = 0;
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            String line;
            if (op[0].equals("update")) {
                int t = Integer.parseInt(op[1]), p = Integer.parseInt(op[2]);
                Integer old = priceAt.put(t, p);
                if (old != null && prices.merge(old, -1, Integer::sum) == 0) prices.remove(old);
                prices.merge(p, 1, Integer::sum);
                latest = Math.max(latest, t);
                continue;
            } else if (op[0].equals("current")) line = String.valueOf(priceAt.get(latest));
            else if (op[0].equals("maximum")) line = String.valueOf(prices.lastKey());
            else line = String.valueOf(prices.firstKey());
            if (sb.length() > 0) sb.append('\\n');
            sb.append(line);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "8\nupdate 1 10\nupdate 2 5\ncurrent\nmaximum\nupdate 1 3\nmaximum\nupdate 4 2\nminimum\n"),
        ("Example 2", "5\nupdate 5 100\nupdate 3 50\ncurrent\nupdate 5 1\ncurrent\n"),
    ],
    hidden=[
        ("Shared price survives a correction", "7\nupdate 1 7\nupdate 2 7\nupdate 1 2\nmaximum\nminimum\nupdate 2 1\nmaximum\n"),
        ("Same record twice", "5\nupdate 1 7\nupdate 1 7\nminimum\nmaximum\ncurrent\n"),
    ],
    expl=[
        "Latest is time 2 (price 5); max 10. Correcting time 1 to 3 makes the max 5. Then time 4 adds 2, the new minimum.",
        "Time 5 is latest even though it arrived first; its correction to 1 changes `current`.",
    ],
    prereqs=[
        ("design_ds", "A timestamp map plus a structure of current prices that supports removal."),
        ("heap", "Max- and min-heaps with lazy deletion of corrected entries."),
    ],
)
