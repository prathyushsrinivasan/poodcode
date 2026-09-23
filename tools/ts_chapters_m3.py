# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New TypeScript chapters for Mastery Month 3 — The type system.
#
#   week 13  ts_function_types   call / construct signatures, `this`, and when
#                                one function type is assignable to another
#   week 13  ts_type_testing     Expect<Equal<…>>, @ts-expect-error — how to
#                                test a type, before months 4-5 grade types
#
# Built with ts_chapter_kit.py's `_chapter`; every printed output and compiler
# message is computed (python tools/gen_ts_outputs.py). Code is written in raw
# strings so a TypeScript "\n" stays a backslash-n.
# ---------------------------------------------------------------------------

_chapter(
    "ts_function_types", "TS: Functions & Types",
    "Function Types in Depth",
    "Call and construct signatures, typing `this`, and the rules for when one function type fits another.",
    "A function's type is its signature: what it accepts and what it gives back. TypeScript can describe a plain callback, a function that also carries properties, a class you call with `new`, and a function that needs a particular `this`. Knowing when one function type is assignable to another — fewer parameters is fine, a narrower parameter is not — is what makes callbacks, handlers and plugin tables type-safe.",
    "Java needs a functional interface for every shape of callback. Here any matching signature fits structurally, a constructor is just a `new (…) => T` signature, and parameter types are checked contravariantly for function-typed properties (bivariantly for methods — a deliberate hole this chapter shows).",
    why=r"""
Functions are values in TypeScript. You store them in tables, pass them to other
functions, hand them to event emitters and receive them back from factories.
Every one of those moves asks the compiler the same question: *does this
function fit that slot?*

Answer it wrongly and you get the bugs this chapter is about: a handler that is
called with an argument it never expected, a method that loses its `this` when
passed around, a constructor called without `new`. A function *type* is how you
write the slot down precisely enough for the compiler to answer for you.
""",
    idea=r"""
**Four kinds of signature.** A function type can be written in four ways, and
they cover everything you will meet:

```ts
type Parse = (text: string) => number;            // call signature (arrow form)
type Labelled = { (x: number): string; label: string }; // callable object with a property
type Maker = new (size: number) => Shape;         // construct signature — called with `new`
function show(this: Account, prefix: string) {}   // a `this` parameter (erased at runtime)
```

**When does one function fit another?** Suppose a slot expects
`(value: number, index: number) => void`.

- **Fewer parameters is fine.** `(value) => …` fits: extra arguments are simply
  ignored. That is why `xs.forEach((x) => …)` compiles although `forEach`
  passes three arguments.
- **More *required* parameters is not.** `(value, index, extra) => …` would be
  called without `extra`.
- **Parameters are checked contravariantly.** A function that only handles
  `"click"` cannot sit in a slot that will pass it any `string`. With `strict`
  on (`strictFunctionTypes`) this is an error — *except* for methods declared
  with method syntax in an interface, which are checked bivariantly for
  historical reasons.
- **Return types are covariant**, and a `void` slot accepts any return type —
  the value is just not used.

**`this` is a parameter too.** Writing `this: Account` first in the parameter
list costs nothing at runtime — it is erased — but every call is now checked:
calling the function detached, where `this` would be `undefined`, is a compile
error instead of a crash.

**Reading function types back.** `ReturnType<typeof f>` and
`Parameters<typeof f>` turn a function's signature into types you can reuse,
so a factory stays the single source of truth for what it builds. You will
rebuild both yourself with `infer` in week 21.
""",
    examples=[
        ("A function that carries a property",
         r"""
type Formatter = {
  (value: number): string;
  label: string;
};

const money = (value: number) => "$" + value.toFixed(2);
money.label = "money";

const percent = (value: number) => (value * 100).toFixed(0) + "%";
percent.label = "percent";

const formatters: Formatter[] = [money, percent];
for (const f of formatters) {
  console.log(f.label + ": " + f(0.256));
}
""", [""],
         "Assigning `money.label` right after a `const` arrow function is recognised by the compiler: `money`'s type becomes the call signature *plus* a `label: string` property, so it fits `Formatter` with no cast."),
        ("A construct signature",
         r"""
interface Shape {
  area(): number;
}
type ShapeMaker = new (size: number) => Shape;

class Square implements Shape {
  size: number;
  constructor(size: number) {
    this.size = size;
  }
  area() {
    return this.size * this.size;
  }
}
class Circle implements Shape {
  radius: number;
  constructor(radius: number) {
    this.radius = radius;
  }
  area() {
    return Math.round(Math.PI * this.radius * this.radius);
  }
}

function build(maker: ShapeMaker, sizes: number[]): Shape[] {
  return sizes.map((size) => new maker(size));
}

for (const shape of [...build(Square, [2, 3]), ...build(Circle, [1])]) {
  console.log(shape.area());
}
""", [""],
         "`build` does not care which class it gets — only that calling it with `new` and a number produces a `Shape`. A class *is* a value with a construct signature."),
        ("Fewer parameters fit; `void` accepts anything",
         r"""
type Visit = (value: number, index: number) => void;

function each(xs: number[], visit: Visit): void {
  for (const [index, value] of xs.entries()) visit(value, index);
}

each([30, 10, 20], (value, index) => console.log(index + ": " + value));

const seen: number[] = [];
each([30, 10, 20], (value) => seen.push(value)); // one parameter, returns a number
console.log(seen.join(","));
""", [""],
         "The second callback takes one parameter where two are offered, and returns `push`'s number where `void` is expected. Both are fine: nothing is ever missing, and a `void` result is simply not used."),
        ("A `this` parameter",
         r"""
interface Account {
  owner: string;
  balance: number;
}

function describe(this: Account, prefix: string): string {
  return prefix + " " + this.owner + " has " + this.balance;
}

const ana = { owner: "Ana", balance: 30, describe };
console.log(ana.describe("->"));
console.log(describe.call({ owner: "Bo", balance: 5 }, "*"));
""", [""],
         "`this: Account` is not a real parameter — `describe` still takes one argument. It tells the compiler what `this` must be at every call site, and `.call` supplies it explicitly."),
        ("Types read back from a function",
         r"""
function parsePoint(text: string, separator = ",") {
  const [x = 0, y = 0] = text.split(separator).map(Number);
  return { x, y };
}

type Point = ReturnType<typeof parsePoint>;
type ParseArgs = Parameters<typeof parsePoint>;

const args: ParseArgs = ["3;4", ";"];
const p: Point = parsePoint(...args);
console.log(p.x + p.y);
""", [""],
         "`Point` is `{ x: number; y: number }` and `ParseArgs` is `[text: string, separator?: string]`, both derived — change `parsePoint` and they follow. `typeof` is needed because `parsePoint` is a value, and these utilities take types."),
    ],
    errors=[
        (2345, r"""
type Visit = (value: number) => void;
function each(xs: number[], visit: Visit) {
  for (const x of xs) visit(x);
}
each([1, 2], (value: number, index: number) => console.log(value, index));
""", "The callback demands an `index` that `each` never passes. Fewer parameters are always safe; more *required* ones never are."),
        (2322, r"""
type Handler = (event: string) => void;
const onlyClicks = (event: "click") => console.log(event);
const handler: Handler = onlyClicks;
""", "A `Handler` will be called with *any* string, and `onlyClicks` only handles one. Parameter types flow the opposite way to values — this is contravariance, enforced by `strictFunctionTypes`."),
        (2684, r"""
interface Account {
  owner: string;
}
function greet(this: Account) {
  return "hi " + this.owner;
}
console.log(greet());
""", "Called on its own, `greet` would run with `this` undefined. Declaring the `this` parameter turns that crash into a compile error."),
        (2348, r"""
class Point {
  x = 0;
}
const p = Point();
""", "A class has a construct signature, not a call signature. The fix is `new Point()`."),
    ],
    pitfalls=[
        ("`map(parseInt)` passes more than you think",
         r"""
const parsed = ["10", "10", "10"].map(parseInt);
console.log(parsed.join(","));
""",
         r"""
const parsed = ["10", "10", "10"].map((s) => parseInt(s, 10));
console.log(parsed.join(","));
""",
         "`parseInt(text, radix?)` fits `map`'s callback slot `(value, index) => …` perfectly — so the element's *index* arrives as the radix. `parseInt(\"10\", 1)` is `NaN` and `parseInt(\"10\", 2)` is `2`. The types agree, and the program is still wrong: pass only what you mean to."),
        ("Method syntax is checked bivariantly",
         r"""
interface Box {
  accept(value: string | number): void;
}
const shout: Box = {
  accept(value: string) {
    console.log(value.toUpperCase());
  },
};
try {
  shout.accept("hi");
  shout.accept(42);
} catch (e) {
  console.log("crashed: " + (e instanceof Error ? e.message : String(e)));
}
""",
         r"""
interface Box {
  accept: (value: string | number) => void;
}
const shout: Box = {
  accept: (value) => console.log(String(value).toUpperCase()),
};
shout.accept("hi");
shout.accept(42);
""",
         "Declared with *method* syntax, `accept(value: string)` is allowed to stand in for `accept(value: string | number)` — a known unsoundness kept for compatibility. Declared as a *property* with a function type, the same mismatch is a compile error, which forces the handler to cope with numbers."),
        ("A detached method loses `this`",
         r"""
class Counter {
  count = 0;
  increment() {
    this.count++;
    return this.count;
  }
}
const counter = new Counter();
const step = counter.increment;
try {
  step();
} catch (e) {
  console.log("crashed: " + (e instanceof Error ? e.message : String(e)));
}
console.log(counter.count);
""",
         r"""
class Counter {
  count = 0;
  increment() {
    this.count++;
    return this.count;
  }
}
const counter = new Counter();
const step = () => counter.increment();
step();
console.log(counter.count);
""",
         "`counter.increment` is a plain function value; calling it on its own runs with `this` undefined. Wrap the call in an arrow (or `bind`), so `this` is fixed where it is created. Writing `increment(this: Counter)` would have made the compiler reject `step()` outright."),
    ],
    later=[
        "**Week 15 — Variance.** Contravariant parameters and the method-bivariance hole, in general form, with `in`/`out` annotations.",
        "**Week 18 — Generics.** Generic call signatures: `<T>(xs: T[]) => T | undefined`.",
        "**Week 21 — Conditional types.** You rebuild `ReturnType` and `Parameters` with `infer`.",
        "**Week 23 — Classes.** `this` in methods, arrow-function fields, and why a class is also a value with a construct signature.",
    ],
    exercises=[
        _drill("ts_function_types-construct", "Build with whatever maker you are given",
               "`ShapeMaker` is a construct signature. Replace `____` so `build` creates one shape per size with the maker it was given.",
               r"""
import * as fs from "fs";
interface Shape {
  area(): number;
}
type ShapeMaker = new (size: number) => Shape;
class Square implements Shape {
  size: number;
  constructor(size: number) {
    this.size = size;
  }
  area() {
    return this.size * this.size;
  }
}
function build(maker: ShapeMaker, sizes: number[]): Shape[] {
  return sizes.map((size) => new maker(size));
}
const sizes = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
console.log(build(Square, sizes).map((s) => s.area()).join(" "));
""", ["new maker(size)"], ["1 2 3", "5", "10 0"],
               hint="A construct signature is called with `new`."),
        _drill("ts_function_types-radix", "Pass only what you mean",
               "The input is a line of numbers in any base-10 spelling (`007`, `12`). Replace `____` with the callback that parses each one in base 10 — `map(parseInt)` would pass the index as the radix.",
               r"""
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const values = words.map((w) => parseInt(w, 10));
console.log(values.join(" "));
console.log(values.reduce((a, b) => a + b, 0));
""", ["(w) => parseInt(w, 10)"], ["10 10 10", "007 12 3", "1"],
               hint="Write the arrow explicitly and give `parseInt` its radix."),
        _drill("ts_function_types-this", "Call it with the right `this`",
               "`label` needs a `this` of type `Item`. Replace `____` so each item is described by calling `label` with that item as `this` and `\"#\"` as the prefix.",
               r"""
import * as fs from "fs";
interface Item {
  name: string;
  qty: number;
}
function label(this: Item, prefix: string): string {
  return prefix + this.name + " x" + this.qty;
}
const items: Item[] = fs.readFileSync(0, "utf8").trim().split("\n").map((line) => {
  const [name = "", qty = "0"] = line.trim().split(/\s+/);
  return { name, qty: Number(qty) };
});
for (const item of items) console.log(label.call(item, "#"));
""", ['label.call(item, "#")'], ["pen 2\ncup 1", "ink 10", "a 1\nb 2\nc 3"],
               hint="`fn.call(thisValue, ...args)` supplies `this` explicitly."),
        _chal("ts_function_types-ops", "An operator table", "Medium",
              "Each input line is `op a b`. Keep a table from operator name to `(a: number, b: number) => number` for `add`, `sub`, `mul`, `max` and `min`. For each line print the result, or `unknown op <op>` when the name is not in the table. Finish with how many lines were computed.",
              r"""
type BinaryOp = (a: number, b: number) => number;
const ops: Record<string, BinaryOp> = {
  add: (a, b) => a + b,
  sub: (a, b) => a - b,
  mul: (a, b) => a * b,
  max: Math.max,
  min: Math.min,
};
let computed = 0;
for (const line of input.split("\n")) {
  const [name = "", a = "0", b = "0"] = line.trim().split(/\s+/);
  const op = Object.hasOwn(ops, name) ? ops[name] : undefined;
  if (op === undefined) {
    console.log("unknown op " + name);
    continue;
  }
  console.log(op(Number(a), Number(b)));
  computed++;
}
console.log(computed);
""", ["add 2 3\nmul 4 5\npow 2 3", "max 7 9\nmin 7 9", "sub 1 10", "toString 1 2\nadd 0 0"],
              hint="`Math.max` fits `BinaryOp`: it takes any number of numbers, and two is a fine number. Guard lookups with `Object.hasOwn` so `toString` is not mistaken for an operator."),
    ],
    quiz=[
        _cq("Which type describes something you call with `new`?",
            "`new (size: number) => Shape`",
            ["`(size: number) => Shape`", "`{ new: (size: number) => Shape }`", "`typeof Shape`, and nothing else can"],
            "A construct signature is written with `new` in front. A class value has one, and so can any object type."),
        _cq("A slot expects `(value: number, index: number) => void`. Why does `(value) => …` fit?",
            "Passing extra arguments to a function that ignores them is harmless",
            ["The compiler adds the missing parameter", "It doesn't fit; you must declare both", "Only because `void` disables checking"],
            "A function that takes fewer parameters can always be called with more arguments; the rest are ignored."),
        _cq("What does `this: Account` in a parameter list do at runtime?",
            "Nothing — it is erased; it only checks what `this` is at each call site",
            ["Binds `this` to an `Account` automatically", "Adds a first parameter the caller must pass", "Creates a new `Account` for each call"],
            "The `this` parameter is purely a type annotation. `describe(\"x\")` still takes one argument."),
        _cq("Under `strict`, why can't `(e: \"click\") => void` be assigned to `(e: string) => void`?",
            "The slot may pass any string, and the handler only accepts one",
            ["Literal types can't appear in parameters", "Arrow functions can't be assigned to type aliases", "It can; parameters are compared bivariantly"],
            "Parameters are checked contravariantly: the function must accept everything the slot might pass it."),
        _cq("What is different about an interface method declared as `accept(v: string): void` compared with `accept: (v: string) => void`?",
            "The method form's parameters are checked bivariantly, so a narrower implementation slips through",
            ["Nothing at all", "The property form can't be implemented by a class", "The method form is always `readonly`"],
            "Method syntax keeps an old, deliberate unsoundness. Property syntax gets the strict, contravariant check."),
        _cq("Why is it `ReturnType<typeof parse>` and not `ReturnType<parse>`?",
            "`parse` is a value; `typeof` lifts it into the type world",
            ["`ReturnType` requires `typeof` for arrow functions only", "`typeof` calls the function to find its result", "Both are valid"],
            "Utility types take types. `typeof parse` is the function's type."),
    ],
    interview=[
        ("How do you type a function that also has properties?",
         "With an object type that has a call signature: `{ (x: number): string; label: string }`. TypeScript also recognises property assignments right after a function declaration or `const` arrow function, so `fn.label = \"x\"` extends the inferred type without a cast."),
        ("What does `strictFunctionTypes` change?",
         "It checks function-typed parameters contravariantly: a handler for `\"click\"` is not a handler for any `string`. Method-syntax members are exempt and stay bivariant, which is a known hole — declaring members as properties closes it."),
        ("What is a `this` parameter for?",
         "Declaring what `this` must be inside a standalone function. It's erased at runtime, but every call is checked, so calling it detached — where `this` would be `undefined` — becomes a compile error instead of a crash."),
    ],
)


_chapter(
    "ts_type_testing", "TS: Type System",
    "Testing Types",
    "Writing tests for types: `Expect<Equal<A, B>>`, `@ts-expect-error`, and the traps that make a type test pass for the wrong reason.",
    "A type is code, and code without tests rots. A type test is a line that only compiles when the type is right — `type _ = Expect<Equal<ReturnType<typeof parse>, Point>>` — and a `// @ts-expect-error` line that only compiles when a misuse is rejected. They run at compile time, cost nothing at runtime, and are how every serious TypeScript library keeps its types honest. Months 4 and 5 of this programme are graded exactly this way.",
    "Java has no equivalent: its types cannot compute, so there is nothing to test. The closest analogue is a compile-fail test in a build tool. In TypeScript, where types are derived from other types, a refactor can silently widen a type to `any` — only a type test notices.",
    why=r"""
Runtime tests catch wrong *values*. They cannot catch wrong *types*: a function
whose return type silently became `any` still returns the right values, every
runtime test still passes, and every caller has quietly lost its type checking.

That happens more than you'd think once types are *derived* — from
`ReturnType`, from a mapped type, from a schema. Change one line upstream and a
type fifty lines away changes shape. A type test pins it down, so the change
shows up as a compile error at the place that states the intent.

The second half of this programme is graded this way: from week 15 on, your
types are checked by hidden `Expect<Equal<…>>` lines. This chapter is how those
work, so a failed check reads as information rather than noise.
""",
    idea=r"""
**Two helpers are the whole toolkit.**

```ts
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type _1 = Expect<Equal<ReturnType<typeof parse>, { x: number; y: number }>>;
```

`Expect<T extends true>` only accepts `true`, so a line that uses it compiles
only when the claim inside is true. `Equal<X, Y>` is the identity check from
the type-challenges project: it compares how the compiler *itself* treats the
two types, so `any`, `readonly` differences and near-miss unions all fail it.

**Why not `A extends B ? B extends A ? … : … : …`?** Mutual assignability is not
identity. `any` is assignable both ways to everything, and `readonly` does not
affect assignability at all — so the naive check calls `{ readonly id: number }`
and `{ id: number }` equal. The pitfalls below show both.

**Testing that something is rejected.** `// @ts-expect-error` on the line
above a statement means "this line must fail to compile". If it does, the
error is swallowed and the file compiles. If it doesn't — because your type
accepts too much — the directive itself is an error (TS2578). That is a
negative test: "a square has no radius".

**Where type tests live.** They must be *compiled* but need not *run*. Type
aliases like `type _1 = …` erase to nothing. A misuse under
`@ts-expect-error` should sit inside a function that is never called, so the
bad call never executes:

```ts
function _typeTests() {
  // @ts-expect-error — a square has no radius
  area({ kind: "square", radius: 2 });
}
```

**What a type test cannot tell you:** whether the values are right. Pair type
tests with ordinary runtime checks; each catches what the other cannot.
""",
    examples=[
        ("Pinning a derived type",
         r"""
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

function parsePoint(text: string) {
  const [x = 0, y = 0] = text.split(",").map(Number);
  return { x, y };
}

type _1 = Expect<Equal<ReturnType<typeof parsePoint>, { x: number; y: number }>>;
type _2 = Expect<Equal<Parameters<typeof parsePoint>, [text: string]>>;

console.log(parsePoint("3,4").x + parsePoint("3,4").y);
""", [""],
         "The program printing `7` is the runtime half. That it *compiled at all* is the type half: both `Expect` lines hold. Change `parsePoint` to return `{ x, y, z: 0 }` and line `_1` stops compiling."),
        ("A negative test: the misuse must be rejected",
         r"""
type Shape = { kind: "square"; size: number } | { kind: "circle"; radius: number };

function area(shape: Shape): number {
  return shape.kind === "square" ? shape.size * shape.size : Math.round(3.14159 * shape.radius ** 2);
}

function _typeTests() {
  // @ts-expect-error — a square has no radius
  area({ kind: "square", radius: 2 });
  // @ts-expect-error — "triangle" is not a kind
  area({ kind: "triangle", size: 1 });
}

console.log(area({ kind: "square", size: 3 }));
console.log(area({ kind: "circle", radius: 1 }));
""", [""],
         "Both directives are satisfied — each line really is an error — so the file compiles. `_typeTests` is never called, so the bad calls never run. If `Shape` were loosened to accept `radius` on a square, the first directive would become TS2578 and the build would fail."),
        ("Type tests beside runtime tests",
         r"""
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

function unique<T>(xs: readonly T[]): T[] {
  return [...new Set(xs)];
}

// type tests: the element type survives, and readonly input is accepted
type _1 = Expect<Equal<ReturnType<typeof unique<string>>, string[]>>;
const frozen: readonly number[] = [3, 1, 3];
type _2 = Expect<Equal<typeof frozen, readonly number[]>>;

// runtime tests: the values are right
let passed = 0;
function check(name: string, actual: string, expected: string) {
  if (actual === expected) passed++;
  else console.log("FAIL " + name + ": " + actual + " !== " + expected);
}
check("dedupes", unique(frozen).join(","), "3,1");
check("keeps order", unique(["b", "a", "b"]).join(","), "b,a");
check("empty", unique([]).join(","), "");
console.log(passed + " runtime checks passed; the type checks passed by compiling");
""", [""],
         "`typeof unique<string>` is an *instantiation expression* — the function's type with `T` fixed — so `ReturnType` can be tested for a specific element type."),
    ],
    errors=[
        (2344, r"""
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

function total(xs: number[]) {
  return xs.reduce((a, b) => a + b, 0).toFixed(2);
}
type _1 = Expect<Equal<ReturnType<typeof total>, number>>;
""", "This is what a failing type test looks like: `Equal` produced `false`, and `Expect` only accepts `true`. Here the test caught a real change — `toFixed` returns a `string`."),
        (2578, r"""
function setPort(port: number | string) {
  return Number(port);
}
function _typeTests() {
  // @ts-expect-error — a port must be a number
  setPort("8080");
}
""", "The directive promised an error on the next line and there wasn't one: `setPort` accepts strings. An unused `@ts-expect-error` is itself an error, which is what makes it a real negative test."),
    ],
    pitfalls=[
        ("Mutual `extends` lets `any` through",
         r"""
type NaiveEqual<A, B> = [A] extends [B] ? ([B] extends [A] ? true : false) : false;
type Expect<T extends true> = T;

function load(text: string) {
  return JSON.parse(text); // any
}
type _1 = Expect<NaiveEqual<ReturnType<typeof load>, { id: number }>>;
console.log("type test passed");
""",
         (r"""
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

function load(text: string) {
  return JSON.parse(text); // any
}
type _1 = Expect<Equal<ReturnType<typeof load>, { id: number }>>;
console.log("type test passed");
""", 2344),
         "`any` is assignable to and from everything, so the naive check calls `any` equal to `{ id: number }` — the test passes while `load` has no useful type at all. The identity-based `Equal` refuses."),
        ("Mutual `extends` ignores `readonly`",
         r"""
type NaiveEqual<A, B> = [A] extends [B] ? ([B] extends [A] ? true : false) : false;
type Expect<T extends true> = T;

type Config = { id: number };  // someone dropped `readonly`
type _1 = Expect<NaiveEqual<Config, { readonly id: number }>>;
console.log("type test passed");
""",
         (r"""
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;

type Config = { id: number };  // someone dropped `readonly`
type _1 = Expect<Equal<Config, { readonly id: number }>>;
console.log("type test passed");
""", 2344),
         "`readonly` does not change assignability, so mutual `extends` cannot see it. A test meant to guarantee immutability has to use an identity check."),
        ("A typo satisfies `@ts-expect-error`",
         r"""
function setPort(port: number | string) {
  return Number(port);
}
function _typeTests() {
  // @ts-expect-error — a port must be a number
  setPrt("8080");
}
console.log(setPort(80));
""",
         (r"""
function setPort(port: number | string) {
  return Number(port);
}
function _typeTests() {
  // @ts-expect-error — a port must be a number
  setPort("8080");
}
console.log(setPort(80));
""", 2578),
         "The directive swallows *any* error, including \"cannot find name `setPrt`\". The test looked green for the wrong reason; with the typo fixed it fails, revealing that `setPort` really does accept strings. Keep negative tests to one small line each, so the only possible error is the one you meant."),
    ],
    later=[
        "**Weeks 14-22 — every Type workshop** is graded by hidden `Expect<Equal<…>>` lines, the helpers from this chapter.",
        "**Week 15 — `satisfies`**, a lightweight check that a value fits a type without changing its inferred type.",
        "**Week 21 — Conditional types.** You'll see why `Equal` is written with generic functions: it is the one comparison `any` cannot fool.",
    ],
    exercises=[
        _drill("ts_type_testing-check", "A tiny runtime check",
               "Type tests prove types; runtime checks prove values. Replace `____` so `check` counts a pass when `actual` equals `expected`, and otherwise prints `FAIL <name>`. The input is `name actual expected` per line.",
               r"""
import * as fs from "fs";
let passed = 0;
function check(name: string, actual: string, expected: string): void {
  if (actual === expected) passed++;
  else console.log("FAIL " + name);
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [name = "", actual = "", expected = ""] = line.trim().split(/\s+/);
  check(name, actual, expected);
}
console.log(passed + " passed");
""", ['if (actual === expected) passed++;\n  else console.log("FAIL " + name);'],
               ["a 1 1\nb 2 3", "only x x", "p 1 2\nq 3 4\nr 5 5"],
               hint="Two branches: count the pass, or print the failure."),
        _drill("ts_type_testing-unique", "The runtime half of a type-tested helper",
               "`unique` is type-tested for its signature; now make its values right. Replace `____` so it returns the distinct items in first-seen order.",
               r"""
import * as fs from "fs";
function unique<T>(xs: readonly T[]): T[] {
  return [...new Set(xs)];
}
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const out = unique(words);
console.log(out.join(" "));
console.log(out.length);
""", ["[...new Set(xs)]"], ["b a b c a", "x", "q q q"],
               hint="A `Set` keeps insertion order; spread it back into an array."),
        _chal("ts_type_testing-report", "A test report", "Easy",
              "Each input line is `PASS name` or `FAIL name reason…`. Print every failure as `✗ name: reason` in input order, then a summary `passed/total`. A line with any other status counts as a failure with reason `bad status <status>`.",
              r"""
let passed = 0;
let total = 0;
for (const line of input.split("\n")) {
  const [status = "", name = "", ...reason] = line.trim().split(/\s+/);
  total++;
  if (status === "PASS") {
    passed++;
  } else if (status === "FAIL") {
    console.log("✗ " + name + ": " + reason.join(" "));
  } else {
    console.log("✗ " + name + ": bad status " + status);
  }
}
console.log(passed + "/" + total);
""", ["PASS a\nFAIL b expected 2 got 3\nPASS c", "PASS only", "SKIP x\nFAIL y timeout"],
              hint="Destructure `status`, `name` and a rest array for the reason."),
    ],
    quiz=[
        _cq("When does `type _ = Expect<Equal<A, B>>` compile?",
            "Only when A and B are the same type",
            ["When A is assignable to B", "Always — it's erased", "When B is a subtype of A"],
            "`Expect` requires `true`, and `Equal` is true only for identical types."),
        _cq("What does an unused `// @ts-expect-error` do?",
            "It is itself a compile error (TS2578)",
            ["Nothing", "It disables checking for the whole file", "It becomes a runtime assertion"],
            "That is what makes it a negative test: if the next line compiles, the directive fails."),
        _cq("Why do misuses under `@ts-expect-error` usually sit inside a function that is never called?",
            "The line must compile-fail but must not run",
            ["The directive only works inside functions", "It makes the test faster", "Top-level code is not type-checked"],
            "The type checker sees the line; the runtime never executes it."),
        _cq("Why is `[A] extends [B] ? [B] extends [A] ? true : false : false` not an identity check?",
            "`any` and `readonly` differences pass mutual assignability",
            ["It distributes over unions", "It is, for every type", "It rejects every object type"],
            "Mutual assignability is weaker than identity; the generic-function trick in `Equal` is not."),
        _cq("What can a type test NOT tell you?",
            "Whether the function returns the right values",
            ["Whether a type is `any`", "Whether a misuse is rejected", "Whether a property is `readonly`"],
            "Types are erased. Values need runtime tests."),
        _cq("What is `typeof unique<string>`?",
            "The type of `unique` with its type parameter fixed to `string` (an instantiation expression)",
            ["A call to `unique`", "A syntax error", "The string `\"function\"`"],
            "Instantiation expressions (TS 4.7) let you test a generic function at a specific type."),
    ],
    interview=[
        ("How would you test a type?",
         "With compile-time assertions: `type _ = Expect<Equal<Actual, Expected>>` for positive claims and `// @ts-expect-error` above a line that must be rejected. They run as part of `tsc`, so CI fails when a type drifts. Libraries often use `expectTypeOf` from Vitest, which is the same idea with a nicer API."),
        ("Why is the `Equal` type written with generic functions?",
         "Because mutual `extends` is too weak — `any` passes both ways and `readonly` doesn't affect assignability. Comparing `<T>() => T extends X ? 1 : 2` for X and Y makes the compiler compare the types by identity, which catches both."),
        ("What's the risk with `@ts-expect-error`?",
         "It swallows any error, so a test can pass for the wrong reason — a typo in the call is an error too. Keep each negative test to one small line, and prefer `@ts-expect-error` over `@ts-ignore`, which never complains when the error goes away."),
    ],
)


_chapter(
    "ts_set_algebra", "TS: Data Structures",
    "Set Algebra, Grouping & Weak Collections",
    "The ES2025 `Set` methods — `union`, `intersection`, `difference`, `symmetricDifference`, `isSubsetOf` and friends — `Map.groupBy`, and `WeakMap`/`WeakSet` for data keyed by object identity.",
    "Sets answer membership questions in constant time, and until recently combining two of them meant hand-written loops. Modern runtimes ship the whole algebra as methods: `a.union(b)`, `a.intersection(b)`, `a.difference(b)`, and the subset tests. `Map.groupBy` buckets values under any kind of key. And `WeakMap`/`WeakSet` attach data to objects without keeping those objects alive — the right tool for caches and metadata keyed by identity.",
    "`Set.retainAll` and `addAll` mutate the set in place; the new JavaScript methods return new sets and leave both inputs alone. `WeakMap` is Java's `WeakHashMap`, except that its keys must be objects and it can't be iterated at all.",
    why=r"""
"Which tags do both articles share?", "which users are in the old list but not
the new one?", "is every required permission granted?" — these are set
questions, and writing them as nested loops is both slower and harder to read
than the one-word answer.

Node 24 runs the ES2025 set methods natively and the judge's `lib` types them,
so this programme can use them from week 9 on. Alongside them this chapter
covers grouping by non-string keys and the weak collections, which exist for
one job the others can't do: remembering something about an object without
preventing it from being garbage-collected.
""",
    idea=r"""
**The algebra.** Each returns a **new** `Set`; neither operand changes.

| method | contains |
|---|---|
| `a.union(b)` | everything in either |
| `a.intersection(b)` | only what's in both |
| `a.difference(b)` | what's in `a` but not `b` |
| `a.symmetricDifference(b)` | what's in exactly one |

And three questions that return a `boolean`: `a.isSubsetOf(b)`,
`a.isSupersetOf(b)`, `a.isDisjointFrom(b)`.

The argument must be *set-like* — it needs `size`, `has` and `keys` — so pass a
`Set` or a `Map`, not an array: `a.union(new Set(array))`.

**Equality inside sets and maps** is *SameValueZero*: like `===`, except that
`NaN` equals `NaN`. Objects are compared by identity — two different objects
with the same contents are two members.

**Order.** Sets and maps iterate in insertion order. The results of the
algebra methods follow the order of the receiver, then the argument.

**`Map.groupBy(items, keyFn)`** groups into a `Map`, so the key can be a
number, an object, anything — unlike `Object.groupBy`, whose keys become
strings.

**Weak collections.** `WeakMap<K, V>` and `WeakSet<T>` only accept objects (or
non-registered symbols) as keys, hold them *weakly* — an entry disappears when
nothing else references the key — and so cannot be iterated or sized. Use them
to attach private data or a cached result to objects you don't own.
""",
    examples=[
        ("Tag algebra",
         r"""
import * as fs from "fs";
const [first = "", second = ""] = fs.readFileSync(0, "utf8").trim().split("\n");
const a = new Set(first.trim().split(/\s+/));
const b = new Set(second.trim().split(/\s+/));
const show = (s: Set<string>) => [...s].join(" ") || "(none)";
console.log("both:     ", show(a.intersection(b)));
console.log("either:   ", show(a.union(b)));
console.log("only a:   ", show(a.difference(b)));
console.log("only one: ", show(a.symmetricDifference(b)));
console.log("a within b?", a.isSubsetOf(b), "| share nothing?", a.isDisjointFrom(b));
""", ["ts js web\njs web css", "x\nx y"],
         "Five questions, five method calls — and `a` and `b` are untouched by all of them."),
        ("Grouping by a numeric key",
         r"""
const scores = [91, 78, 85, 62, 99, 70, 88];
const byDecade = Map.groupBy(scores, (s) => Math.floor(s / 10) * 10);
for (const [decade, group] of [...byDecade].sort((x, y) => y[0] - x[0])) {
  console.log(`${decade}s: ${group.join(" ")}`);
}
""", [""],
         "`Map.groupBy` keeps the keys as numbers, so the buckets sort numerically without converting strings back."),
        ("Remembering things about objects",
         r"""
type Node = { id: string; children: Node[] };
const sizeCache = new WeakMap<Node, number>();
let computed = 0;
function size(node: Node): number {
  const cached = sizeCache.get(node);
  if (cached !== undefined) return cached;
  computed++;
  let total = 1;
  for (const child of node.children) total += size(child);
  sizeCache.set(node, total);
  return total;
}
const leaf = { id: "leaf", children: [] };
const tree: Node = { id: "root", children: [{ id: "a", children: [leaf] }, leaf] };
console.log(size(tree), size(tree), `computed ${computed}`);
""", [""],
         "The cache is keyed by the node object itself. `leaf` appears twice but is sized once, and if the tree is dropped the cache entries go with it — a `Map` would keep every node alive forever."),
    ],
    errors=[
        (2345, r"""
const tags = new Set(["a", "b"]);
const more = ["b", "c"];
console.log(tags.union(more));
""", "The set methods need a set-like argument (`size`, `has`, `keys`). An array has none of them; wrap it: `tags.union(new Set(more))`."),
        (2344, r"""
const seen = new WeakMap<string, number>();
seen.set("id", 1);
console.log(seen.has("id"));
""", "Weak collections only hold objects (and non-registered symbols) — a string can't be held weakly. Use a `Map` for primitive keys."),
    ],
    pitfalls=[
        ("Objects are members by identity",
         r"""
const visited = new Set<{ x: number; y: number }>();
for (const [x, y] of [[0, 0], [1, 0], [0, 0]]) visited.add({ x, y });
console.log(visited.size);
""",
         r"""
const visited = new Set<string>();
for (const [x, y] of [[0, 0], [1, 0], [0, 0]]) visited.add(`${x},${y}`);
console.log(visited.size);
""",
         "Every `{ x, y }` literal is a new object, so the \"duplicate\" point is a third member. For value semantics, key the set by a string (or number) that encodes the value."),
        ("`new Set(\"word\")` is a set of letters",
         r"""
const allowed = new Set("admin");
console.log(allowed.has("admin"), allowed.size);
""",
         r"""
const allowed = new Set(["admin"]);
console.log(allowed.has("admin"), allowed.size);
""",
         "The constructor iterates its argument, and iterating a string yields characters. Wrap a single value in an array."),
        ("A `Set` serialises as `{}`",
         r"""
const tags = new Set(["a", "b"]);
console.log(JSON.stringify({ tags }));
""",
         r"""
const tags = new Set(["a", "b"]);
console.log(JSON.stringify({ tags: [...tags] }));
""",
         "`JSON.stringify` only sees own enumerable properties, and a `Set` has none. Convert to an array first (the same goes for `Map` — use `Object.fromEntries` or an array of entries)."),
    ],
    later=[
        "**Week 12 — Discriminated unions.** A `Set` of visited states in a state machine.",
        "**Week 17 — Utility types.** `Exclude` and `Extract` are set difference and intersection on *types*.",
        "**Week 24 — Generic data structures.** Building your own collections with the same iteration protocol.",
    ],
    exercises=[
        _drill("ts_set_algebra-both", "What both lists share",
               "The input is two lines of words. Replace `____` with the set of words that appear on both lines.",
               r"""
import * as fs from "fs";
const [x = "", y = ""] = fs.readFileSync(0, "utf8").trim().split("\n");
const a = new Set(x.trim().split(/\s+/));
const b = new Set(y.trim().split(/\s+/));
const both = a.intersection(b);
console.log([...both].sort().join(" ") || "(none)");
""", ["a.intersection(b)"], ["red green blue\ngreen blue pink", "a\nb", "x y\ny x"],
               hint="One method call on `a`, with `b` as its argument."),
        _drill("ts_set_algebra-missing", "What's missing",
               "The first line lists required permissions, the second the granted ones. Replace `____` with the set of required permissions that were not granted.",
               r"""
import * as fs from "fs";
const [req = "", got = ""] = fs.readFileSync(0, "utf8").trim().split("\n");
const required = new Set(req.trim().split(/\s+/));
const granted = new Set(got.trim().split(/\s+/));
const missing = required.difference(granted);
console.log(missing.size === 0 ? "all granted" : `missing ${[...missing].join(" ")}`);
console.log(required.isSubsetOf(granted));
""", ["required.difference(granted)"], ["read write\nread", "read\nread write admin", "a b c\nx"],
               hint="Required minus granted."),
        _chal("ts_set_algebra-roster", "Roster changes", "Medium",
              "The first line is last term's roster, the second this term's (names separated by spaces; a name may repeat by mistake). Print `joined: …`, `left: …` and `stayed: …` — each sorted, `(none)` if empty — then `same roster` or `changed`.",
              r"""
const [before = "", after = ""] = input.split("\n");
const old = new Set(before.trim().split(/\s+/).filter((n) => n !== ""));
const now = new Set(after.trim().split(/\s+/).filter((n) => n !== ""));
const list = (s: Set<string>) => [...s].sort().join(" ") || "(none)";
console.log(`joined: ${list(now.difference(old))}`);
console.log(`left: ${list(old.difference(now))}`);
console.log(`stayed: ${list(old.intersection(now))}`);
console.log(old.symmetricDifference(now).size === 0 ? "same roster" : "changed");
""", ["ada bo cy\nbo cy dee", "x y\ny x x", "\nnew"],
              hint="Joined is new minus old; left is old minus new; unchanged means the symmetric difference is empty."),
    ],
    quiz=[
        _cq("What does `a.difference(b)` return?", "A new set of the members of `a` that are not in `b`",
            ["It removes `b`'s members from `a` in place", "Members in exactly one of the two", "A boolean"],
            "The set methods never mutate either operand."),
        _cq("Why can't you write `set.union([1, 2])`?", "The argument must be set-like (`size`, `has`, `keys`), and an array isn't",
            ["Arrays can't contain numbers", "`union` takes two sets", "You can; it's fine"],
            "Wrap it: `set.union(new Set([1, 2]))`."),
        _cq("How are keys compared in a `Set`?", "SameValueZero — like `===`, but `NaN` equals `NaN`; objects by identity",
            ["Deep equality", "By `JSON.stringify`", "By `==`"],
            "Two equal-looking objects are two different members."),
        _cq("When do you need a `WeakMap` rather than a `Map`?", "To attach data to objects without keeping them alive",
            ["For string keys", "When you need to iterate the entries", "For better ordering"],
            "Entries disappear with their key; the price is no iteration and no `size`."),
        _cq("`Map.groupBy` versus `Object.groupBy`?", "`Map.groupBy` keeps keys of any type; `Object.groupBy` turns them into property keys",
            ["They're identical", "`Map.groupBy` sorts the groups", "`Object.groupBy` is faster"],
            "Numbers, objects or booleans as keys call for the `Map` version."),
    ],
    interview=[
        ("How would you find the items common to two large lists?",
         "Put one in a `Set` and filter the other by `has` — O(n + m) rather than nested loops — or, with ES2025, `new Set(a).intersection(new Set(b))`. For objects I'd key by an id, since sets compare objects by identity."),
        ("What's a `WeakMap` good for?",
         "Associating data with objects you don't own without leaking them: caches of computed results, private per-instance state, metadata on DOM nodes. Keys must be objects, entries vanish when the key is collected, and you can't iterate or size it."),
        ("Why does `new Set([{a: 1}, {a: 1}]).size` equal 2?",
         "Sets use SameValueZero, which compares objects by reference. Two literals are two objects. Use a primitive key — an id or a serialised form — for value semantics."),
    ],
)


_chapter(
    "ts_literal_inference", "TS: Type System",
    "Literal Types, Widening & `as const`",
    "When TypeScript keeps a literal type and when it widens it, how `as const` freezes a value's type, and deriving a union from a list of values with `typeof xs[number]`.",
    "Write `\"up\"` and TypeScript can give it the type `\"up\"` — or just `string`. Which one it picks follows a few rules: `const` bindings keep literals, `let` bindings and object properties widen them, and `as const` stops all widening at once. Those rules decide whether a value can be passed where a union like `\"up\" | \"down\"` is expected, and they let one array of values be the single source of truth for both the runtime list and the type.",
    "Java would reach for an enum here. The TypeScript idiom is a union of string literals — erased at runtime, checked at compile time — often derived from an `as const` array so the list of values exists exactly once.",
    why=r"""
You declare `type Direction = "up" | "down"` and a function that takes one. Then
`let dir = "up"; move(dir)` fails to compile, while `move("up")` works. A config
object `{ method: "GET" }` is rejected by a function that wants
`"GET" | "POST"`. And the list of valid values lives twice — once in the union,
once in an array for validation — and they drift.

All three come from literal inference. Once you know when a literal widens,
the errors make sense; and `as const` with `typeof xs[number]` turns the two
lists into one.
""",
    idea=r"""
**Widening rules.**

| declaration | inferred type |
|---|---|
| `const d = "up"` | `"up"` — a `const` can never change |
| `let d = "up"` | `string` — it might be reassigned |
| `const o = { d: "up" }` | `{ d: string }` — properties are mutable |
| `const xs = ["up", "down"]` | `string[]` — arrays are mutable |

The same goes for numbers and booleans.

**Contextual typing prevents widening.** If the value is written where a
literal type is expected — `move("up")`, or `const d: Direction = "up"` — it
stays literal.

**`as const`** makes a whole expression as narrow as possible: literals stay
literals, arrays become `readonly` tuples, object properties become `readonly`:

```ts
const SIZES = ["S", "M", "L"] as const;   // readonly ["S", "M", "L"]
type Size = (typeof SIZES)[number];        // "S" | "M" | "L"
```

`typeof SIZES[number]` asks "what is the type of any element?" — the union of
the literals. Now the array is the single source of truth: add `"XL"` and the
type follows.

**Validation still needs runtime code.** `as const` only affects types. A
string read from input is `string` until you check it against the list —
`SIZES.find((s) => s === text)` narrows it properly.

**Enums** (next chapter, in the same week) are the older, non-erasable way to
name a set of values; literal unions are preferred today, and they run under
Node's type stripping, which enums don't.
""",
    examples=[
        ("One list, the values and the type",
         r"""
import * as fs from "fs";
const SIZES = ["S", "M", "L", "XL"] as const;
type Size = (typeof SIZES)[number];
const chest: Record<Size, number> = { S: 90, M: 98, L: 106, XL: 114 };

function parseSize(text: string): Size | undefined {
  return SIZES.find((s) => s === text);
}

for (const token of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  const size = parseSize(token.toUpperCase());
  console.log(size === undefined ? `${token}: unknown size` : `${size}: ${chest[size]} cm`);
}
""", ["m xl s", "XXL L"],
         "`Size` is derived from `SIZES`; `Record<Size, number>` must cover every size; `find` turns a string into a checked `Size`. Adding a size to the array updates all three."),
        ("Where a literal widens",
         r"""
type Method = "GET" | "POST";
function send(method: Method, path: string): string {
  return `${method} ${path}`;
}

const fixed = "GET";
const request = { method: "POST", path: "/items" } as const;
const table = { method: "GET" as Method, path: "/" };

console.log(send(fixed, "/health"));
console.log(send(request.method, request.path));
console.log(send(table.method, table.path));
""", [""],
         "`fixed` is `\"GET\"` because it's a `const`. The object needs help: `as const` on the whole literal, or an annotation on the one property. Without either, `method` would be `string` and `send` would refuse it."),
        ("Readonly tuples from `as const`",
         r"""
const ORIGIN = [0, 0] as const;
const STEPS = { N: [0, 1], E: [1, 0], S: [0, -1], W: [-1, 0] } as const;
type Heading = keyof typeof STEPS;

function move([x, y]: readonly [number, number], heading: Heading, n: number): [number, number] {
  const [dx, dy] = STEPS[heading];
  return [x + dx * n, y + dy * n];
}

let at = move(ORIGIN, "N", 3);
at = move(at, "E", 2);
at = move(at, "S", 5);
console.log(at.join(","));
""", [""],
         "`as const` makes each step a `readonly [number, number]` and the object's keys a literal union — `keyof typeof STEPS` is `\"N\" | \"E\" | \"S\" | \"W\"` with no separate declaration."),
    ],
    errors=[
        (2345, r"""
type Direction = "up" | "down";
function move(d: Direction): string {
  return d === "up" ? "^" : "v";
}
let current = "up";
console.log(move(current));
""", "`let current = \"up\"` widens to `string`, because a `let` can be reassigned to any string. Declare it `const`, or annotate it `let current: Direction = \"up\"`."),
        (2540, r"""
const LIMITS = { min: 1, max: 10 } as const;
LIMITS.max = 20;
console.log(LIMITS.max);
""", "`as const` made every property `readonly`. (At runtime nothing is frozen — the check is compile-time only.)"),
    ],
    pitfalls=[
        ("An object property widens",
         (r"""
type Level = "info" | "warn";
function log(entry: { level: Level; text: string }): string {
  return `[${entry.level}] ${entry.text}`;
}
const entry = { level: "warn", text: "disk almost full" };
console.log(log(entry));
""", 2345),
         r"""
type Level = "info" | "warn";
function log(entry: { level: Level; text: string }): string {
  return `[${entry.level}] ${entry.text}`;
}
const entry = { level: "warn", text: "disk almost full" } as const;
console.log(log(entry));
""",
         "Object properties are mutable, so `level: \"warn\"` is inferred as `string`. `as const` (or annotating `entry` with the parameter's type) keeps the literal."),
        ("A cast is not a check",
         r"""
import * as fs from "fs";
const MODES = ["fast", "safe"] as const;
type Mode = (typeof MODES)[number];
const mode = fs.readFileSync(0, "utf8").trim() as Mode;
console.log(mode === "fast" ? "fast path" : mode === "safe" ? "safe path" : "unreachable?");
""",
         r"""
import * as fs from "fs";
const MODES = ["fast", "safe"] as const;
type Mode = (typeof MODES)[number];
const text = fs.readFileSync(0, "utf8").trim();
const mode: Mode | undefined = MODES.find((m) => m === text);
console.log(mode === undefined ? "invalid mode" : mode === "fast" ? "fast path" : "safe path");
""",
         "`as Mode` tells the compiler to believe it; the program then reaches a branch its own types say is impossible. Check input against the list and carry `undefined` when it isn't there.",
         ["turbo"]),
        ("`as const` arrays can't go where mutable arrays are expected",
         (r"""
const DEFAULTS = ["a", "b"] as const;
function addTag(tags: string[], tag: string): string[] {
  tags.push(tag);
  return tags;
}
console.log(addTag(DEFAULTS, "c").join(","));
""", 2345),
         r"""
const DEFAULTS = ["a", "b"] as const;
function addTag(tags: readonly string[], tag: string): string[] {
  return [...tags, tag];
}
console.log(addTag(DEFAULTS, "c").join(","), DEFAULTS.length);
""",
         "A `readonly` tuple can't be passed as `string[]`, because the function might mutate it — and this one does. Accept `readonly string[]` and return a new array; that function now works with both."),
    ],
    later=[
        "**Week 15 — `satisfies`.** Check a value against a type *without* widening it — the other half of this chapter.",
        "**Week 18 — `const` type parameters.** A generic function that infers literal types from its arguments, as if the caller wrote `as const`.",
        "**Week 19 — `keyof` and indexed access.** `keyof typeof obj` and `T[number]` in depth.",
    ],
    exercises=[
        _drill("ts_literal_inference-derive", "One list, one type",
               "Replace `____` with the type of any element of `COLORS` — the union of its literals.",
               r"""
import * as fs from "fs";
const COLORS = ["red", "green", "blue"] as const;
type Color = (typeof COLORS)[number];
const hex: Record<Color, string> = { red: "#f00", green: "#0f0", blue: "#00f" };
for (const t of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  const c = COLORS.find((x) => x === t);
  console.log(c === undefined ? `${t}?` : hex[c]);
}
""", ["(typeof COLORS)[number]"], ["red blue", "pink green"],
               hint="`typeof COLORS` is a readonly tuple; indexing it with `number` gives the element type."),
        _drill("ts_literal_inference-check", "Earn the literal type",
               "Replace `____` so `unit` is a checked `Unit`, or `undefined` when the input isn't one of the units.",
               r"""
import * as fs from "fs";
const UNITS = ["kg", "g", "lb"] as const;
type Unit = (typeof UNITS)[number];
const toGrams: Record<Unit, number> = { kg: 1000, g: 1, lb: 453.592 };
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [amount = "0", text = ""] = line.trim().split(/\s+/);
  const unit = UNITS.find((u) => u === text);
  console.log(unit === undefined ? `bad unit ${text}` : `${(Number(amount) * toGrams[unit]).toFixed(1)} g`);
}
""", ["UNITS.find((u) => u === text)"], ["2 kg\n5 lb\n3 oz", "100 g"],
               hint="`find` with an equality test narrows a `string` to the element type."),
        _chal("ts_literal_inference-http", "Route by method", "Medium",
              "Declare `const METHODS = [\"GET\", \"POST\", \"PUT\", \"DELETE\"] as const` and derive `Method` from it. Each input line is `METHOD /path`. Count the requests per method in a `Record<Method, number>` (methods are case-sensitive; anything else counts as `other`). Print the four counts in declaration order as `GET=n`, then `other=n`.",
              r"""
const METHODS = ["GET", "POST", "PUT", "DELETE"] as const;
type Method = (typeof METHODS)[number];
const counts: Record<Method, number> = { GET: 0, POST: 0, PUT: 0, DELETE: 0 };
let other = 0;
for (const line of input.split("\n")) {
  const [text = ""] = line.trim().split(/\s+/);
  const method = METHODS.find((m) => m === text);
  if (method === undefined) other++;
  else counts[method]++;
}
console.log(METHODS.map((m) => `${m}=${counts[m]}`).join(" "));
console.log(`other=${other}`);
""", ["GET /a\nPOST /b\nGET /c\nget /d\nPATCH /e", "DELETE /x", "PUT /y\nPUT /z"],
              hint="`find` turns each token into a `Method | undefined`; the record then indexes safely."),
    ],
    quiz=[
        _cq("`let d = \"up\"` — what type is `d`?", "`string`", ["`\"up\"`", "`any`", "`readonly \"up\"`"],
            "A `let` can be reassigned, so its literal widens."),
        _cq("`const o = { d: \"up\" }` — what is `o.d`?", "`string`", ["`\"up\"`", "`readonly \"up\"`", "`never`"],
            "Object properties are mutable and widen unless you use `as const` or annotate."),
        _cq("What does `as const` do to `[1, 2]`?", "Makes it `readonly [1, 2]`",
            ["Freezes it at runtime", "Makes it `number[]`", "Makes it `[number, number]`"],
            "Literal element types, fixed length, readonly — and nothing at runtime."),
        _cq("`const SIZES = [\"S\", \"M\"] as const` — what is `(typeof SIZES)[number]`?", "`\"S\" | \"M\"`",
            ["`string`", "`2`", "`readonly string[]`"],
            "Indexing a tuple type with `number` gives the union of its element types."),
        _cq("Is `const x = input as Size` a validation?", "No — it only tells the compiler to assume it",
            ["Yes, it throws on bad values", "Yes, at compile time", "Only under `strict`"],
            "Check the value against the list at runtime to earn the type."),
    ],
    interview=[
        ("Why does `let x = \"a\"` get type `string` but `const x = \"a\"` get `\"a\"`?",
         "Widening: a `let` can be reassigned, so TypeScript picks the general type; a `const` can't, so the literal is safe. Object properties and array elements widen too, because they're mutable."),
        ("How do you keep a list of allowed values and a matching type in sync?",
         "Declare the values once with `as const` and derive the type: `const ROLES = [\"admin\", \"user\"] as const; type Role = (typeof ROLES)[number];`. Validation uses the array at runtime, the type follows automatically."),
        ("Literal unions or enums?",
         "Literal unions: they're erased, need no import to use a value, work with Node's type stripping and `erasableSyntaxOnly`, and derive nicely from `as const` arrays. Enums add a runtime object and some odd semantics (numeric reverse mappings)."),
    ],
)


_chapter(
    "ts_control_flow", "TS: Type System",
    "Control-Flow Analysis",
    "How the compiler follows your code to narrow types: assignments, early returns, `in`, `instanceof`, `Array.isArray`, inferred type predicates in `filter`, assertion functions, aliased conditions — and where narrowing stops.",
    "TypeScript doesn't give a variable one type for its whole life. It tracks what each branch has proved: after `if (!user) return;` the rest of the function knows `user` is defined; inside `if (typeof x === \"string\")` it knows `x` is a string. This control-flow analysis is why most narrowing needs no annotations. Knowing its rules — and the few places it deliberately gives up — explains nearly every \"possibly undefined\" error you'll meet.",
    "Java's pattern matching (`if (o instanceof String s)`) binds a new variable. TypeScript narrows the *same* variable in place, following returns, throws, assignments and boolean conditions across the whole function.",
    why=r"""
Real code checks things in many ways: an early return for a missing value, a
`typeof` on a union, an `in` test on an object, a `filter` that removes
`undefined`s, a helper that throws if something is invalid. If the compiler
couldn't follow all of that, you'd be writing casts after every check — and
casts are where bugs hide.

Control-flow analysis is what lets checked code stay cast-free. Its limits —
callbacks, mutable variables, conditions split across functions — are exactly
where you'll still see errors after "obviously" checking, and each has a
standard fix.
""",
    idea=r"""
**Narrowing follows the code.** Each of these narrows the variable for the
code it guards:

- `typeof x === "string"`, `x instanceof Date`, `Array.isArray(x)`
- `"radius" in shape` — for object unions
- `x === null`, `x !== undefined`, `x == null`, truthiness (`if (x)`)
- an **early return or throw**: after `if (!user) return;` the rest of the
  function has a defined `user`
- **assignment**: after `x = 5`, `x` is a `number` until reassigned

**Inferred type predicates (TS 5.5).** A function like
`(x) => x !== undefined` is inferred to return `x is T`. So
`items.filter((x) => x !== undefined)` really returns `T[]`, with no annotation.

**User-defined guards.** `function isUser(v: unknown): v is User` narrows its
argument where it returns `true` (week 11's other chapter).

**Assertion functions** narrow by *throwing*:

```ts
function assertDefined<T>(v: T | undefined, what: string): asserts v is T {
  if (v === undefined) throw new Error(`${what} is missing`);
}
```

After `assertDefined(user, "user")`, `user` is defined for the rest of the
scope. An assertion function must be declared with an explicit type annotation
— a plain `function` declaration, or a `const` with an annotated function type.

**Aliased conditions (TS 4.4).** `const isText = typeof x === "string";
if (isText) …` narrows `x` too — as long as both `isText` and `x` are `const`
(or never reassigned).

**Where narrowing stops.**

- **Callbacks.** Since TypeScript 5.4 a callback keeps a variable's narrowing
  if it's created after the variable's *last* assignment. If the variable is
  assigned again later, the callback might run after that, so the narrowing is
  dropped. Copy the narrowed value into a `const` first.
- **Properties after calls.** Narrowing of `obj.prop` can be reset by a function
  call that might have changed `obj`.
- **Across functions.** A check in one function doesn't narrow in another
  unless it's a type predicate or an assertion function.
""",
    examples=[
        ("Early returns narrow the rest of the function",
         r"""
import * as fs from "fs";
type User = { name: string; email?: string };

function contact(user: User | undefined): string {
  if (user === undefined) return "no user";
  if (user.email === undefined) return `${user.name} (no email)`;
  return `${user.name} <${user.email.toLowerCase()}>`;
}

const users: (User | undefined)[] = JSON.parse(fs.readFileSync(0, "utf8").trim());
for (const u of users) console.log(contact(u ?? undefined));
""", ['[{"name":"Ada","email":"ADA@X.IO"},{"name":"Bo"},null]'],
         "Each `return` removes a case, so by the last line `user` and `user.email` are both known to be defined — no `!` anywhere."),
        ("`filter` that narrows by itself",
         r"""
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const parsed = raw.map((t) => (/^-?\d+$/.test(t) ? Number(t) : undefined));
const numbers = parsed.filter((n) => n !== undefined);
const total = numbers.reduce((a, b) => a + b, 0);
console.log(`${numbers.length} numbers, total ${total}, ${parsed.length - numbers.length} skipped`);
""", ["3 x 4 -2 y", "a b"],
         "`parsed` is `(number | undefined)[]`. The arrow `(n) => n !== undefined` is inferred as a type predicate, so `numbers` is a plain `number[]` and `reduce` needs no casts."),
        ("An assertion function",
         r"""
import * as fs from "fs";
type Order = { id: string; qty: number };

function assertOrder(value: unknown): asserts value is Order {
  if (typeof value !== "object" || value === null) throw new Error("not an object");
  if (!("id" in value) || typeof value.id !== "string") throw new Error("bad id");
  if (!("qty" in value) || typeof value.qty !== "number") throw new Error("bad qty");
}

for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const data: unknown = JSON.parse(line);
  try {
    assertOrder(data);
    console.log(`${data.id}: ${data.qty * 2} units`);
  } catch (e) {
    console.log(`rejected: ${e instanceof Error ? e.message : String(e)}`);
  }
}
""", ['{"id":"a1","qty":3}\n{"id":7,"qty":1}\n["x"]\n{"id":"b2"}'],
         "Past `assertOrder(data)` the compiler treats `data` as an `Order`. The `in` checks narrow `unknown` step by step inside the assertion itself."),
    ],
    errors=[
        (18048, r"""
function shout(items: string[], prefix: string | undefined): string[] {
  if (prefix === undefined) prefix = ">";
  const out = items.map((item) => prefix.toUpperCase() + item);
  prefix = undefined;
  return out;
}
console.log(shout(["a"], undefined));
""", "Because `prefix` is assigned again *after* the arrow is created, the compiler can't be sure which value the callback will see, so the narrowing isn't carried inside. Copy the narrowed value into a `const` and use that: `const p = prefix;`."),
        (2775, r"""
const assertPositive = (n: number): asserts n is number => {
  if (n <= 0) throw new Error("not positive");
};
assertPositive(5);
console.log("ok");
""", "An assertion function called through a name must have an *explicitly* typed declaration. A `const` initialised with an arrow isn't one; write `function assertPositive(...)` or annotate the constant's type."),
        (2339, r"""
type Circle = { radius: number };
type Square = { side: number };
function area(s: Circle | Square): number {
  return s.radius ** 2 * Math.PI;
}
console.log(area({ radius: 1 }));
""", "Only properties present on *every* member of a union can be read before narrowing. Check first: `if (\"radius\" in s) …`."),
    ],
    pitfalls=[
        ("A type predicate that lies",
         r"""
type Point = { x: number; y: number };
function isPoint(v: unknown): v is Point {
  return typeof v === "object" && v !== null;
}
const data: unknown[] = [{ x: 1, y: 2 }, { name: "not a point" }];
for (const d of data) {
  if (isPoint(d)) console.log((d.x + d.y).toFixed(1));
}
""",
         r"""
type Point = { x: number; y: number };
function isPoint(v: unknown): v is Point {
  return typeof v === "object" && v !== null && "x" in v && typeof v.x === "number" && "y" in v && typeof v.y === "number";
}
const data: unknown[] = [{ x: 1, y: 2 }, { name: "not a point" }];
for (const d of data) {
  if (isPoint(d)) console.log((d.x + d.y).toFixed(1));
}
""",
         "The compiler trusts a predicate's body completely. This one only checks \"is an object\", so the second value is treated as a `Point` and `undefined + undefined` prints `NaN`. A predicate must check everything its type claims."),
        ("`typeof null === \"object\"`",
         r"""
function describe(v: unknown): string {
  if (typeof v === "object") return `object with ${Object.keys(v ?? {}).length} keys`;
  return typeof v;
}
console.log([{ a: 1 }, null, [1, 2]].map(describe).join("; "));
""",
         r"""
function describe(v: unknown): string {
  if (v === null) return "null";
  if (Array.isArray(v)) return `array of ${v.length}`;
  if (typeof v === "object") return `object with ${Object.keys(v).length} keys`;
  return typeof v;
}
console.log([{ a: 1 }, null, [1, 2]].map(describe).join("; "));
""",
         "`typeof` reports `\"object\"` for `null` and for arrays too. Rule both out first — and notice that the fixed version needs no `?? {}`, because the checks have narrowed `v` properly."),
        ("Narrowing doesn't survive into a callback if the variable changes later",
         (r"""
let label: string | undefined = "total";
const format = (n: number) => `${label.toUpperCase()} ${n}`;
label = undefined;
console.log(format(1));
""", 18048),
         r"""
let label: string | undefined = "total";
const fixed = label;
const format = (n: number) => `${fixed.toUpperCase()} ${n}`;
label = undefined;
console.log(format(1));
""",
         "The arrow runs *after* `label` becomes `undefined` — so the compiler was right not to trust its narrowing inside the callback. Capturing the narrowed value in a `const` fixes both the error and the crash it predicted."),
    ],
    later=[
        "**Week 12 — Discriminated unions.** Narrowing by a tag field, and exhaustiveness.",
        "**Week 15 — Assertions.** `as` versus assertion functions: claiming versus proving.",
        "**Week 25 — Errors.** Narrowing the `unknown` in `catch (e)`.",
    ],
    exercises=[
        _drill("ts_control_flow-filter", "Drop the undefineds",
               "Replace `____` with a `filter` whose arrow the compiler infers as a type predicate, so `values` is a plain `number[]`.",
               r"""
import * as fs from "fs";
const tokens = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const maybe = tokens.map((t) => (Number.isNaN(Number(t)) ? undefined : Number(t)));
const values = maybe.filter((v) => v !== undefined);
console.log(values.length, Math.max(...values, -Infinity));
""", ["maybe.filter((v) => v !== undefined)"], ["3 x 9 y 4", "a", "-1"],
               hint="An arrow that returns `v !== undefined` is inferred as `v is number`."),
        _drill("ts_control_flow-early", "Return early, then use it",
               "Replace `____` with an early return of `\"anonymous\"` when `name` is missing, so the last line can use `name` directly.",
               r"""
import * as fs from "fs";
function greeting(name: string | undefined): string {
  if (name === undefined || name.trim() === "") return "anonymous";
  return `hello, ${name.trim()}`;
}
for (const line of fs.readFileSync(0, "utf8").split("\n").slice(0, -1)) {
  console.log(greeting(line === "-" ? undefined : line));
}
""", ['if (name === undefined || name.trim() === "") return "anonymous";'], ["ada\n-\n  \nbo\n"],
               hint="After the `if` returns, the compiler knows `name` is a `string`."),
        _chal("ts_control_flow-mixed", "Classify JSON values", "Medium",
              "Each input line is a JSON value. Print its kind — `null`, `array(<length>)`, `object(<keys>)`, `string(<length>)`, `number` or `boolean` — using narrowing on an `unknown`, no casts. Then print how many lines were numbers greater than 10.",
              r"""
let bigNumbers = 0;
function kind(value: unknown): string {
  if (value === null) return "null";
  if (Array.isArray(value)) return `array(${value.length})`;
  if (typeof value === "object") return `object(${Object.keys(value).length})`;
  if (typeof value === "string") return `string(${value.length})`;
  if (typeof value === "number") {
    if (value > 10) bigNumbers++;
    return "number";
  }
  return typeof value;
}
for (const line of input.split("\n")) console.log(kind(JSON.parse(line)));
console.log(`big numbers: ${bigNumbers}`);
""", ['null\n[1,2]\n{"a":1,"b":2}\n"hi"\n42\ntrue', "3\n11\n[]"],
              hint="Rule out `null` and arrays before testing for `\"object\"`."),
    ],
    quiz=[
        _cq("After `if (!user) return;`, what does the compiler know about `user`?", "That it's truthy — `null` and `undefined` are gone",
            ["Nothing", "That it's an object", "That it's `any`"],
            "Early returns narrow everything after them."),
        _cq("What is `[1, undefined, 2].filter((x) => x !== undefined)` typed as (TS 5.5+)?", "`number[]`",
            ["`(number | undefined)[]`", "`unknown[]`", "`never[]`"],
            "The arrow is inferred as a type predicate."),
        _cq("What does `asserts v is T` mean in a return type?", "If the function returns at all, `v` is a `T` from then on",
            ["It returns a boolean", "It casts `v`", "It only works in tests"],
            "It narrows by throwing on failure."),
        _cq("When is a narrowed `let` NOT narrowed inside a callback (TS 5.4+)?", "When the variable is assigned again after the callback is created",
            ["Always", "Never", "Only under `strict`"],
            "The callback might run after that later assignment. Copy the narrowed value to a `const`."),
        _cq("`typeof null` is…", "`\"object\"`", ["`\"null\"`", "`\"undefined\"`", "`\"unknown\"`"],
            "Check `v === null` before trusting a `typeof v === \"object\"` test."),
    ],
    interview=[
        ("What is control-flow narrowing?",
         "The compiler tracks what each branch has proved and gives a variable a narrower type there: after `typeof x === \"string\"`, an early return, an `in` check or an assignment. It's why checked code rarely needs casts."),
        ("Type predicate or assertion function?",
         "A predicate (`v is T`) returns a boolean you branch on — good for filtering and optional handling. An assertion function (`asserts v is T`) throws when the check fails and narrows everything after the call — good at trust boundaries where invalid data should stop processing."),
        ("When does narrowing not apply?",
         "Inside callbacks for variables that are reassigned after the callback is created (TS 5.4 keeps it otherwise), for object properties after an intervening call, and across function boundaries unless the function is a type predicate or assertion. The fix is usually capturing the narrowed value in a `const`."),
    ],
)


_chapter(
    "ts_top_bottom", "TS: Type System",
    "`unknown`, `never`, `void` & Exhaustiveness",
    "The top and bottom of the type system: `unknown` as the safe \"anything\", `never` as \"impossible\", `void` as \"ignore the result\", the three flavours of object type, and using `never` to make a `switch` exhaustive.",
    "Every type sits between two extremes. `unknown` is the top: any value fits, and you must narrow before using it. `never` is the bottom: no value fits, which makes it the type of code that can't run — a function that always throws, the `default` branch after every case is handled. Using `never` on purpose turns \"did I handle every variant?\" into a compile error the moment a new variant is added.",
    "`unknown` is `Object` done right: you can store anything but must check before use. `never` has no Java counterpart — it's closest to a method that always throws. The exhaustiveness check does what Java's sealed interfaces plus a pattern-matching `switch` do.",
    why=r"""
You add a variant to a union — a new shape, a new event, a new state — and
somewhere a `switch` doesn't handle it. With a `default` branch it silently
returns 0 or does nothing; without one, it returns `undefined`. The bug turns
up in production.

`never` makes that impossible: a line that only compiles if every case was
handled. And its opposite, `unknown`, is how you accept untrusted data honestly.
Together they bracket every other type in the language.
""",
    idea=r"""
**`unknown` — the top type.** Every value is assignable to `unknown`, and you
can do nothing with an `unknown` until you narrow it. It's the right type for
parsed JSON, `catch` variables and anything from outside the program.

**`never` — the bottom type.** No value is a `never`. It appears as:

- the return type of a function that never returns (`throw`, infinite loop)
- the type left in a variable after every possibility has been narrowed away
- the empty union: `Exclude<"a", "a">` is `never`

**Exhaustiveness.** At the end of a `switch` over a union, every case has been
removed from the variable's type, so what's left is `never`:

```ts
function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "square": return s.side ** 2;
    default: {
      const unhandled: never = s;   // fails to compile if a case is missing
      throw new Error(`unhandled shape ${JSON.stringify(unhandled)}`);
    }
  }
}
```

Add `{ kind: "triangle" }` to `Shape` and the `default` branch no longer
compiles — the compiler lists every `switch` you must update. `s satisfies
never` does the same check without a variable.

**`void`** means "the return value isn't meant to be used". A function typed
`() => void` may still return something; callers just ignore it. That's why a
`forEach` callback may return a value. Don't use `void` for a value you store.

**Three object types.** `object` is any non-primitive. `{}` is anything that
isn't `null` or `undefined` — including `5` and `"text"`! `Object` (capital O)
is nearly the same as `{}` and is almost never what you want.
""",
    examples=[
        ("An exhaustive switch",
         r"""
import * as fs from "fs";
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number }
  | { kind: "rect"; width: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius ** 2;
    case "square":
      return s.side ** 2;
    case "rect":
      return s.width * s.height;
    default: {
      const unhandled: never = s;
      throw new Error(`unhandled ${JSON.stringify(unhandled)}`);
    }
  }
}

const shapes = JSON.parse(fs.readFileSync(0, "utf8").trim()) as Shape[];
console.log(shapes.map((s) => area(s).toFixed(2)).join(" "));
""", ['[{"kind":"circle","radius":1},{"kind":"square","side":3},{"kind":"rect","width":2,"height":5}]'],
         "Every case returns, so the `default` branch can only be reached by a value of type `never`. If the JSON sneaks in a shape the type doesn't know, the `throw` reports it at runtime too."),
        ("`never` as a function that doesn't return",
         r"""
import * as fs from "fs";
function fail(message: string): never {
  throw new Error(message);
}

function parsePort(text: string): number {
  const n = Number(text);
  return Number.isInteger(n) && n > 0 && n < 65536 ? n : fail(`bad port ${text}`);
}

for (const t of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  try {
    console.log(parsePort(t));
  } catch (e) {
    console.log(e instanceof Error ? e.message : String(e));
  }
}
""", ["8080 0 abc 443"],
         "Because `fail` returns `never`, the conditional's type is just `number` — `never` disappears from any union it joins."),
        ("`{}` versus `object`",
         r"""
function describeLoose(v: {}): string {
  return `${typeof v}`;
}
function describeObject(v: object): string {
  return `${Array.isArray(v) ? "array" : "object"} with ${Object.keys(v).length} keys`;
}
console.log([describeLoose(5), describeLoose("x"), describeLoose({ a: 1 })].join(" "));
console.log(describeObject({ a: 1, b: 2 }), "|", describeObject([1, 2, 3]));
""", [""],
         "`{}` accepts numbers and strings — it only excludes `null` and `undefined`. When you mean \"a real object\", the type is `object`."),
    ],
    errors=[
        (2322, r"""
type Status = "active" | "paused" | "closed";
function label(s: Status): string {
  switch (s) {
    case "active":
      return "Active";
    case "paused":
      return "Paused";
    default: {
      const unhandled: never = s;
      return unhandled;
    }
  }
}
console.log(label("closed"));
""", "`\"closed\"` reaches the `default` branch, so `s` there is `\"closed\"`, not `never`. This is the exhaustiveness check doing its job: add the missing case."),
        (18046, r"""
const data: unknown = JSON.parse('{"name":"ada"}');
console.log(data.name);
""", "Nothing can be done with an `unknown` until it's narrowed — which is the point. Check it's an object with a `name` first (or validate it into a real type)."),
    ],
    pitfalls=[
        ("`default:` swallows new variants",
         r"""
type Shape = { kind: "circle"; r: number } | { kind: "square"; s: number } | { kind: "triangle"; b: number; h: number };
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.r ** 2;
    case "square":
      return shape.s ** 2;
    default:
      return 0;
  }
}
console.log(area({ kind: "triangle", b: 4, h: 3 }).toFixed(1));
""",
         r"""
type Shape = { kind: "circle"; r: number } | { kind: "square"; s: number } | { kind: "triangle"; b: number; h: number };
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.r ** 2;
    case "square":
      return shape.s ** 2;
    case "triangle":
      return (shape.b * shape.h) / 2;
    default: {
      const unhandled: never = shape;
      throw new Error(`unhandled ${JSON.stringify(unhandled)}`);
    }
  }
}
console.log(area({ kind: "triangle", b: 4, h: 3 }).toFixed(1));
""",
         "A catch-all `default` compiles no matter which variants exist, so the new triangle silently has area 0. With the `never` check, forgetting the `triangle` case is a compile error."),
        ("Storing a `void` result",
         r"""
const names = ["ada", "bo"];
const upper = names.forEach((n) => n.toUpperCase());
console.log(String(upper));
""",
         r"""
const names = ["ada", "bo"];
const upper = names.map((n) => n.toUpperCase());
console.log(String(upper));
""",
         "`forEach` returns `void` — there is nothing to keep. TypeScript lets you store it (as `undefined`), which is why this compiles. `map` is the method that returns results."),
        ("`typeof v === \"object\"` includes `null`",
         r"""
function keyCount(v: unknown): number {
  if (typeof v === "object") return Object.keys(v as object).length;
  return 0;
}
try {
  console.log([{ a: 1 }, null].map(keyCount).join(" "));
} catch (e) {
  console.log("crashed:", e instanceof Error ? e.constructor.name : "?");
}
""",
         r"""
function keyCount(v: unknown): number {
  if (typeof v === "object" && v !== null) return Object.keys(v).length;
  return 0;
}
console.log([{ a: 1 }, null].map(keyCount).join(" "));
""",
         "The compiler was right to keep `v` as `object | null` — the `as object` cast silenced it, and `Object.keys(null)` throws. Narrow properly and no cast is needed."),
    ],
    later=[
        "**Week 12 — Discriminated unions.** The tag-and-switch pattern the `never` check guards.",
        "**Week 21 — Conditional types.** `never` as the empty union: how `Exclude` removes members.",
        "**Week 25 — Errors.** `catch (e)` gives `e: unknown` — narrowing it is the first thing every handler does.",
    ],
    exercises=[
        _drill("ts_top_bottom-exhaustive", "Make the switch exhaustive",
               "Replace `____` with the line that makes this `switch` fail to compile if a new `Op` is added without a case — assign `op` to a variable of type `never`.",
               r"""
import * as fs from "fs";
type Op = "add" | "sub" | "mul";
function apply(op: Op, a: number, b: number): number {
  switch (op) {
    case "add":
      return a + b;
    case "sub":
      return a - b;
    case "mul":
      return a * b;
    default: {
      const unhandled: never = op;
      throw new Error(`unhandled ${unhandled}`);
    }
  }
}
for (const line of fs.readFileSync(0, "utf8").trim().split("\n")) {
  const [op = "add", a = "0", b = "0"] = line.trim().split(/\s+/);
  console.log(apply(op as Op, Number(a), Number(b)));
}
""", ["const unhandled: never = op;"], ["add 2 3\nmul 4 5\nsub 1 9"],
               hint="After every case, what type is left for `op`?"),
        _drill("ts_top_bottom-fail", "A function that never returns",
               "Replace `____` with the return type of `fail`, so the ternary in `parseAge` has type `number`.",
               r"""
import * as fs from "fs";
function fail(message: string): never {
  throw new Error(message);
}
function parseAge(text: string): number {
  const n = Number(text);
  return Number.isInteger(n) && n >= 0 ? n : fail(`bad age ${text}`);
}
for (const t of fs.readFileSync(0, "utf8").trim().split(/\s+/)) {
  try {
    console.log(parseAge(t) + 1);
  } catch (e) {
    console.log(e instanceof Error ? e.message : "?");
  }
}
""", ["never"], ["30 -1 x 0"],
               hint="The type with no values — for a function that always throws."),
        _chal("ts_top_bottom-events", "An exhaustive event handler", "Medium",
              "Each input line is a JSON event: `{\"type\":\"click\",\"x\":…,\"y\":…}`, `{\"type\":\"key\",\"key\":…}` or `{\"type\":\"scroll\",\"dy\":…}`. Model them as a union, handle each in an exhaustive `switch` (with a `never` check), and print `click at x,y`, `key <k>`, or `scroll up|down <|dy|>`. A line whose type is none of these prints `ignored <type>` — check that at runtime before trusting the union.",
              r"""
type Event =
  | { type: "click"; x: number; y: number }
  | { type: "key"; key: string }
  | { type: "scroll"; dy: number };
const KNOWN = ["click", "key", "scroll"];
function describe(e: Event): string {
  switch (e.type) {
    case "click":
      return `click at ${e.x},${e.y}`;
    case "key":
      return `key ${e.key}`;
    case "scroll":
      return `scroll ${e.dy < 0 ? "up" : "down"} ${Math.abs(e.dy)}`;
    default: {
      const unhandled: never = e;
      return String(unhandled);
    }
  }
}
for (const line of input.split("\n")) {
  const raw = JSON.parse(line) as { type: string };
  console.log(KNOWN.includes(raw.type) ? describe(raw as Event) : `ignored ${raw.type}`);
}
""", ['{"type":"click","x":3,"y":4}\n{"type":"key","key":"Enter"}\n{"type":"scroll","dy":-120}\n{"type":"drag"}',
      '{"type":"scroll","dy":40}'],
              hint="Switch on the tag; the `default` branch assigns the event to `never`."),
    ],
    quiz=[
        _cq("What can you do with a value of type `unknown` before narrowing it?", "Pass it around or store it — nothing that reads from it",
            ["Anything, like `any`", "Only read its properties", "Nothing; it can't even be stored"],
            "It's the safe top type: everything fits in, nothing comes out unchecked."),
        _cq("What is the return type of a function that always throws?", "`never`", ["`void`", "`undefined`", "`unknown`"],
            "It never produces a value."),
        _cq("Why does `const unhandled: never = s` in a `default` branch catch missing cases?", "If a case is missing, `s` isn't `never` there, and the assignment fails to compile",
            ["It throws at runtime", "It only works with enums", "It disables the switch"],
            "The type left after all narrowing must be empty."),
        _cq("Which values does the type `{}` accept?", "Anything except `null` and `undefined` — including numbers and strings",
            ["Only empty objects", "Only objects", "Nothing"],
            "Use `object` for non-primitives, `Record<string, never>` for truly empty objects."),
        _cq("A slot typed `() => void` receives `() => 5`. Is that allowed?", "Yes — `void` means the result is ignored",
            ["No, it must return `undefined`", "Only with a cast", "Only for async functions"],
            "That's why `forEach` callbacks can return things."),
    ],
    interview=[
        ("`any` vs `unknown` vs `never`?",
         "`any` switches checking off in both directions. `unknown` is the type-safe top: anything can be assigned to it, but you must narrow before using it. `never` is the bottom: nothing can be assigned to it — it's the type of impossible code and the empty union."),
        ("How do you make a `switch` over a union exhaustive?",
         "Handle every case and, in `default`, assign the value to a `never` variable (or `satisfies never`). If someone adds a variant, that line stops compiling and points at every switch to update."),
        ("What's the difference between `object`, `{}` and `Object`?",
         "`object` is any non-primitive. `{}` is any value that isn't `null` or `undefined`, primitives included. `Object` behaves almost like `{}`. For \"some object\" use `object`; for a dictionary use `Record<string, unknown>`."),
    ],
)
