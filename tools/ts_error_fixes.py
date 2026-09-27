# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# A repaired program for every compiler error a TypeScript chapter shows
# (TS_MASTERY_ROADMAP.md X-10: "read the error" per chapter).
#
# For each chapter, one entry per error in the order the lesson shows them:
# the program with the cause fixed — printing something, so the repair is
# judged on output as well as on compiling — or None when the snippet cannot
# become a runnable exercise (enums and decorators do not run under type
# stripping; some snippets exist only to show type machinery).
# mastery_ts_derived.py turns each into a `diagnose` exercise whose starter is
# the chapter's own snippet and whose prompt quotes the chapter's diagnostic.
# ---------------------------------------------------------------------------

TS_ERROR_FIXES = {
    "ts_variables": [
        "let total = 0;\ntotal = total + 5;\nconsole.log(total);",
        "let count = 1;\nconsole.log(count);",
    ],
    "ts_types": [
        'let count: number = 5;\nconsole.log(count);',
        'const biggest = Math.max(Number("3"), 4);\nconsole.log(biggest);',
    ],
    "ts_inference": [
        "function double(x: number) {\n  return x * 2;\n}\nconsole.log(double(21));",
        "let attempts = 0;\nattempts = 3;\nconsole.log(attempts);",
    ],
    "ts_strings": [
        'const word = "abc";\nconsole.log(word.length);',
        'const s: string = "cat";\nconst t = "b" + s.slice(1);\nconsole.log(t);',
    ],
    "ts_operators": [
        'const doubled = Number("21") * 2;\nconsole.log(doubled);',
        "const ordered = 3 > 2 && 2 > 1;\nconsole.log(ordered);",
    ],
    "ts_conditionals": [
        'type Size = "s" | "m" | "l";\nfunction check(size: Size): string {\n  if (size === "l") return "large";\n  return size;\n}\nconsole.log(check("l"));',
        'type Size = "s" | "m" | "x";\nfunction label(size: Size): string {\n  switch (size) {\n    case "s":\n      return "small";\n    case "x":\n      return "extra";\n    default:\n      return "medium";\n  }\n}\nconsole.log(label("x"));',
    ],
    "ts_loops": [
        "const xs = [1, 2, 3];\nfor (const x of xs) {\n  const doubled = x * 2;\n  console.log(doubled);\n}",
        "const prices = { pen: 2, cup: 5 };\nlet total = 0;\nfor (const price of Object.values(prices)) total += price;\nconsole.log(total);",
    ],
    "ts_functions": [
        "function add(a: number, b: number): number {\n  return a + b;\n}\nconsole.log(add(1, 2));",
        "function half(n: number): number {\n  return n / 2;\n}\nconsole.log(half(8));",
    ],
    "ts_params": [
        "function range(start: number | undefined, end: number): number[] {\n  const out: number[] = [];\n  for (let i = start ?? 0; i < end; i++) out.push(i);\n  return out;\n}\nconsole.log(range(undefined, 3).join(\" \"));",
        'function log(level: string, ...messages: string[]): void {\n  console.log(level, messages.join(" "));\n}\nlog("info");',
    ],
    "ts_unions": [
        'function show(x: string | number): string {\n  return typeof x === "number" ? x.toFixed(2) : x;\n}\nconsole.log(show(3), show("x"));',
        'type Status = "idle" | "busy" | "loading";\nlet status: Status = "idle";\nstatus = "loading";\nconsole.log(status);',
    ],
    "ts_aliases": [
        'type Size = "s" | "m" | "l";\nconst s: Size = "l";\nconsole.log(s);',
        "interface Base {\n  id: number;\n}\ninterface Doc extends Base {\n  title: string;\n}\nconst d: Doc = { id: 1, title: \"notes\" };\nconsole.log(d.id, d.title);",
    ],
    "ts_narrowing": [
        'type Fish = { swim: () => string };\ntype Bird = { fly: () => string };\nfunction move(pet: Fish | Bird): string {\n  return "swim" in pet ? pet.swim() : pet.fly();\n}\nconsole.log(move({ fly: () => "flap" }));',
        'const found = "abc".match(/d/);\nconsole.log(found === null ? "no match" : found.index);',
    ],
    "ts_arrays": [
        "const scores: number[] = [90, 85];\nscores.push(100);\nconsole.log(scores.join(\",\"));",
        "const point: [number, number] = [3, 4];\nconst y = point[1];\nconsole.log(y);",
    ],
    "ts_array_methods": [
        'const totalLength = ["a", "bb", "ccc"].reduce((acc, x) => acc + x.length, 0);\nconsole.log(totalLength);',
        "const firstBig: number | undefined = [1, 5, 9].find((x) => x > 4);\nconsole.log(firstBig ?? \"none\");",
    ],
    "ts_objects": [
        'interface User {\n  name: string;\n  email: string;\n}\nconst u: User = { name: "ana", email: "ana@example.com" };\nconsole.log(u.email);',
        "interface Point {\n  x: number;\n  y: number;\n}\nconst p: Point = { x: 1, y: 2 };\nconsole.log(p.x + p.y);",
    ],
    "ts_maps_sets": [
        'const labels = new Map<number, string>();\nlabels.set(1, "one");\nconsole.log(labels.get(1));',
        'const stock = new Map([["pen", 3]]);\nconst left = stock.get("pen") ?? 0;\nconsole.log(left - 1);',
    ],
    "ts_enums": [
        None,  # an `enum` does not run under type stripping
        'const Direction = { North: "N", South: "S" } as const;\ntype Direction = (typeof Direction)[keyof typeof Direction];\nfunction turn(d: Direction): string {\n  return d;\n}\nconsole.log(turn(Direction.North));',
    ],
    "ts_generics": [
        "function firstOr<T>(xs: T[], fallback: T): T {\n  return xs[0] ?? fallback;\n}\nconsole.log(firstOr([], \"none\"));",
        'function pair<T>(a: T, b: T): [T, T] {\n  return [a, b];\n}\nconst p = pair<string>("a", "b");\nconsole.log(p.join(","));',
    ],
    "ts_classes": [
        "class Counter {\n  count: number;\n  constructor(start?: number) {\n    this.count = start ?? 0;\n  }\n}\nconsole.log(new Counter().count, new Counter(5).count);",
        'class Animal {\n  readonly name: string;\n  constructor(name: string) {\n    this.name = name;\n  }\n}\nclass Dog extends Animal {\n  readonly tricks: string[];\n  constructor(name: string) {\n    super(name);\n    this.tricks = [];\n  }\n}\nconsole.log(new Dog("rex").name);',
        "interface Shape {\n  area(): number;\n}\nclass Square implements Shape {\n  readonly side: number;\n  constructor(side: number) {\n    this.side = side;\n  }\n  area(): number {\n    return this.side ** 2;\n  }\n}\nconsole.log(new Square(3).area());",
    ],
    "ts_this_accessors": [
        "class Counter {\n  count = 0;\n  inc(this: Counter): void {\n    this.count++;\n  }\n}\nconst c = new Counter();\nc.inc();\nconsole.log(c.count);",
        "class Rect {\n  readonly w: number;\n  readonly h: number;\n  constructor(w: number, h: number) {\n    this.w = w;\n    this.h = h;\n  }\n  get area(): number {\n    return this.w * this.h;\n  }\n}\nconst r = new Rect(4, 5);\nconsole.log(r.area);",
        "class Rect {\n  readonly w = 3;\n  readonly h = 4;\n  get area(): number {\n    return this.w * this.h;\n  }\n}\nconsole.log(new Rect().area);",
    ],
    "ts_modules": [
        "function add(a: number, b: number): number {\n  return a + b;\n}\nconsole.log(add(1, 2));",
        'import { readFileSync } from "fs";\nconsole.log(typeof readFileSync);',
    ],
    "ts_nullish": [
        'let nickname: string | null = null;\nconsole.log(nickname ?? "none");',
        'const users = [{ name: "ana" }];\nconsole.log(users.find((u) => u.name === "bo")?.name ?? "not found");',
    ],
    "ts_errors": [
        'try {\n  JSON.parse("{");\n} catch (e) {\n  console.log(e instanceof Error ? "failed" : String(e));\n}',
        'try {\n  JSON.parse("{");\n} catch (e) {\n  console.log(e instanceof Error ? "failed" : String(e));\n}',
        'function parse(s: string): number {\n  try {\n    return JSON.parse(s) as number;\n  } catch (e) {\n    console.log("bad input");\n    return NaN;\n  }\n}\nconsole.log(parse("{"));',
    ],
    "ts_utility_types": [
        'type Task = { id: number; title: string };\ntype Summary = Pick<Task, "id" | "title">;\nconst s: Summary = { id: 1, title: "write" };\nconsole.log(s.title);',
        "type Options = { width?: number; height?: number };\nconst full: Required<Options> = { width: 100, height: 50 };\nconsole.log(full.width * full.height);",
    ],
    "ts_async": [
        "async function main(): Promise<void> {\n  const n = await Promise.resolve(1);\n  console.log(n);\n}\nmain();",
        "async function count(): Promise<number> {\n  return 3;\n}\nasync function main(): Promise<void> {\n  const total: number = await count();\n  console.log(total);\n}\nmain();",
        "async function count(): Promise<number> {\n  return 3;\n}\ncount().then(console.log);",
    ],
    "ts_destructuring": [
        'const { name } = { name: "ana" };\nconsole.log(name);',
        "const [first] = [1, 2];\nconsole.log(first);",
    ],
    "ts_assertions": [
        'const count = Number("5");\nconsole.log(count + 1);',
        'const words = ["a", "bb"];\nconst long = words.find((w) => w.length > 5);\nconsole.log(long?.length ?? 0);',
    ],
    "ts_compose": [
        "type A = { id: number };\ntype B = { name: string };\nconst x: A & B = { id: 1, name: \"x\" };\nconsole.log(x.id, x.name);",
        'type Pet = { name: string } | { id: number };\ntype Owner = Pet & { since: number };\nconst o: Owner = { name: "rex", since: 2020 };\nconsole.log(o.since);',
    ],
    "ts_json": [
        "const data: unknown = JSON.parse('{\"name\":\"ana\"}');\nif (typeof data === \"object\" && data !== null && \"name\" in data) console.log(data.name);",
        "const n = JSON.parse(\"42\");\nconsole.log(n + 1);",
    ],
    "ts_immutability": [
        "type Config = { readonly port: number };\nconst c: Config = { port: 80 };\nconst moved: Config = { ...c, port: 8080 };\nconsole.log(moved.port);",
        "const frozen: readonly number[] = [1, 2];\nconst editable: number[] = [...frozen];\neditable.push(3);\nconsole.log(editable.join(\",\"));",
    ],
    "ts_number_math": [
        "const next = 10n + 1n;\nconsole.log(next.toString());",
        'const r = Math.round(Number("2.5"));\nconsole.log(r);',
    ],
    "ts_string_methods": [
        'const line = "ab".repeat(3);\nconsole.log(line);',
        'const hasOne = "a1b".includes("1");\nconsole.log(hasOne);',
    ],
    "ts_higher_order": [
        "const lengths = [\"a\", \"bb\", \"ccc\"].map((s: string) => s.length);\nconsole.log(lengths.join(\",\"));",
        "const retries = 3;\nconst result = retries * 2;\nconsole.log(result);",
    ],
    "ts_type_predicates": [
        "function isNumber(x: unknown): x is number {\n  return typeof x === \"number\";\n}\nconsole.log(isNumber(3), isNumber(\"3\"));",
        'function assertPositive(n: number): asserts n {\n  if (n <= 0) throw new Error("not positive");\n}\nassertPositive(3);\nconsole.log("ok");',
    ],
    "ts_discriminated_unions": [
        'type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };\nfunction area(s: Shape): number {\n  return s.kind === "circle" ? s.r * s.r * 3 : s.side * s.side;\n}\nconsole.log(area({ kind: "circle", r: 2 }));',
        'type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number } | { kind: "tri"; b: number; h: number };\nfunction area(s: Shape): number {\n  switch (s.kind) {\n    case "circle":\n      return 3 * s.r * s.r;\n    case "square":\n      return s.side * s.side;\n    case "tri":\n      return (s.b * s.h) / 2;\n    default: {\n      const unhandled: never = s;\n      return unhandled;\n    }\n  }\n}\nconsole.log(area({ kind: "tri", b: 4, h: 3 }));',
    ],
    "ts_structural_typing": [
        "type Point = { x: number; y: number };\nconst p: Point = { x: 1, y: 2 };\nconsole.log(p.x, p.y);",
        "type Point = { x: number; y: number };\nconst p: Point = { x: 1, y: 0 };\nconsole.log(p.x, p.y);",
    ],
    "ts_satisfies": [
        'const server = { host: "localhost", port: 8080 } satisfies { host: string; port: number };\nconsole.log(server.port + 1);',
        "const limit = 5 satisfies number;\nconsole.log(limit);",
    ],
    "ts_branded_types": [
        'declare const brand: unique symbol;\ntype Email = string & { readonly [brand]: "Email" };\nfunction send(to: Email): void {\n  console.log("to " + to);\n}\nsend("ana@example.com" as Email);',
        'declare const brand: unique symbol;\ntype Cents = number & { readonly [brand]: "Cents" };\nconst a = 150 as Cents;\nconst b = 250 as Cents;\nconst total = (a + b) as Cents;\nconsole.log(total);',
    ],
    "ts_generic_constraints": [
        'function longest<T extends { length: number }>(a: T, b: T): T {\n  return a.length >= b.length ? a : b;\n}\nconsole.log(longest("ten", "twenty"));',
        "type Box<T extends object> = { value: T };\nconst b: Box<{ label: string }> = { value: { label: \"ok\" } };\nconsole.log(b.value.label);",
    ],
    "ts_keyof_indexed": [
        'type Settings = { theme: string; fontSize: number };\ntype Theme = Settings["theme"];\nconst t: Theme = "dark";\nconsole.log(t);',
        'const defaults = { theme: "light", fontSize: 14 };\nfunction read(key: keyof typeof defaults) {\n  return defaults[key];\n}\nconsole.log(read("fontSize"));',
    ],
    "ts_mapped_types": [
        'type Signup = { name: string; age: number };\ntype Validators<T> = { [K in keyof T]: (value: T[K]) => boolean };\nconst rules: Validators<Signup> = { name: (v) => v.length > 1, age: (v) => v >= 18 };\nconsole.log(rules.name("ana"), rules.age(12));',
        'type Signup = { name: string; age: number };\ntype Validators<T> = { [K in keyof T]: (value: T[K]) => boolean };\nconst rules: Validators<Signup> = {\n  name: (v) => v.length > 1,\n  age: (v: number) => v > 0,\n};\nconsole.log(rules.age(3));',
    ],
    "ts_conditional_types": [
        'function describe(x: string | number): string | number {\n  return typeof x === "string" ? x.length : String(x);\n}\nconsole.log(describe("abc"), describe(7));',
        "function f(): string {\n  return \"x\";\n}\ntype R = ReturnType<typeof f>;\nconst r: R = \"ok\";\nconsole.log(r);",
    ],
    "ts_template_literal_types": [
        'type Size = `${number}px`;\nconst width: Size = "12px";\nconsole.log(width);',
        'type EventName = `${"user" | "order"}:${"created" | "deleted"}`;\nfunction emit(e: EventName): void {\n  console.log(e);\n}\nemit("user:deleted");',
    ],
    "ts_type_level": [
        'type Tree = string | Tree[];\nconst t: Tree = ["a", ["b"]];\nconsole.log(JSON.stringify(t));',
        "type Json = null | boolean | number | string | Json[] | { [key: string]: Json };\nconst doc: Json = { created: new Date(0).toISOString() };\nconsole.log(JSON.stringify(doc));",
    ],
    "ts_iterators": [
        "const scores = { ana: 3, ben: 5 };\nfor (const [name, score] of Object.entries(scores)) {\n  console.log(name, score);\n}",
        "function* ids(): Generator<number> {\n  yield 1;\n  yield 2;\n}\nconsole.log([...ids()].join(\",\"));",
    ],
    "ts_error_types": [
        'type Result<T> = { ok: true; value: T } | { ok: false; error: string };\nfunction parsePort(raw: string): Result<number> {\n  const n = Number(raw);\n  return Number.isInteger(n) ? { ok: true, value: n } : { ok: false, error: "not a number" };\n}\nconst r = parsePort("8080");\nconsole.log(r.ok ? r.value + 1 : r.error);',
        'type LoadError = { kind: "missing" } | { kind: "timeout"; ms: number };\nfunction message(e: LoadError): string {\n  switch (e.kind) {\n    case "missing":\n      return "not found";\n    case "timeout":\n      return `timed out after ${e.ms} ms`;\n    default: {\n      const unreachable: never = e;\n      return unreachable;\n    }\n  }\n}\nconsole.log(message({ kind: "timeout", ms: 500 }));',
    ],
    "ts_async_patterns": [
        'async function main(): Promise<void> {\n  const settled = await Promise.allSettled([Promise.resolve(1)]);\n  for (const r of settled) console.log(r.status === "fulfilled" ? r.value : "failed");\n}\nmain();',
        'async function count(): Promise<number> {\n  return 2;\n}\nasync function label(): Promise<string> {\n  return "items";\n}\nasync function main(): Promise<void> {\n  const [n, s]: [number, string] = await Promise.all([count(), label()]);\n  console.log(n, s);\n}\nmain();',
    ],
    "ts_declaration_files": [
        'const BUILD_ID: string = "dev";\nconsole.log(BUILD_ID);',
        'let version: string = "1.0";\nconsole.log(version);',
    ],
    "ts_ds_generics": [
        "class Stack<T> {\n  #items: T[] = [];\n  push(item: T): void {\n    this.#items.push(item);\n  }\n  get size(): number {\n    return this.#items.length;\n  }\n}\nconst s = new Stack<number>();\ns.push(3);\nconsole.log(s.size);",
        "class Stack<T> {\n  #items: T[] = [];\n  push(item: T): void {\n    this.#items.push(item);\n  }\n  clear(): void {\n    this.#items.length = 0;\n  }\n  get size(): number {\n    return this.#items.length;\n  }\n}\nconst s = new Stack<number>();\ns.push(1);\ns.clear();\nconsole.log(s.size);",
        "class Stack<T> {\n  #items: T[] = [];\n  push(item: T): void {\n    this.#items.push(item);\n  }\n  pop(): T | undefined {\n    return this.#items.pop();\n  }\n}\nconst s = new Stack<number>();\ns.push(4);\nconsole.log(s.pop()?.toFixed(1) ?? \"empty\");",
    ],
    "ts_tsconfig": [
        "const readings = [21.5, 22.1];\nconsole.log(readings[0]?.toFixed(1) ?? \"none\");",
        "function describe({ name, age }: { name: string; age: number }) {\n  return `${name} (${age})`;\n}\nconsole.log(describe({ name: \"ada\", age: 36 }));",
    ],
    "ts_program_io": [
        'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8");\nconsole.log(JSON.stringify(input));',
        'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\nconsole.log(Number(input) * 2);',
        'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\nconst n: number = Number(input);\nconsole.log(n + 1);',
    ],
    "ts_equality": [
        'const count: number = 3;\nconst label: string = "3";\nconsole.log(count === Number(label));',
        "const a: number | undefined = undefined;\nconst b = 0;\nconsole.log((a ?? b) || 5);",
    ],
    "ts_number_format": [
        "const count = 10n;\nconst total = count + 1n;\nconsole.log(total.toString());",
        'const price = "19.99";\nconst doubled = Number(price) * 2;\nconsole.log(doubled.toFixed(2));',
    ],
    "ts_regex": [
        'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\nconst m = input.match(/(\\d+)-(\\d+)/);\nconsole.log(m === null ? "no match" : m.length);',
        'const m = "a=1".match(/(\\w+)=(\\w+)/);\nif (m !== null) {\n  const value: string = (m[2] ?? "").toUpperCase();\n  console.log(value);\n}',
    ],
    "ts_unicode": [
        'const first: string = String("😀".codePointAt(0) ?? 0);\nconsole.log(first);',
        'const s = "héllo";\nconsole.log(s.normalize("NFC").length);',
    ],
    "ts_overloads": [
        'function parse(input: string): number;\nfunction parse(input: string[]): number[];\nfunction parse(input: string | string[]): number | number[];\nfunction parse(input: string | string[]): number | number[] {\n  return typeof input === "string" ? Number(input) : input.map(Number);\n}\nconst raw: string | string[] = Math.random() > 2 ? "1" : ["1"];\nconsole.log(parse(raw));',
        "function size(value: string): number;\nfunction size(value: number[]): number;\nfunction size(value: string | number[]): number {\n  return value.length;\n}\nconsole.log(size(\"abc\"), size([1, 2]));",
    ],
    "ts_closures_scope": [
        "let doubled = 0;\nfor (let i = 0; i < 3; i++) {\n  doubled = i * 2;\n}\nconsole.log(doubled);",
        "const total = 10;\nconsole.log(total);",
    ],
    "ts_recursion": [
        "function depth(tree: { children: unknown[] }): number {\n  return tree.children.length === 0\n    ? 1\n    : 1 + Math.max(...tree.children.map((c) => depth(c as { children: unknown[] })));\n}\nconsole.log(depth({ children: [] }));",
        "function power(base: number, exp: number): number {\n  if (exp === 0) return 1;\n  return base * power(base, exp - 1);\n}\nconsole.log(power(2, 10));",
    ],
    "ts_tuples": [
        'const pair: [string, number] = ["ada", 36];\nconsole.log(pair[1]);',
        "function range(): [number, number] {\n  const values: [number, number] = [1, 10];\n  return values;\n}\nconsole.log(range());",
    ],
    "ts_array_modern": [
        "const xs = [3, 1, 2];\nconsole.log(xs.at(-1)?.toFixed(1) ?? \"none\");",
        "const fixed: readonly number[] = [3, 1, 2];\nconsole.log(fixed.toSorted().join(\",\"));",
    ],
    "ts_interfaces_types": [
        'interface Base {\n  id: number;\n}\ninterface Record2 extends Base {\n  label: string;\n}\nconst r: Record2 = { id: 1, label: "a" };\nconsole.log(r.label);',
        'type User = { name: string; age?: number };\nconst u: User = { name: "ada" };\nconsole.log(u.name);',
    ],
    "ts_index_signatures": [
        'const limits = { small: 10, large: 100 };\nconst size: keyof typeof limits = "small";\nconsole.log(limits[size]);',
        'type Level = "info" | "warn" | "error";\nconst colour: Record<Level, string> = { info: "blue", warn: "yellow", error: "red" };\nconsole.log(colour.error);',
        'const settings: Record<"theme" | "lang", string> = { theme: "dark", lang: "en" };\nconsole.log(settings.theme);',
    ],
    "ts_function_types": [
        "type Visit = (value: number, index: number) => void;\nfunction each(xs: number[], visit: Visit) {\n  xs.forEach((x, i) => visit(x, i));\n}\neach([1, 2], (value: number, index: number) => console.log(value, index));",
        "type Handler = (event: string) => void;\nconst anyEvent = (event: string) => console.log(event);\nconst handler: Handler = anyEvent;\nhandler(\"click\");",
        'interface Account {\n  owner: string;\n}\nfunction greet(this: Account) {\n  return "hi " + this.owner;\n}\nconsole.log(greet.call({ owner: "ana" }));',
        "class Point {\n  x = 0;\n}\nconst p = new Point();\nconsole.log(p.x);",
    ],
    "ts_type_testing": [
        None,  # a type test, not a program to repair
        None,
    ],
    "ts_set_algebra": [
        'const tags = new Set(["a", "b"]);\nconst more = ["b", "c"];\nconsole.log([...tags.union(new Set(more))].join(","));',
        'const seen = new Map<string, number>();\nseen.set("id", 1);\nconsole.log(seen.has("id"));',
    ],
    "ts_literal_inference": [
        'type Direction = "up" | "down";\nfunction move(d: Direction): string {\n  return d === "up" ? "^" : "v";\n}\nlet current: Direction = "up";\nconsole.log(move(current));',
        "const LIMITS = { min: 1, max: 10 } as const;\nconst raised = { ...LIMITS, max: 20 };\nconsole.log(raised.max);",
    ],
    "ts_control_flow": [
        'function shout(items: string[], prefix: string | undefined): string[] {\n  const p = prefix ?? ">";\n  return items.map((item) => p.toUpperCase() + item);\n}\nconsole.log(shout(["a"], undefined).join(","));',
        'function assertPositive(n: number): asserts n is number {\n  if (n <= 0) throw new Error("not positive");\n}\nassertPositive(5);\nconsole.log("ok");',
        'type Circle = { radius: number };\ntype Square = { side: number };\nfunction area(s: Circle | Square): number {\n  return "radius" in s ? s.radius ** 2 * Math.PI : s.side ** 2;\n}\nconsole.log(area({ radius: 1 }).toFixed(2));',
    ],
    "ts_top_bottom": [
        'type Status = "active" | "paused" | "closed";\nfunction label(s: Status): string {\n  switch (s) {\n    case "active":\n      return "Active";\n    case "paused":\n      return "Paused";\n    case "closed":\n      return "Closed";\n    default: {\n      const unhandled: never = s;\n      return unhandled;\n    }\n  }\n}\nconsole.log(label("closed"));',
        "const data: unknown = JSON.parse('{\"name\":\"ada\"}');\nif (typeof data === \"object\" && data !== null && \"name\" in data) console.log(data.name);",
    ],
    "ts_erasable_syntax": [
        'type Circle = { radius: number };\ntype Square = { side: number };\nfunction area(s: Circle | Square): number {\n  if ("radius" in s) return Math.PI * s.radius ** 2;\n  return s.side ** 2;\n}\nconsole.log(area({ side: 3 }));',
        "const Level = { Debug: 10, Info: 20, Warn: 30 } as const;\ntype Level = (typeof Level)[keyof typeof Level];\nfunction show(level: Level): string {\n  return String(level);\n}\nconsole.log(show(Level.Warn));",
        'import { readFileSync } from "fs";\nconst text = readFileSync(0, "utf8");\nconsole.log(text.length);',
    ],
    "ts_versions": [
        "function total(prices: number[]) {\n  return prices.reduce((sum, p) => sum + p, 0);\n}\nconsole.log(total([1, 2, 3]));",
        'try {\n  JSON.parse("{");\n} catch (e) {\n  console.log(e instanceof Error ? "bad JSON" : String(e));\n}',
        'class Account {\n  owner: string;\n  balance = 0;\n  constructor(owner: string) {\n    this.owner = owner;\n  }\n}\nconsole.log(new Account("ana").owner);',
    ],
    "ts_variance": [
        'type Animal = { name: string };\ntype Dog = { name: string; bark: () => string };\ntype Handler<T> = (x: T) => void;\nconst handleAnimal: Handler<Animal> = (a) => console.log(a.name);\nconst handleDog: Handler<Dog> = handleAnimal;\nhandleDog({ name: "rex", bark: () => "woof" });',
        'type Animal = { name: string };\ntype Dog = { name: string; bark: () => string };\ntype Cell<T> = { get: () => T; set: (value: T) => void };\nfunction rename(cell: Cell<Animal>): void {\n  cell.set({ name: "tom" });\n}\nlet stored: Animal = { name: "rex" };\nconst animalCell: Cell<Animal> = { get: () => stored, set: (v) => { stored = v; } };\nrename(animalCell);\nconsole.log(animalCell.get().name);',
        None,  # a variance annotation on its own: no program
    ],
    "ts_parse_dont_validate": [
        'declare const EmailBrand: unique symbol;\ntype Email = string & { readonly [EmailBrand]: true };\nfunction parseEmail(s: string): Email | null {\n  return s.includes("@") ? (s as Email) : null;\n}\nfunction sendWelcome(to: Email): string {\n  return "welcome " + to;\n}\nconst email = parseEmail("ana@example.com");\nconsole.log(email === null ? "invalid" : sendWelcome(email));',
        "type NonEmpty = readonly [number, ...number[]];\nconst one: NonEmpty = [1];\nconsole.log(one.length);",
    ],
    "ts_runtime_validation": [
        None,  # declared schema functions: no runtime
        None,
    ],
    "ts_generic_inference": [
        "function filled(n: number): number[] {\n  return Array.from({ length: n }, () => 0);\n}\nconsole.log(filled(3).join(\",\"));",
        'function pick<T extends string>(options: readonly T[], fallback: NoInfer<T>): T {\n  return options[0] ?? fallback;\n}\nconsole.log(pick(["small", "large"], "large"));',
        "type Entity<T extends { id: number }> = { data: T; loadedAt: number };\nconst e: Entity<{ id: number; name: string }> = { data: { id: 1, name: \"a\" }, loadedAt: 0 };\nconsole.log(e.data.name);",
    ],
    "ts_lookup_types": [
        'type User = { id: number; email: string };\ntype Contact = User["email"];\nconst c: Contact = "a@x";\nconsole.log(c);',
        'const PRICES = { apple: 1.2, pear: 0.8 };\nfunction price(fruit: keyof typeof PRICES): number {\n  return PRICES[fruit];\n}\nconsole.log(price("pear"));',
        'type ValueAt<T, K extends keyof T> = T[K];\nconst v: ValueAt<{ a: number }, "a"> = 1;\nconsole.log(v);',
    ],
    "ts_key_remapping": [
        "type Getters<T> = {\n  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];\n};\nconst g: Getters<{ age: number }> = { getAge: () => 36 };\nconsole.log(g.getAge());",
        'type Getters<T> = {\n  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];\n};\nconst g: Getters<{ firstName: string }> = { getFirstName: () => "Ada" };\nconsole.log(g.getFirstName());',
    ],
    "ts_distributive": [
        "type ToArray<T> = T extends unknown ? T[] : never;\nconst mixed: ToArray<string | number> = [1, 2];\nconsole.log(mixed.join(\",\"));",
        'function assertNever(value: never): never {\n  throw new Error(String(value));\n}\nfunction label(v: string | number | boolean): string {\n  if (typeof v === "string") return "text";\n  if (typeof v === "number") return "number";\n  if (typeof v === "boolean") return "flag";\n  return assertNever(v);\n}\nconsole.log(label(true));',
    ],
    "ts_type_performance": [
        "type BuildWrapped<N extends number, T extends unknown[] = []> =\n  T[\"length\"] extends N ? [] : [0, ...BuildWrapped<N, [...T, 0]>];\ntype Few = BuildWrapped<3>;\nconst m: Few = [0, 0, 0];\nconsole.log(m.length);",
        'type Digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";\ntype Code = `${Digit}${Digit}${Digit}`;\nconst c: Code = "123";\nconsole.log(c);',
    ],
    "ts_class_design": [
        "abstract class Shape {\n  abstract area(): number;\n}\nclass Unit extends Shape {\n  area(): number {\n    return 1;\n  }\n}\nconst s = new Unit();\nconsole.log(s.area());",
        'abstract class Shape {\n  abstract area(): number;\n  abstract readonly name: string;\n}\nclass Square extends Shape {\n  readonly name = "square";\n  area(): number {\n    return 4;\n  }\n}\nconsole.log(new Square().area());',
        'class Base {\n  greet(): string {\n    return "hi";\n  }\n}\nclass Loud extends Base {\n  override greet(): string {\n    return "HI";\n  }\n}\nconsole.log(new Loud().greet());',
        None,  # a parameter property does not run under type stripping
    ],
    "ts_decorators": [
        'function logged<T extends () => string>(fn: T): T {\n  return fn;\n}\nconst greet = logged(() => "hi");\nconsole.log(greet());',
        None,  # decorators do not run under type stripping
    ],
    "ts_iterator_helpers": [
        "function firstTwo(items: Iterable<number>): number[] {\n  return Iterator.from(items).take(2).toArray();\n}\nconsole.log(firstTwo([5, 6, 7]).join(\",\"));",
        "const point = { x: 1, y: 2 };\nfor (const v of Object.values(point)) console.log(v);",
    ],
    "ts_heap_pq": [
        None,  # a declared class: no runtime
        None,
    ],
    "ts_resource_management": [
        'const handle = {\n  close() {\n    console.log("closed");\n  },\n  [Symbol.dispose]() {\n    this.close();\n  },\n};\nfunction read() {\n  using h = handle;\n  console.log("reading", typeof h);\n}\nread();',
        'async function read(conn: AsyncDisposable) {\n  await using c = conn;\n  console.log("using", typeof c);\n}\nread({ [Symbol.asyncDispose]: async () => console.log("released") });',
    ],
    "ts_error_cause": [
        'try {\n  JSON.parse("{");\n} catch (e) {\n  console.log(e instanceof Error ? "bad JSON" : String(e));\n}',
        'class HttpError extends Error {\n  readonly status: number;\n  constructor(status: number, message: string) {\n    super(message);\n    this.status = status;\n  }\n}\nfunction report(e: Error): number {\n  return e instanceof HttpError ? e.status : 500;\n}\nconsole.log(report(new HttpError(404, "missing")), report(new Error("x")));',
    ],
    "ts_event_loop": [
        'async function load(): Promise<string> {\n  const text = await Promise.resolve("data");\n  return text;\n}\nload().then(console.log);',
        'async function isReady(): Promise<boolean> {\n  return false;\n}\nasync function main(): Promise<void> {\n  if (await isReady()) console.log("ready!");\n  else console.log("not yet");\n}\nmain();',
    ],
    "ts_cancellation": [
        "const controller = new AbortController();\ncontroller.abort();\nconsole.log(controller.signal.aborted);",
        'async function main(): Promise<void> {\n  const { promise, resolve } = Promise.withResolvers<string>();\n  resolve("42");\n  console.log(await promise);\n}\nmain();',
    ],
    "ts_async_iteration": [
        "async function* ticks(): AsyncGenerator<number> {\n  yield 1;\n}\nasync function main(): Promise<void> {\n  for await (const t of ticks()) console.log(t);\n}\nmain();",
        "async function* ticks(): AsyncGenerator<number> {\n  yield 1;\n}\nasync function show(): Promise<void> {\n  for await (const t of ticks()) console.log(t);\n}\nshow();",
    ],
}
