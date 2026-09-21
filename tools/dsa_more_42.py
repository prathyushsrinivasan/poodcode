# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 42 — flows and matchings, which the roadmap had nothing for at all.
#
#   assign-all-workers      can every worker get a distinct task? (augmenting paths)
#   bipartite-max-matching  the same search, counted instead of tested
#   min-cut-capacity        stated as a CUT, answered by a FLOW (max-flow min-cut)
#   min-path-cover-dag      matching applied somewhere it does not look like matching
#
# `graph-traversal` two-colours a graph and calls it bipartite; that answers a
# different question. Nothing in the course so far can pair things up, and
# "assign these to those" is one of the most common shapes a real problem takes.
# ===========================================================================

_p(
    "assign-all-workers", "Everyone Gets a Job", "Easy",
    topics=["Graphs"], subtopics=["Bipartite Matching", "Augmenting Path", "Backtracking"],
    companies=["Amazon", "Microsoft"],
    shape="bipartite", ret="String",
    todo="for each worker, search for a free task; if a task is taken, ask its current owner to move somewhere else",
    description=(
        "There are `nl` workers and `nr` tasks. Each worker is qualified for some of the tasks. "
        "Every worker must be given **exactly one** task, and no task may go to two workers.\n\n"
        "Print `YES` if that is possible, `NO` otherwise.\n\n"
        "### Input\nLine 1: `nl nr m`.\nNext `m` lines: `u v` — worker `u` is qualified for "
        "task `v`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ nl ≤ 12\n1 ≤ nr ≤ 12\n0 ≤ m ≤ nl · nr\n"
                "0 ≤ u < nl, 0 ≤ v < nr\nNo pair is listed twice.",
    hints=[
        "Giving each worker their first free task is wrong: worker 0 may take the only task worker 1 can do.",
        "So allow a worker to be *displaced*. When the task you want is taken, ask its current owner to go and find another one — recursively.",
        "Mark each task at most once per search, or two workers can push each other back and forth forever. If every worker succeeds, the answer is YES.",
    ],
    opt=("O(nl · m)", "O(nl + nr)",
         "One augmenting search per worker, and each visits every edge at most once."),
    editorial=(
        "## The one thing this teaches\n**The augmenting path: a greedy assignment can be "
        "repaired instead of restarted.** This is the engine under every matching algorithm, and "
        "the reason the greedy failure above is not fatal.\n\n"
        "## Approach\n```java\nint[] owner = new int[nr];        // which worker holds each task, -1 if free\n"
        "Arrays.fill(owner, -1);\n\nboolean place(int u, boolean[] tried) {\n"
        "    for (int v : qualified[u]) {\n        if (tried[v]) continue;\n"
        "        tried[v] = true;                                 // do not revisit in THIS search\n"
        "        if (owner[v] == -1 || place(owner[v], tried)) {  // free, or its owner can move\n"
        "            owner[v] = u;\n            return true;\n        }\n    }\n"
        "    return false;\n}\n\nfor (int u = 0; u < nl; u++)\n"
        "    if (!place(u, new boolean[nr])) return \"NO\";\nreturn \"YES\";\n```\n\n"
        "## Why displacing is safe\nThe recursive call only returns `true` after the displaced "
        "worker has actually been re-housed, and the count of assigned workers never drops — "
        "a successful search moves people around and adds exactly one. So progress is monotone.\n\n"
        "## The `tried` array is per search, not global\nIt is reset for every worker. Within one "
        "search it prevents two workers bouncing a task between them; across searches, resetting "
        "is what lets an earlier decision be undone later.\n\n"
        "## The theory behind the answer\n**Hall's theorem**: every worker can be placed exactly "
        "when no group of k workers is collectively qualified for fewer than k tasks. That is "
        "what a `NO` always means, and naming the offending group is a good way to explain a "
        "failure in an interview — checking all 2^nl groups is what the algorithm avoids."
    ),
    py='''
def solve(nl, nr, edges):
    sys.setrecursionlimit(10000)
    adj = [[] for _ in range(nl)]
    for u, v in edges:
        adj[u].append(v)
    owner = [-1] * nr

    def place(u, tried):
        for v in adj[u]:
            if tried[v]:
                continue
            tried[v] = True
            if owner[v] == -1 or place(owner[v], tried):
                owner[v] = u
                return True
        return False

    for u in range(nl):
        if not place(u, [False] * nr):
            return "NO"
    return "YES"
''',
    java='''
    static List<List<Integer>> adj;
    static int[] owner;

    static boolean place(int u, boolean[] tried) {
        for (int v : adj.get(u)) {
            if (tried[v]) continue;
            tried[v] = true;
            if (owner[v] == -1 || place(owner[v], tried)) { owner[v] = u; return true; }
        }
        return false;
    }

    static String solve(int nl, int nr, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < nl; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        owner = new int[nr];
        Arrays.fill(owner, -1);
        for (int u = 0; u < nl; u++)
            if (!place(u, new boolean[nr])) return "NO";
        return "YES";
    }
''',
    examples=[
        ("Example 1", "3 3 4\n0 0\n1 0\n1 1\n2 2\n"),
        ("Example 2", "3 2 4\n0 0\n0 1\n1 0\n2 1\n"),
    ],
    hidden=[
        ("One worker, one task", "1 1 1\n0 0\n"),
        ("A worker with no qualification", "2 2 1\n0 0\n"),
        ("Greedy would fail, displacement succeeds", "2 2 3\n0 0\n0 1\n1 0\n"),
        ("Everyone wants the same task", "3 3 3\n0 1\n1 1\n2 1\n"),
        ("A long chain of displacements", "4 4 7\n0 0\n1 0\n1 1\n2 1\n2 2\n3 2\n3 3\n"),
        ("Fully qualified", "4 4 16\n0 0\n0 1\n0 2\n0 3\n1 0\n1 1\n1 2\n1 3\n2 0\n2 1\n2 2\n2 3\n3 0\n3 1\n3 2\n3 3\n"),
    ],
    expl=[
        "Worker 0 takes task 0, worker 1 takes task 1, worker 2 takes task 2.",
        "Three workers and only two tasks — impossible whatever the qualifications.",
    ],
    prereqs=[
        ("backtracking", "Undoing an earlier choice when it blocks a later one."),
        ("graph_repr", "Two sets of vertices and the edges between them."),
        ("visited_set", "Marking each task once per search."),
    ],
)


_p(
    "bipartite-max-matching", "Pair Up as Many as You Can", "Medium",
    topics=["Graphs"], subtopics=["Bipartite Matching", "Augmenting Path", "Kuhn's Algorithm"],
    companies=["Google", "Amazon", "Meta"],
    shape="bipartite", ret="long",
    todo="run the augmenting search from every left vertex and count how many succeed",
    description=(
        "`nl` students and `nr` projects. Each student is interested in some projects. A student "
        "takes at most one project and a project takes at most one student.\n\n"
        "Print the largest number of student–project pairs that can be formed at once.\n\n"
        "### Input\nLine 1: `nl nr m`.\nNext `m` lines: `u v` — student `u` is interested in "
        "project `v`.\n\n"
        "### Output\nThe maximum number of pairs."
    ),
    constraints="1 ≤ nl ≤ 300\n1 ≤ nr ≤ 300\n0 ≤ m ≤ 20000\n"
                "0 ≤ u < nl, 0 ≤ v < nr\nNo pair is listed twice.",
    hints=[
        "Pairing greedily and stopping is wrong for the same reason as before — but this time you do not give up when a student fails, you simply leave them unpaired and continue.",
        "Run the same augmenting search from every student. Each successful search increases the number of pairs by exactly one.",
        "Berge's theorem: a matching is maximum exactly when no augmenting path exists. So when every student has been tried once and failed searches are final, the count is optimal.",
    ],
    opt=("O(nl · m)", "O(nl + nr)",
         "One augmenting search per left vertex; each walks each edge at most once."),
    editorial=(
        "## The one thing this teaches\n**Repeatedly finding an augmenting path *is* the "
        "algorithm.** Each one raises the matching by one, and when none exists you are provably "
        "at the maximum — there is nothing greedy left to regret.\n\n"
        "## Approach (Kuhn's)\n```java\nint pairs = 0;\nArrays.fill(owner, -1);\n"
        "for (int u = 0; u < nl; u++)\n"
        "    if (place(u, new boolean[nr])) pairs++;   // same `place` as the previous problem\n"
        "return pairs;\n```\nThe only difference from \"can everyone be placed?\" is that a "
        "failure is counted rather than fatal.\n\n"
        "## Why a failed search stays failed\nIf student u cannot be matched now, no *later* "
        "augmentation can make them matchable: augmenting never un-matches anybody, it only "
        "reroutes. So one pass over the students is enough — a fact that is not obvious and is "
        "worth saying out loud.\n\n"
        "## Berge's theorem, the reason this is optimal\nTake the symmetric difference of your "
        "matching and a hypothetically larger one. It splits into paths and cycles that alternate "
        "between the two; if the other matching is bigger, some component must have more of its "
        "edges than yours — and that component is an augmenting path. Contrapositive: no "
        "augmenting path, no larger matching.\n\n"
        "## The duals worth knowing\nBy **König's theorem**, on a bipartite graph the maximum "
        "matching equals the **minimum vertex cover**, and the maximum independent set is "
        "`nl + nr − matching`. Three questions, one computation — and the reason "
        "\"choose the fewest rows and columns covering every marked cell\" is this problem in "
        "disguise.\n\n"
        "## When to reach for Hopcroft–Karp\nKuhn is O(V·E) and fine to about 10⁵ "
        "edges. Hopcroft–Karp augments along many shortest paths at once for "
        "O(E·√V); know the name and the bound, and reach for it only when Kuhn is "
        "measurably too slow."
    ),
    py='''
def solve(nl, nr, edges):
    sys.setrecursionlimit(10000)
    adj = [[] for _ in range(nl)]
    for u, v in edges:
        adj[u].append(v)
    owner = [-1] * nr

    def place(u, tried):
        for v in adj[u]:
            if tried[v]:
                continue
            tried[v] = True
            if owner[v] == -1 or place(owner[v], tried):
                owner[v] = u
                return True
        return False

    pairs = 0
    for u in range(nl):
        if place(u, [False] * nr):
            pairs += 1
    return pairs
''',
    java='''
    static List<List<Integer>> adj;
    static int[] owner;

    static boolean place(int u, boolean[] tried) {
        for (int v : adj.get(u)) {
            if (tried[v]) continue;
            tried[v] = true;
            if (owner[v] == -1 || place(owner[v], tried)) { owner[v] = u; return true; }
        }
        return false;
    }

    static long solve(int nl, int nr, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < nl; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        owner = new int[nr];
        Arrays.fill(owner, -1);
        long pairs = 0;
        for (int u = 0; u < nl; u++)
            if (place(u, new boolean[nr])) pairs++;
        return pairs;
    }
''',
    examples=[
        ("Example 1", "3 3 4\n0 0\n1 0\n1 1\n2 2\n"),
        ("Example 2", "4 2 5\n0 0\n1 0\n2 1\n3 0\n3 1\n"),
    ],
    hidden=[
        ("No interests at all", "3 3 0\n0 0\n"),
        ("A perfect matching", "4 4 4\n0 0\n1 1\n2 2\n3 3\n"),
        ("One project, many students", "5 1 5\n0 0\n1 0\n2 0\n3 0\n4 0\n"),
        ("Two components", "6 6 8\n0 0\n1 0\n1 1\n2 1\n3 3\n4 3\n4 4\n5 5\n"),
        ("Dense, more students than projects", "6 3 12\n0 0\n0 1\n1 1\n1 2\n2 0\n2 2\n3 0\n3 1\n4 1\n4 2\n5 0\n5 2\n"),
        ("A chain needing repeated repair", "5 5 9\n0 0\n1 0\n1 1\n2 1\n2 2\n3 2\n3 3\n4 3\n4 4\n"),
    ],
    expl=[
        "Student 0 with project 0, student 1 with project 1, student 2 with project 2 — all three pair up.",
        "Only two projects exist, so at most two pairs; students 0 and 2 (or several other choices) achieve it.",
    ],
    prereqs=[
        ("graph_repr", "Adjacency from one side of the split to the other."),
        ("backtracking", "Rerouting an earlier pair to free a vertex."),
        ("greedy", "Why the greedy count needs the repair step to become optimal."),
    ],
)


_p(
    "min-cut-capacity", "Cut the Pipes", "Medium",
    topics=["Graphs"], subtopics=["Max Flow", "Min Cut", "Edmonds-Karp", "BFS"],
    companies=["Google", "Amazon"],
    shape="wgraph", ret="long",
    todo="the cheapest cut equals the largest flow: repeatedly BFS for a path with spare capacity and push as much as it allows",
    description=(
        "A pipe network has `n` junctions numbered `0 … n-1` and `m` one-way pipes. Pipe "
        "`u v w` carries up to `w` litres per second from `u` to `v`.\n\n"
        "Water is pumped in at junction `0` and drawn off at junction `n-1`. You want to stop it "
        "completely by destroying pipes, and destroying a pipe of capacity `w` costs `w`.\n\n"
        "Print the **cheapest total cost** that leaves no route at all from `0` to `n-1`.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v w`.\n\n"
        "### Output\nThe minimum total capacity that has to be destroyed."
    ),
    constraints="2 ≤ n ≤ 200\n0 ≤ m ≤ 2000\n1 ≤ w ≤ 10^9\n"
                "0 ≤ u, v < n\nPipes may repeat and may run in both directions between a pair.",
    hints=[
        "Trying every subset of pipes is hopeless. The trick is that this question has a twin: the **maximum flow** from 0 to n-1 is exactly the minimum cut.",
        "So compute a flow instead. Find any route from 0 to n-1 with spare capacity, push as much as its tightest pipe allows, and repeat until no route remains.",
        "Each push must also create a **reverse** edge of the same amount, so a later path can undo part of an earlier decision. Without that the greedy gets stuck below the true maximum.",
    ],
    opt=("O(V · E²)", "O(V + E)",
         "Edmonds–Karp: BFS for the shortest augmenting path, which bounds the number of rounds."),
    editorial=(
        "## The one thing this teaches\n**Max-flow min-cut**: the largest flow you can push "
        "equals the smallest total capacity you can remove to disconnect source from sink. The "
        "question is asked as a cut and answered as a flow.\n\n"
        "## Why the theorem is true, in two lines\n*Any* cut bounds *any* flow — everything "
        "reaching the sink crosses it. And when no augmenting path remains, the vertices still "
        "reachable from the source in the residual network form a cut whose every forward edge is "
        "saturated and every backward edge is empty, so its capacity *equals* the flow. A flow "
        "meeting a cut proves both are optimal.\n\n"
        "## Approach\n```java\nwhile (bfsFindsPath(source, sink, parentEdge)) {\n"
        "    long push = Long.MAX_VALUE;                       // the tightest pipe on the path\n"
        "    for (int v = sink; v != source; v = from[parentEdge[v]])\n"
        "        push = Math.min(push, cap[parentEdge[v]]);\n"
        "    for (int v = sink; v != source; v = from[parentEdge[v]]) {\n"
        "        cap[parentEdge[v]]     -= push;\n"
        "        cap[parentEdge[v] ^ 1] += push;                // the reverse edge\n"
        "    }\n    flow += push;\n}\nreturn flow;\n```\n\n"
        "## The paired-edge trick\nStore edges in pairs, so edge `e` and its reverse are `e` and "
        "`e ^ 1`. A forward pipe gets capacity w and its partner 0; pushing flow moves capacity "
        "from one to the other. \"Undoing\" a previous decision is then just an ordinary "
        "augmenting path that happens to use a reverse edge — no special case.\n\n"
        "## Why BFS and not DFS\nWith DFS the number of rounds can depend on the capacities: two "
        "pipes of a billion and a bridge of 1 can take a billion alternating pushes. BFS always "
        "takes a shortest augmenting path, which gives the O(V·E²) bound independent of "
        "capacity — that is exactly what Edmonds–Karp adds to Ford–Fulkerson.\n\n"
        "## Overflow\n2000 pipes at 10⁹ is 2·10¹². The flow, the capacities and "
        "the bottleneck are all `long`."
    ),
    py='''
def solve(n, edges):
    to = []
    cap = []
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append(len(to))
        to.append(v)
        cap.append(w)
        graph[v].append(len(to))
        to.append(u)
        cap.append(0)
    s, t = 0, n - 1
    flow = 0
    while True:
        par = [-1] * n
        par[s] = -2
        dq = deque([s])
        while dq and par[t] == -1:
            u = dq.popleft()
            for eid in graph[u]:
                v = to[eid]
                if cap[eid] > 0 and par[v] == -1:
                    par[v] = eid
                    dq.append(v)
        if par[t] == -1:
            return flow
        push = None
        v = t
        while v != s:
            eid = par[v]
            push = cap[eid] if push is None else min(push, cap[eid])
            v = to[eid ^ 1]
        v = t
        while v != s:
            eid = par[v]
            cap[eid] -= push
            cap[eid ^ 1] += push
            v = to[eid ^ 1]
        flow += push
''',
    java='''
    static long solve(int n, int[][] edges) {
        int m = edges.length;
        int[] to = new int[2 * m];
        long[] cap = new long[2 * m];
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        int ec = 0;
        for (int[] e : edges) {
            g.get(e[0]).add(ec); to[ec] = e[1]; cap[ec] = e[2]; ec++;
            g.get(e[1]).add(ec); to[ec] = e[0]; cap[ec] = 0;    ec++;
        }
        int s = 0, t = n - 1;
        long flow = 0;
        int[] par = new int[n];
        int[] queue = new int[n];
        while (true) {
            Arrays.fill(par, -1);
            par[s] = -2;
            int head = 0, tail = 0;
            queue[tail++] = s;
            while (head < tail && par[t] == -1) {
                int u = queue[head++];
                for (int eid : g.get(u)) {
                    int v = to[eid];
                    if (cap[eid] > 0 && par[v] == -1) { par[v] = eid; queue[tail++] = v; }
                }
            }
            if (par[t] == -1) return flow;
            long push = Long.MAX_VALUE;
            for (int v = t; v != s; ) {
                int eid = par[v];
                push = Math.min(push, cap[eid]);
                v = to[eid ^ 1];
            }
            for (int v = t; v != s; ) {
                int eid = par[v];
                cap[eid] -= push;
                cap[eid ^ 1] += push;
                v = to[eid ^ 1];
            }
            flow += push;
        }
    }
''',
    examples=[
        ("Example 1", "4 5\n0 1 3\n0 2 2\n1 2 1\n1 3 2\n2 3 3\n"),
        ("Example 2", "2 1\n0 1 7\n"),
    ],
    hidden=[
        ("No pipes at all", "3 0\n0 0 0\n"),
        ("The sink is unreachable", "4 2\n0 1 5\n2 3 5\n"),
        ("A bottleneck in the middle", "4 3\n0 1 100\n1 2 1\n2 3 100\n"),
        ("Parallel pipes between the same pair", "2 3\n0 1 4\n0 1 5\n0 1 6\n"),
        ("The greedy path must be partly undone", "4 5\n0 1 10\n0 2 10\n1 2 1\n1 3 10\n2 3 10\n"),
        ("Large capacities", "5 6\n0 1 1000000000\n0 2 1000000000\n1 3 1000000000\n2 3 1000000000\n3 4 1000000000\n1 4 1000000000\n"),
    ],
    expl=[
        "Destroying pipes 1→3 and 2→3 costs 2 + 3 = 5, and nothing cheaper disconnects them. The maximum flow is also 5.",
        "One pipe, so cutting it costs its capacity.",
    ],
    prereqs=[
        ("bfs", "Finding a route with spare capacity, shortest first."),
        ("graph_repr", "Edges stored in pairs so a reverse edge is one XOR away."),
        ("greedy", "Why pushing greedily needs an undo to become optimal."),
        ("overflow", "Capacities of 10^9 summed over thousands of pipes."),
    ],
)


_p(
    "min-path-cover-dag", "Fewest Assembly Lines", "Hard",
    topics=["Graphs", "Dynamic Programming"], subtopics=["Bipartite Matching", "DAG", "Path Cover"],
    companies=["Google", "Meta"],
    shape="graph", ret="long",
    todo="split every vertex into an out-copy and an in-copy, match them, and subtract: n - maximum matching",
    description=(
        "A factory has `n` stations and `m` one-way conveyors. The conveyors contain no cycles. "
        "An **assembly line** is a chain of stations linked by conveyors, each station appearing "
        "on at most one line (a line may be a single station on its own).\n\n"
        "Print the fewest lines needed so that every station is on exactly one.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: `u v` — a conveyor from `u` to `v`.\n\n"
        "### Output\nThe minimum number of lines."
    ),
    constraints="1 ≤ n ≤ 300\n0 ≤ m ≤ 20000\n0 ≤ u, v < n\n"
                "The conveyors form a directed acyclic graph.",
    hints=[
        "With n stations and no conveyors used, you need n lines. Every conveyor you actually use joins two lines into one — so the answer is n minus the number of conveyors used.",
        "A station can have at most one conveyor leaving it *on its line*, and at most one arriving. That is a pairing constraint: it is a bipartite matching.",
        "Make two copies of every station — an \"out\" copy on the left and an \"in\" copy on the right — and put an edge for each conveyor. The answer is `n − maximum matching`.",
    ],
    opt=("O(n · m)", "O(n + m)",
         "One bipartite matching on the split graph; the answer is n minus its size."),
    editorial=(
        "## The one thing this teaches\n**Reduction.** Nothing here mentions matching, and the "
        "whole problem is one line of arithmetic once you see the split-vertex construction. "
        "Recognising a matching in disguise is worth more than any matching implementation.\n\n"
        "## The construction\nEach station becomes two vertices: `out(v)` on the left and "
        "`in(v)` on the right. A conveyor `u → v` becomes the edge `out(u) — in(v)`.\n\n"
        "A matching picks a set of conveyors such that no station is left by two of them and no "
        "station is entered by two of them — which is exactly a set of vertex-disjoint paths. "
        "Start from n single-station lines; each matched conveyor glues two of them together, so:\n\n"
        "> **minimum path cover = n − maximum matching**\n\n"
        "## Why the matched edges cannot form a cycle\nThey could, in a general digraph — and "
        "then the count would be wrong, because a cycle joins k lines with k edges instead of "
        "k − 1. The problem says *acyclic*, so it cannot happen. This is why the identity is "
        "stated for DAGs, and it is the follow-up question to expect.\n\n"
        "## Approach\n```java\nfor each conveyor (u, v): adj[u].add(v);      // out(u) -- in(v)\n"
        "long matched = kuhn(n, n, adj);\nreturn n - matched;\n```\n\n"
        "## The family\nSame trick, different dress: \"minimum number of platforms\", \"fewest "
        "increasing subsequences covering a sequence\" (Dilworth's theorem, which is this "
        "identity again), \"fewest taxis for a list of trips\". When a problem asks for the "
        "*fewest chains* covering something ordered, this is the answer."
    ),
    py='''
def solve(n, edges):
    sys.setrecursionlimit(10000)
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    owner = [-1] * n

    def place(u, tried):
        for v in adj[u]:
            if tried[v]:
                continue
            tried[v] = True
            if owner[v] == -1 or place(owner[v], tried):
                owner[v] = u
                return True
        return False

    matched = 0
    for u in range(n):
        if place(u, [False] * n):
            matched += 1
    return n - matched
''',
    java='''
    static List<List<Integer>> adj;
    static int[] owner;

    static boolean place(int u, boolean[] tried) {
        for (int v : adj.get(u)) {
            if (tried[v]) continue;
            tried[v] = true;
            if (owner[v] == -1 || place(owner[v], tried)) { owner[v] = u; return true; }
        }
        return false;
    }

    static long solve(int n, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        owner = new int[n];
        Arrays.fill(owner, -1);
        long matched = 0;
        for (int u = 0; u < n; u++)
            if (place(u, new boolean[n])) matched++;
        return n - matched;
    }
''',
    examples=[
        ("Example 1", "5 4\n0 1\n1 2\n3 4\n0 3\n"),
        ("Example 2", "4 0\n0 0\n"),
    ],
    hidden=[
        ("One station", "1 0\n0 0\n"),
        ("A single long chain", "6 5\n0 1\n1 2\n2 3\n3 4\n4 5\n"),
        ("A fan out of one station", "5 4\n0 1\n0 2\n0 3\n0 4\n"),
        ("A fan into one station", "5 4\n1 0\n2 0\n3 0\n4 0\n"),
        ("A diamond", "4 4\n0 1\n0 2\n1 3\n2 3\n"),
        ("Two chains crossing", "7 8\n0 1\n1 2\n2 3\n4 5\n5 6\n0 5\n4 1\n2 6\n"),
    ],
    expl=[
        "0→1→2 is one line and 3→4 is another — two lines. The conveyor 0→3 cannot also be used, because station 0 would then leave twice.",
        "With no conveyors, every station is its own line.",
    ],
    prereqs=[
        ("graph_repr", "A directed acyclic graph, and a bipartite copy of it."),
        ("topo", "Why acyclicity is what makes the identity hold."),
        ("greedy", "Each matched edge saves exactly one line."),
    ],
)
