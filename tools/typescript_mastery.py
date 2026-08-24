# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript mastery track — the advanced half of the syllabus.
#
# The foundational TypeScript track (typescript_defs.py + typescript_expand.py)
# stops at "can write correct TypeScript". The 6-Month Mastery programme needs
# the rest of what makes someone genuinely fluent: user-defined type guards,
# discriminated unions, structural typing, `satisfies`, branded types, generic
# constraints, keyof/indexed access, mapped and conditional types, template
# literal types, recursive type-level programming, iterators and generators,
# typed error handling, promise combinators, declaration files and generic data
# structures.
#
# This file is exec()'d inside gen_seed.py's namespace AFTER typescript_defs.py
# (so it reuses tsx / tsc / _P / _FS) and extends CONCEPTS / CATEGORY / LESSONS
# / EXERCISES in place.
#
# EXECUTION MODEL — same as the foundational track. Programs run through
# `node --experimental-strip-types`, so:
#   * Types are ERASED before running. A graded blank must always target a
#     RUNTIME expression whose result reaches stdout — never a bare annotation.
#     Purely type-level material (mapped/conditional/template-literal types) is
#     therefore taught in the lesson and assessed by the concept's QUIZ, while
#     the drill exercises the runtime code those types describe.
#   * `enum`, decorators, namespaces and constructor parameter-properties are
#     NOT supported by type-stripping. `satisfies`, `unique symbol` brands,
#     `asserts x is T`, generics, generators and `#private` fields all are
#     (verified against the real runner before authoring).
# Every `solution` here is proven end-to-end by tests/verify_exercises.rs.
# ---------------------------------------------------------------------------

# Read-all-of-stdin scaffold, matching typescript_expand.py's challenges.
_MS = 'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\n'


def _mchal(eid, title, diff, prompt, body, tests, hint=""):
    """A mastery challenge: the stdin scaffold plus a single `____` where the
    learner writes the whole solution."""
    body = body.strip("\n")
    return tsc(eid, title, diff, prompt, _P(_MS + body), body, tests, hint)


TSM_CONCEPTS = {}
TSM_LESSONS = {}
TSM_EXERCISES = {}
TSM_CATEGORY = {}


def _concept(key, category, name, what, deep, note, lesson, exercises, quiz=None):
    """Register one mastery concept with its category, lesson and exercises."""
    TSM_CONCEPTS[key] = {
        "name": name,
        "what": what,
        "deep": deep,
        "java": note,
        "language": "typescript",
        "quiz": quiz or [],
    }
    TSM_CATEGORY[key] = category
    TSM_LESSONS[key] = lesson.strip("\n")
    TSM_EXERCISES[key] = exercises


# ===========================================================================
# TS: Functions & Types — higher-order functions
# ===========================================================================

_concept(
    "ts_higher_order", "TS: Functions & Types",
    "Higher-Order Functions & Currying",
    "Functions that take or return other functions, and the types that describe them.",
    "A higher-order function treats a function as data — it accepts one as an argument (`sort(comparator)`), returns one (`multiplyBy(2)`), or both. The type of a function is written `(a: number, b: number) => number`, and that signature is what makes composition safe: TypeScript checks that the function you pass matches the shape the caller expects.",
    "`(x: number) => string` is TypeScript's version of a `Function<Integer, String>`. Because functions are ordinary values there is no separate functional-interface concept — any matching signature fits, and a closure captures surrounding variables without a `final` requirement.",
    """
### A function type is just a signature
```ts
type Transform = (x: number) => number;
const double: Transform = (x) => x * 2;
```
The parameter type of `x` is *inferred* from `Transform` — this is contextual typing, and it is why callbacks rarely need annotations.

### Taking a function
```ts
function applyTwice(f: (x: number) => number, start: number): number {
  return f(f(start));
}
applyTwice(double, 3);   // 12
```

### Returning a function (currying)
```ts
const multiplyBy = (factor: number) => (x: number) => x * factor;
const triple = multiplyBy(3);
triple(5);   // 15
```
`multiplyBy` has type `(factor: number) => (x: number) => number`. The inner
arrow *closes over* `factor` — that captured variable lives as long as the
returned function does.

### Composing a pipeline
```ts
function pipe<T>(...fns: Array<(x: T) => T>): (start: T) => T {
  return (start) => fns.reduce((acc, f) => f(acc), start);
}
const shout = pipe<string>((s) => s.trim(), (s) => s.toUpperCase());
shout("  hi  ");   // "HI"
```

### Watch out for
- A callback may be given FEWER parameters than the signature offers, never
  more — `["a","b"].map((s) => s)` is fine even though `map` passes three args.
- `this` inside a non-arrow callback is not the enclosing object. Arrow
  functions inherit `this`, which is why they are the default for callbacks.
""",
    [
        tsx("ts_higher_order-comparator", "Sort with a comparator",
            "Replace `____` with a comparator constant named `byDescending` that `sort` can use to order numbers largest-first. A comparator returns a negative number when `a` should come first, positive when `b` should.",
            _P('''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
const byDescending = (a: number, b: number) => b - a;
console.log([...nums].sort(byDescending).join(" "));
'''),
            ["const byDescending = (a: number, b: number) => b - a;"],
            [("3 1 2", "3 2 1"), ("5", "5"), ("-1 -5 0", "0 -1 -5"), ("2 2 1", "2 2 1")],
            hint="b - a is positive when b is bigger, which sorts b before a — that is descending order."),
        tsx("ts_higher_order-curry", "A function that returns a function",
            "Replace `____` with `multiplyBy`: it takes a `factor` and RETURNS a function that multiplies its own argument by that factor. The next lines call it both ways.",
            _P('''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
const multiplyBy = (factor: number) => (x: number) => x * factor;
const double = multiplyBy(2);
console.log(double(a));
console.log(multiplyBy(b)(a));
'''),
            ["const multiplyBy = (factor: number) => (x: number) => x * factor;"],
            [("3 4", "6\n12"), ("5 0", "10\n0"), ("-2 3", "-4\n-6")],
            hint="Two arrows in a row: (factor: number) => (x: number) => .... The inner arrow captures factor."),
        _mchal("ts_higher_order-challenge", "Scoreboard", "Easy",
               "The input is `n` on the first line then `n` lines of `name score`. Using only `map`, `filter`, `sort` and `reduce`, print the names scoring 50 or more — highest score first, ties broken alphabetically — one per line, then print the average of ALL scores rounded down.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const rows = lines.slice(1, n + 1).map((line) => {
  const [name, score] = line.trim().split(/\\s+/);
  return { name, score: Number(score) };
});
const passing = rows
  .filter((r) => r.score >= 50)
  .sort((a, b) => (b.score !== a.score ? b.score - a.score : a.name.localeCompare(b.name)));
for (const r of passing) console.log(r.name);
const total = rows.reduce((sum, r) => sum + r.score, 0);
console.log(Math.floor(total / rows.length));
''',
               [("3\nada 90\nbob 40\ncy 90", "ada\ncy\n73"),
                ("1\nsolo 10", "10"),
                ("2\nx 50\ny 49", "x\n49"),
                ("4\na 100\nb 100\nc 0\nd 0", "a\nb\n50")],
               hint="Parse each line into an object first; then the three stages are a filter, a sort with a two-level comparator, and a reduce."),
    ],
    quiz=[
        {
            "question": "What is the type of `const add = (a: number) => (b: number) => a + b;`?",
            "options": [
                "(a: number) => (b: number) => number",
                "(a: number, b: number) => number",
                "number",
                "(a: number) => number",
            ],
            "answer": 0,
            "explanation": "Calling `add(1)` hands back another function, so the return type is itself a function type. Only `add(1)(2)` produces a number.",
        },
        {
            "question": "Why does `['a','b'].map((s) => s.length)` type-check even though `map` passes three arguments to its callback?",
            "options": [
                "A function may ignore trailing parameters it does not declare",
                "map special-cases single-parameter callbacks",
                "The extra arguments are silently dropped at runtime only",
                "TypeScript infers the missing parameters as any",
            ],
            "answer": 0,
            "explanation": "Function assignability allows FEWER parameters than the target signature — the caller simply passes arguments the callback ignores. Declaring MORE than the signature offers is the error.",
        },
        {
            "question": "In `const shout = pipe<string>(f, g)`, what does `pipe` need to guarantee about `f` and `g`?",
            "options": [
                "Both must be (x: string) => string so the output of one feeds the next",
                "Both must return void",
                "f must return the argument type of g, which can differ from string",
                "Neither — pipe erases the types at runtime",
            ],
            "answer": 0,
            "explanation": "This `pipe` is typed as `Array<(x: T) => T>`, so every stage takes and returns the SAME T. A pipeline that changes types between stages needs overloads or a more elaborate generic.",
        },
    ],
)


# ===========================================================================
# TS: Type System
# ===========================================================================

_concept(
    "ts_type_predicates", "TS: Type System",
    "User-Defined Type Guards",
    "Teaching the compiler how to narrow with `x is T` predicates and `asserts x is T` functions.",
    "`typeof` and `instanceof` narrow the types TypeScript already knows how to test. For your own shapes you write a *type predicate*: a function returning `x is Person` whose `true` result tells the compiler to narrow. An *assertion function* returning `asserts x is Person` narrows for the rest of the enclosing scope instead, by throwing when the check fails. Both are promises YOU make — the compiler trusts the return type, so a wrong predicate silently lies about the whole program.",
    "A type predicate does the job of Java's `instanceof` pattern (`if (o instanceof Person p)`) for structural shapes that have no runtime class. An assertion function is the checked-exception cousin — like `Objects.requireNonNull`, but it also changes the static type afterwards.",
    """
### The problem
```ts
function handle(x: unknown) {
  x.toUpperCase();   // Error: 'x' is of type 'unknown'
}
```
`unknown` forces a check. `typeof x === "string"` works for primitives — but not for object shapes.

### A type predicate
```ts
type Person = { name: string; age: number };

function isPerson(x: unknown): x is Person {
  if (typeof x !== "object" || x === null) return false;
  const o = x as Record<string, unknown>;
  return typeof o.name === "string" && typeof o.age === "number";
}

const raw: unknown = JSON.parse(line);
if (isPerson(raw)) {
  raw.name.toUpperCase();   // narrowed to Person
}
```
The `: x is Person` return type is what does the narrowing — a plain `: boolean`
would type-check the function but narrow nothing at the call site.

### Predicates compose with array methods
```ts
const values: unknown[] = [1, "a", 2];
const numbers = values.filter((v): v is number => typeof v === "number");
// numbers: number[]  — not unknown[]
```

### Assertion functions
```ts
function assertLongEnough(x: unknown): asserts x is string {
  if (typeof x !== "string" || x.length < 3) throw new Error("too short");
}

assertLongEnough(token);
token.toUpperCase();   // narrowed for the REST of the scope
```
An assertion function must be called on a `const`-declared or explicitly-typed
binding — TypeScript refuses to apply it to an inferred `let` in some positions.

### Watch out for
- The compiler does **not** verify that the body matches the promise. `function
  isPerson(x: unknown): x is Person { return true; }` compiles and is a lie.
- Prefer narrowing every field you claim. A predicate that only checks
  `"name" in x` still asserts `age: number` exists.
""",
    [
        tsx("ts_type_predicates-isnumber", "Filter with a predicate",
            "The tokens arrive as `unknown[]` — numbers stayed numbers, everything else is a string. Replace `____` with an `isNumber` function whose RETURN TYPE is a type predicate, so `filter` gives back a `number[]` you can sum.",
            _P('''
import * as fs from "fs";
const raw: unknown[] = fs
  .readFileSync(0, "utf8")
  .trim()
  .split(/\\s+/)
  .map((t) => (isNaN(Number(t)) ? t : Number(t)));
function isNumber(x: unknown): x is number {
  return typeof x === "number";
}
const nums = raw.filter(isNumber);
console.log(nums.reduce((a, b) => a + b, 0));
'''),
            ['function isNumber(x: unknown): x is number {\n  return typeof x === "number";\n}'],
            [("1 a 2 b 3", "6"), ("x y", "0"), ("10 20", "30"), ("7", "7")],
            hint="The signature is `function isNumber(x: unknown): x is number` and the body is a single typeof check."),
        tsx("ts_type_predicates-assert", "An assertion function",
            "Replace `____` with `assertLongEnough`, an assertion function (`asserts x is string`) that throws unless the value is a string of at least 3 characters. The `try` block below relies on it to narrow before calling `.toUpperCase()`.",
            _P('''
import * as fs from "fs";
const token: unknown = fs.readFileSync(0, "utf8").trim();
function assertLongEnough(x: unknown): asserts x is string {
  if (typeof x !== "string" || x.length < 3) throw new Error("too short");
}
try {
  assertLongEnough(token);
  console.log(token.toUpperCase());
} catch {
  console.log("(invalid)");
}
'''),
            ['function assertLongEnough(x: unknown): asserts x is string {\n  if (typeof x !== "string" || x.length < 3) throw new Error("too short");\n}'],
            [("hello", "HELLO"), ("abc", "ABC"), ("hi", "(invalid)"), ("a", "(invalid)")],
            hint="An assertion function returns nothing — it either throws or falls through. Its return type is the words `asserts x is string`."),
        _mchal("ts_type_predicates-challenge", "Validate records", "Medium",
               "The input is `n` then `n` lines of JSON. A record is valid when it parses to an object with a `string` `name` and a `number` `age`. Write a type predicate `isPerson`, collect the valid ones, and print their names space-separated in alphabetical order (or `(none)`), then the number of rejected lines.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Person = { name: string; age: number };
function isPerson(x: unknown): x is Person {
  if (typeof x !== "object" || x === null) return false;
  const o = x as Record<string, unknown>;
  return typeof o.name === "string" && typeof o.age === "number";
}
const people: Person[] = [];
let rejects = 0;
for (let i = 1; i <= n; i++) {
  const parsed: unknown = JSON.parse(lines[i]);
  if (isPerson(parsed)) people.push(parsed);
  else rejects++;
}
const names = people.map((p) => p.name).sort();
console.log(names.length === 0 ? "(none)" : names.join(" "));
console.log(rejects);
''',
               [('3\n{"name":"ada","age":36}\n{"name":"bob"}\n{"name":"cy","age":9}', "ada cy\n1"),
                ('1\n{"age":5}', "(none)\n1"),
                ('2\n{"name":"z","age":1}\n{"name":"a","age":2}', "a z\n0"),
                ('2\n5\n"text"', "(none)\n2")],
               hint="Reject non-objects and null FIRST, then cast to Record<string, unknown> so you can probe each field with typeof."),
    ],
    quiz=[
        {
            "question": "What changes if you write `function isPerson(x: unknown): boolean` instead of `: x is Person`?",
            "options": [
                "The function still runs but no longer narrows x at the call site",
                "Nothing — the two are equivalent",
                "It becomes a compile error",
                "x is narrowed to any instead of Person",
            ],
            "answer": 0,
            "explanation": "Only the `x is T` return type carries narrowing information. With `: boolean` the compiler learns nothing from the `if`, so `x` stays `unknown` inside it.",
        },
        {
            "question": "`function isPerson(x: unknown): x is Person { return true; }` — what does TypeScript do?",
            "options": [
                "Accepts it; the compiler trusts the predicate without verifying the body",
                "Errors, because the body does not check any Person fields",
                "Warns under strict mode only",
                "Narrows to unknown instead, as a safety fallback",
            ],
            "answer": 0,
            "explanation": "A type predicate is an unchecked promise. This is exactly why a predicate should test every field it claims — a sloppy one puts a hole straight through the type system.",
        },
        {
            "question": "What distinguishes `asserts x is string` from `x is string`?",
            "options": [
                "The assertion narrows for the rest of the scope by throwing on failure, rather than returning a boolean to test",
                "The assertion works on primitives only",
                "The assertion is checked at runtime by TypeScript",
                "There is no difference other than spelling",
            ],
            "answer": 0,
            "explanation": "A predicate answers a question you branch on; an assertion function makes a demand — control only continues past the call when the value really is that type.",
        },
    ],
)

_concept(
    "ts_discriminated_unions", "TS: Type System",
    "Discriminated Unions & Exhaustiveness",
    "Modelling 'one of several shapes' with a shared literal tag, and proving you handled every case.",
    "A discriminated (tagged) union is a union whose members all carry the same property holding a distinct literal type — `kind: \"circle\"` vs `kind: \"rect\"`. Switching on that property narrows the whole object, so each branch sees exactly the fields that case has. Assigning the leftover value to `never` in the `default` branch turns 'you forgot a case' into a compile error, which is what makes adding a new variant safe.",
    "This is Java's sealed interface + record pattern-matching, done structurally. The tag replaces the runtime class, so it survives type erasure and JSON round-trips — a plain object from `JSON.parse` narrows just as well as one you constructed.",
    """
### Shape of the pattern
```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number };
```
Every member has `kind`, and each `kind` is a distinct *literal* type. That is
the discriminant.

### Switching narrows
```ts
function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r * s.r;   // s.r exists here
    case "rect":   return s.w * s.h;             // s.w / s.h exist here
  }
}
```
Inside `case "circle"` the compiler knows `s` is the circle member — reaching
for `s.w` there is an error, not a runtime `undefined`.

### Exhaustiveness with `never`
```ts
function describe(s: Shape): string {
  switch (s.kind) {
    case "circle": return "circle";
    case "rect":   return "rect";
    default: {
      const exhaustive: never = s;   // errors if a case is missing
      return exhaustive;
    }
  }
}
```
Once every case is handled, `s` in `default` has type `never` and the assignment
is fine. Add a third variant and the assignment breaks — the compiler points you
at every switch that needs updating.

### Why a plain union is not enough
```ts
type Loose = { r?: number; w?: number; h?: number };
```
Now every field is optional everywhere, and you are back to runtime `undefined`
checks. The tag is what lets one union member exclude the others.

### Watch out for
- The discriminant must be a *literal* type. `kind: string` discriminates
  nothing — use `as const` or an explicit annotation to keep it literal.
- `if (s.kind === "circle")` narrows exactly like `switch`; use whichever reads
  better. `else if` chains still need a final `never` check to stay exhaustive.
""",
    [
        tsx("ts_discriminated_unions-area", "Narrow with switch",
            "`Shape` is a tagged union. Replace `____` with the body of `area`: switch on `s.kind` and return the circle's area (`π r²`, rounded to 2 decimals with `Math.round(x * 100) / 100`) or the rectangle's `w * h`.",
            _P('''
import * as fs from "fs";
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number };
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.round(Math.PI * s.r * s.r * 100) / 100;
    case "rect":
      return s.w * s.h;
  }
}
const [kind, a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
const shape: Shape =
  kind === "circle"
    ? { kind: "circle", r: Number(a) }
    : { kind: "rect", w: Number(a), h: Number(b) };
console.log(area(shape));
'''),
            ['  switch (s.kind) {\n    case "circle":\n      return Math.round(Math.PI * s.r * s.r * 100) / 100;\n    case "rect":\n      return s.w * s.h;\n  }'],
            [("circle 2 0", "12.57"), ("rect 3 4", "12"),
             ("circle 1 0", "3.14"), ("rect 5 5", "25")],
            hint="switch (s.kind) with one case per tag. Inside each case the matching fields are available without any optional-chaining."),
        tsx("ts_discriminated_unions-never", "Prove it is exhaustive",
            "The switch handles all three events but has no safety net. Replace `____` with a `default` branch that assigns the leftover `e` to a `const exhaustive: never` and returns it — so adding a fourth event kind becomes a compile error.",
            _P('''
import * as fs from "fs";
type Event =
  | { type: "click"; x: number }
  | { type: "key"; code: string }
  | { type: "scroll"; dy: number };
function describe(e: Event): string {
  switch (e.type) {
    case "click":
      return "click at " + e.x;
    case "key":
      return "key " + e.code;
    case "scroll":
      return "scroll " + e.dy;
    default: {
      const exhaustive: never = e;
      return exhaustive;
    }
  }
}
const [t, v] = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
const e: Event =
  t === "click"
    ? { type: "click", x: Number(v) }
    : t === "key"
      ? { type: "key", code: v }
      : { type: "scroll", dy: Number(v) };
console.log(describe(e));
'''),
            ["    default: {\n      const exhaustive: never = e;\n      return exhaustive;\n    }"],
            [("click 5", "click at 5"), ("key Enter", "key Enter"),
             ("scroll -3", "scroll -3"), ("click -1", "click at -1")],
            hint="After every tag is handled, e has type never in the default branch — assigning it to a never-typed const is the whole trick."),
        _mchal("ts_discriminated_unions-challenge", "Command interpreter", "Medium",
               "The input is `n` then `n` commands, one per line: `add v`, `mul v`, or `reset`. Model the commands as a discriminated union, start an accumulator at 0, apply each command in order, and print the accumulator after every command (one per line). `reset` sets it back to 0.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Cmd =
  | { kind: "add"; value: number }
  | { kind: "mul"; value: number }
  | { kind: "reset" };
function parse(line: string): Cmd {
  const [op, arg] = line.trim().split(/\\s+/);
  if (op === "add") return { kind: "add", value: Number(arg) };
  if (op === "mul") return { kind: "mul", value: Number(arg) };
  return { kind: "reset" };
}
function apply(acc: number, c: Cmd): number {
  switch (c.kind) {
    case "add":
      return acc + c.value;
    case "mul":
      return acc * c.value;
    case "reset":
      return 0;
  }
}
let acc = 0;
const out: number[] = [];
for (let i = 1; i <= n; i++) {
  acc = apply(acc, parse(lines[i]));
  out.push(acc);
}
console.log(out.join("\\n"));
''',
               [("4\nadd 5\nmul 3\nadd 1\nreset", "5\n15\n16\n0"),
                ("1\nreset", "0"),
                ("3\nadd 2\nadd 3\nmul 4", "2\n5\n20"),
                ("2\nmul 10\nadd 7", "0\n7")],
               hint="Keep parsing and applying separate: parse turns a line into a Cmd, apply switches on Cmd.kind. Only `reset` has no value field."),
    ],
    quiz=[
        {
            "question": "Why must the discriminant be a literal type rather than `string`?",
            "options": [
                "Only distinct literal types let the compiler rule out the other union members",
                "String discriminants are slower at runtime",
                "TypeScript forbids string-typed properties in unions",
                "Literal types are required for JSON serialization",
            ],
            "answer": 0,
            "explanation": "Narrowing works by elimination: `kind === \\\"circle\\\"` can only exclude the rect member if that member's `kind` is the literal `\\\"rect\\\"`. With `kind: string` both members still match.",
        },
        {
            "question": "You add a `{ kind: \"triangle\"; b: number; h: number }` member. What does the `const exhaustive: never = s` line do?",
            "options": [
                "It becomes a compile error in every switch that has not handled the new kind",
                "It silently accepts the new member",
                "It throws at runtime when a triangle arrives",
                "It narrows the triangle to never so the switch keeps working",
            ],
            "answer": 0,
            "explanation": "That is the point of the pattern: `s` in `default` is now the triangle member, which is not assignable to `never`, so the compiler walks you to every place that needs a new case.",
        },
        {
            "question": "Which is the real advantage of a tagged union over one object with all fields optional?",
            "options": [
                "Each branch statically guarantees which fields exist, removing the undefined checks",
                "It uses less memory at runtime",
                "It allows more than one field to be required",
                "It survives JSON.stringify, which optional fields do not",
            ],
            "answer": 0,
            "explanation": "With all-optional fields every access needs a runtime guard and the compiler cannot tell a circle from a rect. The tag makes the impossible combinations unrepresentable.",
        },
    ],
)

_concept(
    "ts_structural_typing", "TS: Type System",
    "Structural Typing & Excess Properties",
    "Why TypeScript compares shapes, not names — and the one place it deliberately does not.",
    "TypeScript's type system is *structural*: a value is assignable to a type when it has at least the required members with compatible types. The name it was declared under is irrelevant, so two unrelated `type` aliases with the same fields are interchangeable. The single exception is the *excess property check*: a fresh object literal assigned straight to a typed target is rejected for having extra fields, because that almost always means a typo.",
    "This is the opposite of Java's nominal typing, where a class must explicitly `implements` an interface. Here a plain object satisfies an interface by accident-of-shape — great for adapters and test doubles, but it also means a typo'd field name in a widened variable slips through where Java would catch it.",
    """
### Shape is identity
```ts
type Point = { x: number; y: number };
type Coord = { x: number; y: number };

const p: Point = { x: 1, y: 2 };
const c: Coord = p;     // fine — same shape, no declaration needed
```
No `implements`, no inheritance. Structural compatibility is checked field by
field.

### Extra fields are usually fine
```ts
function samePlace(a: Point, b: Point): boolean {
  return a.x === b.x && a.y === b.y;
}

const labelled = { x: 1, y: 2, label: "home" };
samePlace(labelled, { x: 1, y: 2 });   // ok — labelled HAS x and y
```
`labelled` has more than `Point` requires, and more is allowed.

### …except for fresh object literals
```ts
const bad: Point = { x: 1, y: 2, label: "home" };
//                              ~~~~~ excess property error
```
Assigning a literal *directly* triggers the excess property check. Assign it to
a variable first and the check does not apply — the same object, now widened:
```ts
const tmp = { x: 1, y: 2, label: "home" };
const ok: Point = tmp;   // no error
```
This asymmetry is intentional: the literal form is where typos live.

### Structural constraints in generics
```ts
function longest<T extends { length: number }>(items: T[]): T {
  let best = items[0];
  for (const it of items) if (it.length > best.length) best = it;
  return best;
}
longest(["a", "bb"]);        // strings have .length
longest([[1], [1, 2, 3]]);   // so do arrays
```

### Watch out for
- Functions compare structurally too, and accept FEWER parameters than declared.
- Optional fields make shapes *wider*, not narrower: `{ x: number; y?: number }`
  is satisfied by `{ x: 1 }`.
- `private` class members DO make a class nominal-ish — two classes with
  identical private fields are not interchangeable.
""",
    [
        tsx("ts_structural_typing-duck", "Anything with a length",
            "`longest` is constrained to `T extends { length: number }`, so it works on strings AND arrays. Replace `____` with its body: track and return the item with the greatest `length`, keeping the first on a tie.",
            _P('''
import * as fs from "fs";
type HasLength = { length: number };
function longest<T extends HasLength>(items: T[]): T {
  let best = items[0];
  for (const item of items) {
    if (item.length > best.length) best = item;
  }
  return best;
}
const words = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
console.log(longest(words));
console.log(longest([[1, 2], [1], [1, 2, 3]]).length);
'''),
            ["  let best = items[0];\n  for (const item of items) {\n    if (item.length > best.length) best = item;\n  }\n  return best;"],
            [("a bb ccc", "ccc\n3"), ("hi", "hi\n3"),
             ("one two three", "three\n3"), ("aa bb", "aa\n3")],
            hint="Seed best with items[0] and only replace it on a strictly greater length, so ties keep the earlier item."),
        tsx("ts_structural_typing-extra", "Extra fields are allowed",
            "`p` carries an extra `label` field that `Point` never mentions — and passing it is still legal, because it is a variable rather than a fresh literal. Replace `____` with the body of `samePlace`: true when both coordinates match.",
            _P('''
import * as fs from "fs";
type Point = { x: number; y: number };
function samePlace(a: Point, b: Point): boolean {
  return a.x === b.x && a.y === b.y;
}
const [ax, ay, bx, by] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
const p = { x: ax, y: ay, label: "p" };
const q = { x: bx, y: by };
console.log(samePlace(p, q));
console.log(Object.keys(p).length);
'''),
            ["  return a.x === b.x && a.y === b.y;"],
            [("1 2 1 2", "true\n3"), ("1 2 3 4", "false\n3"),
             ("0 0 0 1", "false\n3"), ("-1 -1 -1 -1", "true\n3")],
            hint="Compare both fields with === and combine them with &&."),
        _mchal("ts_structural_typing-challenge", "Merge a config", "Medium",
               "A `Config` has `host`, `port` and `debug` (all strings) defaulting to `localhost`, `80`, `false`. The input is lines of `key=value`. Apply each line on top of the defaults — unknown keys are added too — then print every key as `key=value`, one per line in alphabetical key order, and finally how many of the THREE known keys were changed to a different value.",
               '''
const lines = input.split("\\n").filter((l) => l.trim().length > 0);
type Config = { host: string; port: string; debug: string };
const base: Config = { host: "localhost", port: "80", debug: "false" };
const merged: Record<string, string> = { ...base };
let overridden = 0;
for (const line of lines) {
  const idx = line.indexOf("=");
  const key = line.slice(0, idx).trim();
  const value = line.slice(idx + 1).trim();
  if (key in base && merged[key] !== value) overridden++;
  merged[key] = value;
}
for (const key of Object.keys(merged).sort()) {
  console.log(key + "=" + merged[key]);
}
console.log(overridden);
''',
               [("port=8080\ndebug=true", "debug=true\nhost=localhost\nport=8080\n2"),
                ("host=example.com", "debug=false\nhost=example.com\nport=80\n1"),
                ("port=80", "debug=false\nhost=localhost\nport=80\n0"),
                ("extra=1\nhost=h", "debug=false\nextra=1\nhost=h\nport=80\n1")],
               hint="Spread the defaults into a Record<string, string> so unknown keys are allowed, and count an override only when the key is one of the defaults AND the value actually differs."),
    ],
    quiz=[
        {
            "question": "`const bad: Point = { x: 1, y: 2, label: \"home\" };` errors, but assigning the same object through a variable does not. Why?",
            "options": [
                "The excess property check only applies to fresh object literals assigned directly",
                "Variables are always typed as any",
                "The variable version is also an error, just reported later",
                "label is a reserved property name",
            ],
            "answer": 0,
            "explanation": "TypeScript treats a directly-assigned literal as a place where extra keys are almost certainly typos, so it checks them. Once the object is widened into a variable, ordinary structural assignability applies.",
        },
        {
            "question": "Two unrelated aliases `type A = { id: number }` and `type B = { id: number }`. Is `const b: B = someA;` legal?",
            "options": [
                "Yes — structural typing compares shapes, not declaration names",
                "No — they are different named types",
                "Only if B extends A",
                "Only when both are interfaces rather than type aliases",
            ],
            "answer": 0,
            "explanation": "Nothing links A and B by name, but they have identical members, so each is assignable to the other. This is the core difference from Java's nominal `implements`.",
        },
        {
            "question": "What makes a class NOT purely structural in TypeScript?",
            "options": [
                "Having private or protected members, which only match members from the same declaration",
                "Having a constructor",
                "Implementing an interface",
                "Being declared abstract",
            ],
            "answer": 0,
            "explanation": "Private and protected members are tied to their declaring class, so two classes with identical-looking private fields are not interchangeable — the one nominal corner of the type system.",
        },
    ],
)

_concept(
    "ts_satisfies", "TS: Type System",
    "The satisfies Operator",
    "Checking a value against a type without widening it to that type.",
    "`const x: T = value` checks the value AND replaces its inferred type with `T`, throwing away the specific literal information. `value satisfies T` checks it and keeps the narrow inferred type. That difference matters whenever you want both guarantees at once: 'this table really does map every key to a string' and 'the keys are exactly home | about | help, not string'.",
    "There is no Java analogue — it exists because TypeScript infers very precise literal types that an annotation would discard. Think of it as a compile-time assertion that leaves the value's own type alone.",
    """
### The problem an annotation causes
```ts
const routes: Record<string, string> = {
  home: "/",
  about: "/about",
};
routes.hom;   // no error — the key type is now `string`
```
The annotation checked the shape but *widened* the type. Typos in key lookups
are no longer caught.

### Dropping the annotation loses the check
```ts
const routes = { home: "/", about: 404 };   // no error — nothing enforced
```

### `satisfies` gives you both
```ts
const routes = {
  home: "/",
  about: "/about",
} satisfies Record<string, string>;

routes.home;    // "/"  — inferred literal type kept
routes.hom;     // Error: property does not exist
```
Values are still checked against `Record<string, string>` — change `"/about"` to
`404` and it errors — but the inferred type stays the exact object shape.

### Deriving a key union
```ts
type RouteName = keyof typeof routes;   // "home" | "about"

function go(name: RouteName) {
  return routes[name];
}
```
This is the everyday payoff: one literal table drives both the runtime lookup
and the type of its own keys.

### With tuples
```ts
const palette = {
  primary: [0, 122, 255],
  danger: [255, 59, 48],
} satisfies Record<string, [number, number, number]>;
```
Each entry is verified to be a 3-tuple of numbers, and `palette.primary` stays a
tuple rather than collapsing to `number[]`.

### Watch out for
- `satisfies` is purely compile-time; it is erased and has no runtime cost or
  effect. It cannot validate data that arrives at runtime — that still needs a
  type guard.
- It does not widen, so it will NOT let you assign a narrower value where a
  wider annotation was doing useful work. Use an annotation when you genuinely
  want the wider type.
""",
    [
        tsx("ts_satisfies-lookup", "Look up a checked table",
            "`routes` is declared with `satisfies`, so its keys stay the literal union `\"home\" | \"about\" | \"help\"`. Replace `____` to print the path for the requested route, casting the input with `as keyof typeof routes`, and then the number of routes.",
            _P('''
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const routes = {
  home: "/",
  about: "/about",
  help: "/help",
} satisfies Record<string, string>;
console.log(routes[input as keyof typeof routes]);
console.log(Object.keys(routes).length);
'''),
            ["console.log(routes[input as keyof typeof routes]);\nconsole.log(Object.keys(routes).length);"],
            [("home", "/\n3"), ("about", "/about\n3"), ("help", "/help\n3")],
            hint="`keyof typeof routes` is the union of the object's own keys — the cast tells the compiler the raw string is one of them."),
        tsx("ts_satisfies-tuple", "Keep the tuple type",
            "Because `palette` uses `satisfies Record<string, [number, number, number]>`, each entry stays a 3-tuple instead of widening to `number[]`. Replace `____` to read the requested colour, print it comma-separated, and then print the sum of its three channels.",
            _P('''
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const palette = {
  primary: [0, 122, 255],
  danger: [255, 59, 48],
} satisfies Record<string, [number, number, number]>;
const rgb = palette[input as keyof typeof palette];
console.log(rgb.join(","));
console.log(rgb[0] + rgb[1] + rgb[2]);
'''),
            ["const rgb = palette[input as keyof typeof palette];\nconsole.log(rgb.join(\",\"));\nconsole.log(rgb[0] + rgb[1] + rgb[2]);"],
            [("primary", "0,122,255\n377"), ("danger", "255,59,48\n362")],
            hint="Index the palette with the cast key, then join the tuple and add its three entries."),
        _mchal("ts_satisfies-challenge", "Feature flags", "Easy",
               "Declare a `flags` object with `darkMode: true`, `beta: false`, `telemetry: true`, checked with `satisfies Record<string, boolean>`. The input is `n` then `n` flag names. Print each flag's value (`true`/`false`), or `unknown flag` if the name is not in the table, then print how many flags are enabled.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const flags = {
  darkMode: true,
  beta: false,
  telemetry: true,
} satisfies Record<string, boolean>;
type FlagName = keyof typeof flags;
function lookup(name: string): string {
  if (name in flags) return String(flags[name as FlagName]);
  return "unknown flag";
}
for (let i = 1; i <= n; i++) {
  console.log(lookup(lines[i].trim()));
}
console.log(Object.values(flags).filter(Boolean).length);
''',
               [("3\ndarkMode\nbeta\nnope", "true\nfalse\nunknown flag\n2"),
                ("1\ntelemetry", "true\n2"),
                ("2\nx\ny", "unknown flag\nunknown flag\n2"),
                ("1\nbeta", "false\n2")],
               hint="`name in flags` narrows at runtime; the `as FlagName` cast is what lets you index the table afterwards."),
    ],
    quiz=[
        {
            "question": "What does `satisfies` do that a type annotation does not?",
            "options": [
                "It validates the value against the type while keeping the value's own narrower inferred type",
                "It validates the value at runtime",
                "It widens the value to the given type",
                "It makes the value readonly",
            ],
            "answer": 0,
            "explanation": "An annotation replaces the inferred type; `satisfies` only checks against it. That is how you keep literal key and tuple information while still enforcing a contract.",
        },
        {
            "question": "With `const routes = { home: \"/\" } satisfies Record<string, string>`, what is `keyof typeof routes`?",
            "options": [
                "\"home\"",
                "string",
                "Record<string, string>",
                "never",
            ],
            "answer": 0,
            "explanation": "The inferred object type is preserved, so its keys are the literal union of what was actually written. With a plain `Record<string, string>` annotation it would have been `string`.",
        },
        {
            "question": "Does `satisfies` help validate JSON arriving from a network call?",
            "options": [
                "No — it is erased at compile time and checks nothing at runtime",
                "Yes, it throws when the shape does not match",
                "Yes, but only in strict mode",
                "Only for objects, not arrays",
            ],
            "answer": 0,
            "explanation": "Like every type-level construct it disappears before the code runs. Runtime data still needs a type predicate or a schema validator.",
        },
    ],
)

_concept(
    "ts_branded_types", "TS: Type System",
    "Branded (Nominal) Types",
    "Making two structurally identical types incompatible on purpose.",
    "Structural typing means every `string` is interchangeable with every other `string` — so a `UserId` and an `OrderId` are the same type, and passing one where the other is expected compiles fine. A *brand* attaches a phantom property that exists only in the type system, making the two incompatible. The only way to obtain a branded value is through a constructor function that performs the validation, so 'this string has been validated' becomes something the compiler can enforce.",
    "This recreates Java's habit of wrapping primitives in a value class (`record UserId(String value)`) without the runtime allocation — the brand is erased, so a `UserId` IS the underlying string at runtime.",
    """
### The problem
```ts
function loadUser(id: string) { /* ... */ }
function loadOrder(id: string) { /* ... */ }

const orderId = "ord_991";
loadUser(orderId);   // compiles — and is a bug
```

### Branding with a unique symbol
```ts
declare const brand: unique symbol;

type UserId  = string & { readonly [brand]: "UserId" };
type OrderId = string & { readonly [brand]: "OrderId" };
```
`declare const` means "this exists in the type system only" — nothing is emitted.
The intersection keeps all the `string` methods while making the two types
mutually unassignable.

### A validating constructor is the only door in
```ts
function toUserId(raw: string): UserId {
  if (!/^u_\\d+$/.test(raw)) throw new Error("bad user id");
  return raw as UserId;
}

const id = toUserId("u_42");
id.toUpperCase();     // still a string, all methods available
loadOrder(id);        // Error — UserId is not OrderId
```
The single `as UserId` inside the constructor is the one place the invariant is
asserted. Everywhere else, the type carries the proof.

### Branding numbers too
```ts
type Cents   = number & { readonly [brand]: "Cents" };
type Dollars = number & { readonly [brand]: "Dollars" };

const toDollars = (c: Cents): Dollars => (c / 100) as Dollars;
```
Now adding cents to dollars is a compile error rather than a rounding disaster.

### Watch out for
- Brands are erased. `typeof id === "string"` at runtime; there is no way to
  ask "is this a UserId?" without re-running the validation.
- Return `T | null` from the parser rather than throwing when invalid input is
  expected — it forces the caller to handle the failure.
- Keep the brand symbol module-private so nobody can forge a value.
""",
    [
        tsx("ts_branded_types-construct", "A validating constructor",
            "`UserId` is a branded string. Replace `____` with `toUserId`: it rejects an empty string by throwing, and otherwise returns the raw string cast to `UserId` — the single place the brand is applied.",
            _P('''
import * as fs from "fs";
declare const brand: unique symbol;
type UserId = string & { readonly [brand]: "UserId" };
function toUserId(raw: string): UserId {
  if (raw.length === 0) throw new Error("empty id");
  return raw as UserId;
}
const id = toUserId(fs.readFileSync(0, "utf8").trim());
console.log(id.toUpperCase());
console.log(id.length);
'''),
            ['function toUserId(raw: string): UserId {\n  if (raw.length === 0) throw new Error("empty id");\n  return raw as UserId;\n}'],
            [("u42", "U42\n3"), ("abc", "ABC\n3"), ("x", "X\n1")],
            hint="Guard first, then `return raw as UserId`. A branded value is still a plain string at runtime, so .toUpperCase() works."),
        tsx("ts_branded_types-units", "Units that cannot mix",
            "`Cents` and `Dollars` are both branded numbers, so one cannot be passed where the other is expected. Replace `____` with `toDollars`: it takes `Cents`, divides by 100, and returns the result branded as `Dollars`.",
            _P('''
import * as fs from "fs";
declare const brand: unique symbol;
type Cents = number & { readonly [brand]: "Cents" };
type Dollars = number & { readonly [brand]: "Dollars" };
const cents = (n: number) => n as Cents;
const toDollars = (c: Cents): Dollars => (c / 100) as Dollars;
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
const total = cents(a + b);
console.log(total);
console.log(toDollars(total));
'''),
            ["const toDollars = (c: Cents): Dollars => (c / 100) as Dollars;"],
            [("120 30", "150\n1.5"), ("100 0", "100\n1"),
             ("0 0", "0\n0"), ("250 250", "500\n5")],
            hint="An arrow with an explicit return type: (c: Cents): Dollars => (c / 100) as Dollars."),
        _mchal("ts_branded_types-challenge", "Ticket ids", "Medium",
               "A valid ticket id is three letters, a hyphen, then four digits (`ABC-1234`), case-insensitive on input. Brand it as `TicketId`, and write `parseTicket(raw): TicketId | null` that uppercases and validates. The input is `n` then `n` candidate lines. Print the valid ids space-separated in input order (or `(none)`), then the number rejected.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
declare const brand: unique symbol;
type TicketId = string & { readonly [brand]: "TicketId" };
function parseTicket(raw: string): TicketId | null {
  const value = raw.trim().toUpperCase();
  return /^[A-Z]{3}-\\d{4}$/.test(value) ? (value as TicketId) : null;
}
const valid: TicketId[] = [];
let invalid = 0;
for (let i = 1; i <= n; i++) {
  const ticket = parseTicket(lines[i]);
  if (ticket === null) invalid++;
  else valid.push(ticket);
}
console.log(valid.length === 0 ? "(none)" : valid.join(" "));
console.log(invalid);
''',
               [("3\nabc-1234\nXYZ-9999\nbad", "ABC-1234 XYZ-9999\n1"),
                ("1\nzz-1", "(none)\n1"),
                ("2\nAAA-0000\nBBB-1111", "AAA-0000 BBB-1111\n0"),
                ("2\nabc-12345\nabc-123", "(none)\n2")],
               hint="Returning `TicketId | null` rather than throwing makes the caller deal with bad input. Anchor the regex with ^ and $ so partial matches are rejected."),
    ],
    quiz=[
        {
            "question": "What does a brand cost at runtime?",
            "options": [
                "Nothing — the intersection is erased and the value stays a plain string or number",
                "One extra object allocation per value",
                "A hidden property is added to each value",
                "A prototype lookup on every access",
            ],
            "answer": 0,
            "explanation": "The brand lives entirely in the type system. That is the appeal over a wrapper class: full nominal safety with zero runtime representation.",
        },
        {
            "question": "Why should the constructor function be the ONLY place that writes `as UserId`?",
            "options": [
                "It concentrates the unchecked assertion in one validated spot, so the type genuinely implies the invariant",
                "TypeScript only allows one cast per type",
                "Casting elsewhere is a runtime error",
                "The compiler tracks how many casts a program contains",
            ],
            "answer": 0,
            "explanation": "The brand is only as trustworthy as the assertions that create it. Scattering casts around means the type no longer proves anything.",
        },
        {
            "question": "How can you check at runtime whether a value is a `UserId`?",
            "options": [
                "You cannot directly — you must re-run the validation the constructor performs",
                "typeof value === \"UserId\"",
                "value instanceof UserId",
                "brand in value",
            ],
            "answer": 0,
            "explanation": "Since the brand is erased there is nothing to inspect. Runtime questions about a branded value always come back to re-checking the underlying data.",
        },
    ],
)


# ===========================================================================
# REGISTER — merge everything authored above into the shared seed dictionaries.
# New concept chunks are inserted directly above this marker.
# ===========================================================================

# ===========================================================================
# TS: Generics & Type-Level
# ===========================================================================

_concept(
    "ts_generic_constraints", "TS: Generics & Type-Level",
    "Generic Constraints",
    "Restricting a type parameter with `extends` so the body can use it, without losing the caller's exact type.",
    "An unconstrained `<T>` can be anything, so the body can do nothing with it but pass it along. `<T extends Constraint>` promises the body a minimum shape while still remembering, at each call site, the specific type that was supplied. The most valuable constraint is `K extends keyof T`, which links a key argument to the object it indexes — so `get(user, \"name\")` returns `string` and `get(user, \"age\")` returns `number` from one signature.",
    "This is Java's `<T extends Comparable<T>>` bound, plus something Java has no equivalent for: `keyof` turns an object's property names into a type, so a generic can be parameterized by *which field* it touches.",
    """
### Why constrain at all
```ts
function longest<T>(a: T, b: T): T {
  return a.length >= b.length ? a : b;   // Error: no .length on T
}
```
`T` could be a `number`. Add the minimum shape you actually use:
```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
longest("hello", "hi");   // T = string  -> string
longest([1, 2], [3]);     // T = number[] -> number[]
```
The return type is still the *caller's* type, not `{ length: number }` — that is
the difference from just declaring the parameter as `{ length: number }`.

### `K extends keyof T` — the workhorse
```ts
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "ada", age: 36 };
get(user, "name");   // string
get(user, "age");    // number
get(user, "nope");   // Error: not a key of user
```
`T[K]` is an *indexed access type*: the type of the property named `K`.

### Constraints compose
```ts
function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((item) => item[key]);
}
```

### Default type parameters
```ts
function makeBox<T = string>(value: T) {
  return { value };
}
makeBox(1);    // T = number, inferred
makeBox();     // Error — a default is not a fallback for a missing argument
```
A default only supplies `T` when inference has nothing to work with.

### Watch out for
- Do not over-constrain. Add `extends` only for capabilities the body uses.
- `T extends object` excludes primitives; `T extends {}` excludes only
  `null`/`undefined` — they are not the same thing.
- If the body never uses `T`, you probably wanted a plain parameter type.
""",
    [
        tsx("ts_generic_constraints-pluck", "Pull one field out of every row",
            "Replace `____` with `pluck`, constrained as `<T, K extends keyof T>` so `pluck(rows, \"name\")` gives `string[]` and `pluck(rows, \"score\")` gives `number[]`. Its body maps each item to `item[key]`.",
            _P('''
import * as fs from "fs";
type Row = { name: string; score: number };
function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((item) => item[key]);
}
const rows: Row[] = fs
  .readFileSync(0, "utf8")
  .trim()
  .split("\\n")
  .map((line) => {
    const [name, score] = line.trim().split(/\\s+/);
    return { name, score: Number(score) };
  });
console.log(pluck(rows, "name").join(" "));
console.log(pluck(rows, "score").reduce((a, b) => a + b, 0));
'''),
            ["function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {\n  return items.map((item) => item[key]);\n}"],
            [("ada 10\nbob 20", "ada bob\n30"), ("solo 5", "solo\n5"),
             ("a 1\nb 2\nc 3", "a b c\n6")],
            hint="Two type parameters: T for the row and K constrained to keyof T. The return type is T[K][]."),
        tsx("ts_generic_constraints-max", "Constrain to a capability",
            "`maxOf` works on anything with a `valueOf(): number` — numbers and Dates both qualify. Replace `____` with its body: scan for the item whose `valueOf()` is greatest, keeping the first on a tie.",
            _P('''
import * as fs from "fs";
type Comparable = { valueOf(): number };
function maxOf<T extends Comparable>(items: T[]): T {
  let best = items[0];
  for (const item of items) {
    if (item.valueOf() > best.valueOf()) best = item;
  }
  return best;
}
const nums = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
console.log(maxOf(nums));
console.log(maxOf([new Date(0), new Date(1000)]).getTime());
'''),
            ["  let best = items[0];\n  for (const item of items) {\n    if (item.valueOf() > best.valueOf()) best = item;\n  }\n  return best;"],
            [("3 9 2", "9\n1000"), ("-1", "-1\n1000"), ("5 5 4", "5\n1000")],
            hint="Because T is constrained, the body may call .valueOf() — and because it is still generic, the return keeps the caller's element type."),
        _mchal("ts_generic_constraints-challenge", "Group by a field", "Medium",
               "Write `groupBy<T, K extends keyof T>(items, key): Map<T[K], T[]>`. The input is `n` then `n` lines of `dept name`. Group the rows by `dept` and print one line per department in alphabetical order: `dept: name1 name2`, with the names in input order.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Row = { dept: string; name: string };
function groupBy<T, K extends keyof T>(items: T[], key: K): Map<T[K], T[]> {
  const out = new Map<T[K], T[]>();
  for (const item of items) {
    const bucketKey = item[key];
    const bucket = out.get(bucketKey);
    if (bucket === undefined) out.set(bucketKey, [item]);
    else bucket.push(item);
  }
  return out;
}
const rows: Row[] = lines.slice(1, n + 1).map((line) => {
  const [dept, name] = line.trim().split(/\\s+/);
  return { dept, name };
});
const groups = groupBy(rows, "dept");
for (const dept of [...groups.keys()].sort()) {
  console.log(dept + ": " + groups.get(dept)!.map((r) => r.name).join(" "));
}
''',
               [("3\neng ada\nsales bob\neng cy", "eng: ada cy\nsales: bob"),
                ("1\nx solo", "x: solo"),
                ("4\nb 1\na 2\nb 3\na 4", "a: 2 4\nb: 1 3"),
                ("2\nz p\nz q", "z: p q")],
               hint="The Map is keyed by T[K], so the grouping key keeps its real type. Push into an existing bucket or create a new one."),
    ],
    quiz=[
        {
            "question": "Why is `function longest<T extends { length: number }>(a: T, b: T): T` better than `function longest(a: { length: number }, b: { length: number }): { length: number }`?",
            "options": [
                "The generic returns the caller's exact type instead of collapsing it to { length: number }",
                "The generic is faster at runtime",
                "The non-generic version does not compile",
                "Only the generic accepts arrays",
            ],
            "answer": 0,
            "explanation": "Both accept the same arguments. The difference is on the way out: the generic hands back `string` for strings, while the plain signature loses everything except `.length`.",
        },
        {
            "question": "In `function get<T, K extends keyof T>(obj: T, key: K): T[K]`, what is `T[K]`?",
            "options": [
                "An indexed access type — the type of the property named K on T",
                "An array of T indexed by K",
                "A mapped type over T",
                "The same as keyof T",
            ],
            "answer": 0,
            "explanation": "`T[K]` looks up a property type by name, which is what lets one signature return `string` for `\\\"name\\\"` and `number` for `\\\"age\\\"`.",
        },
        {
            "question": "What does the default in `function makeBox<T = string>(value: T)` actually do?",
            "options": [
                "It supplies T only when inference has nothing to infer from",
                "It makes the value parameter optional",
                "It coerces the argument to string",
                "It restricts T to string",
            ],
            "answer": 0,
            "explanation": "A type-parameter default is not a value default. `makeBox(1)` still infers `T = number`; the default matters for cases like `const b: Box = ...` where no argument drives inference.",
        },
    ],
)

_concept(
    "ts_keyof_indexed", "TS: Generics & Type-Level",
    "keyof, typeof & Indexed Access",
    "Deriving types from values and from other types, so one source of truth drives both.",
    "These three operators turn existing things into types. `typeof value` lifts a runtime value into the type world. `keyof Type` collapses a type's property names into a union of string literals. `Type[Key]` reads the type of a property back out. Chained together — `(typeof levels)[number]` — they let a single literal array or object generate the union, the lookup table and the function signatures that use them, so adding an entry can never leave a type out of date.",
    "Java has nothing like this: a type cannot be computed from a value. The nearest habit is generating an enum from a constant list, except here the derivation happens in the compiler and stays in sync automatically.",
    """
### `typeof` — from a value to its type
```ts
const settings = { theme: "dark", fontSize: 14, wrap: true };
type Settings = typeof settings;
// { theme: string; fontSize: number; wrap: boolean }
```
This is the *type-position* `typeof`, unrelated to the runtime `typeof x === "string"` operator.

### `keyof` — from a type to its key union
```ts
type Key = keyof Settings;    // "theme" | "fontSize" | "wrap"
```

### Indexed access — from a type and key to a property type
```ts
type Theme = Settings["theme"];        // string
type Any = Settings[keyof Settings];   // string | number | boolean
```

### The array trick
```ts
const levels = ["debug", "info", "warn", "error"] as const;
type Level = (typeof levels)[number];
// "debug" | "info" | "warn" | "error"
```
`as const` keeps the literal types; indexing by `number` unions all the elements.
One array now drives both the runtime list and the type — add `"fatal"` and every
exhaustive switch over `Level` updates itself.

### Putting them together
```ts
function read<K extends keyof Settings>(key: K): Settings[K] {
  return settings[key];
}
read("fontSize");   // number
```

### Watch out for
- Without `as const`, `["a","b"]` infers `string[]` and `(typeof arr)[number]`
  is just `string`.
- `keyof` on an index signature gives the index type: `keyof Record<string, X>`
  is `string | number`, not a literal union.
- Number-keyed objects surprise people: `keyof { 0: X }` is `0`, not `"0"`.
""",
    [
        tsx("ts_keyof_indexed-read", "A typed getter",
            "Replace `____` with `read`, generic over `K extends keyof Settings` and returning `Settings[K]`, so each key gives back its own property type. Its body is a single indexed lookup.",
            _P('''
import * as fs from "fs";
type Settings = { theme: string; fontSize: number; wrap: boolean };
const settings: Settings = { theme: "dark", fontSize: 14, wrap: true };
function read<K extends keyof Settings>(key: K): Settings[K] {
  return settings[key];
}
const key = fs.readFileSync(0, "utf8").trim() as keyof Settings;
console.log(String(read(key)));
console.log(Object.keys(settings).sort().join(","));
'''),
            ["function read<K extends keyof Settings>(key: K): Settings[K] {\n  return settings[key];\n}"],
            [("theme", "dark\nfontSize,theme,wrap"),
             ("fontSize", "14\nfontSize,theme,wrap"),
             ("wrap", "true\nfontSize,theme,wrap")],
            hint="One type parameter constrained to keyof Settings, returning Settings[K]. The body is just settings[key]."),
        tsx("ts_keyof_indexed-levels", "Derive a union from an array",
            "`levels` is `as const`, so `(typeof levels)[number]` is the union of its four strings. Replace `____` with `rank`, which takes a `Level` and returns its position in `levels`.",
            _P('''
import * as fs from "fs";
const levels = ["debug", "info", "warn", "error"] as const;
type Level = (typeof levels)[number];
function rank(level: Level): number {
  return levels.indexOf(level);
}
const input = fs.readFileSync(0, "utf8").trim();
console.log(rank(input as Level));
console.log(levels.length);
'''),
            ["function rank(level: Level): number {\n  return levels.indexOf(level);\n}"],
            [("warn", "2\n4"), ("debug", "0\n4"), ("error", "3\n4"), ("info", "1\n4")],
            hint="indexOf on the readonly tuple gives the position — the type only has to accept a Level and return a number."),
        _mchal("ts_keyof_indexed-challenge", "Profile lookup", "Medium",
               "A `profile` object holds `name: \"ada\"`, `age: 36`, `city: \"london\"`, `score: 99`. Derive `Profile` with `typeof` and `Key` with `keyof`, and write a `read<K extends Key>(key: K): Profile[K]`. The input is `n` then `n` key names: print each key's value, or `unknown key`. Finally print the keys whose values are numbers, space-separated in alphabetical order.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const profile = { name: "ada", age: 36, city: "london", score: 99 };
type Profile = typeof profile;
type Key = keyof Profile;
function read<K extends Key>(key: K): Profile[K] {
  return profile[key];
}
for (let i = 1; i <= n; i++) {
  const key = lines[i].trim();
  if (key in profile) console.log(String(read(key as Key)));
  else console.log("unknown key");
}
const numeric = (Object.keys(profile) as Key[])
  .filter((k) => typeof profile[k] === "number")
  .sort();
console.log(numeric.join(" "));
''',
               [("2\nname\nage", "ada\n36\nage score"),
                ("1\nnope", "unknown key\nage score"),
                ("3\ncity\nscore\nname", "london\n99\nada\nage score"),
                ("1\nage", "36\nage score")],
               hint="`key in profile` is the runtime check; `as Key` is what lets you index afterwards. Object.keys returns string[], so cast it to Key[] to index safely."),
    ],
    quiz=[
        {
            "question": "What is `(typeof levels)[number]` when `const levels = [\"a\", \"b\"] as const`?",
            "options": [
                "\"a\" | \"b\"",
                "string",
                "readonly [\"a\", \"b\"]",
                "number",
            ],
            "answer": 0,
            "explanation": "`as const` makes the tuple's elements literal types, and indexing the tuple type by `number` unions every element — the standard way to derive a union from a runtime list.",
        },
        {
            "question": "Drop the `as const`. What does `(typeof levels)[number]` become?",
            "options": [
                "string",
                "\"a\" | \"b\"",
                "never",
                "string[]",
            ],
            "answer": 0,
            "explanation": "Without `as const` the array widens to `string[]`, so indexing it by number yields `string` — the literal information is gone before the type-level trick can use it.",
        },
        {
            "question": "How does the type-position `typeof` differ from the runtime `typeof` operator?",
            "options": [
                "The type-position one lifts a value into a type; the runtime one returns a string at execution time",
                "They are the same operator used in two places",
                "The type-position one only works on classes",
                "The runtime one is removed by the compiler",
            ],
            "answer": 0,
            "explanation": "They share a keyword and nothing else. `type S = typeof settings` computes a type; `typeof x === \\\"string\\\"` is a runtime check that happens to also narrow.",
        },
    ],
)

_concept(
    "ts_mapped_types", "TS: Generics & Type-Level",
    "Mapped Types",
    "Building a new object type by transforming every property of an existing one.",
    "A mapped type loops over a union of keys and produces a property for each: `{ [K in keyof T]: ... }`. Changing the value position gives `Readonly<T>` or a wrapped version; adding `?` or `readonly` (or removing them with `-?` / `-readonly`) changes the modifiers; and `as` in the key position renames keys. Every built-in utility type — `Partial`, `Required`, `Readonly`, `Pick`, `Record` — is a mapped type you could have written yourself.",
    "There is no Java parallel. The closest intuition is a compile-time code generator that rewrites a type's members, except it runs in the type checker and stays in sync with the source type automatically.",
    """
### The shape
```ts
type Optional<T> = { [K in keyof T]?: T[K] };
```
Read it as: for each key `K` in `keyof T`, produce a property `K` whose type is
`T[K]` — and make it optional. That is exactly the built-in `Partial<T>`.

### Transforming the value
```ts
type Boxed<T> = { [K in keyof T]: { value: T[K] } };

type Config = { host: string; port: number };
type BoxedConfig = Boxed<Config>;
// { host: { value: string }; port: { value: number } }
```

### Adding and removing modifiers
```ts
type Frozen<T>   = { readonly [K in keyof T]: T[K] };   // Readonly<T>
type Thawed<T>   = { -readonly [K in keyof T]: T[K] };
type Demanded<T> = { [K in keyof T]-?: T[K] };          // Required<T>
```
The `-` prefix strips a modifier the source type had.

### Renaming keys with `as`
```ts
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
};

type P = Getters<{ name: string; age: number }>;
// { getName: () => string; getAge: () => number }
```
Mapping a key to `never` in the `as` clause *removes* it — that is how `Omit`
filters properties out.

### The built-ins are all mapped types
```ts
type Pick<T, K extends keyof T> = { [P in K]: T[P] };
type Record<K extends keyof any, V> = { [P in K]: V };
```

### Watch out for
- Mapped types are erased. `Getters<T>` describes an object you still have to
  build at runtime — usually with a cast at the boundary of the loop that
  builds it.
- Mapping over a union distributes only if you write it that way; `keyof (A | B)`
  is the keys they SHARE, not all of them.
""",
    [
        tsx("ts_mapped_types-patch", "Apply an optional patch",
            "`Optional<T>` is a hand-written `Partial`. Replace `____` with the body of `applyPatch`: return a new object with `base`'s fields overridden by whichever fields `patch` actually supplies.",
            _P('''
import * as fs from "fs";
type Config = { host: string; port: number };
type Optional<T> = { [K in keyof T]?: T[K] };
function applyPatch(base: Config, patch: Optional<Config>): Config {
  return { ...base, ...patch };
}
const [host, port] = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
const patch: Optional<Config> = host === "-" ? { port: Number(port) } : { host };
const patched = applyPatch({ host: "localhost", port: 80 }, patch);
console.log(patched.host + ":" + patched.port);
'''),
            ["  return { ...base, ...patch };"],
            [("- 8080", "localhost:8080"), ("example.com 0", "example.com:80"),
             ("- 443", "localhost:443"), ("api.dev 1", "api.dev:80")],
            hint="Spreading patch second lets its present keys win; absent keys leave base untouched."),
        tsx("ts_mapped_types-getters", "Build what the mapped type describes",
            "`Getters<T>` renames each key to `getX` and wraps its type in a function. Replace `____` with the body of `makeGetters`, which builds that object at runtime: for each key, add a `get`+Capitalized entry holding a function that returns the property.",
            _P('''
import * as fs from "fs";
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
const source = { name: fs.readFileSync(0, "utf8").trim(), age: 36 };
function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: Record<string, () => unknown> = {};
  for (const key of Object.keys(obj)) {
    out["get" + key[0].toUpperCase() + key.slice(1)] = () =>
      (obj as Record<string, unknown>)[key];
  }
  return out as Getters<T>;
}
const g = makeGetters(source);
console.log(g.getName());
console.log(g.getAge());
console.log(Object.keys(g).sort().join(","));
'''),
            ['  const out: Record<string, () => unknown> = {};\n  for (const key of Object.keys(obj)) {\n    out["get" + key[0].toUpperCase() + key.slice(1)] = () =>\n      (obj as Record<string, unknown>)[key];\n  }\n  return out as Getters<T>;'],
            [("ada", "ada\n36\ngetAge,getName"), ("bob", "bob\n36\ngetAge,getName")],
            hint="The mapped type is erased, so the runtime loop has to build the renamed keys itself — and the final cast is where you assert it matches."),
        _mchal("ts_mapped_types-challenge", "Pick a projection", "Medium",
               "Write `pick<T extends object, K extends keyof T>(obj, keys): Pick<T, K>`. The input is `n`, then `n` lines of `key=value`, then a final line of comma-separated keys to keep. Print the kept pairs as `key=value`, one per line in alphabetical key order, then print how many keys were dropped.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const record: Record<string, string> = {};
for (let i = 1; i <= n; i++) {
  const [key, value] = lines[i].split("=");
  record[key.trim()] = value.trim();
}
const wanted = lines[n + 1].trim().split(",").map((s) => s.trim());
function pick<T extends object, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const out = {} as Pick<T, K>;
  for (const key of keys) {
    if (key in obj) out[key] = obj[key];
  }
  return out;
}
const picked = pick(record, wanted);
const keys = Object.keys(picked).sort();
for (const key of keys) console.log(key + "=" + picked[key]);
console.log(Object.keys(record).length - keys.length);
''',
               [("3\na=1\nb=2\nc=3\nb,c", "b=2\nc=3\n1"),
                ("2\nx=9\ny=8\nx", "x=9\n1"),
                ("1\nk=v\nzzz", "1"),
                ("2\np=1\nq=2\np,q", "p=1\nq=2\n0")],
               hint="`Pick<T, K>` is itself the mapped type `{ [P in K]: T[P] }`. Start from an empty object cast to that type and copy only the requested keys that exist."),
    ],
    quiz=[
        {
            "question": "What does `{ [K in keyof T]-?: T[K] }` produce?",
            "options": [
                "Every property of T made required — the built-in Required<T>",
                "Every property of T made optional",
                "T with all properties removed",
                "A union of T's property types",
            ],
            "answer": 0,
            "explanation": "The `-` prefix strips a modifier the source had, so `-?` removes optionality. `-readonly` does the same for readonly.",
        },
        {
            "question": "In a mapped type's `as` clause, what happens to a key you map to `never`?",
            "options": [
                "The property is removed from the result — this is how Omit works",
                "The property's type becomes never",
                "It becomes a compile error",
                "The key is renamed to \"never\"",
            ],
            "answer": 0,
            "explanation": "Key remapping to `never` drops the entry entirely, which is exactly the mechanism behind filtering utilities like `Omit`.",
        },
        {
            "question": "You define `type Getters<T>` that renames keys to `getName`, `getAge`. What exists at runtime?",
            "options": [
                "Nothing — you must still build the object yourself; the type only describes it",
                "An object with those methods, generated by the compiler",
                "A proxy that forwards property access",
                "The original object with extra prototype methods",
            ],
            "answer": 0,
            "explanation": "Mapped types are erased like every other type. They describe the shape your runtime code is obliged to produce, usually ending in a cast where the loop finishes.",
        },
    ],
)

_concept(
    "ts_conditional_types", "TS: Generics & Type-Level",
    "Conditional Types & infer",
    "Types that branch — `T extends U ? X : Y` — and pattern-match with `infer`.",
    "A conditional type asks whether one type is assignable to another and picks a branch accordingly. Inside the `extends` clause, `infer U` introduces a fresh type variable bound to whatever matched at that position — which is how `ReturnType<F>` pulls the result type out of a function, or `Unwrap<T>` pulls the element type out of an array. Conditional types over a *naked* type parameter also distribute across unions, applying the branch to each member separately.",
    "There is no equivalent in Java's generics, which cannot branch on a type argument. The closest mental model is pattern matching on a type's structure at compile time.",
    """
### Branching
```ts
type IsString<T> = T extends string ? "yes" : "no";
type A = IsString<"hi">;    // "yes"
type B = IsString<42>;      // "no"
```

### `infer` pattern-matches inside the check
```ts
type Unwrap<T> = T extends (infer U)[] ? U : T;

type A = Unwrap<number[]>;   // number
type B = Unwrap<string>;     // string  (not an array, so the else branch)
```
`infer U` says "match whatever sits here and call it `U`".

### The built-ins work this way
```ts
type ReturnType<F> = F extends (...args: any[]) => infer R ? R : never;
type Awaited<T>    = T extends Promise<infer V> ? V : T;
type Parameters<F> = F extends (...args: infer P) => any ? P : never;
```

### Distribution over unions
```ts
type NonNil<T> = T extends null | undefined ? never : T;
type C = NonNil<string | null | number>;   // string | number
```
Because `T` appears *naked* on the left, the conditional is applied to each
union member and the results are unioned back up. `never` members vanish — which
is exactly how `Exclude<T, U>` filters a union.

To switch distribution OFF, wrap both sides in brackets:
```ts
type NoDistribute<T> = [T] extends [null] ? "yes" : "no";
```

### Watch out for
- Distribution only happens for a bare type parameter. `Wrapper<T> extends ...`
  does not distribute.
- `any` takes BOTH branches: `IsString<any>` is `"yes" | "no"`.
- Conditional types are erased. They describe what a runtime function returns;
  the function still has to do the work, usually ending in a cast.
""",
    [
        tsx("ts_conditional_types-unwrap", "Unwrap an array type",
            "`Unwrap<T>` gives the element type for arrays and `T` itself otherwise. Replace `____` with the body of `firstOrSelf`: return the first element when the value is an array, else the value — cast to `Unwrap<T>` since the compiler cannot follow the runtime branch.",
            _P('''
import * as fs from "fs";
type Unwrap<T> = T extends (infer U)[] ? U : T;
function firstOrSelf<T>(value: T): Unwrap<T> {
  return (Array.isArray(value) ? value[0] : value) as Unwrap<T>;
}
const tokens = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
console.log(firstOrSelf(tokens));
console.log(firstOrSelf("solo"));
'''),
            ["  return (Array.isArray(value) ? value[0] : value) as Unwrap<T>;"],
            [("a b c", "a\nsolo"), ("x", "x\nsolo"), ("1 2", "1\nsolo")],
            hint="One ternary on Array.isArray, then a cast — the conditional type describes the result the runtime branch produces."),
        tsx("ts_conditional_types-compact", "Filter nulls out of a union",
            "`NonNil<T>` distributes over a union and drops the nullish members. Replace `____` with the body of `compact`: keep only values that are neither `null` nor `undefined`, cast to the filtered type.",
            _P('''
import * as fs from "fs";
type NonNil<T> = T extends null | undefined ? never : T;
function compact<T>(items: T[]): NonNil<T>[] {
  return items.filter((x) => x !== null && x !== undefined) as NonNil<T>[];
}
const raw = fs
  .readFileSync(0, "utf8")
  .trim()
  .split(/\\s+/)
  .map((t) => (t === "-" ? null : t));
console.log(compact(raw).join(" ") || "(none)");
console.log(compact(raw).length);
'''),
            ['  return items.filter((x) => x !== null && x !== undefined) as NonNil<T>[];'],
            [("a - b", "a b\n2"), ("- -", "(none)\n0"),
             ("x y", "x y\n2"), ("-", "(none)\n0")],
            hint="A single filter rejecting both null and undefined, then a cast to NonNil<T>[]."),
        _mchal("ts_conditional_types-challenge", "Route matcher", "Medium",
               "The input is two lines: a route pattern like `/users/:id/posts/:postId` and a concrete path. Segments starting with `:` capture a parameter; every other segment must match exactly, and the segment counts must agree. Print the captured params as `name=value` pairs, space-separated in alphabetical name order, or `(no params)` when the route has none — and `no match` when the path does not fit.",
               '''
const lines = input.split("\\n");
const patternParts = lines[0].trim().split("/").filter((p) => p.length > 0);
const pathParts = lines[1].trim().split("/").filter((p) => p.length > 0);
if (patternParts.length !== pathParts.length) {
  console.log("no match");
} else {
  const params: Record<string, string> = {};
  let matched = true;
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(":")) params[patternParts[i].slice(1)] = pathParts[i];
    else if (patternParts[i] !== pathParts[i]) matched = false;
  }
  if (!matched) {
    console.log("no match");
  } else {
    const names = Object.keys(params).sort();
    console.log(names.length === 0 ? "(no params)" : names.map((k) => k + "=" + params[k]).join(" "));
  }
}
''',
               [("/users/:id/posts/:postId\n/users/7/posts/42", "id=7 postId=42"),
                ("/a/b\n/a/b", "(no params)"),
                ("/users/:id\n/orders/9", "no match"),
                ("/x/:y\n/x/y/z", "no match"),
                ("/:only\n/value", "only=value")],
               hint="Check the segment counts first, then walk both lists together — a `:` segment captures, anything else must be equal."),
    ],
    quiz=[
        {
            "question": "What does `infer` do inside a conditional type?",
            "options": [
                "Binds a fresh type variable to whatever type matched at that position",
                "Forces TypeScript to re-infer the whole expression",
                "Declares a default for the type parameter",
                "Converts a value into a type",
            ],
            "answer": 0,
            "explanation": "`T extends (infer U)[] ? U : T` matches T against 'array of something' and names that something `U` — pattern matching on the type's structure.",
        },
        {
            "question": "`type NonNil<T> = T extends null | undefined ? never : T`. What is `NonNil<string | null>`?",
            "options": [
                "string",
                "string | null",
                "never",
                "string | never",
            ],
            "answer": 0,
            "explanation": "T is a naked type parameter, so the conditional distributes: `string` takes the else branch and `null` becomes `never`, which disappears from the resulting union.",
        },
        {
            "question": "How do you stop a conditional type from distributing over a union?",
            "options": [
                "Wrap both sides in a tuple: [T] extends [U] ? X : Y",
                "Add the `nodistribute` modifier",
                "Constrain T with extends object",
                "Use an interface instead of a type alias",
            ],
            "answer": 0,
            "explanation": "Distribution requires a bare type parameter on the left. Putting it inside a tuple makes it non-naked, so the check runs once against the whole union.",
        },
    ],
)

_concept(
    "ts_template_literal_types", "TS: Generics & Type-Level",
    "Template Literal Types",
    "Building string literal types by interpolation, so naming conventions become type-checked.",
    "A template literal type is a string literal type with holes: `` `${Entity}:${Action}` ``. When the holes hold unions, the result is the cross product of every combination — three entities and three actions give nine valid event names, all checked. Combined with the intrinsic helpers `Uppercase`, `Lowercase`, `Capitalize` and `Uncapitalize`, this turns conventions like `on{Event}` or `--color-{name}` from documentation into something the compiler enforces.",
    "No Java analogue. It is the type system understanding string *structure*, so a typo'd event name or CSS variable is a compile error rather than a silent no-op.",
    """
### Interpolating into a literal type
```ts
type Unit = "px" | "em" | "%";
type Size = `${number}${Unit}`;

const a: Size = "12px";    // ok
const b: Size = "12pt";    // Error
```
`${number}` matches any numeric literal in string form.

### Unions multiply
```ts
type Entity = "user" | "order";
type Action = "created" | "deleted";
type EventName = `${Entity}:${Action}`;
// "user:created" | "user:deleted" | "order:created" | "order:deleted"
```
Two unions of two members give four names — every combination, none invented.

### The intrinsic case helpers
```ts
type Handler<E extends string> = `on${Capitalize<E>}`;
type H = Handler<"click">;    // "onClick"
```
`Uppercase`, `Lowercase`, `Capitalize` and `Uncapitalize` are built into the
compiler and only work inside template literal types.

### Pairing with key remapping
```ts
type Events<T> = {
  [K in keyof T as `on${Capitalize<string & K>}`]: (value: T[K]) => void
};
type E = Events<{ click: number }>;   // { onClick: (value: number) => void }
```

### Deriving the runtime list too
```ts
const entities = ["user", "order"] as const;
type Entity = (typeof entities)[number];
```
Now one `as const` array feeds both the loop that builds the catalogue and the
type that validates names against it.

### Watch out for
- Union sizes multiply. A template over four unions of ten members is 10,000
  types and the compiler will refuse past a limit.
- `${string}` matches anything, which makes the type as loose as `string` —
  useful for `infer` patterns, useless as a constraint.
""",
    [
        tsx("ts_template_literal_types-size", "A CSS size",
            "`Size` is the template literal type `` `${number}${Unit}` ``. Replace `____` with `toSize`, which joins the value and the unit into that shape and returns it cast to `Size`.",
            _P('''
import * as fs from "fs";
type Unit = "px" | "em" | "%";
type Size = `${number}${Unit}`;
function toSize(value: number, unit: Unit): Size {
  return `${value}${unit}` as Size;
}
const [v, u] = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
console.log(toSize(Number(v), u as Unit));
console.log(toSize(0, "px"));
'''),
            ["function toSize(value: number, unit: Unit): Size {\n  return `${value}${unit}` as Size;\n}"],
            [("12 px", "12px\n0px"), ("50 %", "50%\n0px"), ("1 em", "1em\n0px")],
            hint="A backtick template with both holes, then a cast — the compiler cannot verify a runtime-built string matches the pattern."),
        tsx("ts_template_literal_types-events", "Check an event name",
            "`EventName` is every `${Entity}:${Action}` combination. Replace `____` with `isHandled`, which reports whether the given name is one of the handlers registered in `handled`.",
            _P('''
import * as fs from "fs";
type Entity = "user" | "order";
type Action = "created" | "deleted";
type EventName = `${Entity}:${Action}`;
const handled: EventName[] = ["user:created", "order:deleted"];
function isHandled(name: string): boolean {
  return (handled as string[]).includes(name);
}
const input = fs.readFileSync(0, "utf8").trim();
console.log(isHandled(input));
console.log(handled.length);
'''),
            ["function isHandled(name: string): boolean {\n  return (handled as string[]).includes(name);\n}"],
            [("user:created", "true\n2"), ("user:deleted", "false\n2"),
             ("order:deleted", "true\n2"), ("nope", "false\n2")],
            hint="Widen the typed array to string[] before calling includes with an arbitrary string."),
        _mchal("ts_template_literal_types-challenge", "Event catalogue", "Medium",
               "Entities are `user`, `order`, `invoice`; actions are `created`, `updated`, `deleted`. Declare both as `as const` arrays, derive `EventName` as `` `${Entity}:${Action}` ``, and build the full catalogue at runtime in a `Set`. The input is `n` then `n` candidate names: print `ok` or `bad` for each, then the catalogue's size.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const entities = ["user", "order", "invoice"] as const;
const actions = ["created", "updated", "deleted"] as const;
type Entity = (typeof entities)[number];
type Action = (typeof actions)[number];
type EventName = `${Entity}:${Action}`;
const catalogue = new Set<EventName>();
for (const entity of entities) {
  for (const action of actions) {
    const name: EventName = `${entity}:${action}`;
    catalogue.add(name);
  }
}
for (let i = 1; i <= n; i++) {
  console.log((catalogue as Set<string>).has(lines[i].trim()) ? "ok" : "bad");
}
console.log(catalogue.size);
''',
               [("3\nuser:created\ninvoice:deleted\nuser:archived", "ok\nok\nbad\n9"),
                ("1\norder:updated", "ok\n9"),
                ("2\nnope\ninvoice:updated", "bad\nok\n9"),
                ("1\nuser:created", "ok\n9")],
               hint="The nested loops over the two `as const` arrays produce exactly the nine names the template literal type describes."),
    ],
    quiz=[
        {
            "question": "How many members does `` type T = `${\"a\" | \"b\"}-${\"x\" | \"y\" | \"z\"}` `` have?",
            "options": ["6", "5", "2", "3"],
            "answer": 0,
            "explanation": "Interpolating unions produces the cross product — 2 × 3 = 6 literal types. This growth is also why deeply nested templates can blow the compiler's limits.",
        },
        {
            "question": "Where can `Capitalize<T>` be used?",
            "options": [
                "Only inside template literal types — it is a compiler intrinsic, not a runtime function",
                "Anywhere, including as a runtime helper",
                "Only in mapped-type key remapping",
                "Only on union types",
            ],
            "answer": 0,
            "explanation": "`Capitalize`, `Uppercase`, `Lowercase` and `Uncapitalize` exist purely in the type system. Capitalizing an actual string at runtime is still your own code.",
        },
        {
            "question": "Why does `function toSize(v: number, u: Unit): Size { return `${v}${u}` as Size; }` need the cast?",
            "options": [
                "A template built from a runtime `number` widens to `string`, which the compiler cannot prove matches the pattern",
                "Casts are always required when returning template literals",
                "Size is a nominal type",
                "Unit is a union, and unions cannot be interpolated",
            ],
            "answer": 0,
            "explanation": "Type-level interpolation over `${number}` works on literal types. A runtime value produces an ordinary `string`, so you assert the invariant your code maintains.",
        },
    ],
)

_concept(
    "ts_type_level", "TS: Generics & Type-Level",
    "Recursive Types & Type-Level Programming",
    "Types that refer to themselves — modelling JSON, trees and deep transformations.",
    "A type alias may mention itself, which is how you describe data with no fixed depth: JSON, a file tree, a nested array. The same recursion works on transformations — `DeepReadonly<T>` applies itself to every nested object — and on tuples, where a conditional type peels one element at a time. The discipline is the same as writing a recursive function: a base case that stops, and a step that makes the problem strictly smaller.",
    "Java generics cannot recurse structurally, so the usual workaround is `Object` plus `instanceof` chains. Here the shape is described once and every access is checked against it.",
    """
### The canonical recursive type
```ts
type Json =
  | string
  | number
  | boolean
  | null
  | Json[]
  | { [key: string]: Json };
```
`Json` mentions itself twice. Anything `JSON.parse` can return fits, and nothing
else does.

### Recursion in the runtime code follows the type
```ts
function depth(value: Json): number {
  if (Array.isArray(value)) return 1 + Math.max(0, ...value.map(depth));
  if (value !== null && typeof value === "object") {
    return 1 + Math.max(0, ...Object.values(value).map(depth));
  }
  return 0;
}
```
Each `if` narrows one member of the union; the final `return` handles the
primitives that are left.

### Recursive transformations
```ts
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K]
};
```
The conditional decides whether to recurse or stop — the base case is "not an
object".

### Recursing over tuples
```ts
type Length<T extends readonly unknown[]> =
  T extends readonly [unknown, ...infer Rest] ? [1, ...Length<Rest>] : [];
```
`[first, ...infer Rest]` peels one element and recurses on the remainder. This
is how type-level arithmetic and parsers are built.

### Watch out for
- Recursion has a depth limit (around 50 for type instantiation, ~1000 for
  tail-recursive conditional types). Deep recursion errors with "type
  instantiation is excessively deep".
- An interface can be recursive; a `type` alias can too, but only through an
  object, array or function — `type Bad = Bad | string` is a circular error.
- Recursive types cost compile time. Reach for them when the data really is
  unbounded, not to be clever.
""",
    [
        tsx("ts_type_level-depth", "How deep does it nest?",
            "`Json` is a recursive union. Replace `____` with `depth`: arrays and objects count as one level plus the deepest of their children; every primitive is 0.",
            _P('''
import * as fs from "fs";
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };
function depth(value: Json): number {
  if (Array.isArray(value)) return 1 + Math.max(0, ...value.map(depth));
  if (value !== null && typeof value === "object") {
    return 1 + Math.max(0, ...Object.values(value).map(depth));
  }
  return 0;
}
const parsed = JSON.parse(fs.readFileSync(0, "utf8").trim()) as Json;
console.log(depth(parsed));
'''),
            ["function depth(value: Json): number {\n  if (Array.isArray(value)) return 1 + Math.max(0, ...value.map(depth));\n  if (value !== null && typeof value === \"object\") {\n    return 1 + Math.max(0, ...Object.values(value).map(depth));\n  }\n  return 0;\n}"],
            [("[1,[2,[3]]]", "3"), ("5", "0"), ('{"a":{"b":1}}', "2"), ("[]", "1")],
            hint="Test Array.isArray BEFORE the object check, since arrays are objects too — and remember typeof null is \"object\"."),
        tsx("ts_type_level-flatten", "Flatten arbitrary nesting",
            "`Nested` is `number | Nested[]`. Replace `____` with `flatten`, which returns a flat `number[]` — a lone number becomes a one-element array, and an array flat-maps itself.",
            _P('''
import * as fs from "fs";
type Nested = number | Nested[];
function flatten(value: Nested): number[] {
  if (!Array.isArray(value)) return [value];
  return value.flatMap(flatten);
}
const parsed = JSON.parse(fs.readFileSync(0, "utf8").trim()) as Nested;
console.log(flatten(parsed).join(" ") || "(empty)");
console.log(flatten(parsed).length);
'''),
            ["function flatten(value: Nested): number[] {\n  if (!Array.isArray(value)) return [value];\n  return value.flatMap(flatten);\n}"],
            [("[1,[2,[3,4]],5]", "1 2 3 4 5\n5"), ("7", "7\n1"),
             ("[[[]]]", "(empty)\n0"), ("[[1],[2]]", "1 2\n2")],
            hint="The base case wraps a single number; the recursive case is one flatMap over the children."),
        _mchal("ts_type_level-challenge", "Deep merge JSON", "Medium",
               "The input is two lines, each a JSON object. Merge them recursively: when both sides hold an object at a key, merge those; otherwise the right side wins. Print the result with every object's keys sorted, formatted exactly like compact `JSON.stringify` (no spaces), then print the number of top-level keys.",
               '''
const lines = input.split("\\n");
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };
type JsonObject = { [key: string]: Json };
function isObject(value: Json): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function merge(a: Json, b: Json): Json {
  if (isObject(a) && isObject(b)) {
    const out: JsonObject = { ...a };
    for (const key of Object.keys(b)) {
      out[key] = key in a ? merge(a[key], b[key]) : b[key];
    }
    return out;
  }
  return b;
}
function canonical(value: Json): string {
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (isObject(value)) {
    const parts = Object.keys(value)
      .sort()
      .map((key) => JSON.stringify(key) + ":" + canonical(value[key]));
    return "{" + parts.join(",") + "}";
  }
  return JSON.stringify(value);
}
const merged = merge(JSON.parse(lines[0]) as Json, JSON.parse(lines[1]) as Json);
console.log(canonical(merged));
console.log(isObject(merged) ? Object.keys(merged).length : 0);
''',
               [('{"a":1,"b":{"c":2}}\n{"b":{"d":3},"e":4}', '{"a":1,"b":{"c":2,"d":3},"e":4}\n3'),
                ('{"x":1}\n{"x":2}', '{"x":2}\n1'),
                ('{}\n{"k":[1,2]}', '{"k":[1,2]}\n1'),
                ('{"a":{"b":{"c":1}}}\n{"a":{"b":{"d":2}}}', '{"a":{"b":{"c":1,"d":2}}}\n1')],
               hint="A type predicate for 'plain object' keeps merge and canonical readable. Both functions recurse on exactly the branch where the type recurses."),
    ],
    quiz=[
        {
            "question": "Why is `type Bad = Bad | string` an error while `type Json = string | Json[]` is fine?",
            "options": [
                "A recursive alias must go through an object, array or function so the compiler has something concrete to expand",
                "Unions can never be recursive",
                "Bad is missing a base case",
                "type aliases cannot be recursive at all; only interfaces can",
            ],
            "answer": 0,
            "explanation": "`Bad` refers to itself immediately with nothing to anchor the expansion. Wrapping the recursion in `Json[]` gives the checker a structure to defer into.",
        },
        {
            "question": "In `type DeepReadonly<T> = { readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K] }`, what is the base case?",
            "options": [
                "A property whose type is not an object, which stops the recursion",
                "An empty object type",
                "The readonly modifier",
                "keyof T being never",
            ],
            "answer": 0,
            "explanation": "The conditional decides at each property whether to recurse. Primitives take the else branch and terminate that path.",
        },
        {
            "question": "What does `T extends readonly [unknown, ...infer Rest]` accomplish?",
            "options": [
                "Peels the first tuple element and binds the remainder to Rest, enabling recursion over tuples",
                "Checks that T is a readonly array of unknowns",
                "Reverses the tuple",
                "Makes the tuple mutable",
            ],
            "answer": 0,
            "explanation": "It is the type-level equivalent of destructuring a head and tail — the standard step for recursive tuple algorithms, which must shrink toward the empty-tuple base case.",
        },
    ],
)



# ===========================================================================
# TS: Runtime & Architecture
# ===========================================================================

_concept(
    "ts_iterators", "TS: Runtime & Architecture",
    "Iterators & Generators",
    "Making your own objects iterable, and producing values lazily with `function*`.",
    "Anything with a `[Symbol.iterator]()` method that returns `{ next(): { value, done } }` works with `for...of`, spread and destructuring. Writing that protocol by hand is tedious, so `function*` does it for you: each `yield` hands a value to the consumer and pauses until the next one is requested. Because generators are lazy, they can describe infinite sequences and pipelines that never build an intermediate array.",
    "`Iterable<T>` plays the role of Java's `Iterable<T>`, and `Symbol.iterator` is `iterator()`. A generator is what you would otherwise write as a hand-rolled `Iterator` with mutable state — or approximate with a lazy `Stream`.",
    """
### The protocol
```ts
const range: Iterable<number> = {
  [Symbol.iterator]() {
    let i = 0;
    return {
      next: () => (i < 3 ? { value: i++, done: false } : { value: undefined, done: true }),
    };
  },
};
[...range];   // [0, 1, 2]
```

### A generator writes that for you
```ts
function* range(n: number): Generator<number> {
  for (let i = 0; i < n; i++) yield i;
}
[...range(3)];              // [0, 1, 2]
for (const x of range(3)) { /* ... */ }
```
Execution pauses at each `yield` and resumes on the next request — the loop
variable survives across calls without you storing it anywhere.

### Making a class iterable
```ts
class Deck {
  #cards: string[] = ["A", "K", "Q"];
  *[Symbol.iterator](): Generator<string> {
    yield* this.#cards;
  }
}
[...new Deck()];   // ["A", "K", "Q"]
```
`yield*` delegates to another iterable, forwarding all of its values.

### Laziness pays off
```ts
function* naturals(): Generator<number> {
  let i = 1;
  while (true) yield i++;
}
function* take<T>(source: Iterable<T>, n: number): Generator<T> {
  let i = 0;
  for (const value of source) {
    if (i++ >= n) return;
    yield value;
  }
}
[...take(naturals(), 4)];   // [1, 2, 3, 4]
```
An infinite source is fine because nothing is computed until asked for.

### Watch out for
- A generator object is single-use. Iterate it twice and the second pass is
  empty — return a *function* if the caller may need to re-iterate.
- `Generator<T>` is `Generator<T, void, undefined>` by default; the second and
  third parameters are the `return` value and what `next(value)` sends back in.
- Spreading an infinite generator hangs. Always bound it first.
""",
    [
        tsx("ts_iterators-squares", "Yield a sequence",
            "Replace `____` with the generator `squares`, which yields `i * i` for `i` from 1 to `n`. The spread below collects them.",
            _P('''
import * as fs from "fs";
function* squares(n: number): Generator<number> {
  for (let i = 1; i <= n; i++) yield i * i;
}
const n = Number(fs.readFileSync(0, "utf8").trim());
console.log([...squares(n)].join(" ") || "(none)");
console.log([...squares(n)].reduce((a, b) => a + b, 0));
'''),
            ["function* squares(n: number): Generator<number> {\n  for (let i = 1; i <= n; i++) yield i * i;\n}"],
            [("4", "1 4 9 16\n30"), ("1", "1\n1"), ("0", "(none)\n0"), ("5", "1 4 9 16 25\n55")],
            hint="A generator is declared with function* and hands out values with yield — no array is built inside it."),
        tsx("ts_iterators-iterable", "Make a class iterable",
            "Replace `____` with a `[Symbol.iterator]` generator method on `Deck` that delegates to the private `#cards` array with `yield*`, so spreading a deck yields its cards.",
            _P('''
import * as fs from "fs";
class Deck {
  #cards: string[];
  constructor(cards: string[]) {
    this.#cards = cards;
  }
  *[Symbol.iterator](): Generator<string> {
    yield* this.#cards;
  }
}
const deck = new Deck(fs.readFileSync(0, "utf8").trim().split(/\\s+/));
console.log([...deck].join(","));
for (const card of deck) {
  console.log(card.toUpperCase());
}
'''),
            ["  *[Symbol.iterator](): Generator<string> {\n    yield* this.#cards;\n  }"],
            [("a k q", "a,k,q\nA\nK\nQ"), ("j", "j\nJ"), ("x y", "x,y\nX\nY")],
            hint="The method name is the computed key [Symbol.iterator], written as a generator with the * before it. yield* forwards every element."),
        _mchal("ts_iterators-challenge", "Lazy pipeline", "Medium",
               "Write an infinite `naturals()` generator, a `take(source, n)` that stops after `n` values, and a `filter(source, predicate)` — all generators. The input is `count divisor`. Print the first `count` natural numbers divisible by `divisor`, space-separated, then their sum. Nothing infinite may be materialised.",
               '''
const [count, divisor] = input.split(/\\s+/).map(Number);
function* naturals(): Generator<number> {
  let i = 1;
  while (true) yield i++;
}
function* filter<T>(source: Iterable<T>, predicate: (value: T) => boolean): Generator<T> {
  for (const value of source) {
    if (predicate(value)) yield value;
  }
}
function* take<T>(source: Iterable<T>, n: number): Generator<T> {
  let taken = 0;
  for (const value of source) {
    if (taken >= n) return;
    taken++;
    yield value;
  }
}
const picked = [...take(filter(naturals(), (x) => x % divisor === 0), count)];
console.log(picked.join(" ") || "(none)");
console.log(picked.reduce((a, b) => a + b, 0));
''',
               [("3 5", "5 10 15\n30"), ("1 1", "1\n1"),
                ("0 3", "(none)\n0"), ("4 2", "2 4 6 8\n20")],
               hint="take must `return` as soon as it has enough — that is what stops the infinite source. Compose them as take(filter(naturals(), ...), count)."),
    ],
    quiz=[
        {
            "question": "What happens the second time you iterate the SAME generator object?",
            "options": [
                "Nothing is produced — a generator object is exhausted after one pass",
                "It restarts from the beginning",
                "It throws a TypeError",
                "It yields the values in reverse",
            ],
            "answer": 0,
            "explanation": "The generator holds its own position. If callers may iterate more than once, hand back a function that creates a fresh generator each time.",
        },
        {
            "question": "Why does `take(naturals(), 4)` terminate even though `naturals()` never ends?",
            "options": [
                "Generators are lazy — naturals only computes a value when take asks, and take stops asking",
                "TypeScript detects the infinite loop and bounds it",
                "naturals() is evaluated eagerly up to a default limit",
                "The spread operator caps at 1000 elements",
            ],
            "answer": 0,
            "explanation": "Laziness is the point: production is driven entirely by consumption. Spreading `naturals()` directly, with no `take`, really would hang.",
        },
        {
            "question": "What does `yield*` do?",
            "options": [
                "Delegates to another iterable, yielding all of its values in place",
                "Yields an array of the remaining values",
                "Marks the generator as infinite",
                "Yields a value and immediately returns",
            ],
            "answer": 0,
            "explanation": "`yield* other` forwards every value from `other` as if written inline — the standard way to compose generators or expose an internal collection.",
        },
    ],
)

_concept(
    "ts_error_types", "TS: Runtime & Architecture",
    "Result Types & Typed Errors",
    "Making failure part of the return type instead of an invisible side channel.",
    "A thrown error is untyped — TypeScript types every `catch` binding as `unknown`, because any value can be thrown from anywhere. That is fine for genuinely exceptional situations, but for *expected* failure (bad input, a missing record) a `Result` type is stronger: `{ ok: true; value: T } | { ok: false; error: E }` is a discriminated union, so the compiler forces the caller to check `ok` before touching `value`. Custom `Error` subclasses give the thrown path the same discipline via `instanceof`.",
    "Java's checked exceptions try to make failure visible in the signature; `Result` does the same thing without a separate language mechanism, and the exhaustiveness check plays the role of the compiler demanding you handle the exception.",
    """
### `catch` gives you `unknown`
```ts
try {
  risky();
} catch (e) {
  e.message;              // Error: 'e' is of type 'unknown'
  if (e instanceof Error) e.message;   // ok after narrowing
}
```
Since TypeScript 4.4 this is the default under `strict`. Always narrow before
reading anything off a caught value.

### Custom error classes
```ts
class ParseError extends Error {
  line: number;
  constructor(line: number, message: string) {
    super(message);
    this.name = "ParseError";
    this.line = line;
  }
}

catch (e) {
  if (e instanceof ParseError) console.log(e.line);
}
```

### The Result type
```ts
type Result<T, E = string> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function parsePort(raw: string): Result<number> {
  const n = Number(raw);
  if (!Number.isInteger(n)) return { ok: false, error: "not an integer" };
  if (n < 1 || n > 65535) return { ok: false, error: "out of range" };
  return { ok: true, value: n };
}
```
It is just a discriminated union, so all the narrowing you already know applies:
```ts
const r = parsePort(input);
if (r.ok) console.log(r.value);   // value only exists on the ok branch
else console.log(r.error);
```

### Which to use
- **Throw** for bugs and unrecoverable states — a failed invariant, an
  impossible branch.
- **Return a Result** for failures the caller is expected to handle: parsing,
  validation, lookups that can legitimately miss.

### Watch out for
- Anything can be thrown, not just `Error`. `throw "oops"` is legal, so a
  `catch` that assumes `Error` will be wrong eventually.
- Extending `Error` needs `super(message)`; without it the stack and message are
  empty.
- Do not mix both for the same failure. Pick one per boundary and stay
  consistent.
""",
    [
        tsx("ts_error_types-result", "Return a Result",
            "Replace `____` with `parsePort`, returning a `Result<number>`: `not an integer` when the text is not a whole number, `out of range` outside 1–65535, otherwise the parsed value.",
            _P('''
import * as fs from "fs";
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
function parsePort(raw: string): Result<number> {
  const n = Number(raw);
  if (!Number.isInteger(n)) return { ok: false, error: "not an integer" };
  if (n < 1 || n > 65535) return { ok: false, error: "out of range" };
  return { ok: true, value: n };
}
const result = parsePort(fs.readFileSync(0, "utf8").trim());
console.log(result.ok ? "port " + result.value : "rejected: " + result.error);
'''),
            ['function parsePort(raw: string): Result<number> {\n  const n = Number(raw);\n  if (!Number.isInteger(n)) return { ok: false, error: "not an integer" };\n  if (n < 1 || n > 65535) return { ok: false, error: "out of range" };\n  return { ok: true, value: n };\n}'],
            [("8080", "port 8080"), ("abc", "rejected: not an integer"),
             ("0", "rejected: out of range"), ("70000", "rejected: out of range"),
             ("1.5", "rejected: not an integer")],
            hint="Return the failure shapes early, then the success shape. Number(\"abc\") is NaN, which Number.isInteger rejects."),
        tsx("ts_error_types-narrow", "Narrow an unknown catch",
            "`catch` binds `e` as `unknown`. Replace `____` with the catch body: report `ParseError on line N` when it is a `ParseError`, `error: <message>` for any other `Error`, and `unknown failure` otherwise.",
            _P('''
import * as fs from "fs";
class ParseError extends Error {
  line: number;
  constructor(line: number, message: string) {
    super(message);
    this.name = "ParseError";
    this.line = line;
  }
}
function run(kind: string): never {
  if (kind === "parse") throw new ParseError(7, "bad token");
  if (kind === "error") throw new Error("boom");
  throw "just a string";
}
try {
  run(fs.readFileSync(0, "utf8").trim());
} catch (e: unknown) {
  if (e instanceof ParseError) console.log("ParseError on line " + e.line);
  else if (e instanceof Error) console.log("error: " + e.message);
  else console.log("unknown failure");
}
'''),
            ['  if (e instanceof ParseError) console.log("ParseError on line " + e.line);\n  else if (e instanceof Error) console.log("error: " + e.message);\n  else console.log("unknown failure");'],
            [("parse", "ParseError on line 7"), ("error", "error: boom"),
             ("other", "unknown failure")],
            hint="Check the most specific class first — a ParseError is also an Error, so the order of the instanceof tests matters."),
        _mchal("ts_error_types-challenge", "Validate a batch", "Medium",
               "Define `Result<T, E = string>` and `parseAge(raw): Result<number>` rejecting non-integers (`not a number`) and anything outside 0–130 (`out of range`). The input is `n` then `n` lines. Print `ok <value>` or `bad <error>` for each, then a final line with the count of successes and the sum of their values, space-separated.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
function parseAge(raw: string): Result<number> {
  const value = Number(raw.trim());
  if (raw.trim().length === 0 || !Number.isInteger(value)) {
    return { ok: false, error: "not a number" };
  }
  if (value < 0 || value > 130) return { ok: false, error: "out of range" };
  return { ok: true, value };
}
let successes = 0;
let total = 0;
for (let i = 1; i <= n; i++) {
  const result = parseAge(lines[i]);
  if (result.ok) {
    successes++;
    total += result.value;
    console.log("ok " + result.value);
  } else {
    console.log("bad " + result.error);
  }
}
console.log(successes + " " + total);
''',
               [("3\n36\nabc\n200", "ok 36\nbad not a number\nbad out of range\n1 36"),
                ("1\n0", "ok 0\n1 0"),
                ("2\n130\n131", "ok 130\nbad out of range\n1 130"),
                ("2\n1.5\n-1", "bad not a number\nbad out of range\n0 0")],
               hint="Because Result is a discriminated union, `if (result.ok)` narrows to the branch that actually has `value` — no optional chaining needed."),
    ],
    quiz=[
        {
            "question": "Under `strict`, what type does `catch (e)` give `e`?",
            "options": ["unknown", "Error", "any", "never"],
            "answer": 0,
            "explanation": "Any value can be thrown, so TypeScript refuses to assume `Error`. You must narrow with `instanceof` (or a type guard) before reading properties.",
        },
        {
            "question": "What makes `Result<T, E>` enforce error handling?",
            "options": [
                "It is a discriminated union, so `value` is only reachable after checking `ok`",
                "The compiler tracks unhandled Results",
                "It throws if you ignore the error branch",
                "E defaults to string, which cannot be ignored",
            ],
            "answer": 0,
            "explanation": "The `ok` field is the discriminant. On the `false` branch there is no `value` property at all, so skipping the check is a type error rather than a runtime surprise.",
        },
        {
            "question": "When is throwing the better choice over returning a Result?",
            "options": [
                "For bugs and unrecoverable invariant violations the caller cannot sensibly handle",
                "Whenever the failure involves I/O",
                "Whenever the function is async",
                "Never — Result is always preferable",
            ],
            "answer": 0,
            "explanation": "Expected, recoverable failures belong in the return type. Genuinely exceptional situations — an impossible branch, a broken invariant — should unwind loudly.",
        },
    ],
)

_concept(
    "ts_async_patterns", "TS: Runtime & Architecture",
    "Promise Combinators & Concurrency",
    "Running async work in parallel with `Promise.all`, `allSettled`, `race` and `any` — and typing the results.",
    "`await` in a loop runs work one item at a time. The combinators run it concurrently and differ in how they treat failure: `all` rejects as soon as any input does (and infers a tuple of the resolved types), `allSettled` never rejects and gives a discriminated union per item, `race` settles with the first result either way, and `any` returns the first *success*. Choosing the right one is usually the whole performance story of an async function.",
    "`Promise.all` is `CompletableFuture.allOf` with real result types; `allSettled` is the version that collects failures instead of propagating the first. TypeScript infers a tuple from `all`, so destructuring keeps each element's own type.",
    """
### Sequential vs concurrent
```ts
// Sequential — total time is the SUM
for (const id of ids) results.push(await fetchOne(id));

// Concurrent — total time is the MAX
const results = await Promise.all(ids.map(fetchOne));
```

### `Promise.all` — all or nothing, tuple-typed
```ts
const [user, orders] = await Promise.all([fetchUser(), fetchOrders()]);
// user: User, orders: Order[]  — each keeps its own type
```
One rejection rejects the whole thing immediately; the other work keeps running
but its results are discarded.

### `Promise.allSettled` — collect everything
```ts
const settled = await Promise.allSettled([a(), b()]);
for (const r of settled) {
  if (r.status === "fulfilled") console.log(r.value);
  else console.log(r.reason);
}
```
`PromiseSettledResult<T>` is a discriminated union on `status` — the same
narrowing you use everywhere else.

### `race` and `any`
```ts
await Promise.race([work(), timeout(1000)]);   // first to SETTLE, success or not
await Promise.any([mirrorA(), mirrorB()]);     // first to SUCCEED
```
`race` is the timeout pattern. `any` rejects with an `AggregateError` only when
every input fails.

### Typing an async function
```ts
async function load(id: string): Promise<User> { /* ... */ }
```
An `async` function always returns a promise; `Awaited<T>` unwraps nested ones.

### Watch out for
- Creating promises inside `Promise.all(ids.map(fetchOne))` starts them all at
  once. `ids.map(async (id) => await fetchOne(id))` does the same thing — the
  `await` inside does not serialise them.
- An unhandled rejection from work you abandoned (after `race`) still fires.
- `forEach` does not await. Use `for...of` with `await`, or `map` + `all`.
""",
    [
        tsx("ts_async_patterns-all", "Run them concurrently",
            "`delayed` resolves after a tick with `value * 2`. Replace `____` with a single `await` that runs every number concurrently with `Promise.all` and stores the doubled results in `doubled`.",
            _P('''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
function delayed(value: number): Promise<number> {
  return new Promise((resolve) => setTimeout(() => resolve(value * 2), 1));
}
const doubled = await Promise.all(nums.map(delayed));
console.log(doubled.join(" "));
console.log(doubled.reduce((a, b) => a + b, 0));
'''),
            ["const doubled = await Promise.all(nums.map(delayed));"],
            [("1 2 3", "2 4 6\n12"), ("5", "10\n10"), ("0 -1", "0 -2\n-2")],
            hint="nums.map(delayed) creates every promise immediately; Promise.all waits for all of them and preserves the input order."),
        tsx("ts_async_patterns-settled", "Collect successes and failures",
            "Half of these jobs reject. Replace `____` with the loop over the settled results: push `r.value` onto `ok` when the status is `fulfilled`, and `String(r.reason)` onto `failed` otherwise.",
            _P('''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);
function job(value: number): Promise<number> {
  return value < 0 ? Promise.reject("negative") : Promise.resolve(value * 10);
}
const settled = await Promise.allSettled(nums.map(job));
const ok: number[] = [];
const failed: string[] = [];
for (const r of settled) {
  if (r.status === "fulfilled") ok.push(r.value);
  else failed.push(String(r.reason));
}
console.log(ok.join(" ") || "(none)");
console.log(failed.length);
'''),
            ['for (const r of settled) {\n  if (r.status === "fulfilled") ok.push(r.value);\n  else failed.push(String(r.reason));\n}'],
            [("1 -2 3", "10 30\n1"), ("-1 -2", "(none)\n2"), ("4", "40\n0")],
            hint="PromiseSettledResult is a discriminated union on `status` — the fulfilled branch has `value`, the rejected branch has `reason`."),
        _mchal("ts_async_patterns-challenge", "Concurrent lookup with a timeout", "Medium",
               "`lookup(id)` resolves with `id*id` after `id` milliseconds, but rejects for a negative id. The input is a line of ids. Run them all concurrently, racing each against a 50 ms timeout that rejects with `timeout`. Print `id=result`, `id=failed` or `id=timeout` for each in input order, then the number that succeeded.",
               '''
const ids = input.split(/\\s+/).map(Number);
function lookup(id: number): Promise<number> {
  return new Promise((resolve, reject) => {
    if (id < 0) reject(new Error("bad id"));
    else setTimeout(() => resolve(id * id), id);
  });
}
function timeoutAfter(ms: number): Promise<never> {
  return new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), ms));
}
const settled = await Promise.allSettled(
  ids.map((id) => Promise.race([lookup(id), timeoutAfter(50)])),
);
let succeeded = 0;
settled.forEach((result, i) => {
  if (result.status === "fulfilled") {
    succeeded++;
    console.log(ids[i] + "=" + result.value);
  } else {
    const message = result.reason instanceof Error ? result.reason.message : String(result.reason);
    console.log(ids[i] + "=" + (message === "timeout" ? "timeout" : "failed"));
  }
});
console.log(succeeded);
''',
               [("2 3 -1", "2=4\n3=9\n-1=failed\n2"),
                ("1", "1=1\n1"),
                ("-5 -6", "-5=failed\n-6=failed\n0"),
                ("0 4", "0=0\n4=16\n2")],
               hint="Race each lookup against the timeout, then wrap the whole array in allSettled so one rejection does not lose the other results."),
    ],
    quiz=[
        {
            "question": "What is the total time of `await Promise.all(ids.map(fetchOne))` versus awaiting inside a loop?",
            "options": [
                "The maximum of the individual times, versus the sum of them",
                "The same — Promise.all is just syntax",
                "The sum, versus the maximum",
                "Depends on the number of CPU cores",
            ],
            "answer": 0,
            "explanation": "`.map` starts every promise before `all` waits, so they overlap. Awaiting inside a loop starts each one only after the previous resolves.",
        },
        {
            "question": "How does `Promise.allSettled` differ from `Promise.all` on failure?",
            "options": [
                "It never rejects; every entry becomes a fulfilled/rejected record you inspect",
                "It retries the failed promises",
                "It rejects only if every promise fails",
                "It resolves with the successful values and silently drops failures",
            ],
            "answer": 0,
            "explanation": "`allSettled` always resolves with one `PromiseSettledResult` per input. That last behaviour — dropping failures — is what `Promise.any` approximates, and it is not what allSettled does.",
        },
        {
            "question": "What is the difference between `Promise.race` and `Promise.any`?",
            "options": [
                "race settles with the first promise to settle either way; any waits for the first SUCCESS",
                "any is the async version of race",
                "race rejects only on timeout",
                "They are aliases",
            ],
            "answer": 0,
            "explanation": "`race` is the timeout pattern precisely because an early rejection wins. `any` ignores rejections until all of them fail, then rejects with an AggregateError.",
        },
    ],
)

_concept(
    "ts_declaration_files", "TS: Runtime & Architecture",
    "Declaration Files & Ambient Types",
    "Describing code that exists at runtime but has no TypeScript source.",
    "A `.d.ts` file contains types and no implementation — it tells the compiler what already exists. `declare` introduces an ambient binding (a global from a script tag, a value provided by the host), `declare module` types a JavaScript package with no bundled types, and `declare global` reaches into the global scope from inside a module. Every published TypeScript library ships these; `declaration: true` generates them from your source. Nothing in a `.d.ts` is emitted, so a wrong declaration is a silent lie exactly like a wrong type predicate.",
    "This is the role Java's interfaces-plus-jar-metadata plays automatically: since JavaScript carries no type information, the shape has to be described separately and kept in sync by hand.",
    """
### Ambient declarations
```ts
// globals.d.ts
declare const BUILD_VERSION: string;
declare function reportError(message: string): void;
```
Now both are usable everywhere with no import — the promise is that the runtime
really does provide them.

### Typing an untyped package
```ts
// vendor.d.ts
declare module "legacy-chart" {
  export interface Options { width: number; height: number }
  export function render(el: unknown, options: Options): void;
}
```
A bare `declare module "name";` with no body types the whole package as `any` —
a quick unblock, and a permanent hole.

### `declare global` from inside a module
```ts
export {};   // makes this file a module

declare global {
  interface Window { analytics?: { track(event: string): void } }
}
```
The `export {}` matters: without it the file is a script and `declare global`
is an error.

### Module augmentation
```ts
import "express";

declare module "express" {
  interface Request { userId?: string }
}
```
Interfaces merge, so this ADDS a property to an existing type rather than
replacing it — one of the few places where `interface` beats `type`.

### Generating your own
```jsonc
{ "compilerOptions": { "declaration": true, "declarationMap": true } }
```
The compiler emits a `.d.ts` beside each output file, which is what consumers of
your package actually type-check against.

### Watch out for
- `.d.ts` files are never executed. Declaring something that does not exist
  produces a runtime `ReferenceError`.
- `declare` on a value in a normal `.ts` file works too, but only for things the
  environment genuinely supplies.
- Prefer `unknown` over `any` when describing a shape you do not fully know —
  it keeps the checking at the boundary.
""",
    [
        tsx("ts_declaration_files-ambient", "Use an ambient global",
            "`BUILD_VERSION` and `reportError` are declared ambiently — the runtime supplies them just below. Replace `____` with the declarations, then the code that follows can use both without importing anything.",
            _P('''
import * as fs from "fs";
declare const BUILD_VERSION: string;
declare function reportError(message: string): void;
(globalThis as Record<string, unknown>).BUILD_VERSION = "1.4.2";
(globalThis as Record<string, unknown>).reportError = (message: string) => {
  console.log("reported: " + message);
};
const input = fs.readFileSync(0, "utf8").trim();
console.log(BUILD_VERSION);
reportError(input);
'''),
            ["declare const BUILD_VERSION: string;\ndeclare function reportError(message: string): void;"],
            [("disk full", "1.4.2\nreported: disk full"),
             ("oops", "1.4.2\nreported: oops")],
            hint="Two ambient declarations, one for a const and one for a function. They describe what the host provides; the assignments below are that host."),
        tsx("ts_declaration_files-augment", "Augment an existing interface",
            "Interfaces merge across declarations. Replace `____` with a second `interface Session` declaration adding an optional `role?: string`, so the object below can carry it while keeping the original fields.",
            _P('''
import * as fs from "fs";
interface Session {
  id: string;
  createdAt: number;
}
interface Session {
  role?: string;
}
const [id, role] = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
const session: Session = { id, createdAt: 0, role: role === "-" ? undefined : role };
console.log(session.id + " " + session.createdAt);
console.log(session.role ?? "(no role)");
'''),
            ["interface Session {\n  role?: string;\n}"],
            [("s1 admin", "s1 0\nadmin"), ("s2 -", "s2 0\n(no role)"),
             ("abc user", "abc 0\nuser")],
            hint="Declaring the same interface name twice merges the members — this is exactly how module augmentation adds a field to a library type."),
        _mchal("ts_declaration_files-challenge", "Typed host bridge", "Medium",
               "A host environment provides a global `host` object with `version: string` and `emit(name: string, payload: string): void`. Declare it ambiently, install a runtime implementation on `globalThis` that logs `name:payload`, then read `n` and `n` lines of `name payload` and emit each. Print the host version first, and the number of events emitted last.",
               '''
const lines = input.split("\\n");
const n = Number(lines[0]);
interface Host {
  version: string;
  emit(name: string, payload: string): void;
}
declare const host: Host;
let emitted = 0;
(globalThis as Record<string, unknown>).host = {
  version: "2.0.0",
  emit(name: string, payload: string) {
    emitted++;
    console.log(name + ":" + payload);
  },
} satisfies Host;
console.log(host.version);
for (let i = 1; i <= n; i++) {
  const [name, payload] = lines[i].trim().split(/\\s+/);
  host.emit(name, payload);
}
console.log(emitted);
''',
               [("2\nclick a\nkey b", "2.0.0\nclick:a\nkey:b\n2"),
                ("1\nscroll x", "2.0.0\nscroll:x\n1"),
                ("3\na 1\nb 2\nc 3", "2.0.0\na:1\nb:2\nc:3\n3")],
               hint="`declare const host: Host` promises the binding exists; the assignment to globalThis is the runtime keeping that promise. `satisfies Host` checks the implementation matches."),
    ],
    quiz=[
        {
            "question": "What does a `.d.ts` file emit at build time?",
            "options": [
                "Nothing — it only describes types the runtime is assumed to provide",
                "A JavaScript stub for each declaration",
                "A module that must be imported",
                "A runtime validation shim",
            ],
            "answer": 0,
            "explanation": "Declaration files are pure description. If you declare something the runtime does not actually have, you get a ReferenceError with no compile-time warning.",
        },
        {
            "question": "Why does a file using `declare global` usually need `export {};`?",
            "options": [
                "It forces the file to be a module, which `declare global` requires",
                "It re-exports the globals",
                "It prevents the globals from leaking",
                "It is a convention with no effect",
            ],
            "answer": 0,
            "explanation": "A file with no imports or exports is a script, and its top-level declarations are already global — so `declare global` is only meaningful (and only legal) inside a module.",
        },
        {
            "question": "Why must module augmentation use `interface` rather than `type`?",
            "options": [
                "Interfaces merge across declarations; type aliases cannot be reopened",
                "type is not allowed inside declare module",
                "Interfaces are erased and types are not",
                "type aliases cannot describe objects",
            ],
            "answer": 0,
            "explanation": "Declaration merging is an interface-only feature, and it is what lets you add a field to a library's existing type instead of shadowing it.",
        },
    ],
)

_concept(
    "ts_ds_generics", "TS: Runtime & Architecture",
    "Generic Data Structures",
    "Implementing reusable containers — stacks, queues, linked lists — that keep their element type.",
    "A container is where generics earn their keep: one implementation, checked for every element type it is used with. The design questions are the ones that recur everywhere — does an empty pop return `undefined` or throw, is the class iterable, should the internals be `#private` — and getting them right here is what makes `Stack<Order>` as pleasant to use as `number[]`. Adding `[Symbol.iterator]` makes your structure work with `for...of` and spread exactly like a built-in.",
    "Directly comparable to writing `class Stack<T>` in Java, with two differences: no boxing (a `Stack<number>` really holds numbers), and no `Comparable` bound — ordering is supplied as a comparator function instead.",
    """
### A generic stack
```ts
class Stack<T> {
  #items: T[] = [];

  push(item: T): void { this.#items.push(item); }
  pop(): T | undefined { return this.#items.pop(); }
  peek(): T | undefined { return this.#items.at(-1); }
  get size(): number { return this.#items.length; }
  get isEmpty(): boolean { return this.#items.length === 0; }
}

const s = new Stack<string>();
s.push("a");
s.pop();          // string | undefined
```
`T | undefined` forces the caller to handle "empty" — better than a silent
`undefined` typed as `T`.

### `#private` is genuinely private
```ts
class Counter {
  #count = 0;         // not reachable from outside, even at runtime
  private legacy = 0; // compile-time only; visible in JS
}
```
Prefer `#` for anything that must not be touched.

### Make it iterable
```ts
class Queue<T> {
  #items: T[] = [];
  enqueue(item: T): void { this.#items.push(item); }
  dequeue(): T | undefined { return this.#items.shift(); }
  *[Symbol.iterator](): Generator<T> { yield* this.#items; }
}

[...new Queue<number>()];   // works like any built-in
```

### Ordering by comparator, not by interface
```ts
class SortedList<T> {
  #items: T[] = [];
  #compare: (a: T, b: T) => number;

  constructor(compare: (a: T, b: T) => number) {
    this.#compare = compare;
  }

  add(item: T): void {
    this.#items.push(item);
    this.#items.sort(this.#compare);
  }
}
new SortedList<number>((a, b) => a - b);
```
(Constructor *parameter properties* — `constructor(private compare: ...)` — are
a TypeScript-only shorthand that requires a real compile step, so this track
always writes the field out explicitly.)

### Watch out for
- `Array.prototype.shift` is O(n). A real queue keeps a head index or a linked
  list.
- Do not annotate `Stack<any>` to silence an error — you lose every guarantee
  the class exists to provide.
- A generic class cannot inspect `T` at runtime; anything type-dependent must
  arrive as a function parameter.
""",
    [
        tsx("ts_ds_generics-stack", "A generic stack",
            "Replace `____` with the members of `Stack<T>`: a `#items` array, `push`, a `pop` returning `T | undefined`, and a `size` getter.",
            _P('''
import * as fs from "fs";
class Stack<T> {
  #items: T[] = [];
  push(item: T): void {
    this.#items.push(item);
  }
  pop(): T | undefined {
    return this.#items.pop();
  }
  get size(): number {
    return this.#items.length;
  }
}
const stack = new Stack<string>();
for (const token of fs.readFileSync(0, "utf8").trim().split(/\\s+/)) {
  stack.push(token);
}
console.log(stack.size);
console.log(stack.pop() ?? "(empty)");
console.log(stack.pop() ?? "(empty)");
'''),
            ["  #items: T[] = [];\n  push(item: T): void {\n    this.#items.push(item);\n  }\n  pop(): T | undefined {\n    return this.#items.pop();\n  }\n  get size(): number {\n    return this.#items.length;\n  }"],
            [("a b c", "3\nc\nb"), ("only", "1\nonly\n(empty)"),
             ("x y", "2\ny\nx")],
            hint="pop() returns T | undefined, which is why the caller needs ?? \"(empty)\". The #items field is private at runtime, not just to the compiler."),
        tsx("ts_ds_generics-queue", "An iterable queue",
            "Replace `____` with the `[Symbol.iterator]` generator method on `Queue<T>` so spreading and `for...of` walk the queued items front-to-back, delegating to `#items` with `yield*`.",
            _P('''
import * as fs from "fs";
class Queue<T> {
  #items: T[] = [];
  enqueue(item: T): void {
    this.#items.push(item);
  }
  dequeue(): T | undefined {
    return this.#items.shift();
  }
  *[Symbol.iterator](): Generator<T> {
    yield* this.#items;
  }
}
const queue = new Queue<number>();
for (const n of fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number)) {
  queue.enqueue(n);
}
console.log(queue.dequeue() ?? "(empty)");
console.log([...queue].join(" ") || "(empty)");
'''),
            ["  *[Symbol.iterator](): Generator<T> {\n    yield* this.#items;\n  }"],
            [("1 2 3", "1\n2 3"), ("9", "9\n(empty)"), ("4 5", "4\n5")],
            hint="One generator method keyed by [Symbol.iterator]; yield* forwards the backing array's elements."),
        _mchal("ts_ds_generics-challenge", "Generic ring buffer", "Medium",
               "Write `RingBuffer<T>` with a fixed capacity: `push` appends and drops the OLDEST item once full, `toArray()` returns the contents oldest-first, and it is iterable. The input is `capacity` then a line of values. Push each value, then print the buffer space-separated (or `(empty)`), its length, and whether it is at capacity.",
               '''
const lines = input.split("\\n");
const capacity = Number(lines[0]);
const values = lines[1] === undefined ? [] : lines[1].trim().split(/\\s+/).filter((v) => v.length > 0);
class RingBuffer<T> {
  #items: T[] = [];
  #capacity: number;
  constructor(capacity: number) {
    this.#capacity = capacity;
  }
  push(item: T): void {
    this.#items.push(item);
    if (this.#items.length > this.#capacity) this.#items.shift();
  }
  toArray(): T[] {
    return [...this.#items];
  }
  get length(): number {
    return this.#items.length;
  }
  get isFull(): boolean {
    return this.#items.length === this.#capacity;
  }
  *[Symbol.iterator](): Generator<T> {
    yield* this.#items;
  }
}
const buffer = new RingBuffer<string>(capacity);
for (const value of values) buffer.push(value);
console.log([...buffer].join(" ") || "(empty)");
console.log(buffer.length);
console.log(buffer.isFull);
''',
               [("3\na b c d e", "c d e\n3\ntrue"),
                ("5\nx y", "x y\n2\nfalse"),
                ("1\np q", "q\n1\ntrue"),
                ("2\nz", "z\n1\nfalse")],
               hint="Push then trim: once the array is longer than the capacity, shift the oldest off the front. toArray copies so callers cannot mutate the internals."),
    ],
    quiz=[
        {
            "question": "Why should `pop()` be typed `T | undefined` rather than `T`?",
            "options": [
                "An empty stack really does return undefined, and the type should say so",
                "Generic methods cannot return a bare T",
                "It makes the method faster",
                "undefined is required for iteration to work",
            ],
            "answer": 0,
            "explanation": "Typing it as `T` is a lie that hands the caller an `undefined` the compiler swears is a real value — precisely the class of bug the type system exists to prevent.",
        },
        {
            "question": "What is the difference between `#items` and `private items`?",
            "options": [
                "`#items` is private at runtime too; `private` is erased and the field is visible in JavaScript",
                "They are identical",
                "`private` works on methods only",
                "`#items` cannot be used in a generic class",
            ],
            "answer": 0,
            "explanation": "`#` is a real JavaScript private field enforced by the engine. `private` is a compile-time-only marker, so anything ignoring the types can still reach the value.",
        },
        {
            "question": "Why does a generic `SortedList<T>` take a comparator instead of constraining `T extends Comparable`?",
            "options": [
                "T is erased at runtime, so ordering must be supplied as a function the class can call",
                "Comparable does not exist in the TypeScript standard library",
                "Constraints cannot be used on classes",
                "Comparators are faster than interface dispatch",
            ],
            "answer": 0,
            "explanation": "Both parts are true — there is no built-in Comparable — but the underlying reason is erasure: nothing about `T` survives to run, so the behaviour has to be passed in as a value.",
        },
    ],
)

_concept(
    "ts_tsconfig", "TS: Runtime & Architecture",
    "Compiler Strictness & tsconfig",
    "The options that decide how much the compiler actually checks.",
    "`tsconfig.json` is where a project chooses how strict it is. `strict: true` turns on a family of flags — chief among them `strictNullChecks`, which is the difference between `string` meaning 'a string' and 'a string, or null, or undefined'. Additional opt-in flags (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`) close holes that `strict` leaves open. Knowing which flag causes an error is most of the skill of maintaining a large codebase.",
    "The nearest analogue is a build's warning level plus a null-analysis tool. The important difference is that these flags change what the type system *means*, so turning one on can surface hundreds of genuine latent bugs at once.",
    """
### `strict: true` is a bundle
Enabling it turns on, among others:

| Flag | What it catches |
| --- | --- |
| `strictNullChecks` | `null`/`undefined` used where a value was assumed |
| `noImplicitAny` | Parameters and fields with no inferable type |
| `strictFunctionTypes` | Unsound parameter variance in function assignment |
| `strictPropertyInitialization` | Class fields never assigned in the constructor |
| `useUnknownInCatchVariables` | `catch (e)` typed as `unknown`, not `any` |

### `strictNullChecks` changes what a type means
```ts
// off:  string includes null and undefined
// on:   string is a string; write string | null when it can be absent
function len(s: string | null): number {
  return s.length;        // Error until you narrow
}
```
This one flag is why the rest of the type system is trustworthy. Turning it off
in a mature codebase is almost always the wrong trade.

### Useful flags NOT included in `strict`
```jsonc
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,   // arr[i] is T | undefined
    "exactOptionalPropertyTypes": true, // { a?: string } rejects { a: undefined }
    "noImplicitOverride": true,         // subclass overrides must say `override`
    "noFallthroughCasesInSwitch": true,
    "verbatimModuleSyntax": true        // import type stays explicit
  }
}
```
`noUncheckedIndexedAccess` is the highest-value of these and the most disruptive
— every array index becomes possibly-undefined, which is the truth.

### Targets and modules
```jsonc
{ "target": "ES2022", "module": "NodeNext", "lib": ["ES2022"] }
```
`target` sets the output syntax level, `lib` the APIs assumed present. Using
`Array.prototype.at` with `lib: ES2020` is an error, not a runtime surprise.

### Watch out for
- `strict` grows over time. A new compiler version can add a flag to the bundle
  and surface new errors — pin your TypeScript version in CI.
- `skipLibCheck: true` is standard practice; it skips checking `.d.ts` files
  from dependencies, not your own code.
- Suppressing with `@ts-ignore` hides everything on the next line. Prefer
  `@ts-expect-error`, which itself errors once the problem is fixed.
""",
    [
        tsx("ts_tsconfig-nullchecks", "Handle the null the flag exposes",
            "Under `strictNullChecks`, `string | null` cannot be used as a string until you narrow it. Replace `____` with the body of `describe`: return `(missing)` for `null` and the uppercased text otherwise.",
            _P('''
import * as fs from "fs";
function describe(value: string | null): string {
  if (value === null) return "(missing)";
  return value.toUpperCase();
}
const raw = fs.readFileSync(0, "utf8").trim();
const value: string | null = raw === "-" ? null : raw;
console.log(describe(value));
console.log(describe(null));
'''),
            ['  if (value === null) return "(missing)";\n  return value.toUpperCase();'],
            [("hello", "HELLO\n(missing)"), ("-", "(missing)\n(missing)"),
             ("abc", "ABC\n(missing)")],
            hint="Narrow first with an early return; after the guard, TypeScript knows the value is a plain string."),
        tsx("ts_tsconfig-indexed", "Treat an index as possibly missing",
            "`noUncheckedIndexedAccess` makes `arr[i]` have type `T | undefined`. Replace `____` with the body of `at`, which returns the element or the supplied fallback when the index is out of range.",
            _P('''
import * as fs from "fs";
function at<T>(items: T[], index: number, fallback: T): T {
  const value: T | undefined = items[index];
  return value === undefined ? fallback : value;
}
const [indexRaw, ...words] = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
console.log(at(words, Number(indexRaw), "(none)"));
console.log(at(words, 99, "(none)"));
'''),
            ["  const value: T | undefined = items[index];\n  return value === undefined ? fallback : value;"],
            [("0 a b c", "a\n(none)"), ("2 a b c", "c\n(none)"),
             ("5 a b", "(none)\n(none)"), ("1 x y", "y\n(none)")],
            hint="Read the element into a `T | undefined` first, then decide — an out-of-range index gives undefined at runtime whether the flag is on or not."),
        _mchal("ts_tsconfig-challenge", "Strict settings parser", "Medium",
               "Parse lines of `flag=on|off` into a settings object, ignoring unknown flags. Known flags are `strictNullChecks`, `noImplicitAny`, `noUncheckedIndexedAccess`, all defaulting to off. Handle every lookup as possibly-missing. Print each known flag as `flag=on|off` in alphabetical order, then the number of flags enabled, then the number of unknown lines ignored.",
               '''
const lines = input.split("\\n").filter((line) => line.trim().length > 0);
const known = ["noImplicitAny", "noUncheckedIndexedAccess", "strictNullChecks"] as const;
type Flag = (typeof known)[number];
const settings: Record<Flag, boolean> = {
  noImplicitAny: false,
  noUncheckedIndexedAccess: false,
  strictNullChecks: false,
};
let ignored = 0;
for (const line of lines) {
  const [name, value] = line.split("=");
  const flag = name?.trim();
  if (flag === undefined || !(known as readonly string[]).includes(flag)) {
    ignored++;
    continue;
  }
  settings[flag as Flag] = value?.trim() === "on";
}
for (const flag of [...known].sort()) {
  console.log(flag + "=" + (settings[flag] ? "on" : "off"));
}
console.log(Object.values(settings).filter(Boolean).length);
console.log(ignored);
''',
               [("strictNullChecks=on\nnoImplicitAny=on",
                 "noImplicitAny=on\nnoUncheckedIndexedAccess=off\nstrictNullChecks=on\n2\n0"),
                ("bogus=on", "noImplicitAny=off\nnoUncheckedIndexedAccess=off\nstrictNullChecks=off\n0\n1"),
                ("strictNullChecks=off", "noImplicitAny=off\nnoUncheckedIndexedAccess=off\nstrictNullChecks=off\n0\n0"),
                ("noUncheckedIndexedAccess=on\nx=y\nz=on",
                 "noImplicitAny=off\nnoUncheckedIndexedAccess=on\nstrictNullChecks=off\n1\n2")],
               hint="Derive the Flag union from the `as const` array so the settings record cannot drift from it. Treat both split halves as possibly-undefined."),
    ],
    quiz=[
        {
            "question": "What does `strictNullChecks` change about the meaning of `string`?",
            "options": [
                "With it on, `string` excludes null and undefined — absence must be written explicitly",
                "It makes string comparisons case-sensitive",
                "It forbids empty strings",
                "It only affects function parameters",
            ],
            "answer": 0,
            "explanation": "With the flag off, every type silently includes null and undefined, so no annotation can be trusted. It is the flag the rest of the type system's usefulness rests on.",
        },
        {
            "question": "What does `noUncheckedIndexedAccess` do?",
            "options": [
                "Gives `arr[i]` the type `T | undefined`, reflecting that the index may be out of range",
                "Throws at runtime on an out-of-range index",
                "Forbids index signatures",
                "Requires every array access to use .at()",
            ],
            "answer": 0,
            "explanation": "It tells the truth about indexing. It is not part of `strict`, and it is usually the most disruptive flag to enable in an existing codebase — and the most valuable.",
        },
        {
            "question": "Why prefer `@ts-expect-error` over `@ts-ignore`?",
            "options": [
                "It errors once the underlying problem is fixed, so the suppression cannot outlive its reason",
                "It suppresses fewer error categories",
                "It is checked at runtime",
                "It only works in test files",
            ],
            "answer": 0,
            "explanation": "`@ts-ignore` silently hides whatever the next line does forever. `@ts-expect-error` fails when there is no longer an error, forcing the comment to be removed.",
        },
    ],
)


# TSM_REGISTER
CONCEPTS.update(TSM_CONCEPTS)
CATEGORY.update(TSM_CATEGORY)
LESSONS.update(TSM_LESSONS)
EXERCISES.update(TSM_EXERCISES)
