# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter reading kinds, Month 5 (TS_MASTERY_ROADMAP
# X-10, X-11): predict / diagnose / retype / design / fix for the generics and
# type-level chapters of weeks 18-22, topping each chapter up to its target.
#
# Weeks 18-22 run at strict+indexed and are mostly about types, so predict and
# design are often type-only; retype and fix keep a runtime program in which
# the chapter's type feature is what makes the `any` dishonest or the bug
# possible. Helpers are in mastery_ts_chapter_kit.py; exec()'d by gen_seed.py
# with the other tools/mastery_ts_x_m*.py files.
# ---------------------------------------------------------------------------


# ===========================================================================
# Week 18 — ts_generics
# ===========================================================================

_xpr("ts_generics", 1, "Wrapping every element", r'''
function wrapAll<T>(xs: T[]): { item: T }[] {
  return xs.map((item) => ({ item }));
}
const flags = wrapAll([true, false]);
''', "flags", "{ item: boolean }[]",
     hints=["`T` is filled in from the array's element type.", "`[true, false]` is a `boolean[]`, so `T` is `boolean`."])

_xdx("ts_generics", 1, "Pushing the wrong kind",
     "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.",
     r'''
class Stack<T> {
  readonly items: T[] = [];
  push(item: T): void {
    this.items.push(item);
  }
  pop(): T | undefined {
    return this.items.pop();
  }
}
const nums = new Stack<number>();
for (const t of input.split(/\s+/)) nums.push(t);
console.log((nums.pop() ?? 0) + (nums.pop() ?? 0));
''', r'''
class Stack<T> {
  readonly items: T[] = [];
  push(item: T): void {
    this.items.push(item);
  }
  pop(): T | undefined {
    return this.items.pop();
  }
}
const nums = new Stack<number>();
for (const t of input.split(/\s+/)) nums.push(Number(t));
console.log((nums.pop() ?? 0) + (nums.pop() ?? 0));
''', ["1 2 3", "10", "-4 4"],
     hints=["`Stack<number>` fixed `T` for this stack: every `push` must hand it a number.",
            "Convert each token with `Number(t)` before pushing it."])

_xrt("ts_generics", 1, "The last word, not the last anything",
     "`last` works on any array but says `any`, so `word` could be used as anything. Give it a type parameter.",
     r'''
function last(xs: any[]): any {
  return xs[xs.length - 1];
}
const word = last(input.split(/\s+/));
console.log(word?.toUpperCase() ?? "(none)");
''', r'''
function last<T>(xs: T[]): T | undefined {
  return xs[xs.length - 1];
}
const word = last(input.split(/\s+/));
console.log(word?.toUpperCase() ?? "(none)");
''', "type _1 = Expect<Equal<typeof word, string | undefined>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof last<boolean>>, boolean | undefined>>;",
     ["one two three", "solo"],
     hints=["Link the element type of the argument to the result with `<T>`.",
            "Under `noUncheckedIndexedAccess`, `xs[i]` is `T | undefined` — say so in the return type."])

_xrt("ts_generics", 2, "Zipping two kinds",
     "`zip` pairs names with scores but types every pair as `any[]`. Type it so each pair knows it is a name and a score.",
     r'''
function zip(a: any[], b: any[]): any[][] {
  return a.map((x, i) => [x, b[i]]);
}
const [names = "", scores = ""] = input.split("|");
const pairs = zip(names.split(","), scores.split(",").map(Number));
console.log(pairs.map(([n, s]) => `${n}:${s ?? "-"}`).join(" "));
''', r'''
function zip<A, B>(a: A[], b: B[]): [A, B | undefined][] {
  return a.map((x, i) => [x, b[i]]);
}
const [names = "", scores = ""] = input.split("|");
const pairs = zip(names.split(","), scores.split(",").map(Number));
console.log(pairs.map(([n, s]) => `${n}:${s ?? "-"}`).join(" "));
''', "type _1 = Expect<Equal<typeof pairs, [string, number | undefined][]>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof zip<boolean, string>>, [boolean, string | undefined][]>>;",
     ["ana,bo|3,5", "ana,bo,cy|1", "x|9"],
     hints=["Two arrays of two different element types need two type parameters.",
            "`b[i]` may run past the end of `b`, so the second slot is `B | undefined`."])

_xrt("ts_generics", 3, "A queue of something",
     "The queue stores `any`, so what comes out has lost its type. Make the class generic.",
     r'''
class Queue {
  readonly items: any[] = [];
  add(item: any): void {
    this.items.push(item);
  }
  take(): any {
    return this.items.shift();
  }
}
const q = new Queue();
for (const t of input.split(/\s+/)) q.add(Number(t));
const a = q.take();
const b = q.take();
console.log(a === undefined || b === undefined ? "too short" : a - b);
''', r'''
class Queue<T> {
  readonly items: T[] = [];
  add(item: T): void {
    this.items.push(item);
  }
  take(): T | undefined {
    return this.items.shift();
  }
}
const q = new Queue<number>();
for (const t of input.split(/\s+/)) q.add(Number(t));
const a = q.take();
const b = q.take();
console.log(a === undefined || b === undefined ? "too short" : a - b);
''', "type _1 = Expect<Equal<typeof a, number | undefined>>;\n"
     "type _2 = Expect<Equal<ReturnType<Queue<string>[\"take\"]>, string | undefined>>;",
     ["10 3 5", "7", "2 9"],
     hints=["Give the class a type parameter and use it for the items, `add` and `take`.",
            "`shift()` on an empty array gives `undefined`, so `take` returns `T | undefined`."])

_xdz("ts_generics", 1, "A pair of anything", "Write the generic `Pair` type from how it is used.",
     r'''
type Pair<A, B> = { first: A; second: B };
const pairs: Pair<string, number>[] = input.split(/\s+/).map((t) => {
  const [k = "", v = "0"] = t.split("=");
  return { first: k, second: Number(v) };
});
console.log(pairs.map((p) => p.first.toUpperCase() + (p.second * 2)).join(" "));
''', "type Pair<A, B> = { first: A; second: B };",
     "type _1 = Expect<Equal<Pair<1, 2>, { first: 1; second: 2 }>>;\n"
     "type _2 = Expect<Equal<Pair<boolean, string>[\"second\"], string>>;",
     ["a=1 b=2", "x=5"],
     hints=["Two type parameters: one for each field.", "`first` has the first parameter's type, `second` the second's."])

_xdz("ts_generics", 2, "Repeat, for any item", "Write `repeat`'s signature: it must work for any item and keep its type.",
     r'''
function repeat<T>(item: T, n: number): T[] {
  return Array.from({ length: n }, () => item);
}
const [word = "", count = "0"] = input.split(/\s+/);
console.log(repeat(word, Number(count)).join("-"));
console.log(repeat(Number(count), 2).reduce((s, x) => s + x, 0));
''', "function repeat<T>(item: T, n: number): T[] {",
     "type _1 = Expect<Equal<ReturnType<typeof repeat<boolean>>, boolean[]>>;\n"
     "type _2 = Expect<Equal<Parameters<typeof repeat<boolean>>[0], boolean>>;",
     ["ab 3", "x 1", "hey 0"],
     hints=["It is called with a string and with a number, and `.join`/`.reduce` need the right element type back.",
            "One type parameter links the item to the array's element type."])

_xdz("ts_generics", 3, "A tree of anything",
     "Write the generic `Tree` type from how it is used: a value and a list of child trees of the same kind.",
     r'''
type Tree<T> = { value: T; children: Tree<T>[] };
const words: Tree<string> = { value: "root", children: [{ value: "leaf", children: [] }] };
const nums: Tree<number> = { value: 1, children: [{ value: 2, children: [{ value: 3, children: [] }] }] };
function size<T>(t: Tree<T>): number {
  return 1 + t.children.reduce((s, c) => s + size(c), 0);
}
const total: number = size(words) + size(nums);
const top: string = words.value;
''', "type Tree<T> = { value: T; children: Tree<T>[] };",
     "type _1 = Expect<Equal<Tree<number>[\"value\"], number>>;\n"
     "type _2 = Expect<Equal<Tree<number>[\"children\"], Tree<number>[]>>;",
     [],
     hints=["A generic type can refer to itself.", "`children` is an array of trees holding the same `T`."])

_xfx("ts_generics", 1, "A cast in a generic",
     "Each line is `name qty`. It should print the quantity plus one, and prints something else.",
     r'''
function field<T>(row: Record<string, string>, key: string): T {
  return row[key] as T;
}
const [name = "", qty = "0"] = input.split(/\s+/);
const row: Record<string, string> = { name, qty };
const n = field<number>(row, "qty");
console.log(field<string>(row, "name") + ": " + (n + 1));
''', r'''
function field(row: Record<string, string>, key: string): string {
  return row[key] ?? "";
}
const [name = "", qty = "0"] = input.split(/\s+/);
const row: Record<string, string> = { name, qty };
const n = Number(field(row, "qty"));
console.log(field(row, "name") + ": " + (n + 1));
''', ["pen 3", "cup 10"],
     hints=["`field<number>` does not convert anything: the caller just picked a `T` the value never was.",
            "Return what is really there (a string) and convert it with `Number`."])

_xfx("ts_generics", 2, "A fallback for any type",
     "`firstOr` should return the first number, or -1 when there is none. It ignores a first number of 0.",
     r'''
function firstOr<T>(xs: T[], fallback: T): T {
  return xs[0] || fallback;
}
const nums = input === "" ? [] : input.split(/\s+/).map(Number);
console.log(firstOr(nums, -1));
''', r'''
function firstOr<T>(xs: T[], fallback: T): T {
  return xs[0] ?? fallback;
}
const nums = input === "" ? [] : input.split(/\s+/).map(Number);
console.log(firstOr(nums, -1));
''', ["5 6", "0 7", ""],
     hints=["`T` may be `number`, and `0` is a perfectly good number.",
            "`||` falls back on every falsy value; `??` only on `null`/`undefined`."])


# ===========================================================================
# Week 18 — ts_generic_constraints
# ===========================================================================

_xpr("ts_generic_constraints", 1, "Longest of two strings", r'''
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
const w = longest("ab", "c");
''', "w", '"ab" | "c"',
     hints=["Each argument is a candidate for `T`, and nothing here asks for plain `string`.",
            "Both literal candidates survive, as a union."])

_xpr("ts_generic_constraints", 2, "Plucking one field", r'''
function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((item) => item[key]);
}
const tags = pluck([{ id: 1, tags: ["a"] }, { id: 2, tags: [] }], "tags");
''', "tags", "string[][]",
     hints=["`T[K]` is the type of the `tags` property.", "Each row's `tags` is a `string[]`, and `pluck` returns an array of them."])

_xdx("ts_generic_constraints", 1, "Reading id from any T",
     "TS2339: Property 'id' does not exist on type 'T'.",
     r'''
function byId<T>(items: T[], id: string): T | undefined {
  return items.find((x) => x.id === id);
}
const rows = [{ id: "a", title: "write" }, { id: "b", title: "test" }];
console.log(byId(rows, input)?.title ?? "missing");
''', r'''
function byId<T extends { id: string }>(items: T[], id: string): T | undefined {
  return items.find((x) => x.id === id);
}
const rows = [{ id: "a", title: "write" }, { id: "b", title: "test" }];
console.log(byId(rows, input)?.title ?? "missing");
''', ["a", "b", "z"],
     hints=["An unconstrained `T` could be a number — nothing says it has an `id`.",
            "Constrain `T` to the smallest shape the body uses: `{ id: string }`."])

_xrt("ts_generic_constraints", 1, "Best by any key",
     "`maxBy` takes `any`, so the key could be misspelled and the result is `any`. Type it with a constrained key.",
     r'''
function maxBy(items: any[], key: any): any {
  let best = items[0];
  for (const x of items) if (x[key] > best[key]) best = x;
  return best;
}
const players = input.split(/\s+/).map((t) => {
  const [name = "", score = "0"] = t.split(":");
  return { name, score: Number(score) };
});
const top = maxBy(players, "score");
console.log(top === undefined ? "none" : `${top.name} ${top.score}`);
''', r'''
function maxBy<T extends object, K extends keyof T>(items: T[], key: K): T | undefined {
  let best = items[0];
  for (const x of items) if (best === undefined || x[key] > best[key]) best = x;
  return best;
}
const players = input.split(/\s+/).map((t) => {
  const [name = "", score = "0"] = t.split(":");
  return { name, score: Number(score) };
});
const top = maxBy(players, "score");
console.log(top === undefined ? "none" : `${top.name} ${top.score}`);
''', "type _1 = Expect<Equal<typeof top, { name: string; score: number } | undefined>>;\n"
     "type _2 = Expect<Equal<Parameters<typeof maxBy<{ a: 1; b: 2 }, \"a\">>[1], \"a\">>;",
     ["ana:3 bo:9 cy:5", "solo:1", "x:-2 y:-7"],
     hints=["`K extends keyof T` lets only real keys through, and `x[key]` becomes `T[K]`.",
            "The body indexes the elements, so `T extends object`; the result is an element — or `undefined` for an empty array."])

_xrt("ts_generic_constraints", 2, "Renaming keeps the rest",
     "`rename` returns `any`, so the caller loses the fields it did not touch. Keep the caller's own type.",
     r'''
function rename(item: any, name: string): any {
  return { ...item, name };
}
const [name = "", age = "0", next = ""] = input.split(/\s+/);
const renamed = rename({ name, age: Number(age) }, next);
console.log(`${renamed.name} is ${renamed.age + 1} next year`);
''', r'''
function rename<T extends { name: string }>(item: T, name: string): T {
  return { ...item, name };
}
const [name = "", age = "0", next = ""] = input.split(/\s+/);
const renamed = rename({ name, age: Number(age) }, next);
console.log(`${renamed.name} is ${renamed.age + 1} next year`);
''', "type _1 = Expect<Equal<typeof renamed, { name: string; age: number }>>;",
     ["ana 36 ada", "bo 9 bob"],
     hints=["Constrain to what the body needs (a `name`), and return the caller's `T`.",
            "`<T extends { name: string }>(item: T, ...): T`."])

_xrt("ts_generic_constraints", 3, "Picking only real keys",
     "`pickFields` copies some fields into a new object but types everything as `any`. Constrain the keys and type the result.",
     r'''
function pickFields(obj: any, keys: any[]): any {
  const out: any = {};
  for (const k of keys) out[k] = obj[k];
  return out;
}
const [name = "", city = "", age = "0"] = input.split(/\s+/);
const user = { name, city, age: Number(age) };
const view = pickFields(user, ["name", "age"]);
console.log(Object.keys(view).join(","), view.age * 2);
''', r'''
function pickFields<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const out = {} as Pick<T, K>;
  for (const k of keys) out[k] = obj[k];
  return out;
}
const [name = "", city = "", age = "0"] = input.split(/\s+/);
const user = { name, city, age: Number(age) };
const view = pickFields(user, ["name", "age"]);
console.log(Object.keys(view).join(","), view.age * 2);
''', "type _1 = Expect<Equal<typeof view, Pick<{ name: string; city: string; age: number }, \"name\" | \"age\">>>;",
     ["ana oslo 36", "bo rome 9"],
     hints=["The keys must be keys of the object: `K extends keyof T`.",
            "`Pick<T, K>` is the object with just those keys."])

_xdz("ts_generic_constraints", 1, "Anything with a numeric id",
     "Write `byId`'s signature: it must accept any rows with a numeric `id`, reject rows without one, and give back the caller's row type.",
     r'''
function byId<T extends { id: number }>(items: readonly T[], id: number): T | undefined {
  return items.find((x) => x.id === id);
}
const users = [{ id: 1, name: "ana" }, { id: 2, name: "bo" }];
const hit = byId(users, 2);
const name: string | undefined = hit?.name;
''', "function byId<T extends { id: number }>(items: readonly T[], id: number): T | undefined {",
     "type _1 = Expect<Equal<typeof hit, { id: number; name: string } | undefined>>;\n"
     "// @ts-expect-error — rows without an id are rejected\n"
     "byId([{ name: \"x\" }], 1);",
     [],
     hints=["The body reads `.id`, so `T` needs a constraint.",
            "Return `T | undefined` so the caller keeps `name`."])

_xdz("ts_generic_constraints", 2, "A box with a default",
     "Write the `Box` type: used bare it holds a string; given a type argument it holds that.",
     r'''
type Box<T = string> = { value: T; label: string };
const [word = "", n = "0"] = input.split(/\s+/);
const named: Box = { value: word, label: "word" };
const counted: Box<number> = { value: Number(n), label: "count" };
console.log(`${named.label}=${named.value.toUpperCase()} ${counted.label}=${counted.value * 2}`);
''', "type Box<T = string> = { value: T; label: string };",
     "type _1 = Expect<Equal<Box, { value: string; label: string }>>;\n"
     "type _2 = Expect<Equal<Box<number>[\"value\"], number>>;",
     ["hi 4", "x 0"],
     hints=["`Box` is used with no type argument and with one.", "A default type parameter: `<T = string>`."])

_xfx("ts_generic_constraints", 1, "Sorted, but as text",
     "Each token is `name:score`. It should list names from lowest to highest score; with `9` and `10` it gets the order wrong.",
     r'''
function sortBy<T, K extends keyof T>(items: readonly T[], key: K): T[] {
  return items.toSorted((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));
}
const rows = input.split(/\s+/).map((t) => {
  const [name = "", score = "0"] = t.split(":");
  return { name, score };
});
console.log(sortBy(rows, "score").map((r) => r.name).join(","));
''', r'''
function sortBy<T, K extends keyof T>(items: readonly T[], key: K): T[] {
  return items.toSorted((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));
}
const rows = input.split(/\s+/).map((t) => {
  const [name = "", score = "0"] = t.split(":");
  return { name, score: Number(score) };
});
console.log(sortBy(rows, "score").map((r) => r.name).join(","));
''', ["a:9 b:10 c:2", "x:5 y:3"],
     hints=["`K extends keyof T` accepts any key — including one whose values are strings.",
            "Hover `rows`: what is `score`'s type? Strings compare letter by letter."])

_xfx("ts_generic_constraints", 2, "Keep the first",
     "Each token is `name@city`. It should print, for each city, the FIRST person seen there — it prints the last.",
     r'''
function indexBy<T, K extends keyof T>(items: T[], key: K): Map<T[K], T> {
  const m = new Map<T[K], T>();
  for (const x of items) m.set(x[key], x);
  return m;
}
const people = input.split(/\s+/).map((t) => {
  const [name = "", city = ""] = t.split("@");
  return { name, city };
});
console.log([...indexBy(people, "city")].map(([c, p]) => `${c}=${p.name}`).join(" "));
''', r'''
function indexBy<T, K extends keyof T>(items: T[], key: K): Map<T[K], T> {
  const m = new Map<T[K], T>();
  for (const x of items) if (!m.has(x[key])) m.set(x[key], x);
  return m;
}
const people = input.split(/\s+/).map((t) => {
  const [name = "", city = ""] = t.split("@");
  return { name, city };
});
console.log([...indexBy(people, "city")].map(([c, p]) => `${c}=${p.name}`).join(" "));
''', ["ana@oslo bo@rome cy@oslo", "x@a", "p@b q@b r@b"],
     hints=["`Map.set` overwrites an existing key.", "Only set the key when the map does not have it yet."])


# ===========================================================================
# Week 18 — ts_generic_inference
# ===========================================================================

_xpr("ts_generic_inference", 1, "A constrained literal", r'''
function keep<T extends string>(x: T): T {
  return x;
}
const mode = keep("on");
''', "mode", '"on"',
     hints=["A type parameter constrained to `string` does not widen its literal.", "The answer is a literal type."])

_xpr("ts_generic_inference", 2, "Two kinds in one array", r'''
function firstOf<T>(xs: T[]): T | undefined {
  return xs[0];
}
const f = firstOf([1, "a"]);
''', "f", "string | number | undefined",
     hints=["The array literal's element type is the best common type of its elements.",
            "`T` is a union here; do not forget the `| undefined` from the return type."])

_xrt("ts_generic_inference", 1, "Last or a fallback",
     "`lastOr` works but says `any`. Make it generic so the fallback must match the elements and the result keeps their type.",
     r'''
function lastOr(xs: any[], fallback: any): any {
  return xs[xs.length - 1] ?? fallback;
}
const words = input === "" ? [] : input.split(/\s+/);
const w = lastOr(words, "(none)");
console.log(w.toUpperCase(), w.length);
''', r'''
function lastOr<T>(xs: T[], fallback: T): T {
  return xs[xs.length - 1] ?? fallback;
}
const words = input === "" ? [] : input.split(/\s+/);
const w = lastOr(words, "(none)");
console.log(w.toUpperCase(), w.length);
''', "type _1 = Expect<Equal<typeof w, string>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof lastOr<number>>, number>>;",
     ["a bc", "solo", ""],
     hints=["Both arguments mention `T`, so both supply candidates — here both are strings.",
            "`<T>(xs: T[], fallback: T): T`."])

_xrt("ts_generic_inference", 2, "Counting whatever comes in",
     "`countAll` returns a `Map<any, number>`. Let inference carry the element type into the map's keys.",
     r'''
function countAll(items: any[]): Map<any, number> {
  const m = new Map();
  for (const x of items) m.set(x, (m.get(x) ?? 0) + 1);
  return m;
}
const counts = countAll(input.split(/\s+/));
console.log([...counts].map(([k, v]) => `${k.toLowerCase()}=${v}`).join(" "));
''', r'''
function countAll<T>(items: T[]): Map<T, number> {
  const m = new Map<T, number>();
  for (const x of items) m.set(x, (m.get(x) ?? 0) + 1);
  return m;
}
const counts = countAll(input.split(/\s+/));
console.log([...counts].map(([k, v]) => `${k.toLowerCase()}=${v}`).join(" "));
''', "type _1 = Expect<Equal<typeof counts, Map<string, number>>>;",
     ["a B a", "x"],
     hints=["The keys have the elements' type: link them with `<T>`.",
            "An empty `new Map()` infers nothing — write `new Map<T, number>()`."])

_xrt("ts_generic_inference", 3, "Options kept exactly",
     "`options` returns `any`, so `Choice` is `any` and nothing is checked. Keep the literals with a `const` type parameter.",
     r'''
function options(xs: any): any {
  return xs;
}
const colors = options(["red", "green", "blue"]);
type Choice = (typeof colors)[number];
const isChoice = (s: string): s is Choice => (colors as readonly string[]).includes(s);
console.log(isChoice(input) ? `${input} ok` : `${input} unknown`);
''', r'''
function options<const T extends readonly string[]>(xs: T): T {
  return xs;
}
const colors = options(["red", "green", "blue"]);
type Choice = (typeof colors)[number];
const isChoice = (s: string): s is Choice => (colors as readonly string[]).includes(s);
console.log(isChoice(input) ? `${input} ok` : `${input} unknown`);
''', "type _1 = Expect<Equal<typeof colors, readonly [\"red\", \"green\", \"blue\"]>>;\n"
     "type _2 = Expect<Equal<Choice, \"red\" | \"green\" | \"blue\">>;",
     ["red", "pink", "blue"],
     hints=["A plain `<T extends readonly string[]>` would widen the call to `string[]`.",
            "`<const T extends readonly string[]>` infers as if the caller wrote `as const`."])

_xdz("ts_generic_inference", 1, "The fallback is checked, not inferred",
     "Write `choose`'s signature: `T` comes only from `allowed`; the fallback must be one of them without widening `T`.",
     r'''
function choose<T extends number>(allowed: readonly T[], n: number, fallback: NoInfer<T>): T {
  return allowed.find((a) => a === n) ?? fallback;
}
const sizes = [1, 2, 4] as const;
const got = choose(sizes, 3, 2);
''', "function choose<T extends number>(allowed: readonly T[], n: number, fallback: NoInfer<T>): T {",
     "type _1 = Expect<Equal<typeof got, 1 | 2 | 4>>;\n"
     "// @ts-expect-error — 3 is not one of the sizes\n"
     "choose(sizes, 3, 3);",
     [],
     hints=["Without help, the fallback would also be a candidate for `T`.",
            "Wrap the fallback's type in `NoInfer<T>`."])

_xdz("ts_generic_inference", 2, "A tuple, exactly as written",
     "Write `tuple`'s signature so the call keeps each argument's literal type and position.",
     r'''
function tuple<const T extends readonly unknown[]>(...xs: T): T {
  return xs;
}
const t = tuple(1, "a", true);
''', "function tuple<const T extends readonly unknown[]>(...xs: T): T {",
     "type _1 = Expect<Equal<typeof t, readonly [1, \"a\", true]>>;",
     [],
     hints=["A rest parameter typed with a type parameter infers a tuple.",
            "A `const` type parameter keeps the literals and makes it `readonly`."])

_xdz("ts_generic_inference", 3, "An empty list of strings by default",
     "Write `makeList`'s signature: with no type argument it gives a `string[]`, with one it gives that element type.",
     r'''
function makeList<T = string>(): T[] {
  return [];
}
const names = makeList();
const nums = makeList<number>();
for (const t of input.split(/\s+/)) {
  if (/^\d+$/.test(t)) nums.push(Number(t));
  else names.push(t);
}
console.log(names.join(",") || "-", nums.reduce((s, n) => s + n, 0));
''', "function makeList<T = string>(): T[] {",
     "type _1 = Expect<Equal<typeof names, string[]>>;\n"
     "type _2 = Expect<Equal<typeof nums, number[]>>;",
     ["a 1 b 2", "7", "x"],
     hints=["No argument mentions `T`, so inference has nothing to go on.",
            "A default, `<T = string>`, is what `T` becomes then."])

_xfx("ts_generic_inference", 1, "A map nobody typed",
     "It should count each word, and prints `NaN` for every count.",
     r'''
const counts = new Map();
for (const w of input.split(/\s+/)) counts.set(w, counts.get(w) + 1);
console.log([...counts].map(([k, v]) => `${k}=${v}`).join(" "));
''', r'''
const counts = new Map<string, number>();
for (const w of input.split(/\s+/)) counts.set(w, (counts.get(w) ?? 0) + 1);
console.log([...counts].map(([k, v]) => `${k}=${v}`).join(" "));
''', ["a b a", "x"],
     hints=["`new Map()` with nothing to infer from is a `Map<any, any>` — so `counts.get(w) + 1` was never checked.",
            "Write `new Map<string, number>()` and the compiler makes you handle the missing count."])


# ===========================================================================
# Week 19 — ts_keyof_indexed
# ===========================================================================

_xpr("ts_keyof_indexed", 1, "A read that follows the key", r'''
type Settings = { theme: string; size: number; wrap: boolean };
function read<K extends keyof Settings>(s: Settings, key: K): Settings[K] {
  return s[key];
}
const wrap = read({ theme: "dark", size: 14, wrap: true }, "wrap");
''', "wrap", "boolean",
     hints=["`K` is inferred as the literal key you passed.", "`Settings[\"wrap\"]` is the type of that one property."])

_xpr("ts_keyof_indexed", 2, "Position zero of a const list", r'''
const LEVELS = ["debug", "info", "warn"] as const;
const lowest = LEVELS[0];
''', "lowest", '"debug"',
     hints=["`as const` makes `LEVELS` a readonly tuple of literals.",
            "A literal index into a tuple picks that one position — and a tuple's fixed positions are never `undefined`."])

_xdx("ts_keyof_indexed", 1, "The value follows the key",
     "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.",
     r'''
const defaults = { theme: "light", fontSize: 14 };
type Settings = typeof defaults;
const current: Settings = { ...defaults };
function set<K extends keyof Settings>(key: K, value: Settings[K]): void {
  current[key] = value;
}
const [theme = "light", size = "14"] = input.split(/\s+/);
set("theme", theme);
set("fontSize", size);
console.log(`${current.theme} ${current.fontSize + 2}`);
''', r'''
const defaults = { theme: "light", fontSize: 14 };
type Settings = typeof defaults;
const current: Settings = { ...defaults };
function set<K extends keyof Settings>(key: K, value: Settings[K]): void {
  current[key] = value;
}
const [theme = "light", size = "14"] = input.split(/\s+/);
set("theme", theme);
set("fontSize", Number(size));
console.log(`${current.theme} ${current.fontSize + 2}`);
''', ["dark 16", "light 9"],
     hints=["For the key `\"fontSize\"`, `Settings[K]` is `number`.",
            "Convert the text before handing it over."])

_xrt("ts_keyof_indexed", 1, "A getter for known keys",
     "`read` takes and returns `any`. Derive its types from `defaults` so the result follows the key.",
     r'''
const defaults = { theme: "light", fontSize: 14, wrap: true };
type Settings = typeof defaults;
function read(key: any): any {
  return defaults[key as keyof Settings];
}
const bigger = read("fontSize") + Number(input);
console.log(read("theme").toUpperCase(), bigger, read("wrap") ? "wrap" : "no-wrap");
''', r'''
const defaults = { theme: "light", fontSize: 14, wrap: true };
type Settings = typeof defaults;
function read<K extends keyof Settings>(key: K): Settings[K] {
  return defaults[key];
}
const bigger = read("fontSize") + Number(input);
console.log(read("theme").toUpperCase(), bigger, read("wrap") ? "wrap" : "no-wrap");
''', "type _1 = Expect<Equal<typeof bigger, number>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof read<\"theme\">>, string>>;",
     ["2", "-4"],
     hints=["The key is one of `keyof Settings`; make it a type parameter so each call keeps its own key.",
            "Return `Settings[K]`."])

_xrt("ts_keyof_indexed", 2, "Levels from the list",
     "`Level` is declared `any`, so any string is a level. Derive it from `LEVELS`.",
     r'''
const LEVELS = ["debug", "info", "warn", "error"] as const;
type Level = any;
const isLevel = (s: string): s is Level => LEVELS.some((l) => l === s);
const serious = input.split(/\s+/).filter(isLevel).filter((l) => LEVELS.indexOf(l) >= 2);
console.log(serious.length, serious.join(",") || "-");
''', r'''
const LEVELS = ["debug", "info", "warn", "error"] as const;
type Level = (typeof LEVELS)[number];
const isLevel = (s: string): s is Level => LEVELS.some((l) => l === s);
const serious = input.split(/\s+/).filter(isLevel).filter((l) => LEVELS.indexOf(l) >= 2);
console.log(serious.length, serious.join(",") || "-");
''', "type _1 = Expect<Equal<Level, \"debug\" | \"info\" | \"warn\" | \"error\">>;\n"
     "type _2 = Expect<Equal<typeof serious, Level[]>>;",
     ["info warn fatal error", "debug", "warn warn"],
     hints=["`typeof LEVELS` is the tuple type.", "Index it with `[number]` to union its elements."])

_xrt("ts_keyof_indexed", 3, "Only fruit we count",
     "`bump` takes `any` for the key, so a typo would add a new field. Type the key from `Totals`.",
     r'''
type Totals = { apples: number; pears: number };
const totals: Totals = { apples: 0, pears: 0 };
function bump(t: Totals, key: any, by: number): void {
  t[key as "apples"] += by;
}
const isFruit = (s: string): s is keyof Totals => s === "apples" || s === "pears";
const words = input.split(/\s+/);
for (let i = 0; i + 1 < words.length; i += 2) {
  const name = words[i] ?? "";
  if (isFruit(name)) bump(totals, name, Number(words[i + 1]));
}
console.log(`apples=${totals.apples} pears=${totals.pears}`);
''', r'''
type Totals = { apples: number; pears: number };
const totals: Totals = { apples: 0, pears: 0 };
function bump(t: Totals, key: keyof Totals, by: number): void {
  t[key] += by;
}
const isFruit = (s: string): s is keyof Totals => s === "apples" || s === "pears";
const words = input.split(/\s+/);
for (let i = 0; i + 1 < words.length; i += 2) {
  const name = words[i] ?? "";
  if (isFruit(name)) bump(totals, name, Number(words[i + 1]));
}
console.log(`apples=${totals.apples} pears=${totals.pears}`);
''', "type _1 = Expect<Equal<Parameters<typeof bump>[1], \"apples\" | \"pears\">>;",
     ["apples 3 pears 2 apples 1", "kiwi 5 pears 1", "apples 4"],
     hints=["The key can only be one of `Totals`'s keys.", "`keyof Totals`."])

_xdz("ts_keyof_indexed", 1, "A setter that checks the value",
     "Write `set`'s signature: any key of `Prefs`, and a value of that key's type.",
     r'''
type Prefs = { lang: string; volume: number; muted: boolean };
function set<K extends keyof Prefs>(p: Prefs, key: K, value: Prefs[K]): void {
  p[key] = value;
}
const prefs: Prefs = { lang: "en", volume: 5, muted: false };
set(prefs, "volume", 7);
set(prefs, "muted", true);
''', "function set<K extends keyof Prefs>(p: Prefs, key: K, value: Prefs[K]): void {",
     "type _1 = Expect<Equal<Parameters<typeof set<\"lang\">>, [p: Prefs, key: \"lang\", value: string]>>;\n"
     "// @ts-expect-error — volume is a number\n"
     "set(prefs, \"volume\", \"loud\");",
     [],
     hints=["The value's type depends on which key was passed, so the key needs a type parameter.",
            "`<K extends keyof Prefs>(p: Prefs, key: K, value: Prefs[K])`."])

_xdz("ts_keyof_indexed", 2, "Units from one list",
     "Write the `Unit` type so it always matches the `UNITS` list.",
     r'''
const UNITS = ["kg", "g", "lb"] as const;
type Unit = (typeof UNITS)[number];
const isUnit = (s: string): s is Unit => UNITS.some((u) => u === s);
const TO_GRAMS: Record<Unit, number> = { kg: 1000, g: 1, lb: 454 };
const [n = "0", unit = ""] = input.split(/\s+/);
console.log(isUnit(unit) ? `${Number(n) * TO_GRAMS[unit]} g` : `unknown unit ${unit}`);
''', "type Unit = (typeof UNITS)[number];",
     "type _1 = Expect<Equal<Unit, \"kg\" | \"g\" | \"lb\">>;",
     ["2 kg", "3 lb", "5 oz"],
     hints=["Derive it rather than writing the three strings again.",
            "`(typeof UNITS)[number]` unions the tuple's elements."])

_xfx("ts_keyof_indexed", 1, "A key check that sees too much",
     "It should print a setting's value, or `<name>: unknown` for anything that is not a setting. Try `toString`.",
     r'''
const defaults = { theme: "light", fontSize: 14 };
const isKey = (k: string): k is keyof typeof defaults => k in defaults;
console.log(isKey(input) ? `${input}=${defaults[input]}` : `${input}: unknown`);
''', r'''
const defaults = { theme: "light", fontSize: 14 };
const isKey = (k: string): k is keyof typeof defaults => Object.hasOwn(defaults, k);
console.log(isKey(input) ? `${input}=${defaults[input]}` : `${input}: unknown`);
''', ["theme", "fontSize", "toString", "color"],
     hints=["`keyof typeof defaults` is only `\"theme\" | \"fontSize\"` — but `in` also finds inherited properties.",
            "Ask whether the object has the key itself: `Object.hasOwn`."])

_xfx("ts_keyof_indexed", 2, "Counts that start from nothing",
     "It should count each level in the input (ignoring unknown words), and prints `NaN`.",
     r'''
const LEVELS = ["info", "warn", "error"] as const;
type Level = (typeof LEVELS)[number];
const isLevel = (s: string): s is Level => LEVELS.some((l) => l === s);
const counts = {} as Record<Level, number>;
for (const w of input.split(/\s+/)) if (isLevel(w)) counts[w]++;
console.log(LEVELS.map((l) => `${l}=${counts[l]}`).join(" "));
''', r'''
const LEVELS = ["info", "warn", "error"] as const;
type Level = (typeof LEVELS)[number];
const isLevel = (s: string): s is Level => LEVELS.some((l) => l === s);
const counts: Record<Level, number> = { info: 0, warn: 0, error: 0 };
for (const w of input.split(/\s+/)) if (isLevel(w)) counts[w]++;
console.log(LEVELS.map((l) => `${l}=${counts[l]}`).join(" "));
''', ["info warn info", "error", "debug"],
     hints=["`{} as Record<Level, number>` claims every level has a count — none does yet.",
            "Drop the cast and write the starting counts; then the compiler checks every level is there."])


# ===========================================================================
# Week 19 — ts_lookup_types
# ===========================================================================

_xrt("ts_lookup_types", 1, "A role, not any string",
     "`canEdit` takes `any`. Type its parameter by looking it up in `User`, so it follows the model.",
     r'''
type User = { name: string; role: "admin" | "member" };
const canEdit = (role: any): boolean => role === "admin";
const isRole = (s: string): s is User["role"] => s === "admin" || s === "member";
const [name = "", role = ""] = input.split(/\s+/);
if (isRole(role)) {
  const u: User = { name, role };
  console.log(`${u.name} ${canEdit(u.role) ? "can" : "cannot"} edit`);
} else {
  console.log(`bad role ${role}`);
}
''', r'''
type User = { name: string; role: "admin" | "member" };
const canEdit = (role: User["role"]): boolean => role === "admin";
const isRole = (s: string): s is User["role"] => s === "admin" || s === "member";
const [name = "", role = ""] = input.split(/\s+/);
if (isRole(role)) {
  const u: User = { name, role };
  console.log(`${u.name} ${canEdit(u.role) ? "can" : "cannot"} edit`);
} else {
  console.log(`bad role ${role}`);
}
''', "type _1 = Expect<Equal<Parameters<typeof canEdit>[0], \"admin\" | \"member\">>;",
     ["ana admin", "bo member", "cy owner"],
     hints=["Do not copy the union — read it from the model.", "`User[\"role\"]`."])

_xrt("ts_lookup_types", 2, "Positions of an entry",
     "`scoreOf` and `cells` return `any`. Type them with lookups into the `Entry` tuple.",
     r'''
type Entry = [name: string, score: number, passed: boolean];
const scoreOf = (e: Entry): any => e[1];
const cells = (e: Entry): any[] => [...e];
const entries: Entry[] = input.split(/\s+/).map((t) => {
  const [n = "", s = "0"] = t.split(":");
  return [n, Number(s), Number(s) >= 50];
});
const best = Math.max(...entries.map(scoreOf));
console.log(best, entries.flatMap(cells).filter((c) => c === true).length);
''', r'''
type Entry = [name: string, score: number, passed: boolean];
const scoreOf = (e: Entry): Entry[1] => e[1];
const cells = (e: Entry): Entry[number][] => [...e];
const entries: Entry[] = input.split(/\s+/).map((t) => {
  const [n = "", s = "0"] = t.split(":");
  return [n, Number(s), Number(s) >= 50];
});
const best = Math.max(...entries.map(scoreOf));
console.log(best, entries.flatMap(cells).filter((c) => c === true).length);
''', "type _1 = Expect<Equal<ReturnType<typeof scoreOf>, number>>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof cells>, (string | number | boolean)[]>>;",
     ["ana:91 bo:48", "cy:50", "a:1 b:2 c:99"],
     hints=["A literal index picks one position of a tuple type.",
            "`Entry[1]` for the score; `Entry[number]` is the union of every position."])

_xrt("ts_lookup_types", 3, "Prices from the table",
     "`price` takes and returns `any`. Type it from the `PRICES` table, so only real sizes go in and the exact prices come out.",
     r'''
const PRICES = { S: 10, M: 12, L: 14 } as const;
const isSize = (s: string): s is keyof typeof PRICES => Object.hasOwn(PRICES, s);
function price(size: any): any {
  return PRICES[size as "S"];
}
const [size = "", qty = "1"] = input.split(/\s+/);
console.log(isSize(size) ? `${qty} x ${size} = ${price(size) * Number(qty)}` : `no size ${size}`);
''', r'''
const PRICES = { S: 10, M: 12, L: 14 } as const;
const isSize = (s: string): s is keyof typeof PRICES => Object.hasOwn(PRICES, s);
function price(size: keyof typeof PRICES): (typeof PRICES)[keyof typeof PRICES] {
  return PRICES[size];
}
const [size = "", qty = "1"] = input.split(/\s+/);
console.log(isSize(size) ? `${qty} x ${size} = ${price(size) * Number(qty)}` : `no size ${size}`);
''', "type _1 = Expect<Equal<Parameters<typeof price>[0], \"S\" | \"M\" | \"L\">>;\n"
     "type _2 = Expect<Equal<ReturnType<typeof price>, 10 | 12 | 14>>;",
     ["M 3", "L 1", "XL 2"],
     hints=["`keyof typeof PRICES` is the union of sizes.",
            "Index the table's type with that union to get the union of its prices."])

_xdz("ts_lookup_types", 1, "A safe ValueAt",
     "Write `ValueAt`: the type of property `K` of `T`, accepting only real keys.",
     r'''
type ValueAt<T, K extends keyof T> = T[K];
type Order = { id: number; lines: { sku: string; qty: number }[]; note?: string };
type Lines = ValueAt<Order, "lines">;
''', "type ValueAt<T, K extends keyof T> = T[K];",
     "type _1 = Expect<Equal<ValueAt<{ a: 1; b: \"x\" }, \"b\">, \"x\">>;\n"
     "type _2 = Expect<Equal<ValueAt<Order, \"id\" | \"note\">, number | string | undefined>>;\n"
     "// @ts-expect-error — not a key of Order\n"
     "type _3 = ValueAt<Order, \"phone\">;",
     [],
     hints=["An unconstrained `K` cannot index `T`.", "Constrain `K extends keyof T`, then look it up: `T[K]`."])

_xdz("ts_lookup_types", 2, "One line of an order",
     "Write the `Line` type by looking it up in `Order` — do not write its fields again.",
     r'''
type Order = { id: number; lines: { sku: string; qty: number; unit: number }[] };
type Line = Order["lines"][number];
const lineTotal = (l: Line): number => l.qty * l.unit;
const order: Order = {
  id: 1,
  lines: input.split(/\s+/).map((t) => {
    const [sku = "", qty = "0", unit = "0"] = t.split(":");
    return { sku, qty: Number(qty), unit: Number(unit) };
  }),
};
console.log(order.lines.map((l) => `${l.sku}=${lineTotal(l)}`).join(" "));
''', "type Line = Order[\"lines\"][number];",
     "type _1 = Expect<Equal<Line, { sku: string; qty: number; unit: number }>>;",
     ["pen:2:3 cup:1:4", "box:0:9"],
     hints=["First look up the `lines` property, then its element type.", "`Order[\"lines\"][number]`."])

_xfx("ts_lookup_types", 1, "Ages sorted as text",
     "Each token is `name:age`. It should print the ages from youngest to oldest, and puts 10 before 9.",
     r'''
function pluck<T, K extends keyof T>(rows: readonly T[], key: K): T[K][] {
  return rows.map((r) => r[key]);
}
const rows = input.split(/\s+/).map((t) => {
  const [name = "", age = "0"] = t.split(":");
  return { name, age: Number(age) };
});
console.log(pluck(rows, "age").sort().join(" "));
''', r'''
function pluck<T, K extends keyof T>(rows: readonly T[], key: K): T[K][] {
  return rows.map((r) => r[key]);
}
const rows = input.split(/\s+/).map((t) => {
  const [name = "", age = "0"] = t.split(":");
  return { name, age: Number(age) };
});
console.log(pluck(rows, "age").sort((a, b) => a - b).join(" "));
''', ["ana:9 bo:10 cy:31", "x:5 y:40 z:100"],
     hints=["The lookup is right: `pluck(rows, \"age\")` really is a `number[]`.",
            "But `sort()` with no comparator compares elements as text. Pass `(a, b) => a - b`."])

_xfx("ts_lookup_types", 2, "An update that changes nothing",
     "`update` should return a copy of the user with one field replaced. The field keeps its old value.",
     r'''
type User = { name: string; city: string; age: number };
function update<K extends keyof User>(u: User, key: K, value: User[K]): User {
  return { [key]: value, ...u };
}
const [name = "", city = "", age = "0", next = ""] = input.split(/\s+/);
const moved = update({ name, city, age: Number(age) }, "city", next);
console.log(`${moved.name} lives in ${moved.city}`);
''', r'''
type User = { name: string; city: string; age: number };
function update<K extends keyof User>(u: User, key: K, value: User[K]): User {
  return { ...u, [key]: value };
}
const [name = "", city = "", age = "0", next = ""] = input.split(/\s+/);
const moved = update({ name, city, age: Number(age) }, "city", next);
console.log(`${moved.name} lives in ${moved.city}`);
''', ["ana oslo 36 rome", "bo lima 9 kyiv"],
     hints=["The types are right: `User[K]` is the right value for the key.",
            "In an object literal, later properties win — and the spread comes after the new value."])
