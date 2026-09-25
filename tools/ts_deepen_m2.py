# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The original Month 2 TypeScript chapters, brought up to the lesson template
# (TS_MASTERY_ROADMAP.md F-12, X-02/X-03) with `_deepen`:
#
#   ts_functions  ts_params  ts_higher_order  ts_arrays  ts_array_methods
#   ts_destructuring  ts_objects  ts_json
#
# Every output and compiler message is computed (python tools/gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_deepen(
    "ts_functions",
    why=r"""
A function gives a piece of logic a name, a fixed set of inputs and an output.
That's what lets a program be read in chunks: `parseLine`, `total`, `format` —
each small enough to understand and test on its own. In TypeScript the signature
is also a contract the compiler enforces at every call: the right number of
arguments, of the right types, and a return value the caller can rely on.

Most real programs in this course are a handful of short functions and a few
lines that wire them together. Writing them well — one job each, typed
parameters, an honest return type — is the habit this chapter builds.
""",
    examples=[
        ("Small functions, wired together",
         r"""
function parseLine(line: string): number[] {
  return line.trim().split(/\s+/).map(Number);
}
function average(xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
function report(label: string, xs: number[]): string {
  return `${label}: avg ${average(xs).toFixed(1)} over ${xs.length}`;
}
for (const [label, line] of [["mon", "3 5 7"], ["tue", "10 20"]]) {
  console.log(report(label ?? "", parseLine(line ?? "")));
}
""", [""],
         "Each function does one thing and can be tested alone; the loop at the bottom only connects them."),
        ("A function declaration is hoisted",
         r"""
console.log(shout("ready"));
function shout(text: string): string {
  return text.toUpperCase() + "!";
}
""", [""],
         "Declarations are available from the top of their scope, so helpers can live below the code that uses them. `const f = () => …` is not hoisted."),
        ("`void` means \"don't use the result\"",
         r"""
function logLine(text: string): void {
  console.log("> " + text);
}
const result = logLine("saved");
console.log(result === undefined);
""", [""],
         "A `void` function still returns `undefined` at runtime; the type tells callers not to rely on it."),
    ],
    errors=[
        (2554, r"""
function add(a: number, b: number): number {
  return a + b;
}
add(1);
""", "Every required parameter must be passed. Make it optional (`b?: number`) or give it a default if it really can be left out."),
        (2355, r"""
function half(n: number): number {
  if (n > 0) {
    n / 2;
  }
}
""", "The signature promises a `number`, but no path returns one — the computed value is thrown away."),
    ],
    pitfalls=[
        ("Braces without `return`",
         r"""
const double = (x: number) => {
  x * 2;
};
console.log([1, 2].map(double).join(","));
""",
         r"""
const double = (x: number) => x * 2;
console.log([1, 2].map(double).join(","));
""",
         "An arrow with a block body needs `return`; without it the function returns `undefined`. Annotating the return type (`: number`) would have caught it."),
        ("`return` inside `forEach` doesn't return from the function",
         r"""
function hasNegative(xs: number[]): boolean {
  xs.forEach((x) => {
    if (x < 0) return true;
  });
  return false;
}
console.log(hasNegative([3, -1, 2]));
""",
         r"""
function hasNegative(xs: number[]): boolean {
  for (const x of xs) {
    if (x < 0) return true;
  }
  return false;
}
console.log(hasNegative([3, -1, 2]));
""",
         "That `return` leaves only the callback. Use a `for…of` loop, or `xs.some((x) => x < 0)`."),
        ("A function that changes its argument",
         r"""
function median(xs: number[]): number {
  xs.sort((a, b) => a - b);
  return xs[Math.floor(xs.length / 2)] ?? 0;
}
const readings = [9, 1, 5];
console.log(median(readings), readings.join(","));
""",
         r"""
function median(xs: readonly number[]): number {
  const sorted = xs.toSorted((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)] ?? 0;
}
const readings = [9, 1, 5];
console.log(median(readings), readings.join(","));
""",
         "Arrays are passed by reference, so sorting in place reordered the caller's data. Take `readonly` and work on a copy."),
    ],
    later=[
        "**Week 5 — Parameters and overloads.** Optional, default and rest parameters; several signatures for one function.",
        "**Week 6 — Higher-order functions.** Functions that take and return functions.",
        "**Week 13 — Function types in depth.** When one function type fits another.",
    ],
)


_deepen(
    "ts_params",
    why=r"""
Real functions are called in more than one way: sometimes with every argument,
sometimes with just the essentials, sometimes with a list of any length. Optional
parameters, defaults, rest parameters and options objects let one function serve
all of those call sites — and TypeScript checks each form, so an omitted argument
is visible as `undefined` in the type rather than discovered at runtime.

The ordering rules (required, then optional, then rest) and the difference
between "optional" and "may be `undefined`" are small, but they're what makes a
function pleasant to call.
""",
    examples=[
        ("An options object with defaults",
         r"""
function connect({ host = "localhost", port = 5432, tls = false }: { host?: string; port?: number; tls?: boolean } = {}): string {
  return `${tls ? "tls" : "tcp"}://${host}:${port}`;
}
console.log(connect());
console.log(connect({ port: 6000 }));
console.log(connect({ host: "db.local", tls: true }));
""", [""],
         "Named options scale better than a long list of positional parameters, and destructuring with defaults fills in whatever the caller leaves out."),
        ("Spreading an array into a rest parameter",
         r"""
function maxOf(first: number, ...rest: number[]): number {
  return rest.reduce((m, x) => (x > m ? x : m), first);
}
const readings = [4, 11, 7];
console.log(maxOf(3), maxOf(3, 9, 2), maxOf(...(readings as [number, ...number[]])));
""", [""],
         "`first` plus `...rest` makes \"at least one number\" part of the signature. Spreading an array needs the compiler to know it isn't empty — hence the tuple type."),
        ("Optional versus defaulted",
         r"""
function label(text: string, suffix?: string): string {
  return suffix === undefined ? text : `${text} (${suffix})`;
}
function pad(text: string, width = 6): string {
  return text.padStart(width, ".");
}
console.log(label("draft"), label("draft", "v2"));
console.log(pad("ok"), pad("ok", 3));
""", [""],
         "An optional parameter is `undefined` when omitted and must be handled; a defaulted one always has a value inside the function."),
    ],
    errors=[
        (1016, r"""
function range(start?: number, end: number): number[] {
  return [];
}
""", "Arguments are matched by position, so an optional parameter can't be followed by a required one. Reorder, or give `start` a default."),
        (2555, r"""
function log(level: string, ...messages: string[]): void {
  console.log(level, messages.join(" "));
}
log();
""", "A rest parameter can be empty, but the parameters before it are still required."),
    ],
    pitfalls=[
        ("A default doesn't replace `null`",
         r"""
function greet(name: string | null = "friend"): string {
  return "Hello, " + name;
}
console.log(greet(null));
""",
         r"""
function greet(name: string | null = null): string {
  return "Hello, " + (name ?? "friend");
}
console.log(greet(null));
""",
         "Defaults apply only when the argument is `undefined`. For `null` too, fall back with `??` inside the function."),
        ("Required after optional",
         (r"""
function between(lo?: number, hi: number): boolean {
  return (lo ?? 0) <= hi;
}
console.log(between(undefined, 5));
""", 1016),
         r"""
function between(hi: number, lo = 0): boolean {
  return lo <= hi;
}
console.log(between(5));
""",
         "Put required parameters first. Callers then write `between(5)` instead of passing `undefined` placeholders."),
        ("Passing an array to a rest parameter",
         (r"""
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}
const xs = [1, 2, 3];
console.log(sum(xs));
""", 2345),
         r"""
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}
const xs = [1, 2, 3];
console.log(sum(...xs));
""",
         "A rest parameter collects separate arguments. Spread the array into them."),
    ],
    later=[
        "**Week 5 — Overloads.** When different argument shapes should produce different return types.",
        "**Week 8 — Destructuring.** The syntax behind options objects.",
        "**Week 13 — Function types.** Why a callback with fewer parameters still fits.",
    ],
)


_deepen(
    "ts_higher_order",
    why=r"""
Some behaviour is the same apart from one step: "retry this operation", "sort by
this key", "apply these transformations in order". A higher-order function
captures the shared part and takes the varying step as a function argument — or
returns a new function with some settings baked in.

It's the idea behind `map`, `filter` and `sort`, and behind utilities you'll
write yourself: `memoize`, `once`, `debounce`, validators built from rules. The
types make it safe: a callback's parameter types flow in from the slot it's
passed to, and a returned function has a precise signature.
""",
    examples=[
        ("A wrapper that counts calls",
         r"""
function counted<A extends unknown[], R>(fn: (...args: A) => R) {
  let calls = 0;
  const wrapped = (...args: A): R => {
    calls++;
    return fn(...args);
  };
  return { wrapped, calls: () => calls };
}
const area = counted((w: number, h: number) => w * h);
console.log(area.wrapped(2, 3), area.wrapped(4, 5));
console.log(`called ${area.calls()} times`);
""", [""],
         "`counted` works for any function: the wrapper has exactly the original's parameters and return type, and a closure keeps the count."),
        ("A validator built from rules",
         r"""
type Rule = (s: string) => string | undefined;
const minLength = (n: number): Rule => (s) => (s.length < n ? `at least ${n} characters` : undefined);
const hasDigit: Rule = (s) => (/\d/.test(s) ? undefined : "needs a digit");
function validator(...rules: Rule[]) {
  return (s: string) => rules.map((r) => r(s)).filter((m) => m !== undefined);
}
const password = validator(minLength(8), hasDigit);
for (const p of ["short", "longenough", "longer123"]) {
  console.log(`${p}: ${password(p).join(", ") || "ok"}`);
}
""", [""],
         "`minLength(8)` returns a rule with `8` baked in; `validator` returns a function that runs any list of rules."),
        ("Grouping by a key function",
         r"""
function groupBy<T>(items: readonly T[], keyOf: (item: T) => string): Map<string, T[]> {
  const groups = new Map<string, T[]>();
  for (const item of items) groups.set(keyOf(item), [...(groups.get(keyOf(item)) ?? []), item]);
  return groups;
}
const words = ["apple", "avocado", "banana", "blueberry", "cherry"];
for (const [letter, ws] of groupBy(words, (w) => w[0] ?? "")) console.log(`${letter}: ${ws.join(" ")}`);
""", [""],
         "The grouping logic is written once; the caller decides what to group by."),
    ],
    errors=[
        (2345, r"""
const lengths = [1, 2, 3].map((s: string) => s.length);
""", "The callback slot passes numbers; a callback that insists on strings doesn't fit."),
        (2349, r"""
const retries = 3;
const result = retries();
""", "Only functions can be called. This is usually a variable shadowing a function, or a missing function argument."),
    ],
    pitfalls=[
        ("Passing a method loses `this`",
         r"""
class Greeter {
  greeting = "hi";
  greet(name: string): string {
    return this.greeting + " " + name;
  }
}
const g = new Greeter();
try {
  console.log(["ana", "bo"].map(g.greet).join(", "));
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
class Greeter {
  greeting = "hi";
  greet(name: string): string {
    return this.greeting + " " + name;
  }
}
const g = new Greeter();
console.log(["ana", "bo"].map((name) => g.greet(name)).join(", "));
""",
         "`g.greet` passed on its own is a plain function; `map` calls it with `this` undefined. Wrap it in an arrow."),
        ("`reduce` on an empty array",
         r"""
const empty: number[] = [];
try {
  console.log(empty.reduce((a, b) => a + b));
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const empty: number[] = [];
console.log(empty.reduce((a, b) => a + b, 0));
""",
         "Without an initial value, `reduce` needs at least one element. Always pass one when the array might be empty."),
        ("`compose` versus `pipe` order",
         r"""
const compose = (f: (x: number) => number, g: (x: number) => number) => (x: number) => f(g(x));
const addOne = (x: number) => x + 1;
const double = (x: number) => x * 2;
console.log("add one, then double: " + compose(addOne, double)(3));
""",
         r"""
const pipe = (f: (x: number) => number, g: (x: number) => number) => (x: number) => g(f(x));
const addOne = (x: number) => x + 1;
const double = (x: number) => x * 2;
console.log("add one, then double: " + pipe(addOne, double)(3));
""",
         "`compose(f, g)` runs `g` first. When the steps read left to right, use `pipe`."),
    ],
    later=[
        "**Week 6 — Recursion.** Functions that call themselves, and memoising them.",
        "**Week 18 — Generics.** Typing helpers like `counted` and `groupBy` for any element type.",
        "**Week 23 — Decorators.** Wrapping methods the way `counted` wraps functions.",
    ],
)


_deepen(
    "ts_arrays",
    why=r"""
Arrays are the workhorse collection: lines of input, scores, rows of a grid,
results in order. They're ordered, indexable, growable — and they're objects,
which means two things catch almost everyone at least once: assigning an array
to another variable *shares* it rather than copying it, and many methods change
the array in place.

TypeScript adds element types (`number[]`), tuples for fixed shapes
(`[string, number]`) and `readonly` arrays that promise not to change. This
chapter is how to create, copy, compare and reshape arrays safely.
""",
    examples=[
        ("A grid without shared rows",
         r"""
const rows = 3;
const cols = 4;
const grid = Array.from({ length: rows }, (_, r) => Array.from({ length: cols }, (_, c): string => ((r + c) % 2 === 0 ? "#" : ".")));
grid[0]![0] = "@";
for (const row of grid) console.log(row.join(""));
""", [""],
         "`Array.from` with a function builds a new row for each index, so changing one cell changes only that row."),
        ("Copies are shallow",
         r"""
const team = [{ name: "ana", score: 1 }, { name: "bo", score: 2 }];
const copy = [...team];
copy.push({ name: "cy", score: 3 });
copy[0]!.score = 99;
console.log(team.length, copy.length, team[0]!.score);
""", [""],
         "Spreading made a new array — pushing to it didn't change `team` — but both arrays hold the same objects."),
        ("Searching an array",
         r"""
const langs = ["ts", "go", "rust", "go"];
console.log(langs.includes("go"), langs.indexOf("go"), langs.lastIndexOf("go"));
console.log(langs.at(-1), langs.indexOf("java"));
""", [""],
         "`includes` answers yes/no; `indexOf` gives a position or -1; `at(-1)` reads from the end."),
    ],
    errors=[
        (2345, r"""
const scores: number[] = [90, 85];
scores.push("100");
""", "The element type is `number`; a string can't be added. Convert it first."),
        (2493, r"""
const point: [number, number] = [3, 4];
const z = point[2];
""", "A tuple's length is part of its type, so reading past the end is a compile error rather than `undefined`."),
    ],
    pitfalls=[
        ("`fill` with an object shares it",
         r"""
const board = Array(2).fill([] as string[]);
board[0]!.push("x");
console.log(JSON.stringify(board));
""",
         r"""
const board = Array.from({ length: 2 }, () => [] as string[]);
board[0]!.push("x");
console.log(JSON.stringify(board));
""",
         "`fill` puts the *same* array in every slot. Create one per slot with `Array.from`."),
        ("`sort` changes the original",
         r"""
const arrivals = ["cy", "ana", "bo"];
const alphabetical = arrivals.sort();
console.log("arrived: " + arrivals.join(","));
""",
         r"""
const arrivals = ["cy", "ana", "bo"];
const alphabetical = arrivals.toSorted();
console.log("arrived: " + arrivals.join(","));
""",
         "`sort` sorts in place and returns the same array, so the arrival order was lost. `toSorted` returns a sorted copy."),
        ("Arrays compare by identity",
         r"""
const a = [1, 2];
const b = [1, 2];
console.log(a === b ? "same" : "different");
""",
         r"""
const a = [1, 2];
const b = [1, 2];
const same = a.length === b.length && a.every((x, i) => x === b[i]);
console.log(same ? "same" : "different");
""",
         "`===` asks whether two arrays are the same object. Compare element by element for equal contents."),
    ],
    later=[
        "**Week 7 — Tuples and modern array methods.** `toSorted`, `with`, `Object.groupBy`.",
        "**Week 14 — `noUncheckedIndexedAccess`.** Making every index read admit it may be `undefined`.",
        "**Week 16 — Immutability.** `readonly` arrays and immutable updates.",
    ],
)


_deepen(
    "ts_array_methods",
    why=r"""
Most loops over arrays do one of a few things: transform every element, keep some
of them, combine them into one value, or find one. The array methods name those
jobs — `map`, `filter`, `reduce`, `find` — so the code says *what* it does
instead of *how* it walks the array, and chains of them read like a description
of the data flow.

Knowing which methods return new arrays and which change the original, what each
returns when nothing matches, and when a plain loop is clearer is what this
chapter adds to the basics.
""",
    examples=[
        ("`flatMap`: one-to-many",
         r"""
const sentences = ["the quick fox", "jumps over", "the dog"];
const words = sentences.flatMap((s) => s.split(" "));
console.log(words.length, words.join("|"));
""", [""],
         "`flatMap` maps each element to an array and flattens one level — here, sentences to words."),
        ("`reduce` into a lookup",
         r"""
const votes = ["ts", "go", "ts", "rust", "ts", "go"];
const tally = votes.reduce<Record<string, number>>((acc, v) => {
  acc[v] = (acc[v] ?? 0) + 1;
  return acc;
}, {});
console.log(JSON.stringify(tally));
""", [""],
         "The type argument `<Record<string, number>>` types the accumulator; the initial `{}` is its starting value."),
        ("Update one element without mutating",
         r"""
const tasks = [{ id: 1, done: false }, { id: 2, done: false }];
const i = tasks.findIndex((t) => t.id === 2);
const updated = i < 0 ? tasks : tasks.with(i, { id: 2, done: true });
console.log(JSON.stringify(updated), tasks[1]?.done);
""", [""],
         "`findIndex` locates it and `with` returns a copy with that slot replaced; the original array is untouched."),
    ],
    errors=[
        (2339, r"""
const totalLength = [1, 2, 3].reduce((acc, x) => acc + x.length, 0);
""", "The elements are numbers, which have no `length`. `reduce`'s callback parameters are typed from the array and the initial value."),
        (2322, r"""
const firstBig: number = [1, 5, 9].find((x) => x > 4);
""", "`find` returns `undefined` when nothing matches, so its result is `number | undefined`."),
    ],
    pitfalls=[
        ("`forEach` returns nothing",
         r"""
const prices = [2, 4];
const doubled = prices.forEach((p) => p * 2);
console.log(doubled);
""",
         r"""
const prices = [2, 4];
const doubled = prices.map((p) => p * 2);
console.log(doubled.join(","));
""",
         "`forEach` is for side effects and always returns `undefined`. `map` returns the transformed array."),
        ("`indexOf` with objects compares identity",
         r"""
const users = [{ id: 1 }, { id: 2 }];
console.log(users.indexOf({ id: 1 }));
""",
         r"""
const users = [{ id: 1 }, { id: 2 }];
console.log(users.findIndex((u) => u.id === 1));
""",
         "A new `{ id: 1 }` literal is a different object. Search by a property with `findIndex`."),
        ("`splice` removes what it reads",
         r"""
const queue = ["a", "b", "c", "d"];
const firstTwo = queue.splice(0, 2);
console.log(firstTwo.join(","), "| queue:", queue.join(","));
""",
         r"""
const queue = ["a", "b", "c", "d"];
const firstTwo = queue.slice(0, 2);
console.log(firstTwo.join(","), "| queue:", queue.join(","));
""",
         "`splice` removes elements and returns them; `slice` only copies. One letter apart, very different effects."),
    ],
    later=[
        "**Week 7 — Modern array methods.** `toSorted`, `toReversed`, `with`, `Object.groupBy`.",
        "**Week 24 — Iterator helpers.** The same methods, lazily, on any iterator.",
    ],
)


_deepen(
    "ts_destructuring",
    why=r"""
Data arrives in structures — a `[name, score]` pair, a config object, a JSON
record — and most code wants a few pieces of it in local variables.
Destructuring pulls them out in one line, with defaults for anything missing and
`...rest` for everything else. Spread does the reverse: builds new arrays and
objects from existing ones.

It's also how function parameters can accept an options object, how two
variables are swapped, and how a function returns several values as a tuple.
The pitfalls are about what destructuring *doesn't* do: defaults don't replace
`null`, and copies are shallow.
""",
    examples=[
        ("Destructuring in a parameter list",
         r"""
type Order = { id: number; items: { name: string; qty: number }[]; note?: string };
function summary({ id, items, note = "none" }: Order): string {
  const units = items.reduce((n, { qty }) => n + qty, 0);
  return `#${id}: ${units} units, note: ${note}`;
}
console.log(summary({ id: 7, items: [{ name: "pen", qty: 2 }, { name: "cup", qty: 1 }] }));
""", [""],
         "Destructure exactly the fields you use, with defaults, right in the signature — and again in the `reduce` callback."),
        ("Nested destructuring",
         r"""
const response = { status: 200, body: { user: { name: "ana", roles: ["admin", "ops"] } } };
const { status, body: { user: { name, roles: [primary = "none"] } } } = response;
console.log(status, name, primary);
""", [""],
         "Patterns can follow the data's shape several levels deep. Past two levels, a couple of plain lines are usually clearer."),
        ("Returning several values",
         r"""
function minMax(xs: readonly number[]): [min: number, max: number] {
  return [Math.min(...xs), Math.max(...xs)];
}
let [lo, hi] = minMax([4, 9, 1]);
[lo, hi] = [hi, lo];
console.log(lo, hi);
""", [""],
         "A labelled tuple return destructures into two variables; the same syntax swaps them."),
    ],
    errors=[
        (2339, r"""
const { age } = { name: "ana" };
""", "You can only destructure properties the type has."),
        (2488, r"""
const [first] = { x: 1 };
""", "Array patterns need something iterable. Use an object pattern (`{ x }`) for objects."),
    ],
    pitfalls=[
        ("A default doesn't replace `null`",
         r"""
const config = JSON.parse('{"port": null}') as { port: number | null };
const { port = 8080 } = config;
console.log("port " + port);
""",
         r"""
const config = JSON.parse('{"port": null}') as { port: number | null };
const port = config.port ?? 8080;
console.log("port " + port);
""",
         "Destructuring defaults apply only to `undefined`. JSON often uses `null` for \"absent\" — use `??`."),
        ("Destructuring a method loses `this`",
         r"""
const counter = {
  count: 0,
  increment() {
    this.count++;
    return this.count;
  },
};
const { increment } = counter;
try {
  console.log(increment());
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const counter = {
  count: 0,
  increment() {
    this.count++;
    return this.count;
  },
};
console.log(counter.increment());
""",
         "A destructured method is detached from its object. Call it through the object."),
        ("`...rest` copies only one level",
         r"""
const original = { name: "ana", prefs: { theme: "dark" } };
const { name, ...rest } = original;
rest.prefs.theme = "light";
console.log(name, original.prefs.theme);
""",
         r"""
const original = { name: "ana", prefs: { theme: "dark" } };
const { name, ...rest } = structuredClone(original);
rest.prefs.theme = "light";
console.log(name, original.prefs.theme);
""",
         "`rest` is a new object, but `rest.prefs` is the original nested object. Clone deeply when you intend to change nested data."),
    ],
    later=[
        "**Week 5 — Parameters.** Options objects built on destructuring with defaults.",
        "**Week 12 — Discriminated unions.** Destructured tags that still narrow.",
        "**Week 16 — Immutability.** Spread-based updates at every level.",
    ],
)


_deepen(
    "ts_objects",
    why=r"""
Objects group related values under names: a user's `name`, `email` and `role`;
a config's `host` and `port`. In TypeScript an object type — written inline or as
an `interface` — lists which properties exist, which are optional, and what each
holds, and the compiler checks every read and every literal against it.

Objects are also references, so copying, comparing and updating them needs care,
and "does this object have that key?" has more than one answer. This chapter
covers shaping, reading, iterating and updating objects the TypeScript way.
""",
    examples=[
        ("Shorthand and computed keys",
         r"""
const name = "ana";
const role = "admin";
const field = "lastLogin";
const user = { name, role, [field]: "2026-09-01", [`${role}Since`]: 2024 };
console.log(JSON.stringify(user));
""", [""],
         "`{ name }` is shorthand for `{ name: name }`; `[expr]` computes a key at runtime."),
        ("Transforming every value",
         r"""
const prices = { pen: 1.5, cup: 4, ink: 12 };
const withTax = Object.fromEntries(Object.entries(prices).map(([item, p]) => [item, Number((p * 1.2).toFixed(2))]));
console.log(JSON.stringify(withTax));
""", [""],
         "`Object.entries` → `map` → `Object.fromEntries` is the object version of `array.map`."),
        ("Optional chaining through nested data",
         r"""
type Account = { owner?: { address?: { city?: string } } };
const accounts: Account[] = [{ owner: { address: { city: "Oslo" } } }, { owner: {} }, {}];
for (const a of accounts) console.log(a.owner?.address?.city ?? "unknown city");
""", [""],
         "`?.` stops at the first missing link and yields `undefined`; `??` supplies the fallback."),
    ],
    errors=[
        (2741, r"""
interface User {
  name: string;
  email: string;
}
const u: User = { name: "ana" };
""", "`email` is required by the interface. Add it, or make it optional (`email?: string`) if it really can be absent."),
        (2353, r"""
interface Point {
  x: number;
  y: number;
}
const p: Point = { x: 1, y: 2, z: 3 };
""", "An object literal with a property the type doesn't know is usually a typo or a wrong type — the excess-property check flags it."),
    ],
    pitfalls=[
        ("Spread copies one level",
         r"""
const base = { name: "ana", tags: ["a"] };
const copy = { ...base };
copy.tags.push("b");
console.log(base.tags.join(","));
""",
         r"""
const base = { name: "ana", tags: ["a"] };
const copy = { ...base, tags: [...base.tags] };
copy.tags.push("b");
console.log(base.tags.join(","));
""",
         "The copy shared `tags` with the original. Copy every level you intend to change."),
        ("`in` sees inherited properties",
         r"""
const counts: Record<string, number> = {};
const word = "toString";
console.log(word in counts ? "seen" : "new");
""",
         r"""
const counts: Record<string, number> = {};
const word = "toString";
console.log(Object.hasOwn(counts, word) ? "seen" : "new");
""",
         "Every plain object inherits `toString`, `constructor` and friends. `Object.hasOwn` checks only the object's own keys — or use a `Map`."),
        ("Integer-like keys don't keep insertion order",
         r"""
const byId: Record<string, string> = {};
for (const id of ["30", "10", "b", "20"]) byId[id] = "x";
console.log(Object.keys(byId).join(","));
""",
         r"""
const byId = new Map<string, string>();
for (const id of ["30", "10", "b", "20"]) byId.set(id, "x");
console.log([...byId.keys()].join(","));
""",
         "Objects list integer-like keys first, ascending. A `Map` keeps pure insertion order."),
    ],
    later=[
        "**Week 8 — Interfaces vs types, index signatures.** Describing object shapes precisely.",
        "**Week 9 — Maps and Sets.** When a `Map` is the better dictionary.",
        "**Week 15 — Structural typing.** Why an object with extra properties still fits.",
    ],
)


_deepen(
    "ts_json",
    why=r"""
JSON is how programs talk to each other: API responses, config files, messages
in a queue, test fixtures. `JSON.parse` turns text into values and
`JSON.stringify` turns values back into text — and both have rules that surprise
people: dates become strings, `undefined` disappears, a `Map` becomes `{}`.

The TypeScript-specific issue is trust. `JSON.parse` returns `any`, which means
the compiler will believe whatever you claim about the data. Treat parsed JSON as
`unknown` and check it — this chapter shows the basics, and week 17 builds a
schema validator for it.
""",
    examples=[
        ("Pretty output, and choosing the keys",
         r"""
const user = { id: 7, name: "ana", password: "hunter2", roles: ["admin"] };
console.log(JSON.stringify(user, ["id", "name", "roles"], 2));
""", [""],
         "The second argument can list which keys to keep; the third indents the output."),
        ("Reviving dates while parsing",
         r"""
const text = '{"title":"launch","when":"2026-09-26T10:00:00.000Z"}';
const event = JSON.parse(text, (key, value: unknown) =>
  key === "when" && typeof value === "string" ? new Date(value) : value) as { title: string; when: Date };
console.log(event.title, event.when.getUTCFullYear(), event.when instanceof Date);
""", [""],
         "A reviver sees every key/value pair and can replace the value — here turning the ISO string back into a `Date`."),
        ("Parsing that can't crash",
         r"""
function safeParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}
for (const t of ['{"ok":true}', "{oops", "42", "null"]) {
  const v = safeParse(t);
  console.log(v === undefined ? "invalid JSON" : `${typeof v}: ${JSON.stringify(v)}`);
}
""", [""],
         "Bad input throws a `SyntaxError`; catching it once, at the boundary, keeps the rest of the program simple. Note that `null` is valid JSON."),
    ],
    errors=[
        (18046, r"""
const data: unknown = JSON.parse('{"name":"ana"}');
console.log(data.name);
""", "Typed as `unknown`, the parsed value must be checked before use — which is exactly the point."),
        (2345, r"""
const n = JSON.parse(42);
""", "`JSON.parse` takes a string of JSON text. To turn a value *into* JSON, use `JSON.stringify`."),
    ],
    pitfalls=[
        ("Dates come back as strings",
         r"""
const saved = JSON.stringify({ when: new Date(Date.UTC(2026, 0, 2)) });
const loaded = JSON.parse(saved) as { when: Date };
try {
  console.log(loaded.when.getUTCFullYear());
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const saved = JSON.stringify({ when: new Date(Date.UTC(2026, 0, 2)) });
const loaded = JSON.parse(saved) as { when: string };
console.log(new Date(loaded.when).getUTCFullYear());
""",
         "JSON has no date type: a `Date` is written as an ISO string, and the `as { when: Date }` lied about it. Convert explicitly."),
        ("`undefined` and functions vanish",
         r"""
console.log(JSON.stringify({ nickname: undefined, greet() {} }));
""",
         r"""
console.log(JSON.stringify({ nickname: null }));
""",
         "`JSON.stringify` drops `undefined`-valued keys and functions. Use `null` for \"deliberately empty\"."),
        ("A `Map` serialises as `{}`",
         r"""
const scores = new Map([["ana", 3], ["bo", 5]]);
console.log(JSON.stringify(scores));
""",
         r"""
const scores = new Map([["ana", 3], ["bo", 5]]);
console.log(JSON.stringify(Object.fromEntries(scores)));
""",
         "A `Map` has no enumerable own properties. Convert it to an object (or to `[...map]` pairs) first."),
    ],
    later=[
        "**Week 11 — Narrowing.** Checking `unknown` data field by field.",
        "**Week 17 — Runtime validation.** Schemas that validate JSON and produce its type.",
        "**Week 25 — `Result`.** Returning parse failures instead of throwing them.",
    ],
)
