/**
 * The algorithms behind the Trees & Graphs labs (`UnitLab.tsx`): a binary tree
 * typed in level order, a graph typed as an edge list, and a backtracking
 * search over a few items. Everything here is pure and returns plain data —
 * orders, statistics, and for the graph and search labs a list of *steps*, so
 * the page can scrub through an algorithm's run rather than only show its end.
 */

// ------------------------------------------------------------------ trees

export interface TreeNodeRec {
  id: number;
  val: number;
  left: number; // -1 for none
  right: number;
  parent: number;
}

export interface ParsedTree {
  nodes: TreeNodeRec[];
  /** -1 for the empty tree. */
  root: number;
}

/** Parse the level-order encoding the problems use (`null` for a missing
 * child). Returns null on a malformed token. */
export function parseTree(line: string, maxNodes = 63): ParsedTree | null {
  const toks = line.trim().split(/[\s,]+/).filter(Boolean);
  if (toks.length === 0 || toks[0] === "null") return { nodes: [], root: -1 };
  const num = (t: string) => (/^-?\d+$/.test(t) ? Number(t) : NaN);
  if (Number.isNaN(num(toks[0]))) return null;
  const nodes: TreeNodeRec[] = [{ id: 0, val: num(toks[0]), left: -1, right: -1, parent: -1 }];
  const q = [0];
  let head = 0;
  let i = 1;
  while (head < q.length && i < toks.length) {
    const p = q[head++];
    for (const side of ["left", "right"] as const) {
      if (i >= toks.length) break;
      const t = toks[i++];
      if (t === "null") continue;
      const v = num(t);
      if (Number.isNaN(v)) return null;
      if (nodes.length >= maxNodes) return null;
      const id = nodes.length;
      nodes.push({ id, val: v, left: -1, right: -1, parent: p });
      nodes[p][side] = id;
      q.push(id);
    }
  }
  return { nodes, root: 0 };
}

export interface TreeOrders {
  pre: number[];
  in: number[];
  post: number[];
  level: number[];
}

/** The four traversal orders, as node ids. */
export function treeOrders(t: ParsedTree): TreeOrders {
  const pre: number[] = [], ino: number[] = [], post: number[] = [], level: number[] = [];
  const go = (x: number) => {
    if (x < 0) return;
    pre.push(x);
    go(t.nodes[x].left);
    ino.push(x);
    go(t.nodes[x].right);
    post.push(x);
  };
  go(t.root);
  if (t.root >= 0) {
    const q = [t.root];
    for (let h = 0; h < q.length; h++) {
      const x = q[h];
      level.push(x);
      for (const c of [t.nodes[x].left, t.nodes[x].right]) if (c >= 0) q.push(c);
    }
  }
  return { pre, in: ino, post, level };
}

export interface NodeInfo {
  depth: number;
  height: number;
  size: number;
  /** The open BST interval the node must lie in, as the root path imposes it. */
  lo: number | null;
  hi: number | null;
  inRange: boolean;
  path: number[];
}

/** Height (in nodes), subtree size and depth for every node. */
function measure(t: ParsedTree) {
  const n = t.nodes.length;
  const height = new Array(n).fill(0), size = new Array(n).fill(0), depth = new Array(n).fill(0);
  const order = treeOrders(t).post;
  for (const x of order) {
    const { left, right } = t.nodes[x];
    height[x] = 1 + Math.max(left >= 0 ? height[left] : 0, right >= 0 ? height[right] : 0);
    size[x] = 1 + (left >= 0 ? size[left] : 0) + (right >= 0 ? size[right] : 0);
  }
  for (const x of treeOrders(t).pre) {
    const p = t.nodes[x].parent;
    depth[x] = p < 0 ? 0 : depth[p] + 1;
  }
  return { height, size, depth };
}

export function nodeInfo(t: ParsedTree, id: number): NodeInfo {
  const m = measure(t);
  const path: number[] = [];
  for (let x = id; x >= 0; x = t.nodes[x].parent) path.unshift(x);
  let lo: number | null = null, hi: number | null = null;
  for (let i = 0; i + 1 < path.length; i++) {
    const a = t.nodes[path[i]], next = path[i + 1];
    if (a.left === next) hi = hi === null ? a.val : Math.min(hi, a.val);
    else lo = lo === null ? a.val : Math.max(lo, a.val);
  }
  const v = t.nodes[id].val;
  const inRange = (lo === null || v > lo) && (hi === null || v < hi);
  return { depth: m.depth[id], height: m.height[id], size: m.size[id], lo, hi, inRange, path };
}

export interface TreeStats {
  size: number;
  height: number;
  leaves: number;
  /** Longest path, counted in edges. */
  diameter: number;
  balanced: boolean;
  /** The first node (in pre-order) outside its BST interval, or -1 when the
   * tree is a valid BST (strict: no equal values). */
  bstBreaker: number;
}

export function treeStats(t: ParsedTree): TreeStats {
  if (t.root < 0) return { size: 0, height: 0, leaves: 0, diameter: 0, balanced: true, bstBreaker: -1 };
  const m = measure(t);
  const h = (x: number) => (x >= 0 ? m.height[x] : 0);
  let diameter = 0, balanced = true, leaves = 0;
  for (const nd of t.nodes) {
    diameter = Math.max(diameter, h(nd.left) + h(nd.right));
    if (Math.abs(h(nd.left) - h(nd.right)) > 1) balanced = false;
    if (nd.left < 0 && nd.right < 0) leaves++;
  }
  let bstBreaker = -1;
  for (const x of treeOrders(t).pre) {
    if (!nodeInfo(t, x).inRange) {
      bstBreaker = x;
      break;
    }
  }
  return { size: t.nodes.length, height: m.height[t.root], leaves, diameter, balanced, bstBreaker };
}

export interface Descent {
  path: number[];
  found: boolean;
  /** Where an insert would attach: the parent id and side, or null when found / empty. */
  attach: { parent: number; side: "left" | "right" } | null;
}

/** The BST descent a search (and an insert) for `v` follows. */
export function bstDescent(t: ParsedTree, v: number): Descent {
  const path: number[] = [];
  let x = t.root;
  let last = -1, side: "left" | "right" = "left";
  while (x >= 0) {
    path.push(x);
    const nd = t.nodes[x];
    if (v === nd.val) return { path, found: true, attach: null };
    last = x;
    side = v < nd.val ? "left" : "right";
    x = v < nd.val ? nd.left : nd.right;
  }
  return { path, found: false, attach: last >= 0 ? { parent: last, side } : null };
}

// --------------------------------------------------- tree DP, made visible

export const TREE_NOTES = ["none", "depth", "height", "size", "sum", "gain", "rob", "camera"] as const;
export type TreeNote = (typeof TREE_NOTES)[number];

export const TREE_NOTE_NAMES: Record<TreeNote, string> = {
  none: "values only",
  depth: "depth (top-down)",
  height: "height (bottom-up)",
  size: "subtree size",
  sum: "subtree sum",
  gain: "best downward path (max path sum's return value)",
  rob: "house robber: take / skip",
  camera: "cameras: state bottom-up",
};

/** The per-node quantity a tree DP computes, as a short label per node id. */
export function annotateTree(t: ParsedTree, note: TreeNote): string[] {
  const n = t.nodes.length;
  const out = new Array<string>(n).fill("");
  if (note === "none" || n === 0) return out;
  const post = treeOrders(t).post;
  const val = (x: number) => t.nodes[x].val;
  const L = (x: number) => t.nodes[x].left, Rt = (x: number) => t.nodes[x].right;
  if (note === "depth" || note === "height" || note === "size") {
    const m = measure(t);
    const arr = note === "depth" ? m.depth : note === "height" ? m.height : m.size;
    return arr.map(String);
  }
  if (note === "sum") {
    const s = new Array(n).fill(0);
    for (const x of post) s[x] = val(x) + (L(x) >= 0 ? s[L(x)] : 0) + (Rt(x) >= 0 ? s[Rt(x)] : 0);
    return s.map(String);
  }
  if (note === "gain") {
    const g = new Array(n).fill(0);
    for (const x of post) {
      const l = L(x) >= 0 ? Math.max(0, g[L(x)]) : 0, r = Rt(x) >= 0 ? Math.max(0, g[Rt(x)]) : 0;
      g[x] = val(x) + Math.max(l, r);
    }
    return g.map(String);
  }
  if (note === "rob") {
    const take = new Array(n).fill(0), skip = new Array(n).fill(0);
    for (const x of post) {
      const kids = [L(x), Rt(x)].filter((c) => c >= 0);
      take[x] = val(x) + kids.reduce((a, c) => a + skip[c], 0);
      skip[x] = kids.reduce((a, c) => a + Math.max(take[c], skip[c]), 0);
    }
    return take.map((tk, i) => `${tk}/${skip[i]}`);
  }
  // camera: 0 unwatched, 1 guard, 2 watched
  const st = new Array(n).fill(2);
  for (const x of post) {
    const l = L(x) >= 0 ? st[L(x)] : 2, r = Rt(x) >= 0 ? st[Rt(x)] : 2;
    st[x] = l === 0 || r === 0 ? 1 : l === 1 || r === 1 ? 2 : 0;
  }
  if (st[t.root] === 0) st[t.root] = 1; // the root takes its own guard
  return st.map((s) => (s === 1 ? "cam" : s === 2 ? "ok" : "—"));
}

// ----------------------------------------------------- editing a BST by hand

interface MNode {
  val: number;
  left: MNode | null;
  right: MNode | null;
}

function toNodes(t: ParsedTree): MNode | null {
  const mk = (x: number): MNode | null =>
    x < 0 ? null : { val: t.nodes[x].val, left: mk(t.nodes[x].left), right: mk(t.nodes[x].right) };
  return mk(t.root);
}

function toLine(root: MNode | null): string {
  if (!root) return "null";
  const out: string[] = [];
  const q: (MNode | null)[] = [root];
  for (let i = 0; i < q.length; i++) {
    const nd = q[i];
    if (!nd) {
      out.push("null");
      continue;
    }
    out.push(String(nd.val));
    q.push(nd.left, nd.right);
  }
  while (out.length && out[out.length - 1] === "null") out.pop();
  return out.join(" ");
}

/** The level-order line of `t` with `v` inserted by BST descent (equal goes right). */
export function bstInsertLine(t: ParsedTree, v: number): string {
  const root = toNodes(t);
  const fresh: MNode = { val: v, left: null, right: null };
  if (!root) return toLine(fresh);
  let x = root;
  for (;;) {
    if (v < x.val) {
      if (!x.left) { x.left = fresh; break; }
      x = x.left;
    } else {
      if (!x.right) { x.right = fresh; break; }
      x = x.right;
    }
  }
  return toLine(root);
}

/** The level-order line of `t` with `v` deleted (two children: the in-order
 * successor's value moves up), or the same line when `v` is absent. */
export function bstDeleteLine(t: ParsedTree, v: number): string {
  const del = (n: MNode | null, key: number): MNode | null => {
    if (!n) return null;
    if (key < n.val) n.left = del(n.left, key);
    else if (key > n.val) n.right = del(n.right, key);
    else {
      if (!n.left) return n.right;
      if (!n.right) return n.left;
      let s = n.right;
      while (s.left) s = s.left;
      n.val = s.val;
      n.right = del(n.right, s.val);
    }
    return n;
  };
  return toLine(del(toNodes(t), v));
}

/** Rotate at node `id` (by position, not value): "left" lifts its right child,
 * "right" lifts its left child. The in-order sequence is unchanged. Returns
 * null when the rotation is impossible (no such child). */
export function rotateLine(t: ParsedTree, id: number, dir: "left" | "right"): string | null {
  // map ids to the rebuilt nodes so the rotation hits the clicked node
  const byId = new Map<number, MNode>();
  const mk = (x: number): MNode | null => {
    if (x < 0) return null;
    const nd: MNode = { val: t.nodes[x].val, left: mk(t.nodes[x].left), right: mk(t.nodes[x].right) };
    byId.set(x, nd);
    return nd;
  };
  let root = mk(t.root);
  const x = byId.get(id);
  if (!x) return null;
  const y = dir === "left" ? x.right : x.left;
  if (!y) return null;
  if (dir === "left") {
    x.right = y.left;
    y.left = x;
  } else {
    x.left = y.right;
    y.right = x;
  }
  const p = t.nodes[id].parent;
  if (p < 0) root = y;
  else {
    const pn = byId.get(p)!;
    if (pn.left === x) pn.left = y;
    else pn.right = y;
  }
  return toLine(root);
}

/** x = in-order position, y = depth: a layout where no two nodes overlap and
 * a BST's values read left to right in sorted order. */
export function layoutTree(t: ParsedTree): { x: number; y: number }[] {
  const pos: { x: number; y: number }[] = t.nodes.map(() => ({ x: 0, y: 0 }));
  const { depth } = measure(t);
  treeOrders(t).in.forEach((id, i) => {
    pos[id] = { x: i, y: depth[id] };
  });
  return pos;
}

// ------------------------------------------------------------------ graphs

export interface Edge {
  u: number;
  v: number;
  w: number;
}

/** Parse "u v" or "u v w" per line (or per comma). Weight defaults to 1. */
export function parseEdges(text: string, n: number): { edges: Edge[]; error: string | null } {
  const edges: Edge[] = [];
  const parts = text.split(/[\n,;]+/).map((s) => s.trim()).filter(Boolean);
  for (const p of parts) {
    const t = p.split(/\s+/);
    if (t.length < 2 || t.length > 3 || t.some((x) => !/^-?\d+$/.test(x))) {
      return { edges, error: `cannot read "${p}" — write "u v" or "u v w"` };
    }
    const [u, v] = [Number(t[0]), Number(t[1])];
    if (u < 0 || v < 0 || u >= n || v >= n) return { edges, error: `"${p}": vertices run from 0 to ${n - 1}` };
    edges.push({ u, v, w: t.length === 3 ? Number(t[2]) : 1 });
  }
  return { edges, error: null };
}

export interface GraphStep {
  /** One line saying what happened. */
  note: string;
  /** Vertices to highlight (the current one first). */
  focus: number[];
  /** Vertices finished / settled / in the tree so far. */
  done: number[];
  /** Edge indices chosen so far (a BFS tree, an MST, a shortest-path tree). */
  chosen: number[];
  /** The algorithm's state, as labelled lines. */
  state: [string, string][];
}

export const GRAPH_ALGOS = [
  "bfs", "dfs", "bipartite", "kahn", "dsu", "kruskal", "prim", "dijkstra", "zeroone", "bellman", "floyd",
] as const;
export type GraphAlgo = (typeof GRAPH_ALGOS)[number];

export const GRAPH_ALGO_NAMES: Record<GraphAlgo, string> = {
  bfs: "BFS",
  dfs: "DFS (colours, edge types)",
  bipartite: "Two-colouring (bipartite?)",
  kahn: "Kahn's topological sort",
  dsu: "Union-find",
  kruskal: "Kruskal's MST",
  prim: "Prim's MST",
  dijkstra: "Dijkstra",
  zeroone: "0-1 BFS (weights 0 / 1)",
  bellman: "Bellman-Ford",
  floyd: "Floyd–Warshall",
};

type Adj = { to: number; w: number; e: number }[][];

function adjacency(n: number, edges: Edge[], directed: boolean): Adj {
  const adj: Adj = Array.from({ length: n }, () => []);
  edges.forEach(({ u, v, w }, e) => {
    adj[u].push({ to: v, w, e });
    if (!directed) adj[v].push({ to: u, w, e });
  });
  return adj;
}

const fmt = (x: number) => (x === Infinity ? "∞" : String(x));
const list = (xs: (number | string)[]) => (xs.length ? xs.join(" ") : "—");

export function runGraph(
  algo: GraphAlgo,
  n: number,
  edges: Edge[],
  directed: boolean,
  source: number,
): { steps: GraphStep[]; result: string } {
  switch (algo) {
    case "bfs":
      return bfsSteps(n, edges, directed, source);
    case "dfs":
      return dfsSteps(n, edges, directed, source);
    case "kahn":
      return kahnSteps(n, edges);
    case "dsu":
      return dsuSteps(n, edges);
    case "kruskal":
      return kruskalSteps(n, edges);
    case "prim":
      return primSteps(n, edges, source);
    case "dijkstra":
      return dijkstraSteps(n, edges, directed, source);
    case "bellman":
      return bellmanSteps(n, edges, directed, source);
    case "bipartite":
      return bipartiteSteps(n, edges, source);
    case "zeroone":
      return zeroOneSteps(n, edges, directed, source);
    case "floyd":
      return floydSteps(n, edges, directed);
  }
}

function bipartiteSteps(n: number, edges: Edge[], s: number) {
  const adj = adjacency(n, edges, false);
  const colour = new Array(n).fill(-1);
  const steps: GraphStep[] = [];
  const chosen: number[] = [];
  const done: number[] = [];
  const snap = (note: string, focus: number[], queue: number[]) =>
    steps.push({
      note,
      focus,
      done: [...done],
      chosen: [...chosen],
      state: [
        ["queue", list(queue)],
        ["colour", colour.map((c) => (c < 0 ? "·" : c === 0 ? "A" : "B")).join(" ")],
      ],
    });
  const order = [s, ...[...Array(n).keys()].filter((v) => v !== s)];
  for (const start of order) {
    if (colour[start] >= 0) continue;
    colour[start] = 0;
    const q = [start];
    snap(`colour ${start} A and start a BFS`, [start], q);
    for (let h = 0; h < q.length; h++) {
      const u = q[h];
      for (const { to, e } of adj[u]) {
        if (colour[to] < 0) {
          colour[to] = 1 - colour[u];
          q.push(to);
          chosen.push(e);
        } else if (colour[to] === colour[u]) {
          snap(`${u}–${to}: both ${colour[u] === 0 ? "A" : "B"} — an odd cycle, not bipartite`, [u, to], q.slice(h + 1));
          return { steps, result: `not bipartite: edge ${u}–${to} joins two vertices of one colour` };
        }
      }
      done.push(u);
      snap(`pop ${u}: its neighbours get the other colour`, [u], q.slice(h + 1));
    }
  }
  const a = colour.map((c, i) => (c === 0 ? i : -1)).filter((i) => i >= 0);
  const b = colour.map((c, i) => (c === 1 ? i : -1)).filter((i) => i >= 0);
  return { steps, result: `bipartite: A = {${a.join(", ")}}, B = {${b.join(", ")}}` };
}

function zeroOneSteps(n: number, edges: Edge[], directed: boolean, s: number) {
  const bad = edges.find((e) => e.w !== 0 && e.w !== 1);
  if (bad) {
    return {
      steps: [{ note: `0-1 BFS needs every weight to be 0 or 1 (edge ${bad.u}–${bad.v} has ${bad.w})`, focus: [bad.u, bad.v], done: [], chosen: [], state: [] as [string, string][] }],
      result: "not a 0-1 graph — use Dijkstra",
    };
  }
  const adj = adjacency(n, edges, directed);
  const dist = new Array(n).fill(Infinity), via = new Array(n).fill(-1);
  dist[s] = 0;
  const dq: number[] = [s];
  const steps: GraphStep[] = [];
  const done: number[] = [];
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [...done],
      chosen: via.filter((e) => e >= 0),
      state: [
        ["deque (front → back)", list(dq)],
        ["dist", dist.map(fmt).join(" ")],
      ],
    });
  snap(`start: dist[${s}] = 0`, [s]);
  const settled = new Array(n).fill(false);
  while (dq.length) {
    const u = dq.shift()!;
    if (settled[u]) continue;
    settled[u] = true;
    done.push(u);
    const moves: string[] = [];
    for (const { to, w, e } of adj[u]) {
      if (dist[u] + w < dist[to]) {
        dist[to] = dist[u] + w;
        via[to] = e;
        if (w === 0) dq.unshift(to);
        else dq.push(to);
        moves.push(`${to}←${dist[to]} (${w === 0 ? "front" : "back"})`);
      }
    }
    snap(`pop ${u} (dist ${dist[u]})${moves.length ? `: ${moves.join(", ")}` : ""}`, [u]);
    if (steps.length > 400) break;
  }
  return { steps, result: `dist = ${dist.map(fmt).join(" ")}` };
}

function floydSteps(n: number, edges: Edge[], directed: boolean) {
  const d: number[][] = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : Infinity)));
  for (const { u, v, w } of edges) {
    d[u][v] = Math.min(d[u][v], w);
    if (!directed) d[v][u] = Math.min(d[v][u], w);
  }
  const steps: GraphStep[] = [];
  const snap = (note: string, focus: number[], changed: number) =>
    steps.push({
      note,
      focus,
      done: [],
      chosen: [],
      state: [
        ...d.map((row, i) => [`row ${i}`, row.map(fmt).join(" ")] as [string, string]),
        ["improved this round", String(changed)],
      ],
    });
  snap("direct edges only (k = none)", [], 0);
  for (let k = 0; k < n; k++) {
    let changed = 0;
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++)
        if (d[i][k] + d[k][j] < d[i][j]) {
          d[i][j] = d[i][k] + d[k][j];
          changed++;
        }
    snap(`allow vertex ${k} as a stop in the middle`, [k], changed);
  }
  const neg = d.some((row, i) => row[i] < 0);
  return { steps, result: neg ? "some d[i][i] < 0: a negative cycle" : "all-pairs distances in the table above" };
}

function bfsSteps(n: number, edges: Edge[], directed: boolean, s: number) {
  const adj = adjacency(n, edges, directed);
  const dist = new Array(n).fill(-1);
  const chosen: number[] = [];
  const done: number[] = [];
  const steps: GraphStep[] = [];
  const q = [s];
  dist[s] = 0;
  const snap = (note: string, focus: number[], queue: number[]) =>
    steps.push({
      note,
      focus,
      done: [...done],
      chosen: [...chosen],
      state: [
        ["queue", list(queue)],
        ["dist", dist.map((d) => (d < 0 ? "·" : String(d))).join(" ")],
      ],
    });
  snap(`start: dist[${s}] = 0, queue = [${s}]`, [s], q);
  for (let h = 0; h < q.length; h++) {
    const u = q[h];
    const found: number[] = [];
    for (const { to, e } of adj[u]) {
      if (dist[to] < 0) {
        dist[to] = dist[u] + 1;
        q.push(to);
        chosen.push(e);
        found.push(to);
      }
    }
    done.push(u);
    snap(
      found.length
        ? `pop ${u} (dist ${dist[u]}): discover ${found.join(", ")} at dist ${dist[u] + 1}`
        : `pop ${u} (dist ${dist[u]}): no new neighbours`,
      [u, ...found],
      q.slice(h + 1),
    );
  }
  const unreached = dist.map((d, i) => (d < 0 ? i : -1)).filter((i) => i >= 0);
  return {
    steps,
    result: `dist = ${dist.map((d) => (d < 0 ? "−1" : String(d))).join(" ")}` +
      (unreached.length ? ` (unreachable: ${unreached.join(", ")})` : ""),
  };
}

function dfsSteps(n: number, edges: Edge[], directed: boolean, s: number) {
  const adj = adjacency(n, edges, directed);
  const colour = new Array(n).fill(0); // 0 white, 1 grey, 2 black
  const tin = new Array(n).fill(0), tout = new Array(n).fill(0);
  const steps: GraphStep[] = [];
  const chosen: number[] = [];
  const done: number[] = [];
  const stack: number[] = [];
  let clock = 0;
  let cycle = false;
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [...done],
      chosen: [...chosen],
      state: [
        ["stack", list(stack)],
        ["colour", colour.map((c) => "wgb"[c]).join(" ")],
        ["in / out", tin.map((t, i) => `${i}:${t || "·"}/${tout[i] || "·"}`).join("  ")],
      ],
    });
  const visit = (u: number, parentEdge: number) => {
    colour[u] = 1;
    tin[u] = ++clock;
    stack.push(u);
    snap(`enter ${u} at time ${clock}`, [u]);
    for (const { to, e } of adj[u]) {
      if (!directed && e === parentEdge) continue;
      if (colour[to] === 0) {
        chosen.push(e);
        snap(`${u}→${to}: white, a tree edge`, [u, to]);
        visit(to, e);
      } else if (colour[to] === 1) {
        cycle = true;
        snap(`${u}→${to}: grey — a back edge, so a cycle`, [u, to]);
      } else if (directed) {
        snap(`${u}→${to}: black — ${tin[u] < tin[to] ? "a forward" : "a cross"} edge, harmless`, [u, to]);
      }
    }
    colour[u] = 2;
    tout[u] = ++clock;
    stack.pop();
    done.push(u);
    snap(`leave ${u} at time ${clock}`, [u]);
  };
  const order = [s, ...Array.from({ length: n }, (_, i) => i).filter((i) => i !== s)];
  for (const v of order) if (colour[v] === 0) visit(v, -1);
  const finish = [...Array(n).keys()].sort((a, b) => tout[b] - tout[a]);
  return {
    steps,
    result: cycle
      ? "a back edge was found: the graph has a cycle"
      : directed
      ? `no cycle; reverse finish order ${finish.join(" ")} is a topological order`
      : "no cycle: every component is a tree",
  };
}

function kahnSteps(n: number, edges: Edge[]) {
  const adj = adjacency(n, edges, true);
  const indeg = new Array(n).fill(0);
  for (const { v } of edges) indeg[v]++;
  const q: number[] = [];
  for (let v = 0; v < n; v++) if (indeg[v] === 0) q.push(v);
  const out: number[] = [];
  const steps: GraphStep[] = [];
  const chosen: number[] = [];
  const snap = (note: string, focus: number[], head: number) =>
    steps.push({
      note,
      focus,
      done: [...out],
      chosen: [...chosen],
      state: [
        ["queue", list(q.slice(head))],
        ["in-degree", indeg.join(" ")],
        ["order", list(out)],
      ],
    });
  snap(`in-degree 0 at the start: ${list(q)}`, [...q], 0);
  for (let h = 0; h < q.length; h++) {
    const u = q[h];
    out.push(u);
    const freed: number[] = [];
    for (const { to, e } of adj[u]) {
      chosen.push(e);
      if (--indeg[to] === 0) {
        q.push(to);
        freed.push(to);
      }
    }
    snap(`take ${u}${freed.length ? `; now free: ${freed.join(", ")}` : ""}${q.length - h - 1 > 1 ? " (queue wider than one: the order is not unique)" : ""}`, [u, ...freed], h + 1);
  }
  return {
    steps,
    result:
      out.length === n
        ? `topological order: ${out.join(" ")}`
        : `only ${out.length} of ${n} came out — the rest lie on or behind a cycle`,
  };
}

function dsuSteps(n: number, edges: Edge[]) {
  const parent = [...Array(n).keys()], size = new Array(n).fill(1);
  const find = (x: number): number => {
    let r = x;
    while (parent[r] !== r) r = parent[r];
    while (parent[x] !== r) {
      const nx = parent[x];
      parent[x] = r;
      x = nx;
    }
    return r;
  };
  let comps = n;
  const steps: GraphStep[] = [];
  const chosen: number[] = [];
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [],
      chosen: [...chosen],
      state: [
        ["parent", parent.join(" ")],
        ["size", size.join(" ")],
        ["components", String(comps)],
      ],
    });
  snap("every vertex is its own set", []);
  edges.forEach(({ u, v }, e) => {
    const ru = find(u), rv = find(v);
    if (ru === rv) {
      snap(`union(${u}, ${v}): same root ${ru} — false (this edge closes a cycle)`, [u, v]);
      return;
    }
    const [big, small] = size[ru] >= size[rv] ? [ru, rv] : [rv, ru];
    parent[small] = big;
    size[big] += size[small];
    comps--;
    chosen.push(e);
    snap(`union(${u}, ${v}): root ${small} goes under ${big} (by size) — true`, [u, v]);
  });
  return { steps, result: `${comps} component(s)` };
}

function kruskalSteps(n: number, edges: Edge[]) {
  const parent = [...Array(n).keys()];
  const find = (x: number): number => (parent[x] === x ? x : (parent[x] = find(parent[x])));
  const order = edges.map((_, i) => i).sort((a, b) => edges[a].w - edges[b].w || a - b);
  let total = 0, taken = 0;
  const steps: GraphStep[] = [];
  const chosen: number[] = [];
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [],
      chosen: [...chosen],
      state: [
        ["sorted edges", order.map((i) => `${edges[i].u}-${edges[i].v}(${edges[i].w})`).join(" ")],
        ["total", String(total)],
        ["edges taken", `${taken} of ${Math.max(0, n - 1)}`],
      ],
    });
  snap("sort the edges by weight", []);
  for (const i of order) {
    const { u, v, w } = edges[i];
    const ru = find(u), rv = find(v);
    if (ru === rv) {
      snap(`${u}-${v} (${w}): both ends already connected — skip, it would close a cycle`, [u, v]);
    } else {
      parent[ru] = rv;
      total += w;
      taken++;
      chosen.push(i);
      snap(`${u}-${v} (${w}): joins two groups — take it`, [u, v]);
    }
  }
  return {
    steps,
    result: taken === n - 1 || n <= 1 ? `MST weight ${total}` : `not connected: only ${taken} of ${n - 1} edges`,
  };
}

function primSteps(n: number, edges: Edge[], s: number) {
  const adj = adjacency(n, edges, false);
  const inTree = new Array(n).fill(false);
  const best = new Array(n).fill(Infinity), via = new Array(n).fill(-1);
  best[s] = 0;
  let total = 0;
  const steps: GraphStep[] = [];
  const chosen: number[] = [];
  const done: number[] = [];
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [...done],
      chosen: [...chosen],
      state: [
        ["cheapest link", best.map(fmt).join(" ")],
        ["total", String(total)],
      ],
    });
  snap(`start the tree at ${s}`, [s]);
  for (let round = 0; round < n; round++) {
    let u = -1;
    for (let v = 0; v < n; v++) if (!inTree[v] && (u < 0 || best[v] < best[u])) u = v;
    if (u < 0 || best[u] === Infinity) break;
    inTree[u] = true;
    done.push(u);
    total += best[u];
    if (via[u] >= 0) chosen.push(via[u]);
    const upd: string[] = [];
    for (const { to, w, e } of adj[u]) {
      if (!inTree[to] && w < best[to]) {
        best[to] = w;
        via[to] = e;
        upd.push(`${to}←${w}`);
      }
    }
    snap(`add ${u}${round ? ` (link cost ${best[u]})` : ""}${upd.length ? `; cheaper links: ${upd.join(", ")}` : ""}`, [u]);
  }
  return {
    steps,
    result: done.length === n ? `MST weight ${total}` : `not connected: the tree reached ${done.length} of ${n}`,
  };
}

function dijkstraSteps(n: number, edges: Edge[], directed: boolean, s: number) {
  const adj = adjacency(n, edges, directed);
  const neg = edges.some((e) => e.w < 0);
  const dist = new Array(n).fill(Infinity), via = new Array(n).fill(-1);
  const settled = new Array(n).fill(false);
  dist[s] = 0;
  let heap: [number, number][] = [[0, s]];
  const steps: GraphStep[] = [];
  const done: number[] = [];
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [...done],
      chosen: via.filter((e) => e >= 0),
      state: [
        ["heap", heap.length ? [...heap].sort((a, b) => a[0] - b[0]).map(([d, v]) => `(${d}, ${v})`).join(" ") : "—"],
        ["dist", dist.map(fmt).join(" ")],
      ],
    });
  snap(`start: dist[${s}] = 0${neg ? " — warning: a negative edge breaks Dijkstra's guarantee" : ""}`, [s]);
  while (heap.length) {
    heap.sort((a, b) => a[0] - b[0]);
    const [d, u] = heap.shift()!;
    if (d > dist[u] || settled[u]) {
      snap(`pop (${d}, ${u}): stale — ${u} already has ${fmt(dist[u])}`, [u]);
      continue;
    }
    settled[u] = true;
    done.push(u);
    const upd: string[] = [];
    for (const { to, w, e } of adj[u]) {
      if (d + w < dist[to]) {
        dist[to] = d + w;
        via[to] = e;
        heap.push([dist[to], to]);
        upd.push(`${to}←${dist[to]}`);
      }
    }
    snap(`pop (${d}, ${u}): final${upd.length ? `; relax ${upd.join(", ")}` : ""}`, [u]);
    if (steps.length > 400) break;
  }
  heap = [];
  return { steps, result: `dist = ${dist.map((x) => (x === Infinity ? "∞" : String(x))).join(" ")}` };
}

function bellmanSteps(n: number, edges: Edge[], directed: boolean, s: number) {
  const list2: Edge[] = directed ? edges : edges.flatMap((e) => [e, { u: e.v, v: e.u, w: e.w }]);
  const idx = directed ? edges.map((_, i) => i) : edges.flatMap((_, i) => [i, i]);
  const dist = new Array(n).fill(Infinity), via = new Array(n).fill(-1);
  dist[s] = 0;
  const steps: GraphStep[] = [];
  const snap = (note: string, focus: number[]) =>
    steps.push({
      note,
      focus,
      done: [],
      chosen: via.filter((e) => e >= 0),
      state: [["dist", dist.map(fmt).join(" ")]],
    });
  snap(`start: dist[${s}] = 0; relax every edge, up to ${n} rounds`, [s]);
  let negCycle = false;
  for (let round = 1; round <= n; round++) {
    const changed: string[] = [];
    const focus: number[] = [];
    list2.forEach(({ u, v, w }, i) => {
      if (dist[u] !== Infinity && dist[u] + w < dist[v]) {
        dist[v] = dist[u] + w;
        via[v] = idx[i];
        changed.push(`${v}←${dist[v]}`);
        focus.push(v);
      }
    });
    if (!changed.length) {
      snap(`round ${round}: nothing changed — done`, []);
      break;
    }
    if (round === n) {
      negCycle = true;
      snap(`round ${round}: still improving (${changed.join(", ")}) — a negative cycle is reachable`, focus);
    } else snap(`round ${round}: ${changed.join(", ")}`, focus);
  }
  return {
    steps,
    result: negCycle ? "negative cycle reachable from the source" : `dist = ${dist.map(fmt).join(" ")}`,
  };
}

/** Vertices on a circle, for drawing. */
export function circleLayout(n: number, r = 1): { x: number; y: number }[] {
  return Array.from({ length: n }, (_, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / Math.max(1, n);
    return { x: r * Math.cos(a), y: r * Math.sin(a) };
  });
}

// ------------------------------------------------------------------ search

export const SEARCH_MODES = ["subsets", "combinations", "permutations", "subsetsum", "combsum"] as const;
export type SearchMode = (typeof SEARCH_MODES)[number];

export const SEARCH_MODE_NAMES: Record<SearchMode, string> = {
  subsets: "All subsets",
  combinations: "k-combinations",
  permutations: "Permutations",
  subsetsum: "Subsets summing to target",
  combsum: "Combination sum (reuse allowed)",
};

export interface SearchEvent {
  depth: number;
  kind: "choose" | "undo" | "emit" | "prune";
  text: string;
}

export interface SearchRun {
  events: SearchEvent[];
  answers: string[];
  calls: number;
  /** True when the event log was cut short. */
  truncated: boolean;
}

const MAX_EVENTS = 600;
const MAX_CALLS = 200_000;

/** Run one backtracking search, logging choose / undo / emit / prune events.
 * `prune` switches on the unit's pruning rules (sorted break on sums, the size
 * cap on combinations); with it off the same answers come out, more slowly. */
export function runSearch(itemsIn: number[], k: number, target: number, mode: SearchMode, prune: boolean): SearchRun {
  const items = mode === "subsetsum" || mode === "combsum" ? [...itemsIn].sort((a, b) => a - b) : itemsIn;
  const n = items.length;
  const events: SearchEvent[] = [];
  const answers: string[] = [];
  const path: number[] = [];
  const used = new Array(n).fill(false);
  let calls = 0;
  let truncated = false;
  const log = (depth: number, kind: SearchEvent["kind"], text: string) => {
    if (events.length < MAX_EVENTS) events.push({ depth, kind, text });
    else truncated = true;
  };
  const emit = (depth: number) => {
    const s = path.length ? path.join(" ") : "∅";
    answers.push(s);
    log(depth, "emit", `emit {${s}}`);
  };

  const rec = (start: number, rem: number, depth: number): void => {
    calls++;
    if (calls > MAX_CALLS) {
      truncated = true;
      return;
    }
    switch (mode) {
      case "subsets":
        emit(depth);
        break;
      case "combinations":
        if (path.length === k) {
          emit(depth);
          return;
        }
        if (prune && n - start < k - path.length) {
          log(depth, "prune", `only ${n - start} items left, need ${k - path.length}: stop`);
          return;
        }
        break;
      case "permutations":
        if (path.length === n) {
          emit(depth);
          return;
        }
        break;
      case "subsetsum":
      case "combsum":
        if (rem === 0 && path.length > 0) {
          emit(depth);
          return;
        }
        if (!prune && rem < 0) return;
        break;
    }
    const from = mode === "permutations" ? 0 : start;
    for (let i = from; i < n; i++) {
      if (mode === "permutations" && used[i]) continue;
      if ((mode === "subsetsum" || mode === "combsum") && prune && items[i] > rem) {
        log(depth, "prune", `${items[i]} > ${rem} remaining: break — later items are larger`);
        break;
      }
      path.push(items[i]);
      if (mode === "permutations") used[i] = true;
      log(depth, "choose", `choose ${items[i]} → [${path.join(" ")}]`);
      const next = mode === "combsum" ? i : i + 1;
      rec(next, rem - items[i], depth + 1);
      path.pop();
      if (mode === "permutations") used[i] = false;
      log(depth, "undo", `undo ${items[i]} → [${path.join(" ")}]`);
      if (truncated && calls > MAX_CALLS) return;
    }
  };
  // The sum modes only terminate (and only prune correctly) on positive items.
  if ((mode === "combsum" || mode === "subsetsum") && items.some((x) => x <= 0)) {
    return { events: [{ depth: 0, kind: "prune", text: "items must be positive for sum modes" }], answers: [], calls: 0, truncated: false };
  }
  rec(0, target, 0);
  return { events, answers, calls, truncated };
}

// ------------------------------------------------------------------ mazes

export const MAZE_WALKS = ["bfs", "multi", "flood"] as const;
export type MazeWalk = (typeof MAZE_WALKS)[number];

export const MAZE_WALK_NAMES: Record<MazeWalk, string> = {
  bfs: "BFS from S to T",
  multi: "Multi-source BFS from every S",
  flood: "Flood fill: count the regions",
};

export interface MazeRun {
  rows: string[];
  /** Distance (bfs / multi) or region number (flood) per cell; -1 = unreached / wall. */
  value: number[][];
  /** Cells of the shortest S → T path (bfs only). */
  path: [number, number][];
  /** The BFS layer (or the region) at which each cell was reached, for stepping. */
  layer: number[][];
  layers: number;
  result: string;
}

/** Parse a maze: rows of `.`, `#`, `S`, `T` (other characters count as open). */
export function parseMaze(text: string, maxSide = 20): string[] | null {
  const rows = text.split(/\r?\n/).map((r) => r.trim()).filter(Boolean);
  if (!rows.length || rows.length > maxSide) return null;
  const c = rows[0].length;
  if (!c || c > maxSide || rows.some((r) => r.length !== c)) return null;
  return rows;
}

export function runMaze(rows: string[], walk: MazeWalk): MazeRun {
  const R = rows.length, C = rows[0].length;
  const value = rows.map((r) => Array.from(r, () => -1));
  const layer = rows.map((r) => Array.from(r, () => -1));
  const open = (i: number, j: number) => i >= 0 && j >= 0 && i < R && j < C && rows[i][j] !== "#";
  const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  if (walk === "flood") {
    let regions = 0;
    for (let i = 0; i < R; i++)
      for (let j = 0; j < C; j++) {
        if (!open(i, j) || value[i][j] >= 0) continue;
        const st: [number, number][] = [[i, j]];
        value[i][j] = regions;
        layer[i][j] = regions;
        while (st.length) {
          const [x, y] = st.pop()!;
          for (const [dx, dy] of DIRS) {
            const nx = x + dx, ny = y + dy;
            if (open(nx, ny) && value[nx][ny] < 0) {
              value[nx][ny] = regions;
              layer[nx][ny] = regions;
              st.push([nx, ny]);
            }
          }
        }
        regions++;
      }
    return { rows, value, path: [], layer, layers: regions, result: `${regions} open region(s)` };
  }
  const sources: [number, number][] = [];
  let target: [number, number] | null = null;
  for (let i = 0; i < R; i++)
    for (let j = 0; j < C; j++) {
      if (rows[i][j] === "S") sources.push([i, j]);
      if (rows[i][j] === "T") target = [i, j];
    }
  const starts = walk === "bfs" ? sources.slice(0, 1) : sources;
  if (!starts.length) return { rows, value, path: [], layer, layers: 0, result: "put an S in the maze" };
  const parent = rows.map((r) => Array.from(r, () => [-1, -1] as [number, number]));
  const q: [number, number][] = [];
  for (const [i, j] of starts) {
    value[i][j] = 0;
    layer[i][j] = 0;
    q.push([i, j]);
  }
  let maxd = 0;
  for (let h = 0; h < q.length; h++) {
    const [x, y] = q[h];
    for (const [dx, dy] of DIRS) {
      const nx = x + dx, ny = y + dy;
      if (open(nx, ny) && value[nx][ny] < 0) {
        value[nx][ny] = value[x][y] + 1;
        layer[nx][ny] = value[nx][ny];
        maxd = Math.max(maxd, value[nx][ny]);
        parent[nx][ny] = [x, y];
        q.push([nx, ny]);
      }
    }
  }
  const path: [number, number][] = [];
  let result: string;
  if (walk === "bfs") {
    if (!target) result = "no T: distances from S shown";
    else if (value[target[0]][target[1]] < 0) result = "T cannot be reached";
    else {
      for (let cur: [number, number] = target; cur[0] >= 0; cur = parent[cur[0]][cur[1]]) path.unshift(cur);
      result = `shortest path: ${value[target[0]][target[1]]} steps`;
    }
  } else {
    let far = 0;
    for (const row of value) for (const d of row) far = Math.max(far, d);
    result = `every open cell's distance to its nearest S; the farthest is ${far}`;
  }
  return { rows, value, path, layer, layers: maxd + 1, result };
}
