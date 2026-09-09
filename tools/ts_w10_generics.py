# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 10 — generics.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 10 --------------------------------------------------------------
_WEEKS.append(_week(
    10, 3, _M3,
    "Generics",
    "Write one function or type that works over any type — without losing what the compiler knows about it.",
    """
Here is the problem generics exist to solve. You write a helper that returns the
first element of an array:

```ts
function firstNumber(a: number[]): number { return a[0]; }
```

Then you need it for strings. And for records. You have three choices:

1. **Copy it** for every element type — three functions that differ by one word.
2. **Use `any`** — one function, and every caller loses all type information.
3. **Make the type a parameter.**

The third is a **generic**:

```ts
function first<T>(a: T[]): T {
  if (a.length === 0) throw new Error("empty array");
  return a[0]!;
}

first([1, 2, 3]);        // T is number   -> returns number
first(["a", "b"]);       // T is string   -> returns string
```

`<T>` declares a **type parameter** — a placeholder filled in at each call site,
usually inferred so you never write it. One implementation, and the compiler
still knows that `first(["a"])` gives you a `string` with `.toUpperCase()` on it.

The mental model that makes generics click: **`T` is a variable whose value is a
type.** Everything else — constraints, `keyof`, generic interfaces — is that one
idea applied more sharply.

The runtime code in this week's drills is deliberately simple; the difficulty
lives in the signatures. Read them slowly, and lean on the quizzes.

⏱️ Budget about **ten hours**, spread over several sittings.
""",
    objectives=[
        "Say what problem generics solve, and why `any` is not the answer",
        "Write a generic function and let TypeScript infer its type argument",
        "Write generic helpers over arrays that preserve the element type",
        "Constrain a type parameter with extends so you can use its members",
        "Use keyof and indexed access to type a field-plucking helper",
        "Declare generic type aliases and interfaces, including a Result type",
        "Give a type parameter a default, and recognise when a generic is overkill",
        "Write a generic helper that takes a callback and changes the type on the way through",
        "Decide when a second type parameter earns its place — and when it does not",
        "Prove a type is right with Expect<Equal<…>>, and write a negative test with @ts-expect-error",
    ],
    why="Every array method, every Promise, every collection and every well-typed utility in the ecosystem is generic. Reading them fluently — and writing your own when a helper would otherwise need `any` — is the difference between using TypeScript and fighting it.",
    est_minutes=640,
    glossary=[
        _gloss("generic", "A function, type or interface parameterised by a type."),
        _gloss("type parameter", "The placeholder declared in angle brackets: <T>."),
        _gloss("type argument", "The concrete type supplied at a call site: first<string>(...)."),
        _gloss("inference (of type arguments)", "TypeScript working out T from the values you passed."),
        _gloss("T", "The conventional name for a type parameter. K, V, E, R are also common."),
        _gloss("Expect<T extends true>", "A type-level assertion: handing it false is a compile error."),
        _gloss("Equal<X, Y>", "True only when X and Y are the SAME type, not merely assignable."),
        _gloss("@ts-expect-error", "Asserts the NEXT line must fail to compile; an unused one is itself an error."),
        _gloss("constraint", "extends limits what a type parameter may be: <T extends { id: string }>."),
        _gloss("keyof T", "The union of T's key names as literal types."),
        _gloss("indexed access (T[K])", "The type of the property K on T."),
        _gloss("generic interface", "An interface with its own type parameters: interface Box<T>."),
        _gloss("default type parameter", "A fallback type argument: <T = string>."),
        _gloss("Array<T>", "The generic type behind T[]."),
        _gloss("Promise<T>", "A value of type T that arrives later (week 16)."),
        _gloss("Record<K, V>", "A built-in generic object type (week 12)."),
        _gloss("any", "Turns checking off. A generic keeps the information instead."),
        _gloss("unknown", "Accepts anything but must be narrowed. Safe, but loses the caller's type."),
        _gloss("higher-order generic", "A generic function that takes a function, letting the callback decide the output type."),
        _gloss("U", "By convention the second type parameter — usually what a callback returns."),
        _gloss("pinned parameter", "A callback return type fixed to string or number because the helper indexes or compares with it."),
        _gloss("Array<T>", "The same type as T[], written in the generic form."),
    ],
    cheatsheet="""
```ts
// ---- the basic shape --------------------------------------------------
function first<T>(a: T[]): T {
  if (a.length === 0) throw new Error("empty array");
  return a[0]!;
}
first([1, 2]);            // T inferred as number
first<string>(["a"]);     // T given explicitly (rarely needed)

function identity<T>(x: T): T { return x; }

// ---- several parameters -------------------------------------------------
function pair<A, B>(a: A, b: B): [A, B] { return [a, b]; }
function swap<A, B>(p: [A, B]): [B, A] { return [p[1], p[0]]; }

// ---- constraints ---------------------------------------------------------
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;      // .length is now allowed
}
longest("abc", "de");        // ✅ strings have length
longest([1], [2, 3]);        // ✅ arrays do too
longest(1, 2);               // ❌ numbers do not

// ---- keyof & indexed access ------------------------------------------------
type User = { id: string; age: number };
type K = keyof User;              // "id" | "age"
type A = User["age"];             // number

function pluck<T, K extends keyof T>(o: T, k: K): T[K] {
  return o[k];
}
pluck({ id: "u1", age: 3 }, "age");   // returns number, not any

// ---- generic types ----------------------------------------------------------
interface Box<T> { value: T }
type Pair<A, B> = { left: A; right: B };
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

// ---- defaults ----------------------------------------------------------------
interface Options<T = string> { items: T[] }
const o: Options = { items: ["a"] };      // T defaults to string
```
""",
    self_check=[
        "Can you explain why `any` is a bad substitute for a generic?",
        "Can you write a function that returns the last element of an array of any type?",
        "Can you say what TypeScript infers T to be in `first([1, 2])`?",
        "Can you constrain a type parameter so you may read `.length` off it?",
        "Can you say what `keyof User` is, for a User with id and age?",
        "Can you declare a generic interface and use it at two different types?",
        "Can you name a case where a generic would be pointless?",
        "Can you write mapAll, groupBy and maxBy from scratch, with the right type parameters?",
        "Can you say where each type parameter is inferred from at a call site?",
        "Can you write an assertion that fails to COMPILE when a type is wrong?",
        "Can you say why `X extends Y ? true : false` is not the same check as `Equal<X, Y>`?",
    ],
    review=[
        _q("`<T>` in a function signature declares…",
           ["a value parameter", "a type parameter", "an array", "a constraint"], 1,
           "A placeholder for a type, filled at the call site."),
        _q("In `first([1, 2, 3])` where `first<T>(a: T[]): T`, T is…",
           ["any", "number", "number[]", "unknown"], 1,
           "Inferred from the argument's element type."),
        _q("Why not just use `any` instead of a generic?",
           ["any is slower", "any discards the caller's type, so the RESULT is unchecked too",
            "any is deprecated", "no difference"], 1,
           "The generic remembers what came in and hands the same type back."),
        _q("`function f<T extends { length: number }>(x: T)` lets you…",
           ["pass anything", "read x.length inside f", "return a number", "skip inference"], 1,
           "A constraint is what makes a member usable."),
        _q("`keyof { id: string; age: number }` is…",
           ["string", '"id" | "age"', "[string, number]", "never"], 1,
           "A union of the key names as literal types."),
        _q("`User[\"age\"]` where age is a number is…",
           ['"age"', "number", "string", "never"], 1,
           "Indexed access gives the property's TYPE."),
        _q("`interface Box<T> { value: T }` used as `Box<string>` has value of type…",
           ["T", "string", "any", "unknown"], 1,
           "The argument replaces the parameter."),
        _q("`<T = string>` means…",
           ["T must be string", "T defaults to string when not supplied", "T is a value",
            "T is constrained"], 1,
           "A default type argument."),
        _q("A generic with a type parameter used exactly ONCE in the signature is usually…",
           ["ideal", "a sign it should just be a plain parameter type", "faster",
            "required"], 1,
           "A parameter that relates nothing to nothing buys you nothing."),
        _q("`function f<T>(x: T): T` called as `f(\"a\")` returns a value of type…",
           ["string", '"a"', "any", "unknown"], 0,
           "Inference widens the literal to string here."),
        _q("In `mapAll<T, U>(xs: T[], f: (x: T) => U): U[]`, `U` is inferred from…",
           ["the array", "what the callback returns", "the call site only", "the return statement"], 1,
           "The callback decides the output element type."),
        _q("`groupBy<T>(xs: T[], key: (x: T) => string)` pins the callback's return to string because…",
           ["strings are faster", "the helper uses it as an object key", "T must be a string", "generics demand it"], 1,
           "Object keys are strings, so that position cannot stay open."),
        _q("A type parameter that appears in exactly one position…",
           ["is required", "relates nothing, and can usually be a concrete type",
            "must be constrained", "is inferred last"], 1,
           "A type parameter earns its keep by tying two positions together."),
    ],
    milestone="Budget Buddy's helpers now work over any record type at all, and its parser hands back a typed Result — the same shapes real libraries expose. Month 3 is half done.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w10-why", "Why generics exist",
            "The gap between duplication and any.",
            """
Three ways to write "give me the first element".

**Duplicate per type** — correct, and unmaintainable:

```ts
function firstNumber(a: number[]): number { return a[0]; }
function firstString(a: string[]): string { return a[0]; }
function firstUser(a: User[]): User { return a[0]; }
```

**Use `any`** — one function, and the type information is destroyed:

```ts
function first(a: any[]): any { return a[0]; }

const s = first(["a", "b"]);
s.toUpperCase();     // no error... and no checking either
s.toFixed(2);        // also no error — and a crash at runtime
```

`any` doesn't just lose information at the boundary; it *poisons everything
downstream*. The caller got a value the compiler will never question again.

**Make the type a parameter:**

```ts
function first<T>(a: T[]): T {
  if (a.length === 0) throw new Error("empty array");
  return a[0]!;
}

const s = first(["a", "b"]);   // s: string
s.toUpperCase();               // ✅
s.toFixed(2);                  // ❌ caught
```

One implementation, full checking at every call site.

**What `<T>` means.** Read `function first<T>(a: T[]): T` as: *"for any type T,
this takes an array of T and returns a T."* The signature states a
**relationship** — the output type is tied to the input type — and that
relationship is exactly what `any` throws away.

**`unknown` is safer than `any` but still wrong here:**

```ts
function first(a: unknown[]): unknown { return a[0]; }
const s = first(["a"]);
s.toUpperCase();      // ❌ must narrow first — but you already KNEW it was a string
```

`unknown` is honest, and it still makes the caller re-establish something the
function could have preserved. Use `unknown` for values whose type you genuinely
don't know (parsed JSON, caught errors). Use a generic when the type is *known
to the caller* and you're just passing it through.

**The test for whether you need a generic:** does a type appear in **more than
one place** in the signature — two parameters, or a parameter and the return? If
yes, a generic ties them together. If a type parameter appears only once, it is
doing nothing.

> ⚠️ **Common mistakes:** reaching for `any` when a generic was two characters
> away; adding type parameters that appear only once; and thinking `<T>` has a
> runtime cost — it is erased like every other type.
""",
            warmup=[
                _q("`function first(a: any[]): any` — what does the caller get?",
                   ["a checked value", "a value the compiler will never question again",
                    "an error", "unknown"], 1,
                   "any propagates outward."),
                _q("`function first<T>(a: T[]): T` called with `[\"a\"]` returns…",
                   ["any", "string", "unknown", "T"], 1, "T is inferred as string."),
                _q("The point of `<T>` in a signature is to…",
                   ["speed things up", "tie the output type to the input type",
                    "allow any value", "avoid annotations"], 1,
                   "It states a relationship."),
                _q("A type parameter that appears only ONCE in the signature is…",
                   ["ideal", "pointless — it relates nothing", "required", "faster"], 1,
                   "Generics exist to connect two places."),
            ],
            exercises=[
                _ex("tscourse-w10-wh-1", "The identity function",
                    "Return the argument unchanged.",
                    'function identity<T>(x: T): T {\n  return x;\n}\n'
                    'console.log(identity("hello"));\nconsole.log(identity(42));\n',
                    'return x;', [("", "hello\n42")],
                    hints=["The simplest generic there is — hand back what you were given."]),
                _ex("tscourse-w10-wh-2", "First element, generically",
                    "Return the first element of the array.",
                    'function first<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[0]!;\n}\n'
                    'console.log(first([1, 2, 3]));\nconsole.log(first(["a", "b"]));\n',
                    'return a[0]!;', [("", "1\na")],
                    hints=["Index 0, whatever the element type is.",
                           "The guard above is what earns the ! — without it, ! would be a lie."]),
                _ex("tscourse-w10-wh-3", "Declare the parameter",
                    "Add the type parameter so this works for any element type.",
                    'function last<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[a.length - 1]!;\n}\n'
                    'console.log(last([1, 2, 3]));\nconsole.log(last(["a", "b"]));\n',
                    '<T>', [("", "3\nb")],
                    hints=["Angle brackets go right after the function name.",
                           "Write <T>."]),
                _ex("tscourse-w10-wh-4", "Use the preserved type",
                    "The result is a string, so its own methods are available. Uppercase it.",
                    'function first<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[0]!;\n}\n'
                    'const s = first(["hello", "there"]);\nconsole.log(s.toUpperCase());\n',
                    's.toUpperCase()', [("", "HELLO")],
                    hints=["Because T was inferred as string, string methods are allowed.",
                           "Write s.toUpperCase()."]),
                _ex("tscourse-w10-wh-5", "Generic over records",
                    "The same helper works on an array of objects. Print the first record's desc.",
                    'function first<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[0]!;\n}\n'
                    'const rows = [{ desc: "coffee" }, { desc: "book" }];\n'
                    'console.log(first(rows).desc);\n',
                    'first(rows).desc', [("", "coffee")],
                    hints=["T is inferred as the record type, so .desc is available.",
                           "Write first(rows).desc."],
                    difficulty="Medium"),
                _fix("tscourse-w10-wh-fix1", "Fix the any-shaped helper",
                     "This uses `any`, so a genuine mistake goes unnoticed and it crashes at runtime. Make it generic and call the right method.",
                     'function first(a: any[]): any {\n  return a[0];\n}\n'
                     'const s = first(["hello"]);\nconsole.log(s.toFixed(2));\n',
                     'function first<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[0]!;\n}\n'
                     'const s = first(["hello"]);\nconsole.log(s.toUpperCase());\n',
                     [("", "HELLO")],
                     hints=["With any, calling toFixed on a string raised no complaint at all.",
                            "Parameterise the type, then call a method the value actually has."],
                     difficulty="Medium"),
                _fix("tscourse-w10-why-fix2", "Fix the off-by-one helper",
                     "The generic signature is right, but `first` hands back the second element. It should print 10 then a.",
                     'function first<T>(xs: T[]): T {\n'
                     '  if (xs.length === 0) throw new Error("empty array");\n'
                     '  return xs[1]!;\n}\n'
                     'console.log(first([10, 20, 30]));\n'
                     'console.log(first(["a", "b"]));\n',
                     'function first<T>(xs: T[]): T {\n'
                     '  if (xs.length === 0) throw new Error("empty array");\n'
                     '  return xs[0]!;\n}\n'
                     'console.log(first([10, 20, 30]));\n'
                     'console.log(first(["a", "b"]));\n',
                     [("", "10\na")],
                     hints=["Generics make the types line up; they cannot make the logic correct.",
                            "Array positions start at 0."]),
            ],
            quiz=[
                _q("`unknown[]` instead of a generic means the caller must…",
                   ["nothing extra", "narrow a type it already knew", "cast to any",
                    "use a loop"], 1,
                   "Safe, but it discards information the function could have preserved."),
                _q("Generics at runtime…",
                   ["add a lookup", "are erased like all types", "create classes",
                    "slow calls down"], 1,
                   "There is no runtime representation of T at all."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w10-functions", "Generic functions & inference",
            "Declaring type parameters, and letting them be worked out.",
            """
The type parameter list goes between the name and the value parameters:

```ts
function wrap<T>(x: T): T[] {
  return [x];
}
```

**You almost never write the type argument.** TypeScript infers it from what you
pass:

```ts
wrap("a");        // T = string   -> string[]
wrap(3);          // T = number   -> number[]
wrap<boolean>(true);   // explicit — legal, but usually noise
```

Supply it explicitly only when inference can't help — typically when the type
appears nowhere in the arguments:

```ts
function makeEmpty<T>(): T[] { return []; }
const xs = makeEmpty<string>();     // nothing to infer from, so say it
```

**Several type parameters** are independent:

```ts
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b];
}
pair("x", 1);      // [string, number]
```

Conventional names: `T` for a single one; `A`/`B` or `T`/`U` for two; `K` for a
key, `V` for a value, `E` for an error, `R` for a result. Use a descriptive name
when it helps (`<TRow>`), but short names are the norm and nobody minds.

**Inference follows the values, and widens literals:**

```ts
function id<T>(x: T): T { return x; }
const a = id("hello");        // string, not "hello"
const b = id({ n: 1 });       // { n: number }
```

**Generic arrow functions** exist too, and are used constantly for callbacks:

```ts
const wrap = <T>(x: T): T[] => [x];
```

(In `.tsx` files that clashes with JSX and needs `<T,>`; in a plain `.ts` file
it's fine.)

**A generic can call another generic**, passing its own parameter through:

```ts
function firstOrEmpty<T>(a: T[]): T[] {
  return a.length > 0 ? wrap(first(a)) : [];
}
```

That's the payoff: the relationships compose, and the compiler tracks them all
the way down.

> ⚠️ **Common mistakes:** writing explicit type arguments everywhere (let
> inference work); declaring `<T>` and then never using it; and expecting `T` to
> be available at runtime — you cannot write `if (T === string)`.
""",
            warmup=[
                _q("`function wrap<T>(x: T): T[]` called as `wrap(3)` returns type…",
                   ["number", "number[]", "T[]", "any[]"], 1, "T is number, so T[] is number[]."),
                _q("When must you write the type argument explicitly?",
                   ["always", "when nothing in the arguments determines it", "never",
                    "for strings"], 1,
                   "e.g. a function taking no parameters."),
                _q("`const a = id(\"hello\")` where `id<T>(x: T): T` gives a…",
                   ['"hello"', "string", "any", "never"], 1, "Inference widens the literal."),
                _q("Can you test `T` at runtime?",
                   ["yes, with typeof T", "no — type parameters are erased", "yes, with instanceof",
                    "only for classes"], 1,
                   "There is nothing left of T when the program runs."),
            ],
            exercises=[
                _predict("tscourse-w10-fn-p1", "What inference chose for T",
                         'function first<T>(xs: T[]): T | undefined {\n'
                         '  return xs[0];\n'
                         '}\n'
                         'const got = first([1, 2, 3]);\n',
                         "got", "number | undefined",
                         why="Nobody wrote `first<…>` — work out what T became, then what "
                             "the return type says on top of it.",
                         hints=["The argument is a number[], so T was solved as number.",
                                "Now substitute that into the declared return type `T | undefined`.",
                                "Write number | undefined."],
                         difficulty="Medium"),
                _ex("tscourse-w10-fn-1", "Wrap a value",
                    "Return a one-element array holding the argument.",
                    'function wrap<T>(x: T): T[] {\n  return [x];\n}\n'
                    'console.log(wrap("a").length);\nconsole.log(wrap(3)[0]);\n',
                    'return [x];', [("", "1\n3")],
                    hints=["An array literal containing just the parameter."]),
                _ex("tscourse-w10-fn-2", "Two type parameters",
                    "Return the two arguments as a tuple.",
                    'function pair<A, B>(a: A, b: B): [A, B] {\n  return [a, b];\n}\n'
                    'const p = pair("x", 1);\nconsole.log(`${p[0]}${p[1]}`);\n',
                    'return [a, b];', [("", "x1")],
                    hints=["The tuple holds them in order."]),
                _ex("tscourse-w10-fn-3", "Declare two parameters",
                    "Add the type parameter list so both arguments keep their own types.",
                    'function swap<A, B>(a: A, b: B): [B, A] {\n  return [b, a];\n}\n'
                    'const s = swap("x", 1);\nconsole.log(`${s[0]}${s[1]}`);\n',
                    '<A, B>', [("", "1x")],
                    hints=["Two names, separated by a comma, in angle brackets.",
                           "Write <A, B>."],
                    difficulty="Medium"),
                _ex("tscourse-w10-fn-4", "Swap the tuple",
                    "Return the pair with its two slots exchanged.",
                    'function swap<A, B>(p: [A, B]): [B, A] {\n  return [p[1], p[0]];\n}\n'
                    'const s = swap(["x", 1]);\nconsole.log(`${s[0]}${s[1]}`);\n',
                    'return [p[1], p[0]];', [("", "1x")],
                    hints=["Slot 1 first, then slot 0."],
                    difficulty="Medium"),
                _ex("tscourse-w10-fn-5", "Compose two generics",
                    "Return a one-element array holding the first element, or an empty array.",
                    'function first<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[0]!;\n}\n'
                    'function wrap<T>(x: T): T[] {\n  return [x];\n}\n'
                    'function firstOrEmpty<T>(a: T[]): T[] {\n'
                    '  return a.length > 0 ? wrap(first(a)) : [];\n}\n'
                    'console.log(firstOrEmpty([5, 6]).length);\nconsole.log(firstOrEmpty([]).length);\n',
                    'a.length > 0 ? wrap(first(a)) : []',
                    [("", "1\n0")],
                    hints=["Guard the empty case, then pass T straight through both helpers.",
                           "Write a.length > 0 ? wrap(first(a)) : []."],
                    difficulty="Medium"),
                _fix("tscourse-w10-fn-fix1", "Fix the unused parameter",
                     "The helper declares a type parameter it never uses, and hard-codes a string. Make it actually generic so the number is returned unchanged.",
                     'function identity<T>(x: string): string {\n  return x;\n}\n'
                     'console.log(identity("a"));\n',
                     'function identity<T>(x: T): T {\n  return x;\n}\n'
                     'console.log(identity("a"));\nconsole.log(identity(42));\n',
                     [("", "a\n42")],
                     hints=["<T> is declared but the signature still says string everywhere.",
                            "Use T for the parameter and the return, then it works for numbers too."],
                     difficulty="Medium"),
                _fix("tscourse-w10-fn-fix2", "Fix the swap that doesn't swap",
                     "`swap` promises `[B, A]` but hands the pair back untouched — and a double assertion hid it. It should print `1,a`.",
                     'function swap<A, B>(pair: [A, B]): [B, A] {\n'
                     '  return [pair[0], pair[1]] as unknown as [B, A];\n}\n'
                     'console.log(swap(["a", 1]).join(","));\n',
                     'function swap<A, B>(pair: [A, B]): [B, A] {\n'
                     '  return [pair[1], pair[0]];\n}\n'
                     'console.log(swap(["a", 1]).join(","));\n',
                     [("", "1,a")],
                     hints=["Without the assertion, the compiler would have rejected this immediately.",
                            "Return the second slot first: [pair[1], pair[0]]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Explicit type arguments are…",
                   ["always required", "usually unnecessary — inference handles it",
                    "never allowed", "faster"], 1,
                   "Write them only when inference has nothing to go on."),
                _q("`<A, B>` declares…",
                   ["one parameter", "two independent type parameters", "a constraint",
                    "a tuple"], 1,
                   "Each is inferred separately."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w10-arrays", "Generic helpers over arrays",
            "Where generics earn their keep day to day.",
            """
Array helpers are the natural home of generics, because the element type must
survive the trip.

```ts
function last<T>(a: T[]): T            { return a[a.length - 1]; }
function head<T>(a: T[], n: number): T[] { return a.slice(0, n); }
function reversed<T>(a: T[]): T[]      { return [...a].reverse(); }
```

Each says something the compiler can use: `last` of a `string[]` is a `string`;
`reversed` of a `User[]` is a `User[]`.

**Returning "maybe nothing"** needs a union — and this is why the built-in
`find` returns `T | undefined`:

```ts
function firstOr<T>(a: T[], fallback: T): T {
  return a.length > 0 ? a[0]! : fallback;
}
```

Note the `fallback: T`. That's the whole idea again: the fallback must be the
*same* type as the elements, and the signature enforces it.
`firstOr([1, 2], "none")` is a compile error, which is what you want.

**Combining two arrays:**

```ts
function concat<T>(a: T[], b: T[]): T[] {
  return [...a, ...b];
}
```

Both parameters use the *same* `T`, so mixing element types is rejected. If you
genuinely want to allow that, say so — `concat<A, B>(a: A[], b: B[]): (A | B)[]`.
The signature is the design decision.

**Deduplicating:**

```ts
function unique<T>(a: T[]): T[] {
  const out: T[] = [];
  for (const x of a) {
    if (!out.includes(x)) out.push(x);
  }
  return out;
}
```

`out: T[]` needs its annotation for the reason you learned in week 8 — an empty
literal has nothing to infer from.

**Reading the built-ins.** Everything you used in week 6 is generic. Hover over
`map` and you'll see roughly:

```ts
map<U>(fn: (value: T, index: number) => U): U[]
```

`T` is the array's element type; `U` is whatever the callback returns. That is
why `[1,2,3].map((x) => String(x))` is `string[]` and not `number[]` — the
signature *derives* the result type from your callback. Once generics read
easily, the standard library stops being magic.

> ⚠️ **Common mistakes:** forgetting the annotation on an accumulator array;
> using one `T` where you meant two independent ones (or the reverse); and
> writing a helper that returns `T` when it can return `undefined` for an empty
> array.
""",
            warmup=[
                _q("`function last<T>(a: T[]): T` on a `string[]` returns…",
                   ["T", "string", "any", "string[]"], 1, "T is inferred as string."),
                _q("`function concat<T>(a: T[], b: T[]): T[]` called with a number[] and a string[]…",
                   ["works, giving (number|string)[]", "is a compile error", "returns any[]",
                    "throws"], 1,
                   "Both parameters share one T, so they must agree."),
                _q("In `map<U>(fn: (v: T) => U): U[]`, U is…",
                   ["the element type", "whatever the callback returns", "always string",
                    "the index"], 1,
                   "Which is why map can change the array's type."),
                _q("`const out: T[] = [];` needs its annotation because…",
                   ["T is special", "an empty literal gives inference nothing", "it is const",
                    "it does not"], 1,
                   "Same rule as week 8."),
            ],
            exercises=[
                _ex("tscourse-w10-ar-1", "Last element",
                    "Return the final element, whatever the element type.",
                    'function last<T>(a: T[]): T {\n  if (a.length === 0) throw new Error("empty array");\n  return a[a.length - 1]!;\n}\n'
                    'console.log(last([1, 2, 3]));\nconsole.log(last(["a", "b"]));\n',
                    'return a[a.length - 1]!;', [("", "3\nb")],
                    hints=["The last index is one less than the length.",
                           "The guard above is what earns the ! — without it, ! would be a lie."]),
                _ex("tscourse-w10-ar-2", "Reverse a copy",
                    "Return a reversed copy, leaving the original alone.",
                    'function reversed<T>(a: T[]): T[] {\n  return [...a].reverse();\n}\n'
                    'const xs = [1, 2, 3];\nconsole.log(reversed(xs).join(""));\nconsole.log(xs.join(""));\n',
                    'return [...a].reverse();', [("", "321\n123")],
                    hints=["reverse mutates, so spread into a copy first.",
                           "Write return [...a].reverse();"],
                    difficulty="Medium"),
                _ex("tscourse-w10-ar-3", "A typed fallback",
                    "Return the first element, or the fallback when the array is empty.",
                    'function firstOr<T>(a: T[], fallback: T): T {\n'
                    '  return a.length > 0 ? a[0]! : fallback;\n}\n'
                    'console.log(firstOr([5, 6], 0));\nconsole.log(firstOr<number>([], 0));\n',
                    'a.length > 0 ? a[0]! : fallback', [("", "5\n0")],
                    hints=["Guard the empty case and hand back the fallback.",
                           "Write a.length > 0 ? a[0]! : fallback — the length check is what makes the ! true."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ar-4", "Concatenate",
                    "Return the two arrays joined into one.",
                    'function concat<T>(a: T[], b: T[]): T[] {\n  return [...a, ...b];\n}\n'
                    'console.log(concat([1, 2], [3]).join(""));\n',
                    'return [...a, ...b];', [("", "123")],
                    hints=["Spread both into a single new array."]),
                _ex("tscourse-w10-ar-5", "Deduplicate",
                    "Keep only the first occurrence of each element.",
                    _WORDS + 'function unique<T>(a: T[]): T[] {\n'
                    '  const out: T[] = [];\n'
                    '  for (const x of a) {\n    if (!out.includes(x)) {\n      out.push(x);\n    }\n  }\n'
                    '  return out;\n}\n'
                    'console.log(unique(words).join(" "));\n',
                    'if (!out.includes(x)) {\n      out.push(x);\n    }',
                    [("a b a c a", "a b c"), ("x y", "x y")],
                    hints=["Add an element only when it is not already collected.",
                           "Write if (!out.includes(x)) { out.push(x); }"],
                    difficulty="Medium"),
                _ex("tscourse-w10-ar-6", "Generic over records",
                    "The same unique helper works on records compared by reference. Print how many distinct objects remain.",
                    'function unique<T>(a: T[]): T[] {\n'
                    '  const out: T[] = [];\n'
                    '  for (const x of a) {\n    if (!out.includes(x)) {\n      out.push(x);\n    }\n  }\n'
                    '  return out;\n}\n'
                    'const r = { id: 1 };\nconsole.log(unique([r, r, { id: 1 }]).length);\n',
                    'unique([r, r, { id: 1 }]).length', [("", "2")],
                    hints=["includes compares objects by identity, so the two separate literals are different.",
                           "Write unique([r, r, { id: 1 }]).length."],
                    difficulty="Medium"),
                _fix("tscourse-w10-ar-fix1", "Fix the mutating reverse",
                     "The original array should stay `123` but comes back reversed. Fix it.",
                     'function reversed<T>(a: T[]): T[] {\n  return a.reverse();\n}\n'
                     'const xs = [1, 2, 3];\nconsole.log(reversed(xs).join(""));\nconsole.log(xs.join(""));\n',
                     'function reversed<T>(a: T[]): T[] {\n  return [...a].reverse();\n}\n'
                     'const xs = [1, 2, 3];\nconsole.log(reversed(xs).join(""));\nconsole.log(xs.join(""));\n',
                     [("", "321\n123")],
                     hints=["reverse reorders the caller's own array.",
                            "Copy it first with a spread."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Using the same `T` for two parameters means…",
                   ["they may differ", "they must be the same type", "one is inferred",
                    "nothing"], 1,
                   "Sharing a parameter is how you require agreement."),
                _q("Why does `[1,2].map((x) => String(x))` give `string[]`?",
                   ["map always returns strings", "map's signature derives the result type from the callback",
                    "a cast", "coincidence"], 1,
                   "The U in map<U> comes from your callback's return type."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w10-constraints", "Constraints with extends",
            "Requiring a type parameter to have something.",
            """
An unconstrained `T` could be *anything*, so you may not touch it:

```ts
function longest<T>(a: T, b: T): T {
  return a.length >= b.length ? a : b;   // ❌ Property 'length' does not exist on type 'T'
}
```

The compiler is right: `T` might be `number`. **Constrain it** with `extends`:

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;   // ✅
}

longest("abc", "de");        // ✅ strings have length
longest([1], [2, 3]);        // ✅ arrays too
longest(1, 2);               // ❌ numbers do not
```

Read `T extends { length: number }` as *"T, whatever it is, must at least have a
numeric length"*. Inside the function you may use exactly what the constraint
guarantees, and nothing more.

**`extends` here means "is assignable to", not inheritance.** Any type with the
required shape qualifies — structural typing, from week 8.

**Why not just take `{ length: number }` as the parameter type?**

```ts
function longestBad(a: { length: number }, b: { length: number }): { length: number }
```

That works, but the return type has been flattened — the caller gets back
something with only `length`, having passed in strings. The generic **preserves
the actual type**:

```ts
longest("abc", "de").toUpperCase();      // ✅ still a string
longestBad("abc", "de").toUpperCase();   // ❌ information lost
```

This is the clearest demonstration of what generics buy you over a plain
supertype parameter.

**Common constraints:**

```ts
<T extends string>                      // some kind of string
<T extends { id: string }>              // anything with an id
<T extends unknown[]>                   // any array
<T extends object>                      // any non-primitive
```

**Constraints compose with defaults and with `keyof`** (next lesson), and they
are what make a generic *usable* rather than merely general.

> ⚠️ **Common mistakes:** reading `extends` as class inheritance; constraining
> more tightly than the body needs (which rejects valid callers); and forgetting
> that inside the function you get only what the constraint promised, never the
> caller's extra fields.
""",
            warmup=[
                _q("`function f<T>(x: T) { return x.length; }` is…",
                   ["fine", "an error — T might not have length", "an error at runtime",
                    "inferred"], 1,
                   "An unconstrained T guarantees nothing."),
                _q("`<T extends { length: number }>` allows you to pass…",
                   ["only strings", "anything with a numeric length", "only arrays", "numbers"], 1,
                   "Structural, not nominal."),
                _q("`extends` in a constraint means…",
                   ["class inheritance", "is assignable to", "equals", "implements"], 1,
                   "Any type with the required shape qualifies."),
                _q("Taking `{length: number}` directly instead of a constrained generic loses…",
                   ["nothing", "the caller's actual type in the return", "speed",
                    "the constraint"], 1,
                   "The return type would be flattened."),
            ],
            exercises=[
                _diagnose("tscourse-w10-cn-diag1", "The unconstrained type parameter",
                          "TS2339: Property 'length' does not exist on type 'T'.",
                          'function longer<T>(a: T, b: T): T {\n'
                          '  return a.length >= b.length ? a : b;\n}\n'
                          'console.log(longer("abc", "de"));\n',
                          'function longer<T extends { length: number }>(a: T, b: T): T {\n'
                          '  return a.length >= b.length ? a : b;\n}\n'
                          'console.log(longer("abc", "de"));\n',
                          [("", "abc")],
                          ask="`T` is every type, and most types have no `.length`. Say what "
                              "little you need from it — without giving up the fact that what "
                              "goes in comes back out.",
                          hints=["The error is not that the call is wrong; it is that the body "
                                 "assumes something the signature never promised.",
                                 "`extends` is how a type parameter states its minimum shape.",
                                 "Write <T extends { length: number }> — not <T extends string>, "
                                 "which would throw away the generic."],
                          difficulty="Medium"),
                _ex("tscourse-w10-cn-1", "Constrain to length",
                    "Add the constraint so `.length` may be read inside the function.",
                    'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                    '  return a.length >= b.length ? a : b;\n}\n'
                    'console.log(longest("abc", "de"));\n',
                    'extends { length: number }', [("", "abc")],
                    hints=["State the minimum shape T must have.",
                           "Write extends { length: number }."],
                    difficulty="Medium"),
                _ex("tscourse-w10-cn-2", "Use the preserved type",
                    "The result is still a string, so uppercase it.",
                    'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                    '  return a.length >= b.length ? a : b;\n}\n'
                    'console.log(longest("abc", "de").toUpperCase());\n',
                    'longest("abc", "de").toUpperCase()', [("", "ABC")],
                    hints=["A generic hands back the caller's own type, not the constraint.",
                           'Write longest("abc", "de").toUpperCase().'],
                    difficulty="Medium"),
                _ex("tscourse-w10-cn-3", "Anything with an id",
                    "Return the record's id.",
                    'function idOf<T extends { id: string }>(x: T): string {\n'
                    '  return x.id;\n}\n'
                    'console.log(idOf({ id: "u1", age: 3 }));\n',
                    'return x.id;', [("", "u1")],
                    hints=["The constraint guarantees the id field exists."]),
                _ex("tscourse-w10-cn-4", "Constrain to arrays",
                    "Return how many elements the array-like argument holds.",
                    'function count<T extends unknown[]>(a: T): number {\n'
                    '  return a.length;\n}\n'
                    'console.log(count([1, 2, 3]));\nconsole.log(count(["a"]));\n',
                    'extends unknown[]', [("", "3\n1")],
                    hints=["Any array at all satisfies this.",
                           "Write extends unknown[]."],
                    difficulty="Medium"),
                _ex("tscourse-w10-cn-5", "Longest of records",
                    "The constraint is structural, so a record with a length field qualifies. Print the winner's name.",
                    'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                    '  return a.length >= b.length ? a : b;\n}\n'
                    'const big = { name: "big", length: 10 };\n'
                    'const small = { name: "small", length: 2 };\n'
                    'console.log(longest(big, small).name);\n',
                    'longest(big, small).name', [("", "big")],
                    hints=["The generic preserved the record type, so .name survives.",
                           "Write longest(big, small).name."],
                    difficulty="Medium"),
                _fix("tscourse-w10-cn-fix1", "Fix the flattened return",
                     "Taking the constraint directly as the parameter type loses the string, so `.toUpperCase()` is unavailable and this prints the wrong thing. Make it generic.",
                     'function longest(a: { length: number }, b: { length: number }): { length: number } {\n'
                     '  return a.length >= b.length ? a : b;\n}\n'
                     'console.log(longest("abc", "de").length);\n',
                     'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                     '  return a.length >= b.length ? a : b;\n}\n'
                     'console.log(longest("abc", "de").toUpperCase());\n',
                     [("", "ABC")],
                     hints=["The caller passed strings but got back something with only a length.",
                            "Parameterise with T constrained by the shape, then the string survives."],
                     difficulty="Medium"),
                _fix("tscourse-w10-con-fix2", "Fix the reversed comparison",
                     "`longest` is constrained to things that have a length, but it keeps returning the shorter one. It should print `there` then 3.",
                     'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                     '  return a.length < b.length ? a : b;\n}\n'
                     'console.log(longest("hi", "there"));\n'
                     'console.log(longest([1, 2, 3], [1]).length);\n',
                     'function longest<T extends { length: number }>(a: T, b: T): T {\n'
                     '  return a.length > b.length ? a : b;\n}\n'
                     'console.log(longest("hi", "there"));\n'
                     'console.log(longest([1, 2, 3], [1]).length);\n',
                     [("", "there\n3")],
                     hints=["The constraint guarantees `.length` exists; it says nothing about which way you compare.",
                            "Keep a when its length is greater."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Inside a constrained generic you may use…",
                   ["everything the caller passed", "exactly what the constraint guarantees",
                    "nothing", "only length"], 1,
                   "The body is checked against the constraint, not against any particular caller."),
                _q("A constraint that is tighter than the body needs…",
                   ["is safer", "rejects valid callers for no reason", "is faster",
                    "is required"], 1,
                   "Ask for the minimum you actually use."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w10-keyof", "keyof & indexed access",
            "Types computed from other types.",
            """
`keyof T` is the union of `T`'s key names, as literal types:

```ts
type User = { id: string; age: number };
type K = keyof User;        // "id" | "age"
```

**Indexed access** `T[K]` is the *type of that property*:

```ts
type A = User["age"];              // number
type Either = User[keyof User];    // string | number
```

Note `User["age"]` uses a **type** in the brackets, not a value — it looks like
property access but happens entirely at compile time.

Together they type the single most useful generic helper there is:

```ts
function pluck<T, K extends keyof T>(o: T, k: K): T[K] {
  return o[k];
}

const u = { id: "u1", age: 3 };
pluck(u, "age");      // number   ✅
pluck(u, "id");       // string   ✅
pluck(u, "nope");     // ❌ not assignable to "id" | "age"
```

Read the signature slowly, because it is the pattern:

- `T` — the object's type.
- `K extends keyof T` — the key must be one of `T`'s actual keys.
- `T[K]` — the return is the type of *that specific* property.

So a single function returns a `string` for one key and a `number` for another,
and typos are compile errors. Without generics this would be `any`.

**Sorting by a key** is the everyday application:

```ts
function sortBy<T, K extends keyof T>(rows: T[], key: K): T[] {
  return [...rows].sort((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));
}
sortBy(people, "age");      // ✅
sortBy(people, "aeg");      // ❌ caught
```

**`keyof` on an index signature** behaves as you'd expect:

```ts
type Table = { [k: string]: number };
type TK = keyof Table;      // string | number
```

**Where you'll see this:** `Pick`, `Omit` and `Record` (week 12) are all built
from `keyof` and indexed access. Learning to read it now makes that week easy.

> ⚠️ **Common mistakes:** writing `keyof T` where you meant `T[keyof T]` (keys
> versus value types); forgetting the `extends keyof T` constraint, which makes
> `o[k]` an error; and expecting `keyof` to work at runtime — use
> `Object.keys(o)` for that, which returns `string[]`.
""",
            warmup=[
                _q('`keyof { id: string; age: number }` is…',
                   ["string", '"id" | "age"', "string | number", "never"], 1,
                   "The key NAMES as literal types."),
                _q('`{ id: string; age: number }["age"]` is…',
                   ['"age"', "number", "string", "never"], 1,
                   "Indexed access gives the property's type."),
                _q("In `pluck<T, K extends keyof T>(o: T, k: K): T[K]`, the return type is…",
                   ["always any", "the type of the specific property named by k", "T", "K"], 1,
                   "Which is why it returns string for one key and number for another."),
                _q("Does `keyof` exist at runtime?",
                   ["yes", "no — use Object.keys for that", "only for classes",
                    "only for arrays"], 1,
                   "It is a compile-time operator."),
            ],
            exercises=[
                _ex("tscourse-w10-ke-1", "Pluck a field",
                    "Return the property named by the key.",
                    'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n'
                    '  return o[k];\n}\n'
                    'const u = { id: "u1", age: 3 };\n'
                    'console.log(pluck(u, "id"));\nconsole.log(pluck(u, "age"));\n',
                    'return o[k];', [("", "u1\n3")],
                    hints=["Bracket access with the key parameter."]),
                _ex("tscourse-w10-ke-2", "Constrain the key",
                    "Add the constraint so only real keys of T are accepted.",
                    'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n'
                    '  return o[k];\n}\n'
                    'console.log(pluck({ id: "u1", age: 3 }, "age"));\n',
                    'K extends keyof T', [("", "3")],
                    hints=["The key parameter must be one of T's own key names.",
                           "Write K extends keyof T."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ke-3", "Use the specific return type",
                    "The plucked id is a string, so uppercase it.",
                    'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n'
                    '  return o[k];\n}\n'
                    'const u = { id: "u1", age: 3 };\n'
                    'console.log(pluck(u, "id").toUpperCase());\n',
                    'pluck(u, "id").toUpperCase()', [("", "U1")],
                    hints=["T[K] resolved to string for this key.",
                           'Write pluck(u, "id").toUpperCase().'],
                    difficulty="Medium"),
                _ex("tscourse-w10-ke-4", "Sort by a key",
                    "Complete the comparator so the rows sort by the chosen key.",
                    'function sortBy<T, K extends keyof T>(rows: T[], key: K): T[] {\n'
                    '  return [...rows].sort((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0));\n}\n'
                    'const people = [\n  { name: "Cy", age: 47 },\n  { name: "Bo", age: 20 },\n];\n'
                    'console.log(sortBy(people, "age").map((p) => p.name).join(","));\n',
                    'a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0',
                    [("", "Bo,Cy")],
                    hints=["Return a negative, positive or zero number, comparing the two keyed values.",
                           "Write a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ke-5", "Pluck across a list",
                    "Pull one column out of the records by key.",
                    'function pluckAll<T, K extends keyof T>(rows: T[], k: K): T[K][] {\n'
                    '  return rows.map((r) => r[k]);\n}\n'
                    'const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];\n'
                    'console.log(pluckAll(people, "name").join(","));\n',
                    'rows.map((r) => r[k])', [("", "Ada,Bo")],
                    hints=["map each record to the keyed property.",
                           "Write rows.map((r) => r[k])."],
                    difficulty="Medium"),
                _fix("tscourse-w10-ke-fix1", "Fix the any-typed pluck",
                     "This returns `any`, so the mistyped method call was not caught and it crashes. Type it with keyof and call the right method.",
                     'function pluck(o: any, k: string): any {\n  return o[k];\n}\n'
                     'const u = { id: "u1", age: 3 };\nconsole.log(pluck(u, "id").toFixed(2));\n',
                     'function pluck<T, K extends keyof T>(o: T, k: K): T[K] {\n  return o[k];\n}\n'
                     'const u = { id: "u1", age: 3 };\nconsole.log(pluck(u, "id").toUpperCase());\n',
                     [("", "U1")],
                     hints=["With any, calling toFixed on a string raised no complaint.",
                            "Parameterise T and K so the return type is the property's real type."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`T[keyof T]` gives you…",
                   ["the key names", "the union of the property TYPES", "an array", "never"], 1,
                   "keyof gives names; indexing by them gives value types."),
                _q("Omitting `extends keyof T` from the key parameter means…",
                   ["it still works", "o[k] becomes an error, since k might not be a key",
                    "faster inference", "nothing"], 1,
                   "The constraint is what licenses the lookup."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w10-types", "Generic types & interfaces",
            "Parameterising a shape, not just a function.",
            """
Types take parameters too:

```ts
interface Box<T> {
  value: T;
}

const a: Box<string> = { value: "hi" };
const b: Box<number> = { value: 42 };
```

`Box<string>` is a *different type* from `Box<number>`, produced from one
declaration. Type aliases work the same way:

```ts
type Pair<A, B> = { left: A; right: B };
type List<T> = T[];
type Lookup<V> = { [key: string]: V };
```

**The Result type** is the pattern you'll actually reach for, combining week 9's
discriminated union with a type parameter:

```ts
type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

function parseNum(s: string): Result<number> {
  const n = Number(s);
  if (Number.isNaN(n)) return { ok: false, error: `bad number: ${s}` };
  return { ok: true, value: n };
}

const r = parseNum("42");
if (r.ok) {
  r.value.toFixed(2);      // r.value: number
}
```

One `Result<T>` serves every operation that can fail, and the success type
changes per use: `Result<number>`, `Result<User>`, `Result<string[]>`. This is
how serious codebases handle failure without exceptions — and it is the shape
behind Rust's `Result` and many TypeScript libraries.

**Generic types can be constrained** exactly like generic functions:

```ts
type Table<T extends { id: string }> = { [id: string]: T };
```

**Nesting works and reads fine once you're used to it:**

```ts
Result<Box<string>>
Pair<string, number[]>
```

**Recursive generic types** are legal, and are how tree shapes are described:

```ts
type Tree<T> = { value: T; children: Tree<T>[] };
```

**The naming convention** for a generic type's parameter mirrors functions: `T`
for the payload, `K`/`V` for key and value, `E` for an error type. `Result<T, E>`
with a parameterised error is common in larger codebases.

> ⚠️ **Common mistakes:** writing `Box` without its argument (it needs one
> unless there's a default); assuming `Box<string>` is assignable to
> `Box<number>` (it is not); and reaching for a generic type when a plain union
> would say it more clearly.
""",
            warmup=[
                _q("`interface Box<T> { value: T }` — `Box<string>`'s value has type…",
                   ["T", "string", "any", "unknown"], 1, "The argument replaces the parameter."),
                _q("Is `Box<string>` assignable to `Box<number>`?",
                   ["yes", "no", "only if empty", "only with a cast"], 1,
                   "They are unrelated types."),
                _q("`type Result<T> = {ok:true; value:T} | {ok:false; error:string}` — after `if (r.ok)`, `r.value` is…",
                   ["T | undefined", "T", "string", "never"], 1,
                   "The discriminant narrowed it to the success member."),
                _q("Writing `Box` with no type argument is…",
                   ["fine", "an error unless T has a default", "inferred", "any"], 1,
                   "A generic type needs its arguments."),
            ],
            exercises=[
                _design("tscourse-w10-ty-d1", "Design the paged result",
                        "An API hands back a page of results — any kind of results. The code "
                        "that builds and reads one is already written; the type it agrees on "
                        "is not. Write the generic `Page<T>` interface that both halves need, "
                        "so a page of strings and a page of numbers are both describable.",
                        'interface Page<T> {\n'
                        '  items: T[];\n'
                        '  total: number;\n'
                        '  next: string | null;\n'
                        '}\n'
                        'const names: Page<string> = { items: ["Ada", "Bo"], total: 7, next: "p2" };\n'
                        'const scores: Page<number> = { items: [10, 20], total: 2, next: null };\n'
                        'console.log(`${names.items.join(",")} of ${names.total} -> ${names.next}`);\n'
                        'console.log(`${scores.items.length} of ${scores.total} -> ${scores.next}`);\n',
                        '  items: T[];\n'
                        '  total: number;\n'
                        '  next: string | null;\n',
                        'type _1 = Expect<Equal<Page<string>["items"], string[]>>;\n'
                        'type _2 = Expect<Equal<Page<number>["items"], number[]>>;\n'
                        'type _3 = Expect<Equal<Page<string>["total"], number>>;\n'
                        'type _4 = Expect<Equal<Page<string>["next"], string | null>>;\n'
                        'type _5 = Expect<Equal<keyof Page<string>, "items" | "total" | "next">>;\n',
                        [("", "Ada,Bo of 7 -> p2\n2 of 2 -> null")],
                        hints=["Three fields. Only one of them varies with T.",
                               "`total` counts results, so it is a number whatever T is.",
                               "`next` is a cursor when there is another page and `null` when "
                               "there is not — that is a union, not an optional field."],
                        difficulty="Medium"),
                _ex("tscourse-w10-ty-1", "A generic interface",
                    "Declare Box with a type parameter, then print both boxed values.",
                    'interface Box<T> {\n  value: T;\n}\n'
                    'const a: Box<string> = { value: "hi" };\n'
                    'const b: Box<number> = { value: 42 };\n'
                    'console.log(`${a.value} ${b.value}`);\n',
                    'Box<T>', [("", "hi 42")],
                    hints=["The parameter list goes right after the interface name.",
                           "Write Box<T>."]),
                _ex("tscourse-w10-ty-2", "A generic alias",
                    "Print both sides of the pair.",
                    'type Pair<A, B> = { left: A; right: B };\n'
                    'const p: Pair<string, number> = { left: "x", right: 1 };\n'
                    'console.log(`${p.left}${p.right}`);\n',
                    '${p.left}${p.right}', [("", "x1")],
                    hints=["Two holes, no separator.",
                           "Write ${p.left}${p.right}."]),
                _ex("tscourse-w10-ty-3", "A Result type",
                    "Return the failing Result when the input does not parse.",
                    _LINE + 'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseNum(s: string): Result<number> {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: `bad number: ${s}` };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parseNum(line);\n'
                    'console.log(r.ok ? r.value.toFixed(2) : r.error);\n',
                    'return { ok: false, error: `bad number: ${s}` };',
                    [("42", "42.00"), ("abc", "bad number: abc")],
                    hints=["The failure member carries the tag and the message.",
                           "Write return { ok: false, error: `bad number: ${s}` };"],
                    difficulty="Medium"),
                _ex("tscourse-w10-ty-4", "Consume a Result",
                    "Print the value to 2 decimals on success, or the error message.",
                    _LINE + 'type Result<T> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: string };\n'
                    'function parseNum(s: string): Result<number> {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: "bad" };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parseNum(line);\n'
                    'console.log(r.ok ? r.value.toFixed(2) : r.error);\n',
                    'r.ok ? r.value.toFixed(2) : r.error',
                    [("7", "7.00"), ("zz", "bad")],
                    hints=["The tag narrows, so value and error are each available in one branch only.",
                           "Write r.ok ? r.value.toFixed(2) : r.error."],
                    difficulty="Medium"),
                _ex("tscourse-w10-ty-5", "A generic lookup",
                    "Declare a lookup whose values are numbers, then print one.",
                    'type Lookup<V> = { [key: string]: V };\n'
                    'const prices: Lookup<number> = { coffee: 3.25, book: 12 };\n'
                    'console.log((prices["coffee"] ?? 0).toFixed(2));\n',
                    'Lookup<number>', [("", "3.25")],
                    hints=["Supply the value type as the argument.",
                           "Write Lookup<number>."],
                    difficulty="Medium"),
                _fix("tscourse-w10-ty-fix1", "Fix the missing type argument",
                     "`Box` was used without its argument, so the value was left untyped and the wrong method was called. Supply the argument and call the right one.",
                     'interface Box<T> {\n  value: T;\n}\n'
                     'const a: Box<any> = { value: "hi" };\n'
                     'console.log(a.value.toFixed(2));\n',
                     'interface Box<T> {\n  value: T;\n}\n'
                     'const a: Box<string> = { value: "hi" };\n'
                     'console.log(a.value.toUpperCase());\n',
                     [("", "HI")],
                     hints=["Box<any> silenced the check; the value really is a string.",
                            "Use Box<string> and call a string method."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`Result<T>` is useful because…",
                   ["it is shorter", "one failure-handling shape serves every success type",
                    "it avoids unions", "it is built in"], 1,
                   "The success payload varies; the machinery does not."),
                _q("`type Tree<T> = { value: T; children: Tree<T>[] }` is…",
                   ["illegal", "a legal recursive generic type", "an interface", "a union"], 1,
                   "Recursion in type definitions is fine."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w10-defaults", "Defaults & knowing when to stop",
            "Default type arguments, and generics that aren't worth it.",
            """
A type parameter can have a **default**, used when the caller doesn't supply
one:

```ts
interface Options<T = string> {
  items: T[];
}

const a: Options = { items: ["x"] };            // T defaults to string
const b: Options<number> = { items: [1, 2] };
```

Defaults make a generic type usable in the common case without ceremony. They
follow the same rule as default parameters in week 5: **defaults come last.**

```ts
type Result<T, E = string> =
  | { ok: true; value: T }
  | { ok: false; error: E };

Result<number>              // error is string
Result<number, Error>       // error is an Error
```

**Constraints and defaults combine**, in that order:

```ts
interface Table<T extends { id: string } = { id: string }> { rows: T[] }
```

---

**Now the more valuable half of this lesson: when *not* to reach for a generic.**

Generics have a real cost — every reader has to hold another variable in their
head. Three signs you don't need one:

**1. The parameter appears only once.**

```ts
function log<T>(x: T): void { console.log(x); }     // 🚩
function log(x: unknown): void { console.log(x); }  // ✅ says the same thing
```

If `T` doesn't connect two places, it is decoration.

**2. You immediately constrain it to exactly one thing.**

```ts
function f<T extends string>(x: T): void { ... }    // 🚩 unless you return T
function f(x: string): void { ... }                 // ✅
```

The exception is when you *return* `T` — then the constraint preserves literal
types, which is genuinely useful.

**3. You end up casting inside.** If the body needs `as` to do its work, the
signature is promising something the implementation can't honour. Rethink the
types rather than papering over them.

**And the counter-test — when you *do* want one:** a type appears in two or
more positions and callers would otherwise lose information. `first`, `pluck`,
`sortBy`, `Result` all pass. `log` does not.

**Reading generics you didn't write** is most of the benefit here. When a
library signature looks frightening, name the parts:

```ts
function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] }
```

*"For any row type T, and any key K of T, take rows and a key, and give back a
lookup from key values to arrays of rows."* Once you can do that narration, the
ecosystem opens up.

> ⚠️ **Common mistakes:** adding type parameters for symmetry; putting a
> defaulted parameter before a required one; and treating a scary-looking
> signature as unknowable rather than reading it left to right.
""",
            warmup=[
                _q("`interface Options<T = string>` used as plain `Options` gives T as…",
                   ["any", "string", "unknown", "an error"], 1, "The default fills in."),
                _q("Defaulted type parameters must come…",
                   ["first", "last", "anywhere", "alone"], 1,
                   "Same rule as default value parameters."),
                _q("`function log<T>(x: T): void` — is the generic earning its place?",
                   ["yes", "no — T appears only once", "yes, for speed", "only for arrays"], 1,
                   "Nothing is connected, so `unknown` says it better."),
                _q("Needing `as` inside a generic's body usually means…",
                   ["you are done", "the signature promises more than the body can honour",
                    "it is optimised", "T is wrong"], 1,
                   "A cast there is a design smell."),
            ],
            exercises=[
                _ex("tscourse-w10-df-1", "A default type argument",
                    "Give T a default of string, then use Options with no argument.",
                    'interface Options<T = string> {\n  items: T[];\n}\n'
                    'const a: Options = { items: ["x", "y"] };\n'
                    'console.log(a.items.join(","));\n',
                    'T = string', [("", "x,y")],
                    hints=["The default is written with = after the parameter name.",
                           "Write T = string."]),
                _ex("tscourse-w10-df-2", "Override the default",
                    "Use Options at number, then total the items.",
                    'interface Options<T = string> {\n  items: T[];\n}\n'
                    'const b: Options<number> = { items: [1, 2, 3] };\n'
                    'console.log(b.items.reduce((s, x) => s + x, 0));\n',
                    'Options<number>', [("", "6")],
                    hints=["Supply the argument explicitly to override the default.",
                           "Write Options<number>."]),
                _ex("tscourse-w10-df-3", "Result with a defaulted error",
                    "Print the value on success, or the error message.",
                    _LINE + 'type Result<T, E = string> =\n'
                    '  | { ok: true; value: T }\n'
                    '  | { ok: false; error: E };\n'
                    'function parseNum(s: string): Result<number> {\n'
                    '  const n = Number(s);\n'
                    '  if (Number.isNaN(n)) return { ok: false, error: "bad" };\n'
                    '  return { ok: true, value: n };\n}\n'
                    'const r = parseNum(line);\nconsole.log(r.ok ? r.value : r.error);\n',
                    'T, E = string', [("5", "5"), ("zz", "bad")],
                    hints=["The payload type is required; the error type defaults.",
                           "Write T, E = string."],
                    difficulty="Medium"),
                _ex("tscourse-w10-df-4", "Prefer unknown to a pointless generic",
                    "This helper only prints, so it needs no type parameter. Give it the right one.",
                    'function show(x: unknown): void {\n  console.log(x);\n}\n'
                    'show("a");\nshow(1);\n',
                    'x: unknown', [("", "a\n1")],
                    hints=["Nothing is returned, so no type needs preserving.",
                           "Write x: unknown."]),
                _ex("tscourse-w10-df-5", "Group rows by a key",
                    "Complete the grouping so each key value collects its rows.",
                    'function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] } {\n'
                    '  const out: { [k: string]: T[] } = {};\n'
                    '  for (const r of rows) {\n'
                    '    const k = String(r[key]);\n'
                    '    if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
                    '    out[k]!.push(r);\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'const rows = [\n  { tag: "food", n: 1 },\n  { tag: "home", n: 2 },\n  { tag: "food", n: 3 },\n];\n'
                    'const g = groupBy(rows, "tag");\n'
                    'console.log(Object.keys(g).sort().map((k) => `${k}=${g[k]!.length}`).join(","));\n',
                    'if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
                    '    out[k]!.push(r);',
                    [("", "food=2,home=1")],
                    hints=["Create the bucket before pushing into it — week 7's grouping pattern.",
                           "Write if (out[k] === undefined) { out[k] = []; } then out[k]!.push(r);"],
                    difficulty="Medium"),
                _fix("tscourse-w10-df-fix1", "Fix the default's position",
                     "A defaulted type parameter sits before a required one, so `Pair<number>` cannot work. Reorder them.",
                     'type Pair<A = string, B> = { left: A; right: B };\n'
                     'const p: Pair<string, number> = { left: "x", right: 1 };\n'
                     'console.log(`${p.left}${p.right}`);\n',
                     'type Pair<A, B = string> = { left: A; right: B };\n'
                     'const p: Pair<number, string> = { left: 1, right: "x" };\n'
                     'console.log(`${p.left}${p.right}`);\n',
                     [("", "1x")],
                     hints=["Defaults must come last, or callers could never skip them.",
                            "Move the default onto B, and swap the arguments at the use site."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which signature genuinely needs a generic?",
                   ["log<T>(x: T): void", "pluck<T, K extends keyof T>(o: T, k: K): T[K]",
                    "print<T>(x: T): void", "warn<T>(x: T): void"], 1,
                   "Its type parameters connect the arguments to the return type."),
                _q("The best way to read an intimidating generic signature is…",
                   ["skip it", "narrate it left to right, naming each parameter",
                    "look at the body", "assume any"], 1,
                   "'For any T, and any key K of T, …'"),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w10-hof", "Generics that take functions",
            "Two type parameters, with a callback carrying you from one to the other.",
            """
Every generic helper you have written so far kept the same type all the way
through: `T` in, `T` out. The helpers you actually use every day are more
interesting than that — they **change** the type on the way through, and the
callback is what decides the new one.

Look at `map`, written out longhand:

```ts
function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {
  const out: U[] = [];
  for (const x of xs) out.push(f(x));
  return out;
}

mapAll([1, 2, 3], (n) => n * 2);        // T = number, U = number  → number[]
mapAll(["a", "bb"], (s) => s.length);   // T = string, U = number  → number[]
```

Two parameters, two different jobs:

| parameter | where it comes from |
|---|---|
| `T` | inferred from the array you pass |
| `U` | inferred from **what the callback returns** |

Neither is written at the call site. You describe the *relationship* — "give me
an array of whatever this function hands back" — and inference fills in the rest.
This is the whole idea of generics arriving at its most useful form.

**The shape recurs everywhere.** Once you can read `<T, U>` you can write the
standard toolkit:

```ts
function groupBy<T>(xs: T[], key: (x: T) => string): { [k: string]: T[] } { … }
function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] { … }
function maxBy<T>(xs: T[], score: (x: T) => number): T { … }
function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> { … }
```

Note the pattern in the first three: the callback's *return* type is fixed
(`string`, `number`) because the helper needs to compare or index with it, while
`T` stays free. That combination — one parameter open, one pinned — is what makes
them usable on any record shape you invent later.

**`zip` needs two open parameters** because it genuinely relates two independent
things, and the tuple `[A, B]` records that relationship in the result. `T[]` and
`Array<T>` are the same notation, by the way; `Array<[A, B]>` is just easier to
read than `[A, B][]`.

**Naming.** `T` and `U` are fine for a helper that truly works on anything.
`K`/`V` are conventional for a key and value. Once a parameter means something
specific to your domain, spell it out — `<Row>` reads far better than `<T>` in a
function that only makes sense over table rows.

**When inference has nothing to work from, say it yourself:**

```ts
const nums = emptyOf<number>();   // no argument, so nothing to infer from
```

Explicit type arguments are the exception, not the rule — needing them on a call
that *does* pass data usually means the signature is describing the wrong
relationship.

> ⚠️ **Common mistakes:** pushing the original item instead of the callback's
> result, so `U` is a lie; forgetting the callback's parameter type is `T` and
> annotating it `any`; and giving a helper two type parameters when the second
> one only ever appears once — if `U` shows up in exactly one place, it isn't
> relating anything and can be a concrete type.
""",
            warmup=[
                _q("In `mapAll<T, U>(xs: T[], f: (x: T) => U): U[]`, where does `U` come from?",
                   ["the array", "the callback's return type", "the call site, always", "the return statement"], 1,
                   "Inference reads it off what the callback hands back."),
                _q("`mapAll([\"a\", \"bb\"], (s) => s.length)` has type…",
                   ["string[]", "number[]", "unknown[]", "(string | number)[]"], 1,
                   "T is string, U is number, so the result is number[]."),
                _q("`Array<[A, B]>` and `[A, B][]` are…",
                   ["different types", "the same type written two ways", "only valid for tuples", "an error"], 1,
                   "Pick whichever reads better in context."),
                _q("A helper whose second type parameter appears only once…",
                   ["is optimal", "probably doesn't need to be generic there",
                    "cannot compile", "must be constrained"], 1,
                   "A type parameter earns its keep by relating two positions."),
            ],
            exercises=[
                _retype("tscourse-w10-hof-r1", "Give the helper its generics back",
                        "`pluck` reads one field out of every record. Written with `any` it "
                        "accepts anything and tells the caller nothing — `names` below could "
                        "be a number[] for all the compiler knows. Retype it with two type "
                        "parameters so the element type and the key are both tracked, and the "
                        "result is exactly the type of the field you asked for.",
                        'function pluck(rows: any, key: any): any {\n'
                        '  return rows.map((r: any) => r[key]);\n}\n'
                        'const people = [\n'
                        '  { name: "Ada", age: 36 },\n'
                        '  { name: "Bo", age: 24 },\n'
                        '];\n'
                        'const names = pluck(people, "name");\n'
                        'const ages = pluck(people, "age");\n'
                        'console.log(names.join(","));\n'
                        'console.log(ages.join(","));\n',
                        'function pluck<T, K extends keyof T>(rows: T[], key: K): T[K][] {\n'
                        '  return rows.map((r) => r[key]);\n}\n'
                        'const people = [\n'
                        '  { name: "Ada", age: 36 },\n'
                        '  { name: "Bo", age: 24 },\n'
                        '];\n'
                        'const names = pluck(people, "name");\n'
                        'const ages = pluck(people, "age");\n'
                        'console.log(names.join(","));\n'
                        'console.log(ages.join(","));\n',
                        'type _1 = Expect<Equal<typeof names, string[]>>;\n'
                        'type _2 = Expect<Equal<typeof ages, number[]>>;\n',
                        [("", "Ada,Bo\n36,24")],
                        hints=["Two things vary: the record type, and which key is being read. "
                               "That is one type parameter each.",
                               "The key cannot be any string — it must be a key of the record. "
                               "`K extends keyof T` says exactly that.",
                               "The return is an array of the field's type, which is written "
                               "`T[K][]` — an indexed access, then an array of it."],
                        difficulty="Medium"),
                _ex("tscourse-w10-hof-1", "Type the callback",
                    "Fill in the callback's parameter, so `mapAll` takes a `T` and produces a `U`.",
                    'function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {\n'
                    '  const out: U[] = [];\n'
                    '  for (const x of xs) out.push(f(x));\n'
                    '  return out;\n}\n'
                    'console.log(mapAll([1, 2, 3], (n) => n * 2).join(","));\n'
                    'console.log(mapAll(["a", "bb"], (s) => s.length).join(","));\n',
                    'f: (x: T) => U', [("", "2,4,6\n1,2")],
                    hints=["The callback receives an element of the input array and returns an element of the output.",
                           "Write f: (x: T) => U."]),
                _ex("tscourse-w10-hof-2", "Generic groupBy",
                    "Finish the bucket step so any array can be grouped by any key function.",
                    'function groupBy<T>(xs: T[], key: (x: T) => string): { [k: string]: T[] } {\n'
                    '  const out: { [k: string]: T[] } = {};\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    out[k] = out[k] ?? [];\n'
                    '    out[k]!.push(x);\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'const words = ["ant", "bee", "ape"];\n'
                    'const byLetter = groupBy(words, (w) => w[0] ?? "");\n'
                    'console.log(Object.keys(byLetter).sort().join(","));\n'
                    'console.log(byLetter["a"]!.join(" "));\n',
                    'out[k]!.push(x);', [("", "a,b\nant ape")],
                    hints=["The bucket already exists by this line — add the item to it.",
                           "Push the item itself, not the key."],
                    difficulty="Easy"),
                _ex("tscourse-w10-hof-3", "Two open parameters",
                    "`zip` pairs two independent arrays. Fill in its return annotation.",
                    'function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> {\n'
                    '  const out: Array<[A, B]> = [];\n'
                    '  const n = Math.min(as.length, bs.length);\n'
                    '  for (let i = 0; i < n; i++) out.push([as[i]!, bs[i]!]);\n'
                    '  return out;\n}\n'
                    'const pairs = zip(["a", "b", "c"], [1, 2]);\n'
                    'console.log(pairs.map((p) => `${p[0]}=${p[1]}`).join(","));\n',
                    'Array<[A, B]> {', [("", "a=1,b=2")],
                    hints=["Each element pairs one A with one B — that is a two-element tuple.",
                           "The result is an array of those tuples: Array<[A, B]>."],
                    difficulty="Medium"),
                _ex("tscourse-w10-hof-4", "Generic uniqueBy",
                    "Keep the first record for each key and skip the rest. Add the skipping check.",
                    'function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] {\n'
                    '  const seen: { [k: string]: boolean } = {};\n'
                    '  const out: T[] = [];\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    if (seen[k]) continue;\n'
                    '    seen[k] = true;\n'
                    '    out.push(x);\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'const people = [\n'
                    '  { name: "ada", city: "london" },\n'
                    '  { name: "alan", city: "london" },\n'
                    '  { name: "grace", city: "ny" },\n'
                    '];\n'
                    'console.log(uniqueBy(people, (p) => p.city).map((p) => p.name).join(","));\n',
                    'if (seen[k]) continue;', [("", "ada,grace")],
                    hints=["If this key has been recorded already, move on to the next item.",
                           "Write if (seen[k]) continue;"],
                    difficulty="Medium"),
                _ex("tscourse-w10-hof-5", "Say it when nothing can be inferred",
                    "There is no argument to infer from here, so supply the type argument yourself.",
                    'function emptyOf<T>(): T[] {\n'
                    '  return [];\n}\n'
                    'const nums = emptyOf<number>();\n'
                    'nums.push(1);\n'
                    'nums.push(2);\n'
                    'console.log(nums.join(","));\n',
                    'emptyOf<number>()', [("", "1,2")],
                    hints=["Type arguments go in angle brackets between the name and the parentheses.",
                           "Write emptyOf<number>()."],
                    difficulty="Easy"),
                _fix("tscourse-w10-hof-fix1", "Fix the ignored callback",
                     "This should print `2,4,6` but prints the originals — the callback's result is being thrown away.",
                     'function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {\n'
                     '  const out: U[] = [];\n'
                     '  for (const x of xs) out.push(x as unknown as U);\n'
                     '  return out;\n}\n'
                     'console.log(mapAll([1, 2, 3], (n) => n * 2).join(","));\n',
                     'function mapAll<T, U>(xs: T[], f: (x: T) => U): U[] {\n'
                     '  const out: U[] = [];\n'
                     '  for (const x of xs) out.push(f(x));\n'
                     '  return out;\n}\n'
                     'console.log(mapAll([1, 2, 3], (n) => n * 2).join(","));\n',
                     [("", "2,4,6")],
                     hints=["The double assertion was silencing the very error that would have caught this.",
                            "Push what the callback returns: out.push(f(x))."],
                     difficulty="Medium"),
                _fix("tscourse-w10-hof-fix2", "Fix the overrun",
                     "Zipping a three-element array with a two-element one should give two pairs, but a third appears with an undefined half.",
                     'function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> {\n'
                     '  const out: Array<[A, B]> = [];\n'
                     '  const n = as.length;\n'
                     '  for (let i = 0; i < n; i++) out.push([as[i]!, bs[i]!]);\n'
                     '  return out;\n}\n'
                     'const pairs = zip(["a", "b", "c"], [1, 2]);\n'
                     'console.log(pairs.map((p) => `${p[0]}=${p[1]}`).join(","));\n',
                     'function zip<A, B>(as: A[], bs: B[]): Array<[A, B]> {\n'
                     '  const out: Array<[A, B]> = [];\n'
                     '  const n = Math.min(as.length, bs.length);\n'
                     '  for (let i = 0; i < n; i++) out.push([as[i]!, bs[i]!]);\n'
                     '  return out;\n}\n'
                     'const pairs = zip(["a", "b", "c"], [1, 2]);\n'
                     'console.log(pairs.map((p) => `${p[0]}=${p[1]}`).join(","));\n',
                     [("", "a=1,b=2")],
                     hints=["Reading past the end of the shorter array gives undefined.",
                            "Stop at Math.min(as.length, bs.length)."]),
                _fix("tscourse-w10-hof-fix3", "Fix the forgetful set",
                     "This should print `ada,grace` but keeps every record — nothing is ever recorded as seen.",
                     'function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] {\n'
                     '  const seen: { [k: string]: boolean } = {};\n'
                     '  const out: T[] = [];\n'
                     '  for (const x of xs) {\n'
                     '    const k = key(x);\n'
                     '    if (seen[k]) continue;\n'
                     '    out.push(x);\n'
                     '  }\n'
                     '  return out;\n}\n'
                     'const people = [\n'
                     '  { name: "ada", city: "london" },\n'
                     '  { name: "alan", city: "london" },\n'
                     '  { name: "grace", city: "ny" },\n'
                     '];\n'
                     'console.log(uniqueBy(people, (p) => p.city).map((p) => p.name).join(","));\n',
                     'function uniqueBy<T>(xs: T[], key: (x: T) => string): T[] {\n'
                     '  const seen: { [k: string]: boolean } = {};\n'
                     '  const out: T[] = [];\n'
                     '  for (const x of xs) {\n'
                     '    const k = key(x);\n'
                     '    if (seen[k]) continue;\n'
                     '    seen[k] = true;\n'
                     '    out.push(x);\n'
                     '  }\n'
                     '  return out;\n}\n'
                     'const people = [\n'
                     '  { name: "ada", city: "london" },\n'
                     '  { name: "alan", city: "london" },\n'
                     '  { name: "grace", city: "ny" },\n'
                     '];\n'
                     'console.log(uniqueBy(people, (p) => p.city).map((p) => p.name).join(","));\n',
                     [("", "ada,grace")],
                     hints=["The check reads `seen`, but nothing ever writes to it.",
                            "Mark the key before pushing: seen[k] = true;"],
                     difficulty="Medium"),
                _ch("tscourse-w10-hof-ch1", "A generic reporting toolkit", "Hard",
                    "Write two helpers that work on any record type. `countBy(xs, key)` counts items per key; `maxBy(xs, score)` returns the item with the highest score. The program then reports sales per region and the single biggest sale.",
                    _FS +
                    'interface Sale {\n  region: string;\n  amount: number;\n}\n'
                    'function countBy<T>(xs: T[], key: (x: T) => string): { [k: string]: number } {\n'
                    '  const out: { [k: string]: number } = {};\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    out[k] = (out[k] ?? 0) + 1;\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'function maxBy<T>(xs: T[], score: (x: T) => number): T {\n'
                    '  let best: T = xs[0]!;\n'
                    '  for (const x of xs) {\n'
                    '    if (score(x) > score(best)) best = x;\n'
                    '  }\n'
                    '  return best;\n}\n'
                    'const sales: Sale[] = fs.readFileSync(0, "utf8").trim().split("\\n")\n'
                    '  .filter((l) => l.trim().length > 0)\n'
                    '  .map((l) => {\n'
                    '    const parts = l.split(",");\n'
                    '    return { region: (parts[0] ?? "").trim(), amount: Number(parts[1]) };\n'
                    '  });\n'
                    'const counts = countBy(sales, (s) => s.region);\n'
                    'for (const r of Object.keys(counts).sort()) console.log(`${r}: ${counts[r]}`);\n'
                    'const top = maxBy(sales, (s) => s.amount);\n'
                    'console.log(`Top: ${top.region} ${top.amount}`);\n',
                    'function countBy<T>(xs: T[], key: (x: T) => string): { [k: string]: number } {\n'
                    '  const out: { [k: string]: number } = {};\n'
                    '  for (const x of xs) {\n'
                    '    const k = key(x);\n'
                    '    out[k] = (out[k] ?? 0) + 1;\n'
                    '  }\n'
                    '  return out;\n}\n'
                    'function maxBy<T>(xs: T[], score: (x: T) => number): T {\n'
                    '  let best: T = xs[0]!;\n'
                    '  for (const x of xs) {\n'
                    '    if (score(x) > score(best)) best = x;\n'
                    '  }\n'
                    '  return best;\n}',
                    [("north,30\nsouth,20\nnorth,12", "north: 2\nsouth: 1\nTop: north 30"),
                     ("a,5\nb,9", "a: 1\nb: 1\nTop: b 9"),
                     ("solo,7", "solo: 1\nTop: solo 7")],
                    hints=["Both helpers keep T open and pin the callback's return type — string for a key, number for a score.",
                           "countBy is the tally pattern with (out[k] ?? 0) + 1.",
                           "maxBy tracks a running best, starting from the first element.",
                           "Neither helper mentions Sale anywhere — that is the point of writing them generically."]),
            ],
            quiz=[
                _q("In `mapAll<T, U>`, `U` is determined by…",
                   ["the input array", "what the callback returns", "the call site only", "the return statement's variable"], 1,
                   "Inference reads U off the callback's result type."),
                _q("`groupBy<T>(xs: T[], key: (x: T) => string)` pins the callback's return to `string` because…",
                   ["strings are faster", "the helper uses it as an object key",
                    "T must be a string", "generics require it"], 1,
                   "Object keys are strings, so that position cannot stay open."),
                _q("`zip` needs two type parameters because…",
                   ["it takes two arguments", "it relates two independent element types in the result",
                    "tuples require it", "inference fails otherwise"], 1,
                   "The tuple [A, B] carries both through to the output."),
                _q("You should write explicit type arguments…",
                   ["always", "rarely — mainly when there is no argument to infer from",
                    "never", "whenever there are two parameters"], 1,
                   "Needing them on a call that does pass data is usually a signature smell."),
            ],
        ),
        _lesson(
            "proof", "Proving a generic is right",
            "Test a type the only way a type can be tested — with the compiler.",
            """
Every exercise so far has been graded by **running** it: your program printed
something, and the judge compared that text. That works because values exist at
runtime.

Types do not.

```ts
type Value<T> = T[keyof T];
```

There is nothing to `console.log`. `Value` is erased before Node ever sees the
file — so if you get it wrong, *nothing happens*. No crash, no wrong output.
That is exactly why broken types survive in real codebases for months.

## Make a wrong type an error

The fix is to state what the type should be and let the compiler check it:

```ts
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
```

Read `Expect<T extends true>` as a **claim**. Its type parameter is constrained
to `true`, so handing it `false` is a compile error — the same way passing a
`string` to a `number` parameter is. And `Equal<X, Y>` produces `true` only when
`X` and `Y` are the same type.

Put them together and you have a test:

```ts
type Value<T> = T[keyof T];

type _1 = Expect<Equal<Value<{ a: number }>, number>>;        // compiles ✓
type _2 = Expect<Equal<Value<{ a: number }>, string>>;        // TS2344 ✗
```

The second line fails with:

```
Type 'false' does not satisfy the constraint 'true'.
```

`_1` and `_2` are never used and never run. They exist purely to be checked.

## Why not just `extends`?

You might reach for the simpler `T extends U ? true : false`. It is not the
same check, and the difference bites:

```ts
type Loose<X, Y> = X extends Y ? true : false;

type A = Loose<any, string>;     // boolean — any is assignable both ways
type B = Loose<never, string>;   // never   — and not `true`, as you might expect
```

Neither is a usable answer. `any` cannot pick a branch, so you get both. And
`never` collapses the whole thing: a bare type parameter on the left
*distributes* over a union, `never` is the empty union, so there is nothing to
distribute over and the result is `never`.

`Equal` gives a plain `true` or `false` for all of these, because it compares
the two conditional types *before* either is resolved. You do not need to be
able to derive it — you need to know it is the honest one, and reach for it.

## Exercises in this lesson are checked, not run

The three below have **no test cases**. You fill the blank, press
**Type-check**, and either every claim compiles or the compiler tells you which
one did not. Use *What's being checked?* to read the claims first — unlike a
hidden output test there is nothing to game, because you cannot satisfy
`Expect<Equal<…>>` without actually writing the type.
""",
            [
                _types(
                    "tscourse-w10-prf-1", "Pull out the element type",
                    "Write ElementOf so it yields the element type of an array type.",
                    'type ElementOf<T extends unknown[]> = T[number];\n',
                    "T[number]",
                    """
type _1 = Expect<Equal<ElementOf<string[]>, string>>;
type _2 = Expect<Equal<ElementOf<number[]>, number>>;
type _3 = Expect<Equal<ElementOf<boolean[][]>, boolean[]>>;
""",
                    hints=["Indexed access works on arrays too — the question is which key.",
                           "Every element of T sits at a numeric index.",
                           "Write T[number]."],
                    difficulty="Medium"),
                _types(
                    "tscourse-w10-prf-2", "Every value type in an object",
                    "Write ValueOf so it yields the union of an object type's value types.",
                    'type ValueOf<T> = T[keyof T];\n',
                    "T[keyof T]",
                    """
type _1 = Expect<Equal<ValueOf<{ a: number; b: number }>, number>>;
type _2 = Expect<Equal<ValueOf<{ a: number; b: string }>, number | string>>;
type _3 = Expect<Equal<ValueOf<{ id: string }>, string>>;
""",
                    hints=["keyof T is the union of the keys. You want what sits at those keys.",
                           "Indexed access distributes over a union of keys.",
                           "Write T[keyof T]."],
                    difficulty="Medium"),
                _types(
                    "tscourse-w10-prf-3", "Constrain the key",
                    "Field<T, K> should be the type of T's K property — and K must be a real key of T.",
                    'type Field<T, K extends keyof T> = T[K];\n',
                    "K extends keyof T",
                    """
type User = { id: number; name: string };

type _1 = Expect<Equal<Field<User, "id">, number>>;
type _2 = Expect<Equal<Field<User, "name">, string>>;
type _3 = Expect<Equal<Field<User, "id" | "name">, number | string>>;

// The constraint is doing real work: "email" is not a key of User, so this
// line MUST be an error. If you leave K unconstrained the directive below
// goes unused and the checker fails on that instead.
// @ts-expect-error
type _4 = Field<User, "email">;
""",
                    hints=["Without a constraint, T[K] is an error: K might not be a key at all.",
                           "Say that K has to come from keyof T.",
                           "Write K extends keyof T."],
                    difficulty="Medium"),
                _fn(
                    "tscourse-w10-prf-4", "lastOf, written blind",
                    "Return the last element of an array, or undefined when it is empty. "
                    "You write only the function — the checker calls it and inspects what "
                    "you return, so there is nothing to print.",
                    "lastOf",
                    [("xs", "T[]", "number[]")], "T | undefined",
                    """
if (xs.length === 0) return undefined;
return xs[xs.length - 1];
""",
                    [("3 9 4 1", "1"), ("7", "7"), ("", "undefined")],
                    hints=["The empty case has to come first — there is no last element to read.",
                           "The last index is length - 1.",
                           "Under noUncheckedIndexedAccess, xs[i] is already T | undefined, which is exactly the declared return type."],
                    difficulty="Medium", generics="T", prints="number"),
                _fn(
                    "tscourse-w10-prf-5", "countBy, written blind",
                    "Count how many times each word appears and return the tally as an object. "
                    "The checker compares the object you return, not text you printed.",
                    "tally",
                    [("words", "string[]")], "Record<string, number>",
                    """
const out: Record<string, number> = {};
for (const w of words) {
  out[w] = (out[w] ?? 0) + 1;
}
return out;
""",
                    [("red blue red", '{"red":2,"blue":1}'),
                     ("solo", '{"solo":1}'),
                     ("a b a b a", '{"a":3,"b":2}')],
                    hints=["Start from an empty Record<string, number> and walk the array.",
                           "A key you have not seen yet reads back as undefined, so default it.",
                           "out[w] = (out[w] ?? 0) + 1;"],
                    difficulty="Medium"),
            ],
            warmup=[
                _q("`type Expect<T extends true> = T;` rejects `Expect<false>` because…",
                   ["false is not a type", "the constraint `extends true` is violated",
                    "Expect runs at runtime", "T is unused"], 1,
                   "It is the same check as passing a string to a number parameter — just at the type level."),
                _q("A type-level exercise fails at…",
                   ["run time", "compile time", "install time", "never"], 1,
                   "There is no runtime: the assertion is a constraint the compiler enforces."),
                _q("`Equal<any, string>` is…",
                   ["true", "false", "boolean", "an error"], 1,
                   "Equal is exact. `any` is not the same type as `string`, even though it is assignable both ways."),
            ],
            quiz=[
                _q("`type _1 = Expect<Equal<X, Y>>` where the types differ produces…",
                   ["a runtime throw", "TS2344: Type 'false' does not satisfy the constraint 'true'",
                    "silent success", "a lint warning"], 1,
                   "Equal yields false, and Expect's constraint rejects it."),
                _q("Why can a type not be graded by running the program?",
                   ["types are slow", "types are erased before the code runs",
                    "Node lacks a type API", "types have no names"], 1,
                   "Node strips annotations; nothing about the type survives to inspect."),
                _q("`// @ts-expect-error` on the line above a type fails the check when…",
                   ["the line errors", "the line does NOT error", "always", "never"], 1,
                   "An unused directive is itself reported (TS2578) — which is what makes it a real negative test."),
                _q("`ElementOf<T extends unknown[]> = T[number]` works because…",
                   ["number is a key of every array", "arrays are objects",
                    "T is generic", "number[] is special-cased"], 0,
                   "Indexed access with `number` reaches every element slot."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #10 — a generic toolkit",
        """
Budget Buddy's helpers stop being about expenses and start being about
**records** — reusable over any row type at all.

Build three generics and use them on an expense ledger. Input is one row per
line, `desc amount tag`:

```
coffee 3.25 food
rent 900 home
lunch 9.50 food
book 12 fun
```

Print:

```
Rows:     4
By tag:   food=2, fun=1, home=1
Dearest:  rent
Cheapest: coffee
```

Required signatures — implement these exactly:

```ts
function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] }
function maxBy<T, K extends keyof T>(rows: T[], key: K): T
function minBy<T, K extends keyof T>(rows: T[], key: K): T
```

Rules:

- `By tag` lists each tag and its row count, keys sorted alphabetically, joined
  with `, `.
- `Dearest` and `Cheapest` are the descriptions of the rows with the largest and
  smallest amounts. On a tie the **first** such row wins.
- The helpers must not mention `Expense` anywhere — they work for any record.
""",
        _ch("tscourse-w10-capstone", "Budget Buddy #10", "Medium",
            "Write the three generic helpers, then apply them to the parsed rows.",
            _FS + 'interface Expense {\n  desc: string;\n  amount: number;\n  tag: string;\n}\n'
            'function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] } {\n'
            '  const out: { [k: string]: T[] } = {};\n'
            '  for (const r of rows) {\n'
            '    const k = String(r[key]);\n'
            '    if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
            '    out[k]!.push(r);\n'
            '  }\n'
            '  return out;\n}\n'
            'function maxBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best: T = rows[0]!;\n'
            '  for (const r of rows) {\n    if (r[key] > best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}\n'
            'function minBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best: T = rows[0]!;\n'
            '  for (const r of rows) {\n    if (r[key] < best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}\n'
            'function parse(line: string): Expense {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0] ?? "", amount: Number(p[1]), tag: p[2] ?? "" };\n}\n'
            'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
            'const groups = groupBy(rows, "tag");\n'
            'const tagParts = Object.keys(groups).sort().map((k) => `${k}=${groups[k]!.length}`);\n'
            'console.log(`Rows:     ${rows.length}`);\n'
            'console.log(`By tag:   ${tagParts.join(", ")}`);\n'
            'console.log(`Dearest:  ${maxBy(rows, "amount").desc}`);\n'
            'console.log(`Cheapest: ${minBy(rows, "amount").desc}`);\n',
            'function groupBy<T, K extends keyof T>(rows: T[], key: K): { [k: string]: T[] } {\n'
            '  const out: { [k: string]: T[] } = {};\n'
            '  for (const r of rows) {\n'
            '    const k = String(r[key]);\n'
            '    if (out[k] === undefined) {\n      out[k] = [];\n    }\n'
            '    out[k]!.push(r);\n'
            '  }\n'
            '  return out;\n}\n'
            'function maxBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best: T = rows[0]!;\n'
            '  for (const r of rows) {\n    if (r[key] > best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}\n'
            'function minBy<T, K extends keyof T>(rows: T[], key: K): T {\n'
            '  let best: T = rows[0]!;\n'
            '  for (const r of rows) {\n    if (r[key] < best[key]) {\n      best = r;\n    }\n  }\n'
            '  return best;\n}',
            [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
              "Rows:     4\nBy tag:   food=2, fun=1, home=1\nDearest:  rent\nCheapest: coffee"),
             ("tea 2 drink",
              "Rows:     1\nBy tag:   drink=1\nDearest:  tea\nCheapest: tea"),
             ("a 5 x\nb 5 x",
              "Rows:     2\nBy tag:   x=2\nDearest:  a\nCheapest: a")],
            hints=["All three helpers take `rows: T[]` and `key: K extends keyof T` — they must never mention Expense.",
                   "groupBy is week 7's grouping pattern: String(r[key]) for the bucket name, create the array before pushing.",
                   "maxBy and minBy are the best-so-far accumulator, seeded with rows[0] so the answer is always a real row.",
                   "Use a strict comparison (> and <) so a tie keeps the FIRST row.",
                   'Call them as maxBy(rows, "amount").desc — the return type is T, so .desc is available.']),
        example_io="Rows:     4\nBy tag:   food=2, fun=1, home=1\nDearest:  rent\nCheapest: coffee",
        rubric=["The three helpers are generic over the row type and its keys",
                "None of them mentions the Expense type",
                "groupBy creates each bucket before pushing into it",
                "maxBy and minBy seed from rows[0] and keep the first row on a tie"],
        stretch=_ch("tscourse-w10-capstone-stretch", "Budget Buddy #10 (stretch)", "Medium",
                    "Add a generic `sumBy<T, K extends keyof T>(rows: T[], key: K): number` and print `Total:    $924.75` from it. Since T[K] could be anything, convert each value with Number(...) before adding.",
                    _FS + 'interface Expense {\n  desc: string;\n  amount: number;\n  tag: string;\n}\n'
                    'function sumBy<T, K extends keyof T>(rows: T[], key: K): number {\n'
                    '  return rows.reduce((s, r) => s + Number(r[key]), 0);\n}\n'
                    'function parse(line: string): Expense {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0] ?? "", amount: Number(p[1]), tag: p[2] ?? "" };\n}\n'
                    'const rows: Expense[] = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(`Total:    $${sumBy(rows, "amount").toFixed(2)}`);\n',
                    'function sumBy<T, K extends keyof T>(rows: T[], key: K): number {\n'
                    '  return rows.reduce((s, r) => s + Number(r[key]), 0);\n}',
                    [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
                      "Total:    $924.75"),
                     ("tea 2 drink", "Total:    $2.00")],
                    hints=["The key could name a non-numeric field, so the compiler will not let you add T[K] directly.",
                           "Convert at the point of use: Number(r[key]).",
                           "Fold with reduce and an explicit seed of 0."]),
    ),
))
