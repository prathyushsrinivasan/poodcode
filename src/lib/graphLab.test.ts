import { describe, expect, it } from "vitest";
import {
  annotateTree,
  bstDeleteLine,
  bstInsertLine,
  parseMaze,
  rotateLine,
  runMaze,
  bstDescent,
  circleLayout,
  layoutTree,
  nodeInfo,
  parseEdges,
  parseTree,
  runGraph,
  runSearch,
  treeOrders,
  treeStats,
} from "./graphLab";

const vals = (t: ReturnType<typeof parseTree>, ids: number[]) => ids.map((i) => t!.nodes[i].val);

describe("parseTree", () => {
  it("reads level order with nulls", () => {
    const t = parseTree("4 2 6 1 3 null 7")!;
    expect(t.nodes.length).toBe(6);
    expect(t.nodes[t.nodes[0].left].val).toBe(2);
    expect(t.nodes[t.nodes[2].right].val).toBe(7);
    expect(t.nodes[t.nodes[2].right].parent).toBe(2);
  });
  it("handles the empty tree and bad tokens", () => {
    expect(parseTree("")).toEqual({ nodes: [], root: -1 });
    expect(parseTree("null")).toEqual({ nodes: [], root: -1 });
    expect(parseTree("1 x 3")).toBeNull();
  });
  it("caps the node count", () => {
    expect(parseTree(Array.from({ length: 70 }, (_, i) => i).join(" "), 63)).toBeNull();
  });
});

describe("tree orders and stats", () => {
  const t = parseTree("4 2 6 1 3 5 7")!;
  it("gives the four orders", () => {
    const o = treeOrders(t);
    expect(vals(t, o.pre)).toEqual([4, 2, 1, 3, 6, 5, 7]);
    expect(vals(t, o.in)).toEqual([1, 2, 3, 4, 5, 6, 7]);
    expect(vals(t, o.post)).toEqual([1, 3, 2, 5, 7, 6, 4]);
    expect(vals(t, o.level)).toEqual([4, 2, 6, 1, 3, 5, 7]);
  });
  it("measures a perfect BST", () => {
    expect(treeStats(t)).toEqual({ size: 7, height: 3, leaves: 4, diameter: 4, balanced: true, bstBreaker: -1 });
  });
  it("finds the node that breaks the BST range, not just a child comparison", () => {
    // 4 sits in 5's right subtree: every parent-child pair is fine, the tree is not a BST
    const bad = parseTree("5 3 8 null null 4 9")!;
    const s = treeStats(bad);
    expect(bad.nodes[s.bstBreaker].val).toBe(4);
    const info = nodeInfo(bad, s.bstBreaker);
    expect(info.lo).toBe(5);
    expect(info.hi).toBe(8);
    expect(info.inRange).toBe(false);
  });
  it("detects an unbalanced chain", () => {
    const chain = parseTree("1 null 2 null 3")!;
    const s = treeStats(chain);
    expect(s.balanced).toBe(false);
    expect(s.height).toBe(3);
    expect(s.diameter).toBe(2);
  });
  it("reports depth, height, size and the root path", () => {
    const leaf = t.nodes.findIndex((n) => n.val === 5);
    const info = nodeInfo(t, leaf);
    expect(info).toMatchObject({ depth: 2, height: 1, size: 1, lo: 4, hi: 6, inRange: true });
    expect(vals(t, info.path)).toEqual([4, 6, 5]);
  });
  it("lays nodes out by in-order position and depth", () => {
    const pos = layoutTree(t);
    expect(pos[0]).toEqual({ x: 3, y: 0 });
    expect(new Set(pos.map((p) => p.x)).size).toBe(7);
  });
});

describe("bstDescent", () => {
  const t = parseTree("50 30 70 20 40")!;
  it("finds a present key", () => {
    const d = bstDescent(t, 40);
    expect(d.found).toBe(true);
    expect(vals(t, d.path)).toEqual([50, 30, 40]);
  });
  it("says where a missing key would attach", () => {
    const d = bstDescent(t, 45);
    expect(d.found).toBe(false);
    expect(t.nodes[d.attach!.parent].val).toBe(40);
    expect(d.attach!.side).toBe("right");
  });
});

describe("parseEdges", () => {
  it("reads weighted and unweighted edges, by line or comma", () => {
    expect(parseEdges("0 1 5\n1 2", 3)).toEqual({
      edges: [
        { u: 0, v: 1, w: 5 },
        { u: 1, v: 2, w: 1 },
      ],
      error: null,
    });
    expect(parseEdges("0 1, 1 2 -3", 3).edges[1].w).toBe(-3);
  });
  it("rejects out-of-range vertices and junk", () => {
    expect(parseEdges("0 3", 3).error).toMatch(/0 to 2/);
    expect(parseEdges("0 x", 3).error).toMatch(/cannot read/);
  });
});

describe("runGraph", () => {
  const E = (s: string, n: number) => parseEdges(s, n).edges;

  it("BFS distances", () => {
    const r = runGraph("bfs", 6, E("0 1, 0 2, 1 3, 2 3, 3 4", 6), false, 0);
    expect(r.result).toBe("dist = 0 1 1 2 3 −1 (unreachable: 5)");
    expect(r.steps[r.steps.length - 1].chosen.length).toBe(4);
  });
  it("DFS finds a back edge in a directed cycle", () => {
    expect(runGraph("dfs", 3, E("0 1, 1 2, 2 0", 3), true, 0).result).toMatch(/cycle/);
    expect(runGraph("dfs", 3, E("0 1, 1 2, 0 2", 3), true, 0).result).toMatch(/no cycle/);
  });
  it("DFS on an undirected tree does not mistake the parent edge for a cycle", () => {
    expect(runGraph("dfs", 3, E("0 1, 1 2", 3), false, 0).result).toMatch(/no cycle/);
    expect(runGraph("dfs", 3, E("0 1, 1 2, 2 0", 3), false, 0).result).toMatch(/cycle/);
  });
  it("Kahn orders a DAG and reports a cycle", () => {
    expect(runGraph("kahn", 4, E("2 0, 0 3, 3 1, 2 3", 4), true, 0).result).toBe("topological order: 2 0 3 1");
    expect(runGraph("kahn", 3, E("0 1, 1 2, 2 1", 3), true, 0).result).toMatch(/only 1 of 3/);
  });
  it("union-find counts components", () => {
    expect(runGraph("dsu", 5, E("0 1, 1 2, 0 2, 3 4", 5), false, 0).result).toBe("2 component(s)");
  });
  it("Kruskal and Prim agree", () => {
    const g = E("0 1 4, 1 2 2, 2 3 7, 0 2 3, 1 3 9", 4);
    expect(runGraph("kruskal", 4, g, false, 0).result).toBe("MST weight 12");
    expect(runGraph("prim", 4, g, false, 0).result).toBe("MST weight 12");
    expect(runGraph("kruskal", 3, E("0 1 5", 3), false, 0).result).toMatch(/not connected/);
  });
  it("Dijkstra and Bellman-Ford agree on non-negative weights", () => {
    const g = E("0 1 4, 0 2 1, 2 1 2, 1 3 1, 2 3 5", 4);
    expect(runGraph("dijkstra", 4, g, true, 0).result).toBe("dist = 0 3 1 4");
    expect(runGraph("bellman", 4, g, true, 0).result).toBe("dist = 0 3 1 4");
  });
  it("Bellman-Ford detects a negative cycle", () => {
    const g = E("0 1 3, 1 2 -2, 2 3 2, 3 1 -1", 4);
    expect(runGraph("bellman", 4, g, true, 0).result).toMatch(/negative cycle/);
  });
  it("circleLayout puts vertex 0 at the top", () => {
    const p = circleLayout(4);
    expect(p[0].x).toBeCloseTo(0);
    expect(p[0].y).toBeCloseTo(-1);
  });
});

describe("runSearch", () => {
  it("counts subsets, combinations and permutations", () => {
    expect(runSearch([1, 2, 3], 0, 0, "subsets", true).answers.length).toBe(8);
    expect(runSearch([1, 2, 3, 4], 2, 0, "combinations", true).answers).toEqual(
      ["1 2", "1 3", "1 4", "2 3", "2 4", "3 4"],
    );
    expect(runSearch([1, 2, 3], 0, 0, "permutations", true).answers.length).toBe(6);
  });
  it("combination sum with and without pruning: same answers, fewer calls", () => {
    const a = runSearch([5, 2, 3], 0, 8, "combsum", true);
    const b = runSearch([5, 2, 3], 0, 8, "combsum", false);
    expect(a.answers).toEqual(["2 2 2 2", "2 3 3", "3 5"]);
    expect(b.answers).toEqual(a.answers);
    expect(a.calls).toBeLessThan(b.calls);
  });
  it("subset sum with the sorted break", () => {
    const r = runSearch([3, 1, 4, 2], 0, 5, "subsetsum", true);
    expect(r.answers).toEqual(["1 4", "2 3"]);
    expect(r.events.some((e) => e.kind === "prune")).toBe(true);
  });
  it("the size cap prunes k-combinations", () => {
    const a = runSearch([1, 2, 3, 4, 5, 6], 4, 0, "combinations", true);
    const b = runSearch([1, 2, 3, 4, 5, 6], 4, 0, "combinations", false);
    expect(a.answers.length).toBe(15);
    expect(b.answers.length).toBe(15);
    expect(a.calls).toBeLessThan(b.calls);
  });
  it("every choose has a matching undo", () => {
    const r = runSearch([1, 2, 3], 0, 0, "permutations", true);
    const ch = r.events.filter((e) => e.kind === "choose").length;
    const un = r.events.filter((e) => e.kind === "undo").length;
    expect(ch).toBe(un);
  });
  it("refuses non-positive items in sum modes", () => {
    expect(runSearch([0, 1], 0, 2, "combsum", true).answers).toEqual([]);
  });
});

describe("annotateTree", () => {
  const t = parseTree("3 2 3 null 3 null 1")!;
  it("house robber pairs: (take, skip) per node", () => {
    const ann = annotateTree(t, "rob");
    // node 2: take 2, skip 3 (its child 3); right node 3: take 3, skip 1.
    // root: take 3 + 3 + 1 = 7; skip = max(2, 3) + max(3, 1) = 6
    expect(ann[0]).toBe("7/6");
    expect(ann[1]).toBe("2/3");
  });
  it("subtree sums and sizes", () => {
    expect(annotateTree(t, "sum")[0]).toBe("12");
    expect(annotateTree(t, "size")[0]).toBe("5");
  });
  it("best downward gain drops negative branches", () => {
    const g = parseTree("-10 9 20 null null 15 7")!;
    expect(annotateTree(g, "gain")).toEqual(["25", "9", "35", "15", "7"]);
  });
  it("camera states: a chain of three needs one guard, in the middle", () => {
    const c = parseTree("0 0 null 0")!;
    expect(annotateTree(c, "camera")).toEqual(["ok", "cam", "—"]);
  });
  it("none leaves labels empty", () => {
    expect(annotateTree(t, "none").every((s) => s === "")).toBe(true);
  });
});

describe("editing a BST", () => {
  const t = parseTree("50 30 70 20 40 60 80")!;
  it("inserts by descent", () => {
    expect(bstInsertLine(t, 45)).toBe("50 30 70 20 40 60 80 null null null 45");
    expect(bstInsertLine({ nodes: [], root: -1 }, 5)).toBe("5");
  });
  it("deletes with the in-order successor", () => {
    expect(bstDeleteLine(t, 50)).toBe("60 30 70 20 40 null 80");
    expect(bstDeleteLine(t, 20)).toBe("50 30 70 null 40 60 80");
    expect(bstDeleteLine(t, 99)).toBe("50 30 70 20 40 60 80");
    expect(bstDeleteLine(parseTree("7")!, 7)).toBe("null");
  });
  it("rotations keep the in-order sequence", () => {
    const left = rotateLine(t, 0, "left")!;
    expect(left).toBe("70 50 80 30 60 null null 20 40");
    const back = rotateLine(parseTree(left)!, 0, "right")!;
    expect(back).toBe("50 30 70 20 40 60 80");
    const inorder = (line: string) => {
      const p = parseTree(line)!;
      return treeOrders(p).in.map((i) => p.nodes[i].val);
    };
    expect(inorder(left)).toEqual(inorder("50 30 70 20 40 60 80"));
    expect(rotateLine(parseTree("5 3")!, 0, "left")).toBeNull();
  });
  it("rotates a non-root node and re-links its parent", () => {
    const r = rotateLine(t, 1, "right")!; // 30 lifts 20
    expect(r).toBe("50 20 70 null 30 60 80 null 40");
  });
});

describe("new graph algorithms", () => {
  const E = (s: string, n: number) => parseEdges(s, n).edges;
  it("two-colouring finds the odd cycle", () => {
    expect(runGraph("bipartite", 4, E("0 1, 1 2, 2 3, 3 0", 4), false, 0).result).toMatch(/^bipartite/);
    expect(runGraph("bipartite", 3, E("0 1, 1 2, 2 0", 3), false, 0).result).toMatch(/not bipartite/);
  });
  it("0-1 BFS matches Dijkstra and refuses other weights", () => {
    const g = E("0 1 1, 0 2 0, 2 1 0, 1 3 1, 2 3 1", 4);
    expect(runGraph("zeroone", 4, g, true, 0).result).toBe(runGraph("dijkstra", 4, g, true, 0).result);
    expect(runGraph("zeroone", 2, E("0 1 5", 2), true, 0).result).toMatch(/not a 0-1 graph/);
  });
  it("Floyd–Warshall fills the table and spots negative cycles", () => {
    const r = runGraph("floyd", 3, E("0 1 4, 1 2 1, 0 2 7", 3), true, 0);
    const last = r.steps[r.steps.length - 1].state;
    expect(last[0]).toEqual(["row 0", "0 4 5"]);
    expect(runGraph("floyd", 2, E("0 1 1, 1 0 -3", 2), true, 0).result).toMatch(/negative cycle/);
  });
});

describe("mazes", () => {
  it("parses rectangular mazes only", () => {
    expect(parseMaze("S.\n.T")).toEqual(["S.", ".T"]);
    expect(parseMaze("S..\n.T")).toBeNull();
    expect(parseMaze("")).toBeNull();
  });
  it("BFS finds the shortest path around walls", () => {
    const r = runMaze(parseMaze("S.#\n.##\n..T")!, "bfs");
    expect(r.result).toBe("shortest path: 4 steps");
    expect(r.path.length).toBe(5);
    expect(r.path[0]).toEqual([0, 0]);
    expect(r.path[4]).toEqual([2, 2]);
  });
  it("reports an unreachable target", () => {
    expect(runMaze(parseMaze("S#T")!, "bfs").result).toBe("T cannot be reached");
  });
  it("multi-source BFS measures to the nearest S", () => {
    const r = runMaze(parseMaze("S...S")!, "multi");
    expect(r.value[0]).toEqual([0, 1, 2, 1, 0]);
  });
  it("flood fill counts regions", () => {
    expect(runMaze(parseMaze("..#..\n###..\n.#...")!, "flood").result).toBe("3 open region(s)");
  });
});
