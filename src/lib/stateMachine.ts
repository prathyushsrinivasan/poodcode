// State-machine diagrams for the playground (TS_MASTERY_ROADMAP M3-03).
//
// Weeks 10 and 12 model workflows as a union of states plus the moves between
// them. This finds such a machine in a source file and lists its edges, so the
// playground can draw it:
//
//   states  a type alias that is a union of two or more string literals
//           (`type Status = "draft" | "review" | "live"`)
//   edges   either a transition table — an object literal whose keys are
//           states and whose values mention states — or a `switch` over a
//           state whose cases `return` other states.
//
// It reads source text only; it is a picture of what the code says, and the
// type checker (not this) decides whether the code is right.

export type Machine = { name: string; states: string[]; edges: [string, string][]; via: "table" | "switch" };

function mask(src: string): string {
  return src.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " ")).replace(/\/\/[^\n]*/g, (m) => " ".repeat(m.length));
}

/** Unions of string literals: `type S = "a" | "b"` (leading `|` allowed). */
export function literalUnions(src: string): { name: string; states: string[] }[] {
  const out: { name: string; states: string[] }[] = [];
  const re = /^\s*(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*=\s*([^;]+);/gm;
  const code = mask(src);
  for (let m = re.exec(code); m; m = re.exec(code)) {
    const parts = m[2]!.split("|").map((p) => p.trim()).filter(Boolean);
    if (parts.length >= 2 && parts.every((p) => /^"[^"]*"$/.test(p))) {
      out.push({ name: m[1]!, states: parts.map((p) => p.slice(1, -1)) });
    }
  }
  return out;
}

/** The text of the `{ … }` block starting at `open`. */
function block(code: string, open: number): string {
  let depth = 0;
  for (let i = open; i < code.length; i++) {
    const c = code[i];
    if (c === '"' || c === "'" || c === "`") {
      i = code.indexOf(c, i + 1);
      if (i < 0) break;
      continue;
    }
    if (c === "{") depth++;
    else if (c === "}" && --depth === 0) return code.slice(open, i + 1);
  }
  return code.slice(open);
}

const literals = (text: string, states: Set<string>) =>
  [...text.matchAll(/"([^"\n]*)"/g)].map((m) => m[1]!).filter((s) => states.has(s));

/** Edges from transition tables: `{ draft: ["review"], review: ["draft", "live"] }`. */
function tableEdges(code: string, states: Set<string>): [string, string][] {
  const edges: [string, string][] = [];
  for (const m of code.matchAll(/=\s*\{/g)) {
    const body = block(code, m.index! + m[0].length - 1).slice(1, -1);
    const entries = [...body.matchAll(/(?:^|[,{\s])"?([A-Za-z_$][\w$-]*)"?\s*:\s*/g)];
    const keys = entries.map((e) => e[1]!);
    if (keys.length < 2 || !keys.every((k) => states.has(k))) continue;
    entries.forEach((e, i) => {
      const from = e[1]!;
      const end = i + 1 < entries.length ? entries[i + 1]!.index! : body.length;
      for (const to of literals(body.slice(e.index! + e[0].length, end), states)) edges.push([from, to]);
    });
  }
  return edges;
}

/** Edges from `switch` blocks whose cases are states and whose returns name states. */
function switchEdges(code: string, states: Set<string>): [string, string][] {
  const edges: [string, string][] = [];
  for (const m of code.matchAll(/switch\s*\([^)]*\)\s*\{/g)) {
    const body = block(code, m.index! + m[0].length - 1);
    const cases = [...body.matchAll(/case\s+"([^"]+)"\s*:/g)];
    let pending: string[] = [];
    cases.forEach((c, i) => {
      const label = c[1]!;
      if (!states.has(label)) return;
      const end = i + 1 < cases.length ? cases[i + 1]!.index! : body.length;
      const chunk = body.slice(c.index! + c[0].length, end);
      pending.push(label);
      // `case "a": case "b": return …` — fall-through labels share the returns.
      if (chunk.trim() === "") return;
      const targets = [...chunk.matchAll(/return\b([^;]*);/g)].flatMap((r) => literals(r[1]!, states));
      for (const from of pending) for (const to of targets) edges.push([from, to]);
      pending = [];
    });
  }
  return edges;
}

function dedupe(edges: [string, string][]): [string, string][] {
  const seen = new Set<string>();
  return edges.filter(([a, b]) => {
    const k = a + "\u0000" + b;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

/** Every state machine the file describes: a literal union with edges. */
export function findMachines(src: string): Machine[] {
  const code = mask(src);
  const out: Machine[] = [];
  for (const u of literalUnions(src)) {
    const states = new Set(u.states);
    const table = dedupe(tableEdges(code, states));
    const sw = table.length ? [] : dedupe(switchEdges(code, states));
    const edges = table.length ? table : sw;
    if (edges.length > 0) out.push({ name: u.name, states: u.states, edges, via: table.length ? "table" : "switch" });
  }
  return out;
}

/** States no edge leaves (terminal) and states the first state cannot reach. */
export function analyseMachine(m: Machine): { terminal: string[]; unreachable: string[] } {
  const out = new Map(m.states.map((s) => [s, [] as string[]]));
  for (const [a, b] of m.edges) out.get(a)?.push(b);
  const seen = new Set<string>([m.states[0]!]);
  const queue = [m.states[0]!];
  while (queue.length) for (const n of out.get(queue.shift()!) ?? []) if (!seen.has(n)) seen.add(n), queue.push(n);
  return {
    terminal: m.states.filter((s) => (out.get(s) ?? []).filter((t) => t !== s).length === 0),
    unreachable: m.states.filter((s) => !seen.has(s)),
  };
}
