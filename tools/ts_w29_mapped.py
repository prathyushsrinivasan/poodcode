# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 29 — conditional & mapped types.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief, _mk, _TYPE_PRELUDE) and every
# shared program prefix (_FS, _NUMS, _WORDS, _LINE) is already defined. This
# file only appends its week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# MONTH 8 OPENS. TS_ROADMAP: "Weeks 29-31 are the lowest-risk content in the whole
# back half — they are graded entirely by `judge_mode: "types"`." Mostly true here,
# with one deliberate exception: lesson 6 and the capstone put the types back onto
# RUNNING code, because a type-level trick that never meets a value is a puzzle,
# not a tool. Those exercises are graded on stdout AND on type assertions.
#
# REBUILDING THE BUILT-INS. Week 14 USED Partial, Pick, Omit, Exclude and the rest;
# this week WRITES them. An assertion like `Equal<Optional<E>, Partial<E>>` is
# satisfied by writing `Partial<E>`, so every rebuild passes `forbid=` with the
# built-in's name (`_types` gained that parameter for this week). The rebuilt types
# get their own names — Optional, Frozen, Needed, Keep, Drop, Without — both because
# `MyPartial<` would contain the banned substring `Partial<`, and because a name
# that says what it does is better than a copy of the library's.
#
# Every equality this week was probed against the real checker first, including
# the subtle ones: the key-remapped `Drop` IS `Equal` to `Omit` (modifiers survive
# the `as` clause); `DeepReadonly` turns `number[]` into `readonly number[]`; and a
# distributive conditional over `never` is `never` (the empty union), which is why
# `IsNever` must wrap its parameter in a tuple.
#
# `// @ts-expect-error` IN A HARNESS: used (as in week 25) to prove a type REJECTS
# something. Where the rejected line would also RUN — an assignment to a frozen
# object — it sits inside a function that is never called, so it is type-checked
# and never executed.
#
# THE CAPSTONE ARC: decision 2 in TS_ROADMAP — "weeks 29-32: a small typed library".
# Library #1 is the configuration module: DeepPartial overrides, a typed deep merge,
# and a DeepReadonly result that is also frozen at run time.
# ---------------------------------------------------------------------------

_ENTRY = (
    'interface Entry {\n'
    '  readonly id: string;\n'
    '  desc: string;\n'
    '  tag?: string;\n'
    '  cents: number;\n}\n'
)

_DEEP = (
    'type DeepPartial<T> = T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;\n'
    'type DeepReadonly<T> = T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } : T;\n'
    'function isRecord(v: unknown): v is Record<string, unknown> {\n'
    '  return typeof v === "object" && v !== null && !Array.isArray(v);\n}\n'
)


# --- Week 29 --------------------------------------------------------------
_WEEKS.append(_week(
    29, 8, _M8,
    "Conditional & Mapped Types",
    "Types that compute other types: an `if` for types, a `for` loop over keys, and `infer` to pull a type out of another. Then rebuild Partial, Pick, Omit and Exclude by hand — and start a small typed library.",
    """
Week 14 used `Partial`, `Pick`, `Omit` and `Exclude`. They are not compiler magic.
Each is a few characters of ordinary TypeScript, written with two tools this week
teaches — and once you can write them, you can write the ones the library does not
have.

## Two tools

**Conditional types** — an `if` for types:

```ts
type IsString<T> = T extends string ? true : false;
```

**Mapped types** — a `for` loop over a type's keys:

```ts
type Optional<T> = { [K in keyof T]?: T[K] };      // that is Partial
```

Plus **`infer`**, which reads a type *out of* another: "if `F` is a function, call
its return type `R`".

## You have used one every week since week 10

The checker's `Equal<X, Y>` — the line in every type-graded harness — is a
conditional type. This month you can read it.

## How the week is graded

Mostly by the **compiler alone** (week 10's `judge_mode: "types"`): the exercise
passes when the program type-checks against assertions like
`Expect<Equal<Optional<Entry>, Partial<Entry>>>`. Where you rebuild a built-in, its
name is **banned** from your answer, so the assertion cannot be satisfied by copying
it. Lesson 6 and the capstone then put the types back onto running code.

## The library

Months 5-7 ended on interview reps. The last four weeks build **a small typed
library**, one module a week. This week's module: a configuration loader whose
overrides are a `DeepPartial` and whose result is `DeepReadonly` — and genuinely
frozen at run time.

⏱️ Budget about **seven hours**.
""",
    objectives=[
        "Write a conditional type, and read the course's own Equal helper",
        "Say what 'distributive' means, and turn it off when it is not wanted",
        "Rebuild Exclude, Extract and NonNullable by hand",
        "Use `infer` to extract an element, a return type or a promise's value",
        "Write mapped types, including the `?`, `readonly`, `-?` and `-readonly` modifiers",
        "Rebuild Partial, Readonly, Required, Pick and Omit by hand",
        "Filter keys by their value type with `as` remapping",
        "Write a recursive mapped type — DeepReadonly, DeepPartial",
        "Give a runtime function a return type computed from its arguments",
        "Prove a type REJECTS something with `@ts-expect-error`",
    ],
    why="Library and framework types are built from exactly these pieces, and reading them is a daily task: every `Partial`, every `ReturnType`, every generated API client. Interviewers who ask 'type-level' questions ask these. And the skill that transfers is not the syntax — it is thinking of a type as the output of a computation over another type.",
    est_minutes=420,
    glossary=[
        _gloss("conditional type", "T extends U ? X : Y — an if/else evaluated by the compiler."),
        _gloss("distributive", "A conditional on a bare type parameter runs once per union member and unions the results."),
        _gloss("[T] extends [U]", "Wrapping in a tuple switches distribution off."),
        _gloss("never", "The empty union. A distributive conditional over it produces never."),
        _gloss("infer", "Inside a conditional's extends clause: name a part of the type to use in the result."),
        _gloss("mapped type", "{ [K in keyof T]: … } — build an object type by looping over keys."),
        _gloss("homomorphic", "A mapped type over keyof T; it keeps T's readonly and ? modifiers."),
        _gloss("modifier", "readonly and ? on a property. + adds them, - removes them."),
        _gloss("key remapping", "{ [K in keyof T as NewKey]: … } — rename or drop keys; never drops."),
        _gloss("recursive type", "A type that refers to itself, like DeepReadonly."),
        _gloss("@ts-expect-error", "A comment asserting the next line is an error — itself an error if it is not."),
        _gloss("type-level test", "Expect<Equal<Actual, Expected>> — fails to COMPILE when wrong."),
    ],
    cheatsheet="""
```ts
// ---- conditional -------------------------------------------------------
type IsString<T> = T extends string ? true : false;
type ElementOf<T> = T extends readonly unknown[] ? T[number] : never;

// distributive over unions, when T is a bare parameter:
type ToArray<T> = T extends unknown ? T[] : never;     // string | number → string[] | number[]
type ToArrayOne<T> = [T] extends [unknown] ? T[] : never;   // → (string | number)[]
type IsNever<T> = [T] extends [never] ? true : false;       // must be wrapped

// the union filters, by hand
type Without<T, U> = T extends U ? never : T;          // Exclude
type Only<T, U> = T extends U ? T : never;             // Extract

// ---- infer --------------------------------------------------------------
type Ret<F> = F extends (...args: never[]) => infer R ? R : never;     // ReturnType
type Unwrap<P> = P extends Promise<infer V> ? V : P;

// ---- mapped ----------------------------------------------------------------
type Optional<T> = { [K in keyof T]?: T[K] };           // Partial
type Frozen<T>   = { readonly [K in keyof T]: T[K] };   // Readonly
type Needed<T>   = { [K in keyof T]-?: T[K] };          // Required
type Mutable<T>  = { -readonly [K in keyof T]: T[K] };
type Keep<T, K extends keyof T> = { [P in K]: T[P] };   // Pick

// ---- remapping with `as` -----------------------------------------------------
type Drop<T, K extends PropertyKey> = { [P in keyof T as P extends K ? never : P]: T[P] };  // Omit
type NumbersOf<T> = { [K in keyof T as T[K] extends number ? K : never]: T[K] };

// ---- recursive -----------------------------------------------------------------
type DeepReadonly<T> = T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } : T;

// ---- proving a REJECTION in a test --------------------------------------------
// @ts-expect-error — an error if the next line compiles
const bad: Nested = [1, "two"];
```
""",
    self_check=[
        "Can you write IsString<T>, and read the course's Equal<X, Y>?",
        "Can you say what ToArray<string | number> is, and why?",
        "Can you turn distribution off?",
        "Can you say why IsNever<never> needs a tuple?",
        "Can you rebuild Exclude and Extract from memory?",
        "Can you write ReturnType with `infer`?",
        "Can you rebuild Partial, Readonly and Required, including `-?`?",
        "Can you rebuild Pick, and Omit with `as`?",
        "Can you keep only the keys whose values are numbers?",
        "Can you write DeepReadonly, and say what it does to arrays?",
        "Can you give a runtime function a mapped return type?",
        "Can you prove a type rejects a value?",
    ],
    review=[
        _q("`T extends U ? X : Y` is evaluated…",
           ["at run time", "by the compiler, on types", "never", "by Node"], 1,
           "An if for types."),
        _q("`ToArray<string | number>` with `T extends unknown ? T[] : never` is…",
           ["(string | number)[]", "string[] | number[]", "never", "unknown[]"], 1,
           "Distributive: once per member."),
        _q("Distribution is switched off by…",
           ["`as`", "wrapping in a tuple: [T] extends [U]", "`infer`", "`keyof`"], 1,
           "A tuple is not a bare type parameter."),
        _q("`T extends U ? never : T` rebuilds…",
           ["Extract", "Exclude", "Pick", "Omit"], 1,
           "Drop the members that match."),
        _q("`infer R` means…",
           ["R is any", "name this part of the matched type R, for use in the result", "R is required",
            "run R"], 1,
           "Only inside an extends clause."),
        _q("`{ [K in keyof T]?: T[K] }` is…",
           ["Required<T>", "Partial<T>", "Readonly<T>", "Pick<T>"], 1,
           "The ? modifier on every key."),
        _q("`-?` in a mapped type…",
           ["adds optional", "removes optional — Required", "is a syntax error", "negates"], 1,
           "And -readonly removes readonly."),
        _q("Omit is rebuilt with…",
           ["a union", "key remapping: as P extends K ? never : P", "infer", "a tuple"], 1,
           "Mapping a key to never drops it."),
        _q("DeepReadonly on `number[]` gives…",
           ["number[]", "readonly number[]", "never", "Readonly<number>"], 1,
           "Mapped types over arrays produce arrays."),
        _q("`// @ts-expect-error` above a line that compiles…",
           ["is ignored", "is itself an error (TS2578)", "passes", "hides the line"], 1,
           "Which is what lets a test prove a rejection."),
        _q("Why is `Partial<` banned in the rebuild exercises?",
           ["it is slow", "`Equal<Optional<E>, Partial<E>>` would pass by writing Partial<E>",
            "it is deprecated", "it is not typed"], 1,
           "The assertion cannot defend itself."),
    ],
    milestone="Library #1 — the config module. A typed defaults object; overrides read as JSON and typed as a `DeepPartial` of it; a generic deep merge; and a result that is `DeepReadonly` to the compiler and `Object.freeze`d all the way down at run time — with a test that proves writing to it will not compile.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w29-conditional", "An if for types",
            "`T extends U ? X : Y` — and the Equal helper you have used since week 10.",
            """
```ts
type IsString<T> = T extends string ? true : false;

type A = IsString<"hello">;     // true
type B = IsString<42>;          // false
```

`extends` here means **"is assignable to"**, the same relation as everywhere else.
`"hello"` is assignable to `string`, so the first branch is chosen. The result is a
**type** — `true` and `false` here are literal types, not values.

## Useful at once

```ts
type ElementOf<T> = T extends readonly unknown[] ? T[number] : never;
type Flatten<T>   = T extends readonly unknown[] ? T[number] : T;
```

`T[number]` is week 10's indexed access: "the type you get by indexing with a
number" — the element type. It is only allowed once the compiler knows `T` *is* an
array, which is exactly what the `extends` check establishes.

## The error that asks for one

```ts
type Len<T> = T["length"];
```

```
TS2536: Type '"length"' cannot be used to index type 'T'.
```

An unconstrained `T` might be `number`, which has no `length`. Either constrain the
parameter (`T extends readonly unknown[]`) or branch on it with a conditional.

## Reading `Equal`

Every type-graded exercise since week 10 has run this:

```ts
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
```

Two conditional types, deferred because `T` is unknown, compared with a third. The
compiler can only call the two deferred types identical when `X` and `Y` are
*identical* — which is stricter than "each assignable to the other", and is why
`Equal<any, string>` is false where `any extends string` is not. You do not have to
be able to invent that; you now can read it.

> ⚠️ **Common mistakes:** reading `extends` as "inherits"; indexing an
> unconstrained parameter; and expecting `true`/`false` here to be booleans at run
> time — they exist only for the compiler.
""",
            warmup=[
                _q("In a conditional type, `extends` means…",
                   ["inherits from", "is assignable to", "equals", "contains"], 1,
                   "The ordinary relation."),
                _q("`IsString<42>` is…",
                   ["true", "false", "never", "number"], 1,
                   "42 is not assignable to string."),
                _q("`T[number]` on an array type is…",
                   ["the length", "the element type", "a number", "never"], 1,
                   "Indexed access by number."),
                _q("`type Len<T> = T[\"length\"]` fails because…",
                   ["length is private", "T is unconstrained and might have no length", "of a typo", "it is recursive"], 1,
                   "TS2536."),
            ],
            exercises=[
                _types("tscourse-w29-cd-t1", "Is it a string?",
                       "Write `IsString<T>`: `true` when T is assignable to string, `false` otherwise.",
                       'type IsString<T> = T extends string ? true : false;\n',
                       'T extends string ? true : false',
                       """
type _1 = Expect<Equal<IsString<"hello">, true>>;
type _2 = Expect<Equal<IsString<string>, true>>;
type _3 = Expect<Equal<IsString<42>, false>>;
type _4 = Expect<Equal<IsString<{ a: 1 }>, false>>;
""",
                       hints=["A condition, then two branches.",
                              "T extends string ? true : false"],
                       difficulty="Easy"),
                _types("tscourse-w29-cd-t2", "The element type",
                       "Write `ElementOf<T>`: an array's element type, or `never` for anything that is not an array.",
                       'type ElementOf<T> = T extends readonly unknown[] ? T[number] : never;\n',
                       'T extends readonly unknown[] ? T[number] : never',
                       """
type _1 = Expect<Equal<ElementOf<string[]>, string>>;
type _2 = Expect<Equal<ElementOf<readonly number[]>, number>>;
type _3 = Expect<Equal<ElementOf<[1, "a"]>, 1 | "a">>;
type _4 = Expect<Equal<ElementOf<string>, never>>;
""",
                       hints=["Check it is an array — `readonly unknown[]` accepts both kinds.",
                              "Then `T[number]` is the element type.",
                              "T extends readonly unknown[] ? T[number] : never"],
                       difficulty="Medium"),
                _types("tscourse-w29-cd-t3", "Flatten one level",
                       "Write `Flatten<T>`: an array's element type, or T itself when it is not an array.",
                       'type Flatten<T> = T extends readonly unknown[] ? T[number] : T;\n',
                       'T extends readonly unknown[] ? T[number] : T',
                       """
type _1 = Expect<Equal<Flatten<string[]>, string>>;
type _2 = Expect<Equal<Flatten<number>, number>>;
type _3 = Expect<Equal<Flatten<boolean[][]>, boolean[]>>;
""",
                       hints=["The same test as ElementOf; only the else-branch differs.",
                              "T extends readonly unknown[] ? T[number] : T"],
                       difficulty="Easy"),
                _types("tscourse-w29-cd-t4", "Which kind of value",
                       "Write `KindOf<T>`: \"text\" for strings, \"number\" for numbers, \"list\" for arrays, "
                       "\"other\" for anything else — conditionals can be chained like else-if.",
                       'type KindOf<T> = T extends string ? "text" : T extends number ? "number" : T extends readonly unknown[] ? "list" : "other";\n',
                       'T extends string ? "text" : T extends number ? "number" : T extends readonly unknown[] ? "list" : "other"',
                       """
type _1 = Expect<Equal<KindOf<"a">, "text">>;
type _2 = Expect<Equal<KindOf<3>, "number">>;
type _3 = Expect<Equal<KindOf<string[]>, "list">>;
type _4 = Expect<Equal<KindOf<{ x: 1 }>, "other">>;
""",
                       hints=["Each false branch can be another conditional.",
                              "Order matters only when the tests overlap; these do not."],
                       difficulty="Medium"),
                _diagnose("tscourse-w29-cd-d1", "Indexing what might not have it",
                          "TS2536: Type '\"length\"' cannot be used to index type 'T'.",
                          'type Len<T> = T["length"];\n'
                          'const n: Len<[1, 2, 3]> = 3;\n'
                          'console.log(n);\n',
                          'type Len<T extends readonly unknown[]> = T["length"];\n'
                          'const n: Len<[1, 2, 3]> = 3;\n'
                          'console.log(n);\n',
                          [("", "3")],
                          hints=["What if T were number? It has no length.",
                                 "Promise the compiler T is an array, with a constraint.",
                                 "type Len<T extends readonly unknown[]> = T[\"length\"];"],
                          difficulty="Medium"),
            ],
            quiz=[
                _q("`Equal<any, string>` is false where `any extends string ? true : false` is true, because…",
                   ["a bug", "Equal compares for identity, not assignability", "any is never", "of distribution"], 1,
                   "Which is why the harness uses it."),
                _q("A tuple type's `length` is…",
                   ["number", "a literal type, e.g. 3", "never", "string"], 1,
                   "Len<[1, 2, 3]> is 3."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w29-distribute", "Unions go through one at a time",
            "Distribution — the reason Exclude works, and the reason IsNever needs a tuple.",
            """
Give a conditional type a union, with the parameter **bare** on the left of
`extends`, and it runs **once per member** and unions the results:

```ts
type ToArray<T> = T extends unknown ? T[] : never;
type A = ToArray<string | number>;       // string[] | number[]    — not (string | number)[]
```

That is called **distribution**, and it is what makes the union filters a single
line:

```ts
type Without<T, U> = T extends U ? never : T;     // Exclude
type Only<T, U>    = T extends U ? T : never;     // Extract
```

`Without<"a" | "b" | "c", "a">` runs for `"a"` (→ never), `"b"` (→ "b") and `"c"`
(→ "c"); `never` vanishes from a union, leaving `"b" | "c"`.

## Switching it off

Wrap both sides in a one-element tuple. `[T]` is not a bare parameter, so the
condition is checked once, on the whole union:

```ts
type ToArrayOne<T> = [T] extends [unknown] ? T[] : never;   // (string | number)[]
```

## `never`, the empty union

Distribution over a union of **no** members runs **zero** times and produces
`never`. So this looks right and is not:

```ts
type IsNeverWrong<T> = T extends never ? true : false;
type X = IsNeverWrong<never>;            // never — not true
```

The tuple wrapper is required: `[T] extends [never]`. The first time this bites, it
is baffling; now it will not.

> ⚠️ **Common mistakes:** expecting `(A | B)[]` from a distributive conditional;
> forgetting the tuple wrapper for `never`; and wrapping only one side.
""",
            warmup=[
                _q("A conditional distributes when…",
                   ["always", "the checked type is a bare type parameter and receives a union", "it uses infer",
                    "it is recursive"], 1,
                   "Once per member."),
                _q("`never` in a union…",
                   ["stays", "disappears", "becomes unknown", "is an error"], 1,
                   "Which is how Exclude removes members."),
                _q("`[T] extends [U]` means…",
                   ["an array check", "check the whole union once — no distribution", "a tuple of T", "a syntax error"], 1,
                   "The wrapper."),
                _q("`T extends never ? true : false` with T = never gives…",
                   ["true", "false", "never", "unknown"], 2,
                   "Zero members, zero results."),
            ],
            exercises=[
                _types("tscourse-w29-ds-t1", "Exclude, by hand",
                       "Write `Without<T, U>`: the members of T not assignable to U. `Exclude` itself is banned.",
                       'type Without<T, U> = T extends U ? never : T;\n',
                       'T extends U ? never : T',
                       """
type _1 = Expect<Equal<Without<"a" | "b" | "c", "a">, "b" | "c">>;
type _2 = Expect<Equal<Without<string | number | boolean, number>, string | boolean>>;
type _3 = Expect<Equal<Without<"a", "a">, never>>;
type _4 = Expect<Equal<Without<"a" | "b", "a">, Exclude<"a" | "b", "a">>>;
""",
                       hints=["Each member is tested on its own.",
                              "A member that matches U becomes never, and never disappears from the union.",
                              "T extends U ? never : T"],
                       difficulty="Medium", forbid=["Exclude<"]),
                _types("tscourse-w29-ds-t2", "Extract, by hand",
                       "Write `Only<T, U>`: the members of T that ARE assignable to U. `Extract` is banned.",
                       'type Only<T, U> = T extends U ? T : never;\n',
                       'T extends U ? T : never',
                       """
type _1 = Expect<Equal<Only<"a" | "b" | 1, string>, "a" | "b">>;
type _2 = Expect<Equal<Only<string | number, boolean>, never>>;
type _3 = Expect<Equal<Only<"x" | "y", "y">, Extract<"x" | "y", "y">>>;
""",
                       hints=["The mirror image of Without.",
                              "T extends U ? T : never"],
                       difficulty="Easy", forbid=["Extract<"]),
                _types("tscourse-w29-ds-t3", "NonNullable, by hand",
                       "Write `Present<T>`: T without null and undefined. `NonNullable` and `Exclude` are banned.",
                       'type Present<T> = T extends null | undefined ? never : T;\n',
                       'T extends null | undefined ? never : T',
                       """
type _1 = Expect<Equal<Present<string | null>, string>>;
type _2 = Expect<Equal<Present<number | undefined | null>, number>>;
type _3 = Expect<Equal<Present<null>, never>>;
type _4 = Expect<Equal<Present<string | null | undefined>, NonNullable<string | null | undefined>>>;
""",
                       hints=["It is Without<T, null | undefined>, written out.",
                              "T extends null | undefined ? never : T"],
                       difficulty="Easy", forbid=["NonNullable<", "Exclude<"]),
                _types("tscourse-w29-ds-t4", "One array, not a union of arrays",
                       "Write `ToArrayOne<T>` so that a union becomes ONE array of the union, not a union of arrays.",
                       'type ToArrayOne<T> = [T] extends [unknown] ? T[] : never;\n',
                       '[T] extends [unknown] ? T[] : never',
                       """
type _1 = Expect<Equal<ToArrayOne<string | number>, (string | number)[]>>;
type _2 = Expect<Equal<ToArrayOne<boolean>, boolean[]>>;
""",
                       hints=["A bare type parameter distributes; a tuple around it does not.",
                              "[T] extends [unknown] ? T[] : never"],
                       difficulty="Medium"),
                _types("tscourse-w29-ds-t5", "Is it never?",
                       "Write `IsNever<T>`: true only for never. The obvious version returns never for never.",
                       'type IsNever<T> = [T] extends [never] ? true : false;\n',
                       '[T] extends [never] ? true : false',
                       """
type _1 = Expect<Equal<IsNever<never>, true>>;
type _2 = Expect<Equal<IsNever<string>, false>>;
type _3 = Expect<Equal<IsNever<undefined>, false>>;
""",
                       hints=["never is the empty union, so a distributive check runs zero times.",
                              "Wrap both sides in a tuple.",
                              "[T] extends [never] ? true : false"],
                       difficulty="Hard"),
            ],
            quiz=[
                _q("`Without<string | number, string | number>` is…",
                   ["string | number", "never", "unknown", "an error"], 1,
                   "Every member is removed."),
                _q("Why does Exclude need distribution to work?",
                   ["it does not", "it must test and keep or drop each member separately", "for speed", "for never"], 1,
                   "One member at a time."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w29-infer", "Pulling a type out with `infer`",
            "Name a piece of the matched type, and use it in the result.",
            """
`ElementOf` used `T[number]`. That works for arrays because indexing has a syntax.
For a function's return type there is no such syntax — so TypeScript lets you **name
the piece** during the match:

```ts
type Ret<F> = F extends (...args: never[]) => infer R ? R : never;
```

Read it as: "if `F` matches the shape *a function returning something*, call that
something `R`, and the answer is `R`." That is exactly the library's `ReturnType`.

## The same move, other shapes

```ts
type Args<F>   = F extends (...args: infer A) => unknown ? A : never;   // Parameters
type Unwrap<P> = P extends Promise<infer V> ? V : P;                  // one level of Awaited
type Item<T>   = T extends readonly (infer E)[] ? E : never;          // ElementOf, again
type First<F>  = F extends (first: infer A, ...rest: never[]) => unknown ? A : never;
```

`infer` may only appear inside an `extends` clause of a conditional type, and the
name it introduces only exists in the **true** branch.

## Why `never[]` for the parameters

`(...args: never[]) => infer R` matches **every** function, because parameter types
are checked *contravariantly* (week 12): a function accepting anything can stand in
where one accepting nothing is expected. `any[]` would work too; `unknown[]` would
**not** match a function whose parameter is, say, `string`. Week 30 goes deeper into
exactly where `infer` can sit.

> ⚠️ **Common mistakes:** `infer` outside an extends clause; using the inferred
> name in the false branch; and `unknown[]` for the parameters, which rejects most
> real functions.
""",
            warmup=[
                _q("`infer R` introduces R…",
                   ["globally", "inside a conditional's extends clause, usable in the true branch", "as a value",
                    "anywhere"], 1,
                   "Only there."),
                _q("`F extends (...args: never[]) => infer R ? R : never` rebuilds…",
                   ["Parameters", "ReturnType", "Awaited", "InstanceType"], 1,
                   "The return type."),
                _q("`Unwrap<Promise<number>>` with `P extends Promise<infer V> ? V : P` is…",
                   ["Promise<number>", "number", "never", "unknown"], 1,
                   "One level unwrapped."),
                _q("Parameters are matched with `never[]` rather than `unknown[]` because…",
                   ["style", "parameter checks are contravariant, so never[] matches every function", "speed",
                    "unknown is banned"], 1,
                   "Week 12."),
            ],
            exercises=[
                _types("tscourse-w29-if-t1", "ReturnType, by hand",
                       "Write `Ret<F>` with `infer`. `ReturnType` is banned.",
                       'type Ret<F> = F extends (...args: never[]) => infer R ? R : never;\n',
                       'F extends (...args: never[]) => infer R ? R : never',
                       """
type _1 = Expect<Equal<Ret<() => string>, string>>;
type _2 = Expect<Equal<Ret<(a: number, b: string) => boolean>, boolean>>;
type _3 = Expect<Equal<Ret<string>, never>>;
declare function sample(x: number): { ok: true };
type _4 = Expect<Equal<Ret<typeof sample>, ReturnType<typeof sample>>>;
""",
                       hints=["Match the shape 'a function returning something', and name the something.",
                              "Use never[] for the parameters so every function matches.",
                              "F extends (...args: never[]) => infer R ? R : never"],
                       difficulty="Medium", forbid=["ReturnType<"]),
                _types("tscourse-w29-if-t2", "Parameters, by hand",
                       "Write `Args<F>`: the tuple of a function's parameter types. `Parameters` is banned.",
                       'type Args<F> = F extends (...args: infer A) => unknown ? A : never;\n',
                       'F extends (...args: infer A) => unknown ? A : never',
                       """
type _1 = Expect<Equal<Args<(a: number, b: string) => void>, [a: number, b: string]>>;
type _2 = Expect<Equal<Args<() => void>, []>>;
type _3 = Expect<Equal<Args<number>, never>>;
""",
                       hints=["This time the inferred part is the whole rest-parameter tuple.",
                              "F extends (...args: infer A) => unknown ? A : never"],
                       difficulty="Medium", forbid=["Parameters<"]),
                _types("tscourse-w29-if-t3", "What a promise holds",
                       "Write `Unwrap<P>`: the value type of a Promise, or P itself if it is not one.",
                       'type Unwrap<P> = P extends Promise<infer V> ? V : P;\n',
                       'P extends Promise<infer V> ? V : P',
                       """
type _1 = Expect<Equal<Unwrap<Promise<number>>, number>>;
type _2 = Expect<Equal<Unwrap<string>, string>>;
type _3 = Expect<Equal<Unwrap<Promise<string[]>>, string[]>>;
""",
                       hints=["Promise<something> — name the something.",
                              "P extends Promise<infer V> ? V : P"],
                       difficulty="Easy", forbid=["Awaited<"]),
                _types("tscourse-w29-if-t4", "The first argument",
                       "Write `First<F>`: the type of a function's first parameter, or never if it has none.",
                       'type First<F> = F extends (first: infer A, ...rest: never[]) => unknown ? A : never;\n',
                       'F extends (first: infer A, ...rest: never[]) => unknown ? A : never',
                       """
type _1 = Expect<Equal<First<(a: string, b: number) => void>, string>>;
type _2 = Expect<Equal<First<(x: boolean) => void>, boolean>>;
""",
                       hints=["Name the first parameter; accept any rest after it.",
                              "F extends (first: infer A, ...rest: never[]) => unknown ? A : never"],
                       difficulty="Hard"),
                _types("tscourse-w29-if-t5", "Unwrap all the way",
                       "Write `DeepUnwrap<P>`: unwrap nested promises until a non-promise remains — a recursive conditional.",
                       'type DeepUnwrap<P> = P extends Promise<infer V> ? DeepUnwrap<V> : P;\n',
                       'P extends Promise<infer V> ? DeepUnwrap<V> : P',
                       """
type _1 = Expect<Equal<DeepUnwrap<Promise<Promise<number>>>, number>>;
type _2 = Expect<Equal<DeepUnwrap<Promise<string>>, string>>;
type _3 = Expect<Equal<DeepUnwrap<boolean>, boolean>>;
""",
                       hints=["The true branch can call the type again on what it found.",
                              "P extends Promise<infer V> ? DeepUnwrap<V> : P"],
                       difficulty="Medium", forbid=["Awaited<"]),
            ],
            quiz=[
                _q("The library's `Awaited` is essentially…",
                   ["Unwrap", "DeepUnwrap, with care for thenables", "ReturnType", "Promise"], 1,
                   "Recursive unwrapping."),
                _q("Can `infer` appear in a mapped type on its own?",
                   ["yes", "no — only inside a conditional's extends clause", "only with keyof", "only in week 30"], 1,
                   "Pattern matching needs a condition."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w29-mapped", "A loop over keys",
            "Mapped types — and Partial, Readonly and Required in one line each.",
            """
```ts
type Optional<T> = { [K in keyof T]?: T[K] };
```

Read it as a `for` loop: *for each key `K` in `keyof T`, make a property `K`,
optional, with the type `T[K]`*. That is `Partial<T>`, exactly — the library's
definition is this line.

## Modifiers

A mapped property can add or remove the two property modifiers:

```ts
type Frozen<T>  = { readonly [K in keyof T]: T[K] };     // Readonly
type Needed<T>  = { [K in keyof T]-?: T[K] };            // Required — REMOVE ?
type Mutable<T> = { -readonly [K in keyof T]: T[K] };    // remove readonly
```

`+` is the default and rarely written; `-` is the only way to take a modifier
away. There is no built-in `Mutable`, which is a good reason to be able to write it.

## Homomorphic: modifiers carry over

A mapped type over `keyof T` keeps T's own `readonly` and `?` unless told otherwise.
So `Optional<Entry>` leaves `id` readonly, and `Needed<Entry>` leaves it readonly
too — only the modifier you mention changes.

## Changing the value type

The right-hand side can be anything computed from `K` or `T[K]`:

```ts
type Flags<T>    = { [K in keyof T]: boolean };
type Nullable<T> = { [K in keyof T]: T[K] | null };
```

> ⚠️ **Common mistakes:** `?:` when you meant `-?:`; forgetting that the modifiers
> are inherited; and writing `[K in T]` when T is an object rather than a union of
> keys.
""",
            warmup=[
                _q("`[K in keyof T]` loops over…",
                   ["values", "T's keys", "numbers", "T's methods only"], 1,
                   "A for loop over keys."),
                _q("Partial is…",
                   ["{ [K in keyof T]-?: T[K] }", "{ [K in keyof T]?: T[K] }", "{ readonly [K in keyof T]: T[K] }",
                    "{ [K in T]: K }"], 1,
                   "Add ?."),
                _q("To remove readonly you write…",
                   ["readonly-", "-readonly", "!readonly", "mutable"], 1,
                   "A minus before the modifier."),
                _q("A homomorphic mapped type…",
                   ["drops modifiers", "keeps T's readonly and ? unless told otherwise", "is recursive", "is a union"], 1,
                   "They carry over."),
            ],
            exercises=[
                _types("tscourse-w29-mp-t1", "Partial, by hand",
                       "Write `Optional<T>`. `Partial` is banned.",
                       _ENTRY + 'type Optional<T> = { [K in keyof T]?: T[K] };\n',
                       '{ [K in keyof T]?: T[K] }',
                       """
type _1 = Expect<Equal<Optional<Entry>, Partial<Entry>>>;
type _2 = Expect<Equal<Optional<{ a: number }>, { a?: number }>>;
""",
                       hints=["Loop over every key, and add the optional modifier.",
                              "{ [K in keyof T]?: T[K] }"],
                       difficulty="Easy", forbid=["Partial<"]),
                _types("tscourse-w29-mp-t2", "Readonly, by hand",
                       "Write `Frozen<T>`. `Readonly` is banned.",
                       _ENTRY + 'type Frozen<T> = { readonly [K in keyof T]: T[K] };\n',
                       '{ readonly [K in keyof T]: T[K] }',
                       """
type _1 = Expect<Equal<Frozen<Entry>, Readonly<Entry>>>;
type _2 = Expect<Equal<Frozen<{ a: number }>, { readonly a: number }>>;
""",
                       hints=["The modifier goes before the bracket.",
                              "{ readonly [K in keyof T]: T[K] }"],
                       difficulty="Easy", forbid=["Readonly<"]),
                _types("tscourse-w29-mp-t3", "Required, by hand",
                       "Write `Needed<T>`, removing optionality from every key. `Required` is banned.",
                       _ENTRY + 'type Needed<T> = { [K in keyof T]-?: T[K] };\n',
                       '{ [K in keyof T]-?: T[K] }',
                       """
type _1 = Expect<Equal<Needed<Entry>, Required<Entry>>>;
type _2 = Expect<Equal<Needed<{ a?: number }>, { a: number }>>;
""",
                       hints=["A minus in front of the ? removes it.",
                              "{ [K in keyof T]-?: T[K] }"],
                       difficulty="Medium", forbid=["Required<"]),
                _types("tscourse-w29-mp-t4", "The one the library lacks",
                       "Write `Mutable<T>`, removing readonly from every key.",
                       _ENTRY + 'type Mutable<T> = { -readonly [K in keyof T]: T[K] };\n',
                       '{ -readonly [K in keyof T]: T[K] }',
                       """
type _1 = Expect<Equal<Mutable<{ readonly a: number; readonly b: string }>, { a: number; b: string }>>;
type _2 = Expect<Equal<Mutable<Entry>, { id: string; desc: string; tag?: string; cents: number }>>;
""",
                       hints=["-readonly, before the bracket.",
                              "{ -readonly [K in keyof T]: T[K] }"],
                       difficulty="Medium"),
                _types("tscourse-w29-mp-t5", "Every value nullable",
                       "Write `Nullable<T>`: the same keys, each value also allowing null.",
                       _ENTRY + 'type Nullable<T> = { [K in keyof T]: T[K] | null };\n',
                       '{ [K in keyof T]: T[K] | null }',
                       """
type _1 = Expect<Equal<Nullable<{ a: number; b: string }>, { a: number | null; b: string | null }>>;
type _2 = Expect<Equal<Nullable<{ readonly x: boolean }>, { readonly x: boolean | null }>>;
""",
                       hints=["The value side can be any type expression over T[K].",
                              "{ [K in keyof T]: T[K] | null }"],
                       difficulty="Easy"),
            ],
            quiz=[
                _q("`Needed<Entry>` keeps `id` readonly because…",
                   ["a bug", "mapped types over keyof T inherit modifiers not mentioned", "id is required", "of -?"], 1,
                   "Homomorphic."),
                _q("`[K in \"a\" | \"b\"]: number` produces…",
                   ["a union", "{ a: number; b: number }", "number[]", "never"], 1,
                   "Any union of keys can be looped over."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w29-remap", "Choosing and renaming keys",
            "Pick, Omit, filtering by value type — and the first recursive mapped type.",
            """
## Pick loops over a subset of keys

```ts
type Keep<T, K extends keyof T> = { [P in K]: T[P] };
```

The constraint `K extends keyof T` is what week 14 met as **TS2344** when a key was
misspelled — now you can see where it comes from.

## Omit needs `as`

Omit keeps every key *except* some. A mapped type can **remap** each key with `as`,
and remapping a key to `never` **drops** it:

```ts
type Drop<T, K extends PropertyKey> = { [P in keyof T as P extends K ? never : P]: T[P] };
```

Note the constraint: `PropertyKey`, not `keyof T`. The library's `Omit` is
deliberately loose — week 14 found that a misspelled key omits nothing, silently —
and this version reproduces that exactly.

## Filtering by value type

`as` can test the **value**, too:

```ts
type NumbersOf<T> = { [K in keyof T as T[K] extends number ? K : never]: T[K] };
```

`NumbersOf<Entry>` is `{ cents: number }` — a type the library cannot express.

## Recursion

A mapped type can refer to itself. `Frozen` makes the top level readonly; this makes
every level readonly:

```ts
type DeepReadonly<T> = T extends object
  ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
  : T;
```

The conditional is the base case — a primitive is returned unchanged — exactly as
week 25's recursions needed one. Arrays come out as `readonly` arrays, because a
mapped type over an array type produces an array type.

> ⚠️ **Common mistakes:** `keyof T` as Omit's constraint (stricter than the
> library); `as never` meaning "keep"; and a recursive type with no base case,
> which the compiler reports as excessively deep.
""",
            warmup=[
                _q("Pick loops over…",
                   ["keyof T", "the chosen keys K", "values", "never"], 1,
                   "[P in K]."),
                _q("Remapping a key to never…",
                   ["keeps it", "drops it", "is an error", "makes it optional"], 1,
                   "How Omit works."),
                _q("The library's Omit constrains K to…",
                   ["keyof T", "PropertyKey — anything, which is why a typo omits nothing", "string", "never"], 1,
                   "Week 14's silent failure."),
                _q("DeepReadonly's base case is…",
                   ["an array", "a non-object type, returned unchanged", "never", "a function"], 1,
                   "The false branch."),
            ],
            exercises=[
                _types("tscourse-w29-rm-t1", "Pick, by hand",
                       "Write `Keep<T, K>`. `Pick` is banned.",
                       _ENTRY + 'type Keep<T, K extends keyof T> = { [P in K]: T[P] };\n',
                       '{ [P in K]: T[P] }',
                       """
type _1 = Expect<Equal<Keep<Entry, "id" | "tag">, Pick<Entry, "id" | "tag">>>;
type _2 = Expect<Equal<Keep<{ a: 1; b: 2 }, "a">, { a: 1 }>>;
""",
                       hints=["Loop over the chosen keys only.",
                              "{ [P in K]: T[P] }"],
                       difficulty="Medium", forbid=["Pick<"]),
                _types("tscourse-w29-rm-t2", "Omit, by hand",
                       "Write `Drop<T, K>` with key remapping. `Omit`, `Pick` and `Exclude` are all banned.",
                       _ENTRY + 'type Drop<T, K extends PropertyKey> = { [P in keyof T as P extends K ? never : P]: T[P] };\n',
                       '{ [P in keyof T as P extends K ? never : P]: T[P] }',
                       """
type _1 = Expect<Equal<Drop<Entry, "desc">, Omit<Entry, "desc">>>;
type _2 = Expect<Equal<Drop<{ a: 1; b: 2; c: 3 }, "a" | "c">, { b: 2 }>>;
""",
                       hints=["Loop over every key, and remap the unwanted ones to never.",
                              "[P in keyof T as P extends K ? never : P]"],
                       difficulty="Hard", forbid=["Omit<", "Pick<", "Exclude<"]),
                _types("tscourse-w29-rm-t3", "Only the numbers",
                       "Write `NumbersOf<T>`: only the keys whose values are numbers.",
                       _ENTRY + 'type NumbersOf<T> = { [K in keyof T as T[K] extends number ? K : never]: T[K] };\n',
                       '{ [K in keyof T as T[K] extends number ? K : never]: T[K] }',
                       """
type _1 = Expect<Equal<NumbersOf<Entry>, { cents: number }>>;
type _2 = Expect<Equal<NumbersOf<{ a: 1; b: "x"; c: 2 }>, { a: 1; c: 2 }>>;
""",
                       hints=["Test the value type in the `as` clause.",
                              "as T[K] extends number ? K : never"],
                       difficulty="Hard"),
                _types("tscourse-w29-rm-t4", "Readonly all the way down",
                       "Write `DeepReadonly<T>`: readonly at every level, arrays included.",
                       'type DeepReadonly<T> = T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } : T;\n',
                       'T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } : T',
                       """
type _1 = Expect<Equal<DeepReadonly<{ a: { b: number[] } }>, { readonly a: { readonly b: readonly number[] } }>>;
type _2 = Expect<Equal<DeepReadonly<string>, string>>;
""",
                       hints=["A primitive is the base case, returned as it is.",
                              "An object is mapped, and each value goes through DeepReadonly again."],
                       difficulty="Hard"),
                _diagnose("tscourse-w29-rm-d1", "The key that is not there",
                          "TS2344: Type '\"desc\" | \"tagg\"' does not satisfy the constraint 'keyof Entry'.",
                          'interface Entry {\n'
                          '  desc: string;\n'
                          '  tag: string;\n'
                          '  cents: number;\n}\n'
                          'type Keep<T, K extends keyof T> = { [P in K]: T[P] };\n'
                          'type Summary = Keep<Entry, "desc" | "tagg">;\n'
                          'const s: Summary = { desc: "coffee", tagg: "food" };\n'
                          'console.log(`${s.desc} ${s.tagg}`);\n',
                          'interface Entry {\n'
                          '  desc: string;\n'
                          '  tag: string;\n'
                          '  cents: number;\n}\n'
                          'type Keep<T, K extends keyof T> = { [P in K]: T[P] };\n'
                          'type Summary = Keep<Entry, "desc" | "tag">;\n'
                          'const s: Summary = { desc: "coffee", tag: "food" };\n'
                          'console.log(`${s.desc} ${s.tag}`);\n',
                          [("", "coffee food")],
                          hints=["The constraint `K extends keyof T` checked every key you passed.",
                                 "One of them is not a key of Entry.",
                                 "It is spelled tag."],
                          difficulty="Easy"),
            ],
            quiz=[
                _q("`Drop<Entry, \"descc\">` (a typo) gives…",
                   ["an error", "Entry unchanged — nothing matched, nothing dropped", "never", "{}"], 1,
                   "Loose, like the library."),
                _q("A recursive type with no base case…",
                   ["works", "is reported as excessively deep", "is any", "is never"], 1,
                   "Week 25, at the type level."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w29-runtime", "Types that follow values",
            "A computed type on running code — graded on the output AND on the types.",
            """
A mapped type earns its place when a **function** returns it. Then the caller gets a
precise type computed from their own argument:

```ts
function totals<T extends Record<string, readonly number[]>>(groups: T): Totals<T> {
  const out = {} as Totals<T>;
  for (const k of Object.keys(groups) as (keyof T)[]) {
    out[k] = (groups[k] ?? []).reduce((a, b) => a + b, 0);
  }
  return out;
}
type Totals<T> = { [K in keyof T]: number };
```

Call it with `{ food: [3, 4], rent: [900] }` and the result's type is
`{ food: number; rent: number }` — not a vague `Record<string, number>`.

## The casts are at the edge, on purpose

`{} as Totals<T>` and `Object.keys(...) as (keyof T)[]` are claims the checker cannot
verify (week 15): an empty object is not yet a `Totals<T>`, and `Object.keys` returns
`string[]` because an object may have more keys at run time than its type admits.
Keep such casts **inside** the implementation, where one careful reading covers them,
and give callers the precise type.

## A type is not a runtime filter

Week 14 found `Omit` leaking a field at run time, because it is only a type. The
same is true here: a function typed to return `Keep<T, K>` must *build* an object
with only those keys. Spread the whole input and cast, and the type says one thing
while `Object.keys` prints another. That is this lesson's `fix`.

> ⚠️ **Common mistakes:** casting the *result* rather than building it; letting a
> cast leak into the public signature; and believing a mapped type removes anything
> at run time.
""",
            warmup=[
                _q("A function returning `Totals<T>` gives its caller…",
                   ["Record<string, number>", "a type computed from their own argument's keys", "any", "unknown"], 1,
                   "The point of the exercise."),
                _q("`Object.keys(obj)` is typed `string[]` because…",
                   ["a bug", "the object may have more keys at run time than its type lists", "keys are strings",
                    "of symbols"], 1,
                   "Structural typing."),
                _q("A function typed as returning `Keep<T, K>` that returns `{ ...obj }`…",
                   ["removes the extra keys", "still carries them at run time", "fails to compile", "throws"], 1,
                   "Types do not filter."),
                _q("Casts in a typed library belong…",
                   ["in the public signature", "inside the implementation, where they can be checked by reading", "nowhere",
                    "in the caller"], 1,
                   "Precise outside, careful inside."),
            ],
            exercises=[
                _design("tscourse-w29-rt-des1", "Design the totals type",
                        "`totals` is written; declare the type it returns: the SAME keys as its argument, each "
                        "mapped to a number. A `Record<string, number>` would lose the keys and fail the checks.",
                        'type Totals<T> = { [K in keyof T]: number };\n'
                        'function totals<T extends Record<string, readonly number[]>>(groups: T): Totals<T> {\n'
                        '  const out = {} as Totals<T>;\n'
                        '  for (const k of Object.keys(groups) as (keyof T)[]) {\n'
                        '    out[k] = (groups[k] ?? []).reduce((a, b) => a + b, 0);\n  }\n'
                        '  return out;\n}\n'
                        'const t = totals({ food: [325, 450], rent: [90000] });\n'
                        'console.log(`${t.food} ${t.rent}`);\n',
                        'type Totals<T> = { [K in keyof T]: number };',
                        'type _1 = Expect<Equal<typeof t, { food: number; rent: number }>>;\n'
                        'type _2 = Expect<Equal<Totals<{ a: number[] }>, { a: number }>>;\n',
                        [("", "775 90000")],
                        hints=["Keep every key; change every value's type.",
                               "type Totals<T> = { [K in keyof T]: number };"],
                        difficulty="Medium"),
                _ex("tscourse-w29-rt-1", "Build only the chosen keys",
                    "Implement `pick` so the object it returns really has only the requested keys.",
                    'type Keep<T, K extends keyof T> = { [P in K]: T[P] };\n'
                    'function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Keep<T, K> {\n'
                    '  const out = {} as Keep<T, K>;\n'
                    '  for (const k of keys) {\n'
                    '    out[k] = obj[k];\n  }\n'
                    '  return out;\n}\n'
                    'const entry = { id: "e1", desc: "coffee", cents: 325, secret: "x" };\n'
                    'const view = pick(entry, ["desc", "cents"]);\n'
                    'console.log(`${Object.keys(view).join(",")} ${view.desc} ${view.cents}`);\n',
                    '  for (const k of keys) {\n'
                    '    out[k] = obj[k];\n  }',
                    [("", "desc,cents coffee 325")],
                    hints=["Copy one property per requested key — nothing else.",
                           "for (const k of keys) { out[k] = obj[k]; }"],
                    difficulty="Medium"),
                _ex("tscourse-w29-rt-2", "Keys, typed",
                    "Return an object's keys typed as its own key union, with the one cast inside the function.",
                    'function keysOf<T extends object>(obj: T): (keyof T)[] {\n'
                    '  return Object.keys(obj) as (keyof T)[];\n}\n'
                    'const limits = { food: 400, fun: 100 };\n'
                    'for (const k of keysOf(limits)) {\n'
                    '  console.log(`${k}=${limits[k]}`);\n}\n',
                    '  return Object.keys(obj) as (keyof T)[];',
                    [("", "food=400\nfun=100")],
                    hints=["Object.keys returns string[]; the cast narrows it to T's keys.",
                           "Write return Object.keys(obj) as (keyof T)[];"],
                    difficulty="Easy"),
                _fix("tscourse-w29-rt-fix1", "Fix the pick that returned everything",
                     "`view` is typed as having only `desc` and `cents`, and `Object.keys(view)` prints all four keys — including `secret`. The implementation spreads the whole input and casts it; the type promises a filter the code never performs.",
                     'type Keep<T, K extends keyof T> = { [P in K]: T[P] };\n'
                     'function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Keep<T, K> {\n'
                     '  return { ...obj } as Keep<T, K>;\n}\n'
                     'const entry = { id: "e1", desc: "coffee", cents: 325, secret: "x" };\n'
                     'const view = pick(entry, ["desc", "cents"]);\n'
                     'console.log(Object.keys(view).join(","));\n',
                     'type Keep<T, K extends keyof T> = { [P in K]: T[P] };\n'
                     'function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Keep<T, K> {\n'
                     '  const out = {} as Keep<T, K>;\n'
                     '  for (const k of keys) {\n'
                     '    out[k] = obj[k];\n  }\n'
                     '  return out;\n}\n'
                     'const entry = { id: "e1", desc: "coffee", cents: 325, secret: "x" };\n'
                     'const view = pick(entry, ["desc", "cents"]);\n'
                     'console.log(Object.keys(view).join(","));\n',
                     [("", "desc,cents")],
                     hints=["Week 14's Omit leak, again: a type never removes anything at run time.",
                            "`keys` is never even read.",
                            "Build a new object from the requested keys only."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is `{} as Totals<T>` acceptable here?",
                   ["it never is", "it is inside the implementation and every key is filled before return",
                    "casts are free", "Totals is optional"], 1,
                   "A cast is a claim; keep it where it can be checked by reading."),
                _q("After `pick(entry, [\"desc\"])` the variable's type has…",
                   ["all keys", "only desc", "no keys", "desc and id"], 1,
                   "Computed from the call."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w29-library", "Library #1: the config module",
            "DeepPartial overrides, a typed deep merge, and a frozen DeepReadonly result.",
            """
The last four weeks build a small typed library, one module a week. The first is
the kind every application has: **configuration**.

* **Defaults** — a complete, typed object.
* **Overrides** — any subset, at any depth: `{ "db": { "port": 5433 } }`. Its type is
  `DeepPartial<Config>`: every key optional, recursively.
* **The result** — defaults with overrides merged in, `DeepReadonly<Config>` to the
  compiler **and** `Object.freeze`d at every level at run time, so neither a typo nor
  a cast can change it.

## DeepPartial

```ts
type DeepPartial<T> = T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;
```

Lesson 5's DeepReadonly with `?` instead of `readonly`.

## The merge

```ts
function mergeDeep<T>(base: T, patch: DeepPartial<T>): T {
  if (!isRecord(base) || !isRecord(patch)) {
    return (patch === undefined ? base : patch) as T;      // a leaf: the patch wins
  }
  const out: Record<string, unknown> = { ...base };
  for (const [k, v] of Object.entries(patch)) {
    if (v !== undefined) { out[k] = mergeDeep<unknown>(base[k], v); }
  }
  return out as T;
}
```

One recursion, one type guard (`isRecord`, week 15's user-defined guard), and two
casts — both inside, both at the point where the code has just established what the
cast claims.

## Freezing to match the type

`DeepReadonly` is a promise to the compiler; `Object.freeze` is enforcement at run
time, and it is shallow (week 13). A recursive `deepFreeze` makes the two agree:

```ts
function deepFreeze<T>(value: T): DeepReadonly<T> {
  if (isRecord(value)) {
    for (const v of Object.values(value)) { deepFreeze(v); }
    Object.freeze(value);
  }
  return value as DeepReadonly<T>;
}
```

## Testing a rejection

The capstone's checker contains, inside a function that is never called:

```ts
// @ts-expect-error — the config is read-only
cfg.db.port = 1;
```

If your result type were not deeply read-only, that line would compile, the
directive would be unused, and the check would fail with TS2578. The test **proves
the type rejects the write** — and because the function is never called, it never
runs, so it proves it without touching the frozen object.
""",
            warmup=[
                _q("`DeepPartial<{ db: { port: number } }>` accepts…",
                   ["only the full object", "{}, { db: {} } and { db: { port: 1 } }", "only { db }", "nothing"], 1,
                   "Optional at every level."),
                _q("`Object.freeze` is…",
                   ["deep", "shallow — nested objects stay writable", "a type", "recursive by default"], 1,
                   "Week 13."),
                _q("The `@ts-expect-error` write sits in an uncalled function so that…",
                   ["it is hidden", "it is type-checked but never executed", "it runs twice", "it is skipped"], 1,
                   "Proves the rejection without running it."),
                _q("In `mergeDeep`, a leaf is decided by…",
                   ["the key name", "the patch's value, if present", "the default always", "a merge"], 1,
                   "The override wins."),
            ],
            exercises=[
                _types("tscourse-w29-lb-t1", "Partial all the way down",
                       "Write `DeepPartial<T>`: every key optional, at every level.",
                       'type DeepPartial<T> = T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;\n',
                       'T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T',
                       """
interface Config { name: string; db: { host: string; port: number } }
const _a: DeepPartial<Config> = {};
const _b: DeepPartial<Config> = { db: { port: 5433 } };
type _1 = Expect<Equal<DeepPartial<{ a: { b: number } }>, { a?: { b?: number } }>>;
// @ts-expect-error — a wrong type is still wrong, however deep
const _c: DeepPartial<Config> = { db: { port: "5433" } };
""",
                       hints=["DeepReadonly's shape, with ? in place of readonly.",
                              "T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T"],
                       difficulty="Medium"),
                _ex("tscourse-w29-lb-1", "Freeze every level",
                    "Freeze the children before the object itself, recursively.",
                    _DEEP +
                    'function deepFreeze<T>(value: T): DeepReadonly<T> {\n'
                    '  if (isRecord(value)) {\n'
                    '    for (const v of Object.values(value)) {\n'
                    '      deepFreeze(v);\n    }\n'
                    '    Object.freeze(value);\n  }\n'
                    '  return value as DeepReadonly<T>;\n}\n'
                    'const cfg = deepFreeze({ name: "app", db: { host: "localhost", port: 5432 } });\n'
                    'console.log(`${Object.isFrozen(cfg)} ${Object.isFrozen(cfg.db)}`);\n',
                    '    for (const v of Object.values(value)) {\n'
                    '      deepFreeze(v);\n    }',
                    [("", "true true")],
                    hints=["Object.freeze alone would leave cfg.db writable.",
                           "Recurse into every value before freezing the object."],
                    difficulty="Medium"),
                _ex("tscourse-w29-lb-2", "Merge one level down",
                    "Recurse into each overriding key, so a nested override keeps its siblings.",
                    _DEEP +
                    'function mergeDeep<T>(base: T, patch: DeepPartial<T>): T {\n'
                    '  if (!isRecord(base) || !isRecord(patch)) {\n'
                    '    return (patch === undefined ? base : patch) as T;\n  }\n'
                    '  const out: Record<string, unknown> = { ...base };\n'
                    '  for (const [k, v] of Object.entries(patch)) {\n'
                    '    if (v !== undefined) {\n'
                    '      out[k] = mergeDeep<unknown>(base[k], v);\n    }\n  }\n'
                    '  return out as T;\n}\n'
                    'const merged = mergeDeep({ db: { host: "localhost", port: 5432 }, debug: false }, { db: { port: 5433 } });\n'
                    'console.log(JSON.stringify(merged));\n',
                    '      out[k] = mergeDeep<unknown>(base[k], v);',
                    [("", '{"db":{"host":"localhost","port":5433},"debug":false}')],
                    hints=["Replacing out[k] with v outright would lose db.host.",
                           "Merge the base's value for k with the patch's value for k.",
                           "Write out[k] = mergeDeep<unknown>(base[k], v);"],
                    difficulty="Hard"),
                _fix("tscourse-w29-lb-fix1", "Fix the merge that lost the siblings",
                     "Overriding only `db.port` also wiped out `db.host`: this prints `{\"db\":{\"port\":5433},\"debug\":false}`. The merge is shallow — it replaces the whole `db` object with the patch's `db` instead of merging inside it.",
                     _DEEP +
                     'function mergeDeep<T>(base: T, patch: DeepPartial<T>): T {\n'
                     '  return { ...base, ...patch } as T;\n}\n'
                     'const merged = mergeDeep({ db: { host: "localhost", port: 5432 }, debug: false }, { db: { port: 5433 } });\n'
                     'console.log(JSON.stringify(merged));\n',
                     _DEEP +
                     'function mergeDeep<T>(base: T, patch: DeepPartial<T>): T {\n'
                     '  if (!isRecord(base) || !isRecord(patch)) {\n'
                     '    return (patch === undefined ? base : patch) as T;\n  }\n'
                     '  const out: Record<string, unknown> = { ...base };\n'
                     '  for (const [k, v] of Object.entries(patch)) {\n'
                     '    if (v !== undefined) {\n'
                     '      out[k] = mergeDeep<unknown>(base[k], v);\n    }\n  }\n'
                     '  return out as T;\n}\n'
                     'const merged = mergeDeep({ db: { host: "localhost", port: 5432 }, debug: false }, { db: { port: 5433 } });\n'
                     'console.log(JSON.stringify(merged));\n',
                     [("", '{"db":{"host":"localhost","port":5433},"debug":false}')],
                     hints=["A spread is one level deep.",
                            "When both sides of a key are objects, merge them — recursively.",
                            "Walk the patch's entries and recurse for each."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("Why does `mergeDeep` call itself with `<unknown>`?",
                   ["speed", "below the top level the precise type is not tracked; the public signature carries it",
                    "unknown is required", "to disable checks"], 1,
                   "Precise outside, careful inside."),
                _q("DeepReadonly without deepFreeze…",
                   ["is enough", "stops typed writes but not a cast, or plain JavaScript", "freezes the object", "is an error"], 1,
                   "The type is a promise; freezing enforces it."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Library #1 — the config module",
        """
The first module of the typed library: load configuration.

Defaults (write these exactly):

```ts
interface Config {
  name: string;
  db: { host: string; port: number };
  debug: boolean;
}
const DEFAULTS: Config = { name: "app", db: { host: "localhost", port: 5432 }, debug: false };
```

Input: one JSON object of overrides on stdin — any subset, at any depth.

```
{"db":{"port":5433}}
```

```
{"name":"app","db":{"host":"localhost","port":5433},"debug":false}
frozen true true
```

**What to build:**

* `DeepPartial<T>` and `DeepReadonly<T>`, recursive, as in lessons 5 and 7.
* `mergeDeep<T>(base: T, patch: DeepPartial<T>): T` — a nested override keeps its
  siblings.
* `deepFreeze<T>(value: T): DeepReadonly<T>` — freezes every level.
* `configure(patch: DeepPartial<Config>): DeepReadonly<Config>`, which merges the
  overrides into the defaults and freezes the result.
* Print `JSON.stringify` of the result, then `frozen` and whether the result and
  `result.db` are frozen.

**How it is checked:** on stdout, and by type assertions in the hidden harness —
that `configure` returns exactly `DeepReadonly<Config>`, that `DeepPartial<Config>`
accepts `{ db: {} }`, and, inside a function that never runs,
`// @ts-expect-error` on a write to `cfg.db.port`. If the result type is not deeply
read-only, that directive is unused and the check fails.

`JSON.parse` hands back `any` (week 15); this module trusts its input's shape and
says so with one cast at the boundary. Week 15's validation would go there in a real
system.
""",
        _mk("tscourse-w29-capstone", "Library #1 — the config module",
            "Merge JSON overrides into typed defaults, freeze the result at every level, and "
            "type it DeepReadonly — checked on stdout and by type assertions.",
            _FS + _DEEP +
            'interface Config {\n'
            '  name: string;\n'
            '  db: { host: string; port: number };\n'
            '  debug: boolean;\n}\n'
            'const DEFAULTS: Config = { name: "app", db: { host: "localhost", port: 5432 }, debug: false };\n'
            'function mergeDeep<T>(base: T, patch: DeepPartial<T>): T {\n'
            '  if (!isRecord(base) || !isRecord(patch)) {\n'
            '    return (patch === undefined ? base : patch) as T;\n  }\n'
            '  const out: Record<string, unknown> = { ...base };\n'
            '  for (const [k, v] of Object.entries(patch)) {\n'
            '    if (v !== undefined) {\n'
            '      out[k] = mergeDeep<unknown>(base[k], v);\n    }\n  }\n'
            '  return out as T;\n}\n'
            'function deepFreeze<T>(value: T): DeepReadonly<T> {\n'
            '  if (isRecord(value)) {\n'
            '    for (const v of Object.values(value)) {\n'
            '      deepFreeze(v);\n    }\n'
            '    Object.freeze(value);\n  }\n'
            '  return value as DeepReadonly<T>;\n}\n'
            'function configure(patch: DeepPartial<Config>): DeepReadonly<Config> {\n'
            '  return deepFreeze(mergeDeep(DEFAULTS, patch));\n}\n'
            'const cfg = configure(JSON.parse(fs.readFileSync(0, "utf8")) as DeepPartial<Config>);\n'
            'console.log(JSON.stringify(cfg));\n'
            'console.log(`frozen ${Object.isFrozen(cfg)} ${Object.isFrozen(cfg.db)}`);\n',
            [('{"db":{"port":5433}}', '{"name":"app","db":{"host":"localhost","port":5433},"debug":false}\nfrozen true true'),
             ('{}', '{"name":"app","db":{"host":"localhost","port":5432},"debug":false}\nfrozen true true'),
             ('{"debug":true,"db":{"host":"db.internal"},"name":"api"}',
              '{"name":"api","db":{"host":"db.internal","port":5432},"debug":true}\nfrozen true true')],
            ["Write the two recursive types first; the functions follow their shapes.",
             "mergeDeep recurses only when BOTH sides are plain objects; otherwise the patch's value wins if present.",
             "deepFreeze freezes the children before the parent.",
             "configure is one line: freeze the merge.",
             "One cast at the JSON boundary: `as DeepPartial<Config>`."],
            "Hard", "challenge",
            blank='function mergeDeep<T>(base: T, patch: DeepPartial<T>): T {\n'
                  '  if (!isRecord(base) || !isRecord(patch)) {\n'
                  '    return (patch === undefined ? base : patch) as T;\n  }\n'
                  '  const out: Record<string, unknown> = { ...base };\n'
                  '  for (const [k, v] of Object.entries(patch)) {\n'
                  '    if (v !== undefined) {\n'
                  '      out[k] = mergeDeep<unknown>(base[k], v);\n    }\n  }\n'
                  '  return out as T;\n}\n'
                  'function deepFreeze<T>(value: T): DeepReadonly<T> {\n'
                  '  if (isRecord(value)) {\n'
                  '    for (const v of Object.values(value)) {\n'
                  '      deepFreeze(v);\n    }\n'
                  '    Object.freeze(value);\n  }\n'
                  '  return value as DeepReadonly<T>;\n}\n'
                  'function configure(patch: DeepPartial<Config>): DeepReadonly<Config> {\n'
                  '  return deepFreeze(mergeDeep(DEFAULTS, patch));\n}',
            harness=_TYPE_PRELUDE +
                    'type _1 = Expect<Equal<ReturnType<typeof configure>, DeepReadonly<Config>>>;\n'
                    'const _partial: DeepPartial<Config> = { db: {} };\n'
                    'function _neverCalled(): void {\n'
                    '  // @ts-expect-error — the config is read-only, all the way down\n'
                    '  cfg.db.port = 1;\n}\n'),
        example_io='{"name":"app","db":{"host":"localhost","port":5433},"debug":false}\nfrozen true true',
        rubric=["DeepPartial and DeepReadonly are recursive, with a primitive base case",
                "a nested override keeps its siblings",
                "every level of the result is frozen, children before parents",
                "configure's signature is exactly DeepPartial<Config> in, DeepReadonly<Config> out",
                "casts live inside the implementation, and there is exactly one at the JSON boundary",
                "the harness's @ts-expect-error write is rejected by the type"],
        stretch=_types("tscourse-w29-capstone-stretch", "Library #1 (stretch)",
                       "Two more library types. `DeepMutable<T>` undoes DeepReadonly at every level. "
                       "`Settable<T>` keeps only the keys whose values are NOT objects — the leaves a user "
                       "may set directly from a command line.",
                       'type DeepMutable<T> = T extends object ? { -readonly [K in keyof T]: DeepMutable<T[K]> } : T;\n'
                       'type Settable<T> = { [K in keyof T as T[K] extends object ? never : K]: T[K] };\n',
                       'type DeepMutable<T> = T extends object ? { -readonly [K in keyof T]: DeepMutable<T[K]> } : T;\n'
                       'type Settable<T> = { [K in keyof T as T[K] extends object ? never : K]: T[K] };',
                       """
interface Config { name: string; db: { host: string; port: number }; debug: boolean }
type RO = { readonly a: { readonly b: readonly number[] } };
type _1 = Expect<Equal<DeepMutable<RO>, { a: { b: number[] } }>>;
type _2 = Expect<Equal<Settable<Config>, { name: string; debug: boolean }>>;
type _3 = Expect<Equal<Settable<Config["db"]>, { host: string; port: number }>>;
""",
                       hints=["DeepMutable is DeepReadonly with -readonly.",
                              "Settable remaps object-valued keys to never."],
                       difficulty="Hard"),
    ),
))
