# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 31 — type-level challenges.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _typed, _predict, _diagnose,
# _retype, _design, _q, _gloss, _cap_auto, _cap_brief, _mk, _TYPE_PRELUDE) and
# every shared program prefix (_FS, _NUMS, _WORDS, _LINE) is already defined.
# This file only appends its week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# WHAT THIS WEEK IS: TS_ROADMAP's "recursive types · tuple manipulation · depth
# limits and why they exist · type-challenges-style puzzles". Weeks 29-30 built the
# tools; this week is practice with them, at the difficulty interviewers who ask
# type-level questions actually use.
#
# THE DEPTH LIMITS ARE MEASURED, NOT QUOTED. Against the course's checker
# (TypeScript 5.9):
#
#   tail-recursive conditional type (accumulator form)   depth 999 ok, 1000 → TS2589
#   non-tail-recursive (work wrapped around the call)     depth 40 ok,  49 → TS2589
#
# That 25× gap is lesson 3's whole argument — "put the recursion in tail position"
# is the type-level version of week 25's accumulator — and its diagnose ships the
# non-tail version failing at 60 with the real TS2589 message.
#
# EQUAL INSIDE A SOLUTION. `Includes` needs an identity check, and the harness's
# `Equal` is hidden from the learner. Rather than relying on the harness's
# declaration being hoisted into the program (which would work, and would be a
# trap), the program declares its own `Same<X, Y>` in plain sight.
#
# THE LIBRARY: Library #3 is the typed event emitter decision 2 named. An events map
# `{ purchase: [user: string, cents: number] }` types both `on` (the listener's
# parameters) and `emit` (its rest arguments); an unknown event name or a missing
# argument does not compile, and the harness proves both with `@ts-expect-error`
# inside a function that never runs. The class stores listeners in a mapped type
# keyed by event — no casts at all, which is the week's quiet point: the more
# precise the types, the fewer escape hatches the implementation needs.
# ---------------------------------------------------------------------------

_SAME = (
    'type Same<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;\n'
)

_BUILD = (
    'type BuildTuple<N extends number, Acc extends unknown[] = []> =\n'
    '  Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>;\n'
)

_EMITTER = (
    'type Listener<A extends unknown[]> = (...args: A) => void;\n'
    'class Emitter<E extends Record<string, unknown[]>> {\n'
    '  private readonly listeners: { [K in keyof E]?: Listener<E[K]>[] } = {};\n'
    '  on<K extends keyof E>(event: K, listener: Listener<E[K]>): this {\n'
    '    (this.listeners[event] ??= []).push(listener);\n'
    '    return this;\n  }\n'
    '  emit<K extends keyof E>(event: K, ...args: E[K]): number {\n'
    '    const ls = this.listeners[event] ?? [];\n'
    '    for (const l of ls) {\n'
    '      l(...args);\n    }\n'
    '    return ls.length;\n  }\n}\n'
)


# --- Week 31 --------------------------------------------------------------
_WEEKS.append(_week(
    31, 8, _M8,
    "Type-Level Challenges",
    "Puzzles in the style interviewers use: manipulate tuples, count with them, recurse without hitting the compiler's limits, and turn unions inside out. Then the library's third module — a typed event emitter.",
    """
Weeks 29 and 30 built the tools: conditional types, `infer`, mapped types,
template literals, recursion. This week is **practice** — the kind of puzzle that
appears on type-challenges and, occasionally, in an interview for a role that
writes library types.

## What the puzzles are really about

Every one of them is a small program in a strange language:

* **Tuples are the type system's arrays** — and, because their `length` is a literal
  type, its **numbers** too. `[unknown, unknown, unknown]["length"]` is `3`, so adding
  two numbers is concatenating two tuples.
* **Recursion is the only loop**, and the compiler limits how deep it goes. Where you
  put the recursive call decides whether that limit is 999 or about 45.
* **Unions are sets**, and distribution (week 29) is a `for` loop over them — which
  can be turned inside out, into an intersection, with one trick from week 12.

## Why the compiler has limits

The type system is powerful enough to express *any* computation — it is, formally,
Turing-complete. A type that never finishes computing would hang the editor, so the
compiler cuts recursion off and reports **TS2589: "Type instantiation is excessively
deep and possibly infinite."** Lesson 3 measures exactly where, and how to stay under.

## The library

Module three: a **typed event emitter**. One map from event names to argument
tuples types both halves — the listeners you register and the arguments you emit —
so `emit("purchase", "ada")` with a missing amount does not compile.

⏱️ Budget about **seven hours**.
""",
    objectives=[
        "Manipulate tuple types: push, prepend, concatenate, reverse",
        "Search a tuple with an identity check rather than assignability",
        "Count with tuple lengths: build a tuple of length N, add and subtract",
        "Say why the compiler limits type recursion, and what TS2589 means",
        "Rewrite a recursive type into tail position to raise its depth limit",
        "Flatten nested tuples, and describe JSON with a recursive type",
        "Detect a union, and turn a union into an intersection",
        "Generate every permutation of a union",
        "Solve type-challenges-style puzzles: If, TupleToObject, Merge, RequiredKeys, AnyOf",
        "Type an event emitter so listeners and emitted arguments are checked against one map",
    ],
    why="Most working TypeScript never needs a type-level adder. But library types, framework internals and code generators are built from exactly these moves, and a candidate who can explain why a recursive type hits TS2589 — and how to fix it — understands the type system as a language rather than a set of annotations. The event emitter is the payoff: one precise map, and a whole class of wiring bugs stops compiling.",
    est_minutes=420,
    glossary=[
        _gloss("tuple length", "A tuple's length is a literal type — which makes tuples the type system's numbers."),
        _gloss("variadic tuple", "[...A, ...B] — spread tuples into a new one. Concatenation."),
        _gloss("BuildTuple", "A tuple of N unknowns, built by recursion. N as something you can spread."),
        _gloss("TS2589", "Type instantiation is excessively deep and possibly infinite — the recursion limit."),
        _gloss("tail position", "The recursive call is the WHOLE result, not wrapped in more work."),
        _gloss("accumulator", "A type parameter that carries the answer so far, making recursion tail-recursive."),
        _gloss("Turing-complete", "Able to express any computation — including ones that never finish."),
        _gloss("UnionToIntersection", "Infer from a contravariant position and a union comes back as an intersection."),
        _gloss("permutation", "Every ordering of a union's members, as a union of tuples."),
        _gloss("events map", "{ name: [argument tuple] } — the one type an event emitter is checked against."),
    ],
    cheatsheet="""
```ts
// ---- tuples ----------------------------------------------------------------
type Push<T extends readonly unknown[], V> = [...T, V];
type Concat<A extends readonly unknown[], B extends readonly unknown[]> = [...A, ...B];
type Reverse<T extends readonly unknown[]> =
  T extends readonly [infer H, ...infer R] ? [...Reverse<R>, H] : [];
type Includes<T extends readonly unknown[], U> =
  T extends readonly [infer H, ...infer R] ? (Same<H, U> extends true ? true : Includes<R, U>) : false;

// ---- numbers are tuple lengths ------------------------------------------------
type BuildTuple<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>;
type Add<A extends number, B extends number> = [...BuildTuple<A>, ...BuildTuple<B>]["length"];
type Subtract<A extends number, B extends number> =
  BuildTuple<A> extends [...BuildTuple<B>, ...infer R] ? R["length"] : never;

// ---- the depth limit (TS2589), measured on this checker ----------------------
// tail position — the call IS the result:        depth 999 fine, 1000 fails
// non-tail — work wrapped around the call:       depth 40 fine,  49 fails
type Repeat<S extends string, N extends number, C extends unknown[] = [], Out extends string = ""> =
  C["length"] extends N ? Out : Repeat<S, N, [...C, unknown], `${Out}${S}`>;   // tail

// ---- unions inside out ---------------------------------------------------------
type IsUnion<T, U = T> = [T] extends [never] ? false : T extends unknown ? ([U] extends [T] ? false : true) : never;
type UnionToIntersection<U> =
  (U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never;
type Permutation<U, All = U> =
  [U] extends [never] ? [] : U extends unknown ? [U, ...Permutation<Exclude<All, U>>] : never;

// ---- a typed event emitter -----------------------------------------------------
type Events = { login: [user: string]; purchase: [user: string, cents: number] };
on<K extends keyof E>(event: K, listener: (...args: E[K]) => void): this
emit<K extends keyof E>(event: K, ...args: E[K]): number
```
""",
    self_check=[
        "Can you push to, concatenate and reverse a tuple type?",
        "Can you say why Includes needs an identity check rather than `extends`?",
        "Can you add two small numbers at the type level?",
        "Can you say what TS2589 means and why the compiler has it?",
        "Can you rewrite a recursive type into tail position?",
        "Can you flatten a nested tuple type?",
        "Can you write a recursive Json type?",
        "Can you tell whether a type is a union?",
        "Can you explain why UnionToIntersection works?",
        "Can you list the permutations of a union?",
        "Can you type an event emitter from one events map?",
    ],
    review=[
        _q("`[unknown, unknown, unknown][\"length\"]` is…",
           ["number", "3", "unknown", "never"], 1,
           "A literal — which is why tuples can count."),
        _q("`Add<3, 4>` via tuples is computed by…",
           ["arithmetic", "concatenating two tuples and taking the length", "a loop", "infer"], 1,
           "[...BuildTuple<3>, ...BuildTuple<4>][\"length\"]."),
        _q("`Includes<[boolean], true>` should be false. Plain `extends` would say true because…",
           ["of never", "true IS assignable to boolean — assignability is not identity", "of tuples", "it is a bug"], 1,
           "Use an identity check."),
        _q("TS2589 means…",
           ["a syntax error", "type instantiation is excessively deep and possibly infinite", "a missing type", "any"], 1,
           "The recursion limit."),
        _q("The compiler limits recursion because…",
           ["it is slow", "the type system can express computations that never finish", "of memory only", "tradition"], 1,
           "Turing-complete."),
        _q("On this checker, a TAIL-recursive conditional type reaches depth…",
           ["about 45", "999", "unlimited", "100"], 1,
           "Against about 45 for non-tail."),
        _q("A recursion is in tail position when…",
           ["it is last in the file", "the recursive call IS the whole result, with nothing wrapped around it", "it uses infer",
            "it has an accumulator named Acc"], 1,
           "Carry the work in an accumulator instead."),
        _q("UnionToIntersection works by inferring from…",
           ["a return type", "a function PARAMETER position, which is contravariant", "a tuple", "a template"], 1,
           "Week 12's variance, used on purpose."),
        _q("`Permutation<\"a\" | \"b\">` is…",
           ["[\"a\", \"b\"]", "[\"a\", \"b\"] | [\"b\", \"a\"]", "\"a\" | \"b\"", "never"], 1,
           "Every ordering."),
        _q("In the typed emitter, `emit(\"purchase\", \"ada\")` with a missing amount…",
           ["prints undefined", "does not compile", "throws", "is ignored"], 1,
           "The rest parameter is typed E[K]."),
    ],
    milestone="Library #3 — the typed event emitter. One events map types both halves: a listener registered for \"purchase\" receives `(user: string, cents: number)`, and `emit(\"purchase\", \"ada\")` without the amount does not compile, nor does an event name the map does not list. At run time it routes a stream of commands to the right listeners — with no casts in the implementation at all.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w31-tuples", "Tuples are the type system's arrays",
            "Push, concatenate, reverse — and search with identity, not assignability.",
            """
A tuple type is an array whose length and element types are fixed and known. Week
30 matched them with `infer`; this lesson builds them.

## Building

```ts
type Push<T extends readonly unknown[], V> = [...T, V];
type Unshift<T extends readonly unknown[], V> = [V, ...T];
type Concat<A extends readonly unknown[], B extends readonly unknown[]> = [...A, ...B];
```

Spreading a tuple type into a tuple works exactly like spreading an array value.

## Reversing: recursion over a tuple

```ts
type Reverse<T extends readonly unknown[]> =
  T extends readonly [infer H, ...infer R] ? [...Reverse<R>, H] : [];
```

Take the head, reverse the rest, put the head at the end. The empty tuple is the
base case.

## Searching needs identity

"Does the tuple contain U?" The obvious test is `H extends U`. It is wrong:
`Includes<[boolean], true>` would say **true**, because `true` is assignable to
`boolean`. The question is whether some element **is** U — identity — which is the
`Equal` trick from week 29, lesson 1. Since the checker's own `Equal` is hidden from
you, the programs this week declare it in plain sight as `Same<X, Y>`.

> ⚠️ **Common mistakes:** `extends` where identity is meant; forgetting `readonly`
> in patterns (a readonly tuple will not match); and no base case in a recursive
> tuple type.
""",
            warmup=[
                _q("`[...[1, 2], 3]` as a type is…",
                   ["[[1, 2], 3]", "[1, 2, 3]", "[1, 2] | 3", "never"], 1,
                   "Spread, like values."),
                _q("Reverse's base case is…",
                   ["one element", "the empty tuple", "never", "unknown[]"], 1,
                   "Nothing left to move."),
                _q("`true extends boolean` is…",
                   ["false", "true — which is why Includes needs identity", "never", "an error"], 1,
                   "Assignability."),
                _q("`Same<X, Y>` is…",
                   ["a new idea", "the checker's Equal, declared where you can see it", "a built-in", "assignability"], 1,
                   "Identity."),
            ],
            exercises=[
                _types("tscourse-w31-tp-t1", "Push and unshift",
                       "Write `Push<T, V>` and `Unshift<T, V>`.",
                       'type Push<T extends readonly unknown[], V> = [...T, V];\n'
                       'type Unshift<T extends readonly unknown[], V> = [V, ...T];\n',
                       'type Push<T extends readonly unknown[], V> = [...T, V];\n'
                       'type Unshift<T extends readonly unknown[], V> = [V, ...T];',
                       """
type _1 = Expect<Equal<Push<[1, 2], 3>, [1, 2, 3]>>;
type _2 = Expect<Equal<Unshift<[1, 2], 0>, [0, 1, 2]>>;
type _3 = Expect<Equal<Push<[], "a">, ["a"]>>;
""",
                       hints=["Spread the tuple, and put V on one side of it.",
                              "[...T, V] and [V, ...T]"],
                       difficulty="Easy"),
                _types("tscourse-w31-tp-t2", "Concatenate",
                       "Write `Concat<A, B>`.",
                       'type Concat<A extends readonly unknown[], B extends readonly unknown[]> = [...A, ...B];\n',
                       '[...A, ...B]',
                       """
type _1 = Expect<Equal<Concat<[1], [2, 3]>, [1, 2, 3]>>;
type _2 = Expect<Equal<Concat<[], []>, []>>;
""",
                       hints=["Spread both.", "[...A, ...B]"],
                       difficulty="Easy"),
                _types("tscourse-w31-tp-t3", "Reverse",
                       "Write `Reverse<T>` recursively.",
                       'type Reverse<T extends readonly unknown[]> = T extends readonly [infer H, ...infer R] ? [...Reverse<R>, H] : [];\n',
                       'T extends readonly [infer H, ...infer R] ? [...Reverse<R>, H] : []',
                       """
type _1 = Expect<Equal<Reverse<[1, 2, 3]>, [3, 2, 1]>>;
type _2 = Expect<Equal<Reverse<[]>, []>>;
type _3 = Expect<Equal<Reverse<["a"]>, ["a"]>>;
""",
                       hints=["Head and rest; reverse the rest; the head goes last.",
                              "T extends readonly [infer H, ...infer R] ? [...Reverse<R>, H] : []"],
                       difficulty="Medium"),
                _types("tscourse-w31-tp-t4", "Includes, by identity",
                       "Write `Includes<T, U>`: true when some element of T is exactly U. Use the provided `Same`.",
                       _SAME +
                       'type Includes<T extends readonly unknown[], U> =\n'
                       '  T extends readonly [infer H, ...infer R] ? (Same<H, U> extends true ? true : Includes<R, U>) : false;\n',
                       '  T extends readonly [infer H, ...infer R] ? (Same<H, U> extends true ? true : Includes<R, U>) : false;',
                       """
type _1 = Expect<Equal<Includes<[1, 2, 3], 2>, true>>;
type _2 = Expect<Equal<Includes<[1, 2, 3], 4>, false>>;
type _3 = Expect<Equal<Includes<[boolean], true>, false>>;
type _4 = Expect<Equal<Includes<[{ a: 1 }], { a: 1 }>, true>>;
""",
                       hints=["Check the head with Same; if it is not U, recurse on the rest.",
                              "The third assertion is the one plain `extends` gets wrong."],
                       difficulty="Hard"),
                _types("tscourse-w31-tp-t5", "Tuple to object",
                       "Write `TupleToObject<T>`: each element becomes a key whose value is itself.",
                       'type TupleToObject<T extends readonly PropertyKey[]> = { [K in T[number]]: K };\n',
                       '{ [K in T[number]]: K }',
                       """
type _1 = Expect<Equal<TupleToObject<["a", "b"]>, { a: "a"; b: "b" }>>;
const models = ["tesla", "volvo"] as const;
type _2 = Expect<Equal<TupleToObject<typeof models>, { tesla: "tesla"; volvo: "volvo" }>>;
""",
                       hints=["T[number] is the union of the elements; map over it.",
                              "{ [K in T[number]]: K }"],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("Why does `Reverse` use `readonly` in its pattern?",
                   ["style", "so readonly tuples (from `as const`) match too", "speed", "for infer"], 1,
                   "Week 30's lesson."),
                _q("`T[number]` on a tuple gives…",
                   ["its length", "the union of its elements", "the first element", "number"], 1,
                   "Indexed access."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w31-count", "Counting with tuples",
            "A tuple's length is a literal — so tuples are numbers.",
            """
```ts
type Three = [unknown, unknown, unknown]["length"];     // 3 — not number
```

That one fact is enough to do arithmetic.

## Building a number

```ts
type BuildTuple<N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>;
```

Keep adding one `unknown` until the length is N. `BuildTuple<3>` is
`[unknown, unknown, unknown]`.

## Adding and subtracting

```ts
type Add<A extends number, B extends number> = [...BuildTuple<A>, ...BuildTuple<B>]["length"];
type Subtract<A extends number, B extends number> =
  BuildTuple<A> extends [...BuildTuple<B>, ...infer R] ? R["length"] : never;
```

Addition is concatenation. Subtraction is "match B elements off the front and count
what is left" — and when B is larger, nothing matches, which is a reasonable
`never` for "no natural-number answer".

## Why this is a curiosity, and where it is not

Nobody adds numbers this way in real code. But the same machinery indexes tuples,
bounds recursion ("stop after N levels"), and types fixed-length structures — and
it is the clearest possible demonstration that the type system computes. It is also
bounded: `BuildTuple<1000>` hits the depth limit, which is the next lesson.

> ⚠️ **Common mistakes:** expecting `number` to work as N (a non-literal never
> matches a length); negative or fractional N (the recursion never stops); and
> forgetting that every call builds a real tuple type.
""",
            warmup=[
                _q("`BuildTuple<2>` is…",
                   ["2", "[unknown, unknown]", "unknown[]", "[2]"], 1,
                   "Two elements."),
                _q("`Add<2, 3>` is computed as…",
                   ["2 + 3", "the length of a 2-tuple spread with a 3-tuple", "infer", "a union"], 1,
                   "Concatenation."),
                _q("`Subtract<2, 5>` with the tuple method is…",
                   ["-3", "never", "0", "3"], 1,
                   "Five cannot be matched off two."),
                _q("`BuildTuple<number>`…",
                   ["works", "never terminates — a length is never the type `number`", "is []", "is number[]"], 1,
                   "It needs a literal."),
            ],
            exercises=[
                _types("tscourse-w31-ct-t1", "A tuple of length N",
                       "Write `BuildTuple<N>`.",
                       _BUILD,
                       '  Acc["length"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>;',
                       """
type _1 = Expect<Equal<BuildTuple<3>, [unknown, unknown, unknown]>>;
type _2 = Expect<Equal<BuildTuple<0>, []>>;
type _3 = Expect<Equal<BuildTuple<20>["length"], 20>>;
""",
                       hints=["Stop when the accumulator is long enough; otherwise add one and recurse.",
                              "Acc[\"length\"] extends N ? Acc : BuildTuple<N, [...Acc, unknown]>"],
                       difficulty="Medium"),
                _types("tscourse-w31-ct-t2", "Add",
                       "Write `Add<A, B>` with tuple lengths.",
                       _BUILD +
                       'type Add<A extends number, B extends number> = [...BuildTuple<A>, ...BuildTuple<B>]["length"];\n',
                       '[...BuildTuple<A>, ...BuildTuple<B>]["length"]',
                       """
type _1 = Expect<Equal<Add<3, 4>, 7>>;
type _2 = Expect<Equal<Add<0, 0>, 0>>;
type _3 = Expect<Equal<Add<50, 25>, 75>>;
""",
                       hints=["Build both, spread both into one tuple, and read its length.",
                              "[...BuildTuple<A>, ...BuildTuple<B>][\"length\"]"],
                       difficulty="Medium"),
                _types("tscourse-w31-ct-t3", "Subtract",
                       "Write `Subtract<A, B>`: never when B is larger.",
                       _BUILD +
                       'type Subtract<A extends number, B extends number> =\n'
                       '  BuildTuple<A> extends [...BuildTuple<B>, ...infer R] ? R["length"] : never;\n',
                       '  BuildTuple<A> extends [...BuildTuple<B>, ...infer R] ? R["length"] : never;',
                       """
type _1 = Expect<Equal<Subtract<10, 3>, 7>>;
type _2 = Expect<Equal<Subtract<3, 3>, 0>>;
type _3 = Expect<Equal<Subtract<3, 10>, never>>;
""",
                       hints=["Match B elements off the front of an A-tuple, and count the rest.",
                              "BuildTuple<A> extends [...BuildTuple<B>, ...infer R] ? R[\"length\"] : never"],
                       difficulty="Hard"),
                _types("tscourse-w31-ct-t4", "Length, of anything tuple-like",
                       "Write `Len<T>` for any readonly tuple, and `IsEmpty<T>`.",
                       'type Len<T extends readonly unknown[]> = T["length"];\n'
                       'type IsEmpty<T extends readonly unknown[]> = T extends readonly [] ? true : false;\n',
                       'type Len<T extends readonly unknown[]> = T["length"];\n'
                       'type IsEmpty<T extends readonly unknown[]> = T extends readonly [] ? true : false;',
                       """
type _1 = Expect<Equal<Len<[1, 2]>, 2>>;
type _2 = Expect<Equal<Len<readonly ["a", "b", "c"]>, 3>>;
type _3 = Expect<Equal<IsEmpty<[]>, true>>;
type _4 = Expect<Equal<IsEmpty<[1]>, false>>;
""",
                       hints=["A constrained parameter may be indexed by \"length\" (week 29).",
                              "An empty tuple pattern is readonly []."],
                       difficulty="Easy"),
            ],
            quiz=[
                _q("Why is `BuildTuple` written with an accumulator?",
                   ["style", "it keeps the recursive call in tail position, raising the depth limit", "speed", "readonly"], 1,
                   "Lesson 3."),
                _q("Type-level arithmetic is useful in practice for…",
                   ["prices", "bounding recursion and typing fixed-length structures", "nothing", "runtime math"], 1,
                   "Rarely the arithmetic itself."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w31-limits", "Why there is a limit, and how to stay under it",
            "TS2589, measured — and tail position as the fix.",
            """
The type system can express any computation. That includes ones that never
finish, and a type checker that hung on them would hang your editor. So the compiler
cuts deep recursion off:

```
TS2589: Type instantiation is excessively deep and possibly infinite.
```

## Where the limit is, measured on this course's checker

| shape | works | fails |
|---|---|---|
| **tail-recursive** — the recursive call *is* the result | depth 999 | 1,000 |
| **non-tail** — work wrapped around the call | depth 40 | 49 |

A 25-fold difference, from where the call sits.

## Tail position

```ts
// non-tail: the template is built AROUND the recursive call
type Repeat<S extends string, N extends number, C extends unknown[] = []> =
  C["length"] extends N ? "" : `${S}${Repeat<S, N, [...C, unknown]>}`;

// tail: the answer so far travels in an accumulator; the call IS the result
type RepeatAcc<S extends string, N extends number, C extends unknown[] = [], Out extends string = ""> =
  C["length"] extends N ? Out : RepeatAcc<S, N, [...C, unknown], `${Out}${S}`>;
```

Since TypeScript 4.5 the compiler evaluates a conditional type whose branch is
*just* a recursive call in a loop rather than on its stack — so it can afford to
allow far more of them. This is **exactly** week 25's accumulator rewrite, which let a
recursion become a loop; the compiler does the "becomes a loop" part for you.

## The practical rules

* Put the recursion in tail position, with an accumulator parameter.
* Keep type-level recursion to **short** inputs — routes, not documents; tuples of
  tens, not thousands.
* If you hit TS2589 on real code, the recursion is probably unbounded (a recursive
  type walking a type that contains itself), not merely deep.

> ⚠️ **Common mistakes:** building results around the recursive call; parsing long
> strings at the type level; and "fixing" TS2589 with `any`, which hides the problem
> and every type below it.
""",
            warmup=[
                _q("TS2589 exists because…",
                   ["a bug", "some type computations never finish, and the editor must not hang", "tuples are slow", "of any"], 1,
                   "Turing-completeness."),
                _q("A tail-recursive conditional type on this checker reaches depth…",
                   ["about 45", "999", "10,000", "unlimited"], 1,
                   "1,000 fails."),
                _q("`${S}${Repeat<…>}` is not tail-recursive because…",
                   ["of S", "the template is built around the recursive call", "it is a string", "of the default"], 1,
                   "Work after the call."),
                _q("The fix for non-tail recursion is…",
                   ["any", "an accumulator parameter carrying the answer so far", "a smaller N only", "infer"], 1,
                   "Week 25's move."),
            ],
            exercises=[
                _diagnose("tscourse-w31-lm-d1", "The recursion that ran out of depth",
                          "TS2589: Type instantiation is excessively deep and possibly infinite.",
                          'type Repeat<S extends string, N extends number, C extends unknown[] = []> =\n'
                          '  C["length"] extends N ? "" : `${S}${Repeat<S, N, [...C, unknown]>}`;\n'
                          'const rule = "-".repeat(60) as Repeat<"-", 60>;\n'
                          'console.log(rule.length);\n',
                          'type Repeat<S extends string, N extends number, C extends unknown[] = [], Out extends string = ""> =\n'
                          '  C["length"] extends N ? Out : Repeat<S, N, [...C, unknown], `${Out}${S}`>;\n'
                          'const rule = "-".repeat(60) as Repeat<"-", 60>;\n'
                          'console.log(rule.length);\n',
                          [("", "60")],
                          hints=["Sixty levels is not deep — for a TAIL-recursive type.",
                                 "Here the template is built around the recursive call, so each level waits on the next.",
                                 "Carry the string built so far in an accumulator parameter, and make the recursive call the whole result."],
                          difficulty="Hard"),
                _types("tscourse-w31-lm-t1", "Repeat, in tail position",
                       "Write `RepeatAcc<S, N>` so that 500 repetitions compile.",
                       'type RepeatAcc<S extends string, N extends number, C extends unknown[] = [], Out extends string = ""> =\n'
                       '  C["length"] extends N ? Out : RepeatAcc<S, N, [...C, unknown], `${Out}${S}`>;\n',
                       '  C["length"] extends N ? Out : RepeatAcc<S, N, [...C, unknown], `${Out}${S}`>;',
                       """
type _1 = Expect<Equal<RepeatAcc<"ab", 3>, "ababab">>;
type _2 = Expect<Equal<RepeatAcc<"x", 0>, "">>;
type Long = RepeatAcc<"-", 500>;
const _long: Long = "-".repeat(500) as Long;
""",
                       hints=["Two counters: how many so far (a tuple) and the string so far.",
                              "The recursive call must be the entire true-or-false branch."],
                       difficulty="Hard"),
                _types("tscourse-w31-lm-t2", "A bounded walk",
                       "Write `DepthOf<T>`: how many levels of nested arrays T has, as a number, using an accumulator tuple.",
                       'type DepthOf<T, Acc extends unknown[] = []> = T extends readonly (infer E)[] ? DepthOf<E, [...Acc, unknown]> : Acc["length"];\n',
                       'T extends readonly (infer E)[] ? DepthOf<E, [...Acc, unknown]> : Acc["length"]',
                       """
type _1 = Expect<Equal<DepthOf<number>, 0>>;
type _2 = Expect<Equal<DepthOf<number[][]>, 2>>;
type _3 = Expect<Equal<DepthOf<string[][][][]>, 4>>;
""",
                       hints=["Each array layer adds one element to the accumulator.",
                              "When T is no longer an array, the accumulator's length is the answer."],
                       difficulty="Hard"),
            ],
            quiz=[
                _q("You hit TS2589 on a type walking a tree type that contains itself. The likely cause is…",
                   ["too many nodes", "unbounded recursion, not merely deep recursion", "a missing any", "tail position"], 1,
                   "A type that recurses into itself forever."),
                _q("\"Fixing\" TS2589 with `any`…",
                   ["is the standard fix", "hides the error and every type computed below it", "raises the limit", "is required"], 1,
                   "Fix the shape instead."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w31-recursive", "Recursive shapes",
            "Flattening nested tuples, and a type for every JSON value.",
            """
## Flattening

```ts
type DeepFlatten<T extends readonly unknown[]> =
  T extends readonly [infer H, ...infer R]
    ? H extends readonly unknown[] ? [...DeepFlatten<H>, ...DeepFlatten<R>] : [H, ...DeepFlatten<R>]
    : [];
```

Two recursions: into the head when it is itself a tuple, and along the rest.
`DeepFlatten<[1, [2, [3, [4]]]]>` is `[1, 2, 3, 4]`.

## JSON, as a type

Every JSON value is one of six things, two of which contain more JSON:

```ts
type Json =
  | string | number | boolean | null
  | readonly Json[]
  | { readonly [key: string]: Json };
```

A recursive **union** — week 25's `Nested`, grown up. It accepts any parsed JSON and
rejects what JSON cannot hold: `undefined`, functions, `Date` objects, class
instances with methods.

## Types still need runtime checks

`JSON.parse` returns `any` (week 15). The `Json` type describes what a *valid* value
looks like; a **type guard** is what establishes that a value from outside actually
is one. The lesson's runtime exercise walks a parsed value and counts its leaves —
the recursion in the code mirrors the recursion in the type, branch for branch.

> ⚠️ **Common mistakes:** forgetting the head-is-a-tuple case in DeepFlatten; `any`
> in place of a recursive Json; and treating the type as a validator.
""",
            warmup=[
                _q("`DeepFlatten<[1, [2, [3]]]>` is…",
                   ["[1, [2, [3]]]", "[1, 2, 3]", "[1, 2, [3]]", "number[]"], 1,
                   "All the way down."),
                _q("Which is NOT a valid Json value?",
                   ["null", "[1, \"a\"]", "{ f: () => 1 }", "{ a: { b: true } }"], 2,
                   "Functions are not JSON."),
                _q("The Json type's recursive members are…",
                   ["string and number", "arrays and objects", "null and boolean", "none"], 1,
                   "They contain more Json."),
                _q("A value from JSON.parse becomes a trusted Json value by…",
                   ["annotation", "a runtime type guard", "as Json", "nothing"], 1,
                   "Types describe; guards establish."),
            ],
            exercises=[
                _types("tscourse-w31-rc-t1", "Flatten all the way",
                       "Write `DeepFlatten<T>`.",
                       'type DeepFlatten<T extends readonly unknown[]> =\n'
                       '  T extends readonly [infer H, ...infer R]\n'
                       '    ? H extends readonly unknown[] ? [...DeepFlatten<H>, ...DeepFlatten<R>] : [H, ...DeepFlatten<R>]\n'
                       '    : [];\n',
                       '    ? H extends readonly unknown[] ? [...DeepFlatten<H>, ...DeepFlatten<R>] : [H, ...DeepFlatten<R>]',
                       """
type _1 = Expect<Equal<DeepFlatten<[1, [2, [3, [4]]]]>, [1, 2, 3, 4]>>;
type _2 = Expect<Equal<DeepFlatten<[]>, []>>;
type _3 = Expect<Equal<DeepFlatten<[["a"], "b"]>, ["a", "b"]>>;
""",
                       hints=["If the head is itself a tuple, flatten it too, then the rest.",
                              "Otherwise keep the head and flatten the rest."],
                       difficulty="Hard"),
                _types("tscourse-w31-rc-t2", "A type for JSON",
                       "Write `Json`: any value JSON can represent, nested to any depth — and nothing else.",
                       'type Json = string | number | boolean | null | readonly Json[] | { readonly [key: string]: Json };\n',
                       'string | number | boolean | null | readonly Json[] | { readonly [key: string]: Json }',
                       """
const _a: Json = { a: [1, "x", null, { b: true }] };
const _b: Json = 3;
// @ts-expect-error — undefined is not JSON
const _c: Json = { a: undefined };
// @ts-expect-error — functions are not JSON
const _d: Json = [() => 1];
""",
                       hints=["Four primitive members, plus arrays of Json and objects of Json.",
                              "An index signature types the object case."],
                       difficulty="Medium"),
                _typed("tscourse-w31-rc-1", "Walk it like the type",
                       "Count the leaves of a parsed JSON value — one branch per member of the Json union.",
                       _FS +
                       'type Json = string | number | boolean | null | readonly Json[] | { readonly [key: string]: Json };\n'
                       'function leaves(v: Json): number {\n'
                       '  if (Array.isArray(v)) {\n'
                       '    return v.reduce((n: number, x: Json) => n + leaves(x), 0);\n  }\n'
                       '  if (typeof v === "object" && v !== null) {\n'
                       '    return Object.values(v).reduce((n: number, x: Json) => n + leaves(x), 0);\n  }\n'
                       '  return 1;\n}\n'
                       'const data = JSON.parse(fs.readFileSync(0, "utf8")) as Json;\n'
                       'console.log(leaves(data));\n',
                       '  if (typeof v === "object" && v !== null) {\n'
                       '    return Object.values(v).reduce((n: number, x: Json) => n + leaves(x), 0);\n  }',
                       'type _1 = Expect<Equal<ReturnType<typeof leaves>, number>>;\n',
                       [('{"a":[1,"x",null,{"b":true}]}', "4"), ("[1,[2,[3]]]", "3"), ('"solo"', "1")],
                       hints=["Arrays are handled; objects are the other recursive member.",
                              "null is typeof \"object\" too — exclude it.",
                              "Sum the leaves of every value."],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("Why is `null` checked explicitly in `leaves`?",
                   ["style", "typeof null is \"object\"", "null is a leaf", "for arrays"], 1,
                   "JavaScript's oldest quirk."),
                _q("`JSON.parse(...) as Json` is…",
                   ["a validation", "an unchecked claim at the boundary", "required", "a guard"], 1,
                   "Week 15: validate in real code."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w31-unions", "Unions inside out",
            "Detect a union, turn one into an intersection, and list its orderings.",
            """
## Is it a union?

```ts
type IsUnion<T, U = T> =
  [T] extends [never] ? false
  : T extends unknown ? ([U] extends [T] ? false : true)
  : never;
```

`U` keeps a copy of the whole type. Distribution splits `T` into members; for a
union, no single member contains the whole of `U`, so the answer is `true`. (The
`[T] extends [never]` guard is week 29's `IsNever`.)

## Union to intersection

The most famous type puzzle, and it rests on week 12:

```ts
type UnionToIntersection<U> =
  (U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never;
```

1. Distribute: `{a} | {b}` becomes `((x: {a}) => void) | ((x: {b}) => void)`.
2. Infer the parameter type of that union of functions. A value usable as *every*
   one of those functions must accept an argument that is *both* `{a}` and `{b}` —
   parameters are **contravariant**, so inference from them combines with `&`.

`UnionToIntersection<{ a: 1 } | { b: 2 }>` is `{ a: 1 } & { b: 2 }`. Knowing *why* is
what makes it memorable rather than magic.

## Every ordering

```ts
type Permutation<U, All = U> =
  [U] extends [never] ? [] : U extends unknown ? [U, ...Permutation<Exclude<All, U>>] : never;
```

Distribution chooses each member as the first element; recursion permutes the rest.
Three members give six tuples — n! again, as in week 25, but computed by the compiler.

> ⚠️ **Common mistakes:** forgetting the `never` guard (distribution over `never`
> is `never`); expecting UnionToIntersection of primitives to be useful (`string &
> number` is `never`); and permuting large unions (n! grows fast here too).
""",
            warmup=[
                _q("`IsUnion<\"a\" | \"b\">` is…",
                   ["false", "true", "never", "boolean"], 1,
                   "No single member contains the whole."),
                _q("UnionToIntersection infers from…",
                   ["a return type", "a parameter position", "a property", "a tuple"], 1,
                   "Contravariant."),
                _q("`UnionToIntersection<string | number>` is…",
                   ["string & number, which is never", "string | number", "unknown", "an error"], 0,
                   "Two primitives have no common value."),
                _q("`Permutation<\"a\" | \"b\" | \"c\">` has how many tuples?",
                   ["3", "6", "9", "8"], 1,
                   "3!."),
            ],
            exercises=[
                _types("tscourse-w31-un-t1", "Is it a union?",
                       "Write `IsUnion<T>`.",
                       'type IsUnion<T, U = T> = [T] extends [never] ? false : T extends unknown ? ([U] extends [T] ? false : true) : never;\n',
                       '[T] extends [never] ? false : T extends unknown ? ([U] extends [T] ? false : true) : never',
                       """
type _1 = Expect<Equal<IsUnion<"a" | "b">, true>>;
type _2 = Expect<Equal<IsUnion<"a">, false>>;
type _3 = Expect<Equal<IsUnion<never>, false>>;
type _4 = Expect<Equal<IsUnion<string | number | boolean>, true>>;
""",
                       hints=["Keep a copy of the whole type in a second parameter.",
                              "After distribution, compare each member against the whole copy.",
                              "Guard never first, with a tuple."],
                       difficulty="Hard"),
                _types("tscourse-w31-un-t2", "Union to intersection",
                       "Write `UnionToIntersection<U>` using a contravariant inference.",
                       'type UnionToIntersection<U> = (U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never;\n',
                       '(U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never',
                       """
type _1 = Expect<Equal<UnionToIntersection<{ a: 1 } | { b: 2 }>, { a: 1 } & { b: 2 }>>;
type _2 = Expect<Equal<UnionToIntersection<{ a: 1 }>, { a: 1 }>>;
""",
                       hints=["First turn each member into a function taking that member.",
                              "Then infer the parameter of the union of functions.",
                              "(U extends unknown ? (x: U) => void : never) extends (x: infer I) => void ? I : never"],
                       difficulty="Hard"),
                _types("tscourse-w31-un-t3", "Every ordering",
                       "Write `Permutation<U>`: every ordering of a union's members, as a union of tuples.",
                       'type Permutation<U, All = U> = [U] extends [never] ? [] : U extends unknown ? [U, ...Permutation<Exclude<All, U>>] : never;\n',
                       '[U] extends [never] ? [] : U extends unknown ? [U, ...Permutation<Exclude<All, U>>] : never',
                       """
type _1 = Expect<Equal<Permutation<"a" | "b">, ["a", "b"] | ["b", "a"]>>;
type _2 = Expect<Equal<Permutation<never>, []>>;
type _3 = Expect<Equal<Permutation<"x">, ["x"]>>;
""",
                       hints=["Distribution picks each member as the first element.",
                              "The rest is a permutation of everything else: Exclude<All, U>.",
                              "The empty union is the base case: []."],
                       difficulty="Hard"),
            ],
            quiz=[
                _q("Why does IsUnion need a second parameter U?",
                   ["style", "distribution replaces T with one member; U keeps the whole", "for never", "for speed"], 1,
                   "A copy of the original."),
                _q("UnionToIntersection is useful in real code for…",
                   ["numbers", "merging a union of object types — e.g. every plugin's options into one", "strings", "nothing"], 1,
                   "Objects, not primitives."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w31-puzzles", "Puzzles, interview-style",
            "A small set in the type-challenges style — each one a technique you already own.",
            """
Type-challenges puzzles are graded like this course's type exercises: a set of
`Expect<Equal<…>>` lines that must compile. Each one below exercises one earlier
technique; name the technique before writing anything, and most write themselves.

| puzzle | technique | from |
|---|---|---|
| `If<C, T, F>` | a conditional on a boolean | week 29 |
| `Merge<A, B>` | a mapped type over two key sets | week 29 |
| `RequiredKeys<T>` | a mapped type indexed by its own keys | week 30's Paths |
| `AnyOf<T>` | a tuple's element union against the falsy values | weeks 29, 31 |
| `Trim<S>` | recursion on both ends of a template | week 30 |

## One worth a second look

```ts
type RequiredKeys<T> = { [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T];
```

A key is optional exactly when `{}` is assignable to `Pick<T, K>` — an empty object
satisfies `{ b?: 2 }` but not `{ a: 1 }`. Map each key to itself or `never`, then
index by all the keys to collect the survivors (the `-?` stops optional keys adding
`undefined` to the result).

> ⚠️ **Common mistakes:** reaching for a new trick when an earlier one fits; `extends`
> where identity is needed; and forgetting `-?` when collecting keys.
""",
            warmup=[
                _q("`If<true, \"a\", \"b\">` is…",
                   ["\"b\"", "\"a\"", "boolean", "never"], 1,
                   "A conditional on the literal true."),
                _q("A key K of T is optional exactly when…",
                   ["K is a string", "{} is assignable to Pick<T, K>", "T[K] is undefined", "never"], 1,
                   "An empty object satisfies an optional key."),
                _q("`Merge<A, B>` where both have `b` takes `b` from…",
                   ["A", "B", "both", "neither"], 1,
                   "The later one wins, like a spread."),
                _q("The first step with any type puzzle is…",
                   ["guess", "name the technique it needs", "write any", "search"], 1,
                   "Then it mostly writes itself."),
            ],
            exercises=[
                _types("tscourse-w31-pz-t1", "If",
                       "Write `If<C, T, F>`.",
                       'type If<C extends boolean, T, F> = C extends true ? T : F;\n',
                       'C extends true ? T : F',
                       """
type _1 = Expect<Equal<If<true, "a", "b">, "a">>;
type _2 = Expect<Equal<If<false, "a", 2>, 2>>;
""",
                       hints=["A conditional on C.", "C extends true ? T : F"],
                       difficulty="Easy"),
                _types("tscourse-w31-pz-t2", "Merge",
                       "Write `Merge<A, B>`: every key of both, with B's type winning where both have it.",
                       'type Merge<A, B> = { [K in keyof A | keyof B]: K extends keyof B ? B[K] : K extends keyof A ? A[K] : never };\n',
                       '{ [K in keyof A | keyof B]: K extends keyof B ? B[K] : K extends keyof A ? A[K] : never }',
                       """
type _1 = Expect<Equal<Merge<{ a: 1; b: 2 }, { b: "x"; c: 3 }>, { a: 1; b: "x"; c: 3 }>>;
type _2 = Expect<Equal<Merge<{}, { a: 1 }>, { a: 1 }>>;
""",
                       hints=["Loop over the union of both key sets.",
                              "Look in B first, then A."],
                       difficulty="Medium"),
                _types("tscourse-w31-pz-t3", "Required keys",
                       "Write `RequiredKeys<T>`: the union of T's non-optional keys.",
                       'type RequiredKeys<T> = { [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T];\n',
                       '{ [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T]',
                       """
type _1 = Expect<Equal<RequiredKeys<{ a: 1; b?: 2; c: 3 }>, "a" | "c">>;
type _2 = Expect<Equal<RequiredKeys<{ x?: 1 }>, never>>;
""",
                       hints=["An empty object satisfies Pick<T, K> exactly when K is optional.",
                              "Map each key to itself or never, then index by all keys.",
                              "-? stops undefined leaking into the result."],
                       difficulty="Hard"),
                _types("tscourse-w31-pz-t4", "Any truthy?",
                       "Write `AnyOf<T>`: true if any element of the tuple is truthy.",
                       'type AnyOf<T extends readonly unknown[]> = T[number] extends 0 | "" | false | null | undefined | [] ? false : true;\n',
                       'T[number] extends 0 | "" | false | null | undefined | [] ? false : true',
                       """
type _1 = Expect<Equal<AnyOf<[0, "", false]>, false>>;
type _2 = Expect<Equal<AnyOf<[0, 1]>, true>>;
type _3 = Expect<Equal<AnyOf<[]>, false>>;
""",
                       hints=["Compare the union of the elements against the union of falsy values.",
                              "T[number] is every element at once."],
                       difficulty="Medium"),
                _types("tscourse-w31-pz-t5", "Trim both ends",
                       "Write `Trim<S>`, removing spaces from both ends.",
                       'type Trim<S extends string> = S extends ` ${infer R}` | `${infer R} ` ? Trim<R> : S;\n',
                       'S extends ` ${infer R}` | `${infer R} ` ? Trim<R> : S',
                       """
type _1 = Expect<Equal<Trim<"  hi  ">, "hi">>;
type _2 = Expect<Equal<Trim<"hi">, "hi">>;
type _3 = Expect<Equal<Trim<"   ">, "">>;
""",
                       hints=["One pattern can match a space at either end: a union of two templates.",
                              "Recurse until neither matches."],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("`AnyOf<[[]]>` should be false because…",
                   ["[] is falsy in JavaScript", "the puzzle treats an empty array as 'nothing', and lists [] among the falsy types",
                    "of never", "tuples are false"], 1,
                   "A puzzle's definition, not JavaScript's — read the assertions."),
                _q("Type-challenges puzzles are graded by…",
                   ["running", "Expect<Equal<…>> lines that must compile", "tests", "reviewers"], 1,
                   "The same way as this course."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w31-library", "Library #3: the typed event emitter",
            "One events map types both the listeners and the arguments.",
            """
An event emitter lets one part of a program announce things (`emit`) and others
react (`on`). Untyped, it is a bag of strings and `any[]`s, and every mistake — a
misspelled event, a missing argument — is found at run time, if at all.

## One map types everything

```ts
type Events = {
  login: [user: string];
  purchase: [user: string, cents: number];
};
```

Each event name maps to its **argument tuple** (labelled, week 29's `Args`). Both
methods are generic over the event name:

```ts
on<K extends keyof E>(event: K, listener: (...args: E[K]) => void): this
emit<K extends keyof E>(event: K, ...args: E[K]): number
```

`emit("purchase", "ada")` fails because `E["purchase"]` needs two elements;
`on("purchas", …)` fails because it is not a key; and the listener's parameters are
inferred — no annotations at the call site.

## Storage without casts

```ts
private readonly listeners: { [K in keyof E]?: Listener<E[K]>[] } = {};
```

A mapped type keyed by event name, so `this.listeners[event]` is exactly
`Listener<E[K]>[] | undefined`, and `(this.listeners[event] ??= []).push(listener)`
type-checks as written. **No casts anywhere in the class** — contrast the router
(week 30), which stored routes type-erased. The more precisely a structure's type
follows its data, the fewer escape hatches its implementation needs.

## No parameter properties

As with every class in a runnable exercise since week 11, the field is declared
the long way, with an initializer.
""",
            warmup=[
                _q("In the events map, each event maps to…",
                   ["a listener", "its argument tuple", "a string", "a number"], 1,
                   "[user: string, cents: number]."),
                _q("`emit(\"purchase\", \"ada\")` fails because…",
                   ["purchase is misspelled", "E[\"purchase\"] needs two arguments", "emit is private", "of this"], 1,
                   "The rest parameter is typed."),
                _q("The listener table is typed as…",
                   ["Map<string, any>", "a mapped type keyed by event name", "any[]", "Record<string, Function>"], 1,
                   "So no casts are needed."),
                _q("Why does the emitter need no casts where the router needed one?",
                   ["luck", "its storage type follows the data precisely; the router erased types to share one array", "classes",
                    "it is smaller"], 1,
                   "Precision removes escape hatches."),
            ],
            exercises=[
                _typed("tscourse-w31-lb-1", "Store a listener",
                       "Add the listener to its event's list, creating the list if needed.",
                       _EMITTER +
                       'type Events = { ping: [n: number] };\n'
                       'const em = new Emitter<Events>();\n'
                       'em.on("ping", (n) => console.log(`a ${n}`)).on("ping", (n) => console.log(`b ${n * 2}`));\n'
                       'console.log(`listeners ${em.emit("ping", 21)}`);\n',
                       '    (this.listeners[event] ??= []).push(listener);',
                       'type _1 = Expect<Equal<Parameters<Listener<Events["ping"]>>, [n: number]>>;\n',
                       [("", "a 21\nb 42\nlisteners 2")],
                       hints=["The list for this event may not exist yet: ??= [] creates it.",
                              "(this.listeners[event] ??= []).push(listener);"],
                       difficulty="Medium"),
                _typed("tscourse-w31-lb-2", "Emit to everyone listening",
                       "Call every listener for the event with the emitted arguments, and return how many there were.",
                       _EMITTER +
                       'type Events = { say: [who: string, what: string] };\n'
                       'const em = new Emitter<Events>();\n'
                       'em.on("say", (who, what) => console.log(`${who}: ${what}`));\n'
                       'console.log(em.emit("say", "ada", "hello"));\n',
                       '    for (const l of ls) {\n'
                       '      l(...args);\n    }',
                       'type _1 = Expect<Equal<ReturnType<Emitter<Events>["emit"]>, number>>;\n'
                       'function _neverCalled(): void {\n'
                       '  // @ts-expect-error — `say` needs two arguments\n'
                       '  em.emit("say", "ada");\n}\n',
                       [("", "ada: hello\n1")],
                       hints=["Spread the argument tuple into each call.",
                              "for (const l of ls) { l(...args); }"],
                       difficulty="Easy"),
                _fix("tscourse-w31-lb-fix1", "Fix the listener that replaced the others",
                     "Two listeners are registered for `ping`, and only the second ever runs — `listeners 1`. `on` assigns a fresh one-element list every time instead of adding to the existing one.",
                     _EMITTER.replace('    (this.listeners[event] ??= []).push(listener);\n',
                                      '    this.listeners[event] = [listener];\n') +
                     'type Events = { ping: [n: number] };\n'
                     'const em = new Emitter<Events>();\n'
                     'em.on("ping", (n) => console.log(`a ${n}`)).on("ping", (n) => console.log(`b ${n}`));\n'
                     'console.log(`listeners ${em.emit("ping", 1)}`);\n',
                     _EMITTER +
                     'type Events = { ping: [n: number] };\n'
                     'const em = new Emitter<Events>();\n'
                     'em.on("ping", (n) => console.log(`a ${n}`)).on("ping", (n) => console.log(`b ${n}`));\n'
                     'console.log(`listeners ${em.emit("ping", 1)}`);\n',
                     [("", "a 1\nb 1\nlisteners 2")],
                     hints=["What happens to the first listener when the second is registered?",
                            "Add to the list; create it only if it does not exist.",
                            "(this.listeners[event] ??= []).push(listener);"],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why is each event's arguments a TUPLE rather than an object?",
                   ["style", "so it can type a rest parameter and be spread into the call", "speed", "for labels"], 1,
                   "...args: E[K]."),
                _q("A listener registered with `on(\"purchase\", (u, c) => …)` gets its parameter types from…",
                   ["annotations", "E[\"purchase\"], inferred at the call site", "any", "the emitter's constructor"], 1,
                   "No annotations needed."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Library #3 — the typed event emitter",
        """
Write the `Emitter` class, then wire a small shop to it.

**The class** — generic over an events map `E extends Record<string, unknown[]>`:

* `on<K extends keyof E>(event: K, listener: (...args: E[K]) => void): this` —
  add the listener to that event's list; chainable.
* `emit<K extends keyof E>(event: K, ...args: E[K]): number` — call every listener
  for that event, in registration order, and return how many there were.
* Store listeners in a mapped type keyed by event name — **no casts**, and no
  parameter properties.

**The shop** (supplied) registers these listeners:

```ts
type ShopEvents = {
  login: [user: string];
  purchase: [user: string, cents: number];
  logout: [user: string];
};
```

`login` prints `welcome <user>`; `purchase` has **two** listeners — one prints
`<user> spent $<dollars>`, one adds to a running total; `logout` prints
`bye <user> (total $<dollars>)`.

Input: one command per line — `login ada`, `purchase ada 325`, `logout ada`. An
unrecognised command prints `unknown <line>`. After all commands, print
`events <n>`: the total of every `emit`'s return value.

```
login ada
purchase ada 325
purchase ada 100
logout ada
```

```
welcome ada
ada spent $3.25
ada spent $1.00
bye ada (total $4.25)
events 6
```

**How it is checked:** stdout, plus assertions — that a purchase listener's
parameters are `[user: string, cents: number]`, and `@ts-expect-error` on
`emit("purchase", "ada")` (missing amount) and on `on("refund", …)` (no such event).
""",
        _mk("tscourse-w31-capstone", "Library #3 — the typed event emitter",
            "Write a generic Emitter whose listeners and emitted arguments are both checked "
            "against one events map — then drive a small shop with it.",
            _FS + _EMITTER +
            'type ShopEvents = {\n'
            '  login: [user: string];\n'
            '  purchase: [user: string, cents: number];\n'
            '  logout: [user: string];\n};\n'
            'let total = 0;\n'
            'const shop = new Emitter<ShopEvents>()\n'
            '  .on("login", (user) => console.log(`welcome ${user}`))\n'
            '  .on("purchase", (user, cents) => console.log(`${user} spent $${(cents / 100).toFixed(2)}`))\n'
            '  .on("purchase", (_user, cents) => {\n'
            '    total = total + cents;\n  })\n'
            '  .on("logout", (user) => console.log(`bye ${user} (total $${(total / 100).toFixed(2)})`));\n'
            'let events = 0;\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").map((l) => l.trim()).filter((l) => l !== "");\n'
            'for (const line of lines) {\n'
            '  const [cmd, user, amount] = line.split(" ");\n'
            '  if (cmd === "login" && user !== undefined) {\n'
            '    events = events + shop.emit("login", user);\n'
            '  } else if (cmd === "purchase" && user !== undefined && amount !== undefined) {\n'
            '    events = events + shop.emit("purchase", user, Number(amount));\n'
            '  } else if (cmd === "logout" && user !== undefined) {\n'
            '    events = events + shop.emit("logout", user);\n'
            '  } else {\n'
            '    console.log(`unknown ${line}`);\n  }\n}\n'
            'console.log(`events ${events}`);\n',
            [("login ada\npurchase ada 325\npurchase ada 100\nlogout ada",
              "welcome ada\nada spent $3.25\nada spent $1.00\nbye ada (total $4.25)\nevents 6"),
             ("refund ada 100\nlogin bo\nlogout bo", "unknown refund ada 100\nwelcome bo\nbye bo (total $0.00)\nevents 2"),
             ("purchase ada", "unknown purchase ada\nevents 0")],
            ["The listener table is a mapped type: { [K in keyof E]?: Listener<E[K]>[] }.",
             "on: create the event's list if needed, push, return this.",
             "emit: call each listener with ...args, and return how many were called.",
             "No casts are needed anywhere in the class — if you reach for one, the storage type is too loose.",
             "`purchase ada` (no amount) is an unknown command, not a purchase of NaN."],
            "Hard", "challenge",
            blank=_EMITTER.rstrip("\n"),
            harness=_TYPE_PRELUDE +
                    'type _1 = Expect<Equal<Parameters<Listener<ShopEvents["purchase"]>>, [user: string, cents: number]>>;\n'
                    'function _neverCalled(): void {\n'
                    '  // @ts-expect-error — a purchase needs an amount\n'
                    '  shop.emit("purchase", "ada");\n'
                    '  // @ts-expect-error — there is no refund event\n'
                    '  shop.on("refund", () => undefined);\n}\n'),
        example_io="welcome ada\nada spent $3.25\nada spent $1.00\nbye ada (total $4.25)\nevents 6",
        rubric=["one events map types both on and emit",
                "listeners are stored in a mapped type keyed by event, with no casts",
                "on is chainable and appends rather than replaces",
                "emit calls every listener in order and returns the count",
                "a missing argument and an unknown event both fail to compile",
                "no parameter properties"],
        stretch=_typed("tscourse-w31-capstone-stretch", "Library #3 (stretch)",
                       "Add `off(event, listener)` and `once(event, listener)`. `once` registers a wrapper that "
                       "removes itself before calling the listener, so it runs exactly once.",
                       'type Listener<A extends unknown[]> = (...args: A) => void;\n'
                       'class Emitter<E extends Record<string, unknown[]>> {\n'
                       '  private readonly listeners: { [K in keyof E]?: Listener<E[K]>[] } = {};\n'
                       '  on<K extends keyof E>(event: K, listener: Listener<E[K]>): this {\n'
                       '    (this.listeners[event] ??= []).push(listener);\n'
                       '    return this;\n  }\n'
                       '  off<K extends keyof E>(event: K, listener: Listener<E[K]>): this {\n'
                       '    this.listeners[event] = (this.listeners[event] ?? []).filter((l) => l !== listener);\n'
                       '    return this;\n  }\n'
                       '  once<K extends keyof E>(event: K, listener: Listener<E[K]>): this {\n'
                       '    const wrapper: Listener<E[K]> = (...args) => {\n'
                       '      this.off(event, wrapper);\n'
                       '      listener(...args);\n'
                       '    };\n'
                       '    return this.on(event, wrapper);\n  }\n'
                       '  emit<K extends keyof E>(event: K, ...args: E[K]): number {\n'
                       '    const ls = [...(this.listeners[event] ?? [])];\n'
                       '    for (const l of ls) {\n'
                       '      l(...args);\n    }\n'
                       '    return ls.length;\n  }\n}\n'
                       'type Events = { tick: [n: number] };\n'
                       'const em = new Emitter<Events>();\n'
                       'const always = (n: number): void => console.log(`always ${n}`);\n'
                       'em.on("tick", always).once("tick", (n) => console.log(`once ${n}`));\n'
                       'em.emit("tick", 1);\n'
                       'em.emit("tick", 2);\n'
                       'em.off("tick", always);\n'
                       'console.log(`left ${em.emit("tick", 3)}`);\n',
                       '  off<K extends keyof E>(event: K, listener: Listener<E[K]>): this {\n'
                       '    this.listeners[event] = (this.listeners[event] ?? []).filter((l) => l !== listener);\n'
                       '    return this;\n  }\n'
                       '  once<K extends keyof E>(event: K, listener: Listener<E[K]>): this {\n'
                       '    const wrapper: Listener<E[K]> = (...args) => {\n'
                       '      this.off(event, wrapper);\n'
                       '      listener(...args);\n'
                       '    };\n'
                       '    return this.on(event, wrapper);\n  }',
                       'function _neverCalled(): void {\n'
                       '  // @ts-expect-error — tick passes a number\n'
                       '  em.once("tick", (s: string) => console.log(s));\n}\n',
                       [("", "always 1\nonce 1\nalways 2\nleft 0")],
                       hints=["off keeps every listener except the one given — identity comparison.",
                              "once wraps the listener: the wrapper removes ITSELF, then calls through.",
                              "emit iterates a COPY of the list, so a listener removing itself mid-loop is safe."],
                       difficulty="Hard"),
    ),
))
