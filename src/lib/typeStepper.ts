// Stepping a conditional type's evaluation (TS_MASTERY_ROADMAP M5-01).
//
// The playground already shows a type fully expanded. This shows HOW it got
// there, for `type X = F<Args>` where `F` is a conditional type alias:
//
//   1. the checked argument, split into its union members
//   2. for each member (when the conditional distributes): which branch it
//      takes, what every `infer` binds, and the member's result
//   3. the union of those results — the final type
//
// Nothing is evaluated here. This file only reads the source and writes probe
// declarations — helper aliases that ask one question each (`… ? true :
// false`, `… ? E : never`) — which the editor's own TypeScript service then
// answers, so the steps are the compiler's reasoning, not a model of it.

/** Skip a string or template literal starting at `i`; returns the index after it. */
function skipQuoted(s: string, i: number): number {
  const q = s[i];
  let j = i + 1;
  while (j < s.length && s[j] !== q) j += s[j] === "\\" ? 2 : 1;
  return j + 1;
}

/** Call `visit(i, depth)` for every character outside quotes, with the bracket
 * depth before it. `=>` is not a closing angle bracket. */
function scan(s: string, visit: (i: number, depth: number) => boolean | void): void {
  let depth = 0;
  for (let i = 0; i < s.length; ) {
    const c = s[i]!;
    if (c === '"' || c === "'" || c === "`") {
      i = skipQuoted(s, i);
      continue;
    }
    if (c === "=" && s[i + 1] === ">") {
      if (visit(i, depth) === true) return;
      i += 2;
      continue;
    }
    if (visit(i, depth) === true) return;
    if ("([{<".includes(c)) depth++;
    else if (")]}>".includes(c)) depth--;
    i++;
  }
}

/** Split `s` on `sep` (a single character) at bracket depth 0. */
export function splitTop(s: string, sep: string): string[] {
  const parts: string[] = [];
  let start = 0;
  scan(s, (i, depth) => {
    if (depth === 0 && s[i] === sep) {
      parts.push(s.slice(start, i));
      start = i + 1;
    }
  });
  parts.push(s.slice(start));
  return parts.map((p) => p.trim()).filter((p, _i, all) => p !== "" || all.length === 1);
}

/** The members of a union as the compiler prints it: `"a" | "b"` → ["\"a\"", "\"b\""].
 * `never` has none. A leading `|` (multi-line printing) is allowed. */
export function splitUnion(display: string): string[] {
  const t = display.trim().replace(/^\|\s*/, "");
  if (t === "never" || t === "") return [];
  return splitTop(t, "|");
}

export type Conditional = { check: string; ext: string; yes: string; no: string };

/** `A extends B ? C : D` at the top level of a type, or null. */
export function splitConditional(body: string): Conditional | null {
  let ext = -1;
  let q = -1;
  let colon = -1;
  let nested = 0;
  const src = body;
  scan(src, (i, depth) => {
    if (depth !== 0) return;
    if (ext < 0 && /\sextends\s/.test(src.slice(i - 1, i + 8)) && src.startsWith("extends", i)) {
      ext = i;
      return;
    }
    if (ext >= 0 && src[i] === "?") {
      if (q < 0) q = i;
      else nested++;
      return;
    }
    if (q >= 0 && src[i] === ":") {
      if (nested > 0) nested--;
      else if (colon < 0) {
        colon = i;
        return true;
      }
    }
  });
  if (ext < 0 || q < 0 || colon < 0) return null;
  return {
    check: src.slice(0, ext).trim(),
    ext: src.slice(ext + "extends".length, q).trim(),
    yes: src.slice(q + 1, colon).trim(),
    no: src.slice(colon + 1).trim(),
  };
}

/** The names bound by `infer` in an extends clause, in order. */
export function inferNames(ext: string): string[] {
  const out: string[] = [];
  for (const m of ext.matchAll(/\binfer\s+([A-Za-z_$][\w$]*)/g)) if (!out.includes(m[1]!)) out.push(m[1]!);
  return out;
}

export type GenericAlias = { name: string; paramsText: string; params: string[]; body: string };

/** Mask comments so declarations inside them are not found. */
function stripComments(src: string): string {
  return src.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " ")).replace(/\/\/[^\n]*/g, (m) => " ".repeat(m.length));
}

/** A top-level `type Name…= body;` — the body runs to the `;` at depth 0, or
 * to the next line that starts a new top-level statement. */
function topLevelTypes(src: string): { name: string; paramsText: string; body: string }[] {
  const code = stripComments(src);
  const out: { name: string; paramsText: string; body: string }[] = [];
  const re = /^(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*/gm;
  for (let m = re.exec(code); m; m = re.exec(code)) {
    let i = m.index + m[0].length;
    let paramsText = "";
    if (code[i] === "<") {
      let end = -1;
      scan(code.slice(i), (k, depth) => {
        if (code[i + k] === ">" && depth === 1) {
          end = i + k;
          return true;
        }
      });
      if (end < 0) continue;
      paramsText = code.slice(i + 1, end);
      i = end + 1;
    }
    const eq = code.indexOf("=", i);
    if (eq < 0 || code.slice(i, eq).trim() !== "") continue;
    const rest = code.slice(eq + 1);
    let stop = rest.length;
    scan(rest, (k, depth) => {
      if (depth === 0 && (rest[k] === ";" || (rest[k] === "\n" && /^\n(?:export\s+|type\s|interface\s|const\s|let\s|function\s|class\s|declare\s)/.test(rest.slice(k))))) {
        stop = k;
        return true;
      }
    });
    out.push({ name: m[1]!, paramsText, body: rest.slice(0, stop).trim() });
  }
  return out;
}

/** Generic type aliases whose body is a conditional type. */
export function conditionalAliases(src: string): Map<string, GenericAlias & { cond: Conditional }> {
  const out = new Map<string, GenericAlias & { cond: Conditional }>();
  for (const t of topLevelTypes(src)) {
    if (!t.paramsText) continue;
    const cond = splitConditional(t.body);
    if (!cond) continue;
    const params = splitTop(t.paramsText, ",").map((p) => p.trim().split(/[\s=]/)[0]!);
    out.set(t.name, { name: t.name, paramsText: t.paramsText, params, body: t.body, cond });
  }
  return out;
}

export type Application = { name: string; fn: string; args: string[] };

/** `type X = F<A, B>;` where F is one of `fns` — the applications to step. */
export function applications(src: string, fns: Set<string>): Application[] {
  const out: Application[] = [];
  for (const t of topLevelTypes(src)) {
    if (t.paramsText) continue;
    const m = /^([A-Za-z_$][\w$]*)\s*</.exec(t.body);
    if (!m || !fns.has(m[1]!) || !t.body.endsWith(">")) continue;
    const inner = t.body.slice(m[0].length, -1);
    out.push({ name: t.name, fn: m[1]!, args: splitTop(inner, ",") });
  }
  return out;
}

export type StepPlan = {
  app: Application;
  /** Index into `args` of the argument the conditional checks, when it distributes. */
  distributesOver: number | null;
  infers: string[];
  /** Helper aliases to append once per conditional alias. */
  helpers: string[];
  branchHelper: string;
  inferHelper: (name: string) => string;
};

/** How to step one application: which argument it distributes over (the
 * checked type is a bare type parameter), and the helper aliases that ask the
 * compiler "which branch?" and "what does `infer E` bind?". */
export function planSteps(app: Application, alias: GenericAlias & { cond: Conditional }, id: number): StepPlan {
  const idx = alias.params.indexOf(alias.cond.check);
  const branchHelper = `__PgBranch${id}`;
  const infers = inferNames(alias.cond.ext);
  const helpers = [
    `type ${branchHelper}<${alias.paramsText}> = ${alias.cond.check} extends ${alias.cond.ext} ? true : false;`,
    ...infers.map(
      (n) => `type __PgInfer${id}_${n}<${alias.paramsText}> = ${alias.cond.check} extends ${alias.cond.ext} ? ${n} : never;`
    ),
  ];
  return {
    app,
    distributesOver: idx >= 0 ? idx : null,
    infers,
    helpers,
    branchHelper,
    inferHelper: (n) => `__PgInfer${id}_${n}`,
  };
}

/** The arguments with the one at `idx` replaced by `member`. */
export function withArg(args: string[], idx: number, member: string): string {
  return args.map((a, i) => (i === idx ? member : a)).join(", ");
}
