# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 9 — unions & narrowing.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 9 ---------------------------------------------------------------

_WEEKS.append(_week(
    9, 3, _M3,
    "Unions & Narrowing",
    "Model a value that is 'one of several things', then prove to the compiler which one it is before using it.",
    """
Month 2 taught you to describe data that has **one** shape. Month 3 starts with
the far more common case: data that is **one of several** shapes.

- A parsed field is a `number` **or** the string `"n/a"`.
- A status is `"paid"` **or** `"pending"` **or** `"failed"`.
- An API result is a success **or** an error.

That's a **union type**, written with `|`:

```ts
type Result = number | string;
```

And immediately you hit the central problem. Given a `number | string`, you
cannot call `.toFixed(2)` — it might be a string. You cannot call
`.toUpperCase()` — it might be a number. On a union you may only use what **all**
the members have in common.

The way out is **narrowing**: writing an ordinary runtime check that TypeScript
understands, after which it knows which member you have:

```ts
function show(v: number | string): string {
  if (typeof v === "number") {
    return v.toFixed(2);      // here, v is a number
  }
  return v.toUpperCase();     // here, it can only be a string
}
```

That is the whole week, and it is the moment TypeScript stops feeling like
annotation and starts feeling like a proof assistant. The checks are all
JavaScript you already know — `typeof`, `===`, `in`, `Array.isArray`,
truthiness. What's new is that the *type* changes as you check.

⏱️ Budget about **ten hours**, spread over several sittings.
""",
    objectives=[
        "Write union types and say what you may do with an un-narrowed union",
        "Model a fixed set of options as a union of literal types",
        "Narrow with typeof, and know exactly what typeof reports",
        "Narrow with equality and with switch on a literal union",
        "Narrow with truthiness, in, Array.isArray and instanceof",
        "Design and consume a discriminated union",
        "Prove a switch is exhaustive with never, and combine types with &",
        "Write a custom type guard whose return annotation narrows its argument",
        "Use a predicate with filter to narrow a whole array's element type",
    ],
    why="Almost every interesting value in a real program is 'one of several things' — loaded or loading or failed, guest or member, found or missing. Unions plus narrowing are how TypeScript makes those cases impossible to forget.",
    est_minutes=590,
    glossary=[
        _gloss("union", "A type that is one of several: number | string."),
        _gloss("member (of a union)", "One of the alternatives in a union."),
        _gloss("literal type", "A type that is one exact value: \"paid\", 42, true."),
        _gloss("narrowing", "Using a runtime check so the compiler knows which member you have."),
        _gloss("type guard", "An expression that narrows: typeof x === \"string\"."),
        _gloss("control-flow analysis", "TypeScript tracking the narrowed type along each branch."),
        _gloss("typeof", "Reports a value's runtime type as a string."),
        _gloss("in", "Tests whether a key exists on an object — and narrows by it."),
        _gloss("Array.isArray(x)", "The reliable array test; typeof an array is \"object\"."),
        _gloss("instanceof", "Tests against a class or constructor, e.g. Error."),
        _gloss("discriminated union", "A union of objects sharing a literal 'tag' field that identifies each case."),
        _gloss("discriminant / tag", "The shared literal field (kind, type, status) that tells the cases apart."),
        _gloss("exhaustive", "Every case of a union is handled."),
        _gloss("never", "The type with no values — what remains when every case is handled."),
        _gloss("intersection (&)", "A type having ALL the members of both: A & B."),
        _gloss("narrowing by assignment", "Assigning a value narrows the variable's type from then on."),
        _gloss("type predicate", "A return annotation of the form `v is T` that tells the compiler what true means."),
        _gloss("custom type guard", "A function you wrote whose result narrows the value you passed it."),
        _gloss("assertion function", "`asserts v is T` — narrows from the call site onward, or stops the program."),
        _gloss("filter narrowing", "Passing a predicate to filter, so the result comes back as the narrower array."),
    ],
    cheatsheet="""
```ts
// ---- declaring unions --------------------------------------------------
type Score = number | "n/a";
type Status = "paid" | "pending" | "failed";
type Maybe = string | undefined;

// On an un-narrowed union you may only use what ALL members share:
function f(v: number | string) {
  v.toString();      // ✅ both have it
  v.toFixed(2);      // ❌ string does not
}

// ---- typeof narrowing ---------------------------------------------------
if (typeof v === "number") { /* v: number */ }
else                       { /* v: string */ }

typeof 1          // "number"      typeof "a"        // "string"
typeof true       // "boolean"     typeof undefined  // "undefined"
typeof {}         // "object"      typeof []         // "object"  ⚠️
typeof null       // "object"      ⚠️ the famous bug
typeof (() => 1)  // "function"

// ---- equality & switch ---------------------------------------------------
if (s === "paid") { /* s: "paid" */ }
switch (s) {
  case "paid":    ...; break;
  case "pending": ...; break;
  default:        ...;
}

// ---- other guards ---------------------------------------------------------
if (x)                    { /* removes null/undefined/""/0 */ }
if (x !== undefined)      { /* keeps a legitimate 0 or "" */ }
if (Array.isArray(x))     { /* x: something[] */ }
if ("radius" in shape)    { /* shape: the member with radius */ }
if (e instanceof Error)   { /* e: Error */ }

// ---- discriminated union ---------------------------------------------------
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return 3.14 * s.r * s.r;
    case "square": return s.side * s.side;
  }
}

// ---- exhaustiveness --------------------------------------------------------
default: {
  const _exhaustive: never = s;    // errors if a case was forgotten
  return _exhaustive;
}

// ---- intersection -----------------------------------------------------------
type Timestamped = { created: string };
type Row = Timestamped & { desc: string };   // has BOTH members
```
""",
    self_check=[
        "Can you say why `v.toFixed(2)` is rejected on a `number | string`?",
        "Can you narrow a union with typeof and use the member's own methods?",
        "Can you list what typeof reports for an array and for null?",
        "Can you narrow a literal union with a switch?",
        "Can you say when to use `in` rather than `typeof`?",
        "Can you design a discriminated union for two shapes and write a function over it?",
        "Can you explain how the `never` trick catches a forgotten case?",
        "Can you say why a helper annotated `: boolean` fails to narrow, and fix it?",
        "Can you filter a mixed array into a narrower one using a predicate you wrote?",
    ],
    review=[
        _q("On an un-narrowed `number | string` you may use…",
           ["everything on number", "everything on string",
            "only what BOTH have", "nothing at all"], 2,
           "The union's usable surface is the intersection of its members' members."),
        _q("`typeof []` is…", ['"array"', '"object"', '"list"', "undefined"], 1,
           "Arrays are objects — use Array.isArray."),
        _q("`typeof null` is…", ['"null"', '"object"', '"undefined"', "an error"], 1,
           "A famous, permanent JavaScript wart."),
        _q("After `if (typeof v === \"string\")`, inside the block `v` is…",
           ["still the union", "string", "any", "unknown"], 1,
           "TypeScript narrows along the branch."),
        _q("A discriminated union needs…",
           ["an interface", "a shared literal field distinguishing the cases",
            "a class", "an array"], 1,
           "The discriminant is what makes switch-narrowing work."),
        _q("`type Shape = {kind:\"a\"} | {kind:\"b\"}` — after `case \"a\":` the value is…",
           ["Shape", '{kind:"a"}', "never", "any"], 1,
           "The tag narrows it to exactly one member."),
        _q("`const _x: never = s;` in a default branch errors when…",
           ["always", "a union case was not handled", "never", "s is a string"], 1,
           "If any case remains, s is not never — so it fails to compile."),
        _q("`A & B` gives you…",
           ["either A or B", "the members of both", "neither", "an array"], 1,
           "Intersection combines; union chooses."),
        _q("Which safely narrows away a legitimate `0`?",
           ["if (x)", "if (x !== undefined)", "if (!x)", "if (x == null)"], 1,
           "Truthiness would discard the 0 as well."),
        _q("`\"r\" in shape` is useful when…",
           ["the members share a tag", "the members have no tag but different fields",
            "shape is a number", "never"], 1,
           "It distinguishes object shapes by the presence of a key."),
        _q("A helper annotated `: boolean` used in an `if` narrows the argument to…",
           ["the matching member", "nothing", "never", "unknown"], 1,
           "A plain boolean carries no information about which member matched."),
        _q("The name on the left of `is` in a predicate must be…",
           ["any identifier", "one of the function's parameters", "a type", "the return value"], 1,
           "The predicate narrows that particular parameter."),
        _q("A predicate whose body is wrong is…",
           ["rejected by the compiler", "believed anyway, which is worse than no guard",
            "ignored at runtime", "converted to boolean"], 1,
           "Keep the body an obvious restatement of the type."),
    ],
    milestone="Budget Buddy can now hold values that are 'a number or not applicable', and expense events that are one of several kinds — with the compiler refusing to let you forget a case.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w9-unions", "Union types",
            "One value, several possible types.",
            """
A **union** says a value is one of several types:

```ts
type Score = number | "n/a";
let s: Score = 42;
s = "n/a";        // also fine
s = "banana";     // ❌ not a member
```

The `|` reads as "or". Members can be any types: primitives, object shapes,
literal values, arrays, other unions.

**The rule that governs everything else:** on an un-narrowed union you may only
use what **every** member supports.

```ts
function f(v: number | string) {
  v.toString();     // ✅ both numbers and strings have toString
  v.toFixed(2);     // ❌ Property 'toFixed' does not exist on type 'string'
  v.length;         // ❌ numbers have no length
}
```

This feels restrictive for about a day, and then you realise it is the *point*.
The compiler is telling you that you haven't decided what to do about the string
case. `v.toFixed(2)` on a `number | string` isn't unfairly rejected — it is a
crash waiting to happen, caught early.

**Unions are everywhere in real code**, usually with `undefined` or `null`:

```ts
type Maybe = string | undefined;      // what `find` returns
type Id = string | number;            // an API that accepts either
```

Anything optional is secretly a union: `note?: string` gives `e.note` the type
`string | undefined`, which is exactly why last week's compiler errors happened.

**A union of object shapes** is legal and useful, though awkward without a tag
(lesson 6 fixes that):

```ts
type Contact = { email: string } | { phone: string };
```

**Where unions come from in practice:** parsing (`Number(x)` may be `NaN`),
lookups (found or not), external input (any of several shapes), and state
(loading, loaded, failed).

> ⚠️ **Common mistakes:** trying to use a member-specific method without
> narrowing; reaching for `any` to silence the error (throwing away the very
> information you need); and writing `number | any`, which collapses to `any`.
""",
            warmup=[
                _q("`type T = number | string;` — which is allowed on an un-narrowed T?",
                   ["t.toFixed(2)", "t.toUpperCase()", "t.toString()", "t.length"], 2,
                   "Only what both members share."),
                _q("`note?: string` gives the field the type…",
                   ["string", "string | undefined", "undefined", "any"], 1,
                   "Optional is a union in disguise."),
                _q("`let s: \"a\" | \"b\" = \"c\";` is…",
                   ["fine", "a compile error", "a runtime error", "undefined"], 1,
                   '"c" is not a member of the union.'),
                _q("`number | any` collapses to…",
                   ["number", "any", "unknown", "never"], 1,
                   "any absorbs everything — which is why it destroys unions."),
            ],
            exercises=[
                _ex("tscourse-w9-un-1", "Declare a union",
                    "Alias Score so it is either a number or the exact string `n/a`, then print the value.",
                    'type Score = number | "n/a";\nconst s: Score = "n/a";\nconsole.log(s);\n',
                    'number | "n/a"', [("", "n/a")],
                    hints=["Members are separated by |.",
                           'Write number | "n/a".']),
                _ex("tscourse-w9-un-2", "Use only the shared surface",
                    "Print the value using a method BOTH members have.",
                    'const v: number | string = 42;\nconsole.log(v.toString());\n',
                    'v.toString()', [("", "42")],
                    hints=["toFixed and toUpperCase each belong to only one member.",
                           "Both have toString()."]),
                _ex("tscourse-w9-un-3", "A union with undefined",
                    "Print the found element, or `none` when there is none.",
                    _NUMS + 'const hit: number | undefined = nums.find((x) => x > 10);\n'
                    'console.log(hit === undefined ? "none" : hit);\n',
                    'hit === undefined ? "none" : hit',
                    [("5 20 3", "20"), ("1 2", "none")],
                    hints=["find's return type is a union with undefined.",
                           'Write hit === undefined ? "none" : hit.']),
                _ex("tscourse-w9-un-4", "A union of exact values",
                    "Alias Status to the three allowed strings and print the chosen one.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s);\n',
                    '"paid" | "pending" | "failed"',
                    [("paid", "paid"), ("pending", "pending"), ("zzz", "failed")],
                    hints=["Three exact string values, joined by |.",
                           'Write "paid" | "pending" | "failed".']),
                _ex("tscourse-w9-un-5", "Union in an array",
                    "The list holds numbers and strings. Print how many entries are strings.",
                    'const mixed: (string | number)[] = [1, "a", 2, "b", "c"];\n'
                    'console.log(mixed.filter((x) => typeof x === "string").length);\n',
                    'typeof x === "string"', [("", "3")],
                    hints=["typeof reports the runtime type as a string.",
                           'Write typeof x === "string".'],
                    difficulty="Medium"),
                # The union lives on a PARAMETER, not on a const. `const v:
                # number | string = "abc"` is narrowed to string by its own
                # initializer, which makes the `number` branch statically dead
                # (`v` is `never` there) — so the fixed version would not even
                # compile, and the exercise could not teach the narrowing it is
                # named after. A parameter is the honest home for a union the
                # compiler genuinely cannot resolve.
                _fix("tscourse-w9-un-fix1", "Fix the un-narrowed call",
                     "This crashes when the value is a string. Print the number formatted to 2 decimals, or the string uppercased.",
                     'function format(v: number | string): string {\n'
                     '  return (v as number).toFixed(2);\n}\n'
                     'console.log(format("abc"));\n',
                     'function format(v: number | string): string {\n'
                     '  return typeof v === "number" ? v.toFixed(2) : v.toUpperCase();\n}\n'
                     'console.log(format("abc"));\n',
                     [("", "ABC")],
                     hints=["The `as number` cast lies to the compiler; at runtime it is still a string.",
                            "Check with typeof and handle both branches."],
                     difficulty="Medium"),
                _fix("tscourse-w9-uni-fix2", "Fix the half-handled union",
                     "This should print `#AB` then `#7`, but it crashes on the number: the code assumed one member and asserted its way past the other.",
                     'type Id = string | number;\n'
                     'function show(id: Id): string {\n'
                     '  return `#${(id as string).toUpperCase()}`;\n}\n'
                     'console.log(show("ab"));\n'
                     'console.log(show(7));\n',
                     'type Id = string | number;\n'
                     'function show(id: Id): string {\n'
                     '  if (typeof id === "string") return `#${id.toUpperCase()}`;\n'
                     '  return `#${id}`;\n}\n'
                     'console.log(show("ab"));\n'
                     'console.log(show(7));\n',
                     [("", "#AB\n#7")],
                     hints=["A union means you must handle every member, not assert the awkward one away.",
                            "Narrow with typeof, then handle the number case on its own line."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The usable methods on a union are…",
                   ["the union of all members' methods", "the ones common to every member",
                    "none", "all of the first member's"], 1,
                   "Anything else would be unsound."),
                _q("Casting with `as` to silence a union error…",
                   ["is the right fix", "lies to the compiler and can crash at runtime",
                    "narrows properly", "is required"], 1,
                   "A cast asserts; it does not check."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w9-literals", "Literal types",
            "A type that is one exact value.",
            """
A **literal type** is a type whose only value is one specific value:

```ts
let a: "paid" = "paid";
a = "pending";     // ❌ not assignable
```

On its own that's a curiosity. In a union it is the most useful modelling tool
in the language:

```ts
type Status = "paid" | "pending" | "failed";
type Dice = 1 | 2 | 3 | 4 | 5 | 6;
type Flag = true | false;              // (this is just `boolean`)
```

Compare `status: string` with `status: Status`:

| | `string` | `Status` |
|---|---|---|
| `"paid"` | ✅ | ✅ |
| `"Paid"` | ✅ 😬 | ❌ caught |
| `"pian"` | ✅ 😬 | ❌ caught |
| autocomplete | nothing | the three options |
| exhaustive switch | impossible | possible (lesson 7) |

**Inference and widening.** TypeScript decides how specific to be based on
mutability:

```ts
const a = "paid";      // type is "paid"   — it can never change
let b = "paid";        // type is string   — it might be reassigned
```

`const` gets the narrow literal type; `let` gets the **widened** type. That's
why this fails:

```ts
let s = "paid";               // s: string
const st: Status = s;         // ❌ string is not assignable to Status
```

Three fixes, in ascending order of quality:

```ts
const s = "paid";             // ✅ keep it const — it is a literal again
let s: Status = "paid";       // ✅ annotate the variable
const s = "paid" as const;    // ✅ assert the literal type explicitly
```

**Literal unions from input** need a runtime check, because input is `string`
and the compiler cannot know it's one of your three values:

```ts
const raw = readInput();                 // string
const s: Status = raw === "paid" ? "paid" : "pending";
```

That ternary is doing real work: it is the **validation** that justifies the
narrow type. Types describe intent; the check earns it.

**Numeric and boolean literals** work the same way, and are handy for
constrained numbers (`type Digit = 0 | 1 | ... | 9`) — though beyond a handful
of values a runtime range check is usually kinder.

> ⚠️ **Common mistakes:** typing a fixed set of options as `string`; being
> puzzled that a `let` won't fit a literal union (widening); and assuming the
> annotation validates input from outside the program.
""",
            warmup=[
                _q('`const a = "paid";` — the inferred type is…',
                   ["string", '"paid"', "any", "never"], 1,
                   "const cannot be reassigned, so the literal type survives."),
                _q('`let b = "paid";` — the inferred type is…',
                   ["string", '"paid"', "any", "never"], 0,
                   "let widens, because it might be reassigned."),
                _q('`type S = "a" | "b"; let x = "a"; const y: S = x;` is…',
                   ["fine", "an error — x widened to string", "a runtime error", "never"], 1,
                   "Widening is why `as const` and annotations exist."),
                _q("`type Flag = true | false` is the same as…",
                   ["string", "boolean", "never", "any"], 1,
                   "That union IS boolean."),
            ],
            exercises=[
                # The pair is the point: same value, same spelling, two different
                # inferred types. This is where the course pays off the widening
                # note it planted in w8-annotations.
                _predict("tscourse-w9-li-p1", "What a const remembers",
                         'const status = "paid";\n',
                         "status", '"paid"',
                         why="Not `string` — look at what a const can still become.",
                         hints=["A const can never be reassigned, so how many values could it hold?",
                                "Its type is that one value, written as a type.",
                                'Write "paid", quotes and all.'],
                         difficulty="Medium"),
                _predict("tscourse-w9-li-p2", "What a let forgets",
                         'let status = "paid";\n',
                         "status", "string",
                         why="One keyword changed from the exercise above. So did the answer.",
                         hints=["A let can be reassigned to any other string later.",
                                "So TypeScript cannot pin it to the one value it happens to start with.",
                                "Write string."],
                         difficulty="Medium"),
                _ex("tscourse-w9-li-1", "A literal union",
                    "Alias Status to the three exact values and print the one chosen.",
                    'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = "pending";\nconsole.log(s);\n',
                    '"paid" | "pending" | "failed"', [("", "pending")],
                    hints=["Exact string values joined by |."]),
                _ex("tscourse-w9-li-2", "Validate then narrow",
                    "Turn the raw input into a Status: `paid` stays paid, anything else becomes `failed`.",
                    _LINE + 'type Status = "paid" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : "failed";\n'
                    'console.log(s);\n',
                    'line === "paid" ? "paid" : "failed"',
                    [("paid", "paid"), ("nonsense", "failed")],
                    hints=["A runtime check is what makes the narrow type honest.",
                           'Write line === "paid" ? "paid" : "failed".']),
                _ex("tscourse-w9-li-3", "Keep the literal with as const",
                    "Use `as const` so the value keeps its literal type, then print it.",
                    'type Status = "paid" | "failed";\n'
                    'const raw = "paid" as const;\nconst s: Status = raw;\nconsole.log(s);\n',
                    '"paid" as const', [("", "paid")],
                    hints=["`as const` pins the value's literal type.",
                           'Write "paid" as const.'],
                    difficulty="Medium"),
                _ex("tscourse-w9-li-4", "Numeric literals",
                    "Alias Dice to the six faces, then print the chosen face.",
                    _LINE + 'type Dice = 1 | 2 | 3 | 4 | 5 | 6;\n'
                    'const n = Number(line);\n'
                    'const d: Dice = n >= 1 && n <= 6 ? (n as Dice) : 1;\n'
                    'console.log(d);\n',
                    '1 | 2 | 3 | 4 | 5 | 6', [("4", "4"), ("9", "1")],
                    hints=["Numeric literal types are written the same way as string ones.",
                           "Write 1 | 2 | 3 | 4 | 5 | 6."],
                    difficulty="Medium"),
                _ex("tscourse-w9-li-5", "Map a literal to a label",
                    "Print `PAID` for paid, `PENDING` for pending, `FAILED` otherwise.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s.toUpperCase());\n',
                    's.toUpperCase()',
                    [("paid", "PAID"), ("pending", "PENDING"), ("x", "FAILED")],
                    hints=["Every member of the union is a string, so string methods are available.",
                           "Write s.toUpperCase()."]),
                _fix("tscourse-w9-li-fix1", "Fix the widened let",
                     "This should print `paid`, but the value was declared in a way that loses its literal type. Fix the declaration.",
                     # No `as Status` in the starter: the cast silenced the very
                     # error the exercise exists to show, so it already passed.
                     'type Status = "paid" | "failed";\n'
                     'let raw = "paid";\nconst s: Status = raw;\nconsole.log(s);\n',
                     'type Status = "paid" | "failed";\n'
                     'const raw = "paid";\nconst s: Status = raw;\nconsole.log(s);\n',
                     [("", "paid")],
                     hints=["`let` widened the type to string, forcing a cast to paper over it.",
                            "Declare it with const and the cast becomes unnecessary."],
                     difficulty="Medium"),
                _fix("tscourse-w9-lit-fix2", "Fix the literal typo",
                     "Both lines come back unticked. The comparison is against a spelling that is not in the union at all — exactly the mistake literal types exist to catch.",
                     'type Status = "todo" | "done";\n'
                     'function icon(s: Status): string {\n'
                     '  if (s === ("Done" as Status)) return "[x]";\n'
                     '  return "[ ]";\n}\n'
                     'console.log(icon("done"));\n'
                     'console.log(icon("todo"));\n',
                     'type Status = "todo" | "done";\n'
                     'function icon(s: Status): string {\n'
                     '  if (s === "done") return "[x]";\n'
                     '  return "[ ]";\n}\n'
                     'console.log(icon("done"));\n'
                     'console.log(icon("todo"));\n',
                     [("", "[x]\n[ ]")],
                     hints=["The union has no member spelled with a capital letter.",
                            "Remove the assertion and compare against the exact literal \"done\"."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does `const` infer a literal type but `let` does not?",
                   ["a bug", "a let might be reassigned, so the type must allow that",
                    "const is faster", "they behave identically"], 1,
                   "Widening follows mutability."),
                _q("`as const` is used to…",
                   ["convert at runtime", "keep the narrow literal type", "cast to string",
                    "make it readonly at runtime"], 1,
                   "It is a compile-time assertion about specificity."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w9-typeof", "Narrowing with typeof",
            "The workhorse guard for primitive unions.",
            """
`typeof` reports a value's runtime type as a string — and TypeScript
**understands** it, narrowing the type inside the branch:

```ts
function show(v: number | string): string {
  if (typeof v === "number") {
    return v.toFixed(2);      // v: number   ✅ toFixed allowed
  }
  return v.toUpperCase();     // v: string   ✅ the only remaining member
}
```

Notice the second `return` needs no check. Having ruled out `number`, only
`string` remains, and TypeScript knows it. This is **control-flow analysis**:
the type of `v` differs on each path through the function.

**What typeof actually reports** — memorise this table, including the two
warts:

| value | `typeof` |
|---|---|
| `42` | `"number"` |
| `"a"` | `"string"` |
| `true` | `"boolean"` |
| `undefined` | `"undefined"` |
| `() => 1` | `"function"` |
| `{}` | `"object"` |
| `[1,2]` | `"object"` ⚠️ |
| `null` | `"object"` ⚠️ |

The last two are the traps. **Arrays are objects** — use `Array.isArray(x)`.
**`null` is an object** — a bug from 1995 that can never be fixed without
breaking the web. So this is wrong:

```ts
if (typeof x === "object") {
  x.name;      // 💥 x might be null
}
```

and the fix is to test for null first:

```ts
if (x !== null && typeof x === "object") { ... }
```

**Narrowing works with early returns too**, which pairs perfectly with week 5's
guard clauses:

```ts
function len(v: string | number[]): number {
  if (typeof v === "string") return v.length;
  return v.length;              // v: number[] — also has length, but a different one
}
```

**It narrows variables, not arbitrary expressions.** `typeof obj.v === "string"`
does narrow `obj.v` for a `const` object, but if anything could reassign it in
between, TypeScript gives the narrowing up. Pull the value into a local `const`
first when a check seems mysteriously not to stick.

> ⚠️ **Common mistakes:** using `typeof x === "array"` (there is no such thing);
> forgetting `null` passes an `"object"` check; and comparing to a misspelled
> string like `"nunber"` — the comparison is just a string comparison, so it
> silently never matches. (TypeScript does catch this one for you.)
""",
            warmup=[
                _q('`typeof [1,2]` is…', ['"array"', '"object"', '"list"', '"number"'], 1,
                   "Arrays are objects at runtime."),
                _q('`typeof null` is…', ['"null"', '"object"', '"undefined"', '"boolean"'], 1,
                   "A permanent JavaScript wart."),
                _q('After `if (typeof v === "number")` with `v: number | string`, the ELSE branch has v as…',
                   ["number | string", "string", "any", "never"], 1,
                   "Ruling out one member leaves the other."),
                _q('`typeof (() => 1)` is…', ['"object"', '"function"', '"arrow"', '"number"'], 1,
                   "Functions get their own typeof result."),
            ],
            exercises=[
                _ex("tscourse-w9-tf-1", "Narrow a number",
                    "Format the value with 2 decimals when it is a number, otherwise uppercase it.",
                    _LINE + 'const v: number | string = line === "x" ? "abc" : 3.14159;\n'
                    'if (typeof v === "number") {\n  console.log(v.toFixed(2));\n} else {\n  console.log(v.toUpperCase());\n}\n',
                    'typeof v === "number"',
                    [("n", "3.14"), ("x", "ABC")],
                    hints=["Compare typeof against the type name as a string.",
                           'Write typeof v === "number".']),
                _ex("tscourse-w9-tf-2", "Guard-clause style",
                    "Return early for the string case, then handle the number.",
                    _LINE + 'function show(v: number | string): string {\n'
                    '  if (typeof v === "string") return v.toUpperCase();\n'
                    '  return v.toFixed(2);\n}\n'
                    'console.log(show(line === "x" ? "abc" : 3.14159));\n',
                    'if (typeof v === "string") return v.toUpperCase();',
                    [("x", "ABC"), ("n", "3.14")],
                    hints=["Reject one member up front, and the rest of the body is the other.",
                           'Write if (typeof v === "string") return v.toUpperCase();'],
                    difficulty="Medium"),
                _ex("tscourse-w9-tf-3", "Label it by member",
                    "Print `chars: 5` for a string and `items: 3` for an array.",
                    _LINE + 'const v: string | number[] = line === "a" ? [1, 2, 3] : "hello";\n'
                    'console.log(typeof v === "string" ? `chars: ${v.length}` : `items: ${v.length}`);\n',
                    'typeof v === "string" ? `chars: ${v.length}` : `items: ${v.length}`',
                    [("a", "items: 3"), ("b", "chars: 5")],
                    hints=["Both members have a length, but they mean different things — so the branch decides the wording.",
                           "Write typeof v === \"string\" ? `chars: ${v.length}` : `items: ${v.length}`."],
                    difficulty="Medium"),
                _ex("tscourse-w9-tf-4", "Count by runtime type",
                    "Print how many entries in the mixed list are numbers.",
                    'const mixed: (string | number)[] = [1, "a", 2, "b", 3];\n'
                    'console.log(mixed.filter((x) => typeof x === "number").length);\n',
                    'typeof x === "number"', [("", "3")],
                    hints=["Filter by the runtime type of each element."]),
                _ex("tscourse-w9-tf-5", "Null-safe object check",
                    "Print `object` only for a real object, `null` for null, `other` otherwise.",
                    _LINE + 'const v: object | null | string = line === "o" ? {} : line === "z" ? null : "s";\n'
                    'if (v === null) {\n  console.log("null");\n} else if (typeof v === "object") {\n  console.log("object");\n} else {\n  console.log("other");\n}\n',
                    'v === null',
                    [("o", "object"), ("z", "null"), ("q", "other")],
                    hints=["typeof null is \"object\", so null must be ruled out first.",
                           "Test v === null before the typeof check."],
                    difficulty="Medium"),
                _fix("tscourse-w9-tf-fix1", "Fix the array check",
                     "There is no `\"array\"` typeof, so this always prints `not`. Fix it so an array prints `array`.",
                     'const v: string | number[] = [1, 2, 3];\n'
                     'console.log(typeof v === "array" ? "array" : "not");\n',
                     'const v: string | number[] = [1, 2, 3];\n'
                     'console.log(Array.isArray(v) ? "array" : "not");\n',
                     [("", "array")],
                     hints=['typeof an array is "object", never "array".',
                            "Use Array.isArray(v)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Control-flow analysis means…",
                   ["the code runs faster", "the type of a variable differs along different branches",
                    "types are checked at runtime", "loops are unrolled"], 1,
                   "TypeScript tracks what each check has proved."),
                _q("`if (typeof x === \"object\") x.name;` is unsafe because…",
                   ["objects have no name", "null also passes that check", "typeof is slow",
                    "it is fine"], 1,
                   "Rule out null explicitly."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w9-equality", "Narrowing by equality & switch",
            "Comparing against literals, and dispatching on them.",
            """
For a union of **literal types**, `typeof` is useless — every member is a
string. Compare against the values instead:

```ts
type Status = "paid" | "pending" | "failed";

function label(s: Status): string {
  if (s === "paid") {
    return "Settled";       // s: "paid"
  }
  return "Outstanding";     // s: "pending" | "failed"
}
```

Notice the else branch: TypeScript has removed only the member you ruled out.
The remaining type is still a union — a smaller one.

**`switch` narrows the same way**, and reads much better with three or more
cases:

```ts
switch (s) {
  case "paid":    return "Settled";      // s: "paid"
  case "pending": return "Waiting";      // s: "pending"
  case "failed":  return "Rejected";     // s: "failed"
}
```

Each `case` narrows to exactly one member inside its arm. And because every
member is covered, TypeScript can see the function always returns — no `default`
needed, and no "not all code paths return a value" error. That's a small miracle
that only works because the type is a finite union.

**Narrowing by equality between two unions** also works, and is occasionally
handy:

```ts
function f(a: string | number, b: string | boolean) {
  if (a === b) {
    // both must be string — the only overlap
  }
}
```

**`!==` narrows the negative side**, which is how you strip `undefined`:

```ts
function g(v: string | undefined): string {
  if (v === undefined) return "(none)";
  return v.toUpperCase();      // v: string
}
```

**Narrowing survives assignment.** Assigning a value to a union-typed variable
narrows it from that point on:

```ts
let v: string | number;
v = "hi";
v.toUpperCase();      // ✅ TypeScript knows it is a string right now
```

> ⚠️ **Common mistakes:** using `==` and getting unexpected coercion; assuming
> the else branch narrows to a single member when the union had three; and
> adding a `default` that returns something bogus, which silently disables the
> exhaustiveness benefit you'll meet in lesson 7.
""",
            warmup=[
                _q('With `s: "a"|"b"|"c"`, after `if (s === "a")` the ELSE branch is…',
                   ['"a"', '"b" | "c"', "string", "never"], 1,
                   "Only the tested member is removed."),
                _q("A switch covering every member of a literal union…",
                   ["still needs a default to compile", "can omit default and still be seen to always return",
                    "cannot narrow", "is an error"], 1,
                   "Exhaustiveness is visible to the compiler."),
                _q("`if (v === undefined) return; ` then `v` is…",
                   ["still the union", "the union minus undefined", "any", "never"], 1,
                   "The negative branch is narrowed too."),
                _q("`let v: string | number; v = 5; v.toFixed(2)` is…",
                   ["an error", "fine — assignment narrowed it", "a runtime error", "undefined"], 1,
                   "Narrowing by assignment."),
            ],
            exercises=[
                _ex("tscourse-w9-eq-1", "Compare to a literal",
                    "Return `Settled` for paid and `Outstanding` for anything else.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s === "paid" ? "Settled" : "Outstanding");\n',
                    's === "paid" ? "Settled" : "Outstanding"',
                    [("paid", "Settled"), ("pending", "Outstanding"), ("x", "Outstanding")],
                    hints=["Compare the value against the literal member.",
                           'Write s === "paid" ? "Settled" : "Outstanding".']),
                _ex("tscourse-w9-eq-2", "Switch on a union",
                    "Complete the pending case so it prints `Waiting`.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'switch (s) {\n'
                    '  case "paid":\n    console.log("Settled");\n    break;\n'
                    '  case "pending":\n    console.log("Waiting");\n    break;\n'
                    '  case "failed":\n    console.log("Rejected");\n    break;\n'
                    '}\n',
                    'case "pending":\n    console.log("Waiting");\n    break;',
                    [("paid", "Settled"), ("pending", "Waiting"), ("x", "Rejected")],
                    hints=["A case label, the statement, then break.",
                           'Write case "pending": console.log("Waiting"); break;'],
                    difficulty="Medium"),
                _ex("tscourse-w9-eq-3", "Strip the undefined",
                    "Return `(none)` when the value is missing, else the value uppercased.",
                    _LINE + 'function g(v: string | undefined): string {\n'
                    '  if (v === undefined) return "(none)";\n'
                    '  return v.toUpperCase();\n}\n'
                    'console.log(g(line === "z" ? undefined : line));\n',
                    'if (v === undefined) return "(none)";',
                    [("z", "(none)"), ("hi", "HI")],
                    hints=["Reject the undefined case first, and the rest is a plain string.",
                           'Write if (v === undefined) return "(none)";'],
                    difficulty="Medium"),
                _ex("tscourse-w9-eq-4", "Two of three",
                    "Print `open` for pending or failed, `closed` for paid.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(s === "pending" || s === "failed" ? "open" : "closed");\n',
                    's === "pending" || s === "failed"',
                    [("pending", "open"), ("x", "open"), ("paid", "closed")],
                    hints=["Two members share an outcome, so test for either.",
                           'Write s === "pending" || s === "failed".']),
                _ex("tscourse-w9-eq-5", "Narrow by assignment",
                    "Assign a string, then use a string method with no further checking.",
                    'let v: string | number;\nv = "hi";\nconsole.log(v.toUpperCase());\n',
                    'v = "hi";', [("", "HI")],
                    hints=["Assigning a value narrows the variable from that point on.",
                           'Write v = "hi";']),
                _fix("tscourse-w9-eq-fix1", "Fix the missing break",
                     "For `paid` this prints two lines. Fix it so each status prints exactly one.",
                     _LINE + 'type Status = "paid" | "pending";\n'
                     'const s: Status = line === "paid" ? "paid" : "pending";\n'
                     'switch (s) {\n'
                     '  case "paid":\n    console.log("Settled");\n'
                     '  case "pending":\n    console.log("Waiting");\n    break;\n'
                     '}\n',
                     _LINE + 'type Status = "paid" | "pending";\n'
                     'const s: Status = line === "paid" ? "paid" : "pending";\n'
                     'switch (s) {\n'
                     '  case "paid":\n    console.log("Settled");\n    break;\n'
                     '  case "pending":\n    console.log("Waiting");\n    break;\n'
                     '}\n',
                     [("paid", "Settled"), ("pending", "Waiting")],
                     hints=["Without break, execution falls into the next case.",
                            "Add break; to the paid case."],
                     difficulty="Medium"),
                _fix("tscourse-w9-eq-fix2", "Fix the fallthrough",
                     "This should print `1 2 3`. One case forgets to break, so it runs on into the next one and overwrites its own answer.",
                     'type Level = "low" | "mid" | "high";\n'
                     'function score(l: Level): number {\n'
                     '  let n = 0;\n'
                     '  switch (l) {\n'
                     '    case "low":\n'
                     '      n = 1;\n'
                     '    case "mid":\n'
                     '      n = 2;\n'
                     '      break;\n'
                     '    case "high":\n'
                     '      n = 3;\n'
                     '      break;\n'
                     '  }\n'
                     '  return n;\n}\n'
                     'console.log(`${score("low")} ${score("mid")} ${score("high")}`);\n',
                     'type Level = "low" | "mid" | "high";\n'
                     'function score(l: Level): number {\n'
                     '  let n = 0;\n'
                     '  switch (l) {\n'
                     '    case "low":\n'
                     '      n = 1;\n'
                     '      break;\n'
                     '    case "mid":\n'
                     '      n = 2;\n'
                     '      break;\n'
                     '    case "high":\n'
                     '      n = 3;\n'
                     '      break;\n'
                     '  }\n'
                     '  return n;\n}\n'
                     'console.log(`${score("low")} ${score("mid")} ${score("high")}`);\n',
                     [("", "1 2 3")],
                     hints=["A case without break keeps running into the case below it.",
                            "This is why a switch of returns is safer than a switch of assignments."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does typeof not help with `\"a\" | \"b\"`?",
                   ["typeof is broken", "every member is a string, so typeof cannot tell them apart",
                    "literals have no typeof", "it does help"], 1,
                   "Compare against the values instead."),
                _q("A `default` branch that returns a placeholder…",
                   ["is best practice", "hides a forgotten case from the exhaustiveness check",
                    "is required", "narrows better"], 1,
                   "It makes the compiler stop warning you."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w9-guards", "The other guards",
            "Truthiness, in, Array.isArray and instanceof.",
            """
Four more ways to narrow, each for a situation the previous two don't cover.

**Truthiness** removes every falsy member at once:

```ts
function f(v: string | undefined | null) {
  if (v) {
    v.toUpperCase();     // v: string
  }
}
```

Convenient — and it also removes `""`, which may be a legitimate value. When
the empty string or `0` matters, be explicit:

```ts
if (v !== undefined && v !== null) { ... }
if (v != null) { ... }        // the one accepted use of != : catches both
```

**`Array.isArray`** is the correct array test, because `typeof` says
`"object"`:

```ts
function count(v: string | string[]): number {
  if (Array.isArray(v)) return v.length;    // v: string[]
  return 1;                                  // v: string
}
```

**`in`** distinguishes object shapes by the presence of a key — the tool for a
union of objects with **no** shared tag:

```ts
type Contact = { email: string } | { phone: string };

function reach(c: Contact): string {
  if ("email" in c) {
    return c.email;      // c: { email: string }
  }
  return c.phone;        // c: { phone: string }
}
```

**`instanceof`** narrows against a class or constructor. The everyday case is
error handling:

```ts
try {
  risky();
} catch (e) {
  if (e instanceof Error) {
    console.log(e.message);    // e: Error
  }
}
```

(A caught `e` is `unknown` in modern TypeScript, precisely so you're forced to
check.)

**Choosing a guard:**

| the union is… | use |
|---|---|
| primitives (`number \\| string`) | `typeof` |
| literal values (`"a" \\| "b"`) | `===` or `switch` |
| maybe-missing (`T \\| undefined`) | `=== undefined`, or truthiness if safe |
| array or not | `Array.isArray` |
| object shapes without a tag | `in` |
| class instances | `instanceof` |
| object shapes **with** a tag | `switch` on the tag ← next lesson, and the best option |

> ⚠️ **Common mistakes:** using truthiness on a union containing `0` or `""`;
> using `typeof x === "object"` for arrays; and using `in` with a variable key
> (`k in obj` narrows nothing useful — it needs a literal).
""",
            warmup=[
                _q("`if (v)` on `string | undefined` also removes…",
                   ["nothing else", "the empty string", "numbers", "null only"], 1,
                   '"" is falsy, so a legitimate empty string is excluded too.'),
                _q("The correct array test is…",
                   ['typeof x === "array"', "Array.isArray(x)", "x instanceof Array only",
                    "x.length !== undefined"], 1,
                   "typeof can never say \"array\"."),
                _q('`"email" in c` narrows a union of object shapes by…',
                   ["their names", "the presence of that key", "their length", "typeof"], 1,
                   "Useful when there is no shared tag."),
                _q("In modern TypeScript a caught `e` in `catch (e)` has type…",
                   ["Error", "any", "unknown", "string"], 2,
                   "Which forces you to narrow before using it."),
            ],
            exercises=[
                _ex("tscourse-w9-gu-1", "Truthiness guard",
                    "Print the value uppercased, or `(none)` when it is missing or empty.",
                    _LINE + 'const v: string | undefined = line === "z" ? undefined : line;\n'
                    'console.log(v ? v.toUpperCase() : "(none)");\n',
                    'v ? v.toUpperCase() : "(none)"',
                    [("hi", "HI"), ("z", "(none)")],
                    hints=["A truthiness test removes undefined (and empty strings).",
                           'Write v ? v.toUpperCase() : "(none)".']),
                _ex("tscourse-w9-gu-2", "Keep a legitimate zero",
                    "Print the number, treating only a genuinely missing value as `(none)`.",
                    _LINE + 'const v: number | undefined = line === "z" ? undefined : Number(line);\n'
                    'console.log(v !== undefined ? v : "(none)");\n',
                    'v !== undefined ? v : "(none)"',
                    [("0", "0"), ("z", "(none)"), ("7", "7")],
                    hints=["Truthiness would discard the 0.",
                           'Write v !== undefined ? v : "(none)".'],
                    difficulty="Medium"),
                _ex("tscourse-w9-gu-3", "Array or single",
                    "Return the number of items: the array's length, or 1 for a lone string.",
                    _LINE + 'function count(v: string | string[]): number {\n'
                    '  if (Array.isArray(v)) return v.length;\n'
                    '  return 1;\n}\n'
                    'console.log(count(line === "a" ? ["x", "y", "z"] : "solo"));\n',
                    'if (Array.isArray(v)) return v.length;',
                    [("a", "3"), ("b", "1")],
                    hints=["typeof cannot tell an array from an object.",
                           "Write if (Array.isArray(v)) return v.length;"],
                    difficulty="Medium"),
                _ex("tscourse-w9-gu-4", "Narrow with in",
                    "Return the email when present, otherwise the phone.",
                    _LINE + 'type Contact = { email: string } | { phone: string };\n'
                    'function reach(c: Contact): string {\n'
                    '  if ("email" in c) return c.email;\n'
                    '  return c.phone;\n}\n'
                    'console.log(reach(line === "e" ? { email: "a@b.c" } : { phone: "123" }));\n',
                    'if ("email" in c) return c.email;',
                    [("e", "a@b.c"), ("p", "123")],
                    hints=["These shapes share no tag, so test for a key.",
                           'Write if ("email" in c) return c.email;'],
                    difficulty="Medium"),
                _ex("tscourse-w9-gu-5", "Narrow a caught error",
                    "Print the error's message when it is a real Error, otherwise `unknown error`.",
                    'function risky(): void {\n  throw new Error("boom");\n}\n'
                    'try {\n  risky();\n} catch (e) {\n'
                    '  console.log(e instanceof Error ? e.message : "unknown error");\n}\n',
                    'e instanceof Error ? e.message : "unknown error"',
                    [("", "boom")],
                    hints=["A caught value is unknown until you check it.",
                           'Write e instanceof Error ? e.message : "unknown error".'],
                    difficulty="Medium"),
                _fix("tscourse-w9-gu-fix1", "Fix the discarded zero",
                     "A value of 0 is real data, but this prints `(none)`. Fix it.",
                     _LINE + 'const v: number | undefined = line === "z" ? undefined : Number(line);\n'
                     'console.log(v ? v : "(none)");\n',
                     _LINE + 'const v: number | undefined = line === "z" ? undefined : Number(line);\n'
                     'console.log(v !== undefined ? v : "(none)");\n',
                     [("0", "0"), ("z", "(none)"), ("7", "7")],
                     hints=["0 is falsy, so the truthiness guard rejects it.",
                            "Test explicitly against undefined."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`if (v != null)` catches…",
                   ["only null", "only undefined", "both null and undefined",
                    "every falsy value"], 2,
                   "The single defensible use of loose inequality."),
                _q("You have a union of object shapes with no shared field name. Use…",
                   ["typeof", "in", "Array.isArray", "==="], 1,
                   "`in` distinguishes by key presence."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w9-discriminated", "Discriminated unions",
            "The pattern that makes 'one of several shapes' pleasant.",
            """
This is the most important idea in the week, and one of the most important in
TypeScript.

A **discriminated union** is a union of object types that all carry a **literal
field in common** — the *discriminant*, or *tag*:

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number }
  | { kind: "rect"; w: number; h: number };
```

Every member has `kind`, and each `kind` is a different literal. Switch on it
and TypeScript narrows to exactly one member per arm:

```ts
function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return 3.14159 * s.r * s.r;    // s.r exists here
    case "square": return s.side * s.side;         // s.side exists here
    case "rect":   return s.w * s.h;
  }
}
```

Inside `case "circle"` you may read `s.r` and **may not** read `s.side` — the
compiler knows which member you have. No casts, no optional fields, no
defensive checks.

**Why this beats optional fields.** The alternative people reach for first:

```ts
interface Shape { kind: string; r?: number; side?: number; w?: number; h?: number }
```

That type permits `{ kind: "circle", side: 3 }` and `{ kind: "banana" }`, and
every read needs a `?? 0`. The discriminated union makes those states
**unrepresentable** — the phrase from week 8, now with teeth.

**The canonical use: results that might fail.**

```ts
type Result =
  | { ok: true; value: number }
  | { ok: false; error: string };

function show(r: Result): string {
  if (r.ok) {
    return `= ${r.value}`;     // value exists only on the success member
  }
  return `! ${r.error}`;
}
```

Note the discriminant here is a **boolean literal** (`true` / `false`), and a
plain `if (r.ok)` narrows it. The tag doesn't have to be a string.

**Naming the tag.** `kind`, `type`, `status`, `ok` — anything, as long as it is
consistent and its values are literal types. `type` is common in the wider
ecosystem; `kind` avoids clashing with the keyword in your own reading.

**Modelling state** is the other everyday use, and it kills a whole class of
bug:

```ts
type Load =
  | { kind: "loading" }
  | { kind: "loaded"; items: string[] }
  | { kind: "failed"; error: string };
```

There is now no way to be loading *and* have items, or failed *and* have no
error.

> ⚠️ **Common mistakes:** giving the tag a non-literal type (`kind: string`),
> which disables all narrowing; forgetting the tag on one member; and using a
> different field name for the tag in different members.
""",
            warmup=[
                _q("A discriminated union's tag must be…",
                   ["a string", "a literal type", "optional", "a number"], 1,
                   "`kind: string` would narrow nothing."),
                _q('In `case "circle":` of a switch on `s.kind`, `s` is…',
                   ["the whole union", "just the circle member", "any", "never"], 1,
                   "That is the whole payoff."),
                _q("`type R = {ok: true; value: number} | {ok: false; error: string}` — after `if (r.ok)`, `r.error` is…",
                   ["available", "a compile error", "undefined", "any"], 1,
                   "The success member has no error field."),
                _q("Compared with optional fields, a discriminated union…",
                   ["is longer to write only", "makes invalid combinations unrepresentable",
                    "is slower", "needs classes"], 1,
                   "The type itself rules out nonsense."),
            ],
            exercises=[
                _ex("tscourse-w9-di-1", "Switch on the tag",
                    "Complete the square case so it returns side squared.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number };\n'
                    'function area(s: Shape): number {\n'
                    '  switch (s.kind) {\n'
                    '    case "circle":\n      return 3 * s.r * s.r;\n'
                    '    case "square":\n      return s.side * s.side;\n'
                    '  }\n}\n'
                    'console.log(area(line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 }));\n',
                    'return s.side * s.side;', [("c", "12"), ("s", "16")],
                    hints=["Inside this case the compiler knows the member has `side`.",
                           "Write return s.side * s.side;"],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-2", "Build a valid member",
                    "Construct the circle member — it needs the tag AND that member's own field.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number };\n'
                    'const s: Shape = line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 };\n'
                    'console.log(s.kind);\n',
                    '{ kind: "circle", r: 2 }',
                    [("c", "circle"), ("s", "square")],
                    hints=["A member must carry its literal tag and exactly the fields that member declares.",
                           'Write { kind: "circle", r: 2 }.'],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-3", "A Result type",
                    "Print `= <value>` on success and `! <error>` on failure.",
                    _LINE + 'type Result =\n'
                    '  | { ok: true; value: number }\n'
                    '  | { ok: false; error: string };\n'
                    'const n = Number(line);\n'
                    'const r: Result = Number.isNaN(n) ? { ok: false, error: "not a number" } : { ok: true, value: n };\n'
                    'console.log(r.ok ? `= ${r.value}` : `! ${r.error}`);\n',
                    'r.ok ? `= ${r.value}` : `! ${r.error}`',
                    [("42", "= 42"), ("abc", "! not a number")],
                    hints=["A boolean tag narrows with a plain truthiness test.",
                           "Write r.ok ? `= ${r.value}` : `! ${r.error}`."],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-4", "Build the failure case",
                    "Return the failing Result when the input does not parse.",
                    _LINE + 'type Result =\n'
                    '  | { ok: true; value: number }\n'
                    '  | { ok: false; error: string };\n'
                    'function parse(s: string): Result {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: "bad" };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parse(line);\nconsole.log(r.ok ? r.value : r.error);\n',
                    'return { ok: false, error: "bad" };',
                    [("7", "7"), ("zz", "bad")],
                    hints=["The failure member carries the tag AND the error field.",
                           'Write return { ok: false, error: "bad" };'],
                    difficulty="Medium"),
                _ex("tscourse-w9-di-5", "Model a loading state",
                    "Print `loading`, `n items`, or `error: <msg>` for each state.",
                    _LINE + 'type Load =\n'
                    '  | { kind: "loading" }\n'
                    '  | { kind: "loaded"; items: string[] }\n'
                    '  | { kind: "failed"; error: string };\n'
                    'const st: Load =\n'
                    '  line === "l" ? { kind: "loading" }\n'
                    '  : line === "d" ? { kind: "loaded", items: ["a", "b"] }\n'
                    '  : { kind: "failed", error: "oops" };\n'
                    'switch (st.kind) {\n'
                    '  case "loading":\n    console.log("loading");\n    break;\n'
                    '  case "loaded":\n    console.log(`${st.items.length} items`);\n    break;\n'
                    '  case "failed":\n    console.log(`error: ${st.error}`);\n    break;\n'
                    '}\n',
                    'console.log(`${st.items.length} items`);',
                    [("l", "loading"), ("d", "2 items"), ("f", "error: oops")],
                    hints=["Only the loaded member has items, and only inside its case.",
                           "Write console.log(`${st.items.length} items`);"],
                    difficulty="Medium"),
                _fix("tscourse-w9-di-fix1", "Fix the untagged union",
                     "The tag was typed as `string`, so narrowing is impossible and this reads the wrong field. Give each member a literal tag and read the right one.",
                     _LINE + 'type Shape =\n'
                     '  | { kind: string; r: number }\n'
                     '  | { kind: string; side: number };\n'
                     'const s: Shape = line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 };\n'
                     'console.log(s.kind === "circle" ? 12 : 12);\n',
                     _LINE + 'type Shape =\n'
                     '  | { kind: "circle"; r: number }\n'
                     '  | { kind: "square"; side: number };\n'
                     'const s: Shape = line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 };\n'
                     'console.log(s.kind === "circle" ? 3 * s.r * s.r : s.side * s.side);\n',
                     [("c", "12"), ("s", "16")],
                     hints=["`kind: string` is not a literal type, so no narrowing happens and the areas had to be hard-coded.",
                            'Change the tags to the literals "circle" and "square", then compute each area from the member\'s own field.'],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The discriminant of a union must be…",
                   ["named kind", "a literal-typed field present on every member", "a string",
                    "optional"], 1,
                   "The name is free; being a literal on every member is not."),
                _q("A Result union beats returning `number | null` because…",
                   ["it is shorter", "the failure can carry an explanation, and success cannot be confused with it",
                    "it is faster", "null is banned"], 1,
                   "You get the reason, not just the absence."),
                _q("`{ kind: \"circle\", side: 3 }` against a proper Shape union is…",
                   ["allowed", "a compile error", "allowed but undefined", "a runtime error"], 1,
                   "The tag and the fields must agree — that is the whole point."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w9-exhaustive", "Exhaustiveness & intersections",
            "Making the compiler catch the case you forgot.",
            """
Discriminated unions give you one more thing, and it is the reason experienced
people reach for them: **the compiler can prove you handled every case.**

Start with a `never` refresher. `never` is the type with **no values** — the
type of a situation that cannot happen. If you've handled every member of a
union, the value that reaches the `default` branch has type `never`, because
nothing is left.

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return 3.14159 * s.r * s.r;
    case "square": return s.side * s.side;
    default: {
      const _exhaustive: never = s;      // ✅ compiles: s is never here
      return _exhaustive;
    }
  }
}
```

Now **add a third member** to `Shape` and forget to handle it. `s` in the
`default` is no longer `never` — it's the new member — so
`const _exhaustive: never = s;` **fails to compile**, pointing straight at the
function you forgot to update.

That is a genuinely powerful property: adding a case to a type produces a list
of every place that must change. It's why "make the illegal states
unrepresentable" pays off — the compiler becomes a to-do list.

**Without the trick**, a forgotten case falls through the `default` and returns
something plausible-but-wrong at runtime. With it, the code doesn't build.

**A note on returns.** If every case returns and you *don't* write a `default`,
TypeScript already knows the switch is exhaustive and won't complain about a
missing return. Adding the `never` check makes that guarantee explicit and
survives someone later adding a member.

---

**Intersections** are the other half of the type algebra. Where `A | B` is
"either", `A & B` is **both**:

```ts
type Timestamped = { created: string };
type Named = { name: string };

type Entry = Timestamped & Named;      // has created AND name

const e: Entry = { created: "mon", name: "coffee" };   // both required
```

Use them to bolt a common set of fields onto several types:

```ts
type WithId<T> = T & { id: string };    // (generics arrive next week)
```

**Union and intersection pull in opposite directions.** A union has *fewer*
usable members (only the shared ones); an intersection has *more* (all of them).
Beginners routinely expect the opposite, because "union" sounds bigger. The
rule: a union is a bigger set of **values**, and therefore a smaller set of
**guaranteed members**.

Intersecting incompatible primitives gives `never` — no value can be both:

```ts
type Impossible = string & number;      // never
```

> ⚠️ **Common mistakes:** adding a `default` that returns a fallback, which
> silently defeats exhaustiveness; expecting `A | B` to give you the members of
> both; and forgetting that the `never` check must actually *assign* the value
> to a `never`-typed name.
""",
            warmup=[
                _q("`never` is the type of…",
                   ["null", "a value that cannot exist", "undefined", "any value"], 1,
                   "It has no values at all."),
                _q("In an exhaustive switch's default, the value has type…",
                   ["the union", "never", "any", "unknown"], 1,
                   "Every member was removed by a case."),
                _q("Adding a member to the union and forgetting a case makes the never check…",
                   ["still compile", "fail to compile, pointing at the switch", "throw at runtime",
                    "warn only"], 1,
                   "Which is exactly the point."),
                _q("`A & B` gives a value with…",
                   ["either A's or B's members", "all of A's and B's members", "no members",
                    "only shared members"], 1,
                   "Intersection combines; union restricts."),
            ],
            exercises=[
                _ex("tscourse-w9-ex-1", "Add the exhaustiveness check",
                    "Complete the default branch so a forgotten case would fail to compile.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number };\n'
                    'function area(s: Shape): number {\n'
                    '  switch (s.kind) {\n'
                    '    case "circle":\n      return 3 * s.r * s.r;\n'
                    '    case "square":\n      return s.side * s.side;\n'
                    '    default: {\n'
                    '      const _exhaustive: never = s;\n'
                    '      return _exhaustive;\n'
                    '    }\n'
                    '  }\n}\n'
                    'console.log(area(line === "c" ? { kind: "circle", r: 2 } : { kind: "square", side: 4 }));\n',
                    'const _exhaustive: never = s;', [("c", "12"), ("s", "16")],
                    hints=["Assign the leftover value to a name annotated as never.",
                           "Write const _exhaustive: never = s;"],
                    difficulty="Medium"),
                _ex("tscourse-w9-ex-2", "Handle the new case",
                    "A third shape was added. Handle it so the switch stays exhaustive.",
                    _LINE + 'type Shape =\n'
                    '  | { kind: "circle"; r: number }\n'
                    '  | { kind: "square"; side: number }\n'
                    '  | { kind: "rect"; w: number; h: number };\n'
                    'function area(s: Shape): number {\n'
                    '  switch (s.kind) {\n'
                    '    case "circle":\n      return 3 * s.r * s.r;\n'
                    '    case "square":\n      return s.side * s.side;\n'
                    '    case "rect":\n      return s.w * s.h;\n'
                    '    default: {\n'
                    '      const _exhaustive: never = s;\n'
                    '      return _exhaustive;\n'
                    '    }\n'
                    '  }\n}\n'
                    'console.log(area(line === "r" ? { kind: "rect", w: 2, h: 5 } : { kind: "square", side: 4 }));\n',
                    'case "rect":\n      return s.w * s.h;', [("r", "10"), ("s", "16")],
                    hints=["The new member has w and h.",
                           'Write case "rect": return s.w * s.h;'],
                    difficulty="Medium"),
                _ex("tscourse-w9-ex-3", "An intersection",
                    "Combine the two shapes with & so the value must have both fields.",
                    'type Timestamped = { created: string };\n'
                    'type Named = { name: string };\n'
                    'type Entry = Timestamped & Named;\n'
                    'const e: Entry = { created: "mon", name: "coffee" };\n'
                    'console.log(`${e.created} ${e.name}`);\n',
                    'Timestamped & Named', [("", "mon coffee")],
                    hints=["& means 'has all the members of both'.",
                           "Write Timestamped & Named."]),
                _ex("tscourse-w9-ex-4", "Extend records with a shared field",
                    "Total the amounts across records that carry both an id and an amount.",
                    'type WithId = { id: string };\n'
                    'type Amounted = { amount: number };\n'
                    'const rows: (WithId & Amounted)[] = [\n'
                    '  { id: "a", amount: 3 },\n  { id: "b", amount: 12 },\n];\n'
                    'console.log(rows.reduce((s, r) => s + r.amount, 0));\n',
                    '(WithId & Amounted)[]', [("", "15")],
                    hints=["Each element has all the members of both types.",
                           "Write (WithId & Amounted)[]."],
                    difficulty="Medium"),
                _ex("tscourse-w9-ex-5", "Exhaustive over a status",
                    "Complete the failed case so every Status is handled.",
                    _LINE + 'type Status = "paid" | "pending" | "failed";\n'
                    'function label(s: Status): string {\n'
                    '  switch (s) {\n'
                    '    case "paid":\n      return "Settled";\n'
                    '    case "pending":\n      return "Waiting";\n'
                    '    case "failed":\n      return "Rejected";\n'
                    '    default: {\n'
                    '      const _exhaustive: never = s;\n      return _exhaustive;\n'
                    '    }\n'
                    '  }\n}\n'
                    'const s: Status = line === "paid" ? "paid" : line === "pending" ? "pending" : "failed";\n'
                    'console.log(label(s));\n',
                    'case "failed":\n      return "Rejected";',
                    [("paid", "Settled"), ("pending", "Waiting"), ("x", "Rejected")],
                    hints=["Without this case the never check would not compile.",
                           'Write case "failed": return "Rejected";'],
                    difficulty="Medium"),
                _fix("tscourse-w9-ex-fix1", "Fix the defeated exhaustiveness",
                     "The default returns a bogus 0, hiding the unhandled `rect` case — so a rect prints 0 instead of 10. Handle rect properly.",
                     _LINE + 'type Shape =\n'
                     '  | { kind: "circle"; r: number }\n'
                     '  | { kind: "square"; side: number }\n'
                     '  | { kind: "rect"; w: number; h: number };\n'
                     'function area(s: Shape): number {\n'
                     '  switch (s.kind) {\n'
                     '    case "circle":\n      return 3 * s.r * s.r;\n'
                     '    case "square":\n      return s.side * s.side;\n'
                     '    default:\n      return 0;\n'
                     '  }\n}\n'
                     'console.log(area(line === "r" ? { kind: "rect", w: 2, h: 5 } : { kind: "square", side: 4 }));\n',
                     _LINE + 'type Shape =\n'
                     '  | { kind: "circle"; r: number }\n'
                     '  | { kind: "square"; side: number }\n'
                     '  | { kind: "rect"; w: number; h: number };\n'
                     'function area(s: Shape): number {\n'
                     '  switch (s.kind) {\n'
                     '    case "circle":\n      return 3 * s.r * s.r;\n'
                     '    case "square":\n      return s.side * s.side;\n'
                     '    case "rect":\n      return s.w * s.h;\n'
                     '    default: {\n'
                     '      const _exhaustive: never = s;\n      return _exhaustive;\n'
                     '    }\n'
                     '  }\n}\n'
                     'console.log(area(line === "r" ? { kind: "rect", w: 2, h: 5 } : { kind: "square", side: 4 }));\n',
                     [("r", "10"), ("s", "16")],
                     hints=["A plausible fallback in default is what let the missing case through silently.",
                            "Handle rect, and replace the fallback with the never check so the next omission is caught."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The never trick works because…",
                   ["never is a runtime check", "an unhandled member is not assignable to never",
                    "it throws", "default always runs"], 1,
                   "The assignment fails to compile precisely when a case remains."),
                _q("A union has ____ guaranteed members than any single member.",
                   ["more", "fewer or equal", "the same", "infinitely many"], 1,
                   "Only what all members share is usable."),
                _q("`string & number` is…",
                   ["string", "number", "never", "any"], 2,
                   "No value can be both, so the type is empty."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w9-predicates", "Custom type guards",
            "Teach the compiler to narrow through a function you wrote yourself.",
            """
Every narrowing you have done so far happened **inline** — `typeof`, `===`, `in`,
a `switch` on `kind`. The moment you move that test into a helper, the narrowing
evaporates:

```ts
function isCircle(s: Shape): boolean {
  return s.kind === "circle";
}

if (isCircle(s)) {
  console.log(s.r);    // ✗ Property 'r' does not exist on type 'Shape'
}
```

TypeScript sees a function returning `boolean`. It has no idea *what* that
boolean means. You have to say so — in the return position:

```ts
function isCircle(s: Shape): s is Circle {   // ← a type predicate
  return s.kind === "circle";
}

if (isCircle(s)) {
  console.log(s.r);    // ✓ narrowed to Circle
}
```

`s is Circle` reads: *"when this returns true, the argument named `s` is a
`Circle`"*. The parameter name on the left must be one of the function's own
parameters.

**The payoff is `filter`.** This is the moment custom guards stop being a
curiosity:

```ts
const values = ["gold", "wood", "silver"];
const coins: Coin[] = values.filter(isCoin);   // string[] → Coin[]
```

Without the predicate, `filter` hands back `string[]` and you are stuck casting.
With it, the narrowed element type flows out of the filter for free — every
later line knows it is holding coins.

**You are responsible for the truth of it.** A predicate is an *assertion*, in
the same family as `as`: the compiler believes the signature and never checks the
body. A guard whose body is wrong is worse than no guard, because now everything
downstream is confidently wrong.

```ts
function isCoin(v: string): v is Coin {
  return v.length > 0;      // ← compiles. Also completely untrue.
}
```

Keep the body a direct, obvious restatement of the type — one comparison per
member, nothing clever.

**Assertion functions** are the other half. Instead of returning a boolean they
narrow the caller's variable from that line on, and stop the program if the check
fails:

```ts
function assertNumber(v: unknown): asserts v is number {
  if (typeof v !== "number") throw new Error("not a number");
}

assertNumber(raw);
console.log(raw + 1);   // raw is a number from here down
```

(`throw` gets a proper treatment in Month 4 — for now read it as *"stop, this
should never have happened"*.) Use `asserts` for conditions that are genuinely
impossible if the program is correct, and a plain predicate for conditions you
expect to encounter and handle.

> ⚠️ **Common mistakes:** annotating the helper `: boolean` and wondering why
> narrowing is lost; naming a different variable on the left of `is`; writing a
> body that doesn't really establish the type; and reaching for `as` after the
> guard, which is a sign the predicate should have been written properly.
""",
            warmup=[
                _q("`function isCircle(s: Shape): boolean` used in an `if` narrows `s` to…",
                   ["Circle", "nothing — it stays Shape", "unknown", "never"], 1,
                   "A plain boolean carries no information about which member matched."),
                _q("The correct return annotation for a custom guard is…",
                   ["boolean", "s is Circle", "Circle", "asserts Circle"], 1,
                   "The predicate names a parameter and the type it establishes."),
                _q("`values.filter(isCoin)` where `isCoin` is a predicate returns…",
                   ["string[]", "Coin[]", "boolean[]", "unknown[]"], 1,
                   "The narrowed element type flows out of filter."),
                _q("If a predicate's body is wrong, TypeScript…",
                   ["reports an error", "believes it anyway", "falls back to boolean", "throws at runtime"], 1,
                   "It is an assertion — the signature is taken on trust."),
            ],
            exercises=[
                _ex("tscourse-w9-pred-1", "Write the predicate",
                    "Give `isCoin` a return annotation that narrows a string to a Coin.",
                    'type Coin = "gold" | "silver";\n'
                    'function isCoin(v: string): v is Coin {\n'
                    '  return v === "gold" || v === "silver";\n}\n'
                    'const values = ["gold", "wood", "silver"];\n'
                    'const coins: Coin[] = values.filter(isCoin);\n'
                    'console.log(coins.join(","));\n',
                    'v is Coin', [("", "gold,silver")],
                    hints=["Name the parameter, then `is`, then the type it establishes.",
                           "Write v is Coin."]),
                _ex("tscourse-w9-pred-2", "Narrow in an if",
                    "Fill in the body of the guard so each shape takes the right branch.",
                    'interface Circle {\n  kind: "circle";\n  r: number;\n}\n'
                    'interface Square {\n  kind: "square";\n  side: number;\n}\n'
                    'type Shape = Circle | Square;\n'
                    'function isCircle(s: Shape): s is Circle {\n'
                    '  return s.kind === "circle";\n}\n'
                    'const shapes: Shape[] = [{ kind: "circle", r: 2 }, { kind: "square", side: 3 }];\n'
                    'for (const s of shapes) {\n'
                    '  if (isCircle(s)) console.log(`circle area ${(Math.PI * s.r * s.r).toFixed(2)}`);\n'
                    '  else console.log(`square area ${s.side * s.side}`);\n'
                    '}\n',
                    'return s.kind === "circle";',
                    [("", "circle area 12.57\nsquare area 9")],
                    hints=["The body is the same discriminant check you would write inline.",
                           'Write return s.kind === "circle";'],
                    difficulty="Easy"),
                _ex("tscourse-w9-pred-3", "Guard, then trust",
                    "`label` should reject anything that isn't a Status before using it. Add the rejecting guard.",
                    'type Status = "todo" | "doing" | "done";\n'
                    'function isStatus(v: string): v is Status {\n'
                    '  return v === "todo" || v === "doing" || v === "done";\n}\n'
                    'function label(v: string): string {\n'
                    '  if (!isStatus(v)) return `unknown(${v})`;\n'
                    '  return v.toUpperCase();\n}\n'
                    'console.log(label("done"));\n'
                    'console.log(label("wat"));\n',
                    'if (!isStatus(v)) return `unknown(${v})`;',
                    [("", "DONE\nunknown(wat)")],
                    hints=["A guard clause: reject the bad case first, then the happy path runs narrowed.",
                           "Negate the predicate and return early."],
                    difficulty="Easy"),
                _ex("tscourse-w9-pred-4", "Filter into a narrower array",
                    "Keep only the published posts, then total their views. Fill in the filtering step.",
                    'interface Draft {\n  kind: "draft";\n  title: string;\n}\n'
                    'interface Published {\n  kind: "published";\n  title: string;\n  views: number;\n}\n'
                    'type Post = Draft | Published;\n'
                    'function isPublished(p: Post): p is Published {\n'
                    '  return p.kind === "published";\n}\n'
                    'const posts: Post[] = [\n'
                    '  { kind: "draft", title: "a" },\n'
                    '  { kind: "published", title: "b", views: 10 },\n'
                    '  { kind: "published", title: "c", views: 5 },\n'
                    '];\n'
                    'const live = posts.filter(isPublished);\n'
                    'const total = live.reduce((sum, p) => sum + p.views, 0);\n'
                    'console.log(`${live.length} live, ${total} views`);\n',
                    'posts.filter(isPublished)',
                    [("", "2 live, 15 views")],
                    hints=["Pass the predicate itself to filter — no arrow function needed.",
                           "Because it is a predicate, `live` comes out as Published[], so `.views` is available."],
                    difficulty="Medium"),
                _ex("tscourse-w9-pred-5", "An assertion function",
                    "Fill in the annotation that makes this narrow its argument from the call site onwards.",
                    'function assertNumber(v: unknown): asserts v is number {\n'
                    '  if (typeof v !== "number") throw new Error("not a number");\n}\n'
                    'const raw: unknown = 42;\n'
                    'assertNumber(raw);\n'
                    'console.log(raw + 1);\n',
                    'asserts v is number', [("", "43")],
                    hints=["An assertion function's return annotation starts with the word asserts.",
                           "Write asserts v is number."],
                    difficulty="Medium"),
                _fix("tscourse-w9-pred-fix1", "Fix the lying predicate",
                     "This should keep only `gold,silver`, but the guard's body doesn't actually establish the type — it accepts anything non-empty.",
                     'type Coin = "gold" | "silver";\n'
                     'function isCoin(v: string): v is Coin {\n'
                     '  return v.length > 0;\n}\n'
                     'const values = ["gold", "wood", "silver"];\n'
                     'console.log(values.filter(isCoin).join(","));\n',
                     'type Coin = "gold" | "silver";\n'
                     'function isCoin(v: string): v is Coin {\n'
                     '  return v === "gold" || v === "silver";\n}\n'
                     'const values = ["gold", "wood", "silver"];\n'
                     'console.log(values.filter(isCoin).join(","));\n',
                     [("", "gold,silver")],
                     hints=["The compiler believed the signature and never looked at the body.",
                            "Test the value against each member of the union."],
                     difficulty="Medium"),
                _fix("tscourse-w9-pred-fix2", "Fix the impossible condition",
                     "Every label comes back as unknown. The guard asks for a value that is two things at once.",
                     'type Status = "todo" | "done";\n'
                     'function isStatus(v: string): v is Status {\n'
                     '  return v === "todo" && v === "done";\n}\n'
                     'function label(v: string): string {\n'
                     '  if (!isStatus(v)) return `unknown(${v})`;\n'
                     '  return v.toUpperCase();\n}\n'
                     'console.log(label("done"));\n'
                     'console.log(label("todo"));\n'
                     'console.log(label("wat"));\n',
                     'type Status = "todo" | "done";\n'
                     'function isStatus(v: string): v is Status {\n'
                     '  return v === "todo" || v === "done";\n}\n'
                     'function label(v: string): string {\n'
                     '  if (!isStatus(v)) return `unknown(${v})`;\n'
                     '  return v.toUpperCase();\n}\n'
                     'console.log(label("done"));\n'
                     'console.log(label("todo"));\n'
                     'console.log(label("wat"));\n',
                     [("", "DONE\nTODO\nunknown(wat)")],
                     hints=["No single string can equal both members.",
                            "Membership of a union is an OR, not an AND."]),
                _fix("tscourse-w9-pred-fix3", "Fix the wrong field",
                     "This should report `2 live` but reports 0 — the guard is comparing the wrong property against the tag.",
                     'interface Draft {\n  kind: "draft";\n  title: string;\n}\n'
                     'interface Published {\n  kind: "published";\n  title: string;\n  views: number;\n}\n'
                     'type Post = Draft | Published;\n'
                     'function isPublished(p: Post): p is Published {\n'
                     '  return p.title === "published";\n}\n'
                     'const posts: Post[] = [\n'
                     '  { kind: "draft", title: "a" },\n'
                     '  { kind: "published", title: "b", views: 10 },\n'
                     '  { kind: "published", title: "c", views: 5 },\n'
                     '];\n'
                     'console.log(`${posts.filter(isPublished).length} live`);\n',
                     'interface Draft {\n  kind: "draft";\n  title: string;\n}\n'
                     'interface Published {\n  kind: "published";\n  title: string;\n  views: number;\n}\n'
                     'type Post = Draft | Published;\n'
                     'function isPublished(p: Post): p is Published {\n'
                     '  return p.kind === "published";\n}\n'
                     'const posts: Post[] = [\n'
                     '  { kind: "draft", title: "a" },\n'
                     '  { kind: "published", title: "b", views: 10 },\n'
                     '  { kind: "published", title: "c", views: 5 },\n'
                     '];\n'
                     'console.log(`${posts.filter(isPublished).length} live`);\n',
                     [("", "2 live")],
                     hints=["The discriminant is the `kind` field, not the title.",
                            "Both fields are strings, so the compiler had no way to object."],
                     difficulty="Medium"),
                _ch("tscourse-w9-pred-ch1", "Split a stream with guards", "Hard",
                    "Events arrive as `add,<number>` or `note,<text>`. Write the two predicates `isAdd` and `isNote`, then use them to build the total of every add and the list of every note.",
                    _FS +
                    'interface Add {\n  kind: "add";\n  amount: number;\n}\n'
                    'interface Note {\n  kind: "note";\n  text: string;\n}\n'
                    'type Event = Add | Note;\n'
                    'function toEvent(line: string): Event {\n'
                    '  const parts = line.split(",");\n'
                    '  if ((parts[0] ?? "").trim() === "add") return { kind: "add", amount: Number(parts[1]) };\n'
                    '  return { kind: "note", text: (parts[1] ?? "").trim() };\n}\n'
                    'function isAdd(e: Event): e is Add {\n'
                    '  return e.kind === "add";\n}\n'
                    'function isNote(e: Event): e is Note {\n'
                    '  return e.kind === "note";\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0);\n'
                    'const events: Event[] = lines.map(toEvent);\n'
                    'const total = events.filter(isAdd).reduce((sum, e) => sum + e.amount, 0);\n'
                    'const notes = events.filter(isNote).map((e) => e.text);\n'
                    'console.log(`Total: ${total}`);\n'
                    'console.log(`Notes: ${notes.join(" | ")}`);\n',
                    'function isAdd(e: Event): e is Add {\n'
                    '  return e.kind === "add";\n}\n'
                    'function isNote(e: Event): e is Note {\n'
                    '  return e.kind === "note";\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0);\n'
                    'const events: Event[] = lines.map(toEvent);\n'
                    'const total = events.filter(isAdd).reduce((sum, e) => sum + e.amount, 0);\n'
                    'const notes = events.filter(isNote).map((e) => e.text);',
                    [("add,10\nnote,hello\nadd,5\nnote,bye", "Total: 15\nNotes: hello | bye"),
                     ("note,x\nnote,y", "Total: 0\nNotes: x | y"),
                     ("add,7", "Total: 7\nNotes:")],
                    hints=["Each predicate is one line: compare the `kind` tag to its literal.",
                           "Filtering with a predicate gives you an Add[] and a Note[], so .amount and .text are both safe.",
                           "reduce over the adds with a starting accumulator of 0.",
                           "map the notes to their text before joining them."]),
            ],
            quiz=[
                _q("`function isCoin(v: string): v is Coin` differs from `: boolean` because…",
                   ["it is faster", "it tells the compiler what a true result means",
                    "it validates at runtime", "it cannot be used in filter"], 1,
                   "That is the entire content of a type predicate."),
                _q("The name on the left of `is` must be…",
                   ["any identifier", "one of the function's own parameters", "the return value", "a type"], 1,
                   "The predicate narrows that specific parameter."),
                _q("Passing a predicate to `filter` gives you…",
                   ["a boolean array", "an array of the narrowed type",
                    "the original array", "an error"], 1,
                   "Which is why predicates are worth writing at all."),
                _q("An `asserts v is number` function…",
                   ["returns a boolean", "narrows v from the call site on, and stops the program otherwise",
                    "converts v to a number", "is checked by the compiler"], 1,
                   "Use it for conditions that should be impossible."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #9 — the event log",
        """
Budget Buddy stops storing rows and starts storing **events**. Each line of
input is one event, and events come in three kinds:

```
add coffee 3.25
remove coffee
note reviewed the month
```

Model them as a **discriminated union**:

```ts
type Event =
  | { kind: "add"; desc: string; amount: number }
  | { kind: "remove"; desc: string }
  | { kind: "note"; text: string };
```

Process the log in order and print:

```
Events:  3
Added:   1 ($3.25)
Removed: 1 (coffee)
Notes:   1
Balance: $0.00
```

Rules:

- `Balance` is the total of every `add` minus the amount of every `remove` whose
  description was previously added. (Removing something never added changes
  nothing.)
- `Removed` lists the descriptions of removals, in order, joined with `, `.
- A `note` event's text is everything after the word `note`.
- Handle every kind with a `switch` on the tag — no optional fields.
""",
        _ch("tscourse-w9-capstone", "Budget Buddy #9", "Medium",
            "Parse each line into a tagged event, then fold the log.",
            _FS + 'type Event =\n'
            '  | { kind: "add"; desc: string; amount: number }\n'
            '  | { kind: "remove"; desc: string }\n'
            '  | { kind: "note"; text: string };\n'
            'function parse(line: string): Event {\n'
            '  const p = line.trim().split(" ");\n'
            '  if (p[0] === "add") return { kind: "add", desc: p[1] ?? "", amount: Number(p[2]) };\n'
            '  if (p[0] === "remove") return { kind: "remove", desc: p[1] ?? "" };\n'
            '  return { kind: "note", text: p.slice(1).join(" ") };\n'
            '}\n'
            'const events: Event[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const prices: { [key: string]: number } = {};\n'
            'let added = 0;\nlet notes = 0;\nlet balance = 0;\n'
            'const removed: string[] = [];\n'
            'for (const e of events) {\n'
            '  switch (e.kind) {\n'
            '    case "add":\n'
            '      added++;\n      balance += e.amount;\n      prices[e.desc] = e.amount;\n      break;\n'
            '    case "remove":\n'
            '      removed.push(e.desc);\n      balance -= prices[e.desc] ?? 0;\n      break;\n'
            '    case "note":\n'
            '      notes++;\n      break;\n'
            '  }\n'
            '}\n'
            'let addedTotal = 0;\n'
            'for (const e of events) {\n  if (e.kind === "add") addedTotal += e.amount;\n}\n'
            'console.log(`Events:  ${events.length}`);\n'
            'console.log(`Added:   ${added} ($${addedTotal.toFixed(2)})`);\n'
            'console.log(`Removed: ${removed.length} (${removed.join(", ")})`);\n'
            'console.log(`Notes:   ${notes}`);\n'
            'console.log(`Balance: $${balance.toFixed(2)}`);\n',
            'function parse(line: string): Event {\n'
            '  const p = line.trim().split(" ");\n'
            '  if (p[0] === "add") return { kind: "add", desc: p[1] ?? "", amount: Number(p[2]) };\n'
            '  if (p[0] === "remove") return { kind: "remove", desc: p[1] ?? "" };\n'
            '  return { kind: "note", text: p.slice(1).join(" ") };\n'
            '}\n'
            'const events: Event[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const prices: { [key: string]: number } = {};\n'
            'let added = 0;\nlet notes = 0;\nlet balance = 0;\n'
            'const removed: string[] = [];\n'
            'for (const e of events) {\n'
            '  switch (e.kind) {\n'
            '    case "add":\n'
            '      added++;\n      balance += e.amount;\n      prices[e.desc] = e.amount;\n      break;\n'
            '    case "remove":\n'
            '      removed.push(e.desc);\n      balance -= prices[e.desc] ?? 0;\n      break;\n'
            '    case "note":\n'
            '      notes++;\n      break;\n'
            '  }\n'
            '}\n'
            'let addedTotal = 0;\n'
            'for (const e of events) {\n  if (e.kind === "add") addedTotal += e.amount;\n}\n'
            'console.log(`Events:  ${events.length}`);\n'
            'console.log(`Added:   ${added} ($${addedTotal.toFixed(2)})`);\n'
            'console.log(`Removed: ${removed.length} (${removed.join(", ")})`);\n'
            'console.log(`Notes:   ${notes}`);\n'
            'console.log(`Balance: $${balance.toFixed(2)}`);',
            [("add coffee 3.25\nremove coffee\nnote reviewed the month",
              "Events:  3\nAdded:   1 ($3.25)\nRemoved: 1 (coffee)\nNotes:   1\nBalance: $0.00"),
             ("add book 12\nadd tea 2",
              "Events:  2\nAdded:   2 ($14.00)\nRemoved: 0 ()\nNotes:   0\nBalance: $14.00"),
             ("remove ghost\nnote nothing here",
              "Events:  2\nAdded:   0 ($0.00)\nRemoved: 1 (ghost)\nNotes:   1\nBalance: $0.00")],
            hints=["parse decides the tag from the first word, and builds a DIFFERENT shape for each kind.",
                   'A note\'s text is the rest of the line: p.slice(1).join(" ").',
                   "Remember what each amount was: a lookup table from desc to amount, filled on every add.",
                   "Removing something never added must not change the balance — `prices[e.desc] ?? 0` handles that.",
                   "Switch on e.kind so each arm can read only its own member's fields."]),
        example_io="Events:  3\nAdded:   1 ($3.25)\nRemoved: 1 (coffee)\nNotes:   1\nBalance: $0.00",
        rubric=["Event is a discriminated union with a literal `kind` on every member",
                "parse builds a different shape per kind — no optional fields",
                "A switch on the tag handles all three kinds",
                "Removing a description that was never added leaves the balance unchanged"],
        stretch=_ch("tscourse-w9-capstone-stretch", "Budget Buddy #9 (stretch)", "Medium",
                    "Add an exhaustiveness guard: a `default` branch whose `const _exhaustive: never = e;` would stop the build if a fourth event kind were added and left unhandled. Also print the last note's text as `Last note: <text>` (or `Last note: -` when there are none).",
                    _FS + 'type Event =\n'
                    '  | { kind: "add"; desc: string; amount: number }\n'
                    '  | { kind: "remove"; desc: string }\n'
                    '  | { kind: "note"; text: string };\n'
                    'function parse(line: string): Event {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  if (p[0] === "add") return { kind: "add", desc: p[1] ?? "", amount: Number(p[2]) };\n'
                    '  if (p[0] === "remove") return { kind: "remove", desc: p[1] ?? "" };\n'
                    '  return { kind: "note", text: p.slice(1).join(" ") };\n'
                    '}\n'
                    'const events: Event[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'let lastNote = "-";\n'
                    'for (const e of events) {\n'
                    '  switch (e.kind) {\n'
                    '    case "add":\n      break;\n'
                    '    case "remove":\n      break;\n'
                    '    case "note":\n      lastNote = e.text;\n      break;\n'
                    '    default: {\n'
                    '      const _exhaustive: never = e;\n      throw new Error(_exhaustive);\n'
                    '    }\n'
                    '  }\n'
                    '}\n'
                    'console.log(`Last note: ${lastNote}`);\n',
                    'default: {\n'
                    '      const _exhaustive: never = e;\n      throw new Error(_exhaustive);\n'
                    '    }',
                    [("add coffee 3.25\nnote reviewed the month", "Last note: reviewed the month"),
                     ("add book 12", "Last note: -"),
                     ("note first\nnote second", "Last note: second")],
                    hints=["The default branch receives whatever the cases did not cover.",
                           "Assign it to a name annotated never — that is the whole check.",
                           "Write default: { const _exhaustive: never = e; throw new Error(_exhaustive); }"]),
    ),
))
