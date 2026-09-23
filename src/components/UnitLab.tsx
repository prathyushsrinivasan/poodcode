import { useMemo, useState } from "react";
import type { Lab } from "../types";
import { Markdown } from "./Markdown";
import {
  bitRows,
  bits32,
  cellImages,
  extendedEuclid,
  factorize,
  gcdBig,
  javaLongMul,
  neighbours,
  parseBig,
  phiFrom,
  powerSteps,
  ringOf,
  spiralOrder,
  toInt32,
} from "../lib/unitLab";
import {
  GRAPH_ALGOS,
  GRAPH_ALGO_NAMES,
  MAZE_WALKS,
  MAZE_WALK_NAMES,
  SEARCH_MODES,
  SEARCH_MODE_NAMES,
  TREE_NOTES,
  TREE_NOTE_NAMES,
  annotateTree,
  bstDeleteLine,
  bstInsertLine,
  parseMaze,
  rotateLine,
  runMaze,
  type MazeWalk,
  type TreeNote,
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
  type GraphAlgo,
  type SearchMode,
} from "../lib/graphLab";

/**
 * A unit's interactive lab: a playground that computes live in the page, with
 * the author's presets as one-click starting points. Three kinds, each over the
 * arithmetic in `lib/unitLab.ts`:
 *
 *   bits     two ints and a shift, every operator side by side as 32 bits
 *   modular  gcd / lcm, the extended-Euclid table, square-and-multiply, φ
 *   grid     click a cell: neighbours, images under each rotation, keys, spiral
 *   tree     a level-order tree drawn, its orders and stats, BST ranges, a descent
 *   graph    an edge list drawn, and one algorithm's run scrubbed step by step
 *   search   a backtracking run's event log, with and without pruning
 * (the last three over `lib/graphLab.ts`).
 */
export function UnitLab({ lab }: { lab: Lab }) {
  const [values, setValues] = useState<Record<string, string>>(
    () => ({ ...(lab.presets[0]?.values ?? {}) })
  );
  const [preset, setPreset] = useState(0);
  const set = (k: string, v: string) => setValues((p) => ({ ...p, [k]: v }));

  return (
    <div className="card" style={{ padding: 14 }}>
      <Markdown>{lab.intro}</Markdown>
      <div className="row" style={{ flexWrap: "wrap", gap: 6, margin: "8px 0 12px" }}>
        {lab.presets.map((p, i) => (
          <button
            key={p.label}
            className={i === preset ? "" : "ghost"}
            style={{ fontSize: 12, padding: "3px 10px" }}
            onClick={() => {
              setPreset(i);
              setValues({ ...p.values });
            }}
          >
            {p.label}
          </button>
        ))}
      </div>
      {lab.kind === "bits" && <BitsLab v={values} set={set} />}
      {lab.kind === "modular" && <ModularLab v={values} set={set} />}
      {lab.kind === "grid" && <GridLab v={values} set={set} />}
      {lab.kind === "tree" && <TreeLab v={values} set={set} />}
      {lab.kind === "graph" && <GraphLab key={preset} v={values} set={set} />}
      {lab.kind === "search" && <SearchLab v={values} set={set} />}
      {lab.kind === "maze" && <MazeLab key={preset} v={values} set={set} />}
    </div>
  );
}

type LabProps = { v: Record<string, string>; set: (k: string, v: string) => void };

function Field({ label, name, v, set, width = 150 }: LabProps & { label: string; name: string; width?: number }) {
  const bad = parseBig(v[name] ?? "") === null;
  return (
    <label className="dim" style={{ fontSize: 13, display: "inline-flex", alignItems: "center", gap: 6 }}>
      {label}
      <input
        className="mono"
        aria-label={label}
        value={v[name] ?? ""}
        onChange={(e) => set(name, e.target.value)}
        style={{ width, borderColor: bad ? "var(--bad)" : undefined }}
      />
    </label>
  );
}

function Bits({ value, compare }: { value: bigint; compare?: bigint }) {
  const s = bits32(value);
  const c = compare === undefined ? null : bits32(compare);
  return (
    <span className="mono" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
      {s.split("").map((ch, i) => (
        <span
          key={i}
          style={{
            marginLeft: i > 0 && i % 8 === 0 ? 6 : 0,
            color: c && c[i] !== ch ? "var(--accent)" : ch === "1" ? undefined : "var(--faint, #888)",
            fontWeight: c && c[i] !== ch ? 700 : undefined,
          }}
        >
          {ch}
        </span>
      ))}
    </span>
  );
}

function BitsLab({ v, set }: LabProps) {
  const a = parseBig(v.a ?? "");
  const b = parseBig(v.b ?? "");
  const k = parseBig(v.k ?? "");
  const rows = a !== null && b !== null && k !== null ? bitRows(a, b, k) : null;
  return (
    <>
      <div className="row" style={{ gap: 14, flexWrap: "wrap", marginBottom: 10 }}>
        <Field label="a" name="a" v={v} set={set} />
        <Field label="b" name="b" v={v} set={set} />
        <Field label="shift k" name="k" v={v} set={set} width={70} />
      </div>
      {!rows ? (
        <div className="dim">Type integers (decimal, 0x… or 0b…).</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="data">
            <thead>
              <tr>
                <th>Expression</th>
                <th>32 bits (changed vs a in colour)</th>
                <th>Value</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ cursor: "default" }}>
                <td className="mono">a</td>
                <td><Bits value={a!} /></td>
                <td className="mono">{String(toInt32(a!))}</td>
                <td className="dim">{toInt32(a!) !== a ? "wrapped to a Java int" : "as typed"}</td>
              </tr>
              <tr style={{ cursor: "default" }}>
                <td className="mono">b</td>
                <td><Bits value={b!} /></td>
                <td className="mono">{String(toInt32(b!))}</td>
                <td />
              </tr>
              {rows.map((r) => (
                <tr key={r.expr} style={{ cursor: "default" }}>
                  <td className="mono">{r.expr}</td>
                  <td>{r.expr.includes("(a)") ? "" : <Bits value={r.value} compare={a!} />}</td>
                  <td className="mono">{String(r.value)}</td>
                  <td className="dim">{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function ModularLab({ v, set }: LabProps) {
  const a = parseBig(v.a ?? "");
  const b = parseBig(v.b ?? "");
  const m = parseBig(v.m ?? "");
  const ok = a !== null && b !== null && m !== null && m >= 1n && a >= 0n && b >= 0n;
  const res = useMemo(() => {
    if (!ok) return null;
    const g = gcdBig(a!, m!);
    const ee = extendedEuclid(a!, m!);
    const pw = powerSteps(a!, b!, m!);
    const fac = factorize(m!);
    const fermat = m! > 2n ? powerSteps(a!, m! - 2n, m!).value : null;
    return { g, lcm: g === 0n ? 0n : (a! / g) * m!, ee, pw, fac, fermat };
  }, [ok, a, b, m]);

  return (
    <>
      <div className="row" style={{ gap: 14, flexWrap: "wrap", marginBottom: 10 }}>
        <Field label="a" name="a" v={v} set={set} width={190} />
        <Field label="exponent b" name="b" v={v} set={set} width={130} />
        <Field label="modulus m" name="m" v={v} set={set} width={130} />
      </div>
      {!res ? (
        <div className="dim">Type non-negative integers, with m ≥ 1.</div>
      ) : (
        <>
          <div className="grid cols-2" style={{ gap: 8, marginBottom: 12 }}>
            <Stat label="gcd(a, m)" value={String(res.g)} />
            <Stat label="lcm(a, m) = a / gcd · m" value={String(res.lcm)} />
            <Stat
              label="a⁻¹ mod m (extended Euclid)"
              value={res.ee.inverse === null ? `none — gcd is ${res.ee.gcd}` : String(res.ee.inverse)}
            />
            <Stat
              label="Fermat's a^(m−2) mod m"
              value={
                res.fermat === null
                  ? "—"
                  : res.ee.inverse !== null && res.fermat === res.ee.inverse
                  ? `${res.fermat} ✓ agrees`
                  : `${res.fermat} ✗ wrong here (m is not prime or a ≡ 0)`
              }
            />
            <Stat label={`a^b mod m`} value={String(res.pw.value)} />
            <Stat
              label="m factorised, and φ(m)"
              value={
                res.fac === null
                  ? "too large to factor here"
                  : res.fac.length === 0
                  ? "—"
                  : `${res.fac.map(([p, e]) => (e > 1 ? `${p}^${e}` : String(p))).join(" · ")}   φ = ${phiFrom(m!, res.fac)}`
              }
            />
            <Stat
              label="a · a in a Java long (no reduction)"
              value={
                javaLongMul(a!, a!) === a! * a! ? `${a! * a!} (fits)` : `${javaLongMul(a!, a!)} (overflowed!)`
              }
            />
          </div>
          <h4 style={{ margin: "8px 0 4px" }}>Extended Euclid — every row keeps r ≡ a·s (mod m)</h4>
          <div style={{ overflowX: "auto", marginBottom: 12 }}>
            <table className="data">
              <thead>
                <tr><th>q</th><th>r₀</th><th>s₀</th><th>r₁</th><th>s₁</th></tr>
              </thead>
              <tbody>
                {res.ee.steps.map((s, i) => (
                  <tr key={i} style={{ cursor: "default" }}>
                    <td className="mono">{s.q === null ? "start" : String(s.q)}</td>
                    <td className="mono">{String(s.r0)}</td>
                    <td className="mono">{String(s.s0)}</td>
                    <td className="mono">{String(s.r1)}</td>
                    <td className="mono">{String(s.s1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h4 style={{ margin: "8px 0 4px" }}>Square and multiply — one row per bit of b</h4>
          <div style={{ overflowX: "auto" }}>
            <table className="data">
              <thead>
                <tr><th>remaining e</th><th>low bit</th><th>base (squared each row)</th><th>result</th></tr>
              </thead>
              <tbody>
                {res.pw.steps.map((s, i) => (
                  <tr key={i} style={{ cursor: "default" }}>
                    <td className="mono">{String(s.e)}</td>
                    <td className="mono">{String(s.bit)}</td>
                    <td className="mono">{String(s.base)}</td>
                    <td className="mono">{s.bit === 1n ? <strong>{String(s.result)}</strong> : String(s.result)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card" style={{ padding: "8px 10px", margin: 0 }}>
      <div className="dim" style={{ fontSize: 12 }}>{label}</div>
      <div className="mono" style={{ wordBreak: "break-all" }}>{value}</div>
    </div>
  );
}

const GRID_MAX = 12;

function GridLab({ v, set }: LabProps) {
  const clamp = (x: bigint | null, lo: number, hi: number) =>
    x === null ? lo : Math.max(lo, Math.min(hi, Number(x)));
  const r = clamp(parseBig(v.rows ?? ""), 1, GRID_MAX);
  const c = clamp(parseBig(v.cols ?? ""), 1, GRID_MAX);
  const i = clamp(parseBig(v.i ?? ""), 0, r - 1);
  const j = clamp(parseBig(v.j ?? ""), 0, c - 1);
  const [eight, setEight] = useState(true);
  const [show, setShow] = useState("Rotate 90° clockwise");

  const nb = new Set(neighbours(r, c, i, j, eight).map(([a, b]) => `${a},${b}`));
  const spiral = spiralOrder(r, c);
  const spiralIndex = spiral.findIndex(([a, b]) => a === i && b === j);
  const images = cellImages(r, c, i, j);
  const img = images.find((x) => x.name === show) ?? images[0];

  return (
    <>
      <div className="row" style={{ gap: 14, flexWrap: "wrap", marginBottom: 10 }}>
        <Field label="rows" name="rows" v={v} set={set} width={50} />
        <Field label="cols" name="cols" v={v} set={set} width={50} />
        <label className="dim" style={{ fontSize: 13 }}>
          <input type="checkbox" checked={eight} onChange={(e) => setEight(e.target.checked)} /> 8 neighbours
        </label>
        <span className="faint" style={{ fontSize: 12 }}>Click a cell. Up to {GRID_MAX} × {GRID_MAX}.</span>
      </div>
      <div className="row" style={{ gap: 20, flexWrap: "wrap", alignItems: "flex-start" }}>
        <div
          role="grid"
          aria-label="grid"
          style={{ display: "grid", gridTemplateColumns: `repeat(${c}, 30px)`, gap: 2 }}
        >
          {Array.from({ length: r * c }, (_, id) => {
            const a = Math.floor(id / c), b = id % c;
            const sel = a === i && b === j;
            const isNb = nb.has(`${a},${b}`);
            return (
              <button
                key={id}
                title={`(${a}, ${b})  id ${id}`}
                onClick={() => {
                  set("i", String(a));
                  set("j", String(b));
                }}
                style={{
                  width: 30,
                  height: 30,
                  padding: 0,
                  fontSize: 10,
                  background: sel ? "var(--accent)" : isNb ? "color-mix(in srgb, var(--accent) 25%, transparent)" : undefined,
                  color: sel ? "var(--bg, #fff)" : undefined,
                }}
              >
                {spiral.findIndex(([x, y]) => x === a && y === b)}
              </button>
            );
          })}
        </div>
        <div style={{ minWidth: 240, flex: 1 }}>
          <table className="data">
            <tbody>
              <Kv k="Cell" v={`(${i}, ${j})`} />
              <Kv k="Flattened id  i · cols + j" v={`${i} · ${c} + ${j} = ${i * c + j}`} />
              <Kv k={`${eight ? 8 : 4}-neighbours inside the grid`} v={String(nb.size)} />
              <Kv k="↘ diagonal key  i − j" v={String(i - j)} />
              <Kv k="↙ diagonal key  i + j" v={String(i + j)} />
              <Kv k="Ring (layer)" v={String(ringOf(r, c, i, j))} />
              <Kv k="Position in spiral order" v={`${spiralIndex} of ${r * c} (numbers on the cells)`} />
            </tbody>
          </table>
          <div style={{ marginTop: 10 }}>
            <select value={show} onChange={(e) => setShow(e.target.value)} aria-label="transformation">
              {images.map((x) => (
                <option key={x.name}>{x.name}</option>
              ))}
            </select>
            <div className="mono" style={{ marginTop: 6 }}>
              ({i}, {j}) → ({img.to[0]}, {img.to[1]}) in a {img.shape} grid
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function Kv({ k, v }: { k: string; v: string }) {
  return (
    <tr style={{ cursor: "default" }}>
      <td className="dim">{k}</td>
      <td className="mono">{v}</td>
    </tr>
  );
}

// ------------------------------------------------------- Trees & Graphs labs

function TextField({
  label,
  name,
  v,
  set,
  cls = "lab-text-mid",
  bad = false,
}: LabProps & { label: string; name: string; cls?: string; bad?: boolean }) {
  return (
    <label className="lab-label">
      {label}
      <input
        className={`lab-text ${cls}${bad ? " lab-text-bad" : ""}`}
        aria-label={label}
        value={v[name] ?? ""}
        onChange={(e) => set(name, e.target.value)}
      />
    </label>
  );
}

function StatBox({ k, v }: { k: string; v: string }) {
  return (
    <div className="lab-stat">
      <div className="lab-stat-k">{k}</div>
      <div className="lab-stat-v">{v}</div>
    </div>
  );
}

const TREE_DX = 40;
const TREE_DY = 56;

function TreeLab({ v, set }: LabProps) {
  const tree = useMemo(() => parseTree(v.tree ?? ""), [v.tree]);
  const [picked, setPicked] = useState(0);
  const value = parseBig(v.value ?? "");
  if (!tree) {
    return (
      <>
        <div className="lab-row">
          <TextField label="tree (level order)" name="tree" v={v} set={set} cls="lab-text-wide" bad />
        </div>
        <div className="dim">Numbers and `null`, in level order — at most 63 nodes.</div>
      </>
    );
  }
  const n = tree.nodes.length;
  const sel = picked < n ? picked : 0;
  const note = ((TREE_NOTES as readonly string[]).includes(v.note ?? "") ? v.note : "none") as TreeNote;
  const notes = annotateTree(tree, note);
  const pos = layoutTree(tree);
  const orders = treeOrders(tree);
  const stats = treeStats(tree);
  const valsOf = (ids: number[]) => ids.map((i) => tree.nodes[i].val).join(" ") || "—";
  const descent = value !== null && n > 0 ? bstDescent(tree, Number(value)) : null;
  const onPath = new Set(descent?.path ?? []);
  const info = n > 0 ? nodeInfo(tree, sel) : null;
  const depth = n ? Math.max(...pos.map((p) => p.y)) + 1 : 1;
  const W = Math.max(1, n) * TREE_DX + 20;
  const H = depth * TREE_DY + 16;
  const num = value === null ? null : Number(value);
  const rotate = (dir: "left" | "right") => {
    const line = rotateLine(tree, sel, dir);
    if (line) set("tree", line);
  };
  const ops = (
    <div className="lab-ops">
      <label className="lab-label">
        show on each node
        <select aria-label="annotation" value={note} onChange={(e) => set("note", e.target.value)}>
          {TREE_NOTES.map((k) => (
            <option key={k} value={k}>
              {TREE_NOTE_NAMES[k]}
            </option>
          ))}
        </select>
      </label>
      <button className="ghost" disabled={num === null} onClick={() => num !== null && set("tree", bstInsertLine(tree, num))}>
        insert {num ?? "?"}
      </button>
      <button className="ghost" disabled={num === null || n === 0} onClick={() => num !== null && set("tree", bstDeleteLine(tree, num))}>
        delete {num ?? "?"}
      </button>
      <button className="ghost" disabled={n === 0 || tree.nodes[sel]?.right < 0} onClick={() => rotate("left")}>
        rotate left at {n ? tree.nodes[sel].val : "?"}
      </button>
      <button className="ghost" disabled={n === 0 || tree.nodes[sel]?.left < 0} onClick={() => rotate("right")}>
        rotate right at {n ? tree.nodes[sel].val : "?"}
      </button>
    </div>
  );
  const px = (id: number) => 10 + pos[id].x * TREE_DX + TREE_DX / 2;
  const py = (id: number) => 24 + pos[id].y * TREE_DY;
  const range = (lo: number | null, hi: number | null) => `(${lo ?? "−∞"}, ${hi ?? "+∞"})`;

  return (
    <>
      <div className="lab-row">
        <TextField label="tree (level order)" name="tree" v={v} set={set} cls="lab-text-wide" />
        <Field label="search / insert" name="value" v={v} set={set} width={80} />
      </div>
      {ops}
      {n === 0 ? (
        <div className="dim">The empty tree.</div>
      ) : (
        <>
          <div className="lab-split">
            <svg className="lab-svg" width={W} height={H} role="img" aria-label="the tree">
              {tree.nodes.map((nd) =>
                [nd.left, nd.right].filter((c) => c >= 0).map((c) => (
                  <line
                    key={`${nd.id}-${c}`}
                    className={onPath.has(nd.id) && onPath.has(c) ? "edge edge-on" : "edge"}
                    x1={px(nd.id)}
                    y1={py(nd.id)}
                    x2={px(c)}
                    y2={py(c)}
                  />
                )),
              )}
              {tree.nodes.map((nd) => {
                const cls = [
                  "node",
                  onPath.has(nd.id) ? "node-path" : "",
                  nd.id === sel ? "node-focus" : "",
                  nd.id === stats.bstBreaker ? "node-bad" : "",
                ].join(" ");
                return (
                  <g key={nd.id} onClick={() => setPicked(nd.id)}>
                    <title>{`node ${nd.val}`}</title>
                    <circle className={cls} cx={px(nd.id)} cy={py(nd.id)} r={15} />
                    <text className="node-text" x={px(nd.id)} y={py(nd.id)}>
                      {nd.val}
                    </text>
                    {notes[nd.id] && (
                      <text className="node-note" x={px(nd.id)} y={py(nd.id) + 26}>
                        {notes[nd.id]}
                      </text>
                    )}
                  </g>
                );
              })}
            </svg>
            <div className="lab-grow">
              <div className="lab-stats">
                <StatBox k="nodes" v={String(stats.size)} />
                <StatBox k="height (nodes on the longest root path)" v={String(stats.height)} />
                <StatBox k="leaves" v={String(stats.leaves)} />
                <StatBox k="diameter (edges)" v={String(stats.diameter)} />
                <StatBox k="height-balanced?" v={stats.balanced ? "yes" : "no"} />
                <StatBox
                  k="valid BST?"
                  v={
                    stats.bstBreaker < 0
                      ? "yes"
                      : `no — ${tree.nodes[stats.bstBreaker].val} is outside ${(() => {
                          const i = nodeInfo(tree, stats.bstBreaker);
                          return range(i.lo, i.hi);
                        })()}`
                  }
                />
              </div>
              <table className="data">
                <tbody>
                  <Kv k="pre-order" v={valsOf(orders.pre)} />
                  <Kv k="in-order" v={valsOf(orders.in)} />
                  <Kv k="post-order" v={valsOf(orders.post)} />
                  <Kv k="level order" v={valsOf(orders.level)} />
                </tbody>
              </table>
            </div>
          </div>
          {info && (
            <div className="lab-note">
              Node <strong>{tree.nodes[sel].val}</strong>: depth {info.depth}, height {info.height}, subtree
              size {info.size}; root path {valsOf(info.path)}; BST interval {range(info.lo, info.hi)}{" "}
              {info.inRange ? "— inside it" : "— OUTSIDE it"}. Click another node.
            </div>
          )}
          {descent && (
            <div className="lab-note">
              Searching for <strong>{String(value)}</strong> walks {valsOf(descent.path)}
              {descent.found
                ? " and finds it."
                : descent.attach
                ? ` and falls off: an insert would become the ${descent.attach.side} child of ${
                    tree.nodes[descent.attach.parent].val
                  }.`
                : "."}
              {stats.bstBreaker >= 0 && " (The tree is not a valid BST, so this descent can miss values that are present.)"}
            </div>
          )}
        </>
      )}
    </>
  );
}

const GRAPH_MAX = 12;
const GRAPH_R = 120;

function GraphLab({ v, set }: LabProps) {
  const nRaw = parseBig(v.n ?? "");
  const n = nRaw === null ? 1 : Math.max(1, Math.min(GRAPH_MAX, Number(nRaw)));
  const directed = (v.directed ?? "no") === "yes";
  const src = Math.max(0, Math.min(n - 1, Number(parseBig(v.source ?? "") ?? 0)));
  const algo = (GRAPH_ALGOS as readonly string[]).includes(v.algo ?? "") ? (v.algo as GraphAlgo) : "bfs";
  const parsed = useMemo(() => parseEdges(v.edges ?? "", n), [v.edges, n]);
  const run = useMemo(
    () => (parsed.error ? null : runGraph(algo, n, parsed.edges, directed, src)),
    [parsed, algo, n, directed, src],
  );
  const [step, setStep] = useState(0);
  const total = run ? run.steps.length : 0;
  const at = Math.min(step, Math.max(0, total - 1));
  const cur = run && total ? run.steps[at] : null;
  const pts = circleLayout(n, GRAPH_R);
  const cx = (i: number) => pts[i].x + GRAPH_R + 30;
  const cy = (i: number) => pts[i].y + GRAPH_R + 30;
  const size = 2 * GRAPH_R + 60;
  const weighted = parsed.edges.some((e) => e.w !== 1);
  const chosen = new Set(cur?.chosen ?? []);
  const done = new Set(cur?.done ?? []);
  const focus = new Set(cur?.focus ?? []);
  const edgeStyle = directed ? "url(#lab-arrow)" : undefined;

  return (
    <>
      <div className="lab-row">
        <Field label="vertices n" name="n" v={v} set={set} width={50} />
        <Field label="source" name="source" v={v} set={set} width={50} />
        <label className="lab-label">
          <input
            type="checkbox"
            checked={directed}
            onChange={(e) => set("directed", e.target.checked ? "yes" : "no")}
          />{" "}
          directed
        </label>
        <label className="lab-label">
          algorithm
          <select
            aria-label="algorithm"
            value={algo}
            onChange={(e) => {
              set("algo", e.target.value);
              setStep(0);
            }}
          >
            {GRAPH_ALGOS.map((a) => (
              <option key={a} value={a}>
                {GRAPH_ALGO_NAMES[a]}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="lab-split">
        <label className="lab-label">
          <span>
            edges
            <br />
            <span className="faint">u v [w], one per line</span>
          </span>
          <textarea
            className={`lab-edges${parsed.error ? " lab-text-bad" : ""}`}
            aria-label="edges"
            value={v.edges ?? ""}
            onChange={(e) => {
              set("edges", e.target.value);
              setStep(0);
            }}
          />
        </label>
        <svg className="lab-svg" width={size} height={size} role="img" aria-label="the graph">
          <defs>
            <marker id="lab-arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="7" markerHeight="7" orient="auto">
              <path d="M0,0 L10,5 L0,10 z" fill="currentColor" className="edge-label" />
            </marker>
          </defs>
          {parsed.edges.map((e, i) => (
            <g key={i}>
              <line
                className={chosen.has(i) ? "edge edge-on" : "edge"}
                x1={cx(e.u)}
                y1={cy(e.u)}
                x2={cx(e.v)}
                y2={cy(e.v)}
                markerEnd={edgeStyle}
              />
              {weighted && (
                <text className="edge-label" x={(cx(e.u) + cx(e.v)) / 2 + 4} y={(cy(e.u) + cy(e.v)) / 2 - 4}>
                  {e.w}
                </text>
              )}
            </g>
          ))}
          {pts.map((_, i) => (
            <g key={i}>
              <circle
                className={["node", done.has(i) ? "node-done" : "", focus.has(i) ? "node-focus" : ""].join(" ")}
                cx={cx(i)}
                cy={cy(i)}
                r={14}
              />
              <text className="node-text" x={cx(i)} y={cy(i)}>
                {i}
              </text>
            </g>
          ))}
        </svg>
      </div>
      {parsed.error ? (
        <div className="lab-note">{parsed.error}</div>
      ) : (
        cur && (
          <>
            <div className="lab-steps">
              <button className="ghost" disabled={at === 0} onClick={() => setStep(at - 1)} aria-label="previous step">
                ◀
              </button>
              <input
                type="range"
                min={0}
                max={Math.max(0, total - 1)}
                value={at}
                onChange={(e) => setStep(Number(e.target.value))}
                aria-label="step"
              />
              <button className="ghost" disabled={at >= total - 1} onClick={() => setStep(at + 1)} aria-label="next step">
                ▶
              </button>
              <span className="mono faint">
                {at + 1} / {total}
              </span>
            </div>
            <div className="lab-note">{cur.note}</div>
            <table className="data">
              <tbody>
                {cur.state.map(([k, val]) => (
                  <Kv key={k} k={k} v={val} />
                ))}
                <Kv k="result" v={run!.result} />
              </tbody>
            </table>
          </>
        )
      )}
    </>
  );
}

function MazeLab({ v, set }: LabProps) {
  const rows = parseMaze(v.grid ?? "");
  const walk = ((MAZE_WALKS as readonly string[]).includes(v.walk ?? "") ? v.walk : "bfs") as MazeWalk;
  const run = useMemo(() => (rows ? runMaze(rows, walk) : null), [v.grid, walk]); // rows derives from v.grid
  const [step, setStep] = useState<number | null>(null);
  const last = run ? Math.max(0, run.layers - 1) : 0;
  const at = step === null ? last : Math.min(step, last);
  const onPath = new Set((run && at === last ? run.path : []).map(([i, j]) => `${i},${j}`));

  return (
    <>
      <div className="lab-split">
        <label className="lab-label">
          <span>
            maze
            <br />
            <span className="faint"># wall, S start, T target</span>
          </span>
          <textarea
            className={`lab-edges${rows ? "" : " lab-text-bad"}`}
            aria-label="maze"
            value={v.grid ?? ""}
            onChange={(e) => {
              set("grid", e.target.value);
              setStep(null);
            }}
          />
        </label>
        <div className="lab-grow">
          <label className="lab-label">
            walk
            <select
              aria-label="walk"
              value={walk}
              onChange={(e) => {
                set("walk", e.target.value);
                setStep(null);
              }}
            >
              {MAZE_WALKS.map((w) => (
                <option key={w} value={w}>
                  {MAZE_WALK_NAMES[w]}
                </option>
              ))}
            </select>
          </label>
          {run && (
            <>
              <div className="lab-steps">
                <span className="mono faint">{walk === "flood" ? "region" : "distance"} ≤</span>
                <input
                  type="range"
                  min={0}
                  max={last}
                  value={at}
                  onChange={(e) => setStep(Number(e.target.value))}
                  aria-label="layer"
                />
                <span className="mono faint">
                  {at} / {last}
                </span>
              </div>
              <div className="lab-note">{run.result}</div>
            </>
          )}
        </div>
      </div>
      {!rows || !run ? (
        <div className="dim">A rectangle of up to 20 × 20 cells.</div>
      ) : (
        <div className="maze" style={{ gridTemplateColumns: `repeat(${rows[0].length}, 26px)` }} role="grid" aria-label="maze">
          {rows.flatMap((r, i) =>
            Array.from(r).map((ch, j) => {
              const val = run.value[i][j];
              const lay = run.layer[i][j];
              const seen = lay >= 0 && lay <= at;
              const cls = [
                "maze-cell",
                ch === "#" ? "maze-wall" : "",
                seen ? "maze-seen" : "",
                seen && lay === at && walk !== "flood" ? "maze-front" : "",
                onPath.has(`${i},${j}`) ? "maze-path" : "",
              ].join(" ");
              const label = ch === "S" || ch === "T" ? ch : seen && val >= 0 ? String(val) : "";
              return (
                <div key={`${i}-${j}`} className={cls} title={`(${i}, ${j})`}>
                  {ch === "#" ? "" : label}
                </div>
              );
            }),
          )}
        </div>
      )}
    </>
  );
}

function SearchLab({ v, set }: LabProps) {
  const items = (v.items ?? "").trim().split(/[\s,]+/).filter(Boolean).map(Number);
  const bad = items.some((x) => !Number.isInteger(x)) || items.length > 10;
  const k = Number(parseBig(v.k ?? "") ?? 0);
  const target = Number(parseBig(v.target ?? "") ?? 0);
  const mode = (SEARCH_MODES as readonly string[]).includes(v.mode ?? "") ? (v.mode as SearchMode) : "subsets";
  const [prune, setPrune] = useState(true);
  const res = useMemo(() => {
    if (bad) return null;
    return { on: runSearch(items, k, target, mode, true), off: runSearch(items, k, target, mode, false) };
  }, [v.items, k, target, mode, bad]); // `items` is derived from v.items
  const shown = res ? (prune ? res.on : res.off) : null;

  return (
    <>
      <div className="lab-row">
        <TextField label="items" name="items" v={v} set={set} cls="lab-text-wide" bad={bad} />
        <label className="lab-label">
          search
          <select aria-label="search" value={mode} onChange={(e) => set("mode", e.target.value)}>
            {SEARCH_MODES.map((m) => (
              <option key={m} value={m}>
                {SEARCH_MODE_NAMES[m]}
              </option>
            ))}
          </select>
        </label>
        {mode === "combinations" && <Field label="k" name="k" v={v} set={set} width={50} />}
        {(mode === "subsetsum" || mode === "combsum") && <Field label="target" name="target" v={v} set={set} width={60} />}
        <label className="lab-label">
          <input type="checkbox" checked={prune} onChange={(e) => setPrune(e.target.checked)} /> prune
        </label>
      </div>
      {!res || !shown ? (
        <div className="dim">Up to 10 integers.</div>
      ) : (
        <>
          <div className="lab-stats">
            <StatBox k="answers" v={String(shown.answers.length)} />
            <StatBox k="calls with pruning" v={String(res.on.calls)} />
            <StatBox k="calls without" v={String(res.off.calls)} />
            <StatBox
              k="saved by pruning"
              v={res.off.calls ? `${Math.round((100 * (res.off.calls - res.on.calls)) / res.off.calls)}%` : "—"}
            />
          </div>
          <div className="lab-split">
            <div className="lab-grow">
              <div className="dim">Event log (indent = depth){shown.truncated ? " — cut short" : ""}</div>
              <div className="lab-log" role="log">
                {shown.events.map((e, i) => (
                  <div key={i} className={`ev-${e.kind}`}>
                    {"  ".repeat(e.depth) + e.text}
                  </div>
                ))}
              </div>
            </div>
            <div className="lab-grow">
              <div className="dim">Answers, in the order found</div>
              <pre className="lab-log">{shown.answers.slice(0, 300).join("\n") || "none"}</pre>
            </div>
          </div>
        </>
      )}
    </>
  );
}
