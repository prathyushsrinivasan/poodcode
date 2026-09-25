# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 27 — graphs: BFS & DFS.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THE PROMISE WEEK 20 MADE: "DFS and BFS are one algorithm with a different
# container, and week 27 is that fact again plus a visited set." That sentence is
# lesson 2's opening, and it is literally true of the code here: the traversal
# loops are week 20's, with `visited` added.
#
# What the week leans on:
#   week 18   the head-index queue (every BFS here uses it — never `shift`)
#   week 19   Set / Map, and the `${r},${c}` key for grid cells
#   week 20   the traversal loop, and "stack = DFS, queue = BFS"
#   week 25   recursion depth: recursive DFS on a long path is week 25's RangeError,
#             so the grid lessons use an explicit stack
#   week 26   a DP over a topological order (lesson 5's "fewest semesters")
#
# ---------------------------------------------------------------------------
# THE TYPESCRIPT FACT, verified: `Array.from({ length: n }, () => [])` infers
# `never[][]` — an empty array literal with nothing to widen it — so the first
# `adj[u]?.push(v)` is TS2345 ("… is not assignable to parameter of type
# 'never'"). Every adjacency list in a TypeScript tutorial trips over it once.
# Shipped as a `_predict` (answer `never[][]`) and a `_diagnose`; the week's shared
# builder annotates the callback, `(): number[] => []`.
#
# ---------------------------------------------------------------------------
# DETERMINISM. A traversal's ORDER depends on neighbour order, so every graph is
# built from its edge list in input order and every grid tries neighbours in one
# stated order (up, down, left, right). Outputs that could legitimately differ
# between correct solutions — "a" shortest path when several exist — are pinned by
# stating the order in the prompt.
#
# The one lead-in: lesson 7 runs BFS on a weighted graph and gets the wrong answer,
# then fixes it with an O(V²) array-scan Dijkstra. Week 28 replaces that scan with
# a heap — the reason a priority queue exists.
# ---------------------------------------------------------------------------

# Undirected graph from stdin: first line n, then one edge "u v" per line.
_GRAPH = (
    _FS +
    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
    'const n = Number(lines[0] ?? "0");\n'
    'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
    'for (const l of lines.slice(1)) {\n'
    '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
    '  if (u === undefined || v === undefined) {\n'
    '    continue;\n  }\n'
    '  adj[u]?.push(v);\n'
    '  adj[v]?.push(u);\n}\n'
)

# Directed: the same, one push.
_DIGRAPH = (
    _FS +
    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
    'const n = Number(lines[0] ?? "0");\n'
    'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
    'for (const l of lines.slice(1)) {\n'
    '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
    '  if (u === undefined || v === undefined) {\n'
    '    continue;\n  }\n'
    '  adj[u]?.push(v);\n}\n'
)

# A grid of characters from stdin, one row per line.
_CHARGRID = (
    _FS +
    'const grid: readonly string[] = fs.readFileSync(0, "utf8").trim().split("\\n").map((l) => l.trim());\n'
    'const R = grid.length;\n'
    'const C = (grid[0] ?? "").length;\n'
    'function cell(r: number, c: number): string {\n'
    '  if (r < 0 || r >= R || c < 0 || c >= C) {\n'
    '    return "";\n  }\n'
    '  return (grid[r] ?? "").charAt(c);\n}\n'
    'const DIRS: readonly (readonly [number, number])[] = [[-1, 0], [1, 0], [0, -1], [0, 1]];\n'
)


# --- Week 27 --------------------------------------------------------------
_WEEKS.append(_week(
    27, 7, _M7,
    "Graphs: BFS & DFS",
    "Week 20 said depth-first and breadth-first are one algorithm with a different container. On a graph they need one more thing — a visited set — and with it they answer reachability, shortest paths, components, cycles and order.",
    """
A **graph** is things (nodes) and connections between them (edges). A tree is a
graph with no cycles and one path between any two nodes; a linked list is a tree
with one child each. You have been doing graphs since week 20.

## The one new idea

Week 20's traversal:

```ts
const stack = [root];
while (stack.length > 0) {
  const t = stack.pop();
  // visit t, push its children
}
```

On a tree, each node is reached exactly once, because each has one parent. On a
graph, a node can be reached **many ways** — and around a cycle, forever. So:

```ts
const visited = new Set<number>();         // the one addition
```

That is it. **Stack → depth-first. Queue → breadth-first. Plus a visited set.**
Everything this week is those three lines, applied.

## What each one gives you

* **DFS** — goes deep first. Reachability, connected components, cycle detection,
  topological order.
* **BFS** — goes level by level. Because it reaches every node at distance 1 before
  any at distance 2, the first time it reaches a node is by a **shortest path**
  (counting edges). That property is the whole reason to choose it.

## Grids are graphs

Every maze, island-counting and flood-fill question is a graph whose nodes are
cells and whose edges are the four neighbours. Lesson 4 is nothing but that
observation, and it covers a large share of real interview questions.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Store a graph as an adjacency list, directed or undirected",
        "Type an adjacency list so it is not never[][]",
        "Traverse with DFS and a visited set, and say what goes wrong without it",
        "Count connected components and their sizes",
        "Traverse with BFS, and say why it finds shortest paths in unweighted graphs",
        "Reconstruct a shortest path from parent links",
        "Mark nodes visited when they are enqueued, and say why",
        "Treat a grid as a graph, with bounds-checked neighbours",
        "Detect a cycle in a directed graph with three colours",
        "Produce a topological order with Kahn's algorithm, and detect a cycle with it",
        "Run a multi-source BFS, and 2-colour a graph",
        "Say why BFS fails on weighted edges, and what replaces it",
    ],
    why="Graph questions are the ones that look hardest in an interview and reduce most completely to a template. Once 'islands', 'rotting oranges', 'course schedule' and 'word ladder' are all recognised as BFS or DFS with a visited set, a whole category stops being tricks. And it is the payoff of weeks 18-20: the stack and the queue were built for exactly this.",
    est_minutes=480,
    glossary=[
        _gloss("graph", "Nodes and the edges between them."),
        _gloss("directed / undirected", "An undirected edge goes both ways; a directed one only from u to v."),
        _gloss("adjacency list", "For each node, the list of its neighbours. adj[u] = [v, w, …]."),
        _gloss("degree", "How many edges touch a node. In a directed graph: in-degree and out-degree."),
        _gloss("visited set", "The nodes already reached. What stops a traversal looping round a cycle."),
        _gloss("DFS", "Depth-first search: a stack (or recursion). Deep before wide."),
        _gloss("BFS", "Breadth-first search: a queue. Level by level, so first arrival is by a shortest path."),
        _gloss("connected component", "A maximal set of nodes that can all reach each other."),
        _gloss("parent link", "The node you came from. Walking them back rebuilds the path."),
        _gloss("multi-source BFS", "Start the queue with EVERY source at distance 0."),
        _gloss("bipartite", "Two-colourable: every edge joins the two colours."),
        _gloss("DAG", "Directed acyclic graph. The kind that has a topological order."),
        _gloss("topological order", "An order where every edge points forwards. Prerequisites first."),
        _gloss("in-degree", "Edges pointing INTO a node. Kahn's algorithm starts from those with 0."),
        _gloss("three colours", "White (unseen), grey (on the current path), black (finished). A grey hit is a cycle."),
        _gloss("Dijkstra", "Shortest paths with non-negative weights: always settle the nearest unsettled node."),
    ],
    cheatsheet="""
```ts
// ---- an adjacency list — annotate the callback, or it is never[][] ---------
const adj: number[][] = Array.from({ length: n }, (): number[] => []);
adj[u]?.push(v);
adj[v]?.push(u);                                   // undirected: both directions

// ---- DFS: a stack and a visited set --------------------------------------
const seen = new Set<number>([start]);
const stack = [start];
while (stack.length > 0) {
  const u = stack.pop();
  if (u === undefined) { continue; }
  for (const v of adj[u] ?? []) {
    if (!seen.has(v)) { seen.add(v); stack.push(v); }
  }
}

// ---- BFS: a head-index queue (week 18) and distances ----------------------
const dist = new Array<number>(n).fill(-1);
dist[start] = 0;
const queue = [start];
for (let head = 0; head < queue.length; head = head + 1) {
  const u = queue[head] ?? 0;
  for (const v of adj[u] ?? []) {
    if (dist[v] === -1) {                          // mark when ENQUEUED
      dist[v] = (dist[u] ?? 0) + 1;
      parent[v] = u;
      queue.push(v);
    }
  }
}

// ---- a grid is a graph -----------------------------------------------------
const DIRS = [[-1, 0], [1, 0], [0, -1], [0, 1]];   // up, down, left, right
if (r < 0 || r >= R || c < 0 || c >= C) { /* off the board */ }
const key = `${r},${c}`;                            // or r * C + c — NOT id ± 1

// ---- Kahn's topological order ------------------------------------------------
// indegree; queue every node with 0; pop, output, decrement its neighbours,
// enqueue any that reach 0. Output shorter than n  ⇒  a cycle.

// ---- directed cycle: three colours ------------------------------------------
// 0 white · 1 grey (on the current path) · 2 black (done). Reaching GREY = cycle.
```

| question | reach for |
|---|---|
| reachable? components? | DFS or BFS |
| fewest edges from A to B | **BFS** |
| order with prerequisites | topological sort |
| cycle in a directed graph | three colours, or Kahn |
| fewest total WEIGHT | Dijkstra (week 28's heap) |
""",
    self_check=[
        "Can you build an undirected adjacency list from an edge list?",
        "Can you say why `Array.from({ length: n }, () => [])` rejects a push?",
        "Can you write DFS with a visited set, and say what happens without one?",
        "Can you count connected components?",
        "Can you say why BFS finds shortest paths and DFS does not?",
        "Can you rebuild the path itself from parent links?",
        "Can you say why a node is marked when enqueued rather than when dequeued?",
        "Can you walk a grid's four neighbours without going off the edge?",
        "Can you say why `id - 1` is not the left neighbour of a grid cell?",
        "Can you produce a topological order, and tell when none exists?",
        "Can you detect a cycle in a directed graph, and say why 'visited' alone is not enough?",
        "Can you start a BFS from several sources at once?",
        "Can you say what BFS gets wrong on a weighted graph?",
    ],
    review=[
        _q("DFS and BFS differ in…",
           ["everything", "the container: a stack or a queue", "the visited set", "the graph"], 1,
           "Week 20's fact."),
        _q("A traversal of a graph (not a tree) needs…",
           ["recursion", "a visited set", "sorted edges", "a heap"], 1,
           "Or a cycle is walked for ever."),
        _q("`Array.from({ length: 3 }, () => [])` is typed…",
           ["number[][]", "never[][]", "any[][]", "unknown[][]"], 1,
           "Annotate the callback: (): number[] => []."),
        _q("An undirected edge u-v is stored as…",
           ["adj[u].push(v)", "adj[u].push(v) AND adj[v].push(u)", "adj[v].push(u)", "a pair"], 1,
           "Both directions."),
        _q("BFS finds shortest paths because…",
           ["it is fast", "it reaches every node at distance d before any at d + 1", "of the queue's size",
            "it is recursive"], 1,
           "First arrival is by a shortest path."),
        _q("BFS marks a node visited…",
           ["when dequeued", "when enqueued, so it enters the queue once", "never", "at the end"], 1,
           "Otherwise duplicates pile up."),
        _q("Connected components are counted by…",
           ["BFS once", "starting a traversal from every unvisited node", "sorting", "degrees"], 1,
           "Each fresh start is a new component."),
        _q("In a grid stored as r * C + c, the left neighbour of a cell in column 0 is…",
           ["id - 1", "off the board — id - 1 is the previous row's last cell", "id + C", "id"], 1,
           "Check the column, not the id."),
        _q("Kahn's algorithm starts from the nodes with…",
           ["the most edges", "in-degree 0", "out-degree 0", "the smallest number"], 1,
           "Nothing has to come before them."),
        _q("Kahn's output shorter than n means…",
           ["an error", "the graph has a cycle", "it is undirected", "disconnected"], 1,
           "Some nodes never reached in-degree 0."),
        _q("A directed cycle check needs three colours because…",
           ["tradition", "reaching a FINISHED node is not a cycle; reaching one on the current path is",
            "it is faster", "of recursion"], 1,
           "A diamond is not a cycle."),
        _q("Multi-source BFS starts with…",
           ["one node", "every source in the queue at distance 0", "the farthest node", "a sort"], 1,
           "Rotting oranges."),
        _q("BFS on a weighted graph finds…",
           ["the cheapest path", "the path with fewest EDGES, which may cost more", "nothing", "a cycle"], 1,
           "Weights need Dijkstra."),
    ],
    milestone="Interview rep #27 — the maze. Read a grid with a start, an exit and walls; find the shortest route with BFS, draw it on the grid by walking the parent links back, and report its length and how many cells the search explored — or say there is no way out.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w27-model", "Storing a graph",
            "An adjacency list — and the type that TypeScript guesses wrong.",
            """
The input to almost every graph question is an **edge list**: the number of nodes,
then one `u v` pair per edge. The first job is always to turn it into an
**adjacency list** — for each node, its neighbours:

```
4          0: 1 2
0 1   →    1: 0 3
0 2        2: 0
1 3        3: 1
```

```ts
const adj: number[][] = Array.from({ length: n }, (): number[] => []);
for (const [u, v] of edges) {
  adj[u]?.push(v);
  adj[v]?.push(u);         // undirected: an edge goes both ways
}
```

**Directed** graphs push only `adj[u].push(v)`. Forgetting the second push on an
undirected graph is the commonest graph bug there is: half the edges are one-way,
and traversals mysteriously miss nodes.

## `never[][]`

Leave the annotation off:

```ts
const adj = Array.from({ length: n }, () => []);
adj[u]?.push(v);
```

```
TS2345: Argument of type 'number' is not assignable to parameter of type 'never'.
```

`[]` on its own is an array of **nothing** — `never[]` — because there is nothing in
it to infer from, and it is never widened later. Annotate the variable
(`const adj: number[][]`) or, better, the callback (`(): number[] => []`), and it
is typed from the start.

## Why a list and not a matrix

An **adjacency matrix** is an n × n grid of booleans. It answers "is there an edge
u-v?" in O(1), but it costs n² cells whatever the edges: a thousand nodes with three
thousand edges is a million cells, against six thousand list entries. Real graphs
are sparse, so the list is the default.

## Degree

A node's **degree** is `adj[u].length`. In an undirected graph every edge adds 1 to
two degrees, so **the degrees sum to twice the edge count** — a quick check that
you stored every edge both ways.

> ⚠️ **Common mistakes:** one-way edges in an undirected graph; `never[][]`; and
> a matrix for a large sparse graph.
""",
            warmup=[
                _q("An undirected edge is stored…",
                   ["once", "in both nodes' lists", "in a matrix", "as a string"], 1,
                   "adj[u] gets v, adj[v] gets u."),
                _q("`Array.from({ length: n }, () => [])` gives…",
                   ["number[][]", "never[][]", "any[][]", "[][]"], 1,
                   "An empty literal infers never[]."),
                _q("The degrees of an undirected graph sum to…",
                   ["the edge count", "twice the edge count", "n", "n²"], 1,
                   "Each edge touches two nodes."),
                _q("An adjacency matrix costs…",
                   ["O(edges)", "O(n²) whatever the edges", "O(n)", "O(1)"], 1,
                   "A lot, for a sparse graph."),
            ],
            exercises=[
                _ex("tscourse-w27-gm-1", "Both directions",
                    "Store each undirected edge in both nodes' neighbour lists.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const n = Number(lines[0] ?? "0");\n'
                    'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
                    'for (const l of lines.slice(1)) {\n'
                    '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
                    '  if (u === undefined || v === undefined) {\n'
                    '    continue;\n  }\n'
                    '  adj[u]?.push(v);\n'
                    '  adj[v]?.push(u);\n}\n'
                    'adj.forEach((ns, u) => console.log(`${u}: ${ns.join(" ")}`));\n',
                    '  adj[u]?.push(v);\n'
                    '  adj[v]?.push(u);',
                    [("4\n0 1\n0 2\n1 3", "0: 1 2\n1: 0 3\n2: 0\n3: 1"), ("2\n0 1", "0: 1\n1: 0")],
                    hints=["An undirected edge can be walked from either end.",
                           "adj[u]?.push(v); and adj[v]?.push(u);"],
                    difficulty="Easy"),
                _predict("tscourse-w27-gm-p1", "What an empty row is",
                         'const n = 3;\n'
                         'const adj = Array.from({ length: n }, () => []);\n',
                         "adj", "never[][]",
                         why="There is nothing in `[]` to infer an element type from.",
                         hints=["An array literal with no elements has no element type to report.",
                                "The type that has no values at all is `never`.",
                                "Write never[][]."]),
                _diagnose("tscourse-w27-gm-d1", "The list that could hold nothing",
                          "TS2345: Argument of type 'number' is not assignable to parameter of type 'never'.",
                          _FS +
                          'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                          'const n = Number(lines[0] ?? "0");\n'
                          'const adj = Array.from({ length: n }, () => []);\n'
                          'for (const l of lines.slice(1)) {\n'
                          '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
                          '  if (u === undefined || v === undefined) {\n'
                          '    continue;\n  }\n'
                          '  adj[u]?.push(v);\n}\n'
                          'console.log(adj.map((ns) => ns.length).join(" "));\n',
                          _FS +
                          'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                          'const n = Number(lines[0] ?? "0");\n'
                          'const adj = Array.from({ length: n }, (): number[] => []);\n'
                          'for (const l of lines.slice(1)) {\n'
                          '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
                          '  if (u === undefined || v === undefined) {\n'
                          '    continue;\n  }\n'
                          '  adj[u]?.push(v);\n}\n'
                          'console.log(adj.map((ns) => ns.length).join(" "));\n',
                          [("3\n0 1\n0 2", "2 0 0")],
                          hints=["What element type did `[]` give each row?",
                                 "Tell the callback what it returns.",
                                 "Write (): number[] => []."],
                          difficulty="Medium"),
                _ex("tscourse-w27-gm-2", "In and out",
                    "In a directed graph, count the edges leaving and entering each node.",
                    _DIGRAPH +
                    'const into = new Array<number>(n).fill(0);\n'
                    'for (const ns of adj) {\n'
                    '  for (const v of ns) {\n'
                    '    into[v] = (into[v] ?? 0) + 1;\n  }\n}\n'
                    'console.log(`out ${adj.map((ns) => ns.length).join(" ")}`);\n'
                    'console.log(`in ${into.join(" ")}`);\n',
                    '    into[v] = (into[v] ?? 0) + 1;',
                    [("3\n0 1\n0 2\n1 2", "out 2 1 0\nin 0 1 2")],
                    hints=["Every edge u → v adds one to v's in-degree.",
                           "Write into[v] = (into[v] ?? 0) + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w27-gm-3", "The handshake check",
                    "Degrees of an undirected graph sum to twice the edges — confirm it.",
                    _GRAPH +
                    'const edges = lines.length - 1;\n'
                    'let degreeSum = 0;\n'
                    'for (const ns of adj) {\n'
                    '  degreeSum = degreeSum + ns.length;\n}\n'
                    'console.log(`edges=${edges} degreeSum=${degreeSum} ok=${degreeSum === 2 * edges}`);\n',
                    '  degreeSum = degreeSum + ns.length;',
                    [("4\n0 1\n0 2\n1 3", "edges=3 degreeSum=6 ok=true")],
                    hints=["A node's degree is the length of its neighbour list.",
                           "Write degreeSum = degreeSum + ns.length;"],
                    difficulty="Easy"),
                _ex("tscourse-w27-gm-4", "List or matrix",
                    "Compare the storage each would need for a sparse graph.",
                    'const n = 1000;\n'
                    'const edges = 3000;\n'
                    'const matrixCells = n * n;\n'
                    'const listEntries = 2 * edges;\n'
                    'console.log(`matrix=${matrixCells} list=${listEntries}`);\n',
                    'const listEntries = 2 * edges;',
                    [("", "matrix=1000000 list=6000")],
                    hints=["Each undirected edge appears in two lists.",
                           "Write const listEntries = 2 * edges;"],
                    difficulty="Easy"),
                _fix("tscourse-w27-gm-fix1", "Fix the edges that only went one way",
                     "The graph is undirected, but nodes 2 and 3 print empty neighbour lists and node 1 has lost its link back to 0 — each edge was stored only from its first node, so half of every connection is missing.",
                     _FS +
                     'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const n = Number(lines[0] ?? "0");\n'
                     'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
                     'for (const l of lines.slice(1)) {\n'
                     '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
                     '  if (u === undefined || v === undefined) {\n'
                     '    continue;\n  }\n'
                     '  adj[u]?.push(v);\n}\n'
                     'adj.forEach((ns, u) => console.log(`${u}: ${ns.join(" ")}`));\n',
                     _FS +
                     'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const n = Number(lines[0] ?? "0");\n'
                     'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
                     'for (const l of lines.slice(1)) {\n'
                     '  const [u, v] = l.trim().split(/\\s+/).map(Number);\n'
                     '  if (u === undefined || v === undefined) {\n'
                     '    continue;\n  }\n'
                     '  adj[u]?.push(v);\n'
                     '  adj[v]?.push(u);\n}\n'
                     'adj.forEach((ns, u) => console.log(`${u}: ${ns.join(" ")}`));\n',
                     [("4\n0 1\n0 2\n1 3", "0: 1 2\n1: 0 3\n2: 0\n3: 1")],
                     hints=["An undirected edge must be walkable from both ends.",
                            "Which list never hears about the edge?",
                            "Add adj[v]?.push(u);"],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why is the annotation better on the callback than the variable?",
                   ["it is shorter", "the value is typed where it is created, so any use of it is right",
                    "it is required", "it is faster"], 1,
                   "Either compiles; the callback is the source."),
                _q("A tree with n nodes has how many edges?",
                   ["n", "n - 1", "2n", "n²"], 1,
                   "One per node except the root."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w27-dfs", "Depth-first, plus a visited set",
            "Week 20's loop, one Set, and the things it can answer.",
            """
Recursive DFS from a start node:

```ts
const visited = new Array<boolean>(n).fill(false);
function dfs(u: number): void {
  if (visited[u]) { return; }
  visited[u] = true;
  order.push(u);
  for (const v of adj[u] ?? []) { dfs(v); }
}
```

Without the `visited` check, an undirected edge is a cycle of length two: `dfs(0)`
calls `dfs(1)`, which calls `dfs(0)`, which calls `dfs(1)` … until week 25's
`RangeError`. Every graph traversal needs it, and "mark it before you explore from
it" is the rule.

## Connected components

Start a DFS from **every node not yet visited**. Each fresh start discovers a whole
component, so the number of starts is the number of components:

```ts
let components = 0;
for (let u = 0; u < n; u = u + 1) {
  if (!visited[u]) { components = components + 1; dfs(u); }
}
```

Count the nodes each start marks, and you have component sizes too.

## Iterative, when depth matters

Recursive DFS on a long path is a long recursion. A grid of 300 × 300 open cells can
be a 90,000-deep path — week 25's stack overflow. The iterative version is week
20's loop with a Set, and it has no depth limit:

```ts
const seen = new Set<number>([start]);
const stack = [start];
while (stack.length > 0) {
  const u = stack.pop();
  if (u === undefined) { continue; }
  for (const v of adj[u] ?? []) {
    if (!seen.has(v)) { seen.add(v); stack.push(v); }
  }
}
```

It visits the same nodes, though not necessarily in the same order as the recursive
version — "depth-first" describes the shape, not one exact order.

> ⚠️ **Common mistakes:** no visited set; marking after exploring instead of
> before; and recursive DFS on input that can be a long chain.
""",
            warmup=[
                _q("Recursive DFS on an undirected graph without a visited check…",
                   ["works", "bounces along an edge until the stack overflows", "is BFS", "skips nodes"], 1,
                   "Every edge is a two-node cycle."),
                _q("The number of connected components equals…",
                   ["n", "the number of fresh DFS starts from unvisited nodes", "the edge count", "1"], 1,
                   "Each start finds one whole component."),
                _q("Iterative DFS exists because…",
                   ["it is faster", "recursion depth can exceed the stack on long paths", "it is BFS", "of types"], 1,
                   "Week 25."),
                _q("Two correct DFS implementations always visit nodes in the same order.",
                   ["true", "false — only the set visited is guaranteed", "only on trees", "only recursively"], 1,
                   "Order depends on details."),
            ],
            exercises=[
                _ex("tscourse-w27-df-1", "Never twice",
                    "Return at once if the node was already visited.",
                    _GRAPH +
                    'const visited = new Array<boolean>(n).fill(false);\n'
                    'const order: number[] = [];\n'
                    'function dfs(u: number): void {\n'
                    '  if (visited[u]) {\n'
                    '    return;\n  }\n'
                    '  visited[u] = true;\n'
                    '  order.push(u);\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    dfs(v);\n  }\n}\n'
                    'dfs(0);\n'
                    'console.log(order.join(" "));\n',
                    '  if (visited[u]) {\n'
                    '    return;\n  }',
                    [("5\n0 1\n0 2\n1 3\n2 3\n3 4", "0 1 3 2 4"), ("3\n0 1\n1 2\n2 0", "0 1 2")],
                    hints=["A node reached a second time has nothing new to offer.",
                           "if (visited[u]) { return; }"],
                    difficulty="Easy"),
                _ex("tscourse-w27-df-2", "Count the components",
                    "Start a traversal from every node not yet reached; each start is a new component.",
                    _GRAPH +
                    'const visited = new Array<boolean>(n).fill(false);\n'
                    'function dfs(u: number): void {\n'
                    '  if (visited[u]) {\n'
                    '    return;\n  }\n'
                    '  visited[u] = true;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    dfs(v);\n  }\n}\n'
                    'let components = 0;\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (!visited[u]) {\n'
                    '    components = components + 1;\n'
                    '    dfs(u);\n  }\n}\n'
                    'console.log(components);\n',
                    '  if (!visited[u]) {\n'
                    '    components = components + 1;\n'
                    '    dfs(u);\n  }',
                    [("5\n0 1\n2 3", "3"), ("4\n0 1\n1 2\n2 3", "1"), ("3", "3")],
                    hints=["A node nobody has reached yet is the first of a new component.",
                           "Count it, then traverse from it so the rest of its component is marked."],
                    difficulty="Medium"),
                _ex("tscourse-w27-df-3", "Iteratively",
                    "DFS with a stack and a Set: mark a node when you first push it.",
                    _GRAPH +
                    'const seen = new Set<number>([0]);\n'
                    'const stack = [0];\n'
                    'while (stack.length > 0) {\n'
                    '  const u = stack.pop();\n'
                    '  if (u === undefined) {\n'
                    '    continue;\n  }\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (!seen.has(v)) {\n'
                    '      seen.add(v);\n'
                    '      stack.push(v);\n    }\n  }\n}\n'
                    'console.log(`reached ${seen.size} of ${n}`);\n',
                    '    if (!seen.has(v)) {\n'
                    '      seen.add(v);\n'
                    '      stack.push(v);\n    }',
                    [("5\n0 1\n1 2\n3 4", "reached 3 of 5"), ("2\n0 1", "reached 2 of 2")],
                    hints=["Only an unseen neighbour is worth pushing — and it is seen from the moment it is pushed.",
                           "if (!seen.has(v)) { seen.add(v); stack.push(v); }"],
                    difficulty="Medium"),
                _ex("tscourse-w27-df-4", "Component sizes",
                    "Report every component's size, largest first.",
                    _GRAPH +
                    'const visited = new Array<boolean>(n).fill(false);\n'
                    'function size(u: number): number {\n'
                    '  if (visited[u]) {\n'
                    '    return 0;\n  }\n'
                    '  visited[u] = true;\n'
                    '  let total = 1;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    total = total + size(v);\n  }\n'
                    '  return total;\n}\n'
                    'const sizes: number[] = [];\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (!visited[u]) {\n'
                    '    sizes.push(size(u));\n  }\n}\n'
                    'console.log(sizes.sort((a, b) => b - a).join(" "));\n',
                    '    total = total + size(v);',
                    [("6\n0 1\n1 2\n3 4", "3 2 1"), ("2", "1 1")],
                    hints=["A component's size is 1 for this node plus whatever each neighbour's traversal adds.",
                           "Already-visited neighbours contribute 0.",
                           "Write total = total + size(v);"],
                    difficulty="Medium"),
                _ex("tscourse-w27-df-5", "Can you get there?",
                    "Report whether the last node is reachable from node 0.",
                    _GRAPH +
                    'const seen = new Set<number>([0]);\n'
                    'const stack = [0];\n'
                    'while (stack.length > 0) {\n'
                    '  const u = stack.pop();\n'
                    '  if (u === undefined) {\n'
                    '    continue;\n  }\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (!seen.has(v)) {\n'
                    '      seen.add(v);\n'
                    '      stack.push(v);\n    }\n  }\n}\n'
                    'console.log(seen.has(n - 1) ? "yes" : "no");\n',
                    'console.log(seen.has(n - 1) ? "yes" : "no");',
                    [("4\n0 1\n1 3", "yes"), ("4\n0 1\n2 3", "no")],
                    hints=["Everything reachable ends up in `seen`.",
                           'Write console.log(seen.has(n - 1) ? "yes" : "no");'],
                    difficulty="Easy"),
                _fix("tscourse-w27-df-fix1", "Fix the traversal that never stopped",
                     "This dies with `RangeError: Maximum call stack size exceeded`. There is no visited check, so the undirected edge between 0 and 1 is walked 0 → 1 → 0 → 1 … for ever.",
                     _GRAPH +
                     'const order: number[] = [];\n'
                     'function dfs(u: number): void {\n'
                     '  order.push(u);\n'
                     '  for (const v of adj[u] ?? []) {\n'
                     '    dfs(v);\n  }\n}\n'
                     'dfs(0);\n'
                     'console.log(order.join(" "));\n',
                     _GRAPH +
                     'const visited = new Array<boolean>(n).fill(false);\n'
                     'const order: number[] = [];\n'
                     'function dfs(u: number): void {\n'
                     '  if (visited[u]) {\n'
                     '    return;\n  }\n'
                     '  visited[u] = true;\n'
                     '  order.push(u);\n'
                     '  for (const v of adj[u] ?? []) {\n'
                     '    dfs(v);\n  }\n}\n'
                     'dfs(0);\n'
                     'console.log(order.join(" "));\n',
                     [("3\n0 1\n1 2", "0 1 2"), ("2\n0 1", "0 1")],
                     hints=["On a tree this would work. What does an undirected graph have that a tree walk never met?",
                            "Every edge leads back the way you came.",
                            "Keep a visited array; return at once for a node already in it."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("`seen.add(v)` happens when v is pushed, not when popped, because…",
                   ["style", "otherwise v can be pushed many times before it is popped once", "of types", "it is DFS"], 1,
                   "Mark on discovery."),
                _q("Why do both DFS versions reach the same SET but maybe not the same ORDER?",
                   ["a bug", "the recursion and the stack take neighbours in different orders", "randomness",
                    "the Set"], 1,
                   "Both are depth-first."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w27-bfs", "Breadth-first, and shortest paths",
            "A queue instead of a stack — and the first arrival is the shortest.",
            """
Swap the stack for week 18's head-index queue and the traversal goes **level by
level**: everything one edge away, then everything two away, and so on.

```ts
const dist = new Array<number>(n).fill(-1);      // -1: not reached
dist[start] = 0;
const queue = [start];
for (let head = 0; head < queue.length; head = head + 1) {
  const u = queue[head] ?? 0;
  for (const v of adj[u] ?? []) {
    if (dist[v] === -1) {
      dist[v] = (dist[u] ?? 0) + 1;
      queue.push(v);
    }
  }
}
```

`dist` doubles as the visited set: -1 means "not reached".

## Why it finds shortest paths

Every node at distance d is dequeued before any node at distance d + 1 is even
**discovered**, so the first time BFS reaches a node, it is by a route with the
fewest possible edges. DFS has no such property: it will happily reach a neighbour
of the start by a ten-edge detour first. **For "fewest steps", BFS is the answer**,
and this is the reason.

## The path, not just its length

Record where each node was reached **from**:

```ts
parent[v] = u;
```

Then walk back from the target — `t, parent[t], parent[parent[t]] …` — until the
start, and reverse. Week 26's reconstruction, on a graph.

## Mark when you enqueue

The check `dist[v] === -1` happens **before** pushing, and `dist[v]` is set
immediately. Mark on *dequeue* instead and a node can be pushed once by every
neighbour that sees it before it is processed — the answers stay right, but the
queue fills with duplicates and the work multiplies. The month's counting habit is
how you see it: count what enters the queue.

## A queue, never `shift`

Week 18 counted what `shift()` costs: every call moves the whole array. A BFS over
a hundred thousand nodes with `shift` is quadratic. The head index is not an
optimisation, it is the correct data structure.

> ⚠️ **Common mistakes:** marking on dequeue; `shift` as a queue; and using DFS
> when the question says "fewest" or "shortest".
""",
            warmup=[
                _q("BFS uses…",
                   ["a stack", "a queue", "recursion", "a heap"], 1,
                   "Level by level."),
                _q("The first time BFS reaches a node, it is by…",
                   ["some path", "a path with the fewest edges", "the longest path", "a random path"], 1,
                   "Distance d before d + 1."),
                _q("A path is rebuilt from…",
                   ["the queue", "parent links, walked back from the target", "the distances", "the stack"], 1,
                   "Then reversed."),
                _q("Marking visited on DEQUEUE…",
                   ["is required", "lets a node enter the queue several times", "is faster", "breaks BFS order"], 1,
                   "Mark on enqueue."),
            ],
            exercises=[
                _ex("tscourse-w27-bf-1", "One further than where you came from",
                    "Set each newly reached node's distance and queue it.",
                    _GRAPH +
                    'const dist = new Array<number>(n).fill(-1);\n'
                    'dist[0] = 0;\n'
                    'const queue = [0];\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (dist[v] === -1) {\n'
                    '      dist[v] = (dist[u] ?? 0) + 1;\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'console.log(dist.join(" "));\n',
                    '      dist[v] = (dist[u] ?? 0) + 1;\n'
                    '      queue.push(v);',
                    [("5\n0 1\n0 2\n1 3\n2 3\n3 4", "0 1 1 2 3"), ("4\n0 1\n2 3", "0 1 -1 -1")],
                    hints=["A neighbour reached from u for the first time is one edge further than u.",
                           "Record its distance, then queue it."],
                    difficulty="Easy"),
                _ex("tscourse-w27-bf-2", "Walk the parents back",
                    "Rebuild the shortest path from node 0 to the last node.",
                    _GRAPH +
                    'const parent = new Array<number>(n).fill(-1);\n'
                    'const seen = new Array<boolean>(n).fill(false);\n'
                    'seen[0] = true;\n'
                    'const queue = [0];\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (!seen[v]) {\n'
                    '      seen[v] = true;\n'
                    '      parent[v] = u;\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'const target = n - 1;\n'
                    'if (!seen[target]) {\n'
                    '  console.log("unreachable");\n'
                    '} else {\n'
                    '  const path: number[] = [];\n'
                    '  for (let at = target; at !== -1; at = parent[at] ?? -1) {\n'
                    '    path.push(at);\n  }\n'
                    '  console.log(path.reverse().join(" -> "));\n}\n',
                    '  for (let at = target; at !== -1; at = parent[at] ?? -1) {\n'
                    '    path.push(at);\n  }',
                    [("5\n0 1\n0 2\n1 3\n2 3\n3 4", "0 -> 1 -> 3 -> 4"), ("3\n0 2", "0 -> 2"),
                     ("3\n0 1", "unreachable")],
                    hints=["Start at the target and follow parent links until there is no parent (-1).",
                           "The start's parent is -1, so the walk ends there.",
                           "Collect as you go; reverse at the end."],
                    difficulty="Medium"),
                _ex("tscourse-w27-bf-3", "How many at each distance",
                    "Report the size of every BFS level.",
                    _GRAPH +
                    'const dist = new Array<number>(n).fill(-1);\n'
                    'dist[0] = 0;\n'
                    'const queue = [0];\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (dist[v] === -1) {\n'
                    '      dist[v] = (dist[u] ?? 0) + 1;\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'const levels: number[] = [];\n'
                    'for (const d of dist) {\n'
                    '  if (d >= 0) {\n'
                    '    levels[d] = (levels[d] ?? 0) + 1;\n  }\n}\n'
                    'console.log(levels.join(" "));\n',
                    '    levels[d] = (levels[d] ?? 0) + 1;',
                    [("6\n0 1\n0 2\n1 3\n2 4\n4 5", "1 2 2 1"), ("1", "1")],
                    hints=["Each reached node adds one to the count for its distance.",
                           "Write levels[d] = (levels[d] ?? 0) + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w27-bf-4", "Depth-first is not shortest",
                    "Compare the path length DFS happens to find with BFS's shortest one.",
                    _GRAPH +
                    'const dfsDepth = new Array<number>(n).fill(-1);\n'
                    'function dfs(u: number, d: number): void {\n'
                    '  if (dfsDepth[u] !== -1) {\n'
                    '    return;\n  }\n'
                    '  dfsDepth[u] = d;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    dfs(v, d + 1);\n  }\n}\n'
                    'dfs(0, 0);\n'
                    'const dist = new Array<number>(n).fill(-1);\n'
                    'dist[0] = 0;\n'
                    'const queue = [0];\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (dist[v] === -1) {\n'
                    '      dist[v] = (dist[u] ?? 0) + 1;\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'const t = n - 1;\n'
                    'console.log(`dfs=${dfsDepth[t] ?? -1} bfs=${dist[t] ?? -1}`);\n',
                    '    dfs(v, d + 1);',
                    [("5\n0 1\n1 2\n2 3\n3 4\n0 4", "dfs=4 bfs=1")],
                    hints=["Each recursive step is one edge deeper.",
                           "Write dfs(v, d + 1);"],
                    difficulty="Medium"),
                _fix("tscourse-w27-bf-fix1", "Fix the queue full of duplicates",
                     "Every node should enter the queue once — five nodes, five entries — and this reports 6. The distances happen to come out right, but a node is only marked when it is taken OFF the queue, so every neighbour that sees it first queues it again.",
                     _GRAPH +
                     'const dist = new Array<number>(n).fill(-1);\n'
                     'const queue = [0];\n'
                     'const depth = [0];\n'
                     'for (let head = 0; head < queue.length; head = head + 1) {\n'
                     '  const u = queue[head] ?? 0;\n'
                     '  if (dist[u] !== -1) {\n'
                     '    continue;\n  }\n'
                     '  dist[u] = depth[head] ?? 0;\n'
                     '  for (const v of adj[u] ?? []) {\n'
                     '    if (dist[v] === -1) {\n'
                     '      queue.push(v);\n'
                     '      depth.push((dist[u] ?? 0) + 1);\n    }\n  }\n}\n'
                     'console.log(`${dist.join(" ")} enqueued=${queue.length}`);\n',
                     _GRAPH +
                     'const dist = new Array<number>(n).fill(-1);\n'
                     'dist[0] = 0;\n'
                     'const queue = [0];\n'
                     'for (let head = 0; head < queue.length; head = head + 1) {\n'
                     '  const u = queue[head] ?? 0;\n'
                     '  for (const v of adj[u] ?? []) {\n'
                     '    if (dist[v] === -1) {\n'
                     '      dist[v] = (dist[u] ?? 0) + 1;\n'
                     '      queue.push(v);\n    }\n  }\n}\n'
                     'console.log(`${dist.join(" ")} enqueued=${queue.length}`);\n',
                     [("5\n0 1\n0 2\n1 3\n2 3\n3 4", "0 1 1 2 3 enqueued=5")],
                     hints=["Between being queued and being processed, a node looks unvisited to everyone else.",
                            "Mark it the moment it is discovered.",
                            "Set dist[v] as you push v, and drop the separate depth array."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is `shift` wrong for a BFS queue?",
                   ["it is buggy", "each call moves the whole array, making BFS quadratic", "it is not typed",
                    "it reverses order"], 1,
                   "Week 18's count."),
                _q("`dist` filled with -1 also serves as…",
                   ["the queue", "the visited set", "the parent array", "the answer"], 1,
                   "-1 means not reached."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w27-grids", "Grids are graphs",
            "Cells are nodes; the four neighbours are the edges.",
            """
A grid needs no adjacency list. The neighbours of `(r, c)` are computed:

```ts
const DIRS = [[-1, 0], [1, 0], [0, -1], [0, 1]];     // up, down, left, right
for (const [dr, dc] of DIRS) {
  const nr = r + dr;
  const nc = c + dc;
  if (nr < 0 || nr >= R || nc < 0 || nc >= C) { continue; }    // off the board
  // (nr, nc) is a neighbour
}
```

The bounds check is the whole difficulty. Everything else is lesson 2 or lesson 3.

## Naming a cell

A visited set needs a key per cell. Two choices:

* **A string**, `` `${r},${c}` `` — week 19's canonical key. Readable, a little slow.
* **A number**, `r * C + c` — an index into a flat `boolean[]`. Fast.

The number has one trap. The cell to the **left** of `id` is `id - 1` — **unless the
cell is in column 0**, in which case `id - 1` is the last cell of the *previous row*.
Compute neighbours from `(r, c)` and bounds-check them, then convert to an id; never
do arithmetic on the id to find a neighbour.

## Islands

"Count the islands of `#` in a grid of `.`": for every land cell not yet visited,
count one and flood out from it — lesson 2's components, on cells. Use the iterative
stack: a 300 × 300 all-land grid is a 90,000-cell flood, too deep to recurse.

## The shortest way through a maze

BFS from the start over open cells; the distance at the exit is the answer. This is
the capstone.

> ⚠️ **Common mistakes:** a missing half of the bounds check; `id - 1` as the left
> neighbour; and recursive flood fill on a large grid.
""",
            warmup=[
                _q("The four neighbours of (r, c) need…",
                   ["nothing", "a bounds check before use", "sorting", "a Map"], 1,
                   "Or you read off the board."),
                _q("With id = r * C + c, the left neighbour of a column-0 cell is…",
                   ["id - 1", "off the board", "id + 1", "id - C"], 1,
                   "id - 1 is the previous row's last cell."),
                _q("Counting islands is counting…",
                   ["cells", "connected components of land", "edges", "rows"], 1,
                   "Lesson 2, on cells."),
                _q("Flood fill on a large grid should be…",
                   ["recursive", "iterative, with an explicit stack or queue", "sorted", "memoised"], 1,
                   "Depth can be R × C."),
            ],
            exercises=[
                _ex("tscourse-w27-gd-1", "Stay on the board",
                    "Count the islands of `#`, skipping any neighbour off the grid.",
                    _CHARGRID +
                    'const seen = new Set<string>();\n'
                    'let islands = 0;\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if (cell(r, c) !== "#" || seen.has(`${r},${c}`)) {\n'
                    '      continue;\n    }\n'
                    '    islands = islands + 1;\n'
                    '    seen.add(`${r},${c}`);\n'
                    '    const stack: (readonly [number, number])[] = [[r, c]];\n'
                    '    while (stack.length > 0) {\n'
                    '      const top = stack.pop();\n'
                    '      if (top === undefined) {\n'
                    '        continue;\n      }\n'
                    '      for (const [dr, dc] of DIRS) {\n'
                    '        const nr = top[0] + dr;\n'
                    '        const nc = top[1] + dc;\n'
                    '        if (nr < 0 || nr >= R || nc < 0 || nc >= C) {\n'
                    '          continue;\n        }\n'
                    '        if (cell(nr, nc) === "#" && !seen.has(`${nr},${nc}`)) {\n'
                    '          seen.add(`${nr},${nc}`);\n'
                    '          stack.push([nr, nc]);\n        }\n      }\n    }\n  }\n}\n'
                    'console.log(islands);\n',
                    '        if (nr < 0 || nr >= R || nc < 0 || nc >= C) {\n'
                    '          continue;\n        }',
                    [("##..\n#..#\n...#", "2"), ("#.#\n.#.\n#.#", "5"), ("...", "0")],
                    hints=["A neighbour is only real if its row is in 0..R-1 and its column in 0..C-1.",
                           "Four comparisons, one `continue`."],
                    difficulty="Medium"),
                _ex("tscourse-w27-gd-2", "The biggest island",
                    "Flood each island with a queue and keep the largest size.",
                    _CHARGRID +
                    'const seen = new Set<string>();\n'
                    'let biggest = 0;\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if (cell(r, c) !== "#" || seen.has(`${r},${c}`)) {\n'
                    '      continue;\n    }\n'
                    '    seen.add(`${r},${c}`);\n'
                    '    const queue: (readonly [number, number])[] = [[r, c]];\n'
                    '    for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '      const [cr, cc] = queue[head] ?? [0, 0];\n'
                    '      for (const [dr, dc] of DIRS) {\n'
                    '        const nr = cr + dr;\n'
                    '        const nc = cc + dc;\n'
                    '        if (cell(nr, nc) === "#" && !seen.has(`${nr},${nc}`)) {\n'
                    '          seen.add(`${nr},${nc}`);\n'
                    '          queue.push([nr, nc]);\n        }\n      }\n    }\n'
                    '    biggest = Math.max(biggest, queue.length);\n  }\n}\n'
                    'console.log(biggest);\n',
                    '    biggest = Math.max(biggest, queue.length);',
                    [("##..\n#..#\n...#", "3"), ("###\n###", "6")],
                    hints=["Every cell of the island passed through the queue exactly once.",
                           "Write biggest = Math.max(biggest, queue.length);"],
                    difficulty="Medium"),
                _ex("tscourse-w27-gd-3", "Flood fill",
                    "Repaint the region connected to the top-left cell.",
                    _CHARGRID +
                    'const out = grid.map((row) => [...row]);\n'
                    'const from = cell(0, 0);\n'
                    'const stack: (readonly [number, number])[] = [[0, 0]];\n'
                    'if (out[0] !== undefined) {\n'
                    '  out[0][0] = "x";\n}\n'
                    'while (stack.length > 0) {\n'
                    '  const top = stack.pop();\n'
                    '  if (top === undefined) {\n'
                    '    continue;\n  }\n'
                    '  for (const [dr, dc] of DIRS) {\n'
                    '    const nr = top[0] + dr;\n'
                    '    const nc = top[1] + dc;\n'
                    '    const row = out[nr];\n'
                    '    if (row !== undefined && row[nc] === from) {\n'
                    '      row[nc] = "x";\n'
                    '      stack.push([nr, nc]);\n    }\n  }\n}\n'
                    'console.log(out.map((row) => row.join("")).join("\\n"));\n',
                    '    if (row !== undefined && row[nc] === from) {\n'
                    '      row[nc] = "x";\n'
                    '      stack.push([nr, nc]);\n    }',
                    [("..#\n.##\n#..", "xx#\nx##\n#.."), ("aa\naa", "xx\nxx")],
                    hints=["A neighbour of the original colour becomes part of the region — repaint it before pushing, so it is never pushed twice.",
                           "Repainting IS the visited mark here."],
                    difficulty="Medium"),
                _ex("tscourse-w27-gd-4", "The shortest way across",
                    "BFS from the top-left to the bottom-right over `.` cells; report the steps or -1.",
                    _CHARGRID +
                    'const dist = new Map<string, number>([["0,0", 0]]);\n'
                    'const queue: (readonly [number, number])[] = [[0, 0]];\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const [r, c] = queue[head] ?? [0, 0];\n'
                    '  const d = dist.get(`${r},${c}`) ?? 0;\n'
                    '  for (const [dr, dc] of DIRS) {\n'
                    '    const nr = r + dr;\n'
                    '    const nc = c + dc;\n'
                    '    if (cell(nr, nc) === "." && !dist.has(`${nr},${nc}`)) {\n'
                    '      dist.set(`${nr},${nc}`, d + 1);\n'
                    '      queue.push([nr, nc]);\n    }\n  }\n}\n'
                    'console.log(dist.get(`${R - 1},${C - 1}`) ?? -1);\n',
                    '    if (cell(nr, nc) === "." && !dist.has(`${nr},${nc}`)) {\n'
                    '      dist.set(`${nr},${nc}`, d + 1);\n'
                    '      queue.push([nr, nc]);\n    }',
                    [("...\n.#.\n...", "4"), (".#\n#.", "-1"), ("....\n###.\n....", "5")],
                    hints=["An open cell nobody has reached is one step further than the current one.",
                           "Set its distance as you queue it."],
                    difficulty="Medium"),
                _ex("tscourse-w27-gd-5", "A number for every cell",
                    "Key cells by r * C + c in a flat boolean array, and count the open cells reachable from the top-left.",
                    _CHARGRID +
                    'const seen = new Array<boolean>(R * C).fill(false);\n'
                    'seen[0] = true;\n'
                    'const stack: (readonly [number, number])[] = [[0, 0]];\n'
                    'let reached = 1;\n'
                    'while (stack.length > 0) {\n'
                    '  const top = stack.pop();\n'
                    '  if (top === undefined) {\n'
                    '    continue;\n  }\n'
                    '  for (const [dr, dc] of DIRS) {\n'
                    '    const nr = top[0] + dr;\n'
                    '    const nc = top[1] + dc;\n'
                    '    const id = nr * C + nc;\n'
                    '    if (cell(nr, nc) === "." && !seen[id]) {\n'
                    '      seen[id] = true;\n'
                    '      reached = reached + 1;\n'
                    '      stack.push([nr, nc]);\n    }\n  }\n}\n'
                    'console.log(reached);\n',
                    '    const id = nr * C + nc;',
                    [("..#\n.#.\n...", "7"), (".#.\n##.", "1")],
                    hints=["Row-major order: each row is C cells long.",
                           "Write const id = nr * C + nc;"],
                    difficulty="Easy"),
                _fix("tscourse-w27-gd-fix1", "Fix the left neighbour that wrapped round",
                     "This finds 1 island in a grid that has 2. Neighbours are found by arithmetic on the cell's number — `id - 1` for left — so the first cell of row 1 treats the LAST cell of row 0 as its neighbour, and two islands on opposite edges are joined.",
                     _CHARGRID +
                     'const seen = new Array<boolean>(R * C).fill(false);\n'
                     'function isLand(id: number): boolean {\n'
                     '  return id >= 0 && id < R * C && cell(Math.floor(id / C), id % C) === "#";\n}\n'
                     'let islands = 0;\n'
                     'for (let start = 0; start < R * C; start = start + 1) {\n'
                     '  if (!isLand(start) || seen[start]) {\n'
                     '    continue;\n  }\n'
                     '  islands = islands + 1;\n'
                     '  seen[start] = true;\n'
                     '  const stack = [start];\n'
                     '  while (stack.length > 0) {\n'
                     '    const id = stack.pop() ?? 0;\n'
                     '    for (const next of [id - C, id + C, id - 1, id + 1]) {\n'
                     '      if (isLand(next) && !seen[next]) {\n'
                     '        seen[next] = true;\n'
                     '        stack.push(next);\n      }\n    }\n  }\n}\n'
                     'console.log(islands);\n',
                     _CHARGRID +
                     'const seen = new Array<boolean>(R * C).fill(false);\n'
                     'let islands = 0;\n'
                     'for (let r = 0; r < R; r = r + 1) {\n'
                     '  for (let c = 0; c < C; c = c + 1) {\n'
                     '    if (cell(r, c) !== "#" || seen[r * C + c]) {\n'
                     '      continue;\n    }\n'
                     '    islands = islands + 1;\n'
                     '    seen[r * C + c] = true;\n'
                     '    const stack: (readonly [number, number])[] = [[r, c]];\n'
                     '    while (stack.length > 0) {\n'
                     '      const top = stack.pop();\n'
                     '      if (top === undefined) {\n'
                     '        continue;\n      }\n'
                     '      for (const [dr, dc] of DIRS) {\n'
                     '        const nr = top[0] + dr;\n'
                     '        const nc = top[1] + dc;\n'
                     '        if (cell(nr, nc) === "#" && !seen[nr * C + nc]) {\n'
                     '          seen[nr * C + nc] = true;\n'
                     '          stack.push([nr, nc]);\n        }\n      }\n    }\n  }\n}\n'
                     'console.log(islands);\n',
                     [("..#\n#..", "2"), ("#.#\n#.#", "2")],
                     hints=["Where is `id - 1` when the cell is in column 0?",
                            "The row boundary is invisible to arithmetic on the id.",
                            "Find neighbours from (r, c) with a bounds check, and only then convert to an id."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("Why does `cell()` return \"\" off the board rather than throwing?",
                   ["style", "so a neighbour off the edge simply fails the `=== \"#\"` test", "speed", "types"], 1,
                   "The bounds check folded into the lookup."),
                _q("A 300 × 300 all-land grid flooded recursively…",
                   ["is fine", "may be 90,000 frames deep — week 25's overflow", "is O(1)", "cannot happen"], 1,
                   "Iterate."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w27-order", "Cycles and topological order",
            "Directed graphs: what must come before what — and when nothing can.",
            """
In a **directed** graph, an edge `u → v` often means "u must come before v": a
prerequisite, a dependency, a build step. A **topological order** lists every node
so that every edge points forwards. It exists exactly when there is **no cycle** —
a graph like that is a **DAG**.

## Kahn's algorithm

A node with **in-degree 0** has nothing that must precede it, so it can go first:

```ts
// indegree[v] = number of edges into v
queue every node with in-degree 0
while the queue is not empty:
  take u; output it
  for each edge u → v: indegree[v] -= 1; if it reaches 0, queue v
```

Removing `u` removes its edges, which may free its successors. `0→1, 0→2, 1→3, 2→3`
gives `0 1 2 3`.

**And it detects cycles for free**: nodes on a cycle wait on each other and never
reach in-degree 0, so the output comes up **short**. Output shorter than n means a
cycle — "these courses can never be taken".

## Cycles by DFS: three colours

In an undirected graph, reaching a visited node means a cycle. In a **directed** one
it does not — `0→1, 0→2, 1→3, 2→3` reaches 3 twice and has no cycle (a diamond).
The fix is to distinguish *why* a node was seen:

* **white** — not visited yet
* **grey** — visited, and **still on the current path** (its DFS has not finished)
* **black** — finished

Reaching a **grey** node means you have come back round to something you are still
inside: a cycle. Reaching a black one is just a second route to a finished node.

## A DP over a topological order

"Each course takes one semester; how many semesters at minimum?" Process nodes in
topological order and let `level[v] = max(level[v], level[u] + 1)`. Every
prerequisite is finished before the course is reached — which is exactly the
dependency order week 26 said a table must be filled in. The answer is the longest
path in the DAG.

> ⚠️ **Common mistakes:** an undirected-style visited check on a directed graph
> (every diamond becomes a "cycle"); forgetting that Kahn's short output is the
> cycle signal; and edges pointing the wrong way.
""",
            warmup=[
                _q("A topological order exists when the graph…",
                   ["is connected", "has no directed cycle", "is undirected", "is a tree"], 1,
                   "A DAG."),
                _q("Kahn's algorithm begins with…",
                   ["node 0", "every node of in-degree 0", "the deepest node", "a DFS"], 1,
                   "Nothing must come before them."),
                _q("Kahn's output has fewer than n nodes. That means…",
                   ["a bug", "a cycle", "a disconnected graph", "an undirected graph"], 1,
                   "The cycle's nodes never reach 0."),
                _q("In the three-colour DFS, reaching a GREY node means…",
                   ["nothing", "a cycle", "a finished node", "an error"], 1,
                   "You came back to your own path."),
            ],
            exercises=[
                _ex("tscourse-w27-tp-1", "Free the successors",
                    "When a node is output, remove its edges and queue any successor that has nothing left before it.",
                    _DIGRAPH +
                    'const indegree = new Array<number>(n).fill(0);\n'
                    'for (const ns of adj) {\n'
                    '  for (const v of ns) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) + 1;\n  }\n}\n'
                    'const queue: number[] = [];\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (indegree[u] === 0) {\n'
                    '    queue.push(u);\n  }\n}\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'console.log(queue.length === n ? queue.join(" ") : "cycle");\n',
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      queue.push(v);\n    }',
                    [("4\n0 1\n0 2\n1 3\n2 3", "0 1 2 3"), ("3\n2 1\n1 0", "2 1 0")],
                    hints=["u is done, so every v it points to has one fewer thing to wait for.",
                           "When v's count reaches zero, it can be queued."],
                    difficulty="Medium"),
                _ex("tscourse-w27-tp-2", "Short output is a cycle",
                    "Report `cycle` when Kahn's algorithm cannot place every node.",
                    _DIGRAPH +
                    'const indegree = new Array<number>(n).fill(0);\n'
                    'for (const ns of adj) {\n'
                    '  for (const v of ns) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) + 1;\n  }\n}\n'
                    'const queue: number[] = [];\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (indegree[u] === 0) {\n'
                    '    queue.push(u);\n  }\n}\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'console.log(queue.length === n ? queue.join(" ") : `cycle: ${n - queue.length} stuck`);\n',
                    'console.log(queue.length === n ? queue.join(" ") : `cycle: ${n - queue.length} stuck`);',
                    [("3\n0 1\n1 2\n2 0", "cycle: 3 stuck"), ("4\n0 1\n1 2\n2 1\n2 3", "cycle: 3 stuck"),
                     ("2\n0 1", "0 1")],
                    hints=["Every node that never reached in-degree 0 is stuck behind a cycle.",
                           "Compare how many were placed with n."],
                    difficulty="Easy"),
                _ex("tscourse-w27-tp-3", "Grey means cycle",
                    "In a three-colour DFS, reaching a node that is still on the current path is a cycle.",
                    _DIGRAPH +
                    'const colour = new Array<number>(n).fill(0);\n'
                    'function hasCycle(u: number): boolean {\n'
                    '  colour[u] = 1;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    if (colour[v] === 1) {\n'
                    '      return true;\n    }\n'
                    '    if (colour[v] === 0 && hasCycle(v)) {\n'
                    '      return true;\n    }\n  }\n'
                    '  colour[u] = 2;\n'
                    '  return false;\n}\n'
                    'let cycle = false;\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (colour[u] === 0 && hasCycle(u)) {\n'
                    '    cycle = true;\n  }\n}\n'
                    'console.log(cycle ? "cycle" : "no cycle");\n',
                    '    if (colour[v] === 1) {\n'
                    '      return true;\n    }',
                    [("4\n0 1\n0 2\n1 3\n2 3", "no cycle"), ("3\n0 1\n1 2\n2 0", "cycle"), ("2\n0 1\n1 0", "cycle")],
                    hints=["Grey (1) is 'visited, and its DFS has not finished' — it is an ancestor of u.",
                           "An edge back to an ancestor closes a loop.",
                           "if (colour[v] === 1) { return true; }"],
                    difficulty="Hard"),
                _ex("tscourse-w27-tp-4", "The fewest semesters",
                    "Walk the topological order and push each course's level to its successors.",
                    _DIGRAPH +
                    'const indegree = new Array<number>(n).fill(0);\n'
                    'for (const ns of adj) {\n'
                    '  for (const v of ns) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) + 1;\n  }\n}\n'
                    'const level = new Array<number>(n).fill(1);\n'
                    'const queue: number[] = [];\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (indegree[u] === 0) {\n'
                    '    queue.push(u);\n  }\n}\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const u = queue[head] ?? 0;\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    level[v] = Math.max(level[v] ?? 1, (level[u] ?? 1) + 1);\n'
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'console.log(Math.max(...level));\n',
                    '    level[v] = Math.max(level[v] ?? 1, (level[u] ?? 1) + 1);',
                    [("4\n0 1\n0 2\n1 3\n2 3", "3"), ("5\n0 1\n1 2\n2 3\n3 4", "5"), ("3", "1")],
                    hints=["A course can be taken the semester after its latest prerequisite.",
                           "Write level[v] = Math.max(level[v] ?? 1, (level[u] ?? 1) + 1);"],
                    difficulty="Hard"),
                _fix("tscourse-w27-tp-fix1", "Fix the diamond that was called a cycle",
                     "`0→1, 0→2, 1→3, 2→3` has no cycle, and this reports one. It uses the undirected rule — 'reached an already-visited node' — but node 3 is simply reached by two routes. In a directed graph only a node still ON the current path closes a cycle.",
                     _DIGRAPH +
                     'const visited = new Array<boolean>(n).fill(false);\n'
                     'function hasCycle(u: number): boolean {\n'
                     '  visited[u] = true;\n'
                     '  for (const v of adj[u] ?? []) {\n'
                     '    if (visited[v]) {\n'
                     '      return true;\n    }\n'
                     '    if (hasCycle(v)) {\n'
                     '      return true;\n    }\n  }\n'
                     '  return false;\n}\n'
                     'let cycle = false;\n'
                     'for (let u = 0; u < n; u = u + 1) {\n'
                     '  if (!visited[u] && hasCycle(u)) {\n'
                     '    cycle = true;\n  }\n}\n'
                     'console.log(cycle ? "cycle" : "no cycle");\n',
                     _DIGRAPH +
                     'const colour = new Array<number>(n).fill(0);\n'
                     'function hasCycle(u: number): boolean {\n'
                     '  colour[u] = 1;\n'
                     '  for (const v of adj[u] ?? []) {\n'
                     '    if (colour[v] === 1) {\n'
                     '      return true;\n    }\n'
                     '    if (colour[v] === 0 && hasCycle(v)) {\n'
                     '      return true;\n    }\n  }\n'
                     '  colour[u] = 2;\n'
                     '  return false;\n}\n'
                     'let cycle = false;\n'
                     'for (let u = 0; u < n; u = u + 1) {\n'
                     '  if (colour[u] === 0 && hasCycle(u)) {\n'
                     '    cycle = true;\n  }\n}\n'
                     'console.log(cycle ? "cycle" : "no cycle");\n',
                     [("4\n0 1\n0 2\n1 3\n2 3", "no cycle"), ("3\n0 1\n1 2\n2 0", "cycle")],
                     hints=["Node 3 is reached from 1 and then again from 2. Is that a loop?",
                            "You need to know whether a visited node is still being explored or already finished.",
                            "Three states: 0 unseen, 1 on the current path, 2 finished. Only 1 is a cycle."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("The 'fewest semesters' answer is…",
                   ["the node count", "the longest path in the DAG", "the shortest path", "the number of edges"], 1,
                   "Each step of the chain is one more semester."),
                _q("Topological order is unique when…",
                   ["always", "the queue never holds more than one node", "the graph is small", "never"], 1,
                   "Otherwise several orders are correct."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w27-levels", "Many sources, two colours",
            "Two BFS variations that turn up constantly.",
            """
## Multi-source BFS

"A grid of oranges: `2` is rotten, `1` fresh, `0` empty. Each minute, rot spreads to
the four neighbours. How long until every orange is rotten?"

The trap is to BFS from one rotten orange. Rot spreads from **all** of them at once,
so **every** rotten orange starts in the queue at time 0:

```ts
for each cell: if it is rotten, queue it with time 0
// then an ordinary BFS
```

BFS then spreads outward from all sources together, level by level, and the level
at which the last fresh orange falls is the answer — or -1 if some fresh orange is
never reached. Distance-to-the-nearest-anything is the same move.

## Two-colouring

"Can the nodes be split into two groups with every edge between the groups?" —
seating people who dislike each other at two tables, or scheduling in two shifts.
BFS, colouring each newly reached node the **opposite** colour of the node it came
from. If an edge ever joins two nodes of the **same** colour, it is impossible.

A graph is two-colourable exactly when it has **no odd cycle**: a square is fine,
a triangle is not.

Colour every component — start a BFS from each uncoloured node, as lesson 2 counted
components — or an isolated part of the graph is never checked.

> ⚠️ **Common mistakes:** a single source where there are many; forgetting the -1
> for an unreachable target; and checking only the first component.
""",
            warmup=[
                _q("Multi-source BFS starts with…",
                   ["one source", "every source in the queue at distance 0", "the farthest node", "a sorted list"], 1,
                   "Spreading from all at once."),
                _q("A graph is two-colourable exactly when it has…",
                   ["no cycle", "no odd cycle", "an even number of nodes", "one component"], 1,
                   "A triangle fails."),
                _q("Two-colouring must start a BFS from…",
                   ["node 0 only", "every uncoloured node, so every component is checked", "the largest node", "a leaf"], 1,
                   "Components again."),
                _q("Rotting oranges returns -1 when…",
                   ["no orange is rotten", "some fresh orange is never reached", "the grid is empty", "never"], 1,
                   "Unreachable."),
            ],
            exercises=[
                _ex("tscourse-w27-lv-1", "Every source at once",
                    "Queue every rotten orange before the BFS begins.",
                    _CHARGRID +
                    'const time = new Map<string, number>();\n'
                    'const queue: (readonly [number, number])[] = [];\n'
                    'let fresh = 0;\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if (cell(r, c) === "2") {\n'
                    '      time.set(`${r},${c}`, 0);\n'
                    '      queue.push([r, c]);\n'
                    '    } else if (cell(r, c) === "1") {\n'
                    '      fresh = fresh + 1;\n    }\n  }\n}\n'
                    'let latest = 0;\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const [r, c] = queue[head] ?? [0, 0];\n'
                    '  const t = time.get(`${r},${c}`) ?? 0;\n'
                    '  for (const [dr, dc] of DIRS) {\n'
                    '    const nr = r + dr;\n'
                    '    const nc = c + dc;\n'
                    '    if (cell(nr, nc) === "1" && !time.has(`${nr},${nc}`)) {\n'
                    '      time.set(`${nr},${nc}`, t + 1);\n'
                    '      latest = Math.max(latest, t + 1);\n'
                    '      fresh = fresh - 1;\n'
                    '      queue.push([nr, nc]);\n    }\n  }\n}\n'
                    'console.log(fresh === 0 ? latest : -1);\n',
                    '    if (cell(r, c) === "2") {\n'
                    '      time.set(`${r},${c}`, 0);\n'
                    '      queue.push([r, c]);',
                    [("211\n110\n011", "4"), ("211\n011\n101", "-1"), ("201\n102", "1")],
                    hints=["Every rotten orange is a source, and all of them are at time 0.",
                           "Record time 0 and queue it, for each one."],
                    difficulty="Medium"),
                _ex("tscourse-w27-lv-2", "Opposite colours",
                    "Colour each newly reached node the opposite of its neighbour; a same-colour edge makes it impossible.",
                    _GRAPH +
                    'const colour = new Array<number>(n).fill(-1);\n'
                    'let ok = true;\n'
                    'for (let s = 0; s < n; s = s + 1) {\n'
                    '  if (colour[s] !== -1) {\n'
                    '    continue;\n  }\n'
                    '  colour[s] = 0;\n'
                    '  const queue = [s];\n'
                    '  for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '    const u = queue[head] ?? 0;\n'
                    '    for (const v of adj[u] ?? []) {\n'
                    '      if (colour[v] === -1) {\n'
                    '        colour[v] = 1 - (colour[u] ?? 0);\n'
                    '        queue.push(v);\n'
                    '      } else if (colour[v] === colour[u]) {\n'
                    '        ok = false;\n      }\n    }\n  }\n}\n'
                    'console.log(ok ? "two tables" : "impossible");\n',
                    '        colour[v] = 1 - (colour[u] ?? 0);',
                    [("4\n0 1\n1 2\n2 3\n3 0", "two tables"), ("3\n0 1\n1 2\n2 0", "impossible"),
                     ("5\n0 1\n3 4\n2 3\n2 4", "impossible")],
                    hints=["Colours are 0 and 1, so the opposite of c is 1 - c.",
                           "Write colour[v] = 1 - (colour[u] ?? 0);"],
                    difficulty="Medium"),
                _ex("tscourse-w27-lv-3", "Distance to the nearest exit",
                    "Multi-source BFS from every `E`; print each open cell's distance to the nearest one.",
                    _CHARGRID +
                    'const dist: number[][] = Array.from({ length: R }, (): number[] => new Array<number>(C).fill(-1));\n'
                    'const queue: (readonly [number, number])[] = [];\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if (cell(r, c) === "E") {\n'
                    '      const row = dist[r];\n'
                    '      if (row !== undefined) {\n'
                    '        row[c] = 0;\n      }\n'
                    '      queue.push([r, c]);\n    }\n  }\n}\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const [r, c] = queue[head] ?? [0, 0];\n'
                    '  const d = dist[r]?.[c] ?? 0;\n'
                    '  for (const [dr, dc] of DIRS) {\n'
                    '    const nr = r + dr;\n'
                    '    const nc = c + dc;\n'
                    '    const row = dist[nr];\n'
                    '    if (cell(nr, nc) === "." && row !== undefined && row[nc] === -1) {\n'
                    '      row[nc] = d + 1;\n'
                    '      queue.push([nr, nc]);\n    }\n  }\n}\n'
                    'console.log(dist.map((row, r) => row.map((d, c) => (cell(r, c) === "#" ? "#" : String(d))).join(" ")).join("\\n"));\n',
                    '      row[nc] = d + 1;\n'
                    '      queue.push([nr, nc]);',
                    [("E..\n.#.\n..E", "0 1 2\n1 # 1\n2 1 0"), ("E.#.", "0 1 # -1")],
                    hints=["A cell first reached from distance d is at distance d + 1 from its nearest exit.",
                           "Record it and queue it."],
                    difficulty="Medium"),
                _fix("tscourse-w27-lv-fix1", "Fix the rot that started in one place",
                     "Rot spreads from every rotten orange at once. For `2 1 1 2` (one row) the answer is 1 minute; this reports 2, because the BFS was seeded with only the FIRST rotten orange and the second one never spreads.",
                     _CHARGRID +
                     'const time = new Map<string, number>();\n'
                     'const queue: (readonly [number, number])[] = [];\n'
                     'for (let r = 0; r < R && queue.length === 0; r = r + 1) {\n'
                     '  for (let c = 0; c < C; c = c + 1) {\n'
                     '    if (cell(r, c) === "2") {\n'
                     '      time.set(`${r},${c}`, 0);\n'
                     '      queue.push([r, c]);\n'
                     '      break;\n    }\n  }\n}\n'
                     'let latest = 0;\n'
                     'for (let head = 0; head < queue.length; head = head + 1) {\n'
                     '  const [r, c] = queue[head] ?? [0, 0];\n'
                     '  const t = time.get(`${r},${c}`) ?? 0;\n'
                     '  for (const [dr, dc] of DIRS) {\n'
                     '    const nr = r + dr;\n'
                     '    const nc = c + dc;\n'
                     '    const here = cell(nr, nc);\n'
                     '    if ((here === "1" || here === "2") && !time.has(`${nr},${nc}`)) {\n'
                     '      time.set(`${nr},${nc}`, t + 1);\n'
                     '      if (here === "1") {\n'
                     '        latest = Math.max(latest, t + 1);\n      }\n'
                     '      queue.push([nr, nc]);\n    }\n  }\n}\n'
                     'console.log(latest);\n',
                     _CHARGRID +
                     'const time = new Map<string, number>();\n'
                     'const queue: (readonly [number, number])[] = [];\n'
                     'for (let r = 0; r < R; r = r + 1) {\n'
                     '  for (let c = 0; c < C; c = c + 1) {\n'
                     '    if (cell(r, c) === "2") {\n'
                     '      time.set(`${r},${c}`, 0);\n'
                     '      queue.push([r, c]);\n    }\n  }\n}\n'
                     'let latest = 0;\n'
                     'for (let head = 0; head < queue.length; head = head + 1) {\n'
                     '  const [r, c] = queue[head] ?? [0, 0];\n'
                     '  const t = time.get(`${r},${c}`) ?? 0;\n'
                     '  for (const [dr, dc] of DIRS) {\n'
                     '    const nr = r + dr;\n'
                     '    const nc = c + dc;\n'
                     '    const here = cell(nr, nc);\n'
                     '    if ((here === "1" || here === "2") && !time.has(`${nr},${nc}`)) {\n'
                     '      time.set(`${nr},${nc}`, t + 1);\n'
                     '      if (here === "1") {\n'
                     '        latest = Math.max(latest, t + 1);\n      }\n'
                     '      queue.push([nr, nc]);\n    }\n  }\n}\n'
                     'console.log(latest);\n',
                     [("2112", "1"), ("21\n12", "1")],
                     hints=["How many rotten oranges start in the queue?",
                            "Every source must be at time 0 before the BFS runs.",
                            "Queue every rotten orange — drop the early exit."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why not run one BFS per rotten orange and take the minimum?",
                   ["it is wrong", "it gives the right answer but costs one BFS per source", "it is faster",
                    "it cannot"], 1,
                   "Multi-source does it in one pass."),
                _q("A square is two-colourable and a triangle is not because…",
                   ["size", "a triangle is an odd cycle", "a square is a tree", "luck"], 1,
                   "Colours must alternate round the loop."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w27-weighted", "When edges have weights",
            "BFS counts edges. Dijkstra counts cost — and week 28 makes it fast.",
            """
BFS's guarantee is "fewest **edges**". Give edges a **cost** and that is no longer the
question:

```
0 —4— 1 —1— 3
 \\     |
  1    1
   \\   |
    2 —
```

The fewest edges from 0 to 3 is `0 → 1 → 3` (two edges, cost **5**). The cheapest is
`0 → 2 → 1 → 3` (three edges, cost **3**). BFS returns the first one.

## Dijkstra

Keep a tentative distance for every node, all ∞ except the start at 0. Repeatedly:

1. **settle** the unsettled node with the **smallest** tentative distance — its
   distance is now final;
2. **relax** its edges: for each `u → v` with weight w,
   `dist[v] = min(dist[v], dist[u] + w)`.

Why is the smallest safe to settle? Every other route to it would go through some
node that is already at least as far — and with **non-negative** weights, going
further can never make it cheaper. (Negative weights break exactly that argument,
and need a different algorithm.)

## The cost, and why week 28 exists

Step 1, done by scanning every node, is O(V) — and it happens V times: **O(V²)**.
That is fine for a few hundred nodes and far too slow for a road network. What step 1
needs is a structure that hands back **the smallest** item quickly as items keep
arriving. That structure is a **priority queue**, built on a **heap**, and it is week
28's first lesson. With it Dijkstra is O((V + E) log V).

## Choosing

| the question | the tool |
|---|---|
| reachable? components? | DFS or BFS |
| fewest steps / edges | BFS |
| cheapest total with non-negative costs | Dijkstra |
| order respecting prerequisites | topological sort |
| cycle in a directed graph | three colours, or Kahn |
| can it be split in two | BFS two-colouring |

> ⚠️ **Common mistakes:** BFS on weighted edges; relaxing without settling the
> smallest first; and assuming Dijkstra works with negative weights.
""",
            warmup=[
                _q("BFS on a weighted graph returns…",
                   ["the cheapest path", "the path with fewest edges", "nothing", "the longest path"], 1,
                   "Which may cost more."),
                _q("Dijkstra always settles next…",
                   ["the newest node", "the unsettled node with the smallest tentative distance", "node 0",
                    "the largest"], 1,
                   "Its distance is then final."),
                _q("Dijkstra needs weights that are…",
                   ["integers", "non-negative", "distinct", "small"], 1,
                   "A negative edge can undercut a settled node."),
                _q("Array-scan Dijkstra costs…",
                   ["O(V)", "O(V²)", "O(E)", "O(log V)"], 1,
                   "Week 28's heap brings it down."),
            ],
            exercises=[
                _ex("tscourse-w27-wt-1", "Relax the edges",
                    "After settling a node, offer each neighbour a cheaper route through it.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const n = Number(lines[0] ?? "0");\n'
                    'const adj: (readonly [number, number])[][] = Array.from({ length: n }, (): (readonly [number, number])[] => []);\n'
                    'for (const l of lines.slice(1)) {\n'
                    '  const [u, v, w] = l.trim().split(/\\s+/).map(Number);\n'
                    '  if (u === undefined || v === undefined || w === undefined) {\n'
                    '    continue;\n  }\n'
                    '  adj[u]?.push([v, w]);\n'
                    '  adj[v]?.push([u, w]);\n}\n'
                    'const dist = new Array<number>(n).fill(Infinity);\n'
                    'const settled = new Array<boolean>(n).fill(false);\n'
                    'dist[0] = 0;\n'
                    'for (let round = 0; round < n; round = round + 1) {\n'
                    '  let u = -1;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    if (!settled[i] && (u === -1 || (dist[i] ?? Infinity) < (dist[u] ?? Infinity))) {\n'
                    '      u = i;\n    }\n  }\n'
                    '  if (u === -1 || dist[u] === Infinity) {\n'
                    '    break;\n  }\n'
                    '  settled[u] = true;\n'
                    '  for (const [v, w] of adj[u] ?? []) {\n'
                    '    dist[v] = Math.min(dist[v] ?? Infinity, (dist[u] ?? 0) + w);\n  }\n}\n'
                    'console.log(dist.map((d) => (d === Infinity ? "-" : String(d))).join(" "));\n',
                    '    dist[v] = Math.min(dist[v] ?? Infinity, (dist[u] ?? 0) + w);',
                    [("4\n0 1 4\n0 2 1\n2 1 1\n1 3 1", "0 2 1 3"), ("3\n0 1 5", "0 5 -")],
                    hints=["Going to v through u costs dist[u] + w. Keep it if it is cheaper.",
                           "Write dist[v] = Math.min(dist[v] ?? Infinity, (dist[u] ?? 0) + w);"],
                    difficulty="Hard"),
                _ex("tscourse-w27-wt-2", "Settle the nearest",
                    "Find the unsettled node with the smallest tentative distance.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const n = Number(lines[0] ?? "0");\n'
                    'const adj: (readonly [number, number])[][] = Array.from({ length: n }, (): (readonly [number, number])[] => []);\n'
                    'for (const l of lines.slice(1)) {\n'
                    '  const [u, v, w] = l.trim().split(/\\s+/).map(Number);\n'
                    '  if (u === undefined || v === undefined || w === undefined) {\n'
                    '    continue;\n  }\n'
                    '  adj[u]?.push([v, w]);\n'
                    '  adj[v]?.push([u, w]);\n}\n'
                    'const dist = new Array<number>(n).fill(Infinity);\n'
                    'const settled = new Array<boolean>(n).fill(false);\n'
                    'dist[0] = 0;\n'
                    'let scans = 0;\n'
                    'for (let round = 0; round < n; round = round + 1) {\n'
                    '  let u = -1;\n'
                    '  for (let i = 0; i < n; i = i + 1) {\n'
                    '    scans = scans + 1;\n'
                    '    if (!settled[i] && (u === -1 || (dist[i] ?? Infinity) < (dist[u] ?? Infinity))) {\n'
                    '      u = i;\n    }\n  }\n'
                    '  if (u === -1 || dist[u] === Infinity) {\n'
                    '    break;\n  }\n'
                    '  settled[u] = true;\n'
                    '  for (const [v, w] of adj[u] ?? []) {\n'
                    '    dist[v] = Math.min(dist[v] ?? Infinity, (dist[u] ?? 0) + w);\n  }\n}\n'
                    'console.log(`to last=${dist[n - 1] ?? -1} scans=${scans}`);\n',
                    '    if (!settled[i] && (u === -1 || (dist[i] ?? Infinity) < (dist[u] ?? Infinity))) {\n'
                    '      u = i;\n    }',
                    [("4\n0 1 4\n0 2 1\n2 1 1\n1 3 1", "to last=3 scans=16")],
                    hints=["Among nodes not yet settled, keep the one whose distance is smallest.",
                           "The first unsettled node found is the starting candidate (u === -1)."],
                    difficulty="Hard"),
                _ex("tscourse-w27-wt-3", "Name the tool",
                    "Map each question to the algorithm that answers it.",
                    _NUMS +
                    'function tool(kind: number): string {\n'
                    '  if (kind === 1) {\n'
                    '    return "BFS";\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return "Dijkstra";\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return "topological sort";\n  }\n'
                    '  return "DFS";\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} ${tool(k)}`);\n}\n',
                    '  if (kind === 2) {\n'
                    '    return "Dijkstra";\n  }',
                    [("1 2 3 4", "1 BFS\n2 Dijkstra\n3 topological sort\n4 DFS")],
                    hints=["Kind 2 is 'cheapest total cost, costs non-negative'.",
                           'Write if (kind === 2) { return "Dijkstra"; }'],
                    difficulty="Easy"),
                _fix("tscourse-w27-wt-fix1", "Fix the route that took fewest roads, not least cost",
                     "The cheapest way from 0 to 3 costs 3 (0 → 2 → 1 → 3). This reports 5: it is a BFS, so it settles each node the first time it is reached — by the fewest edges — and 0 → 1 → 3 has fewer edges. Costs need Dijkstra.",
                     _FS +
                     'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const n = Number(lines[0] ?? "0");\n'
                     'const adj: (readonly [number, number])[][] = Array.from({ length: n }, (): (readonly [number, number])[] => []);\n'
                     'for (const l of lines.slice(1)) {\n'
                     '  const [u, v, w] = l.trim().split(/\\s+/).map(Number);\n'
                     '  if (u === undefined || v === undefined || w === undefined) {\n'
                     '    continue;\n  }\n'
                     '  adj[u]?.push([v, w]);\n'
                     '  adj[v]?.push([u, w]);\n}\n'
                     'const cost = new Array<number>(n).fill(-1);\n'
                     'cost[0] = 0;\n'
                     'const queue = [0];\n'
                     'for (let head = 0; head < queue.length; head = head + 1) {\n'
                     '  const u = queue[head] ?? 0;\n'
                     '  for (const [v, w] of adj[u] ?? []) {\n'
                     '    if (cost[v] === -1) {\n'
                     '      cost[v] = (cost[u] ?? 0) + w;\n'
                     '      queue.push(v);\n    }\n  }\n}\n'
                     'console.log(cost[n - 1] ?? -1);\n',
                     _FS +
                     'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const n = Number(lines[0] ?? "0");\n'
                     'const adj: (readonly [number, number])[][] = Array.from({ length: n }, (): (readonly [number, number])[] => []);\n'
                     'for (const l of lines.slice(1)) {\n'
                     '  const [u, v, w] = l.trim().split(/\\s+/).map(Number);\n'
                     '  if (u === undefined || v === undefined || w === undefined) {\n'
                     '    continue;\n  }\n'
                     '  adj[u]?.push([v, w]);\n'
                     '  adj[v]?.push([u, w]);\n}\n'
                     'const cost = new Array<number>(n).fill(Infinity);\n'
                     'const settled = new Array<boolean>(n).fill(false);\n'
                     'cost[0] = 0;\n'
                     'for (let round = 0; round < n; round = round + 1) {\n'
                     '  let u = -1;\n'
                     '  for (let i = 0; i < n; i = i + 1) {\n'
                     '    if (!settled[i] && (u === -1 || (cost[i] ?? Infinity) < (cost[u] ?? Infinity))) {\n'
                     '      u = i;\n    }\n  }\n'
                     '  if (u === -1 || cost[u] === Infinity) {\n'
                     '    break;\n  }\n'
                     '  settled[u] = true;\n'
                     '  for (const [v, w] of adj[u] ?? []) {\n'
                     '    cost[v] = Math.min(cost[v] ?? Infinity, (cost[u] ?? 0) + w);\n  }\n}\n'
                     'console.log(cost[n - 1] === Infinity ? -1 : cost[n - 1] ?? -1);\n',
                     [("4\n0 1 4\n0 2 1\n2 1 1\n1 3 1", "3"), ("2\n0 1 7", "7")],
                     hints=["BFS fixes a node's value the first time it is reached. Is the first route the cheapest?",
                            "Settle nodes in order of cost, not in order of discovery.",
                            "Dijkstra: settle the cheapest unsettled node, then relax its edges."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("If every edge weighs 1, Dijkstra and BFS give…",
                   ["different answers", "the same distances", "an error", "nothing"], 1,
                   "BFS is Dijkstra with unit weights."),
                _q("What does Dijkstra need that an array scan provides slowly?",
                   ["sorting", "the smallest item, repeatedly, as items arrive — a priority queue",
                    "a Set", "recursion"], 1,
                   "Week 28."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #27 — the maze",
        """
Find the shortest way through a maze, draw it, and report what the search cost.

Input: the maze, one row per line. `S` is the start, `E` the exit, `#` a wall and
`.` open floor. Moves are up, down, left and right.

```
S.#.
..#.
#...
..#E
```

```
S.#.
**#.
#***
..#E
steps 6  explored 10
```

**The rules:**

* BFS from `S`, trying neighbours in the order **up, down, left, right**, and
  recording each cell's parent the first time it is reached. With that order fixed,
  the path is fully determined.
* Walk the parents back from `E` and mark every cell on the way with `*` — not `S`
  or `E` themselves.
* `steps` is the number of moves. `explored` is how many cells were **taken off the
  queue** before `E` was — the start included, `E` not.
* If `E` cannot be reached, print the maze unchanged, then
  `no way out  explored N`, where N is every cell the search reached.

**What makes it a rep:** it is lessons 3 and 4 together — a grid as a graph, BFS for
fewest steps, parent links for the path — and `explored` is the month's counting
habit applied to a search: in the second test the exit is two columns from the start,
behind a wall, and the search explores every floor cell before it arrives.
""",
        _ch("tscourse-w27-capstone", "Interview rep #27", "Hard",
            "Find the shortest route through the maze with BFS, draw it with `*`, and report its "
            "length and how many cells the search explored.",
            _FS +
            'const maze: readonly string[] = fs.readFileSync(0, "utf8").trim().split("\\n").map((l) => l.trim());\n'
            'const R = maze.length;\n'
            'const C = (maze[0] ?? "").length;\n'
            'function at(r: number, c: number): string {\n'
            '  if (r < 0 || r >= R || c < 0 || c >= C) {\n'
            '    return "#";\n  }\n'
            '  return (maze[r] ?? "").charAt(c);\n}\n'
            'let start: readonly [number, number] = [0, 0];\n'
            'for (let r = 0; r < R; r = r + 1) {\n'
            '  for (let c = 0; c < C; c = c + 1) {\n'
            '    if (at(r, c) === "S") {\n'
            '      start = [r, c];\n    }\n  }\n}\n'
            'const DIRS: readonly (readonly [number, number])[] = [[-1, 0], [1, 0], [0, -1], [0, 1]];\n'
            'const parent = new Map<string, string>();\n'
            'const seen = new Set<string>([`${start[0]},${start[1]}`]);\n'
            'const queue: (readonly [number, number])[] = [start];\n'
            'let explored = 0;\n'
            'let exit: readonly [number, number] | null = null;\n'
            'for (let head = 0; head < queue.length; head = head + 1) {\n'
            '  const [r, c] = queue[head] ?? [0, 0];\n'
            '  if (at(r, c) === "E") {\n'
            '    exit = [r, c];\n'
            '    break;\n  }\n'
            '  explored = explored + 1;\n'
            '  for (const [dr, dc] of DIRS) {\n'
            '    const nr = r + dr;\n'
            '    const nc = c + dc;\n'
            '    const key = `${nr},${nc}`;\n'
            '    if (at(nr, nc) !== "#" && !seen.has(key)) {\n'
            '      seen.add(key);\n'
            '      parent.set(key, `${r},${c}`);\n'
            '      queue.push([nr, nc]);\n    }\n  }\n}\n'
            'const out = maze.map((row) => [...row]);\n'
            'if (exit === null) {\n'
            '  console.log(maze.join("\\n"));\n'
            '  console.log(`no way out  explored ${explored}`);\n'
            '} else {\n'
            '  let steps = 0;\n'
            '  let key = parent.get(`${exit[0]},${exit[1]}`);\n'
            '  steps = steps + 1;\n'
            '  while (key !== undefined && key !== `${start[0]},${start[1]}`) {\n'
            '    const [r, c] = key.split(",").map(Number);\n'
            '    const row = out[r ?? 0];\n'
            '    if (row !== undefined) {\n'
            '      row[c ?? 0] = "*";\n    }\n'
            '    steps = steps + 1;\n'
            '    key = parent.get(key);\n  }\n'
            '  console.log(out.map((row) => row.join("")).join("\\n"));\n'
            '  console.log(`steps ${steps}  explored ${explored}`);\n}\n',
            'const parent = new Map<string, string>();\n'
            'const seen = new Set<string>([`${start[0]},${start[1]}`]);\n'
            'const queue: (readonly [number, number])[] = [start];\n'
            'let explored = 0;\n'
            'let exit: readonly [number, number] | null = null;\n'
            'for (let head = 0; head < queue.length; head = head + 1) {\n'
            '  const [r, c] = queue[head] ?? [0, 0];\n'
            '  if (at(r, c) === "E") {\n'
            '    exit = [r, c];\n'
            '    break;\n  }\n'
            '  explored = explored + 1;\n'
            '  for (const [dr, dc] of DIRS) {\n'
            '    const nr = r + dr;\n'
            '    const nc = c + dc;\n'
            '    const key = `${nr},${nc}`;\n'
            '    if (at(nr, nc) !== "#" && !seen.has(key)) {\n'
            '      seen.add(key);\n'
            '      parent.set(key, `${r},${c}`);\n'
            '      queue.push([nr, nc]);\n    }\n  }\n}\n'
            'const out = maze.map((row) => [...row]);\n'
            'if (exit === null) {\n'
            '  console.log(maze.join("\\n"));\n'
            '  console.log(`no way out  explored ${explored}`);\n'
            '} else {\n'
            '  let steps = 0;\n'
            '  let key = parent.get(`${exit[0]},${exit[1]}`);\n'
            '  steps = steps + 1;\n'
            '  while (key !== undefined && key !== `${start[0]},${start[1]}`) {\n'
            '    const [r, c] = key.split(",").map(Number);\n'
            '    const row = out[r ?? 0];\n'
            '    if (row !== undefined) {\n'
            '      row[c ?? 0] = "*";\n    }\n'
            '    steps = steps + 1;\n'
            '    key = parent.get(key);\n  }\n'
            '  console.log(out.map((row) => row.join("")).join("\\n"));\n'
            '  console.log(`steps ${steps}  explored ${explored}`);\n}',
            [("S.#.\n..#.\n#...\n..#E", "S.#.\n**#.\n#***\n..#E\nsteps 6  explored 10"),
             ("S#E\n.#.\n...", "S#E\n*#*\n***\nsteps 6  explored 6"),
             ("S#E", "S#E\nno way out  explored 1"),
             ("SE", "SE\nsteps 1  explored 1")],
            hints=["Treat anything off the board as a wall, and the neighbour order up, down, left, right is then the whole of the determinism.",
                   "Record a cell's parent the moment it is first queued — never overwrite it.",
                   "`explored` counts dequeues, and the loop stops the moment E is dequeued.",
                   "Walk parents back from E; mark every cell you land on until you reach S.",
                   "Steps: one for each parent link walked.",
                   "`let exit = null` assigned inside the loop IS narrowed correctly here — the loop is not a nested function, unlike week 25's stretch."]),
        example_io="S.#.\n**#.\n#***\n..#E\nsteps 6  explored 10",
        rubric=["the maze is searched with BFS over a head-index queue",
                "neighbours are tried in the stated order, so the path is determined",
                "each cell's parent is recorded once, when first reached",
                "the path is rebuilt from parent links, not searched for again",
                "explored counts dequeued cells, stopping at the exit",
                "an unreachable exit prints the maze unchanged and the explored count",
                "no index access is asserted with `!`"],
        stretch=_ch("tscourse-w27-capstone-stretch", "Interview rep #27 (stretch)", "Hard",
                    "The course planner. The first line is the number of courses; each later line `a b` means "
                    "course a must come before course b. Print a valid order in which, whenever several "
                    "courses are available, the **smallest-numbered** is taken first; then the fewest "
                    "`semesters` needed if any number of courses can be taken at once. If the prerequisites "
                    "contain a cycle, print `impossible: N courses stuck` instead.",
                    _DIGRAPH +
                    'const indegree = new Array<number>(n).fill(0);\n'
                    'for (const ns of adj) {\n'
                    '  for (const v of ns) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) + 1;\n  }\n}\n'
                    'const level = new Array<number>(n).fill(1);\n'
                    'const available: number[] = [];\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (indegree[u] === 0) {\n'
                    '    available.push(u);\n  }\n}\n'
                    'const order: number[] = [];\n'
                    'while (available.length > 0) {\n'
                    '  available.sort((a, b) => a - b);\n'
                    '  const u = available.shift() ?? 0;\n'
                    '  order.push(u);\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    level[v] = Math.max(level[v] ?? 1, (level[u] ?? 1) + 1);\n'
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      available.push(v);\n    }\n  }\n}\n'
                    'if (order.length < n) {\n'
                    '  console.log(`impossible: ${n - order.length} courses stuck`);\n'
                    '} else {\n'
                    '  console.log(`order ${order.join(" ")}`);\n'
                    '  console.log(`semesters ${n === 0 ? 0 : Math.max(...level)}`);\n}\n',
                    'const order: number[] = [];\n'
                    'while (available.length > 0) {\n'
                    '  available.sort((a, b) => a - b);\n'
                    '  const u = available.shift() ?? 0;\n'
                    '  order.push(u);\n'
                    '  for (const v of adj[u] ?? []) {\n'
                    '    level[v] = Math.max(level[v] ?? 1, (level[u] ?? 1) + 1);\n'
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      available.push(v);\n    }\n  }\n}',
                    [("4\n3 1\n3 2\n1 0\n2 0", "order 3 1 2 0\nsemesters 3"),
                     ("5\n0 4\n1 4\n2 3", "order 0 1 2 3 4\nsemesters 2"),
                     ("3\n0 1\n1 2\n2 1", "impossible: 2 courses stuck")],
                    hints=["Kahn's algorithm, with the queue replaced by 'the available set, smallest first'.",
                           "Sorting the available list before each pick is O(V² log V) — fine at this size, and week 28's heap does it properly.",
                           "`shift` is acceptable here only because the list is tiny; say why in a comment if you use it.",
                           "Semesters is the longest chain: a course's level is one more than its latest prerequisite's."]),
    ),
))
