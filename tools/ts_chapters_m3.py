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
