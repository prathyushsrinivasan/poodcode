# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The original Month 3 TypeScript chapters, brought up to the lesson template
# (TS_MASTERY_ROADMAP.md F-12, X-02/X-03) with `_deepen`:
#
#   ts_maps_sets  ts_unions  ts_aliases  ts_enums  ts_narrowing
#   ts_type_predicates  ts_nullish  ts_discriminated_unions
#
# `enum` can't run under type stripping, so ts_enums' runnable examples use
# `as const` objects and enums appear only in compiler-checked snippets.
# Every output and compiler message is computed (python tools/gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_deepen(
    "ts_maps_sets",
    why=r"""
"How many times have I seen this word?", "have I visited this cell?", "which
user owns this id?" — questions of that shape come up in almost every problem,
and scanning an array to answer them makes a program quadratic. A `Map` answers
key → value lookups and a `Set` answers membership, both in constant time on
average, and unlike plain objects they accept any key type and never collide with
inherited names like `toString`.

TypeScript types both precisely (`Map<string, number>`, `Set<Point>`) and is
honest that `map.get(k)` might find nothing. This chapter is the everyday toolkit:
counting, deduplicating, grouping, and knowing when a `Map` beats an object.
""",
    examples=[
        ("The three most common words",
         r"""
const text = "the cat sat on the mat the cat ran";
const counts = new Map<string, number>();
for (const w of text.split(" ")) counts.set(w, (counts.get(w) ?? 0) + 1);
const top = [...counts].sort(([a, x], [b, y]) => y - x || a.localeCompare(b)).slice(0, 3);
console.log(top.map(([w, n]) => `${w}=${n}`).join(" "));
""", [""],
         "Count with `get(k) ?? 0`, then turn the map into entries to sort them — by count, then alphabetically for a stable answer."),
        ("Deduplicate, keeping first-seen order",
         r"""
const visits = ["home", "about", "home", "blog", "about", "home"];
const unique = [...new Set(visits)];
const repeated = visits.filter((v, i) => visits.indexOf(v) !== i);
console.log(unique.join(" > "));
console.log("repeated:", [...new Set(repeated)].join(","));
""", [""],
         "A `Set` keeps the first occurrence of each value, in insertion order."),
        ("Objects as keys",
         r"""
type Task = { title: string };
const a: Task = { title: "write" };
const b: Task = { title: "write" };
const minutes = new Map<Task, number>();
minutes.set(a, 30);
minutes.set(b, 45);
console.log(minutes.size, minutes.get(a), minutes.get(b));
""", [""],
         "Object keys are compared by identity: two equal-looking tasks are two entries. That's exactly right for attaching data to specific objects."),
    ],
    errors=[
        (2345, r"""
const labels = new Map<string, string>();
labels.set(1, "one");
""", "The map's key type is `string`; the compiler checks every `set` and `get`."),
        (18048, r"""
const stock = new Map([["pen", 3]]);
const left = stock.get("pen");
console.log(left - 1);
""", "`get` returns `number | undefined` — the key might be absent. Decide what absence means (`?? 0`) before doing arithmetic."),
    ],
    pitfalls=[
        ("Bracket assignment on a `Map`",
         (r"""
const ages = new Map<string, number>();
ages["ana"] = 31;
console.log(ages.size);
""", 7052),
         r"""
const ages = new Map<string, number>();
ages.set("ana", 31);
console.log(ages.size);
""",
         "`ages[\"ana\"] = …` would set an ordinary property, invisible to `get` and `size`. TypeScript refuses it; use `set`."),
        ("Equal-looking objects are different set members",
         r"""
const seen = new Set<number[]>();
seen.add([1, 2]);
console.log(seen.has([1, 2]) ? "seen" : "new");
""",
         r"""
const seen = new Set<string>();
seen.add([1, 2].join(","));
console.log(seen.has([1, 2].join(",")) ? "seen" : "new");
""",
         "Arrays and objects compare by identity. Key sets by a canonical string when you mean \"equal contents\"."),
        ("Spreading a `Map` gives entries",
         r"""
const ages = new Map([["ana", 31], ["bo", 25]]);
console.log([...ages].join(","));
""",
         r"""
const ages = new Map([["ana", 31], ["bo", 25]]);
console.log([...ages.keys()].join(","));
""",
         "Iterating a map yields `[key, value]` pairs. Ask for `keys()` or `values()` explicitly."),
    ],
    later=[
        "**Week 9 — Set algebra.** `union`, `intersection`, `difference` and friends.",
        "**Week 18 — Generics.** An `LruCache<K, V>` built on a `Map`.",
        "**DSA curriculum — hashing.** The problems these structures turn from O(n²) into O(n).",
    ],
)


_deepen(
    "ts_unions",
    why=r"""
Real values are often "one of several things": an id that's a number or a string,
a result that's a value or an error message, a mode that's `"light"` or `"dark"`.
A union type says exactly that, and TypeScript then insists that code handles
every possibility — you can only use what all members share until you've checked
which one you have.

Literal unions are the everyday case: a fixed set of strings or numbers, checked
at every use, erased at runtime. They replace magic strings, most enums, and a
lot of defensive `if` statements.
""",
    examples=[
        ("Accepting one or many",
         r"""
function tags(input: string | string[]): string[] {
  return Array.isArray(input) ? input : input.split(",").map((t) => t.trim());
}
console.log(tags("a, b").join("|"));
console.log(tags(["x", "y"]).join("|"));
""", [""],
         "One function serves both call styles; `Array.isArray` tells the compiler which member it has."),
        ("A literal union of commands",
         r"""
type Command = "start" | "stop" | "pause";
function run(cmd: Command): string {
  switch (cmd) {
    case "start":
      return "running";
    case "stop":
      return "stopped";
    case "pause":
      return "paused";
  }
}
console.log((["start", "pause", "stop"] as const).map(run).join(" -> "));
""", [""],
         "Every member is handled, so the function needs no `default` — and adding a command makes the compiler point at this switch."),
        ("A result or a reason",
         r"""
function parseAge(text: string): number | "invalid" {
  const n = Number(text);
  return Number.isInteger(n) && n >= 0 ? n : "invalid";
}
for (const t of ["31", "-2", "x"]) {
  const r = parseAge(t);
  console.log(r === "invalid" ? `${t}: rejected` : `${t}: next year ${r + 1}`);
}
""", [""],
         "After `r === \"invalid\"` is ruled out, `r` is a `number`, so `r + 1` is arithmetic."),
    ],
    errors=[
        (2339, r"""
function show(x: string | number): string {
  return x.toFixed(2);
}
""", "`toFixed` exists only on numbers. Narrow first: `typeof x === \"number\" ? x.toFixed(2) : x`."),
        (2322, r"""
type Status = "idle" | "busy";
let status: Status = "idle";
status = "loading";
""", "A literal union accepts only its members — which catches typos and stale values."),
    ],
    pitfalls=[
        ("A sentinel of the same type",
         r"""
const words = ["alpha", "beta"];
const i = words.indexOf("gamma");
console.log("found: " + words[i]);
""",
         r"""
const words = ["alpha", "beta"];
const found = words.find((w) => w === "gamma");
console.log(found === undefined ? "not found" : "found: " + found);
""",
         "`-1` is a number like any valid index, so nothing forces the check. A `T | undefined` result makes \"not found\" part of the type."),
        ("Treating a mixed array as numbers",
         r"""
const values: (number | string)[] = [10, "20", 5];
const total = (values as number[]).reduce((a, b) => a + b, 0);
console.log(total);
""",
         r"""
const values: (number | string)[] = [10, "20", 5];
const total = values.reduce<number>((a, b) => a + Number(b), 0);
console.log(total);
""",
         "The cast hid the strings, and `+` concatenated: `\"10205\"`. Handle each member of the union."),
        ("A widened variable doesn't fit a literal union",
         (r"""
type Theme = "light" | "dark";
function apply(t: Theme): string {
  return "theme " + t;
}
let choice = "dark";
console.log(apply(choice));
""", 2345),
         r"""
type Theme = "light" | "dark";
function apply(t: Theme): string {
  return "theme " + t;
}
let choice: Theme = "dark";
console.log(apply(choice));
""",
         "A `let` widens to `string`. Annotate it with the union (or use `const`)."),
    ],
    later=[
        "**Week 11 — Narrowing.** Every way to tell union members apart.",
        "**Week 12 — Discriminated unions.** Unions of objects with a tag.",
        "**Week 21 — Conditional types.** Transforming each member of a union.",
    ],
)


_deepen(
    "ts_aliases",
    why=r"""
Types get long: `{ id: number; name: string; tags: string[] }` written out at
every parameter is noise, and a union of five literals repeated in three files
will drift. A type alias (`type`) or an `interface` gives a shape a name, so it's
written once, read as a concept (`User`, `Point`, `Handler`), and changed in one
place.

`type` can name *any* type — unions, tuples, functions; `interface` names object
shapes and can be extended and merged. Both are erased at runtime, and both are
structural: a name documents intent but doesn't make two identical shapes
incompatible.
""",
    examples=[
        ("Names that document a domain",
         r"""
type Cents = number;
type Sku = string;
type LineItem = { sku: Sku; qty: number; unit: Cents };
const total = (items: readonly LineItem[]): Cents => items.reduce((s, i) => s + i.qty * i.unit, 0);
console.log(total([{ sku: "PEN-1", qty: 3, unit: 150 }, { sku: "CUP-2", qty: 1, unit: 400 }]));
""", [""],
         "`Cents` is still just `number`, but signatures now say what the numbers mean."),
        ("Extending an interface, intersecting a type",
         r"""
interface Named {
  name: string;
}
interface Employee extends Named {
  team: string;
}
type Timestamped = { createdAt: string };
type Record_ = Employee & Timestamped;
const r: Record_ = { name: "ana", team: "web", createdAt: "2026-09-01" };
console.log(Object.keys(r).join(","));
""", [""],
         "`extends` builds interfaces from interfaces; `&` combines any object types. Both give a type with all the members."),
        ("An alias for a callback shape",
         r"""
type Listener = (event: string, payload: number) => void;
const log: string[] = [];
const listeners: Listener[] = [(e, p) => log.push(`${e}:${p}`), (e) => log.push(e.toUpperCase())];
for (const l of listeners) l("save", 3);
console.log(log.join(" "));
""", [""],
         "Naming the callback type keeps the array's element type readable, and each arrow's parameters are inferred from it."),
    ],
    errors=[
        (2300, r"""
type Size = "s" | "m";
type Size = "l";
""", "A type alias can't be reopened. (Interfaces can — declaration merging — which is one of the real differences.)"),
        (2430, r"""
interface Base {
  id: number;
}
interface Doc extends Base {
  id: string;
}
""", "An extending interface can narrow a member's type but not replace it with an incompatible one."),
    ],
    pitfalls=[
        ("Two aliases of `string` are interchangeable",
         r"""
type UserId = string;
type OrderId = string;
const ordersByUser = new Map<UserId, string[]>([["u1", ["o9"]]]);
function ordersOf(id: UserId): string {
  return (ordersByUser.get(id) ?? []).join(",") || "no orders";
}
const order: OrderId = "o9";
console.log(ordersOf(order));
""",
         (r"""
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };
declare function ordersOf(id: UserId): string;
declare const order: OrderId;
ordersOf(order);
""", 2345),
         "An alias is only a name: an `OrderId` was accepted as a `UserId`, and the lookup silently failed. Branded types (week 16) make the names mean something to the compiler."),
        ("An optional property set to `undefined` still overrides",
         r"""
interface Options {
  retries?: number;
}
const defaults: Required<Options> = { retries: 3 };
const fromUser: Options = { retries: undefined };
console.log({ ...defaults, ...fromUser }.retries);
""",
         r"""
interface Options {
  retries?: number;
}
const defaults: Required<Options> = { retries: 3 };
const fromUser: Options = { retries: undefined };
console.log(fromUser.retries ?? defaults.retries);
""",
         "Spreading copies the key even when its value is `undefined`. Resolve each option with `??`, or turn on `exactOptionalPropertyTypes`."),
        ("`readonly` on a property is shallow",
         r"""
interface Post {
  readonly tags: string[];
}
const p: Post = { tags: ["a"] };
p.tags.push("b");
console.log(p.tags.join(","));
""",
         (r"""
interface Post {
  readonly tags: readonly string[];
}
const p: Post = { tags: ["a"] };
p.tags.push("b");
console.log(p.tags.join(","));
""", 2339),
         "`readonly tags` stops `p.tags = …`, not changes to the array. Make the array type readonly too."),
    ],
    later=[
        "**Week 8 — Interfaces vs types.** Merging, extending and when each wins.",
        "**Week 15 — Structural typing.** Why names don't separate identical shapes.",
        "**Week 16 — Branded types.** Names the compiler enforces.",
    ],
)


_deepen(
    "ts_enums",
    why=r"""
Programs are full of small fixed sets: directions, statuses, log levels,
permissions. TypeScript's `enum` was designed for them, but it's one of the few
features that *generates code* — which is why this app's runner (Node's type
stripping) refuses to run it, and why `--erasableSyntaxOnly` flags it.

The modern replacement is a literal union, or an `as const` object when you also
want a runtime list of the values. This chapter shows both patterns, and enough
about `enum` itself to read the code you'll meet in older projects.
""",
    examples=[
        ("An `as const` object as an enum",
         r"""
const Level = { Debug: 10, Info: 20, Warn: 30, Error: 40 } as const;
type Level = (typeof Level)[keyof typeof Level];
function shouldLog(level: Level, threshold: Level): boolean {
  return level >= threshold;
}
console.log(shouldLog(Level.Warn, Level.Info), shouldLog(Level.Debug, Level.Info));
console.log(Object.entries(Level).map(([name, value]) => `${name}=${value}`).join(" "));
""", [""],
         "`Level.Warn` reads like an enum member; `Object.entries` lists every level at runtime; the type `Level` is `10 | 20 | 30 | 40`."),
        ("Parsing input into a member",
         r"""
const STATUSES = ["todo", "doing", "done"] as const;
type Status = (typeof STATUSES)[number];
const parseStatus = (s: string): Status | undefined => STATUSES.find((x) => x === s);
for (const s of ["doing", "DONE", "archived"]) {
  const st = parseStatus(s.toLowerCase());
  console.log(st === undefined ? `unknown status ${s}` : `status ${st} (#${STATUSES.indexOf(st) + 1})`);
}
""", [""],
         "An array of values plus a derived union gives both a runtime check (`find`) and a precise type."),
        ("Flags you can combine",
         r"""
const Perm = { Read: 1, Write: 2, Exec: 4 } as const;
const describe = (mask: number) =>
  (Object.keys(Perm) as (keyof typeof Perm)[]).filter((p) => (mask & Perm[p]) !== 0).join("+") || "none";
console.log(describe(Perm.Read | Perm.Write), describe(Perm.Exec), describe(0));
""", [""],
         "Powers of two combine with `|` and test with `&` — the one place numeric enum values matter."),
    ],
    errors=[
        (2322, r"""
enum Color {
  Red = "red",
  Green = "green",
}
const c: Color = "red";
""", "A string enum is *nominal*: the string `\"red\"` isn't a `Color`, only `Color.Red` is. (Checked here by the compiler; the runner can't execute `enum` at all.)"),
        (2345, r"""
const Direction = { North: "N", South: "S" } as const;
type Direction = (typeof Direction)[keyof typeof Direction];
function turn(d: Direction): string {
  return d;
}
turn("north");
""", "Only the object's values are members of the derived type."),
    ],
    pitfalls=[
        ("Keys where values were meant",
         r"""
const Color = { Red: "#f00", Green: "#0f0" } as const;
console.log(Object.keys(Color).join(" "));
""",
         r"""
const Color = { Red: "#f00", Green: "#0f0" } as const;
console.log(Object.values(Color).join(" "));
""",
         "An `as const` object has names *and* values; `Object.keys` gives the names."),
        ("Casting input instead of checking it",
         r"""
const SIZES = ["S", "M", "L"] as const;
type Size = (typeof SIZES)[number];
const size = "XXL" as Size;
console.log("size " + size + " ok");
""",
         r"""
const SIZES = ["S", "M", "L"] as const;
type Size = (typeof SIZES)[number];
const requested: string = "XXL";
const size = SIZES.find((s) => s === requested);
console.log(size === undefined ? "unknown size" : "size " + size + " ok");
""",
         "`as Size` is a promise, not a check. Validate against the runtime list."),
        ("Looking a value up by its name",
         r"""
const Code = { NotFound: 404, Teapot: 418 } as const;
const input: string = "418";
console.log((Code as Record<string, number>)[input] ?? "no such code");
""",
         r"""
const Code = { NotFound: 404, Teapot: 418 } as const;
const input: string = "418";
const name = Object.entries(Code).find(([, v]) => String(v) === input)?.[0];
console.log(name ?? "no such code");
""",
         "Indexing looks up by *name*. A numeric `enum` has a built-in reverse mapping; a const object needs an explicit search by value."),
    ],
    later=[
        "**Week 10 — Literal inference.** `as const` and deriving unions from values.",
        "**Week 14 — Erasable syntax.** Exactly why `enum` can't be stripped.",
        "**Week 19 — Lookup types.** `(typeof X)[keyof typeof X]` explained.",
    ],
)


_deepen(
    "ts_narrowing",
    why=r"""
A union type says "this could be several things"; before you can use the value,
you have to find out which. TypeScript follows your checks — `typeof`,
`instanceof`, `in`, `Array.isArray`, comparisons with `null` or a literal — and
*narrows* the variable's type in each branch. No casts, no annotations: the
checks you'd write anyway become proofs the compiler understands.

Knowing which checks narrow, and where narrowing is lost, is the difference
between code that type-checks cleanly and code full of `as`.
""",
    examples=[
        ("Normalising input of several shapes",
         r"""
function toList(x: string | number | string[]): string[] {
  if (Array.isArray(x)) return x;
  if (typeof x === "number") return [String(x)];
  return x.split(",");
}
console.log(toList("a,b").length, toList(7)[0], toList(["z"]).join(""));
""", [""],
         "After each `return`, the remaining type shrinks: by the last line `x` can only be a `string`."),
        ("`instanceof` for classes",
         r"""
function when(value: Date | string): string {
  return value instanceof Date ? value.toISOString().slice(0, 10) : value;
}
console.log(when(new Date(Date.UTC(2026, 8, 26))), when("tomorrow"));
""", [""],
         "`instanceof` works for anything with a runtime constructor — classes, `Date`, `Error`, `Map`."),
        ("Equality with a literal",
         r"""
type Reply = "yes" | "no" | number;
function explain(r: Reply): string {
  if (r === "yes" || r === "no") return `answered ${r}`;
  return `scored ${r.toFixed(1)}`;
}
console.log(explain("yes"), "|", explain(7));
""", [""],
         "Comparing with literals removes those members; what's left is `number`."),
    ],
    errors=[
        (2339, r"""
type Fish = { swim: () => string };
type Bird = { fly: () => string };
function move(pet: Fish | Bird): string {
  return pet.swim();
}
""", "Not every member has `swim`. Narrow with `\"swim\" in pet` first."),
        (18047, r"""
const found = "abc".match(/d/);
console.log(found.index);
""", "`match` returns `null` when nothing matches. Check for `null` before reading from it."),
    ],
    pitfalls=[
        ("Truthiness narrows away zero",
         r"""
function show(count: number | undefined): string {
  return count ? `${count} items` : "no data";
}
console.log(show(0), "|", show(undefined));
""",
         r"""
function show(count: number | undefined): string {
  return count !== undefined ? `${count} items` : "no data";
}
console.log(show(0), "|", show(undefined));
""",
         "`if (count)` rules out `undefined` — and `0`. Compare with `undefined` when zero is valid."),
        ("Narrowing lost in a callback",
         (r"""
let name: string | undefined = "ana";
const shout = () => name.toUpperCase();
name = undefined;
console.log(shout());
""", 18048),
         r"""
let name: string | undefined = "ana";
const fixed = name;
const shout = () => fixed.toUpperCase();
name = undefined;
console.log(shout());
""",
         "A `let` that is reassigned later might have changed by the time the callback runs, so the narrowing isn't trusted there. Capture it in a `const`."),
        ("`instanceof` on data that never met the class",
         r"""
class Point {
  x = 0;
  y = 0;
}
const p: unknown = JSON.parse('{"x":1,"y":2}');
console.log(p instanceof Point ? `point (${p.x}, ${p.y})` : "not a point");
""",
         r"""
class Point {
  x = 0;
  y = 0;
}
const p: unknown = JSON.parse('{"x":1,"y":2}');
const isPointLike = typeof p === "object" && p !== null && "x" in p && "y" in p && typeof p.x === "number" && typeof p.y === "number";
console.log(isPointLike ? `point (${p.x}, ${p.y})` : "not a point");
""",
         "`instanceof` checks how an object was *constructed*. Parsed JSON is a plain object, so it's never an instance of your class even when its shape matches. Check the shape instead."),
    ],
    later=[
        "**Week 11 — Type predicates and control flow.** Your own narrowing functions.",
        "**Week 12 — Discriminated unions.** Narrowing on a tag field.",
        "**Week 25 — Errors.** Narrowing `unknown` from a `catch`.",
    ],
)


_deepen(
    "ts_type_predicates",
    why=r"""
Built-in narrowing (`typeof`, `instanceof`, `in`) covers primitives and classes.
Everything else — "is this `unknown` value a valid `Person`?", "is this string one
of my commands?" — needs a check you write yourself, and a way to tell the
compiler what the check proved. A type predicate (`x is Person`) does exactly
that: the function returns a boolean, and in the `true` branch the argument is
narrowed.

It's the bridge between runtime validation and static types — and because the
compiler trusts it, it's also where a bug can make the types lie. Keep
predicates small and test them.
""",
    examples=[
        ("A predicate that makes `filter` precise",
         r"""
const isNonEmpty = (s: string | null | undefined): s is string => s !== null && s !== undefined && s.trim() !== "";
const raw = ["ana", "", null, "bo", undefined, "  "];
const names = raw.filter(isNonEmpty);
console.log(names.map((n) => n.toUpperCase()).join(","));
""", [""],
         "`filter` with a predicate returns `string[]`, so `toUpperCase` needs no checks."),
        ("Validating `unknown` data",
         r"""
type Point = { x: number; y: number };
function isPoint(v: unknown): v is Point {
  return typeof v === "object" && v !== null && "x" in v && "y" in v && typeof v.x === "number" && typeof v.y === "number";
}
for (const text of ['{"x":1,"y":2}', '{"x":"1","y":2}', "[1,2]"]) {
  const v: unknown = JSON.parse(text);
  console.log(isPoint(v) ? `distance ${Math.hypot(v.x, v.y).toFixed(2)}` : "not a point");
}
""", [""],
         "Inside the `true` branch `v` is a `Point`; the check itself uses `in` and `typeof` narrowing step by step."),
        ("An assertion function",
         r"""
function assertDefined<T>(value: T | undefined, what: string): asserts value is T {
  if (value === undefined) throw new Error(`${what} is missing`);
}
const env = new Map([["PORT", "8080"]]);
for (const key of ["PORT", "HOST"]) {
  try {
    const v = env.get(key);
    assertDefined(v, key);
    console.log(`${key}=${v.padStart(6)}`);
  } catch (e) {
    console.log(e instanceof Error ? e.message : String(e));
  }
}
""", [""],
         "After `assertDefined` returns, `v` is a `string` — the function either proves it or throws."),
    ],
    errors=[
        (2677, r"""
function isNumber(x: string): x is number {
  return !Number.isNaN(Number(x));
}
""", "A predicate can only narrow to something the parameter could be. A `string` can never be a `number` — take `unknown` or `string | number`."),
        (2775, r"""
const assertPositive = (n: number): asserts n => {
  if (n <= 0) throw new Error("not positive");
};
assertPositive(3);
""", "Assertion functions must be called through a name with an explicit type: a `function` declaration, or a `const` with a type annotation."),
    ],
    pitfalls=[
        ("A predicate that lies",
         r"""
function isCount(v: unknown): v is number {
  return v !== undefined;
}
const values: unknown[] = [3, "4", 5];
let total = 0;
for (const v of values) if (isCount(v)) total += v;
console.log(total);
""",
         r"""
function isCount(v: unknown): v is number {
  return typeof v === "number" && Number.isInteger(v);
}
const values: unknown[] = [3, "4", 5];
let total = 0;
for (const v of values) if (isCount(v)) total += v;
console.log(total);
""",
         "The compiler trusted `v is number`, so `\"4\"` was added as if it were a number: `\"345\"`. A predicate must check everything it promises."),
        ("A `boolean` return narrows nothing",
         (r"""
type Admin = { name: string; level: number };
function isAdmin(u: { name: string }): boolean {
  return "level" in u;
}
const u = { name: "ana", level: 3 } as { name: string };
if (isAdmin(u)) console.log(u.level);
""", 2339),
         r"""
type Admin = { name: string; level: number };
function isAdmin(u: { name: string }): u is Admin {
  return "level" in u;
}
const u = { name: "ana", level: 3 } as { name: string };
if (isAdmin(u)) console.log(u.level);
""",
         "Returning `boolean` tells the compiler nothing about the argument. Write the return type as `u is Admin`."),
        ("An assertion that doesn't throw",
         r"""
function assertString(v: unknown): asserts v is string {
  if (typeof v !== "string") console.log("warning: not a string");
}
const input: unknown = 42;
assertString(input);
console.log("length " + input.length);
""",
         r"""
function assertString(v: unknown): asserts v is string {
  if (typeof v !== "string") throw new TypeError("not a string");
}
const input: unknown = 42;
try {
  assertString(input);
  console.log("length " + input.length);
} catch (e) {
  console.log(e instanceof Error ? e.message : String(e));
}
""",
         "An assertion function *must* throw when the check fails; otherwise the code after it runs with a type that's false."),
    ],
    later=[
        "**Week 11 — Control-flow analysis.** Inferred predicates (TS 5.5) and aliased conditions.",
        "**Week 17 — Runtime validation.** Schemas: predicates that also produce the type.",
    ],
)


_deepen(
    "ts_nullish",
    why=r"""
Missing data is everywhere: an optional field, a lookup that found nothing, a
config value nobody set. JavaScript represents it two ways, `undefined` and
`null`, and for decades the resulting crashes ("cannot read properties of
undefined") were the most common runtime error. With `strictNullChecks` (part of
`strict`), TypeScript keeps absence in the type — `string | undefined` — so the
compiler shows you every place it has to be handled.

The operators `?.`, `??` and `??=` make handling it concise. The discipline is
using them where absence is expected, and not reaching for `!` to silence the
compiler where it isn't.
""",
    examples=[
        ("A lazily filled cache with `??=`",
         r"""
const cache = new Map<number, string>();
let computed = 0;
function label(n: number): string {
  let v = cache.get(n);
  v ??= (computed++, `#${n.toString(2)}`);
  cache.set(n, v);
  return v;
}
console.log([5, 3, 5, 5].map(label).join(" "), `computed ${computed}`);
""", [""],
         "`v ??= expr` evaluates `expr` only when `v` is `null` or `undefined`."),
        ("An optional callback",
         r"""
function save(data: string, onDone?: (bytes: number) => void): void {
  onDone?.(data.length);
}
save("hello", (n) => console.log(`saved ${n} bytes`));
save("quiet");
console.log("done");
""", [""],
         "`onDone?.(…)` calls the function only if it was passed."),
        ("Defaults for nested, partial config",
         r"""
type Config = { server?: { port?: number; host?: string }; debug?: boolean };
function resolve(c: Config) {
  return { port: c.server?.port ?? 3000, host: c.server?.host ?? "localhost", debug: c.debug ?? false };
}
console.log(JSON.stringify(resolve({})));
console.log(JSON.stringify(resolve({ server: { port: 0 }, debug: true })));
""", [""],
         "`?.` walks past missing levels; `??` fills in defaults — and keeps a real `0`."),
    ],
    errors=[
        (2322, r"""
let nickname: string = null;
""", "Under `strictNullChecks`, `null` isn't a `string`. Write `string | null` if the value may be absent."),
        (2532, r"""
const users = [{ name: "ana" }];
console.log(users.find((u) => u.name === "bo").name);
""", "`find` may return `undefined`. Handle it: `?.name`, `?? default`, or an explicit check."),
    ],
    pitfalls=[
        ("`?.` guards one step, not the whole chain",
         (r"""
const order: { customer?: { address?: { city: string } } } = { customer: {} };
console.log(order.customer?.address.city);
""", 18048),
         r"""
const order: { customer?: { address?: { city: string } } } = { customer: {} };
console.log(order.customer?.address?.city ?? "no city");
""",
         "`customer?.address` stops only if `customer` is missing; `.city` is then read from an address that may not exist — at runtime, a crash. Each optional link needs its own `?.`."),
        ("`!` silences a real problem",
         r"""
const labels = new Map([["a", "Alpha"]]);
try {
  console.log(labels.get("b")!.toUpperCase());
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
const labels = new Map([["a", "Alpha"]]);
console.log((labels.get("b") ?? "unknown").toUpperCase());
""",
         "The non-null assertion told the compiler \"trust me\" — and it was wrong. Prefer a default or a check."),
        ("Mixing `??` with `||`",
         (r"""
const a: number | null = null;
const b = 0;
console.log(a ?? b || 5);
""", 5076),
         r"""
const a: number | null = null;
const b = 0;
console.log((a ?? b) || 5);
""",
         "JavaScript forbids mixing `??` with `||`/`&&` without parentheses, because the intended grouping is ambiguous. Say which you mean."),
    ],
    later=[
        "**Week 11 — Narrowing.** Checks that remove `null` and `undefined` from a type.",
        "**Week 14 — `noUncheckedIndexedAccess`.** Absence on every index read.",
        "**Week 25 — `Result`.** When \"missing\" should carry a reason.",
    ],
)


_deepen(
    "ts_discriminated_unions",
    why=r"""
Data often comes in variants that carry different fields: a shape is a circle
*with a radius* or a rectangle *with width and height*; a request is loading, or
succeeded *with data*, or failed *with an error*. Modelling that as one object
with every field optional lets impossible combinations exist and forces a check
at every use.

A discriminated union gives each variant its own type with a shared literal tag
(`kind`, `type`, `status`). Checking the tag narrows to exactly one variant, and
a `never` check makes the compiler list every place that must handle a new
variant. It's the most useful modelling pattern in TypeScript.
""",
    examples=[
        ("Processing results",
         r"""
type Result = { ok: true; value: number } | { ok: false; error: string };
const results: Result[] = [{ ok: true, value: 4 }, { ok: false, error: "timeout" }, { ok: true, value: 6 }];
let sum = 0;
for (const r of results) {
  if (r.ok) sum += r.value;
  else console.log("skipped: " + r.error);
}
console.log("sum " + sum);
""", [""],
         "The boolean tag `ok` narrows each branch to one member, so `value` and `error` are only read where they exist."),
        ("A state machine",
         r"""
type Light = { state: "red"; waited: number } | { state: "green" } | { state: "amber" };
function next(l: Light): Light {
  switch (l.state) {
    case "red":
      return l.waited >= 2 ? { state: "green" } : { state: "red", waited: l.waited + 1 };
    case "green":
      return { state: "amber" };
    case "amber":
      return { state: "red", waited: 0 };
  }
}
let light: Light = { state: "red", waited: 0 };
const seen: string[] = [];
for (let i = 0; i < 6; i++) {
  light = next(light);
  seen.push(light.state);
}
console.log(seen.join(" "));
""", [""],
         "Only the red state carries a counter. The transition function handles every state, and each returned object must match one member exactly."),
        ("Replaying events",
         r"""
type Event = { type: "deposit"; amount: number } | { type: "withdraw"; amount: number } | { type: "fee"; reason: string };
function apply(balance: number, e: Event): number {
  switch (e.type) {
    case "deposit":
      return balance + e.amount;
    case "withdraw":
      return balance - e.amount;
    case "fee":
      return balance - 1;
    default: {
      const unhandled: never = e;
      return unhandled;
    }
  }
}
const events: Event[] = [{ type: "deposit", amount: 100 }, { type: "fee", reason: "monthly" }, { type: "withdraw", amount: 30 }];
console.log(events.reduce(apply, 0));
""", [""],
         "The `never` check in `default` compiles only while every event type has a case."),
    ],
    errors=[
        (2339, r"""
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };
function area(s: Shape): number {
  return s.r * s.r * 3;
}
""", "Only circles have `r`. Check `s.kind` first."),
        (2322, r"""
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number } | { kind: "tri"; b: number; h: number };
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return 3 * s.r * s.r;
    case "square":
      return s.side * s.side;
    default: {
      const unhandled: never = s;
      return unhandled;
    }
  }
}
""", "The triangle reaches `default`, where a `tri` can't be assigned to `never`. The compiler names the missing case."),
    ],
    pitfalls=[
        ("A tag typed as `string`",
         (r"""
type Msg = { kind: string; text?: string; code?: number };
function show(m: Msg): string {
  if (m.kind === "text") return m.text.toUpperCase();
  return String(m.code);
}
console.log(show({ kind: "text", text: "hi" }));
""", 18048),
         r"""
type Msg = { kind: "text"; text: string } | { kind: "code"; code: number };
function show(m: Msg): string {
  if (m.kind === "text") return m.text.toUpperCase();
  return String(m.code);
}
console.log(show({ kind: "text", text: "hi" }));
""",
         "With `kind: string` and optional fields, checking the tag narrows nothing. Literal tags on separate members make the check meaningful."),
        ("A `default` that absorbs new variants",
         r"""
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number } | { kind: "tri"; b: number; h: number };
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return 3 * s.r * s.r;
    case "square":
      return s.side * s.side;
    default:
      return 0;
  }
}
console.log(area({ kind: "tri", b: 4, h: 3 }));
""",
         r"""
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number } | { kind: "tri"; b: number; h: number };
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return 3 * s.r * s.r;
    case "square":
      return s.side * s.side;
    case "tri":
      return (s.b * s.h) / 2;
  }
}
console.log(area({ kind: "tri", b: 4, h: 3 }));
""",
         "The triangle was added to the union, and the catch-all `default` quietly returned 0. Without a `default`, a missing case is a compile error."),
        ("Optional fields allow impossible states",
         r"""
type Fetch = { loading: boolean; data?: string; error?: string };
const state: Fetch = { loading: true, error: "timeout" };
console.log(state.loading ? "loading…" : "done", state.error ? `(error: ${state.error})` : "");
""",
         (r"""
type Fetch = { status: "loading" } | { status: "done"; data: string } | { status: "failed"; error: string };
const state: Fetch = { status: "loading", error: "timeout" };
console.log(state.status);
""", 2353),
         "With optional fields, \"loading and also failed\" is a valid value. With a union, it can't even be written down."),
    ],
    later=[
        "**Week 12 — Top and bottom types.** `never`, and why the exhaustiveness check works.",
        "**Week 25 — `Result`.** A discriminated union for success and failure.",
        "**Week 27 — Event sourcing.** Rebuilding state from a union of events.",
    ],
)
