# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New TypeScript chapters for Mastery Month 4 — Rigor.
#
#   week 14  ts_erasable_syntax      type stripping: which syntax can simply be
#                                    deleted, and what to write instead of the
#                                    rest (enum, namespace, parameter properties)
#   week 14  ts_versions             TypeScript 6.0's new defaults and
#                                    deprecations, TypeScript 7 (the native
#                                    compiler), and the strict family they assume
#   week 15  ts_variance             covariance, contravariance, bivariance and
#                                    `in`/`out` annotations
#   week 16  ts_parse_dont_validate  smart constructors and `unique symbol`
#                                    brands: illegal values made unconstructable
#   week 17  ts_runtime_validation   a mini schema library whose validators and
#                                    types come from one source
#
# Built with ts_chapter_kit.py's `_chapter`; every printed output and compiler
# message is computed (python tools/gen_ts_outputs.py). Code is written in raw
# strings so a TypeScript "\n" stays a backslash-n.
#
# Facts about TypeScript 6.0 and 7.0 were checked against the official release
# notes (typescriptlang.org release notes for 6.0; the TypeScript blog's
# "Announcing TypeScript 7.0", 2026-07-08) when this was written, per D-4. The
# app's own checker is still 5.9 — every compiler message shown is 5.9's.
# ---------------------------------------------------------------------------

_chapter(
    "ts_erasable_syntax", "TS: Runtime & Architecture",
    "Erasable Syntax & Type Stripping",
    "Which TypeScript syntax can simply be deleted to leave working JavaScript — and what to write instead of `enum`, `namespace` and parameter properties, which cannot.",
    "Node (22.18+, 23.6+, 24), Deno and Bun run `.ts` files by *stripping* the types: every annotation is replaced with whitespace and the rest runs as JavaScript. That only works for syntax with no runtime meaning. `enum`, `namespace` with values, parameter properties and `import x = require()` generate code, so a stripper rejects them. `--erasableSyntaxOnly` (TS 5.8) makes the compiler reject them too, and `verbatimModuleSyntax` makes every import say whether it is a type or a value. Every program in this app runs this way.",
    "Java's generics are erased too, but Java still has a compile step that generates code. TypeScript's whole type layer is designed to be erasable: nothing a type says survives to runtime — no reflection, no `instanceof SomeInterface`, no casts that convert. The few TypeScript features that break that rule are the ones this chapter replaces.",
    why=r"""
For most of TypeScript's life, running a `.ts` file meant compiling it first:
`tsc` (or Babel, esbuild, swc) read the whole program and wrote JavaScript. That
step is disappearing. Node runs `.ts` files directly, and so do Deno and Bun —
not by compiling them, but by **stripping** them: each annotation is replaced by
spaces, so line and column numbers stay exactly where they were, and whatever is
left is run as JavaScript.

Stripping is fast and simple because it does not understand your program. It
can only *delete*. That is fine for almost everything TypeScript adds — types
exist only for the checker — but a handful of older features are not types at
all. An `enum` becomes an object with reverse mappings; a `namespace` becomes a
function that builds an object; `constructor(private x: number)` quietly writes
`this.x = x`. Delete their syntax and you delete behaviour, so a stripper
refuses to run them.

Every program in this app — the judge, the editor's Run button — runs by
stripping. Knowing which syntax is erasable is knowing what will run.
""",
    idea=r"""
**The test for a feature: delete it — does the program still do the same thing?**

| Erasable (just deleted) | Not erasable (generates code) | Write instead |
|---|---|---|
| annotations, `interface`, `type` | `enum` | an `as const` object plus a derived union type |
| generics `<T>`, `as`, `satisfies`, `!` | `namespace` / `module` with values | ES modules, or a plain object |
| `declare`, `abstract`, `readonly` | parameter properties `constructor(private x)` | declare the field, assign it in the constructor |
| `private` / `protected` / `public` on members | `import x = require(...)`, `export =` | `import` / `export` |
| `import type`, `export type` | legacy (experimental) decorators | — (standard decorators aren't run by Node yet) |

**The replacement for `enum`** is a frozen table and a type computed from it:

```ts
const Level = { Debug: 10, Info: 20, Warn: 30 } as const;
type Level = (typeof Level)[keyof typeof Level];   // 10 | 20 | 30
```

One name is both a value (the object) and a type (its values) — the same trick
`class` uses. `Level.Info` reads like an enum member, `Object.values(Level)`
lists them, and unlike a numeric `enum` the type does not accept any number.

**Two flags keep you honest.** `--erasableSyntaxOnly` (TS 5.8) reports every
non-erasable construct as an error, so the type checker and the stripper agree
about what will run. `--verbatimModuleSyntax` requires an import used only for
types to say so — `import type { User } from "./user"` — because a stripper
cannot know which imports are types and would otherwise leave an import of a
module that exports no such value. A type-only import is deleted; a value import
is kept, exactly as written.

**What erasure means for your mental model.** Types are never available at
runtime. You cannot ask a value whether it is a `User`, cannot `instanceof` an
interface, and `as number` does not turn a string into a number. When runtime
behaviour depends on a type — parsing input, choosing a branch — you need a
*value* to test: a tag field, `typeof`, `in`, `Array.isArray`, or a validator
(week 17).
""",
    examples=[
        ("An enum, rewritten as data",
         r"""
const Direction = { Up: "UP", Down: "DOWN", Left: "LEFT", Right: "RIGHT" } as const;
type Direction = (typeof Direction)[keyof typeof Direction];

function opposite(d: Direction): Direction {
  switch (d) {
    case Direction.Up:
      return Direction.Down;
    case Direction.Down:
      return Direction.Up;
    case Direction.Left:
      return Direction.Right;
    case Direction.Right:
      return Direction.Left;
  }
}

console.log(opposite(Direction.Up));
console.log(Object.values(Direction).join(","));
console.log(Object.keys(Direction).length);
""", [""],
         "`Direction` the value is an ordinary object, so it runs untouched; `Direction` the type is `\"UP\" | \"DOWN\" | \"LEFT\" | \"RIGHT\"`. A string enum would print the same — but only after a compiler turned it into code."),
        ("Parameter properties, written out",
         r"""
class Point {
  readonly x: number;
  readonly y: number;
  private label: string;

  constructor(x: number, y: number, label = "p") {
    this.x = x;
    this.y = y;
    this.label = label;
  }

  distanceTo(other: Point): number {
    return Math.hypot(this.x - other.x, this.y - other.y);
  }

  toString(): string {
    return `${this.label}(${this.x}, ${this.y})`;
  }
}

const a = new Point(0, 0, "a");
const b = new Point(3, 4, "b");
console.log(`${a} to ${b}: ${a.distanceTo(b)}`);
""", [""],
         "`readonly` and `private` on a declared field are erasable — deleting them leaves a plain class field. What is not erasable is the shorthand `constructor(private label: string)`, which *also* generates the assignment; written out, the assignment is visible code."),
        ("Everything here is deleted before it runs",
         r"""
interface User {
  name: string;
  admin?: boolean;
}

function first<T>(xs: readonly T[]): T | undefined {
  return xs[0];
}

const users = [{ name: "ana" }, { name: "bo", admin: true }] satisfies User[];
const lead = first(users)!;
const count = users.length as number;

console.log(lead.name, count);
console.log(typeof lead, Array.isArray(users));
""", [""],
         "The interface, `<T>`, `readonly`, `satisfies`, `!` and `as` all vanish, leaving `function first(xs) { return xs[0]; }` and friends. At runtime `typeof lead` can only say `\"object\"` — the name `User` never existed there."),
        ("A namespace, as a plain object",
         r"""
const Temperature = {
  toFahrenheit(c: number): number {
    return (c * 9) / 5 + 32;
  },
  toCelsius(f: number): number {
    return ((f - 32) * 5) / 9;
  },
  describe(c: number): string {
    return c < 0 ? "freezing" : c < 20 ? "cool" : "warm";
  },
};

for (const c of [-5, 12, 30]) {
  console.log(`${c}C = ${Temperature.toFahrenheit(c)}F, ${Temperature.describe(c)}`);
}
console.log(Temperature.toCelsius(212));
""", [""],
         "A `namespace Temperature { export function … }` compiles to an immediately-invoked function that fills an object. An object literal is that object, written directly — and in a real project, a module (`temperature.ts`) is better still."),
    ],
    errors=[
        (2693, r"""
type Circle = { radius: number };
type Square = { side: number };
function area(s: Circle | Square): number {
  if (s instanceof Circle) return Math.PI * s.radius ** 2;
  return s.side ** 2;
}
""", "`Circle` is a type, and types are erased — at runtime there is nothing named `Circle` to test against. Test a value instead: `\"radius\" in s`, or give the shapes a tag."),
        (2749, r"""
const Level = { Debug: 10, Info: 20, Warn: 30 } as const;
function show(level: Level): string {
  return String(level);
}
""", "Only the *value* `Level` exists. The enum replacement needs its companion type: `type Level = (typeof Level)[keyof typeof Level];`."),
        (1361, r"""
import type { readFileSync } from "fs";
const text = readFileSync(0, "utf8");
console.log(text.length);
""", "`import type` promises the import is only used for types, so it is deleted before the program runs. Using it as a value would leave nothing to call — the compiler stops you."),
    ],
    pitfalls=[
        ("`as` does not convert",
         r"""
const raw: unknown = JSON.parse('"5"');
const n = raw as number;
console.log(n + 1);
""",
         r"""
const raw: unknown = JSON.parse('"5"');
const n = Number(raw);
console.log(n + 1);
""",
         "`as number` is deleted before the program runs; the value is still the string `\"5\"`, and `+ 1` concatenates. Converting is a runtime job — `Number(...)` — and asserting is only a promise to the compiler."),
        ("Asking a type a question at runtime",
         (r"""
type Circle = { radius: number };
type Square = { side: number };
function area(s: Circle | Square): number {
  if (s instanceof Circle) return 3 * s.radius ** 2;
  return s.side ** 2;
}
console.log(area({ radius: 1 }), area({ side: 2 }));
""", 2693),
         r"""
type Circle = { radius: number };
type Square = { side: number };
function area(s: Circle | Square): number {
  if ("radius" in s) return 3 * s.radius ** 2;
  return s.side ** 2;
}
console.log(area({ radius: 1 }), area({ side: 2 }));
""",
         "There is no `Circle` at runtime to be an instance of. `in` asks the value itself, and the compiler narrows on it just as well."),
        ("A narrower type does not remove data",
         r"""
type PublicUser = { name: string };
const user = { name: "ana", password: "hunter2" };
const shown: PublicUser = user;
console.log(JSON.stringify(shown));
""",
         r"""
type PublicUser = { name: string };
const user = { name: "ana", password: "hunter2" };
const shown: PublicUser = { name: user.name };
console.log(JSON.stringify(shown));
""",
         "The annotation `PublicUser` is erased; `shown` is the very same object, password included. A type can hide a property from the compiler, never from `JSON.stringify`. Build the smaller object explicitly."),
    ],
    later=[
        "**Week 15 — Structural typing and assertions.** Why an erased type system compares shapes, and why `as` is a claim.",
        "**Week 16 — Branded types.** A brand is a type-only property: zero runtime cost, because it is erased.",
        "**Week 17 — Runtime validation.** When behaviour depends on a type, you need a validator — a value that knows the type.",
        "**Week 23 — Classes.** Parameter properties and decorators, graded by the type checker only.",
    ],
    exercises=[
        _drill("ts_erasable_syntax-levels", "An enum replacement you can iterate",
               "`Level` is an `as const` object used as an enum. Replace `____` so the program prints every level name whose value is at least the input threshold, in declaration order.",
               r"""
import * as fs from "fs";
const Level = { Debug: 10, Info: 20, Warn: 30, Error: 40 } as const;
type Level = (typeof Level)[keyof typeof Level];
const threshold = Number(fs.readFileSync(0, "utf8").trim());
const names = Object.entries(Level).filter(([, value]) => value >= threshold).map(([name]) => name);
console.log(names.join(" ") || "(none)");
""", ["Object.entries(Level).filter(([, value]) => value >= threshold).map(([name]) => name)"],
               ["20", "0", "41", "40"],
               hint="`Object.entries` gives `[name, value]` pairs of the real object."),
        _drill("ts_erasable_syntax-fields", "Write the parameter properties out",
               "`constructor(readonly name: string, private qty: number)` would not survive type stripping. The fields are declared for you; replace `____` with the two assignments it would have generated.",
               r"""
import * as fs from "fs";
class Item {
  readonly name: string;
  private qty: number;
  constructor(name: string, qty: number) {
    this.name = name;
    this.qty = qty;
  }
  take(n: number): string {
    if (n > this.qty) return `only ${this.qty} ${this.name} left`;
    this.qty -= n;
    return `took ${n} ${this.name}, ${this.qty} left`;
  }
}
const [name = "", qty = "0", ...takes] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const item = new Item(name, Number(qty));
for (const t of takes) console.log(item.take(Number(t)));
""", ["this.name = name;\n    this.qty = qty;"],
               ["pens 5 2 2 2", "cups 1 1", "ink 10 3 3 3 3"],
               hint="A parameter property is shorthand for `this.<name> = <name>;` in the constructor."),
        _chal("ts_erasable_syntax-status", "Status codes without an enum", "Medium",
              "Define `const Status = { Active: \"A\", Suspended: \"S\", Closed: \"C\" } as const` and its companion type. Each input line is `<account> <code>`. Print `<account>: <Name>` for a known code (the key whose value it is) or `<account>: unknown code <code>`, then one line per status in declaration order: `<Name> <count>`.",
              r"""
const Status = { Active: "A", Suspended: "S", Closed: "C" } as const;
type Status = (typeof Status)[keyof typeof Status];
type StatusName = keyof typeof Status;
const names = Object.keys(Status) as StatusName[];
const nameOf = (code: string): StatusName | undefined => names.find((n) => Status[n] === code);
const counts = new Map<StatusName, number>();
for (const line of input.split("\n")) {
  const [account = "", code = ""] = line.trim().split(/\s+/);
  const name = nameOf(code);
  if (name === undefined) {
    console.log(`${account}: unknown code ${code}`);
    continue;
  }
  counts.set(name, (counts.get(name) ?? 0) + 1);
  console.log(`${account}: ${name}`);
}
for (const n of names) console.log(`${n} ${counts.get(n) ?? 0}`);
""", ["acc1 A\nacc2 C\nacc3 A\nacc4 X", "z S", "a C\nb C"],
              hint="`keyof typeof Status` is the union of names; search the names for the one whose value matches."),
    ],
    quiz=[
        _cq("Which of these survives type stripping unchanged?",
            "`function f<T>(x: T): T { return x as T; }`",
            ["`enum Color { Red }`", "`namespace Util { export const x = 1; }`", "`constructor(private id: number) {}`"],
            "Generics and `as` are only deleted. The other three generate runtime code, so a stripper rejects them."),
        _cq("What does `--erasableSyntaxOnly` do?",
            "Reports every construct that would need code generation, such as `enum` and parameter properties",
            ["Strips types from the output", "Forbids `interface`", "Makes every import type-only"],
            "It makes the type checker agree with a stripper about what can run."),
        _cq("Why does `verbatimModuleSyntax` require `import type` for type-only imports?",
            "A stripper can't tell which imports are types, so the source must say which ones to delete",
            ["Type imports are slower", "Interfaces can't be imported otherwise", "It prevents circular imports"],
            "The rule is: what you write is what runs. A type-only import is deleted; any other import is kept."),
        _cq("`const Level = { A: 1, B: 2 } as const; type Level = (typeof Level)[keyof typeof Level];` — what is the type `Level`?",
            "`1 | 2`",
            ["`\"A\" | \"B\"`", "`number`", "`{ A: 1; B: 2 }`"],
            "`keyof typeof Level` is the keys; indexing by them gives the values' literal types."),
        _cq("Why can't you write `x instanceof User` when `User` is an interface?",
            "Interfaces are erased — nothing named `User` exists at runtime",
            ["`instanceof` only works on arrays", "Interfaces need `implements` first", "You can, with `strict` on"],
            "`instanceof` needs a runtime constructor. Test a value (`in`, a tag, a validator) instead."),
        _cq("What does `const n = \"5\" as unknown as number; console.log(n + 1)` print?",
            "`51`",
            ["`6`", "It throws", "`NaN`"],
            "Assertions never convert. The value is still a string, so `+` concatenates."),
    ],
    interview=[
        ("What is type stripping, and what can't be stripped?",
         "Running TypeScript by replacing every type annotation with whitespace and executing the rest as JavaScript — what Node does natively now. It can't handle syntax that generates code: `enum`, `namespace` with values, parameter properties, `import =`/`export =`, and legacy decorators. `--erasableSyntaxOnly` makes the compiler reject exactly those."),
        ("What would you use instead of an `enum`?",
         "An `as const` object and a type derived from it: `const Color = { Red: \"red\" } as const; type Color = (typeof Color)[keyof typeof Color];`. It's plain JavaScript, it's iterable, it has no reverse-mapping surprises, and — unlike a numeric enum — the type doesn't accept arbitrary numbers."),
        ("Why can't TypeScript check a type at runtime?",
         "Because types are erased: the emitted JavaScript contains no trace of them. Runtime checks need values — `typeof`, `in`, `instanceof` on a class, a discriminant tag, or a schema validator that produces both the check and the type."),
    ],
)


_chapter(
    "ts_versions", "TS: Runtime & Architecture",
    "TypeScript 6 & 7",
    "What TypeScript 6.0 changed by default, what it deprecated, what TypeScript 7 (the native compiler) removed — and the `strict` family every modern project now assumes.",
    "TypeScript 6.0 is a bridge release: it turns `strict` on by default, defaults `module` to `esnext` and `types` to `[]`, and deprecates old options — `target: es5`, `moduleResolution: node`, `baseUrl`, `outFile`, AMD/UMD/SystemJS modules. TypeScript 7.0 (July 2026) is the compiler rewritten in Go, about 10× faster, and those deprecated options are hard errors there. The code you write barely changes; the configuration around it does.",
    "Java's language versions add features and almost never take anything away. TypeScript 6 and 7 are the opposite: nearly no new syntax, but a clean-out of configuration and defaults, so that the fast native compiler only has to support the modern subset.",
    why=r"""
Tools age. The TypeScript compiler was written in TypeScript, and for large
codebases it got slow — tens of seconds for a full check, long waits for the
editor. TypeScript 7 is the answer: the same compiler ported to Go, with native
speed and shared-memory parallelism.

A port is also a chance to stop carrying the past. Options that existed for
Internet Explorer (`target: es5`), for module systems nobody ships any more
(AMD, UMD, SystemJS) or for resolution rules Node abandoned years ago were
deprecated in **TypeScript 6.0** — the last release of the old compiler — so
projects could fix their configuration *before* moving to 7.

For you, that means two things. A new project today starts with `strict` on
and modern modules, whether or not it says so. And when you meet an old
`tsconfig.json`, you should recognise which parts are about to stop working.
""",
    idea=r"""
**TypeScript 6.0 changed these defaults** (a `tsconfig.json` that sets them
explicitly is unaffected):

| option | before 6.0 | 6.0 |
|---|---|---|
| `strict` | `false` | `true` |
| `module` | `commonjs` | `esnext` |
| `target` | `es5` | the current year's ES version (`es2025`) |
| `types` | every `@types` package installed | `[]` — list the ones you want, e.g. `["node"]` |
| `rootDir` | inferred from your files | the folder containing `tsconfig.json` |
| `noUncheckedSideEffectImports` | `false` | `true` |

**…and deprecated these.** In 6.0 they still work behind
`"ignoreDeprecations": "6.0"`; in 7.0 they are errors.

- `target: es5` and `downlevelIteration` (ES2015 is the floor now)
- `module: amd`, `umd`, `systemjs`, `none`, and `outFile`
- `moduleResolution: node` (a.k.a. `node10`) and `classic` — use `nodenext`
  for Node, `bundler` for bundled apps
- `baseUrl`; `esModuleInterop: false` and `allowSyntheticDefaultImports: false`
  (both are always on); `alwaysStrict: false`
- the `module Foo { }` spelling of a namespace, and `asserts` on imports (import
  attributes use `with { type: "json" }`)

6.0 also added an `es2025` target and library (Set methods, iterator helpers and
`Promise.try` moved there from `esnext`) and typings for `RegExp.escape`,
`Map.prototype.getOrInsert` and the Temporal API.

**TypeScript 7.0** shipped on 8 July 2026. It installs and runs exactly as
before — the `typescript` package, the `tsc` command — and is typically 8–12×
faster on a full build. Two things to know: the 6.0 deprecations are gone for
good, and 7.0 ships **no compiler API**, so tools that drive the compiler
programmatically use a compatibility package (`@typescript/typescript6`) until
the new API lands.

**The `strict` family.** `strict: true` is shorthand for a set of flags; the
ones you will actually meet are `noImplicitAny` (a parameter must have a type),
`strictNullChecks` (`null`/`undefined` are their own types),
`strictFunctionTypes` (week 13), `strictPropertyInitialization` (a class field
must be assigned), and `useUnknownInCatchVariables` (`catch (e)` gives
`unknown`). Two valuable flags are *not* in `strict` and you turn them on
yourself: `noUncheckedIndexedAccess` (this programme's weeks 14+) and
`exactOptionalPropertyTypes`.

**What this app runs.** Programs execute on Node 24 by type stripping, and are
checked by TypeScript 5.9 with `strict` on — the settings 6.0 made the
default — which is why every message in this chapter is 5.9's.
""",
    examples=[
        ("`catch` gives you `unknown` — narrow it",
         r"""
function parsePort(text: string): number {
  const n = Number(text);
  if (!Number.isInteger(n) || n < 1 || n > 65535) throw new RangeError(`not a port: ${text}`);
  return n;
}

for (const t of ["8080", "http", "70000"]) {
  try {
    console.log(parsePort(t));
  } catch (e) {
    console.log(e instanceof Error ? `${e.name}: ${e.message}` : String(e));
  }
}
""", [""],
         "Under `useUnknownInCatchVariables` (part of `strict`), `e` is `unknown`: anything can be thrown, not just `Error`s. `instanceof Error` narrows it before `.name` and `.message` are read."),
        ("Every field assigned, every parameter typed",
         r"""
class Counter {
  count = 0;
  readonly label: string;

  constructor(label: string) {
    this.label = label;
  }

  add(step: number): this {
    this.count += step;
    return this;
  }
}

const c = new Counter("clicks").add(2).add(3);
console.log(`${c.label}: ${c.count}`);
""", [""],
         "`strictPropertyInitialization` checks that `label` is assigned in the constructor and `count` has an initialiser; `noImplicitAny` is why `step` needs its `: number`. Both are on by default from 6.0."),
        ("ES2025 built-ins, in `es2025` from 6.0",
         r"""
const a = new Set(["ts", "go", "rust"]);
const b = new Set(["go", "java"]);
console.log([...a.union(b)].join(","));
console.log([...a.intersection(b)].join(","));

const doubled = [1, 2, 3, 4].values().filter((n) => n % 2 === 0).map((n) => n * 10).toArray();
console.log(doubled.join(","));

const byLength = Object.groupBy(["a", "bb", "cc", "d"], (w) => String(w.length));
console.log(JSON.stringify(byLength));
""", [""],
         "Set methods and iterator helpers were `esnext` library features until TypeScript 6.0 moved them into the new `es2025` target and library. Node 24 runs them natively."),
    ],
    errors=[
        (7006, r"""
function total(prices) {
  return prices.reduce((sum, p) => sum + p, 0);
}
""", "`noImplicitAny`: a parameter with no annotation and nothing to infer from would silently be `any`. Under `strict` — the default from 6.0 — it must be typed."),
        (18046, r"""
try {
  JSON.parse("{");
} catch (e) {
  console.log(e.message);
}
""", "`useUnknownInCatchVariables`: the caught value is `unknown`, because JavaScript can throw anything. Narrow it with `e instanceof Error` first."),
        (2564, r"""
class Account {
  owner: string;
  balance = 0;
}
""", "`strictPropertyInitialization`: `owner` is declared as a `string` but nothing ever assigns it, so it would really be `undefined`."),
    ],
    pitfalls=[
        ("A catch that assumes an `Error`",
         r"""
function risky(): never {
  throw "disk full";
}
try {
  risky();
} catch (e) {
  console.log("failed: " + (e as Error).message);
}
""",
         r"""
function risky(): never {
  throw "disk full";
}
try {
  risky();
} catch (e) {
  console.log("failed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         "`as Error` silences the compiler, and a thrown string has no `message`. `unknown` is telling the truth — narrow instead of asserting."),
        ("A definite-assignment `!` that was never earned",
         r"""
class Job {
  name!: string;
  describe(): string {
    return "job " + this.name;
  }
}
console.log(new Job().describe());
""",
         r"""
class Job {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
  describe(): string {
    return "job " + this.name;
  }
}
console.log(new Job("backup").describe());
""",
         "`name!:` tells `strictPropertyInitialization` \"trust me, it's assigned\" — and it isn't, so the program prints `undefined`. Assign it in the constructor and the check does its job."),
        ("An untyped parameter",
         (r"""
function average(xs) {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
console.log(average([2, 4, 9]));
""", 7006),
         r"""
function average(xs: readonly number[]): number {
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}
console.log(average([2, 4, 9]));
""",
         "Without `strict` this compiles, and `xs` is `any` — `average(\"abc\")` would compile too. From TypeScript 6.0, a project gets this error unless it opts out."),
    ],
    later=[
        "**Week 14 — tsconfig.** The rest of the configuration file: modules, resolution, and the flags not in `strict`.",
        "**Week 25 — Errors.** `catch (e: unknown)`, `Error` subclasses and `cause`, in depth.",
        "**Week 23 — Classes.** Field initialisation and `this`-returning methods.",
    ],
    exercises=[
        _drill("ts_versions-catch", "Narrow what was caught",
               "Each input line is parsed as JSON. Replace `____` so a failure prints `bad: <message>` for an `Error`, or `bad: <value>` for anything else thrown.",
               r"""
import * as fs from "fs";
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  try {
    const value: unknown = JSON.parse(line);
    console.log(`ok: ${typeof value}`);
  } catch (e) {
    console.log(`bad: ${e instanceof Error ? e.message.split(" ")[0] : String(e)}`);
  }
}
""", ['e instanceof Error ? e.message.split(" ")[0] : String(e)'],
               ["1\n\"x\"\n{", "[1,2]\nnull", "tru"],
               hint="`e` is `unknown`. Narrow with `instanceof Error` before reading `.message`."),
        _drill("ts_versions-init", "Assign every field",
               "`strictPropertyInitialization` requires each field to be assigned. Replace `____` so the constructor assigns `name` and starts `visits` at the given number.",
               r"""
import * as fs from "fs";
class Page {
  name: string;
  visits: number;
  constructor(name: string, visits: number) {
    this.name = name;
    this.visits = visits;
  }
  visit(): string {
    this.visits++;
    return `${this.name}: ${this.visits}`;
  }
}
const [name = "", start = "0", times = "1"] = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const page = new Page(name, Number(start));
for (let i = 0; i < Number(times); i++) console.log(page.visit());
""", ["this.name = name;\n    this.visits = visits;"],
               ["home 0 2", "about 41 1", "faq 7 3"],
               hint="Two assignments to `this`."),
        _chal("ts_versions-config", "Audit a tsconfig", "Medium",
              "The input is a list of `option=value` lines from an old `tsconfig.json`. For each line print `<option>=<value>: ok`, or `deprecated in 6.0` when it is one of: `target=es5`, `downlevelIteration=true`, `module=amd`, `module=umd`, `module=systemjs`, `module=none`, `moduleResolution=node`, `moduleResolution=node10`, `moduleResolution=classic`, `outFile=<anything>`, `baseUrl=<anything>`, `esModuleInterop=false`, `allowSyntheticDefaultImports=false`, `alwaysStrict=false`. Then print `<k> to fix before TypeScript 7`.",
              r"""
const ANY_VALUE = new Set(["outFile", "baseUrl"]);
const DEPRECATED = new Set([
  "target=es5", "downlevelIteration=true", "module=amd", "module=umd", "module=systemjs", "module=none",
  "moduleResolution=node", "moduleResolution=node10", "moduleResolution=classic",
  "esModuleInterop=false", "allowSyntheticDefaultImports=false", "alwaysStrict=false",
]);
let toFix = 0;
for (const line of input.split("\n")) {
  const entry = line.trim();
  const option = entry.split("=")[0] ?? "";
  const deprecated = DEPRECATED.has(entry) || ANY_VALUE.has(option);
  if (deprecated) toFix++;
  console.log(`${entry}: ${deprecated ? "deprecated in 6.0" : "ok"}`);
}
console.log(`${toFix} to fix before TypeScript 7`);
""", ["target=es5\nmodule=esnext\nbaseUrl=./src\nstrict=true", "moduleResolution=bundler\nesModuleInterop=false\noutFile=out.js", "module=nodenext"],
              hint="Two lookups: exact `option=value` pairs, and options that are deprecated whatever their value."),
    ],
    quiz=[
        _cq("In TypeScript 6.0, what is `strict` if a tsconfig doesn't mention it?",
            "`true`", ["`false`", "It depends on `target`", "It must be set explicitly"],
            "6.0 flipped the default. A project that wants the old behaviour has to say `\"strict\": false`."),
        _cq("Which option did TypeScript 6.0 deprecate?",
            "`moduleResolution: node` (node10)",
            ["`moduleResolution: bundler`", "`module: nodenext`", "`noUncheckedIndexedAccess`"],
            "Use `nodenext` for Node and `bundler` for bundled apps."),
        _cq("What does `\"ignoreDeprecations\": \"6.0\"` do in TypeScript 7.0?",
            "Nothing useful — the deprecated options are removed and are errors",
            ["Silences the errors, as in 6.0", "Switches 7.0 into 6.0 mode", "Enables the old JavaScript compiler"],
            "It is a 6.0 transition aid. 7.0 has no switch to bring the options back."),
        _cq("What is TypeScript 7.0?",
            "The compiler ported to Go — same `typescript` package and `tsc` command, roughly 10× faster",
            ["A new language with different syntax", "A runtime that replaces Node", "A linter"],
            "The language is the same; the implementation is native."),
        _cq("Which flag is NOT part of `strict`?",
            "`noUncheckedIndexedAccess`",
            ["`strictNullChecks`", "`noImplicitAny`", "`useUnknownInCatchVariables`"],
            "It's valuable but disruptive, so it is opt-in. So is `exactOptionalPropertyTypes`."),
        _cq("A 6.0 project doesn't list `types`. What happens to the `@types/node` package it has installed?",
            "It isn't loaded — the default is now `[]`, so it must be listed",
            ["It's loaded, as before", "It's loaded only for `.d.ts` files", "It's an error to have it installed"],
            "6.0 changed the default from 'every installed @types package' to none; add `\"types\": [\"node\"]`."),
    ],
    interview=[
        ("What changed in TypeScript 6.0?",
         "It's a transition release. Defaults moved to modern settings — `strict` on, `module: esnext`, `target` of the current ES year, `types: []` — and legacy options were deprecated: ES5 targets, AMD/UMD/SystemJS, `outFile`, `moduleResolution: node`, `baseUrl`. They still work with `ignoreDeprecations: \"6.0\"`, but TypeScript 7 removes them."),
        ("What's TypeScript 7?",
         "The compiler rewritten in Go, released in July 2026 — the same language, the same `tsc`, but typically 8–12× faster thanks to native code and parallel checking. The 6.0 deprecations are hard errors, and 7.0 ships without the old JavaScript compiler API, so tools that embed the compiler use a compatibility package for now."),
        ("Which compiler flags would you turn on in a new project, beyond `strict`?",
         "`noUncheckedIndexedAccess`, so array and record reads admit they may be `undefined`; `exactOptionalPropertyTypes`, so an optional property can't be explicitly set to `undefined` unless the type says so; and `verbatimModuleSyntax` plus `erasableSyntaxOnly` if the code runs by type stripping."),
    ],
)


_chapter(
    "ts_variance", "TS: Type System",
    "Variance",
    "When a container or a function of a subtype can stand in for one of a supertype: covariance, contravariance, invariance, the unsound corners, and `in`/`out` annotations.",
    "`Dog` fits where `Animal` is expected. Does `Dog[]` fit `Animal[]`? Does a handler for `Dog`s fit where a handler for `Animal`s is expected? Variance is the rule that answers: things that *produce* a type follow its direction (covariant), things that *consume* it go the opposite way (contravariant), and things that do both fit only exactly (invariant). TypeScript mostly gets this right — and knowing where it deliberately doesn't (mutable arrays, method parameters) is what keeps you out of the bugs.",
    "Java arrays are covariant and throw `ArrayStoreException` when you exploit it; Java generics are invariant unless you write `? extends T` (producer) or `? super T` (consumer) at the use site. TypeScript measures variance automatically from how a type parameter is used, allows `in`/`out` annotations on the declaration, and — unlike Java — does not check array writes at runtime at all.",
    why=r"""
Subtyping is easy to state for plain values: a `Dog` has everything an
`Animal` has, so a `Dog` can go anywhere an `Animal` can. The hard questions come
one level up, as soon as the type is *inside* something:

- A function wants a list of animals. Can it have your list of dogs?
- An event system wants a handler for any animal event. Can it have the handler
  you wrote for dogs?
- A cache is typed `Cell<Animal>`. Can it hold your `Cell<Dog>`?

The answers are different — yes, no, and no — and the reason is the same rule
applied three ways. Get it wrong in one direction and the compiler rejects
reasonable code; get it wrong in the other and a dog-handler gets called with a
cat. This chapter is the rule, plus the two places TypeScript knowingly breaks
it for convenience.
""",
    idea=r"""
Write `Dog ≤ Animal` for "a `Dog` is assignable to an `Animal`". For a type
built from `T`, ask which way assignability goes:

| shape | `F<Dog>` vs `F<Animal>` | name |
|---|---|---|
| produces `T` — `() => T`, `readonly T[]`, a getter | `F<Dog> ≤ F<Animal>` — same direction | **covariant** |
| consumes `T` — `(x: T) => void`, a setter, a comparator | `F<Animal> ≤ F<Dog>` — reversed | **contravariant** |
| both — `{ get(): T; set(x: T): void }` | neither, unless equal | **invariant** |

The intuition: a producer of dogs is a fine producer of animals (every dog is an
animal). A *consumer* of animals is a fine consumer of dogs (it can handle any
animal, so certainly a dog) — but a consumer of dogs is not a consumer of
animals, because it might be handed a cat.

**TypeScript measures this for you.** It works out each type parameter's
variance from how the type uses it. From TS 4.7 you can also *declare* it —
`interface Source<out T>`, `interface Sink<in T>`, `interface Cell<in out T>` —
and the compiler checks your declaration against the body. Annotations document
intent and speed up checking; they never make something unsound pass.

**Two deliberate holes.**

1. **Arrays are covariant even though they are mutable.** `Dog[]` is accepted as
   `Animal[]`, and nothing stops the receiver from pushing a cat into it.
   Honest covariance needs `readonly Animal[]` — which, since it cannot be
   written to, really is safe.
2. **Method parameters are bivariant.** A member declared with method syntax,
   `handle(x: T): void`, is compared both ways (week 13 showed the bug). A
   member declared as a property, `handle: (x: T) => void`, is checked
   contravariantly under `strictFunctionTypes`.

Mutable object properties are the same story as arrays: `{ pet: Dog }` is
accepted as `{ pet: Animal }`. Make the property `readonly` and the assignment
through the wider type becomes a compile error.
""",
    examples=[
        ("Producers follow the subtype",
         r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
type Getter<T> = () => T;

const rex: Dog = { name: "rex", bark: () => "woof" };
const getDog: Getter<Dog> = () => rex;
const getAnimal: Getter<Animal> = getDog; // covariant: fine

console.log(getAnimal().name);
console.log(getDog().bark());
""", [""],
         "Anything that calls `getAnimal` expects an animal back, and a dog is one. The arrow `Getter<Dog> → Getter<Animal>` points the same way as `Dog → Animal`."),
        ("Consumers go the other way",
         r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
type Handler<T> = (x: T) => string;

const describeAnimal: Handler<Animal> = (a) => "an animal called " + a.name;
const describeDog: Handler<Dog> = describeAnimal; // contravariant: fine

const dogs: Dog[] = [{ name: "rex", bark: () => "woof" }, { name: "fido", bark: () => "arf" }];
console.log(dogs.map(describeDog).join("; "));
""", [""],
         "A handler that copes with *any* animal certainly copes with dogs, so `Handler<Animal>` fits where `Handler<Dog>` is wanted. The reverse would hand a dog-handler a cat."),
        ("`readonly` arrays are honestly covariant",
         r"""
type Animal = { name: string };
type Dog = { name: string; breed: string };

function names(animals: readonly Animal[]): string {
  return animals.map((a) => a.name).join(", ");
}

const dogs: Dog[] = [{ name: "rex", breed: "lab" }, { name: "ada", breed: "pug" }];
console.log(names(dogs));
console.log(dogs.length);
""", [""],
         "`names` promises not to write, so passing `Dog[]` as `readonly Animal[]` is safe, not just allowed. Prefer `readonly` parameters whenever a function only reads."),
        ("Declaring variance with `out` and `in`",
         r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };

interface Source<out T> {
  next(): T;
}
interface Sink<in T> {
  put(value: T): void;
}

const kennel: Source<Dog> = { next: () => ({ name: "rex", bark: () => "woof" }) };
const anyAnimals: Source<Animal> = kennel;

const lines: string[] = [];
const register: Sink<Animal> = { put: (a) => lines.push("registered " + a.name) };
const registerDog: Sink<Dog> = register;

registerDog.put(kennel.next());
console.log(lines.join("\n"));
console.log("the animal view sees " + anyAnimals.next().name);
""", [""],
         "`out T` says `T` only comes out of a `Source`; `in T` says it only goes into a `Sink`. The compiler checks both claims against the interface bodies — and they are erased like every other type annotation."),
    ],
    errors=[
        (2322, r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
type Handler<T> = (x: T) => void;
const handleDog: Handler<Dog> = (d) => console.log(d.bark());
const handleAnimal: Handler<Animal> = handleDog;
""", "A `Handler<Animal>` may be called with a cat, and `handleDog` would call `bark` on it. Parameter types are contravariant: this direction is rejected."),
        (2345, r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
type Cell<T> = { get: () => T; set: (value: T) => void };
function rename(cell: Cell<Animal>): void {
  cell.set({ name: "tom" });
}
const dogCell: Cell<Dog> = { get: () => ({ name: "rex", bark: () => "woof" }), set: () => {} };
rename(dogCell);
""", "`Cell` both produces and consumes `T`, so it is invariant: a `Cell<Dog>` is not a `Cell<Animal>`, because `rename` could store a non-dog in it."),
        (2636, r"""
interface Box<out T> {
  get(): T;
  set: (value: T) => void;
}
""", "The annotation claims `T` only comes *out* of a `Box`, but `set` takes one *in*. (Declared with method syntax, `set(value: T)`, it would slip through — method parameters are bivariant.) A variance annotation is checked against the body — here it should be `in out T`, or no annotation at all."),
    ],
    pitfalls=[
        ("A mutable array accepted as a wider one",
         r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
function adopt(animals: Animal[]): void {
  animals.push({ name: "tom the cat" });
}
const dogs: Dog[] = [{ name: "rex", bark: () => "woof" }];
adopt(dogs);
for (const d of dogs) {
  console.log(typeof d.bark === "function" ? d.bark() : d.name + " cannot bark");
}
""",
         r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
function adopt(animals: readonly Animal[]): Animal[] {
  return [...animals, { name: "tom the cat" }];
}
const dogs: Dog[] = [{ name: "rex", bark: () => "woof" }];
const shelter = adopt(dogs);
for (const d of dogs) console.log(d.bark());
console.log(shelter.length + " animals in the shelter");
""",
         "Arrays are covariant for convenience, so `Dog[]` passed as `Animal[]` compiles — and `adopt` puts a cat in your list of dogs. A `readonly` parameter can't be written through; return a new array instead."),
        ("A mutable property accepted as a wider one",
         r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
type Holder = { pet: Animal };
const dogHouse: { pet: Dog } = { pet: { name: "rex", bark: () => "woof" } };
const house: Holder = dogHouse;
house.pet = { name: "tom" };
console.log(typeof dogHouse.pet.bark === "function" ? dogHouse.pet.bark() : "the dog house holds a cat");
""",
         (r"""
type Animal = { name: string };
type Dog = { name: string; bark: () => string };
type Holder = { readonly pet: Animal };
const dogHouse: { pet: Dog } = { pet: { name: "rex", bark: () => "woof" } };
const house: Holder = dogHouse;
house.pet = { name: "tom" };
console.log(dogHouse.pet.bark());
""", 2540),
         "Object properties are covariant just like arrays, and just as unsound when written. Marking the property `readonly` in the wider view turns the bad write into a compile error."),
        ("An annotation that claims too much",
         (r"""
interface Channel<out T> {
  receive(): T;
  send: (value: T) => void;
}
const log: string[] = [];
const ch: Channel<string> = { receive: () => "ping", send: (v) => { log.push(v); } };
ch.send(ch.receive());
console.log(log.join(","));
""", 2636),
         r"""
interface Channel<in out T> {
  receive(): T;
  send: (value: T) => void;
}
const log: string[] = [];
const ch: Channel<string> = { receive: () => "ping", send: (v) => { log.push(v); } };
ch.send(ch.receive());
console.log(log.join(","));
""",
         "`T` flows both in and out of a channel, so it is invariant: `in out T`. The compiler won't let `out` stand, which is the point of writing annotations — they are checked documentation."),
    ],
    later=[
        "**Week 16 — Immutability.** `readonly` arrays and properties, which is what makes covariance safe.",
        "**Week 18 — Generics.** Every generic you write has a variance; `in`/`out` let you state it.",
        "**Week 23 — Classes.** Method overrides and the bivariance of method parameters.",
    ],
    exercises=[
        _drill("ts_variance-comparator", "One comparator for every subtype",
               "A comparator only *reads* its arguments, so one written for `Animal` sorts any list of animals — including `Dog`s. Replace `____` so `sorted` holds the dogs ordered by name, without modifying `dogs`.",
               r"""
import * as fs from "fs";
type Animal = { name: string };
type Dog = { name: string; breed: string };
const byName = (a: Animal, b: Animal): number => a.name.localeCompare(b.name);
const dogs: Dog[] = fs.readFileSync(0, "utf8").trim().split("\n").map((line) => {
  const [name = "", breed = ""] = line.trim().split(/\s+/);
  return { name, breed };
});
const sorted = dogs.toSorted(byName);
for (const d of sorted) console.log(`${d.name} (${d.breed})`);
console.log(`first input: ${dogs[0]?.name}`);
""", ["dogs.toSorted(byName)"],
               ["rex lab\nada pug\nmilo beagle", "solo mutt", "b x\na y"],
               hint="`toSorted` returns a sorted copy; `byName` fits its comparator slot for `Dog`s because it accepts any `Animal`."),
        _drill("ts_variance-readonly", "A read-only parameter accepts subtypes",
               "`oldest` only reads its argument, so it takes `readonly Person[]` — and a list of `Employee`s fits. Replace `____` with the expression that returns the oldest person's name (the first on a tie).",
               r"""
import * as fs from "fs";
type Person = { name: string; age: number };
type Employee = { name: string; age: number; team: string };
function oldest(people: readonly Person[]): string {
  return people.reduce((best, p) => (p.age > best.age ? p : best)).name;
}
const staff: Employee[] = fs.readFileSync(0, "utf8").trim().split("\n").map((line) => {
  const [name = "", age = "0", team = ""] = line.trim().split(/\s+/);
  return { name, age: Number(age), team };
});
console.log(oldest(staff));
console.log(staff.map((e) => e.team).join(","));
""", ["people.reduce((best, p) => (p.age > best.age ? p : best)).name"],
               ["ana 31 web\nbo 45 ops\ncy 45 web", "dee 20 qa"],
               hint="`reduce` without an initial value starts from the first element; keep the current best unless someone is strictly older."),
        _chal("ts_variance-handlers", "One logger, every event list", "Medium",
              "Events are `<ms> key <k>` or `<ms> click <x> <y>`. Write `logAny(e: BaseEvent)` once and put it in *both* a `((e: KeyEvent) => string)[]` list and a `((e: ClickEvent) => string)[]` list, alongside a specific handler for each (`key <k>`, `click <x>,<y>`). For every event print the output of each handler in its list, joined by ` | `. Unknown lines print `skip`.",
              r"""
type BaseEvent = { type: string; at: number };
type KeyEvent = { type: "key"; at: number; key: string };
type ClickEvent = { type: "click"; at: number; x: number; y: number };
const logAny = (e: BaseEvent): string => `${e.at}ms ${e.type}`;
const keyHandlers: ((e: KeyEvent) => string)[] = [logAny, (e) => `key ${e.key}`];
const clickHandlers: ((e: ClickEvent) => string)[] = [logAny, (e) => `click ${e.x},${e.y}`];
for (const line of input.split("\n")) {
  const [at = "", type = "", a = "", b = ""] = line.trim().split(/\s+/);
  if (type === "key" && a !== "") {
    const e: KeyEvent = { type, at: Number(at), key: a };
    console.log(keyHandlers.map((h) => h(e)).join(" | "));
  } else if (type === "click" && a !== "" && b !== "") {
    const e: ClickEvent = { type, at: Number(at), x: Number(a), y: Number(b) };
    console.log(clickHandlers.map((h) => h(e)).join(" | "));
  } else {
    console.log("skip");
  }
}
""", ["10 key a\n25 click 3 4\n30 hover\n41 key Z", "5 click 0 0"],
              hint="A function that accepts any `BaseEvent` is assignable to one that accepts a `KeyEvent` — parameters are contravariant."),
    ],
    quiz=[
        _cq("`Dog` is assignable to `Animal`. Which is assignable to which for `type Getter<T> = () => T`?",
            "`Getter<Dog>` to `Getter<Animal>`",
            ["`Getter<Animal>` to `Getter<Dog>`", "Neither", "Both"],
            "A getter produces `T`, so it is covariant: same direction as `Dog → Animal`."),
        _cq("And for `type Handler<T> = (x: T) => void`?",
            "`Handler<Animal>` to `Handler<Dog>`",
            ["`Handler<Dog>` to `Handler<Animal>`", "Neither", "Both"],
            "A handler consumes `T`: contravariant. A handler of any animal can handle a dog."),
        _cq("Why is passing `Dog[]` where `Animal[]` is expected unsound?",
            "The receiver can push a non-dog into your array",
            ["Arrays are compared by length", "It isn't — arrays are read-only", "Dog[] has fewer methods"],
            "TypeScript allows it for convenience; `readonly Animal[]` makes it genuinely safe."),
        _cq("What variance does `{ get(): T; set(v: T): void }` have in `T`?",
            "Invariant", ["Covariant", "Contravariant", "Bivariant"],
            "It both produces and consumes `T`, so only the exact same `T` fits."),
        _cq("What does `interface Source<out T>` do?",
            "Declares `T` covariant, and the compiler checks that `T` is only produced",
            ["Makes `T` optional", "Exports `T`", "Makes `Source` readonly at runtime"],
            "Variance annotations are checked, erased documentation."),
        _cq("Which declaration gets the strict, contravariant parameter check under `strictFunctionTypes`?",
            "`handle: (x: T) => void`",
            ["`handle(x: T): void`", "Both", "Neither"],
            "Method syntax stays bivariant; property syntax with a function type is checked contravariantly."),
    ],
    interview=[
        ("Explain covariance and contravariance.",
         "If `Dog` is a subtype of `Animal`, a covariant `F` keeps the direction — `F<Dog>` is usable as `F<Animal>` — which is right for things that produce `T`, like getters and read-only arrays. A contravariant `F` reverses it — `F<Animal>` is usable as `F<Dog>` — which is right for things that consume `T`, like callbacks and comparators. Something that does both is invariant."),
        ("Where is TypeScript's type system unsound on purpose?",
         "Arrays and mutable properties are covariant, so you can pass `Dog[]` as `Animal[]` and push a cat into it; method-syntax parameters are checked bivariantly; and `any` and type assertions opt out entirely. The fixes are `readonly` for data you only read and property syntax for callback members."),
        ("What are `in` and `out` on a type parameter?",
         "Variance annotations, added in TS 4.7: `out T` means `T` is only produced, `in T` only consumed, `in out T` both. The compiler verifies them against the type's body, they make intent explicit, and they can speed up checking of large generic types. They don't change what's sound."),
    ],
)


_chapter(
    "ts_parse_dont_validate", "TS: Type System",
    "Parse, Don't Validate",
    "Turn checks into types: smart constructors, `unique symbol` brands and shapes like non-empty tuples, so that an invalid value cannot be constructed and a valid one never needs checking again.",
    "A validator answers yes or no and throws the answer away: the next function receives the same `string` and has to trust — or recheck — that it was validated. A *parser* returns a new, more precise type (`Email`, `Port`, `NonEmpty`) that can only be produced by passing the check. Brands built on a module-private `unique symbol` make that type impossible to forge by accident, and the rest of the program simply asks for `Email` instead of `string`.",
    "In Java you'd write a small final class with a private constructor and a static `parse` factory — a real wrapper object at runtime. TypeScript gets the same guarantee with zero runtime cost: the brand is a type-only property on a plain `string` or `number`, erased before the program runs.",
    why=r"""
Here is how validation usually goes. A function checks that a string looks like
an email and returns `true`. The caller, satisfied, passes the *same string*
on — typed `string`, exactly like every unvalidated string in the program. Three
calls later, a function that needs an email has no way to know whether this one
was checked. So either it checks again (and there are now four copies of the
rule, slowly drifting apart) or it doesn't (and one day a path skips the check).

The phrase *parse, don't validate* names the fix. A parser does the same
checking but **returns a different type** — `Email` rather than `string` — and
it is the only way to obtain one. Functions that need a checked value ask for
`Email`; the compiler then proves, at every call site, that the check happened.
The knowledge you gained by checking is kept, in the type.
""",
    idea=r"""
**A smart constructor** is a function that is the single door into a type:

```ts
declare const EmailBrand: unique symbol;
export type Email = string & { readonly [EmailBrand]: true };

export function parseEmail(raw: string): Email | undefined {
  const s = raw.trim().toLowerCase();
  return /^[^@\s]+@[^@\s]+\.[a-z]+$/.test(s) ? (s as Email) : undefined;
}
```

- `declare const EmailBrand: unique symbol` creates a symbol *type* that exists
  only in this module. It is erased — `declare` emits nothing — so the brand
  costs nothing at runtime.
- `Email` is a `string` with an extra, type-only property keyed by that symbol.
  An ordinary string doesn't have it, so a plain `"x@y.z"` is not an `Email`.
- The one `as Email` lives inside the parser, right after the check. Code
  elsewhere can't name `EmailBrand` (when it isn't exported), so it can't write
  the brand type by hand — only `parseEmail` makes `Email`s.

**Parse at the boundary, then trust the types.** Input arrives as text at the
edges of a program: stdin, JSON, a form. Parse it there, once, into precise
types, and let everything inside take those types. A function that takes
`Email` never validates; a function that takes `string` never assumes.

**Normalise while you parse.** A parser can return the *canonical* form —
trimmed, lower-cased, integer cents — so that equal things are equal.

**Shapes can carry facts too.** Not every precise type needs a brand:

- `readonly [T, ...T[]]` is a non-empty list; its first element is never
  `undefined`.
- A discriminated union can make an impossible combination unrepresentable
  (week 12).
- A `Result` instead of `undefined` can say *why* parsing failed (week 25).

**The cost** is the boundary code: a parser per precise type, and a moment's
thought about which functions should take `Email` and which `string`. The pay-off
is that the question "was this checked?" disappears from the rest of the code.
""",
    examples=[
        ("An `Email` only a parser can make",
         r"""
declare const EmailBrand: unique symbol;
type Email = string & { readonly [EmailBrand]: true };

function parseEmail(raw: string): Email | undefined {
  const s = raw.trim().toLowerCase();
  return /^[^@\s]+@[^@\s]+\.[a-z]+$/.test(s) ? (s as Email) : undefined;
}

function sendWelcome(to: Email): string {
  return "welcome mail -> " + to;
}

for (const raw of ["  Ana@Example.COM ", "bob", "cy@x.io"]) {
  const email = parseEmail(raw);
  console.log(email === undefined ? `rejected "${raw.trim()}"` : sendWelcome(email));
}
""", [""],
         "`sendWelcome` cannot be called with a raw string, so there is no way to forget the check. And the parser normalised the address on the way in: `ana@example.com`."),
        ("A list that cannot be empty",
         r"""
type NonEmpty = readonly [number, ...number[]];

function parseNonEmpty(xs: readonly number[]): NonEmpty | undefined {
  const [head, ...rest] = xs;
  return head === undefined ? undefined : [head, ...rest];
}

function range(xs: NonEmpty): string {
  let lo = xs[0];
  let hi = xs[0];
  for (const x of xs) {
    lo = Math.min(lo, x);
    hi = Math.max(hi, x);
  }
  return `${lo}..${hi}`;
}

for (const xs of [[4, 9, 1], [], [7]]) {
  const checked = parseNonEmpty(xs);
  console.log(checked === undefined ? "no values" : range(checked));
}
""", [""],
         "Inside `range`, `xs[0]` is a `number` — never `undefined`, even under `noUncheckedIndexedAccess` — because the tuple type says a first element exists. The check happened once, in the parser, and became a shape."),
        ("Parse at the edge, trust inside",
         r"""
declare const CentsBrand: unique symbol;
type Cents = number & { readonly [CentsBrand]: true };
type Order = { sku: string; qty: number; price: Cents };

function parseCents(text: string): Cents | undefined {
  const m = /^(\d+)(?:\.(\d{2}))?$/.exec(text);
  if (m === null) return undefined;
  return (Number(m[1]) * 100 + Number(m[2] ?? "0")) as Cents;
}

function parseOrder(line: string): Order | string {
  const [sku = "", qty = "", price = ""] = line.split(",");
  const n = Number(qty);
  if (!/^[A-Z]{3}\d{2}$/.test(sku)) return `bad sku ${sku}`;
  if (!Number.isInteger(n) || n <= 0) return `bad qty ${qty}`;
  const cents = parseCents(price);
  return cents === undefined ? `bad price ${price}` : { sku, qty: n, price: cents };
}

function lineTotal(o: Order): Cents {
  return (o.qty * o.price) as Cents;
}

for (const line of ["ABC12,3,1.50", "XYZ99,1,20", "abc,1,1.00", "DEF10,2,1.5"]) {
  const o = parseOrder(line);
  console.log(typeof o === "string" ? o : `${o.sku}: ${(lineTotal(o) / 100).toFixed(2)}`);
}
""", [""],
         "Prices become integer cents the moment they enter, so `lineTotal` never sees `\"1.50\"` or floating-point dollars. Everything after `parseOrder` works with `Order`s, not strings."),
    ],
    errors=[
        (2345, r"""
declare const EmailBrand: unique symbol;
type Email = string & { readonly [EmailBrand]: true };
function sendWelcome(to: Email): string {
  return "welcome " + to;
}
sendWelcome("ana@example.com");
""", "A string literal is a `string`, not an `Email`: it hasn't been through the parser. This error is the whole design working — the only way to get an `Email` is `parseEmail`."),
        (2322, r"""
type NonEmpty = readonly [number, ...number[]];
const none: NonEmpty = [];
""", "`[]` has no first element, and `NonEmpty` requires one. An empty list is not constructible as this type."),
    ],
    pitfalls=[
        ("Validate, then forget",
         r"""
function isEmail(s: string): boolean {
  return /^[^@\s]+@[^@\s]+$/.test(s);
}
function sendWelcome(to: string): string {
  return "welcome mail -> " + to;
}
const signups = ["ana@x.io", "bob"];
const first = signups[0] ?? "";
if (isEmail(first)) console.log(sendWelcome(first));
console.log(sendWelcome(signups[1] ?? "")); // this path forgot to check
""",
         r"""
declare const EmailBrand: unique symbol;
type Email = string & { readonly [EmailBrand]: true };
function parseEmail(s: string): Email | undefined {
  return /^[^@\s]+@[^@\s]+$/.test(s) ? (s as Email) : undefined;
}
function sendWelcome(to: Email): string {
  return "welcome mail -> " + to;
}
for (const raw of ["ana@x.io", "bob"]) {
  const email = parseEmail(raw);
  console.log(email === undefined ? "rejected " + raw : sendWelcome(email));
}
""",
         "The boolean validator knew `\"bob\"` was bad, and threw that knowledge away. When `sendWelcome` demands an `Email`, the path that forgot to check doesn't compile."),
        ("A brand forged with `as`",
         r"""
declare const EmailBrand: unique symbol;
type Email = string & { readonly [EmailBrand]: true };
function sendWelcome(to: Email): string {
  return "welcome mail -> " + to;
}
const quick = "not an email" as Email;
console.log(sendWelcome(quick));
""",
         r"""
declare const EmailBrand: unique symbol;
type Email = string & { readonly [EmailBrand]: true };
function parseEmail(s: string): Email | undefined {
  return /^[^@\s]+@[^@\s]+$/.test(s) ? (s as Email) : undefined;
}
function sendWelcome(to: Email): string {
  return "welcome mail -> " + to;
}
const quick = parseEmail("not an email");
console.log(quick === undefined ? "rejected" : sendWelcome(quick));
""",
         "A brand is only as strong as the rule that nobody casts to it outside the parser. `as Email` elsewhere is a lie the compiler can't catch — keep the one cast in the smart constructor and review any other."),
        ("Checking without normalising",
         r"""
const seen = new Set<string>();
for (const raw of ["Ana@X.io", " ana@x.io", "ANA@X.IO "]) {
  if (/^\s*[^@\s]+@[^@\s]+\s*$/.test(raw)) seen.add(raw);
}
console.log("distinct users: " + seen.size);
""",
         r"""
const seen = new Set<string>();
for (const raw of ["Ana@X.io", " ana@x.io", "ANA@X.IO "]) {
  const email = raw.trim().toLowerCase();
  if (/^[^@\s]+@[^@\s]+$/.test(email)) seen.add(email);
}
console.log("distinct users: " + seen.size);
""",
         "A validator that accepts all three spellings but keeps them as typed creates three users. A parser returns the canonical form, so equal emails are equal strings."),
    ],
    later=[
        "**Week 17 — Runtime validation.** Parsing whole objects from JSON with a schema that also produces the type.",
        "**Week 25 — Errors and `Result`.** A parser that says *why* it failed, instead of `undefined`.",
        "**Week 23 — Classes.** A private constructor and a static `parse` is the class-shaped smart constructor.",
    ],
    exercises=[
        _drill("ts_parse_dont_validate-port", "A port only a parser can make",
               "`Port` is a branded number. Replace `____` with the condition under which `text` is a valid port: all digits, and between 1 and 65535.",
               r"""
import * as fs from "fs";
declare const PortBrand: unique symbol;
type Port = number & { readonly [PortBrand]: true };
function parsePort(text: string): Port | undefined {
  const n = Number(text);
  return /^\d+$/.test(text) && n >= 1 && n <= 65535 ? (n as Port) : undefined;
}
function listen(port: Port): string {
  return `listening on ${port}`;
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const port = parsePort(line.trim());
  console.log(port === undefined ? `bad port ${line.trim()}` : listen(port));
}
""", ["/^\\d+$/.test(text) && n >= 1 && n <= 65535"],
               ["8080\n0\n65536\n443", "80.5\n-1\n1", "abc"],
               hint="Check the characters first — `Number(\"1e3\")` is 1000 — then the range."),
        _drill("ts_parse_dont_validate-nonempty", "Parse into a non-empty tuple",
               "Replace `____` so `parseNonEmpty` returns a `NonEmpty` when the list has at least one value (and `undefined` otherwise). `average` can then read `xs[0]` without a check.",
               r"""
import * as fs from "fs";
type NonEmpty = readonly [number, ...number[]];
function parseNonEmpty(xs: readonly number[]): NonEmpty | undefined {
  const [head, ...rest] = xs;
  return head === undefined ? undefined : [head, ...rest];
}
function summary(xs: NonEmpty): string {
  const avg = xs.reduce((a, b) => a + b, 0) / xs.length;
  return `first ${xs[0]}, average ${avg.toFixed(1)}`;
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const values = line.trim() === "-" ? [] : line.trim().split(/\s+/).map(Number);
  const checked = parseNonEmpty(values);
  console.log(checked === undefined ? "empty" : summary(checked));
}
""", ["head === undefined ? undefined : [head, ...rest]"],
               ["3 4 5\n-\n10", "7 7"],
               hint="Destructure the head; if it exists, rebuild the tuple as `[head, ...rest]`."),
        _chal("ts_parse_dont_validate-usernames", "Register usernames", "Medium",
              "Each input line is a requested username. Parse it into a branded `Username`: trim and lower-case it; it must be 3-12 characters of `a-z`, `0-9` and `_`, starting with a letter. Print `registered <name>`, `taken <name>` (already registered, compared after normalising), or `rejected \"<trimmed input>\": <reason>` with reason `length` or `characters` (length is checked first). Finish with `<k> users`.",
              r"""
declare const UsernameBrand: unique symbol;
type Username = string & { readonly [UsernameBrand]: true };
function parseUsername(raw: string): Username | "length" | "characters" {
  const s = raw.trim().toLowerCase();
  if (s.length < 3 || s.length > 12) return "length";
  if (!/^[a-z][a-z0-9_]*$/.test(s)) return "characters";
  return s as Username;
}
const users = new Set<Username>();
for (const line of input.split("\n")) {
  const result = parseUsername(line);
  if (result === "length" || result === "characters") {
    console.log(`rejected "${line.trim()}": ${result}`);
  } else if (users.has(result)) {
    console.log(`taken ${result}`);
  } else {
    users.add(result);
    console.log(`registered ${result}`);
  }
}
console.log(`${users.size} users`);
""", ["Ana_1\nana_1\nbo\n9lives\nsuper_long_name_x\nCy", "  Dee  \ndee\nd-e-e"],
              hint="Return either the branded name or the reason it failed; narrow on the two reason strings."),
    ],
    quiz=[
        _cq("What is the difference between a validator and a parser?",
            "A parser returns a more precise type that records the check; a validator returns a boolean",
            ["A parser is faster", "A validator throws, a parser doesn't", "There is none"],
            "The parser's return type carries the knowledge forward, so nothing downstream has to recheck."),
        _cq("What does `declare const Brand: unique symbol` emit at runtime?",
            "Nothing — `declare` is erased",
            ["A new Symbol()", "A frozen object", "A class"],
            "It only creates a type-level unique symbol to key the brand property."),
        _cq("Where should the `as Email` cast appear?",
            "Once, inside the parser, right after the check",
            ["Wherever an email is needed", "In every test", "Nowhere — brands need no casts"],
            "Concentrating the cast in the smart constructor is what makes the brand trustworthy."),
        _cq("Why is `readonly [number, ...number[]]` useful?",
            "Its first element is never `undefined`, so code taking it needs no emptiness check",
            ["It is faster than an array", "It can't be iterated", "It prevents duplicates"],
            "The non-emptiness is proven once, at construction, and carried in the type."),
        _cq("A parser trims and lower-cases emails. Why?",
            "So equal addresses become equal strings — normalising is part of parsing",
            ["Regexes can't match capitals", "The brand requires it", "It's faster to compare"],
            "Returning the canonical form removes a whole class of duplicate bugs."),
        _cq("Where in a program should parsing happen?",
            "At the boundary, where untyped input enters — once",
            ["In every function that uses the value", "Only in tests", "Just before printing"],
            "Inside the boundary, the precise types carry the guarantee."),
    ],
    interview=[
        ("What does \"parse, don't validate\" mean?",
         "Instead of checking data and returning a boolean — which loses the knowledge — you transform it into a more precise type that can only be produced by passing the check, like `Email` or a non-empty tuple. Downstream functions take the precise type, so the compiler proves the check happened and nobody re-validates."),
        ("How do you make a branded type that can't be forged?",
         "Intersect the base type with a property keyed by a module-private `unique symbol`: `declare const B: unique symbol; type Email = string & { readonly [B]: true }`. Only the module's smart constructor casts to it. It costs nothing at runtime. Code can still lie with `as`, so the rule is one cast, in the parser."),
        ("Brands or wrapper classes?",
         "Brands are free at runtime and the value is still a plain string or number, which serialises and compares naturally. A wrapper class gives you `instanceof` and a place for methods, at the cost of an allocation and conversions at every boundary. For IDs, units and validated strings I use brands."),
    ],
)


_M4_SCHEMA = r"""
type Parsed<T> = { ok: true; value: T } | { ok: false; issues: string[] };
type Schema<T> = { parse: (value: unknown, path: string) => Parsed<T> };
type Infer<S> = S extends Schema<infer T> ? T : never;

const fail = (path: string, expected: string): Parsed<never> => ({ ok: false, issues: [`${path}: expected ${expected}`] });
const str = (): Schema<string> => ({
  parse: (v, path) => (typeof v === "string" ? { ok: true, value: v } : fail(path, "string")),
});
const num = (): Schema<number> => ({
  parse: (v, path) => (typeof v === "number" && Number.isFinite(v) ? { ok: true, value: v } : fail(path, "number")),
});
function opt<T>(inner: Schema<T>): Schema<T | undefined> {
  return { parse: (v, path) => (v === undefined ? { ok: true, value: undefined } : inner.parse(v, path)) };
}
function arr<T>(item: Schema<T>): Schema<T[]> {
  return {
    parse(v, path) {
      if (!Array.isArray(v)) return fail(path, "array");
      const out: T[] = [];
      const issues: string[] = [];
      v.forEach((x: unknown, i) => {
        const r = item.parse(x, `${path}[${i}]`);
        if (r.ok) out.push(r.value);
        else issues.push(...r.issues);
      });
      return issues.length > 0 ? { ok: false, issues } : { ok: true, value: out };
    },
  };
}
function obj<S extends Record<string, Schema<unknown>>>(shape: S): Schema<{ [K in keyof S]: Infer<S[K]> }> {
  return {
    parse(v, path) {
      if (typeof v !== "object" || v === null || Array.isArray(v)) return fail(path, "object");
      const record = v as Record<string, unknown>;
      const out: Record<string, unknown> = {};
      const issues: string[] = [];
      for (const [key, schema] of Object.entries(shape)) {
        const r = schema.parse(record[key], `${path}.${key}`);
        if (r.ok) out[key] = r.value;
        else issues.push(...r.issues);
      }
      return issues.length > 0 ? { ok: false, issues } : { ok: true, value: out as { [K in keyof S]: Infer<S[K]> } };
    },
  };
}
"""

_chapter(
    "ts_runtime_validation", "TS: Robustness",
    "Runtime Validation with Schemas",
    "A mini schema library — `str()`, `num()`, `arr()`, `obj({...})` — where each validator also carries a type, so `Infer<typeof schema>` gives you the TypeScript type and the check can never drift from it.",
    "Types are erased, so data from outside (JSON, stdin, a form) must be checked at runtime. Write the check and the type separately and they drift: the type says `age: number`, the validator forgot to check it. A schema is a value that knows how to check data *and* carries the type it proves; the type is derived from it (`type User = Infer<typeof User>`), so there is only one source of truth. This is how Zod, Valibot and ArkType work — and you can build the core in sixty lines.",
    "Java deserialisers (Jackson) validate against a class you already wrote, using reflection at runtime. TypeScript has no runtime types to reflect on, so the direction flips: you write the *validator* as a value and derive the static type from it.",
    why=r"""
Everything TypeScript knows is gone by the time the program runs. When
`JSON.parse` hands you something, its type is whatever you say it is — and
`JSON.parse(text) as User` is a promise nobody checked.

So you write a validator. And now you have two descriptions of a `User`: the
type, which the compiler reads, and the validator, which the runtime runs.
They start out the same. Then someone adds `email` to the type and forgets the
validator, or loosens the validator and forgets the type. The compiler can't
notice, because it can't read what the validator *means*.

The fix is to write the description **once**, as a value the runtime can run,
and have the compiler *compute* the type from it. That value is a schema.
""",
    idea=r"""
**A schema is an object with a `parse` method** that takes `unknown` and returns
either the value — now typed — or a list of issues:

```ts
type Parsed<T> = { ok: true; value: T } | { ok: false; issues: string[] };
type Schema<T> = { parse: (value: unknown, path: string) => Parsed<T> };
```

**Small schemas combine into big ones.** `str()` and `num()` check primitives;
`arr(item)` checks every element with `item`; `opt(inner)` also allows a missing
value; `obj({ name: str(), age: num() })` checks each property with its schema
and collects *every* issue, each with a path like `user.tags[2]`.

**The type comes out of the schema.**

```ts
const User = obj({ name: str(), age: num(), tags: arr(str()) });
type User = Infer<typeof User>;   // { name: string; age: number; tags: string[] }
```

`Infer` reads the `T` back out of a `Schema<T>`; `obj` builds its result type by
mapping over the shape's keys. You will write both of those type-level tools
yourself in weeks 20 and 21 — for now, notice what they buy: change the schema,
and the type changes with it. There is nothing to keep in sync.

**Use it at the boundary.**

```ts
const r = User.parse(JSON.parse(text), "user");
if (r.ok) greet(r.value);            // r.value: User
else console.log(r.issues.join("\n"));
```

Everything after the `if` works with a real `User`; nothing inside the program
needs to check again. That is parse-don't-validate (week 16) for whole objects.

**Real libraries** — Zod, Valibot, ArkType — add unions, refinements
(`.min(3)`), transforms and good error messages, but the core is exactly this.
""",
    examples=[
        ("A schema, and the type computed from it",
         _M4_SCHEMA + r"""
const User = obj({ name: str(), age: num(), tags: arr(str()) });
type User = Infer<typeof User>;

function greet(u: User): string {
  return `${u.name} (${u.age}) ${u.tags.join("/") || "no tags"}`;
}

for (const text of ['{"name":"ana","age":31,"tags":["admin","ops"]}', '{"name":"bo","age":40,"tags":[]}']) {
  const r = User.parse(JSON.parse(text), "user");
  console.log(r.ok ? greet(r.value) : r.issues.join("; "));
}
""", [""],
         "`greet` is written against `User`, a type nobody wrote by hand. Add a field to the schema and `User` gains it; the compiler then points at every place that should use it."),
        ("Every issue, with a path",
         _M4_SCHEMA + r"""
const Order = obj({
  id: num(),
  customer: obj({ name: str(), email: opt(str()) }),
  items: arr(obj({ sku: str(), qty: num() })),
});

const inputs = [
  '{"id":7,"customer":{"name":"ana"},"items":[{"sku":"A1","qty":2}]}',
  '{"id":"7","customer":{"email":3},"items":[{"sku":"A1","qty":"2"},{"qty":1}]}',
  '[1,2]',
];
for (const text of inputs) {
  const r = Order.parse(JSON.parse(text), "order");
  if (r.ok) {
    const units = r.value.items.reduce((n, item) => n + item.qty, 0);
    console.log(`order ${r.value.id} for ${r.value.customer.name}: ${units} units`);
  } else {
    console.log(r.issues.join("\n"));
  }
}
""", [""],
         "The second input is wrong in five places, and all five are reported at once, each with the exact path — which is what whoever sent the data needs to fix it in one go."),
        ("Parse once, then trust",
         _M4_SCHEMA + r"""
const Config = obj({ host: str(), port: opt(num()), retries: opt(num()) });
type Config = Infer<typeof Config>;

function describe(c: Config): string {
  return `${c.host}:${c.port ?? 80}, ${c.retries ?? 3} retries`;
}

for (const text of ['{"host":"db.local","port":5432}', '{"host":"api","retries":0}', '{"port":"80"}']) {
  const r = Config.parse(JSON.parse(text), "config");
  console.log(r.ok ? describe(r.value) : "invalid: " + r.issues.join(", "));
}
""", [""],
         "`describe` handles only the optional fields' defaults — never the question of whether `host` exists or `port` is secretly a string. Note `retries: 0` survives: `??` keeps real zeroes."),
    ],
    errors=[
        (2339, r"""
type Schema<T> = { parse: (value: unknown) => T | undefined };
type Infer<S> = S extends Schema<infer T> ? T : never;
declare function num(): Schema<number>;
declare function obj<S extends Record<string, Schema<unknown>>>(shape: S): Schema<{ [K in keyof S]: Infer<S[K]> }>;

const Point = obj({ x: num(), y: num() });
type Point = Infer<typeof Point>;
function depth(p: Point): number {
  return p.z;
}
""", "The type came from the schema, and the schema has no `z`. To use a field you must first put it in the schema — which is exactly what keeps the check and the type in step."),
        (2322, r"""
type Schema<T> = { parse: (value: unknown) => T | undefined };
type Infer<S> = S extends Schema<infer T> ? T : never;
declare function str(): Schema<string>;
declare function num(): Schema<number>;
declare function obj<S extends Record<string, Schema<unknown>>>(shape: S): Schema<{ [K in keyof S]: Infer<S[K]> }>;

const Product = obj({ name: str(), price: num() });
type Product = Infer<typeof Product>;
function label(p: Product): string {
  return p.price;
}
""", "The schema says `price` is checked as a number, so the derived type says so too. The compiler knows exactly what the validator guarantees."),
    ],
    pitfalls=[
        ("`JSON.parse(...) as User`",
         r"""
type User = { name: string; age: number };
const user = JSON.parse('{"name":"ana","age":"31"}') as User;
console.log(`${user.name} turns ${user.age + 1}`);
""",
         r"""
type User = { name: string; age: number };
function parseUser(value: unknown): User | undefined {
  if (typeof value !== "object" || value === null) return undefined;
  if (!("name" in value) || typeof value.name !== "string") return undefined;
  if (!("age" in value) || typeof value.age !== "number") return undefined;
  return { name: value.name, age: value.age };
}
const user = parseUser(JSON.parse('{"name":"ana","age":"31"}'));
console.log(user === undefined ? "invalid user" : `${user.name} turns ${user.age + 1}`);
""",
         "The assertion believed the JSON, and `\"31\" + 1` is `\"311\"`. Any real check — hand-written here, or a schema — refuses the string."),
        ("A type and a validator that drifted",
         r"""
type User = { name: string; age: number };
function isUser(v: unknown): v is User {
  return typeof v === "object" && v !== null && "name" in v && typeof v.name === "string";
}
const data: unknown = JSON.parse('{"name":"bo"}');
if (isUser(data)) console.log(`${data.name} is ${data.age} years old`);
else console.log("invalid");
""",
         r"""
type User = { name: string; age: number };
function isUser(v: unknown): v is User {
  return typeof v === "object" && v !== null && "name" in v && typeof v.name === "string"
    && "age" in v && typeof v.age === "number";
}
const data: unknown = JSON.parse('{"name":"bo"}');
if (isUser(data)) console.log(`${data.name} is ${data.age} years old`);
else console.log("invalid");
""",
         "`age` was added to the type and never to the predicate, so the predicate lied: the compiler believes `data.age` is a `number`, and it prints `undefined`. A schema-derived type can't drift, because there is only one description."),
        ("Stopping at the first problem",
         r"""
function check(v: { name?: unknown; age?: unknown; email?: unknown }): string {
  if (typeof v.name !== "string") return "name: expected string";
  if (typeof v.age !== "number") return "age: expected number";
  if (typeof v.email !== "string") return "email: expected string";
  return "ok";
}
console.log(check({ name: 1, age: "x" }));
""",
         r"""
function check(v: { name?: unknown; age?: unknown; email?: unknown }): string {
  const issues: string[] = [];
  if (typeof v.name !== "string") issues.push("name: expected string");
  if (typeof v.age !== "number") issues.push("age: expected number");
  if (typeof v.email !== "string") issues.push("email: expected string");
  return issues.length === 0 ? "ok" : issues.join("\n");
}
console.log(check({ name: 1, age: "x" }));
""",
         "Reporting one problem at a time turns fixing bad data into a slow loop: fix, resubmit, get the next error. Collect them all."),
    ],
    later=[
        "**Week 20 — Mapped types.** You write the `{ [K in keyof S]: … }` that `obj` returns.",
        "**Week 21 — Conditional types and `infer`.** You write `Infer<S>` yourself.",
        "**Week 25 — `Result`.** `Parsed<T>` is a `Result` — the same shape, generalised.",
    ],
    exercises=[
        _drill("ts_runtime_validation-num", "The number schema",
               "The schema library is written for you except one condition. Replace `____` so `num()` accepts only finite numbers, then run the orders through it.",
               _M4_SCHEMA + r"""
import * as fs from "fs";
const Line = obj({ sku: str(), qty: num() });
for (const text of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const r = Line.parse(JSON.parse(text), "line");
  console.log(r.ok ? `${r.value.sku} x${r.value.qty}` : r.issues.join("; "));
}
""", ['typeof v === "number" && Number.isFinite(v)'],
               ['{"sku":"A","qty":2}\n{"sku":"B","qty":"2"}', '{"qty":1}\n{"sku":"C","qty":0}', '{"sku":"D","qty":null}'],
               hint="Two conditions: the right `typeof`, and not `NaN`/`Infinity` (JSON can't produce those, but other sources can)."),
        _drill("ts_runtime_validation-product", "Describe a product",
               "Replace `____` with the schema for a product: a `name` string, a `price` number and a `tags` array of strings. The `Product` type — and everything that uses it — follows from it.",
               _M4_SCHEMA + r"""
import * as fs from "fs";
const Product = obj({ name: str(), price: num(), tags: arr(str()) });
type Product = Infer<typeof Product>;
const label = (p: Product): string => `${p.name} $${p.price.toFixed(2)} [${p.tags.join(",")}]`;
for (const text of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const r = Product.parse(JSON.parse(text), "product");
  console.log(r.ok ? label(r.value) : r.issues.join("; "));
}
""", ["obj({ name: str(), price: num(), tags: arr(str()) })"],
               ['{"name":"pen","price":1.5,"tags":["office"]}\n{"name":"cup","price":"3","tags":[1]}', '{"name":"ink","price":2,"tags":[]}'],
               hint="`obj({ … })` with one schema per property; `arr(str())` for a list of strings."),
        _chal("ts_runtime_validation-events", "Validate an event feed", "Hard",
              "Each input line is JSON for an event: `id` (number), `type` (string), `tags` (array of strings) and optionally `user` (an object with a string `name`). Validate from `unknown` and report every issue with its path, like the schema library does: `event.id: expected number`, `event.tags[1]: expected string`, `event.user.name: expected string`, or `event: expected object`. Print `ok <id> <type>` (plus ` by <name>` when there is a user) or the issues joined by `; `, then `valid <k> of <n>`.",
              r"""
type Event = { id: number; type: string; tags: string[]; user?: { name: string } };
function validate(v: unknown): Event | string[] {
  if (typeof v !== "object" || v === null || Array.isArray(v)) return ["event: expected object"];
  const rec = v as Record<string, unknown>;
  const issues: string[] = [];
  const id = rec["id"];
  const type = rec["type"];
  const tags = rec["tags"];
  const user = rec["user"];
  if (typeof id !== "number") issues.push("event.id: expected number");
  if (typeof type !== "string") issues.push("event.type: expected string");
  const tagList: string[] = [];
  if (!Array.isArray(tags)) issues.push("event.tags: expected array");
  else tags.forEach((t: unknown, i) => (typeof t === "string" ? tagList.push(t) : issues.push(`event.tags[${i}]: expected string`)));
  let who: { name: string } | undefined;
  if (user !== undefined) {
    if (typeof user !== "object" || user === null) issues.push("event.user: expected object");
    else {
      const name = (user as Record<string, unknown>)["name"];
      if (typeof name !== "string") issues.push("event.user.name: expected string");
      else who = { name };
    }
  }
  if (issues.length > 0 || typeof id !== "number" || typeof type !== "string") return issues;
  return who === undefined ? { id, type, tags: tagList } : { id, type, tags: tagList, user: who };
}
const lines = input.split("\n");
let valid = 0;
for (const line of lines) {
  const r = validate(JSON.parse(line));
  if (Array.isArray(r)) {
    console.log(r.join("; "));
  } else {
    valid++;
    console.log(`ok ${r.id} ${r.type}${r.user === undefined ? "" : ` by ${r.user.name}`}`);
  }
}
console.log(`valid ${valid} of ${lines.length}`);
""", ['{"id":1,"type":"login","tags":["web"],"user":{"name":"ana"}}\n{"id":"2","type":5,"tags":["a",3]}\n{"id":3,"type":"ping","tags":[]}',
      '[]\n{"id":4,"type":"x","tags":"a","user":{"name":7}}\n{"id":5,"type":"y","tags":[],"user":null}'],
              hint="Collect issues in an array instead of returning at the first one; return either the typed event or the issue list."),
    ],
    quiz=[
        _cq("Why derive the type from the schema rather than write both?",
            "Two descriptions drift apart; one description can't",
            ["Schemas are faster than types", "Types can't describe JSON", "The compiler requires it"],
            "The validator is the source of truth, and `Infer` computes the type from it."),
        _cq("What does `Infer<typeof User>` give you when `User = obj({ name: str() })`?",
            "`{ name: string }`",
            ["`Schema<{ name: string }>`", "`typeof User`", "`unknown`"],
            "`Infer` extracts the `T` from a `Schema<T>`."),
        _cq("`const user = JSON.parse(text) as User` — what has been checked?",
            "Nothing; the assertion is a promise, erased at runtime",
            ["The top-level keys", "Everything", "Only the types of the values"],
            "Assertions never check. A schema does."),
        _cq("Why should a validator collect every issue instead of stopping at the first?",
            "So whoever sent bad data can fix all of it in one pass",
            ["It is faster", "Stopping early leaks memory", "The type system requires it"],
            "One error at a time makes fixing data a slow loop."),
        _cq("Where should `User.parse` be called?",
            "At the boundary where the data enters the program",
            ["In every function that uses a user", "Only in tests", "Before every print"],
            "Parse once; inside the boundary the type carries the guarantee."),
        _cq("Which existing libraries work this way?",
            "Zod, Valibot and ArkType",
            ["Jest and Vitest", "Express and Fastify", "Prettier and ESLint"],
            "They are schema libraries whose validators also produce static types."),
    ],
    interview=[
        ("How do you validate an API response in TypeScript?",
         "Treat it as `unknown` and run it through a schema — Zod or similar — at the boundary. The schema checks the runtime shape and its inferred type (`z.infer<typeof Schema>`) is what the rest of the code uses, so the check and the type can't disagree. I avoid `as SomeType` on parsed JSON; it checks nothing."),
        ("How does a library like Zod infer the type from a schema?",
         "Each schema is a value typed with a phantom parameter — `ZodType<Output>` — and combinators build bigger types from smaller ones: an object schema maps over its shape's keys with a mapped type, and `z.infer` pulls the output type out with a conditional type and `infer`. The runtime part and the type part are built by the same function calls."),
        ("Why not just generate validators from TypeScript types?",
         "Because types are erased: nothing about them exists at runtime to generate from, without a separate build step (a compiler plugin or codegen). Going the other way — types from runtime schemas — needs no tooling, which is why most of the ecosystem does that."),
    ],
)
