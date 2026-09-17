# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 25 — design, heaps, traversal, backtracking and strings.
#
#   exam-room                        only the ends and the midpoints of gaps can be best
#   single-threaded-cpu              sort by arrival; a heap of ready tasks ordered by length
#   all-paths-source-target          DFS on a DAG needs no visited set, only a path
#   number-of-closed-islands         sink everything touching the border, then count
#   letter-case-permutation          two branches per letter, one per digit
#   combination-sum-iii              choose increasing digits; prune when the sum overshoots
#   meeting-rooms-iii                one heap of free rooms, one of busy rooms by end time
#   min-deletions-unique-frequencies lower each duplicate frequency to the next unused value
#   longest-happy-prefix             the KMP failure function's last value
#   four-sum-count                   sort, fix two, two-pointer the rest, skip duplicates
# ===========================================================================

_p(
    "exam-room", "Exam Room", "Medium",
    topics=["Design", "Ordered Set"], subtopics=["Gaps Between Occupied Seats"], companies=["Google"],
    shape="ops", ret="String", todo="keep occupied seats in a sorted set; the best seat is seat 0, seat n − 1, or the midpoint of the widest gap",
    description=(
        "An exam room has seats `0` to `n − 1` in a row. When a student enters, they sit in the "
        "seat that **maximises the distance to the nearest student**; ties go to the lowest seat "
        "number. An empty room seats the student at `0`. Students may also leave.\n\n"
        "### Input\n- Line 1: `q`, the number of operations.\n- Next `q` lines, one of:\n"
        "  - `init n` — always the first operation;\n  - `seat` — print the chosen seat;\n"
        "  - `leave p` — the student in seat `p` leaves (it is occupied).\n\n"
        "### Output\nOne line per `seat`: the seat number."
    ),
    constraints="1 ≤ n ≤ 10^9\n1 ≤ q ≤ 10^4\nseat is only called when a seat is free",
    hints=[
        "n can be 10^9 — you cannot test every seat.",
        "Between two neighbouring students at a and b, the best seat is (a + b) / 2, at distance (b − a) / 2.",
        "Also consider seat 0 (distance first occupied) and seat n − 1 (distance n − 1 − last). Scan the occupied seats in order and keep the strictly best.",
    ],
    opt=("O(k) per seat, O(log k) per leave", "O(k)", "k is the number of seated students; a scan over the sorted set per seat."),
    editorial=(
        "## The one thing this teaches\n**Reduce infinitely many choices to a few candidates.** "
        "Only three kinds of seat can be optimal: the first seat, the last seat, and the midpoint "
        "of a gap. Everything else in a gap is closer to one of its ends.\n\n"
        "## Approach\n```java\nTreeSet<Long> taken = new TreeSet<>();\n\nlong seat() {\n"
        "    if (taken.isEmpty()) { taken.add(0L); return 0; }\n"
        "    long best = 0, bestDist = taken.first();          // seat 0\n    Long prev = null;\n"
        "    for (long s : taken) {\n        if (prev != null && (s - prev) / 2 > bestDist) { bestDist = (s - prev) / 2; best = prev + bestDist; }\n"
        "        prev = s;\n    }\n"
        "    if (n - 1 - taken.last() > bestDist) best = n - 1;  // seat n − 1\n"
        "    taken.add(best);\n    return best;\n}\n```\n\n"
        "## Ties go left automatically\nThe scan visits candidates from left to right and only "
        "replaces the best on a **strictly** larger distance, so the lowest seat wins every tie.\n\n"
        "## Faster seating\nA priority queue of gaps, ordered by (distance, left end), makes "
        "`seat` O(log k) — at the cost of invalidating gaps when someone leaves, which needs "
        "lazy deletion or a second ordered structure."
    ),
    py='''
def solve(ops):
    import bisect
    n = 0
    taken = []
    out = []
    for op in ops:
        if op[0] == "init":
            n = int(op[1])
        elif op[0] == "leave":
            taken.remove(int(op[1]))
        else:
            if not taken:
                choice = 0
            else:
                candidates = {0, n - 1} | {(taken[i] + taken[i + 1]) // 2 for i in range(len(taken) - 1)}

                def nearest(p):
                    i = bisect.bisect_left(taken, p)
                    gaps = []
                    if i < len(taken):
                        gaps.append(taken[i] - p)
                    if i > 0:
                        gaps.append(p - taken[i - 1])
                    return min(gaps)

                choice = min(candidates, key=lambda p: (-nearest(p), p))
            bisect.insort(taken, choice)
            out.append(str(choice))
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        long n = 0;
        TreeSet<Long> taken = new TreeSet<>();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("init")) n = Long.parseLong(op[1]);
            else if (op[0].equals("leave")) taken.remove(Long.parseLong(op[1]));
            else {
                long best = 0;
                if (!taken.isEmpty()) {
                    long bestDist = taken.first();
                    Long prev = null;
                    for (long s : taken) {
                        if (prev != null && (s - prev) / 2 > bestDist) { bestDist = (s - prev) / 2; best = prev + bestDist; }
                        prev = s;
                    }
                    if (n - 1 - taken.last() > bestDist) best = n - 1;
                }
                taken.add(best);
                if (sb.length() > 0) sb.append('\\n');
                sb.append(best);
            }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "7\ninit 10\nseat\nseat\nseat\nseat\nleave 4\nseat\n")],
    hidden=[
        ("One seat", "2\ninit 1\nseat\n"),
        ("Leaving frees the start", "6\ninit 5\nseat\nseat\nseat\nleave 0\nseat\n"),
        ("Huge room", "5\ninit 1000000000\nseat\nseat\nseat\nseat\n"),
        ("Fill a small room", "6\ninit 4\nseat\nseat\nseat\nseat\nleave 1\n"),
        ("Tie goes to the lower seat", "5\ninit 6\nseat\nseat\nseat\nseat\n"),
    ],
    expl=[
        "0, then the far end 9, then 4 (4 seats from the nearest student), then 2 (a tie with 6, broken downward). After 4 leaves, the gap 2–9 has midpoint 5 at distance 3.",
    ],
    prereqs=[
        ("design_ds", "A class-like set of operations sharing one ordered structure."),
        ("bst", "An ordered set (TreeSet) iterated in increasing order."),
    ],
)

_p(
    "single-threaded-cpu", "Single-Threaded CPU", "Medium",
    topics=["Heaps", "Sorting", "Simulation"], subtopics=["Event Simulation"], companies=["Google", "Amazon"],
    shape="pairs", ret="String", todo="sort tasks by arrival; move arrived tasks into a heap keyed by (duration, index); if the heap is empty, jump the clock to the next arrival",
    description=(
        "Task `i` becomes available at time `arrive` and needs `duration` units of CPU. The CPU "
        "runs one task at a time to completion. Whenever it is free, it picks, among the "
        "available tasks, the one with the **shortest duration** (ties: the smallest index). If no "
        "task is available, it waits for the next arrival.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `arrive duration` for task `i = 0..n−1`.\n\n"
        "### Output\nThe task indices in the order they run, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ arrive, duration ≤ 10^9",
    hints=[
        "Tasks arrive over time, so process them in order of arrival — but the original indices must be kept.",
        "Maintain a heap of tasks that have arrived, ordered by (duration, index).",
        "Loop: push every task with arrive ≤ time. If the heap is empty, set time to the next arrival. Otherwise pop one, run it, and add its duration to time — which can exceed an int.",
    ],
    opt=("O(n log n)", "O(n)", "A sort, then each task is pushed and popped once."),
    editorial=(
        "## The one thing this teaches\n**Event simulation: a sorted stream of arrivals feeding a "
        "priority queue of ready work.** The same shape schedules processes, orders deliveries "
        "and merges timelines — sort by when things appear, heap by which to handle first.\n\n"
        "## Approach\n```java\nInteger[] order = indices sorted by arrive;\n"
        "PriorityQueue<Integer> ready = new PriorityQueue<>((x, y) ->\n"
        "    t[x][1] != t[y][1] ? Integer.compare(t[x][1], t[y][1]) : Integer.compare(x, y));\n"
        "long time = 0;\nint next = 0;\nwhile (result.size() < n) {\n"
        "    while (next < n && t[order[next]][0] <= time) ready.add(order[next++]);\n"
        "    if (ready.isEmpty()) { time = t[order[next]][0]; continue; }   // idle: jump ahead\n"
        "    int task = ready.poll();\n    time += t[task][1];\n    result.add(task);\n}\n```\n\n"
        "## Why jump instead of ticking\nTimes reach 10^9. Advancing the clock one unit at a time "
        "while idle would take that many steps; jumping to the next arrival costs O(1).\n\n"
        "## Use long for the clock\n10^5 tasks of duration 10^9 finish at 10^14."
    ),
    py='''
def solve(p):
    remaining = set(range(len(p)))
    time = 0
    order = []
    while remaining:
        ready = [i for i in remaining if p[i][0] <= time]
        if not ready:
            time = min(p[i][0] for i in remaining)
            continue
        task = min(ready, key=lambda i: (p[i][1], i))
        time += p[task][1]
        order.append(task)
        remaining.discard(task)
    return " ".join(map(str, order))
''',
    java='''
    static String solve(int[][] t) {
        int n = t.length;
        Integer[] order = new Integer[n];
        for (int i = 0; i < n; i++) order[i] = i;
        Arrays.sort(order, (x, y) -> Integer.compare(t[x][0], t[y][0]));
        PriorityQueue<Integer> ready = new PriorityQueue<>((x, y) ->
            t[x][1] != t[y][1] ? Integer.compare(t[x][1], t[y][1]) : Integer.compare(x, y));
        long time = 0;
        int next = 0, done = 0;
        StringBuilder sb = new StringBuilder();
        while (done < n) {
            while (next < n && t[order[next]][0] <= time) ready.add(order[next++]);
            if (ready.isEmpty()) { time = t[order[next]][0]; continue; }
            int task = ready.poll();
            time += t[task][1];
            if (done++ > 0) sb.append(' ');
            sb.append(task);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4\n1 2\n2 4\n3 2\n4 1\n"),
        ("Example 2", "5\n7 10\n7 12\n7 5\n7 4\n7 2\n"),
    ],
    hidden=[
        ("One task", "1\n5 5\n"),
        ("Idle gap", "3\n1 1\n10 1\n5 1\n"),
        ("Equal durations", "3\n1 5\n1 5\n1 5\n"),
        ("Clock past an int", "4\n1 1000000000\n1 1000000000\n1 1000000000\n1000000000 1\n"),
    ],
    expl=[
        "At 1 only task 0 exists; it ends at 3. Tasks 1 and 2 are waiting; 2 is shorter. At 5, task 3 (duration 1) beats task 1.",
        "All arrive together, so they run shortest first: 4 (2), 3 (4), 2 (5), 0 (10), 1 (12).",
    ],
    prereqs=[
        ("heap", "A priority queue with a two-key comparator."),
        ("sorting", "Sorting indices by arrival while keeping the original numbering."),
    ],
)

_p(
    "all-paths-source-target", "All Paths from Source to Target", "Medium",
    topics=["Graphs", "Backtracking", "DFS"], subtopics=["Path Enumeration"], companies=["Amazon", "Google"],
    shape="graph", ret="String", todo="DFS from 0 carrying the current path; visit neighbours in increasing order and record the path on reaching n − 1",
    description=(
        "A directed **acyclic** graph has nodes `0` to `n − 1`. Print every path from node `0` to "
        "node `n − 1`, one per line, as node numbers separated by spaces. Order the paths "
        "lexicographically as sequences of integers. Print `NONE` if there is no path.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v`, an edge from `u` to `v`.\n\n"
        "### Output\nThe paths, or `NONE`."
    ),
    constraints="1 ≤ n ≤ 15\nNo duplicate edges, no cycles",
    hints=[
        "There can be exponentially many paths, so the output size — not the algorithm — sets the cost.",
        "In a DAG, a path can never revisit a node, so the DFS needs no visited set: just the current path.",
        "Sort each adjacency list. A DFS that tries smaller neighbours first produces the paths already in lexicographic order.",
    ],
    opt=("O(2^n · n)", "O(n)", "Up to 2^(n−2) paths, each of length up to n, plus a path-sized stack."),
    editorial=(
        "## The one thing this teaches\n**Enumerate with backtracking: extend, recurse, undo.** "
        "Listing all paths is a search tree whose leaves are the answers. In a DAG no node can "
        "repeat on a path, so the usual visited set is unnecessary — and would even be wrong, "
        "since other paths may pass through the same node.\n\n"
        "## Approach\n```java\nvoid dfs(int u, List<Integer> path) {\n"
        "    if (u == n - 1) { output(path); return; }\n"
        "    for (int v : adj[u]) {          // sorted ascending\n"
        "        path.add(v);\n        dfs(v, path);\n        path.remove(path.size() - 1);   // undo\n    }\n}\n"
        "path = [0]; dfs(0, path);\n```\n\n"
        "## Why sorted adjacency gives sorted output\nTwo paths first differ at some position; "
        "the DFS reaches that branching node once and tries the smaller neighbour first, so "
        "every path through it is printed earlier.\n\n"
        "## Compare numbers, not strings\nAs strings, `0 10 11` sorts before `0 2 11`. As "
        "integer sequences, 2 < 10, so `0 2 11` comes first."
    ),
    py='''
def solve(n, edges):
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
    paths = []
    stack = [(0, (0,))]
    while stack:
        u, path = stack.pop()
        if u == n - 1:
            paths.append(path)
            continue
        for v in out[u]:
            stack.append((v, path + (v,)))
    if not paths:
        return "NONE"
    return "\\n".join(" ".join(map(str, p)) for p in sorted(paths))
''',
    java='''
    static List<List<Integer>> adj;
    static StringBuilder sb;
    static int target;

    static void dfs(int u, List<Integer> path) {
        if (u == target) {
            if (sb.length() > 0) sb.append('\\n');
            for (int i = 0; i < path.size(); i++) { if (i > 0) sb.append(' '); sb.append(path.get(i)); }
            return;
        }
        for (int v : adj.get(u)) {
            path.add(v);
            dfs(v, path);
            path.remove(path.size() - 1);
        }
    }

    static String solve(int n, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        for (List<Integer> l : adj) Collections.sort(l);
        sb = new StringBuilder();
        target = n - 1;
        List<Integer> path = new ArrayList<>();
        path.add(0);
        dfs(0, path);
        return sb.length() == 0 ? "NONE" : sb.toString();
    }
''',
    examples=[
        ("Example 1", "4 4\n0 1\n0 2\n1 3\n2 3\n"),
        ("Example 2", "5 8\n0 4\n0 3\n0 1\n1 3\n1 2\n1 4\n2 3\n3 4\n"),
    ],
    hidden=[
        ("Single node", "1 0\n"),
        ("Target unreachable", "3 1\n0 1\n"),
        ("Numeric, not string, order", "12 4\n0 10\n0 2\n2 11\n10 11\n"),
        ("Direct edge only", "2 1\n0 1\n"),
        ("Layered", "5 6\n0 1\n0 2\n1 3\n2 3\n1 4\n3 4\n"),
    ],
    expl=[
        "0 → 1 → 3 and 0 → 2 → 3.",
        "Five paths; 0 1 2 3 4 comes before 0 1 3 4 because 2 < 3 at the third position.",
    ],
    prereqs=[
        ("backtracking", "Extending a path, recursing, and removing the last node on return."),
        ("graph_repr", "Adjacency lists, sorted to fix the output order."),
    ],
)

_p(
    "number-of-closed-islands", "Number of Closed Islands", "Medium",
    topics=["Graphs", "Matrix"], subtopics=["Flood Fill", "Border Elimination"], companies=["Google", "Amazon"],
    shape="grid", ret="int", todo="flood-fill all land connected to the border into water first; then count the remaining land components",
    description=(
        "A grid has land `L` and water `W`. An island is a group of land cells connected "
        "horizontally or vertically. An island is **closed** if none of its cells lies on the "
        "grid's border. Print the number of closed islands.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: the grid rows.\n\n"
        "### Output\nThe number of closed islands."
    ),
    constraints="1 ≤ r, c ≤ 100",
    hints=[
        "Counting islands is flood fill. The extra condition is about the border.",
        "Any island touching the border is disqualified in full — so remove those first.",
        "Flood-fill from every border land cell, turning it to water. Every island left afterwards is closed; count them with ordinary flood fill.",
    ],
    opt=("O(r · c)", "O(r · c)", "Every cell is filled at most once across both phases; the stack may hold the whole grid."),
    editorial=(
        "## The one thing this teaches\n**Remove what disqualifies, then count what remains.** "
        "Checking \"does this island touch the border\" during each fill works, but a cleaner "
        "shape is two phases: sink every border-connected island, then count islands normally.\n\n"
        "## Approach\n```java\nfor (every border cell (i, j)) if (g[i][j] == 'L') sink(i, j);   // phase 1\n"
        "int closed = 0;\nfor (every cell (i, j)) if (g[i][j] == 'L') { sink(i, j); closed++; }   // phase 2\n\n"
        "void sink(int i, int j) {  // iterative flood fill turning L into W\n"
        "    stack.push(i, j); g[i][j] = 'W';\n    while (!stack.isEmpty()) {\n"
        "        pop (x, y);\n        for each 4-neighbour (a, b) inside with g[a][b] == 'L': g[a][b] = 'W'; push (a, b);\n    }\n}\n```\n\n"
        "## The same trick elsewhere\nSurrounded Regions and Number of Enclaves use exactly this "
        "border-first pass. Anything that must *not* reach the edge is easiest to find by "
        "starting from the edge.\n\n"
        "## Diagonals do not connect\nTwo land cells touching only at a corner are separate "
        "islands."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    seen = set()
    closed = 0
    for i in range(r):
        for j in range(c):
            if g[i][j] != "L" or (i, j) in seen:
                continue
            seen.add((i, j))
            stack = [(i, j)]
            touches = False
            while stack:
                x, y = stack.pop()
                if x in (0, r - 1) or y in (0, c - 1):
                    touches = True
                for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= a < r and 0 <= b < c and g[a][b] == "L" and (a, b) not in seen:
                        seen.add((a, b))
                        stack.append((a, b))
            if not touches:
                closed += 1
    return closed
''',
    java='''
    static void sink(char[][] g, int si, int sj) {
        int r = g.length, c = g[0].length;
        ArrayDeque<int[]> st = new ArrayDeque<>();
        g[si][sj] = 'W';
        st.push(new int[]{si, sj});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!st.isEmpty()) {
            int[] cur = st.pop();
            for (int[] d : dirs) {
                int a = cur[0] + d[0], b = cur[1] + d[1];
                if (a < 0 || b < 0 || a >= r || b >= c || g[a][b] != 'L') continue;
                g[a][b] = 'W';
                st.push(new int[]{a, b});
            }
        }
    }

    static int solve(char[][] g) {
        int r = g.length, c = g[0].length;
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if ((i == 0 || j == 0 || i == r - 1 || j == c - 1) && g[i][j] == 'L') sink(g, i, j);
        int closed = 0;
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++)
                if (g[i][j] == 'L') { sink(g, i, j); closed++; }
        return closed;
    }
''',
    examples=[
        ("Example 1", "5 7\nWWWWWWW\nWLLWLLW\nWLLWWWW\nWWWWLLL\nWWWWWWW\n"),
        ("Example 2", "3 3\nLLL\nLWL\nLLL\n"),
    ],
    hidden=[
        ("Single land cell", "1 1\nL\n"),
        ("One enclosed cell", "3 3\nWWW\nWLW\nWWW\n"),
        ("Four separate islands", "5 5\nWWWWW\nWLWLW\nWWWWW\nWLWLW\nWWWWW\n"),
        ("Diagonal cells are separate", "4 4\nWWWW\nWLWW\nWWLW\nWWWW\n"),
        ("Long arm reaches the border", "5 5\nWWWWW\nWLLLW\nWWWLW\nWLWLL\nWWWWW\n"),
    ],
    expl=[
        "The 2 × 2 block and the pair in row 1 are closed; the island in row 3 reaches the right edge.",
        "The ring of land lies on the border, so it is not closed.",
    ],
    prereqs=[
        ("flood_fill", "Iterative flood fill that marks a whole component."),
        ("grid", "Border detection and 4-directional neighbours."),
    ],
)

_p(
    "letter-case-permutation", "Letter Case Permutation", "Medium",
    topics=["Backtracking", "Strings"], subtopics=["Binary Choices"], companies=["Meta", "Amazon"],
    shape="str", ret="String", todo="recurse over positions: a digit has one choice, a letter two (uppercase first keeps the output sorted)",
    description=(
        "Each letter of `s` may be written in uppercase or lowercase; digits stay as they are. "
        "Print every resulting string, one per line, in lexicographic (ASCII) order — uppercase "
        "letters sort before lowercase.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe strings, one per line."
    ),
    constraints="1 ≤ |s| ≤ 12\ns consists of English letters and digits",
    hints=[
        "With k letters there are 2^k strings.",
        "Build the string one position at a time. A digit has one option; a letter has two.",
        "Trying the uppercase version first at every position produces the strings already in ASCII order.",
    ],
    opt=("O(2^k · n)", "O(n)", "2^k outputs of length n; the recursion depth is n."),
    editorial=(
        "## The one thing this teaches\n**Backtracking as a binary decision tree.** Each letter "
        "is a yes/no choice, so the outputs are the leaves of a tree of depth n. The recursion "
        "is the tree; the order you try children in is the order of the output.\n\n"
        "## Approach\n```java\nvoid build(char[] cur, int i) {\n"
        "    if (i == cur.length) { output(new String(cur)); return; }\n"
        "    if (Character.isDigit(cur[i])) { build(cur, i + 1); return; }\n"
        "    cur[i] = Character.toUpperCase(cur[i]); build(cur, i + 1);\n"
        "    cur[i] = Character.toLowerCase(cur[i]); build(cur, i + 1);\n}\n```\n\n"
        "## Why no undo is needed\nPosition `i` is overwritten on every visit before anything "
        "reads it, so the array never carries a stale choice forward.\n\n"
        "## The iterative view\nStart with `[\"\"]`. For each character, extend every string so "
        "far with it — or, for a letter, with both of its cases. The list doubles at each "
        "letter, the same tree built breadth-first."
    ),
    py='''
def solve(s):
    from itertools import product
    options = [(ch.upper(), ch.lower()) if ch.isalpha() else (ch,) for ch in s]
    return "\\n".join(sorted("".join(p) for p in product(*options)))
''',
    java='''
    static StringBuilder out;

    static void build(char[] cur, int i) {
        if (i == cur.length) {
            if (out.length() > 0) out.append('\\n');
            out.append(cur);
            return;
        }
        if (Character.isDigit(cur[i])) { build(cur, i + 1); return; }
        cur[i] = Character.toUpperCase(cur[i]);
        build(cur, i + 1);
        cur[i] = Character.toLowerCase(cur[i]);
        build(cur, i + 1);
    }

    static String solve(String s) {
        out = new StringBuilder();
        build(s.toCharArray(), 0);
        return out.toString();
    }
''',
    examples=[("Example 1", "a1b2\n"), ("Example 2", "3z4\n")],
    hidden=[
        ("Digits only", "12345\n"),
        ("Single letter", "C\n"),
        ("Mixed case input", "aB\n"),
        ("Letters only", "xyz\n"),
    ],
    expl=[
        "Two letters give four strings; uppercase sorts first.",
        "Only z can change.",
    ],
    prereqs=[
        ("backtracking", "A decision tree with one or two branches per position."),
        ("string_basics", "Character case conversion and ASCII ordering."),
    ],
)

_p(
    "combination-sum-iii", "Combination Sum III", "Medium",
    topics=["Backtracking"], subtopics=["Combinations", "Pruning"], companies=["Amazon", "Microsoft"],
    shape="two", ret="String", todo="choose digits in increasing order starting after the last one; stop when the count or the sum is exceeded",
    description=(
        "Find all combinations of `k` **distinct** digits from 1 to 9 that sum to `n`. Print each "
        "combination in increasing order on its own line, with the lines in lexicographic order. "
        "Print `NONE` if there is none.\n\n"
        "### Input\nOne line: `k n`.\n\n"
        "### Output\nThe combinations, or `NONE`."
    ),
    constraints="1 ≤ k ≤ 9\n1 ≤ n ≤ 60",
    hints=[
        "Choosing digits in increasing order makes each combination appear exactly once.",
        "Recurse with (next smallest digit allowed, digits chosen, remaining sum).",
        "Prune: if the next digit already exceeds the remaining sum, no larger digit can help — stop the loop.",
    ],
    opt=("O(C(9, k) · k)", "O(k)", "At most C(9, k) leaves, each copied once."),
    editorial=(
        "## The one thing this teaches\n**Increasing order removes duplicates; sorted candidates "
        "enable early stopping.** Picking the next digit only from those larger than the last one "
        "generates each set once. Because the candidates are sorted, the first digit that "
        "overshoots ends the whole loop.\n\n"
        "## Approach\n```java\nvoid pick(int start, int k, int remaining, Deque<Integer> chosen) {\n"
        "    if (k == 0) { if (remaining == 0) output(chosen); return; }\n"
        "    for (int d = start; d <= 9; d++) {\n        if (d > remaining) break;            // larger digits overshoot too\n"
        "        chosen.addLast(d);\n        pick(d + 1, k - 1, remaining - d, chosen);\n        chosen.removeLast();\n    }\n}\n```\n\n"
        "## Why output is already sorted\nThe loop tries smaller digits first at every level, so "
        "the combinations come out in lexicographic order with no sort needed.\n\n"
        "## Quick impossibility checks\nThe smallest possible sum of k digits is 1 + … + k and "
        "the largest is (10 − k) + … + 9. Outside that range, the answer is `NONE` immediately."
    ),
    py='''
def solve(x, y):
    from itertools import combinations
    found = [c for c in combinations(range(1, 10), x) if sum(c) == y]
    return "\\n".join(" ".join(map(str, c)) for c in found) if found else "NONE"
''',
    java='''
    static StringBuilder out;

    static void pick(int start, int k, int remaining, ArrayDeque<Integer> chosen) {
        if (k == 0) {
            if (remaining != 0) return;
            if (out.length() > 0) out.append('\\n');
            int i = 0;
            for (int d : chosen) { if (i++ > 0) out.append(' '); out.append(d); }
            return;
        }
        for (int d = start; d <= 9; d++) {
            if (d > remaining) break;
            chosen.addLast(d);
            pick(d + 1, k - 1, remaining - d, chosen);
            chosen.removeLast();
        }
    }

    static String solve(long k, long n) {
        out = new StringBuilder();
        pick(1, (int) k, (int) n, new ArrayDeque<>());
        return out.length() == 0 ? "NONE" : out.toString();
    }
''',
    examples=[("Example 1", "3 7\n"), ("Example 2", "3 9\n"), ("Example 3", "4 1\n")],
    hidden=[
        ("Every digit", "9 45\n"),
        ("Largest pair", "2 17\n"),
        ("Single digit", "1 9\n"),
        ("Just out of reach", "2 18\n"),
        ("Many answers", "3 15\n"),
    ],
    expl=[
        "1 + 2 + 4 is the only way.",
        "1 + 2 + 6, 1 + 3 + 5 and 2 + 3 + 4.",
        "Four distinct digits sum to at least 10.",
    ],
    prereqs=[
        ("backtracking", "Choosing, recursing and un-choosing with a start index."),
        ("pruning", "Breaking out of a sorted loop once a candidate overshoots."),
    ],
)

_p(
    "meeting-rooms-iii", "Meeting Rooms III", "Hard",
    topics=["Heaps", "Intervals", "Simulation"], subtopics=["Two Heaps"], companies=["Google", "Microsoft"],
    shape="pairs_k", ret="int", todo="process meetings by start; free rooms whose end ≤ start, take the lowest free room, or delay into the room that frees first",
    description=(
        "There are `k` rooms numbered `0` to `k − 1` and `n` meetings `[start, end)` with distinct "
        "start times. Meetings are assigned in order of their **original start time**:\n\n"
        "- the meeting takes the **lowest-numbered free room**;\n"
        "- if every room is busy, it waits for the room that frees up **earliest** (lowest number "
        "on a tie) and keeps its original duration.\n\n"
        "Print the room that hosted the most meetings (lowest number on a tie).\n\n"
        "### Input\n- Line 1: `n k`.\n- Next `n` lines: `start end`.\n\n"
        "### Output\nThe busiest room."
    ),
    constraints="1 ≤ k ≤ 100\n1 ≤ n ≤ 10^5\n0 ≤ start < end ≤ 5·10^5, starts distinct",
    hints=[
        "Sort meetings by start. Two questions repeat: which rooms are free now, and which busy room frees first.",
        "Keep a min-heap of free room numbers and a min-heap of busy rooms ordered by (end time, room number).",
        "Before each meeting, move rooms with end ≤ start from busy to free. If a room is free, use the smallest. Otherwise pop the earliest busy room and shift the meeting to start when it ends. Delayed end times can exceed an int.",
    ],
    opt=("O(n log n + n log k)", "O(k)", "A sort, then heap operations over at most k rooms per meeting."),
    editorial=(
        "## The one thing this teaches\n**Two heaps for two different orderings of the same "
        "things.** Free rooms are chosen by number; busy rooms are released by end time. One "
        "heap cannot serve both orders, so rooms move between two heaps as their state changes.\n\n"
        "## Approach\n```java\nsort meetings by start;\nPriorityQueue<Integer> free = rooms 0..k−1;\n"
        "PriorityQueue<long[]> busy = by (end, room);\nfor (meeting (s, e)) {\n"
        "    while (!busy.isEmpty() && busy.peek()[0] <= s) free.add((int) busy.poll()[1]);\n"
        "    if (!free.isEmpty()) {\n        int room = free.poll();\n        busy.add(new long[]{e, room});  count[room]++;\n"
        "    } else {\n        long[] first = busy.poll();                  // earliest to finish\n"
        "        busy.add(new long[]{first[0] + (e - s), first[1]});  count[(int) first[1]]++;\n    }\n}\n```\n\n"
        "## Why release before choosing\nA room whose meeting ends exactly at `s` is free at `s` — "
        "intervals are half-open. Releasing every room with `end ≤ s` first lets the \"lowest "
        "free room\" rule see all of them, not just the one that frees earliest.\n\n"
        "## Delays compound\nA delayed meeting ends later, which can delay the next one further. "
        "With 10^5 meetings the end times can climb far past the input values."
    ),
    py='''
def solve(p, k):
    free_at = [0] * k
    count = [0] * k
    for s, e in sorted(p):
        free = [r for r in range(k) if free_at[r] <= s]
        if free:
            room = free[0]
            free_at[room] = e
        else:
            room = min(range(k), key=lambda r: (free_at[r], r))
            free_at[room] += e - s
        count[room] += 1
    return count.index(max(count))
''',
    java='''
    static int solve(int[][] m, int k) {
        Arrays.sort(m, (x, y) -> Integer.compare(x[0], y[0]));
        PriorityQueue<Integer> free = new PriorityQueue<>();
        for (int i = 0; i < k; i++) free.add(i);
        PriorityQueue<long[]> busy = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Long.compare(x[0], y[0]) : Long.compare(x[1], y[1]));
        int[] count = new int[k];
        for (int[] mt : m) {
            long s = mt[0], e = mt[1];
            while (!busy.isEmpty() && busy.peek()[0] <= s) free.add((int) busy.poll()[1]);
            if (!free.isEmpty()) {
                int room = free.poll();
                busy.add(new long[]{e, room});
                count[room]++;
            } else {
                long[] first = busy.poll();
                busy.add(new long[]{first[0] + (e - s), first[1]});
                count[(int) first[1]]++;
            }
        }
        int best = 0;
        for (int i = 1; i < k; i++) if (count[i] > count[best]) best = i;
        return best;
    }
''',
    examples=[
        ("Example 1", "4 2\n0 10\n1 5\n2 7\n3 4\n"),
        ("Example 2", "5 3\n1 20\n2 10\n3 5\n4 9\n6 8\n"),
    ],
    hidden=[
        ("One room, one meeting", "1 1\n0 5\n"),
        ("Back-to-back in room 0", "3 3\n0 1\n1 2\n2 3\n"),
        ("Everything delayed", "3 1\n0 10\n1 2\n2 3\n"),
        ("Room 1 busiest", "5 2\n0 5\n1 2\n3 4\n4 9\n6 7\n"),
        ("Unsorted input", "4 2\n3 4\n0 10\n2 7\n1 5\n"),
    ],
    expl=[
        "Room 0 hosts [0,10) and the delayed [10,11); room 1 hosts [1,5) and the delayed [5,10). A tie of 2 — room 0.",
        "Room 2 hosts [3,5) and then the 4–9 meeting delayed to [5,10); room 1 hosts [2,10) and then the 6–8 meeting delayed to [10,12). Rooms 1 and 2 tie at 2 — room 1.",
    ],
    prereqs=[
        ("heap", "Min-heaps keyed by room number and by (end time, room)."),
        ("intervals", "Half-open intervals: a room ending at s is free at s."),
    ],
)

_p(
    "min-deletions-unique-frequencies", "Minimum Deletions for Unique Frequencies", "Medium",
    topics=["Greedy", "Hashing", "Strings"], subtopics=["Frequency Counting"], companies=["Microsoft", "Amazon"],
    shape="str", ret="int", todo="count letters; for each frequency, lower it (one deletion per step) until it is 0 or not yet used",
    description=(
        "Delete as few characters as possible from `s` so that no two **distinct letters that "
        "remain** have the same frequency. Print the number of deletions.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe minimum number of deletions."
    ),
    constraints="1 ≤ |s| ≤ 10^5\nLowercase English letters",
    hints=[
        "Only the 26 frequencies matter, not the positions of the characters.",
        "When two letters share a frequency, one of them must drop. Lowering it to the nearest unused value is never worse than lowering it further.",
        "Keep a set of used frequencies. For each letter's frequency, decrement while it is positive and already used, counting deletions; then mark it used.",
    ],
    opt=("O(n + 26²)", "O(26)", "Counting is O(n); each of 26 frequencies drops at most to 0."),
    editorial=(
        "## The one thing this teaches\n**Greedy repair: fix each conflict with the smallest "
        "change.** Letter identity is irrelevant, so the problem is about a multiset of numbers "
        "that must become distinct (zeros allowed to repeat) with the least total decrease.\n\n"
        "## Approach\n```java\nint[] freq = letter counts;\nSet<Integer> used = new HashSet<>();\nint deletions = 0;\n"
        "for (int f : freq) {\n    while (f > 0 && used.contains(f)) { f--; deletions++; }\n    used.add(f);\n}\n```\n\n"
        "## The sorted view\nSort frequencies in decreasing order. Each may be at most one less "
        "than the value kept before it (and not below 0): `keep = min(f, prevKept − 1)`. The "
        "deletions are `f − keep`. Both versions give the same total.\n\n"
        "## Walkthrough: aaabbbcc\nFrequencies 3, 3, 2. Keep 3; the second 3 becomes 2 (one "
        "deletion); the 2 now collides and becomes 1 (one deletion). Total 2."
    ),
    py='''
def solve(s):
    freqs = sorted(Counter(s).values(), reverse=True)
    deletions = 0
    limit = float("inf")
    for f in freqs:
        keep = max(0, min(f, limit))
        deletions += f - keep
        limit = keep - 1
    return deletions
''',
    java='''
    static int solve(String s) {
        int[] freq = new int[26];
        for (int i = 0; i < s.length(); i++) freq[s.charAt(i) - 'a']++;
        HashSet<Integer> used = new HashSet<>();
        int deletions = 0;
        for (int f : freq) {
            while (f > 0 && used.contains(f)) { f--; deletions++; }
            used.add(f);
        }
        return deletions;
    }
''',
    examples=[("Example 1", "aab\n"), ("Example 2", "aaabbbcc\n"), ("Example 3", "ceabaacb\n")],
    hidden=[
        ("Single letter", "a\n"),
        ("All distinct letters", "abcdef\n"),
        ("Four equal groups", "aaaabbbbccccdddd\n"),
        ("Already unique", "abbccc\n"),
    ],
    expl=[
        "a appears twice and b once — already distinct.",
        "Lower one 3 to 2 and the 2 to 1.",
        "Frequencies a 3, b 2, c 2, e 1: c drops to 1, which collides with e, so e drops to 0 — two deletions.",
    ],
    prereqs=[
        ("greedy", "Resolving each collision with the smallest decrease."),
        ("hashing", "Counting letters and tracking which frequencies are taken."),
    ],
)

_p(
    "longest-happy-prefix", "Longest Happy Prefix", "Hard",
    topics=["Strings"], subtopics=["KMP", "Prefix Function"], companies=["Google"],
    shape="str", ret="String", todo="compute the KMP prefix function; its last value is the length of the longest proper prefix that is also a suffix",
    description=(
        "A **happy prefix** is a non-empty prefix of `s` that is also a suffix, excluding `s` "
        "itself. Print the longest happy prefix, or `NONE` if there is none.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe longest happy prefix, or `NONE`."
    ),
    constraints="1 ≤ |s| ≤ 10^5\nLowercase English letters",
    hints=[
        "Comparing every prefix with the suffix of the same length is O(n²).",
        "Define pi[i] as the length of the longest proper prefix of s[0..i] that is also its suffix — the KMP failure function.",
        "Build pi left to right: extend the previous border when the next characters match, otherwise fall back to pi[k − 1] and retry. The answer has length pi[n − 1].",
    ],
    opt=("O(n)", "O(n)", "The fallback pointer moves back at most as far as it has moved forward in total."),
    editorial=(
        "## The one thing this teaches\n**The prefix function reuses borders of borders.** When a "
        "border of `s[0..i−1]` cannot be extended by `s[i]`, the next candidate is not \"one "
        "shorter\" but the border *of that border* — which is already stored.\n\n"
        "## Approach\n```java\nint[] pi = new int[n];\nfor (int i = 1, k = 0; i < n; i++) {\n"
        "    while (k > 0 && s.charAt(i) != s.charAt(k)) k = pi[k - 1];   // fall back\n"
        "    if (s.charAt(i) == s.charAt(k)) k++;\n    pi[i] = k;\n}\nreturn s.substring(0, pi[n - 1]);\n```\n\n"
        "## Why the total work is linear\n`k` increases by at most 1 per step, and every "
        "fallback decreases it. It cannot decrease more in total than it increased, so all the "
        "`while` iterations together are at most n.\n\n"
        "## Walkthrough: ababab\npi = 0 0 1 2 3 4. The last value is 4: `abab` is both a prefix "
        "and a suffix (overlapping in the middle)."
    ),
    py='''
def solve(s):
    for length in range(len(s) - 1, 0, -1):
        if s[:length] == s[-length:]:
            return s[:length]
    return "NONE"
''',
    java='''
    static String solve(String s) {
        int n = s.length();
        int[] pi = new int[n];
        for (int i = 1, k = 0; i < n; i++) {
            while (k > 0 && s.charAt(i) != s.charAt(k)) k = pi[k - 1];
            if (s.charAt(i) == s.charAt(k)) k++;
            pi[i] = k;
        }
        return pi[n - 1] == 0 ? "NONE" : s.substring(0, pi[n - 1]);
    }
''',
    examples=[("Example 1", "level\n"), ("Example 2", "ababab\n"), ("Example 3", "abc\n")],
    hidden=[
        ("Single character", "a\n"),
        ("One letter repeated", "aaaa\n"),
        ("Overlapping border", "abcabcab\n"),
        ("Border after a fallback", "aabaaab\n"),
        ("Short border", "abxab\n"),
    ],
    expl=[
        "\"l\" is a prefix and a suffix; \"le\" is not a suffix.",
        "\"abab\" is both; the prefix and suffix overlap.",
        "No non-empty proper prefix matches the end.",
    ],
    prereqs=[
        ("string_basics", "Prefixes, suffixes and borders of a string."),
        ("two_pointers", "A matching pointer that advances or falls back along a stored table."),
    ],
)

_p(
    "four-sum-count", "4Sum (Count)", "Medium",
    topics=["Two Pointers", "Sorting", "Arrays"], subtopics=["k-Sum"], companies=["Amazon", "Adobe"],
    shape="arr_k", ret="long", todo="sort; fix i and j (skipping repeated values), then two pointers for the other two, counting each distinct quadruple once",
    description=(
        "Count the **distinct** quadruplets of values `[a, b, c, d]` — taken from four different "
        "indices — whose sum equals `target`. Two quadruplets are the same if they contain the "
        "same values (as a multiset).\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of distinct quadruplets."
    ),
    constraints="1 ≤ n ≤ 200\n-10^9 ≤ a[i] ≤ 10^9\n-10^10 ≤ target ≤ 10^10",
    hints=[
        "Sorting makes duplicates adjacent, so a repeated value can be skipped at each position.",
        "Fix the first two values with two loops; the last two are a Two Sum on a sorted range — two pointers.",
        "After a match, move both pointers past equal values. Sums of four values up to 10^9 need 64-bit arithmetic.",
    ],
    opt=("O(n³)", "O(1)", "Two nested loops around a linear two-pointer scan, after sorting."),
    editorial=(
        "## The one thing this teaches\n**k-Sum is (k − 2) loops around Two Sum.** 3Sum fixes one "
        "value; 4Sum fixes two. The duplicate-skipping rule is the same at every level: after "
        "handling a value at some position, skip the equal values that follow it.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong count = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    if (i > 0 && a[i] == a[i - 1]) continue;\n    for (int j = i + 1; j < n; j++) {\n"
        "        if (j > i + 1 && a[j] == a[j - 1]) continue;\n        int lo = j + 1, hi = n - 1;\n"
        "        while (lo < hi) {\n            long sum = (long) a[i] + a[j] + a[lo] + a[hi];\n"
        "            if (sum < target) lo++;\n            else if (sum > target) hi--;\n"
        "            else {\n                count++;\n                do lo++; while (lo < hi && a[lo] == a[lo - 1]);\n"
        "                do hi--; while (lo < hi && a[hi] == a[hi + 1]);\n            }\n        }\n    }\n}\n```\n\n"
        "## Why `j > i + 1` in the skip\nThe first `j` after `i` may equal `a[i]` legitimately — "
        "`[2, 2, 2, 2]` uses the same value four times. Only a *repeat at the same position* is a "
        "duplicate.\n\n"
        "## Overflow\n`4 × 10^9` does not fit in an int. Cast before adding, not after."
    ),
    py='''
def solve(a, k):
    from itertools import combinations
    return len({tuple(sorted(c)) for c in combinations(a, 4) if sum(c) == k})
''',
    java='''
    static long solve(int[] a, long target) {
        int n = a.length;
        Arrays.sort(a);
        long count = 0;
        for (int i = 0; i < n; i++) {
            if (i > 0 && a[i] == a[i - 1]) continue;
            for (int j = i + 1; j < n; j++) {
                if (j > i + 1 && a[j] == a[j - 1]) continue;
                int lo = j + 1, hi = n - 1;
                while (lo < hi) {
                    long sum = (long) a[i] + a[j] + a[lo] + a[hi];
                    if (sum < target) lo++;
                    else if (sum > target) hi--;
                    else {
                        count++;
                        do lo++; while (lo < hi && a[lo] == a[lo - 1]);
                        do hi--; while (lo < hi && a[hi] == a[hi + 1]);
                    }
                }
            }
        }
        return count;
    }
''',
    examples=[("Example 1", "6 0\n1 0 -1 0 -2 2\n"), ("Example 2", "5 8\n2 2 2 2 2\n")],
    hidden=[
        ("Sum beyond an int", "4 4000000000\n1000000000 1000000000 1000000000 1000000000\n"),
        ("Too few numbers", "3 0\n0 0 0\n"),
        ("Symmetric values", "8 0\n-3 -2 -1 0 0 1 2 3\n"),
        ("Many duplicates", "8 -1\n1 1 1 1 1 1 -4 0\n"),
    ],
    expl=[
        "[−2, −1, 1, 2], [−2, 0, 0, 2] and [−1, 0, 0, 1].",
        "Only [2, 2, 2, 2], however many ways the indices can be chosen.",
    ],
    prereqs=[
        ("two_pointers", "Two Sum on a sorted range, with duplicate skipping."),
        ("overflow", "Summing four values of up to 10^9 in a long."),
    ],
)
