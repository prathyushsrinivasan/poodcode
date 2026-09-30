# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter reading kinds, Month 2 (TS_MASTERY_ROADMAP
# X-10, X-11): predict / diagnose / retype / design / fix for the functions,
# arrays, tuples, destructuring, objects, JSON and interface chapters of weeks
# 5-8, topping each chapter up to its target.
#
# Weeks 5-8 run at `strict` (no noUncheckedIndexedAccess), and the scope lint
# keeps each program inside what its week has taught (no `interface`/`JSON`/
# `try` before week 8, no `as const` or `never`). Helpers are in
# mastery_ts_chapter_kit.py; exec()'d by gen_seed.py with the other
# tools/mastery_ts_x_m*.py files.
# ---------------------------------------------------------------------------

# ═══ ts_functions (week 5) ═══════════════════════════════════════════════════

_xpr("ts_functions", 1, "An arrow's signature",
     "const half = (n: number) => n / 2;\n", "half", "(n: number) => number",
     hints=["An arrow function's type is its parameter list and its return type.",
            "The return type is inferred from `n / 2`."])

_xpr("ts_functions", 2, "The result of a void function",
     "function logLine(text: string) {\n  console.log(\"> \" + text);\n}\nconst result = logLine(\"saved\");\n",
     "result", "void",
     hints=["What does `logLine` return? Nothing — and TypeScript has a name for that.",
            "A function with no `return` value is inferred to return `void`."])

_xpr("ts_functions", 3, "An array of functions",
     "function add(a: number, b: number): number {\n  return a + b;\n}\n"
     "const ops = [add, (a: number, b: number) => a - b];\n",
     "ops", "((a: number, b: number) => number)[]",
     hints=["Functions are values, so an array can hold them. Both have the same shape.",
            "An array of a function type needs parentheses: `(( ... ) => number)[]`."])

_xdx("ts_functions", 1, "Passing the raw input",
     "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.",
     r'''
function double(n: number): number {
  return n * 2;
}
console.log(double(input));
''', r'''
function double(n: number): number {
  return n * 2;
}
console.log(double(Number(input)));
''', ["4", "0", "-3"],
     hints=["The signature is a contract: `double` takes a number. What is `input`?",
            "Convert at the call site with `Number(input)`."])

_xrt("ts_functions", 1, "An average, honestly typed",
     "Replace every `any`: say what `average` takes and what it gives back.",
     r'''
function average(xs: any): any {
  return xs.reduce((a: any, b: any) => a + b, 0) / xs.length;
}
console.log(average(input.split(/\s+/).map(Number)).toFixed(2));
''', r'''
function average(xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
console.log(average(input.split(/\s+/).map(Number)).toFixed(2));
''', "type _1 = Expect<Equal<Parameters<typeof average>, [number[]]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof average>, number>>;",
     ["1 2 3 4", "10", "2.5 3.5"],
     hints=["It is called with the result of `.map(Number)`.",
            "`xs: number[]`, and the result is `number`. Once `xs` is typed, the callback needs no annotations."])

_xdz("ts_functions", 1, "The operation's type",
     "Write `Op` from how `add` and `sub` are declared and called.",
     r'''
type Op = (a: number, b: number) => number;
const add: Op = (a, b) => a + b;
const sub: Op = (a, b) => a - b;
const nums = input.split(/\s+/).map(Number);
for (const op of [add, sub]) console.log(op(nums[0], nums[1]));
''', "type Op = (a: number, b: number) => number;",
     "type _1 = Expect<Equal<Op, (a: number, b: number) => number>>;",
     ["7 3", "0 5", "-2 -2"],
     hints=["Each `Op` takes two numbers and returns one.",
            "A function type is written `(a: A, b: B) => R`."])

_xdz("ts_functions", 2, "The parser's signature",
     "`parseLine` has lost its signature. Write its parameter list and return type from how it is used.",
     r'''
function parseLine(line: string): number[] {
  return line.trim().split(/\s+/).map(Number);
}
const nums = parseLine(input);
console.log(nums.length, nums.reduce((a, b) => a + b, 0));
''', "(line: string): number[]",
     "type _1 = Expect<Equal<Parameters<typeof parseLine>, [string]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof parseLine>, number[]>>;",
     ["1 2 3", "  42  ", "5 -5"],
     hints=["It takes one line of text and gives back the numbers in it.",
            "`(line: string): number[]` — the return type goes after the `)`."])

_xdz("ts_functions", 3, "A callback that returns nothing",
     "Write the `Visit` type: the callback `eachWord` calls once per word.",
     r'''
type Visit = (word: string, index: number) => void;
function eachWord(text: string, visit: Visit): void {
  text.split(/\s+/).forEach((w, i) => visit(w, i));
}
eachWord(input, (w, i) => console.log(`${i + 1}. ${w}`));
''', "type Visit = (word: string, index: number) => void;",
     "type _1 = Expect<Equal<Visit, (word: string, index: number) => void>>;",
     ["red green blue", "solo"],
     hints=["`visit` gets a word and its position, and its result is not used.",
            "A callback whose result is ignored returns `void`."])

_xfx("ts_functions", 1, "A return inside the loop",
     "`firstEven` should print the first even number, or -1 if there is none. It gives up too early.",
     r'''
function firstEven(xs: number[]): number {
  for (const x of xs) {
    if (x % 2 === 0) return x;
    return -1;
  }
  return -1;
}
console.log(firstEven(input.split(/\s+/).map(Number)));
''', r'''
function firstEven(xs: number[]): number {
  for (const x of xs) {
    if (x % 2 === 0) return x;
  }
  return -1;
}
console.log(firstEven(input.split(/\s+/).map(Number)));
''', ["1 3 4 5", "8 1", "1 3 5"],
     hints=["`return` leaves the whole function — on the first element, whatever it is.",
            "Only return -1 after the loop has looked at every element."])

# ═══ ts_params (week 5) ══════════════════════════════════════════════════════

_xpr("ts_params", 1, "A rest parameter in the signature",
     "function log(level: string, ...messages: string[]) {\n  return `${level}: ${messages.join(\" \")}`;\n}\n",
     "log", "(level: string, ...messages: string[]) => string",
     hints=["A rest parameter stays a rest parameter in the function's type.",
            "`(level: string, ...messages: string[]) => ...` — and the template literal makes a string."])

_xpr("ts_params", 2, "An options object with a default",
     "function connect({ host = \"localhost\", port = 5432 }: { host?: string; port?: number } = {}) {\n"
     "  return host + \":\" + port;\n}\n",
     "connect", "(options?: { host?: string; port?: number }) => string",
     hints=["The `= {}` default makes the whole options parameter optional.",
            "Parameter names do not matter to the type: `(options?: { host?: string; port?: number }) => string`."])

_xpr("ts_params", 3, "A default does not remove null",
     "function greet(name: string | null = \"friend\") {\n  return name;\n}\nconst who = greet();\n",
     "who", "string | null",
     hints=["The default fills in only for `undefined`; the declared type still allows `null`.",
            "Inside the function `name` is `string | null`, and that is what comes back."])

_xrt("ts_params", 1, "Any count of numbers",
     "Replace the `any`s in `sum`, which takes any number of arguments.",
     r'''
function sum(...nums: any): any {
  return nums.reduce((a: any, b: any) => a + b, 0);
}
const xs = input.split(/\s+/).map(Number);
console.log(sum(...xs), sum(), sum(xs[0], 100));
''', r'''
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}
const xs = input.split(/\s+/).map(Number);
console.log(sum(...xs), sum(), sum(xs[0], 100));
''', "type _1 = Expect<Equal<Parameters<typeof sum>, number[]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof sum>, number>>;",
     ["1 2 3", "5", "-4 4"],
     hints=["A rest parameter is typed as an array.",
            "`...nums: number[]`, returning `number`."])

_xrt("ts_params", 2, "Rectangle or square",
     "Replace the `any`s. `h` may be left out, in which case the shape is a square.",
     r'''
function area(w: any, h?: any): any {
  return w * (h ?? w);
}
const nums = input.split(/\s+/).map(Number);
console.log(nums.length === 1 ? area(nums[0]) : area(nums[0], nums[1]));
''', r'''
function area(w: number, h?: number): number {
  return w * (h ?? w);
}
const nums = input.split(/\s+/).map(Number);
console.log(nums.length === 1 ? area(nums[0]) : area(nums[0], nums[1]));
''', "type _1 = Expect<Equal<Parameters<typeof area>, [w: number, h?: number]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof area>, number>>;",
     ["3 4", "5", "0 9"],
     hints=["Keep the `?`: an optional parameter is `number | undefined` inside.",
            "`(w: number, h?: number): number`."])

_xrt("ts_params", 3, "Price formatting options",
     "Replace the `any`s. The options object and each option in it may be left out.",
     r'''
function formatPrice(amount: any, opts: any = {}): string {
  const symbol = opts.symbol ?? "$";
  const decimals = opts.decimals ?? 2;
  return symbol + amount.toFixed(decimals);
}
const parts = input.split(/\s+/);
const amount = Number(parts[0]);
console.log(formatPrice(amount));
console.log(formatPrice(amount, { decimals: parts.length > 1 ? Number(parts[1]) : 0 }));
console.log(formatPrice(amount, { symbol: "EUR ", decimals: 1 }));
''', r'''
function formatPrice(amount: number, opts: { symbol?: string; decimals?: number } = {}): string {
  const symbol = opts.symbol ?? "$";
  const decimals = opts.decimals ?? 2;
  return symbol + amount.toFixed(decimals);
}
const parts = input.split(/\s+/);
const amount = Number(parts[0]);
console.log(formatPrice(amount));
console.log(formatPrice(amount, { decimals: parts.length > 1 ? Number(parts[1]) : 0 }));
console.log(formatPrice(amount, { symbol: "EUR ", decimals: 1 }));
''', "type _1 = Expect<Equal<Parameters<typeof formatPrice>, "
     "[amount: number, opts?: { symbol?: string; decimals?: number }]>>;",
     ["3.14159 3", "12", "0.5 0"],
     hints=["Every option is optional, and so is the object (it has a default).",
            "`opts: { symbol?: string; decimals?: number } = {}`."])

_xdz("ts_params", 1, "A logger's type",
     "Write `Logger` from how `log` is declared and called.",
     r'''
type Logger = (level: string, ...messages: string[]) => string;
const log: Logger = (level, ...messages) => `[${level}] ${messages.join(" ")}`.trim();
const words = input.split(/\s+/);
console.log(log("info"));
console.log(log("warn", ...words));
''', "type Logger = (level: string, ...messages: string[]) => string;",
     "type _1 = Expect<Equal<Logger, (level: string, ...messages: string[]) => string>>;",
     ["disk low", "ok"],
     hints=["One level is required; after it, any number of messages.",
            "A rest parameter in a function type: `(level: string, ...messages: string[]) => string`."])

_xdz("ts_params", 2, "Range options",
     "Write `RangeOptions` from the defaults `range` gives and the calls it gets.",
     r'''
type RangeOptions = { start?: number; step?: number };
function range(end: number, { start = 0, step = 1 }: RangeOptions = {}): number[] {
  const out: number[] = [];
  for (let i = start; i < end; i += step) out.push(i);
  return out;
}
const end = Number(input);
console.log(range(end).join(" "));
console.log(range(end, { step: 2 }).join(" "));
console.log(range(end, { start: 1, step: 3 }).join(" "));
''', "type RangeOptions = { start?: number; step?: number };",
     "type _1 = Expect<Equal<RangeOptions, { start?: number; step?: number }>>;",
     ["6", "10", "2"],
     hints=["Callers pass neither, one, or both settings.",
            "Both properties are optional numbers."])

_xdz("ts_params", 3, "A padder's type",
     "Write `Pad` so that every call below type-checks.",
     r'''
type Pad = (text: string, width?: number, fill?: string) => string;
const pad: Pad = (text, width = 6, fill = ".") => text.padStart(width, fill);
console.log(pad(input));
console.log(pad(input, 8));
console.log(pad(input, 8, "*"));
''', "type Pad = (text: string, width?: number, fill?: string) => string;",
     "type _1 = Expect<Equal<Pad, (text: string, width?: number, fill?: string) => string>>;",
     ["ok", "wide-word"],
     hints=["Callers may leave out the width, and the fill.",
            "Defaults in the implementation show up as `?` in the type."])

_xfx("ts_params", 1, "A zero factor",
     "`scale(x, factor)` multiplies by `factor`, which should be 1 only when it is left out. A factor of 0 gives the wrong answer.",
     r'''
function scale(x: number, factor?: number): number {
  return x * (factor || 1);
}
const nums = input.split(/\s+/).map(Number);
console.log(nums.length === 1 ? scale(nums[0]) : scale(nums[0], nums[1]));
''', r'''
function scale(x: number, factor = 1): number {
  return x * factor;
}
const nums = input.split(/\s+/).map(Number);
console.log(nums.length === 1 ? scale(nums[0]) : scale(nums[0], nums[1]));
''', ["5 0", "5", "5 3"],
     hints=["`||` falls back on every falsy value, and 0 is falsy.",
            "A default parameter applies only when the argument is missing."])

_xfx("ts_params", 2, "The first argument forgotten",
     "`maxOf(first, ...rest)` should return the largest of its arguments. It is wrong for a single number and for negatives.",
     r'''
function maxOf(first: number, ...rest: number[]): number {
  return rest.reduce((m, x) => (x > m ? x : m), 0);
}
const nums = input.split(/\s+/).map(Number);
console.log(maxOf(nums[0], ...nums.slice(1)));
''', r'''
function maxOf(first: number, ...rest: number[]): number {
  return rest.reduce((m, x) => (x > m ? x : m), first);
}
const nums = input.split(/\s+/).map(Number);
console.log(maxOf(nums[0], ...nums.slice(1)));
''', ["3 9 2", "7", "-3 -5"],
     hints=["`rest` holds everything after `first` — `first` itself is not in it.",
            "Start the reduction from `first`, not from 0."])

# ═══ ts_overloads (week 5) ═══════════════════════════════════════════════════

_xpr("ts_overloads", 1, "Which overload answers",
     "function wrap(x: string): string[];\nfunction wrap(x: number): number[];\n"
     "function wrap(x: string | number): (string | number)[] {\n  return [x];\n}\nconst w = wrap(5);\n",
     "w", "number[]",
     hints=["The caller sees only the overloads; the first that fits a number wins.",
            "The implementation's union return type is hidden."])

_xpr("ts_overloads", 2, "The general overload first",
     "function toNumber(value: unknown): number | null;\nfunction toNumber(value: string): number;\n"
     "function toNumber(value: unknown): number | null {\n  return value === null ? null : Number(value);\n}\n"
     "const n = toNumber(\"5\");\n",
     "n", "number | null",
     hints=["Overloads are tried top-down, and the first one that fits is used.",
            "`unknown` accepts a string, so the second overload is never reached."])

_xpr("ts_overloads", 3, "An overloaded function's type",
     "function parse(text: string): number;\nfunction parse(text: string[]): number[];\n"
     "function parse(text: string | string[]): number | number[] {\n"
     "  return Array.isArray(text) ? text.map(Number) : Number(text);\n}\n",
     "parse", "{ (text: string): number; (text: string[]): number[] }",
     hints=["The type of an overloaded function lists every overload — and not the implementation signature.",
            "Several call signatures are written in braces: `{ (a: A): X; (b: B): Y }`."])

_xrt("ts_overloads", 1, "Number in, number out",
     "Replace the `any` version with two overloads: a number gives back a number, an array of numbers gives back an array (in that order).",
     r'''
function double(x: any): any {
  return typeof x === "number" ? x * 2 : x.map((n: number) => n * 2);
}
const nums = input.split(/\s+/).map(Number);
console.log(double(nums[0]).toFixed(1));
console.log(double(nums).join(" "));
''', r'''
function double(x: number): number;
function double(x: number[]): number[];
function double(x: number | number[]): number | number[] {
  return typeof x === "number" ? x * 2 : x.map((n) => n * 2);
}
const nums = input.split(/\s+/).map(Number);
console.log(double(nums[0]).toFixed(1));
console.log(double(nums).join(" "));
''', "type _1 = Expect<Equal<typeof double, { (x: number): number; (x: number[]): number[] }>>;",
     ["1 2 3", "0.5", "-4 4"],
     hints=["Write the two overload signatures (no body), then the implementation.",
            "The implementation takes `number | number[]` and returns `number | number[]`."])

_xrt("ts_overloads", 2, "One word or the first few",
     "Replace the `any` version with overloads: `pick(words)` gives one string, `pick(words, n)` gives an array (in that order).",
     r'''
function pick(xs: any, n?: any): any {
  return n === undefined ? xs[0] : xs.slice(0, n);
}
const words = input.split(/\s+/);
console.log(pick(words).toUpperCase());
console.log(pick(words, 2).join("+"));
''', r'''
function pick(xs: string[]): string;
function pick(xs: string[], n: number): string[];
function pick(xs: string[], n?: number): string | string[] {
  return n === undefined ? xs[0] : xs.slice(0, n);
}
const words = input.split(/\s+/);
console.log(pick(words).toUpperCase());
console.log(pick(words, 2).join("+"));
''', "type _1 = Expect<Equal<typeof pick, { (xs: string[]): string; (xs: string[], n: number): string[] }>>;",
     ["alpha beta gamma", "solo"],
     hints=["The return type depends on whether `n` is passed — that is what overloads are for.",
            "The implementation's `n` is optional, and it returns `string | string[]`."])

_xdz("ts_overloads", 1, "The missing overload",
     "One overload of `parse` is missing. Write it from how `parse` is called.",
     r'''
function parse(text: string): number;
function parse(text: string[]): number[];
function parse(text: string | string[]): number | number[] {
  return typeof text === "string" ? Number(text) : text.map(Number);
}
const words = input.split(/\s+/);
console.log(parse(words[0]).toFixed(1));
console.log(parse(words).reduce((a, b) => a + b, 0));
''', "function parse(text: string[]): number[];",
     "type _1 = Expect<Equal<typeof parse, { (text: string): number; (text: string[]): number[] }>>;",
     ["1 2 3", "42"],
     hints=["`parse(words)` is called with an array, and its result is reduced.",
            "An overload signature is a declaration with no body, ending in `;`."])

_xdz("ts_overloads", 2, "A field decides the result",
     "One overload of `read` is missing. Write it from the second call.",
     r'''
function read(field: "count", raw: string): number;
function read(field: "tags", raw: string): string[];
function read(field: "count" | "tags", raw: string): number | string[] {
  return field === "count" ? raw.split(",").length : raw.split(",");
}
console.log(read("count", input) + 1);
console.log(read("tags", input).join(" | "));
''', "function read(field: \"tags\", raw: string): string[];",
     "type _1 = Expect<Equal<typeof read, { (field: \"count\", raw: string): number; (field: \"tags\", raw: string): string[] }>>;",
     ["a,b,c", "solo"],
     hints=["The first argument is a literal that picks the return type.",
            "`read(\"tags\", …)` gives back something with `.join`."])

_xdz("ts_overloads", 3, "Now or later",
     "The first overload of `clampTo` is missing. Write it from how `cap` is made and used.",
     r'''
function clampTo(max: number): (n: number) => number;
function clampTo(max: number, n: number): number;
function clampTo(max: number, n?: number): number | ((n: number) => number) {
  if (n === undefined) return (m: number) => Math.min(m, max);
  return Math.min(n, max);
}
const nums = input.split(/\s+/).map(Number);
const cap = clampTo(10);
console.log(nums.map(cap).join(" "));
console.log(clampTo(5, nums[0]));
''', "function clampTo(max: number): (n: number) => number;",
     "type _1 = Expect<Equal<typeof clampTo, { (max: number): (n: number) => number; (max: number, n: number): number }>>;",
     ["3 12 10", "20"],
     hints=["With one argument, `clampTo` gives back something `map` can call.",
            "The return type of that overload is a function type."])

_xfx("ts_overloads", 1, "Zero seconds",
     "`seconds(total)` or `seconds(minutes, secs)` should give a number of seconds. The two-argument form is wrong when `secs` is 0.",
     r'''
function seconds(total: number): number;
function seconds(minutes: number, secs: number): number;
function seconds(a: number, b?: number): number {
  return b ? a * 60 + b : a;
}
const nums = input.split(/\s+/).map(Number);
console.log(nums.length === 1 ? seconds(nums[0]) : seconds(nums[0], nums[1]));
''', r'''
function seconds(total: number): number;
function seconds(minutes: number, secs: number): number;
function seconds(a: number, b?: number): number {
  return b === undefined ? a : a * 60 + b;
}
const nums = input.split(/\s+/).map(Number);
console.log(nums.length === 1 ? seconds(nums[0]) : seconds(nums[0], nums[1]));
''', ["2 0", "90", "1 30"],
     hints=["The body tells the overloads apart with a truthiness test. Is 0 truthy?",
            "Ask whether the argument was passed: `b === undefined`."])

_xfx("ts_overloads", 2, "The two-argument case",
     "`fmt` has three overloads. The one with a unit but no plural prints `undefined` for anything but 1; it should add an `s`.",
     r'''
function fmt(n: number): string;
function fmt(n: number, unit: string): string;
function fmt(n: number, unit: string, plural: string): string;
function fmt(n: number, unit?: string, plural?: string): string {
  if (unit === undefined) return String(n);
  return `${n} ${n === 1 ? unit : plural}`;
}
const parts = input.split(/\s+/);
const n = Number(parts[0]);
if (parts.length === 1) console.log(fmt(n));
else if (parts.length === 2) console.log(fmt(n, parts[1]));
else console.log(fmt(n, parts[1], parts[2]));
''', r'''
function fmt(n: number): string;
function fmt(n: number, unit: string): string;
function fmt(n: number, unit: string, plural: string): string;
function fmt(n: number, unit?: string, plural?: string): string {
  if (unit === undefined) return String(n);
  return `${n} ${n === 1 ? unit : plural ?? unit + "s"}`;
}
const parts = input.split(/\s+/);
const n = Number(parts[0]);
if (parts.length === 1) console.log(fmt(n));
else if (parts.length === 2) console.log(fmt(n, parts[1]));
else console.log(fmt(n, parts[1], parts[2]));
''', ["3 cat", "1 cat", "2 mouse mice", "7"],
     hints=["The body is checked against `plural?: string`, so the compiler lets `undefined` through.",
            "Fall back when `plural` was not passed: `plural ?? unit + \"s\"`."])

# ═══ ts_closures_scope (week 5) ══════════════════════════════════════════════

_xpr("ts_closures_scope", 1, "An object of closures",
     "function makeBank(opening: number) {\n  let balance = opening;\n"
     "  return {\n    deposit: (n: number) => {\n      balance += n;\n    },\n    read: () => balance,\n  };\n}\n"
     "const account = makeBank(10);\n",
     "account", "{ deposit: (n: number) => void; read: () => number }",
     hints=["The factory returns an object literal whose properties are arrow functions.",
            "`deposit` returns nothing; `read` returns the captured `balance`."])

_xpr("ts_closures_scope", 2, "A lookup over a captured Map",
     "const cache = new Map<string, number>();\nconst lookup = (key: string) => cache.get(key);\n",
     "lookup", "(key: string) => number | undefined",
     hints=["The arrow closes over `cache`; its return type is whatever `get` gives.",
            "`Map.get` might not find the key."])

_xpr("ts_closures_scope", 3, "A captured flag",
     "function makeToggle() {\n  let on = false;\n  return () => (on = !on);\n}\nconst flip = makeToggle();\n",
     "flip", "() => boolean",
     hints=["`let on = false` can change, so it is not the literal `false`.",
            "An assignment expression has the type of the value assigned."])

_xdx("ts_closures_scope", 1, "State that cannot change",
     "TS2588: Cannot assign to 'count' because it is a constant.",
     r'''
function makeCounter() {
  const count = 0;
  return () => ++count;
}
const next = makeCounter();
let last = 0;
for (let i = 0; i < Number(input); i++) last = next();
console.log(last);
''', r'''
function makeCounter() {
  let count = 0;
  return () => ++count;
}
const next = makeCounter();
let last = 0;
for (let i = 0; i < Number(input); i++) last = next();
console.log(last);
''', ["3", "1", "0"],
     hints=["The closure's job is to change `count` between calls.",
            "Captured state that changes must be declared with `let`."])

_xrt("ts_closures_scope", 1, "A running total",
     "Replace the `any`s in the factory and in the function it returns.",
     r'''
function makeAccumulator(start: any): any {
  let total = start;
  return (n: any) => {
    total += n;
    return total;
  };
}
const add = makeAccumulator(100);
console.log(input.split(/\s+/).map((t) => add(Number(t))).join(" "));
''', r'''
function makeAccumulator(start: number): (n: number) => number {
  let total = start;
  return (n: number) => {
    total += n;
    return total;
  };
}
const add = makeAccumulator(100);
console.log(input.split(/\s+/).map((t) => add(Number(t))).join(" "));
''', "type _1 = Expect<Equal<Parameters<typeof makeAccumulator>, [number]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof makeAccumulator>, (n: number) => number>>;",
     ["1 2 3", "-100", "5"],
     hints=["The factory returns a function; its return type is a function type.",
            "`(start: number): (n: number) => number`."])

_xrt("ts_closures_scope", 2, "A private stack",
     "Replace the `any`s: the stack holds words from the input.",
     r'''
function makeStack() {
  const items: any[] = [];
  return {
    push: (x: any) => {
      items.push(x);
    },
    pop: () => items.pop(),
    size: () => items.length,
  };
}
const stack = makeStack();
for (const t of input.split(/\s+/)) {
  if (t === "-") console.log(stack.pop() ?? "empty");
  else stack.push(t);
}
console.log(stack.size());
''', r'''
function makeStack() {
  const items: string[] = [];
  return {
    push: (x: string) => {
      items.push(x);
    },
    pop: () => items.pop(),
    size: () => items.length,
  };
}
const stack = makeStack();
for (const t of input.split(/\s+/)) {
  if (t === "-") console.log(stack.pop() ?? "empty");
  else stack.push(t);
}
console.log(stack.size());
''', "type _1 = Expect<Equal<ReturnType<typeof makeStack>, "
     "{ push: (x: string) => void; pop: () => string | undefined; size: () => number }>>;",
     ["a b - c", "- x", "p q r - -"],
     hints=["What is pushed? The tokens of the input.",
            "Type `items` as `string[]` and `x` as `string`; `pop` then follows."])

_xrt("ts_closures_scope", 3, "A tally per word",
     "Replace the `any`: the returned function should be known to give back a number.",
     r'''
function makeTally() {
  const counts: any = new Map();
  return (word: string) => {
    const next = (counts.get(word) ?? 0) + 1;
    counts.set(word, next);
    return next;
  };
}
const tally = makeTally();
console.log(input.split(/\s+/).map((w) => tally(w)).join(" "));
''', r'''
function makeTally() {
  const counts = new Map<string, number>();
  return (word: string) => {
    const next = (counts.get(word) ?? 0) + 1;
    counts.set(word, next);
    return next;
  };
}
const tally = makeTally();
console.log(input.split(/\s+/).map((w) => tally(w)).join(" "));
''', "type _1 = Expect<Equal<ReturnType<typeof makeTally>, (word: string) => number>>;",
     ["a b a a", "x", "one two two one"],
     hints=["An `any` Map makes everything read from it `any` too.",
            "`new Map<string, number>()`."])

_xdz("ts_closures_scope", 1, "A counter's interface",
     "Write the `Counter` type that `makeCounter` returns.",
     r'''
type Counter = { next: () => number; reset: () => void };
function makeCounter(step: number): Counter {
  let n = 0;
  return {
    next: () => (n += step),
    reset: () => {
      n = 0;
    },
  };
}
const [first, ...ops] = input.split(/\s+/);
const c = makeCounter(Number(first));
for (const op of ops) {
  if (op === "r") c.reset();
  else console.log(c.next());
}
''', "type Counter = { next: () => number; reset: () => void };",
     "type _1 = Expect<Equal<Counter, { next: () => number; reset: () => void }>>;",
     ["2 n n r n", "5 n", "1 r n n"],
     hints=["Two methods: one gives back the new count, one gives back nothing.",
            "Write each as a property with a function type."])

_xdz("ts_closures_scope", 2, "A rate fixed at creation",
     "Write `Taxer`: a function that takes a rate and returns a function from a price to a price.",
     r'''
type Taxer = (rate: number) => (price: number) => number;
const makeWithTax: Taxer = (rate) => (price) => price * (1 + rate);
const [price, rate] = input.split(/\s+/).map(Number);
const withTax = makeWithTax(rate);
console.log(withTax(price).toFixed(2));
''', "type Taxer = (rate: number) => (price: number) => number;",
     "type _1 = Expect<Equal<Taxer, (rate: number) => (price: number) => number>>;",
     ["100 0.2", "50 0", "9.99 0.1"],
     hints=["The first call captures the rate; the second takes the price.",
            "Arrows nest to the right: `(rate: number) => (price: number) => number`."])

_xdz("ts_closures_scope", 3, "A gate that remembers",
     "Write `Gate`: the object `makeGate` returns.",
     r'''
type Gate = { allow: (name: string) => boolean; seen: () => string[] };
function makeGate(): Gate {
  const names: string[] = [];
  return {
    allow: (name) => {
      if (names.includes(name)) return false;
      names.push(name);
      return true;
    },
    seen: () => [...names],
  };
}
const gate = makeGate();
for (const name of input.split(/\s+/)) console.log(name, gate.allow(name));
console.log(gate.seen().join(","));
''', "type Gate = { allow: (name: string) => boolean; seen: () => string[] };",
     "type _1 = Expect<Equal<Gate, { allow: (name: string) => boolean; seen: () => string[] }>>;",
     ["ada bo ada", "x"],
     hints=["`allow` answers yes or no; `seen` lists the names so far.",
            "`{ allow: (name: string) => boolean; seen: () => string[] }`."])

_xfx("ts_closures_scope", 1, "A counter that forgets",
     "Each call to `next` should give the next number, 1, 2, 3… It always gives 1.",
     r'''
function makeCounter() {
  return () => {
    let count = 0;
    return ++count;
  };
}
const next = makeCounter();
const out: number[] = [];
for (let i = 0; i < Number(input); i++) out.push(next());
console.log(out.join(" "));
''', r'''
function makeCounter() {
  let count = 0;
  return () => {
    return ++count;
  };
}
const next = makeCounter();
const out: number[] = [];
for (let i = 0; i < Number(input); i++) out.push(next());
console.log(out.join(" "));
''', ["3", "1", "5"],
     hints=["Where is `count` created — once, or on every call?",
            "Declare it in the factory, outside the returned function, so the closure keeps it."])

_xfx("ts_closures_scope", 2, "Once, but every time",
     "`once(f)` should call `f` on the first call only and keep returning that first result. It recomputes each time.",
     r'''
function once(f: (x: number) => number) {
  let done = false;
  let result = 0;
  return (x: number) => {
    if (!done) result = f(x);
    return result;
  };
}
const first = once((x) => x * 10);
console.log(input.split(/\s+/).map((t) => first(Number(t))).join(" "));
''', r'''
function once(f: (x: number) => number) {
  let done = false;
  let result = 0;
  return (x: number) => {
    if (!done) {
      result = f(x);
      done = true;
    }
    return result;
  };
}
const first = once((x) => x * 10);
console.log(input.split(/\s+/).map((t) => first(Number(t))).join(" "));
''', ["1 2 3", "7", "4 4"],
     hints=["The closure keeps `done` — but does anything ever change it?",
            "Set `done = true` after the first call."])
