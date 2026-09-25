# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery, Month 5 (weeks 18-22): problem sets, runnable projects,
# extra practice and review cards for the chapters in ts_chapters_m5.py.
#
# Month 5 is about types, so each week's set mixes runtime problems that USE
# generic and type-level code with type-graded ones (`_tsp_types`, checked by
# hidden Expect<Equal<…>> lines). None repeats a type workshop in
# mastery_ts_practice.py. Everything runs under strict+indexed.
# ---------------------------------------------------------------------------

_SI = "strict+indexed"

# ===========================================================================
# Week 18 — Generics, constraints, inference
# ===========================================================================

TS_PROBLEM_SETS[18] = [
    _tsp(18, "tsm-w18-partition", "Partition anything", "warm-up",
         "Write `partition<T>(items: readonly T[], test: (item: T) => boolean): [T[], T[]]`. The first input line is numbers, the second words. Print the numbers split into even and odd, and the words split into those longer than 3 characters and the rest, as `<yes…> | <no…>` (`-` for an empty half).",
         r"""
function partition<T>(items: readonly T[], test: (item: T) => boolean): [T[], T[]] {
  const yes: T[] = [];
  const no: T[] = [];
  for (const item of items) (test(item) ? yes : no).push(item);
  return [yes, no];
}
const [numLine = "", wordLine = ""] = input.split("\n");
const nums = numLine.trim().split(/\s+/).map(Number);
const words = wordLine.trim().split(/\s+/);
const [even, odd] = partition(nums, (n) => n % 2 === 0);
const [long, short] = partition(words, (w) => w.length > 3);
const show = (xs: readonly (string | number)[]) => xs.join(" ") || "-";
console.log(`${show(even)} | ${show(odd)}`);
console.log(`${show(long)} | ${show(short)}`);
""", ["1 2 3 4 5 6\nthe quick brown fox", "7\nhi there", "2 4\nab cd"],
         hints=["`T` is inferred from `items`, so the callback's parameter is typed for free.", "Return a tuple type `[T[], T[]]` so both halves destructure with the element type."]),
    _tsp(18, "tsm-w18-zip", "Zip two lists", "warm-up",
         "Write `zip<A, B>(as: readonly A[], bs: readonly B[]): [A, B][]`, stopping at the shorter list. The first line is names, the second scores. Print each pair as `<name>: <score>`, then `<k> pairs` and, if the lists had different lengths, `ignored <n> extra`.",
         r"""
function zip<A, B>(as: readonly A[], bs: readonly B[]): [A, B][] {
  const out: [A, B][] = [];
  for (let i = 0; i < Math.min(as.length, bs.length); i++) {
    const a = as[i];
    const b = bs[i];
    if (a !== undefined && b !== undefined) out.push([a, b]);
  }
  return out;
}
const [nameLine = "", scoreLine = ""] = input.split("\n");
const names = nameLine.trim().split(/\s+/);
const scores = scoreLine.trim().split(/\s+/).map(Number);
const pairs = zip(names, scores);
for (const [name, score] of pairs) console.log(`${name}: ${score}`);
console.log(`${pairs.length} pairs`);
const extra = Math.abs(names.length - scores.length);
if (extra > 0) console.log(`ignored ${extra} extra`);
""", ["ana bo cy\n90 80 70", "ana bo cy dee\n1 2", "x\n5 6 7"],
         hints=["Two type parameters, one per list.", "Under `noUncheckedIndexedAccess` each `as[i]` is `A | undefined` — check before pushing."]),
    _tsp(18, "tsm-w18-chunk", "Chunks of any size", "warm-up",
         "Write `chunk<T>(items: readonly T[], size: number): T[][]`. The first input line is the size, the second a list of words. Print each chunk on its own line, words space-separated, then `<k> chunks` (`chunk` for one). A size below 1 prints `bad size`.",
         r"""
function chunk<T>(items: readonly T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < items.length; i += size) out.push(items.slice(i, i + size));
  return out;
}
const [sizeText = "", line = ""] = input.split("\n");
const size = Number(sizeText);
if (!Number.isInteger(size) || size < 1) {
  console.log("bad size");
} else {
  const chunks = chunk(line.trim().split(/\s+/), size);
  for (const c of chunks) console.log(c.join(" "));
  console.log(`${chunks.length} ${chunks.length === 1 ? "chunk" : "chunks"}`);
}
""", ["2\na b c d e", "3\nx y z", "0\na b", "5\nonly"],
         hints=["`slice(i, i + size)` never goes past the end."]),
    _tsp(18, "tsm-w18-unique-by", "Unique by a key", "core",
         "Write `uniqueBy<T, K>(items: readonly T[], keyOf: (item: T) => K): T[]`, keeping the first item for each key. Each input line is `<name> <email>`. Print the people unique by email compared case-insensitively (keeping the first), as `<name> <email>`, then `removed <k>`.",
         r"""
function uniqueBy<T, K>(items: readonly T[], keyOf: (item: T) => K): T[] {
  const seen = new Set<K>();
  const out: T[] = [];
  for (const item of items) {
    const key = keyOf(item);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(item);
  }
  return out;
}
type Person = { name: string; email: string };
const people: Person[] = input.split("\n").map((line) => {
  const [name = "", email = ""] = line.trim().split(/\s+/);
  return { name, email };
});
const unique = uniqueBy(people, (p) => p.email.toLowerCase());
for (const p of unique) console.log(`${p.name} ${p.email}`);
console.log(`removed ${people.length - unique.length}`);
""", ["ana ana@x.io\nbo bo@y.io\nAna2 ANA@X.IO\ncy cy@z.io\nbob BO@y.io", "solo s@s.io"],
         hints=["`K` is inferred from the key function's return type — here `string`.", "A `Set<K>` of keys already seen."]),
    _tsp(18, "tsm-w18-min-max-by", "The best by any score", "core",
         "Write `minBy<T>(items: readonly T[], score: (item: T) => number): T | undefined` and `maxBy` (first on ties). Each input line is `<city> <temp> <rain>`. Print `coldest <city>`, `warmest <city>`, `wettest <city>` and `longest name <city>` — or `no data` for empty input lines only.",
         r"""
function minBy<T>(items: readonly T[], score: (item: T) => number): T | undefined {
  let best: T | undefined;
  let bestScore = Infinity;
  for (const item of items) {
    const s = score(item);
    if (s < bestScore) {
      best = item;
      bestScore = s;
    }
  }
  return best;
}
function maxBy<T>(items: readonly T[], score: (item: T) => number): T | undefined {
  return minBy(items, (item) => -score(item));
}
type City = { name: string; temp: number; rain: number };
const cities: City[] = input.split("\n").filter((l) => l.trim() !== "").map((line) => {
  const [name = "", temp = "0", rain = "0"] = line.trim().split(/\s+/);
  return { name, temp: Number(temp), rain: Number(rain) };
});
const show = (label: string, c: City | undefined) => console.log(`${label} ${c?.name ?? "no data"}`);
show("coldest", minBy(cities, (c) => c.temp));
show("warmest", maxBy(cities, (c) => c.temp));
show("wettest", maxBy(cities, (c) => c.rain));
show("longest name", maxBy(cities, (c) => c.name.length));
""", ["oslo -3 40\nrome 18 70\ncairo 30 1\nlima 18 5", "reykjavik 2 90"],
         hints=["Return `T | undefined` — an empty list has no best item.", "`maxBy` is `minBy` of the negated score."]),
    _tsp(18, "tsm-w18-lru", "A generic LRU cache", "core",
         "Write a class `LruCache<K, V>` with a capacity, `get(key): V | undefined` (marks the key as recently used) and `set(key, value): K | undefined` (returns the evicted key, if any). The first input line is the capacity; each later line is `get <k>` or `set <k> <v>`. Print the value or `miss` for `get`, and `evicted <k>` when a `set` evicts. Finish with the keys from least to most recently used.",
         r"""
class LruCache<K, V> {
  private readonly entries = new Map<K, V>();
  private readonly capacity: number;
  constructor(capacity: number) {
    this.capacity = capacity;
  }
  get(key: K): V | undefined {
    const value = this.entries.get(key);
    if (value !== undefined) {
      this.entries.delete(key);
      this.entries.set(key, value);
    }
    return value;
  }
  set(key: K, value: V): K | undefined {
    this.entries.delete(key);
    this.entries.set(key, value);
    if (this.entries.size <= this.capacity) return undefined;
    const oldest = this.entries.keys().next();
    if (oldest.done === true) return undefined;
    this.entries.delete(oldest.value);
    return oldest.value;
  }
  keys(): K[] {
    return [...this.entries.keys()];
  }
}
const [capText = "1", ...ops] = input.split("\n");
const cache = new LruCache<string, number>(Number(capText));
for (const op of ops) {
  const [cmd = "", key = "", value = ""] = op.trim().split(/\s+/);
  if (cmd === "get") console.log(cache.get(key) ?? "miss");
  else {
    const evicted = cache.set(key, Number(value));
    if (evicted !== undefined) console.log(`evicted ${evicted}`);
  }
}
console.log(cache.keys().join(" ") || "(empty)");
""", ["2\nset a 1\nset b 2\nget a\nset c 3\nget b\nget c", "1\nset x 5\nset x 6\nget x\nset y 1\nget x"],
         hints=["A `Map` iterates in insertion order: delete and re-insert to mark a key as used.",
                "The iterator result has `done`; check it before reading `value`."]),
    _tsp(18, "tsm-w18-memo", "Memoise any function", "stretch",
         "Write `memoize<A extends unknown[], R>(fn: (...args: A) => R, keyOf: (...args: A) => string)` returning a function of the same type plus a `calls()` counter of real computations. Use it on a recursive `ways(n, k)` — the number of ways to climb `n` steps taking 1 to `k` steps at a time. Each input line is `n k`; print `ways(<n>, <k>) = <w>`, and finally `computed <c> times`.",
         r"""
function memoize<A extends unknown[], R>(fn: (...args: A) => R, keyOf: (...args: A) => string) {
  const cache = new Map<string, R>();
  let computed = 0;
  const wrapped = (...args: A): R => {
    const key = keyOf(...args);
    const hit = cache.get(key);
    if (hit !== undefined) return hit;
    computed++;
    const value = fn(...args);
    cache.set(key, value);
    return value;
  };
  return Object.assign(wrapped, { calls: () => computed });
}
const ways = memoize(
  (n: number, k: number): number => {
    if (n === 0) return 1;
    let total = 0;
    for (let step = 1; step <= Math.min(k, n); step++) total += ways(n - step, k);
    return total;
  },
  (n, k) => `${n},${k}`,
);
for (const line of input.split("\n")) {
  const [n = "0", k = "1"] = line.trim().split(/\s+/);
  console.log(`ways(${n}, ${k}) = ${ways(Number(n), Number(k))}`);
}
console.log(`computed ${ways.calls()} times`);
""", ["4 2\n10 3\n4 2", "30 2\n0 5"],
         hints=["`A extends unknown[]` captures the whole parameter list as a tuple, so the wrapper keeps the original signature.",
                "`Object.assign(fn, { calls })` adds a property to a function and types the result as both."]),
    _tsp_types(18, "tsm-w18-const-tuple", "Keep the tuple exactly", "core",
               "`tuple` should return exactly what it was given — including literal types and positions — without the caller writing `as const`. Finish its type parameter.",
               '''
function tuple<const T extends readonly unknown[]>(xs: T): T {
  return xs;
}
const point = tuple([3, 4]);
const mixed = tuple(["id", 7, true]);
''', "const T extends readonly unknown[]",
               '''
type _1 = Expect<Equal<typeof point, readonly [3, 4]>>;
type _2 = Expect<Equal<typeof mixed, readonly ["id", 7, true]>>;
''', hints=["A `const` modifier on a type parameter infers arguments as if they had `as const`.",
            "The constraint must accept a readonly array."]),
    _tsp_types(18, "tsm-w18-name-constraint", "Keep the caller's type through a constraint", "core",
               "`longestName` works on anything with a `name`, and must return the caller's *own* element type (with every other field), not just `{ name: string }`. Write its type parameter.",
               '''
function longestName<T extends { name: string }>(items: readonly T[]): T | undefined {
  let best: T | undefined;
  for (const item of items) if (best === undefined || item.name.length > best.name.length) best = item;
  return best;
}
const people = [{ name: "ana", age: 31 }, { name: "bartholomew", age: 40 }];
const found = longestName(people);
''', "T extends { name: string }",
               '''
type _1 = Expect<Equal<typeof found, { name: string; age: number } | undefined>>;
function _typeTests() {
  // @ts-expect-error — the items need a name
  longestName([{ title: "x" }]);
}
''', hints=["Constrain `T` to things with a `name`, but keep `T` itself as the element type."]),
    _tsp_types(18, "tsm-w18-default-param", "A default type argument", "stretch",
               "`createStore` holds a value. When the caller gives no initial value and no type argument, it should hold a `string`; otherwise the value decides. Add a default to its type parameter.",
               '''
function createStore<T = string>(initial?: T) {
  let value = initial;
  return {
    get: (): T | undefined => value,
    set: (next: T) => {
      value = next;
    },
  };
}
const names = createStore();
const counts = createStore(0);
''', "T = string",
               '''
type _1 = Expect<Equal<ReturnType<typeof names.get>, string | undefined>>;
type _2 = Expect<Equal<ReturnType<typeof counts.get>, number | undefined>>;
function _typeTests() {
  // @ts-expect-error — the default is string
  names.set(5);
}
''', hints=["A default goes after the type parameter's name: `<T = …>`.", "It only applies when nothing can be inferred."]),
]

TS_PROJECTS[18] = _project(
    18, "collections.ts — a generic collection pipeline",
    "Write a small generic `Collection<T>` class whose methods keep the element type through a pipeline — `map` changes it, `filter` and `sortBy` keep it, `groupBy` produces a `Map` — and drive it from commands. The same class serves numbers and words, which is the point of making it generic.",
    ["The first input line is `numbers <n…>` or `words <w…>`; each later line is one step applied to the current collection: `map double|square|length|upper`, `filter even|odd|long` (`long` = length > 3), `sortBy value|length`, `unique`, `take <n>`, `chunk <n>`, `groupBy length|parity`, `first`, `count`.",
     "`map`, `filter`, `sortBy`, `unique` and `take` print the new collection space-separated (or `(empty)`); `first` prints the first item or `none`; `count` prints the size. A step that doesn't apply to the current element type (e.g. `map upper` on numbers) prints `cannot <step> <numbers|words>` and changes nothing.",
     "`chunk <n>` prints the chunks as `[a b] [c]`; `groupBy` prints `<key>: <items>` per group in first-seen order. Neither changes the collection.",
     "Implement `Collection<T>` with generic methods — `map<U>(fn: (x: T) => U): Collection<U>` and friends — so that the element type is tracked at every step.",
     "`sortBy` is stable and ascending; `length` compares the printed length of each item."],
    r"""
class Collection<T> {
  readonly items: readonly T[];
  constructor(items: readonly T[]) {
    this.items = items;
  }
  map<U>(fn: (x: T) => U): Collection<U> {
    return new Collection(this.items.map(fn));
  }
  filter(test: (x: T) => boolean): Collection<T> {
    return new Collection(this.items.filter(test));
  }
  sortBy(score: (x: T) => number): Collection<T> {
    return new Collection(this.items.toSorted((a, b) => score(a) - score(b)));
  }
  unique(): Collection<T> {
    return new Collection([...new Set(this.items)]);
  }
  take(n: number): Collection<T> {
    return new Collection(this.items.slice(0, n));
  }
  chunk(n: number): T[][] {
    const out: T[][] = [];
    for (let i = 0; i < this.items.length; i += n) out.push(this.items.slice(i, i + n));
    return out;
  }
  groupBy<K>(keyOf: (x: T) => K): Map<K, T[]> {
    const groups = new Map<K, T[]>();
    for (const x of this.items) groups.set(keyOf(x), [...(groups.get(keyOf(x)) ?? []), x]);
    return groups;
  }
  first(): T | undefined {
    return this.items[0];
  }
  toString(): string {
    return this.items.join(" ") || "(empty)";
  }
}
type Current = { kind: "numbers"; c: Collection<number> } | { kind: "words"; c: Collection<string> };
const [head = "", ...steps] = input.split("\n");
const [kind = "", ...values] = head.trim().split(/\s+/);
let cur: Current = kind === "numbers" ? { kind: "numbers", c: new Collection(values.map(Number)) } : { kind: "words", c: new Collection(values) };
function apply(cur: Current, cmd: string, arg: string): Current | string {
  const n = Number(arg);
  if (cmd === "take") return cur.kind === "numbers" ? { kind: "numbers", c: cur.c.take(n) } : { kind: "words", c: cur.c.take(n) };
  if (cmd === "unique") return cur.kind === "numbers" ? { kind: "numbers", c: cur.c.unique() } : { kind: "words", c: cur.c.unique() };
  if (cmd === "sortBy" && (arg === "value" || arg === "length")) {
    if (cur.kind === "numbers") return { kind: "numbers", c: cur.c.sortBy((x) => (arg === "value" ? x : String(x).length)) };
    if (arg === "length") return { kind: "words", c: cur.c.sortBy((w) => w.length) };
  }
  if (cur.kind === "numbers") {
    if (cmd === "map" && arg === "double") return { kind: "numbers", c: cur.c.map((x) => x * 2) };
    if (cmd === "map" && arg === "square") return { kind: "numbers", c: cur.c.map((x) => x * x) };
    if (cmd === "filter" && arg === "even") return { kind: "numbers", c: cur.c.filter((x) => x % 2 === 0) };
    if (cmd === "filter" && arg === "odd") return { kind: "numbers", c: cur.c.filter((x) => x % 2 !== 0) };
  } else {
    if (cmd === "map" && arg === "upper") return { kind: "words", c: cur.c.map((w) => w.toUpperCase()) };
    if (cmd === "map" && arg === "length") return { kind: "numbers", c: cur.c.map((w) => w.length) };
    if (cmd === "filter" && arg === "long") return { kind: "words", c: cur.c.filter((w) => w.length > 3) };
  }
  return `cannot ${cmd}${arg === "" ? "" : " " + arg} ${cur.kind}`;
}
for (const step of steps) {
  const [cmd = "", arg = ""] = step.trim().split(/\s+/);
  if (cmd === "first") {
    console.log(cur.c.first() ?? "none");
  } else if (cmd === "count") {
    console.log(cur.c.items.length);
  } else if (cmd === "chunk") {
    const chunks: readonly (readonly (string | number)[])[] = cur.kind === "numbers" ? cur.c.chunk(Number(arg)) : cur.c.chunk(Number(arg));
    console.log(chunks.map((c) => `[${c.join(" ")}]`).join(" "));
  } else if (cmd === "groupBy" && (arg === "length" || (arg === "parity" && cur.kind === "numbers"))) {
    const groups: Map<string, (string | number)[]> = cur.kind === "numbers"
      ? cur.c.groupBy((x) => (arg === "parity" ? (x % 2 === 0 ? "even" : "odd") : String(String(x).length)))
      : cur.c.groupBy((w) => String(w.length));
    for (const [k, items] of groups) console.log(`${k}: ${items.join(" ")}`);
  } else if (cmd === "groupBy") {
    console.log(`cannot groupBy ${arg} ${cur.kind}`);
  } else {
    const next = apply(cur, cmd, arg);
    if (typeof next === "string") {
      console.log(next);
    } else {
      cur = next;
      console.log(String(cur.c));
    }
  }
}
""", ["numbers 5 3 8 3 10 1\nunique\nfilter even\nmap square\nfirst\ncount",
      "words the quick brown fox jumps\nfilter long\nmap upper\nsortBy length\nchunk 2\ngroupBy length",
      "numbers 4 1 3\nmap upper\nsortBy value\ntake 2\ngroupBy parity\nmap double",
      "words a bb a ccc\nunique\nmap length\nmap double\nfilter odd\nfirst",
      "words solo\ngroupBy parity\ntake 0\nfirst\ncount"],
    stretch=["Add `reduce<U>(fn: (acc: U, x: T) => U, start: U): U` and a `sum` step that only type-checks for `Collection<number>` (hint: a `this` parameter, `sum(this: Collection<number>)`).",
             "Make `Collection` iterable (`[Symbol.iterator]`) — week 24 teaches how."],
)

TS_PRACTICE_MORE[18] = [
    _pr("tsm-w18-p9", "An inferred generic call", 'function wrap<T>(value: T) {\n  return [value];\n}\nconst boxed = wrap("ok");\n', "boxed", "string[]",
        strictness=_SI, hints=["The literal `\"ok\"` widens when `T` is inferred.", "So `T` is `string` and the result is `string[]`."]),
    _dx("tsm-w18-d9", "A generic that promises too much",
        "error TS2322: Type 'number' is not assignable to type 'T'.",
        'function orZero<T>(value: T | undefined): T {\n  return value ?? 0;\n}\nconsole.log(orZero<number>(undefined) + 1);\n',
        'function orDefault<T>(value: T | undefined, fallback: T): T {\n  return value ?? fallback;\n}\nconsole.log(orDefault<number>(undefined, 0) + 1);\n',
        [("", "1")], strictness=_SI, ask="Let the caller supply the fallback, so it has the caller's type.",
        hints=["`0` is a number, and `T` might be anything.", "Take the fallback as a parameter of type `T`."], difficulty="Medium"),
]

TS_CARDS_MORE[18] = [
    ("Where do inferred type arguments come from?", "Candidates from the arguments (and the contextual return type); literals widen unless the parameter is `const` or constrained."),
    ("What does `<const T extends readonly unknown[]>` do?", "Infers the argument as if written with `as const` — exact tuples and literal types (TS 5.0)."),
    ("What is `NoInfer<T>` for?", "Excluding one argument from inference so it is only checked against `T` — e.g. a fallback that must be one of the options (TS 5.4)."),
    ("`box([])` gives `T` = ?", "`never` — nothing to infer from. Write `box<string>([])`."),
    ("When does a default type argument `<T = string>` apply?", "Only when there is no explicit argument and nothing to infer."),
    ("A type parameter that appears once — what's wrong?", "It relates nothing to anything; use `unknown` (or a real constraint) instead."),
]

# ===========================================================================
# Week 19 — keyof, typeof, indexed access, lookup types
# ===========================================================================

TS_PROBLEM_SETS[19] = [
    _tsp(19, "tsm-w19-status-codes", "Status names and codes, both ways", "warm-up",
         "Declare `const STATUS = { OK: 200, CREATED: 201, NOT_FOUND: 404, CONFLICT: 409, SERVER_ERROR: 500 } as const` and derive `StatusName` and `StatusCode` from it. Each input line is a name or a code: print `<name> = <code>` for a known one, else `unknown <x>`. Finish with the codes of the 4xx statuses, ascending.",
         r"""
const STATUS = { OK: 200, CREATED: 201, NOT_FOUND: 404, CONFLICT: 409, SERVER_ERROR: 500 } as const;
type StatusName = keyof typeof STATUS;
type StatusCode = (typeof STATUS)[StatusName];
const names = Object.keys(STATUS) as StatusName[];
const nameOf = (code: number): StatusName | undefined => names.find((n) => STATUS[n] === code);
const isName = (s: string): s is StatusName => Object.hasOwn(STATUS, s);
for (const line of input.split("\n")) {
  const t = line.trim();
  const byCode = /^\d+$/.test(t) ? nameOf(Number(t)) : undefined;
  if (isName(t)) console.log(`${t} = ${STATUS[t]}`);
  else if (byCode !== undefined) console.log(`${byCode} = ${STATUS[byCode]}`);
  else console.log(`unknown ${t}`);
}
const clientErrors: StatusCode[] = names.map((n) => STATUS[n]).filter((c) => c >= 400 && c < 500);
console.log(clientErrors.sort((a, b) => a - b).join(" "));
""", ["OK\n404\nCONFLICT\n418\nnot_found", "500"],
         hints=["`keyof typeof STATUS` for the names; index `typeof STATUS` by them for the codes."]),
    _tsp(19, "tsm-w19-settings-io", "Typed get and set", "warm-up",
         "Settings have defaults `{ volume: 5, muted: false, theme: \"light\", name: \"guest\" }`. Write `get<K extends keyof Settings>(key: K): Settings[K]` and `set<K extends keyof Settings>(key: K, value: Settings[K])`. Each input line is `get <key>` or `set <key> <text>`: convert the text to the key's type (the default's `typeof` decides — `true`/`false` for booleans, a finite number for numbers). Print the value after each command, or `unknown key <k>` / `bad value <text> for <key>`.",
         r"""
const defaults = { volume: 5, muted: false, theme: "light", name: "guest" };
type Settings = typeof defaults;
const settings: Settings = { ...defaults };
function get<K extends keyof Settings>(key: K): Settings[K] {
  return settings[key];
}
function set<K extends keyof Settings>(key: K, value: Settings[K]): void {
  settings[key] = value;
}
const isKey = (s: string): s is keyof Settings => Object.hasOwn(defaults, s);
function convert(key: keyof Settings, text: string): Settings[keyof Settings] | undefined {
  const kind = typeof defaults[key];
  if (kind === "number") return text !== "" && Number.isFinite(Number(text)) ? Number(text) : undefined;
  if (kind === "boolean") return text === "true" ? true : text === "false" ? false : undefined;
  return text;
}
for (const line of input.split("\n")) {
  const [cmd = "", key = "", ...rest] = line.trim().split(/\s+/);
  if (!isKey(key)) {
    console.log(`unknown key ${key}`);
    continue;
  }
  if (cmd === "set") {
    const text = rest.join(" ");
    const value = convert(key, text);
    if (value === undefined) {
      console.log(`bad value ${text} for ${key}`);
      continue;
    }
    set(key, value as Settings[typeof key]);
  }
  console.log(`${key} = ${get(key)}`);
}
""", ["get volume\nset volume 8\nset muted yes\nset muted true\nset theme dark\nget colour\nset name Ana Lee", "set volume loud\nget name"],
         hints=["`Settings[K]` follows the key: `get(\"muted\")` is a `boolean`.",
                "Decide how to parse the text from the *default value's* runtime type."]),
    _tsp(19, "tsm-w19-columns", "A table printer driven by column types", "core",
         "Rows are `{ name: string; qty: number; price: number; inStock: boolean }`. The columns are one `as const` list of `{ key, title, width }` checked with `satisfies readonly Column[]` where `key` is a `keyof Row`. The first input line lists the column keys to show (comma-separated); each later line is a CSV row `name,qty,price,inStock`. Print a header of the titles, then each row — text left-aligned, numbers right-aligned, booleans as `yes`/`no`, each padded to the column's width and separated by ` | ` — or `unknown column <k>`.",
         r"""
type Row = { name: string; qty: number; price: number; inStock: boolean };
type Column = { key: keyof Row; title: string; width: number };
const COLUMNS = [
  { key: "name", title: "Item", width: 8 },
  { key: "qty", title: "Qty", width: 4 },
  { key: "price", title: "Price", width: 7 },
  { key: "inStock", title: "Stock", width: 5 },
] as const satisfies readonly Column[];
type ColumnKey = (typeof COLUMNS)[number]["key"];
const findColumn = (k: string) => COLUMNS.find((c) => c.key === k);
function cell(row: Row, key: ColumnKey, width: number): string {
  const v = row[key];
  if (typeof v === "number") return (key === "price" ? v.toFixed(2) : String(v)).padStart(width);
  if (typeof v === "boolean") return (v ? "yes" : "no").padEnd(width);
  return v.padEnd(width);
}
const [header = "", ...lines] = input.split("\n");
const wanted = header.split(",").map((k) => k.trim());
const unknown = wanted.find((k) => findColumn(k) === undefined);
if (unknown !== undefined) {
  console.log(`unknown column ${unknown}`);
} else {
  const cols = wanted.flatMap((k) => {
    const c = findColumn(k);
    return c === undefined ? [] : [c];
  });
  console.log(cols.map((c) => c.title.padEnd(c.width)).join(" | ").trimEnd());
  for (const line of lines) {
    const [name = "", qty = "0", price = "0", stock = ""] = line.split(",");
    const row: Row = { name, qty: Number(qty), price: Number(price), inStock: stock.trim() === "true" };
    console.log(cols.map((c) => cell(row, c.key, c.width)).join(" | ").trimEnd());
  }
}
""", ["name,qty,price,inStock\npen,12,1.5,true\nnotebook,3,4.25,false", "price,name\ncup,1,3,true", "name,colour\nx,1,1,true"],
         hints=["`(typeof COLUMNS)[number][\"key\"]` is the union of keys the columns actually use.",
                "`row[key]` is `string | number | boolean`; narrow with `typeof` to format it."]),
    _tsp(19, "tsm-w19-i18n", "Messages with a fallback language", "core",
         "Messages live in one nested object: `en` and `de`, each with `home.title`, `home.greeting` (containing `{name}`) and `cart.items` (containing `{count}`); `de` is missing `cart.items`. Each input line is `<lang> <section>.<key> [param=value …]`. Print the message with every `{param}` replaced — falling back to `en` when the language lacks that key — or `unknown language <l>` / `unknown message <path>`. A placeholder without a value stays as it is.",
         r"""
const MESSAGES = {
  en: {
    home: { title: "Welcome", greeting: "Hello, {name}!" },
    cart: { items: "You have {count} items" },
  },
  de: {
    home: { title: "Willkommen", greeting: "Hallo, {name}!" },
    cart: {},
  },
} as const;
type Lang = keyof typeof MESSAGES;
type Section = keyof (typeof MESSAGES)["en"];
const isLang = (s: string): s is Lang => Object.hasOwn(MESSAGES, s);
const isSection = (s: string): s is Section => Object.hasOwn(MESSAGES.en, s);
function lookup(lang: Lang, section: Section, key: string): string | undefined {
  const table: Record<string, string> = MESSAGES[lang][section];
  return Object.hasOwn(table, key) ? table[key] : undefined;
}
for (const line of input.split("\n")) {
  const [lang = "", path = "", ...params] = line.trim().split(/\s+/);
  const [section = "", key = ""] = path.split(".");
  if (!isLang(lang)) {
    console.log(`unknown language ${lang}`);
    continue;
  }
  const message = isSection(section) ? lookup(lang, section, key) ?? lookup("en", section, key) : undefined;
  if (message === undefined) {
    console.log(`unknown message ${path}`);
    continue;
  }
  const values = new Map(params.map((p) => [p.slice(0, p.indexOf("=")), p.slice(p.indexOf("=") + 1)] as const));
  console.log(message.replace(/\{(\w+)\}/g, (whole, name: string) => values.get(name) ?? whole));
}
""", ["en home.title\nde home.greeting name=Ana\nde cart.items count=3\nfr home.title\nen home.farewell\nen cart.items", "de home.title\nen blog.title"],
         hints=["`(typeof MESSAGES)[\"en\"]` describes one language's sections; `keyof` it for the section names.",
                "Read a language's section as `Record<string, string>` to look up a key you only know at runtime."]),
    _tsp(19, "tsm-w19-order-report", "A report from a lookup table", "stretch",
         "Products are one `as const` table keyed by SKU, each `{ name, price, category }` with category `food`, `tools` or `toys`. Derive `Sku` and `Category` from the table. Each input line is `<sku> <qty>`; unknown SKUs print `unknown sku <s>`. Then print each category (in the order `food`, `tools`, `toys`) as `<category>: <units> units, $<total>` (`unit` for one), and finally `best seller: <name>` by units (first on a tie; `none` if nothing sold).",
         r"""
const PRODUCTS = {
  A1: { name: "apple", price: 0.5, category: "food" },
  B2: { name: "bread", price: 2.25, category: "food" },
  H3: { name: "hammer", price: 12, category: "tools" },
  Y4: { name: "yo-yo", price: 3.5, category: "toys" },
} as const;
type Sku = keyof typeof PRODUCTS;
type Category = (typeof PRODUCTS)[Sku]["category"];
const CATEGORIES: readonly Category[] = ["food", "tools", "toys"];
const isSku = (s: string): s is Sku => Object.hasOwn(PRODUCTS, s);
const units = new Map<Sku, number>();
for (const line of input.split("\n")) {
  const [sku = "", qty = "0"] = line.trim().split(/\s+/);
  if (!isSku(sku)) {
    console.log(`unknown sku ${sku}`);
    continue;
  }
  units.set(sku, (units.get(sku) ?? 0) + Number(qty));
}
const skus = Object.keys(PRODUCTS) as Sku[];
for (const cat of CATEGORIES) {
  const inCat = skus.filter((s) => PRODUCTS[s].category === cat);
  const count = inCat.reduce((n, s) => n + (units.get(s) ?? 0), 0);
  const total = inCat.reduce((t, s) => t + (units.get(s) ?? 0) * PRODUCTS[s].price, 0);
  console.log(`${cat}: ${count} ${count === 1 ? "unit" : "units"}, $${total.toFixed(2)}`);
}
const best = skus.filter((s) => (units.get(s) ?? 0) > 0).sort((a, b) => (units.get(b) ?? 0) - (units.get(a) ?? 0))[0];
console.log(`best seller: ${best === undefined ? "none" : PRODUCTS[best].name}`);
""", ["A1 6\nH3 1\nY4 2\nZZ 1\nA1 4\nB2 1", "Q9 3"],
         hints=["`(typeof PRODUCTS)[Sku][\"category\"]` is the union of every product's category literal."]),
    _tsp_types(19, "tsm-w19-tuple-union", "A union from a tuple", "warm-up",
               "Write `TupleToUnion<T>`: the union of a tuple's element types.",
               '''
type TupleToUnion<T extends readonly unknown[]> = T[number];
''', "T[number]",
               '''
type _1 = Expect<Equal<TupleToUnion<["a", 1, true]>, "a" | 1 | true>>;
type _2 = Expect<Equal<TupleToUnion<readonly ["x"]>, "x">>;
type _3 = Expect<Equal<TupleToUnion<[]>, never>>;
''', hints=["Index the tuple type with `number`."]),
    _tsp_types(19, "tsm-w19-keys-of-type", "Keys whose values have a type", "core",
               "Write `KeysOfType<T, V>`: the union of `T`'s keys whose property type is assignable to `V`.",
               '''
type KeysOfType<T, V> = { [K in keyof T]: T[K] extends V ? K : never }[keyof T];
''', "{ [K in keyof T]: T[K] extends V ? K : never }[keyof T]",
               '''
type User = { id: number; name: string; email: string; age: number; admin: boolean };
type _1 = Expect<Equal<KeysOfType<User, string>, "name" | "email">>;
type _2 = Expect<Equal<KeysOfType<User, number>, "id" | "age">>;
type _3 = Expect<Equal<KeysOfType<User, Date>, never>>;
''', hints=["Map every key to itself or to `never`, then look up all the values at once with `[keyof T]`.",
            "`never` members disappear from the resulting union."]),
    _tsp_types(19, "tsm-w19-deep-lookup", "Reach into a nested type", "warm-up",
               "Derive `ButtonColour` — the type of the button's `colour` in the theme — and `Spacing`, the union of the spacing scale's values, by looking them up in `Theme`.",
               '''
type Theme = {
  spacing: readonly [4, 8, 16, 32];
  components: { button: { colour: "primary" | "danger"; size: number }; card: { shadow: boolean } };
};
type ButtonColour = Theme["components"]["button"]["colour"];
type Spacing = Theme["spacing"][number];
''', 'Theme["components"]["button"]["colour"]',
               '''
type _1 = Expect<Equal<ButtonColour, "primary" | "danger">>;
type _2 = Expect<Equal<Spacing, 4 | 8 | 16 | 32>>;
''', hints=["Chain indexed accesses, one property at a time."]),
]

TS_PROJECTS[19] = _project(
    19, "settings.ts — settings from one source of truth",
    "Every setting is declared once, with its default and (optionally) its allowed values; the key union, the value types, parsing, validation, reset and export all follow from that declaration. Adding a setting must be a one-line change.",
    ["Declare `const DEFAULTS = { theme: \"light\", fontSize: 14, autosave: true, language: \"en\", tabWidth: 2 }` and `const CHOICES = { theme: [\"light\", \"dark\", \"system\"], language: [\"en\", \"de\", \"ja\"], tabWidth: [2, 4, 8] }`; derive `SettingKey` and `Settings` from `DEFAULTS`.",
     "Commands: `get <key>` prints `<key> = <value>`; `set <key> <value>` converts the text to the setting's type (by its default: numbers must be finite, booleans `true`/`false`) and, if the key has choices, checks it is one of them, then prints `<key> = <value>`; `reset <key>` restores the default and prints it.",
     "Errors: `unknown setting <k>`, `<key> expects a number|boolean`, `<key> must be one of <choices, comma-separated>`.",
     "`diff` prints every setting that differs from its default as `<key>: <default> -> <value>` (in declaration order), or `no changes`; `export` prints the settings as JSON with keys sorted.",
     "No setting name may be written anywhere except in `DEFAULTS` and `CHOICES` — every other use is derived."],
    r"""
const DEFAULTS = { theme: "light", fontSize: 14, autosave: true, language: "en", tabWidth: 2 };
const CHOICES: { [K in SettingKey]?: readonly Settings[K][] } = {
  theme: ["light", "dark", "system"],
  language: ["en", "de", "ja"],
  tabWidth: [2, 4, 8],
};
type Settings = typeof DEFAULTS;
type SettingKey = keyof Settings;
const KEYS = Object.keys(DEFAULTS) as SettingKey[];
const isKey = (s: string): s is SettingKey => Object.hasOwn(DEFAULTS, s);
const current: Settings = { ...DEFAULTS };

type Parsed = { ok: true; value: Settings[SettingKey] } | { ok: false; error: string };
function parseValue(key: SettingKey, text: string): Parsed {
  const kind = typeof DEFAULTS[key];
  let value: Settings[SettingKey];
  if (kind === "number") {
    if (text === "" || !Number.isFinite(Number(text))) return { ok: false, error: `${key} expects a number` };
    value = Number(text);
  } else if (kind === "boolean") {
    if (text !== "true" && text !== "false") return { ok: false, error: `${key} expects a boolean` };
    value = text === "true";
  } else {
    value = text;
  }
  const choices: readonly Settings[SettingKey][] | undefined = CHOICES[key];
  if (choices !== undefined && !choices.includes(value)) return { ok: false, error: `${key} must be one of ${choices.join(",")}` };
  return { ok: true, value };
}
function assign<K extends SettingKey>(key: K, value: Settings[K]): void {
  current[key] = value;
}

for (const line of input.split("\n")) {
  const [cmd = "", key = "", ...rest] = line.trim().split(/\s+/);
  if (cmd === "diff") {
    const changed = KEYS.filter((k) => current[k] !== DEFAULTS[k]);
    if (changed.length === 0) console.log("no changes");
    for (const k of changed) console.log(`${k}: ${DEFAULTS[k]} -> ${current[k]}`);
    continue;
  }
  if (cmd === "export") {
    console.log(JSON.stringify(Object.fromEntries([...KEYS].sort().map((k) => [k, current[k]]))));
    continue;
  }
  if (!isKey(key)) {
    console.log(`unknown setting ${key}`);
    continue;
  }
  if (cmd === "set") {
    const parsed = parseValue(key, rest.join(" "));
    if (!parsed.ok) {
      console.log(parsed.error);
      continue;
    }
    assign(key, parsed.value as Settings[typeof key]);
  } else if (cmd === "reset") {
    assign(key, DEFAULTS[key]);
  }
  console.log(`${key} = ${current[key]}`);
}
""", ["get theme\nset theme dark\nset fontSize 16\nset autosave false\ndiff\nexport",
      "set theme blue\nset tabWidth 3\nset tabWidth 4\nset fontSize big\nset autosave maybe\nset colour red",
      "diff\nset language ja\nreset language\ndiff",
      "set fontSize 12.5\nget fontSize\nreset fontSize\nget fontSize\nexport",
      "set language de\nset theme system\nset tabWidth 8\ndiff"],
    stretch=["Make `set` fully type-safe for callers in code: `set(\"fontSize\", \"big\")` should be a compile error — it already is with `assign`; find where the program needed a cast and remove it.",
             "Add a `validate` hook per setting (e.g. `fontSize` between 8 and 72) declared next to its default."],
)

TS_PRACTICE_MORE[19] = [
    _pr("tsm-w19-p9", "A lookup through a table's values", 'const LIMITS = { free: 3, pro: 50 } as const;\nconst limit = LIMITS.pro;\n', "limit", "50",
        strictness=_SI, hints=["`as const` keeps each value's literal type.", "The property `pro` is exactly `50`."]),
    _dx("tsm-w19-d9", "A string used as a key",
        "error TS7053: Element implicitly has an 'any' type because expression of type 'string' can't be used to index type '{ readonly S: 10; readonly M: 12; }'.",
        _STDIN + 'const PRICES = { S: 10, M: 12 } as const;\nconsole.log(PRICES[input] ?? "unknown size");\n',
        _STDIN + 'const PRICES = { S: 10, M: 12 } as const;\nconst isSize = (s: string): s is keyof typeof PRICES => Object.hasOwn(PRICES, s);\nconsole.log(isSize(input) ? PRICES[input] : "unknown size");\n',
        [("M", "12"), ("XL", "unknown size")], strictness=_SI,
        hints=["Not every string is a key of `PRICES`.", "Narrow the input to `keyof typeof PRICES` first."], difficulty="Medium"),
]

TS_CARDS_MORE[19] = [
    ("`User[\"role\"]`?", "An indexed access type: the type of `User`'s `role` property."),
    ("Element type of `string[][]`'s inner arrays?", "`string[][][number][number]` — or just `string`; `[number]` reads an array's element type."),
    ("`(typeof X)[number]` for `const X = [\"a\", \"b\"] as const`?", "`\"a\" | \"b\"` — a union from a constant list."),
    ("`User[\"id\" | \"email\"]`?", "The union of both properties' types — a union key gives a union."),
    ("Why doesn't `Object.keys` return `(keyof T)[]`?", "Objects can have more keys at runtime than their type lists; `string[]` is the honest type."),
    ("The typed property read, as a signature?", "`function get<T, K extends keyof T>(obj: T, key: K): T[K]`."),
]

# ===========================================================================
# Week 20 — Mapped types, key remapping
# ===========================================================================

TS_PROBLEM_SETS[20] = [
    _tsp(20, "tsm-w20-permissions", "A permission matrix", "warm-up",
         "Roles are `viewer`, `editor`, `admin` and permissions `read`, `write`, `delete`, `invite`, each declared once `as const`. The matrix is typed as a mapped type — `{ [R in Role]: { [P in Perm]: boolean } }` — so every cell must be filled: viewers read; editors read and write; admins do everything. Each input line is `can <role> <perm>` (print `yes`/`no`), `row <role>` (the role's permissions, in order) or `who <perm>` (the roles that have it). Unknown names print `unknown <name>`.",
         r"""
const ROLES = ["viewer", "editor", "admin"] as const;
const PERMS = ["read", "write", "delete", "invite"] as const;
type Role = (typeof ROLES)[number];
type Perm = (typeof PERMS)[number];
type Matrix = { [R in Role]: { [P in Perm]: boolean } };
const MATRIX: Matrix = {
  viewer: { read: true, write: false, delete: false, invite: false },
  editor: { read: true, write: true, delete: false, invite: false },
  admin: { read: true, write: true, delete: true, invite: true },
};
const asRole = (s: string): Role | undefined => ROLES.find((r) => r === s);
const asPerm = (s: string): Perm | undefined => PERMS.find((p) => p === s);
for (const line of input.split("\n")) {
  const [cmd = "", a = "", b = ""] = line.trim().split(/\s+/);
  if (cmd === "can") {
    const role = asRole(a);
    const perm = asPerm(b);
    if (role === undefined) console.log(`unknown ${a}`);
    else if (perm === undefined) console.log(`unknown ${b}`);
    else console.log(MATRIX[role][perm] ? "yes" : "no");
  } else if (cmd === "row") {
    const role = asRole(a);
    console.log(role === undefined ? `unknown ${a}` : PERMS.filter((p) => MATRIX[role][p]).join(" "));
  } else if (cmd === "who") {
    const perm = asPerm(a);
    console.log(perm === undefined ? `unknown ${a}` : ROLES.filter((r) => MATRIX[r][perm]).join(" "));
  }
}
""", ["can editor write\ncan viewer delete\nrow editor\nwho invite\nwho read\ncan owner read\nrow admin", "who share\ncan admin fly"],
         hints=["A nested mapped type makes a missing cell a compile error.", "`ROLES.find((r) => r === s)` turns an input string into a `Role`."]),
    _tsp(20, "tsm-w20-form-state", "Form state for every field", "core",
         "A sign-up model is `{ email: string; age: number; terms: boolean }`. Its form state is the mapped type `{ [K in keyof T]: { value: T[K]; touched: boolean; error?: string } }`, starting at `\"\"`, `0`, `false`, untouched. Commands: `set <field> <text>` (converted to the field's type and marks it touched; a bad number or boolean prints `bad value`), `validate` (email must contain `@`, age at least 18, terms `true`; prints `valid` or `<k> errors`), `show` (each field as `<field>=<value>` plus ` *` if touched and ` !<error>` if it has one, space-separated). Unknown fields print `unknown field <f>`.",
         r"""
type Signup = { email: string; age: number; terms: boolean };
type FieldState<V> = { value: V; touched: boolean; error?: string };
type FormState<T> = { [K in keyof T]: FieldState<T[K]> };
const FIELDS = ["email", "age", "terms"] as const satisfies readonly (keyof Signup)[];
const form: FormState<Signup> = {
  email: { value: "", touched: false },
  age: { value: 0, touched: false },
  terms: { value: false, touched: false },
};
const asField = (s: string) => FIELDS.find((f) => f === s);
function setField(field: keyof Signup, text: string): boolean {
  if (field === "email") form.email = { value: text, touched: true };
  else if (field === "age") {
    if (!/^\d+$/.test(text)) return false;
    form.age = { value: Number(text), touched: true };
  } else {
    if (text !== "true" && text !== "false") return false;
    form.terms = { value: text === "true", touched: true };
  }
  return true;
}
function validate(): number {
  const rules: { [K in keyof Signup]: (v: Signup[K]) => string | undefined } = {
    email: (v) => (v.includes("@") ? undefined : "email"),
    age: (v) => (v >= 18 ? undefined : "too young"),
    terms: (v) => (v ? undefined : "must accept"),
  };
  let errors = 0;
  for (const f of FIELDS) {
    const error = f === "email" ? rules.email(form.email.value) : f === "age" ? rules.age(form.age.value) : rules.terms(form.terms.value);
    if (error === undefined) delete form[f].error;
    else {
      form[f].error = error;
      errors++;
    }
  }
  return errors;
}
for (const line of input.split("\n")) {
  const [cmd = "", name = "", ...rest] = line.trim().split(/\s+/);
  if (cmd === "set") {
    const field = asField(name);
    if (field === undefined) console.log(`unknown field ${name}`);
    else if (!setField(field, rest.join(" "))) console.log("bad value");
  } else if (cmd === "validate") {
    const n = validate();
    console.log(n === 0 ? "valid" : `${n} errors`);
  } else if (cmd === "show") {
    console.log(FIELDS.map((f) => `${f}=${form[f].value}${form[f].touched ? " *" : ""}${form[f].error === undefined ? "" : ` !${form[f].error}`}`).join(" "));
  }
}
""", ["show\nset email ana\nset age 17\nvalidate\nshow\nset email ana@x.io\nset age 30\nset terms true\nvalidate\nshow", "set age old\nset terms yes\nset phone 1\nvalidate"],
         hints=["`FieldState<T[K]>` gives each field's state the right value type.", "A mapped type of validators, `{ [K in keyof T]: (v: T[K]) => … }`, keeps each rule's parameter typed."]),
    _tsp(20, "tsm-w20-changes", "A change log with remapped keys", "core",
         "The input is pairs of lines: a JSON object before and after an edit (flat, same keys possible on both sides). Describe the difference as a `Changes<T>` object whose keys are `<key>Changed` — built with a key-remapping mapped type — and print its entries sorted by key as `<key>Changed: <from> -> <to>` (values as JSON, `missing` for an absent side), or `no changes`. Separate pairs with a line `--`.",
         r"""
type Changes<T> = { [K in keyof T as `${string & K}Changed`]?: { from: T[K] | undefined; to: T[K] | undefined } };
type Flat = Record<string, unknown>;
function diff(before: Flat, after: Flat): Changes<Flat> {
  const changes: Record<string, { from: unknown; to: unknown }> = {};
  for (const key of new Set([...Object.keys(before), ...Object.keys(after)])) {
    const from = before[key];
    const to = after[key];
    if (JSON.stringify(from) !== JSON.stringify(to)) changes[`${key}Changed`] = { from, to };
  }
  return changes as Changes<Flat>;
}
const show = (v: unknown) => (v === undefined ? "missing" : JSON.stringify(v));
const lines = input.split("\n");
for (let i = 0; i + 1 < lines.length; i += 2) {
  if (i > 0) console.log("--");
  const changes = diff(JSON.parse(lines[i] ?? "{}") as Flat, JSON.parse(lines[i + 1] ?? "{}") as Flat);
  const entries = Object.entries(changes).sort(([a], [b]) => a.localeCompare(b));
  if (entries.length === 0) console.log("no changes");
  for (const [key, change] of entries) console.log(`${key}: ${show(change?.from)} -> ${show(change?.to)}`);
}
""", ['{"name":"ana","age":31,"city":"Oslo"}\n{"name":"Ana","age":31,"zip":"0150"}\n{"x":1}\n{"x":1}\n{"tags":["a"]}\n{"tags":["a","b"]}'],
         hints=["`` `${string & K}Changed` `` renames every key; the value type still uses the original `T[K]`.",
                "Compare values with `JSON.stringify` so arrays and objects compare by content."]),
    _tsp_types(20, "tsm-w20-my-record", "Record, by hand", "warm-up",
               "Write `MyRecord<K, V>`: an object type with every key in `K`, each of type `V`.",
               '''
type MyRecord<K extends PropertyKey, V> = { [P in K]: V };
''', "{ [P in K]: V }",
               '''
type _1 = Expect<Equal<MyRecord<"a" | "b", number>, { a: number; b: number }>>;
type _2 = Expect<Equal<MyRecord<"only", string[]>, { only: string[] }>>;
type _3 = Expect<Equal<MyRecord<never, number>, {}>>;
''', hints=["Map over the key union itself, not over `keyof` something."]),
    _tsp_types(20, "tsm-w20-omit-by-value", "Omit by value type", "core",
               "Write `OmitByValue<T, V>`: `T` without the properties whose type is assignable to `V`.",
               '''
type OmitByValue<T, V> = { [K in keyof T as T[K] extends V ? never : K]: T[K] };
''', "{ [K in keyof T as T[K] extends V ? never : K]: T[K] }",
               '''
type Model = { id: number; name: string; save: () => void; load: () => void; count: number };
type _1 = Expect<Equal<OmitByValue<Model, () => void>, { id: number; name: string; count: number }>>;
type _2 = Expect<Equal<OmitByValue<Model, number>, { name: string; save: () => void; load: () => void }>>;
''', hints=["Use an `as` clause and map unwanted keys to `never`."]),
    _tsp_types(20, "tsm-w20-setters", "Setters by remapping", "core",
               "Write `Setters<T>`: for each property `k` of `T`, a method `set<K>` (capitalised) taking the property's type and returning `void`.",
               '''
type Setters<T> = { [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void };
''', "{ [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void }",
               '''
type _1 = Expect<Equal<Setters<{ name: string; age: number }>, { setName: (value: string) => void; setAge: (value: number) => void }>>;
type _2 = Expect<Equal<Setters<{ [1]: boolean }>, {}>>;
''', hints=["`` `set${Capitalize<string & K>}` `` builds the name; `string & K` drops non-string keys."]),
    _tsp_types(20, "tsm-w20-deep-readonly", "Readonly all the way down", "stretch",
               "Write `DeepReadonly<T>`: every property at every depth becomes `readonly`, and arrays become readonly arrays of deeply readonly elements — but functions are left as they are.",
               '''
type DeepReadonly<T> = T extends (...args: never[]) => unknown
  ? T
  : T extends object
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T;
''', '''T extends (...args: never[]) => unknown
  ? T
  : T extends object
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T''',
               '''
type Config = { name: string; db: { hosts: string[]; port: number }; onLoad: () => void };
type _1 = Expect<Equal<DeepReadonly<Config>, {
  readonly name: string;
  readonly db: { readonly hosts: readonly string[]; readonly port: number };
  readonly onLoad: () => void;
}>>;
type _2 = Expect<Equal<DeepReadonly<number>, number>>;
''', hints=["Three cases: functions (leave them), objects and arrays (map with `readonly`, recursing), primitives.",
            "A homomorphic mapped type over an array type produces an array — `readonly` included."]),
    _tsp_types(20, "tsm-w20-optional-keys", "Which keys are optional?", "stretch",
               "Write `OptionalKeys<T>`: the union of `T`'s optional keys (declared with `?`) — not keys whose type merely includes `undefined`.",
               '''
type OptionalKeys<T> = { [K in keyof T]-?: {} extends Pick<T, K> ? K : never }[keyof T];
''', "{ [K in keyof T]-?: {} extends Pick<T, K> ? K : never }[keyof T]",
               '''
type _1 = Expect<Equal<OptionalKeys<{ a: number; b?: string; c?: boolean; d: number | undefined }>, "b" | "c">>;
type _2 = Expect<Equal<OptionalKeys<{ a: 1 }>, never>>;
''', hints=["`{}` is assignable to `Pick<T, K>` exactly when `K` is optional in `T`.",
            "`-?` stops the mapped type's own optionality from adding `undefined` to the looked-up union."]),
]

TS_PROJECTS[20] = _project(
    20, "store.ts — a typed store with watchers and undo",
    "A small state container: `createStore<T>(initial)` returns typed `get`/`set` keyed by `keyof T`, per-key watchers, snapshots and undo. Mapped types describe the watcher table and the change events, so a watcher for `count` receives numbers and nothing else.",
    ["State is `{ count: number; user: string; dark: boolean }`, starting `{ count: 0, user: \"guest\", dark: false }`.",
     "Commands: `get <key>` prints `<key> = <value>`; `set <key> <text>` converts by the key's current type (a bad number/boolean prints `bad value for <key>`); `inc <key> [n]` adds n (default 1) to a number (`<key> is not a number` otherwise); `toggle <key>` flips a boolean (`<key> is not a boolean`); unknown keys print `unknown key <k>`.",
     "`watch <key>` / `unwatch <key>`: while watched, every change to the key prints `<key>: <old> -> <new>` (a set to the same value is not a change and prints nothing).",
     "`undo` restores the state before the last change (and notifies watchers), or prints `nothing to undo`; `snapshot` prints the state as JSON.",
     "Type the watcher table as a mapped type `{ [K in keyof T]?: (from: T[K], to: T[K]) => void }` and `set` as `<K extends keyof T>(key: K, value: T[K])`."],
    r"""
type Watchers<T> = { [K in keyof T]?: (from: T[K], to: T[K]) => void };
function createStore<T extends object>(initial: T) {
  let state: T = { ...initial };
  const history: T[] = [];
  const watchers: Watchers<T> = {};
  function notify<K extends keyof T>(key: K, from: T[K], to: T[K]) {
    if (from !== to) watchers[key]?.(from, to);
  }
  return {
    get<K extends keyof T>(key: K): T[K] {
      return state[key];
    },
    set<K extends keyof T>(key: K, value: T[K]): void {
      const from = state[key];
      if (from === value) return;
      history.push(state);
      state = { ...state, [key]: value };
      notify(key, from, value);
    },
    watch<K extends keyof T>(key: K, fn: (from: T[K], to: T[K]) => void): void {
      watchers[key] = fn;
    },
    unwatch(key: keyof T): void {
      delete watchers[key];
    },
    undo(): boolean {
      const previous = history.pop();
      if (previous === undefined) return false;
      const before = state;
      state = previous;
      for (const key of Object.keys(state) as (keyof T)[]) notify(key, before[key], previous[key]);
      return true;
    },
    snapshot: (): string => JSON.stringify(state),
  };
}
type State = { count: number; user: string; dark: boolean };
const store = createStore<State>({ count: 0, user: "guest", dark: false });
const isKey = (s: string): s is keyof State => s === "count" || s === "user" || s === "dark";
for (const line of input.split("\n")) {
  const [cmd = "", key = "", ...rest] = line.trim().split(/\s+/);
  if (cmd === "undo") {
    if (!store.undo()) console.log("nothing to undo");
    continue;
  }
  if (cmd === "snapshot") {
    console.log(store.snapshot());
    continue;
  }
  if (!isKey(key)) {
    console.log(`unknown key ${key}`);
    continue;
  }
  const text = rest.join(" ");
  if (cmd === "get") console.log(`${key} = ${store.get(key)}`);
  else if (cmd === "watch") store.watch(key, (from, to) => console.log(`${key}: ${from} -> ${to}`));
  else if (cmd === "unwatch") store.unwatch(key);
  else if (cmd === "inc") {
    if (key !== "count") console.log(`${key} is not a number`);
    else store.set("count", store.get("count") + (text === "" ? 1 : Number(text)));
  } else if (cmd === "toggle") {
    if (key !== "dark") console.log(`${key} is not a boolean`);
    else store.set("dark", !store.get("dark"));
  } else if (cmd === "set") {
    if (key === "count") {
      if (text === "" || !Number.isFinite(Number(text))) console.log(`bad value for ${key}`);
      else store.set("count", Number(text));
    } else if (key === "dark") {
      if (text !== "true" && text !== "false") console.log(`bad value for ${key}`);
      else store.set("dark", text === "true");
    } else {
      store.set("user", text);
    }
  }
}
""", ["watch count\ninc count\ninc count 5\nset count 6\nget count\nundo\nget count\nsnapshot",
      "watch dark\ntoggle dark\ntoggle user\nset dark maybe\nset user Ana Lee\nwatch user\nundo\nundo\nundo\nsnapshot",
      "set count ten\ninc user\nset colour red\nget user\nundo",
      "watch count\nset count 3\nunwatch count\nset count 4\nundo\nsnapshot",
      "set user ana\nset user ana\nwatch user\nundo\nundo"],
    stretch=["Add `select<K extends keyof T>(...keys: K[]): Pick<T, K>`.",
             "Generate `setCount`/`setUser`/`setDark` methods with the week's key remapping."],
)

TS_PRACTICE_MORE[20] = [
    _pr("tsm-w20-p9", "A mapped type's result", 'type Flags<T> = { [K in keyof T]: boolean };\nconst f: Flags<{ a: string; b: number }> = { a: true, b: false };\nconst x = f.b;\n', "x", "boolean",
        strictness=_SI, hints=["Every property of `Flags<…>` is a `boolean`."]),
    _dx("tsm-w20-d9", "A remapped key that needs a string",
        "error TS2344: Type 'K' does not satisfy the constraint 'string'.",
        'type Getters<T> = { [K in keyof T as `get${Capitalize<K>}`]: () => T[K] };\nconst g: Getters<{ size: number }> = { getSize: () => 3 };\nconsole.log(g.getSize() * 2);\n',
        'type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };\nconst g: Getters<{ size: number }> = { getSize: () => 3 };\nconsole.log(g.getSize() * 2);\n',
        [("", "6")], strictness=_SI, hints=["`keyof T` may contain number and symbol keys.", "Intersect with `string`."], difficulty="Medium"),
]

TS_CARDS_MORE[20] = [
    ("What does the `as` clause in a mapped type do?", "Computes each output key from the input key `K` — renaming, or filtering with `never`."),
    ("How do you drop a key in a mapped type?", "Map it to `never` in the `as` clause: `[K in keyof T as Test<K> extends true ? never : K]`."),
    ("`Capitalize<string & K>` — why the `string &`?", "`keyof T` may include number and symbol keys; `Capitalize` only accepts strings."),
    ("What is `` `get${Capitalize<\"first_name\">}` ``?", "`\"getFirst_name\"` — only the first letter changes."),
    ("Do `readonly` and `?` survive `{ [K in keyof T as …]: T[K] }`?", "Yes — mapping over `keyof T` keeps the modifiers; `-readonly` / `-?` remove them."),
    ("A remapped type omits `password`; is it gone from the object?", "No — types are erased; remove it at runtime (rest destructuring) and then type the result."),
]

# ===========================================================================
# Week 21 — Conditional types, infer, distribution
# ===========================================================================

TS_PROBLEM_SETS[21] = [
    _tsp(21, "tsm-w21-parse-kinds", "A return type chosen by an argument", "warm-up",
         "Write `parse<K extends Kind>(kind: K, text: string): ParseResult<K>` where `Kind` is `\"int\" | \"list\" | \"flag\"` and `ParseResult<K>` is a conditional type: `number` for `int`, `string[]` for `list` (comma-separated), `boolean` for `flag` (`on`/`yes`/`true`). Each input line is `<kind> <text>`. Call `parse` with a *literal* kind in each branch and print `int <n> (+1 = <n+1>)`, `list of <k>: <items joined by |>`, `flag <b> (not <!b>)`, or `unknown kind <k>`.",
         r"""
type Kind = "int" | "list" | "flag";
type ParseResult<K extends Kind> = K extends "int" ? number : K extends "list" ? string[] : boolean;
function parse<K extends Kind>(kind: K, text: string): ParseResult<K> {
  const value = kind === "int" ? Number.parseInt(text, 10) : kind === "list" ? text.split(",").filter((s) => s !== "") : ["on", "yes", "true"].includes(text);
  return value as ParseResult<K>;
}
for (const line of input.split("\n")) {
  const [kind = "", text = ""] = line.trim().split(/\s+/);
  if (kind === "int") {
    const n = parse("int", text);
    console.log(`int ${n} (+1 = ${n + 1})`);
  } else if (kind === "list") {
    const xs = parse("list", text);
    console.log(`list of ${xs.length}: ${xs.join("|") || "(none)"}`);
  } else if (kind === "flag") {
    const b = parse("flag", text);
    console.log(`flag ${b} (not ${!b})`);
  } else {
    console.log(`unknown kind ${kind}`);
  }
}
""", ["int 41\nlist a,b,c\nflag yes\nflag off\nlist ,\ndate today", "int 7x"],
         hints=["With a literal argument, `K` is that literal, so `ParseResult<K>` resolves to one type.",
                "The implementation can't prove which branch it's in, so it returns with a single cast."]),
    _tsp(21, "tsm-w21-compact", "Compact and unwrap", "core",
         "Each input line is a list of tokens: a number, `null`, `undefined`, or `err:<message>`. Parse them into `(Result<number, string> | null | undefined)[]`. Write `compact<T>(xs: readonly T[]): NonNullable<T>[]` to drop the nulls, then split the results with `Extract<…, { ok: true }>` / `Extract<…, { ok: false }>`. Print `kept <k> of <n>`, `values <v…>` (or `values none`), `sum <s>` and each error as `error <message>`.",
         r"""
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
type Item = Result<number, string> | null | undefined;
function compact<T>(xs: readonly T[]): NonNullable<T>[] {
  return xs.filter((x): x is NonNullable<T> => x !== null && x !== undefined);
}
function token(t: string): Item {
  if (t === "null") return null;
  if (t === "undefined") return undefined;
  if (t.startsWith("err:")) return { ok: false, error: t.slice(4) };
  return { ok: true, value: Number(t) };
}
type Ok = Extract<NonNullable<Item>, { ok: true }>;
type Err = Extract<NonNullable<Item>, { ok: false }>;
for (const line of input.split("\n")) {
  const items = line.trim().split(/\s+/).map(token);
  const present = compact(items);
  const oks = present.filter((r): r is Ok => r.ok);
  const errs = present.filter((r): r is Err => !r.ok);
  console.log(`kept ${present.length} of ${items.length}`);
  console.log(`values ${oks.map((r) => r.value).join(" ") || "none"}`);
  console.log(`sum ${oks.reduce((s, r) => s + r.value, 0)}`);
  for (const e of errs) console.log(`error ${e.error}`);
}
""", ["1 null 2 err:boom undefined 3 err:bad-input", "null undefined", "err:only"],
         hints=["`NonNullable<T>` removes `null` and `undefined` — it is itself a distributive conditional type.",
                "`Extract<U, { ok: true }>` keeps the union members that match the pattern."]),
    _tsp(21, "tsm-w21-flatten-deep", "Flatten to the bottom", "core",
         "Write `flattenDeep<T>(xs: readonly T[]): FlattenDeep<T>[]` where `FlattenDeep<T> = T extends readonly (infer E)[] ? FlattenDeep<E> : T`. First print `sample <…>` — the flattened constant `[[1, [2, [3]]], [4]]`, typed `number[]` straight from the call. Then each input line is a JSON array of numbers nested to any depth: print the flattened numbers space-separated (or `(empty)`), then `depth <d>` — the deepest nesting (a flat array is 1).",
         r"""
type FlattenDeep<T> = T extends readonly (infer E)[] ? FlattenDeep<E> : T;
function flattenDeep<T>(xs: readonly T[]): FlattenDeep<T>[] {
  const out: unknown[] = [];
  const walk = (value: unknown): void => {
    if (Array.isArray(value)) for (const v of value) walk(v);
    else out.push(value);
  };
  walk(xs);
  return out as FlattenDeep<T>[];
}
function depth(value: unknown): number {
  return Array.isArray(value) ? 1 + Math.max(0, ...value.map(depth)) : 0;
}
const sample: number[] = flattenDeep([[1, [2, [3]]], [4]]);
console.log(`sample ${sample.join(" ")}`);
for (const line of input.split("\n")) {
  const data = JSON.parse(line) as unknown[];
  const flat = flattenDeep(data).map(Number);
  console.log(flat.join(" ") || "(empty)");
  console.log(`depth ${depth(data)}`);
}
""", ["[1,[2,[3,[4]]],5]", "[[],[[]]]\n[7]", "[[1,2],[3,[4,[5,[6]]]]]"],
         hints=["The type recurses the same way the function does: while it's an array, look inside.",
                "For a literal argument the type is exact (`sample` is `number[]`). Don't feed it a *recursive* type like `type Nested = number | Nested[]` — that recursion never ends, and the checker stops with TS2589; parse JSON as `unknown[]` instead."]),
    _tsp_types(21, "tsm-w21-if", "A type-level `if`", "warm-up",
               "Write `If<C, T, F>`: `T` when the condition `C` is `true`, `F` when it's `false`.",
               '''
type If<C extends boolean, T, F> = C extends true ? T : F;
''', "C extends true ? T : F",
               '''
type _1 = Expect<Equal<If<true, "yes", "no">, "yes">>;
type _2 = Expect<Equal<If<false, 1, 2>, 2>>;
type _3 = Expect<Equal<If<boolean, "a", "b">, "a" | "b">>;
''', hints=["A conditional type on `C`.", "`boolean` is `true | false`, so it distributes to both branches."]),
    _tsp_types(21, "tsm-w21-first-arg", "The first parameter's type", "warm-up",
               "Write `FirstArg<F>`: the type of a function's first parameter, `never` for a function with no parameters, and `never` for anything that isn't a function.",
               '''
type FirstArg<F> = F extends (...args: infer P) => unknown ? (P extends [infer A, ...unknown[]] ? A : never) : never;
''', "F extends (...args: infer P) => unknown ? (P extends [infer A, ...unknown[]] ? A : never) : never",
               '''
type _1 = Expect<Equal<FirstArg<(name: string, age: number) => void>, string>>;
type _2 = Expect<Equal<FirstArg<() => void>, never>>;
type _3 = Expect<Equal<FirstArg<string>, never>>;
''', hints=["Capture the whole parameter list with `infer P`, then take its first element with a second `infer`."]),
    _tsp_types(21, "tsm-w21-flatten-type", "FlattenDeep, as a type", "core",
               "Write `FlattenDeep<T>`: the innermost element type of an array nested to any depth; non-arrays are left unchanged.",
               '''
type FlattenDeep<T> = T extends readonly (infer E)[] ? FlattenDeep<E> : T;
''', "T extends readonly (infer E)[] ? FlattenDeep<E> : T",
               '''
type _1 = Expect<Equal<FlattenDeep<number[][][]>, number>>;
type _2 = Expect<Equal<FlattenDeep<(string | boolean[])[]>, string | boolean>>;
type _3 = Expect<Equal<FlattenDeep<"x">, "x">>;
''', hints=["If it's an array of `E`, flatten `E`; otherwise stop.", "Distribution handles the union case for you."]),
    _tsp_types(21, "tsm-w21-is-union", "Is it a union?", "stretch",
               "Write `IsUnion<T>`: `true` if `T` is a union of two or more members, else `false` (`never` is not a union).",
               '''
type IsUnion<T, U = T> = [T] extends [never] ? false : T extends unknown ? ([U] extends [T] ? false : true) : never;
''', "[T] extends [never] ? false : T extends unknown ? ([U] extends [T] ? false : true) : never",
               '''
type _1 = Expect<Equal<IsUnion<string>, false>>;
type _2 = Expect<Equal<IsUnion<string | number>, true>>;
type _3 = Expect<Equal<IsUnion<never>, false>>;
type _4 = Expect<Equal<IsUnion<boolean>, true>>;
''', hints=["Keep an undistributed copy of `T` in a second parameter with a default.",
            "Inside a distributive branch, `T` is one member; if the full union isn't assignable to it, there was more than one."]),
    _tsp_types(21, "tsm-w21-union-to-intersection", "Union to intersection", "stretch",
               "Write `UnionToIntersection<U>`: `A | B` becomes `A & B`. (The trick: put each member in a function *parameter* position, then `infer` from the union of those functions.)",
               '''
type UnionToIntersection<U> = (U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never;
''', "(U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never",
               '''
type _1 = Expect<Equal<UnionToIntersection<{ a: 1 } | { b: 2 }>, { a: 1 } & { b: 2 }>>;
type _2 = Expect<Equal<UnionToIntersection<{ x: string }>, { x: string }>>;
''', hints=["Distribute `U` into a union of functions `(x: A) => void | (x: B) => void`.",
            "Inferring a parameter type from a union of functions gives the intersection — parameters are contravariant."]),
]

TS_PROJECTS[21] = _project(
    21, "commands.ts — a dispatcher typed from its handlers",
    "Declare command handlers once; derive each command's argument types with `Parameters`, describe each argument's runtime kind with a mapped conditional type, and let the dispatcher parse text into correctly typed arguments before calling the handler.",
    ["Handlers: `add(a: number, b: number)` → the sum; `greet(name: string, times: number)` → `hello <name>` repeated `times` times, joined by `, ` (`(no greeting)` for none); `flip(flag: boolean)` → the negation; `upper(text: string)` → upper-cased; `between(x: number, lo: number, hi: number)` → `true` if lo ≤ x ≤ hi.",
     "Each input line is `<command> <args…>`. Parse each argument by its declared kind — numbers must be finite, booleans `true`/`false` — and print the handler's result, or `<command> expects <n> arguments`, `argument <i> of <command> must be a <kind>` (1-based, the first bad one), or `unknown command <c>`.",
     "`help` prints every command with its argument kinds, in declaration order, like `add(number, number)`.",
     "Derive `ArgsOf<N> = Parameters<Handlers[N]>` and a signature table typed with a mapped conditional type (`number` → `\"number\"`, …) so a handler whose parameters change breaks the table at compile time.",
     "Only one cast is allowed: the final call of a handler with its parsed argument list."],
    r"""
const HANDLERS = {
  add: (a: number, b: number) => a + b,
  greet: (name: string, times: number) => Array.from({ length: Math.max(0, times) }, () => `hello ${name}`).join(", ") || "(no greeting)",
  flip: (flag: boolean) => !flag,
  upper: (text: string) => text.toUpperCase(),
  between: (x: number, lo: number, hi: number) => lo <= x && x <= hi,
};
type Handlers = typeof HANDLERS;
type Name = keyof Handlers;
type ArgsOf<N extends Name> = Parameters<Handlers[N]>;
type KindOf<T> = T extends number ? "number" : T extends boolean ? "boolean" : "string";
type Kinds<A extends readonly unknown[]> = { [I in keyof A]: KindOf<A[I]> };
const SIGNATURES: { [N in Name]: Kinds<ArgsOf<N>> } = {
  add: ["number", "number"],
  greet: ["string", "number"],
  flip: ["boolean"],
  upper: ["string"],
  between: ["number", "number", "number"],
};
const NAMES = Object.keys(HANDLERS) as Name[];
const isName = (s: string): s is Name => Object.hasOwn(HANDLERS, s);
function convert(kind: "number" | "boolean" | "string", text: string): number | boolean | string | undefined {
  if (kind === "number") return text !== "" && Number.isFinite(Number(text)) ? Number(text) : undefined;
  if (kind === "boolean") return text === "true" ? true : text === "false" ? false : undefined;
  return text;
}
for (const line of input.split("\n")) {
  const [cmd = "", ...args] = line.trim().split(/\s+/);
  if (cmd === "help") {
    for (const n of NAMES) console.log(`${n}(${SIGNATURES[n].join(", ")})`);
    continue;
  }
  if (!isName(cmd)) {
    console.log(`unknown command ${cmd}`);
    continue;
  }
  const kinds: readonly ("number" | "boolean" | "string")[] = SIGNATURES[cmd];
  if (args.length !== kinds.length) {
    console.log(`${cmd} expects ${kinds.length} arguments`);
    continue;
  }
  const parsed: (number | boolean | string)[] = [];
  let bad = -1;
  kinds.forEach((kind, i) => {
    const value = convert(kind, args[i] ?? "");
    if (value === undefined) {
      if (bad < 0) bad = i;
    } else {
      parsed.push(value);
    }
  });
  if (bad >= 0) {
    console.log(`argument ${bad + 1} of ${cmd} must be a ${kinds[bad]}`);
    continue;
  }
  const handler = HANDLERS[cmd] as (...a: (number | boolean | string)[]) => unknown;
  console.log(String(handler(...parsed)));
}
""", ["add 2 3\nupper hello\nflip true\ngreet ana 2\nbetween 5 1 10\nhelp",
      "add 2\nadd two 3\nflip yes\nbetween 1 2 x\nsubtract 5 3",
      "greet bo 0\nbetween 10 1 10\nupper MiXeD",
      "flip false\nadd -1.5 0.5",
      "help\nadd 1 2 3"],
    stretch=["Add optional parameters (`greet(name, times = 1)`) and make the signature table say which arguments may be omitted.",
             "Type `dispatch` so that a *call in code* like `dispatch(\"add\", 1, \"x\")` is a compile error."],
)

TS_PRACTICE_MORE[21] = [
    _pr("tsm-w21-p9", "What NonNullable leaves", 'type Maybe = string | null | undefined;\nconst value: NonNullable<Maybe> = "ok";\nconst copy = value;\n', "copy", "string",
        strictness=_SI, hints=["`NonNullable` removes `null` and `undefined` from a union."]),
    _dx("tsm-w21-d9", "`ReturnType` of an overloaded function",
        "error TS2322: Type 'number' is not assignable to type 'string'.",
        'function size(x: string): number;\nfunction size(x: number): string;\nfunction size(x: string | number): string | number {\n  return typeof x === "string" ? x.length : String(x).length + " digits";\n}\nconst n: ReturnType<typeof size> = size("hello");\nconsole.log(n);\n',
        'function size(x: string): number;\nfunction size(x: number): string;\nfunction size(x: string | number): string | number {\n  return typeof x === "string" ? x.length : String(x).length + " digits";\n}\nconst n = size("hello");\nconsole.log(n);\n',
        [("", "5")], strictness=_SI,
        hints=["`ReturnType` of an overloaded function uses the last overload.", "Let the call infer its own type."], difficulty="Medium"),
]

TS_CARDS_MORE[21] = [
    ("`T extends unknown ? T[] : never` given `string | number`?", "`string[] | number[]` — a naked type parameter distributes over the union."),
    ("What switches distribution off in `T extends U ? X : Y`?", "Wrapping both sides in a tuple: `[T] extends [U] ? … : …`."),
    ("A distributive conditional type given `never`?", "`never` — the empty union has no members to map."),
    ("How is `IsNever<T>` written?", "`[T] extends [never] ? true : false`."),
    ("`infer U extends string` — what's different from `infer U`?", "The branch only matches if the captured type is a `string`, and `U` is known to be one."),
    ("`ReturnType` of an overloaded function?", "The last overload's return type — `infer` sees only the last signature."),
]

# ===========================================================================
# Week 22 — Template literal types, recursive types, type performance
# ===========================================================================

TS_PROBLEM_SETS[22] = [
    _tsp(22, "tsm-w22-case-styles", "Convert identifier styles", "warm-up",
         "Each input line is an identifier in `snake_case`, `kebab-case`, `camelCase` or `PascalCase`. Split it into lower-case words and print it in all four styles as `snake=<…> kebab=<…> camel=<…> pascal=<…>`. Type the style names as a union and the output as `Record<Style, string>`.",
         r"""
type Style = "snake" | "kebab" | "camel" | "pascal";
const STYLES: readonly Style[] = ["snake", "kebab", "camel", "pascal"];
function words(id: string): string[] {
  return id.replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2").replace(/([a-z0-9])([A-Z])/g, "$1 $2").split(/[\s_-]+/).filter((w) => w !== "").map((w) => w.toLowerCase());
}
const cap = (w: string) => w.charAt(0).toUpperCase() + w.slice(1);
function convert(id: string): Record<Style, string> {
  const ws = words(id);
  return {
    snake: ws.join("_"),
    kebab: ws.join("-"),
    camel: ws.map((w, i) => (i === 0 ? w : cap(w))).join(""),
    pascal: ws.map(cap).join(""),
  };
}
for (const line of input.split("\n")) {
  const out = convert(line.trim());
  console.log(STYLES.map((s) => `${s}=${out[s]}`).join(" "));
}
""", ["first_name\nuser-id\nhttpStatusCode\nParseJSONValue\nx"],
         hints=["Normalise to a list of lower-case words first; each style is then one `join`.",
                "A lower-case letter or digit followed by an upper-case one marks a word boundary in camelCase — and so does the last capital of an acronym followed by a lower-case letter (`JSONValue` is `JSON Value`)."]),
    _tsp(22, "tsm-w22-route-params", "Match routes, typed parameters", "core",
         "Routes are `as const` patterns: `/users/:id`, `/users/:id/posts/:postId`, `/files/:name.:ext` is not needed — only whole-segment params. The params type of a pattern is computed with a recursive template literal type, `RouteParams<\"/users/:id\">` = `{ id: string }`. Each input line is a path: print the first matching pattern and its params as `key=value` pairs (in pattern order), or `no route`. A param must be non-empty.",
         r"""
type ParamNames<P extends string> = P extends `${string}:${infer Name}/${infer Rest}` ? Name | ParamNames<`/${Rest}`> : P extends `${string}:${infer Name}` ? Name : never;
type RouteParams<P extends string> = { [K in ParamNames<P>]: string };
const ROUTES = ["/users/:id", "/users/:id/posts/:postId", "/tags/:tag"] as const;
function match<P extends string>(pattern: P, path: string): RouteParams<P> | undefined {
  const want = pattern.split("/");
  const got = path.split("/");
  if (want.length !== got.length) return undefined;
  const params: Record<string, string> = {};
  for (const [i, seg] of want.entries()) {
    const actual = got[i] ?? "";
    if (seg.startsWith(":")) {
      if (actual === "") return undefined;
      params[seg.slice(1)] = actual;
    } else if (seg !== actual) {
      return undefined;
    }
  }
  return params as RouteParams<P>;
}
const user = match("/users/:id", "/users/42");
if (user !== undefined) console.log(`typed access: user ${user.id}`);
for (const line of input.split("\n")) {
  const path = line.trim();
  let found = false;
  for (const route of ROUTES) {
    const params = match(route, path);
    if (params === undefined) continue;
    console.log(`${route} ${Object.entries(params).map(([k, v]) => `${k}=${v}`).join(" ")}`);
    found = true;
    break;
  }
  if (!found) console.log("no route");
}
""", ["/users/7\n/users/7/posts/99\n/tags/ts\n/users/\n/users/7/posts\n/nope", "/tags/a b"],
         hints=["`ParamNames` peels one `:name` off the pattern per step; `RouteParams` maps the names to `string`.",
                "At runtime, compare segment by segment — the type only describes what the match returns."]),
    _tsp(22, "tsm-w22-topics", "Subscriptions with wildcards", "stretch",
         "Event names are `` `${Entity}:${Action}` `` with entities `user`, `order` and actions `created`, `updated`, `deleted`. Input lines are `sub <id> <pattern>` (a pattern is an event name, `<entity>:*` or `*:<action>`), `unsub <id>`, or `emit <event>`. An `emit` of a name that isn't a valid event prints `bad event <e>`; otherwise print the ids of the matching subscriptions, in subscription order, as `<event> -> <ids>` or `<event> -> nobody`. A bad pattern prints `bad pattern <p>`.",
         r"""
const ENTITIES = ["user", "order"] as const;
const ACTIONS = ["created", "updated", "deleted"] as const;
type Entity = (typeof ENTITIES)[number];
type Action = (typeof ACTIONS)[number];
type EventName = `${Entity}:${Action}`;
type Pattern = EventName | `${Entity}:*` | `*:${Action}`;
const isEntity = (s: string): s is Entity => ENTITIES.some((e) => e === s);
const isAction = (s: string): s is Action => ACTIONS.some((a) => a === s);
function isEvent(s: string): s is EventName {
  const [e = "", a = "", extra] = s.split(":");
  return extra === undefined && isEntity(e) && isAction(a);
}
function isPattern(s: string): s is Pattern {
  const [e = "", a = "", extra] = s.split(":");
  if (extra !== undefined) return false;
  return (isEntity(e) || e === "*") && (isAction(a) || a === "*") && !(e === "*" && a === "*");
}
function matches(p: Pattern, ev: EventName): boolean {
  const [pe, pa] = p.split(":");
  const [e, a] = ev.split(":");
  return (pe === "*" || pe === e) && (pa === "*" || pa === a);
}
const subs = new Map<string, Pattern>();
for (const line of input.split("\n")) {
  const [cmd = "", a = "", b = ""] = line.trim().split(/\s+/);
  if (cmd === "sub") {
    if (isPattern(b)) subs.set(a, b);
    else console.log(`bad pattern ${b}`);
  } else if (cmd === "unsub") {
    subs.delete(a);
  } else if (cmd === "emit") {
    if (!isEvent(a)) {
      console.log(`bad event ${a}`);
      continue;
    }
    const ids = [...subs].filter(([, p]) => matches(p, a)).map(([id]) => id);
    console.log(`${a} -> ${ids.join(" ") || "nobody"}`);
  }
}
""", ["sub s1 user:*\nsub s2 *:deleted\nsub s3 order:created\nemit user:created\nemit order:deleted\nemit order:created\nunsub s2\nemit user:deleted\nemit order:updated\nemit user:banned\nsub s4 *:*"],
         hints=["A template literal type of two unions is every combination — six event names here.",
                "Type predicates turn input strings into `EventName` and `Pattern` once, at the boundary."]),
    _tsp_types(22, "tsm-w22-trim", "Trim both ends", "warm-up",
               "Write `Trim<S>`: `S` without leading or trailing spaces.",
               '''
type Trim<S extends string> = S extends ` ${infer R}` ? Trim<R> : S extends `${infer L} ` ? Trim<L> : S;
''', "S extends ` ${infer R}` ? Trim<R> : S extends `${infer L} ` ? Trim<L> : S",
               '''
type _1 = Expect<Equal<Trim<"  hi  ">, "hi">>;
type _2 = Expect<Equal<Trim<"a b">, "a b">>;
type _3 = Expect<Equal<Trim<"   ">, "">>;
''', hints=["Peel one space off the front if there is one, else one off the back, and recurse."]),
    _tsp_types(22, "tsm-w22-starts-with", "Starts with", "warm-up",
               "Write `StartsWith<S, P>`: `true` if the string type `S` begins with `P`.",
               '''
type StartsWith<S extends string, P extends string> = S extends `${P}${string}` ? true : false;
''', "S extends `${P}${string}` ? true : false",
               '''
type _1 = Expect<Equal<StartsWith<"typescript", "type">, true>>;
type _2 = Expect<Equal<StartsWith<"typescript", "script">, false>>;
type _3 = Expect<Equal<StartsWith<"x", "">, true>>;
''', hints=["A template literal pattern: the prefix, then any string."]),
    _tsp_types(22, "tsm-w22-replace-all", "Replace every occurrence", "core",
               "Write `ReplaceAll<S, From, To>`: every occurrence of `From` in `S` replaced with `To` (an empty `From` changes nothing).",
               '''
type ReplaceAll<S extends string, From extends string, To extends string> = From extends ""
  ? S
  : S extends `${infer A}${From}${infer B}`
    ? `${A}${To}${ReplaceAll<B, From, To>}`
    : S;
''', '''From extends ""
  ? S
  : S extends `${infer A}${From}${infer B}`
    ? `${A}${To}${ReplaceAll<B, From, To>}`
    : S''',
               '''
type _1 = Expect<Equal<ReplaceAll<"a_b_c", "_", "-">, "a-b-c">>;
type _2 = Expect<Equal<ReplaceAll<"aaa", "a", "ab">, "ababab">>;
type _3 = Expect<Equal<ReplaceAll<"none", "x", "y">, "none">>;
type _4 = Expect<Equal<ReplaceAll<"keep", "", "z">, "keep">>;
''', hints=["Match `${A}${From}${B}`; replace the first occurrence and recurse on the rest (`B`) only, so replacements aren't matched again."]),
    _tsp_types(22, "tsm-w22-split", "Split, with a fallback", "core",
               "Write `Split<S, D>`: a tuple of the pieces of `S` separated by `D` — and `string[]` when `S` is plain `string`, which has nothing to parse.",
               '''
type Split<S extends string, D extends string> = string extends S
  ? string[]
  : S extends `${infer H}${D}${infer T}`
    ? [H, ...Split<T, D>]
    : [S];
''', '''string extends S
  ? string[]
  : S extends `${infer H}${D}${infer T}`
    ? [H, ...Split<T, D>]
    : [S]''',
               '''
type _1 = Expect<Equal<Split<"a,b,c", ",">, ["a", "b", "c"]>>;
type _2 = Expect<Equal<Split<"solo", ",">, ["solo"]>>;
type _3 = Expect<Equal<Split<string, ",">, string[]>>;
''', hints=["Check `string extends S` first.", "Then peel off the part before the first delimiter and recurse on the rest."]),
    _tsp_types(22, "tsm-w22-paths", "Every dotted path", "stretch",
               "Write `Paths<T>`: the union of every dotted path to a property of a nested object type — `\"a\" | \"a.b\" | \"a.b.c\"` for `{ a: { b: { c: number } } }`.",
               '''
type Paths<T> = T extends object
  ? { [K in keyof T & string]: T[K] extends object ? K | `${K}.${Paths<T[K]>}` : K }[keyof T & string]
  : never;
''', '''T extends object
  ? { [K in keyof T & string]: T[K] extends object ? K | `${K}.${Paths<T[K]>}` : K }[keyof T & string]
  : never''',
               '''
type _1 = Expect<Equal<Paths<{ a: { b: { c: number } }; d: string }>, "a" | "a.b" | "a.b.c" | "d">>;
type _2 = Expect<Equal<Paths<{ x: number }>, "x">>;
''', hints=["Map every string key to itself, plus `key.` followed by the paths inside it when its value is an object.",
            "Then look up all the mapped values at once with `[keyof T & string]`."]),
]

TS_PROJECTS[22] = _project(
    22, "events.ts — a typed event catalogue (arc: typed-kit)",
    "The Month 5 arc project: an event bus whose event names come from a catalogue, whose payloads are checked per event at runtime, and whose subscriptions support one-shot handlers and `entity:*` wildcards. Event names are a template literal type built from the catalogue.",
    ["The catalogue: `user:created { name: string }`, `user:deleted { id: number }`, `order:placed { id: number; total: number }`, `order:shipped { id: number }`. Event names are typed as `` `${Entity}:${Action}` `` restricted to these four.",
     "Commands: `on <sub> <pattern>`, `once <sub> <pattern>` (removed after its first delivery), `off <sub>`, `emit <event> <json>`. A pattern is an event name or `<entity>:*`; anything else prints `bad pattern <p>`.",
     "`emit` checks the event name (`unknown event <e>`), parses the JSON and validates it against that event's payload shape (`bad payload for <event>`), then prints one line per delivery in subscription order: `<sub> got <event> <summary>` where the summary is `name=<n>`, `id=<i>` or `id=<i> total=<t>`; with no deliveries, `<event> unheard`.",
     "`stats` prints each event name in catalogue order with how many times it was emitted successfully: `<event>: <n>`.",
     "Payload validators are declared per event in a mapped type `{ [E in EventName]: (v: unknown) => v is Payloads[E] }`."],
    r"""
type Payloads = {
  "user:created": { name: string };
  "user:deleted": { id: number };
  "order:placed": { id: number; total: number };
  "order:shipped": { id: number };
};
type EventName = keyof Payloads;
type Entity = EventName extends `${infer E}:${string}` ? E : never;
type Pattern = EventName | `${Entity}:*`;
const EVENTS = ["user:created", "user:deleted", "order:placed", "order:shipped"] as const satisfies readonly EventName[];
const isRecord = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);
const VALIDATORS: { [E in EventName]: (v: unknown) => v is Payloads[E] } = {
  "user:created": (v): v is Payloads["user:created"] => isRecord(v) && typeof v["name"] === "string",
  "user:deleted": (v): v is Payloads["user:deleted"] => isRecord(v) && typeof v["id"] === "number",
  "order:placed": (v): v is Payloads["order:placed"] => isRecord(v) && typeof v["id"] === "number" && typeof v["total"] === "number",
  "order:shipped": (v): v is Payloads["order:shipped"] => isRecord(v) && typeof v["id"] === "number",
};
const isEvent = (s: string): s is EventName => EVENTS.some((e) => e === s);
const isPattern = (s: string): s is Pattern => isEvent(s) || s === "user:*" || s === "order:*";
function summary(payload: unknown): string {
  if (!isRecord(payload)) return "";
  return Object.entries(payload).map(([k, v]) => `${k}=${String(v)}`).join(" ");
}
type Sub = { pattern: Pattern; once: boolean };
const subs = new Map<string, Sub>();
const emitted = new Map<EventName, number>();
const matches = (p: Pattern, e: EventName) => p === e || (p.endsWith(":*") && e.startsWith(p.slice(0, -1)));
for (const line of input.split("\n")) {
  const [cmd = "", a = "", ...rest] = line.trim().split(" ");
  if (cmd === "on" || cmd === "once") {
    const p = rest[0] ?? "";
    if (isPattern(p)) subs.set(a, { pattern: p, once: cmd === "once" });
    else console.log(`bad pattern ${p}`);
  } else if (cmd === "off") {
    subs.delete(a);
  } else if (cmd === "emit") {
    if (!isEvent(a)) {
      console.log(`unknown event ${a}`);
      continue;
    }
    let payload: unknown;
    try {
      payload = JSON.parse(rest.join(" "));
    } catch {
      payload = undefined;
    }
    if (!VALIDATORS[a](payload)) {
      console.log(`bad payload for ${a}`);
      continue;
    }
    emitted.set(a, (emitted.get(a) ?? 0) + 1);
    const hits = [...subs].filter(([, s]) => matches(s.pattern, a));
    if (hits.length === 0) console.log(`${a} unheard`);
    for (const [id, s] of hits) {
      console.log(`${id} got ${a} ${summary(payload)}`);
      if (s.once) subs.delete(id);
    }
  } else if (cmd === "stats") {
    for (const e of EVENTS) console.log(`${e}: ${emitted.get(e) ?? 0}`);
  }
}
""", ['on audit user:*\nonce welcome user:created\nemit user:created {"name":"ana"}\nemit user:created {"name":"bo"}\nemit user:deleted {"id":7}\nstats',
      'on ship order:shipped\nemit order:placed {"id":1,"total":9.5}\nemit order:shipped {"id":"1"}\nemit order:shipped {"id":1}\nemit order:lost {}\non x *:*\nstats',
      'on all order:*\noff all\nemit order:placed {"id":2,"total":1}\nemit user:created not-json',
      'once a user:deleted\nonce b user:deleted\nemit user:deleted {"id":3}\nemit user:deleted {"id":4}',
      'stats'],
    stretch=["Make `emit` type-safe in code: `emit(\"order:placed\", { id: 1 })` should fail to compile for the missing `total`.",
             "Collect the Month 5 helpers — `groupBy`, `Paths`, `DeepReadonly`, `RouteParams`, this emitter — into one `typed-kit` file with type tests."],
)

TS_PRACTICE_MORE[22] = [
    _pr("tsm-w22-p9", "A template literal of two unions", 'type Size = "s" | "m";\ntype Colour = "red" | "blue";\ndeclare const sku: `${Size}-${Colour}`;\nconst copy = sku;\n', "copy", '"s-red" | "s-blue" | "m-red" | "m-blue"',
        strictness=_SI, hints=["A template literal type over two unions is every combination.", "Two sizes times two colours."]),
    _dx("tsm-w22-d9", "A union that is too large",
        "error TS2590: Expression produces a union type that is too complex to represent.",
        _STDIN + 'type D = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";\ntype Code = `${D}${D}${D}${D}${D}${D}`;\nconst code = input as Code;\nconsole.log(code.length === 6 ? "ok" : "bad");\n',
        _STDIN + 'const isCode = (s: string) => /^\\d{6}$/.test(s);\nconsole.log(isCode(input) ? "ok" : "bad");\n',
        [("123456", "ok"), ("12a", "bad")], strictness=_SI,
        hints=["Six ten-member unions make a million combinations.", "Check the format at runtime instead of enumerating it in a type."], difficulty="Medium"),
]

TS_CARDS_MORE[22] = [
    ("What does TS2589 mean?", "Type instantiation is excessively deep and possibly infinite — usually recursion that isn't a tail call."),
    ("How do you let a recursive type go deeper?", "Make it tail-recursive: carry the result in an accumulator so the recursive call is the whole branch (up to 1,000 steps)."),
    ("What is TS2590?", "A union too complex to represent (over 100,000 members) — often a template literal of several unions."),
    ("Why check `string extends S` in a string-parsing type?", "A plain `string` has nothing to parse; return the general type (`string[]`) instead of a wrong tuple."),
    ("Cheaper for the checker: interface extends or a big intersection?", "`interface … extends` — named interfaces are cached; intersections are recomputed."),
    ("When is advanced type-level code worth it?", "When it catches real mistakes at many call sites of a widely used API; otherwise prefer a simple type and a runtime check."),
]
