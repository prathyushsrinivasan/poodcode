# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 8 — types that describe your data.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 8 ---------------------------------------------------------------
_WEEKS.append(_week(
    8, 2, _M2,
    "Types that Describe Your Data",
    "Name the shapes your program works with, let inference do the rest, and fold a list to one value with reduce.",
    """
You have been using types since week 1 — TypeScript worked most of them out
silently. This week you take the wheel: **naming** the shapes your data has, so
the compiler can check every place they're used.

The payoff is not decoration. Once `Expense` is a named type, a misspelled
`e.amont`, a forgotten field, a string where a number belongs — each becomes a
red squiggle as you type instead of a wrong number in a report. That is the
entire reason TypeScript exists.

Two things to keep straight all week:

- **Types are erased before the program runs.** Nothing you write here changes
  behaviour at runtime. The drills therefore still exercise real logic; the
  types describe it.
- **Annotate boundaries, infer the middle.** Function parameters and returns,
  and empty containers, are worth annotating. Local variables with an obvious
  initialiser are not — `const n = 5` is already a `number`.

The week closes with **`reduce`**, the last of the big array methods and the one
that generalises all the others.

⏱️ Budget about **nine hours**, spread over several sittings.
""",
    objectives=[
        "Annotate values and functions, and know when inference is enough",
        "Name a shape with a type alias or an interface, and say which to reach for",
        "Type arrays of records, and use a tuple for a fixed-length pair",
        "Mark properties optional, and understand structural typing and excess-property checks",
        "Write a function type, and type a callback parameter",
        "Fold a list to a number, a string or an object with reduce",
        "Design a type for real-world data and process it end to end",
        "Explain that annotations are erased at runtime, and validate data where it enters",
        "Write a boundary function that turns untrusted text into a typed, checked record",
    ],
    why="A named type is documentation the compiler enforces. It is the cheapest bug prevention available, and it is what makes a codebase survive being edited six months later by someone who has forgotten it.",
    est_minutes=550,
    glossary=[
        _gloss("annotation", "A written type after a colon: let n: number."),
        _gloss("inference", "TypeScript working the type out from the value."),
        _gloss("type alias", "A name for any type: type ID = string."),
        _gloss("interface", "A name for the shape of an object type."),
        _gloss("structural typing", "Compatibility by SHAPE, not by name — if it has the right fields, it fits."),
        _gloss("excess property check", "TypeScript rejects unknown fields on an object literal assigned straight to a typed slot."),
        _gloss("optional property", "A field marked `?` that may be absent."),
        _gloss("readonly", "A property that cannot be reassigned after creation."),
        _gloss("union", "A type that is one of several: string | number."),
        _gloss("literal type", "A type that is one exact value: \"paid\"."),
        _gloss("tuple", "A fixed-length array with a type per position: [string, number]."),
        _gloss("Array<T>", "The long form of T[] — the same type."),
        _gloss("function type", "(a: number) => string — the shape of a function."),
        _gloss("void", "The return type of a function that returns nothing useful."),
        _gloss("any", "Opts out of checking entirely. Almost always the wrong answer."),
        _gloss("unknown", "Like any, but you must narrow it before use. The safe version."),
        _gloss(".reduce(f, seed)", "Folds a list into a single accumulated value."),
        _gloss("accumulator (reduce)", "The value carried from one step to the next."),
        _gloss("boundary", "The one place where outside data is validated and turned into your types."),
        _gloss("erasure", "Annotations exist only while compiling; nothing of them survives into the running code."),
        _gloss("any", "Switches type checking off for a value. Every any is a small debt."),
        _gloss("assertion (as)", "A promise to the compiler about a type. Checked never, believed always."),
        _gloss("NaN", "The number you get from a failed conversion. Test for it with Number.isNaN."),
    ],
    cheatsheet="""
```ts
// ---- annotate & infer -------------------------------------------------
const price: number = 10;      // annotation (often unnecessary)
const qty = 3;                 // inferred as number — fine
let names: string[] = [];      // needed: nothing to infer from
function f(s: string, n: number): string { return s.repeat(n); }

// ---- name a shape ------------------------------------------------------
interface Point { x: number; y: number }
type User = { name: string; admin: boolean };
type ID = string;                       // alias for any type, not just objects
type Status = "paid" | "unpaid";        // a union of literal types

// ---- arrays & tuples ---------------------------------------------------
const xs: number[] = [1, 2, 3];
const ys: Array<number> = [1, 2, 3];    // identical
const rows: User[] = [];
const pair: [string, number] = ["a", 1];   // fixed length, typed per slot

// ---- optional & readonly ------------------------------------------------
interface Expense {
  desc: string;
  amount: number;
  note?: string;              // may be absent -> string | undefined
  readonly id: string;        // set at creation, never reassigned
}

// ---- function types ------------------------------------------------------
type Mapper = (x: number) => number;
const double: Mapper = (x) => x * 2;        // parameter type inferred from Mapper
function apply(f: (x: number) => number, x: number): number { return f(x); }

// ---- reduce ---------------------------------------------------------------
[1, 2, 3].reduce((sum, x) => sum + x, 0)          // 6      fold to a number
words.reduce((acc, w) => acc + w[0], "")          // fold to a string
items.reduce((acc, it) => {                        // fold to an object
  acc[it.tag] = (acc[it.tag] ?? 0) + 1;
  return acc;
}, {} as { [key: string]: number })
```
""",
    self_check=[
        "Can you say which annotations are worth writing and which are noise?",
        "Can you name an object shape and use it on a function parameter?",
        "Can you explain what 'structural typing' means in one sentence?",
        "Can you say what `note?: string` does to the type of `e.note`?",
        "Can you write the type of a function that takes a string and returns a number?",
        "Can you total a field with reduce, and say what the seed is for?",
        "Can you say why `any` is worse than `unknown`?",
        "Can you say what happens to your annotations when the program runs?",
        "Can you write a parse function that rejects malformed input instead of crashing on it?",
    ],
    review=[
        _q("What happens to type annotations at runtime?",
           ["They slow it down", "They are erased before the program runs",
            "They become comments", "They are printed"], 1,
           "Checked while you write, then stripped."),
        _q("`interface` names…",
           ["a running object", "the shape of an object type", "a loop", "a value"], 1,
           "A reusable object shape."),
        _q("Which is TRUE of `type` versus `interface`?",
           ["type only works for objects", "interface only works for objects",
            "they are completely identical", "type cannot be exported"], 1,
           "A type alias can name ANY type — unions, functions, primitives — while an interface names object shapes."),
        _q("TypeScript decides two types are compatible based on…",
           ["their names", "their shape", "declaration order", "the file they are in"], 1,
           "Structural typing: the right fields is enough."),
        _q("`note?: string` means `e.note` has type…",
           ["string", "string | undefined", "undefined", "any"], 1,
           "Optional adds undefined to the type."),
        _q("`[string, number]` describes…",
           ["an array of strings and numbers", "a fixed-length pair, typed per position",
            "a union", "an object"], 1,
           "A tuple."),
        _q("`[1,2,3].reduce((s, x) => s + x, 0)` is…", ["0", "6", "123", "3"], 1,
           "It folds to the sum."),
        _q("The seed (second argument) of reduce is…",
           ["the first element", "the starting accumulator", "the length", "optional and pointless"], 1,
           "It is what the accumulator begins as — and the answer for an empty array."),
        _q("Why prefer `unknown` to `any`?",
           ["it is faster", "unknown forces you to narrow before use", "any is deprecated",
            "no difference"], 1,
           "any switches checking off entirely; unknown keeps you honest."),
        _q("Which annotation is genuinely needed?",
           ["const n: number = 5", "const s: string = \"a\"", "const xs: string[] = []",
            "const b: boolean = true"], 2,
           "An empty array gives inference nothing to work from."),
        _q("At runtime, annotations are…",
           ["checked on assignment", "erased", "stored with the value", "converted to guards"], 1,
           "Which is exactly why boundaries need real checks."),
        _q("`Number(\"oops\")` gives…",
           ["a type error", "NaN, whose type is number", "0", "undefined"], 1,
           "The annotation is satisfied and the value is still wrong."),
        _q("`value as Config` at runtime…",
           ["validates the shape", "does nothing", "copies the object", "throws on mismatch"], 1,
           "An assertion silences the compiler; it checks nothing."),
    ],
    milestone="Budget Buddy is now fully typed — the compiler guards its data, and reduce folds a whole ledger into a summary. That's Month 2 complete.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w8-annotations", "Annotations & inference",
            "Writing types — and knowing when not to.",
            """
An **annotation** is a type written after a colon:

```ts
const price: number = 10;
const label: string = "Coffee";
let names: string[] = [];
function repeat(s: string, n: number): string {
  return s.repeat(n);
}
```

**Inference** is TypeScript working it out for you:

```ts
let price = 10;              // inferred: number
let label = "Coffee";        // inferred: string
const xs = [1, 2, 3];        // inferred: number[]
```

Both are equally type-safe. `let price: number = 10` adds nothing the compiler
didn't already know — it's just more to read and more to keep in sync.

**`const` infers something narrower.** A `let` can be reassigned, so TypeScript
gives it the general type. A `const` never can, so it gets the type of that one
value — the **literal type**:

```ts
let a = 10;        // number
const b = 10;      // 10      <- not number!
const c = "paid";  // "paid"  <- not string!
```

This looks like a curiosity and turns into the foundation of week 9: `"paid"` as
a *type* is what makes `Status = "paid" | "unpaid"` mean anything. The narrow
type **widens** as soon as the value is copied somewhere reassignable, which is
why it rarely gets in your way:

```ts
const b = 10;      // 10
let d = b;         // number — d could become anything, so the literal is lost
```

**The rule of thumb: annotate the boundaries, infer the middle.**

| annotate | because |
|---|---|
| function parameters | there is no value to infer from |
| function return types | it pins your intent, and catches a wrong branch |
| empty arrays/objects | `[]` could be an array of anything |
| a value that should be narrower than its literal | `let s: string` when you'll reassign |

| don't annotate | because |
|---|---|
| `const n = 5` | obviously a number |
| `const xs = [1, 2]` | obviously `number[]` |
| a local computed from typed things | inference follows the chain |

**Why annotate a return type** when TypeScript can infer it? Because inference
reports what your code *does*; an annotation states what it's *meant* to do. If
a branch accidentally returns a string, an annotated function errors at the
mistake. An unannotated one silently widens its return type and the error
surfaces somewhere else entirely.

**`any` turns checking off:**

```ts
let x: any = 5;
x.foo.bar();     // no complaint — and a crash at runtime
```

Every `any` is a hole in the net. `unknown` is the honest alternative: it
accepts anything but makes you check before you use it (week 9's narrowing is
exactly that skill).

> ⚠️ **Common mistakes:** annotating everything and drowning the code in noise;
> reaching for `any` to silence an error rather than understanding it; and
> forgetting that annotations vanish at runtime — they never validate real input.
""",
            warmup=[
                _q("`let n = 5;` — what type does TypeScript infer?",
                   ["any", "number", "5", "unknown"], 1,
                   "From the value — and `let` can be reassigned, so it widens to number."),
                _q("`const n = 5;` — what type does TypeScript infer?",
                   ["any", "number", "5", "unknown"], 2,
                   "A const can never hold anything else, so its type is the one value 5. "
                   "It widens to number the moment you copy it somewhere reassignable."),
                _q("Which annotation is genuinely required?",
                   ["const a = 1", "const b: number = 1", "const c: string[] = []",
                    "const d = \"x\""], 2,
                   "An empty array has nothing to infer from."),
                _q("`let x: any = 5; x.foo();` at compile time…",
                   ["errors", "is accepted", "warns", "is impossible"], 1,
                   "any accepts anything — and then it crashes when it runs."),
                _q("Annotations at runtime…",
                   ["validate input", "are erased", "slow things down", "become comments"], 1,
                   "They never check real data — that is your job."),
            ],
            exercises=[
                _ex("tscourse-w8-an-1", "Typed total",
                    "Compute price * qty into the annotated total.",
                    'const price: number = 10;\nconst qty: number = 3;\n'
                    'const total: number = price * qty;\nconsole.log(total);\n',
                    'price * qty', [("", "30")],
                    hints=["Multiply the two annotated numbers."]),
                _ex("tscourse-w8-an-2", "Typed repeat",
                    "Return the string repeated n times.",
                    'function repeat(s: string, n: number): string {\n  return s.repeat(n);\n}\n'
                    'console.log(repeat("ab", 3));\n',
                    's.repeat(n)', [("", "ababab")],
                    hints=["Strings have a .repeat(n) method."]),
                _ex("tscourse-w8-an-3", "An annotated empty array",
                    "Collect the doubled numbers into the annotated array and print them.",
                    _NUMS + 'const out: number[] = [];\n'
                    'for (const x of nums) {\n  out.push(x * 2);\n}\n'
                    'console.log(out.join(" "));\n',
                    'out.push(x * 2);', [("1 2 3", "2 4 6"), ("5", "10")],
                    hints=["The array is already annotated — just fill it.",
                           "Write out.push(x * 2);"]),
                _ex("tscourse-w8-an-4", "Annotate the parameters",
                    "Fill in the parameter list: a string and a number.",
                    'function tag(name: string, n: number): string {\n'
                    '  return `${name}-${n}`;\n}\n'
                    'console.log(tag("row", 3));\n',
                    'name: string, n: number', [("", "row-3")],
                    hints=["Each parameter gets its own annotation, separated by a comma.",
                           "Write name: string, n: number."]),
                _ex("tscourse-w8-an-5", "A narrower let",
                    "Annotate `status` so it can later hold any string, then print it.",
                    'let status: string = "new";\nstatus = "done";\nconsole.log(status);\n',
                    ': string = "new"', [("", "done")],
                    hints=['Without the annotation this would still infer string — but stating it documents the intent.',
                           'Write : string = "new".']),
                _fix("tscourse-w8-an-fix1", "Fix the operator",
                     "This should print 30 but a wrong operator sneaks in. Fix it.",
                     'const price: number = 10;\nconst qty: number = 3;\n'
                     'const total: number = price + qty;\nconsole.log(total);\n',
                     'const price: number = 10;\nconst qty: number = 3;\n'
                     'const total: number = price * qty;\nconsole.log(total);\n',
                     [("", "30")],
                     hints=["price + qty is 13.", "A line total multiplies."]),
                _fix("tscourse-w8-an-fix2", "Fix the any-shaped hole",
                     "`any` let a string through where a number was meant, so this prints `102` instead of 12. Give the value a real type and convert the input.",
                     _FS + 'const raw: any = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(raw + 2);\n',
                     _FS + 'const raw: number = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(raw + 2);\n',
                     [("10", "12"), ("5", "7")],
                     hints=["any silenced the check; the value really is a string, so + joined.",
                            "Annotate it as number and convert with Number(...)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("'Annotate the boundaries, infer the middle' means…",
                   ["annotate everything", "annotate parameters, returns and empty containers",
                    "never annotate", "annotate only locals"], 1,
                   "Those are the places inference has nothing to work from, or where intent matters."),
                _q("An annotated return type helps because…",
                   ["it is faster", "an accidental wrong return errors at the function, not far away",
                    "it is required", "it changes the value"], 1,
                   "Inference reports what the code does; the annotation states what it should do."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w8-aliases", "Naming shapes: type & interface",
            "One name, used everywhere.",
            """
Writing the same inline shape three times is how it drifts:

```ts
function total(e: { desc: string; amount: number }): number { ... }
function label(e: { desc: string; amount: number }): string { ... }
```

Name it once instead. Two ways, both fine:

```ts
interface Expense {
  desc: string;
  amount: number;
}

type Expense = {
  desc: string;
  amount: number;
};
```

Then use the name:

```ts
function total(e: Expense): number { return e.amount; }
const rows: Expense[] = [];
```

**`type` versus `interface`.** For object shapes they are nearly
interchangeable. The real difference:

- **`type` can name *any* type**, not just objects:

```ts
type ID = string;
type Status = "paid" | "unpaid";              // a union
type Mapper = (x: number) => number;          // a function
type Pair = [string, number];                 // a tuple
```

- **`interface` is only for object shapes**, but it can be *reopened* — declare
  it twice and the members merge. That's occasionally essential for extending
  library types, and occasionally a surprise.

A workable convention: **`interface` for object shapes you might extend,
`type` for everything else.** Pick one and be consistent; a codebase that mixes
them arbitrarily is just noise.

**Extending:**

```ts
interface Timestamped { created: string }
interface Expense extends Timestamped { desc: string; amount: number }

type Expense2 = Timestamped & { desc: string; amount: number };   // & = intersection
```

**Structural typing** is the deep idea underneath all of this. TypeScript does
not care what a type is *called* — only what shape it has:

```ts
interface Point { x: number; y: number }
const thing = { x: 1, y: 2, z: 3 };
const p: Point = thing;    // ✅ fine — it has x and y
```

A value fits if it has the required members. This is why you'll sometimes see a
function parameter typed with an inline shape listing only the two fields it
actually needs — anything with those fields can be passed.

> ⚠️ **Common mistakes:** using `,` instead of `;` between interface members
> (both are actually allowed, but be consistent); expecting an interface to
> reject extra fields on a variable (it doesn't — see the next lesson); and
> agonising over `type` versus `interface` when it rarely matters.
""",
            warmup=[
                _q("Which can name a union like `\"a\" | \"b\"`?",
                   ["interface", "type", "both", "neither"], 1,
                   "A type alias names any type; an interface names object shapes."),
                _q("TypeScript decides compatibility by…",
                   ["the type's name", "the shape", "the file", "declaration order"], 1,
                   "Structural typing."),
                _q("`interface A extends B` means A…",
                   ["replaces B", "has B's members plus its own", "is unrelated to B",
                    "is a copy of B"], 1,
                   "Extension adds to the inherited members."),
                _q("An object with EXTRA fields assigned to a variable of a narrower interface is…",
                   ["always rejected", "accepted when it comes from a variable",
                    "an error at runtime", "converted"], 1,
                   "Structural typing accepts it; only fresh object literals get the excess-property check."),
            ],
            exercises=[
                _ex("tscourse-w8-al-1", "Use a named shape",
                    "Return the Manhattan distance of the point from the origin.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'function dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\n'
                    'console.log(dist({ x: 3, y: -4 }));\n',
                    'Math.abs(p.x) + Math.abs(p.y)', [("", "7")],
                    hints=["Add the absolute values of the two coordinates."]),
                _ex("tscourse-w8-al-2", "A type alias for a record",
                    "Return `<name> (admin)` when admin is true, otherwise just the name.",
                    'type User = { name: string; admin: boolean };\n'
                    'function label(u: User): string {\n'
                    '  return u.admin ? `${u.name} (admin)` : u.name;\n}\n'
                    'console.log(label({ name: "Ada", admin: true }));\n'
                    'console.log(label({ name: "Bo", admin: false }));\n',
                    'u.admin ? `${u.name} (admin)` : u.name',
                    [("", "Ada (admin)\nBo")],
                    hints=["A ternary picks between the two strings."]),
                _ex("tscourse-w8-al-3", "Name a non-object type",
                    "Alias `Status` to the two allowed strings, then print the given status.",
                    _FS + 'type Status = "paid" | "unpaid";\n'
                    'const s: Status = fs.readFileSync(0, "utf8").trim() === "paid" ? "paid" : "unpaid";\n'
                    'console.log(s);\n',
                    '"paid" | "unpaid"', [("paid", "paid"), ("no", "unpaid")],
                    hints=["A type alias can name a union of exact string values.",
                           'Write "paid" | "unpaid".'],
                    difficulty="Medium"),
                _ex("tscourse-w8-al-4", "Extend an interface",
                    "Total the amount across the extended records.",
                    'interface Timestamped {\n  created: string;\n}\n'
                    'interface Expense extends Timestamped {\n  desc: string;\n  amount: number;\n}\n'
                    'const rows: Expense[] = [\n'
                    '  { created: "mon", desc: "coffee", amount: 3 },\n'
                    '  { created: "tue", desc: "book", amount: 12 },\n'
                    '];\n'
                    'let total = 0;\nfor (const r of rows) {\n  total += r.amount;\n}\n'
                    'console.log(total);\n',
                    'total += r.amount;', [("", "15")],
                    hints=["The extended interface has both its own fields and the inherited one.",
                           "Accumulate r.amount."]),
                _ex("tscourse-w8-al-5", "Structural fit",
                    "The value has an extra field, but it still fits Point. Print its distance.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'const thing = { x: 1, y: 2, z: 3 };\n'
                    'const p: Point = thing;\n'
                    'console.log(p.x + p.y);\n',
                    'const p: Point = thing;', [("", "3")],
                    hints=["Assigning from a VARIABLE skips the excess-property check.",
                           "Write const p: Point = thing;"],
                    difficulty="Medium"),
                _fix("tscourse-w8-al-fix1", "Fix the distance",
                     "Negative coordinates break this — dist({x:3,y:-4}) should be 7. Fix it.",
                     'interface Point {\n  x: number;\n  y: number;\n}\n'
                     'function dist(p: Point): number {\n  return p.x + p.y;\n}\n'
                     'console.log(dist({ x: 3, y: -4 }));\n',
                     'interface Point {\n  x: number;\n  y: number;\n}\n'
                     'function dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\n'
                     'console.log(dist({ x: 3, y: -4 }));\n',
                     [("", "7")],
                     hints=["3 + (-4) is -1, which is not a distance.",
                            "Wrap each coordinate in Math.abs."]),
                _fix("tscourse-w8-ali-fix2", "Fix the shape that was only promised",
                     "This should print `ada <ada@example.com>` but the email comes out undefined. An assertion was used to force an incomplete object into the shape.",
                     'interface User {\n  name: string;\n  email: string;\n}\n'
                     'function line(u: User): string {\n'
                     '  return `${u.name} <${u.email}>`;\n}\n'
                     'const u = { name: "ada" } as User;\n'
                     'console.log(line(u));\n',
                     'interface User {\n  name: string;\n  email: string;\n}\n'
                     'function line(u: User): string {\n'
                     '  return `${u.name} <${u.email}>`;\n}\n'
                     'const u: User = { name: "ada", email: "ada@example.com" };\n'
                     'console.log(line(u));\n',
                     [("", "ada <ada@example.com>")],
                     hints=["`as User` promised a field that was never supplied.",
                            "Annotate the variable instead of asserting it, and give it every required field."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which CANNOT be expressed with `interface`?",
                   ["an object shape", "extending another shape",
                    "a union of two string literals", "a method signature"], 2,
                   "Unions need a type alias."),
                _q("Structural typing means a value fits a type when…",
                   ["it was declared with that type", "it has the required members",
                    "it is in the same file", "it is a class"], 1,
                   "Names are irrelevant; shape is everything."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w8-collections", "Typed arrays & tuples",
            "Describing lists and fixed-length pairs.",
            """
An array's type says what's inside it:

```ts
const xs: number[] = [1, 2, 3];
const names: string[] = ["Ada"];
const rows: Expense[] = [];
```

`Array<number>` is the identical type written the long way:

```ts
const ys: Array<number> = [1, 2, 3];   // same as number[]
```

Use whichever your codebase uses. `T[]` is shorter; `Array<T>` occasionally
reads better for complicated element types.

**Arrays of arrays:**

```ts
const grid: number[][] = [[1, 2], [3, 4]];
```

Read `number[][]` from the inside out: an array of (arrays of number).

**An array of a union** versus **a union of arrays** are different, and the
distinction bites:

```ts
const a: (string | number)[] = ["x", 1];   // each element is either
const b: string[] | number[] = ["x", "y"]; // the whole array is one or the other
```

**Tuples** are fixed-length arrays with a type per position:

```ts
const pair: [string, number] = ["coffee", 3];
pair[0].toUpperCase();     // TypeScript knows this one is a string
pair[1].toFixed(2);        // ...and this one is a number
```

This is exactly what `Object.entries` gives you — `[key, value]` pairs — which
is why destructuring them works so neatly:

```ts
for (const [k, v] of Object.entries(counts)) {
  console.log(`${k}=${v}`);
}
```

A tuple is the right tool when a pair genuinely has a fixed shape and order.
When there are more than two or three slots, or the order isn't obvious, an
object with names is kinder to read.

**`readonly`** stops reassignment:

```ts
const xs: readonly number[] = [1, 2, 3];
xs.push(4);       // ❌ compile error
```

It's a compile-time promise, not a runtime freeze — but as a signal in a
function signature ("I will not modify your array") it is genuinely valuable.

> ⚠️ **Common mistakes:** writing `number[]` when you meant a tuple and losing
> the per-position types; forgetting that an empty array literal needs an
> annotation; and expecting `readonly` to protect the array at runtime.
""",
            warmup=[
                _q("`Array<string>` and `string[]` are…",
                   ["different", "the same type", "only for classes", "invalid"], 1,
                   "Two spellings of one type."),
                _q("`number[][]` describes…",
                   ["two numbers", "an array of arrays of number", "a tuple",
                    "a union"], 1, "Read it inside out."),
                _q("`const p: [string, number] = [\"a\", 1];` — what is `p.length`?",
                   ["any", "exactly 2", "1", "unknown"], 1, "Tuples are fixed length."),
                _q("`Object.entries(o)` gives you an array of…",
                   ["keys", "values", "[key, value] tuples", "objects"], 2,
                   "Which is why `for (const [k, v] of ...)` works."),
            ],
            exercises=[
                _ex("tscourse-w8-co-1", "A typed list of records",
                    "Total the amounts across the typed array.",
                    'interface Item {\n  name: string;\n  price: number;\n}\n'
                    'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                    'let total = 0;\nfor (const it of items) {\n  total += it.price;\n}\n'
                    'console.log(total);\n',
                    'total += it.price;', [("", "10")],
                    hints=["Accumulate the price field."]),
                _ex("tscourse-w8-co-2", "Array of arrays",
                    "Print the value at row 1, column 0 of the typed grid.",
                    'const grid: number[][] = [[1, 2], [3, 4]];\nconsole.log(grid[1]![0]);\n',
                    'grid[1]![0]', [("", "3")],
                    hints=["Index the row, then the column.",
                           "Each index can miss, so each one needs its own !."]),
                _ex("tscourse-w8-co-3", "A tuple",
                    "Print the pair as `COFFEE costs 3.00`, using both slots.",
                    'const pair: [string, number] = ["coffee", 3];\n'
                    'console.log(`${pair[0].toUpperCase()} costs ${pair[1].toFixed(2)}`);\n',
                    '${pair[0].toUpperCase()} costs ${pair[1].toFixed(2)}',
                    [("", "COFFEE costs 3.00")],
                    hints=["Slot 0 is a string and slot 1 is a number, so each has its own methods.",
                           "Use pair[0].toUpperCase() and pair[1].toFixed(2)."],
                    difficulty="Medium"),
                _ex("tscourse-w8-co-4", "Destructure entries",
                    "Print each key and value as `k=v` lines, sorted by key.",
                    'const counts: { [key: string]: number } = { b: 1, a: 2 };\n'
                    'for (const [k, v] of Object.entries(counts).sort()) {\n'
                    '  console.log(`${k}=${v}`);\n}\n',
                    'const [k, v] of', [("", "a=2\nb=1")],
                    hints=["Each entry is a [key, value] tuple, so destructure it in the loop header.",
                           "Write const [k, v] of."],
                    difficulty="Medium"),
                _ex("tscourse-w8-co-5", "An array of a union",
                    "The list holds numbers and strings. Print only the numbers, space-separated.",
                    'const mixed: (string | number)[] = [1, "a", 2, "b", 3];\n'
                    'const nums = mixed.filter((x) => typeof x === "number");\n'
                    'console.log(nums.join(" "));\n',
                    'typeof x === "number"', [("", "1 2 3")],
                    hints=["typeof reports the runtime type as a string.",
                           'Write typeof x === "number".'],
                    difficulty="Medium"),
                _fix("tscourse-w8-co-fix1", "Fix the grid index",
                     "This should print 3 (row 1, column 0) but prints 2. Fix it.",
                     'const grid: number[][] = [[1, 2], [3, 4]];\nconsole.log(grid[0]![1]);\n',
                     'const grid: number[][] = [[1, 2], [3, 4]];\nconsole.log(grid[1]![0]);\n',
                     [("", "3")],
                     hints=["The row index comes first, then the column.",
                            "Write grid[1]![0]! — one ! per index, and both are visibly there."]),
                _fix("tscourse-w8-col-fix2", "Fix the tuple order",
                     "Each pair is [name, quantity], so this should print `2 x apple`. The destructuring reads the slots the wrong way round.",
                     'type Pair = [string, number];\n'
                     'const items: Pair[] = [["apple", 2], ["fig", 5]];\n'
                     'for (const [qty, name] of items) console.log(`${qty} x ${name}`);\n',
                     'type Pair = [string, number];\n'
                     'const items: Pair[] = [["apple", 2], ["fig", 5]];\n'
                     'for (const [name, qty] of items) console.log(`${qty} x ${name}`);\n',
                     [("", "2 x apple\n5 x fig")],
                     hints=["A tuple's meaning is positional: slot 0 is the name, slot 1 is the quantity.",
                            "Name the destructured slots in the order the tuple declares them."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A tuple differs from an array in that…",
                   ["it is faster", "it has a fixed length with a type per position",
                    "it cannot hold objects", "it is immutable"], 1,
                   "Per-position types are the point."),
                _q("`(string | number)[]` versus `string[] | number[]`:",
                   ["identical", "the first allows mixed elements; the second is all-one-or-all-the-other",
                    "the second allows mixing", "both are invalid"], 1,
                   "Where the union sits changes everything."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w8-optional", "Optional fields & excess properties",
            "Describing data that isn't always complete.",
            """
Real records have holes. Mark a field with `?` when it may be absent:

```ts
interface Expense {
  desc: string;
  amount: number;
  note?: string;        // may be missing
}
```

`note?: string` means `e.note` has type `string | undefined`. TypeScript then
**makes you deal with it** before using it as a string:

```ts
e.note.toUpperCase();          // ❌ 'e.note' is possibly undefined
e.note?.toUpperCase();         // ✅ undefined when absent
(e.note ?? "").toUpperCase();  // ✅ a real fallback
```

That error is the feature. Week 7 taught you `?.` and `??` as runtime tools;
here the compiler tells you exactly where they are needed.

**Optional versus "present but undefined".** `note?: string` allows the field to
be missing entirely. `note: string | undefined` requires you to *write* it, even
if the value is `undefined`. Most of the time you want `?`.

**Default it once** rather than defending everywhere:

```ts
function describe(e: Expense): string {
  const note = e.note ?? "(no note)";
  return `${e.desc}: ${note}`;
}
```

**Excess property checks.** TypeScript is structural — extra fields are usually
fine. But a **fresh object literal** assigned straight to a typed slot gets an
extra check:

```ts
interface Point { x: number; y: number }

const p: Point = { x: 1, y: 2, z: 3 };   // ❌ 'z' does not exist in type 'Point'

const t = { x: 1, y: 2, z: 3 };
const q: Point = t;                       // ✅ fine — not a fresh literal
```

That inconsistency looks arbitrary and isn't: a literal written *right there*
with an unknown field is almost always a typo or a misunderstanding, so it's
worth flagging. A value that came from somewhere else may legitimately carry
more than this particular function needs.

**`readonly` on a property** prevents reassignment after construction:

```ts
interface Expense { readonly id: string; amount: number }
e.id = "x";        // ❌
e.amount = 5;      // ✅
```

Again: compile-time only. It documents and enforces intent while you write.

> ⚠️ **Common mistakes:** reading an optional field without handling
> `undefined`; using `||` instead of `??` and losing legitimate `0`/`""`; and
> being baffled by the excess-property check when a variable works but the same
> literal doesn't.
""",
            warmup=[
                _q("`note?: string` gives `e.note` the type…",
                   ["string", "string | undefined", "undefined", "any"], 1,
                   "Optional adds undefined."),
                _q("`const p: Point = { x:1, y:2, z:3 };` where Point has x and y…",
                   ["is fine", "errors — excess property on a fresh literal",
                    "drops z silently", "errors at runtime"], 1,
                   "Fresh literals get the extra check."),
                _q("`readonly id: string` prevents…",
                   ["reading id", "reassigning id after creation", "id being a string",
                    "nothing"], 1,
                   "Compile-time protection against reassignment."),
                _q("Which safely uppercases a possibly-missing note?",
                   ["e.note.toUpperCase()", "(e.note ?? \"\").toUpperCase()",
                    "e.note!.toUpperCase()", "String(e.note).toUpperCase()"], 1,
                   "Supply a real fallback before calling the method."),
            ],
            exercises=[
                _ex("tscourse-w8-op-1", "Handle the missing note",
                    "Print `coffee: (no note)` when the note is absent.",
                    'interface Expense {\n  desc: string;\n  amount: number;\n  note?: string;\n}\n'
                    'const e: Expense = { desc: "coffee", amount: 3 };\n'
                    'console.log(`${e.desc}: ${e.note ?? "(no note)"}`);\n',
                    'e.note ?? "(no note)"', [("", "coffee: (no note)")],
                    hints=["?? supplies a value only when the left side is missing.",
                           'Write e.note ?? "(no note)".']),
                _ex("tscourse-w8-op-2", "Safely call a method",
                    "Print the note uppercased, or an empty line when there is none.",
                    _FS + 'interface Expense {\n  desc: string;\n  note?: string;\n}\n'
                    'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const e: Expense = raw ? { desc: "x", note: raw } : { desc: "x" };\n'
                    'console.log((e.note ?? "").toUpperCase());\n',
                    '(e.note ?? "").toUpperCase()',
                    [("hi", "HI"), ("", "")],
                    hints=["Give it a real string first, then call the method.",
                           'Write (e.note ?? "").toUpperCase().'],
                    difficulty="Medium"),
                _ex("tscourse-w8-op-3", "Count the complete records",
                    "Count how many records actually have a note.",
                    'interface Expense {\n  desc: string;\n  note?: string;\n}\n'
                    'const rows: Expense[] = [\n'
                    '  { desc: "a", note: "x" },\n  { desc: "b" },\n  { desc: "c", note: "y" },\n];\n'
                    'console.log(rows.filter((r) => r.note !== undefined).length);\n',
                    'r.note !== undefined', [("", "2")],
                    hints=["An absent optional field reads as undefined.",
                           "Write r.note !== undefined."]),
                _ex("tscourse-w8-op-4", "Default it once",
                    "Pull the note out with a fallback at the top of the function.",
                    'interface Expense {\n  desc: string;\n  note?: string;\n}\n'
                    'function describe(e: Expense): string {\n'
                    '  const note = e.note ?? "(no note)";\n'
                    '  return `${e.desc}: ${note}`;\n}\n'
                    'console.log(describe({ desc: "coffee" }));\n'
                    'console.log(describe({ desc: "book", note: "gift" }));\n',
                    'const note = e.note ?? "(no note)";',
                    [("", "coffee: (no note)\nbook: gift")],
                    hints=["Handle the absence once, then the rest of the body is simple.",
                           'Write const note = e.note ?? "(no note)";'],
                    difficulty="Medium"),
                _ex("tscourse-w8-op-5", "Avoid the excess-property check",
                    "Assign the wider value through a variable so it satisfies Point.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'const t = { x: 1, y: 2, z: 3 };\nconst p: Point = t;\n'
                    'console.log(p.x + p.y);\n',
                    'const p: Point = t;', [("", "3")],
                    hints=["A fresh literal with an unknown field would be rejected; a variable is not.",
                           "Write const p: Point = t;"],
                    difficulty="Medium"),
                _fix("tscourse-w8-op-fix1", "Fix the lost zero",
                     "A discount of 0 is real, but this prints 5. Fix it.",
                     'interface Row {\n  discount?: number;\n}\n'
                     'const r: Row = { discount: 0 };\nconsole.log(r.discount || 5);\n',
                     'interface Row {\n  discount?: number;\n}\n'
                     'const r: Row = { discount: 0 };\nconsole.log(r.discount ?? 5);\n',
                     [("", "0")],
                     hints=["0 is falsy, so || replaces it.",
                            "For 'only when missing', use ??."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does TypeScript flag `z` in a fresh literal but not via a variable?",
                   ["a bug", "a literal with an unknown field is almost always a typo",
                    "variables are special", "it does not"], 1,
                   "The check targets the case where the mistake is most likely."),
                _q("`readonly` protects a field…",
                   ["at runtime", "at compile time only", "always", "never"], 1,
                   "Like every type feature, it is erased before running."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w8-fntypes", "Typing functions",
            "The shape of a function, as a type.",
            """
A function's type is written like an arrow function with no body:

```ts
(x: number) => number          // takes a number, returns a number
(s: string) => void            // takes a string, returns nothing useful
() => string                   // takes nothing, returns a string
```

You met this in week 5 as a *parameter* annotation. Now name it:

```ts
type Mapper = (x: number) => number;

const double: Mapper = (x) => x * 2;
const square: Mapper = (x) => x * x;
```

Notice `(x)` with **no annotation** in those arrows. Because the variable is
already typed as `Mapper`, TypeScript infers `x: number` from the target type.
This is called **contextual typing**, and it's why callbacks passed to `map` and
`filter` rarely need annotations:

```ts
nums.map((x) => x * 2);        // x is known to be number
```

**Typing a higher-order function:**

```ts
function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}
```

**Returning a function** — the closure from week 5, now typed:

```ts
function multiplier(factor: number): (x: number) => number {
  return (x) => x * factor;
}
```

**`void` deserves care.** It means "the caller should not rely on a return
value". A function typed `() => void` may actually return something; the type
just says nobody should use it. That's deliberate, and it's why
`items.forEach((x) => list.push(x))` type-checks even though `push` returns a
number.

**Optional and default parameters** appear in the type too:

```ts
type Fmt = (n: number, digits?: number) => string;
const fmt: Fmt = (n, digits = 2) => n.toFixed(digits);
```

The default lives in the implementation, not the type — a type describes what
callers may do, and callers may omit it either way.

> ⚠️ **Common mistakes:** writing `Function` as a type (it accepts anything and
> tells you nothing); annotating callback parameters that contextual typing
> already knows; and confusing a function's *type* `(x: number) => number` with
> a function *value* `(x) => x * 2`.
""",
            warmup=[
                _q("`(s: string) => number` describes…",
                   ["a string", "a function taking a string and returning a number",
                    "a number", "an object"], 1,
                   "It is the shape of a function."),
                _q("In `const f: Mapper = (x) => x * 2;` the type of `x` is…",
                   ["any", "inferred from Mapper", "unknown", "an error"], 1,
                   "Contextual typing supplies it."),
                _q("Why do `map` callbacks rarely need annotations?",
                   ["they are any", "the element type is known, so the parameter is inferred",
                    "annotations are banned", "map is special"], 1,
                   "Contextual typing again."),
                _q("A `() => void` function…",
                   ["must return undefined", "may return something, but callers should ignore it",
                    "cannot be called", "returns null"], 1,
                   "void is about what the caller may rely on."),
            ],
            exercises=[
                _ex("tscourse-w8-fn-1", "Name a function type",
                    "Alias `Mapper` to a function from number to number, then use it.",
                    'type Mapper = (x: number) => number;\n'
                    'const double: Mapper = (x) => x * 2;\n'
                    'console.log(double(21));\n',
                    '(x: number) => number', [("", "42")],
                    hints=["Write it like an arrow function with no body.",
                           "Write (x: number) => number."]),
                _ex("tscourse-w8-fn-2", "Rely on contextual typing",
                    "Fill in the squaring arrow. Its parameter needs no annotation.",
                    'type Mapper = (x: number) => number;\n'
                    'const square: Mapper = (x) => x * x;\n'
                    'console.log(square(7));\n',
                    '(x) => x * x', [("", "49")],
                    hints=["Mapper already says x is a number.",
                           "Write (x) => x * x."]),
                _ex("tscourse-w8-fn-3", "A typed higher-order function",
                    "Apply the function to its own result.",
                    'function applyTwice(f: (x: number) => number, x: number): number {\n'
                    '  return f(f(x));\n}\n'
                    'console.log(applyTwice((n) => n + 3, 10));\n',
                    'return f(f(x));', [("", "16")],
                    hints=["Call f on x, then call f on that.",
                           "Write return f(f(x));"],
                    difficulty="Medium"),
                _ex("tscourse-w8-fn-4", "A typed factory",
                    "Return a function that multiplies by the captured factor.",
                    _FS + 'function multiplier(factor: number): (x: number) => number {\n'
                    '  return (x) => x * factor;\n}\n'
                    'const triple = multiplier(3);\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'return (x) => x * factor;', [("5", "15"), ("10", "30")],
                    hints=["The return type already says what shape to hand back.",
                           "Write return (x) => x * factor;"],
                    difficulty="Medium"),
                _ex("tscourse-w8-fn-5", "Optional parameter in a type",
                    "Implement the formatter with a default of 2 digits.",
                    'type Fmt = (n: number, digits?: number) => string;\n'
                    'const fmt: Fmt = (n, digits = 2) => n.toFixed(digits);\n'
                    'console.log(fmt(3.14159));\nconsole.log(fmt(3.14159, 3));\n',
                    '(n, digits = 2) => n.toFixed(digits)',
                    [("", "3.14\n3.142")],
                    hints=["The default belongs in the implementation, not the type.",
                           "Write (n, digits = 2) => n.toFixed(digits)."],
                    difficulty="Medium"),
                _fix("tscourse-w8-fn-fix1", "Fix the passed-in call",
                     "This passes the RESULT where a function was expected, and crashes. Fix it.",
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'const double = (x: number): number => x * 2;\n'
                     'console.log(applyTwice(double(2), 5));\n',
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'const double = (x: number): number => x * 2;\n'
                     'console.log(applyTwice(double, 5));\n',
                     [("", "20")],
                     hints=["double(2) is the number 4; applyTwice needs something callable.",
                            "Pass the function itself: double."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`Function` as a type annotation is discouraged because…",
                   ["it is slow", "it accepts any function and describes nothing",
                    "it is deprecated", "it cannot be called"], 1,
                   "Write the actual signature instead."),
                _q("Contextual typing is…",
                   ["a runtime feature", "TypeScript inferring a parameter's type from where the function is used",
                    "an annotation", "a union"], 1,
                   "It is why callbacks stay clean."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w8-reduce", "reduce — fold a list to one value",
            "The most general array method.",
            """
`map` gives one output per input. `filter` gives some of the inputs. **`reduce`
gives one value for the whole list** — a total, a maximum, a joined string, a
whole object.

```ts
[1, 2, 3].reduce((sum, x) => sum + x, 0);    // 6
```

Two arguments:

1. a **callback** `(accumulator, element) => newAccumulator`
2. a **seed** — what the accumulator starts as

It walks the list, feeding each result into the next step:

| step | acc in | x | acc out |
|---|---|---|---|
| start | — | — | 0 |
| 1 | 0 | 1 | 1 |
| 2 | 1 | 2 | 3 |
| 3 | 3 | 3 | 6 |

That's the accumulator pattern from week 4, with the bookkeeping done for you.
The loop version is identical in meaning:

```ts
let sum = 0;
for (const x of a) sum = sum + x;
```

**The seed matters, and it is not optional in practice.** It sets both the
starting value *and* the accumulator's type, and it is the answer for an empty
array. Leave it out and `reduce` uses the first element instead — which throws
on an empty array. **Always pass a seed.**

**The accumulator doesn't have to be a number.** This is what makes `reduce`
general:

```ts
// to a string
words.reduce((acc, w) => acc + w[0], "");            // initials

// to a maximum
nums.reduce((best, x) => (x > best ? x : best), -Infinity);

// to an object — a tally
items.reduce((acc, it) => {
  acc[it.tag] = (acc[it.tag] ?? 0) + 1;
  return acc;
}, {} as { [key: string]: number });
```

That last one is week 7's tally, folded. Note the `return acc;` — a braced
callback must hand the accumulator back, and forgetting it is *the* classic
reduce bug: the next step receives `undefined`.

**When not to use it.** `reduce` can express `map` and `filter`, but doing so is
strictly worse — less clear and no faster. Reach for `reduce` when you're
genuinely collapsing a list to one value; use the specific method when one fits.
A `reduce` whose body is ten lines usually wants to be a plain loop.

> ⚠️ **Common mistakes:** omitting the seed; forgetting `return acc` in a braced
> callback; and mutating the seed object across calls (fine here, but a trap when
> the seed is shared).
""",
            warmup=[
                _q("`[2,3,5].reduce((s, x) => s + x, 0)` is…", ["0", "10", "235", "3"], 1,
                   "Folds to the sum."),
                _q("`[].reduce((s, x) => s + x, 0)` is…", ["0", "undefined", "an error", "NaN"], 0,
                   "The seed is the answer for an empty list."),
                _q("`[].reduce((s, x) => s + x)` — no seed — does what?",
                   ["gives 0", "gives undefined", "throws", "gives NaN"], 2,
                   "With no seed and no elements there is nothing to start from."),
                _q("A braced reduce callback that forgets `return acc` gives…",
                   ["the seed", "undefined into the next step", "an error", "the last element"], 1,
                   "The callback's value IS the next accumulator."),
            ],
            exercises=[
                _ex("tscourse-w8-rd-1", "Total with reduce",
                    "Fold the numbers to their sum.",
                    _NUMS + 'console.log(nums.reduce((sum, x) => sum + x, 0));\n',
                    'nums.reduce((sum, x) => sum + x, 0)',
                    [("1 2 3 4", "10"), ("5", "5")],
                    hints=["Callback first, then the seed.",
                           "Write nums.reduce((sum, x) => sum + x, 0)."]),
                _ex("tscourse-w8-rd-2", "Total a field",
                    "Fold the typed records to the sum of their prices.",
                    'interface Item {\n  name: string;\n  price: number;\n}\n'
                    'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                    'console.log(items.reduce((sum, it) => sum + it.price, 0));\n',
                    'sum + it.price', [("", "10")],
                    hints=["Each step adds one record's price to the running total."]),
                _ex("tscourse-w8-rd-3", "Fold to a string",
                    "Build the initials of the words: `ada bo cy` → `abc`.",
                    _WORDS + 'console.log(words.reduce((acc, w) => acc + w[0], ""));\n',
                    'acc + w[0]', [("ada bo cy", "abc"), ("x", "x")],
                    hints=["The accumulator is a string, seeded empty.",
                           "Write acc + w[0]."],
                    difficulty="Medium"),
                _ex("tscourse-w8-rd-4", "Fold to a maximum",
                    "Find the largest number with reduce.",
                    _NUMS + 'console.log(nums.reduce((best, x) => (x > best ? x : best), -Infinity));\n',
                    '(x > best ? x : best)',
                    [("3 9 2", "9"), ("-5 -2", "-2"), ("7", "7")],
                    hints=["Keep whichever of the two is bigger.",
                           "Write (x > best ? x : best)."],
                    difficulty="Medium"),
                _ex("tscourse-w8-rd-5", "Fold to an object",
                    "Tally the words with reduce, then print the count for `a`.",
                    _WORDS + 'const counts = words.reduce((acc, w) => {\n'
                    '  acc[w] = (acc[w] ?? 0) + 1;\n  return acc;\n'
                    '}, {} as { [key: string]: number });\n'
                    'console.log(counts["a"] ?? 0);\n',
                    'acc[w] = (acc[w] ?? 0) + 1;\n  return acc;',
                    [("a b a c a", "3"), ("b c", "0")],
                    hints=["Update the accumulator, then hand it back for the next step.",
                           "Write acc[w] = (acc[w] ?? 0) + 1; then return acc;"],
                    difficulty="Medium"),
                _fix("tscourse-w8-rd-fix1", "Fix the reduce seed",
                     "The total is one too high — the seed is wrong. Fix it to 10.",
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                     'console.log(items.reduce((sum, it) => sum + it.price, 1));\n',
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'const items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\n'
                     'console.log(items.reduce((sum, it) => sum + it.price, 0));\n',
                     [("", "10")],
                     hints=["The last argument is the starting accumulator.",
                            "A sum seeds at 0."]),
                _fix("tscourse-w8-rd-fix2", "Fix the missing return",
                     "This tally should print 3 for `a b a c a` but crashes — the callback returns nothing. Fix it.",
                     _WORDS + 'const counts = words.reduce((acc, w) => {\n'
                     '  acc[w] = (acc[w] ?? 0) + 1;\n'
                     '}, {} as { [key: string]: number });\n'
                     'console.log(counts["a"] ?? 0);\n',
                     _WORDS + 'const counts = words.reduce((acc, w) => {\n'
                     '  acc[w] = (acc[w] ?? 0) + 1;\n  return acc;\n'
                     '}, {} as { [key: string]: number });\n'
                     'console.log(counts["a"] ?? 0);\n',
                     [("a b a c a", "3"), ("a", "1")],
                     hints=["Whatever the callback returns becomes the next accumulator — here that is undefined.",
                            "Add return acc; at the end of the callback."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The seed of a reduce sets…",
                   ["only the starting value", "the starting value, the accumulator's type, and the empty-list answer",
                    "the length", "nothing"], 1,
                   "All three — which is why you always pass one."),
                _q("When should you NOT use reduce?",
                   ["for sums", "when map or filter already says what you mean",
                    "for objects", "for strings"], 1,
                   "Expressing map via reduce is less clear and no faster."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w8-modelling", "Modelling real data",
            "Choosing types that make wrong states hard to write.",
            """
Types are a design tool, not paperwork. The question is always: **what shapes
should be possible?**

Take a payment record. A first attempt:

```ts
interface Payment {
  amount: number;
  status: string;        // "paid" or "pending" or "failed"
}
```

`status: string` allows `"pain"`, `"PAID"`, `""` and `"banana"`. Narrow it to
exactly the values you mean:

```ts
type Status = "paid" | "pending" | "failed";

interface Payment {
  amount: number;
  status: Status;
}
```

Now a typo is a compile error, and your editor autocompletes the three options.
This — **a union of literal types** — is the single highest-value modelling
trick in TypeScript, and week 9 is built on it.

**Make illegal states unrepresentable.** Compare:

```ts
interface Job { done: boolean; result?: string; error?: string }
```

That permits `{ done: false, result: "x", error: "y" }` — finished and failed
and unfinished at once. Nothing in the type says those fields travel together.
Week 9's discriminated unions fix this properly; for now, notice the smell:
**optional fields that are only meaningful in combination.**

**A practical checklist for a new type:**

1. What are the fields, and which are genuinely optional?
2. Which fields are a **fixed set of values** rather than free text?
3. Which fields must never change after creation? (`readonly`)
4. Are any of these fields only valid together?

**A typed pipeline** is what this all pays for. Parse into a named type once, at
the edge, and everything downstream is checked:

```ts
interface Row { desc: string; amount: number }

function parse(line: string): Row {
  const p = line.trim().split(" ");
  return { desc: p[0] ?? "", amount: Number(p[1]) };
}

const rows: Row[] = lines.map(parse);
const total = rows.reduce((s, r) => s + r.amount, 0);
```

`parse` is the boundary. Above it is untrusted text; below it, every field has a
known type. Getting the boundary right is most of what makes a program feel
solid — and note that the *type* does no validation. `Number("abc")` is `NaN`,
and the annotation says `number` regardless. Types describe intent; **runtime
checks enforce it**, and you need both.

> ⚠️ **Common mistakes:** typing a fixed set of values as `string`; scattering
> optional fields that are only valid in combination; and assuming an annotation
> validates real input — it never does.
""",
            warmup=[
                _q("`status: string` versus `status: \"paid\" | \"pending\"` — the union…",
                   ["is slower", "makes typos a compile error and enables autocomplete",
                    "is the same", "is runtime-checked"], 1,
                   "Narrow types catch narrow mistakes."),
                _q("`{ done: boolean; result?: string; error?: string }` allows…",
                   ["only valid states", "done and error together, nonsensically",
                    "nothing", "only done: true"], 1,
                   "Optionals that only make sense in combination are a design smell."),
                _q("Does `const n: number = Number(\"abc\")` error?",
                   ["yes, at compile time", "no — the type is number, the value is NaN",
                    "yes, at runtime", "it returns 0"], 1,
                   "NaN is a number. Types do not validate input."),
                _q("Parsing at the boundary means…",
                   ["parsing everywhere", "converting untrusted text into a named type once, at the edge",
                    "never parsing", "parsing at the end"], 1,
                   "Everything downstream then works with known types."),
            ],
            exercises=[
                _design("tscourse-w8-md-d1", "Design the expense record",
                        "Below is a parser and the code that consumes it — but the type they "
                        "agree on is missing. Read what `parse` builds and what the last line "
                        "reads back, and write the `Expense` interface that describes it. "
                        "Model the category as the fixed set of values it can actually be, "
                        "not as free text.",
                        _FS + 'interface Expense {\n'
                        '  name: string;\n'
                        '  amount: number;\n'
                        '  category: "food" | "home" | "fun";\n'
                        '}\n'
                        'function parse(line: string): Expense {\n'
                        '  const p = line.split(",");\n'
                        '  const cat = (p[2] ?? "").trim();\n'
                        '  return {\n'
                        '    name: (p[0] ?? "").trim(),\n'
                        '    amount: Number(p[1]),\n'
                        '    category: cat === "food" ? "food" : cat === "home" ? "home" : "fun",\n'
                        '  };\n}\n'
                        'const rows = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                        'console.log(rows.map((r) => `${r.name}=${r.category}`).join(" "));\n',
                        '  name: string;\n'
                        '  amount: number;\n'
                        '  category: "food" | "home" | "fun";\n',
                        'type _1 = Expect<Equal<Expense["name"], string>>;\n'
                        'type _2 = Expect<Equal<Expense["amount"], number>>;\n'
                        'type _3 = Expect<Equal<Expense["category"], "food" | "home" | "fun">>;\n'
                        'type _4 = Expect<Equal<keyof Expense, "name" | "amount" | "category">>;\n',
                        [("coffee,3.25,food\nrent,900,home", "coffee=food rent=home"),
                         ("kite,8,fun", "kite=fun")],
                        hints=["Three fields, and the object literal in `parse` names all three.",
                               "`amount` comes from Number(...), so it is a number however the "
                               "text looked.",
                               "The ternary can only ever produce one of three exact strings — "
                               "say so with a union of literal types rather than `string`."]),
                _ex("tscourse-w8-md-1", "Narrow the status",
                    "Alias Status to exactly the three allowed values, then print the payment's status.",
                    'type Status = "paid" | "pending" | "failed";\n'
                    'interface Payment {\n  amount: number;\n  status: Status;\n}\n'
                    'const p: Payment = { amount: 10, status: "paid" };\n'
                    'console.log(p.status);\n',
                    '"paid" | "pending" | "failed"', [("", "paid")],
                    hints=["A union of exact string values, separated by |.",
                           'Write "paid" | "pending" | "failed".']),
                _ex("tscourse-w8-md-2", "A parse boundary",
                    "Complete parse so it turns a `desc amount` line into a Row.",
                    _FS + 'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                    'function parse(line: string): Row {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0] ?? "", amount: Number(p[1]) };\n}\n'
                    'const rows: Row[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(rows[0]!.amount);\n',
                    'return { desc: p[0] ?? "", amount: Number(p[1]) };',
                    [("coffee 3", "3"), ("book 12\nrent 900", "12")],
                    hints=["Build the record, converting the numeric field.",
                           "Write return { desc: p[0] ?? "", amount: Number(p[1]) };"],
                    difficulty="Medium"),
                _ex("tscourse-w8-md-3", "A typed pipeline",
                    "Parse the lines, then fold them to a total with reduce.",
                    _FS + 'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                    'function parse(line: string): Row {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0] ?? "", amount: Number(p[1]) };\n}\n'
                    'const rows: Row[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(rows.reduce((s, r) => s + r.amount, 0));\n',
                    'rows.reduce((s, r) => s + r.amount, 0)',
                    [("coffee 3\nbook 12", "15"), ("rent 900", "900")],
                    hints=["Fold the parsed records to one number.",
                           "Write rows.reduce((s, r) => s + r.amount, 0)."],
                    difficulty="Medium"),
                _ex("tscourse-w8-md-4", "Validate at runtime",
                    "The type says number, but the data may be nonsense. Print `invalid` when the amount does not parse.",
                    _FS + 'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                    'const p = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                    'const row: Row = { desc: p[0] ?? "", amount: Number(p[1]) };\n'
                    'console.log(Number.isNaN(row.amount) ? "invalid" : row.amount);\n',
                    'Number.isNaN(row.amount) ? "invalid" : row.amount',
                    [("coffee abc", "invalid"), ("coffee 3", "3")],
                    hints=["Annotations never check real input — you must.",
                           'Write Number.isNaN(row.amount) ? "invalid" : row.amount.'],
                    difficulty="Medium"),
                _ex("tscourse-w8-md-5", "readonly identity",
                    "Mark the id as readonly, then print the record's label.",
                    'interface Expense {\n  readonly id: string;\n  desc: string;\n}\n'
                    'const e: Expense = { id: "e1", desc: "coffee" };\n'
                    'console.log(`${e.id}: ${e.desc}`);\n',
                    'readonly id: string;', [("", "e1: coffee")],
                    hints=["readonly goes before the field name.",
                           "Write readonly id: string;"]),
                _fix("tscourse-w8-md-fix1", "Fix the unvalidated boundary",
                     "For `coffee abc` this should print `invalid` but prints `NaN`. Fix it.",
                     _FS + 'const p = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                     'const amount: number = Number(p[1]);\n'
                     'console.log(amount);\n',
                     _FS + 'const p = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                     'const amount: number = Number(p[1]);\n'
                     'console.log(Number.isNaN(amount) ? "invalid" : amount);\n',
                     [("coffee abc", "invalid"), ("coffee 3", "3")],
                     hints=["NaN IS a number as far as the type system is concerned.",
                            "Check it at runtime with Number.isNaN."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The highest-value modelling move in TypeScript is…",
                   ["annotating every local", "replacing `string` with a union of the literal values you mean",
                    "using any", "adding readonly everywhere"], 1,
                   "It turns typos into compile errors and drives autocomplete."),
                _q("'Make illegal states unrepresentable' means…",
                   ["validate everything at runtime", "choose types that cannot describe a nonsensical combination",
                    "use readonly", "avoid optional fields"], 1,
                   "Design the type so the bad case cannot be written."),
                _q("Types validate real input…",
                   ["always", "never — they are erased; runtime checks are still required",
                    "only for numbers", "only with interfaces"], 1,
                   "You need both: types for intent, checks for reality."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w8-boundary", "Types at the boundary",
            "Where untrusted text becomes values your types can vouch for.",
            """
Here is the fact that reframes everything you learned this week:

> **Types are erased before the program runs.** Not one annotation survives into
> the running code.

`const n: number = ...` is a promise *you* make to the compiler, checked while
you write. It is not a guard rail at runtime. So the moment data arrives from
outside — stdin, a file, a network call, a form — your annotations describe what
you *hope* is there, and something has to actually check.

```ts
const raw = fs.readFileSync(0, "utf8").trim();
const amount: number = Number(raw);   // annotation satisfied…
console.log(amount + 1);              // …and if raw was "oops", this is NaN
```

`Number("oops")` is `NaN`, whose type is `number`. The annotation is honest; the
value is garbage. That is why real programs have a **boundary**.

**The boundary function.** One place converts text into your shape, validating
as it goes, and everything downstream can then trust its types:

```ts
interface Entry {
  name: string;
  amount: number;
  ok: boolean;       // did this line survive validation?
}

function parseEntry(line: string): Entry {
  const parts = line.split(",");
  if (parts.length !== 2) return { name: line.trim(), amount: 0, ok: false };
  const amount = Number((parts[1] ?? "").trim());
  if (Number.isNaN(amount)) return { name: (parts[0] ?? "").trim(), amount: 0, ok: false };
  return { name: (parts[0] ?? "").trim(), amount, ok: true };
}
```

Two things to notice. Validation is **guard clauses** again — reject, reject,
then the happy path. And a rejected line does not crash the program; it comes
back marked `ok: false` and the caller decides. (Month 4 gives this the name it
has in the wild: the **Result** pattern.)

**Check the things that actually go wrong.** In practice that is a short list:
the field count is wrong, a number didn't parse (`Number.isNaN`), a required
string is empty, or a value is out of range (a negative price).

**`any` switches the compiler off.** It is not "some type" — it is "stop
checking":

```ts
const data: any = { amount: "3.25" };   // a STRING, though nobody said so
console.log(data.amount + 1);           // "3.251" — no error, wrong answer
```

Every bug `any` lets through is a bug you were paying TypeScript to catch. Treat
each `any` as a small debt.

**`as` is a promise, not a check.** An assertion tells the compiler you know
better. Nothing is verified at runtime:

```ts
const cfg = fromElsewhere as Config;   // if it isn't a Config, nothing complains
```

Use it only right after a check you performed yourself, and never as a way to
silence an error you don't understand.

> ⚠️ **Common mistakes:** believing an annotation validates runtime data;
> forgetting the `Number.isNaN` guard, so one bad row poisons every total with
> `NaN`; reaching for `any` to make an error go away; and reading fields out of
> a split line in the wrong order — the types all still line up, and the output
> is nonsense.
""",
            warmup=[
                _q("`const n: number = Number(\"oops\");` — does this compile?",
                   ["No, it is a type error", "Yes, and n is NaN", "Yes, and n is 0", "It throws"], 1,
                   "NaN is a number as far as the type system is concerned."),
                _q("At runtime, your type annotations are…",
                   ["checked on every assignment", "erased — they existed only while compiling",
                    "converted to if-statements", "stored alongside the value"], 1,
                   "Which is exactly why boundaries need real validation code."),
                _q("`const data: any = { amount: \"3.25\" }; data.amount + 1` gives…",
                   ["4.25", '"3.251"', "a type error", "NaN"], 1,
                   "any turns checking off, so string concatenation happens silently."),
                _q("`value as Config` does what at runtime?",
                   ["validates the shape", "nothing at all — it only silences the compiler",
                    "copies the object", "throws if the shape is wrong"], 1,
                   "An assertion is a promise you make, not a check you get."),
            ],
            exercises=[
                _retype("tscourse-w8-bnd-r1", "Switch the compiler back on",
                        "This program works, and every `any` in it is a check you are paying "
                        "for and not receiving. Replace all four with types that say what is "
                        "really there: name the record type `Row`, and let the last two be "
                        "inferred rather than annotated. The output must not change.",
                        _FS + 'function parseRow(line: any): any {\n'
                        '  const parts = line.split(",");\n'
                        '  return { name: parts[0].trim(), amount: Number(parts[1]) };\n}\n'
                        'const rows: any = fs.readFileSync(0, "utf8").trim().split("\\n").map(parseRow);\n'
                        'let total: any = 0;\n'
                        'for (const r of rows) {\n  total = total + r.amount;\n}\n'
                        'console.log(total.toFixed(2));\n',
                        _FS + 'interface Row {\n  name: string;\n  amount: number;\n}\n'
                        'function parseRow(line: string): Row {\n'
                        '  const parts = line.split(",");\n'
                        '  return { name: (parts[0] ?? "").trim(), amount: Number(parts[1]) };\n}\n'
                        'const rows = fs.readFileSync(0, "utf8").trim().split("\\n").map(parseRow);\n'
                        'let total = 0;\n'
                        'for (const r of rows) {\n  total = total + r.amount;\n}\n'
                        'console.log(total.toFixed(2));\n',
                        'type _1 = Expect<Equal<Parameters<typeof parseRow>[0], string>>;\n'
                        'type _2 = Expect<Equal<ReturnType<typeof parseRow>, '
                        '{ name: string; amount: number }>>;\n'
                        'type _3 = Expect<Equal<typeof rows, { name: string; amount: number }[]>>;\n'
                        'type _4 = Expect<Equal<typeof total, number>>;\n',
                        [("coffee,3.25\nbook,12", "15.25"), ("rent,900", "900.00")],
                        hints=["Start at the boundary: `parseRow` takes one line of text and "
                               "returns one record.",
                               "Once `parseRow` is honest, `rows` and `total` no longer need an "
                               "annotation at all — delete them and let inference do it.",
                               "Losing `any` on `line` costs you something: `parts[0]` is now "
                               "`string | undefined`, so it needs a `?? \"\"` before .trim()."],
                        difficulty="Medium"),
                _ex("tscourse-w8-bnd-1", "Annotate the boundary",
                    "Give the parsing function the return annotation that says what it hands back.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'function parsePoint(text: string): Point {\n'
                    '  const parts = text.split(",");\n'
                    '  return { x: Number(parts[0]), y: Number(parts[1]) };\n}\n'
                    'const p = parsePoint("3,4");\n'
                    'console.log(p.x + p.y);\n',
                    'Point {\n'
                    '  const parts = text.split(",");',
                    [("", "7")],
                    hints=["The function builds an object with x and y — there is already a name for that shape.",
                           "Annotate the return as Point."]),
                _ex("tscourse-w8-bnd-2", "Guard the parse",
                    "One unparseable value should become 0 rather than poisoning everything. Add the guard.",
                    _FS +
                    'function toAmount(text: string): number {\n'
                    '  const n = Number(text.trim());\n'
                    '  if (Number.isNaN(n)) return 0;\n'
                    '  return n;\n}\n'
                    'const raw = fs.readFileSync(0, "utf8").trim().split(",");\n'
                    'const amounts: number[] = raw.map(toAmount);\n'
                    'console.log(amounts.join(" "));\n',
                    'if (Number.isNaN(n)) return 0;',
                    [("3, abc, 5", "3 0 5"), ("1,2", "1 2")],
                    hints=["Number() hands back NaN when the text isn't a number.",
                           "NaN === NaN is false, so you must test with Number.isNaN.",
                           "Write if (Number.isNaN(n)) return 0;"],
                    difficulty="Easy"),
                _ex("tscourse-w8-bnd-3", "Reject the wrong field count",
                    "A line must have exactly two fields. Fill in the rejecting guard so a malformed line comes back marked not-ok.",
                    'interface Parsed {\n  ok: boolean;\n  name: string;\n  amount: number;\n}\n'
                    'function parseLine(line: string): Parsed {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts.length !== 2) return { ok: false, name: "", amount: 0 };\n'
                    '  const amount = Number(parts[1]);\n'
                    '  if (Number.isNaN(amount)) return { ok: false, name: "", amount: 0 };\n'
                    '  return { ok: true, name: (parts[0] ?? "").trim(), amount };\n}\n'
                    'console.log(parseLine("coffee, 3.25").ok);\n'
                    'console.log(parseLine("coffee").ok);\n'
                    'console.log(parseLine("coffee, abc").ok);\n',
                    'if (parts.length !== 2) return { ok: false, name: "", amount: 0 };',
                    [("", "true\nfalse\nfalse")],
                    hints=["Splitting on the comma should give exactly two pieces.",
                           'Return { ok: false, name: "", amount: 0 } when it does not.'],
                    difficulty="Medium"),
                _ex("tscourse-w8-bnd-4", "The escape hatch",
                    "Value from elsewhere, shape you are willing to vouch for. Fill in the assertion.",
                    'interface Config {\n  retries: number;\n  verbose: boolean;\n}\n'
                    'const fromElsewhere: any = { retries: 3, verbose: true };\n'
                    'const cfg = fromElsewhere as Config;\n'
                    'console.log(`${cfg.retries} ${cfg.verbose}`);\n',
                    'fromElsewhere as Config',
                    [("", "3 true")],
                    hints=["The `as` keyword asserts a type — remember it checks nothing at runtime.",
                           "Write fromElsewhere as Config."],
                    difficulty="Easy"),
                _ex("tscourse-w8-bnd-5", "Trust only what passed",
                    "Total up the rows that survived validation, ignoring the rest. Fill in the fold.",
                    'interface Row {\n  name: string;\n  amount: number;\n  ok: boolean;\n}\n'
                    'const rows: Row[] = [\n'
                    '  { name: "a", amount: 3, ok: true },\n'
                    '  { name: "b", amount: 99, ok: false },\n'
                    '  { name: "c", amount: 4, ok: true },\n'
                    '];\n'
                    'const total = rows.filter((r) => r.ok).reduce((sum, r) => sum + r.amount, 0);\n'
                    'console.log(total);\n',
                    '.reduce((sum, r) => sum + r.amount, 0)',
                    [("", "7")],
                    hints=["Filter first so the fold only ever sees good rows.",
                           "Start the accumulator at 0 and add each row's amount."],
                    difficulty="Medium"),
                _fix("tscourse-w8-bnd-fix1", "Fix the any that hid a bug",
                     "This should print `Total: 4.25`, but `any` let a string through where a number was meant. Type the shape honestly and convert at the boundary.",
                     'const raw: any = { name: "coffee", amount: "3.25" };\n'
                     'console.log(`Total: ${raw.amount + 1}`);\n',
                     'interface RawEntry {\n  name: string;\n  amount: string;\n}\n'
                     'const raw: RawEntry = { name: "coffee", amount: "3.25" };\n'
                     'console.log(`Total: ${Number(raw.amount) + 1}`);\n',
                     [("", "Total: 4.25")],
                     hints=["`amount` really is text — say so in an interface instead of hiding it under any.",
                            "Then convert it with Number(...) where you actually do arithmetic."],
                     difficulty="Medium"),
                _fix("tscourse-w8-bnd-fix2", "Fix the poisoned total",
                     "One unparseable value turns the whole total into NaN. It should print 15.00.",
                     'function toAmount(text: string): number {\n'
                     '  return Number(text);\n}\n'
                     'const values = ["10", "oops", "5"];\n'
                     'let total = 0;\n'
                     'for (const v of values) total = total + toAmount(v);\n'
                     'console.log(total.toFixed(2));\n',
                     'function toAmount(text: string): number {\n'
                     '  const n = Number(text);\n'
                     '  if (Number.isNaN(n)) return 0;\n'
                     '  return n;\n}\n'
                     'const values = ["10", "oops", "5"];\n'
                     'let total = 0;\n'
                     'for (const v of values) total = total + toAmount(v);\n'
                     'console.log(total.toFixed(2));\n',
                     [("", "15.00")],
                     hints=["Anything added to NaN is NaN, so one bad value ruins every later sum.",
                            "Guard inside toAmount with Number.isNaN and fall back to 0."]),
                _fix("tscourse-w8-bnd-fix3", "Fix the swapped fields",
                     "The types all line up, yet this prints `12 costs NaN`. The fields are being read out of the split line in the wrong order.",
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'function toItem(line: string): Item {\n'
                     '  const parts = line.split(",");\n'
                     '  return { name: parts[1], price: Number(parts[0]) };\n}\n'
                     'const it = toItem("book,12");\n'
                     'console.log(`${it.name} costs ${it.price}`);\n',
                     'interface Item {\n  name: string;\n  price: number;\n}\n'
                     'function toItem(line: string): Item {\n'
                     '  const parts = line.split(",");\n'
                     '  return { name: parts[0] ?? "", price: Number(parts[1]) };\n}\n'
                     'const it = toItem("book,12");\n'
                     'console.log(`${it.name} costs ${it.price}`);\n',
                     [("", "book costs 12")],
                     hints=["parts[0] is the text before the comma; parts[1] is after it.",
                            "The compiler cannot catch this — both fields still receive the right kind of value."],
                     difficulty="Medium"),
                _ch("tscourse-w8-bnd-ch1", "A validating boundary", "Hard",
                    "Each line is `name,amount`. Write the `Entry` shape and `parseEntry`: reject a line that hasn't got exactly two fields, whose amount doesn't parse, or whose amount is negative — marking it `ok: false` with an amount of 0 — and accept everything else with the name trimmed.",
                    _FS +
                    'interface Entry {\n  name: string;\n  amount: number;\n  ok: boolean;\n}\n'
                    'function parseEntry(line: string): Entry {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts.length !== 2) return { name: line.trim(), amount: 0, ok: false };\n'
                    '  const amount = Number((parts[1] ?? "").trim());\n'
                    '  if (Number.isNaN(amount) || amount < 0) {\n'
                    '    return { name: (parts[0] ?? "").trim(), amount: 0, ok: false };\n'
                    '  }\n'
                    '  return { name: (parts[0] ?? "").trim(), amount, ok: true };\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0);\n'
                    'const entries: Entry[] = lines.map((l) => parseEntry(l));\n'
                    'const good = entries.filter((e) => e.ok);\n'
                    'const total = good.reduce((sum, e) => sum + e.amount, 0);\n'
                    'for (const e of good) console.log(`${e.name}: $${e.amount.toFixed(2)}`);\n'
                    'console.log(`Accepted ${good.length}, rejected ${entries.length - good.length}, total $${total.toFixed(2)}`);\n',
                    'interface Entry {\n  name: string;\n  amount: number;\n  ok: boolean;\n}\n'
                    'function parseEntry(line: string): Entry {\n'
                    '  const parts = line.split(",");\n'
                    '  if (parts.length !== 2) return { name: line.trim(), amount: 0, ok: false };\n'
                    '  const amount = Number((parts[1] ?? "").trim());\n'
                    '  if (Number.isNaN(amount) || amount < 0) {\n'
                    '    return { name: (parts[0] ?? "").trim(), amount: 0, ok: false };\n'
                    '  }\n'
                    '  return { name: (parts[0] ?? "").trim(), amount, ok: true };\n}',
                    [("coffee, 3.25\nbroken\nbook, 12\nbad, -4",
                      "coffee: $3.25\nbook: $12.00\nAccepted 2, rejected 2, total $15.25"),
                     ("a,1\nb,2", "a: $1.00\nb: $2.00\nAccepted 2, rejected 0, total $3.00"),
                     ("nope", "Accepted 0, rejected 1, total $0.00")],
                    hints=["Entry needs three fields: the name, the amount, and whether the line survived.",
                           "Write the rejections as guard clauses, one per thing that can go wrong.",
                           "Number.isNaN(amount) catches unparseable text; amount < 0 catches the impossible price.",
                           "The happy path returns at the end with ok: true and the trimmed name."]),
            ],
            quiz=[
                _q("What survives into the running program?",
                   ["the annotations", "only the values and the code — annotations are erased",
                    "interfaces but not type aliases", "everything"], 1,
                   "Which is why runtime data needs runtime checks."),
                _q("`Number(\"oops\")` produces…",
                   ["a type error", "NaN, whose type is number", "0", "undefined"], 1,
                   "The annotation is satisfied and the value is still wrong."),
                _q("The point of a single boundary function is that…",
                   ["it is faster", "everything downstream can trust its types",
                    "it avoids interfaces", "it removes the need for guards"], 1,
                   "Validate once, at the edge; trust everywhere inside."),
                _q("`as` should be used…",
                   ["whenever the compiler complains", "sparingly, right after a check you performed yourself",
                    "instead of interfaces", "to convert strings to numbers"], 1,
                   "It silences the compiler without checking anything."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #8 — the typed ledger",
        """
Month 2's finale. Everything gets a name, and the report is folded with
`reduce`.

Input is one expense per line — `desc amount status` — where status is `paid`
or `unpaid`:

```
coffee 3.25 paid
book 12 unpaid
lunch 9.50 unpaid
rent 900 paid
```

Print:

```
Count:   4
Total:   $924.75
Paid:    $903.25
Unpaid:  $21.50
Largest: rent
```

Requirements:

- A `type Status = "paid" | "unpaid"` and an `interface Expense` with `desc`,
  `amount` and `status`.
- A `parse(line: string): Expense` boundary function.
- Every total computed with **`reduce`**, not a loop.
- `Largest` is the description of the biggest expense.
""",
        _ch("tscourse-w8-capstone", "Budget Buddy #8", "Medium",
            "Model the data, parse it at the boundary, then fold it three ways.",
            _FS + 'type Status = "paid" | "unpaid";\n'
            'interface Expense {\n  desc: string;\n  amount: number;\n  status: Status;\n}\n'
            'function parse(line: string): Expense {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0] ?? "", amount: Number(p[1]), status: p[2] === "paid" ? "paid" : "unpaid" };\n'
            '}\n'
            'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const total = rows.reduce((s, r) => s + r.amount, 0);\n'
            'const paid = rows.filter((r) => r.status === "paid").reduce((s, r) => s + r.amount, 0);\n'
            'const largest = rows.reduce((best, r) => (r.amount > best.amount ? r : best), rows[0]!);\n'
            'console.log(`Count:   ${rows.length}`);\n'
            'console.log(`Total:   $${total.toFixed(2)}`);\n'
            'console.log(`Paid:    $${paid.toFixed(2)}`);\n'
            'console.log(`Unpaid:  $${(total - paid).toFixed(2)}`);\n'
            'console.log(`Largest: ${largest.desc}`);\n',
            'function parse(line: string): Expense {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0] ?? "", amount: Number(p[1]), status: p[2] === "paid" ? "paid" : "unpaid" };\n'
            '}\n'
            'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const total = rows.reduce((s, r) => s + r.amount, 0);\n'
            'const paid = rows.filter((r) => r.status === "paid").reduce((s, r) => s + r.amount, 0);\n'
            'const largest = rows.reduce((best, r) => (r.amount > best.amount ? r : best), rows[0]!);\n'
            'console.log(`Count:   ${rows.length}`);\n'
            'console.log(`Total:   $${total.toFixed(2)}`);\n'
            'console.log(`Paid:    $${paid.toFixed(2)}`);\n'
            'console.log(`Unpaid:  $${(total - paid).toFixed(2)}`);\n'
            'console.log(`Largest: ${largest.desc}`);',
            [("coffee 3.25 paid\nbook 12 unpaid\nlunch 9.50 unpaid\nrent 900 paid",
              "Count:   4\nTotal:   $924.75\nPaid:    $903.25\nUnpaid:  $21.50\nLargest: rent"),
             ("tea 2 unpaid",
              "Count:   1\nTotal:   $2.00\nPaid:    $0.00\nUnpaid:  $2.00\nLargest: tea"),
             ("a 5 paid\nb 5 paid",
              "Count:   2\nTotal:   $10.00\nPaid:    $10.00\nUnpaid:  $0.00\nLargest: a")],
            hints=["parse is the boundary: split the line and build one Expense, converting the amount and narrowing the status.",
                   'The status field is a union, so derive it: p[2] === "paid" ? "paid" : "unpaid".',
                   "Total is rows.reduce((s, r) => s + r.amount, 0) — always pass the seed.",
                   "Paid is a filter followed by the same reduce; unpaid is then just total - paid.",
                   "Largest folds to a RECORD, not a number: seed with rows[0] and keep whichever has the bigger amount."]),
        example_io="Count:   4\nTotal:   $924.75\nPaid:    $903.25\nUnpaid:  $21.50\nLargest: rent",
        rubric=["Status is a union of literal types, not string",
                "A single parse function converts a line into a typed Expense",
                "Every total uses reduce with an explicit seed",
                "Largest folds to a record and reads its desc"],
        stretch=_ch("tscourse-w8-capstone-stretch", "Budget Buddy #8 (stretch)", "Medium",
                    "Add a `By status:` line built with a single reduce that folds to an object: `paid=2, unpaid=2` (counts, keys sorted alphabetically).",
                    _FS + 'type Status = "paid" | "unpaid";\n'
                    'interface Expense {\n  desc: string;\n  amount: number;\n  status: Status;\n}\n'
                    'function parse(line: string): Expense {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0] ?? "", amount: Number(p[1]), status: p[2] === "paid" ? "paid" : "unpaid" };\n'
                    '}\n'
                    'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'const byStatus = rows.reduce((acc, r) => {\n'
                    '  acc[r.status] = (acc[r.status] ?? 0) + 1;\n  return acc;\n'
                    '}, {} as { [key: string]: number });\n'
                    'const parts = Object.keys(byStatus).sort().map((k) => `${k}=${byStatus[k]}`);\n'
                    'console.log(`By status: ${parts.join(", ")}`);\n',
                    'const byStatus = rows.reduce((acc, r) => {\n'
                    '  acc[r.status] = (acc[r.status] ?? 0) + 1;\n  return acc;\n'
                    '}, {} as { [key: string]: number });\n'
                    'const parts = Object.keys(byStatus).sort().map((k) => `${k}=${byStatus[k]}`);\n'
                    'console.log(`By status: ${parts.join(", ")}`);',
                    [("coffee 3.25 paid\nbook 12 unpaid\nlunch 9.50 unpaid\nrent 900 paid",
                      "By status: paid=2, unpaid=2"),
                     ("tea 2 unpaid", "By status: unpaid=1")],
                    hints=["This is the tally fold: seed with an empty object and return the accumulator each step.",
                           "acc[r.status] = (acc[r.status] ?? 0) + 1; then return acc;",
                           "Sort the keys before mapping so the output is deterministic."]),
    ),
))
