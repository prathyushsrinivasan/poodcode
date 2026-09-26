# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The original Month 5 TypeScript chapters, brought up to the lesson template
# (TS_MASTERY_ROADMAP.md F-12, X-02/X-03) with `_deepen`:
#
#   ts_generics  ts_generic_constraints  ts_keyof_indexed  ts_mapped_types
#   ts_conditional_types  ts_template_literal_types  ts_type_level
#
# These are chapters about types, so every example is a program whose runtime
# half uses them. Every output and message is computed (gen_ts_outputs.py).
# ---------------------------------------------------------------------------

_deepen(
    "ts_generics",
    why=r"""
Without generics, a reusable function has two bad options: accept `any` and lose
all type information, or be written again for every element type. A type
parameter (`<T>`) is a third option: the function works for any type, and the
compiler still knows *which* one at each call — `first(["a", "b"])` returns a
`string`, `first([1, 2])` a `number`.

Generics are how collections, `Promise<T>`, `Map<K, V>` and every utility
library are typed. The skill this chapter builds is using a type parameter to
connect things — an input to an output, one argument to another — rather than
decorating a function with `<T>` for its own sake.
""",
    examples=[
        ("A generic stack",
         r"""
class Stack<T> {
  readonly #items: T[] = [];
  push(item: T): this {
    this.#items.push(item);
    return this;
  }
  pop(): T | undefined {
    return this.#items.pop();
  }
  get size(): number {
    return this.#items.length;
  }
}
const words = new Stack<string>().push("a").push("b");
const nums = new Stack<number>().push(1).push(2).push(3);
console.log(words.pop()?.toUpperCase(), (nums.pop() ?? 0) * 10, words.size + nums.size);
""", [""],
         "One class, two element types. `words.pop()` is a `string | undefined`, so `toUpperCase` type-checks after `?.`."),
        ("Transforming every value of a record",
         r"""
function mapValues<T, U>(obj: Record<string, T>, f: (value: T, key: string) => U): Record<string, U> {
  return Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, f(v, k)]));
}
const prices = { pen: 1.5, cup: 4 };
const labels = mapValues(prices, (p, name) => `${name}: $${p.toFixed(2)}`);
console.log(Object.values(labels).join(" | "));
""", [""],
         "`T` is inferred from the object (`number`) and `U` from the callback's return (`string`) — two parameters, each connecting an input to an output."),
        ("A generic result wrapper",
         r"""
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function attempt<T>(f: () => T): Result<T> {
  try {
    return { ok: true, value: f() };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}
const parsed = attempt(() => JSON.parse('{"n": 2}') as { n: number });
const broken = attempt(() => JSON.parse("{"));
console.log(parsed.ok ? parsed.value.n * 21 : parsed.error, "|", broken.ok ? "?" : "error caught");
""", [""],
         "`attempt` works for any function, and `Result<T>` carries the function's own return type."),
    ],
    errors=[
        (2322, r"""
function firstOr<T>(xs: T[], fallback: T): T {
  return xs[0] ?? "none";
}
""", "The body must produce a `T` for *any* `T` the caller chooses, and `\"none\"` is only a string. Return `fallback`."),
        (2558, r"""
function pair<T>(a: T, b: T): [T, T] {
  return [a, b];
}
const p = pair<string, number>("a", 1);
""", "The function declares one type parameter; the call supplies two."),
    ],
    pitfalls=[
        ("`any` instead of a type parameter",
         r"""
function first(xs: any[]): any {
  return xs[0];
}
try {
  console.log(first(["7"]).toFixed(1));
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         (r"""
function first<T>(xs: T[]): T | undefined {
  return xs[0];
}
console.log(first(["7"])?.toFixed(1));
""", 2551),
         "With `any`, the result could be used as anything and crashed at runtime. With `<T>`, the compiler knows the result is a `string` and rejects `toFixed`."),
        ("A type parameter only in the return type",
         r"""
function parse<T>(json: string): T {
  return JSON.parse(json);
}
const count = parse<number>('"5"');
console.log(count + 1);
""",
         r"""
function parse(json: string): unknown {
  return JSON.parse(json);
}
const raw = parse('"5"');
const count = typeof raw === "number" ? raw : Number(raw);
console.log(count + 1);
""",
         "`parse<T>` lets the caller pick any `T` — an unchecked cast in disguise, and `\"5\" + 1` is `\"51\"`. Return `unknown` and check."),
        ("Static members are shared by every `T`",
         r"""
class Registry<T> {
  static count = 0;
  readonly items: T[] = [];
  add(item: T): void {
    this.items.push(item);
    Registry.count++;
  }
}
const names = new Registry<string>();
const ids = new Registry<number>();
names.add("ana");
ids.add(1);
ids.add(2);
console.log("names registered: " + Registry.count);
""",
         r"""
class Registry<T> {
  readonly items: T[] = [];
  add(item: T): void {
    this.items.push(item);
  }
  get count(): number {
    return this.items.length;
  }
}
const names = new Registry<string>();
const ids = new Registry<number>();
names.add("ana");
ids.add(1);
ids.add(2);
console.log("names registered: " + names.count);
""",
         "Type parameters are erased; there's one class at runtime, and its static field counts for every instantiation. Keep per-collection state in instances."),
    ],
    later=[
        "**Week 18 — Constraints and inference.** `extends`, `const` type parameters and `NoInfer`.",
        "**Week 24 — Generic data structures.** Heaps, linked lists and iterators over `T`.",
    ],
)


_deepen(
    "ts_generic_constraints",
    why=r"""
An unconstrained `T` could be anything, so the function body can do almost
nothing with it. A constraint — `T extends { length: number }`,
`K extends keyof T`, `T extends { id: string }` — states what every allowed type
must have, which lets the body use it *and* keeps the caller's specific type in
the result.

The most useful constraint by far is `K extends keyof T`: it ties a key argument
to an object argument, so `sortBy(users, "age")` is checked and `"agee"` isn't
allowed.
""",
    examples=[
        ("Sort by any key of the element",
         r"""
function sortBy<T, K extends keyof T>(items: readonly T[], key: K): T[] {
  return items.toSorted((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));
}
const people = [{ name: "cy", age: 40 }, { name: "ana", age: 31 }, { name: "bo", age: 25 }];
console.log(sortBy(people, "age").map((p) => p.name).join(","));
console.log(sortBy(people, "name").map((p) => p.name).join(","));
""", [""],
         "`key` can only be `\"name\"` or `\"age\"`, and the result is still an array of the caller's element type."),
        ("Upsert anything with an id",
         r"""
function upsert<T extends { id: string }>(items: readonly T[], item: T): T[] {
  const i = items.findIndex((x) => x.id === item.id);
  return i < 0 ? [...items, item] : items.with(i, item);
}
type Todo = { id: string; title: string; done: boolean };
let todos: Todo[] = [{ id: "a", title: "write", done: false }];
todos = upsert(todos, { id: "a", title: "write", done: true });
todos = upsert(todos, { id: "b", title: "test", done: false });
console.log(todos.map((t) => `${t.id}:${t.done}`).join(" "));
""", [""],
         "The constraint lets the body read `.id`; the return type is still `Todo[]`, with `done` and `title` intact."),
        ("A factory constrained to a constructor",
         r"""
function createAll<T>(Ctor: new (label: string) => T, labels: readonly string[]): T[] {
  return labels.map((l) => new Ctor(l));
}
class Tag {
  readonly text: string;
  constructor(label: string) {
    this.text = "#" + label.toLowerCase();
  }
}
console.log(createAll(Tag, ["TS", "Node"]).map((t) => t.text).join(" "));
""", [""],
         "`new (label: string) => T` constrains the argument to something constructible, and `T` becomes the instance type."),
    ],
    errors=[
        (2345, r"""
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
longest(10, 20);
""", "Numbers have no `length`, so they don't satisfy the constraint."),
        (2344, r"""
type Box<T extends object> = { value: T };
type Wrong = Box<string>;
""", "Type-level uses are checked against constraints too."),
    ],
    pitfalls=[
        ("`T extends object` also accepts arrays",
         r"""
function describe<T extends object>(x: T): string {
  return "fields: " + Object.keys(x).join(",");
}
console.log(describe({ a: 1, b: 2 }), "|", describe(["x", "y"]));
""",
         r"""
function describe<T extends object>(x: T): string {
  return Array.isArray(x) ? `list of ${x.length}` : "fields: " + Object.keys(x).join(",");
}
console.log(describe({ a: 1, b: 2 }), "|", describe(["x", "y"]));
""",
         "Arrays are objects, so they satisfy `object` — and `Object.keys` reports their indexes. Handle arrays explicitly (or constrain more tightly)."),
        ("A constraint used as the return type",
         (r"""
function longest(a: { length: number }, b: { length: number }) {
  return a.length >= b.length ? a : b;
}
console.log(longest("hello", "hi").toUpperCase());
""", 2339),
         r"""
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
console.log(longest("hello", "hi").toUpperCase());
""",
         "Without a type parameter, the result is only `{ length: number }` — the string-ness is lost. `T` carries it through."),
        ("Runtime keys are always strings",
         r"""
function hasKey<T extends object>(o: T, key: keyof T): boolean {
  return Object.keys(o).includes(key as string);
}
const byCode: Record<number, string> = { 404: "not found" };
console.log(hasKey(byCode, 404));
""",
         r"""
function hasKey<T extends object>(o: T, key: keyof T): boolean {
  return Object.keys(o).includes(String(key));
}
const byCode: Record<number, string> = { 404: "not found" };
console.log(hasKey(byCode, 404));
""",
         "`keyof T` can include `number` keys, but at runtime every object key is a string. The cast hid the mismatch; convert explicitly."),
    ],
    later=[
        "**Week 18 — Generic inference.** How `T` and `K` are inferred from these calls.",
        "**Week 19 — Lookup types.** `T[K]` and why `K extends keyof T` makes it safe.",
    ],
)


_deepen(
    "ts_keyof_indexed",
    why=r"""
The best way to keep related types in sync is to derive them from one source.
`typeof` lifts a value into a type, `keyof` lists a type's keys, and an indexed
access `T[K]` reads a property's type — together they let a settings object, a
list of allowed values or an event map *be* the specification, with every other
type computed from it.

Change the source and everything derived changes with it; the compiler then
points at each place that needs updating.
""",
    examples=[
        ("Typed get and set from one object",
         r"""
const defaults = { theme: "light", fontSize: 14, autosave: true };
type Settings = typeof defaults;
const current: Settings = { ...defaults };
function set<K extends keyof Settings>(key: K, value: Settings[K]): void {
  current[key] = value;
}
set("fontSize", 16);
set("theme", "dark");
console.log(JSON.stringify(current));
""", [""],
         "`set(\"fontSize\", \"big\")` would be a compile error: the value's type follows the key."),
        ("An event map",
         r"""
type Events = { login: { user: string }; logout: { user: string; reason: string }; tick: number };
const log: string[] = [];
function emit<E extends keyof Events>(name: E, payload: Events[E]): void {
  log.push(`${name} ${JSON.stringify(payload)}`);
}
emit("login", { user: "ana" });
emit("tick", 3);
emit("logout", { user: "ana", reason: "timeout" });
console.log(log.join("\n"));
""", [""],
         "Each event name brings its own payload type; a wrong payload for an event doesn't compile."),
        ("A list of allowed values as the source",
         r"""
const LEVELS = ["debug", "info", "warn", "error"] as const;
type Level = (typeof LEVELS)[number];
const isLevel = (s: string): s is Level => LEVELS.some((l) => l === s);
for (const s of ["warn", "fatal"]) console.log(isLevel(s) ? `level ${s} = ${LEVELS.indexOf(s)}` : `unknown level ${s}`);
""", [""],
         "The array is the runtime check; the type is derived from it."),
    ],
    errors=[
        (2339, r"""
type Settings = { theme: string; fontSize: number };
type Color = Settings["color"];
""", "Indexed access follows the same rules as property access: `color` isn't a key of `Settings`."),
        (7053, r"""
const defaults = { theme: "light", fontSize: 14 };
function read(key: string) {
  return defaults[key];
}
""", "Any `string` isn't a known key. Type the parameter as `keyof typeof defaults`."),
    ],
    pitfalls=[
        ("`keyof` a union is only the shared keys",
         (r"""
type Circle = { kind: "circle"; r: number };
type Square = { kind: "square"; side: number };
function read(s: Circle | Square, key: keyof (Circle | Square)): unknown {
  return s[key];
}
console.log(read({ kind: "circle", r: 2 }, "r"));
""", 2345),
         r"""
type Circle = { kind: "circle"; r: number };
type Square = { kind: "square"; side: number };
function size(s: Circle | Square): number {
  return s.kind === "circle" ? s.r : s.side;
}
console.log(size({ kind: "circle", r: 2 }));
""",
         "`keyof (A | B)` is the keys *every* member has — here only `kind`. To reach member-specific fields, narrow the value first."),
        ("A derived type from a mutable array",
         r"""
const MODES = ["light", "dark"];
type Mode = (typeof MODES)[number];
const input: Mode = "zzz";
console.log("accepted mode " + input);
""",
         (r"""
const MODES = ["light", "dark"] as const;
type Mode = (typeof MODES)[number];
const input: Mode = "zzz";
console.log("accepted mode " + input);
""", 2322),
         "Without `as const`, `MODES` is a `string[]` and `Mode` is just `string`, so anything is accepted. `as const` keeps the literals."),
        ("Numeric keys come back as strings",
         r"""
const names: Record<number, string> = { 1: "one", 2: "two" };
const found = Object.keys(names).find((k) => k === (2 as unknown as string));
console.log(found === undefined ? "not found" : names[Number(found)]);
""",
         r"""
const names: Record<number, string> = { 1: "one", 2: "two" };
const found = Object.keys(names).find((k) => k === String(2));
console.log(found === undefined ? "not found" : names[Number(found)]);
""",
         "`Object.keys` returns strings even for number-keyed records. Compare string to string."),
    ],
    later=[
        "**Week 19 — Lookup types.** `T[number]`, tuple positions, and `Object.keys` in depth.",
        "**Week 20 — Mapped types.** Iterating `keyof T` to build new types.",
    ],
)


_deepen(
    "ts_mapped_types",
    why=r"""
Many types are "the same keys as `T`, but…": every field optional for a patch,
every field a validator for a form, every field a boolean for "which fields
changed". A mapped type, `{ [K in keyof T]: … }`, writes that transformation
once, and the result tracks `T` — add a field to the model and every derived type
gains it.

It's also how `Partial`, `Readonly`, `Pick` and `Record` are defined, which makes
them easy to read and, when needed, to adapt.
""",
    examples=[
        ("A validator for every field",
         r"""
type Signup = { name: string; age: number; email: string };
type Validators<T> = { [K in keyof T]: (value: T[K]) => string | undefined };
const rules: Validators<Signup> = {
  name: (v) => (v.trim().length < 2 ? "too short" : undefined),
  age: (v) => (v < 13 ? "too young" : undefined),
  email: (v) => (v.includes("@") ? undefined : "invalid"),
};
function validate(form: Signup): string[] {
  return (Object.keys(rules) as (keyof Signup)[]).flatMap((k) => {
    const message = k === "age" ? rules.age(form.age) : rules[k](form[k]);
    return message === undefined ? [] : [`${k}: ${message}`];
  });
}
console.log(validate({ name: "A", age: 9, email: "nope" }).join("; "));
console.log(validate({ name: "Ana", age: 31, email: "ana@x.io" }).length);
""", [""],
         "Each rule's parameter is typed from its field. Forgetting a field, or a rule that expects the wrong type, is a compile error."),
        ("Tracking which fields changed",
         r"""
type Flags<T> = { [K in keyof T]: boolean };
function changed<T extends object>(before: T, after: T): Flags<T> {
  return Object.fromEntries((Object.keys(before) as (keyof T)[]).map((k) => [k, before[k] !== after[k]])) as Flags<T>;
}
const diff = changed({ name: "ana", age: 31, city: "Oslo" }, { name: "ana", age: 32, city: "Rome" });
console.log(Object.entries(diff).filter(([, v]) => v).map(([k]) => k).join(","));
""", [""],
         "`Flags<T>` has exactly `T`'s keys; the runtime builds the object from the same keys."),
        ("Nullable columns from a model",
         r"""
type Row = { id: number; name: string; email: string };
type Nullable<T> = { [K in keyof T]: T[K] | null };
const fromDb: Nullable<Row> = { id: 1, name: "ana", email: null };
const display = Object.entries(fromDb).map(([k, v]) => `${k}=${v ?? "(none)"}`).join(" ");
console.log(display);
""", [""],
         "A database row with nullable columns, described once from the model."),
    ],
    errors=[
        (2741, r"""
type Signup = { name: string; age: number };
type Validators<T> = { [K in keyof T]: (value: T[K]) => boolean };
const rules: Validators<Signup> = { name: (v) => v.length > 1 };
""", "A mapped type over `keyof T` requires every key — the form can't forget to validate `age`."),
        (2322, r"""
type Signup = { name: string; age: number };
type Validators<T> = { [K in keyof T]: (value: T[K]) => boolean };
const rules: Validators<Signup> = {
  name: (v) => v.length > 1,
  age: (v: string) => v.length > 0,
};
""", "The `age` validator must take a number, because `T[\"age\"]` is `number`."),
    ],
    pitfalls=[
        ("`Partial` is only one level deep",
         (r"""
type Config = { db: { host: string; port: number }; debug: boolean };
const patch: Partial<Config> = { db: { host: "db.local" } };
console.log(JSON.stringify(patch));
""", 2741),
         r"""
type Config = { db: { host: string; port: number }; debug: boolean };
type ConfigPatch = { db?: Partial<Config["db"]>; debug?: boolean };
const patch: ConfigPatch = { db: { host: "db.local" } };
console.log(JSON.stringify(patch));
""",
         "`Partial<Config>` makes `db` optional, but if present it must be a complete `db`. Nested patches need a deeper type (week 20's `DeepPartial`)."),
        ("`Readonly<T>` is a view, not a copy",
         r"""
type Cfg = { port: number };
const source: Cfg = { port: 80 };
const view: Readonly<Cfg> = source;
source.port = 9;
console.log("view sees port " + view.port);
""",
         r"""
type Cfg = { port: number };
const source: Cfg = { port: 80 };
const view: Readonly<Cfg> = { ...source };
source.port = 9;
console.log("view sees port " + view.port);
""",
         "A readonly *type* on the same object still sees every change made through another reference. Copy when you need a snapshot."),
        ("A mapped type doesn't build the object",
         r"""
type Flags<T> = { [K in keyof T]: boolean };
type Form = { name: string; email: string };
const touched = {} as Flags<Form>;
console.log("email touched: " + touched.email);
""",
         r"""
type Flags<T> = { [K in keyof T]: boolean };
type Form = { name: string; email: string };
const touched: Flags<Form> = { name: false, email: false };
console.log("email touched: " + touched.email);
""",
         "The cast promised a complete object and delivered `{}`. Build every key (or let the compiler check a literal)."),
    ],
    later=[
        "**Week 20 — Key remapping.** Renaming and filtering keys with `as`.",
        "**Week 20 — Problem set.** `DeepReadonly`, `OptionalKeys`, and a typed store.",
    ],
)


_deepen(
    "ts_conditional_types",
    why=r"""
Sometimes the type you want depends on another type: the element type of an
array, the resolved value of a promise, the success member of a result, a
different return type for different argument kinds. Conditional types — `T
extends U ? X : Y` — are `if` statements at the type level, and `infer` lets them
pull a type out of a pattern.

They're how `ReturnType`, `Awaited`, `Exclude` and `NonNullable` work, and how
libraries give precise types to flexible APIs. This chapter is reading and
writing them for everyday use; weeks 21 and 22 go deeper.
""",
    examples=[
        ("A return type chosen by the argument",
         r"""
type Parsed<K extends "int" | "list"> = K extends "int" ? number : string[];
function parse<K extends "int" | "list">(kind: K, text: string): Parsed<K> {
  return (kind === "int" ? Number.parseInt(text, 10) : text.split(",")) as Parsed<K>;
}
const n = parse("int", "41");
const xs = parse("list", "a,b,c");
console.log(n + 1, xs.length, xs.join("+"));
""", [""],
         "At each call `K` is a literal, so the result type resolves to `number` or `string[]`. The implementation needs one cast because `K` is still generic inside it."),
        ("Types read out of a function",
         r"""
async function loadUser(id: number) {
  return { id, name: id === 1 ? "ana" : "bo", roles: ["member"] };
}
type User = Awaited<ReturnType<typeof loadUser>>;
const users: User[] = [await loadUser(1), await loadUser(2)];
console.log(users.map((u) => `${u.id}:${u.name}`).join(" "));
""", [""],
         "`ReturnType` gives `Promise<{…}>`; `Awaited` unwraps it. The loader is the only place the user's shape is written."),
        ("Keys whose values are numbers",
         r"""
type NumericKeys<T> = { [K in keyof T]: T[K] extends number ? K : never }[keyof T];
function sumFields<T>(row: T, keys: readonly NumericKeys<T>[]): number {
  return keys.reduce((s, k) => s + Number(row[k]), 0);
}
const order = { id: "A1", subtotal: 40, tax: 8, shipping: 5, note: "gift" };
console.log(sumFields(order, ["subtotal", "tax", "shipping"]));
""", [""],
         "A conditional inside a mapped type keeps only the numeric keys — so `\"note\"` can't be summed by mistake."),
    ],
    errors=[
        (2322, r"""
function describe<T extends string | number>(x: T): T extends string ? number : string {
  return typeof x === "string" ? x.length : String(x);
}
""", "Inside the body `T` is unresolved, so the compiler can't match a branch to the conditional return type. Use overloads, or a single cast after the check."),
        (2344, r"""
type R = ReturnType<string>;
""", "`ReturnType` is constrained to function types; a `string` has no return type."),
    ],
    pitfalls=[
        ("Using a promise type as if it were the value",
         r"""
async function save(): Promise<string> {
  return "ok";
}
const result: ReturnType<typeof save> = save();
console.log("saved: " + result);
""",
         r"""
async function save(): Promise<string> {
  return "ok";
}
const result: Awaited<ReturnType<typeof save>> = await save();
console.log("saved: " + result);
""",
         "`ReturnType` of an async function is the *promise*. Printing it gives `[object Promise]`; `Awaited` and `await` give the value."),
        ("A pattern that misses readonly arrays",
         (r"""
type Elem<T> = T extends (infer E)[] ? E : never;
function first<T extends readonly unknown[]>(xs: T): Elem<T> | undefined {
  return xs[0] as Elem<T> | undefined;
}
const SIZES = ["s", "m"] as const;
const s = first(SIZES);
console.log(s?.toUpperCase());
""", 2339),
         r"""
type Elem<T> = T extends readonly (infer E)[] ? E : never;
function first<T extends readonly unknown[]>(xs: T): Elem<T> | undefined {
  return xs[0] as Elem<T> | undefined;
}
const SIZES = ["s", "m"] as const;
const s = first(SIZES);
console.log(s?.toUpperCase());
""",
         "`readonly [\"s\", \"m\"]` doesn't match `(infer E)[]` (a mutable array), so `Elem` was `never` and the result could only be `undefined`. Match `readonly (infer E)[]` to cover both."),
        ("Types don't exist at runtime",
         r"""
type IsNumber<T> = T extends number ? true : false;
function check<T>(value: T): IsNumber<T> {
  return (typeof value === "string") as IsNumber<T>;
}
console.log(check(5), check("5"));
""",
         r"""
type IsNumber<T> = T extends number ? true : false;
function check<T>(value: T): IsNumber<T> {
  return (typeof value === "number") as IsNumber<T>;
}
console.log(check(5), check("5"));
""",
         "The conditional type only *describes* the result; the runtime code still has to compute it, and the cast accepted a wrong computation. Test the implementation."),
    ],
    later=[
        "**Week 21 — Distributive conditional types.** What happens with unions and `never`.",
        "**Week 21 — Problem set.** `IsUnion`, `UnionToIntersection`, `FlattenDeep`.",
        "**Week 22 — Template literal types.** Conditional types that parse strings.",
    ],
)


_deepen(
    "ts_template_literal_types",
    why=r"""
Lots of APIs use strings with structure: CSS sizes like `12px`, event names like
`user:created`, routes like `/users/:id`, method names like `getName`. Template
literal types describe those shapes — `` `${number}px` ``, `` `${Entity}:${Action}` `` —
so the compiler can check them, and derive new names from old ones with
`Capitalize`, `Uppercase` and friends.

Like every type, they're erased: a template literal type checks the strings
*written in your code*. Strings arriving at runtime still need a real check, and
this chapter shows both halves.
""",
    examples=[
        ("CSS sizes, checked and parsed",
         r"""
type Size = `${number}px` | `${number}%`;
function toPixels(size: Size, container: number): number {
  return size.endsWith("%") ? (parseFloat(size) / 100) * container : parseFloat(size);
}
const sizes: Size[] = ["120px", "50%", "12.5px"];
console.log(sizes.map((s) => toPixels(s, 400)).join(" "));
""", [""],
         "`\"12pt\"` wouldn't compile as a `Size`; `parseFloat` does the runtime half."),
        ("Event names from two unions",
         r"""
type Entity = "user" | "order";
type Action = "created" | "deleted";
type EventName = `${Entity}:${Action}`;
const counts = new Map<EventName, number>();
const emit = (e: EventName) => counts.set(e, (counts.get(e) ?? 0) + 1);
emit("user:created");
emit("order:deleted");
emit("user:created");
console.log([...counts].map(([e, n]) => `${e}=${n}`).join(" "));
""", [""],
         "Four event names, derived rather than listed, and every `emit` call is checked against them."),
        ("A route prefix that narrows",
         r"""
type ApiPath = `/api/${string}`;
const isApi = (p: string): p is ApiPath => p.startsWith("/api/");
function handle(path: string): string {
  return isApi(path) ? `api call to ${path.slice(5)}` : `page ${path}`;
}
console.log(handle("/api/users"), "|", handle("/about"));
""", [""],
         "A predicate turns a runtime check into the pattern type."),
    ],
    errors=[
        (2322, r"""
type Size = `${number}px`;
const width: Size = "12pt";
""", "The string doesn't match the pattern — the compiler checks literals against template types."),
        (2345, r"""
type EventName = `${"user" | "order"}:${"created" | "deleted"}`;
function emit(e: EventName): void {}
emit("user:updated");
""", "Only the combinations of the two unions are valid event names."),
    ],
    pitfalls=[
        ("A cast is not a check",
         r"""
type Size = `${number}px`;
const fromUser = "12pt" as Size;
console.log("width " + parseFloat(fromUser) + " (" + fromUser + ")");
""",
         r"""
type Size = `${number}px`;
const isSize = (s: string): s is Size => /^\d+(\.\d+)?px$/.test(s);
const raw = "12pt";
console.log(isSize(raw) ? "width " + parseFloat(raw) : "rejected " + raw);
""",
         "The pattern type only checks strings the compiler can see. Validate input at runtime before giving it the type."),
        ("A template of numbers produces strings",
         (r"""
type Code = 200 | 404;
type CodeText = `${Code}`;
function label(code: Code, text: CodeText): boolean {
  return code === text;
}
console.log(label(404, "404"));
""", 2367),
         r"""
type Code = 200 | 404;
type CodeText = `${Code}`;
function label(code: Code, text: CodeText): boolean {
  return String(code) === text;
}
console.log(label(404, "404"));
""",
         "`` `${Code}` `` is `\"200\" | \"404\"` — strings — and a number is never `===` to a string. Convert before comparing."),
        ("An intrinsic type doesn't transform values",
         r"""
const raw = "draft";
const shout = raw as Uppercase<string>;
console.log(shout);
""",
         r"""
const raw = "draft";
const shout = raw.toUpperCase() as Uppercase<string>;
console.log(shout);
""",
         "`Uppercase<…>` describes a string; it doesn't change one. The runtime value has to be produced by real code."),
    ],
    later=[
        "**Week 20 — Key remapping.** Template literals as generated key names.",
        "**Week 22 — Recursive types.** Parsing strings at the type level (`Split`, `RouteParams`).",
    ],
)


_deepen(
    "ts_type_level",
    why=r"""
Some data is recursive: JSON values contain JSON values, trees contain trees,
menus contain submenus. Recursive types describe them exactly — `type Json =
… | Json[] | { [k: string]: Json }` — and the functions that walk them follow the
same structure as the type.

The same recursion also powers type-level programs (`DeepReadonly`, tuple
manipulation, string parsing). This chapter is the practical side: modelling
recursive data, and writing the recursive code that goes with it — including when
recursion is the wrong tool at runtime.
""",
    examples=[
        ("A recursive JSON type and a walker",
         r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
function countLeaves(v: Json): number {
  if (Array.isArray(v)) return v.reduce<number>((n, x) => n + countLeaves(x), 0);
  if (v !== null && typeof v === "object") return Object.values(v).reduce<number>((n, x) => n + countLeaves(x), 0);
  return 1;
}
const doc: Json = { name: "ana", tags: ["a", "b"], address: { city: "Oslo", geo: [59.9, 10.7] }, active: true };
console.log(countLeaves(doc));
""", [""],
         "Each branch of the function matches a member of the type; recursion handles the nesting."),
        ("A generic tree",
         r"""
type Tree<T> = { value: T; children: Tree<T>[] };
const menu: Tree<string> = {
  value: "root",
  children: [{ value: "file", children: [{ value: "open", children: [] }, { value: "save", children: [] }] }, { value: "help", children: [] }],
};
function paths<T>(t: Tree<T>, prefix = ""): string[] {
  const here = prefix === "" ? String(t.value) : `${prefix}/${String(t.value)}`;
  return t.children.length === 0 ? [here] : t.children.flatMap((c) => paths(c, here));
}
console.log(paths(menu).join(" "));
""", [""],
         "`Tree<T>` refers to itself through `children`; `paths` recurses the same way."),
        ("A deeply read-only parameter",
         r"""
type DeepReadonly<T> = { readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K] };
type Config = { server: { host: string; ports: number[] }; debug: boolean };
function describe(c: DeepReadonly<Config>): string {
  return `${c.server.host}:${c.server.ports.join("/")} debug=${c.debug}`;
}
console.log(describe({ server: { host: "localhost", ports: [80, 443] }, debug: false }));
""", [""],
         "`describe` promises not to change anything at any depth — `c.server.ports.push(1)` would be a compile error."),
    ],
    errors=[
        (2456, r"""
type Bad = Bad | string;
""", "A type alias can refer to itself only *inside* a structure (an array, an object property) — directly, it has no meaning."),
        (2322, r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
const doc: Json = { created: new Date() };
""", "A `Date` isn't JSON (it has methods and serialises to a string). Store `new Date().toISOString()`."),
    ],
    pitfalls=[
        ("Recursion too deep for the call stack",
         r"""
function depth(v: unknown): number {
  return Array.isArray(v) ? 1 + Math.max(0, ...v.map(depth)) : 0;
}
let nested: unknown = 0;
for (let i = 0; i < 20000; i++) nested = [nested];
try {
  console.log(depth(nested));
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.name : String(e)));
}
""",
         r"""
function depth(root: unknown): number {
  let max = 0;
  const stack: [unknown, number][] = [[root, 0]];
  while (stack.length > 0) {
    const [v, d] = stack.pop() ?? [null, 0];
    if (Array.isArray(v)) {
      max = Math.max(max, d + 1);
      for (const x of v) stack.push([x, d + 1]);
    }
  }
  return max;
}
let nested: unknown = 0;
for (let i = 0; i < 20000; i++) nested = [nested];
console.log(depth(nested));
""",
         "A recursive function uses a stack frame per level, and Node runs out after roughly ten thousand. An explicit stack handles any depth."),
        ("A `Date` smuggled into JSON",
         (r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
const event: Json = { title: "launch", at: new Date(Date.UTC(2026, 8, 26)) };
console.log(JSON.stringify(event));
""", 2322),
         r"""
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
const event: Json = { title: "launch", at: new Date(Date.UTC(2026, 8, 26)).toISOString() };
console.log(JSON.stringify(event));
""",
         "The recursive `Json` type catches values that wouldn't survive a round trip — convert them explicitly."),
        ("A deep read-only type over shared data",
         r"""
type DeepReadonly<T> = { readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K] };
const settings = { limits: { maxUsers: 10 } };
const view: DeepReadonly<typeof settings> = settings;
settings.limits.maxUsers = 99;
console.log(view.limits.maxUsers);
""",
         r"""
type DeepReadonly<T> = { readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K] };
const settings = { limits: { maxUsers: 10 } };
const view: DeepReadonly<typeof settings> = structuredClone(settings);
settings.limits.maxUsers = 99;
console.log(view.limits.maxUsers);
""",
         "The type prevents writes *through* `view`, but the original object was still writable. Clone when the value must not change underneath you."),
    ],
    later=[
        "**Week 22 — Template literals and recursive types.** Parsing strings and tuples at the type level.",
        "**Week 22 — Type-level performance.** Depth limits (TS2589) and tail recursion.",
    ],
)
