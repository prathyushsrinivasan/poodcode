# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery, Month 2 (weeks 5-8): problem sets, runnable projects,
# extra practice and review cards for the chapters in ts_chapters_m2.py.
#
# From week 5 many problems say "write the function": the learner writes
# only the function (`_tspf`), and a hidden driver reads stdin, calls it and
# prints — the Mastery version of the course's function harness. Expected
# outputs are computed (python tools/gen_ts_outputs.py). Code is in raw strings.
# ---------------------------------------------------------------------------

# Reading helpers the drivers share (drivers are appended after the learner's
# code, so they must not collide with names a solution might use).
_DRV = 'import * as __fs from "fs";\nconst __lines = __fs.readFileSync(0, "utf8").trim().split("\\n");\n'

# ===========================================================================
# Week 5 — Functions, parameters, overloads, closures
# ===========================================================================

TS_PROBLEM_SETS[5] = [
    _tspf(5, "tsm-w5-greet", "Defaults for missing arguments", "warm-up",
          "Write `greet(name?, greeting?)` returning `<greeting>, <name>!`, where a missing name means `world` and a missing greeting means `Hello`. The hidden driver calls it once per input line (`-` stands for an argument that is left out).",
          r"""
function greet(name = "world", greeting = "Hello"): string {
  return `${greeting}, ${name}!`;
}
""", "return `${greeting}, ${name}!`;",
          _DRV + r"""
const __arg = (t: string | undefined) => (t === undefined || t === "-" ? undefined : t);
for (const __line of __lines) {
  const [__a, __b] = __line.trim().split(/\s+/);
  console.log(greet(__arg(__a), __arg(__b)));
}
""", ["Ada Hi\n- Hey\nBo -\n- -", "Grace"],
          hints=["Default parameters apply whenever the argument is `undefined`."]),
    _tspf(5, "tsm-w5-safe-divide", "Divide, or say you can't", "warm-up",
          "Write `safeDivide(a: number, b: number): number | null` returning `a / b`, or `null` when `b` is 0. The driver prints each result (or `null`) for each input line `a b`.",
          r"""
function safeDivide(a: number, b: number): number | null {
  return b === 0 ? null : a / b;
}
""", "return b === 0 ? null : a / b;",
          _DRV + r"""
for (const __line of __lines) {
  const [__a = 0, __b = 0] = __line.trim().split(/\s+/).map(Number);
  const __r = safeDivide(__a, __b);
  console.log(__r === null ? "null" : __r.toFixed(3));
}
""", ["10 4\n1 0\n-9 3", "0 5\n7 -2"],
          hints=["The return type already says what to do when you can't divide."]),
    _tspf(5, "tsm-w5-sum-rest", "Any number of arguments", "warm-up",
          "Write `total(label: string, ...amounts: number[]): string` returning `<label>: <sum> (<count> items)`. The driver calls it with each line's first token as the label and the rest as numbers.",
          r"""
function total(label: string, ...amounts: number[]): string {
  let sum = 0;
  for (const a of amounts) sum += a;
  return `${label}: ${sum} (${amounts.length} items)`;
}
""", "  let sum = 0;\n  for (const a of amounts) sum += a;\n  return `${label}: ${sum} (${amounts.length} items)`;",
          _DRV + r"""
for (const __line of __lines) {
  const [__label = "", ...__rest] = __line.trim().split(/\s+/);
  console.log(total(__label, ...__rest.map(Number)));
}
""", ["food 3 4 5\nrent 900\nnothing"],
          hints=["A rest parameter is a real array inside the function."]),
    _tspf(5, "tsm-w5-plural", "Plurals with a default", "warm-up",
          "Write `pluralize(count: number, singular: string, plural = singular + \"s\"): string` returning `<count> <word>`, using the singular only when count is exactly 1. The driver passes lines `count singular [plural]`.",
          r"""
function pluralize(count: number, singular: string, plural = singular + "s"): string {
  return `${count} ${count === 1 ? singular : plural}`;
}
""", "return `${count} ${count === 1 ? singular : plural}`;",
          _DRV + r"""
for (const __line of __lines) {
  const [__n = "0", __s = "", __p] = __line.trim().split(/\s+/);
  console.log(__p === undefined ? pluralize(Number(__n), __s) : pluralize(Number(__n), __s, __p));
}
""", ["1 cat\n2 cat\n0 goose geese\n1 goose geese\n-1 point"],
          hints=["A default can use an earlier parameter: `plural = singular + \"s\"`."]),
    _tspf(5, "tsm-w5-duration", "Format a duration two ways", "core",
          "Write `formatDuration(seconds: number, style: \"short\" | \"long\" = \"short\"): string`. Short: the non-zero parts as `1h 2m 5s` (`0s` for zero). Long: `1 hour, 2 minutes, 5 seconds` with correct singulars, again skipping zero parts (`0 seconds` for zero). The driver passes `seconds [style]` per line.",
          r"""
function formatDuration(seconds: number, style: "short" | "long" = "short"): string {
  const parts: [number, string, string][] = [
    [Math.floor(seconds / 3600), "h", "hour"],
    [Math.floor((seconds % 3600) / 60), "m", "minute"],
    [seconds % 60, "s", "second"],
  ];
  const shown = parts.filter(([n]) => n > 0);
  if (shown.length === 0) return style === "short" ? "0s" : "0 seconds";
  return style === "short"
    ? shown.map(([n, unit]) => `${n}${unit}`).join(" ")
    : shown.map(([n, , word]) => `${n} ${word}${n === 1 ? "" : "s"}`).join(", ");
}
""", "  const parts: [number, string, string][] = [\n    [Math.floor(seconds / 3600), \"h\", \"hour\"],\n    [Math.floor((seconds % 3600) / 60), \"m\", \"minute\"],\n    [seconds % 60, \"s\", \"second\"],\n  ];\n  const shown = parts.filter(([n]) => n > 0);\n  if (shown.length === 0) return style === \"short\" ? \"0s\" : \"0 seconds\";\n  return style === \"short\"\n    ? shown.map(([n, unit]) => `${n}${unit}`).join(\" \")\n    : shown.map(([n, , word]) => `${n} ${word}${n === 1 ? \"\" : \"s\"}`).join(\", \");",
          _DRV + r"""
for (const __line of __lines) {
  const [__s = "0", __style] = __line.trim().split(/\s+/);
  console.log(__style === "long" ? formatDuration(Number(__s), "long") : formatDuration(Number(__s)));
}
""", ["3725\n3725 long\n0\n0 long", "61 long\n3600\n7200 long\n59"],
          hints=["Compute hours, minutes and seconds once; decide what to show from the style.",
                 "`\"short\" | \"long\"` as the parameter type means a typo like `\"lng\"` won't compile."]),
    _tspf(5, "tsm-w5-range", "Overloaded `range`", "core",
          "Write `range` with two overloads: `range(end)` gives `0 … end-1`, and `range(start, end, step = 1)` counts from start towards end (exclusive) by step, which may be negative. A step of 0 — or one pointing away from end — gives an empty array. The driver prints each result space-separated, or `(empty)`.",
          r"""
function range(end: number): number[];
function range(start: number, end: number, step?: number): number[];
function range(a: number, b?: number, step = 1): number[] {
  const [start, end] = b === undefined ? [0, a] : [a, b];
  const out: number[] = [];
  if (step === 0) return out;
  for (let i = start; step > 0 ? i < end : i > end; i += step) out.push(i);
  return out;
}
""", "  const [start, end] = b === undefined ? [0, a] : [a, b];\n  const out: number[] = [];\n  if (step === 0) return out;\n  for (let i = start; step > 0 ? i < end : i > end; i += step) out.push(i);\n  return out;",
          _DRV + r"""
for (const __line of __lines) {
  const __n = __line.trim().split(/\s+/).map(Number);
  const __r = __n.length === 1 ? range(__n[0] ?? 0) : range(__n[0] ?? 0, __n[1] ?? 0, __n[2]);
  console.log(__r.join(" ") || "(empty)");
}
""", ["5\n2 6\n10 0 -3\n0 10 4", "0\n3 3\n1 5 0\n5 1"],
          hints=["Normalise the two call shapes to one (start, end) pair first.",
                 "The loop condition flips with the sign of the step."]),
    _tspf(5, "tsm-w5-counter", "A counter object from a closure", "core",
          "Write `makeCounter(start = 0)` returning an object with `inc(by = 1)`, `dec(by = 1)`, `reset()` and `value()`, keeping the count in a closure. `reset` returns to the *starting* value. The driver's first line is the start (or empty); each later line is a command, and it prints `value()` after each one.",
          r"""
function makeCounter(start = 0) {
  let count = start;
  return {
    inc(by = 1) {
      count += by;
    },
    dec(by = 1) {
      count -= by;
    },
    reset() {
      count = start;
    },
    value: () => count,
  };
}
""", "  let count = start;\n  return {\n    inc(by = 1) {\n      count += by;\n    },\n    dec(by = 1) {\n      count -= by;\n    },\n    reset() {\n      count = start;\n    },\n    value: () => count,\n  };",
          _DRV + r"""
const __first = (__lines[0] ?? "").trim();
const __c = __first === "" ? makeCounter() : makeCounter(Number(__first));
for (const __line of __lines.slice(1)) {
  const [__cmd = "", __by] = __line.trim().split(/\s+/);
  const __n = __by === undefined ? undefined : Number(__by);
  if (__cmd === "inc") __c.inc(__n);
  else if (__cmd === "dec") __c.dec(__n);
  else if (__cmd === "reset") __c.reset();
  console.log(__c.value());
}
""", ["10\ninc\ninc 5\ndec 2\nreset\ndec", "0\ninc 3\nreset\ninc"],
          hints=["`count` lives in the factory; every method closes over it.", "Remember `start` too, for `reset`."]),
    _tspf(5, "tsm-w5-limiter", "A sliding-window rate limiter", "stretch",
          "Write `makeLimiter(limit: number, window: number): (time: number) => boolean`. The returned function is called with non-decreasing times; it returns `true` (allowed) if fewer than `limit` calls were allowed in the half-open window `(time - window, time]`, recording the call, and `false` otherwise (a denied call is not recorded). The driver's first line is `limit window`, the second a list of times; it prints `allow`/`deny` for each.",
          r"""
function makeLimiter(limit: number, window: number): (time: number) => boolean {
  const allowed: number[] = [];
  return (time: number) => {
    while (allowed.length > 0 && (allowed[0] ?? 0) <= time - window) allowed.shift();
    if (allowed.length >= limit) return false;
    allowed.push(time);
    return true;
  };
}
""", "  const allowed: number[] = [];\n  return (time: number) => {\n    while (allowed.length > 0 && (allowed[0] ?? 0) <= time - window) allowed.shift();\n    if (allowed.length >= limit) return false;\n    allowed.push(time);\n    return true;\n  };",
          _DRV + r"""
const [__limit = 1, __window = 1] = (__lines[0] ?? "").trim().split(/\s+/).map(Number);
const __ok = makeLimiter(__limit, __window);
const __times = (__lines[1] ?? "").trim().split(/\s+/).map(Number);
console.log(__times.map((t) => (__ok(t) ? "allow" : "deny")).join(" "));
""", ["2 10\n1 2 3 11 12 13", "1 5\n0 4 5 9 10", "3 1\n7 7 7 7 8"],
          hints=["Keep the times of allowed calls in the closure; drop the ones that have left the window first.",
                 "A time exactly `window` ago is outside the half-open window."]),
    _tspf(5, "tsm-w5-memoize", "Memoise, and report hits", "stretch",
          "Write `memoize(fn: (n: number) => number)` returning `{ call(n): number; stats(): string }`. `call` returns the cached result for an argument seen before; `stats` returns `hits=<h> misses=<m>`. The driver wraps a function that counts its own real calls, calls the memo for every number on the line, and prints the results, the stats and the real call count.",
          r"""
function memoize(fn: (n: number) => number) {
  const cache = new Map<number, number>();
  let hits = 0;
  let misses = 0;
  return {
    call(n: number): number {
      const cached = cache.get(n);
      if (cached !== undefined) {
        hits++;
        return cached;
      }
      misses++;
      const value = fn(n);
      cache.set(n, value);
      return value;
    },
    stats: () => `hits=${hits} misses=${misses}`,
  };
}
""", "  const cache = new Map<number, number>();\n  let hits = 0;\n  let misses = 0;\n  return {\n    call(n: number): number {\n      const cached = cache.get(n);\n      if (cached !== undefined) {\n        hits++;\n        return cached;\n      }\n      misses++;\n      const value = fn(n);\n      cache.set(n, value);\n      return value;\n    },\n    stats: () => `hits=${hits} misses=${misses}`,\n  };",
          _DRV + r"""
let __real = 0;
const __m = memoize((n) => {
  __real++;
  return n * n + 1;
});
const __xs = (__lines[0] ?? "").trim().split(/\s+/).map(Number);
console.log(__xs.map((x) => __m.call(x)).join(" "));
console.log(__m.stats());
console.log(`real=${__real}`);
""", ["3 4 3 3 5", "1", "2 2 2 2"],
          hints=["A `Map` in the closure is the cache; two counters beside it are the stats.",
                 "Check the cache with `get` and compare to `undefined` — a cached value could be 0."]),
    _tspf(5, "tsm-w5-args", "Parse command-line flags", "stretch",
          "Write `parseArgs(argv: string[]): { verbose: boolean; level: number; name: string } | string`. Defaults are `false`, `1` and `\"anon\"`. Flags: `--verbose`, `--level=<n>` (an integer 0-5), `--name <value>` (the next token). Anything else returns the error string `bad flag <token>`; a bad level returns `bad level <value>`; `--name` with nothing after it returns `missing name`. The driver prints the result as JSON (the error as a JSON string).",
          r"""
function parseArgs(argv: string[]): { verbose: boolean; level: number; name: string } | string {
  const opts = { verbose: false, level: 1, name: "anon" };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i] ?? "";
    if (token === "--verbose") {
      opts.verbose = true;
    } else if (token.startsWith("--level=")) {
      const text = token.slice("--level=".length);
      const n = Number(text);
      if (!/^\d+$/.test(text) || n > 5) return `bad level ${text}`;
      opts.level = n;
    } else if (token === "--name") {
      const value = argv[i + 1];
      if (value === undefined) return "missing name";
      opts.name = value;
      i++;
    } else {
      return `bad flag ${token}`;
    }
  }
  return opts;
}
""", "  const opts = { verbose: false, level: 1, name: \"anon\" };\n  for (let i = 0; i < argv.length; i++) {\n    const token = argv[i] ?? \"\";\n    if (token === \"--verbose\") {\n      opts.verbose = true;\n    } else if (token.startsWith(\"--level=\")) {\n      const text = token.slice(\"--level=\".length);\n      const n = Number(text);\n      if (!/^\\d+$/.test(text) || n > 5) return `bad level ${text}`;\n      opts.level = n;\n    } else if (token === \"--name\") {\n      const value = argv[i + 1];\n      if (value === undefined) return \"missing name\";\n      opts.name = value;\n      i++;\n    } else {\n      return `bad flag ${token}`;\n    }\n  }\n  return opts;",
          _DRV + r"""
for (const __line of __lines) {
  const __argv = __line.trim() === "" ? [] : __line.trim().split(/\s+/);
  console.log(JSON.stringify(parseArgs(__argv)));
}
""", ["--verbose --level=3 --name ada\n--name\n--level=9\n--level=x\n--fast", "--name bo --verbose\n-v"],
          hints=["Start from the defaults and overwrite them flag by flag.",
                 "`--name` consumes the next token, so advance the index an extra step."]),
]

TS_PROJECTS[5] = _project(
    5, "format.ts — a money formatter with options",
    "Write the kind of function every app ends up with: `formatMoney(cents, options?)`, where each option has a sensible default. The acceptance tests drive it through stdin; the design question is how a caller turns one option on without having to spell out all the others.",
    ["Define `formatMoney(cents: number, options: MoneyOptions = {}): string`, where `MoneyOptions` has optional `symbol` (default `$`), `decimals` (default `true`) and `grouping` (default `true`).",
     "Output is the symbol, then the amount: with `decimals` it has exactly two decimals, without it is rounded to whole units; with `grouping` thousands are separated by commas.",
     "Negative amounts print as `-` then the symbol: `-$1,234.50`.",
     "Each input line is `cents` followed by any of `symbol=<s>`, `decimals=no`, `grouping=no`; print one formatted amount per line.",
     "Use default parameters and destructuring with defaults — no `if (options.symbol === undefined)` chains."],
    r"""
type MoneyOptions = { symbol?: string; decimals?: boolean; grouping?: boolean };

function formatMoney(cents: number, { symbol = "$", decimals = true, grouping = true }: MoneyOptions = {}): string {
  const negative = cents < 0;
  const units = Math.abs(cents) / 100;
  const text = decimals ? units.toFixed(2) : String(Math.round(units));
  const [whole = "0", frac] = text.split(".");
  const grouped = grouping ? whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : whole;
  return `${negative ? "-" : ""}${symbol}${grouped}${frac === undefined ? "" : "." + frac}`;
}

for (const line of input.split("\n")) {
  const [cents = "0", ...flags] = line.trim().split(/\s+/);
  const options: MoneyOptions = {};
  for (const flag of flags) {
    const [key, value = ""] = flag.split("=");
    if (key === "symbol") options.symbol = value;
    else if (key === "decimals") options.decimals = value !== "no";
    else if (key === "grouping") options.grouping = value !== "no";
  }
  console.log(formatMoney(Number(cents), options));
}
""", ["123450", "123450 symbol=€", "123450 decimals=no", "123450 grouping=no symbol=£", "-99", "5", "100000000 decimals=no grouping=no", "-123456789 symbol=¥"],
    stretch=["Add `style: \"accounting\"`, which prints negatives in parentheses: `($1,234.50)`.",
             "Accept a locale and use `Intl.NumberFormat` instead of the hand-written grouping."],
)

TS_PRACTICE_MORE[5] = [
    _pr("tsm-w5-p4", "A default parameter's type", "function pad(text: string, width = 8) {\n  return text.padStart(width);\n}\nconst w = pad;\n", "w", "(text: string, width?: number) => string",
        hints=["A parameter with a default is optional to the caller.", "Its type comes from the default: `number`."]),
    _pr("tsm-w5-p5", "What a factory returns", "function makeCounter() {\n  let n = 0;\n  return () => ++n;\n}\nconst next = makeCounter();\n", "next", "() => number",
        hints=["The factory returns an arrow function.", "It takes nothing and returns the incremented number."]),
    _dx("tsm-w5-d4", "An optional parameter before a required one",
        "error TS1016: A required parameter cannot follow an optional parameter.",
        _STDIN + "function tag(label?: string, value: number) {\n  return `${label ?? \"value\"}=${value}`;\n}\nconsole.log(tag(undefined, Number(input)));\n",
        _STDIN + "function tag(value: number, label?: string) {\n  return `${label ?? \"value\"}=${value}`;\n}\nconsole.log(tag(Number(input)));\n",
        [("7", "value=7")], ask="Reorder the parameters so the call can leave the label out.",
        hints=["Arguments match parameters left to right.", "Put the optional one last."]),
    _dx("tsm-w5-d5", "No overload matches",
        "error TS2769: No overload matches this call.",
        _STDIN + "function show(x: number): string;\nfunction show(x: string): string;\nfunction show(x: number | string): string {\n  return `<${x}>`;\n}\nconst v: number | string = input.length > 3 ? input : input.length;\nconsole.log(show(v));\n",
        _STDIN + "function show(x: number | string): string {\n  return `<${x}>`;\n}\nconst v: number | string = input.length > 3 ? input : input.length;\nconsole.log(show(v));\n",
        [("hello", "<hello>"), ("hi", "<2>")], ask="The return type never depended on the argument — simplify the function so the call compiles.",
        hints=["Neither overload accepts `number | string`.", "One union signature does the job."]),
    _fx("tsm-w5-f3", "Shared state between counters",
        "Each input number creates a fresh counter and calls it that many times, printing the final value. Later counters start where the earlier ones stopped.",
        _STDIN + "let count = 0;\nfunction makeCounter() {\n  return () => ++count;\n}\nfor (const t of input.split(/\\s+/)) {\n  const next = makeCounter();\n  let last = 0;\n  for (let i = 0; i < Number(t); i++) last = next();\n  console.log(last);\n}\n",
        _STDIN + "function makeCounter() {\n  let count = 0;\n  return () => ++count;\n}\nfor (const t of input.split(/\\s+/)) {\n  const next = makeCounter();\n  let last = 0;\n  for (let i = 0; i < Number(t); i++) last = next();\n  console.log(last);\n}\n",
        [("3 2", "3\n2"), ("1 1 1", "1\n1\n1")], hints=["Where does `count` live?", "Move it inside the factory."], difficulty="Medium"),
]

TS_CARDS_MORE[5] = [
    ("Overloads: what do callers see?", "Only the overload signatures. The implementation signature behind them is hidden, so a union argument needs its own overload."),
    ("In what order are overloads matched?", "Top to bottom, first match wins — put the most specific overloads first."),
    ("Overloads or one union signature — how do you decide?", "When the return type doesn't depend on which argument type was passed."),
    ("What does the compiler check about an overloaded function's body?", "Only that it satisfies the implementation signature — not that each branch keeps the matching overload's promise."),
    ("Define a closure in one sentence.", "A function plus the variables of the scope it was written in; it keeps them alive and sees their current values."),
    ("Why do callbacks made in `for (var i …)` all print the same `i`?", "`var` is one function-scoped variable for the whole loop. `let` gives each iteration its own."),
    ("How do you give each counter from `makeCounter()` its own state?", "Declare the state *inside* the factory — each call creates a fresh variable for the returned function to close over."),
    ("A closure reads a variable that changes later. What does it see?", "The current value when it runs, not the value when it was created."),
    ("TS1016?", "\"A required parameter cannot follow an optional parameter\" — optional parameters must come last."),
    ("What is the temporal dead zone?", "The part of a block before a `let`/`const` declaration; reading the variable there throws (TS2448 at compile time)."),
    ("How do you type an options object with defaults in the signature?", "`function f({ a = 1, b = \"x\" }: Options = {})` — destructure with defaults, and default the whole object to `{}`."),
    ("`(x = 5)` — what is the parameter's type inside and outside?", "`number` inside (never undefined); optional (`x?: number`) to callers."),
]

# ===========================================================================
# Week 6 — Higher-order functions and recursion
# ===========================================================================

TS_PROBLEM_SETS[6] = [
    _tsp(6, "tsm-w6-ops", "Apply a pipeline of named operations", "warm-up",
         "The first line is a starting number; the second a list of operation names. Keep a table `Record<string, (n: number) => number>` with `double`, `inc`, `dec`, `square`, `neg` and `half` (halving rounds down). Apply the operations left to right and print the value after each, space-separated. An unknown name prints `unknown <name>` and stops.",
         r"""
const [startText = "0", opsLine = ""] = input.split("\n");
const ops: Record<string, (n: number) => number> = {
  double: (n) => n * 2,
  inc: (n) => n + 1,
  dec: (n) => n - 1,
  square: (n) => n * n,
  neg: (n) => -n,
  half: (n) => Math.floor(n / 2),
};
let value = Number(startText);
const seen: number[] = [];
let unknown = "";
for (const name of opsLine.trim().split(/\s+/)) {
  const op = Object.hasOwn(ops, name) ? ops[name] : undefined;
  if (op === undefined) {
    unknown = name;
    break;
  }
  value = op(value);
  seen.push(value);
}
if (seen.length > 0) console.log(seen.join(" "));
if (unknown !== "") console.log(`unknown ${unknown}`);
""", ["3\ndouble inc square", "10\nhalf half neg dec", "5\ninc cube double", "7\ntoString"],
         hints=["A table of functions replaces an if-chain; `Object.hasOwn` keeps `toString` out."]),
    _tspf(6, "tsm-w6-count-by", "Count with any predicate", "warm-up",
          "Write `countBy(xs: number[], pred: (x: number) => boolean): number`. The driver calls it with four predicates — even, negative, a multiple of 3, and greater than the mean — and prints the four counts.",
          r"""
function countBy(xs: number[], pred: (x: number) => boolean): number {
  let n = 0;
  for (const x of xs) if (pred(x)) n++;
  return n;
}
""", "  let n = 0;\n  for (const x of xs) if (pred(x)) n++;\n  return n;",
          _DRV + r"""
const __xs = (__lines[0] ?? "").trim().split(/\s+/).map(Number);
const __mean = __xs.reduce((a, b) => a + b, 0) / __xs.length;
console.log(
  countBy(__xs, (x) => x % 2 === 0),
  countBy(__xs, (x) => x < 0),
  countBy(__xs, (x) => x % 3 === 0),
  countBy(__xs, (x) => x > __mean),
);
""", ["1 2 3 4 5 6", "-3 -2 0 9", "7"],
          hints=["The predicate is just a function you call on each element."]),
    _tspf(6, "tsm-w6-find-from", "Find, starting somewhere", "warm-up",
          "Write `findIndexFrom(xs: number[], pred: (x: number) => boolean, start = 0): number` returning the first index ≥ start whose element satisfies `pred`, or -1. The driver's first line is the numbers; each later line is `start threshold`, and it searches for the first element greater than the threshold.",
          r"""
function findIndexFrom(xs: number[], pred: (x: number) => boolean, start = 0): number {
  for (let i = Math.max(0, start); i < xs.length; i++) if (pred(xs[i])) return i;
  return -1;
}
""", "  for (let i = Math.max(0, start); i < xs.length; i++) if (pred(xs[i])) return i;\n  return -1;",
          _DRV + r"""
const __xs = (__lines[0] ?? "").trim().split(/\s+/).map(Number);
for (const __q of __lines.slice(1)) {
  const [__start = 0, __t = 0] = __q.trim().split(/\s+/).map(Number);
  console.log(findIndexFrom(__xs, (x) => x > __t, __start));
}
""", ["5 1 8 3 9\n0 4\n3 4\n0 100\n-5 0"],
          hints=["A plain loop from `start`, returning as soon as the predicate holds."]),
    _tsp(6, "tsm-w6-quantifiers", "every, some, none", "warm-up",
         "The input is a line of integers. Print `all even: <bool>`, `any negative: <bool>`, `none zero: <bool>` and `sorted: <bool>` (non-decreasing), using `every` and `some`.",
         r"""
const xs = input.split(/\s+/).map(Number);
console.log(`all even: ${xs.every((x) => x % 2 === 0)}`);
console.log(`any negative: ${xs.some((x) => x < 0)}`);
console.log(`none zero: ${!xs.some((x) => x === 0)}`);
console.log(`sorted: ${xs.every((x, i) => i === 0 || (xs[i - 1] ?? x) <= x)}`);
""", ["2 4 6", "1 -2 0 5", "3 3 7 9", "0"],
         hints=["`every` gets the index too — compare each element with the one before it."]),
    _tsp(6, "tsm-w6-hanoi", "Towers of Hanoi", "core",
         "The input is n (1-10). Print the moves that transfer n disks from peg A to peg C using B, one per line as `disk <d>: <from> -> <to>`, then `<m> moves`.",
         r"""
const moves: string[] = [];
function hanoi(n: number, from: string, to: string, via: string): void {
  if (n === 0) return;
  hanoi(n - 1, from, via, to);
  moves.push(`disk ${n}: ${from} -> ${to}`);
  hanoi(n - 1, via, to, from);
}
hanoi(Number(input), "A", "C", "B");
for (const m of moves) console.log(m);
console.log(`${moves.length} moves`);
""", ["1", "2", "3", "5"],
         hints=["Move n-1 disks out of the way, move the biggest, move the n-1 back on top."]),
    _tsp(6, "tsm-w6-no-11", "Binary strings with no adjacent ones", "core",
         "The input is n (1-15). Print every binary string of length n with no two consecutive `1`s, in increasing order, space-separated, then their count.",
         r"""
const n = Number(input);
const out: string[] = [];
function build(prefix: string): void {
  if (prefix.length === n) {
    out.push(prefix);
    return;
  }
  build(prefix + "0");
  if (!prefix.endsWith("1")) build(prefix + "1");
}
build("");
console.log(out.join(" "));
console.log(out.length);
""", ["1", "3", "4", "12"],
         hints=["Recurse on the prefix: `0` can always follow; `1` only when the prefix doesn't end in `1`.",
                "Trying `0` before `1` produces the strings in increasing order."]),
    _tsp(6, "tsm-w6-json-walk", "Walk any JSON", "core",
         "The input is one JSON value. Recursively visit everything inside it and print `numbers <count> sum <sum>`, `strings <count>`, and `depth <d>` — where a scalar has depth 0 and each array or object adds one level.",
         r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
let numbers = 0;
let sum = 0;
let strings = 0;
function walk(value: Json): number {
  if (typeof value === "number") {
    numbers++;
    sum += value;
    return 0;
  }
  if (typeof value === "string") {
    strings++;
    return 0;
  }
  if (value === null || typeof value === "boolean") return 0;
  const children = Array.isArray(value) ? value : Object.values(value);
  let deepest = 0;
  for (const child of children) deepest = Math.max(deepest, walk(child));
  return deepest + 1;
}
const depth = walk(JSON.parse(input) as Json);
console.log(`numbers ${numbers} sum ${sum}`);
console.log(`strings ${strings}`);
console.log(`depth ${depth}`);
""", ['{"a": 1, "b": [2, "x", {"c": 3}], "d": null}', "42", '[[[]], "s", true]', '{}'],
         hints=["One recursive function can both count and return the depth.",
                "`Array.isArray` first, then objects via `Object.values`."]),
    _tsp(6, "tsm-w6-big-fib", "Fibonacci, memoised and exact", "core",
         "Each input line is n (0-500). Print F(n) exactly (F(0) = 0, F(1) = 1), computed recursively with a memo `Map<number, bigint>` shared across lines. After all lines print `computed <k>` — how many distinct values were computed.",
         r"""
const memo = new Map<number, bigint>();
function fib(n: number): bigint {
  if (n < 2) return BigInt(n);
  const known = memo.get(n);
  if (known !== undefined) return known;
  const value = fib(n - 1) + fib(n - 2);
  memo.set(n, value);
  return value;
}
for (const line of input.split("\n")) console.log(fib(Number(line)).toString());
console.log(`computed ${memo.size}`);
""", ["10\n0\n1", "90\n100", "500\n499"],
         hints=["The memo turns an exponential recursion linear.", "`bigint` keeps F(500)'s 105 digits exact."]),
    _tspf(6, "tsm-w6-pipe", "Build a pipe", "stretch",
          "Write `pipe(...fns: ((s: string) => string)[]): (s: string) => string` returning a function that applies each of `fns` in order. The driver maps names (`trim`, `lower`, `upper`, `squash` — collapse whitespace runs to one space, `reverse`) to functions, builds one pipe from the first line's names and applies it to every later line, printing `[<result>]`.",
          r"""
function pipe(...fns: ((s: string) => string)[]): (s: string) => string {
  return (s) => fns.reduce((acc, fn) => fn(acc), s);
}
""", "return (s) => fns.reduce((acc, fn) => fn(acc), s);",
          _DRV + r"""
const __table: Record<string, (s: string) => string> = {
  trim: (s) => s.trim(),
  lower: (s) => s.toLowerCase(),
  upper: (s) => s.toUpperCase(),
  squash: (s) => s.replace(/\s+/g, " "),
  reverse: (s) => [...s].reverse().join(""),
};
const __names = (__lines[0] ?? "").trim().split(/\s+/);
const __run = pipe(...__names.map((n) => __table[n] ?? ((s: string) => s)));
for (const __l of __lines.slice(1)) console.log(`[${__run(__l)}]`);
""", ["trim squash lower\n  Hello    WORLD  \nA  b", "reverse upper\nabc\nxyz", "trim\n  keep  "],
          hints=["`reduce` over the functions, threading the string through."]),
    _tsp(6, "tsm-w6-unique-perms", "Distinct permutations", "stretch",
         "Each input line is a word (up to 8 letters, possibly repeated). Print its distinct permutations in lexicographic order, space-separated, then their count on the next line. Generate them recursively without building duplicates (don't just deduplicate at the end).",
         r"""
for (const word of input.split("\n")) {
  const counts = new Map<string, number>();
  for (const ch of word.trim()) counts.set(ch, (counts.get(ch) ?? 0) + 1);
  const letters = [...counts.keys()].sort();
  const out: string[] = [];
  const total = word.trim().length;
  function build(prefix: string): void {
    if (prefix.length === total) {
      out.push(prefix);
      return;
    }
    for (const ch of letters) {
      const left = counts.get(ch) ?? 0;
      if (left === 0) continue;
      counts.set(ch, left - 1);
      build(prefix + ch);
      counts.set(ch, left);
    }
  }
  build("");
  console.log(out.join(" "));
  console.log(out.length);
}
""", ["aab\nabc", "zz", "baba\nx"],
         hints=["Count each letter; at every level choose each *distinct* letter that still has copies left.",
                "Iterating the distinct letters in sorted order yields lexicographic output."]),
    _tsp(6, "tsm-w6-debounce", "Debounce on a simulated clock", "stretch",
         "A debounced handler runs only once events stop arriving for `delay` time units: each event resets a timer, and the handler fires `delay` after the last event of a burst, receiving that event's label. The first line is `delay`; each later line is `time label` (times non-decreasing). Print when the handler fires as `<time>: <label>`, one per burst.",
         r"""
const [delayText = "0", ...events] = input.split("\n");
const delay = Number(delayText);
let pendingLabel: string | undefined;
let fireAt = -Infinity;
const fired: string[] = [];
for (const line of events) {
  const [timeText = "0", label = ""] = line.trim().split(/\s+/);
  const time = Number(timeText);
  if (pendingLabel !== undefined && time >= fireAt) fired.push(`${fireAt}: ${pendingLabel}`);
  if (pendingLabel === undefined || time >= fireAt) pendingLabel = undefined;
  pendingLabel = label;
  fireAt = time + delay;
}
if (pendingLabel !== undefined) fired.push(`${fireAt}: ${pendingLabel}`);
console.log(fired.join("\n"));
""", ["10\n0 a\n5 b\n30 c\n39 d\n49 e", "5\n1 x", "3\n0 a\n3 b\n6 c\n9 d"],
         hints=["Keep the pending label and when it would fire; a new event either lands after that moment (the old burst fired) or resets it.",
                "An event exactly at the fire time arrives too late to cancel it."]),
]

TS_PROJECTS[6] = _project(
    6, "pipeline.ts — a text-cleaning pipeline",
    "Build a `pipe` helper and a table of small string transforms, then let the input choose the pipeline. Every step is a function; the program is just composition — which is the point of the week.",
    ["The first input line names the steps, in order; every later line is text to push through them.",
     "Provide the steps `trim`, `lower`, `upper`, `squash` (whitespace runs to one space), `strip` (remove anything that isn't a letter, digit or space), `slug` (lowercase words joined by `-`) and `title` (capitalise each word).",
     "Write `pipe(...steps)` yourself — no library — and build the pipeline once, before processing the lines.",
     "If any step name is unknown, print `unknown step <name>` and nothing else.",
     "Print each transformed line between square brackets, so leading and trailing spaces are visible."],
    r"""
type Step = (s: string) => string;
function pipe(...steps: Step[]): Step {
  return (s) => steps.reduce((acc, step) => step(acc), s);
}
const steps: Record<string, Step> = {
  trim: (s) => s.trim(),
  lower: (s) => s.toLowerCase(),
  upper: (s) => s.toUpperCase(),
  squash: (s) => s.replace(/\s+/g, " "),
  strip: (s) => s.replace(/[^\p{L}\p{N} ]/gu, ""),
  slug: (s) => s.toLowerCase().trim().split(/\s+/).filter((w) => w !== "").join("-"),
  title: (s) => s.replace(/\p{L}+/gu, (w) => w[0].toUpperCase() + w.slice(1).toLowerCase()),
};
const [header = "", ...lines] = input.split("\n");
const names = header.trim().split(/\s+/);
const unknown = names.find((n) => !Object.hasOwn(steps, n));
if (unknown !== undefined) {
  console.log(`unknown step ${unknown}`);
} else {
  const run = pipe(...names.map((n) => steps[n]));
  for (const line of lines) console.log(`[${run(line)}]`);
}
""", ["trim squash\n   hello    there   \nok", "strip squash trim lower slug\nHello, World! 2026\n  Type--Script  rocks!!", "title\nthe QUICK brown fox", "trim nope upper\nx", "upper\n\nabc"],
    stretch=["Add parameterised steps, like `truncate:10` or `replace:a:b`.",
             "Type `pipe` so each step can change the type (`string` → `string[]` → `number`) — you'll have the tools in week 18."],
)

TS_PRACTICE_MORE[6] = [
    _pr("tsm-w6-p4", "A callback's parameter", "const doubled = [1, 2, 3].map((n) => n * 2);\n", "doubled", "number[]",
        hints=["`map` returns an array of whatever the callback returns."]),
    _pr("tsm-w6-p5", "A function returning a function", "const add = (a: number) => (b: number) => a + b;\nconst addTwo = add(2);\n", "addTwo", "(b: number) => number",
        hints=["`add(2)` returns the inner arrow."]),
    _dx("tsm-w6-d4", "A recursive function without a return type",
        "error TS7023: 'sum' implicitly has return type 'any' because it does not have a return type annotation and is referenced directly or indirectly in one of its return expressions.",
        _STDIN + "function sum(xs: number[]) {\n  return xs.length === 0 ? 0 : (xs[0] ?? 0) + sum(xs.slice(1));\n}\nconsole.log(sum(input.split(/\\s+/).map(Number)));\n",
        _STDIN + "function sum(xs: number[]): number {\n  return xs.length === 0 ? 0 : (xs[0] ?? 0) + sum(xs.slice(1));\n}\nconsole.log(sum(input.split(/\\s+/).map(Number)));\n",
        [("1 2 3", "6"), ("10", "10")], hints=["The return type depends on itself.", "Annotate it: `: number`."]),
    _fx("tsm-w6-f3", "parseInt as a callback",
        "Convert every token to an integer and print their sum. It's wrong for most inputs.",
        _STDIN + "const values = input.split(/\\s+/).map(parseInt);\nconsole.log(values.reduce((a, b) => a + b, 0));\n",
        _STDIN + "const values = input.split(/\\s+/).map((t) => parseInt(t, 10));\nconsole.log(values.reduce((a, b) => a + b, 0));\n",
        [("10 10 10", "30"), ("1 2 3", "6")], hints=["`map` passes the index as the second argument.", "`parseInt`'s second parameter is the radix."]),
    _fx("tsm-w6-f4", "A base case that isn't reached",
        "Print the digit sum of each (possibly negative) integer. Negative inputs crash.",
        _STDIN + "function digitSum(n: number): number {\n  if (n === 0) return 0;\n  return (n % 10) + digitSum(Math.floor(n / 10));\n}\nfor (const t of input.split(/\\s+/)) console.log(digitSum(Number(t)));\n",
        _STDIN + "function digitSum(n: number): number {\n  if (n < 0) return digitSum(-n);\n  if (n === 0) return 0;\n  return (n % 10) + digitSum(Math.floor(n / 10));\n}\nfor (const t of input.split(/\\s+/)) console.log(digitSum(Number(t)));\n",
        [("123 -45", "6\n9"), ("0 -7", "0\n7")], hints=["`Math.floor(-4.5)` is `-5` — the recursion runs away from zero.", "Handle negatives by recursing on `-n`."], difficulty="Medium"),
]

TS_CARDS_MORE[6] = [
    ("The two parts every recursive function needs?", "A base case that answers directly, and a step that recurses on a strictly smaller input."),
    ("What limits recursion depth in Node?", "The call stack — about ten thousand frames; past it you get `RangeError: Maximum call stack size exceeded`."),
    ("Why annotate a recursive function's return type?", "Inference can go circular (TS7023) — and the annotation documents the contract."),
    ("How does memoisation change recursion with overlapping subproblems?", "Caching each result by its argument the first time it's computed, so overlapping subproblems are solved once."),
    ("When should recursion become a loop?", "When it's linear (one call per level) and the depth can be large — a loop has no stack limit."),
    ("Backtracking with a shared array: what must you push into the results?", "A copy (`[...current]`) — the shared array keeps changing as the search backtracks."),
]

# ===========================================================================
# Week 7 — Arrays, array methods, tuples and the modern array toolkit
# ===========================================================================

TS_PROBLEM_SETS[7] = [
    _tsp(7, "tsm-w7-chunk", "Chunk an array", "warm-up",
         "The first line is the chunk size k; the second a list of values. Print the values in chunks of k, one chunk per line (the last may be shorter).",
         r"""
const [kText = "1", line = ""] = input.split("\n");
const k = Number(kText);
const xs = line.trim().split(/\s+/);
for (let i = 0; i < xs.length; i += k) console.log(xs.slice(i, i + k).join(" "));
""", ["2\na b c d e", "3\n1 2 3", "10\nx y"],
         hints=["Step the start index by k and `slice(i, i + k)`."]),
    _tsp(7, "tsm-w7-zip", "Zip two lists", "warm-up",
         "Two lines of values. Pair them up position by position as `a:b`, stopping at the shorter list, then print `<n> pairs, <m> left over`.",
         r"""
const [first = "", second = ""] = input.split("\n");
const a = first.trim().split(/\s+/);
const b = second.trim().split(/\s+/);
const n = Math.min(a.length, b.length);
const pairs = Array.from({ length: n }, (_, i): [string, string] => [a[i], b[i]]);
console.log(pairs.map(([x, y]) => `${x}:${y}`).join(" "));
console.log(`${n} pairs, ${Math.max(a.length, b.length) - n} left over`);
""", ["a b c\n1 2 3", "x y z w\n1 2", "solo\nmany more here"],
         hints=["`Array.from({ length: n }, …)` builds the pairs as tuples."]),
    _tsp(7, "tsm-w7-rotate", "Rotate left by k", "warm-up",
         "The first line is k (may be larger than the length, or negative for a right rotation); the second a list. Print the list rotated left by k.",
         r"""
const [kText = "0", line = ""] = input.split("\n");
const xs = line.trim().split(/\s+/);
const n = xs.length;
const k = ((Number(kText) % n) + n) % n;
console.log([...xs.slice(k), ...xs.slice(0, k)].join(" "));
""", ["2\n1 2 3 4 5", "7\na b c", "-1\n1 2 3 4", "0\nz"],
         hints=["Normalise k into 0…n-1 with a double modulo, then concatenate two slices."]),
    _tsp(7, "tsm-w7-dedupe", "Remove duplicates, keep the order", "warm-up",
         "Print the distinct values in order of first appearance, then `<k> removed`.",
         r"""
const xs = input.split(/\s+/);
const unique = [...new Set(xs)];
console.log(unique.join(" "));
console.log(`${xs.length - unique.length} removed`);
""", ["3 1 3 2 1", "a a a", "x y z"],
         hints=["A `Set` keeps insertion order."]),
    _tsp(7, "tsm-w7-diffs", "Consecutive differences", "core",
         "Print the differences between consecutive numbers, then `increasing`, `decreasing`, `constant` or `mixed` — strictly increasing, strictly decreasing, all equal, or none of those. A single number prints `(none)` then `constant`.",
         r"""
const xs = input.split(/\s+/).map(Number);
const diffs = xs.slice(1).map((x, i) => x - (xs[i] ?? 0));
console.log(diffs.join(" ") || "(none)");
if (diffs.every((d) => d === 0)) console.log("constant");
else if (diffs.every((d) => d > 0)) console.log("increasing");
else if (diffs.every((d) => d < 0)) console.log("decreasing");
else console.log("mixed");
""", ["1 3 6 10", "9 7 7", "5 5 5", "4", "10 5 1"],
         hints=["`xs.slice(1).map((x, i) => x - xs[i])` pairs each element with the one before it."]),
    _tsp(7, "tsm-w7-transpose", "Transpose a matrix", "core",
         "Each input line is a row of a rectangular matrix. Print its transpose, one row per line.",
         r"""
const rows = input.split("\n").map((line) => line.trim().split(/\s+/));
const cols = rows[0]?.length ?? 0;
const transposed = Array.from({ length: cols }, (_, c) => rows.map((row) => row[c] ?? ""));
for (const row of transposed) console.log(row.join(" "));
""", ["1 2 3\n4 5 6", "a\nb\nc", "7"],
         hints=["Column c of the input becomes row c of the output: `rows.map(row => row[c])`."]),
    _tsp(7, "tsm-w7-group-length", "Group words by length", "core",
         "Group the words by length with `Object.groupBy`. Print one line per length, shortest first: `<length>: <words in input order>`, then the length with the most words (the shortest on a tie).",
         r"""
const words = input.split(/\s+/);
const groups = Object.groupBy(words, (w) => w.length);
const lengths = Object.keys(groups).map(Number).toSorted((a, b) => a - b);
let best = 0;
let bestSize = -1;
for (const len of lengths) {
  const group = groups[len] ?? [];
  console.log(`${len}: ${group.join(" ")}`);
  if (group.length > bestSize) {
    best = len;
    bestSize = group.length;
  }
}
console.log(best);
""", ["the cat sat on a big mat", "hello", "aa b cc d eee"],
         hints=["`Object.groupBy` keys are property keys; turn them back into numbers to sort numerically."]),
    _tsp(7, "tsm-w7-two-keys", "Sort by two keys", "core",
         "Each input line is `name score`. Print the records sorted by score descending, then by name ascending, as `name score`; then the original first line unchanged, to prove the input wasn't reordered.",
         r"""
const records = input.split("\n").map((line): [string, number] => {
  const [name = "", score = "0"] = line.trim().split(/\s+/);
  return [name, Number(score)];
});
const sorted = records.toSorted((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
for (const [name, score] of sorted) console.log(`${name} ${score}`);
console.log(`first was ${records[0]?.[0]}`);
""", ["cy 80\nada 95\nbo 80\nal 95", "solo 1", "b 1\na 1\nc 2"],
         hints=["`b[1] - a[1] || a[0].localeCompare(b[0])` — the second key only matters when the first ties.",
                "`toSorted` leaves `records` in input order."]),
    _tsp(7, "tsm-w7-dense-rank", "Top scores with dense ranking", "core",
         "The first line is n; the second a list of scores. Print the top n *distinct* scores with their dense rank (equal scores share a rank; the next rank is one more) as `#<rank> <score> (x<count>)`, highest first.",
         r"""
const [nText = "0", line = ""] = input.split("\n");
const scores = line.trim().split(/\s+/).map(Number);
const counts = new Map<number, number>();
for (const s of scores) counts.set(s, (counts.get(s) ?? 0) + 1);
const distinct = [...counts.keys()].toSorted((a, b) => b - a).slice(0, Number(nText));
distinct.forEach((score, i) => console.log(`#${i + 1} ${score} (x${counts.get(score) ?? 0})`));
""", ["3\n90 85 90 70 85 60", "10\n5 5 5", "1\n-1 -3 -2"],
         hints=["Count each score, sort the distinct scores descending, take n."]),
    _tsp(7, "tsm-w7-interleave", "Round-robin interleave", "stretch",
         "Each input line is a list. Interleave them round-robin — first item of each list, then second of each, and so on, skipping lists that have run out. Print the result, then the length of the longest list.",
         r"""
const lists = input.split("\n").map((line) => line.trim().split(/\s+/).filter((t) => t !== ""));
const longest = Math.max(...lists.map((l) => l.length));
const out: string[] = [];
for (let i = 0; i < longest; i++) {
  for (const list of lists) {
    const item = list.at(i);
    if (item !== undefined) out.push(item);
  }
}
console.log(out.join(" "));
console.log(longest);
""", ["a b c\n1 2\nx y z w", "only\nlist", "1 2 3"],
         hints=["The outer loop is the position; the inner loop visits each list."]),
    _tsp(7, "tsm-w7-spiral", "Spiral order", "stretch",
         "Each input line is a row of a rectangular matrix. Print its elements in clockwise spiral order from the top-left, space-separated.",
         r"""
const grid = input.split("\n").map((line) => line.trim().split(/\s+/));
let top = 0;
let bottom = grid.length - 1;
let left = 0;
let right = (grid[0]?.length ?? 0) - 1;
const out: string[] = [];
const at = (r: number, c: number) => grid[r]?.[c] ?? "";
while (top <= bottom && left <= right) {
  for (let c = left; c <= right; c++) out.push(at(top, c));
  for (let r = top + 1; r <= bottom; r++) out.push(at(r, right));
  if (top < bottom) for (let c = right - 1; c >= left; c--) out.push(at(bottom, c));
  if (left < right) for (let r = bottom - 1; r > top; r--) out.push(at(r, left));
  top++;
  bottom--;
  left++;
  right--;
}
console.log(out.join(" "));
""", ["1 2 3\n4 5 6\n7 8 9", "1 2 3 4\n5 6 7 8\n9 10 11 12", "1\n2\n3", "a b c"],
         hints=["Four walls — top, right, bottom, left — shrinking after each lap.",
                "Guard the bottom and left passes when a single row or column is left."]),
]

TS_PROJECTS[7] = _project(
    7, "table.ts — an aligned, sortable table",
    "Render records as a text table — the kind a CLI prints. Arrays of tuples hold the rows, the copying methods sort them without disturbing the input, and column widths come from one pass over the data.",
    ["The first line is `sort <column> asc|desc`; the second is the header, columns separated by commas; each later line is a row with the same number of comma-separated cells.",
     "Sort the rows by the named column (numerically if every cell in it is a number, otherwise with `localeCompare`), keeping the original order for ties. An unknown column prints `no column <name>` and nothing else.",
     "Print the header, a separator of `-` characters under each column, and the rows. Columns are padded to their widest cell and separated by ` | `; numeric columns are right-aligned, the rest left-aligned.",
     "Finally print `<n> rows`. Don't mutate the parsed rows while sorting."],
    r"""
const [command = "", header = "", ...rest] = input.split("\n");
const [, column = "", direction = "asc"] = command.trim().split(/\s+/);
const columns = header.split(",").map((c) => c.trim());
const rows = rest.map((line) => line.split(",").map((c) => c.trim()));
const index = columns.indexOf(column);
if (index < 0) {
  console.log(`no column ${column}`);
} else {
  const numeric = columns.map((_, c) => rows.every((r) => r[c] !== undefined && r[c] !== "" && !Number.isNaN(Number(r[c]))));
  const sign = direction === "desc" ? -1 : 1;
  const sorted = rows.toSorted((a, b) => {
    const x = a[index] ?? "";
    const y = b[index] ?? "";
    return sign * (numeric[index] ? Number(x) - Number(y) : x.localeCompare(y));
  });
  const widths = columns.map((name, c) => Math.max(name.length, ...rows.map((r) => (r[c] ?? "").length)));
  const cell = (text: string, c: number) =>
    numeric[c] ? text.padStart(widths[c] ?? 0) : text.padEnd(widths[c] ?? 0);
  const line = (cells: string[]) => cells.map((t, c) => cell(t, c)).join(" | ").trimEnd();
  console.log(line(columns));
  console.log(widths.map((w) => "-".repeat(w)).join("-+-"));
  for (const r of sorted) console.log(line(r));
  console.log(`${rows.length} rows`);
}
""", ["sort score desc\nname,score,city\nada,95,London\nbo,80,Oslo\ncy,95,Paris",
      "sort name asc\nname,qty\npear,3\napple,12\nfig,7",
      "sort city asc\nname,city\nx,Zurich\ny,Athens\nz,Zurich",
      "sort nope asc\na,b\n1,2",
      "sort n desc\nn\n10\n9\n100"],
    stretch=["Support `sort <col1>,<col2>` for a tie-breaking second key.",
             "Truncate cells wider than 20 characters with `…`, counting graphemes."],
)

TS_PRACTICE_MORE[7] = [
    _pr("tsm-w7-p4", "An array literal", 'const pair = [1, "a"];\n', "pair", "(string | number)[]",
        hints=["Array literals infer arrays, not tuples."]),
    _pr("tsm-w7-p5", "A copying sort", "const xs = [3, 1, 2];\nconst sorted = xs.toSorted();\n", "sorted", "number[]",
        hints=["`toSorted` returns a new array of the same element type."]),
    _pr("tsm-w7-p6", "Reading from the end", "const xs = [3, 1, 2];\nconst last = xs.at(-1);\n", "last", "number | undefined",
        hints=["`at` may be given an index that's out of range."]),
    _dx("tsm-w7-d4", "An index past the end of a tuple",
        "error TS2493: Tuple type '[string, number]' of length '2' has no element at index '2'.",
        _STDIN + 'const [name = "", age = "0"] = input.split(/\\s+/);\nconst person: [string, number] = [name, Number(age)];\nconsole.log(`${person[0]} ${person[2]}`);\n',
        _STDIN + 'const [name = "", age = "0"] = input.split(/\\s+/);\nconst person: [string, number] = [name, Number(age)];\nconsole.log(`${person[0]} ${person[1]}`);\n',
        [("ada 36", "ada 36")], ask="Print the name and the age.", hints=["A two-element tuple has indexes 0 and 1."]),
    _fx("tsm-w7-f3", "The sort that changed the input",
        "Print the median, then the input in its original order. The original order comes out sorted.",
        _STDIN + "const xs = input.split(/\\s+/).map(Number);\nconst sorted = xs.sort((a, b) => a - b);\nconsole.log(sorted[Math.floor(sorted.length / 2)]);\nconsole.log(xs.join(\" \"));\n",
        _STDIN + "const xs = input.split(/\\s+/).map(Number);\nconst sorted = xs.toSorted((a, b) => a - b);\nconsole.log(sorted[Math.floor(sorted.length / 2)]);\nconsole.log(xs.join(\" \"));\n",
        [("3 1 2", "2\n3 1 2"), ("9 7 8 1 5", "7\n9 7 8 1 5")], hints=["`sort` works in place.", "`toSorted` returns a copy."]),
    _fx("tsm-w7-f4", "Numbers sorted as text",
        "Print the numbers in ascending order.",
        _STDIN + "console.log(input.split(/\\s+/).map(Number).toSorted().join(\" \"));\n",
        _STDIN + "console.log(input.split(/\\s+/).map(Number).toSorted((a, b) => a - b).join(\" \"));\n",
        [("10 9 1 100", "1 9 10 100"), ("3 2 1", "1 2 3")], hints=["Without a comparator, sorting compares strings."]),
]

TS_CARDS_MORE[7] = [
    ("How do you make an array literal a tuple?", "Annotate it (or the function's return type), or use `as const` for a readonly literal tuple."),
    ("Why return `readonly [number, number]` rather than `[number, number]`?", "A mutable tuple still allows `push`, which breaks the length its type promises."),
    ("What does `[name: string, ...scores: number[]]` describe?", "A string followed by any number of numbers — a tuple with a rest element."),
    ("TS2493?", "\"Tuple type … has no element at index n\" — reading past a tuple's fixed length."),
    ("What is each element of `Object.entries(obj)`?", "A `[key, value]` tuple."),
    ("`sort` vs `toSorted`?", "`sort` rearranges the array in place; `toSorted` returns a sorted copy. Both compare as strings without a comparator."),
    ("How do you read the last element safely?", "`xs.at(-1)`, which is `T | undefined` — handle the empty case with `?? fallback`."),
    ("Why doesn't `new Array(3).map((_, i) => i)` work?", "The array is three holes, and `map` skips holes. Use `Array.from({ length: 3 }, (_, i) => i)`."),
    ("What does `Object.groupBy(xs, f)` return?", "An object from each key `f` produced to the array of items with that key (each group typed as possibly `undefined`)."),
    ("`with(i, v)` does what?", "Returns a copy of the array with index `i` replaced by `v` — the non-mutating `xs[i] = v`."),
    ("Spread vs `structuredClone`?", "Spread copies one level, so nested objects stay shared; `structuredClone` copies all the way down."),
    ("When is `flatMap` the right tool?", "Maps each element to an array and flattens the results one level — \"each item gives zero or more outputs\"."),
]

# ===========================================================================
# Week 8 — Destructuring, objects, JSON, interfaces and index signatures
# ===========================================================================

# Records in these problems are untyped JSON, so the solutions read them as
# `Record<string, unknown>` (or a narrower shape) and check before using.
_JSON_OBJ = "type Obj = { [key: string]: unknown };\nconst isObj = (v: unknown): v is Obj => typeof v === \"object\" && v !== null && !Array.isArray(v);\n"

TS_PROBLEM_SETS[8] = [
    _tsp(8, "tsm-w8-pick", "Pick fields", "warm-up",
         "The first line is a list of field names; each later line is a JSON object. Print each object reduced to just those fields (in the listed order, skipping fields it doesn't have), as compact JSON.",
         r"""
const [fieldLine = "", ...records] = input.split("\n");
const fields = fieldLine.trim().split(/\s+/);
for (const line of records) {
  const record = JSON.parse(line) as Record<string, unknown>;
  const picked: Record<string, unknown> = {};
  for (const f of fields) if (Object.hasOwn(record, f)) picked[f] = record[f];
  console.log(JSON.stringify(picked));
}
""", ['name id\n{"id":1,"name":"ada","age":36}\n{"name":"bo"}', 'x\n{"y":1}', 'b a\n{"a":1,"b":[2],"c":3}'],
         hints=["`Object.hasOwn` tells a missing field from one that holds `undefined` or `null`."]),
    _tsp(8, "tsm-w8-invert", "Invert an object", "warm-up",
         "The input is a JSON object whose values are strings. Print the inverted object — values become keys, keys become values — with the keys sorted. When two keys share a value, the one that appears later wins. Then print how many keys were lost to collisions.",
         r"""
const original = JSON.parse(input) as Record<string, string>;
const inverted: Record<string, string> = {};
for (const [key, value] of Object.entries(original)) inverted[value] = key;
const sorted = Object.fromEntries(Object.entries(inverted).sort(([a], [b]) => a.localeCompare(b)));
console.log(JSON.stringify(sorted));
console.log(Object.keys(original).length - Object.keys(inverted).length);
""", ['{"a":"x","b":"y","c":"x"}', '{"one":"1","two":"2"}', '{}'],
         hints=["`Object.entries` then `Object.fromEntries` — sort the entries in between."]),
    _tsp(8, "tsm-w8-count-by-key", "Count by a field", "warm-up",
         "The first line is a field name; the second a JSON array of objects. Count the objects by the value of that field (as a string; missing becomes `(missing)`). Print `value: count` lines sorted by count descending, then value ascending — or `(none)` for an empty array.",
         r"""
const [field = "", json = "[]"] = input.split("\n");
const items = JSON.parse(json) as Record<string, unknown>[];
const counts: Record<string, number> = Object.create(null);
for (const item of items) {
  const key = Object.hasOwn(item, field) ? String(item[field]) : "(missing)";
  counts[key] = (counts[key] ?? 0) + 1;
}
const rows = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
for (const [value, n] of rows) console.log(`${value}: ${n}`);
if (rows.length === 0) console.log("(none)");
""", ['city\n[{"city":"Oslo"},{"city":"Rome"},{"city":"Oslo"},{"name":"x"}]', 'active\n[{"active":true},{"active":false},{"active":true}]', 'k\n[]'],
         hints=["A dictionary with no prototype is safe for any field value; default missing counts to 0."]),
    _tsp(8, "tsm-w8-rename", "Rename keys", "warm-up",
         "The first line is a list of renames `old=new`; the second a JSON object. Print the object with those keys renamed (other keys unchanged, key order preserved).",
         r"""
const [renameLine = "", json = "{}"] = input.split("\n");
const renames = new Map(renameLine.trim().split(/\s+/).map((pair): [string, string] => {
  const [from = "", to = ""] = pair.split("=");
  return [from, to];
}));
const source = JSON.parse(json) as Record<string, unknown>;
const renamed = Object.fromEntries(Object.entries(source).map(([k, v]) => [renames.get(k) ?? k, v]));
console.log(JSON.stringify(renamed));
""", ['fname=first lname=last\n{"fname":"Ada","lname":"L","age":36}', 'x=y\n{"a":1}', 'a=b\n{"a":1,"c":[1,2]}'],
         hints=["Map each entry's key through the rename table, defaulting to itself."]),
    _tsp(8, "tsm-w8-query", "Object to query string", "core",
         "The input is a JSON object with string, number, boolean, null or array values. Build a URL query string: keys sorted, each `key=value` percent-encoded with `encodeURIComponent`, arrays as repeated keys, `null` values skipped, joined with `&`. Print it, or `(empty)`.",
         r"""
const params = JSON.parse(input) as Record<string, string | number | boolean | null | (string | number)[]>;
const parts: string[] = [];
for (const key of Object.keys(params).sort()) {
  const value = params[key];
  if (value === null || value === undefined) continue;
  const values = Array.isArray(value) ? value : [value];
  for (const v of values) parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(v))}`);
}
console.log(parts.join("&") || "(empty)");
""", ['{"q":"type script","page":2,"tags":["a","b&c"],"debug":null}', '{}', '{"z":true,"a b":"x=y"}'],
         hints=["Normalise every value to an array, then encode each pair."]),
    _tsp(8, "tsm-w8-flatten", "Flatten nested JSON", "core",
         "The input is a JSON object that may contain nested objects and arrays. Print every leaf as `path = value` (compact JSON for the value), paths using `.` for object keys and `[i]` for array indexes, sorted by path. An empty object or array is itself a leaf.",
         _JSON_OBJ + r"""
const leaves: [string, string][] = [];
function walk(value: unknown, path: string): void {
  if (Array.isArray(value) && value.length > 0) {
    value.forEach((item, i) => walk(item, `${path}[${i}]`));
  } else if (isObj(value) && Object.keys(value).length > 0) {
    for (const [key, child] of Object.entries(value)) walk(child, path === "" ? key : `${path}.${key}`);
  } else {
    leaves.push([path, JSON.stringify(value)]);
  }
}
walk(JSON.parse(input), "");
for (const [path, value] of leaves.toSorted((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))) {
  console.log(`${path} = ${value}`);
}
""", ['{"a":{"b":1,"c":[true,{"d":null}]},"e":"x"}', '{"k":{},"l":[]}', '{"z":1,"a":{"y":2}}'],
         hints=["Recurse into non-empty arrays and objects, extending the path; everything else is a leaf.",
                "Sort with a plain code-unit comparison so `a[1]` and `a.b` order predictably."]),
    _tsp(8, "tsm-w8-unflatten", "Unflatten paths", "core",
         "Each input line is `dotted.path=value`. Build the nested object they describe (the value is parsed as JSON if possible, otherwise kept as a string) and print it as JSON with two-space indentation. A path that tries to descend into a non-object prints `conflict at <path>` and is skipped.",
         _JSON_OBJ + r"""
const root: Obj = {};
for (const line of input.split("\n")) {
  const eq = line.indexOf("=");
  const path = line.slice(0, eq).trim();
  const raw = line.slice(eq + 1).trim();
  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    value = raw;
  }
  const keys = path.split(".");
  let node: Obj = root;
  let ok = true;
  for (const key of keys.slice(0, -1)) {
    const next = node[key];
    if (next === undefined) {
      const created: Obj = {};
      node[key] = created;
      node = created;
    } else if (isObj(next)) {
      node = next;
    } else {
      ok = false;
      break;
    }
  }
  if (ok) node[keys[keys.length - 1] ?? ""] = value;
  else console.log(`conflict at ${path}`);
}
console.log(JSON.stringify(root, null, 2));
""", ["a.b=1\na.c=true\nd=hello", "x.y.z=[1,2]\nx.y.w=null", "a=1\na.b=2\nc.d=\"quoted\""],
         hints=["Walk the path, creating objects as you go; the last key gets the value.",
                "`JSON.parse` throws on plain text — catch it and keep the string."]),
    _tsp(8, "tsm-w8-diff", "Diff two objects", "core",
         "The input is two JSON objects on two lines (flat: values are scalars). Print the differences sorted by key: `+ key: value` for added, `- key: value` for removed, `~ key: old -> new` for changed (values as compact JSON). Print `no changes` if they are equal.",
         r"""
const [left = "{}", right = "{}"] = input.split("\n");
const a = JSON.parse(left) as Record<string, unknown>;
const b = JSON.parse(right) as Record<string, unknown>;
const keys = [...new Set([...Object.keys(a), ...Object.keys(b)])].sort();
const out: string[] = [];
for (const key of keys) {
  const inA = Object.hasOwn(a, key);
  const inB = Object.hasOwn(b, key);
  const va = JSON.stringify(a[key]);
  const vb = JSON.stringify(b[key]);
  if (!inA) out.push(`+ ${key}: ${vb}`);
  else if (!inB) out.push(`- ${key}: ${va}`);
  else if (va !== vb) out.push(`~ ${key}: ${va} -> ${vb}`);
}
console.log(out.join("\n") || "no changes");
""", ['{"a":1,"b":2,"c":3}\n{"a":1,"b":20,"d":4}', '{"x":null}\n{"x":null}', '{}\n{"k":"v"}', '{"n":1}\n{"n":"1"}'],
         hints=["Take the union of keys, then decide added / removed / changed per key.",
                "Compare `JSON.stringify` of each value so `1` and `\"1\"` differ."]),
    _tsp(8, "tsm-w8-get", "Nested get with a default", "core",
         "The first line is a JSON document. Each later line is `path | default`, where the path uses `.key` and `[index]` (e.g. `users[0].name`). Print the value at the path as compact JSON, or the default text if any step is missing.",
         _JSON_OBJ + r"""
const [doc = "null", ...queries] = input.split("\n");
const data: unknown = JSON.parse(doc);
function get(value: unknown, path: string): unknown {
  const steps = path.match(/[^.[\]]+/g) ?? [];
  let node = value;
  for (const step of steps) {
    if (Array.isArray(node) && /^\d+$/.test(step)) node = node[Number(step)];
    else if (isObj(node) && Object.hasOwn(node, step)) node = node[step];
    else return undefined;
  }
  return node;
}
for (const q of queries) {
  const [path = "", fallback = ""] = q.split("|").map((s) => s.trim());
  const found = get(data, path);
  console.log(found === undefined ? fallback : JSON.stringify(found));
}
""", ['{"users":[{"name":"ada","tags":["x"]},{"name":"bo"}]}\nusers[0].name | ?\nusers[1].tags[0] | none\nusers[5] | out of range\nusers | -',
      '[1,[2,3]]\n[1][0] | ?\n[0].x | no'],
         hints=["Split the path into steps with a regex; walk them, checking arrays and objects separately."]),
    _tsp(8, "tsm-w8-deep-merge", "Deep-merge two configs", "stretch",
         "The input is two JSON objects: defaults, then overrides. Merge them: where both hold objects, merge recursively; otherwise the override wins — except `null`, which deletes the key. Arrays are replaced, not merged. Print the result as JSON with keys sorted at every level and two-space indentation.",
         _JSON_OBJ + r"""
const [defaultsText = "{}", overridesText = "{}"] = input.split("\n");
function merge(base: Obj, over: Obj): Obj {
  const out: Obj = { ...base };
  for (const [key, value] of Object.entries(over)) {
    const current = out[key];
    if (value === null) delete out[key];
    else if (isObj(current) && isObj(value)) out[key] = merge(current, value);
    else out[key] = value;
  }
  return out;
}
function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (!isObj(value)) return value;
  return Object.fromEntries(Object.keys(value).sort().map((k) => [k, sortKeys(value[k])]));
}
const merged = merge(JSON.parse(defaultsText) as Obj, JSON.parse(overridesText) as Obj);
console.log(JSON.stringify(sortKeys(merged), null, 2));
""", ['{"server":{"port":80,"host":"x"},"debug":false,"tags":["a"]}\n{"server":{"port":8080},"tags":["b","c"]}',
      '{"a":1,"b":{"c":2}}\n{"b":null,"d":{"e":3}}',
      '{}\n{}'],
         hints=["Recurse only when *both* sides are plain objects.", "Sort keys in a separate pass so merging stays simple."]),
    _tsp(8, "tsm-w8-validate", "Validate records against a schema", "stretch",
         "The first line is a schema of `field:type` entries (`string`, `number`, `boolean`), where a `?` after the field name makes it optional (`email?:string`). Each later line is a JSON record. Print `ok` or the problems joined by `; ` — `missing <f>`, `<f> should be <type>`, and `unexpected <f>` for fields not in the schema, in schema order then record order.",
         r"""
const [schemaLine = "", ...records] = input.split("\n");
type Field = { name: string; type: string; optional: boolean };
const schema: Field[] = schemaLine.trim().split(/\s+/).map((entry) => {
  const [rawName = "", type = ""] = entry.split(":");
  const optional = rawName.endsWith("?");
  return { name: optional ? rawName.slice(0, -1) : rawName, type, optional };
});
const known = new Set(schema.map((f) => f.name));
for (const line of records) {
  const record = JSON.parse(line) as Record<string, unknown>;
  const problems: string[] = [];
  for (const f of schema) {
    if (!Object.hasOwn(record, f.name)) {
      if (!f.optional) problems.push(`missing ${f.name}`);
    } else if (typeof record[f.name] !== f.type) {
      problems.push(`${f.name} should be ${f.type}`);
    }
  }
  for (const key of Object.keys(record)) if (!known.has(key)) problems.push(`unexpected ${key}`);
  console.log(problems.length === 0 ? "ok" : problems.join("; "));
}
""", ['name:string age:number email?:string\n{"name":"ada","age":36}\n{"name":"bo","age":"x","admin":true}\n{"age":1,"email":5}',
      'on:boolean\n{"on":true}\n{}\n{"on":1,"x":1}'],
         hints=["Parse the schema into objects once; check each field, then look for unexpected keys."]),
]

TS_PROJECTS[8] = _project(
    8, "config.ts — a typed config loader",
    "Every service reads a config file: defaults, overrides, validation, and a clear report. This one pulls the month together — objects and destructuring, JSON, an interface for the shape, and a dictionary of settings you didn't predict.",
    ["The input is one JSON object: the user's config. The defaults are `{ \"name\": \"app\", \"port\": 8080, \"debug\": false, \"db\": { \"host\": \"localhost\", \"pool\": 5 } }`.",
     "Merge the config over the defaults one level into `db` (a user `db` object overrides only the keys it has). Describe the result with an `interface Config`.",
     "Validate: `port` must be an integer 1-65535, `debug` a boolean, `name` a non-empty string, `db.pool` an integer 1-100. Each failure prints `error: <path> <problem>` (`must be an integer 1-65535` and so on) and the value falls back to its default.",
     "Unknown top-level keys print `warning: unknown key <key>` (sorted) and are ignored.",
     "Finally print every setting as `<path> = <value>`, sorted by path, values as compact JSON."],
    r"""
interface DbConfig {
  host: string;
  pool: number;
}
interface Config {
  name: string;
  port: number;
  debug: boolean;
  db: DbConfig;
}
const defaults: Config = { name: "app", port: 8080, debug: false, db: { host: "localhost", pool: 5 } };
const user = JSON.parse(input) as Record<string, unknown>;
const known = new Set(Object.keys(defaults));
const errors: string[] = [];
const isInt = (v: unknown, lo: number, hi: number): v is number =>
  typeof v === "number" && Number.isInteger(v) && v >= lo && v <= hi;

function pick<T>(path: string, value: unknown, fallback: T, ok: (v: unknown) => boolean, problem: string): T {
  if (value === undefined) return fallback;
  if (ok(value)) return value as T;
  errors.push(`error: ${path} ${problem}`);
  return fallback;
}

const userDb = typeof user.db === "object" && user.db !== null ? (user.db as Record<string, unknown>) : {};
const config: Config = {
  name: pick("name", user.name, defaults.name, (v) => typeof v === "string" && v !== "", "must be a non-empty string"),
  port: pick("port", user.port, defaults.port, (v) => isInt(v, 1, 65535), "must be an integer 1-65535"),
  debug: pick("debug", user.debug, defaults.debug, (v) => typeof v === "boolean", "must be a boolean"),
  db: {
    host: pick("db.host", userDb.host, defaults.db.host, (v) => typeof v === "string" && v !== "", "must be a non-empty string"),
    pool: pick("db.pool", userDb.pool, defaults.db.pool, (v) => isInt(v, 1, 100), "must be an integer 1-100"),
  },
};
for (const e of errors) console.log(e);
for (const key of Object.keys(user).filter((k) => !known.has(k)).sort()) console.log(`warning: unknown key ${key}`);
const lines: [string, unknown][] = [
  ["db.host", config.db.host],
  ["db.pool", config.db.pool],
  ["debug", config.debug],
  ["name", config.name],
  ["port", config.port],
];
for (const [path, value] of lines) console.log(`${path} = ${JSON.stringify(value)}`);
""", ['{}', '{"port":3000,"debug":true,"db":{"pool":20}}', '{"port":70000,"name":"","db":{"pool":0,"host":"db.internal"}}',
      '{"verbose":true,"colour":"red","port":1.5}', '{"debug":"yes","db":null}', '{"name":"svc","db":{"host":"x"}}'],
    stretch=["Read the defaults from a second JSON document instead of the code.",
             "Report *every* problem with a nested path, for arbitrarily deep configs."],
)

TS_PRACTICE_MORE[8] = [
    _pr("tsm-w8-p5", "Object.entries on a record", "const scores: Record<string, number> = { ada: 3 };\nconst entries = Object.entries(scores);\n", "entries", "[string, number][]",
        hints=["Each entry is a `[key, value]` tuple."]),
    _pr("tsm-w8-p6", "An index-signature read", "const counts: { [k: string]: number } = {};\nconst n = counts[\"x\"];\n", "n", "number",
        hints=["Without `noUncheckedIndexedAccess`, the read is typed as the value type — even though it may be missing."]),
    _dx("tsm-w8-d5", "Indexing a known shape with a string",
        "error TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type '{ small: number; large: number; }'.",
        _STDIN + "const limits = { small: 10, large: 100 };\nconsole.log(limits[input]);\n",
        _STDIN + "const limits: Record<string, number> = { small: 10, large: 100 };\nconsole.log(limits[input] ?? \"unknown\");\n",
        [("small", "10"), ("huge", "unknown")], ask="Print the limit, or `unknown` for a name that isn't there.",
        hints=["The object's type has exactly two keys.", "Type it as a `Record<string, number>` and handle the missing case."]),
    _dx("tsm-w8-d6", "A missing key in an exhaustive record",
        "error TS2741: Property 'error' is missing in type '{ info: string; warn: string; }' but required in type 'Record<Level, string>'.",
        _STDIN + 'type Level = "info" | "warn" | "error";\nconst icon: Record<Level, string> = { info: "i", warn: "!" };\nconsole.log(icon[input as Level]);\n',
        _STDIN + 'type Level = "info" | "warn" | "error";\nconst icon: Record<Level, string> = { info: "i", warn: "!", error: "x" };\nconsole.log(icon[input as Level]);\n',
        [("error", "x"), ("info", "i")], ask="Give every level an icon — `error` is `x`.", hints=["`Record` over a union needs every member."]),
    _fx("tsm-w8-f3", "Counting into a plain object",
        "Count each word and print the counts as `word=n`, sorted. The word `constructor` breaks it.",
        _STDIN + "const counts: Record<string, number> = {};\nfor (const w of input.split(/\\s+/)) counts[w] = (counts[w] ?? 0) + 1;\nconsole.log(Object.keys(counts).sort().map((w) => `${w}=${counts[w]}`).join(\" \"));\n",
        _STDIN + "const counts: Record<string, number> = Object.create(null);\nfor (const w of input.split(/\\s+/)) counts[w] = (counts[w] ?? 0) + 1;\nconsole.log(Object.keys(counts).sort().map((w) => `${w}=${counts[w]}`).join(\" \"));\n",
        [("constructor a constructor", "a=1 constructor=2"), ("x x", "x=2")],
        hints=["`{}` inherits a `constructor` property.", "Start from an object with no prototype."], difficulty="Medium"),
]

TS_CARDS_MORE[8] = [
    ("`interface` vs `type` — what can only a type alias name?", "Unions, tuples, primitives and computed (mapped / conditional) types."),
    ("What can only an interface do?", "Merge: two declarations with the same name combine into one (declaration merging)."),
    ("`extends` vs `&` on a conflicting property?", "`extends` errors at the declaration; `&` quietly makes the property `never`, erroring only when a value is built."),
    ("Does a type annotation strip extra properties from an object?", "No — assigning a variable with extra fields is allowed and the fields stay at runtime (e.g. in `JSON.stringify`)."),
    ("Does `implements` do anything at runtime?", "No — it only asks the compiler to check the class's shape."),
    ("Why default dictionary reads: `counts[k] ?? 0`?", "A missing key reads as `undefined` even though an index signature types it as the value type; `undefined + 1` is `NaN`."),
    ("What does `Record<\"a\" | \"b\", V>` require?", "Exactly the keys `a` and `b` (TS2741 if one is missing, TS2353 for extras in a fresh literal)."),
    ("How do you make a dictionary safe for keys like `constructor`?", "`Object.create(null)`, `Object.hasOwn` checks, or a `Map`."),
    ("`{ x?: T }` vs `{ x: T | undefined }`?", "The first may omit the key; the second must include it, possibly as `undefined`."),
    ("TS7053?", "Indexing an object with an arbitrary `string` when its type has no index signature."),
    ("In what order does `Object.keys` list keys?", "Integer-like keys first in ascending numeric order, then the others in insertion order."),
    ("How do you rebuild an object from transformed entries?", "`Object.fromEntries(Object.entries(obj).map(([k, v]) => [newK, newV]))`."),
]
