# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — the rest of optional week 27 (TS_MASTERY_ROADMAP
# "Week 27 — Capstone & Mock Interview"):
#
#   TS_INTERVIEW_BANK   60 conceptual interview questions with model answers,
#                       grouped by topic.
#   TS_MOCK_SESSIONS    three timed 45-minute mock interviews. Each is idiom
#                       questions from the bank + one problem + one type puzzle
#                       from week 27's problem set, and a self-scored rubric.
#   TS_CODE_REVIEWS     ten PR-sized snippets that compile and run — and are
#                       wrong. Write the review, then compare it with the model
#                       review. Both the snippet and the corrected version are
#                       run, and what each prints is computed, not typed.
#
# exec()'d by gen_seed.py after the month files and before
# mastery_ts_attach.py, which attaches all three to week 27 and checks them.
# ---------------------------------------------------------------------------


def _iq(topic, question, answer):
    return {"topic": topic, "question": question, "answer": answer.strip()}


TS_INTERVIEW_BANK = [
    # ---------------------------------------------------------------- types
    _iq("Types & inference", "What is the difference between `any`, `unknown` and `never`?",
        """
`any` switches checking off: every operation is allowed and the value spreads
`any` to everything it touches. `unknown` is the safe top type — anything can be
assigned to it, but you can do nothing with it until you narrow it (`typeof`,
`instanceof`, a type guard). `never` is the bottom type: no value has it. It is
the type of a function that never returns, of an impossible branch, and of the
empty union — which is what makes exhaustiveness checks work. Rule of thumb:
data from outside (JSON, `catch`, user input) is `unknown`; `any` is a
migration tool, not a design.
"""),
    _iq("Types & inference", "`interface` or `type` — which do you use, and when does it matter?",
        """
For object shapes they are nearly interchangeable. The real differences:
`interface` supports declaration merging (two declarations with the same name
combine — useful for augmenting a library, surprising otherwise) and `extends`,
which reports conflicting members clearly. `type` can name anything — unions,
tuples, mapped and conditional types — which `interface` cannot. A common
convention: `interface` for object shapes that others might extend, `type` for
everything else. What matters more than the choice is being consistent.
"""),
    _iq("Types & inference", "What does \"structural typing\" mean, and how would you get nominal behaviour when you need it?",
        """
Compatibility is decided by shape, not by name: any value with the required
members is assignable, whatever it was declared as. Two classes with the same
public members are interchangeable. When two things share a shape but must not
mix — `UserId` and `OrderId` are both `number` — add a *brand*:
`type UserId = number & { readonly __brand: "UserId" }`, created only by a
validating function. The brand exists only in the type system; at runtime it is
still a plain number.
"""),
    _iq("Types & inference", "When should you write a type annotation, and when should you let TypeScript infer?",
        """
Annotate boundaries; infer the inside. Function parameters must be annotated
(there is nothing to infer from). Return types of exported functions are worth
writing: they document intent and stop an accidental change of return type from
leaking to every caller. Locals are usually better inferred — an annotation
there can only widen the type or repeat it. Annotate a local when inference
would be too wide (an empty array, a `let` that starts as `null`).
"""),
    _iq("Types & inference", "Why does `let x = \"up\"` have type `string` while `const x = \"up\"` has type `\"up\"`?",
        """
Widening. A `const` can never change, so the literal type is exact. A `let` can
be reassigned, so TypeScript widens the literal to its base type — otherwise
you could never assign another string. Object properties widen too, because
they are mutable. `as const` opts out: it keeps literal types and makes
properties `readonly`, which is how you derive a union from a constant array
(`typeof SIZES[number]`).
"""),
    _iq("Types & inference", "What does `\"strict\": true` actually turn on?",
        """
A family of flags: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`,
`strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`,
`useUnknownInCatchVariables` and `alwaysStrict` (plus newer ones added to the
family over time). The two most important are `strictNullChecks` — `null` and
`undefined` become their own types — and `noImplicitAny`. Two valuable flags are
*not* in `strict`: `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`.
"""),
    _iq("Types & inference", "What is the difference between `prop?: string` and `prop: string | undefined`?",
        """
`prop?: string` means the key may be absent; `prop: string | undefined` means
the key must be present but its value may be `undefined`. By default TypeScript
lets you write `undefined` into an optional property, so the two blur. Under
`exactOptionalPropertyTypes` they separate: `{ prop: undefined }` is rejected
for `prop?: string`. It matters wherever absence and `undefined` behave
differently — `"prop" in obj`, `Object.keys`, spreading over defaults.
"""),
    _iq("Types & inference", "Do types exist at runtime? What does that mean for your code?",
        """
No. Types are erased — Node's type stripping literally replaces them with
whitespace. So you cannot `instanceof` an interface, cannot branch on a type
parameter, and a type assertion converts nothing. Anything you need to check at
runtime must be a runtime value: a tag field, a class, a validator. That is why
validation libraries derive the type *from* the validator — one source of truth
for both worlds.
"""),
    # ------------------------------------------------------------ narrowing
    _iq("Narrowing & unions", "What is narrowing, and which constructs narrow a type?",
        """
Control-flow analysis: after a check, the compiler knows more about a value in
that branch. Narrowing constructs: `typeof x === "string"`, `instanceof`,
`"key" in x`, equality with a literal (`x.kind === "circle"`, `x === null`),
truthiness, `Array.isArray`, user-defined type predicates (`x is T`), assertion
functions (`asserts x is T`), and since 5.5 inferred predicates from arrow
functions like `x => x !== undefined`. Assignments narrow too, and early
returns narrow everything after them.
"""),
    _iq("Narrowing & unions", "What is a discriminated union, and how do you make a `switch` over one exhaustive?",
        """
A union of object types that share a literal-typed tag field
(`{ kind: "circle"; r: number } | { kind: "square"; side: number }`). Checking
the tag narrows to one member. For exhaustiveness, end the `switch` with
`default: { const unreachable: never = shape; ... }` (or `shape satisfies never`).
If someone adds a variant, the leftover member is not assignable to `never` and
every unhandled switch becomes a compile error — the compiler hands you the
to-do list.
"""),
    _iq("Narrowing & unions", "What is a user-defined type guard, and what is the risk?",
        """
A function returning `x is T`: when it returns `true`, the caller's value is
narrowed to `T`. The risk is that the compiler trusts it completely — a guard
that checks only `"id" in x` but claims `x is User` will happily let you read
`x.email` that is not there. Write guards that check every property you will
use, keep them next to the type, and test them with bad inputs.
"""),
    _iq("Narrowing & unions", "What is an assertion function?",
        """
A function whose return type is `asserts x is T` (or `asserts cond`). If it
returns at all, the compiler narrows `x` for the rest of the scope; it signals
failure by throwing. `function assertIsDefined<T>(v: T): asserts v is NonNullable<T>`
is the classic. It must be declared with an explicit type annotation to be
used as an assertion, and like a type predicate it is trusted — it must really
throw on bad input.
"""),
    _iq("Narrowing & unions", "Compare `const x: T = ...`, `... as T` and `... satisfies T`.",
        """
An annotation checks the value against `T` and then *forgets* the precise type —
`x` is just `T`. `as T` is a claim, not a check: it only refuses conversions
between unrelated types, so it can hide a real mismatch. `satisfies T` checks the
value against `T` *and keeps the inferred type*, so a route table
`satisfies Record<string, Route>` still knows its exact keys. Prefer
`satisfies` for config-like literals, annotations for boundaries, and `as` only
where you know something the compiler cannot.
"""),
    _iq("Narrowing & unions", "Why is narrowing sometimes lost inside a callback?",
        """
The callback may run later, after the variable has changed. For a `let` (or a
property) that is reassigned anywhere, the compiler cannot prove the narrowed
type still holds when the callback runs, so it falls back to the declared type.
A `const`, or a `let` that is never reassigned after the check, keeps its
narrowing (TypeScript 5.4 improved this for closures created after the last
assignment). The fix is usually to copy the narrowed value into a `const`.
"""),
    _iq("Narrowing & unions", "When is the non-null assertion `!` acceptable?",
        """
When you know something the compiler cannot express and the knowledge is local
and obvious — a `Map` lookup right after `has` on the same key, an element that
the surrounding code has just created. It is never a fix for "possibly
undefined" that you have not thought about: it removes the check without
removing the bug. Prefer narrowing, `??` with a default, or restructuring so the
value cannot be missing.
"""),
    _iq("Narrowing & unions", "How does the `in` operator narrow, and what is the catch?",
        """
`"swim" in animal` narrows a union to the members that declare `swim` (and, since
4.9, adds the property to types that do not declare it). The catch is that `in`
looks at the prototype chain: `"toString" in {}` is `true`. For "does this
object have its own key", use `Object.hasOwn(obj, key)` — and remember that an
object literal type does not promise the absence of extra keys at runtime.
"""),
    # -------------------------------------------------------------- generics
    _iq("Functions & generics", "How would you type `pipe(f, g, h)`?",
        """
Two honest answers. The practical one is overloads for 1..N steps, each linking
one function's return type to the next one's parameter — readable, and what
most libraries ship. The general one is a variadic signature validated by a
recursive conditional type over the tuple of functions — it works, but the
error messages get worse. Say which trade-off you are making; an interviewer
cares more about that than about the cleverer type.
"""),
    _iq("Functions & generics", "When should a function be generic, and when should it take a union?",
        """
Generic when the type parameter *relates* two positions: the input type
determines the output (`first<T>(xs: readonly T[]): T | undefined`). If a type
parameter appears only once, it relates nothing — it is `unknown` in disguise,
or worse, a hidden cast (`parse<T>(s): T`). A union is right when the function
accepts several shapes and returns the same thing regardless.
"""),
    _iq("Functions & generics", "What does `K extends keyof T` buy you in `get<T, K extends keyof T>(obj: T, key: K)`?",
        """
Two things. The constraint rejects keys that do not exist, at the call site. And
the return type can be `T[K]` — the type of exactly that property — instead of
the union of all property types. Because `K` is inferred as the literal key
(`"name"`), `get(user, "name")` returns `string`, not `string | number`.
"""),
    _iq("Functions & generics", "Overloads or a union parameter — how do you choose?",
        """
Use a union parameter when the return type does not depend on which member was
passed; one signature is simpler and callers can pass a value that is itself a
union. Use overloads when the return type *does* depend on the argument
(`parse(s: string): number; parse(s: string[]): number[]`). Remember that the
implementation signature is invisible to callers, and a union argument cannot
match any single overload.
"""),
    _iq("Functions & generics", "What does a `const` type parameter do?",
        """
`function f<const T>(x: T)` infers `T` as if the argument had been written with
`as const`: literal types are kept and arrays become readonly tuples. So
`f(["a", "b"])` gives `T = readonly ["a", "b"]` instead of `string[]`. It is how
libraries preserve literal route names or column lists without making every
caller write `as const`. Added in TypeScript 5.0.
"""),
    _iq("Functions & generics", "What problem does `NoInfer<T>` solve?",
        """
Stopping a position from contributing to inference. In
`createStore<T>(initial: T, fallback: T)` both arguments are inference sites, so
a wrong fallback silently widens `T` instead of erroring. Writing
`fallback: NoInfer<T>` makes `T` come from `initial` only, and the fallback is
checked against it. Added in TypeScript 5.4.
"""),
    _iq("Functions & generics", "Why is `(x: Dog) => void` not assignable to `(x: Animal) => void` under `strictFunctionTypes`?",
        """
Parameters are contravariant. A function expecting an `Animal` may be called with
a `Cat`; a handler that only knows how to handle a `Dog` would then receive a
`Cat`. `strictFunctionTypes` enforces this for function-typed properties — but
*not* for methods declared with method syntax (`handle(x: Dog): void`), which stay
bivariant for compatibility. That is a reason to prefer property syntax for
callbacks in interfaces.
"""),
    _iq("Functions & generics", "Show a place where TypeScript is deliberately unsound.",
        """
Array covariance: `Dog[]` is assignable to `Animal[]`, and then
`animals.push(cat)` puts a `Cat` in the dog array — no error. Others: method
parameter bivariance, `any`, type assertions, and index access without
`noUncheckedIndexedAccess` (`xs[99]` is typed `T`). These are trade-offs for
usability; knowing them tells you where to add `readonly` or a stricter flag.
"""),
    # ------------------------------------------------------------ type level
    _iq("Type-level programming", "What is a mapped type, and what does key remapping add?",
        """
`{ [K in keyof T]: F<T[K]> }` builds an object type by iterating keys — it is how
`Partial`, `Readonly` and `Record` are written. Modifiers can be added or removed
(`-readonly`, `-?`). Key remapping (`as`) renames or filters keys:
``[K in keyof T as `get${Capitalize<K & string>}`]`` produces getter names, and
mapping a key to `never` drops it — `PickByValue` and `OmitByValue` are written
that way.
"""),
    _iq("Type-level programming", "What is a distributive conditional type, and how do you stop the distribution?",
        """
A conditional type whose checked type is a *naked* type parameter distributes
over unions: `T extends U ? X : Y` with `T = A | B` evaluates for `A` and `B`
separately and unions the results. That is how `Exclude` works. Wrap both sides
in a tuple — `[T] extends [U]` — to test the union as a whole. Watch out for
`never`: it is the empty union, so a distributive type given `never` returns
`never` without evaluating either branch.
"""),
    _iq("Type-level programming", "What does `infer` do?",
        """
Inside the `extends` clause of a conditional type, `infer R` declares a type
variable that TypeScript solves by matching: `T extends (...args: any[]) => infer R ? R : never`
is `ReturnType`. It works in any position — array elements, promise payloads,
tuple heads (`[infer H, ...infer Rest]`), template literal pieces. `infer R extends string`
constrains what may be captured.
"""),
    _iq("Type-level programming", "Give an example of a template literal type doing real work.",
        """
Extracting route parameters: `RouteParams<"/users/:id/posts/:postId">` evaluates
to `"id" | "postId"` by recursively matching `${string}:${infer P}/${infer Rest}`.
Another: typed event names `${Entity}:${"created" | "deleted"}`. The catch is
that unions inside template literals multiply — three unions of ten members
make a thousand strings.
"""),
    _iq("Type-level programming", "How do you test that two types are equal, and why does the naive version fail?",
        """
The naive `A extends B ? (B extends A ? true : false) : false` distributes over
unions and treats `any` as equal to everything. The standard trick compares two
generic functions:
`type Equal<X, Y> = (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false`,
which relies on the compiler's internal identity check. Pair it with
`type Expect<T extends true> = T` so a failing assertion is a compile error, and
use `@ts-expect-error` to prove something is *rejected*.
"""),
    _iq("Type-level programming", "What goes wrong with a naive `DeepReadonly<T>`?",
        """
`{ readonly [K in keyof T]: DeepReadonly<T[K]> }` recurses into everything —
including functions (whose call signatures a mapped type does not preserve) and
built-ins like `Date` or `Map`, whose methods still mutate. A usable version
stops at primitives and functions, and maps arrays to `ReadonlyArray`. Also:
`readonly` is compile-time only, so it documents intent rather than freezing
anything.
"""),
    _iq("Type-level programming", "Why is `Omit<User, \"passwrd\">` (with a typo) not an error, while `Pick<User, \"passwrd\">` is?",
        """
`Pick<T, K extends keyof T>` constrains its keys; `Omit<T, K extends keyof any>`
deliberately does not, so omitting a key that is not there compiles and removes
nothing. If you want the safety, define `StrictOmit<T, K extends keyof T> = Omit<T, K>`.
And remember that `Omit` changes only the type — the object still carries the
key at runtime unless you remove it.
"""),
    _iq("Type-level programming", "You hit \"Type instantiation is excessively deep and possibly infinite\" (TS2589). What do you do?",
        """
It means a recursive type went past the compiler's depth limit — often a
recursive conditional type fed a recursive type, or an unbounded tuple
counter. Options: make the recursion tail-recursive (accumulate in a parameter
so the compiler can evaluate it iteratively), bound the depth with a counter,
narrow the input so the recursion terminates sooner, or step back — a type that
clever is often costing more than it saves.
"""),
    _iq("Type-level programming", "What is `keyof (A | B)` versus `keyof (A & B)`?",
        """
`keyof (A | B)` is the keys common to both — the only ones you can safely read
from a value that might be either. `keyof (A & B)` is the keys of either — the
intersection value has all of them. It feels backwards until you think of
values: a union value promises less, so fewer keys are safe.
"""),
    _iq("Type-level programming", "How would you write a type for any JSON value?",
        """
A recursive union:
`type Json = string | number | boolean | null | Json[] | { [key: string]: Json }`.
Recursive type aliases are allowed when the recursion goes through an object or
array type. It is the right return type for a *validated* parse — though
`JSON.parse` itself returns `any`, so you would parse into `unknown` and check.
"""),
    # ----------------------------------------------------- objects & classes
    _iq("Objects, classes & modules", "`#count` or `private count`?",
        """
`private` is a compile-time rule: it is erased, so plain JavaScript (or an
`as any`) can read and write it. `#count` is an ECMAScript private field,
enforced by the engine — genuinely inaccessible outside the class, and
`#count in obj` is a reliable brand check. Use `#` when the privacy protects an
invariant. `private` still exists for older targets and for code that
deliberately peeks in tests.
"""),
    _iq("Objects, classes & modules", "Abstract class or interface?",
        """
An interface is a pure contract with no runtime existence; any shape that matches
satisfies it. An abstract class can carry shared implementation and state, and
it exists at runtime (so `instanceof` works), but it forces single inheritance.
Default to an interface for the contract; reach for an abstract class when there
is real shared behaviour to inherit — and often composition does that job
better.
"""),
    _iq("Objects, classes & modules", "What is declaration merging, and where is it useful?",
        """
Several declarations with the same name combine into one: two `interface Foo`
blocks merge their members; an interface can merge with a class; a namespace can
merge with a function. It is how you augment a library's types
(`declare module "express" { interface Request { user?: User } }`) or add to
globals with `declare global`. It is also why an accidental second `interface`
with a common name can silently change a type.
"""),
    _iq("Objects, classes & modules", "Why do many teams avoid `enum`?",
        """
An `enum` is one of the few TypeScript features that emits runtime code, so it
does not work under type stripping (`--erasableSyntaxOnly`); numeric enums have
reverse mappings and historically accepted any number; and `const enum` has
cross-file pitfalls. A literal union — or an `as const` object plus
`type Kind = typeof KIND[keyof typeof KIND]` — gives the same safety, erases
cleanly, and plays well with narrowing.
"""),
    _iq("Objects, classes & modules", "Why does TypeScript report an excess property only sometimes?",
        """
Excess-property checking applies to *fresh* object literals assigned directly to
a typed target: there, an unknown key is almost certainly a typo. Once the object
is stored in a variable and passed along, structural typing applies — having
extra members is allowed, because every subtype has them. So
`f({ nmae: "x" })` errors while `const o = { nmae: "x" }; f(o)` may not.
"""),
    _iq("Objects, classes & modules", "`readonly`, `as const` and `Object.freeze` — what does each actually do?",
        """
`readonly` (and `ReadonlyArray`, `Readonly<T>`) is a compile-time rule that
disappears at runtime, and it is shallow. `as const` makes a literal deeply
readonly *in the type* and keeps literal types. `Object.freeze` really prevents
changes at runtime — but only one level deep, and in sloppy-mode scripts a
write fails silently rather than throwing. Types document intent; freeze
enforces it at runtime.
"""),
    _iq("Objects, classes & modules", "How do branded types work, and how do values get their brand?",
        """
`type Cents = number & { readonly __brand: "Cents" }` is a subtype of `number`
that no plain number is assignable to. Values get the brand only through a
*smart constructor* — `function toCents(n: number): Cents | null` that validates
and then asserts `n as Cents`. That single assertion is the whole trusted
boundary; everywhere else the compiler stops you mixing `Cents` with dollars or
with an `AccountId`. "Parse, don't validate" is the principle behind it.
"""),
    _iq("Objects, classes & modules", "Index signature, `Record`, or `Map`?",
        """
`Record<K, V>` with a finite key union is a fixed-shape object: every key must be
present. An index signature `{ [k: string]: V }` (≈ `Record<string, V>`) is an
open dictionary whose lookups are typed `V` — a lie without
`noUncheckedIndexedAccess`. A `Map` is the runtime dictionary: any key type,
insertion order, `size`, no prototype keys, and `get` honestly returns
`V | undefined`. Use a `Map` for data you add and remove at runtime.
"""),
    # ------------------------------------------------- errors, async, runtime
    _iq("Errors & async", "Why is the `catch` variable `unknown`, and how do you use it?",
        """
Because JavaScript can throw anything — a string, a number, `undefined`.
`useUnknownInCatchVariables` (part of `strict`) types `e` as `unknown`, so you
must narrow: `e instanceof Error ? e.message : String(e)`. Throw only `Error`
subclasses yourself, and attach the original with `new Error("...", { cause: e })`
when you wrap one.
"""),
    _iq("Errors & async", "Exceptions or a `Result` type?",
        """
Throw for bugs and truly exceptional conditions — things the immediate caller
cannot sensibly handle. Return a `Result<T, E>` (a discriminated union
`{ ok: true; value } | { ok: false; error }`) for failures that are part of the
contract, like invalid user input: the type forces the caller to look at the
error branch before reaching the value. Mixing both is fine as long as the rule
is clear.
"""),
    _iq("Errors & async", "Compare `Promise.all`, `allSettled`, `race` and `any`.",
        """
`all` resolves with every value (a tuple type when given a tuple) and rejects on
the first rejection — fail fast, losing the other results. `allSettled` always
resolves with an array of `{ status, value | reason }` — collect everything.
`race` settles with the first promise to settle either way — the timeout
pattern. `any` resolves with the first *fulfilment* and rejects with an
`AggregateError` only if all reject — first success wins.
"""),
    _iq("Errors & async", "In what order does this print: `console.log(1); setTimeout(() => console.log(2)); Promise.resolve().then(() => console.log(3)); console.log(4);`?",
        """
1, 4, 3, 2. Synchronous code runs to completion first (1, 4). Then the microtask
queue drains — promise reactions, `queueMicrotask`, code after an `await` — so 3.
Only then does the event loop take the next task, the timer callback: 2. Every
`await` is a microtask boundary, which is why async code interleaves the way it
does.
"""),
    _iq("Errors & async", "What is wrong with `items.forEach(async (item) => { await save(item); })`?",
        """
`forEach` ignores the promises the callback returns. The saves start, nothing
waits for them, the code after the loop runs immediately, and any rejection is
unhandled. Use `for (const item of items) await save(item)` for one at a time,
or `await Promise.all(items.map(save))` for concurrency — and a pool if the
number must be limited.
"""),
    _iq("Errors & async", "How do you cancel async work in TypeScript?",
        """
With `AbortController`: the caller creates a controller and passes
`controller.signal` down; the work checks `signal.aborted` or listens for
`"abort"`, and `fetch` and many Node APIs accept a signal directly.
`AbortSignal.timeout(ms)` gives a signal that aborts itself, and
`AbortSignal.any([a, b])` combines them. Cancellation is cooperative — a promise
cannot be forcibly stopped; the work has to notice.
"""),
    _iq("Errors & async", "What does `Awaited<T>` do?",
        """
It models what `await` produces: it unwraps promises (and thenables) recursively,
so `Awaited<Promise<Promise<number>>>` is `number` and a non-promise type is
returned unchanged. The type of `Promise.all`'s result uses it for every
element. Writing it yourself is a good `infer` exercise, and a naive
`T extends Promise<infer U> ? U : T` gets nested promises wrong.
"""),
    _iq("Errors & async", "What are generators good for, and what is the gotcha?",
        """
Producing values lazily: `function*` returns an iterator that computes each value
only when asked, so a pipeline over an infinite source works as long as
something (`take`) stops asking. `yield*` delegates to another iterable, which
makes recursive traversals (a tree's in-order walk) short. The gotchas: a
generator object is single-use — iterate it twice and the second pass is empty —
and spreading an infinite one hangs.
"""),
    _iq("Errors & async", "What do `using` and `Symbol.dispose` give you over `try/finally`?",
        """
`using res = open()` calls `res[Symbol.dispose]()` automatically when the
enclosing block exits — normally or by an exception — in reverse order of
declaration. It is `try/finally` that cannot be forgotten and composes when
you hold several resources. `await using` does the same with
`Symbol.asyncDispose`, and `DisposableStack` collects cleanups dynamically.
"""),
    _iq("Errors & async", "What is a floating promise and why is it dangerous?",
        """
A promise that nobody awaits, returns or attaches a handler to — typically a
call to an `async` function without `await`. Errors from it become unhandled
rejections (which crash Node by default), and the code after it runs before the
work finishes. The compiler does not flag it; lint rules like
`no-floating-promises` do. Mark deliberate fire-and-forget with `void`.
"""),
    # -------------------------------------------------------------- tooling
    _iq("Tooling & ecosystem", "How does TypeScript code actually run?",
        """
Either compiled (`tsc` or a bundler emits JavaScript) or with its types stripped
(Node 22.6+ runs `.ts` files by replacing type syntax with whitespace; esbuild
and swc do the same). Stripping only works for *erasable* syntax — `enum`,
`namespace` with values and parameter properties need a transform, which
`--erasableSyntaxOnly` rejects. Either way, type-checking is a separate step:
running a file never checks it.
"""),
    _iq("Tooling & ecosystem", "What is a `.d.ts` file, and how do you type an untyped library?",
        """
A declaration file: types only, no implementation, describing JavaScript that
exists elsewhere. For an untyped package, first look for `@types/<name>`; if
there is none, write `declare module "lib" { export function f(x: string): number; }`
in a `.d.ts` in your project — start with the functions you use, not the whole
API. `declare module "lib";` alone makes every import `any`, which is a
stopgap, not a solution.
"""),
    _iq("Tooling & ecosystem", "What is module augmentation?",
        """
Adding declarations to an existing module's types from your own code:
`declare module "express" { interface Request { user?: User } }` merges into the
library's `Request` interface; `declare global { interface Window { ... } }`
does the same for globals. The file must be a module (have an `import` or
`export`) for `declare global` to be an augmentation rather than a new global
script.
"""),
    _iq("Tooling & ecosystem", "What does `skipLibCheck` do, and is it safe?",
        """
It skips type-checking of declaration files (`.d.ts`), including those in
`node_modules`. It speeds up builds a lot and hides conflicts between two
libraries' types that you cannot fix anyway, so most projects enable it. The
cost: errors in *your own* `.d.ts` files go unreported too — keep hand-written
declarations small and exercised by real code.
"""),
    _iq("Tooling & ecosystem", "`moduleResolution: nodenext` or `bundler`?",
        """
`nodenext` models Node exactly: ESM files need explicit extensions in relative
imports, `package.json` `"type"` decides ESM vs CommonJS per file, and
`exports` maps are honoured. Use it for code Node runs directly. `bundler` models
tools like Vite and esbuild: extensionless imports are fine and `exports` are
still respected. The old `node` (node10) resolution is deprecated as of
TypeScript 6.0.
"""),
    _iq("Tooling & ecosystem", "What changed in TypeScript 6.0 and 7.0 that a project needs to know about?",
        """
6.0 was the last release of the JavaScript-based compiler and a bridge: new
defaults (`strict` on, `module: esnext`, a current `target`, `types: []`) and
deprecations — `target: es5`, AMD/UMD/SystemJS modules, `moduleResolution: node`,
`baseUrl` — that still work behind `ignoreDeprecations: "6.0"`. 7.0 is the
native (Go) compiler: same `tsc`, much faster, the deprecated options removed,
and no programmatic compiler API yet. Fix the 6.0 deprecations and 7.0 is a
drop-in upgrade.
"""),
    _iq("Tooling & ecosystem", "How do you test types?",
        """
With assertions that fail at compile time: `type Expect<T extends true> = T`
and an `Equal<A, B>` helper give `type _ = Expect<Equal<ReturnType<typeof f>, string>>`;
`// @ts-expect-error` above a line proves it is rejected (and errors if it
compiles — TS2578). Libraries like `expect-type` or `tsd` package the same idea.
Run them in CI through `tsc --noEmit`; nothing needs to execute.
"""),
    _iq("Tooling & ecosystem", "How would you migrate a large JavaScript codebase to TypeScript?",
        """
Incrementally. Add `tsconfig` with `allowJs` (and `checkJs` for a first read of
existing JSDoc), rename files one module at a time starting from the leaves,
and type the boundaries first — API clients, data models, shared utilities.
Start with `strict` off if you must, then turn flags on one at a time, fixing
each wave. Keep `any` countable (a lint rule, or `// TODO` search) so it goes
down, and add types for the libraries you depend on early.
"""),
    _iq("Tooling & ecosystem", "What does `verbatimModuleSyntax` enforce, and why?",
        """
That imports and exports are emitted exactly as written: anything imported only
as a type must say so (`import type { User }` or `import { type User }`),
otherwise it is an error (TS1484). The point is predictability for tools that
compile one file at a time — type stripping, esbuild, swc — which cannot know
whether an import is a type without seeing the other file. It replaces the
older `importsNotUsedAsValues`/`preserveValueImports` pair.
"""),
    _iq("Tooling & ecosystem", "What is `noUncheckedIndexedAccess`, and why is it not part of `strict`?",
        """
It types every index read — `xs[i]`, `record[key]` — as `T | undefined`, so you
must handle the missing case. It catches real out-of-range and missing-key bugs.
It is left out of `strict` because it is noisy: loops that are provably in range
still need a check or a `!`. `for…of`, destructuring with defaults, and `.at()`
avoid most of the noise, which is why this programme turns it on from week 14.
"""),
    _iq("Tooling & ecosystem", "A teammate says \"TypeScript made our code slower.\" What do you say?",
        """
Types are erased, so the emitted JavaScript runs at the same speed — the only
runtime costs come from features that emit code (`enum`, down-levelling to an
old `target`, decorators) and from the build. What can be slow is the *compiler*:
huge unions, deep recursive types and project-wide checks. Measure with
`tsc --extendedDiagnostics` or `--generateTrace`, and consider project
references — and TypeScript 7's native compiler — before blaming the types.
"""),
]


# Three timed sessions. `questions` index the bank above; `problem` and
# `puzzle` are ids in week 27's problem set (mastery_ts_more_m6.py).
_MOCK_RUBRIC = [
    "Communication — said the plan out loud before coding, and named the trade-offs",
    "Correctness — the tests pass, and I named the edge cases before running them",
    "Types — no `any`, honest signatures, the compiler did work for me",
    "Testing — I walked an example by hand and checked the output myself",
]

TS_MOCK_SESSIONS = [
    {"title": "Mock interview 1 — data wrangling",
     "minutes": 45,
     "brief": "Ten minutes of idiom questions (answer out loud or in the notes box, then compare), twenty on the problem, fifteen on the type puzzle.",
     "questions": [0, 1, 12], "problem": "tsm-w27-top-words", "puzzle": "tsm-w27-deep-partial",
     "rubric": _MOCK_RUBRIC},
    {"title": "Mock interview 2 — modelling data",
     "minutes": 45,
     "brief": "The questions lean on narrowing and generics; the problem needs careful sorting and merging; the puzzle is about optional keys.",
     "questions": [9, 17, 30], "problem": "tsm-w27-intervals", "puzzle": "tsm-w27-required-keys",
     "rubric": _MOCK_RUBRIC},
    {"title": "Mock interview 3 — async and time",
     "minutes": 45,
     "brief": "Async questions, a stateful rate limiter over a stream of timestamps, and the type of `Promise.all`.",
     "questions": [44, 45, 46], "problem": "tsm-w27-rate-limiter", "puzzle": "tsm-w27-awaited-all",
     "rubric": _MOCK_RUBRIC},
]


# ---------------------------------------------------------------------------
# Code review (X-14 "explain"): read the PR, write the comments, compare. The
# snippet compiles under plain `strict` (the PR's project config) and runs; the
# `fixed` version is the code after the review. Both outputs are computed.
# ---------------------------------------------------------------------------

def _cr(rid, title, context, code, comments, fixed):
    code = code.strip("\n") + "\n"
    fixed = fixed.strip("\n") + "\n"
    runs = _computed(f"{rid}-pr", code, [""], "strict")[0]["output"]
    fixed_runs = _computed(f"{rid}-fixed", fixed, [""], "strict")[0]["output"]
    return {"id": rid, "title": title, "context": context.strip(), "code": code,
            "runs": runs, "comments": list(comments), "fixed": fixed, "fixed_runs": fixed_runs}


TS_CODE_REVIEWS = [
    _cr("tsm-cr-config", "Load the service config",
        "The PR adds a config loader. The config arrives as JSON text from a file the ops team edits by hand.",
        """
interface Config {
  name: string;
  retries: number;
}

function loadConfig(text: string): Config {
  return JSON.parse(text);
}

const cfg = loadConfig('{"name":"api","retries":"3"}');
console.log(cfg.retries + 1);
""",
        ["`JSON.parse` returns `any`, so `loadConfig` promises a `Config` it never checked — the return type is a cast in disguise.",
         "Here `retries` is the string `\"3\"`, so `cfg.retries + 1` is `\"31\"`. Nothing in the types can see it.",
         "Parse into `unknown` and validate every field; return a `Result` (or throw a descriptive error) when the file is wrong.",
         "Name the failure: which field, what was expected, what arrived — whoever edits the file by hand needs that message."],
        """
interface Config {
  name: string;
  retries: number;
}

type Result<T> = { ok: true; value: T } | { ok: false; error: string };

function loadConfig(text: string): Result<Config> {
  const raw: unknown = JSON.parse(text);
  if (typeof raw !== "object" || raw === null) return { ok: false, error: "config must be an object" };
  const name: unknown = (raw as Record<string, unknown>)["name"];
  const retries: unknown = (raw as Record<string, unknown>)["retries"];
  if (typeof name !== "string") return { ok: false, error: "name must be a string" };
  if (typeof retries !== "number" || !Number.isInteger(retries)) {
    return { ok: false, error: `retries must be an integer, got ${JSON.stringify(retries)}` };
  }
  return { ok: true, value: { name, retries } };
}

for (const text of ['{"name":"api","retries":"3"}', '{"name":"api","retries":3}']) {
  const r = loadConfig(text);
  console.log(r.ok ? `retries + 1 = ${r.value.retries + 1}` : `rejected: ${r.error}`);
}
"""),
    _cr("tsm-cr-status", "Label account statuses",
        "The PR adds a `pending` status to the account model and ships the UI labels in the same change.",
        """
type Status = "active" | "suspended" | "deleted" | "pending";

function label(s: Status): string {
  switch (s) {
    case "active":
      return "Active";
    case "suspended":
      return "Suspended";
    default:
      return "Deleted";
  }
}

const incoming = ["active", "pending"];
console.log(incoming.map((s) => label(s as Status)).join(", "));
""",
        ["The `default` branch swallows every status it does not name — the new `pending` accounts are labelled \"Deleted\".",
         "Handle each status explicitly and end with an exhaustiveness check (`const unreachable: never = s`), so the next new status is a compile error here rather than a wrong label.",
         "`s as Status` asserts that any string is a status. Type the source as `Status[]`, or validate strings from outside with a guard."],
        """
type Status = "active" | "suspended" | "deleted" | "pending";

function label(s: Status): string {
  switch (s) {
    case "active":
      return "Active";
    case "suspended":
      return "Suspended";
    case "deleted":
      return "Deleted";
    case "pending":
      return "Pending";
    default: {
      const unreachable: never = s;
      return unreachable;
    }
  }
}

const incoming: Status[] = ["active", "pending"];
console.log(incoming.map(label).join(", "));
"""),
    _cr("tsm-cr-guard", "A guard for user rows",
        "The PR adds a type guard for rows coming back from the database layer, which types them as `unknown`.",
        """
interface User {
  id: number;
  email: string;
}

function isUser(x: unknown): x is User {
  return typeof x === "object" && x !== null && "id" in x;
}

const rows: unknown[] = [{ id: 1, email: "a@x.io" }, { id: 2 }];
for (const r of rows) {
  if (isUser(r)) console.log(`${r.id}: ${r.email}`);
}
""",
        ["The guard checks only that `id` exists, then promises a full `User`. The compiler trusts a type predicate completely, so the second row prints `undefined` for its email.",
         "Check every property the type promises, with its type: `typeof id === \"number\"` and `typeof email === \"string\"`.",
         "Add a test with a malformed row — a guard is only as good as the bad inputs it has been shown."],
        """
interface User {
  id: number;
  email: string;
}

function isUser(x: unknown): x is User {
  if (typeof x !== "object" || x === null) return false;
  const r = x as Record<string, unknown>;
  return typeof r["id"] === "number" && typeof r["email"] === "string";
}

const rows: unknown[] = [{ id: 1, email: "a@x.io" }, { id: 2 }];
for (const r of rows) {
  console.log(isUser(r) ? `${r.id}: ${r.email}` : `skipped: ${JSON.stringify(r)}`);
}
"""),
    _cr("tsm-cr-tags", "Add a tag to a post",
        "The PR adds a helper used by the editor to attach tags, starting from a shared default list.",
        """
const DEFAULT_TAGS: string[] = ["draft"];

function withTag(tags: string[], tag: string): string[] {
  tags.push(tag);
  return tags;
}

const a = withTag(DEFAULT_TAGS, "news");
const b = withTag(DEFAULT_TAGS, "sport");
console.log(a.join(","));
console.log(b.join(","));
console.log(DEFAULT_TAGS.join(","));
""",
        ["`withTag` mutates its argument and returns the same array, so both posts share one list and the shared default grows with every call.",
         "Take `readonly string[]` — the signature then says the function will not change it, and `push` stops compiling.",
         "Return a new array: `[...tags, tag]`. Make the default `as const` (or `readonly`) so nobody else can mutate it either."],
        """
const DEFAULT_TAGS: readonly string[] = ["draft"];

function withTag(tags: readonly string[], tag: string): string[] {
  return [...tags, tag];
}

const a = withTag(DEFAULT_TAGS, "news");
const b = withTag(DEFAULT_TAGS, "sport");
console.log(a.join(","));
console.log(b.join(","));
console.log(DEFAULT_TAGS.join(","));
"""),
    _cr("tsm-cr-foreach", "Save every draft",
        "The PR adds a \"save all\" button. The log line is used by support to confirm a save happened.",
        """
async function save(id: number): Promise<void> {
  await Promise.resolve();
  console.log(`saved ${id}`);
}

async function saveAll(ids: number[]) {
  ids.forEach(async (id) => {
    await save(id);
  });
  console.log("all saved");
}

saveAll([1, 2, 3]);
""",
        ["`forEach` ignores the promises its async callback returns, so \"all saved\" is logged before any save finishes — and a failed save would be an unhandled rejection.",
         "Use `await Promise.all(ids.map(save))` to save concurrently (or `for…of` with `await` if order matters).",
         "Give `saveAll` an explicit `Promise<void>` return type, and `await` the top-level call (or `.catch` it) — it is a floating promise as written."],
        """
async function save(id: number): Promise<void> {
  await Promise.resolve();
  console.log(`saved ${id}`);
}

async function saveAll(ids: readonly number[]): Promise<void> {
  await Promise.all(ids.map(save));
  console.log("all saved");
}

saveAll([1, 2, 3]).catch((e: unknown) => console.log(`save failed: ${String(e)}`));
"""),
    _cr("tsm-cr-prices", "Price a basket",
        "The PR adds basket pricing. Item names come from the client.",
        """
const PRICES: Record<string, number> = { apple: 120, pear: 90 };

function total(items: string[]): number {
  return items.reduce((sum, item) => sum + PRICES[item], 0);
}

console.log(total(["apple", "pear", "kiwi"]));
""",
        ["`Record<string, number>` claims every string has a price, so `PRICES[item]` is typed `number` — but `kiwi` gives `undefined` and the total becomes `NaN`.",
         "Turn on `noUncheckedIndexedAccess`: this line stops compiling until the missing price is handled.",
         "Decide what an unknown item means — reject the basket with a message, or skip it and report it — and make that visible in the return type.",
         "Derive the item names from the price table (`as const satisfies Record<string, number>`, then `keyof typeof PRICES`) so known items are checked at compile time."],
        """
const PRICES = { apple: 120, pear: 90 } as const satisfies Record<string, number>;
type Item = keyof typeof PRICES;

function isItem(name: string): name is Item {
  return Object.hasOwn(PRICES, name);
}

function total(items: readonly string[]): { cents: number; unknown: string[] } {
  let cents = 0;
  const unknown: string[] = [];
  for (const name of items) {
    if (isItem(name)) cents += PRICES[name];
    else unknown.push(name);
  }
  return { cents, unknown };
}

const r = total(["apple", "pear", "kiwi"]);
console.log(`${r.cents} cents; unknown: ${r.unknown.join(",") || "none"}`);
"""),
    _cr("tsm-cr-account", "An account class",
        "The PR introduces an `Account` class for the wallet feature. Balances must never go negative.",
        """
class Account {
  private balance = 0;

  deposit(amount: number) {
    this.balance += amount;
  }

  get total() {
    return this.balance;
  }
}

const acct = new Account();
acct.deposit(-50);
console.log(acct.total);
(acct as any).balance = 1_000_000;
console.log(acct.total);
""",
        ["`deposit` accepts negative (and fractional, and `NaN`) amounts, so the \"never negative\" invariant is not enforced anywhere.",
         "`private` is erased at runtime — `(acct as any).balance` rewrites it. Use a `#balance` field when privacy protects an invariant.",
         "Validate in the method and reject bad amounts (throw a `RangeError`, or return a `Result`); add explicit return types on the public members."],
        """
class Account {
  #balance = 0;

  deposit(amount: number): void {
    if (!Number.isInteger(amount) || amount <= 0) {
      throw new RangeError(`deposit must be a positive whole number of cents, got ${amount}`);
    }
    this.#balance += amount;
  }

  get total(): number {
    return this.#balance;
  }
}

const acct = new Account();
try {
  acct.deposit(-50);
} catch (e) {
  console.log(e instanceof Error ? e.message : String(e));
}
acct.deposit(250);
console.log(acct.total);
"""),
    _cr("tsm-cr-transfer", "Move money between accounts",
        "The PR adds the transfer call used by the payments screen.",
        """
function transfer(fromId: number, toId: number, cents: number): string {
  return `move ${cents} from #${fromId} to #${toId}`;
}

const userId = 42;
const accountId = 7;
console.log(transfer(accountId, 2500, userId));
""",
        ["Three `number` parameters in a row: the call passes the amount as the destination and a user id as the amount, and it type-checks.",
         "Brand the ids and the money (`AccountId`, `Cents`) so the compiler can tell them apart — a user id is not an account id either.",
         "Or take one object parameter, `{ from, to, amount }`, so every argument is named at the call site."],
        """
type AccountId = number & { readonly __brand: "AccountId" };
type Cents = number & { readonly __brand: "Cents" };

const accountId = (n: number): AccountId => n as AccountId;
const cents = (n: number): Cents => n as Cents;

function transfer(t: { from: AccountId; to: AccountId; amount: Cents }): string {
  return `move ${t.amount} from #${t.from} to #${t.to}`;
}

console.log(transfer({ from: accountId(7), to: accountId(12), amount: cents(2500) }));
"""),
    _cr("tsm-cr-age", "Parse an age field",
        "The PR adds age parsing for the sign-up form. Zero is not a valid age.",
        """
function parseAge(s: string): number {
  const n = Number(s);
  if (Number.isNaN(n)) throw "bad age";
  return n;
}

function safeAge(s: string): number {
  try {
    return parseAge(s);
  } catch {
    return 0;
  }
}

console.log(["31", "x", "", "4.5"].map(safeAge).join(","));
""",
        ["`throw \"bad age\"` throws a string: no stack trace, and every `catch` has to guess its type. Throw an `Error` (a `RangeError` here).",
         "`Number(\"\")` is `0`, so an empty field is accepted as age 0; `\"4.5\"` passes too. Check for an integer in a sensible range.",
         "`safeAge` turns every failure into `0`, which the caller cannot tell apart from a real value. Return `number | null` or a `Result` instead of a sentinel."],
        """
function parseAge(s: string): number | null {
  const trimmed = s.trim();
  if (!/^\\d+$/.test(trimmed)) return null;
  const n = Number(trimmed);
  return n >= 1 && n <= 130 ? n : null;
}

console.log(["31", "x", "", "4.5"].map((s) => parseAge(s) ?? "invalid").join(","));
"""),
    _cr("tsm-cr-generic", "Two little helpers",
        "The PR adds `first` and `parse` to the shared utilities module.",
        """
function first<T>(xs: T[]): T {
  return xs[0] as T;
}

function parse<T>(json: string): T {
  return JSON.parse(json) as T;
}

const n = first<number>([]);
const p = parse<{ x: number }>('{"y":1}');
console.log(n, p.x);
""",
        ["`first` claims to return a `T`, but an empty array gives `undefined`; the `as T` is there only to hide that. Return `T | undefined` (and take `readonly T[]`).",
         "`parse<T>` uses its type parameter only in the return type, which makes it a cast with extra steps — the caller picks the type and nothing checks it. Return `unknown` and validate.",
         "Neither `as` is needed once the signatures are honest — a good sign the types were wrong."],
        """
function first<T>(xs: readonly T[]): T | undefined {
  return xs[0];
}

function parsePoint(json: string): { x: number } | null {
  const raw: unknown = JSON.parse(json);
  if (typeof raw === "object" && raw !== null) {
    const x: unknown = (raw as Record<string, unknown>)["x"];
    if (typeof x === "number") return { x };
  }
  return null;
}

console.log(first<number>([]) ?? "empty", parsePoint('{"y":1}')?.x ?? "no x");
"""),
]
