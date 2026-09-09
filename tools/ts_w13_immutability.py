# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 13 — immutability & readonly.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THIS WEEK DEEPENS, IT DOES NOT INTRODUCE. Non-negotiable, and the reason the
# `_SCOPE_RULES` table deliberately omits `readonly ` and `as const`:
#
#   week 8  — `readonly` as an interface member modifier, while modelling data
#   week 9  — `as const` to pin a literal type
#   week 11 — `readonly` class fields, and value objects whose methods return
#             a new instance
#   week 12 — `readonly T[]` as the fix for the array variance hole, and
#             `readonly __brand` inside a branded type
#
# So every lesson here has to say "you have already used this" and then go
# further, rather than pretending to introduce it. Lesson 1 is the bug class
# nobody has named yet (aliasing); lessons 2-3 name what has been in use;
# lessons 4-8 are new ground.
#
# ---------------------------------------------------------------------------
# ONE VERIFIED RUNTIME FACT the freeze lesson is built on.
#
# The judge runs each program as a CommonJS module, so TOP-LEVEL code is in
# sloppy mode while class bodies are always strict. That gives `Object.freeze`
# two different failure modes in the same file, both checked against the real
# runner:
#
#   top level (sloppy):        o.x = 5  ->  silently ignored, o.x stays 1
#   inside a class method:     p.y = 9  ->  throws TypeError
#
# Lesson 7 teaches exactly that contrast — it is the sharpest available argument
# for preferring a compile-time `readonly` over a runtime freeze. Do not "fix"
# either exercise into the other's behaviour.
# ---------------------------------------------------------------------------

# --- Week 13 --------------------------------------------------------------
_WEEKS.append(_week(
    13, 4, _M4,
    "Immutability & readonly",
    "Lock data down with readonly, as const, and pure (copy-don't-mutate) updates.",
    """
You have been using `readonly` since week 8, and `as const` since week 9. This
week is not an introduction — it is the week those tools stop being decoration
and become a way of writing programs.

Here is the bug they prevent, and it has been available to you the whole time:

```ts
const tags: string[] = ["food"];
const alias = tags;
alias.push("home");
console.log(tags.length);      // 2
```

`tags` and `alias` are not two arrays. They are two **names for one array**, and
nothing in the program said so. Now scale that up: you hand a list to a helper,
the helper sorts it "for convenience", and a caller three files away starts
seeing a different order. Nothing crashed, nothing was reported, and the bug is
in whichever file you are not looking at.

That failure has a name — **aliasing** — and there are two ways to deal with it.

**Discipline:** never modify a value you were given; build a new one.

```ts
const more = [...tags, "home"];     // tags is untouched
```

**Enforcement:** make the compiler refuse.

```ts
function report(tags: readonly string[]): string {
  tags.push("home");
  // ❌ TS2339: Property 'push' does not exist on type 'readonly string[]'.
  return tags.join(", ");
}
```

The second is what `readonly` is for, and week 12 already used it once — as the
fix for the array variance hole. Same tool, wider job.

Four things to take away, and the last is the one that pays for the week:

1. `readonly` and `readonly T[]` say "I will not change this", and are checked.
2. `as const` pins a literal all the way down, which is how you get a tuple and
   a union out of one declaration.
3. `readonly` is **shallow** — a `readonly` field holding an array is a mutable
   array, and lesson 5 is entirely about that gap.
4. If every update returns a **new** value, then keeping the old ones is free —
   and that is undo, for nothing. The capstone is a ledger with undo in about
   twenty lines.

⏱️ Budget about **nine hours**.
""",
    objectives=[
        "Explain aliasing, and spot the two-names-one-value bug in code that compiles cleanly",
        "Say what `readonly` costs at runtime (nothing) and what it buys at compile time",
        "Name the array methods `readonly T[]` does not have, and the ones it still does",
        "Choose between `readonly T[]` and `ReadonlyArray<T>` on style alone",
        "Say exactly what `as const` does to an array, an object, and a literal",
        "Update an object or an array without mutating it — replace, remove, insert, sort",
        "Explain why `readonly` is shallow, and write the type that closes the gap one level down",
        "Say what makes a function pure, and demonstrate impurity by calling it twice",
        "Contrast `Object.freeze` with `readonly`: runtime vs compile time, and freeze's two failure modes",
        "Model state as a sequence of values, and get undo out of it for free",
    ],
    why="Every framework you will touch assumes this. React re-renders on a new reference and ignores a mutated one; Redux requires pure reducers; a dependency array compares by identity. Beyond that it is the cheapest debugging win available: a value that cannot change is a value you do not have to trace.",
    est_minutes=560,
    glossary=[
        _gloss("mutation", "Changing a value in place, so every holder of it sees the change."),
        _gloss("aliasing", "Two or more names bound to the same object or array."),
        _gloss("immutable", "A value that is never changed after it is built; updates produce a new value."),
        _gloss("readonly (modifier)", "On a field or member: assignable at construction, never after (TS2540)."),
        _gloss("readonly T[]", "An array type with the mutating methods removed (TS2339 on push, TS2542 on index assignment)."),
        _gloss("ReadonlyArray<T>", "The same type as `readonly T[]`, written in generic form."),
        _gloss("readonly tuple", "`readonly [string, number]` — fixed length, fixed types, no mutation."),
        _gloss("as const (const assertion)", "Pins literal types and makes arrays and object members readonly, all the way down."),
        _gloss("shallow", "`readonly` applies to the member itself, not to what the member points at."),
        _gloss("spread (...)", "`[...xs]` / `{ ...o }` — a one-level copy, which is what makes copy-don't-mutate cheap."),
        _gloss("copy-on-write", "Build a new value that shares what it can and replaces what changed."),
        _gloss("pure function", "Same inputs give the same output, and it changes nothing outside itself."),
        _gloss("side effect", "Any observable change beyond the return value: mutation, I/O, a clock read."),
        _gloss("referential transparency", "A call can be replaced by its result without changing the program."),
        _gloss("Object.freeze", "A RUNTIME guard that makes an object's own properties unwritable."),
        _gloss("Object.isFrozen", "Asks at runtime whether an object has been frozen."),
        _gloss("sloppy mode", "Non-strict JavaScript. A write to a frozen property is silently ignored rather than throwing."),
        _gloss("strict mode", "Class bodies and ES modules. A write to a frozen property throws a TypeError."),
        _gloss("state", "The current value. When updates are immutable, state is just the latest in a sequence."),
        _gloss("history", "The sequence of past states. Undo is stepping back through it."),
        _gloss("update function", "`(state, change) => newState` — the shape every reducer has."),
        _gloss("DeepReadonly", "A type that applies readonly recursively. Built by hand in week 29."),
    ],
    cheatsheet="""
```ts
// ---- the bug ------------------------------------------------------------
const tags: string[] = ["food"];
const alias = tags;          // NOT a copy — one array, two names
alias.push("home");          // tags.length is now 2

const copy = [...tags];      // a real (one-level) copy

// ---- readonly members & arrays -------------------------------------------
interface Entry {
  readonly desc: string;              // TS2540 if reassigned
  readonly tags: readonly string[];   // BOTH words needed — see "shallow"
}
function report(xs: readonly string[]): string {   // no push/pop/sort/reverse...
  return xs.join(", ");                            // ...but map/filter/slice/join stay
}
const a: readonly string[] = ["x"];
const b: ReadonlyArray<string> = ["x"];            // identical type, other spelling

// ---- as const ------------------------------------------------------------
const CATS = ["food", "fun"] as const;   // readonly ["food", "fun"]
type Cat = (typeof CATS)[number];        // "food" | "fun"
const CFG = { retries: 3 } as const;     // { readonly retries: 3 }
// const bad: string[] = CATS;           // TS4104 — readonly cannot become mutable

// ---- copy, don't mutate --------------------------------------------------
const next  = { ...entry, cents: 400 };            // change one field
const added = [...xs, item];                       // append
const gone  = xs.filter((x) => x !== item);        // remove
const swapped = xs.map((x, i) => (i === 2 ? item : x));   // replace at index
const sorted  = [...xs].sort();                    // sort a COPY — .sort() mutates!

// ---- shallow -------------------------------------------------------------
interface Bad  { readonly tags: string[]; }          // tags.push(...) is allowed!
interface Good { readonly tags: readonly string[]; } // now it is not

// ---- freeze: runtime, not compile time -----------------------------------
const o = { x: 1 };
Object.freeze(o);
o.x = 5;                     // top level (sloppy): SILENTLY IGNORED, x stays 1
                             // in a class method (strict): throws TypeError
Object.isFrozen(o);          // true
const f = Object.freeze({ y: 1 });
// f.y = 2;                  // TS2540 — freeze's RETURN type is readonly

// ---- state as a sequence -------------------------------------------------
let history: readonly Ledger[] = [EMPTY];
history = [...history, add(current, "coffee", 325)];   // do
history = history.slice(0, -1);                        // undo
const current = history[history.length - 1] ?? EMPTY;
```
""",
    self_check=[
        "Can you write four lines that show two names mutating one array?",
        "Can you say what `readonly` weighs at runtime?",
        "Can you name four methods `readonly T[]` does not have?",
        "Can you name four it still does?",
        "Can you say what `as const` does to `[\"a\", \"b\"]`, and derive the union from it?",
        "Can you say why `const bad: string[] = someAsConstArray` is an error?",
        "Can you update one field of an object without mutating it?",
        "Can you sort an array without changing the original?",
        "Can you say why `readonly tags: string[]` does not stop `tags.push(...)`, and fix it?",
        "Can you demonstrate that a function is impure by calling it twice?",
        "Can you say the two different things that happen when you write to a frozen property?",
        "Can you say why `readonly` is the better default and `Object.freeze` the special case?",
        "Can you get undo out of an immutable update function without writing an undo algorithm?",
    ],
    review=[
        _q("`const alias = tags;` where tags is an array makes…",
           ["a copy", "a second name for the same array", "a readonly view", "a frozen copy"], 1,
           "Aliasing — the bug this week exists to prevent."),
        _q("`readonly` at runtime…",
           ["freezes the object", "does not exist — it is erased with every other type",
            "throws on write", "copies"], 1,
           "It is a compile-time claim only."),
        _q("`readonly string[]` does NOT have…",
           ["join", "map", "push", "slice"], 2,
           "The mutating methods are removed: push, pop, shift, unshift, splice, sort, reverse, fill."),
        _q("`xs[0] = \"a\"` where xs is `readonly string[]` gives…",
           ["TS2339", "TS2542 — index signature only permits reading", "TS2540", "no error"], 1,
           "A different code from the missing-method one."),
        _q("`ReadonlyArray<string>` and `readonly string[]` are…",
           ["different types", "the same type, two spellings", "generic vs concrete",
            "incompatible"], 1,
           "Pick one and be consistent."),
        _q("`[\"food\", \"fun\"] as const` has type…",
           ["string[]", "readonly [\"food\", \"fun\"]", "(\"food\" | \"fun\")[]",
            "readonly string[]"], 1,
           "A readonly tuple of literal types."),
        _q("`const bad: string[] = catsAsConst` gives…",
           ["no error", "TS4104 — readonly cannot be assigned to a mutable type",
            "TS2540", "TS2339"], 1,
           "The direction is refused on purpose."),
        _q("`{ ...entry, cents: 400 }` does what?",
           ["mutates entry", "builds a new object with one field replaced",
            "deep-copies entry", "freezes entry"], 1,
           "A one-level copy with an override."),
        _q("`xs.sort()` …",
           ["returns a sorted copy", "sorts xs IN PLACE and returns it",
            "is pure", "is not allowed"], 1,
           "Which is why `[...xs].sort()` is the safe form."),
        _q("`readonly tags: string[]` stops…",
           ["tags.push(...)", "reassigning the tags field, and nothing more",
            "everything", "nothing"], 1,
           "readonly is shallow."),
        _q("The fix for that is…",
           ["Object.freeze", "readonly tags: readonly string[]", "a class", "as const"], 1,
           "Both words, one per level."),
        _q("A pure function…",
           ["never returns", "gives the same output for the same input and changes nothing else",
            "takes no arguments", "is faster"], 1,
           "Which is what makes it testable and safe to move."),
        _q("Calling an impure accumulator twice with the same input…",
           ["gives the same answer", "can give a different answer, which is how you detect it",
            "throws", "is a compile error"], 1,
           "A cheap, observable test for purity."),
        _q("Writing to a frozen property at the TOP LEVEL of these programs…",
           ["throws TypeError", "is silently ignored, because top-level code is sloppy mode",
            "is a compile error", "works"], 1,
           "Silence is the worst failure mode, and the reason readonly is better."),
        _q("Writing to a frozen property inside a CLASS METHOD…",
           ["is silently ignored", "throws TypeError, because class bodies are always strict",
            "is a compile error", "works"], 1,
           "Same code, two behaviours, decided by strict mode."),
        _q("`const f = Object.freeze(o); f.x = 1;` is…",
           ["allowed", "TS2540 — freeze's return type is readonly", "a runtime error only",
            "TS2339"], 1,
           "Using the return value is what gets you compile-time help."),
        _q("If every update returns a new state, undo is…",
           ["an algorithm you write", "keeping the previous states and stepping back",
            "impossible", "Object.freeze"], 1,
           "Which is the capstone."),
    ],
    milestone="Budget Buddy's ledger can no longer be changed — every `add` returns a new one. Which means the old ones are still lying around, and that is undo: a four-line feature you got for free by choosing the right shape. Week 18's undo/redo stack is the same idea with a better data structure.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w13-why", "Two names, one value",
            "The bug class nobody has named yet.",
            """
Assignment does not copy. This is the single most important sentence in the
week:

```ts
const tags: string[] = ["food"];
const alias = tags;

alias.push("home");

console.log(tags.length);      // 2
console.log(alias.length);     // 2
```

There is one array. `tags` and `alias` are both **names for it**. The same is
true of objects, and of every array or object nested inside them.

## Why this is worse than it looks

It compiles. It is not a type error, because no type was violated: `alias` is a
`string[]` and `push` is a `string[]` method. TypeScript has raised no
objection, and it is right not to — you asked for exactly this.

The damage comes from distance. Passing a value to a function is an assignment
too:

```ts
function shortest(names: string[]): string {
  names.sort((a, b) => a.length - b.length);     // "just to make this easier"
  return names[0] ?? "";
}

const order = ["coffee", "a", "book"];
console.log(shortest(order));    // a
console.log(order.join(","));    // a,book,coffee  ← the caller's array is reordered
```

`shortest` looks like a question. It is also an instruction, and the caller
never agreed to it. Week 12 met this once already, from the variance side — a
function that pushes into an `Animal[]` it was handed.

## The two answers

**Discipline** — build a new value instead of changing the one you were given:

```ts
function shortest(names: string[]): string {
  const sorted = [...names].sort((a, b) => a.length - b.length);
  return sorted[0] ?? "";
}
```

`[...names]` makes a copy, and the sort happens to the copy.

**Enforcement** — say in the type that you will not change it:

```ts
function shortest(names: readonly string[]): string {
  const sorted = [...names].sort((a, b) => a.length - b.length);
  return sorted[0] ?? "";
}
```

Now a future edit that reaches for `names.sort()` does not compile. Discipline
is a promise; the type is a check. Prefer the check.

## Copies are one level deep

`[...tags]` copies the array. It does **not** copy what is inside it:

```ts
const rows = [{ desc: "coffee" }];
const copy = [...rows];
copy[0]!.desc = "tea";
console.log(rows[0]!.desc);      // tea — the objects are still shared
```

Two arrays, one object. That is the same lesson one level down, and lesson 5 is
about it.

> ⚠️ **Common mistakes:** believing `=` copies; believing a spread copies deeply;
> and sorting or reversing an argument "because it is easier that way".
""",
            warmup=[
                _q("`const alias = tags` where tags is an array gives you…",
                   ["a copy", "a second name for the same array", "a readonly view", "an error"], 1,
                   "Assignment never copies."),
                _q("Aliasing is caught by the type checker…",
                   ["always", "never — no type is violated", "under strict", "with readonly"], 1,
                   "Which is why the bug survives."),
                _q("`[...names].sort()` sorts…",
                   ["names", "a copy of names", "nothing", "both"], 1,
                   "The spread is what protects the original."),
                _q("A spread copies…",
                   ["deeply", "one level — nested objects are still shared", "nothing",
                    "the types"], 1,
                   "Lesson 5 goes after that gap."),
            ],
            exercises=[
                _ex("tscourse-w13-wh-1", "Two names, one array",
                    "Bind a second name to the same array, then watch both report the new length.",
                    'const tags: string[] = ["food"];\n'
                    'const alias = tags;\n'
                    'alias.push("home");\n'
                    'console.log(`${tags.length} ${alias.length}`);\n',
                    'const alias = tags;', [("", "2 2")],
                    hints=["Plain assignment — no spread, no slice.",
                           "Write const alias = tags;"]),
                _ex("tscourse-w13-wh-2", "A real copy",
                    "Make a genuine copy, so pushing to it leaves the original alone.",
                    'const tags: string[] = ["food"];\n'
                    'const copy = [...tags];\n'
                    'copy.push("home");\n'
                    'console.log(`${tags.length} ${copy.length}`);\n',
                    'const copy = [...tags];', [("", "1 2")],
                    hints=["Spread the elements into a fresh array literal.",
                           "Write const copy = [...tags];"]),
                _ex("tscourse-w13-wh-3", "Sort without disturbing the caller",
                    "Sort a copy, so the caller's array keeps its original order.",
                    'function shortest(names: string[]): string {\n'
                    '  const sorted = [...names].sort((a, b) => a.length - b.length);\n'
                    '  return sorted[0] ?? "";\n}\n'
                    'const order: string[] = ["coffee", "a", "book"];\n'
                    'console.log(shortest(order));\n'
                    'console.log(order.join(","));\n',
                    'const sorted = [...names].sort((a, b) => a.length - b.length);',
                    [("", "a\ncoffee,a,book")],
                    hints=["`.sort()` changes the array it is called on, so do not call it on `names`.",
                           "Copy first, then sort the copy."],
                    difficulty="Medium"),
                _ex("tscourse-w13-wh-4", "Objects alias too",
                    "Bind a second name to the same object and change it through that name.",
                    'const entry = { desc: "coffee", cents: 325 };\n'
                    'const same = entry;\n'
                    'same.cents = 400;\n'
                    'console.log(`${entry.cents} ${same.cents}`);\n',
                    'const same = entry;', [("", "400 400")],
                    hints=["Nothing about arrays was special — this is how all objects behave.",
                           "Write const same = entry;"]),
                _ex("tscourse-w13-wh-5", "A copy is one level deep",
                    "Copy the array, then change the shared object inside it.",
                    'const rows = [{ desc: "coffee" }];\n'
                    'const copy = [...rows];\n'
                    'copy[0]!.desc = "tea";\n'
                    'console.log(`${rows[0]?.desc} ${copy[0]?.desc}`);\n',
                    'copy[0]!.desc = "tea";', [("", "tea tea")],
                    hints=["Two arrays now, but only one object between them.",
                           "The ! is earned: the array plainly has an element 0.",
                           'Write copy[0]!.desc = "tea";'],
                    difficulty="Medium"),
                _predict("tscourse-w13-wh-p1", "What a spread infers",
                         'const tags: string[] = ["food"];\n'
                         'const copy = [...tags];\n',
                         "copy", "string[]",
                         why="A copy of a mutable array is still a mutable array — the spread "
                             "changes the identity, not the type.",
                         hints=["Spreading a string[] into a new literal gives another array of the same element type.",
                                "Nothing here made it readonly.",
                                "Write string[]."]),
                _fix("tscourse-w13-wh-fix1", "Fix the helper that reorders its argument",
                     "`shortest` sorts the array it was given, so the caller's order is destroyed — this prints `a` then `a,book,coffee` instead of `a` then `coffee,a,book`.",
                     'function shortest(names: string[]): string {\n'
                     '  names.sort((a, b) => a.length - b.length);\n'
                     '  return names[0] ?? "";\n}\n'
                     'const order: string[] = ["coffee", "a", "book"];\n'
                     'console.log(shortest(order));\n'
                     'console.log(order.join(","));\n',
                     'function shortest(names: readonly string[]): string {\n'
                     '  const sorted = [...names].sort((a, b) => a.length - b.length);\n'
                     '  return sorted[0] ?? "";\n}\n'
                     'const order: string[] = ["coffee", "a", "book"];\n'
                     'console.log(shortest(order));\n'
                     'console.log(order.join(","));\n',
                     [("", "a\ncoffee,a,book")],
                     hints=["`names` and `order` are the same array.",
                            "Sort a copy instead: [...names].sort(...).",
                            "Then annotate the parameter `readonly string[]`, so a future edit cannot reintroduce the bug."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Passing an array to a function is…",
                   ["a copy", "an assignment — the function gets the same array",
                    "a readonly view", "a freeze"], 1,
                   "Which is why a mutating helper reaches the caller."),
                _q("Discipline versus enforcement: prefer…",
                   ["discipline, it is shorter", "enforcement — a type is checked, a promise is not",
                    "neither", "Object.freeze"], 1,
                   "Write the readonly and let the compiler hold you to it."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w13-readonly", "`readonly` members and `readonly T[]`",
            "Naming the tool you have been using since week 8.",
            """
You have met all of this before, in pieces. Week 8 put `readonly` on an
interface member; week 11 put it on class fields and built value objects out of
it; week 12 used `readonly T[]` to close the array variance hole. Here it is as
one idea.

## On a member

```ts
interface Entry {
  readonly desc: string;
  readonly cents: number;
}

const e: Entry = { desc: "coffee", cents: 325 };
e.cents = 400;
// ❌ TS2540: Cannot assign to 'cents' because it is a read-only property.
```

`readonly` restricts **assignment through that name**. It says nothing about the
value's own contents (lesson 5), and it costs nothing at runtime — it is erased
like every other type.

## On an array

`readonly T[]` is the array type with the mutating methods **removed**:

```ts
const tags: readonly string[] = ["food"];

tags.push("home");
// ❌ TS2339: Property 'push' does not exist on type 'readonly string[]'.

tags[0] = "home";
// ❌ TS2542: Index signature in type 'readonly string[]' only permits reading.
```

Two different errors for two different attempts, and both worth recognising.

**Gone:** `push`, `pop`, `shift`, `unshift`, `splice`, `sort`, `reverse`,
`fill`, `copyWithin`.

`sort` and `reverse` on that list surprise people. They belong there: both
change the array in place and merely *return* it as a convenience, which is
exactly the bug from lesson 1.

**Still there:** `map`, `filter`, `reduce`, `slice`, `concat`, `join`,
`includes`, `indexOf`, `find`, `some`, `every`, `at`, `length`, and iteration
with `for...of`. Everything that reads, in other words — which is most of what
you do.

## Two spellings, one type

```ts
const a: readonly string[] = ["x"];
const b: ReadonlyArray<string> = ["x"];
```

Identical. `readonly T[]` is shorter and reads better in a parameter list;
`ReadonlyArray<T>` is occasionally clearer for a nested type. Pick one per
codebase. Note that `readonly` shorthand only works on the array form: for a
`Map` or a `Set` you need the named type (week 19).

## Where to put it

**In a parameter, whenever the function only reads.** This is the habit worth
forming, and week 12 gave the two reasons: it documents intent, and it accepts
mutable arrays anyway, so it costs the caller nothing.

```ts
function summary(tags: readonly string[]): string {
  return `${tags.length}: ${tags.join(", ")}`;
}
summary(["food", "home"]);          // ✅
const mutable: string[] = ["x"];
summary(mutable);                    // ✅ a string[] is assignable to readonly string[]
```

The reverse is refused, which is the whole point:

```ts
const back: string[] = someReadonlyArray;
// ❌ TS4104
```

> ⚠️ **Common mistakes:** expecting `readonly` to do something at runtime;
> forgetting that `sort` and `reverse` mutate; and annotating the *variable*
> readonly when you meant the *parameter*, which protects nothing that matters.
""",
            warmup=[
                _q("`readonly cents: number` then `e.cents = 400` gives…",
                   ["TS2339", "TS2540", "TS2542", "no error"], 1,
                   "Cannot assign to a read-only property."),
                _q("`readonly string[]` is missing…",
                   ["join", "map", "sort", "slice"], 2,
                   "sort mutates in place, so it goes with push and reverse."),
                _q("`tags[0] = \"x\"` on a readonly array gives…",
                   ["TS2540", "TS2542", "TS2339", "no error"], 1,
                   "Index signature only permits reading."),
                _q("`ReadonlyArray<string>` versus `readonly string[]`…",
                   ["different types", "the same type", "one is generic", "incompatible"], 1,
                   "Purely a style choice."),
            ],
            exercises=[
                _ex("tscourse-w13-ro-1", "Settle a member",
                    "Declare `cents` so it cannot be assigned after construction.",
                    'interface Entry {\n  desc: string;\n  readonly cents: number;\n}\n'
                    'const e: Entry = { desc: "coffee", cents: 325 };\n'
                    'e.desc = "tea";\n'
                    'console.log(`${e.desc} ${e.cents}`);\n',
                    'readonly cents: number;', [("", "tea 325")],
                    hints=["One modifier in front of the member.",
                           "`desc` is deliberately still writable, so the program can prove which is which."]),
                _ex("tscourse-w13-ro-2", "A parameter that only reads",
                    "Type the parameter so the function cannot mutate it, and still accepts a plain array.",
                    'function summary(tags: readonly string[]): string {\n'
                    '  return `${tags.length}: ${tags.join(", ")}`;\n}\n'
                    'const mutable: string[] = ["food", "home"];\n'
                    'console.log(summary(mutable));\n',
                    'tags: readonly string[]', [("", "2: food, home")],
                    hints=["The body only reads, so say so.",
                           "A mutable string[] is still assignable to it.",
                           "Write tags: readonly string[]"]),
                _ex("tscourse-w13-ro-3", "The other spelling",
                    "Write the same type in its generic form.",
                    'const tags: ReadonlyArray<string> = ["food", "home"];\n'
                    'console.log(tags.join("/"));\n',
                    'ReadonlyArray<string>', [("", "food/home")],
                    hints=["The named generic type behind `readonly T[]`.",
                           "Write ReadonlyArray<string>"]),
                _ex("tscourse-w13-ro-4", "What you can still do",
                    "Build the report using only methods a readonly array still has.",
                    'function report(tags: readonly string[]): string {\n'
                    '  return tags.filter((t) => t.length > 3).map((t) => t.toUpperCase()).join(",");\n}\n'
                    'console.log(report(["food", "fun", "home"]));\n',
                    'tags.filter((t) => t.length > 3).map((t) => t.toUpperCase()).join(",")',
                    [("", "FOOD,HOME")],
                    hints=["filter, map and join all read rather than mutate, so all three survive.",
                           'Keep tags longer than 3 characters, uppercase them, join with a comma.'],
                    difficulty="Medium"),
                _ex("tscourse-w13-ro-5", "Sorting a readonly array",
                    "`sort` is not available here — produce a sorted copy instead.",
                    'function sorted(tags: readonly string[]): string {\n'
                    '  return [...tags].sort().join(",");\n}\n'
                    'console.log(sorted(["home", "food", "fun"]));\n',
                    'return [...tags].sort().join(",");',
                    [("", "food,fun,home")],
                    hints=["Spread into a fresh mutable array, which does have sort.",
                           "Write return [...tags].sort().join(\",\");"],
                    difficulty="Medium"),
                _predict("tscourse-w13-ro-p1", "Reading a readonly array",
                         'const tags: readonly string[] = ["food"];\n'
                         'const got = tags[0];\n',
                         "got", "string | undefined",
                         why="`readonly` changes what you may WRITE. Something else decides what "
                             "a read gives you.",
                         hints=["readonly does not affect the element type at all.",
                                "This course has run under noUncheckedIndexedAccess since week 6.",
                                "Write string | undefined."],
                         difficulty="Medium"),
                _diagnose("tscourse-w13-ro-d1", "The member that was settled",
                          "TS2540: Cannot assign to 'cents' because it is a read-only property.",
                          'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                          'function withTax(e: Entry): Entry {\n'
                          '  e.cents = Math.round(e.cents * 1.1);\n'
                          '  return e;\n}\n'
                          'const e: Entry = { desc: "coffee", cents: 325 };\n'
                          'console.log(withTax(e).cents);\n',
                          'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                          'function withTax(e: Entry): Entry {\n'
                          '  return { ...e, cents: Math.round(e.cents * 1.1) };\n}\n'
                          'const e: Entry = { desc: "coffee", cents: 325 };\n'
                          'console.log(withTax(e).cents);\n',
                          [("", "358")],
                          hints=["Do not remove `readonly` — the member is meant to be settled.",
                                 "The function already promises to return an Entry, so build a new one.",
                                 "Spread the old entry and override the one field: { ...e, cents: ... }."],
                          difficulty="Medium"),
                _diagnose("tscourse-w13-ro-d2", "The method that is not there",
                          "TS2339: Property 'push' does not exist on type 'readonly string[]'.",
                          'function withDefault(tags: readonly string[]): readonly string[] {\n'
                          '  tags.push("misc");\n'
                          '  return tags;\n}\n'
                          'const tags: readonly string[] = ["food"];\n'
                          'console.log(withDefault(tags).join(","));\n',
                          'function withDefault(tags: readonly string[]): readonly string[] {\n'
                          '  return [...tags, "misc"];\n}\n'
                          'const tags: readonly string[] = ["food"];\n'
                          'console.log(withDefault(tags).join(","));\n',
                          [("", "food,misc")],
                          hints=["The mutating methods are deliberately absent from this type.",
                                 "Return a new array containing the old elements and the new one."],
                          difficulty="Medium"),
                _fix("tscourse-w13-ro-fix1", "Fix the reverse that reached the caller",
                     "`newestFirst` reverses in place, so the caller's array is left backwards too — this prints `c,b,a` twice instead of `c,b,a` then `a,b,c`.",
                     'function newestFirst(tags: string[]): string {\n'
                     '  return tags.reverse().join(",");\n}\n'
                     'const tags: string[] = ["a", "b", "c"];\n'
                     'console.log(newestFirst(tags));\n'
                     'console.log(tags.join(","));\n',
                     'function newestFirst(tags: readonly string[]): string {\n'
                     '  return [...tags].reverse().join(",");\n}\n'
                     'const tags: string[] = ["a", "b", "c"];\n'
                     'console.log(newestFirst(tags));\n'
                     'console.log(tags.join(","));\n',
                     [("", "c,b,a\na,b,c")],
                     hints=["`reverse` mutates and returns the same array — the return value hid that.",
                            "Reverse a copy instead.",
                            "Then make the parameter readonly so it cannot come back."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The best place for `readonly T[]` is…",
                   ["every variable", "a parameter the function only reads",
                    "a return type", "a class field"], 1,
                   "That is where it protects someone else's data."),
                _q("`const back: string[] = readonlyArray` gives…",
                   ["no error", "TS4104", "TS2540", "TS2339"], 1,
                   "Losing readonly would defeat the point."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w13-asconst", "`as const` and const assertions",
            "Pinning a value all the way down.",
            """
Week 9 used `as const` to stop a literal type widening. Week 12 used it to build
a category list and derive a union from it. Here is the full rule.

## What it does

Without it, inference widens:

```ts
const tags = ["food", "fun"];
// string[]  — the literals are gone, and the array is mutable
```

With it, nothing widens and nothing is writable:

```ts
const tags = ["food", "fun"] as const;
// readonly ["food", "fun"]
```

Three changes at once:

1. Literal types are **kept** — `"food"`, not `string`.
2. The array becomes a **readonly tuple** — fixed length, fixed types per slot.
3. The whole thing is **deeply** readonly — nested arrays and objects too, which
   is the one place in this week where you get depth for free.

On an object:

```ts
const CFG = { retries: 3, mode: "fast" } as const;
// { readonly retries: 3; readonly mode: "fast" }

CFG.retries = 5;
// ❌ TS2540: Cannot assign to 'retries' because it is a read-only property.
```

Note `retries` is the type `3`, not `number`. That is usually what you want from
a configuration constant, and occasionally not — if the value is a starting
point that will be reassigned, `as const` is the wrong tool.

## The tuple, and the union out of it

This is the pattern worth memorising, and you have already seen it twice:

```ts
const CATS = ["food", "fun", "home"] as const;
type Cat = (typeof CATS)[number];      // "food" | "fun" | "home"
```

`typeof CATS` is the tuple type; indexing it with `number` reaches every slot;
the result is the union of them. One declaration gives you **both** the runtime
list to iterate and the compile-time union to check against — and they cannot
drift apart, because one is derived from the other.

Compare writing them separately:

```ts
type Cat = "food" | "fun" | "home";                  // and now maintain
const CATS: Cat[] = ["food", "fun", "home"];         // both by hand
```

## Assigning it back to a mutable type is refused

```ts
const mutable: string[] = CATS;
// ❌ TS4104: The type 'readonly ["food", "fun", "home"]' is 'readonly'
//            and cannot be assigned to the mutable type 'string[]'.
```

Exactly as it should be — the whole promise would be void. When you genuinely
need a mutable copy, spread it: `[...CATS]` gives you a `("food" | "fun" |
"home")[]`.

## A tuple slot cannot be assigned either

```ts
CATS[0] = "fun";
// ❌ TS2540: Cannot assign to '0' because it is a read-only property.
```

A readonly *tuple* reports TS2540 on an index, where a readonly *array* reported
TS2542. The difference is that a tuple's slots are known members with names
(`0`, `1`, `2`), while an array has an index signature. Same intent, two codes.

> ⚠️ **Common mistakes:** using `as const` on a value that needs to be widened
> later; expecting it to freeze anything at runtime (it is a type-level
> assertion, erased like the rest); and writing the union and the list
> separately, then letting them drift.
""",
            warmup=[
                _q("`[\"food\", \"fun\"]` with no assertion infers…",
                   ['readonly ["food", "fun"]', "string[]", '("food"|"fun")[]', "never[]"], 1,
                   "Both the literals and the immutability are lost."),
                _q("`as const` on an object makes its members…",
                   ["optional", "readonly, with literal types", "private", "mutable"], 1,
                   "retries becomes the type 3, not number."),
                _q("`(typeof CATS)[number]` where CATS is an as-const array is…",
                   ["the tuple", "the union of its elements", "number", "never"], 1,
                   "Indexed access reaches every slot."),
                _q("`as const` at runtime…",
                   ["freezes the value", "does nothing — it is erased", "copies it",
                    "throws on write"], 1,
                   "Object.freeze is the runtime tool, in lesson 7."),
            ],
            exercises=[
                _ex("tscourse-w13-ac-1", "Pin the array",
                    "Assert the list so its element types are kept and it cannot be mutated.",
                    'const CATS = ["food", "fun", "home"] as const;\n'
                    'type Cat = (typeof CATS)[number];\n'
                    'const c: Cat = "fun";\n'
                    'console.log(`${c} of ${CATS.length}`);\n',
                    'as const', [("", "fun of 3")],
                    hints=["Two words after the array literal.",
                           "Without it, the derived type would be plain `string`."]),
                _ex("tscourse-w13-ac-2", "Derive the union from the list",
                    "Write the type that is the union of the list's elements.",
                    'const CATS = ["food", "fun", "home"] as const;\n'
                    'type Cat = (typeof CATS)[number];\n'
                    'function budget(c: Cat): number {\n'
                    '  return c === "food" ? 50 : c === "fun" ? 20 : 800;\n}\n'
                    'for (const c of CATS) {\n  console.log(`${c} ${budget(c)}`);\n}\n',
                    'type Cat = (typeof CATS)[number];',
                    [("", "food 50\nfun 20\nhome 800")],
                    hints=["`typeof CATS` is the tuple type; index it to reach the slots.",
                           "Write type Cat = (typeof CATS)[number];"],
                    difficulty="Medium"),
                _ex("tscourse-w13-ac-3", "Pin an object",
                    "Assert the config so its members are readonly with literal types.",
                    'const CFG = { retries: 3, mode: "fast" } as const;\n'
                    'console.log(`${CFG.mode} x${CFG.retries}`);\n',
                    '{ retries: 3, mode: "fast" } as const',
                    [("", "fast x3")],
                    hints=["Same two words, after the object literal.",
                           'Write { retries: 3, mode: "fast" } as const']),
                _ex("tscourse-w13-ac-4", "A mutable copy, when you need one",
                    "Produce a mutable array from the pinned list.",
                    'const CATS = ["food", "fun", "home"] as const;\n'
                    'const mutable: string[] = [...CATS];\n'
                    'mutable.push("misc");\n'
                    'console.log(mutable.join(","));\n',
                    'const mutable: string[] = [...CATS];',
                    [("", "food,fun,home,misc")],
                    hints=["Assigning CATS directly would be TS4104.",
                           "Spread it into a fresh array."],
                    difficulty="Medium"),
                _predict("tscourse-w13-ac-p1", "What the assertion produced",
                         'const CATS = ["food", "fun"] as const;\n',
                         "CATS", 'readonly ["food", "fun"]',
                         why="Name the tuple exactly — the modifier, the brackets and the two "
                             "literal types.",
                         hints=["It is a tuple, not an array: each slot has its own type.",
                                "And the whole thing carries a modifier.",
                                'Write readonly ["food", "fun"].'],
                         difficulty="Medium"),
                _diagnose("tscourse-w13-ac-d1", "The pinned slot",
                          "TS2540: Cannot assign to '0' because it is a read-only property.",
                          'const CATS = ["food", "fun", "home"] as const;\n'
                          'CATS[0] = "misc";\n'
                          'console.log(CATS.join(","));\n',
                          'const CATS = ["food", "fun", "home"] as const;\n'
                          'const renamed: string[] = ["misc", ...CATS.slice(1)];\n'
                          'console.log(renamed.join(","));\n',
                          [("", "misc,fun,home")],
                          hints=["A pinned tuple's slots are read-only members, so none can be assigned.",
                                 "Do not drop the `as const` — build a new array instead.",
                                 "Put the replacement first, then spread everything from index 1 onwards."],
                          difficulty="Medium"),
                _diagnose("tscourse-w13-ac-d2", "Losing the promise",
                          "TS4104: The type 'readonly [\"food\", \"fun\"]' is 'readonly' and cannot be assigned to the mutable type 'string[]'.",
                          'const CATS = ["food", "fun"] as const;\n'
                          'const mutable: string[] = CATS;\n'
                          'mutable.push("home");\n'
                          'console.log(mutable.join(","));\n',
                          'const CATS = ["food", "fun"] as const;\n'
                          'const mutable: string[] = [...CATS];\n'
                          'mutable.push("home");\n'
                          'console.log(mutable.join(","));\n',
                          [("", "food,fun,home")],
                          hints=["Allowing this would make the readonly promise meaningless.",
                                 "Ask for a copy rather than a second name."],
                          difficulty="Easy"),
                _fix("tscourse-w13-ac-fix1", "Fix the list and union that drifted",
                     "The union and the runtime list are written out separately, and a category was added to only one of them — so the loop prints a budget of 0 for `home`. Derive one from the other so they cannot disagree.",
                     'type Cat = "food" | "fun" | "home";\n'
                     'const CATS: Cat[] = ["food", "fun"];\n'
                     'function budget(c: Cat): number {\n'
                     '  return c === "food" ? 50 : c === "fun" ? 20 : 800;\n}\n'
                     'for (const c of CATS) {\n  console.log(`${c} ${budget(c)}`);\n}\n',
                     'const CATS = ["food", "fun", "home"] as const;\n'
                     'type Cat = (typeof CATS)[number];\n'
                     'function budget(c: Cat): number {\n'
                     '  return c === "food" ? 50 : c === "fun" ? 20 : 800;\n}\n'
                     'for (const c of CATS) {\n  console.log(`${c} ${budget(c)}`);\n}\n',
                     [("", "food 50\nfun 20\nhome 800")],
                     hints=["Nothing was a type error: the list is a valid Cat[], just an incomplete one.",
                            "Write the list once, `as const`, and derive the union from it.",
                            "type Cat = (typeof CATS)[number]; — and the list has to declare all three."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`as const` gives you depth…",
                   ["never", "yes — nested arrays and objects are readonly too",
                    "only one level", "only for arrays"], 1,
                   "The one place this week where readonly is not shallow."),
                _q("Writing the union and the list separately is bad because…",
                   ["it is slower", "they drift apart and nothing reports it",
                    "it is a type error", "as const is required"], 1,
                   "Derive one from the other."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w13-copy", "Copy, don't mutate",
            "The five updates you actually need.",
            """
Once values are immutable, "changing" one means **building the next one**. There
are only about five moves, and you know most of them already.

## Change one field

```ts
const entry = { desc: "coffee", cents: 325 };
const next = { ...entry, cents: 400 };
// { desc: "coffee", cents: 400 }
```

The spread copies every member; the later `cents` wins. Order matters — put the
overrides **after** the spread, or the spread overwrites them:

```ts
const wrong = { cents: 400, ...entry };
// ❌ TS2783: 'cents' is specified more than once,
//            so this usage will be overwritten.
```

TypeScript is unusually generous here: a write that would be silently discarded
is reported rather than allowed. Do not rely on it in general — it fires only for
this literal-plus-spread shape.

## Append and prepend

```ts
const added = [...tags, "home"];
const front = ["home", ...tags];
```

## Remove

```ts
const gone = tags.filter((t) => t !== "food");
```

`filter` already returns a new array, which is why it needs no spread. Same for
`map`, `slice` and `concat` — the read-only methods from lesson 2 were always
the immutable ones.

## Replace at an index

```ts
const swapped = tags.map((t, i) => (i === 1 ? "home" : t));
```

`map` with the index is the idiomatic form. It reads better than slicing around
the element, and it is one pass.

## Sort, reverse, and the trap

```ts
const sorted = [...tags].sort();          // ✅ sorts the copy
const reversed = [...tags].reverse();     // ✅
```

`sort` and `reverse` are the two everyday methods that mutate **and** return the
same array, so forgetting the spread produces code that looks right and quietly
edits its input. This is the single most common instance of lesson 1's bug.

(Newer runtimes add `toSorted` and `toReversed`, which return copies. They are
not in this course's compiler target, so `[...xs].sort()` is the form to know.)

## Nested updates

To change something one level down, you copy at every level you pass through:

```ts
const state = { user: { name: "ada", age: 36 }, tags: ["x"] };

const older = {
  ...state,
  user: { ...state.user, age: 37 },
};
```

`state.tags` is *shared* between the two — which is fine, because nobody
mutates it. That is the deal immutability offers: copying is cheap because you
only copy the path you changed.

This gets verbose fast, and that verbosity is the honest cost of the approach.
Libraries exist to hide it; the shape underneath is always this.

> ⚠️ **Common mistakes:** putting the override before the spread; forgetting the
> spread before `sort`; and reaching for a deep clone when copying one path
> would do.
""",
            warmup=[
                _q("`{ ...entry, cents: 400 }` …",
                   ["mutates entry", "builds a new object with cents replaced", "deep-copies",
                    "freezes entry"], 1,
                   "A one-level copy with an override."),
                _q("`{ cents: 400, ...entry }` …",
                   ["is the same as spreading first",
                    "would let entry's cents win — and TypeScript reports it, as TS2783",
                    "is deeper", "drops cents"], 1,
                   "The later member wins, so the 400 would be pointless. The compiler says so."),
                _q("`filter` needs a spread around it…",
                   ["yes", "no — it already returns a new array", "only for objects",
                    "under strict"], 1,
                   "Same for map, slice and concat."),
                _q("`tags.sort()` without a spread…",
                   ["returns a copy", "sorts tags in place", "is an error", "is pure"], 1,
                   "The most common version of this week's bug."),
            ],
            exercises=[
                _ex("tscourse-w13-cp-1", "Change one field",
                    "Build a new entry with a different amount, leaving the original alone.",
                    'const entry = { desc: "coffee", cents: 325 };\n'
                    'const next = { ...entry, cents: 400 };\n'
                    'console.log(`${entry.cents} ${next.cents} ${next.desc}`);\n',
                    'const next = { ...entry, cents: 400 };',
                    [("", "325 400 coffee")],
                    hints=["Spread the old object, then override the one member.",
                           "The override goes after the spread."]),
                _ex("tscourse-w13-cp-2", "Remove an element",
                    "Produce the tags without \"fun\".",
                    'const tags: readonly string[] = ["food", "fun", "home"];\n'
                    'const gone = tags.filter((t) => t !== "fun");\n'
                    'console.log(`${tags.length} ${gone.join(",")}`);\n',
                    'const gone = tags.filter((t) => t !== "fun");',
                    [("", "3 food,home")],
                    hints=["filter already builds a new array.",
                           "Keep everything that is not \"fun\"."]),
                _ex("tscourse-w13-cp-3", "Replace at an index",
                    "Replace the element at index 1 with \"home\", leaving the rest as they are.",
                    'const tags: readonly string[] = ["food", "fun", "misc"];\n'
                    'const swapped = tags.map((t, i) => (i === 1 ? "home" : t));\n'
                    'console.log(swapped.join(","));\n',
                    'const swapped = tags.map((t, i) => (i === 1 ? "home" : t));',
                    [("", "food,home,misc")],
                    hints=["map hands you the index as its second argument.",
                           "Return the new value at that index and the old one everywhere else."],
                    difficulty="Medium"),
                _ex("tscourse-w13-cp-4", "Sort a copy",
                    "Sort without disturbing the original, then show both.",
                    'const tags: string[] = ["home", "food", "fun"];\n'
                    'const sorted = [...tags].sort();\n'
                    'console.log(`${tags.join(",")} | ${sorted.join(",")}`);\n',
                    'const sorted = [...tags].sort();',
                    [("", "home,food,fun | food,fun,home")],
                    hints=["`sort` mutates whatever it is called on, so call it on a copy.",
                           "Write const sorted = [...tags].sort();"]),
                _ex("tscourse-w13-cp-5", "Update one level down",
                    "Produce a new state whose user is a year older, copying only the path you changed.",
                    'const state = { user: { name: "ada", age: 36 }, tags: ["x"] };\n'
                    'const older = {\n  ...state,\n  user: { ...state.user, age: 37 },\n};\n'
                    'console.log(`${state.user.age} ${older.user.age} ${older.user.name}`);\n'
                    'console.log(state.tags === older.tags);\n',
                    'user: { ...state.user, age: 37 },',
                    [("", "36 37 ada\ntrue")],
                    hints=["Copy the outer object, then copy the user and override its age.",
                           "The tags array is shared on purpose — that is what makes this cheap.",
                           "Write user: { ...state.user, age: 37 },"],
                    difficulty="Medium"),
                _diagnose("tscourse-w13-cp-d1", "The method a readonly array lacks",
                          "TS2339: Property 'sort' does not exist on type 'readonly string[]'.",
                          'function sorted(tags: readonly string[]): string {\n'
                          '  return tags.sort().join(",");\n}\n'
                          'console.log(sorted(["home", "food"]));\n',
                          'function sorted(tags: readonly string[]): string {\n'
                          '  return [...tags].sort().join(",");\n}\n'
                          'console.log(sorted(["home", "food"]));\n',
                          [("", "food,home")],
                          hints=["`sort` is absent because it mutates, not because sorting is forbidden.",
                                 "Sort a copy of the array."],
                          difficulty="Easy"),
                _diagnose("tscourse-w13-cp-d2", "The override that would be overridden",
                          "TS2783: 'cents' is specified more than once, so this usage will be overwritten.",
                          'const entry = { desc: "coffee", cents: 325 };\n'
                          'const next = { cents: 400, ...entry };\n'
                          'console.log(next.cents);\n',
                          'const entry = { desc: "coffee", cents: 325 };\n'
                          'const next = { ...entry, cents: 400 };\n'
                          'console.log(next.cents);\n',
                          [("", "400")],
                          hints=["In an object literal the LAST value for a key wins, so the spread is burying the 400.",
                                 "TypeScript is unusually helpful here — it reports the pointless write rather than letting it through.",
                                 "Put the spread first and the override after it."],
                          difficulty="Easy"),
                _fix("tscourse-w13-cp-fix2", "Fix the update that mutated instead",
                     "`bump` edits the entry it was given and returns it, so both names show the new amount — this prints `400 400` instead of `325 400`.",
                     'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                     'function bump(e: Entry, cents: number): Entry {\n'
                     '  e.cents = cents;\n'
                     '  return e;\n}\n'
                     'const entry: Entry = { desc: "coffee", cents: 325 };\n'
                     'const next = bump(entry, 400);\n'
                     'console.log(`${entry.cents} ${next.cents}`);\n',
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'function bump(e: Entry, cents: number): Entry {\n'
                     '  return { ...e, cents };\n}\n'
                     'const entry: Entry = { desc: "coffee", cents: 325 };\n'
                     'const next = bump(entry, 400);\n'
                     'console.log(`${entry.cents} ${next.cents}`);\n',
                     [("", "325 400")],
                     hints=["`entry` and `next` are the same object here.",
                            "Return a new object built from the old one: { ...e, cents }.",
                            "Then mark the interface's members readonly, so the mutation cannot come back."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Copying only the path you changed is cheap because…",
                   ["objects are small", "everything you did not change is safely shared",
                    "of the compiler", "spreads are free"], 1,
                   "Nothing mutates, so sharing is safe."),
                _q("The verbosity of nested spreads is…",
                   ["avoidable in plain TypeScript", "the honest cost, which libraries hide",
                    "a compiler bug", "solved by as const"], 1,
                   "The shape underneath is always this."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w13-shallow", "`readonly` is shallow",
            "The gap, and how far down you have to go.",
            """
This is the lesson that catches people, including people who have used
TypeScript for years.

```ts
interface Entry {
  readonly desc: string;
  readonly tags: string[];
}

const e: Entry = { desc: "coffee", tags: ["food"] };

e.tags = [];            // ❌ TS2540 — cannot reassign the member
e.tags.push("home");    // ✅ ...but this is completely fine
console.log(e.tags.join(","));    // food,home
```

Read the modifier literally: **`readonly` protects the binding, not the value.**
`e.tags` must always point at the same array. Nobody said anything about what is
*in* that array.

It is the same fact as lesson 1's one-level copy, seen from the type side.

## Closing it one level

You need `readonly` at each level:

```ts
interface Entry {
  readonly desc: string;
  readonly tags: readonly string[];
}

e.tags.push("home");
// ❌ TS2339: Property 'push' does not exist on type 'readonly string[]'.
```

Two `readonly`s, and they mean different things: the first stops the field being
reassigned, the second stops the array being modified. Both are usually what you
want, and forgetting the second is the standard bug.

## Nested objects, same story

```ts
interface State {
  readonly user: { name: string };
}

s.user.name = "tom";      // ✅ allowed — the OBJECT is not readonly
```

Fix it by making the nested type readonly too:

```ts
interface State {
  readonly user: { readonly name: string };
}
```

Which is fine for one level and tedious for five. Two ways out:

**`as const`**, for literal values you write yourself — it is deep, as lesson 3
said:

```ts
const CFG = { limits: { retries: 3 } } as const;
CFG.limits.retries = 5;    // ❌ TS2540, all the way down
```

**A recursive type**, for types you declare. That is `DeepReadonly<T>`, and
writing it needs mapped and conditional types — which is **week 29**. It is
about six lines, it is the natural first exercise of that week, and it is worth
knowing it exists now so you recognise the shape when a library exposes one.

## What to do in the meantime

Be deliberate about depth rather than exhaustive. In practice:

* Make arrays `readonly T[]` — this is where almost all accidental mutation
  happens.
* Make leaf members `readonly`.
* Do not hand-write five levels of readonly for a type nobody mutates; the
  copy-don't-mutate habit from lesson 4 is doing most of the work, and the type
  is a backstop.

> ⚠️ **Common mistakes:** writing `readonly tags: string[]` and believing the
> array is protected; assuming `Object.freeze` fixes the depth problem (it is
> shallow too — lesson 7); and trying to hand-roll DeepReadonly before week 29.
""",
            warmup=[
                _q("`readonly tags: string[]` stops…",
                   ["push", "reassigning the tags member only", "everything", "nothing"], 1,
                   "The binding is protected, not the array."),
                _q("The fix is…",
                   ["Object.freeze", "readonly tags: readonly string[]", "as const on the interface",
                    "a class"], 1,
                   "One readonly per level."),
                _q("`readonly user: { name: string }` allows…",
                   ["nothing", "s.user.name = \"tom\"", "s.user = {...}", "both"], 1,
                   "The nested object was never made readonly."),
                _q("A type that applies readonly recursively is…",
                   ["ReadonlyArray", "DeepReadonly, built in week 29", "as const",
                    "Object.freeze"], 1,
                   "It needs mapped and conditional types."),
            ],
            exercises=[
                _ex("tscourse-w13-sh-1", "Watch the gap",
                    "The member is readonly. Push into the array it points at anyway.",
                    'interface Entry {\n  readonly desc: string;\n  readonly tags: string[];\n}\n'
                    'const e: Entry = { desc: "coffee", tags: ["food"] };\n'
                    'e.tags.push("home");\n'
                    'console.log(e.tags.join(","));\n',
                    'e.tags.push("home");', [("", "food,home")],
                    hints=["`readonly` stopped reassigning `e.tags`. It said nothing about the array.",
                           'Write e.tags.push("home");'],
                    difficulty="Medium"),
                _ex("tscourse-w13-sh-2", "Close it one level",
                    "Declare `tags` so the array itself cannot be modified either.",
                    'interface Entry {\n  readonly desc: string;\n  readonly tags: readonly string[];\n}\n'
                    'const e: Entry = { desc: "coffee", tags: ["food"] };\n'
                    'const next: Entry = { ...e, tags: [...e.tags, "home"] };\n'
                    'console.log(`${e.tags.length} ${next.tags.join(",")}`);\n',
                    'readonly tags: readonly string[];',
                    [("", "1 food,home")],
                    hints=["Two modifiers: one for the member, one for the array.",
                           "Write readonly tags: readonly string[];"],
                    difficulty="Medium"),
                _ex("tscourse-w13-sh-3", "Nested objects, same gap",
                    "Change the nested user's name, even though the member holding it is readonly.",
                    'interface State {\n  readonly user: { name: string };\n}\n'
                    'const s: State = { user: { name: "ada" } };\n'
                    's.user.name = "tom";\n'
                    'console.log(s.user.name);\n',
                    's.user.name = "tom";', [("", "tom")],
                    hints=["The member is readonly; the object it points at is not.",
                           'Write s.user.name = "tom";']),
                _ex("tscourse-w13-sh-4", "Deep, when you wrote the value yourself",
                    "Pin the nested config so even the inner member is readonly.",
                    'const CFG = { limits: { retries: 3 } } as const;\n'
                    'console.log(CFG.limits.retries);\n',
                    '{ limits: { retries: 3 } } as const',
                    [("", "3")],
                    hints=["A const assertion goes all the way down, unlike the readonly modifier.",
                           "Write { limits: { retries: 3 } } as const"]),
                _ex("tscourse-w13-sh-5", "A deliberate deep copy",
                    "Copy the state and its nested user, so changing the copy leaves the original alone.",
                    'const state = { user: { name: "ada" }, tags: ["x"] };\n'
                    'const copy = { ...state, user: { ...state.user } };\n'
                    'copy.user.name = "tom";\n'
                    'console.log(`${state.user.name} ${copy.user.name}`);\n',
                    'const copy = { ...state, user: { ...state.user } };',
                    [("", "ada tom")],
                    hints=["A single spread would share the user object.",
                           "Spread the outer object AND the nested one."],
                    difficulty="Medium"),
                _diagnose("tscourse-w13-sh-d1", "Now the array is protected too",
                          "TS2339: Property 'push' does not exist on type 'readonly string[]'.",
                          'interface Entry {\n  readonly desc: string;\n  readonly tags: readonly string[];\n}\n'
                          'function tagged(e: Entry, tag: string): Entry {\n'
                          '  e.tags.push(tag);\n'
                          '  return e;\n}\n'
                          'const e: Entry = { desc: "coffee", tags: ["food"] };\n'
                          'console.log(tagged(e, "home").tags.join(","));\n',
                          'interface Entry {\n  readonly desc: string;\n  readonly tags: readonly string[];\n}\n'
                          'function tagged(e: Entry, tag: string): Entry {\n'
                          '  return { ...e, tags: [...e.tags, tag] };\n}\n'
                          'const e: Entry = { desc: "coffee", tags: ["food"] };\n'
                          'console.log(tagged(e, "home").tags.join(","));\n',
                          [("", "food,home")],
                          hints=["The second `readonly` is doing its job — do not remove it.",
                                 "Return a new Entry with a new tags array.",
                                 "{ ...e, tags: [...e.tags, tag] }"],
                          difficulty="Medium"),
                _fix("tscourse-w13-sh-fix1", "Fix the type that only looked immutable",
                     "`Entry` marks both members readonly, but `tags` is a mutable array — so `addTag` pushes into the caller's own array and this prints `2 2` instead of `1 2`. Close the gap and build a new value.",
                     'interface Entry {\n  readonly desc: string;\n  readonly tags: string[];\n}\n'
                     'function addTag(e: Entry, tag: string): Entry {\n'
                     '  e.tags.push(tag);\n'
                     '  return e;\n}\n'
                     'const e: Entry = { desc: "coffee", tags: ["food"] };\n'
                     'const next = addTag(e, "home");\n'
                     'console.log(`${e.tags.length} ${next.tags.length}`);\n',
                     'interface Entry {\n  readonly desc: string;\n  readonly tags: readonly string[];\n}\n'
                     'function addTag(e: Entry, tag: string): Entry {\n'
                     '  return { ...e, tags: [...e.tags, tag] };\n}\n'
                     'const e: Entry = { desc: "coffee", tags: ["food"] };\n'
                     'const next = addTag(e, "home");\n'
                     'console.log(`${e.tags.length} ${next.tags.length}`);\n',
                     [("", "1 2")],
                     hints=["`readonly tags: string[]` protects the member, not the array — that is the whole lesson.",
                            "Make the array type readonly as well, and the compiler will reject the push.",
                            "Then return a new Entry with a new tags array."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Where does accidental mutation almost always happen?",
                   ["scalar members", "arrays held in readonly members", "class fields",
                    "return values"], 1,
                   "Which is why `readonly T[]` earns its keep first."),
                _q("Hand-writing five levels of readonly is…",
                   ["required", "usually not worth it — the copy habit does most of the work",
                    "impossible", "what DeepReadonly does at runtime"], 1,
                   "The type is a backstop, not the whole strategy."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w13-pure", "Pure functions",
            "Same input, same output, nothing else.",
            """
A function is **pure** when two things hold:

1. Given the same inputs it always returns the same output.
2. It changes nothing observable outside itself.

Everything in lessons 1-5 was in service of this. A function that mutates its
argument breaks rule 2; one that reads mutable outer state breaks rule 1.

```ts
// pure
function total(xs: readonly number[]): number {
  return xs.reduce((s, n) => s + n, 0);
}

// impure: reads and writes state outside itself
let running = 0;
function addAll(xs: readonly number[]): number {
  for (const n of xs) {
    running = running + n;
  }
  return running;
}
```

## How to catch impurity: call it twice

This is the practical test, and it needs no theory:

```ts
const xs = [1, 2, 3];
console.log(addAll(xs));    // 6
console.log(addAll(xs));    // 12  ← same input, different answer
```

`total` would print `6` twice. Any function whose answer depends on when you
called it is impure, and that is exactly the property that makes it hard to test
and hard to reason about.

## What counts as impure

* Mutating an argument, or anything reachable from one.
* Reading or writing a variable declared outside the function.
* `Math.random()`, `Date.now()`, `new Date()` — different answer each call.
* Reading stdin, writing a file, making a request.
* `console.log` — technically an effect. In practice nobody counts logging, and
  this course's exercises print their answers, so treat the top level of a
  program as the impure part and keep the helpers pure.

## Why it is worth the trouble

**Testable.** A pure function needs no setup: call it, check the result. Every
exercise in this course that uses `_fn`-style grading depends on this.

**Movable.** You can reorder, cache, or skip a pure call without changing the
program's meaning. That property has a name — **referential transparency** — and
it is what lets a compiler or a framework optimise around your code.

**Debuggable.** When a pure function is wrong, the bug is inside it. When an
impure one is wrong, the bug might be in the order somebody called it.

## The shape to aim for

Push effects to the edges. A pure core, with the reading, printing and mutating
in a thin shell around it:

```ts
const lines = fs.readFileSync(0, "utf8").trim().split("\\n");   // effect
const report = summarise(lines.map(parse));                     // pure
console.log(report);                                            // effect
```

Every capstone in this course is built that way, and the week 13 capstone makes
it explicit: `add` is pure, and the loop that reads stdin is where the impurity
lives.

> ⚠️ **Common mistakes:** calling a function pure because it returns something;
> hiding a mutation in a helper the pure function calls; and reaching for a
> module-level `let` as an accumulator when `reduce` would do.
""",
            warmup=[
                _q("A pure function…",
                   ["returns void", "gives the same output for the same input and changes nothing else",
                    "takes one argument", "is recursive"], 1,
                   "Both halves matter."),
                _q("The practical test for impurity is…",
                   ["read the types", "call it twice with the same input and compare",
                    "check the length", "run a linter"], 1,
                   "A different answer proves it."),
                _q("`Math.random()` inside a function makes it…",
                   ["pure", "impure — rule 1 fails", "faster", "readonly"], 1,
                   "Same input, different output."),
                _q("The recommended shape is…",
                   ["effects everywhere", "a pure core with effects at the edges",
                    "no functions", "all impure"], 1,
                   "Read, compute, print."),
            ],
            exercises=[
                _ex("tscourse-w13-pu-1", "A pure total",
                    "Fold the numbers without touching anything outside the function.",
                    'function total(xs: readonly number[]): number {\n'
                    '  return xs.reduce((s, n) => s + n, 0);\n}\n'
                    'const xs: readonly number[] = [1, 2, 3];\n'
                    'console.log(total(xs));\n'
                    'console.log(total(xs));\n',
                    'return xs.reduce((s, n) => s + n, 0);',
                    [("", "6\n6")],
                    hints=["A fold with a seed of 0 — no outer variable involved.",
                           "Called twice, it must give the same answer."]),
                _ex("tscourse-w13-pu-2", "Prove the impure one is impure",
                    "Call the accumulator twice with the same input, so the second answer exposes it.",
                    'let running = 0;\n'
                    'function addAll(xs: readonly number[]): number {\n'
                    '  for (const n of xs) {\n    running = running + n;\n  }\n'
                    '  return running;\n}\n'
                    'const xs: readonly number[] = [1, 2, 3];\n'
                    'console.log(addAll(xs));\n'
                    'console.log(addAll(xs));\n',
                    'console.log(addAll(xs));\nconsole.log(addAll(xs));',
                    [("", "6\n12")],
                    hints=["Two identical calls, one after the other.",
                           "The outer `running` survives between them, which is the bug."],
                    difficulty="Medium"),
                _ex("tscourse-w13-pu-3", "Make it pure",
                    "Rewrite the body so it depends on nothing but its argument.",
                    'function addAll(xs: readonly number[]): number {\n'
                    '  return xs.reduce((s, n) => s + n, 0);\n}\n'
                    'const xs: readonly number[] = [1, 2, 3];\n'
                    'console.log(addAll(xs));\n'
                    'console.log(addAll(xs));\n',
                    'return xs.reduce((s, n) => s + n, 0);',
                    [("", "6\n6")],
                    hints=["The accumulator belongs inside the fold, not outside the function.",
                           "reduce carries the running value for you."]),
                _ex("tscourse-w13-pu-4", "Pure, with a parameter instead of outer state",
                    "Take the starting value as a parameter, so the caller decides and nothing is remembered.",
                    'function addAll(xs: readonly number[], start: number): number {\n'
                    '  return xs.reduce((s, n) => s + n, start);\n}\n'
                    'const xs: readonly number[] = [1, 2, 3];\n'
                    'console.log(addAll(xs, 0));\n'
                    'console.log(addAll(xs, 100));\n',
                    'return xs.reduce((s, n) => s + n, start);',
                    [("", "6\n106")],
                    hints=["Whatever the function needed to remember becomes an argument.",
                           "Seed the reduce with `start`."],
                    difficulty="Medium"),
                _ex("tscourse-w13-pu-5", "A pure core with the effects outside",
                    "Write the pure `summarise`; the reading and printing stay where they are.",
                    _WORDS +
                    'function summarise(tags: readonly string[]): string {\n'
                    '  return `${tags.length}: ${[...tags].sort().join(",")}`;\n}\n'
                    'console.log(summarise(words));\n',
                    'return `${tags.length}: ${[...tags].sort().join(",")}`;',
                    [("home food fun", "3: food,fun,home"),
                     ("solo", "1: solo")],
                    hints=["The count, then a colon and a space, then the sorted tags joined with commas.",
                           "Sort a copy — the function must not disturb what it was given."],
                    difficulty="Medium"),
                _fix("tscourse-w13-pu-fix1", "Fix the helper that remembers",
                     "`label` keeps a counter outside itself, so the same entry gets a different label each time — this prints `1. coffee` then `2. coffee` instead of `1. coffee` twice.",
                     'let seen = 0;\n'
                     'function label(desc: string): string {\n'
                     '  seen = seen + 1;\n'
                     '  return `${seen}. ${desc}`;\n}\n'
                     'console.log(label("coffee"));\n'
                     'console.log(label("coffee"));\n',
                     'function label(desc: string, n: number): string {\n'
                     '  return `${n}. ${desc}`;\n}\n'
                     'console.log(label("coffee", 1));\n'
                     'console.log(label("coffee", 1));\n',
                     [("", "1. coffee\n1. coffee")],
                     hints=["The function's answer depends on how many times it has been called.",
                            "Whatever it was remembering should be a parameter instead.",
                            "Take the number as an argument and pass 1 at both call sites."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Referential transparency means…",
                   ["types are erased", "a call can be replaced by its result",
                    "the function is readonly", "no arguments"], 1,
                   "Which is what makes reordering and caching safe."),
                _q("When a pure function is wrong, the bug is…",
                   ["in the caller", "inside it", "in the order of calls", "unfindable"], 1,
                   "That is most of the debugging value."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w13-freeze", "`Object.freeze` vs `readonly`",
            "One is a runtime guard, the other is a compile-time check. They fail very differently.",
            """
`readonly` is a **type**. It is erased, so at runtime there is nothing there:

```ts
interface Entry { readonly cents: number; }
// compiles to nothing at all
```

`Object.freeze` is a **function**. It runs, and it makes an object's own
properties genuinely unwritable:

```ts
const o = { x: 1 };
Object.freeze(o);
console.log(Object.isFrozen(o));    // true
```

So: `readonly` catches *your* code before it ships and costs nothing;
`Object.freeze` catches *any* code at runtime and costs a call. They are
complementary, not alternatives.

## The part worth learning: freeze's two failure modes

Write to a frozen property and what happens depends on **strict mode**.

At the top level of these programs — which run as CommonJS, so sloppy mode —
the write is **silently ignored**:

```ts
const o = { x: 1 };
Object.freeze(o);
o.x = 5;
console.log(o.x);      // 1  — no error, no warning, nothing
```

Inside a class body — which is **always** strict, whatever surrounds it — the
same write **throws**:

```ts
class Box {
  poke(): string {
    const p = { y: 1 };
    Object.freeze(p);
    try {
      p.y = 9;
      return "no throw";
    } catch (e) {
      return "threw TypeError";     // this is what happens
    }
  }
}
```

Same code, two behaviours, and the sloppy one is worse: a silently dropped write
is the hardest kind of bug to find. This is the strongest available argument for
reaching for `readonly` **first** — a compile error has exactly one failure
mode, and you get it before the program runs.

## freeze is shallow too

```ts
const state = { tags: ["food"] };
Object.freeze(state);
state.tags.push("home");            // ✅ works — the ARRAY was not frozen
console.log(state.tags.length);     // 2
```

Freezing `state` made `state.tags` unwritable. It did nothing to the array that
`state.tags` points at. Exactly the same gap as lesson 5, at runtime this time,
and "deep freeze" means walking the whole structure yourself.

## Using freeze's return value gets you both

`Object.freeze` returns its argument with a read-only type, so if you use the
return value you get the compile-time check *as well*:

```ts
const f = Object.freeze({ x: 1 });
f.x = 5;
// ❌ TS2540: Cannot assign to 'x' because it is a read-only property.
```

That is the form to prefer when you do freeze something. (The type it returns is
`Readonly<T>` — a utility type, which is **next week**.)

## When to actually reach for freeze

Rarely, and deliberately:

* A genuinely shared constant that must not be edited by anyone, including code
  you did not write.
* Temporarily, while hunting an accidental mutation — freeze the value and see
  what breaks.
* At a library boundary, where a caller might mutate what you handed back.

For everything else, `readonly` plus the copy-don't-mutate habit is cheaper and
catches more, earlier.

> ⚠️ **Common mistakes:** expecting `readonly` to do anything at runtime;
> expecting `freeze` to report a failure (at the top level it will not);
> expecting `freeze` to be deep; and freezing in a hot path, where the cost is
> real and the benefit is not.
""",
            warmup=[
                _q("`readonly` at runtime is…",
                   ["a frozen object", "not there at all — it is erased", "a getter",
                    "a proxy"], 1,
                   "Compile time only."),
                _q("Writing to a frozen property at the top level of these programs…",
                   ["throws", "is silently ignored, because top-level code is sloppy mode",
                    "is a compile error", "succeeds"], 1,
                   "The worst failure mode there is."),
                _q("The same write inside a class method…",
                   ["is silently ignored", "throws a TypeError, because class bodies are always strict",
                    "succeeds", "is a compile error"], 1,
                   "Strict mode changes the behaviour, not the code."),
                _q("`Object.freeze` is…",
                   ["deep", "shallow — nested arrays and objects are untouched", "a type",
                    "erased"], 1,
                   "The same gap as lesson 5."),
            ],
            exercises=[
                _ex("tscourse-w13-fz-1", "The write that vanishes",
                    "Freeze the object, then try to change it and report what the property actually holds.",
                    'const o = { x: 1 };\n'
                    'Object.freeze(o);\n'
                    'o.x = 5;\n'
                    'console.log(o.x);\n',
                    'Object.freeze(o);', [("", "1")],
                    hints=["One call, before the assignment.",
                           "Top-level code here is sloppy mode, so the assignment is dropped without a word."],
                    difficulty="Medium"),
                _ex("tscourse-w13-fz-2", "Ask at runtime",
                    "Report whether each object is frozen.",
                    'const frozen = { x: 1 };\n'
                    'const open = { x: 1 };\n'
                    'Object.freeze(frozen);\n'
                    'console.log(`${Object.isFrozen(frozen)} ${Object.isFrozen(open)}`);\n',
                    'console.log(`${Object.isFrozen(frozen)} ${Object.isFrozen(open)}`);',
                    [("", "true false")],
                    hints=["A runtime question needs a runtime answer — there is a method for it.",
                           "Object.isFrozen, on each of the two."]),
                _ex("tscourse-w13-fz-3", "Where it does throw",
                    "Assign to the frozen property inside the class method, and let the catch report it.",
                    'class Box {\n'
                    '  poke(): string {\n'
                    '    const p: { y: number } = { y: 1 };\n'
                    '    Object.freeze(p);\n'
                    '    try {\n'
                    '      p.y = 9;\n'
                    '      return `no throw, y=${p.y}`;\n'
                    '    } catch (err) {\n'
                    '      return err instanceof TypeError ? "threw TypeError" : "threw something else";\n'
                    '    }\n'
                    '  }\n}\n'
                    'console.log(new Box().poke());\n',
                    'p.y = 9;', [("", "threw TypeError")],
                    hints=["A plain assignment — the point is where it sits, not how it is written.",
                           "A class body is always strict mode, so the frozen write is an error rather than a no-op.",
                           "Write p.y = 9;"],
                    difficulty="Medium"),
                _ex("tscourse-w13-fz-4", "freeze is shallow",
                    "Freeze the state, then modify the array it holds.",
                    'const state = { tags: ["food"] };\n'
                    'Object.freeze(state);\n'
                    'state.tags.push("home");\n'
                    'console.log(`${Object.isFrozen(state)} ${state.tags.join(",")}`);\n',
                    'state.tags.push("home");', [("", "true food,home")],
                    hints=["Freezing `state` made `state.tags` unwritable. The array is a different object.",
                           'Write state.tags.push("home");'],
                    difficulty="Medium"),
                _diagnose("tscourse-w13-fz-d1", "The return value that is typed",
                          "TS2540: Cannot assign to 'x' because it is a read-only property.",
                          'const f = Object.freeze({ x: 1 });\n'
                          'f.x = 5;\n'
                          'console.log(f.x);\n',
                          'const f = Object.freeze({ x: 1 });\n'
                          'const next = { ...f, x: 5 };\n'
                          'console.log(next.x);\n',
                          [("", "5")],
                          hints=["Using freeze's RETURN value is what got you a compile error instead of silence.",
                                 "The frozen object cannot change, so build a new one from it.",
                                 "Spread it and override x, then report the new object's value."],
                          difficulty="Medium"),
                _fix("tscourse-w13-fz-fix1", "Fix the guard that guarded nothing",
                     "`Object.freeze` was relied on to keep the config safe, but the write is at the top level so it is silently dropped and `bump` reports the unchanged value — this prints `3` twice. Use a type the compiler enforces and build a new config instead.",
                     'const CFG = { retries: 3 };\n'
                     'Object.freeze(CFG);\n'
                     'function bump(): number {\n'
                     '  CFG.retries = CFG.retries + 1;\n'
                     '  return CFG.retries;\n}\n'
                     'console.log(CFG.retries);\n'
                     'console.log(bump());\n',
                     'interface Config {\n  readonly retries: number;\n}\n'
                     'const CFG: Config = { retries: 3 };\n'
                     'function bump(c: Config): Config {\n'
                     '  return { ...c, retries: c.retries + 1 };\n}\n'
                     'console.log(CFG.retries);\n'
                     'console.log(bump(CFG).retries);\n',
                     [("", "3\n4")],
                     hints=["The freeze worked; the assignment was thrown away in silence, which is why nothing looked wrong.",
                            "Declare the config type with a readonly member so the compiler refuses the write.",
                            "Then make bump pure: take a config, return a new one with retries incremented."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Prefer `readonly` first because…",
                   ["it is faster at runtime", "a compile error has one failure mode, and arrives before the program runs",
                    "freeze is deprecated", "it is deep"], 1,
                   "Silence is the problem with freeze."),
                _q("Freeze earns its place when…",
                   ["always", "code you do not control might mutate what you handed out",
                    "never", "in a hot loop"], 1,
                   "A real boundary, not a default."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w13-history", "State as a sequence of values",
            "Undo, for free, because you chose the right shape.",
            """
Put the week together. If an update **returns a new value** instead of changing
the old one, then the old one is still there — and a list of old values is a
history.

## The update function

Every immutable update has the same shape:

```ts
interface Ledger {
  readonly entries: readonly Entry[];
}

function add(l: Ledger, e: Entry): Ledger {
  return { entries: [...l.entries, e] };
}
```

`(state, change) => newState`. That is a **reducer**, and it is the shape Redux,
`useReducer`, and every event-sourced system is built on. Nothing about it is
framework-specific; it falls out of lesson 4.

## Keeping the versions

```ts
const EMPTY: Ledger = { entries: [] };
let history: readonly Ledger[] = [EMPTY];

history = [...history, add(current, entry)];      // do
```

Note what this costs. `add` shares every entry that did not change, so a
hundred-version history of a hundred-entry ledger is a hundred small arrays of
pointers, not ten thousand copies of anything. Immutability is what makes
keeping the past affordable.

## Undo

```ts
history = history.slice(0, -1);
```

That is the whole feature. There is no undo *algorithm* — no inverse operation
to write per command, no "unadd", nothing to keep in step. You throw away the
last version and the previous one is already correct.

Compare the mutable version: to undo an `add` you must write a `remove` that
exactly reverses it, and then another inverse for every command you ever add,
and each one is a new place to get it wrong.

## Reading the current state

```ts
const current = history[history.length - 1] ?? EMPTY;
```

The `?? EMPTY` is not decoration — under `noUncheckedIndexedAccess` the index
gives `Ledger | undefined`, and defaulting to the empty ledger is both honest
and exactly right.

Guard the undo, too, or you can empty the history and lose your base state:

```ts
if (history.length > 1) {
  history = history.slice(0, -1);
}
```

## Where this goes

Two places, both later in the course:

* **Week 18** builds this properly as an undo/**redo** stack. Redo needs the
  versions you undid, so it is two stacks rather than one — a small extension,
  and a natural fit for the week that teaches stacks.
* **Week 14** gives you a better vocabulary for the update itself: `Partial<T>`
  for "some of the fields changed", so `update(state, patch)` can take exactly
  the changes rather than the whole new value.

> ⚠️ **Common mistakes:** mutating the state inside the update function, which
> silently corrupts every version in the history at once; forgetting to guard
> undo at the base state; and keeping a deep clone per version, which throws away
> the sharing that made this cheap.
""",
            warmup=[
                _q("`(state, change) => newState` is the shape of…",
                   ["a getter", "a reducer / immutable update", "a constructor", "a guard"], 1,
                   "The same shape every reducer has."),
                _q("Undo, given a history of versions, is…",
                   ["an inverse operation per command", "dropping the last version",
                    "a deep clone", "impossible"], 1,
                   "history.slice(0, -1)."),
                _q("Keeping every version is affordable because…",
                   ["versions are small numbers", "unchanged parts are SHARED between versions",
                    "of compression", "of freeze"], 1,
                   "Nothing mutates, so sharing is safe."),
                _q("Mutating state inside the update function…",
                   ["is fine", "corrupts every version in the history at once", "is a type error",
                    "only affects the newest"], 1,
                   "They all share the mutated part."),
            ],
            exercises=[
                _ex("tscourse-w13-hi-1", "An immutable update",
                    "Return a new ledger with the entry appended.",
                    'interface Ledger {\n  readonly entries: readonly string[];\n}\n'
                    'function add(l: Ledger, e: string): Ledger {\n'
                    '  return { entries: [...l.entries, e] };\n}\n'
                    'const empty: Ledger = { entries: [] };\n'
                    'const one = add(empty, "coffee");\n'
                    'const two = add(one, "rent");\n'
                    'console.log(`${empty.entries.length} ${one.entries.length} ${two.entries.length}`);\n',
                    'return { entries: [...l.entries, e] };',
                    [("", "0 1 2")],
                    hints=["A new object, with a new array made from the old one plus the entry.",
                           "All three ledgers must still be readable afterwards."]),
                _ex("tscourse-w13-hi-2", "Keep the versions",
                    "Append the new version to the history instead of replacing it.",
                    'interface Ledger {\n  readonly entries: readonly string[];\n}\n'
                    'function add(l: Ledger, e: string): Ledger {\n'
                    '  return { entries: [...l.entries, e] };\n}\n'
                    'const EMPTY: Ledger = { entries: [] };\n'
                    'let history: readonly Ledger[] = [EMPTY];\n'
                    'for (const e of ["coffee", "rent"]) {\n'
                    '  const current = history[history.length - 1] ?? EMPTY;\n'
                    '  history = [...history, add(current, e)];\n'
                    '}\n'
                    'console.log(history.length);\n',
                    'history = [...history, add(current, e)];',
                    [("", "3")],
                    hints=["The history starts with one version, and each add makes one more.",
                           "Spread the old history and put the new version on the end."],
                    difficulty="Medium"),
                _ex("tscourse-w13-hi-3", "Undo",
                    "Step back one version by dropping the last one.",
                    'interface Ledger {\n  readonly entries: readonly string[];\n}\n'
                    'const EMPTY: Ledger = { entries: [] };\n'
                    'let history: readonly Ledger[] = [\n'
                    '  EMPTY,\n'
                    '  { entries: ["coffee"] },\n'
                    '  { entries: ["coffee", "rent"] },\n'
                    '];\n'
                    'history = history.slice(0, -1);\n'
                    'const current = history[history.length - 1] ?? EMPTY;\n'
                    'console.log(`${history.length} ${current.entries.join(",")}`);\n',
                    'history = history.slice(0, -1);',
                    [("", "2 coffee")],
                    hints=["Everything except the last element.",
                           "slice with a negative end index does exactly that."],
                    difficulty="Medium"),
                _ex("tscourse-w13-hi-4", "Guard the base state",
                    "Only undo when there is something to undo, so the base version survives.",
                    'interface Ledger {\n  readonly entries: readonly string[];\n}\n'
                    'const EMPTY: Ledger = { entries: [] };\n'
                    'let history: readonly Ledger[] = [EMPTY];\n'
                    'for (const cmd of ["undo", "undo"]) {\n'
                    '  if (cmd === "undo" && history.length > 1) {\n'
                    '    history = history.slice(0, -1);\n'
                    '  }\n'
                    '}\n'
                    'console.log(history.length);\n',
                    'history.length > 1', [("", "1")],
                    hints=["Undoing past the first version would leave you with nothing.",
                           "There must be more than one version for an undo to be possible."],
                    difficulty="Medium"),
                _ex("tscourse-w13-hi-5", "Do, undo, do",
                    "Read the current version off the end of the history each time round.",
                    'interface Ledger {\n  readonly entries: readonly string[];\n}\n'
                    'function add(l: Ledger, e: string): Ledger {\n'
                    '  return { entries: [...l.entries, e] };\n}\n'
                    'const EMPTY: Ledger = { entries: [] };\n'
                    'let history: readonly Ledger[] = [EMPTY];\n'
                    'for (const cmd of ["coffee", "rent", "undo", "book"]) {\n'
                    '  if (cmd === "undo") {\n'
                    '    if (history.length > 1) {\n      history = history.slice(0, -1);\n    }\n'
                    '  } else {\n'
                    '    const current = history[history.length - 1] ?? EMPTY;\n'
                    '    history = [...history, add(current, cmd)];\n'
                    '  }\n'
                    '}\n'
                    'const final = history[history.length - 1] ?? EMPTY;\n'
                    'console.log(final.entries.join(","));\n',
                    'const current = history[history.length - 1] ?? EMPTY;',
                    [("", "coffee,book")],
                    hints=["The version to build on is always the last one in the history.",
                           "Indexing may find nothing, so default to the empty ledger.",
                           "Write const current = history[history.length - 1] ?? EMPTY;"],
                    difficulty="Medium"),
                _fix("tscourse-w13-hi-fix1", "Fix the update that corrupted the history",
                     "`add` pushes into the ledger's own array instead of building a new one, so every version in the history shares it and they all show the same entries — this prints `2 2` instead of `1 2`.",
                     'interface Ledger {\n  entries: string[];\n}\n'
                     'function add(l: Ledger, e: string): Ledger {\n'
                     '  l.entries.push(e);\n'
                     '  return l;\n}\n'
                     'const one: Ledger = { entries: ["coffee"] };\n'
                     'const two = add(one, "rent");\n'
                     'console.log(`${one.entries.length} ${two.entries.length}`);\n',
                     'interface Ledger {\n  readonly entries: readonly string[];\n}\n'
                     'function add(l: Ledger, e: string): Ledger {\n'
                     '  return { entries: [...l.entries, e] };\n}\n'
                     'const one: Ledger = { entries: ["coffee"] };\n'
                     'const two = add(one, "rent");\n'
                     'console.log(`${one.entries.length} ${two.entries.length}`);\n',
                     [("", "1 2")],
                     hints=["`one` and `two` are the same object, so there is only ever one version.",
                            "Return a new ledger with a new entries array.",
                            "Then make both the member and the array readonly, so a future edit cannot push again."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The advantage over writing an inverse per command is…",
                   ["speed", "there is no inverse to write, and nothing to keep in step",
                    "less memory", "type safety"], 1,
                   "You throw the version away and the previous one is already right."),
                _q("Redo needs…",
                   ["nothing extra", "the versions you undid — so two stacks, in week 18",
                    "a deep clone", "Object.freeze"], 1,
                   "A small extension of the same idea."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #13 — an immutable ledger with undo",
        """
Week 11's `Ledger` was a class that mutated a private array. This week it stops
changing at all — and gets undo as a side effect.

Input is one command per line, either `add <desc> <amount>` or `undo`:

```
add coffee 3.25
add rent 900
add lunch 9.50
undo
add book 12
```

Print exactly:

```
Entries:  3
Total:    $915.25
Log:      coffee, rent, book
Undos:    1
```

Build this scaffolding:

```ts
interface Entry {
  readonly desc: string;
  readonly cents: number;
}
interface Ledger {
  readonly entries: readonly Entry[];
}
function add(l: Ledger, desc: string, cents: number): Ledger   // pure
function total(l: Ledger): number                              // in CENTS
const EMPTY: Ledger = { entries: [] };
```

Rules:

- **Nothing mutates.** `add` returns a new `Ledger`; there is no `push` anywhere
  in the file except the spread that builds a new array. Both `Entry` members,
  the `entries` member and the array itself are `readonly` — all four.
- The driver keeps `let history: readonly Ledger[] = [EMPTY]`. `add` appends a
  version; `undo` drops the last one.
- **`undo` at the base state does nothing** and does not count towards `Undos`.
  Only undos that actually stepped back are counted.
- Read the current version as `history[history.length - 1] ?? EMPTY` — indexing
  gives `Ledger | undefined`, and the empty ledger is the honest default.
- Money is integer cents: `Math.round(Number(...) * 100)`.
- `Log` is the final ledger's descriptions in order, joined with `, `.
""",
        _ch("tscourse-w13-capstone", "Budget Buddy #13", "Medium",
            "Write the immutable ledger types, the pure add and total, and the empty base state.",
            _FS + 'interface Entry {\n'
            '  readonly desc: string;\n  readonly cents: number;\n}\n'
            'interface Ledger {\n  readonly entries: readonly Entry[];\n}\n'
            'function add(l: Ledger, desc: string, cents: number): Ledger {\n'
            '  return { entries: [...l.entries, { desc, cents }] };\n}\n'
            'function total(l: Ledger): number {\n'
            '  return l.entries.reduce((s, e) => s + e.cents, 0);\n}\n'
            'const EMPTY: Ledger = { entries: [] };\n'
            'let history: readonly Ledger[] = [EMPTY];\n'
            'let undos = 0;\n'
            'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
            '  const p = line.trim().split(" ");\n'
            '  const cmd = p[0] ?? "";\n'
            '  if (cmd === "undo") {\n'
            '    if (history.length > 1) {\n'
            '      history = history.slice(0, -1);\n'
            '      undos = undos + 1;\n'
            '    }\n'
            '  } else if (cmd === "add") {\n'
            '    const current = history[history.length - 1] ?? EMPTY;\n'
            '    const cents = Math.round(Number(p[2] ?? "0") * 100);\n'
            '    history = [...history, add(current, p[1] ?? "", cents)];\n'
            '  }\n}\n'
            'const final = history[history.length - 1] ?? EMPTY;\n'
            'console.log(`Entries:  ${final.entries.length}`);\n'
            'console.log(`Total:    $${(total(final) / 100).toFixed(2)}`);\n'
            'console.log(`Log:      ${final.entries.map((e) => e.desc).join(", ")}`);\n'
            'console.log(`Undos:    ${undos}`);\n',
            'interface Entry {\n'
            '  readonly desc: string;\n  readonly cents: number;\n}\n'
            'interface Ledger {\n  readonly entries: readonly Entry[];\n}\n'
            'function add(l: Ledger, desc: string, cents: number): Ledger {\n'
            '  return { entries: [...l.entries, { desc, cents }] };\n}\n'
            'function total(l: Ledger): number {\n'
            '  return l.entries.reduce((s, e) => s + e.cents, 0);\n}\n'
            'const EMPTY: Ledger = { entries: [] };',
            [("add coffee 3.25\nadd rent 900\nadd lunch 9.50\nundo\nadd book 12",
              "Entries:  3\nTotal:    $915.25\nLog:      coffee, rent, book\nUndos:    1"),
             ("add tea 2",
              "Entries:  1\nTotal:    $2.00\nLog:      tea\nUndos:    0"),
             ("undo\nadd tea 2",
              "Entries:  1\nTotal:    $2.00\nLog:      tea\nUndos:    0"),
             ("add a 1\nundo\nadd b 2\nundo\nadd c 3",
              "Entries:  1\nTotal:    $3.00\nLog:      c\nUndos:    2")],
            hints=["All four readonlys matter: both Entry members, the entries member, AND the array (`readonly Entry[]`).",
                   "`add` builds a whole new Ledger: { entries: [...l.entries, { desc, cents }] }.",
                   "`total` is week 8's reduce over e.cents, seeded with 0.",
                   "EMPTY is the base version the history starts with, and the default when indexing finds nothing.",
                   "The third test case is the guard: an undo with only the base version present must change nothing and must not count.",
                   "Math.round(Number(p[2] ?? \"0\") * 100) turns \"3.25\" into 325."]),
        example_io="Entries:  3\nTotal:    $915.25\nLog:      coffee, rent, book\nUndos:    1",
        rubric=["Entry and Ledger are fully readonly, including the array element type",
                "add is pure: it returns a new Ledger and never touches the one it was given",
                "the history is a readonly array of versions, reassigned rather than mutated",
                "undo drops the last version with slice(0, -1)",
                "undo at the base state is a no-op and is not counted",
                "the current version is read with ?? EMPTY rather than a ! assertion",
                "money is integer cents throughout"],
        stretch=_ch("tscourse-w13-capstone-stretch", "Budget Buddy #13 (stretch)", "Medium",
                    "Add a pure `remove(l: Ledger, desc: string): Ledger` that returns a new ledger "
                    "with every entry of that description dropped, and support a `remove <desc>` "
                    "command. Because it pushes a version like any other command, `undo` works on "
                    "it for free — no inverse operation needed.",
                    _FS + 'interface Entry {\n'
                    '  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'interface Ledger {\n  readonly entries: readonly Entry[];\n}\n'
                    'function add(l: Ledger, desc: string, cents: number): Ledger {\n'
                    '  return { entries: [...l.entries, { desc, cents }] };\n}\n'
                    'function remove(l: Ledger, desc: string): Ledger {\n'
                    '  return { entries: l.entries.filter((e) => e.desc !== desc) };\n}\n'
                    'function total(l: Ledger): number {\n'
                    '  return l.entries.reduce((s, e) => s + e.cents, 0);\n}\n'
                    'const EMPTY: Ledger = { entries: [] };\n'
                    'let history: readonly Ledger[] = [EMPTY];\n'
                    'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  const cmd = p[0] ?? "";\n'
                    '  const current = history[history.length - 1] ?? EMPTY;\n'
                    '  if (cmd === "undo") {\n'
                    '    if (history.length > 1) {\n      history = history.slice(0, -1);\n    }\n'
                    '  } else if (cmd === "remove") {\n'
                    '    history = [...history, remove(current, p[1] ?? "")];\n'
                    '  } else if (cmd === "add") {\n'
                    '    const cents = Math.round(Number(p[2] ?? "0") * 100);\n'
                    '    history = [...history, add(current, p[1] ?? "", cents)];\n'
                    '  }\n}\n'
                    'const final = history[history.length - 1] ?? EMPTY;\n'
                    'console.log(`Entries:  ${final.entries.length}`);\n'
                    'console.log(`Total:    $${(total(final) / 100).toFixed(2)}`);\n'
                    'console.log(`Log:      ${final.entries.map((e) => e.desc).join(", ")}`);\n',
                    'function remove(l: Ledger, desc: string): Ledger {\n'
                    '  return { entries: l.entries.filter((e) => e.desc !== desc) };\n}',
                    [("add coffee 3.25\nadd rent 900\nadd coffee 4\nremove coffee",
                      "Entries:  1\nTotal:    $900.00\nLog:      rent"),
                     ("add coffee 3.25\nadd rent 900\nremove coffee\nundo",
                      "Entries:  2\nTotal:    $903.25\nLog:      coffee, rent")],
                    hints=["filter already returns a new array, so no spread is needed around it.",
                           "Keep every entry whose desc is NOT the one being removed.",
                           "The second test case is the payoff: undo reverses the remove without any code that knows how to un-remove."]),
    ),
))
