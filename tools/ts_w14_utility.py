# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 14 — utility types.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THE ROADMAP CALLS THIS "the natural first home for `design` at volume", and it
# is — but the week is deliberately NOT all type-level. Utility types change the
# shape of values you then build and print, so most exercises here are ordinary
# stdout programs whose difficulty lives in the annotation.
#
# Three runtime facts this week is built on, all checked against the real runner:
#
#   1. `Omit` is a TYPE, not a runtime filter. A function returning
#      `Omit<Entry, "secret">` that does `return { ...e }` compiles cleanly and
#      still carries `secret` at runtime (`Object.keys` proves it). That is the
#      w14-pickomit fix, and it is the sharpest available restatement of week 12
#      lesson 2 — annotating never reshapes a value.
#   2. `Readonly<T>` is shallow, exactly like the `readonly` modifier in week 13:
#      `s.tags.push(...)` on a `Readonly<State>` runs fine.
#   3. `Parameters<typeof f>` is a real tuple, so `f(...args)` works — which is
#      what makes the fn-types lesson gradeable by stdout rather than assertions.
#
# `Omit`'s key is NOT constrained (a typo silently omits nothing) while `Pick`'s
# IS (TS2344). That asymmetry is the pickomit lesson's main teaching point.
# ---------------------------------------------------------------------------

# --- Week 14 --------------------------------------------------------------
_WEEKS.append(_week(
    14, 4, _M4,
    "Utility Types",
    "Reshape existing types with Partial, Pick, Omit, and Record — and know when a purpose-built type reads better.",
    """
Here is a shape of code you have almost certainly written:

```ts
interface Entry       { id: string; desc: string; cents: number; }
interface EntryCreate { desc: string; cents: number; }
interface EntryPatch  { desc?: string; cents?: number; }
interface EntryRow    { desc: string; cents: number; }
```

Four types describing one thing. They agree today. In three months somebody adds
`tag: string` to `Entry`, updates two of the four, and now `EntryPatch` cannot
express a change that the application definitely makes — and nothing reported it,
because all four are perfectly valid types.

The fix is to stop writing them and start **computing** them:

```ts
interface Entry { id: string; desc: string; cents: number; tag: string; }

type EntryCreate = Omit<Entry, "id">;
type EntryPatch  = Partial<Omit<Entry, "id">>;
type EntryRow    = Pick<Entry, "desc" | "cents">;
```

Now `Entry` is the single source of truth. Add `tag` and all three follow. Delete
`cents` and everything that used it stops compiling — which is exactly what you
want, because those are the places that need attention.

**You already do this.** Week 10 gave you `keyof Entry` and `Entry["cents"]`,
and both are derived types. This week is the standard library of such
derivations: about ten of them, all built into TypeScript, no import needed.

The ones worth knowing cold:

| | |
|---|---|
| `Partial<T>` / `Required<T>` | make every member optional / required |
| `Readonly<T>` | make every member readonly (week 13's modifier, as a type) |
| `Pick<T, K>` / `Omit<T, K>` | keep only these members / drop these members |
| `Record<K, V>` | an object type with these keys and that value type |
| `Exclude<U, X>` / `Extract<U, X>` | filter a **union** down |
| `ReturnType<F>` / `Parameters<F>` | pull a function's return type / arguments |

Two habits matter more than memorising them. First, **`Pick` checks its keys and
`Omit` does not** — a typo in an `Omit` silently omits nothing. Second, a chain
of four utilities is often less readable than the type written out; lesson 8 is
about knowing when to stop.

⏱️ Budget about **nine hours**. Much of this week is graded by the type-checker.
""",
    objectives=[
        "Say why hand-writing four related types is a maintenance bug rather than a style choice",
        "Recognise `keyof` and indexed access as the derived types you already use",
        "Use `Partial<T>` for a patch API, and handle the `| undefined` it introduces",
        "Use `Required<T>`, and say what it does to an optional member",
        "Use `Readonly<T>`, and say why it is shallow",
        "Choose between `Pick` and `Omit`, and explain why only one of them checks its keys",
        "Say why `Omit` does not remove a property at runtime",
        "Use `Record<K, V>`, and predict whether a lookup is `V` or `V | undefined`",
        "Filter a union with `Exclude`, and narrow a discriminated union with `Extract`",
        "Derive a type from a function with `ReturnType<typeof f>` and `Parameters<typeof f>`",
        "Decide when a derived type earns its place and when a purpose-built type reads better",
    ],
    why="This is the week that stops types from drifting. Every real codebase has a core entity and a dozen views of it — create, update, summary, API response, form state — and the difference between deriving them and copying them is whether a change to the entity is a two-line edit or a three-day bug hunt.",
    est_minutes=580,
    glossary=[
        _gloss("utility type", "A generic type built into TypeScript that computes a new type from an existing one."),
        _gloss("derived type", "Any type computed from another rather than written out. `keyof T` and `T[K]` are the simplest."),
        _gloss("single source of truth", "One declaration every related type is computed from."),
        _gloss("Partial<T>", "Every member of T made optional."),
        _gloss("Required<T>", "Every member of T made required — the inverse of Partial."),
        _gloss("Readonly<T>", "Every member of T made readonly. Shallow, like the modifier."),
        _gloss("Pick<T, K>", "T with only the members named in K. K is constrained to keyof T (TS2344 otherwise)."),
        _gloss("Omit<T, K>", "T without the members named in K. K is NOT constrained — a typo omits nothing."),
        _gloss("Record<K, V>", "An object type with keys K and values V. `Record<\"a\"|\"b\", number>` has known members."),
        _gloss("Exclude<U, X>", "The union U with every member assignable to X removed."),
        _gloss("Extract<U, X>", "The union U with only the members assignable to X kept."),
        _gloss("ReturnType<F>", "The type a function type F returns."),
        _gloss("Parameters<F>", "A tuple of F's parameter types, so `f(...args)` works."),
        _gloss("typeof (type position)", "`typeof f` is the TYPE of the value f — the bridge into ReturnType and Parameters."),
        _gloss("patch object", "A value carrying only the members that changed. `Partial<T>` is its type."),
        _gloss("keyof T", "The union of T's key names (week 10)."),
        _gloss("indexed access T[K]", "The type of T's K member (week 10)."),
        _gloss("index signature", "`[k: string]: V` — any string key allowed. `Record<string, V>` produces one."),
        _gloss("composition (of utilities)", "Nesting them: `Partial<Omit<Entry, \"id\">>`. Readable up to about two."),
    ],
    cheatsheet="""
```ts
interface Entry {
  id: string;
  desc: string;
  cents: number;
  tag?: string;
}

// ---- what you already had (week 10) -------------------------------------
type Keys  = keyof Entry;          // "id" | "desc" | "cents" | "tag"
type Cents = Entry["cents"];       // number

// ---- optional / required / readonly --------------------------------------
type Draft = Partial<Entry>;       // every member optional; every READ is `| undefined`
type Firm  = Required<Entry>;      // every member required — tag is no longer optional
type Frozen = Readonly<Entry>;     // every member readonly (SHALLOW)

// ---- choosing members ----------------------------------------------------
type Row    = Pick<Entry, "desc" | "cents">;    // { desc: string; cents: number }
type Create = Omit<Entry, "id">;                // everything except id
// type Bad = Pick<Entry, "nope">;   // ❌ TS2344 — Pick's key is constrained
// type Oops = Omit<Entry, "nope">;  // ✅ compiles, omits NOTHING — the usual bug

// Omit is a TYPE. It does not strip anything at runtime:
function publish(e: Entry): Omit<Entry, "id"> {
  return { ...e };                 // compiles — and `id` is still there at runtime!
}

// ---- Record --------------------------------------------------------------
type Cat = "food" | "fun";
const totals: Record<Cat, number> = { food: 0, fun: 0 };   // miss one -> TS2741
totals.food;                       // number — known member, no `| undefined`
const loose: Record<string, number> = {};
loose.anything;                    // number | undefined — it is an index signature

// ---- filtering a UNION ---------------------------------------------------
type Away = Exclude<Cat, "fun">;   // "food"
type Action = { kind: "add"; amount: number } | { kind: "del"; id: string };
type Add = Extract<Action, { kind: "add" }>;   // just the add member

// ---- from a function -----------------------------------------------------
function parse(line: string): { desc: string; cents: number } { … }
type Parsed = ReturnType<typeof parse>;        // { desc: string; cents: number }
type Args   = Parameters<typeof parse>;        // [line: string]
const args: Args = ["coffee 3.25"];
parse(...args);                                 // a real tuple, so spread works

// ---- composing, and knowing when to stop --------------------------------
type Patch = Partial<Omit<Entry, "id">>;              // ✅ reads fine
// type Ugh = Partial<Omit<Pick<Entry, "desc" | "cents" | "id">, "id">>;   // write it out
```
""",
    self_check=[
        "Can you say what goes wrong when four related types are written out by hand?",
        "Can you name two derived types you already used in week 10?",
        "Can you write a patch function taking `Partial<Entry>` and applying it with a spread?",
        "Can you say why every read off a `Partial<T>` is `| undefined`?",
        "Can you say what `Required<T>` does to `tag?: string`?",
        "Can you say why `Readonly<T>` does not stop `s.tags.push(...)`?",
        "Can you say which of `Pick` and `Omit` checks its key argument, and what the other one does on a typo?",
        "Can you explain why a function returning `Omit<Entry, \"secret\">` can still leak `secret`?",
        "Can you say when `Record<K, V>` gives you `V` and when it gives you `V | undefined`?",
        "Can you filter a union with `Exclude`, and pull one member of a discriminated union with `Extract`?",
        "Can you write the type of a function's return value without repeating it?",
        "Can you name a case where a hand-written type reads better than a derived one?",
    ],
    review=[
        _q("Hand-writing four related types is a problem because…",
           ["it is slow to compile", "they drift apart and every one of them stays valid",
            "it is not allowed", "utilities are faster"], 1,
           "Nothing reports the disagreement."),
        _q("`keyof Entry` and `Entry[\"cents\"]` are…",
           ["utility types", "derived types you already met in week 10", "new this week",
            "runtime values"], 1,
           "This week is the standard library of the same idea."),
        _q("`Partial<Entry>` makes every member…",
           ["readonly", "optional", "required", "a union"], 1,
           "Which is what a patch object needs."),
        _q("Reading `p.cents` off a `Partial<Entry>` gives…",
           ["number", "number | undefined", "never", "unknown"], 1,
           "Optional means it might not be there."),
        _q("`Required<T>` where T has `tag?: string` gives tag the type…",
           ["string | undefined", "string, and it is now required", "never", "unknown"], 1,
           "The inverse of Partial."),
        _q("`Readonly<State>` where State has `tags: string[]` stops…",
           ["tags.push(...)", "reassigning s.tags, and nothing deeper", "everything", "nothing"], 1,
           "Shallow, exactly like week 13's modifier."),
        _q("`Pick<Entry, \"nope\">` gives…",
           ["an empty type", "TS2344 — the key is constrained to keyof Entry", "no error",
            "never"], 1,
           "Pick checks its keys."),
        _q("`Omit<Entry, \"nope\">` gives…",
           ["TS2344", "no error at all — and omits nothing", "an empty type", "never"], 1,
           "The asymmetry that catches people."),
        _q("A function returning `Omit<Entry, \"secret\">` that does `return { ...e }`…",
           ["strips secret", "compiles, and still carries secret at runtime",
            "is a type error", "throws"], 1,
           "Omit is a type. Annotating never reshapes a value."),
        _q("`Record<\"food\" | \"fun\", number>` missing one key is…",
           ["allowed", "TS2741", "TS2344", "an index signature"], 1,
           "Union keys become known, required members."),
        _q("`totals.food` on a `Record<\"food\"|\"fun\", number>` is typed…",
           ["number | undefined", "number", "never", "unknown"], 1,
           "A known member, so noUncheckedIndexedAccess does not apply."),
        _q("`loose.anything` on a `Record<string, number>` is typed…",
           ["number", "number | undefined", "never", "any"], 1,
           "A string key is an index signature."),
        _q("`Exclude<\"a\" | \"b\" | \"c\", \"c\">` is…",
           ['"c"', '"a" | "b"', "never", "string"], 1,
           "It filters a union, not an object."),
        _q("`Extract<Action, { kind: \"add\" }>` gives…",
           ["the kind member", "just the union member whose kind is \"add\"", "never",
            "all members"], 1,
           "Which is how you name one arm of a discriminated union."),
        _q("`ReturnType<typeof parse>` needs `typeof` because…",
           ["it is faster", "ReturnType takes a TYPE, and parse is a value",
            "of generics", "it is optional"], 1,
           "`typeof parse` bridges from the value to its type."),
        _q("`Parameters<typeof f>` is…",
           ["an object", "a tuple, so f(...args) works", "a union", "never"], 1,
           "Which makes it usable at runtime, not just decorative."),
        _q("A chain of four nested utilities is usually…",
           ["ideal", "less readable than writing the type out", "faster", "required"], 1,
           "Derive when the relationship must hold; write it out when it need not."),
    ],
    milestone="Budget Buddy has a real update API. `EntryPatch` is computed from `Entry`, so a new field is patchable the moment it exists and nobody has to remember to add it in a second place. The summary and the per-category totals are derived the same way.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w14-why", "Types computed from other types",
            "You have been doing this since week 10.",
            """
Before naming a single utility type, notice that you already write derived types.

```ts
interface Entry {
  desc: string;
  cents: number;
}

type Keys = keyof Entry;          // "desc" | "cents"
type Cents = Entry["cents"];      // number
```

Neither of those was written out. Both are **computed** from `Entry`, so both
follow it automatically. `typeof` does the same thing from a value:

```ts
const DEFAULTS = { retries: 3, mode: "fast" };
type Defaults = typeof DEFAULTS;   // { retries: number; mode: string }
```

## The problem this solves

Write related types by hand and they rot:

```ts
interface Entry       { id: string; desc: string; cents: number; }
interface EntryUpdate { desc: string; cents: number; }
```

Add `tag` to `Entry`. `EntryUpdate` is still a perfectly valid type — it just no
longer describes an update. Nothing fails to compile. The application quietly
cannot change a tag, and you find out from a bug report.

Derive it instead and there is nothing to keep in step:

```ts
type EntryUpdate = Omit<Entry, "id">;
```

## The rule of thumb

**Derive when a relationship must hold.** "An update is an entry without its id"
is a relationship; encode it and the compiler maintains it.

**Write it out when the shapes are independent.** If two types happen to look
alike today but are free to diverge — a database row and an API response, say —
tying them together creates a false coupling that will hurt later. Lesson 8
returns to this.

## What is coming

All of these are built in; there is nothing to install or import:

* `Partial`, `Required`, `Readonly` — flip a modifier on every member.
* `Pick`, `Omit` — choose members.
* `Record` — build an object type from keys and a value type.
* `Exclude`, `Extract` — filter a union.
* `ReturnType`, `Parameters` — reach into a function type.

Each is a handful of characters, and each replaces a type somebody would
otherwise have to maintain.

> ⚠️ **Common mistakes:** deriving types that are only coincidentally similar;
> forgetting that `typeof` in a *type* position takes a name, not an expression
> (`typeof xs[0]` is not what you think); and assuming a derived type has runtime
> behaviour — it has none.
""",
            warmup=[
                _q("`keyof Entry` is…",
                   ["a value", "a derived type — the union of Entry's key names", "an array",
                    "a utility function"], 1,
                   "Week 10 already had it."),
                _q("`typeof DEFAULTS` in a type position gives…",
                   ['the string "object"', "the TYPE of the DEFAULTS value", "a union",
                    "never"], 1,
                   "The bridge from a value to its type."),
                _q("A hand-written duplicate type rots because…",
                   ["it is slow", "it stays valid while no longer describing anything",
                    "it errors", "of generics"], 1,
                   "Validity is not correctness."),
                _q("Derive a type when…",
                   ["always", "a relationship between the two must hold",
                    "never", "the type is short"], 1,
                   "Coincidental similarity is not a relationship."),
            ],
            exercises=[
                _ex("tscourse-w14-wh-1", "A type from a member",
                    "Declare the money type by reading it off the interface instead of writing `number`.",
                    'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                    'type Cents = Entry["cents"];\n'
                    'function money(c: Cents): string {\n'
                    '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                    'console.log(money(325));\n',
                    'type Cents = Entry["cents"];', [("", "$3.25")],
                    hints=["Week 10's indexed access, with the member name as a string literal.",
                           'Write type Cents = Entry["cents"];']),
                _ex("tscourse-w14-wh-2", "A type from the keys",
                    "Type the field parameter as the union of the interface's key names.",
                    'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                    'const e: Entry = { desc: "coffee", cents: 325 };\n'
                    'function show(field: keyof Entry): string {\n'
                    '  return String(e[field]);\n}\n'
                    'console.log(`${show("desc")} ${show("cents")}`);\n',
                    'field: keyof Entry', [("", "coffee 325")],
                    hints=["The union of key names, derived rather than written out.",
                           "Write field: keyof Entry"]),
                _ex("tscourse-w14-wh-3", "A type from a value",
                    "Derive the config type from the config value.",
                    'const DEFAULTS = { retries: 3, mode: "fast" };\n'
                    'type Defaults = typeof DEFAULTS;\n'
                    'function describe(d: Defaults): string {\n'
                    '  return `${d.mode} x${d.retries}`;\n}\n'
                    'console.log(describe(DEFAULTS));\n'
                    'console.log(describe({ retries: 1, mode: "slow" }));\n',
                    'type Defaults = typeof DEFAULTS;',
                    [("", "fast x3\nslow x1")],
                    hints=["`typeof` in a type position takes the name of a value.",
                           "Write type Defaults = typeof DEFAULTS;"]),
                _predict("tscourse-w14-wh-p1", "An element of the key union",
                         'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                         'const keys: (keyof Entry)[] = ["desc", "cents"];\n'
                         'const first = keys[0];\n',
                         "first", '"desc" | "cents" | undefined',
                         why="Two things at once: what `keyof Entry` expands to, and what "
                             "indexing an array adds to it.",
                         hints=["`keyof Entry` is a union of the two key names as literal types.",
                                "Indexing may find nothing, under noUncheckedIndexedAccess.",
                                'Write "desc" | "cents" | undefined.'],
                         difficulty="Medium"),
                _types("tscourse-w14-wh-t1", "Name the key union exactly",
                       "Write `Keys` so it is the union of the interface's key names — derived, "
                       "not typed out by hand.",
                       'interface Entry {\n  desc: string;\n  cents: number;\n  tag: string;\n}\n'
                       'type Keys = keyof Entry;\n',
                       'keyof Entry',
                       """
type _1 = Expect<Equal<Keys, "desc" | "cents" | "tag">>;
""",
                       hints=["One operator and the interface name.",
                              "Writing the three literals out would satisfy the assertion — and defeat the exercise.",
                              "Write keyof Entry."]),
                _diagnose("tscourse-w14-wh-d1", "The duplicate that drifted",
                          "TS2353: Object literal may only specify known properties, and 'tag' does not exist in type 'EntryUpdate'.",
                          'interface Entry {\n  id: string;\n  desc: string;\n  tag: string;\n}\n'
                          'interface EntryUpdate {\n  desc: string;\n}\n'
                          'function update(e: Entry, u: EntryUpdate): Entry {\n'
                          '  return { ...e, ...u };\n}\n'
                          'const e: Entry = { id: "e1", desc: "coffee", tag: "food" };\n'
                          'const next = update(e, { desc: "espresso", tag: "fun" });\n'
                          'console.log(`${next.desc} ${next.tag}`);\n',
                          'interface Entry {\n  id: string;\n  desc: string;\n  tag: string;\n}\n'
                          'type EntryUpdate = Omit<Entry, "id">;\n'
                          'function update(e: Entry, u: EntryUpdate): Entry {\n'
                          '  return { ...e, ...u };\n}\n'
                          'const e: Entry = { id: "e1", desc: "coffee", tag: "food" };\n'
                          'const next = update(e, { desc: "espresso", tag: "fun" });\n'
                          'console.log(`${next.desc} ${next.tag}`);\n',
                          [("", "espresso fun")],
                          hints=["`tag` was added to `Entry` and never added to the hand-written `EntryUpdate`.",
                                 "Do not add the member by hand — that is how the drift happened in the first place.",
                                 'An update is an entry without its id: type EntryUpdate = Omit<Entry, "id">;'],
                          difficulty="Medium"),
            ],
            quiz=[
                _q("A derived type at runtime…",
                   ["adds a check", "does nothing — it is erased like every type",
                    "copies members", "is a function"], 1,
                   "All of this week is compile-time only."),
                _q("Coupling two coincidentally-similar types with a utility is…",
                   ["good practice", "a false coupling that hurts when they diverge",
                    "required", "faster"], 1,
                   "Lesson 8 returns to this."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w14-partial", "`Partial<T>` and `Required<T>`",
            "Every member optional, and back again.",
            """
`Partial<T>` makes every member of `T` optional:

```ts
interface Entry {
  desc: string;
  cents: number;
}

type Draft = Partial<Entry>;
// { desc?: string; cents?: number }
```

## The use case: a patch

This is what `Partial` is for. A caller wants to change *some* of the fields and
should not have to restate the rest:

```ts
function applyPatch(e: Entry, patch: Partial<Entry>): Entry {
  return { ...e, ...patch };
}

const e: Entry = { desc: "coffee", cents: 325 };
const next = applyPatch(e, { cents: 400 });
// { desc: "coffee", cents: 400 }
```

`{ ...e, ...patch }` is week 13's copy-don't-mutate with a second spread: every
member of `e`, then every member the patch actually has. A member the patch
omits is simply not in the spread, so the original survives.

## The cost: every read is `| undefined`

```ts
const p: Partial<Entry> = { desc: "coffee" };
console.log(p.cents.toFixed(2));
// ❌ TS18048: 'p.cents' is possibly 'undefined'.
```

Correct, and worth taking seriously. `Partial` is the right type for a value that
is **passed in and spread**; it is the wrong type for a value you intend to read
member by member. If you find yourself writing `?? 0` after every access, the
type is telling you that you wanted a full `Entry` and a default, not a
`Partial`.

Note what `Partial` does *not* do: it does not accept unknown keys. `{ nope: 1 }`
is still an excess property (week 12) — and because every member is optional,
`Partial<Entry>` is a **weak type**, so an object with nothing in common with it
is rejected outright.

## `Required<T>` is the inverse

```ts
interface Options {
  retries?: number;
  mode?: string;
}

type Settled = Required<Options>;
// { retries: number; mode: string }
```

The `?` is removed and `| undefined` goes with it. The standard use is the
"resolved options" pattern: take a `Partial` from the caller, fill in every
default, and hand back a `Required` that the rest of the program can read without
a guard:

```ts
function resolve(o: Options): Required<Options> {
  return { retries: o.retries ?? 3, mode: o.mode ?? "fast" };
}
```

Now `resolve(o).retries` is a plain `number`. All the `??` lives in one place,
which is exactly where you want it.

> ⚠️ **Common mistakes:** using `Partial` for a value you then read repeatedly;
> expecting `Partial` to allow extra keys; and `Required<T>` on a type whose
> members are optional *for a reason* — making them required does not conjure
> values, it just moves the error to whoever builds one.
""",
            warmup=[
                _q("`Partial<Entry>` makes every member…",
                   ["readonly", "optional", "required", "a union"], 1,
                   "Which is what a patch needs."),
                _q("`{ ...e, ...patch }` where patch omits `desc`…",
                   ["sets desc to undefined", "keeps e's desc", "throws", "drops desc"], 1,
                   "An absent member is not in the spread at all."),
                _q("Reading `p.cents` off a Partial gives…",
                   ["number", "TS18048 — possibly undefined", "never", "0"], 1,
                   "Optional means it might not be there."),
                _q("`Required<Options>` where retries is optional makes it…",
                   ["number | undefined", "a required number", "never", "readonly"], 1,
                   "The `?` and the `| undefined` both go."),
            ],
            exercises=[
                _ex("tscourse-w14-pa-1", "A patch parameter",
                    "Type the patch so a caller may supply any subset of the entry's members.",
                    'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'function applyPatch(e: Entry, patch: Partial<Entry>): Entry {\n'
                    '  return { ...e, ...patch };\n}\n'
                    'const e: Entry = { desc: "coffee", cents: 325 };\n'
                    'const next = applyPatch(e, { cents: 400 });\n'
                    'console.log(`${e.cents} ${next.cents} ${next.desc}`);\n',
                    'patch: Partial<Entry>', [("", "325 400 coffee")],
                    hints=["Every member optional, derived from Entry.",
                           "Write patch: Partial<Entry>"]),
                _ex("tscourse-w14-pa-2", "Apply it",
                    "Merge the patch over the entry, without mutating either.",
                    'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'function applyPatch(e: Entry, patch: Partial<Entry>): Entry {\n'
                    '  return { ...e, ...patch };\n}\n'
                    'const e: Entry = { desc: "coffee", cents: 325 };\n'
                    'console.log(applyPatch(e, { desc: "espresso" }).desc);\n'
                    'console.log(applyPatch(e, {}).desc);\n',
                    'return { ...e, ...patch };', [("", "espresso\ncoffee")],
                    hints=["The original first, the patch second, so the patch wins where it has a member.",
                           "An empty patch changes nothing — that is the second line."]),
                _ex("tscourse-w14-pa-3", "Resolve the options",
                    "Fill in every default, so the result can be read without a guard.",
                    'interface Options {\n  retries?: number;\n  mode?: string;\n}\n'
                    'function resolve(o: Options): Required<Options> {\n'
                    '  return { retries: o.retries ?? 3, mode: o.mode ?? "fast" };\n}\n'
                    'const r = resolve({ retries: 5 });\n'
                    'console.log(`${r.mode} x${r.retries}`);\n'
                    'console.log(`${resolve({}).mode} x${resolve({}).retries}`);\n',
                    'return { retries: o.retries ?? 3, mode: o.mode ?? "fast" };',
                    [("", "fast x5\nfast x3")],
                    hints=["Every member of the result is required, so every one needs a value.",
                           "`?? 3` and `?? \"fast\"` supply the defaults."],
                    difficulty="Medium"),
                _ex("tscourse-w14-pa-4", "The return type that needs no guard",
                    "Declare the return type so `r.retries` is a plain number.",
                    'interface Options {\n  retries?: number;\n  mode?: string;\n}\n'
                    'function resolve(o: Options): Required<Options> {\n'
                    '  return { retries: o.retries ?? 3, mode: o.mode ?? "fast" };\n}\n'
                    'const r = resolve({});\n'
                    'console.log(r.retries.toFixed(1));\n',
                    'Required<Options>', [("", "3.0")],
                    hints=["Without it, `.toFixed` on a possibly-undefined number would be TS18048.",
                           "Write Required<Options>"],
                    difficulty="Medium"),
                _predict("tscourse-w14-pa-p1", "Reading off a Partial",
                         'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                         'const p: Partial<Entry> = { desc: "coffee" };\n'
                         'const got = p.cents;\n',
                         "got", "number | undefined",
                         why="The value plainly has no `cents`. The question is what the TYPE says.",
                         hints=["Partial made every member optional.",
                                "An optional member reads as its type or undefined.",
                                "Write number | undefined."]),
                _diagnose("tscourse-w14-pa-d1", "The member that might not be there",
                          "TS18048: 'p.cents' is possibly 'undefined'.",
                          'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                          'function show(p: Partial<Entry>): string {\n'
                          '  return `${p.desc ?? "?"} $${(p.cents / 100).toFixed(2)}`;\n}\n'
                          'console.log(show({ desc: "coffee", cents: 325 }));\n'
                          'console.log(show({ desc: "gift" }));\n',
                          'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                          'function show(p: Partial<Entry>): string {\n'
                          '  return `${p.desc ?? "?"} $${((p.cents ?? 0) / 100).toFixed(2)}`;\n}\n'
                          'console.log(show({ desc: "coffee", cents: 325 }));\n'
                          'console.log(show({ desc: "gift" }));\n',
                          [("", "coffee $3.25\ngift $0.00")],
                          hints=["The second call proves the compiler is right — there really is no cents there.",
                                 "`desc` is already defaulted; do the same for the amount.",
                                 "Default it BEFORE dividing: ((p.cents ?? 0) / 100)."],
                          difficulty="Medium"),
                _diagnose("tscourse-w14-pa-d2", "Required means required",
                          "TS2741: Property 'retries' is missing in type '{ mode: string; }' but required in type 'Required<Options>'.",
                          'interface Options {\n  retries?: number;\n  mode?: string;\n}\n'
                          'function resolve(o: Options): Required<Options> {\n'
                          '  return { mode: o.mode ?? "fast" };\n}\n'
                          'console.log(resolve({}).retries);\n',
                          'interface Options {\n  retries?: number;\n  mode?: string;\n}\n'
                          'function resolve(o: Options): Required<Options> {\n'
                          '  return { retries: o.retries ?? 3, mode: o.mode ?? "fast" };\n}\n'
                          'console.log(resolve({}).retries);\n',
                          [("", "3")],
                          hints=["Required removed the `?`, so every member has to be supplied.",
                                 "Give retries a default of 3."],
                          difficulty="Medium"),
                _fix("tscourse-w14-pa-fix1", "Fix the patch that erased a field",
                     "`applyPatch` spreads the patch first, so the original values win and the patch has no effect — this prints `325` instead of `400`.",
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'function applyPatch(e: Entry, patch: Partial<Entry>): Entry {\n'
                     '  return { ...patch, ...e };\n}\n'
                     'const e: Entry = { desc: "coffee", cents: 325 };\n'
                     'console.log(applyPatch(e, { cents: 400 }).cents);\n',
                     'interface Entry {\n  readonly desc: string;\n  readonly cents: number;\n}\n'
                     'function applyPatch(e: Entry, patch: Partial<Entry>): Entry {\n'
                     '  return { ...e, ...patch };\n}\n'
                     'const e: Entry = { desc: "coffee", cents: 325 };\n'
                     'console.log(applyPatch(e, { cents: 400 }).cents);\n',
                     [("", "400")],
                     hints=["Both spreads are valid, so nothing was reported — the order is the bug.",
                            "The later spread wins, and the patch is supposed to win.",
                            "Spread the entry first, then the patch."]),
            ],
            quiz=[
                _q("`Partial<T>` is the wrong type when…",
                   ["you spread it", "you read member after member and default each one",
                    "it is a parameter", "T is small"], 1,
                   "That is a full T plus defaults, not a Partial."),
                _q("The resolved-options pattern puts the `??` …",
                   ["at every use site", "in one place, returning Required<T>",
                    "in the interface", "nowhere"], 1,
                   "Which is the point of it."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w14-readonly", "`Readonly<T>`",
            "Week 13's modifier, as a type — with the same shallow gap.",
            """
A short lesson, because you already know what it does.

```ts
interface Entry {
  desc: string;
  cents: number;
}

type Frozen = Readonly<Entry>;
// { readonly desc: string; readonly cents: number }
```

`Readonly<T>` puts the `readonly` modifier on every member of `T`. Assigning one
is the same TS2540 as week 13.

## Why bother, when you could write the modifier?

Two reasons, and they are the reasons for every utility type:

**You do not own the type.** `Readonly<SomeLibraryType>` works without editing
the library.

**You want both versions.** One declaration, two views:

```ts
interface MutableEntry { desc: string; cents: number; }
type Entry = Readonly<MutableEntry>;
```

That is how you offer a builder that mutates internally and hands back something
the caller cannot change.

## It is shallow, in exactly the same way

```ts
interface State {
  tags: string[];
}

const s: Readonly<State> = { tags: ["food"] };
s.tags = [];              // ❌ TS2540 — the member is readonly
s.tags.push("home");      // ✅ ...and the array is not
console.log(s.tags.length);    // 2
```

Identical to week 13 lesson 5. `Readonly<T>` maps over `T`'s **own** members and
stops. To go deeper you need `DeepReadonly`, and that is still week 29.

## Where you have already met it

`Object.freeze` returns `Readonly<T>`:

```ts
const f = Object.freeze({ x: 1 });
f.x = 5;         // ❌ TS2540
```

Week 13 mentioned that the return type was "a utility type, next week". This is
it — which also means `Object.freeze` gives you the compile-time check and the
runtime guard in one call, provided you use the value it returns.

> ⚠️ **Common mistakes:** expecting depth; expecting `Readonly<T>` to do
> something at runtime (`Object.freeze` is the runtime tool); and applying it to
> a type whose arrays are the mutable part, where `readonly T[]` on the member is
> what you actually needed.
""",
            warmup=[
                _q("`Readonly<Entry>` makes every member…",
                   ["optional", "readonly", "required", "a union"], 1,
                   "Week 13's modifier applied across the type."),
                _q("`Readonly<T>` is…",
                   ["deep", "shallow — own members only", "a runtime freeze", "a class"], 1,
                   "Same gap as the modifier."),
                _q("`Object.freeze` returns…",
                   ["void", "Readonly<T>", "T", "never"], 1,
                   "Which is why using the return value gets you a compile error."),
                _q("The reason to prefer the utility over writing `readonly` by hand is…",
                   ["it is shorter", "you may not own the type, and you may want both views",
                    "it is deeper", "performance"], 1,
                   "The general argument for every utility type."),
            ],
            exercises=[
                _ex("tscourse-w14-ro-1", "A parameter nothing can change",
                    "Type the parameter so the function cannot assign to any member.",
                    'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                    'function money(e: Readonly<Entry>): string {\n'
                    '  return `${e.desc} $${(e.cents / 100).toFixed(2)}`;\n}\n'
                    'console.log(money({ desc: "coffee", cents: 325 }));\n',
                    'e: Readonly<Entry>', [("", "coffee $3.25")],
                    hints=["Every member readonly, derived from Entry.",
                           "Write e: Readonly<Entry>"]),
                _ex("tscourse-w14-ro-2", "Two views of one declaration",
                    "Derive the public, immutable view from the mutable one.",
                    'interface MutableEntry {\n  desc: string;\n  cents: number;\n}\n'
                    'type Entry = Readonly<MutableEntry>;\n'
                    'function build(desc: string, cents: number): Entry {\n'
                    '  const draft: MutableEntry = { desc: "", cents: 0 };\n'
                    '  draft.desc = desc;\n'
                    '  draft.cents = cents;\n'
                    '  return draft;\n}\n'
                    'console.log(`${build("coffee", 325).cents}`);\n',
                    'type Entry = Readonly<MutableEntry>;',
                    [("", "325")],
                    hints=["The builder mutates its own draft; the caller gets something settled.",
                           "Write type Entry = Readonly<MutableEntry>;"],
                    difficulty="Medium"),
                _ex("tscourse-w14-ro-3", "Shallow, again",
                    "The member is readonly. Modify the array it points at anyway.",
                    'interface State {\n  tags: string[];\n}\n'
                    'const s: Readonly<State> = { tags: ["food"] };\n'
                    's.tags.push("home");\n'
                    'console.log(s.tags.join(","));\n',
                    's.tags.push("home");', [("", "food,home")],
                    hints=["Readonly<T> mapped over the members and stopped there.",
                           'Write s.tags.push("home");'],
                    difficulty="Medium"),
                _diagnose("tscourse-w14-ro-d1", "The settled member",
                          "TS2540: Cannot assign to 'cents' because it is a read-only property.",
                          'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                          'function withTax(e: Readonly<Entry>): Readonly<Entry> {\n'
                          '  e.cents = Math.round(e.cents * 1.1);\n'
                          '  return e;\n}\n'
                          'console.log(withTax({ desc: "coffee", cents: 325 }).cents);\n',
                          'interface Entry {\n  desc: string;\n  cents: number;\n}\n'
                          'function withTax(e: Readonly<Entry>): Readonly<Entry> {\n'
                          '  return { ...e, cents: Math.round(e.cents * 1.1) };\n}\n'
                          'console.log(withTax({ desc: "coffee", cents: 325 }).cents);\n',
                          [("", "358")],
                          hints=["Do not weaken the parameter type — the promise is the point.",
                                 "Week 13's answer: build a new value instead of assigning.",
                                 "{ ...e, cents: ... }"],
                          difficulty="Medium"),
                _fix("tscourse-w14-ro-fix1", "Fix the type that only looked settled",
                     "`Readonly<State>` protects the members, but `tags` is a mutable array — so `addTag` pushes into the caller's own array and this prints `2 2` instead of `1 2`. Make the array readonly too, and build a new value.",
                     'interface State {\n  tags: string[];\n}\n'
                     'function addTag(s: Readonly<State>, tag: string): Readonly<State> {\n'
                     '  s.tags.push(tag);\n'
                     '  return s;\n}\n'
                     'const s: Readonly<State> = { tags: ["food"] };\n'
                     'const next = addTag(s, "home");\n'
                     'console.log(`${s.tags.length} ${next.tags.length}`);\n',
                     'interface State {\n  tags: readonly string[];\n}\n'
                     'function addTag(s: Readonly<State>, tag: string): Readonly<State> {\n'
                     '  return { ...s, tags: [...s.tags, tag] };\n}\n'
                     'const s: Readonly<State> = { tags: ["food"] };\n'
                     'const next = addTag(s, "home");\n'
                     'console.log(`${s.tags.length} ${next.tags.length}`);\n',
                     [("", "1 2")],
                     hints=["Readonly<T> is shallow, so the array was never protected.",
                            "Declare the member as `readonly string[]` in State — the depth has to come from the member's own type.",
                            "Then return a new state with a new tags array."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("To make a type's ARRAY member immutable you…",
                   ["use Readonly<T>", "declare the member as readonly T[]",
                    "call Object.freeze", "use Partial"], 1,
                   "The depth has to come from the member's own type."),
                _q("`Readonly<T>` at runtime…",
                   ["freezes", "does nothing", "copies", "throws"], 1,
                   "Object.freeze is the runtime tool."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w14-pickomit", "`Pick<T, K>` and `Omit<T, K>`",
            "Choosing members — and the asymmetry that catches everyone.",
            """
Two ways to say the same thing, from opposite ends.

```ts
interface Entry {
  id: string;
  desc: string;
  cents: number;
  tag: string;
}

type Row    = Pick<Entry, "desc" | "cents">;   // { desc: string; cents: number }
type Create = Omit<Entry, "id">;               // desc, cents, tag
```

**Use `Pick` when the list you want is short.** **Use `Omit` when the list you
want to drop is short.** `Pick<Entry, "desc" | "cents">` and
`Omit<Entry, "id" | "tag">` are the same type; the first says what it means.

## The asymmetry

`Pick`'s key parameter is **constrained** to `keyof T`:

```ts
type Bad = Pick<Entry, "nope">;
// ❌ TS2344: Type '"nope"' does not satisfy the constraint 'keyof Entry'.
```

`Omit`'s is **not**:

```ts
type Oops = Omit<Entry, "nope">;
// ✅ compiles. Omits nothing. Exactly equal to Entry.
```

That is not an oversight — `Omit` is defined that way on purpose, so you can omit
a key from a union of types where it exists in only some of them. But the
practical consequence is that **a typo in an `Omit` is silent**, and it is a real
source of bugs: you meant to drop `password` and you dropped nothing.

If it matters, constrain it yourself:

```ts
type StrictOmit<T, K extends keyof T> = Omit<T, K>;
type Caught = StrictOmit<Entry, "nope">;    // ❌ now TS2344
```

Three lines, and worth having in a shared types file.

## `Omit` does not remove anything at runtime

This is the one that bites hardest, and it is week 12 lesson 2 again:

```ts
interface Entry { desc: string; cents: number; secret: string; }
type Public = Omit<Entry, "secret">;

function publish(e: Entry): Public {
  return { ...e };          // ✅ compiles
}

console.log(Object.keys(publish(entry)).join(","));
// desc,cents,secret        ← the secret is still there
```

`Omit` changed the **type**. The spread copied every property the value had.
Nothing was stripped, because types do not exist at runtime — and if that value
goes on to `JSON.stringify` (week 15) the secret goes out with it.

To actually remove a property you have to build the value:

```ts
function publish(e: Entry): Public {
  return { desc: e.desc, cents: e.cents };
}
```

Verbose, and correct. This is why "type it as `Omit<...>`" is not a security
measure.

## Composing them

```ts
type EntryPatch = Partial<Omit<Entry, "id">>;
```

"Any subset of an entry's fields except its id." Two utilities deep is readable;
four is not, and lesson 8 is about where to stop.

> ⚠️ **Common mistakes:** trusting an `Omit` key (check the spelling, or write
> `StrictOmit`); believing `Omit` strips a property from the value; and reaching
> for `Omit` when `Pick` would have named the intent better.
""",
            warmup=[
                _q("`Pick<Entry, \"nope\">` gives…",
                   ["no error", "TS2344 — the key is constrained to keyof Entry", "never",
                    "an empty type"], 1,
                   "Pick checks its keys."),
                _q("`Omit<Entry, \"nope\">` gives…",
                   ["TS2344", "no error, and omits nothing", "never", "an empty type"], 1,
                   "Deliberate, and a real source of silent bugs."),
                _q("`return { ...e }` from a function typed `Omit<Entry, \"secret\">`…",
                   ["strips secret", "compiles and keeps secret at runtime", "is TS2353",
                    "throws"], 1,
                   "Types do not exist at runtime."),
                _q("Prefer `Pick` when…",
                   ["always", "the list of members you WANT is the short one", "never",
                    "the type is large"], 1,
                   "And Omit when the list you are dropping is short."),
            ],
            exercises=[
                _ex("tscourse-w14-po-1", "Keep two members",
                    "Derive the row type by naming the two members you want.",
                    'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n  tag: string;\n}\n'
                    'type Row = Pick<Entry, "desc" | "cents">;\n'
                    'function render(r: Row): string {\n'
                    '  return `${r.desc} $${(r.cents / 100).toFixed(2)}`;\n}\n'
                    'console.log(render({ desc: "coffee", cents: 325 }));\n',
                    'type Row = Pick<Entry, "desc" | "cents">;',
                    [("", "coffee $3.25")],
                    hints=["A union of the two key names as the second argument.",
                           'Write type Row = Pick<Entry, "desc" | "cents">;']),
                _ex("tscourse-w14-po-2", "Drop one member",
                    "Derive the create type as everything except the id.",
                    'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n}\n'
                    'type Create = Omit<Entry, "id">;\n'
                    'function build(id: string, c: Create): Entry {\n'
                    '  return { id, ...c };\n}\n'
                    'const e = build("e1", { desc: "coffee", cents: 325 });\n'
                    'console.log(`${e.id} ${e.desc} ${e.cents}`);\n',
                    'type Create = Omit<Entry, "id">;',
                    [("", "e1 coffee 325")],
                    hints=["One key name to drop, as a string literal.",
                           'Write type Create = Omit<Entry, "id">;']),
                _ex("tscourse-w14-po-3", "Remove it for real",
                    "Build the public value explicitly, so the secret is genuinely absent at runtime.",
                    'interface Entry {\n  desc: string;\n  cents: number;\n  secret: string;\n}\n'
                    'type Public = Omit<Entry, "secret">;\n'
                    'function publish(e: Entry): Public {\n'
                    '  return { desc: e.desc, cents: e.cents };\n}\n'
                    'const e: Entry = { desc: "coffee", cents: 325, secret: "s3cr3t" };\n'
                    'console.log(Object.keys(publish(e)).join(","));\n',
                    'return { desc: e.desc, cents: e.cents };',
                    [("", "desc,cents")],
                    hints=["A spread would copy every property, secret included.",
                           "Name the two members you want, explicitly."],
                    difficulty="Medium"),
                _ex("tscourse-w14-po-4", "A strict Omit",
                    "Declare an Omit that DOES check its key, by constraining the parameter yourself.",
                    'interface Entry {\n  id: string;\n  desc: string;\n}\n'
                    'type StrictOmit<T, K extends keyof T> = Omit<T, K>;\n'
                    'type Create = StrictOmit<Entry, "id">;\n'
                    'const c: Create = { desc: "coffee" };\n'
                    'console.log(c.desc);\n',
                    'type StrictOmit<T, K extends keyof T> = Omit<T, K>;',
                    [("", "coffee")],
                    hints=["Week 10's constraint syntax, wrapped around the built-in.",
                           "Write type StrictOmit<T, K extends keyof T> = Omit<T, K>;"],
                    difficulty="Medium"),
                _design("tscourse-w14-po-des1", "Recover the derived type",
                        "The summary type has been removed. Work out what it must be from how "
                        "`render` uses it and what the entry has, and write it back as a "
                        "derivation of `Entry` — not as a fresh object type.",
                        'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n  tag: string;\n}\n'
                        'type Summary = Pick<Entry, "desc" | "cents">;\n'
                        'function render(s: Summary): string {\n'
                        '  return `${s.desc} $${(s.cents / 100).toFixed(2)}`;\n}\n'
                        'const e: Entry = { id: "e1", desc: "coffee", cents: 325, tag: "food" };\n'
                        'console.log(render({ desc: e.desc, cents: e.cents }));\n',
                        'type Summary = Pick<Entry, "desc" | "cents">;',
                        """
type _1 = Expect<Equal<Summary, { desc: string; cents: number }>>;
""",
                        [("", "coffee $3.25")],
                        hints=["`render` reads exactly two members off it.",
                               "Both of those members already exist on Entry with the right types.",
                               'Pick the two you need: Pick<Entry, "desc" | "cents">.'],
                        difficulty="Medium"),
                _diagnose("tscourse-w14-po-d1", "The key that is not a key",
                          "TS2344: Type '\"amount\"' does not satisfy the constraint 'keyof Entry'.",
                          'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n}\n'
                          'type Row = Pick<Entry, "desc" | "amount">;\n'
                          'function render(r: Row): string {\n'
                          '  return `${r.desc}`;\n}\n'
                          'console.log(render({ desc: "coffee" }));\n',
                          'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n}\n'
                          'type Row = Pick<Entry, "desc" | "cents">;\n'
                          'function render(r: Row): string {\n'
                          '  return `${r.desc}`;\n}\n'
                          'console.log(render({ desc: "coffee", cents: 325 }));\n',
                          [("", "coffee")],
                          hints=["Pick's second parameter is constrained, so a name that is not a member is rejected.",
                                 "The interface calls the money field something else.",
                                 "Use \"cents\", and give the call the member it now needs."],
                          difficulty="Medium"),
                _fix("tscourse-w14-po-fix1", "Fix the leak that type-checked",
                     "`publish` is typed `Omit<Entry, \"secret\">` and spreads the whole entry, so the secret is still there at runtime — this prints `desc,cents,secret` instead of `desc,cents`. `Omit` is a type, not a filter.",
                     'interface Entry {\n  desc: string;\n  cents: number;\n  secret: string;\n}\n'
                     'type Public = Omit<Entry, "secret">;\n'
                     'function publish(e: Entry): Public {\n'
                     '  return { ...e };\n}\n'
                     'const e: Entry = { desc: "coffee", cents: 325, secret: "s3cr3t" };\n'
                     'console.log(Object.keys(publish(e)).join(","));\n',
                     'interface Entry {\n  desc: string;\n  cents: number;\n  secret: string;\n}\n'
                     'type Public = Omit<Entry, "secret">;\n'
                     'function publish(e: Entry): Public {\n'
                     '  return { desc: e.desc, cents: e.cents };\n}\n'
                     'const e: Entry = { desc: "coffee", cents: 325, secret: "s3cr3t" };\n'
                     'console.log(Object.keys(publish(e)).join(","));\n',
                     [("", "desc,cents")],
                     hints=["The annotation narrowed the TYPE. The spread copied every property the value had.",
                            "Nothing at runtime knows what Omit said, because types are erased.",
                            "Build the result member by member instead of spreading."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`Omit`'s key is unconstrained so that…",
                   ["it is faster", "you can omit a key present in only some members of a union",
                    "typos are allowed", "of Pick"], 1,
                   "A deliberate design decision with a real cost."),
                _q("Typing a return value `Omit<T, \"password\">` as a security measure is…",
                   ["sufficient", "not a security measure at all — nothing is removed",
                    "better than deleting", "required"], 1,
                   "Build the value you mean to hand out."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w14-record", "`Record<K, V>`",
            "An object type from a set of keys — and when the lookup is safe.",
            """
`Record<K, V>` builds an object type with keys `K` and values `V`. Week 10 used
it in passing and week 12 checked one with `satisfies`; here is the whole thing.

```ts
type Cat = "food" | "fun" | "home";

const budgets: Record<Cat, number> = {
  food: 5000,
  fun: 2000,
  home: 80000,
};
```

## The important distinction: union keys vs `string`

This is the part worth getting right, because it decides whether every lookup
needs a `??`.

**Union keys become known, required members:**

```ts
const budgets: Record<Cat, number> = { food: 1, fun: 2, home: 3 };
budgets.food;        // number — no `| undefined`
```

Miss one and it is an error:

```ts
const partial: Record<Cat, number> = { food: 1 };
// ❌ TS2741: Property 'fun' is missing in type '{ food: number; }'
//            but required in type 'Record<Cat, number>'.
```

That is `Record`'s best feature: **exhaustiveness**. Add a fourth category to
`Cat` and every `Record<Cat, …>` in the codebase stops compiling until it is
filled in.

**A `string` key becomes an index signature:**

```ts
const loose: Record<string, number> = { food: 1 };
loose.food;          // number | undefined
```

Any string is allowed, so nothing is guaranteed to be there — and under
`noUncheckedIndexedAccess` the read reflects that. Week 12's `satisfies` lesson
was exactly this problem: annotate a literal with `Record<string, number>` and
you throw away the keys you knew about.

So:

| you want | use |
|---|---|
| a fixed, known set of keys | `Record<Union, V>` |
| an arbitrary lookup table | `Record<string, V>`, and handle `undefined` |
| a literal whose keys you want to keep | `satisfies Record<string, V>` (week 12) |

## Versus an index signature

```ts
interface Loose { [key: string]: number; }        // ≡ Record<string, number>
```

The same type. `Record` composes better (it takes any key union, and nests) and
reads better in a type position; an index signature is what you write inside an
interface that also has known members.

## Building one immutably

Week 13's rules still apply, and a `Record` with union keys is easy to build in
one expression:

```ts
function totalFor(es: readonly Entry[], tag: Cat): number {
  return es.filter((e) => e.tag === tag).reduce((s, e) => s + e.cents, 0);
}

const totals: Record<Cat, number> = {
  food: totalFor(entries, "food"),
  fun: totalFor(entries, "fun"),
  home: totalFor(entries, "home"),
};
```

Slightly repetitive, entirely readable, no mutation, and exhaustively checked.
That is the capstone's shape.

> ⚠️ **Common mistakes:** using `Record<string, V>` when you meant a fixed set,
> then fighting `| undefined` forever; annotating a literal with
> `Record<string, V>` instead of using `satisfies`; and forgetting that adding a
> union member is a **deliberately** breaking change.
""",
            warmup=[
                _q("`Record<\"a\" | \"b\", number>` has…",
                   ["an index signature", "two known, required members", "optional members",
                    "no members"], 1,
                   "Which is what makes it exhaustive."),
                _q("`Record<string, number>` lookup gives…",
                   ["number", "number | undefined", "never", "any"], 1,
                   "Any string is allowed, so nothing is guaranteed."),
                _q("Missing a key from `Record<Cat, number>` is…",
                   ["allowed", "TS2741", "TS2344", "a warning"], 1,
                   "The exhaustiveness check."),
                _q("`interface Loose { [key: string]: number }` is…",
                   ["different from Record<string, number>", "the same type",
                    "narrower", "wider"], 1,
                   "Two spellings."),
            ],
            exercises=[
                _ex("tscourse-w14-re-1", "A table with known keys",
                    "Type the budgets so every category is required and every lookup is a plain number.",
                    'type Cat = "food" | "fun" | "home";\n'
                    'const budgets: Record<Cat, number> = {\n'
                    '  food: 5000,\n  fun: 2000,\n  home: 80000,\n};\n'
                    'function money(c: number): string {\n'
                    '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                    'console.log(`${money(budgets.food)} ${money(budgets.home)}`);\n',
                    'Record<Cat, number>', [("", "$50.00 $800.00")],
                    hints=["The key type is the union, the value type is number.",
                           "Write Record<Cat, number>"]),
                _ex("tscourse-w14-re-2", "Exhaustive by construction",
                    "Fill in the third category, which the type requires.",
                    'type Cat = "food" | "fun" | "home";\n'
                    'const budgets: Record<Cat, number> = {\n'
                    '  food: 5000,\n  fun: 2000,\n  home: 80000,\n};\n'
                    'const CATS: readonly Cat[] = ["food", "fun", "home"];\n'
                    'console.log(CATS.map((c) => `${c}=${budgets[c]}`).join(", "));\n',
                    '  home: 80000,\n',
                    [("", "food=5000, fun=2000, home=80000")],
                    hints=["The type demands every member of the union.",
                           "Add home with a budget of 80000."]),
                _ex("tscourse-w14-re-3", "An arbitrary lookup",
                    "Handle the missing key, since a string-keyed Record guarantees nothing.",
                    'const seen: Record<string, number> = { food: 2 };\n'
                    'function countOf(tag: string): number {\n'
                    '  return seen[tag] ?? 0;\n}\n'
                    'console.log(`${countOf("food")} ${countOf("fun")}`);\n',
                    'return seen[tag] ?? 0;', [("", "2 0")],
                    hints=["The lookup is `number | undefined`, so default it.",
                           "Write return seen[tag] ?? 0;"]),
                _ex("tscourse-w14-re-4", "Build one immutably",
                    "Compute each category's total with the helper, without mutating anything.",
                    'type Cat = "food" | "fun";\n'
                    'interface Entry {\n  readonly tag: Cat;\n  readonly cents: number;\n}\n'
                    'const entries: readonly Entry[] = [\n'
                    '  { tag: "food", cents: 325 },\n'
                    '  { tag: "fun", cents: 1200 },\n'
                    '  { tag: "food", cents: 950 },\n];\n'
                    'function totalFor(es: readonly Entry[], tag: Cat): number {\n'
                    '  return es.filter((e) => e.tag === tag).reduce((s, e) => s + e.cents, 0);\n}\n'
                    'const totals: Record<Cat, number> = {\n'
                    '  food: totalFor(entries, "food"),\n'
                    '  fun: totalFor(entries, "fun"),\n};\n'
                    'console.log(`${totals.food} ${totals.fun}`);\n',
                    'const totals: Record<Cat, number> = {\n'
                    '  food: totalFor(entries, "food"),\n'
                    '  fun: totalFor(entries, "fun"),\n};',
                    [("", "1275 1200")],
                    hints=["One member per category, each calling the helper.",
                           "No accumulator variable and no push — just an object literal.",
                           "The type will tell you if you forget a category."],
                    difficulty="Medium"),
                _predict("tscourse-w14-re-p1", "A known-key lookup",
                         'type Cat = "food" | "fun";\n'
                         'const budgets: Record<Cat, number> = { food: 1, fun: 2 };\n'
                         'const got = budgets.food;\n',
                         "got", "number",
                         why="Compare your answer with the next exercise, which changes only "
                             "the key type.",
                         hints=["A union key produces known, required members.",
                                "noUncheckedIndexedAccess applies to index signatures, and this is not one.",
                                "Write number."]),
                _predict("tscourse-w14-re-p2", "A string-key lookup",
                         'const budgets: Record<string, number> = { food: 1, fun: 2 };\n'
                         'const got = budgets.food;\n',
                         "got", "number | undefined",
                         why="Same value, same member, and only the key type is different.",
                         hints=["A string key makes this an index signature.",
                                "Any string is allowed, so nothing is guaranteed to be present.",
                                "Write number | undefined."]),
                _diagnose("tscourse-w14-re-d1", "The category nobody budgeted",
                          "TS2741: Property 'home' is missing in type '{ food: number; fun: number; }' but required in type 'Record<Cat, number>'.",
                          'type Cat = "food" | "fun" | "home";\n'
                          'const budgets: Record<Cat, number> = {\n'
                          '  food: 5000,\n  fun: 2000,\n};\n'
                          'const CATS: readonly Cat[] = ["food", "fun", "home"];\n'
                          'console.log(CATS.map((c) => budgets[c]).join(","));\n',
                          'type Cat = "food" | "fun" | "home";\n'
                          'const budgets: Record<Cat, number> = {\n'
                          '  food: 5000,\n  fun: 2000,\n  home: 80000,\n};\n'
                          'const CATS: readonly Cat[] = ["food", "fun", "home"];\n'
                          'console.log(CATS.map((c) => budgets[c]).join(","));\n',
                          [("", "5000,2000,80000")],
                          hints=["This is Record's best feature working as intended.",
                                 "Add the missing category with a budget of 80000."],
                          difficulty="Easy"),
                _fix("tscourse-w14-re-fix1", "Fix the table that lost its keys",
                     "The totals are annotated `Record<string, number>`, so every lookup is possibly undefined and the `?? 0` fallbacks hide a mistyped category — this prints `0` instead of `1275`. Use the union as the key type instead.",
                     'type Cat = "food" | "fun";\n'
                     'const totals: Record<string, number> = { food: 1275, fun: 1200 };\n'
                     'function spent(c: Cat): number {\n'
                     '  return totals[c + "s"] ?? 0;\n}\n'
                     'console.log(spent("food"));\n',
                     'type Cat = "food" | "fun";\n'
                     'const totals: Record<Cat, number> = { food: 1275, fun: 1200 };\n'
                     'function spent(c: Cat): number {\n'
                     '  return totals[c];\n}\n'
                     'console.log(spent("food"));\n',
                     [("", "1275")],
                     hints=["A string-keyed Record accepts any string, so the mangled key raised no complaint.",
                            "Key the table on the union instead, and the members become known and required.",
                            "Then index it with the category itself — no `?? 0` needed, and `c + \"s\"` no longer compiles."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Adding a member to the key union is…",
                   ["silent", "a deliberately breaking change, which is the point",
                    "an error in Record", "ignored"], 1,
                   "Every table stops compiling until it is filled in."),
                _q("If you are writing `?? 0` after every Record lookup, you probably…",
                   ["need a class", "should have keyed it on a union rather than string",
                    "need Partial", "should use as"], 1,
                   "The type is telling you the keys were known all along."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w14-filter", "`Exclude<U, X>` and `Extract<U, X>`",
            "These two work on unions, not on objects.",
            """
Everything so far reshaped an **object** type. These two reshape a **union**.

```ts
type Cat = "food" | "fun" | "home";

type Away  = Exclude<Cat, "home">;          // "food" | "fun"
type Only  = Extract<Cat, "home" | "x">;    // "home"
```

`Exclude<U, X>` drops every member of `U` that is assignable to `X`.
`Extract<U, X>` keeps only those. They are exact opposites, and neither cares
whether the members are strings, objects, or anything else.

Note `Extract<Cat, "home" | "x">` is `"home"` and not an error — `"x"` simply
matches nothing. Both of these filter silently rather than complaining, so a
typo gives you a union that is quietly wrong. `Exclude<Cat, "hom">` is just
`Cat`.

## `Extract` on a discriminated union

This is where they earn their place. Week 9 built discriminated unions; naming
one arm of one used to mean writing it out again:

```ts
type Action =
  | { kind: "add"; amount: number }
  | { kind: "remove"; id: string };

type Add = Extract<Action, { kind: "add" }>;
// { kind: "add"; amount: number }

function amountOf(a: Add): number {
  return a.amount;          // no narrowing needed — the type is already the one arm
}
```

`{ kind: "add" }` is used as a **pattern**: the arm whose `kind` matches is the
one that is assignable to it. Add a third arm and nothing here changes; rename
`add` and this stops compiling, which is right.

The alternative — declaring each arm as its own named interface and then a union
of them — is also perfectly good, and arguably clearer:

```ts
interface AddAction    { kind: "add"; amount: number; }
interface RemoveAction { kind: "remove"; id: string; }
type Action = AddAction | RemoveAction;
```

Use `Extract` when the union is the thing you were given (from a library, or
already written); declare the arms separately when you own the union and expect
to reference the arms often.

## `Exclude` for "everything but"

```ts
type Cat = "food" | "fun" | "home";
type Discretionary = Exclude<Cat, "home">;

function isDiscretionary(c: Cat): c is Discretionary {
  return c !== "home";
}
```

That is a type guard (week 9) whose type is derived rather than restated — so it
cannot fall out of step with `Cat`.

`Exclude` also has one very common specific use, removing `null` and `undefined`
from a union. TypeScript ships that as its own utility, `NonNullable<T>`, and it
belongs to **week 15**, where null-safety gets a week of its own.

> ⚠️ **Common mistakes:** reaching for `Exclude`/`Extract` on an object type
> (they do nothing useful there — you want `Omit`/`Pick`); assuming a typo will
> be reported (it will not); and using `Extract` where naming the arms would
> have been clearer.
""",
            warmup=[
                _q("`Exclude` and `Extract` operate on…",
                   ["object members", "unions", "arrays", "functions"], 1,
                   "Omit and Pick are the object-shaped pair."),
                _q("`Exclude<\"a\"|\"b\"|\"c\", \"c\">` is…",
                   ['"c"', '"a" | "b"', "never", "string"], 1,
                   "It drops what matches."),
                _q("`Exclude<Cat, \"hom\">` where the member is \"home\" gives…",
                   ["an error", "Cat unchanged — the typo matches nothing", "never",
                    "a warning"], 1,
                   "Silent, like Omit."),
                _q("`Extract<Action, { kind: \"add\" }>` gives…",
                   ["the kind member", "the union arm whose kind is \"add\"", "never",
                    "all arms"], 1,
                   "The object is used as a pattern."),
            ],
            exercises=[
                _ex("tscourse-w14-fi-1", "Everything but one",
                    "Derive the discretionary categories as the union without \"home\".",
                    'type Cat = "food" | "fun" | "home";\n'
                    'type Discretionary = Exclude<Cat, "home">;\n'
                    'function label(c: Discretionary): string {\n'
                    '  return `${c} is optional spending`;\n}\n'
                    'console.log(label("fun"));\n',
                    'type Discretionary = Exclude<Cat, "home">;',
                    [("", "fun is optional spending")],
                    hints=["Drop the one member you do not want.",
                           'Write type Discretionary = Exclude<Cat, "home">;']),
                _ex("tscourse-w14-fi-2", "One arm of a discriminated union",
                    "Derive the add action type by matching on its discriminant.",
                    'type Action =\n'
                    '  | { kind: "add"; amount: number }\n'
                    '  | { kind: "remove"; id: string };\n'
                    'type Add = Extract<Action, { kind: "add" }>;\n'
                    'function amountOf(a: Add): number {\n'
                    '  return a.amount;\n}\n'
                    'console.log(amountOf({ kind: "add", amount: 325 }));\n',
                    'type Add = Extract<Action, { kind: "add" }>;',
                    [("", "325")],
                    hints=["Use an object with just the discriminant as the pattern.",
                           'Write type Add = Extract<Action, { kind: "add" }>;'],
                    difficulty="Medium"),
                _ex("tscourse-w14-fi-3", "A guard whose type is derived",
                    "Write the predicate so it narrows to the derived union.",
                    'type Cat = "food" | "fun" | "home";\n'
                    'type Discretionary = Exclude<Cat, "home">;\n'
                    'function isDiscretionary(c: Cat): c is Discretionary {\n'
                    '  return c !== "home";\n}\n'
                    'const cats: readonly Cat[] = ["food", "home", "fun"];\n'
                    'console.log(cats.filter(isDiscretionary).join(","));\n',
                    'return c !== "home";', [("", "food,fun")],
                    hints=["The predicate is true for exactly the members Exclude kept.",
                           'Write return c !== "home";'],
                    difficulty="Medium"),
                _types("tscourse-w14-fi-t1", "Both directions",
                       "Write `Away` as the categories without \"home\", and `Fixed` as only "
                       "\"home\" — one with each utility.",
                       'type Cat = "food" | "fun" | "home";\n'
                       'type Away = Exclude<Cat, "home">;\n'
                       'type Fixed = Extract<Cat, "home">;\n',
                       'type Away = Exclude<Cat, "home">;\n'
                       'type Fixed = Extract<Cat, "home">;',
                       """
type _1 = Expect<Equal<Away, "food" | "fun">>;
type _2 = Expect<Equal<Fixed, "home">>;
""",
                       hints=["One drops what matches; the other keeps only what matches.",
                              "Both take the union first and the pattern second.",
                              'Exclude<Cat, "home"> and Extract<Cat, "home">.'],
                       difficulty="Medium"),
                _diagnose("tscourse-w14-fi-d1", "The member that was excluded",
                          "TS2322: Type '\"home\"' is not assignable to type 'Discretionary'.",
                          'type Cat = "food" | "fun" | "home";\n'
                          'type Discretionary = Exclude<Cat, "home">;\n'
                          'function label(c: Discretionary): string {\n'
                          '  return `${c} is optional`;\n}\n'
                          'const c: Discretionary = "home";\n'
                          'console.log(label(c));\n',
                          'type Cat = "food" | "fun" | "home";\n'
                          'type Discretionary = Exclude<Cat, "home">;\n'
                          'function label(c: Discretionary): string {\n'
                          '  return `${c} is optional`;\n}\n'
                          'const c: Discretionary = "fun";\n'
                          'console.log(label(c));\n',
                          [("", "fun is optional")],
                          hints=["The whole point of the derived type is that this member is not in it.",
                                 "Pick a category that survived the Exclude."],
                          difficulty="Easy"),
                _fix("tscourse-w14-fi-fix1", "Fix the guard that drifted from its type",
                     "`Discretionary` excludes \"home\", but the predicate tests for something else, so the filter keeps the wrong categories — this prints `food,home` instead of `food,fun`.",
                     'type Cat = "food" | "fun" | "home";\n'
                     'type Discretionary = Exclude<Cat, "home">;\n'
                     'function isDiscretionary(c: Cat): c is Discretionary {\n'
                     '  return c !== "fun";\n}\n'
                     'const cats: readonly Cat[] = ["food", "home", "fun"];\n'
                     'console.log(cats.filter(isDiscretionary).join(","));\n',
                     'type Cat = "food" | "fun" | "home";\n'
                     'type Discretionary = Exclude<Cat, "home">;\n'
                     'function isDiscretionary(c: Cat): c is Discretionary {\n'
                     '  return c !== "home";\n}\n'
                     'const cats: readonly Cat[] = ["food", "home", "fun"];\n'
                     'console.log(cats.filter(isDiscretionary).join(","));\n',
                     [("", "food,fun")],
                     hints=["A `c is T` predicate is a promise the compiler takes on trust — it does not check the body.",
                            "The type excludes \"home\", so the test must exclude \"home\" too.",
                            "This is why a derived type is only half the safety: the guard body still has to agree."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("On an object type, `Exclude` …",
                   ["removes members", "does nothing useful — you wanted Omit", "errors",
                    "is the same as Omit"], 1,
                   "Unions and objects need different tools."),
                _q("Removing null and undefined from a union has its own utility, and it is…",
                   ["Exclude", "NonNullable, in week 15", "Extract", "Omit"], 1,
                   "Null-safety gets a whole week."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w14-fntypes", "`ReturnType`, `Parameters` and `typeof`",
            "Deriving from a function you already wrote.",
            """
You have written a function. Somewhere else you need the type of what it returns.
Do not write it out again:

```ts
function parse(line: string): { desc: string; cents: number } {
  const p = line.split(" ");
  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };
}

type Parsed = ReturnType<typeof parse>;
// { desc: string; cents: number }
```

## Why `typeof` is needed

`ReturnType` takes a **type**. `parse` is a **value**. `typeof parse` is the
bridge:

```ts
type Fn = typeof parse;              // (line: string) => { desc: string; cents: number }
type Parsed = ReturnType<Fn>;
```

You will nearly always see them together as `ReturnType<typeof f>`. Forgetting
the `typeof` is the standard mistake, and the error message is unhelpful, so
learn the shape as one unit.

## `Parameters` gives a real tuple

```ts
function fmt(desc: string, cents: number): string {
  return `${desc} $${(cents / 100).toFixed(2)}`;
}

type Args = Parameters<typeof fmt>;      // [desc: string, cents: number]

const args: Args = ["coffee", 325];
console.log(fmt(...args));               // coffee $3.25
```

That is not decorative — a tuple is a value type, so you can store arguments,
pass them around, and spread them back into the call. It is how you write a
wrapper without restating the signature.

## What this is actually for

**A function is often the source of truth.** A parser defines the shape of a
parsed row; a factory defines the shape of what it makes. Deriving from the
function means the shape has exactly one definition:

```ts
type Row = ReturnType<typeof parse>;

function total(rows: readonly Row[]): number {
  return rows.reduce((s, r) => s + r.cents, 0);
}
```

Change what `parse` returns and `total` follows — or fails to compile at the
place that needs attention.

**The alternative is often better, though.** If the shape is meaningful in its
own right, name it and annotate the function with it:

```ts
interface Row { desc: string; cents: number; }
function parse(line: string): Row { … }
```

Now the name is the source of truth, the signature documents itself, and nobody
needs `ReturnType` at all. Reach for `ReturnType<typeof f>` when the shape is
**incidental** — an anonymous object a function happens to return — or when you
do not own the function.

Related utilities you will meet later: `Awaited<T>` unwraps a `Promise`, and
comes with **week 17**. `ConstructorParameters<T>` does for a class what
`Parameters` does for a function.

> ⚠️ **Common mistakes:** forgetting `typeof`; using `ReturnType` on a shape that
> deserved a name; and deriving from an overloaded function, where `ReturnType`
> only sees the last overload.
""",
            warmup=[
                _q("`ReturnType<parse>` without `typeof` is…",
                   ["fine", "wrong — ReturnType needs a TYPE, and parse is a value",
                    "faster", "the same"], 1,
                   "Learn `ReturnType<typeof f>` as one shape."),
                _q("`Parameters<typeof f>` is…",
                   ["an object", "a tuple, so f(...args) works", "a union", "never"], 1,
                   "A real value type."),
                _q("Deriving `Row` from `parse` means…",
                   ["parse gets slower", "the shape has exactly one definition",
                    "Row is any", "nothing"], 1,
                   "Change parse and Row follows."),
                _q("If the shape is meaningful in its own right you should…",
                   ["still use ReturnType", "name it and annotate the function with it",
                    "use Pick", "use any"], 1,
                   "Then nobody needs ReturnType."),
            ],
            exercises=[
                _ex("tscourse-w14-fn-1", "The shape a function returns",
                    "Derive the row type from the parser rather than writing it out.",
                    'function parse(line: string): { desc: string; cents: number } {\n'
                    '  const p = line.split(" ");\n'
                    '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                    'type Row = ReturnType<typeof parse>;\n'
                    'function money(r: Row): string {\n'
                    '  return `${r.desc} $${(r.cents / 100).toFixed(2)}`;\n}\n'
                    'console.log(money(parse("coffee 3.25")));\n',
                    'type Row = ReturnType<typeof parse>;',
                    [("", "coffee $3.25")],
                    hints=["The utility takes a type, so bridge from the value with `typeof`.",
                           "Write type Row = ReturnType<typeof parse>;"],
                    difficulty="Medium"),
                _ex("tscourse-w14-fn-2", "Arguments as a value",
                    "Derive the argument tuple type, then spread it back into the call.",
                    'function fmt(desc: string, cents: number): string {\n'
                    '  return `${desc} $${(cents / 100).toFixed(2)}`;\n}\n'
                    'type Args = Parameters<typeof fmt>;\n'
                    'const args: Args = ["coffee", 325];\n'
                    'console.log(fmt(...args));\n',
                    'type Args = Parameters<typeof fmt>;',
                    [("", "coffee $3.25")],
                    hints=["A tuple of the parameter types, derived from the function.",
                           "Write type Args = Parameters<typeof fmt>;"],
                    difficulty="Medium"),
                _ex("tscourse-w14-fn-3", "Derive, then use it in a list",
                    "Total the parsed rows, with the row type derived from the parser.",
                    _FS +
                    'function parse(line: string): { desc: string; cents: number } {\n'
                    '  const p = line.split(" ");\n'
                    '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                    'type Row = ReturnType<typeof parse>;\n'
                    'function total(rows: readonly Row[]): number {\n'
                    '  return rows.reduce((s, r) => s + r.cents, 0);\n}\n'
                    'const rows = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                    'console.log(`$${(total(rows) / 100).toFixed(2)}`);\n',
                    'function total(rows: readonly Row[]): number {\n'
                    '  return rows.reduce((s, r) => s + r.cents, 0);\n}',
                    [("coffee 3.25\nrent 900", "$903.25"),
                     ("tea 2", "$2.00")],
                    hints=["The parameter is a readonly array of the derived row type.",
                           "Fold the cents with a seed of 0."],
                    difficulty="Medium"),
                _types("tscourse-w14-fn-t1", "Name the argument tuple",
                       "Write `Args` as the tuple of the function's parameter types — derived from "
                       "the function, not written out.",
                       'function fmt(desc: string, cents: number): string {\n'
                       '  return `${desc} $${(cents / 100).toFixed(2)}`;\n}\n'
                       'type Args = Parameters<typeof fmt>;\n',
                       'Parameters<typeof fmt>',
                       """
type _1 = Expect<Equal<Args, [desc: string, cents: number]>>;

// It is a real tuple, so it can be spread back into the call.
const args: Args = ["coffee", 325];
type _2 = Expect<Equal<ReturnType<typeof fmt>, string>>;
""",
                       hints=["The utility takes a type, so bridge from the value with `typeof`.",
                              "Writing [string, number] out by hand would satisfy the assertion and miss the point.",
                              "Write Parameters<typeof fmt>."],
                       difficulty="Medium"),
                _design("tscourse-w14-fn-des1", "Recover the derivation",
                        "The row type has been removed. Write it back as a derivation of the "
                        "parser — the whole point is that the shape is written once.",
                        'function parse(line: string): { desc: string; cents: number } {\n'
                        '  const p = line.split(" ");\n'
                        '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                        'type Row = ReturnType<typeof parse>;\n'
                        'function louder(r: Row): string {\n'
                        '  return `${r.desc.toUpperCase()} ${r.cents}`;\n}\n'
                        'console.log(louder(parse("coffee 3.25")));\n',
                        'type Row = ReturnType<typeof parse>;',
                        """
type _1 = Expect<Equal<Row, { desc: string; cents: number }>>;
""",
                        [("", "COFFEE 325")],
                        hints=["`louder` reads two members, and `parse` returns exactly those.",
                               "Do not write the object type out — derive it.",
                               "ReturnType, with typeof to bridge from the value."],
                        difficulty="Medium"),
                _diagnose("tscourse-w14-fn-d1", "The bridge that was missing",
                          "TS2749: 'parse' refers to a value, but is being used as a type here. Did you mean 'typeof parse'?",
                          'function parse(line: string): { desc: string; cents: number } {\n'
                          '  const p = line.split(" ");\n'
                          '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                          'type Row = ReturnType<parse>;\n'
                          'function money(r: Row): string {\n'
                          '  return `${r.desc} ${r.cents}`;\n}\n'
                          'console.log(money(parse("coffee 3.25")));\n',
                          'function parse(line: string): { desc: string; cents: number } {\n'
                          '  const p = line.split(" ");\n'
                          '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                          'type Row = ReturnType<typeof parse>;\n'
                          'function money(r: Row): string {\n'
                          '  return `${r.desc} ${r.cents}`;\n}\n'
                          'console.log(money(parse("coffee 3.25")));\n',
                          [("", "coffee 325")],
                          hints=["The error message names the fix precisely.",
                                 "ReturnType takes a type; a function name in a type position is a value."],
                          difficulty="Easy"),
                _fix("tscourse-w14-fn-fix1", "Fix the shape that was written twice",
                     "`Row` was written out by hand and no longer matches what `parse` returns — a field was renamed — so `total` reads a member that is undefined at runtime and this prints `$NaN` instead of `$903.25`. Derive the type instead.",
                     _FS +
                     'interface Row {\n  desc: string;\n  amount: number;\n}\n'
                     'function parse(line: string): { desc: string; cents: number } {\n'
                     '  const p = line.split(" ");\n'
                     '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                     'function total(rows: readonly Row[]): number {\n'
                     '  return rows.reduce((s, r) => s + r.amount, 0);\n}\n'
                     'const rows = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse) as unknown as Row[];\n'
                     'console.log(`$${(total(rows) / 100).toFixed(2)}`);\n',
                     _FS +
                     'function parse(line: string): { desc: string; cents: number } {\n'
                     '  const p = line.split(" ");\n'
                     '  return { desc: p[0] ?? "", cents: Math.round(Number(p[1] ?? "0") * 100) };\n}\n'
                     'type Row = ReturnType<typeof parse>;\n'
                     'function total(rows: readonly Row[]): number {\n'
                     '  return rows.reduce((s, r) => s + r.cents, 0);\n}\n'
                     'const rows = fs.readFileSync(0, "utf8").trim().split("\\n").map(parse);\n'
                     'console.log(`$${(total(rows) / 100).toFixed(2)}`);\n',
                     [("coffee 3.25\nrent 900", "$903.25"),
                      ("tea 2", "$2.00")],
                     hints=["`as unknown as Row[]` is what let the mismatch through — it checks literally nothing (week 12). A single `as` would have been rejected as TS2352.",
                            "Delete the hand-written interface and derive: type Row = ReturnType<typeof parse>;",
                            "Then `total` has to read `cents`, and the assertion is no longer needed."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`ReturnType` on an overloaded function sees…",
                   ["all overloads", "only the last one", "the first one", "an error"], 1,
                   "A real limitation worth knowing."),
                _q("`Awaited<T>` unwraps a Promise, and arrives in…",
                   ["this week", "week 17", "week 29", "never"], 1,
                   "With async and promises."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w14-choose", "When a purpose-built type reads better",
            "Knowing where to stop.",
            """
Everything this week was a reason to derive a type. Here is the other side,
because a codebase where every type is four utilities deep is worse than one
where a few types are written out.

## Name your derivations

The first rule costs nothing. This is unreadable inline:

```ts
function applyPatch(e: Entry, patch: Partial<Omit<Entry, "id" | "createdAt">>): Entry
```

This is not:

```ts
type EntryPatch = Partial<Omit<Entry, "id" | "createdAt">>;

function applyPatch(e: Entry, patch: EntryPatch): Entry
```

Same type. The alias gives the concept a name, and every signature that uses it
gets shorter. **Derive once, name it, use the name.**

## Two deep is plenty

```ts
type EntryPatch = Partial<Omit<Entry, "id">>;                       // ✅ clear
type Thing = Partial<Omit<Pick<Entry, "a" | "b" | "c">, "c">>;      // ❌ just write it
```

The second says "take three members, drop one of them, make the rest optional".
By the time you have worked that out you could have read the two-member type it
describes. When a chain stops being readable at a glance, write the type out —
and leave a comment saying what it relates to, if the relationship matters.

## Derive a relationship, not a coincidence

The real judgement call. Ask: **must these two change together?**

```ts
type EntryCreate = Omit<Entry, "id">;
```

"A create payload is an entry without its id." That is a rule about your domain.
It should hold forever, and deriving it means it does.

```ts
type ApiResponse = Pick<DbRow, "desc" | "cents">;
```

That is a coincidence. A database row and an API response are separate contracts
that happen to overlap today. Tie them together and the first time you need to
rename a column without changing the public API, you have to unpick it — and
worse, somebody might change the column and silently change your API.

**Independent contracts get independent types**, even when that means writing the
same three members twice. Duplication is cheaper than a wrong coupling.

## A checklist

Reach for a derived type when:

* one type is genuinely defined in terms of another (`Create`, `Patch`, `Row`);
* you do not own the source type and cannot annotate it;
* the relationship is the thing you want the compiler to enforce.

Write it out when:

* the two types are free to diverge;
* the chain is more than about two utilities deep;
* the shape is meaningful enough to deserve its own name and documentation.

And remember what all of this is for: **when the source type changes, the right
places break.** If a derivation does not produce a useful compile error when the
source changes, it is not buying you anything.

> ⚠️ **Common mistakes:** inlining a four-deep chain into a signature; coupling
> a storage type to a wire type; and treating "derived" as automatically better —
> it is better only when the relationship is real.
""",
            warmup=[
                _q("The cheapest readability win with utilities is…",
                   ["fewer of them", "naming the derivation with a type alias", "any",
                    "interfaces"], 1,
                   "Derive once, name it, use the name."),
                _q("A chain more than about two utilities deep is…",
                   ["ideal", "usually less readable than the type written out", "faster",
                    "required"], 1,
                   "Write it out."),
                _q("A DB row and an API response should…",
                   ["be derived from each other", "have independent types — they may diverge",
                    "be the same type", "use Pick"], 1,
                   "Duplication is cheaper than a wrong coupling."),
                _q("A derivation is buying you nothing if…",
                   ["it is short", "changing the source type produces no useful error",
                    "it is named", "it uses Omit"], 1,
                   "That error IS the value."),
            ],
            exercises=[
                _ex("tscourse-w14-ch-1", "Name the derivation",
                    "Give the patch type a name, so the signature stays readable.",
                    'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n}\n'
                    'type EntryPatch = Partial<Omit<Entry, "id">>;\n'
                    'function applyPatch(e: Entry, patch: EntryPatch): Entry {\n'
                    '  return { ...e, ...patch };\n}\n'
                    'const e: Entry = { id: "e1", desc: "coffee", cents: 325 };\n'
                    'console.log(applyPatch(e, { cents: 400 }).cents);\n',
                    'type EntryPatch = Partial<Omit<Entry, "id">>;',
                    [("", "400")],
                    hints=["Any subset of an entry's members except the id.",
                           'Write type EntryPatch = Partial<Omit<Entry, "id">>;'],
                    difficulty="Medium"),
                _ex("tscourse-w14-ch-2", "Independent contracts",
                    "The wire format is free to diverge from the stored row, so write it out rather than deriving it.",
                    'interface DbRow {\n  row_id: string;\n  desc: string;\n  cents: number;\n}\n'
                    'interface ApiEntry {\n  description: string;\n  amount: number;\n}\n'
                    'function toApi(r: DbRow): ApiEntry {\n'
                    '  return { description: r.desc, amount: r.cents };\n}\n'
                    'const a = toApi({ row_id: "1", desc: "coffee", cents: 325 });\n'
                    'console.log(`${a.description} ${a.amount}`);\n',
                    'interface ApiEntry {\n  description: string;\n  amount: number;\n}',
                    [("", "coffee 325")],
                    hints=["The member NAMES differ, so no Pick or Omit could produce this type.",
                           "Two members: description as a string, amount as a number.",
                           "This is the case where writing it out is the right answer."],
                    difficulty="Medium"),
                _ex("tscourse-w14-ch-3", "Unpick the unreadable chain",
                    "This derivation is three deep and describes a two-member type. Write that type out instead.",
                    'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n  tag: string;\n}\n'
                    'interface Draft {\n  desc?: string;\n  cents?: number;\n}\n'
                    'function describe(d: Draft): string {\n'
                    '  return `${d.desc ?? "?"}/${d.cents ?? 0}`;\n}\n'
                    'console.log(describe({ desc: "coffee" }));\n'
                    'console.log(describe({ desc: "rent", cents: 90000 }));\n',
                    'interface Draft {\n  desc?: string;\n  cents?: number;\n}',
                    [("", "coffee/0\nrent/90000")],
                    hints=["Two optional members, both readable at a glance.",
                           "desc is an optional string; cents is an optional number.",
                           "The first call omits cents, so the `?? 0` fires and it prints coffee/0."],
                    difficulty="Medium"),
                _types("tscourse-w14-ch-t1", "The derivation that must hold",
                       "A create payload is an entry without its id. Encode that relationship, "
                       "so adding a member to Entry makes it patchable automatically.",
                       'interface Entry {\n  id: string;\n  desc: string;\n  cents: number;\n}\n'
                       'type EntryCreate = Omit<Entry, "id">;\n',
                       'type EntryCreate = Omit<Entry, "id">;',
                       """
type _1 = Expect<Equal<EntryCreate, { desc: string; cents: number }>>;

// The relationship, not the members, is what is being encoded: `id` must be
// gone and everything else must remain.
// @ts-expect-error
const withId: EntryCreate = { id: "e1", desc: "coffee", cents: 325 };
""",
                       hints=["Drop exactly one member, by name.",
                              "Writing the two members out would satisfy the first assertion and miss the point.",
                              'Write type EntryCreate = Omit<Entry, "id">;'],
                       difficulty="Medium"),
                _fix("tscourse-w14-ch-fix1", "Fix the coupling that should not exist",
                     "`ApiEntry` was derived from `DbRow`, so renaming the storage column silently renamed the public API field — `toApi` now produces `row_desc` and this prints `undefined coffee` instead of `coffee 325`. Give the wire format its own type.",
                     'interface DbRow {\n  row_id: string;\n  row_desc: string;\n  cents: number;\n}\n'
                     'type ApiEntry = Omit<DbRow, "row_id">;\n'
                     'function toApi(r: DbRow): ApiEntry {\n'
                     '  return { row_desc: r.row_desc, cents: r.cents };\n}\n'
                     'const a = toApi({ row_id: "1", row_desc: "coffee", cents: 325 });\n'
                     'console.log(`${(a as { desc?: string }).desc} ${a.row_desc}`);\n',
                     'interface DbRow {\n  row_id: string;\n  row_desc: string;\n  cents: number;\n}\n'
                     'interface ApiEntry {\n  desc: string;\n  cents: number;\n}\n'
                     'function toApi(r: DbRow): ApiEntry {\n'
                     '  return { desc: r.row_desc, cents: r.cents };\n}\n'
                     'const a = toApi({ row_id: "1", row_desc: "coffee", cents: 325 });\n'
                     'console.log(`${a.desc} ${a.cents}`);\n',
                     [("", "coffee 325")],
                     hints=["The API's field names are a public contract and must not follow the database's.",
                            "Declare ApiEntry with its own members: desc and cents.",
                            "Then toApi does the mapping explicitly, and the cast in the print goes away."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Duplication versus a wrong coupling:",
                   ["always avoid duplication", "duplication is cheaper than a wrong coupling",
                    "they are the same", "use any"], 1,
                   "Independent contracts get independent types."),
                _q("Before deriving, ask…",
                   ["is it shorter?", "must these two change together?", "is it generic?",
                    "is it readonly?"], 1,
                   "That is the whole judgement call."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #14 — a patch/update API",
        """
Week 13 made the ledger immutable. Now it gets a real update API, with every
supporting type **derived from `Entry`** rather than written out beside it.

Input is entries first, then patch commands. An entry line is
`<id> <desc> <amount> <tag>`; a patch line is `patch <id> <field> <value>`:

```
e1 coffee 3.25 food
e2 rent 900 home
patch e1 cents 4.00
patch e2 tag fun
```

Print exactly:

```
Entries:  2
Total:    $904.00
By tag:   food=$4.00, fun=$900.00
Cheapest: coffee $4.00
```

Build this scaffolding — note that all three types are **derivations**:

```ts
type EntryPatch   = Partial<Omit<Entry, "id">>;      // any field but the id
type EntrySummary = Pick<Entry, "desc" | "cents">;   // just what a summary needs
type Totals       = Record<Category, number>;        // exhaustive per category

function applyPatch(e: Entry, patch: EntryPatch): Entry
function parsePatch(field: string, value: string): EntryPatch
function summarise(e: Entry): EntrySummary
```

Rules:

- **Nothing is written out that could be derived.** `EntryPatch`,
  `EntrySummary` and `Totals` must all be computed from `Entry` and `Category`.
  Add a member to `Entry` and it should become patchable with no other edit.
- `parsePatch` handles `desc`, `cents` and `tag`, and **throws** on any other
  field name. `cents` is parsed as integer cents; `tag` is validated into a
  `Category`.
- `applyPatch` is pure: `{ ...e, ...patch }`, nothing mutated. A patch for an
  unknown id changes nothing.
- `By tag` lists only categories with a non-zero total, in `CATEGORIES` order,
  joined with `, `.
- `Cheapest` uses `EntrySummary`, so the function that produces it can see only
  `desc` and `cents` — not the id or the tag.
- Money is integer cents throughout; `Totals` values are cents.
""",
        _ch("tscourse-w14-capstone", "Budget Buddy #14", "Medium",
            "Write the three derived types and the three functions that use them.",
            _FS + 'const CATEGORIES = ["food", "fun", "home"] as const;\n'
            'type Category = (typeof CATEGORIES)[number];\n'
            'interface Entry {\n'
            '  readonly id: string;\n  readonly desc: string;\n'
            '  readonly cents: number;\n  readonly tag: Category;\n}\n'
            'function toCategory(s: string): Category {\n'
            '  for (const c of CATEGORIES) {\n'
            '    if (c === s) {\n      return c;\n    }\n  }\n'
            '  throw new Error(`unknown category: ${s}`);\n}\n'
            'type EntryPatch = Partial<Omit<Entry, "id">>;\n'
            'type EntrySummary = Pick<Entry, "desc" | "cents">;\n'
            'type Totals = Record<Category, number>;\n'
            'function applyPatch(e: Entry, patch: EntryPatch): Entry {\n'
            '  return { ...e, ...patch };\n}\n'
            'function parsePatch(field: string, value: string): EntryPatch {\n'
            '  if (field === "desc") {\n    return { desc: value };\n  }\n'
            '  if (field === "cents") {\n    return { cents: Math.round(Number(value) * 100) };\n  }\n'
            '  if (field === "tag") {\n    return { tag: toCategory(value) };\n  }\n'
            '  throw new Error(`unknown field: ${field}`);\n}\n'
            'function summarise(e: Entry): EntrySummary {\n'
            '  return { desc: e.desc, cents: e.cents };\n}\n'
            'function money(cents: number): string {\n'
            '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
            'function totalFor(es: readonly Entry[], tag: Category): number {\n'
            '  return es.filter((e) => e.tag === tag).reduce((s, e) => s + e.cents, 0);\n}\n'
            'function cheapest(es: readonly Entry[]): EntrySummary {\n'
            '  const first = es[0];\n'
            '  if (first === undefined) {\n    throw new Error("no entries");\n  }\n'
            '  let best: Entry = first;\n'
            '  for (const e of es) {\n'
            '    if (e.cents < best.cents) {\n      best = e;\n    }\n  }\n'
            '  return summarise(best);\n}\n'
            'let entries: readonly Entry[] = [];\n'
            'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
            '  const p = line.trim().split(" ");\n'
            '  if (p[0] === "patch") {\n'
            '    const id = p[1] ?? "";\n'
            '    const patch = parsePatch(p[2] ?? "", p[3] ?? "");\n'
            '    entries = entries.map((e) => (e.id === id ? applyPatch(e, patch) : e));\n'
            '  } else {\n'
            '    entries = [...entries, {\n'
            '      id: p[0] ?? "",\n'
            '      desc: p[1] ?? "",\n'
            '      cents: Math.round(Number(p[2] ?? "0") * 100),\n'
            '      tag: toCategory(p[3] ?? ""),\n'
            '    }];\n'
            '  }\n}\n'
            'const totals: Totals = {\n'
            '  food: totalFor(entries, "food"),\n'
            '  fun: totalFor(entries, "fun"),\n'
            '  home: totalFor(entries, "home"),\n};\n'
            'const byTag = CATEGORIES.filter((c) => totals[c] > 0).map((c) => `${c}=${money(totals[c])}`);\n'
            'const low = cheapest(entries);\n'
            'console.log(`Entries:  ${entries.length}`);\n'
            'console.log(`Total:    ${money(entries.reduce((s, e) => s + e.cents, 0))}`);\n'
            'console.log(`By tag:   ${byTag.join(", ")}`);\n'
            'console.log(`Cheapest: ${low.desc} ${money(low.cents)}`);\n',
            'type EntryPatch = Partial<Omit<Entry, "id">>;\n'
            'type EntrySummary = Pick<Entry, "desc" | "cents">;\n'
            'type Totals = Record<Category, number>;\n'
            'function applyPatch(e: Entry, patch: EntryPatch): Entry {\n'
            '  return { ...e, ...patch };\n}\n'
            'function parsePatch(field: string, value: string): EntryPatch {\n'
            '  if (field === "desc") {\n    return { desc: value };\n  }\n'
            '  if (field === "cents") {\n    return { cents: Math.round(Number(value) * 100) };\n  }\n'
            '  if (field === "tag") {\n    return { tag: toCategory(value) };\n  }\n'
            '  throw new Error(`unknown field: ${field}`);\n}\n'
            'function summarise(e: Entry): EntrySummary {\n'
            '  return { desc: e.desc, cents: e.cents };\n}',
            [("e1 coffee 3.25 food\ne2 rent 900 home\npatch e1 cents 4.00\npatch e2 tag fun",
              "Entries:  2\nTotal:    $904.00\nBy tag:   food=$4.00, fun=$900.00\nCheapest: coffee $4.00"),
             ("e1 tea 2 food",
              "Entries:  1\nTotal:    $2.00\nBy tag:   food=$2.00\nCheapest: tea $2.00"),
             ("e1 coffee 3.25 food\npatch e1 desc espresso",
              "Entries:  1\nTotal:    $3.25\nBy tag:   food=$3.25\nCheapest: espresso $3.25"),
             ("e1 coffee 3.25 food\ne2 book 12 fun\npatch e9 cents 1.00",
              "Entries:  2\nTotal:    $15.25\nBy tag:   food=$3.25, fun=$12.00\nCheapest: coffee $3.25")],
            hints=["EntryPatch is `Partial<Omit<Entry, \"id\">>` — two utilities deep, which lesson 8 says is fine.",
                   "EntrySummary is `Pick<Entry, \"desc\" | \"cents\">`; Totals is `Record<Category, number>`.",
                   "applyPatch is one line: { ...e, ...patch } — the entry first, so the patch wins.",
                   "parsePatch returns a one-member patch object per field, and throws on anything else. Each branch returns a valid EntryPatch because every member is optional.",
                   "For the tag branch, run the value through toCategory so an unknown tag throws rather than being stored.",
                   "summarise names the two members explicitly — a spread would carry the id and tag along (lesson 4).",
                   "The last test case patches an id that does not exist: `entries.map` finds no match, so nothing changes."]),
        example_io="Entries:  2\nTotal:    $904.00\nBy tag:   food=$4.00, fun=$900.00\nCheapest: coffee $4.00",
        rubric=["EntryPatch, EntrySummary and Totals are all derived from Entry/Category, not written out",
                "applyPatch is pure and spreads the entry before the patch",
                "parsePatch throws on an unknown field name rather than returning an empty patch",
                "a tag patch is validated through toCategory",
                "summarise builds its result member by member rather than spreading",
                "By tag skips zero categories and follows CATEGORIES order",
                "a patch for an unknown id leaves every entry unchanged"],
        stretch=_ch("tscourse-w14-capstone-stretch", "Budget Buddy #14 (stretch)", "Medium",
                    "Print a `Fields:` line listing the patchable field names, sorted. A union has "
                    "no runtime representation, so declare the list `as const` and check it against "
                    "the derived key union with `satisfies readonly (keyof EntryPatch)[]` — week "
                    "12's tool proving that the runtime list matches the type.",
                    _FS + 'interface Entry {\n'
                    '  readonly id: string;\n  readonly desc: string;\n'
                    '  readonly cents: number;\n  readonly tag: string;\n}\n'
                    'type EntryPatch = Partial<Omit<Entry, "id">>;\n'
                    'const PATCHABLE = ["cents", "desc", "tag"] as const satisfies readonly (keyof EntryPatch)[];\n'
                    'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'console.log(`Entries:  ${rows.length}`);\n'
                    'console.log(`Fields:   ${[...PATCHABLE].sort().join(", ")}`);\n',
                    'const PATCHABLE = ["cents", "desc", "tag"] as const satisfies readonly (keyof EntryPatch)[];',
                    [("e1 coffee 3.25 food", "Entries:  1\nFields:   cents, desc, tag"),
                     ("e1 coffee 3.25 food\ne2 rent 900 home", "Entries:  2\nFields:   cents, desc, tag")],
                    hints=["`keyof EntryPatch` is the union of the patchable member names — derived, so it follows Entry.",
                           "The list needs `as const` to keep its literal types, then `satisfies` to check it against that union.",
                           "Misspell a field and the satisfies fails; miss one out and it still passes — satisfies checks that every element is a valid key, not that every key is present.",
                           "Sort a copy: [...PATCHABLE].sort()."]),
    ),
))
