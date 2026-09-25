# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The original Month 4 TypeScript chapters, brought up to the lesson template
# (TS_MASTERY_ROADMAP.md F-12, X-02/X-03) with `_deepen`:
#
#   ts_tsconfig  ts_modules  ts_declaration_files  ts_assertions  ts_satisfies
#   ts_structural_typing  ts_branded_types  ts_immutability  ts_compose
#   ts_utility_types
#
# Programs here are single files, so module and declaration examples use `fs`,
# dynamic import and `declare global`; multi-file mistakes are shown as real
# compiler errors. Every output and message is computed (gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_deepen(
    "ts_tsconfig",
    why=r"""
The same source file can be checked leniently or strictly: `tsconfig.json`
decides whether a parameter without a type is an error, whether `string` includes
`null`, whether an array read admits it may be `undefined`. Those flags change
what your types *mean*, so the configuration is part of the program — two
projects with different settings are effectively checking different languages.

This app runs every program under `strict`, and from week 14 of this programme
also under `noUncheckedIndexedAccess`. Knowing what each flag buys you — and
what it costs to adopt — is how you choose a configuration on purpose rather
than by copying one.
""",
    examples=[
        ("Code that is honest about index reads",
         r"""
function nth<T>(xs: readonly T[], i: number): T | undefined {
  return xs[i];
}
const names = ["ana", "bo"];
for (const i of [0, 1, 5]) {
  const n = nth(names, i);
  console.log(n === undefined ? `no name at ${i}` : `name ${i}: ${n.toUpperCase()}`);
}
""", [""],
         "Under `noUncheckedIndexedAccess`, `xs[i]` is already `T | undefined`, so code written this way compiles under both settings — and handles the out-of-range case either way."),
        ("Absent versus explicitly undefined",
         r"""
type Profile = { nickname?: string };
const absent: Profile = {};
const cleared: Profile = { nickname: undefined };
console.log("nickname" in absent, "nickname" in cleared);
console.log(JSON.stringify(absent), JSON.stringify(cleared));
""", [""],
         "Both values are allowed by default, and they behave differently at runtime. `exactOptionalPropertyTypes` forbids the second unless the type says `nickname?: string | undefined`."),
        ("Every path returns",
         r"""
function price(size: "s" | "m" | "l"): number {
  switch (size) {
    case "s":
      return 2;
    case "m":
      return 3;
    case "l":
      return 4;
  }
}
console.log(price("s") + price("l"));
""", [""],
         "With `strict`, a function whose declared return type isn't `undefined` must return on every path; the exhaustive `switch` satisfies it. (`noImplicitReturns` extends the check to functions with inferred return types.)"),
    ],
    errors=[
        (2532, r"""
const readings = [21.5, 22.1];
console.log(readings[0].toFixed(1));
""", "With `noUncheckedIndexedAccess` every index read may be `undefined` — even `[0]` of a non-empty-looking array, because the type doesn't know its length.", "strict+indexed"),
        (7031, r"""
function describe({ name, age }) {
  return `${name} (${age})`;
}
""", "`noImplicitAny` also covers destructured parameters: give the whole parameter a type, `({ name, age }: { name: string; age: number })`."),
    ],
    pitfalls=[
        ("An index read assumed to exist",
         r"""
const scores = [90, 72];
const third = scores[2] as number;
console.log("average with third: " + (scores[0]! + scores[1]! + third) / 3);
""",
         r"""
const scores = [90, 72];
const present = [0, 1, 2].map((i) => scores[i]).filter((s) => s !== undefined);
console.log("average of present: " + present.reduce((a, b) => a + b, 0) / present.length);
""",
         "The cast (and the `!`s) silenced exactly the check the flag exists for, and `undefined` turned the average into `NaN`."),
        ("`@ts-ignore` hides a real error",
         r"""
// @ts-ignore
const quantity: number = "5";
console.log(quantity + 1);
""",
         r"""
const quantity: number = Number("5");
console.log(quantity + 1);
""",
         "`@ts-ignore` suppresses whatever error is on the next line, forever. Fix the cause — or use `@ts-expect-error`, which at least fails when the error goes away."),
        ("`in` treats a cleared property as present",
         r"""
type Settings = { theme?: string };
const s: Settings = { theme: undefined };
console.log("theme" in s ? `theme is ${s.theme}` : "default theme");
""",
         r"""
type Settings = { theme?: string };
const s: Settings = { theme: undefined };
console.log(s.theme !== undefined ? `theme is ${s.theme}` : "default theme");
""",
         "Without `exactOptionalPropertyTypes`, an optional property can hold `undefined` explicitly — and `in` still reports it. Check the value."),
    ],
    later=[
        "**Week 14 — TypeScript 6 and 7.** The new defaults and the deprecated options.",
        "**Week 14 — Erasable syntax.** `erasableSyntaxOnly` and `verbatimModuleSyntax`.",
        "**Week 17 — Utility types.** `Required<T>` and the `-?` modifier, the type-level cousins of these flags.",
    ],
)


_deepen(
    "ts_modules",
    why=r"""
Past a few hundred lines, a program needs files: one for parsing, one for the
data model, one for output. ES modules connect them — each file `export`s what
it offers and `import`s what it needs — and TypeScript checks every import
against the exporting file's types, so renaming a function breaks its callers at
compile time rather than at runtime.

This app's judged programs are single files that import one module, `fs`. That's
enough to see how imports are typed, what a namespace import is, and the errors
you'll meet in multi-file projects.
""",
    examples=[
        ("Named imports, typed by the module",
         r"""
import { readFileSync } from "fs";
const text = readFileSync(0, "utf8");
console.log(JSON.stringify(text), typeof readFileSync);
""", [""],
         "The declaration of `fs` says what `readFileSync` accepts and returns, so the call is checked. (The judge feeds this example empty stdin.)"),
        ("A namespace import",
         r"""
import * as fs from "fs";
const exported = Object.keys(fs).filter((k) => k === "readFileSync" || k === "writeFileSync");
console.log(exported.sort().join(","));
""", [""],
         "`import * as fs` gives one object holding every export — a module namespace, whose properties are read-only."),
        ("Loading a module on demand",
         r"""
const mod = await import("fs");
console.log(typeof mod.readFileSync, typeof mod.writeFileSync);
""", [""],
         "`await import(…)` loads a module when the code reaches it and returns the same namespace object; the result is still fully typed."),
    ],
    errors=[
        (2307, r"""
import { add } from "./math";
console.log(add(1, 2));
""", "The compiler resolves every import path. A missing file (or a wrong path, or a missing `.d.ts` for a package) is caught before running."),
        (2305, r"""
import { readFile } from "fs";
""", "The module has no export by that name. The compiler checks every imported name against what the other file actually exports."),
    ],
    pitfalls=[
        ("A dynamic import without `await`",
         (r"""
const mod = import("fs");
console.log(typeof mod.readFileSync);
""", 2339),
         r"""
const mod = await import("fs");
console.log(typeof mod.readFileSync);
""",
         "`import()` returns a *promise* of the module namespace. Await it (or `.then`) before reading exports."),
        ("`require` in an ES module",
         (r"""
const fs = require("fs");
console.log(typeof fs.readFileSync);
""", 2591),
         r"""
import * as fs from "fs";
console.log(typeof fs.readFileSync);
""",
         "`require` belongs to CommonJS. In an ES module, use `import` (or `await import()` to load lazily)."),
        ("Patching an imported binding",
         (r"""
import * as fs from "fs";
fs.readFileSync = () => "mocked";
""", 2540),
         r"""
import * as fs from "fs";
const read = (): string => "mocked";
console.log(read(), typeof fs.readFileSync);
""",
         "A module namespace is read-only; to substitute behaviour (in tests, say), pass the function in rather than overwriting the import."),
    ],
    later=[
        "**Week 14 — Declaration files.** How modules without types get them.",
        "**Week 14 — Erasable syntax.** `import type` and `verbatimModuleSyntax`.",
        "**Week 14 — The ledger project.** A single-file program organised like modules.",
    ],
)


_deepen(
    "ts_declaration_files",
    why=r"""
TypeScript can only check code whose types it knows. Your own `.ts` files carry
their types, but a plain JavaScript library, a global the runtime provides, or a
field a plugin adds to a built-in type doesn't. Declaration files (`.d.ts`) and
`declare` statements describe those things — shapes without implementations —
so the rest of your code is checked against them.

The catch is that declarations are *trusted*: the compiler can't see the real
JavaScript behind them. A declaration that doesn't match the runtime is a bug the
type system will happily hide, which is why this chapter's pitfalls are all
about declarations that lie.
""",
    examples=[
        ("Adding a method to every array",
         r"""
declare global {
  interface Array<T> {
    sumBy(this: T[], f: (x: T) => number): number;
  }
}
Array.prototype.sumBy = function <T>(this: T[], f: (x: T) => number): number {
  return this.reduce((s, x) => s + f(x), 0);
};
const cart = [{ price: 2, qty: 3 }, { price: 5, qty: 1 }];
console.log(cart.sumBy((i) => i.price * i.qty));
""", [""],
         "`declare global` reopens the built-in `Array<T>` interface (interfaces merge), and the implementation supplies the runtime part. Real projects rarely patch globals; libraries do it through declaration files."),
        ("Augmenting a built-in type",
         r"""
declare global {
  interface Error {
    code?: string;
  }
}
const e = new Error("disk full");
e.code = "ENOSPC";
console.log(`${e.code}: ${e.message}`);
""", [""],
         "Adding an optional field to `Error` lets code attach error codes without casts — exactly what Node's own type definitions do."),
        ("Types derived from a JavaScript value",
         r"""
export const defaults = { retries: 3, timeoutMs: 500, verbose: false };
export type Defaults = typeof defaults;
function describe(d: Defaults): string {
  return Object.entries(d).map(([k, v]) => `${k}=${v}`).join(" ");
}
console.log(describe(defaults));
""", [""],
         "This is what `tsc --declaration` does for a JavaScript-shaped module: it writes the types of the values it exports, and consumers get them for free."),
    ],
    errors=[
        (2304, r"""
console.log(BUILD_ID);
""", "An undeclared global is an error. If the runtime really provides it, declare it: `declare const BUILD_ID: string;`."),
        (1039, r"""
declare let version: string = "1.0";
""", "`declare` describes something that exists elsewhere, so it can't carry a value."),
    ],
    pitfalls=[
        ("A declaration nothing provides",
         r"""
declare const API_URL: string;
try {
  console.log("calling " + API_URL);
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const API_URL = "https://api.example.com";
console.log("calling " + API_URL);
""",
         "`declare` promised a global the runtime never defined. The compiler can't know — the program fails when it gets there."),
        ("A declaration that disagrees with the code",
         r"""
const lib = { add: (a: number, b: number) => a + b } as unknown as { add(a: number, b: number): string };
try {
  console.log(lib.add(1, 2).toUpperCase());
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const lib: { add(a: number, b: number): number } = { add: (a, b) => a + b };
console.log(lib.add(1, 2).toFixed(1));
""",
         "Types written by hand for someone else's code are claims. Here the claimed `string` was really a number. Test declarations against the real library."),
        ("An augmentation that forgets `undefined`",
         r"""
declare global {
  interface Array<T> {
    last(): T;
  }
}
Array.prototype.last = function () {
  return this[this.length - 1];
};
const empty: number[] = [];
try {
  console.log(empty.last().toFixed(2));
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
declare global {
  interface Array<T> {
    last(): T | undefined;
  }
}
Array.prototype.last = function () {
  return this[this.length - 1];
};
const empty: number[] = [];
console.log(empty.last()?.toFixed(2) ?? "empty");
""",
         "Declared as returning `T`, `last()` let the empty case through. The declaration must describe every value the code can return."),
    ],
    later=[
        "**Week 14 — The toolchain.** `types`, `skipLibCheck` and where declarations come from.",
        "**Week 14 — Problem set.** Declaring a library and augmenting a global, type-graded.",
    ],
)


_deepen(
    "ts_assertions",
    why=r"""
Sometimes you know more than the compiler: you checked a value in a way it can't
follow, or you're handling a well-understood API response. A type assertion
(`value as T`) or a non-null assertion (`value!`) tells the compiler to trust
you. They're erased at runtime — no conversion, no check — so an assertion is a
*claim*, and a wrong claim is a bug the type system can no longer see.

`as const` is the exception: it doesn't claim anything, it asks the compiler to
infer the narrowest types. This chapter separates the safe uses from the ones
that hide errors.
""",
    examples=[
        ("`as const` for a tuple return",
         r"""
function range(xs: readonly number[]) {
  return [Math.min(...xs), Math.max(...xs)] as const;
}
const [lo, hi] = range([4, 9, 2]);
console.log(lo, hi, hi - lo);
""", [""],
         "Without `as const` the return type is `number[]`; with it, a readonly pair, so destructuring gives two `number`s rather than `number | undefined` under strict indexing."),
        ("An assertion after a check the compiler can't follow",
         r"""
const stock = new Map([["pen", 3], ["cup", 1]]);
function take(item: string): string {
  if (!stock.has(item)) return `no ${item}`;
  const left = stock.get(item)! - 1;
  stock.set(item, left);
  return `${item}: ${left} left`;
}
console.log(take("pen"), "|", take("ink"));
""", [""],
         "`has` doesn't narrow `get`, so `!` records a fact you've just checked. Even better is one `get` and a `=== undefined` test."),
        ("A checked assertion helper",
         r"""
type Point = { x: number; y: number };
function asPoint(v: unknown): Point {
  if (typeof v === "object" && v !== null && "x" in v && "y" in v && typeof v.x === "number" && typeof v.y === "number") {
    return { x: v.x, y: v.y };
  }
  throw new TypeError("not a point: " + JSON.stringify(v));
}
for (const t of ['{"x":1,"y":2}', '{"x":1}']) {
  try {
    const p = asPoint(JSON.parse(t));
    console.log(p.x + p.y);
  } catch (e) {
    console.log(e instanceof Error ? e.message : String(e));
  }
}
""", [""],
         "Instead of `JSON.parse(t) as Point`, a function checks and either returns a real `Point` or throws."),
    ],
    errors=[
        (2352, r"""
const count = "5" as number;
""", "`as` refuses conversions between unrelated types, because they're almost always mistakes. Convert with `Number(\"5\")`."),
        (18048, r"""
const words = ["a", "bb"];
const long = words.find((w) => w.length > 5);
console.log(long.length);
""", "Without an assertion, the compiler insists on the `undefined` case — the check the `!` would skip."),
    ],
    pitfalls=[
        ("Asserting untrusted JSON",
         r"""
type Order = { qty: number };
const order = JSON.parse('{"qty":"3"}') as Order;
console.log(order.qty + 1);
""",
         r"""
type Order = { qty: number };
const raw: unknown = JSON.parse('{"qty":"3"}');
const qty = typeof raw === "object" && raw !== null && "qty" in raw ? Number(raw.qty) : 0;
const order: Order = { qty };
console.log(order.qty + 1);
""",
         "The assertion believed the JSON; `\"3\" + 1` is `\"31\"`. Check (or convert) data from outside."),
        ("`!` on a search that can miss",
         r"""
const users = [{ id: 1, name: "ana" }];
try {
  console.log(users.find((u) => u.id === 2)!.name);
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const users = [{ id: 1, name: "ana" }];
console.log(users.find((u) => u.id === 2)?.name ?? "no such user");
""",
         "`!` removed `undefined` from the type, not from the runtime. Handle the miss."),
        ("A double assertion",
         r"""
const input = "twelve";
const n = input as unknown as number;
console.log(n * 2);
""",
         r"""
const input = "twelve";
const n = Number(input);
console.log(Number.isNaN(n) ? "not a number" : n * 2);
""",
         "`as unknown as T` forces any conversion past the compiler. It's occasionally necessary at a boundary; it's never a way to turn text into a number."),
    ],
    later=[
        "**Week 15 — `satisfies`.** Checking a value against a type without asserting.",
        "**Week 16 — Branded types.** The one place an `as` is legitimate: inside a validating constructor.",
        "**Week 17 — Runtime validation.** Replacing `as T` on JSON with a schema.",
    ],
)


_deepen(
    "ts_satisfies",
    why=r"""
A type annotation does two jobs at once: it checks the value, and it *replaces*
the value's inferred type with the annotation. Often you want only the first:
check that a route table maps names to paths, but keep the exact keys so you can
derive a union of route names from them. `satisfies` (TS 4.9) does exactly that —
it validates the expression against a type and leaves the inferred type alone.

It's the tool for configuration objects, lookup tables and palettes: checked
thoroughly, and still precise enough to derive other types from.
""",
    examples=[
        ("Checked, with the keys kept",
         r"""
type Route = { path: string; auth: boolean };
const routes = {
  home: { path: "/", auth: false },
  settings: { path: "/settings", auth: true },
  billing: { path: "/billing", auth: true },
} satisfies Record<string, Route>;
type RouteName = keyof typeof routes;
const protectedRoutes = (Object.keys(routes) as RouteName[]).filter((n) => routes[n].auth);
console.log(protectedRoutes.join(","));
""", [""],
         "Every entry is checked against `Route`, and `RouteName` is still `\"home\" | \"settings\" | \"billing\"`."),
        ("Each entry keeps its own shape",
         r"""
type Field = { kind: "text"; maxLength: number } | { kind: "number"; min: number; max: number };
const form = {
  name: { kind: "text", maxLength: 20 },
  age: { kind: "number", min: 0, max: 150 },
} satisfies Record<string, Field>;
console.log(form.name.maxLength, form.age.max - form.age.min);
""", [""],
         "With an annotation, `form.age` would be the whole `Field` union and `.max` wouldn't type-check without narrowing. `satisfies` keeps each entry's specific member."),
        ("A lookup that must cover every case",
         r"""
type Status = "todo" | "doing" | "done";
const LABEL = { todo: "To do", doing: "In progress", done: "Done" } satisfies Record<Status, string>;
const statuses: Status[] = ["done", "todo"];
console.log(statuses.map((s) => LABEL[s]).join(" / "));
""", [""],
         "`satisfies Record<Status, string>` fails to compile if a status is missing — add one to the union, and the table must follow."),
    ],
    errors=[
        (2322, r"""
const server = { host: "localhost", port: "8080" } satisfies { host: string; port: number };
""", "`satisfies` reports the mismatching property itself."),
        (1360, r"""
const limit = 5 satisfies string;
""", "For a non-object value, the failure is reported on the whole expression."),
    ],
    pitfalls=[
        ("An annotation widens the keys",
         r"""
const routes: Record<string, string> = { home: "/", about: "/about" };
console.log("go to " + routes.hme);
""",
         (r"""
const routes = { home: "/", about: "/about" } satisfies Record<string, string>;
console.log("go to " + routes.hme);
""", 2551),
         "Typed as `Record<string, string>`, any key compiles, so the typo reached runtime as `undefined`. With `satisfies`, the object keeps its own keys and the typo is caught."),
        ("A narrow inferred type you later need to widen",
         (r"""
const theme = { mode: "dark" } satisfies { mode: "dark" | "light" };
theme.mode = "light";
console.log(theme.mode);
""", 2322),
         r"""
const theme: { mode: "dark" | "light" } = { mode: "dark" };
theme.mode = "light";
console.log(theme.mode);
""",
         "`satisfies` kept the inferred type `\"dark\"`, so assigning `\"light\"` fails. When a value is meant to change, annotate it with the wider type."),
        ("`satisfies` doesn't check runtime data",
         r"""
type Config = { retries: number };
const config = JSON.parse('{"retries":"3"}') satisfies Config;
console.log(config.retries + 1);
""",
         r"""
type Config = { retries: number };
const raw: unknown = JSON.parse('{"retries":"3"}');
const retries = typeof raw === "object" && raw !== null && "retries" in raw ? Number(raw.retries) : 0;
const config: Config = { retries };
console.log(config.retries + 1);
""",
         "`JSON.parse` returns `any`, which satisfies every type — nothing was checked. Validate data from outside at runtime."),
    ],
    later=[
        "**Week 15 — Variance.** What makes one type assignable to another.",
        "**Week 15 — Problem set.** Route tables, plugin registries and form schemas built with `satisfies`.",
        "**Week 19 — Lookup types.** Deriving types from `satisfies`-checked objects.",
    ],
)


_deepen(
    "ts_structural_typing",
    why=r"""
In Java, a class is a `Comparable` only if it says `implements Comparable`. In
TypeScript, a value fits a type if it has the right *shape* — the names of types
don't matter, only their members. That's how JavaScript is actually written
(objects are passed around by what they contain, not what they were declared
as), and it makes TypeScript flexible: any object with `x` and `y` numbers is a
`Point`, whether it came from a class, a literal or `JSON.parse`.

It also means types don't prevent some mix-ups that nominal systems would, and
that an object can carry more than its type lists. This chapter shows both sides.
""",
    examples=[
        ("Same shape, same type",
         r"""
type Point = { x: number; y: number };
type Vector = { x: number; y: number };
const p: Point = { x: 3, y: 4 };
const v: Vector = p;
const len = (vec: Vector) => Math.hypot(vec.x, vec.y);
console.log(len(v), len(p));
""", [""],
         "`Point` and `Vector` are different names for the same shape, so values move freely between them."),
        ("Ask only for what you use",
         r"""
function describeLength(x: { length: number }): string {
  return `length ${x.length}`;
}
const rope = { length: 7, unit: "m" };
console.log(describeLength("hello"), "|", describeLength([1, 2, 3]), "|", describeLength(rope));
""", [""],
         "Strings, arrays and plain objects all have a numeric `length`, so one function accepts them all. (Passing `{ length: 7, unit: \"m\" }` as a fresh literal would trip the excess-property check — through a variable, the extra field is fine.)"),
        ("Classes are structural too",
         r"""
class Celsius {
  readonly degrees: number;
  constructor(degrees: number) {
    this.degrees = degrees;
  }
}
const fromLiteral: Celsius = { degrees: 21 };
const fromClass: Celsius = new Celsius(19);
console.log(fromLiteral.degrees + fromClass.degrees, fromLiteral instanceof Celsius, fromClass instanceof Celsius);
""", [""],
         "A literal with the right members is assignable to the class type — but `instanceof` checks the constructor, so it tells them apart at runtime."),
    ],
    errors=[
        (2353, r"""
type Point = { x: number; y: number };
const p: Point = { x: 1, y: 2, z: 3 };
""", "Fresh object literals get an extra check: a property the type doesn't know is probably a typo."),
        (2741, r"""
type Point = { x: number; y: number };
const p: Point = { x: 1 };
""", "Structural typing still requires every member the type lists."),
    ],
    pitfalls=[
        ("Two meanings, one shape",
         r"""
type Celsius = { value: number };
type Fahrenheit = { value: number };
const toCelsius = (f: Fahrenheit): Celsius => ({ value: ((f.value - 32) * 5) / 9 });
const indoor: Celsius = { value: 21 };
console.log(toCelsius(indoor).value.toFixed(1));
""",
         r"""
type Celsius = { unit: "C"; value: number };
type Fahrenheit = { unit: "F"; value: number };
const toCelsius = (f: Fahrenheit): Celsius => ({ unit: "C", value: ((f.value - 32) * 5) / 9 });
const outdoor: Fahrenheit = { unit: "F", value: 70 };
console.log(toCelsius(outdoor).value.toFixed(1));
""",
         "Identical shapes are interchangeable, so a Celsius value was converted as if it were Fahrenheit. A literal `unit` tag (or a brand) makes them different types."),
        ("An empty interface accepts anything",
         r"""
interface Options {}
function configure(o: Options): string {
  return "configured with " + JSON.stringify(o);
}
console.log(configure(42));
""",
         (r"""
interface Options {
  verbose?: boolean;
}
function configure(o: Options): string {
  return "configured with " + JSON.stringify(o);
}
console.log(configure(42));
""", 2559),
         "`{}` has no required members, so even a number fits. Give the type real members (an all-optional type then rejects values with nothing in common)."),
        ("A class with private state isn't matched by shape",
         (r"""
class Account {
  #balance = 0;
  deposit(n: number): number {
    this.#balance += n;
    return this.#balance;
  }
}
function fund(a: Account): number {
  return a.deposit(10);
}
console.log(fund({ deposit: (n: number) => n }));
""", 2345),
         r"""
class Account {
  #balance = 0;
  deposit(n: number): number {
    this.#balance += n;
    return this.#balance;
  }
}
function fund(a: Account): number {
  return a.deposit(10);
}
console.log(fund(new Account()));
""",
         "Private members (`#` or `private`) make a class nominal: only real instances fit, so the invariant can't be bypassed with a look-alike object."),
    ],
    later=[
        "**Week 15 — Variance.** Structural rules applied to containers and functions.",
        "**Week 16 — Branded types.** Adding a nominal distinction on purpose.",
        "**Week 23 — Class design.** Private state as a deliberate nominal boundary.",
    ],
)


_deepen(
    "ts_branded_types",
    why=r"""
Structural typing makes every `string` interchangeable with every other `string`
— a user id, an email address, an order id, a SQL fragment. Most of the time
that's fine; for values that must never be mixed up, it's a bug waiting to
happen. A *brand* is a type-only marker, `string & { readonly [brand]: "UserId" }`,
that makes such values distinct to the compiler while leaving them plain strings
at runtime.

Brands pair with a validating constructor: the only way to get a `UserId` is a
function that checks the input. After that, a `UserId` in a signature means
"already validated" — see week 16's parse-don't-validate chapter.
""",
    examples=[
        ("Units that can't be mixed",
         r"""
declare const unit: unique symbol;
type Meters = number & { readonly [unit]: "m" };
type Feet = number & { readonly [unit]: "ft" };
const meters = (n: number) => n as Meters;
const feetToMeters = (f: Feet): Meters => meters(f * 0.3048);
const feet = (n: number) => n as Feet;
const total: Meters = meters(meters(100) + feetToMeters(feet(328)));
console.log(total.toFixed(1));
""", [""],
         "Adding meters to feet directly would be a compile error; the conversion function is the only bridge."),
        ("A validated non-empty string",
         r"""
declare const brand: unique symbol;
type Title = string & { readonly [brand]: "Title" };
function parseTitle(raw: string): Title | undefined {
  const t = raw.trim().replace(/\s+/g, " ");
  return t.length > 0 && t.length <= 40 ? (t as Title) : undefined;
}
const publish = (t: Title) => `published "${t}"`;
for (const raw of ["  Hello   world ", "   ", "x".repeat(50)]) {
  const t = parseTitle(raw);
  console.log(t === undefined ? "rejected" : publish(t));
}
""", [""],
         "`publish` can only be called with a checked, normalised title."),
        ("Brands as map keys",
         r"""
declare const brand: unique symbol;
type UserId = string & { readonly [brand]: "UserId" };
const toUserId = (s: string): UserId | undefined => (/^u\d+$/.test(s) ? (s as UserId) : undefined);
const names = new Map<UserId, string>();
for (const [raw, name] of [["u1", "ana"], ["x9", "bo"], ["u2", "cy"]] as const) {
  const id = toUserId(raw);
  if (id !== undefined) names.set(id, name);
}
console.log([...names].map(([id, n]) => `${id}=${n}`).join(" "));
""", [""],
         "A `Map<UserId, …>` can only be indexed with validated ids."),
    ],
    errors=[
        (2345, r"""
declare const brand: unique symbol;
type Email = string & { readonly [brand]: "Email" };
function send(to: Email): void {}
send("ana@example.com");
""", "A plain string isn't an `Email` until a parser says so."),
        (2322, r"""
declare const brand: unique symbol;
type Cents = number & { readonly [brand]: "Cents" };
declare const a: Cents;
declare const b: Cents;
const total: Cents = a + b;
""", "Arithmetic gives back a plain `number`. Re-brand through a function (`add(a, b): Cents`) so the rule stays in one place."),
    ],
    pitfalls=[
        ("Plain numbers mix units silently",
         r"""
const runMeters = 5000;
const climbFeet = 1200;
console.log(`total distance ${runMeters + climbFeet}`);
""",
         r"""
declare const unit: unique symbol;
type Meters = number & { readonly [unit]: "m" };
type Feet = number & { readonly [unit]: "ft" };
const runMeters = 5000 as Meters;
const climbFeet = 1200 as Feet;
const toMeters = (f: Feet) => (f * 0.3048) as Meters;
console.log(`total distance ${Math.round(runMeters + toMeters(climbFeet))}`);
""",
         "With plain numbers, adding feet to meters compiles and is wrong. With brands, the conversion has to be written — and so it's right."),
        ("A cast from JSON bypasses the parser",
         r"""
declare const brand: unique symbol;
type UserId = string & { readonly [brand]: "UserId" };
const ids = JSON.parse('["u1", "DROP TABLE", "u3"]') as UserId[];
console.log(ids.map((id) => `user ${id}`).join(", "));
""",
         r"""
declare const brand: unique symbol;
type UserId = string & { readonly [brand]: "UserId" };
const toUserId = (s: unknown): UserId | undefined => (typeof s === "string" && /^u\d+$/.test(s) ? (s as UserId) : undefined);
const raw: unknown = JSON.parse('["u1", "DROP TABLE", "u3"]');
const ids = (Array.isArray(raw) ? raw : []).map(toUserId).filter((id) => id !== undefined);
console.log(ids.map((id) => `user ${id}`).join(", "));
""",
         "A brand means \"validated\" only if every one came from the parser. Casting a whole array of input to `UserId[]` breaks the promise."),
        ("Comparing different brands",
         (r"""
declare const brand: unique symbol;
type UserId = string & { readonly [brand]: "UserId" };
type OrderId = string & { readonly [brand]: "OrderId" };
declare const u: UserId;
declare const o: OrderId;
console.log(u === o);
""", 2367),
         r"""
declare const brand: unique symbol;
type UserId = string & { readonly [brand]: "UserId" };
const a = "u1" as UserId;
const b = "u1" as UserId;
console.log(a === b);
""",
         "Two brands of the same base type have no overlap, so comparing them is flagged — it's nearly always a mix-up."),
    ],
    later=[
        "**Week 16 — Parse, don't validate.** Smart constructors that produce brands.",
        "**Week 16 — Problem set.** Money, percentages and ids as brands.",
        "**Week 27 — Capstone.** Branded `AccountId` and `Cents` in the final ledger.",
    ],
)


_deepen(
    "ts_immutability",
    why=r"""
A value that never changes is a value you never have to track. Shared mutable
state is behind a large share of bugs: a helper that sorts its argument in place,
a "copy" that still shares nested objects, a cached array someone else pushes
to. Immutability — creating new values instead of editing old ones — removes the
question entirely.

TypeScript supports it at the type level with `readonly` properties,
`ReadonlyArray<T>` and `Readonly<T>`, all erased at runtime; `Object.freeze`
adds a (shallow) runtime guarantee. This chapter is the update patterns that
make immutable code practical, and the places the guarantees are thinner than
they look.
""",
    examples=[
        ("Read-only inputs, new outputs",
         r"""
function topTwo(scores: readonly number[]): number[] {
  return scores.toSorted((a, b) => b - a).slice(0, 2);
}
const scores = [70, 95, 82];
console.log(topTwo(scores).join(","), "| original:", scores.join(","));
""", [""],
         "`readonly number[]` has no `sort` or `push`, so the function has to work on copies — and the caller's data is safe."),
        ("Updating a nested value",
         r"""
type State = { user: { name: string; prefs: { theme: string; lang: string } }; version: number };
const before: State = { user: { name: "ana", prefs: { theme: "dark", lang: "en" } }, version: 1 };
const after: State = { ...before, user: { ...before.user, prefs: { ...before.user.prefs, theme: "light" } }, version: 2 };
console.log(before.user.prefs.theme, after.user.prefs.theme, before.user === after.user);
""", [""],
         "Copy along the path to the change, share everything else. `before` is untouched."),
        ("`Object.freeze` at runtime, in strict code",
         r"""
"use strict";
const limits = Object.freeze({ maxUsers: 10 });
try {
  (limits as { maxUsers: number }).maxUsers = 99;
} catch (e) {
  console.log(e instanceof TypeError ? "refused: frozen" : "unexpected");
}
console.log(limits.maxUsers, Object.isFrozen(limits));
""", [""],
         "In strict code (every ES module, and this snippet), writing to a frozen object throws. In sloppy scripts it fails silently."),
    ],
    errors=[
        (2540, r"""
type Config = { readonly port: number };
const c: Config = { port: 80 };
c.port = 8080;
""", "`readonly` properties can be set when the object is created and never after."),
        (4104, r"""
const frozen: readonly number[] = [1, 2];
const editable: number[] = frozen;
""", "A readonly array can't be handed to something that expects to mutate it."),
    ],
    pitfalls=[
        ("A copied array still shares its objects",
         r"""
const todos = [{ title: "write", done: false }];
const next = [...todos];
next[0]!.done = true;
console.log("original done:", todos[0]!.done);
""",
         r"""
const todos = [{ title: "write", done: false }];
const next = todos.map((t, i) => (i === 0 ? { ...t, done: true } : t));
console.log("original done:", todos[0]!.done);
""",
         "Spreading copies the array, not the todos. Replace the object you change."),
        ("Keeping a reference to a caller's array",
         r"""
class Report {
  readonly rows: readonly string[];
  constructor(rows: readonly string[]) {
    this.rows = rows;
  }
}
const rows = ["a", "b"];
const report = new Report(rows);
rows.push("added later");
console.log(report.rows.length);
""",
         r"""
class Report {
  readonly rows: readonly string[];
  constructor(rows: readonly string[]) {
    this.rows = [...rows];
  }
}
const rows = ["a", "b"];
const report = new Report(rows);
rows.push("added later");
console.log(report.rows.length);
""",
         "`readonly` stops *this* code from mutating the array; the caller still holds a mutable reference. Copy what you keep."),
        ("`Object.freeze` is shallow",
         r"""
const config = Object.freeze({ db: { host: "localhost" } });
config.db.host = "prod-db";
console.log(config.db.host);
""",
         r"""
function deepFreeze<T extends object>(o: T): T {
  for (const v of Object.values(o)) if (typeof v === "object" && v !== null) deepFreeze(v);
  return Object.freeze(o);
}
const config = deepFreeze({ db: { host: "localhost" } });
try {
  config.db.host = "prod-db";
} catch {
  // a frozen property can't be written (this throws in strict code)
}
console.log(config.db.host);
""",
         "Freezing the outer object left `db` writable. Freeze recursively when the whole structure must stay fixed."),
    ],
    later=[
        "**Week 16 — Problem set.** An immutable cart with undo, and a persistent stack.",
        "**Week 20 — Mapped types.** Writing `DeepReadonly<T>` yourself.",
    ],
)


_deepen(
    "ts_compose",
    why=r"""
Large types are best built from small ones. A `Timestamped` shape, an
`Identified` shape and a `Named` shape can be combined into whatever an entity
needs — with `interface … extends` or an intersection `A & B` — instead of being
written out again in every type. The same idea at runtime is building objects
from parts with spread, rather than through deep class hierarchies.

Composition keeps each piece small and reusable. Its pitfalls come from merging:
which value wins when two parts share a key, and what happens to nested objects
when you spread.
""",
    examples=[
        ("Types built from parts",
         r"""
type Identified = { id: number };
type Named = { name: string };
type Timestamped = { createdAt: string; updatedAt: string };
type Product = Identified & Named & Timestamped & { price: number };
const p: Product = { id: 1, name: "pen", price: 2, createdAt: "2026-09-01", updatedAt: "2026-09-26" };
console.log(Object.keys(p).length, `${p.name} #${p.id}`);
""", [""],
         "Each part is reusable; `Product` is their combination plus its own field."),
        ("Objects built from parts",
         r"""
const withTimestamps = <T extends object>(o: T, now: string) => ({ ...o, createdAt: now, updatedAt: now });
const withId = <T extends object>(o: T, id: number) => ({ id, ...o });
const user = withId(withTimestamps({ name: "ana" }, "2026-09-26"), 7);
console.log(JSON.stringify(user));
""", [""],
         "Small functions each add one aspect; the result's type is inferred as the intersection of the pieces."),
        ("`extends` for a named family",
         r"""
interface Shape {
  name: string;
  area(): number;
}
interface Solid extends Shape {
  volume(): number;
}
const cube: Solid = { name: "cube", area: () => 6 * 4, volume: () => 8 };
const shapes: Shape[] = [cube, { name: "square", area: () => 4 }];
console.log(shapes.map((s) => `${s.name}:${s.area()}`).join(" "), cube.volume());
""", [""],
         "An extended interface is usable anywhere its base is."),
    ],
    errors=[
        (2322, r"""
type A = { id: number };
type B = { id: string };
const x: A & B = { id: 1 };
""", "Intersecting conflicting property types gives `never` for that property, so no value fits. An `interface extends` would report the conflict where it's declared."),
        (2312, r"""
type Pet = { name: string } | { id: number };
interface Owner extends Pet {}
""", "An interface can only extend an object type with statically known members, not a union."),
    ],
    pitfalls=[
        ("Spread order decides who wins",
         r"""
const defaults = { theme: "light", fontSize: 14 };
const user = { theme: "dark" };
console.log(JSON.stringify({ ...user, ...defaults }));
""",
         r"""
const defaults = { theme: "light", fontSize: 14 };
const user = { theme: "dark" };
console.log(JSON.stringify({ ...defaults, ...user }));
""",
         "Later properties overwrite earlier ones: defaults first, overrides last."),
        ("A shallow merge loses nested defaults",
         r"""
const defaults = { db: { host: "localhost", port: 5432 }, debug: false };
const user = { db: { host: "db.local" } };
const merged = { ...defaults, ...user };
console.log(JSON.stringify(merged));
""",
         r"""
const defaults = { db: { host: "localhost", port: 5432 }, debug: false };
const user = { db: { host: "db.local" } };
const merged = { ...defaults, ...user, db: { ...defaults.db, ...user.db } };
console.log(JSON.stringify(merged));
""",
         "Spreading replaced the whole `db` object, so `port` vanished. Merge nested objects explicitly."),
        ("`Object.assign` changes its first argument",
         r"""
const defaults = { retries: 3 };
const a = Object.assign(defaults, { retries: 5 });
const b = Object.assign(defaults, {});
console.log(a.retries, b.retries, defaults.retries);
""",
         r"""
const defaults = { retries: 3 };
const a = Object.assign({}, defaults, { retries: 5 });
const b = Object.assign({}, defaults, {});
console.log(a.retries, b.retries, defaults.retries);
""",
         "The first call wrote into `defaults` itself, so every later merge started from the changed values. Pass a fresh `{}` first."),
    ],
    later=[
        "**Week 17 — Utility types.** `Pick`, `Omit`, `Partial` — composing by selecting.",
        "**Week 23 — Class design.** Composition over inheritance for classes.",
    ],
)


_deepen(
    "ts_utility_types",
    why=r"""
Most related types are transformations of one model: a draft is a task without
its id, a patch is any subset of its fields, a summary picks two of them, a
lookup is a record of them by key. TypeScript ships these transformations as
utility types — `Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`,
`ReturnType`, `Parameters` and more — so each related type is *derived* from the
model and changes with it.

This chapter is about using them well; weeks 20 and 21 show how they're built.
""",
    examples=[
        ("A patch, applied",
         r"""
type Task = { id: number; title: string; done: boolean; priority: "low" | "high" };
type TaskPatch = Partial<Omit<Task, "id">>;
function update(task: Task, patch: TaskPatch): Task {
  return { ...task, ...patch };
}
const t: Task = { id: 1, title: "write", done: false, priority: "low" };
console.log(JSON.stringify(update(t, { done: true, priority: "high" })));
""", [""],
         "`TaskPatch` is \"any fields except `id`\" — derived, so adding a field to `Task` makes it patchable automatically."),
        ("Totals for every category",
         r"""
type Category = "food" | "rent" | "fun";
const totals: Record<Category, number> = { food: 0, rent: 0, fun: 0 };
for (const [c, amount] of [["food", 12], ["fun", 30], ["food", 8]] as const) totals[c] += amount;
console.log(JSON.stringify(totals));
""", [""],
         "`Record<Category, number>` requires every category up front, so no lookup can find nothing."),
        ("Types read from a function",
         r"""
function createUser(name: string, age: number) {
  return { name, age, createdAt: "2026-09-26" };
}
type User = ReturnType<typeof createUser>;
type UserArgs = Parameters<typeof createUser>;
const args: UserArgs = ["ana", 31];
const u: User = createUser(...args);
console.log(Object.keys(u).join(","));
""", [""],
         "The factory stays the single source of truth for what a user is and what creating one takes."),
    ],
    errors=[
        (2344, r"""
type Task = { id: number; title: string };
type Summary = Pick<Task, "id" | "titel">;
""", "`Pick` only accepts keys the type has — a typo is caught. (`Omit` accepts any key, so the same typo there would silently do nothing.)"),
        (2741, r"""
type Options = { width?: number; height?: number };
const full: Required<Options> = { width: 100 };
""", "`Required` removes the `?`, so every property must be present."),
    ],
    pitfalls=[
        ("`Partial` where the data is really required",
         r"""
type User = { name: string; email: string };
function greet(u: Partial<User>): string {
  return "hi " + u.name;
}
console.log(greet({}));
""",
         r"""
type User = { name: string; email: string };
function greet(u: Partial<User>): string {
  return "hi " + (u.name ?? "there");
}
console.log(greet({}));
""",
         "`Partial` makes every field possibly absent. Either handle absence (as here) or take the full type so callers must supply it."),
        ("A `Record<string, …>` read that finds nothing",
         r"""
const prices: Record<string, number> = { pen: 2, cup: 5 };
const basket = ["pen", "ink"];
console.log(basket.reduce((sum, item) => sum + (prices[item] as number), 0));
""",
         r"""
const prices: Record<string, number> = { pen: 2, cup: 5 };
const basket = ["pen", "ink"];
console.log(basket.reduce((sum, item) => sum + (prices[item] ?? 0), 0));
""",
         "A `Record<string, …>` claims every key exists; `ink` doesn't, and the total became `NaN`. Handle the missing case (and see `noUncheckedIndexedAccess`)."),
        ("`Required` at the type level isn't a default at runtime",
         r"""
type Options = { retries?: number };
const fromUser = JSON.parse("{}") as Required<Options>;
console.log("retries: " + fromUser.retries);
""",
         r"""
type Options = { retries?: number };
const fromUser = JSON.parse("{}") as Options;
const resolved: Required<Options> = { retries: fromUser.retries ?? 3 };
console.log("retries: " + resolved.retries);
""",
         "A type can't fill in a missing value. Produce a `Required<T>` by actually supplying defaults."),
    ],
    later=[
        "**Week 17 — Runtime validation.** Types derived from a schema instead of a model.",
        "**Week 20 — Mapped types.** How `Partial`, `Readonly` and `Pick` are written.",
        "**Week 21 — Conditional types.** How `ReturnType` and `Parameters` are written.",
    ],
)
