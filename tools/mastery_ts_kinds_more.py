# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Three exercise kinds the Mastery weeks did not have (TS_MASTERY_ROADMAP.md
# X-10, X-13):
#
#   _rt — retype: the program runs and prints the right thing, and its types
#         say nothing (`any` everywhere). Replace every `any` with a type that
#         describes what is there. Graded on stdout AND on hidden claims that
#         `any` cannot satisfy — `Equal` treats `any` as its own type.
#   _dz — design: the type declaration is blanked and the code that uses it is
#         left in place, so the shape has to be recovered from its use. Graded
#         on stdout and on claims about the type.
#   _rf — refactor: working code and a constraint ("no loops", "no `as`",
#         "truly private fields"). The banned tokens go in `forbid`, which the
#         judge checks before compiling, so the working starter does not pass
#         until the constraint is met — and the tests prove behaviour is kept.
#
# Programs name only their inputs; outputs are computed (tools/ts_outputs_kit.py).
# Every program here is scope-linted with its week (mastery_ts_scope.py).
# exec()'d by gen_seed.py before mastery_ts_attach.py.
# ---------------------------------------------------------------------------

import re as _km_re

_KM_PRELUDE = _TW_PRELUDE + "type IsAny<T> = 0 extends 1 & T ? true : false;\n"
_KM_ANY = _km_re.compile(r"\bany\b")


def _km(week, eid, kind, title, prompt, starter, solution, inputs, harness="", forbid=(), hints=(),
        difficulty="Medium"):
    strictness = _week_strictness(week)
    starter = _TS_SCAFFOLD + starter.strip("\n") + "\n"
    solution = _TS_SCAFFOLD + solution.strip("\n") + "\n"
    assert starter != solution, f"{eid}: starter equals solution"
    hints = list(hints)
    ex = {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "", "hints": hints,
        "language": "typescript", "kind": kind, "difficulty": difficulty,
        "strictness": strictness,
        "harness": (_KM_PRELUDE + "\n" + harness.strip("\n") + "\n") if harness.strip() else "",
        "judge_mode": "", "forbid": list(forbid),
        "starter": starter, "solution": solution,
        "tests": _computed(eid, solution, inputs, strictness),
        "source_slug": "", "dataset": "",
    }
    TS_PRACTICE_MORE.setdefault(week, []).append(ex)
    return ex


def _rt(week, eid, title, prompt, anyish, typed, asserts, inputs, hints=()):
    assert _KM_ANY.search(anyish), f"{eid}: a retype starter needs an `any` to replace"
    assert not _KM_ANY.search(typed), f"{eid}: the solution still says `any`"
    return _km(week, eid, "retype", title, prompt, anyish, typed, inputs, harness=asserts, hints=hints)


def _dz(week, eid, title, prompt, full, blank, asserts, inputs, hints=()):
    assert full.count(blank) == 1, f"{eid}: the blank must appear exactly once"
    return _km(week, eid, "design", title, prompt, full.replace(blank, "____", 1), full, inputs,
               harness=asserts, hints=hints)


def _rf(week, eid, title, prompt, before, after, forbid, inputs, hints=()):
    # A ban may also close the obvious workaround (no `if` chain -> no `switch`
    # either), so only one banned token has to be in the starter.
    assert any(tok in before for tok in forbid), f"{eid}: the starter uses none of {forbid}, so it would pass"
    for tok in forbid:
        assert tok not in after, f"{eid}: the solution still uses the banned {tok!r}"
        assert tok not in _TS_SCAFFOLD, f"{eid}: {tok!r} is in the stdin scaffold"
    return _km(week, eid, "refactor", title, prompt, before, after, inputs, forbid=forbid, hints=hints)


# ---- Month 1 ----------------------------------------------------------------

_rt(1, "tsm-w1-rt1", "Temperatures without any",
    "It converts Celsius to Fahrenheit correctly — and `any` means the compiler checks none of it. Replace both `any` annotations with the type each value really has.",
    r'''
const celsius: any = Number(input);
const fahrenheit: any = (celsius * 9) / 5 + 32;
console.log(fahrenheit + " F");
''', r'''
const celsius: number = Number(input);
const fahrenheit: number = (celsius * 9) / 5 + 32;
console.log(fahrenheit + " F");
''', '''
type _1 = Expect<Equal<typeof celsius, number>>;
type _2 = Expect<Equal<typeof fahrenheit, number>>;
''', ["100", "0", "-40", "37"],
    hints=["`Number(...)` always produces a number.", "Arithmetic on numbers gives a number: both are `number`."])

_rf(1, "tsm-w1-rf1", "Nothing here changes",
    "Every `let` below is assigned once and never again. Make each one a `const`, so the compiler stops anyone reassigning them by accident. The output must not change.",
    r'''
let parts = input.split(/\s+/);
let w = Number(parts[0]);
let h = Number(parts[1]);
let area = w * h;
let perimeter = 2 * (w + h);
console.log(`area ${area}`);
console.log(`perimeter ${perimeter}`);
''', r'''
const parts = input.split(/\s+/);
const w = Number(parts[0]);
const h = Number(parts[1]);
const area = w * h;
const perimeter = 2 * (w + h);
console.log(`area ${area}`);
console.log(`perimeter ${perimeter}`);
''', ["let "], ["3 4", "10 2", "1 1"],
    hints=["Reach for `const` by default; `let` is for values that really change."])

_rt(2, "tsm-w2-rt1", "Classify with real types",
    "`classify` compares two numbers and names the result. Replace every `any`: the two parameters are numbers, and the return type should be `string`.",
    r'''
function classify(n: any, limit: any): any {
  if (n > limit) return "high";
  if (n === limit) return "equal";
  return "low";
}
const [a, b] = input.split(/\s+/).map(Number);
console.log(classify(a, b));
''', r'''
function classify(n: number, limit: number): string {
  if (n > limit) return "high";
  if (n === limit) return "equal";
  return "low";
}
const [a, b] = input.split(/\s+/).map(Number);
console.log(classify(a, b));
''', '''
type _1 = Expect<Equal<Parameters<typeof classify>[0], number>>;
type _2 = Expect<Equal<Parameters<typeof classify>[1], number>>;
type _3 = Expect<Equal<ReturnType<typeof classify>, string>>;
''', ["5 3", "3 3", "1 9"],
    hints=["The call passes the numbers from `.map(Number)`.", "Annotate the return as `string`."])

_rf(2, "tsm-w2-rf1", "A table, not a chain",
    "The if/else chain maps a colour code to its name. Replace it with a lookup object and `??` for the fallback — no `if (` and no `switch` left.",
    r'''
let name = "";
if (input === "R") name = "red";
else if (input === "G") name = "green";
else if (input === "B") name = "blue";
else name = "unknown";
console.log(name);
''', r'''
const names: Record<string, string> = { R: "red", G: "green", B: "blue" };
console.log(names[input] ?? "unknown");
''', ["if (", "switch"], ["R", "B", "X", "G"],
    hints=["An object whose keys are the codes: `{ R: \"red\", ... }`.", "Annotate it `Record<string, string>` so any code can index it, then `?? \"unknown\"`."])

_rt(3, "tsm-w3-rt1", "Statistics, typed",
    "`stats` sums a list of numbers and averages it. Replace each `any` — `xs` is an array of numbers (a `readonly` one is fine too) and `sum` is a number.",
    r'''
function stats(xs: any) {
  let sum: any = 0;
  for (const x of xs) sum += x;
  return { sum, mean: sum / xs.length };
}
const s = stats(input.split(/\s+/).map(Number));
console.log(s.sum + " " + s.mean.toFixed(2));
''', r'''
function stats(xs: readonly number[]) {
  let sum = 0;
  for (const x of xs) sum += x;
  return { sum, mean: sum / xs.length };
}
const s = stats(input.split(/\s+/).map(Number));
console.log(s.sum + " " + s.mean.toFixed(2));
''', '''
type _P = Parameters<typeof stats>[0];
type _1 = Expect<Equal<IsAny<_P>, false>>;
type _2 = Expect<Equal<number[] extends _P ? (_P extends readonly number[] ? true : false) : false, true>>;
type _3 = Expect<Equal<ReturnType<typeof stats>, { sum: number; mean: number }>>;
''', ["1 2 3 4", "10", "5 5 6"],
    hints=["`number[]` or `readonly number[]` for the list.", "Once `sum` starts as a number, the return type follows."])

_rf(3, "tsm-w3-rf1", "No index bookkeeping",
    "The loop only ever reads `xs[i]`. Rewrite it without an index: iterate over the values directly. The output must not change.",
    r'''
const xs = input.split(/\s+/).map(Number);
let total = 0;
let best = -Infinity;
for (let i = 0; i < xs.length; i++) {
  total += xs[i];
  if (xs[i] > best) best = xs[i];
}
console.log(`total ${total} max ${best}`);
''', r'''
const xs = input.split(/\s+/).map(Number);
let total = 0;
let best = -Infinity;
for (const x of xs) {
  total += x;
  if (x > best) best = x;
}
console.log(`total ${total} max ${best}`);
''', ["for (let", "xs[i]"], ["3 9 2", "-5 -1", "7"],
    hints=["`for (const x of xs)` hands you each value."])

_rt(4, "tsm-w4-rt1", "Initials, typed",
    "`initials` turns a full name into its initials. Replace the three `any`s: a name is a string, each word is a string, and so is the result.",
    r'''
function initials(name: any): any {
  return name.split(" ").map((w: any) => w[0].toUpperCase()).join("");
}
for (const line of input.split("\n")) console.log(initials(line.trim()));
''', r'''
function initials(name: string): string {
  return name.split(" ").map((w) => w[0].toUpperCase()).join("");
}
for (const line of input.split("\n")) console.log(initials(line.trim()));
''', '''
type _1 = Expect<Equal<Parameters<typeof initials>[0], string>>;
type _2 = Expect<Equal<ReturnType<typeof initials>, string>>;
''', ["ada lovelace\ngrace brewster hopper", "alan turing"],
    hints=["Once `name` is a string, `split` gives `string[]` and the callback's `w` is inferred — no annotation needed."])

_rf(4, "tsm-w4-rf1", "Template, not glue",
    "The line is glued together with `+`. Build it with one template literal instead — no `\" +` or `+ \"` left. Same output.",
    r'''
const [first, last, city] = input.split(",").map((s) => s.trim());
console.log("Name: " + last.toUpperCase() + ", " + first + " (" + city + ")");
''', r'''
const [first, last, city] = input.split(",").map((s) => s.trim());
console.log(`Name: ${last.toUpperCase()}, ${first} (${city})`);
''', ['" +', '+ "'], ["ada, lovelace, london", "alan,turing,wilmslow"],
    hints=["Backticks, with each value in `${...}`."])

# ---- Month 2 ----------------------------------------------------------------

_dz(5, "tsm-w5-dz1", "A formatter's type",
    "Write `Formatter` first: a function type taking a number and an optional options object (`decimals?: number`, `unit?: string`) and returning a string. The implementation and the calls below already rely on it.",
    r'''
type Formatter = (value: number, opts?: { decimals?: number; unit?: string }) => string;
const format: Formatter = (value, opts = {}) => `${value.toFixed(opts.decimals ?? 0)}${opts.unit ?? ""}`;
const [v, d, u] = input.split(/\s+/);
console.log(format(Number(v)));
console.log(format(Number(v), { decimals: Number(d) }));
console.log(format(Number(v), { decimals: Number(d), unit: u }));
''', "type Formatter = (value: number, opts?: { decimals?: number; unit?: string }) => string;", '''
type _1 = Expect<Equal<Parameters<Formatter>[0], number>>;
type _2 = Expect<Equal<Parameters<Formatter>[1], { decimals?: number; unit?: string } | undefined>>;
type _3 = Expect<Equal<ReturnType<Formatter>, string>>;
type _4 = Expect<Equal<Parameters<Formatter>["length"], 1 | 2>>;
''', ["3.14159 2 m", "10 1 kg"],
    hints=["A function type: `(value: number, opts?: {...}) => string`.", "The second parameter is optional — `opts?:` — because the first call leaves it out."])

_rt(5, "tsm-w5-rt1", "Discounts, typed",
    "Replace every `any` in `applyDiscount`. The discount percentage has a default of 10; its type should still be `number`.",
    r'''
function applyDiscount(price: any, pct: any = 10): any {
  return Math.round(price * (100 - pct)) / 100;
}
const [p, d] = input.split(/\s+/).map(Number);
console.log(applyDiscount(p));
console.log(applyDiscount(p, d));
''', r'''
function applyDiscount(price: number, pct = 10): number {
  return Math.round(price * (100 - pct)) / 100;
}
const [p, d] = input.split(/\s+/).map(Number);
console.log(applyDiscount(p));
console.log(applyDiscount(p, d));
''', '''
type _1 = Expect<Equal<Parameters<typeof applyDiscount>[0], number>>;
type _2 = Expect<Equal<Parameters<typeof applyDiscount>[1], number | undefined>>;
type _3 = Expect<Equal<ReturnType<typeof applyDiscount>, number>>;
''', ["80 25", "19.99 50"],
    hints=["A default value is enough for inference: `pct = 10` is a `number`.", "Callers may leave it out, so its parameter type reads `number | undefined` from outside."])

_rf(5, "tsm-w5-rf1", "Defaults where they belong",
    "`greet` fakes default arguments with `||`. Use real default parameters instead — no `||` left. (Every test passes non-empty names, so the behaviour is the same.)",
    r'''
function greet(name?: string, greeting?: string): string {
  const n = name || "friend";
  const g = greeting || "Hello";
  return `${g}, ${n}!`;
}
const parts = input.split(",").map((s) => s.trim());
console.log(greet());
console.log(greet(parts[0]));
console.log(greet(parts[0], parts[1]));
''', r'''
function greet(name = "friend", greeting = "Hello"): string {
  return `${greeting}, ${name}!`;
}
const parts = input.split(",").map((s) => s.trim());
console.log(greet());
console.log(greet(parts[0]));
console.log(greet(parts[0], parts[1]));
''', ["||"], ["Ada, Hi", "Bo, Welcome"],
    hints=["`function greet(name = \"friend\", ...)` — the default applies when the argument is missing."])

_rt(6, "tsm-w6-rt1", "Composition, typed",
    "`compose(f, g)` returns a function that applies `f` then `g`. Here both work on numbers. Replace every `any` so the parameters are `(n: number) => number` functions and the result is one too.",
    r'''
function compose(f: any, g: any): any {
  return (x: any) => g(f(x));
}
const double = (n: number) => n * 2;
const inc = (n: number) => n + 1;
const both = compose(double, inc);
for (const n of input.split(/\s+/).map(Number)) console.log(both(n));
''', r'''
function compose(f: (n: number) => number, g: (n: number) => number): (x: number) => number {
  return (x) => g(f(x));
}
const double = (n: number) => n * 2;
const inc = (n: number) => n + 1;
const both = compose(double, inc);
for (const n of input.split(/\s+/).map(Number)) console.log(both(n));
''', '''
type _1 = Expect<Equal<Parameters<typeof compose>[0], (n: number) => number>>;
type _2 = Expect<Equal<Parameters<typeof compose>[1], (n: number) => number>>;
type _3 = Expect<Equal<ReturnType<typeof compose>, (x: number) => number>>;
''', ["1 2 3", "10"],
    hints=["A function type is written `(n: number) => number`.", "Annotate the return type and the inner arrow's `x` is inferred."])

_rf(6, "tsm-w6-rf1", "Loops into a pipeline",
    "Rewrite the two loops as a `filter`, a `map` and a `reduce` — no `for (` or `while (` left. Same output.",
    r'''
const words = input.split(/\s+/);
const lengths: number[] = [];
for (const w of words) {
  if (w.length > 3) lengths.push(w.length);
}
let total = 0;
for (const n of lengths) total += n;
console.log(lengths.join(","));
console.log(total);
''', r'''
const words = input.split(/\s+/);
const lengths = words.filter((w) => w.length > 3).map((w) => w.length);
const total = lengths.reduce((a, b) => a + b, 0);
console.log(lengths.join(","));
console.log(total);
''', ["for (", "while ("], ["the quick brown fox jumps", "a bb ccc dddd eeeee"],
    hints=["Keep the long words, then turn each into its length.", "`reduce((a, b) => a + b, 0)` sums."])

_dz(6, "tsm-w6-dz1", "A recursive shape",
    "Write the `Tree` type: a node has a numeric `value` and a list of `children`, each of which is itself a `Tree`. Both recursive functions below depend on it.",
    r'''
type Tree = { value: number; children: Tree[] };
function sum(t: Tree): number {
  return t.value + t.children.reduce((acc, c) => acc + sum(c), 0);
}
function depth(t: Tree): number {
  return 1 + Math.max(0, ...t.children.map(depth));
}
const [a, b, c] = input.split(/\s+/).map(Number);
const tree: Tree = {
  value: a,
  children: [{ value: b, children: [] }, { value: c, children: [{ value: 1, children: [] }] }],
};
console.log(sum(tree), depth(tree));
''', "type Tree = { value: number; children: Tree[] };", '''
type _1 = Expect<Equal<Tree["value"], number>>;
type _2 = Expect<Equal<Tree["children"][number], Tree>>;
''', ["5 3 2", "1 1 1"],
    hints=["A type alias may refer to itself inside an object type.", "`children: Tree[]`."])

_rt(7, "tsm-w7-rt1", "Min and max as a pair",
    "`minMax` returns the smallest and largest number as a pair. Replace every `any`: the input is a list of numbers (`readonly` is fine) and the result is the tuple `[number, number]` (a `readonly` tuple is fine too).",
    r'''
function minMax(xs: any): any {
  const sorted = xs.toSorted((a: any, b: any) => a - b);
  return [sorted[0], sorted[sorted.length - 1]];
}
const [lo, hi] = minMax(input.split(/\s+/).map(Number));
console.log(`${lo}..${hi}`);
''', r'''
function minMax(xs: readonly number[]): [number, number] {
  const sorted = xs.toSorted((a, b) => a - b);
  return [sorted[0], sorted[sorted.length - 1]];
}
const [lo, hi] = minMax(input.split(/\s+/).map(Number));
console.log(`${lo}..${hi}`);
''', '''
type _P = Parameters<typeof minMax>[0];
type _R = ReturnType<typeof minMax>;
type _1 = Expect<Equal<IsAny<_P>, false>>;
type _2 = Expect<Equal<number[] extends _P ? (_P extends readonly number[] ? true : false) : false, true>>;
type _3 = Expect<Equal<IsAny<_R>, false>>;
type _4 = Expect<Equal<[number, number] extends _R ? (_R extends readonly [number, number] ? true : false) : false, true>>;
''', ["3 1 2", "5", "-1 10 4"],
    hints=["Without an annotation, `[a, b]` is inferred as `number[]` — say `[number, number]`."])

_dz(7, "tsm-w7-dz1", "Name the pair",
    "Write `Entry`: a tuple of a name (string) and a score (number). `parse` builds one per line and the sort reads the score at position 1.",
    r'''
type Entry = [name: string, score: number];
function parse(line: string): Entry {
  const [name, score] = line.split(":");
  return [name.trim(), Number(score)];
}
const entries = input.split("\n").map(parse);
const best = entries.toSorted((a, b) => b[1] - a[1])[0];
console.log(`${best[0]} ${best[1]}`);
console.log(entries.length);
''', "type Entry = [name: string, score: number];", '''
type _1 = Expect<Equal<Entry, [string, number]>>;
''', ["ada: 90\nbob: 72\ncy: 95", "solo: 1"],
    hints=["A tuple type lists each position's type: `[string, number]`.", "Labels such as `[name: string, score: number]` document it without changing it."])

_rf(7, "tsm-w7-rf1", "Stop mutating the input",
    "`sort` and `reverse` change the array in place — which is why the last line prints the sorted order instead of the order the numbers came in. Use the copying methods, so the last line prints the input order. No `.sort(` or `.reverse(` left.",
    r'''
const xs = input.split(/\s+/).map(Number);
const asc = xs.sort((a, b) => a - b);
const desc = [...asc].reverse();
console.log(asc.join(" "));
console.log(desc.join(" "));
console.log(xs.join(" "));
''', r'''
const xs = input.split(/\s+/).map(Number);
const asc = xs.toSorted((a, b) => a - b);
const desc = asc.toReversed();
console.log(asc.join(" "));
console.log(desc.join(" "));
console.log(xs.join(" "));
''', [".sort(", ".reverse("], ["3 1 2", "9 8 7 10"],
    hints=["ES2023 added `toSorted` and `toReversed`, which return new arrays."])

_dz(8, "tsm-w8-dz1", "Shape the orders",
    "Write the `Order` interface the code below reads: an `id` string, a list of `items` (each with `sku` string, `qty` number and `price` number), and an optional `note` string.",
    r'''
interface Order {
  id: string;
  items: { sku: string; qty: number; price: number }[];
  note?: string;
}
const orders: Order[] = JSON.parse(input);
for (const o of orders) {
  const total = o.items.reduce((s, i) => s + i.qty * i.price, 0);
  console.log(`${o.id}: ${total.toFixed(2)}${o.note ? " (" + o.note + ")" : ""}`);
}
''', '''interface Order {
  id: string;
  items: { sku: string; qty: number; price: number }[];
  note?: string;
}''', '''
type _1 = Expect<Equal<Order["id"], string>>;
type _2 = Expect<Equal<Order["items"][number], { sku: string; qty: number; price: number }>>;
type _3 = Expect<Equal<Order["note"], string | undefined>>;
type _4 = Expect<Equal<{} extends Pick<Order, "note"> ? true : false, true>>;
''', ['[{"id":"A1","items":[{"sku":"x","qty":2,"price":1.5}],"note":"gift"},{"id":"B2","items":[{"sku":"y","qty":1,"price":10},{"sku":"z","qty":3,"price":0.5}]}]'],
    hints=["`note` is sometimes missing: make it optional with `?`.", "`items` is an array of object types."])

_rt(8, "tsm-w8-rt1", "JSON with a shape",
    "Each user in the input has a `name` (string), `roles` (string array), `email` (string) and `age` (number). Replace every `any` — including the one on `JSON.parse`'s result — with types that say so.",
    r'''
function summarize(user: any): any {
  const { name, roles, ...rest } = user;
  return `${name} [${roles.join(",")}] ${Object.keys(rest).length} more`;
}
const users: any = JSON.parse(input);
for (const u of users) console.log(summarize(u));
''', r'''
type User = { name: string; roles: string[]; email: string; age: number };
function summarize(user: User): string {
  const { name, roles, ...rest } = user;
  return `${name} [${roles.join(",")}] ${Object.keys(rest).length} more`;
}
const users: User[] = JSON.parse(input);
for (const u of users) console.log(summarize(u));
''', '''
type _U = { name: string; roles: string[]; email: string; age: number };
type _1 = Expect<Equal<Parameters<typeof summarize>[0], _U>>;
type _2 = Expect<Equal<ReturnType<typeof summarize>, string>>;
type _3 = Expect<Equal<typeof users, _U[]>>;
''', ['[{"name":"ada","roles":["admin","dev"],"email":"a@x","age":36},{"name":"bo","roles":[],"email":"b@x","age":20}]'],
    hints=["Name the shape once with `type User = { ... }`.", "Annotate what `JSON.parse` returns — it is `any` until you say otherwise."])

_rf(8, "tsm-w8-rf1", "Destructure the point",
    "The loop reads `p.x` and `p.y` five times. Destructure `{ x, y }` in the loop header instead — no `p.x` or `p.y` left.",
    r'''
const points = input.split("\n").map((l) => {
  const [x, y] = l.split(",").map(Number);
  return { x, y };
});
for (const p of points) console.log(`(${p.x}, ${p.y}) -> ${Math.hypot(p.x, p.y).toFixed(1)}`);
''', r'''
const points = input.split("\n").map((l) => {
  const [x, y] = l.split(",").map(Number);
  return { x, y };
});
for (const { x, y } of points) console.log(`(${x}, ${y}) -> ${Math.hypot(x, y).toFixed(1)}`);
''', ["p.x", "p.y"], ["3,4\n1,1", "0,5"],
    hints=["`for (const { x, y } of points)`."])

# ---- Month 3 ----------------------------------------------------------------

_rt(9, "tsm-w9-rt1", "A typed word count",
    "Replace both `any`s: the map counts words (string keys, number values), and `top` is one `[word, count]` entry.",
    r'''
const counts: any = new Map();
for (const w of input.split(/\s+/)) counts.set(w, (counts.get(w) ?? 0) + 1);
const top: any = [...counts].sort((a: any, b: any) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
console.log(`${top[0]} ${top[1]}`);
console.log(counts.size);
''', r'''
const counts = new Map<string, number>();
for (const w of input.split(/\s+/)) counts.set(w, (counts.get(w) ?? 0) + 1);
const top = [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
console.log(`${top[0]} ${top[1]}`);
console.log(counts.size);
''', '''
type _1 = Expect<Equal<typeof counts, Map<string, number>>>;
type _2 = Expect<Equal<typeof top, [string, number]>>;
''', ["b a b c a b", "x"],
    hints=["`new Map<string, number>()` gives the map its types.", "Spreading a `Map<K, V>` gives `[K, V][]`, so `top` needs no annotation."])

_dz(9, "tsm-w9-dz1", "An adjacency map",
    "Write `Graph`: a map from each node's name to the set of names it is connected to.",
    r'''
type Graph = Map<string, Set<string>>;
function addEdge(g: Graph, a: string, b: string): void {
  if (!g.has(a)) g.set(a, new Set());
  if (!g.has(b)) g.set(b, new Set());
  g.get(a)!.add(b);
  g.get(b)!.add(a);
}
const g: Graph = new Map();
for (const pair of input.split("\n")) {
  const [a, b] = pair.split("-");
  addEdge(g, a, b);
}
for (const [node, nbrs] of [...g].sort((x, y) => x[0].localeCompare(y[0]))) {
  console.log(`${node}: ${[...nbrs].sort().join(",")}`);
}
''', "type Graph = Map<string, Set<string>>;", '''
type _1 = Expect<Equal<Graph, Map<string, Set<string>>>>;
''', ["a-b\nb-c\na-c", "x-y"],
    hints=["`Map<Key, Value>` where each value is a `Set<string>`."])

_rf(9, "tsm-w9-rf1", "Sets, not searches",
    "`includes` searches the whole array every time. Track what you have seen with `Set`s instead — no `.includes(` left. The output order must stay the same.",
    r'''
const seen: string[] = [];
const dupes: string[] = [];
for (const w of input.split(/\s+/)) {
  if (seen.includes(w) && !dupes.includes(w)) dupes.push(w);
  seen.push(w);
}
console.log(dupes.join(" ") || "none");
''', r'''
const seen = new Set<string>();
const dupes = new Set<string>();
for (const w of input.split(/\s+/)) {
  if (seen.has(w)) dupes.add(w);
  seen.add(w);
}
console.log([...dupes].join(" ") || "none");
''', [".includes("], ["a b a c b a", "x y z"],
    hints=["`Set.has` is a constant-time lookup, and a Set ignores a second `add` of the same value.", "A Set iterates in insertion order, so the output order is kept."])

_dz(10, "tsm-w10-dz1", "The sizes on sale",
    "Write `Size`: exactly the three sizes the shop sells, as a union of string literals. The price table is keyed by it, so a missing or extra size would be a compile error.",
    r'''
type Size = "S" | "M" | "L";
const PRICE: Record<Size, number> = { S: 10, M: 12, L: 14 };
const SIZES: readonly Size[] = ["S", "M", "L"];
let total = 0;
for (const token of input.split(/\s+/)) {
  const size = SIZES.find((s) => s === token);
  if (size === undefined) console.log(`skip ${token}`);
  else total += PRICE[size];
}
console.log(total);
''', 'type Size = "S" | "M" | "L";', '''
type _1 = Expect<Equal<Size, "S" | "M" | "L">>;
''', ["S M XL L", "M M"],
    hints=["A union of literal types: `\"S\" | \"M\" | \"L\"`."])

_rt(10, "tsm-w10-rt1", "What can a value be?",
    "`describe` handles numbers, booleans and strings. Replace the `any`s: the parameter is the union of those three, and the function returns a `string`.",
    r'''
function describe(v: any): any {
  if (typeof v === "number") return `number ${v.toFixed(1)}`;
  if (typeof v === "boolean") return v ? "yes" : "no";
  return `text ${v.toUpperCase()}`;
}
for (const t of input.split(/\s+/)) {
  const v = t === "true" || t === "false" ? t === "true" : Number.isNaN(Number(t)) ? t : Number(t);
  console.log(describe(v));
}
''', r'''
function describe(v: string | number | boolean): string {
  if (typeof v === "number") return `number ${v.toFixed(1)}`;
  if (typeof v === "boolean") return v ? "yes" : "no";
  return `text ${v.toUpperCase()}`;
}
for (const t of input.split(/\s+/)) {
  const v = t === "true" || t === "false" ? t === "true" : Number.isNaN(Number(t)) ? t : Number(t);
  console.log(describe(v));
}
''', '''
type _1 = Expect<Equal<Parameters<typeof describe>[0], string | number | boolean>>;
type _2 = Expect<Equal<ReturnType<typeof describe>, string>>;
''', ["3 true hello", "false 2.25"],
    hints=["A union type: `string | number | boolean`.", "Each `typeof` check narrows `v` for the line after it."])

_rt(11, "tsm-w11-rt1", "A port or nothing",
    "`parsePort` returns the port number, or `null` when the text is not a valid port. Replace the `any`s so the return type says exactly that.",
    r'''
function parsePort(raw: any): any {
  const n = Number(raw);
  return Number.isInteger(n) && n > 0 && n < 65536 ? n : null;
}
for (const t of input.split(/\s+/)) {
  const port = parsePort(t);
  console.log(port === null ? `bad ${t}` : `port ${port}`);
}
''', r'''
function parsePort(raw: string): number | null {
  const n = Number(raw);
  return Number.isInteger(n) && n > 0 && n < 65536 ? n : null;
}
for (const t of input.split(/\s+/)) {
  const port = parsePort(t);
  console.log(port === null ? `bad ${t}` : `port ${port}`);
}
''', '''
type _1 = Expect<Equal<Parameters<typeof parsePort>[0], string>>;
type _2 = Expect<Equal<ReturnType<typeof parsePort>, number | null>>;
''', ["80 abc 70000 443"],
    hints=["`number | null` — and callers must check for `null` before using it."])

_dz(11, "tsm-w11-dz1", "A contact, with gaps",
    "Write `Contact`: a `name` (string), an optional `email` (string), and an optional `phone` that is a string or explicitly `null` when the number was withdrawn.",
    r'''
type Contact = { name: string; email?: string; phone?: string | null };
function reach(c: Contact): string {
  return c.email ?? c.phone ?? `no way to reach ${c.name}`;
}
const contacts: Contact[] = JSON.parse(input);
for (const c of contacts) console.log(reach(c));
''', "type Contact = { name: string; email?: string; phone?: string | null };", '''
type _1 = Expect<Equal<Contact["name"], string>>;
type _2 = Expect<Equal<Contact["email"], string | undefined>>;
type _3 = Expect<Equal<Contact["phone"], string | null | undefined>>;
type _4 = Expect<Equal<{} extends Pick<Contact, "email" | "phone"> ? true : false, true>>;
''', ['[{"name":"ada","email":"a@x"},{"name":"bo","phone":"555"},{"name":"cy","phone":null},{"name":"di","email":"d@x","phone":"1"}]'],
    hints=["Optional means `?:` — the key may be missing.", "`phone?: string | null` allows missing, a string, or `null`."])

_rf(11, "tsm-w11-rf1", "Narrow instead of insisting",
    "`m.get(key)!` asserts the value is there — it happens to be, after `has`, but the compiler cannot see that. Read the value once and narrow it with a check. No `!.` left.",
    r'''
const m = new Map<string, number>();
for (const pair of input.split(",")) {
  const [k, v] = pair.split("=");
  m.set(k.trim(), Number(v));
}
for (const key of ["a", "b", "c"]) {
  if (m.has(key)) console.log(`${key}=${m.get(key)!.toFixed(1)}`);
  else console.log(`${key} missing`);
}
''', r'''
const m = new Map<string, number>();
for (const pair of input.split(",")) {
  const [k, v] = pair.split("=");
  m.set(k.trim(), Number(v));
}
for (const key of ["a", "b", "c"]) {
  const value = m.get(key);
  if (value !== undefined) console.log(`${key}=${value.toFixed(1)}`);
  else console.log(`${key} missing`);
}
''', ["!."], ["a=1, c=2.5", "b=3"],
    hints=["`const value = m.get(key)` is `number | undefined`; `if (value !== undefined)` narrows it."])

_dz(12, "tsm-w12-dz1", "Success or a reason",
    "Write `Parsed`: a discriminated union on `ok` — `{ ok: true; value: number }` or `{ ok: false; reason: string }`.",
    r'''
type Parsed = { ok: true; value: number } | { ok: false; reason: string };
function parse(t: string): Parsed {
  const n = Number(t);
  if (t === "") return { ok: false, reason: "empty" };
  if (Number.isNaN(n)) return { ok: false, reason: `not a number: ${t}` };
  return { ok: true, value: n };
}
for (const t of input.split(",")) {
  const r = parse(t.trim());
  console.log(r.ok ? r.value * 2 : r.reason);
}
''', "type Parsed = { ok: true; value: number } | { ok: false; reason: string };", '''
type _1 = Expect<Equal<Parsed, { ok: true; value: number } | { ok: false; reason: string }>>;
''', ["4, x, , 2.5"],
    hints=["Two object types joined by `|`, each with a literal `ok`."])

_rt(12, "tsm-w12-rt1", "Area of a shape",
    "`Shape` is already a discriminated union. Replace `area`'s `any`s: it takes a `Shape` and returns a number — and with every case handled, no `undefined` sneaks into the return type.",
    r'''
type Shape = { kind: "circle"; r: number } | { kind: "rect"; w: number; h: number };
function area(s: any): any {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r ** 2;
    case "rect":
      return s.w * s.h;
  }
}
for (const line of input.split("\n")) {
  const [k, a, b] = line.split(/\s+/);
  const s: Shape = k === "circle" ? { kind: "circle", r: Number(a) } : { kind: "rect", w: Number(a), h: Number(b) };
  console.log(area(s).toFixed(2));
}
''', r'''
type Shape = { kind: "circle"; r: number } | { kind: "rect"; w: number; h: number };
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.r ** 2;
    case "rect":
      return s.w * s.h;
  }
}
for (const line of input.split("\n")) {
  const [k, a, b] = line.split(/\s+/);
  const s: Shape = k === "circle" ? { kind: "circle", r: Number(a) } : { kind: "rect", w: Number(a), h: Number(b) };
  console.log(area(s).toFixed(2));
}
''', '''
type _1 = Expect<Equal<Parameters<typeof area>[0], { kind: "circle"; r: number } | { kind: "rect"; w: number; h: number }>>;
type _2 = Expect<Equal<ReturnType<typeof area>, number>>;
''', ["circle 1\nrect 2 3", "rect 1 1"],
    hints=["`s: Shape` makes each `case` narrow `s`.", "Because the switch is exhaustive, the compiler knows the end of the function is unreachable."])

_rf(12, "tsm-w12-rf1", "Let the compiler count the cases",
    "The `default` branch quietly ignores any command added later. Remove it: with every case handled and a `number` return type, the compiler proves the switch is exhaustive — and would flag a new command. No `default` left.",
    r'''
type Cmd = { type: "add"; n: number } | { type: "mul"; n: number } | { type: "reset" };
function apply(acc: number, c: Cmd): number {
  switch (c.type) {
    case "add":
      return acc + c.n;
    case "mul":
      return acc * c.n;
    case "reset":
      return 0;
    default:
      return acc;
  }
}
let acc = 0;
for (const line of input.split("\n")) {
  const [t, n] = line.split(" ");
  const c: Cmd = t === "reset" ? { type: "reset" } : { type: t === "mul" ? "mul" : "add", n: Number(n) };
  acc = apply(acc, c);
  console.log(acc);
}
''', r'''
type Cmd = { type: "add"; n: number } | { type: "mul"; n: number } | { type: "reset" };
function apply(acc: number, c: Cmd): number {
  switch (c.type) {
    case "add":
      return acc + c.n;
    case "mul":
      return acc * c.n;
    case "reset":
      return 0;
  }
}
let acc = 0;
for (const line of input.split("\n")) {
  const [t, n] = line.split(" ");
  const c: Cmd = t === "reset" ? { type: "reset" } : { type: t === "mul" ? "mul" : "add", n: Number(n) };
  acc = apply(acc, c);
  console.log(acc);
}
''', ["default"], ["add 3\nmul 4\nreset\nadd 2", "mul 5"],
    hints=["Delete the `default` branch — nothing else needs to change."])

_dz(13, "tsm-w13-dz1", "A middleware chain",
    "Write `Middleware`: a function that takes the current string and a `next` callback (string in, string out), and returns a string.",
    r'''
type Middleware = (value: string, next: (v: string) => string) => string;
const trim: Middleware = (v, next) => next(v.trim());
const upper: Middleware = (v, next) => next(v.toUpperCase());
const exclaim: Middleware = (v, next) => next(v + "!");
function run(chain: Middleware[], value: string): string {
  const step = (i: number, v: string): string => (i === chain.length ? v : chain[i](v, (n) => step(i + 1, n)));
  return step(0, value);
}
for (const line of input.split("\n")) console.log(run([trim, upper, exclaim], line));
''', "type Middleware = (value: string, next: (v: string) => string) => string;", '''
type _1 = Expect<Equal<Parameters<Middleware>[0], string>>;
type _2 = Expect<Equal<Parameters<Middleware>[1], (v: string) => string>>;
type _3 = Expect<Equal<ReturnType<Middleware>, string>>;
''', ["  hi \nthere", "x"],
    hints=["A function type whose second parameter is itself a function type."])

_rt(13, "tsm-w13-rt1", "Memo, typed",
    "`memo` wraps a number-to-number function with a cache. Replace the `any`s: it takes a `(n: number) => number` and returns one.",
    r'''
function memo(fn: any): any {
  const cache = new Map<number, number>();
  return (n: number) => {
    const hit = cache.get(n);
    if (hit !== undefined) return hit;
    const v = fn(n);
    cache.set(n, v);
    return v;
  };
}
let calls = 0;
const square = memo((n: number) => {
  calls++;
  return n * n;
});
for (const t of input.split(/\s+/)) console.log(square(Number(t)));
console.log(`calls ${calls}`);
''', r'''
function memo(fn: (n: number) => number): (n: number) => number {
  const cache = new Map<number, number>();
  return (n: number) => {
    const hit = cache.get(n);
    if (hit !== undefined) return hit;
    const v = fn(n);
    cache.set(n, v);
    return v;
  };
}
let calls = 0;
const square = memo((n: number) => {
  calls++;
  return n * n;
});
for (const t of input.split(/\s+/)) console.log(square(Number(t)));
console.log(`calls ${calls}`);
''', '''
type _1 = Expect<Equal<Parameters<typeof memo>[0], (n: number) => number>>;
type _2 = Expect<Equal<ReturnType<typeof memo>, (n: number) => number>>;
''', ["2 3 2 2 4"],
    hints=["Both the parameter and the result are `(n: number) => number`."])

# ---- Month 4 (strict+indexed from here) ---------------------------------------

_rt(14, "tsm-w14-rt1", "Command-line flags",
    "`flag` finds the value after a flag like `--port`, or `undefined` when the flag is absent. Replace the `any`s — remembering that with `noUncheckedIndexedAccess` an array read may be `undefined`.",
    r'''
const args: any = input.split(/\s+/);
function flag(name: any): any {
  const i = args.indexOf(name);
  return i === -1 ? undefined : args[i + 1];
}
console.log(flag("--port") ?? "3000");
console.log(flag("--host") ?? "localhost");
''', r'''
const args = input.split(/\s+/);
function flag(name: string): string | undefined {
  const i = args.indexOf(name);
  return i === -1 ? undefined : args[i + 1];
}
console.log(flag("--port") ?? "3000");
console.log(flag("--host") ?? "localhost");
''', '''
type _1 = Expect<Equal<typeof args, string[]>>;
type _2 = Expect<Equal<Parameters<typeof flag>[0], string>>;
type _3 = Expect<Equal<ReturnType<typeof flag>, string | undefined>>;
''', ["--port 8080", "--host example.org --port 1", "--verbose"],
    hints=["`args[i + 1]` is `string | undefined` under the week's strictness — and so is the result."])

_dz(14, "tsm-w14-dz1", "Environment settings",
    "Write `Env`: `NODE_ENV` is exactly `\"development\"` or `\"production\"`, `PORT` is a number and `DEBUG` a boolean.",
    r'''
type Env = { NODE_ENV: "development" | "production"; PORT: number; DEBUG: boolean };
function loadEnv(pairs: string[]): Env {
  const raw: Record<string, string> = {};
  for (const p of pairs) {
    const [k = "", v = ""] = p.split("=");
    raw[k] = v;
  }
  return {
    NODE_ENV: raw["NODE_ENV"] === "production" ? "production" : "development",
    PORT: Number(raw["PORT"] ?? "3000"),
    DEBUG: raw["DEBUG"] === "1",
  };
}
const env = loadEnv(input.split(/\s+/));
console.log(`${env.NODE_ENV} ${env.PORT} ${env.DEBUG}`);
''', 'type Env = { NODE_ENV: "development" | "production"; PORT: number; DEBUG: boolean };', '''
type _1 = Expect<Equal<Env, { NODE_ENV: "development" | "production"; PORT: number; DEBUG: boolean }>>;
''', ["NODE_ENV=production PORT=80", "DEBUG=1"],
    hints=["`NODE_ENV` is a union of two string literals, not `string`."])

_rf(15, "tsm-w15-rf1", "Check, don't assert",
    "Each `as Rgb` tells the compiler to trust the literal — so a colour missing a channel would compile. Replace them with one `satisfies` on the whole object, which checks every entry and keeps the keys. No `as Rgb` left.",
    r'''
type Rgb = { r: number; g: number; b: number };
const colours = {
  red: { r: 255, g: 0, b: 0 } as Rgb,
  teal: { r: 0, g: 128, b: 128 } as Rgb,
};
const hex = (c: Rgb) => "#" + [c.r, c.g, c.b].map((n) => n.toString(16).padStart(2, "0")).join("");
for (const name of input.split(/\s+/)) {
  const c = name === "red" ? colours.red : name === "teal" ? colours.teal : undefined;
  console.log(c ? hex(c) : `unknown ${name}`);
}
''', r'''
type Rgb = { r: number; g: number; b: number };
const colours = {
  red: { r: 255, g: 0, b: 0 },
  teal: { r: 0, g: 128, b: 128 },
} satisfies Record<string, Rgb>;
const hex = (c: Rgb) => "#" + [c.r, c.g, c.b].map((n) => n.toString(16).padStart(2, "0")).join("");
for (const name of input.split(/\s+/)) {
  const c = name === "red" ? colours.red : name === "teal" ? colours.teal : undefined;
  console.log(c ? hex(c) : `unknown ${name}`);
}
''', ["as Rgb"], ["red teal blue"],
    hints=["`{ ... } satisfies Record<string, Rgb>` checks every value against `Rgb`."])

_rt(15, "tsm-w15-rt1", "Merging settings",
    "`merge` overlays `b` on `a`. Here `a` is `{ host: string; port: number }` and `b` is `{ port: number }`. Replace the `any`s so the result's type is `{ host: string; port: number }`.",
    r'''
function merge(a: any, b: any): any {
  return { ...a, ...b };
}
const base = { host: "localhost", port: 80 };
const merged = merge(base, { port: Number(input) });
console.log(`${merged.host}:${merged.port}`);
''', r'''
function merge(a: { host: string; port: number }, b: { port: number }): { host: string; port: number } {
  return { ...a, ...b };
}
const base = { host: "localhost", port: 80 };
const merged = merge(base, { port: Number(input) });
console.log(`${merged.host}:${merged.port}`);
''', '''
type _1 = Expect<Equal<Parameters<typeof merge>[0], { host: string; port: number }>>;
type _2 = Expect<Equal<Parameters<typeof merge>[1], { port: number }>>;
type _3 = Expect<Equal<ReturnType<typeof merge>, { host: string; port: number }>>;
''', ["8080", "443"],
    hints=["Spreading two objects gives their combined properties — the later one wins for `port`."])

_dz(15, "tsm-w15-dz1", "Only what is needed",
    "Write `Named`: the smallest type `greetAll` needs — just a `name` string. The people passed in carry more than that, and structural typing lets them through.",
    r'''
type Named = { name: string };
function greetAll(xs: readonly Named[]): string[] {
  return xs.map((x) => `hi ${x.name}`);
}
const people = input.split(",").map((s) => ({ name: s.trim(), joined: 2020 }));
console.log(greetAll(people).join("; "));
''', "type Named = { name: string };", '''
type _1 = Expect<Equal<Named, { name: string }>>;
''', ["ada, bo", "cy"],
    hints=["Ask for exactly what the function reads — a type with one property."])

_dz(16, "tsm-w16-dz1", "An email you can trust",
    "Write `Email`: a branded string. A plain `string` must not be assignable to it, but an `Email` must still be usable as a string. `parseEmail` is the only way to make one.",
    r'''
type Email = string & { readonly __brand: "Email" };
function parseEmail(s: string): Email | null {
  return /^[^@\s]+@[^@\s]+\.[a-z]+$/.test(s) ? (s as Email) : null;
}
function send(to: Email, body: string): string {
  return `to ${to}: ${body}`;
}
for (const line of input.split("\n")) {
  const [addr = "", ...rest] = line.split(" ");
  const e = parseEmail(addr);
  console.log(e === null ? `rejected ${addr}` : send(e, rest.join(" ")));
}
''', 'type Email = string & { readonly __brand: "Email" };', '''
type _1 = Expect<Equal<string extends Email ? true : false, false>>;
type _2 = Expect<Equal<Email extends string ? true : false, true>>;
type _3 = Expect<Equal<IsAny<Email>, false>>;
''', ["ada@x.io hello there\nnot-an-email hi"],
    hints=["Intersect `string` with an object type that only exists at compile time.", "`string & { readonly __brand: \"Email\" }`."])

_rt(16, "tsm-w16-rt1", "Rows nobody may change",
    "Replace the `any`s. `totals` must not be able to modify the rows it is given: type the parameter as a readonly array of `{ readonly qty: number; readonly price: number }`, and the result as `number[]`.",
    r'''
function totals(rows: any): any {
  return rows.map((r: any) => r.qty * r.price);
}
const rows = input.split("\n").map((l) => {
  const [qty = "0", price = "0"] = l.split(" ");
  return { qty: Number(qty), price: Number(price) };
});
console.log(totals(rows).join(" "));
''', r'''
function totals(rows: readonly { readonly qty: number; readonly price: number }[]): number[] {
  return rows.map((r) => r.qty * r.price);
}
const rows = input.split("\n").map((l) => {
  const [qty = "0", price = "0"] = l.split(" ");
  return { qty: Number(qty), price: Number(price) };
});
console.log(totals(rows).join(" "));
''', '''
type _1 = Expect<Equal<Parameters<typeof totals>[0], readonly { readonly qty: number; readonly price: number }[]>>;
type _2 = Expect<Equal<ReturnType<typeof totals>, number[]>>;
''', ["2 3\n1 10", "5 5"],
    hints=["`readonly T[]` forbids `push`; `readonly` on each property forbids reassigning it."])

_rf(16, "tsm-w16-rf1", "Build it without mutation",
    "The cart is built by pushing and bumping `qty` in place. Build it immutably instead — each step returns a new array (spread, `map`) — with no `.push(` or `+=` left. Same output.",
    r'''
const cart: { sku: string; qty: number }[] = [];
for (const token of input.split(/\s+/)) {
  const found = cart.find((l) => l.sku === token);
  if (found) found.qty += 1;
  else cart.push({ sku: token, qty: 1 });
}
console.log(cart.map((l) => `${l.sku}x${l.qty}`).join(" "));
''', r'''
type Line = { readonly sku: string; readonly qty: number };
const empty: readonly Line[] = [];
const cart = input.split(/\s+/).reduce(
  (acc, sku) =>
    acc.some((l) => l.sku === sku)
      ? acc.map((l) => (l.sku === sku ? { ...l, qty: l.qty + 1 } : l))
      : [...acc, { sku, qty: 1 }],
  empty,
);
console.log(cart.map((l) => `${l.sku}x${l.qty}`).join(" "));
''', [".push(", "+="], ["a b a c a", "x"],
    hints=["`reduce` with an empty readonly array as the seed.", "Existing SKU: `map` to a copy with `qty + 1`; new SKU: `[...acc, { sku, qty: 1 }]`."])

_dz(17, "tsm-w17-dz1", "Derive, don't restate",
    "Write `NewTask` (what `add` needs: a `Task` without `id` or `done`) and `TaskPatch` (any of a `Task`'s fields except `id`, all optional) — derived from `Task` with utility types, not written out.",
    r'''
type Task = { id: number; title: string; done: boolean; tags: string[] };
type NewTask = Omit<Task, "id" | "done">;
type TaskPatch = Partial<Omit<Task, "id">>;
let nextId = 1;
const tasks: Task[] = [];
function add(t: NewTask): Task {
  const task = { ...t, id: nextId++, done: false };
  tasks.push(task);
  return task;
}
function patch(id: number, p: TaskPatch): void {
  const i = tasks.findIndex((t) => t.id === id);
  const current = tasks[i];
  if (current) tasks[i] = { ...current, ...p };
}
for (const line of input.split("\n")) {
  const [cmd = "", ...rest] = line.split(" ");
  if (cmd === "add") add({ title: rest.join(" "), tags: [] });
  else if (cmd === "done") patch(Number(rest[0]), { done: true });
}
for (const t of tasks) console.log(`${t.id} ${t.done ? "x" : "-"} ${t.title}`);
''', '''type NewTask = Omit<Task, "id" | "done">;
type TaskPatch = Partial<Omit<Task, "id">>;''', '''
type _1 = Expect<Equal<NewTask, { title: string; tags: string[] }>>;
type _2 = Expect<Equal<TaskPatch, { title?: string; done?: boolean; tags?: string[] }>>;
''', ["add write tests\nadd ship it\ndone 1"],
    hints=["`Omit<Task, \"id\" | \"done\">`.", "`Partial` makes every remaining property optional."])

_rt(17, "tsm-w17-rt1", "Overrides over defaults",
    "`configure` overlays some settings on the defaults. Replace the `any`s: the overrides are any subset of the defaults' fields (derive that type — don't write it out), and the result has every field.",
    r'''
const DEFAULTS = { retries: 3, timeoutMs: 1000, verbose: false };
function configure(overrides: any): any {
  return { ...DEFAULTS, ...overrides };
}
const o: { retries?: number; timeoutMs?: number; verbose?: boolean } = {};
for (const pair of input.split(/\s+/)) {
  const [k, v = ""] = pair.split("=");
  if (k === "retries") o.retries = Number(v);
  else if (k === "timeoutMs") o.timeoutMs = Number(v);
  else if (k === "verbose") o.verbose = v === "true";
}
const c = configure(o);
console.log(`${c.retries} ${c.timeoutMs} ${c.verbose}`);
''', r'''
const DEFAULTS = { retries: 3, timeoutMs: 1000, verbose: false };
type Settings = typeof DEFAULTS;
function configure(overrides: Partial<Settings>): Settings {
  return { ...DEFAULTS, ...overrides };
}
const o: { retries?: number; timeoutMs?: number; verbose?: boolean } = {};
for (const pair of input.split(/\s+/)) {
  const [k, v = ""] = pair.split("=");
  if (k === "retries") o.retries = Number(v);
  else if (k === "timeoutMs") o.timeoutMs = Number(v);
  else if (k === "verbose") o.verbose = v === "true";
}
const c = configure(o);
console.log(`${c.retries} ${c.timeoutMs} ${c.verbose}`);
''', '''
type _1 = Expect<Equal<Parameters<typeof configure>[0], { retries?: number; timeoutMs?: number; verbose?: boolean }>>;
type _2 = Expect<Equal<ReturnType<typeof configure>, { retries: number; timeoutMs: number; verbose: boolean }>>;
''', ["retries=5 verbose=true", "timeoutMs=250"],
    hints=["`typeof DEFAULTS` names the full settings type.", "`Partial<...>` of it is the overrides."])

_rt(18, "tsm-w18-rt1", "Group by, generically",
    "Make `groupBy` generic: for a list of `T` and a key function from `T` to `string`, it returns `Record<string, T[]>`. No `any` left.",
    r'''
function groupBy(xs: any, key: any): any {
  const out: any = {};
  for (const x of xs) (out[key(x)] ??= []).push(x);
  return out;
}
const words = input.split(/\s+/);
const byFirst = groupBy(words, (w: string) => w[0] ?? "");
for (const k of Object.keys(byFirst).sort()) console.log(`${k}: ${byFirst[k]!.join(",")}`);
''', r'''
function groupBy<T>(xs: readonly T[], key: (x: T) => string): Record<string, T[]> {
  const out: Record<string, T[]> = {};
  for (const x of xs) (out[key(x)] ??= []).push(x);
  return out;
}
const words = input.split(/\s+/);
const byFirst = groupBy(words, (w: string) => w[0] ?? "");
for (const k of Object.keys(byFirst).sort()) console.log(`${k}: ${byFirst[k]!.join(",")}`);
''', '''
const _g = groupBy([1, 2, 3], (n) => (n % 2 ? "odd" : "even"));
type _1 = Expect<Equal<typeof _g, Record<string, number[]>>>;
const _h = groupBy(["a"], (s) => s);
type _2 = Expect<Equal<typeof _h, Record<string, string[]>>>;
''', ["apple avocado banana blueberry cherry", "kiwi"],
    hints=["One type parameter `T` links the list, the key function's argument and the groups.", "`function groupBy<T>(xs: readonly T[], key: (x: T) => string): Record<string, T[]>`."])

_dz(18, "tsm-w18-dz1", "A page of anything",
    "Write the generic `Page<T>`: the `items` on this page (an array of `T`), the `page` number and the `total` number of pages.",
    r'''
type Page<T> = { items: T[]; page: number; total: number };
function paginate<T>(all: readonly T[], page: number, size: number): Page<T> {
  return { items: all.slice((page - 1) * size, page * size), page, total: Math.ceil(all.length / size) };
}
const [pageText = "1", sizeText = "2", ...rest] = input.split(/\s+/);
const p = paginate(rest, Number(pageText), Number(sizeText));
console.log(`page ${p.page}/${p.total}: ${p.items.join(" ")}`);
''', "type Page<T> = { items: T[]; page: number; total: number };", '''
type _1 = Expect<Equal<Page<number>, { items: number[]; page: number; total: number }>>;
type _2 = Expect<Equal<Page<string>["items"], string[]>>;
''', ["2 2 a b c d e", "1 3 x"],
    hints=["A type alias can take a type parameter: `type Page<T> = { ... }`."])

_rf(18, "tsm-w18-rf1", "One function, not two",
    "`firstNum` and `firstStr` are the same function twice. Replace them with one generic `first<T>` — neither old name may remain.",
    r'''
function firstNum(xs: readonly number[]): number | undefined {
  return xs[0];
}
function firstStr(xs: readonly string[]): string | undefined {
  return xs[0];
}
const words = input.split(/\s+/);
console.log(firstStr(words) ?? "none");
console.log(firstNum(words.map((w) => w.length)) ?? "none");
''', r'''
function first<T>(xs: readonly T[]): T | undefined {
  return xs[0];
}
const words = input.split(/\s+/);
console.log(first(words) ?? "none");
console.log(first(words.map((w) => w.length)) ?? "none");
''', ["firstNum", "firstStr"], ["hello world", "a"],
    hints=["`function first<T>(xs: readonly T[]): T | undefined`."])

_dz(19, "tsm-w19-dz1", "Operations from a table",
    "Write `Op`: the names of the handlers in `HANDLERS`, derived from the object itself so that adding a handler adds an operation.",
    r'''
const HANDLERS = {
  upper: (s: string) => s.toUpperCase(),
  reverse: (s: string) => [...s].reverse().join(""),
  length: (s: string) => String(s.length),
};
type Op = keyof typeof HANDLERS;
function isOp(s: string): s is Op {
  return s in HANDLERS;
}
for (const line of input.split("\n")) {
  const [op = "", ...words] = line.split(" ");
  console.log(isOp(op) ? HANDLERS[op](words.join(" ")) : `unknown op ${op}`);
}
''', "type Op = keyof typeof HANDLERS;", '''
type _1 = Expect<Equal<Op, "upper" | "reverse" | "length">>;
''', ["upper hi there\nreverse abc\nnope x\nlength four"],
    hints=["`typeof HANDLERS` is the object's type; `keyof` of that is its keys."])

_rt(19, "tsm-w19-rt1", "A typed getter",
    "`get(key)` reads one setting. Replace the `any`s so the key must be one of `config`'s keys and the result has that key's type — `get(\"port\")` is a `number`, `get(\"host\")` a `string`.",
    r'''
const config = { host: "localhost", port: 8080, tls: false };
function get(key: any): any {
  return config[key];
}
for (const k of input.split(/\s+/)) {
  if (k === "host" || k === "port" || k === "tls") console.log(`${k}=${get(k)}`);
  else console.log(`no ${k}`);
}
''', r'''
const config = { host: "localhost", port: 8080, tls: false };
function get<K extends keyof typeof config>(key: K): (typeof config)[K] {
  return config[key];
}
for (const k of input.split(/\s+/)) {
  if (k === "host" || k === "port" || k === "tls") console.log(`${k}=${get(k)}`);
  else console.log(`no ${k}`);
}
''', '''
const _p = get("port");
const _h = get("host");
type _1 = Expect<Equal<typeof _p, number>>;
type _2 = Expect<Equal<typeof _h, string>>;
''', ["port host tls nope"],
    hints=["A type parameter constrained to the keys: `K extends keyof typeof config`.", "The result is the indexed access type `(typeof config)[K]`."])

_dz(20, "tsm-w20-dz1", "An error per field",
    "Write the mapped type `Errors<T>`: for every key of `T`, an optional error message string.",
    r'''
type Form = { name: string; age: number; email: string };
type Errors<T> = { [K in keyof T]?: string };
function validate(f: Form): Errors<Form> {
  const e: Errors<Form> = {};
  if (f.name.trim() === "") e.name = "required";
  if (!Number.isInteger(f.age) || f.age < 0) e.age = "must be a whole number";
  if (!f.email.includes("@")) e.email = "invalid";
  return e;
}
for (const line of input.split("\n")) {
  const [name = "", age = "", email = ""] = line.split(",");
  const errs = validate({ name, age: Number(age), email });
  const list = Object.entries(errs).map(([k, v]) => `${k} ${v}`);
  console.log(list.length ? list.join("; ") : "ok");
}
''', "type Errors<T> = { [K in keyof T]?: string };", '''
type _1 = Expect<Equal<Errors<{ a: number; b: string }>, { a?: string; b?: string }>>;
''', ["ada,36,a@x\n,x,nope"],
    hints=["`{ [K in keyof T]?: string }` — map over the keys, with `?` on each."])

_rt(20, "tsm-w20-rt1", "Flags from names",
    "`toggles` turns a list of names into an object with one `false` flag per name. Replace the `any`s so that `toggles([\"a\", \"b\"])` has the type `{ a: boolean; b: boolean }`.",
    r'''
function toggles(keys: any): any {
  const out: any = {};
  for (const k of keys) out[k] = false;
  return out;
}
const t = toggles(input.split(/\s+/));
console.log(Object.keys(t).join(","));
console.log(Object.values(t).every((v) => v === false));
''', r'''
function toggles<K extends string>(keys: readonly K[]): { [P in K]: boolean } {
  const out = {} as { [P in K]: boolean };
  for (const k of keys) out[k] = false;
  return out;
}
const t = toggles(input.split(/\s+/));
console.log(Object.keys(t).join(","));
console.log(Object.values(t).every((v) => v === false));
''', '''
const _t = toggles(["a", "b"]);
type _1 = Expect<Equal<typeof _t, { a: boolean; b: boolean }>>;
''', ["dark compact beta"],
    hints=["Capture the names as a type parameter `K extends string` so the literals are kept.", "The result is the mapped type `{ [P in K]: boolean }`."])

_dz(21, "tsm-w21-dz1", "The element of a list",
    "Write `ElementOf<T>`: the element type of an array or readonly array `T`, and `never` for anything else. `Size` is derived with it.",
    r'''
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;
const SIZES = ["S", "M", "L", "XL"] as const;
type Size = ElementOf<typeof SIZES>;
const ORDER: Record<Size, number> = { S: 0, M: 1, L: 2, XL: 3 };
const isSize = (s: string): s is Size => (SIZES as readonly string[]).includes(s);
const given = input.split(/\s+/).filter(isSize);
console.log(given.toSorted((a, b) => ORDER[a] - ORDER[b]).join(" "));
''', "type ElementOf<T> = T extends readonly (infer E)[] ? E : never;", '''
type _1 = Expect<Equal<ElementOf<string[]>, string>>;
type _2 = Expect<Equal<ElementOf<readonly [1, 2]>, 1 | 2>>;
type _3 = Expect<Equal<ElementOf<number>, never>>;
''', ["XL S M foo L S"],
    hints=["A conditional type with `infer`: `T extends readonly (infer E)[] ? E : never`.", "`readonly` in the pattern matches mutable arrays too."])

_dz(22, "tsm-w22-dz1", "Getter names",
    "Write `Getter<K>`: for a property name like `\"name\"`, the getter name `\"getName\"` — a template literal type with the name capitalised.",
    r'''
type Getter<K extends string> = `get${Capitalize<K>}`;
const user = { name: "ada", city: "london" };
type User = typeof user;
const getters = {
  getName: () => user.name,
  getCity: () => user.city,
} satisfies { [K in keyof User as Getter<K>]: () => string };
for (const k of input.split(/\s+/)) {
  if (k === "getName" || k === "getCity") console.log(getters[k]());
  else console.log(`no ${k}`);
}
''', "type Getter<K extends string> = `get${Capitalize<K>}`;", '''
type _1 = Expect<Equal<Getter<"name">, "getName">>;
type _2 = Expect<Equal<Getter<"a" | "b">, "getA" | "getB">>;
''', ["getCity getName getAge"],
    hints=["A template literal type: `` `get${...}` ``.", "`Capitalize<K>` upper-cases the first letter."])

# ---- Month 6 ----------------------------------------------------------------

_dz(23, "tsm-w23-dz1", "What an account promises",
    "Write the `Account` interface that `Wallet` implements: a readonly `id` string, a `balance()` method returning a number, and `deposit(amount: number)` returning nothing.",
    r'''
interface Account {
  readonly id: string;
  balance(): number;
  deposit(amount: number): void;
}
class Wallet implements Account {
  readonly id: string;
  #cents = 0;
  constructor(id: string) {
    this.id = id;
  }
  balance(): number {
    return this.#cents / 100;
  }
  deposit(amount: number): void {
    this.#cents += Math.round(amount * 100);
  }
}
const w = new Wallet("w1");
for (const t of input.split(/\s+/)) w.deposit(Number(t));
console.log(`${w.id} ${w.balance().toFixed(2)}`);
''', '''interface Account {
  readonly id: string;
  balance(): number;
  deposit(amount: number): void;
}''', '''
type _1 = Expect<Equal<Account["id"], string>>;
type _2 = Expect<Equal<Account["balance"], () => number>>;
type _3 = Expect<Equal<Account["deposit"], (amount: number) => void>>;
type _4 = Expect<Equal<Readonly<Pick<Account, "id">>, Pick<Account, "id">>>;
''', ["1.10 2.20", "0.1 0.2"],
    hints=["Method signatures in an interface: `balance(): number;`.", "`readonly id: string;` — the implementing class keeps it readonly too."])

_rt(23, "tsm-w23-rt1", "A typed stack",
    "Replace every `any` in `Stack`: it holds numbers, `push` returns the stack itself so calls chain, `pop` may find it empty, and `size` is a number.",
    r'''
class Stack {
  private items: any = [];
  push(x: any): any {
    this.items.push(x);
    return this;
  }
  pop(): any {
    return this.items.pop();
  }
  get size(): any {
    return this.items.length;
  }
}
const s = new Stack();
for (const line of input.split("\n")) {
  const [cmd, arg] = line.split(" ");
  if (cmd === "push") s.push(Number(arg));
  else console.log(s.pop() ?? "empty");
}
console.log(`size ${s.size}`);
''', r'''
class Stack {
  private items: number[] = [];
  push(x: number): this {
    this.items.push(x);
    return this;
  }
  pop(): number | undefined {
    return this.items.pop();
  }
  get size(): number {
    return this.items.length;
  }
}
const s = new Stack();
for (const line of input.split("\n")) {
  const [cmd, arg] = line.split(" ");
  if (cmd === "push") s.push(Number(arg));
  else console.log(s.pop() ?? "empty");
}
console.log(`size ${s.size}`);
''', '''
type _1 = Expect<Equal<Parameters<Stack["push"]>[0], number>>;
type _2 = Expect<Equal<ReturnType<Stack["pop"]>, number | undefined>>;
type _3 = Expect<Equal<Stack["size"], number>>;
type _4 = Expect<Equal<ReturnType<Stack["push"]>, Stack>>;
''', ["push 1\npush 2\npop\npop\npop", "push 7"],
    hints=["`pop` on an empty array returns `undefined`, so say `number | undefined`.", "Returning `this` (or `Stack`) lets calls chain."])

_rf(23, "tsm-w23-rf1", "Private for real",
    "`private` is only a compile-time rule — at runtime anyone can read `count`. Make both fields JavaScript private fields (`#`) instead. No `private ` left; same output.",
    r'''
class Counter {
  private count = 0;
  private readonly step: number;
  constructor(step: number) {
    this.step = step;
  }
  tick(): number {
    this.count += this.step;
    return this.count;
  }
}
const [step = "1", times = "1"] = input.split(/\s+/);
const c = new Counter(Number(step));
const seen: number[] = [];
for (let i = 0; i < Number(times); i++) seen.push(c.tick());
console.log(seen.join(" "));
''', r'''
class Counter {
  #count = 0;
  readonly #step: number;
  constructor(step: number) {
    this.#step = step;
  }
  tick(): number {
    this.#count += this.#step;
    return this.#count;
  }
}
const [step = "1", times = "1"] = input.split(/\s+/);
const c = new Counter(Number(step));
const seen: number[] = [];
for (let i = 0; i < Number(times); i++) seen.push(c.tick());
console.log(seen.join(" "));
''', ["private "], ["2 3", "5 1"],
    hints=["Rename `count` to `#count` everywhere, declaration included."])

_rt(24, "tsm-w24-rt1", "Chunks of anything",
    "`chunks` lazily yields slices of a list. Replace the `any`s so it works for any element type and `for (const c of chunks(xs, 2))` gives `c` the type `T[]`.",
    r'''
function* chunks(xs: any, size: any): any {
  for (let i = 0; i < xs.length; i += size) yield xs.slice(i, i + size);
}
for (const c of chunks(input.split(/\s+/), 2)) console.log(c.join(","));
''', r'''
function* chunks<T>(xs: readonly T[], size: number): Generator<T[]> {
  for (let i = 0; i < xs.length; i += size) yield xs.slice(i, i + size);
}
for (const c of chunks(input.split(/\s+/), 2)) console.log(c.join(","));
''', '''
type _Elem<I> = I extends Iterable<infer E> ? E : never;
const _c = chunks([1, 2, 3], 2);
type _1 = Expect<Equal<IsAny<typeof _c>, false>>;
type _2 = Expect<Equal<_Elem<typeof _c>, number[]>>;
''', ["a b c d e", "x"],
    hints=["A generic generator: `function* chunks<T>(xs: readonly T[], size: number)`.", "Its return type is `Generator<T[]>` — or leave it off and let inference find it."])

_dz(24, "tsm-w24-dz1", "A queue you can iterate",
    "Write the generic `Queue<T>` interface: it is `Iterable<T>`, has `enqueue(x: T): void`, `dequeue(): T | undefined`, and a readonly `length` number.",
    r'''
interface Queue<T> extends Iterable<T> {
  enqueue(x: T): void;
  dequeue(): T | undefined;
  readonly length: number;
}
function makeQueue<T>(): Queue<T> {
  const items: T[] = [];
  return {
    enqueue: (x) => {
      items.push(x);
    },
    dequeue: () => items.shift(),
    get length() {
      return items.length;
    },
    [Symbol.iterator]: () => items[Symbol.iterator](),
  };
}
const q = makeQueue<string>();
for (const line of input.split("\n")) {
  const [cmd = "", arg = ""] = line.split(" ");
  if (cmd === "in") q.enqueue(arg);
  else console.log(q.dequeue() ?? "empty");
}
console.log(`${q.length} left: ${[...q].join(",")}`);
''', '''interface Queue<T> extends Iterable<T> {
  enqueue(x: T): void;
  dequeue(): T | undefined;
  readonly length: number;
}''', '''
type _1 = Expect<Equal<Queue<number>["enqueue"], (x: number) => void>>;
type _2 = Expect<Equal<Queue<number>["dequeue"], () => number | undefined>>;
type _3 = Expect<Equal<Queue<number>["length"], number>>;
type _4 = Expect<Equal<Queue<number> extends Iterable<number> ? true : false, true>>;
''', ["in a\nin b\nout\nin c", "out"],
    hints=["`interface Queue<T> extends Iterable<T> { ... }`.", "`readonly length: number;`."])

_dz(25, "tsm-w25-dz1", "Result, generic",
    "Write `Result<T, E = string>`: `{ ok: true; value: T }` or `{ ok: false; error: E }`, with the error type defaulting to `string`.",
    r'''
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
function parseAge(s: string): Result<number> {
  const n = Number(s);
  if (!Number.isInteger(n)) return { ok: false, error: `not a whole number: ${s}` };
  if (n < 0 || n > 150) return { ok: false, error: `out of range: ${n}` };
  return { ok: true, value: n };
}
for (const t of input.split(/\s+/)) {
  const r = parseAge(t);
  console.log(r.ok ? `age ${r.value}` : `error ${r.error}`);
}
''', "type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };", '''
type _1 = Expect<Equal<Result<number>, { ok: true; value: number } | { ok: false; error: string }>>;
type _2 = Expect<Equal<Result<1, 2>, { ok: true; value: 1 } | { ok: false; error: 2 }>>;
''', ["36 -1 abc 200 0"],
    hints=["Two type parameters; give the second a default with `E = string`."])

_rf(25, "tsm-w25-rf1", "Don't assume it is an Error",
    "`(e as Error).message` assumes whatever was thrown is an `Error` — the thrown string prints `failed: undefined`. Narrow with `instanceof` and fall back to `String(e)`. No `as Error` left.",
    r'''
function risky(s: string): number {
  if (s === "boom") throw new Error("exploded");
  if (s === "str") throw "a plain string";
  return s.length;
}
for (const t of input.split(/\s+/)) {
  try {
    console.log(risky(t));
  } catch (e) {
    console.log(`failed: ${(e as Error).message}`);
  }
}
''', r'''
function risky(s: string): number {
  if (s === "boom") throw new Error("exploded");
  if (s === "str") throw "a plain string";
  return s.length;
}
for (const t of input.split(/\s+/)) {
  try {
    console.log(risky(t));
  } catch (e) {
    console.log(`failed: ${e instanceof Error ? e.message : String(e)}`);
  }
}
''', ["as Error"], ["ok boom str"],
    hints=["A caught value is `unknown`: `e instanceof Error` narrows it."])

_rt(25, "tsm-w25-rt1", "Wrapping a failure",
    "`wrap` adds context to whatever was thrown, keeping the original as the `cause`. Replace the `any`s: a caught value is `unknown`, the context is a string, and the result is an `Error`.",
    r'''
function wrap(e: any, context: any): any {
  return new Error(`${context}: ${e instanceof Error ? e.message : String(e)}`, { cause: e });
}
for (const t of input.split(/\s+/)) {
  try {
    if (t === "x") throw new Error("bad x");
    if (t === "y") throw 42;
    console.log(`ok ${t}`);
  } catch (e) {
    const w = wrap(e, `handling ${t}`);
    console.log(w.message, w.cause instanceof Error ? "(error cause)" : `(cause ${String(w.cause)})`);
  }
}
''', r'''
function wrap(e: unknown, context: string): Error {
  return new Error(`${context}: ${e instanceof Error ? e.message : String(e)}`, { cause: e });
}
for (const t of input.split(/\s+/)) {
  try {
    if (t === "x") throw new Error("bad x");
    if (t === "y") throw 42;
    console.log(`ok ${t}`);
  } catch (e) {
    const w = wrap(e, `handling ${t}`);
    console.log(w.message, w.cause instanceof Error ? "(error cause)" : `(cause ${String(w.cause)})`);
  }
}
''', '''
type _1 = Expect<Equal<Parameters<typeof wrap>[0], unknown>>;
type _2 = Expect<Equal<Parameters<typeof wrap>[1], string>>;
type _3 = Expect<Equal<ReturnType<typeof wrap>, Error>>;
''', ["a x y"],
    hints=["`unknown` is the honest type of anything that was thrown."])

_rt(26, "tsm-w26-rt1", "Async, typed",
    "Replace the `any`s in `double`: it takes a number and resolves to a number.",
    r'''
async function double(n: any): Promise<any> {
  return n * 2;
}
async function main(): Promise<void> {
  const xs = input.split(/\s+/).map(Number);
  const ys = await Promise.all(xs.map(double));
  console.log(ys.join(" "));
}
main();
''', r'''
async function double(n: number): Promise<number> {
  return n * 2;
}
async function main(): Promise<void> {
  const xs = input.split(/\s+/).map(Number);
  const ys = await Promise.all(xs.map(double));
  console.log(ys.join(" "));
}
main();
''', '''
type _1 = Expect<Equal<Parameters<typeof double>[0], number>>;
type _2 = Expect<Equal<ReturnType<typeof double>, Promise<number>>>;
''', ["1 2 3", "10"],
    hints=["An async function's return type is always a `Promise<...>`."])

_dz(26, "tsm-w26-dz1", "A task is a promise-maker",
    "Write `Task<T>`: a function with no arguments that returns a promise of `T`. `runAll` runs a list of them with at most `limit` in flight.",
    r'''
type Task<T> = () => Promise<T>;
async function runAll<T>(tasks: readonly Task<T>[], limit: number): Promise<T[]> {
  const results: T[] = [];
  let next = 0;
  async function worker(): Promise<void> {
    while (next < tasks.length) {
      const i = next++;
      const task = tasks[i];
      if (task) results[i] = await task();
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, tasks.length) }, worker));
  return results;
}
const nums = input.split(/\s+/).map(Number);
runAll(nums.map((n) => async () => n * n), 2).then((r) => console.log(r.join(" ")));
''', "type Task<T> = () => Promise<T>;", '''
type _1 = Expect<Equal<Task<number>, () => Promise<number>>>;
''', ["1 2 3 4", "5"],
    hints=["A function type with no parameters: `() => Promise<T>`."])

_rf(26, "tsm-w26-rf1", "Chains into awaits",
    "Rewrite `main` with `async`/`await` instead of `.then` chains — no `.then(` left. Same output.",
    r'''
function load(id: number): Promise<string> {
  return Promise.resolve(`item${id}`);
}
function main(): Promise<void> {
  const ids = input.split(/\s+/).map(Number);
  return Promise.all(ids.map(load)).then((items) => {
    console.log(items.join(","));
    return load(ids.length).then((extra) => console.log(`extra ${extra}`));
  });
}
main();
''', r'''
function load(id: number): Promise<string> {
  return Promise.resolve(`item${id}`);
}
async function main(): Promise<void> {
  const ids = input.split(/\s+/).map(Number);
  const items = await Promise.all(ids.map(load));
  console.log(items.join(","));
  const extra = await load(ids.length);
  console.log(`extra ${extra}`);
}
main();
''', [".then("], ["1 2 3", "7"],
    hints=["Mark `main` `async`, then `const items = await Promise.all(...)`."])
