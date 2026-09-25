# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The original Month 1 TypeScript chapters, brought up to the lesson template
# (TS_MASTERY_ROADMAP.md F-12, X-02/X-03) with `_deepen` from ts_chapter_kit.py:
#
#   ts_variables  ts_types  ts_inference  ts_operators  ts_conditionals
#   ts_loops  ts_number_math  ts_strings  ts_string_methods
#
# Each keeps its original lesson as the core and gains "Why it exists", more
# worked examples, real compiler errors, pitfalls and forward links. Every
# output and compiler message is computed (python tools/gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_deepen(
    "ts_variables",
    why=r"""
Every program keeps track of things: the running total, the name the user typed,
the index of the line being read. A variable gives a value a name — and in
TypeScript it also records two promises about that name: *what kind of value it
holds* (its type) and *whether it will ever point at something else* (`const` or
`let`).

Those promises are what let the compiler help. A `const` can't be reassigned by a
typo three screens later; a block-scoped `let` can't leak out of the `if` that
created it; reading a variable before its line is an error instead of a silent
`undefined`. Most of this chapter is about choosing the declaration that says
exactly what you mean.
""",
    examples=[
        ("`const` fixes the name, not the contents",
         r"""
const scores = [70, 85];
scores.push(92);
const user = { name: "ana", visits: 1 };
user.visits += 1;
console.log(scores.join(","), user.visits);
""", [""],
         "`const` stops `scores = …`, not `scores.push(…)`. To stop the contents changing you need `readonly` types or `Object.freeze` (week 16)."),
        ("A fresh `let` for every loop iteration",
         r"""
const printers: (() => string)[] = [];
for (let i = 0; i < 3; i++) {
  printers.push(() => `printer ${i}`);
}
console.log(printers.map((p) => p()).join(", "));
""", [""],
         "Each iteration gets its own `i`, so each function remembers a different value. With `var` all three would share one variable and print 3."),
        ("Shadowing: an inner name hides an outer one",
         r"""
const label = "outer";
function show(): string {
  const label = "inner";
  return label;
}
{
  const label = "block";
  console.log(label);
}
console.log(show(), label);
""", [""],
         "Each `{ }` can declare its own `label`. Legal, but easy to misread — prefer distinct names unless the shadowing is the point."),
    ],
    errors=[
        (2588, r"""
const total = 0;
total = total + 5;
""", "A `const` binding can never be pointed at a new value. Use `let` if the value really changes."),
        (2448, r"""
console.log(count);
let count = 1;
""", "`let` and `const` exist from the start of their block but can't be read before their line (the temporal dead zone). The compiler catches it before the runtime would throw."),
    ],
    pitfalls=[
        ("`var` in a loop shares one variable",
         r"""
const fns: (() => number)[] = [];
for (var i = 0; i < 3; i++) fns.push(() => i);
console.log(fns.map((f) => f()).join(" "));
""",
         r"""
const fns: (() => number)[] = [];
for (let i = 0; i < 3; i++) fns.push(() => i);
console.log(fns.map((f) => f()).join(" "));
""",
         "`var` is function-scoped: all three closures see the same `i`, which is 3 once the loop ends. `let` creates a new binding per iteration."),
        ("A `const` object changed through a helper",
         r"""
const defaults = { debug: false };
function withDebug(config: { debug: boolean }) {
  config.debug = true;
  return config;
}
const mine = withDebug(defaults);
console.log(defaults.debug, mine.debug);
""",
         r"""
const defaults = { debug: false };
function withDebug(config: { debug: boolean }) {
  return { ...config, debug: true };
}
const mine = withDebug(defaults);
console.log(defaults.debug, mine.debug);
""",
         "`const defaults` didn't protect the object — the helper mutated the shared value. Return a copy instead."),
        ("A shadowed total that never grows",
         r"""
let total = 0;
for (const x of [1, 2, 3]) {
  let total = 0;
  total += x;
}
console.log("total " + total);
""",
         r"""
let total = 0;
for (const x of [1, 2, 3]) {
  total += x;
}
console.log("total " + total);
""",
         "The inner `let total` is a different variable that disappears each iteration. The outer one is never touched."),
    ],
    later=[
        "**Week 5 — Closures.** Why each loop iteration's `let` matters to callbacks.",
        "**Week 11 — Narrowing.** A `const` keeps its narrowed type inside callbacks; a reassigned `let` may not.",
        "**Week 16 — Immutability.** `readonly` and `Object.freeze` for the contents `const` doesn't protect.",
    ],
)


_deepen(
    "ts_types",
    why=r"""
JavaScript values come in a handful of kinds — numbers, strings, booleans,
`null`, `undefined`, objects — and most bugs are one kind turning up where another
was expected: `"5" + 1` is `"51"`, `undefined.length` crashes. TypeScript gives
each variable, parameter and return value a *type*, and checks every use against
it before the program runs.

Types cost nothing at runtime — they are erased — but they change how you write
code: a function's signature becomes a contract you can read instead of guess, and
the editor can tell you what a value is at every point. This chapter is the basic
vocabulary: the primitive types, `null` and `undefined`, and the two escape
hatches, `any` and `unknown`.
""",
    examples=[
        ("What each value is at runtime",
         r"""
const values: unknown[] = [42, "hi", true, null, undefined, [1], { a: 1 }, 10n];
for (const v of values) {
  const kind = v === null ? "null" : Array.isArray(v) ? "array" : typeof v;
  console.log(`${String(v)} -> ${kind}`);
}
""", [""],
         "`typeof` is the runtime view: `null` reports `\"object\"` and arrays report `\"object\"`, so real code checks them first. TypeScript's types are richer, but they're gone by the time this runs."),
        ("A literal type as a promise",
         r"""
function setMode(mode: "light" | "dark"): string {
  return mode === "dark" ? "white text on black" : "black text on white";
}
console.log(setMode("dark"));
console.log(setMode("light"));
""", [""],
         "`\"light\" | \"dark\"` is narrower than `string`: the compiler rejects `setMode(\"blue\")` before it can run."),
        ("`null` and `undefined` in data",
         r"""
const profile = { name: "ana", nickname: null, age: undefined };
console.log(JSON.stringify(profile));
console.log("nickname" in profile, "age" in profile, profile.age === undefined);
""", [""],
         "`null` is \"deliberately empty\" and survives JSON; an `undefined` property is dropped from JSON even though the key exists in the object."),
    ],
    errors=[
        (2322, r"""
let count: number = "5";
""", "The annotation says `number`; a string can't go there. Convert explicitly: `Number(\"5\")`."),
        (2345, r"""
const biggest = Math.max("3", 4);
""", "`Math.max` takes numbers. JavaScript would quietly convert `\"3\"`; TypeScript makes you say so."),
    ],
    pitfalls=[
        ("`Number` is not `number`",
         r"""
const boxed: Number = new Number(5);
console.log(boxed === 5);
""",
         r"""
const plain: number = 5;
console.log(plain === 5);
""",
         "`Number` (capital N) is the wrapper object type. A `new Number(5)` is an object, and objects are never `===` to a primitive. Always use the lower-case primitive types."),
        ("`typeof null` is `\"object\"`",
         r"""
function describe(v: unknown): string {
  return typeof v === "object" ? "an object" : "not an object";
}
console.log(describe(null), describe({}));
""",
         r"""
function describe(v: unknown): string {
  return v !== null && typeof v === "object" ? "an object" : "not an object";
}
console.log(describe(null), describe({}));
""",
         "A historical quirk of JavaScript. Every object check must rule out `null` first."),
        ("`any` switches checking off — everywhere it spreads",
         r"""
const data: any = JSON.parse('{"n":"5"}');
const next: number = data.n + 1;
console.log(next);
""",
         r"""
const data: unknown = JSON.parse('{"n":"5"}');
const n = typeof data === "object" && data !== null && "n" in data ? Number(data.n) : 0;
console.log(n + 1);
""",
         "With `any`, `data.n + 1` compiled and produced the string `\"51\"` — typed as `number`. `unknown` forces the check that converts it."),
    ],
    later=[
        "**Week 1 — Inference.** When you don't need to write a type at all.",
        "**Week 10 — Unions and literal types.** Types like `\"light\" | \"dark\"` in depth.",
        "**Week 12 — Top and bottom types.** `unknown`, `never`, `{}` and `object`.",
    ],
)


_deepen(
    "ts_inference",
    why=r"""
If you had to annotate every variable, TypeScript would be exhausting to write.
You don't: the compiler *infers* a type from each initialiser, return statement
and callback position, and most local variables need no annotation at all.

Knowing what gets inferred matters for two reasons. It tells you where
annotations are actually required — function parameters, mostly — and it
explains the surprises: why `let x = "up"` is a `string` but `const x = "up"` is
`"up"`, why an object's properties don't keep their literal types, and why a
function that forgets a `return` is typed as possibly `undefined`.
""",
    examples=[
        ("Types flowing into callbacks",
         r"""
const prices = [3.5, 10, 7.25];
const withTax = prices.map((p) => p * 1.2);
const cheap = prices.filter((p) => p < 8);
console.log(withTax.map((p) => p.toFixed(2)).join(" "));
console.log(cheap.length);
""", [""],
         "No annotation on `p`: it's inferred from `prices` (contextual typing), so `p.toFixed` is checked. The results' types (`number[]`) are inferred too."),
        ("The best common type",
         r"""
const mixed = [1, "two", 3];
const numbersOnly = mixed.filter((x) => typeof x === "number");
console.log(mixed.length, numbersOnly.join("+"));
""", [""],
         "`mixed` is inferred as `(string | number)[]`, and the filter's arrow is inferred as a type predicate (TS 5.5), so `numbersOnly` is `number[]`."),
        ("Return types, inferred from every path",
         r"""
function classify(n: number) {
  if (n < 0) return "negative";
  if (n === 0) return 0;
  return "positive";
}
for (const n of [-2, 0, 5]) console.log(typeof classify(n), classify(n));
""", [""],
         "The inferred return type is `\"negative\" | 0 | \"positive\"` — every `return` contributes. Mixing kinds like this is usually a sign to annotate the return type and let the compiler hold you to it."),
    ],
    errors=[
        (7006, r"""
function double(x) {
  return x * 2;
}
""", "A parameter has nothing to infer from, so under `strict` it must be annotated: `(x: number)`."),
        (2322, r"""
let attempts = 0;
attempts = "three";
""", "`attempts` was inferred as `number` from its initialiser; later assignments must match."),
    ],
    pitfalls=[
        ("A `let` widens its literal",
         (r"""
function move(dir: "up" | "down"): string {
  return "moving " + dir;
}
let dir = "up";
console.log(move(dir));
""", 2345),
         r"""
function move(dir: "up" | "down"): string {
  return "moving " + dir;
}
const dir = "up";
console.log(move(dir));
""",
         "`let dir = \"up\"` is inferred as `string` because it could be reassigned to anything. A `const` keeps `\"up\"`."),
        ("Object properties widen too",
         (r"""
function send(method: "GET" | "POST"): string {
  return method + " sent";
}
const request = { method: "GET" };
console.log(send(request.method));
""", 2345),
         r"""
function send(method: "GET" | "POST"): string {
  return method + " sent";
}
const request = { method: "GET" } as const;
console.log(send(request.method));
""",
         "Properties are mutable, so `request.method` is a `string`. `as const` (or an annotation) keeps the literal."),
        ("A forgotten branch returns `undefined`",
         r"""
function label(n: number) {
  if (n > 0) return "positive";
}
console.log("label: " + label(-1));
""",
         r"""
function label(n: number): string {
  if (n > 0) return "positive";
  return "not positive";
}
console.log("label: " + label(-1));
""",
         "Inference happily typed the first version as `\"positive\" | undefined`. Annotating the return type turns a missing branch into a compile error."),
    ],
    later=[
        "**Week 10 — Literal inference.** `as const`, widening rules and `const` type parameters.",
        "**Week 18 — Generic inference.** How type arguments are inferred from calls.",
    ],
)


_deepen(
    "ts_operators",
    why=r"""
Operators are where JavaScript's type coercion lives: `+` concatenates as soon as
one side is a string, `==` converts before comparing, `||` treats `0` and `""` as
missing. Much of TypeScript's early value is rejecting the combinations that are
almost always bugs — arithmetic on strings, comparing a boolean with a number —
while leaving the useful operators alone.

This chapter is the everyday toolkit: arithmetic (including `%` and `**`),
comparison, the logical operators and their short-circuiting, and the two modern
additions that replace most `||` defaults: `??` and optional chaining.
""",
    examples=[
        ("Integer arithmetic on floating-point numbers",
         r"""
const minutes = 137;
console.log(Math.trunc(minutes / 60), minutes % 60);
console.log(2 ** 10, 7 / 2, Math.floor(7 / 2));
""", [""],
         "There is no integer type: `/` always divides exactly. Use `Math.trunc`/`Math.floor` for whole quotients and `%` for remainders."),
        ("`++` before and after",
         r"""
let i = 5;
const a = i++;
const b = ++i;
console.log(a, b, i);
""", [""],
         "`i++` yields the old value then increments; `++i` increments then yields. Most style guides prefer `i += 1` to avoid the question."),
        ("Defaults that keep zero",
         r"""
const settings: { retries?: number; name?: string } = { retries: 0, name: "" };
console.log(settings.retries || 3, settings.retries ?? 3);
console.log(JSON.stringify(settings.name || "anon"), JSON.stringify(settings.name ?? "anon"));
""", [""],
         "`||` replaces every falsy value; `??` only `null` and `undefined`. For numbers and strings that may legitimately be 0 or empty, `??` is almost always what you want."),
    ],
    errors=[
        (2362, r"""
const doubled = "21" * 2;
""", "Arithmetic needs numbers. JavaScript would convert the string; TypeScript asks you to do it explicitly with `Number(...)`."),
        (2365, r"""
const ordered = 3 > 2 > 1;
""", "`3 > 2` is `true`, and `true > 1` compares a boolean with a number — legal JavaScript (and `false`!), rejected by TypeScript."),
    ],
    pitfalls=[
        ("`+` joins text",
         r"""
const [a = "", b = ""] = "1 2".split(" ");
console.log(a + b);
""",
         r"""
const [a = "", b = ""] = "1 2".split(" ");
console.log(Number(a) + Number(b));
""",
         "Values read from input are strings, and `+` on strings concatenates. Convert first."),
        ("`%` keeps the sign of the dividend",
         r"""
const hours = 24;
const shifted = (-7) % hours;
console.log("hour " + shifted);
""",
         r"""
const hours = 24;
const shifted = (((-7) % hours) + hours) % hours;
console.log("hour " + shifted);
""",
         "JavaScript's `%` is a remainder, not a modulo: negative in, negative out. Wrap around with `((a % n) + n) % n`."),
        ("`||` treats zero as missing",
         r"""
function volume(level?: number): number {
  return level || 5;
}
console.log(volume(0), volume(8), volume());
""",
         r"""
function volume(level?: number): number {
  return level ?? 5;
}
console.log(volume(0), volume(8), volume());
""",
         "Muting (level 0) turned into volume 5. `??` defaults only when the value is really absent."),
    ],
    later=[
        "**Week 2 — Equality.** `===`, `Object.is` and the truthiness table.",
        "**Week 3 — Numbers.** Rounding, floating point and `bigint`.",
        "**Week 11 — Nullish.** `?.`, `??` and `??=` for data that may be missing.",
    ],
)


_deepen(
    "ts_conditionals",
    why=r"""
Almost every program decides something: pass or fail, which command to run, what
to print for an empty list. `if`/`else`, `switch` and the conditional operator
`?:` are the tools, and choosing between them is mostly about readability — a
`switch` for one value against many cases, early returns to keep the main path
unindented, a ternary only when the result is a value.

TypeScript adds something the plain language lacks: conditions *narrow* types.
Inside `if (typeof x === "string")`, `x` is a string. That idea grows into week
11's narrowing chapter; here it's the everyday benefit of writing clear branches.
""",
    examples=[
        ("Guard clauses keep the main path flat",
         r"""
function grade(score: number): string {
  if (!Number.isFinite(score)) return "invalid";
  if (score < 0 || score > 100) return "out of range";
  if (score >= 90) return "A";
  if (score >= 75) return "B";
  return "C";
}
console.log([95, 80, 42, 120, NaN].map(grade).join(" "));
""", [""],
         "Each early `return` handles one case and gets out of the way; the order of the checks is the specification."),
        ("Grouped `switch` cases",
         r"""
function kind(day: string): string {
  switch (day) {
    case "sat":
    case "sun":
      return "weekend";
    case "mon":
    case "tue":
    case "wed":
    case "thu":
    case "fri":
      return "weekday";
    default:
      return "not a day";
  }
}
console.log(["sat", "wed", "xyz"].map(kind).join(", "));
""", [""],
         "Stacked `case` labels share one body. Returning from each case avoids the need for `break`."),
        ("A ternary for a value, `if` for an action",
         r"""
const items = ["pen"];
const noun = items.length === 1 ? "item" : "items";
console.log(`${items.length} ${noun}`);
if (items.length > 0) {
  console.log("first: " + items[0]);
}
""", [""],
         "`?:` produces a value, so it fits inside an expression. When a branch *does* something, an `if` reads better."),
    ],
    errors=[
        (2367, r"""
type Size = "s" | "m";
function check(size: Size): string {
  if (size === "l") return "large";
  return size;
}
""", "`size` can never be `\"l\"`, so the comparison is always false — usually a typo or an out-of-date union."),
        (2678, r"""
type Size = "s" | "m";
function label(size: Size): string {
  switch (size) {
    case "s":
      return "small";
    case "x":
      return "extra";
    default:
      return "medium";
  }
}
""", "The same check for `switch`: a `case` that can't match the switched value's type is flagged."),
    ],
    pitfalls=[
        ("A `switch` that falls through",
         r"""
function price(size: string): number {
  let p = 0;
  switch (size) {
    case "small":
      p = 5;
    case "large":
      p = 9;
  }
  return p;
}
console.log(price("small"), price("large"));
""",
         r"""
function price(size: string): number {
  let p = 0;
  switch (size) {
    case "small":
      p = 5;
      break;
    case "large":
      p = 9;
      break;
  }
  return p;
}
console.log(price("small"), price("large"));
""",
         "Without `break`, `small` ran on into the `large` case and was overwritten. (`noFallthroughCasesInSwitch` makes this an error.)"),
        ("Assignment where a comparison was meant",
         r"""
let x = 1;
if ((x = 5)) console.log("x was five?");
console.log("x is " + x);
""",
         r"""
let x = 1;
if (x === 5) console.log("x was five?");
console.log("x is " + x);
""",
         "`x = 5` assigns and evaluates to 5, which is truthy — the branch runs and `x` is changed. Use `===`."),
        ("Checks in the wrong order",
         r"""
function band(score: number): string {
  if (score >= 50) return "pass";
  if (score >= 90) return "excellent";
  return "fail";
}
console.log(band(95));
""",
         r"""
function band(score: number): string {
  if (score >= 90) return "excellent";
  if (score >= 50) return "pass";
  return "fail";
}
console.log(band(95));
""",
         "The first matching branch wins, so the most specific condition must come first."),
    ],
    later=[
        "**Week 11 — Narrowing.** How conditions change a variable's type inside each branch.",
        "**Week 12 — Discriminated unions.** `switch` on a tag with exhaustiveness checking.",
    ],
)


_deepen(
    "ts_loops",
    why=r"""
Loops are how a program handles *any number* of things — every line of input,
every item in a cart, every step of a simulation. JavaScript has several loop
forms, and they differ in ways that matter: `for…of` walks values, `for…in` walks
property *names* (as strings), `while` suits "until something happens", and a
classic `for (let i…)` gives you the index.

Choosing the right one removes whole classes of bugs — off-by-one indexes,
string keys where numbers were expected, mutating a list while walking it. This
chapter pairs each form with the job it does best.
""",
    examples=[
        ("Index and value together",
         r"""
const tasks = ["write", "test", "ship"];
for (const [i, task] of tasks.entries()) {
  console.log(`${i + 1}. ${task}`);
}
""", [""],
         "`entries()` gives `[index, value]` pairs, so `for…of` covers the case people usually reach for a counting `for` loop to handle."),
        ("A `while` loop that runs until a condition",
         r"""
let n = 27;
let steps = 0;
while (n !== 1) {
  n = n % 2 === 0 ? n / 2 : 3 * n + 1;
  steps++;
}
console.log(`27 reaches 1 in ${steps} steps`);
""", [""],
         "When you can't say in advance how many iterations there will be, `while` states the stopping condition directly."),
        ("Breaking out of nested loops",
         r"""
const xs = [3, 8, 11, 15];
let found = "none";
search: for (const a of xs) {
  for (const b of xs) {
    if (a < b && a + b === 19) {
      found = `${a} + ${b}`;
      break search;
    }
  }
}
console.log(found);
""", [""],
         "A label names the outer loop so one `break` can leave both. Often a function with an early `return` reads even better."),
    ],
    errors=[
        (2588, r"""
const xs = [1, 2, 3];
for (const x of xs) {
  x = x * 2;
}
""", "A `for…of` variable declared with `const` is a new constant each iteration. To transform values, build a new array (`map`)."),
        (7053, r"""
const prices = { pen: 2, cup: 5 };
let total = 0;
for (const item in prices) total += prices[item];
""", "`for…in` gives keys as plain `string`s, which aren't known to be keys of `prices`. Use `Object.values(prices)` or `Object.entries(prices)`."),
    ],
    pitfalls=[
        ("`for…in` over an array gives indexes as strings",
         r"""
const out: string[] = [];
for (const i in ["a", "b"]) out.push(i);
console.log(out.join(","));
""",
         r"""
const out: string[] = [];
for (const x of ["a", "b"]) out.push(x);
console.log(out.join(","));
""",
         "`for…in` is for object keys; `for…of` is for values."),
        ("Removing items while iterating",
         r"""
const xs = [2, 4, 6, 7];
for (const x of xs) {
  if (x % 2 === 0) xs.splice(xs.indexOf(x), 1);
}
console.log(xs.join(","));
""",
         r"""
const xs = [2, 4, 6, 7];
const odd = xs.filter((x) => x % 2 !== 0);
console.log(odd.join(","));
""",
         "Removing an element shifts the rest left, so the loop skips the next one. Build a new array instead."),
        ("One step too far",
         r"""
const xs = [10, 20];
const out: string[] = [];
for (let i = 0; i <= xs.length; i++) out.push(String(xs[i]));
console.log(out.join(" "));
""",
         r"""
const xs = [10, 20];
const out: string[] = [];
for (let i = 0; i < xs.length; i++) out.push(String(xs[i]));
console.log(out.join(" "));
""",
         "Indexes run from 0 to `length - 1`. `noUncheckedIndexedAccess` (week 14) makes the `undefined` visible in the type."),
    ],
    later=[
        "**Week 6 — Higher-order functions.** `map`, `filter` and `reduce` replace many loops.",
        "**Week 24 — Iterators and generators.** What `for…of` is really calling.",
    ],
)


_deepen(
    "ts_number_math",
    why=r"""
JavaScript has one number type: a 64-bit floating-point value. That's convenient
— no `int` vs `double` decisions — but it means `0.1 + 0.2` isn't `0.3`, integer
division needs `Math.trunc`, and whole numbers above 2^53 silently lose
precision. The `Math` object fills in the rest: rounding, powers, minimum and
maximum, randomness.

Knowing these rules is the difference between output that matches the judge and
output that is off in the last decimal place. For money and big integers there
are better tools — integer cents and `bigint` — and this chapter shows when to
reach for them.
""",
    examples=[
        ("Four ways to round",
         r"""
for (const x of [2.5, -2.5, 2.7]) {
  console.log(x, Math.round(x), Math.floor(x), Math.ceil(x), Math.trunc(x));
}
""", [""],
         "`round` sends exact halves up (towards +∞, so -2.5 becomes -2), `floor` goes down, `ceil` up, `trunc` towards zero."),
        ("Past the safe-integer limit",
         r"""
const big = 2 ** 53;
console.log(big + 1 === big, Number.isSafeInteger(big));
const exact = 2n ** 53n + 1n;
console.log(exact.toString());
""", [""],
         "Above `Number.MAX_SAFE_INTEGER` some integers can't be represented; `bigint` (the `n` suffix) is exact at any size."),
        ("Clamping with `Math.min` and `Math.max`",
         r"""
const clamp = (x: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, x));
for (const v of [-5, 42, 180]) console.log(`${v} -> ${clamp(v, 0, 100)}%`);
""", [""],
         "Bounding a value into a range is one expression — handy for percentages, indexes and volumes."),
    ],
    errors=[
        (2365, r"""
const next = 10n + 1;
""", "`bigint` and `number` don't mix in arithmetic. Write `10n + 1n`, or convert with `BigInt(1)` / `Number(10n)`."),
        (2345, r"""
const r = Math.round("2.5");
""", "The `Math` functions take numbers. Convert text first."),
    ],
    pitfalls=[
        ("Comparing floats with `===`",
         r"""
const total = 0.1 + 0.2;
console.log(total === 0.3 ? "equal" : "not equal");
""",
         r"""
const total = 0.1 + 0.2;
console.log(Math.abs(total - 0.3) < Number.EPSILON ? "equal" : "not equal");
""",
         "Binary floating point can't represent 0.1 exactly. Compare with a tolerance, or avoid fractions altogether."),
        ("Money as floating-point dollars",
         r"""
let total = 0;
for (let i = 0; i < 10; i++) total += 0.1;
console.log(total);
""",
         r"""
let cents = 0;
for (let i = 0; i < 10; i++) cents += 10;
console.log((cents / 100).toFixed(2));
""",
         "Ten dimes added as floats come to 0.9999999999999999. Integer cents are exact; format only for display."),
        ("`toFixed` returns a string",
         r"""
const price = (1.5).toFixed(1);
console.log(price + 1);
""",
         r"""
const price = Number((1.5).toFixed(1));
console.log(price + 1);
""",
         "`toFixed` is for display. Doing arithmetic on its result concatenates."),
    ],
    later=[
        "**Week 3 — Number formatting.** `Intl.NumberFormat`, grouping and currencies.",
        "**Week 16 — Branded types.** A `Cents` type that can't be mixed with plain numbers.",
    ],
)


_deepen(
    "ts_strings",
    why=r"""
Almost every program in this programme reads text and writes text: stdin arrives
as one string, output is built as strings, and most data formats — CSV, JSON,
logs — are text. Strings in JavaScript are immutable sequences of UTF-16 code
units, which explains nearly every surprise: methods return *new* strings, `s[0]
= "x"` does nothing, and an emoji has a `length` of 2.

Template literals (`` `…${x}…` ``) are the modern way to build output, and
comparing strings — for equality, sorting, or ignoring case — needs a little care.
This chapter covers the text you'll handle every day.
""",
    examples=[
        ("Template literals for output",
         r"""
const name = "Ada";
const items = ["pen", "cup"];
const receipt = `Customer: ${name}
Items: ${items.length} (${items.join(", ")})
Total: $${(12.5).toFixed(2)}`;
console.log(receipt);
""", [""],
         "Any expression goes inside `${}`, and a template can span lines. `$${…}` prints a literal dollar sign before the value."),
        ("Methods return new strings",
         r"""
const original = "  Hello, World  ";
const cleaned = original.trim().toLowerCase();
console.log(JSON.stringify(original));
console.log(JSON.stringify(cleaned));
""", [""],
         "Strings never change in place. Keep the result of every method call."),
        ("Comparing text",
         r"""
const a: string = "Apple";
const b: string = "apple";
console.log(a === b, a.toLowerCase() === b.toLowerCase());
console.log(["b", "a", "C"].sort((x, y) => x.localeCompare(y)).join(","));
""", [""],
         "`===` compares exactly. Normalise case for case-insensitive equality, and use `localeCompare` for human sort order."),
    ],
    errors=[
        (2339, r"""
const word = "abc";
console.log(word.size);
""", "Strings have `length`, not `size`. The compiler knows every member of `string`."),
        (2542, r"""
const s: string = "cat";
s[0] = "b";
""", "String characters are read-only. Build a new string: `\"b\" + s.slice(1)`."),
    ],
    pitfalls=[
        ("`length` counts code units, not characters",
         r"""
const face = "😀";
console.log(face.length);
""",
         r"""
const face = "😀";
console.log([...face].length);
""",
         "An emoji outside the Basic Multilingual Plane takes two UTF-16 code units. Spreading a string iterates by code point."),
        ("`replace` with a string changes only the first match",
         r"""
console.log("a-b-c".replace("-", "+"));
""",
         r"""
console.log("a-b-c".replaceAll("-", "+"));
""",
         "Use `replaceAll`, or a regex with the `g` flag."),
        ("The default sort is by code unit",
         r"""
console.log(["banana", "apple", "Cherry"].sort().join(","));
""",
         r"""
console.log(["banana", "apple", "Cherry"].sort((a, b) => a.localeCompare(b)).join(","));
""",
         "Upper-case letters sort before all lower-case ones in code-unit order. `localeCompare` sorts the way people expect."),
    ],
    later=[
        "**Week 4 — String methods, regex and Unicode.** `split`, `slice`, patterns and grapheme segmentation.",
        "**Week 22 — Template literal types.** The same `${…}` syntax, at the type level.",
    ],
)


_deepen(
    "ts_string_methods",
    why=r"""
Reading input is mostly string manipulation: split the text into lines, split a
line into fields, trim whitespace, find a separator, slice out a part, pad a
column for output. A dozen methods cover almost all of it, and knowing their exact
behaviour — what `split` does with repeated spaces, what `indexOf` returns when
nothing matches, how negative indexes work — is what makes a parser correct on
the awkward inputs a judge will try.
""",
    examples=[
        ("Parsing `key=value` pairs",
         r"""
const text = " name = Ana ; city=Oslo;  role =admin ";
const fields = new Map<string, string>();
for (const part of text.split(";")) {
  const eq = part.indexOf("=");
  if (eq < 0) continue;
  fields.set(part.slice(0, eq).trim(), part.slice(eq + 1).trim());
}
console.log([...fields].map(([k, v]) => `${k}:${v}`).join(" "));
""", [""],
         "`split` on the record separator, `indexOf` to find the first `=`, `slice` on either side, `trim` everything."),
        ("A padded table",
         r"""
const rows: [string, number][] = [["pen", 2], ["notebook", 12], ["ink", 7]];
for (const [name, qty] of rows) {
  console.log(name.padEnd(10, ".") + String(qty).padStart(4));
}
""", [""],
         "`padEnd` and `padStart` align columns without counting spaces by hand."),
        ("Counting occurrences",
         r"""
const text = "the cat and the hat and the bat";
const count = (word: string) => text.split(" ").filter((w) => w === word).length;
console.log(count("the"), count("and"), count("dog"));
console.log(text.split("at").length - 1);
""", [""],
         "Split and count words; for a substring, the number of pieces minus one is the number of occurrences."),
    ],
    errors=[
        (2554, r"""
const line = "ab".repeat();
""", "`repeat` needs a count. The compiler checks every method's parameter list."),
        (2345, r"""
const hasOne = "a1b".includes(1);
""", "`includes` on a string searches for a *string*. Pass `\"1\"`."),
    ],
    pitfalls=[
        ("Splitting on a single space",
         r"""
const words = "one  two   three".split(" ");
console.log(words.length);
""",
         r"""
const words = "one  two   three".split(/\s+/);
console.log(words.length);
""",
         "Runs of spaces produce empty strings between them. Split on `/\\s+/` (after trimming) to get just the words."),
        ("`indexOf` returns 0 for a match at the start",
         r"""
const s = "apple pie";
console.log(s.indexOf("apple") ? "found" : "not found");
""",
         r"""
const s = "apple pie";
console.log(s.includes("apple") ? "found" : "not found");
""",
         "`indexOf` returns the position — 0 here, which is falsy — or -1 when absent. Use `includes` for yes/no questions."),
        ("`substring` ignores negative indexes",
         r"""
console.log("abcdef".substring(-2));
""",
         r"""
console.log("abcdef".slice(-2));
""",
         "`substring` treats negatives as 0; `slice` counts them from the end. Prefer `slice`."),
    ],
    later=[
        "**Week 4 — Regular expressions.** Patterns for everything `split` and `indexOf` can't express.",
        "**Week 14 — Parsing a `.env` file.** These methods, under `noUncheckedIndexedAccess`.",
    ],
)
