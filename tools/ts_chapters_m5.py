# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New TypeScript chapters for Mastery Month 5 — Generics & type-level
# programming.
#
#   week 18  ts_generic_inference  how type arguments are inferred; `const`
#                                  type parameters, `NoInfer`, defaults, and
#                                  when to write the type argument yourself
#   week 19  ts_lookup_types       indexed access: T[K], T[number], tuple
#                                  elements, `typeof obj[keyof typeof obj]`
#   week 20  ts_key_remapping      `as` clauses in mapped types: renaming,
#                                  filtering and template-literal keys
#   week 21  ts_distributive       distribution over unions, `[T] extends [U]`,
#                                  `never` as the empty union, `infer … extends`
#   week 22  ts_type_performance   recursion limits (TS2589), tail-recursive
#                                  conditional types, and when to stop
#
# Built with ts_chapter_kit.py's `_chapter`; every printed output and compiler
# message is computed (python tools/gen_ts_outputs.py). These are chapters
# about types, which print nothing — so every example is a small program whose
# runtime half *uses* the types, and the notes say what the compiler inferred.
# ---------------------------------------------------------------------------

_chapter(
    "ts_generic_inference", "TS: Generics & Type-Level",
    "How Generic Inference Works",
    "How TypeScript picks a type argument from your call, why it sometimes picks the wrong one, and the tools that steer it: `const` type parameters, `NoInfer`, defaults, and writing the type argument yourself.",
    "When you call `first(xs)` you never write `first<number>(xs)` — the compiler infers `T` from the arguments, widening literals the same way a `let` does. Most of the time that is exactly right. When it isn't, you have four tools: a `const` type parameter keeps literal types (TS 5.0), `NoInfer<T>` stops one argument from influencing `T` (TS 5.4), a default applies when nothing can be inferred, and an explicit type argument overrides inference entirely.",
    "Java infers generic method type arguments too, but conservatively and from fewer places. TypeScript infers from every argument, from the expected return type, and even from callbacks' return values — and it widens literal types unless you ask it not to.",
    why=r"""
A generic function is a promise: *give me any `T` and I'll keep track of it.* The
caller almost never says what `T` is — the compiler works it out from the call.
That inference is so good that it is easy to forget it's happening, until it
picks something you didn't expect:

- `pick(["small", "large"], "medium")` compiles, because `T` became `string`.
- `box([])` gives you a box of `never`, and nothing can be added to it.
- `routes(["/", "/users"])` returns `string[]`, not the two paths you wrote.

Each of these is inference doing exactly what its rules say. Knowing the rules
— where candidates come from, when literals widen, which argument wins — turns
these from mysteries into one-line fixes.
""",
    idea=r"""
**Where `T` comes from.** For each type parameter the compiler collects
*candidates* from the arguments whose parameter types mention it, then picks the
best common type. `wrap(1)` has the candidate `1`, widened to `number` because
nothing asked for the literal. Contextual types count too: in
`const n: number[] = parse(text)`, the expected return type can supply `T`.

**Literal widening.** Like `let x = "a"`, an inferred type parameter widens
`"a"` to `string` and `1` to `number` — unless the parameter is *constrained* to
a literal-ish type (`T extends string` keeps `"a"`), or declared `const`.

**`const` type parameters (TS 5.0).** `function routes<const T extends readonly
string[]>(paths: T): T` infers `readonly ["/", "/users"]` from
`routes(["/", "/users"])` — as if the caller had written `as const`.

**`NoInfer<T>` (TS 5.4).** Sometimes one argument should *decide* `T` and
another should only be *checked* against it:

```ts
function pick<T extends string>(options: T[], fallback: NoInfer<T>): T
```

Without `NoInfer`, `"medium"` would become a candidate and `T` would widen to
include it; with it, `T` comes only from `options`, and `"medium"` is an error.

**Defaults.** `<T = string>` supplies `T` when there is nothing to infer from —
typically for classes and factory functions called with no arguments.

**Say it yourself** when inference has nothing to go on (`new Map()`,
`box([])`, `JSON.parse`) or would pick something too narrow. An explicit
`box<string>([])` is clearer than a cast afterwards.

**Two smells.** A type parameter used only once — `function log<T>(x: T): void`
— relates nothing to anything; it is just `unknown`. And a function whose return
type is a bare `T` that the body can't actually produce is lying: the compiler
will say "`T` could be instantiated with an arbitrary type".
""",
    examples=[
        ("Inference from the arguments",
         r"""
function wrap<T>(value: T): { value: T; label: string } {
  return { value, label: typeof value };
}

const a = wrap(42);            // T = number   (the literal 42 widened)
const b = wrap(["x", "y"]);    // T = string[]
const c = wrap({ id: 7 });     // T = { id: number }

console.log(a.value + 1, a.label);
console.log(b.value.join("+"), b.label);
console.log(c.value.id * 2, c.label);
""", [""],
         "No type argument is written anywhere. Each call's `T` comes from its argument, which is why `a.value + 1` and `b.value.join` type-check: the result keeps the precise type."),
        ("`const` type parameters keep the literals",
         r"""
function plainRoutes<T extends readonly string[]>(paths: T): T {
  return paths;
}
function exactRoutes<const T extends readonly string[]>(paths: T): T {
  return paths;
}

const loose = plainRoutes(["/", "/users"]);   // string[]
const exact = exactRoutes(["/", "/users"]);   // readonly ["/", "/users"]
type Route = (typeof exact)[number];          // "/" | "/users"

const go = (r: Route) => "navigating to " + r;
console.log(go(exact[1]));
console.log(loose.length, exact.length);
""", [""],
         "Same body, one modifier apart. With `const`, the call is inferred as if the caller had written `as const`, so the route union can be derived from the value."),
        ("`NoInfer` — one argument decides, the other is checked",
         r"""
function pick<T extends string>(options: readonly T[], choice: string, fallback: NoInfer<T>): T {
  return options.find((o) => o === choice) ?? fallback;
}

const sizes = ["small", "large"] as const;
console.log(pick(sizes, "large", "small"));
console.log(pick(sizes, "huge", "small"));
""", [""],
         "`T` is inferred only from `options` (`\"small\" | \"large\"`). Without `NoInfer`, the fallback would also be a candidate, and `pick(sizes, \"x\", \"medium\")` would quietly widen `T` to include `\"medium\"`."),
        ("When to write the type argument",
         r"""
function box<T>(items: T[]) {
  return {
    add(item: T) {
      items.push(item);
      return this;
    },
    all: () => items.join(", "),
  };
}

const names = box<string>([]).add("ana").add("bo");
const counts = new Map<string, number>();
for (const n of ["a", "b", "a"]) counts.set(n, (counts.get(n) ?? 0) + 1);

console.log(names.all());
console.log([...counts].map(([k, v]) => `${k}=${v}`).join(" "));
""", [""],
         "An empty array or an empty `Map` gives inference nothing to work with, so say what goes in it. `box([])` alone would infer `never` and reject every `add`."),
    ],
    errors=[
        (2322, r"""
function filled<T>(n: number): T[] {
  return Array.from({ length: n }, () => 0);
}
""", "The signature promises an array of whatever `T` the caller picks, and the body can only make numbers. \"`T` could be instantiated with an arbitrary type\" is the compiler refusing that lie."),
        (2345, r"""
function pick<T extends string>(options: readonly T[], fallback: NoInfer<T>): T {
  return options[0] ?? fallback;
}
pick(["small", "large"], "medium");
""", "`NoInfer` kept `\"medium\"` out of inference, so `T` is `\"small\" | \"large\"` and the fallback is checked against it."),
        (2344, r"""
type Entity<T extends { id: number }> = { data: T; loadedAt: number };
type Wrong = Entity<{ name: string }>;
""", "A constraint is checked wherever the generic is used: a type without an `id` can't be an `Entity`'s data."),
    ],
    pitfalls=[
        ("An empty argument infers `never`",
         (r"""
function box<T>(items: T[]) {
  return { add: (item: T) => items.push(item), size: () => items.length };
}
const b = box([]);
b.add("ana");
console.log(b.size());
""", 2345),
         r"""
function box<T>(items: T[]) {
  return { add: (item: T) => items.push(item), size: () => items.length };
}
const b = box<string>([]);
b.add("ana");
console.log(b.size());
""",
         "With nothing inside `[]`, the best `T` is `never` — a box that accepts nothing. Write the type argument when the argument can't carry it."),
        ("Two candidates that don't agree",
         (r"""
function same<T>(a: T, b: T): boolean {
  return a === b;
}
console.log(same(1, "1"));
""", 2345),
         r"""
function same<T>(a: T, b: T): boolean {
  return a === b;
}
console.log(same<number | string>(1, "1"));
""",
         "`T` is fixed by the first argument (`number`), and the second must then fit it. If mixing is intended, say so with an explicit union; usually the error is catching a real mix-up."),
        ("A bare `T` return that can be `undefined`",
         r"""
function first<T>(xs: T[]): T {
  return xs[0] as T;
}
const empty: string[] = [];
console.log("first: " + first(empty));
""",
         r"""
function first<T>(xs: T[]): T | undefined {
  return xs[0];
}
const empty: string[] = [];
console.log("first: " + (first(empty) ?? "(none)"));
""",
         "Promising `T` forced a cast, and the empty array returned `undefined` anyway. `T | undefined` is the honest signature, and it makes every caller decide what an empty list means."),
    ],
    later=[
        "**Week 19 — Lookup types.** `K extends keyof T` and `T[K]`: inference that follows a key to its value type.",
        "**Week 21 — Conditional types.** `infer` is inference *inside* a type.",
        "**Week 24 — Generic data structures.** `Stack<T>`, `Heap<T>` and when a class's type argument must be written.",
    ],
    exercises=[
        _drill("ts_generic_inference-groupby", "A generic group-by",
               "`groupBy` works for any element type and any key function. Replace `____` so it returns a `Map` from each key to the items that produced it, in input order.",
               r"""
import * as fs from "fs";
function groupBy<T, K>(items: readonly T[], keyOf: (item: T) => K): Map<K, T[]> {
  const groups = new Map<K, T[]>();
  for (const item of items) {
    const key = keyOf(item);
    groups.set(key, [...(groups.get(key) ?? []), item]);
  }
  return groups;
}
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
for (const [len, ws] of groupBy(words, (w) => w.length)) console.log(`${len}: ${ws.join(" ")}`);
""", ["groups.set(key, [...(groups.get(key) ?? []), item]);"],
               ["a bb cc d eee", "same size here", "x"],
               hint="Look up the current group (maybe missing), and store a new array with the item added."),
        _drill("ts_generic_inference-explicit", "Tell inference what goes in",
               "`counter` starts empty, so inference can't see the key type. Replace `____` with the call that creates a counter of `string` keys.",
               r"""
import * as fs from "fs";
function counter<K>(start: [K, number][]) {
  const counts = new Map<K, number>(start);
  return {
    add(key: K) {
      counts.set(key, (counts.get(key) ?? 0) + 1);
    },
    top(): string {
      return [...counts].sort((a, b) => b[1] - a[1])[0]?.[0] + "";
    },
  };
}
const c = counter<string>([]);
for (const w of fs.readFileSync(0, "utf8").trim().split(/\s+/)) c.add(w);
console.log(c.top());
""", ["counter<string>([])"],
               ["a b a c a", "x y y", "solo"],
               hint="Write the type argument between `<` and `>` right after the function name."),
        _chal("ts_generic_inference-countby", "Count by any key", "Medium",
              "Write `countBy<T>(items: readonly T[], keyOf: (item: T) => string): Map<string, number>`. The input is lines of `name age city`. Print counts by city (in first-seen order), then by age group (`<30`, `30s`, `40+`), both as `key=count` space-separated.",
              r"""
type Person = { name: string; age: number; city: string };
function countBy<T>(items: readonly T[], keyOf: (item: T) => string): Map<string, number> {
  const counts = new Map<string, number>();
  for (const item of items) {
    const key = keyOf(item);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return counts;
}
const people: Person[] = input.split("\n").map((line) => {
  const [name = "", age = "0", city = ""] = line.trim().split(/\s+/);
  return { name, age: Number(age), city };
});
const show = (m: Map<string, number>) => [...m].map(([k, n]) => `${k}=${n}`).join(" ");
console.log(show(countBy(people, (p) => p.city)));
console.log(show(countBy(people, (p) => (p.age < 30 ? "<30" : p.age < 40 ? "30s" : "40+"))));
""", ["ana 31 oslo\nbo 25 rome\ncy 44 oslo\ndee 39 oslo", "eve 20 lima"],
              hint="`T` is inferred from `items`; the callback's parameter then gets `T` for free."),
    ],
    quiz=[
        _cq("What is `T` in `wrap(42)` for `function wrap<T>(x: T)`?",
            "`number` — the literal widens", ["`42`", "`unknown`", "`any`"],
            "Inferred type arguments widen literals like a `let` does, unless the parameter is `const` or constrained."),
        _cq("What does a `const` type parameter change?",
            "Arguments are inferred as if written with `as const`, keeping literal and tuple types",
            ["The parameter can't be reassigned", "The function becomes pure", "`T` must be a primitive"],
            "Added in TS 5.0: `<const T extends readonly string[]>`."),
        _cq("What is `NoInfer<T>` for?",
            "Stopping one argument from contributing to `T`, so it is only checked against it",
            ["Disabling type checking for an argument", "Making `T` optional", "Forcing an explicit type argument"],
            "TS 5.4. Typical use: a fallback or default that must be one of the inferred options."),
        _cq("`box([])` infers `T` as?",
            "`never`", ["`unknown`", "`any`", "`undefined`"],
            "There is no element to infer from. Write `box<string>([])`."),
        _cq("Why is `function log<T>(x: T): void` a smell?",
            "`T` appears once, so it relates nothing — it's just `unknown`",
            ["Generic functions can't return `void`", "It is slower", "`T` must be constrained"],
            "Type parameters exist to connect types: an input to an output, or two inputs."),
        _cq("When does a type parameter default like `<T = string>` apply?",
            "When no type argument is given and nothing can be inferred",
            ["Always, overriding inference", "Only for classes", "Only when `T` is `unknown`"],
            "Inference wins when it has candidates; the default fills the gap when it doesn't."),
    ],
    interview=[
        ("How does TypeScript infer generic type arguments?",
         "It collects candidates for each type parameter from the arguments (and the contextual return type), picks the best common type, and widens literals unless the parameter is constrained or `const`. If candidates conflict it reports an error at the argument that doesn't fit the chosen type."),
        ("What are `const` type parameters and `NoInfer`?",
         "`const T` (TS 5.0) infers arguments as if they had `as const`, keeping tuples and literal types — useful for route tables and config builders. `NoInfer<T>` (TS 5.4) blocks inference from one position, so an argument like a fallback is checked against `T` instead of widening it."),
        ("When do you pass a type argument explicitly?",
         "When inference has nothing to work with — an empty array or `new Map()` — or when I want a wider type than the argument suggests. Otherwise I let it infer; an explicit argument that inference would have produced anyway is just noise."),
    ],
)


_chapter(
    "ts_lookup_types", "TS: Generics & Type-Level",
    "Lookup Types",
    "Reading types out of other types: `T[K]`, `T[number]`, `T[\"a\" | \"b\"]`, tuple positions, and `(typeof obj)[keyof typeof obj]` — so one declaration can be the source of every related type.",
    "An indexed access type looks up a property's type the way `obj[key]` looks up a value: `User[\"email\"]` is the type of a user's email, `Row[number]` is the element type of an array, `Point[0]` the first position of a tuple, and `Config[keyof Config]` the union of every value type. Combined with `typeof` and `keyof`, they let you declare data once and derive the types, instead of writing each type twice.",
    "Java has nothing like it: a field's type can't be referred to as a type. In TypeScript the property access you write on values has a type-level twin, so a type can follow another type's structure and stay in step when it changes.",
    why=r"""
Duplicated types rot. You write a `User` type, then a function that takes "a
user's role", and you type the parameter `string` — or you copy the role union
into a second place. The day someone adds a role, one copy is updated and the
other isn't.

Lookup types remove the copy. `User["role"]` *is* the type of a user's role,
wherever you write it. `(typeof ROUTES)[number]` *is* whatever routes the array
holds. Change the source and every derived type follows — and the compiler shows
you every place the change matters.
""",
    idea=r"""
**Indexed access.** `T[K]` is the type of property `K` on `T`:

```ts
type User = { id: number; email: string; role: "admin" | "member"; tags: string[] };
type Role = User["role"];              // "admin" | "member"
type IdOrEmail = User["id" | "email"]; // number | string — a union key gives a union
type Tag = User["tags"][number];       // string — an array's element type
```

`K` must be a type the compiler knows is a key of `T`; anything else is an error.

**`[number]` reads arrays and tuples.** `string[][number]` is `string`.
For a tuple, `[number]` is the union of its elements and a literal index picks
one position: `[string, number][1]` is `number`.

**From values to types.** `typeof` lifts a value into the type world and
`keyof` lists a type's keys, so the common patterns are:

```ts
const SIZES = ["S", "M", "L"] as const;
type Size = (typeof SIZES)[number];                 // "S" | "M" | "L"

const LIMITS = { free: 3, pro: 50 } as const;
type Plan = keyof typeof LIMITS;                    // "free" | "pro"
type Limit = (typeof LIMITS)[keyof typeof LIMITS];  // 3 | 50
```

**Generic lookups.** `function get<T, K extends keyof T>(obj: T, key: K): T[K]`
is the typed property read: the result type follows the key you pass.

**`keyof` details worth knowing.** `keyof` a type with a string index signature
is `string | number` (numeric keys are strings at runtime). `PropertyKey` is
`string | number | symbol`, the type of any key. And `Object.keys(obj)` returns
`string[]`, not `(keyof T)[]` — correctly, because an object can have more keys
at runtime than its type lists.
""",
    examples=[
        ("Types read from one model",
         r"""
type User = { id: number; email: string; role: "admin" | "member"; tags: string[] };
type Role = User["role"];
type Tag = User["tags"][number];

const canEdit = (role: Role): boolean => role === "admin";
const badge = (tag: Tag): string => "#" + tag;

const u: User = { id: 1, email: "ana@x.io", role: "admin", tags: ["ops", "web"] };
console.log(canEdit(u.role), u.tags.map(badge).join(" "));
""", [""],
         "`Role` and `Tag` are never written out. Add `\"owner\"` to `User[\"role\"]` and `canEdit`'s parameter accepts it — and a `switch` over roles would show you where it's unhandled."),
        ("A union from a list, a union from a table",
         r"""
const SIZES = ["S", "M", "L", "XL"] as const;
type Size = (typeof SIZES)[number];

const PRICES = { S: 10, M: 12, L: 14, XL: 16 } as const satisfies Record<Size, number>;
type Price = (typeof PRICES)[Size];

function quote(size: Size, qty: number): string {
  const unit: Price = PRICES[size];
  return `${qty} x ${size} = ${unit * qty}`;
}
console.log(quote("M", 3));
console.log(SIZES.map((s) => `${s}:${PRICES[s]}`).join(" "));
""", [""],
         "`Size` comes from the array, `Price` (`10 | 12 | 14 | 16`) from the table, and `satisfies Record<Size, number>` guarantees the table covers every size."),
        ("A typed property read",
         r"""
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
function pluck<T, K extends keyof T>(rows: readonly T[], key: K): T[K][] {
  return rows.map((r) => r[key]);
}

const rows = [
  { name: "ana", age: 31, admin: true },
  { name: "bo", age: 25, admin: false },
];
const ages = pluck(rows, "age");     // number[]
const names = pluck(rows, "name");   // string[]
console.log(ages.reduce((a, b) => a + b, 0), names.join(","));
console.log(get({ name: "cy", age: 40, admin: true }, "admin"));
""", [""],
         "The return type follows the key: `pluck(rows, \"age\")` is `number[]`, so `reduce` adds numbers. A key that isn't on the row type is a compile error, not an `undefined` column."),
        ("Tuple positions",
         r"""
type Entry = [name: string, score: number, passed: boolean];
type Score = Entry[1];
type Cell = Entry[number];

const entries: Entry[] = [["ana", 91, true], ["bo", 48, false]];
const best: Score = Math.max(...entries.map((e) => e[1]));
const cells: Cell[] = entries.flat();
console.log(best, cells.length, cells.filter((c) => typeof c === "boolean").length);
""", [""],
         "A literal index picks one position of a tuple (`Entry[1]` is `number`); `[number]` is the union of all of them (`string | number | boolean`)."),
    ],
    errors=[
        (2339, r"""
type User = { id: number; email: string };
type Phone = User["phone"];
""", "Indexed access is checked like property access: `User` has no `phone`, so there is no type to look up."),
        (7053, r"""
const PRICES = { apple: 1.2, pear: 0.8 };
function price(fruit: string): number {
  return PRICES[fruit];
}
""", "Any `string` might not be a key of `PRICES`, so the lookup would be `any`. Type the parameter as `keyof typeof PRICES` and the lookup is exact."),
        (2536, r"""
type ValueAt<T, K> = T[K];
""", "An unconstrained `K` could be anything, so `T[K]` has no meaning yet. Constrain it: `type ValueAt<T, K extends keyof T> = T[K];` — the same fix as for a generic function, `<T, K extends keyof T>(obj: T, key: K)`."),
    ],
    pitfalls=[
        ("A lookup table keyed by any string",
         r"""
const PRICES: Record<string, number> = { apple: 1.2, pear: 0.8 };
const basket = ["apple", "aple", "pear"];
const total = basket.reduce((sum, f) => sum + (PRICES[f] as number), 0);
console.log("total " + total);
""",
         (r"""
const PRICES = { apple: 1.2, pear: 0.8 } as const;
type Fruit = keyof typeof PRICES;
const basket: Fruit[] = ["apple", "aple", "pear"];
const total = basket.reduce((sum, f) => sum + PRICES[f], 0);
console.log("total " + total);
""", 2820),
         "`Record<string, number>` accepts every string, so the typo reaches runtime and the total is `NaN`. Deriving the key type from the table turns the typo into a compile error."),
        ("`Object.keys` cast to `keyof T`",
         r"""
type Point = { x: number; y: number };
function sum(p: Point): number {
  let total = 0;
  for (const k of Object.keys(p) as (keyof Point)[]) total += p[k];
  return total;
}
const withLabel = { x: 1, y: 2, label: "A" };
console.log(sum(withLabel));
""",
         r"""
type Point = { x: number; y: number };
const POINT_KEYS = ["x", "y"] as const satisfies readonly (keyof Point)[];
function sum(p: Point): number {
  let total = 0;
  for (const k of POINT_KEYS) total += p[k];
  return total;
}
const withLabel = { x: 1, y: 2, label: "A" };
console.log(sum(withLabel));
""",
         "Structural typing let an object with an extra `label` in, and `Object.keys` found it: `3` + `\"A\"` became `\"3A\"`. `Object.keys` returns `string[]` on purpose; iterate a list of the keys you mean."),
        ("An optional property's lookup includes `undefined`",
         r"""
type Settings = { theme: string; fontSize?: number };
type FontSize = Settings["fontSize"];
function describe(size: FontSize): string {
  return "font " + size + "px";
}
console.log(describe(undefined));
""",
         r"""
type Settings = { theme: string; fontSize?: number };
type FontSize = NonNullable<Settings["fontSize"]>;
function describe(size: FontSize): string {
  return "font " + size + "px";
}
console.log(describe(14));
""",
         "`Settings[\"fontSize\"]` is `number | undefined`, because the property is optional — so `describe(undefined)` compiles and prints `undefinedpx`. `NonNullable<…>` strips it when you need the value itself."),
    ],
    later=[
        "**Week 20 — Mapped types.** `{ [K in keyof T]: T[K] }` — a lookup for every key at once.",
        "**Week 21 — Conditional types.** `T extends readonly (infer E)[] ? E : never` generalises `T[number]`.",
        "**Week 22 — Recursive types.** `Paths<T>` and a typed `get(obj, \"a.b.c\")` built from repeated lookups.",
    ],
    exercises=[
        _drill("ts_lookup_types-sizes", "A union from a list of values",
               "`SIZES` is the single source of truth. Replace `____` with the type of one of its elements, so `isSize` narrows an input to exactly those sizes.",
               r"""
import * as fs from "fs";
const SIZES = ["S", "M", "L", "XL"] as const;
type Size = (typeof SIZES)[number];
const isSize = (s: string): s is Size => SIZES.some((x) => x === s);
for (const t of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  console.log(isSize(t) ? `${t}: size ${SIZES.indexOf(t) + 1} of ${SIZES.length}` : `${t}: not a size`);
}
""", ["(typeof SIZES)[number]"],
               ["M XL S", "XXL m", "L"],
               hint="`typeof SIZES` is a readonly tuple; index it with `number`."),
        _drill("ts_lookup_types-pluck", "A column of a table",
               "Replace `____` with the return type of `pluck` so the result's type follows the key.",
               r"""
import * as fs from "fs";
function pluck<T, K extends keyof T>(rows: readonly T[], key: K): T[K][] {
  return rows.map((r) => r[key]);
}
type Row = { name: string; score: number };
const rows: Row[] = fs.readFileSync(0, "utf8").trim().split("\n").map((line) => {
  const [name = "", score = "0"] = line.trim().split(/\s+/);
  return { name, score: Number(score) };
});
const scores = pluck(rows, "score");
console.log(pluck(rows, "name").join(","));
console.log(scores.reduce((a, b) => a + b, 0) / scores.length);
""", ["T[K][]"],
               ["ana 90\nbo 70", "cy 55"],
               hint="An array of the value type at key `K` of `T`."),
        _chal("ts_lookup_types-limits", "Plans from one table", "Medium",
              "Declare `const LIMITS = { free: { projects: 3, seats: 1 }, pro: { projects: 50, seats: 5 }, team: { projects: 500, seats: 50 } } as const`, and derive `Plan` and `Resource` (`\"projects\" | \"seats\"`) from it. Each input line is `<plan> <resource> <used>`. Print `<plan> <resource>: <used>/<limit> ok`, `… over by <n>`, `unknown plan <p>` or `unknown resource <r>`.",
              r"""
const LIMITS = {
  free: { projects: 3, seats: 1 },
  pro: { projects: 50, seats: 5 },
  team: { projects: 500, seats: 50 },
} as const;
type Plan = keyof typeof LIMITS;
type Resource = keyof (typeof LIMITS)[Plan];
const isPlan = (s: string): s is Plan => Object.hasOwn(LIMITS, s);
const isResource = (s: string): s is Resource => s === "projects" || s === "seats";
for (const line of input.split("\n")) {
  const [plan = "", resource = "", usedText = "0"] = line.trim().split(/\s+/);
  if (!isPlan(plan)) {
    console.log(`unknown plan ${plan}`);
    continue;
  }
  if (!isResource(resource)) {
    console.log(`unknown resource ${resource}`);
    continue;
  }
  const limit = LIMITS[plan][resource];
  const used = Number(usedText);
  console.log(`${plan} ${resource}: ${used}/${limit} ${used <= limit ? "ok" : `over by ${used - limit}`}`);
}
""", ["free projects 2\nfree seats 3\npro projects 50\nteam cpu 1\ngold seats 1", "team seats 51"],
              hint="`keyof (typeof LIMITS)[Plan]` is the keys every plan's limits share."),
    ],
    quiz=[
        _cq("`type U = { tags: string[] }`. What is `U[\"tags\"][number]`?",
            "`string`", ["`string[]`", "`number`", "`never`"],
            "`U[\"tags\"]` is `string[]`; indexing an array type by `number` gives its element type."),
        _cq("`const S = [\"a\", \"b\"] as const; type T = (typeof S)[number];` — `T` is?",
            "`\"a\" | \"b\"`", ["`string`", "`readonly [\"a\", \"b\"]`", "`number`"],
            "`as const` keeps the literals; `[number]` unions the tuple's elements."),
        _cq("What does `User[\"id\" | \"email\"]` give?",
            "The union of both properties' types", ["A tuple of both", "An error — keys must be single", "`never`"],
            "Indexing with a union key distributes over it."),
        _cq("Why does `Object.keys(obj)` return `string[]` and not `(keyof T)[]`?",
            "At runtime an object can have more keys than its type lists",
            ["It is a TypeScript bug", "Symbols are excluded", "For performance"],
            "Structural typing admits objects with extra properties, so `keyof T` would be a lie."),
        _cq("What is `keyof { [k: string]: number }`?",
            "`string | number`", ["`string`", "`never`", "`PropertyKey`"],
            "Numeric keys are allowed on a string index signature (they become strings at runtime)."),
        _cq("`function get<T, K extends keyof T>(o: T, k: K)` — what should it return?",
            "`T[K]`", ["`T`", "`unknown`", "`keyof T`"],
            "The indexed access type follows the specific key passed in."),
    ],
    interview=[
        ("What is an indexed access type?",
         "`T[K]` — the type of property `K` of `T`, written like a property access but in type space. `User[\"email\"]`, `Row[number]` for an array's elements, `Tuple[0]` for a position, and a union key gives a union. It's how you derive related types from one declaration instead of repeating them."),
        ("How would you get a union type from a constant array?",
         "`const X = [\"a\", \"b\"] as const; type X = (typeof X)[number];` — `as const` keeps the literals as a readonly tuple, `typeof` brings the value into type space, and `[number]` unions its elements."),
        ("Why isn't `Object.keys` typed as `(keyof T)[]`?",
         "Because TypeScript's types are structural: a value of type `{ x: number }` can have extra properties at runtime, so claiming the keys are only `\"x\"` would be unsound. If you need to iterate known keys, keep an explicit list of them."),
    ],
)


_chapter(
    "ts_key_remapping", "TS: Generics & Type-Level",
    "Key Remapping in Mapped Types",
    "The `as` clause in a mapped type: rename keys (`getName`), drop keys by mapping them to `never`, and build keys from template literals — the type-level half of every getter, setter, event and API wrapper generator.",
    "A mapped type `{ [K in keyof T]: … }` keeps `T`'s keys. Add `as` and you choose the new key for each: `` [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] `` turns `{ name: string }` into `{ getName: () => string }`, and mapping a key to `never` removes it. The result is still tied to `T` — change the model and the derived API changes with it.",
    "Java generates this kind of boilerplate with annotation processors or Lombok, at build time. TypeScript describes it in the type system: the runtime code that creates `getName` is written once, generically, and the mapped type tells the compiler exactly which methods exist.",
    why=r"""
A lot of code is a *transformation* of some other shape. For a `User` model you
write getters, then setters, then a `UserChanged` event per field, then a form
state with an error per field. Written by hand, each of those is a second copy of
`User` that must be kept in step.

Mapped types (week 20) already let you derive `{ [K in keyof User]: … }` — the
same keys with new value types. But getters aren't called `name`; they're called
`getName`. Event handlers aren't `click`; they're `onClick`. And a snapshot for
logging should drop the methods entirely. Key remapping is the missing piece:
the key itself becomes something you compute.
""",
    idea=r"""
**The `as` clause** sits after `in keyof T` and gives each key its new name:

```ts
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
type G = Getters<{ name: string; age: number }>;
// { getName: () => string; getAge: () => number }
```

- `string & K` is needed because `keyof T` can include `number` and `symbol`
  keys, and `Capitalize` only takes strings. The intersection keeps just the
  string keys (a `number | symbol` key becomes `never` and disappears).
- Template literal types (week 22 goes deeper) build the new name; `Capitalize`,
  `Uncapitalize`, `Uppercase` and `Lowercase` are built in.
- The value side can still use `T[K]` — `K` is the *original* key.

**Mapping to `never` filters.** A key renamed to `never` is dropped:

```ts
type DataOnly<T> = {
  [K in keyof T as T[K] extends (...args: never[]) => unknown ? never : K]: T[K];
};
type OmitByName<T, Bad> = { [K in keyof T as K extends Bad ? never : K]: T[K] };
```

This is the general form of `Omit` — keyed on anything you can test, including
the property's *value* type.

**Modifiers survive.** A mapped type over `keyof T` keeps each property's
`readonly` and `?`, with or without `as`, so `Getters` of an optional property is
still optional unless you add `-?`.

**Types describe; code must match.** A remapped type is only a claim about an
object. The function that builds the object at runtime has to compute the same
keys — `"get" + key[0].toUpperCase() + key.slice(1)` — and usually needs one
cast at the end, because the compiler can't follow string manipulation. Keep
that function small and test it.
""",
    examples=[
        ("Getters, derived and built",
         r"""
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: Record<string, () => unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    out["get" + key.charAt(0).toUpperCase() + key.slice(1)] = () => value;
  }
  return out as Getters<T>;
}

const user = makeGetters({ name: "ana", age: 31, admin: true });
console.log(user.getName().toUpperCase());
console.log(user.getAge() + 1);
console.log(user.getAdmin() ? "admin" : "member");
""", [""],
         "`user.getAge()` is typed `number`, so `+ 1` is arithmetic. The one cast lives in `makeGetters`, where the runtime key computation mirrors the type's template literal exactly."),
        ("Dropping keys by value type",
         r"""
type DataOnly<T> = {
  [K in keyof T as T[K] extends (...args: never[]) => unknown ? never : K]: T[K];
};

function snapshot<T extends object>(obj: T): DataOnly<T> {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => typeof v !== "function")) as DataOnly<T>;
}

const counter = {
  count: 3,
  label: "clicks",
  increment() {
    this.count++;
  },
};
counter.increment();
const saved = snapshot(counter);   // { count: number; label: string }
console.log(JSON.stringify(saved));
console.log(saved.count * 10);
""", [""],
         "Mapping `increment` to `never` removes it from the type; filtering functions out of the entries removes it at runtime. `saved.increment()` would now be a compile error — matching the object you actually have."),
        ("Event handlers named from events",
         r"""
type Events = { open: { path: string }; close: { code: number }; error: { message: string } };
type Handlers<E> = {
  [K in keyof E as `on${Capitalize<string & K>}`]?: (payload: E[K]) => string;
};

function emit<K extends keyof Events>(handlers: Handlers<Events>, name: K, payload: Events[K]): string {
  const key = "on" + name.charAt(0).toUpperCase() + name.slice(1);
  const handler = (handlers as Record<string, ((p: Events[K]) => string) | undefined>)[key];
  return handler === undefined ? `(no handler for ${name})` : handler(payload);
}

const handlers: Handlers<Events> = {
  onOpen: (p) => "opened " + p.path,
  onClose: (p) => "closed with " + p.code,
};
console.log(emit(handlers, "open", { path: "/tmp/a" }));
console.log(emit(handlers, "close", { code: 0 }));
console.log(emit(handlers, "error", { message: "disk" }));
""", [""],
         "`onOpen`'s parameter is inferred as `{ path: string }` from `Events[\"open\"]` — no annotation needed. Rename an event in `Events` and the handler object stops compiling until it's renamed too."),
    ],
    errors=[
        (2344, r"""
type Getters<T> = {
  [K in keyof T as `get${Capitalize<K>}`]: () => T[K];
};
""", "`keyof T` may include `number` and `symbol` keys, and `Capitalize` needs a string. Intersect: `Capitalize<string & K>`."),
        (2551, r"""
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
declare const g: Getters<{ firstName: string }>;
g.getFirstname();
""", "The remapped key is `getFirstName` — `Capitalize` only touches the first letter; the rest of the key is kept exactly. The compiler has computed the real name and suggests it."),
    ],
    pitfalls=[
        ("The type drops a key the object still has",
         r"""
type User = { name: string; password: string };
type Public<T> = { [K in keyof T as K extends "password" ? never : K]: T[K] };
const user: User = { name: "ana", password: "hunter2" };
const shown: Public<User> = user;
console.log(JSON.stringify(shown));
""",
         r"""
type User = { name: string; password: string };
type Public<T> = { [K in keyof T as K extends "password" ? never : K]: T[K] };
const user: User = { name: "ana", password: "hunter2" };
const { password: _hidden, ...shown }: User = user;
const safe: Public<User> = shown;
console.log(JSON.stringify(safe));
""",
         "A remapped type is a view, not an operation: `Public<User>` hides `password` from the compiler, but assigning `user` to it keeps the very same object. Remove the key at runtime (rest destructuring), then give the result the type."),
        ("Type and runtime disagree about the name",
         r"""
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: Record<string, () => unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const camel = key.replace(/_(\w)/g, (_, c: string) => c.toUpperCase());
    out["get" + camel.charAt(0).toUpperCase() + camel.slice(1)] = () => value;
  }
  return out as Getters<T>;
}
const row = makeGetters({ first_name: "ana" });
console.log(typeof row.getFirst_name === "function" ? row.getFirst_name() : "no such getter at runtime");
""",
         r"""
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: Record<string, () => unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    out["get" + key.charAt(0).toUpperCase() + key.slice(1)] = () => value;
  }
  return out as Getters<T>;
}
const row = makeGetters({ first_name: "ana" });
console.log(typeof row.getFirst_name === "function" ? row.getFirst_name() : "no such getter at runtime");
""",
         "The type says `getFirst_name`; the runtime also camel-cased the key and created `getFirstName`. The cast in `makeGetters` hid the mismatch. The runtime key computation must follow the type's rule exactly — that function is where the bugs live."),
        ("Forgetting `string &`",
         (r"""
type Setters<T> = { [K in keyof T as `set${Capitalize<K>}`]: (value: T[K]) => void };
const state = { theme: "dark" };
const setters: Setters<typeof state> = { setTheme: (v) => { state.theme = v; } };
setters.setTheme("light");
console.log(state.theme);
""", 2344),
         r"""
type Setters<T> = { [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void };
const state = { theme: "dark" };
const setters: Setters<typeof state> = { setTheme: (v) => { state.theme = v; } };
setters.setTheme("light");
console.log(state.theme);
""",
         "Even when every actual key is a string, `keyof T` for a generic `T` is `string | number | symbol` as far as the definition knows. `string & K` is the idiom."),
    ],
    later=[
        "**Week 21 — Conditional types.** The `T[K] extends … ? never : K` test inside the `as` clause, in general.",
        "**Week 22 — Template literal types.** Building and *parsing* key names: `CamelCase<\"first_name\">`.",
        "**Week 23 — Classes.** Accessors (`get name()`) — the runtime feature these getter types often describe.",
    ],
    exercises=[
        _drill("ts_key_remapping-setters", "Setters from a state shape",
               "Replace `____` with the `as` clause that renames each key `K` to `set` + the capitalised key, so `setters.setVolume` and `setters.setMuted` exist and take the right value types.",
               r"""
import * as fs from "fs";
type Setters<T> = { [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void };
const state = { volume: 5, muted: false };
const setters: Setters<typeof state> = {
  setVolume: (v) => {
    state.volume = Math.max(0, Math.min(10, v));
  },
  setMuted: (m) => {
    state.muted = m;
  },
};
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [cmd = "", arg = ""] = line.trim().split(/\s+/);
  if (cmd === "volume") setters.setVolume(Number(arg));
  else if (cmd === "mute") setters.setMuted(arg === "on");
  console.log(`volume ${state.volume}${state.muted ? " (muted)" : ""}`);
}
""", ["as `set${Capitalize<string & K>}`"],
               ["volume 7\nmute on\nvolume 12", "mute off", "volume -3\nmute on\nmute off"],
               hint="`as` followed by a template literal type; remember `string & K`."),
        _drill("ts_key_remapping-getters", "Build the getters at runtime",
               "The type `Getters<T>` is given. Replace `____` with the runtime key that matches it: `get` followed by the key with its first letter upper-cased.",
               r"""
import * as fs from "fs";
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: Record<string, () => unknown> = {};
  for (const [key, value] of Object.entries(obj)) out["get" + key.charAt(0).toUpperCase() + key.slice(1)] = () => value;
  return out as Getters<T>;
}
const [name = "", city = "", visits = "0"] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const profile = makeGetters({ name, city, visits: Number(visits) });
console.log(`${profile.getName()} from ${profile.getCity()}, visit ${profile.getVisits() + 1}`);
console.log(Object.keys(profile).join(","));
""", ['"get" + key.charAt(0).toUpperCase() + key.slice(1)'],
               ["ana oslo 3", "bo rome 0"],
               hint="`charAt(0).toUpperCase()` for the first letter, then the rest unchanged."),
        _chal("ts_key_remapping-emitter", "A typed event emitter", "Hard",
              "Events are `type Events = { join: { user: string }; leave: { user: string; reason: string }; message: { user: string; text: string } }`. Build `Handlers<E>` with keys `on<Event>` and register handlers for all three. Each input line is `<event> <user> [rest…]` (for `leave` the rest is the reason, for `message` the text). Dispatch it and print the handler's result — `+ <user>`, `- <user> (<reason>)`, `<user>: <text>` — or `unknown event <e>`. Finish with `<n> online` (joins minus leaves).",
              r"""
type Events = { join: { user: string }; leave: { user: string; reason: string }; message: { user: string; text: string } };
type Handlers<E> = { [K in keyof E as `on${Capitalize<string & K>}`]: (payload: E[K]) => string };
let online = 0;
const handlers: Handlers<Events> = {
  onJoin: (p) => {
    online++;
    return `+ ${p.user}`;
  },
  onLeave: (p) => {
    online--;
    return `- ${p.user} (${p.reason})`;
  },
  onMessage: (p) => `${p.user}: ${p.text}`,
};
for (const line of input.split("\n")) {
  const [event = "", user = "", ...rest] = line.trim().split(/\s+/);
  const text = rest.join(" ");
  if (event === "join") console.log(handlers.onJoin({ user }));
  else if (event === "leave") console.log(handlers.onLeave({ user, reason: text || "no reason" }));
  else if (event === "message") console.log(handlers.onMessage({ user, text }));
  else console.log(`unknown event ${event}`);
}
console.log(`${online} online`);
""", ["join ana\njoin bo\nmessage ana hello there\nleave bo timeout\nwave cy", "leave x\njoin y"],
              hint="The handler object's keys are checked against `Handlers<Events>` — a misspelt `onJion` won't compile."),
    ],
    quiz=[
        _cq("What does `as` do in `{ [K in keyof T as NewKey]: … }`?",
            "Chooses a new key for each property", ["Casts the value type", "Filters values at runtime", "Makes the key readonly"],
            "The `as` clause computes the output key from the input key `K`."),
        _cq("How do you remove a key in a mapped type?",
            "Map it to `never` in the `as` clause", ["Map its value to `never`", "Use `delete`", "Map it to `undefined`"],
            "A key of `never` produces no property. (A value of `never` would keep the key, with an unusable type.)"),
        _cq("Why write `Capitalize<string & K>` instead of `Capitalize<K>`?",
            "`keyof T` can include `number` and `symbol`, and `Capitalize` only accepts strings",
            ["`Capitalize` is lazy otherwise", "It converts numbers to strings", "It is required by `as` clauses"],
            "The intersection keeps only string keys."),
        _cq("What is `` `get${Capitalize<\"first_name\">}` ``?",
            "`\"getFirst_name\"`", ["`\"getFirstName\"`", "`\"getFIRST_NAME\"`", "`\"get_first_name\"`"],
            "`Capitalize` upper-cases only the first character."),
        _cq("Does `{ [K in keyof T as …]: T[K] }` keep `?` and `readonly` modifiers?",
            "Yes — it's still homomorphic over `keyof T`", ["No, `as` drops them", "Only `readonly`", "Only `?`"],
            "Add `-?` or `-readonly` to remove them explicitly."),
        _cq("A value is assigned to a remapped type that omits `password`. Is the password gone?",
            "No — types are erased; the object is unchanged", ["Yes, the compiler strips it", "Only in `JSON.stringify`", "Only with `strict`"],
            "Remove keys at runtime (rest destructuring), then type the result."),
    ],
    interview=[
        ("How would you type a function that turns an object into getters?",
         "With a mapped type that remaps keys: `{ [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] }`. The implementation builds the same keys at runtime and returns the object with one cast, since the compiler can't follow string manipulation — so that function needs a test."),
        ("How do you omit properties by their value type?",
         "Key remapping with a conditional: `{ [K in keyof T as T[K] extends Function ? never : K]: T[K] }`. Mapping a key to `never` drops it. That's a generalised `Omit` that can filter on anything, not just key names."),
        ("What's `string & K` for in mapped types?",
         "`keyof T` is `string | number | symbol` in general, and template literal types and `Capitalize` need strings. Intersecting with `string` keeps just the string keys, which is almost always what you want for generated names."),
    ],
)


_chapter(
    "ts_distributive", "TS: Generics & Type-Level",
    "Distributive Conditional Types",
    "Why a conditional type applied to a union runs once per member, how `[T] extends [U]` switches that off, why `never` goes in and `never` comes out, and how `infer U extends X` constrains what it captures.",
    "`T extends U ? X : Y` on a *naked* type parameter distributes: given `A | B` it evaluates for `A` and for `B` separately and unions the results. That is what makes `Exclude<T, U>` work — and what makes `ToArray<string | number>` come out as `string[] | number[]` rather than `(string | number)[]`. Wrapping both sides in a tuple, `[T] extends [U]`, evaluates the union as a whole. `never` is the empty union, so a distributive type given `never` returns `never` without evaluating either branch.",
    "Nothing in Java's type system computes, so there is no analogue. The closest intuition is `map` over a list: a distributive conditional type maps a type function over the members of a union.",
    why=r"""
Conditional types (week 21) are `if` statements on types. The surprise comes
when the input is a union. Write a helper that wraps a type in an array, give it
`string | number`, and you get `string[] | number[]` — an array of all strings
*or* all numbers, not a mixed array. Write `IsString<T>` and give it `never`,
and the answer is neither `true` nor `false` but `never`.

These aren't bugs; they're the rule that makes the standard library's
`Exclude`, `Extract` and `NonNullable` one line each. But if you don't know the
rule, it looks like the compiler is making things up. This chapter is the rule
and its two escape hatches.
""",
    idea=r"""
**The rule.** A conditional type `T extends U ? X : Y` whose checked type is a
*naked* type parameter (just `T`, not `T[]` or `[T]`) is **distributive**: when
`T` is instantiated with a union, the conditional is applied to each member
separately and the results are unioned.

```ts
type ToArray<T> = T extends unknown ? T[] : never;
type A = ToArray<string | number>;   // string[] | number[]

type MyExclude<T, U> = T extends U ? never : T;
type B = MyExclude<"a" | "b" | "c", "a">;   // "b" | "c"
```

`MyExclude` works *because* of distribution: each member either survives (`T`)
or vanishes (`never`, the empty union).

**Switching it off.** Put the checked type in a one-element tuple:

```ts
type ToArrayAll<T> = [T] extends [unknown] ? T[] : never;
type C = ToArrayAll<string | number>;   // (string | number)[]
```

`[T]` isn't a naked type parameter, so the union is checked as a whole.

**`never` is the empty union.** Distributing over zero members produces zero
results — `never` — without looking at either branch. So `IsString<never>` is
`never`, and a test for `never` itself must be non-distributive:
`type IsNever<T> = [T] extends [never] ? true : false`.

**`any` takes both branches.** `IsString<any>` is `true | false`, because `any`
is assignable to anything *and* anything is assignable to it.

**`infer` with a constraint.** `infer U extends X` captures a type only if it
fits `X` — the branch is taken only then, and `U` is known to be an `X`:

```ts
type FirstNumber<T> = T extends [infer H extends number, ...unknown[]] ? H : never;
type D = FirstNumber<[42, "x"]>;   // 42
type E = FirstNumber<["x", 42]>;   // never
```

**Distribution at runtime?** There is none — types are erased. What the rule
changes is which *values* the compiler accepts: `ToArray<string | number>`
rejects `[1, "a"]`, and `ToArrayAll` accepts it.
""",
    examples=[
        ("One array type per member",
         r"""
type ToArray<T> = T extends unknown ? T[] : never;
type ToArrayAll<T> = [T] extends [unknown] ? T[] : never;

const perMember: ToArray<string | number>[] = [["a", "b"], [1, 2, 3]];   // each all-strings or all-numbers
const mixed: ToArrayAll<string | number> = ["a", 1, "b", 2];            // one mixed array

for (const arr of perMember) console.log(arr.length, typeof arr[0]);
console.log(mixed.map((x) => typeof x).join(","));
""", [""],
         "`ToArray<string | number>` is `string[] | number[]`, so a mixed array would be rejected there; `ToArrayAll` checks the union as a whole and gives `(string | number)[]`."),
        ("`Exclude` and `Extract` are one line each",
         r"""
type MyExclude<T, U> = T extends U ? never : T;
type MyExtract<T, U> = T extends U ? T : never;

type Event = "click" | "keydown" | "keyup" | "scroll";
type KeyEvent = MyExtract<Event, `key${string}`>;
type OtherEvent = MyExclude<Event, KeyEvent>;

const keys: KeyEvent[] = ["keydown", "keyup"];
const others: OtherEvent[] = ["click", "scroll"];
console.log(keys.join(" "), "|", others.join(" "));
""", [""],
         "Each member of `Event` is tested against the pattern on its own; the ones that fail become `never` and vanish from the union. The template literal `` `key${string}` `` matches any string starting with `key`."),
        ("`never` goes in, `never` comes out",
         r"""
type IsString<T> = T extends string ? "yes" : "no";
type IsNever<T> = [T] extends [never] ? true : false;

function assertNever(value: never): never {
  throw new Error("unhandled: " + JSON.stringify(value));
}
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };
function area(s: Shape): number {
  if (s.kind === "circle") return Math.round(3.14159 * s.r * s.r);
  if (s.kind === "square") return s.side * s.side;
  return assertNever(s);
}

const neverCheck: IsNever<never> = true;
const stringCheck: IsString<"a"> = "yes";
console.log(area({ kind: "circle", r: 2 }), area({ kind: "square", side: 3 }), neverCheck, stringCheck);
""", [""],
         "`IsString<never>` would be `never` (no members, no results). `IsNever` wraps both sides in tuples to test `never` itself. In `area`, the leftover `s` is `never` because every union member was handled."),
        ("`infer … extends` captures only what fits",
         r"""
type FirstNumber<T> = T extends readonly [infer H extends number, ...unknown[]] ? H : never;
type LastString<T> = T extends readonly [...unknown[], infer L extends string] ? L : never;

const row = [7, "x", "tail"] as const;
const first: FirstNumber<typeof row> = 7;
const last: LastString<typeof row> = "tail";
console.log(first * 6, last.toUpperCase());
""", [""],
         "`H` is captured only if it is a `number`, so inside the true branch it's known to be one. With `row` starting with a string, `FirstNumber` would be `never` and `const first` could hold nothing."),
    ],
    errors=[
        (2322, r"""
type ToArray<T> = T extends unknown ? T[] : never;
const mixed: ToArray<string | number> = [1, "a"];
""", "Distribution made the type `string[] | number[]`: all strings or all numbers. A mixed array fits neither. Use `[T] extends [unknown]` if a mixed array is what you meant."),
        (2345, r"""
function assertNever(value: never): never {
  throw new Error(String(value));
}
function label(v: string | number | boolean): string {
  if (typeof v === "string") return "text";
  if (typeof v === "number") return "number";
  return assertNever(v);
}
""", "After two checks, `v` is still `boolean` — not `never` — so a case is missing. Exhaustiveness checks are distribution's `never` behaviour put to work."),
    ],
    pitfalls=[
        ("A wrapper that distributes when you didn't want it to",
         (r"""
type Boxed<T> = T extends unknown ? { value: T } : never;
function box(v: string | number): Boxed<string | number> {
  return { value: v };
}
console.log(JSON.stringify(box(1)), JSON.stringify(box("a")));
""", 2322),
         r"""
type Boxed<T> = [T] extends [unknown] ? { value: T } : never;
function box(v: string | number): Boxed<string | number> {
  return { value: v };
}
console.log(JSON.stringify(box(1)), JSON.stringify(box("a")));
""",
         "Distributed, `Boxed<string | number>` is `{ value: string } | { value: number }`, and an object whose `value` is `string | number` fits neither member. Wrapped in a tuple, it's `{ value: string | number }`."),
        ("A test that returns `never` for `never`",
         (r"""
type Describe<T> = T extends string ? "text" : "other";
function describeNothing(): Describe<never> {
  return "other";
}
console.log(describeNothing());
""", 2322),
         r"""
type Describe<T> = [T] extends [never] ? "nothing" : T extends string ? "text" : "other";
function describeNothing(): Describe<never> {
  return "nothing";
}
console.log(describeNothing());
""",
         "Distributing over the empty union gives the empty union: `Describe<never>` is `never`, so no value can be returned. Check for `never` first, non-distributively."),
        ("`ReturnType` of an overloaded function",
         (r"""
function parse(text: string): number;
function parse(text: number): string;
function parse(text: string | number): string | number {
  return typeof text === "string" ? Number(text) : String(text);
}
type Parsed = ReturnType<typeof parse>;
const n: Parsed = parse("5");
console.log(n);
""", 2322),
         r"""
function parse(text: string): number;
function parse(text: number): string;
function parse(text: string | number): string | number {
  return typeof text === "string" ? Number(text) : String(text);
}
const n = parse("5");
console.log(n + 1);
""",
         "`infer` on an overloaded function sees only the *last* overload, so `ReturnType<typeof parse>` is `string`. Let the call site infer, or pull the overload you want out explicitly."),
    ],
    later=[
        "**Week 22 — Template literal and recursive types.** Distribution over string unions builds every combination — and can explode.",
        "**Week 25 — `Result`.** `Extract<R, { ok: true }>` pulls the success member out of a result union.",
    ],
    exercises=[
        _drill("ts_distributive-flatten", "Flatten one level",
               "`Flatten<T>` is the element type if `T` is an array, otherwise `T` itself. Replace `____` with the conditional type so `flattenOnce` type-checks.",
               r"""
import * as fs from "fs";
type Flatten<T> = T extends readonly (infer E)[] ? E : T;
function flattenOnce<T>(items: readonly T[]): Flatten<T>[] {
  const out: unknown[] = [];
  for (const item of items) {
    if (Array.isArray(item)) out.push(...item);
    else out.push(item);
  }
  return out as Flatten<T>[];
}
const parsed: (number | number[])[] = fs.readFileSync(0, "utf8").trim().split(/\s+/)
  .map((t) => (t.includes(",") ? t.split(",").map(Number) : Number(t)));
const flat: number[] = flattenOnce(parsed);
console.log(flat.join(" "), "sum", flat.reduce((a, b) => a + b, 0));
""", ["T extends readonly (infer E)[] ? E : T"],
               ["1 2,3 4", "5,6,7", "9"],
               hint="`infer E` inside `readonly (infer E)[]` captures the element type."),
        _drill("ts_distributive-never", "Prove every case is handled",
               "`assertNever` only accepts `never`. Replace `____` so the last line of `describe` passes the leftover value to it — which compiles only because every `kind` is handled above.",
               r"""
import * as fs from "fs";
function assertNever(value: never): never {
  throw new Error("unhandled " + String(value));
}
type Cmd = { kind: "add"; n: number } | { kind: "sub"; n: number } | { kind: "reset" };
function apply(total: number, c: Cmd): number {
  if (c.kind === "add") return total + c.n;
  if (c.kind === "sub") return total - c.n;
  if (c.kind === "reset") return 0;
  return assertNever(c);
}
const cmds: Cmd[] = fs.readFileSync(0, "utf8").trim().split("\n").map((line) => {
  const [k = "", n = "0"] = line.trim().split(/\s+/);
  return k === "add" || k === "sub" ? { kind: k, n: Number(n) } : { kind: "reset" };
});
console.log(cmds.reduce(apply, 0));
""", ["return assertNever(c);"],
               ["add 5\nsub 2\nadd 10", "add 3\nreset\nadd 1", "sub 4"],
               hint="After the three checks, `c` is `never`."),
        _chal("ts_distributive-partition", "Split a union of results", "Medium",
              "Each input line is `ok <number>` or `err <message…>`. Parse into `type Result = { ok: true; value: number } | { ok: false; error: string }`, then use `Extract<Result, { ok: true }>` and `Extract<Result, { ok: false }>` to type two arrays filled with type predicates. Print `values: <v…>` (or `values: none`), `sum: <s>`, and each error as `error: <message>`.",
              r"""
type Result = { ok: true; value: number } | { ok: false; error: string };
type Ok = Extract<Result, { ok: true }>;
type Err = Extract<Result, { ok: false }>;
const results: Result[] = input.split("\n").map((line) => {
  const [tag = "", ...rest] = line.trim().split(/\s+/);
  return tag === "ok" ? { ok: true, value: Number(rest[0]) } : { ok: false, error: rest.join(" ") };
});
const oks: Ok[] = results.filter((r): r is Ok => r.ok);
const errs: Err[] = results.filter((r): r is Err => !r.ok);
console.log(`values: ${oks.map((r) => r.value).join(" ") || "none"}`);
console.log(`sum: ${oks.reduce((s, r) => s + r.value, 0)}`);
for (const e of errs) console.log(`error: ${e.error}`);
""", ["ok 3\nerr disk full\nok 4\nerr timeout", "err only one"],
              hint="`Extract` distributes over the union and keeps the members that match the pattern."),
    ],
    quiz=[
        _cq("`type F<T> = T extends unknown ? T[] : never`. What is `F<string | number>`?",
            "`string[] | number[]`", ["`(string | number)[]`", "`never`", "`unknown[]`"],
            "A naked type parameter distributes over the union."),
        _cq("How do you stop a conditional type from distributing?",
            "Wrap both sides in a tuple: `[T] extends [U]`",
            ["Use `infer`", "Add `readonly`", "Use `NoInfer<T>`"],
            "`[T]` isn't a naked type parameter, so the union is checked as a whole."),
        _cq("A distributive conditional type is given `never`. The result is?",
            "`never`", ["The true branch", "The false branch", "`unknown`"],
            "`never` is the empty union: zero members, zero results."),
        _cq("How is `IsNever<T>` written?",
            "`[T] extends [never] ? true : false`", ["`T extends never ? true : false`", "`T extends unknown ? false : true`", "`never extends T ? true : false`"],
            "The distributive version would return `never` for `never`."),
        _cq("What does `infer U extends string` do?",
            "Captures `U` only if it is a `string`, and types it as one in the true branch",
            ["Converts `U` to a string", "Makes `U` a string at runtime", "Nothing different from `infer U`"],
            "The constraint is part of the match (TS 4.7+)."),
        _cq("Why is `Exclude<\"a\" | \"b\", \"a\">` equal to `\"b\"`?",
            "Each member is tested; `\"a\"` becomes `never` and vanishes from the union",
            ["`Exclude` sorts the union", "String literals are compared by length", "It's a special case in the compiler"],
            "`type Exclude<T, U> = T extends U ? never : T` — distribution does the work."),
    ],
    interview=[
        ("What is a distributive conditional type?",
         "A conditional type whose checked type is a bare type parameter. When that parameter is a union, the conditional is applied to each member and the results are unioned — which is how `Exclude`, `Extract` and `NonNullable` work. Wrapping in a tuple, `[T] extends [U]`, turns distribution off."),
        ("Why does `IsString<never>` give `never`?",
         "`never` is the empty union, and distribution over an empty union produces no results — so the answer is `never` without either branch being evaluated. To test for `never` you have to check non-distributively: `[T] extends [never]`."),
        ("How would you write `IsUnion<T>`?",
         "Compare the distributed and undistributed forms: `type IsUnion<T, U = T> = T extends unknown ? ([U] extends [T] ? false : true) : never`. Inside the distributive branch `T` is one member while `U` is still the whole union, so they differ exactly when there was more than one member."),
    ],
)


_chapter(
    "ts_type_performance", "TS: Generics & Type-Level",
    "Type-Level Performance & Limits",
    "Where type-level programming stops: recursion depth and TS2589, tail-recursive conditional types, unions that explode, recursion on plain `string` — and when to stop being clever.",
    "The type checker runs your type-level code, and it has limits: a non-tail-recursive conditional type gives up after a few dozen levels of instantiation with TS2589 (\"excessively deep and possibly infinite\"); a tail-recursive one (whose recursive call is the whole branch) can go to 1,000. A union past 100,000 members is TS2590. And a type that parses string literals falls back to plain `string` for a plain `string` input — it has nothing to parse.",
    "Java's type checker doesn't run programs, so it has no such limits — and no such power. The trade-off in TypeScript is the same as with any runtime: an algorithm that is fine for ten items can time out at ten thousand, and a type that is fine for a small union can stall the editor.",
    why=r"""
The last few weeks turned the type system into a programming language: it
branches (conditional types), loops (recursion), pattern-matches (`infer`) and
builds strings (template literals). Like any language it has a runtime — the
type checker — and that runtime has resource limits.

You'll meet them in two ways. Loudly, as an error: "Type instantiation is
excessively deep and possibly infinite." Or quietly, as an editor that takes
seconds to show a hover, and a build that got slower one clever type at a time.
Knowing where the limits are — and the handful of techniques that keep types
cheap — lets you use type-level code where it earns its keep and stop before it
becomes the problem.
""",
    idea=r"""
**Recursion depth.** Every recursive step of a conditional type is an
instantiation, and the checker caps how deep it will go. A recursive type whose
recursive call is *wrapped* in something — `[0, ...Build<N, …>]` — stops at a
depth of a few dozen levels (the 80-deep pitfall below already fails) with **TS2589**.

**Tail recursion goes further.** When the recursive reference *is* the whole
branch — nothing wrapped around it — the checker evaluates it in a loop, up to
1,000 iterations (TS 4.5+). The trick is the same as in runtime code: carry the
result in an accumulator parameter.

```ts
// wrapped: fails after a few dozen levels
type BuildWrapped<N extends number, T extends unknown[] = []> =
  T["length"] extends N ? [] : [0, ...BuildWrapped<N, [...T, 0]>];
// tail-recursive: fine to 999
type Build<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : Build<N, [...Acc, 0]>;
```

**Unions multiply.** A template literal with union placeholders produces every
combination: five 10-member unions make 100,000 members. Past 100,000 the
checker refuses with **TS2590**. Use a pattern type (`` `${number}` ``,
`` `#${string}` ``) instead of enumerating.

**Recursion on non-literals.** A type that parses a string, like
`Split<S, " ">`, only works when `S` is a *literal*. Given plain `string` (a
value read at runtime), there is nothing to parse; decide explicitly what that
case returns — usually `string[]` — with a `string extends S ? … : …` check.

**Keeping types cheap.**

- Name intermediate types; the checker caches named instantiations.
- Prefer `interface … extends` to big intersections — interfaces are cached,
  intersections are recomputed.
- Constrain early (`K extends keyof T`) so the checker does less work per step.
- Type-level arithmetic with tuples is a toy: fine for tuple lengths, wrong for
  real numbers.

**When to stop.** A type is worth its complexity when it catches real mistakes
at the call sites of a widely used API — a router, a query builder, a typed
event bus. It is not worth it when a plain type and a runtime check would do,
or when nobody on the team can read it. `tsc --extendedDiagnostics` and
`--generateTrace` show where checking time goes.
""",
    examples=[
        ("Tail recursion with an accumulator",
         r"""
type Build<N extends number, Acc extends unknown[] = []> = Acc["length"] extends N ? Acc : Build<N, [...Acc, 0]>;
type Length<T extends readonly unknown[]> = T["length"];

type Hundred = Build<100>;
const size: Length<Hundred> = 100;
const zeros = Array.from({ length: size }, () => 0);
console.log(zeros.length, zeros.every((z) => z === 0));
""", [""],
         "`Build<100>` recurses 100 times — past the wrapped-recursion limit, but fine for a tail call. The result's `length` is the literal type `100`, so `const size: Length<Hundred> = 100` only accepts exactly 100."),
        ("A pattern instead of an enumeration",
         r"""
type Hex = `#${string}`;
type Percent = `${number}%`;

function parseColour(text: string): Hex | undefined {
  return /^#[0-9a-f]{6}$/i.test(text) ? (text.toLowerCase() as Hex) : undefined;
}
function scale(p: Percent, of: number): number {
  return (parseFloat(p) / 100) * of;
}
console.log(parseColour("#3355FF"), parseColour("blue"));
console.log(scale("25%", 80), scale("12.5%", 8));
""", [""],
         "Enumerating every hex colour as a union would be 16.7 million members; `` `#${string}` `` is one pattern type the checker handles instantly. Combine it with a runtime check for the exact format."),
        ("Parsing literals, with a fallback for `string`",
         r"""
type Split<S extends string> = string extends S
  ? string[]
  : S extends `${infer Head} ${infer Rest}`
    ? [Head, ...Split<Rest>]
    : [S];

function words<S extends string>(s: S): Split<S> {
  return s.split(" ") as Split<S>;
}

const known = words("red green blue");   // ["red", "green", "blue"]
const fromInput = words(["a", "b", "c"].join(" "));   // string[]
console.log(known[2].toUpperCase(), known.length);
console.log(fromInput.length, fromInput[1] ?? "-");
""", [""],
         "For a literal, `Split` computes the exact tuple, so `known[2]` is `\"blue\"`. For a runtime `string` it falls back to `string[]` — without the `string extends S` check it would claim a one-element tuple."),
    ],
    errors=[
        (2589, r"""
type BuildWrapped<N extends number, T extends unknown[] = []> =
  T["length"] extends N ? [] : [0, ...BuildWrapped<N, [...T, 0]>];
type Many = BuildWrapped<200>;
const m: Many = [];
""", "The recursive call is wrapped in a tuple spread, so it isn't a tail call and hits the depth limit. Carry the result in an accumulator and return the recursive call directly."),
        (2590, r"""
type Digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";
type Code = `${Digit}${Digit}${Digit}${Digit}${Digit}${Digit}`;
const c: Code = "123456";
""", "Six 10-member unions make a million combinations; the checker gives up past 100,000. Use `` `${number}` `` plus a runtime length check, or a branded string from a parser."),
    ],
    pitfalls=[
        ("Recursion that isn't a tail call",
         (r"""
type BuildWrapped<N extends number, T extends unknown[] = []> =
  T["length"] extends N ? [] : [0, ...BuildWrapped<N, [...T, 0]>];
const row: BuildWrapped<80>["length"] = 80;
console.log(row);
""", 2589),
         r"""
type Build<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : Build<N, [...Acc, 0]>;
const row: Build<80>["length"] = 80;
console.log(row);
""",
         "Same result, but the second form's recursive call is the entire branch, so the checker runs it as a loop."),
        ("A string parser given a plain `string`",
         (r"""
type Split<S extends string> = S extends `${infer Head} ${infer Rest}` ? [Head, ...Split<Rest>] : [S];
function words<S extends string>(s: S): Split<S> {
  return s.split(" ") as Split<S>;
}
const line: string = ["a", "b", "c"].join(" ");
const [first, second] = words(line);
console.log(first, second);
""", 2493),
         r"""
type Split<S extends string> = string extends S ? string[] : S extends `${infer Head} ${infer Rest}` ? [Head, ...Split<Rest>] : [S];
function words<S extends string>(s: S): Split<S> {
  return s.split(" ") as Split<S>;
}
const line: string = ["a", "b", "c"].join(" ");
const [first, second] = words(line);
console.log(first, second);
""",
         "`string` doesn't match the pattern, so the first version says the result is `[string]` — one element — and rejects `second`, although the runtime array has three. Test `string extends S` first and return the honest general type."),
        ("Enumerating what a pattern can describe",
         (r"""
type Digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";
type Pin = `${Digit}${Digit}${Digit}${Digit}${Digit}${Digit}`;
const pin: Pin = "004271";
console.log(pin.length);
""", 2590),
         r"""
declare const PinBrand: unique symbol;
type Pin = string & { readonly [PinBrand]: true };
const parsePin = (s: string): Pin | undefined => (/^\d{6}$/.test(s) ? (s as Pin) : undefined);
const pin = parsePin("004271");
console.log(pin === undefined ? "bad pin" : pin.length);
""",
         "A million-member union is too big to check. A parser and a brand (week 16) give the same guarantee — only valid PINs reach code that takes `Pin` — at no type-level cost."),
    ],
    later=[
        "**Week 27 — Capstone.** Decide, for your own typed CLI, which guarantees are worth type-level code and which are runtime checks.",
        "**TypeScript 7** (week 14): the native compiler makes checking faster, but the same depth and union limits apply.",
    ],
    exercises=[
        _drill("ts_type_performance-build", "A tail-recursive tuple",
               "`Build<N>` should produce a tuple of `N` zeros, tail-recursively. Replace `____` with the recursive branch so `Build<120>` compiles.",
               r"""
import * as fs from "fs";
type Build<N extends number, Acc extends unknown[] = []> = Acc["length"] extends N ? Acc : Build<N, [...Acc, 0]>;
const size: Build<120>["length"] = 120;
const n = Number(fs.readFileSync(0, "utf8").trim());
const row = Array.from({ length: Math.min(n, size) }, (_, i) => i % 10);
console.log(row.join(""));
console.log(`${row.length} of at most ${size}`);
""", ["Build<N, [...Acc, 0]>"],
               ["12", "0", "130"],
               hint="Return the recursive call itself, with one more element in the accumulator."),
        _drill("ts_type_performance-split", "A fallback for plain strings",
               "Replace `____` with the check that makes `Split` return `string[]` when `S` is plain `string`, so the runtime line can be split and its words read safely.",
               r"""
import * as fs from "fs";
type Split<S extends string> = string extends S ? string[] : S extends `${infer H},${infer R}` ? [H, ...Split<R>] : [S];
function fields<S extends string>(s: S): Split<S> {
  return s.split(",") as Split<S>;
}
const header = fields("name,age");
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const values = fields(line);
  console.log(`${header[0]}=${values[0] ?? "?"} ${header[1]}=${values[1] ?? "?"} (+${Math.max(0, values.length - 2)} extra)`);
}
""", ["string extends S"],
               ["ana,31\nbo,25,x,y", "solo"],
               hint="Put `string` on the left: \"is plain `string` assignable to `S`?\" is true only when `S` is `string` itself."),
        _chal("ts_type_performance-depth", "How deep is this JSON?", "Medium",
              "Types have a recursion limit; so does runtime code, and so do data formats. Each input line is JSON. Print its nesting depth (a primitive is 0, `[]`/`{}` is 1, `[[1]]` is 2) and `too deep` instead when it exceeds 5, computing depth with a recursive function over `unknown`.",
              r"""
function depth(value: unknown): number {
  if (Array.isArray(value)) return 1 + Math.max(0, ...value.map(depth));
  if (typeof value === "object" && value !== null) return 1 + Math.max(0, ...Object.values(value).map(depth));
  return 0;
}
for (const line of input.split("\n")) {
  const d = depth(JSON.parse(line));
  console.log(d > 5 ? "too deep" : d);
}
""", ['1\n[]\n[[1]]\n{"a":{"b":[1,{"c":2}]}}\n[[[[[[0]]]]]]', '"x"\n{}'],
              hint="An array or object is one level more than its deepest child; `Math.max(0, …)` handles the empty case."),
    ],
    quiz=[
        _cq("What does TS2589 mean?",
            "Type instantiation is excessively deep and possibly infinite",
            ["A union has too many members", "A type is used before it is declared", "A generic has too many parameters"],
            "Usually a non-tail-recursive type, or genuinely infinite recursion."),
        _cq("Which recursive type can go deepest?",
            "One whose recursive call is the whole branch, with the result carried in an accumulator",
            ["One wrapped in a tuple spread", "One using `infer`", "Any recursive interface"],
            "Tail-recursive conditional types are evaluated iteratively, up to 1,000 steps."),
        _cq("A template literal of six 10-member unions is…",
            "A million members — TS2590, too complex to represent",
            ["60 members", "Fine, unions are free", "Automatically widened to `string`"],
            "Unions in template literals multiply. Use a pattern like `` `${number}` ``."),
        _cq("`Split<string>` with no special case returns `[string]`. Why is that wrong?",
            "A plain `string` has nothing to parse; the honest answer is `string[]`",
            ["`Split` can't take `string`", "It should be `never`", "It is right"],
            "Check `string extends S` first."),
        _cq("Which is cheaper for the checker?",
            "`interface C extends A, B {}`", ["`type C = A & B & …` with many parts", "They are identical", "Neither can be cached"],
            "Interfaces are cached by name; large intersections are recomputed."),
        _cq("When is complex type-level code worth it?",
            "When it catches real mistakes at many call sites of a widely used API",
            ["Always — more types are safer", "Never", "Only in libraries"],
            "Otherwise a plain type and a runtime check are cheaper to read and to check."),
    ],
    interview=[
        ("You hit \"Type instantiation is excessively deep\". What do you do?",
         "Check whether the recursion is really infinite; if not, make it tail-recursive — carry the result in an accumulator parameter so the recursive reference is the entire branch — which raises the limit from a few dozen levels to 1,000. If it still doesn't fit, the type is probably doing a runtime job and should be simplified."),
        ("How do you keep a large codebase's type checking fast?",
         "Name intermediate types so they're cached, prefer `interface extends` over big intersections, avoid unions that explode through template literals, constrain generics early, and measure with `--extendedDiagnostics` or `--generateTrace` before optimising. TypeScript 7's native compiler helps, but doesn't remove those limits."),
        ("When should you not use advanced types?",
         "When a simpler type plus a runtime check gives the same safety, or when the type is harder to read than the bug it prevents. Type-level code pays off in widely used APIs — routers, ORMs, event buses — where it catches mistakes at hundreds of call sites."),
    ],
)
