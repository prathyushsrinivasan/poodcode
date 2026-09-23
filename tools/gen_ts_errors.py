# -*- coding: utf-8 -*-
"""The TypeScript error glossary — src/data/ts_errors.json.

Every judged TypeScript program is type-checked before it runs, so the first
thing a learner meets when something is wrong is a line like

    main.ts(4,7): error TS2322: Type 'string' is not assignable to type 'number'.

The compiler's wording is precise but assumes you already know the vocabulary.
Each entry here explains one code: what it means in plain English, the usual
cause, a minimal program that produces it, the same program fixed, and the
Mastery week that teaches the idea. The app links compile errors to these
entries (TsErrorLinks) and lists them all at /ts-errors.

NOTHING HERE IS TAKEN ON TRUST. Before writing the JSON this script
type-checks, with the judge's exact options (tools/ts_typecheck.mjs):

  * every `bad` program — it must report the entry's code, and
  * every `good` program — it must report nothing at all.

The TypeScript roadmap records why this matters: the code depends on the
syntactic form, not just the rule (TS2353 vs TS2561, TS18048 vs TS2532…), and
guessing gets it wrong often enough that the course's own verifier caught four
wrong codes in one batch.

Usage: python tools/gen_ts_errors.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "src", "data", "ts_errors.json")


def E(code, title, meaning, cause, bad, good, week, preset="strict"):
    return {
        "code": code,
        "title": title,
        "meaning": meaning,
        "cause": cause,
        "bad": bad.strip("\n") + "\n",
        "good": good.strip("\n") + "\n",
        "week": week,
        "preset": preset,
    }


ERRORS = [
    # ---- assignability ------------------------------------------------------
    E(2322, "Type 'A' is not assignable to type 'B'",
      "You put a value somewhere whose declared type doesn't allow it.",
      "The most common error there is. Read it right to left: the thing on the right of the message is what the slot accepts; the thing on the left is what you tried to put in. Either the value is wrong, or the declared type is too narrow.",
      '''
let count = 0;
count = "zero";
''',
      '''
let count = 0;
count = 0;
''', 1),
    E(2345, "Argument of type 'A' is not assignable to parameter of type 'B'",
      "A function was called with an argument its parameter doesn't accept.",
      "The same rule as TS2322, applied at a call. Check the argument's real type (hover it) against the parameter's declared type.",
      '''
function double(n: number): number {
  return n * 2;
}
double("4");
''',
      '''
function double(n: number): number {
  return n * 2;
}
double(Number("4"));
''', 5),
    E(2741, "Property 'x' is missing in type 'A' but required in type 'B'",
      "An object is missing a property its type requires.",
      "Assigning an object literal to a declared type checks that every required property is present. Add the property, or mark it optional with `?` in the type if it really can be absent.",
      '''
type User = { name: string; age: number };
const u: User = { name: "Ada" };
''',
      '''
type User = { name: string; age: number };
const u: User = { name: "Ada", age: 36 };
''', 8),
    E(2739, "Type 'A' is missing the following properties from type 'B': x, y",
      "Several required properties are missing at once.",
      "TS2741's plural form. The list tells you exactly which properties to add.",
      '''
type Point = { x: number; y: number; z: number };
const p: Point = { x: 1 };
''',
      '''
type Point = { x: number; y: number; z: number };
const p: Point = { x: 1, y: 2, z: 3 };
''', 8),
    E(2353, "Object literal may only specify known properties",
      "An object literal has a property its target type doesn't declare.",
      "This excess-property check applies only to fresh object literals, where an extra key is almost always a typo. Remove it, or add it to the type.",
      '''
type Point = { x: number; y: number };
const p: Point = { x: 1, y: 2, label: "origin" };
''',
      '''
type Point = { x: number; y: number; label?: string };
const p: Point = { x: 1, y: 2, label: "origin" };
''', 8),
    E(2561, "Object literal may only specify known properties, but 'x' does not exist. Did you mean 'y'?",
      "An excess property whose name is close to a real one — almost certainly a typo.",
      "The same check as TS2353, but the compiler found a property with a similar name and suggests it. You'd guess TS2353; the near-miss spelling is what changes the code.",
      '''
type Options = { width: number };
const o: Options = { widht: 8 };
''',
      '''
type Options = { width: number };
const o: Options = { width: 8 };
''', 15),
    E(2783, "'x' is specified more than once, so this usage will be overwritten",
      "A property written before a spread that always sets it too.",
      "In `{ x: 1, ...o }`, if `o` always has `x`, your `x: 1` is dead. Put it after the spread to override, or drop it.",
      '''
const base = { x: 5, y: 6 };
const moved = { x: 1, ...base };
''',
      '''
const base = { x: 5, y: 6 };
const moved = { ...base, x: 1 };
''', 8),
    # ---- names --------------------------------------------------------------
    E(2304, "Cannot find name 'x'",
      "You used a name that isn't declared anywhere the compiler can see.",
      "A typo, a missing declaration, or a variable declared in a different scope (inside another block or function).",
      '''
console.log(totl);
''',
      '''
const total = 3;
console.log(total);
''', 1),
    E(2552, "Cannot find name 'x'. Did you mean 'y'?",
      "An undeclared name that looks like a declared one.",
      "The compiler found a close match in scope — it is almost always a typo.",
      '''
const total = 3;
console.log(totl);
''',
      '''
const total = 3;
console.log(total);
''', 1),
    E(2339, "Property 'x' does not exist on type 'A'",
      "You read a property the type doesn't have.",
      "Either a typo, or the value's type is wider than you think — e.g. a union where only one member has the property. Narrow first (`if (\"x\" in v)`, a tag check) or fix the name.",
      '''
type Circle = { kind: "circle"; radius: number };
type Square = { kind: "square"; side: number };
function size(s: Circle | Square): number {
  return s.radius;
}
''',
      '''
type Circle = { kind: "circle"; radius: number };
type Square = { kind: "square"; side: number };
function size(s: Circle | Square): number {
  return s.kind === "circle" ? s.radius : s.side;
}
''', 12),
    E(2551, "Property 'x' does not exist on type 'A'. Did you mean 'y'?",
      "A misspelled property that is close to a real one.",
      "TS2339 with a suggestion. Take it.",
      '''
const word = "hello";
console.log(word.lenght);
''',
      '''
const word = "hello";
console.log(word.length);
''', 4),
    E(2584, "Cannot find name 'document'. Do you need to change your target library?",
      "You used a browser API in a program that runs in Node.",
      "The judge type-checks against the ES library only — no DOM. `document`, `window` and `alert` don't exist; read stdin and write with `console.log` instead.",
      '''
document.write("hi");
''',
      '''
console.log("hi");
''', 1),
    E(2580, "Cannot find name 'require'",
      "`require` is CommonJS, and the judge's TypeScript declares only ES module imports.",
      "Use `import * as fs from \"fs\";` at the top of the file instead of `require(\"fs\")`. (Depending on configuration the code is TS2580 or TS2591; the fix is the same.)",
      '''
const fs = require("fs");
''',
      '''
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8");
console.log(input.length);
''', 1),
    # ---- declarations -------------------------------------------------------
    E(2588, "Cannot assign to 'x' because it is a constant",
      "You reassigned a `const`.",
      "`const` bindings can't be reassigned. Use `let` if the value really changes — or build a new value instead of changing the old one.",
      '''
const total = 0;
total = 5;
''',
      '''
let total = 0;
total = 5;
''', 1),
    E(2451, "Cannot redeclare block-scoped variable 'x'",
      "The same name is declared twice in one scope.",
      "Rename one, or reuse the existing variable instead of declaring it again.",
      '''
let x = 1;
let x = 2;
''',
      '''
let x = 1;
x = 2;
''', 1),
    E(2448, "Block-scoped variable 'x' used before its declaration",
      "You used a `let`/`const` on a line above where it's declared.",
      "`let` and `const` exist only from their declaration onward (the temporal dead zone). Move the declaration up.",
      '''
console.log(limit);
const limit = 10;
''',
      '''
const limit = 10;
console.log(limit);
''', 5),
    E(2454, "Variable 'x' is used before being assigned",
      "A variable is read on a path where nothing has assigned it yet.",
      "Declared with `let x: T;` and assigned only in some branches. Initialise it, or assign it on every path.",
      '''
let label: string;
if (Math.random() > 0.5) label = "heads";
console.log(label);
''',
      '''
let label = "tails";
if (Math.random() > 0.5) label = "heads";
console.log(label);
''', 2),
    E(2393, "Duplicate function implementation",
      "Two function bodies share a name.",
      "TypeScript allows several overload *signatures* but only one implementation. Rename one function, or merge them.",
      '''
function area(w: number): number { return w * w; }
function area(w: number, h: number): number { return w * h; }
''',
      '''
function area(w: number, h: number = w): number { return w * h; }
''', 5),
    E(2300, "Duplicate identifier 'x'",
      "Something is declared twice where only one declaration is allowed.",
      "Type aliases can't be reopened (interfaces can — that's declaration merging). Use one alias, or combine two with `&`.",
      '''
type Point = { x: number };
type Point = { y: number };
''',
      '''
type Point = { x: number; y: number };
''', 8),
    # ---- functions ----------------------------------------------------------
    E(2554, "Expected N arguments, but got M",
      "A call passes the wrong number of arguments.",
      "Count the parameters. If an argument should be optional, mark the parameter with `?` or give it a default.",
      '''
function greet(name: string, greeting: string): string {
  return greeting + ", " + name;
}
greet("Ada");
''',
      '''
function greet(name: string, greeting = "Hello"): string {
  return greeting + ", " + name;
}
greet("Ada");
''', 5),
    E(1016, "A required parameter cannot follow an optional parameter",
      "An optional parameter comes before a required one.",
      "Callers can only leave off trailing arguments, so optional and defaulted parameters must come last. Reorder them, or take an options object.",
      '''
function pad(width?: number, text: string): string {
  return text.padStart(width ?? 8);
}
''',
      '''
function pad(text: string, width?: number): string {
  return text.padStart(width ?? 8);
}
''', 5),
    E(7006, "Parameter 'x' implicitly has an 'any' type",
      "A parameter has no type and nothing lets the compiler infer one.",
      "Under `strict` a parameter's type can't silently fall back to `any`. Annotate it. (Callback parameters are exempt when the call site supplies the type.)",
      '''
function double(n) {
  return n * 2;
}
''',
      '''
function double(n: number): number {
  return n * 2;
}
''', 5),
    E(2366, "Function lacks ending return statement and return type does not include 'undefined'",
      "Some path through a function falls off the end without returning.",
      "You declared a return type, but one branch doesn't return. Add the missing `return` — or, for a switch over a union, handle every member.",
      '''
function sign(n: number): string {
  if (n > 0) return "positive";
  if (n < 0) return "negative";
}
''',
      '''
function sign(n: number): string {
  if (n > 0) return "positive";
  if (n < 0) return "negative";
  return "zero";
}
''', 12),
    E(2355, "A function whose declared type is neither 'undefined', 'void', nor 'any' must return a value",
      "A function with a declared return type never returns anything.",
      "Usually a forgotten `return` — often inside a braced arrow function, where the value of the last expression is not returned automatically.",
      '''
function total(xs: number[]): number {
  xs.reduce((a, b) => a + b, 0);
}
''',
      '''
function total(xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0);
}
''', 5),
    E(2349, "This expression is not callable",
      "You called something that isn't a function.",
      "Often a property that's a value, not a method (`s.length()`), or a union where not every member is callable.",
      '''
const word = "hi";
console.log(word.length());
''',
      '''
const word = "hi";
console.log(word.length);
''', 4),
    E(2769, "No overload matches this call",
      "None of a function's overload signatures accepts these arguments.",
      "The message lists each overload and why it failed; read the last one first — it is usually the one you meant. Common with built-ins that have several signatures, like `replace`.",
      '''
const dashed = "a-b".replace("-", 5);
''',
      '''
const dashed = "a-b".replace("-", "5");
console.log(dashed);
''', 4),
    # ---- null / undefined ---------------------------------------------------
    E(18048, "'x' is possibly 'undefined'",
      "A named value might be `undefined`, and you used it as if it weren't.",
      "Optional parameters, `find`, `Map.get` and optional properties all produce `T | undefined`. Check first (`if (x !== undefined)`), supply a default with `??`, or use `?.`.",
      '''
function shout(text?: string): string {
  return text.toUpperCase();
}
''',
      '''
function shout(text?: string): string {
  return (text ?? "").toUpperCase();
}
''', 14),
    E(18047, "'x' is possibly 'null'",
      "A named value might be `null`, and you used it as if it weren't.",
      "`String.prototype.match` returns `null` when nothing matches — the classic source. Check for `null` before using it.",
      '''
const m = "abc".match(/z/);
console.log(m.length);
''',
      '''
const m = "abc".match(/z/);
console.log(m === null ? 0 : m.length);
''', 11),
    E(2532, "Object is possibly 'undefined'",
      "An expression — not a plain name — might be `undefined`.",
      "The same problem as TS18048, but on something with no name to quote, like an element access `xs[0]` under `noUncheckedIndexedAccess`. Guard it or give a default.",
      '''
const xs: number[] = [3, 1, 2];
console.log(xs[0].toFixed(1));
''',
      '''
const xs: number[] = [3, 1, 2];
console.log((xs[0] ?? 0).toFixed(1));
''', 14, "strict+indexed"),
    E(2531, "Object is possibly 'null'",
      "An expression — not a plain name — might be `null`.",
      "TS18047 for an unnamed expression: `\"abc\".match(/z/)[0]` reads from something that may be `null`.",
      '''
console.log("abc".match(/z/)[0]);
''',
      '''
console.log("abc".match(/z/)?.[0] ?? "none");
''', 11),
    E(18046, "'x' is of type 'unknown'",
      "You used a value of type `unknown` before narrowing it.",
      "`unknown` blocks every operation until you prove what the value is. Narrow with `typeof`, `instanceof`, `in`, or a type predicate — this is exactly what `unknown` is for.",
      '''
const data: unknown = JSON.parse("{\\"id\\": 1}");
console.log(data.id);
''',
      '''
const data: unknown = JSON.parse("{\\"id\\": 1}");
if (typeof data === "object" && data !== null && "id" in data) {
  console.log(data.id);
}
''', 11),
    # ---- operators ----------------------------------------------------------
    E(2362, "The left-hand side of an arithmetic operation must be of type 'any', 'number', 'bigint' or an enum type",
      "You did arithmetic (`-`, `*`, `/`, `%`) with a non-number on the left.",
      "JavaScript would coerce a string silently; TypeScript refuses. Convert with `Number(...)` first.",
      '''
const input = "10";
console.log(input - 1);
''',
      '''
const input = "10";
console.log(Number(input) - 1);
''', 2),
    E(2365, "Operator 'op' cannot be applied to types 'A' and 'B'",
      "An operator was used between types it doesn't support.",
      "Often mixing `bigint` with `number`, or comparing values that can't be ordered. Convert one side so both match.",
      '''
const big = 10n;
console.log(big + 1);
''',
      '''
const big = 10n;
console.log(big + 1n);
''', 3),
    E(2367, "This comparison appears to be unintentional because the types 'A' and 'B' have no overlap",
      "You compared two values that can never be equal.",
      "Usually a misspelled literal, or a value whose type was narrowed earlier so it can't be the thing you're checking for.",
      '''
type Status = "idle" | "loading" | "done";
function isFinished(s: Status): boolean {
  return s === "finished";
}
''',
      '''
type Status = "idle" | "loading" | "done";
function isFinished(s: Status): boolean {
  return s === "done";
}
''', 10),
    # ---- readonly / classes -------------------------------------------------
    E(2540, "Cannot assign to 'x' because it is a read-only property",
      "You wrote to a `readonly` property (or a getter with no setter).",
      "The type says this can't change after construction. Build a new object with the new value, or remove `readonly` if mutation is really intended.",
      '''
type Point = { readonly x: number; readonly y: number };
const p: Point = { x: 1, y: 2 };
p.x = 5;
''',
      '''
type Point = { readonly x: number; readonly y: number };
const p: Point = { x: 1, y: 2 };
const moved: Point = { ...p, x: 5 };
console.log(moved.x);
''', 16),
    E(2341, "Property 'x' is private and only accessible within class 'C'",
      "Code outside a class touched a `private` member.",
      "Go through a public method or getter instead. Note that `private` is compile-time only; `#x` is enforced at runtime too.",
      '''
class Counter {
  private count = 0;
}
const c = new Counter();
console.log(c.count);
''',
      '''
class Counter {
  private count = 0;
  get value(): number { return this.count; }
}
const c = new Counter();
console.log(c.value);
''', 23),
    E(18013, "Property '#x' is not accessible outside class 'C' because it has a private identifier",
      "Code outside a class touched a `#private` field.",
      "`#` fields are truly private, enforced by JavaScript itself. Expose what callers need through a method or getter.",
      '''
class Account {
  #balance = 0;
}
console.log(new Account().#balance);
''',
      '''
class Account {
  #balance = 0;
  get balance(): number { return this.#balance; }
}
console.log(new Account().balance);
''', 23),
    E(2564, "Property 'x' has no initializer and is not definitely assigned in the constructor",
      "A class field isn't guaranteed a value when the object is created.",
      "Initialise it where it's declared, assign it in the constructor, or make it optional (`x?: T`).",
      '''
class User {
  name: string;
}
''',
      '''
class User {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
}
''', 23),
    E(17009, "'super' must be called before accessing 'this' in the constructor of a derived class",
      "A subclass constructor used `this` before calling `super(...)`.",
      "The object doesn't exist until the parent constructor has run. Call `super(...)` first.",
      '''
class Animal {}
class Dog extends Animal {
  name: string;
  constructor(name: string) {
    this.name = name;
    super();
  }
}
''',
      '''
class Animal {}
class Dog extends Animal {
  name: string;
  constructor(name: string) {
    super();
    this.name = name;
  }
}
''', 23),
    E(2511, "Cannot create an instance of an abstract class",
      "You used `new` on an `abstract` class.",
      "Abstract classes exist to be extended. Instantiate a concrete subclass.",
      '''
abstract class Shape {
  abstract area(): number;
}
const s = new Shape();
''',
      '''
abstract class Shape {
  abstract area(): number;
}
class Square extends Shape {
  side: number;
  constructor(side: number) {
    super();
    this.side = side;
  }
  area(): number { return this.side ** 2; }
}
const s = new Square(2);
console.log(s.area());
''', 23),
    # ---- generics & type-level ----------------------------------------------
    E(2344, "Type 'A' does not satisfy the constraint 'B'",
      "A type argument doesn't meet its type parameter's constraint.",
      "Common with `Pick<T, K>` when `K` isn't a key of `T` — which is exactly the typo protection `Pick` gives you (and `Omit`, whose keys are unconstrained, doesn't).",
      '''
type User = { name: string; age: number };
type Preview = Pick<User, "nmae">;
''',
      '''
type User = { name: string; age: number };
type Preview = Pick<User, "name">;
''', 17),
    E(2536, "Type 'K' cannot be used to index type 'T'",
      "You indexed a type with a key the compiler can't prove belongs to it.",
      "Constrain the key: `K extends keyof T` lets `obj[key]` be typed `T[K]`.",
      '''
function get<T, K extends string>(obj: T, key: K) {
  return obj[key];
}
''',
      '''
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
''', 19),
    E(7053, "Element implicitly has an 'any' type because expression of type 'string' can't be used to index type 'T'",
      "You indexed an object with an arbitrary string, and its type has no index signature.",
      "Either narrow the key to `keyof typeof obj`, or give the object a type that allows any string key, like `Record<string, number>`.",
      '''
const prices = { apple: 3, pear: 4 };
function price(fruit: string): number {
  return prices[fruit];
}
''',
      '''
const prices: Record<string, number> = { apple: 3, pear: 4 };
function price(fruit: string): number {
  return prices[fruit] ?? 0;
}
''', 19),
    E(2352, "Conversion of type 'A' to type 'B' may be a mistake",
      "An `as` assertion between types that don't overlap enough.",
      "`as` never converts anything; it only makes a claim. For a real conversion call `Number(...)`, `String(...)` or a parser. (`as unknown as T` forces it — and makes the danger obvious.)",
      '''
const n = "5" as number;
''',
      '''
const n = Number("5");
console.log(n);
''', 15),
    E(1360, "Type 'A' does not satisfy the expected type 'B'",
      "A `satisfies` check failed.",
      "The expression before `satisfies` doesn't match the type after it. Note that for an object literal the compiler usually points at the offending property instead, as TS2322 — TS1360 is what you get when the whole value is wrong.",
      '''
const port = "8080" satisfies number;
''',
      '''
const port = 8080 satisfies number;
console.log(port);
''', 15),
    E(2578, "Unused '@ts-expect-error' directive",
      "A `// @ts-expect-error` comment sits above a line that no longer has an error.",
      "That's the directive doing its job: whatever it was suppressing got fixed. Delete the comment.",
      '''
// @ts-expect-error
const n: number = 5;
''',
      '''
const n: number = 5;
console.log(n);
''', 14),
    E(2493, "Tuple type '[A, B]' of length '2' has no element at index '2'",
      "You indexed past the end of a tuple.",
      "Tuples have a fixed length, so the compiler knows index 2 doesn't exist on a pair.",
      '''
const pair: [string, number] = ["a", 1];
console.log(pair[2]);
''',
      '''
const pair: [string, number] = ["a", 1];
console.log(pair[1]);
''', 7),
    E(2488, "Type 'A' must have a '[Symbol.iterator]()' method that returns an iterator",
      "You used `for…of` or spread on something that isn't iterable.",
      "Plain objects aren't iterable. Iterate `Object.entries(obj)` (or keys/values), or give your class a `[Symbol.iterator]` method.",
      '''
const scores = { ada: 3, bob: 5 };
for (const s of scores) console.log(s);
''',
      '''
const scores = { ada: 3, bob: 5 };
for (const [name, s] of Object.entries(scores)) console.log(name, s);
''', 24),
    E(1308, "'await' expressions are only allowed within async functions and at the top levels of modules",
      "You used `await` inside a function that isn't `async`.",
      "Mark the enclosing function `async` (its return type becomes a `Promise`).",
      '''
function load(): number {
  const v = await Promise.resolve(1);
  return v;
}
''',
      '''
async function load(): Promise<number> {
  const v = await Promise.resolve(1);
  return v;
}
load().then(console.log);
''', 25),
]


def typecheck(items):
    r = subprocess.run(
        ["node", os.path.join(HERE, "ts_typecheck.mjs")],
        input=json.dumps(items), capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        sys.exit(f"ts_typecheck.mjs failed:\n{r.stderr}")
    return {o["id"]: o["diagnostics"] for o in json.loads(r.stdout)}


def main():
    codes = [e["code"] for e in ERRORS]
    assert len(set(codes)) == len(codes), "duplicate error code in the glossary"
    items = []
    for e in ERRORS:
        items.append({"id": f"bad-{e['code']}", "src": e["bad"], "preset": e["preset"]})
        items.append({"id": f"good-{e['code']}", "src": e["good"], "preset": e["preset"]})
    diags = typecheck(items)

    problems = []
    for e in ERRORS:
        bad = diags[f"bad-{e['code']}"]
        got = sorted({d["code"] for d in bad})
        # TS2580 and TS2591 are the same "no require" error under different
        # configurations; either proves the entry.
        accept = {2580, 2591} if e["code"] == 2580 else {e["code"]}
        if not accept & set(got):
            problems.append(f"TS{e['code']}: the bad program reports {got}, not TS{e['code']}"
                            + "".join(f"\n      TS{d['code']} {d['msg']}" for d in bad[:3]))
        good = diags[f"good-{e['code']}"]
        if good:
            problems.append(f"TS{e['code']}: the fixed program still reports "
                            + "; ".join(f"TS{d['code']} {d['msg']}" for d in good[:3]))
    if problems:
        print("\n".join(problems))
        sys.exit(f"{len(problems)} glossary entr{'y is' if len(problems) == 1 else 'ies are'} wrong — nothing written")

    ERRORS.sort(key=lambda e: e["code"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ERRORS, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {len(ERRORS)} verified TypeScript errors to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
