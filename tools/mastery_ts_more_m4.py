# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery, Month 4 (weeks 14-17): problem sets, runnable projects,
# extra practice and review cards for the chapters in ts_chapters_m4.py.
#
# From week 14 everything runs under `strict+indexed` (TS_INDEXED_FROM_WEEK):
# every index read is `T | undefined`, so every solution here handles it.
# Expected outputs are computed (python tools/gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_SI = "strict+indexed"

# ===========================================================================
# Week 14 — The toolchain: tsconfig, modules, declarations, erasable syntax
# ===========================================================================

TS_PROBLEM_SETS[14] = [
    _tsp(14, "tsm-w14-lookup", "An honest lookup table", "warm-up",
         "The first line is `key=value` pairs separated by spaces (a later pair replaces an earlier one; a value may itself contain `=`). Each later line is a key to look up. Print `<key> -> <value>` or `missing <key>` — and an inherited name like `toString` is missing too. Finish with `keys: <k>`.",
         r"""
const [tableLine = "", ...queries] = input.split("\n");
const table: Record<string, string> = {};
for (const pair of tableLine.trim().split(/\s+/)) {
  const eq = pair.indexOf("=");
  if (eq > 0) table[pair.slice(0, eq)] = pair.slice(eq + 1);
}
for (const q of queries) {
  const key = q.trim();
  const value = Object.hasOwn(table, key) ? table[key] : undefined;
  console.log(value === undefined ? `missing ${key}` : `${key} -> ${value}`);
}
console.log(`keys: ${Object.keys(table).length}`);
""", ["a=1 b=2 a=3\na\nb\nc\ntoString", "k=v=w\nk\nK"],
         hints=["Under `noUncheckedIndexedAccess`, `table[key]` is `string | undefined` — the type now says what you already had to handle.",
                "`Object.hasOwn` rules out inherited names."]),
    _tsp(14, "tsm-w14-matrix", "Reads that may fall off the grid", "warm-up",
         "The input is a grid of integers (rows may have different lengths), a line `---`, then queries: `get r c`, `row r` (the row's sum) or `col c` (the column's sum — out of bounds if any row lacks that column). Print each answer or `out of bounds`.",
         r"""
const [gridPart = "", queryPart = ""] = input.split("\n---\n");
const grid = gridPart.split("\n").map((row) => row.trim().split(/\s+/).map(Number));
for (const q of queryPart.split("\n")) {
  const [kind = "", a = "", b = ""] = q.trim().split(/\s+/);
  if (kind === "get") {
    const v = grid[Number(a)]?.[Number(b)];
    console.log(v === undefined ? "out of bounds" : v);
  } else if (kind === "row") {
    const row = grid[Number(a)];
    console.log(row === undefined ? "out of bounds" : row.reduce((s, x) => s + x, 0));
  } else if (kind === "col") {
    const values = grid.map((row) => row[Number(b === "" ? a : b)]);
    const complete = values.every((v) => v !== undefined);
    console.log(complete ? values.reduce<number>((s, x) => s + (x ?? 0), 0) : "out of bounds");
  }
}
""", ["1 2 3\n4 5 6\n---\nget 0 2\nget 2 0\nget 1 -1\nrow 1\nrow 5\ncol 1\ncol 3",
      "7\n8 9\n---\ncol 0\ncol 1\nget 1 1"],
         hints=["`grid[r]?.[c]` stops at a missing row; the result is `number | undefined` either way.",
                "Check every value of a column before summing it."]),
    _tsp(14, "tsm-w14-esm-cjs", "ES module or CommonJS?", "warm-up",
         "Each input line is a file name, optionally followed by the package's `type` (`module` or `commonjs`, default `commonjs`). Apply Node's rule: `.mjs`/`.mts` are always ESM, `.cjs`/`.cts` always CommonJS, and `.js`/`.ts` follow the package type. Print `<file>: ESM`, `<file>: CJS` or `<file>: not a module file`, then `esm=<a> cjs=<b>`.",
         r"""
type Format = "ESM" | "CJS";
function formatOf(file: string, packageType: string): Format | undefined {
  const dot = file.lastIndexOf(".");
  const ext = dot < 0 ? "" : file.slice(dot);
  if (ext === ".mjs" || ext === ".mts") return "ESM";
  if (ext === ".cjs" || ext === ".cts") return "CJS";
  if (ext === ".js" || ext === ".ts") return packageType === "module" ? "ESM" : "CJS";
  return undefined;
}
const counts: Record<Format, number> = { ESM: 0, CJS: 0 };
for (const line of input.split("\n")) {
  const [file = "", type = "commonjs"] = line.trim().split(/\s+/);
  const format = formatOf(file, type);
  if (format === undefined) {
    console.log(`${file}: not a module file`);
  } else {
    counts[format]++;
    console.log(`${file}: ${format}`);
  }
}
console.log(`esm=${counts.ESM} cjs=${counts.CJS}`);
""", ["index.ts module\nutil.cjs module\nold.js\nlib.mts\nstyles.css", "a.cts\nb.js module\nREADME"],
         hints=["The explicit extensions win; only `.js` and `.ts` depend on the package."]),
    _tsp(14, "tsm-w14-env", "Parse a .env file", "core",
         "The input is a `.env` file. Blank lines and `#` comments are skipped; an optional `export ` prefix is ignored. Each other line must be `KEY=value` (a key is letters, digits and `_`, not starting with a digit; spaces around `=` are allowed). A value in `\"double\"` or `'single'` quotes is taken up to the matching quote (`line <n>: unterminated quote` if there is none); an unquoted value ends at ` #`. A later key replaces an earlier one. Print errors (`line <n>: expected KEY=value`) as they occur, then every variable sorted by key as `KEY=<value as JSON>`.",
         r"""
const vars = new Map<string, string>();
for (const [i, raw] of input.split("\n").entries()) {
  let line = raw.trim();
  if (line === "" || line.startsWith("#")) continue;
  if (line.startsWith("export ")) line = line.slice(7).trim();
  const m = /^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/.exec(line);
  if (m === null) {
    console.log(`line ${i + 1}: expected KEY=value`);
    continue;
  }
  const key = m[1] ?? "";
  let value = (m[2] ?? "").trim();
  const quote = value.charAt(0);
  if (quote === '"' || quote === "'") {
    const end = value.indexOf(quote, 1);
    if (end < 0) {
      console.log(`line ${i + 1}: unterminated quote`);
      continue;
    }
    value = value.slice(1, end);
  } else {
    const hash = value.indexOf(" #");
    if (hash >= 0) value = value.slice(0, hash).trim();
  }
  vars.set(key, value);
}
for (const [k, v] of [...vars].sort(([a], [b]) => a.localeCompare(b))) console.log(`${k}=${JSON.stringify(v)}`);
""", ["# settings\nexport PORT=8080\nNAME=\"Poodcode App\"  # quoted\nDEBUG=true # inline\nEMPTY=\nbad line\nPORT = 9090",
      "A='x # not a comment'\nB=\"open\n9X=1\n_ok=yes"],
         hints=["A regex with two groups splits the key from the value; `m[1]` and `m[2]` are `string | undefined` under this week's flag.",
                "Handle the quoted case first — a `#` inside quotes is part of the value."]),
    _tsp(14, "tsm-w14-flags", "Feature flags from one table", "core",
         "Plans are an enum-style object: `const Plan = { Free: \"free\", Pro: \"pro\", Team: \"team\" } as const`. Flags are rules in one object: `darkMode` (everyone), `export` (any paid plan), `sso` (team only), `newEditor` (users who opted into beta), `euBilling` (country `DE`, `FR` or `NL`). Each input line is `<name> <plan> <country> [beta]`. Print `<name>: <flags in declaration order>` or `<name>: unknown plan <p>`, then each flag with how many users have it.",
         r"""
const Plan = { Free: "free", Pro: "pro", Team: "team" } as const;
type Plan = (typeof Plan)[keyof typeof Plan];
type User = { name: string; plan: Plan; country: string; beta: boolean };
const FLAGS = {
  darkMode: () => true,
  export: (u: User) => u.plan !== Plan.Free,
  sso: (u: User) => u.plan === Plan.Team,
  newEditor: (u: User) => u.beta,
  euBilling: (u: User) => ["DE", "FR", "NL"].includes(u.country),
};
type Flag = keyof typeof FLAGS;
const flagNames = Object.keys(FLAGS) as Flag[];
const parsePlan = (s: string): Plan | undefined => Object.values(Plan).find((p) => p === s);
const counts = new Map<Flag, number>();
for (const line of input.split("\n")) {
  const [name = "", planText = "", country = "", beta = ""] = line.trim().split(/\s+/);
  const plan = parsePlan(planText);
  if (plan === undefined) {
    console.log(`${name}: unknown plan ${planText}`);
    continue;
  }
  const user: User = { name, plan, country, beta: beta === "beta" };
  const on = flagNames.filter((f) => {
    const rule: (u: User) => boolean = FLAGS[f];
    return rule(user);
  });
  for (const f of on) counts.set(f, (counts.get(f) ?? 0) + 1);
  console.log(`${name}: ${on.join(" ")}`);
}
for (const f of flagNames) console.log(`${f} ${counts.get(f) ?? 0}`);
""", ["ana free DE\nbo pro US beta\ncy team NL\ndee gold FR", "eve team JP beta"],
         hints=["`keyof typeof FLAGS` is the flag-name union; `Object.values(Plan)` is the list of valid plans.",
                "Store a rule in a variable typed `(u: User) => boolean` before calling it — `darkMode` takes no parameter, and that still fits."]),
    _tsp(14, "tsm-w14-merge", "Merge config patches", "core",
         "The first line is a JSON config; each later line is a JSON patch. Merge each patch into the running config: objects merge key by key (recursively), anything else — arrays included — replaces, and a `null` value deletes the key. Print the config after each patch as JSON with keys sorted at every level.",
         r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
function isObject(v: Json | undefined): v is { [key: string]: Json } {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}
function merge(base: Json, patch: Json): Json {
  if (!isObject(patch) || !isObject(base)) return patch;
  const out: { [key: string]: Json } = { ...base };
  for (const [k, v] of Object.entries(patch)) {
    if (v === null) delete out[k];
    else out[k] = merge(out[k] ?? null, v);
  }
  return out;
}
function sortKeys(v: Json): Json {
  if (Array.isArray(v)) return v.map(sortKeys);
  if (isObject(v)) return Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortKeys(v[k] ?? null)]));
  return v;
}
const [first = "null", ...patches] = input.split("\n");
let config: Json = JSON.parse(first);
for (const line of patches) {
  const patch: Json = JSON.parse(line);
  config = merge(config, patch);
  console.log(JSON.stringify(sortKeys(config)));
}
""", ['{"port":80,"db":{"host":"a","pool":5},"tags":["x"]}\n{"db":{"pool":10},"tags":["y","z"]}\n{"db":{"host":null},"debug":true}\n{"db":"sqlite"}',
      '{"a":1}\n{"b":{"c":{"d":1}}}\n{"b":{"c":{"e":2}}}\n5'],
         hints=["A recursive `Json` type describes any JSON value; narrow it with a type predicate `isObject`.",
                "Under this week's flag `out[k]` may be `undefined` — decide what merging into nothing means."]),
    _tsp(14, "tsm-w14-optional", "Missing, cleared or empty?", "core",
         "Each input line is a JSON record that should have a string `name` and may have `nickname`. Tell the cases apart — they mean different things, which is what `exactOptionalPropertyTypes` makes the compiler see: `<name>: no nickname field` (the key is absent), `<name>: nickname cleared` (`null`), `<name>: empty nickname` (`\"\"`), `<name>: nickname \"<n>\"`, or `<name>: bad nickname` (any other type). A record without a string `name` prints `bad record`.",
         r"""
for (const line of input.split("\n")) {
  const data: unknown = JSON.parse(line);
  if (typeof data !== "object" || data === null || !("name" in data) || typeof data.name !== "string") {
    console.log("bad record");
    continue;
  }
  let nick: string;
  if (!("nickname" in data)) nick = "no nickname field";
  else if (data.nickname === null) nick = "nickname cleared";
  else if (typeof data.nickname !== "string") nick = "bad nickname";
  else nick = data.nickname === "" ? "empty nickname" : `nickname "${data.nickname}"`;
  console.log(`${data.name}: ${nick}`);
}
""", ['{"name":"ana"}\n{"name":"bo","nickname":null}\n{"name":"cy","nickname":""}\n{"name":"dee","nickname":"D"}\n{"name":"eve","nickname":5}\n{"nick":"x"}'],
         hints=["`\"nickname\" in data` asks whether the key exists at all; `=== null` and `=== \"\"` ask about its value."]),
    _tsp(14, "tsm-w14-load-order", "Module load order", "stretch",
         "Each input line is `<file> imports <file…>` (possibly importing nothing). A module must load after everything it imports. Print a load order — visiting files alphabetically and each file's imports alphabetically, depth first — one file per line; or, if the imports form a cycle, only `cycle: <a> -> <b> -> … -> <a>` for the first cycle found that way.",
         r"""
const deps = new Map<string, string[]>();
for (const line of input.split("\n")) {
  const [file = "", , ...imports] = line.trim().split(/\s+/);
  deps.set(file, imports);
  for (const d of imports) if (!deps.has(d)) deps.set(d, []);
}
const state = new Map<string, "visiting" | "done">();
const order: string[] = [];
const stack: string[] = [];
function visit(f: string): string | undefined {
  const s = state.get(f);
  if (s === "done") return undefined;
  if (s === "visiting") return [...stack.slice(stack.indexOf(f)), f].join(" -> ");
  state.set(f, "visiting");
  stack.push(f);
  for (const d of [...(deps.get(f) ?? [])].sort()) {
    const cycle = visit(d);
    if (cycle !== undefined) return cycle;
  }
  stack.pop();
  state.set(f, "done");
  order.push(f);
  return undefined;
}
let cycle: string | undefined;
for (const f of [...deps.keys()].sort()) {
  cycle = visit(f);
  if (cycle !== undefined) break;
}
console.log(cycle === undefined ? order.join("\n") : `cycle: ${cycle}`);
""", ["main.ts imports app.ts util.ts\napp.ts imports util.ts db.ts\ndb.ts imports util.ts",
      "a.ts imports b.ts\nb.ts imports c.ts\nc.ts imports a.ts",
      "solo.ts imports",
      "x.ts imports y.ts\nw.ts imports x.ts z.ts\nz.ts imports"],
         hints=["Depth-first search with three states: unvisited, visiting (on the current path) and done.",
                "Reaching a `visiting` file again means a cycle; the path from it on the stack is the cycle."]),
    _tsp_types(14, "tsm-w14-declare-lib", "Declare an untyped library", "core",
               "`tiny-slug` ships no types. Write the declaration for its `slugify` function: it takes the text and optional options (`separator`, a string, and `lower`, a boolean — both optional) and returns a string.",
               '''
declare function slugify(text: string, options?: { separator?: string; lower?: boolean }): string;
declare const SLUG_VERSION: string;

const slug: string = slugify("Hello World", { separator: "_" });
const plain: string = slugify("Hi");
''', "(text: string, options?: { separator?: string; lower?: boolean }): string",
               '''
type _1 = Expect<Equal<Parameters<typeof slugify>, [text: string, options?: { separator?: string; lower?: boolean }]>>;
type _2 = Expect<Equal<ReturnType<typeof slugify>, string>>;
function _typeTests() {
  // @ts-expect-error — the text must be a string
  slugify(42);
  // @ts-expect-error — there is no `sep` option
  slugify("x", { sep: "-" });
}
''', hints=["A `declare function` is a signature with no body.", "The options object is optional as a whole, and so is each of its fields."]),
    _tsp_types(14, "tsm-w14-augment", "Augment a global type", "stretch",
               "Add a `last()` method to every array's type: it returns the last element, or `undefined` for an empty array. (Doing this for real is usually a bad idea — every array in the program changes — but it's how libraries add typings to globals.)",
               '''
declare global {
  interface Array<T> {
    last(): T | undefined;
  }
}
Array.prototype.last = function () {
  return this[this.length - 1];
};
''', "last(): T | undefined;",
               '''
type _1 = Expect<Equal<ReturnType<number[]["last"]>, number | undefined>>;
type _2 = Expect<Equal<ReturnType<string[]["last"]>, string | undefined>>;
''', hints=["Interfaces merge: declaring `interface Array<T>` again inside `declare global` adds members to the built-in one.",
            "The element type is the interface's own `T`."]),
]

TS_PROJECTS[14] = _project(
    14, "ledger.ts v4 — a strict bank statement",
    "The arc project's fourth version: the ledger read under every flag this month turns on. Money is integer cents in a branded type, every index read is honest under `noUncheckedIndexedAccess`, and bad rows are reported, never guessed at.",
    ["Each input line is a CSV row `date,account,amount,memo` — the memo is optional and may itself contain commas. Dates are `YYYY-MM-DD` and must exist on the calendar; amounts are like `12`, `-3.5` or `1200.75` (at most two decimals).",
     "For a bad row print `line <n>: bad date <d>`, `line <n>: missing account` or `line <n>: bad amount <a>` (checked in that order) and skip it.",
     "Then print each account, sorted, as `<account>: <balance> (<k> transactions)` (`transaction` for one), with balances to two decimals (`-4.50`).",
     "Then `total: <sum of all balances>`, `busiest month: <YYYY-MM> (<n> transactions)` (the earliest on a tie; `none` with no rows) and `largest expense: <memo, or the account if no memo> <amount>` (the most negative amount; `none` if nothing is negative).",
     "Keep amounts as a branded `Cents` type produced by one parser, never as floating-point dollars."],
    r"""
declare const CentsBrand: unique symbol;
type Cents = number & { readonly [CentsBrand]: true };
type Txn = { readonly date: string; readonly account: string; readonly amount: Cents; readonly memo: string };

function parseCents(text: string): Cents | undefined {
  const m = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(text.trim());
  if (m === null) return undefined;
  const cents = Number(m[2] ?? "0") * 100 + Number((m[3] ?? "").padEnd(2, "0"));
  return (m[1] === "-" ? -cents : cents) as Cents;
}
function isDate(s: string): boolean {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (m === null) return false;
  const [year, month, day] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const d = new Date(Date.UTC(year, month - 1, day));
  return d.getUTCMonth() === month - 1 && d.getUTCDate() === day;
}
const money = (c: number): string => (c < 0 ? "-" : "") + (Math.abs(c) / 100).toFixed(2);

const txns: Txn[] = [];
for (const [i, line] of input.split("\n").entries()) {
  const [date = "", account = "", amountText = "", ...memo] = line.split(",").map((s) => s.trim());
  if (!isDate(date)) {
    console.log(`line ${i + 1}: bad date ${date}`);
    continue;
  }
  if (account === "") {
    console.log(`line ${i + 1}: missing account`);
    continue;
  }
  const amount = parseCents(amountText);
  if (amount === undefined) {
    console.log(`line ${i + 1}: bad amount ${amountText}`);
    continue;
  }
  txns.push({ date, account, amount, memo: memo.join(", ") });
}

const byAccount = new Map<string, { balance: number; count: number }>();
for (const t of txns) {
  const acc = byAccount.get(t.account) ?? { balance: 0, count: 0 };
  byAccount.set(t.account, { balance: acc.balance + t.amount, count: acc.count + 1 });
}
for (const [name, acc] of [...byAccount].sort(([a], [b]) => a.localeCompare(b))) {
  console.log(`${name}: ${money(acc.balance)} (${acc.count} ${acc.count === 1 ? "transaction" : "transactions"})`);
}
console.log(`total: ${money(txns.reduce((s, t) => s + t.amount, 0))}`);

const months = new Map<string, number>();
for (const t of txns) months.set(t.date.slice(0, 7), (months.get(t.date.slice(0, 7)) ?? 0) + 1);
const busiest = [...months].sort(([a, x], [b, y]) => y - x || a.localeCompare(b))[0];
console.log(busiest === undefined ? "busiest month: none" : `busiest month: ${busiest[0]} (${busiest[1]} ${busiest[1] === 1 ? "transaction" : "transactions"})`);

const largest = txns.filter((t) => t.amount < 0).sort((a, b) => a.amount - b.amount)[0];
console.log(largest === undefined ? "largest expense: none" : `largest expense: ${largest.memo || largest.account} ${money(largest.amount)}`);
""", ["2026-01-05,checking,2500,salary\n2026-01-09,checking,-45.50,groceries\n2026-01-20,savings,500\n2026-02-01,checking,-1200,rent, February",
      "2026-02-30,checking,10\n,checking,5\n2026-03-01,,5\n2026-03-01,cash,5.555\n2026-03-02,cash,-0.5",
      "2025-12-31,a,1.1\n2026-01-01,b,-1.10,refund\n2026-01-02,a,-3,coffee",
      "bad",
      "2024-02-29,wallet,-20,leap day lunch\n2024-02-28,wallet,100\n2024-03-01,wallet,-20,book"],
    stretch=["Split it into modules — `money.ts`, `parse.ts`, `report.ts`, `main.ts` — with `import type` for the types.",
             "Write a `money.d.ts` describing a pretend untyped `currency-format` library, and format balances with it."],
)

TS_PRACTICE_MORE[14] = [
    _pr("tsm-w14-p2", "A record read under the flag",
        'const scores: Record<string, number> = { ana: 3 };\nconst s = scores["bo"];\n', "s", "number | undefined",
        strictness=_SI, why="This exercise is checked with `noUncheckedIndexedAccess` on.",
        hints=["A `Record<string, …>` might not have this key.", "The flag adds `undefined` to every index read."]),
    _dx("tsm-w14-d4", "A type-only import used as a value",
        "error TS1361: 'readFileSync' cannot be used as a value because it was imported using 'import type'.",
        'import type { readFileSync } from "fs";\nconst input = readFileSync(0, "utf8").trim();\nconsole.log(input.length);\n',
        'import { readFileSync } from "fs";\nconst input = readFileSync(0, "utf8").trim();\nconsole.log(input.length);\n',
        [("abc", "3"), ("hello", "5")], strictness=_SI,
        hints=["`import type` is deleted before the program runs.", "This import is a value — import it normally."]),
    _fx("tsm-w14-f1", "The element past the end",
        "Print the last word on the line, or `empty`. It always prints `empty`.",
        _STDIN + 'const words = input.split(" ").filter((w) => w !== "");\nconsole.log(words[words.length] ?? "empty");\n',
        _STDIN + 'const words = input.split(" ").filter((w) => w !== "");\nconsole.log(words.at(-1) ?? "empty");\n',
        [("a b c", "c"), ("", "empty"), ("solo", "solo")], strictness=_SI,
        hints=["Indexes run from 0 to `length - 1`.", "`words.at(-1)` reads the last element — and is honest about `undefined`."]),
]

TS_CARDS_MORE[14] = [
    ("What does type stripping do with `enum Color { Red }`?", "Refuses to run it: an `enum` generates an object, so it isn't erasable. Use an `as const` object plus a derived type."),
    ("`const Level = {…} as const; type Level = …` — how is the type written?", "`type Level = (typeof Level)[keyof typeof Level];` — the union of the object's values."),
    ("Why must type-only imports say `import type` under `verbatimModuleSyntax`?", "A stripper can't tell types from values, so the source must mark which imports to delete."),
    ("TypeScript 6.0's new default for `strict`?", "`true` — and `module` defaults to `esnext`, `types` to `[]`, `target` to the current ES year."),
    ("Name three options TypeScript 6.0 deprecated.", "Any of: `target: es5`, `moduleResolution: node`/`classic`, `baseUrl`, `outFile`, `module: amd/umd/systemjs/none`, `esModuleInterop: false`."),
    ("What is TypeScript 7.0?", "The compiler ported to Go (July 2026): same `tsc`, about 10× faster; the 6.0 deprecations are errors, and it ships no compiler API yet."),
]

# ===========================================================================
# Week 15 — Assertions, satisfies, structural typing, variance
# ===========================================================================

TS_PROBLEM_SETS[15] = [
    _tsp(15, "tsm-w15-routes", "Which route is this?", "warm-up",
         "A route table maps names to `{ method, path }` and is checked with `satisfies Record<string, Route>`: `home` GET `/`, `listUsers` GET `/users`, `createUser` POST `/users`, `logout` POST `/logout`. Each input line is `<METHOD> <path>`. Print the route's name, `405 method not allowed` if the path exists with other methods, or `404 not found`.",
         r"""
type Method = "GET" | "POST" | "DELETE";
type Route = { method: Method; path: string };
const routes = {
  home: { method: "GET", path: "/" },
  listUsers: { method: "GET", path: "/users" },
  createUser: { method: "POST", path: "/users" },
  logout: { method: "POST", path: "/logout" },
} satisfies Record<string, Route>;
type RouteName = keyof typeof routes;
const names = Object.keys(routes) as RouteName[];
for (const line of input.split("\n")) {
  const [method = "", path = ""] = line.trim().split(/\s+/);
  const name = names.find((n) => routes[n].method === method && routes[n].path === path);
  const samePath = names.some((n) => routes[n].path === path);
  console.log(name ?? (samePath ? "405 method not allowed" : "404 not found"));
}
""", ["GET /\nPOST /users\nGET /users\nDELETE /users\nGET /nope", "POST /logout\nGET /logout"],
         hints=["`satisfies` checks each route but keeps the object's own keys, so `keyof typeof routes` is the four names."]),
    _tsp(15, "tsm-w15-icons", "An icon registry", "warm-up",
         "Icons are registered as `{ glyph, size }` with `size` one of `16 | 24 | 32`, checked by `satisfies Record<string, Icon>`: `home` `⌂` 24, `star` `★` 16, `heart` `♥` 24, `check` `✓` 32. Each input line is `<name> [size]`. Print `<glyph> <name> <size>px` (the requested size, if it is a valid one, otherwise the icon's own), `bad size <s>` for any other size, or `no icon <name>` plus `; did you mean <n>?` when exactly one icon name starts with its first letter.",
         r"""
type Icon = { glyph: string; size: 16 | 24 | 32 };
const icons = {
  home: { glyph: "⌂", size: 24 },
  star: { glyph: "★", size: 16 },
  heart: { glyph: "♥", size: 24 },
  check: { glyph: "✓", size: 32 },
} satisfies Record<string, Icon>;
type IconName = keyof typeof icons;
const names = Object.keys(icons) as IconName[];
const isName = (s: string): s is IconName => Object.hasOwn(icons, s);
const SIZES: readonly number[] = [16, 24, 32];
for (const line of input.split("\n")) {
  const [name = "", sizeText] = line.trim().split(/\s+/);
  if (!isName(name)) {
    const guesses = names.filter((n) => n.startsWith(name.charAt(0)));
    const only = guesses.length === 1 ? guesses[0] : undefined;
    console.log(`no icon ${name}${only === undefined ? "" : `; did you mean ${only}?`}`);
    continue;
  }
  const icon = icons[name];
  if (sizeText !== undefined && !SIZES.includes(Number(sizeText))) {
    console.log(`bad size ${sizeText}`);
    continue;
  }
  console.log(`${icon.glyph} ${name} ${sizeText ?? icon.size}px`);
}
""", ["home\nstar 32\nheart 20\nhouse\nzap\nsun", "check\ncheck 16\nhart\ncheq"],
         hints=["A type predicate `isName` turns an input string into an `IconName`, after which `icons[name]` needs no `undefined` check."]),
    _tsp(15, "tsm-w15-shapes", "Which interfaces does it satisfy?", "warm-up",
         "Structural typing asks only what a value *has*. Each input line is JSON. Report which of these shapes it satisfies, in this order: `Named` (a string `name`), `Priced` (a number `price`), `Dated` (a string `date` that `Date.parse` accepts). Print `line <n>: <shapes>`, `line <n>: nothing` or `line <n>: not an object`, then how many lines satisfied each shape.",
         r"""
type Rec = Record<string, unknown>;
const SHAPES = {
  Named: (v: Rec) => typeof v["name"] === "string",
  Priced: (v: Rec) => typeof v["price"] === "number",
  Dated: (v: Rec) => {
    const d = v["date"];
    return typeof d === "string" && !Number.isNaN(Date.parse(d));
  },
} satisfies Record<string, (v: Rec) => boolean>;
type Shape = keyof typeof SHAPES;
const shapes = Object.keys(SHAPES) as Shape[];
const counts = new Map<Shape, number>();
for (const [i, line] of input.split("\n").entries()) {
  const data: unknown = JSON.parse(line);
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    console.log(`line ${i + 1}: not an object`);
    continue;
  }
  const rec = data as Rec;
  const fits = shapes.filter((s) => SHAPES[s](rec));
  for (const s of fits) counts.set(s, (counts.get(s) ?? 0) + 1);
  console.log(`line ${i + 1}: ${fits.join(" ") || "nothing"}`);
}
for (const s of shapes) console.log(`${s} ${counts.get(s) ?? 0}`);
""", ['{"name":"pen","price":2}\n{"date":"2026-01-02","name":"launch"}\n{"price":"2"}\n[1]\n{"date":"soon"}',
      '{"name":"x","price":1,"date":"2020-02-02","extra":true}'],
         hints=["A value satisfies a shape when it has the right members — extra members don't matter."]),
    _tsp(15, "tsm-w15-plugins", "A plugin pipeline", "core",
         "Text plugins are `{ order, run }` objects checked with `satisfies Record<string, Plugin>`: `trim` (0), `collapse` (1, runs of whitespace become one space), `upper` (2), `reverse` (3), `exclaim` (4, appends `!`). Each input line is `<plugin,plugin,…> | <text>`. Apply the named plugins in `order` (each once, however often it is named) and print `[<applied, in order>] <result>` — or `unknown plugin <name>` for the first unknown one.",
         r"""
type Plugin = { order: number; run: (text: string) => string };
const plugins = {
  trim: { order: 0, run: (t) => t.trim() },
  collapse: { order: 1, run: (t) => t.replace(/\s+/g, " ") },
  upper: { order: 2, run: (t) => t.toUpperCase() },
  reverse: { order: 3, run: (t) => [...t].reverse().join("") },
  exclaim: { order: 4, run: (t) => t + "!" },
} satisfies Record<string, Plugin>;
type PluginName = keyof typeof plugins;
const isPlugin = (s: string): s is PluginName => Object.hasOwn(plugins, s);
for (const line of input.split("\n")) {
  const bar = line.indexOf("|");
  const requested = line.slice(0, bar).split(",").map((s) => s.trim()).filter((s) => s !== "");
  const text = line.slice(bar + 1).replace(/^ /, "");
  const unknown = requested.find((p) => !isPlugin(p));
  if (unknown !== undefined) {
    console.log(`unknown plugin ${unknown}`);
    continue;
  }
  const chosen = [...new Set(requested.filter(isPlugin))].sort((a, b) => plugins[a].order - plugins[b].order);
  const result = chosen.reduce((t, p) => plugins[p].run(t), text);
  console.log(`[${chosen.join(",")}] ${result}`);
}
""", ["upper,trim |   hello   world  \nexclaim,reverse,collapse | a  b\nupper,shout | x\nupper,upper | twice"],
         hints=["`satisfies` gives each `run` its parameter type from `Plugin`, and keeps the keys for `PluginName`.",
                "Filter with the type predicate itself: `requested.filter(isPlugin)` is `PluginName[]`."]),
    _tsp(15, "tsm-w15-theme", "Resolve theme tokens", "core",
         "The input defines design tokens, one per line, as `<name> = <value>` where a value is a colour `#rgb`/`#rrggbb` or a reference `$<other>`; then a line `---`; then token names to resolve. Follow references to a colour and print `<name>: <#colour>`, or `<name>: unknown token <t>` (for the first unknown name met), or `<name>: cycle`. A malformed definition prints `bad definition <line>` while reading.",
         r"""
type TokenValue = { kind: "colour"; hex: string } | { kind: "ref"; name: string };
const [defs = "", queries = ""] = input.split("\n---\n");
const tokens = new Map<string, TokenValue>();
for (const line of defs.split("\n")) {
  const m = /^(\w+)\s*=\s*(#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?|\$\w+)$/.exec(line.trim());
  const name = m?.[1];
  const value = m?.[2];
  if (name === undefined || value === undefined) {
    console.log(`bad definition ${line.trim()}`);
    continue;
  }
  tokens.set(name, value.startsWith("#") ? { kind: "colour", hex: value.toLowerCase() } : { kind: "ref", name: value.slice(1) });
}
function resolve(name: string): string {
  const seen = new Set<string>();
  let current = name;
  for (;;) {
    if (seen.has(current)) return "cycle";
    seen.add(current);
    const t = tokens.get(current);
    if (t === undefined) return `unknown token ${current}`;
    if (t.kind === "colour") return t.hex;
    current = t.name;
  }
}
for (const q of queries.split("\n")) console.log(`${q.trim()}: ${resolve(q.trim())}`);
""", ["brand = #3355FF\nprimary = $brand\nbutton = $primary\nlink = $accent\nloop = $loop2\nloop2 = $loop\nbad = blue\n---\nbutton\nlink\nloop\nbrand\nnothing",
      "a = #abc\nb = $a\n---\nb"],
         hints=["A small discriminated union for a token's value makes the resolver a loop with two cases.",
                "Remember every name visited; seeing one again means a cycle."]),
    _tsp(15, "tsm-w15-form", "Validate a form against its schema", "core",
         "A sign-up form's fields are declared with `satisfies Record<string, Field>`: `name` (text, required, 2-20 characters), `age` (number, optional, 13-120), `email` (email, required), `bio` (text, optional, at most 40 characters). Each input line is a submitted JSON object. Print `ok`, or every problem in field order joined by `; ` — `<f>: required`, `<f>: must be text`, `<f>: must be a number`, `<f>: not an email`, `<f>: at least <n>` / `<f>: at most <n>` (characters for text, value for numbers) — followed by `unknown field <k>` for extra keys.",
         r"""
type Field = { type: "text" | "number" | "email"; required: boolean; min?: number; max?: number };
const signup = {
  name: { type: "text", required: true, min: 2, max: 20 },
  age: { type: "number", required: false, min: 13, max: 120 },
  email: { type: "email", required: true },
  bio: { type: "text", required: false, max: 40 },
} satisfies Record<string, Field>;
const fields: [string, Field][] = Object.entries(signup);
function check(name: string, field: Field, value: unknown): string | undefined {
  if (value === undefined || value === "") return field.required ? `${name}: required` : undefined;
  let size: number;
  if (field.type === "number") {
    if (typeof value !== "number") return `${name}: must be a number`;
    size = value;
  } else {
    if (typeof value !== "string") return `${name}: must be text`;
    if (field.type === "email" && !/^[^@\s]+@[^@\s]+\.\w+$/.test(value)) return `${name}: not an email`;
    size = value.length;
  }
  if (field.min !== undefined && size < field.min) return `${name}: at least ${field.min}`;
  if (field.max !== undefined && size > field.max) return `${name}: at most ${field.max}`;
  return undefined;
}
for (const line of input.split("\n")) {
  const data = JSON.parse(line) as Record<string, unknown>;
  const problems = fields.map(([name, field]) => check(name, field, data[name])).filter((p) => p !== undefined);
  for (const key of Object.keys(data)) if (!Object.hasOwn(signup, key)) problems.push(`unknown field ${key}`);
  console.log(problems.length === 0 ? "ok" : problems.join("; "));
}
""", ['{"name":"Ana","email":"ana@x.io"}\n{"name":"A","age":9,"email":"nope"}\n{"age":"30","bio":"' + "x" * 41 + '","role":"admin"}\n{"name":"Bo","email":"bo@y.dev","age":120,"bio":""}'],
         hints=["`satisfies` checks every field definition; to loop over them as `Field`s, annotate the entries: `[string, Field][]`.",
                "Missing and empty are the same case; decide it before checking the type."]),
    _tsp(15, "tsm-w15-endpoints", "Route requests to endpoints", "stretch",
         "Endpoints are declared with `satisfies Record<string, Endpoint>` where a path may have `:params`: `listUsers` GET `/users`, `getUser` GET `/users/:id`, `deleteUser` DELETE `/users/:id` (auth), `userPosts` GET `/users/:id/posts/:postId`, `createPost` POST `/posts` (auth). Each input line is `<METHOD> <path> [token]`. Print `<name> <param=value,…>` (or just the name without params), `401 <name>` for an auth endpoint called without a token, `405` if the path matches other methods only, or `404`.",
         r"""
type Endpoint = { method: "GET" | "POST" | "DELETE"; path: string; auth: boolean };
const endpoints = {
  listUsers: { method: "GET", path: "/users", auth: false },
  getUser: { method: "GET", path: "/users/:id", auth: false },
  deleteUser: { method: "DELETE", path: "/users/:id", auth: true },
  userPosts: { method: "GET", path: "/users/:id/posts/:postId", auth: false },
  createPost: { method: "POST", path: "/posts", auth: true },
} satisfies Record<string, Endpoint>;
type EndpointName = keyof typeof endpoints;
const names = Object.keys(endpoints) as EndpointName[];
function match(pattern: string, path: string): Map<string, string> | undefined {
  const want = pattern.split("/");
  const got = path.split("/");
  if (want.length !== got.length) return undefined;
  const params = new Map<string, string>();
  for (const [i, seg] of want.entries()) {
    const actual = got[i] ?? "";
    if (seg.startsWith(":")) {
      if (actual === "") return undefined;
      params.set(seg.slice(1), actual);
    } else if (seg !== actual) {
      return undefined;
    }
  }
  return params;
}
for (const line of input.split("\n")) {
  const [method = "", path = "", token] = line.trim().split(/\s+/);
  const hits = names.flatMap((n) => {
    const params = match(endpoints[n].path, path);
    return params === undefined ? [] : [{ name: n, params }];
  });
  const hit = hits.find((h) => endpoints[h.name].method === method);
  if (hit === undefined) {
    console.log(hits.length > 0 ? "405" : "404");
  } else if (endpoints[hit.name].auth && token === undefined) {
    console.log(`401 ${hit.name}`);
  } else {
    const params = [...hit.params].map(([k, v]) => `${k}=${v}`).join(",");
    console.log(params === "" ? hit.name : `${hit.name} ${params}`);
  }
}
""", ["GET /users\nGET /users/42\nDELETE /users/42\nDELETE /users/42 t0k\nGET /users/7/posts/3\nPUT /users/7\nPOST /posts abc\nGET /users//posts/1\nGET /teams"],
         hints=["Split both paths on `/` and compare segment by segment; a `:name` segment captures.",
                "Collect every endpoint whose path matches, then pick the one whose method matches — that's how 404 differs from 405."]),
    _tsp_types(15, "tsm-w15-palette", "Derive the palette's keys", "warm-up",
               "The palette is checked with `satisfies` (every value must be a `#` colour) and frozen with `as const`. Derive `PaletteKey`, the union of its colour names, from the object itself.",
               '''
const palette = {
  red: "#e5484d",
  green: "#30a46c",
  blue: "#0090ff",
} as const satisfies Record<string, `#${string}`>;
type PaletteKey = keyof typeof palette;
type PaletteHex = (typeof palette)[PaletteKey];
''', "keyof typeof palette",
               '''
type _1 = Expect<Equal<PaletteKey, "red" | "green" | "blue">>;
type _2 = Expect<Equal<PaletteHex, "#e5484d" | "#30a46c" | "#0090ff">>;
function _typeTests() {
  // @ts-expect-error — not a colour in the palette
  const k: PaletteKey = "pink";
}
''', hints=["`typeof palette` is the object's type; you want its keys.", "`keyof typeof palette`."]),
    _tsp_types(15, "tsm-w15-sink", "A sink that is really contravariant", "core",
               "A `Sink<T>` only accepts values. Declare its `put` member so that a sink of animals can be used as a sink of dogs, but not the other way round. (Careful: one of the two ways of writing a member is checked bivariantly.)",
               '''
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
interface Sink<in T> {
  put: (value: T) => void;
}
''', "put: (value: T) => void;",
               '''
declare const animalSink: Sink<Animal>;
declare const dogSink: Sink<Dog>;
const fine: Sink<Dog> = animalSink;
// @ts-expect-error — a dog sink cannot accept every animal
const unsafe: Sink<Animal> = dogSink;
type _1 = Expect<Equal<Parameters<Sink<Dog>["put"]>, [value: Dog]>>;
''', hints=["`put(value: T): void` is method syntax — bivariant, so the unsafe assignment would compile.",
            "Write it as a property with a function type: `put: (value: T) => void;`."]),
    _tsp_types(15, "tsm-w15-route-literals", "Keep the literal types", "stretch",
               "Finish the route table so that it is checked against `Route`, keeps its own keys, *and* keeps every value's literal type, read-only (`routes.login.method` is exactly `\"POST\"`).",
               '''
type Route = { method: "GET" | "POST"; path: string };
const routes = {
  home: { method: "GET", path: "/" },
  login: { method: "POST", path: "/login" },
} as const satisfies Record<string, Route>;
type RouteName = keyof typeof routes;
''', "as const satisfies Record<string, Route>",
               '''
type _1 = Expect<Equal<RouteName, "home" | "login">>;
type _2 = Expect<Equal<(typeof routes)["login"]["method"], "POST">>;
type _3 = Expect<Equal<(typeof routes)["home"], { readonly method: "GET"; readonly path: "/" }>>;
''', hints=["An annotation `: Record<string, Route>` would lose the keys; `satisfies` keeps them.",
            "`as const` first (literal, read-only values), then `satisfies` to check them."]),
]

TS_PROJECTS[15] = _project(
    15, "routes.ts — a typed route table with reverse routing",
    "Declare a route table once, with `satisfies`, and derive everything else from it: the route-name union, request matching with `:params`, and reverse routing — building a URL from a route's name — that rejects unknown names and missing parameters.",
    ["Routes: `home` GET `/`, `listTodos` GET `/todos`, `getTodo` GET `/todos/:id`, `createTodo` POST `/todos`, `updateTodo` PUT `/todos/:id`, `deleteTodo` DELETE `/todos/:id`, `todoComments` GET `/todos/:id/comments/:commentId`. Declare them `as const satisfies Record<string, Route>`.",
     "`match <METHOD> <path>`: ignore a `?query` and a trailing `/` (except on `/` itself). Print `<name>` plus ` <param=value,…>` when there are params; `405 allow <methods>` (the matching routes' methods, sorted, comma-separated) when only the method is wrong; `404` otherwise.",
     "`url <name> <param=value …>`: print the path with the params filled in, or `unknown route <name>`, `missing param <p>` (the first missing) or `unknown param <p>` (the first extra).",
     "`names` prints every route name, sorted, space-separated; `count` prints `<k> routes`.",
     "Keep one source of truth: the name union comes from `keyof typeof routes`, not from a list you typed."],
    r"""
type Method = "GET" | "POST" | "PUT" | "DELETE";
type Route = { method: Method; path: string };
const routes = {
  home: { method: "GET", path: "/" },
  listTodos: { method: "GET", path: "/todos" },
  getTodo: { method: "GET", path: "/todos/:id" },
  createTodo: { method: "POST", path: "/todos" },
  updateTodo: { method: "PUT", path: "/todos/:id" },
  deleteTodo: { method: "DELETE", path: "/todos/:id" },
  todoComments: { method: "GET", path: "/todos/:id/comments/:commentId" },
} as const satisfies Record<string, Route>;
type RouteName = keyof typeof routes;
const names = Object.keys(routes) as RouteName[];
const isRoute = (s: string): s is RouteName => Object.hasOwn(routes, s);

function match(pattern: string, path: string): [string, string][] | undefined {
  const want = pattern.split("/");
  const got = path.split("/");
  if (want.length !== got.length) return undefined;
  const params: [string, string][] = [];
  for (const [i, seg] of want.entries()) {
    const actual = got[i] ?? "";
    if (seg.startsWith(":")) {
      if (actual === "") return undefined;
      params.push([seg.slice(1), actual]);
    } else if (seg !== actual) {
      return undefined;
    }
  }
  return params;
}
function normalise(path: string): string {
  const bare = path.split("?")[0] ?? "";
  return bare.length > 1 && bare.endsWith("/") ? bare.slice(0, -1) : bare;
}
function buildUrl(name: string, args: string[]): string {
  if (!isRoute(name)) return `unknown route ${name}`;
  const given = new Map<string, string>();
  for (const arg of args) {
    const eq = arg.indexOf("=");
    given.set(arg.slice(0, eq), arg.slice(eq + 1));
  }
  const segments: string[] = routes[name].path.split("/");
  const wanted = segments.filter((s) => s.startsWith(":")).map((s) => s.slice(1));
  const missing = wanted.find((p) => !given.has(p));
  if (missing !== undefined) return `missing param ${missing}`;
  const extra = [...given.keys()].find((p) => !wanted.includes(p));
  if (extra !== undefined) return `unknown param ${extra}`;
  return segments.map((s) => (s.startsWith(":") ? given.get(s.slice(1)) ?? "" : s)).join("/") || "/";
}
for (const line of input.split("\n")) {
  const [cmd = "", a = "", ...rest] = line.trim().split(/\s+/);
  if (cmd === "match") {
    const path = normalise(rest[0] ?? "");
    const hits = names.flatMap((n) => {
      const params = match(routes[n].path, path);
      return params === undefined ? [] : [{ name: n, params }];
    });
    const hit = hits.find((h) => routes[h.name].method === a);
    if (hit !== undefined) {
      const params = hit.params.map(([k, v]) => `${k}=${v}`).join(",");
      console.log(params === "" ? hit.name : `${hit.name} ${params}`);
    } else if (hits.length > 0) {
      console.log(`405 allow ${[...new Set(hits.map((h) => routes[h.name].method))].sort().join(",")}`);
    } else {
      console.log("404");
    }
  } else if (cmd === "url") {
    console.log(buildUrl(a, rest));
  } else if (cmd === "names") {
    console.log([...names].sort().join(" "));
  } else if (cmd === "count") {
    console.log(`${names.length} routes`);
  }
}
""", ["match GET /todos/7\nmatch PATCH /todos/7\nmatch GET /todos/\nmatch GET /\nmatch GET /todos/7/comments/2?x=1\nmatch GET /users",
      "url getTodo id=5\nurl todoComments commentId=9 id=3\nurl home\nurl getTodo\nurl getTodo id=1 x=2\nurl nowhere id=1",
      "names\ncount",
      "match POST /todos\nmatch DELETE /todos\nmatch PUT /todos/abc/",
      "match GET //\nurl listTodos\nmatch DELETE /todos/1/comments/2"],
    stretch=["Type `url` so its parameters are checked at compile time: `url(\"getTodo\", { id: \"5\" })` — you'll have the tools in week 22 (template literal types).",
             "Add route groups (`/api/v1` prefixes) without repeating the prefix in every path."],
)

TS_PRACTICE_MORE[15] = [
    _pr("tsm-w15-p3", "An annotation widens", 'const cfg: { mode: string } = { mode: "dark" };\n', "cfg.mode", "string",
        strictness=_SI, hints=["An annotation replaces the inferred type.", "The declared type says `string`."]),
    _dx("tsm-w15-d2", "A value that doesn't satisfy",
        "error TS2322: Type 'string' is not assignable to type 'number'.",
        'const server = { host: "localhost", port: "8080" } satisfies { host: string; port: number };\nconsole.log(server.port + 1);\n',
        'const server = { host: "localhost", port: 8080 } satisfies { host: string; port: number };\nconsole.log(server.port + 1);\n',
        [("", "8081")], strictness=_SI, ask="The port is a number.",
        hints=["`satisfies` reports the mismatching property itself.", "Write the port as a number literal."]),
    _fx("tsm-w15-f2", "A narrower type that kept its secret",
        "Print a user's public profile as JSON: only `name` and `city`. The password is printed too.",
        _STDIN + 'type Public = { name: string; city: string };\nconst user = { ...(JSON.parse(input) as Public), password: "hunter2" };\nconst profile: Public = user;\nconsole.log(JSON.stringify(profile));\n',
        _STDIN + 'type Public = { name: string; city: string };\nconst user = { ...(JSON.parse(input) as Public), password: "hunter2" };\nconst profile: Public = { name: user.name, city: user.city };\nconsole.log(JSON.stringify(profile));\n',
        [('{"name":"ana","city":"Oslo"}', '{"name":"ana","city":"Oslo"}'), ('{"city":"Rome","name":"bo"}', '{"name":"bo","city":"Rome"}')],
        strictness=_SI, hints=["Structural typing lets a bigger object through; the annotation removes nothing.", "Build the smaller object explicitly."]),
]

TS_CARDS_MORE[15] = [
    ("Covariant, contravariant, invariant — in one line each?", "Producers keep the subtype direction; consumers reverse it; things that do both need an exact match."),
    ("Is `Dog[]` assignable to `Animal[]`? Is that safe?", "Yes, and no: arrays are covariant for convenience, but the receiver can push a non-dog. `readonly Animal[]` is the safe version."),
    ("`(a: Animal) => void` vs `(d: Dog) => void` — which fits where the other is expected?", "The `Animal` handler fits a `Dog` slot, not the reverse (parameters are contravariant)."),
    ("What does `interface Source<out T>` promise?", "`T` only comes out of a `Source`; the compiler checks the body and rejects members that take a `T` in."),
    ("Why does `interface Box<out T> { set(v: T): void }` compile?", "Method syntax is bivariant, so the check misses it; `set: (v: T) => void` is caught (TS2636)."),
    ("How do you make an object property safe to widen?", "Mark it `readonly` in the wider type, so nothing can write a supertype value through it."),
]

# ===========================================================================
# Week 16 — Branded types, immutability, parse don't validate
# ===========================================================================

TS_PROBLEM_SETS[16] = [
    _tsp(16, "tsm-w16-money", "Money in branded cents", "warm-up",
         "Each input line is a money command: `add <a> <b>`, `sub <a> <b>`, `mul <a> <factor>` (rounded to the nearest cent) or `split <a> <n>` (into n parts that differ by at most a cent, the larger parts first). Amounts look like `12`, `-3.5` or `0.99`. Parse them once into a branded `Cents` type and print results like `$12.34` / `-$0.50` (a split prints its parts space-separated). Errors: `bad amount <x>`, `bad count <n>` (n must be a whole number ≥ 1), `cannot split a negative amount`, `unknown command <c>`.",
         r"""
declare const CentsBrand: unique symbol;
type Cents = number & { readonly [CentsBrand]: true };
function parseMoney(text: string): Cents | undefined {
  const m = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(text);
  if (m === null) return undefined;
  const cents = Number(m[2] ?? "0") * 100 + Number((m[3] ?? "").padEnd(2, "0"));
  return (m[1] === "-" ? -cents : cents) as Cents;
}
const show = (c: Cents): string => (c < 0 ? "-" : "") + "$" + (Math.abs(c) / 100).toFixed(2);
const add = (a: Cents, b: Cents): Cents => (a + b) as Cents;
const scale = (a: Cents, factor: number): Cents => Math.round(a * factor) as Cents;
function split(total: Cents, n: number): Cents[] {
  const base = Math.floor(total / n);
  const extra = total - base * n;
  return Array.from({ length: n }, (_, i) => (base + (i < extra ? 1 : 0)) as Cents);
}
for (const line of input.split("\n")) {
  const [cmd = "", x = "", y = ""] = line.trim().split(/\s+/);
  const a = parseMoney(x);
  if (a === undefined) {
    console.log(`bad amount ${x}`);
    continue;
  }
  if (cmd === "add" || cmd === "sub") {
    const b = parseMoney(y);
    if (b === undefined) console.log(`bad amount ${y}`);
    else console.log(show(add(a, cmd === "add" ? b : ((-b) as Cents))));
  } else if (cmd === "mul") {
    const f = Number(y);
    console.log(y === "" || !Number.isFinite(f) ? `bad amount ${y}` : show(scale(a, f)));
  } else if (cmd === "split") {
    const n = Number(y);
    if (!Number.isInteger(n) || n < 1) console.log(`bad count ${y}`);
    else if (a < 0) console.log("cannot split a negative amount");
    else console.log(split(a, n).map(show).join(" "));
  } else {
    console.log(`unknown command ${cmd}`);
  }
}
""", ["add 0.10 0.20\nsub 5 7.5\nmul 19.99 3\nmul 10 0.175\nsplit 10 3\nsplit 0.05 2", "add 1.234 1\nsplit -3 2\nsplit 1 0\ndiv 1 2\nmul 2 x"],
         hints=["Integer cents make `0.10 + 0.20` exactly `0.30`.",
                "A split gives everyone `floor(total / n)` and hands out the remaining cents one each."]),
    _tsp(16, "tsm-w16-percent", "A percentage that can't be out of range", "warm-up",
         "Each input line is `<price> <discount>`, the discount written like `15%` or `12.5%`. Parse the discount into a branded `Percent` (0-100, at most one decimal) and the price into cents, then print `<price> - <p>% = <final>` with money as `$x.yy` and the final price rounded to the nearest cent. Errors: `bad price <x>`, `bad percent <x>`, `percent out of range <x>`.",
         r"""
declare const PercentBrand: unique symbol;
type Percent = number & { readonly [PercentBrand]: true };
function parsePercent(text: string): Percent | "bad" | "range" {
  const m = /^(\d+(?:\.\d)?)%$/.exec(text);
  if (m === null) return "bad";
  const p = Number(m[1]);
  return p <= 100 ? (p as Percent) : "range";
}
function parseCents(text: string): number | undefined {
  return /^\d+(\.\d{1,2})?$/.test(text) ? Math.round(Number(text) * 100) : undefined;
}
const money = (c: number) => "$" + (c / 100).toFixed(2);
for (const line of input.split("\n")) {
  const [priceText = "", pctText = ""] = line.trim().split(/\s+/);
  const price = parseCents(priceText);
  const pct = parsePercent(pctText);
  if (price === undefined) console.log(`bad price ${priceText}`);
  else if (pct === "bad") console.log(`bad percent ${pctText}`);
  else if (pct === "range") console.log(`percent out of range ${pctText}`);
  else console.log(`${money(price)} - ${pct}% = ${money(Math.round((price * (100 - pct)) / 100))}`);
}
""", ["80 15%\n19.99 12.5%\n10 100%\n5 0%", "10 150%\n10 15\nx 5%\n9.99 33.33%"],
         hints=["Return the reason alongside the branded value — `Percent | \"bad\" | \"range\"` — and narrow on the two reasons."]),
    _tsp(16, "tsm-w16-emails", "Canonical email addresses", "warm-up",
         "Each input line is an email address as someone typed it. Parse it into a branded `Email`: trim, lower-case, exactly one `@`, a non-empty local part and a domain containing a dot. Print `rejected <input, trimmed>` for bad ones as you go; then every distinct valid address, sorted; then each domain with its count, most first (ties alphabetically).",
         r"""
declare const EmailBrand: unique symbol;
type Email = string & { readonly [EmailBrand]: true };
function parseEmail(raw: string): Email | undefined {
  const s = raw.trim().toLowerCase();
  const parts = s.split("@");
  const [local = "", domain = ""] = parts;
  return parts.length === 2 && local !== "" && /^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(domain) ? (s as Email) : undefined;
}
const emails = new Set<Email>();
for (const line of input.split("\n")) {
  const email = parseEmail(line);
  if (email === undefined) console.log(`rejected ${line.trim()}`);
  else emails.add(email);
}
const sorted = [...emails].sort();
for (const e of sorted) console.log(e);
const domains = new Map<string, number>();
for (const e of sorted) {
  const domain = e.slice(e.indexOf("@") + 1);
  domains.set(domain, (domains.get(domain) ?? 0) + 1);
}
for (const [d, n] of [...domains].sort(([a, x], [b, y]) => y - x || a.localeCompare(b))) console.log(`${d} ${n}`);
""", ["Ana@Example.com\n ana@example.com \nbo@mail.io\ncy@@x.io\n@x.io\ndee@localhost\nEVE@MAIL.IO"],
         hints=["Normalising is part of parsing: after it, equal addresses are equal strings, so a `Set` dedupes them."]),
    _tsp(16, "tsm-w16-cart", "An immutable cart with undo", "core",
         "Commands, one per line: `add <sku> <qty> <price>` (adds to an existing line's quantity, keeping its first price), `remove <sku>`, `qty <sku> <n>` (0 removes the line), `undo`, `show`. Every change must build a *new* cart (a `readonly` array of `readonly` lines) and remember the previous one; `undo` goes back one change (`nothing to undo`). `remove`/`qty` on a missing sku print `no <sku>` and change nothing. `show` prints each line as `<sku> x<qty> = <line total>` and then `total <sum>` (money with two decimals), or `(empty)`. Finally print `changes kept: <k>`.",
         r"""
type Line = { readonly sku: string; readonly qty: number; readonly price: number };
type Cart = readonly Line[];
let cart: Cart = [];
const history: Cart[] = [];
function commit(next: Cart): void {
  history.push(cart);
  cart = next;
}
const money = (n: number) => n.toFixed(2);
for (const raw of input.split("\n")) {
  const [cmd = "", sku = "", a = "", b = ""] = raw.trim().split(/\s+/);
  const index = cart.findIndex((l) => l.sku === sku);
  const line = cart[index];
  if (cmd === "add") {
    const qty = Number(a);
    commit(line === undefined ? [...cart, { sku, qty, price: Number(b) }] : cart.with(index, { ...line, qty: line.qty + qty }));
  } else if (cmd === "remove" || cmd === "qty") {
    if (line === undefined) {
      console.log(`no ${sku}`);
      continue;
    }
    const n = cmd === "remove" ? 0 : Number(a);
    commit(n === 0 ? cart.toSpliced(index, 1) : cart.with(index, { ...line, qty: n }));
  } else if (cmd === "undo") {
    const previous = history.pop();
    if (previous === undefined) console.log("nothing to undo");
    else cart = previous;
  } else if (cmd === "show") {
    if (cart.length === 0) console.log("(empty)");
    for (const l of cart) console.log(`${l.sku} x${l.qty} = ${money(l.qty * l.price)}`);
    if (cart.length > 0) console.log(`total ${money(cart.reduce((s, l) => s + l.qty * l.price, 0))}`);
  }
}
console.log(`changes kept: ${history.length}`);
""", ["add pen 2 1.50\nadd cup 1 4\nadd pen 1 9\nshow\nqty cup 3\nremove pen\nshow\nundo\nundo\nshow",
      "undo\nremove ink\nshow\nadd ink 1 2.25\nqty ink 0\nshow\nundo\nshow"],
         hints=["`with(i, v)` and `toSpliced(i, 1)` return new arrays — the old cart is untouched, so it can go in the history.",
                "Under `noUncheckedIndexedAccess`, `cart[index]` is `Line | undefined`; that check doubles as \"is the sku in the cart?\"."]),
    _tsp(16, "tsm-w16-versions", "A persistent stack", "core",
         "A persistent stack never changes: `push` and `pop` make a new version that shares the old nodes. Version 0 is empty. Commands: `push <v>` and `pop` (from the current version; print `v<k>: <values top first>` for the new version k, or `v<k>: (empty)`; popping an empty stack prints `empty`), `checkout <k>` (make version k current; `no version <k>`), `print` (the current version). Finish with `versions <n>, nodes <m>` — how many versions exist and how many nodes were ever created.",
         r"""
type Node = { readonly value: string; readonly next: Node | undefined };
const versions: (Node | undefined)[] = [undefined];
let current = 0;
let nodes = 0;
const show = (head: Node | undefined): string => {
  const values: string[] = [];
  for (let n = head; n !== undefined; n = n.next) values.push(n.value);
  return values.join(" ") || "(empty)";
};
function publish(head: Node | undefined): void {
  versions.push(head);
  current = versions.length - 1;
  console.log(`v${current}: ${show(head)}`);
}
for (const line of input.split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  const head = versions[current];
  if (cmd === "push") {
    nodes++;
    publish({ value: arg, next: head });
  } else if (cmd === "pop") {
    if (head === undefined) console.log("empty");
    else publish(head.next);
  } else if (cmd === "checkout") {
    const k = Number(arg);
    if (Number.isInteger(k) && k >= 0 && k < versions.length) current = k;
    else console.log(`no version ${arg}`);
  } else if (cmd === "print") {
    console.log(show(head));
  }
}
console.log(`versions ${versions.length}, nodes ${nodes}`);
""", ["push a\npush b\npush c\ncheckout 1\npush x\nprint\ncheckout 3\npop\npop\npop\npop\ncheckout 9",
      "pop\npush 1\ncheckout 0\nprint\npush 2"],
         hints=["A push creates exactly one node whose `next` is the old head — the rest of the list is shared, not copied.",
                "Keep every version's head in an array; checking out is just picking an index."]),
    _tsp(16, "tsm-w16-deep-equal", "Where do they differ?", "core",
         "The input is pairs of lines, each line a JSON value. For each pair print `equal`, or the first difference as `<path>: <left> vs <right>`, with values as JSON and `missing` for an absent key or index. Paths start at `$`, then `.key` and `[i]`. Compare objects by their keys in sorted order (a key in either side), arrays index by index; values of different kinds differ at that path.",
         r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
const isObject = (v: Json): v is { [key: string]: Json } => typeof v === "object" && v !== null && !Array.isArray(v);
const show = (v: Json | undefined) => (v === undefined ? "missing" : JSON.stringify(v));
function diff(a: Json | undefined, b: Json | undefined, path: string): string | undefined {
  if (a === undefined || b === undefined) return a === b ? undefined : `${path}: ${show(a)} vs ${show(b)}`;
  if (Array.isArray(a) && Array.isArray(b)) {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const d = diff(a[i], b[i], `${path}[${i}]`);
      if (d !== undefined) return d;
    }
    return undefined;
  }
  if (isObject(a) && isObject(b)) {
    for (const k of [...new Set([...Object.keys(a), ...Object.keys(b)])].sort()) {
      const d = diff(a[k], b[k], `${path}.${k}`);
      if (d !== undefined) return d;
    }
    return undefined;
  }
  return JSON.stringify(a) === JSON.stringify(b) ? undefined : `${path}: ${show(a)} vs ${show(b)}`;
}
const lines = input.split("\n");
for (let i = 0; i + 1 < lines.length; i += 2) {
  const left: Json = JSON.parse(lines[i] ?? "null");
  const right: Json = JSON.parse(lines[i + 1] ?? "null");
  console.log(diff(left, right, "$") ?? "equal");
}
""", ['{"a":1,"b":[1,2]}\n{"b":[1,2],"a":1}\n{"a":{"x":[1,{"y":2}]}}\n{"a":{"x":[1,{"y":3}]}}\n[1,2,3]\n[1,2]\n{"k":1}\n{"j":1}',
      '5\n"5"\nnull\nnull\n{"a":[]}\n{"a":{}}'],
         hints=["Recursion over a `Json` union: arrays, objects, and everything else compared directly.",
                "Under `noUncheckedIndexedAccess`, `a[i]` and `a[k]` are already `Json | undefined` — which is exactly the \"missing\" case."]),
    _tsp(16, "tsm-w16-time-travel", "A counter with time travel", "stretch",
         "A counter starts at 0. Commands: `inc <n>`, `dec <n>`, `set <n>` (each prints the new value), `snapshot <name>` (prints `saved <name>`), `restore <name>` (the value when saved — it counts as a change and prints the value; `no snapshot <name>`), `back <k>` (undo the last k changes — or all of them — and print the value), `history` (every value from the start to now, space-separated). Keep the history as an immutable list of states: each change appends, and `back` returns to an earlier prefix.",
         r"""
type State = { readonly value: number; readonly cause: string };
let history: readonly State[] = [{ value: 0, cause: "start" }];
const snapshots = new Map<string, number>();
const now = (): number => history.at(-1)?.value ?? 0;
function change(value: number, cause: string): void {
  history = [...history, { value, cause }];
  console.log(value);
}
for (const line of input.split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  const n = Number(arg);
  if (cmd === "inc") change(now() + n, line);
  else if (cmd === "dec") change(now() - n, line);
  else if (cmd === "set") change(n, line);
  else if (cmd === "snapshot") {
    snapshots.set(arg, now());
    console.log(`saved ${arg}`);
  } else if (cmd === "restore") {
    const saved = snapshots.get(arg);
    if (saved === undefined) console.log(`no snapshot ${arg}`);
    else change(saved, line);
  } else if (cmd === "back") {
    history = history.slice(0, Math.max(1, history.length - n));
    console.log(now());
  } else if (cmd === "history") {
    console.log(history.map((s) => s.value).join(" "));
  }
}
""", ["inc 5\ninc 3\nsnapshot mid\ndec 10\nhistory\nback 1\nrestore mid\nrestore end\nset 42\nback 99\nhistory"],
         hints=["`back` never mutates: `history.slice(0, …)` is a new, shorter list.", "Keep the start state, so going back further than the beginning stops at 0."]),
    _tsp_types(16, "tsm-w16-id-brands", "Ids that can't be mixed up", "core",
               "`UserId` is a branded string. Declare `OrderId` the same way with its own brand, so that a user id can't be used as an order id (or a plain string as either) — but an order id can still be used as a string.",
               '''
declare const UserIdBrand: unique symbol;
declare const OrderIdBrand: unique symbol;
type UserId = string & { readonly [UserIdBrand]: true };
type OrderId = string & { readonly [OrderIdBrand]: true };
''', "string & { readonly [OrderIdBrand]: true }",
               '''
declare const u: UserId;
declare const o: OrderId;
const asText: string = o;
function _typeTests() {
  // @ts-expect-error — a user id is not an order id
  const mixed: OrderId = u;
  // @ts-expect-error — a plain string is not an order id
  const raw: OrderId = "O-1001";
}
''', hints=["Intersect `string` with an object type whose only property is keyed by `OrderIdBrand`.",
            "Each brand needs its own symbol, or the two types would be the same."]),
    _tsp_types(16, "tsm-w16-tags", "A tag list that is never empty", "core",
               "Declare `Tags`: a read-only list of strings with at least one element, so an empty list is rejected, the first tag is a plain `string` (no `undefined`, even under `noUncheckedIndexedAccess`), and nothing can push onto it.",
               '''
type Tags = readonly [string, ...string[]];
const one: Tags = ["urgent"];
const many: Tags = ["a", "b", "c"];
''', "readonly [string, ...string[]]",
               '''
type _1 = Expect<Equal<Tags[0], string>>;
function _typeTests(t: Tags) {
  // @ts-expect-error — at least one tag
  const none: Tags = [];
  // @ts-expect-error — tags are read-only
  t.push("x");
}
''', hints=["A tuple with a fixed first element and a rest element.", "Prefix it with `readonly`."]),
]

TS_PROJECTS[16] = _project(
    16, "ids.ts — branded ids and a read-only store",
    "Parse users and orders into branded `UserId`/`OrderId` values and integer cents, reject every bad row, and answer queries from a store that callers cannot mutate. A user id where an order id belongs is a compile error — and, from the query input, a clear message.",
    ["The input has three sections separated by lines containing only `---`: users (`<userId> <name>`), orders (`<orderId> <userId> <amount>`), queries.",
     "A `UserId` is `U-` and three digits; an `OrderId` is `O-` and four; an amount has at most two decimals. Report bad rows as they are read: `bad user line: <line>`, `bad order line: <line>`, `duplicate id <id>`, `order <id>: unknown user <userId>`.",
     "Queries: `user <id>` → `<name>: <k> orders, $<total>` (`order` for one); `order <id>` → `<id> by <name>: $<amount>`; `top` → the user with the highest total, `<name> $<total>` (earliest id on a tie; `none` if no orders). A missing id prints `no user <id>` / `no order <id>`; an id of the wrong kind or format prints `not a user id <x>` / `not an order id <x>`.",
     "Store users and orders in `ReadonlyMap`s keyed by the branded ids, built once and never changed afterwards.",
     "Money is printed with two decimals."],
    r"""
declare const UserIdBrand: unique symbol;
declare const OrderIdBrand: unique symbol;
type UserId = string & { readonly [UserIdBrand]: true };
type OrderId = string & { readonly [OrderIdBrand]: true };
type User = { readonly id: UserId; readonly name: string };
type Order = { readonly id: OrderId; readonly user: UserId; readonly cents: number };

const parseUserId = (s: string): UserId | undefined => (/^U-\d{3}$/.test(s) ? (s as UserId) : undefined);
const parseOrderId = (s: string): OrderId | undefined => (/^O-\d{4}$/.test(s) ? (s as OrderId) : undefined);
const parseCents = (s: string): number | undefined => (/^\d+(\.\d{1,2})?$/.test(s) ? Math.round(Number(s) * 100) : undefined);
const money = (c: number) => "$" + (c / 100).toFixed(2);

const sections: string[][] = [[]];
for (const line of input.split("\n")) {
  if (line.trim() === "---") sections.push([]);
  else if (line.trim() !== "") sections.at(-1)?.push(line);
}
const [userLines = [], orderLines = [], queryLines = []] = sections;
const userMap = new Map<UserId, User>();
for (const line of userLines) {
  const [idText = "", ...name] = line.trim().split(/\s+/);
  const id = parseUserId(idText);
  if (id === undefined || name.length === 0) console.log(`bad user line: ${line.trim()}`);
  else if (userMap.has(id)) console.log(`duplicate id ${id}`);
  else userMap.set(id, { id, name: name.join(" ") });
}
const orderMap = new Map<OrderId, Order>();
for (const line of orderLines) {
  const [idText = "", userText = "", amountText = ""] = line.trim().split(/\s+/);
  const id = parseOrderId(idText);
  const user = parseUserId(userText);
  const cents = parseCents(amountText);
  if (id === undefined || user === undefined || cents === undefined) console.log(`bad order line: ${line.trim()}`);
  else if (orderMap.has(id)) console.log(`duplicate id ${id}`);
  else if (!userMap.has(user)) console.log(`order ${id}: unknown user ${user}`);
  else orderMap.set(id, { id, user, cents });
}
const users: ReadonlyMap<UserId, User> = userMap;
const orders: ReadonlyMap<OrderId, Order> = orderMap;
const ordersOf = (u: UserId) => [...orders.values()].filter((o) => o.user === u);
const totalOf = (u: UserId) => ordersOf(u).reduce((s, o) => s + o.cents, 0);

for (const q of queryLines) {
  const [cmd = "", arg = ""] = q.trim().split(/\s+/);
  if (cmd === "user") {
    const id = parseUserId(arg);
    const user = id === undefined ? undefined : users.get(id);
    if (id === undefined) console.log(`not a user id ${arg}`);
    else if (user === undefined) console.log(`no user ${id}`);
    else {
      const n = ordersOf(id).length;
      console.log(`${user.name}: ${n} ${n === 1 ? "order" : "orders"}, ${money(totalOf(id))}`);
    }
  } else if (cmd === "order") {
    const id = parseOrderId(arg);
    const order = id === undefined ? undefined : orders.get(id);
    if (id === undefined) console.log(`not an order id ${arg}`);
    else if (order === undefined) console.log(`no order ${id}`);
    else console.log(`${id} by ${users.get(order.user)?.name ?? "?"}: ${money(order.cents)}`);
  } else if (cmd === "top") {
    const ranked = [...users.keys()].filter((u) => ordersOf(u).length > 0)
      .sort((a, b) => totalOf(b) - totalOf(a) || a.localeCompare(b));
    const best = ranked[0];
    console.log(best === undefined ? "none" : `${users.get(best)?.name ?? "?"} ${money(totalOf(best))}`);
  }
}
""", ["U-001 ana\nU-002 bo lee\n---\nO-1001 U-001 12.50\nO-1002 U-002 30\nO-1003 U-001 20.25\n---\nuser U-001\nuser U-002\norder O-1002\ntop",
      "U-1 x\nU-003 cy\nU-003 dup\n---\nO-2001 U-009 5\nO-2002 U-003 1.999\nO-2003 U-003 7\nO-2003 U-003 8\n---\nuser O-2003\norder U-003\nuser U-004\norder O-9999\nuser U-003",
      "U-005 solo\n---\n---\ntop\nuser U-005",
      "U-010 a\nU-011 b\n---\nO-3001 U-011 10\nO-3002 U-010 10\n---\ntop\norder O-3001",
      "---\nO-4001 U-001 1\n---\nuser U-001\ntop"],
    stretch=["Make the maps impossible to mutate even through a cast by freezing them — and explain why that is not the same guarantee.",
             "Add `refund <orderId> <amount>` producing a new store rather than editing the old one."],
)

TS_PRACTICE_MORE[16] = [
    _pr("tsm-w16-p2", "A tuple index under the flag", 'const tags = ["a", "b"] as const;\nconst first = tags[0];\n', "first", '"a"',
        strictness=_SI, why="This exercise is checked with `noUncheckedIndexedAccess` on.",
        hints=["A tuple's length is known, so a fixed index is never out of range.", "`as const` keeps the literal."]),
    _dx("tsm-w16-d3", "A read-only list passed to a mutating helper",
        "error TS2345: Argument of type 'readonly string[]' is not assignable to parameter of type 'string[]'.",
        _STDIN + 'function sortNames(xs: string[]): string[] {\n  return xs.sort();\n}\nconst names: readonly string[] = input.split(" ");\nconsole.log(sortNames(names).join(","));\nconsole.log(names.join(","));\n',
        _STDIN + 'function sortNames(xs: readonly string[]): string[] {\n  return xs.toSorted();\n}\nconst names: readonly string[] = input.split(" ");\nconsole.log(sortNames(names).join(","));\nconsole.log(names.join(","));\n',
        [("b c a", "a,b,c\nb,c,a"), ("x", "x\nx")], strictness=_SI, ask="Sort a copy — the original order must survive.",
        hints=["A function that sorts in place needs a mutable array.", "Accept `readonly string[]` and return a sorted copy with `toSorted()`."]),
    _fx("tsm-w16-f2", "A frozen object with a mutable inside",
        "Print the default tags, then the user's tags (the defaults plus the input word). The defaults change too.",
        _STDIN + 'const DEFAULTS = Object.freeze({ tags: ["base"] });\nfunction withTag(tag: string): string[] {\n  const tags = DEFAULTS.tags;\n  tags.push(tag);\n  return tags;\n}\nconst mine = withTag(input);\nconsole.log(DEFAULTS.tags.join(","));\nconsole.log(mine.join(","));\n',
        _STDIN + 'const DEFAULTS = Object.freeze({ tags: ["base"] });\nfunction withTag(tag: string): string[] {\n  return [...DEFAULTS.tags, tag];\n}\nconst mine = withTag(input);\nconsole.log(DEFAULTS.tags.join(","));\nconsole.log(mine.join(","));\n',
        [("x", "base\nbase,x"), ("urgent", "base\nbase,urgent")], strictness=_SI,
        hints=["`Object.freeze` is shallow: the array inside is still mutable.", "Build a new array instead of pushing onto the shared one."]),
]

TS_CARDS_MORE[16] = [
    ("Validator vs parser, in one line?", "A validator returns `true`/`false` and forgets; a parser returns a more precise type (`Email`) that proves the check happened."),
    ("How do you declare an unforgeable brand?", "`declare const B: unique symbol; type Email = string & { readonly [B]: true };` — kept private to the module."),
    ("What does a `unique symbol` brand cost at runtime?", "Nothing: `declare` emits no code and the intersection is erased — the value is a plain string."),
    ("Where does the one `as Email` belong?", "Inside the smart constructor, immediately after the check that justifies it."),
    ("How do you type a list that can't be empty?", "`readonly [T, ...T[]]` — its first element is always present."),
    ("Why normalise inside the parser?", "So equal values become equal (trimmed, lower-cased, integer cents) and duplicates can't sneak in."),
]

# ===========================================================================
# Week 17 — Composition, utility types, runtime validation
# ===========================================================================

TS_PROBLEM_SETS[17] = [
    _tsp(17, "tsm-w17-apply-patch", "Apply patches to a task", "warm-up",
         "The first input line is a task's title; the task starts as `{ id: 1, title, done: false, priority: \"normal\" }`. Each later line is a JSON patch of type `Partial<Omit<Task, \"id\">>`. Check it — `title` a non-empty string, `done` a boolean, `priority` one of `low`/`normal`/`high`, no other keys (including `id`) — and print `rejected: <problems joined by \"; \">` or apply it and print the task as `#1 [x] <title> (<priority>)` (`[ ]` when not done).",
         r"""
type Priority = "low" | "normal" | "high";
type Task = { id: number; title: string; done: boolean; priority: Priority };
type TaskPatch = Partial<Omit<Task, "id">>;
const PRIORITIES: readonly string[] = ["low", "normal", "high"];
const isPriority = (v: unknown): v is Priority => typeof v === "string" && PRIORITIES.includes(v);
function parsePatch(data: Record<string, unknown>): TaskPatch | string[] {
  const problems: string[] = [];
  const patch: TaskPatch = {};
  for (const [key, value] of Object.entries(data)) {
    if (key === "title" && typeof value === "string" && value.trim() !== "") patch.title = value.trim();
    else if (key === "done" && typeof value === "boolean") patch.done = value;
    else if (key === "priority" && isPriority(value)) patch.priority = value;
    else if (key === "title" || key === "done" || key === "priority") problems.push(`bad ${key}`);
    else problems.push(`cannot change ${key}`);
  }
  return problems.length > 0 ? problems : patch;
}
const [title = "", ...patches] = input.split("\n");
let task: Task = { id: 1, title: title.trim(), done: false, priority: "normal" };
for (const line of patches) {
  const result = parsePatch(JSON.parse(line) as Record<string, unknown>);
  if (Array.isArray(result)) {
    console.log(`rejected: ${result.join("; ")}`);
    continue;
  }
  task = { ...task, ...result };
  console.log(`#${task.id} [${task.done ? "x" : " "}] ${task.title} (${task.priority})`);
}
""", ['Write report\n{"done":true}\n{"priority":"urgent","id":7}\n{"title":"Write the report","priority":"high"}\n{"title":"  "}\n{}'],
         hints=["`Partial<Omit<Task, \"id\">>` is exactly \"any subset of the fields except the id\".",
                "Build the patch key by key, so a bad field never reaches the task."]),
    _tsp(17, "tsm-w17-defaults", "Fill in the defaults — carefully", "warm-up",
         "Window options have defaults `{ width: 800, height: 600, title: \"Untitled\", resizable: true, theme: \"light\" }`. Each input line is a JSON object of overrides (a `Partial<Options>`). Keep only overrides of the right type (a positive number for `width`/`height`, a string `title`, a boolean `resizable`, `light` or `dark` for `theme`); print `ignored <key>` for each other key, in input order. Then print the resolved `<width>x<height> \"<title>\" resizable=<bool> theme=<theme>`. Note that a spread of `{ width: undefined }` would *erase* the default.",
         r"""
type Options = { width: number; height: number; title: string; resizable: boolean; theme: "light" | "dark" };
const DEFAULTS: Options = { width: 800, height: 600, title: "Untitled", resizable: true, theme: "light" };
function overrides(data: Record<string, unknown>): Partial<Options> {
  const out: Partial<Options> = {};
  for (const [key, v] of Object.entries(data)) {
    if ((key === "width" || key === "height") && typeof v === "number" && v > 0) out[key] = v;
    else if (key === "title" && typeof v === "string") out.title = v;
    else if (key === "resizable" && typeof v === "boolean") out.resizable = v;
    else if (key === "theme" && (v === "light" || v === "dark")) out.theme = v;
    else console.log(`ignored ${key}`);
  }
  return out;
}
for (const line of input.split("\n")) {
  const o: Options = { ...DEFAULTS, ...overrides(JSON.parse(line) as Record<string, unknown>) };
  console.log(`${o.width}x${o.height} "${o.title}" resizable=${o.resizable} theme=${o.theme}`);
}
""", ['{}\n{"width":1024,"theme":"dark"}\n{"height":-1,"title":"","resizable":"no","color":"red"}\n{"width":null,"theme":"blue","title":"Main"}'],
         hints=["Copy an override only when it is present *and* valid; a key set to `undefined` or `null` must not reach the spread."]),
    _tsp(17, "tsm-w17-redact", "Strip the secrets", "warm-up",
         "Each input line is a JSON value (usually an object) to be logged. Remove, at any depth, every key named `password` or `token`, every key ending in `Secret`, and every key starting with `_`. Print the cleaned value as JSON (keys in their original order) and then `removed <k>`.",
         r"""
let removed = 0;
const isSecret = (key: string) => key === "password" || key === "token" || key.endsWith("Secret") || key.startsWith("_");
function redact(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(redact);
  if (typeof value !== "object" || value === null) return value;
  const out: Record<string, unknown> = {};
  for (const [key, v] of Object.entries(value)) {
    if (isSecret(key)) removed++;
    else out[key] = redact(v);
  }
  return out;
}
for (const line of input.split("\n")) {
  removed = 0;
  console.log(JSON.stringify(redact(JSON.parse(line))));
  console.log(`removed ${removed}`);
}
""", ['{"user":"ana","password":"x","profile":{"apiSecret":"k","city":"Oslo"},"sessions":[{"token":"t","ip":"1.2.3.4"}],"_rev":3}\n[1,{"password":2}]\n"just a string"'],
         hints=["At runtime there is no `Omit` — you build a new object without the keys.", "Recurse into arrays and objects; return everything else unchanged."]),
    _tsp(17, "tsm-w17-category-totals", "Totals for every category", "core",
         "Categories are `food`, `rent`, `travel`, `fun`, declared once `as const` with the `Category` type derived from them. Each input line is `<category> <amount>`; an unknown category counts as `other`. Keep a `Record<Category | \"other\", number>` — every key present from the start — and print every category in order as `<name> <total> <share>%` (total with two decimals, share of the grand total with one), then `biggest <name>` (the first on a tie).",
         r"""
const CATEGORIES = ["food", "rent", "travel", "fun"] as const;
type Category = (typeof CATEGORIES)[number];
type Bucket = Category | "other";
const BUCKETS: readonly Bucket[] = [...CATEGORIES, "other"];
const totals: Record<Bucket, number> = { food: 0, rent: 0, travel: 0, fun: 0, other: 0 };
const toBucket = (s: string): Bucket => CATEGORIES.find((c) => c === s) ?? "other";
for (const line of input.split("\n")) {
  const [category = "", amount = "0"] = line.trim().split(/\s+/);
  totals[toBucket(category)] += Number(amount);
}
const grand = BUCKETS.reduce((s, b) => s + totals[b], 0);
for (const b of BUCKETS) {
  const share = grand === 0 ? 0 : (totals[b] / grand) * 100;
  console.log(`${b} ${totals[b].toFixed(2)} ${share.toFixed(1)}%`);
}
const biggest = BUCKETS.reduce((best, b) => (totals[b] > totals[best] ? b : best));
console.log(`biggest ${biggest}`);
""", ["food 12.50\nrent 900\nfood 30\ntaxes 120\ntravel 0.5", "fun 1\nfun 2", "gift 5"],
         hints=["A `Record` over a finite union has every key — no `undefined`, even under this week's flag.",
                "`CATEGORIES.find((c) => c === s)` turns an input string into a `Category` or `undefined`."]),
    _tsp(17, "tsm-w17-project", "Project the fields you asked for", "core",
         "The first input line is a JSON array of tasks with `id`, `title`, `owner`, `done` and `estimate`. Each later line is `fields: <a,b,…>`. Print every task with only those fields, in the order asked, as JSON — or `unknown field <f>` for the first field a task doesn't have in its type. (A runtime `Pick`.)",
         r"""
type Task = { id: number; title: string; owner: string; done: boolean; estimate: number };
const KEYS: readonly (keyof Task)[] = ["id", "title", "owner", "done", "estimate"];
const isKey = (s: string): s is keyof Task => KEYS.some((k) => k === s);
const [first = "[]", ...requests] = input.split("\n");
const tasks = JSON.parse(first) as Task[];
for (const line of requests) {
  const wanted = line.replace(/^fields:\s*/, "").split(",").map((f) => f.trim());
  const bad = wanted.find((f) => !isKey(f));
  if (bad !== undefined) {
    console.log(`unknown field ${bad}`);
    continue;
  }
  const keys = wanted.filter(isKey);
  for (const t of tasks) console.log(JSON.stringify(Object.fromEntries(keys.map((k) => [k, t[k]]))));
}
""", ['[{"id":1,"title":"write","owner":"ana","done":false,"estimate":3},{"id":2,"title":"test","owner":"bo","done":true,"estimate":1}]\nfields: id,title\nfields: done, owner\nfields: id,secret\nfields: estimate'],
         hints=["A type predicate `isKey` turns a requested name into a `keyof Task`.",
                "`Object.fromEntries` builds the projected object from `[key, value]` pairs."]),
    _tsp(17, "tsm-w17-teams", "Summarise hours by team", "core",
         "Each input line is `<team> <person> <hours>`. For each team print `<team>: <members> people (`person` for one), <total>h, avg <a>h, top <person>` — members counted once however many lines they have, the average per person to one decimal, the top person by their total hours (alphabetically first on a tie) — teams sorted by total hours, most first (then by name).",
         r"""
type TeamSummary = { team: string; members: number; hours: number; top: string };
const teams = new Map<string, Map<string, number>>();
for (const line of input.split("\n")) {
  const [team = "", person = "", hours = "0"] = line.trim().split(/\s+/);
  const people = teams.get(team) ?? new Map<string, number>();
  people.set(person, (people.get(person) ?? 0) + Number(hours));
  teams.set(team, people);
}
const summaries: TeamSummary[] = [...teams].map(([team, people]) => {
  const ranked = [...people].sort(([a, x], [b, y]) => y - x || a.localeCompare(b));
  return {
    team,
    members: people.size,
    hours: ranked.reduce((s, [, h]) => s + h, 0),
    top: ranked[0]?.[0] ?? "",
  };
});
summaries.sort((a, b) => b.hours - a.hours || a.team.localeCompare(b.team));
for (const s of summaries) {
  console.log(`${s.team}: ${s.members} ${s.members === 1 ? "person" : "people"}, ${s.hours}h, avg ${(s.hours / s.members).toFixed(1)}h, top ${s.top}`);
}
""", ["web ana 5\nweb bo 3\nops cy 4\nweb ana 2\nops dee 4\nqa eve 1", "solo zed 0.5"],
         hints=["A `Map` of `Map`s: team → person → hours.", "Sort each team's people once; the first is the top person and the rest give the total."]),
    _tsp(17, "tsm-w17-form-errors", "A map of form errors", "stretch",
         "A sign-up form has `username`, `password`, `confirm` and `age`. Each input line is the submitted JSON. Collect errors in a `Partial<Record<Field, string>>` — at most one per field: `username` must be 3-16 letters, digits or `_`; `password` at least 8 characters with a digit; `confirm` must equal the password; `age` is optional but must be a whole number of at least 13. A missing required field is `required`. Print `ok` or the errors in field order as `<field>: <message>` joined by `; `.",
         r"""
const FIELDS = ["username", "password", "confirm", "age"] as const;
type Field = (typeof FIELDS)[number];
type FormErrors = Partial<Record<Field, string>>;
function validate(form: Record<string, unknown>): FormErrors {
  const errors: FormErrors = {};
  const { username, password, confirm, age } = form;
  if (username === undefined) errors.username = "required";
  else if (typeof username !== "string" || !/^\w{3,16}$/.test(username)) errors.username = "3-16 letters, digits or _";
  if (password === undefined) errors.password = "required";
  else if (typeof password !== "string" || password.length < 8 || !/\d/.test(password)) errors.password = "at least 8 characters with a digit";
  if (confirm === undefined) errors.confirm = "required";
  else if (confirm !== password) errors.confirm = "does not match";
  if (age !== undefined && (typeof age !== "number" || !Number.isInteger(age) || age < 13)) errors.age = "must be a whole number, 13 or over";
  return errors;
}
for (const line of input.split("\n")) {
  const errors = validate(JSON.parse(line) as Record<string, unknown>);
  const messages = FIELDS.flatMap((f) => {
    const message = errors[f];
    return message === undefined ? [] : [`${f}: ${message}`];
  });
  console.log(messages.length === 0 ? "ok" : messages.join("; "));
}
""", ['{"username":"ana_1","password":"secret123","confirm":"secret123"}\n{"username":"a!","password":"short","confirm":"other","age":12.5}\n{"age":30}\n{"username":"bo","password":"longenough1","confirm":"longenough1","age":13}'],
         hints=["`Partial<Record<Field, string>>` means \"any of these fields may have an error\" — every read is `string | undefined`.",
                "Loop over `FIELDS`, not over the errors object, so the output order is fixed."]),
    _tsp_types(17, "tsm-w17-update-type", "An update needs the id, and nothing else is required", "core",
               "Derive `UserUpdate` from `User`: the `id` is required, `name` and `email` may be given, and nothing else (the password and the creation date are not updatable).",
               '''
type User = { id: number; name: string; email: string; password: string; createdAt: string };
type UserUpdate = Pick<User, "id"> & Partial<Pick<User, "name" | "email">>;

const justId: UserUpdate = { id: 1 };
const rename: UserUpdate = { id: 1, name: "ana" };
''', 'Pick<User, "id"> & Partial<Pick<User, "name" | "email">>',
               '''
type _1 = Expect<Equal<UserUpdate["id"], number>>;
type _2 = Expect<Equal<UserUpdate["email"], string | undefined>>;
function _typeTests() {
  // @ts-expect-error — the id is required
  const noId: UserUpdate = { name: "x" };
  // @ts-expect-error — passwords are not updated here
  const pw: UserUpdate = { id: 1, password: "x" };
}
''', hints=["Two pieces: the required part and the optional part, joined with `&`.",
            "`Pick` the id; `Partial<Pick<…>>` the rest."]),
    _tsp_types(17, "tsm-w17-settings-type", "Settings typed from their defaults", "core",
               "The defaults function is the single source of truth. Derive `Settings` from what it returns, so adding a setting there adds it to the type.",
               '''
const defaults = () => ({ theme: "dark" as "dark" | "light", fontSize: 14, autosave: true });
type Settings = ReturnType<typeof defaults>;
type SettingKey = keyof Settings;
''', "ReturnType<typeof defaults>",
               '''
type _1 = Expect<Equal<Settings, { theme: "dark" | "light"; fontSize: number; autosave: boolean }>>;
type _2 = Expect<Equal<SettingKey, "theme" | "fontSize" | "autosave">>;
''', hints=["`defaults` is a value; `typeof defaults` is its function type.", "A utility type reads a function type's result."]),
]

TS_PROJECTS[17] = _project(
    17, "tasks.ts — a typed task API with validation",
    "Build the core of a task service: one `Task` model, and every other shape — the create payload, the patch, the list summary — derived from it with utility types. Every JSON body is validated from `unknown`, and every problem is reported at once.",
    ["`Task` is `{ id, title, done, priority, tags }` with priority `low`/`normal`/`high`. Derive `TaskDraft = Pick<Task, \"title\"> & Partial<Pick<Task, \"priority\" | \"tags\">>` and `TaskPatch = Partial<Omit<Task, \"id\">>`.",
     "`create <json>`: title a non-empty string (required), priority one of the three (default `normal`), tags an array of strings (default none), no other keys. Print `created #<id>` (ids start at 1) or `create rejected: ` and every problem — `title: required`, `title: must be text`, `priority: must be low, normal or high`, `tags: must be a list of strings`, `unknown field <k>` — joined by `; `.",
     "`patch <id> <json>`: the same rules for any subset of `title`, `done` (boolean, else `done: must be true or false`), `priority`, `tags`; `id: cannot change` if `id` is present. Print `patched #<id> (<changed fields in input order>)`, `patch #<id>: nothing to change` for an empty patch, `patch rejected: …`, or `no task #<id>`. `delete <id>` prints `deleted #<id>` or `no task #<id>`.",
     "`list` prints each task by id: `#<id> [x] <title> (<priority>)` plus ` #tag` for each tag (`[ ]` when not done), or `(no tasks)`.",
     "`summary` prints `open <a>, done <b>, high=<h> normal=<n> low=<l>`."],
    r"""
type Priority = "low" | "normal" | "high";
type Task = { id: number; title: string; done: boolean; priority: Priority; tags: string[] };
type TaskDraft = Pick<Task, "title"> & Partial<Pick<Task, "priority" | "tags">>;
type TaskPatch = Partial<Omit<Task, "id">>;
const PRIORITIES: readonly Priority[] = ["low", "normal", "high"];
const isPriority = (v: unknown): v is Priority => PRIORITIES.some((p) => p === v);
const isTags = (v: unknown): v is string[] => Array.isArray(v) && v.every((t) => typeof t === "string");

function readFields(data: unknown, allowDone: boolean): { patch: TaskPatch; problems: string[] } {
  const patch: TaskPatch = {};
  const problems: string[] = [];
  if (typeof data !== "object" || data === null || Array.isArray(data)) return { patch, problems: ["body: must be an object"] };
  for (const [key, v] of Object.entries(data)) {
    if (key === "title") {
      if (typeof v !== "string") problems.push("title: must be text");
      else if (v.trim() === "") problems.push("title: required");
      else patch.title = v.trim();
    } else if (key === "priority") {
      if (isPriority(v)) patch.priority = v;
      else problems.push("priority: must be low, normal or high");
    } else if (key === "tags") {
      if (isTags(v)) patch.tags = v;
      else problems.push("tags: must be a list of strings");
    } else if (key === "done" && allowDone) {
      if (typeof v === "boolean") patch.done = v;
      else problems.push("done: must be true or false");
    } else if (key === "id" && allowDone) {
      problems.push("id: cannot change");
    } else {
      problems.push(`unknown field ${key}`);
    }
  }
  return { patch, problems };
}
function parseDraft(data: unknown): TaskDraft | string[] {
  const { patch, problems } = readFields(data, false);
  if (patch.title === undefined && !problems.some((p) => p.startsWith("title"))) problems.unshift("title: required");
  if (problems.length > 0 || patch.title === undefined) return problems;
  const draft: TaskDraft = { title: patch.title };
  if (patch.priority !== undefined) draft.priority = patch.priority;
  if (patch.tags !== undefined) draft.tags = patch.tags;
  return draft;
}

const tasks = new Map<number, Task>();
let nextId = 1;
for (const line of input.split("\n")) {
  const [cmd = "", ...rest] = line.trim().split(" ");
  if (cmd === "create") {
    const draft = parseDraft(JSON.parse(rest.join(" ")));
    if (Array.isArray(draft)) {
      console.log(`create rejected: ${draft.join("; ")}`);
      continue;
    }
    const task: Task = { id: nextId++, done: false, priority: draft.priority ?? "normal", tags: draft.tags ?? [], title: draft.title };
    tasks.set(task.id, task);
    console.log(`created #${task.id}`);
  } else if (cmd === "patch" || cmd === "delete") {
    const id = Number(rest[0]);
    const task = tasks.get(id);
    if (task === undefined) {
      console.log(`no task #${rest[0] ?? ""}`);
    } else if (cmd === "delete") {
      tasks.delete(id);
      console.log(`deleted #${id}`);
    } else {
      const { patch, problems } = readFields(JSON.parse(rest.slice(1).join(" ")), true);
      if (problems.length > 0) {
        console.log(`patch rejected: ${problems.join("; ")}`);
        continue;
      }
      if (Object.keys(patch).length === 0) {
        console.log(`patch #${id}: nothing to change`);
        continue;
      }
      tasks.set(id, { ...task, ...patch });
      console.log(`patched #${id} (${Object.keys(patch).join(", ")})`);
    }
  } else if (cmd === "list") {
    if (tasks.size === 0) console.log("(no tasks)");
    for (const t of [...tasks.values()].sort((a, b) => a.id - b.id)) {
      console.log(`#${t.id} [${t.done ? "x" : " "}] ${t.title} (${t.priority})${t.tags.map((tag) => ` #${tag}`).join("")}`);
    }
  } else if (cmd === "summary") {
    const all = [...tasks.values()];
    const count = (p: Priority) => all.filter((t) => t.priority === p).length;
    const done = all.filter((t) => t.done).length;
    console.log(`open ${all.length - done}, done ${done}, high=${count("high")} normal=${count("normal")} low=${count("low")}`);
  }
}
""", ['create {"title":"Write report","priority":"high","tags":["work"]}\ncreate {"title":"Buy milk"}\nlist\npatch 2 {"done":true,"tags":["home","errand"]}\nlist\nsummary',
      'create {}\ncreate {"title":5,"priority":"urgent","tags":"x","owner":"ana"}\ncreate {"title":"  "}\nlist\nsummary',
      'create {"title":"a"}\npatch 1 {"id":9,"done":"yes"}\npatch 7 {"done":true}\ndelete 1\ndelete 1\nlist',
      'create {"title":"t","priority":"low"}\npatch 1 {"title":"renamed","priority":"normal","done":false}\nlist',
      'summary\ncreate {"title":"x","tags":[]}\npatch 1 {}\nlist'],
    stretch=["Rewrite the validation with the week's schema library, so `TaskDraft` is `Infer<typeof TaskDraftSchema>`.",
             "Add `undo`, keeping each version of the store immutable (week 16)."],
)

TS_PRACTICE_MORE[17] = [
    _pr("tsm-w17-p9", "Reading a Partial field", 'const patch: Partial<{ title: string }> = {};\nconst t = patch.title;\n', "t", "string | undefined",
        strictness=_SI, hints=["`Partial` makes every property optional.", "An optional property reads as `T | undefined`."]),
    _dx("tsm-w17-d9", "A key that isn't there",
        "error TS2344: Type '\"titel\"' does not satisfy the constraint 'keyof Task'.",
        'type Task = { id: number; title: string };\ntype Summary = Pick<Task, "id" | "titel">;\nconst s: Summary = { id: 1, title: "write" };\nconsole.log(JSON.stringify(s));\n',
        'type Task = { id: number; title: string };\ntype Summary = Pick<Task, "id" | "title">;\nconst s: Summary = { id: 1, title: "write" };\nconsole.log(JSON.stringify(s));\n',
        [("", '{"id":1,"title":"write"}')], strictness=_SI,
        hints=["`Pick` only accepts keys the type has.", "Fix the spelling."]),
    _fx("tsm-w17-f9", "A spread that erased the default",
        "Print the window width: the given number, or 800 when the input is empty. It prints `undefined` for empty input.",
        _STDIN + 'const DEFAULTS = { width: 800 };\nconst given = input === "" ? undefined : Number(input);\nconst options = { ...DEFAULTS, ...{ width: given } };\nconsole.log(options.width);\n',
        _STDIN + 'const DEFAULTS = { width: 800 };\nconst given = input === "" ? undefined : Number(input);\nconst options = { ...DEFAULTS, width: given ?? DEFAULTS.width };\nconsole.log(options.width);\n',
        [("", "800"), ("1024", "1024")], strictness=_SI,
        hints=["Spreading `{ width: undefined }` sets `width` to `undefined` — it doesn't skip it.", "Fall back explicitly with `??`."]),
]

TS_CARDS_MORE[17] = [
    ("Why derive a type from a schema instead of writing both?", "Two descriptions drift; with `type T = Infer<typeof Schema>` there is only one."),
    ("`JSON.parse(text) as User` — what did it check?", "Nothing. An assertion is erased; only a runtime validator checks."),
    ("What does a schema's `parse` return?", "Either the typed value or the issues — a result union such as `{ ok: true; value } | { ok: false; issues }`."),
    ("Why collect every validation issue?", "So the sender can fix all of them in one pass instead of one per round trip."),
    ("Name three libraries built on the schema-first idea.", "Zod, Valibot and ArkType."),
    ("Where do you call a schema's `parse`?", "Once, at the boundary where untrusted data enters; inside, the inferred type carries the guarantee."),
]

# ===========================================================================
# Quiz top-ups (X-30): Month 4 week banks raised to 40+ questions.
# ===========================================================================

TS_QUIZ_TOPUP[14] = [
    _mq("Under `noUncheckedIndexedAccess`, what is `const [first] = xs` typed as for `xs: string[]`?", "`string | undefined`", ["`string`", "`[string]`", "`never`"],
        "Destructuring reads an index, so the flag adds `undefined` (a tuple's fixed positions are exempt)."),
    _mq("What does `exactOptionalPropertyTypes` forbid?", "Assigning `undefined` explicitly to an optional property not typed `| undefined`", ["Optional properties entirely", "Missing properties", "`null` values"],
        "It separates \"absent\" from \"present but undefined\"."),
    _mq("`moduleResolution: bundler` vs `nodenext` — which fits a Node app without a bundler?", "`nodenext`", ["`bundler`", "`classic`", "`node10`"],
        "`nodenext` follows Node's own rules (file extensions, `exports`); `bundler` mirrors how bundlers resolve."),
]

TS_QUIZ_TOPUP[15] = [
    _mq("What does `x as unknown as T` do?", "Forces any conversion past the compiler — a double assertion with no check", ["Converts `x` safely", "Validates `x` at runtime", "Is a syntax error"],
        "It exists for genuine escape hatches; treat it as a code-review red flag."),
    _mq("When is `as` reasonable?", "When you know something the compiler can't — and you've checked it, or it's a well-understood API", ["Whenever the compiler complains", "To convert strings to numbers", "Never"],
        "`as` is a claim. Prefer narrowing or validation when a check is possible."),
    _mq("What does `satisfies` check against a union target like `\"a\" | \"b\"`?", "That the value is one of the members, keeping the literal type", ["Nothing", "That it's a string", "That it's both"],
        "`const x = \"a\" satisfies \"a\" | \"b\"` is typed `\"a\"`."),
    _mq("Do excess-property checks apply to a variable passed to a function?", "No — only to fresh object literals", ["Yes, always", "Only in strict mode", "Only for classes"],
        "Structural typing admits objects with extra properties once they're in a variable."),
    _mq("Why does TypeScript use structural rather than nominal typing?", "JavaScript code routinely uses plain objects of the right shape, not declared classes", ["It's faster to check", "It prevents all bugs", "Classes don't exist in JavaScript"],
        "Typing \"duck typing\" is the whole point."),
    _mq("A function takes `{ name: string }`. Can you pass a `Date` with a `name` property added?", "Yes, if it has a string `name`", ["No, Date isn't an object type", "Only with `as`", "Only if `name` is readonly"],
        "Only the required members matter."),
    _mq("Is a `readonly` property assignable to a mutable one of the same type?", "Yes — `readonly` doesn't affect assignability", ["No", "Only for arrays", "Only with `as`"],
        "That's why a readonly view isn't a guarantee someone else can't mutate the object."),
    _mq("Is `readonly string[]` assignable to `string[]`?", "No — the mutable type has methods the readonly one lacks", ["Yes", "Only for tuples", "Only with `satisfies`"],
        "Array readonly-ness *is* checked, because `push` and friends differ."),
    _mq("What does `in out T` declare?", "`T` is invariant — both consumed and produced", ["`T` is optional", "`T` is exported", "`T` is readonly"], "Variance annotations: `out` covariant, `in` contravariant, both invariant."),
    _mq("Why is a callback parameter typed `(x: Animal) => void` more flexible for callers?", "It accepts any animal, so it fits slots expecting handlers for dogs, cats, …", ["It's faster", "It can return anything", "It's not"],
        "Contravariance: a handler of the supertype works wherever a handler of a subtype is needed."),
    _mq("What is `const el = document as any` in a codebase a sign of?", "Type checking turned off at that point — every use of `el` is unchecked", ["Good practice", "A performance fix", "Required for DOM access"],
        "`any` spreads: anything derived from it is `any` too."),
    _mq("What does `satisfies` do to the variable's declared type?", "Nothing — the variable keeps its inferred type", ["Replaces it with the target", "Makes it readonly", "Widens it"], "It checks, it doesn't annotate."),
    _mq("Which reports a missing property in a literal: annotation, `satisfies`, or `as`?", "Annotation and `satisfies`, but not `as`", ["Only `as`", "All three", "None"],
        "`as` only requires the two types to overlap, so a literal missing a required property is accepted."),
    _mq("Can you assign `{ x: 1 }` to `{ x: number; y?: number }`?", "Yes — optional properties may be absent", ["No", "Only with `as`", "Only if `y` is readonly"], "Optional means \"may be missing\"."),
    _mq("How does TypeScript compare two function types' return types?", "Covariantly — the source's return must be assignable to the target's", ["Contravariantly", "Bivariantly", "It ignores them"],
        "A function returning `Dog` fits a slot expecting a function returning `Animal`."),
    _mq("Why is `interface` method syntax `m(x: T): void` looser than `m: (x: T) => void`?", "Method parameters are checked bivariantly for compatibility", ["It isn't", "Methods can't be typed", "Properties are optional"],
        "Prefer property syntax for callback members you want checked strictly."),
    _mq("What is the risk of `JSON.parse(text) satisfies User`?", "It compiles and checks nothing — `JSON.parse` returns `any`, which satisfies every type", ["It validates the JSON", "It throws on bad JSON", "It converts the JSON"],
        "`satisfies` is compile-time only; untrusted data needs a runtime check."),
    _mq("What makes `private` members affect assignability?", "A class with a private member is compatible only with instances of that same class declaration", ["Nothing", "They're erased", "Only `#private` affects it"],
        "The one nominal corner of TypeScript's class types."),
]

TS_QUIZ_TOPUP[16] = [
    _mq("What is the smallest brand you can write?", "`type Email = string & { readonly __brand: \"Email\" }`", ["`type Email = string`", "`class Email extends String {}`", "`enum Email {}`"],
        "The phantom property only exists in the type; a `unique symbol` key makes it unforgeable outside the module."),
    _mq("Does a branded `Cents` still support arithmetic?", "Yes, but the result is a plain `number` — re-brand it through a function", ["No", "Yes, and the result stays `Cents`", "Only addition"],
        "`a + b` on two `Cents` gives `number`; wrap arithmetic in helpers that return `Cents`."),
    _mq("What does `ReadonlyArray<T>` lack compared with `T[]`?", "Every mutating method — `push`, `pop`, `splice`, `sort`, index assignment", ["`map` and `filter`", "`length`", "Iteration"],
        "Non-mutating methods (`map`, `slice`, `toSorted`) are all still there."),
    _mq("What does `Readonly<T>` do to nested objects?", "Nothing — it's shallow", ["Freezes them", "Makes them readonly too", "Removes them"], "A `DeepReadonly` needs a recursive mapped type (week 20)."),
    _mq("What does `Object.freeze` return, typed?", "`Readonly<T>` (and `readonly T[]` for arrays)", ["`T`", "`void`", "`frozen T`"], "The type reflects the shallow freeze."),
    _mq("In strict mode, what happens on assigning to a frozen object's property?", "A TypeError is thrown", ["It's silently ignored", "The property is updated", "A warning"],
        "Modules are strict, so the failure is loud. In sloppy scripts it's silent."),
    _mq("How do you sort an array without mutating it?", "`xs.toSorted(compare)`", ["`xs.sort(compare)`", "`sorted(xs)`", "`xs.sorted()`"], "Or `[...xs].sort(compare)` before ES2023."),
    _mq("Why is aliasing a common source of mutation bugs?", "Two variables refer to the same object, so a change through one is seen through the other", ["It creates copies", "It's a TypeScript feature", "It slows programs"],
        "Immutable updates avoid the question entirely."),
    _mq("What does `{ ...state, user: { ...state.user, name } }` do?", "Copies the path to the change and shares everything else", ["Deep-copies the whole state", "Mutates `state.user`", "Replaces the state with `user`"],
        "Structural sharing: new objects only where something changed."),
    _mq("A smart constructor returns `Email | undefined`. What should the caller do with `undefined`?", "Handle the invalid case explicitly — report or reject it", ["Cast it to `Email`", "Ignore it", "Retry until it works"],
        "The type forces the decision to be made, which is the point."),
    _mq("Why not validate an email with a `boolean` function?", "The knowledge is thrown away; later code can't tell a checked string from an unchecked one", ["Booleans are slow", "Regexes don't return booleans", "It's fine"],
        "Parse into a branded type instead."),
    _mq("Does `const` make an array immutable?", "No — it prevents rebinding; `push` still works", ["Yes", "Only for primitives", "Only with `as const`"], "Use `readonly` types (or `as const` for literals)."),
    _mq("What does `as const` on an array literal make it?", "A readonly tuple of literal types", ["A frozen array", "A mutable array", "A Set"], "Types only — nothing is frozen at runtime."),
    _mq("What's the cost of a brand compared with a wrapper class?", "Zero runtime cost; a wrapper allocates an object and needs unwrapping", ["Brands are slower", "They're identical", "Brands need a library"],
        "Brands are erased; the value is still a plain string or number."),
    _mq("Can two brands with the same symbol-less `__brand` string be confused?", "Yes — `{ __brand: \"Id\" }` in two modules is the same type", ["No, never", "Only at runtime", "Only for numbers"],
        "A module-private `unique symbol` avoids accidental collisions."),
    _mq("Which update to `const arr: readonly number[]` compiles?", "`const next = [...arr, 4];`", ["`arr.push(4)`", "`arr[0] = 4`", "`arr.length = 0`"], "Build a new array."),
    _mq("What is persistent data structure sharing good for?", "Cheap copies: undo/redo, time travel and snapshots without copying everything", ["Faster mutation", "Smaller types", "Avoiding garbage collection"],
        "Each version shares unchanged parts with the previous one."),
    _mq("Why validate at the boundary rather than in every function?", "Inside the boundary, precise types carry the guarantee; checking again is noise and drift", ["Boundaries are faster", "Types can't be trusted inside", "Functions can't validate"],
        "Parse once, then trust."),
]

TS_QUIZ_TOPUP[17] = [
    _mq("What is `Omit<{ a: 1; b: 2 }, \"c\">`?", "`{ a: 1; b: 2 }` — `Omit` accepts keys that don't exist", ["A compile error", "`{}`", "`never`"],
        "`Omit`'s key parameter is unconstrained, so a typo silently does nothing. `Pick` would reject it."),
    _mq("Why does `Pick<T, \"typo\">` fail while `Omit<T, \"typo\">` compiles?", "`Pick` constrains keys to `keyof T`; `Omit` takes any key", ["`Omit` is newer", "`Pick` is stricter about values", "It's a bug"],
        "Wrap it in your own `StrictOmit<T, K extends keyof T>` if you want the check."),
    _mq("What does `ReturnType<typeof f>` require?", "`typeof` — `f` is a value, and utilities take types", ["Nothing", "A generic", "`as const`"], "`ReturnType<f>` is an error."),
    _mq("What is `Parameters<typeof f>[0]`?", "The type of `f`'s first parameter", ["`f`'s first argument value", "The number of parameters", "`unknown`"], "An indexed access on the parameter tuple."),
    _mq("What does `Readonly<Pick<User, \"id\" | \"name\">>` produce?", "A type with just `id` and `name`, both readonly", ["All of `User`, readonly", "An error", "A mutable pick"], "Utilities compose."),
    _mq("What does `NoInfer<T>` (TS 5.4) do in a signature?", "Stops that position from contributing to inferring `T`", ["Makes `T` optional", "Disables checks", "Requires an explicit type argument"], "Useful for defaults and fallbacks."),
    _mq("What is composition over inheritance, in types?", "Building types by combining smaller ones (`&`, `Pick`, mapped types) instead of deep `extends` chains", ["Using classes everywhere", "Never using interfaces", "Using `any`"],
        "Small pieces are easier to reuse and to change."),
    _mq("What's a risk of `Partial<T>` as a function parameter everywhere?", "Required data can go missing without the compiler noticing", ["It's slow", "It removes methods", "It makes fields readonly"], "Use it for patches and options, not for complete records."),
    _mq("A `Record<\"a\" | \"b\", number>` literal is missing `b`. Result?", "A compile error — every key is required", ["It's fine", "`b` defaults to 0", "A runtime error"], "`Record` over a finite union demands every key."),
    _mq("What does `Awaited<Promise<Promise<number>>>` give?", "`number`", ["`Promise<number>`", "`Promise<Promise<number>>`", "`unknown`"], "It unwraps recursively, as `await` does."),
    _mq("What does `InstanceType<typeof MyClass>` give?", "The type of an instance of `MyClass`", ["The class itself", "The constructor's parameters", "`object`"], "Useful when all you have is the class value."),
    _mq("What does `ConstructorParameters<typeof Date>` describe?", "The argument tuples `new Date(…)` accepts", ["Date's methods", "Date's instance type", "Nothing"], "The constructor counterpart of `Parameters`."),
    _mq("Where should a validator's schema live relative to the type?", "The type should be derived from the schema — one source of truth", ["Separately, kept in sync by hand", "In a comment", "Only in tests"],
        "Two descriptions drift; one can't."),
    _mq("What does `Required<T>` do to `x?: number | undefined`?", "Makes `x` required and removes the `undefined` added by `?`", ["Nothing", "Makes it `never`", "Removes the property"], "It's the `-?` modifier in a mapped type."),
    _mq("What is `Extract<\"a\" | \"b\" | \"c\", \"a\" | \"z\">`?", "`\"a\"`", ["`\"a\" | \"z\"`", "`never`", "`\"b\" | \"c\"`"], "Only members of the first union that fit the second survive."),
    _mq("A `TaskPatch = Partial<Omit<Task, \"id\">>` — can a patch change the id?", "No — `id` isn't in the patch type", ["Yes, optionally", "Only to a number", "Only at runtime"], "Types make the rule part of the API."),
    _mq("When is a hand-written type better than a derived one?", "When it's a deliberate contract that must not change just because the source does", ["Never", "Always", "Only for primitives"],
        "Public API types are often pinned on purpose."),
    _mq("What does spreading a `Partial<Options>` with `{ width: undefined }` into defaults do?", "Overwrites `width` with `undefined`", ["Keeps the default", "Removes `width`", "Throws"],
        "Filter out undefined values or use `??` per field."),
]
